"""
Bridges the Job Intelligence module with the upskilling roadmap & content engines.
"""

from __future__ import annotations
from typing import List, Dict, Any
from .models import MatchResult, Priority
from upskilling.roadmap_generator import generate_personalized_roadmap
from upskilling.content_recommender import get_content_recommendations

def enrich_match_with_roadmap(m: MatchResult, target_track: str = "Full-Stack Developer", target_lpa: float = 12.0) -> MatchResult:
    missing = [g.skill for g in m.skill_gap_priority if g.priority in (Priority.CRITICAL, Priority.HIGH)]
    if not missing:
        m.recommended_actions = ["All core required skills met! Focus on system design mock interviews."]
        return m
        
    roadmap = generate_personalized_roadmap(
        student_data={},
        missing_skills=missing,
        target_role=target_track,
        target_lpa=target_lpa
    )
    
    actions = []
    for week in roadmap.get("weeks", [])[:4]:
        actions.append(f"Week {week['week']}: {week['title']} ({week['time_estimate']})")
        
    m.recommended_actions = actions
    return m
