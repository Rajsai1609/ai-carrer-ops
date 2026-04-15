"""
MCT PathAI — Job Intelligence Pipeline Dashboard
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

# ── Global CSS ───────────────────────────────────────────────────────────────
# Interface Design principles: 8px base, border-only depth, cool slate palette
st.markdown(
    """
    <style>
    /* ── Design Tokens (8px base, border-only depth) ── */
    :root {
        --spacing-xs: 4px;
        --spacing-sm: 8px;
        --spacing-md: 12px;
        --spacing-lg: 16px;
        --spacing-xl: 24px;
        --spacing-2xl: 32px;
        
        --surface-1: #ffffff;
        --surface-2: #f8fafc;
        --surface-3: #f1f5f9;
        
        --border-subtle: rgba(15, 23, 42, 0.06);
        --border-default: rgba(15, 23, 42, 0.12);
        --border-strong: rgba(15, 23, 42, 0.18);
        
        --accent-purple: #7c3aed;
        --accent-blue: #2563eb;
        --accent-green: #16a34a;
        --accent-orange: #ea580c;
        
        --text-primary: #0f172a;
        --text-secondary: #475569;
        --text-muted: #94a3b8;
    }

    /* ── Sidebar pinned open ── */
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebar"] {
        min-width: 300px !important;
        max-width: 300px !important;
        background-color: #0f172a !important;
        border-right: 0.5px solid rgba(255,255,255,0.06) !important;
    }
    [data-testid="stSidebar"][aria-expanded="false"] {
        min-width: 300px !important;
        width: 300px !important;
        transform: none !important;
    }

    /* ── Base ── */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #f8fafc !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        color: var(--text-primary);
    }
    .block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; }

    /* ── Mobile Responsive ── */
    @media (max-width: 768px) {
        .mct-header { padding: var(--spacing-lg) !important; }
        .mct-header h1 { font-size: 1.5rem !important; }
        .metric-card { min-height: 80px !important; padding: var(--spacing-lg) !important; }
    }

    /* ── Header ── */
    .mct-header {
        background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%);
        border-radius: 12px;
        padding: var(--spacing-xl);
        margin-bottom: var(--spacing-xl);
        color: white;
        border: 0.5px solid rgba(255,255,255,0.1);
    }
    .mct-header h1 {
        font-size: 1.75rem;
        font-weight: 700;
        letter-spacing: -0.025em;
        margin: 0 0 var(--spacing-xs) 0;
    }
    .mct-header p { font-size: 0.875rem; opacity: 0.85; margin: 0; }
    .mct-powered { font-size: 0.75rem; opacity: 0.6; margin-top: var(--spacing-sm) !important; letter-spacing: 0.5px; }

    /* ── Section Title ── */
    .section-title {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: var(--spacing-lg);
        letter-spacing: -0.01em;
    }

    /* ── Metric cards ── */
    .metric-card {
        border-radius: 8px;
        padding: var(--spacing-lg);
        color: white;
        border: 0.5px solid rgba(255,255,255,0.08);
        min-height: 88px;
    }
    .metric-card .icon {
        position: absolute;
        top: var(--spacing-sm);
        right: var(--spacing-sm);
        font-size: 1.25rem;
        opacity: 0.4;
    }
    .metric-card .number {
        font-size: 1.75rem;
        font-weight: 700;
        line-height: 1.1;
    }
    .metric-card .label {
        font-size: 0.75rem;
        font-weight: 500;
        opacity: 0.85;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .card-purple { background: linear-gradient(135deg, #7c3aed, #6d28d9); }
    .card-blue   { background: linear-gradient(135deg, #2563eb, #1d4ed8); }
    .card-green  { background: linear-gradient(135deg, #16a34a, #15803d); }
    .card-orange { background: linear-gradient(135deg, #ea580c, #dc2626); }

    /* ── Job Cards ── */
    .job-card {
        background: var(--surface-1);
        border-radius: 8px;
        padding: var(--spacing-lg);
        margin-bottom: var(--spacing-md);
        border: 0.5px solid var(--border-subtle);
        transition: border-color 0.15s ease;
    }
    .job-card:hover {
        border-color: var(--border-default);
    }
    .job-card-company {
        width: 40px;
        height: 40px;
        border-radius: 8px;
        background: linear-gradient(135deg, #7c3aed15, #2563eb15);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        color: #7c3aed;
        font-size: 1rem;
    }
    .job-card-title {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-primary);
    }
    .job-card-company-name {
        font-size: 0.8125rem;
        color: var(--text-secondary);
    }
    .job-card-badge {
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.6875rem;
        font-weight: 600;
    }
    .grade-a { background: #dcfce7; color: #166534; }
    .grade-b { background: #dbeafe; color: #1e40af; }
    .grade-c { background: #f1f5f9; color: #475569; }
    .job-card-score {
        font-size: 1.5rem;
        font-weight: 700;
        color: #7c3aed;
    }
    .btn-primary {
        background: #7c3aed;
        color: white;
        border: none;
        padding: 10px 16px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.8125rem;
        cursor: pointer;
        transition: background 0.15s;
    }
    .btn-primary:hover { background: #6d28d9; }
    .btn-secondary {
        background: white;
        color: #7c3aed;
        border: 0.5px solid #7c3aed;
        padding: 10px 16px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.8125rem;
        cursor: pointer;
    }

    /* ── Student Profile Hero ── */
    .student-hero {
        background: linear-gradient(135deg, #7c3aed08, #2563eb08);
        border: 0.5px solid var(--border-default);
        border-radius: 10px;
        padding: var(--spacing-lg);
        margin-bottom: var(--spacing-xl);
        display: flex;
        align-items: center;
        gap: var(--spacing-md);
    }
    .student-avatar {
        width: 48px;
        height: 48px;
        border-radius: 10px;
        background: linear-gradient(135deg, #7c3aed, #4f46e5);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        font-weight: 700;
        color: white;
    }
    .student-name {
        font-size: 1.125rem;
        font-weight: 700;
        color: var(--text-primary);
    }
    .student-badge {
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.6875rem;
        font-weight: 500;
    }
    .mct-header h1 {
        margin: 0 0 4px 0;
        letter-spacing: -0.5px;
    }
    .mct-header p {
        font-size: 0.95rem;
        opacity: 0.88;
        margin: 0;
    }
    .mct-powered {
        font-size: 0.75rem;
        opacity: 0.70;
        margin-top: 8px !important;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    /* ── Metric cards ── */
    .metric-card {
        border-radius: 16px;
        padding: 22px 24px;
        color: white;
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        position: relative;
        overflow: hidden;
        min-height: 110px;
    }
    .metric-card .icon {
        position: absolute;
        top: 16px;
        right: 18px;
        font-size: 1.8rem;
        opacity: 0.30;
    }
    .metric-card .number {
        font-size: 2.4rem;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 6px;
    }
    .metric-card .label {
        font-size: 0.80rem;
        font-weight: 500;
        opacity: 0.88;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }
    .card-purple { background: linear-gradient(135deg, #a855f7, #7c3aed); }
    .card-blue   { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }
    .card-green  { background: linear-gradient(135deg, #22c55e, #15803d); }
    .card-orange { background: linear-gradient(135deg, #f97316, #c2410c); }

    /* ── Section titles ── */
    .section-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1e293b;
        margin: 8px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #e2e8f0;
    }

    /* ── Daily summary rows ── */
    .daily-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid #f1f5f9;
        font-size: 0.9rem;
    }
    .daily-date { font-weight: 600; color: #334155; }
    .daily-count {
        background: #ede9fe;
        color: #6d28d9;
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 0.78rem;
        font-weight: 600;
    }

    /* ── Table row colors ── */
    .row-green { background-color: #f0fdf4 !important; }
    .row-blue  { background-color: #eff6ff !important; }
    .row-gray  { background-color: #f8fafc !important; }

    /* ── Sidebar ── */
    .sidebar-label {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #64748b;
        margin-bottom: 4px;
    }

    /* Hide Streamlit branding */
    #MainMenu, footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Constants ────────────────────────────────────────────────────────────────
GRADE_ORDER = ["A+", "A", "B+", "B", "C+", "C", "D", "F"]

GRADE_COLORS: dict[str, str] = {
    "A+": "background-color:#dcfce7; color:#166534;",
    "A":  "background-color:#dcfce7; color:#166534;",
    "B+": "background-color:#dbeafe; color:#1e40af;",
    "B":  "background-color:#dbeafe; color:#1e40af;",
    "C+": "background-color:#f1f5f9; color:#475569;",
    "C":  "background-color:#f1f5f9; color:#475569;",
    "D":  "background-color:#fef2f2; color:#991b1b;",
    "F":  "background-color:#fef2f2; color:#991b1b;",
}

GRADE_PALETTE: dict[str, str] = {
    "A+": "#16a34a",
    "A":  "#22c55e",
    "B+": "#3b82f6",
    "B":  "#60a5fa",
    "C+": "#94a3b8",
    "C":  "#cbd5e1",
    "D":  "#f97316",
    "F":  "#ef4444",
}

DISPLAY_COLS = [
    "company",
    "title",
    "career_ops_grade",
    "career_ops_score",
    "evaluated_at",
]


# ── Supabase client ──────────────────────────────────────────────────────────
def get_client() -> Client | None:
    url = ""
    key = ""
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
        st.error(
            "**Supabase credentials not found.**\n\n"
            "Please set `SUPABASE_URL` and `SUPABASE_KEY` in your `.env` file "
            "or in `.streamlit/secrets.toml`."
        )
        return None

    return create_client(url, key)


# ── Data fetchers ────────────────────────────────────────────────────────────
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
        return pd.DataFrame(flat)
    except Exception as exc:
        st.warning(f"Could not load jobs: {exc}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def fetch_student_jobs(student_id: str, min_score: float = 0.4, limit: int = 50) -> pd.DataFrame:
    """Fetch personalized jobs for a student via PostgREST join on student_job_scores."""
    client = get_client()
    if client is None:
        return pd.DataFrame()
    try:
        result = (
            client.table("student_job_scores")
            .select(
                "fit_score, "
                "jobs(id, url, company, title, location, career_ops_grade, "
                "career_ops_score, visa_flag, evaluated_at)"
            )
            .eq("student_id", student_id)
            .gte("fit_score", min_score)
            .order("fit_score", ascending=False)
            .limit(limit)
            .execute()
        )
        rows = result.data or []
        if not rows:
            return pd.DataFrame()

        flat: list[dict] = []
        for r in rows:
            job = r.pop("jobs", None) or {}
            flat.append({"fit_score": round(r["fit_score"] * 100, 1), **job})

        return pd.DataFrame(flat)
    except Exception as exc:
        st.warning(f"Could not load student jobs: {exc}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def fetch_student_metrics(student_id: str, min_score: float = 0.4) -> dict:
    """Return per-student stats: total qualified jobs and top match score."""
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
            .order("fit_score", ascending=False)
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

    try:
        res = client.table("jobs").select("id", count="exact").execute()
        metrics["total_jobs"] = res.count or 0
    except Exception:
        metrics["total_jobs"] = 0

    try:
        res = (
            client.table("jobs")
            .select("id", count="exact")
            .not_.is_("career_ops_grade", "null")
            .execute()
        )
        metrics["total_evaluated"] = res.count or 0
    except Exception:
        metrics["total_evaluated"] = 0

    try:
        res = (
            client.table("jobs")
            .select("id", count="exact")
            .in_("career_ops_grade", ["A+", "A"])
            .execute()
        )
        metrics["top_matches"] = res.count or 0
    except Exception:
        metrics["top_matches"] = 0

    try:
        res = (
            client.table("resumes")
            .select("id", count="exact")
            .eq("status", "generated")
            .execute()
        )
        metrics["resumes_generated"] = res.count or 0
    except Exception:
        metrics["resumes_generated"] = 0

    return metrics


# ── Student state — initialize before any reference ─────────────────────────
selected_student_id: str | None = None
selected_student_name: str = "All students"

# ── Header ───────────────────────────────────────────────────────────────────
# Gradient header
st.markdown(
    """
    <div class="mct-header">
        <h1>🚀 MCT PathAI</h1>
        <p>Job Intelligence Pipeline — Real-time evaluation &amp; career matching</p>
        <p class="mct-powered">⚡ Powered by MCTechnology LLC</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 Filters")
    st.markdown("---")

    grade_filter: list[str] = st.multiselect(
        "Grade Filter",
        options=GRADE_ORDER,
        default=["A+", "A"],
        help="Filter jobs by evaluation grade",
    )

    company_search: str = st.text_input("🏢 Company Search", "", placeholder="e.g. Google")

    hide_visa_flagged: bool = st.checkbox("Hide visa-flagged jobs", value=True)

    st.markdown("---")
    st.markdown("### 👤 Student View")

    students = fetch_students()

    student_options = ["All students"] + [s["name"] for s in students]
    chosen = st.selectbox(
        "View jobs for:",
        options=student_options,
        index=0,
        key="student_selector",
    )
    if chosen != "All students":
        match = next((s for s in students if s["name"] == chosen), None)
        if match:
            selected_student_id = match["id"]
            selected_student_name = chosen

    st.markdown("---")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.caption("Cache TTL: 30 min")


# ── Student Profile Hero (rendered after sidebar so selected_student_id is set) ──
if selected_student_id:
    initials = "".join([n[0] for n in selected_student_name.split()[:2]]).upper()
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #667eea22 0%, #764ba222 100%);
                    border: 1px solid #e9ecef; border-radius: 16px; padding: 20px;
                    margin-bottom: 24px; display: flex; align-items: center; gap: 16px;">
            <div style="width: 56px; height: 56px; border-radius: 50%;
                        background: linear-gradient(135deg, #667eea, #764ba2);
                        display: flex; align-items: center; justify-content: center;
                        font-size: 20px; font-weight: 700; color: white;">
                {initials}
            </div>
            <div style="flex: 1;">
                <div style="font-size: 18px; font-weight: 700; color: #1e293b;">
                    {selected_student_name}
                </div>
                <div style="color: #64748b; font-size: 13px; margin-top: 4px;">
                    Showing personalized job matches from student_job_scores
                </div>
            </div>
            <div style="text-align: right; color: #64748b; font-size: 12px;">
                fit_score &gt; 40% · top 50 results
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Metrics ──────────────────────────────────────────────────────────────────
def _metric_card(col, color_class: str, icon: str, value: str, label: str) -> None:
    col.markdown(
        f"""
        <div class="metric-card {color_class}">
            <div class="icon">{icon}</div>
            <div class="number">{value}</div>
            <div class="label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


if selected_student_id:
    # Per-student metric cards
    sm = fetch_student_metrics(selected_student_id, min_score=0.4)
    global_m = fetch_metrics()
    c1, c2, c3, c4 = st.columns(4)
    _metric_card(c1, "card-purple", "📈", f"{sm['total_jobs']:,}",         "Matched Jobs")
    _metric_card(c2, "card-blue",   "🎯", f"{sm['top_score']:.0f}%",       "Top Match Score")
    _metric_card(c3, "card-green",  "⭐", f"{global_m.get('top_matches', 0):,}", "A/A+ (Global)")
    _metric_card(c4, "card-orange", "📄", f"{global_m.get('resumes_generated', 0):,}", "Resumes Generated")
else:
    # Global metric cards
    global_m = fetch_metrics()
    c1, c2, c3, c4 = st.columns(4)
    _metric_card(c1, "card-purple", "📈", f"{global_m.get('total_jobs', 0):,}",      "Total Jobs Scraped")
    _metric_card(c2, "card-blue",   "💼", f"{global_m.get('total_evaluated', 0):,}", "Jobs Evaluated")
    _metric_card(c3, "card-green",  "⭐", f"{global_m.get('top_matches', 0):,}",     "A / A+ Matches")
    _metric_card(c4, "card-orange", "📄", f"{global_m.get('resumes_generated', 0):,}", "Resumes Generated")

st.markdown("<br>", unsafe_allow_html=True)


# ── Load full data ────────────────────────────────────────────────────────────
# Use personalized student jobs if a student is selected
if selected_student_id:
    df_all = fetch_student_jobs(selected_student_id, min_score=0.4, limit=50)
    if df_all.empty:
        st.warning(f"No qualified jobs found for {selected_student_name} (score >= 0.4)")
else:
    df_all = fetch_jobs_with_evals()

if df_all.empty:
    st.info("No job data found. Run the sync pipeline to populate Supabase.")
    st.stop()

# Parse evaluated_at
if "evaluated_at" in df_all.columns:
    df_all["evaluated_at"] = pd.to_datetime(df_all["evaluated_at"], errors="coerce")
    df_all["eval_date"] = df_all["evaluated_at"].dt.date


# ── Charts row ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📊 Analytics</div>', unsafe_allow_html=True)

ch1, ch2 = st.columns(2)

# Left: Jobs graded over time
with ch1:
    if "eval_date" in df_all.columns:
        time_df = (
            df_all.dropna(subset=["eval_date"])
            .groupby("eval_date")
            .size()
            .reset_index(name="count")
            .sort_values("eval_date")
        )
        if not time_df.empty:
            fig_time = px.bar(
                time_df,
                x="eval_date",
                y="count",
                title="Jobs Graded Over Time",
                labels={"eval_date": "Date", "count": "Jobs"},
                color_discrete_sequence=["#3b82f6"],
            )
            fig_time.update_layout(
                plot_bgcolor="white",
                paper_bgcolor="white",
                font_family="Inter, Segoe UI, Arial",
                title_font_size=15,
                title_font_color="#1e293b",
                margin=dict(t=50, l=10, r=10, b=10),
                xaxis=dict(gridcolor="#f1f5f9"),
                yaxis=dict(gridcolor="#f1f5f9"),
            )
            st.plotly_chart(fig_time, use_container_width=True)
        else:
            st.info("No dated evaluations yet.")
    else:
        st.info("No evaluation timestamps found.")

# Right: Grade distribution donut
with ch2:
    grade_col = "career_ops_grade"
    if grade_col in df_all.columns:
        grade_counts = (
            df_all[grade_col]
            .dropna()
            .value_counts()
            .reindex(GRADE_ORDER, fill_value=0)
            .reset_index()
        )
        grade_counts.columns = ["grade", "count"]
        grade_counts = grade_counts[grade_counts["count"] > 0]

        if not grade_counts.empty:
            colors = [GRADE_PALETTE.get(g, "#94a3b8") for g in grade_counts["grade"]]
            fig_donut = go.Figure(
                go.Pie(
                    labels=grade_counts["grade"],
                    values=grade_counts["count"],
                    hole=0.52,
                    marker=dict(colors=colors, line=dict(color="white", width=2)),
                    textinfo="label+percent",
                    textfont_size=12,
                )
            )
            fig_donut.update_layout(
                title="Grade Distribution",
                title_font_size=15,
                title_font_color="#1e293b",
                paper_bgcolor="white",
                font_family="Inter, Segoe UI, Arial",
                showlegend=False,
                margin=dict(t=50, l=10, r=10, b=10),
            )
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.info("No grade data available yet.")
    else:
        st.info("No grade column found.")


# ── Top Companies bar chart ──────────────────────────────────────────────────
st.markdown('<div class="section-title">🏢 Top Companies by Job Count</div>', unsafe_allow_html=True)

if "company" in df_all.columns:
    top_cos = (
        df_all["company"]
        .dropna()
        .value_counts()
        .head(10)
        .reset_index()
    )
    top_cos.columns = ["company", "count"]
    top_cos = top_cos.sort_values("count")

    fig_companies = px.bar(
        top_cos,
        x="count",
        y="company",
        orientation="h",
        labels={"count": "Job Count", "company": ""},
        color="count",
        color_continuous_scale=["#bfdbfe", "#1d4ed8"],
    )
    fig_companies.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font_family="Inter, Segoe UI, Arial",
        coloraxis_showscale=False,
        margin=dict(t=20, l=10, r=30, b=10),
        yaxis=dict(tickfont=dict(size=12)),
        xaxis=dict(gridcolor="#f1f5f9"),
        height=380,
    )
    st.plotly_chart(fig_companies, use_container_width=True)
else:
    st.info("No company data available.")


# ── Daily Job Summary ────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📅 Daily Job Summary</div>', unsafe_allow_html=True)

if "eval_date" in df_all.columns:
    daily_groups = (
        df_all.dropna(subset=["eval_date"])
        .groupby("eval_date")
    )
    dates_sorted = sorted(daily_groups.groups.keys(), reverse=True)

    if dates_sorted:
        for date in dates_sorted:
            group = daily_groups.get_group(date)
            count = len(group)
            label = f"📆 {date}  —  {count} job{'s' if count != 1 else ''} evaluated"
            with st.expander(label):
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
else:
    st.info("No evaluation timestamps found.")


# ── Apply filters for jobs table ─────────────────────────────────────────────
df = df_all.copy()

# Grade filter only applies to the global (all-students) view
if not selected_student_id and grade_filter and "career_ops_grade" in df.columns:
    df = df[df["career_ops_grade"].isin(grade_filter)]

if company_search:
    df = df[df["company"].str.contains(company_search, case=False, na=False)]

if hide_visa_flagged and "visa_flag" in df.columns:
    df = df[df["visa_flag"].ne(True)]


def _row_style(row: pd.Series) -> list[str]:
    grade = str(row.get("career_ops_grade", ""))
    return [GRADE_COLORS.get(grade, "")] * len(row)


table_title = (
    f"🎯 {selected_student_name}'s Matched Jobs ({len(df):,} results)"
    if selected_student_id
    else f"📋 Jobs ({len(df):,} results)"
)
st.markdown(f'<div class="section-title">{table_title}</div>', unsafe_allow_html=True)

if df.empty:
    st.info(
        f"No qualified jobs found for {selected_student_name} (fit_score ≥ 40%)."
        if selected_student_id
        else "No jobs match the current filters."
    )
else:
    for _, row in df.iterrows():
        company = row.get("company", "Unknown Company")
        title = row.get("title", "Unknown Title")
        grade = row.get("career_ops_grade", "—")
        job_url = row.get("url", "#")

        # For student view use fit_score; for global view use career_ops_score
        if selected_student_id and "fit_score" in row:
            raw_score = row["fit_score"]  # already multiplied by 100
            score_label = "Match Score"
        else:
            raw = row.get("career_ops_score", 0)
            try:
                raw_score = float(raw) * 20 if pd.notna(raw) and raw != "" else 0
            except (ValueError, TypeError):
                raw_score = 0
            score_label = "Career Score"

        try:
            score_int = int(raw_score)
        except (ValueError, TypeError):
            score_int = 0

        grade_color = GRADE_PALETTE.get(str(grade), "#94a3b8")
        grade_class = "grade-a" if grade in ["A+", "A"] else "grade-b" if grade in ["B+", "B"] else "grade-c"

        # Build badge row
        badges = f'<span class="job-card-badge {grade_class}">Grade: {grade}</span>'
        if selected_student_id:
            badges += f'<span style="background:#ede9fe; color:#6d28d9; padding:4px 10px; border-radius:6px; font-size:12px; margin-left:8px;">🎯 {raw_score:.1f}% fit</span>'

        st.markdown(
            f"""
            <div class="job-card">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div style="flex:1;">
                        <div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
                            <div class="job-card-company">{str(company)[:1].upper()}</div>
                            <div>
                                <div class="job-card-title">{title}</div>
                                <div class="job-card-company-name">{company}</div>
                            </div>
                        </div>
                        <div style="display:flex; gap:8px; margin-top:10px; flex-wrap:wrap;">
                            {badges}
                        </div>
                    </div>
                    <div style="text-align:right; min-width:90px;">
                        <div class="job-card-score">{score_int}%</div>
                        <div style="font-size:11px; color:#64748b;">{score_label}</div>
                    </div>
                </div>
                <div style="margin-top:16px; padding-top:16px; border-top:1px solid #f1f5f9;">
                    <a href="{job_url}" target="_blank" class="btn-primary">
                        Apply Now ↗
                    </a>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ── Job Detail ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🔎 Job Detail</div>', unsafe_allow_html=True)

if "report_markdown" in df.columns and not df.empty:
    labels = df.apply(
        lambda r: (
            f"{r.get('company', '?')} — {r.get('title', '?')} "
            f"({r.get('career_ops_grade', '?')})"
        ),
        axis=1,
    ).tolist()

    selected_label = st.selectbox(
        "View full evaluation report:",
        ["— select a job —"] + labels,
    )

    if selected_label and selected_label != "— select a job —":
        idx = labels.index(selected_label)
        row = df.iloc[idx]
        report_md = row.get("report_markdown", "")

        meta_cols = st.columns(3)
        meta_cols[0].metric("Company", row.get("company", "—"))
        meta_cols[1].metric("Grade", row.get("career_ops_grade", "—"))
        raw_score = row.get("career_ops_score", None)
        score_str = f"{float(raw_score):.2f}" if pd.notna(raw_score) and raw_score != "" else "—"
        meta_cols[2].metric("Score", score_str)

        if report_md:
            with st.expander("Full Evaluation Report", expanded=True):
                st.markdown(report_md)
        else:
            st.info("No evaluation report available for this job.")
else:
    st.info("Select grades that include evaluated jobs to see reports.")
