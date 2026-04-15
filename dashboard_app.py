"""
MCT PathAI — Job Intelligence Pipeline Dashboard
Powered by MCTechnology LLC
"""

from __future__ import annotations

import os
import json

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv
from supabase import Client, create_client

# ── Config ──────────────────────────────────────────────────────────────────
load_dotenv()

st.set_page_config(
    page_title="MCT PathAI — Job Intelligence",
    page_icon="🎯",
    layout="wide",
)

# ── Constants ────────────────────────────────────────────────────────────────
GRADE_ORDER = ["A+", "A", "B+", "B", "C+", "C", "D", "F"]

GRADE_COLORS: dict[str, str] = {
    "A+": "background-color: #d4edda; color: #155724;",
    "A":  "background-color: #d4edda; color: #155724;",
    "B+": "background-color: #cce5ff; color: #004085;",
    "B":  "background-color: #cce5ff; color: #004085;",
    "C+": "background-color: #e2e3e5; color: #383d41;",
    "C":  "background-color: #e2e3e5; color: #383d41;",
    "D":  "background-color: #e2e3e5; color: #383d41;",
    "F":  "background-color: #e2e3e5; color: #383d41;",
}

DISPLAY_COLS = [
    "company",
    "title",
    "career_ops_grade",
    "career_ops_score",
    "scraper_score",
    "evaluated_at",
]


# ── Supabase client ──────────────────────────────────────────────────────────
def get_client() -> Client | None:
    url = ""
    key = ""
    # Try Streamlit secrets first
    try:
        url = st.secrets.get("SUPABASE_URL", "")
        key = st.secrets.get("SUPABASE_KEY", "")
    except Exception:
        pass
    # Fallback to environment
    if not url:
        url = os.environ.get("SUPABASE_URL", "")
    if not key:
        key = os.environ.get("SUPABASE_KEY", "")

    if not url or not key:
        st.error(
            "**Supabase credentials not found.**\n\n"
            "Please set `SUPABASE_URL` and `SUPABASE_KEY` in your `.env` file "
            "or in `.streamlit/secrets.toml`."
        )
        return None

    return create_client(url, key)


# ── Cached queries ───────────────────────────────────────────────────────────
@st.cache_data(ttl=1800)
def fetch_jobs_with_evals() -> pd.DataFrame:
    client = get_client()
    if client is None:
        return pd.DataFrame()

    try:
        result = (
            client.table("jobs")
            .select(
                "id, url, company, title, career_ops_grade, career_ops_score, "
                "scraper_score, evaluated_at, visa_flag, "
                "evaluations(final_score, report_markdown)"
            )
            .execute()
        )
        rows = result.data or []

        # Flatten nested evaluations (take first eval per job)
        flat: list[dict] = []
        for r in rows:
            evals = r.pop("evaluations", None) or []
            first_eval = evals[0] if evals else {}
            flat.append({**r, **first_eval})

        return pd.DataFrame(flat)

    except Exception as exc:
        st.warning(f"Could not load jobs: {exc}")
        return pd.DataFrame()


@st.cache_data(ttl=1800)
def fetch_metrics() -> dict[str, int]:
    client = get_client()
    if client is None:
        return {}

    metrics: dict[str, int] = {}

    try:
        res = client.table("jobs").select("id", count="exact").execute()
        metrics["total_jobs"] = res.count or 0
    except Exception as exc:
        st.warning(f"Metrics (total jobs): {exc}")
        metrics["total_jobs"] = 0

    try:
        res = (
            client.table("jobs")
            .select("id", count="exact")
            .not_.is_("career_ops_grade", "null")
            .execute()
        )
        metrics["total_evaluated"] = res.count or 0
    except Exception as exc:
        st.warning(f"Metrics (evaluated): {exc}")
        metrics["total_evaluated"] = 0

    try:
        res = (
            client.table("jobs")
            .select("id", count="exact")
            .in_("career_ops_grade", ["A+", "A"])
            .execute()
        )
        metrics["top_matches"] = res.count or 0
    except Exception as exc:
        st.warning(f"Metrics (top matches): {exc}")
        metrics["top_matches"] = 0

    try:
        res = (
            client.table("resumes")
            .select("id", count="exact")
            .eq("status", "generated")
            .execute()
        )
        metrics["resumes_generated"] = res.count or 0
    except Exception as exc:
        # resumes table may not exist yet
        metrics["resumes_generated"] = 0

    return metrics


@st.cache_data(ttl=1800)
def fetch_resumes() -> pd.DataFrame:
    client = get_client()
    if client is None:
        return pd.DataFrame()

    try:
        result = (
            client.table("resumes")
            .select(
                "id, match_score, status, generated_at, tailored_resume_md, "
                "jobs(company, title)"
            )
            .eq("status", "generated")
            .execute()
        )
        rows = result.data or []

        flat: list[dict] = []
        for r in rows:
            job = r.pop("jobs", None) or {}
            flat.append({**r, **job})

        return pd.DataFrame(flat)

    except Exception as exc:
        st.warning(f"Could not load resumes: {exc}")
        return pd.DataFrame()


