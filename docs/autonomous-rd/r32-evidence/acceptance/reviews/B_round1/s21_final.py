#!/usr/bin/python3 -I
"""席位定稿生成器 s21: 汇总中间表与席位叙述, 一次性写出 PROSE-round1.md 与 VERDICT-round1.json.

用法: /usr/bin/python3 -I s21_final.py <dry|final> <席位目录> <运行目录> <快照> <CODE_VERSION.json>
dry  : 只写 x_PROSE_draft.md / x_VERDICT_draft.json, 打印自检结果(针脚命中/活算核对/数字回贴/原句与改句摘录);
final: 自检全部通过才写出两件正式产出(已存在则拒绝覆盖), 写出后回读校验.
自写脚本, 只读本席目录与规程列明的只读面.
"""
import glob
import hashlib
import json
import os
import re
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from seatlib import Store, load_json  # noqa: E402

MODE, SEAT, RUN, SNAP, CODEVER = sys.argv[1:6]
assert MODE in ("dry", "final")
OUT_PROSE = os.path.join(SEAT, "PROSE-round1.md")
OUT_VERDICT = os.path.join(SEAT, "VERDICT-round1.json")
if MODE == "final":
    for p in (OUT_PROSE, OUT_VERDICT):
        if os.path.exists(p):
            sys.exit("拒绝覆盖(产出只写一次): " + p)


def rd(name):
    return open(os.path.join(SEAT, name), encoding="utf-8").read()


aj = json.load(open(os.path.join(RUN, "agent_judgment.json"), encoding="utf-8"))
rep = json.load(open(os.path.join(RUN, "report.json"), encoding="utf-8"))
snap = load_json(SNAP)
ev = load_json(os.path.join(RUN, "evidence_index.json"))
cv = load_json(CODEVER)
cal = load_json(os.path.join(RUN, "root_overlay/config/release_calendar.json"))
S = Store(snap)
problems = []
PUNCT = {"，": ",", "（": "(", "）": ")", "；": ";", "：": ":", "％": "%"}


def nmap(s):
    out, idx = [], []
    for i, ch in enumerate(s):
        if ch.isspace():
            continue
        out.append(PUNCT.get(ch, ch))
        idx.append(i)
    return "".join(out), idx


def find_in(s, needle):
    """去空白、全角标点归一后的子串定位, 返回原串上的 [起, 止)."""
    n, idx = nmap(s)
    nn = nmap(needle)[0]
    k = n.find(nn) if nn else -1
    if k < 0:
        return None
    return idx[k], idx[k + len(nn) - 1] + 1


def walk(o, path="$"):
    if isinstance(o, str):
        yield path, o
    elif isinstance(o, dict):
        for k, v in o.items():
            yield from walk(v, f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, f"{path}[{i}]")


def locate(needle, exact=False):
    res = []
    for p, s in walk(aj):
        if exact:
            if nmap(s)[0] == nmap(needle)[0]:
                res.append((p, s, 0, len(s)))
        else:
            h = find_in(s, needle)
            if h:
                res.append((p, s, h[0], h[1]))
    return res


def piece_span(s, a, b):
    """含 [a,b) 的整句(以句号分隔)."""
    ps = s.rfind("。", 0, a)
    ps = 0 if ps < 0 else ps + 1
    pe = s.find("。", b)
    pe = len(s) if pe < 0 else pe + 1
    return ps, pe


def narrow(s, ps, pe, a, b):
    """整句过长时用分号收窄到含 [a,b) 的子句, 收窄处加省略号."""
    qs = max(s.rfind("；", ps, a), s.rfind(";", ps, a))
    rs = [x for x in (s.find("；", b, pe), s.find(";", b, pe)) if x >= 0]
    nps, npe = (ps if qs < 0 else qs + 1), (min(rs) if rs else pe)
    return (("…" if nps > ps else "") + s[nps:npe].strip() + ("…" if npe < pe else "")).strip()


