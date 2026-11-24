#!/bin/zsh
# plan_w.sh — re-plan the five R32 work orders at the final stamp W (24141c01a73daa44e56e380320f46bb0f7cbd723;
# trees final8 / final8-degraded) for the cross-stamp engine-face comparison Y (36499bb) -> W. AUG is re-planned
# by w_stage.sh in final8-aug. Plan stage only (no judgment, no archive); new run directories next to the
# byte-identical carried Y run directories (never touching them). Receipts out/WPLAN-<tag>_plan_<ts>.*;
# logs out/plan_w_*.launcher.log. Two trees in parallel.
S=/tmp/r32-accept/scripts
Q=/docs/autonomous-rd/r32-evidence/acceptance/questions
(
  for pair in "A:question_A.txt" "B:question_B.txt" "T3:question_T3.txt" "N30:question_NEW30.txt"; do
    zsh $S/rx.sh /tmp/r32-accept/final8 "WPLAN-${pair%%:*}" plan --question-file "/tmp/r32-accept/final8$Q/${pair#*:}"
  done
) > /tmp/r32-accept/out/plan_w_base.launcher.log 2>&1 &
(
  zsh $S/rx.sh /tmp/r32-accept/final8-degraded "WPLAN-C4" plan --question-file "/tmp/r32-accept/final8-degraded$Q/question_open.txt"
) > /tmp/r32-accept/out/plan_w_degraded.launcher.log 2>&1 &
wait
echo "plan_w done $(date '+%F %T')"
cat /tmp/r32-accept/out/plan_w_*.launcher.log | cut -c1-200
