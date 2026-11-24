#!/usr/bin/python3 -I
"""只读: 冻结日历逐条摘要。用法: s15_calendar.py <release_calendar.json>"""
import json, sys
cal = json.load(open(sys.argv[1], encoding='utf-8'))
ents = cal.get('entries') or []
print('n entries', len(ents))
for e in ents:
    print(json.dumps(e, ensure_ascii=False)[:520])
    print()
