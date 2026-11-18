# -*- coding: utf-8 -*-
"""Audit-R17 门测试: 共用名并列绑定 + 「只比较」限定 + 空格前缀抑制 +
「另加」连接词 + 缺数项写明缺什么 + 单指标 S7 模式门豁免。

三缺陷(基线 264dc14 复现,见 AUDIT_R17_REPORT.md):
  G1 并列共用名「2年期和10年期美债收益率」只映射尾部紧邻品种的期限 →
     省写缺 UST_2Y、调换顺序缺 UST_10Y;
  G2 「过去 2年」空格击穿固定宽度 lookbehind 前缀抑制 → UST_2Y 误入必需集
     (「只比较」限定缺位,三空格形必需集不一);
  G3 「另加」不在连接词集 → 「十八个月另加三天」复合尾部漏过 → 18 月照付。
产品验收(a): 单指标 PMI 问句 S7_mode_gate 无可比对=非豁免红(run_ok=False
→attach 拒收)——查清该前置检查不适用于单指标问句(无可比性要求),
诚实豁免镜像 S6。

共享逻辑修(缺数项保留在计划并写明缺什么;plan/report/archive 同一份判定):
  D _metric_tenor_map_patterns 并列中段(和|及|与|、|或)+数量+单位,共用
    品种名绑定每个期限(不跨产品——中段断裂即不绑);
  E map_entities 位置感知+「只比较/仅比较」限定必需指标;
  F 范围前缀抑制改命中时检查(容忍空格,研究时长与期限各自识别);
  G _QCONT_RE 连接词 [再又外]→[再又外另];
  H _evaluate_data_requirements 缺数项 outcome_basis 前缀「缺什么: <mid>」;
  I S7_mode_gate 单指标 honest_refusal 豁免。

合成隔离标记: 本文件全部裁决/夹具 role=R17-SYNTHETIC-ISOLATED-TEST,
synthetic:true 顶层双写(离线测试,冻结面=仓内 cn-task-b 宏观档)。"""
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
import research_orchestrator as ro    # noqa: E402
import snapshot_builder as sb         # noqa: E402
import workbench_data as wd           # noqa: E402

SYN_ROLE = 'R17-SYNTHETIC-ISOLATED-TEST'
SYN_MARK = {'synthetic': True,
            'note': 'R17 离线门测试: 冻结面+正式 CLI,非真实外部数据'}

RESULTS = []


def check(name, ok, detail=''):
    RESULTS.append((name, bool(ok), str(detail)[:200]))
    print(('  ✅ ' if ok else '  ❌ ') + name + (f' — {detail}' if detail else ''),
          flush=True)


# ═══ 冻结面: 仓内 cn-task-b 宏观档(34 指标,UST×3 各 2497 日频 + PMI 226 月频) ═══
_REAL = json.load(open(os.path.join(
    ROOT, 'docs/autonomous-rd/cn-task-b-20261117T083954Z/macro_input/',
    'macro_20261117.json')))
TMPG = tempfile.mkdtemp(prefix='r17gate_')
ARC = os.path.join(TMPG, 'research_archive')


def build_root(mutate, china=False):
    """引擎根=仓码+变异冻结面+重建快照(每次更换输入即重建)。

    china=True 补全 CN 输入面(冻结档 CN 条目按 normalize_china 契约
    data.macro.<key> 写 china_20261117.json)——事实权威=china_market_
    collector(注册表 source 门);不补则 CN 族 L1 事实面缺席(输入面
    性质,非代码缺陷;单指标 PMI 正常入口交付验证用)。"""
    d = tempfile.mkdtemp(prefix='r17gate_')
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
    if china:
        _CK = {'pmi_mfg': 'CN_PMI_MFG', 'omo_7d': 'CN_OMO_7D',
               'lpr_1y': 'CN_LPR_1Y', 'lpr_5y': 'CN_LPR_5Y',
               'cpi_yoy': 'CN_CPI_YOY', 'ppi_yoy': 'CN_PPI_YOY',
               'sf_flow': 'CN_SF_FLOW', 'new_loans': 'CN_NEW_LOANS'}
        mac = {}
        for k, mid in _CK.items():
            e = (doc.get('data') or {}).get(mid)
            if isinstance(e, dict) and e.get('value') is not None:
                mac[k] = {'value': e.get('value'), 'date': e.get('date')}
        json.dump({'macro': mac}, open(os.path.join(dd, 'china_20261117.json'),
                                       'w', encoding='utf-8'),
                  ensure_ascii=False)
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


