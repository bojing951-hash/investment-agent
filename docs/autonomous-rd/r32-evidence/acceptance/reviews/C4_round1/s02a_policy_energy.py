#!/usr/bin/python3 -I
# s02a: 政策面 + 能源面 独立复算(只读)
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rc_lib import *

snap_p, rep_p, cal_p, reg_p, aj_p, outdir = sys.argv[1:7]
snap, rep, cal, reg, aj = load(snap_p, rep_p, cal_p, reg_p, aj_p)
SS = snap["series_store"]
P = Points()
RP = "agent_judgment.json"

# ---------- 政策面 (C1 / M1 / reader_map) ----------
a = at_or_before(SS, "DFEDTARU", ANC); b = at_or_before(SS, "DFEDTARU", CUT)
P.add("P01", SNAP, "DFEDTARU@<=%s (obs %s)" % (ANC, a[0]), a[1], 3.75, 2)
P.adds("P02", SNAP, "DFEDTARU anchor obs date", a[0], "2026-08-23")
P.add("P03", SNAP, "DFEDTARU@<=%s (obs %s)" % (CUT, b[0]), b[1], 4.0, 2)
P.adds("P04", SNAP, "DFEDTARU latest obs date", b[0], "2026-11-23")
P.add("P05", SNAP, "DFEDTARU 上限变动(bp)=(b-a)*100", bp(a[1], b[1]), 25, 0)
ch = changes(SS, "DFEDTARU", "2025-11-23", CUT)
P.adds("P06", SNAP, "DFEDTARU 窗内变动点1 日期(生效)", ch[-1][0], "2026-09-17")
P.add("P07", SNAP, "DFEDTARU 变动点1 from", ch[-1][2], 3.75, 2)
P.add("P08", SNAP, "DFEDTARU 变动点1 to", ch[-1][3], 4.0, 2)
P.add("P09", SNAP, "DFEDTARU 变动点1 幅度(bp)", bp(ch[-1][2], ch[-1][3]), 25, 0)
P.adds("P10", SNAP, "决议日=生效日前一日", plus_days(ch[-1][0], -1), "2026-09-16")
P.adds("P11", SNAP, "DFEDTARU 窗内变动点0 日期(生效)", ch[0][0], "2025-12-11")
P.add("P12", SNAP, "DFEDTARU 变动点0 from", ch[0][2], 4.0, 2)
P.add("P13", SNAP, "DFEDTARU 变动点0 to", ch[0][3], 3.75, 2)
P.add("P14", SNAP, "DFEDTARU 变动点0 幅度(bp)", bp(ch[0][2], ch[0][3]), -25, 0)
P.adds("P15", SNAP, "决议日=生效日前一日", plus_days(ch[0][0], -1), "2025-12-10")
P.addb("P16", SNAP, "DFEDTARU 近一年窗变动点数=2", len(ch) == 2, str(ch))
P.add("P17", SNAP, "DFEDTARU 近一年净变动(bp)", sum(bp(c[2], c[3]) for c in ch), 0, 0)
d0 = [x for x in series(SS, "DFF") if plus_days(x[0], 1) <= ANC][-1]; d1 = [x for x in series(SS, "DFF") if plus_days(x[0], 1) <= CUT][-1]
P.adds("P18", SNAP, "DFF 三个月前锚 obs(发布=观测日+1 ≤ 2026-08-23 的最后观测)", d0[0], "2026-08-22")
P.add("P19", SNAP, "DFF@%s" % d0[0], d0[1], 3.63, 2)
P.adds("P20", SNAP, "DFF 最新 obs(发布=观测日+1 ≤ 2026-11-23 的最后观测)", d1[0], "2026-11-19")
P.add("P21", SNAP, "DFF@%s" % d1[0], d1[1], 3.88, 2)
P.add("P22", SNAP, "DFF@2026-09-16", at(SS, "DFF", "2026-09-16"), 3.63, 2)
P.add("P23", SNAP, "DFF@2026-09-17", at(SS, "DFF", "2026-09-17"), 3.88, 2)
for i, (ym, rv, nd) in enumerate([("2025-11", 0.478, 3), ("2025-12", 0.557, 3), ("2026-04", 0.727, 3),
                                  ("2026-07", 0.978, 3), ("2026-08", 0.977, 3), ("2026-09", 1.043, 3),
                                  ("2026-10", 1.227, 3)]):
    P.add("P%02d" % (24 + i), SNAP, "JP_POLICY_RATE@%s" % ym, mv(SS, "JP_POLICY_RATE", ym), rv, nd)
