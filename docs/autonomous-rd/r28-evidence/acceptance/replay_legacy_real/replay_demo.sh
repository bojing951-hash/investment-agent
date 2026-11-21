#!/bin/bash
# Audit-R28 任务4 实包重放验收: R27 旧真实包(20261117T_修正后 BEI/黄金)
# 候选代码 2679629 重放——旧档 manifest 无 run_code_git_head 键:
#   [0] 严格面(无旗标)→拒(键未记录≠一致)
#   [1] --allow-code-mismatch 披露降级→干净目录一条命令重放(逐字节)
#   [2] 重复运行: 新输出目录+原包逐字节不动
#   [3] 缺件拒绝(副本抽 views_digest.json)
#   [4] 篡改拒绝(副本翻转 MAP_REPORT 一字节)
# 用法: replay_demo_r28.sh <archive_pkg_dir>
set -u
PKG="$1"
BASE=/tmp/r70/r28-accept
INSTALL="$BASE/install"
CLEAN="$BASE/replay-clean"
TS=$(date +%Y%m%dT%H%M%S)
FLAG="--allow-code-mismatch"
echo "=== R28 实包重放验收 $(date '+%F %T') pkg=$PKG ==="
echo "    候选代码=$(python3 -c "import json;print(json.load(open('$INSTALL/CODE_VERSION.json'))['git_head'])")"
mkdir -p "$CLEAN/$TS"
cd "$CLEAN/$TS"

echo "--- [0] 严格面: 旧档键未记录→拒(rc=1) ---"
python3 "$INSTALL/ia_cli.py" research-one --stage replay --package "$PKG" \
  > replay_strict.json 2> replay_strict.err
RC0=$?
python3 -c "
import json
d = json.load(open('replay_strict.json'))
dd = d.get('data') or {}
print('rc=$RC0 blocked=', dd.get('blocked'),
      '| crosscheck_ok=', [c.get('ok') for c in (dd.get('checks') or [])
                            if c.get('check') == 'run_code_sha_crosscheck'])
" 2>/dev/null || { echo "rc=$RC0"; tail -2 replay_strict.err; }

echo "--- [1] 披露降级重放: 干净目录一条命令(逐字节) ---"
python3 "$INSTALL/ia_cli.py" research-one --stage replay --package "$PKG" \
  $FLAG --replay-out "$CLEAN/$TS/out-main" > replay_main.json 2> replay_main.err
RC1=$?
echo "rc=$RC1"
python3 -c "
import json
d = json.load(open('replay_main.json'))
dd = d.get('data') or {}
print('ok=', d.get('ok'), '| render_mode=', dd.get('render_mode'),
      '| checks_n=', dd.get('checks_n'), '| failed=', dd.get('failed_checks'))
xc = [c for c in (dd.get('checks') or []) if c.get('check') == 'run_code_sha_crosscheck']
if xc: print('crosscheck detail:', xc[0].get('detail'))
" 2>/dev/null || tail -3 replay_main.err

echo "--- [2] 重复运行: 新输出目录+原包不动 ---"
BEFORE=$(find "$PKG" -type f | sort | xargs shasum -a 256 | shasum -a 256 | cut -c1-16)
python3 "$INSTALL/ia_cli.py" research-one --stage replay --package "$PKG" \
  $FLAG --replay-out "$CLEAN/$TS/out-repeat" > replay_repeat.json 2>&1
RC2=$?
AFTER=$(find "$PKG" -type f | sort | xargs shasum -a 256 | shasum -a 256 | cut -c1-16)
echo "rc=$RC2 | package_before=$BEFORE package_after=$AFTER unchanged=$([ "$BEFORE" = "$AFTER" ] && echo YES || echo NO)"

echo "--- [3] 缺件拒绝(副本抽 views_digest.json) ---"
CP3="$CLEAN/$TS/pkg-missing"
cp -R "$PKG" "$CP3"
rm "$CP3/views_digest.json"
python3 "$INSTALL/ia_cli.py" research-one --stage replay --package "$CP3" \
  $FLAG > replay_missing.json 2>&1
echo "rc=$?"
python3 -c "
import json
d = json.load(open('replay_missing.json'))
dd = d.get('data') or {}
print('failed_checks=', dd.get('failed_checks'))
" 2>/dev/null || tail -2 replay_missing.json

echo "--- [4] 篡改拒绝(副本翻转 report.md 一字节;该包=非地图问句无 MAP_REPORT) ---"
CP4="$CLEAN/$TS/pkg-tampered"
cp -R "$PKG" "$CP4"
python3 - "$CP4" <<'PY'
import sys, os
p = os.path.join(sys.argv[1], 'report.md')
b = bytearray(open(p, 'rb').read())
i = next(i for i, c in enumerate(b) if c == 0xE5)  # 任一 UTF-8 中文首字节
b[i] = 0xE6
open(p, 'wb').write(bytes(b))
print('tampered byte @', i)
PY
python3 "$INSTALL/ia_cli.py" research-one --stage replay --package "$CP4" \
  $FLAG > replay_tamper.json 2>&1
echo "rc=$?"
python3 -c "
import json
d = json.load(open('replay_tamper.json'))
dd = d.get('data') or {}
fc = dd.get('failed_checks') or []
print('failed_checks:', fc[:4])
" 2>/dev/null || tail -2 replay_tamper.json

echo "=== 重放验收五步完 $(date '+%F %T') 输出根=$CLEAN/$TS ==="
