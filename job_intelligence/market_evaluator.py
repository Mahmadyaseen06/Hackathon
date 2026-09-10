from __future__ import annotations
from typing import Dict, Any, List, Tuple
from .demo_data import build_demo_jobs
from .matcher import rank
from .models import StudentProfile, MatchCategory

def evaluate_market_grounding(student_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates student profile against all active campus job requisitions.
    Returns:
      - total_jobs: count of active requisitions evaluated
      - best_matches: count of BEST_MATCH roles (fit >= 78%)
      - near_matches: count of NEAR_MATCH roles (fit >= 58%)
      - stretch_matches: count of STRETCH roles
      - top_fit_score: highest fit score achieved
      - top_job_company: company offering highest fit
      - top_job_title: role title offering highest fit
      - is_market_viable: bool, True if at least one Best or Near match exists
    """
    skills = {}
    for k, v in student_data.get("skills", {}).items():
        try:
            skills[k] = float(v)
        except (ValueError, TypeError):
            skills[k] = 5.0

    certifications = []
    for c in student_data.get("certifications", []):
        if isinstance(c, str):
            certifications.append(c)
        elif isinstance(c, dict):
            certifications.append(c.get("name", ""))

    projects = []
    for p in student_data.get("projects", []):
        if isinstance(p, dict):
            projects.append(p)
        elif isinstance(p, str):
            projects.append({"name": p, "tags": []})

    internships = []
    for i in student_data.get("internships", []):
        if isinstance(i, dict):
            internships.append(i)
        elif isinstance(i, str):
            internships.append({"company": i, "role": "Intern"})

    profile = StudentProfile(
        student_id=student_data.get("student_id", student_data.get("usn", "STU")),
        branch=student_data.get("branch"),
        cgpa=float(student_data.get("cgpa", 7.0)),
        tenth_pct=float(student_data.get("tenth_percentage", 75.0)),
        twelfth_pct=float(student_data.get("twelfth_percentage", 75.0)),
        backlogs=int(student_data.get("active_backlogs", student_data.get("backlogs", 0))),
        semester=int(student_data.get("semester", 6)),
        target_role=student_data.get("primary_track", student_data.get("target_role", "Software Engineer")),
        skills=skills,
        certifications=certifications,
        projects=projects,
        internships=internships,
        aptitude=student_data.get("aptitude", {}),
        soft_skills=student_data.get("soft_skills", {})
    )

    jobs = build_demo_jobs()
    ranked = rank(jobs, profile, limit=50)

    best_count = 0
    near_count = 0
    stretch_count = 0

    for job, res in ranked:
        if res.category == MatchCategory.BEST_MATCH:
            best_count += 1
        elif res.category == MatchCategory.NEAR_MATCH:
            near_count += 1
        else:
            stretch_count += 1

    top_fit = 0.0
    top_co = "Market"
    top_role = "Software Role"
    if ranked:
        top_job, top_res = ranked[0]
        top_fit = round(top_res.job_fit_score, 1)
        top_co = top_job.company
        top_role = top_job.title

    return {
        "total_jobs": len(jobs),
        "best_matches": best_count,
        "near_matches": near_count,
        "stretch_matches": stretch_count,
        "top_fit_score": top_fit,
        "top_job_company": top_co,
        "top_job_title": top_role,
        "is_market_viable": (best_count + near_count) > 0
    }
