"""
Company-specific interview question banks with role-specific and skill-calibrated questions.
Each company has: intro questions, technical questions (by skill), HR/behavioral questions.
"""

COMPANY_PROFILES = {
    "TCS": {
        "name": "Tata Consultancy Services (TCS NQT)",
        "style": "structured",
        "focus": "aptitude-heavy, basic coding, core CS fundamentals",
        "tone": "formal and systematic",
        "interviewer_persona": "I am your TCS NQT interviewer. TCS values structured thinking, communication, and fundamental CS knowledge. I will ask you a mix of technical, aptitude, and behavioral questions. Please answer clearly and concisely.",
        "rounds": ["Technical Round", "Managerial Round", "HR Round"],
        "intro_questions": [
            "Tell me about yourself and why you want to join TCS.",
            "What do you know about TCS and its services?",
            "Where do you see yourself in 5 years?"
        ],
        "skill_questions": {
            "Python": [
                "What is the difference between a list and a tuple in Python?",
                "Explain how Python's garbage collection works.",
                "Write a function to find the factorial of a number using recursion.",
                "What are Python decorators? Give a real-world example.",
                "Explain the difference between *args and **kwargs."
            ],
            "Java": [
                "Explain the concept of OOP with an example from your project.",
                "What is the difference between abstract class and interface in Java?",
                "Explain how HashMap works internally.",
                "What is the difference between checked and unchecked exceptions?",
                "How does Java handle multithreading?"
            ],
            "SQL": [
                "Write a query to find the second highest salary from an employee table.",
                "What is the difference between INNER JOIN and LEFT JOIN?",
                "Explain normalization and its types.",
                "What is an index in SQL? When would you use it?",
                "Difference between DELETE, TRUNCATE and DROP?"
            ],
            "DSA": [
                "Explain the time complexity of binary search.",
                "What is a stack? Give a real-life example.",
                "Reverse a linked list — walk me through your approach.",
                "What is the difference between BFS and DFS?",
                "How would you detect a cycle in a linked list?"
            ],
            "C": [
                "What is a pointer? How is it different from a variable?",
                "Explain the difference between malloc() and calloc().",
                "What is a segmentation fault and what causes it?",
                "Explain pass by value vs pass by reference.",
                "What are the storage classes in C?"
            ],
            "default": [
                "Explain a technical project you worked on recently.",
                "What programming languages are you most comfortable with and why?",
                "How do you approach debugging a problem you've never seen before?",
                "Explain one data structure and a problem where you applied it.",
                "What is the difference between compiler and interpreter?"
            ]
        },
        "hr_questions": [
            "Are you willing to relocate to any city across India?",
            "How do you handle working under tight deadlines?",
            "Describe a situation where you worked in a team and faced a conflict.",
            "What are your strengths and weaknesses?",
            "Why should TCS hire you over other candidates?"
        ]
    },
    "Google": {
        "name": "Google SDE Interview",
        "style": "rigorous",
        "focus": "algorithms, system design, problem-solving, scalability",
        "tone": "intellectually challenging and collaborative",
        "interviewer_persona": "I am your Google SDE interviewer. At Google, we care deeply about algorithmic thinking, problem decomposition, and scalable design. I will push you to think through edge cases, optimize solutions, and explain your reasoning clearly. Think out loud — I want to follow your thought process.",
        "rounds": ["Phone Screen", "Coding Round 1", "Coding Round 2", "System Design", "Behavioral/Googleyness"],
        "intro_questions": [
            "Walk me through the most technically challenging project you've built.",
            "Tell me about a time you disagreed with a technical decision and how you handled it."
        ],
        "skill_questions": {
            "Python": [
                "Given an array, find two numbers that sum to a target. What's the most efficient approach?",
                "Implement a LRU Cache. Explain your data structure choices.",
                "Given a binary tree, return the level-order traversal.",
                "Write a function to merge K sorted lists.",
                "Explain Python's GIL. How does it affect multithreading?"
            ],
            "C++": [
                "Implement a thread-safe singleton pattern.",
                "What is RAII? Give an example.",
                "Explain virtual functions and vtables.",
                "When would you use std::move and why?",
                "How would you implement your own shared_ptr?"
            ],
            "DSA": [
                "Find the longest common subsequence of two strings. What's the time complexity?",
                "Design an algorithm to serialize and deserialize a binary tree.",
                "Given a matrix, find the number of islands. Walk me through your solution.",
                "Implement Dijkstra's algorithm. Where would you use it?",
                "How would you find the kth largest element in an unsorted array?"
            ],
            "System Design": [
                "How would you design YouTube's video upload and streaming service?",
                "Design a URL shortener like bit.ly. What are the key components?",
                "How would you design a distributed cache?",
                "How does Google Search autocomplete work at scale?",
                "Design a notification system that handles 10 million users."
            ],
            "Machine Learning": [
                "How would you handle class imbalance in a binary classification problem?",
                "Explain the bias-variance tradeoff.",
                "How does backpropagation work in a neural network?",
                "When would you use Random Forest vs Gradient Boosting?",
                "How would you evaluate a recommendation system?"
            ],
            "default": [
                "Given a string, find the longest substring without repeating characters.",
                "How would you check if a binary tree is balanced?",
                "Explain how HashMap resolves collisions.",
                "What's the difference between process and thread?",
                "How would you design a parking lot system?"
            ]
        },
        "hr_questions": [
            "Tell me about a time you had to make a decision with incomplete information.",
            "Describe your proudest technical achievement and why.",
            "How do you keep yourself updated with new technologies?",
            "Give an example of when you went above and beyond for a project.",
            "Tell me about a failure and what you learned from it."
        ]
    },
    "Amazon": {
        "name": "Amazon SDE Interview",
        "style": "leadership-principles",
        "focus": "STAR method behavioral + coding + system design",
        "tone": "customer-obsessed and outcome-focused",
        "interviewer_persona": "I am your Amazon SDE interviewer. Amazon's interviews are built around our 16 Leadership Principles — every answer should show how you embody them. I will ask coding questions AND behavioral questions. Use the STAR method: Situation, Task, Action, Result. Be specific with numbers and outcomes.",
        "rounds": ["Online Assessment", "Technical Phone Screen", "Loop (4-5 interviews)"],
        "intro_questions": [
            "Tell me about yourself — focus on your biggest technical achievement.",
            "Tell me about a time you had to deliver something under extreme time pressure."
        ],
        "skill_questions": {
            "Python": [
                "Given a list of intervals, merge all overlapping intervals.",
                "Implement a producer-consumer pattern using Python threading.",
                "Write code to find the longest palindromic substring.",
                "How would you handle millions of file reads efficiently in Python?",
                "Implement a trie data structure for autocomplete."
            ],
            "Java": [
                "Implement a thread-safe bounded blocking queue.",
                "How does Java's ConcurrentHashMap differ from Hashtable?",
                "Explain Java's memory model and garbage collection.",
                "Implement the Observer pattern in Java.",
                "How would you design an order processing system in Java?"
            ],
            "DSA": [
                "Given a binary tree, find the maximum path sum.",
                "Implement a stack that supports push, pop, and getMin in O(1).",
                "Find all permutations of a string.",
                "Given a sorted rotated array, find an element. What's the time complexity?",
                "Design a data structure that supports insert, delete, and getRandom in O(1)."
            ],
            "System Design": [
                "Design Amazon's shopping cart system.",
                "How would you design Amazon's recommendation engine?",
                "Design a distributed messaging system like SQS.",
                "How would you handle millions of concurrent orders during a flash sale?",
                "Design Amazon's order tracking system."
            ],
            "default": [
                "Explain a project where you had to balance speed and quality.",
                "Given an array of stock prices, find the maximum profit.",
                "How would you design a database schema for an e-commerce platform?",
                "Explain the CAP theorem.",
                "How would you build a real-time notification system?"
            ]
        },
        "hr_questions": [
            "Tell me about a time you disagreed with your manager. What did you do?",
            "Describe a situation where you had to learn something new very quickly.",
            "Give an example of when you took ownership of a project beyond your role.",
            "Tell me about a time you made a mistake. How did you fix it?",
            "How do you prioritize when you have multiple competing deadlines?"
        ]
    },
    "Microsoft": [
        "Microsoft SDE Interview",
        {
            "name": "Microsoft SDE Interview",
            "style": "collaborative",
            "focus": "problem-solving, OOP design, system design, growth mindset",
            "tone": "growth-minded and collaborative",
            "interviewer_persona": "I am your Microsoft SDE interviewer. Microsoft values growth mindset, collaboration, and clean problem-solving. I will start with coding questions and move toward design and behavioral questions. Think out loud. I am here to help if you get stuck — just ask for hints.",
            "rounds": ["Online Assessment", "Technical Phone Screen", "Design Round", "Behavioral Round"],
            "intro_questions": [
                "Tell me about a technical project you're proud of.",
                "Walk me through your problem-solving process when you face a bug you can't immediately solve."
            ],
            "skill_questions": {
                "Python": [
                    "How would you implement Python's built-in `sorted()` function from scratch?",
                    "Explain generators and lazy evaluation in Python with an example.",
                    "Write a decorator that measures execution time of a function.",
                    "How would you handle concurrency in a Python web server?",
                    "Explain Python's memory management for large datasets."
                ],
                "C++": [
                    "Implement a generic stack in C++ using templates.",
                    "Explain the Rule of Three/Five in C++.",
                    "How does C++ handle multiple inheritance? What is the diamond problem?",
                    "What are smart pointers? When would you use each type?",
                    "Implement a simple event-driven system in C++."
                ],
                "DSA": [
                    "Given a graph, find the shortest path between two nodes.",
                    "Implement a priority queue using a heap.",
                    "How would you find all anagrams of a word in a document?",
                    "Explain dynamic programming with a real problem.",
                    "Design an algorithm to detect a palindrome in a stream of characters."
                ],
                "System Design": [
                    "Design Microsoft Teams' real-time messaging system.",
                    "How would you design OneDrive's file sync system?",
                    "Design an autocomplete feature for a search engine.",
                    "How would you build a CI/CD pipeline architecture?",
                    "Design a rate limiting system for an API."
                ],
                "default": [
                    "Reverse words in a sentence without using built-in split functions.",
                    "How would you find duplicates in an array in O(n) time?",
                    "Explain the SOLID principles with examples.",
                    "What is dependency injection and why is it useful?",
                    "How would you design a library management system?"
                ]
            },
            "hr_questions": [
                "Tell me about a time you helped a teammate who was struggling.",
                "Describe your approach to learning a new technology you've never used.",
                "How do you handle feedback that you disagree with?",
                "Tell me about a project where you had to collaborate across teams.",
                "What motivates you to do your best work?"
            ]
        }
    ],
    "Infosys": {
        "name": "Infosys Campus Interview",
        "style": "structured-basic",
        "focus": "core CS fundamentals, communication, aptitude, trainability",
        "tone": "encouraging but thorough",
        "interviewer_persona": "I am your Infosys campus interviewer. Infosys values core CS fundamentals, communication skills, and the ability to learn quickly. My questions will cover DBMS, OS, networking, basic programming, and behavioral scenarios. Please answer clearly.",
        "rounds": ["Online Test", "Technical Interview", "HR Interview"],
        "intro_questions": [
            "Tell me about yourself and your background.",
            "Why do you want to join Infosys?",
            "What are your technical strengths?"
        ],
        "skill_questions": {
            "Python": [
                "What is the difference between a class and an object?",
                "Explain list comprehensions in Python.",
                "What is the purpose of the `__init__` method?",
                "How do you handle exceptions in Python?",
                "What is the difference between shallow copy and deep copy?"
            ],
            "SQL": [
                "What is a primary key vs foreign key?",
                "Explain ACID properties.",
                "Write a query to count employees department-wise.",
                "What is a stored procedure?",
                "Explain the difference between OLTP and OLAP."
            ],
            "DSA": [
                "What is the difference between array and linked list?",
                "Explain sorting algorithms you know and their complexities.",
                "What is a hash table and how does it work?",
                "Explain recursion with a simple example.",
                "What is the time complexity of binary search?"
            ],
            "Operating Systems": [
                "What is a process vs thread?",
                "Explain deadlock and its conditions.",
                "What is virtual memory?",
                "What is a semaphore?",
                "Explain paging vs segmentation."
            ],
            "Networking": [
                "What is the OSI model?",
                "Explain TCP vs UDP.",
                "What is DNS and how does it work?",
                "What is an IP address? Difference between IPv4 and IPv6.",
                "What is HTTP vs HTTPS?"
            ],
            "default": [
                "Explain the concept of OOP with a real-life example.",
                "What is the difference between compiled and interpreted languages?",
                "How does the internet work at a high level?",
                "What is version control and why is it important?",
                "Explain what happens when you type a URL in a browser."
            ]
        },
        "hr_questions": [
            "Are you comfortable with the Infosys service model?",
            "How do you handle working in a large team?",
            "Tell me about a time you met a tight deadline.",
            "What do you do to keep your technical skills sharp?",
            "Where do you see yourself after 2 years at Infosys?"
        ]
    },
    "Wipro": {
        "name": "Wipro WILP / Elite Campus Interview",
        "style": "assessment-focused",
        "focus": "coding aptitude, basic algorithms, problem-solving speed",
        "tone": "direct and efficiency-focused",
        "interviewer_persona": "I am your Wipro technical interviewer. Wipro evaluates coding speed, correctness, and basic software engineering fundamentals. My questions will test your ability to write clean, working code quickly. Focus on correctness first, then optimization.",
        "rounds": ["Online Aptitude Test", "Technical Interview", "HR Interview"],
        "intro_questions": [
            "Briefly introduce yourself — keep it under 2 minutes.",
            "What's the most interesting program you've written?"
        ],
        "skill_questions": {
            "Python": [
                "Write a program to check if a string is a palindrome.",
                "Write a function to find all prime numbers up to N.",
                "How would you reverse a list without using built-in reverse?",
                "Write code to count the frequency of each character in a string.",
                "Explain what happens when you do list1 = list2 in Python."
            ],
            "Java": [
                "Write a Java program to implement a basic stack using arrays.",
                "What is the output of this code: System.out.println(1+2+\"3\"); Explain why.",
                "How do you iterate over a HashMap in Java?",
                "What is the difference between == and .equals() in Java?",
                "Write code to find the largest element in an array."
            ],
            "SQL": [
                "Write a query to find all students who scored above 80.",
                "What is the difference between WHERE and HAVING clause?",
                "How do you remove duplicate rows from a table?",
                "Write a JOIN query between two tables of your choice.",
                "What is a view in SQL?"
            ],
            "DSA": [
                "Write code to check if two strings are anagrams.",
                "How would you find the missing number in an array 1 to N?",
                "Write code to reverse a linked list.",
                "What is the difference between stack and queue?",
                "Write code to find the maximum element in an unsorted array."
            ],
            "default": [
                "Write a program to print the Fibonacci series up to 10 terms.",
                "Explain the difference between procedural and object-oriented programming.",
                "What are the basic operations on an array?",
                "Write a function to swap two numbers without a third variable.",
                "What is recursion? Write a simple recursive function."
            ]
        },
        "hr_questions": [
            "Are you open to working in shifts?",
            "Tell me about your teamwork experience.",
            "How quickly can you adapt to a new technology?",
            "What do you do when you don't understand a task assigned to you?",
            "Why Wipro over other companies?"
        ]
    }
}

