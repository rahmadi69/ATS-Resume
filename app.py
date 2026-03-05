import streamlit as st
import google.generativeai as genai
import json
import re
import io

# ── page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResumeAI – ATS Checker & Builder",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

* { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0a0a0f;
    color: #e8e4dc;
}

h1, h2, h3, h4 {
    font-family: 'Syne', sans-serif !important;
}

/* Hide default Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 1.5rem !important; max-width: 1100px; }

/* Hero */
.hero {
    text-align: center;
    padding: 3.5rem 1rem 2rem;
    background: radial-gradient(ellipse 80% 50% at 50% -20%, #2a1a4e 0%, transparent 70%);
}
.hero-badge {
    display: inline-block;
    background: rgba(139,92,246,0.15);
    border: 1px solid rgba(139,92,246,0.4);
    color: #c4b5fd;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.75rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
    font-family: 'Syne', sans-serif;
}
.hero h1 {
    font-size: clamp(2.2rem, 6vw, 4rem) !important;
    font-weight: 800 !important;
    line-height: 1.1 !important;
    margin: 0 0 0.8rem !important;
    background: linear-gradient(135deg, #f0e8ff 0%, #a78bfa 50%, #6d28d9 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero p {
    color: #9d97b0;
    font-size: 1.05rem;
    max-width: 520px;
    margin: 0 auto;
    line-height: 1.7;
}

/* Mode cards */
.mode-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 1rem;
    margin: 2rem 0;
}
.mode-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 1.4rem;
    cursor: pointer;
    transition: all 0.2s;
    text-align: center;
}
.mode-card:hover {
    border-color: rgba(139,92,246,0.5);
    background: rgba(139,92,246,0.08);
    transform: translateY(-2px);
}
.mode-icon { font-size: 2rem; margin-bottom: 0.5rem; }
.mode-title { font-family: 'Syne', sans-serif; font-weight: 700; font-size: 1rem; color: #e8e4dc; }
.mode-desc { font-size: 0.82rem; color: #7a7590; margin-top: 0.3rem; }

/* Score ring */
.score-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 2rem;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px;
    margin-bottom: 1.5rem;
}
.score-ring {
    width: 140px;
    height: 140px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Syne', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    margin-bottom: 0.8rem;
    position: relative;
}
.score-label {
    font-size: 0.85rem;
    color: #9d97b0;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-family: 'Syne', sans-serif;
}

/* Metric cards */
.metric-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
    gap: 0.75rem;
    margin: 1rem 0;
}
.metric-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
}
.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: #a78bfa;
}
.metric-label { font-size: 0.75rem; color: #7a7590; margin-top: 0.2rem; }

/* Feedback cards */
.feedback-card {
    background: rgba(255,255,255,0.025);
    border-left: 3px solid #7c3aed;
    border-radius: 0 10px 10px 0;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
}
.feedback-section {
    font-family: 'Syne', sans-serif;
    font-size: 0.8rem;
    color: #a78bfa;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.3rem;
}
.feedback-text { font-size: 0.92rem; color: #c8c3d8; line-height: 1.6; }

/* Keyword pills */
.pill-container { display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 0.5rem 0; }
.pill {
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-family: 'Syne', sans-serif;
}
.pill-missing { background: rgba(239,68,68,0.15); border: 1px solid rgba(239,68,68,0.3); color: #fca5a5; }
.pill-found { background: rgba(34,197,94,0.15); border: 1px solid rgba(34,197,94,0.3); color: #86efac; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #5b21b6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 1.5rem !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    transition: all 0.2s !important;
    width: 100%;
}
.stButton > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03) !important;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px !important;
    color: #9d97b0 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(139,92,246,0.3) !important;
    color: #e8e4dc !important;
}

/* Inputs */
.stTextArea textarea, .stTextInput input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #e8e4dc !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: rgba(139,92,246,0.5) !important;
    box-shadow: 0 0 0 2px rgba(139,92,246,0.1) !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1.5px dashed rgba(139,92,246,0.3) !important;
    border-radius: 12px !important;
}

/* Divider */
hr { border-color: rgba(255,255,255,0.06) !important; }

