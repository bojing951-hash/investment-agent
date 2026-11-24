#!/usr/bin/python3
"""Seat recompute script -- Audit-R32 acceptance, work order C4, Round-1 (independent semantic review).

READ-ONLY with respect to every input. The only file it writes is the point table whose path is given
as the last argument (the seat's own output directory).

Usage:
  /usr/bin/python3 -I s05_recompute.py <snapshot.json> <release_calendar.json> <metric_registry.json> \
      <report.json> <agent_judgment.json> <evidence_index.json> <MAP_REPORT.md> <out_table.md>

Method: every number is computed independently from the frozen snapshot series_store, the frozen
calendar and the engine faces in report.json, then compared with the value stated in the audited
judgment (agent_judgment.json). No number is taken from memory or common knowledge.
Categories (protocol section 3): the circled items 1..15.
"""
import datetime as dt
import json
import re
import sys
from zoneinfo import ZoneInfo

PTS = []
EVID = []

CATS = {"1": "①", "2": "②", "3": "③", "4": "④", "5": "⑤", "6": "⑥", "7": "⑦", "8": "⑧", "9": "⑨",
        "10": "⑩", "11": "⑪", "12": "⑫", "13": "⑬", "14": "⑭", "15": "⑮", "ER": "证据引用", "RR": "读者报告"}


def jload(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def D(s):
    return dt.date(int(s[:4]), int(s[5:7]), int(s[8:10]))


def show(v):
    return json.dumps(v, ensure_ascii=False, default=str)


def same(a, b, tol):
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a is b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) <= tol
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(same(x, y, tol) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k], tol) for k in a)
    return a == b


def add(pid, cat, key, computed, reported, tol=5e-3, note=""):
    ok = same(computed, reported, tol)
    PTS.append({"id": pid, "cat": cat, "key": key, "computed": computed, "reported": reported,
                "ok": bool(ok), "note": note})
    return ok


def chk(pid, cat, key, fn, reported, tol=5e-3, note=""):
    """fn() computes the value; an exception becomes an ERR row (neither hit nor mismatch)."""
    try:
        computed = fn()
    except Exception as ex:
        PTS.append({"id": pid, "cat": cat, "key": key, "computed": "ERR %s: %s" % (type(ex).__name__, ex),
                    "reported": reported, "ok": None, "note": note})
        return False
    return add(pid, cat, key, computed, reported, tol, note)


def ev(key, value):
    EVID.append((key, value))


class Series(object):
    def __init__(self, ss):
        self.ss = ss

    def dates(self, m):
        return self.ss[m]["dates"]

    def vals(self, m):
        return self.ss[m]["values"]

    def at(self, m, day):
        d = self.dates(m)
        if day in d:
            return self.vals(m)[d.index(day)]
        return None

    def last_on_or_before(self, m, day):
        best = None
        for d, v in zip(self.dates(m), self.vals(m)):
            if d <= day:
                best = (d, v)
            else:
                break
        return best

    def monthly(self, m):
        return dict(zip(self.dates(m), self.vals(m)))

    def changes(self, m, a, b):
        out = []
        d, v = self.dates(m), self.vals(m)
        for i in range(1, len(d)):
            if a <= d[i] <= b and v[i] != v[i - 1]:
                out.append((d[i], v[i - 1], v[i]))
        return out

    def yoy(self, m, ym):
        """level / level(same month one year earlier) - 1, in percent; None when either is absent."""
        d = self.dates(m)
        y, mo = int(ym[:4]), int(ym[5:7])
        cur = "%04d-%02d-01" % (y, mo)
        base = "%04d-%02d-01" % (y - 1, mo)
        if cur not in d or base not in d:
            return None
        a = self.vals(m)[d.index(cur)]
        b = self.vals(m)[d.index(base)]
        if a is None or b is None:
            return None
        return (a / b - 1.0) * 100.0


def month_end(y, m):
    if m == 12:
        return dt.date(y, 12, 31)
    return dt.date(y, m + 1, 1) - dt.timedelta(days=1)


# Publication rules restated independently from the engine rule text (rule-based, not an official calendar).
PUB = {
    "CPI": ("me", 13), "CORE_CPI": ("me", 13), "UNEMPLOYMENT": ("me", 5), "INDPRO": ("me", 15),
    "CORE_PCE": ("me", 30), "JP_CPI_YOY": ("me", 20), "JP_POLICY_RATE": ("me", 5),
    "CN_CPI_YOY": ("me", 9), "CN_PPI_YOY": ("me", 9), "CN_PMI_MFG": ("me", -1),
    "JP_CPI_TOKYO_YOY": ("me", -1),
    "US_REAL_GDP": ("q", 29), "JP_REAL_GDP_YOY": ("q", 45),
    "DFF": ("d", 1), "DFEDTARU": ("d", 0), "CN_LPR_1Y": ("d", 0), "CN_OMO_7D": ("d", 0),
    "CN_POLICY_OVERNIGHT": ("d", 0),
}


def pub_date(metric, obs):
    o = D(obs)
    kind, n = PUB[metric]
    if kind == "me":
        return month_end(o.year, o.month) + dt.timedelta(days=n)
    if kind == "q":
        return month_end(o.year, o.month + 2) + dt.timedelta(days=n)
    return o + dt.timedelta(days=n)


def anchor(S, metric, asof):
    """latest observation whose (rule-based) publication date <= asof -> (obs_date, value, pub_date)"""
    best = None
    for d, v in zip(S.dates(metric), S.vals(metric)):
        pd = pub_date(metric, d)
        if pd <= asof:
            best = (d, v, pd)
        else:
            break
    return best


def pct(a, b):
    return (b / a - 1.0) * 100.0


