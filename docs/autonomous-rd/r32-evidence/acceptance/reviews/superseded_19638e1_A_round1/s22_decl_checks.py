#!/usr/bin/python3 -I
"""Read-only: verify counts stated in agent_declaration and the CN anchor-switch record (information only).
Usage: python3 -I s22_decl_checks.py <evidence_index.json> <release_calendar.json> <metric_registry.json>
"""
import json
import sys


def main():
    ev = json.load(open(sys.argv[1], encoding='utf-8'))
    cal = json.load(open(sys.argv[2], encoding='utf-8'))
    reg = json.load(open(sys.argv[3], encoding='utf-8'))
    print('evidence_index top keys: %s' % (sorted(ev.keys()) if isinstance(ev, dict) else type(ev)))
    if isinstance(ev, dict):
        for k, v in ev.items():
            if isinstance(v, list):
                print('  %s: list len=%d' % (k, len(v)))
            elif isinstance(v, dict):
                print('  %s: dict len=%d' % (k, len(v)))
            else:
                print('  %s: %s' % (k, str(v)[:200]))
    txt = json.dumps(cal, ensure_ascii=False)
    for kw in ('2026-11-02', '隔夜', 'anchor', '政策利率锚'):
        print('calendar mentions of "%s": %d' % (kw, txt.count(kw)))
    for e in cal.get('entries', []):
        s = json.dumps(e, ensure_ascii=False)
        if '2026-11-02' in s or 'JP_POLICY' in s or '日本' in s or '隔夜' in s:
            print('entry: %s' % s[:700])
    rt = json.dumps(reg, ensure_ascii=False)
    for kw in ('JP_POLICY_TARGET', 'JP_POLICY_RATE', '2026-11-02', '隔夜逆回购', 'policy_anchor'):
        print('registry mentions of "%s": %d' % (kw, rt.count(kw)))


if __name__ == '__main__':
    main()


def extra(ev, reg):
    print('evidence_index rows: %d' % len(ev))
    if ev:
        print('  first row keys: %s' % sorted(ev[0].keys()) if isinstance(ev[0], dict) else ev[0])
    s = json.dumps(reg, ensure_ascii=False)
    i = 0
    shown = 0
    while shown < 5:
        i = s.find('2026-11-02', i)
        if i < 0:
            break
        print('  registry ctx: …%s…' % s[max(0, i - 160): i + 160].replace('\n', ' '))
        i += 10
        shown += 1
