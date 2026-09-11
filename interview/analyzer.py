"""
AI Interview Analyzer — STRICT MODE using Ollama (llama3.2:3b local).

Design principle: NEVER inflate scores. A student who claims Python level 8
but gives a surface answer gets a 3/10 and "Overstated" verdict.

Analyzes:
- Technical accuracy (is the answer factually correct?)
- Depth vs claimed level (did they actually demonstrate that skill?)
- Communication clarity (grammar, structure, confidence, filler words)
- Speaking patterns (from transcript: hesitation, vagueness, buzzword padding)
- Claim vs reality gap
"""

import json
import re
import httpx
import asyncio
from typing import Optional

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2:3b"

# ──────────────────────────────────────────────────────────────────────────────
# STRICT SCORING RUBRIC (used in prompt + post-processing validation)
# ──────────────────────────────────────────────────────────────────────────────
STRICT_RUBRIC = """
ABSOLUTE SCORING RULES — DO NOT DEVIATE:

10: Perfect answer. Complete, accurate, includes edge cases, real examples. Rare.
9:  Excellent. Covers all key points with confidence and precision.
8:  Good. Minor gaps but demonstrates solid understanding.
7:  Decent. Covers most key points but lacks depth or misses one concept.
6:  Average. Understands the basics but significant gaps.
5:  Partial. Gets the surface but misses the core mechanism or use cases.
4:  Weak. Knows the term but cannot explain it properly.
3:  Very weak. Mostly wrong, vague, or confused.
2:  Almost empty. One or two correct words with no substance.
1:  Barely relevant. Doesn't really answer the question.
0:  "I don't know", blank, completely off-topic, or gibberish.

CLAIM VERIFICATION:
- If student claims 8/10 in Python but gives a 4/10 answer → "Overstated", mark red_flags=true
- If student claims 5/10 and gives a 5/10 answer → "Verified"
- Never give higher score just because the student seems nice or tried hard
- Buzzwords without substance = score -2 from where the answer would otherwise land
- Vague generalities without examples = score -1

COMMUNICATION SCORING (separate from technical):
- Check grammar, sentence structure, clarity of thought
- Check if answer is organized or rambling
- Check for filler phrases: "basically", "like I said", "you know", "kind of", "sort of" = -1
- Short, clear, precise answers score HIGHER than long rambling ones
"""

# ──────────────────────────────────────────────────────────────────────────────
# COMMUNICATION PATTERN DETECTOR (rule-based, runs first)
# ──────────────────────────────────────────────────────────────────────────────
FILLER_WORDS = [
    "basically", "you know", "kind of", "sort of", "like i said", "um", "uh",
    "i think maybe", "i guess", "not sure but", "i believe maybe", "probably like",
    "i mean", "and stuff", "et cetera", "etc etc"
]

def _analyze_communication_patterns(text: str) -> dict:
    """
    Rule-based communication pattern analysis from transcript.
    Returns communication quality metrics.
    """
    text_lower = text.lower()
    words = text.split()
    word_count = len(words)
    sentence_count = max(1, text.count('.') + text.count('!') + text.count('?'))

    # Filler word count
    filler_count = sum(1 for f in FILLER_WORDS if f in text_lower)

    # Check for vagueness markers
    vague_phrases = ["it does something", "basically works", "i think it", "not sure exactly",
                     "something like that", "and so on", "etc", "similar stuff"]
    vague_count = sum(1 for v in vague_phrases if v in text_lower)

    # Check for concrete indicators
    concrete_markers = ["for example", "for instance", "specifically", "in python",
                       "when i", "i implemented", "in my project", "the syntax is",
                       "the time complexity", "the reason is", "this means that"]
    concrete_count = sum(1 for c in concrete_markers if c in text_lower)

    # Communication score (out of 10)
    base_comm = 5
    if word_count < 10:
        base_comm = 2  # too short
    elif word_count > 20:
        base_comm += 1  # answered properly
    if word_count > 50:
        base_comm += 1  # detailed

    base_comm -= min(3, filler_count)      # penalize fillers
    base_comm -= min(2, vague_count)        # penalize vagueness
    base_comm += min(2, concrete_count)     # reward specificity

    comm_score = max(1, min(10, base_comm))

    # Avg words per sentence
    avg_sentence_length = word_count / sentence_count

    return {
        "word_count": word_count,
        "filler_words_detected": filler_count,
        "vague_phrases_detected": vague_count,
        "concrete_examples_detected": concrete_count,
        "communication_score": comm_score,
        "avg_sentence_length": round(avg_sentence_length, 1),
        "verdict_hint": (
            "Clear and structured" if comm_score >= 7 else
            "Needs improvement" if comm_score >= 5 else
            "Poor communication"
        )
    }


