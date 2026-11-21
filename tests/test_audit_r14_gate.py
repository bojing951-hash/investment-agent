#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit-R14(R58) 门: 准确区分研究时长/复合时长后半段/行业与指标名。

基线 07d83c6 六缺陷(修复前):
  G1b 「十八个月加上三天」/G1c 「再加三天」/G1e 「零一个星期」/
  G1f 「零三个交易日」→ 尾部逃逸=按十八个月交付并归档;
  G2a 「过去三年半导体需求」→ half 组吞「半」=误折 42 月(的-形=3 年,
  两形不同窗);
  G3a 「过去六个月7天期逆回购利率(CN_OMO_7D)」→ 期限词形误作复合尾部
  =unparseable(应=六月窗+缺数如实,非时间解析错误)。
修复(共享规则,零例句特判):
  ① _QCONT_RE 连接词扩容(再加上/加上);
  ② 单位侧: 「个」前缀推广(星期/季度/交易日/日)+「交易日」单位+
     期限后缀护栏(天/月 不带「期」);
  ③ _QRANGE_RE half 后随白名单(非汉字/虚词/连接词;后随其它汉字=
     「半」开头行业/术语词形,归行业名不归 half);
  ④ _QNUM_RESIDUAL_RE 月护栏同步带「期」。
§A G1 六形 §B 行业名±的等价 §C 连接词×单位拒绝族 §D 期限±的同窗+
指标命中+缺数分类 §E 保留行为 §F 变体+反误伤 §G 正式 plan+report/
archive 双门(合成裁决显式标记 role=synthetic-isolated-test)。
破坏性操作全部限于临时目录;子进程一律 sys.executable(同解释器)。
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


# ══════════════════════════════════════════════════════════════════
print('§A G1 额外时长不能丢失(生产链: 冻结 CN_PMI_MFG 全史 226 点,'
      '时点 2026-11-17)')

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
    d = tempfile.mkdtemp(prefix='r14gate_')
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


def eval_item_omo(question, as_of='2026-11-17'):
    """CN_OMO_7D 冻结面=零历史(源未接线如实缺席)→缺数判定。"""
    env = {'n': 0, 'source': '冻结面: CN_OMO_7D 无历史(源未接线)',
           'frequency': 'daily', 'first': None, 'last': None,
           'dates': [], 'values': []}
    step = {'step': 'S4_history_CN_OMO_7D', 'ok': True,
            'envelope': {'data': {'series': env}}}
    return ro._evaluate_data_requirements(
        ['CN_OMO_7D'], [step], {'target_date': as_of}, [],
        question=question,
        registry={'CN_OMO_7D': {'frequency': 'daily'}})[0]


dF = _new_root()
_run_round(dF, _cn_item(_RD, _RV))   # 全史 226 点: 足以过合法 3 年/42 月窗
_dd = os.path.join(dF, 'data', 'daily')
_f = [f for f in os.listdir(_dd) if f.startswith('macro_')][0]
os.rename(os.path.join(_dd, _f), os.path.join(_dd, 'macro_20261117.json'))
sb.build_snapshot(target_ymd='20261117', data_dir=_dd, out_dir=_dd,
                  as_of='2026-11-17T08:36:00+08:00', trusted_root=dF)
check('A0 冻结数据(全史 226 点+快照 target_date=2026-11-17)',
      len(_RD) == 226 and os.path.isfile(os.path.join(
          _dd, 'research_snapshot_20261117.json')), f"n={len(_RD)}")

qw = ro._question_window
_G1 = [('G1a 加三天(基线已拒)', '研究过去十八个月加三天 CN_PMI_MFG 的变化'),
       ('G1b 加上三天(基线放行)', '研究过去十八个月加上三天 CN_PMI_MFG 的变化'),
       ('G1c 再加三天(基线放行)', '研究过去十八个月再加三天 CN_PMI_MFG 的变化'),
       ('G1d 零一星期(基线已拒)', '研究过去十八个月零一星期 CN_PMI_MFG 的变化'),
       ('G1e 零一个星期(基线放行)', '研究过去十八个月零一个星期 CN_PMI_MFG 的变化'),
       ('G1f 零三个交易日(基线放行)', '研究过去十八个月零三个交易日 CN_PMI_MFG 的变化')]
