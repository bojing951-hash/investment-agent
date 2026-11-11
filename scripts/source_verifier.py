#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Charter9 P0-3 来源验证引擎(source_verifier)——qb_source 溯源的代码执行。

背景(audit/C9_D_AUDIT_AND_DESIGN §3 × C席复现 audit/C9_P0_REPRODUCE P0-3):
Charter8 传导边档/机制结论的 qb_source 仅有"非空字符串"校验——伪号
QB-20990101-999 零拦截静默入页(C席实测 CONFIRMED);引用数值与归档原文
一致性纯靠纪律零代码;引擎有复算能力(ia_cli compare 3/3 边 4 位小数
复现,C席实证)但装载链不调用。

本引擎四状态机(每条 qb_source → 一个状态):
  VERIFIED    归档在册 + sidecar(answer_text)可回读 + 引用数值可在归档
              原文中找到(规范化包含核验); --recompute 时复算 r 亦一致
  PARTIAL     归档在册但 sidecar 缺失(证据正文不可回读),或复算 r 一致
              而 n 漂移(归档后数据自然延展,非矛盾,如实降级)
  MISSING     归档不在册(悬空引用——C席实测的伪号场景)
  CONFLICTED  引用数值在归档原文中不存在,或 --recompute 复算 r 超容差
              (边表数字与归档证据矛盾)

离线纪律: 默认零网络(URL 活性属 `ia_cli views lint --verify-urls`
显式档位,不在本引擎);归档缺席(干净 clone)时存在性核验如实降级为
performed=False 而非静默通过。SYNTH: 前缀=测试合成标记,跳过归档核验
并在 detail 显式披露(生产边档禁用,source_verifier 输出永不隐藏该标记)。

用法:
  python3 scripts/source_verifier.py                    # 边档全量(存在性+包含)
  python3 scripts/source_verifier.py --recompute        # 追加统计复算对账
  python3 scripts/source_verifier.py --qb QB-20261110-022
  python3 scripts/source_verifier.py --archive-dir /tmp/fixture_arch
