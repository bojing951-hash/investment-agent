#!/usr/bin/python3 -I
# s01: 把引擎面各键落盘为本席目录内的文本中间表(只读受审文件)
import json, sys, os

rep_p, snap_p, cal_p, reg_p, outdir = sys.argv[1:6]
rep = json.load(open(rep_p, encoding="utf-8"))
snap = json.load(open(snap_p, encoding="utf-8"))
cal = json.load(open(cal_p, encoding="utf-8"))
reg = json.load(open(reg_p, encoding="utf-8"))
rp = rep["research_plan"]

def w(name, text):
    with open(os.path.join(outdir, name), "w", encoding="utf-8") as f:
        f.write(text)

# 1) point_values cells
lines = []
pv = rp["point_values"]
lines.append("point_values top keys: %s" % list(pv.keys()))
for k in pv:
    if k != "cells":
        lines.append("  %s: %s" % (k, json.dumps(pv[k], ensure_ascii=False)[:1500]))
for c in pv["cells"]:
    lines.append("---- cell " + json.dumps({k: c[k] for k in c if k != "anchors"}, ensure_ascii=False))
    for an, av in c["anchors"].items():
        lines.append("     anchor[%s]: %s" % (an, json.dumps(av, ensure_ascii=False)))
w("mid_point_values.txt", "\n".join(lines))

# 2) turning candidates
w("mid_turning_candidates.txt", json.dumps(rp["turning_candidates"], ensure_ascii=False, indent=1))

# 3) rates trio
w("mid_us_rates_trio.txt", json.dumps(rp["us_rates_trio"], ensure_ascii=False, indent=1))

# 4) asset moves
w("mid_asset_moves.txt", json.dumps(rp["asset_moves"], ensure_ascii=False, indent=1))

# 5) policy clusters / doc facts / dimension gaps
w("mid_policy_clusters.txt", json.dumps(rp["policy_event_clusters"], ensure_ascii=False, indent=1))
w("mid_policy_doc_facts.txt", json.dumps(rp["policy_doc_facts"], ensure_ascii=False, indent=1))
w("mid_dimension_gaps.txt", json.dumps(rp["dimension_gaps"], ensure_ascii=False, indent=1))

# 6) regions (planned metrics)
w("mid_regions.txt", json.dumps(rp["regions"], ensure_ascii=False, indent=1))
w("mid_as_of_declared.txt", json.dumps(rp["as_of_declared"], ensure_ascii=False, indent=1))
w("mid_evidence_gate.txt", json.dumps(rep["run"]["evidence_gate"], ensure_ascii=False, indent=1))

# 7) contract verification
cv = rep["agent_judgment"]["contract_verification"]
w("mid_contract_verification.txt", json.dumps(cv, ensure_ascii=False, indent=1))
aj = {k: v for k, v in rep["agent_judgment"].items() if k != "contract_verification"}
w("mid_agent_judgment_meta.txt", json.dumps(aj, ensure_ascii=False, indent=1))
w("mid_semantic_review.txt", json.dumps(rep["semantic_review"], ensure_ascii=False, indent=1))

# 8) calendar
w("mid_calendar.txt", json.dumps(cal, ensure_ascii=False, indent=1))

# 9) snapshot gate_a / quality / sources_status / notes
w("mid_gate_a.txt", json.dumps({"gate_a": snap["gate_a"], "quality": snap["quality"],
                                "sources_status": snap["sources_status"], "notes": snap["notes"]},
                               ensure_ascii=False, indent=1))

