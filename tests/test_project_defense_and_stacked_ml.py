import pytest
from fastapi.testclient import TestClient
from api.main import app
from auth import login_student, login_tpo, create_session_token, get_student_by_usn
from ml.model_trainer import predict_student_employability, load_or_train_model
from interview.question_bank import get_company_interview_rounds, get_project_defense_interview_rounds
from upskilling.developer_sync import (
    fetch_github_activity,
    fetch_leetcode_activity,
    compute_developer_consistency_score,
    sync_student_developer_profiles
)

client = TestClient(app)

@pytest.fixture
def student_auth():
    auth = login_student("4JN25CS001", "pass@001")
    assert auth is not None
    token = create_session_token("4JN25CS001", "student")
    return {"token": token, "usn": "4JN25CS001"}

@pytest.fixture
def tpo_auth():
    auth = login_tpo("TPO-001", "tpo@admin")
    assert auth is not None
    token = create_session_token("TPO-001", "tpo")
    return {"token": token, "employee_id": "TPO-001"}

def test_stacked_model_and_engineered_signals():
    bundle = load_or_train_model()
    assert "ensemble" in bundle
    assert "StackingClassifier" in str(type(bundle["ensemble"]))
    assert "metrics" in bundle
    metrics = bundle["metrics"]
    assert metrics["roc_auc"] >= 0.98
    assert metrics["accuracy"] >= 0.95

    dummy_student = {
        "student_id": "TEST-STU-STACK",
        "cgpa": 8.4,
        "skills": {"Python": 9.0, "DSA": 8.0, "SQL": 7.0, "React": 6.0},
        "coding_benchmark": 85.0,
        "active_backlogs": 0,
        "backlogs_history": 1,
        "internships": [{"company": "Amazon"}],
        "projects": [{"name": "P1"}, {"name": "P2"}],
        "hackathons": 1
    }
    pred = predict_student_employability(dummy_student)
    assert "placement_probability" in pred
    assert "engineered_signals" in pred
    eng = pred["engineered_signals"]
    assert "skill_depth_ratio" in eng
    assert "coding_academic_balance" in eng
    assert "backlog_recovery_rate" in eng
    assert "practical_exposure_score" in eng
    assert eng["backlog_recovery_rate"] == 1.0  # 1 history, 0 active -> fully recovered
    assert eng["practical_exposure_score"] > 0

def test_project_defense_interview_rounds():
    student_projects = [
        {"name": "Distributed In-Memory Cache", "tech_stack": "Go, Redis", "architecture": "LSM tree with Raft consensus"},
        {"name": "PlaceIQ Employability Engine", "tech_stack": "Python, FastAPI", "architecture": "Microservices"}
    ]
    rounds = get_project_defense_interview_rounds("Google", student_projects, {"Python": 8, "Go": 7})
    assert len(rounds) == 2
    assert rounds[0]["round_id"] == 1
    assert "Project Architecture" in rounds[0]["name"]
    # Check that the student's project name is present in the questions
    questions_text = " ".join(q["question"] for q in rounds[0]["questions"])
    assert "Distributed In-Memory Cache" in questions_text

    assert rounds[1]["round_id"] == 2
    assert "Behavioral" in rounds[1]["name"]

def test_developer_sync_engine():
    # Test fallback & consistency computation
    gh = fetch_github_activity("torvalds")
    assert gh["status"] in ["live", "verified_cached_rate_limited", "verified_cached_offline"]
    assert gh["active_days_last_30"] >= 0

    lc = fetch_leetcode_activity("sample_dev")
    assert "total_solved" in lc

    consistency = compute_developer_consistency_score(gh, lc)
    assert 0 <= consistency["consistency_score"] <= 100
    assert "tier" in consistency
    assert "current_streak_days" in consistency

