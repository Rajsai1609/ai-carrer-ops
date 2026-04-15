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

# ── Global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="block-container"] {
    background-color: #0f172a !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #f8fafc;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #0f172a !important;
    border-right: 1px solid rgba(148,163,184,0.08) !important;
    min-width: 280px !important;
    max-width: 280px !important;
}
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stCheckbox label span { color: #94a3b8 !important; }
[data-testid="stSidebar"] .sidebar-section { color: #94a3b8 !important; }
[data-testid="stSidebar"] .sidebar-footer { color: #475569 !important; }

/* Sidebar inputs */
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stMultiSelect > div > div {
    background-color: #1e293b !important;
    border: 1px solid rgba(148,163,184,0.15) !important;
    color: #f1f5f9 !important;
    border-radius: 8px !important;
}

/* ── Block container ── */
.block-container {
    padding: 1.5rem 2rem 3rem !important;
    max-width: 1400px;
}

/* ── Hero Banner ── */
.hero {
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #1e3a5f 100%);
    border-radius: 20px;
    padding: 40px 48px;
    margin-bottom: 32px;
    border: 1px solid rgba(139,92,246,0.25);
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 260px; height: 260px;
    background: radial-gradient(circle, rgba(139,92,246,0.18) 0%, transparent 70%);
    pointer-events: none;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -40px; left: 30%;
    width: 180px; height: 180px;
    background: radial-gradient(circle, rgba(37,99,235,0.15) 0%, transparent 70%);
    pointer-events: none;
}
.hero-eyebrow {
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #a78bfa;
    margin-bottom: 10px;
}
.hero-title {
    font-size: 2.4rem;
    font-weight: 800;
    line-height: 1.1;
    letter-spacing: -0.03em;
    background: linear-gradient(90deg, #f8fafc 0%, #c4b5fd 60%, #93c5fd 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 10px;
}
.hero-sub {
    font-size: 1rem;
    color: #94a3b8;
    max-width: 520px;
    line-height: 1.6;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(139,92,246,0.18);
    border: 1px solid rgba(139,92,246,0.35);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.72rem;
    font-weight: 600;
    color: #c4b5fd;
    margin-top: 16px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

/* ── Metric Cards ── */
.metric-card {
    border-radius: 16px;
    padding: 22px 24px;
    color: white;
    position: relative;
    overflow: hidden;
    min-height: 110px;
    border: 1px solid rgba(255,255,255,0.07);
}
.metric-card::after {
    content: '';
    position: absolute;
    bottom: -20px; right: -20px;
    width: 100px; height: 100px;
    border-radius: 50%;
    background: rgba(255,255,255,0.05);
}
.metric-card .icon {
    font-size: 1.5rem;
    margin-bottom: 12px;
    display: block;
    opacity: 0.85;
}
.metric-card .number {
    font-size: 2rem;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 4px;
    letter-spacing: -0.03em;
}
.metric-card .label {
    font-size: 0.72rem;
    font-weight: 600;
    opacity: 0.75;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.card-purple { background: linear-gradient(135deg, #7c3aed, #4f46e5); }
.card-blue   { background: linear-gradient(135deg, #2563eb, #0284c7); }
.card-green  { background: linear-gradient(135deg, #16a34a, #0d9488); }
.card-orange { background: linear-gradient(135deg, #ea580c, #dc2626); }

/* ── Section titles ── */
.section-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #f1f5f9;
    margin: 8px 0 20px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(148,163,184,0.12);
    margin-left: 8px;
}

/* ── Student Hero ── */
.student-hero {
    background: linear-gradient(135deg, rgba(124,58,237,0.12), rgba(37,99,235,0.08));
    border: 1px solid rgba(139,92,246,0.2);
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 28px;
    display: flex;
    align-items: center;
    gap: 16px;
}
.student-avatar {
    width: 52px; height: 52px;
    border-radius: 14px;
    background: linear-gradient(135deg, #7c3aed, #4f46e5);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem; font-weight: 800; color: white;
    flex-shrink: 0;
    box-shadow: 0 4px 12px rgba(124,58,237,0.4);
}

/* ── Job Cards ── */
.job-card {
    background: #1e293b;
    border-radius: 14px;
    padding: 20px 22px;
    margin-bottom: 12px;
    border: 1px solid rgba(148,163,184,0.1);
    transition: border-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
}
.job-card:hover {
    border-color: rgba(139,92,246,0.4);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.25);
}
.job-logo {
    width: 42px; height: 42px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 1.05rem; color: white;
    flex-shrink: 0;
}
.job-title {
    font-size: 0.975rem;
    font-weight: 700;
    color: #f1f5f9;
    line-height: 1.3;
}
.job-company {
    font-size: 0.8rem;
    color: #64748b;
    margin-top: 2px;
}
.badge {
    display: inline-flex;
    align-items: center;
    padding: 3px 9px;
    border-radius: 6px;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.03em;
}
.badge-grade-a  { background: rgba(22,163,74,0.15);  color: #4ade80; border: 1px solid rgba(22,163,74,0.25); }
.badge-grade-b  { background: rgba(37,99,235,0.15);  color: #60a5fa; border: 1px solid rgba(37,99,235,0.25); }
.badge-grade-c  { background: rgba(148,163,184,0.1); color: #94a3b8; border: 1px solid rgba(148,163,184,0.2); }
.badge-grade-d  { background: rgba(234,88,12,0.12);  color: #fb923c; border: 1px solid rgba(234,88,12,0.25); }
.badge-match    { background: rgba(139,92,246,0.15); color: #c4b5fd; border: 1px solid rgba(139,92,246,0.3); }
.score-ring {
    font-size: 1.6rem;
    font-weight: 800;
    color: #a78bfa;
    line-height: 1;
    letter-spacing: -0.04em;
}
.score-label { font-size: 0.65rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; }
.apply-btn {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: linear-gradient(135deg, #7c3aed, #4f46e5);
    color: white !important;
    text-decoration: none !important;
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 0.78rem;
    font-weight: 700;
    transition: opacity 0.15s;
    border: none;
}
.apply-btn:hover { opacity: 0.88; }
.card-divider {
    border: none;
    border-top: 1px solid rgba(148,163,184,0.08);
    margin: 14px 0 12px;
}

/* ── Analytics panel ── */
.analytics-panel {
    background: #1e293b;
    border-radius: 16px;
    padding: 20px;
    border: 1px solid rgba(148,163,184,0.1);
}

/* ── Expander dark ── */
.streamlit-expanderHeader {
    background-color: #1e293b !important;
    color: #f1f5f9 !important;
    border-radius: 10px !important;
    border: 1px solid rgba(148,163,184,0.1) !important;
}
.streamlit-expanderContent {
    background-color: #1e293b !important;
    border: 1px solid rgba(148,163,184,0.08) !important;
    border-top: none !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
}

/* ── Selectbox / inputs ── */
.stSelectbox > div > div,
.stMultiSelect > div > div,
.stTextInput > div > div > input {
    background-color: #1e293b !important;
    border: 1px solid rgba(148,163,184,0.15) !important;
    color: #f1f5f9 !important;
    border-radius: 8px !important;
}
.stSelectbox label, .stMultiSelect label, .stTextInput label,
.stCheckbox label span { color: #94a3b8 !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
    transition: opacity 0.15s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* ── Warning / info ── */
.stWarning, .stInfo { border-radius: 10px !important; }

/* ── Sidebar section header ── */
.sidebar-section {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #94a3b8;
    margin: 20px 0 8px;
    padding-bottom: 4px;
    border-bottom: 1px solid rgba(148,163,184,0.1);
}
.sidebar-footer {
    margin-top: 32px;
    padding-top: 16px;
    border-top: 1px solid rgba(148,163,184,0.08);
    font-size: 0.65rem;
    color: #475569;
    text-align: center;
    line-height: 1.7;
}

/* ── Caption ── */
.stCaption { color: #475569 !important; }

/* Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Constants ────────────────────────────────────────────────────────────────
GRADE_ORDER = ["A+", "A", "B+", "B", "C+", "C", "D", "F"]

GRADE_PALETTE: dict[str, str] = {
    "A+": "#22c55e", "A":  "#4ade80",
    "B+": "#3b82f6", "B":  "#60a5fa",
    "C+": "#94a3b8", "C":  "#cbd5e1",
    "D":  "#f97316", "F":  "#ef4444",
}

# Gradient per company initial for logo circles
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


# ── Supabase client ──────────────────────────────────────────────────────────
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
    """Fetch personalized jobs for a student via the student_top_jobs view."""
    client = get_client()
    if client is None:
        return pd.DataFrame()
    try:
        result = (
            client.table("student_top_jobs")
            .select("*")
            .eq("student_id", student_id)
            .eq("is_usa_job", True)
            .gte("fit_score", min_score)
            .order("fit_score", desc=True)
            .limit(limit)
            .execute()
        )
        rows = result.data or []
        if not rows:
            return pd.DataFrame()
        flat = [{**r, "fit_score": round(r["fit_score"] * 100, 1)} for r in rows]
        return pd.DataFrame(flat)
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
        ("total_jobs",        "jobs", None),
        ("total_evaluated",   "jobs", ("not_.is_", "career_ops_grade", "null")),
        ("top_matches",       "jobs", ("in_",       "career_ops_grade", ["A+", "A"])),
        ("resumes_generated", "resumes", ("eq",     "status", "generated")),
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


# ── Sidebar ──────────────────────────────────────────────────────────────────
selected_student_id: str | None = None
selected_student_name: str = "All Students"

with st.sidebar:
    st.markdown("""
    <div style="padding: 4px 0 20px;">
        <div style="font-size:1.1rem; font-weight:800; color:#f1f5f9; letter-spacing:-0.02em;">
            🎯 MCT PathAI
        </div>
        <div style="font-size:0.72rem; color:#475569; margin-top:3px; font-weight:500;
                    letter-spacing:0.06em; text-transform:uppercase;">
            Job Intelligence
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">Student</div>', unsafe_allow_html=True)
    students = fetch_students()
    student_options = ["All Students"] + [s["name"] for s in students]
    chosen = st.selectbox("View jobs for:", options=student_options, index=0, label_visibility="collapsed")
    if chosen != "All Students":
        match = next((s for s in students if s["name"] == chosen), None)
        if match:
            selected_student_id = match["id"]
            selected_student_name = chosen

    st.markdown('<div class="sidebar-section">Filters</div>', unsafe_allow_html=True)
    grade_filter: list[str] = st.multiselect(
        "Grade", options=GRADE_ORDER, default=["A+", "A"],
    )
    company_search: str = st.text_input("Company", placeholder="Search company…")
    hide_visa_flagged: bool = st.checkbox("Hide visa-flagged", value=True)

    st.markdown('<div class="sidebar-section">Actions</div>', unsafe_allow_html=True)
    if st.button("Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("""
    <div class="sidebar-footer">
        MCTechnology LLC · AI Automation<br>Cache refreshes every 30 min
    </div>
    """, unsafe_allow_html=True)


# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">⚡ MCTechnology LLC</div>
    <div class="hero-title">MCT PathAI</div>
    <div class="hero-sub">AI-Powered Job Matching for F1 &amp; OPT Students — real-time scoring, visa intelligence, career insights.</div>
    <div class="hero-badge">🚀 Live Pipeline</div>
</div>
""", unsafe_allow_html=True)


# ── Metric Cards ─────────────────────────────────────────────────────────────
def _metric(col, cls: str, icon: str, value: str, label: str) -> None:
    col.markdown(f"""
    <div class="metric-card {cls}">
        <span class="icon">{icon}</span>
        <div class="number">{value}</div>
        <div class="label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


global_m = fetch_metrics()

if selected_student_id:
    sm = fetch_student_metrics(selected_student_id, min_score=0.4)
    c1, c2, c3 = st.columns(3)
    _metric(c1, "card-purple", "🎯", f"{sm['total_jobs']:,}",              "Matched Jobs")
    _metric(c2, "card-blue",   "📈", f"{sm['top_score']:.0f}%",            "Top Match Score")
    _metric(c3, "card-green",  "⭐", f"{global_m.get('top_matches', 0):,}", "A / A+ (Global)")
else:
    c1, c2, c3 = st.columns(3)
    _metric(c1, "card-purple", "📋", f"{global_m.get('total_jobs', 0):,}",      "Total Jobs Scraped")
    _metric(c2, "card-blue",   "💼", f"{global_m.get('total_evaluated', 0):,}", "Jobs Evaluated")
    _metric(c3, "card-green",  "⭐", f"{global_m.get('top_matches', 0):,}",     "A / A+ Matches")

st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)


# ── Student Profile Hero ──────────────────────────────────────────────────────
if selected_student_id:
    initials = "".join(n[0] for n in selected_student_name.split()[:2]).upper()
    st.markdown(f"""
    <div class="student-hero">
        <div class="student-avatar">{initials}</div>
        <div style="flex:1;">
            <div style="font-size:1rem; font-weight:700; color:#f1f5f9;">{selected_student_name}</div>
            <div style="color:#64748b; font-size:0.8rem; margin-top:3px;">
                Personalized matches · fit score &gt; 40% · top 50 results
            </div>
        </div>
        <div style="background:rgba(139,92,246,0.15); border:1px solid rgba(139,92,246,0.3);
                    border-radius:8px; padding:8px 14px; text-align:center;">
            <div style="font-size:0.65rem; color:#a78bfa; font-weight:600;
                        text-transform:uppercase; letter-spacing:0.08em;">Student View</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Load Data ─────────────────────────────────────────────────────────────────
if selected_student_id:
    df_all = fetch_student_jobs(selected_student_id, min_score=0.4, limit=50)
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
st.markdown('<div class="section-title">📊 Analytics</div>', unsafe_allow_html=True)

_CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#e2e8f0"),
    margin=dict(t=40, l=10, r=10, b=10),
)

ch1, ch2 = st.columns(2)

with ch1:
    st.markdown('<div class="analytics-panel">', unsafe_allow_html=True)
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
                         color_discrete_sequence=["#7c3aed"])
            layout = dict(_CHART_LAYOUT)
            layout.update({
                "title": dict(text="Jobs Graded Over Time", font=dict(size=14, color="#f1f5f9")),
                "xaxis": dict(gridcolor="rgba(255,255,255,0.1)", color="#e2e8f0", linecolor="rgba(0,0,0,0)"),
                "yaxis": dict(gridcolor="rgba(255,255,255,0.1)", color="#e2e8f0", linecolor="rgba(0,0,0,0)"),
            })
            fig.update_layout(**layout)
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No dated evaluations yet.")
    else:
        st.info("No evaluation timestamps found.")
    st.markdown('</div>', unsafe_allow_html=True)

with ch2:
    st.markdown('<div class="analytics-panel">', unsafe_allow_html=True)
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
                marker=dict(colors=colors, line=dict(color="#0f172a", width=2)),
                textinfo="label+percent",
                textfont=dict(size=11, color="#f1f5f9"),
            ))
            layout2 = dict(_CHART_LAYOUT)
            layout2.update({
                "title": dict(text="Grade Distribution", font=dict(size=14, color="#f1f5f9")),
                "showlegend": False,
            })
            fig2.update_layout(**layout2)
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No grade data yet.")
    elif "job_category" in df_all.columns:
        cat_counts = (
            df_all["job_category"].dropna().value_counts().head(8)
            .reset_index()
        )
        cat_counts.columns = ["category", "count"]
        fig2 = px.pie(cat_counts, values="count", names="category", hole=0.55,
                      color_discrete_sequence=px.colors.sequential.Purpor)
        layout2 = dict(_CHART_LAYOUT)
        layout2.update({
            "title": dict(text="Job Categories", font=dict(size=14, color="#f1f5f9")),
            "showlegend": False,
        })
        fig2.update_layout(**layout2)
        fig2.update_traces(textfont=dict(color="#f1f5f9"))
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No category data.")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


# ── Top Companies ─────────────────────────────────────────────────────────────
if "company" in df_all.columns:
    st.markdown('<div class="section-title">🏢 Top Companies</div>', unsafe_allow_html=True)
    st.markdown('<div class="analytics-panel">', unsafe_allow_html=True)
    top_cos = (
        df_all["company"].dropna().value_counts().head(10)
        .reset_index()
    )
    top_cos.columns = ["company", "count"]
    top_cos = top_cos.sort_values("count")
    fig3 = px.bar(top_cos, x="count", y="company", orientation="h",
                  labels={"count": "Jobs", "company": ""},
                  color="count",
                  color_continuous_scale=["#312e81", "#7c3aed", "#a78bfa"])
    layout3 = dict(_CHART_LAYOUT)
    layout3.update({
        "coloraxis_showscale": False,
        "height": 360,
        "xaxis": dict(gridcolor="rgba(255,255,255,0.1)", color="#e2e8f0"),
        "yaxis": dict(gridcolor="rgba(0,0,0,0)", color="#e2e8f0",
                      tickfont=dict(size=11, color="#94a3b8")),
    })
    fig3.update_layout(**layout3)
    fig3.update_traces(marker_line_width=0)
    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


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
    f"🎯 {selected_student_name}'s Matches &nbsp;<span style='color:#475569;font-weight:500;font-size:0.85rem;'>({len(df):,} results)</span>"
    if selected_student_id
    else f"📋 All Jobs &nbsp;<span style='color:#475569;font-weight:500;font-size:0.85rem;'>({len(df):,} results)</span>"
)
st.markdown(f'<div class="section-title">{table_title}</div>', unsafe_allow_html=True)

if df.empty:
    st.info(
        f"No qualified jobs for {selected_student_name} (fit score ≥ 40%)."
        if selected_student_id
        else "No jobs match the current filters."
    )
else:
    # Render in 2-column grid for global view; full-width for student view
    jobs_list = list(df.iterrows())
    use_grid = not selected_student_id and len(jobs_list) > 3

    def _render_job_card(row: pd.Series) -> str:
        company   = str(row.get("company", "?"))
        title     = str(row.get("title",   "Unknown Title"))
        grade     = str(row.get("career_ops_grade", ""))
        job_url   = str(row.get("url", "#"))
        location  = str(row.get("location", ""))

        if selected_student_id and "fit_score" in row:
            raw_score  = float(row["fit_score"])   # already ×100
            score_label = "Match"
        else:
            raw = row.get("career_ops_score", 0)
            try:
                raw_score = float(raw) * 20 if pd.notna(raw) and raw != "" else 0
            except (ValueError, TypeError):
                raw_score = 0
            score_label = "Score"

        score_int = max(0, min(100, int(raw_score)))

        # Grade badge
        if grade in ("A+", "A"):
            grade_cls = "badge-grade-a"
        elif grade in ("B+", "B"):
            grade_cls = "badge-grade-b"
        elif grade in ("D", "F"):
            grade_cls = "badge-grade-d"
        else:
            grade_cls = "badge-grade-c"

        grade_badge = (
            f'<span class="badge {grade_cls}">Grade {grade}</span>'
            if grade and grade != "nan" else ""
        )
        match_badge = (
            f'<span class="badge badge-match">🎯 {raw_score:.0f}% fit</span>'
            if selected_student_id else ""
        )
        loc_badge = (
            f'<span style="font-size:0.72rem;color:#475569;">📍 {location}</span>'
            if location and location != "nan" else ""
        )

        logo_grad = _logo_gradient(company)

        # Score color
        score_color = (
            "#4ade80" if score_int >= 70
            else "#60a5fa" if score_int >= 50
            else "#a78bfa"
        )

        return f"""
        <div class="job-card">
            <div style="display:flex;align-items:flex-start;gap:14px;">
                <div class="job-logo" style="background:{logo_grad};">{company[:1].upper()}</div>
                <div style="flex:1;min-width:0;">
                    <div class="job-title">{title}</div>
                    <div class="job-company">{company}</div>
                    <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;align-items:center;">
                        {grade_badge}{match_badge}{loc_badge}
                    </div>
                </div>
                <div style="text-align:right;flex-shrink:0;">
                    <div class="score-ring" style="color:{score_color};">{score_int}%</div>
                    <div class="score-label">{score_label}</div>
                </div>
            </div>
            <hr class="card-divider">
            <a href="{job_url}" target="_blank" class="apply-btn">Apply Now ↗</a>
        </div>
        """

    if use_grid:
        col_a, col_b = st.columns(2)
        for i, (_, row) in enumerate(jobs_list):
            target = col_a if i % 2 == 0 else col_b
            target.markdown(_render_job_card(row), unsafe_allow_html=True)
    else:
        for _, row in jobs_list:
            st.markdown(_render_job_card(row), unsafe_allow_html=True)


# ── Daily Summary ─────────────────────────────────────────────────────────────
if "eval_date" in df_all.columns:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">📅 Daily Summary</div>', unsafe_allow_html=True)

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
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔎 Job Detail Report</div>', unsafe_allow_html=True)

    labels = df.apply(
        lambda r: f"{r.get('company','?')} — {r.get('title','?')} ({r.get('career_ops_grade','?')})",
        axis=1,
    ).tolist()

    selected_label = st.selectbox("View evaluation report:", ["— select a job —"] + labels)

    if selected_label and selected_label != "— select a job —":
        idx = labels.index(selected_label)
        row = df.iloc[idx]
        report_md = row.get("report_markdown", "")

        m1, m2, m3 = st.columns(3)
        m1.metric("Company", row.get("company", "—"))
        m2.metric("Grade",   row.get("career_ops_grade", "—"))
        raw_score = row.get("career_ops_score")
        score_str = f"{float(raw_score):.2f}" if pd.notna(raw_score) and raw_score != "" else "—"
        m3.metric("Score", score_str)

        if report_md:
            with st.expander("Full Evaluation Report", expanded=True):
                st.markdown(report_md)
        else:
            st.info("No evaluation report available for this job.")
