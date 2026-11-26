#!/usr/bin/python3 -I
"""Seat-internal: print ledger rows whose id/note contains any of the given substrings (read-only).

Usage:
  python3 -I s30d_ledger_grep.py <points_all.jsonl> <substr> [<substr> ...]
"""
import json
import sys


def main():
    rows = [json.loads(x) for x in open(sys.argv[1], encoding='utf-8') if x.strip()]
    pats = sys.argv[2:]
    n = 0
    for r in rows:
        blob = json.dumps(r, ensure_ascii=False)
        if all(p in blob for p in pats):
            n += 1
            print('%s | %s | computed=%s | reported=%s | ok=%s | src=%s | note=%s' % (
                r['section'], r['id'], json.dumps(r.get('computed'), ensure_ascii=False),
                json.dumps(r.get('reported'), ensure_ascii=False), r.get('ok'), r.get('src'), r.get('note')))
    print('-- %d rows' % n)


if __name__ == '__main__':
    main()
