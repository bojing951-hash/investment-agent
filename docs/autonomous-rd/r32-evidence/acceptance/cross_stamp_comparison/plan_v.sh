#!/bin/zsh
# plan_v.sh — re-plan the five R32 work orders at the final stamp V (cf33de3a9942578b71cecb45077b7a505d8fca01; trees final9 / final9-degraded)
# for the cross-stamp engine-face comparison Y (36499bb) -> V. AUG is re-planned by v_stage.sh in final9-aug.
# Plan stage only (no judgment, no archive); new run directories next to the byte-identical carried Y run
# directories (never touching them). Receipts out/VPLAN-<tag>_plan_<ts>.*; logs out/plan_v_*.launcher.log.
# Two trees in parallel.
S=/tmp/r32-accept/scripts
Q=/docs/autonomous-rd/r32-evidence/acceptance/questions
(
  for pair in "A:question_A.txt" "B:question_B.txt" "T3:question_T3.txt" "N30:question_NEW30.txt"; do
    zsh $S/rx.sh /tmp/r32-accept/final9 "VPLAN-${pair%%:*}" plan --question-file "/tmp/r32-accept/final9$Q/${pair#*:}"
  done
) > /tmp/r32-accept/out/plan_v_base.launcher.log 2>&1 &
(
  zsh $S/rx.sh /tmp/r32-accept/final9-degraded "VPLAN-C4" plan --question-file "/tmp/r32-accept/final9-degraded$Q/question_open.txt"
) > /tmp/r32-accept/out/plan_v_degraded.launcher.log 2>&1 &
wait
echo "plan_v done $(date '+%F %T')"
cat /tmp/r32-accept/out/plan_v_*.launcher.log | cut -c1-200
