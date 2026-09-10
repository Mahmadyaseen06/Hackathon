import pytest
from upskilling.skill_gap_engine import diagnose_skill_gaps, load_benchmarks
from upskilling.roadmap_generator import generate_personalized_roadmap
from upskilling.content_recommender import get_content_recommendations
from upskilling.project_ladder import get_project_recommendations
from upskilling.internship_matcher import match_internships
from upskilling.monitoring_tracker import log_student_activity, get_student_monitoring_metrics

def test_skill_gap_diagnostic():
    student = {
        "cgpa": 7.5,
        "skills": {"JavaScript": 9, "React": 8},
        "target_role": "Full-Stack Developer"
    }
    result = diagnose_skill_gaps(student, "full_stack")
    assert "track_readiness_score" in result
    assert 0 <= result["track_readiness_score"] <= 100
    assert "critical_gaps" in result
    assert "mastered_skills" in result
    assert any(s["skill"] == "JavaScript" for s in result["mastered_skills"])

def test_roadmap_generator():
    roadmap = generate_personalized_roadmap(
        student_data={},
        missing_skills=["Docker", "Kubernetes"],
        target_role="Cloud / DevOps Engineer",
        target_lpa=14.0
    )
    assert roadmap["total_weeks"] == 8
    assert len(roadmap["weeks"]) == 8
    assert "milestone" in roadmap["weeks"][0]

def test_content_recommender():
    recs = get_content_recommendations(["DSA", "React"])
    assert len(recs["youtube_videos"]) > 0
    assert len(recs["nptel_courses"]) > 0

def test_internship_matcher():
    student = {"skills": {"Python": 8, "C++": 7}, "cgpa": 8.0}
    matches = match_internships(student)
    assert len(matches) >= 4
    assert any("gsoc" in m["id"] for m in matches)

def test_monitoring_tracker():
    log_student_activity("TEST-TRACK", "dsa_solved", "Solved 3 Mediums", 60)
    metrics = get_student_monitoring_metrics("TEST-TRACK")
    assert "consistency_score_30d" in metrics
    assert "total_hours_logged_30d" in metrics
    assert "coding_profiles" in metrics
