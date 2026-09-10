"""
Explainable AI (XAI) & Factor Transparency Engine
Computes SHAP feature attributions and translates numerical Shapley values
into plain-English percentage impact factors for students and mentors.
"""

from __future__ import annotations
from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd

FEATURE_DESCRIPTIONS = {
    "cgpa": "Academic CGPA ({value:.2f})",
    "tenth_percentage": "Secondary 10th marks ({value:.1f}%)",
    "twelfth_percentage": "Higher secondary 12th marks ({value:.1f}%)",
    "backlogs_history": "History of past backlogs ({value:.0f})",
    "active_backlogs": "Active uncleared backlogs ({value:.0f})",
    "quantitative_aptitude": "Quantitative aptitude assessment ({value:.0f}/100)",
    "logical_reasoning": "Logical reasoning benchmark ({value:.0f}/100)",
    "coding_benchmark": "Coding & problem-solving benchmark ({value:.0f}/100)",
    "skills_python": "Python programming competency ({value:.0f}/10)",
    "skills_java": "Java programming competency ({value:.0f}/10)",
    "skills_cpp": "C/C++ competency ({value:.0f}/10)",
    "skills_dsa": "Data Structures & Algorithms benchmark ({value:.0f}/10)",
    "skills_sql": "SQL database competency ({value:.0f}/10)",
    "skills_web": "Modern Web / Frontend proficiency ({value:.0f}/10)",
    "skills_cloud": "Cloud / DevOps fundamentals ({value:.0f}/10)",
    "skills_ml": "Data Science / ML proficiency ({value:.0f}/10)",
    "internships": "Completed industry internships ({value:.0f})",
    "projects_count": "Verified practical project portfolio ({value:.0f} projects)",
    "certifications_count": "Industry certifications verified ({value:.0f})",
    "hackathons": "Competitive hackathon participations ({value:.0f})",
    "communication_rating": "Verbal communication rating ({value:.1f}/10)",
    "interview_rating": "Mock interview score ({value:.1f}/10)",
    "is_cs_branch": "Core CS/IT department discipline"
}

def translate_shap_to_factors(
    feature_names: List[str],
    feature_values: np.ndarray,
    shap_values: np.ndarray,
    base_value: float,
    top_k: int = 5
) -> Dict[str, Any]:
    """
    Translates raw SHAP log-odds contributions into percentage impact factors.
    Returns:
      - positive_factors: [{ feature, impact_pct, text, value }]
      - negative_factors: [{ feature, impact_pct, text, value }]
      - waterfall_data: list of components for UI waterfall visualization
    """
    total_abs_shap = np.sum(np.abs(shap_values)) or 1.0
    
    factors = []
    for name, val, shap in zip(feature_names, feature_values, shap_values):
        # Approximate marginal percentage contribution
        # Bound between -30% and +30% for realistic factor communication
        pct = float(np.clip(shap * 35.0, -35.0, 35.0))
        
        desc_tmpl = FEATURE_DESCRIPTIONS.get(name, f"{name} ({{value}})")
        try:
            desc = desc_tmpl.format(value=val)
        except Exception:
            desc = f"{name} ({val})"
            
        factors.append({
            "feature": name,
            "value": float(val),
            "shap_value": float(shap),
            "impact_pct": round(pct, 1),
            "text": f"{'+' if pct > 0 else ''}{pct:.1f}% due to {desc}"
        })
        
    positives = [f for f in factors if f["impact_pct"] > 0]
    negatives = [f for f in factors if f["impact_pct"] < 0]
    
    positives.sort(key=lambda x: x["impact_pct"], reverse=True)
    negatives.sort(key=lambda x: x["impact_pct"]) # most negative first
    
    # Format waterfall data for interactive charts
    waterfall = []
    for f in factors:
        waterfall.append({
            "name": f["feature"].replace("skills_", "skill: ").replace("_", " ").title(),
            "impact": f["impact_pct"],
            "raw_val": f["value"]
        })
    waterfall.sort(key=lambda x: abs(x["impact"]), reverse=True)
    
    return {
        "positive_factors": positives[:top_k],
        "negative_factors": negatives[:top_k],
        "waterfall": waterfall[:10],
        "base_probability": round(float(1.0 / (1.0 + np.exp(-base_value))) * 100.0, 1) if base_value else 50.0
    }