def pwin(q):
    """生产口径: map_entities→_entity_spans→_question_window(同源)。"""
    reg = wd.load_registry(ROOT)
    ent = ro.map_entities(q, reg)
    return ro._question_window(
        q, ro._entity_spans(q, reg['by_id'], ent['metrics'])), ent


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
    s7 = next((s for s in steps if s.get('step') == 'S7_mode_gate'), {})
    items = ((j.get('run') or {}).get('data_requirements') or {}).get('items')
    return {'rc': r.returncode, 'rd': os.path.dirname(c[0]),
            'metrics': ent.get('metrics'),
            's7': s7,
            'items': items or [], 'run_ok': j.get('run_ok')}


def cli_stage(stage, rd, engine_root, arc=None, judgment=None, timeout=180):
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
        data = {'raw': (r.stdout or r.stderr or '')[-160:]}
    return r.returncode, data


def valid_judgment(rd):
    """合规判决 v2(证伪/敏感/引用指标派生自该 plan **在场**证据面——
    契约验证「证伪指标可观测」硬拦缺席指标,移除某序列的根判决不得再
    引用它)。"""
    rep = json.load(open(os.path.join(rd, 'report.json'), encoding='utf-8'))
    ev = rep.get('evidence_index') or []
    present = [m for m in ('UST_2Y', 'UST_10Y', 'UST_30Y', 'CN_PMI_MFG')
               if any(e.get('metric_id') == m for e in ev)]
    if not present:
        present = [e.get('metric_id') for e in ev
                   if e.get('metric_id')][:1] or ['CN_PMI_MFG']
    m1 = present[0]
    m2 = present[1] if len(present) > 1 else present[-1]
    refs = [e['ref'] for e in ev if e.get('metric_id') in (m1, m2)][:2] \
        or [f'{m1}@2026-11-13']
    jd = {
        'schema_version': '1.1',
        'agent_declaration': {'attribution': 'ai_inferred',
                              'note': '合成判决(离线门测试)', **SYN_MARK},
        'l3': {
            'contradictions': [{
                'id': 'CON-1', 'statement': '合成矛盾陈述(离线门测试)',
                'basis': '基于证据索引的推断',
                'competing_explanations': ['解释一(基准)', '解释二(反例)'],
                'evidence_refs': refs}],
            'mechanism_chains': [{
                'id': 'MECH-1', 'name': '合成链',
                'links': [
                    {'step': 1, 'text': 'E1 环(引擎可验证)',
                     'evidence_level': 'E1', 'evidence_refs': refs},
                    {'step': 2, 'text': 'E2 环(部分支持)',
                     'evidence_level': 'E2',
                     'missing_link_note': '本环为【假设】: 合成缺环注记(离线)',
                     'evidence_refs': refs},
                    {'step': 3, 'text': 'E3 环(纯叙事)',
                     'evidence_level': 'E3',
                     'falsification_metric': m2}]}]},
        'l4': {'scenarios': [
            {'id': 'SCN-A', 'role': '基准', 'rows': {
                'scenario': '情景A(假设非预测): 合成基准',
                'asset_direction': {'direction': '上行',
                                    'confidence_tier': '有相关证据',
                                    'text': '合成方向', 'evidence_refs': refs},
                'sensitive_variables': [m1],
                'falsification': {'metric_id': m2,
                                  'threshold': '突破合成阈值 4.5'},
                'trigger': {'condition': '合成可观测条件',
                            'deadline': '2027-06-30'}}},
            {'id': 'SCN-B', 'role': '反例', 'rows': {
                'scenario': '情景B(假设非预测): 合成反例',
                'asset_direction': {'direction': '区间',
                                    'confidence_tier': '纯逻辑推理',
                                    'text': '合成反例方向', 'evidence_refs': []},
                'sensitive_variables': [m2],
                'falsification': {'metric_id': m1,
                                  'threshold': '跌破合成阈值 2.5'},
                'trigger': {'condition': '合成反例条件',
                            'deadline': '2027-06-30'}}}]},
    }
    jd.update(SYN_MARK)
    jp = os.path.join(TMPG, 'jd_%d.json' % valid_judgment.seq)
    valid_judgment.seq += 1
    json.dump(jd, open(jp, 'w', encoding='utf-8'), ensure_ascii=False)
    return jp


