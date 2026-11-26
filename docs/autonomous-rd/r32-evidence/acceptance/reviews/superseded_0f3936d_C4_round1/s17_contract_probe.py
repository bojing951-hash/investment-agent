#!/usr/bin/python3 -I
# s17_contract_probe.py — 契约验证面与计划注记的事实核对（只读）
# 用法: /usr/bin/python3 -I s17_contract_probe.py <snapshot> <report.json> <agent_judgment.json> <out>
import json, re, sys

snap_p, rep_p, aj_p, out_p = sys.argv[1:5]
snap = json.load(open(snap_p, encoding="utf-8"))
rep = json.load(open(rep_p, encoding="utf-8"))
aj = json.load(open(aj_p, encoding="utf-8"))
ss = snap.get("series_store", {})
L = []
def w(s=""):
    L.append(str(s))

cv = (rep.get("agent_judgment") or {}).get("contract_verification") or {}
w("=== E5 contract_verification keys=%s" % list(cv.keys()))
for k, v in cv.items():
    if not isinstance(v, list):
        w("  %s = %s" % (k, json.dumps(v, ensure_ascii=False)[:500]))
for k, v in cv.items():
    if isinstance(v, list):
        w("  %s n=%d" % (k, len(v)))
        for row in v:
            if isinstance(row, dict):
                w("    " + json.dumps(row, ensure_ascii=False)[:620])
            else:
                w("    " + str(row)[:620])

w("")
w("=== E5b L3 陈述: 阿拉伯数字 token 与汉字数字百分比计数")
CN_NUM = "零〇一二两三四五六七八九十百千万点"
for c in aj.get("l3", {}).get("contradictions", []):
    st = str(c.get("statement") or "")
    ar = re.findall(r"\d+(?:\.\d+)?", st)
    zh = re.findall(r"百分之[零〇一二两三四五六七八九十百千万点]+", st)
    w("  %s: 阿拉伯数字 %d 个 %s; 「百分之X」 %d 个 %s" % (c.get("id"), len(ar), ar, len(zh), zh))

w("")
w("=== E8b research_plan 键与注记")
rp = rep.get("research_plan") or {}
w("  research_plan keys=%s" % list(rp.keys()))
for k, v in rp.items():
    if k in ("point_values",):
        continue
    s = json.dumps(v, ensure_ascii=False)
    if len(s) < 1500:
        w("  %s = %s" % (k, s))
    else:
        w("  %s (len %d) = %s…" % (k, len(s), s[:700]))

w("")
w("=== E8c gate_a 全文")
w("  " + json.dumps(snap.get("gate_a"), ensure_ascii=False)[:3500])

w("")
w("=== E8d noncore_missing 中在 series_store 有观测的指标")
for m in snap.get("gate_a", {}).get("noncore_missing", []):
    v = ss.get(m)
    w("  %s in_store=%s n=%s last=%s" % (m, v is not None, (len(v["dates"]) if v else None), ((v["dates"][-1], v["values"][-1]) if v else None)))

w("")
w("=== E8e 锚格标签: 月末标签的指标")
pv = rp.get("point_values") or {}
first = True
for c in pv.get("cells") or []:
    if first:
        w("  cell 键=%s" % list(c.keys()))
        first = False
    w("  %s keys=%s" % (c.get("metric_id"), [k for k in c.keys()]))
    for k, v in c.items():
        if isinstance(v, (list, dict)) and k not in ("anchors",):
            w("     %s = %s" % (k, json.dumps(v, ensure_ascii=False)[:900]))

open(out_p, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("written", out_p, "lines", len(L))
