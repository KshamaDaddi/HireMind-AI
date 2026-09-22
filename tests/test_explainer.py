from app.explainer import generate_explanation


def test_deterministic_explanation_contains_evidence(monkeypatch):
    monkeypatch.setenv("HIREMIND_DISABLE_LLM", "true")

    result = generate_explanation(
        {
            "skill_score": 80.0,
            "semantic_score": 75.0,
            "experience_score": 100.0,
            "overall_score": 84.25,
            "matched_skills": ["python", "sql"],
            "missing_required_skills": ["docker"],
        }
    )

    assert result["llm_used"] is False
    assert "python" in result["text"]
    assert "docker" in result["text"]
    assert "84.2" in result["text"]
