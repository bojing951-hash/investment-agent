#!/usr/bin/env python3
"""Probe top-level structure of calendar / registry / report.json / agent_judgment.json (read-only).

usage: python3 -I probe6.py <release_calendar.json> <metric_registry.json> <report.json> <agent_judgment.json> <out.txt>
"""
import json
import sys

cal_p, reg_p, rep_p, aj_p, out_p = sys.argv[1:6]
out = open(out_p, "w", encoding="utf-8")


def w(s=""):
    out.write(s + "\n")


def pj(obj, indent=1, limit=3000):
    w(json.dumps(obj, ensure_ascii=False, indent=indent)[:limit])


cal = json.load(open(cal_p, encoding="utf-8"))
w("=== calendar top keys ===")
w(str(list(cal.keys())))
for k in cal:
    v = cal[k]
    w(f"{k}: type={type(v).__name__} len={len(v) if hasattr(v, '__len__') else '-'}")
w("entries n=%d" % len(cal.get("entries", [])))
ekeys = {}
for e in cal.get("entries", []):
    for k in e:
        ekeys[k] = ekeys.get(k, 0) + 1
w("entry keys: " + str(ekeys))
w("batches n=%d" % len(cal.get("batches", [])))

reg = json.load(open(reg_p, encoding="utf-8"))
w("\n=== registry top keys ===")
w(str(list(reg.keys())[:30]))
mets = reg.get("metrics") or reg.get("series") or {}
w("metrics type=%s len=%d" % (type(mets).__name__, len(mets)))
sample = mets[0] if isinstance(mets, list) else list(mets.items())[0]
pj(sample, 1, 2500)
ids = [m.get("id") or m.get("series_id") for m in mets] if isinstance(mets, list) else list(mets.keys())
w("ids: " + " ".join(str(i) for i in ids))
for want in ("JP_POLICY_TARGET", "JP_POLICY_RATE", "CN_POLICY_OVERNIGHT", "CN_OMO_7D"):
    hit = [m for m in (mets if isinstance(mets, list) else mets.values())
           if (m.get("id") or m.get("series_id")) == want] if isinstance(mets, list) else []
    if isinstance(mets, dict) and want in mets:
        hit = [mets[want]]
    w(f"--- registry {want}: {'FOUND' if hit else 'ABSENT'}")
    if hit:
        pj(hit[0], 1, 3000)

rep = json.load(open(rep_p, encoding="utf-8"))
w("\n=== report.json top keys ===")
w(str(list(rep.keys())))
for k in rep:
    v = rep[k]
    if isinstance(v, (dict, list)):
        w(f"{k}: {type(v).__name__} len={len(v)}")
    else:
        w(f"{k}: {str(v)[:200]}")
w("gate_a: " + json.dumps(rep.get("gate_a"), ensure_ascii=False)[:2500])
w("quality_flags: " + json.dumps(rep.get("quality_flags"), ensure_ascii=False)[:2500])
w("noncore_missing: " + json.dumps(rep.get("noncore_missing"), ensure_ascii=False)[:1500])
steps = rep.get("steps") or []
w("steps n=%d" % len(steps))
st0 = steps[0]
w("step keys: " + str(list(st0.keys())))
env = st0.get("envelope") or {}
w("envelope keys: " + str(list(env.keys())))
w("gate_a non-null steps: " + str([ (st.get("name"), (st.get("envelope") or {}).get("gate_a") is not None, (st.get("envelope") or {}).get("status")) for st in steps]))

aj = json.load(open(aj_p, encoding="utf-8"))
w("\n=== agent_judgment keys ===")
w(str(list(aj.keys())))
for k in aj:
    v = aj[k]
    if isinstance(v, dict):
        w(f"{k}: dict keys={list(v.keys())[:20]}")
    elif isinstance(v, list):
        w(f"{k}: list len={len(v)}")
    else:
        w(f"{k}: {str(v)[:200]}")
rm = aj.get("reader_map") or {}
for k in rm:
    v = rm[k]
    if isinstance(v, dict):
        w(f"reader_map.{k}: dict keys={list(v.keys())[:20]}")
    elif isinstance(v, list):
        w(f"reader_map.{k}: list len={len(v)}")
    else:
        w(f"reader_map.{k}: {str(v)[:200]}")
out.close()
print("written", out_p)
