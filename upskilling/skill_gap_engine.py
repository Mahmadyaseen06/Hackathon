"""
Skill Gap Diagnostic Engine
Compares evaluated student competencies against target career track benchmarks
to isolate specific technical, aptitude, and practical deficits.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, List

BENCHMARKS_PATH = Path(__file__).resolve().parent.parent / "data" / "benchmark_profiles.json"

def load_benchmarks() -> Dict[str, Any]:
    if BENCHMARKS_PATH.exists():
        with open(BENCHMARKS_PATH, "r") as f:
            return json.load(f).get("tracks", {})
    return {}

def diagnose_skill_gaps(student_data: Dict[str, Any], target_track_id: str | None = None) -> Dict[str, Any]:
    """
    Diagnoses student gaps against a target track.
    If target_track_id is None, defaults to student's target_role or 'full_stack'.
    """
    benchmarks_data = load_benchmarks()
    
    # Map track title or id
    track_key = target_track_id
    if not track_key or track_key not in benchmarks_data:
        # Match by name
        target_role = student_data.get("target_role", "").lower()
        if "data" in target_role or "ml" in target_role or "analyst" in target_role:
            track_key = "data_ai_ml"
        elif "cloud" in target_role or "devops" in target_role:
            track_key = "cloud_devops"
        elif "qa" in target_role or "test" in target_role:
            track_key = "qa_specialist"
        elif "core" in target_role or "sde" in target_role or "system" in target_role:
            track_key = "core_sde"
        else:
            track_key = "full_stack"
            
    track = benchmarks_data.get(track_key, list(benchmarks_data.values())[0])
    b_skills_req = track["benchmarks"].get("required_skills", {})
    b_skills_pref = track["benchmarks"].get("preferred_skills", {})
    
    student_skills = student_data.get("skills", {})
    
    # Analyze required skills
    critical_gaps = []
    minor_gaps = []
    mastered_skills = []
    
    total_req_points = 0
    student_req_points = 0
    
    for skill, target_level in b_skills_req.items():
        total_req_points += target_level
        student_level = student_skills.get(skill, 0)
        # Check aliases/subskills (e.g. if React is required, check JavaScript or Web)
        if student_level == 0 and skill == "React" and "JavaScript" in student_skills:
            student_level = max(0, student_skills["JavaScript"] - 2)
            
        student_req_points += min(student_level, target_level)
        deficit = target_level - student_level
        
        item = {
            "skill": skill,
            "target_level": target_level,
            "current_level": student_level,
            "deficit": max(0, deficit),
            "is_required": True
        }
        
        if deficit <= 0:
            item["status"] = "Mastered"
            mastered_skills.append(item)
        elif deficit <= 2:
            item["status"] = "Minor Gap"
            minor_gaps.append(item)
        else:
            item["status"] = "Critical Gap"
            critical_gaps.append(item)
            
    # Preferred skills
    preferred_missing = []
    for skill, target_level in b_skills_pref.items():
        student_level = student_skills.get(skill, 0)
        if student_level < target_level:
            preferred_missing.append({
                "skill": skill,
                "target_level": target_level,
                "current_level": student_level,
                "deficit": target_level - student_level,
                "is_required": False,
                "status": "Recommended Addition"
            })
            
    # Practical and aptitude benchmarks
    student_cgpa = float(student_data.get("cgpa", 0.0))
    target_cgpa = float(track["benchmarks"].get("cgpa", 7.0))
    
    student_dsa = float(student_data.get("aptitude", {}).get("Coding", student_data.get("coding_benchmark", 50.0)))
    target_dsa = float(track["benchmarks"].get("coding_benchmarks", 75.0))
    
    raw_projects = student_data.get("projects", [])
    proj_count = len(raw_projects) if isinstance(raw_projects, list) else int(raw_projects or 0)
    target_projects = int(track["benchmarks"].get("projects_count", 3))
    
    raw_internships = student_data.get("internships", [])
    intern_count = len(raw_internships) if isinstance(raw_internships, list) else int(raw_internships or 0)
    target_internships = int(track["benchmarks"].get("internships_count", 1))
    
    # Calculate Overall Track Readiness (0 - 100%)
    skill_pct = (student_req_points / max(total_req_points, 1)) * 100.0
    cgpa_pct = min(100.0, (student_cgpa / max(target_cgpa, 0.1)) * 100.0)
    dsa_pct = min(100.0, (student_dsa / max(target_dsa, 0.1)) * 100.0)
    proj_pct = min(100.0, (proj_count / max(target_projects, 1)) * 100.0)
    intern_pct = min(100.0, (intern_count / max(target_internships, 1)) * 100.0)
    
    track_fit_score = round(
        0.40 * skill_pct + 0.20 * dsa_pct + 0.15 * cgpa_pct + 0.15 * proj_pct + 0.10 * intern_pct,
        1
    )
    
    return {
        "track_id": track["id"],
        "track_title": track["title"],
        "target_lpa_range": track["target_lpa_range"],
        "track_readiness_score": track_fit_score,
        "critical_gaps": critical_gaps,
        "minor_gaps": minor_gaps,
        "mastered_skills": mastered_skills,
        "preferred_missing": preferred_missing,
        "metrics_comparison": {
            "cgpa": {"current": student_cgpa, "target": target_cgpa, "met": student_cgpa >= target_cgpa},
            "coding_aptitude": {"current": student_dsa, "target": target_dsa, "met": student_dsa >= target_dsa},
            "projects": {"current": proj_count, "target": target_projects, "met": proj_count >= target_projects},
            "internships": {"current": intern_count, "target": target_internships, "met": intern_count >= target_internships}
        }
    }
