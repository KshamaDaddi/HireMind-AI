# HireMind AI

AI-powered automatic job screening system.

## Step 1 — Resume Parser

The first module extracts and cleans text from candidate resumes in PDF or DOCX format.

### Current workflow

```text
PDF / DOCX Resume
       ↓
Document Parser
       ↓
Text Extraction
       ↓
Text Cleaning
       ↓
Clean Resume Text
```

### Setup

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### Run the parser

```bash
python -m app.resume_parser path/to/resume.pdf
```

or:

```bash
python -m app.resume_parser path/to/resume.docx
```

### Run tests

```bash
pytest
```

## Roadmap

- Step 1: Resume text extraction and cleaning
- Step 2: Job Description analyzer
- Step 3: Resume–JD matching and scoring
- Step 4: Semantic embeddings and GenAI explanation
- Step 5: FastAPI backend
- Step 6: Streamlit dashboard
