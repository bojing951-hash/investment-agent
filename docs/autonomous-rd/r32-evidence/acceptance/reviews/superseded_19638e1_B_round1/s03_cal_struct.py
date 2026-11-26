# -*- coding: utf-8 -*-
"""只读: 冻结日历结构。用法: python3 -I s03_cal_struct.py <calendar_path>"""
import json, sys
p = sys.argv[1]
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)
print("TYPE", type(d).__name__)
if isinstance(d, dict):
    for k, v in d.items():
        if isinstance(v, list):
            print("KEY", k, "list len", len(v))
        elif isinstance(v, dict):
            print("KEY", k, "dict len", len(v), "subkeys", list(v.keys())[:30])
        else:
            print("KEY", k, "=", repr(v)[:400])
