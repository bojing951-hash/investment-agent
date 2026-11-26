# -*- coding: utf-8 -*-
"""按 section 前缀清除 points.jsonl 中的登记(仅本席目录; 用于脚本中断后的重置)。用法: rc_clean.py <section精确名>..."""
import sys, os, json
PTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'points.jsonl')
SEC = set(sys.argv[1:])
L = [json.loads(l) for l in open(PTS, encoding='utf-8')]
keep = [x for x in L if x['section'] not in SEC]
with open(PTS, 'w', encoding='utf-8') as f:
    for x in keep:
        f.write(json.dumps(x, ensure_ascii=False) + '\n')
print('before', len(L), 'keep', len(keep))
