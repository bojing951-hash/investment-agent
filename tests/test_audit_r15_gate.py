#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit-R15(R59) 门: 时间范围与研究对象的边界。

基线 4f9c75d 六缺陷(修复前):
  G1a/G1c 「过去一年半里/期间」→ half 后随 里/期 不在白名单=窗缩 1 年,
     12 点数据按缩窗 satisfied 放行 rc=0/0 已归档(数据不足靠缩短窗口
     通过);G1b「一年半内」基线已正确(白名单有 内);
  G2a 「十八个月零三个工作日」→ 工作日 不在日单位族=按十八个月放行;
  G2c 「十八个月又加上三天」→ 又加上 连接词形逃逸=按十八个月放行;
  G3c 「过去六个月7天逆回购利率(CN_OMO_7D)」→ 期限简称(无期无的)误作
     复合尾部=unparseable 时间解析错误(应=六月窗+命中+缺数如实)。
修复(共享规则,零例句特判):
  ① _QRANGE_RE half 后随白名单扩容(里|期|间|当|中)+后缀组收编
     期间|之中|当中|里(无前缀形也构成约束);
  ② _QCONT_RE 连接词再扩([再又]?加上?)+日单位族扩容(工作/营业/自然日);
  ③ 研究对象先识别: _entity_spans(已映射指标的 id/display_name/期限
     词形正则——数量通配+期可选+中文数量形),复合尾部候选与残缺扫描
     让位实体区间(指标期限不改变窗口);
  ④ _question_window/_question_range_years/months/_q_relative_constraints
     /_q_relative_tail/_evaluate_data_requirements 全链同源传跨度。
§A G1 双根(12 点拒绝不缩窗/226 点同窗通过) §B G2 复合时长拒绝族
§C G3 指标简称四形+缺数分类 §D 保留行为 §E 参数化等价问法
§F 正式 plan+report/archive 双门(合成裁决显式标记
role=R15-SYNTHETIC-ISOLATED-TEST)。破坏性操作全部限于临时目录。
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import agent_judgment as aj           # noqa: E402
import china_market_collector as cmc  # noqa: E402
import macro_collector as mc          # noqa: E402
import research_orchestrator as ro    # noqa: E402
import research_history_query as rhq  # noqa: E402
import snapshot_builder as sb         # noqa: E402
import workbench_data as wd           # noqa: E402

PASS, FAIL = 0, 0


def check(name, cond, detail=''):
    global PASS, FAIL
    print(f"  {'✅' if cond else '❌'} {name}"
          + (f" — {detail}" if detail and not cond else ''))
    PASS = PASS + (1 if cond else 0)
    FAIL = FAIL + (0 if cond else 1)


def _verdict(it):
    return (it or {}).get('blocked_class') or (it or {}).get('outcome')


# ═══ 冻结双根(12 点/全史 226 点,均锚 2026-11-17+正式快照) ═════════
_REAL = json.load(open(os.path.join(
    ROOT, 'docs/autonomous-rd/cn-task-b-20261117T083954Z/macro_input/',
    'macro_20261117.json')))
_RD = _REAL['data']['CN_PMI_MFG']['series']['dates']
_RV = _REAL['data']['CN_PMI_MFG']['series']['values']


def _cn_item(ds, vs):
    return {'date': ds[-1], 'value': vs[-1], 'prev': vs[-2],
            'frequency': 'monthly', 'unit': 'index_point',
            'series': {'dates': ds, 'values': vs},
            'provenance': {'source': 'akshare_em(macro_china)',
                           'fetched_at': '2026-11-17T02:00:00Z',
                           'coverage': {'n': len(ds)}}}


def _new_root():
    d = tempfile.mkdtemp(prefix='r15gate_')
    os.makedirs(os.path.join(d, 'data', 'daily'))
    os.makedirs(os.path.join(d, 'config'))
    shutil.copy(os.path.join(ROOT, 'config', 'metric_registry.json'),
                os.path.join(d, 'config', 'metric_registry.json'))
    return d


def _run_round(d, item):
    mc.DATA_DIR = os.path.join(d, 'data')
    cmc.fetch_macro_history = lambda: {'CN_PMI_MFG':
                                       json.loads(json.dumps(item))}
    results, _ = mc.merge_cn_history({'HY_OAS': {'value': 3.1,
                                                  'date': '2026-11-13',
                                                  'frequency': 'daily'}},
                                     data_dir=mc.DATA_DIR)
    mc.save_macro(results, [], {}, cn_history=_)


