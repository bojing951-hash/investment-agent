#!/usr/bin/python3 -I
"""Read-only: print the judgment blocks the prose tail needs to quote exactly
(agent_declaration, quality_gate_notes, transmission links, turnings, turning_supplement, headline).

Usage:
  python3 -I s30c_dump_notes.py <agent_judgment.json>
"""
import json
import sys


def main():
    jud = json.load(open(sys.argv[1], encoding='utf-8'))
    print('top keys:', list(jud.keys()))
    rm = jud['reader_map']
    print('reader_map keys:', list(rm.keys()))
    ad = jud.get('agent_declaration')
    print('=== agent_declaration')
    print(json.dumps(ad, ensure_ascii=False, indent=1))
    print('=== quality_gate_notes')
    for i, n in enumerate(jud.get('quality_gate_notes', [])):
        print('[%d] %s' % (i, n if isinstance(n, str) else json.dumps(n, ensure_ascii=False)))
    print('=== headline_conclusion')
    print(rm.get('headline_conclusion'))
    print('=== turnings')
    for i, t in enumerate(rm.get('turnings', [])):
        print(json.dumps(t, ensure_ascii=False, indent=1))
    print('=== turning_supplement')
    for i, t in enumerate(rm.get('turning_supplement', [])):
        print(json.dumps(t, ensure_ascii=False, indent=1))
    print('=== transmission')
    for i, t in enumerate(rm.get('transmission', [])):
        for k, v in t.items():
            if k == 'links':
                for j, l in enumerate(v):
                    print('transmission[%d].links[%d]:' % (i, j))
                    print(json.dumps(l, ensure_ascii=False, indent=1))
            else:
                print('transmission[%d].%s = %s' % (i, k, json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v))
    print('=== history_periods')
    for i, h in enumerate(rm.get('history_periods', [])):
        print(json.dumps(h, ensure_ascii=False, indent=1))
    print('=== other reader_map string blocks')
    for k, v in rm.items():
        if k in ('headline_conclusion', 'turnings', 'turning_supplement', 'transmission', 'history_periods', 'regions'):
            continue
        print('--- %s' % k)
        print(json.dumps(v, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
