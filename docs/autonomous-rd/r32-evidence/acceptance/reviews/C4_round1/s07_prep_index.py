#!/usr/bin/python3 -I
# s07a: 受审版本核对后的索引生成 —— (B) S8 信封摘要 (C) 修正 X16 并重跑合并 (D) 全点索引 (E) 受审稿原句定位。只读; 产出只写本席目录。
import sys, os, json, subprocess
snap_p, rep_p, aj_p, mapmd_p, outdir, s06 = sys.argv[1:7]
rep = json.load(open(rep_p, encoding="utf-8"))
aj = json.load(open(aj_p, encoding="utf-8"))
# B
_s8 = [s for s in rep["steps"] if s.get("step") == "S8_grounded_qa"][0]
env = _s8.get("envelope") or {}
print("B. S8 step: executed=%s ok=%s | envelope keys=%s" % (_s8.get("executed"), _s8.get("ok"), sorted(env.keys())))
print("   envelope scalars:", {k: v for k, v in env.items() if not isinstance(v, (dict, list))})
for k, v in env.items():
    if isinstance(v, dict):
        print("   envelope.%s scalars:" % k, {a: b for a, b in v.items() if not isinstance(b, (dict, list))})
# C
p = os.path.join(outdir, "s06_merge_and_extra.py")
L = open(p, encoding="utf-8").read().split("\n")
idx = [i for i, l in enumerate(L) if l.startswith('P.addb("X16"')]
assert len(idx) == 1, idx
Q = chr(34)
new = [
    '_x16 = [s.get("step") for s in rep["steps"] if s.get("ok") is not True]',
    '_s8 = [s for s in rep["steps"] if s.get("step") == "S8_grounded_qa"][0]',
    '_s8e = _s8.get("envelope") or {}',
    'P.addb("X16", "report.json run_ok / steps[*].ok / steps[S8_grounded_qa].envelope", "run_ok=true 且 66 步 step 级 ok 全为 true(62 已执行+4 未执行); S8_grounded_qa 信封含 unmapped(地图问句不属其支持的问题类型, 非失败步骤)", rep.get("run_ok") is True and len(_x16) == 0 and len(rep["steps"]) == 66 and "unmapped" in json.dumps(_s8e, ensure_ascii=False), "ok!=true 步骤=%s; S8 信封状态=%s" % (_x16, _s8e.get("status")))',
]
L[idx[0]:idx[0] + 1] = new
open(p, "w", encoding="utf-8").write("\n".join(L))
print("C. X16 restated")
A = sys.argv
r = subprocess.run(["/usr/bin/python3", "-I", s06, A[1], A[2], A[7], A[8], A[3], A[5], A[4], A[9], A[10], A[11]], capture_output=True, text=True)
print(r.stdout.strip()[-900:]); print(r.stderr.strip()[-600:])
# D
pts = json.load(open(os.path.join(outdir, "pts_all.json"), encoding="utf-8"))
with open(os.path.join(outdir, "out_points_index.txt"), "w", encoding="utf-8") as f:
    for r in pts:
        f.write("%s|%s|%s|%s|%s|%s\n" % (r["id"], "Y" if r["ok"] else "N", str(r.get("face", ""))[-46:], str(r.get("key", ""))[:96], str(r.get("calc_str", ""))[:30], json.dumps(r.get("report"), ensure_ascii=False)[:30]))
print("D. index lines", len(pts), "-> out_points_index.txt")
# E
kws = ["11-09 起", "同窗 USDJPY", "盈亏平衡降幅", "0.3767", "互补而不穷尽", "实测锚", "巧合", "近一月", "并项", "尚无传导", "同一周内", "事后回顾", "十一", "十五"]
hits = []
def walk(o, path):
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, path + "." + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, path + "[%d]" % i)
    elif isinstance(o, str):
        ks = [k for k in kws if k in o]
        if ks:
            hits.append((path, ks, o))
walk(aj, "$")
with open(os.path.join(outdir, "out_quotes.txt"), "w", encoding="utf-8") as f:
    seen = set()
    for path, ks, s in hits:
        if s in seen:
            continue
        seen.add(s)
        f.write("%s  <%s>\n%s\n\n" % (path, "/".join(ks), s))
print("E. quote hits", len(seen), "-> out_quotes.txt")
