#!/usr/bin/env python3
"""make_expectations_gap_judgment.py <data_tree> <report.json> <out.json> <judgment_path> [code_root]

席位侧工具(Agent 研究席判定档装配;引擎不调用,不属任何自动链路)。
Audit-R33 任务5: 问句问到「预期差」的地图型工单(五面地图+预期差对照块)。
  - 五面环境叙述(四地三时点/转折/传导/历史类比/事后表现): 按引擎分面块
    模板装配,数值与日期一律由引擎面代入,零手敲、零网络;
  - 预期差判断: 引擎候选与须席位推导行逐行给出判定;须席位推导的解读、
    竞争解释与证伪判据为席位撰写并固化于本脚本(按行号绑定),数值取自
    引擎定价曲线与规则池;
  - L3 正文(矛盾陈述/机制链): 中文数字为主,事实水平以「指标 水平为 X」
    回贴引擎;L4 情景阈值为席位自设。
守卫: 只装配「美/中/欧/日四地+问到预期差」且须席位推导行集合与本脚本
预设一致的工单;引擎报出预期差候选、定价缺席或证据配置改变时拒绝装配,
须席位另写判定档。
写出前自检: 纪律校验 + 契约验证,不绿不写。"""
import bisect
import datetime
import json
import os
import re
import sys

if len(sys.argv) < 5:
    sys.exit('usage: make_expectations_gap_judgment.py <data_tree> <report.json> '
             '<out.json> <judgment_path> [code_root]')
