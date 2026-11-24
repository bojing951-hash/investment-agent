#!/usr/bin/python3 -I
"""Read-only probe #3 for part C (targeted fields).
Args: <snapshot.json> <report.json> <agent_judgment.json> <release_calendar.json>
"""
import json
import sys


def main():
    snap = json.load(open(sys.argv[1], "r", encoding="utf-8"))
    rep = json.load(open(sys.argv[2], "r", encoding="utf-8"))
    aj = json.load(open(sys.argv[3], "r", encoding="utf-8"))
    cal = json.load(open(sys.argv[4], "r", encoding="utf-8"))
    print("==== snapshot facts")
    for f in snap["facts"]:
        if f["metric_id"] in ("JP_CPI_YOY", "EA_HICP_YOY", "JP_POLICY_RATE", "ECB_MRO", "ECB_DFR", "SPX", "VIX",
                              "NIKKEI225", "USDJPY", "DAX", "CAC40", "EURUSD", "DXY", "UST_10Y", "DFEDTARU"):
            keep = {k: v for k, v in f.items() if k not in ("derived", "calc", "identity", "display_name", "unit",
                                                              "value_type", "source", "calculation_ref")}
            print(json.dumps(keep, ensure_ascii=False)[:700])
    print("==== agent_judgment top keys")
    for k, v in aj.items():
        s = json.dumps(v, ensure_ascii=False)
        print(k, type(v).__name__, len(s), s[:160].replace("\n", " "))
    cv = aj.get("contract_verification") or rep["agent_judgment"].get("contract_verification")
    print("==== contract_verification keys", list(cv.keys()) if cv else None)
    for k, v in (cv or {}).items():
        if k not in ("verdicts", "six_checks", "map_checks"):
            print(" ", k, json.dumps(v, ensure_ascii=False)[:300])
    for v in (cv or {}).get("verdicts", []):
        print("  V", json.dumps(v, ensure_ascii=False)[:500])
    ent = cal.get("entries") or cal.get("records") or []
    if isinstance(ent, dict):
        ent = list(ent.values())
    print("==== calendar keys", list(cal.keys()), "n", len(ent))
    for e in ent:
        slim = {k: e.get(k) for k in e.keys() if k not in ("note", "notes", "evidence", "source_note")}
        print("  ", json.dumps(slim, ensure_ascii=False)[:380])
        if "BOJ" in json.dumps(e):
            print("     note:", e.get("note"))
    print("==== point cells")
    for c in rep["research_plan"]["point_values"]["cells"]:
        print("==", c["metric_id"], json.dumps({k: v for k, v in c.items() if k not in ("anchors", "policy_window_path")}, ensure_ascii=False)[:300])
        for lab, a in c["anchors"].items():
            print("  [%s]" % lab, json.dumps({k: v for k, v in a.items() if k != "vintage"}, ensure_ascii=False)[:700])


if __name__ == "__main__":
    main()
