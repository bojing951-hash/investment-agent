#!/usr/bin/python3 -I
# s17a: 汇总复算点(追加 X47-X51), 分类比对点/辅助点, 直算反方攻击所需数值, 重建逐点表, 输出 draft_data.json。
# 只读受审面; 只写本席目录。用法: /usr/bin/python3 -I s17a_data.py SNAP REP CAL REG AJ ENVF OUTDIR PTS_ALL MAPMD
import sys, os, json, re, hashlib, datetime as dt
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rc_lib import *

snap_p, rep_p, cal_p, reg_p, aj_p, env_p, outdir, pts_p = sys.argv[1:9]
snap, rep, cal, reg, aj = load(snap_p, rep_p, cal_p, reg_p, aj_p)
env = json.load(open(env_p, encoding="utf-8"))
SS = snap["series_store"]
pts = json.load(open(pts_p, encoding="utf-8"))


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def pre_of(r):
    return re.match(r"[A-Z]+", r["id"]).group(0)


aj_sha, rp_sha, sn_sha, cl_sha, rg_sha = sha(aj_p), sha(rep_p), sha(snap_p), sha(cal_p), sha(reg_p)
assert aj_sha.startswith("7f9bcc62b5f1cd69"), "受审版本已变化: " + aj_sha

# ---------- A. 追加补充核对点 ----------
pvm = rep["research_plan"]["point_values"]
s6 = [s for s in rep["steps"] if s.get("step") == "S6_analog"][0]["envelope"]["data"]
fd = s6["features_dropped_at_anchor"]


def mkrow(pid, face, key, calc, repv, nd=2, note=""):
    if isinstance(calc, bool) or isinstance(repv, bool):
        okk = (calc == repv)
    elif isinstance(calc, (int, float)) and isinstance(repv, (int, float)):
        okk = abs(round(calc, nd) - repv) <= 1e-9 * max(1.0, abs(repv))
    else:
        okk = (calc == repv)
    return {"id": pid, "face": face, "file": face, "key": key, "calc": calc, "calc_str": str(calc),
            "report": repv, "ok": bool(okk), "note": note}


new = [
    mkrow("X47", "report.json",
          "research_plan.point_values.cells 数量(与信封 reader_map_contract.engine_faces.point_values_cells 同值); 受审稿 agent_declaration.basis: 点值格(18格",
          len(pvm["cells"]), 18),
    mkrow("X48", "report.json",
          "research_plan.point_values.absent 数量(与信封 point_values_absent 同值: EA_REAL_GDP_YOY/EA_HICP_YOY/ECB_MRO/ECB_DFR); 受审稿: 另4格序列缺席",
          len(pvm["absent"]), 4),
    mkrow("X49", "snapshot.series_store",
          "JP_POLICY_RATE 2025-12 月均→2026-10 月均 变动(bp); 受审稿 quality_gate_notes[6]: 仅自窗内首观测(2025-12 月均 0.557)起算为 +67bp",
          bp(mv(SS, "JP_POLICY_RATE", "2025-12"), mv(SS, "JP_POLICY_RATE", "2026-10")), 67),
    mkrow("X50", "report.json",
          "S6_analog.features_dropped_at_anchor 的 HY_IG_gap_d12m/HY_OAS_d12m 均含『hist_25<36点(=36个月史…)』且 normalization.min_history_months=36; 受审稿 history_zero_case_note: 历史长度不足 36 个月——HY_IG_gap_d12m、HY_OAS_d12m",
          all(("36" in fd[f]) for f in ("HY_IG_gap_d12m", "HY_OAS_d12m")) and s6["normalization"]["min_history_months"] == 36, True),
]
fi = env.get("frozen_inputs", {})
sha_ok = all(sha(p)[:16] == fi[k] for k, p in (("config/release_calendar.json", cal_p),
                                                 ("config/metric_registry.json", reg_p),
                                                 ("data/daily/research_snapshot_20261123.json", snap_p)))
new.append(mkrow("X51", "AGENT_SEAT_ENVELOPE.json",
                 "frozen_inputs 三项 sha256 前16位与实测文件一致(完整性前提; 受审稿无对应文字)",
                 sha_ok, True))
ids = {r["id"] for r in pts}
new = [r for r in new if r["id"] not in ids]  # 幂等: 重跑不重复追加
pts.extend(new)

FIXED_AUX = {"X01", "X02", "X03", "X16", "X17", "C07", "C09", "P41", "P42", "A41", "A42", "A43",
             "Q05", "Q06", "T18", "K01", "K02", "K03", "I09", "T19", "X51"}
