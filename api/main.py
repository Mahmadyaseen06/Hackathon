"""
FastAPI Application Server for AI Placement Predictor
Institutional Career Readiness & Upskilling Engine
"""

from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Core ML & Upskilling
from ml.model_trainer import predict_student_employability, load_or_train_model
from ml.dataset_generator import generate_student_dataset
from upskilling.skill_gap_engine import diagnose_skill_gaps, load_benchmarks
from upskilling.roadmap_generator import generate_personalized_roadmap
from upskilling.content_recommender import get_content_recommendations
from upskilling.project_ladder import get_project_recommendations
from upskilling.internship_matcher import match_internships
from upskilling.monitoring_tracker import (
    log_student_activity, get_student_monitoring_metrics
)

# Job Intelligence
from job_intelligence.repository import (
    init_tables, list_active_jobs, get_job, get_company_statuses
)
from job_intelligence.matcher import score, rank
from job_intelligence.gap_engine import aggregate_gaps, summary_counts
from job_intelligence.roadmap_bridge import enrich_match_with_roadmap
from job_intelligence.refresh import (
    refresh_company_jobs, ensure_demo_fallback, refresh_status
)
from job_intelligence.models import StudentProfile

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = FastAPI(
    title="AI Placement Predictor API",
    description="Decode Employability DNA: Institutional Career Readiness & Upskilling Engine",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SEED_STUDENTS_PATH = DATA_DIR / "seed_students.json"

@app.on_event("startup")
def startup_event():
    log.info("Initializing persistence and pre-loading ML model ensemble...")
    init_tables()
    ensure_demo_fallback()
    try:
        load_or_train_model()
        log.info("ML model ensemble loaded successfully.")
    except Exception as e:
        log.warning("Model load deferred: %s", e)

# ----------------- Base Endpoints -----------------

@app.get("/api/health")
def health():
    return {"status": "healthy", "service": "AI Placement Predictor Engine", "version": "2.0.0"}

@app.get("/api/demo-students")
def get_demo_students():
    if SEED_STUDENTS_PATH.exists():
        with open(SEED_STUDENTS_PATH, "r") as f:
            return json.load(f)
    return []

@app.get("/api/benchmarks")
def get_track_benchmarks():
    return load_benchmarks()

# ----------------- Student ML & XAI Endpoints -----------------

@app.post("/api/predict")
def predict_employability(payload: Dict[str, Any]):
    try:
        result = predict_student_employability(payload)
        return result
    except Exception as e:
        log.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/skill-gap")
def diagnose_gaps(payload: Dict[str, Any], track_id: Optional[str] = Query(None)):
    try:
        return diagnose_skill_gaps(payload, track_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/roadmap")
def get_roadmap(payload: Dict[str, Any]):
    student_data = payload.get("student", {})
    missing = payload.get("missing_skills", [])
    target_role = payload.get("target_role", "Full-Stack Developer")
    target_lpa = float(payload.get("target_lpa", 12.0))
    return generate_personalized_roadmap(student_data, missing, target_role, target_lpa)

@app.post("/api/resources")
def get_resources(payload: Dict[str, Any]):
    missing = payload.get("missing_skills", [])
    return get_content_recommendations(missing)

@app.post("/api/projects")
def get_projects(payload: Dict[str, Any]):
    skills = payload.get("skills", {})
    missing = payload.get("missing_skills", [])
    return get_project_recommendations(skills, missing)

@app.post("/api/internships")
def get_internships(payload: Dict[str, Any]):
    return match_internships(payload)

# ----------------- Daily Monitoring Tracker -----------------

class ActivityLogRequest(BaseModel):
    student_id: str
    activity_type: str
    details: str
    duration_minutes: int = 60

@app.post("/api/tracker/log")
def log_activity(req: ActivityLogRequest):
    return log_student_activity(req.student_id, req.activity_type, req.details, req.duration_minutes)

@app.get("/api/tracker/{student_id}")
def get_tracker_metrics(student_id: str, github: str = "", leetcode: str = ""):
    return get_student_monitoring_metrics(student_id, github, leetcode)

# ----------------- TPO Institutional Analytics -----------------

@app.get("/api/tpo/overview")
def get_tpo_overview():
    csv_path = DATA_DIR / "student_placement_dataset.csv"
    if not csv_path.exists():
        df = generate_student_dataset(1500)
    else:
        import pandas as pd
        df = pd.read_csv(csv_path).head(1500)
        
    total_students = len(df)
    ready_count = int((df["readiness_status"] == "Ready").sum())
    near_ready_count = int((df["readiness_status"] == "Near-Ready").sum())
    needs_training_count = int((df["readiness_status"] == "Needs Training").sum())
    
    avg_cgpa = round(float(df["cgpa"].mean()), 2)
    avg_prob = round(float(df["placement_probability"].mean()), 1)
    
    # Branch-wise breakdown
    branches = {}
    for branch, group in df.groupby("branch"):
        b_total = len(group)
        b_ready = int((group["readiness_status"] == "Ready").sum())
        b_vulnerable = int((group["readiness_status"] == "Needs Training").sum())
        branches[branch] = {
            "total": b_total,
            "readiness_pct": round((b_ready / b_total) * 100.0, 1),
            "vulnerable_pct": round((b_vulnerable / b_total) * 100.0, 1),
            "avg_cgpa": round(float(group["cgpa"].mean()), 2),
            "avg_probability": round(float(group["placement_probability"].mean()), 1)
        }
        
    return {
        "cohort_size": total_students,
        "overall_placement_rate_predicted": avg_prob,
        "readiness_distribution": {
            "Ready": ready_count,
            "Near-Ready": near_ready_count,
            "Needs Training": needs_training_count
        },
        "readiness_percentages": {
            "Ready": round((ready_count / total_students) * 100.0, 1),
            "Near-Ready": round((near_ready_count / total_students) * 100.0, 1),
            "Needs Training": round((needs_training_count / total_students) * 100.0, 1)
        },
        "average_cgpa": avg_cgpa,
        "branch_analytics": branches
    }

@app.get("/api/tpo/vulnerable")
def get_vulnerable_cohort(max_prob: float = 60.0):
    csv_path = DATA_DIR / "student_placement_dataset.csv"
    import pandas as pd
    if csv_path.exists():
        df = pd.read_csv(csv_path)
    else:
        df = generate_student_dataset(1000)
        
    vulnerable = df[df["placement_probability"] < max_prob].sort_values("placement_probability")
    records = vulnerable.head(40).to_dict(orient="records")
    return {
        "count": len(vulnerable),
        "threshold": max_prob,
        "recommended_bootcamp_size": len(vulnerable),
        "students": records
    }

@app.get("/api/tpo/skill-heatmap")
def get_institutional_skill_heatmap():
    """Generates matrix of skill deficits across department branches."""
    csv_path = DATA_DIR / "student_placement_dataset.csv"
    import pandas as pd
    if csv_path.exists():
        df = pd.read_csv(csv_path)
    else:
        df = generate_student_dataset(1500)
        
    skills = ["skills_dsa", "skills_sql", "skills_python", "skills_web", "skills_cloud", "skills_ml"]
    display_names = ["DSA", "SQL", "Python", "Web/React", "Cloud/DevOps", "AI/ML"]
    
    heatmap = []
    for branch, group in df.groupby("branch"):
        row = {"branch": branch}
        for col, disp in zip(skills, display_names):
            # Percentage of students with deficit (skill < 6.0)
            deficit_pct = round(float((group[col] < 6.0).mean() * 100.0), 1)
            row[disp] = deficit_pct
        heatmap.append(row)
        
    return heatmap

@app.get("/api/tpo/alerts")
def get_mentor_alerts():
    """Generates actionable mentor alerts categorized by urgency."""
    return [
        {
            "id": "ALT-001",
            "type": "OUTPERFORMING",
            "priority": "HIGH",
            "student_id": "STU-2026-001",
            "student_name": "Priya Patel",
            "branch": "CSE",
            "metric": "Placement Prob: 94.8% | 14-day GitHub Streak",
            "message": "Priya is consistently outperforming department benchmarks.",
            "recommended_action": "Fast-track for Tier-1 Product interviews (Google/NVIDIA referrals) and leadership mentorship."
        },
        {
            "id": "ALT-002",
            "type": "AT_RISK",
            "priority": "CRITICAL",
            "student_id": "STU-2026-003",
            "student_name": "Amit Verma",
            "branch": "ECE",
            "metric": "Placement Prob: 38.2% | 2 Active Backlogs",
            "message": "Amit's employability score is below critical campus threshold (<40%).",
            "recommended_action": "Mandatory enrollment in 4-week Academic Clearance & Fundamentals Coding Bootcamp."
        },
        {
            "id": "ALT-003",
            "type": "CONSISTENCY_DROP",
            "priority": "MEDIUM",
            "student_id": "STU-2026-002",
            "student_name": "Rahul Sharma",
            "branch": "ISE",
            "metric": "Learning Activity down 42% over last 14 days",
            "message": "Rahul's daily problem-solving submissions have experienced a sharp drop.",
            "recommended_action": "Schedule 1-on-1 mentor check-in to clear external blockers or project roadblocks."
        },
        {
            "id": "ALT-004",
            "type": "RISING_STAR",
            "priority": "LOW",
            "student_id": "STU-2026-004",
            "student_name": "Sneha Rao",
            "branch": "CSE",
            "metric": "Completed 2 Advanced Systems Projects in 3 weeks",
            "message": "Rapid advancement in low-level distributed systems design.",
            "recommended_action": "Encourage submission to open-source foundation fellowships and GSoC 2026."
        }
    ]

# ----------------- Job Intelligence Endpoints -----------------

def _build_student_from_dict(p: Dict[str, Any]) -> StudentProfile:
    skills = {k: float(v) for k, v in p.get("skills", {}).items()}
    return StudentProfile(
        student_id=p.get("student_id", "STU-001"),
        branch=p.get("branch"),
        cgpa=float(p.get("cgpa", 7.0)),
        tenth_pct=float(p.get("tenth_percentage", 75.0)),
        twelfth_pct=float(p.get("twelfth_percentage", 75.0)),
        backlogs=int(p.get("active_backlogs", p.get("backlogs_history", 0))),
        semester=int(p.get("semester", 7)),
        target_role=p.get("target_role"),
        target_lpa=float(p.get("target_lpa", 12.0)),
        skills=skills,
        certifications=p.get("certifications", []),
        projects=p.get("projects", []),
        internships=p.get("internships", []),
        soft_skills=p.get("soft_skills", {}),
        aptitude=p.get("aptitude", {}),
        placement_probability=float(p.get("placement_probability", 70.0))
    )

@app.post("/api/jobs/match")
def match_student_jobs(payload: Dict[str, Any]):
    ensure_demo_fallback()
    student = _build_student_from_dict(payload)
    jobs = list_active_jobs()
    pairs = rank(jobs, student, limit=30)
    
    out = []
    for j, m in pairs:
        m_enriched = enrich_match_with_roadmap(m, student.target_role or "Full-Stack Developer")
        out.append({
            **m_enriched.model_dump(),
            "company": j.company,
            "title": j.title,
            "official_url": j.official_url,
            "location": j.location,
            "employment_type": j.employment_type,
            "work_mode": j.work_mode,
            "description": j.description,
            "required_skills": j.required_skills,
            "preferred_skills": j.preferred_skills
        })
        
    return {
        "student_id": student.student_id,
        "total_jobs_evaluated": len(jobs),
        "matched_count": len(out),
        "summary": summary_counts(pairs),
        "insights": aggregate_gaps(pairs),
        "items": out
    }

@app.get("/api/jobs/{job_id}")
def get_job_detail(job_id: str):
    j = get_job(job_id)
    if not j:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return j.model_dump()

@app.get("/api/companies")
def get_companies():
    return get_company_statuses()

@app.get("/api/tpo/industry-demand")
def get_industry_demand():
    ensure_demo_fallback()
    jobs = list_active_jobs()
    counts: Dict[str, int] = {}
    for j in jobs:
        for s in j.required_skills:
            counts[s] = counts.get(s, 0) + 1
            
    sorted_demand = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return [
        {"skill": s, "demand_count": c, "share_pct": round((c / max(len(jobs), 1)) * 100.0, 1)}
        for s, c in sorted_demand[:12]
    ]

@app.post("/api/jobs/refresh")
def trigger_refresh(background_tasks: BackgroundTasks):
    background_tasks.add_task(refresh_company_jobs)
    return {"status": "scheduled", "message": "Background sync across all official company sources initiated"}

@app.get("/api/jobs/refresh/status")
def get_refresh_status():
    return refresh_status()
