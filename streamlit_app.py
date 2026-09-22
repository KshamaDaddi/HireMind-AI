"""HireMind AI — polished Streamlit interface."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import streamlit as st

from app.explainer import generate_explanation
from app.hybrid_matcher import hybrid_match
from app.jd_analyzer import analyze_job_description, requirements_to_dict
from app.resume_parser import extract_text


st.set_page_config(
    page_title="HireMind AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #f7f8fc; }
.block-container { max-width: 1320px; padding-top: 2rem; padding-bottom: 3rem; }
.hero { padding: 2rem 2.2rem; border-radius: 24px; background: linear-gradient(135deg, #111827 0%, #273449 100%); color: white; margin-bottom: 1.5rem; box-shadow: 0 16px 40px rgba(15,23,42,.12); }
.hero h1 { font-family: 'Space Grotesk', sans-serif; font-size: 2.4rem; margin: 0 0 .35rem; letter-spacing: -.04em; }
.hero p { margin: 0; color: #cbd5e1; font-size: 1rem; }
.section-title { font-family: 'Space Grotesk', sans-serif; font-size: 1.2rem; font-weight: 700; color: #111827; margin: 1.25rem 0 .65rem; }
.card, .score-card { background: white; border: 1px solid #e7eaf0; border-radius: 18px; padding: 1.15rem 1.25rem; box-shadow: 0 8px 24px rgba(15,23,42,.05); }
.score-card { text-align: center; border-radius: 22px; padding: 1.4rem; }
.score-number { font-family: 'Space Grotesk', sans-serif; font-size: 3.7rem; line-height: 1; font-weight: 700; color: #111827; }
.score-label { color: #64748b; margin-top: .45rem; font-size: .9rem; }
.pill { display:inline-block; padding:.42rem .72rem; margin:.2rem .25rem .2rem 0; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:.82rem; font-weight:600; }
.pill-missing { background:#fff1f2; color:#be123c; }
.small-muted { color:#64748b; font-size:.82rem; }
div[data-testid="stMetric"] { background:white; border:1px solid #e7eaf0; border-radius:16px; padding:1rem; }
button[kind="primary"] { border-radius:12px; min-height:3rem; font-weight:700; }
[data-testid="stSidebar"] { background:#111827; }
[data-testid="stSidebar"] * { color:#e5e7eb !important; }
</style>
""",
    unsafe_allow_html=True,
)

if "result" not in st.session_state:
    st.session_state.result = None
if "explanation" not in st.session_state:
    st.session_state.explanation = None

st.markdown(
    """
<div class="hero">
  <h1>✦ HireMind AI</h1>
  <p>Evidence-grounded resume intelligence for transparent candidate–job matching.</p>
</div>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### HIREMIND")
    st.caption("AI recruitment intelligence")
    st.divider()
    st.markdown("**Pipeline**")
    for item in [
        "01 · Resume parsing",
        "02 · Requirement extraction",
        "03 · Skill matching",
        "04 · Semantic matching",
        "05 · Evidence explanation",
    ]:
        st.markdown(item)
    st.divider()
    st.caption("Local-first • Testable • Transparent")

left, right = st.columns([1, 1], gap="large")
with left:
    st.markdown('<div class="section-title">Candidate resume</div>', unsafe_allow_html=True)
    resume_file = st.file_uploader("Upload PDF or DOCX", type=["pdf", "docx"])
    resume_years = st.number_input(
        "Experience (years)", min_value=0.0, max_value=50.0, value=0.0, step=0.5
    )

with right:
    st.markdown('<div class="section-title">Job description</div>', unsafe_allow_html=True)
    job_description = st.text_area(
        "Paste the role description",
        height=250,
        placeholder="Paste requirements, responsibilities, preferred skills, experience and qualifications...",
        label_visibility="collapsed",
    )

st.markdown('<div class="section-title">Analysis</div>', unsafe_allow_html=True)

if st.button("Analyze candidate  →", type="primary", use_container_width=True):
    if resume_file is None:
        st.error("Upload a PDF or DOCX resume first.")
    elif not job_description.strip():
        st.error("Paste a job description first.")
    else:
        suffix = Path(resume_file.name).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
            temp.write(resume_file.getbuffer())
            resume_path = temp.name
        try:
            with st.spinner("Parsing, embedding and matching…"):
                resume_text = extract_text(resume_path)
                requirements = analyze_job_description(job_description)
                result = hybrid_match(
                    resume_text,
                    job_description,
                    requirements,
                    resume_years=resume_years if resume_years > 0 else None,
                )
                match = {
                    "skill_score": result.skill_score,
                    "semantic_score": result.semantic_score,
                    "experience_score": result.experience_score,
                    "overall_score": result.overall_score,
                    "matched_skills": result.matched_skills,
                    "missing_required_skills": result.missing_required_skills,
                }
                st.session_state.result = {
                    "resume_name": resume_file.name,
                    "requirements": requirements_to_dict(requirements),
                    "match": match,
                }
                st.session_state.explanation = generate_explanation(match)
        except Exception as exc:
            st.error(f"Analysis failed: {exc}")
        finally:
            Path(resume_path).unlink(missing_ok=True)

result = st.session_state.result
if result:
    match = result["match"]
    st.divider()
    st.markdown('<div class="section-title">Match overview</div>', unsafe_allow_html=True)
    score_col, metrics_col = st.columns([1, 2.5], gap="large")

    with score_col:
        st.markdown(
            f'<div class="score-card"><div class="score-number">{match["overall_score"]:.0f}</div><div class="score-label">OVERALL MATCH / 100</div></div>',
            unsafe_allow_html=True,
        )

    with metrics_col:
        a, b, c = st.columns(3)
        a.metric("Skill coverage", f'{match["skill_score"]:.1f}/100')
        b.metric("Semantic match", f'{match["semantic_score"]:.1f}/100')
        c.metric("Experience", f'{match["experience_score"]:.1f}/100')

    st.markdown('<div class="section-title">Skills evidence</div>', unsafe_allow_html=True)
    skills_col, gaps_col = st.columns(2, gap="large")

    with skills_col:
        matched = match["matched_skills"]
        pills = "".join(f'<span class="pill">✓ {skill}</span>' for skill in matched)
        body = pills or '<span class="small-muted">No configured skills detected.</span>'
        st.markdown(f'<div class="card"><strong>Matched skills</strong><br>{body}</div>', unsafe_allow_html=True)

    with gaps_col:
        missing = match["missing_required_skills"]
        pills = "".join(f'<span class="pill pill-missing">! {skill}</span>' for skill in missing)
        body = pills or '<span class="small-muted">None detected.</span>'
        st.markdown(f'<div class="card"><strong>Missing required skills</strong><br>{body}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Evidence-grounded explanation</div>', unsafe_allow_html=True)
    explanation = st.session_state.explanation or {}
    st.markdown(
        f'<div class="card"><span class="small-muted">Generated by {explanation.get("source", "unknown")}</span><br><br>{str(explanation.get("text", "")).replace(chr(10), "<br><br>")}</div>',
        unsafe_allow_html=True,
    )

    with st.expander("View extracted requirements"):
        st.json(result["requirements"])

    st.download_button(
        "Download analysis JSON",
        data=json.dumps(result, indent=2),
        file_name="hiremind_analysis.json",
        mime="application/json",
    )
else:
    st.markdown(
        '<div class="card"><strong>Ready to screen.</strong><br><span class="small-muted">Upload a resume, paste a job description, and run the analysis to see transparent matching evidence.</span></div>',
        unsafe_allow_html=True,
    )
