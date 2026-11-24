# -*- coding: utf-8 -*-
"""只读结构探查: report.json / 快照 / 日历 / 注册表 的键结构(不整读大文件)。"""
import json, sys, os

RUN = sys.argv[1]
SNAP = sys.argv[2]

def short(v, n=160):
    s = json.dumps(v, ensure_ascii=False)
    return s if len(s) <= n else s[:n] + "...(len=%d)" % len(s)

def describe(obj, depth=0, maxdepth=2, prefix=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, dict):
                print("%s%s: dict(%d)" % (prefix, k, len(v)))
                if depth < maxdepth:
                    describe(v, depth + 1, maxdepth, prefix + "  ")
            elif isinstance(v, list):
                print("%s%s: list(%d) %s" % (prefix, k, len(v), short(v[:1], 120) if v else ""))
            else:
                print("%s%s: %s" % (prefix, k, short(v)))

print("=" * 20, "report.json top", "=" * 20)
rep = json.load(open(os.path.join(RUN, "report.json"), encoding="utf-8"))
describe(rep, maxdepth=1)
print()
print("=" * 20, "run", "=" * 20)
describe(rep.get("run", {}), maxdepth=2)
print()
print("=" * 20, "research_plan (keys + short)", "=" * 20)
rp = rep.get("research_plan", {})
for k, v in rp.items():
    if isinstance(v, (dict, list)):
        print("--", k, type(v).__name__, len(v))
    else:
        print("--", k, "=", short(v))
print()
print("=" * 20, "snapshot top", "=" * 20)
sn = json.load(open(SNAP, encoding="utf-8"))
for k, v in sn.items():
    if isinstance(v, dict):
        print("%s: dict(%d) keys=%s" % (k, len(v), short(list(v.keys())[:40], 600)))
    elif isinstance(v, list):
        print("%s: list(%d) %s" % (k, len(v), short(v[:3], 300)))
    else:
        print("%s: %s" % (k, short(v)))
print()
print("research_as_of =", json.dumps(sn.get("research_as_of"), ensure_ascii=False)[:600])
ss = sn.get("series_store", {})
print("series_store count:", len(ss))
print("series ids:", sorted(ss.keys()))
# sample series structure
for sid in list(sorted(ss.keys()))[:2]:
    print("SAMPLE", sid, "->", short(ss[sid], 900))
