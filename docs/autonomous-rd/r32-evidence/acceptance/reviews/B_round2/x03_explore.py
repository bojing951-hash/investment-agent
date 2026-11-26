# -*- coding: utf-8 -*-
"""只读探查(3): 冻结日历全文 / 注册表相关条目 / 快照 facts 相关行 / 证据索引 / S3 等信封摘要。"""
import json, sys, os

RUN = sys.argv[1]; SNAP = sys.argv[2]; OUT = sys.argv[3]
rep = json.load(open(os.path.join(RUN, "report.json"), encoding="utf-8"))
sn = json.load(open(SNAP, encoding="utf-8"))
cal = json.load(open(os.path.join(RUN, "root_overlay/config/release_calendar.json"), encoding="utf-8"))
reg = json.load(open(os.path.join(RUN, "root_overlay/config/metric_registry.json"), encoding="utf-8"))
evi = json.load(open(os.path.join(RUN, "evidence_index.json"), encoding="utf-8"))

out = open(OUT, "w", encoding="utf-8")
def P(*a):
    out.write(" ".join(str(x) for x in a) + "\n")
def J(v):
    return json.dumps(v, ensure_ascii=False, indent=1)

P("=== release_calendar.spec ==="); P(cal["spec"])
P("=== release_calendar.batches ==="); P(J(cal["batches"]))
P("=== release_calendar.entries (all) ===")
for i, e in enumerate(cal["entries"]):
    P("--- entry", i); P(J(e))

P("\n=== registry.field_semantics ==="); P(J(reg["field_semantics"]))
P("=== registry: relevant metrics ===")
want = ["US_REAL_GDP","UNEMPLOYMENT","INDPRO","CPI","CORE_CPI","CORE_PCE","EA_REAL_GDP_YOY","EA_HICP_YOY","JP_POLICY_RATE","JP_POLICY_TARGET","JP_CPI_YOY","JP_REAL_GDP_YOY","DFEDTARU","DFEDTARL","ECB_DFR","ECB_MRO","UST_2Y","UST_10Y","TIPS_10Y","BEI_10Y","CURVE_2S10S","BRENT_F","EURUSD","USDJPY","NIKKEI225","SPX","VIX","GOLD_F","DXY","DAX"]
ids = [m.get("metric_id") for m in reg["metrics"]]
P("registry metric ids (%d):" % len(ids), ids)
P("JP_POLICY_TARGET in registry:", "JP_POLICY_TARGET" in ids)
P("any registry id containing 'JGB' or 'JP':", [i for i in ids if i and ("JGB" in i or i.startswith("JP"))])
for m in reg["metrics"]:
    if m.get("metric_id") in want:
        P("---", J(m))
P("=== registry.notes ===")
for n in reg["notes"]:
    P("-", n)

P("\n=== snapshot.facts: obs 2026-11-2x and all JGB/JP rows and quality != PASS ===")
for f in sn["facts"]:
    od = f.get("observation_date", "")
    if od >= "2026-11-13" or f.get("metric_id","").startswith("JP") or "JGB" in json.dumps(f, ensure_ascii=False):
        P(J(f))
P("=== facts: metric ids set (%d) ===" % len(sn["facts"]))
P(sorted(set(f.get("metric_id") for f in sn["facts"])))
P("=== facts quality values ===")
from collections import Counter
P(Counter((f.get("quality_status") or f.get("quality") or "?") for f in sn["facts"]))
P("=== reconciliation ==="); P(J(sn["reconciliation"]))
P("=== sources_status ==="); P(J(sn["sources_status"])[:4000])
P("=== notes ==="); P(J(sn["notes"]))
P("=== series_store_notes ==="); P(J(sn["series_store_notes"]))
P("=== series_store_clean (JP_POLICY_RATE, CPI, EA_HICP_YOY sample) ===")
ssc = sn.get("series_store_clean", {})
for k in ("CPI", "CORE_PCE", "US_REAL_GDP", "INDPRO"):
    if k in ssc:
        P(k, J(ssc[k])[:1500])

P("\n=== evidence_index.json ===")
P(type(evi).__name__, len(evi) if hasattr(evi, "__len__") else "")
P(J(evi) if not isinstance(evi, list) else J(evi[:3]))
if isinstance(evi, list):
    P("refs:", [x.get("ref") if isinstance(x, dict) else x for x in evi])

P("\n=== steps envelopes: S2_doctor / S5_compare / S6_analog / S8_grounded_qa (trimmed) ===")
for st in rep["steps"]:
    if st["step"] in ("S2_doctor", "S5_compare", "S6_analog", "S8_grounded_qa", "S3_overview_JP", "S3_overview_EA", "S3_overview_US", "S3_changes", "S9_views_lint"):
        env = st.get("envelope") or {}
        P("--- ", st["step"], "keys:", sorted(env.keys()))
        data = env.get("data")
        P(J(data)[:3500] if data is not None else "data=None")

P("\n=== layers keys / L3 / L4 ===")
for k, v in rep["layers"].items():
    P(k, sorted(v.keys()) if isinstance(v, dict) else type(v).__name__)
P(J(rep["layers"]["L3_AI推断层"])[:2500])
P(J(rep["layers"]["L4_条件情景层"])[:1500])
P("=== fanout / other top ==="); P(J(rep.get("fanout"))[:500])
out.close()
print("written", OUT)
