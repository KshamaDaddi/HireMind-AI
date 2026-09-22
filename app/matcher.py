"""Deterministic baseline resume-to-job matching for HireMind AI."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MatchResult:
    skill_score: float
    semantic_score: float
    experience_score: float
    overall_score: float
    matched_skills: list[str]
    missing_required_skills: list[str]


def _score_experience(
    resume_years: float | None, required_years: float | None
) -> float:
    if required_years is None:
        return 1.0
    if resume_years is None:
        return 0.0
    if required_years <= 0:
        return 1.0
    return min(resume_years / required_years, 1.0)


def match_requirements(
    resume_text: str,
    required_skills: list[str],
    preferred_skills: list[str] | None = None,
    *,
    resume_years: float | None = None,
    required_years: float | None = None,
) -> MatchResult:
    """Score explicit skill overlap and text overlap.

    This is the transparent baseline. It intentionally does not use an LLM.
    """
    if not isinstance(resume_text, str):
        raise TypeError("resume_text must be a string.")

    preferred_skills = preferred_skills or []
    resume_lower = resume_text.lower()

    required = sorted(set(required_skills))
    preferred = sorted(set(preferred_skills))
    matched_required = [s for s in required if s.lower() in resume_lower]
    matched_preferred = [s for s in preferred if s.lower() in resume_lower]

    if required:
        required_score = len(matched_required) / len(required)
    else:
        required_score = 1.0

    preferred_score = (
        len(matched_preferred) / len(preferred) if preferred else 1.0
    )
    skill_score = (required_score * 0.8 + preferred_score * 0.2) * 100

    resume_tokens = set(resume_lower.split())
    job_tokens = set(s.lower() for s in required + preferred)
    semantic_score = (
        len(resume_tokens & job_tokens) / len(job_tokens) * 100
        if job_tokens
        else 100.0
    )

    experience_score = _score_experience(resume_years, required_years) * 100
    overall_score = (
        required_score * 0.60
        + preferred_score * 0.10
        + semantic_score / 100 * 0.15
        + experience_score / 100 * 0.15
    ) * 100

    return MatchResult(
        skill_score=round(skill_score, 2),
        semantic_score=round(semantic_score, 2),
        experience_score=round(experience_score, 2),
        overall_score=round(overall_score, 2),
        matched_skills=sorted(set(matched_required + matched_preferred)),
        missing_required_skills=sorted(set(required) - set(matched_required)),
    )