items = []
for spec in load_json(os.path.join(SEAT, "x_items.json")):
    origs, fixes, paths = [], [], []
    for loc in spec.get("locs", []):
        hits = locate(loc["needle"], loc.get("exact", False))
        if not hits:
            problems.append(f"{spec['id']}: 未找到针脚 {loc['needle']!r}")
            continue
        p, s, a, b = hits[0]
        paths.append(p)
        ps, pe = piece_span(s, a, b)
        long = pe - ps > 300
        origs.append(narrow(s, ps, pe, a, b) if long else s[ps:pe].strip())
        if loc.get("replace"):
            s2, span = s, (a, b)
            for frm, to in loc["replace"]:
                h = find_in(s2, frm)
                if not h:
                    problems.append(f"{spec['id']}: 未找到替换源 {frm!r}")
                    continue
                s2 = s2[:h[0]] + to + s2[h[1]:]
                h2 = find_in(s2, to)
                if h2:
                    span = h2
            pe2 = pe + len(s2) - len(s)
            fixes.append(narrow(s2, ps, pe2, span[0], span[1]) if long else s2[ps:pe2].strip())
        else:
            fixes.append(spec.get("fix", ""))
    items.append({"severity": spec["severity"], "where": spec["where"] + " 〔" + "; ".join(paths) + "〕", "note": spec["note"],
                  "original": " ‖ ".join(origs), "fix": " ‖ ".join(fixes), "id": spec["id"]})

agg = load_json(os.path.join(SEAT, "x_aggregate.json"))
P, N, B, M, PR = agg["recompute_points"], agg["numeric_points"], agg["bool_points"], agg["recompute_mismatches"], agg["probes"]
H = P - M - agg["undetermined"]
n_major = sum(1 for i in items if i["severity"] == "MAJOR")
n_minor = sum(1 for i in items if i["severity"] == "MINOR")
n_nit = sum(1 for i in items if i["severity"] == "NIT")


def expect(key, got, want):
    """活算值记入 live; 与叙述所引不一致则记问题."""
    live[key] = got
    if got != want:
        problems.append(f"活算不符 {key}: 直算 {got!r} ≠ 叙述 {want!r}")


# ---- 活算核对(定稿前再从只读面直算一遍叙述所引的关键数) ----
live = {"hit": H}
yms = ["2025-11", "2025-12", "2026-01", "2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10"]
mv = {y: S.mval("JP_POLICY_RATE", y) for y in yms}
steps = [mv["2025-12"] - mv["2025-11"], mv["2026-01"] - mv["2025-12"], mv["2026-06"] - mv["2026-05"], mv["2026-07"] - mv["2026-06"], mv["2026-09"] - mv["2026-08"], mv["2026-10"] - mv["2026-09"]]
expect("six_step_sum_bp", round(sum(steps) * 100, 1), 75.1)
expect("net_bp", round((mv["2026-10"] - mv["2025-11"]) * 100, 1), 74.9)
expect("since_first_obs_bp", round((mv["2026-10"] - mv["2025-12"]) * 100, 1), 67.0)
expect("band_exact", (round(mv["2026-10"] - 0.03, 3), round(mv["2026-10"] + 0.03, 3)), (1.197, 1.257))
jp = [e for e in cal.get("entries", []) if e.get("entry_id") == "RC-JP-BOJ-TARGET-2026-09"]
expect("jp_target", (jp[0].get("decision_date"), jp[0].get("effective_on"), jp[0].get("target_value")) if jp else None, ("2026-09-18", "2026-09-24", 1.25))
expect("target_gap", round(1.25 - mv["2026-10"], 3), 0.023)
cands = [c.get("metric_id") for c in rep["research_plan"]["turning_candidates"]["candidates"]]
expect("candidates", cands, ["CPI", "EA_HICP_YOY", "INDPRO", "CORE_CPI", "JP_POLICY_RATE", "CORE_PCE", "UNEMPLOYMENT"])
ev_ids = {e.get("metric_id") for e in ev} if isinstance(ev, list) else set()
for mid in ("CURVE_2S10S", "UST_2Y", "UST_5Y", "UST_10Y", "UST_30Y", "TIPS_5Y", "TIPS_10Y", "DAX", "BEI_10Y"):
    if mid not in ev_ids:
        problems.append(f"证据索引内无 {mid}(改句引用了它)")


