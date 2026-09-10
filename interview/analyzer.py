"""
AI Interview Analyzer using Ollama (local, open-source, completely free).
Uses llama3.2:3b running locally via Ollama REST API on port 11434.
No API keys. No internet. 100% private. Runs on Apple Silicon Metal GPU.

Falls back to rule-based scoring if Ollama is not available.
"""

import json
import httpx
import asyncio
from typing import Optional

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2:3b"


async def _ollama_chat(prompt: str, max_tokens: int = 600, json_mode: bool = True) -> str:
    """Send a prompt to Ollama and get a response."""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.15 if json_mode else 0.4,
            "num_predict": max_tokens,
            "top_p": 0.9
        }
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()


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
    import re
    # Try to find JSON block
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    # Try full text as JSON
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
    question_type: str = "technical"
) -> dict:
    """
    Analyze one interview answer using Ollama (llama3.2:3b locally).
    Returns structured analysis with score, verdict, skill verification.
    """
    ollama_available = await _is_ollama_running()
    if not ollama_available:
        return _fallback_analysis(question, spoken_answer, topic, claimed_skill_level, question_type)

    prompt = f"""You are a strict {company} technical interviewer evaluating a candidate's answer.

Question: "{question}"
Topic: {topic}
Student's claimed skill level in {topic}: {claimed_skill_level}/10

Student's answer: "{spoken_answer}"

Evaluate this answer STRICTLY and return ONLY valid JSON. No markdown, no explanation, just the JSON object:

{{
  "score": <integer 0-10, be strict>,
  "technical_accuracy": <integer 0-10>,
  "communication_clarity": <integer 0-10>,
  "depth_of_knowledge": <integer 0-10>,
  "verdict": "<exactly one of: Verified, Partially Verified, Overstated, Insufficient Answer>",
  "what_was_good": "<one sentence or null>",
  "what_was_missing": "<one sentence about key missing knowledge>",
  "claim_vs_reality": "<exactly one of: Matches Claim, Below Claim, Exceeds Claim>",
  "red_flags": <true or false>
}}

Scoring rules:
- 9-10: Expert level, complete accurate answer
- 7-8: Good answer, minor gaps
- 5-6: Partial understanding, key concepts missing
- 3-4: Mostly wrong but shows some awareness
- 0-2: Completely wrong, blank, or "don't know"

Student claims {claimed_skill_level}/10 in {topic}. If their answer doesn't match that level, mark claim_vs_reality as "Below Claim" and lower the score accordingly. Be honest."""

    try:
        raw = await _ollama_chat(prompt, max_tokens=300, json_mode=True)
        result = _extract_json_from_response(raw)
        if not result or "score" not in result:
            return _fallback_analysis(question, spoken_answer, topic, claimed_skill_level, question_type)
        # Ensure all required fields exist
        result.setdefault("verdict", "Partially Verified")
        result.setdefault("claim_vs_reality", "Matches Claim")
        result.setdefault("red_flags", False)
        result.setdefault("what_was_good", None)
        result.setdefault("what_was_missing", "Could not parse details.")
        return result
    except Exception as e:
        return _fallback_analysis(question, spoken_answer, topic, claimed_skill_level, question_type)


async def generate_followup(
    question: str,
    spoken_answer: str,
    topic: str,
    company: str
) -> str:
    """Generate a natural follow-up question based on the student's answer."""
    ollama_available = await _is_ollama_running()
    if not ollama_available:
        return "Can you give me a specific example where you applied this concept in a real project?"

    prompt = f"""You are a {company} technical interviewer. The candidate was asked:
"{question}"

They answered: "{spoken_answer}"

Write ONE follow-up question (1-2 sentences only) that probes deeper into what they said or tests if they truly understand it. Be direct and specific. Return only the question text, no explanation."""

    try:
        result = await _ollama_chat(prompt, max_tokens=80, json_mode=False)
        # Clean up the response
        result = result.strip().strip('"').strip()
        if len(result) < 10:
            return "Can you walk me through a concrete example of this in practice?"
        return result
    except Exception:
        return "Interesting — can you walk me through a real project where you applied this?"


