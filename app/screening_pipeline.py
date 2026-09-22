"""End-to-end HireMind AI screening pipeline."""

from __future__ import annotations

from dataclasses import asdict

from app.hybrid_matcher import HybridMatchResult, hybrid_match
from app.jd_analyzer import analyze_job_description, requirements_to_dict
from app.resume_parser import extract_text


def screen_resume(
    resume_path: str,
    job_description_path: str,
    *,
    resume_years: float | None = None,
    model_name: str = "all-MiniLM-L6-v2",
) -> dict:
    """Parse a resume, analyze a JD, and return a hybrid match report."""
    resume_text = extract_text(resume_path)
    job_description = open(
        job_description_path, encoding="utf-8"
    ).read()

    requirements = analyze_job_description(job_description)
    result: HybridMatchResult = hybrid_match(
        resume_text,
        job_description,
        requirements,
        resume_years=resume_years,
        model_name=model_name,
    )

    return {
        "resume": resume_path,
        "job_description": job_description_path,
        "requirements": requirements_to_dict(requirements),
        "match": asdict(result),
    }


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="Screen a resume against a job description."
    )
    parser.add_argument("resume", help="Path to a PDF or DOCX resume")
    parser.add_argument("job_description", help="Path to a text job description")
    parser.add_argument(
        "--resume-years",
        type=float,
        default=None,
        help="Candidate experience in years, if known",
    )
    args = parser.parse_args()

    report = screen_resume(
        args.resume,
        args.job_description,
        resume_years=args.resume_years,
    )
    print(json.dumps(report, indent=2))
