#!/bin/zsh
# diag_step2.sh <install_tree> <tag> — run the pipeline's step-2 collection script directly, exactly as
# run_weekly.run_step invokes it (venv python, cwd = tree, no arguments), keeping the complete output
# outside the tree (the standard entry keeps only output/critical/stderr tails of the pipeline).
# Purpose: find the cause of a failed step 2 ("A股港股数据采集") of a standard update run.
TREE="$1"; TAG="$2"
OUT=/tmp/r32-accept/out
cd "$TREE" || exit 99
date -u +%FT%TZ > "$OUT/${TAG}_step2diag.meta"
"$TREE/.venv/bin/python" scripts/china_market_collector.py > "$OUT/${TAG}_step2diag.log" 2>&1
rc=$?
echo "rc=$rc" >> "$OUT/${TAG}_step2diag.meta"
date -u +%FT%TZ >> "$OUT/${TAG}_step2diag.meta"
echo "$(date '+%F %T') op stage=step2-diag tag=$TAG tree=$(basename $TREE) rc=$rc note=(pipeline step 2 collector run directly with its full output kept; same invocation as run_weekly.run_step)" \
    >> /tmp/r32-accept/seat_operator.log
echo "rc=$rc"
