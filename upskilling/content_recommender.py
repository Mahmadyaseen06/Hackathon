"""
Content Recommender: YouTube Tutorials & NPTEL IIT Courses
Provides curated, high-impact educational resources directly aligned
with diagnosed student skill deficits.
"""

from __future__ import annotations
from typing import Dict, List, Any

YOUTUBE_CATALOG: Dict[str, List[Dict[str, Any]]] = {
    "DSA": [
        {
            "title": "Data Structures & Algorithms in Python / C++ - Full Course",
            "channel": "freeCodeCamp.org",
            "duration": "12 hours",
            "url": "https://www.youtube.com/watch?v=pkYVOmU3MgA",
            "topics": ["Arrays", "Linked Lists", "Trees", "Graphs", "Dynamic Programming"],
            "difficulty": "Beginner to Advanced"
        },
        {
            "title": "NeetCode 150 - Complete LeetCode Coding Interview Prep",
            "channel": "NeetCode",
            "duration": "24 hours",
            "url": "https://www.youtube.com/c/NeetCode",
            "topics": ["Two Pointers", "Sliding Window", "Backtracking", "Heaps"],
            "difficulty": "Interview Ready"
        }
    ],
    "React": [
        {
            "title": "React 19 & Next.js Full Course 2026",
            "channel": "CodeWithHarry",
            "duration": "8 hours",
            "url": "https://www.youtube.com/watch?v=RGKi6LSPDLU",
            "topics": ["Hooks", "State Management", "Server Components", "API Routes"],
            "difficulty": "Intermediate"
        },
        {
            "title": "React JS Crash Course for Beginners",
            "channel": "Traversy Media",
            "duration": "3 hours",
            "url": "https://www.youtube.com/watch?v=w7ejDZ8SWv8",
            "topics": ["JSX", "Components", "Props", "Context API"],
            "difficulty": "Beginner"
        }
    ],
    "Node.js": [
        {
            "title": "Node.js and Express.js - Full Course",
            "channel": "freeCodeCamp.org",
            "duration": "8 hours",
            "url": "https://www.youtube.com/watch?v=Oe421EPjeBE",
            "topics": ["Event Loop", "REST APIs", "Middleware", "Authentication"],
            "difficulty": "Intermediate"
        }
    ],
    "SQL": [
        {
            "title": "SQL Tutorial - Full Database Course for Beginners",
            "channel": "freeCodeCamp.org",
            "duration": "4.5 hours",
            "url": "https://www.youtube.com/watch?v=HXV3zeQKqGY",
            "topics": ["Queries", "Joins", "Aggregations", "Indexing", "Normalization"],
            "difficulty": "Beginner to Intermediate"
        }
    ],
    "Python": [
        {
            "title": "Python for Beginners - Full Course (2026 Edition)",
            "channel": "Programming with Mosh",
            "duration": "6 hours",
            "url": "https://www.youtube.com/watch?v=_uQrJ0TkZlc",
            "topics": ["Variables", "OOP", "Modules", "File Handling"],
            "difficulty": "Beginner"
        }
    ],
    "Machine Learning": [
        {
            "title": "Machine Learning Specialization - Andrew Ng",
            "channel": "DeepLearning.AI",
            "duration": "30 hours",
            "url": "https://www.youtube.com/playlist?list=PLkDaE6sCZn6FNC6YRfRQc_FbeQrF8BwGI",
            "topics": ["Supervised Learning", "Gradient Descent", "Decision Trees", "Regularization"],
            "difficulty": "Intermediate"
        }
    ],
    "Docker": [
        {
            "title": "Docker Tutorial for Beginners [Hands-on]",
            "channel": "TechWorld with Nana",
            "duration": "3 hours",
            "url": "https://www.youtube.com/watch?v=3c-iBn73dDE",
            "topics": ["Containers", "Images", "Docker Compose", "Networking"],
            "difficulty": "Beginner to Intermediate"
        }
    ],
    "AWS": [
        {
            "title": "AWS Certified Cloud Practitioner Training 2026",
            "channel": "freeCodeCamp.org",
            "duration": "14 hours",
            "url": "https://www.youtube.com/watch?v=SOTamWNgDKc",
            "topics": ["EC2", "S3", "IAM", "VPC", "Serverless Lambda"],
            "difficulty": "Certification Ready"
        }
    ],
    "System Design": [
        {
            "title": "System Design for Beginners - Architecture & Patterns",
            "channel": "Gaurav Sen",
            "duration": "5 hours",
            "url": "https://www.youtube.com/c/GauravSensei",
            "topics": ["Load Balancers", "Caching", "Sharding", "CAP Theorem", "Microservices"],
            "difficulty": "Advanced"
        }
    ]
}