tree, rp, _out, jp_out = sys.argv[1:5]
# 数据根(工单冻结输入)与代码根分离: 数据树内可以没有代码
code_root = (sys.argv[5] if len(sys.argv) > 5 else os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
for _p in (os.path.join(code_root, 'scripts'),
           os.path.join(code_root, 'scripts', 'research_contract'),
           code_root):
    if _p not in sys.path:
        sys.path.insert(0, _p)

rep = json.load(open(rp, encoding='utf-8'))
plan = rep.get('research_plan') or {}
blk = plan.get('expectations_gap') or {}
run = rep.get('run') or {}
as_of = plan.get('cutoff')


def refuse(msg):
    sys.exit('make_expectations_gap_judgment: %s ——须席位另写判定档' % msg)


LABELS = ('12个月前', '3个月前', '最新一期')
REGIONS = ('US', 'CN', 'EA', 'JP')
REG_TXT = {'US': '美国', 'CN': '中国', 'EA': '欧元区', 'JP': '日本'}
DIM_TXT = {'growth': '增长', 'inflation': '通胀', 'policy': '政策'}
# 席位指标名(水平序列带引擎派生同比者标「同比」;其余为序列原口径)
NAME = {
    'US_REAL_GDP': '实际GDP同比', 'UNEMPLOYMENT': '失业率',
    'INDPRO': '工业生产同比', 'CPI': 'CPI同比', 'CORE_CPI': '核心CPI同比',
    'CORE_PCE': '核心PCE同比', 'DFEDTARU': '联邦基金目标区间上限',
    'DFF': '有效联邦基金利率', 'CN_PMI_MFG': '制造业PMI(同比变动)',
    'CN_CPI_YOY': 'CPI同比', 'CN_PPI_YOY': 'PPI同比',
    'CN_POLICY_OVERNIGHT': '央行隔夜逆回购利率(政策利率锚)',
    'CN_OMO_7D': '7天逆回购利率', 'CN_LPR_1Y': 'LPR(1年)',
    'EA_REAL_GDP_YOY': '实际GDP同比', 'EA_HICP_YOY': 'HICP同比',
    'ECB_MRO': '主要再融资利率', 'ECB_DFR': '存款便利利率',
    'JP_REAL_GDP_YOY': '实际GDP同比', 'JP_CPI_YOY': '全国CPI同比',
    'JP_CPI_TOKYO_YOY': '东京都CPI同比',
    'JP_POLICY_RATE': '无担保隔夜拆借利率(月均)',
    'FED_FUNDS': '联邦基金有效利率'}
# 须席位推导行: 行号 → (指标, 引擎状态, 席位判定)
AUTHORED = {
    'VIEW-20261110-003#f2': ('FED_FUNDS', 'reading_required', 'supported'),
    'VIEW-20261111-002#f3': ('US_REAL_GDP', 'reading_required', 'not_a_gap'),
}
NUM_PATHS = ('VIEW-20261111-004#f1', 'VIEW-20261111-004#f2',
             'VIEW-20261111-006#f1')
STALE_ROWS = ('VIEW-20261110-005#f1', 'VIEW-20261110-005#f2',
              'VIEW-20261110-006#f1')
EXPOST_SERIES = (('DFEDTARU', 'pp'), ('UNEMPLOYMENT', 'pp'), ('CPI', '%'),
                 ('INDPRO', '%'), ('SPX', '%'), ('NIKKEI225', '%'),
                 ('DAX', '%'), ('SHCOMP', '%'), ('GOLD_F', '%'),
                 ('DXY', '%'), ('UST_10Y', 'pp'))
SYNC_KNOWN = ('CN_PPI_YOY', 'CN_CPI_YOY', 'EA_HICP_YOY', 'JP_CPI_YOY')
ANALOG_DIM_CN = {'growth': '增长', 'inflation': '通胀', 'rates': '利率',
                 'credit': '信用', 'volatility': '波动', 'valuation': '估值'}
FEAT_SFX = {'d12m': ' 12月变化', 'level': ' 水平', '4w_avg': ' 4周均值',
            'rv21': ' 21日已实现波动'}
D = '零一二三四五六七八九'

# ── 守卫: 本脚本只覆盖证据配置与预设一致的工单 ──────────────────────
if not (plan.get('map_question') and blk.get('asked') is True
        and blk.get('schema') == 'r33-expectations-gap'):
    refuse('工单不是「问到预期差」的地图型问句')
if not as_of or set(plan.get('regions') or []) != set(REGIONS):
    refuse('须有研究截止日且地区为美/中/欧/日四地')
sm = blk.get('summary') or {}
rows_all = [r for r in blk.get('rows') or [] if isinstance(r, dict)]
rows = {r.get('row_id'): r for r in rows_all}
if sm.get('candidate_n') or sm.get('inconsistent_n'):
    refuse('引擎已报预期差候选/不一致行——候选行须席位逐行研判')
must = sorted(r.get('row_id') for r in rows_all
              if r.get('candidate') or r.get('status') == 'reading_required')
if must != sorted(AUTHORED):
    refuse('须席位推导行集合与本脚本预设不符(%s)' % must)
for rid, (mid, st, _v) in AUTHORED.items():
    r = rows[rid]
    if r.get('metric_id') != mid or r.get('status') != st:
        refuse('须席位推导行配置改变(%s: %s/%s)' % (
            rid, r.get('metric_id'), r.get('status')))


def hg(r):
    return (r.get('comparison') or {}).get('horizon_gap') or {}


for rid in NUM_PATHS:
    r = rows.get(rid) or {}
    if not (r and r.get('status') == 'consistent' and hg(r).get('assessable')
            and hg(r).get('material') is False):
        refuse('编号加息路径行配置改变(%s)' % rid)
pr = blk.get('pricing') or {}
prow = pr.get('rows') or []
if (pr.get('status') != 'present' or pr.get('metric_id') != 'FED_FUNDS'
        or len(prow) < 6
        or not all(isinstance(x.get('change_bp'), (int, float))
                   and x['change_bp'] >= 0 for x in prow)
        or not float(prow[-1]['change_bp']) > float(prow[0]['change_bp'])):
    refuse('联邦基金利率期货定价缺席或曲线非累计上调')
for rid in STALE_ROWS:
    r = rows.get(rid) or {}
    if not (r.get('status') == 'consistent_stale_fact' and (
            (r.get('facts') or {}).get('at_cutoff') or {}).get('stale')):
        refuse('欧日政策利率行配置改变(%s)' % rid)
dis = {d.get('metric_id'): d for d in blk.get('disagreements') or []}
if not {'FED_FUNDS', 'SPX_EPS', 'CN_REAL_GDP_YOY'} <= set(dis):
    refuse('机构间分歧面配置改变')
pv = plan.get('point_values') or {}
cells = pv.get('cells') or []
trio = plan.get('us_rates_trio') or {}
amv = plan.get('asset_moves') or {}
cands = (plan.get('turning_candidates') or {}).get('candidates') or []
clusters = (plan.get('policy_event_clusters') or {}).get('clusters') or []
steps = {s.get('step'): s for s in rep.get('steps') or []}
analog = ((steps.get('S6_analog') or {}).get('envelope') or {}).get('data') or {}
top = analog.get('top') or []
if len(cands) < 3 or trio.get('status') != 'ok' or not amv.get('rows') \
        or len(top) < 3:
    refuse('转折候选/三利率分解/资产月窗/相似检索面缺席')
fw = blk.get('falsification_window') or {}
wt = blk.get('window_testability') or {}
if not (isinstance(fw, dict) and fw.get('months') and fw.get('end')
            and fw.get('start')):
    refuse('问句未指定证伪窗口')
NEED_STORE = ('BRENT_F', 'SPX', 'NIKKEI225', 'DAX', 'SHCOMP', 'GOLD_F',
              'DXY', 'UST_10Y', 'DFEDTARU', 'UNEMPLOYMENT', 'CPI', 'INDPRO')
NEED_L1 = ('DFF', 'ECB_DFR', 'JP_POLICY_RATE', 'SPX_EPS', 'UST_10Y',
           'TIPS_10Y', 'BEI_10Y', 'SPX', 'HY_OAS')

import research_map_planner as rmp                                # noqa: E402
from research_contract import judgment_contract as jc             # noqa: E402

face = jc.build_face(rep)
store = face.get('series_store') or {}
l1 = {r.get('metric_id'): r
      for r in ((rep.get('layers') or {}).get('L1_事实层') or {}).get('rows')
      or []}
if any(mid not in store for mid in NEED_STORE) or any(
        mid not in l1 for mid in NEED_L1):
    refuse('传导/历史/正文所需序列或事实行不在证据面')


# ── 数值/日期字面与小工具 ─────────────────────────────────────────────
def fmt(v):
    """引擎面数值字面: 整数值不带小数点(4.0→4),其余保留原精度。"""
    if v is None:
        return '不可得'
    f = float(v)
    return str(int(f)) if f.is_integer() else repr(f)


def f2(v):
    return '%+.2f' % v


def _cn_int(n):
    if n < 10:
        return D[n]
    if n < 100:
        t, o = divmod(n, 10)
        return (D[t] if t > 1 else '') + '十' + (D[o] if o else '')
    return str(n)


def cn_num(v):
    """1.25→一点二五; 6.5→六点五; 25.0→二十五; 12.5→十二点五"""
    s = ('%.4f' % float(v)).rstrip('0').rstrip('.')
    if '.' in s:
        a, _, b = s.partition('.')
        return _cn_int(int(a)) + '点' + ''.join(D[int(c)] for c in b)
    return _cn_int(int(s))


def cn_amt(v):
    """带「两」口语的整数(2→两);小数同 cn_num。"""
    s = ('%.4f' % float(v)).rstrip('0').rstrip('.')
    if '.' not in s and int(s) == 2:
        return '两'
    return cn_num(v)


def ym_shift(ym, n):
    y, m = int(ym[:4]), int(ym[5:7])
    t = y * 12 + (m - 1) + n
    return '%04d-%02d' % (t // 12, t % 12 + 1)


def steps_of(bp, step_bp):
    """定价读数折合整步数(向上取整): 69bp@25bp→3;12.5bp@25bp→1。"""
    return int(-(-float(bp) // float(step_bp)))


def horizon_row(h_end, pricing_rows, pref=None):
    """到期日当月或之前最后一个有读数的合约月(与引擎 _pricing_reference
    同规则: 无读数的合约月跳过;引擎已附 pricing_reference 时以其月份为准)
    → 该行;无→None。"""
    if isinstance(pref, dict) and pref.get('month'):
        row = next((x for x in pricing_rows
                    if x.get('month') == pref.get('month')), None)
    else:
        cands = [x for x in pricing_rows
                 if str(x.get('month')) <= str(h_end or '')[:7]
                 and isinstance(x.get('change_bp'), (int, float))]
        row = cands[-1] if cands else None
    return row


def month_last(mid, ym):
    """月末口径观测(与契约 _month_last_obs 同算法)。"""
    ser = store.get(mid) or {}
    dates, values = ser.get('dates') or [], ser.get('values') or []
    if not dates:
        return None, None
    j = bisect.bisect_right(dates, ym + '-31') - 1
    while j >= 0 and (j >= len(values) or values[j] is None):
        j -= 1
    return (dates[j], values[j]) if j >= 0 else (None, None)


def last_obs(mid):
    ser = store.get(mid) or {}
    for d, v in zip(reversed(ser.get('dates') or []),
                    reversed(ser.get('values') or [])):
        if v is not None:
            return d, v
    return None, None


def obs_at(mid, date):
    """≤date 的最新观测 (date, value)(与 month_last 同算法)。"""
    ser = store.get(mid) or {}
    dates, values = ser.get('dates') or [], ser.get('values') or []
    j = bisect.bisect_right(dates, date) - 1
    while j >= 0 and (j >= len(values) or values[j] is None):
        j -= 1
    return (dates[j], values[j]) if j >= 0 else (None, None)


def mon_series(mid, yoy=False):
    """月序列 [(ym, date, value)]: yoy=水平序列转同比空间(引擎转折探测
    同算法),否则月末口径(引擎 _monthly_last 同算法)。"""
    ser = store.get(mid) or {}
    dates, values = ser.get('dates') or [], ser.get('values') or []
    if not dates:
        return []
    if yoy:
        try:
            return rmp._monthly_series_for_turning(dates, values,
                                                   ser.get('unit')) or []
        except (TypeError, ValueError, ZeroDivisionError):
            return []
    return rmp._monthly_last(dates, values) or []


def days_before(d):
    """观测日距研究截止日的天数(观测晚于截止日→负;不可算→None)。"""
    try:
        return (datetime.date.fromisoformat(str(as_of)[:10])
                - datetime.date.fromisoformat(str(d)[:10])).days
    except (ValueError, TypeError):
        return None


def level_txt(mid):
    """「指标 水平为 X(观测 日[,距截止日N天])」——证据索引有该指标快照事实
    引用时才写(契约按快照事实回贴);天数用中文数字(陈述内不引入未绑定
    数值)。"""
    r, ref = l1.get(mid), ref_for(mid)
    if not (r and ref and r.get('value') is not None):
        return None
    lag = days_before(r.get('observation_date'))
    out = '%s 水平为 %s(观测 %s' % (mid, fmt(r.get('value')),
                                  r.get('observation_date'))
    if lag is not None and lag > 0:
        out += ',距截止日%s天' % cn_num(lag)
    return out + ')'


def ref_for(mid):
    """证据索引内该指标的首个快照事实引用。"""
    for e in rep.get('evidence_index') or []:
        if e.get('kind') == 'snapshot_fact' and str(
                e.get('ref') or '').startswith(mid + '@'):
            return e['ref']
    return None


def refs(*mids):
    return [x for x in (ref_for(m) for m in mids) if x]


def cell_name(mid):
    return NAME.get(mid) or mid


def cand_name(c):
    return NAME.get(c.get('metric_id')) or re.sub(
        r'[((].*$', '', c.get('display_name') or c.get('metric_id'))


def anchor(c, lbl):
    return (c.get('anchors') or {}).get(lbl) or {}


def yoy_of(c, lbl):
    """锚格可比数值(水平序列取引擎派生同比)。"""
    a = anchor(c, lbl)
    if a.get('status') != 'ok' or a.get('value') is None:
        return None
    if str(a.get('value_kind') or '').startswith('level'):
        return a.get('derived_yoy_pct')
    return a.get('value')


def cell_by_id(mid):
    return next((c for c in cells if c.get('metric_id') == mid), None)


def short_inst(name):
    return re.sub(r'\s*[((].*$', '', str(name)).strip()


def feat_cn(feat):
    base = str(feat)
    for s in ('_d12m', '_level', '_4w_avg', '_rv21'):
        if base.endswith(s):
            return base[:-len(s)] + FEAT_SFX[s[1:]]
    return base


# ── 面一: 四地三时点走位 ──────────────────────────────────────────────
regions = []
for reg in REGIONS:
    dim_parts, echo, pol = [], [], []
    for dim in ('growth', 'inflation', 'policy'):
        items = []
        for c in cells:
            if c.get('region') != reg or c.get('dimension') != dim:
                continue
            vals, obs, note = [], [], ''
            for lbl in LABELS:
                a = anchor(c, lbl)
                if a.get('status') != 'ok' or a.get('value') is None:
                    vals.append('不可得')
                    obs.append(None)
                    continue
                od = str(a.get('observation_date') or '')
                obs.append(od[:7])
                echo.append({'anchor': lbl, 'metric_id': c['metric_id'],
                             'value': a.get('value'),
                             'observation_month': od[:7]})
                if str(a.get('value_kind') or '').startswith('level'):
                    if a.get('derived_yoy_pct') is None:
                        vals.append('同比不可得')
                        note = '(%s锚缺同比基期,水平值 %s)' % (
                            lbl, fmt(a.get('value')))
                    else:
                        vals.append(fmt(a.get('derived_yoy_pct')))
                else:
                    vals.append(fmt(a.get('value')))
            items.append('%s %s(观测 %s)%s' % (
                cell_name(c['metric_id']), '→'.join(vals),
                '→'.join(o or '—' for o in obs), note))
        if items:
            dim_parts.append('%s: %s' % (DIM_TXT[dim], '、'.join(items)))
    for c in cells:
        if c.get('region') != reg or c.get('dimension') != 'policy':
            continue
        nm = cell_name(c['metric_id'])
        a12, a0 = anchor(c, LABELS[0]), anchor(c, LABELS[2])
        if (a12.get('status') == 'ok' and a0.get('status') == 'ok'
                and a12.get('value') is not None
                and a0.get('value') is not None):
            pol.append('%s %spp' % (nm, f2(float(a0['value']) -
                                           float(a12['value']))))
        else:
            pol.append('%s 不可比(12个月前锚前无已发布观测)' % nm)
    regions.append({
        'region': reg,
        'from_to': (
            '%s三时点走位(12个月前→3个月前→最新一期;数值取锚日当时可得'
            '观测,水平序列的同比由引擎严格同期派生)——%s。政策利率较 '
            '12 个月前锚: %s。' % (REG_TXT[reg], '；'.join(dim_parts),
                                  '、'.join(pol) or '无政策利率格')),
        'anchor_echo': echo})

# ── 面二: 三个转折 ────────────────────────────────────────────────────
order = sorted(cands, key=lambda c: -abs(float(c.get('delta') or 0)))
picked = []
for c in order:
    if len(picked) == 3:
        break
    if c['metric_id'] in {p['metric_id'] for p in picked}:
        continue
    picked.append(c)
if len({p.get('dimension') for p in picked}) < 2:
    for c in order:
        if (c.get('dimension') not in {p.get('dimension') for p in picked}
                and c['metric_id'] not in {p['metric_id'] for p in picked}):
            picked[-1] = c
            break
if len(picked) != 3 or len({p.get('dimension') for p in picked}) < 2:
    refuse('转折候选不足以取三个跨维度转折')
if any(c['metric_id'] not in store for c in picked):
    refuse('转折指标序列不在证据面')
events = [e for cl in clusters for e in cl.get('events') or []]
# Audit-R33 任务5修订(独立预审 M3): 月均型政策序列(日本)没有阶梯变动点,
# 引擎事件簇不收录——按引擎 _policy_window_path 取窗内相邻月上行点,相邻月
# 并为段(段内变动点之和),与美/欧事件并列,政策计数不漏日本。


def policy_path(mid):
    """近 12 个月政策序列路径(引擎同算法: 变动点日=生效日;美/欧决议日=
    惯例回推,月均序列无决议日语义)。"""
    ser = store.get(mid) or {}
    return rmp._policy_window_path(ser.get('dates') or [],
                                   ser.get('values') or [], as_of, 12, mid,
                                   True) or {}


def rise_segments(mid):
    """月均政策序列窗内上行点合并为段 [{from_ym,to_ym,bp,n,v0,v1}]。"""
    segs = []
    for e in sorted(policy_path(mid).get('events') or [],
                    key=lambda x: str(x.get('date'))):
        if float(e.get('delta_bp') or 0) <= 0:
            continue
        ym = str(e.get('date'))[:7]
        if segs and ym_shift(segs[-1]['to_ym'], 1) == ym:
            g = segs[-1]
            g.update(to_ym=ym, bp=g['bp'] + int(e['delta_bp']), n=g['n'] + 1,
                     v1=e.get('to'))
        else:
            segs.append({'from_ym': ym, 'to_ym': ym,
                         'bp': int(e['delta_bp']), 'n': 1,
                         'v0': e.get('from'), 'v1': e.get('to')})
    return segs


monthly_events = []
for _mid in ('JP_POLICY_RATE', 'CN_POLICY_OVERNIGHT', 'CN_LPR_1Y',
             'CN_OMO_7D'):
    # 只补引擎事件簇未收录、且为月频(日期落在月初)的政策序列
    _ds = (store.get(_mid) or {}).get('dates') or []
    if (not _ds or any(e.get('metric_id') == _mid for e in events)
            or not all(str(d).endswith('-01') for d in _ds[-6:])):
        continue
    _reg = next((c.get('region') for c in cells
                 if c.get('metric_id') == _mid), None)
    for _g in rise_segments(_mid):
        monthly_events.append({
            'region': _reg, 'metric_id': _mid, 'monthly_segment': True,
            'from_ym': _g['from_ym'], 'to_ym': _g['to_ym'],
            'from': _g['v0'], 'to': _g['v1'], 'delta_bp': _g['bp'],
            'date': '%s-01' % _g['from_ym'], 'effective_date': None})
events_all = events + monthly_events


def ev_txt(e):
    if e.get('monthly_segment'):
        return ('%s→%s %s %s 月均序列上行段 %s→%s(+%dbp;月均口径,无单一'
                '生效日)' % (
                    e['from_ym'], e['to_ym'],
                    REG_TXT.get(e.get('region'), e.get('region')),
                    cell_name(e.get('metric_id')), fmt(e.get('from')),
                    fmt(e.get('to')), int(e.get('delta_bp') or 0)))
    return '%s %s %s %s→%s(%+d bp;生效 %s)' % (
        e.get('date'), REG_TXT.get(e.get('region'), e.get('region')),
        cell_name(e.get('metric_id')), fmt(e.get('from')), fmt(e.get('to')),
        int(e.get('delta_bp') or 0), e.get('effective_date'))


def is_level(mid):
    a = ((cell_by_id(mid) or {}).get('anchors') or {}).get(LABELS[2]) or {}
    return str(a.get('value_kind') or '').startswith('level')


LEVEL_NAME = {'CN_PMI_MFG': '制造业PMI', 'CPI': 'CPI指数',
              'CORE_CPI': '核心CPI指数', 'INDPRO': '工业生产指数',
              'US_REAL_GDP': '实际GDP', 'CORE_PCE': '核心PCE指数'}


def level_name(mid):
    return LEVEL_NAME.get(mid) or cell_name(mid).replace(
        '同比变动', '').replace('同比', '')


def cand_full(c):
    return REG_TXT.get(c.get('region'), '') + cand_name(c)


def trio_vals(mid, with_region=False):
    c = cell_by_id(mid)
    if not c:
        return '%s 不可得' % cell_name(mid)
    pre = REG_TXT.get(c.get('region'), '') if with_region else ''
    return '%s%s %s→%s→%s' % (pre, cell_name(mid),
                            fmt(yoy_of(c, LABELS[0])),
                            fmt(yoy_of(c, LABELS[1])),
                            fmt(yoy_of(c, LABELS[2])))


def pol_trio(reg):
    return '、'.join(trio_vals(c['metric_id']) for c in cells
                     if c.get('dimension') == 'policy'
                     and c.get('region') == reg) or '无政策利率格'


def region_flat(reg):
    """该地区政策利率格(三时点可比者)是否全部持平。"""
    ok = False
    for c in cells:
        if c.get('dimension') != 'policy' or c.get('region') != reg:
            continue
        v = [yoy_of(c, lbl) for lbl in LABELS]
        if None in v:
            continue
        ok = True
        if len(set(v)) != 1:
            return False
    return ok


def pol_ctx(reg):
    """某地区转折的政策背景: 本地区事件与三时点、同期其他地区事件。"""
    own = [e for e in events_all if e.get('region') == reg]
    others = [e for e in events_all if e.get('region') != reg]
    parts = []
    if own:
        parts.append('本地区政策事件(冻结发布日历实录与序列变动点;月均序列'
                     '按相邻月上行段): ' + '、'.join(ev_txt(e) for e in own))
    else:
        parts.append('窗内未识别到本地区政策事件(冻结发布日历实录与序列变动点)')
    parts.append('本地区政策利率三时点: %s' % pol_trio(reg))
    if others:
        o = '同期其他地区政策事件: ' + '、'.join(ev_txt(e) for e in others)
        if reg == 'CN' and region_flat(reg) and any(
                float(e.get('delta_bp') or 0) > 0 for e in others):
            o += '(本地区政策利率可比者三时点持平,未跟进其他地区的收紧)'
        parts.append(o)
    else:
        parts.append('同期其他地区无政策事件')
    return ';'.join(parts) + '。'


n_cand = len(cands)
turnings = []
for c in picked:
    to_ym, from_ym = str(c['to_ym']), str(c['from_ym'])
    dim = c.get('dimension') or ''
    dlt = float(c.get('delta') or 0)
    k_dim = 1 + sum(1 for x in cands if x.get('dimension') == dim and abs(
        float(x.get('delta') or 0)) > abs(dlt))
    k_all = order.index(c) + 1
    arrow = '升至' if dlt > 0 else '降至'
    same_win = [x for x in cands if x is not c and x.get('to_ym') == to_ym]
    o_txt = '、'.join('%s[%s] %s→%s' % (
        cand_full(x), DIM_TXT.get(x.get('dimension'), ''),
        fmt(x.get('value_before')), fmt(x.get('value_after')))
        for x in same_win) or '无'
    first = (
        '%s维候选面按幅度%s的转折=%s自 %s %s %s(%s→%s;候选面为三个月变化窗、'
        '共 %d 项,本项按变动幅度排第 %d 位——幅度排序仅为选取规则,跨指标'
        '单位不一);同窗(终点 %s)候选面另有: %s;月频分辨率下同窗先后'
        '未定,不作单一先动者主张。' % (
            DIM_TXT.get(dim, dim),
            '居首' if k_dim == 1 else '排第 %d 位' % k_dim,
            cand_full(c), fmt(c.get('value_before')), arrow,
            fmt(c.get('value_after')), from_ym, to_ym, n_cand, k_all, to_ym,
            o_txt))
    d_to, v_to = month_last(c['metric_id'], to_ym)
    d_l, v_l = last_obs(c['metric_id'])
    if is_level(c['metric_id']):
        after = (
            '本指标转折月之后的读数(水平口径): %s %s 月末 %s → 最新 %s@%s'
            '(同比口径: 转折月 %s → 最新一期锚 %s)' % (
                level_name(c['metric_id']), to_ym, fmt(v_to), fmt(v_l), d_l,
                fmt(c.get('value_after')),
                fmt(yoy_of(cell_by_id(c['metric_id']), LABELS[2]))))
    else:
        after = ('本指标转折月之后的读数: %s %s 月末 %s → 最新 %s@%s' % (
            cand_full(c), to_ym, fmt(v_to), fmt(v_l), d_l))
    follow = '跟进/背离: %s;%s月频分辨率下同窗先后未定。' % (
        after, pol_ctx(c.get('region')))
    turnings.append({
        'metric_id': c['metric_id'], 'date': to_ym, 'before_date': from_ym,
        'value_before': c.get('value_before'),
        'value_after': c.get('value_after'), 'dimension': dim,
        'first_mover': first, 'follow_or_diverge': follow})

# 引擎补选(并项后不足三项时)交还席位: 位置关系只按候选窗起止月记述,
# 月频分辨率下不主张单一先动者;本地区同维读数与政策利率如实列出
_eps, picks = rmp.turning_merge_and_picks(turnings, cands)
turning_supplement = []
for c in picks:
    c_from, c_to = str(c.get('from_ym')), str(c.get('to_ym'))
    p_to = max(str(p['to_ym']) for p in picked)
    p_from = min(str(p['from_ym']) for p in picked)
    if c_from > p_to:
        pos = '该转折窗(%s→%s)位于已列三窗(终点 %s)之后' % (c_from, c_to, p_to)
    elif c_to < p_from:
        pos = '该转折窗(%s→%s)位于已列三窗(起点 %s)之前' % (
            c_from, c_to, p_from)
    else:
        pos = '该转折窗(%s→%s)与已列三窗在时间上交叠' % (c_from, c_to)
    reg = c.get('region')
    same_reg = [x for x in cells if x.get('region') == reg
                and x.get('dimension') == c.get('dimension')
                and x.get('metric_id') != c.get('metric_id')]
    fm = (
        '引擎补选(已列转折同轮并项后不足三项,由引擎按候选面变动幅度补足): '
        '%s自 %s %s %s(%s→%s);%s;月频分辨率下不主张其为单一先动者。' % (
            cand_full(c), fmt(c.get('value_before')),
            '升至' if float(c.get('delta') or 0) > 0 else '降至',
            fmt(c.get('value_after')), c_from, c_to, pos))
    fd = (
        '跟进/背离: 本地区同维三时点(12个月前→3个月前→最新一期): %s;'
        '本地区政策利率三时点: %s。' % (
            '、'.join(trio_vals(x['metric_id']) for x in same_reg) or '无同维格',
            pol_trio(reg)))
    turning_supplement.append({
        'metric_id': c.get('metric_id'), 'to_ym': c_to,
        'first_mover': fm, 'follow_or_diverge': fd,
        'resolution_note': (
            '月频分辨率下无法分辨本项与已列转折、其他地区同维读数的先后;'
            '位置关系只按候选窗起止月记述。'),
        'evidence_gap': '缺更高频读数与跨国同步证据,无法分辨先后'})

# ── 面四: 历史类比(引擎相似检索前三段) ──────────────────────────────
fwm = int(analog.get('feature_window_months') or 12)
cmeta = analog.get('candidates') or {}
valid_n = cmeta.get('valid')
n_cl = cmeta.get('n_independent_clusters_topN') or len(top)
sv = analog.get('state_vector') or {}
agree = (analog.get('dispersion') or {}).get('topN_aftermath_sign_agreement') or {}
a_warns = [str(w) for w in
           (((steps.get('S6_analog') or {}).get('envelope') or {}).get('warnings')
            or [])]
hist = []
for t in top[:3]:
    a = str(t.get('candidate_month'))
    w = rmp.ex_post_windows(a)
    hist.append({'anchor_ym': a, 'judgment_cutoff_ym': a,
                 'match_window': {'start_ym': ym_shift(a, -(fwm - 1)),
                                  'end_ym': a},
                 'aftermath_obs_months': [w['3m'], w['6m'], w['12m']]})
aof = rmp.history_asof_face(hist, rep)
syncf = rmp.history_region_sync_face(hist, rep, root=tree)
if len(aof.get('periods') or []) < len(hist) or len(
        syncf.get('periods') or []) < len(hist):
    refuse('历史类比当时可知面/地区同步面缺席')


def ex_post_txt(i, key):
    h = hist[i]
    tgt = h['aftermath_obs_months'][('3m', '6m', '12m').index(key)]
    a = h['anchor_ym']
    parts = []
    for mid, unit in EXPOST_SERIES:
        _d0, v0 = month_last(mid, a)
        _d1, v1 = month_last(mid, tgt)
        if v0 is None or v1 is None:
            parts.append('%s 数据不可得' % mid)
        elif unit == 'pp':
            parts.append('%s %+.2fpp' % (mid, float(v1) - float(v0)))
        else:
            parts.append('%s %+.2f%%' % (mid, (float(v1) / float(v0) - 1.0)
                                         * 100.0))
    return ('%s月末→%s月末: %s(月末口径;期末非交易日时与行情面两口径数值'
            '可差约1个百分点)' % (a, tgt, '、'.join(parts)))


cur_from = ym_shift(as_of[:7], -(fwm - 1))
res_from = ym_shift(as_of[:7], -12)
history_periods = []
for i, (h, t) in enumerate(zip(hist, top[:3])):
    a = h['anchor_ym']
    dims = t.get('dims') or {}
    shares = sorted(((k, float((v or {}).get('contribution_share') or 0))
                     for k, v in dims.items() if v), key=lambda kv: -kv[1])
    share_txt = '+'.join('%s维 %.1f%%' % (ANALOG_DIM_CN.get(k, k), s * 100)
                         for k, s in shares if s >= 0.001)
    top2 = [ANALOG_DIM_CN.get(k, k) for k, _ in shares[:2]]
    warn = next((w for w in a_warns if w.startswith(a + ':')), '')
    sim = ('相似检索距离 %.4f(状态向量六维: 增长/通胀/利率/信用/波动/估值),'
           '在 %s 个有效候选的 TOP-%s 独立簇中排第 %s(距离分位 %.1f);'
           '贡献=%s,相似主要来自%s的组合。相似≠因果,更非预测。%s' % (
               float(t.get('distance') or 0), valid_n, n_cl, t.get('rank'),
               float(t.get('distance_percentile') or 0), share_txt,
               '与'.join(top2) or '—',
               ('引擎提示: ' + warn + '。') if warn else ''))
    fd = t.get('features_detail') or {}
    gaps = sorted(((k, float(v.get('gap') or 0)) for k, v in fd.items()
                   if isinstance(v, dict) and abs(float(v.get('gap') or 0))
                   > 1.0), key=lambda kv: -abs(kv[1]))
    diff_parts = ['%s(%s,%+.2f)' % (
        feat_cn(k), '当前高于候选期' if g > 0 else '候选期高于当前', g)
        for k, g in gaps] or ['六维特征差异均在一个标准差内']
    miss = t.get('missing_features') or {}
    miss_txt = (';候选月缺席特征: ' + '、'.join(
        '%s(%s)' % (feat_cn(k), v) for k, v in miss.items())) if miss else ''
    difference = '差异(标准差距离,绝对值大于一者): ' + '、'.join(diff_parts) \
        + miss_txt
    kp = (aof.get('periods') or [{}] * 3)[i]
    sp = (syncf.get('periods') or [{}] * 3)[i]
    srows = [r for r in sp.get('rows') or [] if r.get('region') != 'US']
    n_all = len(srows)
    n_sync = sum(1 for r in srows if str(r.get('label_sync') or '')
                 .startswith('同步'))
    by_dim = {}
    for r in srows:
        by_dim.setdefault(r.get('dimension'), []).append(
            '%s%s' % (REG_TXT.get(r.get('region'), r.get('region')),
                      r.get('label_sync')))
    dim_txt = '；'.join('%s维: %s' % (DIM_TXT.get(d, d), '、'.join(v))
                       for d, v in by_dim.items())
    if n_all and n_sync == n_all:
        head = '全部同步'
    elif n_sync == 0:
        head = '均不同步'
    else:
        head = '部分同步(引擎「地区×维度同步面」%d 格中 %d 格同步——%s)' % (
            n_all, n_sync, dim_txt)
    known = [k for k in kp.get('known') or []
             if k.get('metric_id') in SYNC_KNOWN]
    kt = '、'.join('%s%s为%s' % (k.get('label'), k.get('obs_month'),
                                fmt(k.get('value'))) for k in known)
    sync = ('{%s}: 截至%s已发布数据显示,%s。' % (
        head, kp.get('cutoff_end'), kt) if kt else
        '{%s}: 当时可知的非美价格读数缺席。' % head)
    w3, w12 = h['aftermath_obs_months'][0], h['aftermath_obs_months'][2]
    cov = '、'.join('%s维 %.2f' % (ANALOG_DIM_CN.get(k, k), float(
        (v or {}).get('coverage') or 0)) for k, v in sv.items())
    _n_ag = {k: round(float(v) * n_cl) for k, v in agree.items()}
    _full = [k for k, x in _n_ag.items() if x >= n_cl]
    _rest = sorted(x for k, x in _n_ag.items() if x < n_cl)
    ag_txt = ''
    if _full:
        ag_txt = '%s 共%s个窗口内%s簇全同号' % (
            '、'.join(_full), cn_num(len(_full)), cn_num(n_cl))
    if _rest:
        ag_txt += ';其余 %d 个窗口为%s簇同号' % (
            len(_rest), cn_num(_rest[0]) if _rest[0] == _rest[-1]
            else '%s至%s' % (cn_num(_rest[0]), cn_num(_rest[-1])))
        ag_txt += '(样本内已有分歧)'
    m0 = h['match_window']['start_ym']
    _ov = ['%s 个月窗(至 %s)%s重叠' % (
        lbl, tgt, '' if (a <= as_of[:7] and res_from <= tgt) else '不')
        for lbl, tgt in zip(('3', '6', '12'), h['aftermath_obs_months'])]
    note = ('样本注记: 检索范围=%s 个有效候选(六维状态向量,特征窗 %d 个月),'
            'TOP-%s 为独立簇;各维特征覆盖: %s;匹配区间(%s 至 %s)与当前特征窗'
            '(%s 至 %s)%s;事后窗与研究窗(自 %s 起)的重叠: %s%s;TOP 簇事后'
            '方向一致性: %s。' % (
                valid_n, fwm, n_cl, cov, m0, a, cur_from, as_of[:7],
                '重叠' if (m0 <= as_of[:7] and cur_from <= a) else '不重叠',
                res_from, '、'.join(_ov),
                '——重叠窗的样本非独立' if any(
                    x.endswith('重叠') and not x.endswith('不重叠')
                    for x in _ov) else '',
                ag_txt or '无'))
    history_periods.append({
        'anchor_ym': a, 'match_window': h['match_window'],
        'judgment_cutoff_ym': a, 'us_analog': True,
        'aftermath_obs_months': h['aftermath_obs_months'],
        'period_label': (
            '%s(相似检索第 %s 名: 距离 %.4f,距离分位 %.1f;匹配区间 %s 至 %s;'
            '判断只用截至 %s 已发布数据;事后窗至 %s)' % (
                a, t.get('rank'), float(t.get('distance') or 0),
                float(t.get('distance_percentile') or 0),
                h['match_window']['start_ym'], a, a, w12)),
        'similarity': sim, 'difference': difference,
        'other_regions_sync': sync,
        'ex_post': {k: ex_post_txt(i, k) for k in ('3m', '6m', '12m')},
        'sample_note': note})

# ── 三利率分解回贴 / 资产回报回贴 ────────────────────────────────────
w1 = trio.get('window') or {}
c1 = trio.get('chg_bp') or {}
w12 = trio.get('window_12m') or {}
c12 = trio.get('chg_bp_12m') or {}
rates_decomposition = {
    'window_from': w1.get('from'), 'window_to': w1.get('to'),
    'nominal_bp': c1.get('UST_10Y'), 'real_bp': c1.get('TIPS_10Y'),
    'bei_bp': c1.get('BEI_10Y')}
sp12 = rmp.asset_move_rows({'SPX': store['SPX']}, as_of, months=12)
sp12_row = next((r for r in sp12.get('rows') or []
                 if r.get('metric_id') == 'SPX'), None)
if not sp12_row:
    refuse('SPX 12 个月窗不可复算')


def mv(mid):
    return next((r for r in amv.get('rows') or []
                 if r.get('metric_id') == mid), None)


def mv_txt(mid, label=''):
    r = mv(mid)
    if not r:
        return '%s 数据不可得' % mid
    return '%s%s %+.2f%%(%s→%s)' % (label, mid, r['chg_pct'],
                                   r['window']['from'], r['window']['to'])


asset_returns_echo = [{
    'metric_id': r['metric_id'], 'window_months': amv.get('window_months', 1),
    'chg_pct': r['chg_pct'],
    'window': {'from': r['window']['from'], 'to': r['window']['to']}}
    for r in amv.get('rows') or []]
asset_returns_echo.append({
    'metric_id': 'SPX', 'window_months': 12, 'chg_pct': sp12_row['chg_pct'],
    'window': {'from': sp12_row['window']['from'],
               'to': sp12_row['window']['to']}})

# ── 面三: 传导链(冲击环→政策环→利率环→资产环) ───────────────────────
c0 = picked[0]
if c0.get('dimension') != 'inflation':
    refuse('冲击环预设通胀维候选居首——传导链须席位另写')
same_win = [x for x in cands if x is not c0 and x.get('to_ym') == c0['to_ym']]


def _sw(dim):
    return '、'.join('%s %s→%s' % (
        cand_full(x), fmt(x.get('value_before')), fmt(x.get('value_after')))
        for x in same_win if x.get('dimension') == dim)


sw_txt = '、'.join('%s %s→%s' % (
    cand_full(x), fmt(x.get('value_before')), fmt(x.get('value_after')))
    for x in [c0] + [y for y in same_win
                     if y.get('dimension') == c0.get('dimension')])
_od = [d for d in ('growth', 'inflation')
       if d != c0.get('dimension') and _sw(d)]
sw_other = ';%s维同窗: %s' % (DIM_TXT[_od[0]], _sw(_od[0])) if _od else ''
bd0, bv0 = month_last('BRENT_F', c0['from_ym'])
bd1, bv1 = month_last('BRENT_F', c0['to_ym'])
if bv0 is None or bv1 is None:
    refuse('布伦特原油同窗读数缺席')
b_chg = (float(bv1) / float(bv0) - 1.0) * 100.0
bt0, bt1 = '%.2f' % float(bv0), '%.2f' % float(bv1)
if b_chg < 10:
    refuse('同窗布伦特原油涨幅不足一成——对质预期须席位另写')
bl_d, bl_v = last_obs('BRENT_F')
win1 = {'from': c0['from_ym'], 'to': c0['to_ym'], 'basis': 'month_end'}
brent_path = (rmp._window_obs_text(rep, 'BRENT_F', win1, as_of)
              or '同窗观测不可复算')

# ── 政策变动点(引擎同算法)与冻结发布日历政策记录 ─────────────────────
# Audit-R33 任务5修订(独立预审 M2/M3): 政策计数须含月均型序列(日本);
# 决议日与生效日分记——日本以冻结日历实录为准,美/欧为序列变动点
# (=生效日)加惯例回推的决议日,如实标明口径。
cal = os.path.join(tree, 'config', 'release_calendar.json')
try:
    cal_doc = json.load(open(cal, encoding='utf-8'))
except Exception:                                        # pragma: no cover
    cal_doc = {}
cal_entries = [e for e in (cal_doc.get('entries') or cal_doc.get('items')
                           or []) if isinstance(e, dict)]
n_cal = len(cal_entries)


def cal_records(prefix):
    """冻结发布日历内、截止日当时已发布的政策类记录(first_publish_on_or_after
    /decision_date ≤ 截止日;晚于截止日发布的不引用)。"""
    out = []
    for e in cal_entries:
        if not str(e.get('kind') or '').startswith(prefix):
            continue
        pub = str(e.get('first_publish_on_or_after')
                  or e.get('decision_date') or '')
        if pub and pub <= as_of:
            out.append(e)
    return out


def rec_region(e):
    s = ' '.join(str(e.get(k) or '') for k in ('entry_id', 'metric_id', 'id'))
    for key, reg in (('BOJ', 'JP'), ('JP', 'JP'), ('ECB', 'EA'),
                     ('EA_', 'EA'), ('FOMC', 'US'), ('FED', 'US')):
        if key in s:
            return reg
    return None


cal_dec = cal_records('policy_decision')
cal_maint = cal_records('policy_maintenance')
if any(str(e.get('effective_on') or '9999') > as_of for e in cal_dec):
    refuse('存在截止日已公布但尚未生效的日历决议——待生效口径须席位另写')


def cal_dec_txt(reg, eff_month=None):
    """该地区已发布的日历决议记录文本(决议日、生效日、目标值成对);
    eff_month 给定时只取生效日落在该月的记录。"""
    out = []
    for e in cal_dec:
        if rec_region(e) != reg:
            continue
        if eff_month and str(e.get('effective_on') or '')[:7] != eff_month:
            continue
        out.append('冻结日历实录 %s 决议、%s 生效、目标 %s' % (
            e.get('decision_date'), e.get('effective_on'),
            fmt(e.get('target_value'))))
    return out


def cal_maint_txt(reg):
    """该地区已发布的日历「维持」记录文本。"""
    out = []
    for e in cal_maint:
        if rec_region(e) == reg:
            out.append('冻结日历实录 %s 会议确认维持政策目标利率约 %s' % (
                e.get('decision_date'), fmt(e.get('target_value'))))
    return out


def _chg(mid):
    evs = sorted(policy_path(mid).get('events') or [],
                 key=lambda x: str(x.get('date')))
    return ([e for e in evs if float(e.get('delta_bp') or 0) > 0],
            [e for e in evs if float(e.get('delta_bp') or 0) < 0])


if not policy_path('DFEDTARU') or not policy_path('ECB_DFR'):
    refuse('美/欧政策序列近 12 个月窗内无观测')
us_up, us_dn = _chg('DFEDTARU')
ea_up, ea_dn = _chg('ECB_DFR')
jp_seg = [e for e in monthly_events
          if e.get('metric_id') == 'JP_POLICY_RATE']
_eng = sorted((str(e.get('effective_date') or e.get('date')),
               int(e.get('delta_bp') or 0), e.get('metric_id'))
              for e in events)
_mine = sorted((str(e.get('date')), int(e.get('delta_bp') or 0), mid)
               for mid, _p in (('DFEDTARU', None), ('ECB_DFR', None))
               for e in policy_path(mid).get('events') or [])
if _eng != _mine:
    refuse('引擎政策事件簇与序列变动点不一致(须席位另写)')


def chg_txt(mid, reg, e):
    dd = e.get('decision_date')
    return '%s %s %s %s→%s(%+dbp;变动点日=生效日 %s%s)' % (
        e.get('date'), REG_TXT[reg], cell_name(mid), fmt(e.get('from')),
        fmt(e.get('to')), int(e.get('delta_bp') or 0), e.get('date'),
        (';决议日 %s' % dd) if dd else '')


def _dec_day(e):
    return e.get('decision_date') or e.get('date')


def _up_txt(reg, mid, ups, dns):
    ups_s = sorted(ups, key=lambda e: str(e.get('date')))
    dns_s = sorted(dns, key=lambda e: str(e.get('date')))
    out = '%s' % '、'.join('%s 决议,变动点日 %s' % (_dec_day(e), e.get('date'))
                          for e in ups_s) or '无'
    if dns_s:
        pp = policy_path(mid)
        path = [pp.get('window_start_value')] + [
            e.get('to') for e in sorted(pp.get('events') or [],
                                        key=lambda x: str(x.get('date')))]
        out += ';此前 %s 为下调,%s %s' % (
            '、'.join('%s 决议,变动点日 %s' % (_dec_day(e), e.get('date'))
                      for e in dns_s), cell_name(mid),
            '→'.join(fmt(v) for v in path))
    return out


_jp_bp = sorted({int(e['delta_bp']) for e in jp_seg})
_jp_rise = '、'.join('%s 至 %s' % (e['from_ym'], e['to_ym']) for e in jp_seg)
_jp_net = sum(int(e['delta_bp']) for e in jp_seg)
_jp_cal, _jp_nocal = [], 0
for e in jp_seg:
    hit = cal_dec_txt('JP', e['to_ym']) or cal_dec_txt('JP', e['from_ym'])
    if hit:
        _jp_cal += hit
    else:
        _jp_nocal += 1
_jp_cal_s = (';'.join(_jp_cal) or '冻结日历无对应决议记录')
if _jp_nocal and _jp_cal:
    _jp_cal_s += ';其余%s段无冻结日历决议记录' % cn_num(_jp_nocal)
_jp_bp_s = (('各 %dbp' % _jp_bp[0]) if len(_jp_bp) == 1
            else ('分别 %s' % '、'.join('%dbp' % b for b in _jp_bp)))
pol_ev = '、'.join(
    [chg_txt('DFEDTARU', 'US', e) for e in sorted(us_up + us_dn, key=lambda x: str(x.get('date')))]
    + [chg_txt('ECB_DFR', 'EA', e) for e in sorted(ea_up + ea_dn, key=lambda x: str(x.get('date')))]
    + ['%s→%s 日本 %s 月均序列上行段 %s→%s(+%dbp;%s)' % (
        e['from_ym'], e['to_ym'], cell_name('JP_POLICY_RATE'),
        fmt(e.get('from')), fmt(e.get('to')), int(e['delta_bp']),
        '、'.join(cal_dec_txt('JP', e['to_ym'])
                  or cal_dec_txt('JP', e['from_ym'])) or '无冻结日历决议记录')
       for e in jp_seg]) + (
    ';口径: 美国与欧元区为序列变动点(=生效日),决议日按惯例回推'
    '(美联储=生效前一日,欧央行=决议后首个周三,仅周三生效时);日本月均'
    '序列无单一生效日,决议与生效以冻结日历实录为准')
policy_trio = '、'.join(trio_vals(c['metric_id'], True) for c in cells
                       if c.get('dimension') == 'policy')
core_a = yoy_of(cell_by_id('CORE_PCE'), LABELS[1])
core_0 = yoy_of(cell_by_id('CORE_PCE'), LABELS[2])
if core_a is None or core_0 is None:
    refuse('核心PCE同比读数缺席')


def trio_txt(label, w, chg):
    return ('%s(%s→%s)十年期美债名义 %+.1fbp = 实际 %+.1fbp + 盈亏平衡 %+.1fbp'
            % (label, w.get('from'), w.get('to'), chg.get('UST_10Y') or 0.0,
               chg.get('TIPS_10Y') or 0.0, chg.get('BEI_10Y') or 0.0))


tri1 = trio_txt('近1个月', w1, c1)
tri12 = trio_txt('12个月窗', w12, c12)
spx12_txt = 'SPX 12个月窗 %+.2f%%(%s→%s)' % (
    sp12_row['chg_pct'], sp12_row['window']['from'], sp12_row['window']['to'])
real_up_long = float(c12.get('TIPS_10Y') or 0) > 0
real_up_short = float(c1.get('TIPS_10Y') or 0) > 0
spx_dn_long = float(sp12_row['chg_pct']) < 0
spx_dn_short = float((mv('SPX') or {}).get('chg_pct') or 0) < 0
# Audit-R33 任务5修订(独立预审 M3): 收紧计数含日本月均序列上行段;
# 美国先降后升按路径写,不把单次上调写成净收紧。
_n_up = len(us_up) + len(ea_up) + len(jp_seg)
_after = ([e for e in us_up + ea_up if str(e.get('date')) > c0['to_ym'] + '-31']
          + [e for e in jp_seg if e['from_ym'] > c0['to_ym']])
_before = [e for e in jp_seg if e['to_ym'] < c0['from_ym']]
if len(_after) + len(_before) != _n_up:
    refuse('收紧事件相对通胀回升窗的位置存在窗内段(计数措辞须席位另写)')
# 措辞注意: 先后顺序契约(R25)按「日期…早于/晚于…日期」的相邻对判定,窗内/
# 窗外两类事件不写成「终点日期之后,…早于…起点日期」(会被读成终点早于起点)。
hyp2 = (
    '【假设】通胀再加速迫使央行收紧。近 12 个月窗内按序列变动点计的收紧'
    '共 %d 起: 欧元区 %d 起(%s)、美国 %d 起(%s)、日本 %d 段(政策利率月均'
    '序列相邻月上行点 %s,%s,净 +%dbp;%s);其中%s早于通胀回升窗起点,'
    '其余 %d 起在通胀回升窗终点(%s)之后——时序大体相容但不全面,因果未证。'
    % (_n_up, len(ea_up), _up_txt('EA', 'ECB_DFR', ea_up, ea_dn),
       len(us_up), _up_txt('US', 'DFEDTARU', us_up, us_dn), len(jp_seg),
       _jp_rise, _jp_bp_s, _jp_net, _jp_cal_s,
       ('%d 段(%s)' % (len(_before), '、'.join(
           '%s 至 %s' % (e['from_ym'], e['to_ym']) for e in _before)))
       if _before else '无一段', len(_after), c0['to_ym']))
# 窗终月=该序列截至研究截止日的最后一个有观测月(月频序列的最新一期早于
# 截止日所在月): 窗标签不得写到尚无观测的月份(引擎按可复算的窗核验)
_cp = [(ym, v) for ym, _d, v in mon_series('CORE_PCE', yoy=True)
       if c0['to_ym'] <= ym <= as_of[:7] and isinstance(v, (int, float))]
if not _cp:
    refuse('核心PCE同比在通胀回升窗之后无可用观测(观测窗无从声明)')
win2 = {'from': c0['to_ym'], 'to': _cp[-1][0], 'yoy': True}
core_path = (rmp._window_obs_text(rep, 'CORE_PCE', win2, as_of)
             or '同窗观测不可复算')
if len(_cp) < 3 or not (-0.1 < round(_cp[-1][1] - _cp[0][1], 6) < 0.1):
    refuse('窗后核心PCE同比路径与「两解释预期未分立」不符(须席位另写)')
if real_up_long == real_up_short and spx_dn_long == spx_dn_short \
        and real_up_long != spx_dn_long:
    v3 = '支持主解释'
elif real_up_long != real_up_short or spx_dn_long != spx_dn_short:
    v3 = '尚不能区分'
else:
    v3 = '支持竞争解释'
transmission = [{
    'chain_id': 'TR1', 'title': '通胀再加速→政策再收紧→实际利率→风险资产',
    'links': [
        {'step': 1, 'title': '冲击环: 同窗通胀回升',
         'observed_fact': (
             '%s→%s %s维同窗回升: %s(候选面同窗,月频口径)%s;同窗供给侧'
             '读数: 布伦特原油(BRENT_F)月末 %s@%s→%s@%s(首尾 %+.2f%%;%s);'
             '窗后信息(不用于裁决): BRENT_F 截止日前最新 %s@%s。' % (
                 c0['from_ym'], c0['to_ym'],
                 DIM_TXT.get(c0.get('dimension'), ''), sw_txt, sw_other,
                 bt0, bd0, bt1, bd1, b_chg, brent_path, fmt(bl_v), bl_d)),
         'causal_hypothesis': (
             '【假设】供给/能源冲击推升生产价格并传导至消费价格——该归因环'
             '不可由本引擎直接验证。'),
         'competing_explanation': (
             '【假设】需求或基数效应主导(低基数消退、内需回暖),能源价格只是'
             '同向伴随,并非驱动。'),
         'distinguishing_metric': 'BRENT_F',
         'main_predicts': (
             '区分指标 BRENT_F 同窗首尾上行不低于一成(席位自设阈值: 能源'
             '冲击归因需要同窗出现大幅上行)'),
         'competing_predicts': (
             '区分指标 BRENT_F 同窗首尾上行(能源价格只是同向伴随——同样'
             '容纳油价上行,两解释在该指标上预期未分立)'),
         'observation_window': win1,
         'face_off_check': {
             'main': {'op': '>=', 'value': 10.0, 'unit': 'pct'},
             'competing': {'op': '>', 'value': 0.0, 'unit': 'pct'}},
         'face_off_verdict': '尚不能区分',
         'evidence_refs': refs('BRENT_F', 'CPI', 'EA_HICP_YOY', 'CN_PPI_YOY')},
        {'step': 2, 'title': '政策环: 通胀再加速→央行收紧',
         'observed_fact': (
             '政策事件(冻结发布日历与序列变动点): %s;政策利率三时点: %s;'
             '同窗核心PCE同比: %s。' % (pol_ev, policy_trio, core_path)),
         'causal_hypothesis': hyp2,
         'competing_explanation': (
             '【假设】加息由通胀以外的因素驱动(汇率、通胀预期脱锚、期限溢价),'
             '通胀回升只是背景。'),
         'distinguishing_metric': 'CORE_PCE',
         'main_predicts': (
             '区分指标 CORE_PCE 同比在通胀回升窗之后继续走高(较窗终点读数'
             '上行不少于 0.1 个百分点;阈值为席位自设)'),
         'competing_predicts': (
             '区分指标 CORE_PCE 同比在窗之后回落(较窗终点读数回落不少于 '
             '0.1 个百分点)而央行仍加息'),
         'observation_window': win2,
         'face_off_check': {
             'main': {'op': '>=', 'value': 0.1, 'unit': 'pp'},
             'competing': {'op': '<=', 'value': -0.1, 'unit': 'pp'}},
         'face_off_verdict': '尚不能区分',
         'evidence_refs': refs('DFEDTARU', 'ECB_DFR', 'JP_POLICY_RATE',
                               'CORE_PCE')},
        {'step': 3, 'title': '利率环与资产环: 实际利率→风险资产',
         'observed_fact': '%s;%s;%s;%s。' % (
             tri12, tri1, spx12_txt, mv_txt('SPX', '近1个月 ')),
         'causal_hypothesis': '【假设】实际利率上行压制估值,风险资产承压。',
         'competing_explanation': (
             '【假设】风险资产回落由盈利或风险偏好驱动,与实际利率无关。'),
         'distinguishing_metric': 'TIPS_10Y',
         'main_predicts': '区分指标 TIPS_10Y 上行期 SPX 同步走低',
         'competing_predicts': '区分指标 TIPS_10Y 与 SPX 同向变动',
         'face_off_verdict': v3,
         'evidence_refs': refs('UST_10Y', 'TIPS_10Y', 'BEI_10Y', 'SPX')}]}]

# ── 首页结论 ──────────────────────────────────────────────────────────


def trend(label, mid):
    c = cell_by_id(mid)
    a, b = (yoy_of(c, LABELS[0]), yoy_of(c, LABELS[2])) if c else (None, None)
    if a is None or b is None:
        return '%s三时点不可比' % label
    if b > a:
        return '%s较去年同月走高' % label
    if b < a:
        return '%s较去年同月走低' % label
    return '%s较去年同月持平' % label


def pol_phrase(label, mid):
    c = cell_by_id(mid)
    v = [yoy_of(c, lbl) for lbl in LABELS] if c else [None, None, None]
    if None in v:
        return '%s三时点不可比' % label
    if v[2] > v[0]:
        return '%s较去年同月上调' % label
    if v[2] < v[0]:
        return '%s较去年同月下调' % label
    if v[1] < v[0]:
        return '%s期内先降后升、首尾持平' % label
    if v[1] > v[0]:
        return '%s期内先升后降、首尾持平' % label
    return '%s三时点持平' % label


n_in = len(wt.get('rows_in_window') or [])
n_test = sum(1 for x in wt.get('rows_in_window') or [] if x.get('testable'))
pimco = rows['VIEW-20261110-003#f2']
oecd = rows['VIEW-20261111-002#f3']
# Audit-R33 任务5修订(独立预审 m/n): 政策记录计数与日历版本取自冻结日历
# 顶层字段;截止日当日读数与资产月窗端点敏感性如实披露;PARTIAL 点明已到期
# 未核验行(质量门注记不入数值绑定,可写行号)。
_n_dec = {reg: len([e for e in cal_dec if rec_region(e) == reg])
          for reg in ('JP', 'EA', 'US')}
_n_maint = {reg: len([e for e in cal_maint if rec_region(e) == reg])
            for reg in ('JP', 'EA', 'US')}
_asof_d = datetime.date.fromisoformat(as_of[:10])
_cut_rows = [r for r in amv.get('rows') or []
             if str((r.get('window') or {}).get('to')) == as_of]
_flip = []
for _r in _cut_rows:
    _ad, _av = obs_at(_r['metric_id'], str(_asof_d - datetime.timedelta(days=1)))
    try:
        _alt = (float(_av) / float(_r['from_value']) - 1.0) * 100.0
    except (TypeError, ValueError, ZeroDivisionError):
        continue
    if float(_r['chg_pct']) != 0 and (_alt > 0) != (float(_r['chg_pct']) > 0):
        _flip.append('%s 一个月变动止于 %s 为 %+.2f%%、改取 %s 则为 %+.2f%%' % (
            _r['metric_id'], as_of, float(_r['chg_pct']), _ad, _alt))
_mat_unv = [r for r in rows_all if r.get('maturity') == 'MATURED'
            and not str(r.get('status') or '').startswith('ex_post')]
_MAT_WHY = {'unmapped': '目标未映射到在册指标', 'series_absent': '在册序列缺席',
            'context_only': '仅背景信息', 'reading_required': '须席位推导'}
_mat_reason = '、'.join(sorted({_MAT_WHY.get(str(r.get('status')), str(r.get('status')))
                                for r in _mat_unv})) or '—'
# Audit-R33 任务5修订(独立预审 M4): 该表述与定价同向(均为上调)、只是
# 幅度更低——原文须含「加息」与「低于/不必」类幅度措辞,且定价曲线为累计
# 上行(上方守卫已核);措辞或定价方向改变即拒绝装配。
if not ('加息' in str(pimco.get('value_raw') or '') and any(
        k in str(pimco.get('value_raw') or '')
        for k in ('无需完全兑现', '不必', '低于', '少于'))):
    refuse('PIMCO 文字型表述的方向/幅度措辞与预设不符(须席位另写解读)')
n_sup = sum(1 for v in AUTHORED.values() if v[2] == 'supported')
n_ng = sum(1 for v in AUTHORED.values() if v[2] == 'not_a_gap')
gaps = blk.get('gaps') or []
# Audit-R33 任务5修订(独立预审 M2): 读数陈旧=序列形态;日本有冻结日历
# 「维持」记录,欧元区其后有无决议本轮冻结证据未知——如实分述。
_jp_maint = cal_maint_txt('JP')
_ea_rec = [e for e in cal_dec + cal_maint if rec_region(e) == 'EA']
pol_stale = (
    '欧日政策利率表述与截止日可得读数一致,但对账读数陈旧源于序列形态('
    + ('日本央行有冻结日历维持记录' if _jp_maint
       else '日本无冻结日历维持记录') + ';'
    + ('欧元区有冻结日历政策记录' if _ea_rec
       else '欧元区其后有无新决议本轮冻结证据未知') + ')')


def biggest_component():
    comps = (('名义', c1.get('UST_10Y') or 0.0), ('实际', c1.get('TIPS_10Y') or 0.0),
             ('盈亏平衡', c1.get('BEI_10Y') or 0.0))
    return max(comps, key=lambda kv: abs(float(kv[1])))[0]


hl_env = '、'.join([trend('核心PCE同比', 'CORE_PCE'), trend('欧元区HICP同比', 'EA_HICP_YOY'),
                    trend('中国PPI同比', 'CN_PPI_YOY'), trend('日本CPI同比', 'JP_CPI_YOY')])
hl_pol = ';'.join([
    pol_phrase('联邦基金目标区间上限', 'DFEDTARU'),
    pol_phrase('存款便利利率', 'ECB_DFR'), pol_phrase('日本政策利率(月均)', 'JP_POLICY_RATE')])
headline = (
    '问句问的是『市场定价和机构观点之间有哪些预期差、未来什么会证伪』。'
    '席位研判: 有证据支持的预期差 %d 项,均为文字型表述的席位推导(PIMCO『%s』'
    '——政策方向与市场相同、幅度更低且不可量化,弱证据);有编号的机构加息'
    '路径与同期限期货定价一致(同期限定价差不足半个定价步长);%s;定价面'
    '只入库美国联邦基金利率期货,『未'
    '建立对照』不等于『无预期差』。环境面(同一冻结证据): %s;政策面: %s;'
    '利率: %s,近月变动以%s分量为最大;近1个月资产: %s。证伪窗口: %s→%s'
    '(问句『%s』),窗内到期 %d 行、'
    '可检验 %d 行。' % (
        n_sup, pimco.get('value_raw'), pol_stale, hl_env, hl_pol, tri1,
        biggest_component(),
        '、'.join(mv_txt(m) for m in ('SPX', 'NIKKEI225', 'GOLD_F', 'DXY', 'VIX')
                  if mv(m)),
        fw.get('start'), fw.get('end'), fw.get('source'), n_in, n_test))

# ── L3: 矛盾陈述与机制链 ──────────────────────────────────────────────
r_u1, r_u2, r_m1 = (rows[x] for x in NUM_PATHS)
g1 = float(hg(r_u1).get('gap_bp'))
g2 = float(hg(r_u2).get('gap_bp'))
g_m1 = float(hg(r_m1).get('gap_bp'))
if not all(x < float(pr.get('material_gap_bp')) for x in (g1, g2, g_m1)):
    refuse('编号路径期限差不满足「不足半步」')
g_max = max(g1, g2, g_m1)
n_inst = len((dis.get('FED_FUNDS') or {}).get('institutions') or [])
step_m = ((r_u1.get('comparison') or {}).get('step') or {}).get('month')
hor_m = hg(r_u1).get('month')
# Audit-R33 任务5修订(独立预审 M4/m): PIMCO 表述的同期限定价参照=到期日
# (期限上界)当月或之前最后一个合约月;其定价引用能解析才绑定到证据(旧引擎
# 的证据索引不含该月则如实不绑定)。阈值离散化: 目标区间上限按定价步长变动。
idx_ref = {e.get('ref') for e in rep.get('evidence_index') or []}
_hz_end0 = str(pimco.get('horizon_end') or '')
hz_low = str(pimco.get('view_horizon_end') or '')
_pzref = pimco.get('pricing_reference') or {}
step_bp = float(pr.get('step_bp'))
hz_row = horizon_row(_hz_end0, prow, _pzref)
if not (hz_row and _hz_end0 and hz_low
        and fw.get('start') <= hz_low <= fw.get('end')
        and _hz_end0 > fw.get('end')):
    refuse('PIMCO 表述到期日与定价曲线/证伪窗口关系改变(须席位另写判据)')
hz_m = str(hz_row.get('month'))
hz_bp = float(hz_row.get('change_bp'))
_hz_n = steps_of(hz_bp, step_bp)
hz_ref = (hz_row.get('evidence_ref')
          if hz_row.get('evidence_ref') in idx_ref else None)
gc1 = (
    '美国政策路径: 有编号的机构加息路径与同期限期货定价一致——UBS 的『%s』'
    '『%s』与 MSIM 的『%s』,对到期终点月的期货定价差最大仅%s个基点,均不足'
    '半个定价步长(%s个基点;期货为月均口径,基线=截止日有效利率)。'
    '联邦基金利率上共%s家机构的表述与市场对照,其中唯一的幅度性分歧来自 '
    'PIMCO 的『%s』——文字型表述、未给幅度,引擎不解读(席位推导见预期差面): '
    '席位读作『不必加到期货曲线隐含的那么多』,政策方向与市场相同(均为上调)、'
    '幅度更低且不可量化(同期限期货定价隐含累计上调%s个基点,见预期差面)。'
    '『编号路径一致』成立,但对『定价即共识』至少有三种数据同样容纳的'
    '解释(见竞争解释),当前证据不足以在它们之间裁决——区分依赖 %s 与 %s '
    '合约在后续会议后的重定价。证据面最新水平(引擎回贴): DFF 水平为 %s。'
    % (r_u1.get('value_raw'), r_u2.get('value_raw'), r_m1.get('value_raw'),
       cn_amt(g_max), cn_num(pr.get('material_gap_bp')), cn_num(n_inst),
       pimco.get('value_raw'), cn_num(hz_bp), step_m, hor_m,
       fmt(l1['DFF'].get('value'))))
stale_dates = sorted({str(((rows[x].get('facts') or {}).get('at_cutoff') or {})
                          .get('observation_date')) for x in STALE_ROWS})
# Audit-R33 任务5修订(独立预审 M2): 读数陈旧=序列形态(政策利率序列只在
# 变动日产生新观测),非采集缺口;日本有冻结日历维持记录、其后至截止日一段
# 与欧元区其后决议同为冻结证据未知——日期、滞后天数与观测日取自冻结面,
# 陈述内计数与数值用中文数字(水平值只在句末按「指标 水平为 X」回贴)。
_ecb_obs = [str(e.get('date')) for e in sorted(
    policy_path('ECB_DFR').get('events') or [], key=lambda x: str(x.get('date')))]
_jp_l1 = l1['JP_POLICY_RATE']
_jp_maint_rec = [e for e in cal_maint if rec_region(e) == 'JP']
_ea_row = rows['VIEW-20261110-005#f1']
_ea_pub = str(_ea_row.get('publish_date') or '')
_ea_eff = str(l1['ECB_DFR'].get('observation_date') or '')
if not (_ecb_obs and _jp_maint_rec and _ea_pub <= as_of
        and _jp_l1.get('observation_date') and _ea_eff):
    refuse('欧日政策利率行的日历/序列/发布日配置改变(须席位另写)')
_jp_maint_date = str(_jp_maint_rec[-1].get('decision_date') or '')
if days_before(_jp_maint_date) is None or days_before(_ea_pub) is None:
    refuse('欧日政策利率行的日期不可解析(须席位另写)')
gc2 = (
    '欧日政策利率现值: 欧央行与日本央行的政策利率表述(%s条: 存款便利利率、'
    '主要再融资利率与日本政策利率)与截止日可得读数对上(日本为 %s 月均值对'
    '目标约%s;欧元区为 %s 生效值),但读数陈旧来自序列形态——政策利率序列'
    '只在变动日产生新观测(欧元区存款便利利率近十二个月窗内观测日: %s),'
    '不是采集缺口。冻结发布日历实录: 日本央行 %s 会议确认维持政策目标利率'
    '(距截止日%s天),与月均值相符,其后至截止日一段无冻结日历记录(如实记为'
    '未知);欧元区无冻结日历决议记录,只有 %s 的央行维持表述(距截止日%s天)'
    '与 %s 生效值,其后至截止日有无新决议本轮冻结证据无从确认(如实记为'
    '未知)。且欧元区与日本无同期限市场定价工具入库——『机构表述与现值一致』'
    '不等于『机构与市场之间无预期差』,后者本轮无从对账(明确缺口)。对『表述'
    '与现值一致』至少有两种数据同样容纳的解释(见竞争解释;日本一侧的『采集'
    '缺口』解释已被维持实录否定),当前证据不足以在它们之间裁决。证据面最新'
    '水平(引擎回贴): ECB_DFR 水平为 %s、JP_POLICY_RATE 水平为 %s。'
    % (cn_num(len(STALE_ROWS)), str(_jp_l1.get('observation_date'))[:7],
       cn_num(_jp_maint_rec[-1].get('target_value')), _ea_eff, '、'.join(_ecb_obs),
       _jp_maint_date, cn_num(days_before(_jp_maint_date)), _ea_pub,
       cn_num(days_before(_ea_pub)), _ea_eff,
       fmt(l1['ECB_DFR'].get('value')), fmt(l1['JP_POLICY_RATE'].get('value'))))
d_eps, d_cn = dis['SPX_EPS'], dis['CN_REAL_GDP_YOY']


def _year_vals(mid):
    """行点位按年份取值 {年: [(数值, 是否约数)]}: 多值行按原文「YYYY年X%」
    配对;增速等非水平点位行与百分比水平行按到期年;指数点位行原文括注的
    增速记在到期年(标约数)。只用于同一口径(年度增速)的并列。"""
    out = {}
    for r in rows_all:
        if r.get('metric_id') != mid:
            continue
        pt = r.get('point') or {}
        raw = str(pt.get('raw') or r.get('value_raw') or '')
        yr = str(r.get('horizon_end') or '')[:4]
        pairs = re.findall(r'(\d{4})\s*年\s*[^\d%,，]{0,6}?[+]?\s*(\d+(?:\.\d+)?)\s*%',
                           raw)
        if len(pairs) > 1:
            for y, x in pairs:
                out.setdefault(y, []).append((float(x), False))
            continue
        if not yr:
            continue
        if isinstance(pt.get('value'), (int, float)) and (
                pt.get('kind') != 'level'
                or str(pt.get('unit') or r.get('metric_unit') or '')
                .startswith('percent')):
            out.setdefault(yr, []).append((float(pt['value']), False))
            continue
        m = re.search(r'约\s*([+-]?\d+(?:\.\d+)?)\s*%', raw)
        if m:
            out.setdefault(yr, []).append((float(m.group(1)), True))
    return out


def _same_basis_txt(mid, year, pct_style):
    """同一口径(该年度增速)的并列数字(中文数字);不足两行时返回空串。"""
    vs = _year_vals(mid).get(year) or []
    if len(vs) < 2:
        return ''
    vals = [v for v, _a in vs]
    lo, hi = cn_num(min(vals)), cn_num(max(vals))
    if pct_style:
        body = '%s%s对%s' % ('约百分之' if any(a for _v, a in vs) else '百分之',
                             lo, '百分之' + hi)
    else:
        body = '%s对%s' % (lo, hi)
    return '(同为 %s 年口径: %s,相差约%s个百分点)' % (
        year, body, cn_num(round(max(vals) - min(vals), 1)))


_eps_years = sorted(y for y, v in _year_vals('SPX_EPS').items() if len(v) >= 2)
_eps_sb = _same_basis_txt('SPX_EPS', _eps_years[0], True) if _eps_years else ''
_cn_sb = _same_basis_txt('CN_REAL_GDP_YOY', as_of[:4], False)
gc3 = (
    '机构间分歧的不可对账面: 盈利预测上%s表述形式相异(点位对增速)、期限'
    '不一%s;中国增长预测上%s不一%s,中国实际 GDP 同比序列本轮缺席——这些是'
    '『机构之间』的分歧,不是『机构与市场之间』可量化的预期差(未建立对照='
    '明确缺口)%s。对『分歧为真实』至少有两种数据同样容纳的解释(见竞争'
    '解释),当前证据不足以在它们之间裁决。证据面最新水平(末观测已陈旧): %s。'
    % ('与'.join(short_inst(x) for x in d_eps.get('institutions') or []),
       _eps_sb,
       '与'.join(short_inst(x) for x in d_cn.get('institutions') or []),
       _cn_sb,
       ';同一口径下仍有差距(见括注),口径差不足以完全解释'
       if (_eps_sb and _cn_sb) else '',
       level_txt('SPX_EPS')
       or 'SPX_EPS 水平为 %s' % fmt(l1['SPX_EPS'].get('value'))))


def sgn(v):
    return '上行' if v > 0 else ('走低' if v < 0 else '持平')


DOWN = [m for m in ('SPX', 'NIKKEI225', 'GOLD_F') if mv(m) and mv(m)['chg_pct'] < 0]
UP = [m for m in ('DXY', 'VIX') if mv(m) and mv(m)['chg_pct'] > 0]
# Audit-R33 任务5修订(独立预审 m): 中国政策利率逐指标如实写三时点可比性
# 与新鲜度(引擎面已标过期者带末观测日与滞后天数;换锚后仅最新一期可得者
# 写不可比),不再并成一句「三时点持平」。名称不带阿拉伯数字(陈述内数值
# 须绑定);水平回贴带观测日与距截止日天数(中文数字)。
CN_POLICY_MIDS = ('CN_LPR_1Y', 'CN_OMO_7D', 'CN_POLICY_OVERNIGHT')
CN_POLICY_NAME = {'CN_LPR_1Y': '一年期贷款市场报价利率',
                  'CN_OMO_7D': '七天逆回购利率',
                  'CN_POLICY_OVERNIGHT': '央行隔夜逆回购利率(政策利率锚)'}


def _cn_cell_txt(mid):
    c = cell_by_id(mid)
    if not c:
        return '%s三时点缺席' % CN_POLICY_NAME[mid]
    vals = [yoy_of(c, lbl) for lbl in LABELS]
    oks = [i for i, v in enumerate(vals) if v is not None]
    if len(oks) < 3:
        return '%s三时点不可比(%s)' % (
            CN_POLICY_NAME[mid],
            '仅最新一期可得' if oks == [2] else '部分锚前无已发布观测')
    if len(set(vals)) != 1:
        return '%s三时点有变动' % CN_POLICY_NAME[mid]
    a = anchor(c, LABELS[2])
    out = '%s三时点持平' % CN_POLICY_NAME[mid]
    if a.get('freshness') == 'stale' and a.get('observation_date'):
        lag = a.get('freshness_lag_days')
        out += '(末观测 %s,滞后%s天,引擎面标过期)' % (
            a.get('observation_date'),
            cn_num(lag) if isinstance(lag, (int, float)) else '未知')
    return out


cn_pol_txt = '、'.join(_cn_cell_txt(m) for m in CN_POLICY_MIDS)
if not (region_flat('CN') and all(cell_by_id(m) for m in CN_POLICY_MIDS)
        and '有变动' not in cn_pol_txt
        and any(float(e.get('delta_bp') or 0) > 0 for e in events)):
    refuse('中国政策利率三时点并非可比者全持平,或窗内无其他地区收紧'
           '(须席位另写)')
ec1 = (
    '环境面共动: 四地三时点走位(12个月前→3个月前→最新一期)显示——通胀: '
    '%s、%s、%s、%s;政策: %s;%s;%s;中国%s,可比者未跟进收紧;利率: 长期窗'
    '(%s→%s)UST_10Y %s、TIPS_10Y %s而 BEI_10Y %s;资产: 近1个月%s走低而%s'
    '走高。证据面水平(引擎回贴): %s。对『这一共动由'
    '通胀再加速→政策再收紧主导』至少有两种数据同样容纳的解释(见竞争解释),'
    '当前证据不足以在它们之间裁决。'
    % (trend('核心PCE同比', 'CORE_PCE').replace('去年同月', '一年前'),
       trend('欧元区HICP同比', 'EA_HICP_YOY').replace('去年同月', '一年前'),
       trend('中国PPI同比', 'CN_PPI_YOY').replace('去年同月', '一年前'),
       trend('日本CPI同比', 'JP_CPI_YOY').replace('去年同月', '一年前'),
       pol_phrase('联邦基金目标区间上限', 'DFEDTARU').replace('去年同月', '一年前'),
       pol_phrase('存款便利利率', 'ECB_DFR').replace('去年同月', '一年前'),
       pol_phrase('日本政策利率(月均)', 'JP_POLICY_RATE').replace('去年同月', '一年前'),
       cn_pol_txt,
       w12.get('from'), w12.get('to'), sgn(float(c12.get('UST_10Y') or 0)),
       sgn(float(c12.get('TIPS_10Y') or 0)), sgn(float(c12.get('BEI_10Y') or 0)),
       '、'.join(DOWN) or '无', '、'.join(UP) or '无',
       '、'.join(x for x in (level_txt('UST_10Y'), level_txt('TIPS_10Y'),
                             level_txt('BEI_10Y'), level_txt('SPX'),
                             level_txt('HY_OAS'), level_txt('CN_LPR_1Y'))
                 if x) or '水平事实缺席'))
if not DOWN or not UP:
    refuse('近1个月资产方向与预设叙述不符(须席位另写)')
contras = [
    {'id': 'G-C1', 'statement': gc1,
     'competing_explanations': [
         '解释A(定价即共识): 期货曲线本身就是市场对未来会议结果的最优'
         '预测,机构编号路径与之一致说明双方共享同一信息集——若成立,后续'
         '会议决议应逐次落在曲线隐含幅度附近【尚未验证】',
         '解释B(同源性): 机构预测与市场定价同源于对央行沟通的解读,一致'
         '并不代表独立信息相互印证——若成立,机构预测在会议前的修正应'
         '滞后于曲线变动【尚未验证】',
         '解释C(期限溢价/分布均值): 期货月均隐含幅度含分布均值与技术性'
         '因素,机构点位指最可能路径,两者一致只是口径巧合【假设】'],
     'evidence_refs': [x for x in (
         'VIEW-20261111-004#f1', 'VIEW-20261111-004#f2', 'VIEW-20261111-006#f1',
         'VIEW-20261110-003#f2', ref_for('DFF'), ref_for('DFEDTARU'),
         ref_for('FED_FUNDS')) if x]},
    {'id': 'G-C2', 'statement': gc2,
     'competing_explanations': [
         '解释A(序列形态): 读数陈旧来自政策利率序列只在变动日产生新'
         '观测,不是采集缺口——若成立,下一变动日前读数保持不变(日本一侧'
         '与冻结日历维持实录相符)【尚未验证】',
         '解释B(真实一致): 日本央行维持会议之后至截止日、欧元区末次变动'
         '之后至截止日确无新决议,表述与现值一致是真实的一致【假设】',
         '解释C(未入库决议): 欧元区在其央行维持表述之后另有决议而冻结'
         '日历与序列均未入库——若成立,更新后读数将与表述出现差异(日本'
         '一侧该解释已被维持实录否定)【尚未验证】'],
     'evidence_refs': [x for x in (
         'VIEW-20261110-005#f1', 'VIEW-20261110-005#f2', 'VIEW-20261110-006#f1',
         ref_for('ECB_DFR'), ref_for('ECB_MRO'), ref_for('JP_POLICY_RATE'))
         if x]},
    {'id': 'G-C3', 'statement': gc3,
     'competing_explanations': [
         '解释A(口径差): 分歧部分来自表述形式与预测期限不同(点位对增速),'
         '但同一口径下仍有差距(见陈述括注),口径差不足以完全解释——是否'
         '为对经济前景的真实分歧须看后续数据【假设】',
         '解释B(真实分歧): 机构对增长与盈利前景确有不同判断,口径差不足'
         '以解释差距——若成立,分歧应随数据发布收敛或持续扩大【尚未验证】'],
     'evidence_refs': [x for x in (
         'VIEW-20261111-002#f3', ref_for('SPX_EPS'), ref_for('US_REAL_GDP'))
         if x]},
    {'id': 'E-C1', 'statement': ec1,
     'competing_explanations': [
         '解释A(通胀再加速→政策再收紧): 通胀回升迫使央行收紧,名义利率'
         '上行由实际利率主导,高实际利率压制风险资产——若成立,TIPS_10Y '
         '续升而 BEI_10Y 大体稳定【假设】',
         '解释B(增长担忧): 风险资产走低主要由增长预期下修驱动,利率变化'
         '是结果而非原因——若成立,BEI_10Y 主导性走低而 TIPS_10Y 转平'
         '【假设】'],
     'evidence_refs': refs('CORE_PCE', 'EA_HICP_YOY', 'CN_PPI_YOY', 'JP_CPI_YOY',
                           'DFEDTARU', 'ECB_DFR', 'JP_POLICY_RATE', 'UST_10Y',
                           'TIPS_10Y', 'BEI_10Y', 'SPX', 'HY_OAS')}]
cpi_c = next((c for c in picked if c['metric_id'] == 'CPI'), None)
chain_links = [
    {'step': 1, 'text': (
        '冲击环【事实/E1】: %s→%s 通胀维同窗回升: %s(增长维同窗: %s);同窗'
        '布伦特原油(BRENT_F)月末 %s→%s(首尾 %+.2f%%)——能源/供给冲击为待检验'
        '归因;引用为各指标快照最新观测事实,同窗月末读数由契约按冻结序列'
        '复算。' % (c0['from_ym'], c0['to_ym'], sw_txt,
                   _sw('growth') or '无', bt0, bt1, b_chg)),
     'evidence_level': 'E1',
     'evidence_refs': refs('CPI', 'EA_HICP_YOY', 'CN_PPI_YOY', 'BRENT_F')},
    {'step': 2, 'text': (
        '政策环【时序为事实,动机为假设/E3】: %s;窗后核心PCE同比路径: %s。'
        '政策收紧的动机归因不可由引擎直接验证;证伪指标=CORE_PCE。'
        % (pol_ev, core_path)),
     'evidence_level': 'E3', 'falsification_metric': 'CORE_PCE',
     'evidence_refs': refs('DFEDTARU', 'ECB_DFR', 'JP_POLICY_RATE', 'CORE_PCE')},
    {'step': 3, 'text': '利率环【事实/E1】: %s;%s。' % (tri12, tri1),
     'evidence_level': 'E1', 'evidence_refs': refs('UST_10Y', 'TIPS_10Y', 'BEI_10Y')},
    {'step': 4, 'text': (
        '资产环【E2,缺环为假设】: %s;%s。' % (
            spx12_txt, mv_txt('SPX', '近1个月 '))),
     'evidence_level': 'E2',
     'missing_link_note': (
         '缺失环=利率变化→估值变化的因果传导(引擎只有共动事实,无因果'
         '识别);该环为【假设】,证伪指标=HY_OAS'),
     'evidence_refs': refs('SPX', 'NIKKEI225', 'GOLD_F', 'DXY', 'VIX',
                           'TIPS_10Y', 'HY_OAS')}]
for c in contras:
    if not any(ev in {e.get('ref') for e in rep.get('evidence_index') or []}
               and (next(e for e in rep['evidence_index']
                         if e.get('ref') == ev).get('kind')) == 'snapshot_fact'
               for ev in c['evidence_refs']):
        refuse('矛盾陈述 %s 缺快照事实引用' % c['id'])

# ── L4: 情景(假设非预测) ──────────────────────────────────────────────
pool = {p.get('id'): p for p in blk.get('falsification_pool') or []}
rule_pol = pool.get('VIEW-20261111-004#f1/policy') or {}
if not rule_pol.get('pass_min_pct') or not rule_pol.get('date'):
    refuse('规则池缺编号路径的政策通过线')
pass_min = rule_pol['pass_min_pct']
dead_g1 = str(rule_pol['date'])
p_by_month = {x.get('month'): x for x in prow}
last_m = str(pr.get('last_month') or prow[-1].get('month'))
last_p = p_by_month.get(last_m) or prow[-1]
# 窗口内最后一个完整合约月: 窗口末日不是月末时,该月合约未走完
_end_d = datetime.date(int(fw['end'][:4]), int(fw['end'][5:7]),
                       int(fw['end'][8:10]))
_nxt = _end_d + datetime.timedelta(days=1)
win_m = fw['end'][:7] if _nxt.month != _end_d.month else \
    ym_shift(fw['end'][:7], -1)
win_p = p_by_month.get(win_m)
if not (win_p and win_p.get('change_bp') is not None):
    refuse('窗口内最后一个完整合约月缺定价读数(须席位另写判据)')
# 窗内阈值同期限参照的离散化: 月均隐含有效利率读数对定价步长折合加息次数
_wp_n = steps_of(win_p.get('change_bp'), step_bp)
hz_end = str(pimco.get('horizon_end') or '')
if not (hz_end and win_p and str(last_m) < hz_end[:7]):
    refuse('PIMCO 表述到期日与定价曲线关系改变(须席位另写判据)')
base_u = float(((pr.get('midpoint') or {}).get('upper') or {}).get('value'))
scen = [
    {'id': 'SCN-G1', 'role': '定价情景', 'rows': {
        'scenario': (
            '假设期货定价路径兑现: 首个编号路径到期月(%s)会议加息落地,'
            '目标区间上限升至规则池通过线以上。' % step_m),
        'asset_direction': {
            'direction': '在此假设下,实际利率维持高位,久期与高估值资产承压、'
                         'DXY 偏强;纯逻辑推演,未作幅度主张。',
            'confidence_tier': '纯逻辑推理',
            'evidence_refs': [x for x in (ref_for('TIPS_10Y'), ref_for('DFEDTARU'),
                                          'DFF@%s' % pr['baseline']['observation_date'])
                              if x]},
        'sensitive_variables': ['DFEDTARU', 'FED_FUNDS'],
        'falsification': {
            'metric_id': 'DFEDTARU',
            'threshold': 'DFEDTARU 在 %s 的读数低于 %s(首个编号路径的加息'
                         '未兑现=期货定价的近期加息落空,本情景前提失效)'
                         % (dead_g1, fmt(pass_min)),
            'secondary_metric_ids': ['FED_FUNDS']},
        'trigger': {
            'condition': '%s FOMC 决议后的 DFEDTARU 最新读数' % step_m,
            'deadline': dead_g1}}},
    {'id': 'SCN-G2', 'role': '机构基线情景', 'rows': {
        'scenario': (
            '假设机构基线兑现: PIMCO『%s』成立——截至其表述到期日(%s),联邦'
            '基金目标区间上限累计上调幅度低于期货曲线同期限隐含的累计幅度'
            '(政策方向与市场相同、幅度更低)。'
            % (pimco.get('value_raw'), hz_end)),
        'asset_direction': {
            'direction': '在此假设下,政策路径低于期货定价,久期资产承压小于'
                         '定价所示、风险资产估值压力缓和;纯逻辑推演,未作幅度'
                         '主张。',
            'confidence_tier': '纯逻辑推理',
            'evidence_refs': [x for x in (
                'VIEW-20261110-003#f2', ref_for('DFEDTARU'), ref_for('DFF'),
                hz_ref) if x]},
        'sensitive_variables': ['DFEDTARU', 'FED_FUNDS'],
        'falsification': {
            'metric_id': 'DFEDTARU',
            'threshold': 'DFEDTARU 在 %s 之前较 %s 的 %s 累计上调不少于 %sbp'
                         '(达到期货曲线对 %s 合约月均隐含的累计幅度;目标区间'
                         '上限按 %sbp 步长变动,折合等于或超过%s次加息;阈值为'
                         '期货月均隐含有效利率口径)=本情景证伪' % (
                             hz_end, as_of, fmt(base_u), fmt(hz_bp), hz_m,
                             fmt(step_bp), cn_num(_hz_n)),
            'secondary_metric_ids': ['FED_FUNDS']},
        'trigger': {
            'condition': '每次美联储决议后的 DFEDTARU 最新读数',
            'deadline': hz_end}}},
]
t2 = top[1] if len(top) > 1 else {}
af2 = (t2.get('aftermath') or {})
try:
    spx3 = float(((af2.get('SPX') or {}).get('3m')))
    gold3 = float(((af2.get('GOLD_F') or {}).get('3m')))
    dxy3 = float(((af2.get('DXY') or {}).get('3m')))
except (TypeError, ValueError):
    spx3 = gold3 = dxy3 = None
aligned = (spx3 is not None and spx3 < 0 and gold3 < 0 and dxy3 > 0)
cpi_thr = fmt(cpi_c.get('value_before')) if cpi_c else '3'
e1_dir = ('在此假设下,股指与 GOLD_F 承压、DXY 偏强' + (
    ';该方向与相似检索第 %s 名 %s 段事后 3 个月(SPX %+.2f%%、GOLD_F '
    '%+.2f%%、DXY %+.2f%%)方向一致,但历史相似≠因果【假设】' % (
        t2.get('rank'), t2.get('candidate_month'), spx3, gold3, dxy3)
    if aligned else ';相似检索各段事后方向并不一致,无历史同构支持,'
    '纯逻辑推演') + '。')
# Audit-R33 任务5修订(独立预审 m): 情景前提旁写当前读数与转折窗终点/其后
# 低点的关系(月频同比路径,与转折探测同算法;关系改变即拒绝装配)。
_cp_ym = [(ym, d, v) for ym, d, v in mon_series('CPI', yoy=True)
          if isinstance(v, (int, float)) and ym >= c0['to_ym']]
_cpi_first = _cp_ym[0] if _cp_ym else None
_cpi_last = _cp_ym[-1] if _cp_ym else None
_cpi_low = min(_cp_ym[1:], key=lambda x: x[2]) if len(_cp_ym) > 1 else None
if not (_cpi_first and _cpi_last and _cpi_low
        and _cpi_first[0] == c0['to_ym']
        and _cpi_last[2] < _cpi_first[2] and _cpi_last[2] > _cpi_low[2]):
    refuse('当前美国CPI同比与转折窗终点/其后低点的关系改变(情景前提须席位另写)')
scen.append({
    'id': 'SCN-E1', 'role': '风险情景', 'rows': {
        'scenario': (
            '假设通胀再加速延续(同窗转折后读数续升;当前美国 CPI 同比 %s@%s,'
            '低于转折窗终点读数 %s@%s、高于其后低点 %s@%s),则政策再收紧与'
            '风险资产承压的情景成立。' % (
                fmt(_cpi_last[2]), _cpi_last[1], fmt(_cpi_first[2]),
                _cpi_first[1], fmt(_cpi_low[2]), _cpi_low[1])),
        'asset_direction': {
            'direction': e1_dir,
            'confidence_tier': '有历史相似证据' if aligned else '纯逻辑推理',
            'evidence_refs': refs('SPX', 'GOLD_F', 'DXY', 'CPI', 'TIPS_10Y')},
        'sensitive_variables': ['CPI', 'CORE_PCE'],
        'falsification': {
            'metric_id': 'CPI',
            'threshold': '美国CPI同比回落至%s以下并持续两个月(跌破转折起点='
                         '再加速被证伪,本情景失效)' % cpi_thr,
            'secondary_metric_ids': ['CORE_PCE']},
        'trigger': {
            'condition': '美国月度 CPI 同比读数(引擎月末口径)',
            'deadline': '2027-02-28'}}})
if cpi_c is None:
    refuse('转折三项缺美国CPI——情景阈值须席位另写')

# ── 预期差对照块: 席位回声与逐行判定 ────────────────────────────────
pool_inst = [p for p in blk.get('falsification_pool') or []
             if p.get('source') == 'view_library'
             and p.get('view_id') == pimco.get('view_id')
             and p.get('attribution') == 'institution_stated']
if not pool_inst:
    refuse('PIMCO 观点库证伪条件缺席')
c1p = pool_inst[0]
oecd_vals = [float(v) for v in ((oecd.get('point') or {}).get('values') or [])
             if isinstance(v, (int, float))]
if not oecd_vals:
    refuse('OECD 行点位非数值——须席位另写判据')
oecd_hi = max(oecd_vals)
oecd_lo = min(oecd_vals)
u2_cum = float(r_u2.get('cum_inst_bp') or 0)
pimco_refs = [x for x in (
    'VIEW-20261110-003#f2',
    ((pimco.get('facts') or {}).get('at_cutoff') or {}).get('evidence_ref'),
    hg(r_u1).get('evidence_ref'), hg(r_u2).get('evidence_ref'),
    (pr.get('baseline') or {}).get('evidence_ref'), hz_ref,
    _pzref.get('evidence_ref')) if x and x in idx_ref]
oecd_at = (oecd.get('facts') or {}).get('at_cutoff') or {}
pimco_reading = (
    '席位推导: 『%s』读作——到表述到期日 %s(按期限上界;下界 %s),联邦基金'
    '目标区间上限的累计上调幅度低于期货曲线同期限隐含的累计幅度(引擎定价'
    '曲线中到期日当月或之前最后一个合约月 %s 月均隐含累计 %sbp)。政策方向与'
    '市场相同(均为上调)而幅度更低,故判为有证据支持的预期差(弱证据: 单一'
    '机构、表述含糊、幅度不可量化;『低于曲线隐含幅度』为席位对原文的解读,'
    '原文未给数值)。' % (pimco.get('value_raw'), hz_end, hz_low, hz_m,
                      fmt(hz_bp)))
pimco_cond = [
    {'attribution': 'ai_inferred',
     'condition': (
         '若 %s 或之前 DFEDTARU 最新读数较 %s 的 %s 累计上调达到或超过 '
         '%sbp(即期货曲线对 %s 合约月均隐含的累计幅度;目标区间上限按 %sbp '
         '步长变动,折合等于或超过%s次加息;阈值为期货月均隐含有效利率口径,'
         '出处快照期货曲线),则『无需完全兑现市场定价的加息』被证伪' % (
             hz_end, as_of, fmt(base_u), fmt(hz_bp), hz_m, fmt(step_bp),
             cn_num(_hz_n))),
     'observable': 'DFEDTARU'},
    {'attribution': 'ai_inferred',
     'condition': (
         '若 %s 时 DFEDTARU 读数较 %s 的 %s 累计上调已达到 %sbp(即期货曲线'
         '对窗口内最后一个完整合约月 %s 月均隐含的累计幅度;目标区间上限按 '
         '%sbp 步长变动,折合等于或超过%s次加息;阈值为期货月均隐含有效利率'
         '口径,出处快照期货曲线),则『无需完全兑现市场定价的加息』在证伪窗口内'
         '未获路径前段支持——预期差未显现' % (
             fw['end'], as_of, fmt(base_u), fmt(win_p.get('change_bp')), win_m,
             fmt(step_bp), cn_num(_wp_n))),
     'observable': 'DFEDTARU'}]
# Audit-R33 任务5修订(独立预审 m): 三时点同比读数逐期列出(引擎面派生同比
# 原值),证伪条件写明期数、到期日在窗口外与窗内可核验期数(季度节奏为席位
# 推断,冻结发布日历未收录其发布日);最新两期已不低于点位即拒绝装配。
_gdp_vals = [yoy_of(cell_by_id('US_REAL_GDP'), lbl) for lbl in LABELS]
if None in _gdp_vals:
    refuse('美国实际 GDP 三时点同比不可比(须席位另写)')
_gdp_txt = '、'.join(fmt(v) for v in _gdp_vals)
_gdp_down = all(_gdp_vals[i] > _gdp_vals[i + 1] for i in range(2))
if _gdp_vals[-1] >= oecd_hi or _gdp_vals[-2] >= oecd_hi:
    refuse('最新两期同比已不低于点位——判据须席位另写')


def _q_label(y, q):
    return '%dQ%d' % (y, q)


_q_y, _q = int(as_of[:4]), (int(as_of[5:7]) - 1) // 3 + 1
_q_in = []
for _ in range(8):                     # 至多看八个季度
    _qe_m = _q * 3
    _qe = datetime.date(_q_y + (_qe_m - 1) // 12, (_qe_m - 1) % 12 + 1, 1)
    _qe = _qe.replace(day=28) + datetime.timedelta(days=4)
    if str(_qe + datetime.timedelta(days=29)) > fw['end']:
        break
    _q_in.append(_q_label(_q_y, _q))
    _q += 1
    if _q > 4:
        _q, _q_y = 1, _q_y + 1
oecd_reading = (
    '席位推导: 该行为年度增速点位(原文『%s』),定价面只覆盖联邦基金利率,'
    '增长预测无同期限市场定价工具——『机构对市场』的预期差无从建立;对'
    '事实一端,引擎事实面的美国实际 GDP 最新读数为 %s(水平值,观测 %s),'
    '三时点同比读数 %s%s,与『增速放缓』的方向判断不矛盾。故按契约口径记为'
    '非预期差并写明缺口: 『无从对照』不等于『不存在』。' % (
        oecd.get('value_raw'), fmt(oecd_at.get('value')),
        oecd_at.get('observation_date'), _gdp_txt,
        ',逐期走低' if _gdp_down else ''))
oecd_cond = [
    {'attribution': 'ai_inferred',
     'condition': (
         '若 %s 之后公布的 US_REAL_GDP 同比读数(美国实际 GDP)连续两个季度'
         '不低于 %s(原文所列较高的年度增速点位),则『%s』的放缓路径被证伪;'
         '该点位到期日 %s 在证伪窗口之外,窗口内至多可核验 %s 两期读数'
         '(季度节奏为席位推断,冻结发布日历未收录其发布日);当前三时点同比'
         '读数 %s,未触发' % (
             as_of, fmt(oecd_hi), oecd.get('value_raw'), oecd.get('horizon_end'),
             ' 与 '.join(_q_in) if len(_q_in) == 2 else '、'.join(_q_in) or '无',
             _gdp_txt)),
     'observable': 'US_REAL_GDP'}]
supported_gaps = [
    {'row_id': 'VIEW-20261110-003#f2', 'verdict': 'supported',
     'reading': pimco_reading, 'reading_attribution': 'ai_inferred',
     'competing_explanation': (
         '【假设】表述与定价的差异源于口径而非方向: 期货曲线含期限溢价与'
         '分布均值,且该机构所说的『市场定价』可能指时点路径而非月均口径——'
         '若如此,该行并非预期差。'),
     'reason': (
         '原文为文字型表述、未给幅度,政策方向与市场相同(均为上调)而幅度'
         '更低;单一机构、表述含糊,证据强度弱。'),
     'falsification_conditions': pimco_cond,
     'evidence_refs': pimco_refs},
    {'row_id': 'VIEW-20261111-002#f3', 'verdict': 'not_a_gap',
     'reading': oecd_reading, 'reading_attribution': 'ai_inferred',
     'competing_explanation': (
         '【假设】该增速点位显著低于市场隐含的增长路径,则『机构低于市场』的'
         '预期差可能存在,但本轮定价面未入库利率以外的工具,无法检验。'),
     'reason': '增长预测无同期限市场定价工具;与事实面方向不矛盾。',
     'falsification_conditions': oecd_cond,
     'evidence_refs': [x for x in (oecd.get('evidence_refs') or []) if x]}]
seat_summary = (
    '问句问的是『市场定价和机构观点之间有哪些预期差、未来什么会证伪』。'
    '引擎对照面: %s 份机构观点可见、%s 行对照,可与同期限市场定价或事实'
    '对账 %s 行,其中引擎判为预期差候选 %s 行、须席位推导 %s 行。席位推导'
    '后: 有证据支持的预期差 %d 项(PIMCO『%s』——政策方向与市场相同、幅度'
    '更低且不可量化,单一机构、表述含糊,属弱证据);判非预期差 %d 项'
    '(OECD 美国增长预测,无同期限定价);有编号的加息路径与同期限期货定价'
    '之差最大仅 %sbp,不足半个定价步长(%sbp);欧央行与日本央行政策利率表述'
    '与截止日可得读数一致,但对账读数陈旧源于序列形态(日本央行有冻结日历'
    '维持记录;欧元区其后有无新决议本轮冻结证据未知);定价面只入库美国联邦'
    '基金利率期货(中国、欧元区、日本的政策利率与美股、盈利、欧元区增长目标'
    '均无同期限定价),%s 行中 %s 行机构目标未映射到在册指标——'
    '『未建立对照』不等于『无预期差』。证伪窗口(%s,%s→%s): 窗内到期 %d 行,'
    '其中可检验 %d 行;PIMCO 表述的到期日按期限上界取 %s(期限下界 %s 在'
    '窗口内),上界在窗口之外,窗口内只能核其路径前段;窗口后到期 %s 行'
    '(最早 %s)。到期预测核验保持 PARTIAL。'
    % (fmt(sm.get('n_views_visible')), fmt(sm.get('n_rows')),
       fmt(sm.get('comparable_n')), fmt(sm.get('candidate_n')),
       fmt(sm.get('reading_required_n')), n_sup, pimco.get('value_raw'), n_ng,
       fmt(g_max), fmt(pr.get('material_gap_bp')), fmt(sm.get('n_rows')),
       fmt(sm.get('unmapped_n')),
       fw.get('source'), fw.get('start'), fw.get('end'), n_in, n_test, hz_end,
       hz_low,
       fmt(wt.get('n_rows_after_window')), wt.get('earliest_after_window')))
key_unknowns = [
    '机构观点发布时点的市场定价未入库(定价基线取截止日有效利率),'
    '无法还原『观点发布当日』的预期差。',
    'PIMCO 表述幅度不可量化,席位推导的判据依赖期货曲线口径。',
    '欧央行存款便利利率序列末观测日为 %s,其后至截止日有无新决议本轮冻结'
    '证据未知(日本有冻结日历维持记录);陈旧读数上的对账不等于现值对账。'
    % _ea_eff,
    '定价面只入库美国联邦基金利率期货,其余目标无同期限市场定价;%s 行机构'
    '目标未映射到在册指标,无从对账。' % fmt(sm.get('unmapped_n')),
    '期货曲线远端合约流动性有限,隐含幅度的可信度低于近月。']
if yoy_of(cell_by_id('CPI'), LABELS[2]) is None:
    key_unknowns.append('美国CPI最新锚缺同比基期,通胀面最新一期的同比读数'
                        '暂不可得。')
comments = [
    '证伪窗口由问句『%s』解析为 %s 个月,窗口内外逐行可检验性见引擎渲染面;'
    '本档只对须席位推导的两行给出判定,其余行沿用引擎确定性判定。'
    % (fw.get('source'), fmt(fw.get('months'))),
    '到期预测核验保持 PARTIAL: 窗后到期 %s 行的 earliest 为 %s,按实际到期'
    '证据更新;已到期未核验%s(%s),逐行见引擎渲染面。' % (
        fmt(wt.get('n_rows_after_window')), wt.get('earliest_after_window'),
        cn_num(len(_mat_unv)) + '行' if _mat_unv else '零行', _mat_reason),
    '同一观点文件对其基线情景自述的证伪条件(『%s』)针对的是该机构的基线'
    '情景而非本行表述,未计入本行的证伪条件,在此如实转述供参考。'
    % (c1p.get('condition') or '')]
echo = {
    'as_of': blk.get('as_of'),
    'n_views_visible': sm.get('n_views_visible'), 'n_rows': sm.get('n_rows'),
    'comparable_n': sm.get('comparable_n'),
    'engine_candidate_n': sm.get('candidate_n'),
    'engine_candidates_echoed': sorted(
        r['row_id'] for r in rows_all if r.get('candidate')),
    'gaps_echoed': [{'code': g.get('code'), 'region': g.get('region'),
                     'metric_id': g.get('metric_id')} for g in gaps],
    'window_echo': {'months': fw.get('months'), 'start': fw.get('start'),
                    'end': fw.get('end')},
    'seat_summary': seat_summary, 'supported_gaps': supported_gaps,
    'key_unknowns': key_unknowns, 'comments': comments}

# ── 质量门注记 / 声明 ────────────────────────────────────────────────
# (政策记录计数 _n_dec/_n_maint、截止日当日读数 _cut_rows、资产月窗端点
#  敏感性 _flip、已到期未核验行 _mat_unv 在上方工单段计算,此处只引用。)
cov = blk.get('pricing_coverage') or {}
cov_txt = '、'.join('%s %s' % (REG_TXT.get(k, k), (v or {}).get('status'))
                    for k, v in cov.items()) or '无'
gate_txt = next((str((s.get('envelope') or {}).get('gate_a'))
                 for s in rep.get('steps') or []
                 if isinstance(s.get('envelope'), dict)
                 and (s.get('envelope') or {}).get('gate_a') is not None),
                str((run.get('evidence_gate') or {}).get('discipline') or '未披露'))
n_ref = sum(len(c['evidence_refs']) for c in contras) + sum(
    len(l.get('evidence_refs') or []) for l in chain_links)
now = datetime.datetime.now().astimezone()
judgment = {
    'schema_version': '1.1',
    'agent_declaration': {
        'attribution': 'ai_inferred',
        'agent': 'Agent 研究席(操作者会话经正式入口 ia_cli research-one 代持席位)',
        'produced_by': ('Agent 研究席(操作者会话经正式入口 ia_cli research-one '
                        '代持席位, %s, %s)' % (run.get('ts_utc') or '', as_of)),
        'written_at': now.isoformat(timespec='seconds'),
        'note': ('判断内容 100% Agent 产;证据引用取自本报告证据索引原值;结构化'
                 '回声逐字取自引擎分面块,叙述数值与引擎面逐位对账;校验是纪律'
                 '地板,判断质量归 Agent 与独立审计。'),
        'tooling': ('席位侧装配脚本 scripts/seat_tools/'
                    'make_expectations_gap_judgment.py: 确定性装配——环境五面'
                    '(四地三时点/转折/传导/历史类比/事后表现)按引擎分面块模板'
                    '装配(数值与日期零手敲);预期差逐行判定的措辞、竞争解释与'
                    '证伪判据为席位撰写并固化于脚本,数值取自引擎定价曲线与'
                    '规则池;对质观测窗的同窗读数由引擎按冻结序列复算;零网络'
                    '调用;席位经正式入口提交,契约与文本一致性校验照常执行,'
                    '判断质量归席位与独立审计'),
        'basis': ('读本轮 AGENT_SEAT_ENVELOPE 工单、证据索引(%d 行)、预期差'
                  '对照块(%s 行对照/可比 %s 行/须席位推导 %s 行)、工单冻结输入'
                  '(发布日历/注册表/快照/观点库文件)后独立研判;引擎只供确定性'
                  '证据,判断内容 100%% 归 Agent。'
                  % (len(rep.get('evidence_index') or []), fmt(sm.get('n_rows')),
                     fmt(sm.get('comparable_n')),
                     fmt(sm.get('reading_required_n'))))},
    'l3': {'contradictions': contras,
           'mechanism_chains': [{'id': 'M1', 'title': '通胀再加速→政策再收紧→'
                                 '实际利率→风险资产', 'links': chain_links}]},
    'l4': {'scenarios': scen},
    'quality_gate_notes': [
        '证据绑定: %d 条矛盾陈述+机制链 %d 环共 %d 条引用,全部解析到本报告'
        '证据索引;零悬空引用。' % (len(contras), len(chain_links), n_ref),
        '竞争性解释: 每条矛盾陈述并列至少 2 条(均标【假设】或【尚未验证】),'
        '如实并列、不裁胜负。',
        '预期差判定: 引擎候选 %s 行、须席位推导 %s 行全部判定;有证据支持的'
        '预期差 %d 项(弱证据)、判非预期差 %d 项;未建立对照的行不判为'
        '『无预期差』。' % (fmt(sm.get('candidate_n')),
                          fmt(sm.get('reading_required_n')), n_sup, n_ng),
        '定价口径: %s;定价步长 %sbp、实质缺口线 %sbp;定价覆盖: %s。'
        % (pr.get('instrument'), fmt(pr.get('step_bp')),
           fmt(pr.get('material_gap_bp')), cov_txt),
        '数据面: Gate A 状态 %s(逐项见引擎渲染的 Gate A 段);事实保留 %s 项。'
        % (gate_txt, fmt((run.get('evidence_gate') or {}).get('counts', {})
                         .get('facts_kept'))),
        '政策口径披露: 决议日与生效日成对出现——日本为冻结发布日历实录'
        '(决议记录%s条、维持记录%s条);美国/欧元区为序列变动点(=生效日)'
        '加惯例回推的决议日(美联储=生效前一日;欧央行=决议后首个周三,仅周三'
        '生效时),冻结日历无美/欧政策记录(各%s/%s条);发布日历版本 %s'
        '(建档 %s,更新 %s)、条目 %s 条。' % (
            cn_num(_n_dec['JP']), cn_num(_n_maint['JP']),
            cn_num(_n_dec['US'] + _n_maint['US']),
            cn_num(_n_dec['EA'] + _n_maint['EA']),
            str(cal_doc.get('version') or '未标注'),
            str(cal_doc.get('created') or '未标注'),
            str(cal_doc.get('updated') or '未标注'), n_cal),
        ('截止日当日读数说明: %s(观测 %s)为快照冻结值,日内时点与收盘状态'
         '在冻结面内不可核(本轮运行时间戳 %s UTC)。' % (
             '、'.join(str(r.get('metric_id')) for r in _cut_rows), as_of,
             run.get('ts_utc') or '未标注')
         if _cut_rows else '截止日当日读数说明: 资产月窗终点无截止日当日读数。'),
        '资产月窗端点敏感性: %s。' % (
            ';'.join(_flip) if _flip
            else '终点改取截止日前一交易日不改变各指标变动方向'),
        '引擎缺口披露(数据面缺口 %d 项,非本档判断问题;逐项见 gaps_echoed)。'
        % len(gaps),
        '证伪窗口: %s→%s(问句『%s』解析为 %s 个月);窗内到期 %d 行、其中可'
        '检验 %d 行,窗口后到期 %s 行;到期预测核验保持 PARTIAL(已到期未核验'
        '%s: %s——%s)。'
        % (fw.get('start'), fw.get('end'), fw.get('source'),
           fmt(fw.get('months')), n_in, n_test,
           fmt(wt.get('n_rows_after_window')),
           cn_num(len(_mat_unv)) + '行',
           '、'.join(str(r.get('row_id')) for r in _mat_unv) or '无',
           _mat_reason)],
    'reader_map': {
        'headline_conclusion': headline,
        'regions': regions, 'transmission': transmission,
        'turnings': turnings, 'turning_supplement': turning_supplement,
        'history_periods': history_periods,
        'rates_decomposition': rates_decomposition,
        'asset_returns_echo': asset_returns_echo,
        'expectations_gap': echo}}

_txt = json.dumps(judgment, ensure_ascii=False)
assert not re.search(r'[A-Z0-9_][较公为系][去年厘官]', _txt), '标识符与中文之间缺空格'
assert '  ' not in _txt, '连续空格'

# ── 自检(不绿不写) ────────────────────────────────────────────────────
import agent_judgment as aj                                       # noqa: E402

mids = aj._registry_metric_ids(tree)
res = aj.validate_judgment(
    judgment, {e.get('ref') for e in rep['evidence_index']}, mids,
    policy_events=aj.collect_policy_events(cal),
    as_of=(run.get('evidence_asof') or as_of))
con = jc.verify_judgment(judgment, rep)
print('discipline passed', res['passed'],
      json.dumps(res['violations'], ensure_ascii=False)[:2000])
print('contract', con['verdict'], json.dumps(con['stats'], ensure_ascii=False),
      'family_checks', len(con['map_checks']))
for c in con['map_checks']:
    if c['status'] != 'VERIFIED':
        print('   FAMILY', json.dumps(c, ensure_ascii=False)[:600])
for u in con['unresolved_unbound'][:12]:
    print('   UNB', json.dumps(u, ensure_ascii=False)[:400])
for c in con['verdicts']:
    if c['status'] != 'VERIFIED':
        print('   VERD', json.dumps({k: c.get(k) for k in (
            'item', 'token', 'metric', 'value', 'expected', 'status', 'note')},
            ensure_ascii=False)[:500])
for c in con['six_checks']:
    if c['status'] != 'VERIFIED':
        print('   SIX', json.dumps(c, ensure_ascii=False)[:600])
if not (res['passed'] and con['verdict'] == 'VERIFIED'
        and len(con['map_checks']) >= 30):
    print('NOT WRITTEN')
    sys.exit(3)
json.dump(judgment, open(jp_out, 'w', encoding='utf-8'), ensure_ascii=False,
          indent=2)
json.dump({'turnings': [(t['metric_id'], t['date']) for t in turnings],
           'picks': [(p.get('metric_id'), p.get('to_ym')) for p in picks],
           'history': [h['anchor_ym'] for h in history_periods],
           'headline': headline,
           'revision': {
               'policy_counts': {'us_up': len(us_up), 'ea_up': len(ea_up),
                                 'jp_segments': len(jp_seg),
                                 'tightenings_in_window': _n_up,
                                 'after_turning_window_end': len(_after),
                                 'before_turning_window_start': len(_before)},
               'face_off': [
                   {'step': l['step'], 'metric': l['distinguishing_metric'],
                    'window': l.get('observation_window'),
                    'verdict': l['face_off_verdict']}
                   for l in transmission[0]['links'] if l.get('observation_window')],
               'pricing_reference': {'month': hz_m, 'change_bp': hz_bp,
                                     'evidence_bound': bool(hz_ref)},
               'cn_policy_cells': {m: _cn_cell_txt(m) for m in CN_POLICY_MIDS},
               'cutoff_day_rows': [str(r.get('metric_id')) for r in _cut_rows],
               'endpoint_flips': _flip,
               'matured_unverified': [str(r.get('row_id')) for r in _mat_unv],
               'calendar': {'version': str(cal_doc.get('version') or ''),
                            'entries': n_cal,
                            'decision_records': _n_dec,
                            'maintenance_records': _n_maint}}},
          open(_out, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('written', jp_out, os.path.getsize(jp_out))
print('HEADLINE', headline)
