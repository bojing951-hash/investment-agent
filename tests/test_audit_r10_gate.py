#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit-R10 第十轮审计修复回归(P1: 时间范围处理)。

外审反例(基线 c30bd7d 复现,/tmp/r10_repro.py 六例 BASELINE-BUG):
  A(as_of 2026-11-17,真实 CN_PMI_MFG 隔离副本 168 点=前史167+2026-10-01,
    最近半年/十二月窗内仅 1 点)以下全部经 max_available **误交付**:
    ①「研究过去半年」——「半年」词形不解析→None→未限定;
    ②「研究过去十二个月」——中文多数位 run 不匹配→None→未限定;
    ③「研究近 6 个月」——前缀与数量间空格不匹配→None→未限定;
    ④「以2026-11-17为研究时点,研究过去六个月」——单日期分支吞掉
      范围词→None→未限定(时点与范围未分别处理)。
  B(as_of 2026-11-01,仅 2026-09-01+2026-10-01 两点):
    ⑤「研究十二个月内」→「二个月内」截断 months=2→窗 2026-09-01..
      2026-11-01 窗内 2 点≥下界 2 →**误交付**(数量非完整词元匹配);
    ⑥完整历史正例窗同样被截为 months=2(窗核验失真)。

修复判据:
  §V 数量完整词元匹配+表达变体(中文数字/阿拉伯数字/空格;半年=6;
    混写与残缺→明确拒绝不缩短范围;资产名护栏;未支持词形保留)。
  §C 研究时点与研究范围分别处理(时点标记≠窗口边界;范围词不因日期
    在场丢失;冲突明确阻断;相对窗锚定问题/快照时点,不用系统当前时间)。
  §A/§B 反例经生产链(真实格式采集档→loader→S4 信封→需求判定)全部
    阻断+窗核验(实际窗口/有效观测数/下界);正例窗=十二个月(非 2)。
  §G 生产 report/archive CLI 双门: 误放行反例双拒;完整历史正例交付。
  §P 既有正例保留(ISO/斜杠/去年/前年/以来/截至/未限定 max_available/
    快照路径/历史回放锚点)。

判定=逐 check 打印+exit code(0=全过)。合成裁决仅用于本门测试的身份
标记,不冒充真实独立审查。
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import agent_judgment as aj          # noqa: E402
import research_orchestrator as ro   # noqa: E402
import china_market_collector as cmc  # noqa: E402
import macro_collector as mc         # noqa: E402
import research_history_query as rhq  # noqa: E402
import snapshot_builder as sb        # noqa: E402

PASS, FAIL = 0, 0


def check(name, cond, detail=''):
    global PASS, FAIL
    print(f"  {'✅' if cond else '❌'} {name}" + (f" — {detail}" if detail and not cond else ''))
    PASS = PASS + (1 if cond else 0)
    FAIL = FAIL + (0 if cond else 1)


# ── 真实 CN_PMI_MFG 历史(仓内 2026-11-17 实采档)与隔离副本 ──────────
_REAL = json.load(open(os.path.join(
    ROOT, 'docs/autonomous-rd/cn-task-b-20261117T083954Z/macro_input/',
    'macro_20261117.json')))
_RD = _REAL['data']['CN_PMI_MFG']['series']['dates']
_RV = _REAL['data']['CN_PMI_MFG']['series']['values']
# A: 保留 <2021-11-17(167 点)+2026-10-01 → 168 点(审计指令口径)
A_D = [d for d in _RD if d < '2021-11-17'] + ['2026-10-01']
A_V = [v for d, v in zip(_RD, _RV) if d < '2021-11-17'] + \
    [_RV[_RD.index('2026-10-01')]]
# B: 仅两个真实观测
B_D = ['2026-09-01', '2026-10-01']
B_V = [_RV[_RD.index(d)] for d in B_D]
assert len(A_D) == 168, len(A_D)


def cn_item(ds, vs):
    return {'date': ds[-1], 'value': vs[-1], 'prev': vs[-2],
            'frequency': 'monthly', 'unit': 'index_point',
            'series': {'dates': ds, 'values': vs},
            'provenance': {'source': 'akshare_em(macro_china_pmi)',
                           'fetched_at': '2026-11-17T02:00:00Z',
                           'coverage': {'n': len(ds)}}}