async def _ollama_chat(prompt: str, max_tokens: int = 500) -> str:
    """Send a prompt to Ollama and get a response."""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.05,  # Very low — we want deterministic strict judgment
            "num_predict": max_tokens,
            "top_p": 0.8,
            "repeat_penalty": 1.1
        }
    }
    async with httpx.AsyncClient(timeout=90.0) as client:
        response = await client.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload)
        response.raise_for_status()
        return response.json().get("response", "").strip()


async def _is_ollama_running() -> bool:
    """Check if Ollama is running and model is available."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(f"{OLLAMA_BASE_URL}/api/version")
            return r.status_code == 200
    except Exception:
        return False


def _extract_json_from_response(text: str) -> dict:
    """Extract JSON from LLM response, handling markdown code blocks."""
    # Strip markdown code blocks
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    # Find JSON object
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


async def analyze_answer(
    question: str,
    spoken_answer: str,
    topic: str,
    claimed_skill_level: int,
    company: str,
    question_type: str = "technical",
    audio_metrics: dict = None
) -> dict:
    """
    STRICT analysis of one interview answer using Ollama.
    Communication patterns analyzed separately by rule engine.
    Technical accuracy judged by Ollama.
    """
    # Always run communication analysis (no Ollama needed)
    comm_analysis = _analyze_communication_patterns(spoken_answer)

    ollama_available = await _is_ollama_running()
    if not ollama_available:
        return _fallback_analysis(question, spoken_answer, topic, claimed_skill_level,
                                  question_type, comm_analysis)

    audio_context = ""
    if audio_metrics:
        wpm = audio_metrics.get("wpm", 0)
        vol = audio_metrics.get("averageVolume", 0)
        hesitations = audio_metrics.get("pauseCount", 0)
        audio_context = f"\nAUDIO DELIVERY METRICS:\n- Speaking Speed: {wpm} WPM\n- Average Volume/Energy: {vol:.2f} (proxy for confidence)\n- Long Pauses/Hesitations: {hesitations}\n\nUse these metrics to penalize or boost their communication score. A highly confident, well-paced answer is better than a hesitant, low-energy one."

    prompt = f"""You are a STRICT {company} senior engineer conducting a technical interview. Your job is to evaluate honestly — NOT to encourage or be nice. Inflate nothing.

QUESTION ASKED: "{question}"
TOPIC: {topic}
CANDIDATE'S CLAIMED SKILL LEVEL IN {topic}: {claimed_skill_level}/10

CANDIDATE'S SPOKEN ANSWER:
"{spoken_answer}"
{audio_context}

{STRICT_RUBRIC}

Now evaluate this specific answer. Return ONLY a valid JSON object. No markdown fences, no explanation:

{{
  "score": <integer 0-10, follow rubric strictly>,
  "technical_accuracy": <integer 0-10, how factually correct is the answer?>,
  "depth_of_knowledge": <integer 0-10, does the depth match their claimed level?>,
  "verdict": "<one of: Verified | Partially Verified | Overstated | Insufficient Answer>",
  "what_was_good": "<one specific thing correct in their answer, or null if nothing>",
  "what_was_missing": "<the single most important concept they missed or got wrong>",
  "claim_vs_reality": "<one of: Matches Claim | Below Claim | Exceeds Claim>",
  "red_flags": <true if score < 5 OR claim_vs_reality is Below Claim, else false>,
  "honest_feedback": "<one sentence of direct honest feedback a real interviewer would say>"
}}

