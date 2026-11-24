#!/usr/bin/python3 -I
"""只读: 判断档文字字段在读者报告(MAP_REPORT/FULL_REPORT)中的渲染一致性 + 打印传导链第3环全文。
用法: s14_render_check.py <agent_judgment.json> <MAP_REPORT.md> <FULL_REPORT.md> <outdir>"""
import json, sys, os, re
aj = json.load(open(sys.argv[1], encoding='utf-8'))
mapr = open(sys.argv[2], encoding='utf-8').read()
fullr = open(sys.argv[3], encoding='utf-8').read()
out = sys.argv[4]

def norm(s):
    s = re.sub(r'[*_`>|\-]', '', s)
    s = re.sub(r'\s+', '', s)
    return s

nm, nf = norm(mapr), norm(fullr)
texts = []
texts.append(('headline_conclusion', aj['reader_map']['headline_conclusion']))
for r in aj['reader_map']['regions']:
    texts.append(('regions[%s].from_to' % r['region'], r['from_to']))
for c in aj['l3']['contradictions']:
    texts.append(('l3[%s].statement' % c['id'], c['statement']))
    for i, x in enumerate(c.get('competing_explanations') or []):
        texts.append(('l3[%s].competing[%d]' % (c['id'], i), x))
ch = aj['reader_map']['transmission'][0]
for i, l in enumerate(ch['links']):
    for k in ('observed_fact', 'causal_hypothesis', 'competing_explanation', 'main_predicts', 'competing_predicts', 'verdict_note'):
        texts.append(('chain.link%d.%s' % (i + 1, k), l[k]))
    texts.append(('chain.link%d.face_off_verdict' % (i + 1), l['face_off_verdict']))
for t in aj['reader_map']['turnings']:
    for k in ('first_mover', 'follow_or_diverge', 'narrative'):
        texts.append(('turnings[%s].%s' % (t['metric_id'], k), t[k]))
texts.append(('history_zero_case_note', aj['reader_map']['history_zero_case_note']))
for s in aj['l4']['scenarios']:
    for k in ('scenario',):
        texts.append(('l4[%s].%s' % (s['id'], k), s['rows'][k]))
    texts.append(('l4[%s].asset_direction' % s['id'], s['rows']['asset_direction']['direction']))
    texts.append(('l4[%s].falsification' % s['id'], s['rows']['falsification']['threshold']))
    texts.append(('l4[%s].trigger' % s['id'], s['rows']['trigger']['condition']))
res = []
for name, t in texts:
    n = norm(t)
    res.append({'field': name, 'len': len(t), 'in_MAP': n in nm, 'in_FULL': n in nf})
tot = len(res)
print('fields', tot, '| in MAP', sum(r['in_MAP'] for r in res), '| in FULL', sum(r['in_FULL'] for r in res),
      '| in neither', sum(1 for r in res if not r['in_MAP'] and not r['in_FULL']))
for r in res:
    if not (r['in_MAP'] and r['in_FULL']):
        print('  ', r)
json.dump(res, open(os.path.join(out, 'render_check.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('===== link 3 full =====')
print(json.dumps(ch['links'][2], ensure_ascii=False, indent=1))
print('===== JP region from_to =====')
print(aj['reader_map']['regions'][2]['from_to'])
print(json.dumps(aj['reader_map']['regions'][2].get('anchor_echo'), ensure_ascii=False))
print('===== chain title', ch.get('title'), 'extra keys', sorted(ch.keys()))
