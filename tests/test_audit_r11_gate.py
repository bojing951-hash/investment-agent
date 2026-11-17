#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit-R11 第十一轮审计修复回归(P1 时间约束全量收集 / P1 并发写入
互斥 / P1 引用扫描失败禁删 / P2 工作台缓存重载)。

外审反例(基线 0877516 复现,/tmp/r11_repro_p{1,2,3,4}.py):
  一(P1-① 时间约束,6 BUG):
    ①「分别研究过去五年与过去六个月」只检查六个月;
    ②「去年和前年」只检查去年;
    ③「过去一年半」被解析为一年(1 年窗误交付);
    ④「过去1.5年」「过去六季度」「近 20 24个月」被当作无范围要求
      → max_available 误交付。
  二(P1-② 并发,3/3 场景): 同 run 裁决 REVISE 被 UPHELD 覆盖且双成功;
    同日查询同配号双 written 实存一条;工作台并发归档配号撞车。
  三(P1-③ 保留策略,1 BUG): 快照 JSON 截断 → 引用被当作不存在,
    声明来源档被直接删除且无归档(字节不可恢复)。
  四(P2-④ 工作台,2 BUG): st.cache_data 无参无 TTL,文件更新后
    永远返回旧快照(须重启);首次生成后同进程仍 None。

修复判据:
  §A 窗口解析: 全部时间约束先收集后裁决;多范围=unparseable+拆分提示;
    年半/小数年/中文数量完整词元;一年半=十八个月=1.5年=months 18;
    残缺数量与未支持词形明确拒绝;既有正例(半年/空格/时点/显式区间/
    去年/前年/未限定/资产名护栏)全保留。
  §G 生产 report/archive 双门: 多范围与未支持词形双拒;真实 18 个月
    窗正例交付。
  §B 并发: 目录级跨进程互斥(store_lock)+独立临时名+原子发布;
    N 次成功=N 份完整记录;拒绝须诚实;中断写入终档不出现、前档原样;
    串行追加/重复拒绝/裁决链保持。
  §C 保留: 扫描异常逐份登记(scan_problems);扫描不完整→永久删除
    全部停止,降级 gzip 字节保全(deletion_skipped);净扫描常规策略
    不变;研究层不动。
  §D 工作台: state_fingerprint(快照候选集+注册表)为缓存键;文件
    新增/更新/注册表变化→指纹变化,无变化→稳定;app 采集成功=
    clear+rerun,失败=仅报错不失效;真实 streamlit 缓存运行时验证
    (CI 无 streamlit 时如实跳过,本地 venv 执行记录见 AUDIT_R11_REPORT)。

