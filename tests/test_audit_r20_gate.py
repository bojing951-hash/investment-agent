# -*- coding: utf-8 -*-
"""Audit-R20 门测试: 四地地图补齐+发布日历实录(历史可见性)+读者正文
回贴对账+核心维度草稿门+四反例端到端拦截。

缺陷类(基线 abba4d1 复现,复现档 docs/autonomous-rd/r19-evidence/):
  P1 四地缺组: EA/JP 增长维与 JP 全国 CPI 注册/序列缺席,CN 通胀政策
     挂缺口行——12 组(地区×维度)不满仍以「全球地图」名义交付;
  P2 历史可见性: 零发布日历实录——2025 政府停摆(9-10 月 BLS/BEA 数据
     2025-11-19 才补发)被推定规则「月末+5 天」洗成锚前可见,2025-11-18
     当日读者被喂 9 月失业率/Q3 GDP(审计给定事实: 只能看到 Q2 GDP 与
     8 月失业率 4.3%);FRED 最新修订值与当时首发值无区分(事后回顾未标);
     政策只给单一利率数字,决议日/生效日/统计窗口不分;
  P3 读者正文: 数字与引擎面零对账——编造回报(−6.27%→+99.00%)、正文
     月份错误、提前引用未发布数据均可入正文;利率分解无共同交易日复算;
     VIX 月涨幅与计算窗口读者不可见;情景触发/失效方向不分列;零段类比
     无检索范围注记;
  P4 核心维度缺失可归档: 组级缺口不阻断正式归档(草稿混入正式库)。

修复位: metric_registry v2.8.6+config/release_calendar.json(release_
calendar.py)+research_map_planner(_visible_publish 日历优先/三日期
POLICY_FACE/事后回顾/us_rates_trio_face/asset_move_rows/render 四新节)
+judgment_contract._map_checks(6/7/8 三类回贴)+agent_judgment
(map_core_dimension_missing)+ia_cli(_r1_archive_core 组级 belt)。

合成隔离标记: 复用 R19 门冻结面(cn-task-b)+_complete_r20_face 四地
注入+global SPX/VIX 注入(全部 synthetic:true);裁决 role=R20-
SYNTHETIC-ISOLATED-TEST。真实面核验(38.07% VIX/共同交易日分解等)
= r20-evidence 实跑档,另于 AUDIT_R20_REPORT.md 在档。"""
import copy
import glob
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import test_audit_r19_gate as r19   # noqa: E402  复用其冻结面/CLI 夹具
import agent_judgment as aj         # noqa: E402
import research_map_planner as rmp  # noqa: E402
import snapshot_builder as sb       # noqa: E402
import workbench_data as wd         # noqa: E402
import release_calendar as rc       # noqa: E402

SYN_ROLE = 'R20-SYNTHETIC-ISOLATED-TEST'
TMPG = tempfile.mkdtemp(prefix='r20gate_')
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
    """进程内共享计划+rmp 三面(与 orchestrator map-plan 同装配)。"""
    snap = load_snap(root)
    reg = wd.load_registry(root)
    plan = rmp.plan_map(r19.Q_MAP, {'economies': ['US', 'CN', 'EA', 'JP']},
                        reg.get('by_id') or {}, cutoff)
    plan['point_values'] = rmp.point_values(plan, snap, root)
    return plan, snap


