#!/usr/bin/python3 -I
# s11: X21-X24 改按引擎发布规则重算锚(X21-X24 首版用『观测日≤锚日』是检查口径之误), X33 按证据索引两类来源重述, X41 缺口明细分组核对。只读; 可重复运行。
import sys, os, json, re, datetime as dt
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rc_lib import *
snap_p, rep_p, cal_p, reg_p, aj_p, outdir = sys.argv[1:7]
snap, rep, cal, reg, aj = load(snap_p, rep_p, cal_p, reg_p, aj_p)
SS = snap["series_store"]; F = "snapshot.series_store"
def J(o, n=500):
    s = json.dumps(o, ensure_ascii=False)
    return s if len(s) <= n else s[:n] + "…"
kinds = Counter(str(r.get("kind")) for r in rep["evidence_index"])
s3 = [s for s in rep["steps"] if str(s.get("step", "")).startswith("S3")]
s3env = (s3[0].get("envelope") or {}) if s3 else {}
print("=== evidence_index kinds:", dict(kinds))
s3rows = [r for r in rep["evidence_index"] if str(r.get("kind")) == "s3_envelope"]
print("=== s3_envelope rows n=%d sample:" % len(s3rows), [r.get("ref") for r in s3rows[:8]])
print("=== S3 step:", [(s.get("step"), s.get("executed"), s.get("ok")) for s in s3], "| envelope scalars:", {k: v for k, v in s3env.items() if not isinstance(v, (dict, list))})
eg = rep["run"].get("evidence_gate") or {}
print("=== evidence_gate keys:", list(eg.keys()))
for k, v in eg.items():
    if isinstance(v, str) and len(v) > 40:
        print("   ", k, ":", v[:400])
    elif isinstance(v, list):
        print("   ", k, ":", J(v, 700))
print("=== run scalar fields:", {k: v for k, v in rep["run"].items() if not isinstance(v, (dict, list))})
print("=== run keys with degrad/allow:", [k for k in rep["run"] if re.search("degrad|allow|failed", k, re.I)], "| archive_requested:", rep["run"].get("archive_requested"))
pts = json.load(open(os.path.join(outdir, "pts_all.json"), encoding="utf-8"))
P = Points()
RULE = {"CN_CPI_YOY": ("月末+9天", 9), "CN_PPI_YOY": ("月末+9天", 9), "UNEMPLOYMENT": ("月末+5天", 5), "CN_PMI_MFG": ("月末-1天", -1)}
def anchor_pub(mid, off):
    best = None
    for d, v in series(SS, mid):
        y, m = int(d[:4]), int(d[5:7])
        pe = (dt.date(y + m // 12, m % 12 + 1, 1) - dt.timedelta(days=1)).isoformat()
        if plus_days(pe, off) <= ANC:
            best = d
    return best
for i, mid in enumerate(("CN_CPI_YOY", "CN_PPI_YOY", "UNEMPLOYMENT", "CN_PMI_MFG")):
    nm, off = RULE[mid]
    na = at_or_before(SS, mid, ANC)[0]
    P.adds("X%d" % (21 + i), "report.json research_plan.point_values.cells[%s].anchors[3个月前].observation_date × %s.%s(按引擎发布规则%s独立重算)" % (mid, F, mid, nm), "%s 三个月前锚观测日(受审稿『观测 2026-07-01』; 按『发布日≤锚日』重算; 若仅按观测日≤锚日会误取 2026-08-01, 即 %s)" % (mid, na), anchor_pub(mid, off), "2026-07-01", )
    c = [c for c in rep["research_plan"]["point_values"]["cells"] if c["metric_id"] == mid][0]["anchors"]["3个月前"]
    P.adds("X%d" % (43 + i), "report.json research_plan.point_values.cells[%s].anchors[3个月前].observation_date" % mid, "%s 点值格三个月前锚观测日(引擎面直读)" % mid, c.get("observation_date"), "2026-07-01")
P.addb("X33", "report.json evidence_index[*].kind × steps[S3_*].envelope.snapshot_id", "证据索引 69 行 = snapshot_fact %d 行 + s3_envelope %d 行, 且 S3 步信封源快照 = research_snapshot_20261123(与受审稿『全部取自本工单冻结快照』相容)" % (kinds.get("snapshot_fact", 0), kinds.get("s3_envelope", 0)), sum(kinds.values()) == 69 and set(kinds) <= {"snapshot_fact", "s3_envelope"} and str(s3env.get("snapshot_id")) == "research_snapshot_20261123", "kinds=%s; S3=%s; snapshot_id=%s" % (dict(kinds), [s.get("step") for s in s3], s3env.get("snapshot_id")))
det = snap["gate_a"].get("noncore_missing_detail") or {}
exp = {"BUND_10Y": 0, "BUND_2Y": 0, "EA_HICP_YOY": 0, "EA_REAL_GDP_YOY": 0, "ECB_DFR": 0, "ECB_MRO": 0, "CN_OMO_7D": 1, "CN_POLICY_OVERNIGHT": 1, "JP_CPI_TOKYO_YOY": 2, "JP_REAL_GDP_YOY": 3}
def grp(t):
    if "ea:MISSING" in t:
        return 0
    if "注册表未登记该指标子源状态键" in t:
        return 1
    if "档内无该指标子源状态记录" in t:
        return 2
    if "FRED_JP_GDP" in t:
        return 3
    return 9
P.addb("X41", "snapshot.gate_a.noncore_missing_detail", "缺口明细四组归类与受审稿数据面注记逐指标一致(ea:MISSING×6 / 注册表未登记×2 / 档内无记录×1 / FRED_JP_GDP×1)", isinstance(det, dict) and set(det) == set(exp) and all(grp(str(det[k])) == exp[k] for k in exp), J(det, 420))
new = P.pts
for r in new:
    r["file"] = "s11"
ids_new = set(r["id"] for r in new)
allpts = [r for r in pts if r["id"] not in ids_new] + new
order = {"pts_a.json": 0, "pts_b.json": 1, "pts_c.json": 2, "pts_d.json": 3, "s06": 4, "s08": 5, "s10": 6, "s11": 7}
allpts.sort(key=lambda r: (order.get(r["file"], 9), r["id"]))
json.dump(allpts, open(os.path.join(outdir, "pts_all.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
L = ["| 编号 | 出处(文件+键) | 复算项 | 直算值 | 受审稿值 | 一致 |", "|---|---|---|---|---|---|"]
for r in allpts:
    rv = json.dumps(r.get("report"), ensure_ascii=False) if not isinstance(r.get("report"), str) else r["report"]
    L.append("| %s | %s | %s | %s | %s | %s |" % (r["id"], str(r.get("face", "")).replace("|", "/")[:150], str(r.get("key", "")).replace("|", "/")[:150], str(r.get("calc_str", ""))[:80], str(rv)[:80], "是" if r["ok"] else "**否**"))
open(os.path.join(outdir, "points_table.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n=== 本脚本点 ===")
for r in new:
    print(r["id"], "|", str(r.get("calc_str"))[:60], "|", json.dumps(r.get("report"), ensure_ascii=False)[:30], "|", r["ok"], "|", (r.get("note") or "")[:200])
mis = [r["id"] for r in allpts if not r["ok"]]
print("FINAL points=%d mismatches=%d %s" % (len(allpts), len(mis), mis))
