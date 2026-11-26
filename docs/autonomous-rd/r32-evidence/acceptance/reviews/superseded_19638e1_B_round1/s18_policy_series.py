#!/usr/bin/python3 -I
"""只读攻击探针: 冻结快照内的美欧政策利率序列(不与报告值比对,不计入复算点)。

目的: 检验传导链第 2 环主解释前件「央行维持紧缩偏向」在序列面是否有记录。
用法: s18_policy_series.py <research_snapshot.json> <metric_registry.json> <MAP_REPORT.md> <out.json>"""
import json
import os
import sys

snap_p, reg_p, map_p, out_p = sys.argv[1:5]
snap = json.load(open(snap_p, encoding='utf-8'))
reg = json.load(open(reg_p, encoding='utf-8'))
MAP = open(map_p, encoding='utf-8').read()
S = snap['series_store']
ms = reg['metrics']
REG = ms if isinstance(ms, dict) else {m.get('metric_id') or m.get('id'): m for m in ms}

DAYS = ['2025-11-19', '2026-08-19', '2026-09-15', '2026-09-16', '2026-09-17', '2026-10-20', '2026-11-19', '2026-11-23']
out = {}
for m in ['DFEDTARU', 'DFEDTARL', 'FED_FUNDS', 'ECB_DFR', 'ECB_MRO']:
    d, v = S[m]['dates'], S[m]['values']
    idx = {dd: vv for dd, vv in zip(d, v) if vv is not None}
    ch, prev = [], None
    for dd in d:
        vv = idx.get(dd)
        if vv is None:
            continue
        if prev is None or abs(vv - prev) > 1e-9:
            ch.append([dd, vv])
            prev = vv
    e = REG.get(m) or {}
    out[m] = {
        'n': len(d), 'first': d[0], 'last': d[-1],
        'registry': {k: e.get(k) for k in ('status', 'criticality', 'economy')},
        'change_points_last8': ch[-8:],
        'values': {day: idx[day] for day in DAYS if day in idx},
        'net_bp': {
            '12m 2025-11-19→2026-11-19': round((idx['2026-11-19'] - idx['2025-11-19']) * 100, 1) if ('2026-11-19' in idx and '2025-11-19' in idx) else None,
            '3m 2026-08-19→2026-11-19': round((idx['2026-11-19'] - idx['2026-08-19']) * 100, 1) if ('2026-11-19' in idx and '2026-08-19' in idx) else None,
            '1m 2026-10-20→2026-11-19': round((idx['2026-11-19'] - idx['2026-10-20']) * 100, 1) if ('2026-11-19' in idx and '2026-10-20' in idx) else None,
        },
    }
out['MAP_L66_literals'] = {
    'Fed 事后次日生效: 2026-09 决议 09-16→生效 09-17': MAP.count('Fed 事后次日生效: 2026-09 决议 09-16→生效 09-17'),
    'ECB 决议后首个周三生效: 2026-09 决议 09-10→生效 09-16': MAP.count('ECB 决议后首个周三生效: 2026-09 决议 09-10→生效 09-16'),
    '本问计划指标面未纳入美欧政策利率序列': MAP.count('本问计划指标面未纳入美欧政策利率序列'),
}
out['snapshot_header'] = {
    'research_as_of': snap.get('research_as_of'), 'target_date': snap.get('target_date'),
    'series_count': len(S), 'timezone': snap.get('timezone'),
}
os.makedirs(os.path.dirname(out_p), exist_ok=True)
with open(out_p, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
for m in ['DFEDTARU', 'DFEDTARL', 'FED_FUNDS', 'ECB_DFR', 'ECB_MRO']:
    o = out[m]
    print(m, 'n=%d last=%s reg=%s' % (o['n'], o['last'], o['registry']))
    print('   changes:', o['change_points_last8'])
    print('   values:', o['values'])
    print('   net_bp:', o['net_bp'])
print('MAP literals:', out['MAP_L66_literals'])
print('header:', out['snapshot_header'])
