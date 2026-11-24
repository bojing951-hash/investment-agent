#!/usr/bin/python3 -I
# Seat script 11: verbatim extraction for the PROSE/VERDICT drafting (read-only).
# usage: s11_probe.py <agent_judgment.json> <release_calendar.json> <snapshot.json> <MAP_REPORT.md> <FULL_REPORT.md> <report.md> <what...>
import json, sys

aj = json.load(open(sys.argv[1], encoding="utf-8"))
cal = json.load(open(sys.argv[2], encoding="utf-8"))
snap = json.load(open(sys.argv[3], encoding="utf-8"))
mds = [open(p, encoding="utf-8").read().split("\n") for p in sys.argv[4:7]]
whats = sys.argv[7:]

def find_lines(needle):
    for name, lines in zip(("MAP_REPORT.md", "FULL_REPORT.md", "report.md"), mds):
        for i, ln in enumerate(lines, 1):
            if needle in ln:
                print("  %s L%d: %s" % (name, i, ln.strip()[:900]))

for w in whats:
    print("=== %s ===" % w)
    if w == "scenarios":
        for s in aj.get("l4", aj.get("scenarios", [])).get("scenarios", []) if isinstance(aj.get("l4"), dict) else []:
            print(json.dumps(s, ensure_ascii=False, indent=1))
    elif w == "aj-keys":
        print(list(aj.keys()))
        for k in aj.keys():
            v = aj[k]
            print(k, type(v).__name__, (list(v.keys()) if isinstance(v, dict) else len(v) if isinstance(v, list) else ""))
    elif w == "cal-ea":
        print("calendar keys:", list(cal.keys()))
        for e in cal.get("entries", cal.get("facts", [])):
            s = json.dumps(e, ensure_ascii=False)
            if "HICP" in s or "EA_" in s:
                print(" ", s[:600])
    elif w == "cal-rules":
        for k in cal.keys():
            if k not in ("entries", "facts"):
                print(k, "=", json.dumps(cal[k], ensure_ascii=False)[:2500])
    elif w == "cal-jp":
        for e in cal.get("entries", cal.get("facts", [])):
            s = json.dumps(e, ensure_ascii=False)
            if "JP" in s or "BOJ" in s:
                print(" ", s[:900])
    elif w == "store-pol":
        for mid in ("DFEDTARU", "DFEDTARL", "DFF", "FED_FUNDS", "ECB_DFR", "ECB_MRO", "JP_POLICY_RATE", "JP_POLICY_TARGET", "JGB_10Y", "JGB_2Y", "UMCSENT", "BRENT_F", "EURUSD", "DXY", "UST_10Y", "TIPS_10Y", "BEI_10Y"):
            s = snap["series_store"].get(mid)
            if s is None:
                print(" ", mid, "NOT IN STORE")
                continue
            pts = [(d, v) for d, v in zip(s["dates"], s["values"]) if d >= "2026-05-01" and v is not None]
            # compress: print value changes and last
            out = []
            prev = None
            for d, v in pts:
                if prev is None or abs(v - prev) > 1e-9:
                    out.append((d, v))
                prev = v
            print(" ", mid, "n=%d" % len(pts), "changes/first:", out[:40], "last:", pts[-1] if pts else None)
    elif w == "l3":
        for c in aj.get("l3", {}).get("contradictions", aj.get("l3", {}).get("items", [])):
            print(json.dumps(c, ensure_ascii=False, indent=1))
    elif w == "mech":
        for c in aj.get("l3", {}).get("mechanism_chains", []):
            print(json.dumps(c, ensure_ascii=False, indent=1))
    elif w == "qgn":
        for i, n in enumerate(aj.get("quality_gate_notes", [])):
            print(i, json.dumps(n, ensure_ascii=False))
    elif w == "decl":
        print(json.dumps(aj.get("agent_declaration"), ensure_ascii=False, indent=1))
    elif w == "rm-keys":
        rm = aj.get("reader_map", {})
        print(list(rm.keys()))
        for k in ("headline_conclusion", "verdict_note", "narrative"):
            if k in rm:
                print(k, "=", json.dumps(rm[k], ensure_ascii=False))
    elif w == "trans":
        for l in aj.get("reader_map", {}).get("transmission", []):
            print(json.dumps(l, ensure_ascii=False, indent=1))
    elif w == "turn":
        for t in aj.get("reader_map", {}).get("turnings", []):
            print(json.dumps(t, ensure_ascii=False, indent=1))
    elif w == "regions":
        for t in aj.get("reader_map", {}).get("regions", []):
            print(json.dumps(t, ensure_ascii=False, indent=1))
    elif w == "hist":
        print(json.dumps(aj.get("reader_map", {}).get("history_periods"), ensure_ascii=False))
        print(json.dumps(aj.get("reader_map", {}).get("history_zero_case_note"), ensure_ascii=False))
    elif w == "find":
        pass
    else:
        find_lines(w)