# Fix Microsoft entry (it was accidentally set to a list)
COMPANY_PROFILES["Microsoft"] = {
    "name": "Microsoft SDE Interview",
    "style": "collaborative",
    "focus": "problem-solving, OOP design, system design, growth mindset",
    "tone": "growth-minded and collaborative",
    "interviewer_persona": "I am your Microsoft SDE interviewer. Microsoft values growth mindset, collaboration, and clean problem-solving. I will start with coding questions and move toward design and behavioral questions. Think out loud. I am here to help if you get stuck — just ask for hints.",
    "rounds": ["Online Assessment", "Technical Phone Screen", "Design Round", "Behavioral Round"],
    "intro_questions": [
        "Tell me about a technical project you're proud of.",
        "Walk me through your problem-solving process when you face a bug you can't immediately solve."
    ],
    "skill_questions": {
        "Python": [
            "How would you implement Python's built-in sorted() from scratch?",
            "Explain generators and lazy evaluation in Python with an example.",
            "Write a decorator that measures execution time of a function.",
            "How would you handle concurrency in a Python web server?",
            "Explain Python's memory management for large datasets."
        ],
        "C++": [
            "Implement a generic stack in C++ using templates.",
            "Explain the Rule of Three/Five in C++.",
            "How does C++ handle multiple inheritance? What is the diamond problem?",
            "What are smart pointers? When would you use each type?",
            "Implement a simple event-driven system in C++."
        ],
        "DSA": [
            "Given a graph, find the shortest path between two nodes.",
            "Implement a priority queue using a heap.",
            "How would you find all anagrams of a word in a document?",
            "Explain dynamic programming with a real problem.",
            "Design an algorithm to detect a palindrome in a stream of characters."
        ],
        "System Design": [
            "Design Microsoft Teams' real-time messaging system.",
            "How would you design OneDrive's file sync system?",
            "Design an autocomplete feature for a search engine.",
            "How would you build a CI/CD pipeline architecture?",
            "Design a rate limiting system for an API."
        ],
        "default": [
            "Reverse words in a sentence without using built-in split functions.",
            "How would you find duplicates in an array in O(n) time?",
            "Explain the SOLID principles with examples.",
            "What is dependency injection and why is it useful?",
            "How would you design a library management system?"
        ]
    },
    "hr_questions": [
        "Tell me about a time you helped a teammate who was struggling.",
        "Describe your approach to learning a new technology.",
        "How do you handle feedback that you disagree with?",
        "Tell me about a project where you had to collaborate across teams.",
        "What motivates you to do your best work?"
    ]
}


