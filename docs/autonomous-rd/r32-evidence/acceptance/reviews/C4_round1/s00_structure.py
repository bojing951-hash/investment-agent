#!/usr/bin/python3 -I
# s00: 探查 report.json / 快照 / 日历 / 注册表结构(只读)
import json, sys

def shape(o, depth=0, maxdepth=2):
    if isinstance(o, dict):
        if depth >= maxdepth:
            return "{dict %d keys}" % len(o)
        return {k: shape(v, depth + 1, maxdepth) for k, v in list(o.items())[:60]}
    if isinstance(o, list):
        if depth >= maxdepth:
            return "[list %d]" % len(o)
        return [shape(o[0], depth + 1, maxdepth)] if o else []
    return type(o).__name__

rep_p, snap_p, cal_p, reg_p, ev_p, vd_p, env_p = sys.argv[1:8]

rep = json.load(open(rep_p, encoding="utf-8"))
print("== report.json top keys ==")
for k, v in rep.items():
    if isinstance(v, dict):
        print(" ", k, "-> dict", list(v.keys())[:40])
    elif isinstance(v, list):
        print(" ", k, "-> list", len(v))
    else:
        print(" ", k, "->", repr(v)[:200])

print("\n== run ==")
run = rep.get("run", {})
for k, v in run.items():
    s = json.dumps(v, ensure_ascii=False)
    print(" ", k, ":", s[:400])

print("\n== research_plan keys ==")
rp = rep.get("research_plan", {})
for k, v in rp.items():
    s = json.dumps(v, ensure_ascii=False)
    print(" ", k, ": len(json)=", len(s), " ::", s[:300])

print("\n== layers keys ==")
print(" ", list(rep.get("layers", {}).keys()))
for k, v in rep.get("layers", {}).items():
    print("  ", k, "->", (list(v.keys()) if isinstance(v, dict) else type(v).__name__))

print("\n== steps ==")
for i, st in enumerate(rep.get("steps", [])):
    print("  [%d]" % i, st.get("step") or st.get("name"), "| keys:", list(st.keys())[:12])
    env = st.get("envelope")
    if isinstance(env, dict):
        print("       envelope keys:", list(env.keys())[:30])

snap = json.load(open(snap_p, encoding="utf-8"))
print("\n== snapshot top keys ==")
for k, v in snap.items():
    if isinstance(v, dict):
        print(" ", k, "-> dict", list(v.keys())[:30])
    elif isinstance(v, list):
        print(" ", k, "-> list", len(v))
    else:
        print(" ", k, "->", repr(v)[:200])

ss = snap.get("series_store", {})
print("\n== series_store: n=", len(ss))
for k in sorted(ss.keys()):
    v = ss[k]
    if isinstance(v, dict):
        ks = list(v.keys())
        print("  ", k, "keys:", ks[:15], "| n_dates=", len(v.get("dates", [])) if isinstance(v.get("dates"), list) else "?")
    else:
        print("  ", k, type(v).__name__)

cal = json.load(open(cal_p, encoding="utf-8"))
print("\n== release_calendar top ==")
for k, v in cal.items():
    if isinstance(v, (dict, list)):
        print(" ", k, "->", type(v).__name__, len(v))
    else:
        print(" ", k, "->", repr(v)[:200])

reg = json.load(open(reg_p, encoding="utf-8"))
print("\n== registry top ==")
for k, v in reg.items():
    if isinstance(v, (dict, list)):
        print(" ", k, "->", type(v).__name__, len(v))
    else:
        print(" ", k, "->", repr(v)[:200])

ev = json.load(open(ev_p, encoding="utf-8"))
print("\n== evidence_index ==")
print(json.dumps(ev, ensure_ascii=False)[:1500])

vd = json.load(open(vd_p, encoding="utf-8"))
print("\n== views_digest ==")
print(json.dumps(vd, ensure_ascii=False)[:500])

envj = json.load(open(env_p, encoding="utf-8"))
print("\n== AGENT_SEAT_ENVELOPE top ==")
for k, v in envj.items():
    s = json.dumps(v, ensure_ascii=False)
    print(" ", k, ": len=", len(s), "::", s[:300])
