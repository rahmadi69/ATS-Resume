import streamlit as st
from resume_parser import parse_pdf, parse_docx
from ai_engine import ats_check, improve_resume, build_resume, get_role_tips
from ui_components import header, tips

st.set_page_config(page_title="ResumeAI", page_icon="📄", layout="wide")

header()

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 ATS Checker",
    "🏗️ Resume Builder",
    "✏️ Resume Improver",
    "💡 Tips"
])


# ─────────────────────── ATS CHECKER ─────────────────────── #

with tab1:
    st.subheader("ATS Resume Checker")

    option = st.radio(
        "How do you want to provide your resume?",
        ["Upload PDF", "Upload DOCX", "Paste Text"],
        horizontal=True
    )

    resume_text = ""

    if option == "Upload PDF":
        file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
        if file:
            resume_text = parse_pdf(file)
            st.success("PDF parsed successfully.")

    elif option == "Upload DOCX":
        file = st.file_uploader("Upload your resume (DOCX)", type=["docx"])
        if file:
            resume_text = parse_docx(file)
            st.success("DOCX parsed successfully.")

    else:
        resume_text = st.text_area("Paste your resume here", height=300)

    job_desc = st.text_area("Paste the Job Description here", height=200)

    if st.button("🔍 Analyze Resume", type="primary"):
        if not resume_text.strip():
            st.warning("Please upload or paste your resume first.")
        elif not job_desc.strip():
            st.warning("Please paste a job description to compare against.")
      else:
            with st.spinner("Analyzing with Groq AI..."):
                result = ats_check(resume_text, job_desc)
            if result:
                st.markdown(result)

# ─────────────────────── RESUME BUILDER ─────────────────────── #

with tab2:
    st.subheader("AI Resume Builder")
    st.caption("Fill in your details and Gemini will write a professional resume for you.")

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Full Name")
        skills = st.text_input("Skills (comma separated)")
        certs = st.text_input("Certifications")

    with col2:
        education = st.text_area("Education", height=100)
        projects = st.text_area("Projects", height=100)

    experience = st.text_area("Work Experience", height=150)

    if st.button("🚀 Generate Resume", type="primary"):
        if not name.strip():
            st.warning("Please enter your name.")
        else:
            with st.spinner("Gemini is building your resume..."):
                resume = build_resume(name, education, experience, skills, projects, certs)
            if resume:
                st.markdown("---")
                st.markdown(resume)
                st.download_button(
                    "⬇️ Download as Markdown",
                    data=resume,
                    file_name=f"{name.replace(' ', '_')}_resume.md",
                    mime="text/markdown"
                )


# ─────────────────────── RESUME IMPROVER ─────────────────────── #

with tab3:
    st.subheader("Resume Improver")
    st.caption("Paste your existing resume and Gemini will rewrite it to be ATS optimized.")

    text = st.text_area("Paste your resume here", height=350)

    if st.button("✨ Improve Resume", type="primary"):
        if not text.strip():
            st.warning("Please paste your resume first.")
        else:
            with st.spinner("Gemini is improving your resume..."):
                result = improve_resume(text)
            if result:
                st.markdown("---")
                st.markdown(result)
                st.download_button(
                    "⬇️ Download Improved Resume",
                    data=result,
                    file_name="improved_resume.md",
                    mime="text/markdown"
                )


# ─────────────────────── TIPS ─────────────────────── #

with tab4:
    st.subheader("Resume Tips")

    tips()

    st.markdown("---")
    st.markdown("### Get Role-Specific Tips from AI")
    role = st.text_input("Enter your target job title (e.g. Software Engineer, Data Analyst)")

    if st.button("💡 Get AI Tips", type="primary"):
        if not role.strip():
            st.warning("Enter a job title first.")
        else:
            with st.spinner("Getting tips from Gemini..."):
                ai_tips = get_role_tips(role)
            if ai_tips:
                st.markdown(ai_tips)
