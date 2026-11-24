#!/bin/zsh
# run_gates.sh <outdir> <test_file> ... — run gate tests in the dev tree with the
# system interpreter; one log per file + summary.txt (rc, last gate line).
set -u
OUT="$1"; shift
REPO=~/investment-agent-product
mkdir -p "$OUT"
: > "$OUT/summary.txt"
for f in "$@"; do
  b=$(basename "$f")
  ( cd "$REPO" && python3 "tests/$b" ) > "$OUT/$b.log" 2>&1
  rc=$?
  last=$(grep -E "门:|PASS|FAIL|passed|failed|OK" "$OUT/$b.log" | tail -1 | cut -c1-110)
  printf '%s rc=%s %s\n' "${b#test_}" "$rc" "$last" >> "$OUT/summary.txt"
done
echo "gates done: $(grep -c 'rc=0 ' "$OUT/summary.txt")/$(wc -l < "$OUT/summary.txt" | tr -d ' ') rc=0"