def test_api_developer_sync(student_auth):
    resp = client.post(
        "/api/student/developer-sync",
        json={
            "usn": student_auth["usn"],
            "token": student_auth["token"],
            "github_handle": "priyapatel-dev",
            "leetcode_handle": "priya_codes"
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "developer_activity" in data
    dev = data["developer_activity"]
    assert "consistency" in dev
    assert dev["consistency"]["consistency_score"] > 0

def test_api_jobs_matched(student_auth):
    resp = client.get(f"/api/jobs/matched?usn={student_auth['usn']}&token={student_auth['token']}")
    assert resp.status_code == 200
    data = resp.json()
    assert "best_matches" in data
    assert "near_matches" in data
    assert "stretch_matches" in data
    assert "aggregate_skill_gap_matrix" in data
    assert len(data["best_matches"]) + len(data["near_matches"]) + len(data["stretch_matches"]) > 0
    # Check aggregate gap matrix items have frequency and skill
    if data["aggregate_skill_gap_matrix"]:
        first_gap = data["aggregate_skill_gap_matrix"][0]
        assert "skill" in first_gap
        assert "frequency" in first_gap

def test_api_tpo_4_tier_alerts_and_actions(tpo_auth):
    resp = client.get(f"/api/tpo/alerts?token={tpo_auth['token']}")
    assert resp.status_code == 200
    alerts = resp.json()
    assert isinstance(alerts, list)
    assert len(alerts) > 0
    for a in alerts:
        assert "type" in a
        assert a["type"] in ["OUTPERFORMING", "AT_RISK", "CONSISTENCY_DROP", "RISING_STAR", "NEEDS_INTERVIEW_PRACTICE"]
        assert "action_label" in a
        assert "action_type" in a

    # Test trigger action
    first_alert = alerts[0]
    action_resp = client.post(
        "/api/tpo/trigger-action",
        json={
            "token": tpo_auth["token"],
            "usn": first_alert["usn"],
            "action_type": first_alert["action_type"]
        }
    )
    assert action_resp.status_code == 200
    assert action_resp.json()["success"] is True

def test_professional_hr_progression_and_self_intro(student_auth):
    resp = client.post(
        "/api/interview/start",
        json={
            "usn": student_auth["usn"],
            "token": student_auth["token"],
            "company": "Google",
            "track": "project_defense"
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["track"] == "project_defense"
    questions = data["questions"]
    assert len(questions) == 5

    # Q1 must be Self-Introduction & Background
    assert "introduce yourself" in questions[0]["question"].lower()
    assert questions[0]["topic"] == "Self-Introduction & Background"

    # Q2 must be Project Architecture walkthrough
    assert "architecture" in questions[1]["question"].lower()

    # Q3 must be Trade-offs & Failure Modes
    assert "trade-off" in questions[2]["question"].lower() or "failure mode" in questions[2]["question"].lower()

    # Q4 must be STAR Behavioral
    assert "star" in questions[3]["question"].lower() or "deadline" in questions[3]["question"].lower()

    # Q5 must be Company Alignment
    assert "google" in questions[4]["question"].lower()

def test_adaptive_project_selection_and_followup(student_auth):
    # Case A: Candidate explicitly mentions a project ("Cluster Manager")
    resp = client.post(
        "/api/interview/analyze-answer",
        json={
            "usn": student_auth["usn"],
            "token": student_auth["token"],
            "company": "Google",
            "question_index": 0,
            "question": "Welcome to your interview with Google. To start off, please introduce yourself — tell me about your background, the core engineering domains you specialize in, and give me a brief overview of the projects you have built.",
            "spoken_answer": "Hi, I am Priya Patel. I study computer science and I built a Cluster Manager project to orchestrate containers across nodes.",
            "topic": "Self-Introduction & Background",
            "track": "project_defense"
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "next_question" in data
    next_q = data["next_question"]
    assert next_q["round_id"] == 1
    assert "cluster manager" in next_q["question"].lower() or "cluster manager" in str(next_q.get("project_name", "")).lower()

    # Case B: Candidate introduces themselves without mentioning a specific project
    resp_no_proj = client.post(
        "/api/interview/analyze-answer",
        json={
            "usn": "",
            "token": student_auth["token"],
            "company": "Amazon",
            "question_index": 0,
            "question": "Welcome to your interview with Amazon. To start off, please introduce yourself.",
            "spoken_answer": "Hello, I am a software engineer passionate about backend distributed systems and algorithmic problem solving.",
            "topic": "Self-Introduction & Background",
            "track": "project_defense"
        }
    )
    assert resp_no_proj.status_code == 200
    data_no_proj = resp_no_proj.json()
    assert "next_question" in data_no_proj
    next_q_no_proj = data_no_proj["next_question"]
    assert "project" in next_q_no_proj["question"].lower()

