#!/usr/bin/python3 -I
# s16_engine_obs.py — 引擎面附带观察的事实核对（只读）
# 用法: /usr/bin/python3 -I s16_engine_obs.py <snapshot> <report.json> <MAP> <FULL> <report.md> <out>
import json, re, sys

snap_p, rep_p, map_p, full_p, md_p, out_p = sys.argv[1:7]
snap = json.load(open(snap_p, encoding="utf-8"))
rep = json.load(open(rep_p, encoding="utf-8"))
MAP = open(map_p, encoding="utf-8").read()
FULL = open(full_p, encoding="utf-8").read()
MD = open(md_p, encoding="utf-8").read()
L = []
def w(s=""):
    L.append(str(s))

def find_key(obj, needle, path="$", out=None, depth=0):
    if out is None:
        out = []
    if depth > 12:
        return out
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = path + "." + str(k)
            if needle in str(k):
                out.append((p, type(v).__name__, (len(v) if hasattr(v, "__len__") else v)))
            find_key(v, needle, p, out, depth + 1)
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:400]):
            find_key(v, needle, path + "[%d]" % i, out, depth + 1)
    return out

w("=== E5 契约验证结构定位")
for needle in ("contract", "judgment"):
    for row in find_key(rep, needle)[:60]:
        w("  %s  type=%s len=%s" % row)

w("")
w("=== E9 steps 信封: 各步状态")
steps = None
for path in ("steps", "run_steps", "pipeline_steps"):
    if isinstance(rep.get(path), list):
        steps = rep[path]; w("  steps 位于 report.json.$.%s n=%d" % (path, len(steps))); break
if steps is None:
    found = find_key(rep, "step")
    w("  顶层无 steps; 含 step 的键: %s" % [r[0] for r in found][:30])
else:
    for st in steps:
        if not isinstance(st, dict):
            continue
        name = st.get("name") or st.get("step") or st.get("id")
        if name in ("S5_compare", "S8_grounded_qa", "S11_archive", "S10_reader_map", "S9_l3_l4", "S6_analog"):
            keys = {k: st.get(k) for k in ("executed", "ok", "semantic_ok", "exit", "status", "note") if k in st}
            w("  %s -> %s" % (name, json.dumps(keys, ensure_ascii=False)[:700]))

w("")
w("=== E8 gate_a / 缺席格")
ga = None
for k in ("gate_a", "gates", "quality"):
    if isinstance(snap.get(k), dict):
        w("  snapshot.%s keys=%s" % (k, list(snap[k].keys())[:30]))
ga = snap.get("gate_a") if isinstance(snap.get("gate_a"), dict) else None
if ga:
    for k in ("noncore_missing", "core_missing", "missing", "noncore_missing_ids"):
        if k in ga:
            w("  gate_a.%s = %s" % (k, json.dumps(ga[k], ensure_ascii=False)[:900]))
ss = snap.get("series_store", {})
w("  series_store n=%d" % len(ss))
pv = ((rep.get("research_plan") or {}).get("point_values") or {})
cells = pv.get("cells")
if isinstance(cells, list):
    absent = [(c.get("metric_id"), c.get("region"), c.get("dimension")) for c in cells if (c.get("anchors") is None or len(c.get("anchors") or []) == 0)]
    w("  point_values.cells 缺席格 n=%d -> %s" % (len(absent), absent))
    w("  cells 指标数=%d" % len(set(c.get("metric_id") for c in cells)))
for k in pv:
    if k != "cells":
        w("  point_values.%s = %s" % (k, json.dumps(pv[k], ensure_ascii=False)[:1200]))

w("")
w("=== E10 CN_NEW_LOANS 负值")
v = ss.get("CN_NEW_LOANS")
if v:
    d, x = v["dates"], v["values"]
    neg = [(a, b) for a, b in zip(d, x) if isinstance(b, (int, float)) and b < 0]
    w("  n=%d 首=%s 末=%s 负值个数=%d" % (len(d), (d[0], x[0]), (d[-1], x[-1]), len(neg)))
    w("  末 12 点: %s" % [(a, b) for a, b in zip(d, x)][-12:])
    used = 0
    aj_p = None
w("  判断档引用计数见下")

w("")
w("=== E4 渲染计数")
try:
    aj = json.load(open(sys.argv[7], encoding="utf-8"))
except Exception as e:
    aj = None
    w("  未提供判断档路径或读取失败: %s" % e)
if aj:
    rm = aj.get("reader_map", {})
    for i, t in enumerate(rm.get("turnings") or []):
        nar = str(t.get("narrative") or "")
        frag = nar[:18]
        w("  turnings[%d].narrative MAP=%s FULL=%s report.md=%s | %s" % (i, frag in MAP, frag in FULL, frag in MD, frag))
    for i, n in enumerate(aj.get("quality_gate_notes") or []):
        frag = str(n)[:18]
        w("  note[%d] MAP=%s FULL=%s report.md=%s | %s" % (i, frag in MAP, frag in FULL, frag in MD, frag))
    tr = (rm.get("transmission") or [{}])[0]
    for i, lk in enumerate(tr.get("links") or []):
        vn = str(lk.get("verdict_note") or "")
        w("  link[%d].verdict_note MAP=%s FULL=%s report.md=%s len=%d | %s" % (i, vn[:18] in MAP, vn[:18] in FULL, vn[:18] in MD, len(vn), vn[:160]))
        fv = str(lk.get("face_off_verdict") or "")
        w("  link[%d].face_off_verdict MAP计数=%d FULL计数=%d | %s" % (i, MAP.count(fv), FULL.count(fv), fv))
    w("  history_zero_case_note MAP=%s" % (str(rm.get("history_zero_case_note"))[:18] in MAP))
    w("  MAP 含「尚不能区分」次数=%d; 判断档出现=%d" % (MAP.count("尚不能区分"), json.dumps(aj, ensure_ascii=False).count("尚不能区分")))

open(out_p, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("written", out_p, "lines", len(L))