valid_judgment.seq = 0

Q1 = ['过去半年，2年期和10年期美债收益率各变了多少？30年期美债收益率也同向吗？',
      '过去半年，2年期美债收益率和10年期美债收益率各变了多少？30年期美债收益率也同向吗？',
      '过去半年，10年期和2年期美债收益率各变了多少？30年期美债收益率也同向吗？']
Q2 = ['过去2年美债收益率怎样变化？只比较10年期美债收益率和30年期美债收益率。',
      '过去 2年美债收益率怎样变化？只比较10年期美债收益率和30年期美债收益率。',
      '过去  2年美债收益率怎样变化？只比较10年期美债收益率和30年期美债收益率。']
Q3 = ['过去十八个月另加三天，10年期美债收益率走势如何？',
      '过去十八个月外加三天，10年期美债收益率走势如何？',
      '过去十八个月加三天，10年期美债收益率走势如何？']
Q_PMI = '过去一年半制造业PMI有什么变化？'
UST3 = ['UST_2Y', 'UST_10Y', 'UST_30Y']


def test_audit_r17_gate():
    reg = wd.load_registry(ROOT)

    # ═══ §A 映射: 共用名并列 + 只比较 + 空格前缀抑制 ═════════════════
    print('§A 映射(共用名并列/只比较/空格)')
    for i, q in enumerate(Q1):
        _q = ['省写共用名', '写全品种名', '调换顺序'][i]
        w, ent = pwin(q)
        check(f'§A G1 {_q} → 三期限全映射+六月窗',
              sorted(set(ent['metrics'])) == sorted(UST3)
              and w.get('kind') == 'relative_months'
              and w.get('months') == 6,
              f"mets={ent['metrics']} months={w.get('months')}")
    for i, q in enumerate(Q2):
        _q = ['无空格', '中空格', '双空格'][i]
        w, ent = pwin(q)
        check(f'§A G2 {_q} → 只比较限定 [10Y,30Y]+两年窗(空格不改变含义)',
              sorted(set(ent['metrics'])) == ['UST_10Y', 'UST_30Y']
              and w.get('kind') == 'relative' and w.get('years') == 2,
              f"mets={ent['metrics']} years={w.get('years')}")
    _supp = [('过去 2年美债收益率怎样变化？', 2),
             ('过去  2年美债收益率走势？', 2),
             ('过去10年美债收益率走势', 10),
             ('近2年美债收益率怎样？', 2),
             ('最近30年美债收益率走势？', 30)]
    for q, yy in _supp:
        w, ent = pwin(q)
        check(f'§A 抑制锚「{q[:9]}…」→ 不凭空映射+{yy}年窗',
              ent['metrics'] == [] and w.get('kind') == 'relative'
              and w.get('years') == yy,
              f"mets={ent['metrics']} years={w.get('years')}")
    w, ent = pwin('2年美债收益率怎样变化？')
    check('§A 裸「2年美债收益率」→ 映射 UST_2Y(无前缀=期限读法)',
          ent['metrics'] == ['UST_2Y'], f"mets={ent['metrics']}")
    w, ent = pwin('2年期国债和10年期美债收益率怎样变化？')
    check('§A 并列不跨产品 → 首段随「国债」断裂,只映射 UST_10Y',
          ent['metrics'] == ['UST_10Y'], f"mets={ent['metrics']}")
    w, ent = pwin('只比较2年期美债收益率和10年期美债收益率')
    check('§A 只比较全后置 → 限定不落空,两期限都在必需集',
          sorted(set(ent['metrics'])) == ['UST_10Y', 'UST_2Y'],
          f"mets={ent['metrics']}")
    w, ent = pwin('过去 3年美债收益率怎样变化？仅比较10年期美债收益率。')
    check('§A 仅比较形 → [10Y]+三年窗',
          ent['metrics'] == ['UST_10Y'] and w.get('kind') == 'relative'
          and w.get('years') == 3,
          f"mets={ent['metrics']} years={w.get('years')}")

    # ═══ §B 窗口: 复合尾部整体拒绝(另加/外加/加) ═════════════════════
    print('§B 复合尾部(完整处理所有明确时间分量)')
    for i, q in enumerate(Q3):
        w, ent = pwin(q)
        check(f'§B G3 {["另加", "外加", "加"][i]}三天 → 无法完整解析'
              f'(不缩短范围,提示改写)',
              w.get('kind') == 'unparseable'
              and '无法完整解析' in (w.get('reason') or ''),
              f"kind={w.get('kind')} reason={(w.get('reason') or '')[:50]}")
    w, ent = pwin('过去十八个月，10年期美债收益率走势如何？')
    check('§B 净十八月 → 18 月窗正常解析',
          w.get('kind') == 'relative_months' and w.get('months') == 18,
          f"months={w.get('months')}")

    # ═══ §C 正式 plan: 指标/窗口/覆盖判定/缺什么 ═════════════════════
    print('§C 正式 plan(冻结根×案变异,每次更换输入重建快照)')
    r_full = build_root(m_full)
    r_n2 = build_root(m_drop('UST_2Y'))
    r_n10 = build_root(m_drop('UST_10Y'))
    r_cn = build_root(m_full, china=True)      # CN 输入面补全根(PMI 交付)

    p = plan_run(r_full, 'G1full', Q1[0])
    _it = {i.get('metric_id'): i for i in (p and p['items'] or [])}
    _ok = (p is not None and sorted(set(p['metrics'])) == sorted(UST3)
           and all(
               ((_it.get(m) or {}).get('spec') or {}).get('window', {})
               .get('start') == '2026-05-17'
               and ((_it.get(m) or {}).get('spec') or {}).get('window', {})
               .get('end') == '2026-11-17'
               and ((_it.get(m) or {}).get('spec') or {}).get('window', {})
               .get('n_in_window') == 124
               and (_it.get(m) or {}).get('outcome') == 'satisfied'
               for m in UST3))
    check('§C G1 省写共用名 → 三项各 124 窗内观测+窗日期逐位',
          _ok and p.get('run_ok') is True,
          f"mets={p and p['metrics']} n={[(m, ((_it.get(m) or {}).get('spec') or {}).get('window', {}).get('n_in_window'), (_it.get(m) or {}).get('outcome')) for m in UST3]} run_ok={p and p.get('run_ok')}")

    p2 = plan_run(r_n2, 'G1no2y', Q1[0])
    _i2 = {i.get('metric_id'): i for i in (p2['items'] if p2 else [])}
    _w2 = ((_i2.get('UST_2Y') or {}).get('spec') or {}).get('window') or {}
    check('§C G1 移除2年 → 仍列该项+要求窗原样+缺数阻断+写明缺什么',
          p2 is not None and sorted(set(p2['metrics'])) == sorted(UST3)
          and _i2.get('UST_2Y', {}).get('outcome') == 'insufficient_coverage'
          and (_i2.get('UST_2Y', {}).get('outcome_basis') or '')
          .startswith('缺什么: UST_2Y')
          and _w2.get('start') == '2026-05-17'
          and _w2.get('end') == '2026-11-17'
          and _w2.get('n_in_window') is None
          and _i2.get('UST_10Y', {}).get('outcome') == 'satisfied'
          and _i2.get('UST_30Y', {}).get('outcome') == 'satisfied',
          f"mets={p2 and p2['metrics']} "
          f"ob={(_i2.get('UST_2Y', {}).get('outcome_basis') or '')[:60]}")

    p3 = plan_run(r_full, 'G2full', Q2[0])
    _i3 = {i.get('metric_id'): i for i in (p3['items'] if p3 else [])}
    _ok3 = (p3 is not None
            and sorted(set(p3['metrics'])) == ['UST_10Y', 'UST_30Y']
            and 'UST_2Y' not in _i3
            and all(
                ((_i3.get(m) or {}).get('spec') or {}).get('window', {})
                .get('start') == '2024-11-17'
                and ((_i3.get(m) or {}).get('spec') or {}).get('window', {})
                .get('end') == '2026-11-17'
                and ((_i3.get(m) or {}).get('spec') or {}).get('window', {})
                .get('n_in_window') == 497
                and (_i3.get(m) or {}).get('outcome') == 'satisfied'
                for m in ('UST_10Y', 'UST_30Y')))
    check('§C G2 无空格 → 只要求 [10Y,30Y]+两年窗+各 497 观测',
          _ok3, f"mets={p3 and p3['metrics']} "
          f"n={[(m, ((_i3.get(m) or {}).get('spec') or {}).get('window', {}).get('n_in_window')) for m in ('UST_10Y', 'UST_30Y')]}")

    p4 = plan_run(r_full, 'G2sp', Q2[1])
    _i4 = {i.get('metric_id'): i for i in (p4['items'] if p4 else [])}
    check('§C G2 中空格 plan 同判 → 必需集/窗口与无空格一致',
          p4 is not None
          and sorted(set(p4['metrics'])) == ['UST_10Y', 'UST_30Y']
          and 'UST_2Y' not in _i4
          and ((_i4.get('UST_10Y') or {}).get('spec') or {})
          .get('window', {}).get('start') == '2024-11-17',
          f"mets={p4 and p4['metrics']}")

    p5 = plan_run(r_n10, 'G2no10y', Q2[0])
    _i5 = {i.get('metric_id'): i for i in (p5['items'] if p5 else [])}
    check('§C G2 移除10年 → 指定期限缺数阻断+写明缺什么(2Y 不在必需集)',
          p5 is not None
          and sorted(set(p5['metrics'])) == ['UST_10Y', 'UST_30Y']
          and 'UST_2Y' not in _i5
          and _i5.get('UST_10Y', {}).get('outcome') == 'insufficient_coverage'
          and (_i5.get('UST_10Y', {}).get('outcome_basis') or '')
          .startswith('缺什么: UST_10Y')
          and _i5.get('UST_30Y', {}).get('outcome') == 'satisfied',
          f"mets={p5 and p5['metrics']} "
          f"ob={(_i5.get('UST_10Y', {}).get('outcome_basis') or '')[:60]}")

    p5b = plan_run(r_n2, 'G2no2y', Q2[0])
    _i5b = {i.get('metric_id'): i for i in (p5b['items'] if p5b else [])}
    check('§C G2 移除无关2年 → 必需集不含 2Y+两指定期限满足(应交付)',
          p5b is not None
          and sorted(set(p5b['metrics'])) == ['UST_10Y', 'UST_30Y']
          and 'UST_2Y' not in _i5b
          and _i5b.get('UST_10Y', {}).get('outcome') == 'satisfied'
          and _i5b.get('UST_30Y', {}).get('outcome') == 'satisfied'
          and p5b.get('run_ok') is True,
          f"mets={p5b and p5b['metrics']} "
          f"outcomes={ {k: v.get('outcome') for k, v in _i5b.items()} }"
          f" run_ok={p5b and p5b.get('run_ok')}")

    pg = plan_run(r_full, 'G3lj', Q3[0])
    itg = (pg['items'] or [{}])[0]
    _wg = (itg.get('spec') or {}).get('window') or {}
    check('§C G3 另加三天 → 无法完整解析+提示改写(计划保留该项)',
          pg is not None and itg.get('outcome') == 'insufficient_coverage'
          and '无法完整解析' in (_wg.get('basis') or '')
          and '不缩短范围' in (_wg.get('basis') or '')
          and (itg.get('outcome_basis') or '').startswith('缺什么: UST_10Y'),
          f"outcome={itg.get('outcome')} "
          f"basis={(_wg.get('basis') or '')[:60]}")

    pp = plan_run(r_cn, 'PMI', Q_PMI)
    itp = (pp['items'] or [{}])[0]
    _wp = (itp.get('spec') or {}).get('window') or {}
    check('§C 单指标 PMI(正常入口) → S7 豁免+run_ok True+17 点满足',
          pp is not None and pp['metrics'] == ['CN_PMI_MFG']
          and pp.get('run_ok') is True
          and (pp['s7'].get('ok') or pp['s7'].get('honest_refusal'))
          and _wp.get('start') == '2025-05-17'
          and _wp.get('end') == '2026-11-17'
          and _wp.get('n_in_window') == 17
          and itp.get('outcome') == 'satisfied',
          f"mets={pp and pp['metrics']} run_ok={pp and pp.get('run_ok')} "
          f"s7ok={pp and pp['s7'].get('ok')} "
          f"s7hr={pp and pp['s7'].get('honest_refusal')} "
          f"n={_wp.get('n_in_window')} outcome={itp.get('outcome')}")

    # ═══ §D 交付面: 正式全链(正例 rc=0+1 份归档;反例非零+0 份) ═══════
    print('§D 交付面(attach→report→archive)')

    def chain(tag, plan, positive):
        rd = plan['rd']
        rc_a, _ = cli_stage('attach', rd, eroot,
                            judgment=valid_judgment(rd))
        if os.path.isfile(os.path.join(rd, 'agent_judgment.json')):
            aj.record_semantic_verdict(eroot, rd, 'UPHELD', SYN_ROLE)
        rc_r, d_r = cli_stage('report', rd, eroot)
        arcx = os.path.join(ARC, tag)
        rc_arc, _ = cli_stage('archive', rd, eroot, arc=arcx)
        _mx = glob.glob(os.path.join(arcx, '**', 'ARCHIVE_MANIFEST.json'),
                        recursive=True)
        if positive:
            check(f'§D {tag} → report rc=0 交付+归档 1 份',
                  rc_r == 0 and d_r.get('deliverable') is True
                  and rc_arc == 0 and len(_mx) == 1,
                  f"attach={rc_a} report={rc_r} dlv={d_r.get('deliverable')} "
                  f"archive={rc_arc} manifests={len(_mx)}")
        else:
            check(f'§D {tag} → report/archive 非零+零归档',
                  rc_r != 0 and d_r.get('deliverable') is not True
                  and rc_arc != 0 and len(_mx) == 0,
                  f"attach={rc_a} report={rc_r} dlv={d_r.get('deliverable')} "
                  f"archive={rc_arc} manifests={len(_mx)}")

    chain('G1full', p, True)            # 美债并列正例
    chain('G2full', p3, True)           # 只比较正例
    chain('G2no2y', p5b, True)          # 移除无关 2Y 仍交付
    pn = plan_run(r_full, 'G3plain', '过去十八个月，10年期美债收益率走势如何？')
    chain('G3plain18', pn, True)        # 净十八月正例
    chain('PMIsingle', pp, True)        # 单指标 PMI 正常入口正例(S7 豁免)
    chain('G1no2y', p2, False)          # 移除指定期限反例
    chain('G3lj', pg, False)            # 另加三天反例

    # ═══ §E 参数化回归电池(既有锚保全,映射+窗口面) ═══════════════════
    print('§E 参数化回归电池(锚保全)')
    _BAT = [
        ('逆回购7天简称', '过去六个月7天逆回购利率走势如何?', ['CN_OMO_7D'],
         ('m', 6)),
        ('逆回购七天中文', '过去六个月七天逆回购利率走势如何?', ['CN_OMO_7D'],
         ('m', 6)),
        ('逆回购全形', '过去六个月央行7天期逆回购利率走势如何?', ['CN_OMO_7D'],
         ('m', 6)),
        ('十年期美债非近十年', '过去六个月十年期美债收益率走势如何?',
         ['UST_10Y'], ('m', 6)),
        ('数值绑定2年', '过去六个月2年美债收益率走势如何?', ['UST_2Y'],
         ('m', 6)),
        ('数值绑定30年', '过去六个月30年美债收益率走势如何?', ['UST_30Y'],
         ('m', 6)),
        ('一年半制造业PMI', '过去一年半制造业PMI有什么变化？',
         ['CN_PMI_MFG'], ('m', 18)),
        ('一年半发生了', 'CN_PMI_MFG 在过去一年半发生了哪些变化？',
         ['CN_PMI_MFG'], ('m', 18)),
        ('三年半导体', '过去三年半导体需求与 CN_PMI_MFG 的关系?',
         ['CN_PMI_MFG'], ('y', 3)),
        ('三年半', '研究过去三年半 CN_PMI_MFG 的变化', ['CN_PMI_MFG'], ('m', 42)),
        ('半年报独立拒绝', '过去半年报的CN_PMI_MFG如何?', ['CN_PMI_MFG'],
         'bad'),
        ('半年度独立拒绝', '过去半年度的CN_PMI_MFG如何?', ['CN_PMI_MFG'],
         'bad'),
        ('半年正形保全', '过去半年，CN_PMI_MFG如何?', ['CN_PMI_MFG'],
         ('m', 6)),
        ('另加三天拒绝', '过去十八个月另加三天CN_PMI_MFG如何?',
         ['CN_PMI_MFG'], 'bad'),
        ('外加三天拒绝', '过去十八个月外加三天CN_PMI_MFG如何?',
         ['CN_PMI_MFG'], 'bad'),
        ('零三个工作日拒绝', '过去十八个月零三个工作日CN_PMI_MFG如何?',
         ['CN_PMI_MFG'], 'bad'),
        ('裸六个月未限定', '六个月CN_PMI_MFG变化?', ['CN_PMI_MFG'], 'unset'),
        ('近7天无产品尾', '近7天的数据怎么样?', [], 'bad'),
        ('2026年内既档', '2026年内的CN_PMI_MFG如何?', ['CN_PMI_MFG'], 'bad'),
        ('十二个月整体', '过去十二个月CN_PMI_MFG如何?', ['CN_PMI_MFG'],
         ('m', 12)),
        ('廿一个月', '过去廿一个月CN_PMI_MFG如何?', ['CN_PMI_MFG'], ('m', 21)),
        ('工作日期护栏', '研究过去三年工作日期安排 CN_PMI_MFG',
         ['CN_PMI_MFG'], ('y', 3)),
    ]
    for tag, q, exp_m, face in _BAT:
        w, ent = pwin(q)
        if isinstance(face, tuple):
            unit, n = face
            if unit == 'm':
                ok = w.get('kind') == 'relative_months' and w.get('months') == n
                det = f"months={w.get('months')}"
            else:
                ok = w.get('kind') == 'relative' and w.get('years') == n
                det = f"years={w.get('years')}"
        elif face == 'bad':
            ok = w.get('kind') == 'unparseable'
            det = f"kind={w.get('kind')}"
        else:
            ok = w is None
            det = f"kind={(w or {}).get('kind')}"
        ok = ok and sorted(set(exp_m)) == sorted(set(ent['metrics']))
        check(f'§E {tag} → 指标集+窗口逐位', ok,
              f"mets={ent['metrics']} {det}")

    # ═══ 判定 ═══════════════════════════════════════════════════════
    n_pass = sum(1 for _, ok, _ in RESULTS if ok)
    n_fail = len(RESULTS) - n_pass
    print(f'\nAudit-R17 判定: {n_pass} PASS / {n_fail} FAIL')
    assert n_fail == 0, f'{n_fail} 项未过: ' + '; '.join(
        n for n, ok, _ in RESULTS if not ok)


eroot = os.path.join(TMPG, 'engine')
os.makedirs(os.path.join(eroot, 'config'))
shutil.copy(os.path.join(ROOT, 'config', 'metric_registry.json'),
            os.path.join(eroot, 'config', 'metric_registry.json'))

test_audit_r17_gate()
sys.exit(0)
