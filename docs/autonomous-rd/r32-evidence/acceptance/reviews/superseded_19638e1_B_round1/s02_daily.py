# -*- coding: utf-8 -*-
"""只读: 日频序列尾部。用法: python3 -I s02_daily.py <snapshot_path> <n_tail>"""
import json, sys
p = sys.argv[1]; n = int(sys.argv[2])
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)
ss = d['series_store']
want = ['UST_10Y','TIPS_10Y','BEI_10Y','SPX','NIKKEI225','VIX','DXY','GOLD_F','USDJPY','EURUSD']
for m in want:
    s = ss[m]; dates = s['dates']; vals = s['values']
    print("==", m, "n=", len(dates), "first", dates[0], "last", dates[-1], "nulls=", sum(1 for v in vals if v is None))
    for dt, v in list(zip(dates, vals))[-n:]:
        print("   ", dt, v)