Important: The candidate claims {claimed_skill_level}/10. If score < claimed_level - 2, verdict MUST be "Overstated" and claim_vs_reality MUST be "Below Claim"."""

    try:
        raw = await _ollama_chat(prompt, max_tokens=350)
        result = _extract_json_from_response(raw)

        if not result or "score" not in result:
            return _fallback_analysis(question, spoken_answer, topic, claimed_skill_level,
                                      question_type, comm_analysis)

        # ── POST-PROCESSING HARD RULES (cannot be overridden by LLM) ──
        score = int(result.get("score", 5))
        tech_acc = int(result.get("technical_accuracy", score))

        # Rule: blank or "I don't know" answers cannot score > 0
        answer_lower = spoken_answer.lower().strip()
        if not answer_lower or len(answer_lower) < 5 or any(
            x in answer_lower for x in ["i don't know", "idk", "no idea", "not sure", "i have no", "i cannot"]
        ):
            score = 0
            tech_acc = 0
            result["verdict"] = "Insufficient Answer"
            result["claim_vs_reality"] = "Below Claim"
            result["red_flags"] = True

        # Rule: if score < claimed_level - 2, enforce Below Claim
        if score < claimed_skill_level - 2:
            result["claim_vs_reality"] = "Below Claim"
            result["red_flags"] = True
            if score < claimed_skill_level - 4:
                result["verdict"] = "Overstated"

        # Rule: apply communication penalty to overall score
        comm_score = comm_analysis["communication_score"]
        # Weight: 70% technical + 30% communication
        combined_score = round(score * 0.70 + comm_score * 0.30)
        combined_score = max(0, min(10, combined_score))

        result["score"] = combined_score
        result["technical_accuracy"] = tech_acc
        result["communication_clarity"] = comm_score
        result["communication_analysis"] = comm_analysis
        result.setdefault("honest_feedback", "No specific feedback available.")
        return result

    except Exception as e:
        return _fallback_analysis(question, spoken_answer, topic, claimed_skill_level,
                                  question_type, comm_analysis)


async def generate_followup(
    question: str,
    spoken_answer: str,
    topic: str,
    company: str,
    score: int = 5
) -> str:
    """
    Generate a follow-up that PROBES DEEPER or CHALLENGES the weakness.
    If score < 5, ask them to prove they know what they claimed.
    """
    ollama_available = await _is_ollama_running()
    if not ollama_available:
        probes = [
            "Can you write the actual code for that? Walk me through it line by line.",
            "You mentioned that concept — what's the time complexity, and why?",
            "Give me a real example from a project you built. Be specific.",
            "What would break if that assumption was wrong? Think about edge cases."
        ]
        import random
        return random.choice(probes)

    # If the score was low, ask a challenging follow-up
    if score <= 4:
        probe_instruction = "The candidate's answer was weak or incomplete. Ask a simpler version of the same concept to test if they know the basics at all. Be direct, not gentle."
    elif score <= 6:
        probe_instruction = "The candidate's answer was partial. Ask a follow-up that tests the specific concept they got wrong or missed."
    else:
        probe_instruction = "The candidate's answer was decent. Ask a deeper follow-up about edge cases, trade-offs, or real-world application."

    prompt = f"""You are a {company} technical interviewer. {probe_instruction}

Original question: "{question}"
Candidate answered: "{spoken_answer}"

Write ONE follow-up question (1-2 sentences max). Be direct. No preamble, no "Good answer", just the question. Return only the question text."""

    try:
        result = await _ollama_chat(prompt, max_tokens=80)
        result = result.strip().strip('"').strip()
        if len(result) < 10:
            return "Can you walk me through the actual implementation? Be specific."
        return result
    except Exception:
        return "Interesting — can you walk me through a real example where this applies, step by step?"


def _extract_project_mention(answer: str, candidate_projects: list = None) -> Optional[str]:
    """Extract a specific project name from candidate's spoken text or known profile."""
    if not answer:
        if candidate_projects and len(candidate_projects) > 0:
            first = candidate_projects[0]
            return first.get("name") if isinstance(first, dict) else str(first)
        return None

    # Check candidate profile projects first
    if candidate_projects:
        for p in candidate_projects:
            name = p.get("name") if isinstance(p, dict) else str(p)
            if name.lower() in answer.lower():
                return name
            words = [w for w in name.split() if len(w) > 4]
            for w in words:
                if w.lower() in answer.lower():
                    return name

    # Regex patterns for phrases like "built X", "worked on X", "project called X", "project is X"
    patterns = [
        r'(?:built|developed|created|worked on|architected|project called|project named|my project)\s+(?:a|an|the)?\s*([A-Za-z0-9\s\-]{3,35})',
        r'([A-Za-z0-9\s\-]{3,25})\s+project',
    ]
    for pat in patterns:
        m = re.search(pat, answer, re.IGNORECASE)
        if m:
            candidate = m.group(1).strip()
            stopwords = {"system", "app", "application", "website", "few", "lot", "bunch", "couple", "it", "this", "that", "some"}
            if candidate.lower() not in stopwords and len(candidate.split()) <= 4:
                return candidate.title()

    if candidate_projects and len(candidate_projects) > 0:
        first = candidate_projects[0]
        return first.get("name") if isinstance(first, dict) else str(first)

    return None


