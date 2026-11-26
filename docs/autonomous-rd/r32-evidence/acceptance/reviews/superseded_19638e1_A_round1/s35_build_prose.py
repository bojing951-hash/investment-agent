#!/usr/bin/python3 -I
"""Seat-internal: assemble PROSE-round1.md from the seat ledger, the verdict file and the two fixed-text
parts written by the seat.  Every table of points is generated row by row from the ledger (nothing is
retyped); the script asserts that the ledger counts equal the counts recorded in the verdict and that no
placeholder is left unreplaced.  The only file written is the output path (argv[5]).

Usage:
  python3 -I s35_build_prose.py <points_all.jsonl> <VERDICT-round1.json> <prose_head.md> <prose_tail.md> <out.md>
"""
import json
import re
import sys
from collections import Counter

SECTIONS = [('anchors', u'锚点(三时点对照)'), ('monthly', u'月频'), ('daily', u'日频'),
            ('history', u'历史段'), ('sync', u'同步面'), ('misc', u'其他')]
ANCHORS = [('12m', u'12个月前'), ('3m', u'3个月前'), ('now', u'最新一期')]
REGIONS = [('US', u'美国'), ('CN', u'中国'), ('EA', u'欧元区'), ('JP', u'日本')]
DIMS = [('growth', u'增长'), ('inflation', u'通胀'), ('policy', u'政策')]
REG = {
    'US_REAL_GDP': (u'美国', u'增长'), 'UNEMPLOYMENT': (u'美国', u'增长'), 'INDPRO': (u'美国', u'增长'),
    'CPI': (u'美国', u'通胀'), 'CORE_CPI': (u'美国', u'通胀'), 'CORE_PCE': (u'美国', u'通胀'),
    'DFEDTARU': (u'美国', u'政策'), 'DFF': (u'美国', u'政策'),
    'CN_PMI_MFG': (u'中国', u'增长'), 'CN_CPI_YOY': (u'中国', u'通胀'), 'CN_PPI_YOY': (u'中国', u'通胀'),
    'CN_POLICY_OVERNIGHT': (u'中国', u'政策'), 'CN_OMO_7D': (u'中国', u'政策'), 'CN_LPR_1Y': (u'中国', u'政策'),
    'EA_REAL_GDP_YOY': (u'欧元区', u'增长'), 'EA_HICP_YOY': (u'欧元区', u'通胀'),
    'ECB_MRO': (u'欧元区', u'政策'), 'ECB_DFR': (u'欧元区', u'政策'),
    'JP_REAL_GDP_YOY': (u'日本', u'增长'), 'JP_CPI_YOY': (u'日本', u'通胀'), 'JP_CPI_TOKYO_YOY': (u'日本', u'通胀'),
    'JP_POLICY_RATE': (u'日本', u'政策'),
}
CAND = {
    'CN_PPI_YOY': (u'中国', u'通胀'), 'CN_PMI_MFG': (u'中国', u'增长'), 'CPI': (u'美国', u'通胀'),
    'JP_CPI_YOY': (u'日本', u'通胀'), 'EA_HICP_YOY': (u'欧元区', u'通胀'), 'JP_CPI_TOKYO_YOY': (u'日本', u'通胀'),
    'CN_CPI_YOY': (u'中国', u'通胀'), 'INDPRO': (u'美国', u'增长'), 'CORE_CPI': (u'美国', u'通胀'),
}
MINOR_KEYS = ['transmission[0].links[0]', 'mechanism_chains[0].links[1]', 'contradictions[0].statement',
              'other_regions_sync', 'trigger.condition', 'evidence_refs[3]', 'headline_conclusion', 'GDP', 'CORE_CPI']
NIT_KEYS = ['transmission[1].links[0]', 'turning_supplement[0]', u'四地最高', u'制造业 PMI', 'turnings[1].first_mover',
            u'2026-08至10加速', 'turnings[0].first_mover;turnings[1].first_mover', 'quality_gate_notes[3]',
            u'12个月前锚', 'observed_fact', 'scenarios[1].rows.falsification.threshold']
