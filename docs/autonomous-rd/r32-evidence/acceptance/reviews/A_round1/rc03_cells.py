# -*- coding: utf-8 -*-
"""rc03: 四地×维度×三锚 22 格逐格直算(series_store + 冻结日历 + 发布规则) vs 引擎格 vs 判断档 anchor_echo。
用法: /usr/bin/python3 -I rc03_cells.py <snapshot.json> <release_calendar.json> <report.json> <agent_judgment.json>
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rc_lib as L
import rc_points as P

snap = L.load(sys.argv[1]); cal = L.load(sys.argv[2])
rep = L.load(sys.argv[3]); aj = L.load(sys.argv[4])
F = L.Face(snap, cal)
cells = rep['research_plan']['point_values']['cells']
echo = {}
for rg in aj['reader_map']['regions']:
    for e in rg['anchor_echo']:
        echo[(rg['region'], e['anchor'], e['metric_id'])] = e
print('research_as_of', snap.get('research_as_of'), 'target_date', snap.get('target_date'))
SEC = '②/⑬点值格'
LEVELS = ('CPI', 'CORE_CPI', 'INDPRO', 'CORE_PCE')
QLEVEL = ('US_REAL_GDP',)
ABS = 'no_published_observation_on_or_before_anchor'
rows = []
for c in cells:
    m = c['metric_id']; rg = c['region']
    for lab, a in c['anchors'].items():
        asof = a['as_of']
        vis = L.visible_latest(F, m, asof)
        obs = vis['obs_date'] if vis else None
        val = vis['value'] if vis else None
        pub = vis['pub_date'] if vis else None
        yoy = None; bstat = None
        if vis:
            if m in LEVELS:
                yoy, bstat, base, _ = L.yoy_level(F, m, obs[:7])
            elif m in QLEVEL:
                yq = '%sQ%d' % (obs[:4], (int(obs[5:7]) - 1) // 3 + 1)
                yoy, bstat, bobs, _ = L.qyoy_level(F, m, yq)
        st = a.get('status')
        e = echo.get((rg, lab, m))
        ok_obs = (a.get('observation_date') == obs)
        if vis is None:
            ok_val = (st == ABS); ok_pub = (a.get('publication_date') in (None, ''))
        else:
            ok_val = (st == 'ok') and P.eq(val, a.get('value'))
            ok_pub = (a.get('publication_date') == pub)
        if m in LEVELS or m in QLEVEL:
            if isinstance(yoy, float):
                ok_yoy = P.eq(round(yoy, 2), a.get('derived_yoy_pct'))
            else:
                ok_yoy = (a.get('yoy_status') == bstat == 'no_same_period_base')
        else:
            ok_yoy = True  # 无同比字段可比(比率/同比/利率序列)
        if e is not None:
            ok_echo = (vis is not None) and P.eq(val, e['value']) and (e['observation_month'] == obs[:7])
        elif vis is None:
            ok_echo = True   # 缺席格不设 echo,相称
        else:
            ok_echo = False   # 引擎有值而判断档缺 echo
        latest_valid = None
        if m in LEVELS and not isinstance(yoy, float):
            mm = F.monthly(m)
            for k in sorted(mm, reverse=True):
                yy, bs, _, _ = L.yoy_level(F, m, k)
                if isinstance(yy, float):
                    latest_valid = {'ym': k, 'yoy': round(yy, 2)}; break
        ok = bool(ok_obs and ok_val and ok_pub and ok_yoy)
        key = 'research_plan.point_values.cells[%s].anchors[%s]' % (m, lab)
        P.add(SEC, 'snapshot.series_store.%s + release_calendar.entries + 注册表发布规则' % m,
              {'obs': obs, 'value': val, 'pub': pub, 'pub_basis': (vis['basis'] if vis else None),
               'yoy': (round(yoy, 4) if isinstance(yoy, float) else yoy), 'yoy_status': bstat, 'latest_valid_yoy': latest_valid},
              {'status': st, 'obs': a.get('observation_date'), 'value': a.get('value'), 'pub': a.get('publication_date'),
               'yoy': a.get('derived_yoy_pct'), 'yoy_status': a.get('yoy_status'), 'latest_valid': a.get('latest_valid_yoy')},
              ok, 'echo_match=%s' % ok_echo, where='report.json:' + key)
        if e is not None:
            P.add(SEC, 'agent_judgment.reader_map.regions[%s].anchor_echo[%s|%s]' % (rg, lab, m),
                  {'value': val, 'observation_month': (obs[:7] if obs else None)},
                  {'value': e['value'], 'observation_month': e['observation_month']},
                  bool(ok_echo), where='判断档 anchor_echo')
        rows.append((rg, m, lab, asof, obs, val, pub, (vis['basis'] if vis else None), (round(yoy, 4) if isinstance(yoy, float) else yoy), bstat, st, ok, ok_echo, latest_valid, a.get('latest_valid_yoy')))
bad = [r for r in rows if (not r[11]) or (r[12] is False)]
for r in rows:
    print(r)
print('BAD rows:', bad)
print('n cells', len(cells), 'anchors total', len(rows))
print('tally', P.tally())
