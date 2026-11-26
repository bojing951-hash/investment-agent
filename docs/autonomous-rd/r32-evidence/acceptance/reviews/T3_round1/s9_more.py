#!/usr/bin/env python3
"""Extra read-only lookups needed to close remaining recompute items (T3 round 1).
usage: python3 -I s9_more.py <run_dir>
"""
import datetime as dt
import json
import os
import sys


def load(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def walk(obj, path, hits, needle):
    if isinstance(obj, dict):
        for k, v in obj.items():
            walk(v, path + "." + str(k), hits, needle)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            walk(v, path + "[%d]" % i, hits, needle)
    elif isinstance(obj, str):
        if needle in obj:
            hits.append((path, obj[:300]))


def main():
    run = sys.argv[1]
    snap = load(os.path.join(run, "root_overlay", "data", "daily", "research_snapshot_20261123.json"))
    cal = load(os.path.join(run, "root_overlay", "config", "release_calendar.json"))
    reg = load(os.path.join(run, "root_overlay", "config", "metric_registry.json"))
    rep = load(os.path.join(run, "report.json"))
    SS = snap["series_store"]
    regm = {m["metric_id"]: m for m in reg["metrics"]}

    def S(m):
        return dict(zip(SS[m]["dates"], SS[m]["values"]))

    print("### JP_CPI_YOY 2024-10..2026-02")
    s = S("JP_CPI_YOY")
    print([(k[:7], s[k]) for k in sorted(s) if "2024-10-01" <= k <= "2026-02-01"])
    print("### JP_CPI_YOY max after 2025-01:", max((v, k) for k, v in s.items() if k > "2025-01-01"))
    print("### EA_HICP_YOY 2025-05..2026-01")
    e = S("EA_HICP_YOY")
    print([(k[:7], e[k]) for k in sorted(e) if "2025-05-01" <= k <= "2026-01-01"])
    for m in ("ECB_MRO", "ECB_DFR"):
        print("### %s obs since 2025-01" % m, [(k, v, dt.date.fromisoformat(k).strftime("%a")) for k, v in S(m).items() if k >= "2025-01-01"])
        ser = S(m)
        nonwed = [(k, v) for k, v in ser.items() if dt.date.fromisoformat(k).strftime("%a") != "Wed"]
        print("### %s non-Wednesday obs (n=%d of %d)" % (m, len(nonwed), len(ser)), nonwed[:40])
        last10 = sorted(ser)[-12:]
        print("### %s last 12 obs weekdays" % m, [(k, dt.date.fromisoformat(k).strftime("%a")) for k in last10])
    print("### calendar EA HICP entries")
    for x in cal["entries"]:
        blob = json.dumps(x, ensure_ascii=False)
        if "HICP" in blob or "EA_" in blob or "ECB" in blob:
            print(blob[:700])
    print("### calendar all entry ids/kinds")
    print([(x["entry_id"], x.get("kind"), x.get("metric_id") or x.get("metric_ids")) for x in cal["entries"]])
    print("### calendar top-level keys", sorted(cal.keys()), "version", cal.get("version"), "updated", cal.get("updated"))
    for eid in ("RC-JP-BOJ-TARGET-2026-09", "RC-JP-BOJ-MAINT-2026-10"):
        x = [y for y in cal["entries"] if y["entry_id"] == eid][0]
        print("### calendar", eid, json.dumps(x, ensure_ascii=False))
    print("### calendar: any entry mentioning ECB/MRO/DFR/欧央行")
    print([x["entry_id"] for x in cal["entries"] if any(t in json.dumps(x, ensure_ascii=False) for t in ("ECB", "MRO", "DFR", "欧央行", "存款便利", "再融资"))])
    for m in ("ECB_MRO", "ECB_DFR", "JP_POLICY_RATE", "JP_CPI_YOY", "EA_HICP_YOY", "JP_CPI_TOKYO_YOY"):
        mm = regm.get(m)
        if mm is None:
            print("### registry", m, "ABSENT")
            continue
        print("### registry", m, "keys", sorted(mm.keys()))
        for k in ("freshness", "release_semantics", "release_rule", "frequency", "decision_dated", "calc", "unit", "display_name", "series_semantics", "publication"):
            if k in mm:
                print("   ", k, "=", json.dumps(mm[k], ensure_ascii=False)[:900])
    print("### registry JP_POLICY_TARGET:", regm.get("JP_POLICY_TARGET"))
    # search report.json for engine faces
    for needle in ("2026-06-11", "2026-09-10", "全为周三", "窗启时在值", "0.478", "周四", "pending", "待生效"):
        hits = []
        walk(rep, "", hits, needle)
        print("### report.json hits for %r: %d" % (needle, len(hits)))
        for p, t in hits[:12]:
            print("    ", p[:140], "=>", t[:200].replace("\n", " "))
    for name in ("MAP_REPORT.md", "FULL_REPORT.md", "report.md"):
        with open(os.path.join(run, name), "r", encoding="utf-8") as fh:
            txt = fh.read()
        for needle in ("全为周三", "待生效", "席位待唤起", "独立语义审查待裁", "草稿", "blocked"):
            idx = [i for i in range(len(txt)) if txt.startswith(needle, i)]
            for i in idx[:3]:
                print("### %s contains %r @%d: ...%s..." % (name, needle, i, txt[max(0, i - 80): i + 120].replace("\n", " / ")))
    print("### L1 structure")
    l1 = rep["layers"]["L1_事实层"]
    print(type(l1).__name__, sorted(l1.keys()) if isinstance(l1, dict) else len(l1))
    rows = l1.get("rows") if isinstance(l1, dict) else l1
    print("n rows", len(rows), "row0 keys", sorted(rows[0].keys()))
    print([(r.get("metric_id"), r.get("observation_date"), r.get("value"), r.get("quality_status")) for r in rows if r.get("metric_id") in ("JP_CPI_YOY", "EA_HICP_YOY", "JP_POLICY_RATE", "ECB_MRO", "ECB_DFR", "JP_CPI_TOKYO_YOY", "USDJPY", "SPX", "VIX", "DAX", "CAC40", "NIKKEI225", "UST_10Y", "EURUSD", "DXY")])
    print("### policy_event_clusters", json.dumps(rep["research_plan"]["policy_event_clusters"], ensure_ascii=False)[:3500])
    print("### ex_post_offsets", json.dumps(rep["research_plan"]["ex_post_offsets"], ensure_ascii=False)[:800])
    print("### cross_face_consistency", json.dumps(rep["research_plan"]["cross_face_consistency"], ensure_ascii=False)[:1500])
    print("### anchor_semantics_note", json.dumps(rep["research_plan"]["anchor_semantics_note"], ensure_ascii=False)[:800])
    print("### asof_discipline", json.dumps(rep["research_plan"]["asof_discipline"], ensure_ascii=False)[:800])
    print("### run keys", sorted(rep["run"].keys()))
    print("### run.data_requirements", json.dumps(rep["run"].get("data_requirements"), ensure_ascii=False)[:2500])
    print("### run.evidence_gate", json.dumps(rep["run"].get("evidence_gate"), ensure_ascii=False)[:1500])
    print("### run.frozen_inputs", json.dumps(rep["run"].get("frozen_inputs"), ensure_ascii=False)[:1200])
    print("### report.semantic_review", json.dumps(rep.get("semantic_review"), ensure_ascii=False)[:600])
    print("### report.notes", json.dumps(rep.get("notes"), ensure_ascii=False)[:2500])
    print("### weekdays", [(d, dt.date.fromisoformat(d).strftime("%a")) for d in ("2026-05-22", "2026-05-23", "2026-10-23", "2026-11-13", "2026-11-20", "2026-11-23", "2026-09-18", "2026-09-24", "2026-10-30", "2026-09-17", "2026-11-20", "2026-11-16", "2026-11-05", "2026-05-16", "2026-05-20", "2026-05-05", "2026-04-29", "2026-10-30", "2026-11-18")])
    eu, uj = S("EURUSD"), S("USDJPY")
    print("### legs 2026-05-22", eu.get("2026-05-22"), uj.get("2026-05-22"), "| 2026-05-21", eu.get("2026-05-21"), uj.get("2026-05-21"))
    print("### fx daily 11-13..11-20 EURUSD", [(k, eu[k]) for k in sorted(eu) if "2026-11-12" <= k <= "2026-11-23"])
    print("### fx daily 11-13..11-20 USDJPY", [(k, uj[k]) for k in sorted(uj) if "2026-11-12" <= k <= "2026-11-23"])
    for name in ("AGENT_SEAT_ENVELOPE.json", "views_digest.json"):
        p = os.path.join(run, name)
        print("### file", name, "size", os.path.getsize(p))
        obj = load(p)
        print(json.dumps(obj, ensure_ascii=False, indent=1)[:6000])


if __name__ == "__main__":
    main()
