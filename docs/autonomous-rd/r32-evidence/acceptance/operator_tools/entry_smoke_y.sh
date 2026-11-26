#!/bin/zsh
# entry_smoke_y.sh — Audit-R32 任务4 (印章 Y = 36499bb): 用户文档流程冒烟。入口树 final6-entry =
# 干净安装 + 标准更新入口真跑后的树 (update --yes, 回执 YENTRY_update_20261123T235033Z, rc=0,
# 新快照 research_snapshot_20261124): doctor + 四个工单原问 (--question-file 逐字, 取自树内已提交的
# questions/) 只跑 plan 段。不产研判、不 attach、不归档——只证明"干净安装→update→doctor→plan"
# 在最终代码+新快照上端到端可跑。
# 回执: /tmp/r32-accept/out/F6ENTRY_doctor_<ts>.{json,err,rc} + ESMOKE-Y<tag>_plan_<ts>.{json,err,rc}
# 勘误: 本脚本首跑 (2026-11-24 08:15) 的体检行误写成 `research-one --stage doctor`(argparse 拒绝,
# rc=2, 引擎代码未执行; 回执改名 F6ENTRY_doctor_wrongcmd_* 留档), 四个 plan 段回执不受影响。
# 体检改由 doctor_y.sh (`ia_cli.py doctor`) 于 08:2x 单独补跑。
T=/tmp/r32-accept/final6-entry
S=/tmp/r32-accept/scripts
Q=$T/docs/autonomous-rd/r32-evidence/acceptance/questions
zsh "$S/doctor_y.sh"
for pair in "T3:question_T3.txt" "A:question_A.txt" "B:question_B.txt" "N30:question_NEW30.txt"; do
  tag="${pair%%:*}"; q="${pair#*:}"
  zsh "$S/rx.sh" "$T" "ESMOKE-Y$tag" plan --question-file "$Q/$q"
done
echo "entry smoke done $(date '+%F %T')"