missing_aux = sorted(FIXED_AUX - {r["id"] for r in pts})
assert not missing_aux, "辅助点清单含不存在的编号: %s" % missing_aux
for r in pts:
    r["aux"] = (r["id"] in FIXED_AUX) or r["id"].startswith("U_wd_")
cmp_ = [r for r in pts if not r["aux"]]
aux = [r for r in pts if r["aux"]]
mis = [r for r in cmp_ if not r["ok"]]
aux_mis = [r for r in aux if not r["ok"]]

# ---------- B. 重建逐点表 ----------
def cell(x):
    return str(x).replace("|", "\\|").replace("\n", " ").strip()


HDR = "| 编号 | 出处(只读面: 文件 · 面/键) | 复算项(序列ID@观测日/月 或 字段) | 直算值 | 受审稿值 | 判定 |\n|---|---|---|---|---|---|"


def src(r):
    f, fc = str(r.get("file")), str(r.get("face"))
    if re.match(r"^(pts_[a-z0-9]+\.json|s\d+[a-z0-9_]*)$", f):
        for a, b in (("snapshot.", "research_snapshot_20261123.json "), ("calendar.", "release_calendar.json "), ("registry.", "metric_registry.json ")):
            if fc.startswith(a):
                fc = b + fc[len(a):]
                break
        return {"datetime": "直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of)",
                "算术": "直算(算术; 输入=已比对的两端值)"}.get(fc, fc)
    if f == fc:
        return fc
    return {"datetime": "直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of)",
            "算术": "直算(算术; 输入=已比对的两端值)"}.get(fc, f + " · " + fc)


def table(rows, auxflag):
    out = [HDR]
    for r in rows:
        v = "辅助(不计入)" if auxflag else ("一致" if r["ok"] else "偏离")
        cols = [str(r["id"]), cell(src(r)), cell(r.get("key")),
                cell(r.get("calc_str")), cell(r.get("report")), v]
        out.append("| " + " | ".join(cols) + " |")
    return "\n".join(out)


tbl_cmp, tbl_aux = table(cmp_, False), table(aux, True)
with open(pts_p, "w", encoding="utf-8") as f:
    json.dump(pts, f, ensure_ascii=False, indent=0)
with open(os.path.join(outdir, "points_table.md"), "w", encoding="utf-8") as f:
    f.write("# 复算点逐点表(比对点 %d, 辅助点 %d; 由 s17a_data.py 重建)\n\n" % (len(cmp_), len(aux)) + tbl_cmp + "\n\n## 辅助核对点\n\n" + tbl_aux + "\n")

# ---------- C. 分组统计 ----------
DESC = {"P": "政策维(美/日政策利率、事件簇、日历实录、中国 LPR/逆回购/隔夜、注册表)", "E": "能源价格对账(WTI_F/BRENT_F/现货月均价/月均值)",
        "I": "通胀维(日/美/中通胀序列水平、同比与发布日)", "T": "转折候选池、三转折叙述与补选项", "G": "增长维(GDP/失业率/工业生产/PMI/日本 GDP)",
        "V": "点值格锚格按发布规则独立重选", "A": "资产月窗两口径与盘中反弹", "R": "美国三利率分解(近一月窗、12 个月窗)",
        "N": "类比面(扫描/有效/剔除/TOP-5/覆盖率/贡献份额/缺席特征)", "C": "情景(阈值派生、截止日取值、互斥、期限)",
        "U": "发布日(日历实录/推定规则)与截止纪律", "D": "日期与截止时点(四地时刻、末观测日、截止后日期)",
        "Q": "Gate A 缺口与质量计数", "K": "结构性陈述计数(矛盾/链条/传导环/转折/并列解释)",
        "X": "补充核对(渲染面/信封/证据索引/别名表/并项规则/计数类数字)"}
groups = sorted({pre_of(r) for r in pts}, key=lambda x: (len(x), x))
grow = []
for g in groups:
    c = [r for r in cmp_ if pre_of(r) == g]
    a = [r for r in aux if pre_of(r) == g]
    grow.append((g, DESC.get(g, ""), len(c), sum(1 for r in c if not r["ok"]), len(a)))

