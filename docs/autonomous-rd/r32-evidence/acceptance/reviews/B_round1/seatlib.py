#!/usr/bin/python3 -I
"""seatlib.py — Audit-R32 B/Round-1 独立语义审查席自写复算库(只读).

用法: 各 sNN_*.py 脚本以 `/usr/bin/python3 -I <脚本> <路径参数…>` 运行,
脚本内用 sys.path.insert(0, 本文件所在目录) 载入本库(-I 隔离模式下不自动加路径).
全部函数只读: 只 json.load 只读面文件, 不写任何运行目录/安装树文件.
"""
import json
import os
import sys
from bisect import bisect_right
from datetime import date, datetime, timedelta

SEAT_DIR = os.path.dirname(os.path.abspath(__file__))
if SEAT_DIR not in sys.path:
    sys.path.insert(0, SEAT_DIR)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def to_date(s):
    return date.fromisoformat(s[:10])


def month_shift(ym_first, n):
    """'YYYY-MM-01' 月首字符串平移 n 个月(n 可负)."""
    y, m = int(ym_first[:4]), int(ym_first[5:7])
    t = (y * 12 + (m - 1)) + n
    y2, m2 = divmod(t, 12)
    return f"{y2:04d}-{m2 + 1:02d}-01"


def days_between(a, b):
    return (to_date(b) - to_date(a)).days


class Store:
    """冻结快照只读访问器: series_store + facts."""

    def __init__(self, snap):
        self.snap = snap
        self.ss = snap["series_store"]
        self.facts = snap["facts"]
        self.facts_by_id = {f["fact_id"]: f for f in snap["facts"]}

    def has(self, mid):
        return mid in self.ss

    def series(self, mid):
        e = self.ss[mid]
        return e["dates"], e["values"]

    def exact(self, mid, d):
        """精确观测日取值; 无则 None."""
        dates, values = self.series(mid)
        i = bisect_right(dates, d) - 1
        if i >= 0 and dates[i] == d:
            return values[i]
        return None

    def le(self, mid, d):
        """不晚于 d 的最后一个观测 -> (date, value) 或 None."""
        dates, values = self.series(mid)
        i = bisect_right(dates, d) - 1
        if i < 0:
            return None
        return dates[i], values[i]

    def ge(self, mid, d):
        """不早于 d 的第一个观测 -> (date, value) 或 None."""
        dates, values = self.series(mid)
        i = bisect_right(dates, d)
        if i == 0 and dates and dates[0] == d:
            i = 0
        if i >= len(dates):
            return None
        return dates[i], values[i]

    def between(self, mid, d0, d1):
        """[d0, d1] 闭区间观测 -> [(date, value)]."""
        dates, values = self.series(mid)
        return [(dt, v) for dt, v in zip(dates, values) if d0 <= dt <= d1]

    def monthly(self, mid, n=14, end=None):
        """月末对齐的最后 n 个月度观测 -> [(YYYY-MM, value)]."""
        dates, values = self.series(mid)
        rows = [(d[:7], v) for d, v in zip(dates, values)]
        if end is not None:
            rows = [r for r in rows if r[0] <= end]
        return rows[-n:]

    def mval(self, mid, ym):
        """月度序列按 'YYYY-MM' 精确取值; 无则 None."""
        v = self.exact(mid, ym + "-01")
        return v

    def yoy(self, mid, ym):
        """水平序列同比(%): value(ym)/value(ym-12 月)-1; 基期缺席返回 (None, reason)."""
        cur = self.mval(mid, ym)
        base_ym = month_shift(ym + "-01", -12)[:7]
        base = self.mval(mid, base_ym)
        if cur is None:
            return None, f"current {ym} absent"
        if base is None:
            return None, f"base {base_ym} absent"
        return (cur / base - 1.0) * 100.0, None

    def fact(self, mid):
        """facts 中该 metric_id 的唯一事实(若有多个取观测日最晚)."""
        fs = [f for f in self.facts if f["metric_id"] == mid]
        if not fs:
            return None
        fs.sort(key=lambda f: f["observation_date"])
        return fs[-1]


class Points:
    """复算点收集器: 每点含 出处键 / 直算值 / 报告值 / 一致与否."""

    def __init__(self, block, title):
        self.block = block
        self.title = title
        self.rows = []

    def add(self, pid, claim, computed, source, note="", tol=None, nd=2):
        """claim=受审稿写法(字符串), computed=直算值, source=文件+键.
        tol: 数值容差(默认按 nd 位小数四舍五入后比较)."""
        match = None
        detail = note
        if isinstance(computed, (int, float)) and not isinstance(computed, bool):
            c = round(computed, nd)
            if tol is None:
                tol = 0.5 * (10 ** -nd) + 1e-9
            try:
                claimed = float(str(claim).replace("%", "").replace("bp", ""))
            except ValueError:
                claimed = None
            if claimed is not None:
                match = abs(c - claimed) <= tol
                detail = f"直算 {computed:.6g} → 取 {nd} 位 {c}; 报告 {claim}; {note}"
            else:
                match = None
        elif computed is None:
            match = None
            detail = f"直算 None; 报告 {claim}; {note}"
        else:
            match = (str(computed) == str(claim))
            detail = f"直算 {computed!r}; 报告 {claim!r}; {note}"
        self.rows.append({
            "block": self.block, "id": pid, "source": source, "kind": "point",
            "computed": computed if not isinstance(computed, float) else round(computed, 6),
            "claim": claim, "match": match, "detail": detail,
        })
        return match

    def add_probe(self, pid, claim, computed, source, note=""):
        """口径敏感性探针: 不计入复算点与偏离, 仅留档(受审稿未写明口径时的替代口径直算)."""
        self.rows.append({
            "block": self.block, "id": pid, "source": source, "kind": "probe",
            "computed": computed, "claim": claim, "match": None, "detail": f"探针(不计点): {note}",
        })

    def add_bool(self, pid, claim, computed, source, note=""):
        """布尔/一致性类点: claim 为 True/False 断言, computed 为直算布尔."""
        match = (computed == claim)
        self.rows.append({
            "block": self.block, "id": pid, "source": source, "kind": "point",
            "computed": computed, "claim": claim, "match": match,
            "detail": f"直算 {computed!r}; 报告断言 {claim!r}; {note}",
        })
        return match

    def save(self, name):
        path = os.path.join(SEAT_DIR, name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"block": self.block, "title": self.title, "rows": self.rows},
                      f, ensure_ascii=False, indent=1)
        pts = [r for r in self.rows if r.get("kind", "point") == "point"]
        n = len(pts)
        ok = sum(1 for r in pts if r["match"])
        bad = sum(1 for r in pts if r["match"] is False)
        unk = sum(1 for r in pts if r["match"] is None)
        npr = len(self.rows) - n
        print(f"[{self.block}] {self.title}: points={n} match={ok} MISMATCH={bad} undetermined={unk} probes={npr}")
        for r in self.rows:
            flag = "OK " if r["match"] else ("XX " if r["match"] is False else "?? ")
            print(f"  {flag}{r['id']}: {r['detail']}  <{r['source']}>")
        return path
