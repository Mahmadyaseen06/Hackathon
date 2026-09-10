"""
AI Placement Predictor v3 — FastAPI Backend
Full rebuild with:
- Real login (USN/Employee ID based auth)
- Company-specific AI voice interview engine
- Static file serving for HTML dashboards
- All existing ML + upskilling endpoints preserved
"""

import os
import json
import logging
import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

# Load .env manually (no python-dotenv dependency required)
def _load_dotenv():
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())
_load_dotenv()

# Local modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import (
    login_student, login_tpo, create_session_token, verify_session_token,
    get_student_by_usn, get_all_students, save_interview_result,
    register_student, usn_exists, save_platform_stats, update_student_skills_from_platforms
)
from interview.question_bank import get_calibrated_questions, COMPANY_PROFILES
from interview.analyzer import analyze_answer, generate_followup, generate_full_interview_report

# ML imports (preserved from v2)
from ml.pipeline import extract_features_from_student as extract_features
from ml.explainer import translate_shap_to_factors as _translate_shap
from ml.model_trainer import load_or_train_model, predict_student_employability
from upskilling.skill_gap_engine import diagnose_skill_gaps as compute_skill_gap
from upskilling.roadmap_generator import generate_personalized_roadmap as generate_roadmap
from upskilling.content_recommender import get_content_recommendations as recommend_resources
from upskilling.project_ladder import get_project_recommendations as get_project_ladder
from upskilling.internship_matcher import match_internships
from api.cv_parser import parse_cv
from api.progress_tracker import fetch_all_platform_stats
from api.code_executor import execute_code, analyze_code_with_ollama

DATA_DIR = Path(__file__).parent.parent / "data"
STATIC_DIR = Path(__file__).parent.parent / "static"

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
log = logging.getLogger("api.main")

app = FastAPI(
    title="AI Placement Predictor v3",
    description="Institutional Employability Intelligence with Real Auth & AI Voice Interviewer",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (HTML dashboards)
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Pre-load ML model
from ml.model_trainer import load_or_train_model
_model = None

@app.on_event("startup")
def startup_event():
    global _model
    log.info("Initializing AI Placement Predictor v3...")
    try:
        _model = load_or_train_model()
        log.info("ML ensemble loaded successfully.")
    except Exception as e:
        log.warning(f"Model load deferred: {e}")


# ─────────────────────────────────────────────
# SCHEMAS
# ─────────────────────────────────────────────

class LoginRequest(BaseModel):
    credential: str   # USN or Employee ID
    password: str

class InterviewStartRequest(BaseModel):
    usn: str
    company: str
    token: str

class AnswerSubmitRequest(BaseModel):
    usn: str
    company: str
    session_id: str
    question_index: int
    question: str
    topic: str
    claimed_level: int
    spoken_answer: str
    token: str

class InterviewCompleteRequest(BaseModel):
    usn: str
    company: str
    qa_pairs: list[dict]
    token: str

class PredictRequest(BaseModel):
    usn: Optional[str] = None
    token: Optional[str] = None
    # Inline profile fields (for direct API calls)
    name: Optional[str] = None
    branch: Optional[str] = None
    semester: Optional[int] = None
    cgpa: Optional[float] = None
    backlogs_history: Optional[int] = 0
    active_backlogs: Optional[int] = 0
    quantitative_aptitude: Optional[int] = 70
    logical_reasoning: Optional[int] = 70
    coding_benchmark: Optional[int] = 70
    communication_rating: Optional[float] = 7.0
    interview_rating: Optional[float] = 7.0
    target_role: Optional[str] = None
    target_lpa: Optional[float] = 10.0
    skills: Optional[dict] = {}
    certifications: Optional[list] = []
    internships: Optional[list] = []
    projects: Optional[list] = []


# ─────────────────────────────────────────────
# AUTH ENDPOINTS
# ─────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "service": "AI Placement Predictor v3",
        "version": "3.0.0",
        "status": "online",
        "dashboards": {
            "student": "/student",
            "tpo": "/tpo",
            "login": "/login"
        },
        "api_docs": "/docs"
    }