def bp(mid, d0, d1):
    return round((S.le(mid, d1)[1] - S.le(mid, d0)[1]) * 100)


rate_ids = ["UST_2Y", "UST_5Y", "UST_10Y", "UST_30Y", "TIPS_5Y", "TIPS_10Y"]
expect("rates_3m_bp", [bp(m, "2026-08-19", "2026-11-19") for m in rate_ids], [57, 51, 39, 21, 57, 53])
expect("rates_12m_bp", [bp(m, "2025-11-19", "2026-11-19") for m in rate_ids], [118, 115, 91, 65, 129, 102])
expect("curve_3m", (S.le("CURVE_2S10S", "2026-08-19")[1], S.le("CURVE_2S10S", "2026-11-19")[1]), (0.46, 0.28))
expect("curve_12m", (S.le("CURVE_2S10S", "2025-11-19")[1], S.le("CURVE_2S10S", "2026-11-19")[1]), (0.55, 0.28))
dax = [r for r in rep["research_plan"]["asset_moves"].get("rows", []) if r.get("metric_id") == "DAX"]
expect("dax_1m_pct", round(dax[0].get("chg_pct", 0), 2) if dax else None, 0.11)
cac = (S.le("CAC40", "2026-10-23")[1], S.le("CAC40", "2026-11-23")[1])
expect("cac_1m_pct", round((cac[1] / cac[0] - 1) * 100, 2), 3.08)
# 汇率: 引擎三个月窗端点与日历锚读法
for mid, w in (("USDJPY", (159.550003, 159.347, 158.882996, 0.29)), ("EURUSD", (1.157943, 1.093972, 1.168784, -6.4))):
    a0, a1 = S.le(mid, "2026-08-19")[1], S.exact(mid, "2026-11-23")
    kd, kv = S.le(mid, "2026-08-23")
    expect(mid + "_3m", (round(a0, 6), round(a1, 6), round((a1 / a0 - 1) * 100, 2)), w[:2] + (round((w[1] / w[0] - 1) * 100, 2),))
    expect(mid + "_anchor", (kd, round(kv, 6), round((a1 / kv - 1) * 100, 2)), ("2026-08-21", w[2], w[3]))
k6 = [S.exact("USDJPY", d) for d in ("2026-09-18", "2026-09-25")]
expect("usdjpy_0918_0925", (round(k6[0], 6), round(k6[1], 6), round((k6[1] / k6[0] - 1) * 100, 2)), (156.128998, 158.811005, 1.72))
# 油价
PUBDAYS = ["2026-10-13", "2026-10-16", "2026-10-30", "2026-11-13", "2026-11-16"]
bd, bv = S.series("BRENT_F")
win = [(dd, x) for dd, x in zip(bd, bv) if "2026-08-19" <= dd <= "2026-11-23" and x is not None]
mx = max(win, key=lambda t: t[1])
expect("oil_window", (len(win), sum(1 for _, x in win if x >= 91.62), round(mx[1], 2), mx[0], round(S.exact("BRENT_F", "2026-10-23"), 2)), (68, 61, 117.64, "2026-10-30", 116.72))
expect("oil_pubdays", [round(S.exact("BRENT_F", d), 2) for d in PUBDAYS], [105.69, 109.86, 117.64, 95.84, 92.44])
rng = [(dd, x) for dd, x in zip(bd, bv) if "2026-10-13" <= dd <= "2026-11-16" and x is not None]
mn = min(rng, key=lambda t: t[1])
expect("oil_range_min", (round(mn[1], 2), mn[0], len(rng)), (91.49, "2026-11-10", 25))


def mm(mid, ym):
    d, v = S.series(mid)
    xs = [x for dd, x in zip(d, v) if dd.startswith(ym) and x is not None]
    return round(sum(xs) / len(xs), 2) if xs else None


