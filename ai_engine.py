import os
import streamlit as st
from groq import Groq
from prompts import (
    ATS_PROMPT, IMPROVE_PROMPT, BUILDER_PROMPT,
    TIPS_PROMPT, SKILLS_SUGGEST_PROMPT, EXPERIENCE_SUGGEST_PROMPT,
    CAREER_FIT_PROMPT
)


def get_api_key():
    try:
        key = st.secrets.get("GROQ_API_KEY", None)
        if key:
            return key
    except Exception:
        pass
    return os.getenv("GROQ_API_KEY", "")


def _call_groq(prompt: str, max_tokens: int = 2048) -> str:
    api_key = get_api_key()
    if not api_key:
        st.error("⚠️ Groq API key missing. Add GROQ_API_KEY to Streamlit Secrets.")
        st.stop()
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Groq API error: {e}")
        return ""


def ats_check(resume: str, job: str) -> str:
    return _call_groq(ATS_PROMPT.format(resume=resume, job_description=job))


def improve_resume(text: str) -> str:
    return _call_groq(IMPROVE_PROMPT.format(resume=text))


def build_resume(name, education, exp, skills, projects, certs) -> str:
    return _call_groq(BUILDER_PROMPT.format(
        name=name, education=education, experience=exp,
        skills=skills, projects=projects, certs=certs
    ), max_tokens=3000)


def get_role_tips(role: str) -> str:
    return _call_groq(TIPS_PROMPT.format(role=role))


def suggest_skills(skills: str) -> str:
    return _call_groq(SKILLS_SUGGEST_PROMPT.format(skills=skills), max_tokens=200)


def improve_experience_bullets(experience: str) -> str:
    return _call_groq(EXPERIENCE_SUGGEST_PROMPT.format(experience=experience), max_tokens=500)


def career_fit(resume: str) -> str:
    return _call_groq(CAREER_FIT_PROMPT.format(resume=resume), max_tokens=2000)