@app.get("/login")
def serve_login():
    login_file = STATIC_DIR / "login.html"
    if login_file.exists():
        return FileResponse(str(login_file))
    return {"error": "Login page not found. Run setup."}

@app.get("/student")
def serve_student_dashboard():
    student_file = STATIC_DIR / "student" / "index.html"
    if student_file.exists():
        return FileResponse(str(student_file))
    return {"error": "Student dashboard not found."}

@app.get("/tpo")
def serve_tpo_dashboard():
    tpo_file = STATIC_DIR / "tpo" / "index.html"
    if tpo_file.exists():
        return FileResponse(str(tpo_file))
    return {"error": "TPO dashboard not found."}

@app.post("/api/auth/login")
def auth_login(req: LoginRequest):
    """
    Universal login endpoint.
    - USN format (starts with digit or '4JN') → student login
    - TPO/FAC format → TPO login
    """
    credential = req.credential.strip().upper()
    password = req.password.strip()

    # Detect role from credential format
    is_student = credential[0].isdigit() or credential.startswith("4JN")

    if is_student:
        student = login_student(credential, password)
        if not student:
            raise HTTPException(status_code=401, detail="Invalid USN or password")
        token = create_session_token(credential, "student")
        return {
            "success": True,
            "role": "student",
            "token": token,
            "user": {
                "usn": student["usn"],
                "name": student["name"],
                "branch": student["branch"],
                "cgpa": student["cgpa"]
            },
            "redirect": "/student"
        }
    else:
        tpo_user = login_tpo(credential, password)
        if not tpo_user:
            raise HTTPException(status_code=401, detail="Invalid Employee ID or password")
        token = create_session_token(credential, "tpo")
        return {
            "success": True,
            "role": "tpo",
            "token": token,
            "user": {
                "employee_id": tpo_user["employee_id"],
                "name": tpo_user["name"],
                "role": tpo_user["role"]
            },
            "redirect": "/tpo"
        }

@app.get("/api/auth/verify")
def verify_token(token: str):
    """Verify a session token."""
    session = verify_session_token(token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"valid": True, "session": session}


# ─────────────────────────────────────────────
# STUDENT DATA ENDPOINTS
# ─────────────────────────────────────────────

@app.get("/api/student/profile")
def get_student_profile(usn: str, token: str):
    session = verify_session_token(token)
    if not session:
        raise HTTPException(status_code=401, detail="Authentication required")
    if session["role"] == "student" and session["user_id"].upper() != usn.upper():
        raise HTTPException(status_code=403, detail="Access denied")
    student = get_student_by_usn(usn)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.get("/api/students/all")
def get_all_students_tpo(token: str):
    """TPO only: get all students."""
    session = verify_session_token(token)
    if not session or session["role"] != "tpo":
        raise HTTPException(status_code=403, detail="TPO access required")
    return get_all_students()


# ─────────────────────────────────────────────
# ML PREDICTION ENDPOINTS
# ─────────────────────────────────────────────


@app.post("/api/predict")
def predict_employability(req: PredictRequest):
    """Predict employability score + SHAP XAI. Works with USN or inline profile."""
    if req.usn and req.token:
        session = verify_session_token(req.token)
        if not session:
            raise HTTPException(status_code=401, detail="Authentication required")
        student = get_student_by_usn(req.usn)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        profile = student
    else:
        profile = req.dict(exclude_none=True)

    try:
        result = predict_student_employability(profile)
        score = result.get("placement_probability", 50.0)
        tier = result.get("readiness_tier", "Near-Ready")

        # Blend interview score if available (20% weight)
        if req.usn:
            s = get_student_by_usn(req.usn)
            history = s.get("interview_history", []) if s else []
            if history:
                interview_score = history[-1].get("overall_score", 0)
                score = round(score * 0.8 + interview_score * 0.2, 1)
                tier = "Ready" if score >= 78 else "Near-Ready" if score >= 55 else "Needs Training"

        factors = result.get("shap_factors", result.get("factors", []))
        return {
            "employability_score": score,
            "readiness_status": tier,
            "probability": score / 100.0,
            "shap_factors": factors,
            "top_track": result.get("top_track", result.get("best_track", "SDE")),
            "track_scores": result.get("track_scores", {})
        }
    except Exception as e:
        log.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/skill-gap")
