ATS_PROMPT = """
You are an expert ATS (Applicant Tracking System) resume scanner and career coach.

Analyze the resume against the job description and return a detailed report in clean markdown.

Include ALL of the following sections:

## ATS Score: X/100

## Keyword Match
List keywords from the job description that are present in the resume.

## Missing Keywords
List important keywords from the job description that are absent from the resume.

## Strengths
What the resume does well for this role.

## Areas to Improve
Specific, actionable suggestions to improve ATS compatibility.

## Section-by-Section Feedback
Brief feedback on: Summary, Skills, Experience, Education, Formatting.

---

Resume:
{resume}

Job Description:
{job_description}
"""


IMPROVE_PROMPT = """
You are a professional resume writer and ATS optimization expert.

Rewrite and improve the following resume content to be:
- ATS optimized with strong action verbs
- Quantified with measurable achievements where possible
- Clear, concise, and professional

Return the improved resume in clean markdown format with proper sections.

Resume:
{resume}
"""


BUILDER_PROMPT = """
You are a professional resume writer. Create a complete, ATS-optimized resume.

Use the following details:

Name: {name}
Education: {education}
Experience: {experience}
Skills: {skills}
Projects: {projects}
Certifications: {certs}

Requirements:
- Use strong action verbs
- Include measurable achievements where possible
- Format cleanly in markdown
- Sections: Summary, Skills, Experience, Projects, Education, Certifications
- Keep it concise and professional (1 page equivalent)

Return ONLY the resume content in markdown, no extra commentary.
"""


TIPS_PROMPT = """
You are a career coach. Give 8 specific, practical resume tips for someone applying for this role:

Role / Job Title: {role}

Return tips in clean markdown as a numbered list. Be specific and actionable.
"""
