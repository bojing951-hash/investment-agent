#!/usr/bin/env python3
"""Scan S3-S8 step envelopes for values dated after the research cutoff.

Usage: python3 -I scan_steps_late.py <report.json>

For every step with an envelope, walk the payload and collect every
(node-path, date) pair where a date-like string value later than the cutoff
appears under a date-bearing key (observation_date / basis_date / end_date /
anchor / as_of / date / last / latest ...). Summarises per step.
"""
import json
import re
import sys

DATE_KEYS = ('observation_date', 'basis_date', 'end_date', 'anchor',
             'anchor_ym', 'as_of', 'date', 'last', 'latest_observation',
             'latest', 'period_end', 'target_date', 'research_as_of',
             'decision_date', 'effective_on', 'first_publish',
             'cutoff', 'anchor_date', 'month', 'ym')
ISO = re.compile(r'^\d{4}-\d{2}-\d{2}$')
YM = re.compile(r'^\d{4}-\d{2}$')


def walk(node, path, out, cut):
    if isinstance(node, dict):
        for k, v in node.items():
            walk(v, path + '.' + str(k), out, cut)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, '%s[%d]' % (path, i), out, cut)
    elif isinstance(node, str):
        leaf = path.rsplit('.', 1)[-1].split('[')[0]
        if ISO.match(node) and node > cut:
            out.append((path, node))
        elif leaf in DATE_KEYS and YM.match(node) and node > cut[:7]:
            out.append((path, node))


def main(p):
    r = json.load(open(p, encoding='utf-8'))
    cut = (r.get('research_plan') or {}).get('cutoff')
    print('cutoff=%s' % cut)
    for s in r.get('steps') or []:
        env = s.get('envelope')
        if not isinstance(env, dict):
            continue
        out = []
        walk(env, '', out, cut)
        top = env.get('data') if isinstance(env.get('data'), dict) else {}
        extra = ''
        if s['step'] == 'S6_analog' and isinstance(top, dict):
            extra = ' anchor=%s' % (top.get('anchor_ym') or top.get('anchor'))
        if s['step'] == 'S3_changes' and isinstance(top, dict):
            extra = ' keys=%s' % list(top.keys())[:8]
        if s['step'] == 'S8_grounded_qa' and isinstance(top, dict):
            extra = ' status=%s' % (top.get('status'),)
        print('%-28s ok=%-5s late_date_nodes=%-5d sample=%s%s' % (
            s['step'], s.get('ok'), len(out),
            sorted({d for _, d in out})[-3:], extra))


if __name__ == '__main__':
    main(sys.argv[1])