def skill_gap(req: PredictRequest):
    if req.usn and req.token:
        session = verify_session_token(req.token)
        if not session:
            raise HTTPException(status_code=401, detail="Auth required")
        profile = get_student_by_usn(req.usn) or req.dict(exclude_none=True)
    else:
        profile = req.dict(exclude_none=True)
    return compute_skill_gap(profile)

@app.post("/api/roadmap")
def roadmap(req: PredictRequest):
    if req.usn and req.token:
        session = verify_session_token(req.token)
        if not session:
            raise HTTPException(status_code=401, detail="Auth required")
        profile = get_student_by_usn(req.usn) or req.dict(exclude_none=True)
    else:
        profile = req.dict(exclude_none=True)
    gap = compute_skill_gap(profile)
    missing = [g["skill"] for g in gap.get("critical_gaps", [])] + [g["skill"] for g in gap.get("minor_gaps", [])]
    return generate_roadmap(profile, missing, target_role=profile.get("target_role", "SDE"), target_lpa=float(profile.get("target_lpa", 12.0)))

@app.post("/api/resources")
def resources(req: PredictRequest):
    if req.usn and req.token:
        session = verify_session_token(req.token)
        if not session:
            raise HTTPException(status_code=401, detail="Auth required")
        profile = get_student_by_usn(req.usn) or req.dict(exclude_none=True)
    else:
        profile = req.dict(exclude_none=True)
    gap = compute_skill_gap(profile)
    missing = [g["skill"] for g in gap.get("critical_gaps", [])]
    return recommend_resources(missing[:5])

@app.post("/api/projects")
def projects(req: PredictRequest):
    if req.usn and req.token:
        session = verify_session_token(req.token)
        if not session:
            raise HTTPException(status_code=401, detail="Auth required")
        profile = get_student_by_usn(req.usn) or req.dict(exclude_none=True)
    else:
        profile = req.dict(exclude_none=True)
    gap = compute_skill_gap(profile)
    skill_gaps = [g["skill"] for g in gap.get("critical_gaps", [])] + [g["skill"] for g in gap.get("minor_gaps", [])]
    return get_project_ladder(profile.get("skills", {}), skill_gaps)

@app.post("/api/internships")
def internships(req: PredictRequest):
    if req.usn and req.token:
        session = verify_session_token(req.token)
        if not session:
            raise HTTPException(status_code=401, detail="Auth required")
        profile = get_student_by_usn(req.usn) or req.dict(exclude_none=True)
    else:
        profile = req.dict(exclude_none=True)
    return match_internships(profile)


# ─────────────────────────────────────────────
# INTERVIEW ENDPOINTS
# ─────────────────────────────────────────────

@app.get("/api/interview/companies")
def get_companies():
    """Get list of available company interview simulations."""
    return [
        {"id": k, "name": v["name"], "style": v["style"], "focus": v["focus"]}
        for k, v in COMPANY_PROFILES.items()
    ]

@app.post("/api/interview/start")
def start_interview(req: InterviewStartRequest):
    """Start an interview session — returns calibrated questions for this student + company."""
    session = verify_session_token(req.token)
    if not session:
        raise HTTPException(status_code=401, detail="Authentication required")

    student = get_student_by_usn(req.usn)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    company_profile = COMPANY_PROFILES.get(req.company)
    if not company_profile:
        raise HTTPException(status_code=400, detail=f"Unknown company: {req.company}")

    questions = get_calibrated_questions(req.company, student.get("skills", {}), num_questions=7)

    import uuid
    session_id = str(uuid.uuid4())[:8]

    return {
        "session_id": session_id,
        "company": req.company,
        "company_name": company_profile["name"],
        "interviewer_persona": company_profile["interviewer_persona"],
        "total_questions": len(questions),
        "questions": questions,
        "student_name": student["name"]
    }

