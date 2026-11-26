#!/bin/zsh
# zdry.sh — dry run (pre-commit check, NOT formal evidence; no ledger line) of the post-fix
# re-delivery on scratch copies of the execution-stamp trees:
#   scratch copies of final6 / final6-degraded (incl. the run dirs and verdict records)
#   + the three modified working-tree files of the fix
#   -> report + archive for A, T3 (approved) and C4 (draft: archive must be refused)
# Receipts: out/zdry/<tag>_{report,archive}.{json,err,rc}; archives: scratch_zdry/arc/<run id>
set -u
S=/tmp/r32-accept/scripts; O=/tmp/r32-accept/out/zdry; D=/tmp/r32-accept/scratch_zdry
DEV=~/investment-agent-product
[ -e "$D" ] && { echo "exists: $D"; exit 2; }
[ -e "$O" ] && { echo "exists: $O"; exit 2; }
mkdir -p $O $D/arc
date '+%F %T start'
rsync -a /tmp/r32-accept/final6/ $D/base/
rsync -a /tmp/r32-accept/final6-degraded/ $D/degraded/
for f in ia_cli.py scripts/agent_judgment.py tests/test_audit_r32_gate.py; do
  cp $DEV/$f $D/base/$f; cp $DEV/$f $D/degraded/$f
done
source /tmp/r32-accept/env6.sh
for tag in A T3 C4; do
  eval "RDY=\$RD_$tag"
  case $tag in C4) T=$D/degraded;; *) T=$D/base;; esac
  RD=${RDY/\/tmp\/r32-accept\/final6-degraded/$D/degraded}; RD=${RD/\/tmp\/r32-accept\/final6/$D/base}
  RID=$(basename "$RD")
  [ -d "$RD" ] || { echo "missing scratch run dir: $RD"; exit 3; }
  cp -p "$RD/MAP_REPORT.md" $O/${tag}_pre.md
  echo "== $tag report ($(date '+%T'))"
  ( cd $T && .venv/bin/python ia_cli.py research-one --stage report --report-dir "$RD" > $O/${tag}_report.json 2> $O/${tag}_report.err; echo $? > $O/${tag}_report.rc )
  echo "report rc=$(cat $O/${tag}_report.rc)"
  echo "== $tag archive ($(date '+%T'))"
  ( cd $T && .venv/bin/python ia_cli.py research-one --stage archive --report-dir "$RD" --archive-dir "$D/arc/$RID" > $O/${tag}_archive.json 2> $O/${tag}_archive.err; echo $? > $O/${tag}_archive.rc )
  echo "archive rc=$(cat $O/${tag}_archive.rc) dir present: $([ -d "$D/arc/$RID" ] && echo yes || echo no)"
done
date '+%F %T end'
