"""
Synthetic Realistic Student Employability Dataset Generator
Models multi-tier academic, technical, practical, aptitude, and soft-skill signals
calibrated against real-world Indian engineering campus recruitment data.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from pathlib import Path

def generate_student_dataset(n_samples: int = 15000, random_seed: int = 42) -> pd.DataFrame:
    np.random.seed(random_seed)
    
    branches = ["CSE", "ISE", "ECE", "EEE", "Mech", "Civil"]
    branch_weights = [0.35, 0.20, 0.20, 0.10, 0.10, 0.05]
    student_branches = np.random.choice(branches, size=n_samples, p=branch_weights)
    
    semesters = np.random.choice([6, 7, 8], size=n_samples, p=[0.2, 0.6, 0.2])
    
    # Academics
    cgpa = np.clip(np.random.normal(loc=7.4, scale=1.1, size=n_samples), 5.0, 9.9)
    tenth_pct = np.clip(cgpa * 8.5 + np.random.normal(loc=12.0, scale=6.0, size=n_samples), 55.0, 98.0)
    twelfth_pct = np.clip(cgpa * 8.2 + np.random.normal(loc=11.0, scale=7.0, size=n_samples), 50.0, 97.0)
    
    # Backlogs (correlated with lower CGPA)
    backlog_prob = np.clip((8.5 - cgpa) * 0.22, 0.02, 0.75)
    backlogs_history = np.random.binomial(n=4, p=backlog_prob)
    active_backlogs = np.array([np.random.randint(0, bh + 1) if bh > 0 else 0 for bh in backlogs_history])
    
    # Aptitude benchmarks
    quant = np.clip(cgpa * 8.0 + np.random.normal(loc=15.0, scale=12.0, size=n_samples), 30.0, 99.0)
    logical = np.clip(cgpa * 7.8 + np.random.normal(loc=18.0, scale=11.0, size=n_samples), 30.0, 99.0)
    
    # Coding benchmark (CS/IS students generally perform higher)
    cs_bias = np.isin(student_branches, ["CSE", "ISE"]).astype(float) * 12.0
    coding = np.clip(cgpa * 7.5 + cs_bias + np.random.normal(loc=10.0, scale=14.0, size=n_samples), 20.0, 99.0)
    
    # Technical competencies (0 to 10 scale) — allow realistic zeroes for unlearned stacks
    skills_python = np.clip((coding / 10.0) + np.random.normal(0, 1.2, n_samples), 0.0, 10.0)
    skills_java = np.clip((coding / 10.5) + np.random.normal(0, 1.3, n_samples), 0.0, 10.0)
    skills_cpp = np.clip((coding / 11.0) + np.random.normal(0, 1.4, n_samples), 0.0, 10.0)
    skills_dsa = np.clip((coding / 10.0) * 0.8 + (cgpa / 10.0) * 2.0 + np.random.normal(0, 1.0, n_samples), 0.0, 10.0)
    skills_sql = np.clip((quant / 12.0) + (cgpa / 2.5) + np.random.normal(0, 1.1, n_samples), 0.0, 10.0)
    skills_web = np.clip((cs_bias / 2.0) + np.random.normal(5.0, 2.2, n_samples), 0.0, 10.0)
    skills_cloud = np.clip(np.random.normal(3.8, 2.0, n_samples), 0.0, 10.0)
    skills_ml = np.clip((quant / 15.0) + np.random.normal(3.5, 2.1, n_samples), 0.0, 10.0)

    # 18% of students have zero or unstudied DSA
    dsa_zero_mask = np.random.binomial(1, 0.18, n_samples).astype(bool)
    skills_dsa = np.where(dsa_zero_mask, 0.0, skills_dsa)

    # 20% of students have zero database / SQL
    sql_zero_mask = np.random.binomial(1, 0.20, n_samples).astype(bool)
    skills_sql = np.where(sql_zero_mask, 0.0, skills_sql)
    
    # Experience & Practical Work
    internships = np.random.choice([0, 1, 2, 3], size=n_samples, p=[0.45, 0.35, 0.15, 0.05])
    projects_count = np.clip(np.random.poisson(lam=2.5, size=n_samples), 0, 7)
    certifications_count = np.clip(np.random.poisson(lam=1.5, size=n_samples), 0, 5)
    hackathons = np.random.choice([0, 1, 2, 3, 4], size=n_samples, p=[0.50, 0.25, 0.15, 0.07, 0.03])
    
    # Soft skills & Interview
    comm_score = np.clip(np.random.normal(loc=7.0, scale=1.4, size=n_samples), 3.0, 10.0)
    interview_score = np.clip(comm_score * 0.6 + (logical / 25.0) + np.random.normal(0, 0.9, n_samples), 3.0, 10.0)
    
    # Online Assessment (OA) Hard Screening Barrier:
    # In corporate drives (Google, Amazon, TCS Digital, Cisco, Oracle), DSA >= 4.0
    # OR (SQL >= 5.5 and Python >= 5.5 for Data roles) is mandatory to clear Round 1.
    oa_cleared = (skills_dsa >= 4.0) | ((skills_sql >= 5.5) & (skills_python >= 5.5))
    oa_penalty = np.where(~oa_cleared, -3.2, 0.0)

    # Academic-only trap: High CGPA (>= 8.5) but zero practical problem-solving (DSA < 3.0 & SQL < 3.0)
    academic_only_penalty = np.where((cgpa >= 8.5) & (skills_dsa < 3.0) & (skills_sql < 3.0), -2.2, 0.0)

    # Employability Probability Logit (latent ground truth)
    z = (
        0.45 * (cgpa - 7.0)
        + 0.025 * (coding - 55.0)
        + 0.012 * (quant - 55.0)
        + 0.012 * (logical - 55.0)
        + 0.60 * internships
        + 0.20 * projects_count
        + 0.20 * certifications_count
        + 0.40 * (skills_dsa - 5.0)
        + 0.25 * (skills_sql - 5.0)
        + 0.18 * (comm_score - 6.0)
        + 0.20 * (interview_score - 6.0)
        - 1.10 * active_backlogs
        - 0.35 * backlogs_history
        + oa_penalty
        + academic_only_penalty
        + np.random.normal(0, 0.45, n_samples)
    )
    
    placement_prob = 1.0 / (1.0 + np.exp(-z))
    placed = (placement_prob >= 0.50).astype(int)
    
    # Readiness Tier
    readiness = np.where(
        placement_prob >= 0.75, "Ready",
        np.where(placement_prob >= 0.60, "Near-Ready", "Needs Training")
    )
    
    # Primary Track Affinity
    track_scores = {
        "Full-Stack Developer": skills_web * 1.5 + skills_java * 1.0 + skills_sql * 1.0,
        "Data Analyst / ML Engineer": skills_ml * 1.6 + skills_python * 1.2 + skills_sql * 1.2,
        "Cloud / DevOps Engineer": skills_cloud * 1.7 + skills_python * 0.9 + skills_sql * 0.8,
        "QA Specialist": skills_java * 1.2 + comm_score * 0.8 + (10.0 - coding / 10.0),
        "Core Systems / SDE": skills_dsa * 1.8 + skills_cpp * 1.5 + (coding / 10.0) * 1.2
    }
    track_df = pd.DataFrame(track_scores)
    primary_track = track_df.idxmax(axis=1)
    
    df = pd.DataFrame({
        "student_id": [f"STU-2026-{i+1:05d}" for i in range(n_samples)],
        "branch": student_branches,
        "semester": semesters,
        "cgpa": np.round(cgpa, 2),
        "tenth_percentage": np.round(tenth_pct, 1),
        "twelfth_percentage": np.round(twelfth_pct, 1),
        "backlogs_history": backlogs_history,
        "active_backlogs": active_backlogs,
        "quantitative_aptitude": np.round(quant, 1),
        "logical_reasoning": np.round(logical, 1),
        "coding_benchmark": np.round(coding, 1),
        "skills_python": np.round(skills_python, 1),
        "skills_java": np.round(skills_java, 1),
        "skills_cpp": np.round(skills_cpp, 1),
        "skills_dsa": np.round(skills_dsa, 1),
        "skills_sql": np.round(skills_sql, 1),
        "skills_web": np.round(skills_web, 1),
        "skills_cloud": np.round(skills_cloud, 1),
        "skills_ml": np.round(skills_ml, 1),
        "internships": internships,
        "projects_count": projects_count,
        "certifications_count": certifications_count,
        "hackathons": hackathons,
        "communication_rating": np.round(comm_score, 1),
        "interview_rating": np.round(interview_score, 1),
        "primary_track": primary_track,
        "placement_probability": np.round(placement_prob * 100.0, 1),
        "readiness_status": readiness,
        "placed": placed
    })
    
    return df

if __name__ == "__main__":
    out_path = Path(__file__).resolve().parent.parent / "data" / "student_placement_dataset.csv"
    df = generate_student_dataset(15000)
    df.to_csv(out_path, index=False)
    print(f"Generated {len(df)} records at {out_path}")
    print(df["readiness_status"].value_counts(normalize=True))
