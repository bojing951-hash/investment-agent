#!/usr/bin/python3 -I
"""席位自写探针 s13b: BRENT_F 在 facts / 证据索引 / report.json 的出场(只读)."""
import json
import re
import sys

snap = json.load(open(sys.argv[1], "r", encoding="utf-8"))
run = sys.argv[2]
print("== facts BRENT_F ==")
for f in snap["facts"]:
    if f["metric_id"] in ("BRENT_F", "WTI_F", "OIL_F") or "BRENT" in f["metric_id"]:
        print({k: f[k] for k in f if k in ("fact_id", "metric_id", "value", "observation_date", "quality_status")})
ss = snap["series_store"]
print("series ids containing OIL/BRENT/WTI:", [k for k in ss if any(t in k for t in ("OIL", "BRENT", "WTI", "CRUDE"))])
print("== evidence_index rows mentioning BRENT ==")
ev = json.load(open(run + "/evidence_index.json", "r", encoding="utf-8"))
rows = ev if isinstance(ev, list) else ev.get("rows", ev)
for r in rows:
    s = json.dumps(r, ensure_ascii=False)
    if "BRENT" in s:
        print(s[:400])
print("== grep 92.44 / 91.49 / 117.64 / 91.62 in rendered/engine files ==")
for name in ("MAP_REPORT.md", "FULL_REPORT.md", "report.md", "report.json", "AGENT_SEAT_ENVELOPE.json"):
    txt = open(run + "/" + name, "r", encoding="utf-8").read()
    for tok in ("92.44", "91.49", "117.64", "91.62", "91.5", "91.95", "91.98"):
        hits = [m.start() for m in re.finditer(re.escape(tok), txt)]
        if hits:
            ctx = txt[max(0, hits[0] - 90):hits[0] + 60].replace("\n", " ")
            print(f"{name}: '{tok}' x{len(hits)} e.g. …{ctx}…")