mo = {y: mm("BRENT_F", y) for y in ("2025-10", "2026-07", "2026-09", "2026-10")}
expect("oil_month_means", [mo["2026-07"], mo["2026-09"], mo["2026-10"], mo["2025-10"], round((mo["2026-10"] / mo["2025-10"] - 1) * 100, 1)], [84.51, 102.26, 108.34, 63.95, 69.4])
# 欧元区对美国 CPI 同比: 「2023-09 以来首个高于美国的可比月份」
hist = []
y, m = 2022, 7
while (y, m) <= (2026, 9):
    ym = f"{y}-{m:02d}"
    ea, us = S.mval("EA_HICP_YOY", ym), S.yoy("CPI", ym)[0]
    hist.append((ym, None if (ea is None or us is None) else ea > us))
    m += 1
    if m == 13:
        y, m = y + 1, 1
expect("ea_gt_us_2022-07..2023-09", [g for _, g in hist if _ <= "2023-09"], [True] * 15)
expect("ea_gt_us_2023-10..2026-08", [g for _, g in hist if "2023-10" <= _ <= "2026-08"], [False] * 24 + [None] + [False] * 10)
expect("ea_gt_us_2026-09", hist[-1], ("2026-09", True))
expect("ea_vals", [S.mval("EA_HICP_YOY", x) for x in ("2026-07", "2026-08", "2026-09", "2026-10")], [2.9, 3.2, 3.8, 4.0])
expect("us_cpi_yoy_2026-07_09", (round(S.yoy("CPI", "2026-07")[0], 4), round(S.yoy("CPI", "2026-09")[0], 4)), (3.3039, 3.7173))
expect("stale_lag_days", ((date(2026, 11, 23) - date(2026, 9, 1)).days, (date(2026, 11, 23) - date(2026, 7, 1)).days, round(83 / 60, 1), round(145 / 120, 1)), (83, 145, 1.4, 1.2))
miss = {}
for mid in ("CPI", "CORE_CPI", "UNEMPLOYMENT"):
    ds = set(S.series(mid)[0])
    miss[mid] = [f"{y}-{m:02d}" for y in range(2016, 2027) for m in range(1, 13) if "2016-11" <= f"{y}-{m:02d}" <= "2026-10" and f"{y}-{m:02d}-01" not in ds]
expect("missing_months", miss, {"CPI": ["2025-10"], "CORE_CPI": ["2025-10"], "UNEMPLOYMENT": ["2025-10"]})
crows = [r for r in load_json(os.path.join(SEAT, "points_16_counter.json"))["rows"] if r.get("kind") == "probe"]
expect("counter_probe_count", len(crows), 33)
map_lines = [ln.strip().lstrip("> ").strip() for ln in open(os.path.join(RUN, "MAP_REPORT.md"), encoding="utf-8").read().splitlines() if "5/5组ok" in "".join(ln.split())]
if not map_lines:
    problems.append("MAP_REPORT.md 未复核到「5/5组ok」汇总行")
git_head = cv.get("git_head")
if not (git_head and git_head == rep.get("run", {}).get("git_head")):
    problems.append(f"印章不一致: {git_head} vs {rep.get('run', {}).get('git_head')}")
if M != 1 or agg["undetermined"] != 0 or not agg["mismatch_details"][0].split(" | ")[1].startswith("F3"):
    problems.append(f"汇总不符: 偏离 {M} 未定 {agg['undetermined']} {agg['mismatch_details']}")

# ---- 文本组装 ----
cand_txt = "、".join(str(c) for c in cands)
miss_txt = "序列缺采复核: " + ";".join(f"{k} 在 2016-11 至 2026-10 间缺 " + ("、".join(v) if v else "无") + " 的月度观测" for k, v in miss.items()) + \
    "。受审稿披露的「美国 CPI 与核心 CPI 2026-10 同比缺 2025-10 基期」属实(points_03);失业率不涉同比,无影响。"
map_txt = ("读者报告 MAP_REPORT.md 的锚格汇总行写「" + map_lines[0] + "」,而日本政策维的 JP_POLICY_TARGET 在引擎面为维度缺口"
           "(report.json:research_plan.dimension_gaps 恰一条 registry_absent;同报告另有缺口披露段)。") if map_lines else ""
