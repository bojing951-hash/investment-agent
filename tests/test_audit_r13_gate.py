#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit-R13(R57) 门: 用户明确指定时间范围时只能按完整、准确的范围核验。

基线 1d39ec8 三反例(修复前全部放行):
  T1 「过去半个月」→ 「个」归一缺陷=误折半年按六个月放行;
  T2 「过去六个月和近半个月」→ 近半个月误折六月,去重合并成单一六月窗放行;
  T3 「十八个月零三天」→ 复合尾部未消费=按十八个月放行。
修复(共享解析逻辑,零特判): ①单位**先归一**('月'/'个月'/'个 月'→月/年)
再换算数量——半月类(含空白变体/0.5个月)一致拒绝,只有 半+年=6 个月;
②同一时间短语复合尾部(_QCONT_RE,可经 零/又/加/+ 连接的数量+时间单位)
=未处理数量/单位,整体拒绝不截断,与日期词重叠时让位日期分支(多范围拆分);
③等价判断/去重只发生在每个范围完整解析之后(六个月和近半月→拒;六个月和
近半年→等价合一)。

§A 三反例(生产链) §B 等价参数化 §C 拒绝族参数化 §D 双范围组合
§E 保留行为 §F 变体探测+反误伤 §G 生产 report/archive 双门。
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

PASS, FAIL = 0, 0


def check(name, cond, detail=''):
    global PASS, FAIL
    print(f"  {'✅' if cond else '❌'} {name}"
          + (f" — {detail}" if detail and not cond else ''))
    PASS = PASS + (1 if cond else 0)
    FAIL = FAIL + (0 if cond else 1)


# ══════════════════════════════════════════════════════════════════
print('§A 三审计反例(生产链: 冻结 CN_PMI_MFG 全史 226 点,时点 2026-11-17)')

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
    d = tempfile.mkdtemp(prefix='r13gate_')
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


def eval_item(d, question, as_of):
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


dF = _new_root()
_run_round(dF, _cn_item(_RD, _RV))   # 全史 226 点: 足以过合法 6/18 月窗
check('A0 冻结数据(全史,足以过合法窗)', len(_RD) == 226,
      f"n={len(_RD)}")

qw = ro._question_window
_AQ = [('T1 过去半个月(日粒度不可核验)', '研究过去半个月 CN_PMI_MFG 的变化',
        '过去半个月'),
       ('T2 六个月+近半个月双范围(先验证后去重)',
        '分别研究过去六个月和近半个月 CN_PMI_MFG 的变化', '近半个月'),
       ('T3 十八个月零三天(复合尾部)',
        '研究过去十八个月零三天 CN_PMI_MFG 的变化', '过去十八个月零三天')]
for _tag, _q, _raw in _AQ:
    _w = qw(_q)
    _r = eval_item(dF, _q, '2026-11-17')
    _win = win_of(_r)
    check(f'A {_tag} → unparseable+生产链阻断(带改写提示)',
          _w.get('kind') == 'unparseable' and _raw in str(_w.get('raw'))
          and ('改写' in str(_w.get('hint')) or '拆分' in str(_w.get('hint')))
          and _r['outcome'] == 'insufficient_coverage'
          and _win.get('kind') == 'unparseable',
          f"kind={_w.get('kind')} raw={_w.get('raw')} "
          f"outcome={_r['outcome']}")

# ══════════════════════════════════════════════════════════════════
print('§B 等价表达参数化(同窗同界,数据充足可交付)')

_EQ6 = ['研究过去半年 CN_PMI_MFG 的变化', '研究过去六个月 CN_PMI_MFG 的变化',
        '研究过去6个月 CN_PMI_MFG 的变化', '研究过去 6 个月 CN_PMI_MFG 的变化',
        '研究近六个月 CN_PMI_MFG 的变化', '研究最近半年 CN_PMI_MFG 的变化']
_EQ18 = ['研究过去一年半 CN_PMI_MFG 的变化',
         '研究过去十八个月 CN_PMI_MFG 的变化',
         '研究过去18个月 CN_PMI_MFG 的变化',
         '研究过去 18 个月 CN_PMI_MFG 的变化',
         '研究近1.5年 CN_PMI_MFG 的变化',
         '研究过去十八月 CN_PMI_MFG 的变化']
