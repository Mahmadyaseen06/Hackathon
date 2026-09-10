"""
Feature Pipeline & Model Inference for AI Placement Predictor
Handles transformation, encoding, model inference, and target role mapping.
"""

from __future__ import annotations
from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "cgpa",
    "tenth_percentage",
    "twelfth_percentage",
    "backlogs_history",
    "active_backlogs",
    "quantitative_aptitude",
    "logical_reasoning",
    "coding_benchmark",
    "skills_python",
    "skills_java",
    "skills_cpp",
    "skills_dsa",
    "skills_sql",
    "skills_web",
    "skills_cloud",
    "skills_ml",
    "internships",
    "projects_count",
    "certifications_count",
    "hackathons",
    "communication_rating",
    "interview_rating",
    "is_cs_branch"
]

BRANCH_MAPPING = {
    "CSE": 1,
    "ISE": 1,
    "Computer Science & Engineering": 1,
    "Information Science & Engineering": 1,
    "ECE": 0,
    "Electronics & Communication Engineering": 0,
    "EEE": 0,
    "Electrical & Electronics Engineering": 0,
    "Mech": 0,
    "Mechanical Engineering": 0,
    "Civil": 0,
    "Civil Engineering": 0
}

def extract_features_from_student(student_data: Dict[str, Any]) -> pd.DataFrame:
    """Extract standard numerical feature vector from rich student profile dictionary."""
    skills = student_data.get("skills", {})
    if not isinstance(skills, dict):
        skills = {}
    aptitude = student_data.get("aptitude", {})
    if not isinstance(aptitude, dict):
        aptitude = {}
    soft_skills = student_data.get("soft_skills", {})
    if not isinstance(soft_skills, dict):
        soft_skills = {}

    level_map = {
        "beginner": 3.0, "basic": 3.0, "novice": 2.0,
        "intermediate": 6.0, "moderate": 5.0,
        "good": 7.0, "advanced": 8.5, "expert": 9.5
    }

    def _get_skill(*aliases) -> float:
        for a in aliases:
            for k, v in skills.items():
                if k.lower() == a.lower():
                    if isinstance(v, (int, float)):
                        return float(v)
                    if isinstance(v, str):
                        v_lower = v.strip().lower()
                        if v_lower in level_map:
                            return level_map[v_lower]
                        try:
                            return float(v)
                        except ValueError:
                            pass
        return 0.0

    # Branch
    raw_branch = str(student_data.get("branch", "CSE"))
    is_cs = BRANCH_MAPPING.get(raw_branch, 1 if "computer" in raw_branch.lower() or "information" in raw_branch.lower() or "data" in raw_branch.lower() or "ai" in raw_branch.lower() else 0)

    # Programming competency drives coding benchmark if untested
    p_skill = _get_skill("Python")
    j_skill = _get_skill("Java")
    c_skill = _get_skill("C++", "C")
    dsa_skill = _get_skill("DSA", "Data Structures", "Algorithms")
    sql_skill = _get_skill("SQL", "MySQL", "PostgreSQL", "Database")
    web_skill = _get_skill("React", "JavaScript", "Web", "Node.js", "HTML/CSS")
    cloud_skill = _get_skill("AWS", "Docker", "Cloud", "Azure", "GCP")
    ml_skill = _get_skill("Machine Learning", "Pandas", "AI", "Data Science")

    max_core_skill = max(p_skill, j_skill, c_skill, dsa_skill)
    estimated_coding = max(15.0, min(95.0, max_core_skill * 9.0 + dsa_skill * 3.0))

    # Aptitude fallback (neutral 45 if unassessed)
    quant = float(aptitude.get("Quantitative", student_data.get("quantitative_aptitude", 45.0)))
    logical = float(aptitude.get("Logical", student_data.get("logical_reasoning", 45.0)))
    coding = float(aptitude.get("Coding", student_data.get("coding_benchmark", estimated_coding)))

    # Soft skills fallback
    comm = float(soft_skills.get("Communication", student_data.get("communication_rating", 5.0)))
    interview = float(soft_skills.get("Interview", student_data.get("interview_rating", 5.0)))

    # Internships count
    raw_internships = student_data.get("internships", [])
    intern_count = len(raw_internships) if isinstance(raw_internships, list) else int(raw_internships or 0)

    # Projects count
    raw_projects = student_data.get("projects", [])
    proj_count = len(raw_projects) if isinstance(raw_projects, list) else int(raw_projects or 0)

    # Certifications count
    raw_certs = student_data.get("certifications", [])
    cert_count = len(raw_certs) if isinstance(raw_certs, list) else int(raw_certs or 0)

    row = {
        "cgpa": float(student_data.get("cgpa", 7.0)),
        "tenth_percentage": float(student_data.get("tenth_percentage", 75.0)),
        "twelfth_percentage": float(student_data.get("twelfth_percentage", 75.0)),
        "backlogs_history": int(student_data.get("backlogs_history", 0)),
        "active_backlogs": int(student_data.get("active_backlogs", 0)),
        "quantitative_aptitude": quant,
        "logical_reasoning": logical,
        "coding_benchmark": coding,
        "skills_python": p_skill,
        "skills_java": j_skill,
        "skills_cpp": c_skill,
        "skills_dsa": dsa_skill,
        "skills_sql": sql_skill,
        "skills_web": web_skill,
        "skills_cloud": cloud_skill,
        "skills_ml": ml_skill,
        "internships": intern_count,
        "projects_count": proj_count,
        "certifications_count": cert_count,
        "hackathons": int(student_data.get("hackathons", 0)),
        "communication_rating": comm,
        "interview_rating": interview,
        "is_cs_branch": int(is_cs)
    }

    return pd.DataFrame([row])[FEATURE_COLUMNS]

