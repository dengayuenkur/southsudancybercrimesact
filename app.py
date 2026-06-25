from flask import Flask, render_template, request, Response, stream_with_context
from dotenv import load_dotenv
import re
import html as html_lib
import os
import json

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

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
NUM_PENALTIES = sum(1 for s in ALL_SECTIONS if "penalty" in s["title"].lower() or "penalty" in s["content"].lower())

@app.context_processor
def inject_globals():
    return {"num_sections": NUM_SECTIONS}

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

_STOPWORDS = {'the','a','an','is','are','was','were','what','how','who','when',
              'where','which','in','of','to','for','with','and','or','that',
              'this','it','be','as','at','by','from','do','does','did','has',
              'have','had','can','will','would','could','should','under','act'}

def get_relevant_sections(query, top_n=8):
    keywords = [w for w in re.findall(r'\w+', query.lower())
                if w not in _STOPWORDS and len(w) > 2]
    if not keywords:
        return ALL_SECTIONS[:top_n]
    scored = []
    for s in ALL_SECTIONS:
        text = (s['title'] + ' ' + s['content']).lower()
        score = sum(text.count(kw) * (3 if kw in s['title'].lower() else 1)
                    for kw in keywords)
        if score > 0:
            scored.append((score, s))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [s for _, s in scored[:top_n]] or ALL_SECTIONS[:top_n]

def build_context(sections):
    parts = []
    for s in sections:
        parts.append(f"[Chapter {s['chapter']} | Section {s['section']}] {s['title']}\n{s['content']}")
    return "\n\n---\n\n".join(parts)

def get_groq_client():
    try:
        from groq import Groq
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            return None, "GROQ_API_KEY environment variable not set."
        return Groq(api_key=api_key), None
    except ImportError:
        return None, "groq package not installed. Run: pip install groq"

ASSISTANT_SYSTEM = """You are a legal research assistant for the Cybercrimes and Computer Misuse Act, 2026 of the Republic of South Sudan.

Answer questions clearly and accurately, citing specific section numbers when relevant. If a question falls outside the Act, say so. Keep answers concise but thorough. Use plain language where possible.

RELEVANT SECTIONS FROM THE ACT:
{context}"""

SCENARIO_SYSTEM = """You are a legal analyst for the Cybercrimes and Computer Misuse Act, 2026 of the Republic of South Sudan. A user will describe a real-world scenario. Your job is to:

1. Identify which sections of the Act apply to the scenario.
2. For each relevant section, explain exactly how it applies.
3. Summarise any potential offences, penalties, or legal obligations involved.
4. Note any important caveats or limitations.

Be specific with section numbers. Structure your response with clear headings. Use plain, accessible language.

RELEVANT SECTIONS FROM THE ACT:
{context}"""

# ── Routes ──────────────────────────────────────────────────

@app.route("/")
def home():
    return render_template("home.html", active="home",
        num_chapters=NUM_CHAPTERS, num_sections=NUM_SECTIONS,
        num_offences=NUM_OFFENCES, num_penalties=NUM_PENALTIES,
        chapters=ACT_DATA["chapters"])

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

@app.route("/assistant")
def assistant():
    _, err = get_groq_client()
    return render_template("assistant.html", active="assistant",
        num_sections=NUM_SECTIONS, api_error=err)

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json()
    messages = data.get("messages", [])
    if not messages:
        return Response("No messages provided.", status=400)

    client, err = get_groq_client()
    if err:
        return Response(json.dumps({"error": err}), status=503, mimetype="application/json")

    last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
    context = build_context(get_relevant_sections(last_user))
    system_prompt = ASSISTANT_SYSTEM.format(context=context)

    def generate():
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=1024,
            stream=True,
            messages=[{"role": "system", "content": system_prompt}] + messages
        )
        for chunk in stream:
            text = chunk.choices[0].delta.content or ""
            if text:
                yield f"data: {json.dumps({'text': text})}\n\n"
        yield "data: [DONE]\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

@app.route("/scenario")
def scenario():
    _, err = get_groq_client()
    return render_template("scenario.html", active="scenario",
        num_sections=NUM_SECTIONS, api_error=err)

@app.route("/api/scenario", methods=["POST"])
def api_scenario():
    data = request.get_json()
    description = data.get("description", "").strip()
    if not description:
        return Response("No scenario provided.", status=400)

    client, err = get_groq_client()
    if err:
        return Response(json.dumps({"error": err}), status=503, mimetype="application/json")

    context = build_context(get_relevant_sections(description, top_n=10))
    system_prompt = SCENARIO_SYSTEM.format(context=context)

    def generate():
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=1500,
            stream=True,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": description}
            ]
        )
        for chunk in stream:
            text = chunk.choices[0].delta.content or ""
            if text:
                yield f"data: {json.dumps({'text': text})}\n\n"
        yield "data: [DONE]\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
