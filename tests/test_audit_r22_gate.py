# -*- coding: utf-8 -*-
"""Audit-R22(R66) 门测试 — 发布批次/政策时序/中文窜写拦截/读者渲染面。

指令五任务的确定性判据(离线可复跑,零外部数据):
  §A 发布批次日历(同批多指标/一次补发两月/前一天-当天)
  §B 六族锚可见性(2025-11-19 面: CPI/核心CPI/失业/GDP/核心PCE/工业生产)
  §C 政策时序(决议≠生效: ECB 09-10→09-16/Fed 09-16→09-17/2022-07 上限
     2.50 生效 07-28/纪要 11-18 可见/一年窗先降后升净零+决议日入路径)
  §D 跨国政策事件簇(Fed+ECB ±7 日合并=同一全球政策事件)
  §E 契约正反例(真实工单档案: 三窜写全 CONTRADICTED,原文与中文同义
     正例 VERIFIED——pp 容差 0.06/中文别名面/观测月串锚序)
  §F 读者渲染(首页三件/对质表/逐窗并列面/决议→生效分记/缺席分支)
  §G 溯源(运行代码 SHA 入 MAP_REPORT 头+批次对账+修订口径注记)
"""
import copy
import datetime
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
sys.path.insert(0, os.path.join(ROOT, 'scripts', 'research_contract'))

import test_audit_r19_gate as r19                     # noqa: E402
import release_calendar as rc                         # noqa: E402
import research_map_planner as rmp                    # noqa: E402
import snapshot_builder as sb                         # noqa: E402
from judgment_contract import build_face, verify_judgment  # noqa: E402

TMPG = tempfile.mkdtemp(prefix='r22gate_')
RESULTS = []
ARC_DIR = os.path.join(
    ROOT, 'docs/autonomous-rd/r21-evidence/acceptance/'
    '20261119T120815Z_给我一份全球宏观经济变化地图_美国_中国_欧元区_'
    '日本在12个月前_3个月前和最')


def check(name, ok, detail=''):
    RESULTS.append((name, bool(ok), str(detail)[:220]))
    print(('  ✅ ' if ok else ' ❌ ') + name
          + (f' — {detail}' if detail else ''), flush=True)


# ═══ §A 发布批次日历(纯 API,config/release_calendar.json v1.2.0) ═══
def sec_a():
    print('═══ §A 发布批次: 同批多指标/一次补发两月/前一天-当天 ═══')
    e = rc.first_publish('CORE_CPI', '2025-09-01') or {}
    check('§A 核心CPI 2025-09: 首发日 2025-10-24/前一天 10-23 不可见/挂批',
          e.get('first_publish') == '2025-10-24'
          and e.get('not_published_as_of') == '2025-10-23'
          and e.get('batch_id') == 'BLS-CPI-2025M09-REL',
          json.dumps(e, ensure_ascii=False)[:120])
    b1 = rc.batch_of('CPI', '2025-09-01')
    b2 = rc.batch_of('CORE_CPI', '2025-09-01')
    check('§A 同批多指标: CPI 与核心CPI 同一份 BLS 新闻稿(整批一致)',
          bool(b1) and b1.get('batch_id') == b2.get('batch_id')
          and b1.get('published_on') == '2025-10-24'
          and set(b1.get('metrics') or []) >= {'CPI', 'CORE_CPI'}
          and b1.get('backfill_months') == 1,
          str(b1)[:120])
    eu = rc.first_publish('UNEMPLOYMENT', '2025-11-01') or {}
    bu = rc.batch_of('UNEMPLOYMENT', '2025-11-01') or {}
    check('§A 十一月失业率: 首发日 2025-12-16/前一天 12-15 不可见/'
          '就业形势报告批(含 NFP/AHE)',
          eu.get('first_publish') == '2025-12-16'
          and eu.get('not_published_as_of') == '2025-12-15'
          and set(bu.get('metrics') or []) >= {'UNEMPLOYMENT', 'NFP', 'AHE'},
          json.dumps(bu, ensure_ascii=False)[:120])
    p10 = rc.batch_of('CORE_PCE', '2025-10-01')
    p11 = rc.batch_of('CORE_PCE', '2025-11-01')
    ep = rc.first_publish('CORE_PCE', '2025-10-01') or {}
    check('§A 一次补发两月: 2025-10 与 11 核心PCE 同批 2026-01-22 首发'
          '(01-21 不可见,backfill=2)',
          bool(p10) and p10 == p11
          and p10.get('published_on') == '2026-01-22'
          and p10.get('backfill_months') == 2
          and [str(x)[:7] for x in p10.get('obs_months') or []]
          == ['2025-10', '2025-11']
          and ep.get('not_published_as_of') == '2026-01-21',
          json.dumps(p10, ensure_ascii=False)[:130])
    pub, basis = rmp._visible_publish('CORE_CPI', 'M', '2025-09-01')
    check('§A 发布依据随批号披露(读者可按批核)',
          pub == '2025-10-24' and 'batch=BLS-CPI-2025M09-REL' in basis,
          basis)