def r20_judgment(rd, root, variant=None):
    """R20 判定夹具: R19 ok 版为底,按变体注入回贴面/篡改正文。"""
    base_p = r19.map_judgment(rd, 'ok')
    jd = json.load(open(base_p, encoding='utf-8'))
    jd['agent_declaration']['note'] = 'R20 合成地图判决(离线门测试)'
    rep = json.load(open(os.path.join(rd, 'report.json'), encoding='utf-8'))
    rp = rep.get('research_plan') or {}
    if variant == 'fabric_return':
        # 反例A: 正文宣称标普月回报被翻转(−6.27% 实况被写成 +99.00%),
        # 回贴面如实带上 +99.00——引擎同窗复算对账必杀
        jd['reader_map']['headline_conclusion'] = (
            '合成总判断: 标普500近一个月回报 +99.00%(叙述翻转自 −6.27%,'
            '离线反例)')
        spx = (load_snap(root).get('series_store') or {}).get('SPX') or {}
        eng = rmp.asset_move_rows({'SPX': spx}, str(rp.get('cutoff') or ''),
                                  months=1)
        row = next((r for r in eng.get('rows') or []
                    if r.get('metric_id') == 'SPX'), {}) or {}
        jd['reader_map']['asset_returns_echo'] = [{
            'metric_id': 'SPX', 'window_months': 1, 'chg_pct': 99.00,
            'window': {'from': (row.get('window') or {}).get('from'),
                       'to': (row.get('window') or {}).get('to')}}]
    elif variant == 'wrong_month':
        # 反例B: 正文月份错误——引用 2025-09 失业率 4.4,引擎锚前(停摆
        # 日历)只可见 2025-08 4.3
        for r in jd['reader_map']['regions']:
            if r.get('region') == 'US':
                r['from_to'] = ('美国 12 个月前失业率 4.4(2025-09 走弱,'
                                '离线反例)')
                r['anchor_echo'] = [{'anchor': '12个月前',
                                     'metric_id': 'UNEMPLOYMENT',
                                     'value': 4.4,
                                     'observation_month': '2025-09'}]
    elif variant == 'prenatal':
        # 反例C: 提前引用未发布——东京 CPI 序列面缺席(无 ok 锚格),
        # 回贴引用其 12 个月前值=虚构不在引擎点值面的锚
        for r in jd['reader_map']['regions']:
            if r.get('region') == 'JP':
                r['from_to'] = '日本 12 个月前东京CPI 2.1(离线反例)'
                r['anchor_echo'] = [{'anchor': '12个月前',
                                     'metric_id': 'JP_CPI_TOKYO_YOY',
                                     'value': 2.1,
                                     'observation_month': '2025-09'}]
    jd.update({'synthetic': True, 'role': SYN_ROLE,
               'note': 'R20 离线门测试: 冻结面+正式 CLI,非真实外部数据'})
    p = os.path.join(TMPG, 'r20jd_%s.json' % (variant or 'ok'))
    json.dump(jd, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
    return p


_ROOT = {}


def build_sparse_root():
    """负例D 根: 完整面去掉 ea_/jp_/japan_ 注入——EA/JP 组缺数(草稿面)。"""
    if 'sparse' in _ROOT:
        return _ROOT['sparse']
    d = tempfile.mkdtemp(prefix='r20sparse_')
    for f in ('ia_cli.py', 'env_config.py'):
        shutil.copy(os.path.join(ROOT, f), os.path.join(d, f))
    shutil.copytree(os.path.join(ROOT, 'scripts'), os.path.join(d, 'scripts'))
    shutil.copytree(os.path.join(ROOT, 'config'), os.path.join(d, 'config'))
    dd = os.path.join(d, 'data', 'daily')
    os.makedirs(dd)
    src = os.path.join(_ROOT['full'], 'data', 'daily')
    keep = ('macro_20261117.json', 'china_20261117.json',
            'global_20261117.json')
    for f in keep:
        shutil.copy(os.path.join(src, f), os.path.join(dd, f))
    sb.build_snapshot(target_ymd='20261117', data_dir=dd, out_dir=dd,
                      as_of='2026-11-17T08:36:00+08:00', trusted_root=d)
    _ROOT['sparse'] = d
    return d


def cli(stage, rd, root, judgment=None, arc=None):
    return r19.cli_stage(stage, rd, root, arc=arc, judgment=judgment)


def find_item(mc, frag):
    return next((m for m in mc if frag in str(m.get('item'))), None)


def test_audit_r20_gate():
    print('── 构建完整面引擎根+正式 CLI plan……')
    root = r19.build_root()
    _ROOT['full'] = root
    rep, r = r19.plan_run(root, 'r20a')
    assert rep is not None, ((r.stdout or '') + (r.stderr or ''))[-500:]
    rd = os.path.dirname(sorted(glob.glob(os.path.join(
        r19.TMPG, 'plan_r20a', '*', 'report.json')))[0])
    rp = rep.get('research_plan') or {}
    pv = rp.get('point_values') or {}

    print('═══ §A 注册面+发布日历实录(离线纯函数) ═══')
    reg = json.load(open(os.path.join(ROOT, 'config',
                                      'metric_registry.json')))
    ms = {m['metric_id']: m for m in reg['metrics']}
    new_ids = ['JP_CPI_YOY', 'JP_CPI_TOKYO_YOY', 'EA_REAL_GDP_YOY',
               'JP_REAL_GDP_YOY', 'CN_CPI_YOY', 'CN_OMO_7D', 'CN_LPR_1Y']
    check('§A P1 修复: 注册表四地新指标在列(全国CPI/GDP同比/OMO/LPR)',
          all(i in ms for i in new_ids),
          str([i for i in new_ids if i not in ms]))
    check('§A 事后回顾声明: FRED 最新修订族 release_semantics 含标记',
          all('latest_vintage' in (ms[i].get('release_semantics') or '')
              for i in ('EA_REAL_GDP_YOY', 'JP_REAL_GDP_YOY', 'US_REAL_GDP')),
          str([(i, ms.get(i, {}).get('release_semantics')) for i in
               ('EA_REAL_GDP_YOY', 'JP_REAL_GDP_YOY')]))
    check('§A DFEDTARU/L 历史通道=macro_collector(区间上下限序列可溯)',
          (ms.get('DFEDTARU', {}).get('history_source')
           == ms.get('DFEDTARL', {}).get('history_source')
           == 'macro_collector'))
    ent = rc.first_publish('US_REAL_GDP', '2025-07-01')
    # R21: 验收指令实录把 Q3 GDP 首发由整批 2025-11-19 改精确日 2025-12-23
    # (日历 v1.1.0);断言意图不变(日历实录条目优先),期望值随实录修订。
    check('§A 日历实录: 停摆期 Q3 GDP 首发日=2025-12-23(user_directive)',
          ent is not None and ent.get('first_publish') == '2025-12-23'
          and ent.get('basis') == 'user_directive', str(ent))
    ent2 = rc.first_publish('UNEMPLOYMENT', '2025-09-01')
    ent3 = rc.first_publish('UNEMPLOYMENT', '2025-08-01')
    # R21: 9 月失业率首发由整批 11-19 改实录精确日 2025-11-20。
    check('§A 日历实录: 9 月失业率首发 2025-11-20;8 月无条目走规则',
          ent2 is not None and ent2.get('first_publish') == '2025-11-20'
          and ent3 is None, f'{ent2}/{ent3}')
    pub, basis = rmp._visible_publish('US_REAL_GDP', 'quarterly', '2025-07-01')
    # R21: Q3 可见日随日历 v1.1.0 精确化改 2025-12-23。
    check('§A _visible_publish 日历优先: Q3→12-23+basis 带条目号',
          pub == '2025-12-23' and basis.startswith('calendar:RC-'), f'{pub}|{basis}')
    pub2, basis2 = rmp._visible_publish('UNEMPLOYMENT', 'monthly', '2025-08-01')
    check('§A _visible_publish 规则兜底: 8 月→09-05+推定规则文本随格',
          pub2 == '2025-09-05' and '推定' in basis2, f'{pub2}|{basis2}')

    print('═══ §B 计划面: 12组×3锚+回归锚+格五要素(P1/P2) ═══')
    plan2, snap2 = plan_at(root, '2026-11-18')
    pv2 = plan2['point_values']
    cells2 = {(c['region'], c['dimension'], c['metric_id']): c
              for c in pv2.get('cells') or []}
    gdp = cells2.get(('US', 'growth', 'US_REAL_GDP')) or {}
    a12 = (gdp.get('anchors') or {}).get('12个月前') or {}
    check('§B 回归锚①: 截止 2026-11-18 的 12个月前(2025-11-18)美国 GDP'
          ' 只可见 Q2(2025-04-01)——Q3 停摆未发布',
          a12.get('observation_date') == '2025-04-01',
          json.dumps(a12, ensure_ascii=False)[:130])
    une = cells2.get(('US', 'growth', 'UNEMPLOYMENT')) or {}
    u12 = (une.get('anchors') or {}).get('12个月前') or {}
    check('§B 回归锚②: 12个月前失业率=8月 4.3(9月停摆首发 11-19 被排除)',
          u12.get('observation_date') == '2025-08-01'
          and u12.get('value') == 4.3
          and str(u12.get('publication_date')) <= '2025-11-18',
          json.dumps(u12, ensure_ascii=False)[:130])
    ok_m = {}
    for c in pv2.get('cells') or []:
        for lbl, a in (c.get('anchors') or {}).items():
            if a.get('status') == 'ok':
                ok_m.setdefault((c['region'], c['dimension']), set()).add(lbl)
    planned = {(eco, dim) for eco in ('US', 'CN', 'EA', 'JP')
               for dim in ('growth', 'inflation', 'policy')}
    labels = {'12个月前', '3个月前', '最新一期'}
    full = {k for k, v in ok_m.items() if v == labels}
    check('§B 12组×3锚全 ok(36 时点格无一缺组)',
          planned <= full and len(full) >= 12,
          str(sorted(planned - full)) + '|' + str(sorted(full)))
    bad_elem = []
    for c in pv2.get('cells') or []:
        if not c.get('unit'):
            bad_elem.append((c['metric_id'], 'unit'))
        for lbl, a in (c.get('anchors') or {}).items():
            if a.get('status') == 'ok' and (
                    a.get('value') is None or not a.get('observation_date')
                    or not a.get('publication_date')
                    or not a.get('publication_basis')):
                bad_elem.append((c['metric_id'], lbl))
    check('§B 每格五要素齐: 数值/单位/观察期/实际发布日期(+依据)/来源',
          not bad_elem and all(c.get('source') for c in pv2.get('cells') or []),
          str(bad_elem[:4]))
    dfed = cells2.get(('US', 'policy', 'DFEDTARU')) or {}
    pdt = ((dfed.get('anchors') or {}).get('最新一期') or {}).get('policy_dates') or {}
    jpr = cells2.get(('JP', 'policy', 'JP_POLICY_RATE')) or {}
    jface = (jpr.get('anchors') or {}).get('最新一期') or {}
    # Audit-R22 任务2 语义修订: 决议/生效日锚**值变更日**(合成面 DFEDTARU
    # 全窗无变更→决议/生效不可推=如实缺席,不虚构);R20 旧口径「决议=生效
    # =观测日」已被数据面证伪(2026-09 决议 09-16→生效 09-17),真实面
    # 断言在 r22 门 §C。
    check('§B 政策三日期: DFEDTARU 合成面无值变更→决议/生效不可推'
          '(如实缺席不虚构),统计窗口如实缺席',
          pdt.get('decision') is None and pdt.get('effective') is None
          and '不可推' in str(pdt.get('decision_note'))
          and pdt.get('stat_window_end') is None
          and (dfed.get('policy_face') or {}).get('face', '').find('目标') >= 0,
          json.dumps(pdt, ensure_ascii=False)[:160])
    check('§B 口径分列: JP 隔夜市场均值无决议日+统计窗口月末(区别于目标口径)',
          '市场' in str((jpr.get('policy_face') or {}).get('face'))
          and not (jface.get('policy_dates') or {}).get('decision')
          and (jface.get('policy_dates') or {}).get('stat_window_end'),
          str(jface.get('policy_dates')))
    vind = ((cells2.get(('EA', 'growth', 'EA_REAL_GDP_YOY')) or {})
            .get('vintage_semantics'))
    check('§B 事后回顾: 注册声明最新修订族的行带标记,采集时点族无',
          '事后回顾' in str(vind)
          and '事后回顾' in str((cells2.get(
              ('JP', 'inflation', 'JP_CPI_YOY')) or {})
              .get('vintage_semantics'))
          and '事后回顾' not in str((cells2.get(
              ('CN', 'inflation', 'CN_CPI_YOY')) or {})
              .get('vintage_semantics')),
          str(vind))
    s, _e = wd.metric_series('CN_PMI_MFG', root=root)
    m_map = dict(zip(s['dates'], s['values']))
    check('§B CN PMI 事实: 2026-05=50.0 与 2026-09=50.1(引擎序列可复算)',
          m_map.get('2026-05-01') == 50.0 and m_map.get('2026-09-01') == 50.1,
          f"05={m_map.get('2026-05-01')} 09={m_map.get('2026-09-01')}")

    print('═══ §B2 引擎三面: 三利率共同交易日+关键资产月窗(P3) ═══')
    trio = rp.get('us_rates_trio') or {}
    chg = trio.get('chg_bp') or {}
    res = trio.get('identity_residual_bp')
    check('§B2 三利率分解面 ok: 共同交易日窗+三分量+恒等式残差<0.5bp',
          trio.get('status') == 'ok' and (trio.get('window') or {}).get('from')
          and set(chg) >= {'UST_10Y', 'TIPS_10Y', 'BEI_10Y'}
          and res is not None and abs(res) < 0.5,
          json.dumps(trio, ensure_ascii=False)[:170])
    am = rp.get('asset_moves') or {}
    rows = am.get('rows') or []
    vix = next((x for x in rows if x.get('metric_id') == 'VIX'), {})
    vix_ser = (snap2.get('series_store') or {}).get('VIX') or {}
    re_vix = rmp.asset_move_rows({'VIX': vix_ser},
                                 str(rp.get('cutoff')), months=1)
    re_row = next((x for x in re_vix.get('rows') or []
                   if x.get('metric_id') == 'VIX'), {})
    check('§B2 VIX 月涨幅带计算窗口,与纯函数同窗复算逐位一致',
          vix.get('chg_pct') is not None
          and (vix.get('window') or {}).get('from')
          == (re_row.get('window') or {}).get('from')
          and abs(float(vix.get('chg_pct'))
                  - float(re_row.get('chg_pct'))) < 1e-9,
          f"{vix.get('chg_pct')}% {vix.get('window')} vs {re_row.get('chg_pct')}%")

    print('═══ §C 判定契约三类回贴反例(attach 正式 CLI) ═══')
    for variant, frag, note in (
            ('fabric_return', 'asset_returns_echo', '编造回报'),
            ('wrong_month', 'anchor_echo', '正文月份错误'),
            ('prenatal', 'anchor_echo', '提前引用未发布')):
        jd_p = r20_judgment(rd, root, variant)
        rc_, data = cli('attach', rd, root, judgment=jd_p)
        rep2 = json.load(open(os.path.join(rd, 'report.json'),
                              encoding='utf-8'))
        cv = ((rep2.get('agent_judgment') or {})
              .get('contract_verification')) or {}
        hits = [m for m in cv.get('map_checks') or []
                if frag in str(m.get('item'))
                and m.get('status') == 'CONTRADICTED']
        check(f'§C 反例({note}) → 回贴对账 CONTRADICTED+attach 拒绝',
              data.get('attached') is not True and bool(hits),
              '; '.join(h.get('note', '')[:80] for h in hits[:2]))
    # 还原 ok 判定(后续 §E 用)
    cli('attach', rd, root, judgment=r20_judgment(rd, root))

    print('═══ §D 渲染面: 四新节+日历阻断格+零段类比注记(P2/P3) ═══')
    rep3 = json.load(open(os.path.join(rd, 'report.json'), encoding='utf-8'))
    jd_doc = json.load(open(r20_judgment(rd, root), encoding='utf-8'))
    md = rmp.render_map_report(rep3, jd_doc)
    check('§D 政策口径四分面节(目标/报价/市场均值+三日期列)',
          '政策口径' in md and '决议日' in md and '统计窗口' in md)
    check('§D 美债三利率分解节(共同交易日复算+恒等式)',
          '三利率' in md and '共同交易日' in md
          and ('=' in md and 'bp' in md))
    check('§D 关键资产月度变化节(含计算窗口,VIX 在列)',
          '关键资产' in md and 'VIX' in md and '计算窗口' in md)
    check('§D 情景节分列触发与失效方向(SCN-A/SCN-B 各自可读)',
          '情景' in md and '触发' in md and '失效' in md
          and 'SCN-A' in md and 'SCN-B' in md)
    jd0 = copy.deepcopy(jd_doc)
    jd0['reader_map']['history_periods'] = []
    md0 = rmp.render_map_report(rep3, jd0)
    check('§D 零段类比: 检索范围与原因注记在读者面',
          '历史上结构最像的时期' in md0 and '零段类比' in md0
          and '检索范围' in md0)
    repc = copy.deepcopy(rep3)
    pv_copy = repc['research_plan']['point_values']
    for c in pv_copy.get('cells') or []:
        if c['metric_id'] == 'UNEMPLOYMENT':
            c['anchors']['12个月前'] = {
                'status': 'no_published_observation_on_or_before_anchor',
                'as_of': '2025-11-18',
                'calendar_blocked_observation': '2025-09-01',
                'calendar_first_publish': '2025-11-19',
                'note': '锚日前无已发布观测'}
    mdc = rmp.render_map_report(repc, jd_doc)
    check('§D 停摆阻断格如实渲染(最早可见日期对读者可见)',
          '停摆延误' in mdc and '2025-11-19' in mdc)

    print('═══ §E 端到端: 正例交付归档+负例D 组级缺数=草稿不归档(P4) ═══')
    # R29 任务4: 席位终裁绑定冻结输入摘要(席位仿体随新合同)
    _fi_p = (json.load(open(os.path.join(rd, 'report.json'),
                            encoding='utf-8')).get('run') or {}
             ).get('frozen_inputs')
    aj.record_semantic_verdict(root, rd, 'UPHELD', SYN_ROLE,
                               notes='R20 门正例席位(合成隔离)',
                               extra=({'frozen_inputs_sha256':
                                       aj.frozen_inputs_digest(_fi_p)}
                                      if _fi_p else None))
    rc_r, data_r = cli('report', rd, root)
    arc = os.path.join(TMPG, 'arc_pos')
    rc_a, data_a = cli('archive', rd, root, arc=arc)
    n_arc = 1 if os.path.isfile(os.path.join(arc, 'report.json')) else 0
    check('§E 正例: report 可交付+正式归档 1 份(完整面)',
          rc_r == 0 and data_r.get('deliverable') is True
          and n_arc == 1, f"rc={rc_r} dlv={data_r.get('deliverable')} n={n_arc}")
    sparse = build_sparse_root()
    rep_s, r_s = r19.plan_run(sparse, 'r20sparse')
    assert rep_s is not None, ((r_s.stdout or '') + (r_s.stderr or ''))[-500:]
    rd_s = os.path.dirname(sorted(glob.glob(os.path.join(
        r19.TMPG, 'plan_r20sparse', '*', 'report.json')))[0])
    cli('attach', rd_s, sparse, judgment=r20_judgment(rd_s, sparse))
    aj.record_semantic_verdict(sparse, rd_s, 'UPHELD', SYN_ROLE,
                               notes='R20 门负例D席位(合成隔离;组级缺口'
                               '与席位无关,照样拦)',
                               extra=({'frozen_inputs_sha256':
                                       aj.frozen_inputs_digest(
                                           (json.load(open(
                                               os.path.join(
                                                   rd_s, 'report.json'),
                                               encoding='utf-8'))
                                            .get('run') or {})
                                           .get('frozen_inputs'))}
                                      if (json.load(open(os.path.join(
                                              rd_s, 'report.json'),
                                              encoding='utf-8'))
                                          .get('run') or {}
                                          ).get('frozen_inputs') else None))
    rc_rs, data_rs = cli('report', rd_s, sparse)
    bc = aj.blocked_class_of(json.load(open(os.path.join(rd_s, 'report.json'),
                                            encoding='utf-8')))
    arc_s = os.path.join(TMPG, 'arc_neg')
    rc_as, data_as = cli('archive', rd_s, sparse, arc=arc_s)
    n_as = len(glob.glob(os.path.join(arc_s, '*',)))
    check('§E 负例D: EA/JP 组缺数 → 分类=核心维度缺失+不交付',
          bc == 'map_core_dimension_missing'
          and data_rs.get('deliverable') is not True, f'bc={bc}')
    check('§E 负例D: 正式归档拒绝(草稿不混入正式库)',
          n_as == 0 and (data_as.get('blocked')
                         == 'map_core_dimension_missing'
                         or rc_as != 0),
          f"rc={rc_as} blocked={data_as.get('blocked')} n={n_as}")
    # 进程内组级 belt 直证: 完整面报告剥掉 EA/JP 格 → 新分类生效
    rep4 = json.load(open(os.path.join(rd, 'report.json'), encoding='utf-8'))
    rep4['research_plan']['point_values']['cells'] = [
        c for c in pv.get('cells') or [] if c.get('region') in ('US', 'CN')]
    check('§E 组级分类器: 剥 EA/JP 格 → map_core_dimension_missing',
          aj.blocked_class_of(rep4) == 'map_core_dimension_missing',
          str(aj.blocked_class_of(rep4)))

    n_fail = sum(1 for _, ok, _d in RESULTS if not ok)
    print(f'\nAudit-R20 判定: {len(RESULTS) - n_fail} PASS / {n_fail} FAIL')
    assert n_fail == 0, f'{n_fail} 项未过: ' + '; '.join(
        n for n, ok, _d in RESULTS if not ok)


if __name__ == '__main__':
    test_audit_r20_gate()
    sys.exit(0)   # R20: 直跑口径 0=全过(conftest SuiteFile 自执行静态查)
