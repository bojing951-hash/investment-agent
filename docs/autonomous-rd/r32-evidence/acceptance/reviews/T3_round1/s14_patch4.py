# -*- coding: utf-8 -*-
"""Fourth one-off patcher for the seat's own part scripts (exact-string, first occurrence)."""
import sys
out = sys.argv[1]
P = {
 "s7_p4b.py": [
  ('    ok = [ym for ym in EA if lib.first_next(ym) <= date]\n    return EA[max(ok)]\n',
   '    ok = [ym for ym in EA if lib.first_next(ym) <= date]\n    return max(ok)\n'),
  ('[vis2("2026-06-11"), EA[vis2("2026-06-11")], vis2("2026-09-10"), EA[vis2("2026-09-10")]]',
   '[vis2("2026-06-11"), EA[vis2("2026-06-11")], vis2("2026-09-10"), EA[vis2("2026-09-10")]]'),
  ('      [m1[0], d1[0], len(lib.changes("ECB_MRO", "2025-06-11", "2026-06-17")), len(lib.changes("ECB_DFR", "2025-06-11", "2026-06-17")), lib.days("2025-06-11", "2026-06-17")],',
   '      [lib.at("ECB_MRO", "2025-06-11"), lib.at("ECB_DFR", "2025-06-11"), len(lib.changes("ECB_MRO", "2025-06-11", "2026-06-16")),\n'
   '       len(lib.changes("ECB_DFR", "2025-06-11", "2026-06-16")), lib.days("2025-06-11", "2026-06-17")],'),
  ('"快照 series_store.ECB_MRO/ECB_DFR 首观测(日,值); (2025-06-11,2026-06-17) 内变更点数; 天数差"',
   '"快照 series_store.ECB_MRO/ECB_DFR@2025-06-11(日,值); (2025-06-11,2026-06-17) 开区间内变更点数; 天数差"'),
 ],
 "s7_p6.py": [
  ('    A(K10, "agent_declaration", "证据索引(60行)、点值格(6格)", ', '    A(K10, "agent_declaration", None, '),
 ],
}
for n, reps in P.items():
    p = "%s/%s" % (out, n)
    src = open(p, encoding="utf-8").read()
    for a, b in reps:
        assert src.count(a) >= 1, (n, a[:60])
        src = src.replace(a, b, 1)
    open(p, "w", encoding="utf-8").write(src)
    print("patched", n, len(reps))
