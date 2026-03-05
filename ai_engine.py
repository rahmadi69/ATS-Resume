import os
import time
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


def _call_groq(prompt: str, max_tokens: int = 2048, retries: int = 3) -> str:
    """Call Groq API with automatic retry on 429 rate limit errors."""
    api_key = get_api_key()
    if not api_key:
        st.error("⚠️ Groq API key missing. Add GROQ_API_KEY to Streamlit Secrets.")
        st.stop()

    client = Groq(api_key=api_key)

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            return response.choices[0].message.content

        except Exception as e:
            error_str = str(e)

            # Rate limit hit — wait and retry
            if "429" in error_str or "rate_limit" in error_str.lower() or "RATE_LIMIT" in error_str:
                if attempt < retries - 1:
                    wait_time = 20 * (attempt + 1)  # 20s, 40s, 60s
                    with st.warning(
                        f"⏳ Too many requests. Retrying in {wait_time} seconds... "
                        f"(Attempt {attempt + 1}/{retries})"
                    ):
                        time.sleep(wait_time)
                    continue
                else:
                    st.error(
                        "⚠️ The AI service is currently busy due to high traffic. "
                        "Please wait 1-2 minutes and try again."
                    )
                    return ""

            # Any other error
            st.error(f"⚠️ Something went wrong: {error_str[:200]}")
            return ""

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
