#!/usr/bin/env python3
"""dryverify.py <tree> <run_dir> <judgment.json>   (read-only attach rehearsal)

Runs exactly the two gates attach applies — agent_judgment.validate_judgment
(structure + policy) and judgment_contract.verify_judgment (facts vs the
run's own evidence face) — without writing anything into the run dir."""
import json
import os
import sys

tree, run_dir, jpath = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, os.path.join(tree, 'scripts'))
sys.path.insert(0, os.path.join(tree, 'scripts', 'research_contract'))
os.chdir(tree)
import agent_judgment as aj                                   # noqa: E402
from research_contract.judgment_contract import verify_judgment  # noqa: E402

report = json.load(open(os.path.join(run_dir, 'report.json'), encoding='utf-8'))
J = json.load(open(jpath, encoding='utf-8'))
ev_refs = {e.get('ref') for e in report.get('evidence_index') or [] if e.get('ref')}
mids = aj._registry_metric_ids(tree)
_asof = ((report.get('run') or {}).get('evidence_asof')
         or (report.get('research_plan') or {}).get('cutoff'))
cal = os.environ.get('IA_CALENDAR_PIN') or os.path.join(tree, 'config', 'release_calendar.json')
res = aj.validate_judgment(J, ev_refs, mids, policy_events=aj.collect_policy_events(cal),
                           as_of=_asof if isinstance(_asof, str) else None)
print('as_of', _asof, '| validate_judgment passed', res['passed'],
      'violations', len(res['violations']))
for v in res['violations']:
    print('  V', v['code'], '|', v.get('where'), '|', str(v.get('detail'))[:220])
contract = verify_judgment(J, report)
print('verify_judgment verdict', contract.get('verdict'), 'stats', json.dumps(contract.get('stats'), ensure_ascii=False)[:400])
if contract.get('error'):
    print('  error', contract['error'])
for v in contract.get('verdicts') or []:
    if v.get('status') not in ('VERIFIED',):
        print('  V', v.get('status'), '|', v.get('item'), '|', v.get('metric'), '|',
              'claim', v.get('claimed') or v.get('value'), '|', str(v.get('note'))[:200])
for u in contract.get('unresolved_unbound') or []:
    print('  U unbound |', u.get('item'), '|', u.get('raw'), '|', str(u.get('ctx'))[:120], '|', u.get('reason'))
for c in (contract.get('six_checks') or []) + (contract.get('map_checks') or []):
    if c.get('status') != 'VERIFIED':
        print('  M', c.get('status'), '|', c.get('item'), c.get('check') or '', '|', str(c.get('note'))[:300])
sys.exit(0 if (res['passed'] and contract.get('verdict') == 'VERIFIED') else 1)
