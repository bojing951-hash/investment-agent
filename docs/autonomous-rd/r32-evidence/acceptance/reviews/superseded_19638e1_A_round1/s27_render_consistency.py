#!/usr/bin/python3 -I
"""Read-only: are the numbers in the judgment text rendered identically in the reader reports?

Usage:
  python3 -I s27_render_consistency.py <agent_judgment.json> <MAP_REPORT.md> <FULL_REPORT.md> <out.txt>
"""
import json
import re
import sys

NUM = re.compile(r'(?<![A-Za-z0-9_.])-?\d+(?:\.\d+)?')
CJK = re.compile(u'[一-鿿]')

# full-width punctuation -> ASCII (code points, so the source stays plain ASCII)
TABLE = {0xFF0C: ',', 0x3002: '.', 0xFF1B: ';', 0xFF1A: ':', 0xFF08: '(', 0xFF09: ')',
         0xFF0D: '-', 0xFF5E: '~', 0x2192: '->', 0x3000: ' '}


def norm(s):
    return s.translate(TABLE)


def leaves(o, path, out):
    if isinstance(o, str):
        out.append((path, o))
    elif isinstance(o, dict):
        for k in o:
            leaves(o[k], path + '.' + k, out)
    elif isinstance(o, list):
        for i, x in enumerate(o):
            leaves(x, path + '[%d]' % i, out)


def main():
    jud = json.load(open(sys.argv[1], encoding='utf-8'))
    md = norm(open(sys.argv[2], encoding='utf-8').read())
    full = norm(open(sys.argv[3], encoding='utf-8').read())
    out = []
    leaves(jud, '', out)
    tot = 0
    miss_md = []
    miss_full = []
    for path, s in out:
        if not CJK.search(s):
            continue  # ids / metric names / ref lists
        for m in NUM.finditer(s):
            tok = m.group(0)
            tot += 1
            ctx = s[max(0, m.start() - 12):m.end() + 12]
            if tok not in md:
                miss_md.append((path, tok, ctx))
            if tok not in full:
                miss_full.append((path, tok, ctx))
    lines = ['judgment text leaves (with CJK only): %d ; numeric tokens: %d' % (len(out), tot),
             'tokens absent from MAP_REPORT.md: %d ; absent from FULL_REPORT.md: %d' % (len(miss_md), len(miss_full))]
    for name, lst in (('MAP_REPORT.md', miss_md), ('FULL_REPORT.md', miss_full)):
        for path, tok, ctx in lst[:120]:
            lines.append('  absent in %s :: %s :: token %s :: ...%s...' % (name, path[-70:], tok, ctx.replace('\n', ' ')))
    txt = '\n'.join(lines) + '\n'
    open(sys.argv[4], 'w', encoding='utf-8').write(txt)
    print(txt)


if __name__ == '__main__':
    main()
