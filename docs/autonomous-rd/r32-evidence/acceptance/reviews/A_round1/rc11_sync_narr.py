# -*- coding: utf-8 -*-
"""rc11: 历史段『当时同步性』叙述句逐数复算(Audit-R32 A round1; 只读)。
用法: /usr/bin/python3 -I rc11_sync_narr.py <snapshot.json> <run_dir>
复算对象: agent_judgment.reader_map.history_periods[i].other_regions_sync 中
  "截至<截止日>已发布数据显示, 欧元区HICP同比YYYY-MM为V、日本CPI同比…、中国PPI同比…、中国CPI同比…" 的
  观测月与数值(= series_store 该月观测值; 且为截止日前按发布纪律可见的最新观测),
  以及政策维叙述("美国上行一百二十五个基点、三地持平"类)。
所有记录 note 带 [rc11] 标记: 重跑前 /usr/bin/python3 -I rc_clean_mark.py '[rc11] '
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rc_lib as L
import rc_points as P

snap = L.load(sys.argv[1]); RUN = sys.argv[2]
cal = L.load(os.path.join(RUN, 'root_overlay', 'config', 'release_calendar.json'))
F = L.Face(snap, cal)
aj = L.load(os.path.join(RUN, 'agent_judgment.json'))

S8 = '⑧同步面/当时可知'
_add = P.add
P.add = lambda section, src, computed, reported, ok, note='', where='': _add(section, src, computed, reported, ok, note='[rc11] ' + note, where=where)

NM = {'欧元区HICP': 'EA_HICP_YOY', '日本CPI': 'JP_CPI_YOY', '中国PPI': 'CN_PPI_YOY', '中国CPI': 'CN_CPI_YOY'}
CUT = {'2025-03': '2025-03-31', '2022-06': '2022-06-30', '2023-10': '2023-10-31'}
PAT = re.compile(r'(欧元区HICP|日本CPI|中国PPI|中国CPI)同比(\d{4}-\d{2})为(-?[0-9.]+)')
NUMCN = {'零': 0, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}


def vis(name, asof):
    """发布纪律下的最新可见观测。EA_HICP_YOY 两级发布: 日历实录条目优先(RC-EA-HICP-*),
    否则按引擎推定规则『快报=观测月末当日可见』(终值=月末+16日, 见 MAP 当时可知面表注记)。"""
    if name != 'EA_HICP_YOY':
        return L.visible_latest(F, name, asof)
    out = None
    for d, v in F.series(name):
        if d > asof:
            break
        pub, basis = L.release_date(F, name, d)
        if not basis.startswith('calendar:'):
            pub, basis = L.month_end(d[:7]), 'rule:推定(快报月末)'
        if pub <= asof:
            out = {'obs_date': d, 'value': v, 'pub_date': pub, 'basis': basis}
    return out


def cn_num(s):
    """中文数位(十/百/千进制, 如 一百二十五)转整数; 不可解析返回 None。"""
    d = {'零': 0, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}
    u = {'十': 10, '百': 100, '千': 1000}
    total = 0; cur = 0
    for ch in s:
        if ch in d:
            cur = d[ch]
        elif ch in u:
            total += (cur if cur else 1) * u[ch]; cur = 0
        else:
            return None
    return total + cur


for hp in aj['reader_map']['history_periods']:
    c = hp['judgment_cutoff_ym']; s = hp['other_regions_sync']; cut = CUT[c]
    hits = PAT.findall(s)
    comp = []; rep = []
    for lbl, ym, v in hits:
        name = NM[lbl]
        val = F.at(name, ym + '-01')
        if val is None:
            val = F.monthly(name).get(ym)
        vv = vis(name, cut)
        comp.append([ym, round(val, 4), vv['obs_date'][:7], round(vv['value'], 4)])
        rep.append([ym, float(v), ym, float(v)])
    ok = len(hits) == 4 and all(a[0] == b[0] and P.eq(a[1], b[1]) and a[2] == b[2] and P.eq(a[3], b[3]) for a, b in zip(comp, rep))
    P.add(S8, 'history_periods[%s].other_regions_sync "截至%s已发布数据显示,…同比YYYY-MM为V" 四项: (叙述观测月, 序列值, 截止前可见最新观测月, 可见值)' % (c, cut),
          comp, rep, ok,
          note='可见性: 日历实录条目优先; EA_HICP_YOY 无实录条目时按引擎推定规则『快报=观测月末当日』',
          where='agent_judgment.history_periods[%s].other_regions_sync / MAP_REPORT 历史段 "当时同步性"' % c)
    print(c, 'cut', cut)
    for a, b in zip(comp, rep):
        print('    叙述', b[:2], '| 序列值', a[1], '| 规则可见最新', a[2], a[3], '| 可见发布日', L.release_date(F, NM[hits[comp.index(a)][0]], a[2] + '-01') if a[2] else None)
    # 政策维叙述
    m = re.search(r'美国上行(.*?)个基点、三地持平', s)
    if m:
        bp = cn_num(m.group(1))
        a = vis('DFEDTARU', L.month_end(L.add_months(c, -3))); b = vis('DFEDTARU', L.month_end(c))
        a = (a['obs_date'], a['value']); b = (b['obs_date'], b['value'])
        calc = round((b[1] - a[1]) * 100)
        others = []
        for nm in ('CN_LPR_1Y', 'ECB_MRO', 'JP_POLICY_RATE'):  # 与引擎同步面政策维所用序列一致
            x = vis(nm, L.month_end(L.add_months(c, -3))); y = vis(nm, L.month_end(c))
            others.append(None if x is None or y is None else round((y['value'] - x['value']) * 100))
            print('    ', nm, (x['obs_date'], x['value']) if x else None, '->', (y['obs_date'], y['value']) if y else None)
        P.add(S8, 'policy narrative: 美国上行<中文数位>个基点、三地持平(三地=CN_LPR_1Y/ECB_MRO/JP_POLICY_RATE, 发布纪律下截止前可见观测)', [bp, calc, others], [bp, bp, [0, 0, 0]],
              bp is not None and calc == bp and all(o == 0 for o in others), where='history_periods[%s].other_regions_sync 政策维' % c)
        print('    政策叙述 bp 文本', m.group(1), '->', bp, '| DFEDTARU 锚-3月→截止', a, b, calc, '| 三地(CN_LPR_1Y, ECB_MRO, JP_POLICY_RATE) bp', others)
    else:
        print('    政策叙述: 无「美国上行…个基点、三地持平」句')

print('tally', P.tally())
