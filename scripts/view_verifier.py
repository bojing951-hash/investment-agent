#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""机构观点确定性验证器(Charter 8 交付③)——零 AI 判断,零网络。

职责: 输入 view_id → 读该观点 subjects → 经 config/view_metric_map.json
取注册表现有指标 → 从最新研究快照取数 → 输出支持/反对证据表。

口径纪律(防分叉):
  区间变动一律调 research_history_query.interval_change——与 ia_cli compare
  自配对(P2-2 正式口径)**同一函数同一条 common window 规则**: 基准=严格
  早于窗口起点的最后观测,末值=窗口内最后观测;利率 pp/价格 pct/计数 abs;
  数据不足 available=False+原因,不回退 0(月频 1m 窗无当月新观测→如报
  empty 即诚实缺席)。3m 窗=P2-2 已裁决机制的自然参数(禁新窗口逻辑)。

方向关系(与 view 方向关系):
  本模块不做语义判断。relation 仅在调用方显式传入 directions
  {metric_id: 'up'|'down'} 时机械计算: 窗口内净变动方向与 hint 同号且
  available → 'supports',反号 → 'against',不足/无变化 → 'neutral';
  未传 → None+note(方向提取属 Agent 层,attribution 纪律不进本模块)。

序列来源: workbench_data.metric_series——快照 series_store 优先,缺席时按
注册表 source 回落最新采集档(与工作台历史页/compare 同一条取数路径,
防口径分叉);两级都无序列的指标只报 level+缺席原因(不猜)。

运行: python3 scripts/view_verifier.py VIEW-YYYYMMDD-NNN [--directions '{"SPX":"up"}']
      [--snapshot-id research_snapshot_YYYYMMDD_vN]
输出: 单个 JSON(stdout);rc=0 成功 / 1 执行错(无快照/无 view) / 2 用法错。
快照指针(DEFERRED②, 2026-11-10): 默认=最新;研究针对特定版本时 --snapshot-id
显式指定(archive save 同款: 短形 YYYYMMDD_vN 容忍,不存在/非规范 rc=2
snapshot_not_found)——验证结果与归档指针同版,读者按 envelope.snapshot_id
可复现。
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import view_store as vs                      # noqa: E402
import research_history_query as rhq         # noqa: E402
import fact_engine as fe                     # noqa: E402
import workbench_data as wd                  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP_PATH = os.path.join(ROOT, 'config', 'view_metric_map.json')

HORIZONS = ('1m', '3m', '1y', '5y')          # 页①复用含 5y;verifier 默认前三个


def load_map(map_path=None):
    """读 subject→metric 映射;结构校验(subjects 非空且每 subject 有 metrics)。"""
    with open(map_path or MAP_PATH, encoding='utf-8') as f:
        m = json.load(f)
    subs = m.get('subjects')
    if not isinstance(subs, dict) or not subs:
        raise ValueError('view_metric_map.json 须含非空 subjects 对象')
    for k, v in subs.items():
        if not isinstance(v, dict) or not isinstance(v.get('metrics'), list):
            raise ValueError(f'subject {k} 须含 metrics 列表')
    return m


def interval_table(metric_id, snapshot, unit, target_ymd, horizons=HORIZONS):
    """单指标多窗口区间变动——薄委托 workbench_data.metric_window_changes
    (区间口径唯一实现处,app 页①与本模块共用,防口径分叉)。"""
    return wd.metric_window_changes(metric_id, snapshot, unit, target_ymd,
                                    horizons=horizons, root=ROOT)


def _net_direction(chg):
    """窗口净变动方向: 取可用窗口中最长者(1y>3m>1m);None=无可用。

    interval_change 契约: 成功节点不带 available 键(带变化值),失败节点
    available=False+reason——判可用=键缺席或非 False,判值=三个变化键。"""
    for h in ('1y', '3m', '1m'):
        node = (chg or {}).get(h) or {}
        if node.get('available') is False:
            continue
        for key in ('pp_change', 'pct_change', 'abs_change'):
            if node.get(key) is not None:
                return 'up' if node[key] > 0 else 'down' if node[key] < 0 else 'flat'
    return None