# ── Resume generation ───────────────────────────────────────────────────────────────
RESUME_AI_URL = os.environ.get(
    "RESUME_AI_URL", "https://resume-agent-production-ea2e.up.railway.app"
)


def generate_resume(job_info: dict, base_resume: str) -> dict:
    """Call ResumeAI API to generate a tailored resume."""
    try:
        # Try with job_description at top level (not nested)
        payload = {
            "base_resume": base_resume,
            "company": job_info.get("company", ""),
            "title": job_info.get("title", ""),
            "job_description": job_info.get("description", ""),
        }
        st.write("Debug payload:", payload)
        response = requests.post(
            f"{RESUME_AI_URL}/api/tailor",
            json=payload,
            timeout=120,
        )
        if response.status_code == 200:
            data = response.json()
            tailored = data.get("tailored_resume") or data.get("resume") or ""
            return {"success": True, "tailored_resume": tailored}
        else:
            return {"success": False, "error": f"API error: {response.status_code} - {response.text[:200]}"}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def save_resume_to_supabase(
    job_id: str,
    resume_md: str,
    match_score: float = 0.0,
) -> bool:
    """Save generated resume to Supabase resumes table."""
    client = get_client()
    if client is None:
        st.error("Supabase client is None - check credentials")
        return False

    if not job_id:
        st.error(f"Empty job_id passed to save_resume_to_supabase")
        return False

    try:
        result = client.table("resumes").insert({
            "job_id": job_id,
            "tailored_resume_md": resume_md,
            "match_score": match_score,
            "status": "generated",
        }).execute()
        return True
    except Exception as exc:
        st.error(f"Save failed: {exc}")
        return False


# ── Styling ──────────────────────────────────────────────────────────────────
def _row_style(row: pd.Series) -> list[str]:
    grade = str(row.get("career_ops_grade", ""))
    css = GRADE_COLORS.get(grade, "")
    return [css] * len(row)


def style_dataframe(df: pd.DataFrame) -> pd.io.formats.style.Styler:
    return df.style.apply(_row_style, axis=1)


# ── Header ───────────────────────────────────────────────────────────────────
st.title("🎯 MCT PathAI — Job Intelligence Pipeline")
st.caption("Powered by MCTechnology LLC")
st.divider()


# ── Metrics row ──────────────────────────────────────────────────────────────
metrics = fetch_metrics()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Jobs", metrics.get("total_jobs", 0))
col2.metric("Evaluated", metrics.get("total_evaluated", 0))
col3.metric("A / A+ Matches", metrics.get("top_matches", 0))
col4.metric("Resumes Generated", metrics.get("resumes_generated", 0))

st.divider()


# ── Sidebar filters ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")

    grade_filter: list[str] = st.multiselect(
        "Grade Filter",
        options=GRADE_ORDER,
        default=["A+", "A"],
    )

    company_search: str = st.text_input("Search Company", "")

    hide_visa_flagged: bool = st.checkbox("Hide visa-flagged jobs", value=True)

    if st.button("Refresh Data"):
        st.cache_data.clear()
        st.rerun()

    st.divider()
    st.caption("Cache TTL: 30 min")


# ── Load & filter data ───────────────────────────────────────────────────────
df = fetch_jobs_with_evals()

if df.empty:
    st.info("No job data found. Run the sync pipeline to populate Supabase.")
    st.stop()

# Apply grade filter
if grade_filter:
    df = df[df["career_ops_grade"].isin(grade_filter)]

# Apply company search
if company_search:
    mask = df["company"].str.contains(company_search, case=False, na=False)
    df = df[mask]

# Hide visa-flagged
if hide_visa_flagged and "visa_flag" in df.columns:
    df = df[df["visa_flag"].ne(True)]


# ── Main jobs table ──────────────────────────────────────────────────────────
st.subheader(f"Jobs ({len(df)} results)")

display_cols = [c for c in DISPLAY_COLS if c in df.columns]
display_df = df[display_cols].copy()

# Format score columns
for col in ("career_ops_score", "scraper_score", "final_score"):
    if col in display_df.columns:
        display_df[col] = display_df[col].apply(
            lambda v: f"{float(v):.2f}" if pd.notna(v) and v != "" else ""
        )

st.dataframe(
    style_dataframe(display_df),
    use_container_width=True,
    hide_index=True,
)


# ── Generate Resume ──────────────────────────────────────────────────────────
st.divider()
st.subheader("Generate Tailored Resume")

