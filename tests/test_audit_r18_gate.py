# -*- coding: utf-8 -*-
"""Audit-R18 门测试: 全球宏观地图问句的共享研究计划 + 读者报告五面契约 +
地图计划指标 planned 分级 + 「3个月前」日历点 vs 「事件后3个月」事后偏移分记。

缺陷类(基线 57bcb66 复现): 原问输入后 map_entities 只出经济体、metrics=[]
→ 降级「经济体概览」照常 run_ok=True 交付——答非所问的误通过面。
修复(共享一份研究计划,取数/报告/验收三段同源):
  M1 detect_map_question 严格触发(≥2 经济体∩{US,CN,EA,JP}+≥2 维度词
     增长/通胀/货币政策+形状词 地图/转折/传导/结构最像/环境);
  M2 plan_map: 地区×维度→注册表指标(口径注记)+三类时点锚分记
     (point=日历点 cutoff−N月 / ex_post=事件后+N月)+引擎转折候选面
     (水平序列转同比空间——指数漂移≠转折);
  M3 S4/S5/数据要求吃同一计划: 计划指标 tier=planned(缺数=缺数格披露
     不阻断,区别于词面命中 required 缺数阻断);
  M4 判定契约 reader_map 五面(总判断/走位/传导四字段环/恰三转折数值
     回贴引擎月末口径/历史 1..3 段含 ex_post 3/6/12月);
  M5 MAP_REPORT.md=确定性装配读者报告(零生成;在场文件≠当前装配
     → copies_consistent False 拒交付拒归档;缺席拒归档)。

产品验收(任务4反例): 机制正文空/None、必需图表面(对照/传导/转折/历史)
缺失、明确指定指标遗漏——全部阻止正式交付与新增归档;
「我关注10年期美债收益率。过去半年，只比较10年期美债收益率和30年期
美债收益率。」两项都保留,缺任一项阻止归档(R17 语义在新代码位保全)。

合成隔离标记: 本文件全部裁决/夹具 role=R18-SYNTHETIC-ISOLATED-TEST,
synthetic:true 顶层双写(离线测试,冻结面=仓内 cn-task-b 宏观档)。"""
import glob
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import agent_judgment as aj           # noqa: E402
import research_map_planner as rmp    # noqa: E402
import research_orchestrator as ro    # noqa: E402
import snapshot_builder as sb         # noqa: E402
import workbench_data as wd           # noqa: E402

SYN_ROLE = 'R18-SYNTHETIC-ISOLATED-TEST'
SYN_MARK = {'synthetic': True,
            'note': 'R18 离线门测试: 冻结面+正式 CLI,非真实外部数据'}

RESULTS = []


def check(name, ok, detail=''):
    RESULTS.append((name, bool(ok), str(detail)[:220]))
    print(('  ✅ ' if ok else '  ❌ ') + name + (f' — {detail}' if detail else ''),
          flush=True)


# ═══ 冻结面: 仓内 cn-task-b 宏观档(US 三维 8 序列+CN_PMI 226 月频) ═══
_REAL = json.load(open(os.path.join(
    ROOT, 'docs/autonomous-rd/cn-task-b-20261117T083954Z/macro_input/',
    'macro_20261117.json')))
TMPG = tempfile.mkdtemp(prefix='r18gate_')
ARC = os.path.join(TMPG, 'research_archive')

Q_MAP = ('给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在12个月前、'
         '3个月前和最新一期，分别处于什么增长、通胀和货币政策环境？过去一年'
         '最重要的三个转折是什么，谁先变，谁跟进或背离？证据最充分的传导机制'
         '是什么，还有什么解释，哪个指标能区分它们？历史上哪些时期结构最像，'
         '当时其他经济体是否同步，随后3、6、12个月经济和主要资产实际怎么走？')
Q_ONLY = ('我关注10年期美债收益率。过去半年，只比较10年期美债收益率和'
          '30年期美债收益率。')