# ---------- D. 反方攻击与问题项所需直算值 ----------
anc = at(SS, "WTI_F", "2026-08-21")
w = [(d, v) for d, v in series(SS, "WTI_F") if d >= "2026-11-09"]
below = [(d, round(v, 2)) for d, v in w if v < anc]
above = [(d, round(v, 2)) for d, v in w if v >= anc]
aug = [(d, round(v, 2)) for d, v in series(SS, "WTI_F") if "2026-08-21" <= d <= "2026-08-31" and v < anc]
soct = [v for d, v in series(SS, "WTI_F") if "2026-09-01" <= d <= "2026-10-31"]
D = {
    "wti_all": "、".join("%s=%.2f" % (d[5:], v) for d, v in w),
    "wti_below_n": len(below), "wti_above": "、".join("%s=%.2f" % (d[5:], v) for d, v in above),
    "wti_n": len(w), "wti_first": below[0][0] if below else None, "wti_first_v": below[0][1] if below else None,
    "wti_anchor": round(anc, 2), "wti_aug": "、".join(d[5:] for d, _ in aug),
    "soct_n": len(soct), "soct_min": round(min(soct), 2),
    "u_cd": pct(at(SS, "USDJPY", "2026-10-20"), at(SS, "USDJPY", "2026-11-19")),
    "c_cd": pct(at(SS, "USDCNY", "2026-10-20"), at(SS, "USDCNY", "2026-11-19")),
    "u_m": pct(at(SS, "USDJPY", "2026-10-23"), at(SS, "USDJPY", "2026-11-23")),
    "c_m": pct(at(SS, "USDCNY", "2026-10-23"), at(SS, "USDCNY", "2026-11-23")),
    "u0": round(at(SS, "USDJPY", "2026-10-20"), 3), "u1": round(at(SS, "USDJPY", "2026-11-19"), 3),
    "ppi_path": "→".join("%.1f" % v for d, v in series(SS, "CN_PPI_YOY") if "2026-07" <= d[:7] <= "2026-10"),
    "cpi_path": "→".join("%.1f" % v for d, v in series(SS, "CN_CPI_YOY") if "2026-07" <= d[:7] <= "2026-10"),
    "t23": round(bp(at(SS, "TIPS_10Y", "2026-10-23"), at(SS, "TIPS_10Y", "2026-11-19")), 1),
    "b23": round(bp(at(SS, "BEI_10Y", "2026-10-23"), at(SS, "BEI_10Y", "2026-11-19")), 1),
    "n23": round(bp(at(SS, "UST_10Y", "2026-10-23"), at(SS, "UST_10Y", "2026-11-19")), 1),
    "isow": dt.date(2026, 9, 16).isocalendar()[1],
    "iso_ok": dt.date(2026, 9, 16).isocalendar()[1] == dt.date(2026, 9, 18).isocalendar()[1],
    "wd_1114": dt.date(2026, 11, 14).strftime("%A"), "wd_1115": dt.date(2026, 11, 15).strftime("%A"),
    "wd_0815": dt.date(2026, 8, 15).strftime("%A"),
    "core_d": round(yoy(SS, "CORE_CPI", "2026-08") - yoy(SS, "CORE_CPI", "2026-05"), 6),
    "core_d4": round(round(yoy(SS, "CORE_CPI", "2026-08"), 4) - round(yoy(SS, "CORE_CPI", "2026-05"), 4), 4),
    "core_y05": yoy(SS, "CORE_CPI", "2026-05"), "core_y08": yoy(SS, "CORE_CPI", "2026-08"),
    "d_gdp": round(2.07 - 2.19, 2), "d_ip": round(2.15 - 1.25, 2), "d_pm": round(49.3 - 49.2, 1), "d_jp": round(1.16 - 0.80, 2),
    "absent": pvm["absent"], "cells": len(pvm["cells"]),
}

# ---------- E. 数字 token 复扫(ASCII 边界) ----------
leaves = []


def walk(o, p):
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, p + "." + k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, "%s[%d]" % (p, i))
    elif isinstance(o, str):
        leaves.append((p, o))


walk(aj, "$")
repvals = []
for r in cmp_:
    if not r["ok"]:
        continue
    try:
        repvals.append(float(r.get("report")))
    except Exception:
        pass
tok = {}
for p, s in leaves:
    t = re.sub(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+\-]\d{2}:\d{2}", " ", s)
    t = re.sub(r"\d{4}-\d{2}-\d{2}", " ", t)
    for m in re.finditer(r"(?<![0-9A-Za-z_.\-])(\d+(?:\.\d+)?)(?![0-9A-Za-z_.])", t):
        x = m.group(1)
        if re.match(r"^\d{4}$", x):
            continue
        try:
            f = float(x)
        except Exception:
            continue
        cov = any(abs(fv) == abs(f) for fv in repvals)
        a, b = max(0, m.start() - 14), min(len(t), m.end() + 10)
        e = tok.setdefault(x, {"n": 0, "cov": cov, "ctx": []})
        e["n"] += 1
        c = t[a:b].replace("\n", " ")
        if len(e["ctx"]) < 2 and c not in e["ctx"]:
            e["ctx"].append(c)
