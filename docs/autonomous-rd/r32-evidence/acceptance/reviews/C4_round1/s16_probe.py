#!/usr/bin/python3 -I
# s16: 三处待核陈述的只读面定位: ①「历史长度不足 36 个月」; ②「干净安装后的降级面(未接入历史补全流程)」; ③冻结输入 sha 前缀。只读, 仅打印。
import sys, os, json, re, hashlib
rep_p, env_p, snap_p, cal_p, reg_p, aj_p, mapmd_p = sys.argv[1:8]
rep = json.load(open(rep_p, encoding="utf-8")); env = json.load(open(env_p, encoding="utf-8"))
def leaves(o, p="$"):
    if isinstance(o, dict):
        for k, v in o.items(): yield from leaves(v, p + "." + k)
    elif isinstance(o, list):
        for i, v in enumerate(o): yield from leaves(v, "%s[%d]" % (p, i))
    else: yield p, o
def sha16(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]
print("##### ③ 冻结输入 sha256 前16位")
fi = env.get("frozen_inputs", {})
rel = {"config/release_calendar.json": cal_p, "config/metric_registry.json": reg_p, "data/daily/research_snapshot_20261123.json": snap_p}
for k, v in fi.items(): print(k, "信封=%s 实测=%s %s" % (v, sha16(rel[k]), "一致" if sha16(rel[k]) == v else "不一致"))
print("\n##### ① 类比面中的 36 / dropped 特征原因")
st = rep.get("steps", [])
for i, s in enumerate(st):
    nm = s.get("step") or s.get("name") or s.get("id")
    blob = json.dumps(s, ensure_ascii=False)
    if ("analog" in blob.lower() and "1871" in blob):
        print("step[%d] %s keys=%s" % (i, nm, list(s.keys())))
        for p, v in leaves(s):
            if isinstance(v, (int, float)) and not isinstance(v, bool) and v == 36: print("  36 @", p)
            if isinstance(v, str) and ("36" in v or "min_hist" in v.lower() or "历史长度" in v or "insufficient" in v.lower() or "history" in v.lower()):
                print("  str @", p[:70], "=>", v[:260])
        for p, v in leaves(s):
            if "drop" in p.lower() or "missing" in p.lower() or "absent" in p.lower():
                print("  face @", p[:70], "=>", json.dumps(v, ensure_ascii=False)[:1500])
print("\n##### ② 补全/backfill/干净/降级 字样(report.json 与信封)")
for name, obj in (("report.json", rep), ("envelope", env)):
    for kw in ("补全", "backfill", "干净", "clean_install", "historical_backfill"):
        n = 0
        for p, v in leaves(obj):
            if isinstance(v, str) and kw in v:
                n += 1
                i = v.find(kw)
                if n <= 3: print("[%s] %s @ %s => …%s…" % (name, kw, p[:60], v[max(0, i - 60):i + 70]))
        print("[%s] %s 命中 %d 处" % (name, kw, n))
print("\nrun 段键:", list(rep.get("run", {}).keys()))
print("run.degradation_policy:", json.dumps(rep.get("run", {}).get("degradation_policy"), ensure_ascii=False)[:700])
for k in rep.get("run", {}):
    v = rep["run"][k]
    if isinstance(v, (str, int, float, bool)) or v is None: print("  run.%s = %r" % (k, v if not isinstance(v, str) else v[:120]))
print("\nMAP_REPORT 含『降级』次数:", open(mapmd_p, encoding="utf-8").read().count("降级"), " 含『补全』:", open(mapmd_p, encoding="utf-8").read().count("补全"))
