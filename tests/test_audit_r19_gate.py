# -*- coding: utf-8 -*-
"""Audit-R19 门测试: 同比基期纪律+发布纪律+三维转折候选+历史类比结构面
+四阻断器+传导达资产+普通读者版量化显示。

缺陷类(基线 2178b2d 复现,复现档 ${TMPDIR}r19_repro/EVIDENCE.md):
  D1 月度同比缺基期→13 个月变化被写成同比(_derive_yoy 取最近前值代基);
  D2 提前引用未发布数据(_obs_at 只按观测日,零发布日概念——8月18日引用
     10月29日才公布的 Q3 GDP);
  D3 转折候选池硬编码 policy+inflation→增长转折零候选;
  D4 历史类比无 anchor_ym/match_window/judgment_cutoff/事后窗机器核验;
  D5 四阻断器(错用同比基期/提前引用未发布/同一转折重复三次/历史结果
     落在匹配期内)在判定契约缺席;
  D6 CN PPI 误归增长维;JP 市场利率与央行目标未分别列示;
  D7 传导图无「连到资产」要求;
  D8 普通读者版(report.md/FULL_REPORT)不显示后台已有的 S6 历史比较与
     S5 量化说明(R24 VIX 样本佐证)。

修复位: research_map_planner(RELEASE_RULES/_publish_date/严格同基期
_derive_yoy/发布过滤 point_values/三维候选/ex_post_windows/ASSET_UNIVERSE
/PPI 归价格维/JP 目标行)+ judgment_contract._map_checks(四阻断器+维度
覆盖+资产达+历史结构面)+ research_orchestrator._render_quant_sections
(读者版确定性量化节;ia_cli FULL_REPORT 同节)。

合成隔离标记: 本文件全部裁决/夹具 role=R19-SYNTHETIC-ISOLATED-TEST,
synthetic:true 顶层双写(离线测试,冻结面=仓内 cn-task-b 宏观档;VIX 形
样本=R24 真档 S6 信封形状构造,数值取自 R32 语义审查在档事实)。"""
import copy
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import agent_judgment as aj           # noqa: E402
import research_map_planner as rmp    # noqa: E402
import research_orchestrator as ro    # noqa: E402
import snapshot_builder as sb         # noqa: E402
from research_contract import judgment_contract as jc  # noqa: E402

SYN_ROLE = 'R19-SYNTHETIC-ISOLATED-TEST'
SYN_MARK = {'synthetic': True,
            'note': 'R19 离线门测试: 冻结面+正式 CLI,非真实外部数据'}

RESULTS = []


def check(name, ok, detail=''):
    RESULTS.append((name, bool(ok), str(detail)[:220]))
    print(('  ✅ ' if ok else ' ❌ ') + name + (f' — {detail}' if detail else ''),
          flush=True)


# ═══ 冻结面: 仓内 cn-task-b 宏观档(同 R18 门;US 三维序列+CN_PMI) ═══
_REAL = json.load(open(os.path.join(
    ROOT, 'docs/autonomous-rd/cn-task-b-20261117T083954Z/macro_input/',
    'macro_20261117.json')))
TMPG = tempfile.mkdtemp(prefix='r19gate_')
ARC = os.path.join(TMPG, 'research_archive')

Q_MAP = ('给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在12个月前、'
         '3个月前和最新一期，分别处于什么增长、通胀和货币政策环境？过去一年'
         '最重要的三个转折是什么，谁先变，谁跟进或背离？证据最充分的传导机制'
         '是什么，还有什么解释，哪个指标能区分它们？历史上哪些时期结构最像，'
         '当时其他经济体是否同步，随后3、6、12个月经济和主要资产实际怎么走？')