async def generate_adaptive_next_question(
    current_index: int,
    company: str,
    last_question: str,
    last_answer: str,
    all_qa_history: list = None,
    student_projects: list = None,
    student_skills: dict = None
) -> dict:
    """
    HackerRank-style Adaptive AI Interview Progression:
    Stage 0 (current_index=0 completed): Selects candidate's project or asks for best project architecture.
    Stage 1 (current_index=1 completed): Probes technical trade-offs, concurrency, or failure modes on that architecture.
    Stage 2 (current_index=2 completed): Asks STAR behavioral question about deadlines, conflict, or teamwork.
    Stage 3 (current_index=3 completed): Asks about company culture fit and career alignment.
    Stage 4 (current_index=4 completed): Concludes the interview (is_final=True).
    """
    all_qa = all_qa_history or []
    ollama_ok = await _is_ollama_running()

    # Stage 0 -> Stage 1: Candidate completed Self-Introduction & Overview
    if current_index == 0:
        detected_project = _extract_project_mention(last_answer, student_projects)
        if detected_project:
            q_text = f"You mentioned your project '{detected_project}'. Let's dive into that. Walk me through the system architecture: what real-world problem does it solve, and how does data flow across its core components?"
            voice_prompt = f"You mentioned your project '{detected_project}'. Walk me through the system architecture and how data flows across your components."
            project_label = detected_project
        else:
            q_text = "Tell me about one of your best software engineering projects: what real-world problem did you set out to solve, how did you architect the system, and what was your specific technical role?"
            voice_prompt = "Tell me about one of your best software projects: what problem did you set out to solve, and walk me through its system architecture."
            project_label = "Flagship Engineering Project"

        if ollama_ok and last_answer and len(last_answer) > 20:
            prompt = f"""You are a senior {company} interviewer in an AI mock room.
The candidate just completed their self-introduction:
"{last_answer}"
Detected or profile project: {detected_project or 'None specified'}

Goal:
If they mentioned a specific project, ask them directly to explain that project's architecture and data flow.
If they did not name a project, ask them to pick their best project and walk through its architecture.
Write ONE direct, conversational interview question (1-2 sentences). Return ONLY the question."""
            try:
                ai_q = await _ollama_chat(prompt, max_tokens=70)
                cleaned = ai_q.strip().strip('"').replace('\n', ' ').strip()
                if len(cleaned) > 20 and "?" in cleaned:
                    q_text = cleaned
                    voice_prompt = cleaned
            except Exception:
                pass

        return {
            "round_id": 1,
            "round_name": "Round 1: Project Architecture & Technical Defense",
            "round_type": "project_defense",
            "project_name": project_label,
            "question": q_text,
            "topic": f"System Architecture ({project_label})",
            "difficulty": "Medium",
            "claimed_level": 7,
            "voice_prompt": voice_prompt,
            "is_final": False
        }

    # Stage 1 -> Stage 2: Candidate explained Project Architecture
    elif current_index == 1:
        fallback_project = _extract_project_mention(last_answer, student_projects) or "this project"
        q_text = f"In that architecture, what were the most critical technical trade-offs you evaluated (e.g. database, caching, or framework choices)? What was the hardest failure mode, concurrency bottleneck, or production bug you resolved?"
        voice_prompt = "In that architecture, what was the hardest technical trade-off or failure mode you encountered, and how did you resolve it?"

        if ollama_ok and last_answer and len(last_answer) > 20:
            prompt = f"""You are a senior {company} engineering director.
The candidate just explained their system architecture:
"{last_answer}"

Goal:
Challenge ONE technical decision, trade-off, or failure mode they described (e.g. concurrency, database bottlenecks, caching, or error recovery).
Write ONE direct, probing question (1-2 sentences max). Return ONLY the question."""
            try:
                ai_q = await _ollama_chat(prompt, max_tokens=70)
                cleaned = ai_q.strip().strip('"').replace('\n', ' ').strip()
                if len(cleaned) > 20 and "?" in cleaned:
                    q_text = cleaned
                    voice_prompt = cleaned
            except Exception:
                pass

        return {
            "round_id": 1,
            "round_name": "Round 1: Project Architecture & Technical Defense",
            "round_type": "project_defense",
            "project_name": fallback_project,
            "question": q_text,
            "topic": f"Trade-offs & Failure Modes",
            "difficulty": "Hard",
            "claimed_level": 8,
            "voice_prompt": voice_prompt,
            "is_final": False
        }

    # Stage 2 -> Stage 3: Candidate defended trade-offs -> advance to STAR Behavioral
    elif current_index == 2:
        q_text = f"That demonstrates solid engineering problem-solving. Now, while building software or collaborating in a team, tell me about a time you faced a strict delivery deadline or conflicting technical priorities with a team member. Using the STAR framework (Situation, Task, Action, Result), how did you handle it and what was the quantifiable outcome?"
        voice_prompt = "Using the STAR method, tell me about a time you handled a strict deadline or team disagreement while delivering software."

        return {
            "round_id": 2,
            "round_name": "Round 2: Behavioral & Corporate HR Round",
            "round_type": "behavioral",
            "project_name": "STAR Behavioral Framework",
            "question": q_text,
            "topic": "STAR: Conflict & Deadline Delivery",
            "difficulty": "Medium",
            "claimed_level": 7,
            "voice_prompt": voice_prompt,
            "is_final": False
        }

    # Stage 3 -> Stage 4: Candidate answered STAR -> advance to Company Culture & Alignment
    elif current_index == 3:
        q_text = f"Thank you for sharing that experience. To conclude our interview, why are you specifically targeting {company}, and how do your technical strengths and long-term career aspirations align with our engineering culture?"
        voice_prompt = f"Lastly, why {company}, and how do your long-term career aspirations align with our engineering culture?"

        return {
            "round_id": 2,
            "round_name": "Round 2: Behavioral & Corporate HR Round",
            "round_type": "behavioral",
            "project_name": f"{company} Alignment",
            "question": q_text,
            "topic": f"{company} Cultural Alignment & Fit",
            "difficulty": "Medium",
            "claimed_level": 7,
            "voice_prompt": voice_prompt,
            "is_final": False
        }

    # Stage 4+: Final question completed
    else:
        return {
            "round_id": 2,
            "round_name": "Round 2: Behavioral & Corporate HR Round",
            "round_type": "behavioral",
            "question": "Interview Completed.",
            "topic": "Evaluation Complete",
            "is_final": True
        }


