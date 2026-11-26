#!/usr/bin/python3 -I
"""Final recompute points for the three candidate deviations + delivery-face checks (read-only).
usage: s26_final.py <snapshot.json> <agent_judgment.json> <AGENT_SEAT_ENVELOPE.json> <report.json> <MAP_REPORT.md> <MAP_REPORT.sha256> <FULL_REPORT.md>"""
import sys
sys.path.insert(0, "/tmp/r32-accept/review5/A_round1")
import json
import hashlib
import lib
snap = lib.load_json(sys.argv[1])
jud = lib.load_json(sys.argv[2])
env = lib.load_json(sys.argv[3])
rep = lib.load_json(sys.argv[4])
md = open(sys.argv[5], encoding="utf-8").read()
sha_file = open(sys.argv[6], encoding="utf-8").read().split()[0]
st = lib.Store(snap)
N = [0, 0]
MIS = []
def info(tag, val):
    print("   %-66s %s   (info)" % (tag, val))
def cmp(tag, mine, claim, nd=4):
    N[0] += 1
    if isinstance(mine, (int, float)) and isinstance(claim, (int, float)):
        ok = abs(round(mine, nd) - round(claim, nd)) <= 1e-9
    else:
        ok = mine == claim
    if not ok:
        N[1] += 1
        MIS.append("%s mine=%s claim=%s" % (tag, mine, claim))
    print("   %-66s mine=%-26s claim=%-22s %s" % (tag, mine, claim, "OK" if ok else "<<< MISMATCH"))
print("### (C) turning-candidate face rank (judgment reader_map.turnings[1].first_mover: 候选面全体首位为中国制造业PMI，增量3.40)")
face = env["reader_map_contract"]["engine_faces"]["turning_candidates_top9"]
def yoy_pct(mid, ym):
    v = st.at(mid, ym + "-01")
    b = st.at(mid, lib.shift_months(ym + "-01", -12))
    return (v / b - 1) * 100
