#!/usr/bin/python3 -I
# 席位自写：report.json 内嵌 agent_judgment 与受审 agent_judgment.json 的逐叶差异(只读)
import json, sys, re
jp, rp = sys.argv[1], sys.argv[2]
J = json.load(open(jp, encoding="utf-8"))
R = json.load(open(rp, encoding="utf-8"))
EJ = R["agent_judgment"]
TOPS = ("agent_declaration", "l3", "l4", "reader_map", "quality_gate_notes")
def leaves(o, p, out):
    if isinstance(o, dict):
        for k, v in o.items():
            leaves(v, (p + "." if p else "") + str(k), out)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            leaves(v, "%s[%d]" % (p, i), out)
    else:
        out[p] = o
def tr(v):
    s = json.dumps(v, ensure_ascii=False)
    return s if len(s) <= 150 else s[:150] + "…"
NUM = re.compile(r"\d+(?:\.\d+)?")
A, B = {}, {}
for top in TOPS:
    leaves(J.get(top), top, A)
    leaves(EJ.get(top), top, B)
ka, kb = set(A), set(B)
only_a = sorted(ka - kb); only_b = sorted(kb - ka)
diff = sorted(k for k in ka & kb if A[k] != B[k])
print("TOTAL file_leaves", len(ka), "emb_leaves", len(kb), "only_file", len(only_a), "only_emb", len(only_b), "value_diff", len(diff))
for top in TOPS:
    print("TOP", top, "file", sum(1 for k in ka if k.startswith(top)), "emb", sum(1 for k in kb if k.startswith(top)),
          "only_file", sum(1 for k in only_a if k.startswith(top)), "only_emb", sum(1 for k in only_b if k.startswith(top)),
          "value_diff", sum(1 for k in diff if k.startswith(top)))
nd = []
for k in diff:
    a, b = A[k], B[k]
    if isinstance(a, bool) or isinstance(b, bool):
        if a != b: nd.append((k, a, b))
    elif isinstance(a, (int, float)) and isinstance(b, (int, float)):
        nd.append((k, a, b))
    elif isinstance(a, str) and isinstance(b, str):
        na, nb = sorted(NUM.findall(a)), sorted(NUM.findall(b))
        if na != nb:
            nd.append((k, "NUMS_FILE=" + ",".join(na), "NUMS_EMB=" + ",".join(nb)))
print("NUMERIC_OR_DATE_DIFF_COMMON", len(nd))
for row in nd[:80]:
    print("   ND", row[0], "|", str(row[1])[:200], "|", str(row[2])[:200])
print("ONLY_FILE", len(only_a))
for k in only_a[:120]:
    print("   A", k, "=", tr(A[k]))
print("ONLY_EMB", len(only_b))
for k in only_b[:120]:
    print("   B", k, "=", tr(B[k]))
# numbers present only on one side (incl. only-file / only-emb leaves)
fa = {}; fb = {}
for k in ka: fa[k] = sorted(NUM.findall(json.dumps(A[k], ensure_ascii=False))) if isinstance(A[k], str) else ([str(A[k])] if isinstance(A[k], (int, float)) and not isinstance(A[k], bool) else [])
for k in kb: fb[k] = sorted(NUM.findall(json.dumps(B[k], ensure_ascii=False))) if isinstance(B[k], str) else ([str(B[k])] if isinstance(B[k], (int, float)) and not isinstance(B[k], bool) else [])
print("SAMPLE_VALUE_DIFF")
for k in diff[:40]:
    print("   D", k)
    print("      FILE:", tr(A[k]))
    print("      EMB :", tr(B[k]))