async def generate_interviewer_speech(
    question: str,
    answer: str,
    topic: str,
    company: str,
    code: Optional[str] = None,
    execution_result: Optional[dict] = None
) -> str:
    """
    Generate a realistic conversational remark from the company interviewer
    acknowledging the candidate's answer, challenging edge cases, or probing trade-offs.
    Kept concise (1-2 sentences) for human-like Text-To-Speech output.
    """
    tests_summary = ""
    if execution_result:
        passed = execution_result.get("tests_passed", 0)
        total = execution_result.get("tests_total", 0)
        success = execution_result.get("success", False)
        if total > 0:
            tests_summary = f"Passed {passed} out of {total} test cases."
        elif success:
            tests_summary = "Code executed with 0 runtime errors."
        else:
            tests_summary = f"Code execution failed with error: {execution_result.get('error', '')[:80]}"

    is_intro_q = "introduce yourself" in question.lower() or "about yourself" in question.lower() or "background" in question.lower()
    is_arch_q = "system architecture" in question.lower() or "architecture" in question.lower()
    is_tradeoff_q = "trade-off" in question.lower() or "failure mode" in question.lower() or "bottleneck" in question.lower() or "100x" in question.lower()
    is_star_q = "star" in question.lower() or "deadline" in question.lower() or "conflict" in question.lower()
    is_company_q = f"why {company.lower()}" in question.lower() or "targeting" in question.lower() or "culture" in question.lower()

    if is_intro_q:
        stage_goal = "Acknowledge the candidate's introduction and background in 1 sentence. Then smoothly invite them into defending their technical projects."
    elif is_arch_q:
        stage_goal = "Acknowledge their architectural choices. Challenge them on one real-world edge case, data consistency issue, or trade-off."
    elif is_tradeoff_q:
        stage_goal = "Acknowledge how they debugged the bottleneck or handled failure modes. Transition smoothly toward their collaboration and team delivery."
    elif is_star_q:
        stage_goal = "Acknowledge their resolution under pressure using STAR. Then transition to asking about their alignment with the company."
    elif is_company_q:
        stage_goal = f"Conclude professionally, expressing appreciation for their interest in {company} and stating their responses have been logged."
    else:
        stage_goal = "Acknowledge the answer and challenge edge cases, time complexity, or architectural trade-offs."

    role_desc = f"You are a senior {company} engineering director conducting a live professional recruitment interview."

    prompt = f"""{role_desc} Talk to the candidate directly in a natural, professional spoken tone.
Question asked: "{question}"
Candidate's response: "{answer or '[No verbal answer provided]'}"
Code submitted: "{code[:250] if code else 'None (Verbal defense)'}"
Execution outcome: {tests_summary or 'None'}

Goal: {stage_goal}
In 1 or 2 natural, spoken sentences (max 35 words):
Speak directly like an interviewer sitting across the table. Be professional, authentic, and direct. Do NOT introduce yourself or say "Hello candidate".
Return ONLY the spoken sentences."""

    try:
        reply = await _ollama_chat(prompt, max_tokens=70)
        cleaned = reply.strip().strip('"').replace('\n', ' ').strip()
        if len(cleaned) > 15:
            return cleaned
    except Exception:
        pass

    if is_intro_q:
        detected = _extract_project_mention(answer)
        if detected:
            return f"Thank you for that overview. You mentioned your project '{detected}' — let's dive into that. Walk me through the system architecture and how data flows across your components."
        return "Thank you for that background overview. Tell me about one of your best software projects: what problem did you set out to solve and what was your architecture?"
    if is_arch_q:
        return "Good breakdown of the system components and data flow. What was the single most difficult technical trade-off or failure mode you hit?"
    if is_tradeoff_q:
        return "That shows solid engineering maturity and resilience. Now let's explore how you handle situational pressure and team dynamics."
    if is_star_q:
        return f"Strong explanation of how you delivered under pressure. To wrap up, why are you interested in {company} and how do our engineering values fit your goals?"
    if is_company_q:
        return f"Thank you for sharing your perspective and enthusiasm for {company}. We have logged your assessment and will compile your hiring report."

    if execution_result and execution_result.get("test_results"):
        passed = execution_result.get("tests_passed", 0)
        total = execution_result.get("tests_total", 0)
        if passed == total:
            return f"Your solution passed all {total} test cases. What is the worst-case space and time complexity?"
        return f"Your code passed {passed} of {total} test cases. Which edge case do you think is failing?"

    return "Good explanation. Can you give me a specific real-world scenario where that trade-off would become a bottleneck?"


