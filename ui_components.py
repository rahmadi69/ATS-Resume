import streamlit as st


def header():
    st.markdown(
        """
        <h1 style='text-align:center; color:#4F8BF9;'>ResumeAI</h1>
        <p style='text-align:center; font-size:1.1rem; color:#888;'>
            AI Powered &nbsp;•&nbsp; Free &nbsp;•&nbsp; ATS Resume Checker & Builder
        </p>
        <hr/>
        """,
        unsafe_allow_html=True
    )


def tips():
    st.markdown("""
### General Resume Tips

1. **Use simple formatting** — No tables, columns, or graphics. ATS can't read them.
2. **Use strong action verbs** — Led, Built, Improved, Designed, Reduced, Increased.
3. **Quantify achievements** — "Improved performance by 30%" beats "Improved performance".
4. **Tailor for each job** — Mirror keywords directly from the job description.
5. **Keep it 1 page** — Unless you have 10+ years of experience.
6. **Use standard section names** — Experience, Education, Skills, Projects, Certifications.
7. **Save as PDF** — Preserves formatting across all systems.
8. **No photos or logos** — ATS systems discard them and it wastes space.
""")
