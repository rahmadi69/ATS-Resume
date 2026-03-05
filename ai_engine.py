from google import genai
import streamlit as st
from prompts import ATS_PROMPT, IMPROVE_PROMPT, BUILDER_PROMPT

api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("Gemini API key missing in Streamlit secrets.")
    st.stop()

client = genai.Client(api_key=api_key)


def ats_check(resume, job):

    prompt = ATS_PROMPT.format(
        resume=resume,
        job_description=job
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    return response.text if hasattr(response, "text") else str(response)


def improve_resume(text):

    prompt = IMPROVE_PROMPT.format(resume=text)

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    return response.text if hasattr(response, "text") else str(response)


def build_resume(name, education, exp, skills, projects, certs):

    prompt = BUILDER_PROMPT.format(
        name=name,
        education=education,
        experience=exp,
        skills=skills,
        projects=projects,
        certs=certs
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    return response.text if hasattr(response, "text") else str(response)