退出码: 0=全部 VERIFIED/PARTIAL; 1=存在 MISSING/CONFLICTED; 2=用法错误。
"""
import argparse
import datetime as dt
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (ROOT, os.path.join(ROOT, 'scripts')):
    if p not in sys.path:
        sys.path.insert(0, p)

import research_archive as ra          # noqa: E402
import workbench_data as wd            # noqa: E402
from fact_engine import (COUNT_UNITS, PRICE_LIKE_UNITS,  # noqa: E402
                         RATE_UNITS)

SYNTH_PREFIX = 'SYNTH:'
STATES = ('VERIFIED', 'PARTIAL', 'MISSING', 'CONFLICTED')
R_TOLERANCE = 5e-5 + 1e-12             # 边表 r=4 位小数舍入容差


# ══ 纯函数层(可测) ════════════════════════════════════════════════════
def normalize_number_text(text):
    """归档原文数值规范化: 全角负号→半角(归档用 −,边表用 -;C席注记),
    千分位逗号与全角数字分隔剔除——包含核验的字节级障碍清零。"""
    return (str(text).replace('−', '-').replace('－', '-')
            .replace(',', '').replace('，', '').replace(' ', ''))


def _r_candidate_strings(r):
    """一个 r 值在归档文表中可能出现的全部书写形式(降精度变体全收,
    防格式差异假阳性 CONFLICTED)。"""
    out = []
    for prec in (4, 3, 2, 1):
        out.append(f'{r:.{prec}f}')
        out.append(f'{r:+.{prec}f}')
    out.append(f'{r:g}')
    out.append(f'{r:+g}')
    return out


def containment_check(full_text, r, n):
    """引用数值 vs 归档原文(离线,弱核验): r 按书写变体包含,n 按字面包含。
    弱核验只证'数字在归档文字中在场',不证统计正确——强核验走 --recompute。"""
    if full_text is None:
        return {'r_found': False, 'n_found': False, 'performed': False}
    norm = normalize_number_text(full_text)
    r_found = any(s in norm for s in _r_candidate_strings(r))
    n_found = str(int(n)) in norm
    return {'r_found': r_found, 'n_found': n_found, 'performed': True}


def verify_qb_source(qb_id, archive_dir=None):
    """单条 qb_source 存在性+可回读性核验 → 四状态之一(纯离线)。

    MISSING=不在册; PARTIAL=在册但 sidecar(answer_text)不可回读,或归档
    目录本身缺席(干净clone——存在性未核验=证据不完整,如实降级非通过);
    VERIFIED=在册且证据正文可回读。SYNTH: 前缀=合成标记,跳过核验
    (detail 披露,不冒充真实归档)。"""
    if str(qb_id).startswith(SYNTH_PREFIX):
        return {'qb_id': qb_id, 'state': 'VERIFIED',
                'detail': 'SYNTH: 合成标记——归档核验跳过(测试专用;生产边档禁用)'}
    check_dir = archive_dir or ra.DEFAULT_ARCHIVE_DIR
    if not os.path.isdir(check_dir):
        return {'qb_id': qb_id, 'state': 'PARTIAL',
                'detail': '研究归档目录不存在(干净clone)——存在性未核验,'
                          '非在册证据;有归档环境重跑本引擎'}
    known = set(ra.list_query_records(check_dir))
    if qb_id not in known:
        return {'qb_id': qb_id, 'state': 'MISSING',
                'detail': '研究归档不在册(悬空引用)——见 list_query_records'}
    full = ra.load_research_full(qb_id, archive_dir=check_dir)
    at = (full or {}).get('answer_text')
    if not at:
        return {'qb_id': qb_id, 'state': 'PARTIAL',
                'detail': '在册但 sidecar(answer_text)缺失——证据正文不可回读'}
    return {'qb_id': qb_id, 'state': 'VERIFIED',
            'detail': f'在册+sidecar 可回读(answer_text {len(at)} 字符)'}


def _unit_family(unit, asset_class=''):
    """ia_cli.unit_family 同源口径(rate/price/count/other),避免拉起 CLI 层。"""
    if unit in RATE_UNITS:
        return 'rate'
    if unit in PRICE_LIKE_UNITS:
        return 'price'
    if unit in COUNT_UNITS:
        return 'count'
    return 'other'


_WINDOW_PATTERNS = (
    (re.compile(r'^全窗'), None),
    (re.compile(r'^(\d{4})起$'), 'year_start'),
    (re.compile(r'^(\d+)\s*yr'), 'years_back'),
    (re.compile(r'^月网格'), None),
)


def parse_window(window):
    """边表自由文本窗 → {'start': 'YYYY-MM-DD'|None, 'lag': int}。

    '全窗'/'月网格'→无界; '2016起'→该年1月1日; '3yr'→数据末观测自然年
    回退(C席复算口径 start 2023-11 即此); '月网格 lag6'→月频滞后 6 期。
    无法解析→ start=None+unparsed 标记(deterministic,不猜)。"""
    w = str(window or '').strip()
    lag = 0
    m = re.search(r'lag\s*(\d+)', w, re.IGNORECASE)
    if m:
        lag = int(m.group(1))
        w = re.sub(r'\s*lag\s*\d+', '', w, flags=re.IGNORECASE).strip()
    for pat, kind in _WINDOW_PATTERNS:
        m = pat.match(w) if kind else pat.search(w)
        if not m:
            continue
        if kind == 'year_start':
            return {'start': f'{m.group(1)}-01-01', 'lag': lag}
        if kind == 'years_back':
            return {'start': None, 'years_back': int(m.group(1)), 'lag': lag}
        return {'start': None, 'lag': lag}
    return {'start': None, 'lag': lag, 'unparsed': True}


def recompute_edge(edge, snap, registry, root=None):
    """统计复算对账(强核验): 与 ia_cli compare --metrics 同算法重算 r/n
    ——metric_series 取序列 → 注册表 frequency 决定对齐(exact/月网格,
    mixed 聚高频侧) → 窗口过滤 → paired_unit_changes(单位感知) → pearson。
    C席已证引擎 3/3 边 4 位小数复现;本函数把该能力接进装载核验链。

    返回 {'available': True, 'r', 'n', 'basis', 'window_start'} 或
    {'available': False, 'reason'}(序列缺失/单位不可比等如实拒算)。"""
    if snap is None or registry is None:
        return {'available': False, 'reason': '无本地快照(干净clone/未采集)——复算对账不可执行'}
    import correlation_calculator as cc
    import research_history_query as rhq
    ids = (edge.get('from'), edge.get('to'))
    metas = [registry['by_id'].get(i) or {} for i in ids]
    if any(not m for m in metas):
        return {'available': False, 'reason': f'指标不在注册表: {[i for i, m in zip(ids, metas) if not m]}'}
    fams = [_unit_family(m.get('unit', ''), m.get('asset_class', '')) for m in metas]
    if 'other' in fams:
        return {'available': False, 'reason': f'单位族不可比(other): {fams}'}
    series = []
    for i in ids:
        s, err = wd.metric_series(i, snap, root)
        if s is None:
            return {'available': False, 'reason': f'{i} 序列不可得: {err}'}
        series.append({'dates': list(s['dates']), 'values': list(s['values'])})
    win = parse_window(edge.get('window'))
    if win.get('years_back'):
        last_ymd = max(series[0]['dates'][-1], series[1]['dates'][-1])
        win['start'] = wd.horizon_start(str(last_ymd).replace('-', ''),
                                        f"{win['years_back']}y")
    if win.get('start'):
        kept = []
        for s in series:
            idx = [k for k, d in enumerate(s['dates']) if d >= win['start']]
            if not idx:
                return {'available': False,
                        'reason': f"窗 {win['start']} 起一侧无观测(数据覆盖不足)"}
            s['dates'] = [s['dates'][k] for k in idx]
            s['values'] = [s['values'][k] for k in idx]
            kept.append(len(idx))
    freqs = [m.get('frequency') for m in metas]
    pair_a, pair_b = series[0], series[1]
    align_mode = 'exact_date'
    if freqs[0] and freqs[1] and freqs[0] != freqs[1] and 'monthly' in freqs:
        if freqs[0] == 'monthly':
            grid = rhq.align_to_month(pair_b)
            pair_b = {'dates': grid['grid_keys'], 'values': grid['values']}
            pair_a = {'dates': [str(d)[:7] for d in pair_a['dates']],
                      'values': pair_a['values']}
        else:
            grid = rhq.align_to_month(pair_a)
            pair_a = {'dates': grid['grid_keys'], 'values': grid['values']}
            pair_b = {'dates': [str(d)[:7] for d in pair_b['dates']],
                      'values': pair_b['values']}
        align_mode = 'month_grid'
    elif freqs[0] == freqs[1] == 'monthly':
        ga, gb = rhq.align_to_month(pair_a), rhq.align_to_month(pair_b)
        pair_a = {'dates': ga['grid_keys'], 'values': ga['values']}
        pair_b = {'dates': gb['grid_keys'], 'values': gb['values']}
        align_mode = 'month_grid'
    try:
        paired, _common = cc.paired_unit_changes(pair_a, fams[0], pair_b, fams[1])
    except ValueError as e:
        return {'available': False, 'reason': f'配对失败: {e}'}
    if not paired:
        return {'available': False, 'reason': '共同观测<3——变化对不足'}
    ca, cb = paired['changes_a'], paired['changes_b']
    if win.get('lag'):
        # ia_cli --lag 同口径: 变化序列上索引平移 (ca[i], cb[i−k]),k>0=B 领先。
        # 边档 lag 方向未结构化登记→双向试算对账(哪个方向命中边表 r 即该方向,
        # 双向都不中=真 CONFLICTED;direction 字段如实披露命中方向)。
        k = win['lag']
        out = {}
        for sign in (+1, -1):
            idx = [i for i in range(len(ca)) if 0 <= i - sign * k < len(cb)]
            if len(idx) >= 3:
                out[sign] = {'r': cc.pearson([ca[i] for i in idx],
                                             [cb[i - sign * k] for i in idx]),
                             'n': len(idx)}
        if not out:
            return {'available': False,
                    'reason': f'lag±{k} 后变化对均不足(<3)'}
        return {'available': True, 'lag_candidates': out,
                'basis': f"{fams[0]}×{fams[1]}", 'align': align_mode,
                'window_start': win.get('start')}
    r = cc.pearson(ca, cb)
    return {'available': True, 'r': r, 'n': paired['n_change_pairs'],
            'basis': f"{fams[0]}×{fams[1]}", 'align': align_mode,
            'window_start': win.get('start')}


# ══ 边档全量核验 ══════════════════════════════════════════════════════
def _iter_cited(doc):
    """边档中全部 (kind, 对象, r, n) 引用: edges(带 r/n 复算面) + 机制结论
    (mechanism_findings 无独立 r/n,只做存在性) + 结构性结论。"""
    for e in doc.get('edges') or []:
        yield 'edge', e, e.get('r'), e.get('n')
    for f in doc.get('mechanism_findings') or []:
        yield 'mechanism', f, None, None
    ss = doc.get('structural_summary') or {}
    if ss.get('qb_source'):
        yield 'structural', {'id': str(ss.get('text', ''))[:24], **ss}, None, None


def verify_edges(archive_dir=None, root=None, recompute=False, edges_path=None,
                 snap=None, reg=None):
    """边档全量核验: 存在性(四状态)+包含核验+可选复算对账 → 汇总报告。

    归档缺席(目录不存在)时存在性核验 performed=False 如实降级——
    与 workbench_data.transmission_edges 双轨同语义,禁静默通过。
    snap/reg 可注入(测试合成快照;默认 --recompute 时自动装载本地)。"""
    path = edges_path or os.path.join(root or ROOT, 'config',
                                      'transmission_edges.json')
    with open(path, encoding='utf-8') as f:
        doc = json.load(f)
    resolved = archive_dir or ra.DEFAULT_ARCHIVE_DIR
    archive_present = os.path.isdir(resolved)
    recompute_note = None
    if recompute and snap is None:
        snap, note = wd.latest_snapshot(root or ROOT)
        reg = wd.load_registry(root or ROOT)
        if snap is None:
            recompute_note = f'无本地快照({note})——复算对账跳过'
    refs, rows = {}, []
    for kind, obj, r, n in _iter_cited(doc):
        ident = obj.get('edge_id') or obj.get('mechanism_label') or obj.get('id')
        qb = obj.get('qb_source')
        if qb in refs:
            src = refs[qb]
        else:
            src = verify_qb_source(qb, resolved)
            refs[qb] = src
        state, extra = src['state'], {}
        if src['state'] == 'VERIFIED' and r is not None and archive_present:
            full = ra.load_research_full(qb, archive_dir=resolved) or {}
            cont = containment_check(full.get('answer_text'), r, n)
            extra['containment'] = cont
            if not cont['r_found'] or not cont['n_found']:
                state = 'CONFLICTED'
                extra['conflict'] = ('引用数值未在归档原文找到'
                                     f"(r_found={cont['r_found']},"
                                     f"n_found={cont['n_found']})")
        if recompute and kind == 'edge' and src['state'] in ('VERIFIED', 'PARTIAL'):
            if r is None:
                rc = {'available': False, 'reason': '无 r 引用'}
            else:
                rc = recompute_edge(obj, snap, reg, root or ROOT)
            extra['recompute'] = rc
            if rc.get('available') and rc.get('lag_candidates'):
                # lag 边: 双向候选任一命中即一致(方向随行披露)
                hit = [(s, c) for s, c in rc['lag_candidates'].items()
                       if abs(c['r'] - float(r)) <= R_TOLERANCE]
                if hit:
                    extra['r_match'] = True
                    extra['n_match'] = hit[0][1]['n'] == int(n)
                    rc['direction_hit'] = ('B领先' if hit[0][0] > 0 else 'A领先')
                else:
                    state = 'CONFLICTED'
                    extra['r_match'] = False
                    extra['conflict'] = (
                        '复算 lag 双向 r 候选 '
                        f"{ {s: round(c['r'], 4) for s, c in rc['lag_candidates'].items()} }"
                        f" vs 边表 {r}(双向均超容差)")
            elif rc.get('available'):
                r_ok = abs(rc['r'] - float(r)) <= R_TOLERANCE
                n_ok = rc['n'] == int(n)
                extra['r_match'], extra['n_match'] = r_ok, n_ok
                if not r_ok:
                    state = 'CONFLICTED'
                    extra['conflict'] = (f"复算 r={rc['r']:.6f} vs 边表 {r}"
                                         '(超 4 位小数容差)')
                elif not n_ok and state == 'VERIFIED':
                    state = 'PARTIAL'
                    extra['drift'] = (f"复算 n={rc['n']} vs 边表 {n}"
                                      '(归档后数据延展,如实降级非矛盾)')
        rows.append({'kind': kind, 'id': ident, 'qb_source': qb,
                     'state': state, **extra})
    summary = {s: sum(1 for x in rows if x['state'] == s) for s in STATES}
    return {'edges_path': path, 'archive_dir': resolved,
            'archive_present': archive_present,
            'existence_check': {'performed': archive_present,
                                'note': None if archive_present else (
                                    '归档目录不存在(干净clone)——存在性核验跳过;'
                                    '有归档环境执行 python3 scripts/source_verifier.py')},
            'refs': refs, 'results': rows, 'summary': summary,
            'recompute': {'requested': bool(recompute), 'note': recompute_note}}


# ══ CLI ═══════════════════════════════════════════════════════════════
def main(argv=None):
    p = argparse.ArgumentParser(
        prog='source_verifier.py',
        description='来源验证引擎(Charter9 P0-3): qb_source 四状态机'
                    '(VERIFIED/PARTIAL/MISSING/CONFLICTED)+数值包含核验'
                    '+可选统计复算对账;默认零网络')
    p.add_argument('--edges', action='store_true',
                   help='核验边档 config/transmission_edges.json 全量引用(默认)')
    p.add_argument('--qb', action='append', default=[],
                   help='核验指定 qb_source(可多次)')
    p.add_argument('--archive-dir',
                   help='研究归档目录(默认 data/research/research_archive;'
                        '测试传合成归档)')
    p.add_argument('--recompute', action='store_true',
                   help='复算对账(与 ia_cli compare 同算法重算边 r;需本地数据)')
    p.add_argument('--root', help='项目根(默认脚本上级)')
    p.add_argument('--json', action='store_true', help='机器可读 JSON 输出')
    args = p.parse_args(argv)
    if not args.qb:
        args.edges = True
    report = {'qb_checks': [], 'edges_report': None}
    worst = 0
    for qb in args.qb:
        res = verify_qb_source(qb, args.archive_dir)
        report['qb_checks'].append(res)
        if res['state'] in ('MISSING', 'CONFLICTED'):
            worst = 1
        print(f"[{res['state']:11s}] {res['qb_id']}  {res['detail']}")
    if args.edges:
        rep = verify_edges(archive_dir=args.archive_dir, root=args.root,
                           recompute=args.recompute)
        report['edges_report'] = rep
        bad = [x for x in rep['results'] if x['state'] in ('MISSING', 'CONFLICTED')]
        if bad:
            worst = 1
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
            return worst
        print('─' * 64)
        for x in rep['results']:
            line = f"[{x['state']:11s}] {x['kind']:<10s} {x['id']} ← {x['qb_source']}"
            if x.get('conflict'):
                line += f"  ⚠ {x['conflict']}"
            if x.get('drift'):
                line += f"  ~ {x['drift']}"
            if x.get('recompute', {}).get('available'):
                rc = x['recompute']
                if rc.get('lag_candidates'):
                    line += (f"  复算 lag双向 "
                             f"{ {s: round(c['r'], 4) for s, c in rc['lag_candidates'].items()} }"
                             f"({'r✓' if x.get('r_match') else 'r✗'})")
                else:
                    line += (f"  复算 r={rc['r']:.4f} n={rc['n']}"
                             f"({'r✓' if x.get('r_match') else 'r✗'}"
                             f"{'n✓' if x.get('n_match') else 'n~'})")
            print(line)
        print('─' * 64)
        print(f"汇总: {rep['summary']} · 归档在场={rep['archive_present']}")
        if not rep['existence_check']['performed']:
            print(f"注: {rep['existence_check']['note']}")
        if rep['recompute']['note']:
            print(f"注: {rep['recompute']['note']}")
    return worst


if __name__ == '__main__':
    sys.exit(main())
