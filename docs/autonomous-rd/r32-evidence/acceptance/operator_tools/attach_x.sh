#!/bin/zsh
# attach_x.sh <stage> — formal entry <stage> for the five X work orders with the folded
# judgments (A/B/T3/N30 in final5, C4 in final5-degraded). Explicit variables only.
STAGE="$1"
[ -n "$STAGE" ] || { echo "usage: attach_x.sh <stage>"; exit 2; }
source /tmp/r32-accept/env5.sh
S=/tmp/r32-accept/scratch_x
for pair in "final5:A:$RD_A" "final5:B:$RD_B" "final5:T3:$RD_T3" "final5:N30:$RD_N30" "final5-degraded:C4:$RD_C4"; do
  tree="${pair%%:*}"
  rest="${pair#*:}"
  tag="${rest%%:*}"
  rd="${rest#*:}"
  if [ "$STAGE" = "attach" ]; then
    zsh /tmp/r32-accept/scripts/rx.sh "/tmp/r32-accept/$tree" "X$tag" attach --report-dir "$rd" --judgment "$S/judgment5_$tag.json"
  else
    zsh /tmp/r32-accept/scripts/rx.sh "/tmp/r32-accept/$tree" "X$tag" "$STAGE" --report-dir "$rd"
  fi
done
