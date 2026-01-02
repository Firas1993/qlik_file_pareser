#!/usr/bin/env bash
set -euo pipefail

# Workflow runner for months 2024-09 .. 2024-01 (descending)
# Runs two parts per month:
# 1) node xl_2_csv.js <invoice.xlsx> && node read-file-2-db.js output.csv qlik_invoice_raw
# 2) node execute_qlik_delta.js
# Each command is retried once on failure. If both attempts fail, a per-month log is
# written to ./failed_months/failed_<YEAR>_<MM>.log and the script moves to next month.

WORKDIR="$(cd "$(dirname "$0")" && pwd)"
FAILED_DIR="$WORKDIR/failed_months"
mkdir -p "$FAILED_DIR"

YEAR=2024
# Months from Sep to Jan (user requested 2024-09 to 2024-01)
MONTHS=(09 08 07 06 05 04 03 02 01)

run_cmd_with_retry() {
  local cmd="$1"
  local failfile="$2"
  local attempt=1
  local max_attempts=2
  while [ $attempt -le $max_attempts ]; do
    echo "[${FAILFILE:-}] Attempt $attempt: $cmd"
    tmpout=$(mktemp)
    if bash -c "$cmd" >"$tmpout" 2>&1; then
      echo "Command succeeded on attempt $attempt"
      rm -f "$tmpout"
      return 0
    else
      echo "Command failed on attempt $attempt"
      echo "---- attempt $attempt output ----" >> "$failfile"
      cat "$tmpout" >> "$failfile" || true
      echo "---- end attempt $attempt ----" >> "$failfile"
      rm -f "$tmpout"
    fi
    attempt=$((attempt+1))
  done
  return 1
}

for MM in "${MONTHS[@]}"; do
  INVOICE="$WORKDIR/invoice_list_by_month/invoice_${YEAR}_${MM}.xlsx"
  FAILFILE="$FAILED_DIR/failed_${YEAR}_${MM}.log"

  echo "\n===== Processing ${YEAR}-${MM} ====="

  if [ ! -f "$INVOICE" ]; then
    echo "Invoice file missing: $INVOICE" | tee -a "$FAILFILE"
    echo "Skipping ${YEAR}-${MM}"
    continue
  fi

  # Part 1
  PART1="node \"$WORKDIR/xl_2_csv.js\" \"$INVOICE\" && node \"$WORKDIR/read-file-2-db.js\" output.csv qlik_invoice_raw"
  if run_cmd_with_retry "$PART1" "$FAILFILE"; then
    echo "Part 1 succeeded for ${YEAR}-${MM}"
  else
    echo "Part 1 failed after retries for ${YEAR}-${MM}. See $FAILFILE"
    continue
  fi

  # Part 2
  PART2="node \"$WORKDIR/execute_qlik_delta.js\""
  if run_cmd_with_retry "$PART2" "$FAILFILE"; then
    echo "Part 2 succeeded for ${YEAR}-${MM}"
  else
    echo "Part 2 failed after retries for ${YEAR}-${MM}. See $FAILFILE"
    continue
  fi

  echo "Completed ${YEAR}-${MM}"
done

echo "\nAll months processed. Failed logs (if any) are in: $FAILED_DIR"