def new_data_root():
    d = tempfile.mkdtemp(prefix='r10g_')
    os.makedirs(os.path.join(d, 'data', 'daily'))
    os.makedirs(os.path.join(d, 'config'))
    shutil.copy(os.path.join(ROOT, 'config', 'metric_registry.json'),
                os.path.join(d, 'config', 'metric_registry.json'))
    return d


def run_round(d, pmi_item):
    mc.DATA_DIR = os.path.join(d, 'data')
    cmc.fetch_macro_history = lambda: {'CN_PMI_MFG':
                                       json.loads(json.dumps(pmi_item))}
    results, _ = mc.merge_cn_history(
        {'HY_OAS': {'value': 3.1, 'date': '2026-11-13',
                    'frequency': 'daily'}}, data_dir=mc.DATA_DIR)
    mc.save_macro(results, [], {}, cn_history=_)


def latest_ymd(d):
    fs = sorted(f for f in os.listdir(os.path.join(d, 'data', 'daily'))
                if f.startswith('macro_'))
    return fs[-1][6:14]


def query(d):
    return rhq.load_metric_series(
        'CN_PMI_MFG', latest_ymd(d),
        data_dir=os.path.join(d, 'data', 'daily'), trusted_root=d)


def eval_item(d, question, as_of):
    """生产链: 采集档→loader→S4 信封(ia_cli cmd_history 同形)→判定。"""
    res = query(d)
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


def snap_with(ds, vs, target='2026-11-17'):
    """正式快照面: 生产 merge_macro_series → series_store。"""
    raw = {'macro': {'data': {'CN_PMI_MFG': {
        'series': {'dates': ds, 'values': vs},
        'provenance': {'source': 'akshare_em(macro_china_pmi)',
                       'fetched_at': '2026-11-17T12:00:00Z',
                       'coverage': {'n': len(ds)}}}}}}
    store, prov, clean = {}, {}, {}
    sb.merge_macro_series(store, raw, prov_out=prov, clean_out=clean)
    return {'series_store': store, 'series_provenance': prov,
            **({'series_store_clean': clean} if clean else {}),
            'target_date': target}


def eval_snap(snap, question):
    return ro._evaluate_data_requirements(
        ['CN_PMI_MFG'], [], snap, [], question=question,
        registry={'CN_PMI_MFG': {'frequency': 'monthly'}})[0]


def win_of(r):
    w = (r.get('spec') or {}).get('window')
    return w if isinstance(w, dict) else {}


# 数据树(隔离副本/两点/完整)
dA, dB, dF = new_data_root(), new_data_root(), new_data_root()
run_round(dA, cn_item(A_D, A_V))
run_round(dB, cn_item(B_D, B_V))
run_round(dF, cn_item(_RD, _RV))

# ══════════════════════════════════════════════════════════════════
print('§V 数量完整词元匹配与表达变体(解析层)')


def _m(q):
    w = ro._question_window(q)
    return w.get('months') if isinstance(w, dict) else None


def _y(q):
    w = ro._question_window(q)
    return w.get('years') if isinstance(w, dict) else None


V1 = [('研究十二个月内 X', 12), ('研究过去十二个月 X', 12),
      ('研究近十二个月 X', 12), ('研究12个月内 X', 12),
      ('研究 12 个月以内 X', 12), ('研究近 6 个月 X', 6),
      ('研究过去 12 个月 X', 12), ('研究近廿一个月 X', 21),
      ('研究二十四个月内 X', 24), ('研究过去卅六个月 X', 36),
      ('研究过去6个月 X', 6)]
check('V1 月数完整词元(中文多数位/阿拉伯/空格变体)',
      all(_m(q) == n for q, n in V1),
      str([(q, _m(q), n) for q, n in V1 if _m(q) != n]))
V2 = [('研究过去半年 X', 6), ('研究近半年 X', 6), ('研究最近半年 X', 6),
      ('研究半年内 X', 6), ('研究半年以来 X', 6)]
check('V2 半年=6 个月(前缀/后缀形态)',
      all(_m(q) == 6 for q, n in V2) and _m('研究半年 X') is None,
      str([(_m(q)) for q, n in V2]))
V3 = [('研究近 5 年 X', 5), ('研究近二十年 X', 20), ('研究近十年 X', 10),
      ('研究三十年内 X', 30), ('研究 3 年以来 X', 3), ('研究近十五年 X', 15)]
