#!/usr/bin/python3 -I
"""Read-only: print the structure of the agent seat envelope's engine faces and the
text of the envelope's role/produce/discipline/read_first fields (for provenance notes).

Usage:
  python3 -I s33_envelope_pool.py <AGENT_SEAT_ENVELOPE.json>
"""
import json
import sys


def size(v):
    try:
        return len(v)
    except TypeError:
        return None


def main():
    env = json.load(open(sys.argv[1], encoding='utf-8'))
    print('top keys:', sorted(env.keys()))
    for k in sorted(env.keys()):
        v = env[k]
        print('  %s: %s len=%s' % (k, type(v).__name__, size(v)))
    rc = env.get('reader_map_contract', {})
    print('reader_map_contract keys:', sorted(rc.keys()))
    ef = rc.get('engine_faces', {})
    print('engine_faces keys:')
    for k in ef:
        v = ef[k]
        print('  %s: %s len=%s' % (k, type(v).__name__, size(v)))
        if any(w in k.lower() for w in ('polic', 'pool', 'turning')):
            print(json.dumps(v, ensure_ascii=False)[:6000])
    for k in ('role', 'produce', 'discipline', 'read_first', 'then'):
        if k in env:
            print('--- %s: %s' % (k, json.dumps(env[k], ensure_ascii=False)[:1800]))
    print('--- reader_map_contract.discipline: %s' % json.dumps(rc.get('discipline'), ensure_ascii=False)[:1800])


if __name__ == '__main__':
    main()
