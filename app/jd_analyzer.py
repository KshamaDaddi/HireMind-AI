"""Job-description analysis utilities for HireMind AI.

Extract structured requirements from a job description using deterministic
rules so the baseline pipeline is reproducible and easy to test.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
import re


DEFAULT_SKILLS = {
    "python", "java", "c++", "sql", "r", "javascript", "typescript",
    "html", "css", "react", "node.js", "django", "flask", "fastapi",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
    "opencv", "nlp", "machine learning", "deep learning",
    "generative ai", "genai", "llm", "large language models",
    "rag", "langchain", "docker", "kubernetes", "aws", "azure", "gcp",
    "git", "github", "rest api", "data analysis", "power bi",
    "tableau", "spark", "airflow", "mongodb", "postgresql", "mysql",
}


@dataclass(frozen=True)
class JobRequirements:
    """Structured requirements extracted from a job description."""

    required_skills: list[str]
    preferred_skills: list[str]
    experience_years: float | None
    education: list[str]


def _normalize(text: str) -> str:
    text = text.lower()
    text = text.replace("c sharp", "c#")
    text = text.replace("c plus plus", "c++")
    return re.sub(r"\s+", " ", text)


def _find_skills(text: str) -> list[str]:
    normalized = _normalize(text)
    found = []
    for skill in sorted(DEFAULT_SKILLS, key=len, reverse=True):
        pattern = rf"(?<![\w+#.]){re.escape(skill)}(?![\w+#.])"
        if re.search(pattern, normalized):
            found.append(skill)
    return sorted(set(found))


def _section(text: str, headings: tuple[str, ...]) -> str:
    pattern = r"(?is)(?:^|\n)\s*(?:" + "|".join(map(re.escape, headings)) + r")\s*:?[ \t]*\n?(.*?)(?=\n\s*[A-Z][A-Za-z /&-]{2,40}\s*:?[ \t]*\n|\Z)"
    match = re.search(pattern, text)
    return match.group(1) if match else ""


def extract_experience_years(text: str) -> float | None:
    normalized = _normalize(text)
    patterns = [
        r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s+(?:of\s+)?experience",
        r"(?:experience|exp).*?(\d+(?:\.\d+)?)\s*\+?\s*years?",
    ]
    values = []
    for pattern in patterns:
        for match in re.finditer(pattern, normalized):
            values.append(float(match.group(1)))
    return min(values) if values else None


def extract_education(text: str) -> list[str]:
    normalized = _normalize(text)
    education = []
    patterns = {
        "bachelor": r"\b(?:b\.?e\.?|b\.?tech|bachelor(?:'s)?|undergraduate)\b",
        "master": r"\b(?:m\.?e\.?|m\.?tech|master(?:'s)?|postgraduate)\b",
        "phd": r"\b(?:ph\.?d\.?|doctorate)\b",
    }
    for label, pattern in patterns.items():
        if re.search(pattern, normalized):
            education.append(label)
    return education


def analyze_job_description(text: str) -> JobRequirements:
    """Extract required/preferred skills and common requirements."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Job description must be a non-empty string.")

    required_section = _section(
        text,
        ("requirements", "required skills", "must have", "qualifications"),
    )
    preferred_section = _section(
        text,
        ("preferred", "nice to have", "good to have", "bonus skills"),
    )

    all_skills = _find_skills(text)
    required_skills = _find_skills(required_section) if required_section else all_skills
    preferred_skills = _find_skills(preferred_section)

    # A skill explicitly classified as preferred should not be counted as required.
    preferred_set = set(preferred_skills)
    required_skills = [s for s in required_skills if s not in preferred_set]

    return JobRequirements(
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        experience_years=extract_experience_years(text),
        education=extract_education(text),
    )


def requirements_to_dict(requirements: JobRequirements) -> dict:
    """Return a JSON-serializable representation."""
    return asdict(requirements)


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Analyze a job description.")
    parser.add_argument("file", help="Path to a text job description")
    args = parser.parse_args()

    description = open(args.file, encoding="utf-8").read()
    print(json.dumps(requirements_to_dict(analyze_job_description(description)), indent=2))