j7, j10 = mv(SS, "JP_POLICY_RATE", "2026-07"), mv(SS, "JP_POLICY_RATE", "2026-10")
P.add("P31", SNAP, "JP_POLICY_RATE 三个月净变动(bp)=(10月-7月)*100", bp(j7, j10), 25, 0)
j11 = mv(SS, "JP_POLICY_RATE", "2025-11"); j12 = mv(SS, "JP_POLICY_RATE", "2025-12")
P.add("P32", SNAP, "JP_POLICY_RATE 近12个月净变动(bp)", bp(j11, j10), 75, 0)
P.add("P33", SNAP, "JP_POLICY_RATE 自窗内首观测起算(bp)", bp(j12, j10), 67, 0)
jc = changes(SS, "JP_POLICY_RATE", "2025-11-24", CUT)
P.addb("P34", SNAP, "JP_POLICY_RATE 12月窗变动点=6 个且幅度=[8,17,11,14,7,18]", len(jc) == 6 and [round(bp(c[2], c[3])) for c in jc] == [8, 17, 11, 14, 7, 18], str([(c[0], round(bp(c[2], c[3]))) for c in jc]))
P.add("P35", SNAP, "JP_POLICY_RATE 2026-07 - 2026-04 (pp)", mv(SS, "JP_POLICY_RATE", "2026-07") - mv(SS, "JP_POLICY_RATE", "2026-04"), 0.251, 3)
# 日历实录
ents = cal["entries"]
def find(sub):
    return [e for e in ents if sub in json.dumps(e, ensure_ascii=False)]
boj = [e for e in ents if "BOJ" in json.dumps(e, ensure_ascii=False)]
P.addb("P36", "calendar.entries[*]", "存在日本央行 2026-09 目标条目 (决议 2026-09-18)", any("2026-09-18" in json.dumps(e, ensure_ascii=False) and "TARGET" in json.dumps(e, ensure_ascii=False) for e in boj), "ids=" + str([e.get("id") or e.get("entry_id") for e in boj]))
P.addb("P37", "calendar.entries[*]", "生效 2026-09-24", any("2026-09-24" in json.dumps(e, ensure_ascii=False) for e in boj))
P.addb("P38", "calendar.entries[*]", "目标水平 1.25", any("1.25" in json.dumps(e, ensure_ascii=False) for e in boj))
mt = [e for e in boj if "MAINT" in json.dumps(e, ensure_ascii=False)]
P.addb("P39", "calendar.entries[*]", "2026-10-30 维持条目", any("2026-10-30" in json.dumps(e, ensure_ascii=False) for e in mt), "ids=" + str([e.get("id") or e.get("entry_id") for e in mt]))
P.addb("P40", "calendar.entries[*]", "维持条目无生效日", all(v in (None, "", []) for e in mt for k, v in e.items() if "effect" in k.lower()))
P.adds("P41", "datetime", "2026-09-16 星期", wd("2026-09-16"), "Wednesday")
P.adds("P42", "datetime", "2026-09-18 星期", wd("2026-09-18"), "Friday")
P.addb("P43", "datetime", "两决议同一 ISO 周", dt.date.fromisoformat("2026-09-16").isocalendar()[1] == dt.date.fromisoformat("2026-09-18").isocalendar()[1])
P.add("P44", "datetime", "两决议相隔天数", days("2026-09-16", "2026-09-18"), 2, 0)
# 中国
l0 = at_or_before(SS, "CN_LPR_1Y", ANC); l1 = at_or_before(SS, "CN_LPR_1Y", CUT)
P.adds("P45", SNAP, "CN_LPR_1Y 锚 obs", l0[0], "2026-08-20")
P.add("P46", SNAP, "CN_LPR_1Y@2026-08-20", l0[1], 3.0, 2)
P.adds("P47", SNAP, "CN_LPR_1Y 最新 obs", l1[0], "2026-11-20")
P.add("P48", SNAP, "CN_LPR_1Y@2026-11-20", l1[1], 3.0, 2)
P.adds("P49", SNAP, "CN_LPR_1Y 序列末观测", last(SS, "CN_LPR_1Y")[0], "2026-11-20")
midv = [v for d, v in series(SS, "CN_LPR_1Y") if "2026-08-20" <= d <= "2026-11-20"]
P.addb("P50", SNAP, "CN_LPR_1Y 2026-08-20..2026-11-20 全部观测均为 3.0 (n=%d)" % len(midv), all(abs(v - 3.0) < 1e-9 for v in midv))
lpr = find("RC-CN-LPR-2026M11")
P.addb("P51", "calendar.entries[RC-CN-LPR-2026M11]", "日期 2026-11-20 / 09:00", len(lpr) == 1 and "2026-11-20" in json.dumps(lpr[0], ensure_ascii=False) and "09:00" in json.dumps(lpr[0], ensure_ascii=False), json.dumps(lpr[0], ensure_ascii=False)[:300] if lpr else "absent")
P.addb("P52", "calendar.entries", "无 2026-08 LPR 实录条目(锚发布日属官方惯例)", not any("LPR" in json.dumps(e, ensure_ascii=False) and "2026-08-20" in json.dumps(e, ensure_ascii=False) for e in ents), str([e.get("id") or e.get("entry_id") for e in ents if "LPR" in json.dumps(e, ensure_ascii=False)]))
o0 = at_or_before(SS, "CN_OMO_7D", ANC); o1 = last(SS, "CN_OMO_7D")
P.adds("P53", SNAP, "CN_OMO_7D 锚 obs", o0[0], "2026-08-21")
P.add("P54", SNAP, "CN_OMO_7D@2026-08-21", o0[1], 1.4, 2)
P.adds("P55", SNAP, "CN_OMO_7D 末观测", o1[0], "2026-10-30")
P.add("P56", SNAP, "CN_OMO_7D@2026-10-30", o1[1], 1.4, 2)
P.add("P57", SNAP, "CN_OMO_7D 末观测滞后天数(=2026-11-23-末观测)", days(o1[0], CUT), 24, 0)
P.addb("P58", SNAP, "CN_OMO_7D 2026-08-21 之后全部观测=1.4 (n=%d)" % sum(1 for d, v in series(SS, "CN_OMO_7D") if d >= "2026-08-21"), all(abs(v - 1.4) < 1e-9 for d, v in series(SS, "CN_OMO_7D") if d >= "2026-08-21"))
ov = series(SS, "CN_POLICY_OVERNIGHT")
P.adds("P59", SNAP, "CN_POLICY_OVERNIGHT 首观测", ov[0][0], "2026-11-02")
P.adds("P60", SNAP, "CN_POLICY_OVERNIGHT 末观测", ov[-1][0], "2026-11-23")
P.add("P61", SNAP, "CN_POLICY_OVERNIGHT@末观测", ov[-1][1], 1.25, 2)
P.addb("P62", SNAP, "CN_POLICY_OVERNIGHT 在 2026-08-23 前无观测", all(d > ANC for d, v in ov), "n=%d" % len(ov))
for i, m in enumerate(["EA_REAL_GDP_YOY", "EA_HICP_YOY", "ECB_MRO", "ECB_DFR", "BUND_10Y", "BUND_2Y", "JP_POLICY_TARGET"]):
    P.addb("P%02d" % (63 + i), SNAP, "series_store 无 %s" % m, m not in SS)
