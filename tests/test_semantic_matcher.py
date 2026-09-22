import pytest

from app.semantic_matcher import semantic_similarity


def test_empty_resume_rejected():
    with pytest.raises(ValueError):
        semantic_similarity("", "Python developer")


def test_empty_job_description_rejected():
    with pytest.raises(ValueError):
        semantic_similarity("Python developer", "")


def test_similarity_uses_model(monkeypatch):
    class FakeModel:
        def encode(self, texts, normalize_embeddings=True):
            assert normalize_embeddings is True
            return [[1.0, 0.0], [1.0, 0.0]]

    monkeypatch.setattr(
        "app.semantic_matcher._load_model",
        lambda model_name: FakeModel(),
    )

    assert semantic_similarity("Python", "Python") == 100.0