fills = {"{{POINTS}}": str(P), "{{NUM}}": str(N), "{{BOOL}}": str(B), "{{HIT}}": str(H), "{{MIS}}": str(M), "{{PROBES}}": str(PR), "{{N_MAJOR}}": str(n_major), "{{N_MINOR}}": str(n_minor), "{{N_NIT}}": str(n_nit),
         "{{CAND_METRICS}}": cand_txt, "{{MAP_OK_LINE}}": map_txt, "{{MISSING_MONTHS}}": miss_txt}


def fill(text):
    for k, v in fills.items():
        text = text.replace(k, v)
    if "{{" in text:
        problems.append("未替换的占位符: " + re.findall(r"\{\{\w+\}\}", text)[0])
    return text


def render_items(sev):
    out = []
    for i in items:
        if i["severity"] != sev:
            continue
        s = f"- **{i['id']}** 位置: {i['where']}\n  - 问题: {i['note']}"
        if i["original"]:
            s += f"\n  - 原句: 「{i['original']}」"
        if i["fix"]:
            s += f"\n  - 建议改句: 「{i['fix']}」"
        out.append(s)
    return "\n".join(out)


na, nb, nc = rd("x_narrative_a.md"), rd("x_narrative_b.md"), rd("x_narrative_c.md")
att = []
for line in nb.splitlines():
    if line.startswith("- 攻击 "):
        body = line[2:].strip()
        if " ==> " in body:
            a, r = body.split(" ==> ", 1)
            att.append(re.sub(r"^攻击 ", "反方攻击 ", a.strip()) + "→" + r.strip())
        else:
            att.append(re.sub(r"^攻击 ", "反方攻击 ", body))
cover = ("覆盖对照: C1=攻击 1、2;C2=攻击 3;C3=攻击 4、5;M1-JP-RATE-PATH 第 1 环=攻击 4(台阶数值与三口径,另见攻击 5)、第 2 环=攻击 6、第 3 环=攻击 7;"
         "传导链 CH-INFL-RATES-RISKOFF 第 1 至 3 环=攻击 8、9、10;两情景=攻击 11;历史信息=攻击 12。")
head3 = "## 三、反方攻击记录(每条 L3 矛盾陈述与每条机制链至少一次)\n"
if nb.count(head3) != 1:
    problems.append("x_narrative_b.md 的第三节标题未找到")
else:
    nb = nb.replace(head3, head3 + "\n" + cover + "\n", 1)
nc = nc.replace("{{ITEMS_MAJOR}}", render_items("MAJOR")).replace("{{ITEMS_MINOR}}", render_items("MINOR")).replace("{{ITEMS_NIT}}", render_items("NIT"))
nc = fill(nc)

verdict = "REVISE" if (n_major > 0) else "UPHELD"
if verdict != "REVISE" or n_major != 1:
    problems.append(f"裁决前提变化: MAJOR {n_major} 条(verdict {verdict}); 本稿 notes 与叙述按恰一条 MAJOR-1 写就")
notes = (f"独立零上下文席位对印章 {git_head} 上工单 B 研判稿(agent_judgment.json 全文与读者报告判断文字)只读复算: "
         f"复算 {P} 点(数值直算 {N}、条件核对 {B}),命中 {H},偏离 {M};另留 {PR} 条口径敏感性探针不计点。"
         "唯一偏离即唯一 MAJOR(MAJOR-1): quality_gate_notes[3] 末句的证据引用自计数「共 19 条(矛盾陈述 10、机制链 4、情景 5)」,逐条直数为 20 条"
         "(矛盾陈述 6+3+2=11、机制链 1+1+2=4、情景 5),按第 5 节「数字错」计为 MAJOR,必修改句只动这两个计数;该句是不进渲染的程序性自述,不涉任何结论数字,"
         "其所证明的断言(全部引用解析到本轮证据索引)经逐条核对为真。"
         "除此之外未见 MAJOR 情形: 研究截止日与发布纪律、9 格×2 锚、全部同比与基期(美国 CPI 与核心 CPI 2026-10 同比如实标缺 2025-10 基期)、"
         "日本央行决议 2026-09-18 与生效 2026-09-24、距截止日按决议日 66 天与按生效日 60 天、月均台阶与 +75bp/+67bp、三利率分解三窗恒等、资产月窗、油价对账、"
         "转折候选窗、情景触发与证伪线对截止日读数的相容性、契约 STALE 与 Gate A 缺口披露,均与冻结快照、冻结日历、report.json 一致。"
         f"六查与反方攻击 {len(att)} 次(C1、C2、C3、M1 三环、传导链三环、两情景、历史信息): 未见稻草人解释、未披露的反向事实、结论超出证据而无标注或不可观测的证伪条件;"
         "两处同步主张与引擎点值面及转折候选面一致。"
         f"MINOR {n_minor} 条(油价发布日区间的读法、两处「三个月」未写窗启日、美国走位段缺契约 STALE 滞后披露、风险收缩未注明欧元区股指未同跌、"
         f"「本环实无可区分指标」过强、C3 并列解释缺区分观测与自身失效条件)与 NIT {n_nit} 条如实列出。按「存在 MAJOR → REVISE」裁决 REVISE,必修仅 MAJOR-1 一句。")