ids = [m.get("metric_id") for m in reg["metrics"]]
P.addb("P70", "registry.metrics[*].metric_id", "注册表无 JP_POLICY_TARGET", "JP_POLICY_TARGET" not in ids)
_ids = [str(e.get("id") or e.get("entry_id")) for e in ents]
_kinds = sorted(set(str(e.get("kind")) for e in ents))
P.addb("P71", "calendar.entries[*].id/kind", "冻结日历无美国政策条目、无 FOMC 纪要条目(条目 id 仅 2025SHUTDOWN 数据发布/EA-HICP/JP-BOJ/CN-LPR)", not any(("FOMC" in i) or ("FED" in i.upper()) or ("POLICY" in i.upper()) for i in _ids), "ids=" + str(_ids) + " kinds=" + str(_kinds))
pdf = rp_policy = rep["research_plan"]["policy_doc_facts"]
P.addb("P72", "report.json research_plan.policy_doc_facts", "FOMC-MINUTES-2026-10 发布 2026-11-18, basis=user_directive", any((x.get("doc_id") == "FOMC-MINUTES-2026-10") and x.get("published_on") == "2026-11-18" and x.get("basis") == "user_directive" for x in pdf))

# ---------- 能源面 (C1 竞争解释一 / quality_gate_notes) ----------
w0 = at_or_before(SS, "WTI_F", ANC)
P.adds("E01", SNAP, "WTI_F 锚 obs", w0[0], "2026-08-21")
P.add("E02", SNAP, "WTI_F@2026-08-21", w0[1], 87.06, 2)
w1 = at(SS, "WTI_F", "2026-10-30"); w2 = at(SS, "WTI_F", CUT)
P.add("E03", SNAP, "WTI_F@2026-10-30", w1, 104.12, 2)
P.add("E04", SNAP, "WTI_F 10-30 vs 锚 %", pct(w0[1], w1), 19.60, 2)
P.add("E05", SNAP, "WTI_F@2026-11-23", w2, 82.02, 2)
P.add("E06", SNAP, "WTI_F 11-23 vs 锚 %", pct(w0[1], w2), -5.79, 2)
P.add("E07", SNAP, "WTI_F 11-23 vs 10-30 %", pct(w1, w2), -21.23, 2)
b0 = at_or_before(SS, "BRENT_F", ANC); b1 = at(SS, "BRENT_F", "2026-10-30"); b2 = at(SS, "BRENT_F", CUT)
P.add("E08", SNAP, "BRENT_F 锚 obs %s" % b0[0], b0[1], 94.39, 2)
P.add("E09", SNAP, "BRENT_F@2026-10-30", b1, 117.64, 2)
P.add("E10", SNAP, "BRENT_F 10-30 vs 锚 %", pct(b0[1], b1), 24.63, 2)
P.add("E11", SNAP, "BRENT_F@2026-11-23", b2, 88.19, 2)
P.add("E12", SNAP, "BRENT_F 11-23 vs 锚 %", pct(b0[1], b2), -6.57, 2)
P.add("E13", SNAP, "BRENT_F 11-23 vs 10-30 %", pct(b1, b2), -25.03, 2)
m8, m10 = mv(SS, "WTI_SPOT_M", "2026-08"), mv(SS, "WTI_SPOT_M", "2026-10")
P.add("E14", SNAP, "WTI_SPOT_M@2026-08", m8, 83.9, 1)
P.add("E15", SNAP, "WTI_SPOT_M@2026-10", m10, 102.07, 2)
P.add("E16", SNAP, "WTI_SPOT_M 10月 vs 8月 %", pct(m8, m10), 21.66, 2)
def mean(mid, ym):
    xs = [v for d, v in series(SS, mid) if d[:7] == ym]
    return sum(xs) / len(xs)