def _anchor(d):
    _dd = os.path.join(d, 'data', 'daily')
    _f = [f for f in os.listdir(_dd) if f.startswith('macro_')][0]
    os.rename(os.path.join(_dd, _f), os.path.join(_dd, 'macro_20261117.json'))
    sb.build_snapshot(target_ymd='20261117', data_dir=_dd, out_dir=_dd,
                      as_of='2026-11-17T08:36:00+08:00', trusted_root=d)


def _latest_ymd(d):
    fs = sorted(f for f in os.listdir(os.path.join(d, 'data', 'daily'))
                if f.startswith('macro_'))
    return fs[-1][6:14]


def win_of(r):
    w = (r.get('spec') or {}).get('window')
    return w if isinstance(w, dict) else {}


def eval_item_pmi(d, question, as_of='2026-11-17'):
    res = rhq.load_metric_series(
        'CN_PMI_MFG', _latest_ymd(d),
        data_dir=os.path.join(d, 'data', 'daily'), trusted_root=d)
    env = {'n': len(res['dates']),
           'source': f"采集档 {res['source']['file']}",
           'frequency': res['frequency'],
           'first': res['dates'][0] if res['dates'] else None,
           'last': res['dates'][-1] if res['dates'] else None,
           'dates': res['dates'], 'values': res['values']}
    step = {'step': 'S4_history_CN_PMI_MFG', 'ok': True,
            'envelope': {'data': {'series': env}}}
    return ro._evaluate_data_requirements(
        ['CN_PMI_MFG'], [step], {'target_date': as_of}, [],
        question=question,
        registry={'CN_PMI_MFG': {'frequency': 'monthly'}})[0]


_OMO_ENTRY = wd.load_registry(ROOT)['by_id'].get('CN_OMO_7D')


def eval_item_omo(question, as_of='2026-11-17'):
    """CN_OMO_7D 冻结面=零历史(源未接线如实缺席)→缺数判定。

    registry 传真实条目(display_name 在场→期限词形跨度生成,与生产
    run_research 同口径;薄注册会让裸「7天」形失去实体让位)。"""
    env = {'n': 0, 'source': '冻结面: CN_OMO_7D 无历史(源未接线)',
           'frequency': 'daily', 'first': None, 'last': None,
           'dates': [], 'values': []}
    step = {'step': 'S4_history_CN_OMO_7D', 'ok': True,
            'envelope': {'data': {'series': env}}}
    return ro._evaluate_data_requirements(
        ['CN_OMO_7D'], [step], {'target_date': as_of}, [],
        question=question,
        registry={'CN_OMO_7D': _OMO_ENTRY})[0]


def pwin(q, reg_root):
    """生产口径窗口: map_entities→_entity_spans→_question_window(同源)。"""
    reg = wd.load_registry(reg_root)
    ent = ro.map_entities(q, reg)
    return ro._question_window(
        q, ro._entity_spans(q, reg['by_id'], ent['metrics'])), ent


d12 = _new_root()
_run_round(d12, _cn_item(_RD[-12:], _RV[-12:]))   # 最近 12 个真实月度观测
_anchor(d12)
d226 = _new_root()
_run_round(d226, _cn_item(_RD, _RV))              # 全史 226 点
_anchor(d226)
check('A0 冻结双根(12 点 2025-11..2026-10+226 点全史,快照 2026-11-17)',
      len(_RD) == 226 and _RD[-12:][0] == '2025-11-01'
      and os.path.isfile(os.path.join(d12, 'data', 'daily',
                                      'research_snapshot_20261117.json'))
      and os.path.isfile(os.path.join(d226, 'data', 'daily',
                                      'research_snapshot_20261117.json')),
      f"n12={len(_RD[-12:])}")

# ══════════════════════════════════════════════════════════════════
print('§A G1 数据不足不能靠缩短窗口通过(一年半三形×双根)')
_G1Q = [('一年半里', '过去一年半里，CN_PMI_MFG 有哪些变化？'),
        ('一年半内', '过去一年半内，CN_PMI_MFG 有哪些变化？'),
        ('一年半期间', '过去一年半期间，CN_PMI_MFG 有哪些变化？')]
for _tag, _q in _G1Q:
    _r12 = eval_item_pmi(d12, _q)
    _w12 = win_of(_r12)
    check(f'A 12点根 {_tag} → 18 月窗 2025-05-17..2026-11-17 不缩窗'
          '+insufficient_coverage',
          _w12.get('kind') == 'relative_months'
          and _w12.get('start') == '2025-05-17'
          and _w12.get('end') == '2026-11-17'
          and _verdict(_r12) == 'insufficient_coverage',
          f"kind={_w12.get('kind')} start={_w12.get('start')} "
          f"verdict={_verdict(_r12)}")
