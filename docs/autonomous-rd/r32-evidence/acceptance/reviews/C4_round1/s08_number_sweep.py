#!/usr/bin/python3 -I
# s08: (1) 阿拉伯数字全量扫描: 受审稿内每个阿拉伯数字/日期是否已被复算点覆盖(未覆盖者列出并附上下文, 逐个人工判定)
#      (2) 补打受审稿中未在上轮引文定位里出现的段落全文(质量门注记 1/3/5/6/9、agent_declaration、转折补选、情景触发行)
#      (3) 三项残余核对并入复算表(X18-X20)并重写 pts_all.json / points_table.md。只读; 产出只写本席目录。
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rc_lib import *
snap_p, rep_p, cal_p, reg_p, aj_p, outdir = sys.argv[1:7]
snap, rep, cal, reg, aj = load(snap_p, rep_p, cal_p, reg_p, aj_p)
SS = snap["series_store"]
def norm(s):
    s = str(s).strip().replace(",", "").replace("%", "").replace("+", "").replace("bp", "")
    try:
        return ("%.6f" % float(s)).rstrip("0").rstrip(".")
    except ValueError:
        return s
pts = json.load(open(os.path.join(outdir, "pts_all.json"), encoding="utf-8"))
cov = set(); covdates = set()
for r in pts:
    repv = r.get("report")
    vals = list(repv) if isinstance(repv, (list, tuple)) else (list(repv.values()) if isinstance(repv, dict) else [repv])
    vals.append(r.get("calc_str"))
    for v in vals:
        if isinstance(v, bool):
            continue
        for d in re.findall(r"20\d\d-\d\d-\d\d", str(v)):
            covdates.add(d)
        for t in re.findall(r"-?\d+(?:\.\d+)?", str(v)):
            cov.add(norm(t))
strings = []
def walk(o, path):
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, path + "." + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, path + "[%d]" % i)
    elif isinstance(o, str):
        strings.append((path, o))
walk(aj, "$")
unc = {}
ndates = 0; uncd = {}
for path, s in strings:
    for m in re.finditer(r"20\d\d-\d\d-\d\d", s):
        ndates += 1
        d = m.group(0)
        if d not in covdates:
            uncd.setdefault(d, []).append("%s …%s…" % (path[-34:], s[max(0, m.start() - 26):m.end() + 22].replace("\n", " ")))
    for m in re.finditer(r"(?<![\d.\-])[+\-−]?\d+(?:\.\d+)?(?![\d.\-]*\d)(?!%?(?:年|月|日|Q))", s):
        pass
    # 逐 token: 去掉日期后取数
    s2 = re.sub(r"20\d\d-\d\d-\d\d", " ", s)
    for m in re.finditer(r"[+\-−]?\d+(?:\.\d+)?", s2):
        tok = m.group(0).replace("−", "-")
        if re.match(r"^\d{4}$", tok) and 1900 <= int(tok) <= 2100:
            continue  # 年份
        if norm(tok) not in cov:
            unc.setdefault(norm(tok), []).append("%s …%s…" % (path[-34:], s2[max(0, m.start() - 24):m.end() + 18].replace("\n", " ")))
print("strings=%d  dates=%d  uncovered dates=%d  uncovered numeric tokens=%d" % (len(strings), ndates, len(uncd), len(unc)))
for d in sorted(uncd):
    print("  DATE", d, "|", uncd[d][0])
for t in sorted(unc, key=lambda x: (len(x), x)):
    print("  NUM", t, "(%d)" % len(unc[t]), "|", unc[t][0])
print("\n===== 未重读段落全文 =====")
def show(label, o):
    print("\n## %s" % label)
    print(json.dumps(o, ensure_ascii=False, indent=1) if not isinstance(o, str) else o)
show("agent_declaration", aj.get("agent_declaration"))
qn = aj.get("quality_gate_notes")
for i in (1, 3, 5, 6, 9):
    show("quality_gate_notes[%d]" % i, qn[i])
