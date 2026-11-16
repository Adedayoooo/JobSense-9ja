import json
from groq import Groq
from src.config import GROQ_API_KEY, MODEL
import logging

logging.basicConfig(level=logging.INFO,format='%(asctime)s | %(levelname)s | %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

client = Groq(api_key=GROQ_API_KEY)

def ask(prompt, system_prompt=None, temperature=0.3, as_json=False):
    messages = []

    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=temperature,
        response_format={"type": "json_object"} if as_json else None
    )

    raw_response = response.choices[0].message.content

    if as_json:
        return json.loads(raw_response)
    else:
        return raw_response

JD_SYSTEM_PROMPT = """
You are an expert recruiter and job market analyst.
Analyze the job description and extract key information.
Return ONLY valid JSON, nothing else.
"""

def analyze_job_description(jd_text: str) -> dict:
    prompt = f"""
Analyze this job description and return JSON with exactly these fields:

{{
    "company_name": "company name or Unknown",
    "role_title": "exact job title",
    "seniority": "junior or mid or senior or lead",
    "experience_years_required": number or 0 if not stated,
    "required_skills": ["skill1", "skill2"],
    "nice_to_have_skills": ["skill1", "skill2"],
    "key_responsibilities": ["responsibility1", "responsibility2"],
    "company_signals": ["fast-paced", "remote-friendly", etc],
    "red_flags": ["any concerning phrases"],
    "location": "city/country or Remote",
    "salary_mentioned": true or false,
    "summary": "2 sentence plain English summary of the role"
}}

Job Description:
{jd_text}
"""
    return ask(prompt, system_prompt=JD_SYSTEM_PROMPT,
               temperature=0.1, as_json=True)

CV_SYSTEM_PROMPT = """
You are an expert technical recruiter reviewing a candidate's CV.
Extract information accurately. Do not infer skills not explicitly mentioned.
Return ONLY valid JSON, nothing else.
"""

def analyze_cv(cv_text: str) -> dict:
    prompt = f"""
Analyze this CV and return JSON with at least the fields below. Do NOT leave out any extra revenant info. If you do see any extra relevant info not covered in the fields, create a new field with the appropriate name to classify that info.

{{
    "candidate_name": "full name",
    "current_role": "current or most recent role title",
    "total_experience_years": number,
    "technical_skills": ["skill1", "skill2"],
    "ml_specific_skills": ["only ML/AI related skills"],
    "tools_and_frameworks": ["Docker", "FastAPI", etc],
    "projects": [
        {{
            "name": "project name",
            "description": "one sentence",
            "technologies": ["tech1", "tech2"],
            "impact": "measurable result if any"
        }}
    ],
    "education": "degree, institution, year",
    "strengths": ["strength1", "strength2"],
    "gaps": ["potential weakness1", "potential weakness2"]
}}

CV Text:
{cv_text}
"""
    return ask(prompt, system_prompt=CV_SYSTEM_PROMPT,
               temperature=0.1, as_json=True)
