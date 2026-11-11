#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Charter9 P4 研究地图(research-map): 十问确定性扇出证据包(零模型)。

编排面(A席13节契约的工程底座): 每问给出①问题与五层归属(config/
research_questions.json,章程§五原文)②当前确定性数据面(计数/覆盖/新鲜度,
零模型零网络)③可执行命令清单(既有 ia_cli/view_verifier/source_verifier
能力);AI 综合判断(RQ3 主要矛盾/RQ9 条件情景等)不在此产出——归编排层
Agent 明示 ai_inferred。

协调增量【1】落地面:
- 04/05 节问题集自动提名=编排层 Agent 规则: 本引擎只给确定性原料
  nomination_inputs{conflicts(同指标多空机构对撞), pseudo_consensus
  (单源主题)};提名本身非引擎硬编码
- ART-M/ART-FALS 独立文件化: data/research/art_m.json / art_fals.json
  由编排层维护,本引擎存在则透传(计数+id),缺席如实 null——终报告内嵌
  可接受(不阻塞)
- 观察钟(orchestration clock): data/research/observation_clock.json 由
  编排层维护;引擎日历门无对外 ia_cli 能力,引擎只透传在场条目供 Agent
  每轮检查(deadline/trigger 判定与报警归 Agent),绝不代触发

纯函数入口: build_map(root=None, views_dir=None, questions_path=None,
archive_dir=None) → dict(ia_cli research-map 与 app 页④共用)。
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
SCRIPTS = os.path.join(ROOT, 'scripts')
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)


def _load_json_if(path):
    if not os.path.isfile(path):
        return None
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return {'_unreadable': True, '_path': path}


def _snapshot_face(root):
    import workbench_data as wd
    snap, note = wd.latest_snapshot(root)
    if snap is None:
        return {'available': False, 'note': note}
    return {'available': True, 'snapshot_id': snap.get('snapshot_id'),
            'target_date': snap.get('target_date'),
            'gate_a': (snap.get('gate_a') or {}).get('status'),
            'n_facts': len(snap.get('facts') or []),
            'n_series': len(snap.get('series_store') or {})}


def _views_face(views_dir):
    import view_store as vs
    res = vs.load_views(views_dir)
    insts = sorted({d['institution']['name'] for d in res['views']})
    return {'n_views': len(res['views']), 'n_quarantined': len(res['quarantined']),
            'n_institutions': len(insts), 'institutions': insts,
            'schema_version': vs.SCHEMA_VERSION}


def _archive_face(archive_dir):
    import research_archive as ra
    qids = ra.list_query_records(archive_dir=archive_dir)
    if not qids:
        return {'n_records': 0, 'latest': None,
                'note': '研究归档为空/目录缺席(干净 clone)——RQ7/RQ10 证据面待建档'}
    return {'n_records': len(qids), 'latest': qids[-1]}


def _edges_face(root):
    import workbench_data as wd
    try:
        doc = wd.transmission_edges(root=root)
    except (OSError, ValueError) as e:
        return {'available': False, 'note': f'传导边档不可用: {e}'}
    mech = {}
    for f in doc.get('mechanism_findings') or []:
        mech[f['verdict']] = mech.get(f['verdict'], 0) + 1
    return {'available': True,
            'n_strong': sum(1 for e in doc['edges'] if e['category'] == 'strong'),
            'n_near_zero': sum(1 for e in doc['edges']
                               if e['category'] == 'near_zero'),
            'mechanism_verdicts': mech,
            'archive_check': doc.get('archive_check')}


def _nomination_inputs(views_dir):
    """04/05 节问题集确定性原料(Agent 提名规则消费,引擎不提名)。

    conflicts: forecast target 经 forecast_target_map 映射+方向可解析后,
    同指标同时出现 up/down 机构 → 对撞(多空双方机构名+view_id)。
    pseudo_consensus: 主题恰 1 家机构覆盖(单源伪共识风险,与页③
    subject_coverage 同源)。"""
    import view_store as vs
    import view_verifier as vv
    try:
        tmap = vv.load_forecast_target_map()
    except (OSError, ValueError):
        tmap = None
    res = vs.load_views(views_dir)
    sides = {}
    for d in res['views']:
        inst, vid = d['institution']['name'], d['view_id']
        for f in d.get('forecasts') or []:
            metric = (vv._resolve_forecast_metric(f.get('target'), tmap)
                      if tmap else None)
            direction = vv._parse_direction(f.get('value_or_direction'))
            if metric is None or direction not in ('up', 'down'):
                continue
            sides.setdefault(metric, {'up': set(), 'down': set()})
            sides[metric][direction].add(f"{inst}({vid})")
    conflicts = [{'metric_id': m,
                  'bull': sorted(v['up']), 'bear': sorted(v['down'])}
                 for m, v in sorted(sides.items()) if v['up'] and v['down']]
    vm = wd_views_coverage(views_dir)
    pseudo = [s for s, c in vm.items() if c['pseudo_consensus_risk']]
    return {'conflicts': conflicts,
            'pseudo_consensus_subjects': pseudo,
            'note': '提名规则归编排层 Agent(矛盾+单源→04/05 节问题);'
                    '本面=确定性原料,非引擎提名'}


def wd_views_coverage(views_dir):
    import workbench_data as wd
    return wd.views_matrix(views_dir)['subject_coverage']


