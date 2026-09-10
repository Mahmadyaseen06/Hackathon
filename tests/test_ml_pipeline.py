import pytest
import numpy as np
from ml.dataset_generator import generate_student_dataset
from ml.pipeline import extract_features_from_student, predict_career_track_alignment
from ml.model_trainer import predict_student_employability, load_or_train_model

def test_dataset_generation():
    df = generate_student_dataset(100)
    assert len(df) == 100
    assert "placement_probability" in df.columns
    assert "readiness_status" in df.columns
    assert set(df["readiness_status"].unique()).issubset({"Ready", "Near-Ready", "Needs Training"})

def test_feature_extraction():
    dummy = {
        "cgpa": 8.0,
        "skills": {"Python": 8, "DSA": 7},
        "internships": [{"company": "Test"}],
        "projects": [{"name": "P1"}, {"name": "P2"}]
    }
    feat = extract_features_from_student(dummy)
    assert feat.shape == (1, 23)
    assert feat["cgpa"].iloc[0] == 8.0
    assert feat["skills_python"].iloc[0] == 8.0
    assert feat["internships"].iloc[0] == 1
    assert feat["projects_count"].iloc[0] == 2

def test_prediction_and_xai():
    dummy = {
        "student_id": "TEST-01",
        "cgpa": 8.5,
        "skills": {"Python": 9, "DSA": 8, "SQL": 8},
        "internships": [1, 2],
        "projects": [1, 2, 3],
        "active_backlogs": 0
    }
    res = predict_student_employability(dummy)
    assert "placement_probability" in res
    assert 0 <= res["placement_probability"] <= 100
    assert res["readiness_status"] in ["Ready", "Near-Ready", "Needs Training"]
    assert "factor_transparency" in res
    factors = res["factor_transparency"]
    assert "positive_factors" in factors
    assert "negative_factors" in factors
    assert len(factors["positive_factors"]) > 0 or len(factors["negative_factors"]) > 0