check('V3 年限完整词元+空格变体(二/三/十/十五位中文)',
      all(_y(q) == n for q, n in V3),
      str([(q, _y(q), n) for q, n in V3 if _y(q) != n]))
V4 = ['研究过去十2个月 X', '研究近2十个月 X', '研究2026年内 X',
      '研究近1十二个月 X', '研究过去2六个月 X']
_w4 = [ro._question_window(q) for q in V4]
check('V4 混写/残缺数量→明确拒绝(不缩短范围)',
      all(isinstance(w, dict) and w['kind'] == 'unparseable'
          and '无法完整解析' in w['reason'] for w in _w4),
      str(_w4))
V5 = ['研究十年期美债收益率的变化', '十年期美债与两年期利差',
      '研究上周期值 X', '研究CN_PMI_MFG六月与七月对比']
check('V5 资产期限/频率词不误判研究范围',
      all(ro._question_window(q) is None for q in V5),
      str([ro._question_window(q) for q in V5]))
V6 = ['研究今年 X', '研究上周 X', '研究近三十天 X', '研究未来三个月 X',
      '研究大前年 X', '研究上半年 X', '研究下个月 X']
check('V6 未支持时间词保留阻断(带改写提示)',
      all(isinstance(ro._question_window(q), dict)
          and ro._question_window(q)['kind'] == 'unparseable'
          and 'hint' in ro._question_window(q) for q in V6))
w7 = [ro._question_window(q) for q in
      ('研究近六个月 CN_PMI_MFG 的变化', '研究六个月内 X',
       '研究过去12个月 X')]
check('V7 既有支持词形原样(不带时点键)',
      w7[0] == {'kind': 'relative_months', 'months': 6}
      and w7[1] == {'kind': 'relative_months', 'months': 6}
      and w7[2] == {'kind': 'relative_months', 'months': 12})

# ══════════════════════════════════════════════════════════════════
print('§C 研究时点与研究范围分别处理(解析+锚点)')

wA4 = ro._question_window(
    '以2026-11-17为研究时点，研究过去六个月 CN_PMI_MFG 的变化')
wA4b = ro._question_window(
    '研究时点为2026-11-01，研究十二个月内 CN_PMI_MFG 的变化')
wA4c = ro._question_window('研究时点 2021-01-15，研究近五年 X')
check('C1 时点标记+范围: 范围不丢失,as_of 随窗携带',
      wA4 == {'kind': 'relative_months', 'months': 6,
              'as_of': '2026-11-17'}
      and wA4b == {'kind': 'relative_months', 'months': 12,
                   'as_of': '2026-11-01'}
      and wA4c == {'kind': 'relative', 'years': 5,
                   'as_of': '2021-01-15'},
      f'{wA4} | {wA4b} | {wA4c}')
wC2 = ro._question_window(
    '以2026-11-17为研究时点，研究2024-01-01至2024-12-31 X')
wC2b = ro._question_window(
    '以2026-11-17为研究时点，以2026-11-01为研究时点，研究近半年 X')
check('C2 时点+显式区间不倒置;双时点冲突明确阻断',
      wC2['kind'] == 'explicit' and wC2['start'] == '2024-01-01'
      and wC2['end'] == '2024-12-31' and wC2.get('as_of') == '2026-11-17'
      and wC2b['kind'] == 'unparseable' and '冲突' in wC2b['reason'],
      f'{wC2} | {wC2b}')
# C3: 问题声明时点优先于快照 target_date,不一致在 basis 披露
rC3 = eval_item(dA, '以2026-11-17为研究时点，研究过去六个月 '
              'CN_PMI_MFG 的变化', '2026-11-14')
wC3 = win_of(rC3)
check('C3 问题时点优先于快照 target_date(冲突披露,不静默换锚)',
      rC3['outcome'] == 'insufficient_coverage'
      and wC3.get('end') == '2026-11-17'
      and '以问题声明为准' in wC3.get('basis', ''),
      f"end={wC3.get('end')} basis={wC3.get('basis', '')[:80]}")
# C4: 历史回放锚点——近半年绑回放时点 2021-01-15(非系统当前时间),
# A 副本 2020-08..2021-01 六点在窗 → satisfied(系统时间窗=阻断)
rC4 = eval_item(dA, '研究近半年 CN_PMI_MFG 的变化', '2021-01-15')
wC4 = win_of(rC4)
check('C4 相对窗绑定研究时点(回放 2021-01-15,非系统当前时间)',
      wC4.get('start') == '2020-07-15' and wC4.get('end') == '2021-01-15'
      and wC4.get('n_in_window') == 6 and rC4['outcome'] == 'satisfied',
      f"win={wC4.get('start')}..{wC4.get('end')} "
      f"n_in={wC4.get('n_in_window')} outcome={rC4['outcome']}")
