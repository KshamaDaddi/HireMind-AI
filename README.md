# HireMind AI

AI-powered automatic job screening system that turns resumes and job descriptions into transparent, testable candidate-matching signals.

## Architecture

```text
Resume (PDF/DOCX)
      │
      ▼
 Resume Parser ───────────────┐
      │                       │
      ▼                       ▼
Resume Text              Skill Matching
                              │
Job Description               │
      │                       │
      ▼                       │
 JD Analyzer                  │
      │                       │
      ▼                       ▼
Structured Requirements ─→ Hybrid Matcher
                              │
                 ┌────────────┼────────────┐
                 ▼            ▼            ▼
            Skill Score  Semantic Score  Experience
                 │            │            │
                 └────────────┼────────────┘
                              ▼
                       Overall Match Score
                              │
                              ▼
                         JSON Report
```

The project is built incrementally. The core pipeline uses deterministic rules for explicit requirements and a sentence-transformer embedding model for semantic similarity. This keeps the important matching signals transparent while allowing the system to recognize relevant wording that does not exactly match the job description.

## Current Pipeline

### 1. Resume Parser

`app/resume_parser.py`

- PDF extraction with PyMuPDF
- DOCX paragraph and table extraction
- text normalization
- unsupported-file and missing-file validation

### 2. Job Description Analyzer

`app/jd_analyzer.py`

Extracts:

- required skills
- preferred / nice-to-have skills
- minimum experience in years
- common education levels

The analyzer uses deterministic rules and a controlled skill vocabulary.

### 3. Transparent Matching Baseline

`app/matcher.py`

Provides:

- required-skill coverage
- preferred-skill coverage
- matched skills
- missing required skills
- experience score
- baseline overall score

### 4. Semantic Matching

`app/semantic_matcher.py`

Uses:

- Sentence Transformers
- `all-MiniLM-L6-v2`
- normalized embeddings
- cosine similarity

The model is loaded lazily and cached so importing the module does not download the model.

### 5. Hybrid Matching

`app/hybrid_matcher.py`

Combines:

| Signal | Weight |
|---|---:|
| Explicit skill coverage | 70% |
| Semantic similarity | 15% |
| Experience match | 15% |

The result also reports matched skills and missing required skills.

### 6. Evidence-Based GenAI Explanation

`app/explainer.py`

- uses a local Ollama model when available
- sends only measurable matching evidence to the model
- instructs the model not to invent qualifications or make a hiring decision
- provides a deterministic fallback when Ollama is unavailable

Default local model: `llama3.2`.

### 7. End-to-End Screening

`app/screening_pipeline.py`

The pipeline accepts:

- a PDF/DOCX resume
- a text job description
- optional candidate experience in years

It returns a JSON-compatible report containing structured requirements and match results.

## Aesthetic Web Interface

`streamlit_app.py` provides a recruiter-style dashboard with:

- PDF/DOCX resume upload
- job-description input
- overall match score
- skill, semantic and experience metrics
- matched and missing skill evidence
- evidence-grounded explanation
- extracted requirements viewer
- JSON report download

Run it with:

```bash
streamlit run streamlit_app.py
```

For the GenAI explanation, install and run Ollama locally and make sure the configured model is available. If Ollama is unavailable, HireMind automatically uses its deterministic evidence summary.

## Run the Project

### 1. Create the environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\\Scripts\\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

The first semantic-matching run downloads the `all-MiniLM-L6-v2` model from the Sentence Transformers ecosystem.

### 3. Analyze a job description

Save the job description as `job_description.txt`:

```bash
python -m app.jd_analyzer job_description.txt
```

### 4. Screen a resume

```bash
python -m app.screening_pipeline path/to/resume.pdf job_description.txt --resume-years 1
```

For a DOCX resume:

```bash
python -m app.screening_pipeline path/to/resume.docx job_description.txt --resume-years 1
```

Example output structure:

```json
{
  "requirements": {
    "required_skills": ["python", "sql"],
    "preferred_skills": ["docker"]
  },
  "match": {
    "skill_score": 90.0,
    "semantic_score": 82.41,
    "experience_score": 100.0,
    "overall_score": 88.86,
    "matched_skills": ["python", "sql", "docker"],
    "missing_required_skills": []
  }
}
```

## Testing

Run the full test suite:

```bash
pytest
```

Semantic model tests mock the embedding model, so unit tests do not require a model download.

## Project Structure

```text
HireMind-AI/
├── app/
│   ├── __init__.py
│   ├── resume_parser.py
│   ├── jd_analyzer.py
│   ├── matcher.py
│   ├── semantic_matcher.py
│   ├── hybrid_matcher.py
│   └── screening_pipeline.py
├── tests/
│   ├── test_resume_parser.py
│   ├── test_jd_analyzer.py
│   ├── test_matcher.py
│   ├── test_semantic_matcher.py
│   └── test_hybrid_matcher.py
├── requirements.txt
└── README.md
```

## Roadmap

- [x] Resume text extraction and cleaning
- [x] Job description analysis
- [x] Transparent baseline matching
- [x] Embedding-based semantic similarity
- [x] Hybrid matching
- [x] End-to-end screening pipeline
- [ ] Better skill/entity extraction
- [x] Evidence-based GenAI explanation
- [ ] FastAPI backend
- [x] Streamlit recruiter dashboard
- [ ] End-to-end integration tests
- [ ] Docker / deployment
- [ ] CI/CD

## Design Principles

- **Transparent:** explicit skill matches and missing requirements are visible.
- **Deterministic core:** rule-based extraction remains reproducible.
- **Semantic understanding:** embeddings capture related wording beyond exact keyword matches.
- **Testable:** matching components have isolated unit tests.
- **Incremental:** advanced GenAI features are added after the core pipeline is stable.
