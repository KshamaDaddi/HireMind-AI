"""Evidence-grounded candidate explanation for HireMind AI.

Uses a local Ollama model when available. The prompt contains only extracted
matching evidence so the explanation can be traced back to measurable signals.
A deterministic fallback keeps the UI usable without an LLM.
"""

from __future__ import annotations

import os
from typing import Any

import requests


DEFAULT_OLLAMA_MODEL = "llama3.2"
DEFAULT_OLLAMA_URL = "http://localhost:11434/api/generate"


def _fallback_explanation(match: dict[str, Any]) -> str:
    overall = match["overall_score"]
    matched = match.get("matched_skills", [])
    missing = match.get("missing_required_skills", [])
    skill = match["skill_score"]
    semantic = match["semantic_score"]
    experience = match["experience_score"]

    lines = [
        f"Overall match score: {overall:.1f}/100.",
        f"Explicit skill coverage is {skill:.1f}/100, semantic similarity is {semantic:.1f}/100, and experience alignment is {experience:.1f}/100.",
    ]

    if matched:
        lines.append("Matched skills: " + ", ".join(matched) + ".")
    if missing:
        lines.append("Missing required skills: " + ", ".join(missing) + ".")
    else:
        lines.append("No missing required skills were detected by the configured skill vocabulary.")

    return "\n\n".join(lines)


def _build_prompt(match: dict[str, Any]) -> str:
    return f"""You are an evidence-grounded hiring analysis assistant.

Explain the candidate-job match using ONLY the evidence below.
Do not invent qualifications, experience, projects, education, or skills.
Do not make a hiring decision or recommendation.
Do not infer protected characteristics.
Clearly distinguish measured signals from interpretation.

Evidence:
- Overall score: {match["overall_score"]}/100
- Skill score: {match["skill_score"]}/100
- Semantic similarity: {match["semantic_score"]}/100
- Experience score: {match["experience_score"]}/100
- Matched skills: {", ".join(match.get("matched_skills", [])) or "None detected"}
- Missing required skills: {", ".join(match.get("missing_required_skills", [])) or "None detected"}

Return 3 short sections:
1. Match summary
2. Evidence
3. Gaps

Keep the response concise and factual.
"""


def generate_explanation(
    match: dict[str, Any],
    *,
    model: str = DEFAULT_OLLAMA_MODEL,
    url: str = DEFAULT_OLLAMA_URL,
    timeout: int = 45,
) -> dict[str, str | bool]:
    """Generate an explanation with local Ollama, with a deterministic fallback."""
    if os.getenv("HIREMIND_DISABLE_LLM", "").lower() == "true":
        return {
            "text": _fallback_explanation(match),
            "source": "deterministic",
            "llm_used": False,
        }

    payload = {
        "model": model,
        "prompt": _build_prompt(match),
        "stream": False,
        "options": {"temperature": 0.1},
    }

    try:
        response = requests.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        text = str(data.get("response", "")).strip()
        if text:
            return {"text": text, "source": f"Ollama · {model}", "llm_used": True}
    except (requests.RequestException, ValueError, TypeError):
        pass

    return {
        "text": _fallback_explanation(match),
        "source": "deterministic fallback",
        "llm_used": False,
    }