# ═══ §B 六族锚可见性(2025-11-19 面=12个月前锚) ═══
def sec_b(plan, root):
    print('═══ §B 六族: 2025-11-19 面只见当时已发布观测 ═══')
    _root_of_plan = root
    cells = {(c.get('metric_id')): c
             for c in (plan.get('point_values') or {}).get('cells') or []}
    a12 = '12个月前'

    def anchor(mid):
        c = cells.get(mid) or {}
        return (c.get('anchors') or {}).get(a12) or {}

    v = anchor('CPI')
    check('§B CPI: 12个月前锚=2025-09(10-24 已发布可引,日历实录)',
          v.get('status') == 'ok'
          and str(v.get('observation_date'))[:7] == '2025-09'
          and v.get('publication_date') == '2025-10-24'
          and str(v.get('publication_basis')).startswith('calendar:'),
          json.dumps(v, ensure_ascii=False)[:130])
    v = anchor('UNEMPLOYMENT')
    pub09 = rmp._visible_publish('UNEMPLOYMENT', 'monthly', '2025-09-01')[0]
    check('§B 失业率: 12个月前锚=2025-08(八月 4.3;九月 11-20 才可见'
          '故不可引)',
          v.get('status') == 'ok'
          and str(v.get('observation_date'))[:7] == '2025-08'
          and v.get('value') == 4.3
          and str(pub09) == '2025-11-20',
          f'{json.dumps(v, ensure_ascii=False)[:90]}|九月首发={pub09}')
    v = anchor('US_REAL_GDP')
    pubq3 = rmp._visible_publish('US_REAL_GDP', 'quarterly',
                                 '2025-07-01')[0]
    check('§B GDP: 12个月前锚=2025-04(Q2;Q3 12-23 才可见故不可引)',
          v.get('status') == 'ok'
          and str(v.get('observation_date'))[:7] == '2025-04'
          and str(pubq3) == '2025-12-23',
          f'{json.dumps(v, ensure_ascii=False)[:90]}|Q3首发={pubq3}')
    v = anchor('INDPRO')
    check('§B 工业生产: 12个月前锚≤2025-08(09/10 月保守界 2026-01-22)',
          v.get('status') == 'ok'
          and str(v.get('observation_date'))[:7] <= '2025-08',
          json.dumps(v, ensure_ascii=False)[:110])

    def series_walk(mid, as_of):
        """锚纪律复演: 序列内发布日≤锚日的最新观测(与 point_values 同径)。"""
        snap = json.load(open(os.path.join(
            _root_of_plan, 'data', 'daily',
            'research_snapshot_20261117.json'), encoding='utf-8'))
        ser = (snap.get('series_store') or {}).get(mid) or {}
        for k in range(len(ser.get('dates') or []) - 1, -1, -1):
            if ser['dates'][k] > as_of:
                continue
            pub, basis = rmp._visible_publish(mid, 'M', ser['dates'][k])
            if pub is None or pub <= as_of:
                return ser['dates'][k], pub, basis
        return None, None, None

    d, pub, basis = series_walk('CORE_CPI', '2025-11-19')
    check('§B 核心CPI: 2025-11-19 面最近可见=2025-09(同批 10-24 首发)',
          str(d)[:7] == '2025-09' and pub == '2025-10-24'
          and 'CORECPI' in str(basis),
          f'{d}|{pub}|{basis}')
    d, pub, basis = series_walk('CORE_PCE', '2025-11-19')
    check('§B 核心PCE: 2025-11-19 面最近可见≤2025-08(09/10 月积压至 '
          '2026-01-22,不提前引用)',
          d is not None and str(d)[:7] <= '2025-08'
          and (pub is None or str(pub) <= '2025-11-19'),
          f'{d}|{pub}')


