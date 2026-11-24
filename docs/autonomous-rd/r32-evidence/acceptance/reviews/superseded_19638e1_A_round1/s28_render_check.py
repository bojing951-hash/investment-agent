#!/usr/bin/python3 -I
"""Read-only: which judgment text blocks are rendered in which report file?

A text leaf counts as rendered when it is found after stripping whitespace and
markdown emphasis / table separators.  Information for the PROSE remarks only.

Usage:
  python3 -I s28_render_check.py <agent_judgment.json> <MAP_REPORT.md> <FULL_REPORT.md> <report.md> <out.txt>
"""
import json
import re
import sys

STRIP = re.compile(u'[\s*`|]')


def norm(s):
    return STRIP.sub('', s)


def leaves(o, path, out):
    if isinstance(o, str):
        out.append((path, o))
    elif isinstance(o, dict):
        for k in o:
            leaves(o[k], path + '.' + k, out)
    elif isinstance(o, list):
        for i, x in enumerate(o):
            leaves(x, path + '[%d]' % i, out)


def top_block(path):
    # path starts with '.'
    parts = path.split('.')[1:]
    if parts and parts[0] == 'l3' and len(parts) > 1:
        return 'l3.' + parts[1]
    if parts and parts[0] == 'l4':
        return 'l4'
    if parts and parts[0] == 'reader_map' and len(parts) > 1:
        return 'reader_map.' + parts[1]
    return parts[0] if parts else '(root)'


def main():
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        jud = json.load(f)
    texts = []
    for p in sys.argv[2:5]:
        with open(p, 'r', encoding='utf-8') as f:
            texts.append(norm(f.read()))
    out = []
    leaves(jud, '', out)
    # keep narrative leaves only: contains CJK and length >= 8
    nar = [(p, s) for p, s in out if len(s) >= 8 and re.search(u'[一-鿿]', s)]
    res = {}
    for p, s in nar:
        n = norm(s)
        b = top_block(p)
        r = res.setdefault(b, [0, 0, 0, 0])
        r[0] += 1
        for i, t in enumerate(texts):
            if n in t:
                r[i + 1] += 1
    lines = ['narrative leaves (CJK, len>=8): %d' % len(nar),
             'block | n | in MAP_REPORT.md | in FULL_REPORT.md | in report.md']
    for b in sorted(res):
        r = res[b]
        lines.append('%s | %d | %d | %d | %d' % (b, r[0], r[1], r[2], r[3]))
    tot = [sum(res[b][i] for b in res) for i in range(4)]
    lines.append('TOTAL | %d | %d | %d | %d' % tuple(tot))
    lines.append('')
    lines.append('not rendered in MAP_REPORT.md (block path : first 70 chars):')
    for p, s in nar:
        if norm(s) not in texts[0]:
            lines.append('  %s : %s' % (p[-60:], s[:70].replace('\n', ' ')))
    lines.append('')
    kws = [u'09:53', u'2027-02-28', u'缺基期', u'Gate A', u'尚不能区分', u'缺环为假设', u'【推断】', u'【尚未验证】', u'【假设】',
           u'盘中快照', u'事后回顾', u'首发', u'近30日', u'收盘口径', u'停摆', u'2025-12-23', u'无变化', u'数据不可得', u'推定']
    names = ['MAP_REPORT.md', 'FULL_REPORT.md', 'report.md']
    raw = []
    for p in sys.argv[2:5]:
        with open(p, 'r', encoding='utf-8') as f:
            raw.append(f.read())
    lines.append('keyword occurrences (raw text):')
    for kw in kws:
        lines.append('  %s : %s' % (kw, ' / '.join('%s=%d' % (n, t.count(kw)) for n, t in zip(names, raw))))
    blob = json.dumps(jud, ensure_ascii=False)
    lines.append('keyword occurrences in agent_judgment.json:')
    for kw in kws:
        lines.append('  %s : %d' % (kw, blob.count(kw)))
    txt = '\n'.join(lines) + '\n'
    with open(sys.argv[5], 'w', encoding='utf-8') as f:
        f.write(txt)
    print(txt)


if __name__ == '__main__':
    main()
