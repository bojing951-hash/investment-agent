#!/usr/bin/python3 -I
"""Seat-internal: count ledger rows by id suffix within a section (read-only).

Usage:
  python3 -I s30e_ledger_suffix.py <points_all.jsonl> <section> [<section> ...]
"""
import json
import sys
import re
from collections import Counter


def main():
    rows = [json.loads(x) for x in open(sys.argv[1], encoding='utf-8') if x.strip()]
    for sec in sys.argv[2:]:
        c = Counter()
        ex = {}
        for r in rows:
            if r['section'] != sec:
                continue
            pid = r['id']
            if ':' in pid:
                suf = pid.split(':', 1)[1]
            else:
                suf = re.sub(r'\d{4}-\d{2}(-\d{2})?', '<D>', pid)
                suf = re.sub(r'-?\d+(\.\d+)?', '<n>', suf)
            c[suf] += 1
            ex.setdefault(suf, pid)
        print('=== %s (%d rows)' % (sec, sum(c.values())))
        for k, n in sorted(c.items(), key=lambda kv: -kv[1]):
            print('  %4d  %-60s e.g. %s' % (n, k, ex[k]))


if __name__ == '__main__':
    main()