for _grp, _qs, _start in (('半年=六个月', _EQ6, '2026-05-17'),
                          ('一年半=十八个月', _EQ18, '2025-05-17')):
    _wins = []
    for _q in _qs:
        _w = qw(_q)
        _r = eval_item(dF, _q, '2026-11-17')
        _win = win_of(_r)
        _wins.append((_w.get('months'), _win.get('start'),
                      _win.get('end'), _r['outcome']))
    check(f'B 等价组 {_grp}({len(_qs)} 形) → 同 months/起止/结论',
          len(set(_wins)) == 1 and _wins[0][0] is not None
          and _wins[0][1] == _start and _wins[0][2] == '2026-11-17'
          and _wins[0][3] == 'satisfied',
          f"wins={set(_wins)}")
check('B 半年=6(只有 半+年 折六个月)', qw('研究过去半年 X').get('months') == 6)
check('B 一年半=18(N年半=N×12+6)', qw('研究过去一年半 X').get('months') == 18)

# ══════════════════════════════════════════════════════════════════
print('§C 拒绝族参数化(量词/空格/复合单位尾部 → unparseable 带提示)')

_REJ = [
    ('半月(裸日粒度)', '研究过去半月 CN_PMI_MFG 的变化'),
    ('半个月(个归一)', '研究过去半个月 CN_PMI_MFG 的变化'),
    ('半 个 月(空白变体)', '研究过去半 个 月 CN_PMI_MFG 的变化'),
    ('近半 个 月', '研究近半 个 月 CN_PMI_MFG 的变化'),
    ('0.5个月(非整月)', '研究过去0.5个月 CN_PMI_MFG 的变化'),
    ('0.5月(个可省)', '研究过去0.5月 CN_PMI_MFG 的变化'),
    ('十八个月零三天(连接词零)', '研究过去十八个月零三天 CN_PMI_MFG 的变化'),
    ('18个月3天(阿拉伯直邻)', '研究过去18个月3天 CN_PMI_MFG 的变化'),
    ('半年零一周(半年+尾部)', '研究过去半年零一周 CN_PMI_MFG 的变化'),
    ('两年零三个月(复合月)', '研究过去两年零三个月 CN_PMI_MFG 的变化'),
    ('六个月又三天(连接词又)', '研究过去六个月又三天 CN_PMI_MFG 的变化'),
    ('3个月+3天(ASCII加号)', '研究过去3个月+3天 CN_PMI_MFG 的变化'),
    ('十二个月零三天', '研究过去十二个月零三天 CN_PMI_MFG 的变化'),
    ('一年半零三天(年半+尾部)', '研究过去一年半零三天 CN_PMI_MFG 的变化'),
    ('半年以内半年(尾随半年=数量词)', '研究过去半年以内半年 CN_PMI_MFG 的变化'),
    ('六个月半年(尾随半年)', '研究过去六个月半年 CN_PMI_MFG 的变化'),
    ('六个月半年报(保守拒)', '研究过去六个月半年报 CN_PMI_MFG 的变化'),
]
for _tag, _q in _REJ:
    _w = qw(_q)
    check(f'C {_tag} → unparseable(改写提示)',
          _w.get('kind') == 'unparseable'
          and ('改写' in str(_w.get('hint')) or '拆分' in str(_w.get('hint'))),
          f"kind={_w.get('kind')} raw={_w.get('raw')}")
# 拒绝族在生产链一致(抽两形走全链)
for _q in ('研究过去半个月 CN_PMI_MFG 的变化',
           '研究过去两年零三个月 CN_PMI_MFG 的变化'):
    _r = eval_item(dF, _q, '2026-11-17')
    check(f'C 生产链一致阻断({(_q[4:12])}…)',
          _r['outcome'] == 'insufficient_coverage'
          and win_of(_r).get('kind') == 'unparseable',
          f"outcome={_r['outcome']}")

# ══════════════════════════════════════════════════════════════════
print('§D 双范围组合(先验证每个范围,再等价判断或去重)')

_w = qw('分别研究过去六个月和近半个月 CN_PMI_MFG 的变化')
check('D 六个月+近半个月 → 先拒无法解析项(不合并放行)',
      _w.get('kind') == 'unparseable' and '近半个月' in str(_w.get('raw')),
      f"raw={_w.get('raw')}")
_w = qw('研究过去六个月和近半年 CN_PMI_MFG 的变化')
_r = eval_item(dF, '研究过去六个月和近半年 CN_PMI_MFG 的变化', '2026-11-17')
check('D 六个月+近半年 → 每项完整解析后等价合一(单六月窗)',
      _w.get('kind') == 'relative_months' and _w.get('months') == 6
      and _r['outcome'] == 'satisfied',
      f"kind={_w.get('kind')} outcome={_r['outcome']}")
