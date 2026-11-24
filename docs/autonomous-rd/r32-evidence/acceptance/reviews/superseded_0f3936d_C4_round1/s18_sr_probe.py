#!/usr/bin/python3 -I
# s18_sr_probe.py — 只读抽取 report.json 的 semantic_review / 交付门 / 渲染位置
import json, sys
rep = json.load(open(sys.argv[1], encoding="utf-8"))
aj = json.load(open(sys.argv[2], encoding="utf-8"))
def find(obj, needle, path="$", out=None, depth=0):
    if out is None: out = []
    if depth > 6: return out
    if isinstance(obj, dict):
        for k, v in obj.items():
            if needle in str(k):
                out.append((path + "." + str(k), v))
            find(v, needle, path + "." + str(k), out, depth + 1)
    return out
for p, v in find(rep, "semantic_review"):
    print(p, "=", json.dumps(v, ensure_ascii=False)[:600])
for p, v in find(rep, "deliverab"):
    print(p, "=", json.dumps(v, ensure_ascii=False)[:600])
for p, v in find(rep, "blocked_class"):
    print(p, "=", json.dumps(v, ensure_ascii=False)[:300])
for p, v in find(rep, "degraded_ok"):
    print(p, "=", json.dumps(v, ensure_ascii=False)[:300])
ajr = aj.get("agent_judgment") if isinstance(aj.get("agent_judgment"), dict) else aj
print("AJ top keys =", list(aj.keys()))
print("agent_declaration =", json.dumps(aj.get("agent_declaration"), ensure_ascii=False)[:900])
sr = aj.get("semantic_review")
print("AJ.semantic_review =", json.dumps(sr, ensure_ascii=False)[:900])
print("AJ keys containing review/verdict =", [k for k in aj.keys() if "review" in k or "verdict" in k])
