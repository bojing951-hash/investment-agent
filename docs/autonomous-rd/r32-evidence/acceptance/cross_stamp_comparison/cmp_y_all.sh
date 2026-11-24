#!/bin/zsh
# cmp_y_all.sh — key-by-key comparison of the engine deterministic face of every work order
# between stamp X (8f9055d, env5.sh run dirs) and stamp Y (36499bb, env6.sh run dirs).
# Read-only on the run directories; writes out/cmp_Y_<tag>.txt + cmp_Y_condensed.txt.
S=/tmp/r32-accept/scripts; O=/tmp/r32-accept/out
source /tmp/r32-accept/env5.sh
for t in A B T3 N30 C4 AUG; do
  eval "OLD=\$RD_$t"
  eval "NEW=\$(zsh -c 'source /tmp/r32-accept/env6.sh; echo \$RD_$t')"
  /usr/bin/python3 -I $S/cmp_runs.py "$OLD" "$NEW" $O/cmp_Y_$t.txt > $O/cmp_Y_$t.console 2>&1
  echo "cmp Y $t rc=$? | $(grep -c 'REAL DIFF' $O/cmp_Y_$t.txt) sections with real diffs"
done
{
  echo "# cmp_Y_condensed — engine-face comparison X (8f9055d) -> Y (36499bb) per work order (from cmp_Y_<tag>.txt)"
  for t in A B T3 N30 C4 AUG; do
    echo "== $t | $(sed -n '4p' $O/cmp_Y_$t.txt | cut -c1-200)"
    grep '^## ' $O/cmp_Y_$t.txt | cut -c1-200
  done
} > $O/cmp_Y_condensed.txt
grep '^## ' $O/cmp_Y_condensed.txt | awk '{print $3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17}' | sort | uniq -c > $O/cmp_Y_summary.txt
echo "done $(date '+%F %T')"
