"""
Career-Ops → Supabase Sync
Reads grades.tsv + reports + scraper DB, upserts into Supabase.
"""

import csv
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client, Client

# ── Paths ───────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent.resolve()
GRADES_TSV = ROOT / "data" / "grades.tsv"
REPORTS_DIR = ROOT / "reports"
SCRAPER_ROOT = ROOT.parent / "scraper-2.0-agent"
SCRAPER_DB = SCRAPER_ROOT / "data" / "jobs.db"
LAST_RUN_JSON = SCRAPER_ROOT / "bridge" / "last_run.json"

# ── Env ─────────────────────────────────────────────────────────────────────
load_dotenv(ROOT / ".env")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")


# ── Helpers ──────────────────────────────────────────────────────────────────

def detect_ats(url: str) -> str:
    """Infer ATS platform from the job URL."""
    patterns = {
        "ashby": r"ashbyhq\.com",
        "lever": r"lever\.co",
        "greenhouse": r"greenhouse\.io",
        "workday": r"myworkdayjobs\.com|workday\.com",
        "icims": r"icims\.com",
        "taleo": r"taleo\.net",
        "smartrecruiters": r"smartrecruiters\.com",
        "jobvite": r"jobvite\.com",
        "breezy": r"breezy\.hr",
        "workable": r"workable\.com",
        "linkedin": r"linkedin\.com/jobs",
        "indeed": r"indeed\.com",
    }
    for platform, pattern in patterns.items():
        if re.search(pattern, url, re.IGNORECASE):
            return platform
    return "unknown"


def company_slug_from_url(url: str) -> str:
    """Extract a lowercase slug from the URL hostname for report matching."""
    match = re.search(r"https?://(?:www\.)?([^/]+)", url)
    if not match:
        return ""
    host = match.group(1).lower()
    # Strip common ATS subdomains so 'acme.ashbyhq.com' → 'acme'
    host = re.sub(r"\.(ashbyhq|lever|greenhouse|myworkdayjobs|icims|taleo|"
                  r"smartrecruiters|jobvite|breezy|workable)\..*$", "", host)
    # Also strip plain TLDs for direct company sites
    host = re.sub(r"\.(com|io|co|net|org|ai|dev)$", "", host)
    return host.replace("-", "").replace(".", "")


def find_report(company: str, url: str) -> str:
    """Return the markdown content of the best-matching report file."""
    if not REPORTS_DIR.exists():
        return ""

    slug = company_slug_from_url(url)
    candidates = [
        *REPORTS_DIR.glob(f"*{slug}*.md"),
        *REPORTS_DIR.glob(f"*{company.lower().replace(' ', '-')}*.md"),
        *REPORTS_DIR.glob(f"*{company.lower().replace(' ', '_')}*.md"),
    ]
    if candidates:
        # Prefer the most recently modified report
        candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return candidates[0].read_text(encoding="utf-8", errors="replace")
    return ""


def scraper_score_for(url: str) -> float | None:
    """Look up fit_score from the scraper SQLite database."""
    if not SCRAPER_DB.exists():
        return None
    try:
        con = sqlite3.connect(str(SCRAPER_DB))
        cur = con.execute("SELECT fit_score FROM jobs WHERE url = ?", (url,))
        row = cur.fetchone()
        con.close()
        return float(row[0]) if row and row[0] is not None else None
    except Exception as exc:
        print(f"  [warn] scraper DB lookup failed for {url}: {exc}")
        return None


def read_grades_tsv() -> list[dict]:
    """Parse data/grades.tsv → list of row dicts."""
    if not GRADES_TSV.exists():
        print(f"[warn] {GRADES_TSV} not found — no rows to sync.")
        return []

    rows = []
    with GRADES_TSV.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            rows.append(row)
    return rows


def normalize_timestamp(raw: str) -> str | None:
    """Return an ISO-8601 string with UTC timezone, or None."""
    if not raw:
        return None
    raw = raw.strip()
    # Already ISO with timezone
    if raw.endswith("Z") or "+" in raw[10:]:
        return raw
    # Attempt naive parse
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc)
            return dt.isoformat()
        except ValueError:
            continue
    return None


# ── Main sync ────────────────────────────────────────────────────────────────

def main() -> None:
    # Validate env
    if not SUPABASE_URL or SUPABASE_URL == "YOUR_SUPABASE_URL":
        sys.exit(
            "❌  SUPABASE_URL is not set.\n"
            "    Edit .env in the project root and set SUPABASE_URL and SUPABASE_KEY."
        )
    if not SUPABASE_KEY or SUPABASE_KEY == "YOUR_SUPABASE_ANON_OR_SERVICE_KEY":
        sys.exit(
            "❌  SUPABASE_KEY is not set.\n"
            "    Edit .env in the project root and set SUPABASE_URL and SUPABASE_KEY."
        )

    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    rows = read_grades_tsv()
    if not rows:
        print("No rows found in grades.tsv — nothing to sync.")
        return

    jobs_upserted = 0
    evals_inserted = 0
    errors = 0

    for row in rows:
        url = (row.get("url") or row.get("URL") or "").strip()
        company = (row.get("company") or row.get("Company") or "").strip()
        title = (row.get("title") or row.get("Title") or "").strip()
        grade = (row.get("grade") or row.get("Grade") or row.get("career_ops_grade") or "").strip()
        score_raw = (row.get("score") or row.get("Score") or row.get("career_ops_score") or "").strip()
        evaluated_at_raw = (row.get("evaluated_at") or row.get("date") or "").strip()

        if not url:
            print(f"  [skip] row missing url: {row}")
            continue

        try:
            score = float(score_raw) if score_raw else None
        except ValueError:
            score = None

        evaluated_at = normalize_timestamp(evaluated_at_raw)
        ats_platform = detect_ats(url)
        s_score = scraper_score_for(url)
        report_md = find_report(company, url)

        # ── Upsert jobs ──────────────────────────────────────────────────────
        job_payload = {
            "url": url,
            "title": title or None,
            "company": company or None,
            "ats_platform": ats_platform,
            "career_ops_grade": grade or None,
            "career_ops_score": score,
            "scraper_score": s_score,
            "evaluated_at": evaluated_at,
        }

        try:
            result = (
                supabase.table("jobs")
                .upsert(job_payload, on_conflict="url")
                .execute()
            )
            upserted_row = result.data[0] if result.data else None
            job_id = upserted_row["id"] if upserted_row else None
            jobs_upserted += 1
        except Exception as exc:
            print(f"  [error] jobs upsert failed for {url}: {exc}")
            errors += 1
            continue

        # ── Insert evaluation ────────────────────────────────────────────────
        if job_id:
            eval_payload = {
                "job_id": job_id,
                "final_grade": grade or None,
                "final_score": score,
                "report_markdown": report_md or None,
                "evaluated_at": evaluated_at,
            }
            try:
                supabase.table("evaluations").insert(eval_payload).execute()
                evals_inserted += 1
            except Exception as exc:
                print(f"  [error] evaluations insert failed for {url}: {exc}")
                errors += 1

    print()
    print("✅  Supabase sync complete")
    print(f"    Jobs upserted:        {jobs_upserted}")
    print(f"    Evaluations inserted: {evals_inserted}")
    print(f"    Errors:               {errors}")


if __name__ == "__main__":
    main()
