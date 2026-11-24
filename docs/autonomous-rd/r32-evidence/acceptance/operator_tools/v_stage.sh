#!/bin/zsh
# v_stage.sh — final-stamp (V) delivery of the work orders closed at the execution stamp Y (36499bb): carry
#   (byte-identical, sha256-verified; listings out/carry_yz_*_V.txt) -> report/archive (v_deliver.sh)
#   -> replays (v_replay.sh) -> AUG plan-stage re-check (count_late.py).
# Set: A, T3, B, N30 (verdicts at the execution stamp Y), C4 (draft), AUG(plan). B is a same-render package
# (its map was rendered at Y with the round-1 verdict already bound): its strict replay is the Y engine's
# (the recording code); the V engine is refused at gate 4 by design and passes only with the disclosed
# --allow-code-mismatch override (v_replay.sh B override).
# Log: out/v_stage.log.  Run from /tmp/r32-accept after the four final9* trees are built.
set -u
S=/tmp/r32-accept/scripts; O=/tmp/r32-accept/out; A=/tmp/r32-accept
PY=/usr/bin/python3
source $A/env9.sh
L=/tmp/r32-accept/seat_operator.log
V7=$($PY -I -c 'import json,sys; print(json.load(open(sys.argv[1]))["git_head"][:7])' /tmp/r32-accept/final9/CODE_VERSION.json)
echo "$(date '+%Y-%m-%d %H:%M:%S') op stage=v-stage-start stamp=$V7 note=carry+report+archive+replay at V for A/T3/B/N30/C4/AUG(plan)" >> $L
echo "=== carry $(date '+%F %T')"
$PY -I $S/carry_yz.py /tmp/r32-accept/final6 /tmp/r32-accept/final9 "$(basename "$RDY_A")" "$(basename "$RDY_T3")" "$(basename "$RDY_B")" "$(basename "$RDY_N30")" > $O/carry_yz_base_AT3BN30_V.txt 2>&1
echo "carry base (A,T3,B,N30) rc=$? | $(tail -1 $O/carry_yz_base_AT3BN30_V.txt | cut -c1-160)"
$PY -I $S/carry_yz.py /tmp/r32-accept/final6-degraded /tmp/r32-accept/final9-degraded "$(basename "$RDY_C4")" > $O/carry_yz_degraded_C4_V.txt 2>&1
echo "carry degraded (C4) rc=$? | $(tail -1 $O/carry_yz_degraded_C4_V.txt | cut -c1-160)"
$PY -I $S/carry_yz.py /tmp/r32-accept/final6-aug /tmp/r32-accept/final9-aug "$(basename "$RDY_AUG")" > $O/carry_yz_aug_AUG_V.txt 2>&1
echo "carry aug (AUG) rc=$? | $(tail -1 $O/carry_yz_aug_AUG_V.txt | cut -c1-160)"
for t in T3 A B N30; do echo "=== v_deliver $t ($(date '+%T'))"; zsh $S/v_deliver.sh $t; done
echo "=== v_deliver C4 ($(date '+%T'))"; zsh $S/v_deliver.sh C4
for t in T3 A N30; do echo "=== v_replay $t ($(date '+%T'))"; zsh $S/v_replay.sh $t; done
echo "=== v_replay B override ($(date '+%T'))"; zsh $S/v_replay.sh B override
echo "=== AUG plan at V ($(date '+%T'))"
TAUG=/tmp/r32-accept/final9-aug
zsh $S/rx.sh "$TAUG" "VAUG" plan --question-file "$TAUG/docs/autonomous-rd/r32-evidence/acceptance/questions/question_aug.txt"
NEWAUG=$($PY -I -c 'import os,sys; d=sys.argv[1]; print(max(os.listdir(d)))' "$TAUG/output/research_runs")
echo "newest AUG run: $NEWAUG"
$PY -I $S/count_late.py "$TAUG/output/research_runs/$NEWAUG/report.json" > $O/count_late_V.txt 2>&1
echo "count_late rc=$?"; cat $O/count_late_V.txt
echo "=== summary ($(date '+%T'))"
for t in T3 A B N30 C4; do $PY -I $S/zsumm.py $t V; done > $O/vdeliver_summary.txt 2>&1
cat $O/vdeliver_summary.txt | cut -c1-230
echo "$(date '+%Y-%m-%d %H:%M:%S') op stage=v-stage-end" >> $L
echo "=== done $(date '+%F %T')"
