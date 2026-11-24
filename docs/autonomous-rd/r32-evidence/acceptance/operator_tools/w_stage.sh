#!/bin/zsh
# w_stage.sh — final-stamp (W = 24141c01a73daa44e56e380320f46bb0f7cbd723) delivery of the work orders closed at the
# execution stamp Y (36499bb): carry (byte-identical, sha256-verified; listings out/carry_yz_*_W.txt)
#   -> report/archive (w_deliver.sh)  -> replays (w_replay.sh)  -> AUG plan-stage re-check (count_late.py).
# Work orders still under review at Y (B round 2, N30 round 1) are carried and delivered separately after their verdict.
# Log: out/w_stage.log.  Run from /tmp/r32-accept.
set -u
S=/tmp/r32-accept/scripts; O=/tmp/r32-accept/out; A=/tmp/r32-accept
PY=/usr/bin/python3
source $A/env8.sh
L=/tmp/r32-accept/seat_operator.log
echo "$(date '+%Y-%m-%d %H:%M:%S') op stage=w-stage-start note=carry+report+archive+replay at W 24141c0 for A/T3/C4/AUG(plan); seats in flight: B-Y r2, N30-Y r1" >> $L
echo "=== carry $(date '+%F %T')"
$PY -I $S/carry_yz.py /tmp/r32-accept/final6 /tmp/r32-accept/final8 "$(basename "$RDY_A")" "$(basename "$RDY_T3")" > $O/carry_yz_base_AT3_W.txt 2>&1
echo "carry base (A,T3) rc=$? | $(tail -1 $O/carry_yz_base_AT3_W.txt | cut -c1-160)"
$PY -I $S/carry_yz.py /tmp/r32-accept/final6-degraded /tmp/r32-accept/final8-degraded "$(basename "$RDY_C4")" > $O/carry_yz_degraded_C4_W.txt 2>&1
echo "carry degraded (C4) rc=$? | $(tail -1 $O/carry_yz_degraded_C4_W.txt | cut -c1-160)"
$PY -I $S/carry_yz.py /tmp/r32-accept/final6-aug /tmp/r32-accept/final8-aug "$(basename "$RDY_AUG")" > $O/carry_yz_aug_AUG_W.txt 2>&1
echo "carry aug (AUG) rc=$? | $(tail -1 $O/carry_yz_aug_AUG_W.txt | cut -c1-160)"
for t in T3 A C4; do echo "=== w_deliver $t ($(date '+%T'))"; zsh $S/w_deliver.sh $t; done
for t in T3 A; do echo "=== w_replay $t ($(date '+%T'))"; zsh $S/w_replay.sh $t; done
echo "=== AUG plan at W ($(date '+%T'))"
TAUG=/tmp/r32-accept/final8-aug
zsh $S/rx.sh "$TAUG" "WAUG" plan --question-file "$TAUG/docs/autonomous-rd/r32-evidence/acceptance/questions/question_aug.txt"
NEWAUG=$($PY -I -c 'import os,sys; d=sys.argv[1]; print(max(os.listdir(d)))' "$TAUG/output/research_runs")
echo "newest AUG run: $NEWAUG"
$PY -I $S/count_late.py "$TAUG/output/research_runs/$NEWAUG/report.json" > $O/count_late_W.txt 2>&1
echo "count_late rc=$?"; cat $O/count_late_W.txt
echo "=== summary ($(date '+%T'))"
for t in T3 A C4; do $PY -I $S/zsumm.py $t W; done > $O/wdeliver_summary.txt 2>&1
cat $O/wdeliver_summary.txt | cut -c1-230
echo "$(date '+%Y-%m-%d %H:%M:%S') op stage=w-stage-end" >> $L
echo "=== done $(date '+%F %T')"
