#!/usr/bin/python3 -I
"""席位自写探针 s13: 逐日打印 BRENT_F / USDJPY / EURUSD 指定区间 + 百分位多定义(只读)."""
import json
import sys

snap = json.load(open(sys.argv[1], "r", encoding="utf-8"))
ss = snap["series_store"]
mode = sys.argv[2]
if mode == "brent":
    d, v = ss["BRENT_F"]["dates"], ss["BRENT_F"]["values"]
    for a, b in zip(d, v):
        if "2026-10-08" <= a <= "2026-11-23":
            print(a, round(b, 3))
    w = [(a, b) for a, b in zip(d, v) if "2026-08-19" <= a <= "2026-11-23"]
    print("window n", len(w), "min", min(w, key=lambda x: x[1]), "max", max(w, key=lambda x: x[1]))
    below = [(a, round(b, 3)) for a, b in w if b < 91.62]
    print("below 91.62 in window:", below)
    for lo, hi in (("2026-10-13", "2026-11-06"), ("2026-10-13", "2026-11-09"), ("2026-10-13", "2026-11-16"), ("2026-10-16", "2026-11-16"), ("2026-10-13", "2026-11-13"), ("2026-10-20", "2026-11-16")):
        p = [(a, b) for a, b in zip(d, v) if lo <= a <= hi]
        print(lo, hi, "n", len(p), "min", min(p, key=lambda x: x[1])[0], round(min(p, key=lambda x: x[1])[1], 3), "max", round(max(p, key=lambda x: x[1])[1], 3))
    # 12m candidates
    for a in ("2025-11-19", "2025-11-20", "2025-11-21", "2025-11-23"):
        if a in d:
            i = d.index(a)
            print("12m from", a, round(v[i], 3), "-> 2026-11-23", round((v[-1] / v[i] - 1) * 100, 2))
elif mode == "fx":
    for mid in ("USDJPY", "EURUSD"):
        d, v = ss[mid]["dates"], ss[mid]["values"]
        cur = v[d.index("2026-11-23")]
        for lo, hi, nm in (("2025-11-23", "2026-11-23", "12m[2025-11-23..2026-11-23]"), ("2025-11-24", "2026-11-23", "12m excl start"), ("2025-11-19", "2026-11-23", "12m[2025-11-19..]")):
            xs = [b for a, b in zip(d, v) if lo <= a <= hi]
            n = len(xs)
            lt = sum(1 for x in xs if x < cur)
            le = sum(1 for x in xs if x <= cur)
            print(mid, nm, "n", n, "lt%%=%.2f le%%=%.2f mid=%.2f rank/(n)=%.2f (le-1)/(n-1)=%.2f" % (lt / n * 100, le / n * 100, (lt + le) / 2 / n * 100, le / n * 100, (le - 1) / (n - 1) * 100), "min", round(min(xs), 3), "max", round(max(xs), 3))
        xs = [b for a, b in zip(d, v) if a <= "2026-11-23"]
        n = len(xs)
        lt = sum(1 for x in xs if x < cur)
        le = sum(1 for x in xs if x <= cur)
        print(mid, "full n", n, "first", d[0], "lt%%=%.2f le%%=%.2f mid=%.2f (le-1)/(n-1)=%.2f" % (lt / n * 100, le / n * 100, (lt + le) / 2 / n * 100, (le - 1) / (n - 1) * 100), "max", round(max(xs), 3))
        for a in ("2026-08-19", "2026-08-20", "2026-08-21", "2026-08-22", "2026-08-23"):
            if a in d:
                print(mid, a, round(v[d.index(a)], 4), "chg%", round((cur / v[d.index(a)] - 1) * 100, 2))