@app.post("/api/interview/analyze-answer")
async def analyze_single_answer(req: AnswerSubmitRequest):
    """Analyze one interview answer using Gemini Flash AI."""
    session = verify_session_token(req.token)
    if not session:
        raise HTTPException(status_code=401, detail="Authentication required")

    if not req.spoken_answer or len(req.spoken_answer.strip()) < 3:
        return {
            "score": 0,
            "verdict": "Insufficient Answer",
            "technical_accuracy": 0,
            "communication_clarity": 0,
            "what_was_missing": "No answer was provided.",
            "red_flags": True
        }

    result = await analyze_answer(
        question=req.question,
        spoken_answer=req.spoken_answer,
        topic=req.topic,
        claimed_skill_level=req.claimed_level,
        company=req.company,
        question_type="technical"
    )
    return result

@app.post("/api/interview/followup")
async def get_followup_question(req: AnswerSubmitRequest):
    """Get a natural AI-generated follow-up question."""
    session = verify_session_token(req.token)
    if not session:
        raise HTTPException(status_code=401, detail="Authentication required")

    followup = await generate_followup(
        question=req.question,
        spoken_answer=req.spoken_answer,
        topic=req.topic,
        company=req.company
    )
    return {"followup_question": followup}

@app.post("/api/interview/complete")
async def complete_interview(req: InterviewCompleteRequest):
    """Generate full interview report and save to student record."""
    session = verify_session_token(req.token)
    if not session:
        raise HTTPException(status_code=401, detail="Authentication required")

    student = get_student_by_usn(req.usn)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    report = await generate_full_interview_report(
        student_name=student["name"],
        company=req.company,
        qa_pairs=req.qa_pairs,
        student_skills=student.get("skills", {})
    )

    # Save to student record
    report["timestamp"] = datetime.datetime.now().isoformat()
    report["usn"] = req.usn
    save_interview_result(req.usn, report)

    return report

@app.get("/api/interview/history")
def get_interview_history(usn: str, token: str):
    """Get all past interview sessions for a student."""
    session = verify_session_token(token)
    if not session:
        raise HTTPException(status_code=401, detail="Authentication required")
    student = get_student_by_usn(usn)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {
        "usn": usn,
        "name": student["name"],
        "interview_history": student.get("interview_history", [])
    }


# ─────────────────────────────────────────────
# TPO COMMAND CENTER ENDPOINTS
# ─────────────────────────────────────────────

@app.get("/api/tpo/overview")
def tpo_overview(token: str):
    session = verify_session_token(token)
    if not session or session["role"] != "tpo":
        raise HTTPException(status_code=403, detail="TPO access required")

    students = get_all_students()
    total = len(students)

    # Calculate scores for each student using predict_student_employability
    scores = []
    for s in students:
        try:
            res = predict_student_employability(s)
            scores.append(res.get("placement_probability", 50.0))
        except:
            scores.append(50.0)

    ready = sum(1 for sc in scores if sc >= 78)
    near_ready = sum(1 for sc in scores if 55 <= sc < 78)
    needs_training = sum(1 for sc in scores if sc < 55)
    avg_score = round(sum(scores) / total, 1) if scores else 0.0

    return {
        "cohort_size": total,
        "average_employability": avg_score,
        "ready_count": ready,
        "near_ready_count": near_ready,
        "needs_training_count": needs_training,
        "readiness_distribution": {
            "Ready": round(ready / total * 100, 1),
            "Near-Ready": round(near_ready / total * 100, 1),
            "Needs Training": round(needs_training / total * 100, 1)
        },
        "total_interviews_taken": sum(len(s.get("interview_history", [])) for s in students),
        "students_with_internships": sum(1 for s in students if len(s.get("internships", [])) > 0)
    }

