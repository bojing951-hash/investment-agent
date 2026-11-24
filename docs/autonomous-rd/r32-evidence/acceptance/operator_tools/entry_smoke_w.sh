#!/bin/zsh
# entry_smoke_w.sh — Audit-R32 任务4 (印章 W = 24141c0): 用户文档流程冒烟。入口树 final8-entry =
# 干净安装 + 标准更新入口真跑后的树 (update --yes, 回执 WENTRY_update_*): doctor + 四个工单原问
# (--question-file 逐字, 取自树内已提交的 questions/) 只跑 plan 段。不产研判、不 attach、不归档。
# 回执: out/F8ENTRY_doctor_<ts>.{json,err,rc} + ESMOKE-W<tag>_plan_<ts>.{json,err,rc}
T=/tmp/r32-accept/final8-entry
S=/tmp/r32-accept/scripts
Q=$T/docs/autonomous-rd/r32-evidence/acceptance/questions
zsh "$S/doctor_w.sh"
for pair in "T3:question_T3.txt" "A:question_A.txt" "B:question_B.txt" "N30:question_NEW30.txt"; do
  tag="${pair%%:*}"; q="${pair#*:}"
  zsh "$S/rx.sh" "$T" "ESMOKE-W$tag" plan --question-file "$Q/$q"
done
echo "entry smoke done $(date '+%F %T')"
