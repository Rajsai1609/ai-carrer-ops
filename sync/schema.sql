-- Career-Ops Supabase Schema
-- Run this once in the Supabase SQL Editor to create the required tables.

CREATE TABLE IF NOT EXISTS jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  url TEXT UNIQUE NOT NULL,
  title TEXT,
  company TEXT,
  ats_platform TEXT,
  scraper_score FLOAT,
  career_ops_grade TEXT,
  career_ops_score FLOAT,
  visa_flag BOOLEAN DEFAULT FALSE,
  scraped_at TIMESTAMPTZ,
  evaluated_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS evaluations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
  final_grade TEXT,
  final_score FLOAT,
  report_markdown TEXT,
  evaluated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS resumes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
  tailored_resume_md TEXT,
  match_score FLOAT,
  generated_at TIMESTAMPTZ DEFAULT NOW(),
  status TEXT DEFAULT 'pending'
);
