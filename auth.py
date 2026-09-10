"""Authentication module for AI Placement Predictor v3.
Handles USN-based student login and Employee ID-based TPO login.
Uses simple JSON lookup + JWT-like session tokens.
"""

import json
import hashlib
import time
import hmac
import base64
import os
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
STUDENTS_FILE = DATA_DIR / "students.json"
TPO_FILE = DATA_DIR / "tpo_users.json"
SECRET_KEY = os.getenv("SECRET_KEY", "placement_predictor_secret_key_2026")


def _load_students() -> list[dict]:
    with open(STUDENTS_FILE, "r") as f:
        return json.load(f)


def _load_tpo() -> list[dict]:
    with open(TPO_FILE, "r") as f:
        return json.load(f)


def _save_students(students: list[dict]):
    with open(STUDENTS_FILE, "w") as f:
        json.dump(students, f, indent=2)


def login_student(usn: str, password: str) -> dict | None:
    """
    Authenticate student by USN and password.
    Returns student data (without password) or None if invalid.
    """
    students = _load_students()
    for s in students:
        if s["usn"].upper() == usn.upper() and s["password"] == password:
            student_data = {k: v for k, v in s.items() if k != "password"}
            return student_data
    return None


def login_tpo(employee_id: str, password: str) -> dict | None:
    """
    Authenticate TPO/faculty by employee ID and password.
    Returns user data (without password) or None if invalid.
    """
    tpo_users = _load_tpo()
    for u in tpo_users:
        if u["employee_id"].upper() == employee_id.upper() and u["password"] == password:
            return {k: v for k, v in u.items() if k != "password"}
    return None


def create_session_token(user_id: str, role: str) -> str:
    """
    Create a simple signed session token.
    Format: base64(user_id:role:timestamp):signature
    """
    payload = f"{user_id}:{role}:{int(time.time())}"
    payload_b64 = base64.b64encode(payload.encode()).decode()
    sig = hmac.new(SECRET_KEY.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
    return f"{payload_b64}.{sig}"


def verify_session_token(token: str) -> dict | None:
    """
    Verify and decode a session token.
    Returns {"user_id": ..., "role": ..., "timestamp": ...} or None.
    """
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None
        payload_b64, sig = parts
        expected_sig = hmac.new(SECRET_KEY.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected_sig):
            return None
        payload = base64.b64decode(payload_b64.encode()).decode()
        user_id, role, timestamp = payload.split(":")
        # Tokens expire after 8 hours
        if int(time.time()) - int(timestamp) > 28800:
            return None
        return {"user_id": user_id, "role": role, "timestamp": int(timestamp)}
    except Exception:
        return None


def get_student_by_usn(usn: str) -> dict | None:
    """Get student data by USN (without password)."""
    students = _load_students()
    for s in students:
        if s["usn"].upper() == usn.upper():
            return {k: v for k, v in s.items() if k != "password"}
    return None


def get_all_students() -> list[dict]:
    """Get all students (without passwords)."""
    students = _load_students()
    return [{k: v for k, v in s.items() if k != "password"} for s in students]


def save_interview_result(usn: str, interview_result: dict):
    """Save an interview result to the student's record."""
    students = _load_students()
    for s in students:
        if s["usn"].upper() == usn.upper():
            if "interview_history" not in s:
                s["interview_history"] = []
            s["interview_history"].append(interview_result)
            break
    _save_students(students)
