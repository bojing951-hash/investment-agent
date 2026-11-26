# -*- coding: utf-8 -*-
#!/usr/bin/python3 -I
# s18: 一次性落盘终稿(此前须不存在), 逐字节复制草稿, 校验 JSON 结构与计数, 打印 sha256。写出后不得改写。
# 用法: /usr/bin/python3 -I s18_finalize.py OUTDIR DRAFT_DATA AJ
import sys, os, json, hashlib
outdir, data_p, aj_p = sys.argv[1:4]
dd = json.load(open(data_p, encoding="utf-8"))
pairs = [("_draft_PROSE-round1.md", "PROSE-round1.md"), ("_draft_VERDICT-round1.json", "VERDICT-round1.json")]
for a, b in pairs:
    dst = os.path.join(outdir, b)
    assert not os.path.exists(dst), "终稿已存在, 不得改写: " + dst
v = json.loads(open(os.path.join(outdir, pairs[1][0]), "rb").read().decode("utf-8"))
need = ["seat", "reviewer", "verdict", "overall", "notes", "items", "must_fix", "counterexamples_sought",
        "recompute_points", "recompute_mismatches", "mismatch_details", "audited_at"]
assert list(v.keys()) == need, list(v.keys())
assert v["verdict"] in ("UPHELD", "REVISE") and v["overall"] == v["verdict"]
assert v["recompute_points"] == dd["n_cmp"] and v["recompute_mismatches"] == dd["n_mis"]
assert len(v["mismatch_details"]) == dd["n_mis"] == len(dd["mis_ids"])
assert all(x["id"] == dd["mis_ids"][i] for i, x in enumerate(v["mismatch_details"]))
assert all(set(x) == {"severity", "where", "note", "original", "fix"} for x in v["items"])
n_maj = sum(1 for x in v["items"] if x["severity"] == "MAJOR")
assert (n_maj == 0) == (v["verdict"] == "UPHELD") and len(v["must_fix"]) == n_maj
assert all(x["original"] and x["fix"] for x in v["items"])
assert all(isinstance(x, str) and x for x in v["counterexamples_sought"]) and len(v["counterexamples_sought"]) >= 8
assert isinstance(v["notes"], str) and len(v["notes"]) > 200 and v["audited_at"] == "2026-11-24"
assert hashlib.sha256(open(aj_p, "rb").read()).hexdigest() == dd["aj_sha"], "受审稿哈希与复算时不一致"
ajraw = open(aj_p, encoding="utf-8").read()
assert all(x["original"] in ajraw for x in v["items"]), "原句不在受审稿中"
prose = open(os.path.join(outdir, pairs[0][0]), "rb").read().decode("utf-8")
assert "@@" not in prose and "[[" not in prose
assert prose.count("\n| ") >= dd["n_cmp"] + dd["n_aux"] + 20
bodies = [(b, open(os.path.join(outdir, a), "rb").read()) for a, b in pairs]
for b, body in bodies:
    with open(os.path.join(outdir, b), "xb") as f:
        f.write(body)
    print("%s  %d bytes  sha256 %s" % (b, len(body), hashlib.sha256(body).hexdigest()))
print("verdict=%s points=%d mismatches=%d MAJOR=%d MINOR=%d NIT=%d attacks=%d" % (
    v["verdict"], v["recompute_points"], v["recompute_mismatches"], n_maj,
    sum(1 for x in v["items"] if x["severity"] == "MINOR"), sum(1 for x in v["items"] if x["severity"] == "NIT"),
    len(v["counterexamples_sought"])))
