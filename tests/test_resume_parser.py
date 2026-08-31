from pathlib import Path

import pytest

from app.resume_parser import clean_text, extract_text


def test_clean_text():
    text = "  Python   Developer\n\n\n\n FastAPI  "
    assert clean_text(text) == "Python Developer\n\nFastAPI"


def test_unsupported_file_type(tmp_path: Path):
    resume = tmp_path / "resume.txt"
    resume.write_text("Python", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported file type"):
        extract_text(resume)


def test_missing_file():
    with pytest.raises(FileNotFoundError):
        extract_text("does-not-exist.pdf")