def _complete_r20_face(dd):
    """R20 四地补齐注入: cn-task-b 冻结面只有 US+CN_PMI——R20 任务1 起
    12 组(地区×维度)每组至少一格 ok 才可正式交付(agent_judgment
    map_core_dimension_missing),正例须在补齐面上跑。注入走各通道顶层
    series 节(与真实采集档同构,merge_series_sections 权属门校验
    source=对应采集器),数值=合成(离线标记),观测/发布日满足发布纪律
    (JP_CPI +20 天→9 月锚前可见等)。"""
    inj = {
        'china_20261117.json': {
            'CN_CPI_YOY': (['2025-10-01', '2026-07-01', '2026-10-01'],
                           [0.4, 0.5, 0.7]),
            'CN_OMO_7D': (['2025-11-14', '2026-08-14', '2026-11-13'],
                          [1.4, 1.4, 1.4])},
        'ea_20261117.json': {
            'EA_HICP_YOY': (['2025-10-01', '2026-07-01', '2026-10-01'],
                            [2.2, 2.1, 2.0]),
            'EA_REAL_GDP_YOY': (['2025-07-01', '2026-04-01', '2026-07-01'],
                                [1.2, 1.0, 1.1]),
            'ECB_MRO': (['2025-11-14', '2026-08-14', '2026-11-13'],
                        [3.15, 2.65, 2.65])},
        'jp_20261117.json': {
            # JP_CPI 月频+20 天: 10 月观测 11-20 才可见→锚前最近=9 月
            'JP_CPI_YOY': (['2025-09-01', '2026-06-01', '2026-09-01'],
                           [2.6, 2.8, 2.9]),
            'JP_REAL_GDP_YOY': (['2025-07-01', '2026-04-01', '2026-07-01'],
                                [0.6, 0.5, 0.6])},
        'japan_20261117.json': {
            'JP_POLICY_RATE': (['2025-10-01', '2026-07-01', '2026-10-01'],
                               [0.5, 0.75, 0.75])},
    }
    for fname, series in inj.items():
        doc = {'date': '20261117', 'version': 'r19gate-r20face',
               'series': {mid: {'dates': d, 'values': v,
                                'note': 'R19 门 R20 四地补齐注入(合成,'
                                        '离线)'} for mid, (d, v)
                          in series.items()},
               **SYN_MARK}
        json.dump(doc, open(os.path.join(dd, fname), 'w', encoding='utf-8'),
                  ensure_ascii=False)
    # R20 政策目标行注入: DFEDTARU/L(冻结面 cn-task-b 只有 DFF 市场口径)
    # ——注册表 history_source=macro_collector,走 macro 档 data 节入 store
    mp = os.path.join(dd, 'macro_20261117.json')
    mdoc = json.load(open(mp, encoding='utf-8'))
    _pol_days = ['2025-11-14', '2026-08-14', '2026-11-13']
    mdoc['data']['DFEDTARU'] = {'value': 3.75, 'date': '2026-11-13',
                                'frequency': 'daily', 'unit': 'percent',
                                'series': {'dates': _pol_days,
                                           'values': [3.75, 3.75, 3.75]}}
    mdoc['data']['DFEDTARL'] = {'value': 3.50, 'date': '2026-11-13',
                                'frequency': 'daily', 'unit': 'percent',
                                'series': {'dates': _pol_days,
                                           'values': [3.50, 3.50, 3.50]}}
    json.dump(mdoc, open(mp, 'w', encoding='utf-8'), ensure_ascii=False)
    # R20 资产回贴注入: SPX/VIX 日频序列(global 通道,周内日 2026-09-28→
    # 2026-11-13)——资产回报回贴契约的复算标的;VIX 段值单调抬升,月窗
    # 涨幅约 +38%(真实面 38.07% 核验在 r20-evidence 实跑档)
    import datetime as _dt
    d0, d1 = _dt.date(2026, 9, 28), _dt.date(2026, 11, 13)
    days = [(d0 + _dt.timedelta(days=i)).isoformat()
            for i in range((d1 - d0).days + 1)]
    days = [x for x in days
            if _dt.date(int(x[:4]), int(x[5:7]), int(x[8:10])).weekday() < 5]
    n = len(days)
    spx_v = [round(5997.0 - 92.0 * i / max(n - 1, 1), 2) for i in range(n)]
    vix_v = [round(16.5 + 6.3 * i / max(n - 1, 1), 2) for i in range(n)]
    gdoc = {'date': '20261117', 'version': 'r19gate-r20face',
            'data': {'SPX': {'close': spx_v[-1], 'date': days[-1],
                             'series': {'dates': days, 'values': spx_v}},
                     'VIX': {'close': vix_v[-1], 'date': days[-1],
                             'series': {'dates': days, 'values': vix_v}}},
            **SYN_MARK}
    json.dump(gdoc, open(os.path.join(dd, 'global_20261117.json'), 'w',
                         encoding='utf-8'), ensure_ascii=False)


def build_root(mutate=lambda doc: doc):
    """引擎根=仓码+变异冻结面+重建快照。"""
    d = tempfile.mkdtemp(prefix='r19gate_')
    shutil.copy(os.path.join(ROOT, 'ia_cli.py'), os.path.join(d, 'ia_cli.py'))
    shutil.copy(os.path.join(ROOT, 'env_config.py'),
                os.path.join(d, 'env_config.py'))
    shutil.copytree(os.path.join(ROOT, 'scripts'), os.path.join(d, 'scripts'))
    shutil.copytree(os.path.join(ROOT, 'config'), os.path.join(d, 'config'))
    dd = os.path.join(d, 'data', 'daily')
    os.makedirs(dd)
    doc = mutate(json.loads(json.dumps(_REAL)))
    json.dump(doc, open(os.path.join(dd, 'macro_20261117.json'), 'w',
                        encoding='utf-8'), ensure_ascii=False)
    _complete_r20_face(dd)
    sb.build_snapshot(target_ymd='20261117', data_dir=dd, out_dir=dd,
                      as_of='2026-11-17T08:36:00+08:00', trusted_root=d)
    return d


