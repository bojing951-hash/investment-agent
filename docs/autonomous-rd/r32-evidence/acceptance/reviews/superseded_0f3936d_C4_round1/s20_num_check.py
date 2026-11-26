#!/usr/bin/python3 -I
# s20_num_check.py — 问题清单所引数字的独立回贴（只读, 直接读 series_store）
import json, sys
snap = json.load(open(sys.argv[1], encoding="utf-8"))
aj = json.load(open(sys.argv[2], encoding="utf-8"))
ss = snap["series_store"]
out = []
def w(s=""): out.append(str(s))
def at(m, d):
    v = ss[m]; i = v["dates"].index(d) if d in v["dates"] else None
    return None if i is None else v["values"][i]
def le(m, d):
    v = ss[m]; best = None
    for a, b in zip(v["dates"], v["values"]):
        if a <= d and isinstance(b, (int, float)): best = (a, b)
    return best
def pct(m, d0, d1):
    a, b = le(m, d0), le(m, d1)
    return a, b, (b[1] / a[1] - 1) * 100
def yoy(m, d):  # d=YYYY-MM-01
    y, mo = int(d[:4]), int(d[5:7])
    base = "%04d-%02d-01" % (y - 1, mo)
    a, b = at(m, base), at(m, d)
    return (a, b, (b / a - 1) * 100 if (a and b) else None)
w("== MINOR 3")
for m, d0, d1 in (("US_REAL_GDP", "2025-04-01", "2026-04-01"), ("US_REAL_GDP", "2025-07-01", "2026-07-01"),
                  ("INDPRO", "2025-07-01", "2026-07-01"), ("INDPRO", "2025-10-01", "2026-10-01")):
    a, b, r = yoy(m, d1)
    w("  %s 同比@%s: 基期%s=%s 当期%s=%s → %.4f%%" % (m, d1, "%04d-%02d-01" % (int(d1[:4]) - 1, int(d1[5:7])), a, d1, b, r))
w("  JP_REAL_GDP_YOY 2026-04=%s 2026-07=%s" % (at("JP_REAL_GDP_YOY", "2026-04-01"), at("JP_REAL_GDP_YOY", "2026-07-01")))
w("  UNEMPLOYMENT 2026-07=%s 2026-10=%s; CN_PMI_MFG 2026-07=%s 2026-10=%s" % (at("UNEMPLOYMENT", "2026-07-01"), at("UNEMPLOYMENT", "2026-10-01"), at("CN_PMI_MFG", "2026-07-01"), at("CN_PMI_MFG", "2026-10-01")))
w("== MINOR 4")
w("  JP_CPI_YOY 2026-07-01=%s 2026-10-01=%s" % (at("JP_CPI_YOY", "2026-07-01"), at("JP_CPI_YOY", "2026-10-01")))
a, b, r = yoy("CPI", "2026-09-01"); w("  CPI 同比 2026-09 = %.2f (基期 %s=%s)" % (r, "%04d-%02d-01" % (2025, 9), a))
a, b, r = yoy("CPI", "2026-07-01"); w("  CPI 同比 2026-07 = %.2f" % r)
a, b, r = yoy("CORE_CPI", "2026-07-01"); w("  CORE_CPI 同比 2026-07 = %.4f" % r)
for d in ("2026-05-01", "2026-08-01", "2026-09-01"):
    a, b, r = yoy("CORE_CPI", d); w("  CORE_CPI 同比 %s = %.4f" % (d, r))
w("  JP_CPI_TOKYO_YOY 2026-06=%s 2026-09=%s 2026-10=%s" % (at("JP_CPI_TOKYO_YOY", "2026-06-01"), at("JP_CPI_TOKYO_YOY", "2026-09-01"), at("JP_CPI_TOKYO_YOY", "2026-10-01")))
w("== MINOR 5")
for m in ("UST_10Y", "TIPS_10Y", "BEI_10Y"):
    a, b = le(m, "2025-11-19"), at(m, "2026-11-19")
    w("  %s 2025-11-19=%s → 2026-11-19=%s = %+.0fbp; 末观测=%s" % (m, a, b, (b - a[1]) * 100, (ss[m]["dates"][-1], ss[m]["values"][-1])))
v = ss["DFEDTARU"]
ch = [(v["dates"][i], v["values"][i - 1], v["values"][i]) for i in range(1, len(v["dates"])) if v["values"][i] != v["values"][i - 1] and v["dates"][i] >= "2025-11-19"]
w("  DFEDTARU 2025-11-19 之后变更点: %s; 末=%s" % (ch, (v["dates"][-1], v["values"][-1])))
w("== MINOR 7")
w("  CN_PPI_YOY 2026-07=%s 2026-10=%s; CN_CPI_YOY 2026-07=%s 2026-10=%s" % (at("CN_PPI_YOY", "2026-07-01"), at("CN_PPI_YOY", "2026-10-01"), at("CN_CPI_YOY", "2026-07-01"), at("CN_CPI_YOY", "2026-10-01")))
w("  series_store 含利润类序列: %s" % [k for k in ss if any(t in k.upper() for t in ("PROFIT", "MARGIN", "利润", "EARN"))])
w("  series_store 含日/中国债: %s" % [k for k in ss if k.upper().startswith(("JGB", "CGB", "JP_", "CN_"))])
w("== MINOR 8")
for m in ("WTI_F", "BRENT_F"):
    a, b, r = pct(m, "2026-08-23", "2026-11-23"); w("  %s %s → %s = %+.2f%%" % (m, a, b, r))
v = ss["WTI_SPOT_M"]; w("  WTI_SPOT_M %s" % [(d, x) for d, x in zip(v["dates"], v["values"]) if d >= "2026-06-01"])
w("  能源类序列键: %s" % [k for k in ss if any(t in k.upper() for t in ("WTI", "BRENT", "OIL", "GAS", "ENERGY", "NATGAS"))])
w("== MINOR 9 / NIT 3")
w("  JP_POLICY_RATE 2025-11..2026-04: %s" % [(d, x) for d, x in zip(ss["JP_POLICY_RATE"]["dates"], ss["JP_POLICY_RATE"]["values"]) if "2025-11-01" <= d <= "2026-10-01"])
txt = json.dumps(aj, ensure_ascii=False)
for n in ("24408.011", "24611.077", "0.8", "1.16", "1.97", "2.44", "事后回顾", "最新修订值", "尚不能区分"):
    w("  判断档含 %r 次数=%d" % (n, txt.count(n)))
open(sys.argv[3], "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out))