P_ANCHOR = re.compile(r'^([A-Z0-9_]+)@(12m|3m|now):(value|obs_month|engine_cell_value|engine_cell_obs_month|yoy_vs_engine_cell)$')
P_CAND = re.compile(r'^candidate\[(\d)\] ([A-Z0-9_]+) (value_before|value_after|delta|window = seat max \|3-apart change\|)(?: \((\S*)\))?$')
P_SYNC = re.compile(r'^sync (\S+) (US|CN|EA|JP) (growth|inflation|policy) (label|direction)$')
P_SYNCJ = re.compile(r'^sync (\S+) judgment (CN|EA|JP) inflation label$')
P_EXP = re.compile(r'^(2025-03|2022-06|2023-10) (3m|6m|12m) ([A-Z0-9_]+) \((%|pp)\)$')
P_AFT = re.compile(r'^(2025-03|2022-06|2023-10) engine aftermath ([A-Z0-9_]+) (1m|3m|6m|12m)$')
PERIODS = ['2025-03', '2022-06', '2023-10']


def esc(s):
    return str(s).replace('|', '\\|').replace('\n', ' ').replace('\r', '')


def fmt(v, info=False):
    if info and v is None:
        return u'—(仅席位直算)'
    if v is None:
        return u'不可得(null)'
    if isinstance(v, bool):
        return 'True' if v else 'False'
    if isinstance(v, (list, dict)):
        return json.dumps(v, ensure_ascii=False)
    if v == '':
        return u'∅(空串)'
    return str(v)


def is_info(r):
    return r['reported'] is None and r['computed'] is not None


def status(r):
    if is_info(r):
        return u'信息行(不计入)'
    return u'一致' if r['ok'] else u'偏离'


def row_cells(r, n):
    return u'| %d | %s | %s | %s | %s | %s | %s |' % (
        n, esc(r['id']), esc(r['src']), esc(fmt(r['computed'])), esc(fmt(r['reported'], is_info(r))),
        status(r), esc(r.get('note', '')))


