import streamlit as st
from resume_parser import parse_pdf, parse_docx
from ai_engine import ats_check, improve_resume, build_resume
from ui_components import header, tips

st.set_page_config(page_title="ResumeAI", layout="wide")

header()

tab1, tab2, tab3, tab4 = st.tabs(
    ["ATS Checker", "Resume Builder", "Resume Improver", "Tips"]
)

# ---------------- ATS CHECKER ---------------- #

with tab1:

    st.subheader("Upload or Paste Resume")

    option = st.radio(
        "Resume Input",
        ["Upload PDF", "Upload DOCX", "Paste Text"]
    )

    resume_text = ""

    if option == "Upload PDF":

        file = st.file_uploader("Upload PDF", type=["pdf"])

        if file:
            resume_text = parse_pdf(file)

    elif option == "Upload DOCX":

        file = st.file_uploader("Upload DOCX", type=["docx"])

        if file:
            resume_text = parse_docx(file)

    else:

        resume_text = st.text_area(
            "Paste Resume",
            height=300
        )

    job_desc = st.text_area(
        "Paste Job Description",
        height=200
    )

    if st.button("Analyze Resume"):

        if resume_text:

            with st.spinner("Analyzing..."):

                result = ats_check(
                    resume_text,
                    job_desc
                )

                st.markdown(result)

        else:
            st.warning("Upload or paste a resume first.")


# ---------------- RESUME BUILDER ---------------- #

with tab2:

    st.subheader("Build Resume")

    name = st.text_input("Name")

    education = st.text_area("Education")

    experience = st.text_area("Experience")

    skills = st.text_input("Skills")

    projects = st.text_area("Projects")

    certs = st.text_input("Certifications")

    if st.button("Generate Resume"):

        with st.spinner("Generating..."):

            resume = build_resume(
                name,
                education,
                experience,
                skills,
                projects,
                certs
            )

            st.markdown(resume)


# ---------------- RESUME IMPROVER ---------------- #

with tab3:

    text = st.text_area(
        "Paste Resume Section",
        height=300
    )

    if st.button("Improve Resume"):

        with st.spinner("Improving..."):

            result = improve_resume(text)

            st.markdown(result)


# ---------------- TIPS ---------------- #

with tab4:

    tips()