unc = [(k, v["n"], " ‖ ".join(v["ctx"])) for k, v in sorted(tok.items(), key=lambda kv: float(kv[0])) if not v["cov"]]

# ---------- F. 被引用点编号的键(供复核) ----------
CITE = ["P06", "P10", "P17", "P28", "P29", "P30", "P34", "P38", "P50", "P57", "P58", "P62", "P63", "P68", "P71", "P43", "P44",
        "E25", "I12", "I13", "I18", "I19", "I23", "I24", "I30", "I30b", "I33", "I36",
        "T04", "T04b", "T16", "T17", "T20", "G03", "G04", "G06", "G07", "G11", "G12", "G14", "G15", "G16", "G17",
        "V01", "V02", "A31", "A34", "A36", "A40", "A44", "A45", "R08", "R12", "Q03", "Q13", "K17",
        "X07", "X08", "X09", "X13", "X14", "X15", "X19", "X33", "X39", "X40", "D01", "D02"] + ["X47", "X48", "X49", "X50", "X51"]
byid = {r["id"]: r for r in pts}
cited = {c: (byid[c].get("key") if c in byid else "!!不存在!!") for c in CITE}

out = {"aj_sha": aj_sha, "rep_sha": rp_sha, "snap_sha": sn_sha, "cal_sha": cl_sha, "reg_sha": rg_sha,
       "n_cmp": len(cmp_), "n_ok": len(cmp_) - len(mis), "n_mis": len(mis), "mis_ids": [r["id"] for r in mis],
       "n_aux": len(aux), "aux_ids": [r["id"] for r in aux], "aux_mis": [r["id"] for r in aux_mis],
       "n_all": len(pts), "new": new, "grow": grow, "tbl_cmp": tbl_cmp, "tbl_aux": tbl_aux,
       "tok_total": len(tok), "unc": unc, "cited": cited, "D": D,
       "e25": {k: byid["E25"].get(k) for k in ("key", "calc_str", "report", "note")},
       "sample_rows": [pts[0], pts[-1]],
       "question": rep["run"]["question"], "ts": rep["run"]["ts_utc"], "gh": rep["run"]["git_head"],
       "ssid": (rep["run"].get("evidence_gate") or {}).get("source_snapshot_id"),
       "cal_version": cal.get("version"), "cal_n": len(cal.get("entries", cal.get("batches", []))),
       "reg_version": reg.get("version"), "frozen": fi, "sha_ok": sha_ok,
       "map_shang": open(sys.argv[9], encoding="utf-8").read().count("尚不能区分"),
       "cal_keys": list(cal.keys())[:12] if isinstance(cal, dict) else None}
with open(os.path.join(outdir, "draft_data.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("比对点 %d (一致 %d, 偏离 %d %s) | 辅助点 %d (偏离 %s) | 合计 %d" % (len(cmp_), len(cmp_) - len(mis), len(mis), [r["id"] for r in mis], len(aux), [r["id"] for r in aux_mis], len(pts)))
print("补充点:", [(r["id"], r["ok"], r["calc_str"], r["report"]) for r in new])
print("token 总数 %d, 无同值通过点 %d: %s" % (len(tok), len(unc), [u[0] for u in unc]))
print("D:", json.dumps(D, ensure_ascii=False))
print("E25:", json.dumps(out["e25"], ensure_ascii=False))
print("样例行0:", json.dumps(pts[0], ensure_ascii=False)[:500])
print("样例行末:", json.dumps(pts[-1], ensure_ascii=False)[:500])
for c in CITE:
    print("引用 %s => %s" % (c, str(cited[c])[:170]))
print("未覆盖 token:")
for u in unc:
    print("   [%s] x%d : %s" % u)
print("分组(组, 比对点, 偏离, 辅助点):", [(g[0], g[2], g[3], g[4]) for g in grow])
print("cal_keys:", out["cal_keys"], "| cal_version:", out["cal_version"], "| cal_n:", out["cal_n"], "| map 尚不能区分:", out["map_shang"], "| frozen_ok:", sha_ok)
