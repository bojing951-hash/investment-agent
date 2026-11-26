#!/usr/bin/python3 -I
"""只读自检: 校验 VERDICT-round1.json 结构(规程第 6 节)与 PROSE-round1.md 基本面。
用法: s19_validate.py <VERDICT-round1.json> <PROSE-round1.md> <recompute_points.json>"""
import json
import sys

vp, pp, rp = sys.argv[1:4]
raw = open(vp, 'rb').read()
txt = raw.decode('utf-8')  # 非法 UTF-8 会抛异常
V = json.loads(txt)
P = open(pp, encoding='utf-8').read()

want = ['seat', 'reviewer', 'verdict', 'overall', 'notes', 'items', 'must_fix',
        'counterexamples_sought', 'recompute_points', 'recompute_mismatches',
        'mismatch_details', 'audited_at']
print('keys ok:', list(V.keys()) == want, list(V.keys()))
assert list(V.keys()) == want
assert V['verdict'] in ('UPHELD', 'REVISE')
assert V['reviewer'] == 'independent-zero-context-seat-r32-b-round1'
assert V['audited_at'] == '2026-11-24'
assert isinstance(V['notes'], str) and len(V['notes']) >= 100
assert isinstance(V['must_fix'], list) and len(V['must_fix']) >= 1  # 规程: 字符串数组
for i, m in enumerate(V['must_fix']):
    assert isinstance(m, str) and '→' in m, (i, type(m).__name__)
    assert '→' in m
maj = [it for it in V['items'] if it['severity'] == 'MAJOR']
for it in maj:  # MAJOR 必填原句/改句
    assert isinstance(it['original'], str) and it['original'].strip(), it['where']
    assert isinstance(it['fix'], str) and it['fix'].strip(), it['where']
sev = {}
for it in V['items']:
    assert set(it.keys()) == {'severity', 'where', 'note', 'original', 'fix'}, sorted(it.keys())
    sev[it['severity']] = sev.get(it['severity'], 0) + 1
print('severity:', sev, 'must_fix:', len(V['must_fix']))
assert (V['verdict'] == 'REVISE') == (sev.get('MAJOR', 0) >= 1 or len(V['must_fix']) >= 1)
assert V['recompute_mismatches'] == 0 or V['mismatch_details']
assert isinstance(V['counterexamples_sought'], list) and len(V['counterexamples_sought']) >= 6
assert all(isinstance(s, str) and '→' in s for s in V['counterexamples_sought'])
assert isinstance(V['mismatch_details'], list)
assert V['verdict'] == V['overall'] == 'REVISE'
assert len(maj) == 1

pts = json.load(open(rp, encoding='utf-8'))
ind = [p for p in pts if not p.get('structural')]
bad = [p for p in ind if not p.get('ok')]
print('points independent=%d bad=%d structural=%d' % (len(ind), len(bad), len(pts) - len(ind)))
assert len(ind) == V['recompute_points'] and len(bad) == V['recompute_mismatches']

# PROSE 基本面
for s in ('REVISE', '302', 'MAJOR', '尚不能区分', '支持主解释'):
    print('PROSE has %r:' % s, s in P)
print('PROSE chars=%d lines=%d' % (len(P), P.count('\n') + 1))
print('JSON chars=%d bytes=%d' % (len(txt), len(raw)))
print('overall:', V['overall'][:200])
print('notes n=%d' % len(V['notes']))
print('VALID')
