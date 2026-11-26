#!/bin/zsh
# attach_y.sh <stage> [tag ...] — formal entry <stage> for the Y work orders with the folded
# judgments (A/B/T3/N30 in final6, C4 in final6-degraded, AUG in final6-aug). Explicit variables
# only; no indirect expansion. Tags default to the five review work orders.
STAGE="$1"; shift
[ -n "$STAGE" ] || { echo "usage: attach_y.sh <stage> [tag ...]"; exit 2; }
source /tmp/r32-accept/env6.sh
S=/tmp/r32-accept/scratch_x
R=/tmp/r32-accept/scripts/rx.sh
run_one() {
  local tag="$1"
  local tree rd
  case $tag in
    C4) tree=/tmp/r32-accept/final6-degraded; rd="$RD_C4";;
    AUG) tree=/tmp/r32-accept/final6-aug; rd="$RD_AUG";;
    A) tree=/tmp/r32-accept/final6; rd="$RD_A";;
    B) tree=/tmp/r32-accept/final6; rd="$RD_B";;
    T3) tree=/tmp/r32-accept/final6; rd="$RD_T3";;
    N30) tree=/tmp/r32-accept/final6; rd="$RD_N30";;
    *) echo "unknown tag $tag"; return 1;;
  esac
  if [ "$STAGE" = "attach" ]; then
    zsh $R "$tree" "Y$tag" attach --report-dir "$rd" --judgment "$S/judgment6_$tag.json"
  else
    zsh $R "$tree" "Y$tag" "$STAGE" --report-dir "$rd"
  fi
}
if [ $# -eq 0 ]; then
  for tag in A B T3 N30 C4; do run_one "$tag"; done
else
  for tag in "$@"; do run_one "$tag"; done
fi
