# -*- coding: utf-8 -*-
"""撤除 points.jsonl 中 note 以指定标记开头的记录(用于带标记脚本的整体重跑)。
用法: /usr/bin/python3 -I rc_clean_mark.py '<标记前缀>'
"""
import json, os
PTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'points.jsonl')
mark = sys_prefix = None
import sys
mark = sys.argv[1]
keep = []
n = 0
with open(PTS, encoding='utf-8') as f:
    for line in f:
        rec = json.loads(line)
        if str(rec.get('note', '')).startswith(mark):
            n += 1
            continue
        keep.append(line)
with open(PTS, 'w', encoding='utf-8') as f:
    f.writelines(keep)
print('removed', n, 'keep', len(keep))
