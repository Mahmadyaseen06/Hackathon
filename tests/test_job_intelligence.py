import pytest
from job_intelligence.skill_taxonomy import get_skill, all_canonical
from job_intelligence.normalizer import canonicalize_one, split_required_preferred
from job_intelligence.dedupe import job_fingerprint
from job_intelligence.eligibility import evaluate
from job_intelligence.matcher import score, rank
from job_intelligence.demo_data import build_demo_jobs
from job_intelligence.models import JobPosting, StudentProfile, MatchCategory

def test_taxonomy_canonicalization():
    assert get_skill("Python").canonical == "Python"
    assert canonicalize_one("react.js") == "React"
    assert canonicalize_one("Golang") == "Go"

def test_deduplication():
    f1 = job_fingerprint("amazon", "SDE 1", "Bangalore", "https://amazon.jobs/1", "101")
    f2 = job_fingerprint("amazon", "sde 1", "bangalore", "https://amazon.jobs/1", "101")
    assert f1 == f2

def test_eligibility_and_scoring():
    demo_jobs = build_demo_jobs()
    student = StudentProfile(
        student_id="TEST-STU",
        cgpa=8.5,
        backlogs=0,
        skills={"Python": 9.0, "DSA": 8.0, "Machine Learning": 8.0, "Statistics": 7.0}
    )
    res = score(demo_jobs[2], student) # NVIDIA ML Intern
    assert 0 <= res.job_fit_score <= 100
    assert 0 <= res.readiness_score <= 100
    assert res.category in [MatchCategory.BEST_MATCH, MatchCategory.NEAR_MATCH, MatchCategory.STRETCH]
    assert res.eligibility.status in ["eligible", "partially_eligible", "not_eligible"]
