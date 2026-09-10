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

from fastapi import FastAPI, Request, HTTPException, Depends
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
    get_student_by_usn, get_all_students, save_interview_result
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
        "students_loaded": len(get_all_students())
    }
