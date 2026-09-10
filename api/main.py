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
    register_student, usn_exists, save_platform_stats, update_student_skills_from_platforms,
    update_student_profile, batch_upsert_students
)
from interview.question_bank import get_calibrated_questions, get_company_interview_rounds, COMPANY_PROFILES
from interview.analyzer import analyze_answer, generate_followup, generate_full_interview_report, generate_interviewer_speech

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

from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
log = logging.getLogger("api.main")

def decode_csv_bytes(contents: bytes) -> str:
    """Robust decoding supporting Windows Excel BOM (utf-8-sig), standard utf-8, and latin-1."""
    try:
        return contents.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            return contents.decode("utf-8", errors="replace")
        except Exception:
            return contents.decode("latin-1", errors="ignore")

# Pre-load ML model
from ml.model_trainer import load_or_train_model
_model = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _model
    log.info("Initializing AI Placement Predictor v3...")
    try:
        _model = load_or_train_model()
        log.info("ML stacked ensemble loaded successfully.")
    except Exception as e:
        log.warning(f"Model load deferred: {e}")
    yield
    log.info("Shutting down AI Placement Predictor...")

app = FastAPI(
    title="AI Placement Predictor v3",
    description="Institutional Employability Intelligence with Real Auth & AI Voice Interviewer",
    version="3.0.0",
    lifespan=lifespan
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
    track: Optional[str] = "technical"

class AnswerSubmitRequest(BaseModel):
    usn: Optional[str] = ""
    company: Optional[str] = ""
    session_id: Optional[str] = ""
    question_index: Optional[int] = 0
    question: str
    topic: Optional[str] = "General"
    claimed_level: Optional[int] = 5
    claimed_skill_level: Optional[int] = None
    spoken_answer: Optional[str] = ""
    token: Optional[str] = ""
    code: Optional[str] = None
    language: Optional[str] = None
    execution_result: Optional[dict] = None
    question_type: Optional[str] = "technical"

class CodeExecuteRequest(BaseModel):
    code: str
    language: str = "python"
    stdin: Optional[str] = ""
    test_cases: Optional[list] = None
    question_id: Optional[int] = None

class TalkBackRequest(BaseModel):
    question: str
    spoken_answer: Optional[str] = ""
    topic: Optional[str] = "General"
    company: str
    code: Optional[str] = None
    execution_result: Optional[dict] = None

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

@app.get("/interview")
def serve_interview():
    interview_file = STATIC_DIR / "interview" / "index.html"
    if interview_file.exists():
        return FileResponse(str(interview_file))
    return {"error": "Interview page not found."}

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

class StudentProfileUpdateRequest(BaseModel):
    usn: str
    token: str
    updates: dict

@app.post("/api/student/profile")
def update_profile(req: StudentProfileUpdateRequest):
    """Update student profile (academic track, skills, projects, certifications, internships)."""
    session = verify_session_token(req.token)
    if not session:
        raise HTTPException(status_code=401, detail="Authentication required")
    if session["role"] == "student" and session["user_id"].upper() != req.usn.upper():
        raise HTTPException(status_code=403, detail="Access denied")

    updated = update_student_profile(req.usn, req.updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"success": True, "student": updated}

@app.post("/api/student/upload-csv")
async def student_upload_csv(usn: str = Form(...), token: str = Form(...), file: UploadFile = File(...)):
    """Allow student to ingest or sync their profile from a CSV file."""
    session = verify_session_token(token)
    if not session:
        raise HTTPException(status_code=401, detail="Authentication required")
    if session["role"] == "student" and session["user_id"].upper() != usn.upper():
        raise HTTPException(status_code=403, detail="Access denied")

    contents = await file.read()
    import csv, io, json
    decoded = decode_csv_bytes(contents)
    reader = csv.DictReader(io.StringIO(decoded))
    updates = {}
    for row in reader:
        for k, v in row.items():
            if not v: continue
            k_lower = k.lower().strip()
            if k_lower in ["cgpa", "tenth_percentage", "twelfth_percentage", "quantitative_aptitude", "coding_benchmark", "communication_rating"]:
                try: updates[k_lower] = float(v)
                except: pass
            elif k_lower in ["semester", "active_backlogs", "backlogs_history"]:
                try: updates[k_lower] = int(v)
                except: pass
            elif k_lower == "skills":
                try:
                    updates["skills"] = json.loads(v)
                except:
                    parsed_skills = {}
                    for p in v.split(","):
                        if ":" in p:
                            sk, lvl = p.split(":", 1)
                            try: parsed_skills[sk.strip()] = float(lvl.strip())
                            except: parsed_skills[sk.strip()] = 5.0
                    if parsed_skills:
                        updates["skills"] = parsed_skills
            elif k_lower in ["projects", "certifications", "internships"]:
                updates[k_lower] = [x.strip() for x in v.split(";") if x.strip()]

    if updates:
        update_student_profile(usn, updates)
    return {"success": True, "updated_fields": list(updates.keys())}

class DeveloperSyncRequest(BaseModel):
    usn: str
    token: str
    github_handle: Optional[str] = None
    leetcode_handle: Optional[str] = None

@app.post("/api/student/developer-sync")
def student_developer_sync(req: DeveloperSyncRequest):
    """Sync live external activity from GitHub and LeetCode and compute 30-day consistency score."""
    session = verify_session_token(req.token)
    if not session:
        raise HTTPException(status_code=401, detail="Authentication required")
    if session["role"] == "student" and session["user_id"].upper() != req.usn.upper():
        raise HTTPException(status_code=403, detail="Access denied")

    student = get_student_by_usn(req.usn)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    from upskilling.developer_sync import sync_student_developer_profiles
    payload = sync_student_developer_profiles(
        student_id=student.get("student_id", req.usn),
        github_handle=req.github_handle,
        leetcode_handle=req.leetcode_handle
    )
    return {"success": True, "developer_activity": payload}

def _student_to_job_profile(student: dict):
    from job_intelligence.models import StudentProfile
    skills = {}
    for k, v in student.get("skills", {}).items():
        try:
            skills[k] = float(v)
        except (ValueError, TypeError):
            skills[k] = 5.0

    certifications = []
    for c in student.get("certifications", []):
        if isinstance(c, str):
            certifications.append(c)
        elif isinstance(c, dict):
            certifications.append(c.get("name", ""))

    projects = []
    for p in student.get("projects", []):
        if isinstance(p, dict):
            projects.append(p)
        elif isinstance(p, str):
            projects.append({"name": p, "tags": []})

    internships = []
    for i in student.get("internships", []):
        if isinstance(i, dict):
            internships.append(i)
        elif isinstance(i, str):
            internships.append({"company": i, "role": "Intern"})

    return StudentProfile(
        student_id=student.get("student_id", student.get("usn", "STU")),
        branch=student.get("branch"),
        cgpa=float(student.get("cgpa", 7.0)),
        tenth_pct=float(student.get("tenth_percentage", 75.0)),
        twelfth_pct=float(student.get("twelfth_percentage", 75.0)),
        backlogs=int(student.get("active_backlogs", student.get("backlogs", 0))),
        semester=int(student.get("semester", 6)),
        target_role=student.get("primary_track", student.get("target_role", "Software Engineer")),
        skills=skills,
        certifications=certifications,
        projects=projects,
        internships=internships,
        aptitude=student.get("aptitude", {}),
        soft_skills=student.get("soft_skills", {})
    )

@app.get("/api/jobs/matched")
def get_matched_jobs_for_student(usn: str, token: str):
    """Evaluate all official job postings against student profile and return Best/Near/Stretch matches + Aggregate Gap Matrix."""
    session = verify_session_token(token)
    if not session:
        raise HTTPException(status_code=401, detail="Authentication required")
    if session["role"] == "student" and session["user_id"].upper() != usn.upper():
        raise HTTPException(status_code=403, detail="Access denied")

    student = get_student_by_usn(usn)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    from job_intelligence.demo_data import build_demo_jobs
    from job_intelligence.matcher import rank
    from job_intelligence.models import MatchCategory

    jobs = build_demo_jobs()
    profile = _student_to_job_profile(student)
    ranked = rank(jobs, profile, limit=50)

    best_matches = []
    near_matches = []
    stretch_matches = []
    skill_gap_freq = {}

    for job, res in ranked:
        job_item = {
            "job_id": job.id,
            "company": job.company,
            "title": job.title,
            "location": job.location or "India / Remote",
            "work_mode": job.work_mode or "Hybrid",
            "employment_type": job.employment_type or "Full-Time",
            "fit_score": res.job_fit_score,
            "readiness_score": res.readiness_score,
            "category": res.category.value,
            "eligibility": res.eligibility.model_dump(),
            "matched_skills": res.matched_skills,
            "missing_required_skills": res.missing_required_skills,
            "missing_preferred_skills": res.missing_preferred_skills,
            "skill_gap_priority": [g.model_dump() for g in res.skill_gap_priority],
            "why_recommended": res.why_recommended,
            "recommended_actions": res.recommended_actions,
            "application_url": job.application_url or job.official_url
        }

        # Track aggregate gap matrix across all prospective roles
        for g in res.skill_gap_priority:
            s = g.skill
            if s not in skill_gap_freq:
                skill_gap_freq[s] = {"skill": s, "frequency": 0, "priority": g.priority.value, "kind": g.kind}
            skill_gap_freq[s]["frequency"] += 1

        if res.category == MatchCategory.BEST_MATCH:
            best_matches.append(job_item)
        elif res.category == MatchCategory.NEAR_MATCH:
            near_matches.append(job_item)
        else:
            stretch_matches.append(job_item)

    aggregate_gap_matrix = sorted(skill_gap_freq.values(), key=lambda x: (-x["frequency"], x["priority"]))

    return {
        "usn": usn,
        "total_evaluated_jobs": len(jobs),
        "best_matches": best_matches,
        "near_matches": near_matches,
        "stretch_matches": stretch_matches,
        "aggregate_skill_gap_matrix": aggregate_gap_matrix[:12]
    }

@app.get("/api/jobs/list")
def list_all_jobs(token: str):
    """List all available jobs."""
    session = verify_session_token(token)
    if not session:
        raise HTTPException(status_code=401, detail="Authentication required")

    from job_intelligence.demo_data import build_demo_jobs
    jobs = build_demo_jobs()
    return [
        {
            "id": j.id,
            "company": j.company,
            "title": j.title,
            "location": j.location,
            "work_mode": j.work_mode,
            "employment_type": j.employment_type,
            "required_skills": j.required_skills,
            "preferred_skills": j.preferred_skills,
            "application_url": j.application_url or j.official_url
        }
        for j in jobs
    ]

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
        tier = result.get("readiness_status", "Needs Training")

        # Blend interview score if available (20% weight)
        if req.usn:
            s = get_student_by_usn(req.usn)
            history = s.get("interview_history", []) if s else []
            if history:
                interview_score = history[-1].get("overall_score", 0)
                score = round(score * 0.8 + interview_score * 0.2, 1)
                tier = "Ready" if score >= 78 else "Near-Ready" if score >= 62 else "Needs Training"

        factors = result.get("factor_transparency", result.get("shap_factors", []))
        tracks = result.get("career_track_alignments", [])
        top_track = result.get("primary_recommended_track", tracks[0]["track"] if tracks else "Full-Stack Developer")
        track_scores = {t["track"]: t.get("match_pct", 0) for t in tracks}

        return {
            "employability_score": score,
            "placement_probability": score,
            "readiness_status": tier,
            "readiness_badge": result.get("readiness_badge", "error" if tier == "Needs Training" else "warning"),
            "probability": score / 100.0,
            "shap_factors": factors,
            "factor_transparency": factors,
            "reality_check_penalties": result.get("reality_check_penalties", []),
            "top_track": top_track,
            "primary_recommended_track": top_track,
            "career_track_alignments": tracks,
            "track_scores": track_scores,
            "scoring_note": result.get("scoring_note", "")
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

    rounds = get_company_interview_rounds(
        req.company,
        student.get("skills", {}),
        track=req.track or "technical",
        student_projects=student.get("projects", [])
    )
    flat_questions = []
    for r in rounds:
        for q in r["questions"]:
            q_copy = q.copy()
            q_copy["round_id"] = r["round_id"]
            q_copy["round_name"] = r["name"]
            flat_questions.append(q_copy)

    import uuid
    session_id = str(uuid.uuid4())[:8]

    return {
        "success": True,
        "session_id": session_id,
        "company": req.company,
        "company_name": company_profile["name"],
        "interviewer_persona": company_profile["interviewer_persona"],
        "track": req.track or "technical",
        "total_questions": len(flat_questions),
        "questions": flat_questions,
        "rounds": rounds,
        "student_name": student["name"],
        "round": "Project Defense & HR Interview" if req.track == "project_defense" else "Multi-Round Recruitment Simulation"
    }

@app.post("/api/interview/talk-back")
async def interview_talk_back(req: TalkBackRequest):
    """Generate instant conversational spoken response from the AI interviewer."""
    reply = await generate_interviewer_speech(
        question=req.question,
        answer=req.spoken_answer or "",
        topic=req.topic or "General",
        company=req.company,
        code=req.code,
        execution_result=req.execution_result
    )
    return {"spoken_reply": reply}

@app.post("/api/code/execute")
def run_code_sandbox(req: CodeExecuteRequest):
    """Execute code in a secure subprocess sandbox."""
    res = execute_code(
        code=req.code,
        language=req.language,
        stdin=req.stdin or "",
        test_cases=req.test_cases or []
    )
    return res

@app.post("/api/interview/analyze-answer")
async def analyze_single_answer(req: AnswerSubmitRequest):
    """Analyze one interview answer (spoken and/or code) using local Ollama & strict analyzer."""
    if req.token:
        verify_session_token(req.token)

    code_eval = None
    if req.code and req.code.strip():
        try:
            code_eval = await analyze_code_with_ollama(
                code=req.code,
                question=req.question,
                language=req.language or "python",
                execution_result=req.execution_result or {},
                claimed_skill_level=req.claimed_skill_level or req.claimed_level or 5
            )
        except Exception as e:
            log.warning(f"Ollama code analysis failed: {e}")

    spoken = (req.spoken_answer or "").strip()
    is_placeholder_spoken = spoken in ["[No verbal explanation provided]", "[No answer]", "[Code only]", ""]

    try:
        spoken_reply = await generate_interviewer_speech(
            question=req.question,
            answer=spoken if not is_placeholder_spoken else "[Candidate submitted code solution]",
            topic=req.topic or "General",
            company=req.company or "Company",
            code=req.code,
            execution_result=req.execution_result
        )
    except Exception as e:
        spoken_reply = "I have noted your solution. Let us proceed to the next question."

    if is_placeholder_spoken and code_eval:
        return {
            "score": code_eval.get("code_score", 5),
            "technical_accuracy": code_eval.get("correctness", 5),
            "communication_clarity": 7,
            "verdict": code_eval.get("verdict", "Partially Verified"),
            "what_was_good": f"Approach: {code_eval.get('approach', 'Code solution submitted')}",
            "what_was_missing": code_eval.get("what_is_wrong") or "None",
            "claim_vs_reality": code_eval.get("skill_match", "Matches Claim"),
            "red_flags": code_eval.get("code_score", 5) < 4,
            "honest_feedback": code_eval.get("better_approach") or f"Complexity: {code_eval.get('time_complexity', 'O(n)')}",
            "code_analysis": code_eval,
            "interviewer_speech": spoken_reply
        }

    if not spoken or len(spoken) < 3:
        if code_eval:
            return {
                "score": code_eval.get("code_score", 5),
                "technical_accuracy": code_eval.get("correctness", 5),
                "communication_clarity": 6,
                "verdict": code_eval.get("verdict", "Partially Verified"),
                "what_was_good": code_eval.get("approach", "Code solution"),
                "what_was_missing": code_eval.get("what_is_wrong") or "No verbal explanation provided",
                "claim_vs_reality": code_eval.get("skill_match", "Matches Claim"),
                "red_flags": code_eval.get("code_score", 5) < 4,
                "honest_feedback": code_eval.get("better_approach") or "Add verbal explanation of your thought process.",
                "code_analysis": code_eval,
                "interviewer_speech": spoken_reply
            }
        return {
            "score": 0,
            "verdict": "Insufficient Answer",
            "technical_accuracy": 0,
            "communication_clarity": 0,
            "what_was_missing": "No answer was provided.",
            "red_flags": True,
            "interviewer_speech": "No response was recorded. Please attempt the question or move forward."
        }

    result = await analyze_answer(
        question=req.question,
        spoken_answer=spoken,
        topic=req.topic or "General",
        claimed_skill_level=req.claimed_skill_level or req.claimed_level or 5,
        company=req.company or "Company",
        question_type=req.question_type or "technical"
    )

    if code_eval:
        result["code_analysis"] = code_eval
        # Blend score: 60% code, 40% explanation
        blended = round(0.6 * code_eval.get("code_score", 5) + 0.4 * result.get("score", 5))
        result["score"] = blended

    result["interviewer_speech"] = spoken_reply

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
        dev_activity = s.get("developer_activity", {})
        dev_consistency = dev_activity.get("consistency", {}).get("consistency_score")

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
            "developer_consistency": dev_consistency,
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

@app.get("/api/tpo/skill-deficit-heatmap")
def skill_deficit_heatmap(token: str):
    """Aggregate skill proficiency across all students to identify batch-wide gaps."""
    session = verify_session_token(token)
    if not session or session["role"] != "tpo":
        raise HTTPException(status_code=403, detail="TPO access required")

    students = get_all_students()
    total = len(students) or 1

    skill_counts = {}
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
    """Generate 4-tier institutional mentor alerts for at-risk, outperforming, and consistency-lagging students."""
    session = verify_session_token(token)
    if not session or session["role"] != "tpo":
        raise HTTPException(status_code=403, detail="TPO access required")

    all_scored = students_with_scores(token)
    alerts = []

    for s in all_scored:
        score = s["employability_score"]
        backlogs = s["active_backlogs"]
        history = s["interview_attempts"]
        dev_score = s.get("developer_consistency")

        if score >= 85 and (history > 0 or (dev_score and dev_score >= 70)):
            alerts.append({
                "type": "OUTPERFORMING",
                "usn": s["usn"],
                "name": s["name"],
                "score": score,
                "message": f"{s['name']} scored {score}% employability with verified consistency. Prime candidate for Tier-1 Super Dream drives.",
                "color": "green",
                "action_label": "Fast-Track Referral",
                "action_type": "referral"
            })
        elif score < 50 or backlogs >= 2:
            alerts.append({
                "type": "AT_RISK",
                "usn": s["usn"],
                "name": s["name"],
                "score": score,
                "message": f"{s['name']} is at critical risk ({score}% employability, {backlogs} active backlogs). Immediate 1-on-1 counseling mandated.",
                "color": "red",
                "action_label": "Schedule Counseling",
                "action_type": "counseling"
            })
        elif dev_score is not None and dev_score < 40:
            alerts.append({
                "type": "CONSISTENCY_DROP",
                "usn": s["usn"],
                "name": s["name"],
                "score": score,
                "message": f"{s['name']}'s 30-day coding consistency dropped to {dev_score}%. Send practice reminder.",
                "color": "orange",
                "action_label": "Send Consistency Nudge",
                "action_type": "consistency_nudge"
            })
        elif score >= 65 and score < 85 and history >= 1:
            alerts.append({
                "type": "RISING_STAR",
                "usn": s["usn"],
                "name": s["name"],
                "score": score,
                "message": f"{s['name']} showed positive momentum with {score}% employability. Recommend for target off-campus drives & internships.",
                "color": "purple",
                "action_label": "Recommend for Drives",
                "action_type": "recommend_drives"
            })
        elif score < 65 and history == 0:
            alerts.append({
                "type": "NEEDS_INTERVIEW_PRACTICE",
                "usn": s["usn"],
                "name": s["name"],
                "score": score,
                "message": f"{s['name']} hasn't taken any mock interviews yet and scores {score}%. Invite to Project Defense & Technical mock.",
                "color": "orange",
                "action_label": "Invite to Mock Interview",
                "action_type": "invite_interview"
            })

    return alerts

class TpoActionRequest(BaseModel):
    token: str
    usn: str
    action_type: str
    notes: Optional[str] = None

@app.post("/api/tpo/trigger-action")
def tpo_trigger_action(req: TpoActionRequest):
    """Execute actionable interventions from TPO dashboard directly on student record."""
    session = verify_session_token(req.token)
    if not session or session["role"] != "tpo":
        raise HTTPException(status_code=403, detail="TPO access required")

    student = get_student_by_usn(req.usn)
    student_name = student["name"] if student else req.usn
    action_desc = req.action_type.replace("_", " ").title()

    return {
        "success": True,
        "message": f"Action '{action_desc}' successfully dispatched for {student_name} ({req.usn}).",
        "action_type": req.action_type,
        "usn": req.usn,
        "dispatched_by": session["user_id"],
        "timestamp": datetime.datetime.now().isoformat()
    }

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

@app.post("/api/tpo/upload-csv")
async def tpo_upload_csv(token: str = Form(...), file: UploadFile = File(...)):
    """TPO Batch CSV Ingestion for institutional cohorts."""
    session = verify_session_token(token)
    if not session or session["role"] != "tpo":
        raise HTTPException(status_code=403, detail="TPO access required")

    contents = await file.read()
    import csv, io, json
    decoded = decode_csv_bytes(contents)
    reader = csv.DictReader(io.StringIO(decoded))

    students_to_add = []
    for row in reader:
        usn = row.get("usn") or row.get("USN")
        if not usn:
            continue
        skills = {}
        raw_skills = row.get("skills", "")
        if raw_skills:
            try:
                skills = json.loads(raw_skills)
            except:
                for part in raw_skills.split(","):
                    if ":" in part:
                        k, v = part.split(":", 1)
                        try: skills[k.strip()] = float(v.strip())
                        except: skills[k.strip()] = 5.0

        item = {
            "usn": usn.strip().upper(),
            "name": row.get("name") or row.get("Name") or "Student",
            "branch": row.get("branch") or row.get("Branch") or "Computer Science & Engineering",
            "cgpa": float(row.get("cgpa") or row.get("CGPA") or 7.0),
            "semester": int(row.get("semester") or row.get("Semester") or 7),
            "active_backlogs": int(row.get("active_backlogs") or row.get("backlogs") or 0),
            "quantitative_aptitude": float(row.get("quantitative_aptitude") or row.get("aptitude") or 75.0),
            "coding_benchmark": float(row.get("coding_benchmark") or row.get("coding") or 75.0),
            "communication_rating": float(row.get("communication_rating") or row.get("communication") or 7.0),
            "skills": skills,
            "internships": [row.get("internship")] if row.get("internship") else [],
            "certifications": [row.get("certification")] if row.get("certification") else [],
            "projects": [row.get("project")] if row.get("project") else []
        }
        students_to_add.append(item)

    imported = batch_upsert_students(students_to_add)
    return {
        "success": True,
        "imported_count": imported,
        "message": f"Successfully ingested {imported} student records into institutional database."
    }


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