def build_root(mutate):
    """引擎根=仓码+变异冻结面+重建快照(每次更换输入即重建)。"""
    d = tempfile.mkdtemp(prefix='r18gate_')
    shutil.copy(os.path.join(ROOT, 'ia_cli.py'), os.path.join(d, 'ia_cli.py'))
    shutil.copy(os.path.join(ROOT, 'env_config.py'),
                os.path.join(d, 'env_config.py'))
    shutil.copytree(os.path.join(ROOT, 'scripts'), os.path.join(d, 'scripts'))
    shutil.copytree(os.path.join(ROOT, 'config'), os.path.join(d, 'config'))
    dd = os.path.join(d, 'data', 'daily')
    os.makedirs(dd)
    doc = json.loads(json.dumps(_REAL))
    doc = mutate(doc)
    json.dump(doc, open(os.path.join(dd, 'macro_20261117.json'), 'w',
                        encoding='utf-8'), ensure_ascii=False)
    sb.build_snapshot(target_ymd='20261117', data_dir=dd, out_dir=dd,
                      as_of='2026-11-17T08:36:00+08:00', trusted_root=d)
    return d


def m_full(doc):
    return doc


def m_drop(key):
    def f(doc):
        doc['data'].pop(key)
        return doc
    return f


def plan_run(engine_root, tag, q, timeout=600):
    od = os.path.join(TMPG, 'plan_%s' % tag)
    r = subprocess.run(
        [sys.executable, 'ia_cli.py', 'research-one', '--stage', 'plan',
         '--question', q, '--out-dir', od, '--engine-root', engine_root],
        cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    c = sorted(glob.glob(os.path.join(od, '*', 'report.json')))
    if not c:
        return None
    j = json.load(open(c[0], encoding='utf-8'))
    steps = j.get('steps') or [{}]
    ent = next((s.get('deterministic_face') for s in steps
                if s.get('deterministic_face')), {}) or {}
    dr = ((j.get('run') or {}).get('data_requirements') or {})
    return {'rc': r.returncode, 'rd': os.path.dirname(c[0]),
            'metrics': ent.get('metrics'),
            'items': dr.get('items') or [], 'notes': j.get('notes') or [],
            'rp': j.get('research_plan') or {},
            'run_ok': j.get('run_ok')}


def cli_stage(stage, rd, engine_root, arc=None, judgment=None, timeout=240):
    cmd = [sys.executable, 'ia_cli.py', 'research-one', '--stage', stage,
           '--report-dir', rd, '--engine-root', engine_root]
    if arc:
        cmd += ['--archive-dir', arc]
    if judgment:
        cmd += ['--judgment', judgment]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                       timeout=timeout)
    data = {}
    try:
        data = json.loads(r.stdout)['data']
    except Exception:
        data = {'raw': ((r.stdout or '') + (r.stderr or ''))[-400:]}
    return r.returncode, data


_seq = [0]


