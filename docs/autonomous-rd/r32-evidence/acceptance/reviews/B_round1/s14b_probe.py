#!/usr/bin/python3 -I
"""席位自写探针 s14b: UNEMPLOYMENT / 各候选指标逐月值与 3 个月滚动差(只读)."""
import json
import sys

snap = json.load(open(sys.argv[1], "r", encoding="utf-8"))
ss = snap["series_store"]
for mid in sys.argv[2:]:
    d, v = ss[mid]["dates"], ss[mid]["values"]
    rows = [(a[:7], b) for a, b in zip(d, v) if "2025-04" <= a[:7] <= "2026-11"]
    print("==", mid, "==")
    for ym, b in rows:
        i = [r[0] for r in rows].index(ym)
        d3 = (b - rows[i - 3][1]) if i >= 3 else None
        print(ym, round(b, 4), "" if d3 is None else f"Δ3={d3:+.4f}")
