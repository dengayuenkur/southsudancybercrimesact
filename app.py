from flask import Flask, render_template, request
import re
import html as html_lib
import os

app = Flask(__name__)

# ── Load & Parse ────────────────────────────────────────────

def load_act(path="cybercrime_act.txt"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return None

def parse_act(text):
    chapters = []
    chapter_pattern = r"CHAPTER\s+([IVX]+)\s*\n([A-Z][A-Z\s]+)"
    section_pattern = r"(\d+)\.\s+([^\n]+)"
    chapter_matches = list(re.finditer(chapter_pattern, text))
    for i, cm in enumerate(chapter_matches):
        start = cm.end()
        end = chapter_matches[i + 1].start() if i + 1 < len(chapter_matches) else len(text)
        chapter_text = text[start:end]
        sections = []
        section_matches = list(re.finditer(section_pattern, chapter_text))
        for j, sm in enumerate(section_matches):
            s_start = sm.end()
            s_end = section_matches[j + 1].start() if j + 1 < len(section_matches) else len(chapter_text)
            content = chapter_text[s_start:s_end].strip()
            sections.append({
                "number": sm.group(1),
                "title": sm.group(2).strip(),
                "content": content
            })
        chapters.append({
            "number": cm.group(1),
            "title": cm.group(2).strip(),
            "sections": sections
        })
    return {"chapters": chapters}

raw_text = load_act()
ACT_DATA = parse_act(raw_text) if raw_text else {"chapters": []}
ALL_SECTIONS = [
    {"chapter": ch["number"], "chapter_title": ch["title"],
     "section": sec["number"], "title": sec["title"], "content": sec["content"]}
    for ch in ACT_DATA["chapters"] for sec in ch["sections"]
]
NUM_CHAPTERS = len(ACT_DATA["chapters"])
NUM_SECTIONS = len(ALL_SECTIONS)
NUM_OFFENCES = sum(1 for s in ALL_SECTIONS if "offence" in s["content"].lower())

# ── Helpers ─────────────────────────────────────────────────

def highlight(text, term):
    escaped = html_lib.escape(text)
    if not term:
        return escaped
    return re.sub(
        f"({re.escape(html_lib.escape(term))})",
        r"<mark>\1</mark>", escaped, flags=re.IGNORECASE
    )

def search_sections(term, chapter_filter=None):
    results = []
    for s in ALL_SECTIONS:
        if chapter_filter and s["chapter"] != chapter_filter:
            continue
        if term.lower() in s["title"].lower() or term.lower() in s["content"].lower():
            results.append({**s, "score": s["content"].lower().count(term.lower())})
    return sorted(results, key=lambda x: x["score"], reverse=True)

# ── Routes ──────────────────────────────────────────────────

@app.route("/")
def home():
    return render_template("home.html", active="home",
        num_chapters=NUM_CHAPTERS, num_sections=NUM_SECTIONS,
        num_offences=NUM_OFFENCES, chapters=ACT_DATA["chapters"])

@app.route("/browse")
def browse():
    chapter_num = request.args.get("chapter", ACT_DATA["chapters"][0]["number"] if ACT_DATA["chapters"] else "")
    chapter = next((c for c in ACT_DATA["chapters"] if c["number"] == chapter_num),
                   ACT_DATA["chapters"][0] if ACT_DATA["chapters"] else None)
    return render_template("browse.html", active="browse",
        chapters=ACT_DATA["chapters"], chapter=chapter, selected_num=chapter_num)

@app.route("/search")
def search():
    term = request.args.get("q", "").strip()
    chapter_filter = request.args.get("chapter", "")
    results = []
    if term:
        for r in search_sections(term, chapter_filter or None):
            preview = r["content"][:600] + ("…" if len(r["content"]) > 600 else "")
            results.append({
                **r,
                "title_hl": highlight(r["title"], term),
                "content_hl": highlight(preview, term)
            })
    return render_template("search.html", active="search",
        chapters=ACT_DATA["chapters"], term=term,
        chapter_filter=chapter_filter, results=results)

@app.route("/analytics")
def analytics():
    chapter_data = [
        {"label": f"Ch. {c['number']}", "value": len(c["sections"])}
        for c in ACT_DATA["chapters"]
    ]
    kw = {
        "Offence": "offence", "Penalty": "penalty", "Hacking": "hacking",
        "Fraud": "fraud", "Cyberbullying": "cyberbullying", "Phishing": "phishing",
        "Pornography": "pornography", "Terrorism": "terror",
        "Imprisonment": "imprisonment", "Fine": "fine",
        "Espionage": "espionage", "Extortion": "extortion",
    }
    keyword_data = sorted([
        {"label": k, "value": sum(v in s["content"].lower() for s in ALL_SECTIONS)}
        for k, v in kw.items()
    ], key=lambda x: x["value"], reverse=True)
    penalty_sections = [
        s for s in ALL_SECTIONS
        if "penalty" in s["title"].lower() or "penalty" in s["content"].lower()
    ]
    total_words = f"{len(raw_text.split()):,}" if raw_text else "0"
    avg_len = int(sum(len(s["content"].split()) for s in ALL_SECTIONS) / max(NUM_SECTIONS, 1))
    return render_template("analytics.html", active="analytics",
        chapters=ACT_DATA["chapters"], chapter_data=chapter_data,
        keyword_data=keyword_data, penalty_sections=penalty_sections,
        total_words=total_words, avg_len=avg_len)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
