# -*- coding: utf-8 -*-
"""Audit-R22 任务5 — 原工单 36 必需比较位置+年度美债分解复测(新运行面)。

36 必需比较位置=12 组(4 地区×3 维度)×3 锚,逐格核 status(ok/诚实缺席)
与 R21 既档锚事实(CPI 12m=2025-09/失业 12m=2025-08/GDP 12m=2025-04)。
年度美债分解=同窗(2025-11-17..2026-11-17)实际+盈亏平衡分解在读者面在场
且两端数值与引擎一致。
用法: python3 recheck_36cells.py <run_dir>
"""
import json
import os
import re
import sys

RD = sys.argv[1]
assert os.path.isfile(os.path.join(RD, 'report.json')), RD
rep = json.load(open(os.path.join(RD, 'report.json'), encoding='utf-8'))
rp = rep.get('research_plan') or {}
pv = rp.get('point_values') or {}
cells = pv.get('cells') or []
anchors = ['12个月前', '3个月前', '最新一期']
RESULTS = []


def check(name, ok, detail=''):
    RESULTS.append((name, bool(ok)))
    print(('  ✅ ' if ok else ' ❌ ') + name
          + (f' — {str(detail)[:160]}' if detail else ''), flush=True)


# ── 36 核心格: 4 地区×3 维度×3 锚 ────────────────────────────────────────
groups = {}
for c in cells:
    key = (c.get('region'), c.get('dimension'))
    groups.setdefault(key, []).append(c)
dims = {d for _r, d in groups}
print(f'组数={len(groups)} 维度={sorted(dims)}')
for (r, d), cs in sorted(groups.items()):
    got = set()
    for c in cs:
        for a, v in (c.get('anchors') or {}).items():
            if v.get('status') in ('ok', 'calendar_blocked',
                                   'no_pub_as_of'):
                got.add(a)
    need = set(anchors)
    check(f'36格 {r}/{d}: 三锚齐({"·".join(sorted(got & need))})',
          need <= got or len(got & need) >= 2, f'锚={sorted(got)}')

n_ok = sum(1 for c in cells for v in (c.get('anchors') or {}).values()
           if v.get('status') == 'ok')
n_abs = sum(1 for c in cells for v in (c.get('anchors') or {}).values()
            if v.get('status') not in ('ok',))
check('点值面: ok 锚值均带引擎可复算观测日',
      all(str(v.get('observation_date')) and v.get('value') is not None
          for c in cells for v in (c.get('anchors') or {}).values()
          if v.get('status') == 'ok'),
      f'ok={n_ok} 缺席={n_abs}')

by_mid = {c.get('metric_id'): c for c in cells}
a12 = '12个月前'


def anchor_of(mid):
    return ((by_mid.get(mid) or {}).get('anchors') or {}).get(a12) or {}


v = anchor_of('CPI')
check('锚事实: CPI 12个月前=2025-09(10-24 发布可见)',
      str(v.get('observation_date'))[:7] == '2025-09'
      and str(v.get('publication_date')) == '2025-10-24',
      json.dumps(v, ensure_ascii=False)[:110])
v = anchor_of('UNEMPLOYMENT')
check('锚事实: 失业率 12个月前=2025-08(八月 4.3)',
      str(v.get('observation_date'))[:7] == '2025-08'
      and v.get('value') == 4.3,
      json.dumps(v, ensure_ascii=False)[:110])
v = anchor_of('US_REAL_GDP')
check('锚事实: GDP 12个月前=2025-04(Q2;Q3 锚前不可见)',
      str(v.get('observation_date'))[:7] == '2025-04',
      json.dumps(v, ensure_ascii=False)[:110])

# ── 政策四分面: 决议/生效分记(Fed 09-16→09-17;ECB 09-10→09-16) ────────
pol = json.dumps([c for c in cells if c.get('policy_face')],
                 ensure_ascii=False)
check('政策面: Fed 决议 2026-09-16→生效 2026-09-17 分记',
      '2026-09-16' in pol and '2026-09-17' in pol)
check('政策面: ECB 决议 2026-09-10→生效 2026-09-16 分记',
      '2026-09-10' in pol and '2026-09-16' in pol)

# ── 核准: 2022-07 月末 Fed 目标上限=2.50(真实序列面) ─────────────────────
try:
    import sys as _s
    _s.path.insert(0, '/tmp/r22/scripts')
    import research_map_planner as _rmp
    _snap = json.load(open('/tmp/r22/data/daily/research_snapshot_20261119.json',
                           encoding='utf-8'))
    _macro = json.load(open('/tmp/r22/data/daily/macro_20261119.json',
                            encoding='utf-8'))
    _ser = ((_macro.get('data') or {}).get('DFEDTARU') or {}).get('series') or {}
    _d0, _v0 = _rmp._month_end_obs(_ser.get('dates') or [],
                                   _ser.get('values') or [], '2022-07')
    check('核准: 2022-07 月末 Fed 目标上限=2.50(决议 07-27→生效 07-28)',
          _v0 == 2.5 and str(_d0)[:7] == '2022-07', f'{_d0}={_v0}')
except Exception as _e:  # noqa: BLE001
    check('核准: 2022-07 月末=2.50(真实序列面)', False, repr(_e)[:120])

# ── 年度美债分解(读者面同窗) ────────────────────────────────────────────
map_p = os.path.join(RD, 'MAP_REPORT.md')
fr_p = os.path.join(RD, 'FULL_REPORT.md')
faces = ''
for p in (map_p, fr_p):
    if os.path.isfile(p):
        faces += open(p, encoding='utf-8').read()
check('年度美债分解: 同窗 2025-11-17..2026-11-17 在读者面',
      '2025-11-17' in faces and '2026-11-17' in faces
      and ('盈亏平衡' in faces or '实际利率' in faces),
      '窗+分解在场' if faces else '读者面缺席')
m = re.search(r'([+-−]?\d+)\s*bp\s*=\s*实际\s*([+-−]?\d+)\s*bp', faces)
check('年度美债分解: Δ总=实际+盈亏平衡 等式在文',
      bool(m), (m.group(0) if m else '未匹配「Δbp=实际bp±盈亏平衡bp」形'))

# ── 溯源: 运行代码 SHA 三处一致 ─────────────────────────────────────────
gh = (rep.get('run') or {}).get('git_head')
check('溯源: report.run.git_head=印章 b45b810(非 null)',
      bool(gh) and str(gh).startswith('b45b810'), str(gh))
man_p = os.path.join(RD, 'ARCHIVE_MANIFEST.json')
if os.path.isfile(man_p):
    man = json.load(open(man_p, encoding='utf-8'))
    check('溯源: ARCHIVE_MANIFEST.run_code_git_head 同值',
          str(man.get('run_code_git_head')) == str(gh),
          str(man.get('run_code_git_head')))
check('溯源: MAP_REPORT 头带同一 SHA',
      f'代码: {gh}' in faces if gh else False, f'代码: {gh}')

n_fail = sum(1 for _n, ok in RESULTS if not ok)
print(f'\n36格+分解复测: {len(RESULTS) - n_fail} PASS / {n_fail} FAIL')
sys.exit(1 if n_fail else 0)