async def generate_full_interview_report(
    student_name: str,
    company: str,
    qa_pairs: list,
    student_skills: dict
) -> dict:
    """
    STRICT comprehensive interview report.
    Includes: technical score, communication score, skill verification,
    honest assessment, what must change for the student to be hireable.
    """
    ollama_available = await _is_ollama_running()
    if not ollama_available:
        return _fallback_report(student_name, company, qa_pairs, student_skills)

    # Build transcript
    qa_text = ""
    for i, qa in enumerate(qa_pairs):
        qa_text += f"\nQ{i+1} [{qa.get('topic','General')}] (Claimed: {qa.get('claimed_level','?')}/10):\n"
        qa_text += f"Question: {qa.get('question', '')}\n"
        qa_text += f"Answer: {qa.get('answer', 'No answer given')}\n"
        qa_text += f"Score: {qa.get('score', '?')}/10 | Verdict: {qa.get('verdict','?')} | Claim: {qa.get('claim_vs_reality','?')}\n"

    prompt = f"""You are a senior {company} hiring manager. You just interviewed {student_name}.

FULL INTERVIEW TRANSCRIPT:
{qa_text}

STUDENT'S CLAIMED SKILLS: {json.dumps(student_skills)}

Write a hiring decision report. Be brutally honest. Do not inflate. If the student performed poorly, say so clearly.
Return ONLY valid JSON (no markdown):

{{
  "overall_score": <integer 0-100, weighted avg of all scores>,
  "technical_score": <integer 0-100>,
  "communication_score": <integer 0-100>,
  "verdict": "<STRONGLY_RECOMMENDED | RECOMMENDED | BORDERLINE | NOT_RECOMMENDED>",
  "readiness_tier": "<Interview Ready | Near Ready | Needs Preparation>",
  "skill_verification": [
    {{"skill": "<name>", "claimed_level": <1-10>, "demonstrated_level": <1-10>, "status": "<Verified|Partially Verified|Overstated|Unverified>"}}
  ],
  "strengths": ["<strength1 - only real ones seen in transcript>"],
  "critical_gaps": ["<gap1 - specific things they clearly don't know>"],
  "communication_observations": "<2 specific sentences about how they communicated>",
  "technical_observations": "<2 specific sentences about their technical depth>",
  "honest_verdict": "<1-2 sentences a real hiring manager would say, no sugarcoating>",
  "what_must_improve": ["<specific actionable improvement 1>", "<specific actionable improvement 2>"]
}}

Rules:
- overall_score >= 80 → STRONGLY_RECOMMENDED
- overall_score 65-79 → RECOMMENDED
- overall_score 45-64 → BORDERLINE
- overall_score < 45 → NOT_RECOMMENDED
- If ANY skill was "Overstated" by more than 3 levels, flag it clearly in critical_gaps
- Do NOT be kind just because they attempted questions. Score what was demonstrated."""

    try:
        raw = await _ollama_chat(prompt, max_tokens=700)
        report = _extract_json_from_response(raw)

        if not report or "overall_score" not in report:
            return _fallback_report(student_name, company, qa_pairs, student_skills)

        # Hard rule: enforce verdict consistency
        overall = int(report.get("overall_score", 50))
        if overall >= 80:
            report["verdict"] = "STRONGLY_RECOMMENDED"
            report["readiness_tier"] = "Interview Ready"
        elif overall >= 65:
            report["verdict"] = "RECOMMENDED"
            report["readiness_tier"] = "Interview Ready"
        elif overall >= 45:
            report["verdict"] = "BORDERLINE"
            report["readiness_tier"] = "Near Ready"
        else:
            report["verdict"] = "NOT_RECOMMENDED"
            report["readiness_tier"] = "Needs Preparation"

        report["company"] = company
        report["student_name"] = student_name
        report["total_questions"] = len(qa_pairs)
        report["round_breakdown"] = _compute_round_breakdown(qa_pairs)
        report["powered_by"] = "Ollama llama3.2:3b (local, 100% private)"
        return report

    except Exception:
        return _fallback_report(student_name, company, qa_pairs, student_skills)


