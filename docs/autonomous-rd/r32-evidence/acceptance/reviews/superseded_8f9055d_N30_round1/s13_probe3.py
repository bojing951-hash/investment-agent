import json, sys
jp, rp, sp, cp, mp = sys.argv[1:6]
J = json.load(open(jp, encoding="utf-8")); R = json.load(open(rp, encoding="utf-8"))
SN = json.load(open(sp, encoding="utf-8")); CA = json.load(open(cp, encoding="utf-8"))
MAPL = open(mp, encoding="utf-8").read().split("\n")
def d(o, n=3000):
    return json.dumps(o, ensure_ascii=False)[:n]
P = print
P("CALE_TOP", d({k: (v if not isinstance(v, (list, dict)) else type(v).__name__) for k, v in CA.items()}))
for e in CA["entries"]:
    if "JP" in str(e.get("entry_id")) or "EA" in str(e.get("entry_id")): P("CE", d(e, 1500))
P("PDF", d(R["research_plan"]["policy_doc_facts"], 1500))
P("AM0", d(R["research_plan"]["asset_moves"]["rows"][0], 1500))
P("ECHO", d(J["reader_map"]["asset_returns_echo"], 2500))
P("URT", d(R["research_plan"]["us_rates_trio"], 1500))
P("RD", d(J["reader_map"]["rates_decomposition"]))
P("CELL_ECB", d([c for c in R["research_plan"]["point_values"]["cells"] if c["metric_id"] == "ECB_MRO"][0], 4000))
F = [f for f in SN["facts"] if f["fact_id"] == "ECB_MRO@2026-09-16"][0]
P("FACT_ISSUES", d(F["issues"], 1500)); P("FACT_KEYS", list(F.keys()))
P("GA", d({k: SN["gate_a"][k] for k in SN["gate_a"] if k != "noncore_missing_detail"}, 2500))
P("GA_DET", d(SN["gate_a"]["noncore_missing_detail"], 2500))
P("SCE", d(J["l4"]["scenarios"], 6000))
P("QGN", d(J["quality_gate_notes"], 6000))
P("AD", d(J["agent_declaration"]))
P("HEAD", d(J["reader_map"]["headline_conclusion"]))
P("TR_KEYS", [list(x.keys()) for x in J["reader_map"]["transmission"][0]["links"]], list(J["reader_map"]["transmission"][0].keys()))
P("RM_KEYS", {k: type(v).__name__ for k, v in J["reader_map"].items()})
P("S5", d([s for s in R["steps"] if s.get("step") == "S5_compare"][0]["envelope"]["data"], 1500))
P("S6", d([s for s in R["steps"] if s.get("step") == "S6_analog"][0]["envelope"]["data"], 1500))
P("HZ", d(J["reader_map"]["history_zero_case_note"]))
P("DRI", d({k: {kk: vv for kk, vv in v.items() if kk != "spec"} for k, v in ((it.get("metric_id"), it) for it in R["run"]["data_requirements"]["items"])}, 3000))
P("DRSPEC", d([it.get("spec") for it in R["run"]["data_requirements"]["items"]][:2], 1500))
P("RUNKEYS", list(R["run"].keys()), d(R["run"].get("evidence_gate"), 1500))
