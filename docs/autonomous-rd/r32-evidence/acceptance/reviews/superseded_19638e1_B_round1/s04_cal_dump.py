# -*- coding: utf-8 -*-
"""只读: 冻结日历全文(逐条)。用法: python3 -I s04_cal_dump.py <calendar_path>"""
import json, sys
p = sys.argv[1]
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)
print("version", d['version'], "created", d['created'], "updated", d['updated'])
print("SPEC:", d['spec'])
print()
for i, b in enumerate(d['batches']):
    print("BATCH", i, json.dumps(b, ensure_ascii=False))
print()
for i, e in enumerate(d['entries']):
    print("ENTRY", i, json.dumps(e, ensure_ascii=False))
