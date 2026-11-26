#!/bin/zsh
# doctor_w.sh — Audit-R32 任务4: 用户文档标准入口的只读体检 (`python3 ia_cli.py doctor`), 在入口树
# final8-entry (干净安装 + 标准更新入口真跑后的树) 上运行。回执: out/F8ENTRY_doctor_<ts>.{json,err,rc}
T=/tmp/r32-accept/final8-entry
OUT=/tmp/r32-accept/out
TS=$(date -u +%Y%m%dT%H%M%SZ)
cd "$T" || exit 99
PY="$T/.venv/bin/python"; [ -x "$PY" ] || PY=python3
"$PY" ia_cli.py doctor > "$OUT/F8ENTRY_doctor_${TS}.json" 2> "$OUT/F8ENTRY_doctor_${TS}.err"
rc=$?
echo "rc=$rc" > "$OUT/F8ENTRY_doctor_${TS}.rc"
echo "$(date '+%Y-%m-%d %H:%M:%S') op stage=doctor tag=F8ENTRY tree=final8-entry rc=$rc args=ia_cli.py doctor" >> /tmp/r32-accept/seat_operator.log
echo "$OUT/F8ENTRY_doctor_${TS}.json rc=$rc"
