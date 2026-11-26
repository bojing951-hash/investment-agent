# -*- coding: utf-8 -*-
"""撤除 points.jsonl 中完全重复的记录(同 section/src/where/computed/reported; 保留首条)。
用法: /usr/bin/python3 -I rc_dedupe.py
"""
import json, os
PTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'points.jsonl')
keep = []; seen = set(); n = 0
with open(PTS, encoding='utf-8') as f:
    for line in f:
        r = json.loads(line)
        k = (r['section'], r['src'], r['where'], json.dumps(r['computed'], sort_keys=True, ensure_ascii=False),
             json.dumps(r['reported'], sort_keys=True, ensure_ascii=False))
        if k in seen:
            n += 1; continue
        seen.add(k); keep.append(line)
with open(PTS, 'w', encoding='utf-8') as f:
    f.writelines(keep)
print('removed duplicates', n, 'keep', len(keep))