# 数字回贴: 叙述与条目里的每个数字须在本席中间表、受审稿文本或定稿活算值里出现过(字符串相同或数值相等)
tok = re.compile(r"\d+(?:\.\d+)?")
pool_txt = json.dumps(agg, ensure_ascii=False) + json.dumps(live, ensure_ascii=False) + json.dumps(aj, ensure_ascii=False)
for f in glob.glob(os.path.join(SEAT, "points_*.json")):
    pool_txt += open(f, encoding="utf-8").read()
pool_tok = set(tok.findall(pool_txt))
pool_num = [float(t) for t in pool_tok]
typed = [x.replace(str(git_head), "") for x in [na, nb, nc, notes] + [json.dumps(i, ensure_ascii=False) for i in items]]


def backed(t):
    if t in pool_tok:
        return True
    x = float(t)
    return any(abs(x - y) <= 1e-9 * max(1.0, abs(x)) for y in pool_num)


unmatched = sorted({t for x in typed for t in tok.findall(x) if not backed(t)})
if unmatched:
    problems.append(f"叙述中有数字未在中间表/受审稿/活算值中出现: {unmatched}")

verd = {"seat": "semantic-audit-seat", "reviewer": "independent-zero-context-seat-r32-b-round1", "verdict": verdict, "overall": verdict, "notes": notes,
        "items": [{k: (f"[{i['id']}] " + i["note"] if k == "note" else i[k]) for k in ("severity", "where", "note", "original", "fix")} for i in items],
        "must_fix": [f"{i['id']} | {i['where']}: 原句「{i['original']}」→ 改句「{i['fix']}」" for i in items if i["severity"] == "MAJOR"],
        "counterexamples_sought": att, "recompute_points": P, "recompute_mismatches": M, "mismatch_details": agg["mismatch_details"], "audited_at": "2026-11-24"}

ga = snap.get("gate_a") or {}
ga_status = ga.get("status") or "DEGRADED"
fi = rep.get("run", {}).get("frozen_inputs") or {}
fi_txt = "; ".join(f"{k} {v}" for k, v in fi.items())
as_of = str(snap.get("research_as_of", ""))
header = (f"# Audit-R32 独立语义审查席复算记录(工单 B,Round-1,零上下文)\n\n"
          f"- 席位: independent-zero-context-seat-r32-b-round1(semantic-audit-seat)\n"
          f"- 审查日期: 2026-11-24\n"
          f"- 受审运行目录: `{RUN}`\n"
          f"- 代码印章: {git_head}(CODE_VERSION.json 的 git_head 与 report.json:run.git_head 一致)\n"
          f"- 冻结输入指纹(report.json:run.frozen_inputs): {fi_txt}\n"
          f"- 研究截止日: {as_of[:10]}(快照 research_as_of {as_of});Gate A={ga_status}\n"
          f"- 受审对象: agent_judgment.json 全文(schema {aj.get('schema_version')}: l3 / l4 / reader_map / quality_gate_notes / agent_declaration)与读者报告中的判断文字;"
          "MAP_REPORT.md、FULL_REPORT.md、report.md 为裁决缺席状态下的渲染\n"
          f"- 裁决: **{verdict}**;复算 {P} 点(数值直算 {N}、条件核对 {B}),命中 {H},偏离 {M};MAJOR {n_major} / MINOR {n_minor} / NIT {n_nit};探针 {PR} 条不计点\n"
          f"- 配套产出: VERDICT-round1.json;中间表 points_*.json 与脚本 s*.py、seatlib.py 同目录\n")
