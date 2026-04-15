import os
import streamlit as st
from supabase import create_client
from datetime import date, timedelta

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

st.set_page_config(page_title="MCT PathAI", page_icon="🎯", layout="wide")

@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

@st.cache_data(ttl=300)
def fetch_students():
    return get_supabase().table("students").select("id,name,email").order("name").execute().data or []

@st.cache_data(ttl=300)
def fetch_scores(student_id, days_back=1):
    since = str(date.today() - timedelta(days=days_back))
    return (get_supabase().table("student_job_scores").select("*")
        .eq("student_id", student_id).gte("date_scored", since)
        .order("score", desc=True).execute().data or [])

st.sidebar.title("MCT PathAI")
st.sidebar.caption("Personalized AI Job Matching")
st.sidebar.divider()

students = fetch_students()
if not students:
    st.error("No students found. Run step1_ingest_resumes.py first.")
    st.stop()

selected_name = st.sidebar.selectbox("👤 Your profile", [s["name"] for s in students])
selected_student = next(s for s in students if s["name"] == selected_name)
days_back = st.sidebar.selectbox("📅 Show jobs from", [1,3,7], format_func=lambda x: f"Last {x} day{'s' if x>1 else ''}")
visa_only = st.sidebar.checkbox("🛂 Visa-friendly only", value=True)
min_score = st.sidebar.slider("Min match score", 0.4, 1.0, 0.5, 0.05)
st.sidebar.divider()
st.sidebar.caption("mctpathai-dashboard.streamlit.app")

st.title(f"🎯 Job Matches — {selected_student['name']}")
st.caption("Updated daily at 7:00 AM PDT · Scored against your resume")

jobs = fetch_scores(selected_student["id"], days_back)
if visa_only:
    jobs = [j for j in jobs if j.get("visa_friendly")]
jobs = [j for j in jobs if j.get("score", 0) >= min_score]

c1,c2,c3,c4 = st.columns(4)
c1.metric("Total matches", len(jobs))
c2.metric("Strong (≥0.7)", sum(1 for j in jobs if j["score"] >= 0.7))
c3.metric("Visa-friendly", sum(1 for j in jobs if j.get("visa_friendly")))
c4.metric("Date", str(date.today()))
st.divider()

if not jobs:
    st.info("No matches found. Try lowering the score threshold or expanding date range.")
else:
    for job in jobs:
        score = job.get("score", 0)
        icon = "🟢" if score >= 0.7 else "🟡" if score >= 0.55 else "🟠"
        with st.container(border=True):
            c1,c2 = st.columns([4,1])
            with c1:
                st.markdown(f"**{job['job_title']}** — {job['company']}")
                st.caption(f"📍 {job.get('location','N/A')} · {job.get('ats_source','').upper()} · {'🛂 Visa-friendly' if job.get('visa_friendly') else ''}")
            with c2:
                st.markdown(f"### {icon} {round(score*100)}%")
            if job.get("job_url"):
                st.link_button("Apply →", job["job_url"])