def map_judgment(rd, variant=None):
    """地图判定夹具: l3/l4 合规面 + reader_map 五面。

    转折数值/区分指标全部从该 plan 的引擎确定性面取(与真实 Agent 席
    同一约束——契约数值回贴核对);variant 注入任务4反例。"""
    rep = json.load(open(os.path.join(rd, 'report.json'), encoding='utf-8'))
    rp = rep.get('research_plan') or {}
    ev = rep.get('evidence_index') or []
    refs = [e['ref'] for e in ev if e.get('ref')][:2] or ['CPI@2026-10-01']
    cands = (rp.get('turning_candidates') or {}).get('candidates') or []
    t3 = cands[:3]
    turnings = [{'date': f"{c.get('to_ym')}-15",
                 'metric_id': c.get('metric_id'),
                 'before_date': f"{c.get('from_ym')}-15",
                 'value_before': c.get('value_before'),
                 'value_after': c.get('value_after'),
                 'first_mover': f"{c.get('region')} {c.get('metric_id')}"
                                '先动(合成)',
                 'follow_or_diverge': '其余维度滞后跟进(合成)'}
                for c in t3]
    if variant == 'turnings2':
        turnings = turnings[:2]
    elif variant == 'turnings4':
        turnings = turnings + [dict(turnings[0])]
    elif variant == 'numeric_drift' and turnings:
        import copy
        turnings = [copy.deepcopy(turnings)]
        turnings[0][0]['value_after'] = \
            float(turnings[0][0]['value_after']) + 0.5
        turnings = turnings[0]
    dm = (t3[0].get('metric_id') if t3 else 'CPI')
    if variant == 'fake_dm':
        dm = 'ZZZ_FAKE_METRIC'
    links = [
        {'step': 1, 'text': 'E1 环: 引擎序列可验证的观察(合成)',
         'evidence_level': 'E1', 'evidence_refs': refs,
         'observed_fact': '观察事实: 合成链环一(引擎面)',
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
    if variant == 'link_text_empty':
        links[0]['text'] = ''
    elif variant == 'link_text_none':
        links[0]['text'] = None
    elif variant == 'link_missing_field':
        links[0].pop('competing_explanation')
    regions = [{'region': r, 'from_to': f'{r} 从合成环境A走到合成环境B(离线)'}
               for r in sorted((rp.get('regions') or {}).keys()
                               or ['US', 'CN', 'EA', 'JP'])]
    hist = [{'period_label': '2015-2016(合成类比期)',
             'similarity': '合成相似点(离线)',
             'difference': '合成关键差异(离线)',
             'other_regions_sync': '其他经济体合成同步注记(离线)',
             'ex_post': {'3m': '随后3个月合成实际表现(离线)',
                         '6m': '随后6个月合成实际表现(离线)',
                         '12m': '随后12个月合成实际表现(离线)'},
             'data_note': '样本注记: 合成(离线门测试)', 'us_analog': True}]
    if variant == 'history4':
        hist = hist + [dict(hist[0]), dict(hist[0]), dict(hist[0])]
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
                'id': 'MECH-1', 'name': '合成传导链',
                'links': links}]},
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
            'headline_conclusion': ('合成一句总判断: 四地合成环境对照'
                                    '(离线门测试)'),
            'regions': regions,
            'transmission': [{'chain_name': '合成传导链(文字传导图)',
                              'links': links}],
            'turnings': turnings,
            'history_periods': hist}}
    if variant == 'no_reader_map':
        jd.pop('reader_map')
    elif variant == 'hollow_headline':
        jd['reader_map']['headline_conclusion'] = ''
    jd.update(SYN_MARK)
    _seq[0] += 1
    jp = os.path.join(TMPG, 'jd%d_%s.json' % (_seq[0], variant or 'ok'))
    json.dump(jd, open(jp, 'w', encoding='utf-8'), ensure_ascii=False)
    return jp


def fresh_dir(src, tag):
    """复制 plan 运行目录(attach 会拒绝对已附档目录重复 attach)。"""
    dst = os.path.join(TMPG, tag)
    shutil.copytree(src, dst)
    return dst


