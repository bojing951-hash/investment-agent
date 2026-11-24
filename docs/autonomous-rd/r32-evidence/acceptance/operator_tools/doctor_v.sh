#!/bin/zsh
# doctor_v.sh — Audit-R32 任务4: 用户文档标准入口的只读体检 (`python3 ia_cli.py doctor`), 在入口树
# final9-entry (干净安装 + 标准更新入口真跑后的树) 上运行。回执: out/F9ENTRY_doctor_<ts>.{json,err,rc}
T=/tmp/r32-accept/final9-entry
OUT=/tmp/r32-accept/out
TS=$(date -u +%Y%m%dT%H%M%SZ)
cd "$T" || exit 99
PY="$T/.venv/bin/python"; [ -x "$PY" ] || PY=python3
"$PY" ia_cli.py doctor > "$OUT/F9ENTRY_doctor_${TS}.json" 2> "$OUT/F9ENTRY_doctor_${TS}.err"
rc=$?
echo "rc=$rc" > "$OUT/F9ENTRY_doctor_${TS}.rc"
echo "$(date '+%Y-%m-%d %H:%M:%S') op stage=doctor tag=F9ENTRY tree=final9-entry rc=$rc args=ia_cli.py doctor" >> /tmp/r32-accept/seat_operator.log
echo "$OUT/F9ENTRY_doctor_${TS}.json rc=$rc"
