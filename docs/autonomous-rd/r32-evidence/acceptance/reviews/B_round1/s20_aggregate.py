#!/usr/bin/python3 -I
"""席位自写脚本 s20: 汇总全部 points_*.json(只读本席目录), 产出 x_aggregate.json / x_table.md / x_table_probes.md / x_blocks.md.

计数规则: kind 缺省或 "point" 的行计为复算点; kind=="probe" 的行(口径敏感性探针/脚本自检)不计点.
数值点 = computed 为 int/float 且非 bool; 其余(含 bool 与字典型直算值)记为条件核对点.

用法: /usr/bin/python3 -I s20_aggregate.py <席位目录>
"""
import glob
import json
import os
import sys

SEAT = sys.argv[1]
files = sorted(glob.glob(os.path.join(SEAT, "points_*.json")))


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def is_point(r):
    return r.get("kind", "point") == "point"


allrows = []
per = []
first_keys = None
for f in files:
    d = json.load(open(f, encoding="utf-8"))
    rows = d["rows"]
    if first_keys is None and rows:
        first_keys = sorted(rows[0].keys())
    pts = [r for r in rows if is_point(r)]
    n_num = sum(1 for r in pts if is_num(r.get("computed")))
    per.append({"file": os.path.basename(f), "block": d.get("block"), "title": d.get("title"), "points": len(pts), "numeric": n_num, "bool": len(pts) - n_num,
                "match": sum(1 for r in pts if r.get("match") is True), "mismatch": sum(1 for r in pts if r.get("match") is False),
                "undetermined": sum(1 for r in pts if r.get("match") is None), "probes": len(rows) - len(pts)})
    for r in rows:
        r = dict(r)
        r["_file"] = os.path.basename(f)
        allrows.append(r)
pts = [r for r in allrows if is_point(r)]
probes = [r for r in allrows if not is_point(r)]
mis = [r for r in pts if r.get("match") is False]
und = [r for r in pts if r.get("match") is None]
tot = len(pts)
n_num = sum(1 for r in pts if is_num(r.get("computed")))


def fmt(v):
    if isinstance(v, bool):
        return "True" if v else "False"
    if isinstance(v, float):
        return repr(v)
    return json.dumps(v, ensure_ascii=False)


def one_line(v):
    return fmt(v).replace("\n", " ")


def det(r):
    return str(r.get("detail", r.get("note", "")))


agg = {"files": per, "row_keys": first_keys, "recompute_points": tot, "numeric_points": n_num, "bool_points": tot - n_num, "recompute_mismatches": len(mis), "undetermined": len(und),
       "probes": len(probes),
       "mismatch_details": [f"{r['_file']} | {r.get('id')} | 直算 {one_line(r.get('computed'))} | 受审稿 {one_line(r.get('claim'))} | 出处 {r.get('source')}" for r in mis],
       "undetermined_details": [f"{r['_file']} | {r.get('id')} | 直算 {one_line(r.get('computed'))} | 受审稿 {one_line(r.get('claim'))} | {det(r)}" for r in und]}
json.dump(agg, open(os.path.join(SEAT, "x_aggregate.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def esc(s):
    return str(s).replace("|", "｜").replace("\n", " ")


lines = ["| # | 中间表 | 复算点 | 出处(文件+键) | 直算值 | 受审稿值 | 一致 |", "|---|---|---|---|---|---|---|"]
n = 0
for r in pts:
    n += 1
    verdict = "一致" if r.get("match") is True else ("偏离" if r.get("match") is False else "未定")
    lines.append(f"| {n} | {r['_file'].replace('points_', '').replace('.json', '')} | {esc(r.get('id'))} | {esc(r.get('source'))} | {esc(one_line(r.get('computed')))} | {esc(one_line(r.get('claim')))} | {verdict} |")
open(os.path.join(SEAT, "x_table.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
plines = ["| # | 中间表 | 探针 | 直算值 | 出处(文件+键) | 说明 |", "|---|---|---|---|---|---|"]
m = 0
for r in probes:
    m += 1
    plines.append(f"| {m} | {r['_file'].replace('points_', '').replace('.json', '')} | {esc(r.get('id'))} | {esc(one_line(r.get('computed')))} | {esc(r.get('source'))} | {esc(det(r))} |")
open(os.path.join(SEAT, "x_table_probes.md"), "w", encoding="utf-8").write("\n".join(plines) + "\n")
blines = ["| 块 | 中间表 | 覆盖内容 | 复算点 | 其中数值直算 | 条件核对 | 命中 | 偏离 | 未定 | 探针(不计点) |", "|---|---|---|---|---|---|---|---|---|---|"]
for p in per:
    blines.append(f"| {p['block']} | {p['file']} | {esc(p['title'])} | {p['points']} | {p['numeric']} | {p['bool']} | {p['match']} | {p['mismatch']} | {p['undetermined']} | {p['probes']} |")
blines.append(f"| 合计 | {len(per)} 个中间表 | — | {tot} | {n_num} | {tot - n_num} | {tot - len(mis) - len(und)} | {len(mis)} | {len(und)} | {len(probes)} |")
open(os.path.join(SEAT, "x_blocks.md"), "w", encoding="utf-8").write("\n".join(blines) + "\n")
print(json.dumps({k: agg[k] for k in ("recompute_points", "numeric_points", "bool_points", "recompute_mismatches", "undetermined", "probes", "row_keys")}, ensure_ascii=False))
for p in per:
    print(p)
for x in agg["mismatch_details"]:
    print("MISMATCH:", x)
for x in agg["undetermined_details"]:
    print("UNDETERMINED:", x)
print("table rows:", n, "probe rows:", m)