for _tag, _q in _G1:
    _w = qw(_q)
    _r = eval_item_pmi(dF, _q)
    _win = win_of(_r)
    check(f'A {_tag} → unparseable+生产链阻断(充足十八月数据不放行)',
          _w.get('kind') == 'unparseable'
          and ('改写' in str(_w.get('hint')) or '拆分' in str(_w.get('hint')))
          and _r['outcome'] == 'insufficient_coverage'
          and _win.get('kind') == 'unparseable',
          f"kind={_w.get('kind')} outcome={_r['outcome']}")

# ══════════════════════════════════════════════════════════════════
print('§B G2 行业名不能改变窗口(±的 同三年窗;三年半=42 月正例保留)')

_IND = ['半导体', '新能源车', '光伏', '银行业', '半衰期']
_G2 = [(f'过去三年{ind}需求', f'分析过去三年{ind}需求与 CN_PMI_MFG 的关系')
       for ind in _IND] + \
      [(f'过去三年的{ind}需求', f'分析过去三年的{ind}需求与 CN_PMI_MFG 的关系')
       for ind in _IND]
_wins = []
for _tag, _q in _G2:
    _w = qw(_q)
    _r = eval_item_pmi(dF, _q)
    _wins.append((_w.get('kind'), _w.get('years'),
                  win_of(_r).get('start'), _r['outcome']))
check(f'B 行业名±的({len(_G2)} 形) → 同 kind/年限/窗起/结论(2023-11-17)',
      len(set(_wins)) == 1 and _wins[0][0] == 'relative'
      and _wins[0][1] == 3 and _wins[0][2] == '2023-11-17'
      and _wins[0][3] == 'satisfied', f"wins={set(_wins)}")
_w42 = qw('研究过去三年半 CN_PMI_MFG 的变化')
_r42 = eval_item_pmi(dF, '研究过去三年半 CN_PMI_MFG 的变化')
check('B 三年半=42 月正例保留(2023-05-17..2026-11-17)',
      _w42.get('months') == 42 and win_of(_r42).get('start') == '2023-05-17'
      and _r42['outcome'] == 'satisfied',
      f"months={_w42.get('months')} start={win_of(_r42).get('start')}")
_w6i = [qw('研究过去六个月半导体销售额与 CN_PMI_MFG 的关系').get('months'),
        qw('研究过去六个月的半导体销售额与 CN_PMI_MFG 的关系').get('months')]
check('B 六个月+行业名±的 → 同六月窗', _w6i == [6, 6], f"wins={_w6i}")

# ══════════════════════════════════════════════════════════════════
print('§C 连接词×单位拒绝族参数化(更换等价连接词不改变拒绝)')

_REJ = [('十八个月%s%s' % (c, u),
         '研究过去十八个月%s%s CN_PMI_MFG 的变化' % (c, u))
        for c in ('加', '加上', '再加', '零', '又', '+')
        for u in ('三天', '一星期', '一个星期', '三个交易日')]
_REJ += [('半年加上三天', '研究过去半年加上三天 CN_PMI_MFG 的变化'),
         ('一年半零一个星期', '研究过去一年半零一个星期 CN_PMI_MFG 的变化')]
for _tag, _q in _REJ:
    _w = qw(_q)
    check(f'C {_tag} → unparseable(改写提示)',
          _w.get('kind') == 'unparseable'
          and ('改写' in str(_w.get('hint')) or '拆分' in str(_w.get('hint'))),
          f"kind={_w.get('kind')} raw={_w.get('raw')}")

# ══════════════════════════════════════════════════════════════════
print('§D G3 指标期限不能改变窗口(±的 同六月窗+命中 CN_OMO_7D+缺数如实)')