def metric_evidence_table(subjects, snapshot, registry, vmap,
                          horizons=('1m', '3m', '1y'), directions=None):
    """证据表(纯函数): subjects∪映射指标 × 快照 facts/series_store。

    返回 {'evidence': [row...], 'missing': [...], 'notes': [...]}——missing=
    映射在册但快照无事实的指标(缺席如实,不猜)。"""
    directions = directions or {}
    facts = {f['metric_id']: f for f in (snapshot or {}).get('facts', [])}
    by_id = registry['by_id']
    subj_of = {}
    for subj, spec in vmap['subjects'].items():
        if subj in subjects:
            for mid in spec['metrics']:
                subj_of.setdefault(mid, subj)
    evidence, missing, notes = [], [], []
    for mid in sorted(subj_of):
        m = by_id.get(mid)
        if m is None or m.get('status') != 'active':
            missing.append({'metric_id': mid,
                            'reason': '映射含非注册表/非active指标(映射完整性违规)'})
            continue
        fact = facts.get(mid)
        if fact is None:
            miss_detail = ((snapshot or {}).get('gate_a') or {}).get(
                'noncore_missing_detail', {}).get(mid, '快照无该指标事实')
            missing.append({'metric_id': mid, 'reason': miss_detail})
            continue
        unit = fact.get('unit') or m.get('unit', '')
        fam = ('rate' if unit in fe.RATE_UNITS else
               'price' if unit in fe.PRICE_LIKE_UNITS else
               'count' if unit in fe.COUNT_UNITS else 'other')
        chg, series_source = interval_table(mid, snapshot, unit,
                                            snapshot.get('target_date'), horizons)
        rel, rel_note = None, '未传 directions→不做方向判断(纯确定性,语义层归 Agent)'
        if mid in directions:
            hint = directions[mid]
            got = _net_direction(chg)
            if hint not in ('up', 'down'):
                rel, rel_note = None, f'directions 值非法({hint!r},须 up/down)'
            elif got is None:
                rel, rel_note = 'neutral', '窗口内无可用变动(诚实缺席)'
            elif got == 'flat':
                rel, rel_note = 'neutral', '窗口净变动=0'
            else:
                rel = 'supports' if got == hint else 'against'
                rel_note = f'净变动方向={got} vs hint={hint}(最长可用窗口机械比对)'
        evidence.append({
            'metric_id': mid, 'subject': subj_of[mid],
            'display_name': fact.get('display_name') or m.get('display_name', mid),
            'unit': unit, 'unit_family': fam,
            'level': fact.get('value'), 'observation_date': fact.get('observation_date'),
            'quality_status': fact.get('quality_status'), 'series_source': series_source,
            'changes': chg, 'relation': rel, 'relation_note': rel_note,
        })
    if directions and set(directions) - set(subj_of):
        notes.append(f'directions 含映射外指标: '
                     f'{sorted(set(directions) - set(subj_of))}(忽略,防越权拼凑)')
    dir_missing = sorted(m['metric_id'] for m in missing if m['metric_id'] in directions)
    if dir_missing:
        notes.append(f'directions 指标缺席未判方向(如实): {dir_missing}')
    return {'evidence': evidence, 'missing': missing, 'notes': notes}


def verify(view_id, snapshot, registry, vmap, views_dir=None, directions=None):
    """完整验证: view → subjects → 证据表。返回输出 JSON dict(不含 AI 文本)。"""
    doc, reason = vs.get_view(view_id, views_dir)
    if doc is None:
        return {'ok': False, 'error': {'kind': 'view_not_found_or_quarantined',
                                       'message': reason}}
    tab = metric_evidence_table(doc['subjects'], snapshot, registry, vmap,
                                horizons=('1m', '3m', '1y'), directions=directions)
    n_sup = sum(1 for e in tab['evidence'] if e['relation'] == 'supports')
    n_ag = sum(1 for e in tab['evidence'] if e['relation'] == 'against')
    return {
        'ok': True, 'view_id': view_id,
        'institution': doc['institution']['name'],
        'publish_date': doc['publish_date'], 'fetch_date': doc['fetch_date'],
        'subjects': list(doc['subjects']),
        'snapshot_id': snapshot.get('snapshot_id'),
        'target_date': snapshot.get('target_date'),
        'research_as_of': snapshot.get('research_as_of'),
        'gate_a': (snapshot.get('gate_a') or {}).get('status'),
        'determinism_note': '全部数值=本地快照事实与 interval_change 区间变动'
                            '(compare 自配对同函数同 common window);relation 仅在'
                            '显式 directions 下机械计算,零 AI 判断',
        'n_evidence': len(tab['evidence']), 'n_missing': len(tab['missing']),
        'n_supports': n_sup, 'n_against': n_ag,
        'evidence': tab['evidence'], 'missing': tab['missing'], 'notes': tab['notes'],
    }


