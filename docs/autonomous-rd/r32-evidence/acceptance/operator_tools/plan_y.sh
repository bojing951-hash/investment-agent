#!/bin/zsh
# plan_y.sh — re-plan the six R32 work orders at the new stamp (trees final6*), plus the
# standard update entry in the clean-install tree. Three trees in parallel; outputs stay
# under /tmp/r32-accept/out/ (rx.sh / ux.sh envelope convention).
S=/tmp/r32-accept/scripts
Q=/docs/autonomous-rd/r32-evidence/acceptance/questions
(
  for pair in "YA:question_A.txt" "YB:question_B.txt" "YT3:question_T3.txt" "YN30:question_NEW30.txt"; do
    zsh $S/rx.sh /tmp/r32-accept/final6 "${pair%%:*}" plan --question-file "/tmp/r32-accept/final6$Q/${pair#*:}"
  done
) > /tmp/r32-accept/out/plan_y_base.launcher.log 2>&1 &
(
  zsh $S/rx.sh /tmp/r32-accept/final6-degraded YC4 plan --question-file "/tmp/r32-accept/final6-degraded$Q/question_open.txt"
) > /tmp/r32-accept/out/plan_y_degraded.launcher.log 2>&1 &
(
  zsh $S/rx.sh /tmp/r32-accept/final6-aug YAUG plan --question-file "/tmp/r32-accept/final6-aug$Q/question_aug.txt"
) > /tmp/r32-accept/out/plan_y_aug.launcher.log 2>&1 &
(
  zsh $S/ux.sh /tmp/r32-accept/final6-entry YENTRY
) > /tmp/r32-accept/out/plan_y_entry.launcher.log 2>&1 &
wait
echo "plan_y done $(date '+%F %T')"
cat /tmp/r32-accept/out/plan_y_*.launcher.log | cut -c1-200
