import sys
path = sys.argv[1]
src = open(path, encoding="utf-8").read()
PAIRS = []
A = PAIRS.append
A((r'''    info("cell_vintages", {c_["metric_id"]: [c_["anchors"]["6个月前"]["vintage"], c_["anchors"]["最新一期"]["vintage"]] for c_ in (CE, CJ, CT, CP, CM, CD)}, "research_plan.point_values.cells[].anchors")''',
   r'''    info("cell_vintages", dict(zip(("EA_HICP_YOY", "JP_CPI_YOY", "JP_CPI_TOKYO_YOY", "JP_POLICY_RATE", "ECB_MRO", "ECB_DFR"), [[c_["6个月前"]["vintage"], c_["最新一期"]["vintage"]] for c_ in (CE, CJ, CT, CP, CM, CD)])), "research_plan.point_values.cells[].anchors")'''))
A((r'''def changes(mid, d0, d1):
    out = []
    sv = ser(mid)
''', r'''def changes(mid, d0, d1):
    out = []
    sv = ser(mid)
    d0, d1 = D(d0), D(d1)
'''))
bad = 0
for old, new in PAIRS:
    c = src.count(old)
    if c != 1:
        bad += 1
        print("BAD count", c, "for:", old[:100])
        continue
    src = src.replace(old, new)
if bad:
    sys.exit(1)
open(path, "w", encoding="utf-8").write(src)
print("patched", len(PAIRS))
