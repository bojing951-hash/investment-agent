#!/usr/bin/python3
"""Independent confirmation of the three counted deviations and of quoted rendering lines (read-only).
Usage: /usr/bin/python3 -I s15_confirm.py <snapshot.json> <report.json> <release_calendar.json> <MAP_REPORT.md> <FULL_REPORT.md> <report.md> <out.txt>
"""
import json
import sys


def main():
    snap_path, rep_path, cal_path, map_path, full_path, md_path, out_path = sys.argv[1:8]
    out = []
    with open(snap_path, "r", encoding="utf-8") as fh:
        snap = json.load(fh)
    st = snap["series_store"]

    def at(m, d):
        s = st[m]
        for i, x in enumerate(s["dates"]):
            if x == d:
                return s["values"][i]
        return None

    def le(m, d):
        s = st[m]
        best = None
        for x, v in zip(s["dates"], s["values"]):
            if x <= d and v is not None:
                best = (x, v)
        return best

    def pct(a, b):
        return (b / a - 1.0) * 100.0

    out.append("=== 资产窗独立复算(不依赖 s10 辅助函数)")
    res = {}
    for m in ("SPX", "NIKKEI225", "SHCOMP", "DAX", "CAC40", "VIX", "DXY"):
        s = le(m, "2026-10-23")
        c20 = at(m, "2026-11-20")
        last = le(m, "2026-11-23")
        eng = pct(s[1], last[1])
        close = pct(s[1], c20) if c20 is not None else None
        res[m] = (s, c20, last, eng, close)
        out.append("%s: 起 %s %s | 11-20 收盘 %s | 末观测 %s | 引擎窗 %+.4f%% | 收盘口径 %s" % (
            m, s[0], s[1], c20, last, eng, ("%+.4f%%" % close) if close is not None else "N/A"))
    spx_e, nk_e = res["SPX"][3], res["NIKKEI225"][3]
    spx_c, nk_c = res["SPX"][4], res["NIKKEI225"][4]
    out.append("引擎窗 SPX %+.2f%% vs NIKKEI225 %+.2f%%: 差 %.2f pp; 比值 %.3f" % (spx_e, nk_e, abs(spx_e - nk_e), nk_e / spx_e))
    out.append("收盘口径 SPX %+.2f%% vs NIKKEI225 %+.2f%%: 差 %.2f pp; 比值 %.3f" % (spx_c, nk_c, abs(spx_c - nk_c), nk_c / spx_c))
    out.append("引擎窗 SPX vs SHCOMP: 差 %.2f pp; SPX vs DAX: %.2f pp; SPX vs CAC40(末观测) 见上" % (
        abs(spx_e - res["SHCOMP"][3]), abs(spx_e - res["DAX"][3])))
    out.append("收盘口径 SPX vs SHCOMP: %.2f pp; NIKKEI vs SHCOMP: %.2f pp" % (
        abs(spx_c - res["SHCOMP"][4]), abs(nk_c - res["SHCOMP"][4])))
    out.append("BEI_10Y 末观测 %s ; @2026-11-19 %s ; @2026-11-18 %s" % (le("BEI_10Y", "2026-11-23"), at("BEI_10Y", "2026-11-19"), at("BEI_10Y", "2026-11-18")))
    out.append("TIPS_10Y 末观测 %s ; UST_10Y 末观测 %s" % (le("TIPS_10Y", "2026-11-23"), le("UST_10Y", "2026-11-23")))

    with open(cal_path, "r", encoding="utf-8") as fh:
        cal = json.load(fh)
    ents = cal.get("entries") or []
    out.append("=== 冻结日历 version=%s entries=%d" % (cal.get("version"), len(ents)))
    ekeys = sorted(set(k for e in ents for k in e.keys()))
    out.append("entry keys: %s" % ekeys)
    for e in ents:
        s = json.dumps(e, ensure_ascii=False)
        if any(t in s for t in ("FOMC", "DFEDTAR", "DFF", "federal", "Fed", "分钟", "纪要", "minutes")):
            out.append("  US-like entry: " + s[:400])
    out.append("  id 列表: %s" % [e.get("id") for e in ents])

    with open(rep_path, "r", encoding="utf-8") as fh:
        rep = json.load(fh)
    pdf = rep["research_plan"].get("policy_doc_facts")
    out.append("=== research_plan.policy_doc_facts: " + json.dumps(pdf, ensure_ascii=False)[:900])

    for name, p in (("MAP_REPORT.md", map_path), ("FULL_REPORT.md", full_path), ("report.md", md_path)):
        with open(p, "r", encoding="utf-8") as fh:
            lines = fh.read().split("\n")
        out.append("=== %s (%d lines) 命中行" % (name, len(lines)))
        for i, ln in enumerate(lines, 1):
            if any(t in ln for t in ("跌幅均相近", "最新 2.16", "2.15", "日历内仅有", "三个对照时点", "经独立语义审查", "互补", "方向互补", "支持主解释", "尚不能区分", "席位待唤起", "待裁")):
                out.append("%d: %s" % (i, ln[:520]))
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    print("wrote", out_path, "lines", len(out))


if __name__ == "__main__":
    main()
