#!/usr/bin/python3 -I
"""Read-only check: does each item.original / fix fragment of the verdict file occur verbatim in the audited text?

Usage:
  python3 -I s25_check_originals.py <VERDICT-round1.json> <agent_judgment.json> <MAP_REPORT.md>
"""
import difflib
import json
import re
import sys


def main():
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        v = json.load(f)
    with open(sys.argv[2], 'r', encoding='utf-8') as f:
        jud_txt = json.dumps(json.load(f), ensure_ascii=False)
    with open(sys.argv[3], 'r', encoding='utf-8') as f:
        rep_txt = f.read()
    jud_plain = jud_txt.encode('utf-8').decode('unicode_escape') if False else jud_txt
    # unescaped view of the judgment text (join of all string leaves)
    leaves = []

    def walk(o):
        if isinstance(o, str):
            leaves.append(o)
        elif isinstance(o, dict):
            for k in o:
                walk(o[k])
        elif isinstance(o, list):
            for x in o:
                walk(x)

    with open(sys.argv[2], 'r', encoding='utf-8') as f:
        walk(json.load(f))
    leaves_txt = '\n'.join(leaves)
    sents = re.split(r'(?<=[。；;])', leaves_txt)
    sents = [s.strip() for s in sents if s.strip()]
    bad = 0
    for i, it in enumerate(v['items']):
        orig = it.get('original', '')
        if not orig:
            continue
        found_j = orig in leaves_txt
        found_r = orig in rep_txt
        # also test after normalising whitespace
        norm = lambda s: re.sub(r'\s+', '', s)
        found_jn = norm(orig) in norm(leaves_txt)
        found_rn = norm(orig) in norm(rep_txt)
        ok = found_jn or found_rn
        if not ok:
            bad += 1
        print('item %d [%s] original in judgment=%s report=%s (ws-normalised %s/%s)' % (
            i, it['severity'], found_j, found_r, found_jn, found_rn))
        if not ok:
            best = difflib.get_close_matches(norm(orig), [norm(s) for s in sents], n=2, cutoff=0.6)
            for b in best:
                print('   closest: %s' % b[:400])
    print('items with original not found verbatim: %d' % bad)


if __name__ == '__main__':
    main()
