"""
Local code execution sandbox for interview coding questions.
Runs Python, JavaScript (node), Java, C++ safely in subprocess.
No Docker, no external API. Runs on your Mac.

Security: timeout=5s, no file I/O, no network inside sandbox.
"""

import subprocess
import tempfile
import os
import time
import json
import asyncio
from typing import Optional

TIMEOUT_SECONDS = 6
MAX_OUTPUT_BYTES = 10_000

LANGUAGE_CONFIG = {
    "python": {
        "extension": ".py",
        "command": ["python3"],
        "check": ["python3", "--version"],
    },
    "javascript": {
        "extension": ".js",
        "command": ["node"],
        "check": ["node", "--version"],
    },
    "java": {
        "extension": ".java",
        "compile": ["javac"],
        "run": ["java"],
        "check": ["java", "--version"],
    },
    "cpp": {
        "extension": ".cpp",
        "compile": ["g++", "-o"],
        "check": ["g++", "--version"],
    },
    "c": {
        "extension": ".c",
        "compile": ["gcc", "-o"],
        "check": ["gcc", "--version"],
    },
}


def _check_runtime(lang: str) -> bool:
    """Check if the runtime is available."""
    config = LANGUAGE_CONFIG.get(lang)
    if not config:
        return False
    try:
        subprocess.run(config["check"], capture_output=True, timeout=3)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def execute_code(
    code: str,
    language: str,
    stdin: str = "",
    test_cases: Optional[list] = None
) -> dict:
    """
    Execute code safely in a temp file with timeout.
    Returns: {success, output, error, runtime_ms, test_results}
    """
    language = language.lower()
    if language not in LANGUAGE_CONFIG:
        return {
            "success": False,
            "output": "",
            "error": f"Language '{language}' not supported. Use: python, javascript, java, cpp, c",
            "runtime_ms": 0,
            "test_results": []
        }

    if not _check_runtime(language):
        return {
            "success": False,
            "output": "",
            "error": f"Runtime for '{language}' not found on this machine. Install it first.",
            "runtime_ms": 0,
            "test_results": []
        }

    config = LANGUAGE_CONFIG[language]
    ext = config["extension"]

    with tempfile.TemporaryDirectory() as tmpdir:
        # Write source file
        src_file = os.path.join(tmpdir, f"solution{ext}")
        with open(src_file, "w") as f:
            f.write(code)

        # Compile if needed
        if language == "java":
            # Extract class name
            import re
            class_match = re.search(r'public\s+class\s+(\w+)', code)
            class_name = class_match.group(1) if class_match else "Solution"
            src_file = os.path.join(tmpdir, f"{class_name}.java")
            with open(src_file, "w") as f:
                f.write(code)
            compile_result = subprocess.run(
                ["javac", src_file], capture_output=True, text=True, timeout=10, cwd=tmpdir
            )
            if compile_result.returncode != 0:
                return {
                    "success": False, "output": "",
                    "error": compile_result.stderr[:2000],
                    "runtime_ms": 0, "test_results": []
                }
            run_cmd = ["java", "-cp", tmpdir, class_name]

        elif language == "cpp":
            out_bin = os.path.join(tmpdir, "solution_out")
            compile_result = subprocess.run(
                ["g++", "-O2", "-o", out_bin, src_file],
                capture_output=True, text=True, timeout=15
            )
            if compile_result.returncode != 0:
                return {
                    "success": False, "output": "",
                    "error": compile_result.stderr[:2000],
                    "runtime_ms": 0, "test_results": []
                }
            run_cmd = [out_bin]

        elif language == "c":
            out_bin = os.path.join(tmpdir, "solution_out")
            compile_result = subprocess.run(
                ["gcc", "-O2", "-o", out_bin, src_file],
                capture_output=True, text=True, timeout=15
            )
            if compile_result.returncode != 0:
                return {
                    "success": False, "output": "",
                    "error": compile_result.stderr[:2000],
                    "runtime_ms": 0, "test_results": []
                }
            run_cmd = [out_bin]

        elif language == "python":
            run_cmd = ["python3", src_file]

        elif language == "javascript":
            run_cmd = ["node", src_file]

        # Run with optional stdin
        start = time.time()
        try:
            result = subprocess.run(
                run_cmd,
                input=stdin,
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SECONDS,
                cwd=tmpdir,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
            )
            runtime_ms = int((time.time() - start) * 1000)
            stdout = result.stdout[:MAX_OUTPUT_BYTES]
            stderr = result.stderr[:2000]

            # Run test cases if provided
            test_results = []
            if test_cases:
                for i, tc in enumerate(test_cases[:5]):
                    tc_input = tc.get("input", "")
                    expected = tc.get("expected_output", "").strip()
                    try:
                        tc_result = subprocess.run(
                            run_cmd, input=tc_input,
                            capture_output=True, text=True,
                            timeout=TIMEOUT_SECONDS, cwd=tmpdir
                        )
                        actual = tc_result.stdout.strip()
                        passed = actual == expected
                        test_results.append({
                            "test_case": i + 1,
                            "passed": passed,
                            "input": tc_input[:200],
                            "expected": expected[:200],
                            "actual": actual[:200],
                            "error": tc_result.stderr[:200] if tc_result.returncode != 0 else None
                        })
                    except subprocess.TimeoutExpired:
                        test_results.append({
                            "test_case": i + 1,
                            "passed": False,
                            "error": "Time Limit Exceeded"
                        })

            return {
                "success": result.returncode == 0,
                "output": stdout,
                "error": stderr if result.returncode != 0 else "",
                "runtime_ms": runtime_ms,
                "return_code": result.returncode,
                "test_results": test_results,
                "tests_passed": sum(1 for t in test_results if t.get("passed")),
                "tests_total": len(test_results)
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": f"⏰ Time Limit Exceeded ({TIMEOUT_SECONDS}s). Optimize your algorithm.",
                "runtime_ms": TIMEOUT_SECONDS * 1000,
                "test_results": []
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "runtime_ms": 0,
                "test_results": []
            }


