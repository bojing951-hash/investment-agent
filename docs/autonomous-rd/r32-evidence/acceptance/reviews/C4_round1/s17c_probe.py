#!/usr/bin/python3 -I
# s17c: 定稿前核对——report.json 引擎面 us_rates_trio / asset_moves 与受审稿对应块的一致性, 以及 MAP_REPORT 利率窗行。
# 用法: /usr/bin/python3 -I s17c_probe.py REP AJ MAPMD OUT
import sys, json
rep_p, aj_p, map_p, outp = sys.argv[1:5]
rep = json.load(open(rep_p, encoding="utf-8"))
aj = json.load(open(aj_p, encoding="utf-8"))
L = []


def find(o, key, path="$"):
    hits = []
    if isinstance(o, dict):
        for k, v in o.items():
            if k == key:
                hits.append((path + "." + k, v))
            hits += find(v, key, path + "." + k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            hits += find(v, key, "%s[%d]" % (path, i))
    return hits


for key in ("us_rates_trio", "asset_moves"):
    hs = find(rep, key)
    L.append("== report.json 键 %s: %d 处 ==" % (key, len(hs)))
    for p, v in hs[:3]:
        s = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
        L.append("  @ %s (类型 %s, %d 字符)" % (p, type(v).__name__, len(s)))
        L.append("  " + s[:2600])
md = open(map_p, encoding="utf-8").read().split("\n")
L.append("== MAP_REPORT 含『近30日』或『近一月』且含 TIPS/BEI/盈亏平衡/名义 的行 ==")
for i, line in enumerate(md, 1):
    if any(w in line for w in ("TIPS", "BEI", "盈亏平衡", "名义")) and ("近30日" in line or "近一月" in line):
        L.append("  L%d: %s" % (i, line.strip()[:300]))
L.append("== MAP_REPORT 含 USDJPY / USDCNY 的行 ==")
for i, line in enumerate(md, 1):
    if "USDJPY" in line or "USDCNY" in line:
        L.append("  L%d: %s" % (i, line.strip()[:300]))
open(outp, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("OK lines %d -> %s" % (len(L), outp))