def main():
    rows = [json.loads(x) for x in open(sys.argv[1], encoding='utf-8') if x.strip()]
    v = json.load(open(sys.argv[2], encoding='utf-8'))
    head = open(sys.argv[3], encoding='utf-8').read()
    tail = open(sys.argv[4], encoding='utf-8').read()
    counted = [r for r in rows if not is_info(r)]
    bad = [r for r in counted if not r['ok']]
    info = len(rows) - len(counted)
    assert len(counted) == v['recompute_points'] and len(bad) == v['recompute_mismatches'], 'counts differ from verdict'
    by_id = {}
    for r in rows:
        by_id.setdefault(r['id'], []).append(r)

    def one(iid):
        # a point id is normally unique; the few ids recorded twice (same observation cited at two
        # places of the judgment) are never the ids looked up here
        assert len(by_id.get(iid, [])) == 1, (iid, len(by_id.get(iid, [])))
        return by_id[iid][0]

    dup = sorted(k for k, lst in by_id.items() if len(lst) > 1)
    for k in dup:
        vals = set((json.dumps(r['computed']), json.dumps(r['reported']), r['ok'], r['section']) for r in by_id[k])
        assert len(vals) == 1, (k, vals)
    assert set(r['section'] for r in rows) <= set(k for k, _ in SECTIONS)

    # ---- head placeholders ----
    counts = u'计点 %d / 偏离 %d(信息行 %d 不计入)' % (len(counted), len(bad), info)
    assert '\n' not in v['notes']
    # the fixed-text part already carries the blockquote marker in front of the placeholder
    assert v['notes'].startswith(u'零上下文独立席') and not v['notes'].startswith('>')
    notes = v['notes']
    lines = [u'| 节 | 计点行 | 一致 | 偏离 | 信息行(不计入) |', u'|---|---|---|---|---|']
    tot = [0, 0, 0, 0]
    for key, name in SECTIONS:
        rs = [r for r in rows if r['section'] == key]
        c = [r for r in rs if not is_info(r)]
        b = [r for r in c if not r['ok']]
        vals = [len(c), len(c) - len(b), len(b), len(rs) - len(c)]
        tot = [a + b2 for a, b2 in zip(tot, vals)]
        lines.append(u'| %s | %d | %d | %d | %d |' % ((name,) + tuple(vals)))
    lines.append(u'| 合计 | %d | %d | %d | %d |' % tuple(tot))
    summary = u'\n'.join(lines)

    pts = []
    n = 0
    for key, name in SECTIONS:
        rs = [r for r in rows if r['section'] == key]
        c = [r for r in rs if not is_info(r)]
        b = [r for r in c if not r['ok']]
        pts.append(u'#### 1.2.%d %s(计点 %d 行: 一致 %d、偏离 %d;信息行 %d)' % (
            SECTIONS.index((key, name)) + 1, name, len(c), len(c) - len(b), len(b), len(rs) - len(c)))
        pts.append(u'')
        pts.append(u'| # | 点 | 出处键 | 直算值 | 报告值 | 一致与否 | 备注 |')
        pts.append(u'|---|---|---|---|---|---|---|')
        for r in rs:
            n += 1
            pts.append(row_cells(r, n))
        pts.append(u'')
    assert n == len(rows)
    points = u'\n'.join(pts).rstrip('\n')

    # ---- attacks ----
    lines = [u'| 序号与对象 | 攻击问句 | 结果 |', u'|---|---|---|']
    for a in v['counterexamples_sought']:
        # the question itself may contain an arrow ("A→B"), so it is split at the first "?→"
        m = re.match(r'^(反方攻击 \d+ \([^)]*\)): (.*?)\?→(.*)$', a, re.S)
        assert m, a[:40]
        assert a.count(u'?→') == 1, a[:40]
        q, res = m.group(2), m.group(3)
        lines.append(u'| %s | %s? | %s |' % (esc(m.group(1)), esc(q.rstrip()), esc(res.strip())))
    assert [int(re.match(r'^反方攻击 (\d+)', a).group(1)) for a in v['counterexamples_sought']] == list(range(1, len(v['counterexamples_sought']) + 1))
    attacks = u'\n'.join(lines)
    n_attacks = len(v['counterexamples_sought'])

    # ---- items ----
    maj = [it for it in v['items'] if it['severity'] == 'MAJOR']
    minor = [it for it in v['items'] if it['severity'] == 'MINOR']
    nit = [it for it in v['items'] if it['severity'] == 'NIT']
    assert len(maj) + len(minor) + len(nit) == len(v['items'])
    assert not maj and v['must_fix'] == []
    # the fixed-text parts refer to MINOR-k / NIT-k by order; pin that order
    for lst, keys in ((minor, MINOR_KEYS), (nit, NIT_KEYS)):
        assert len(lst) == len(keys), (len(lst), len(keys))
        for k, (it, key) in enumerate(zip(lst, keys), 1):
            assert key in it['where'] or key in it['note'], (k, key, it['where'][:80])
    out = [u'**MAJOR(%d 条)**: 无——must_fix 为空。' % len(maj)]
    for sev, lst in (('MINOR', minor), ('NIT', nit)):
        out.append(u'')
        out.append(u'**%s(%d 条;不构成阻断)**' % (sev, len(lst)))
        for k, it in enumerate(lst, 1):
            assert sorted(it.keys()) == ['fix', 'note', 'original', 'severity', 'where'], sorted(it.keys())
            out.append(u'')
            out.append(u'- **%s-%d**' % (sev, k))
            out.append(u'  - 位置: %s' % esc(it['where']))
            out.append(u'  - 问题: %s' % esc(it['note']))
            out.append(u'  - 原句: 「%s」' % esc(it['original']))
            out.append(u'  - 改句(建议): 「%s」' % esc(it['fix']))
    items = u'\n'.join(out)

    # ---- 5.2 anchor table ----
    used = set()
    lines = [u'| 地区 | 维度 | 指标 | 锚 | 值: 报告 | 值: 直算 | 观测月: 报告 | 观测月: 直算 | 引擎格值 | 引擎格观测月 | '
             u'同比: 直算 | 同比: 引擎格 | 一致与否 |',
             u'|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    n_ok = n_abs = 0
    for metric, (reg, dim) in REG.items():
        for a, an in ANCHORS:
            part = {kind: one('%s@%s:%s' % (metric, a, kind)) for kind in
                    ('value', 'obs_month', 'engine_cell_value', 'engine_cell_obs_month')
                    if '%s@%s:%s' % (metric, a, kind) in by_id}
            yoy = one('%s@%s:yoy_vs_engine_cell' % (metric, a)) if '%s@%s:yoy_vs_engine_cell' % (metric, a) in by_id else None
            if yoy:
                part['yoy'] = yoy
            for r in part.values():
                used.add(r['id'])
            if 'value' not in part:
                assert not part, part
                n_abs += 1
                lines.append(u'| %s | %s | %s | %s | — | — | — | — | 缺席(no_published_observation_on_or_before_anchor) | — | — | — | 诚实缺席格(不计点) |' % (
                    reg, dim, metric, an))
                continue
            st = u'一致' if all(r['ok'] for r in part.values()) else u'偏离'
            n_ok += 1
            lines.append(u'| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                reg, dim, metric, an, fmt(part['value']['reported']), fmt(part['value']['computed']),
                fmt(part['obs_month']['reported']), fmt(part['obs_month']['computed']),
                fmt(part['engine_cell_value']['reported']), fmt(part['engine_cell_obs_month']['reported']),
                fmt(part['yoy']['computed']) if yoy else u'—', fmt(part['yoy']['reported']) if yoy else u'—', st))
    assert n_ok == 63 and n_abs == 3, (n_ok, n_abs)
    anchor_other = [r for r in rows if r['section'] == 'anchors' and r['id'] not in used and P_ANCHOR.match(r['id'])]
    assert not anchor_other, [r['id'] for r in anchor_other]
    anchor_table = u'\n'.join(lines)
    anchor_table += (u'\n\n「值: 报告」=判断档 anchor_echo 回贴值;「引擎格值」=report.json research_plan.point_values.cells;'
                     u'「同比」=水平序列的同比派生值(直算自 series_store 同月一年前,报告侧为引擎格 derived_yoy_pct),无同比行的格为同比序列本身。\n\n'
                     u'锚点节其余行(非逐格行):\n\n')
    extra = [r for r in rows if r['section'] == 'anchors' and r['id'] not in used]
    assert len(extra) == 8, [r['id'] for r in extra]
    lines = [u'| 点 | 出处键 | 直算值 | 报告值 | 一致与否 | 备注 |', u'|---|---|---|---|---|---|']
    for r in extra:
        lines.append(u'| %s | %s | %s | %s | %s | %s |' % (
            esc(r['id']), esc(r['src']), esc(fmt(r['computed'])), esc(fmt(r['reported'], is_info(r))), status(r), esc(r.get('note', ''))))
    anchor_table += u'\n'.join(lines)

    # ---- 5.3 candidate table ----
    used = set()
    lines = [u'| 序 | 指标 | 地区/维度 | 窗口: 引擎 | 窗口: 直算 | 前值: 引擎 | 前值: 直算 | 后值: 引擎 | 后值: 直算 | Δ: 引擎 | Δ: 直算 | 一致与否 |',
             u'|---|---|---|---|---|---|---|---|---|---|---|---|']
    for i in range(9):
        part = {}
        for r in rows:
            m = P_CAND.match(r['id'])
            if m and int(m.group(1)) == i:
                assert m.group(3) not in part, ('duplicate', r['id'])
                part[m.group(3)] = r
                used.add(r['id'])
        assert sorted(part) == sorted(['window = seat max |3-apart change|', 'value_before', 'value_after', 'delta']), (i, sorted(part))
        w, vb, va, d = (part[k] for k in ('window = seat max |3-apart change|', 'value_before', 'value_after', 'delta'))
        names = set(P_CAND.match(r['id']).group(2) for r in part.values())
        assert len(names) == 1, (i, names)
        name = names.pop()
        assert name in CAND, name
        st = u'一致' if all(r['ok'] for r in part.values()) else u'偏离(%s)' % u', '.join(k for k, r in part.items() if not r['ok'])
        lines.append(u'| %d | %s | %s/%s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            i + 1, name, CAND[name][0], CAND[name][1], fmt(w['reported']), fmt(w['computed']),
            fmt(vb['reported']), fmt(vb['computed']), fmt(va['reported']), fmt(va['computed']),
            fmt(d['reported']), fmt(d['computed']), st))
    assert len(used) == 36, len(used)
    candidate_table = (u'窗口=引擎候选窗(相隔三个观测的最大变化所在月);「引擎」=report.json turning_candidates.candidates / 研判席工单 '
                       u'turning_candidates_top9;「直算」=本席按同一规则自冻结快照重算。唯一偏离见第 8 行。\n\n') + u'\n'.join(lines)
    cand_other = [r for r in rows if r['section'] == 'monthly' and r['id'] not in used
                  and (r['id'].startswith('candidate') or r['id'].startswith('turnings['))]
    assert len(cand_other) == 4, [r['id'] for r in cand_other]
    candidate_table += u'\n\n候选面相关的其余 4 行:\n\n'
    lines = [u'| 点 | 出处键 | 直算值 | 报告值 | 一致与否 | 备注 |', u'|---|---|---|---|---|---|']
    for r in cand_other:
        lines.append(u'| %s | %s | %s | %s | %s | %s |' % (
            esc(r['id']), esc(r['src']), esc(fmt(r['computed'])), esc(fmt(r['reported'], is_info(r))), status(r), esc(r.get('note', ''))))
    candidate_table += u'\n'.join(lines)

    # ---- 5.4 sync table ----
    used = set()
    lines = [u'| 段 | 地区 | 维度 | 标签: 直算 | 标签: 引擎 | 底层读数变化(席位直算,信息行) | 判断档通胀维标签: 直算 | 判断档通胀维标签: 报告 | 一致与否 |',
             u'|---|---|---|---|---|---|---|---|---|']
    for p in PERIODS:
        for rk, rn in REGIONS:
            for dk, dn in DIMS:
                lab = one('sync %s %s %s label' % (p, rk, dk))
                dire = one('sync %s %s %s direction' % (p, rk, dk))
                used.update([lab['id'], dire['id']])
                assert is_info(dire) and not is_info(lab)
                jl = one('sync %s judgment %s inflation label' % (p, rk)) if ('sync %s judgment %s inflation label' % (p, rk)) in by_id else None
                if jl:
                    used.add(jl['id'])
                parts = [lab] + ([jl] if jl and dk == 'inflation' else [])
                jshow = jl if (jl and dk == 'inflation') else None
                lines.append(u'| %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                    p, rn, dn, fmt(lab['computed']), fmt(lab['reported']), fmt(dire['computed']),
                    fmt(jshow['computed']) if jshow else u'—', fmt(jshow['reported']) if jshow else u'—',
                    u'一致' if all(r['ok'] for r in parts) else u'偏离'))
    sync_rest = [r for r in rows if r['section'] == 'sync' and r['id'] not in used]
    assert not sync_rest, [r['id'] for r in sync_rest]
    sync_table = (u'「标签: 引擎」=report.json steps[60] S5_compare 信封的地区×维度同步面(相对美国);「标签: 直算」=本席自 series_store 重算;'
                  u'「判断档通胀维标签」=判断档 history_periods[*].other_regions_sync 文字所引标签(报告),「直算」=按引擎面规则应取的通胀维标签,只列在通胀行;美国为参照系,其自身无同步标签。\n\n') + u'\n'.join(lines)

    # ---- 5.5 ex-post table ----
    exp = {}
    units = {}
    for r in rows:
        m = P_EXP.match(r['id'])
        if m:
            exp[(m.group(1), m.group(2), m.group(3))] = r
            units.setdefault(m.group(3), m.group(4))
    assert len(exp) == 99, len(exp)
    metrics = []
    for r in rows:
        m = P_EXP.match(r['id'])
        if m and m.group(3) not in metrics:
            metrics.append(m.group(3))
    assert len(metrics) == 11, metrics
    lines = [u'| 指标(单位) | ' + u' | '.join('%s %s' % (p, w) for p in PERIODS for w in ('3个月', '6个月', '12个月')) + u' |',
             u'|---|' + u'---|' * 9]
    for mt in metrics:
        cells = []
        for p in PERIODS:
            for w in ('3m', '6m', '12m'):
                r = exp[(p, w, mt)]
                cells.append(u'%s / %s%s' % (fmt(r['reported']), fmt(r['computed']), u'' if r['ok'] else u' ✗偏离'))
        lines.append(u'| %s(%s) | %s |' % (mt, units[mt], u' | '.join(cells)))
    expost_table = (u'每格=「报告值 / 直算值」;报告值=判断档 ex_post 文字(两位小数、带符号),直算值=series_store 自然月末→锚+N 月月末的变化率(%)或差(pp),未舍入值见第 1.2 节;'
                    u'99 格全部一致。\n\n') + u'\n'.join(lines)

    aft = {}
    for r in rows:
        m = P_AFT.match(r['id'])
        if m:
            aft[(m.group(1), m.group(2), m.group(3))] = r
    assert len(aft) == 48, len(aft)
    a_metrics = []
    for r in rows:
        m = P_AFT.match(r['id'])
        if m and m.group(2) not in a_metrics:
            a_metrics.append(m.group(2))
    lines = [u'| 资产 | ' + u' | '.join('%s %s' % (p, w) for p in PERIODS for w in ('1个月', '3个月', '6个月', '12个月')) + u' |',
             u'|---|' + u'---|' * 12]
    for mt in a_metrics:
        cells = []
        for p in PERIODS:
            for w in ('1m', '3m', '6m', '12m'):
                r = aft.get((p, mt, w))
                cells.append(u'—' if r is None else u'%s / %s%s' % (fmt(r['reported']), fmt(r['computed']), u'' if r['ok'] else u' ✗偏离'))
        lines.append(u'| %s | %s |' % (mt, u' | '.join(cells)))
    aftermath_table = (u'每格=「报告值 / 直算值」(%,引擎口径: 锚后首个观测→锚+N 月后首个观测);报告值=report.json steps[61] 相似检索面事后块(研判席工单 ex_post_offsets),'
                       u'直算值=本席按引擎口径自 series_store 重算;48 格全部一致。\n\n') + u'\n'.join(lines)

    # ---- assemble ----
    doc = head + tail
    repl = [('{{COUNTS}}', counts), ('{{NOTES}}', notes), ('{{SUMMARY_TABLE}}', summary), ('{{POINTS}}', points),
            ('{{N_ATTACKS}}', str(n_attacks)), ('{{ATTACKS}}', attacks), ('{{ITEMS}}', items),
            ('{{ANCHOR_TABLE}}', anchor_table), ('{{CANDIDATE_TABLE}}', candidate_table), ('{{SYNC_TABLE}}', sync_table),
            ('{{EXPOST_TABLE}}', expost_table), ('{{ENGINE_AFTERMATH_TABLE}}', aftermath_table)]
    for ph, text in repl:
        assert doc.count(ph) == 1, (ph, doc.count(ph))
        doc = doc.replace(ph, text)
    assert '{{' not in doc and '}}' not in doc
    with open(sys.argv[5], 'w', encoding='utf-8') as f:
        f.write(doc)
    print('written %s: %d chars, %d lines' % (sys.argv[5], len(doc), doc.count('\n') + 1))
    print('counts: %s; sections counted: %s; attacks: %d; items: %s' % (
        counts, dict(Counter(r['section'] for r in counted)), n_attacks,
        dict(Counter(it['severity'] for it in v['items']))))


if __name__ == '__main__':
    main()