/* Success / Warning / Error */
.stSuccess { background: rgba(34,197,94,0.1) !important; border-color: rgba(34,197,94,0.3) !important; }
.stWarning { background: rgba(245,158,11,0.1) !important; border-color: rgba(245,158,11,0.3) !important; }
.stError { background: rgba(239,68,68,0.1) !important; border-color: rgba(239,68,68,0.3) !important; }

/* Expander */
.streamlit-expanderHeader {
    background: rgba(255,255,255,0.03) !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
}

/* Section titles */
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #e8e4dc;
    margin: 1.5rem 0 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.divider-line {
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.06);
}

/* Suggestion box */
.suggestion-box {
    background: rgba(124,58,237,0.08);
    border: 1px solid rgba(124,58,237,0.25);
    border-radius: 12px;
    padding: 1.2rem;
    margin: 0.8rem 0;
}
.suggestion-before {
    font-size: 0.83rem;
    color: #f87171;
    font-style: italic;
    margin-bottom: 0.5rem;
}
.suggestion-after {
    font-size: 0.88rem;
    color: #86efac;
    font-weight: 500;
}
.suggestion-why {
    font-size: 0.78rem;
    color: #9d97b0;
    margin-top: 0.5rem;
}

/* Resume preview */
.resume-preview {
    background: #1a1a2e;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 2rem;
    font-size: 0.88rem;
    line-height: 1.8;
    white-space: pre-wrap;
    color: #d4cfea;
}

