# -*- coding: utf-8 -*-
"""Audit-R16 门测试: 期限值绑定映射 + 「半」完整短语黑名单 + 「外加」连接词。

三缺陷(基线 fe54e0a 复现,见 AUDIT_R16_REPORT.md):
  G1 「2年美债收益率」(无期)不映射 UST_2Y → 三品种比较只答两种;
  G2 「一年半制造业PMI/一年半发生了」半形被单字白名单误杀 → 18 月缩 12 月,
     12 点根误放行;
  G3 「十八个月外加三天」外不在连接词集 → 复合尾部漏过 → 18 月照付。

共享逻辑修(plan 完整记录每个指标+窗口;report/archive 同判):
  A map_entities 增值绑定期限映射(_metric_tenor_map_patterns: 品种+数值+
    单位,期可选,中文数量等价,范围前缀抑制——「过去10年美债」仍十年窗);
  B _QRANGE_RE 半组改词黑名单(半导体/衰[期变]/年度/年报/成品/场/岛/球/径
    之外全部放行——完整短语口径,废除单字后随白名单);
  C _QCONT_RE 连接词 [再又]→[再又外](外加形)。

合成隔离标记: 本文件全部裁决/夹具 role=R16-SYNTHETIC-ISOLATED-TEST,
synthetic:true 顶层双写(离线测试,冻结面=仓内 cn-task-b 宏观档)。"""
import glob
import importlib.util
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

SYN_ROLE = 'R16-SYNTHETIC-ISOLATED-TEST'
SYN_MARK = {'synthetic': True,
            'note': 'R16 离线门测试: 冻结面+正式 CLI,非真实外部数据'}

RESULTS = []


def check(name, ok, detail=''):
    RESULTS.append((name, bool(ok), str(detail)[:200]))
    print(('  ✅ ' if ok else '  ❌ ') + name + (f' — {detail}' if detail else ''),
          flush=True)


# ═══ 冻结面: 仓内 cn-task-b 宏观档(34 指标,UST×3 各 2497 日频 + PMI 226 月频) ═══
_REAL = json.load(open(os.path.join(
    ROOT, 'docs/autonomous-rd/cn-task-b-20261117T083954Z/macro_input/',
    'macro_20261117.json')))


def build_root(mutate):
    """引擎根=仓码+变异冻结面+重建快照(每次更换输入即重建)。"""
    d = tempfile.mkdtemp(prefix='r16gate_')
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


def m_pmi12(doc):
    p = doc['data']['CN_PMI_MFG']
    p['series'] = {'dates': p['series']['dates'][-12:],
                   'values': p['series']['values'][-12:]}
    return doc


def m_drop(key):
    def f(doc):
        doc['data'].pop(key)
        return doc
    return f


