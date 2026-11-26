# -*- coding: utf-8 -*-
"""rc20 辅助只读检视(草稿阶段用): 打印台账若干记录全文、判断档中若干短语上下文、草稿 PROSE 指定段。
用法: /usr/bin/python3 -I rc20_inspect.py <run_dir> <points.jsonl> <draft_md>"""
import sys, os, re, json
R, PTS, DR = sys.argv[1:4]
recs = [json.loads(l) for l in open(PTS, encoding='utf-8') if l.strip()]
aj = json.load(open(os.path.join(R, 'agent_judgment.json'), encoding='utf-8'))


def leaves(o, path=''):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from leaves(v, (path + '.' + k) if path else k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from leaves(v, '%s[%d]' % (path, i))
    elif isinstance(o, str):
        yield path, o


LV = list(leaves(aj))
for i in (686, 687, 897, 874, 870, 916, 326, 327, 328, 358, 521, 860, 879, 881, 883, 875):
    r = recs[i]
    print('REC #%d [%s] ok=%s\n   src=%s\n   computed=%s\n   reported=%s\n   where=%s\n   note=%s' % (
        i, r.get('section'), r['ok'], r.get('src'), json.dumps(r.get('computed'), ensure_ascii=False)[:900], json.dumps(r.get('reported'), ensure_ascii=False)[:500], r.get('where'), r.get('note')))
print('--- mention contexts')
core = '\n'.join(t for _, t in leaves({'l3': aj.get('l3'), 'l4': aj.get('l4'), 'reader_map': aj.get('reader_map')}))
for a in ('M2', '美国GDP', '美国实际GDP', 'ECB_DFR', 'MRO', '东京CPI', '欧元区GDP同比', '日本GDP同比', '隔夜利率', '7天逆回购'):
    hits = [m.start() for m in re.finditer(re.escape(a), core)]
    print('%s x%d' % (a, len(hits)), '||', core[max(0, hits[0] - 70):hits[0] + 90].replace('\n', ' ') if hits else '')
print('--- phrase contexts')
for ph in ('全国口径的回升起点', '中国 PPI 低点在 2025-11', '逐项见质量注记', '四地证据面呈现', 'NIKKEI225 止于 2026-11-20 收盘', '冻结发布日历无美联储与欧央行实录条目', '两口径数值可差约1个百分点', '对质表判断记', '历史段事后数字取自相似检索面事后块', 'DFF 3.88→3.63→3.88', '支持竞争解释', '尚不能区分'):
    n = 0
    for p, t in LV:
        for m in re.finditer(re.escape(ph), t):
            if n < 2:
                print('%s @%s :: %s' % (ph, p, t[max(0, m.start() - 110):m.end() + 150].replace('\n', ' ')))
            n += 1
    print('   (%s 共 %d 处)' % (ph, n))
md = open(DR, encoding='utf-8').read()
L = md.split('\n')


def show(start_pat, nlines, maxw=900):
    for i, ln in enumerate(L):
        if start_pat in ln:
            for x in L[i:i + nlines]:
                print(x[:maxw])
            print('  …')
            return


print('--- draft head')
for x in L[:75]:
    print(x[:700])
print('--- draft section 3/4/5')
show('## 3 登记项', 14, 600)
show('## 4 规程第 3 节覆盖面', 60, 1300)
print('--- draft section 6/7/8')
show('## 6 问题清单', 80, 700)
