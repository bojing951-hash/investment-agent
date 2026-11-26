# -*- coding: utf-8 -*-
"""s01_dump_raw.py — 只读转储: Gate A / 相关事实行 / 相关序列尾部 / 冻结日历 / 注册表相关条目。"""
import json, sys

snap_path, cal_path, reg_path = sys.argv[1], sys.argv[2], sys.argv[3]
snap = json.load(open(snap_path, encoding="utf-8"))
ss = snap["series_store"]
facts = snap["facts"]

print("===== research_as_of / target_date =====")
print(snap["research_as_of"], snap["target_date"], snap["timezone"])
print("quality:", json.dumps(snap["quality"], ensure_ascii=False))
print("series_store_notes:", json.dumps(snap["series_store_notes"], ensure_ascii=False)[:3000])
print("series_provenance keys:", list(snap["series_provenance"].keys()))
print("sources_status:", json.dumps(snap["sources_status"], ensure_ascii=False)[:2500])

print("\n===== gate_a =====")
print(json.dumps(snap["gate_a"], ensure_ascii=False, indent=1))

print("\n===== facts: metric ids present (105) =====")
ids = []
for f in facts:
    ids.append(f["metric_id"])
print(sorted(set(ids)))
print("count distinct:", len(set(ids)))
WATCH = ["EA_HICP_YOY","JP_CPI_YOY","JP_CPI_TOKYO_YOY","JP_POLICY_RATE","ECB_DFR","ECB_MRO",
         "EA_REAL_GDP_YOY","JP_REAL_GDP_YOY","BUND_10Y","BUND_2Y","JGB2Y","JGB5Y","JGB10Y",
         "UST_10Y","SPX","VIX","DAX","CAC40","NIKKEI225","EURUSD","USDJPY","DXY","DFEDTARU","DFEDTARL","FED_FUNDS","DFF"]
print("\n===== facts rows for WATCH metrics =====")
for f in facts:
    if f["metric_id"] in WATCH:
        print(json.dumps({k: f.get(k) for k in ("fact_id","value","unit","observation_date","as_of","quality_status","source","calc")}, ensure_ascii=False))

def tail(mid, n=None, since=None):
    s = ss.get(mid)
    if s is None:
        print(f"--- {mid}: NOT IN series_store"); return
    d, v = s["dates"], s["values"]
    print(f"--- {mid}: n={len(d)} first={d[0]} last={d[-1]} keys={[k for k in s.keys() if k not in ('dates','values')]}")
    extra = {k: s[k] for k in s.keys() if k not in ("dates","values")}
    print("    meta:", json.dumps(extra, ensure_ascii=False)[:700])
    idx = range(len(d))
    if since:
        idx = [i for i in idx if d[i] >= since]
    elif n:
        idx = list(range(max(0, len(d)-n), len(d)))
    for i in idx:
        print(f"    {d[i]}  {v[i]}")

print("\n===== series tails: monthly =====")
tail("EA_HICP_YOY", since="2024-01")
tail("JP_CPI_YOY", since="2024-01")
tail("JP_CPI_TOKYO_YOY")
tail("JP_POLICY_RATE", since="2024-10")
tail("ECB_DFR")
tail("ECB_MRO")
tail("EA_REAL_GDP_YOY", n=8)
tail("JP_REAL_GDP_YOY", n=8)
tail("DFEDTARU", n=4); tail("DFEDTARL", n=4); tail("FED_FUNDS", n=4); tail("DFF", n=4)

print("\n===== series tails: daily since 2026-10-15 =====")
for m in ["SPX","VIX","DAX","CAC40","NIKKEI225","EURUSD","USDJPY","DXY","UST_10Y","TIPS_10Y","BEI_10Y"]:
    tail(m, since="2026-10-15")

print("\n===== release calendar =====")
cal = json.load(open(cal_path, encoding="utf-8"))
print(json.dumps(cal, ensure_ascii=False, indent=1))

print("\n===== registry: entries for plan metrics + neighbours =====")
reg = json.load(open(reg_path, encoding="utf-8"))
print("registry top keys:", list(reg.keys())[:10] if isinstance(reg, dict) else type(reg))
metrics = reg.get("metrics", reg) if isinstance(reg, dict) else reg
if isinstance(metrics, dict):
    for m in WATCH + ["JP_POLICY_TARGET","JP_CORE_CPI_YOY","EA_CORE_HICP_YOY","BUND_10Y","BUND_2Y"]:
        if m in metrics:
            print(f"## {m}:", json.dumps(metrics[m], ensure_ascii=False))
        else:
            print(f"## {m}: NOT IN REGISTRY")
    print("registry metric ids:", sorted(metrics.keys()))
    ea_jp = [k for k,v in metrics.items() if isinstance(v, dict) and str(v.get("economy","")).upper() in ("EA","JP","EUROZONE","JAPAN","EUR")]
    print("economy in EA/JP:", sorted(ea_jp))
elif isinstance(metrics, list):
    for e in metrics:
        if e.get("id") in WATCH or e.get("metric_id") in WATCH:
            print(json.dumps(e, ensure_ascii=False))
    print("n registry entries:", len(metrics))