overview = ("## 一、复算总览\n\n" + rd("x_blocks.md") + "\n口径说明: 「数值直算」=从只读面(冻结快照 series_store、冻结日历、report.json 引擎面)直算出一个数,再与受审稿数字比对;"
            "「条件核对」=按规程第 3 节各条逐项核对的布尔条件(出处、发布纪律、口径分列、披露在场等)。同一数值在不同受审语句中各出现一次即各核一次。\n")
lists = ("## 九、复算清单(逐点: 出处键 / 直算值 / 受审稿值 / 一致与否)\n\n" + rd("x_table.md") + "\n### 口径敏感性探针(不计点)\n\n" + rd("x_table_probes.md") + "\n")
prose = header + "\n" + overview + "\n" + na + "\n" + nb + "\n" + nc + "\n" + lists
prose_json = json.dumps(verd, ensure_ascii=False, indent=1) + "\n"

print("MODE", MODE, "| verdict", verdict, "| points", P, f"({N}+{B})", "hit", H, "mismatch", M, "probes", PR, "| MAJOR/MINOR/NIT", n_major, n_minor, n_nit, "| attacks", len(att))
print("LIVE", json.dumps(live, ensure_ascii=False))
print("UNMATCHED_TOKENS", unmatched)
print("PROBLEMS", json.dumps(problems, ensure_ascii=False))
print("NOTES", notes)
print("MUST_FIX", json.dumps(verd["must_fix"], ensure_ascii=False))
print("SEV", [(i["severity"], i["id"]) for i in items])
if MODE == "dry":
    for i in items:
        print("---", i["severity"], i["id"], i["where"])
        print("  原句:", i["original"][:430])
        print("  改句:", i["fix"][:430])
    open(os.path.join(SEAT, "x_PROSE_draft.md"), "w", encoding="utf-8").write(prose)
    open(os.path.join(SEAT, "x_VERDICT_draft.json"), "w", encoding="utf-8").write(prose_json)
    print("DRAFT sizes", len(prose.encode("utf-8")), len(prose_json.encode("utf-8")))
    sys.exit(0)
if problems:
    sys.exit("自检未通过, 未写出正式产出: " + json.dumps(problems, ensure_ascii=False))
if len(att) < 12 or n_major != 1 or len(items) != 13:
    sys.exit("覆盖或裁决前提不成立, 未写出正式产出")
open(OUT_PROSE, "w", encoding="utf-8").write(prose)
open(OUT_VERDICT, "w", encoding="utf-8").write(prose_json)
back = json.load(open(OUT_VERDICT, encoding="utf-8"))
need = ["seat", "reviewer", "verdict", "overall", "notes", "items", "must_fix", "counterexamples_sought", "recompute_points", "recompute_mismatches", "mismatch_details", "audited_at"]
assert list(back.keys()) == need and back["verdict"] in ("UPHELD", "REVISE") and back["overall"] == back["verdict"]
assert all(list(x.keys()) == ["severity", "where", "note", "original", "fix"] for x in back["items"])
assert isinstance(back["recompute_points"], int) and isinstance(back["recompute_mismatches"], int) and isinstance(back["must_fix"], list) and isinstance(back["mismatch_details"], list)
for name in ("x_PROSE_draft.md", "x_VERDICT_draft.json"):
    p = os.path.join(SEAT, name)
    if os.path.exists(p):
        os.remove(p)
        print("REMOVED_STALE_DRAFT", p)
for p in (OUT_PROSE, OUT_VERDICT):
    b = open(p, "rb").read()
    b.decode("utf-8")
    print("WRITTEN", p, len(b), "sha256", hashlib.sha256(b).hexdigest())
