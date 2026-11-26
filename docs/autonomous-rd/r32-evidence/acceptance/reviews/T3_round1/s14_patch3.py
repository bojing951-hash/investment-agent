# -*- coding: utf-8 -*-
"""Third one-off patcher (p4b only): first-occurrence replacement for the vis() helper plus two claim fixes."""
import sys
out = sys.argv[1]
p = "%s/s7_p4b.py" % out
src = open(p, encoding="utf-8").read()
reps = [
 ('    return EA[max(ok)]\n', '    return max(ok)\n', 1),
 ('      [c.cal.get("version"), c.cal.get("updated"), 1.25], ["v1.5.0", "2026-11-21", 1.25])',
  '      [str(c.cal.get("version")).lstrip("v"), c.cal.get("updated"), 1.25], ["1.5.0", "2026-11-21", 1.25],\n'
  '      "日历 version 字段=%r(无 v 前缀),受审稿写作 v1.5.0=书写差异" % c.cal.get("version"))', 1),
 ('      [JPR["2025-11"], JPR["2026-10"], round((JPR["2026-10"] - JPR["2025-11"]) * 100, 2)], [0.478, 1.227, 75.0])',
  '      [JPR["2025-11"], JPR["2026-10"], round((JPR["2026-10"] - JPR["2025-11"]) * 100)], [0.478, 1.227, 75],\n'
  '      "未取整=74.9bp,受审稿『约 +75bp』(取整 bp)")', 1),
]
for a, b, cnt in reps:
    assert src.count(a) >= 1, a[:50]
    src = src.replace(a, b, cnt)
open(p, "w", encoding="utf-8").write(src)
print("patched p4b", len(reps))
