"""
MCT PathAI — Job Intelligence Dashboard
Powered by MCTechnology LLC

Data sources:
  scraped_jobs      — raw jobs from scraper-2.0 (Supabase)
  student_job_scores — per-student fit scores (Supabase)
  students          — student profiles (Supabase)
"""

from __future__ import annotations

import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv
from supabase import Client, create_client

# ── Bootstrap ────────────────────────────────────────────────────────────────
load_dotenv()

st.set_page_config(
    page_title="MCT PathAI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
button[kind="header"] {
    display: none !important;
}
[data-testid="collapsedControl"] {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
    width: 0 !important;
    height: 0 !important;
}
#MainMenu {
    visibility: hidden !important;
}
section[data-testid="stSidebar"] {
    min-width: 280px !important;
    max-width: 280px !important;
    background-color: #0f172a !important;
}
section[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar helpers (must be defined before sidebar renders) ──────────────────
@st.cache_data(ttl=300)
def _sidebar_student_names() -> list[str]:
    """Fetch student names for sidebar dropdown. Cached 5 min."""
    _url = _key = ""
    try:
        _url = st.secrets.get("SUPABASE_URL", "")
        _key = st.secrets.get("SUPABASE_KEY", "")
    except Exception:
        pass
    _url = _url or os.environ.get("SUPABASE_URL", "")
    _key = _key or os.environ.get("SUPABASE_KEY", "")
    if not _url or not _key:
        return []
    try:
        _c = create_client(_url, _key)
        _r = _c.table("students").select("name").order("name").execute()
        return [row["name"] for row in (_r.data or [])]
    except Exception:
        return []


# ── Sidebar ────────────────────────────────────────────────────────────────────
selected_student_id: str | None = None
selected_student_name: str = "All Students"

with st.sidebar:
    st.markdown("### 👤 Student View")

    _dynamic_names = _sidebar_student_names()
    _student_options = ["All Students"] + _dynamic_names

    st.markdown("**View jobs for:**")
    chosen = st.selectbox("", options=_student_options, key="student_select")
    selected_student_name = chosen if chosen != "All Students" else "All Students"

    st.markdown("---")
    st.markdown("### 🔍 Filters")

    grade_filter: list[str] = st.multiselect(
        "Score Filter",
        options=["A+", "A", "B+", "B", "C+", "C", "D", "F"],
        default=["A+", "A"],
    )
    company_search: str = st.text_input(
        "Search Company",
        placeholder="e.g. Google",
    )
    hide_visa_flagged: bool = st.checkbox(
        "Hide visa-flagged jobs",
        value=True,
    )

    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.caption("Cache TTL: 30 min")
    st.caption("Powered by MCTechnology LLC")


# ── Constants ─────────────────────────────────────────────────────────────────
GRADE_ORDER = ["A+", "A", "B+", "B", "C+", "C", "D", "F"]

GRADE_PALETTE: dict[str, str] = {
    "A+": "#22c55e", "A":  "#4ade80",
    "B+": "#3b82f6", "B":  "#60a5fa",
    "C+": "#94a3b8", "C":  "#cbd5e1",
    "D":  "#f97316", "F":  "#ef4444",
}

# scraper_score thresholds that map to letter grades
_GRADE_THRESHOLDS: list[tuple[float, str]] = [
    (0.70, "A+"),
    (0.60, "A"),
    (0.50, "B+"),
    (0.40, "B"),
    (0.30, "C+"),
    (0.20, "C"),
    (0.10, "D"),
    (0.00, "F"),
]


def _score_to_grade(score: float) -> str:
    """Convert a scraper_score [0,1] to a letter grade."""
    for threshold, grade in _GRADE_THRESHOLDS:
        if score >= threshold:
            return grade
    return "F"


def _fit_score_to_grade(score_pct: float) -> tuple[str, str]:
    """Convert fit_score percentage [0,100] to (grade, badge_emoji)."""
    _BADGE = {"A+": "🟢", "A": "🔵", "B+": "🟣", "B": "🟠"}
    grade = _score_to_grade(score_pct / 100)
    badge = _BADGE.get(grade, "⚪")
    return grade, badge


# ── Supabase client ───────────────────────────────────────────────────────────
def get_client() -> Client | None:
    url = key = ""
    try:
        url = st.secrets.get("SUPABASE_URL", "")
        key = st.secrets.get("SUPABASE_KEY", "")
    except Exception:
        pass
    if not url:
        url = os.environ.get("SUPABASE_URL", "")
    if not key:
        key = os.environ.get("SUPABASE_KEY", "")
    if not url or not key:
        st.error("Supabase credentials missing. Set SUPABASE_URL and SUPABASE_KEY.")
        return None
    return create_client(url, key)


# ── Data fetchers ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_students() -> list[dict]:
    client = get_client()
    if client is None:
        return []
    try:
        result = client.table("students").select("id, name").order("name").execute()
        return result.data or []
    except Exception:
        return []


@st.cache_data(ttl=1800)
def fetch_scraped_jobs() -> pd.DataFrame:
    """Fetch all jobs from the scraped_jobs table."""
    client = get_client()
    if client is None:
        return pd.DataFrame()
    try:
        result = (
            client.table("scraped_jobs")
            .select(
                "id, url, company, title, location, scraper_score, "
                "visa_flag, job_category, work_mode, experience_level, "
                "h1b_sponsor, opt_friendly, is_entry_eligible, fetched_at"
            )
            .execute()
        )
        rows = result.data or []
        if not rows:
            return pd.DataFrame()
        df = pd.DataFrame(rows)
        if "id" in df.columns:
            df = df.drop_duplicates(subset="id")
        if "url" in df.columns:
            df = df.drop_duplicates(subset="url")
        # Derive letter grade from scraper_score
        if "scraper_score" in df.columns:
            df["grade"] = df["scraper_score"].apply(
                lambda v: _score_to_grade(float(v)) if pd.notna(v) else "F"
            )
        return df
    except Exception as exc:
        st.warning(f"Could not load scraped jobs: {exc}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def fetch_student_jobs(student_id: str, min_score: float = 0.4, limit: int = 500) -> pd.DataFrame:
    """
    Fetch personalized jobs for a student.

    1. Pull fit scores from student_job_scores (Supabase).
    2. Fetch matching job details from scraped_jobs.
    3. Merge and return.
    """
    client = get_client()
    if client is None:
        return pd.DataFrame()
    try:
        # Step 1 — student scores
        scores_res = (
            client.table("student_job_scores")
            .select("job_id, fit_score, skill_score, semantic_score")
            .eq("student_id", student_id)
            .gte("fit_score", min_score)
            .order("fit_score", desc=True)
            .limit(limit)
            .execute()
        )
        scores = scores_res.data or []
        if not scores:
            return pd.DataFrame()

        scores_df = pd.DataFrame(scores)
        scores_df["fit_score"] = (scores_df["fit_score"] * 100).round(1)

        # Step 2 — job details from scraped_jobs
        job_ids = scores_df["job_id"].tolist()
        jobs_res = (
            client.table("scraped_jobs")
            .select(
                "id, url, company, title, location, visa_flag, "
                "job_category, work_mode, scraper_score"
            )
            .in_("id", job_ids)
            .execute()
        )
        jobs = jobs_res.data or []
        if not jobs:
            return pd.DataFrame()

        jobs_df = pd.DataFrame(jobs)

        # Step 3 — merge on job_id / id
        df = scores_df.merge(jobs_df, left_on="job_id", right_on="id", how="inner")

        # Deduplicate by URL (keep highest fit_score per URL)
        if "url" in df.columns:
            df = df.sort_values("fit_score", ascending=False).drop_duplicates(subset="url")

        # USA filter — scraped_jobs already has is_usa_job; filter on location as fallback
        if "location" in df.columns:
            _USA_KEYWORDS = [
                "United States", "USA", " US ",
                "Remote", "Anywhere", "Hybrid",
                "Alabama", "Alaska", "Arizona", "Arkansas", "California",
                "Colorado", "Connecticut", "Delaware", "Florida", "Georgia",
                "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas",
                "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts",
                "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana",
                "Nebraska", "Nevada", "New Hampshire", "New Jersey",
                "New Mexico", "New York", "North Carolina", "North Dakota",
                "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island",
                "South Carolina", "South Dakota", "Tennessee", "Texas",
                "Utah", "Vermont", "Virginia", "Washington", "West Virginia",
                "Wisconsin", "Wyoming",
                ", CA", ", NY", ", WA", ", TX", ", GA",
                ", FL", ", IL", ", MA", ", VA", ", CO",
            ]
            _USA_PATTERN = "|".join(_USA_KEYWORDS)
            df = df[
                df["location"].str.contains(_USA_PATTERN, case=False, na=False)
                | df["location"].isna()
            ]

        # Enforce minimum score
        df = df[df["fit_score"] >= 40]
        return df.reset_index(drop=True)

    except Exception as exc:
        st.warning(f"Could not load student jobs: {exc}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def fetch_student_metrics(student_id: str, min_score: float = 0.4) -> dict:
    client = get_client()
    if client is None:
        return {"total_jobs": 0, "top_score": 0}
    try:
        count_res = (
            client.table("student_job_scores")
            .select("id", count="exact")
            .eq("student_id", student_id)
            .gte("fit_score", min_score)
            .execute()
        )
        total = count_res.count or 0
        top_res = (
            client.table("student_job_scores")
            .select("fit_score")
            .eq("student_id", student_id)
            .order("fit_score", desc=True)
            .limit(1)
            .execute()
        )
        top_rows = top_res.data or []
        top_score = round(top_rows[0]["fit_score"] * 100, 1) if top_rows else 0.0
        return {"total_jobs": total, "top_score": top_score}
    except Exception as exc:
        st.warning(f"Could not load student metrics: {exc}")
        return {"total_jobs": 0, "top_score": 0}


@st.cache_data(ttl=1800)
def fetch_metrics() -> dict[str, int]:
    """Global counts from scraped_jobs."""
    client = get_client()
    if client is None:
        return {}
    metrics: dict[str, int] = {}
    try:
        metrics["total_jobs"] = (
            client.table("scraped_jobs").select("id", count="exact").execute().count or 0
        )
    except Exception:
        metrics["total_jobs"] = 0
    try:
        # "High match" = scraper_score >= 0.6 (A or A+)
        metrics["top_matches"] = (
            client.table("scraped_jobs")
            .select("id", count="exact")
            .gte("scraper_score", 0.6)
            .execute().count or 0
        )
    except Exception:
        metrics["top_matches"] = 0
    try:
        metrics["entry_eligible"] = (
            client.table("scraped_jobs")
            .select("id", count="exact")
            .eq("is_entry_eligible", True)
            .execute().count or 0
        )
    except Exception:
        metrics["entry_eligible"] = 0
    return metrics


# ── Resolve student_id from name ──────────────────────────────────────────────
if chosen != "All Students":
    students_data = fetch_students()
    match = next((s for s in students_data if s["name"] == chosen), None)
    if match:
        selected_student_id = match["id"]


# ── Header ────────────────────────────────────────────────────────────────────
st.title("🎯 MCT PathAI")
st.caption("AI-Powered Job Matching for F1 & OPT Students — Powered by MCTechnology LLC")
st.markdown("---")

# ── Metric Cards ──────────────────────────────────────────────────────────────
global_m = fetch_metrics()

if selected_student_id:
    sm = fetch_student_metrics(selected_student_id, min_score=0.4)
    c1, c2, c3 = st.columns(3)
    c1.metric("Matched Jobs",    f"{sm['total_jobs']:,}")
    c2.metric("Top Match Score", f"{sm['top_score']:.0f}%")
    c3.metric("A/A+ (Global)",   f"{global_m.get('top_matches', 0):,}")
else:
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Jobs Scraped", f"{global_m.get('total_jobs', 0):,}")
    c2.metric("Entry Eligible",     f"{global_m.get('entry_eligible', 0):,}")
    c3.metric("High Match (A/A+)",  f"{global_m.get('top_matches', 0):,}")

st.markdown("---")


# ── Load Data ─────────────────────────────────────────────────────────────────
if selected_student_id:
    df_all = fetch_student_jobs(selected_student_id, min_score=0.4, limit=500)
    if df_all.empty:
        st.warning(f"No qualified matches for {selected_student_name} (fit score ≥ 40%).")
else:
    df_all = fetch_scraped_jobs()

if df_all.empty:
    st.info("No job data found. Run the scraper pipeline to populate Supabase.")
    st.stop()

# Parse fetched_at for time-series chart
if "fetched_at" in df_all.columns:
    df_all["fetched_at"] = pd.to_datetime(df_all["fetched_at"], errors="coerce")
    df_all["fetch_date"] = df_all["fetched_at"].dt.date


# ── Analytics ─────────────────────────────────────────────────────────────────
st.subheader("📊 Analytics")

_CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#e2e8f0"),
    margin=dict(t=40, l=10, r=10, b=10),
)

ch1, ch2 = st.columns(2)

with ch1:
    if "fetch_date" in df_all.columns:
        time_df = (
            df_all.dropna(subset=["fetch_date"])
            .groupby("fetch_date").size()
            .reset_index(name="count")
            .sort_values("fetch_date")
        )
        if not time_df.empty:
            fig = px.bar(time_df, x="fetch_date", y="count",
                         labels={"fetch_date": "", "count": "Jobs"},
                         color_discrete_sequence=["#7c3aed"],
                         title="Jobs Scraped Over Time")
            layout = dict(_CHART_LAYOUT)
            layout.update({
                "xaxis": dict(gridcolor="rgba(255,255,255,0.1)", color="#e2e8f0"),
                "yaxis": dict(gridcolor="rgba(255,255,255,0.1)", color="#e2e8f0"),
            })
            fig.update_layout(**layout)
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No scrape timestamps yet.")
    else:
        st.info("No scrape timestamps found.")

with ch2:
    grade_col = "grade"
    if grade_col in df_all.columns:
        grade_counts = (
            df_all[grade_col].dropna().value_counts()
            .reindex(GRADE_ORDER, fill_value=0)
            .reset_index()
        )
        grade_counts.columns = ["grade", "count"]
        grade_counts = grade_counts[grade_counts["count"] > 0]
        if not grade_counts.empty:
            colors = [GRADE_PALETTE.get(g, "#94a3b8") for g in grade_counts["grade"]]
            fig2 = go.Figure(go.Pie(
                labels=grade_counts["grade"],
                values=grade_counts["count"],
                hole=0.58,
                marker=dict(colors=colors, line=dict(color="white", width=2)),
                textinfo="label+percent",
            ))
            layout2 = dict(_CHART_LAYOUT)
            layout2.update({"title": "Score Distribution", "showlegend": False})
            fig2.update_layout(**layout2)
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No grade data yet.")
    elif "job_category" in df_all.columns:
        cat_counts = (
            df_all["job_category"].dropna().value_counts().head(8).reset_index()
        )
        cat_counts.columns = ["category", "count"]
        fig2 = px.pie(cat_counts, values="count", names="category", hole=0.55,
                      title="Job Categories",
                      color_discrete_sequence=px.colors.sequential.Purpor)
        layout2 = dict(_CHART_LAYOUT)
        layout2.update({"showlegend": False})
        fig2.update_layout(**layout2)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No score data.")


# ── Top Companies ─────────────────────────────────────────────────────────────
if "company" in df_all.columns:
    st.subheader("🏢 Top Companies")
    top_cos = (
        df_all["company"].dropna().value_counts().head(10).reset_index()
    )
    top_cos.columns = ["company", "count"]
    top_cos = top_cos.sort_values("count")
    fig3 = px.bar(top_cos, x="count", y="company", orientation="h",
                  labels={"count": "Jobs", "company": ""},
                  color="count",
                  color_continuous_scale=["#312e81", "#7c3aed", "#a78bfa"])
    layout3 = dict(_CHART_LAYOUT)
    layout3.update({
        "coloraxis_showscale": False, "height": 360,
        "xaxis": dict(gridcolor="rgba(255,255,255,0.1)", color="#e2e8f0"),
        "yaxis": dict(gridcolor="rgba(0,0,0,0)", color="#e2e8f0",
                      tickfont=dict(size=11)),
    })
    fig3.update_layout(**layout3)
    fig3.update_traces(marker_line_width=0)
    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

st.markdown("---")


# ── Apply filters ─────────────────────────────────────────────────────────────
df = df_all.copy()

# Grade filter applies to the derived "grade" column (from scraper_score)
if not selected_student_id and grade_filter and "grade" in df.columns:
    df = df[df["grade"].isin(grade_filter)]

if company_search:
    df = df[df["company"].str.contains(company_search, case=False, na=False)]

if hide_visa_flagged and "visa_flag" in df.columns:
    df = df[df["visa_flag"].ne(True)]


# ── Job Cards ─────────────────────────────────────────────────────────────────
table_title = (
    f"🎯 {selected_student_name}'s Matches ({len(df):,} results)"
    if selected_student_id
    else f"📋 All Jobs ({len(df):,} results)"
)
st.subheader(table_title)

if df.empty:
    st.info(
        f"No qualified jobs for {selected_student_name} (fit score ≥ 40%)."
        if selected_student_id
        else "No jobs match the current filters."
    )
else:
    for _, row in df.iterrows():
        company  = str(row.get("company", "?"))
        title    = str(row.get("title", "Unknown Title"))
        job_url  = str(row.get("url", "#"))
        location = str(row.get("location", ""))

        if selected_student_id and "fit_score" in row:
            raw_score = float(row["fit_score"])   # already ×100
            grade, badge = _fit_score_to_grade(raw_score)
            score_label = "Match Score"
        else:
            raw = row.get("scraper_score", 0)
            try:
                raw_score = float(raw) * 100 if pd.notna(raw) and raw != "" else 0
            except (ValueError, TypeError):
                raw_score = 0
            grade = str(row.get("grade", "—"))
            badge = {"A+": "🟢", "A": "🔵", "B+": "🟣", "B": "🟠"}.get(grade, "⚪")
            score_label = "Scraper Score"

        score_int = max(0, min(100, int(raw_score)))

        col_info, col_grade, col_score = st.columns([4, 1, 1])
        with col_info:
            st.markdown(f"**{title}**")
            st.caption(f"{company}  ·  {location}")
            st.markdown(f"[Apply Now ↗]({job_url})")
        with col_grade:
            st.metric("Grade", f"{badge} {grade}")
        with col_score:
            st.metric(score_label, f"{score_int}%")
        st.markdown("---")


# ── Daily Summary ─────────────────────────────────────────────────────────────
if "fetch_date" in df_all.columns:
    st.subheader("📅 Daily Summary")
    daily_groups = df_all.dropna(subset=["fetch_date"]).groupby("fetch_date")
    dates_sorted = sorted(daily_groups.groups.keys(), reverse=True)
    if dates_sorted:
        for date in dates_sorted:
            group = daily_groups.get_group(date)
            count = len(group)
            with st.expander(f"📆 {date}  —  {count} job{'s' if count != 1 else ''} scraped"):
                cols = [c for c in ["company", "title", "grade", "scraper_score"] if c in group.columns]
                sub = group[cols].copy()
                sub = sub.rename(columns={
                    "grade": "Grade",
                    "scraper_score": "Score",
                    "company": "Company",
                    "title": "Title",
                })
                if "Score" in sub.columns:
                    sub["Score"] = sub["Score"].apply(
                        lambda v: f"{float(v):.2f}" if pd.notna(v) and v != "" else "—"
                    )
                st.dataframe(sub, use_container_width=True, hide_index=True)
    else:
        st.info("No scraped jobs with dates yet.")
