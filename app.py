import re
import streamlit as st
from resume_parser import parse_pdf, parse_docx
from ai_engine import (
    ats_check, improve_resume, build_resume,
    get_role_tips, suggest_skills, improve_experience_bullets,
    career_fit
)
from ui_components import (
    header, tips, footer,
    ats_explainer, score_card,
    next_steps_after_ats,
    next_steps_after_build,
    next_steps_after_improve
)
from resume_to_docx import markdown_to_docx

st.set_page_config(
    page_title="ResumeAI — Free ATS Resume Checker & Builder",
    page_icon="📄",
    layout="centered"
)

# ── Session state init ──
for key in ["ats_result", "ats_resume_text", "ats_score",
            "career_fit_result", "improved_result", "built_resume",
            "skill_suggestions", "exp_bullets", "role_tips"]:
    if key not in st.session_state:
        st.session_state[key] = "" if key != "ats_score" else 0

header()

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Check Resume",
    "✍️ Build Resume",
    "🔧 Improve Resume",
    "💡 Tips & Advice"
])


# ─────────────────────── ATS CHECKER ─────────────────────── #

with tab1:

    ats_explainer()

    st.markdown('<div class="section-header">📤 Your Resume</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Upload your resume or paste the text below</div>', unsafe_allow_html=True)

    option = st.radio(
        "Choose input method",
        ["📄 Upload PDF", "📝 Upload DOCX", "✏️ Paste Text"],
        horizontal=True,
        label_visibility="collapsed"
    )

    resume_text = ""

    if option == "📄 Upload PDF":
        file = st.file_uploader(
            "Upload PDF",
            type=["pdf"],
            help="Upload a text-based PDF resume. Scanned or image PDFs won't work.",
            label_visibility="collapsed"
        )
        if file:
            try:
                resume_text = parse_pdf(file)
                if not resume_text.strip():
                    st.error("❌ Could not read text from this PDF. Please upload a text-based resume PDF — not a scanned image or photo of a resume.")
                    resume_text = ""
                else:
                    st.success(f"✅ Resume loaded — {len(resume_text.split())} words detected.")
            except Exception:
                st.error("❌ Failed to read PDF. Please try a different file.")
                resume_text = ""

    elif option == "📝 Upload DOCX":
        file = st.file_uploader(
            "Upload DOCX",
            type=["docx"],
            help="Upload a Word document resume.",
            label_visibility="collapsed"
        )
        if file:
            try:
                resume_text = parse_docx(file)
                if not resume_text.strip():
                    st.error("❌ Could not read text from this DOCX. Please upload a valid Word resume document.")
                    resume_text = ""
                else:
                    st.success(f"✅ Resume loaded — {len(resume_text.split())} words detected.")
            except Exception:
                st.error("❌ Failed to read DOCX. Please try a different file.")
                resume_text = ""

    else:
        resume_text = st.text_area(
            "Paste your resume here",
            height=260,
            placeholder="Paste your full resume text here...\n\nExample:\nJohn Doe\njohn@email.com | LinkedIn\n\nSummary\nSoftware engineer with 3 years experience...\n\nSkills\nPython, SQL, React, AWS...",
            label_visibility="collapsed"
        )

    st.markdown('<div class="section-header">💼 Job Description</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Copy the job description from LinkedIn, Indeed, or Naukri and paste it here</div>', unsafe_allow_html=True)

    job_desc = st.text_area(
        "Job description",
        height=180,
        placeholder="Paste the full job description here...\n\nTip: Copy it directly from the job posting on LinkedIn or Indeed.",
        label_visibility="collapsed"
    )

    if st.button("🔍 Check My ATS Score", type="primary"):
        if not resume_text.strip():
            st.warning("⚠️ Please upload or paste your resume first.")
        elif not job_desc.strip():
            st.warning("⚠️ Please paste a job description. You can copy it from LinkedIn or Indeed.")
        else:
            with st.spinner("🤖 AI is analyzing your resume..."):
                result = ats_check(resume_text, job_desc)
                st.session_state.ats_result = result
                st.session_state.ats_resume_text = resume_text
                st.session_state.career_fit_result = ""

                # Extract score from result
                score = 0
                try:
                    match = re.search(r'(\d{1,3})\s*/\s*100|(\d{1,3})%', result)
                    if match:
                        score = int(match.group(1) or match.group(2))
                        score = max(0, min(100, score))
                except Exception:
                    score = 0
                st.session_state.ats_score = score

    # ── Results ──
    if st.session_state.ats_result:

        # Score card
        if st.session_state.ats_score > 0:
            score_card(st.session_state.ats_score)

        # Full AI result in styled card
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown(st.session_state.ats_result)
        st.markdown('</div>', unsafe_allow_html=True)

        # Next steps
        next_steps_after_ats()

        # Career fit
        st.markdown("---")
        st.markdown('<div class="section-header">🎯 Where Should You Apply?</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Based on your resume, AI will suggest which job roles match you best right now</div>', unsafe_allow_html=True)

        if st.button("🔎 Find My Best Job Matches"):
            with st.spinner("🤖 Analyzing your career profile..."):
                st.session_state.career_fit_result = career_fit(
                    st.session_state.ats_resume_text
                )

    if st.session_state.career_fit_result:
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown(st.session_state.career_fit_result)
        st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────── RESUME BUILDER ─────────────────────── #