_TEN = ['7天期', '14天期', '90天期', '1年期', '1个月期']
_G3 = [(f'过去六个月{t}逆回购利率', f'研究过去六个月{t}逆回购利率（CN_OMO_7D）的变化')
       for t in _TEN] + \
      [(f'过去六个月的{t}逆回购利率', f'研究过去六个月的{t}逆回购利率（CN_OMO_7D）的变化')
       for t in _TEN]
_twin = []
for _tag, _q in _G3:
    _w = qw(_q)
    _twin.append((_w.get('kind'), _w.get('months')))
check(f'D 期限词形±的({len(_G3)} 形) → 同 relative_months=6',
      len(set(_twin)) == 1 and _twin[0] == ('relative_months', 6),
      f"wins={set(_twin)}")
reg = wd.load_registry(ROOT)
_m = [ro.map_entities(q, reg)['metrics'] for _, q in _G3]
check('D 指标命中 CN_OMO_7D(±的 同命中)', all(m == ['CN_OMO_7D'] for m in _m),
      f"metrics={set(map(tuple, _m))}")
_om = eval_item_omo('研究过去六个月7天期逆回购利率（CN_OMO_7D）的变化')
check('D 缺数如实(窗口已解析 2026-05-17..2026-11-17,非时间解析错误)',
      _om['outcome'] == 'insufficient_coverage'
      and win_of(_om).get('kind') == 'relative_months'
      and win_of(_om).get('start') == '2026-05-17'
      and win_of(_om).get('end') == '2026-11-17'
      and '时间' not in str(_om.get('outcome_basis') or '')[:2],
      f"outcome={_om['outcome']} win={win_of(_om).get('kind')}")
for _tag, _q in (('真复合 7天(无期)', '研究过去六个月7天 CN_PMI_MFG 的变化'),
                 ('真复合 3个月(无期)', '研究过去六个月3个月 CN_PMI_MFG 的变化')):
    check(f'D {_tag} → 仍拒绝(复合不带期=真时长)',
          qw(_q).get('kind') == 'unparseable', f"kind={qw(_q).get('kind')}")

# ══════════════════════════════════════════════════════════════════
print('§E 保留行为(上轮已修+既档语义)')

_KEPT = [('半个月(R13 反例1)', '研究过去半个月 CN_PMI_MFG 的变化', 'reject'),
         ('六个月和半个月(R13 反例2)',
          '分别研究过去六个月和近半个月 CN_PMI_MFG 的变化', 'reject'),
         ('十八个月零三天(R13 反例3)',
          '研究过去十八个月零三天 CN_PMI_MFG 的变化', 'reject'),
         ('半年=6', '研究过去半年 CN_PMI_MFG 的变化', 'mo6'),
         ('一年半=18', '研究过去一年半 CN_PMI_MFG 的变化', 'mo18'),
         ('明确年份', '研究2024年 CN_PMI_MFG 的变化', 'explicit'),
         ('未指定', '研究 CN_PMI_MFG 的变化', 'none'),
         ('十年期美债(资产名护栏)', '研究十年期美债与 CN_PMI_MFG 的关系', 'none'),
         ('裸数量未限定', '研究六个月 CN_PMI_MFG 的变化', 'none'),
         ('半年 零售数据(R13 反误伤)', '研究近半年 零售数据与 CN_PMI_MFG 的关系', 'mo6'),
         ('三年半年度数据(R13 词界)', '研究过去三年半年度数据 CN_PMI_MFG 的变化', 'y3'),
         ('六个月半年报(R13 保守拒)', '研究过去六个月半年报 CN_PMI_MFG 的变化', 'reject'),
         ('近3年2024年(R11 多范围)', '研究近3年2024年 CN_PMI_MFG 的变化', 'reject')]


