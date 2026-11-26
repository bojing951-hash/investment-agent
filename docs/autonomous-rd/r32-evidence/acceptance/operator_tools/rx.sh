#!/bin/zsh
# rx.sh <install_tree> <tag> <stage> [research-one args...] — formal entry in an
# arbitrary acceptance tree (AUG / degraded). Same envelope convention as r1.sh.
TREE="$1"; shift; TAG="$1"; shift; STAGE="$1"; shift
OUT=/tmp/r32-accept/out
TS=$(date -u +%Y%m%dT%H%M%SZ)
cd "$TREE" || exit 99
PY="$TREE/.venv/bin/python"; [ -x "$PY" ] || PY=python3
"$PY" ia_cli.py research-one --stage "$STAGE" "$@" \
    > "$OUT/${TAG}_${STAGE}_${TS}.json" 2> "$OUT/${TAG}_${STAGE}_${TS}.err"
rc=$?
echo "rc=$rc" > "$OUT/${TAG}_${STAGE}_${TS}.rc"
echo "$(date '+%Y-%m-%d %H:%M:%S') op stage=$STAGE tag=$TAG tree=$(basename $TREE) rc=$rc args=$*" \
    >> /tmp/r32-accept/seat_operator.log
echo "$OUT/${TAG}_${STAGE}_${TS}.json rc=$rc"