# ═══ §C 政策时序(决议日≠生效日;纪要;净零路径) ═══
def sec_c():
    print('═══ §C 政策时序: 决议/生效分记+纪要发布日+路径复算 ═══')
    pf = rmp.POLICY_FACE.get('ECB_MRO') or {}
    pd_ = rmp._policy_dates(pf, '2026-09-16', value_change_date='2026-09-16')
    check('§C ECB 2026-09: 决议 09-10→生效 09-16(值变更日=生效日)',
          pd_.get('decision') == '2026-09-10'
          and pd_.get('effective') == '2026-09-16',
          json.dumps(pd_, ensure_ascii=False)[:120])
    pfu = rmp.POLICY_FACE.get('DFEDTARU') or {}
    pd2 = rmp._policy_dates(pfu, '2026-09-17', value_change_date='2026-09-17')
    check('§C Fed 2026-09: 决议 09-16→生效 09-17(次日生效)',
          pd2.get('decision') == '2026-09-16'
          and pd2.get('effective') == '2026-09-17',
          json.dumps(pd2, ensure_ascii=False)[:120])
    pd3 = rmp._policy_dates(pfu, '2022-07-29', value_change_date='2022-07-28')
    check('§C 2022-07: 决议 07-27→生效 07-28(七月末上限 2.50 的由来)',
          pd3.get('decision') == '2022-07-27'
          and pd3.get('effective') == '2022-07-28',
          json.dumps(pd3, ensure_ascii=False)[:120])
    check('§C ECB 不规则生效日(变更日非周三): 决议不可推=如实缺席',
          rmp._policy_dates(pf, '2026-08-14',
                            value_change_date='2026-08-14')
          .get('decision') is None)
    check('§C FOMC 十月纪要: 11-18 可见/11-17 不可见',
          rmp.policy_doc_visible('FOMC-MINUTES-2026-10', '2026-11-18')
          and not rmp.policy_doc_visible('FOMC-MINUTES-2026-10',
                                         '2026-11-17'))
    dates = ['2025-10-01', '2025-10-30', '2025-11-20', '2025-12-11',
             '2026-09-17', '2026-11-18']
    vals = [4.25, 4.0, 4.0, 3.75, 4.0, 4.0]
    wp = rmp._policy_window_path(dates, vals, '2026-11-19',
                                 metric_id='DFEDTARU')
    ev = {e['date']: e for e in (wp or {}).get('events', [])}
    check('§C 一年窗路径: 先降 25(决议 12-10)再升 25(决议 09-16)净零',
          wp.get('net_bp') == 0
          and ev.get('2025-12-11', {}).get('decision_date') == '2025-12-10'
          and ev.get('2026-09-17', {}).get('decision_date') == '2026-09-16',
          str(sorted(ev))[:120])


