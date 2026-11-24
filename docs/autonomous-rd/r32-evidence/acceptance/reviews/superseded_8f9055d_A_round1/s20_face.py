#!/usr/bin/python3 -I
"""Locate the engine turning-candidate face in report.json / envelope and recompute its rows from the series.
usage: s20_face.py <report.json> <AGENT_SEAT_ENVELOPE.json> <snapshot.json>"""
import sys
sys.path.insert(0, "/tmp/r32-accept/review5/A_round1")
import json
import lib
rep = lib.load_json(sys.argv[1])
env = lib.load_json(sys.argv[2])
snap = lib.load_json(sys.argv[3])
st = lib.Store(snap)

def find_key(o, path, key, out):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == key:
                out.append((path + "/" + k, v))
            find_key(v, path + "/" + k, key, out)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            find_key(v, path + "[%d]" % i, key, out)

for name, obj in (("report.json", rep), ("envelope", env)):
    out = []
    find_key(obj, "", "turning_candidates_top9", out)
    print("##", name, "hits", len(out))
    for p, v in out:
        print("  PATH", p, "n=", len(v) if isinstance(v, list) else type(v))
        if isinstance(v, list):
            for i, row in enumerate(v):
                print("   [%d]" % i, json.dumps(row, ensure_ascii=False)[:520])
N = [0, 0]
MIS = []
def cmp(tag, mine, claim, nd=4):
    N[0] += 1
    ok = abs(round(mine, nd) - round(claim, nd)) <= 1e-9 if isinstance(mine, (int, float)) and isinstance(claim, (int, float)) else mine == claim
    if not ok:
        N[1] += 1
        MIS.append("%s mine=%s claim=%s" % (tag, mine, claim))
    print("   %-62s mine=%-24s claim=%-22s %s" % (tag, mine, claim, "OK" if ok else "<<< MISMATCH"))
out = []
find_key(rep, "", "turning_candidates_top9", out)
rows = out[0][1] if out else []
# first row and the CN_PMI row
top = rows[0]
print("## top row keys", sorted(top.keys()))
for k in sorted(top.keys()):
    print("   ", k, "=", json.dumps(top[k], ensure_ascii=False)[:200])