@app.get("/api/tpo/students-with-scores")
def students_with_scores(token: str):
    """All students with their computed employability scores."""
    session = verify_session_token(token)
    if not session or session["role"] != "tpo":
        raise HTTPException(status_code=403, detail="TPO access required")

    students = get_all_students()

    result = []
    for s in students:
        try:
            res = predict_student_employability(s)
            score = round(res.get("placement_probability", 50.0), 1)
            tier = "Ready" if score >= 78 else "Near-Ready" if score >= 55 else "Needs Training"
        except:
            score = 50.0
            tier = "Near-Ready"

        history = s.get("interview_history", [])
        latest_interview = history[-1] if history else None

        result.append({
            "usn": s["usn"],
            "name": s["name"],
            "branch": s["branch"],
            "cgpa": s["cgpa"],
            "employability_score": score,
            "readiness_tier": tier,
            "active_backlogs": s.get("active_backlogs", 0),
            "internships_count": len(s.get("internships", [])),
            "certifications_count": len(s.get("certifications", [])),
            "interview_attempts": len(history),
            "latest_interview": {
                "company": latest_interview["company"],
                "overall_score": latest_interview.get("overall_score", 0),
                "verdict": latest_interview.get("verdict", ""),
                "timestamp": latest_interview.get("timestamp", "")
            } if latest_interview else None
        })

    result.sort(key=lambda x: x["employability_score"], reverse=True)
    return result

@app.get("/api/tpo/vulnerable")
def vulnerable_students(token: str, threshold: float = 60.0):
    """Students below threshold score — for early intervention."""
    session = verify_session_token(token)
    if not session or session["role"] != "tpo":
        raise HTTPException(status_code=403, detail="TPO access required")

    all_scored = students_with_scores(token)
    return [s for s in all_scored if s["employability_score"] < threshold]

@app.get("/api/tpo/skill-heatmap")
def skill_heatmap(token: str):
    """Institutional skill deficit heatmap."""
    session = verify_session_token(token)
    if not session or session["role"] != "tpo":
        raise HTTPException(status_code=403, detail="TPO access required")

    students = get_all_students()
    skill_counts = {}
    total = len(students)

    for s in students:
        for skill, level in s.get("skills", {}).items():
            if skill not in skill_counts:
                skill_counts[skill] = {"total": 0, "below_threshold": 0}
            skill_counts[skill]["total"] += 1
            if level < 6:
                skill_counts[skill]["below_threshold"] += 1

    heatmap = []
    for skill, data in skill_counts.items():
        deficit_pct = round(data["below_threshold"] / total * 100, 1)
        heatmap.append({
            "skill": skill,
            "students_with_skill": data["total"],
            "students_lacking_proficiency": data["below_threshold"],
            "deficit_percentage": deficit_pct,
            "severity": "Critical" if deficit_pct > 60 else "High" if deficit_pct > 40 else "Medium" if deficit_pct > 20 else "Low"
        })

    heatmap.sort(key=lambda x: x["deficit_percentage"], reverse=True)
    return heatmap

@app.get("/api/tpo/alerts")
def tpo_alerts(token: str):
    """Generate mentor alerts for at-risk and outperforming students."""
    session = verify_session_token(token)
    if not session or session["role"] != "tpo":
        raise HTTPException(status_code=403, detail="TPO access required")

    all_scored = students_with_scores(token)
    alerts = []

    for s in all_scored:
        score = s["employability_score"]
        backlogs = s["active_backlogs"]
        history = s["interview_attempts"]

        if score >= 88 and history > 0:
            alerts.append({"type": "OUTPERFORMING", "usn": s["usn"], "name": s["name"], "score": score,
                           "message": f"{s['name']} scored {score}% with strong interview performance. Fast-track for referrals.", "color": "green"})
        elif score < 50 or backlogs >= 2:
            alerts.append({"type": "AT_RISK", "usn": s["usn"], "name": s["name"], "score": score,
                           "message": f"{s['name']} is at risk — score {score}%, {backlogs} active backlogs. Immediate mentoring required.", "color": "red"})
        elif score < 65 and history == 0:
            alerts.append({"type": "NEEDS_INTERVIEW_PRACTICE", "usn": s["usn"], "name": s["name"], "score": score,
                           "message": f"{s['name']} hasn't taken any mock interviews yet and scores {score}%.", "color": "orange"})

    return alerts

