import sys
path = sys.argv[1]
src = open(path, encoding="utf-8").read()
PAIRS = []
A = PAIRS.append

A((r'''    occ = re.findall(r"决议日 2026-\d\d-\d\d[^。;]{0,80}", T)''',
   r'''    occ = re.findall(r"决议日 (?:2026-06-11|2026-09-10)[^。;]{0,80}", T)'''))
A((r'''    add(s, "锚格 vintage: EA=事后回顾(最新修订值) / 其余=as_collected", ["事后回顾(最新修订值,非当时首发值)", "as_collected(采集时点值)"], [CE["最新一期"]["vintage"], CJ["最新一期"]["vintage"]], "research_plan.point_values.cells[].anchors.最新一期.vintage")''',
   r'''    VT = "事后回顾(最新修订值,非当时首发值)"
    CT_ = "as_collected(采集时点值)"
    add(s, "锚格 vintage: EA 与日本全国 CPI=事后回顾(最新修订值);东京 CPI 与月均拆借利率=采集时点值", [VT, VT, CT_, CT_], [CE["最新一期"]["vintage"], CJ["最新一期"]["vintage"], CT["最新一期"]["vintage"], CP["最新一期"]["vintage"]], "research_plan.point_values.cells[].anchors.最新一期.vintage")
    add(s, "C3④ vintage 披露在文且与锚格一致(全国/全区 CPI=事后回顾;东京 CPI 与月均拆借利率=采集时点值)", [True, True],
        [has("欧元区 HICP 与日本全国 CPI 月度数值为事后回顾口径(最新修订值,非当时首发值)"), has("东京 CPI 与月均拆借利率为采集时点值")], "l3.contradictions[2].statement ④")
    info("cell_vintages", {c_["metric_id"]: [c_["anchors"]["6个月前"]["vintage"], c_["anchors"]["最新一期"]["vintage"]] for c_ in (CE, CJ, CT, CP, CM, CD)}, "research_plan.point_values.cells[].anchors")'''))
A((r'''[], [x for x in fed + fedl] + [x for x in changes("ECB_MRO", D("2026-10-23"), CUTOFF)] + [x for x in changes("JP_POLICY_RATE", D("2026-10-23"), CUTOFF)], "series_store 变更点")''',
   r'''[], [x for x in changes("DFEDTARU", D("2026-10-23"), CUTOFF) + changes("DFEDTARL", D("2026-10-23"), CUTOFF)] + [x for x in changes("ECB_MRO", D("2026-10-23"), CUTOFF)] + [x for x in changes("JP_POLICY_RATE", D("2026-10-23"), CUTOFF)], "series_store 变更点(窗 2026-10-23..2026-11-23)")
    add(s, "判断档未作「ECB 观测日全为周三」类全称主张(该句仅见于引擎读者面注记)", True, not has("观测日全为周三"), "agent_judgment 全文 vs MAP_REPORT.md 注记")
    recent_nonwed = [d_ for d_ in ecbs if D(d_) >= D("2015-01-01") and D(d_).weekday() != 2]
    info("ECB_obs_dates_not_Wednesday_since_2015", recent_nonwed, "series_store.ECB_MRO/ECB_DFR 观测日(2015 起)")
    add(s, "引擎注记「ECB 观测日全为周三」对 2015 年以来观测日成立(历史 1999-2008 有 21 个例外,INFO)", True, not recent_nonwed, "series_store.ECB_MRO/ECB_DFR 观测日")'''))
A((r'''距上次调整\(按生效日\) (\d+)天 \| 距决议 (\d+)天 \| 距维持 (\d+)天")''', r'''距上次调整\(按生效日\) (\d+)天 \| 距决议 (\d+)天 \| 距维持 (\d+)天")'''))
A((r'''    add(s, "M1-step3 %s 至 11-23 变动%" % mid, fx[10 + 2 * k], F(abs(pct(a, c)), 2), "11-23/10-23 − 1")''',
   r'''    add(s, "M1-step3 %s 至 11-23 变动%%" % mid, fx[10 + 2 * k], F(abs(pct(a, c)), 2), "11-23/10-23 − 1")'''))
bad = 0
for old, new in PAIRS:
    c = src.count(old)
    if c != 1:
        bad += 1
        print("BAD count", c, "for:", old[:100].replace("\n", " | "))
        continue
    src = src.replace(old, new)
if bad:
    print("NOT WRITTEN", bad)
    sys.exit(1)
open(path, "w", encoding="utf-8").write(src)
print("patched", len(PAIRS))
