#!/usr/bin/python3 -I
"""Exact original strings of candidate findings + locate them in the reader reports (read-only).
usage: s19_originals.py <agent_judgment.json> <report.json> <snapshot.json> <MAP_REPORT.md> <FULL_REPORT.md> <report.md>"""
import sys
sys.path.insert(0, "/tmp/r32-accept/review5/A_round1")
import json
import lib
jud = lib.load_json(sys.argv[1])
rep = lib.load_json(sys.argv[2])
snap = lib.load_json(sys.argv[3])
st = lib.Store(snap)

def find(o, path, pred, out):
    if isinstance(o, dict):
        for k, v in o.items():
            find(v, path + "/" + str(k), pred, out)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            find(v, path + "[%d]" % i, pred, out)
    elif isinstance(o, str) and pred(o):
        out.append((path, o))

NEEDLES = ["低 35 个基点", "此后连升", "候选面全体首位", "解释相容", "回到降息前水平"]
res = {}
for nd in NEEDLES:
    out = []
    find(jud, "", lambda s, nd=nd: nd in s, out)
    res[nd] = out
    print("== needle:", nd, "hits:", len(out))
    for p, s in out:
        print("  PATH:", p)
        print("  TEXT:", s)
        print()
# reader reports
for fp in sys.argv[4:]:
    txt = open(fp, encoding="utf-8").read()
    lines = txt.split("\n")
    print("#### FILE", fp, "lines=", len(lines))
    for nd in NEEDLES:
        hits = [i + 1 for i, l in enumerate(lines) if nd in l]
        print("  ", nd, "-> lines", hits)
    for key in ("席位待唤起", "独立语义审查待裁", "语义审查"):
        hits = [i + 1 for i, l in enumerate(lines) if key in l]
        print("  ", key, "-> lines", hits[:10], "n=", len(hits))
# recompute: CN PPI monthly path, CN PMI candidate window
print("## CN_PPI_YOY monthly 2025-09..2026-11")
for ym in [lib.shift_months("2025-09-01", i)[:7] for i in range(15)]:
    print("  ", ym, st.at("CN_PPI_YOY", ym + "-01"))
print("## CN_PMI_MFG monthly 2025-11..2026-10 (level) and yoy pct")
for ym in [lib.shift_months("2025-11-01", i)[:7] for i in range(12)]:
    v = st.at("CN_PMI_MFG", ym + "-01")
    b = st.at("CN_PMI_MFG", lib.shift_months(ym + "-01", -12))
    print("  ", ym, v, "yoy_pct=", lib.r((v / b - 1) * 100, 4) if (v is not None and b) else None)
print("## CN_PPI_YOY 2026-02 / 2026-05")
print("  ", st.at("CN_PPI_YOY", "2026-02-01"), st.at("CN_PPI_YOY", "2026-05-01"))
# engine face
env = jud.get("envelope") or {}
data = env.get("data") or {}
tc = (data.get("reader_map_contract") or {}).get("engine_faces", {}).get("turning_candidates_top9")
print("## envelope/reader_map_contract/engine_faces/turning_candidates_top9")
for i, row in enumerate(tc or []):
    print("  [%d]" % i, json.dumps(row, ensure_ascii=False)[:400])
# reader_map.turnings
rm = jud.get("reader_map") or {}
print("## reader_map.turnings count", len(rm.get("turnings") or []))
for i, t in enumerate(rm.get("turnings") or []):
    print("  turning[%d] keys" % i, sorted(t.keys()))
    print("   first_mover:", t.get("first_mover"))