for _tag, _q in _G1Q:
    _r = eval_item_pmi(d226, _q)
    _w = win_of(_r)
    check(f'A 226点根 {_tag} → 同一 18 月窗通过(satisfied)',
          _w.get('kind') == 'relative_months'
          and _w.get('start') == '2025-05-17'
          and _verdict(_r) == 'satisfied',
          f"start={_w.get('start')} verdict={_verdict(_r)}")
_w, _ = pwin('分析过去三年半导体需求与 CN_PMI_MFG 的关系', d226)
check('A 复核 三年半导体 → 三年窗(保留)', _w.get('kind') == 'relative'
      and _w.get('years') == 3, f"kind={_w.get('kind')}")
_w, _ = pwin('研究过去三年半 CN_PMI_MFG 的变化', d226)
check('A 复核 三年半 → 42 月(保留)', _w.get('months') == 42,
      f"months={_w.get('months')}")

# ══════════════════════════════════════════════════════════════════
print('§B G2 额外时长不能丢(复合时长拒绝族,226 点充足数据不放行)')
_G2 = [('零三个工作日', '研究过去十八个月零三个工作日 CN_PMI_MFG 的变化'),
       ('零三个交易日', '研究过去十八个月零三个交易日 CN_PMI_MFG 的变化'),
       ('又加上三天', '研究过去十八个月又加上三天 CN_PMI_MFG 的变化'),
       ('又加三天', '研究过去十八个月又加三天 CN_PMI_MFG 的变化'),
       ('零三个营业日', '研究过去十八个月零三个营业日 CN_PMI_MFG 的变化'),
       ('零三个自然日', '研究过去十八个月零三个自然日 CN_PMI_MFG 的变化')]
for _tag, _q in _G2:
    _w = ro._question_window(_q)
    _r = eval_item_pmi(d226, _q)
    check(f'B {_tag} → unparseable+生产链阻断(充足十八月数据不放行)',
          _w.get('kind') == 'unparseable'
          and '无法完整解析' in str(_w.get('reason'))
          and '改写' in str(win_of(_r).get('basis')),
          f"kind={_w.get('kind')}")
_w = ro._question_window('研究过去十八个月 CN_PMI_MFG 的变化')
_r = eval_item_pmi(d226, '研究过去十八个月 CN_PMI_MFG 的变化')
check('B 合法十八个月 → 18 月窗通过', _w.get('months') == 18
      and _verdict(_r) == 'satisfied',
      f"months={_w.get('months')} verdict={_verdict(_r)}")

# ══════════════════════════════════════════════════════════════════
print('§C G3 指标简称不能改变研究窗口(四形同指标+同六月窗+缺数如实)')
_G3 = [('7天期', '研究过去六个月7天期逆回购利率（CN_OMO_7D）的变化'),
       ('的7天期', '研究过去六个月的7天期逆回购利率（CN_OMO_7D）的变化'),
       ('7天', '研究过去六个月7天逆回购利率（CN_OMO_7D）的变化'),
       ('的7天', '研究过去六个月的7天逆回购利率（CN_OMO_7D）的变化')]
for _tag, _q in _G3:
    _w, _ent = pwin(_q, d226)
    _r = eval_item_omo(_q)
    _rw = win_of(_r)
    check(f'C {_tag} → 命中 CN_OMO_7D+六月窗+缺数分类(非时间错误)',
          _ent['metrics'] == ['CN_OMO_7D']
          and _w.get('kind') == 'relative_months' and _w.get('months') == 6
          and _rw.get('kind') == 'relative_months'
          and _rw.get('start') == '2026-05-17'
          and _rw.get('end') == '2026-11-17'
          and _verdict(_r) == 'insufficient_coverage',
          f"mets={_ent['metrics']} win={_w.get('kind')}/{_w.get('months')} "
          f"verdict={_verdict(_r)}")
for _tag, _q in [('7天无锚(真复合)', '研究过去六个月7天的数据'),
                 ('3个月无锚(真复合)', '研究过去六个月3个月的数据')]:
    _w, _ent = pwin(_q, d226)
    check(f'C {_tag} → 仍拒绝(实体锚不在场,期限让位不外溢)',
          _w.get('kind') == 'unparseable' and not _ent['metrics'],
          f"kind={_w.get('kind')} mets={_ent['metrics']}")

