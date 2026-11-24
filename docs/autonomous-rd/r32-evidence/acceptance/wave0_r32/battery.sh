#!/bin/zsh
# Battery runner for Audit-R32 (raw logs stay outside the repo).
# Usage: battery.sh <tag> [test_file ...]   (no files => all tests/test_*.py)
# Per-file: python3 tests/<file> ; green = rc in {0,5}.
set -u
TAG="$1"; shift
REPO=~/investment-agent-product
OUT=/tmp/r32-accept/out/battery_${TAG}
mkdir -p "$OUT"
: > "$OUT/summary.tsv"
if [ $# -gt 0 ]; then
  FILES=("$@")
else
  FILES=( ${REPO}/tests/test_*.py )
fi
n=0; pass=0; fail=0
for f in $FILES; do
  b=$(basename "$f")
  n=$((n+1))
  ( cd "$REPO" && python3 "tests/$b" ) > "$OUT/$b.log" 2>&1
  rc=$?
  last=$(grep -E "门:|PASS|FAIL|passed|failed|OK" "$OUT/$b.log" | tail -1 | cut -c1-120)
  if [ $rc -eq 0 ] || [ $rc -eq 5 ]; then
    pass=$((pass+1)); st=PASS
  else
    fail=$((fail+1)); st=FAIL
  fi
  printf '%s\t%s\t%s\t%s\n' "$st" "$rc" "$b" "$last" >> "$OUT/summary.tsv"
done
echo "battery[$TAG] files=$n pass=$pass fail=$fail" | tee "$OUT/total.txt"
