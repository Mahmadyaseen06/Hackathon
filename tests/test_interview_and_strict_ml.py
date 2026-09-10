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