def _compute_round_breakdown(qa_pairs: list) -> list[dict]:
    """Compute round-specific scores for OA, Technical Deep Dive, and Behavioral."""
    rounds_map = {}
    for qa in qa_pairs:
        rid = qa.get("round_id") or (1 if qa.get("code") or qa.get("language") else 2 if qa.get("topic") not in ["Behavioral", "HR", "Leadership"] else 3)
        rname = qa.get("round_name") or ("Round 1: Online Coding (OA)" if rid == 1 else "Round 2: Technical Deep Dive" if rid == 2 else "Round 3: Leadership & Behavioral")
        if rid not in rounds_map:
            rounds_map[rid] = {
                "round_id": rid,
                "round_name": rname,
                "scores": [],
                "questions_count": 0,
                "code_submissions": 0
            }
        rounds_map[rid]["scores"].append(qa.get("score", 0))
        rounds_map[rid]["questions_count"] += 1
        if qa.get("code"):
            rounds_map[rid]["code_submissions"] += 1

    breakdown = []
    for rid in sorted(rounds_map.keys()):
        item = rounds_map[rid]
        avg_score = round(sum(item["scores"]) / max(1, len(item["scores"])), 1)
        scaled_pct = min(100, int(avg_score * 10))
        status = "Passed" if scaled_pct >= 65 else "Borderline" if scaled_pct >= 45 else "Needs Improvement"
        breakdown.append({
            "round_id": rid,
            "round_name": item["round_name"],
            "score": scaled_pct,
            "status": status,
            "questions_count": item["questions_count"],
            "code_submissions": item["code_submissions"]
        })
    return breakdown