def _kind_of(q):
    x = qw(q)
    if x is None:
        return 'none'
    k = x.get('kind')
    if k == 'relative_months':
        return 'mo%d' % x['months']
    if k == 'relative':
        return 'y%s' % x['years']
    return k if k == 'explicit' else 'reject'


for _tag, _q, _exp in _KEPT:
    check(f'E {_tag} → {_exp}', _kind_of(_q) == _exp,
          f"got={_kind_of(_q)}")

# ══════════════════════════════════════════════════════════════════
print('§F 变体+反误伤(词界/独立词护栏)')

_F = [('日本护栏', '研究过去六个月日本央行政策与 CN_PMI_MFG 的关系', 'mo6'),
      ('再独立词', '研究过去六个月再分析 CN_PMI_MFG 的变化', 'mo6'),
      ('期不带数', '研究过去六个月期限利差与 CN_PMI_MFG 的关系', 'mo6'),
      ('星期独立词', '研究过去六个月星期效应 CN_PMI_MFG 的变化', 'mo6'),
      ('交易日历', '研究过去六个月交易日历与 CN_PMI_MFG 的关系', 'mo6'),
      ('加无数量', '研究过去六个月加 CN_PMI_MFG 的变化', 'mo6'),
      ('正常三年', '研究过去三年 CN_PMI_MFG 的变化', 'y3'),
      ('三年半的', '研究过去三年半的 PMI 与 CN_PMI_MFG 的关系', 'mo42'),
      ('三年半以来', '研究过去三年半以来 CN_PMI_MFG 的变化', 'mo42'),
      ('三年半左右', '研究过去三年半左右 CN_PMI_MFG 的变化', 'mo42'),
      ('三年半零三天', '研究过去三年半零三天 CN_PMI_MFG 的变化', 'reject'),
      ('十四天期', '研究过去六个月14天期逆回购利率（CN_OMO_7D）的变化', 'mo6')]
for _tag, _q, _exp in _F:
    check(f'F {_tag} → {_exp}', _kind_of(_q) == _exp, f"got={_kind_of(_q)}")

# ══════════════════════════════════════════════════════════════════
print('§G 正式 plan+report/archive 双门(合成裁决显式标记)')
SYN_ROLE = 'R14-SYNTHETIC-ISOLATED-TEST'
SYN_MARK = {'synthetic': True, 'note':
            '隔离测试合成裁决(非正式归档面;Audit-R14 指令要求显式标记)'}


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
                'ts_utc': '20261118T23%04dZ' % make_run.seq,
                'git_head': SYN_ROLE, 'degradation_policy': {}},
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
        open(os.path.join(rd, 'views_digest.json'), 'w',
             encoding='utf-8'), ensure_ascii=False)
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


tmpG = tempfile.mkdtemp(prefix='r14gateG_')
eroot = os.path.join(tmpG, 'engine')
os.makedirs(os.path.join(eroot, 'config'), exist_ok=True)
shutil.copy(os.path.join(ROOT, 'config', 'metric_registry.json'),
            os.path.join(eroot, 'config', 'metric_registry.json'))


def _nfiles(p):
    return sum(len(fs) for _, _, fs in os.walk(p)) if os.path.isdir(p) else 0


# 正式 plan 核对(两钉子: 三年半导体=3 年窗 2023-11-17;7天期=六月窗+OMO 命中)
_p1 = plan_run(dF, 'G2a', '分析过去三年半导体需求与 CN_PMI_MFG 的关系')
_p2 = plan_run(dF, 'G3a', '研究过去六个月7天期逆回购利率（CN_OMO_7D）的变化')
_p1w = win_of(_p1['item']) if _p1 and _p1.get('item') else {}
_p2w = win_of(_p2['item']) if _p2 and _p2.get('item') else {}
check('G plan 三年半导体 → 3 年窗 2023-11-17..2026-11-17+指标命中',
      _p1 and _p1['metrics'] == ['CN_PMI_MFG']
      and _p1w.get('kind') == 'relative' and _p1w.get('start') == '2023-11-17'
      and _p1w.get('end') == '2026-11-17',
      f"metrics={_p1 and _p1['metrics']} win={_p1w.get('kind')}"
      f"/{_p1w.get('start')}")