@app.get("/api/tpo/branch-breakdown")
def branch_breakdown(token: str):
    session = verify_session_token(token)
    if not session or session["role"] != "tpo":
        raise HTTPException(status_code=403, detail="TPO access required")

    all_scored = students_with_scores(token)
    branches = {}
    for s in all_scored:
        b = s["branch"]
        if b not in branches:
            branches[b] = {"students": 0, "total_score": 0, "ready": 0}
        branches[b]["students"] += 1
        branches[b]["total_score"] += s["employability_score"]
        if s["readiness_tier"] == "Ready":
            branches[b]["ready"] += 1

    return [
        {
            "branch": b,
            "student_count": data["students"],
            "avg_score": round(data["total_score"] / data["students"], 1),
            "ready_count": data["ready"],
            "placement_rate": round(data["ready"] / data["students"] * 100, 1)
        }
        for b, data in branches.items()
    ]

@app.get("/api/tpo/interview-summary")
def interview_summary(token: str):
    """Summary of all mock interviews taken across the batch."""
    session = verify_session_token(token)
    if not session or session["role"] != "tpo":
        raise HTTPException(status_code=403, detail="TPO access required")

    students = get_all_students()
    all_interviews = []
    for s in students:
        for interview in s.get("interview_history", []):
            all_interviews.append({
                "usn": s["usn"],
                "name": s["name"],
                "branch": s["branch"],
                "company": interview.get("company", ""),
                "overall_score": interview.get("overall_score", 0),
                "verdict": interview.get("verdict", ""),
                "readiness_tier": interview.get("readiness_tier", ""),
                "timestamp": interview.get("timestamp", "")
            })
    all_interviews.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return all_interviews


# ─────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "service": "AI Placement Predictor v3",
        "version": "3.0.0",
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY", "") and os.getenv("GEMINI_API_KEY") != "your_gemini_api_key_here"),
        "ollama_url": "http://localhost:11434",
        "students_loaded": len(get_all_students())
    }


# ─────────────────────────────────────────────
# SIGNUP & CV UPLOAD ENDPOINTS
# ─────────────────────────────────────────────

@app.get("/signup")
def serve_signup():
    signup_file = STATIC_DIR / "signup.html"
    if signup_file.exists():
        return FileResponse(str(signup_file))
    return {"error": "Signup page not found."}


class SignupRequest(BaseModel):
    # Personal info
    name: str
    email: Optional[str] = ""
    phone: Optional[str] = ""
    password: str
    # Academic
    usn: Optional[str] = ""
    branch: str = "Computer Science & Engineering"
    semester: int = 7
    cgpa: float = 7.0
    active_backlogs: int = 0
    backlogs_history: int = 0
    # Scores
    quantitative_aptitude: int = 70
    logical_reasoning: int = 70
    coding_benchmark: int = 70
    communication_rating: float = 7.0
    # Target
    target_role: str = "SDE"
    target_lpa: float = 10.0
    # Skills as comma-separated string OR dict
    skills_text: Optional[str] = ""
    skills: Optional[dict] = {}
    # Certifications / projects (comma-separated)
    certifications_text: Optional[str] = ""
    # Platform usernames
    github_username: Optional[str] = ""
    leetcode_username: Optional[str] = ""
    hackerrank_username: Optional[str] = ""
    codeforces_username: Optional[str] = ""


