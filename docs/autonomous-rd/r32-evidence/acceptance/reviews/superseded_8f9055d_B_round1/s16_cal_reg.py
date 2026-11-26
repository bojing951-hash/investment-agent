import json, sys
cal_p, reg_p, snap_p = sys.argv[1], sys.argv[2], sys.argv[3]
with open(cal_p) as f: cal = json.load(f)
print("CAL top keys:", list(cal.keys()))
for k, v in cal.items():
    if not isinstance(v, (list, dict)): print("  ", k, "=", v)
ents = cal.get("entries") or cal.get("items") or []
print("n entries:", len(ents))
for e in ents:
    print(json.dumps(e, ensure_ascii=False))
with open(reg_p) as f: reg = json.load(f)
print("REG top keys:", list(reg.keys()))
for k, v in reg.items():
    if not isinstance(v, (list, dict)): print("  ", k, "=", v)
ms = reg.get("metrics")
print(type(ms), len(ms))
sample = ms[0] if isinstance(ms, list) else list(ms.values())[0]
print("metric keys:", list(sample.keys()))
for want in ("CORE_PCE","CPI","EA_REAL_GDP_YOY","EA_HICP_YOY","JP_POLICY_RATE","JP_POLICY_TARGET","JGB10Y","BRENT_F","US_REAL_GDP","UNEMPLOYMENT","INDPRO","CORE_CPI","BEI_10Y","TIPS_10Y","USDJPY","DFEDTARU","ECB_DFR"):
    m = None
    if isinstance(ms, list):
        for x in ms:
            if x.get("metric_id") == want: m = x; break
    else:
        m = ms.get(want)
    if m is None:
        print(want, ": NOT IN REGISTRY"); continue
    keep = {k: m[k] for k in m if k in ("metric_id","status","frequency","max_calendar_lag_days","release_lag","expected_release_lag","publication","release_rule","first_publish","vintage","collector","economy","dimension","latest_observation","coverage","span","obs_note","calc","note","notes")}
    print(want, "=>", json.dumps(keep, ensure_ascii=False)[:900])
