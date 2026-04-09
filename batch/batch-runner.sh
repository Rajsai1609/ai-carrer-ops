#!/usr/bin/env bash
# batch-runner.sh
# Process multiple JD URLs in parallel using Claude Code workers.
#
# Usage:
#   bash batch/batch-runner.sh <urls-file> [--workers N]
#
# Input file format: one URL per line, # for comments
#
# Output:
#   batch/tracker-additions/{timestamp}-batch.tsv
#   batch/logs/{timestamp}.log

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
LOG_FILE="$SCRIPT_DIR/logs/${TIMESTAMP}.log"
OUTPUT_TSV="$SCRIPT_DIR/tracker-additions/${TIMESTAMP}-batch.tsv"
WORKERS=3
URLS_FILE=""

# ── Argument parsing ──────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --workers|-w)
      WORKERS="$2"
      shift 2
      ;;
    --help|-h)
      echo "Usage: bash batch/batch-runner.sh <urls-file> [--workers N]"
      echo ""
      echo "Options:"
      echo "  --workers N   Number of parallel workers (default: 3)"
      echo "  --help        Show this help"
      echo ""
      echo "Input file: one JD URL per line, # for comments"
      exit 0
      ;;
    *)
      URLS_FILE="$1"
      shift
      ;;
  esac
done

if [[ -z "$URLS_FILE" ]]; then
  echo "Error: URL file is required." >&2
  echo "Usage: bash batch/batch-runner.sh <urls-file> [--workers N]" >&2
  exit 1
fi

if [[ ! -f "$URLS_FILE" ]]; then
  echo "Error: File not found: $URLS_FILE" >&2
  exit 1
fi

# ── Setup ─────────────────────────────────────────────────────────────────────
mkdir -p "$SCRIPT_DIR/logs" "$SCRIPT_DIR/tracker-additions"

echo "Career-Ops Batch Runner" | tee "$LOG_FILE"
echo "Started: $(date)" | tee -a "$LOG_FILE"
echo "Workers: $WORKERS" | tee -a "$LOG_FILE"
echo "Input: $URLS_FILE" | tee -a "$LOG_FILE"
echo "Output: $OUTPUT_TSV" | tee -a "$LOG_FILE"
echo "─────────────────────────────────" | tee -a "$LOG_FILE"

# ── Read URLs ─────────────────────────────────────────────────────────────────
URLS=()
while IFS= read -r line; do
  # Skip blank lines and comments
  [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
  URLS+=("$line")
done < "$URLS_FILE"

TOTAL="${#URLS[@]}"
echo "URLs to process: $TOTAL" | tee -a "$LOG_FILE"

if [[ $TOTAL -eq 0 ]]; then
  echo "No URLs found in $URLS_FILE. Exiting." | tee -a "$LOG_FILE"
  exit 0
fi

# ── TSV header ────────────────────────────────────────────────────────────────
echo -e "#\tDate\tCompany\tRole\tScore\tStatus\tPDF\tReport\tNotes" > "$OUTPUT_TSV"

# ── Worker function ───────────────────────────────────────────────────────────
process_url() {
  local url="$1"
  local idx="$2"
  local batch_prompt="$SCRIPT_DIR/batch-prompt.md"
  local worker_log="$SCRIPT_DIR/logs/${TIMESTAMP}-worker-${idx}.log"

  echo "  [Worker $idx] Processing: $url" | tee -a "$LOG_FILE"

  # Invoke Claude Code with the batch prompt against this URL
  # Output is expected to be a TSV row
  if command -v claude &>/dev/null; then
    result=$(claude --print "$(cat "$batch_prompt")\n\nURL: $url" 2>"$worker_log" || true)
    # Extract TSV row from result (look for tab-separated line starting with date)
    tsv_row=$(echo "$result" | grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}' | head -1 || true)
    if [[ -n "$tsv_row" ]]; then
      echo "$tsv_row" >> "$OUTPUT_TSV"
      echo "  [Worker $idx] ✅ Done" | tee -a "$LOG_FILE"
    else
      echo "  [Worker $idx] ⚠️  No TSV row extracted — check $worker_log" | tee -a "$LOG_FILE"
    fi
  else
    echo "  [Worker $idx] ❌ 'claude' CLI not found — manual processing required" | tee -a "$LOG_FILE"
    # Write placeholder row
    echo -e "-\t$(date +%Y-%m-%d)\t(URL: $url)\t-\t-\tPipeline\t-\t-\tBatch worker failed: claude CLI not found" >> "$OUTPUT_TSV"
  fi
}

# ── Parallel execution ────────────────────────────────────────────────────────
RUNNING=0
IDX=0

for url in "${URLS[@]}"; do
  IDX=$((IDX + 1))
  process_url "$url" "$IDX" &
  RUNNING=$((RUNNING + 1))

  # Wait when we hit max workers
  if [[ $RUNNING -ge $WORKERS ]]; then
    wait -n 2>/dev/null || wait  # wait for any child to finish
    RUNNING=$((RUNNING - 1))
  fi
done

# Wait for remaining workers
wait

echo "─────────────────────────────────" | tee -a "$LOG_FILE"
echo "Batch complete: $(date)" | tee -a "$LOG_FILE"

TSV_ROWS=$(wc -l < "$OUTPUT_TSV")
DATA_ROWS=$((TSV_ROWS - 1))  # exclude header
echo "TSV rows written: $DATA_ROWS / $TOTAL" | tee -a "$LOG_FILE"
echo "Output: $OUTPUT_TSV" | tee -a "$LOG_FILE"

# ── Auto-merge ────────────────────────────────────────────────────────────────
if [[ $DATA_ROWS -gt 0 ]]; then
  echo ""
  echo "Running merge-tracker.mjs..."
  if command -v node &>/dev/null; then
    node "$PROJECT_ROOT/merge-tracker.mjs" 2>&1 | tee -a "$LOG_FILE"
  else
    echo "⚠️  Node.js not found — run 'node merge-tracker.mjs' manually" | tee -a "$LOG_FILE"
  fi
fi

echo ""
echo "✅ Batch processing complete. Check $LOG_FILE for details."
