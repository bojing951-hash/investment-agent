#!/usr/bin/env python3
"""Print the exact key shapes of the engine faces I must address in s7 (read-only).
usage: python3 -I s8_shapes.py <run_dir>
"""
import json
import os
import sys


def abbrev(obj, max_items=3, max_str=160, depth=0):
    if isinstance(obj, dict):
        if depth > 6:
            return "{...%d keys}" % len(obj)
        return {k: abbrev(v, max_items, max_str, depth + 1) for k, v in obj.items()}
    if isinstance(obj, list):
        if len(obj) > max_items:
            return [abbrev(x, max_items, max_str, depth + 1) for x in obj[:max_items]] + ["...(%d items)" % len(obj)]
        return [abbrev(x, max_items, max_str, depth + 1) for x in obj]
    if isinstance(obj, str) and len(obj) > max_str:
        return obj[:max_str] + "...(+%d)" % (len(obj) - max_str)
    return obj


def main():
    run = sys.argv[1]

    def load(p):
        with open(p, "r", encoding="utf-8") as fh:
            return json.load(fh)

    rep = load(os.path.join(run, "report.json"))
    aj = load(os.path.join(run, "agent_judgment.json"))
    snap = load(os.path.join(run, "root_overlay", "data", "daily", "research_snapshot_20261123.json"))
    plan = rep["research_plan"]
    print("== plan keys:", sorted(plan.keys()))
    for k in ("point_anchors", "question_window", "us_rates_trio", "asset_moves", "policy_doc_facts", "dimension_gaps"):
        print("== plan.%s" % k, json.dumps(abbrev(plan.get(k)), ensure_ascii=False))
    print("== point_values keys:", sorted(plan["point_values"].keys()))
    print("== point_values.cells[0]", json.dumps(abbrev(plan["point_values"]["cells"][0]), ensure_ascii=False))
    tc = plan["turning_candidates"]
    print("== turning_candidates keys:", sorted(tc.keys()) if isinstance(tc, dict) else type(tc))
    print("== turning_candidates.candidates[0]", json.dumps(abbrev(tc["candidates"][0] if isinstance(tc, dict) and "candidates" in tc else tc), ensure_ascii=False))
    print("== policy_window_path", json.dumps(abbrev(plan.get("policy_window_path")), ensure_ascii=False))
    for st in rep["steps"]:
        if st.get("step") == "S6_analog":
            print("== S6_analog envelope keys:", sorted(st["envelope"].keys()))
            print("== S6_analog envelope.data keys:", sorted(st["envelope"]["data"].keys()) if isinstance(st["envelope"].get("data"), dict) else type(st["envelope"].get("data")))
            print(json.dumps(abbrev(st["envelope"], max_items=2), ensure_ascii=False)[:3000])
    cv = rep["agent_judgment"].get("contract_verification")
    print("== contract_verification", json.dumps(abbrev(cv, max_items=6, max_str=120), ensure_ascii=False)[:4000])
    print("== report.agent_judgment keys:", sorted(rep["agent_judgment"].keys()))
    ei = rep["evidence_index"]
    print("== evidence_index[0..2]", json.dumps(ei[:3], ensure_ascii=False))
    print("== evidence_index kinds:", sorted({x.get("kind") for x in ei}))
    print("== report keys:", sorted(rep.keys()))
    if "layers" in rep:
        print("== layers keys:", sorted(rep["layers"].keys()) if isinstance(rep["layers"], dict) else type(rep["layers"]))
    ga = snap["gate_a"]
    print("== gate_a keys:", sorted(ga.keys()))
    for k in ga:
        if "detail" in k:
            print("== gate_a.%s" % k, json.dumps(abbrev(ga[k]), ensure_ascii=False)[:1500])
    rm = aj["reader_map"]
    print("== reader_map keys:", sorted(rm.keys()))
    for k in rm:
        print("== reader_map.%s" % k, json.dumps(abbrev(rm[k], max_items=2), ensure_ascii=False)[:2500])
    l3 = aj["l3"]
    print("== l3 keys:", sorted(l3.keys()))
    print("== contradictions[0] keys:", sorted(l3["contradictions"][0].keys()))
    print("== mechanism_chains[0] keys:", sorted(l3["mechanism_chains"][0].keys()))
    print("== mechanism_chains[0].links[0] keys:", sorted(l3["mechanism_chains"][0]["links"][0].keys()))
    print("== fact ids:", [f["fact_id"] for f in snap["facts"]][:40])
    print("== fact[0] keys:", sorted(snap["facts"][0].keys()))
    print("== judgment keys:", sorted(aj.keys()))


if __name__ == "__main__":
    main()
