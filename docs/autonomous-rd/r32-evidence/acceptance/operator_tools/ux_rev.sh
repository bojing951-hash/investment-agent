#!/bin/zsh
# ux_rev.sh <install_tree> <tag> "<revision reason>" — standard update entry, same-day re-run:
# `ia_cli.py update --yes --allow-revision --revision-reason "<reason>"` (the entry's documented option for a
# re-run on a day whose snapshot already exists; without it the immutable-snapshot guard refuses, exit 3).
# Output stays outside the tree under /tmp/r32-accept/out/ (same receipts as ux.sh).
TREE="$1"; TAG="$2"; REASON="$3"
OUT=/tmp/r32-accept/out
TS=$(date -u +%Y%m%dT%H%M%SZ)
cd "$TREE" || exit 99
PY="$TREE/.venv/bin/python"; [ -x "$PY" ] || PY=python3
date -u +%Y-%m-%dT%H:%M:%SZ > "$OUT/${TAG}_update_${TS}.meta"
"$PY" ia_cli.py update --yes --allow-revision --revision-reason "$REASON" \
    > "$OUT/${TAG}_update_${TS}.json" 2> "$OUT/${TAG}_update_${TS}.err"
rc=$?
echo "rc=$rc" >> "$OUT/${TAG}_update_${TS}.meta"
date -u +%Y-%m-%dT%H:%M:%SZ >> "$OUT/${TAG}_update_${TS}.meta"
echo "$(date '+%Y-%m-%d %H:%M:%S') op stage=update tag=$TAG tree=$(basename $TREE) rc=$rc args=update --yes --allow-revision --revision-reason <recorded in receipt note> note=($REASON)" \
    >> /tmp/r32-accept/seat_operator.log
echo "$OUT/${TAG}_update_${TS}.json rc=$rc"
