#!/usr/bin/python3 -I
# s13: 打印 C2/C3/C4 陈述原文、头条结论、情景全行、传导三环与辅助点候选清单(只读, 仅打印)
import sys, os, json, re
snap_p, aj_p, pts_p, reg_p, outdir = sys.argv[1:6]
aj = json.load(open(aj_p, encoding="utf-8")); pts = json.load(open(pts_p, encoding="utf-8"))
reg = json.load(open(reg_p, encoding="utf-8"))
print("registry version:", reg.get("version"), "| schema:", reg.get("schema_version"))
rm = aj["reader_map"]
print("\n##### headline_conclusion\n", rm["headline_conclusion"])
for i in (1, 2, 3):
    print("\n##### statement[%d] %s\n%s" % (i, aj["l3"]["contradictions"][i]["id"], aj["l3"]["contradictions"][i]["statement"]))
print("\n##### agent_declaration\n", json.dumps(aj["agent_declaration"], ensure_ascii=False)[:1500])
print("\n##### scenarios")
for s in aj["l4"]["scenarios"]:
    print(json.dumps(s, ensure_ascii=False, indent=1)[:3500])
print("\n##### transmission links")
for l in rm["transmission"][0]["links"]:
    print({k: v for k, v in l.items()})
print("\n##### history fields")
print("history_periods:", json.dumps(rm["history_periods"], ensure_ascii=False)[:300])
print("history_zero_case_note:", rm["history_zero_case_note"])
print("turning_supplement:", rm["turning_supplement"][:1500])
print("rates_decomposition:", json.dumps(rm["rates_decomposition"], ensure_ascii=False)[:1500])
print("asset_returns_echo:", json.dumps(rm["asset_returns_echo"], ensure_ascii=False)[:1500])
AUX = ["X01", "X02", "X03", "X16", "X17", "C07", "C09", "P41", "P42", "A41", "A42", "A43", "Q05", "Q06", "T18", "K01", "K02", "K03", "I09", "T19"]
print("\n##### 辅助点候选(id | ok | 复算项 | 直算 | 受审稿值)")
for r in pts:
    if r["id"] in AUX or r["id"].startswith("U_wd_") or r["id"].startswith("D05_"):
        print("%s | %s | %s | %s | %s" % (r["id"], r["ok"], str(r.get("key"))[:150], r.get("calc_str"), r.get("report")))
from collections import Counter
g = Counter(re.match(r"[A-Z]+", r["id"]).group(0) for r in pts)
print("\n##### 分组计数", dict(sorted(g.items())), "total", len(pts))
print("mismatches:", [r["id"] for r in pts if not r["ok"]])
print("row keys:", sorted(pts[0].keys()))
for tok in ("2026-01", "首观测", "序列自", "十七", "17 ", "15 "):
    print("token %r in text: %d" % (tok, json.dumps(aj, ensure_ascii=False).count(tok)))