def plan_run(engine_root, tag, timeout=600):
    od = os.path.join(TMPG, 'plan_%s' % tag)
    r = subprocess.run(
        [sys.executable, 'ia_cli.py', 'research-one', '--stage', 'plan',
         '--question', Q_MAP, '--out-dir', od, '--engine-root', engine_root],
        cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    c = sorted(glob.glob(os.path.join(od, '*', 'report.json')))
    if not c:
        return None, r
    return json.load(open(c[0], encoding='utf-8')), r


def cli_stage(stage, rd, engine_root, arc=None, judgment=None, timeout=240):
    cmd = [sys.executable, 'ia_cli.py', 'research-one', '--stage', stage,
           '--report-dir', rd, '--engine-root', engine_root]
    if arc:
        cmd += ['--archive-dir', arc]
    if judgment:
        cmd += ['--judgment', judgment]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                       timeout=timeout)
    try:
        data = json.loads(r.stdout)['data']
    except Exception:
        data = {'raw': ((r.stdout or '') + (r.stderr or ''))[-400:]}
    return r.returncode, data


_seq = [0]


def map_judgment(rd, variant=None):
    """地图判定夹具(R18 门同源,历史段升级 R19 结构化四字段)。"""
    rep = json.load(open(os.path.join(rd, 'report.json'), encoding='utf-8'))
    rp = rep.get('research_plan') or {}
    ev = rep.get('evidence_index') or []
    refs = [e['ref'] for e in ev if e.get('ref')][:2] or ['CPI@2026-10-01']
    cands = (rp.get('turning_candidates') or {}).get('candidates') or []
    pool = [c for c in cands if c.get('metric_id')]
    if variant == 'same_dim':
        pool = [c for c in pool if c.get('dimension') == 'inflation'] or pool
    t3 = pool[:3]
    turnings = [{'date': f"{c.get('to_ym')}-15",
                 'metric_id': c.get('metric_id'),
                 'before_date': f"{c.get('from_ym')}-15",
                 'value_before': c.get('value_before'),
                 'value_after': c.get('value_after'),
                 'first_mover': f"{c.get('region')} {c.get('metric_id')}"
                                '先动(合成)',
                 'follow_or_diverge': '其余维度滞后跟进(合成)'}
                for c in t3]
    if variant == 'dup_turning' and len(turnings) >= 2:
        turnings[1] = dict(turnings[0], follow_or_diverge='重复计数(合成)')
    dm = (t3[0].get('metric_id') if t3 else 'CPI')
    links = [
        {'step': 1, 'text': 'E1 环: 引擎序列可验证的观察(合成)',
         'evidence_level': 'E1', 'evidence_refs': refs,
         'observed_fact': '观察事实: 合成链环一(传导终点连到资产 UST_10Y,合成)',
         'causal_hypothesis': '因果假设: 合成(假设非预测)',
         'competing_explanation': '竞争解释: 合成竞争解释一',
         'distinguishing_metric': dm},
        {'step': 2, 'text': 'E2 环: 部分支持(合成)',
         'evidence_level': 'E2',
         'missing_link_note': '本环为【假设】: 合成缺环注记(离线)',
         'evidence_refs': refs,
         'observed_fact': '观察事实: 合成链环二',
         'causal_hypothesis': '因果假设: 合成二',
         'competing_explanation': '竞争解释: 合成竞争解释二',
         'distinguishing_metric': dm}]
    if variant == 'no_asset':
        links[0]['observed_fact'] = '观察事实: 合成链环一(不提任何资产,合成)'
        links[1]['observed_fact'] = '观察事实: 合成链环二(无资产)'
    regions = [{'region': r, 'from_to': f'{r} 从合成环境A走到合成环境B(离线)'}
               for r in sorted((rp.get('regions') or {}).keys()
                               or ['US', 'CN', 'EA', 'JP'])]
    # R20 回贴纪律: 三利率共同交易日面在场(trio ok)时,判定须回贴
    # rates_decomposition——夹具按引擎面逐字回贴(数值取自 report 引擎
    # 复算,非编造),保持 R19 行为断言(attach 正例)在 R20 契约下成立
    trio = rp.get('us_rates_trio') or {}
    reader_map_extra = {}
    if trio.get('status') == 'ok':
        _w, _c = trio.get('window') or {}, trio.get('chg_bp') or {}
        reader_map_extra['rates_decomposition'] = {
            'window_from': _w.get('from'), 'window_to': _w.get('to'),
            'nominal_bp': _c.get('UST_10Y'),
            'real_bp': _c.get('TIPS_10Y'),
            'bei_bp': _c.get('BEI_10Y')}
    hist = [{'period_label': '2015-2016(合成类比期)',
             'similarity': '合成相似点(离线)',
             'difference': '合成关键差异(离线)',
             'other_regions_sync': '其他经济体合成同步注记(离线)',
             'ex_post': {'3m': '随后3个月合成实际表现(2016-03)',
                         '6m': '随后6个月合成实际表现(2016-06)',
                         '12m': '随后12个月合成实际表现(2016-12)'},
             'anchor_ym': '2015-12',
             'match_window': {'start_ym': '2015-01', 'end_ym': '2015-12'},
             'judgment_cutoff_ym': '2015-12',
             'aftermath_obs_months': ['2016-03', '2016-06', '2016-12'],
             # R21: 样本注记字段名随契约正名 sample_note(渲染同读);
             # data_note 保留兼容旧档,断言意图不变。
             'data_note': '样本注记: 合成(离线门测试)',
             'sample_note': '样本注记: 合成(离线门测试;与当前窗不重叠)',
             'us_analog': True}]
    if variant == 'hist_no_anchor':
        hist[0].pop('anchor_ym')
        hist[0].pop('match_window')
        hist[0].pop('judgment_cutoff_ym')
        hist[0].pop('aftermath_obs_months')
    elif variant == 'hist_short_reach':
        hist[0]['aftermath_obs_months'] = ['2016-03', '2016-06']  # 缺 12m 月
    elif variant == 'hist_leak':
        hist[0]['aftermath_obs_months'] = ['2015-06', '2016-03',
                                           '2016-06', '2016-12']
    elif variant == 'hist_cutoff_early':
        hist[0]['judgment_cutoff_ym'] = '2015-06'   # 早于匹配末月
    jd = {
        'schema_version': '1.1',
        'agent_declaration': {'attribution': 'ai_inferred',
                              'note': '合成地图判决(离线门测试)', **SYN_MARK},
        'l3': {
            'contradictions': [{
                'id': 'CON-1', 'statement': '合成矛盾陈述(离线门测试)',
                'basis': '基于证据索引的推断',
                'competing_explanations': ['解释一(基准)', '解释二(反例)'],
                'evidence_refs': refs}],
            'mechanism_chains': [{
                'id': 'MECH-1', 'name': '合成传导链', 'links': links}]},
        'l4': {'scenarios': [
            {'id': 'SCN-A', 'role': '基准', 'rows': {
                'scenario': '情景A(假设非预测): 合成基准',
                'asset_direction': {'direction': '上行',
                                    'confidence_tier': '有相关证据',
                                    'text': '合成方向', 'evidence_refs': refs},
                'sensitive_variables': [dm],
                'falsification': {'metric_id': dm,
                                  'threshold': '突破合成阈值 4.5'},
                'trigger': {'condition': '合成可观测条件',
                            'deadline': '2027-06-30'}}},
            {'id': 'SCN-B', 'role': '反例', 'rows': {
                'scenario': '情景B(假设非预测): 合成反例',
                'asset_direction': {'direction': '区间',
                                    'confidence_tier': '纯逻辑推理',
                                    'text': '合成反例方向', 'evidence_refs': []},
                'sensitive_variables': [dm],
                'falsification': {'metric_id': dm,
                                  'threshold': '跌破合成阈值 2.5'},
                'trigger': {'condition': '合成反例条件',
                            'deadline': '2027-06-30'}}}]},
        'reader_map': {
            'headline_conclusion': '合成一句总判断: 四地合成环境对照(离线)',
            'regions': regions,
            'transmission': [{'chain_name': '合成传导链(文字传导图)',
                              'links': links}],
            'turnings': turnings,
            'history_periods': hist,
            **reader_map_extra}}
    jd.update(SYN_MARK)
    _seq[0] += 1
    jp = os.path.join(TMPG, 'jd%d_%s.json' % (_seq[0], variant or 'ok'))
    json.dump(jd, open(jp, 'w', encoding='utf-8'), ensure_ascii=False)
    return jp


