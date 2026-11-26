import json, sys
snap_p, rep_p, ej_p = sys.argv[1], sys.argv[2], sys.argv[3]
with open(snap_p) as f: s = json.load(f)
with open(rep_p) as f: p = json.load(f)
with open(ej_p) as f: e = json.load(f)
print("snapshot top keys:", list(s.keys()))
print("research_as_of:", s["research_as_of"], "target_date:", s["target_date"], "timezone:", s.get("timezone"))
ss = s["series_store"]
print("JGB in series_store:", [k for k in ss if "JGB" in k])
print("JGB in facts:", [f_["metric_id"] for f_ in s["facts"] if "JGB" in f_["metric_id"]])
txt = json.dumps(s, ensure_ascii=False)
import re
print("JGB mentions (unique contexts):")
for m in sorted(set(re.findall(r'"[A-Za-z_]*JGB[A-Za-z0-9_]*"', txt))): print("  ", m, txt.count(m))
# where does JGB10Y appear
for k in s.keys():
    t = json.dumps(s[k], ensure_ascii=False)
    if "JGB" in t: print("  appears under top key:", k)
# policy series
for m in ("DFEDTARU","DFEDTARL","ECB_DFR","ECB_MRO","UST10Y","JP_POLICY_RATE"):
    if m in ss:
        d = ss[m]["dates"]; v = ss[m]["values"]
        chg = [(d[i], v[i-1], v[i]) for i in range(1, len(d)) if v[i] is not None and v[i-1] is not None and v[i] != v[i-1]]
        print(m, "n=", len(d), "first", d[0], "last", d[-1], "lastval", v[-1], "changes(last6):", chg[-6:])
    else:
        print(m, "NOT in series_store")
# evidence index
print("evidence_index type:", type(e).__name__, "len", len(e) if hasattr(e, "__len__") else None)
rows = e if isinstance(e, list) else (e.get("rows") or e.get("entries") or e.get("facts") or [])
print("row sample:", json.dumps(rows[0], ensure_ascii=False)[:500] if rows else None)
# run-level info
run = p.get("run", {})
print("run keys:", list(run.keys()))
for k in ("evidence_gate","blocked_class","blocked","delivery_gate","gate","status"):
    if k in run: print(" run.", k, "=", json.dumps(run[k], ensure_ascii=False)[:800])
rp = p["research_plan"]
print("plan keys:", list(rp.keys()))
for k in ("cutoff","map_question","policy_event_clusters","policy_doc_facts","dimension_gaps","ex_post_offsets"):
    print(" plan.", k, "=", json.dumps(rp.get(k), ensure_ascii=False)[:1500])
