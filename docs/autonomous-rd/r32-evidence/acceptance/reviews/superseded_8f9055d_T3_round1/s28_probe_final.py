#!/usr/bin/python3 -I
"""Final probes behind citations used in the deliverables.
Read-only. Args: <out_dir> <agent_judgment.json> <run_dir>
"""
import hashlib
import json
import os
import re
import sys

out_dir, jdp, run_dir = sys.argv[1], sys.argv[2], sys.argv[3]
d = json.load(open(os.path.join(out_dir, "recompute_points.json"), "r", encoding="utf-8"))
want = {"O013", "G018", "D026", "D036", "O014", "A026", "I012", "I013", "M005", "O009", "O010", "N001", "O007", "O008", "K015"}
for r in d["rows"]:
    if r["id"] in want:
        print("ROW", r["id"], "| where:", r.get("where"))
        print("    src:", r.get("src"))
        print("    computed:", json.dumps(r.get("computed"), ensure_ascii=False)[:700])
        print("    reported:", json.dumps(r.get("reported"), ensure_ascii=False)[:400])
        print("    note:", r.get("note"))
        print("    text:", (r.get("text") or "")[:500])
jd = json.load(open(jdp, "r", encoding="utf-8"))
rm = jd["reader_map"]
for i, lk in enumerate(rm["transmission"][0]["links"]):
    print("=== ring", i + 1, "verdict_note (full)")
    print(lk.get("verdict_note"))


def walk(o, out, path=""):
    if isinstance(o, str):
        out.append((path, o))
    elif isinstance(o, dict):
        for k, v in o.items():
            walk(v, out, path + "." + k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, out, path + "[%d]" % i)
    return out


print("=== reader_map keys", sorted(rm.keys()))
for k in rm:
    v = rm[k]
    if not isinstance(v, (str, list)) or (isinstance(v, list) and len(json.dumps(v, ensure_ascii=False)) < 400):
        print("   ", k, "=", json.dumps(v, ensure_ascii=False)[:400])
    else:
        print("   ", k, "= <%s len %d>" % (type(v).__name__, len(v)))
for i, tr in enumerate(rm["turnings"]):
    print("    turning", i, "keys", sorted(tr.keys()))


allstr = walk(jd, [])
for kw in ("复检", "尚不能区分", "事后", "同期公布"):
    print("=== keyword", kw)
    for p, s in allstr:
        for m in re.finditer(kw, s):
            print("  ", p, "|", s[max(0, m.start() - 60):m.end() + 80].replace("\n", " "))
print("=== overlay sha16 at build time")
for n, p in (("release_calendar", "config/release_calendar.json"), ("metric_registry", "config/metric_registry.json"),
             ("snapshot", "data/daily/research_snapshot_20261123.json")):
    print("  ", n, hashlib.sha256(open(os.path.join(run_dir, "root_overlay", p), "rb").read()).hexdigest()[:16])
mp = open(os.path.join(run_dir, "MAP_REPORT.md"), "rb").read()
print("   MAP_REPORT.md sha256", hashlib.sha256(mp).hexdigest())
for fn in os.listdir(run_dir):
    if fn.startswith("MAP_REPORT.sha"):
        print("   ", fn, open(os.path.join(run_dir, fn), "r", encoding="utf-8").read().strip()[:200])
