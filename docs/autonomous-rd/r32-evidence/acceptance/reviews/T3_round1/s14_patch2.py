# -*- coding: utf-8 -*-
"""Second one-off patcher for the seat's own part scripts (exact-string replacements, each must hit once)."""
import sys
out = sys.argv[1]
P = {
 "s7_p4a.py": [
  ('    nch = lib.changes("JP_POLICY_RATE", "2025-11-01", cut)\n',
   '    nch = [x for x in lib.changes("JP_POLICY_RATE", "2025-11-01", cut) if round((x[2] - x[1]) * 100) != 0]\n'
   '    c.F["jpr_strict_n"] = len(lib.changes("JP_POLICY_RATE", "2025-11-01", cut))\n'),
  ('"近 12 个月 JP_POLICY_RATE 月均变动点数 vs 日历中改变目标的 JP 条目数"',
   '"近 12 个月 JP_POLICY_RATE 月均变动点数(整数 bp 非零;严格不等比较另含两次 -0.1bp 舍入伪变动) vs 日历中改变目标的 JP 条目数"'),
 ],
 "s7_p4b.py": [
  ('    return EA[max(ok)]\n', '    return max(ok)\n'),
  ('      [c.cal.get("version"), c.cal.get("updated"), 1.25], ["v1.5.0", "2026-11-21", 1.25])',
   '      [str(c.cal.get("version")).lstrip("v"), c.cal.get("updated"), 1.25], ["1.5.0", "2026-11-21", 1.25],\n'
   '      "日历 version 字段=%r(无 v 前缀),受审稿写作 v1.5.0=书写差异" % c.cal.get("version"))'),
  ('      [JPR["2025-11"], JPR["2026-10"], round((JPR["2026-10"] - JPR["2025-11"]) * 100, 2)], [0.478, 1.227, 75.0])',
   '      [JPR["2025-11"], JPR["2026-10"], round((JPR["2026-10"] - JPR["2025-11"]) * 100)], [0.478, 1.227, 75],\n'
   '      "未取整=74.9bp,受审稿『约 +75bp』(取整 bp)")'),
 ],
}
for n, reps in P.items():
    p = "%s/%s" % (out, n)
    src = open(p, encoding="utf-8").read()
    for a, b in reps:
        assert src.count(a) == 1, (n, a[:50], src.count(a))
        src = src.replace(a, b)
    open(p, "w", encoding="utf-8").write(src)
    print("patched", n, len(reps))
