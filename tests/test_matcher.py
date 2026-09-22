from app.matcher import match_requirements


def test_match_requirements():
    result = match_requirements(
        "Python developer with SQL and FastAPI experience",
        ["python", "sql", "fastapi"],
        ["docker"],
        resume_years=2,
        required_years=2,
    )

    assert result.overall_score > 60
    assert result.matched_skills == ["fastapi", "python", "sql"]
    assert result.missing_required_skills == []


def test_missing_required_skills():
    result = match_requirements("Python developer", ["python", "pytorch"])

    assert result.missing_required_skills == ["pytorch"]
    assert result.experience_score == 0.0
