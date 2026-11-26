# -*- coding: utf-8 -*-
"""只读结构探查(2): 序列条目结构 / research_plan 各面 / steps / contract_verification / 日历 / 注册表。"""
import json, sys, os

RUN = sys.argv[1]; SNAP = sys.argv[2]; OUT = sys.argv[3]
rep = json.load(open(os.path.join(RUN, "report.json"), encoding="utf-8"))
sn = json.load(open(SNAP, encoding="utf-8"))
cal = json.load(open(os.path.join(RUN, "root_overlay/config/release_calendar.json"), encoding="utf-8"))
reg = json.load(open(os.path.join(RUN, "root_overlay/config/metric_registry.json"), encoding="utf-8"))

def short(v, n=300):
    s = json.dumps(v, ensure_ascii=False)
    return s if len(s) <= n else s[:n] + "...(len=%d)" % len(s)

out = open(OUT, "w", encoding="utf-8")
def P(*a):
    s = " ".join(str(x) for x in a)
    out.write(s + "\n")

ss = sn["series_store"]
P("=== series entry keys (CPI) ===")
P({k: (short(v, 200) if k not in ("dates", "values") else type(v).__name__ + "[%d]" % len(v)) for k, v in ss["CPI"].items()})
P("=== series entry keys (JP_POLICY_RATE) ===")
P({k: (short(v, 200) if k not in ("dates", "values") else type(v).__name__ + "[%d]" % len(v)) for k, v in ss["JP_POLICY_RATE"].items()})
P("=== per-series: n, first, last, last_value ===")
for sid in sorted(ss):
    s = ss[sid]; d = s.get("dates"); v = s.get("values")
    if not d:
        P(sid, "NO DATES", short(s, 200)); continue
    # last non-null
    last = None
    for i in range(len(d) - 1, -1, -1):
        if v is not None and i < len(v) and v[i] is not None:
            last = (d[i], v[i]); break
    P("%-18s n=%5d first=%s last_nonnull=%s meta_keys=%s" % (sid, len(d), d[0] if d else None, last, [k for k in s if k not in ("dates", "values")]))

rp = rep["research_plan"]
P("\n=== research_plan.regions/dimensions/metrics/context/point_anchors ===")
P("regions:", short(rp["regions"], 600))
P("dimensions:", short(rp["dimensions"], 600))
P("metrics:", short(rp["metrics"], 600))
P("context_metrics:", short(rp["context_metrics"], 600))
P("point_anchors:", json.dumps(rp["point_anchors"], ensure_ascii=False))
P("dimension_gaps:", json.dumps(rp["dimension_gaps"], ensure_ascii=False))
P("as_of_declared:", json.dumps(rp["as_of_declared"], ensure_ascii=False))
P("policy_doc_facts:", json.dumps(rp["policy_doc_facts"], ensure_ascii=False))
P("\n=== point_values ===")
P(json.dumps(rp["point_values"], ensure_ascii=False, indent=0))
P("\n=== turning_candidates ===")
P(json.dumps(rp["turning_candidates"], ensure_ascii=False, indent=0))
P("\n=== us_rates_trio ===")
P(json.dumps(rp["us_rates_trio"], ensure_ascii=False, indent=0))
P("\n=== asset_moves ===")
P(json.dumps(rp["asset_moves"], ensure_ascii=False, indent=0))
P("\n=== policy_event_clusters ===")
P(json.dumps(rp["policy_event_clusters"], ensure_ascii=False, indent=0))

P("\n=== steps (name, ok, envelope keys) ===")
for st in rep["steps"]:
    env = st.get("envelope")
    P(st.get("step"), "executed=%s ok=%s" % (st.get("executed"), st.get("ok")),
      "env_keys=%s" % (sorted(env.keys()) if isinstance(env, dict) else type(env).__name__),
      "| det_face_keys=%s" % (sorted(st["deterministic_face"].keys()) if isinstance(st.get("deterministic_face"), dict) else ""))

P("\n=== agent_judgment.validation / contract_verification ===")
aj = rep["agent_judgment"]
P("validation:", json.dumps(aj.get("validation"), ensure_ascii=False)[:1500])
P("attach_history:", json.dumps(aj.get("attach_history"), ensure_ascii=False))
P("reader_map_faces:", json.dumps(aj.get("reader_map_faces"), ensure_ascii=False)[:1500])
cv = aj.get("contract_verification", {})
for k, v in cv.items():
    P("cv.%s: %s" % (k, short(v, 400)))
ver = cv.get("verdicts") or cv.get("items") or []
P("verdicts type:", type(ver).__name__, len(ver) if hasattr(ver, "__len__") else "")
P(json.dumps(ver, ensure_ascii=False, indent=0)[:12000])

P("\n=== notes ===")
for n in rep.get("notes", []):
    P("-", n)
P("\n=== L1 rows sample ===")
rows = rep["layers"]["L1_事实层"].get("rows", [])
P("L1 keys:", sorted(rep["layers"]["L1_事实层"].keys()), "rows n=", len(rows))
P(json.dumps(rows[:3], ensure_ascii=False))

P("\n=== release_calendar top ===")
P("keys:", list(cal.keys()))
for k, v in cal.items():
    if isinstance(v, list):
        P("%s: list(%d)" % (k, len(v)))
    elif isinstance(v, dict):
        P("%s: dict(%d) keys=%s" % (k, len(v), short(list(v.keys()), 500)))
    else:
        P("%s: %s" % (k, short(v)))

P("\n=== registry top ===")
P("keys:", list(reg.keys()))
for k, v in reg.items():
    if isinstance(v, list):
        P("%s: list(%d) sample=%s" % (k, len(v), short(v[:1], 500)))
    elif isinstance(v, dict):
        P("%s: dict(%d) keys=%s" % (k, len(v), short(list(v.keys())[:60], 900)))
    else:
        P("%s: %s" % (k, short(v)))

P("\n=== gate_a ===")
P(json.dumps(sn["gate_a"], ensure_ascii=False, indent=0)[:6000])
P("\n=== quality ===")
P(json.dumps(sn["quality"], ensure_ascii=False, indent=0)[:3000])
out.close()
print("written", OUT)
