from app.jd_analyzer import analyze_job_description, extract_experience_years


def test_analyze_job_description():
    jd = """
    Requirements:
    - Python, SQL and FastAPI
    - 2+ years of experience
    Preferred:
    - Docker and AWS
    Bachelor's degree preferred.
    """

    result = analyze_job_description(jd)

    assert "python" in result.required_skills
    assert "sql" in result.required_skills
    assert "fastapi" in result.required_skills
    assert "docker" in result.preferred_skills
    assert "aws" in result.preferred_skills
    assert result.experience_years == 2.0
    assert "bachelor" in result.education


def test_extract_experience_years():
    assert extract_experience_years("At least 3 years of experience") == 3.0
