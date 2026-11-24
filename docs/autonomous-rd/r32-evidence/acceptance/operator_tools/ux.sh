#!/bin/zsh
# ux.sh <install_tree> <tag> — standard update entry per the user doc
# (SKILL.md: `... update --yes`, real collection pipeline). Output stays outside
# the tree under /tmp/r32-accept/out/.
TREE="$1"; TAG="$2"
OUT=/tmp/r32-accept/out
TS=$(date -u +%Y%m%dT%H%M%SZ)
cd "$TREE" || exit 99
PY="$TREE/.venv/bin/python"; [ -x "$PY" ] || PY=python3
date -u +%Y-%m-%dT%H:%M:%SZ > "$OUT/${TAG}_update_${TS}.meta"
"$PY" ia_cli.py update --yes \
    > "$OUT/${TAG}_update_${TS}.json" 2> "$OUT/${TAG}_update_${TS}.err"
rc=$?
echo "rc=$rc" >> "$OUT/${TAG}_update_${TS}.meta"
date -u +%Y-%m-%dT%H:%M:%SZ >> "$OUT/${TAG}_update_${TS}.meta"
echo "$(date '+%Y-%m-%d %H:%M:%S') op stage=update tag=$TAG tree=$(basename $TREE) rc=$rc args=update --yes" \
    >> /tmp/r32-accept/seat_operator.log
echo "$OUT/${TAG}_update_${TS}.json rc=$rc"
