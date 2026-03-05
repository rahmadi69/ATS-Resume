import streamlit as st
from resume_parser import parse_pdf, parse_docx
from ai_engine import (
    ats_check, improve_resume, build_resume,
    get_role_tips, suggest_skills, improve_experience_bullets,
    career_fit
)
from ui_components import header, tips
from resume_to_docx import markdown_to_docx

st.set_page_config(page_title="ResumeAI", page_icon="📄", layout="wide")

# ── Mobile-friendly CSS ──
st.markdown("""
<style>
    /* Reduce side padding on mobile */
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 1rem !important;
        max-width: 100% !important;
    }
    /* Bigger buttons on mobile */
    .stButton > button {
        width: 100%;
        padding: 0.6rem 1rem;
        font-size: 1rem;
    }
    /* Full width download buttons */
    .stDownloadButton > button {
        width: 100%;
        padding: 0.6rem 1rem;
        font-size: 0.95rem;
    }
    /* Stack columns on small screens */
    @media (max-width: 640px) {
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
    }
    /* Larger text inputs on mobile */
    .stTextInput input, .stTextArea textarea {
        font-size: 1rem !important;
    }
    /* Tab labels readable on mobile */
    .stTabs [data-baseweb="tab"] {
        font-size: 0.85rem;
        padding: 0.4rem 0.6rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state init ──
for key in ["ats_result", "ats_resume_text", "career_fit_result",
            "improved_result", "built_resume", "skill_suggestions",
            "exp_bullets", "role_tips"]:
    if key not in st.session_state:
        st.session_state[key] = ""

header()

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 ATS Checker",
    "🏗️ Builder",
    "✏️ Improver",
    "💡 Tips"
])


# ─────────────────────── ATS CHECKER ─────────────────────── #

with tab1:
    st.subheader("ATS Resume Checker")

    option = st.radio(
        "Resume input method",
        ["Upload PDF", "Upload DOCX", "Paste Text"],
        horizontal=True
    )

    resume_text = ""

    if option == "Upload PDF":
        file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
        if file:
            resume_text = parse_pdf(file)
            if not resume_text.strip():
                st.error(
                    "❌ Could not read text from this PDF. "
                    "Please upload a valid text-based resume PDF "
                    "(not a scanned image or photo)."
                )
                resume_text = ""
            else:
                st.success("✅ PDF parsed successfully.")

    elif option == "Upload DOCX":
        file = st.file_uploader("Upload your resume (DOCX)", type=["docx"])
        if file:
            resume_text = parse_docx(file)
            if not resume_text.strip():
                st.error(
                    "❌ Could not read text from this DOCX. "
                    "Please upload a valid resume document."
                )
                resume_text = ""
            else:
                st.success("✅ DOCX parsed successfully.")

    else:
        resume_text = st.text_area("Paste your resume here", height=280)

    job_desc = st.text_area("Paste the Job Description here", height=180)

    if st.button("🔍 Analyze Resume", type="primary"):
        if not resume_text.strip():
            st.warning("⚠️ Please upload a valid resume or paste your resume text first.")
        elif not job_desc.strip():
            st.warning("⚠️ Please paste a job description to compare against.")
        else:
            with st.spinner("Analyzing with Groq AI..."):
                st.session_state.ats_result = ats_check(resume_text, job_desc)
                st.session_state.ats_resume_text = resume_text
                st.session_state.career_fit_result = ""

    if st.session_state.ats_result:
        st.markdown(st.session_state.ats_result)
        st.markdown("---")
        st.markdown("### 🎯 Where Should You Apply?")
        st.caption("AI will analyze your resume and suggest the best job roles for you.")

        if st.button("🔎 Find Best Job Matches for Me"):
            with st.spinner("Analyzing your career fit..."):
                st.session_state.career_fit_result = career_fit(
                    st.session_state.ats_resume_text
                )

    if st.session_state.career_fit_result:
        st.markdown(st.session_state.career_fit_result)


# ─────────────────────── RESUME BUILDER ─────────────────────── #

with tab2:
    st.subheader("AI Resume Builder")
    st.caption("Fill in your details — AI writes a professional ATS-optimized resume.")

    name = st.text_input("Full Name")
    education = st.text_area("Education (Degree, Institution, Year)", height=90)
    certs = st.text_input("Certifications (e.g. AWS, Google, CompTIA)")

    skills = st.text_input("Skills (comma separated)")

    if skills.strip():
        if st.button("💡 Suggest More Skills"):
            with st.spinner("Getting skill suggestions..."):
                st.session_state.skill_suggestions = suggest_skills(skills)

    if st.session_state.skill_suggestions:
        st.info(f"**Suggested skills to add:** {st.session_state.skill_suggestions}")

    experience = st.text_area("Work Experience (job title, company, what you did)", height=130)

    if experience.strip():
        if st.button("✨ Improve Experience Bullets"):
            with st.spinner("Rewriting with action verbs..."):
                st.session_state.exp_bullets = improve_experience_bullets(experience)

    if st.session_state.exp_bullets:
        st.info("**AI-improved bullets — copy these above:**")
        st.code(st.session_state.exp_bullets, language=None)

    projects = st.text_area("Projects (name, tech stack, what it does)", height=110)

    if st.button("🚀 Generate Resume", type="primary"):
        if not name.strip():
            st.warning("⚠️ Please enter your full name.")
        else:
            with st.spinner("Groq AI is building your ATS resume..."):
                st.session_state.built_resume = build_resume(
                    name, education, experience, skills, projects, certs
                )

    if st.session_state.built_resume:
        st.markdown("---")
        st.markdown(st.session_state.built_resume)

        docx_bytes = markdown_to_docx(st.session_state.built_resume, name)
        safe_name = name.strip().replace(" ", "_") if name.strip() else "resume"

        st.download_button(
            "⬇️ Download as DOCX (Word)",
            data=docx_bytes,
            file_name=f"{safe_name}_resume.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        st.download_button(
            "⬇️ Download as Markdown",
            data=st.session_state.built_resume,
            file_name=f"{safe_name}_resume.md",
            mime="text/markdown"
        )


# ─────────────────────── RESUME IMPROVER ─────────────────────── #

with tab3:
    st.subheader("Resume Improver")
    st.caption("Upload or paste your resume — AI will rewrite it ATS optimized.")

    improve_option = st.radio(
        "Resume input method",
        ["Upload PDF", "Upload DOCX", "Paste Text"],
        horizontal=True,
        key="improve_radio"
    )

    improve_text = ""

    if improve_option == "Upload PDF":
        imp_file = st.file_uploader("Upload resume PDF", type=["pdf"], key="imp_pdf")
        if imp_file:
            improve_text = parse_pdf(imp_file)
            if not improve_text.strip():
                st.error(
                    "❌ Could not read text from this PDF. "
                    "Please upload a valid text-based resume PDF "
                    "(not a scanned image or photo)."
                )
                improve_text = ""
            else:
                st.success("✅ PDF parsed successfully.")

    elif improve_option == "Upload DOCX":
        imp_file = st.file_uploader("Upload resume DOCX", type=["docx"], key="imp_docx")
        if imp_file:
            improve_text = parse_docx(imp_file)
            if not improve_text.strip():
                st.error(
                    "❌ Could not read text from this DOCX. "
                    "Please upload a valid resume document."
                )
                improve_text = ""
            else:
                st.success("✅ DOCX parsed successfully.")

    else:
        improve_text = st.text_area("Paste your resume here", height=320, key="improve_text")

    if st.button("✨ Improve Resume", type="primary"):
        if not improve_text.strip():
            st.warning("⚠️ Please upload a valid resume or paste your resume text first.")
        else:
            with st.spinner("Groq AI is improving your resume..."):
                st.session_state.improved_result = improve_resume(improve_text)

    if st.session_state.improved_result:
        st.markdown("---")
        st.markdown(st.session_state.improved_result)

        first_line = improve_text.strip().split('\n')[0] if improve_text.strip() else "resume"
        safe_name = first_line[:30].replace(" ", "_").replace("/", "")
        docx_bytes = markdown_to_docx(st.session_state.improved_result, safe_name)

        st.download_button(
            "⬇️ Download Improved Resume (DOCX)",
            data=docx_bytes,
            file_name="improved_resume.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        st.download_button(
            "⬇️ Download as Markdown",
            data=st.session_state.improved_result,
            file_name="improved_resume.md",
            mime="text/markdown"
        )


# ─────────────────────── TIPS ─────────────────────── #

with tab4:
    st.subheader("Resume Tips")

    tips()

    st.markdown("---")
    st.markdown("### Get Role-Specific Tips from AI")
    role = st.text_input("Enter your target job title (e.g. SOC Analyst, Data Scientist)")

    if st.button("💡 Get AI Tips", type="primary"):
        if not role.strip():
            st.warning("⚠️ Please enter a job title first.")
        else:
            with st.spinner("Getting tips from Groq AI..."):
                st.session_state.role_tips = get_role_tips(role)

    if st.session_state.role_tips:
        st.markdown(st.session_state.role_tips)
