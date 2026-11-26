import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
old = '''sup("点值格推定发布日落周末者 %d 个;研究计划内 2025-06 以来落周末的日期记号 %d 个(%s);判断档正文日期记号落周末者 %d 个(日历版本日 %s 除外)" % (
    len(WK), len(RP_WK), ",".join(RP_WK), len(CITED_WK), CALE.get("updated")), len(WK) >= 1 and not CITED_WK, (WK, RP_WK, CITED_WK))
'''
new = '''WKD = {d: ("周六" if D(d).weekday() == 5 else "周日") for d in CITED_WK}
sup("判断档正文落周末的日期记号 %d 个(日历版本日 %s 除外): 窗起日 2026-05-23(%s,六个月窗起点)、欧元区 2026-04 期推定发布日 2026-05-16(%s,句中未点明)、东京都 2026-08 期推定发布日 2026-08-30(%s,句中已点明);"
    "研究计划点值格推定发布日落周末者 %d 个(%s);研究计划 2025-06 以来落周末的日期记号 %d 个(%s)" % (
    len(CITED_WK), CALE.get("updated"), WKD.get("2026-05-23"), WKD.get("2026-05-16"), WKD.get("2026-08-30"), len(WK), ";".join(WK), len(RP_WK), ",".join(RP_WK)),
    CITED_WK == ["2026-05-16", "2026-05-23", "2026-08-30"] and WK == ["EA_HICP_YOY/6个月前@2026-05-16"] and "2026-05-16" in PLAN_PUB
    and all(D(d).weekday() >= 5 for d in CITED_WK + RP_WK) and "该推定日落在周日" in JALL and "2026-05-23" in RPTXT, (WK, RP_WK, CITED_WK))
'''
assert s.count(old) == 1
s = s.replace(old, new)
open(p, "w", encoding="utf-8").write(s)
print("part D patched")
