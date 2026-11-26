# -*- coding: utf-8 -*-
"""Audit-R20 任务3 真实 VIX 工单回归(R17 工单在其真实数据面上的复算)。

工单原文: 「近一个月VIX飙升而高收益债OAS利差几乎未动,信用市场是否对
股市风险过于自满?」——原运行期面=LIVE data/daily *_20261118.json(本
目录只读副本),截止 2026-11-18。R19 缺陷=读者只看到「月涨38.07%」数字
而无计算窗口;R20 修复后同一面须给出 数字+窗口+两端实测值。

零 LIVE 写入;只读副本上重建快照后走 rmp.asset_move_face(与契约层
asset_returns_echo 同一算术源)。"""
import json
import os
import sys

ROOT = '/tmp/r20_vix'
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import research_map_planner as rmp   # noqa: E402
import snapshot_builder as sb        # noqa: E402

fails = []


def ck(name, ok, detail=''):
    print(('  ✅ ' if ok else ' ❌ ') + name + (f' — {str(detail)[:220]}' if detail else ''))
    if not ok:
        fails.append(name)


dd = os.path.join(ROOT, 'data', 'daily')
sb.build_snapshot(target_ymd='20261118', data_dir=dd, out_dir=dd,
                  as_of='2026-11-18T23:59:00+08:00', trusted_root=ROOT)
snap = json.load(open(os.path.join(dd, 'research_snapshot_20261118.json')))
am = rmp.asset_move_face(snap, ROOT, cutoff='2026-11-18')
vix = next((x for x in am.get('rows') or [] if x.get('metric_id') == 'VIX'), {})
w = vix.get('window') or {}
ck('VIX 月涨=+38.07%(窗口 2026-10-19→2026-11-17,两端实测值随行)',
   abs((vix.get('chg_pct') or 0) - 38.07) < 0.011
   and w.get('from') == '2026-10-19' and w.get('to') == '2026-11-17',
   json.dumps(vix, ensure_ascii=False))

# 读者表行(与 MAP_REPORT 资产表同一 f-string 格式,零另造口径)
if vix:
    line = (f"| VIX | {w.get('from')}..{w.get('to')} | "
            f"{vix['from_value']}→{vix['to_value']} | "
            f"{vix['chg_pct']:+g}%({vix['chg_abs']:+g}) |")
    print('读者表行: ' + line)
    ck('读者行含数字+窗口+两端值(可核)',
       '38.07' in f"{vix['chg_pct']:+g}" and w.get('from') in line)

# 契约同源性: asset_returns_echo 复算入口=同一函数同参
ser = (snap.get('series_store') or {}).get('VIX') or {}
eng = rmp.asset_move_rows({'VIX': ser}, '2026-11-18', months=1)
erow = next((x for x in eng.get('rows') or [] if x.get('metric_id') == 'VIX'), {})
ck('契约层同窗复算逐位一致(echo 回贴可通过)',
   erow.get('chg_pct') == vix.get('chg_pct')
   and (erow.get('window') or {}).get('from') == w.get('from'))

# 其余资产行同面列出(披露)
for r in am.get('rows') or []:
    if r.get('metric_id') != 'VIX':
        rw = r.get('window') or {}
        print(f"  · {r['metric_id']}: {rw.get('from')}..{rw.get('to')} "
              f"{r.get('chg_pct'):+g}%")
ck('窗口规则文案随行(界日最近邻,两端实测日披露)',
   '最近于' in str(am.get('window_rule')))
print('\nVIX 工单回归判定: %d PASS / %d FAIL' % (4 - len(fails), len(fails)))
sys.exit(1 if fails else 0)
