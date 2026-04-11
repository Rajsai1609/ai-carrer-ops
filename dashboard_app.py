"""
MCT PathAI — Job Intelligence Pipeline Dashboard
Powered by MCTechnology LLC
"""

from __future__ import annotations

import os

import pandas as pd
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
    url = os.environ.get("SUPABASE_URL", "")
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