CODING_CHALLENGES = [
    {
        "type": "technical",
        "question": "Two Sum: Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. Each input has exactly one solution.",
        "topic": "Python / DSA",
        "difficulty": "Easy",
        "claimed_level": 6,
        "examples": [
            {"input": "target = 9, nums = [2, 7, 11, 15]", "output": "[0, 1]", "explanation": "nums[0] + nums[1] == 9"}
        ],
        "constraints": ["2 <= nums.length <= 10^4", "-10^9 <= nums[i] <= 10^9", "O(n) time complexity required"],
        "starter_code": """import sys

def two_sum(nums, target):
    # Complete this function using a dictionary
    seen = {}
    for i, num in enumerate(nums):
        diff = target - num
        if diff in seen:
            return [seen[diff], i]
        seen[num] = i
    return []

if __name__ == '__main__':
    lines = sys.stdin.read().strip().split('\\n')
    if len(lines) >= 2:
        t = int(lines[0])
        arr = [int(x) for x in lines[1].split()]
        print(two_sum(arr, t))
""",
        "test_cases": [
            {"input": "9\\n2 7 11 15", "expected_output": "[0, 1]"},
            {"input": "6\\n3 2 4", "expected_output": "[1, 2]"}
        ]
    },
    {
        "type": "technical",
        "question": "Valid Palindrome: A phrase is a palindrome if, after converting all uppercase letters into lowercase letters and removing all non-alphanumeric characters, it reads the same forward and backward.",
        "topic": "Python / Strings",
        "difficulty": "Easy",
        "claimed_level": 5,
        "examples": [
            {"input": "s = 'A man, a plan, a canal: Panama'", "output": "true", "explanation": "'amanaplanacanalpanama' is a palindrome."}
        ],
        "constraints": ["1 <= s.length <= 2 * 10^5", "Return true or false"],
        "starter_code": """import sys

def is_palindrome(s):
    # Complete this function
    cleaned = [c.lower() for c in s if c.isalnum()]
    return cleaned == cleaned[::-1]

if __name__ == '__main__':
    inp = sys.stdin.read().strip()
    print("true" if is_palindrome(inp) else "false")
""",
        "test_cases": [
            {"input": "A man, a plan, a canal: Panama", "expected_output": "true"},
            {"input": "race a car", "expected_output": "false"}
        ]
    },
    {
        "type": "technical",
        "question": "Maximum Subarray (Kadane's Algorithm): Given an integer array nums, find the subarray with the largest sum and return its sum in O(n) time.",
        "topic": "DSA / Algorithms",
        "difficulty": "Medium",
        "claimed_level": 7,
        "examples": [
            {"input": "nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]", "output": "6", "explanation": "[4, -1, 2, 1] has largest sum 6."}
        ],
        "constraints": ["1 <= nums.length <= 10^5", "-10^4 <= nums[i] <= 10^4", "O(n) time complexity"],
        "starter_code": """import sys

def max_subarray(nums):
    # Implement Kadane's Algorithm
    max_so_far = nums[0]
    curr_max = nums[0]
    for x in nums[1:]:
        curr_max = max(x, curr_max + x)
        max_so_far = max(max_so_far, curr_max)
    return max_so_far

if __name__ == '__main__':
    lines = sys.stdin.read().strip().split('\\n')
    if lines and lines[0]:
        arr = [int(x) for x in lines[0].split()]
        print(max_subarray(arr))
""",
        "test_cases": [
            {"input": "-2 1 -3 4 -1 2 1 -5 4", "expected_output": "6"},
            {"input": "1", "expected_output": "1"},
            {"input": "5 4 -1 7 8", "expected_output": "23"}
        ]
    }
]


