# -*- coding: utf-8 -*-
# x80_probe4.py — 终装配前的二次自检探针(只读受审面; 只打印)
# 用法: python3 -I x80_probe4.py <RUN_DIR> <SNAPSHOT_JSON> <B_DIR>
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r00_common import *

NL = chr(10)


def main():
    RUN, SNAPP, B = sys.argv[1], sys.argv[2], sys.argv[3]

    def F(n):
        return os.path.join(RUN, n)

    aj = load(F('agent_judgment.json'))
    rm = aj['reader_map']
    c = aj['l3']['contradictions']
    out = []
    P = out.append
    P('T2.first_mover: ' + rm['turnings'][2]['first_mover'])
    P('T0.follow_or_diverge: ' + rm['turnings'][0]['follow_or_diverge'])
    P('L0.observed_fact: ' + rm['transmission'][0]['links'][0]['observed_fact'])
    P('L0.causal_hypothesis: ' + rm['transmission'][0]['links'][0]['causal_hypothesis'])
    P('C1.statement: ' + c[0]['statement'])
    P('C1.competing: ' + json.dumps(c[0].get('competing_explanations'), ensure_ascii=False))
    P('C3.statement: ' + c[2]['statement'])
    P('C3.competing: ' + json.dumps(c[2].get('competing_explanations'), ensure_ascii=False))
    P('HL: ' + rm['headline_conclusion'])
    for i, q in enumerate(aj['quality_gate_notes']):
        P('QG[%d]: %s' % (i, q))
    P('HZ: ' + str(rm.get('history_zero_case_note')))
    P('M1L2: ' + aj['l3']['mechanism_chains'][0]['links'][2]['text'])
    for i, t in enumerate(rm['turnings']):
        P('T%d.narrative: %s' % (i, t['narrative']))
    for i, l in enumerate(rm['transmission'][0]['links']):
        P('L%d.verdict_note: %s' % (i, l['verdict_note']))
    P('DECL: ' + json.dumps(aj['agent_declaration'], ensure_ascii=False))
    for fn in ('MAP_REPORT.md', 'FULL_REPORT.md', 'report.md'):
        for i, l in enumerate(open(F(fn), encoding='utf-8').read().split(NL)):
            if ('语义审查' in l or '席位' in l):
                P('%s L%d: %s' % (fn, i + 1, l[:500]))
    sn = Snap(load(SNAPP))
    for sid in ('JP_CPI_YOY', 'EA_HICP_YOY', 'CPI', 'CORE_CPI', 'BEI_10Y'):
        P('SERIES %s: %s' % (sid, [(d, round(v, 4)) for d, v in sn.win(sid, '2026-01-01', '2026-12-31')]))
    P('BEI_10Y 2026-02-27/05-04/02-02/05-29: %s %s %s %s' % (sn.val('BEI_10Y', '2026-02-27'), sn.val('BEI_10Y', '2026-05-04'), sn.val('BEI_10Y', '2026-02-02'), sn.val('BEI_10Y', '2026-05-29')))
    txt = NL.join(out)
    with open(os.path.join(B, 'x80_probe4.txt'), 'w', encoding='utf-8') as f:
        f.write(txt)
    print(txt)


main()
