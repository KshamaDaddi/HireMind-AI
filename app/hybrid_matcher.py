"""Hybrid resume-to-job matching for HireMind AI."""

from __future__ import annotations

from dataclasses import dataclass

from app.jd_analyzer import JobRequirements
from app.matcher import match_requirements
from app.semantic_matcher import semantic_similarity


@dataclass(frozen=True)
class HybridMatchResult:
    skill_score: float
    semantic_score: float
    experience_score: float
    overall_score: float
    matched_skills: list[str]
    missing_required_skills: list[str]


def hybrid_match(
    resume_text: str,
    job_description: str,
    requirements: JobRequirements,
    *,
    resume_years: float | None = None,
    model_name: str = "all-MiniLM-L6-v2",
) -> HybridMatchResult:
    """Combine transparent skill/experience signals with embeddings.

    Weighting:
    - 70% explicit skill coverage
    - 15% semantic similarity
    - 15% experience match
    """
    baseline = match_requirements(
        resume_text,
        requirements.required_skills,
        requirements.preferred_skills,
        resume_years=resume_years,
        required_years=requirements.experience_years,
    )
    semantic_score = semantic_similarity(
        resume_text,
        job_description,
        model_name=model_name,
    )
    overall_score = (
        baseline.skill_score * 0.70
        + semantic_score * 0.15
        + baseline.experience_score * 0.15
    )

    return HybridMatchResult(
        skill_score=baseline.skill_score,
        semantic_score=semantic_score,
        experience_score=baseline.experience_score,
        overall_score=round(overall_score, 2),
        matched_skills=baseline.matched_skills,
        missing_required_skills=baseline.missing_required_skills,
    )