NPTEL_CATALOG: Dict[str, List[Dict[str, Any]]] = {
    "DSA": [
        {
            "name": "Data Structures and Algorithms using Java / C++",
            "institution": "IIT Kharagpur",
            "instructor": "Prof. Debasis Samanta",
            "duration_weeks": 12,
            "url": "https://onlinecourses.nptel.ac.in/noc24_cs42/preview",
            "exam_fee": "₹1,000 (Optional IIT Certificate)",
            "impact": "High recruiter recognition across top Indian IT & product firms."
        }
    ],
    "Python": [
        {
            "name": "The Joy of Computing using Python",
            "institution": "IIT Ropar",
            "instructor": "Prof. Sudarshan Iyengar",
            "duration_weeks": 12,
            "url": "https://onlinecourses.nptel.ac.in/noc24_cs57/preview",
            "exam_fee": "₹1,000",
            "impact": "Foundational Python certification from IIT."
        }
    ],
    "Machine Learning": [
        {
            "name": "Introduction to Machine Learning",
            "institution": "IIT Madras",
            "instructor": "Prof. Balaraman Ravindran",
            "duration_weeks": 12,
            "url": "https://onlinecourses.nptel.ac.in/noc24_cs55/preview",
            "exam_fee": "₹1,000",
            "impact": "Industry benchmark course for AI/ML recruitment."
        },
        {
            "name": "Deep Learning",
            "institution": "IIT Ropar & IIT Madras",
            "instructor": "Prof. Mitesh Khapra",
            "duration_weeks": 12,
            "url": "https://onlinecourses.nptel.ac.in/noc24_cs51/preview",
            "exam_fee": "₹1,000",
            "impact": "Covers neural networks, CNNs, RNNs, and Transformers."
        }
    ],
    "Cloud": [
        {
            "name": "Cloud Computing",
            "institution": "IIT Kharagpur",
            "instructor": "Prof. Soumya Kanti Ghosh",
            "duration_weeks": 8,
            "url": "https://onlinecourses.nptel.ac.in/noc24_cs17/preview",
            "exam_fee": "₹1,000",
            "impact": "Recognized by enterprise cloud consulting firms."
        }
    ],
    "SQL": [
        {
            "name": "Database Management System",
            "institution": "IIT Kharagpur",
            "instructor": "Prof. Partha Pratim Das",
            "duration_weeks": 8,
            "url": "https://onlinecourses.nptel.ac.in/noc24_cs21/preview",
            "exam_fee": "₹1,000",
            "impact": "Essential for backend and database administration interviews."
        }
    ],
    "Communication": [
        {
            "name": "Developing Soft Skills and Personality",
            "institution": "IIT Kanpur",
            "instructor": "Prof. T. Ravichandran",
            "duration_weeks": 8,
            "url": "https://onlinecourses.nptel.ac.in/noc24_hs28/preview",
            "exam_fee": "₹1,000",
            "impact": "Improves behavioral interview ratings and presentation fluency."
        }
    ]
}

def get_content_recommendations(missing_skills: List[str]) -> Dict[str, Any]:
    """Fetch matching YouTube videos and NPTEL IIT courses for a list of missing skills."""
    yt_results = []
    nptel_results = []
    
    seen_yt = set()
    seen_nptel = set()
    
    for skill in missing_skills:
        # Match skill in YouTube catalog
        for k, v in YOUTUBE_CATALOG.items():
            if k.lower() in skill.lower() or skill.lower() in k.lower():
                for item in v:
                    if item["title"] not in seen_yt:
                        seen_yt.add(item["title"])
                        yt_results.append({**item, "mapped_skill": skill})
                        
        # Match skill in NPTEL catalog
        for k, v in NPTEL_CATALOG.items():
            if k.lower() in skill.lower() or skill.lower() in k.lower():
                for item in v:
                    if item["name"] not in seen_nptel:
                        seen_nptel.add(item["name"])
                        nptel_results.append({**item, "mapped_skill": skill})
                        
    # Fallback to general DSA / Web if empty
    if not yt_results:
        yt_results.extend([{**x, "mapped_skill": "DSA"} for x in YOUTUBE_CATALOG["DSA"][:2]])
    if not nptel_results:
        nptel_results.extend([{**x, "mapped_skill": "DSA"} for x in NPTEL_CATALOG["DSA"][:1]])
        
    return {
        "youtube_videos": yt_results[:6],
        "nptel_courses": nptel_results[:4]
    }
