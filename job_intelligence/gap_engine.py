"""
Aggregate Cross-Job Gap Engine
Calculates widespread missing skills and identifies the Single Most Valuable Next Skill
to learn to unlock the maximum number of eligible roles.
"""

from __future__ import annotations
from collections import Counter
from typing import List, Tuple, Dict, Any
from .models import JobPosting, MatchResult, Priority, MatchCategory

def aggregate_gaps(pairs: List[Tuple[JobPosting, MatchResult]]) -> Dict[str, Any]:
    counter: Counter[str] = Counter()
    weighted_eligible: Counter[str] = Counter()
    
    for j, m in pairs:
        for g in m.skill_gap_priority:
            counter[g.skill] += 1
            if m.eligibility.status in ("eligible", "partially_eligible"):
                weight = {Priority.CRITICAL: 4, Priority.HIGH: 3, Priority.MEDIUM: 2, Priority.LOW: 1}[g.priority]
                weighted_eligible[g.skill] += weight
                
    most_common = counter.most_common(10)
    top_skill, top_score = (None, 0)
    if weighted_eligible:
        top_skill, top_score = weighted_eligible.most_common(1)[0]
        
    return {
        "most_common_missing": [{"skill": s, "jobs": c} for s, c in most_common],
        "most_valuable_next_skill": top_skill,
        "most_valuable_next_skill_score": top_score,
        "most_valuable_reason": (
            f"Learning {top_skill} resolves critical blockers across {top_score} weighted campus target postings"
            if top_skill else "All primary skills well aligned"
        )
    }

def summary_counts(pairs: List[Tuple[JobPosting, MatchResult]]) -> Dict[str, int]:
    best = sum(1 for _, m in pairs if m.category == MatchCategory.BEST_MATCH)
    near = sum(1 for _, m in pairs if m.category == MatchCategory.NEAR_MATCH)
    stretch = sum(1 for _, m in pairs if m.category == MatchCategory.STRETCH)
    return {"total": len(pairs), "best": best, "near": near, "stretch": stretch}
