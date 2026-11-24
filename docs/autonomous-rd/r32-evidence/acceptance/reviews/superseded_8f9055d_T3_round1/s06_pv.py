#!/usr/bin/python3 -I
"""Compact dump of engine point_values cells / policy window paths / clusters / trio.
Args: <report.json> [pv|path|cluster|trio|turn|gate|cv|l1|analog|steps]
"""
import json
import sys


def main():
    d = json.load(open(sys.argv[1], "r", encoding="utf-8"))
    what = sys.argv[2:] or ["pv"]
    rp = d["research_plan"]
    if "pv" in what:
        for c in rp["point_values"]["cells"]:
            print(f"== {c['region']}/{c['dimension']}/{c['metric_id']} unit={c.get('unit')}")
            for lab, a in c["anchors"].items():
                keep = {k: v for k, v in a.items() if k not in ("publication_basis", "vintage")}
                print(f"  [{lab}] {json.dumps(keep, ensure_ascii=False)}")
            for k in ("derived_yoy_pct", "yoy_status", "latest_valid_yoy"):
                if k in c:
                    print(f"  {k}={json.dumps(c[k], ensure_ascii=False)}")
    if "path" in what:
        for c in rp["point_values"]["cells"]:
            p = c.get("policy_window_path")
            if p:
                slim = {k: v for k, v in p.items() if k != "note"}
                print(f"PATH {c['metric_id']}: {json.dumps(slim, ensure_ascii=False)}")
    if "cluster" in what:
        print(json.dumps(rp["policy_event_clusters"], ensure_ascii=False)[:6000])
    if "trio" in what:
        print(json.dumps(rp["us_rates_trio"], ensure_ascii=False)[:4000])
    if "turn" in what:
        print(json.dumps(rp["turning_candidates"], ensure_ascii=False)[:12000])
    if "gate" in what:
        print(json.dumps(d["run"]["evidence_gate"], ensure_ascii=False)[:6000])
    if "cv" in what:
        print(json.dumps(d["agent_judgment"]["contract_verification"], ensure_ascii=False)[:12000])
    if "l1" in what:
        for row in d["layers"]["L1_事实层"]["rows"]:
            print(json.dumps(row, ensure_ascii=False)[:600])
    if "analog" in what:
        for st in d["steps"]:
            env = st.get("envelope") or {}
            if "analog" in json.dumps(env)[:400].lower() or "analog" in str(st.get("step")).lower():
                s = json.dumps(st, ensure_ascii=False)
                print(st.get("step"), len(s), s[:3000])
    if "steps" in what:
        for st in d["steps"]:
            env = st.get("envelope")
            print(st.get("step"), "ok=", st.get("ok"), "exec=", st.get("executed"),
                  "env_keys=", (list(env.keys()) if isinstance(env, dict) else type(env).__name__))


if __name__ == "__main__":
    main()
