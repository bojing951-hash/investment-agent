#!/bin/zsh
# doctor_y.sh — Audit-R32 任务4: 用户文档标准入口的只读体检 (`python3 ia_cli.py doctor`, 见
# .claude/skills/global-macro-research/SKILL.md 能力表), 在入口树 final6-entry (干净安装 + 标准更新入口
# 真跑后的树) 上运行。回执: /tmp/r32-accept/out/F6ENTRY_doctor_<ts>.{json,err,rc}
T=/tmp/r32-accept/final6-entry
OUT=/tmp/r32-accept/out
TS=$(date -u +%Y%m%dT%H%M%SZ)
cd "$T" || exit 99
PY="$T/.venv/bin/python"; [ -x "$PY" ] || PY=python3
"$PY" ia_cli.py doctor > "$OUT/F6ENTRY_doctor_${TS}.json" 2> "$OUT/F6ENTRY_doctor_${TS}.err"
rc=$?
echo "rc=$rc" > "$OUT/F6ENTRY_doctor_${TS}.rc"
echo "$(date '+%Y-%m-%d %H:%M:%S') op stage=doctor tag=F6ENTRY tree=final6-entry rc=$rc args=ia_cli.py doctor" >> /tmp/r32-accept/seat_operator.log
echo "$OUT/F6ENTRY_doctor_${TS}.json rc=$rc"