_w = qw('研究过去六个月和2024年 CN_PMI_MFG 的变化')
check('D 六个月+2024年 → 多范围拆分提示(保留 R11 语义)',
      _w.get('kind') == 'unparseable' and '多个时间范围约束' in str(_w)
      and '拆分' in str(_w.get('hint')))
_w = qw('近五年 2022年1月至2025年6月 DXY 走势')
check('D 近五年+显式区间 → 多范围拆分(复合尾部让位日期词,R7/r11 回归)',
      _w.get('kind') == 'unparseable' and '多个时间范围约束' in str(_w),
      f"{_w}")

# ══════════════════════════════════════════════════════════════════
print('§E 保留行为(明确年份/未指定/资产名护栏/既有口径)')

_w = qw('研究2024年 CN_PMI_MFG 的变化')
check('E 明确年份 → 日历年显式窗(R12)', _w == {
    'kind': 'explicit', 'start': '2024-01-01', 'end': '2024-12-31',
    'raw': '2024年'})
check('E 未指定范围 → None(max_available 唯一合法路径)',
      qw('研究 CN_PMI_MFG 的变化') is None)
check('E 资产名护栏(十年期美债≠范围)', qw('研究十年期美债收益率走势') is None)
check('E 去年 → calendar_year(-1)',
      qw('研究去年 CN_PMI_MFG 的变化').get('kind') == 'calendar_year')
check('E 前年 → calendar_year(-2)',
      qw('研究前年 CN_PMI_MFG 的变化').get('offset') == -2)
check('E 去年和前年 → 多范围拆分(不择一)',
      '多个时间范围约束' in str(qw('研究去年和前年 CN_PMI_MFG 的变化')))
check('E 裸数量无标记 → 未限定(R9/R10 既档)',
      qw('研究六个月 CN_PMI_MFG 趋势') is None)

# ══════════════════════════════════════════════════════════════════
print('§F 同类变体探测+反误伤')

for _tag, _q in (
        ('近半月', '研究近半月 CN_PMI_MFG 的变化'),
        ('最近半个月', '研究最近半个月 CN_PMI_MFG 的变化'),
        ('过去 半 个 月(全空白)', '研究过去 半 个 月 CN_PMI_MFG 的变化'),
        ('近18个月零3天', '研究近18个月零3天 CN_PMI_MFG 的变化'),
        ('过去十二个月又三天', '研究过去十二个月又三天 X'),
        ('过去 0.5 个月(空格)', '研究过去 0.5 个月 CN_PMI_MFG 的变化'),
        ('过去半年+三天', '研究过去半年+三天 X'),
        ('过去一年零六个月(年+复合月)', '研究过去一年零六个月 X')):
    _w = qw(_q)
    check(f'F 变体拒绝 {_tag}', _w.get('kind') == 'unparseable',
          f"kind={_w.get('kind')} raw={_w.get('raw')}")
for _tag, _q, _m in (
        ('半年 零售数据(零后无数量)', '研究过去半年 零售数据', 6),
        ('过去六个月 CN_PMI_MFG(正常问题)', '研究过去六个月 CN_PMI_MFG 的变化', 6),
        ('三年半年度数据(半年度=术语,half 组词界)', '研究过去三年半年度数据 X', 'y3'),
        ('六个月半年度报告(半年度=术语)', '研究过去六个月半年度报告 X', 6),
        ('近3年2024年(四位年=日期词→多范围)',
         '研究近3年 2024年的数据', None)):
    _w = qw(_q)
    if _m is None:
        check(f'F 反误伤 {_tag} → 多范围拆分(非复合量)',
              _w.get('kind') == 'unparseable'
              and '多个时间范围约束' in str(_w), f"{_w}")
    elif _m == 'y3':
        check(f'F 反误伤 {_tag} → years=3',
              _w.get('kind') == 'relative' and _w.get('years') == 3,
              f"{_w}")
    else:
        check(f'F 反误伤 {_tag} → months={_m}',
              _w.get('kind') == 'relative_months' and _w.get('months') == _m,
              f"{_w}")

# ══════════════════════════════════════════════════════════════════
print('§G 生产 report/archive 双门(正式入口,退出码+归档在场性)')