# ═══ §D 跨国政策事件簇 ═══
def sec_d():
    print('═══ §D 同一事件的跨国信号合并(决议日 ±7 日聚簇) ═══')
    plan = {'point_values': {'cells': [
        {'region': 'US', 'metric_id': 'DFEDTARU',
         'display_name': 'Fed 目标区间上限',
         'policy_window_path': {'events': [
             {'date': '2026-09-17', 'decision_date': '2026-09-16',
              'delta_bp': 25, 'from': 3.75, 'to': 4.0}]}},
        {'region': 'EA', 'metric_id': 'ECB_MRO',
         'display_name': 'ECB 主要再融资利率',
         'policy_window_path': {'events': [
             {'date': '2026-09-16', 'decision_date': '2026-09-10',
              'delta_bp': -25, 'from': 3.15, 'to': 2.9}]}},
        {'region': 'CN', 'metric_id': 'CN_OMO_7D',
         'display_name': '逆回购七天',
         'policy_window_path': {'events': [
             {'date': '2026-05-20', 'decision_date': '2026-05-20',
              'delta_bp': -10, 'from': 1.5, 'to': 1.4}]}}]}}
    out = rmp.policy_clusters_from_plan(plan)
    cl = out.get('clusters') or []
    fed_ecb = next((c for c in cl if 'POLCLUSTER' in str(c.get('cluster_id'))
                    and set(c.get('regions') or []) == {'US', 'EA'}), {})
    evs = fed_ecb.get('events') or []
    check('§D Fed(决议 09-16)+ECB(决议 09-10)合并=同一全球政策事件',
          len(cl) == 2 and bool(fed_ecb)
          and fed_ecb.get('same_event_cross_country') is True
          and sorted(str(e.get('date')) for e in evs)
          == ['2026-09-10', '2026-09-16']
          and str(fed_ecb.get('date_from')) == '2026-09-10'
          and str(fed_ecb.get('date_to')) == '2026-09-16',
          json.dumps(fed_ecb, ensure_ascii=False)[:150])
    dts = {str(e.get('date')): e.get('decision_to_effective_days')
           for e in evs}
    check('§D 逐事件决议→生效间隔: Fed=1 日/ECB=6 日(分记不混同)',
          dts.get('2026-09-16') == 1 and dts.get('2026-09-10') == 6,
          str(dts))
    cn = next((c for c in cl if c.get('regions') == ['CN']), {})
    check('§D 远端单国事件独立成簇(非跨国)',
          bool(cn) and cn.get('same_event_cross_country') is False,
          json.dumps(cn, ensure_ascii=False)[:100])


# ═══ §E 契约正反例(真实工单档案,离线零外部数据) ═══
def sec_e():
    print('═══ §E 三窜写拦截+原文/中文同义正例(真实工单档案) ═══')
    jd0 = json.load(open(os.path.join(ARC_DIR, 'agent_judgment.json'),
                         encoding='utf-8'))
    rj = json.load(open(os.path.join(ARC_DIR, 'report.json'),
                        encoding='utf-8'))
    face = build_face(rj)

    def contract(mutate):
        jd = copy.deepcopy(jd0)
        mutate(jd)
        res = verify_judgment(jd, rj, face=face)
        return res, [f for f in (res.get('map_checks') or [])
                     if f.get('status') != 'VERIFIED']

    def h22(jd):
        return next(h for h in jd['reader_map']['history_periods']
                    if h.get('anchor_ym') == '2022-06')

    res, bad = contract(lambda jd: None)
    check('§E 正例: 原文未动 → VERIFIED(契约改动零漂移)',
          res.get('verdict') == 'VERIFIED' and not bad,
          str([b.get('item') for b in bad])[:120])
    res, bad = contract(lambda jd: h22(jd)['ex_post'].__setitem__(
        '3m', '标普500指数上涨99.00%、UST_10Y +0.85pp、DXY +7.10%、'
              'GOLD_F −7.49%、NIKKEI225 −1.73%(锚月末→2022-09 月末口径)。'))
    check('§E 反例①中文: 标普500指数上涨99.00%(引擎 −5.28)→CONTRADICTED',
          res.get('verdict') == 'CONTRADICTED'
          and any('中文面' in str(b.get('note')) for b in bad),
          str([str(b.get('note'))[:80] for b in bad[:1]]))
    res, bad = contract(lambda jd: h22(jd)['ex_post'].__setitem__(
        '3m', 'SPX −5.28%、美国十年期国债收益率上升0.35个百分点、'
              'DXY +7.10%、GOLD_F −7.49%、NIKKEI225 −1.73%'
              '(锚月末→2022-09 月末口径)。'))
    check('§E 反例②pp 窜写: +0.35 个百分点(引擎 +0.85,容差 0.06)→'
          'CONTRADICTED',
          res.get('verdict') == 'CONTRADICTED'
          and any('UST_10Y' in str(b.get('note')) for b in bad),
          str([str(b.get('note'))[:80] for b in bad[:1]]))
    res, bad = contract(lambda jd: h22(jd)['ex_post'].__setitem__(
        '3m', 'SPX −5.28%、UST_10Y +0.35pp、DXY +7.10%、GOLD_F −7.49%、'
              'NIKKEI225 −1.73%(锚月末→2022-09 月末口径)。'))
    check('§E 反例②ASCII: UST_10Y +0.35pp 同拦(pp 容差收紧生效)',
          res.get('verdict') == 'CONTRADICTED'
          and any('UST_10Y' in str(b.get('note'))
                  and '中文面' not in str(b.get('note')) for b in bad),
          str([str(b.get('note'))[:60] for b in bad[:1]]))

    def n3(jd):
        for r in jd['reader_map']['regions']:
            if r.get('region') == 'US':
                r['from_to'] = r['from_to'].replace(
                    '观测 2025-04→2026-04→2026-07',
                    '观测 2025-07→2026-04→2026-07')
    res, bad = contract(n3)
    check('§E 反例③观测串: GDP Q2→Q3(2025-07 在序列但锚前不可见)→'
          'CONTRADICTED',
          res.get('verdict') == 'CONTRADICTED'
          and any('obs_run' in str(b.get('item')) for b in bad),
          str([str(b.get('note'))[:80] for b in bad[:1]]))
    res, bad = contract(lambda jd: h22(jd)['ex_post'].__setitem__(
        '3m', '标普500指数下跌5.28%、美国十年期国债收益率上升0.85个'
              '百分点、美元指数上涨7.10%、黄金期货下跌7.49%、日经225'
              '下跌1.73%(锚月末→2022-09 月末口径)。'))
    check('§E 正例: 含义相同的正确中文表述 → VERIFIED(同义改写不误伤)',
          res.get('verdict') == 'VERIFIED' and not bad,
          str([b.get('item') for b in bad])[:120])