# ══════════════════════════════════════════════════════════════════
print('§D 保留行为(R13/R14 已修+既档语义)')
_KEPT = [('半个月(R13 反例1)', '研究过去半个月 CN_PMI_MFG 的变化', 'reject'),
         ('六个月和近半个月(R13 反例2)',
          '分别研究过去六个月和近半个月 CN_PMI_MFG 的变化', 'reject'),
         ('十八个月零三天(R13)', '研究过去十八个月零三天 CN_PMI_MFG 的变化',
          'reject'),
         ('加上三天(R14)', '研究过去十八个月加上三天 CN_PMI_MFG 的变化',
          'reject'),
         ('零一个星期(R14)', '研究过去十八个月零一个星期 CN_PMI_MFG 的变化',
          'reject'),
         ('六个月半年报(R14 保守拒)',
          '研究过去六个月半年报 CN_PMI_MFG 的变化', 'reject'),
         ('半年=6', '研究过去半年 CN_PMI_MFG 的变化', 6),
         ('一年半=18', '研究过去一年半 CN_PMI_MFG 的变化', 18),
         ('1.5年=18', '研究过去1.5年 CN_PMI_MFG 的变化', 18),
         ('三年半年度=3年', '研究过去三年半年度数据 CN_PMI_MFG 的变化', 'y3'),
         ('十年期美债≠近十年', '分析十年期美债与 CN_PMI_MFG 的关系', 'none'),
         ('裸六个月=未限定', '研究六个月 CN_PMI_MFG 数据', 'none'),
         ('近3年2024年多范围', '分析近3年 2024年 CN_PMI_MFG', 'reject')]
for _tag, _q, _exp in _KEPT:
    _w = ro._question_window(_q)
    if _exp == 'reject':
        _ok = _w.get('kind') == 'unparseable'
    elif _exp == 'none':
        _ok = _w is None
    elif _exp == 'y3':
        _ok = _w.get('kind') == 'relative' and _w.get('years') == 3
    else:
        _ok = _w.get('kind') == 'relative_months' and _w.get('months') == _exp
    check(f'D {_tag}', _ok,
          f"kind={_w and _w.get('kind')} val="
          f"{_w and (_w.get('months') or _w.get('years'))}")

# ══════════════════════════════════════════════════════════════════
print('§E 参数化等价问法(自选复验: 更换虚词/单位/连接词/词形不变结果)')
_EQ1 = [('以来', '过去一年半以来 CN_PMI_MFG', 18),
        ('以内', '过去一年半以内 CN_PMI_MFG', 18),
        ('之中', '过去一年半之中 CN_PMI_MFG', 18),
        ('当中', '过去一年半当中 CN_PMI_MFG', 18),
        ('间', '过去一年半间 CN_PMI_MFG', 18),
        ('时', '过去一年半时间 CN_PMI_MFG', 18),
        ('的', '过去一年半的 CN_PMI_MFG', 18),
        ('无pre期间', '一年半期间 CN_PMI_MFG 有哪些变化', 18),
        ('无pre里', '一年半里 CN_PMI_MFG 有哪些变化', 18),
        ('无pre内', '一年半内 CN_PMI_MFG 有哪些变化', 18),
        ('三年半里', '过去三年半里 CN_PMI_MFG', 42),
        ('三年半期间', '过去三年半期间 CN_PMI_MFG', 42)]
for _tag, _q, _m in _EQ1:
    _w = ro._question_window(_q)
    check(f'E 虚词 {_tag} → {_m} 月', _w.get('kind') == 'relative_months'
          and _w.get('months') == _m,
          f"kind={_w.get('kind')} months={_w.get('months')}")
_EQ2 = [('七天中文形', '研究过去六个月七天逆回购利率（CN_OMO_7D）的变化'),
        ('全名央行形', '研究过去六个月央行7天期逆回购利率（CN_OMO_7D）的变化')]
for _tag, _q in _EQ2:
    _w, _ent = pwin(_q, d226)
    check(f'E 期限 {_tag} → 命中+六月窗', _ent['metrics'] == ['CN_OMO_7D']
          and _w.get('months') == 6,
          f"mets={_ent['metrics']} months={_w.get('months')}")
_w, _ent = pwin('过去六个月2年美债收益率（UST_2Y）的走势', d226)
check('E 期限 2年美债简称(UST_2Y) → 命中+六月窗',
      _ent['metrics'] == ['UST_2Y'] and _w.get('months') == 6,
      f"mets={_ent['metrics']} months={_w.get('months')}")
