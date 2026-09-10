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


def update_student_profile(usn: str, updates: dict) -> dict | None:
    """Update profile fields for a student and persist."""
    students = _load_students()
    updated_student = None
    for s in students:
        if s["usn"].upper() == usn.upper():
            for k, v in updates.items():
                if k not in ["usn", "password"]:  # preserve credentials
                    s[k] = v
            updated_student = {k: val for k, val in s.items() if k != "password"}
            break
    if updated_student:
        _save_students(students)
    return updated_student


def batch_upsert_students(new_students: list[dict]) -> int:
    """Batch add or update students from CSV data."""
    students = _load_students()
    existing_map = {s["usn"].upper(): i for i, s in enumerate(students)}
    count = 0
    for ns in new_students:
        usn_key = ns.get("usn", "").strip().upper()
        if not usn_key:
            continue
        if usn_key in existing_map:
            idx = existing_map[usn_key]
            for k, v in ns.items():
                if k != "password":
                    students[idx][k] = v
        else:
            if "password" not in ns:
                ns["password"] = "student123"
            students.append(ns)
            existing_map[usn_key] = len(students) - 1
        count += 1
    _save_students(students)
    return count


def usn_exists(usn: str) -> bool:
    """Check if a USN is already registered."""
    students = _load_students()
    return any(s["usn"].upper() == usn.upper() for s in students)


def register_student(profile: dict) -> dict:
    """
    Register a new self-signup student.
    Assigns USN, hashes nothing (plain password stored same as mock data).
    Returns the created student record (without password).
    """
    students = _load_students()

    # Auto-generate USN if not provided
    usn = profile.get("usn", "").strip().upper()
    if not usn:
        # Generate USN: SELF-YYYY-NNNN
        import datetime
        year = datetime.datetime.now().year % 100
        existing_self = [s for s in students if s["usn"].startswith("SELF")]
        seq = len(existing_self) + 1
        usn = f"SELF{year:02d}{seq:04d}"

    # Build full student record with defaults
    student = {
        "usn": usn,
        "password": profile.get("password", "changeme123"),
        "name": profile.get("name", "Student"),
        "branch": profile.get("branch", "Computer Science & Engineering"),
        "semester": int(profile.get("semester", 7)),
        "cgpa": float(profile.get("cgpa", 7.0)),
        "active_backlogs": int(profile.get("active_backlogs", 0)),
        "backlogs_history": int(profile.get("backlogs_history", 0)),
        "quantitative_aptitude": int(profile.get("quantitative_aptitude", 70)),
        "logical_reasoning": int(profile.get("logical_reasoning", 70)),
        "coding_benchmark": int(profile.get("coding_benchmark", 70)),
        "communication_rating": float(profile.get("communication_rating", 7.0)),
        "interview_rating": float(profile.get("interview_rating", 7.0)),
        "target_role": profile.get("target_role", "SDE"),
        "target_lpa": float(profile.get("target_lpa", 10.0)),
        "skills": profile.get("skills", {}),
        "certifications": profile.get("certifications", []),
        "internships": profile.get("internships", []),
        "projects": profile.get("projects", []),
        # Platform usernames
        "github_username": profile.get("github_username", ""),
        "leetcode_username": profile.get("leetcode_username", ""),
        "hackerrank_username": profile.get("hackerrank_username", ""),
        "codeforces_username": profile.get("codeforces_username", ""),
        # Metadata
        "email": profile.get("email", ""),
        "phone": profile.get("phone", ""),
        "self_registered": True,
        "interview_history": [],
        "platform_stats": {},
        "platform_stats_history": []
    }

    students.append(student)
    _save_students(students)
    return {k: v for k, v in student.items() if k != "password"}


def save_platform_stats(usn: str, stats: dict):
    """Save fetched platform stats snapshot to student record."""
    students = _load_students()
    for s in students:
        if s["usn"].upper() == usn.upper():
            s["platform_stats"] = stats
            if "platform_stats_history" not in s:
                s["platform_stats_history"] = []
            s["platform_stats_history"].append(stats)
            # Keep only last 30 snapshots
            s["platform_stats_history"] = s["platform_stats_history"][-30:]
            break
    _save_students(students)


def update_student_skills_from_platforms(usn: str, platform_stats: dict):
    """
    Auto-update student skill levels based on platform activity.
    e.g. if LeetCode hard solved > 50, bump DSA skill.
    """
    students = _load_students()
    for s in students:
        if s["usn"].upper() == usn.upper():
            skills = s.get("skills", {})

            # LeetCode → DSA skill
            lc = platform_stats.get("leetcode", {})
            if not lc.get("error"):
                hard = lc.get("hard_solved", 0)
                medium = lc.get("medium_solved", 0)
                total = lc.get("total_solved", 0)
                if hard >= 50:
                    skills["DSA"] = max(skills.get("DSA", 1), 9)
                elif hard >= 20:
                    skills["DSA"] = max(skills.get("DSA", 1), 8)
                elif medium >= 50:
                    skills["DSA"] = max(skills.get("DSA", 1), 7)
                elif total >= 50:
                    skills["DSA"] = max(skills.get("DSA", 1), 6)

            # GitHub → language skills
            gh = platform_stats.get("github", {})
            if not gh.get("error"):
                lang_map = {
                    "Python": "Python", "JavaScript": "JavaScript", "TypeScript": "JavaScript",
                    "Java": "Java", "C++": "C++", "C": "C", "Go": "Go", "Rust": "Rust",
                    "Kotlin": "Kotlin", "Swift": "Swift", "Ruby": "Ruby", "PHP": "PHP"
                }
                for lang_item in gh.get("top_languages", []):
                    lang = lang_item.get("language", "")
                    repos = lang_item.get("repos", 0)
                    skill_name = lang_map.get(lang)
                    if skill_name and repos >= 3:
                        skills[skill_name] = max(skills.get(skill_name, 1), min(8, 4 + repos))

                # Coding benchmark from activity
                activity = gh.get("activity_score", 0)
                if activity > 0:
                    s["coding_benchmark"] = max(s.get("coding_benchmark", 70), min(95, 60 + activity // 3))

            # Codeforces → DSA + competitive
            cf = platform_stats.get("codeforces", {})
            if not cf.get("error"):
                rating = cf.get("rating", 0)
                if rating >= 2000:
                    skills["DSA"] = max(skills.get("DSA", 1), 10)
                elif rating >= 1600:
                    skills["DSA"] = max(skills.get("DSA", 1), 9)
                elif rating >= 1200:
                    skills["DSA"] = max(skills.get("DSA", 1), 7)

            s["skills"] = skills
            break

    _save_students(students)