def predict_career_track_alignment(features: pd.DataFrame) -> List[Dict[str, Any]]:
    """Predict alignment and confidence levels across institutional career tracks."""
    row = features.iloc[0]
    
    tracks = [
        {
            "track": "Full-Stack Developer",
            "score": 0.35 * row["skills_web"] + 0.25 * row["skills_dsa"] + 0.20 * row["skills_sql"] + 0.20 * (row["coding_benchmark"] / 10.0),
            "match_pct": 0.0
        },
        {
            "track": "Data Analyst / ML Engineer",
            "score": 0.35 * row["skills_ml"] + 0.25 * row["skills_python"] + 0.25 * row["skills_sql"] + 0.15 * (row["quantitative_aptitude"] / 10.0),
            "match_pct": 0.0
        },
        {
            "track": "Cloud / DevOps Engineer",
            "score": 0.40 * row["skills_cloud"] + 0.25 * row["skills_python"] + 0.20 * row["skills_dsa"] + 0.15 * (row["logical_reasoning"] / 10.0),
            "match_pct": 0.0
        },
        {
            "track": "QA & Automation Specialist",
            "score": 0.35 * row["skills_java"] + 0.25 * row["skills_sql"] + 0.20 * row["communication_rating"] + 0.20 * (row["logical_reasoning"] / 10.0),
            "match_pct": 0.0
        },
        {
            "track": "Core Systems / SDE",
            "score": 0.40 * row["skills_dsa"] + 0.30 * row["skills_cpp"] + 0.20 * (row["coding_benchmark"] / 10.0) + 0.10 * row["cgpa"],
            "match_pct": 0.0
        }
    ]
    
    # Normalize to percentages summing to 100%
    total_score = sum(t["score"] for t in tracks) or 1.0
    for t in tracks:
        t["match_pct"] = round((t["score"] / total_score) * 100.0, 1)
        
    tracks.sort(key=lambda x: x["match_pct"], reverse=True)
    return tracks
