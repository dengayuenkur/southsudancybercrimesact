
import streamlit as st
import pandas as pd
import re

st.set_page_config(
    page_title="Cybercrimes Act 2026 | Republic of South Sudan",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# CUSTOM CSS
# =========================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,300;0,400;0,700;1,300&family=Inter:wght@400;500;600;700&display=swap');

* { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background-color: #f0f2f6;
}

/* ── Sidebar ─────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #001f4d 0%, #003080 100%);
    border-right: 3px solid #C9A227;
}
[data-testid="stSidebar"] * { color: #e8edf5 !important; }
[data-testid="stSidebar"] .stRadio label:hover { color: #C9A227 !important; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
    color: #C9A227 !important;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 1.5rem;
    margin-bottom: 0.25rem;
}

/* ── Header ──────────────────────────────────────────── */
.app-header {
    background: linear-gradient(135deg, #001228 0%, #001f4d 60%, #002a6b 100%);
    padding: 32px 28px 28px;
    border-radius: 12px;
    color: white;
    text-align: center;
    margin-bottom: 28px;
    border-bottom: 4px solid #C9A227;
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}
.app-header .flag-bar {
    display: flex;
    justify-content: center;
    gap: 0;
    margin-bottom: 16px;
    border-radius: 4px;
    overflow: hidden;
    width: 80px;
    margin-left: auto;
    margin-right: auto;
    height: 6px;
}
.app-header .flag-bar span { flex: 1; }
.app-header h1 {
    font-family: 'Merriweather', serif;
    font-size: clamp(1.2rem, 4vw, 2rem);
    font-weight: 700;
    margin: 0 0 6px;
    letter-spacing: 0.5px;
}
.app-header h2 {
    font-family: 'Merriweather', serif;
    font-size: clamp(0.95rem, 2.5vw, 1.35rem);
    font-weight: 300;
    margin: 0 0 4px;
    color: #C9A227;
    letter-spacing: 1px;
}
.app-header p {
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    margin: 0;
    color: #a0b0cc;
}

/* ── Metric Cards ─────────────────────────────────────── */
.metrics-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 16px;
    margin-bottom: 28px;
}
.metric-card {
    background: linear-gradient(135deg, #001f4d, #003080);
    padding: 22px 16px;
    border-radius: 12px;
    text-align: center;
    border-top: 3px solid #C9A227;
    box-shadow: 0 2px 12px rgba(0,0,0,0.12);
    color: white;
}
.metric-card .metric-value {
    font-family: 'Inter', sans-serif;
    font-size: clamp(1.8rem, 5vw, 2.6rem);
    font-weight: 700;
    color: #C9A227;
    line-height: 1;
    margin-bottom: 6px;
}
.metric-card .metric-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #a0b0cc;
}

/* ── Chapter Box ──────────────────────────────────────── */
.chapter-header {
    background: linear-gradient(135deg, #001228, #001f4d);
    padding: 20px 24px;
    border-radius: 10px 10px 0 0;
    margin-bottom: 0;
    border-left: 5px solid #C9A227;
    color: white;
}
.chapter-header h2 {
    font-family: 'Inter', sans-serif;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #C9A227;
    margin: 0 0 4px;
}
.chapter-header h3 {
    font-family: 'Merriweather', serif;
    font-size: clamp(1rem, 2.5vw, 1.3rem);
    font-weight: 700;
    margin: 0;
    color: white;
}

/* ── Section Box ──────────────────────────────────────── */
.section-card {
    background: white;
    border-radius: 8px;
    margin-bottom: 16px;
    border-left: 4px solid #003080;
    box-shadow: 0 1px 6px rgba(0,0,0,0.07);
    overflow: hidden;
}
.section-card-header {
    background: #f8f9fb;
    padding: 14px 20px;
    border-bottom: 1px solid #e4e8f0;
}
.section-card-header .section-num {
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #003080;
    margin: 0 0 2px;
}
.section-card-header h4 {
    font-family: 'Merriweather', serif;
    font-size: clamp(0.9rem, 2vw, 1.05rem);
    font-weight: 700;
    color: #1a2540;
    margin: 0;
}
.section-card-body {
    padding: 16px 20px;
    font-family: 'Merriweather', serif;
    font-size: 0.92rem;
    line-height: 1.75;
    color: #2d3748;
    text-align: justify;
    white-space: pre-wrap;
    word-break: break-word;
}

/* ── Search ──────────────────────────────────────────── */
.search-result-card {
    background: white;
    border-radius: 8px;
    margin-bottom: 16px;
    border-left: 4px solid #C9A227;
    box-shadow: 0 1px 6px rgba(0,0,0,0.07);
    overflow: hidden;
}
.search-result-header {
    background: #fffbf0;
    padding: 12px 18px;
    border-bottom: 1px solid #ede7c8;
}
.search-result-header .result-meta {
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    color: #7a6a1e;
    letter-spacing: 0.5px;
    margin: 0 0 3px;
}
.search-result-header h4 {
    font-family: 'Merriweather', serif;
    font-size: 1rem;
    font-weight: 700;
    color: #1a2540;
    margin: 0;
}
.search-result-body {
    padding: 14px 18px;
    font-family: 'Merriweather', serif;
    font-size: 0.88rem;
    line-height: 1.7;
    color: #2d3748;
    text-align: justify;
}
mark {
    background-color: #fff3cd;
    color: #6a4c00;
    padding: 1px 3px;
    border-radius: 3px;
    font-weight: 600;
}

/* ── Info banner ─────────────────────────────────────── */
.info-banner {
    background: #e8f0fe;
    border-left: 4px solid #003080;
    border-radius: 6px;
    padding: 12px 18px;
    margin-bottom: 20px;
    font-family: 'Inter', sans-serif;
    font-size: 0.88rem;
    color: #1a2540;
}

/* ── TOC table ───────────────────────────────────────── */
.toc-row {
    display: flex;
    align-items: flex-start;
    padding: 10px 0;
    border-bottom: 1px solid #e4e8f0;
    gap: 12px;
}
.toc-chapter-num {
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    background: #003080;
    color: white;
    padding: 3px 8px;
    border-radius: 4px;
    white-space: nowrap;
    min-width: 70px;
    text-align: center;
}
.toc-chapter-title {
    font-family: 'Merriweather', serif;
    font-size: 0.88rem;
    color: #1a2540;
    flex: 1;
}
.toc-section-count {
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
    color: #8899b0;
    white-space: nowrap;
}

/* ── Footer ──────────────────────────────────────────── */
.app-footer {
    margin-top: 48px;
    background: #001228;
    color: #a0b0cc;
    padding: 28px 24px;
    border-radius: 10px;
    text-align: center;
    font-family: 'Inter', sans-serif;
    font-size: 0.8rem;
    border-top: 3px solid #C9A227;
}
.app-footer strong { color: #C9A227; }
.app-footer .disclaimer {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid #1e3a6e;
    font-size: 0.75rem;
    line-height: 1.6;
}

/* ── Streamlit overrides ─────────────────────────────── */
[data-testid="stSelectbox"] label,
[data-testid="stTextInput"] label { font-weight: 600; color: #1a2540; }
.stDataFrame { border-radius: 8px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# =========================
# LOAD & PARSE
# =========================

@st.cache_data
def load_act(path="cybercrime_act.txt"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return None

@st.cache_data
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

if raw_text is None:
    st.error("**Error:** Could not load `cybercrime_act.txt`. Please ensure the file is in the same directory as `app.py`.")
    st.stop()

ACT_DATA = parse_act(raw_text)

# =========================
# HELPERS
# =========================

def get_all_sections():
    return [
        {
            "chapter": ch["number"],
            "chapter_title": ch["title"],
            "section": sec["number"],
            "title": sec["title"],
            "content": sec["content"]
        }
        for ch in ACT_DATA["chapters"]
        for sec in ch["sections"]
    ]

def highlight(text, term):
    if not term:
        return text
    escaped = re.escape(term)
    return re.sub(f"({escaped})", r"<mark>\1</mark>", text, flags=re.IGNORECASE)

def search_sections(term, chapter_filter=None):
    results = []
    for s in get_all_sections():
        if chapter_filter and s["chapter"] != chapter_filter:
            continue
        title_hit = term.lower() in s["title"].lower()
        body_hit = term.lower() in s["content"].lower()
        if title_hit or body_hit:
            score = s["content"].lower().count(term.lower())
            results.append({**s, "score": score})
    results.sort(key=lambda x: x["score"], reverse=True)
    return results

ALL_SECTIONS = get_all_sections()
NUM_CHAPTERS = len(ACT_DATA["chapters"])
NUM_SECTIONS = len(ALL_SECTIONS)
NUM_OFFENCES = sum(1 for s in ALL_SECTIONS if "offence" in s["content"].lower())

# =========================
# HEADER
# =========================

st.markdown("""
<div class="app-header">
    <div class="flag-bar">
        <span style="background:#000;"></span>
        <span style="background:#d00;"></span>
        <span style="background:#0f0;"></span>
        <span style="background:#00f;"></span>
    </div>
    <h1>Republic of South Sudan</h1>
    <h2>⚖ CYBERCRIMES AND COMPUTER MISUSE ACT, 2026</h2>
    <p>Professional Legal Research Platform</p>
</div>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================

st.sidebar.markdown("### Navigation")
page = st.sidebar.radio(
    "Go to",
    ["🏠 Home", "📖 Browse Act", "🔍 Search", "📊 Analytics"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Cybercrimes and Computer Misuse Act, 2026 \n\nThis platform provides structured access to the Cybercrimes and Computer Misuse Act, 2026 of the Republic of South Sudan. Use the navigation above to explore chapters, search for specific provisions, or view analytics about the Act.")


# =========================
# HOME
# =========================

if page == "🏠 Home":

    st.markdown(f"""
<div class="metrics-row">
    <div class="metric-card">
        <div class="metric-value">{NUM_CHAPTERS}</div>
        <div class="metric-label">Chapters</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{NUM_SECTIONS}</div>
        <div class="metric-label">Sections</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{NUM_OFFENCES}</div>
        <div class="metric-label">Offence Sections</div>
    </div>
    
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="info-banner">📋 This platform provides structured access to the Cybercrimes and Computer Misuse Act, 2026 of the Republic of South Sudan. Use <b>Browse Act</b> to read chapters, <b>Search</b> to find specific provisions, and <b>Analytics</b> for statistical insights.</div>', unsafe_allow_html=True)

    st.subheader("Chapters Overview")

    toc_html = '<div style="background:white;border-radius:10px;padding:8px 20px;box-shadow:0 1px 6px rgba(0,0,0,0.07);">'
    for ch in ACT_DATA["chapters"]:
        sec_count = len(ch["sections"])
        title_case = ch["title"].title()
        toc_html += f"""
        <div class="toc-row">
            <span class="toc-chapter-num">Chapter {ch['number']}</span>
            <span class="toc-chapter-title">{title_case}</span>
            <span class="toc-section-count">{sec_count} section{'s' if sec_count != 1 else ''}</span>
        </div>"""
    toc_html += "</div>"
    st.markdown(toc_html, unsafe_allow_html=True)

# =========================
# BROWSE ACT
# =========================

elif page == "📖 Browse Act":

    chapter_names = [f"Chapter {c['number']} — {c['title'].title()}" for c in ACT_DATA["chapters"]]
    selected = st.selectbox("Select Chapter", chapter_names)
    selected_index = chapter_names.index(selected)
    chapter = ACT_DATA["chapters"][selected_index]

    st.markdown(f"""
<div class="chapter-header">
    <h2>Chapter {chapter['number']}</h2>
    <h3>{chapter['title'].title()}</h3>
</div>
""", unsafe_allow_html=True)

    st.markdown(f"<p style='font-family:Inter,sans-serif;font-size:0.82rem;color:#8899b0;margin:4px 0 20px;'>{len(chapter['sections'])} section(s)</p>", unsafe_allow_html=True)

    for section in chapter["sections"]:
        content_html = section["content"].replace("<", "&lt;").replace(">", "&gt;")
        st.markdown(f"""
<div class="section-card">
    <div class="section-card-header">
        <div class="section-num">Section {section['number']}</div>
        <h4>{section['title']}</h4>
    </div>
    <div class="section-card-body">{content_html}</div>
</div>
""", unsafe_allow_html=True)

# =========================
# SEARCH
# =========================

elif page == "🔍 Search":

    st.subheader("Legal Search Engine")

    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input(
            "Search the Act",
            placeholder="e.g. hacking, phishing, cyberbullying, penalty …",
            label_visibility="collapsed"
        )
    with col2:
        chapter_options = ["All Chapters"] + [f"Chapter {c['number']}" for c in ACT_DATA["chapters"]]
        chapter_filter_label = st.selectbox("Filter", chapter_options, label_visibility="collapsed")
        chapter_filter = None if chapter_filter_label == "All Chapters" else chapter_filter_label.split(" ")[1]

    if search_term:
        results = search_sections(search_term.strip(), chapter_filter)

        if results:
            st.success(f"**{len(results)}** result{'s' if len(results) != 1 else ''} found for **\"{search_term}\"**")
        else:
            st.warning(f"No results found for **\"{search_term}\"**. Try a different keyword.")

        for r in results:
            title_hl = highlight(r["title"], search_term)
            content_preview = r["content"][:600] + ("…" if len(r["content"]) > 600 else "")
            content_hl = highlight(content_preview.replace("<", "&lt;").replace(">", "&gt;"), search_term)
            st.markdown(f"""
<div class="search-result-card">
    <div class="search-result-header">
        <div class="result-meta">Chapter {r['chapter']} — {r['chapter_title'].title()} &nbsp;·&nbsp; Section {r['section']}</div>
        <h4>{title_hl}</h4>
    </div>
    <div class="search-result-body">{content_hl}</div>
</div>
""", unsafe_allow_html=True)

    else:
        st.markdown('<div class="info-banner">Enter a keyword above to search all sections of the Act. You can filter by chapter using the dropdown on the right.</div>', unsafe_allow_html=True)

# =========================
# ANALYTICS
# =========================

elif page == "📊 Analytics":

    st.subheader("Act Analytics")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Sections per Chapter**")
        chapter_df = pd.DataFrame([
            {"Chapter": f"Ch. {c['number']}", "Sections": len(c["sections"]), "Title": c["title"].title()}
            for c in ACT_DATA["chapters"]
        ])
        st.bar_chart(chapter_df.set_index("Chapter")["Sections"])
        st.dataframe(
            chapter_df[["Chapter", "Title", "Sections"]].rename(columns={"Title": "Chapter Title"}),
            use_container_width=True,
            hide_index=True
        )

    with col2:
        st.markdown("**Keyword Occurrences Across All Sections**")
        keywords = {
            "Offence": "offence",
            "Penalty": "penalty",
            "Hacking": "hacking",
            "Fraud": "fraud",
            "Cyberbullying": "cyberbullying",
            "Phishing": "phishing",
            "Pornography": "pornography",
            "Terrorism": "terror",
            "Imprisonment": "imprisonment",
            "Fine": "fine",
            "Espionage": "espionage",
            "Extortion": "extortion",
        }
        stats = {
            label: sum(kw in s["content"].lower() for s in ALL_SECTIONS)
            for label, kw in keywords.items()
        }
        stats_df = pd.DataFrame(
            sorted(stats.items(), key=lambda x: x[1], reverse=True),
            columns=["Keyword", "Sections Containing"]
        )
        st.bar_chart(stats_df.set_index("Keyword"))
        st.dataframe(stats_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("**Sections with Penalty Provisions**")
    penalty_sections = [s for s in ALL_SECTIONS if "penalty" in s["title"].lower() or "penalty" in s["content"].lower()]
    if penalty_sections:
        penalty_df = pd.DataFrame([
            {
                "Section": s["section"],
                "Title": s["title"],
                "Chapter": s["chapter"],
            }
            for s in penalty_sections
        ])
        st.dataframe(penalty_df, use_container_width=True, hide_index=True)
    else:
        st.info("No penalty sections detected.")

    st.markdown("---")
    col3, col4 = st.columns(2)
    with col3:
        total_words = len(raw_text.split())
        st.metric("Total Words", f"{total_words:,}")
    with col4:
        avg_len = int(sum(len(s["content"].split()) for s in ALL_SECTIONS) / max(NUM_SECTIONS, 1))
        st.metric("Avg. Words per Section", avg_len)

# =========================
# FOOTER
# =========================

st.markdown("""
<div class="app-footer">
    <strong>Cybercrimes and Computer Misuse Act, 2026</strong> &nbsp;·&nbsp; Republic of South Sudan
    <div class="disclaimer">
        <strong>Disclaimer:</strong> This platform is for educational and informational purposes only. Content is derived from the
        Cybercrimes and Computer Misuse Act, 2026. Users should consult official legal sources and qualified legal professionals
        for authoritative interpretation and legal advice.<br><br>
        Implemented by
<strong>
    <a href="https://dengayuenkur.github.io"
       style="color: #FFD700; text-decoration: none;"
       target="_blank"
       rel="noopener noreferrer">
        Deng Ayuen Kur
    </a>
</strong>
    </div>
</div>
""", unsafe_allow_html=True)