@app.post("/api/auth/signup")
async def signup(req: SignupRequest):
    """Register a new student with manually entered details."""
    if not req.name or not req.password:
        raise HTTPException(status_code=400, detail="Name and password are required")

    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    # Check USN conflict if provided
    if req.usn and usn_exists(req.usn):
        raise HTTPException(status_code=409, detail=f"USN '{req.usn}' is already registered")

    # Parse skills from text if not provided as dict
    skills = req.skills or {}
    if not skills and req.skills_text:
        for item in req.skills_text.split(","):
            item = item.strip()
            if ":" in item:
                sk, lv = item.split(":", 1)
                try:
                    skills[sk.strip()] = int(lv.strip())
                except ValueError:
                    skills[sk.strip()] = 6
            elif item:
                skills[item] = 6  # default proficiency

    # Parse certifications
    certs = []
    if req.certifications_text:
        certs = [c.strip() for c in req.certifications_text.split(",") if c.strip()]

    profile = req.dict()
    profile["skills"] = skills
    profile["certifications"] = certs

    student = register_student(profile)
    token = create_session_token(student["usn"], "student")

    return {
        "success": True,
        "message": f"Account created! Your USN is {student['usn']}",
        "usn": student["usn"],
        "role": "student",
        "token": token,
        "user": {
            "usn": student["usn"],
            "name": student["name"],
            "branch": student["branch"],
            "cgpa": student["cgpa"]
        },
        "redirect": "/student"
    }


@app.post("/api/auth/signup-cv")
async def signup_with_cv(
    cv_file: UploadFile = File(...),
    password: str = Form(...),
    usn: str = Form(default=""),
    github_username: str = Form(default=""),
    leetcode_username: str = Form(default=""),
    hackerrank_username: str = Form(default=""),
    codeforces_username: str = Form(default="")
):
    """
    Register a new student by uploading their CV/resume PDF.
    Ollama AI extracts the profile automatically.
    """
    if not cv_file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    if usn and usn_exists(usn):
        raise HTTPException(status_code=409, detail=f"USN '{usn}' is already registered")

    # Read file content
    file_bytes = await cv_file.read()
    if len(file_bytes) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")

    # Parse CV with AI
    log.info(f"Parsing CV: {cv_file.filename} ({len(file_bytes)} bytes)")
    cv_profile = await parse_cv(file_bytes, cv_file.filename)

    if not cv_profile:
        raise HTTPException(status_code=422, detail="Could not extract information from CV. Please check the PDF or use manual signup.")

    # Override/supplement with form fields
    cv_profile["password"] = password
    if usn:
        cv_profile["usn"] = usn
    if github_username:
        cv_profile["github_username"] = github_username
    if leetcode_username:
        cv_profile["leetcode_username"] = leetcode_username
    if hackerrank_username:
        cv_profile["hackerrank_username"] = hackerrank_username
    if codeforces_username:
        cv_profile["codeforces_username"] = codeforces_username

    student = register_student(cv_profile)
    token = create_session_token(student["usn"], "student")

    return {
        "success": True,
        "message": f"CV parsed! Account created as {student['usn']}",
        "usn": student["usn"],
        "role": "student",
        "token": token,
        "extracted_profile": {
            "name": student["name"],
            "skills_found": len(student.get("skills", {})),
            "projects_found": len(student.get("projects", [])),
            "certifications_found": len(student.get("certifications", [])),
            "internships_found": len(student.get("internships", [])),
        },
        "user": {
            "usn": student["usn"],
            "name": student["name"],
            "branch": student["branch"],
            "cgpa": student["cgpa"]
        },
        "redirect": "/student"
    }


# ─────────────────────────────────────────────
# PROGRESS TRACKING ENDPOINTS
# ─────────────────────────────────────────────

@app.post("/api/progress/refresh")
async def refresh_progress(usn: str, token: str):
    """
    Fetch fresh stats from GitHub, LeetCode, Codeforces, HackerRank.
    Updates student profile and auto-adjusts skill levels.
    """
    session = verify_session_token(token)
    if not session:
        raise HTTPException(status_code=401, detail="Authentication required")
    if session["role"] == "student" and session["user_id"].upper() != usn.upper():
        raise HTTPException(status_code=403, detail="Access denied")

    student = get_student_by_usn(usn)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Fetch all platform stats in parallel
    log.info(f"Fetching platform stats for {usn}")
    stats = await fetch_all_platform_stats(student)

    # Save to student record
    save_platform_stats(usn, stats)

    # Auto-update skill levels based on real activity
    update_student_skills_from_platforms(usn, stats)

    return {
        "success": True,
        "usn": usn,
        "platforms_fetched": [k for k in stats if k not in ("fetched_at", "aggregate_activity_score", "message")],
        "aggregate_activity_score": stats.get("aggregate_activity_score", 0),
        "stats": stats
    }


