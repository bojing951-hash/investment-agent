#!/usr/bin/python3 -I
# s03: 引擎面与原始切片(只读), 供人工逐项核对
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rc_lib import *

snap_p, rep_p, cal_p, reg_p, aj_p, outdir = sys.argv[1:7]
snap, rep, cal, reg, aj = load(snap_p, rep_p, cal_p, reg_p, aj_p)
SS = snap["series_store"]
rp = rep["research_plan"]
L = []
def p(*a):
    L.append(" ".join(str(x) for x in a))

p("== calendar entries (%d) ==" % len(cal["entries"]))
for e in cal["entries"]:
    p("  ", json.dumps({k: v for k, v in e.items() if k not in ("note", "notes", "spec", "source_note")}, ensure_ascii=False)[:420])
p("== calendar batches ==", json.dumps(cal.get("batches"), ensure_ascii=False)[:1500])
p("== calendar spec ==", str(cal.get("spec"))[:900])
p("== turning_candidates ==")
p(json.dumps(rp["turning_candidates"], ensure_ascii=False, indent=1))
p("== policy_event_clusters ==")
p(json.dumps(rp["policy_event_clusters"], ensure_ascii=False, indent=1))
p("== notes ==", json.dumps(rep.get("notes"), ensure_ascii=False)[:3000])
p("== gate_a ==", json.dumps(snap["gate_a"], ensure_ascii=False, indent=1))
p("== quality ==", json.dumps(snap["quality"], ensure_ascii=False))
p("== sources_status.ea/jp ==", json.dumps(snap["sources_status"].get("ea"), ensure_ascii=False)[:500], "|", json.dumps(snap["sources_status"].get("jp"), ensure_ascii=False)[:800])
p("== snapshot.notes ==", json.dumps(snap["notes"], ensure_ascii=False)[:1500])
v = rep["agent_judgment"].get("validation")
p("== agent_judgment.validation ==", json.dumps(v, ensure_ascii=False)[:2500])
sr = rep["semantic_review"]
p("== semantic_review(keys) ==", json.dumps({k: v for k, v in sr.items() if k not in ("prior_verdicts",)}, ensure_ascii=False)[:1500])
p("== agent_judgment.meta ==", json.dumps({k: v for k, v in rep["agent_judgment"].items() if k not in ("contract_verification", "reader_map_faces", "validation")}, ensure_ascii=False)[:1500])
p("== dimension_gaps ==", json.dumps(rp["dimension_gaps"], ensure_ascii=False)[:2800])
p("== asof_discipline / cross_face ==", rp.get("asof_discipline"), rp.get("cross_face_consistency"), "| consumed_time_spans", rp.get("consumed_time_spans"))
p("== evidence_gate.vintage ==", json.dumps(rep["run"]["evidence_gate"].get("vintage"), ensure_ascii=False)[:1200])
p("== plan metrics (%d) ==" % len(rp["metrics"]), rp["metrics"])
p("== evidence_index metric ids (%d) ==" % len(rep["evidence_index"]), sorted(set(r.get("metric_id") for r in rep["evidence_index"])))
p("== evidence_index rows w/ JP/CN/US macro ==", [r["ref"] for r in rep["evidence_index"] if any(r["ref"].startswith(x) for x in ("JP_", "CN_", "CPI", "CORE_", "US_REAL", "UNEMP", "INDPRO", "DFED", "DFF"))])
# 原始切片
p("== DFEDTARU changes 2025-10-01..CUT ==", changes(SS, "DFEDTARU", "2025-10-01", CUT))
p("== DFEDTARL changes 2025-10-01..CUT ==", changes(SS, "DFEDTARL", "2025-10-01", CUT))
p("== DFF changes 2025-10-01..CUT ==", changes(SS, "DFF", "2025-10-01", CUT))
p("== DFF obs 2026-08-17..2026-08-25 ==", [(d, v) for d, v in series(SS, "DFF") if "2026-08-17" <= d <= "2026-08-25"])
p("== DFF obs 2026-11-13..CUT ==", [(d, v) for d, v in series(SS, "DFF") if "2026-11-13" <= d <= CUT])
p("== DFEDTARU obs 2026-09-10..2026-09-22 ==", [(d, v) for d, v in series(SS, "DFEDTARU") if "2026-09-10" <= d <= "2026-09-22"])
p("== CN_POLICY_OVERNIGHT all ==", series(SS, "CN_POLICY_OVERNIGHT"))
p("== CN_OMO_7D 2026-08-15.. ==", [(d, v) for d, v in series(SS, "CN_OMO_7D") if d >= "2026-08-15"])
p("== CN_OMO_7D first/last/n ==", series(SS, "CN_OMO_7D")[0], series(SS, "CN_OMO_7D")[-1], len(series(SS, "CN_OMO_7D")))
p("== CN_LPR_1Y 2026-08-01..CUT (distinct runs) ==")
prev = None
for d, v in series(SS, "CN_LPR_1Y"):
    if d >= "2025-11-01" and v != prev:
        p("   ", d, v); prev = v
