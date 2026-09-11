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
    sde_roadmap = generate_personalized_roadmap(
        student_data={},
        missing_skills=["System Design", "Microservices"],
        target_role="Full-Stack SDE",
        target_lpa=12.0
    )
    assert sde_roadmap["total_weeks"] == 8
    assert len(sde_roadmap["weeks"]) == 8
    assert sde_roadmap["track"] == "sde"

    ds_roadmap = generate_personalized_roadmap(
        student_data={},
        missing_skills=["PyTorch", "Pandas"],
        target_role="Data Science & AI",
        target_lpa=14.0
    )
    assert ds_roadmap["track"] == "data_science"
    assert "Data Science" in ds_roadmap["track_title"]

    devops_roadmap = generate_personalized_roadmap(
        student_data={},
        missing_skills=["Docker", "Kubernetes"],
        target_role="Cloud / DevOps Engineer",
        target_lpa=14.0
    )
    assert devops_roadmap["track"] == "cloud_devops"

    cyber_roadmap = generate_personalized_roadmap(
        student_data={},
        missing_skills=["Burp Suite", "OWASP"],
        target_role="Cybersecurity Specialist",
        target_lpa=12.0
    )
    assert cyber_roadmap["track"] == "cybersecurity"

    # Verify roadmaps across different courses are distinct and customized
    assert sde_roadmap["track_title"] != ds_roadmap["track_title"]
    assert ds_roadmap["weeks"][0]["title"] != devops_roadmap["weeks"][0]["title"]

def test_linkedin_reviewer():
    from upskilling.linkedin_reviewer import review_linkedin_profile, get_linkedin_preset
    
    preset = get_linkedin_preset("generic_student")
    assert preset is not None
    assert "headline" in preset
    
    review = review_linkedin_profile(
        headline=preset["headline"],
        about=preset["about"],
        experience=preset["experience"],
        target_role="Full-Stack SDE"
    )
    
    assert "score" in review
    assert "recruiter_score" in review
    assert 0 <= review["recruiter_score"] <= 100
    assert "headline_analysis" in review
    assert len(review["headline_analysis"]["optimized_headlines"]) >= 3
    assert "keyword_analysis" in review
    assert len(review["experience_star_optimizer"]) >= 1
    assert "about_analysis" in review
    assert "checklist" in review

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
