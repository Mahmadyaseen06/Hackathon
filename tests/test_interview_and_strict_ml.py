import pytest
from api.code_executor import execute_code
from ml.model_trainer import predict_student_employability
from interview.question_bank import get_calibrated_questions

def test_code_executor_basic():
    res = execute_code("print(10 + 25)", "python")
    assert res["success"] is True
    assert "35" in res["output"]
    assert res["runtime_ms"] >= 0

def test_code_executor_test_cases():
    code = """
import sys
x = int(sys.stdin.read().strip())
print(x * 3)
"""
    test_cases = [
        {"input": "3", "expected_output": "9"},
        {"input": "5", "expected_output": "15"}
    ]
    res = execute_code(code, "python", stdin="3", test_cases=test_cases)
    assert res["tests_passed"] == 2
    assert res["tests_total"] == 2

def test_strict_ml_basic_python_not_job_ready():
    """Verify student claiming only basic python is NOT placed in Ready tier."""
    student = {
        "name": "Beginner Student",
        "branch": "CSE",
        "cgpa": 7.0,
        "skills": {"Python": 3},
        "projects": [],
        "internships": [],
        "certifications": []
    }
    result = predict_student_employability(student)
    assert result["placement_probability"] < 40.0
    assert result["readiness_status"] == "Needs Training"
    assert len(result["reality_check_penalties"]) > 0
    assert any("Only 1 skill" in p or "beginner level" in p for p in result["reality_check_penalties"])

def test_calibrated_questions_has_coding_challenge():
    """Verify that calibrated questions include a practical coding challenge with test cases."""
    questions = get_calibrated_questions("Google", {"Python": 7, "DSA": 6}, num_questions=5)
    coding_qs = [q for q in questions if "test_cases" in q and len(q["test_cases"]) > 0]
    assert len(coding_qs) >= 1
    assert "starter_code" in coding_qs[0]
    assert "examples" in coding_qs[0]

def test_company_interview_rounds():
    """Verify structured 3-round generation for company interview."""
    from interview.question_bank import get_company_interview_rounds
    rounds = get_company_interview_rounds("Google", {"Python": 8, "DSA": 7})
    assert len(rounds) == 3
    assert rounds[0]["type"] == "coding"
    assert "Coding Assessment" in rounds[0]["name"]
    assert rounds[1]["type"] == "technical"
    assert "Technical Deep Dive" in rounds[1]["name"]
    assert rounds[2]["type"] == "behavioral"
    assert "Leadership" in rounds[2]["name"] or "Behavioral" in rounds[2]["name"]

def test_compute_round_breakdown():
    """Verify round breakdown aggregation logic."""
    from interview.analyzer import _compute_round_breakdown
    qa_pairs = [
        {"round_id": 1, "round_name": "Round 1: OA", "score": 8, "code": "print(1)"},
        {"round_id": 2, "round_name": "Round 2: Tech", "score": 7},
        {"round_id": 3, "round_name": "Round 3: Behavioral", "score": 9}
    ]
    breakdown = _compute_round_breakdown(qa_pairs)
    assert len(breakdown) == 3
    assert breakdown[0]["round_id"] == 1
    assert breakdown[0]["score"] == 80
    assert breakdown[0]["status"] == "Passed"
    assert breakdown[0]["code_submissions"] == 1
    assert breakdown[1]["round_id"] == 2
    assert breakdown[1]["score"] == 70
    assert breakdown[2]["round_id"] == 3
    assert breakdown[2]["score"] == 90
