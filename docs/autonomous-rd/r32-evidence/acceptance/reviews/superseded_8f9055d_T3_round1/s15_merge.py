#!/usr/bin/python3 -I
"""Merge recompute parts A-E into recompute_points.json + recompute_table.md and print totals.
Read-only on inputs. Args: <out_dir>
"""
import json
import os
import sys
from collections import OrderedDict

out_dir = sys.argv[1]
rows = []
for part in "ABCDE":
    p = os.path.join(out_dir, "recompute_points_%s.json" % part)
    if not os.path.exists(p):
        continue
    d = json.load(open(p, "r", encoding="utf-8"))
    for r in d["rows"]:
        r = dict(r)
        r["part"] = part
        if part == "E":
            # statement-level Chinese-numeral rows: distinct id prefix (part A already uses E001.. for category ⑤)
            r["id"] = "CN" + r["id"][1:]
        r["duplicate"] = bool(part in ("D", "E") and r["id"].endswith("X"))
        r["scope_out"] = (r.get("sev") == "SCOPE-OUT")
        rows.append(r)


def esc(x, n=110):
    s = json.dumps(x, ensure_ascii=False) if not isinstance(x, str) else x
    s = str(s).replace("|", "\\|").replace("\n", " ")
    return s if len(s) <= n else s[:n] + "…"


cat_order = OrderedDict()
for r in rows:
    cat_order.setdefault(r["cat"], []).append(r)
in_scope = [r for r in rows if not r["duplicate"] and not r["scope_out"]]
dups = [r for r in rows if r["duplicate"]]
scope_out = [r for r in rows if r["scope_out"]]
mism = [r for r in in_scope if not r["ok"]]
lines = []
lines.append("| 序 | 编号 | 类别 | 位置 | 出处键 | 直算值 | 报告值 | 一致 | 备注 |")
lines.append("|---|---|---|---|---|---|---|---|---|")
k = 0
for cat, rs in cat_order.items():
    for r in rs:
        if r["duplicate"] or r["scope_out"]:
            continue
        k += 1
        note = esc(r.get("note") or "", 90)
        lit = "" if r.get("lit") is None else ("字面命中" if r.get("lit_found") else "字面未命中")
        lines.append("| %d | %s | %s | %s | %s | %s | %s | %s | %s%s |" % (
            k, r["id"], esc(cat, 24), esc(r.get("where"), 60), esc(r.get("src"), 90), esc(r.get("computed"), 70),
            esc(r.get("reported"), 70), "是" if r["ok"] else "否", lit + (";" if lit and note else ""), note))
lines.append("")
lines.append("### 逐对复核(与上表已覆盖点重复,全中,不重复计数;%d 条)" % len(dups))
lines.append("")
lines.append("| 编号 | 指标@时点 | 直算值 | 报告值 | 字面 | 已由 |")
lines.append("|---|---|---|---|---|---|")
for r in dups:
    lines.append("| %s | %s | %s | %s | %s | %s |" % (
        r["id"], esc(r.get("src"), 70), esc(r.get("computed"), 40), esc(r.get("reported"), 40),
        "命中" if r.get("lit_found") else "未命中", esc((r.get("note") or "").replace("已由 ", "").replace(" 覆盖,不重复计数", ""), 12)))
lines.append("")
lines.append("### 范围外观察(引擎渲染/口径面,非判断偏离,不计入命中/偏离;%d 条)" % len(scope_out))
lines.append("")
lines.append("| 编号 | 类别 | 位置 | 出处键 | 直算值 | 引擎面值 | 备注 |")
lines.append("|---|---|---|---|---|---|---|")
for r in scope_out:
    lines.append("| %s | %s | %s | %s | %s | %s | %s |" % (
        r["id"], esc(r["cat"], 24), esc(r.get("where"), 60), esc(r.get("src"), 80), esc(r.get("computed"), 120),
        esc(r.get("reported"), 120), esc(r.get("note"), 200)))
table = "\n".join(lines) + "\n"
open(os.path.join(out_dir, "recompute_table.md"), "w", encoding="utf-8").write(table)
by_cat = {c: {"in_scope": sum(1 for r in rs if not r["duplicate"] and not r["scope_out"]),
               "dup": sum(1 for r in rs if r["duplicate"]),
               "scope_out": sum(1 for r in rs if r["scope_out"]),
               "in_scope_mismatch": sum(1 for r in rs if not r["duplicate"] and not r["scope_out"] and not r["ok"])}
           for c, rs in cat_order.items()}
json.dump({"recompute_points": len(in_scope), "recompute_mismatches": len(mism),
           "duplicate_pair_rechecks": len(dups), "duplicate_rechecks_ok": sum(1 for r in dups if r["ok"]),
           "scope_out_observations": len(scope_out),
           "by_category": {c: {"in_scope": sum(1 for r in rs if not r["duplicate"] and not r["scope_out"]),
                               "dup": sum(1 for r in rs if r["duplicate"]),
                               "scope_out": sum(1 for r in rs if r["scope_out"]),
                               "in_scope_mismatch": sum(1 for r in rs if not r["duplicate"] and not r["scope_out"] and not r["ok"])}
                           for c, rs in cat_order.items()},
           "rows": rows}, open(os.path.join(out_dir, "recompute_points.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("in_scope points=%d mismatches=%d | duplicate pair rechecks=%d (ok %d) | scope-out=%d" % (
    len(in_scope), len(mism), len(dups), sum(1 for r in dups if r["ok"]), len(scope_out)))
for c, v in by_cat.items():
    print("  %-28s in_scope=%d dup=%d scope_out=%d mismatch=%d" % (c[:28], v["in_scope"], v["dup"], v["scope_out"], v["in_scope_mismatch"]))
for r in scope_out:
    print("SCOPE-OUT", r["id"], "|", r.get("where"), "|", str(r.get("note"))[:300])
