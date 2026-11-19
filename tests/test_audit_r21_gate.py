# -*- coding: utf-8 -*-
"""Audit-R21 门测试: 发布可见性逐项实录(公告前一天/当天)+中国政策换锚
(OMO 零值根修/隔夜锚/七天与 LPR 单列)+政策四日期与一年窗路径(先降后升
净零可复算)+三利率窗历史不足+事后正文数值/正文月份/月频时序三阻断+锚
覆盖组级阻断+读者渲染(美国类比/样本注记/区分性观测/同窗年度分解)。

缺陷类(基线 62c973e,验收指令实录):
  P1 发布可见性整批化: R20 初版把停摆积压首发统一记 2025-11-19,与逐项
     实录相左(九月CPI 10-24/九月失业率 11-20/Q3 GDP 12-23/十月PCE
     2026-01-22);
  P2 政策面: OMO 七天序列 23 个零值=零操作日误读(量格 '0亿元' 被当利率);
     2026-11-02 换锚后无隔夜政策利率序列;决议/生效/市场观测/统计窗口
     四日期不分;美联储一年窗先降 25bp 再升 25bp 净零路径不可复算;
  P3 正文对账缺口: 历史段 ex_post 正文资产数字与校验字段可各行其是
     (只改 −6.27%→+99.00% 原样过);走位正文月份可虚构(2030-07);
     月频证据只能支持同步时排序主张不须写先后未定;只剩两个相邻交易日
     时月度/年度利率变化仍出数;
  P4 锚覆盖: 序列在场但一组仅剩最新单点(两个历史锚空)仍可正式归档。

修复位: config/release_calendar.json v1.1.0(逐项实录+保守界条目)+
china_market_collector(_pboc_rate_cell_value/_pboc_omo_parse_announcement
零值根修+CN_POLICY_OVERNIGHT)+metric_registry v2.8.7+research_map_
planner(_policy_dates 四日期+market_pair 配对+_policy_window_path+
_trio_window span_status+渲染美国类比/样本注记/区分性观测/年度窗打头)
+judgment_contract._map_checks(10/11/12+us_analog/sample_note 必填)
+agent_judgment(map_anchor_coverage_insufficient)+ia_cli(归档 belt)。

合成隔离标记: 复用 R19 门冻结面与 CLI 夹具;裁决 role=R21-
SYNTHETIC-ISOLATED-TEST。真实面核验(四日期/净零路径/201obs 零清零/
287 篇公告缓存根因)= r21-evidence 实跑档,另于 AUDIT_R21_REPORT.md。"""
import copy
import glob
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import test_audit_r19_gate as r19   # noqa: E402  复用其冻结面/CLI 夹具
import agent_judgment as aj         # noqa: E402
import research_map_planner as rmp  # noqa: E402
import release_calendar as rc       # noqa: E402
from research_contract import judgment_contract as jc   # noqa: E402
import china_market_collector as cmc   # noqa: E402

SYN_ROLE = 'R21-SYNTHETIC-ISOLATED-TEST'
TMPG = tempfile.mkdtemp(prefix='r21gate_')
RESULTS = []


def check(name, ok, detail=''):
    RESULTS.append((name, bool(ok), str(detail)[:220]))
    print(('  ✅ ' if ok else ' ❌ ') + name + (f' — {detail}' if detail else ''),
          flush=True)


def load_snap(root):
    p = os.path.join(root, 'data', 'daily',
                     'research_snapshot_20261117.json')
    return json.load(open(p, encoding='utf-8'))


def plan_at(root, cutoff):
    snap = load_snap(root)
    reg_json = json.load(open(os.path.join(
        root, 'config', 'metric_registry.json'), encoding='utf-8'))
    reg_by_id = {m['metric_id']: m for m in reg_json['metrics']}
    plan = rmp.plan_map(r19.Q_MAP, {'economies': ['US', 'CN', 'EA', 'JP']},
                        reg_by_id, cutoff)
    plan['point_values'] = rmp.point_values(plan, snap, root)
    return plan, snap


def cell_of(pv, region, dim, mid):
    return next((c for c in pv.get('cells') or []
                 if c.get('region') == region and c.get('dimension') == dim
                 and c.get('metric_id') == mid), {})


