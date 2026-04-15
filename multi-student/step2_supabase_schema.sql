create table if not exists students (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    email text unique not null,
    resume_text text,
    resume_file text,
    created_at timestamptz default now()
);

create table if not exists student_job_scores (
    id uuid primary key default gen_random_uuid(),
    student_id uuid references students(id) on delete cascade,
    job_title text,
    company text,
    location text,
    job_url text,
    ats_source text,
    visa_friendly boolean default false,
    score float,
    date_scored date default current_date,
    created_at timestamptz default now(),
    unique(student_id, job_url, date_scored)
);

create index if not exists idx_student_scores_student_id
    on student_job_scores(student_id, date_scored desc);