def _resolve_snapshot(snapshot_id=None, root=ROOT):
    """快照解析: 显式 id→research_archive.load_snapshot_by_id(archive save
    同款,短形容忍);缺省→workbench_data.latest_snapshot(默认行为不变)。

    返回 (snapshot|None, 说明)。(None, 原因) 时调用方按 kind 分流:
    显式指定失败=snapshot_not_found(用法错), 缺省无快照=no_snapshot(执行错)。"""
    if not snapshot_id:
        return wd.latest_snapshot(root)
    import research_archive as ra
    sid = snapshot_id
    if not sid.startswith('research_snapshot_'):
        sid = 'research_snapshot_' + sid         # 容忍短形 20261110_v4
    return ra.load_snapshot_by_id(sid, os.path.join(root, 'data', 'daily'))


def main(argv=None, data_root=None):
    """data_root: 快照查找根(默认 ROOT;测试注入沙箱用——注册表/映射仍走
    引擎根,与 verify 的 views_dir 同款注入缝)。"""
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print(__doc__)
        return 2
    view_id = argv[0] if not argv[0].startswith('--') else None
    directions = None
    snapshot_id = None
    rest = argv[1:] if view_id else argv
    j = 0
    while j < len(rest):
        if rest[j] == '--directions' and j + 1 < len(rest):
            try:
                directions = json.loads(rest[j + 1])
                assert isinstance(directions, dict)
            except (ValueError, AssertionError):
                print(json.dumps({'ok': False, 'error': {
                    'kind': 'bad_directions', 'message': '--directions 须为 {"METRIC":"up|down"} JSON'}},
                    ensure_ascii=False))
                return 2
            j += 2
        elif rest[j] == '--snapshot-id' and j + 1 < len(rest):
            snapshot_id = rest[j + 1].strip()
            if not snapshot_id:
                print(json.dumps({'ok': False, 'error': {
                    'kind': 'bad_snapshot_id', 'message': '--snapshot-id 须为非空 research_snapshot_YYYYMMDD[_vN]'}},
                    ensure_ascii=False))
                return 2
            j += 2
        else:
            print(json.dumps({'ok': False, 'error': {
                'kind': 'usage', 'message': f'无法识别参数: {rest[j]}(用法见 --help 或模块 docstring)'}},
                ensure_ascii=False))
            return 2
    if not view_id:
        print(json.dumps({'ok': False, 'error': {
            'kind': 'missing_view_id', 'message': '首参须为 VIEW-YYYYMMDD-NNN'}},
            ensure_ascii=False))
        return 2
    snap, note = _resolve_snapshot(snapshot_id, data_root or ROOT)
    if snap is None:
        kind = 'snapshot_not_found' if snapshot_id else 'no_snapshot'
        print(json.dumps({'ok': False, 'error': {'kind': kind,
                                                 'message': note}}, ensure_ascii=False))
        return 2 if snapshot_id else 1
    reg = wd.load_registry(ROOT)
    try:
        vmap = load_map()
    except (OSError, ValueError) as e:
        print(json.dumps({'ok': False, 'error': {'kind': 'bad_map',
                                                 'message': str(e)}}, ensure_ascii=False))
        return 1
    out = verify(view_id, snap, reg, vmap, directions=directions)
    print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
    return 0 if out.get('ok') else 1


if __name__ == '__main__':
    sys.exit(main())
