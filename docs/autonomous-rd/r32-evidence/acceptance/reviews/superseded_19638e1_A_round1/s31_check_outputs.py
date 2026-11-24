#!/usr/bin/python3 -I
"""Seat-internal, read-only: final check of the two deliverables against the seat ledger.
Prints PASS/FAIL lines and exits with status 1 on any failure; writes no file.

Usage:
  python3 -I s31_check_outputs.py <points_all.jsonl> <VERDICT-round1.json> <PROSE-round1.md> <s35_build_prose.py>
"""
import importlib.util
import json
import re
import sys
from collections import Counter

ORDER = ['seat', 'reviewer', 'verdict', 'overall', 'notes', 'items', 'must_fix', 'counterexamples_sought',
         'recompute_points', 'recompute_mismatches', 'mismatch_details', 'audited_at']
HEADERS = ['## 0. 结论速览与计数口径', '## 1. 复算清单', '### 1.1 分节计数', '### 1.2 逐点台账',
           '## 2. 规程第 4 节: 六查逐项结论', '## 3. 专项核对', '## 4. 反方攻击记录', '## 5. 规程第 3 节覆盖核对',
           '## 6. 问题清单', '## 7. 引擎面与渲染面旁注', '## 8. 文件索引']
fails = []


def check(cond, msg):
    print(('PASS  ' if cond else 'FAIL  ') + msg)
    if not cond:
        fails.append(msg)


def split_row(line):
    # split a markdown table row on unescaped pipes
    s = line.replace('\\|', '\x00').strip()
    assert s.startswith('|') and s.endswith('|'), line[:80]
    return [c.replace('\x00', '\\|').strip() for c in s[1:-1].split('|')]