_w, _ent = pwin('过去10年美债收益率走势', d226)
check('E 反误伤 10年美债无id → 十年窗+不凭空命中',
      _w.get('years') == 10 and not _ent['metrics'],
      f"years={_w.get('years')} mets={_ent['metrics']}")
_EQ3 = [('又加上一个工作日', '研究过去十八个月又加上一个工作日 CN_PMI_MFG 的变化'),
        ('零一季度', '研究过去十八个月零一季度 CN_PMI_MFG 的变化')]
for _tag, _q in _EQ3:
    _w = ro._question_window(_q)
    check(f'E 复合 {_tag} → 拒绝', _w.get('kind') == 'unparseable',
          f"kind={_w.get('kind')}")
_w = ro._question_window('研究过去三年工作日期安排 CN_PMI_MFG')
check('E 反误伤 工作日期护栏 → 三年窗', _w.get('years') == 3,
      f"years={_w.get('years')}")

# ══════════════════════════════════════════════════════════════════
print('§F 正式 plan+report/archive 双门(合成裁决显式标记)')

SYN_MARK = {'synthetic': True, 'note':
            '隔离测试合成裁决(非正式归档面;Audit-R15 指令要求显式标记)'}
SYN_ROLE = 'R15-SYNTHETIC-ISOLATED-TEST'


def make_run(base, name, question, req_item):
    make_run.seq += 1
    rd = os.path.join(base, name)
    os.makedirs(rd, exist_ok=True)
    rows = [{'metric_id': 'TEST_M%d' % i, 'value': 1.0 * i, 'unit': 'x',
             'observation_date': '2026-11-09', 'quality_status': 'OK',
             'source': {'id': 'src%d' % i, 'kind': 'synthetic'}}
            for i in range(2)]
    report = {
        'schema_version': '2.0', 'pipeline_version': 't',
        'run': {'question': question,
                'ts_utc': '20261119T01%04dZ' % make_run.seq,
                'git_head': 'synthetic-isolated-test', 'degradation_policy': {}},
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
        'items': [req_item],
        'optional_face': {'tier': 'optional'}}
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


def stage_report(rd, engine_root):
    r = subprocess.run(
        [sys.executable, 'ia_cli.py', 'research-one', '--stage', 'report',
         '--report-dir', rd, '--engine-root', engine_root],
        cwd=ROOT, capture_output=True, text=True, timeout=180)
    return r.returncode, json.loads(r.stdout)['data']


def stage_archive(rd, engine_root, arc):
    r = subprocess.run(
        [sys.executable, 'ia_cli.py', 'research-one', '--stage', 'archive',
         '--report-dir', rd, '--engine-root', engine_root,
         '--archive-dir', arc],
        cwd=ROOT, capture_output=True, text=True, timeout=180)
    return r.returncode, json.loads(r.stdout)['data']


def plan_run(engine_root, tag, q):
    od = os.path.join(tmpG, 'plan_%s' % tag)
    r = subprocess.run(
        [sys.executable, 'ia_cli.py', 'research-one', '--stage', 'plan',
         '--question', q, '--out-dir', od, '--engine-root', engine_root],
        cwd=ROOT, capture_output=True, text=True, timeout=600)
    import glob as _g
    _c = _g.glob(os.path.join(od, '*', 'report.json'))
    if not _c:
        return None
    j = json.load(open(_c[0], encoding='utf-8'))
    ent = (j.get('steps') or [{}])[0].get('deterministic_face') or {}
    items = ((j.get('run') or {}).get('data_requirements') or {}).get('items')
    return {'rc': r.returncode, 'metrics': ent.get('metrics'),
            'item': items[0] if items else None}


tmpG = tempfile.mkdtemp(prefix='r15gateF_')
eroot = os.path.join(tmpG, 'engine')
os.makedirs(os.path.join(eroot, 'config'), exist_ok=True)
shutil.copy(os.path.join(ROOT, 'config', 'metric_registry.json'),
            os.path.join(eroot, 'config', 'metric_registry.json'))


def _nfiles(p):
    return sum(len(fs) for _, _, fs in os.walk(p)) if os.path.isdir(p) else 0