def pwin(q, reg_root=None):
    """生产口径: map_entities→_entity_spans→_question_window(同源)。"""
    reg = wd.load_registry(reg_root or ROOT)
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
    items = ((j.get('run') or {}).get('data_requirements') or {}).get('items')
    return {'rc': r.returncode, 'rd': os.path.dirname(c[0]),
            'metrics': ent.get('metrics'),
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
    """合规判决(证据引用取该 plan 真实 evidence_index 的 UST 面)。"""
    rep = json.load(open(os.path.join(rd, 'report.json'), encoding='utf-8'))
    refs = [e['ref'] for e in rep.get('evidence_index') or []
            if e.get('metric_id') in ('UST_2Y', 'UST_10Y', 'UST_30Y')][:2] \
        or ['UST_2Y@2026-11-13']
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
                     'falsification_metric': 'UST_10Y'}]}]},
        'l4': {'scenarios': [
            {'id': 'SCN-A', 'role': '基准', 'rows': {
                'scenario': '情景A(假设非预测): 合成基准',
                'asset_direction': {'direction': '上行',
                                    'confidence_tier': '有相关证据',
                                    'text': '合成方向', 'evidence_refs': refs},
                'sensitive_variables': ['UST_2Y'],
                'falsification': {'metric_id': 'UST_10Y',
                                  'threshold': '突破合成阈值 4.5'},
                'trigger': {'condition': '合成可观测条件',
                            'deadline': '2027-06-30'}}},
            {'id': 'SCN-B', 'role': '反例', 'rows': {
                'scenario': '情景B(假设非预测): 合成反例',
                'asset_direction': {'direction': '区间',
                                    'confidence_tier': '纯逻辑推理',
                                    'text': '合成反例方向', 'evidence_refs': []},
                'sensitive_variables': ['UST_10Y'],
                'falsification': {'metric_id': 'UST_2Y',
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


def make_run(name, question, req_item):
    """隔离夹具 run(交付面验证): 正式 plan 的判定项原样带入。

    R17 起单指标问句 S7 模式门不适用=诚实豁免(正式链贯通,见
    test_audit_r17_gate);本夹具仍用于判定面复用(G2/G3 判定带入)。"""
    make_run.seq += 1
    rd = os.path.join(TMPG, name)
    os.makedirs(rd, exist_ok=True)
    rows = [{'metric_id': 'TEST_M%d' % i, 'value': 1.0 * i, 'unit': 'x',
             'observation_date': '2026-11-09', 'quality_status': 'OK',
             'source': {'id': 'src%d' % i, 'kind': 'synthetic'}}
            for i in range(2)]
    report = {
        'schema_version': '2.0', 'pipeline_version': 't',
        'run': {'question': question,
                'ts_utc': '20261119T01%04dZ' % make_run.seq,
                'git_head': 'synthetic-isolated-test',
                'degradation_policy': {}},
        'steps': [], 'fanout': {},
        'layers': {
            'L1_事实层': {'rows': rows, 'available': True, 'n': 2,
                         'note': '合成: 无事实行'},
            'L2_机构观点层': {'views': {'available': False, 'n': 0,
                                        'note': '合成: 观点库缺席'}},
            'L3_AI推断层': {'produced': True, 'attribution': 'ai_inferred',
                           'note': '合成: L3 注记'},
            'L4_条件情景层': {'produced': True, 'attribution': 'ai_inferred',
                           'note': '合成: L4 注记'}},
        'evidence_index': [{'kind': 'metric', 'ref': 'TEST_M0@2026-11-09'},
                           {'kind': 'metric', 'ref': 'TEST_M1@2026-11-09'}],
        'notes': [], 'run_ok': True,
        'agent_judgment': {
            'attached': True, 'judgment_file': 'judgment.json',
            'validation': {'passed': True, 'violations': []},
            'run_ok_at_attach': True, 'allow_failed_run': False}}
    report['run']['data_requirements'] = {
        'frozen_at': 'plan(采集前冻结;分类与规格不随采集结果改判)',
        'items': [req_item], 'optional_face': {'tier': 'optional'}}
    json.dump(report, open(os.path.join(rd, 'report.json'), 'w',
                           encoding='utf-8'), ensure_ascii=False)
    jd = {'schema_version': aj.JUDGMENT_SCHEMA_VERSION,
          'agent_declaration': dict(role=SYN_ROLE, **SYN_MARK),
          'l3': {'claims': []}, 'l4': {'scenarios': []}}
    jd.update(SYN_MARK)
    json.dump(jd, open(os.path.join(rd, 'agent_judgment.json'), 'w',
                       encoding='utf-8'), ensure_ascii=False)
    open(os.path.join(rd, 'report.md'), 'w', encoding='utf-8').write(
        ro._render_md(report))
    json.dump({'n': 1, 'note': 'views 库在场', 'views': [
        {'view_id': 'V-2026-001', 'institution_name': '机构A',
         'publish_date': '2026-11-01', 'report_title': '标题',
         'core_views': ['主张'], 'forecasts': [], 'risk_factors': []}]},
        open(os.path.join(rd, 'views_digest.json'), 'w', encoding='utf-8'),
        ensure_ascii=False)
    return rd


make_run.seq = 0


TMPG = tempfile.mkdtemp(prefix='r16gate_')
eroot = os.path.join(TMPG, 'engine')
os.makedirs(os.path.join(eroot, 'config'))
shutil.copy(os.path.join(ROOT, 'config', 'metric_registry.json'),
            os.path.join(eroot, 'config', 'metric_registry.json'))
ARC = os.path.join(TMPG, 'research_archive')

UST3 = ['UST_2Y', 'UST_10Y', 'UST_30Y']
Q_G1 = '比较过去六个月2年美债收益率、10年期美债收益率和30年期美债收益率的走势'
Q_G2 = ['过去一年半制造业PMI有什么变化（CN_PMI_MFG）？',
        '过去一年半的制造业PMI有什么变化（CN_PMI_MFG）？',
        'CN_PMI_MFG 在过去一年半发生了哪些变化？']


def test_audit_r16_gate():
    # ═══ §A G1 期限值绑定映射(列举变体+抑制锚) ═════════════════════
    print('§A G1 期限映射(品种+数值+单位)')
    for tag, q in (('A 原句2年无期', Q_G1),
                   ('A 换2年期全形',
                    '比较过去六个月2年期美债收益率、10年期美债收益率和'
                    '30年期美债收益率的走势'),
                   ('A 顺序调整',
                    '比较过去六个月10年期美债收益率、30年期美债收益率和'
                    '2年美债收益率的走势'),
                   ('A 附指标ID',
                    '比较过去六个月UST_2Y、UST_10Y和UST_30Y的走势')):
        w, ent = pwin(q)
        check(f'§A {tag} → 三品种全映射+六月窗',
              sorted(set(ent['metrics'])) == sorted(UST3)
              and w.get('kind') == 'relative_months' and w.get('months') == 6,
              f"mets={ent['metrics']} kind={w.get('kind')} "
              f"months={w.get('months')}")
    for tag, q, yy in (('过去10年美债', '过去10年美债收益率走势', 10),
                       ('近2年美债', '近2年美债收益率走势', 2),
                       ('最近30年美债', '最近30年美债收益率怎么样', 30)):
        w, ent = pwin(q)
        check(f'§A 抑制 {tag} → 不凭空命中+N年窗',
              not ent['metrics'] and w.get('kind') == 'relative'
              and w.get('years') == yy,
              f"mets={ent['metrics']} years={w.get('years')}")

    # ═══ §B G2 「半」完整短语(黑名单口径)+既有半词锚 ═══════════════
    print('§B G2 一年半三形+半词锚')
    for i, q in enumerate(Q_G2):
        w, ent = pwin(q)
        check(f'§B 一年半形{i + 1} → 18 月+PMI 命中',
              ent['metrics'] == ['CN_PMI_MFG']
              and w.get('kind') == 'relative_months' and w.get('months') == 18,
              f"mets={ent['metrics']} months={w.get('months')}")
    _w, _ = pwin('分析过去三年半导体需求与 CN_PMI_MFG 的关系')
    check('§B 锚 三年半导体 → 36 月(三年不被半裂)',
          _w.get('kind') == 'relative' and _w.get('years') == 3,
          f"kind={_w.get('kind')} years={_w.get('years')}")
    _w, _ = pwin('研究过去三年半 CN_PMI_MFG 的变化')
    check('§B 锚 三年半 → 42 月', _w.get('months') == 42,
          f"months={_w.get('months')}")
    for tag, q in (('半衰期', '过去一年半衰期数据怎么样?'),
                   ('半年度', '过去一年半年度数据怎么样?'),
                   ('半成品', '过去一年半成品产量如何?')):
        _w, _ = pwin(q)
        check(f'§B 锚 {tag} → 一年(词黑名单不裂)',
              _w.get('kind') == 'relative' and _w.get('years') == 1,
              f"kind={_w.get('kind')} years={_w.get('years')}")
    _w, _ = pwin('过去一年半年报披露的情况?')
    check('§B 锚 半年报 → 既档拒绝(unparseable)',
          _w.get('kind') == 'unparseable', f"kind={_w.get('kind')}")
    _w, _ = pwin('过去六个月半导体销售怎么样?')
    check('§B 锚 六个月半导体 → 六月窗不裂', _w.get('months') == 6,
          f"months={_w.get('months')}")

    # ═══ §C G3 连接词(外加+既档复合族) ═════════════════════════════
    print('§C G3 追加三天')
    for tag, q in (('外加三天', '过去十八个月外加三天的CN_PMI_MFG走势如何?'),
                   ('加三天', '过去十八个月加三天的CN_PMI_MFG走势如何?'),
                   ('又加上三天', '过去十八个月又加上三天的CN_PMI_MFG走势?'),
                   ('零三天', '过去一年半零三天的CN_PMI_MFG如何?'),
                   ('零三个工作日',
                    '过去十八个月零三个工作日的CN_PMI_MFG如何?'),
                   ('零三个交易日',
                    '过去十八个月零三个交易日的CN_PMI_MFG如何?'),
                   ('又加上一个工作日',
                    '研究过去十八个月又加上一个工作日 CN_PMI_MFG 的变化'),
                   ('零一季度', '研究过去十八个月零一季度 CN_PMI_MFG 的变化')):
        _w = ro._question_window(q)
        check(f'§C {tag} → 拒绝(提示改写)', _w.get('kind') == 'unparseable',
              f"kind={_w.get('kind')}")
    _w, _ = pwin('过去十八个月的CN_PMI_MFG走势如何?')
    check('§C 净十八个月 → 18 月正常', _w.get('months') == 18,
          f"months={_w.get('months')}")

    # ═══ §D 正式 plan 集成(冻结根×案变异,逐项指标/窗/覆盖) ═════════
    print('§D 正式 plan 集成(冻结面+正式 CLI)')
    r_full = build_root(m_full)
    r_p12 = build_root(m_pmi12)
    r_n2 = build_root(m_drop('UST_2Y'))

    p = plan_run(r_full, 'G1full', Q_G1)
    _ok = p is not None and sorted(set(p['metrics'])) == sorted(UST3)
    for it in p['items'] if p else []:
        _w = (it.get('spec') or {}).get('window') or {}
        _ok = _ok and it.get('outcome') == 'satisfied' \
            and _w.get('start') == '2026-05-17' and _w.get('end') == '2026-11-17' \
            and _w.get('n_in_window') == 124
    check('§D G1 全数据 → 三项各 124 窗内观测+窗日期逐位', _ok,
          f"mets={p and p['metrics']} items={[(i.get('metric_id'), (i.get('spec') or {}).get('window', {}).get('n_in_window'), i.get('outcome')) for i in (p and p['items'] or [])]}")

    p2 = plan_run(r_n2, 'G1no2y', Q_G1)
    _i2 = {(i.get('metric_id')): i for i in (p2['items'] if p2 else [])}
    _w2 = ((_i2.get('UST_2Y') or {}).get('spec') or {}).get('window') or {}
    check('§D G1 移除2年 → 仍列该项+要求窗原样+缺数阻断',
          p2 is not None and sorted(set(p2['metrics'])) == sorted(UST3)
          and _i2.get('UST_2Y', {}).get('outcome') == 'insufficient_coverage'
          and _w2.get('start') == '2026-05-17'
          and _w2.get('end') == '2026-11-17'
          and _w2.get('n_in_window') is None
          and _i2.get('UST_10Y', {}).get('outcome') == 'satisfied'
          and _i2.get('UST_30Y', {}).get('outcome') == 'satisfied',
          f"mets={p2 and p2['metrics']} "
          f"outcomes={ {k: v.get('outcome') for k, v in _i2.items()} }")

    for tag, root, exp in (('完整226点', r_full, True),
                           ('只给12观测', r_p12, False)):
        pp = plan_run(root, 'G2_' + ('f' if exp else 'p'), Q_G2[0])
        it = (pp['items'] or [{}])[0]
        _w = (it.get('spec') or {}).get('window') or {}
        check(f'§D G2 {tag} → 窗 2025-05-17..2026-11-17+'
              f'{"17 点满足" if exp else "缺数拒绝(不缩窗)"}',
              pp is not None and pp['metrics'] == ['CN_PMI_MFG']
              and _w.get('start') == '2025-05-17'
              and _w.get('end') == '2026-11-17'
              and _w.get('n_in_window') == (17 if exp else 12)
              and (it.get('outcome') == ('satisfied' if exp
                                         else 'insufficient_coverage')),
              f"w={_w.get('start')}..{_w.get('end')} "
              f"n={_w.get('n_in_window')} outcome={it.get('outcome')}")
        if not exp:
            check('§D G2 整项状态记录(R17 起: 单指标 S7 模式门不适用='
                  '诚实豁免,run_ok 不因门缺席翻 False)',
                  pp.get('run_ok') is True,
                  f"run_ok={pp.get('run_ok')}(S7_mode_gate 单指标"
                  f"honest_refusal 豁免,R17 契约)")

    pg = plan_run(r_full, 'G3', '过去十八个月外加三天的CN_PMI_MFG走势如何?')
    itg = (pg['items'] or [{}])[0]
    _wg = (itg.get('spec') or {}).get('window') or {}
    check('§D G3 外加三天 → 无法完整解析+提示改写',
          pg is not None and itg.get('outcome') == 'insufficient_coverage'
          and '无法完整解析' in (_wg.get('basis') or '')
          and '不缩短范围' in (_wg.get('basis') or ''),
          f"outcome={itg.get('outcome')} "
          f"basis={(_wg.get('basis') or '')[:60]}")

    # ═══ §E 交付面: G1 正式全链 + PMI/G3 判定带入隔离夹具 ═══════════
    print('§E 交付面(attach→report→archive)')
    rc_a, d_a = cli_stage('attach', p['rd'], eroot,
                          judgment=valid_judgment(p['rd']))
    aj.record_semantic_verdict(eroot, p['rd'], 'UPHELD', SYN_ROLE)
    rc_r, d_r = cli_stage('report', p['rd'], eroot)
    arc1 = os.path.join(ARC, 'G1full')
    rc_arc, _ = cli_stage('archive', p['rd'], eroot, arc=arc1)
    _mans = glob.glob(os.path.join(arc1, '**', 'ARCHIVE_MANIFEST.json'),
                      recursive=True)
    check('§E G1 正式全链 → attach 落位+report rc=0 交付+归档 1 份',
          rc_a == 0 and os.path.isfile(os.path.join(p['rd'],
                                                    'agent_judgment.json'))
          and rc_r == 0 and d_r.get('deliverable') is True
          and rc_arc == 0 and len(_mans) == 1,
          f"attach={rc_a} report={rc_r} dlv={d_r.get('deliverable')} "
          f"archive={rc_arc} manifests={len(_mans)}")

    _FIX = [
        ('正例 226 点', (plan_run(r_full, 'E226', Q_G2[0])['items'] or [{}])[0],
         True),
        ('反例 12 点', (plan_run(r_p12, 'E12', Q_G2[0])['items'] or [{}])[0],
         False),
        ('反例 外加三天', itg, False),
        ('反例 加三天',
         (plan_run(r_full, 'Ejia',
                   '过去十八个月加三天的CN_PMI_MFG走势如何?'
                   )['items'] or [{}])[0], False),
    ]
    for k, (tag, item, pos) in enumerate(_FIX):
        rd = make_run('e%d' % k, Q_G2[0] if '例' in tag else
                      ('过去十八个月外加三天的CN_PMI_MFG走势如何?'
                       if '外加' in tag else
                       '过去十八个月加三天的CN_PMI_MFG走势如何?'), item)
        aj.record_semantic_verdict(eroot, rd, 'UPHELD', SYN_ROLE)
        rc_r2, d_r2 = cli_stage('report', rd, eroot)
        arcx = os.path.join(ARC, 'fix%d' % k)
        rc_arc2, _ = cli_stage('archive', rd, eroot, arc=arcx)
        _mx = glob.glob(os.path.join(arcx, '**', 'ARCHIVE_MANIFEST.json'),
                        recursive=True)
        if pos:
            check(f'§E 夹具 {tag} → report rc=0+归档 1 份',
                  rc_r2 == 0 and d_r2.get('deliverable') is True
                  and rc_arc2 == 0 and len(_mx) == 1,
                  f"report={rc_r2} dlv={d_r2.get('deliverable')} "
                  f"archive={rc_arc2} manifests={len(_mx)}")
        else:
            check(f'§E 夹具 {tag} → 非零退出+零归档',
                  rc_r2 != 0 and d_r2.get('deliverable') is not True
                  and rc_arc2 != 0 and len(_mx) == 0,
                  f"report={rc_r2} dlv={d_r2.get('deliverable')} "
                  f"archive={rc_arc2} manifests={len(_mx)}")

    # ═══ §F 参数化回归电池(映射+窗口面,正反例逐案) ═════════════════
    print('§F 参数化回归电池')
    _BAT = [
        # (tag, q, exp_metrics, exp_face)  face: ('m',N)=月 /('y',N)=年 /
        #   'bad'=unparseable / 'unset'=None
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
        ('数值绑定不越5年', '过去六个月2年美债收益率走势如何?', [], None),
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
        if tag == '数值绑定不越5年':
            continue                    # 占位(与上重复,数值绑定已双证)
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
        ok = ok and (exp_m is None or sorted(set(exp_m))
                     == sorted(set(ent['metrics'])))
        check(f'§F {tag} → 指标集+窗口逐位', ok,
              f"mets={ent['metrics']} {det}")

    # ═══ 判定 ═══════════════════════════════════════════════════════
    n_pass = sum(1 for _, ok, _ in RESULTS if ok)
    n_fail = len(RESULTS) - n_pass
    print(f'\nAudit-R16 判定: {n_pass} PASS / {n_fail} FAIL')
    assert n_fail == 0, f'{n_fail} 项未过: ' + '; '.join(
        n for n, ok, _ in RESULTS if not ok)


test_audit_r16_gate()
sys.exit(0)