@app.get("/api/progress/stats")
def get_progress_stats(usn: str, token: str):
    """Get the most recently fetched platform stats for a student."""
    session = verify_session_token(token)
    if not session:
        raise HTTPException(status_code=401, detail="Authentication required")
    if session["role"] == "student" and session["user_id"].upper() != usn.upper():
        raise HTTPException(status_code=403, detail="Access denied")

    student = get_student_by_usn(usn)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return {
        "usn": usn,
        "platform_stats": student.get("platform_stats", {}),
        "has_github": bool(student.get("github_username")),
        "has_leetcode": bool(student.get("leetcode_username")),
        "has_hackerrank": bool(student.get("hackerrank_username")),
        "has_codeforces": bool(student.get("codeforces_username")),
        "github_username": student.get("github_username", ""),
        "leetcode_username": student.get("leetcode_username", ""),
        "hackerrank_username": student.get("hackerrank_username", ""),
        "codeforces_username": student.get("codeforces_username", ""),
    }


@app.get("/api/progress/history")
def get_progress_history(usn: str, token: str):
    """Get platform stats history (daily snapshots) for trend graphs."""
    session = verify_session_token(token)
    if not session:
        raise HTTPException(status_code=401, detail="Authentication required")

    student = get_student_by_usn(usn)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    history = student.get("platform_stats_history", [])
    return {
        "usn": usn,
        "snapshots": len(history),
        "history": history[-30:]  # Last 30 days
    }


@app.get("/api/progress/recommendations")
async def get_progress_recommendations(usn: str, token: str):
    """
    Generate resource recommendations based on platform activity + skill gaps.
    """
    session = verify_session_token(token)
    if not session:
        raise HTTPException(status_code=401, detail="Authentication required")

    student = get_student_by_usn(usn)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Get skill gaps
    gap_data = compute_skill_gap(student)
    missing = (
        [g["skill"] for g in gap_data.get("critical_gaps", [])] +
        [g["skill"] for g in gap_data.get("minor_gaps", [])]
    )

    # Get resources for top 5 gaps
    resources = recommend_resources(missing[:5])

    # Get platform stats
    platform_stats = student.get("platform_stats", {})

    # Build activity-aware recommendations
    suggestions = []

    lc = platform_stats.get("leetcode", {})
    if not lc.get("error") and lc.get("total_solved", 0) < 50:
        suggestions.append({
            "type": "action",
            "platform": "LeetCode",
            "message": f"You've solved {lc.get('total_solved', 0)} problems. Aim for 100+ to be competitive.",
            "link": f"https://leetcode.com/{student.get('leetcode_username', '')}"
        })

    gh = platform_stats.get("github", {})
    if not gh.get("error") and gh.get("recent_commits_30d", 0) < 10:
        suggestions.append({
            "type": "action",
            "platform": "GitHub",
            "message": f"Only {gh.get('recent_commits_30d', 0)} commits in 30 days. Try to commit daily!",
            "link": f"https://github.com/{student.get('github_username', '')}"
        })

    cf = platform_stats.get("codeforces", {})
    if not cf.get("error") and cf.get("rating", 0) < 1200:
        suggestions.append({
            "type": "action",
            "platform": "Codeforces",
            "message": f"Codeforces rating: {cf.get('rating', 0)}. Practice div.3 contests to reach 1200+.",
            "link": f"https://codeforces.com/profile/{student.get('codeforces_username', '')}"
        })

    return {
        "skill_gap_resources": resources,
        "activity_suggestions": suggestions,
        "skill_gaps": missing[:8]
    }

