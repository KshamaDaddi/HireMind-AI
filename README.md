# HireMind AI

AI-powered automatic job screening system that turns resumes and job descriptions into transparent, testable candidate-matching signals.

## Architecture

```text
Resume (PDF/DOCX) ──→ Resume Parser ──→ Clean Resume Text ──┐
                                                            ├─→ Matching ─→ Candidate Score
Job Description ────→ JD Analyzer ───→ Structured Requirements ─┘
```

The project is being built incrementally. The baseline deliberately uses deterministic Python logic first; semantic embeddings and GenAI explanations will be added only after the core pipeline is reliable and testable.

## Implemented

### Step 1 — Resume Parser

- PDF extraction with PyMuPDF
- DOCX paragraph and table extraction
- text normalization
- unsupported-file and missing-file validation
- pytest coverage for core behavior

### Step 2 — Job Description Analyzer

`app/jd_analyzer.py` extracts:

- required skills
- preferred / nice-to-have skills
- minimum experience in years
- common education levels

The analyzer uses a controlled skill vocabulary and deterministic rules, which makes the output reproducible and easy to test.

### Step 3 — Transparent Matching Baseline

`app/matcher.py` compares resume text against structured job requirements.

Current signals:

- required-skill coverage
- preferred-skill coverage
- explicit skill matches
- experience requirement
- overall weighted score
- missing required skills

This is a **baseline matcher**, not yet a true semantic model. Step 4 will replace the keyword-overlap component with embedding-based similarity.

## Project Structure

```text
HireMind-AI/
├── app/
│   ├── __init__.py
│   ├── resume_parser.py
│   ├── jd_analyzer.py
│   └── matcher.py
├── tests/
│   ├── test_resume_parser.py
│   ├── test_jd_analyzer.py
│   └── test_matcher.py
├── requirements.txt
└── README.md
```

## Setup

```bash
python -m venv .venv

# Windows PowerShell
.venv\\Scripts\\Activate.ps1

pip install -r requirements.txt
```

## Run the resume parser

```bash
python -m app.resume_parser path/to/resume.pdf
```

or:

```bash
python -m app.resume_parser path/to/resume.docx
```

## Run the job-description analyzer

Save a job description as a text file, then:

```bash
python -m app.jd_analyzer path/to/job_description.txt
```

## Run tests

```bash
pytest
```

## Roadmap

- [x] Resume text extraction and cleaning
- [x] Job description analysis
- [x] Transparent baseline matching
- [ ] Embedding-based semantic similarity
- [ ] Skill/entity extraction improvements
- [ ] Evidence-based GenAI explanation
- [ ] FastAPI backend
- [ ] Streamlit recruiter dashboard
- [ ] End-to-end integration tests
- [ ] Docker / deployment