# ═══ 夹具: r19 冻结面 + DFEDTARU 长史(真实 2022 加息路径+净零路径) ═══
_ROOT_R22 = {}


def build_root_r22():
    if 'r22' in _ROOT_R22:
        return _ROOT_R22['r22']
    d = r19.build_root()
    mp = os.path.join(d, 'data', 'daily', 'macro_20261117.json')
    mdoc = json.load(open(mp, encoding='utf-8'))
    changes = {'2022-03-17': 0.50, '2022-05-05': 1.00, '2022-06-16': 1.75,
               '2022-07-28': 2.50, '2022-09-21': 3.00, '2022-11-03': 3.75,
               '2022-12-15': 4.50, '2023-07-27': 5.50, '2024-09-19': 5.00,
               '2024-11-08': 4.75, '2024-12-19': 4.50, '2025-06-18': 4.25,
               '2025-12-11': 4.00, '2026-09-17': 4.25}
    pts = set(changes)
    cur = datetime.date(2021, 6, 1)
    while cur <= datetime.date(2026, 11, 30):
        nxt = (cur.replace(day=28)
               + datetime.timedelta(days=4)).replace(day=1)
        pts.add((nxt - datetime.timedelta(days=1)).isoformat())  # 月末日
        cur = nxt
    dates, values = [], []
    for ds in sorted(pts):
        v = 0.25
        for cd, cv in changes.items():
            if cd <= ds:
                v = cv
        dates.append(ds)
        values.append(v)
    mdoc['data']['DFEDTARU'] = {
        'value': values[-1], 'date': dates[-1], 'frequency': 'daily',
        'unit': 'percent', 'series': {'dates': dates, 'values': values}}
    json.dump(mdoc, open(mp, 'w', encoding='utf-8'), ensure_ascii=False)
    sb.build_snapshot(target_ymd='20261117',
                      data_dir=os.path.dirname(mp),
                      out_dir=os.path.dirname(mp),
                      as_of='2026-11-17T08:36:00+08:00', trusted_root=d,
                      allow_revision=True,
                      revision_reason='R22 门夹具: DFEDTARU 注入 2022 真实'
                                      '加息路径(隔离测试重建,非生产面)')
    # 修订版落 _v2 文件;夹具将注入面回写主快照名(渲染层按 L1 snapshot_id
    # 解析主名,测试目录内覆写,不触生产面)
    dd = os.path.dirname(mp)
    v2 = os.path.join(dd, 'research_snapshot_20261117_v2.json')
    if os.path.exists(v2):
        shutil.copy(v2, os.path.join(dd, 'research_snapshot_20261117.json'))
    _ROOT_R22['r22'] = d
    return d


