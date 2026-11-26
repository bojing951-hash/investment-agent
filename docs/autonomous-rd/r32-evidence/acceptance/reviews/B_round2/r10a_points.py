# -*- coding: utf-8 -*-
# r10a_points.py — A 截止时点 / B 锚点格(9×2)与发布纪律
# 用法: /usr/bin/python3 -I r10a_points.py <RUN_DIR> <SNAPSHOT_JSON> <OUT_JSON>
import sys, os, json, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from r00_common import *

RUN, SNAP, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
sn = Snap(load(SNAP))
aj = load(os.path.join(RUN, 'agent_judgment.json'))
cal = load(os.path.join(RUN, 'root_overlay', 'config', 'release_calendar.json'))
reg = load(os.path.join(RUN, 'root_overlay', 'config', 'metric_registry.json'))
PTS = []
EX = {}
CAT = ['']


def cat(c):
    CAT[0] = c


def P(pid, where, key, comp, rep, note='', tol=None):
    disp = round(comp, 6) if isinstance(comp, float) else comp
    ok = same(comp, rep, tol)
    PTS.append({'id': pid, 'cat': CAT[0], 'where': where, 'key': key, 'computed': disp,
                'reported': rep, 'ok': bool(ok), 'note': note})
    print('%s|%s|%s|comp=%s|rep=%s|%s|%s' % ('OK' if ok else 'XX', pid, CAT[0], disp, rep, where, note))
    return ok


cut = dt.date(2026, 11, 23)
cutm3 = dt.date(2026, 8, 23)
try:
    from zoneinfo import ZoneInfo

    def tzc(iso, z):
        return dt.datetime.fromisoformat(iso).astimezone(ZoneInfo(z))
except Exception:
    def tzc(iso, z):
        off = {'America/New_York': -5, 'Europe/Berlin': 1, 'Asia/Tokyo': 9, 'Asia/Shanghai': 8}[z]
        return dt.datetime.fromisoformat(iso).astimezone(dt.timezone.utc) + dt.timedelta(hours=off)


# ---------------- A 截止时点 ----------------
cat('A 截止时点')
ra = sn.sn.get('research_as_of')
P('A01', 'quality_gate_notes[0]「research_as_of 2026-11-23T22:53:47+08:00」', 'snapshot.research_as_of', ra, '2026-11-23T22:53:47+08:00')
for i, (nm, z, rep) in enumerate([('纽约', 'America/New_York', '09:53'), ('法兰克福', 'Europe/Berlin', '15:53'),
                                  ('东京', 'Asia/Tokyo', '23:53'), ('上海', 'Asia/Shanghai', '22:53')]):
    P('A%02d' % (2 + i), 'quality_gate_notes[0]「截止时点%s %s」' % (nm, rep),
      'snapshot.research_as_of 换算 %s' % z, tzc(ra, z).strftime('%H:%M'), rep)
P('A06', '各月窗窗启日 2026-10-23(交易日)', '日历: 2026-10-23 星期', weekday('2026-10-23'), 'Fri')
P('A07', 'quality_gate_notes[0]「NIKKEI225 止于 2026-11-20 收盘」', 'series_store.NIKKEI225.dates[-1]',
  sn.last('NIKKEI225')[0].isoformat(), '2026-11-20')
P('A08', '同上(2026-11-20 应为周五)', '日历: 2026-11-20 星期', weekday('2026-11-20'), 'Fri')
P('A09', '截止日 2026-11-23 为周一', '日历: 2026-11-23 星期', weekday('2026-11-23'), 'Mon')
for i, sid in enumerate(['SPX', 'VIX', 'DXY', 'GOLD_F', 'EURUSD', 'USDJPY']):
    P('A%02d' % (10 + i), 'quality_gate_notes[0]「SPX、VIX、GOLD_F、DXY 与外汇的当日值均为截止时点的盘中快照」',
      'series_store.%s.dates[-1]' % sid, sn.last(sid)[0].isoformat(), '2026-11-23')
for i, sid in enumerate(['UST_10Y', 'TIPS_10Y', 'UST_2Y']):
    P('A%02d' % (16 + i), '传导环3「利率序列止于 2026-11-19」', 'series_store.%s.dates[-1]' % sid,
      sn.last(sid)[0].isoformat(), '2026-11-19')
P('A19', '传导环1「BEI_10Y 2.15(观测 2026-11-20)」', 'series_store.BEI_10Y.dates[-1]', sn.last('BEI_10Y')[0].isoformat(), '2026-11-20')

# ---------------- B 锚点格 ----------------
cat('B 锚点格')
regions = aj['reader_map']['regions']
cells = []
for rg in regions:
    for c in rg['anchor_echo']:
        cells.append(c)
EX['anchor_cells'] = cells
n = 0
for c in cells:
    n += 1
    sid = c['metric_id']
    d = c['observation_month']
    dd = D(d + '-01') if len(d) == 7 else D(d)
    v = sn.val(sid, dd)
    P('B%02d' % n, 'reader_map.%s.anchor_echo[%s]' % (c['metric_id'], c['anchor']), sn.key(sid, dd), v, c['value'],
      '观测月 %s' % d)
# 锚点纪律(观测面): 「最新一期」= 序列在截止日前最新观测; 「3个月前」锚的发布纪律见 r30 的 B' 组
n = 20
for rg in regions:
    for c in rg['anchor_echo']:
        sid = c['metric_id']
        dd = D(c['observation_month'] + '-01') if len(c['observation_month']) == 7 else D(c['observation_month'])
        if c['anchor'] == '最新一期':
            n += 1
            P('B%02d' % n, '%s「最新一期」应为截止日前最新观测' % sid, 'series_store.%s.dates[-1]' % sid,
              sn.last(sid)[0].isoformat(), dd.isoformat())
        else:
            # 「3个月前」锚的发布纪律(锚观测发布日 ≤ 锚日 < 下一观测发布日)在 r30 的 B' 组逐指标核验, 此处不重复
            pass
EX['series_tail'] = {sid: [sn.first(sid)[0].isoformat(), sn.last(sid)[0].isoformat(), len(sn.series(sid))]
                     for sid in ['CPI', 'CORE_CPI', 'CORE_PCE', 'INDPRO', 'UNEMPLOYMENT', 'US_REAL_GDP',
                                 'EA_HICP_YOY', 'EA_REAL_GDP_YOY', 'JP_POLICY_RATE']}
EX['cells_values'] = {c['metric_id'] + '@' + c['observation_month']: sn.val(
    c['metric_id'], D(c['observation_month'] + '-01') if len(c['observation_month']) == 7 else D(c['observation_month']))
    for c in cells}

json.dump({'points': PTS, 'extra': EX}, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('POINTS', len(PTS), 'MISMATCH', sum(1 for p in PTS if not p['ok']))