def day_pair(mid, freq, obs, day_before, day_of):
    """发布可见性逐项: 公告前一天不可见/当天可见(_visible_publish 口径)。"""
    pub, basis = rmp._visible_publish(mid, freq, obs)
    okv = pub is not None and pub > day_before and pub <= day_of
    return okv, f'{mid}@{obs}: pub={pub} basis={basis}'


def r21_judgment(rd, root, variant=None):
    """R21 判定夹具: R19 ok 版为底,按变体只动指令指定的单一字段。"""
    base_p = r19.map_judgment(rd, 'ok')
    jd = json.load(open(base_p, encoding='utf-8'))
    jd['agent_declaration']['note'] = 'R21 合成地图判决(离线门测试)'
    if variant == 'hist_fabric':
        # 反例①: 只改 2022-06 类比 ex_post.3m 正文,SPX −6.27%→+99.00%,
        # 所有校验字段原样——事后窗数值回贴的拦截位
        h0 = jd['reader_map']['history_periods'][0]
        h0['period_label'] = '2026-09→11(合成类比期)'
        h0['anchor_ym'] = '2026-09'
        h0['match_window'] = {'start_ym': '2026-08', 'end_ym': '2026-09'}
        h0['judgment_cutoff_ym'] = '2026-09'
        h0['aftermath_obs_months'] = ['2026-12', '2027-03', '2027-09']
        h0['ex_post']['3m'] = 'SPX +99.00%(合成反例: 翻转自引擎复算值)'
        h0['ex_post']['6m'] = '数据不可得(合成)'
        h0['ex_post']['12m'] = '数据不可得(合成)'
    elif variant == 'prose_2030':
        # 反例②: 只把美国正文观测月改成 2030-07,校验字段(anchor_echo)
        # 原样对——正文月份扫描的拦截位
        for r in jd['reader_map']['regions']:
            if r.get('region') == 'US':
                r['from_to'] = ('美国 12 个月前失业率 4.3(2025-08 走弱;'
                                '2030-07 误植,离线反例)')
                r['anchor_echo'] = [{'anchor': '12个月前',
                                     'metric_id': 'UNEMPLOYMENT',
                                     'value': 4.3,
                                     'observation_month': '2025-08'}]
    elif variant == 'ordering_sync':
        # 反例(月频时序): 同月变动的两指标断言先后而不写「先后未定」
        t0 = jd['reader_map']['turnings'][0]
        ym = str(t0.get('date') or '')[:7]
        t0['first_mover'] = (f"{t0.get('metric_id')} 于 {ym} 率先转身"
                             '(合成反例: 同月另一指标亦变动,先后不可分)')
        rep = json.load(open(os.path.join(rd, 'report.json'),
                             encoding='utf-8'))
        cands = ((rep.get('research_plan') or {})
                 .get('turning_candidates') or {}).get('candidates') or []
        peer_ok = any(c.get('metric_id') != t0.get('metric_id')
                      and str(c.get('to_ym')) == ym for c in cands)
        if not peer_ok:
            # 引擎候选面无同月对: 注入一枚同窗对侧候选(指标在计划面,
            # 数值与 t0 同源同窗——仅为构造同月对照,断言意图不变)
            m0 = next((c for c in cands
                       if c.get('metric_id') == t0.get('metric_id')), {})
            if m0:
                peer = dict(m0)
                peer['metric_id'] = 'UNEMPLOYMENT' if \
                    t0.get('metric_id') != 'UNEMPLOYMENT' else 'CPI'
                rep['research_plan']['turning_candidates']['candidates'] \
                    = cands + [peer]
                json.dump(rep, open(os.path.join(rd, 'report.json'), 'w',
                                    encoding='utf-8'), ensure_ascii=False)
    elif variant == 'ordering_ok':
        t0 = jd['reader_map']['turnings'][0]
        ym = str(t0.get('date') or '')[:7]
        t0['first_mover'] = (f"{t0.get('metric_id')} 与同月变动指标先后未定"
                             f'({ym} 月频证据只能支持同步,合成正例)')
    jd.update({'synthetic': True, 'role': SYN_ROLE,
               'note': 'R21 离线门测试: 冻结面+正式 CLI,非真实外部数据'})
    p = os.path.join(TMPG, 'r21jd_%s.json' % (variant or 'ok'))
    json.dump(jd, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
    return p


def verify_map(rd, judgment_path):
    rep = json.load(open(os.path.join(rd, 'report.json'), encoding='utf-8'))
    jd = json.load(open(judgment_path, encoding='utf-8'))
    v = jc.verify_judgment(jd, rep)
    mc = v.get('map_checks') or []
    contra = [m for m in mc if m.get('status') == 'CONTRADICTED']
    nv = [m for m in mc if m.get('status') == 'NOT_VERIFIED']
    return v, contra, nv


def cli(stage, rd, root, judgment=None, arc=None):
    return r19.cli_stage(stage, rd, root, arc=arc, judgment=judgment)


def test_audit_r21_gate():
    print('── 构建完整面引擎根+正式 CLI plan……')
    root = r19.build_root()
    rep, r = r19.plan_run(root, 'r21a')
    assert rep is not None, ((r.stdout or '') + (r.stderr or ''))[-500:]
    rd = os.path.dirname(sorted(glob.glob(os.path.join(
        r19.TMPG, 'plan_r21a', '*', 'report.json')))[0])

    print('═══ §A 发布可见性逐项实录(公告前一天/当天;纯函数) ═══')
    ent = rc.first_publish('CPI', '2025-09-01')
    check('§A 九月CPI 实录条目: 首发 2025-10-24(user_directive)',
          ent is not None and ent.get('first_publish') == '2025-10-24'
          and ent.get('basis') == 'user_directive', str(ent))
    okv, det = day_pair('CPI', 'monthly', '2025-09-01',
                        '2025-10-23', '2025-10-24')
    check('§A 九月CPI: 10-23 前不可见/10-24 当天可见', okv, det)
    okv, det = day_pair('UNEMPLOYMENT', 'monthly', '2025-09-01',
                        '2025-11-19', '2025-11-20')
    check('§A 九月失业率: 11-19 前不可见/11-20 当天可见', okv, det)
    okv, det = day_pair('US_REAL_GDP', 'quarterly', '2025-07-01',
                        '2025-12-22', '2025-12-23')
    check('§A Q3 GDP: 12-22 前不可见/12-23 当天可见', okv, det)
    okv, det = day_pair('CORE_PCE', 'monthly', '2025-10-01',
                        '2026-01-21', '2026-01-22')
    check('§A 十月PCE: 2026-01-21 前不可见/01-22 当天可见', okv, det)
    pub_aug, basis_aug = rmp._visible_publish('UNEMPLOYMENT', 'monthly',
                                              '2025-08-01')
    check('§A 八月失业率无实录条目→规则推定(09-05)',
          pub_aug == '2025-09-05' and '推定' in basis_aug,
          f'{pub_aug}|{basis_aug}')
    ent_c = rc.first_publish('CPI', '2025-10-01')
    check('§A 十月CPI 未逐条实录→保守界条目 2026-01-22(convention)',
          ent_c is not None and ent_c.get('first_publish') == '2026-01-22'
          and ent_c.get('basis') == 'convention', str(ent_c))

    print('═══ §B 锚级双时点(2025-11-18 与 11-19 同面;正式计划) ═══')
    plan18, _ = plan_at(root, '2026-11-18')
    plan19, _ = plan_at(root, '2026-11-19')
    for tag, plan in (('11-18', plan18), ('11-19', plan19)):
        pv = plan['point_values']
        gdp = (cell_of(pv, 'US', 'growth', 'US_REAL_GDP')
               .get('anchors') or {}).get('12个月前') or {}
        une = (cell_of(pv, 'US', 'growth', 'UNEMPLOYMENT')
               .get('anchors') or {}).get('12个月前') or {}
        cpi = (cell_of(pv, 'US', 'inflation', 'CPI')
               .get('anchors') or {}).get('12个月前') or {}
        check(f'§B {tag} 12个月前: 美国只见 Q2 GDP(obs 2025-04-01)',
              gdp.get('observation_date') == '2025-04-01',
              json.dumps(gdp, ensure_ascii=False)[:110])
        check(f'§B {tag} 12个月前: 失业率=八月 4.3(九月 11-20 才可见)',
              une.get('observation_date') == '2025-08-01'
              and une.get('value') == 4.3,
              json.dumps(une, ensure_ascii=False)[:110])
        check(f'§B {tag} 12个月前: 九月CPI 已于 10-24 发布→允许引用',
              cpi.get('observation_date') == '2025-09-01'
              and str(cpi.get('publication_date')) == '2025-10-24',
              json.dumps(cpi, ensure_ascii=False)[:110])
    pv19 = plan19['point_values']
    pub_ok = all(
        str(a.get('publication_date')) <= str(a.get('as_of'))
        for c in pv19.get('cells') or []
        for a in (c.get('anchors') or {}).values()
        if a.get('status') == 'ok')
    check('§B 11-19 全格发布纪律: ok 锚发布日≤锚日(无一例外)', pub_ok)

    print('═══ §C 中国政策换锚(解析级根修;离线) ═══')
    check('§C 利率格解析: 纯数值/带%收,量纲格与零值拒收',
          cmc._pboc_rate_cell_value('1.4') == 1.4
          and cmc._pboc_rate_cell_value('1.40%') == 1.4
          and cmc._pboc_rate_cell_value('0亿元') is None
          and cmc._pboc_rate_cell_value('3000亿元') is None
          and cmc._pboc_rate_cell_value('0') is None
          and cmc._pboc_rate_cell_value('') is None)
    zero_day = ('<tr><td>期限</td><td>投标量</td><td>中标量</td></tr>'
                '<tr><td>7天</td><td>0亿元</td><td>0亿元</td></tr>')
    rates = cmc._pboc_omo_parse_announcement(zero_day)
    check('§C 零操作日(期限|投标量|中标量 形): 七天利率=None(无成交利率'
          '留空,不产 0.0 伪影)', rates.get('7天') is None, str(rates))
    anchor_day = ('<tr><td>期限</td><td>操作利率</td><td>投标量</td>'
                  '<td>中标量</td></tr>'
                  '<tr><td>隔夜</td><td>1. 25 %</td><td>固定</td>'
                  '<td>固定</td></tr>'
                  '<tr><td>7天</td><td>1. 40 %</td><td>4000亿元</td>'
                  '<td>4000亿元</td></tr>')
    rates2 = cmc._pboc_omo_parse_announcement(anchor_day)
    check('§C 换锚后公告(隔夜行在场): 隔夜=1.25/七天=1.40(空格变体剥离)',
          rates2.get('隔夜') == 1.25 and rates2.get('7天') == 1.4, str(rates2))
    reg = json.load(open(os.path.join(ROOT, 'config',
                                      'metric_registry.json')))
    ms = {m['metric_id']: m for m in reg['metrics']}
    o = ms.get('CN_POLICY_OVERNIGHT') or {}
    check('§C 注册表 v2.8.7: CN_POLICY_OVERNIGHT 在册 active/daily/percent',
          reg.get('version') == '2.8.7' and o.get('status') == 'active'
          and o.get('frequency') == 'daily' and o.get('unit') == 'percent',
          f"{reg.get('version')}|{o.get('status')}")
    check('§C CN_OMO_7D 口径注记: 换锚单列+零值根修在档',
          '换锚' in json.dumps(
              ms.get('CN_OMO_7D') or {}, ensure_ascii=False)
          and '零' in str((ms.get('CN_OMO_7D') or {}).get('calc') or '')
          + str((ms.get('CN_OMO_7D') or {}).get('release_semantics') or ''))

    print('═══ §D 政策四日期+一年窗路径(纯函数/合成序列) ═══')
    pfu = rmp.POLICY_FACE.get('DFEDTARU') or {}
    pd_ = rmp._policy_dates(pfu, '2026-11-18', market_date='2026-11-17')
    check('§D DFEDTARU 四日期: 决议=生效=11-18/市场观测=11-17(DFF 配对)'
          '/统计窗口终点=None(日频决议序列)',
          pd_.get('decision') == '2026-11-18'
          and pd_.get('effective') == '2026-11-18'
          and pd_.get('market_observation') == '2026-11-17'
          and pd_.get('stat_window_end') is None,
          json.dumps(pd_, ensure_ascii=False)[:150])
    pff = rmp.POLICY_FACE.get('DFF') or {}
    pd2 = rmp._policy_dates(pff, '2026-11-17')
    check('§D DFF(市场均值): 市场观测=自身观测日/无决议日/统计窗=当日',
          pd2.get('market_observation') == '2026-11-17'
          and pd2.get('decision') is None
          and pd2.get('stat_window_end') == '2026-11-17',
          json.dumps(pd2, ensure_ascii=False)[:150])
    pfo = rmp.POLICY_FACE.get('CN_POLICY_OVERNIGHT') or {}
    check('§D CN_POLICY_OVERNIGHT 政策面在册(换锚新锚口径)',
          bool(pfo) and '2026-11-02' in str(pfo.get('face')))
    check('§D RELEASE_RULES 携带隔夜锚(当日可见)',
          'CN_POLICY_OVERNIGHT' in rmp.RELEASE_RULES)
    # 指令实录形态: 窗启(11-19)后降息(12-11)前有观测在窗内
    dates = ['2025-10-01', '2025-10-30', '2025-11-20', '2025-12-11',
             '2026-09-17', '2026-11-18']
    vals = [4.25, 4.0, 4.0, 3.75, 4.0, 4.0]
    wp = rmp._policy_window_path(dates, vals, '2026-11-19')
    ev = [(e['date'], e['delta_bp']) for e in (wp or {}).get('events', [])]
    check('§D 一年窗路径: 先降 25bp(12-11)再升 25bp(09-17),净变动=0',
          wp is not None and wp.get('net_bp') == 0
          and ev == [('2025-12-11', -25), ('2026-09-17', 25)]
          and wp.get('window') == ['2025-11-19', '2026-11-19'],
          f'{wp and wp.get("net_bp")}|{ev}')
    # 边界形态: 降息为窗内首观测,前值在窗启前——变动点仍须入路径
    # (按其自身决议日归属),净变动如实=+25(窗首观测即降后值)
    wp2 = rmp._policy_window_path(dates[:2] + dates[3:], vals[:2] + vals[3:],
                                  '2026-11-19')
    ev2 = [(e['date'], e['delta_bp'])
           for e in (wp2 or {}).get('events', [])]
    check('§D 窗内首观测的变动: 前值在窗启前一格仍入路径(不漏首场降息)',
          wp2 is not None
          and ev2 == [('2025-12-11', -25), ('2026-09-17', 25)]
          and wp2.get('net_bp') == 25,
          f'{wp2 and wp2.get("net_bp")}|{ev2}')

    print('═══ §E 三利率窗: 只剩两个相邻共同交易日→历史不足 ═══')
    snap2 = {'series_store': {
        mid: {'dates': ['2026-11-18', '2026-11-19'],
              'values': [4.0, 4.01], 'unit': 'percent'}
        for mid in rmp.US_RATES_TRIO}}
    trio = rmp.us_rates_trio_face(snap2, root)
    check('§E 两相邻日: status=insufficient_history+月度年度均不出数',
          trio.get('status') == 'insufficient_history'
          and 'chg_bp' not in trio and '历史不足' in str(trio.get('note')),
          json.dumps(trio, ensure_ascii=False)[:160])

    print('═══ §F 契约三阻断+历史样本前提(端到端 attach 复核) ═══')
    jd_ok = r21_judgment(rd, root, 'ok')
    rc_ok, data_ok = cli('attach', rd, root, judgment=jd_ok)
    _v0, c0, n0 = verify_map(rd, jd_ok)
    check('§F 正例: 契约过(零 CONTRADICTED)', rc_ok == 0 and not c0,
          f'rc={rc_ok} contra={[m.get("item") for m in c0]}')
    jd1 = r21_judgment(rd, root, 'hist_fabric')
    rc1, _ = cli('attach', rd, root, judgment=jd1)
    _v1, c1, _n1 = verify_map(rd, jd1)
    hit1 = [m for m in c1 if 'ex_post' in str(m.get('item'))]
    check('§F 反例①: 只改 ex_post 正文 SPX +99.00% → CONTRADICTED(引擎'
          '同窗复算不符)', bool(hit1),
          '; '.join(str(m.get('detail') or m.get('item')) for m in hit1)[:180])
    # 正向对照: 同窗真值入文→不拦(与契约同口径: 锚月末/窗月末观测)
    spx = (load_snap(root).get('series_store') or {}).get('SPX') or {}
    sd, sv = spx.get('dates') or [], spx.get('values') or []
    i0 = max(i for i in range(len(sd)) if sd[i][:7] == '2026-09')
    v0, v1 = sv[i0], sv[-1]
    eng_pct = (v1 / v0 - 1) * 100
    jd1b = json.load(open(jd1, encoding='utf-8'))
    jd1b['reader_map']['history_periods'][0]['ex_post']['3m'] = (
        f'SPX {eng_pct:+.2f}%(合成正例: 引擎同窗复算值)')
    jp = os.path.join(TMPG, 'r21jd_hist_ok.json')
    json.dump(jd1b, open(jp, 'w', encoding='utf-8'), ensure_ascii=False)
    _v1b, c1b, _ = verify_map(rd, jp)
    check('§F 正向对照: 同窗复算值入文→ex_post 零拦截',
          not [m for m in c1b if 'ex_post' in str(m.get('item'))])
    jd2 = r21_judgment(rd, root, 'prose_2030')
    rc2, _ = cli('attach', rd, root, judgment=jd2)
    _v2, c2, _ = verify_map(rd, jd2)
    hit2 = [m for m in c2 if 'prose_month' in str(m.get('item'))]
    check('§F 反例②: 美国正文观测月改 2030-07(校验字段原样)→CONTRADICTED',
          bool(hit2), '; '.join(
              str(m.get('detail') or m.get('item')) for m in hit2)[:180])
    jd3 = r21_judgment(rd, root, 'ordering_sync')
    rc3, _ = cli('attach', rd, root, judgment=jd3)
    _v3, c3, _ = verify_map(rd, jd3)
    hit3 = [m for m in c3 if 'ordering_resolution' in str(m.get('item'))]
    check('§F 月频同步时序: 同月两指标排序主张未写先后未定→CONTRADICTED',
          bool(hit3), '; '.join(
              str(m.get('detail') or m.get('item')) for m in hit3)[:180])
    jd4 = r21_judgment(rd, root, 'ordering_ok')
    _v4, c4, _ = verify_map(rd, jd4)
    check('§F 正向对照: 写明先后未定→零时序拦截',
          not [m for m in c4 if 'ordering_resolution' in str(m.get('item'))])
    jd5 = json.load(open(jd_ok, encoding='utf-8'))
    h = jd5['reader_map']['history_periods'][0]
    h.pop('sample_note', None)
    h.pop('us_analog', None)
    jp5 = os.path.join(TMPG, 'r21jd_nosample.json')
    json.dump(jd5, open(jp5, 'w', encoding='utf-8'), ensure_ascii=False)
    _v5, _c5, n5 = verify_map(rd, jp5)
    hit5 = {str(m.get('item')) for m in n5
            if 'sample_note' in str(m.get('item'))
            or 'us_analog' in str(m.get('item'))}
    check('§F 历史样本前提: 缺 sample_note/us_analog → NOT_VERIFIED',
          len(hit5) >= 2, str(sorted(hit5))[:180])

    print('═══ §G 锚覆盖组级阻断(blocked_class_of 单元) ═══')
    check('§G map_anchor_coverage_insufficient 入阻断类目',
          'map_anchor_coverage_insufficient' in aj.BLOCKING_BLOCKED_CLASSES)

    def _rep(cells):
        return {'layers': {'L1_事实层': {'rows': [{'metric_id': 'CPI'}]}},
                'run': {'data_requirements': {'items': []}},
                'run_ok': True,
                'agent_judgment': {'reader_map_faces': {'complete': True}},
                'research_plan': {
                    'map_question': True,
                    'regions': {'JP': {'dimensions': {'growth': [
                        {'metric_id': 'JP_REAL_GDP_YOY'}]}}},
                    'point_values': {'cells': cells}}}

    def _anchor(status, cal=False):
        a = {'status': status, 'as_of': '2025-11-19'}
        if cal:
            a['calendar_blocked_observation'] = '2025-10-01'
        return a

    sparse = [{'region': 'JP', 'dimension': 'growth',
               'metric_id': 'JP_REAL_GDP_YOY',
               'anchors': {'最新一期': _anchor('ok'),
                           '12个月前': _anchor('no_x'),
                           '3个月前': _anchor('no_x')}}]
    check('§G 仅剩最新单点(两历史锚空无实据)→锚覆盖不足',
          aj.blocked_class_of(_rep(sparse))
          == 'map_anchor_coverage_insufficient',
          str(aj.blocked_class_of(_rep(sparse))))
    sparse_cal = copy.deepcopy(sparse)
    for a in sparse_cal[0]['anchors'].values():
        if a.get('status') != 'ok':
            a['calendar_blocked_observation'] = '2025-10-01'
    check('§G 空锚带日历实录依据(停摆延误)→放行(诚实缺口)',
          aj.blocked_class_of(_rep(sparse_cal)) is None,
          str(aj.blocked_class_of(_rep(sparse_cal))))
    zero = [{'region': 'JP', 'dimension': 'growth',
             'metric_id': 'JP_REAL_GDP_YOY',
             'anchors': {k: _anchor('no_x') for k in
                         ('最新一期', '12个月前', '3个月前')}}]
    check('§G 整组零 ok → 仍走 map_core_dimension_missing(R20 类目不变)',
          aj.blocked_class_of(_rep(zero)) == 'map_core_dimension_missing')

    print('═══ §H 渲染: 读者面新节(正式 report 段产物) ═══')
    jd_h = json.load(open(jd_ok, encoding='utf-8'))
    jd_h['reader_map']['history_periods'][0]['us_analog'] = True
    jd_h['reader_map']['history_periods'][0]['sample_note'] = \
        '样本注记: 合成(与当前窗重叠须声明,离线)'
    jdh_p = os.path.join(TMPG, 'r21jd_render.json')
    json.dump(jd_h, open(jdh_p, 'w', encoding='utf-8'), ensure_ascii=False)
    cli('attach', rd, root, judgment=jdh_p)
    # 独立语义席裁决(R18/R19 门同法——report 的席位门,合成隔离)
    aj.record_semantic_verdict(root, rd, 'UPHELD', SYN_ROLE,
                               notes='R21 门渲染席位(合成隔离)')
    rc_r, data_r = cli('report', rd, root)
    mp = open(os.path.join(rd, 'MAP_REPORT.md'), encoding='utf-8').read()
    check('§H 报告段 rc=0', rc_r == 0,
          json.dumps(data_r, ensure_ascii=False)[:200])
    check('§H 政策四分面表含市场观测日列', '市场观测日' in mp)
    check('§H 政策一年窗路径行(净变动 bp)在场', '政策一年窗路径' in mp
          and '净变动' in mp)
    check('§H 历史段: 美国类比标签+样本注记+当时同步性与随后结果分列',
          '美国类比' in mp and '样本注记' in mp
          and '当时同步性' in mp and '随后结果(事后实际' in mp)
    check('§H 传导链区分指标附引擎当前面观测(或如实缺席)',
          ('引擎当前面' in mp) or ('如实缺席' in mp))
    check('§H 三利率分解: 年度窗(年度判断同窗)打头+月度另列',
          '年度窗(年度判断同窗)' in mp and '月度窗(另列)' in mp)

    n_pass = sum(1 for _n, okk, _d in RESULTS if okk)
    n_fail = len(RESULTS) - n_pass
    print(f'\nAudit-R21 判定: {n_pass} PASS / {n_fail} FAIL')
    assert n_fail == 0, f'{n_fail} 项未过: ' + '; '.join(
        n for n, okk, _d in RESULTS if not okk)


if __name__ == '__main__':
    test_audit_r21_gate()
    sys.exit(0)   # R21: 直跑口径 0=全过(conftest SuiteFile 自执行静态查)