rm = aj.get("reader_map")
print("\n## reader_map keys:", list(rm.keys()))
for k in ("turning_supplement", "history_zero_case_note", "rates_decomposition", "asset_returns_echo"):
    if k in rm:
        show("reader_map." + k, rm[k])
for i, sc in enumerate(aj["l4"]["scenarios"]):
    show("l4.scenarios[%d] (除 scenario/asset_direction.direction)" % i, {k: v for k, v in sc.items() if k != "rows"} | {"rows": {k: v for k, v in sc["rows"].items() if not (k == "asset_direction")}})
    if "asset_direction" in sc["rows"]:
        print("   asset_direction keys:", {k: (v if k != "direction" else "…") for k, v in sc["rows"]["asset_direction"].items()})
print("\n## l4 keys:", list(aj["l4"].keys()), "| l3 keys:", list(aj["l3"].keys()))
# ---- (3) 残余核对并入 ----
P = Points()
F = "snapshot.series_store"
P.add("X18", F + ".VIX@2026-11-23", "VIX 引擎窗末值(受审稿『VIX +38.87%(19.45→27.01)』)", at(SS, "VIX", "2026-11-23"), 27.01, 2)
pv = rep["research_plan"]["point_values"]["cells"]
omo = [c for c in pv if c["metric_id"] == "CN_OMO_7D"][0]["anchors"]
txt_omo = json.dumps(omo.get("最新一期", {}), ensure_ascii=False) + json.dumps(omo.get("3个月前", {}), ensure_ascii=False)
P.addb("X19", "report.json research_plan.point_values.cells[CN_OMO_7D].anchors", "七天逆回购最新一格引擎注记含『过期/滞后』与十天发布频率窗(受审稿『末观测滞后二十四天、超出十天发布频率窗口』)", ("过期" in txt_omo or "stale" in txt_omo) and "24" in txt_omo and ("10" in txt_omo), re.sub(r"\s+", " ", txt_omo)[:260])
blob = json.dumps(reg, ensure_ascii=False) + json.dumps(rep["research_plan"], ensure_ascii=False) + json.dumps(snap.get("notes"), ensure_ascii=False)
i0 = blob.find("换锚")
P.addb("X20", "metric_registry.json / report.json research_plan (含『换锚』字样的引擎注记)", "隔夜利率注记含 2026-11-02 换锚后的操作目标锚(受审稿转述)", i0 >= 0 and "2026-11-02" in blob[max(0, i0 - 160):i0 + 160], blob[max(0, i0 - 150):i0 + 130] if i0 >= 0 else "NOT FOUND")
res = P.pts
for r in res:
    r["file"] = "s08"
allpts = pts + res
json.dump(allpts, open(os.path.join(outdir, "pts_all.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
L = ["| 编号 | 出处(文件+键) | 复算项 | 直算值 | 受审稿值 | 一致 |", "|---|---|---|---|---|---|"]
for r in allpts:
    rv = json.dumps(r.get("report"), ensure_ascii=False) if not isinstance(r.get("report"), str) else r["report"]
    L.append("| %s | %s | %s | %s | %s | %s |" % (r["id"], str(r.get("face", "")).replace("|", "/")[:150], str(r.get("key", "")).replace("|", "/")[:150], str(r.get("calc_str", ""))[:80], str(rv)[:80], "是" if r["ok"] else "**否**"))
open(os.path.join(outdir, "points_table.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n===== X18-X20 =====")
for r in res:
    print(r["id"], "|", r.get("calc_str"), "|", json.dumps(r.get("report"), ensure_ascii=False), "|", r["ok"], "|", (r.get("note") or "")[:300])
mis = [r["id"] for r in allpts if not r["ok"]]
print("FINAL points=%d mismatches=%d %s" % (len(allpts), len(mis), mis))
