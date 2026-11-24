#!/usr/bin/python3 -I
"""Seat-internal: list ledger rows with unusual value shapes (read-only).

Usage:
  python3 -I s30b_ledger_odd.py <points_all.jsonl>
"""
import json
import sys


def main():
    rows = [json.loads(x) for x in open(sys.argv[1], encoding='utf-8') if x.strip()]
    print('=== rows with computed None and reported None')
    for r in rows:
        if r.get('computed') is None and r.get('reported') is None:
            print(json.dumps(r, ensure_ascii=False))
    print('=== rows with computed None and reported not None (absence claims)')
    for r in rows:
        if r.get('computed') is None and r.get('reported') is not None:
            print(json.dumps(r, ensure_ascii=False)[:400])
    print('=== rows with computed str and reported bool')
    for r in rows:
        if isinstance(r.get('computed'), str) and isinstance(r.get('reported'), bool):
            print(json.dumps(r, ensure_ascii=False)[:400])
    print('=== rows with computed list')
    for r in rows:
        if isinstance(r.get('computed'), list):
            print(json.dumps(r, ensure_ascii=False)[:400])


if __name__ == '__main__':
    main()