def main():
    spec = importlib.util.spec_from_file_location('s35_build_prose', sys.argv[4])
    s35 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(s35)

    raw = open(sys.argv[2], 'rb').read()
    v = json.loads(raw.decode('utf-8'))
    check(list(v.keys()) == ORDER, 'verdict keys exactly in protocol order (%d keys)' % len(v))
    check(v['seat'] == 'semantic-audit-seat', 'seat')
    check(v['reviewer'] == 'independent-zero-context-seat-r32-a-round1', 'reviewer')
    check(v['audited_at'] == '2026-11-24', 'audited_at')
    check(v['verdict'] in ('UPHELD', 'REVISE') and v['overall'] == v['verdict'], 'verdict/overall = %s' % v['verdict'])
    check(isinstance(v['notes'], str) and '\n' not in v['notes'] and len(v['notes']) > 200, 'notes is one non-empty line (%d chars)' % len(v['notes']))
    items = v['items']
    check(all(sorted(it.keys()) == ['fix', 'note', 'original', 'severity', 'where'] for it in items), 'items have exactly the five protocol keys')
    check(all(isinstance(it[k], str) and it[k].strip() for it in items for k in it), 'item fields are non-empty strings')
    sev = Counter(it['severity'] for it in items)
    check(set(sev) <= {'MAJOR', 'MINOR', 'NIT'}, 'item severities valid: %s' % dict(sev))
    check(sev.get('MAJOR', 0) == 0, 'MAJOR count = 0')
    check(v['must_fix'] == [], 'must_fix empty (no MAJOR, verdict UPHELD)')
    if v['verdict'] == 'REVISE':
        check(len(v['must_fix']) > 0, 'REVISE requires must_fix')
    att = v['counterexamples_sought']
    check(isinstance(att, list) and all(isinstance(a, str) for a in att), 'counterexamples_sought is a list of strings')
    nums = [int(re.match(r'^反方攻击 (\d+) ', a).group(1)) for a in att]
    check(nums == list(range(1, len(att) + 1)), 'attacks numbered 1..%d' % len(att))
    check(all(a.count('?→') == 1 for a in att), 'each attack has exactly one "?→" separator')
    check(len(att) >= 6 + 6, 'at least one attack per L3 statement (3) and per chain link (6): %d' % len(att))
    md = v['mismatch_details']
    check(isinstance(md, list) and len(md) == v['recompute_mismatches'], 'mismatch_details length = recompute_mismatches (%d)' % len(md))
    check(all(sorted(m.keys()) == ['computed', 'difference', 'note', 'point', 'reported', 'severity', 'where'] for m in md), 'mismatch detail keys')

    rows = [json.loads(x) for x in open(sys.argv[1], encoding='utf-8') if x.strip()]
    counted = [r for r in rows if not s35.is_info(r)]
    bad = [r for r in counted if not r['ok']]
    info = len(rows) - len(counted)
    check(v['recompute_points'] == len(counted), 'recompute_points = ledger counted rows (%d)' % len(counted))
    check(v['recompute_mismatches'] == len(bad), 'recompute_mismatches = ledger mismatches (%d)' % len(bad))
    check(len(counted) >= 120, 'coverage >= protocol minimum 120 points')
    check([m['point'] for m in md] == [r['id'] for r in bad], 'mismatch_details names exactly the mismatching ledger rows')

    praw = open(sys.argv[3], 'rb').read()
    p = praw.decode('utf-8')
    check('\r' not in p, 'PROSE has no CR characters')
    check('{{' not in p and '}}' not in p, 'PROSE has no unreplaced placeholder')
    for h in HEADERS:
        check(p.count('\n' + h) == 1, 'PROSE header present once: ' + h)
    check(p.count('\n> ' + v['notes'] + '\n') == 1, 'PROSE carries the verdict notes verbatim (one blockquote line)')
    check('| 复算计点 / 偏离 | 计点 %d / 偏离 %d(信息行 %d 不计入) |' % (len(counted), len(bad), info) in p, 'PROSE head count row matches ledger')
    # attacks
    ok_att = True
    for a in att:
        m = re.match(r'^(反方攻击 \d+ \([^)]*\)): (.*?)\?→(.*)$', a, re.S)
        ok_att = ok_att and bool(m) and ('| %s | %s? | %s |' % (s35.esc(m.group(1)), s35.esc(m.group(2).rstrip()), s35.esc(m.group(3).strip()))) in p
    check(ok_att, 'every attack appears in PROSE (question / result cells)')
    check(('共 %d 次' % len(att)) in p, 'attack count sentence = %d' % len(att))
    # items
    ok_it = True
    for k, it in enumerate([i for i in items if i['severity'] == 'MINOR'], 1):
        ok_it = ok_it and all(s35.esc(it[f]) in p for f in ('where', 'note', 'original', 'fix')) and ('**MINOR-%d**' % k) in p
    for k, it in enumerate([i for i in items if i['severity'] == 'NIT'], 1):
        ok_it = ok_it and all(s35.esc(it[f]) in p for f in ('where', 'note', 'original', 'fix')) and ('**NIT-%d**' % k) in p
    check(ok_it, 'every item (where/note/original/fix) appears in PROSE with its MINOR-k / NIT-k label')
    check(('MAJOR 0 / MINOR %d / NIT %d' % (sev.get('MINOR', 0), sev.get('NIT', 0))) in p, 'PROSE head severity counts match verdict')

    # section 1.2 must be a row-by-row rendering of the ledger
    start = p.index('#### 1.2.1 ')
    end = p.index('\n## 2. ')
    sec = p[start:end]
    lines = [x for x in sec.split('\n') if re.match(r'^\| \d+ \| ', x)]
    check(len(lines) == len(rows), 'section 1.2 has one numbered row per ledger row (%d)' % len(rows))
    ok_rows = True
    st = Counter()
    # section 1.2 groups the ledger by section (anchors, monthly, daily, history, sync, misc), keeping the
    # file order inside each section; rebuild that order here independently of the builder's helpers
    sec_order = ['anchors', 'monthly', 'daily', 'history', 'sync', 'misc']
    grouped = [r for key in sec_order for r in rows if r['section'] == key]
    check(len(grouped) == len(rows), 'every ledger section is one of the six rendered sections')
    sub = [x for x in sec.split('\n') if x.startswith('#### 1.2.') and re.search(r'计点 (\d+) 行: 一致 (\d+)、偏离 (\d+);信息行 (\d+)', x)]
    check([int(re.search(r'计点 (\d+) 行', x).group(1)) for x in sub] == [sum(1 for r in rows if r['section'] == k and not s35.is_info(r)) for k in sec_order],
          'subsection counted-row counts match ledger')
    for n, (line, r) in enumerate(zip(lines, grouped), 1):
        c = split_row(line)
        exp = [str(n), s35.esc(r['id']), s35.esc(r['src']), s35.esc(s35.fmt(r['computed'])),
               s35.esc(s35.fmt(r['reported'], s35.is_info(r))), s35.status(r), s35.esc(r.get('note', ''))]
        ok_rows = ok_rows and c == exp
        st[c[5] if len(c) > 5 else '?'] += 1
    check(ok_rows, 'section 1.2 rows equal the ledger row by row (id / source / computed / reported / status / note)')
    check(st.get(u'一致', 0) == len(counted) - len(bad) and st.get(u'偏离', 0) == len(bad) and st.get(u'信息行(不计入)', 0) == info,
          'section 1.2 status counts = %s' % dict(st))
    # summary table
    by = Counter(r['section'] for r in counted)
    for key, name in s35.SECTIONS:
        rs = [r for r in rows if r['section'] == key]
        c = [r for r in rs if not s35.is_info(r)]
        b = [r for r in c if not r['ok']]
        check('| %s | %d | %d | %d | %d |' % (name, len(c), len(c) - len(b), len(b), len(rs) - len(c)) in p, 'summary table row: ' + name)
    print('counts: points=%d mismatches=%d info=%d items=%s attacks=%d prose_chars=%d prose_lines=%d' % (
        len(counted), len(bad), info, dict(sev), len(att), len(p), p.count('\n') + 1))
    print('RESULT: %s' % ('ALL PASS' if not fails else 'FAILURES=%d' % len(fails)))
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
