#!/usr/bin/python3 -I
"""Read-only probe of registry entries needed for part C.
Args: <metric_registry.json> <snapshot.json> <report.json> <agent_judgment.json> <tree_dir>
"""
import json
import re
import sys


def main():
    reg = json.load(open(sys.argv[1], "r", encoding="utf-8"))
    snap = json.load(open(sys.argv[2], "r", encoding="utf-8"))
    rep = json.load(open(sys.argv[3], "r", encoding="utf-8"))
    aj = json.load(open(sys.argv[4], "r", encoding="utf-8"))
    ms = reg["metrics"]
    print("metric keys sample:", sorted(ms[0].keys()))
    idk = "metric_id" if "metric_id" in ms[0] else "id"
    byid = {m[idk]: m for m in ms}
    ids = sorted(byid)
    for title, pat in (("component-like", r"CORE|ENERG|FOOD|GOODS|SERV|EXCL"),
                       ("text-like", r"STATE|SPEECH|TEXT|MINUTE|PROJ|DOT|COMMUN|SURVEY|SENTIM"),
                       ("EA", r"^(EA_|ECB_|EUR)"), ("JP", r"^(JP_|BOJ|NIKKEI|JTSJ)")):
        print(title, "->", [i for i in ids if re.search(pat, i)])
    for mid in ("ECB_MRO", "ECB_DFR", "JP_POLICY_RATE", "JP_CPI_TOKYO_YOY", "JP_CPI_YOY", "EA_HICP_YOY",
                "VIX", "EURJPY", "UST_10Y", "DFEDTARU", "DFEDTARL"):
        m = byid.get(mid)
        if m is None:
            print("----", mid, "ABSENT")
            continue
        slim = {k: v for k, v in m.items() if k in (
            "metric_id", "id", "name", "display_name", "frequency", "criticality", "status", "freshness",
            "release_semantics", "release_date_available", "calc", "calc_note", "notes", "note", "economy",
            "observation_period_kind", "source", "source_key", "publication_rule", "release_lag_days")}
        print("----", mid)
        print(json.dumps(slim, ensure_ascii=False, indent=None)[:1500])
    # L1 rows quality
    print("==== L1")
    for row in rep["layers"]["L1_事实层"]["rows"]:
        print(json.dumps(row, ensure_ascii=False)[:420])
    print("==== L1 layer keys", list(rep["layers"]["L1_事实层"].keys()))
    for k, v in rep["layers"]["L1_事实层"].items():
        if k != "rows":
            print(k, json.dumps(v, ensure_ascii=False)[:1500])
    print("==== dimension_gaps")
    rp = rep["research_plan"]
    print(json.dumps(rp.get("dimension_gaps"), ensure_ascii=False)[:1500])
    print("==== publication_basis of cells")
    for c in rp["point_values"]["cells"]:
        for lab, a in c["anchors"].items():
            print(c["metric_id"], lab, json.dumps(a.get("publication_basis"), ensure_ascii=False)[:700])
    print("==== snapshot research_asof keys")
    for k in snap.keys():
        if k != "series_store":
            print(k, json.dumps(snap[k], ensure_ascii=False)[:300])


if __name__ == "__main__":
    main()