rows = {r["metric_id"]: r for r in face}
cmp("CN_PPI_YOY 2026-02 (face value_before)", st.at("CN_PPI_YOY", "2026-02-01"), rows["CN_PPI_YOY"]["value_before"], nd=2)
cmp("CN_PPI_YOY 2026-05 (face value_after)", st.at("CN_PPI_YOY", "2026-05-01"), rows["CN_PPI_YOY"]["value_after"], nd=2)
cmp("CN_PPI_YOY delta recomputed (face 4.8)", round(st.at("CN_PPI_YOY", "2026-05-01") - st.at("CN_PPI_YOY", "2026-02-01"), 4), rows["CN_PPI_YOY"]["delta"], nd=2)
cmp("CN_PMI_MFG yoy% 2026-02 (face -2.3904)", yoy_pct("CN_PMI_MFG", "2026-02"), rows["CN_PMI_MFG"]["value_before"])
cmp("CN_PMI_MFG yoy% 2026-05 (face 1.0101)", yoy_pct("CN_PMI_MFG", "2026-05"), rows["CN_PMI_MFG"]["value_after"])
cmp("CN_PMI_MFG delta recomputed (face 3.4005)", round(yoy_pct("CN_PMI_MFG", "2026-05") - yoy_pct("CN_PMI_MFG", "2026-02"), 4), rows["CN_PMI_MFG"]["delta"])
info("face order by delta (metric:delta:dimension)", [(r["metric_id"], r["delta"], r["dimension"]) for r in face])
cmp("face first row metric (judgment: 中国制造业PMI)", face[0]["metric_id"], "CN_PMI_MFG")
info("rank of CN_PMI_MFG in the whole face (1-based)", [r["metric_id"] for r in face].index("CN_PMI_MFG") + 1)
info("rank of CN_PMI_MFG within growth dimension", [r["metric_id"] for r in face if r["dimension"] == "growth"].index("CN_PMI_MFG") + 1)
cmp("face is sorted by |delta| descending", [abs(r["delta"]) for r in face] == sorted([abs(r["delta"]) for r in face], reverse=True), True)
info("face |delta| order", [abs(r["delta"]) for r in face])
cmp("largest |delta| row in face is also first row", max(face, key=lambda r: abs(r["delta"]))["metric_id"], face[0]["metric_id"])
print("### (B) CN_PPI_YOY path after the window low (judgment: 中国 PPI 低点在 2025-11 且此后连升)")
path = st.in_range("CN_PPI_YOY", "2025-11-01", "2026-10-31")
low = min(path, key=lambda t: t[1])
cmp("window low month (judgment 2025-11)", low[0][:7], "2025-11")
cmp("window low value", low[1], -2.2, nd=2)
dec = [(path[i - 1][0][:7], path[i][0][:7], path[i - 1][1], path[i][1]) for i in range(1, len(path)) if path[i][1] < path[i - 1][1]]
info("monthly declines after the low", dec)
cmp("number of monthly declines after the low (judgment '连升' = 0)", len(dec), 0, nd=0)
info("monthly path", [(d[:7], v) for d, v in path])
print("### (A) BEI_10Y threshold sentence (judgment l4.scenarios[SCN2].falsification.threshold)")
last_below = [(d, v) for d, v in st.in_range("BEI_10Y", "2016-01-01", "2026-11-23") if v < 1.8][-1]
cmp("last obs below 1.8 date (judgment 2020-11-30)", last_below[0], "2020-11-30")
cmp("last obs below 1.8 value (judgment 1.77)", last_below[1], 1.77, nd=2)
lat = st.on_or_before("BEI_10Y", "2026-11-23")
cmp("latest BEI_10Y date (judgment 2026-11-20)", lat[0], "2026-11-20")
cmp("latest BEI_10Y value (judgment 2.15)", lat[1], 2.15, nd=2)
cmp("latest minus last-below reading, bp (judgment 低 35 个基点)", round((lat[1] - last_below[1]) * 100, 4), 35, nd=2)
cmp("latest minus threshold 1.8, bp", round((lat[1] - 1.8) * 100, 4), 35, nd=2)
print("### rendering / delivery face")
sc = jud["l4"]["scenarios"][1]["rows"]["falsification"]["threshold"]
cmp("SCN2 falsification threshold sentence rendered verbatim in MAP_REPORT.md", sc in md, True)
cmp("turnings[0].first_mover rendered verbatim in MAP_REPORT.md", jud["reader_map"]["turnings"][0]["first_mover"] in md, True)
cmp("turnings[1].first_mover rendered verbatim in MAP_REPORT.md", jud["reader_map"]["turnings"][1]["first_mover"] in md, True)
full = open(sys.argv[7], encoding="utf-8").read()
info("C1 explanation B verbatim: MAP / FULL", (jud["l3"]["contradictions"][0]["competing_explanations"][1] in md, jud["l3"]["contradictions"][0]["competing_explanations"][1] in full))
cmp("C1 explanation B rendered verbatim in FULL_REPORT.md", jud["l3"]["contradictions"][0]["competing_explanations"][1] in full, True)
cmp("SCN2 falsification threshold sentence rendered verbatim in FULL_REPORT.md", sc in full, True)
cmp("C1 statement rendered verbatim in FULL_REPORT.md", jud["l3"]["contradictions"][0]["statement"] in full, True)
h = hashlib.sha256(open(sys.argv[5], "rb").read()).hexdigest()
cmp("MAP_REPORT.md sha256 == sidecar MAP_REPORT.sha256", h == sha_file, True)
cv = rep["agent_judgment"]["contract_verification"]
vs = cv.get("verdicts") or []
cmp("contract verdicts count", len(vs), 14, nd=0)
cmp("contract verdicts not VERIFIED", [v.get("item") for v in vs if v.get("status") != "VERIFIED"], [])
for key in ("six_checks", "map_checks"):
    arr = cv.get(key) or []
    info(key, [(x.get("item"), x.get("status")) for x in arr])
    cmp("%s not VERIFIED" % key, [x.get("item") for x in arr if x.get("status") != "VERIFIED"], [])
cmp("semantic_review.seat_invoked (verdict-absent render expected)", rep["semantic_review"].get("seat_invoked"), False)
cmp("semantic_review.verdict", rep["semantic_review"].get("verdict"), None)
cmp("attach record attached_at (file mtime 06:40:04 HKT)", rep["agent_judgment"].get("attached_at"), "20261123T224004Z")
print("POINTS=%d MISMATCHES=%d" % (N[0], N[1]))
for m in MIS:
    print("MISMATCH:", m)
