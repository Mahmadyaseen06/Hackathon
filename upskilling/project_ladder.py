"""
Skill-Level-Based Progressive Project Ladder
Suggests hands-on projects starting from foundational CLI tools
and progressing systematically to distributed, production-grade systems.
"""

from __future__ import annotations
from typing import Dict, Any, List

PROJECT_LADDER = {
    "beginner": {
        "tier": "Level 1: Beginner Foundation",
        "description": "Strengthens variables, control flow, functions, and file I/O.",
        "projects": [
            {
                "name": "Smart Multi-Mode Calculator",
                "concepts": ["Functions", "Conditionals", "Error Handling"],
                "duration": "1 week",
                "difficulty": "Beginner",
                "deliverable": "Command-line scientific calculator handling edge cases and history logging."
            },
            {
                "name": "Task & Study Plan Manager (CLI)",
                "concepts": ["Lists/Dictionaries", "JSON / File I/O", "Date Math"],
                "duration": "1.5 weeks",
                "difficulty": "Beginner",
                "deliverable": "Interactive CLI tool to schedule study tasks and track completion status."
            },
            {
                "name": "Password Strength Evaluator & Generator",
                "concepts": ["Regular Expressions", "Random Generation", "String Manipulation"],
                "duration": "1 week",
                "difficulty": "Beginner",
                "deliverable": "Security audit tool calculating entropy and generating strong hashes."
            }
        ]
    },
    "intermediate": {
        "tier": "Level 2: Intermediate Full-Stack / API",
        "description": "Applies REST APIs, database persistence, asynchronous calls, and frontend state.",
        "projects": [
            {
                "name": "Weather & Air Quality Dashboard",
                "concepts": ["External REST APIs", "Async HTTP Requests", "Interactive Charts"],
                "duration": "2 weeks",
                "difficulty": "Intermediate",
                "deliverable": "Full-stack dashboard visualizing 7-day forecasts and air quality trends."
            },
            {
                "name": "Personal Budget & Expense Tracker",
                "concepts": ["SQL Databases", "CRUD Operations", "Data Aggregation"],
                "duration": "2.5 weeks",
                "difficulty": "Intermediate",
                "deliverable": "Web app with monthly expenditure categories, charts, and CSV report export."
            },
            {
                "name": "Automated Web Data Scraper & Alert System",
                "concepts": ["BeautifulSoup / Selenium", "Cron Jobs", "Email/Webhook Notifications"],
                "duration": "2 weeks",
                "difficulty": "Intermediate",
                "deliverable": "Background service tracking price drops or internship postings with alerts."
            }
        ]
    },
    "advanced": {
        "tier": "Level 3: Advanced Production & Distributed Systems",
        "description": "Enterprise-grade architectures, machine learning pipelines, concurrency, and cloud deployment.",
        "projects": [
            {
                "name": "Collaborative Real-Time Workspace",
                "concepts": ["WebSockets", "Redis Pub/Sub", "Docker Containers", "JWT Auth"],
                "duration": "4 weeks",
                "difficulty": "Advanced",
                "deliverable": "Multi-user live document editing with room-based WebSocket syncing."
            },
            {
                "name": "AI-Powered Content Recommendation Engine",
                "concepts": ["Cosine Similarity", "Vector Embeddings", "Pandas", "FastAPI"],
                "duration": "3.5 weeks",
                "difficulty": "Advanced",
                "deliverable": "Personalized content discovery API serving item recommendations in <20ms."
            },
            {
                "name": "High-Throughput Distributed Task Queue",
                "concepts": ["Message Queues (RabbitMQ/Kafka)", "Worker Pools", "Retry Exponential Backoff"],
                "duration": "4 weeks",
                "difficulty": "Advanced",
                "deliverable": "Resilient asynchronous job execution platform with live metrics dashboard."
            }
        ]
    }
}

def get_project_recommendations(student_skills: Dict[str, Any], skill_gaps: List[str]) -> List[Dict[str, Any]]:
    """Determine appropriate ladder tier based on coding and programming proficiencies."""
    prog_level = float(student_skills.get("DSA", student_skills.get("Python", student_skills.get("Java", 5.0))))
    
    if prog_level < 4.5:
        tier_key = "beginner"
    elif prog_level < 7.5:
        tier_key = "intermediate"
    else:
        tier_key = "advanced"
        
    tier_data = PROJECT_LADDER[tier_key]
    return {
        "tier_name": tier_data["tier"],
        "description": tier_data["description"],
        "projects": tier_data["projects"]
    }
