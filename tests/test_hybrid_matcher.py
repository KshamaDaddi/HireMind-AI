from app.hybrid_matcher import hybrid_match
from app.jd_analyzer import analyze_job_description


def test_hybrid_match_combines_scores(monkeypatch):
    monkeypatch.setattr(
        "app.hybrid_matcher.semantic_similarity",
        lambda resume, job, model_name: 80.0,
    )

    requirements = analyze_job_description(
        """
        Requirements:
        Python, SQL

        Preferred:
        Docker
        """
    )

    result = hybrid_match(
        "Python SQL Docker",
        "Python SQL Docker developer",
        requirements,
        resume_years=2,
    )

    assert result.skill_score == 100.0
    assert result.semantic_score == 80.0
    assert result.experience_score == 100.0
    assert result.overall_score == 97.0
    assert result.missing_required_skills == []
