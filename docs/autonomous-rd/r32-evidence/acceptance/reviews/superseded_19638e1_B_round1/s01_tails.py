# -*- coding: utf-8 -*-
"""只读: 导出相关序列尾部观测。用法: python3 -I s01_tails.py <snapshot_path> <n_tail>"""
import json, sys
p = sys.argv[1]; n = int(sys.argv[2])
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)
ss = d['series_store']
want = ['CPI','CORE_CPI','CORE_PCE','INDPRO','UNEMPLOYMENT','US_REAL_GDP','EA_HICP_YOY','EA_REAL_GDP_YOY',
        'JP_POLICY_RATE','JP_CPI_YOY','JP_REAL_GDP_YOY','JP_CPI_TOKYO_YOY']
for m in want:
    s = ss.get(m)
    if s is None:
        print("==", m, "ABSENT in series_store"); continue
    dates = s['dates']; vals = s['values']
    print("==", m, "n=", len(dates), "first", dates[0], "last", dates[-1])
    # count nulls
    nn = sum(1 for v in vals if v is None)
    print("   nulls=", nn)
    for dt, v in list(zip(dates, vals))[-n:]:
        print("   ", dt, v)