# 10) registry metrics relevant
want = set("""US_REAL_GDP UNEMPLOYMENT INDPRO CPI CORE_CPI CORE_PCE DFEDTARU DFEDTARL DFF EA_REAL_GDP_YOY EA_HICP_YOY ECB_MRO ECB_DFR BUND_10Y BUND_2Y
CN_PMI_MFG CN_CPI_YOY CN_PPI_YOY CN_POLICY_OVERNIGHT CN_OMO_7D CN_LPR_1Y JP_REAL_GDP_YOY JP_CPI_YOY JP_CPI_TOKYO_YOY JP_POLICY_RATE JP_POLICY_TARGET
UST_10Y TIPS_10Y BEI_10Y SPX NIKKEI225 SHCOMP DAX CAC40 VIX DXY USDJPY USDCNY WTI_F BRENT_F WTI_SPOT_M GOLD_F JP_POLICY_TARGET""".split())
lines = []
ids = []
for m in reg["metrics"]:
    ids.append(m.get("metric_id"))
    if m.get("metric_id") in want:
        lines.append(json.dumps(m, ensure_ascii=False, sort_keys=True))
w("mid_registry_relevant.txt", "ALL IDS(%d): %s\n\n" % (len(ids), ", ".join(str(i) for i in ids)) + "\n".join(lines))
w("mid_registry_field_semantics.txt", json.dumps({"field_semantics": reg.get("field_semantics"), "notes": reg.get("notes")}, ensure_ascii=False, indent=1))

# 11) step envelopes: dump selected
lines = []
for st in rep["steps"]:
    s = st.get("step")
    lines.append("==== %s | ok=%s exit=%s semantic_ok=%s note=%s" % (s, st.get("ok"), st.get("exit_code"), st.get("semantic_ok"), str(st.get("note"))[:300]))
    if s in ("S1_decompose", "S7_mode_gate", "S10_selfcheck", "S11_archive"):
        lines.append(json.dumps({k: v for k, v in st.items() if k not in ("envelope",)}, ensure_ascii=False, indent=1)[:4000])
        continue
    env = st.get("envelope")
    if not isinstance(env, dict):
        lines.append("  (no envelope) " + json.dumps({k: v for k, v in st.items() if k != "argv"}, ensure_ascii=False)[:800])
        continue
    lines.append("  argv: %s" % json.dumps(st.get("argv"), ensure_ascii=False)[:500])
    for k in env:
        if k in ("data", "gate_a"):
            continue
        lines.append("  env.%s: %s" % (k, json.dumps(env[k], ensure_ascii=False)[:1200]))
    ga = env.get("gate_a")
    if ga is not None and s == "S2_doctor":
        lines.append("  env.gate_a: " + json.dumps(ga, ensure_ascii=False, indent=1))
    d = env.get("data")
    if isinstance(d, dict):
        lines.append("  env.data keys: %s" % list(d.keys()))
        for dk, dv in d.items():
            s2 = json.dumps(dv, ensure_ascii=False)
            # skip huge series
            if len(s2) > 6000:
                lines.append("    data.%s: (len %d) %s ... %s" % (dk, len(s2), s2[:3500], s2[-1500:]))
            else:
                lines.append("    data.%s: %s" % (dk, s2))
    else:
        lines.append("  env.data: " + json.dumps(d, ensure_ascii=False)[:3000])
w("mid_steps_envelopes.txt", "\n".join(lines))

# 12) L1 rows
w("mid_L1_rows.txt", json.dumps(rep["layers"]["L1_事实层"], ensure_ascii=False, indent=1)[:60000])
w("mid_notes.txt", json.dumps(rep.get("notes"), ensure_ascii=False, indent=1))

# 13) data_requirements summary
dr = rep["run"]["data_requirements"]
lines = ["data_requirements keys: %s" % list(dr.keys())]
for k in dr:
    if k != "items":
        lines.append("  %s: %s" % (k, json.dumps(dr[k], ensure_ascii=False)[:800]))
for it in dr["items"]:
    lines.append(json.dumps({k: it[k] for k in it if k != "gap_detail"}, ensure_ascii=False)[:700])
w("mid_data_requirements.txt", "\n".join(lines))

print("done; files:")
for fn in sorted(os.listdir(outdir)):
    print("  ", fn, os.path.getsize(os.path.join(outdir, fn)))
