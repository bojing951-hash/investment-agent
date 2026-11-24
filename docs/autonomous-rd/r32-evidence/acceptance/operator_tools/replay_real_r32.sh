#!/bin/bash
# Audit-R32 任务3 实包重放验收(R29 六步模板参数化):
# 引擎与工作根可注入——本地包+验收树引擎,或 GitHub 重下包+干净目录
# git archive 引擎(离线重放,按 manifest 版本),同一判据:
#   [0] 严格面→绿(逐字节+冻结三查+终裁绑定)
#   [1] 更换本地日历→仍逐字节(root=包内 overlay,本地现状零影响)
#   [2] 重复重放: 新输出目录+原包不动
#   [3] 缺冻结件→拒
#   [4] 篡改冻结件一字节→拒
#   [5] manifest 冻结摘要单侧改写→拒
# 用法: replay_real_r32.sh <archive_pkg_dir> <tag> [engine_dir] [workroot]
# 解释器 = 引擎自带 venv(<engine_dir>/.venv/bin/python;与验收树同建法),无 venv 回落 python3。
set -u
PKG="$1"; TAG="$2"
ENGINE=${3:-/tmp/r32-accept/install}
WORKROOT=${4:-/tmp/r32-accept/replay-$TAG}
PY="$ENGINE/.venv/bin/python"; [ -x "$PY" ] || PY=python3
TS=$(date +%Y%m%dT%H%M%S)
mkdir -p "$WORKROOT/$TS"
cd "$WORKROOT/$TS"
J() { python3 -c "
import json
d = json.load(open('$1'))
dd = d.get('data') or {}
print('ok=', d.get('ok'), '| mode=', dd.get('render_mode'),
      '| blocked=', dd.get('blocked'), '| failed=', dd.get('failed_checks'))
fz = {c.get('check'): c.get('ok') for c in (dd.get('checks') or [])
      if (c.get('check') or '').startswith(('frozen', 'verdict_binding'))}
print('frozen/binding:', fz)
print('all checks:', {c.get('check'): c.get('ok') for c in (dd.get('checks') or [])})
" 2>/dev/null || { echo "parse-fail"; tail -2 "$1.err" 2>/dev/null; }; }

echo "=== R32 实包重放验收 $(date '+%F %T') tag=$TAG engine=$ENGINE ==="
echo "pkg=$PKG"

echo "--- [0] 严格面(无旗标) ---"
"$PY" "$ENGINE/ia_cli.py" research-one --stage replay --package "$PKG" \
  --replay-out "$WORKROOT/$TS/out0" > r0.json 2> r0.err; RC0=$?
echo "rc=$RC0"; J r0.json
cp out0/MAP_REPLAY_RENDER.md m0.md 2>/dev/null

echo "--- [1] 更换本地日历→重放不变 ---"
CAL="$ENGINE/config/release_calendar.json"
cp "$CAL" cal.bak
python3 - "$CAL" <<'PY'
import json, sys
p = sys.argv[1]
d = json.load(open(p))
d['entries'] = (d.get('entries') or []) + [{
    'entry_id': 'R30-SWAP-TEST', 'metric_id': 'CN_LPR_1Y',
    'obs_from': '2026-11-01', 'obs_to': '2026-11-30',
    'first_publish_on_or_after': '2026-11-99', 'time': '23:59'}]
json.dump(d, open(p, 'w'), ensure_ascii=False, indent=2)
PY
"$PY" "$ENGINE/ia_cli.py" research-one --stage replay --package "$PKG" \
  --replay-out "$WORKROOT/$TS/out1" > r1.json 2> r1.err; RC1=$?
echo "rc=$RC1"; J r1.json
if cmp -s m0.md out1/MAP_REPLAY_RENDER.md; then echo "map bytes: IDENTICAL"; else echo "map bytes: DIFFER ❌"; fi
cp cal.bak "$CAL"

echo "--- [1b] 独立引擎目录移去本地日历 RC-EA-HICP-2022M06 → 仍 rc=0+逐字节(R31 任务2: 重放绑包内冻结日历,引擎本地日历现状零影响) ---"
EMINUS="$WORKROOT/$TS/engine-minus-rc"
rm -rf "$EMINUS"; cp -R "$ENGINE" "$EMINUS"
python3 - "$EMINUS/config/release_calendar.json" <<'PY'
import json, sys
p = sys.argv[1]
d = json.load(open(p))
n0 = len(d.get('entries') or [])
d['entries'] = [e for e in (d.get('entries') or [])
                if e.get('entry_id') != 'RC-EA-HICP-2022M06']
json.dump(d, open(p, 'w'), ensure_ascii=False, indent=2)
print('entries: %d → %d (RC-EA-HICP-2022M06 removed)' % (n0, len(d['entries'])))
PY
"$PY" "$EMINUS/ia_cli.py" research-one --stage replay --package "$PKG" \
  --replay-out "$WORKROOT/$TS/out1b" > r1b.json 2> r1b.err; RC1B=$?
echo "rc=$RC1B"; J r1b.json
if cmp -s m0.md out1b/MAP_REPLAY_RENDER.md; then echo "map bytes: IDENTICAL"; else echo "map bytes: DIFFER ❌"; fi

echo "--- [2] 重复重放: 新目录+原包不动 ---"
BEFORE=$(find "$PKG" -type f -exec shasum {} \; | sort | shasum)
"$PY" "$ENGINE/ia_cli.py" research-one --stage replay --package "$PKG" \
  --replay-out "$WORKROOT/$TS/out2" > r2.json 2> r2.err; RC2=$?
AFTER=$(find "$PKG" -type f -exec shasum {} \; | sort | shasum)
echo "rc=$RC2"; J r2.json
[ "$BEFORE" = "$AFTER" ] && echo "package: UNTOUCHED" || echo "package: MUTATED ❌"
cmp -s m0.md out2/MAP_REPLAY_RENDER.md && echo "map bytes: IDENTICAL" || echo "map bytes: DIFFER ❌"

echo "--- [3] 缺冻结件→拒 ---"
P3="$WORKROOT/$TS/pkg-miss"; rm -rf "$P3"; cp -R "$PKG" "$P3"
rm -f "$P3/root_overlay/config/release_calendar.json"
python3 "$ENGINE/ia_cli.py" research-one --stage replay --package "$P3" \
  > r3.json 2> r3.err; RC3=$?
echo "rc=$RC3 (期望≠0)"; J r3.json

echo "--- [4] 篡改冻结件一字节→拒 ---"
P4="$WORKROOT/$TS/pkg-tamper"; rm -rf "$P4"; cp -R "$PKG" "$P4"
python3 - "$P4" <<'PY'
import sys
p = sys.argv[1] + '/root_overlay/config/release_calendar.json'
b = open(p, 'rb').read()
open(p, 'wb').write(b.replace(b'"version"', b'"versionX"', 1))
PY
python3 "$ENGINE/ia_cli.py" research-one --stage replay --package "$P4" \
  > r4.json 2> r4.err; RC4=$?
echo "rc=$RC4 (期望≠0)"; J r4.json

echo "--- [5] manifest 冒冻摘要单侧改写→拒 ---"
P5="$WORKROOT/$TS/pkg-rewr"; rm -rf "$P5"; cp -R "$PKG" "$P5"
python3 - "$P5" <<'PY'
import json, sys
p = sys.argv[1] + '/ARCHIVE_MANIFEST.json'
d = json.load(open(p))
d['frozen_inputs']['config/release_calendar.json'] = 'deadbeef'
json.dump(d, open(p, 'w'), ensure_ascii=False, indent=2, default=str)
PY
python3 "$ENGINE/ia_cli.py" research-one --stage replay --package "$P5" \
  > r5.json 2> r5.err; RC5=$?
echo "rc=$RC5 (期望≠0)"; J r5.json

echo "=== R32 实包重放验收毕 tag=$TAG ==="