# 正式 plan 两钉子: 12 点根一年半里=18 月窗+缺数;226 点根=同窗满足;
# G3c 7天简称=六月窗+OMO 命中+缺数分类
_pa = plan_run(d12, 'G1a12', '过去一年半里，CN_PMI_MFG 有哪些变化？')
_pb = plan_run(d226, 'G1a226', '过去一年半里，CN_PMI_MFG 有哪些变化？')
_pc = plan_run(d226, 'G3c', '研究过去六个月7天逆回购利率（CN_OMO_7D）的变化')
for _tag, _p, _mets, _start, _blocked in (
        ('12点根', _pa, ['CN_PMI_MFG'], '2025-05-17', True),
        ('226点根', _pb, ['CN_PMI_MFG'], '2025-05-17', False),
        ('G3c 7天简称', _pc, ['CN_OMO_7D'], '2026-05-17', True)):
    _pw = win_of(_p['item']) if _p and _p.get('item') else {}
    check(f'F plan {_tag} → 窗口/指标/分类逐位',
          _p is not None
          and _p['metrics'] == _mets
          and _pw.get('start') == _start
          and _pw.get('end') == '2026-11-17'
          and ((_verdict(_p['item']) == 'insufficient_coverage')
               if _blocked else (_verdict(_p['item']) == 'satisfied')),
          f"mets={_p and _p['metrics']} start={_pw.get('start')} "
          f"verdict={_p and _verdict(_p['item'])}")

# 阻断面: 12 点三形(数据不足不缩窗)+G2 三形(复合)+G3 四形(缺数)
# → report rc≠0+deliverable=False+archive rc≠0+零归档
_FIRST_BLOCKED_JD = None
_BLOCK = [(f'12点 {t}', q, eval_item_pmi(d12, q)) for t, q in _G1Q]
_BLOCK += [(f'G2 {t}', q, eval_item_pmi(d226, q)) for t, q in _G2[:3]]
_BLOCK += [(f'G3 {t}', q, eval_item_omo(q)) for t, q in _G3]
for _tag, _q, _it in _BLOCK:
    _rd = make_run(tmpG, 'b%d' % make_run.seq, _q, _it)
    aj.record_semantic_verdict(eroot, _rd, 'UPHELD', SYN_ROLE)
    if _FIRST_BLOCKED_JD is None:
        _FIRST_BLOCKED_JD = os.path.join(_rd, 'agent_judgment.json')
    _rc, _d = stage_report(_rd, eroot)
    _arc = os.path.join(tmpG, 'arc_b%d' % make_run.seq)
    _rca, _da = stage_archive(_rd, eroot, _arc)
    check(f'F 阻断 {_tag} → report/archive rc≠0+零归档',
          _rc != 0 and _d.get('deliverable') is False and _rca != 0
          and _nfiles(_arc) == 0,
          f"rc={_rc}/{_rca} deliv={_d.get('deliverable')} "
          f"bc={_d.get('blocked_class')} files={_nfiles(_arc)}")

# 交付面: 226 点三形同窗 2025-05-17 交付+归档;十八个月正例
_DELIV = [(f'226点 {t}', q, '2025-05-17') for t, q in _G1Q]
_DELIV += [('十八个月正例', '研究过去十八个月 CN_PMI_MFG 的变化', None)]
for _tag, _q, _start in _DELIV:
    _it = eval_item_pmi(d226, _q)
    _rd = make_run(tmpG, 'p%d' % make_run.seq, _q, _it)
    aj.record_semantic_verdict(eroot, _rd, 'UPHELD', SYN_ROLE)
    _rc, _d = stage_report(_rd, eroot)
    _arc = os.path.join(tmpG, 'arc_p%d' % make_run.seq)
    _rca, _da = stage_archive(_rd, eroot, _arc)
    check(f'F 交付 {_tag} → report/archive rc=0+归档在场'
          + (f'+窗起={_start}' if _start else ''),
          _rc == 0 and _d.get('deliverable') is True and _rca == 0
          and _nfiles(_arc) > 0
          and ((_start is None) or win_of(_it).get('start') == _start),
          f"rc={_rc}/{_rca} start={win_of(_it).get('start')} "
          f"files={_nfiles(_arc)}")

# 合成裁决标记在场核验(judgment 顶层 synthetic+声明 role)
_jd = json.load(open(_FIRST_BLOCKED_JD, encoding='utf-8'))
check('F 合成裁决显式标记(role+顶层 synthetic:true)',
      _jd.get('agent_declaration', {}).get('role') == SYN_ROLE
      and _jd.get('synthetic') is True,
      f"role={_jd.get('agent_declaration', {}).get('role')}")

print(f"Audit-R15 判定: {PASS} PASS / {FAIL} FAIL")
sys.exit(1 if FAIL else 0)
