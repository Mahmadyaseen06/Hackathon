"""
CV Parser using pdfplumber (text extraction) + Ollama (AI understanding).
Extracts: name, skills, projects, education, certifications, internships
from any uploaded PDF resume/CV.
"""

import json
import re
import httpx
import asyncio
from pathlib import Path
from typing import Optional

try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2:3b"


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract raw text from a PDF file."""
    if not PDF_AVAILABLE:
        return ""
    import io
    text_chunks = []
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_chunks.append(text)
        return "\n".join(text_chunks)
    except Exception as e:
        return ""


async def parse_cv_with_ollama(cv_text: str) -> dict:
    """
    Use Ollama llama3.2:3b to extract structured student profile from CV text.
    Returns a structured dict ready to be saved as a student record.
    """
    if not cv_text.strip():
        return {}

    # Truncate to avoid token limit
    cv_text_trimmed = cv_text[:3000]

    prompt = f"""You are a CV parser. Extract structured information from this resume/CV text.

CV TEXT:
{cv_text_trimmed}

Extract and return ONLY valid JSON (no markdown, no explanation):
{{
  "name": "<full name>",
  "email": "<email if present, else null>",
  "phone": "<phone if present, else null>",
  "branch": "<engineering branch like 'Computer Science & Engineering' or 'Information Science', infer from skills if not explicit>",
  "cgpa": <CGPA as float if mentioned, else 7.5>,
  "semester": <semester number as integer if mentioned, else 7>,
  "skills": {{
    "<SkillName>": <proficiency 1-10 inferred from context, e.g. 'Python (Advanced)' = 8>
  }},
  "certifications": ["<cert1>", "<cert2>"],
  "internships": [
    {{"company": "<company>", "role": "<role>", "duration_months": <months>}}
  ],
  "projects": [
    {{"name": "<project name>", "tags": ["<tech1>", "<tech2>"], "complexity": "<Beginner|Intermediate|Advanced>"}}
  ],
  "target_role": "<inferred target role from resume, e.g. SDE, Data Scientist, ML Engineer>",
  "target_lpa": <expected salary as float, default 10.0>,
  "github_username": "<github username if mentioned, else null>",
  "leetcode_username": "<leetcode username if mentioned, else null>",
  "hackerrank_username": "<hackerrank username if mentioned, else null>",
  "quantitative_aptitude": 70,
  "logical_reasoning": 70,
  "coding_benchmark": 70,
  "communication_rating": 7.0,
  "interview_rating": 7.0,
  "active_backlogs": 0,
  "backlogs_history": 0
}}

Rules:
- Infer skill proficiency: 'proficient/strong' = 8, 'familiar/basic' = 5, 'expert/advanced' = 9, listed without qualifier = 6
- If branch not mentioned, infer from skills (Python/JS/Java → CSE, MATLAB/Arduino → ECE)
- Keep certifications short (just the name, no URLs)
- If something is not mentioned, use sensible defaults"""

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1, "num_predict": 600}
                }
            )
            response.raise_for_status()
            raw = response.json().get("response", "").strip()

            # Extract JSON from response
            json_match = re.search(r'\{.*\}', raw, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
    except Exception as e:
        pass

    return {}


def _rule_based_cv_parse(cv_text: str) -> dict:
    """Fallback rule-based CV parsing when Ollama is slow/unavailable."""
    import re

    # Extract name (first non-empty line often)
    lines = [l.strip() for l in cv_text.splitlines() if l.strip()]
    name = lines[0] if lines else "Unknown"

    # Extract email
    email_match = re.search(r'[\w.+-]+@[\w-]+\.[a-z]{2,}', cv_text, re.IGNORECASE)
    email = email_match.group() if email_match else None

    # Extract CGPA
    cgpa_match = re.search(r'(?:cgpa|gpa|cpi)[:\s]*([0-9]\.[0-9]{1,2})', cv_text, re.IGNORECASE)
    cgpa = float(cgpa_match.group(1)) if cgpa_match else 7.0

    # Extract skills from common keywords
    skill_keywords = ["Python", "Java", "C++", "JavaScript", "React", "Node.js", "SQL",
                      "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch",
                      "Django", "Flask", "MongoDB", "Docker", "Kubernetes", "AWS",
                      "Git", "Linux", "HTML", "CSS", "TypeScript", "Go", "Rust",
                      "Data Structures", "Algorithms", "DSA", "Computer Networks",
                      "Operating Systems", "Database", "R", "MATLAB"]
    found_skills = {}
    for skill in skill_keywords:
        if skill.lower() in cv_text.lower():
            found_skills[skill] = 6  # default proficiency

    # Extract GitHub username
    github_match = re.search(r'github\.com/([A-Za-z0-9_-]+)', cv_text, re.IGNORECASE)
    github_username = github_match.group(1) if github_match else None

    # Extract LeetCode
    lc_match = re.search(r'leetcode\.com/([A-Za-z0-9_-]+)', cv_text, re.IGNORECASE)
    lc_username = lc_match.group(1) if lc_match else None

    return {
        "name": name,
        "email": email,
        "phone": None,
        "branch": "Computer Science & Engineering",
        "cgpa": cgpa,
        "semester": 7,
        "skills": found_skills,
        "certifications": [],
        "internships": [],
        "projects": [],
        "target_role": "SDE",
        "target_lpa": 10.0,
        "github_username": github_username,
        "leetcode_username": lc_username,
        "hackerrank_username": None,
        "quantitative_aptitude": 70,
        "logical_reasoning": 70,
        "coding_benchmark": 70,
        "communication_rating": 7.0,
        "interview_rating": 7.0,
        "active_backlogs": 0,
        "backlogs_history": 0
    }


async def parse_cv(file_bytes: bytes, filename: str) -> dict:
    """
    Main CV parsing pipeline:
    1. Extract text from PDF
    2. Try Ollama AI parsing
    3. Fallback to rule-based if needed
    """
    cv_text = extract_text_from_pdf(file_bytes)
    if not cv_text:
        return {}

    # Try Ollama first
    result = await parse_cv_with_ollama(cv_text)
    if not result or not result.get("name"):
        # Fallback to rule-based
        result = _rule_based_cv_parse(cv_text)

    result["cv_text_preview"] = cv_text[:500]
    return result