def main():
    snap_p, cal_p, reg_p, rep_p, jud_p, eidx_p, map_p, out_p = sys.argv[1:9]
    snap, cal, reg, rep, jud, eidx = [jload(p) for p in (snap_p, cal_p, reg_p, rep_p, jud_p, eidx_p)]
    with open(map_p, "r", encoding="utf-8") as fh:
        map_text = fh.read()
    ss = snap["series_store"]
    S = Series(ss)
    plan = rep["research_plan"]
    cutoff = D(plan["cutoff"])
    a3 = D([a for a in plan["point_anchors"] if a["label"] == "3个月前"][0]["as_of"])
    A3, A0 = "3个月前", "最新一期"
    jud_text = json.dumps(jud, ensure_ascii=False)
    l3 = {c["id"]: c for c in jud["l3"]["contradictions"]}
    chains = {c["id"]: c for c in jud["l3"]["mechanism_chains"]}
    sc = {s["id"]: s["rows"] for s in jud["l4"]["scenarios"]}
    rm = jud["reader_map"]
    regions = {r["region"]: r for r in rm["regions"]}
    qgn = jud["quality_gate_notes"]
    tr = rm["transmission"][0]["links"]
    tn = rm["turnings"]
    ts = rm["turning_supplement"][0]
    hn = rm["history_zero_case_note"]
    hl = rm["headline_conclusion"]
    c1 = l3["C1-POLICY-DIVERGENCE"]["statement"]
    m1 = chains["M1-POLICY-RATES-ASSETS"]["links"]
    m2 = chains["M2-CN-PPI-CPI-SCISSORS"]["links"]
    cells = {c["metric_id"]: c for c in plan["point_values"]["cells"]}
    y = S.yoy

    # ================= (1) research cutoff =================
    chk("P001", "1", "report.json research_plan.cutoff vs snapshot.target_date",
        lambda: snap["target_date"][:4] + "-" + snap["target_date"][4:6] + "-" + snap["target_date"][6:], plan["cutoff"])
    chk("P002", "1", "snapshot.research_as_of vs 判断档注记①『2026-11-23T22:58:11+08:00』",
        lambda: snap["research_as_of"], "2026-11-23T22:58:11+08:00")
    chk("P003", "1", "判断档注记①载『研究截止日=快照版本日 2026-11-23』且快照版本日=2026-11-23",
        lambda: ("研究截止日=快照版本日 2026-11-23" in qgn[0]) and snap["snapshot_id"].endswith(snap["target_date"]), True)
    maxd = max(S.dates(m)[-1] for m in ss)
    chk("P004", "1", "88 序列最大观测日(不得晚于截止日)", lambda: maxd, "2026-11-23",
        note="max obs date over series_store == cutoff")
    t = dt.datetime(2026, 11, 23, 22, 58, 11, tzinfo=ZoneInfo("Asia/Shanghai"))
    for i, (name, zone, rep_) in enumerate((("纽约", "America/New_York", "09:58"), ("法兰克福", "Europe/Berlin", "15:58"),
                                            ("东京", "Asia/Tokyo", "23:58"), ("上海", "Asia/Shanghai", "22:58"))):
        chk("P%03d" % (5 + i), "12", "截止时点 2026-11-23T22:58:11+08:00 换算 %s" % name,
            lambda z=zone: t.astimezone(ZoneInfo(z)).strftime("%H:%M"), rep_)
    ents = cal["entries"]
    boj = [e for e in ents if e["entry_id"] == "RC-JP-BOJ-TARGET-2026-09"][0]
    bojm = [e for e in ents if e["entry_id"] == "RC-JP-BOJ-MAINT-2026-10"][0]
    pol = [e for e in ents if e.get("kind", "").startswith("policy")]
    chk("P009", "1", "日历 RC-JP-BOJ-TARGET-2026-09.decision_date <= 截止日", lambda: D(boj["decision_date"]) <= cutoff, True)
    chk("P010", "1", "日历 RC-JP-BOJ-TARGET-2026-09.effective_on <= 截止日(无待生效决定)",
        lambda: D(boj["effective_on"]) <= cutoff, True)
    chk("P011", "1", "日历内无生效日晚于截止日的政策条目(『待生效』如实缺席)",
        lambda: all(D(e["effective_on"]) <= cutoff for e in pol if e.get("effective_on")), True,
        note="policy entries=%d" % len(pol))
    chk("P012", "1", "判断档引用的全部点值格发布日均不晚于截止日(已发布锚格计数)",
        lambda: len([1 for c in plan["point_values"]["cells"] for an, a in c["anchors"].items()
                     if a.get("publication_date") and D(a["publication_date"]) <= cutoff]), 35)

    # ================= (2) anchor cells =================
    n = 0
    for regname in ("US", "EA", "CN", "JP"):
        r = regions[regname]
        for e in r["anchor_echo"]:
            n += 1
            m, an = e["metric_id"], e["anchor"]
            asof = a3 if an == A3 else cutoff
            got = anchor(S, m, asof)
            chk("A%03d" % n, "2", "series_store.%s 锚格值[%s@%s]" % (m, an, asof.isoformat()),
                lambda g=got: g[1], e["value"], tol=1e-6, note="obs %s" % got[0])
            chk("B%03d" % n, "2", "series_store.%s 观测期[%s]" % (m, an), lambda g=got: g[0][:7], e["observation_month"])
            eng = cells[m]["anchors"][an]
            chk("C%03d" % n, "15", "发布日按规则独立推算 %s[%s] vs 引擎点值格 publication_date" % (m, an),
                lambda g=got: g[2].isoformat(), eng.get("publication_date"),
                note=eng.get("publication_basis", "")[:70])
    chk("A100", "14", "series_store.CN_POLICY_OVERNIGHT 在三个月前锚(2026-08-23)前无已发布观测",
        lambda: S.last_on_or_before("CN_POLICY_OVERNIGHT", "2026-08-23") is None, True,
        note="首观测 %s" % S.dates("CN_POLICY_OVERNIGHT")[0])
    pubtxt = {
        "US_REAL_GDP": "发布 2026-07-29→2026-10-29", "UNEMPLOYMENT": "发布 2026-08-05→2026-11-05",
        "INDPRO": "发布 2026-08-15→2026-11-15", "CPI": "发布 2026-08-13→2026-11-13",
        "CORE_CPI": "2026-11-13(2026-10 指数)", "CORE_PCE": "发布 2026-07-30→2026-10-30",
        "DFEDTARU": "2026-09-16 决议、2026-09-17 生效", "DFF": "发布 2026-08-23→2026-11-20",
        "CN_PMI_MFG": "发布 2026-07-30→2026-10-30", "CN_CPI_YOY": "发布 2026-08-09→2026-11-09",
        "CN_PPI_YOY": "发布 2026-08-09→2026-11-09", "CN_LPR_1Y": "RC-CN-LPR-2026M11",
        "CN_OMO_7D": "1.4(2026-08-21)→1.4(末次", "CN_POLICY_OVERNIGHT": "1.25(2026-11-23",
        "JP_REAL_GDP_YOY": "发布 2026-08-14→2026-11-14", "JP_CPI_YOY": "发布 2026-08-20→2026-11-20",
        "JP_CPI_TOKYO_YOY": "发布 2026-07-30→2026-10-30", "JP_POLICY_RATE": "发布 2026-08-05→2026-11-05",
    }
    k = 0
    for m, s in pubtxt.items():
        k += 1
        chk("T%02d" % k, "15", "判断档文字载有公布时间片段 %s『%s』" % (m, s), lambda s=s: s in jud_text, True)
    chk("T20", "15", "判断档注记③(公布时间口径)逐格点名的锚格数 vs 点值格锚格总数 35",
        lambda: len(re.findall(r"[A-Z][A-Z0-9_]+(?:\(三个月前锚\))?", qgn[4].split("——", 1)[1])), 35)
    chk("T21", "15", "判断档注记③中标注『(三个月前锚)』的格数 / 点值格三个月前锚状态=ok 的格数 / 隔夜利率三个月前锚(缺席)未被列入",
        lambda: (qgn[4].count("(三个月前锚)"), sum(1 for c in plan["point_values"]["cells"] if c["anchors"].get(A3, {}).get("status") == "ok"), "CN_POLICY_OVERNIGHT(三个月前锚)" in qgn[4]),
        (17, 17, False))

    # ================= (3) yoy =================
    for pid, m, ym, rep_ in (("Y01", "CPI", "2026-07", 3.30), ("Y02", "CPI", "2026-09", 3.72),
                             ("Y04", "CORE_CPI", "2026-07", 2.47), ("Y05", "CORE_CPI", "2026-09", 2.57),
                             ("Y07", "CORE_PCE", "2026-06", 3.04), ("Y08", "CORE_PCE", "2026-09", 3.12),
                             ("Y09", "INDPRO", "2026-07", 1.25), ("Y10", "INDPRO", "2026-10", 2.15),
                             ("Y11", "US_REAL_GDP", "2026-04", 2.19), ("Y12", "US_REAL_GDP", "2026-07", 2.07),
                             ("Y13", "CN_PMI_MFG", "2026-07", -0.2), ("Y14", "CN_PMI_MFG", "2026-10", 0.61)):
        chk(pid, "3", "series_store.%s 同比 %s(基期=%s 同月/季)" % (m, ym, str(int(ym[:4]) - 1) + ym[4:]),
            lambda m=m, ym=ym: round(y(m, ym), 2), rep_)
    chk("Y03", "3", "CPI 2026-10 同比不可得(2025-10 基期观测缺席)", lambda: y("CPI", "2026-10"), None,
        note="2025-10-01 in CPI dates: %s" % ("2025-10-01" in S.dates("CPI")))
    chk("Y06", "3", "CORE_CPI 2026-10 同比不可得", lambda: y("CORE_CPI", "2026-10"), None)
    for pid, m, ym, rep_ in (("Y15", "CPI", "2026-02", 2.434), ("Y16", "CPI", "2026-05", 4.1666),
                             ("Y17", "CORE_CPI", "2026-05", 2.8229), ("Y18", "CORE_CPI", "2026-08", 2.4462),
                             ("Y19", "CORE_CPI", "2026-09", 2.5658), ("Y20", "INDPRO", "2025-11", 1.7543),
                             ("Y21", "INDPRO", "2026-02", 0.7972), ("Y22", "CN_PMI_MFG", "2026-02", -2.3904),
                             ("Y23", "CN_PMI_MFG", "2026-05", 1.0101)):
        chk(pid, "3", "series_store.%s 同比 %s(转折面所引 4 位小数)" % (m, ym),
            lambda m=m, ym=ym: round(y(m, ym), 4), rep_, tol=5e-5)
    chk("Y24", "3", "UNEMPLOYMENT 2025-10 基期同样缺席(同比口径一致性: 缺基期不补)",
        lambda: "2025-10-01" in S.dates("UNEMPLOYMENT"), False)
    chk("Y25", "3", "INDPRO 2025-10 基期在场(故 2026-10 同比可得)", lambda: "2025-10-01" in S.dates("INDPRO"), True)

    # ================= (4) policy face =================
    du = S.changes("DFEDTARU", "2025-01-01", "2026-11-23")[-1]
    chk("PO01", "4", "series_store.DFEDTARU 最近变更日/前值→后值", lambda: "%s %s→%s" % du, "2026-09-17 3.75→4.0")
    chk("PO02", "4", "DFEDTARU 变更幅 bp", lambda: round((du[2] - du[1]) * 100), 25)
    chk("PO03", "4", "DFEDTARU 决议日=生效日前一日(引擎惯例) vs 判断档『2026-09-16 决议』",
        lambda: (D(du[0]) - dt.timedelta(days=1)).isoformat(), "2026-09-16")
    chk("PO04", "4", "DFEDTARU 12 个月窗(2025-11-23..2026-11-23)变更点 vs 判断档『先降后升』",
        lambda: ["%s %s→%s" % c for c in S.changes("DFEDTARU", "2025-11-23", "2026-11-23")],
        ["2025-12-11 4.0→3.75", "2026-09-17 3.75→4.0"])
    chk("PO05", "4", "DFEDTARU 12 个月窗净变动 bp vs 判断档『净变动为零』",
        lambda: round(sum(c[2] - c[1] for c in S.changes("DFEDTARU", "2025-11-23", "2026-11-23")) * 100), 0)
    chk("PO06", "4", "DFEDTARU 生效日距截止日天数 vs 引擎面『距研究截止67天』",
        lambda: (cutoff - D(du[0])).days, 67)
    chk("PO07", "4", "series_store.DFF@2026-08-22 vs 判断档『3.63(观测 2026-08-22)』",
        lambda: S.at("DFF", "2026-08-22"), 3.63, tol=5e-4)
    chk("PO08", "4", "DFF 末观测日/值 vs 判断档『3.88(观测 2026-11-19)』",
        lambda: "%s %s" % S.last_on_or_before("DFF", "2026-11-23"), "2026-11-19 3.88")
    chk("PO09", "4", "DFF 生效日同日跳变 2026-09-17 vs 引擎面『3.63→3.88』",
        lambda: "%s→%s" % (S.at("DFF", "2026-09-16"), S.at("DFF", "2026-09-17")), "3.63→3.88")
    chk("PO10", "4", "DFF 末观测距截止日天数 vs 引擎面『距研究截止4天』", lambda: (cutoff - D("2026-11-19")).days, 4)
    chk("PO11", "4", "日历 RC-JP-BOJ-TARGET-2026-09 决议日/生效日/目标值",
        lambda: "%s/%s/%s" % (boj["decision_date"], boj["effective_on"], boj["target_value"]), "2026-09-18/2026-09-24/1.25")
    chk("PO12", "4", "日历 RC-JP-BOJ-MAINT-2026-10 确认维持日/无生效日",
        lambda: "%s/%s" % (bojm["decision_date"], bojm.get("effective_on")), "2026-10-30/None")
    chk("PO13", "4", "日本生效日距截止日天数 vs 引擎面『60天』", lambda: (cutoff - D(boj["effective_on"])).days, 60)
    chk("PO14", "4", "日本决议日距截止日天数 vs 引擎面『66天』", lambda: (cutoff - D(boj["decision_date"])).days, 66)
    chk("PO15", "4", "日本确认维持日距截止日天数 vs 引擎面『24天』", lambda: (cutoff - D(bojm["decision_date"])).days, 24)
    chk("PO16", "4", "美日决议日相隔天数 vs 判断档『相隔两日』", lambda: (D(boj["decision_date"]) - D("2026-09-16")).days, 2)
    jp = S.monthly("JP_POLICY_RATE")
    chk("PO17", "4", "series_store.JP_POLICY_RATE 月均 2026-07/08/09/10", lambda: [jp[x] for x in ("2026-07-01", "2026-08-01", "2026-09-01", "2026-10-01")],
        [0.978, 0.977, 1.043, 1.227], tol=5e-7)
    chk("PO18", "4", "JP_POLICY_RATE 三个月窗净变动 bp(0.978→1.227) vs 判断档『净 +25bp』",
        lambda: round((jp["2026-10-01"] - jp["2026-07-01"]) * 100), 25)
    jch = [c for c in S.changes("JP_POLICY_RATE", "2025-11-23", "2026-11-23") if abs(c[2] - c[1]) >= 0.005]
    chk("PO19", "4", "JP_POLICY_RATE 12 个月窗变更点(幅度>=0.5pp)/之和 bp vs 判断档『窗内六个变动点之和』『+75bp』",
        lambda: (len(jch), round(sum(c[2] - c[1] for c in jch) * 100)), (6, 75),
        note="; ".join("%s %+.1fbp" % (c[0], (c[2] - c[1]) * 100) for c in jch))
    chk("PO19b", "4", "JP_POLICY_RATE 窗内另有两个 -0.1bp 月均舍入点(0.728→0.727 / 0.978→0.977), 非政策变动",
        lambda: ["%s %.3f→%.3f" % c for c in S.changes("JP_POLICY_RATE", "2025-11-23", "2026-11-23") if abs(c[2] - c[1]) < 0.005],
        ["2026-04-01 0.728→0.727", "2026-08-01 0.978→0.977"])
    chk("PO19c", "4", "12 个月窗全量变动点之和(含舍入点) bp = 74.9 → +75bp", lambda: round(sum(c[2] - c[1] for c in S.changes("JP_POLICY_RATE", "2025-11-23", "2026-11-23")) * 100), 75)
    chk("PO20", "4", "JP_POLICY_RATE 12 个月窗净 bp(2025-11 月均 0.478→2026-10 月均 1.227)",
        lambda: round((jp["2026-10-01"] - jp["2025-11-01"]) * 100), 75)
    chk("PO21", "4", "JP_POLICY_RATE 另列口径: 自 2025-12 月均 0.557 起 bp vs 判断档『+67bp』",
        lambda: round((jp["2026-10-01"] - jp["2025-12-01"]) * 100), 67)
    chk("PO22", "4", "JP_POLICY_RATE 2026-04 月均(转折候选前值)", lambda: jp["2026-04-01"], 0.727, tol=5e-7)
    chk("PO22b", "4", "JP_POLICY_RATE 2026-05/06 月均(一年窗路径变更点 0.727→0.841)", lambda: (jp["2026-05-01"], jp["2026-06-01"]), (0.727, 0.841), tol=5e-7)
    chk("PO23", "4", "JP_POLICY_RATE 末观测月", lambda: S.dates("JP_POLICY_RATE")[-1][:7], "2026-10")
    lpr = S.monthly("CN_LPR_1Y")
    chk("PO24", "4", "series_store.CN_LPR_1Y@2026-08-20 / @2026-11-20", lambda: (lpr.get("2026-08-20"), lpr.get("2026-11-20")), (3.0, 3.0))
    chk("PO25", "4", "CN_LPR_1Y 12 个月窗内变更点数", lambda: len(S.changes("CN_LPR_1Y", "2025-11-23", "2026-11-23")), 0)
    chk("PO26", "4", "CN_LPR_1Y 最近一次变更日", lambda: S.changes("CN_LPR_1Y", "2016-01-01", "2026-11-23")[-1][0], "2025-05-20")
    chk("PO27", "4", "CN_LPR_1Y 末观测距截止日天数 vs 引擎面『距研究截止3天』", lambda: (cutoff - D("2026-11-20")).days, 3)
    e17 = [e for e in ents if e["entry_id"] == "RC-CN-LPR-2026M11"][0]
    chk("PO28", "4", "日历 RC-CN-LPR-2026M11 首发可见日/时刻 vs 判断档『公布时刻 09:00』",
        lambda: (e17["first_publish_on_or_after"], e17.get("time")), ("2026-11-20", "09:00"))
    chk("PO28b", "4", "日历无覆盖 2026-08 观测月的 LPR 条目(三个月前锚『官方惯例时刻，非本轮日历实录』)",
        lambda: [e["entry_id"] for e in ents if e.get("metric_id") == "CN_LPR_1Y" and e.get("obs_from", "9999") <= "2026-08-31" and e.get("obs_to", "0000") >= "2026-08-01"], [])
    omo = S.last_on_or_before("CN_OMO_7D", "2026-11-23")
    chk("PO29", "4", "series_store.CN_OMO_7D 三个月前锚(<=2026-08-23)/值", lambda: S.last_on_or_before("CN_OMO_7D", "2026-08-23"), ("2026-08-21", 1.4))
    chk("PO30", "4", "CN_OMO_7D 末观测/值", lambda: omo, ("2026-10-30", 1.4))
    chk("PO31", "4", "CN_OMO_7D 末观测滞后天数 vs 判断档『滞后 24 天、超出 10 天发布频率窗口』",
        lambda: ((cutoff - D(omo[0])).days, cells["CN_OMO_7D"]["anchors"][A0].get("freshness_window_days"), cells["CN_OMO_7D"]["anchors"][A0].get("freshness")), (24, 10, "stale"))
    chk("PO32", "4", "CN_OMO_7D 观测数/首观测/序列内变更点数", lambda: (len(S.dates("CN_OMO_7D")), S.dates("CN_OMO_7D")[0], len(S.changes("CN_OMO_7D", "2016-01-01", "2026-11-23"))),
        (201, "2025-10-09", 0))
    od = S.dates("CN_POLICY_OVERNIGHT")
    chk("PO33", "4", "series_store.CN_POLICY_OVERNIGHT 首观测日/观测数/取值集合 vs 判断档『序列自 2026-11-02 起』『最新 1.25』",
        lambda: (od[0], len(od), sorted(set(S.vals("CN_POLICY_OVERNIGHT")))), ("2026-11-02", 16, [1.25]))
    regm = {m["metric_id"]: m for m in reg["metrics"]}
    chk("PO34", "14", "JP_POLICY_TARGET 不在注册表亦不在 series_store(宣布目标序列缺席)",
        lambda: ("JP_POLICY_TARGET" not in regm) and ("JP_POLICY_TARGET" not in ss), True)
    chk("PO35", "4", "注册表 JP_POLICY_RATE.value_type=月均口径(非宣布目标)", lambda: regm["JP_POLICY_RATE"]["value_type"], "monthly_avg_rate")
    chk("PO36", "4", "判断档明示 JP_POLICY_RATE 为月均口径非政策目标宣布值",
        lambda: "非政策目标宣布值" in c1 and "宣布目标序列不在引擎注册表" in qgn[6], True)
    chk("PO37", "4", "官方目标 1.25 仅见于日历实录; 序列月均 1.227 未被写成官方目标",
        lambda: ("1.25" in qgn[6]) and ("目标水平 1.25" in m1[0]["text"]) and ("非宣布目标" in m1[0]["text"]), True)

    def path_net(m, w0, w1):
        a = S.last_on_or_before(m, w0)
        if a is None:
            a = (None, S.vals(m)[0])
        return round((S.last_on_or_before(m, w1)[1] - a[1]) * 100)

    for pid, m in (("PW01", "DFEDTARU"), ("PW02", "JP_POLICY_RATE"), ("PW03", "CN_LPR_1Y"), ("PW04", "CN_OMO_7D"),
                   ("PW05", "CN_POLICY_OVERNIGHT"), ("PW06", "DFF")):
        pwp = cells[m]["policy_window_path"]
        w0, w1 = pwp["window"]
        evs = [c for c in S.changes(m, w0, w1) if round((c[2] - c[1]) * 100) != 0]
        chk(pid + "a", "4", "policy_window_path(%s) 窗内变动点 日期/变动 bp: 序列直算 vs 引擎一年窗路径面" % m,
            lambda evs=evs: [(c[0], round((c[2] - c[1]) * 100)) for c in evs], [(e["date"], e["delta_bp"]) for e in pwp["events"]])
        chk(pid + "b", "4", "policy_window_path(%s) 窗启在值→窗末观测净 bp: 序列直算 vs 引擎面 net_bp" % m,
            lambda m=m, w0=w0, w1=w1: path_net(m, w0, w1), pwp["net_bp"],
            note="engine window %s..%s" % (w0, w1))
    chk("PW07", "4", "DFEDTARU 引擎事件簇 decision_date = 序列变更日前一日(两事件)", lambda: [((D(e["date"]) - dt.timedelta(days=1)).isoformat(), e["decision_date"]) for e in cells["DFEDTARU"]["policy_window_path"]["events"]],
        [("2025-12-10", "2025-12-10"), ("2026-09-16", "2026-09-16")])
    chk("X29", "10", "headline『转折面的美日方向分化取 2026-05→2026-08 与 2026-06→2026-09 两窗，起点均早于三个月前锚』",
        lambda: D("2026-05-01") < a3 and D("2026-06-01") < a3 and ("起点均早于三个月前锚" in hl), True)

    # ================= (5) rates trio + asset windows =================
    u0, u1 = S.at("UST_10Y", "2026-10-20"), S.at("UST_10Y", "2026-11-19")
    t0, t1 = S.at("TIPS_10Y", "2026-10-20"), S.at("TIPS_10Y", "2026-11-19")
    b0, b1 = S.at("BEI_10Y", "2026-10-20"), S.at("BEI_10Y", "2026-11-19")
    chk("R01", "5", "series_store.UST_10Y 2026-10-20→2026-11-19 变动 bp", lambda: round((u1 - u0) * 100), -8)
    chk("R02", "5", "series_store.TIPS_10Y 2026-10-20→2026-11-19 变动 bp", lambda: round((t1 - t0) * 100), 11)
    chk("R03", "5", "series_store.BEI_10Y 2026-10-20→2026-11-19 变动 bp", lambda: round((b1 - b0) * 100), -19)
    chk("R04", "5", "近一月窗恒等残差 bp(名义-实际-盈亏平衡)", lambda: round(((u1 - u0) - (t1 - t0) - (b1 - b0)) * 100), 0)
    u0y, t0y, b0y = S.at("UST_10Y", "2025-11-19"), S.at("TIPS_10Y", "2025-11-19"), S.at("BEI_10Y", "2025-11-19")
    chk("R05", "5", "UST_10Y 2025-11-19→2026-11-19 变动 bp", lambda: round((u1 - u0y) * 100), 91)
    chk("R06", "5", "TIPS_10Y 12 个月窗变动 bp", lambda: round((t1 - t0y) * 100), 102)
    chk("R07", "5", "BEI_10Y 12 个月窗变动 bp", lambda: round((b1 - b0y) * 100), -11)
    chk("R08", "5", "12 个月窗恒等残差 bp", lambda: round(((u1 - u0y) - (t1 - t0y) - (b1 - b0y)) * 100), 0)
    chk("R09", "5", "期末水平 名义/实际/盈亏平衡(2026-11-19)", lambda: (u1, t1, b1), (5.04, 2.88, 2.16), tol=5e-4)
    chk("R10", "5", "水平恒等 5.04=2.88+2.16 残差", lambda: round(u1 - t1 - b1, 2), 0.0, tol=5e-3)
    chk("R11", "5", "series_store.BEI_10Y@2026-11-20(最新观测)", lambda: S.at("BEI_10Y", "2026-11-20"), 2.15, tol=5e-4)
    chk("R12", "5", "UST_10Y/TIPS_10Y 无 2026-11-20 观测(共同交易日止于 11-19)", lambda: (S.at("UST_10Y", "2026-11-20"), S.at("TIPS_10Y", "2026-11-20")), (None, None))
    chk("R13", "5", "判断档 rates_decomposition 面与序列一致(窗/三分量)",
        lambda: (rm["rates_decomposition"]["window_from"], rm["rates_decomposition"]["window_to"], rm["rates_decomposition"]["nominal_bp"], rm["rates_decomposition"]["real_bp"], rm["rates_decomposition"]["bei_bp"]),
        ("2026-10-20", "2026-11-19", -8.0, 11.0, -19.0))
    chk("R14", "10", "M1 第2环『实际利率在单月窗为唯一上行分量』", lambda: (t1 - t0 > 0) and (b1 - b0 < 0), True)
    chk("R15", "10", "M1 第2环『实际利率在 12 个月窗为主导分量』", lambda: abs(t1 - t0y) > abs(b1 - b0y), True)
    chk("R16", "12", "读者报告『近30日』TIPS_10Y 2.66→2.88 / BEI_10Y 2.34→2.15(引擎面)",
        lambda: (S.last_on_or_before("TIPS_10Y", "2026-10-24")[1], S.last_on_or_before("BEI_10Y", "2026-10-24")[1]), (2.66, 2.34), tol=5e-4,
        note="engine face label; start obs located on/before 10-24")

    def near(m, day):
        r = S.last_on_or_before(m, day)
        return (r[0], r[1])

    eng = {"SPX": ("2026-10-23", "2026-11-23", 7623.680176, 7203.850098, -5.51),
           "NIKKEI225": ("2026-10-23", "2026-11-20", 62693.16, 56436.65, -9.98),
           "SHCOMP": ("2026-10-23", "2026-11-23", 3690.4753, 3538.948, -4.11),
           "DAX": ("2026-10-23", "2026-11-23", 25181.650391, 25209.449219, 0.11),
           "VIX": ("2026-10-23", "2026-11-23", 19.450001, 27.01, 38.87),
           "DXY": ("2026-10-23", "2026-11-23", 101.809998, 104.079002, 2.23),
           "CAC40": ("2026-10-23", "2026-11-20", 7782.819824, 7927.75, 1.86)}
    i = 0
    for m, (f, t_, vf, vt, pc) in eng.items():
        i += 1
        gf, gt = near(m, f), near(m, t_)
        chk("W%02da" % i, "5", "series_store.%s 引擎窗/收盘窗起止观测日" % m, lambda a=gf, b=gt: (a[0], b[0]), (f, t_))
        chk("W%02db" % i, "5", "series_store.%s 起止值" % m, lambda a=gf, b=gt: (a[1], b[1]), (vf, vt), tol=5e-5)
        chk("W%02dc" % i, "5", "%s 窗内变动 %% (末值/首值-1)" % m, lambda a=gf, b=gt: round(pct(a[1], b[1]), 2), pc)
    close = {"SPX": -9.36, "SHCOMP": -4.25, "DAX": -1.50, "VIX": 84.52, "DXY": 1.96}
    i = 0
    for m, pc in close.items():
        i += 1
        gf, gt = near(m, "2026-10-23"), near(m, "2026-11-20")
        chk("X%02d" % i, "5", "series_store.%s 收盘口径窗(10-23→11-20)变动 %%" % m, lambda a=gf, b=gt: round(pct(a[1], b[1]), 2), pc)
    for m, pc in (("SPX", 4.25), ("VIX", -24.74), ("DAX", 1.64)):
        gf, gt = near(m, "2026-11-20"), near(m, "2026-11-23")
        chk("Z-%s" % m, "12", "series_store.%s 11-23 盘中值较 11-20 收盘变动 %%" % m, lambda a=gf, b=gt: round(pct(a[1], b[1]), 2), pc)
    chk("Z-gap1", "10", "SPX 与 NIKKEI225 引擎窗跌幅差 pp(9.98-5.51)", lambda: round(9.98 - 5.51, 2), 4.47)
    chk("Z-gap2", "10", "SPX 与 SHCOMP 引擎窗跌幅差 pp(5.51-4.11)", lambda: round(5.51 - 4.11, 2), 1.40)
    chk("Z-gap3", "10", "『SPX 与 SHCOMP 落差不足两个百分点』", lambda: 5.51 - 4.11 < 2.0, True)
    chk("Z-CAC", "12", "series_store.CAC40@2026-11-23 值(未在判断档引用, 仅核在场)", lambda: S.at("CAC40", "2026-11-23"), 8022.620117, tol=5e-5)
    chk("Z-VIX", "5", "VIX 窗起/收盘窗末/引擎窗末 19.45→35.89→27.01", lambda: (near("VIX", "2026-10-23")[1], near("VIX", "2026-11-20")[1], near("VIX", "2026-11-23")[1]), (19.450001, 35.89, 27.01), tol=5e-5)
    ev("USDJPY 10-23→11-23 (engine window) value/pct", (near("USDJPY", "2026-10-23"), near("USDJPY", "2026-11-23"), round(pct(near("USDJPY", "2026-10-23")[1], near("USDJPY", "2026-11-23")[1]), 2)))
    ev("USDCNY 10-23→11-23 (engine window) value/pct", (near("USDCNY", "2026-10-23"), near("USDCNY", "2026-11-23"), round(pct(near("USDCNY", "2026-10-23")[1], near("USDCNY", "2026-11-23")[1]), 2)))
    ev("USDJPY 10-23→11-20 (close window) pct", round(pct(near("USDJPY", "2026-10-23")[1], near("USDJPY", "2026-11-20")[1]), 2))
    ev("USDCNY 10-23→11-20 (close window) pct", round(pct(near("USDCNY", "2026-10-23")[1], near("USDCNY", "2026-11-20")[1]), 2))

    # ================= (6) turning candidates =================
    def mser(m):
        d = dict(zip(S.dates(m), S.vals(m)))
        if m in ("CPI", "CORE_CPI", "INDPRO", "CN_PMI_MFG", "CORE_PCE"):
            return {k[:7]: round(y(m, k[:7]), 4) for k, v_ in d.items() if y(m, k[:7]) is not None}
        return {k[:7]: v_ for k, v_ in d.items()}

    cand = plan["turning_candidates"]["candidates"]
    cnum = 0
    for c in cand:
        cnum += 1
        m, f, t_ = c["metric_id"], c["from_ym"], c["to_ym"]
        s = mser(m)
        chk("TC%02da" % cnum, "6", "series_store.%s 候选窗 %s→%s 前值" % (m, f, t_), lambda s=s, f=f: s.get(f), c["value_before"], tol=5e-5)
        chk("TC%02db" % cnum, "6", "series_store.%s 候选窗后值" % m, lambda s=s, t_=t_: s.get(t_), c["value_after"], tol=5e-5)
        chk("TC%02dc" % cnum, "6", "%s Δ=后值-前值" % m, lambda s=s, f=f, t_=t_: round(s[t_] - s[f], 4), c["delta"], tol=5e-5)
    allm = sorted(set(plan["metrics"]) | set(c["metric_id"] for c in cand))
    best = {}
    for m in allm:
        if m not in ss or m not in PUB or PUB[m][0] == "d":
            continue
        s = mser(m)
        cands = []
        for t_ in sorted(s):
            if "2026-02" <= t_ <= "2026-11" and s[t_] is not None:
                fy, fm = int(t_[:4]), int(t_[5:7])
                fm -= 3
                if fm <= 0:
                    fm += 12
                    fy -= 1
                f = "%04d-%02d" % (fy, fm)
                if f in s and s[f] is not None:
                    cands.append((abs(round(s[t_] - s[f], 4)), t_, f))
        if cands:
            mx = max(cands)
            best[m] = (mx[1], mx[2], round(s[mx[1]] - s[mx[2]], 4))
    tcmap = {c["metric_id"]: (c["to_ym"], c["from_ym"], c["delta"]) for c in cand}
    tc_note = "; ".join("%s %s→%s Δ=%s" % (m, v[1], v[0], v[2]) for m, v in sorted(best.items(), key=lambda kv: -abs(kv[1][2])))
    chk("TC10", "6", "候选池 9 项各自=『过去12个月内 3 个月滚动变化绝对值最大者』(独立搜索: 窗两端点均在 2025-11..2026-11, 水平序列取同比)",
        lambda: all(best.get(m, (None,))[0:2] == (v[0], v[1]) for m, v in tcmap.items()), True, note=tc_note)
    chk("TC10b", "6", "未入池的月频计划指标(CORE_PCE/UNEMPLOYMENT)其最大 |Δ| 均不大于池内最小项 JP_POLICY_RATE 0.251(与『按幅度排序的候选池』相容)",
        lambda: all(abs(v[2]) <= 0.251 + 5e-5 for m, v in best.items() if m not in tcmap and PUB[m][0] == "me"), True,
        note="; ".join("%s max|Δ|=%s" % (m, v[2]) for m, v in sorted(best.items()) if m not in tcmap))
    ev("quarterly plan metrics not in the turning pool (3-month change by obs labels)", [(m, best[m]) for m in ("US_REAL_GDP", "JP_REAL_GDP_YOY") if m in best])
    ev("turning pool: independent max |3m delta| per monthly metric (to, from, delta)", sorted(best.items(), key=lambda kv: -abs(kv[1][2])))
    ev("plan metrics without a search result (daily/quarterly/absent)", [m for m in allm if m not in best])
    chk("TC11", "6", "候选池内政策维候选仅 JP_POLICY_RATE 一项(判断档『候选池内唯一的政策维候选』)",
        lambda: sorted(c["metric_id"] for c in cand if c["dimension"] == "policy"), ["JP_POLICY_RATE"])
    chk("TC12", "6", "美国 DFEDTARU 变更不在候选池且判断档已声明补述",
        lambda: ("DFEDTARU" not in tcmap) and ("未进入引擎候选池" in tn[0]["narrative"]), True)
    chk("TC13", "6", "候选池其余六项窗口终点均不晚于 2026-05",
        lambda: max(c["to_ym"] for c in cand if c["metric_id"] not in ("JP_CPI_TOKYO_YOY", "JP_POLICY_RATE", "CORE_CPI")), "2026-05")
    chk("TC14", "6", "转折窗口与锚关系: CORE_CPI 终点 2026-08-01 < 锚 2026-08-23 < 东京都终点 2026-09-01",
        lambda: D("2026-08-01") < a3 < D("2026-09-01"), True)
    chk("TC15", "6", "reader_map.turnings 三项 前值/后值/前值期 与序列一致",
        lambda: [(t_["metric_id"], t_["before_date"], mser(t_["metric_id"]).get(t_["before_date"]), mser(t_["metric_id"]).get(t_["date"])) for t_ in tn],
        [("JP_POLICY_RATE", "2026-04", 0.727, 0.978), ("JP_CPI_TOKYO_YOY", "2026-06", 1.6, 2.69), ("CORE_CPI", "2026-05", 2.8229, 2.4462)], tol=5e-5)
    chk("TC16", "6", "日本政策利率转折三个月上行 0.251 个百分点", lambda: round(0.978 - 0.727, 3), 0.251, tol=5e-5)
    chk("TC17", "6", "东京都CPI转折三个月上行 1.09 个百分点", lambda: round(mser("JP_CPI_TOKYO_YOY")["2026-09"] - mser("JP_CPI_TOKYO_YOY")["2026-06"], 2), 1.09)
    chk("TC18", "6", "东京都CPI 2026-10 值", lambda: mser("JP_CPI_TOKYO_YOY")["2026-10"], 2.73)
    chk("TC19", "6", "美国核心CPI转折三个月回落 0.3767 个百分点", lambda: round(2.8229 - 2.4462, 4), 0.3767, tol=5e-5)
    chk("TC20", "6", "转折补选 INDPRO 三个月回落 0.9571 个百分点", lambda: round(1.7543 - 0.7972, 4), 0.9571, tol=5e-5)
    chk("TC21", "6", "JP_CPI_YOY 2025-11→2026-02 = 2.9→1.27", lambda: (mser("JP_CPI_YOY")["2025-11"], mser("JP_CPI_YOY")["2026-02"]), (2.9, 1.27))
    chk("TC22", "6", "CN_CPI_YOY 2026-01→2026-04 = 0.2→1.2", lambda: (mser("CN_CPI_YOY")["2026-01"], mser("CN_CPI_YOY")["2026-04"]), (0.2, 1.2))
    chk("TC23b", "6", "CN_PMI_MFG 水平 2026-02-01", lambda: S.at("CN_PMI_MFG", "2026-02-01"), 49.0)
    chk("TC23c", "6", "CN_PMI_MFG 水平 2026-05-01", lambda: S.at("CN_PMI_MFG", "2026-05-01"), 50.0)

    # ================= (7) mechanism chains =================
    chk("M01", "7", "M2 第1环 剪刀差 2026-07: PPI 3.5 - CPI 0.5", lambda: round(S.at("CN_PPI_YOY", "2026-07-01") - S.at("CN_CPI_YOY", "2026-07-01"), 1), 3.0)
    chk("M02", "7", "M2 第2环 剪刀差 2026-10: PPI 5.7 - CPI 0.7", lambda: round(S.at("CN_PPI_YOY", "2026-10-01") - S.at("CN_CPI_YOY", "2026-10-01"), 1), 5.0)
    chk("M03", "7", "M2 第2环 evidence_level=E2 且文字含字面『【假设】』", lambda: m2[1]["evidence_level"] == "E2" and "【假设】" in m2[1]["text"], True)
    chk("M04", "7", "M1 第2/3 环 evidence_level=E2 且文字含字面『【假设】』", lambda: all(l["evidence_level"] == "E2" and "【假设】" in l["text"] for l in m1[1:]), True)
    chk("M05", "7", "M1 第1环 evidence_level=E1 且为观察位", lambda: m1[0]["evidence_level"] == "E1" and m1[0]["text"].startswith("观察"), True)
    chk("M05b", "7", "M2 第1环 evidence_level=E1 且为观察位", lambda: m2[0]["evidence_level"] == "E1" and m2[0]["text"].startswith("观察"), True)
    chk("M06", "7", "M2 第2环区分指标=CN_CPI_YOY 相对 CN_PPI_YOY 且两序列在场", lambda: "CN_CPI_YOY 相对 CN_PPI_YOY" in m2[1]["missing_link_note"] and "CN_CPI_YOY" in ss and "CN_PPI_YOY" in ss, True)
    chk("M07", "7", "M1 第1环 DFF 3.63(2026-08-22)→3.88(2026-11-19) 与序列一致", lambda: (S.at("DFF", "2026-08-22"), S.at("DFF", "2026-11-19")), (3.63, 3.88), tol=5e-4)
    chk("M08", "7", "M1 第1环 CN_OMO_7D 1.4(2026-08-21)→1.4(2026-10-30) 与序列一致", lambda: (S.at("CN_OMO_7D", "2026-08-21"), S.at("CN_OMO_7D", "2026-10-30")), (1.4, 1.4))
    chk("M09", "7", "M1 第1环 CN_POLICY_OVERNIGHT 最新 1.25(2026-11-23)", lambda: S.at("CN_POLICY_OVERNIGHT", "2026-11-23"), 1.25)
    chk("M10", "7", "M1 第2环 事件研究被 research_mode_gate 阻断(与引擎面一致)",
        lambda: "blocked" in [s for s in rep["steps"] if s["step"] == "S6_analog"][0]["envelope"]["data"]["research_mode_gate"]["event_study"], True)
    chk("M11", "7", "M2 缺环注记期限 2027-02-23 在场", lambda: "2027-02-23" in m2[1]["missing_link_note"], True)

    # ================= (8) history note =================
    an = [s for s in rep["steps"] if s["step"] == "S6_analog"][0]["envelope"]["data"]
    chk("H01", "8", "S6_analog.candidates.scanned vs 判断档『1871』", lambda: an["candidates"]["scanned"], 1871)
    chk("H02", "8", "S6_analog.candidates.valid vs 『74』", lambda: an["candidates"]["valid"], 74)
    chk("H03", "8", "S6_analog.candidates.dropped_insufficient vs 『1785』", lambda: an["candidates"]["dropped_insufficient"], 1785)
    chk("H04", "8", "S6_analog.candidates.dropped_overlap vs 『12』", lambda: an["candidates"]["dropped_overlap"], 12)
    chk("H05", "8", "候选数闭合: scanned - insufficient - overlap = valid", lambda: an["candidates"]["scanned"] - an["candidates"]["dropped_insufficient"] - an["candidates"]["dropped_overlap"], an["candidates"]["valid"])
    chk("H06", "8", "S6_analog TOP-5 独立簇代表月", lambda: [t_["candidate_month"] for t_ in an["top"]], ["2025-03", "2022-06", "2023-10", "2021-02", "2020-01"])
    chk("H07", "8", "S6_analog 维度覆盖率 增长/通胀/利率/信用/波动/估值", lambda: [round(an["state_vector"][k]["coverage"], 2) for k in ("growth", "inflation", "rates", "credit", "volatility", "valuation")],
        [0.17, 0.33, 0.75, 0.50, 1.00, 0.50], tol=5e-3)
    dims = an["top"][0]["dims"]
    chk("H08", "8", "S6_analog 首位候选各维距离贡献份额%(volatility/rates/inflation/valuation/credit/growth)",
        lambda: [round(dims[k]["contribution_share"] * 100, 2) for k in ("volatility", "rates", "inflation", "valuation", "credit", "growth")],
        [42.13, 40.66, 10.54, 6.67, 0.00, 0.00], tol=5e-3)
    fd = an["features_dropped_at_anchor"]
    chk("H09", "8", "S6_analog 锚点月缺席特征项数 vs 『12』", lambda: len(fd), 12)
    chk("H09b", "8", "缺席原因分组 hist<36 / no_value_at_anchor / release_lag vs 『2/4/6』",
        lambda: (sum(1 for v_ in fd.values() if v_.startswith("hist")), sum(1 for v_ in fd.values() if v_.startswith("no_value_at_anchor")), sum(1 for v_ in fd.values() if v_.startswith("release_lag"))), (2, 4, 6))
    chk("H09c", "8", "缺席特征名单与判断档逐项一致",
        lambda: sorted(fd), sorted(["HY_IG_gap_d12m", "HY_OAS_d12m", "CORE_CPI_yoy", "CPI_yoy", "GDP_yoy", "SPX_PE_TTM_level",
                                    "FED_FUNDS_d12m", "FED_FUNDS_level", "INDPRO_yoy", "NFP_3m_chg", "RSAFS_yoy", "UNEMPLOYMENT_level"]))
    chk("H10", "8", "S6_analog 事后表现资产集合(DXY/GOLD_F/SPX/UST_10Y)", lambda: sorted(set(k.rsplit("_", 1)[0] for k in an["dispersion"]["topN_aftermath_sign_agreement"])),
        ["DXY", "GOLD_F", "SPX", "UST_10Y"])
    chk("H11", "8", "类比特征集 13 项(判断档『美国序列锚定』)", lambda: len(an["feature_set"]["features"]), 13)
    chk("H12", "8", "研究模式门: 描述性可用/事件研究被阻断", lambda: (an["research_mode_gate"]["descriptive"], an["research_mode_gate"]["event_study"].startswith("blocked")), ("available", True))
    chk("H13", "8", "判断档 history_periods 为空且零段原因如实写明", lambda: (len(rm["history_periods"]), "取零段" in hn), (0, True))
    chk("H14", "8", "排序依据=缺席特征数优先", lambda: an["sort_basis"].startswith("(n_missing, distance, month)"), True)
    chk("H15", "8", "锚月/特征窗(2026-11, 12 个月)", lambda: (an["anchor_month"], an["feature_window_months"]), ("2026-11", 12))
    chk("H16", "8", "零段注记无事后结果冒充预测(含『相似≠因果≠预测』『事后结果≠当时可知』)", lambda: "相似≠因果≠预测" in hn and "事后结果≠当时可知" in hn, True)

    # ================= (9) scenarios =================
    A, B = sc["SCN-A-POLICY-DIVERGENCE-EXTENDS"], sc["SCN-B-POLICY-CONVERGES"]
    chk("S01", "9", "SCN-A 证伪指标在证据面在场", lambda: A["falsification"]["metric_id"] in ss, True)
    chk("S02", "9", "SCN-B 证伪指标在证据面在场", lambda: B["falsification"]["metric_id"] in ss, True)
    chk("S03", "9", "SCN-A 次级证伪指标均在场", lambda: all(m in ss for m in A["falsification"]["secondary_metric_ids"]), True)
    chk("S04", "9", "SCN-B 次级证伪指标均在场", lambda: all(m in ss for m in B["falsification"]["secondary_metric_ids"]), True)
    cur = (S.last_on_or_before("DFEDTARU", "2026-11-23")[1], S.last_on_or_before("JP_POLICY_RATE", "2026-11-23")[1], S.last_on_or_before("CN_LPR_1Y", "2026-11-23")[1])
    chk("S05", "9", "截止日读数 DFEDTARU/JP_POLICY_RATE/CN_LPR_1Y(阈值派生所本)", lambda: cur, (4.0, 1.227, 3.0), tol=5e-7)
    chk("S06", "9", "SCN-A 触发在截止日未达(DFEDTARU<4.25 且 JP<1.28)", lambda: cur[0] < 4.25 and cur[1] < 1.28, True)
    chk("S07", "9", "SCN-B 触发在截止日未达(CN_LPR_1Y>2.90)", lambda: cur[2] > 2.90, True)
    chk("S08", "9", "两情景触发方向互补(A: ≥4.25 且 ≥1.28; B: ≤4 且 <1.28)",
        lambda: ("≥4.25" in A["trigger"]["condition"] and "≥1.28" in A["trigger"]["condition"] and "≤4" in B["trigger"]["condition"] and "低于 1.28" in B["trigger"]["condition"]), True)
    chk("S09", "9", "阈值派生: 4.0+0.25=4.25 / 3.0-0.10=2.90 与判断档注记②一致",
        lambda: ("DFEDTARU 上限 4.0 再加一次标准步长=4.25" in qgn[2]) and ("=1.28" in qgn[2]) and ("3.0 下调 0.10=2.90" in qgn[2]) and (round(cur[0] + 0.25, 2), round(cur[2] - 0.10, 2)) == (4.25, 2.90), True)
    chk("S10", "9", "期限 2027-02-28 两情景一致且晚于截止日",
        lambda: ("2027-02-28" in A["falsification"]["threshold"], B["trigger"]["deadline"], A["trigger"]["deadline"], D("2027-02-28") > cutoff), (True, "2027-02-28", "2027-02-28", True))
    chk("S11", "9", "SCN-A 证伪下限 1.17 在截止日未触及(1.17<1.227<1.28) 且该阈值派生式注记②未写明",
        lambda: (1.17 < cur[1] < 1.28, "1.17" in qgn[2]), (True, False))
    chk("S12", "9", "两情景互补而不穷尽声明在场", lambda: "互补而不穷尽" in A["scenario"] and "不属任一情景" in B["scenario"], True)
    chk("S13", "9", "SCN-A 资产方向所引 TIPS +11bp / VIX +38.87% / DXY +2.23% 与序列一致且文字含该三数",
        lambda: (("+11bp" in A["asset_direction"]["direction"]) and ("+38.87%" in A["asset_direction"]["direction"]) and ("+2.23%" in A["asset_direction"]["direction"]),
                 round((t1 - t0) * 100), round(pct(19.450001, 27.01), 2), round(pct(101.809998, 104.079002), 2)), (True, 11, 38.87, 2.23))
    chk("S14", "9", "SCN-A 资产方向 evidence_refs 所引序列均在场", lambda: all(r.split("@")[0] in ss for r in A["asset_direction"]["evidence_refs"]), True)
    chk("S15", "9", "SCN-B 资产方向 evidence_refs 所引序列均在场", lambda: all(r.split("@")[0] in ss for r in B["asset_direction"]["evidence_refs"]), True)

    # ================= (10) text vs numbers =================
    chk("X06", "10", "SHCOMP@2026-11-23 在场", lambda: S.at("SHCOMP", "2026-11-23"), 3538.948, tol=5e-5)
    chk("X07", "10", "DXY@2026-11-23 在场", lambda: S.at("DXY", "2026-11-23"), 104.079002, tol=5e-6)
    chk("X08", "10", "VIX@2026-11-20=35.89", lambda: S.at("VIX", "2026-11-20"), 35.89, tol=5e-5)
    chk("X09", "10", "『收盘口径下美日股指跌幅相近且深于中国与欧洲』(美日差<1pp 且均深于 CN/DAX/CAC40)",
        lambda: abs(-9.36 - -9.98) < 1.0 and max(-9.36, -9.98) < -4.25 and max(-9.36, -9.98) < -1.50 and max(-9.36, -9.98) < 1.86, True)
    chk("X10", "10", "『引擎窗下美日跌幅相差 4.47pp 并不相近』", lambda: abs(4.47) > 2.0, True)
    chk("X11", "10", "传导环1『近一月共同交易日窗内美国政策无变动』", lambda: len(S.changes("DFEDTARU", "2026-10-20", "2026-11-19")), 0)
    chk("X12", "10", "传导环1『12 个月窗内美国政策先降后升净 0』", lambda: [(c[0], c[2] - c[1]) for c in S.changes("DFEDTARU", "2025-11-19", "2026-11-19")], [("2025-12-11", -0.25), ("2026-09-17", 0.25)])
    chk("X13", "10", "C2『三个月对照窗内三地通胀读数均高于三个月前』(序列直算: JP_CPI_YOY 07→10 / CPI 同比 07→09 / CORE_CPI 07→09 / CORE_PCE 06→09 / CN_CPI / CN_PPI)",
        lambda: (S.at("JP_CPI_YOY", "2026-10-01") > S.at("JP_CPI_YOY", "2026-07-01"), y("CPI", "2026-09") > y("CPI", "2026-07"),
                 y("CORE_CPI", "2026-09") > y("CORE_CPI", "2026-07"), y("CORE_PCE", "2026-09") > y("CORE_PCE", "2026-06"),
                 S.at("CN_CPI_YOY", "2026-10-01") > S.at("CN_CPI_YOY", "2026-07-01"), S.at("CN_PPI_YOY", "2026-10-01") > S.at("CN_PPI_YOY", "2026-07-01")),
        (True, True, True, True, True, True))
    chk("X14", "10", "C3『美国 GDP 同比小幅回落、日本回升、工业生产同比上升』(序列直算)",
        lambda: (y("US_REAL_GDP", "2026-07") < y("US_REAL_GDP", "2026-04"), S.at("JP_REAL_GDP_YOY", "2026-07-01") > S.at("JP_REAL_GDP_YOY", "2026-04-01"), y("INDPRO", "2026-10") > y("INDPRO", "2026-07")),
        (True, True, True))
    for pid, m, ra, rb, st, lvy in (("D01", "US_REAL_GDP", 2.19, 2.07, "ok", None), ("D02", "INDPRO", 1.25, 2.15, "ok", None),
                                    ("D03", "CPI", 3.30, None, "no_same_period_base", ("2026-09-01", 3.72)),
                                    ("D04", "CORE_CPI", 2.47, None, "no_same_period_base", ("2026-09-01", 2.57)),
                                    ("D05", "CORE_PCE", 3.04, 3.12, "ok", None)):
        a3c = cells[m]["anchors"][A3]
        la0 = cells[m]["anchors"][A0]
        chk(pid + "a", "3", "点值格 derived_yoy_pct(%s 三个月前锚) vs 序列同比直算" % m,
            lambda m=m, a3c=a3c: (a3c["derived_yoy_pct"], round(y(m, a3c["observation_date"][:7]), 2)), (ra, ra), tol=5e-5)
        chk(pid + "b", "3", "点值格最新锚 derived_yoy_pct / yoy_status / latest_valid_yoy vs 序列直算(%s)" % m,
            lambda m=m, la0=la0: (la0["derived_yoy_pct"], la0["yoy_status"], la0.get("latest_valid_yoy"), (lambda v: None if v is None else round(v, 2))(y(m, la0["observation_date"][:7]))),
            (rb, st, ({"observation_date": lvy[0], "yoy_pct": lvy[1]} if lvy else None), rb), tol=5e-5)
    chk("X15", "10", "C1『上限上调二十五』(3.75→4.0)", lambda: round((S.last_on_or_before("DFEDTARU", "2026-11-23")[1] - S.last_on_or_before("DFEDTARU", "2026-08-23")[1]) * 100), 25)
    chk("X16", "10", "C1 日本『三个月前锚 0.978(观测 2026-07)』『最新 1.227(观测 2026-10)』", lambda: (jp["2026-07-01"], jp["2026-10-01"]), (0.978, 1.227), tol=5e-7)
    chk("X17", "10", "C2 东京都 CPI 1.85→2.73(2026-07→2026-10)", lambda: (mser("JP_CPI_TOKYO_YOY")["2026-07"], mser("JP_CPI_TOKYO_YOY")["2026-10"]), (1.85, 2.73))
    chk("X18", "10", "C3 JP_REAL_GDP_YOY 0.8(2026-04)→1.16(2026-07)", lambda: (S.at("JP_REAL_GDP_YOY", "2026-04-01"), S.at("JP_REAL_GDP_YOY", "2026-07-01")), (0.8, 1.16))
    chk("X19", "10", "C3 US_REAL_GDP 水平 24408.011→24611.077", lambda: (S.at("US_REAL_GDP", "2026-04-01"), S.at("US_REAL_GDP", "2026-07-01")), (24408.011, 24611.077), tol=1e-6)
    chk("X20", "10", "M2『两序列两期读数发布 2026-08-09→2026-11-09』(规则推算 CN 月末+9)", lambda: (pub_date("CN_CPI_YOY", "2026-07-01").isoformat(), pub_date("CN_CPI_YOY", "2026-10-01").isoformat()), ("2026-08-09", "2026-11-09"))
    chk("X21", "10", "C3『PMI 两期均在荣枯线下方』", lambda: S.at("CN_PMI_MFG", "2026-07-01") < 50 and S.at("CN_PMI_MFG", "2026-10-01") < 50, True)
    chk("X22", "10", "C3『失业率两期持平 4.1』", lambda: (S.at("UNEMPLOYMENT", "2026-07-01"), S.at("UNEMPLOYMENT", "2026-10-01")), (4.1, 4.1))
    chk("X23", "10", "series_store.DAX@2026-11-23 vs 判断档『25209.45』", lambda: S.at("DAX", "2026-11-23"), 25209.45, tol=5e-3)
    chk("X24", "10", "NIKKEI225 末观测日 vs 『止于 2026-11-20 收盘』", lambda: S.dates("NIKKEI225")[-1], "2026-11-20")
    chk("X25", "10", "NIKKEI225 无 2026-11-23 观测", lambda: S.at("NIKKEI225", "2026-11-23"), None)
    chk("X26", "10", "SCN-A 资产方向 evidence_refs 所引序列集合(DXY/TIPS_10Y/VIX; 未含 USDJPY/USDCNY)",
        lambda: sorted(r.split("@")[0] for r in A["asset_direction"]["evidence_refs"]), ["DXY", "TIPS_10Y", "VIX"])
    chk("X27", "12", "SCN-A 资产方向所称『美元…相对日元偏强』在所引引擎窗(10-23→11-23)的 USDJPY 方向为上行",
        lambda: pct(near("USDJPY", "2026-10-23")[1], near("USDJPY", "2026-11-23")[1]) > 0, True)
    chk("X28", "10", "SCN-A 资产方向所称『美元…相对人民币偏强』在所引引擎窗(10-23→11-23)的 USDCNY 方向与所称相反(直算=下行)",
        lambda: "美元相对人民币走弱(USDCNY %s→%s, %.2f%%)" % (near("USDCNY", "2026-10-23")[1], near("USDCNY", "2026-11-23")[1], pct(near("USDCNY", "2026-10-23")[1], near("USDCNY", "2026-11-23")[1])),
        "美元指数(DXY)相对人民币与日元偏强")

    # energy (judgment note 1 + C1 competing explanation 1)
    w0, wn = S.at("WTI_F", "2026-08-21"), S.at("WTI_F", "2026-11-23")
    b0e, bn = S.at("BRENT_F", "2026-08-21"), S.at("BRENT_F", "2026-11-23")
    s0, s1_ = S.at("WTI_SPOT_M", "2026-08-01"), S.at("WTI_SPOT_M", "2026-10-01")
    chk("E01", "10", "series_store.WTI_F@2026-08-21 vs 注记①『87.06』", lambda: w0, 87.06, tol=5e-3)
    chk("E02", "10", "series_store.WTI_F@2026-11-23 vs 『82.02』", lambda: wn, 82.02, tol=5e-3)
    chk("E03", "10", "series_store.BRENT_F@2026-08-21 vs 『94.39』", lambda: b0e, 94.39, tol=5e-3)
    chk("E04", "10", "series_store.BRENT_F@2026-11-23 vs 『88.19』", lambda: bn, 88.19, tol=5e-3)
    chk("E05", "10", "WTI_F 三个月窗变动 %(08-21→11-23) vs 『-5.79%』", lambda: round(pct(w0, wn), 2), -5.79)
    chk("E06", "10", "BRENT_F 三个月窗变动 % vs 『-6.57%』", lambda: round(pct(b0e, bn), 2), -6.57)
    chk("E07", "10", "series_store.WTI_SPOT_M 2026-08→2026-10 vs 『83.9→102.07 为 +21.66%』", lambda: (s0, s1_, round(pct(s0, s1_), 2)), (83.9, 102.07, 21.66))
    chk("E08", "10", "WTI_SPOT_M 不在证据索引(判断档『该序列不在本轮证据索引，按 series_store 直读』)", lambda: all(r["metric_id"] != "WTI_SPOT_M" for r in eidx), True)
    wo, bo = S.at("WTI_F", "2026-10-30"), S.at("BRENT_F", "2026-10-30")
    fw, fb = pct(w0, wo), pct(b0e, bo)
    chk("E09", "10", "C1 竞争解释一/注记①『期货与月度现货均价方向不一致』——同窗(截至 2026-10)直算方向",
        lambda: "期货与现货同窗同向(均上升): WTI_F %s→%s 为 %+.2f%%, BRENT_F %s→%s 为 %+.2f%%, WTI_SPOT_M 08→10 为 %+.2f%%" % (w0, wo, fw, b0e, bo, fb, pct(s0, s1_)),
        "方向不一致")
    ev("WTI_F 2026-08-21 / 2026-10-30 / 2026-11-23", (w0, wo, wn))
    ev("BRENT_F 2026-08-21 / 2026-10-30 / 2026-11-23", (b0e, bo, bn))
    ev("WTI_F 10-30→11-23 pct (November reversal)", round(pct(wo, wn), 2))
    ev("BRENT_F 10-30→11-23 pct (November reversal)", round(pct(bo, bn), 2))
    ev("WTI_F 08-21→10-30 pct", round(fw, 2))
    ev("BRENT_F 08-21→10-30 pct", round(fb, 2))

    def mmean(m, ym):
        vals = [x for d, x in zip(S.dates(m), S.vals(m)) if d.startswith(ym)]
        return round(sum(vals) / len(vals), 2) if vals else None

    for m in ("WTI_F", "BRENT_F"):
        ev("%s monthly means 2026-08/09/10/11" % m, [mmean(m, ym) for ym in ("2026-08", "2026-09", "2026-10", "2026-11")])
    ev("WTI_SPOT_M 2026-06..2026-10", [(d, v_) for d, v_ in zip(S.dates("WTI_SPOT_M"), S.vals("WTI_SPOT_M")) if d >= "2026-06-01"])
    for day in ("2026-09-15", "2026-09-16", "2026-09-17", "2026-09-18"):
        r1, r2 = S.last_on_or_before("WTI_F", day), S.last_on_or_before("BRENT_F", day)
        ev("energy futures on/before %s (decision window): WTI_F %s=%s (%+.2f%% vs 08-21) | BRENT_F %s=%s (%+.2f%%)" % (
            day, r1[0], r1[1], pct(w0, r1[1]), r2[0], r2[1], pct(b0e, r2[1])), None)

    # ================= (11) honest absences =================
    for m in ("EA_REAL_GDP_YOY", "EA_HICP_YOY", "ECB_MRO", "ECB_DFR", "BUND_10Y", "BUND_2Y"):
        chk("AB-%s" % m, "11", "series_store.%s 缺席(判断档称缺席)" % m, lambda m=m: m not in ss, True)
    ga = snap["gate_a"]
    chk("G01", "11", "snapshot.gate_a.status vs 判断档『Gate A=DEGRADED』", lambda: ga["status"], "DEGRADED")
    chk("G02", "11", "gate_a.core_missing 条数 vs 『核心缺口 0 项』", lambda: len(ga["core_missing"]), 0)
    chk("G03", "11", "gate_a.noncore_missing 十项(逐项)", lambda: sorted(ga["noncore_missing"]),
        sorted(["BUND_10Y", "BUND_2Y", "CN_OMO_7D", "CN_POLICY_OVERNIGHT", "EA_HICP_YOY", "EA_REAL_GDP_YOY", "ECB_DFR", "ECB_MRO", "JP_CPI_TOKYO_YOY", "JP_REAL_GDP_YOY"]))
    chk("G04", "11", "gate_a.noncore_degraded 六项(逐项)", lambda: sorted(ga["noncore_degraded"]), sorted(["CN_SF_FLOW", "JTSJOL", "M2SL", "SPX_EPS", "SPX_PE_TTM", "US_REAL_GDP"]))
    chk("G05", "11", "snapshot.quality.counts vs 『PASS 72 / DEGRADED 7 / FAIL 0』", lambda: snap["quality"]["counts"], {"PASS": 72, "DEGRADED": 7, "FAIL": 0})
    det = ga["noncore_missing_detail"]
    chk("G06", "11", "缺口明细『来源文件缺失(ea:MISSING)』六项", lambda: sorted(m for m, s in det.items() if "ea:MISSING" in s),
        sorted(["BUND_10Y", "BUND_2Y", "EA_HICP_YOY", "EA_REAL_GDP_YOY", "ECB_DFR", "ECB_MRO"]))
    chk("G07", "11", "缺口明细『注册表未登记该指标子源状态键』两项", lambda: sorted(m for m, s in det.items() if "注册表未登记" in s), sorted(["CN_OMO_7D", "CN_POLICY_OVERNIGHT"]))
    chk("G08", "11", "缺口明细『档内无该指标子源状态记录』一项", lambda: sorted(m for m, s in det.items() if "档内无该指标" in s), ["JP_CPI_TOKYO_YOY"])
    chk("G09", "11", "缺口明细『FRED_JP_GDP 取数成功而事实未生成』一项", lambda: sorted(m for m, s in det.items() if "FRED_JP_GDP" in s), ["JP_REAL_GDP_YOY"])
    chk("G10", "14", "非核心缺口中有存量观测的四项(判断档披露③)", lambda: sorted(m for m in ga["noncore_missing"] if m in ss),
        sorted(["CN_OMO_7D", "CN_POLICY_OVERNIGHT", "JP_CPI_TOKYO_YOY", "JP_REAL_GDP_YOY"]))
    chk("G11", "11", "证据索引条数 vs 『证据索引共 69 条』", lambda: (len(eidx), len(rep["evidence_index"])), (69, 69))
    chk("G12", "11", "证据索引不含 JP_CPI_TOKYO_YOY/JP_REAL_GDP_YOY/CN_OMO_7D/CN_POLICY_OVERNIGHT(判断档逐项声明不在索引)",
        lambda: [r["ref"] for r in eidx if r["metric_id"] in ("JP_CPI_TOKYO_YOY", "JP_REAL_GDP_YOY", "CN_OMO_7D", "CN_POLICY_OVERNIGHT")], [])
    note_metrics = rep["notes"][0].split("): ", 1)[1].split("、")
    chk("G13", "14", "计划注记缺数指标数/其中点值格有值数 vs 『十九/十五』",
        lambda: (len(note_metrics), len([m for m in note_metrics if m in cells and cells[m]["anchors"][A0].get("status") == "ok"])), (19, 15))
    chk("G14", "11", "事实数 run.evidence_gate.counts.facts_kept vs 读者报告『保留 102』", lambda: rep["run"]["evidence_gate"]["counts"]["facts_kept"], 102)
    chk("G15", "11", "snapshot.facts 条数", lambda: len(snap["facts"]), 102)
    chk("G16", "11", "EA 四指标在点值格为缺席(absent: series_absent)且 cells 内无 EA 格(缺口不以相邻口径冒充)",
        lambda: (sorted(a["metric_id"] for a in plan["point_values"]["absent"]), sorted(set(a["gap"] for a in plan["point_values"]["absent"])),
                 [c["metric_id"] for c in plan["point_values"]["cells"] if c["region"] == "EA"]),
        (sorted(["EA_HICP_YOY", "EA_REAL_GDP_YOY", "ECB_DFR", "ECB_MRO"]), ["series_absent"], []))
    chk("G19", "14", "引擎缺口披露⑥: DFEDTARU 点值格观测日=序列打印日 2026-08-23 / 2026-11-23(非决议日)",
        lambda: (cells["DFEDTARU"]["anchors"][A3]["observation_date"], cells["DFEDTARU"]["anchors"][A0]["observation_date"]), ("2026-08-23", "2026-11-23"))
    chk("G20", "14", "引擎缺口披露⑤: 传导环 verdict_note 字段确实不进读者报告渲染",
        lambda: all(l["verdict_note"] not in map_text for l in tr) and all(len(l["verdict_note"]) > 10 for l in tr), True)
    vint = sorted(c["metric_id"] for c in plan["point_values"]["cells"] if any(str(a.get("vintage", "")).startswith("事后回顾") for a in c["anchors"].values()))
    chk("G21", "12", "判断档口径注记『美国实际 GDP、日本实际 GDP 同比、日本全国 CPI 同比的锚格值为最新修订族(事后回顾口径，引擎逐格标注)』vs 点值格 vintage 逐格标注集合",
        lambda: vint, ["JP_CPI_YOY", "JP_REAL_GDP_YOY", "US_REAL_GDP"])
    chk("G17", "14", "JP_POLICY_TARGET 缺口登记 registry_absent(计划 dimension_gaps)", lambda: (plan["dimension_gaps"][0]["metric_id"], plan["dimension_gaps"][0]["gap"]), ("JP_POLICY_TARGET", "registry_absent"))
    chk("G18", "11", "series_store_notes 无 NIKKEI225 注记(判断档『引擎序列未载原因』)", lambda: "NIKKEI225" in snap.get("series_store_notes", {}), False)

    # ================= (13) contract verification non-VERIFIED =================
    cv = rep["agent_judgment"]["contract_verification"]
    vs = cv["verdicts"]
    st = [v_ for v_ in vs if v_["status"] != "VERIFIED"]
    chk("ST01", "13", "契约验证总数/VERIFIED 数", lambda: (len(vs), sum(1 for v_ in vs if v_["status"] == "VERIFIED")), (17, 15))
    chk("ST02", "13", "非 VERIFIED 项状态集合", lambda: sorted(set(v_["status"] for v_ in st)), ["STALE"])
    chk("ST03", "13", "STALE 项指标集合 vs 判断档『核心PCE…与美国实际 GDP…标注 STALE』", lambda: sorted(set(v_["metric"] for v_ in st)), ["CORE_PCE", "US_REAL_GDP"])
    chk("ST04", "13", "STALE 项数值直读一致(value==expected)且判断档称『数值直读一致』", lambda: all(v_["value"] == v_["expected"] for v_ in st) and "数值直读一致" in qgn[3], True)
    ev("contract_verification non-VERIFIED rows", [(v_["item"], v_["metric"], v_["value"], v_["status"], v_["note"]) for v_ in st])

    # ================= evidence refs resolve =================
    refs = []
    for c in jud["l3"]["contradictions"]:
        refs += c["evidence_refs"]
    for c in jud["l3"]["mechanism_chains"]:
        for l in c["links"]:
            refs += l["evidence_refs"]
    for s_ in jud["l4"]["scenarios"]:
        refs += s_["rows"]["asset_direction"]["evidence_refs"]
    idx_refs = set(r["ref"] for r in eidx)
    k = 0
    for ref in sorted(set(refs)):
        k += 1
        m, d = ref.split("@")
        chk("ER%02d" % k, "ER", "证据引用 %s 可在证据索引或 series_store 解析" % ref,
            lambda m=m, d=d: (ref in idx_refs) or (m in ss and d in S.dates(m)), True,
            note="index" if ref in idx_refs else "series")
    chk("ER90", "ER", "判断档声明不在证据索引的指标确不在索引(东京都CPI/日本GDP同比/CN_OMO_7D/隔夜/WTI_SPOT_M)",
        lambda: [m for m in ("JP_CPI_TOKYO_YOY", "JP_REAL_GDP_YOY", "CN_OMO_7D", "CN_POLICY_OVERNIGHT", "WTI_SPOT_M") if any(r["metric_id"] == m for r in eidx)], [])
    chk("ER90b", "ER", "判断档按证据索引引用的指标确在索引(JP_CPI_YOY/JP_POLICY_RATE/CN_LPR_1Y/DFEDTARU/DFF/TIPS_10Y/BEI_10Y/VIX/CN_CPI_YOY/CN_PPI_YOY)",
        lambda: [m for m in ("JP_CPI_YOY", "JP_POLICY_RATE", "CN_LPR_1Y", "DFEDTARU", "DFF", "TIPS_10Y", "BEI_10Y", "VIX", "CN_CPI_YOY", "CN_PPI_YOY") if not any(r["metric_id"] == m for r in eidx)], [])
    chk("ER91", "ER", "判断档注记⑥②: CN 月度指标索引标签日期为月末(与点值格观测日不同口径)属实",
        lambda: sorted(r["ref"] for r in eidx if r["metric_id"] in ("CN_CPI_YOY", "CN_PPI_YOY")), ["CN_CPI_YOY@2026-10-31", "CN_PPI_YOY@2026-10-31"])
    chk("ER92", "ER", "判断档『日历内仅有 FOMC 2026年10月会议纪要条目』出处核对: 冻结日历文本含 FOMC/纪要 条目数",
        lambda: sum(1 for e in ents if ("FOMC" in json.dumps(e, ensure_ascii=False)) or ("纪要" in json.dumps(e, ensure_ascii=False))), 1,
        note="会议纪要事实实际出自 report.json research_plan.policy_doc_facts[0](published_on 2026-11-18)")
    pdf = plan["policy_doc_facts"][0]
    chk("ER93", "ER", "policy_doc_facts[0] 文档/发布日/依据 vs 判断档『2026-11-18 发布』",
        lambda: (pdf.get("doc_id"), pdf.get("published_on"), pdf.get("basis")), ("FOMC-MINUTES-2026-10", "2026-11-18", "user_directive"))

    # ================= reader report carries the judgment text verbatim =================
    pieces = [("headline", hl)] + [("%s.from_to" % k, regions[k]["from_to"]) for k in ("US", "EA", "CN", "JP")] + \
             [("transmission[%d].%s" % (i, f), tr[i][f]) for i in range(3) for f in ("observed_fact", "causal_hypothesis", "competing_explanation", "main_predicts", "competing_predicts", "face_off_verdict")] + \
             [("turnings[%d].%s" % (i, f), tn[i][f]) for i in range(3) for f in ("first_mover", "follow_or_diverge")] + \
             [("turnings[%d].narrative 关键数字" % i, s) for i, s in enumerate(("三个月上行 0.251 个百分点", "三个月回落 0.3767 个百分点", "三个月上行 1.09 个百分点"))] + \
             [("turning_supplement.%s" % f, ts[f]) for f in ("first_mover", "follow_or_diverge", "resolution_note", "evidence_gap")] + \
             [("history_zero_case_note", hn)] + \
             [("SCN.%s" % sid, sc[sid]["asset_direction"]["direction"]) for sid in sc] + \
             [("SCN.%s.falsification" % sid, sc[sid]["falsification"]["threshold"]) for sid in sc] + \
             [("SCN.%s.trigger" % sid, sc[sid]["trigger"]["condition"]) for sid in sc]
    k = 0
    for name, text in pieces:
        k += 1
        chk("RR%02d" % k, "RR", "MAP_REPORT.md 逐字载有判断档 %s" % name, lambda text=text: text in map_text, True)
    chk("RR90", "RR", "MAP_REPORT.sha256 与 MAP_REPORT.md 实际 sha256 一致", lambda: __import__("hashlib").sha256(map_text.encode("utf-8")).hexdigest() == "169ebb8738038bbe1afa108ff69333de80078dbd74d89f1cca96dae55161e683", True)
    chk("RR91", "RR", "读者报告载研究截止日 2026-11-23", lambda: "2026-11-23" in map_text, True)

    # ================= output =================
    pts = [p for p in PTS if p["ok"] is not None]
    errs = [p for p in PTS if p["ok"] is None]
    bad = [p for p in pts if not p["ok"]]
    hits = len(pts) - len(bad)
    lines = ["| 编号 | 类 | 出处键(文件+键) | 直算值 | 报告值 | 一致 | 备注 |", "|---|---|---|---|---|---|---|"]
    for p in PTS:
        flag = "ERR" if p["ok"] is None else ("是" if p["ok"] else "**否**")
        lines.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            p["id"], CATS.get(p["cat"], p["cat"]), p["key"].replace("|", "/"), show(p["computed"]).replace("|", "/"),
            show(p["reported"]).replace("|", "/"), flag, p["note"].replace("|", "/")))
    with open(out_p, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("POINTS=%d HITS=%d MISMATCHES=%d ERR=%d" % (len(pts), hits, len(bad), len(errs)))
    print("--- MISMATCHES")
    for p in bad:
        print("  %s | %s | 直算=%s | 报告=%s | %s" % (p["id"], p["key"], show(p["computed"]), show(p["reported"]), p["note"]))
    print("--- ERR")
    for p in errs:
        print("  %s | %s | %s" % (p["id"], p["key"], p["computed"]))
    print("--- EVIDENCE")
    for key, val in EVID:
        print("  %s => %s" % (key, show(val)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
