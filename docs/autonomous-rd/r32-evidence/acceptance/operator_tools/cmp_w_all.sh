#!/bin/zsh
# cmp_w_all.sh — key-by-key comparison of the engine deterministic face of every work order between
# the execution stamp Y (36499bb; final6* run dirs = env8.sh RDY_*) and the final stamp W (24141c01…: the
# same questions re-planned in the final8* trees by plan_w.sh / w_stage.sh; plan-only runs).
# Read-only on the run directories; writes out/cmp_W_<tag>.txt + .console, cmp_W_condensed.txt, cmp_W_summary.txt.
S=/tmp/r32-accept/scripts; O=/tmp/r32-accept/out
source /tmp/r32-accept/env8.sh
for t in A B T3 N30 C4 AUG; do
  eval "OLD=\$RDY_$t"
  case $t in C4) T=/tmp/r32-accept/final8-degraded;; AUG) T=/tmp/r32-accept/final8-aug;; *) T=/tmp/r32-accept/final8;; esac
  NEW=$(/usr/bin/python3 -I $S/wrun.py "$T" "$OLD") || { echo "cmp W $t: $NEW"; continue; }
  /usr/bin/python3 -I $S/cmp_runs.py "$OLD" "$NEW" $O/cmp_W_$t.txt > $O/cmp_W_$t.console 2>&1
  echo "cmp W $t rc=$? | $(grep -c 'REAL DIFF' $O/cmp_W_$t.txt) sections with real diffs | new run $(basename "$NEW" | cut -c1-16)"
done
{
  echo "# cmp_W_condensed — engine-face comparison Y (36499bb, attached judgment present) -> W (24141c01…, plan-only re-plan) per work order (from cmp_W_<tag>.txt)"
  for t in A B T3 N30 C4 AUG; do
    [ -f $O/cmp_W_$t.txt ] || continue
    echo "== $t | $(sed -n '4p' $O/cmp_W_$t.txt | cut -c1-200)"
    grep '^## ' $O/cmp_W_$t.txt | cut -c1-200
  done
} > $O/cmp_W_condensed.txt
/usr/bin/python3 -I $S/cmp_w_summary.py
echo "done $(date '+%F %T')"
