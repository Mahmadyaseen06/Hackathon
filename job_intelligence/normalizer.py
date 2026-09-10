"""
Normalizer for extracting and canonicalizing skills from job descriptions.
"""

from __future__ import annotations
import re
from typing import Iterable, List, Set, Tuple
from .skill_taxonomy import SKILLS, SkillDef

_ALL_PAIRS: List[Tuple[str, SkillDef]] = []
for s in SKILLS:
    for alias in s.aliases:
        _ALL_PAIRS.append((alias.strip(), s))

# Sort by length descending so longer matches (e.g. 'react.js') take precedence over short ones (e.g. 'js')
_ALL_PAIRS.sort(key=lambda x: len(x[0]), reverse=True)

_ALIAS_PATTERNS: List[Tuple[re.Pattern, SkillDef]] = []
for alias_str, sdef in _ALL_PAIRS:
    pat = re.compile(r"(?<![A-Za-z0-9])" + re.escape(alias_str) + r"(?![A-Za-z0-9])", re.IGNORECASE)
    _ALIAS_PATTERNS.append((pat, sdef))

def canonicalize_one(text: str) -> str | None:
    if not text:
        return None
    for pat, sdef in _ALIAS_PATTERNS:
        if pat.search(text):
            return sdef.canonical
    return None

def extract_skills(text: str) -> Set[str]:
    if not text:
        return set()
    found: Set[str] = set()
    for pat, sdef in _ALIAS_PATTERNS:
        if pat.search(text):
            found.add(sdef.canonical)
    return found

def canonicalize_list(items: Iterable[str]) -> List[str]:
    out: List[str] = []
    seen = set()
    for item in items or []:
        c = canonicalize_one(item) or item.strip()
        if c and c not in seen:
            seen.add(c)
            out.append(c)
    return out

_REQ_HEADERS = re.compile(r"(minimum qualifications|required qualifications|requirements|must have|you have|you must have|required skills?)", re.I)
_PREF_HEADERS = re.compile(r"(preferred qualifications|preferred skills?|nice to have|bonus points?|good to have|plus(es)?)", re.I)

def split_required_preferred(description: str) -> Tuple[List[str], List[str]]:
    if not description:
        return [], []
    req_matches = list(_REQ_HEADERS.finditer(description))
    pref_matches = list(_PREF_HEADERS.finditer(description))
    
    req_region = ""
    pref_region = ""
    
    if req_matches:
        start = req_matches[0].start()
        end = pref_matches[0].start() if pref_matches and pref_matches[0].start() > start else len(description)
        req_region = description[start:end]
        
    if pref_matches:
        start = pref_matches[0].start()
        pref_region = description[start:start + 4000]
        
    req_skills = extract_skills(req_region) if req_region else set()
    pref_skills = (extract_skills(pref_region) - req_skills) if pref_region else set()
    
    if not req_skills:
        req_skills = extract_skills(description)
        
    return sorted(req_skills), sorted(pref_skills)
