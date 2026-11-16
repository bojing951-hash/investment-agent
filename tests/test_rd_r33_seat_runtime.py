# -*- coding: utf-8 -*-
"""R33 席位 runtime 接入三件(首审席建议;SEMANTIC-AUDIT-SEAT §8 过渡条款)。

① attach 写 report.semantic_review 状态面(required/seat_invoked/verdict,
   编排层读 required 自动唤席)+report.md 披露开关——未裁=「叙事语义
   未经独立裁决」常设披露,席位裁决档在案=升为裁决摘要;
② report.md gate_a 状态披露行(各步信封顶层汇总;首审发现全 DEGRADED
   而全文零披露);
③ S3_changes 信封在场指标入证据索引(kind=s3_envelope,与 L1 按
   metric_id 去重;L3 叙事被引数字可锚)。

CI 安全: 全合成面+临时目录;零网络零模型零绝对路径依赖。
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import research_orchestrator as ro  # noqa: E402
import agent_judgment as aj  # noqa: E402

RESULTS = []


def check(name, ok, detail=''):
    RESULTS.append((name, bool(ok)))
    print(('PASS ' if ok else 'FAIL ') + name
          + (f'  [{detail}]' if detail and not ok else ''))


def section(title):
    print(f'\n══ {title} ══')


def synth_report():
    """最小合成报告(_render_md/_semantic_review_state 消费面)。"""
    return {
        'schema_version': '2.0', 'pipeline_version': ro.PIPELINE_VERSION,
        'run': {'question': '合成问题', 'ts_utc': '20260101T000000Z',
                'archive_requested': False, 'git_head': None},
        'steps': [], 'fanout': {'requested': False},
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


def _steps_gates(*vals):
    return [{'step': f'S{i}_synth', 'executed': True, 'ok': True,
             'envelope': {'gate_a': v, 'data': {}}}
            for i, v in enumerate(vals)]


# ══════════════════════════════════════════════════════════════════
section('1 ③ _s3_envelope_rows(索引扩展)')
# ══════════════════════════════════════════════════════════════════
l1 = [{'metric_id': 'SPX', 'value': 1.0, 'unit': 'index_point',
       'observation_date': '2026-11-11', 'quality_status': None,
       'source': {'kind': 'snapshot_fact', 'id': 'SPX@2026-11-11'}}]
env_rows = {'rates': [
    {'metric_id': 'SPX', 'observation_date': '2026-11-11',
     'presence': 'present'},                                  # L1 已有→去重
    {'metric_id': 'UST_10Y', 'observation_date': '2026-11-10',
     'presence': 'present'},                                  # 新增可锚
    {'metric_id': 'TLT', 'observation_date': None,
     'presence': 'present'},                                  # 缺观测日→不收
    {'metric_id': 'X_MISS', 'observation_date': '2026-11-10',
     'presence': 'missing'}],                                 # 缺席→不收
    'crypto': [
        {'metric_id': 'BTC', 'observation_date': '2026-11-11',
         'presence': 'present'}]}
steps_s3 = [{'step': 'S3_changes', 'executed': True, 'ok': True,
             'envelope': {'gate_a': 'OK',
                          'data': {'by_asset_class': env_rows}}}]
rows = ro._s3_envelope_rows(steps_s3, l1)
check('在场指标入索引(kind=s3_envelope,mid@date ref)',
      [r['ref'] for r in rows]
      == ['UST_10Y@2026-11-10', 'BTC@2026-11-11']
      and all(r['kind'] == 's3_envelope' for r in rows),
      str(rows))
check('与 L1 按 metric_id 去重',
      all(r['metric_id'] != 'SPX' for r in rows))
check('无 S3 步/畸形面→空(契约全域可判定)',
      ro._s3_envelope_rows([], l1) == []
      and ro._s3_envelope_rows(
          [{'step': 'S3_changes', 'envelope':
            {'data': {'by_asset_class': 'not-a-dict'}}}], l1) == [])

# ══════════════════════════════════════════════════════════════════
section('2 ② gate_a 披露行(_render_md)')
# ══════════════════════════════════════════════════════════════════
rep = synth_report()
rep['steps'] = _steps_gates('DEGRADED', 'DEGRADED', 'OK')
md = ro._render_md(rep)
check('降级计数行在 md(2/3 非 OK(DEGRADED))',
      '- 数据门(gate_a): 2/3 信封步非 OK(DEGRADED)' in md, md[:400])
rep2 = synth_report()
rep2['steps'] = _steps_gates('OK', 'OK')
md2 = ro._render_md(rep2)
check('全 OK 行在 md', '- 数据门(gate_a): OK(2/2 信封步)' in md2, md2[:400])
md3 = ro._render_md(synth_report())
check('无信封步=零 gate 行(不编造)',
      '数据门(gate_a)' not in md3)

# ══════════════════════════════════════════════════════════════════
section('3 ① 席位状态面(_semantic_review_state)')
# ══════════════════════════════════════════════════════════════════
with tempfile.TemporaryDirectory() as td:
    rep3 = synth_report()
    st = aj._semantic_review_state(rep3, td)
    # Audit-R1 F02: 状态面新增 fresh/verdicts_n/prior_verdicts(裁决哈希
    # 绑定+修订链)常设键;required 语义不变,旧七键等值断言升级为含新键
    check('L3/L4 未落位→required=False',
          st['required'] is False and st['reasons'] == []
          and st['seat_invoked'] is False and st['verdict'] is None
          and st['archive'] is None and st['fresh'] is None
          and st['verdicts_n'] == 0 and st['prior_verdicts'] == [],
          str(st))

    rep3['layers']['L3_AI推断层']['produced'] = True
    rep3['layers']['L4_条件情景层']['produced'] = True
    st = aj._semantic_review_state(rep3, td)
    check('L3+L4 落位→required=True 双理由+未裁(空审计面)',
          st['required'] is True
          and st['reasons'] == ['l3_qualitative_inference',
                                'l4_conditional_scenarios']
          and st['seat_invoked'] is False and st['verdict'] is None,
          str(st))

    # 裁决档在案(run ts 命中)→invoked+verdict+档路径
    vdir = os.path.join(td, 'audit', 'semantic_review', '20260101')
    os.makedirs(vdir)
    vpath = os.path.join(vdir, 'VERDICT-20260101T000000Z_合成.json')
    with open(vpath, 'w', encoding='utf-8') as f:
        json.dump({'seat': 'R-synth', 'overall': 'REVISE', 'items': []},
                  f, ensure_ascii=False)
    st = aj._semantic_review_state(rep3, td)
    check('裁决档命中→seat_invoked+verdict=REVISE+相对档径',
          st['seat_invoked'] is True and st['verdict'] == 'REVISE'
          and st['archive'] == os.path.join(
              'audit', 'semantic_review', '20260101',
              'VERDICT-20260101T000000Z_合成.json'), str(st))

    # 非命中 ts 档存在→仍未裁(匹配按 run ts,不误吸他档)
    rep4 = synth_report()
    rep4['run']['ts_utc'] = '20260202T000000Z'
    rep4['layers']['L3_AI推断层']['produced'] = True
    st = aj._semantic_review_state(rep4, td)
    check('他档不误吸(run ts 不命中→未裁)',
          st['seat_invoked'] is False, str(st))

# ══════════════════════════════════════════════════════════════════
section('4 ① 披露开关(_render_md 组合面,同 attach 写法)')
# ══════════════════════════════════════════════════════════════════
rep5 = synth_report()
rep5['layers']['L3_AI推断层']['produced'] = True
with tempfile.TemporaryDirectory() as td:
    rep5['semantic_review'] = aj._semantic_review_state(rep5, td)
md5 = ro._render_md(rep5)
check('未裁→「叙事语义未经独立裁决」常设披露在 md',
      '## 语义审查(席位待唤起)' in md5 and '叙事语义未经独立裁决' in md5,
      md5[-400:])
rep5['semantic_review'].update(
    seat_invoked=True, verdict='REVISE',
    archive='audit/semantic_review/20260101/VERDICT-x.json')
md6 = ro._render_md(rep5)
check('已裁→席位裁决摘要行在 md(开关翻转)',
      '## 语义审查(席位已裁)' in md6 and '席位裁决: REVISE' in md6,
      md6[-400:])
md7 = ro._render_md(synth_report())
check('required=False→零席位节(不噪)', '语义审查' not in md7)

# ══════════════════════════════════════════════════════════════════
section('5 ① attach 集成(状态键随档+blocked 面一致)')
# ══════════════════════════════════════════════════════════════════
with tempfile.TemporaryDirectory() as td:
    rd = os.path.join(td, 'run')
    os.makedirs(rd)
    rep_b = synth_report()
    rep_b['run_ok'] = False                    # blocked 路径(run_ok=False)
    with open(os.path.join(rd, 'report.json'), 'w',
              encoding='utf-8') as f:
        json.dump(rep_b, f, ensure_ascii=False)
    jp = os.path.join(td, 'judgment.json')
    with open(jp, 'w', encoding='utf-8') as f:
        json.dump({'l3': {}, 'l4': {}}, f, ensure_ascii=False)
    res = aj.attach_judgment(rd, jp, root=td)
    rep_after = json.load(open(os.path.join(rd, 'report.json'),
                               encoding='utf-8'))
    check('blocked 面同样落 semantic_review 键(L3 未落位→False)',
          rep_after.get('semantic_review', {}).get('required') is False
          and res.get('blocked') == 'run_ok_false',
          str(rep_after.get('semantic_review')))

n_pass = sum(1 for _, ok in RESULTS if ok)
print(f'\n==== R33 席位 runtime: {n_pass}/{len(RESULTS)} ====')
sys.exit(0 if n_pass == len(RESULTS) else 1)
