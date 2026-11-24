# -*- coding: utf-8 -*-
"""Merge the part tables written by s7_p*.py, assign ids, write recompute_table.json/.md, print summary.
usage: python3 -I s7_recompute.py <run_dir> <install_tree> <out_dir>   (run after all s7_p*.py)"""
import glob
import json
import os
import sys


def main():
    out = sys.argv[3]
    rows, errors, F, info = [], [], {}, {}
    for p in sorted(glob.glob(os.path.join(out, "_part_*.json"))):
        with open(p, "r", encoding="utf-8") as fh:
            d = json.load(fh)
        rows += d["rows"]
        errors += d["errors"]
        for k, v in d["F"].items():
            F["%s@%s" % (k, os.path.basename(p))] = v
        info[os.path.basename(p)] = len(d["rows"])
    for i, x in enumerate(rows):
        x["id"] = "P%03d" % (i + 1)
    bad = [x for x in rows if not x["ok"]]
    cats = {}
    for x in rows:
        k = x["cat"]
        cats.setdefault(k, [0, 0])
        cats[k][0] += 1
        cats[k][1] += 0 if x["ok"] else 1
    summ = {"points": len(rows), "ok": len(rows) - len(bad),
            "mismatches": len([x for x in bad if x["found"]]),
            "not_found": len([x for x in bad if not x["found"]]), "errors": len(errors),
            "by_cat": cats, "parts": info}
    with open(os.path.join(out, "recompute_table.json"), "w", encoding="utf-8") as fh:
        json.dump({"summary": summ, "rows": rows, "errors": errors, "findings_support": F},
                  fh, ensure_ascii=False, indent=1)
    with open(os.path.join(out, "recompute_table.md"), "w", encoding="utf-8") as fh:
        fh.write("| 编号 | 覆盖项 | 受审位置 | 受审原文片段 | 出处(文件+键) | 直算值 | 报告值 | 一致 |\n"
                 "|---|---|---|---|---|---|---|---|\n")
        for x in rows:
            tag = "是" if x["ok"] else ("否(偏离)" if x["found"] else "未找到原文")
            cell = lambda s: str(s).replace("|", "/").replace("\n", " ")
            fh.write("| %s | %s | %s | %s | %s | %s | %s | %s |\n" % (
                x["id"], x["cat"], x["where"], cell(x["needle"] or "(结构化字段)"), cell(x["src"]),
                json.dumps(x["computed"], ensure_ascii=False), json.dumps(x["claimed"], ensure_ascii=False), tag))
    print(json.dumps(summ, ensure_ascii=False, indent=1))
    for x in bad:
        print("BAD %s [%s] %s :: needle=%s :: computed=%s claimed=%s :: %s" % (
            x["id"], x["cat"], x["where"], x["needle"], json.dumps(x["computed"], ensure_ascii=False),
            json.dumps(x["claimed"], ensure_ascii=False), x["src"]))
    for e in errors:
        print("ERR %s" % json.dumps(e, ensure_ascii=False))


if __name__ == "__main__":
    main()