p("== CN_LPR_1Y obs 2026-11-18..CUT ==", [(d, v) for d, v in series(SS, "CN_LPR_1Y") if d >= "2026-11-18"])
p("== JP_POLICY_RATE 2025-09.. ==", [(d[:7], v) for d, v in series(SS, "JP_POLICY_RATE") if d >= "2025-09-01"])
p("== CPI months 2025-07..2026-10 ==", [(d[:7], v) for d, v in series(SS, "CPI") if "2025-07" <= d[:7] <= "2026-10"])
p("== CORE_CPI months 2025-07..2026-10 ==", [(d[:7], v) for d, v in series(SS, "CORE_CPI") if "2025-07" <= d[:7] <= "2026-10"])
p("== CORE_PCE months 2025-05.. ==", [(d[:7], v) for d, v in series(SS, "CORE_PCE") if d >= "2025-05-01"])
p("== US_REAL_GDP 2025-01.. ==", [(d[:7], v) for d, v in series(SS, "US_REAL_GDP") if d >= "2025-01-01"])
p("== JP_REAL_GDP_YOY 2025-01.. ==", [(d[:7], v) for d, v in series(SS, "JP_REAL_GDP_YOY") if d >= "2025-01-01"])
p("== UNEMPLOYMENT 2026-01.. ==", [(d[:7], v) for d, v in series(SS, "UNEMPLOYMENT") if d >= "2026-01-01"])
p("== UNEMPLOYMENT months missing in 2016-11..2026-10 ==")
have = set(d[:7] for d, v in series(SS, "UNEMPLOYMENT"))
import datetime as _dt
allm = []
y, m = 2016, 11
while (y, m) <= (2026, 10):
    allm.append("%04d-%02d" % (y, m)); m += 1
    if m == 13: y, m = y + 1, 1
p("   ", [x for x in allm if x not in have], "first", series(SS, "UNEMPLOYMENT")[0])
p("== INDPRO 2025-07.. ==", [(d[:7], v) for d, v in series(SS, "INDPRO") if d >= "2025-07-01"])
p("== JP_CPI_YOY 2025-09.. ==", [(d, v) for d, v in series(SS, "JP_CPI_YOY") if d >= "2025-09-01"])
p("== JP_CPI_TOKYO_YOY all ==", series(SS, "JP_CPI_TOKYO_YOY"))
p("== CN_PMI_MFG 2025-12.. ==", [(d, v) for d, v in series(SS, "CN_PMI_MFG") if d >= "2025-12-01"])
p("== CN_CPI_YOY 2026-06.. ==", [(d, v) for d, v in series(SS, "CN_CPI_YOY") if d >= "2026-06-01"])
p("== CN_PPI_YOY 2026-06.. ==", [(d, v) for d, v in series(SS, "CN_PPI_YOY") if d >= "2026-06-01"])
p("== WTI_F < anchor within ANC..CUT ==", [(d, v) for d, v in series(SS, "WTI_F") if ANC <= d <= CUT and v < 87.06])
p("== WTI_F 2026-11-02..CUT ==", [(d, v) for d, v in series(SS, "WTI_F") if d >= "2026-11-02"])
p("== WTI_F obs 2026-08-14..2026-09-22 ==", [(d, v) for d, v in series(SS, "WTI_F") if "2026-08-14" <= d <= "2026-09-22"])
p("== BRENT_F 2026-08-20..2026-08-25 / 10-30 / CUT ==", [(d, v) for d, v in series(SS, "BRENT_F") if "2026-08-20" <= d <= "2026-08-25"], at(SS, "BRENT_F", "2026-10-30"), at_or_before(SS, "BRENT_F", CUT))
p("== WTI_SPOT_M 2026-06.. ==", [(d, v) for d, v in series(SS, "WTI_SPOT_M") if d >= "2026-06-01"])
p("== assets 2026-10-20..2026-10-23 and 2026-11-18..CUT ==")
for m in ("SPX", "NIKKEI225", "SHCOMP", "DAX", "CAC40", "VIX", "DXY", "USDJPY", "USDCNY", "GOLD_F"):
    p("  ", m, [(d, v) for d, v in series(SS, m) if "2026-10-20" <= d <= "2026-10-23"], [(d, v) for d, v in series(SS, m) if d >= "2026-11-18"])
with open(os.path.join(outdir, "out_s03_slices.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(L))
print("slices written, lines", len(L))