def make_run(tmp, name, question, req_item):
    make_run.seq += 1
    rd = os.path.join(tmp, name)
    os.makedirs(rd, exist_ok=True)
    rows = [{'metric_id': 'TEST_M%d' % i, 'value': 1.0 * i, 'unit': 'x',
             'observation_date': '2026-11-09', 'quality_status': 'OK',
             'source': {'id': 'src%d' % i, 'kind': 'synthetic'}}
            for i in range(2)]
    report = {
        'schema_version': '2.0', 'pipeline_version': 't',
        'run': {'question': question,
                'ts_utc': '20261118T23%04dZ' % make_run.seq,
                'git_head': 'synthetic', 'degradation_policy': {}},
        'steps': [], 'fanout': {},
        'layers': {
            'L1_事实层': {'rows': rows, 'available': True, 'n': 2,
                         'note': '合成: 无事实行'},
            'L2_机构观点层': {'views': {'available': False, 'n': 0,
                                        'note': '合成: 观点库缺席'}},
            'L3_AI推断层': {'produced': True, 'attribution': 'ai_inferred',
                           'note': '合成: L3 注记'},
            'L4_条件情景层': {'produced': True, 'attribution': 'ai_inferred',
                           'note': '合成: L4 注解'}},
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
    json.dump({'schema_version': aj.JUDGMENT_SCHEMA_VERSION,
               'agent_declaration': {'role': 'synthetic'},
               'l3': {'claims': []}, 'l4': {'scenarios': []}},
              open(os.path.join(rd, 'agent_judgment.json'), 'w',
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


tmpG = tempfile.mkdtemp(prefix='r13gateG_')
eroot = os.path.join(tmpG, 'engine')
os.makedirs(os.path.join(eroot, 'config'), exist_ok=True)
shutil.copy(os.path.join(ROOT, 'config', 'metric_registry.json'),
            os.path.join(eroot, 'config', 'metric_registry.json'))


def _nfiles(p):
    return sum(len(fs) for _, _, fs in os.walk(p)) if os.path.isdir(p) else 0


# 三反例: report/archive 退出码均非零,报告不可交付,零新增正式归档
for _tag, _q in (('G1 过去半个月', '研究过去半个月 CN_PMI_MFG 的变化'),
                 ('G2 六个月+近半个月',
                  '分别研究过去六个月和近半个月 CN_PMI_MFG 的变化'),
                 ('G3 十八个月零三天',
                  '研究过去十八个月零三天 CN_PMI_MFG 的变化')):
    _r = eval_item(dF, _q, '2026-11-17')
    _rd = make_run(tmpG, 'g%d' % make_run.seq, _q, _r)
    aj.record_semantic_verdict(eroot, _rd, 'UPHELD', 'R13-GATE')
    _rc, _d = stage_report(_rd, eroot)
    _arc = os.path.join(tmpG, 'arc_b%d' % make_run.seq)
    _rca, _da = stage_archive(_rd, eroot, _arc)
    check(f'G 阻断 {_tag} → report rc≠0+archive rc≠0+零归档',
          _rc != 0 and _d.get('deliverable') is False
          and _d.get('blocked_class') == 'required_data_missing'
          and _rca != 0 and _nfiles(_arc) == 0,
          f"rc={_rc}/{_rca} deliv={_d.get('deliverable')} "
          f"bc={_d.get('blocked_class')} files={_nfiles(_arc)}")

# 两等价对: report rc=0 可交付 + archive rc=0 正式归档在场
for _tag, _q, _start in (
        ('G4 过去半年(=六个月)', '研究过去半年 CN_PMI_MFG 的变化',
         '2026-05-17'),
        ('G5 过去一年半(=十八个月)', '研究过去一年半 CN_PMI_MFG 的变化',
         '2025-05-17')):
    _r = eval_item(dF, _q, '2026-11-17')
    _rd = make_run(tmpG, 'g%d' % make_run.seq, _q, _r)
    aj.record_semantic_verdict(eroot, _rd, 'UPHELD', 'R13-GATE')
    _rc, _d = stage_report(_rd, eroot)
    _arc = os.path.join(tmpG, 'arc_p%d' % make_run.seq)
    _rca, _da = stage_archive(_rd, eroot, _arc)
    check(f'G 交付 {_tag} → 同窗起点={_start},report/archive 双 rc=0+归档在场',
          _rc == 0 and _d.get('deliverable') is True and _rca == 0
          and _nfiles(_arc) > 0
          and win_of(_r).get('start') == _start,
          f"rc={_rc}/{_rca} start={win_of(_r).get('start')} "
          f"files={_nfiles(_arc)}")

# ══════════════════════════════════════════════════════════════════
print(f"\nR13 gate: {PASS} PASS / {FAIL} FAIL")
sys.exit(1 if FAIL else 0)
