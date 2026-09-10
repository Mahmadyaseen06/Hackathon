"""
Canonical skill taxonomy for normalization.
Maps free-text skill tokens and aliases to canonical names.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass(frozen=True)
class SkillDef:
    canonical: str
    category: str
    difficulty: str
    aliases: tuple
    related: tuple = ()
    prerequisites: tuple = ()

SKILLS: List[SkillDef] = [
    # Programming
    SkillDef("Python", "Programming", "beginner", ("python", "python3", "python 3")),
    SkillDef("Java", "Programming", "beginner", ("java", "core java")),
    SkillDef("C++", "Programming", "intermediate", ("c++", "cpp", "c plus plus")),
    SkillDef("C", "Programming", "beginner", (" c ", "c language")),
    SkillDef("JavaScript", "Programming", "beginner", ("javascript", "js", "es6")),
    SkillDef("TypeScript", "Programming", "intermediate", ("typescript", "ts")),
    SkillDef("Go", "Programming", "intermediate", ("golang", "go lang", "go")),
    SkillDef("Rust", "Programming", "advanced", ("rust",)),
    SkillDef("SQL", "Databases", "beginner", ("sql", "sql databases", "structured query language")),
    SkillDef("Bash", "Programming", "beginner", ("bash", "shell scripting", "shell")),
    SkillDef("Kotlin", "Programming", "intermediate", ("kotlin",)),
    # Frameworks
    SkillDef("React", "Frameworks", "intermediate", ("react", "reactjs", "react.js")),
    SkillDef("Next.js", "Frameworks", "intermediate", ("nextjs", "next.js")),
    SkillDef("Node.js", "Frameworks", "intermediate", ("node", "nodejs", "node.js")),
    SkillDef("Django", "Frameworks", "intermediate", ("django",)),
    SkillDef("FastAPI", "Frameworks", "intermediate", ("fastapi", "fast api")),
    SkillDef("Spring Boot", "Frameworks", "advanced", ("spring boot", "springboot", "spring")),
    SkillDef("REST APIs", "Frameworks", "intermediate", ("rest", "rest api", "restful", "rest apis")),
    # Databases
    SkillDef("MySQL", "Databases", "beginner", ("mysql",)),
    SkillDef("PostgreSQL", "Databases", "intermediate", ("postgres", "postgresql")),
    SkillDef("MongoDB", "Databases", "intermediate", ("mongodb", "mongo")),
    SkillDef("Redis", "Databases", "intermediate", ("redis",)),
    # Cloud / DevOps
    SkillDef("AWS", "Cloud", "intermediate", ("aws", "amazon web services")),
    SkillDef("Azure", "Cloud", "intermediate", ("azure", "microsoft azure")),
    SkillDef("Docker", "DevOps", "intermediate", ("docker", "containerization")),
    SkillDef("Kubernetes", "DevOps", "advanced", ("kubernetes", "k8s")),
    SkillDef("CI/CD", "DevOps", "intermediate", ("ci/cd", "cicd", "continuous integration")),
    SkillDef("Linux", "DevOps", "beginner", ("linux", "unix")),
    # Data / AI / ML
    SkillDef("Machine Learning", "Machine Learning", "intermediate", ("machine learning", "ml")),
    SkillDef("Deep Learning", "Machine Learning", "advanced", ("deep learning", "neural networks")),
    SkillDef("PyTorch", "Machine Learning", "advanced", ("pytorch", "torch")),
    SkillDef("TensorFlow", "Machine Learning", "advanced", ("tensorflow", "tf")),
    SkillDef("Pandas", "Data Science", "beginner", ("pandas",)),
    SkillDef("NumPy", "Data Science", "beginner", ("numpy",)),
    SkillDef("Statistics", "Data Science", "intermediate", ("statistics", "stats")),
    SkillDef("Data Visualization", "Data Science", "beginner", ("data visualization", "power bi", "tableau")),
    # CS Fundamentals & Testing
    SkillDef("DSA", "CS Fundamentals", "intermediate", ("data structures", "algorithms", "dsa")),
    SkillDef("System Design", "CS Fundamentals", "advanced", ("system design", "distributed systems", "hld", "lld")),
    SkillDef("Operating Systems", "CS Fundamentals", "intermediate", ("operating systems", "os")),
    SkillDef("Computer Networks", "CS Fundamentals", "intermediate", ("computer networks", "networking")),
    SkillDef("DBMS", "CS Fundamentals", "intermediate", ("dbms", "database management")),
    SkillDef("OOP", "CS Fundamentals", "beginner", ("oop", "object oriented", "oops")),
    SkillDef("Selenium", "Testing", "intermediate", ("selenium",)),
    SkillDef("Automation Testing", "Testing", "intermediate", ("automation testing", "test automation")),
    SkillDef("Git", "Tools", "beginner", ("git", "version control", "github")),
    SkillDef("Communication", "Soft Skills", "beginner", ("communication", "verbal communication")),
    SkillDef("Problem Solving", "Soft Skills", "beginner", ("problem solving", "analytical thinking"))
]

_CANONICAL_INDEX: Dict[str, SkillDef] = {s.canonical.lower(): s for s in SKILLS}

def get_skill(canonical: str) -> Optional[SkillDef]:
    return _CANONICAL_INDEX.get(canonical.lower())

def all_canonical() -> List[str]:
    return [s.canonical for s in SKILLS]
