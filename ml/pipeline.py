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
    aptitude = student_data.get("aptitude", {})
    soft_skills = student_data.get("soft_skills", {})
    
    # Branch
    raw_branch = student_data.get("branch", "CSE")
    is_cs = BRANCH_MAPPING.get(raw_branch, 1 if "computer" in raw_branch.lower() or "information" in raw_branch.lower() else 0)
    
    # Aptitude fallback
    quant = aptitude.get("Quantitative", student_data.get("quantitative_aptitude", 70.0))
    logical = aptitude.get("Logical", student_data.get("logical_reasoning", 70.0))
    coding = aptitude.get("Coding", student_data.get("coding_benchmark", 65.0))
    
    # Soft skills
    comm = soft_skills.get("Communication", student_data.get("communication_rating", 7.0))
    interview = soft_skills.get("Interview", student_data.get("interview_rating", 7.0))
    
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
        "quantitative_aptitude": float(quant),
        "logical_reasoning": float(logical),
        "coding_benchmark": float(coding),
        "skills_python": float(skills.get("Python", 5.0)),
        "skills_java": float(skills.get("Java", 5.0)),
        "skills_cpp": float(skills.get("C++", skills.get("C", 4.0))),
        "skills_dsa": float(skills.get("DSA", 5.0)),
        "skills_sql": float(skills.get("SQL", 5.0)),
        "skills_web": float(skills.get("React", skills.get("JavaScript", skills.get("Web", 5.0)))),
        "skills_cloud": float(skills.get("AWS", skills.get("Docker", skills.get("Cloud", 4.0)))),
        "skills_ml": float(skills.get("Machine Learning", skills.get("Pandas", 4.0))),
        "internships": intern_count,
        "projects_count": proj_count,
        "certifications_count": cert_count,
        "hackathons": int(student_data.get("hackathons", 0)),
        "communication_rating": float(comm),
        "interview_rating": float(interview),
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
