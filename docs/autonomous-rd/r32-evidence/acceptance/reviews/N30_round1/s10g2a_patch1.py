# s10g2a_patch1.py <script> <aj>: abs() for signed deltas; locate history key
import sys, json
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
for a, b in (
    ("tk(S2, '1.63', 1.63, df(JP, '2025-11', '2026-02'),", "tk(S2, '1.63', 1.63, abs(df(JP, '2025-11', '2026-02')),"),
    ("round(E(JP, '2026-09') - E(EA, '2026-09'), 2), 'JP − EA @2026-09')", "abs(round(E(JP, '2026-09') - E(EA, '2026-09'), 2)), 'JP − EA @2026-09')"),
    ("round(E(TK, '2026-09') - E(EA, '2026-09'), 2), 'TK − EA @2026-09')", "abs(round(E(TK, '2026-09') - E(EA, '2026-09'), 2)), 'TK − EA @2026-09')"),
):
    assert s.count(a) == 1, a
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s)
aj = json.load(open(sys.argv[2], encoding='utf-8'))
def show(o, pre, depth):
    if isinstance(o, dict) and depth > 0:
        for k, v in o.items():
            t = type(v).__name__
            ln = len(v) if hasattr(v, '__len__') else ''
            print(pre + str(k), t, ln)
            show(v, pre + '  ', depth - 1)
show(aj, '', 2)
for k, v in aj['l4'].items():
    if isinstance(v, list) and v and isinstance(v[0], dict):
        print('l4.' + k, 'item keys', sorted(v[0].keys()))
