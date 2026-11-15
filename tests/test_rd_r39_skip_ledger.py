#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R39: 步骤台账跳过步标签 executed 优先判(R25 审计预存观察收口)。

缺陷: skipped_step() 数据面 ok=True(跳过≠失败,run_ok 聚合不吃假失败)
→台账渲染 ok 先判→SKIP 分支死码→跳过步渲 [OK |—](读者以为执行成功)。
修法: 两处台账(主步骤台账+十问扇出台账)executed 优先判——跳过步渲
[SKIP|—]+skipped_reason;执行步 OK/FAIL 判定不变。

全合成报告面;CI 干净 clone 可跑。
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import research_orchestrator as ro  # noqa: E402

RESULTS = []


def check(name, ok, detail=''):
    RESULTS.append((name, bool(ok)))
    print(('PASS ' if ok else 'FAIL ') + name
          + (f'  [{detail}]' if detail and not ok else ''))


def synth_report():
    return {
        'schema_version': '2.0', 'pipeline_version': ro.PIPELINE_VERSION,
        'run': {'question': '合成问题', 'ts_utc': '20260101T000000Z',
                'archive_requested': False, 'git_head': None},
        'steps': [
            {'step': 'S1_decompose', 'argv': ['a'], 'executed': True,
             'ok': True, 'exit_code': 0, 'skipped_reason': None,
             'envelope': None, 'semantic_ok': True},
            # skipped_step 形态: executed=False + ok=True(跳过≠失败)
            {'step': 'S5_history', 'argv': [], 'executed': False,
             'ok': True, 'exit_code': None,
             'skipped_reason': '本地无 DFF 序列(合成跳过理由)', 'envelope': None},
            {'step': 'S6_x', 'argv': ['b'], 'executed': True,
             'ok': False, 'exit_code': 2, 'skipped_reason': None,
             'envelope': None},
        ],
        'fanout': {'requested': True, 'n_executed': 2, 'n_agent_layer': 0,
                   'n_rq': 1, 'substitution_rule': '合成',
                   'rq': [{'id': 'RQ-1', 'text': '合成扇出问',
                           'primary_layer': 'L1',
                           'agent_layer_notes': [],
                           'steps': [
                               {'step': 'S3_x', 'argv': [], 'executed': False,
                                'ok': True, 'exit_code': None,
                                'skipped_reason': '扇出跳过理由',
                                'substitutions': [], 'note': None},
                               {'step': 'S4_y', 'argv': ['z'], 'executed': True,
                                'ok': True, 'exit_code': 0,
                                'skipped_reason': None,
                                'substitutions': [], 'note': None}]}]},
        'layers': {
            'L1_事实层': {'available': True, 'snapshot_id': 'SYNTH',
                          'target_date': '2026-01-10', 'n_facts_total': 2,
                          'rows': [], 'note': None},
            'L2_机构观点层': {'views': {'available': False, 'n': 0,
                                        'rows': [], 'note': '合成'},
                               'note': '合成'},
            'L3_AI推断层': {'produced': False, 'note': '零模型管线: 不代写'},
            'L4_条件情景层': {'produced': False, 'note': '零模型管线: 不代写'}},
        'evidence_index': [], 'notes': [], 'run_ok': True}


md = ro._render_md(synth_report()).replace('  ', ' ')

# ── §1 主步骤台账 ─────────────────────────────────────────────────
check('执行成功步渲 [OK(语义✔不变)',
      '[OK |语义✔] S1_decompose' in md)
check('跳过步渲 [SKIP|—] 不再渲 [OK |—](死码复活)',
      '[SKIP|—] S5_history' in md and '[OK |—] S5_history' not in md,
      md[md.find('S5_history') - 40:md.find('S5_history') + 20]
      if 'S5_history' in md else 'S5 不在 md')
check('跳过理由随行披露',
      '本地无 DFF 序列(合成跳过理由)' in md)
check('执行失败步照渲 [FAIL(不藏失败)',
      '[FAIL|' in md)

# ── §2 十问扇出台账 ──────────────────────────────────────────────
check('扇出跳过步渲 [SKIP](原 ok 先判同病)',
      '[SKIP] S3_x' in md and '[OK ] S3_x' not in md)
check('扇出执行步照渲 [OK ]',
      '[OK ] S4_y' in md)

# ── §3 数据面契约不变: skipped_step ok=True 保留 ─────────────────
ss = ro.skipped_step('S_test', '理由')
check('skipped_step 数据面契约不变(executed=False/ok=True/理由在场)',
      ss['executed'] is False and ss['ok'] is True
      and ss['skipped_reason'] == '理由')

# ── 汇总 ──────────────────────────────────────────────────────────
n_pass = sum(1 for _, ok in RESULTS if ok)
n_fail = len(RESULTS) - n_pass
print('═' * 64)
print(f'结果: PASS={n_pass} FAIL={n_fail}')
print('═' * 64)
sys.exit(0 if n_fail == 0 else 1)