with tab2:

    st.markdown("""
<div class="info-box">
    <strong>✍️ How this works:</strong> Fill in your details below — even rough notes are fine.
    AI will turn them into a professional, ATS-optimized resume and generate a Word document for you to download.
    <br><br><strong>No experience?</strong> No problem — just fill in your projects, education, and skills.
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="section-header">👤 Personal Details</div>', unsafe_allow_html=True)

    name = st.text_input(
        "Full Name",
        placeholder="e.g. Muzzammil Khan"
    )

    st.markdown('<div class="section-header">🎓 Education</div>', unsafe_allow_html=True)

    education = st.text_area(
        "Education",
        height=90,
        placeholder="e.g. BCA — Nandi Institute of Management and Science, Bellary (2022–2025)\n12th — XYZ School (2022)",
        label_visibility="collapsed"
    )

    st.markdown('<div class="section-header">🛠️ Skills</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">List your technical and soft skills — the more the better for ATS</div>', unsafe_allow_html=True)

    skills = st.text_input(
        "Skills",
        placeholder="e.g. Python, Machine Learning, SQL, Git, Linux, Cybersecurity, Streamlit",
        label_visibility="collapsed"
    )

    if skills.strip():
        if st.button("💡 Suggest More Skills Based on What I Typed"):
            with st.spinner("Finding relevant skills..."):
                st.session_state.skill_suggestions = suggest_skills(skills)

    if st.session_state.skill_suggestions:
        st.markdown(f"""
<div class="info-box">
    <strong>💡 Suggested skills to add:</strong><br>{st.session_state.skill_suggestions}
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="section-header">💼 Work Experience</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">No work experience? Leave this blank or describe internships, freelance work, or college activities</div>', unsafe_allow_html=True)

    experience = st.text_area(
        "Experience",
        height=130,
        placeholder="e.g. Intern at ABC Company (June 2024 — Aug 2024)\n- Worked on Python automation scripts\n- Helped with data analysis using Pandas\n\nOr for freshers:\n- No formal experience yet (just leave blank)",
        label_visibility="collapsed"
    )

    if experience.strip():
        if st.button("✨ Rewrite My Experience with Strong Action Verbs"):
            with st.spinner("Improving your experience bullets..."):
                st.session_state.exp_bullets = improve_experience_bullets(experience)

    if st.session_state.exp_bullets:
        st.markdown("""
<div class="info-box">
    <strong>✨ AI-improved version — copy this into the box above:</strong>
</div>
""", unsafe_allow_html=True)
        st.code(st.session_state.exp_bullets, language=None)

    st.markdown('<div class="section-header">🚀 Projects</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Projects are very important for freshers — list everything you have built</div>', unsafe_allow_html=True)

    projects = st.text_area(
        "Projects",
        height=120,
        placeholder="e.g. Mini-SIEM AI — Python, Streamlit, Scikit-learn\nDetects threats in log files using ML. Achieved 97% accuracy.\n\nPhishing Detector — Python, NLP\nClassifies phishing URLs with 0.97 accuracy.",
        label_visibility="collapsed"
    )

    st.markdown('<div class="section-header">🏆 Certifications</div>', unsafe_allow_html=True)

    certs = st.text_input(
        "Certifications",
        placeholder="e.g. Google Cybersecurity Certificate, HuggingFace AI Agents, AWS Cloud Practitioner",
        label_visibility="collapsed"
    )

    if st.button("🚀 Build My Resume Now", type="primary"):
        if not name.strip():
            st.warning("⚠️ Please enter your full name to continue.")
        else:
            with st.spinner("🤖 AI is writing your professional resume..."):
                st.session_state.built_resume = build_resume(
                    name, education, experience, skills, projects, certs
                )

    if st.session_state.built_resume:
        st.markdown("---")
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown(st.session_state.built_resume)
        st.markdown('</div>', unsafe_allow_html=True)

        next_steps_after_build()

        try:
            docx_bytes = markdown_to_docx(st.session_state.built_resume, name)
            safe_name = name.strip().replace(" ", "_") if name.strip() else "resume"
            st.download_button(
                "⬇️ Download Resume as Word Document (.docx)",
                data=docx_bytes,
                file_name=f"{safe_name}_resume.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        except Exception:
            pass

        st.download_button(
            "⬇️ Download Resume as Markdown (.md)",
            data=st.session_state.built_resume,
            file_name=f"{name.strip().replace(' ', '_') or 'resume'}_resume.md",
            mime="text/markdown"
        )


# ─────────────────────── RESUME IMPROVER ─────────────────────── #

with tab3:

    st.markdown("""
<div class="info-box">
    <strong>🔧 How this works:</strong> Upload or paste your existing resume.
    AI will rewrite it with stronger language, better structure, and ATS-friendly keywords —
    then generate a Word document you can download immediately.
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="section-header">📤 Upload Your Existing Resume</div>', unsafe_allow_html=True)

    improve_option = st.radio(
        "Choose input method",
        ["📄 Upload PDF", "📝 Upload DOCX", "✏️ Paste Text"],
        horizontal=True,
        key="improve_radio",
        label_visibility="collapsed"
    )

    improve_text = ""

    if improve_option == "📄 Upload PDF":
        imp_file = st.file_uploader(
            "Upload PDF",
            type=["pdf"],
            key="imp_pdf",
            label_visibility="collapsed"
        )
        if imp_file:
            try:
                improve_text = parse_pdf(imp_file)
                if not improve_text.strip():
                    st.error("❌ Could not read text from this PDF. Please upload a text-based resume PDF — not a scanned image.")
                    improve_text = ""
                else:
                    st.success(f"✅ Resume loaded — {len(improve_text.split())} words detected.")
            except Exception:
                st.error("❌ Failed to read PDF. Please try a different file.")
                improve_text = ""

    elif improve_option == "📝 Upload DOCX":
        imp_file = st.file_uploader(
            "Upload DOCX",
            type=["docx"],
            key="imp_docx",
            label_visibility="collapsed"
        )
        if imp_file:
            try:
                improve_text = parse_docx(imp_file)
                if not improve_text.strip():
                    st.error("❌ Could not read text from this DOCX. Please upload a valid Word document.")
                    improve_text = ""
                else:
                    st.success(f"✅ Resume loaded — {len(improve_text.split())} words detected.")
            except Exception:
                st.error("❌ Failed to read DOCX. Please try a different file.")
                improve_text = ""

    else:
        improve_text = st.text_area(
            "Paste resume",
            height=300,
            key="improve_text",
            placeholder="Paste your existing resume text here and AI will rewrite it to be stronger and ATS-optimized...",
            label_visibility="collapsed"
        )

    if st.button("🔧 Improve My Resume Now", type="primary"):
        if not improve_text.strip():
            st.warning("⚠️ Please upload or paste your resume first.")
        else:
            with st.spinner("🤖 AI is rewriting your resume..."):
                st.session_state.improved_result = improve_resume(improve_text)

    if st.session_state.improved_result:
        st.markdown("---")
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown(st.session_state.improved_result)
        st.markdown('</div>', unsafe_allow_html=True)

        next_steps_after_improve()

        try:
            first_line = improve_text.strip().split('\n')[0] if improve_text.strip() else "resume"
            safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', first_line[:30])
            docx_bytes = markdown_to_docx(st.session_state.improved_result, safe_name)
            st.download_button(
                "⬇️ Download Improved Resume as Word Document (.docx)",
                data=docx_bytes,
                file_name="improved_resume.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        except Exception:
            pass

        st.download_button(
            "⬇️ Download as Markdown (.md)",
            data=st.session_state.improved_result,
            file_name="improved_resume.md",
            mime="text/markdown"
        )


# ─────────────────────── TIPS ─────────────────────── #

with tab4:

    st.markdown('<div class="section-header">📋 Resume Tips for Everyone</div>', unsafe_allow_html=True)
    tips()

    st.markdown("---")
    st.markdown('<div class="section-header">🎯 Get Tips for Your Specific Job</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Enter any job title and AI gives you 8 specific tips tailored for that role</div>', unsafe_allow_html=True)

    role = st.text_input(
        "Job title",
        placeholder="e.g. SOC Analyst, Software Engineer, Data Scientist, Product Manager",
        label_visibility="collapsed"
    )

    if st.button("💡 Get My Personalized Tips", type="primary"):
        if not role.strip():
            st.warning("⚠️ Please enter a job title first.")
        else:
            with st.spinner(f"🤖 Getting tips for {role}..."):
                st.session_state.role_tips = get_role_tips(role)

    if st.session_state.role_tips:
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown(st.session_state.role_tips)
        st.markdown('</div>', unsafe_allow_html=True)


# ── Footer ──
footer()