def test_audit_r18_gate():
    reg = wd.load_registry(ROOT)

    # ═══ §A 识别与共享计划(纯函数面) ═══════════════════════════════
    print('§A 地图问句识别+计划')
    ent = ro.map_entities(Q_MAP, reg)
    check('§A M1 原问 → 识别为地图问句(基线: 仅经济体概览)',
          rmp.detect_map_question(Q_MAP, ent) is True,
          f"detect={rmp.detect_map_question(Q_MAP, ent)}")
    for q, why in [
            ('美国12个月前和3个月前的增长、通胀环境怎样？', '单经济体'),
            ('美国、中国、欧元区、日本的宏观环境地图', '无维度词'),
            ('日本和欧元区的货币政策地图', '经济体不足(严格触发≥2交集)')]:
        _e = ro.map_entities(q, reg)
        check(f'§A 近失({why})「{q[:14]}…」→ 非地图问句(不误触发)',
              rmp.detect_map_question(q, _e) is False,
              f"detect={rmp.detect_map_question(q, _e)}")
    plan = rmp.plan_map(Q_MAP, ent, reg['by_id'], '2026-11-18')
    check('§A M2 计划: 四地×三维+指标非空(答非所问面闭合)',
          sorted(plan['regions'].keys()) == ['CN', 'EA', 'JP', 'US']
          and sorted(plan['dimensions']) == ['growth', 'inflation', 'policy']
          and len(plan['metrics']) >= 15,
          f"regions={sorted(plan['regions'].keys())} "
          f"n_metrics={len(plan['metrics'])}")
    _pa = rmp.parse_point_anchors(Q_MAP, '2026-11-18')
    check('§A 三时点=日历点锚分记(12月前/3月前/最新)',
          [(a['kind'], a['as_of']) for a in _pa] ==
          [('point', '2025-11-18'), ('point', '2026-08-18'),
           ('point', '2026-11-18')],
          f"anchors={[(a['kind'], a.get('as_of')) for a in _pa]}")
    _pb = rmp.parse_point_anchors('美国一年前和3个月前处于什么增长环境？',
                                  '2026-11-18')
    check('§A 「一年前」形 → 同为 12 月日历点锚',
          [a.get('months_before') for a in _pb] == [12, 3],
          f"months={[a.get('months_before') for a in _pb]}")
    _ex = rmp.parse_ex_post_offsets(Q_MAP)
    check('§A 「随后3、6、12个月」=事后偏移锚(kind≠point)',
          [e['months'] for e in _ex] == [3, 6, 12]
          and all(e['kind'] == 'ex_post' for e in _ex),
          f"ex={[ (e['kind'], e['months']) for e in _ex]}")
    check('§A 锚语义注记: 两类时间分记不混同',
          '日历点锚' in (plan.get('anchor_semantics_note') or '')
          and '事后偏移' in (plan.get('anchor_semantics_note') or ''),
          f"note={(plan.get('anchor_semantics_note') or '')[:80]}")
    check('§A 维度缺口如实点名(EA/JP 增长无注册表指标)',
          any('EA' in (g.get('note') or '') and '增长' in (g.get('note') or '')
              for g in plan.get('dimension_gaps') or [])
          and any('JP' in (g.get('note') or '')
                  for g in plan.get('dimension_gaps') or []),
          f"gaps={len(plan.get('dimension_gaps') or [])}")
    check('§A 上下文指标含美债三利率(任务3复算面)',
          {'UST_10Y', 'TIPS_10Y', 'BEI_10Y'} <=
          set(plan.get('context_metrics') or []),
          f"ctx={plan.get('context_metrics')}")

    # ═══ §B 窗口透传: 点/事后时间词被计划消费,非地图路径不变 ══════
    print('§B 窗口(地图透传+非地图零回归)')
    _spans = rmp.consumed_time_spans(Q_MAP)
    w_map = ro._question_window(Q_MAP, ro._entity_spans(
        Q_MAP, reg['by_id'], ent['metrics']), map_time_spans=_spans)
    check('§B M3 原问+计划时间词消费 → 「过去一年」窗正常解析',
          w_map.get('kind') == 'relative' and w_map.get('years') == 1,
          f"kind={w_map.get('kind')} years={w_map.get('years')}")
    w_bare = ro._question_window(Q_MAP, ro._entity_spans(
        Q_MAP, reg['by_id'], ent['metrics']))
    check('§B 同问无地图透传 → 残缺数量仍拒绝(R10 语义保全,仅地图放行)',
          w_bare.get('kind') == 'unparseable'
          and '无法完整解析' in (w_bare.get('reason') or ''),
          f"kind={w_bare.get('kind')}")
    _e2 = ro.map_entities(Q_ONLY, reg)
    w2 = ro._question_window(Q_ONLY, ro._entity_spans(
        Q_ONLY, reg['by_id'], _e2['metrics']))
    check('§B 只比较问句零回归 → [10Y,30Y]+六月窗',
          sorted(set(_e2['metrics'])) == ['UST_10Y', 'UST_30Y']
          and w2.get('kind') == 'relative_months' and w2.get('months') == 6,
          f"mets={_e2['metrics']} months={w2.get('months')}")
    check('§B 只比较问句非地图问句(不误入地图面)',
          rmp.detect_map_question(Q_ONLY, _e2) is False,
          f"detect={rmp.detect_map_question(Q_ONLY, _e2)}")

    # ═══ §C 正式 plan: 共享计划入档+planned 分级+缺数披露 ══════════
    print('§C 正式 plan(冻结根,原问+只比较)')
    r_full = build_root(m_full)
    r_n10 = build_root(m_drop('UST_10Y'))

    p = plan_run(r_full, 'map', Q_MAP)
    _rp = p['rp'] if p else {}
    _pl = [i for i in (p['items'] if p else [])
           if i.get('tier') == 'planned']
    _rq = [i for i in (p['items'] if p else [])
           if i.get('tier') == 'required']
    _cands = ((_rp.get('turning_candidates') or {})
              .get('candidates') or [])
    check('§C 原问 plan → run_ok+research_plan 入档(基线 metrics=[] 已闭合)',
          p is not None and p.get('run_ok') is True
          and _rp.get('map_question') is True
          and sorted((_rp.get('regions') or {}).keys()) ==
          ['CN', 'EA', 'JP', 'US'],
          f"run_ok={p and p.get('run_ok')} regions="
          f"{sorted((_rp.get('regions') or {}).keys())}")
    check('§C 计划指标 planned 分级在场(缺数=披露非阻断)',
          len(_pl) >= 10
          and all('地图研究计划' in (i.get('basis') or '') for i in _pl),
          f"planned={len(_pl)} basis0={(_pl[0].get('basis') if _pl else '')[:40]}")
    check('§C 缺数注记点名(检索范围+影响分级,run_ok 不被计划缺口阻断)',
          any(n.startswith('地图计划指标缺数') for n in (p['notes'] if p else [])),
          f"notes={[n[:30] for n in (p['notes'] if p else [])][:3]}")
    check('§C 转折候选面在场+同比空间(水平序列漂移不作转折)',
          len(_cands) >= 3
          and all('同比' not in (c.get('unit') or '')
                  or '派生' in (c.get('unit') or '') for c in _cands),
          f"n={len(_cands)} top={[(c.get('metric_id'), c.get('to_ym')) for c in _cands[:3]]}")

    p2 = plan_run(r_full, 'only', Q_ONLY)
    _i2 = {i.get('metric_id'): i for i in (p2['items'] if p2 else [])}
    check('§C 只比较(任务4再测) → 两期限都在必需集+满足',
          p2 is not None
          and sorted(set(p2['metrics'])) == ['UST_10Y', 'UST_30Y']
          and _i2.get('UST_10Y', {}).get('outcome') == 'satisfied'
          and _i2.get('UST_30Y', {}).get('outcome') == 'satisfied',
          f"mets={p2 and p2['metrics']} "
          f"out={ {k: v.get('outcome') for k, v in _i2.items()} }")
    p3 = plan_run(r_n10, 'onlyNo10', Q_ONLY)
    _i3 = {i.get('metric_id'): i for i in (p3['items'] if p3 else [])}
    check('§C 移除10年 → 明确指定指标遗漏=阻断(写明缺什么,30Y 仍要求)',
          p3 is not None
          and sorted(set(p3['metrics'])) == ['UST_10Y', 'UST_30Y']
          and _i3.get('UST_10Y', {}).get('outcome') in
          ('insufficient_coverage', 'missing')
          and (_i3.get('UST_10Y', {}).get('outcome_basis') or '')
          .startswith('缺什么: UST_10Y'),
          f"out10={(_i3.get('UST_10Y') or {}).get('outcome')} "
          f"ob={((_i3.get('UST_10Y') or {}).get('outcome_basis') or '')[:50]}")

    # ═══ §D 判定契约反例(attach 级: 正例落位,反例 attached=False) ═══
    print('§D reader_map 契约(任务4反例)')
    _pos = fresh_dir(p['rd'], 'd_ok')
    rc_ok, d_ok = cli_stage('attach', _pos, eroot,
                            judgment=map_judgment(_pos))
    check('§D 正例(五面齐+数值回贴引擎面) → attach 落位',
          rc_ok == 0 and d_ok.get('attached') is True
          and os.path.isfile(os.path.join(_pos, 'agent_judgment.json')),
          f"rc={rc_ok} attached={d_ok.get('attached')}")
    for var, label, kind in [
            ('link_text_empty', '机制正文空串', 'schema'),
            ('link_text_none', '机制正文 None', 'schema'),
            ('no_reader_map', 'reader_map 整体缺席', 'contract'),
            ('hollow_headline', '一句总判断为空', 'contract'),
            ('link_missing_field', '传导环缺竞争解释字段', 'contract'),
            ('turnings2', '转折仅 2 个', 'contract'),
            ('turnings4', '转折 4 个', 'contract'),
            ('history4', '历史 4 段', 'contract'),
            ('numeric_drift', '转折后值与引擎月末口径不符', 'contra'),
            ('fake_dm', '区分指标不在计划/证据面', 'contra')]:
        _d = fresh_dir(p['rd'], 'd_%s' % var)
        _rc, _out = cli_stage('attach', _d, eroot,
                              judgment=map_judgment(_d, variant=var))
        _ok = _rc == 0 and _out.get('attached') is False and not \
            os.path.isfile(os.path.join(_d, 'agent_judgment.json'))
        _det = ''
        if kind == 'schema':
            _v = json.dumps((_out.get('violations') or []), ensure_ascii=False)
            _ok = _ok and '正文' in _v
            _det = f"viol={_v[:80]}"
        else:
            _rj = json.load(open(os.path.join(_d, 'report.json'),
                                 encoding='utf-8'))
            _cv = ((_rj.get('agent_judgment') or {})
                   .get('contract_verification') or {})
            _ver = _cv.get('verdict')
            _mcs = json.dumps(_cv.get('map_checks') or [],
                              ensure_ascii=False)
            if kind == 'contra':
                _ok = _ok and _ver == 'CONTRADICTED' and \
                    'reader_map' in _mcs
                _det = f"verdict={_ver}"
            else:
                _ok = _ok and _ver == 'NOT_VERIFIED' and \
                    'reader_map' in _mcs
                _det = f"verdict={_ver}"
        check(f'§D 反例({label}) → 拒落位'
              + ('[CONTRADICTED]' if kind == 'contra' else ''), _ok,
              f"attached={_out.get('attached')} {_det}")

    # ═══ §E 交付/归档门(读者报告+篡改+缺席+SHA 回读) ═══════════════
    print('§E 报告/归档门')
    _rep_hollow = {'run_ok': True,
                   'layers': {'L1_事实层': {'rows': [1, 2, 3]}},
                   'run': {'data_requirements': {'items': [
                       {'metric_id': 'CPI', 'tier': 'planned',
                        'outcome': 'satisfied'}]}},
                   'research_plan': {'map_question': True},
                   'agent_judgment': {'attached': False,
                                      'reader_map_faces':
                                      {'complete': False,
                                       'note': 'attach 未成功'}}}
    check('§E 空洞 reader_map → blocked_class=map_required_face_missing',
          aj.blocked_class_of(_rep_hollow) == 'map_required_face_missing',
          f"bc={aj.blocked_class_of(_rep_hollow)}")

    def chain(tag, plan_d, positive, judgment=None):
        rd = plan_d
        rc_a, _ = cli_stage('attach', rd, eroot,
                            judgment=judgment or map_judgment(rd))
        if os.path.isfile(os.path.join(rd, 'agent_judgment.json')):
            aj.record_semantic_verdict(eroot, rd, 'UPHELD', SYN_ROLE)
        rc_r, d_r = cli_stage('report', rd, eroot)
        arcx = os.path.join(ARC, tag)
        rc_arc, _ = cli_stage('archive', rd, eroot, arc=arcx)
        _mx = glob.glob(os.path.join(arcx, '**', 'ARCHIVE_MANIFEST.json'),
                        recursive=True)
        return rc_a, rc_r, d_r, rc_arc, _mx, arcx

    _e_ok = fresh_dir(p['rd'], 'e_ok')
    rc_a, rc_r, d_r, rc_arc, _mx, arcx = chain('mapE2E', _e_ok, True)
    _mp = os.path.join(_e_ok, 'MAP_REPORT.md')
    _mt = open(_mp, encoding='utf-8').read() if os.path.exists(_mp) else ''
    _secs = ['一句总判断', '四地三时点环境对照', '各地区环境走位',
             '传导机制', '三个转折', '关键数字与来源', '历史', '语义审查']
    _arc_map = glob.glob(os.path.join(arcx, '**', 'MAP_REPORT.md'),
                         recursive=True)
    _sha_rd = hashlib.sha256(open(_mp, 'rb').read()).hexdigest() \
        if _arc_map else ''
    _sha_ar = hashlib.sha256(open(_arc_map[0], 'rb').read()).hexdigest() \
        if _arc_map else ''
    check('§E 正例全链 → 交付+归档1份+读者报告五面俱全',
          rc_a == 0 and rc_r == 0 and d_r.get('deliverable') is True
          and rc_arc == 0 and len(_mx) == 1
          and all(s in _mt for s in _secs),
          f"a={rc_a} r={rc_r} dlv={d_r.get('deliverable')} arc={rc_arc} "
          f"mx={len(_mx)} secs={[s for s in _secs if s not in _mt]}")
    check('§E 归档回读 SHA-256 与读者文件逐位一致',
          bool(_arc_map) and _sha_rd == _sha_ar and len(_sha_ar) == 64,
          f"rd={_sha_rd[:12]} arc={_sha_ar[:12]}")

    _t = fresh_dir(p['rd'], 'e_tamper')
    chain('mapTamperPre', _t, True)
    open(os.path.join(_t, 'MAP_REPORT.md'), 'w', encoding='utf-8').write(
        '# 篡改版读者报告(单改在场文件)\n')
    rc_rt, d_rt = cli_stage('report', _t, eroot)
    rc_at, _ = cli_stage('archive', _t, eroot,
                         arc=os.path.join(ARC, 'mapTamper'))
    _mxt = glob.glob(os.path.join(ARC, 'mapTamper', '**',
                                  'ARCHIVE_MANIFEST.json'), recursive=True)
    check('§E 篡改 MAP_REPORT(≠旁挂锚) → 拒交付+拒归档+不洗白',
          d_rt.get('deliverable') is not True and rc_at != 0 and not _mxt
          and open(os.path.join(_t, 'MAP_REPORT.md'),
                   encoding='utf-8').read().startswith('# 篡改版'),
          f"dlv={d_rt.get('deliverable')} arc={rc_at} mx={len(_mxt)}")
    os.remove(os.path.join(_t, 'MAP_REPORT.md'))
    rc_rr, d_rr = cli_stage('report', _t, eroot)
    check('§E 篡改恢复(删除单改文件) → 重渲交付(合法修订通道不误伤)',
          rc_rr == 0 and d_rr.get('deliverable') is True,
          f"rc={rc_rr} dlv={d_rr.get('deliverable')}")

    _m = fresh_dir(p['rd'], 'e_missing')
    chain('mapMissingPre', _m, True)
    os.remove(os.path.join(_m, 'MAP_REPORT.md'))
    sys.path.insert(0, ROOT)
    import ia_cli as _iac
    _orig = _iac._r1_report_core
    _iac._r1_report_core = lambda *a, **k: (True, {'deliverable': True,
                                                   'review': {'ok': True}}, [])
    try:
        _okm, _dm, _ = _iac._r1_archive_core(
            types.SimpleNamespace(report_dir=_m,
                                  archive_dir=os.path.join(ARC, 'mapMiss')),
            eroot)
    finally:
        _iac._r1_report_core = _orig
    check('§E MAP_REPORT 缺席 → 归档 blocked=map_required_face_missing',
          _okm is False
          and _dm.get('blocked') == 'map_required_face_missing',
          f"ok={_okm} blocked={_dm.get('blocked')}")

    _e_only = fresh_dir(p2['rd'], 'e_only')
    rc_a4, rc_r4, d_r4, rc_arc4, _mx4, _ = chain(
        'onlyE2E', _e_only, True, judgment=map_judgment(p2['rd']))
    check('§E 只比较正例 → 全链交付+归档(两项都保留才放行)',
          rc_a4 == 0 and rc_r4 == 0 and d_r4.get('deliverable') is True
          and rc_arc4 == 0 and len(_mx4) == 1,
          f"a={rc_a4} r={rc_r4} dlv={d_r4.get('deliverable')} "
          f"arc={rc_arc4} mx={len(_mx4)}")
    _neg = fresh_dir(p3['rd'], 'e_onlyneg')
    rc_a5, rc_r5, d_r5, rc_arc5, _mx5, _ = chain(
        'onlyNeg', _neg, False, judgment=map_judgment(_neg))
    check('§E 移除10年反例 → 缺任一项即阻止正式归档(零归档)',
          d_r5.get('deliverable') is not True and rc_arc5 != 0
          and len(_mx5) == 0,
          f"dlv={d_r5.get('deliverable')} arc={rc_arc5} mx={len(_mx5)}")

    # ═══ 判定 ═══════════════════════════════════════════════════════
    n_pass = sum(1 for _, ok, _ in RESULTS if ok)
    n_fail = len(RESULTS) - n_pass
    print(f'\nAudit-R18 判定: {n_pass} PASS / {n_fail} FAIL')
    assert n_fail == 0, f'{n_fail} 项未过: ' + '; '.join(
        n for n, ok, _ in RESULTS if not ok)


eroot = os.path.join(TMPG, 'engine')
os.makedirs(os.path.join(eroot, 'config'))
shutil.copy(os.path.join(ROOT, 'config', 'metric_registry.json'),
            os.path.join(eroot, 'config', 'metric_registry.json'))

test_audit_r18_gate()
sys.exit(0)