# Load base resume from GitHub API (scraper-2.0-agent repo)
@st.cache_data(ttl=3600)
def fetch_base_resume() -> str:
    """Fetch base resume from scraper-2.0-agent repo."""
    gh_pat = ""
    # Try Streamlit secrets first, then environment
    try:
        gh_pat = st.secrets.get("GH_PAT", "")
    except Exception:
        pass
    if not gh_pat:
        gh_pat = os.environ.get("GH_PAT", "")
    if not gh_pat:
        st.warning("GH_PAT not configured in Streamlit secrets or environment")
        return ""
    try:
        url = "https://raw.githubusercontent.com/Rajsai1609/scraper-2.0-agent/main/data/resume.txt"
        headers = {"Authorization": f"token {gh_pat}"}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.text
        elif r.status_code == 401:
            st.error("GH_PAT authentication failed. Check your token.")
        else:
            st.warning(f"Failed to fetch resume: {r.status_code}")
    except Exception as exc:
        st.warning(f"Error fetching resume: {exc}")
    return ""

base_resume = fetch_base_resume()

col_left, col_right = st.columns([2, 1])

with col_left:
    # Job selector for resume generation
    job_options = df.apply(
        lambda r: f"{r.get('company', '?')} — {r.get('title', '?')} ({r.get('career_ops_grade', '?')})",
        axis=1,
    ).tolist()
    selected_job_for_resume = st.selectbox(
        "Select job to tailor resume for:",
        ["— select —"] + job_options,
        key="resume_job_select",
    )

with col_right:
    generate_btn = st.button(
        "Generate Resume",
        type="primary",
        disabled=(selected_job_for_resume == "— select —" or not base_resume),
    )

if selected_job_for_resume != "— select —" and base_resume:
    idx = job_options.index(selected_job_for_resume)
    job_row = df.iloc[idx]
    # Use report_markdown if available, otherwise fall back to title/company
    report = job_row.get("report_markdown", "") or job_row.get("title", "")
    job_info = {
        "company": job_row.get("company", ""),
        "title": job_row.get("title", ""),
        "description": (job_row.get("company", "") + " - " + job_row.get("title", ""))[:2000],
    }
    job_id = job_row.get("id", "")
    # Debug: show what job_id we're getting
    if not job_id:
        st.error(f"Job ID not found for: {job_row.get('company')} - {job_row.get('title')}")
    elif generate_btn:
        with st.spinner("Generating tailored resume..."):
            result = generate_resume(job_info, base_resume)
            if result.get("success"):
                tailored = result.get("tailored_resume", "")
                if tailored and save_resume_to_supabase(job_id, tailored, job_row.get("career_ops_score", 0)):
                    st.success("Resume generated and saved!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("Failed to save resume to database")
            else:
                st.error(f"Generation failed: {result.get('error', 'Unknown error')}")
    else:
        st.info("Select a job above and click 'Generate Resume' to create a tailored resume.")
elif not base_resume:
    st.warning("Base resume not found. Please ensure data/resume.txt exists in scraper-2.0-agent.")


# ── Job detail expander ──────────────────────────────────────────────────────
st.divider()
st.subheader("Job Detail")

if "report_markdown" in df.columns and not df.empty:
    # Build label list: "Company — Title (Grade)"
    labels = df.apply(
        lambda r: f"{r.get('company', '?')} — {r.get('title', '?')} "
                  f"({r.get('career_ops_grade', '?')})",
        axis=1,
    ).tolist()

    selected_label = st.selectbox("View full report for job:", ["— select —"] + labels)

    if selected_label and selected_label != "— select —":
        idx = labels.index(selected_label)
        row = df.iloc[idx]
        report_md = row.get("report_markdown", "")

        if report_md:
            with st.expander("Full Evaluation Report", expanded=True):
                st.markdown(report_md)
        else:
            st.info("No report markdown available for this job.")
else:
    st.info("Select grades that include evaluated jobs to see reports.")


# ── Resumes section ──────────────────────────────────────────────────────────
st.divider()
st.subheader("Generated Resumes")

resumes_df = fetch_resumes()

if resumes_df.empty:
    st.info("No generated resumes found.")
else:
    resume_display_cols = [
        c for c in ["company", "title", "match_score", "status", "generated_at"]
        if c in resumes_df.columns
    ]
    st.dataframe(
        resumes_df[resume_display_cols],
        use_container_width=True,
        hide_index=True,
    )

    # Download buttons
    for _, r in resumes_df.iterrows():
        resume_md = r.get("tailored_resume_md", "")
        if not resume_md:
            continue

        company = r.get("company", "company")
        title = r.get("title", "role")
        filename = f"resume_{company}_{title}.md".replace(" ", "_").lower()

        st.download_button(
            label=f"Download resume — {company} ({title})",
            data=resume_md,
            file_name=filename,
            mime="text/markdown",
            key=f"dl_{r.get('id', filename)}",
        )