def attach_map_checks(rd, root, variant):
    """attach 某变体→(attached, map_checks)。契约细节随档在
    report.json→agent_judgment.contract_verification(attach 双路都写)。"""
    jd_p = map_judgment(rd, variant)
    rc, data = cli_stage('attach', rd, root, judgment=jd_p)
    rep = json.load(open(os.path.join(rd, 'report.json'), encoding='utf-8'))
    cv = ((rep.get('agent_judgment') or {}).get('contract_verification')) or {}
    return data.get('attached'), cv.get('map_checks') or [], \
        cv.get('verdict')


def find_item(mc, frag):
    return next((m for m in mc if frag in str(m.get('item'))), None)


def fresh_dir(src, tag):
    dst = os.path.join(TMPG, tag)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    return dst


def contract_of(rd):
    rep = json.load(open(os.path.join(rd, 'report.json'), encoding='utf-8'))
    jd_doc = json.load(open(os.path.join(rd, 'agent_judgment.json'),
                            encoding='utf-8'))
    return jc.verify_judgment(jd_doc, rep), rep


def test_audit_r19_gate():
    global _plan_a_rd
    print('── 构建冻结面引擎根+plan 阶段(正式 CLI)……')
    root, rep = _init()
    _plan_a_rd = _plan_a_rd
    rp = rep.get('research_plan') or {}
    pv = rp.get('point_values') or {}
    print('═══ §A 同比基期纪律(D1) ═══')
    # A1 单元级: 严格同基期——去年同月在=出数,缺= None(不取最近前值)
    y = rmp._derive_yoy(['2025-02-01', '2026-02-01'], [100.0, 110.0], 1)
    n = rmp._derive_yoy(['2025-01-01', '2026-02-01'], [100.0, 110.0], 1)
    check('§A 严格同基期: 同月在→同比,缺基期→None(非最近前值)',
          y == 10.0 and n is None, f'{y}/{n}')
    # A2 真实冻结面: CPI 最新一期(2026-10)缺 2025-10 基月(面已由 _init 构建)
    cpi = next((c for c in pv.get('cells') or []
                if c['metric_id'] == 'CPI'), {})
    latest = (cpi.get('anchors') or {}).get('最新一期') or {}
    check('§A CPI@最新一期 缺基期→derived=None+yoy_status 标注+最近有效同比',
          latest.get('derived_yoy_pct') is None
          and latest.get('yoy_status') == 'no_same_period_base'
          and (latest.get('latest_valid_yoy') or {}).get('observation_date'),
          json.dumps(latest, ensure_ascii=False)[:150])
    # A3 基线缺陷值不得再现: 13 个月变化(≈4.08)不得以同比身份出现
    blob = json.dumps(pv, ensure_ascii=False)
    check('§A 13 个月变化不得写成同比(4.08 不在点值面)',
          '4.08' not in blob and '"derived_yoy_pct": 4.08' not in blob)
    # A4 同比空间转折序列同纪律: 缺基期月被剔除
    mon = rmp._monthly_series_for_turning(
        ['2025-01-01', '2026-01-01', '2026-02-01'],
        [100.0, 110.0, 120.0], 'index_point')
    check('§A 转折同比空间: 缺基期月不出数',
          [m[0] for m in mon] == ['2026-01'], str(mon))

    print('═══ §B 发布纪律(D2) ═══')
    gdp = next((c for c in pv.get('cells') or []
                if c['metric_id'] == 'US_REAL_GDP'), {})
    a3m = (gdp.get('anchors') or {}).get('3个月前') or {}
    aln = (gdp.get('anchors') or {}).get('最新一期') or {}
    check('§B GDP 3个月前(锚2026-08-17)→Q2 观测(非 10-29 才公布的 Q3)',
          a3m.get('observation_date') == '2026-04-01'
          and a3m.get('publication_date') == '2026-07-29',
          json.dumps(a3m, ensure_ascii=False)[:130])
    check('§B GDP 最新一期→Q3 观测+发布日 2026-10-29(审计给定事实)',
          aln.get('observation_date') == '2026-07-01'
          and aln.get('publication_date') == '2026-10-29',
          json.dumps(aln, ensure_ascii=False)[:130])
    une = next((c for c in pv.get('cells') or []
                if c['metric_id'] == 'UNEMPLOYMENT'), {})
    u12 = (une.get('anchors') or {}).get('12个月前') or {}
    # R20 口径修正(2025 政府停摆日历实录): 锚 2025-11-17 时 9 月观测
    # (BLS 停摆,first_publish=2025-11-19>锚日)被日历条目判不可见→排除;
    # 11月值发布 2025-12-05>锚日同样排除;数据面缺 10 月 → 交付 8 月
    # 4.3——与审计给定事实「2025-11-18 该日美国只能看到…八月失业率
    # 4.3%」逐位一致(R19 旧断言=规则推定世界的 9 月,已被 R20 日历实录
    # 取代;规则本身未删,作为无日历条目时的兜底仍在 §B GDP 两断言中验证)
    check('§B 失业率 12个月前: 9月停摆未发布+11月滞后发布均被排除→'
          '交付 8月 4.3(R20 日历实录修正)',
          u12.get('observation_date') == '2025-08-01'
          and u12.get('value') == 4.3
          and u12.get('publication_date') == '2025-09-05'
          and str(u12.get('publication_date')) <= '2025-11-17',
          json.dumps(u12, ensure_ascii=False)[:130])
    viol = []
    for c in pv.get('cells') or []:
        for lbl, a in (c.get('anchors') or {}).items():
            if a.get('status') == 'ok':
                if not a.get('publication_date') or \
                        a['publication_date'] > a['as_of']:
                    viol.append((c['metric_id'], lbl))
    check('§B 全格不变量: 发布日≤锚日且发布日随格披露',
          not viol, str(viol)[:120])

    print('═══ §C 覆盖与口径(D6) ═══')
    cn_inf = [c['metric_id'] for c in (
        (rp.get('regions') or {}).get('CN', {})
        .get('dimensions', {}).get('inflation') or [])]
    cn_grw = [c['metric_id'] for c in (
        (rp.get('regions') or {}).get('CN', {})
        .get('dimensions', {}).get('growth') or [])]
    check('§C 中国 PPI 归入价格(通胀)维,不再挂增长维',
          'CN_PPI_YOY' in cn_inf and 'CN_PPI_YOY' not in cn_grw,
          f'inf={cn_inf} grw={cn_grw}')
    jp_pol = [c['metric_id'] for c in (
        (rp.get('regions') or {}).get('JP', {})
        .get('dimensions', {}).get('policy') or [])]
    gaps = {(g.get('region'), g.get('metric_id'), g.get('gap'))
            for g in rp.get('dimension_gaps') or []}
    check('§C 日本市场利率在列+央行目标以声明式缺口行分别列示',
          jp_pol == ['JP_POLICY_RATE']
          and ('JP', 'JP_POLICY_TARGET', 'registry_absent') in gaps,
          f'{jp_pol} gaps={sorted(map(str, gaps))[:4]}')
    tgt_gap = next((g for g in rp.get('dimension_gaps') or []
                    if g.get('metric_id') == 'JP_POLICY_TARGET'), {})
    check('§C 目标缺口注记写清查过的来源+影响',
          '检索范围' in str(tgt_gap.get('note'))
          and '影响' in str(tgt_gap.get('note')))

    print('═══ §D 转折候选三维(D3) ═══')
    cands = (rp.get('turning_candidates') or {}).get('candidates') or []
    dims = {c.get('dimension') for c in cands}
    mids = [c.get('metric_id') for c in cands]
    check('§D 候选池含增长+通胀+政策三维',
          {'growth', 'inflation', 'policy'} <= dims, str(dims))
    check('§D 每指标至多一候选', len(mids) == len(set(mids)))
    check('§D 候选窗端点在截止日回看 13 月内',
          all(c.get('from_ym') >= '2025-11' and c.get('to_ym') <= '2026-11'
              for c in cands))

    print('═══ §E 历史类比结构面(D4) ═══')
    check('§E 锚 2022-06 → 3/6/12 月=2022-09/2022-12/2023-06',
          rmp.ex_post_windows('2022-06') == {'3m': '2022-09',
                                             '6m': '2022-12',
                                             '12m': '2023-06'},
          str(rmp.ex_post_windows('2022-06')))
    for variant in ('hist_no_anchor', 'hist_short_reach',
                    'hist_cutoff_early'):
        att, mc, verdict = attach_map_checks(_plan_a_rd, root, variant)
        bads = [f"{m.get('item')}={m.get('status')}" for m in mc
                if m.get('status') != 'VERIFIED']
        check(f'§E {variant} → 契约拦截阻断归档',
              att is False and verdict != 'VERIFIED' and bool(bads),
              '; '.join(bads)[:160])
    att, mc, verdict = attach_map_checks(_plan_a_rd, root, 'hist_leak')
    leak = find_item(mc, 'aftermath_in_match')
    check('§E 历史结果落在匹配期内 → CONTRADICTED(四阻断器④)',
          att is False and leak and leak.get('status') == 'CONTRADICTED',
          str(leak)[:150])

    print('═══ §F 四阻断器+传导达资产(D5/D7) ═══')
    att, mc, _v = attach_map_checks(_plan_a_rd, root, 'dup_turning')
    hit = find_item(mc, 'turnings.duplicate')
    check('§F 同一转折重复三次 → 阻断(turnings.duplicate)',
          att is False and hit is not None, str(hit)[:140])
    att, mc, _v = attach_map_checks(_plan_a_rd, root, 'same_dim')
    hit = find_item(mc, 'dimension_coverage')
    check('§F 三转折维度覆盖不足(候选池跨三维而全选通胀) → 阻断',
          att is False and hit is not None, str(hit)[:140])
    att, mc, _v = attach_map_checks(_plan_a_rd, root, 'no_asset')
    hit = find_item(mc, 'asset_reach')
    check('§F 传导图未连到资产指标 → 阻断',
          att is False and hit is not None, str(hit)[:140])
    # 注入式引擎面自检: 篡改 research_plan(假同比/假发布日) → CONTRADICTED
    rep_tamper = json.load(open(os.path.join(_plan_a_rd, 'report.json'),
                                encoding='utf-8'))
    pv_t = copy.deepcopy(rep_tamper['research_plan']['point_values'])
    for c in pv_t.get('cells') or []:
        if c['metric_id'] == 'CPI':
            for lbl, a in (c.get('anchors') or {}).items():
                if a.get('yoy_status') == 'no_same_period_base':
                    a['derived_yoy_pct'] = 4.08   # 错用基期的假同比
        if c['metric_id'] == 'UNEMPLOYMENT':
            for lbl, a in (c.get('anchors') or {}).items():
                a['publication_date'] = '2099-01-01'   # 提前引用未发布
    rep_tamper['research_plan']['point_values'] = pv_t
    jd_doc = json.load(open(map_judgment(_plan_a_rd, 'ok'), encoding='utf-8'))
    v2 = jc.verify_judgment(jd_doc, rep_tamper)
    mitems = {str(m.get('item')): m for m in v2.get('map_checks') or []}
    check('§F 错用同比基期(引擎面自检) → CONTRADICTED',
          mitems.get('point_values.yoy_base', {}).get('status')
          == 'CONTRADICTED', str(mitems.get('point_values.yoy_base'))[:120])
    check('§F 提前引用未发布(引擎面自检) → CONTRADICTED',
          mitems.get('point_values.publication', {}).get('status')
          == 'CONTRADICTED',
          str(mitems.get('point_values.publication'))[:120])

    print('═══ §G 普通读者版量化显示(D8,VIX 样本形状) ═══')
    # R24 真档 S6 信封形状(VIX volatility 维+rank-1 2023-03+披露三行)
    s6_shape = {
        'anchor_month': '2026-11', 'feature_window_months': 12,
        'sort_basis': 'expanding z 距离',
        'top': [{'rank': 1, 'candidate_month': '2023-03',
                 'distance': 0.486589, 'distance_percentile': 0.0,
                 'dims': {'rates': {'contribution_share': 0.746109},
                          'volatility': {'contribution_share': 0.159602},
                          'credit': {'contribution_share': 0.0}}}],
        'disclosure': ['相似≠因果, 更非预测: TOP-N 是历史状态距离最近的时期, '
                       '当时之后的演变只是历史记录',
                       '距离分位=该候选在全部有效候选中的相对位置, 不是概率']}
    s5_shape = {'pearson_returns': 0.10669569322272435,
                'sides': [{'metric_id': 'SPX'}, {'metric_id': 'UST_10Y'}],
                'alignment': {'n_change_pairs': 2493,
                              'common_first': '2016-11-14',
                              'common_last': '2026-11-10'}}
    shaped = {'run': {'question': 'VIX 样本形状(合成)', 'ts_utc': 'x',
                      'git_head': 'x'},
              'layers': {}, 'steps': [
                  {'step': 'S6_analog', 'ok': True, 'executed': True,
                   'envelope': {'data': s6_shape}},
                  {'step': 'S5_compare', 'ok': True, 'executed': True,
                   'envelope': {'data': s5_shape}}],
              'evidence_index': [], 'notes': []}
    q_lines = ro._render_quant_sections(shaped)
    q_txt = '\n'.join(q_lines)
    check('§G 读者版渲染 S6 历史比较(rank-1 2023-03+披露)',
          '历史相似结构' in q_txt and '2023-03' in q_txt
          and '相似≠因果' in q_txt and 'volatility' in q_txt)
    check('§G 读者版渲染 S5 量化说明(pearson+n+共同窗)',
          '日度相关' in q_txt and '0.1067' in q_txt and '2493' in q_txt)
    # report.md 整渲同节(_render_md 内联): 真档 report.json 为底座,
    # S6 步骤信封注入 R24 VIX 形状 top(真实结构,数值取自 R32 在档事实)
    arc_rp = sorted(glob.glob(os.path.join(
        ROOT, 'research_archive', '20261116T045959Z_*', 'report.json')))[0]
    base = json.load(open(arc_rp, encoding='utf-8'))
    for s in base.get('steps') or []:
        if s.get('step') == 'S6_analog':
            s['envelope'] = {'ok': True, 'data': s6_shape}
    md = ro._render_md(base)
    check('§G report.md 普通读者版含 S6/S5 节',
          '## 历史相似结构' in md and '## 日度相关' in md
          and '2023-03' in md)

    print('═══ §H 端到端正反例(四阻断器守住归档门) ═══')
    jd_ok = map_judgment(_plan_a_rd, 'ok')
    rc, data = cli_stage('attach', _plan_a_rd, root, judgment=jd_ok)
    rep_a = json.load(open(os.path.join(_plan_a_rd, 'report.json'),
                           encoding='utf-8'))
    cv_v = ((rep_a.get('agent_judgment') or {})
            .get('contract_verification') or {}).get('verdict')
    check('§H 正例 attach → attached=True 契约过',
          data.get('attached') is True, str(cv_v))
    # 独立语义席裁决(合成席位;R18 门同法): report/archive 的席位门
    # R29 任务4: 席位终裁绑定冻结输入摘要(席位仿体随新合同)
    _fi_a = (rep_a.get('run') or {}).get('frozen_inputs')
    aj.record_semantic_verdict(
        root, _plan_a_rd, 'UPHELD', SYN_ROLE,
        notes='R19 门正例席位(合成隔离)',
        extra=({'frozen_inputs_sha256': aj.frozen_inputs_digest(_fi_a)}
               if _fi_a else None))
    rc, data = cli_stage('report', _plan_a_rd, root)
    dlv = data.get('deliverable')
    check('§H 正例 report → deliverable', dlv is True, str(dlv))
    map_md = open(os.path.join(_plan_a_rd, 'MAP_REPORT.md'),
                  encoding='utf-8').read()
    check('§H MAP_REPORT 缺基期格显示「同比不可得」+最近有效同比',
          '同比不可得' in map_md and '最近有效同比' in map_md)
    check('§H MAP_REPORT 关键数字表带发布日期列',
          '发布日期' in map_md and '2026-10-29' in map_md)
    check('§H MAP_REPORT 转折表带观测窗口列+历史段带匹配区间/事后窗锚月',
          '观测窗口' in map_md and '匹配区间' in map_md
          and '锚2015-12+12月→2016-12' in map_md.replace(' ', ''))
    fr_p = os.path.join(_plan_a_rd, 'FULL_REPORT.md')
    fr = open(fr_p, encoding='utf-8').read() if os.path.exists(fr_p) else ''
    check('§H FULL_REPORT 普通读者版显示 S5 量化说明(pearson 节)',
          '## 日度相关' in fr and 'pearson' in fr, fr_p[-60:])
    n0 = len(glob.glob(os.path.join(ARC, '*')))
    arc_pos = os.path.join(ARC, 'pos1')
    rc, data = cli_stage('archive', _plan_a_rd, root, arc=arc_pos)
    check('§H 正例归档 1 份(独立归档目录)',
          rc == 0 and os.path.isfile(os.path.join(arc_pos, 'report.json')),
          str(data.get('blocked') or 'ok')[:100])
    # 反例: 泄漏历史段 → 不可交付不可归档(席位即便 UPHELD 也拦)
    rd2 = fresh_dir(_plan_a_rd, 'neg_leak')
    jd_ng = map_judgment(rd2, 'hist_leak')
    cli_stage('attach', rd2, root, judgment=jd_ng)
    _fi_2 = (json.load(open(os.path.join(rd2, 'report.json'),
                            encoding='utf-8')).get('run')
             or {}).get('frozen_inputs')
    aj.record_semantic_verdict(
        root, rd2, 'UPHELD', SYN_ROLE,
        notes='R19 门反例席位(合成隔离)',
        extra=({'frozen_inputs_sha256': aj.frozen_inputs_digest(_fi_2)}
               if _fi_2 else None))
    rc, data = cli_stage('report', rd2, root)
    arc_neg = os.path.join(ARC, 'neg_leak')
    rc2, data2 = cli_stage('archive', rd2, root, arc=arc_neg)
    check('§H 反例(历史结果落在匹配期内) → 不交付+零归档目录',
          data.get('deliverable') is False and rc2 != 0
          and not os.path.exists(arc_neg),
          f"dlv={data.get('deliverable')} blocked={data2.get('blocked')}")

    n_pass = sum(1 for _n, okk, _d in RESULTS if okk)
    n_fail = len(RESULTS) - n_pass
    print(f'\nAudit-R19 判定: {n_pass} PASS / {n_fail} FAIL')
    assert n_fail == 0, f'{n_fail} 项未过: ' + '; '.join(
        n for n, okk, _d in RESULTS if not okk)


_plan_a_rd = None


def _init():
    global _plan_a_rd
    _r = build_root()
    rep, _pr = plan_run(_r, 'A')
    _plan_a_rd = os.path.dirname(glob.glob(os.path.join(
        TMPG, 'plan_A', '*', 'report.json'))[0])
    return _r, rep


if __name__ == '__main__':
    test_audit_r19_gate()
    # Audit-R20 任务5: conftest.SuiteFile 自执行静态检查要求字面
    # sys.exit(——本套件曾缺入口识别被强制判「套件不自执行」。补齐入口,
    # 原断言零改动(test_audit_r19_gate 全量保留)。
    sys.exit(0)
else:
    _r0, _rep0 = _init()
