"""
MCT PathAI — Job Intelligence Dashboard
Powered by MCTechnology LLC
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

# ── Sidebar (must be first after set_page_config) ────────────────────────────
selected_student_id: str | None = None
selected_student_name: str = "All Students"

with st.sidebar:
    st.markdown("### 👤 Student View")

    _STUDENT_NAMES = [
        "All Students",
        "Akhila",
        "M Pavan",
        "Sucharan",
        "Unnatha Bi",
        "Vinit",
    ]

    st.markdown("**View jobs for:**")
    chosen = st.selectbox("", options=_STUDENT_NAMES, key="student_select")
    # Note: hardcoded names for sidebar test — real IDs fetched below
    selected_student_name = chosen if chosen != "All Students" else "All Students"

    st.markdown("---")
    st.markdown("### 🔍 Filters")

    grade_filter: list[str] = st.multiselect(
        "Grade Filter",
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

_LOGO_GRADIENTS = [
    "linear-gradient(135deg,#7c3aed,#4f46e5)",
    "linear-gradient(135deg,#2563eb,#0284c7)",
    "linear-gradient(135deg,#16a34a,#0d9488)",
    "linear-gradient(135deg,#ea580c,#dc2626)",
    "linear-gradient(135deg,#d97706,#b45309)",
    "linear-gradient(135deg,#db2777,#9333ea)",
]


def _logo_gradient(company: str) -> str:
    return _LOGO_GRADIENTS[ord(company[0].upper()) % len(_LOGO_GRADIENTS)]


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
        flat: list[dict] = []
        for r in rows:
            evals = r.pop("evaluations", None) or []
            first_eval = evals[0] if evals else {}
            flat.append({**r, **first_eval})
        df = pd.DataFrame(flat)
        # Deduplicate by id (primary key), then by URL as a safety net
        if "id" in df.columns:
            df = df.drop_duplicates(subset="id")
        if "url" in df.columns:
            df = df.drop_duplicates(subset="url")
        return df
    except Exception as exc:
        st.warning(f"Could not load jobs: {exc}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def fetch_student_jobs(student_id: str, min_score: float = 0.4, limit: int = 500) -> pd.DataFrame:
    """Fetch personalized jobs for a student via the student_top_jobs view."""
    client = get_client()
    if client is None:
        return pd.DataFrame()
    try:
        result = (
            client.table("student_top_jobs")
            .select("*")
            .eq("student_id", student_id)
            .gte("fit_score", min_score)
            .order("fit_score", desc=True)
            .limit(limit)
            .execute()
        )
        rows = result.data or []
        if not rows:
            return pd.DataFrame()
        flat = [{**r, "fit_score": round(r["fit_score"] * 100, 1)} for r in rows]
        df = pd.DataFrame(flat)
        # Deduplicate by URL (keep highest fit_score per URL)
        if "url" in df.columns:
            df = df.sort_values("fit_score", ascending=False).drop_duplicates(subset="url")
        # Filter USA jobs using full state names + common abbreviation suffixes
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
        # Keep all jobs with fit_score >= 40% (grades B and above)
        # fit_score is already ×100 at this point
        if "fit_score" in df.columns:
            df = df[df["fit_score"] >= 40]
        return df
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
    client = get_client()
    if client is None:
        return {}
    metrics: dict[str, int] = {}
    for key, table, extra_filter in [
        ("total_jobs",      "jobs", None),
        ("total_evaluated", "jobs", ("not_.is_", "career_ops_grade", "null")),
        ("top_matches",     "jobs", ("in_",       "career_ops_grade", ["A+", "A"])),
    ]:
        try:
            q = client.table(table).select("id", count="exact")
            if extra_filter:
                method, col, val = extra_filter
                if method == "not_.is_":
                    q = q.not_.is_(col, val)
                elif method == "in_":
                    q = q.in_(col, val)
                else:
                    q = q.eq(col, val)
            metrics[key] = q.execute().count or 0
        except Exception:
            metrics[key] = 0
    return metrics


# ── Resolve student_id from name (now that fetchers are defined) ──────────────
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
    c2.metric("Jobs Evaluated",     f"{global_m.get('total_evaluated', 0):,}")
    c3.metric("A / A+ Matches",     f"{global_m.get('top_matches', 0):,}")

st.markdown("---")


# ── Load Data ─────────────────────────────────────────────────────────────────
if selected_student_id:
    df_all = fetch_student_jobs(selected_student_id, min_score=0.4, limit=500)
    if df_all.empty:
        st.warning(f"No qualified matches for {selected_student_name} (fit score ≥ 40%).")
else:
    df_all = fetch_jobs_with_evals()

if df_all.empty:
    st.info("No job data found. Run the sync pipeline to populate Supabase.")
    st.stop()

if "evaluated_at" in df_all.columns:
    df_all["evaluated_at"] = pd.to_datetime(df_all["evaluated_at"], errors="coerce")
    df_all["eval_date"] = df_all["evaluated_at"].dt.date


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
    if "eval_date" in df_all.columns:
        time_df = (
            df_all.dropna(subset=["eval_date"])
            .groupby("eval_date").size()
            .reset_index(name="count")
            .sort_values("eval_date")
        )
        if not time_df.empty:
            fig = px.bar(time_df, x="eval_date", y="count",
                         labels={"eval_date": "", "count": "Jobs"},
                         color_discrete_sequence=["#7c3aed"],
                         title="Jobs Graded Over Time")
            layout = dict(_CHART_LAYOUT)
            layout.update({
                "xaxis": dict(gridcolor="rgba(255,255,255,0.1)", color="#e2e8f0"),
                "yaxis": dict(gridcolor="rgba(255,255,255,0.1)", color="#e2e8f0"),
            })
            fig.update_layout(**layout)
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No dated evaluations yet.")
    else:
        st.info("No evaluation timestamps found.")

with ch2:
    grade_col = "career_ops_grade"
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
            layout2.update({"title": "Grade Distribution", "showlegend": False})
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
        st.info("No category data.")


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

if not selected_student_id and grade_filter and "career_ops_grade" in df.columns:
    df = df[df["career_ops_grade"].isin(grade_filter)]

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

def _fit_score_to_grade(score_pct: float) -> tuple[str, str]:
    """Convert fit_score percentage to letter grade and badge emoji."""
    if score_pct >= 70:
        return "A+", "🟢"
    if score_pct >= 60:
        return "A",  "🔵"
    if score_pct >= 50:
        return "B+", "🟣"
    if score_pct >= 40:
        return "B",  "🟠"
    return "C", "⚪"


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
            raw_score   = float(row["fit_score"])   # already ×100
            grade, badge = _fit_score_to_grade(raw_score)
            score_label = "Match Score"
        else:
            raw = row.get("career_ops_score", 0)
            try:
                raw_score = float(raw) * 20 if pd.notna(raw) and raw != "" else 0
            except (ValueError, TypeError):
                raw_score = 0
            grade = str(row.get("career_ops_grade", "—"))
            badge = {"A+": "🟢", "A": "🔵", "B+": "🟣", "B": "🟠"}.get(grade, "⚪")
            score_label = "Career Score"

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
if "eval_date" in df_all.columns:
    st.subheader("📅 Daily Summary")
    daily_groups = df_all.dropna(subset=["eval_date"]).groupby("eval_date")
    dates_sorted = sorted(daily_groups.groups.keys(), reverse=True)
    if dates_sorted:
        for date in dates_sorted:
            group = daily_groups.get_group(date)
            count = len(group)
            with st.expander(f"📆 {date}  —  {count} job{'s' if count != 1 else ''} evaluated"):
                sub = group[["company", "title", "career_ops_grade", "career_ops_score"]].copy()
                sub = sub.rename(columns={
                    "career_ops_grade": "Grade",
                    "career_ops_score": "Score",
                    "company": "Company",
                    "title": "Title",
                })
                if "Score" in sub.columns:
                    sub["Score"] = sub["Score"].apply(
                        lambda v: f"{float(v):.2f}" if pd.notna(v) and v != "" else "—"
                    )
                st.dataframe(sub, use_container_width=True, hide_index=True)
    else:
        st.info("No evaluated jobs with dates yet.")


# ── Job Detail Report ─────────────────────────────────────────────────────────
if "report_markdown" in df.columns and not df.empty:
    st.subheader("🔎 Job Detail Report")
    labels = df.apply(
        lambda r: f"{r.get('company','?')} — {r.get('title','?')} ({r.get('career_ops_grade','?')})",
        axis=1,
    ).tolist()
    selected_label = st.selectbox("View evaluation report:", ["— select a job —"] + labels)
    if selected_label and selected_label != "— select a job —":
        idx = labels.index(selected_label)
        row = df.iloc[idx]
        m1, m2, m3 = st.columns(3)
        m1.metric("Company", row.get("company", "—"))
        m2.metric("Grade",   row.get("career_ops_grade", "—"))
        raw_score = row.get("career_ops_score")
        score_str = f"{float(raw_score):.2f}" if pd.notna(raw_score) and raw_score != "" else "—"
        m3.metric("Score", score_str)
        report_md = row.get("report_markdown", "")
        if report_md:
            with st.expander("Full Evaluation Report", expanded=True):
                st.markdown(report_md)
        else:
            st.info("No evaluation report available for this job.")