# C5: 时点声明但无范围词→未限定(max_available 口径不变)
wC5 = ro._question_window('以2026-11-17为研究时点，研究 CN_PMI_MFG')
check('C5 仅时点无范围=未指定(None,max_available 唯一合法态)',
      wC5 is None, str(wC5))

# ══════════════════════════════════════════════════════════════════
print('§A 反例A(168 点: 前史167+2026-10-01,as_of 2026-11-17)')
QA = [('A1 过去半年', '研究过去半年 CN_PMI_MFG 的变化', 6, 1),
      ('A2 过去十二个月', '研究过去十二个月 CN_PMI_MFG 的变化', 12, 1),
      ('A3 近 6 个月', '研究近 6 个月 CN_PMI_MFG 的变化', 6, 1),
      ('A4 时点+过去六个月',
       '以2026-11-17为研究时点，研究过去六个月 CN_PMI_MFG 的变化', 6, 1),
      ('A0 对照 过去六个月', '研究过去六个月 CN_PMI_MFG 的变化', 6, 1)]
for tag, q, months, n_in in QA:
    r = eval_item(dA, q, '2026-11-17')
    w = win_of(r)
    # _win 不携带 months 字段(窗口以 start/end 呈现)——以窗界+窗内数核验
    import datetime as _dt
    _exp_start = ro._shift_months(_dt.date(2026, 11, 17), -months).isoformat()
    check(f'{tag} → 阻断(窗起={_exp_start},窗内 {n_in} 点,非 max_available)',
          r['outcome'] == 'insufficient_coverage'
          and w.get('kind') == 'relative_months'
          and w.get('start') == _exp_start and w.get('end') == '2026-11-17'
          and w.get('n_in_window') == n_in
          and w.get('n_floor_in_window') > n_in,
          f"s={w.get('start')} e={w.get('end')} "
          f"n_in={w.get('n_in_window')} floor={w.get('n_floor_in_window')} "
          f"o={r['outcome']}")

print('§B 反例B(仅 2026-09-01+2026-10-01,as_of 2026-11-01)')
QB = [('B1 十二个月内(中文)', '研究十二个月内 CN_PMI_MFG 的变化'),
      ('B2 12个月内(阿拉伯)', '研究12个月内 CN_PMI_MFG 的变化')]
for tag, q in QB:
    w_q = ro._question_window(q)
    r = eval_item(dB, q, '2026-11-01')
    w = win_of(r)
    check(f'{tag} → months=12(非 2)+窗 2025-11-01..2026-11-01 阻断',
          w_q == {'kind': 'relative_months', 'months': 12}
          and r['outcome'] == 'insufficient_coverage'
          and w.get('start') == '2025-11-01' and w.get('end') == '2026-11-01'
          and w.get('n_in_window') == 2
          and w.get('n_floor_in_window') == 6,
          f"qw={w_q} s={w.get('start')} n_in={w.get('n_in_window')} "
          f"floor={w.get('n_floor_in_window')} o={r['outcome']}")
# B 正例: 完整历史十二个月内 → 窗确为十二个月+跨窗满足(非仅终态放行)
rBp = eval_item(dF, '研究十二个月内 CN_PMI_MFG 的变化', '2026-11-01')
wBp = win_of(rBp)
check('B+ 完整历史十二个月内 → 窗核验=十二个月(n_in=12≥floor 6)+satisfied',
      ro._question_window('研究十二个月内 X') ==
      {'kind': 'relative_months', 'months': 12}
      and wBp.get('start') == '2025-11-01' and wBp.get('end') == '2026-11-01'
      and wBp.get('n_in_window') == 12
      and wBp.get('n_floor_in_window') == 6
      and rBp['outcome'] == 'satisfied',
      f"s={wBp.get('start')} n_in={wBp.get('n_in_window')} "
      f"floor={wBp.get('n_floor_in_window')} o={rBp['outcome']}")

# ══════════════════════════════════════════════════════════════════
print('§G 生产入口双门(report/archive 同判据源)')