判定=逐 check 打印+exit code(0=全过)。合成裁决仅用于本门测试的身份
标记,不冒充真实独立审查。
"""
import json
import multiprocessing as mp
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import agent_judgment as aj          # noqa: E402
import data_retention as drt         # noqa: E402
import research_orchestrator as ro   # noqa: E402
import china_market_collector as cmc  # noqa: E402
import macro_collector as mc         # noqa: E402
import research_history_query as rhq  # noqa: E402
import store_lock as sl              # noqa: E402

PASS, FAIL = 0, 0


def check(name, cond, detail=''):
    global PASS, FAIL
    print(f"  {'✅' if cond else '❌'} {name}" + (f" — {detail}" if detail and not cond else ''))
    PASS = PASS + (1 if cond else 0)
    FAIL = FAIL + (0 if cond else 1)


# ══════════════════════════════════════════════════════════════════
print('§A P1-① 时间约束完整处理(生产链: 真实 CN_PMI_MFG 隔离副本)')

_REAL = json.load(open(os.path.join(
    ROOT, 'docs/autonomous-rd/cn-task-b-20261117T083954Z/macro_input/',
    'macro_20261117.json')))
_RD = _REAL['data']['CN_PMI_MFG']['series']['dates']
_RV = _REAL['data']['CN_PMI_MFG']['series']['values']
_VMAP = dict(zip(_RD, _RV))


def _sub(pred):
    ds = [d for d in _RD if pred(d)]
    return ds, [_VMAP[d] for d in ds]


C_D, C_V = _sub(lambda d: '2025-01-01' <= d <= '2026-10-01')   # 22 点
E_D, E_V = _sub(lambda d: '2026-01-01' <= d <= '2026-10-01')   # 10 点


def _cn_item(ds, vs):
    return {'date': ds[-1], 'value': vs[-1], 'prev': vs[-2],
            'frequency': 'monthly', 'unit': 'index_point',
            'series': {'dates': ds, 'values': vs},
            'provenance': {'source': 'akshare_em(macro_china)',
                           'fetched_at': '2026-11-17T02:00:00Z',
                           'coverage': {'n': len(ds)}}}


def _new_root():
    d = tempfile.mkdtemp(prefix='r11gate_')
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


dC, dE, dF = _new_root(), _new_root(), _new_root()
_run_round(dC, _cn_item(C_D, C_V))
_run_round(dE, _cn_item(E_D, E_V))
_run_round(dF, _cn_item(_RD, _RV))

# A1 多范围任务 → unparseable+拆分提示,不再只检查其一而误交付
rA1 = eval_item(dC, '分别研究过去五年与过去六个月 CN_PMI_MFG 的变化',
                '2026-11-17')
wA1 = ro._question_window('分别研究过去五年与过去六个月 '
                          'CN_PMI_MFG 的变化')
check('A1 多范围(五年+六个月)→ unparseable+拆分, C 数据不误交付',
      wA1.get('kind') == 'unparseable'
      and '多个时间范围约束' in str(wA1.get('reason'))
      and '拆分' in str(wA1.get('hint'))
      and rA1['outcome'] != 'satisfied',
      f"kind={wA1.get('kind')} outcome={rA1['outcome']}")

# A2 去年和前年(两个日历年约束)→ unparseable,不再只查去年
rA2 = eval_item(dC, '研究去年和前年 CN_PMI_MFG 的变化', '2026-11-17')
wA2 = win_of(rA2)
check('A2 去年和前年 → unparseable+拆分(前年零覆盖不因只查去年放行)',
      wA2.get('kind') == 'unparseable' and rA2['outcome'] != 'satisfied',
      f"kind={wA2.get('kind')} outcome={rA2['outcome']}")

# A3 一年半=十八个月=1.5年 → 同一 months=18 窗口;E 数据(10 点)阻断
rA3a = eval_item(dE, '研究过去一年半 CN_PMI_MFG 的变化', '2026-11-17')
rA3b = eval_item(dE, '研究过去十八个月 CN_PMI_MFG 的变化', '2026-11-17')
rA3c = eval_item(dE, '研究过去1.5年 CN_PMI_MFG 的变化', '2026-11-17')
_w3 = [ro._question_window(q) for q in
       ('研究过去一年半 X', '研究过去十八个月 X', '研究过去1.5年 X')]
_w3s = win_of(rA3a)
check('A3 一年半=十八个月=1.5年 → 同窗 months=18(2025-05-17..2026-11-17)',
      all(w.get('months') == 18 for w in _w3)
      and _w3s.get('start') == '2025-05-17'
      and _w3s.get('end') == '2026-11-17'
      and _w3s.get('as_of') == '2026-11-17'
      and rA3a['outcome'] != 'satisfied'
      and rA3b['outcome'] != 'satisfied',
      f"months={[w.get('months') for w in _w3]} "
      f"o={rA3a['outcome']}/{rA3b['outcome']}/{rA3c['outcome']}")

# A4 1.5年真实窗在完整历史=可交付(非 max_available 无窗交付)
rA4 = eval_item(dF, '研究过去1.5年 CN_PMI_MFG 的变化', '2026-11-17')
check('A4 过去1.5年@完整历史 → 真实 18 个月窗交付(n_in=17)',
      rA4['outcome'] == 'satisfied'
      and ro._question_window('研究过去1.5年 X').get('months') == 18
      and win_of(rA4).get('n_in_window') == 17
      and win_of(rA4).get('n_floor_in_window') == 10,
      f"o={rA4['outcome']} spec={win_of(rA4)}")

# A5 六季度 → 未支持明确拒绝(不转 max_available)
rA5 = eval_item(dF, '研究过去六季度 CN_PMI_MFG 的变化', '2026-11-17')
wA5 = ro._question_window('研究过去六季度 X')
check('A5 过去六季度 → unparseable(未支持词形),完整历史也不无窗交付',
      wA5.get('kind') == 'unparseable' and '季度' in str(wA5.get('raw'))
      and rA5['outcome'] != 'satisfied',
      f"kind={wA5.get('kind')} raw={wA5.get('raw')}")

# A6 残缺数量 → 明确拒绝
rA6 = eval_item(dF, '研究近 20 24个月 CN_PMI_MFG 的变化', '2026-11-17')
wA6 = win_of(rA6)
check('A6 近 20 24个月 → unparseable(残缺数量)',
      wA6.get('kind') == 'unparseable' and rA6['outcome'] != 'satisfied',
      f"kind={wA6.get('kind')} raw={wA6.get('raw')}")

# A7 验收不变式(原文: 增加一项必要范围要求,不能让原本因覆盖不足
#    被拒绝的同一数据变成可交付): E=10 点 2026-01..2026-10,未限定
#    (max_available)即因历史不足被拒 → 加十八个月窗仍须拒(不得翻转
#    为可交付);对照 C=22 点,窗内 17 点≥下限 → 满足=真满足非放松
rA7a = eval_item(dE, '研究 CN_PMI_MFG 的变化', '2026-11-17')
rA7b = eval_item(dE, '研究过去十八个月 CN_PMI_MFG 的变化', '2026-11-17')
rA7c = eval_item(dC, '研究过去十八个月 CN_PMI_MFG 的变化', '2026-11-17')
check('A7 验收不变式: E 被拒+加窗仍拒(不翻转);C 窗内足量=真满足',
      rA7a['outcome'] != 'satisfied' and rA7b['outcome'] != 'satisfied'
      and rA7c['outcome'] == 'satisfied'
      and win_of(rA7c).get('n_in_window') == 17,
      f"E:{rA7a['outcome']}→{rA7b['outcome']} C:{rA7c['outcome']}"
      f"(n_in={win_of(rA7c).get('n_in_window')})")

# A8 既有正例保留(解析面,完整历史)
A8 = [('研究过去半年 CN_PMI_MFG 的变化', {'kind': 'relative_months', 'months': 6}),
      ('研究过去 6 个月 CN_PMI_MFG 的变化', {'kind': 'relative_months', 'months': 6}),
      ('研究过去 6个月 CN_PMI_MFG 的变化', {'kind': 'relative_months', 'months': 6}),
      ('研究去年 CN_PMI_MFG 的变化', {'kind': 'calendar_year', 'offset': -1}),
      ('研究前年 CN_PMI_MFG 的变化', {'kind': 'calendar_year', 'offset': -2}),
      ('研究2020年以来 CN_PMI_MFG 的变化', {'kind': 'explicit'}),
      ('研究十年期美债近半年的变化',
       {'kind': 'relative_months', 'months': 6}),
      ('研究十年期美债的变化', None),
      ('研究 CN_PMI_MFG 半年均值', None),
      ('研究 CN_PMI_MFG 的变化', None)]
_ok8 = []
for q, expect in A8:
    w = ro._question_window(q)
    got = None if w is None else {k: w.get(k) for k in
                                  ('kind', 'months', 'offset')
                                  if w.get(k) is not None}
    _ok8.append((q, got == expect, got, expect))
check('A8 既有正例保留: 半年/空格变体/去年/前年/以来/资产名护栏/裸量/未限定',
      all(ok for _, ok, _, _ in _ok8),
      '; '.join(f'{q}:{g}≠{e}' for q, ok, g, e in _ok8 if not ok))

# A9 反例保留: 2026年内(日历年形)仍 BAD;显式区间+相对并存仍多范围阻断
wA9a = ro._question_window('研究2026年内 CN_PMI_MFG 的变化')
wA9b = ro._question_window('近五年 2022年1月至2025年6月 DXY 走势')
check('A9 反例保留: 2026年内=BAD;区间+年限并存=多范围阻断(拆分)',
      wA9a is not None and wA9a.get('kind') == 'unparseable'
      and wA9b.get('kind') == 'unparseable'
      and '多个时间范围约束' in str(wA9b.get('reason')),
      f"a={wA9a and wA9a.get('kind')} b={wA9b.get('kind')}")

# ══════════════════════════════════════════════════════════════════
print('§G 生产入口双门(report/archive 同判据源)')


def make_run(tmp, name, question, req_items):
    run_ts = '20261118T23%04dZ' % (make_run.seq + 1)
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
    return e['data']


def stage_archive(rd, engine_root, arc):
    return subprocess.run(
        [sys.executable, 'ia_cli.py', 'research-one', '--stage', 'archive',
         '--report-dir', rd, '--engine-root', engine_root,
         '--archive-dir', arc],
        cwd=ROOT, capture_output=True, text=True, timeout=180)


tmpG = tempfile.mkdtemp(prefix='r11gateG_')
eroot = os.path.join(tmpG, 'engine')
os.makedirs(os.path.join(eroot, 'config'), exist_ok=True)
shutil.copy(os.path.join(ROOT, 'config', 'metric_registry.json'),
            os.path.join(eroot, 'config', 'metric_registry.json'))

rG1 = eval_item(dC, '分别研究过去五年与过去六个月 CN_PMI_MFG 的变化',
                '2026-11-17')
rdG1 = make_run(tmpG, 'g1', '分别研究过去五年与过去六个月 '
                'CN_PMI_MFG 的变化', [rG1])
eG1 = stage_report(rdG1, eroot)
aG1 = stage_archive(rdG1, eroot, os.path.join(tmpG, 'arcG1'))
check('G1 多范围任务 → report 拒+archive 拒',
      eG1.get('deliverable') is False
      and eG1.get('blocked_class') == 'required_data_missing'
      and aG1.returncode != 0,
      f"bc={eG1.get('blocked_class')} rc={aG1.returncode}")

rG2 = eval_item(dF, '研究过去六季度 CN_PMI_MFG 的变化', '2026-11-17')
rdG2 = make_run(tmpG, 'g2', '研究过去六季度 CN_PMI_MFG 的变化', [rG2])
eG2 = stage_report(rdG2, eroot)
aG2 = stage_archive(rdG2, eroot, os.path.join(tmpG, 'arcG2'))
check('G2 未支持词形(六季度)→ report 拒+archive 拒',
      eG2.get('deliverable') is False
      and eG2.get('blocked_class') == 'required_data_missing'
      and aG2.returncode != 0,
      f"bc={eG2.get('blocked_class')} rc={aG2.returncode}")

rG3 = eval_item(dF, '研究过去1.5年 CN_PMI_MFG 的变化', '2026-11-17')
rdG3 = make_run(tmpG, 'g3', '研究过去1.5年 CN_PMI_MFG 的变化', [rG3])
aj.record_semantic_verdict(eroot, rdG3, 'UPHELD', 'R11-GATE')
eG3 = stage_report(rdG3, eroot)
check('G3 1.5年真实 18 个月窗@完整历史 → 可交付(正例对照)',
      eG3.get('blocked_class') != 'required_data_missing'
      and eG3.get('deliverable') is True
      and ro._question_window('研究过去1.5年 X').get('months') == 18,
      f"bc={eG3.get('blocked_class')} deliv={eG3.get('deliverable')}")

# ══════════════════════════════════════════════════════════════════
print('§B P1-② 并发写入互斥(真实多进程,临时目录)')

TDB = tempfile.mkdtemp(prefix='r11gateB_')
mp.set_start_method('fork', force=True)


def _mk_report_dir(td, run_ts):
    rd = os.path.join(td, 'report_' + run_ts.replace(':', '').replace('-', ''))
    os.makedirs(rd, exist_ok=True)
    json.dump({'run': {'ts_utc': run_ts}, 'title': 'r11-gate'},
              open(os.path.join(rd, 'report.json'), 'w'), ensure_ascii=False)
    json.dump({'ok': True}, open(os.path.join(rd, 'agent_judgment.json'), 'w'))
    return rd


def _worker_verdict(root, rd, overall, start_flag, q):
    import agent_judgment as aj
    while not os.path.exists(start_flag):
        time.sleep(0.002)
    try:
        p = aj.record_semantic_verdict(root, rd, overall,
                                       'r11-gate-seat', notes='并发门测')
        q.put(('ok', overall, p))
    except Exception as e:  # noqa: BLE001
        q.put(('err', overall, f'{type(e).__name__}: {e}'))


# B1 六进程并发裁决同一 run → 六份完整记录,序号唯一,无一覆盖
rdB1 = _mk_report_dir(TDB, '2026-11-18T10:00:00Z')
rootB1 = os.path.join(TDB, 'audit_root_b1')
startB1 = os.path.join(TDB, 'b1_start')
qB1 = mp.Queue()
N = 6
_overalls = ['REVISE', 'UPHELD', 'REVISE', 'UPHELD', 'REVISE', 'UPHELD']
psB1 = [mp.Process(target=_worker_verdict,
                   args=(rootB1, rdB1, _overalls[i], startB1, qB1))
        for i in range(N)]
for p in psB1:
    p.start()
time.sleep(0.25)
open(startB1, 'w').close()
for p in psB1:
    p.join(timeout=60)
resB1 = [qB1.get(timeout=5) for _ in psB1]
# R11 热修: 生产 record_semantic_verdict 以北京+8 定日目录(agent_judgment
# .py:617),门的读取面必须同口径——runner 本地时区(UTC CI 窗)会错位到昨日,
# files=0 假红(本地复现: TZ=UTC 27/2 → 修后 29/0)。
import datetime as _dtb  # noqa: E402
_day = _dtb.datetime.now(
    _dtb.timezone(_dtb.timedelta(hours=8))).strftime('%Y%m%d')
_vdir = os.path.join(rootB1, 'audit', 'semantic_review', _day)
filesB1 = sorted(f for f in os.listdir(_vdir)
                 if f.startswith('VERDICT-')) if os.path.isdir(_vdir) else []
_docs = []
for f in filesB1:
    _docs.append(json.load(open(os.path.join(_vdir, f), encoding='utf-8')))
_seqs = sorted(f.split('-')[-1].split('.')[0] for f in filesB1)
check('B1 六进程并发裁决 → 六份完整记录(序号唯一 01-06,零覆盖零崩溃)',
      all(st == 'ok' for st, _, _ in resB1)
      and len(filesB1) == N and len(set(_seqs)) == N
      and all(d.get('overall') for d in _docs),
      f"files={len(filesB1)} seqs={_seqs} "
      f"errs={[r for r in resB1 if r[0] != 'ok'][:1]}")
_revs = sorted(d.get('revision') for d in _docs)
check('B1b 裁决链合法(revision/predecessor 成链)',
      _revs == list(range(1, N + 1)),
      f"revisions={_revs}")

# B2 工作台并发归档(save_to_archive×2 事务) → 两条完整记录,配号唯一
SYN_SNAP = {'snapshot_id': 'research_snapshot_20261118',
            'target_date': '20261118',
            'sources_status': {}, 'facts': [], 'series_store': {}}


def _worker_wb(arch, q):
    import workbench_data as wd
    try:
        qid, err = wd.save_to_archive(
            '美国和日本10年期国债收益率差是多少？', SYN_SNAP,
            archive_dir=arch)
        q.put((qid, err))
    except Exception as e:  # noqa: BLE001
        q.put((None, f'{type(e).__name__}: {e}'))


archB2 = os.path.join(TDB, 'arch_b2')
qB2 = mp.Queue()
psB2 = [mp.Process(target=_worker_wb, args=(archB2, qB2)) for _ in range(2)]
for p in psB2:
    p.start()
for p in psB2:
    p.join(timeout=60)
resB2 = [qB2.get(timeout=5) for _ in psB2]
filesB2 = []
for _d, _f, fn in os.walk(archB2):
    filesB2.extend(f for f in fn if f.endswith('.json'))
oksB2 = [qid for qid, err in resB2 if qid]
check('B2 工作台并发归档 → 两成功=两完整记录,配号互异',
      len(oksB2) == 2 and len(set(oksB2)) == 2 and len(filesB2) == 2,
      f"qids={sorted(set(oksB2))} files={len(filesB2)} "
      f"errs={[e for _, e in resB2 if e][:1]}")

# B3 同日查询并发(配号→落盘 split 调用): 假成功/崩溃=缺陷;诚实拒绝+已存
# 记录原样=允许(验收口径);配号→落盘原子成对走事务(B2 工作台路径)
def _mk_ir(qid, created):
    import e2eb_query_mapper as qm
    seq = int(qid.rsplit('-', 1)[-1])
    return qm.map_question('美国和日本10年期国债收益率差是多少？',
                           created_at=created, query_seq=seq)


def _worker_query(archive_dir, created, start_flag, q):
    import research_archive as ra
    while not os.path.exists(start_flag):
        time.sleep(0.002)
    qid = ra.allocate_query_id(created, archive_dir=archive_dir)
    q.put(('alloc', qid))
    try:
        st, p = ra.append_query_record(_mk_ir(qid, created),
                                       snapshot=SYN_SNAP,
                                       archive_dir=archive_dir)
        q.put((st, qid, p))
    except Exception as e:  # noqa: BLE001
        q.put(('err', qid, f'{type(e).__name__}: {e}'))


archB3 = os.path.join(TDB, 'arch_b3')
startB3 = os.path.join(TDB, 'b3_start')
createdB3 = '2026-11-18T12:00:00+08:00'
qB3 = mp.Queue()
psB3 = [mp.Process(target=_worker_query,
                   args=(archB3, createdB3, startB3, qB3)) for _ in range(2)]
for p in psB3:
    p.start()
time.sleep(0.25)
open(startB3, 'w').close()
for p in psB3:
    p.join(timeout=60)
msgsB3 = [qB3.get(timeout=5) for _ in range(4)]
_resultsB3 = [m for m in msgsB3 if m[0] != 'alloc']
_bdir = os.path.join(archB3, 'research_archive', 'query_history')
filesB3 = sorted(f for f in os.listdir(_bdir) if f.endswith('.json')) \
    if os.path.isdir(_bdir) else []
_writtenB3 = [m for m in _resultsB3 if m[0] == 'written']
check('B3 同日查询并发(split 调用)→ 无假成功/无崩溃/已存记录完整',
      not any(m[0] == 'err' for m in _resultsB3)
      and len(_writtenB3) <= len(filesB3)
      and len(filesB3) >= 1
      and all(json.load(open(os.path.join(_bdir, f), encoding='utf-8'))
              .get('query_id') for f in filesB3),
      f"written={len(_writtenB3)} files={filesB3} "
      f"returns={[m[0] for m in _resultsB3]}")

# B4 中断写入: 原子发布前失败 → 终档不出现,前档原样,只留独立临时孤儿
tmpB4 = os.path.join(TDB, 'b4')
os.makedirs(tmpB4)
_prior = {'k': 'prior-verdict'}
sl.atomic_write_json(os.path.join(tmpB4, 'target.json'), _prior)
_orig_dump = json.dump


def _boom(*a, **k):
    raise ValueError('模拟中断: json.dump 失败')


try:
    sl.json.dump = _boom
    try:
        sl.atomic_write_json(os.path.join(tmpB4, 'target.json'),
                             {'k': 'new'})
        raised = False
    except ValueError:
        raised = True
finally:
    sl.json.dump = _orig_dump
_orphans = [f for f in os.listdir(tmpB4) if f.startswith('target.json.tmp.')]
check('B4 中断写入 → 异常上抛+终档原样+仅独立临时孤儿(不撕裂)',
      raised and json.load(open(os.path.join(tmpB4, 'target.json'))) == _prior
      and len(_orphans) == 1,
      f"raised={raised} orphans={_orphans}")

# B5 串行行为保留: 追加/重复拒绝
import research_archive as ra  # noqa: E402
archB5 = os.path.join(TDB, 'arch_b5')
irB5 = _mk_ir('QB-20261118-001', createdB3)
st1, p1 = ra.append_query_record(irB5, snapshot=SYN_SNAP, archive_dir=archB5)
st2, p2 = ra.append_query_record(irB5, snapshot=SYN_SNAP, archive_dir=archB5)
check('B5 串行追加+重复明确拒绝(既有行为保留)',
      st1 == 'written' and st2 != 'written',
      f"st1={st1} st2={st2}")

# ══════════════════════════════════════════════════════════════════
print('§C P1-③ 引用扫描失败禁止误删证据(临时目录)')

NOWC = time.strftime('%Y-%m-%d %H:%M:%S')
import datetime as _dt  # noqa: E402
NOWC = _dt.datetime(2026, 11, 18)


def _exists_anywhere(daily, name):
    if os.path.exists(os.path.join(daily, name)):
        return 'plain'
    if os.path.exists(os.path.join(daily, 'archive', name + '.gz')):
        return 'gz'
    return None


import gzip as _gzip  # noqa: E402

# C1 扫描脏: 截断快照+不可读快照在场 → 永久删除停止,字节保全
tdC1 = os.path.join(TDB, 'c1')
dailyC1 = os.path.join(tdC1, 'daily')
os.makedirs(dailyC1)
FC1 = {
    'macro_20260101.json': b'{"data": {"A": 1}}',
    'macro_20260205.json': b'{"data": {"B": 2}}',   # 仅被截断快照引用
    'macro_20260220.json': b'{"data": {"C": 3}}',
    'macro_20260701.json': b'{"data": {"D": 4}}',   # 无引用(扫描脏也停删)
    'macro_20260715.json': b'{"data": {"E": 5}}',
}
for n, b in FC1.items():
    open(os.path.join(dailyC1, n), 'wb').write(b)
json.dump({'snapshot_id': 'research_snapshot_20260301',
           'sources_status': {'macro': {'file': 'macro_20260101.json',
                                        'match': 'EXACT'}}},
          open(os.path.join(dailyC1, 'research_snapshot_20260301.json'), 'w'))
open(os.path.join(dailyC1, 'research_snapshot_20260401.json'), 'w').write(
    '{"snapshot_id": "research_snapshot_20260401", "sources_status": '
    '{"macro": {"file": "macro_2026')
os.makedirs(os.path.join(dailyC1, 'research_snapshot_20260501.json'))
repC1 = drt.prune_daily_archives(dailyC1, keep_days=90, now=NOWC)
_gz_ok = all(_exists_anywhere(dailyC1, n)
             == 'gz' and _gzip.open(
                 os.path.join(dailyC1, 'archive', n + '.gz'), 'rb').read()
             == FC1[n]
             for n in ('macro_20260101.json', 'macro_20260205.json',
                       'macro_20260220.json', 'macro_20260701.json',
                       'macro_20260715.json'))
check('C1 扫描脏 → 零永久删除,全部原始字节 gzip 可恢复',
      repC1['deleted'] == [] and _gz_ok
      and set(repC1['deletion_skipped']) >= {'macro_20260205.json',
                                             'macro_20260701.json'},
      f"deleted={repC1['deleted']} skipped={repC1['deletion_skipped']}")
check('C1b 扫描异常逐份登记(截断+不可读=2,快照名在场)',
      len(repC1['scan_problems']) == 2
      and {p['snapshot'] for p in repC1['scan_problems']}
      == {'research_snapshot_20260401.json',
          'research_snapshot_20260501.json'}
      and all(p.get('error') for p in repC1['scan_problems']),
      f"problems={repC1['scan_problems']}")
check('C1c 研究层文件不动(截断快照原样保留)',
      os.path.exists(os.path.join(dailyC1,
                                  'research_snapshot_20260401.json')))

# C2 扫描净: 常规策略不变(无引用删除/引用保护/月度归档/近窗保留)
tdC2 = os.path.join(TDB, 'c2')
dailyC2 = os.path.join(tdC2, 'daily')
os.makedirs(dailyC2)
FC2 = {
    'macro_20260105.json': b'{"old": 1}',
    'macro_20260120.json': b'{"ref": 2}',
    'macro_20260131.json': b'{"rep": 3}',
    'macro_20261108.json': b'{"recent": 4}',
}
for n, b in FC2.items():
    open(os.path.join(dailyC2, n), 'wb').write(b)
json.dump({'snapshot_id': 'research_snapshot_20260125',
           'sources_status': {'macro': {'file': 'macro_20260120.json',
                                        'match': 'FALLBACK'}}},
          open(os.path.join(dailyC2, 'research_snapshot_20260125.json'), 'w'))
repC2 = drt.prune_daily_archives(dailyC2, keep_days=90, now=NOWC)
check('C2 扫描净 → 常规策略不变(删无引用/保护引用/月度归档/近窗保留)',
      repC2['deleted'] == ['macro_20260105.json']
      and repC2['protected_archived'] == ['macro_20260120.json']
      and repC2['archived'] == ['macro_20260131.json']
      and repC2['kept'] == ['macro_20261108.json']
      and repC2['scan_problems'] == []
      and repC2['deletion_skipped'] == []
      and _gzip.open(os.path.join(dailyC2, 'archive',
                                  'macro_20260120.json.gz'),
                     'rb').read() == b'{"ref": 2}',
      f"del={repC2['deleted']} prot={repC2['protected_archived']} "
      f"arch={repC2['archived']} kept={repC2['kept']}")

# ══════════════════════════════════════════════════════════════════
print('§D P2-④ 工作台缓存重载(指纹键+采集成功失效)')

import workbench_data as wd  # noqa: E402

tdD = tempfile.mkdtemp(prefix='r11gateD_')
os.makedirs(os.path.join(tdD, 'data', 'daily'))
os.makedirs(os.path.join(tdD, 'config'))
json.dump({'metrics': []},
          open(os.path.join(tdD, 'config', 'metric_registry.json'), 'w'))
fp0 = wd.state_fingerprint(tdD)
check('D1 指纹稳定: 输入无变化 → 指纹不变',
      wd.state_fingerprint(tdD) == fp0)
json.dump({'snapshot_id': 'research_snapshot_20261117',
           'target_date': '20261117', 'facts': [], 'series_store': {}},
          open(os.path.join(tdD, 'data', 'daily',
                            'research_snapshot_20261117.json'), 'w'))
fp1 = wd.state_fingerprint(tdD)
check('D2 快照新增 → 指纹变化', fp1 != fp0)
_p = os.path.join(tdD, 'data', 'daily', 'research_snapshot_20261117.json')
os.utime(_p, (time.time() + 5, time.time() + 5))   # mtime 变化=内容更新信号
check('D3 快照更新(mtime)→ 指纹变化',
      wd.state_fingerprint(tdD) != fp1)
os.rename(_p, os.path.join(tdD, 'data', 'daily',
                           'research_snapshot_20261118.json'))
fpD4 = wd.state_fingerprint(tdD)
check('D4 快照删除/改名 → 指纹变化', fpD4 != fp1)
json.dump({'metrics': [{'metric_id': 'X'}]},
          open(os.path.join(tdD, 'config', 'metric_registry.json'), 'w'))
fp5 = wd.state_fingerprint(tdD)
check('D5 注册表变化 → 指纹变化(注册表亦为加载输入)', fp5 != fpD4)
check('D5b 指纹复稳定', wd.state_fingerprint(tdD) == fp5)

# D6 app.py 结构: 指纹入参 + 成功 clear+rerun + 失败仅报错
_src = open(os.path.join(ROOT, 'app.py'), encoding='utf-8').read()
_succ = _src[_src.index('if proc.returncode == 0:'):]
_succ = _succ[:_succ.index('else:')]
_fail = _src[_src.index('if proc.returncode == 0:'):]
_fail = _fail[_fail.index('else:'):_fail.index('except subprocess')]
check('D6 app 结构: _load_state(指纹入参)+_current_state;成功=clear+'
      'rerun,失败=仅 st.error(不失效不假成功)',
      'def _load_state(state_fp)' in _src
      and 'state_fingerprint()' in _src
      and '_load_state.clear()' in _succ and 'st.rerun()' in _succ
      and 'st.success' in _succ
      and 'st.error' in _fail and 'clear' not in _fail
      and 'rerun' not in _fail and 'success' not in _fail)

# D7 真实 streamlit 缓存运行时(CI 无 streamlit → 如实跳过,不伪造;
#    本地 /tmp/r11_venv 执行记录见 docs/autonomous-rd/AUDIT_R11_REPORT.md)
try:
    import streamlit  # noqa: F401
    HAS_ST = True
except ImportError:
    HAS_ST = False
if HAS_ST:
    @__import__('streamlit').cache_data(show_spinner=False)
    def _ld(fp):
        return fp

    _v1 = _ld(wd.state_fingerprint(tdD))
    json.dump({'metrics': [{'metric_id': 'Y'}]},
              open(os.path.join(tdD, 'config', 'metric_registry.json'), 'w'))
    _v2 = _ld(wd.state_fingerprint(tdD))
    check('D7 真实 st.cache_data: 指纹变→缓存键变→新值(非陈旧)',
          _v1 == fp5 and _v2 != _v1 and _v2 == wd.state_fingerprint(tdD),
          f"v1==fp5:{_v1 == fp5} v2==now:{_v2 == wd.state_fingerprint(tdD)}")
else:
    print('  ⏭️  D7 如实跳过: 本环境无 streamlit(CI 口径);'
          '真实缓存运行时验证=本地 /tmp/r11_venv(streamlit 1.50.0 bare 模式,'
          '直接导入 app.py 本体验证旧→新/首次生成/失败路径,'
          '记录于 docs/autonomous-rd/AUDIT_R11_REPORT.md §四)')

# ══════════════════════════════════════════════════════════════════
for _d in (dC, dE, dF, tmpG, TDB, tdD):
    shutil.rmtree(_d, ignore_errors=True)
print(f"\nAudit-R11 判定: {PASS} PASS / {FAIL} FAIL")
sys.exit(1 if FAIL else 0)
