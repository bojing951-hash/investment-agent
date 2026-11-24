#!/bin/zsh
# dv.sh <install_tree> <run_dir> <judgment.json> — read-only attach rehearsal with a saved
# receipt (dryverify.py output + rc) in the operator out area, and a ledger line.
OUT=/tmp/r32-accept/out
J=$(basename "$3" .json)
"$1/.venv/bin/python" -I /tmp/r32-accept/scripts/dryverify.py "$1" "$2" "$3" > "$OUT/dryverify_${J}.txt" 2>&1
rc=$?
echo "rc=$rc" >> "$OUT/dryverify_${J}.txt"
echo "$(date '+%Y-%m-%d %H:%M:%S') op stage=dryverify judgment=$J rc=$rc" >> /tmp/r32-accept/seat_operator.log
echo "$OUT/dryverify_${J}.txt rc=$rc"