# 每问确定性命令清单(既有能力;零新语义)
QUESTION_COMMANDS = {
    'RQ1': ['ia_cli.py overview --economy US', 'ia_cli.py overview --economy CN',
            'ia_cli.py changes'],
    'RQ2': ['ia_cli.py changes', 'ia_cli.py compare --metrics UST_10Y,SPX'],
    'RQ3': ['(Agent 综合: RQ1/RQ2 证据+RQ4/RQ5 观点面;须明示 ai_inferred)'],
    'RQ4': ['ia_cli.py views list', 'ia_cli.py views get --view-id VIEW-…'],
    'RQ5': ['ia_cli.py research-map', 'ia_cli.py views list'],
    'RQ6': ['scripts/view_verifier.py VIEW-… --mode A',
            'scripts/view_verifier.py VIEW-… --mode C',
            'ia_cli.py compare --metrics A_ID,B_ID'],
    'RQ7': ['ia_cli.py analog', 'ia_cli.py archive list'],
    'RQ8': ['ia_cli.py research-map', '(面: edges/mechanism——map 输出内含)'],
    'RQ9': ['(Agent 条件推演五行,纪律16 权威模板: 情景[假设非预测]/'
            '资产方向判断[方向+置信层级]/敏感变量/证伪指标/触发条件;'
            '不冒充预测)'],
    'RQ10': ['ia_cli.py views get --view-id VIEW-…',
             '(要点: falsification_conditions 字段;观察钟=编排层检查 '
             'data/research/observation_clock.json)'],
}


def build_map(root=None, views_dir=None, questions_path=None, archive_dir=None):
    """研究地图: 十问×(问题/数据面/命令)+提名原料+ART 透传+观察钟透传。"""
    import workbench_data as wd
    root = root or ROOT
    rq = wd.research_questions(questions_path)
    snap_face = _snapshot_face(root)
    views_face = _views_face(views_dir)
    arch_face = _archive_face(archive_dir)
    edges_face = _edges_face(root)

    def face_for(qid, layer):
        faces = []
        if qid in ('RQ1', 'RQ2', 'RQ6'):
            faces.append({'kind': 'snapshot', **snap_face})
        if qid in ('RQ4', 'RQ5'):
            faces.append({'kind': 'views', **views_face})
        if qid in ('RQ6', 'RQ8'):
            faces.append({'kind': 'transmission', **edges_face})
        if qid in ('RQ7', 'RQ10'):
            faces.append({'kind': 'archive', **arch_face})
        if layer in ('AI推断', '条件情景') and not faces:
            faces.append({'kind': 'agent_judgment',
                          'note': '本层答案=编排层 Agent 判断/推演,引擎不产出;'
                                  '须明示 attribution(ai_inferred/条件推演不冒充预测)'})
        return faces

    questions = [{'id': q['id'], 'text': q['text'],
                  'primary_layer': q['primary_layer'], 'draws': q['draws'],
                  'surface': q['surface'],
                  'data_faces': face_for(q['id'], q['primary_layer']),
                  'commands': QUESTION_COMMANDS.get(q['id'], [])}
                 for q in rq['questions']]

    art_m = _load_json_if(os.path.join(root, 'data', 'research', 'art_m.json'))
    art_f = _load_json_if(os.path.join(root, 'data', 'research', 'art_fals.json'))
    clock = _load_json_if(os.path.join(root, 'data', 'research',
                                       'observation_clock.json'))

    def _art_summary(doc):
        if doc is None:
            return {'present': False,
                    'note': '缺席(终报告内嵌可接受;编排层可文件化增修)'}
        if doc.get('_unreadable'):
            return {'present': False, 'note': '文件不可读(非 JSON)——如实不装载'}
        items = doc.get('entries') or doc.get('items') or []
        return {'present': True, 'n': len(items),
                'ids': [it.get('id') for it in items if isinstance(it, dict)][:50]}

    clock_sum = {'present': False,
                 'note': '缺席——观察钟归编排层(引擎日历门无对外能力,不代触发)'}
    if clock is not None:
        if clock.get('_unreadable'):
            clock_sum = {'present': False, 'note': '文件不可读(非 JSON)'}
        else:
            entries = clock.get('entries') or []
            clock_sum = {'present': True, 'n': len(entries),
                         'entries': [{'id': e.get('id'),
                                      'metric_id': e.get('metric_id'),
                                      'trigger': e.get('trigger'),
                                      'deadline': e.get('deadline'),
                                      'status': e.get('status')}
                                     for e in entries if isinstance(e, dict)][:100],
                         'note': '每轮由编排层 Agent 检查 deadline/trigger;'
                                 '引擎只透传,绝不代触发'}

    return {'schema_version': '1.0',
            'questions': questions,
            'nomination_inputs': _nomination_inputs(views_dir),
            'art': {'m_table': _art_summary(art_m),
                    'falsification': _art_summary(art_f),
                    'note': 'ART-M/ART-FALS 文件化=编排层增修(append+状态迁移);'
                            '引擎透传在场件'},
            'observation_clock': clock_sum,
            'notes': ['十问=章程§五原文(裁定⑤);五层=答案内容层归因',
                      '零模型零网络: 全部计数/装载面确定性',
                      'RQ3/RQ9 类 AI 层答案不在此产出(归编排层,明示 attribution)']}


def main(argv=None):
    """轻量 CLI(调试面;正式入口=ia_cli research-map 同信封)。"""
    argv = sys.argv[1:] if argv is None else argv
    import argparse
    p = argparse.ArgumentParser(description='研究地图: 十问确定性扇出证据包')
    p.add_argument('--root', default=ROOT)
    p.add_argument('--views-dir', default=None)
    args = p.parse_args(argv)
    print(json.dumps(build_map(root=args.root, views_dir=args.views_dir),
                     ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == '__main__':
    sys.exit(main())