/* Step indicator */
.step-indicator {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
    align-items: center;
}
.step-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: rgba(255,255,255,0.15);
}
.step-dot.active { background: #7c3aed; }
.step-dot.done { background: #22c55e; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #3b2d6e; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── helpers ───────────────────────────────────────────────────────────────────

def extract_text_from_pdf(file_bytes):
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            return "\n".join(p.extract_text() or "" for p in pdf.pages)
    except Exception as e:
        return f"[PDF read error: {e}]"

def extract_text_from_docx(file_bytes):
    try:
        import docx
        doc = docx.Document(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception as e:
        return f"[DOCX read error: {e}]"

def get_score_color(score):
    if score >= 75: return "#22c55e"
    if score >= 50: return "#f59e0b"
    return "#ef4444"

def get_score_label(score):
    if score >= 80: return "Excellent ✦"
    if score >= 65: return "Good — Minor Fixes"
    if score >= 45: return "Needs Work"
    return "Needs Major Improvement"

def parse_json_response(text):
    """Robustly extract JSON from Gemini response."""
    text = text.strip()
    # Remove markdown fences
    text = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()
    # Find first { ... }
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end])
        except:
            pass
    return None

# ── Gemini calls ──────────────────────────────────────────────────────────────

def analyze_resume(api_key, resume_text, job_description):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""
You are a professional ATS (Applicant Tracking System) expert and resume coach. Analyze the resume below against the job description.

RESUME:
{resume_text[:4000]}

JOB DESCRIPTION:
{job_description[:2000]}

Return ONLY a valid JSON object (no markdown, no explanation) with this exact structure:
{{
  "ats_score": <integer 0-100>,
  "keyword_match_score": <integer 0-100>,
  "format_score": <integer 0-100>,
  "impact_score": <integer 0-100>,
  "overall_verdict": "<one sentence plain English summary>",
  "found_keywords": ["keyword1", "keyword2"],
  "missing_keywords": ["keyword1", "keyword2"],
  "section_feedback": {{
    "summary": "<feedback or 'Not found'>",
    "skills": "<feedback>",
    "experience": "<feedback>",
    "education": "<feedback>",
    "formatting": "<feedback>"
  }},
  "top_improvements": [
    {{"issue": "<what is wrong>", "fix": "<what to do — plain English>"}},
    {{"issue": "...", "fix": "..."}},
    {{"issue": "...", "fix": "..."}}
  ],
  "bullet_rewrites": [
    {{"original": "<existing bullet>", "improved": "<rewritten>", "reason": "<why this is better>"}},
    {{"original": "...", "improved": "...", "reason": "..."}}
  ]
}}
"""
    response = model.generate_content(prompt)
    return parse_json_response(response.text)


def build_resume_from_form(api_key, form_data):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""
You are a professional resume writer. Build a clean, ATS-optimized resume from the information below.
Make it professional, concise, and impactful. Use strong action verbs. Return ONLY the plain text resume — no JSON, no markdown headers, no explanation.

PERSONAL INFO:
Name: {form_data.get('name', '')}
Email: {form_data.get('email', '')}
Phone: {form_data.get('phone', '')}
Location: {form_data.get('location', '')}
LinkedIn: {form_data.get('linkedin', '')}

CAREER OBJECTIVE / SUMMARY (what they told us):
{form_data.get('objective', '')}

TARGET JOB ROLE:
{form_data.get('target_role', '')}

EDUCATION:
{form_data.get('education', '')}

WORK EXPERIENCE (raw notes):
{form_data.get('experience', '')}

SKILLS:
{form_data.get('skills', '')}

PROJECTS:
{form_data.get('projects', '')}

CERTIFICATIONS:
{form_data.get('certifications', '')}

ACHIEVEMENTS / EXTRA:
{form_data.get('achievements', '')}

Write a complete, well-structured resume. Use clear sections with ALL CAPS headings. Use bullet points for experience and projects starting with strong action verbs. Keep it to 1 page worth of content.
"""
    response = model.generate_content(prompt)
    return response.text


def get_resume_tips(api_key, job_role):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""
Give 5 practical, specific resume tips for someone applying to: {job_role}
Return ONLY a JSON array of strings — no markdown, no explanation.
Example: ["Tip 1", "Tip 2", ...]
"""
    response = model.generate_content(prompt)
    text = response.text.strip().replace("```json","").replace("```","").strip()
    try:
        start = text.find("[")
        end = text.rfind("]") + 1
        return json.loads(text[start:end])
    except:
        return ["Focus on quantifiable achievements.", "Use keywords from the job description.", "Keep formatting clean and ATS-friendly."]

# ── UI ────────────────────────────────────────────────────────────────────────

# Hero
st.markdown("""
<div class="hero">
  <div class="hero-badge">✦ AI-Powered • Free • For Everyone</div>
  <h1>ResumeAI</h1>
  <p>Check your ATS score, get instant feedback, and build a professional resume — no experience needed.</p>
</div>
""", unsafe_allow_html=True)

# API Key input
with st.expander("🔑 Enter your Gemini API Key (free at aistudio.google.com)", expanded=not st.session_state.get("api_key_saved", False)):
    api_key_input = st.text_input("Gemini API Key", type="password", placeholder="AIza...", label_visibility="collapsed")
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Save Key"):
            if api_key_input.startswith("AIza"):
                st.session_state["gemini_api_key"] = api_key_input
                st.session_state["api_key_saved"] = True
                st.success("✓ API key saved!")
            else:
                st.error("Invalid key format.")
    with col2:
        st.markdown("<small style='color:#7a7590'>Get a free key → [aistudio.google.com](https://aistudio.google.com/app/apikey) → Create API Key</small>", unsafe_allow_html=True)

api_key = st.session_state.get("gemini_api_key", "")

st.markdown("<br>", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["✦ ATS Checker", "✦ Resume Builder", "✦ Quick Tips"])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — ATS CHECKER
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-title">📄 Your Resume <div class="divider-line"></div></div>', unsafe_allow_html=True)

    input_method = st.radio("How do you want to provide your resume?", ["Upload PDF", "Upload Word (.docx)", "Paste Text"], horizontal=True, label_visibility="collapsed")

    resume_text = ""

    if input_method == "Upload PDF":
        uploaded = st.file_uploader("Upload your resume PDF", type=["pdf"])
        if uploaded:
            resume_text = extract_text_from_pdf(uploaded.read())
            st.success(f"✓ PDF loaded — {len(resume_text.split())} words extracted")

    elif input_method == "Upload Word (.docx)":
        uploaded = st.file_uploader("Upload your resume DOCX", type=["docx"])
        if uploaded:
            resume_text = extract_text_from_docx(uploaded.read())
            st.success(f"✓ DOCX loaded — {len(resume_text.split())} words extracted")

    else:
        resume_text = st.text_area(
            "Paste your resume text here",
            placeholder="Paste your full resume here. Don't worry about formatting — just copy and paste everything...",
            height=200,
        )

    st.markdown('<div class="section-title">💼 Job Description <div class="divider-line"></div></div>', unsafe_allow_html=True)
    jd_text = st.text_area(
        "Job Description",
        placeholder="Paste the job posting here. The more complete, the better the analysis...",
        height=160,
        label_visibility="collapsed"
    )

    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        analyze_btn = st.button("✦ Analyze My Resume", use_container_width=True)

    if analyze_btn:
        if not api_key:
            st.error("Please enter your Gemini API key above first.")
        elif not resume_text.strip():
            st.error("Please provide your resume.")
        elif not jd_text.strip():
            st.error("Please paste the job description.")
        else:
            with st.spinner("Analyzing your resume... ✦"):
                result = analyze_resume(api_key, resume_text, jd_text)

            if not result:
                st.error("Couldn't parse AI response. Try again.")
            else:
                st.markdown("<br>", unsafe_allow_html=True)
                score = result.get("ats_score", 0)
                color = get_score_color(score)
                label = get_score_label(score)

                # Score display
                st.markdown(f"""
                <div class="score-container">
                    <div class="score-ring" style="background: conic-gradient({color} {score*3.6}deg, rgba(255,255,255,0.05) 0deg); box-shadow: 0 0 30px {color}40;">
                        <div style="background:#0a0a0f; width:110px; height:110px; border-radius:50%; display:flex; align-items:center; justify-content:center; flex-direction:column;">
                            <span style="color:{color}; font-size:2.2rem; font-weight:800; font-family:'Syne',sans-serif;">{score}</span>
                            <span style="font-size:0.65rem; color:#9d97b0; text-transform:uppercase; letter-spacing:0.1em;">ATS Score</span>
                        </div>
                    </div>
                    <div style="font-family:'Syne',sans-serif; font-size:1.05rem; font-weight:700; color:{color}; margin-top:0.3rem;">{label}</div>
                    <div style="font-size:0.88rem; color:#9d97b0; text-align:center; max-width:400px; margin-top:0.4rem;">{result.get('overall_verdict','')}</div>
                </div>
                """, unsafe_allow_html=True)

                # Sub-scores
                st.markdown(f"""
                <div class="metric-row">
                    <div class="metric-card">
                        <div class="metric-value" style="color:{get_score_color(result.get('keyword_match_score',0))}">{result.get('keyword_match_score',0)}</div>
                        <div class="metric-label">Keyword Match</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" style="color:{get_score_color(result.get('format_score',0))}">{result.get('format_score',0)}</div>
                        <div class="metric-label">Format Score</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" style="color:{get_score_color(result.get('impact_score',0))}">{result.get('impact_score',0)}</div>
                        <div class="metric-label">Impact Score</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Keywords
                st.markdown('<div class="section-title">🔑 Keywords <div class="divider-line"></div></div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**✓ Found in your resume**")
                    found = result.get("found_keywords", [])
                    pills_html = '<div class="pill-container">' + "".join(f'<span class="pill pill-found">{k}</span>' for k in found[:15]) + "</div>"
                    st.markdown(pills_html, unsafe_allow_html=True)
                with c2:
                    st.markdown("**✗ Missing — add these**")
                    missing = result.get("missing_keywords", [])
                    pills_html = '<div class="pill-container">' + "".join(f'<span class="pill pill-missing">{k}</span>' for k in missing[:15]) + "</div>"
                    st.markdown(pills_html, unsafe_allow_html=True)

                # Section feedback
                st.markdown('<div class="section-title">📋 Section Feedback <div class="divider-line"></div></div>', unsafe_allow_html=True)
                section_icons = {"summary": "👤", "skills": "⚙️", "experience": "💼", "education": "🎓", "formatting": "📐"}
                for section, feedback in result.get("section_feedback", {}).items():
                    st.markdown(f"""
                    <div class="feedback-card">
                        <div class="feedback-section">{section_icons.get(section,'•')} {section.title()}</div>
                        <div class="feedback-text">{feedback}</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Top improvements
                st.markdown('<div class="section-title">⚡ Top Things to Fix <div class="divider-line"></div></div>', unsafe_allow_html=True)
                for i, item in enumerate(result.get("top_improvements", []), 1):
                    with st.expander(f"{i}. {item.get('issue', 'Improvement')}"):
                        st.markdown(f"**What to do:** {item.get('fix', '')}")

                # Bullet rewrites
                rewrites = result.get("bullet_rewrites", [])
                if rewrites:
                    st.markdown('<div class="section-title">✍️ Bullet Point Rewrites <div class="divider-line"></div></div>', unsafe_allow_html=True)
                    for rw in rewrites:
                        st.markdown(f"""
                        <div class="suggestion-box">
                            <div class="suggestion-before">✗ Before: {rw.get('original','')}</div>
                            <div class="suggestion-after">✓ After: {rw.get('improved','')}</div>
                            <div class="suggestion-why">💡 {rw.get('reason','')}</div>
                        </div>
                        """, unsafe_allow_html=True)

                # Download report
                report_lines = [
                    "RESUMEAI — ATS ANALYSIS REPORT",
                    "=" * 40,
                    f"ATS Score: {score}/100  ({label})",
                    f"Verdict: {result.get('overall_verdict','')}",
                    "",
                    f"Keyword Match: {result.get('keyword_match_score',0)}/100",
                    f"Format Score:  {result.get('format_score',0)}/100",
                    f"Impact Score:  {result.get('impact_score',0)}/100",
                    "",
                    "MISSING KEYWORDS TO ADD:",
                    ", ".join(missing),
                    "",
                    "SECTION FEEDBACK:",
                ]
                for s, f in result.get("section_feedback", {}).items():
                    report_lines.append(f"  {s.upper()}: {f}")
                report_lines += ["", "TOP IMPROVEMENTS:"]
                for item in result.get("top_improvements", []):
                    report_lines.append(f"  - {item.get('issue','')}: {item.get('fix','')}")
                report_lines += ["", "BULLET REWRITES:"]
                for rw in rewrites:
                    report_lines.append(f"  Before: {rw.get('original','')}")
                    report_lines.append(f"  After:  {rw.get('improved','')}")
                    report_lines.append("")

                st.download_button(
                    "⬇ Download Full Report (.txt)",
                    data="\n".join(report_lines),
                    file_name="ats_report.txt",
                    mime="text/plain",
                )

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — RESUME BUILDER
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("#### 🛠 Build your resume from scratch")
    st.markdown('<small style="color:#9d97b0">No experience? No problem. Just fill in what you know — AI handles the rest.</small>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    with st.form("resume_builder_form"):
        st.markdown("**Personal Info**")
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Full Name *", placeholder="Mohammed Muzammil")
            email = st.text_input("Email *", placeholder="muzzy@gmail.com")
            phone = st.text_input("Phone", placeholder="+91 98765 43210")
        with c2:
            location = st.text_input("City, State", placeholder="Bellary, Karnataka")
            linkedin = st.text_input("LinkedIn (optional)", placeholder="linkedin.com/in/muzzammilc7")
            target_role = st.text_input("Target Job Role *", placeholder="SOC Analyst / Cybersecurity Intern")

        st.markdown("---")
        st.markdown("**Career Objective** *(in your own words — AI will improve it)*")
        objective = st.text_area("", placeholder="I'm a BCA final year student interested in cybersecurity. I want to work in a SOC team and learn threat analysis...", height=80, label_visibility="collapsed")

        st.markdown("**Education** *(just type it simply)*")
        education = st.text_area("", placeholder="BCA — Nandi Institute of Management and Science, Bellary\n2022–2025, CGPA: 7.5\n\nPUC — XYZ College, 2022, 78%", height=90, label_visibility="collapsed")

        st.markdown("**Work Experience** *(internships, part-time, freelance — or leave blank)*")
        experience = st.text_area("", placeholder="Intern at ABC Company (Jan 2024 – Mar 2024)\n- Helped with network monitoring\n- Wrote Python scripts for log analysis", height=100, label_visibility="collapsed")

        st.markdown("**Skills** *(comma separated is fine)*")
        skills = st.text_input("", placeholder="Python, Scikit-learn, Pandas, Streamlit, Linux, Wireshark, SQL, HTML/CSS, Git", label_visibility="collapsed")

        st.markdown("**Projects**")
        projects = st.text_area("", placeholder="Mini-SIEM AI — Python/Streamlit — Detects anomalies in system logs using ML\nPhishing Detector — 0.97 accuracy, Random Forest, deployed on Streamlit Cloud", height=90, label_visibility="collapsed")

        st.markdown("**Certifications**")
        certs = st.text_input("", placeholder="Google Cloud Cybersecurity, HuggingFace AI Agents, Anthropic Claude 101", label_visibility="collapsed")

        st.markdown("**Achievements / Extra**")
        achievements = st.text_input("", placeholder="Participated in Chakravyuha 3.0 Hackathon, BITM Bellary. Active on TryHackMe, HackTheBox.", label_visibility="collapsed")

        submit_build = st.form_submit_button("✦ Generate My Resume", use_container_width=True)

    if submit_build:
        if not api_key:
            st.error("Please enter your Gemini API key above first.")
        elif not name or not email or not target_role:
            st.error("Please fill in at least Name, Email, and Target Role.")
        else:
            form_data = {
                "name": name, "email": email, "phone": phone, "location": location,
                "linkedin": linkedin, "target_role": target_role, "objective": objective,
                "education": education, "experience": experience, "skills": skills,
                "projects": projects, "certifications": certs, "achievements": achievements,
            }
            with st.spinner("Building your resume... ✦"):
                resume_output = build_resume_from_form(api_key, form_data)

            st.markdown('<div class="section-title">✦ Your Resume <div class="divider-line"></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="resume-preview">{resume_output}</div>', unsafe_allow_html=True)

            st.download_button(
                "⬇ Download Resume (.txt)",
                data=resume_output,
                file_name=f"{name.replace(' ','_')}_resume.txt",
                mime="text/plain",
            )
            st.info("💡 Tip: Copy this into the ATS Checker tab + paste a job description to get your score and further improvements!")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — QUICK TIPS
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown("#### 💡 Get role-specific resume tips instantly")
    role_input = st.text_input("What job are you applying for?", placeholder="e.g. SOC Analyst, Data Analyst, Marketing Executive, Teacher...")
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        tips_btn = st.button("✦ Get Tips", use_container_width=True)

    if tips_btn:
        if not api_key:
            st.error("Please enter your Gemini API key above first.")
        elif not role_input.strip():
            st.error("Please enter a job role.")
        else:
            with st.spinner("Getting tips..."):
                tips = get_resume_tips(api_key, role_input)
            st.markdown('<div class="section-title">✦ Tips for ' + role_input + ' <div class="divider-line"></div></div>', unsafe_allow_html=True)
            for i, tip in enumerate(tips, 1):
                st.markdown(f"""
                <div class="feedback-card" style="border-left-color:#6d28d9;">
                    <div class="feedback-section">Tip {i}</div>
                    <div class="feedback-text">{tip}</div>
                </div>
                """, unsafe_allow_html=True)

    # General tips always visible
    st.markdown('<div class="section-title">📖 General ATS Tips <div class="divider-line"></div></div>', unsafe_allow_html=True)
    general_tips = [
        ("Use standard section headings", "ATS systems scan for 'Experience', 'Education', 'Skills'. Avoid creative names like 'My Journey'."),
        ("Mirror the job description", "Find keywords in the job posting and naturally include them in your resume. ATS literally counts them."),
        ("Quantify everything you can", "Instead of 'improved sales', write 'improved sales by 30% in Q2'. Numbers stand out to both ATS and humans."),
        ("One simple font, no tables/columns", "Fancy layouts confuse ATS parsers. Stick to a single-column layout with standard fonts."),
        ("Include both acronyms and full forms", "Write 'Search Engine Optimization (SEO)' so ATS catches both variations."),
        ("Use a .docx or simple PDF", "Some ATS systems struggle with heavily formatted PDFs. Use the Resume Builder here for a clean output."),
    ]
    for title, desc in general_tips:
        with st.expander(f"✦ {title}"):
            st.write(desc)

# Footer
st.markdown("""
<br><br>
<div style="text-align:center; color:#3d3a4f; font-size:0.78rem; font-family:'Syne',sans-serif; padding:1rem;">
    Built by <span style="color:#7c3aed">Muzzy</span> · Powered by Gemini · Free forever ✦
</div>
""", unsafe_allow_html=True)