def make_run(tmp, name, question, req_items):
    run_ts = '20261117T22%04dZ' % (make_run.seq + 1)
    make_run.seq += 1
    rd = os.path.join(tmp, name)
    os.makedirs(rd, exist_ok=True)
    rows = [{'metric_id': 'TEST_M%d' % i, 'value': 1.0 * i, 'unit': 'x',
             'observation_date': '2026-11-09', 'quality_status': 'OK',
             'source': {'id': 'src%d' % i, 'kind': 'synthetic'}}
            for i in range(2)]
    report = {
        'schema_version': '2.0', 'pipeline_version': 't',
        'run': {'question': question, 'ts_utc': run_ts,
                'git_head': 'synthetic', 'degradation_policy': {}},
        'steps': [], 'fanout': {},
        'layers': {
            'L1_事实层': {'rows': rows, 'available': True,
                         'n': 2, 'note': '合成: 无事实行'},
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
        'items': req_items,
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
        open(os.path.join(rd, 'views_digest.json'), 'w', encoding='utf-8'),
        ensure_ascii=False)
    return rd


make_run.seq = 0


def stage_report(rd, engine_root):
    r = subprocess.run(
        [sys.executable, 'ia_cli.py', 'research-one', '--stage', 'report',
         '--report-dir', rd, '--engine-root', engine_root],
        cwd=ROOT, capture_output=True, text=True, timeout=180)
    e = json.loads(r.stdout)
    e['_warnings'] = e.get('warnings') or []
    return e['data']


def stage_archive(rd, engine_root, arc):
    return subprocess.run(
        [sys.executable, 'ia_cli.py', 'research-one', '--stage', 'archive',
         '--report-dir', rd, '--engine-root', engine_root,
         '--archive-dir', arc],
        cwd=ROOT, capture_output=True, text=True, timeout=180)


tmpG = tempfile.mkdtemp(prefix='r10gate_')
eroot = os.path.join(tmpG, 'engine')
os.makedirs(os.path.join(eroot, 'config'), exist_ok=True)
shutil.copy(os.path.join(ROOT, 'config', 'metric_registry.json'),
            os.path.join(eroot, 'config', 'metric_registry.json'))

# G1 反例A2「过去十二个月」误放行规格 → report 拒+archive 拒
rG1 = eval_item(dA, '研究过去十二个月 CN_PMI_MFG 的变化', '2026-11-17')
rdG1 = make_run(tmpG, 'g1', '研究过去十二个月 CN_PMI_MFG 的变化', [rG1])
eG1 = stage_report(rdG1, eroot)
aG1 = stage_archive(rdG1, eroot, os.path.join(tmpG, 'arcG1'))
check('G1 「过去十二个月」168 点规格 → report 拒+archive 拒',
      eG1.get('deliverable') is False
      and eG1.get('blocked_class') == 'required_data_missing'
      and aG1.returncode != 0,
      f"bc={eG1.get('blocked_class')} deliv={eG1.get('deliverable')} "
      f"rc={aG1.returncode}")

# G2 反例A4「时点+过去六个月」误放行规格 → 双拒
rG2 = eval_item(dA, '以2026-11-17为研究时点，研究过去六个月 '
                'CN_PMI_MFG 的变化', '2026-11-14')
rdG2 = make_run(tmpG, 'g2', '以2026-11-17为研究时点，研究过去六个月 '
                'CN_PMI_MFG 的变化', [rG2])
eG2 = stage_report(rdG2, eroot)
aG2 = stage_archive(rdG2, eroot, os.path.join(tmpG, 'arcG2'))
check('G2 「时点+过去六个月」误放行规格 → report 拒+archive 拒',
      eG2.get('deliverable') is False
      and eG2.get('blocked_class') == 'required_data_missing'
      and aG2.returncode != 0,
      f"bc={eG2.get('blocked_class')} rc={aG2.returncode}")

# G3 反例B1「十二个月内」截断误放行规格 → 双拒
rG3 = eval_item(dB, '研究十二个月内 CN_PMI_MFG 的变化', '2026-11-01')
rdG3 = make_run(tmpG, 'g3', '研究十二个月内 CN_PMI_MFG 的变化', [rG3])
eG3 = stage_report(rdG3, eroot)
aG3 = stage_archive(rdG3, eroot, os.path.join(tmpG, 'arcG3'))
check('G3 「十二个月内」两点规格(months=12) → report 拒+archive 拒',
      eG3.get('deliverable') is False
      and eG3.get('blocked_class') == 'required_data_missing'
      and aG3.returncode != 0,
      f"bc={eG3.get('blocked_class')} rc={aG3.returncode}")

# G4 完整历史「十二个月内」正例 → 可交付(窗=十二个月,正例对照)
rdG4 = make_run(tmpG, 'g4', '研究十二个月内 CN_PMI_MFG 的变化', [rBp])
aj.record_semantic_verdict(eroot, rdG4, 'UPHELD', 'R10-GATE')
eG4 = stage_report(rdG4, eroot)
check('G4 「十二个月内」完整历史 → 可交付(窗核验 months=12 非终态-only)',
      win_of(rBp).get('start') == '2025-11-01'
      and eG4.get('blocked_class') != 'required_data_missing'
      and eG4.get('deliverable') is True,
      f"bc={eG4.get('blocked_class')} deliv={eG4.get('deliverable')}")

# ══════════════════════════════════════════════════════════════════
print('§P 既有正例保留(生产链+快照路径)')

# P1 既有正例全集(完整历史,as_of 2026-11-17)
P1 = [('研究 CN_PMI_MFG 的变化', 'max_available'),
      ('研究近五年 CN_PMI_MFG 的变化', 'satisfied'),
      ('研究过去六个月 CN_PMI_MFG 的变化', 'satisfied'),
      ('研究2024-01-01至2024-12-31 CN_PMI_MFG 的变化', 'satisfied'),
      ('研究2024/01/01到2024/12/31 CN_PMI_MFG 的变化', 'satisfied'),
      ('研究去年 CN_PMI_MFG 的变化', 'satisfied'),
      ('研究前年 CN_PMI_MFG 的变化', 'satisfied'),
      ('研究2020年以来 CN_PMI_MFG 的变化', 'satisfied'),
      ('截至2026-06-30 CN_PMI_MFG 的变化', 'satisfied')]
_ok = []
for q, _ in P1:
    r = eval_item(dF, q, '2026-11-17')
    _ok.append((q, r['outcome'], win_of(r).get('kind')))
check('P1 未限定/近N年/月/ISO/斜杠/去年/前年/以来/截至 全 satisfied',
      all(o == 'satisfied' for _, o, _ in _ok),
      str([x for x in _ok if x[1] != 'satisfied']))
check('P1-未限定 仍走 max_available(三态之①唯一合法)',
      _ok[0][1] == 'satisfied'
      and win_of(eval_item(dF, '研究 CN_PMI_MFG 的变化',
                           '2026-11-17')).get('kind') is None)
# P2 快照路径(正式快照面)+回放时点
rP2 = eval_snap(snap_with(A_D, A_V),
                '研究过去十二个月 CN_PMI_MFG 的变化')
wP2 = win_of(rP2)
check('P2 快照路径同判(过去十二个月 168 点 → 阻断,窗界一致)',
      rP2['outcome'] == 'insufficient_coverage'
      and wP2.get('start') == '2025-11-17'
      and wP2.get('end') == '2026-11-17'
      and wP2.get('n_in_window') == 1,
      f"s={wP2.get('start')} n_in={wP2.get('n_in_window')}")
rP3 = eval_snap(snap_with(_RD, _RV, target='2021-01-15'),
                '研究近半年 CN_PMI_MFG 的变化')
wP3 = win_of(rP3)
check('P3 快照回放锚点(近半年@2021-01-15,非系统时间)',
      wP3.get('start') == '2020-07-15' and wP3.get('end') == '2021-01-15'
      and rP3['outcome'] == 'satisfied',
      f"s={wP3.get('start')} e={wP3.get('end')} o={rP3['outcome']}")
# P4 required 满足时 optional 缺失合理降级(r5 门 §S 同判据;此处
# 以 optional 面 tier 降级路径在场性复证——optional 缺席不阻断)
rP4 = eval_item(dF, '研究近五年 CN_PMI_MFG 的变化', '2026-11-17')
check('P4 required 满足正例形态不变(spec+tier=basis 问题词面)',
      rP4['tier'] == 'required' and rP4['outcome'] == 'satisfied',
      f"tier={rP4.get('tier')} o={rP4['outcome']}")

print(f"\nAudit-R10 判定: {PASS} PASS / {FAIL} FAIL")
sys.exit(1 if FAIL else 0)
