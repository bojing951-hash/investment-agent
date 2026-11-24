#!/bin/zsh
# cmp_v_all.sh — key-by-key comparison of the engine deterministic face of every work order between
# the execution stamp Y (36499bb; final6* run dirs = env9.sh RDY_*) and the final stamp V (cf33de3a9942578b71cecb45077b7a505d8fca01: the
# same questions re-planned in the final9* trees by plan_v.sh / v_stage.sh; plan-only runs).
# Read-only on the run directories; writes out/cmp_V_<tag>.txt + .console, cmp_V_condensed.txt, cmp_V_summary.txt.
S=/tmp/r32-accept/scripts; O=/tmp/r32-accept/out
source /tmp/r32-accept/env9.sh
for t in A B T3 N30 C4 AUG; do
  eval "OLD=\$RDY_$t"
  case $t in C4) T=/tmp/r32-accept/final9-degraded;; AUG) T=/tmp/r32-accept/final9-aug;; *) T=/tmp/r32-accept/final9;; esac
  NEW=$(/usr/bin/python3 -I $S/wrun.py "$T" "$OLD") || { echo "cmp V $t: $NEW"; continue; }
  /usr/bin/python3 -I $S/cmp_runs.py "$OLD" "$NEW" $O/cmp_V_$t.txt > $O/cmp_V_$t.console 2>&1
  echo "cmp V $t rc=$? | $(grep -c 'REAL DIFF' $O/cmp_V_$t.txt) sections with real diffs | new run $(basename "$NEW" | cut -c1-16)"
done
{
  echo "# cmp_V_condensed — engine-face comparison Y (36499bb, attached judgment present) -> V (cf33de3…, plan-only re-plan) per work order (from cmp_V_<tag>.txt)"
  for t in A B T3 N30 C4 AUG; do
    [ -f $O/cmp_V_$t.txt ] || continue
    echo "== $t | $(sed -n '4p' $O/cmp_V_$t.txt | cut -c1-200)"
    grep '^## ' $O/cmp_V_$t.txt | cut -c1-200
  done
} > $O/cmp_V_condensed.txt
/usr/bin/python3 -I $S/cmp_v_summary.py
echo "done $(date '+%F %T')"