P.add("E17", SNAP, "WTI_F 2026-08 自然月均值", mean("WTI_F", "2026-08"), 82.45, 2)
P.add("E18", SNAP, "WTI_F 2026-10 自然月均值", mean("WTI_F", "2026-10"), 96.94, 2)
w16, w18 = at(SS, "WTI_F", "2026-09-16"), at(SS, "WTI_F", "2026-09-18")
P.add("E19", SNAP, "WTI_F@2026-09-16", w16, 102.43, 2)
P.add("E20", SNAP, "WTI_F 09-16 vs 锚 %", pct(w0[1], w16), 17.65, 2)
P.add("E21", SNAP, "WTI_F@2026-09-18", w18, 100.30, 2)
P.add("E22", SNAP, "WTI_F 09-18 vs 锚 %", pct(w0[1], w18), 15.21, 2)
aut = [(d, v) for d, v in series(SS, "WTI_F") if "2026-09-01" <= d <= "2026-10-31"]
P.addb("E23", SNAP, "WTI_F 2026-09-01..2026-10-31 全部观测 > 锚 87.06 (n=%d, min=%.2f)" % (len(aut), min(v for d, v in aut)), min(v for d, v in aut) > w0[1])
late = [(d, v) for d, v in series(SS, "WTI_F") if d >= "2026-11-02"]
first_below = [d for d, v in late if v < w0[1]][0]
P.adds("E24", SNAP, "WTI_F 11-02 起首个跌破锚的观测日", first_below, "2026-11-09")
P.addb("E25", SNAP, "WTI_F 2026-11-09..11-23 全部 < 锚(受审稿『11-09 起再度跌破该锚』的字面持续性; 实测 11 个观测中 9 个低于锚, 11-12=88.74、11-13=88.56 回到锚上方)", all(v < w0[1] for d, v in late if d >= first_below))
P.addb("E29", SNAP, "WTI_F 2026-09-01..2026-10-31 观测全部 > 锚(受审稿『期货 9 月初至 10 月底的观测全部高于三个月前锚』)", all(v > w0[1] for d, v in series(SS, "WTI_F") if "2026-09-01" <= d <= "2026-10-31"), "观测数 %d, 最低 %.2f" % (len([1 for d, v in series(SS, "WTI_F") if "2026-09-01" <= d <= "2026-10-31"]), min(v for d, v in series(SS, "WTI_F") if "2026-09-01" <= d <= "2026-10-31")))
P.addb("E26", SNAP, "WTI_F 2026-11-02..11-06(跌破前) 全部 > 锚", all(v > w0[1] for d, v in late if d < first_below), str([(d, v) for d, v in late if d < first_below]))
dip = [(d, v) for d, v in series(SS, "WTI_F") if ANC <= d < "2026-09-01" and v < w0[1]]
P.addb("E27", SNAP, "WTI_F 8 月底(锚后至 8-31)有短暂低于锚的观测", len(dip) > 0, str(dip))
P.adds("E28", SNAP, "WTI_SPOT_M 末观测月", last(SS, "WTI_SPOT_M")[0][:7], "2026-10")
P.save(outdir, "pts_a.json")