def get_calibrated_questions(company: str, student_skills: dict, num_questions: int = 7) -> list[dict]:
    """
    Select and calibrate interview questions based on:
    1. Company interview style
    2. Student's claimed skill levels (harder questions for higher claimed proficiency)
    3. Number of questions requested
    4. Includes real HackerRank-style live coding challenges with test cases
    """
    import random
    profile = COMPANY_PROFILES.get(company)
    if not profile:
        profile = COMPANY_PROFILES["TCS"]

    questions = []
    skill_qs = profile.get("skill_questions", {})

    # Always start with 1 intro question
    intro = random.choice(profile.get("intro_questions", ["Tell me about yourself."]))
    questions.append({"type": "intro", "question": intro, "topic": "Introduction", "difficulty": "Easy"})

    # Always include 1-2 practical coding challenges with test cases
    coding_challenge = random.choice(CODING_CHALLENGES)
    questions.append(coding_challenge.copy())

    # Pick technical questions calibrated to the student's claimed skills
    top_skills = sorted(student_skills.items(), key=lambda x: x[1], reverse=True)[:4]
    tech_count = max(1, num_questions - 3)  # reserve 1 intro + 1 coding + 1 HR

    skill_question_pool = []
    for skill_name, skill_level in top_skills:
        matched_key = next((k for k in skill_qs if k.lower() == skill_name.lower()), None)
        pool = skill_qs.get(matched_key, skill_qs.get("default", []))
        if pool:
            if skill_level >= 8:
                q_set = pool[-3:]
            elif skill_level >= 6:
                q_set = pool[1:4]
            else:
                q_set = pool[:3]
            for q in random.sample(q_set, min(2, len(q_set))):
                skill_question_pool.append({
                    "type": "technical",
                    "question": q,
                    "topic": skill_name,
                    "difficulty": "Hard" if skill_level >= 8 else "Medium" if skill_level >= 6 else "Easy",
                    "claimed_level": skill_level
                })

    if len(skill_question_pool) < tech_count:
        for q in skill_qs.get("default", []):
            skill_question_pool.append({"type": "technical", "question": q, "topic": "General CS", "difficulty": "Medium", "claimed_level": 5})

    random.shuffle(skill_question_pool)
    questions.extend(skill_question_pool[:tech_count])

    # End with 1 HR question
    hr_q = random.choice(profile.get("hr_questions", ["Tell me your strengths and weaknesses."]))
    questions.append({"type": "hr", "question": hr_q, "topic": "Behavioral", "difficulty": "Easy"})

    return questions
