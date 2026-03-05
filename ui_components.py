import streamlit as st


def header():

    st.markdown(
        """
        <h1 style='text-align:center;'>ResumeAI</h1>
        <p style='text-align:center;'>AI Powered • Free • ATS Resume Checker</p>
        """,
        unsafe_allow_html=True
    )


def tips():

    st.markdown("""
### Resume Tips

• Use simple formatting  
• Avoid images or graphics  
• Use strong action verbs  
• Include measurable achievements  
• Tailor resume for each job
""")