check('G plan 7天期逆回购 → 六月窗 2026-05-17..2026-11-17+命中 CN_OMO_7D'
      '+缺数分类(非时间错误)',
      _p2 and _p2['metrics'] == ['CN_OMO_7D']
      and _p2w.get('kind') == 'relative_months'
      and _p2w.get('start') == '2026-05-17' and _p2w.get('end') == '2026-11-17'
      and _p2['item'].get('outcome') == 'insufficient_coverage'
      and _p2w.get('kind') != 'unparseable',
      f"metrics={_p2 and _p2['metrics']} win={_p2w.get('kind')}"
      f"/{_p2w.get('start')} outcome={_p2 and _p2['item'].get('outcome')}")

# 阻断面: G1 六形+G3 两形 → report/archive rc≠0+deliverable=False+零归档
_BLOCK = [(t, q, eval_item_pmi(dF, q)) for t, q in _G1]
_BLOCK += [('G3a 7天期(缺数)', '研究过去六个月7天期逆回购利率（CN_OMO_7D）的变化',
            eval_item_omo('研究过去六个月7天期逆回购利率（CN_OMO_7D）的变化')),
           ('G3b 的7天期(缺数)', '研究过去六个月的7天期逆回购利率（CN_OMO_7D）的变化',
            eval_item_omo('研究过去六个月的7天期逆回购利率（CN_OMO_7D）的变化'))]
for _tag, _q, _it in _BLOCK:
    _rd = make_run(tmpG, 'b%d' % make_run.seq, _q, _it)
    aj.record_semantic_verdict(eroot, _rd, 'UPHELD', SYN_ROLE)
    _rc, _d = stage_report(_rd, eroot)
    _arc = os.path.join(tmpG, 'arc_b%d' % make_run.seq)
    _rca, _da = stage_archive(_rd, eroot, _arc)
    check(f'G 阻断 {_tag} → report rc≠0+archive rc≠0+零归档',
          _rc != 0 and _d.get('deliverable') is False and _rca != 0
          and _nfiles(_arc) == 0,
          f"rc={_rc}/{_rca} deliv={_d.get('deliverable')} "
          f"bc={_d.get('blocked_class')} files={_nfiles(_arc)}")

# 交付面: G2a/G2b 同窗交付+归档;G2c 42 月正例交付+归档
_DELIV = [('G2a 三年半导体', '分析过去三年半导体需求与 CN_PMI_MFG 的关系',
           '2023-11-17', None),
          ('G2b 三年的半导体', '分析过去三年的半导体需求与 CN_PMI_MFG 的关系',
           '2023-11-17', None),
          ('G2c 三年半(42 月正例)', '研究过去三年半 CN_PMI_MFG 的变化',
           '2023-05-17', None)]
for _tag, _q, _start, _ in _DELIV:
    _it = eval_item_pmi(dF, _q)
    _rd = make_run(tmpG, 'p%d' % make_run.seq, _q, _it)
    aj.record_semantic_verdict(eroot, _rd, 'UPHELD', SYN_ROLE)
    _rc, _d = stage_report(_rd, eroot)
    _arc = os.path.join(tmpG, 'arc_p%d' % make_run.seq)
    _rca, _da = stage_archive(_rd, eroot, _arc)
    check(f'G 交付 {_tag} → 同窗起点={_start},report/archive rc=0+归档在场',
          _rc == 0 and _d.get('deliverable') is True and _rca == 0
          and _nfiles(_arc) > 0 and win_of(_it).get('start') == _start,
          f"rc={_rc}/{_rca} start={win_of(_it).get('start')} "
          f"files={_nfiles(_arc)}")

# ══════════════════════════════════════════════════════════════════
print(f"\nR14 gate: {PASS} PASS / {FAIL} FAIL")
sys.exit(1 if FAIL else 0)