# ═══ §F+§G 读者渲染与溯源(计划面+合成判定,root 注入) ═══
def sec_fg(plan, root):
    print('═══ §F 读者渲染: 首页三件/对质表/逐窗并列/决议生效分记 ═══')
    # 2022-07 月末上限 2.50 核准(真实加息路径注入面)
    snap = json.load(open(os.path.join(
        root, 'data', 'daily', 'research_snapshot_20261117.json'),
        encoding='utf-8'))
    ser = (snap.get('series_store') or {}).get('DFEDTARU') or {}
    d0, v0 = rmp._month_end_obs(ser.get('dates') or [],
                                ser.get('values') or [], '2022-07')
    check('§F 核准: 2022-07 月末 Fed 目标上限=2.50(决议 07-27 生效 07-28'
          '后七月末观测即 2.50)',
          v0 == 2.5 and str(d0)[:7] == '2022-07',
          f'{d0}={v0}')
    hw = rmp.history_window_face(
        [{'anchor_ym': '2022-06'}], snap, root)
    row = next((r for r in ((hw.get('periods') or [{}])[0]
                            .get('windows', {}).get('3m') or {})
                .get('rows') or [] if r.get('metric_id') == 'DFEDTARU'), {})
    check('§F 逐窗并列: 2022-06 锚 3 月窗 DFEDTARU 1.75→3.00(+1.25pp)',
          row.get('from_value') == 1.75 and row.get('to_value') == 3.0
          and row.get('change') == 1.25 and row.get('change_unit') == 'pp'
          and row.get('from_date') == '2022-06-30'
          and row.get('to_date') == '2022-09-30',
          json.dumps(row, ensure_ascii=False)[:150])
    plan = copy.deepcopy(plan)
    plan['policy_event_clusters'] = rmp.policy_clusters_from_plan(plan)
    plan['policy_doc_facts'] = rmp.POLICY_DOC_FACTS
    rj = {'research_plan': plan,
          'run': {'question': r19.Q_MAP, 'ts_utc': '20261119T000000Z',
                  'git_head': 'r22gateHEAD'},
          # S4 步骤面在场 → 区分指标观测可解析(首页速览/对质表判定前提)
          'steps': [{'step': 'S4_history_CPI', 'envelope': {'data': {
              'series': {'dates': ['2026-08-01', '2026-09-01',
                                   '2026-10-01'],
                         'values': [4.0, 4.1, 4.2]}}}}],
          'layers': {'L1_事实层': {
              'snapshot_id': 'research_snapshot_20261117'}}}
    jd = {'reader_map': {
        'headline_conclusion': '合成总判断(离线门测试)。',
        'regions': [
            {'region': 'US', 'from_to': '美国走位(合成)。'},
            {'region': 'CN', 'from_to': '中国走位(合成)。'},
            {'region': 'EA', 'from_to': '欧元区走位(合成)。'},
            {'region': 'JP', 'from_to': '日本走位(合成)。'}],
        'transmission': [
            {'chain_name': '合成传导链',
             'links': [
                 {'observed_fact': '政策利率上调(合成)',
                  'causal_hypothesis': '加息压通胀(合成)',
                  'competing_explanation': '供给修复主导(合成)',
                  'distinguishing_metric': 'CPI',
                  'main_predicts': '加息路径下通胀回落更慢(合成)',
                  'competing_predicts': '供给修复下通胀回落更快(合成)',
                  'face_off_verdict': '支持主解释'},
                 {'observed_fact': '美元走强(合成)',
                  'causal_hypothesis': '利差驱动(合成)',
                  'competing_explanation': '避险需求驱动(合成)',
                  'distinguishing_metric': 'DXY'}]}],
        'turnings': [], 'history_periods': [
            {'period_label': '2022-06(合成类比)', 'anchor_ym': '2022-06',
             'similarity': '合成', 'difference': '合成',
             'other_regions_sync': '合成',
             'ex_post': {'3m': 'SPX −5.28%(锚月末→月末口径)。'},
             'sample_note': '合成样本注记(独立性/修订口径)'}]}}
    md = rmp.render_map_report(rj, jd, None, root=root)
    check('§F 首页三件: 总判断+四地三时点表+证据最充分传导速览',
          '## 一句总判断' in md and '## 四地三时点环境对照' in md
          and '## 证据最充分的传导(首页速览)' in md
          and md.index('## 一句总判断') < md.index('## 四地三时点环境对照')
          < md.index('## 证据最充分的传导(首页速览)')
          < md.index('## 政策口径四分面'),
          '节次序核对')
    check('§F 对质表: 主解释 vs 竞争解释(预期分立+已有观测+判断;'
          '未分立环=尚不能区分)',
          '## 主解释 vs 竞争解释(对质表)' in md
          and '支持主解释' in md and '尚不能区分' in md
          and '预期未写明——如实缺席' in md,
          '对质面渲染')
    check('§F 决议→生效分记渲染: 事件行带决议日(09-16→09-17)',
          '决议日 2026-09-16' in md and '生效日 2026-09-17' in md
          and '跨国政策事件簇' in md,
          '政策节渲染')
    check('§F 纪要事实行: FOMC 十月纪要 11-18 发布',
          'FOMC 2026年10月会议纪要' in md and '2026-11-18' in md)
    check('§F 历史段逐窗并列表在读者面(起止期/数值/单位/来源列)',
          '随后3个月窗' in md and '经济指标' in md and '资产表现' in md
          and '起期' in md and '来源' in md,
          '并列面渲染')
    md_nr = rmp.render_map_report(rj, jd, None, root=None)
    check('§F root 缺席分支: 逐窗并列面=缺席注记(不跨快照取数)',
          '逐窗并列面: **缺席**' in md_nr and '不跨快照取数' in md_nr)
    print('═══ §G 溯源: 运行代码 SHA+批次对账+修订口径 ═══')
    check('§G MAP_REPORT 头带运行代码 SHA(与 report.run.git_head 同值)',
          '代码: r22gateHEAD' in md,
          '头行核对')
    check('§G 发布批次对账节(同批指标按批列示)+修订口径注记',
          '发布批次对账' in md and 'BLS-CPI-2025M09-REL' in md
          and '修订口径' in md,
          '对账节渲染')


def test_audit_r22_gate():
    sec_a()
    root = build_root_r22()
    snap = json.load(open(os.path.join(
        root, 'data', 'daily', 'research_snapshot_20261117.json'),
        encoding='utf-8'))
    import workbench_data as wd
    plan = rmp.plan_map(r19.Q_MAP, {'economies': ['US', 'CN', 'EA', 'JP']},
                        (wd.load_registry(root)).get('by_id') or {},
                        '2026-11-19')
    plan['point_values'] = rmp.point_values(plan, snap, root)
    sec_b(plan, root)
    sec_c()
    sec_d()
    sec_e()
    sec_fg(plan, root)
    n_fail = sum(1 for _n, ok, _d in RESULTS if not ok)
    print(f'\n== R22 门: {len(RESULTS) - n_fail}/{len(RESULTS)} PASS ==')
    assert n_fail == 0, f'{n_fail} 项未过: ' + '; '.join(
        _n for _n, ok, _d in RESULTS if not ok)


if __name__ == '__main__':
    test_audit_r22_gate()
    sys.exit(0)   # R22: 直跑口径 0=全过(conftest SuiteFile 自执行静态查)