def _fallback_analysis(question, answer, topic, claimed_level, q_type, comm_analysis=None):
    """Rule-based fallback when Ollama is not available. Also strict."""
    answer_lower = answer.lower().strip()
    word_count = len(answer_lower.split()) if answer_lower else 0

    # Blank / "I don't know"
    if word_count < 3 or any(x in answer_lower for x in ["i don't know", "idk", "not sure", "no idea"]):
        score, verdict = 0, "Insufficient Answer"
        claim_reality = "Below Claim"
        red_flag = True
    elif word_count > 50 and any(w in answer_lower for w in ["because", "example", "for instance", "when i", "specifically"]):
        score = min(7, claimed_level)
        verdict = "Verified" if claimed_level <= 6 else "Partially Verified"
        claim_reality = "Matches Claim" if score >= claimed_level - 1 else "Below Claim"
        red_flag = score < 4
    elif word_count > 20:
        score = min(5, max(2, claimed_level - 2))
        verdict = "Partially Verified"
        claim_reality = "Below Claim" if score < claimed_level - 1 else "Matches Claim"
        red_flag = score < 4
    else:
        score = 2
        verdict = "Overstated"
        claim_reality = "Below Claim"
        red_flag = True

    score = max(0, min(10, score))
    comm = comm_analysis or {"communication_score": 5 if word_count > 15 else 2}
    combined = round(score * 0.70 + comm["communication_score"] * 0.30)

    return {
        "score": combined,
        "technical_accuracy": score,
        "communication_clarity": comm.get("communication_score", 5),
        "depth_of_knowledge": max(0, score - 1),
        "verdict": verdict,
        "what_was_good": None if score < 4 else "Some relevant points mentioned.",
        "what_was_missing": "Ollama not running — start it for full AI analysis.",
        "claim_vs_reality": claim_reality,
        "red_flags": red_flag,
        "communication_analysis": comm,
        "honest_feedback": "Start Ollama for accurate AI feedback: `brew services start ollama`",
        "note": "⚠️ Fallback scoring (Ollama offline)"
    }


def _fallback_report(student_name, company, qa_pairs, student_skills):
    """Strict fallback report."""
    scores = [qa.get("score", 0) for qa in qa_pairs if "score" in qa]
    avg_score = (sum(scores) / len(scores)) if scores else 0
    overall = int(avg_score * 10)

    # Count overstated skills
    overstated = [qa for qa in qa_pairs if qa.get("claim_vs_reality") == "Below Claim"]
    if len(overstated) >= 2:
        overall = min(overall, 45)  # Cap if skills were overstated

    if overall >= 80:
        verdict = "STRONGLY_RECOMMENDED"
        tier = "Interview Ready"
    elif overall >= 65:
        verdict = "RECOMMENDED"
        tier = "Interview Ready"
    elif overall >= 45:
        verdict = "BORDERLINE"
        tier = "Near Ready"
    else:
        verdict = "NOT_RECOMMENDED"
        tier = "Needs Preparation"

    return {
        "overall_score": overall,
        "technical_score": overall,
        "communication_score": 45,
        "verdict": verdict,
        "readiness_tier": tier,
        "skill_verification": [
            {
                "skill": s,
                "claimed_level": l,
                "demonstrated_level": max(1, l - 2),
                "status": "Partially Verified"
            }
            for s, l in list(student_skills.items())[:4]
        ],
        "strengths": ["Attempted questions"] if scores else ["No answers recorded"],
        "critical_gaps": ["Start Ollama for detailed gap analysis. Run: brew services start ollama"],
        "communication_observations": "Detailed analysis requires Ollama AI (not running).",
        "technical_observations": f"Avg score: {avg_score:.1f}/10 across {len(qa_pairs)} questions.",
        "honest_verdict": "Ollama not available. Scores based on rule-based fallback only.",
        "what_must_improve": ["Start Ollama for specific improvement recommendations"],
        "company": company,
        "student_name": student_name,
        "total_questions": len(qa_pairs),
        "round_breakdown": _compute_round_breakdown(qa_pairs),
        "powered_by": "Rule-based fallback (Ollama offline)"
    }