async def generate_full_interview_report(
    student_name: str,
    company: str,
    qa_pairs: list[dict],
    student_skills: dict
) -> dict:
    """
    Generate comprehensive interview report using Ollama after all questions answered.
    """
    ollama_available = await _is_ollama_running()
    if not ollama_available:
        return _fallback_report(student_name, company, qa_pairs, student_skills)

    # Build a summary of the Q&A session
    qa_text = ""
    for i, qa in enumerate(qa_pairs):
        qa_text += f"\nQ{i+1} [{qa.get('topic','General')}] (Claimed: {qa.get('claimed_level','?')}/10): {qa.get('question','')}\n"
        qa_text += f"Answer: {qa.get('answer', 'No answer')}\n"
        qa_text += f"Score: {qa.get('score', '?')}/10, Verdict: {qa.get('verdict','?')}\n"

    prompt = f"""You are a senior {company} interviewer. You just finished interviewing {student_name}.

Interview transcript:
{qa_text}

Student's claimed skills: {json.dumps(student_skills)}

Write a final interview report. Return ONLY valid JSON (no markdown):

{{
  "overall_score": <integer 0-100>,
  "technical_score": <integer 0-100>,
  "communication_score": <integer 0-100>,
  "verdict": "<one of: STRONGLY_RECOMMENDED, RECOMMENDED, BORDERLINE, NOT_RECOMMENDED>",
  "readiness_tier": "<one of: Interview Ready, Near Ready, Needs Preparation>",
  "skill_verification": [
    {{"skill": "<name>", "claimed_level": <1-10>, "demonstrated_level": <1-10>, "status": "<Verified|Partially Verified|Overstated>"}}
  ],
  "strengths": ["<strength1>", "<strength2>"],
  "gaps": ["<gap1>", "<gap2>"],
  "communication_observations": "<2 sentences>",
  "technical_observations": "<2 sentences>",
  "recommendation": "<specific advice for this student, 2 sentences>"
}}

Be honest. Base scores strictly on answers shown. Include top 3-4 skills in skill_verification."""

    try:
        raw = await _ollama_chat(prompt, max_tokens=600, json_mode=True)
        report = _extract_json_from_response(raw)
        if not report or "overall_score" not in report:
            return _fallback_report(student_name, company, qa_pairs, student_skills)
        report["company"] = company
        report["student_name"] = student_name
        report["total_questions"] = len(qa_pairs)
        report["powered_by"] = "Ollama llama3.2:3b (local)"
        return report
    except Exception:
        return _fallback_report(student_name, company, qa_pairs, student_skills)


def _fallback_analysis(question, answer, topic, claimed_level, q_type):
    """Rule-based fallback when Ollama is not available."""
    answer_lower = answer.lower().strip()
    word_count = len(answer_lower.split()) if answer_lower else 0

    if word_count < 5 or any(x in answer_lower for x in ["i don't know", "not sure", "no idea", "idk"]):
        score, verdict = 0, "Insufficient Answer"
    elif word_count > 60 and any(w in answer_lower for w in ["because", "example", "for instance", "specifically", "when i"]):
        score = min(7, claimed_level)
        verdict = "Verified" if claimed_level <= 7 else "Partially Verified"
    elif word_count > 25:
        score = min(5, claimed_level - 1)
        verdict = "Partially Verified"
    else:
        score = 2
        verdict = "Overstated"

    score = max(0, min(10, score))
    return {
        "score": score,
        "technical_accuracy": score,
        "communication_clarity": 5 if word_count > 15 else 2,
        "depth_of_knowledge": max(0, score - 1),
        "verdict": verdict,
        "what_was_good": "Answer provided." if score > 3 else None,
        "what_was_missing": "Start Ollama service for AI-powered evaluation.",
        "claim_vs_reality": "Matches Claim" if score >= claimed_level - 2 else "Below Claim",
        "red_flags": score < 3,
        "note": "⚠️ Rule-based fallback — Ollama not running. Start with: brew services start ollama"
    }


def _fallback_report(student_name, company, qa_pairs, student_skills):
    """Simple fallback report when Ollama is unavailable."""
    scores = [qa.get("score", 5) for qa in qa_pairs if qa.get("score") is not None]
    avg = sum(scores) / len(scores) if scores else 5
    overall = int(avg * 10)
    verdict = "RECOMMENDED" if overall >= 70 else "BORDERLINE" if overall >= 50 else "NOT_RECOMMENDED"

    return {
        "overall_score": overall,
        "technical_score": overall,
        "communication_score": 55,
        "verdict": verdict,
        "readiness_tier": "Interview Ready" if overall >= 75 else "Near Ready" if overall >= 55 else "Needs Preparation",
        "skill_verification": [
            {"skill": s, "claimed_level": l, "demonstrated_level": max(1, l - 2), "status": "Partially Verified"}
            for s, l in list(student_skills.items())[:4]
        ],
        "strengths": ["Attempted all questions", "Showed willingness to engage"],
        "gaps": ["Start Ollama for detailed skill gap analysis"],
        "communication_observations": "Detailed analysis unavailable — Ollama not running.",
        "technical_observations": f"Rule-based average score: {avg:.1f}/10.",
        "recommendation": "Run 'brew services start ollama' for full AI-powered analysis.",
        "company": company,
        "student_name": student_name,
        "total_questions": len(qa_pairs),
        "powered_by": "Rule-based fallback (Ollama not running)"
    }
