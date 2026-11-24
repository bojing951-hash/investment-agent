#!/bin/zsh
# entry_smoke.sh — Audit-R32 任务4: 用户文档流程冒烟(入口树 final5-entry = 干净安装 +
# 标准更新入口真跑后的树; 快照 research_snapshot_20261124): doctor + 四个工单原问
# (--question-file 逐字, 取自树内已提交的 questions/)只跑 plan 段。不产研判、不 attach、
# 不归档——只证明"干净安装→update→doctor→plan"在最终代码+新快照上端到端可跑。
# 回执: /tmp/r32-accept/out/ESMOKE_<tag>_plan_<ts>.{json,err,rc} + ESMOKE_summary.txt
source /tmp/r32-accept/env5.sh
T=/tmp/r32-accept/final5-entry
S=/tmp/r32-accept/scripts
OUT=/tmp/r32-accept/out
Q=$T/docs/autonomous-rd/r32-evidence/acceptance/questions
for pair in "T3:question_T3.txt" "A:question_A.txt" "B:question_B.txt" "N30:question_NEW30.txt"; do
  tag="${pair%%:*}"; q="${pair#*:}"
  zsh "$S/rx.sh" "$T" "ESMOKE-$tag" plan --question-file "$Q/$q"
done