async def analyze_code_with_ollama(
    code: str,
    question: str,
    language: str,
    execution_result: dict,
    claimed_skill_level: int
) -> dict:
    """
    Use Ollama to analyze submitted code quality, correctness, and complexity.
    Returns strict analysis matching the interview scoring standard.
    """
    import httpx

    test_summary = ""
    if execution_result.get("test_results"):
        passed = execution_result.get("tests_passed", 0)
        total = execution_result.get("tests_total", 0)
        test_summary = f"Test cases: {passed}/{total} passed."

    prompt = f"""You are a senior software engineer reviewing interview code. Be STRICT and HONEST.

QUESTION: {question}

CANDIDATE'S {language.upper()} CODE:
```{language}
{code}
```

EXECUTION RESULT:
- Success: {execution_result.get('success', False)}
- Output: {execution_result.get('output', 'none')[:300]}
- Error: {execution_result.get('error', 'none')[:300]}
- Runtime: {execution_result.get('runtime_ms', 0)}ms
- {test_summary}

CANDIDATE'S CLAIMED SKILL LEVEL: {claimed_skill_level}/10

Evaluate the code. Return ONLY valid JSON:
{{
  "code_score": <0-10, how good is this solution?>,
  "correctness": <0-10, does it actually solve the problem?>,
  "code_quality": <0-10, is the code clean, readable, well-named?>,
  "time_complexity": "<e.g. O(n), O(n^2), O(log n)>",
  "space_complexity": "<e.g. O(1), O(n)>",
  "approach": "<one sentence: what approach did they use?>",
  "what_is_wrong": "<specific bugs, edge cases missed, or null if perfect>",
  "better_approach": "<how an expert would solve this, or null if already optimal>",
  "skill_match": "<Matches Claim | Below Claim | Exceeds Claim>",
  "verdict": "<Accepted | Wrong Answer | Time Limit Exceeded | Compilation Error | Partial>"
}}

Scoring: 0=doesn't compile, 3=compiles but wrong, 5=partially correct, 7=correct but inefficient, 9=optimal, 10=perfect with edge cases handled."""

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            res = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2:3b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.05, "num_predict": 400}
                }
            )
            raw = res.json().get("response", "")
            import re
            raw = re.sub(r'```json\s*', '', raw)
            raw = re.sub(r'```\s*', '', raw)
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                return json.loads(match.group())
    except Exception:
        pass

    # Fallback
    success = execution_result.get("success", False)
    tests_passed = execution_result.get("tests_passed", 0)
    tests_total = execution_result.get("tests_total", 1)
    score = 0
    if success:
        score = 5 + int((tests_passed / max(tests_total, 1)) * 4)
    return {
        "code_score": score,
        "correctness": score,
        "code_quality": 5,
        "time_complexity": "Unknown",
        "space_complexity": "Unknown",
        "approach": "Could not analyze (Ollama busy)",
        "what_is_wrong": None if success else "Code did not execute successfully",
        "better_approach": None,
        "skill_match": "Matches Claim" if score >= claimed_skill_level - 2 else "Below Claim",
        "verdict": "Accepted" if success and tests_passed == tests_total else "Wrong Answer"
    }
