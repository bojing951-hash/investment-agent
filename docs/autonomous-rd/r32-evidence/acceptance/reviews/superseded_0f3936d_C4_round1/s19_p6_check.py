#!/usr/bin/python3 -I
# s19_p6_check.py — 第 8 节各条事实的逐项复核（只读）
import json, re, sys
rep_p, map_p, out_p = sys.argv[1:4]
rep = json.load(open(rep_p, encoding="utf-8"))
lines = open(map_p, encoding="utf-8").read().split("\n")
out = []
def w(s=""): out.append(str(s))
for i, l in enumerate(lines, 1):
    if "⚠过期" in l:
        w("L%d: %s" % (i, l[:260]))
w("MAP 含「12个月前」=%d; 含「−12月」=%d; 含「-12月」=%d; 含「－12月」=%d; 含「研究截止−12个月」=%d" % (
    sum("12个月前" in l for l in lines), sum("−12月" in l for l in lines), sum("-12月" in l for l in lines),
    sum("－12月" in l for l in lines), sum("研究截止−12个月" in l for l in lines)))
w("MAP 含「支持主解释」=%d; 「尚不能区分」=%d; 「两情景方向互补」=%d; 「经独立语义审查」=%d; 「独立席位待裁」=%d" % (
    sum("支持主解释" in l for l in lines), sum("尚不能区分" in l for l in lines), sum("两情景方向互补" in l for l in lines),
    sum("经独立语义审查" in l for l in lines), sum("独立席位待裁" in l for l in lines)))
w("MAP 行数=%d" % len([l for l in lines if l.strip() != ""]))
steps = rep.get("steps") or []
w("steps n=%d" % len(steps))
bad = []
for st in steps:
    if not isinstance(st, dict): continue
    so = st.get("semantic_ok")
    if st.get("executed") and so is not True:
        bad.append((st.get("step"), st.get("executed"), st.get("ok"), so, st.get("exit_code"), st.get("note")))
w("executed=True 且 semantic_ok≠True 的步骤: %s" % bad)
w("executed=False 的步骤: %s" % [(st.get("step"), str(st.get("skipped_reason"))[:60]) for st in steps if isinstance(st, dict) and st.get("executed") is False])
pre = [st.get("step") for st in steps if isinstance(st, dict) and re.match(r"S[3-6]_", str(st.get("step")))]
w("S3–S6 步数=%d, 其中 semantic_ok=True: %d" % (len(pre), sum(1 for st in steps if isinstance(st, dict) and st.get("step") in pre and st.get("semantic_ok") is True)))
cv = rep["agent_judgment"]["contract_verification"]
fam = {}
for v in cv["verdicts"]:
    fam.setdefault(v["family"], []).append(v["status"])
w("契约 family 计数: %s" % {k: (len(v), {s: v.count(s) for s in set(v)}) for k, v in fam.items()})
w("six_checks 中 C4 opposing: %s" % [c for c in cv["six_checks"] if c.get("item") == "C4-EVIDENCE-BOUNDARY" and c.get("check") == "opposing"])
open(out_p, "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out))
