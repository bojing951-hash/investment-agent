#!/usr/bin/python3 -I
"""entry_v2_post.py — read-only post-processing of the same-day re-run of the standard update entry
(tag VRENTRY) at the final stamp: its pipeline log copied out of the tree, the Gate A block of the new
snapshot (data/daily/research_snapshot_20261124_v2.json) extracted as text with a header, and the ledger
line. The snapshot itself stays in the tree (it carries collected market data; only its Gate A block
and scalar quality fields are copied)."""
import glob
import json
import os
import shutil
import time

OUT = '/tmp/r32-accept/out'
TREE = '/tmp/r32-accept/final9-entry'
meta = sorted(glob.glob(os.path.join(OUT, 'VRENTRY_update_*.meta')))[-1]
name = os.path.basename(meta).replace('.meta', '.json')
rec = json.load(open(os.path.join(OUT, name), encoding='utf-8'))
lines = [l.strip() for l in open(meta, encoding='utf-8') if l.strip()]
rc = [l for l in lines if l.startswith('rc=')][-1][3:]
tail = rec['data']['output_tail']
res = [x.strip() for x in tail if x.strip().startswith('结果:')]
steps_ok = res[0].split()[1] if res else '?'   # the pipeline's own summary line, e.g. 结果: 15/15 步骤成功
shutil.copyfile(os.path.join(TREE, 'logs', 'pipeline_run_20261124.json'), os.path.join(OUT, 'VRENTRY_pipeline_log.json'))

snap = os.path.join(TREE, 'data', 'daily', 'research_snapshot_20261124_v2.json')
s = json.load(open(snap, encoding='utf-8'))
g = s.get('gate_a') or {}
head = ['# Gate A block of the snapshot built by the same-day re-run of the standard entry at the final stamp cf33de3',
        '# (2026-11-24T08:58:14Z..09:13:01Z = 16:58:14..17:13:01 HKT, rc=%s, steps ok %s; option --allow-revision with a recorded reason)' % (rc, steps_ok),
        '# Source: data/daily/research_snapshot_20261124_v2.json of the clean install tree (immutable file; kept in the tree, not copied:',
        '# it carries collected market data). research_as_of=%s target_date=%s snapshot_id=%s' % (
            s.get('research_as_of'), s.get('target_date'), s.get('snapshot_id')),
        '# The first run of the day (research_snapshot_20261124.json, 16:10:06 HKT, rc=1) stays untouched next to it.',
        '# Quality fields of the new snapshot: ' + '; '.join('%s=%s' % (k, s.get(k)) for k in (
            'allow_formal_report', 'n_series', 'quality', 'degraded', 'revision', 'revision_reason', 'supersedes') if k in s),
        '# Values below are the Gate A block as stored; copied verbatim as JSON.', '',
        json.dumps(g, ensure_ascii=False, indent=1)]
open(os.path.join(OUT, 'VRENTRY_gate_a_v2_snapshot.txt'), 'w', encoding='utf-8').write('\n'.join(head) + '\n')
open(os.path.join(OUT, 'ux_VRENTRY.log'), 'w', encoding='utf-8').write('/tmp/r32-accept/out/%s rc=%s\n' % (name, rc))

with open('/tmp/r32-accept/seat_operator.log', 'a', encoding='utf-8') as f:
    f.write('%s op stage=update-end tag=VRENTRY stamp=cf33de3 rc=%s note=(standard entry re-run on the same day through its '
            'documented revision option (--allow-revision --revision-reason): ok=%s exit_code=%s steps ok %s; total %s s; '
            'snapshot research_snapshot_20261124_v2; Gate A status=%s core_missing %d noncore_missing %d noncore_degraded %d; '
            'the failed first run of the day is kept as evidence (receipt VENTRY_update_20261124T081006Z); cause of that failure '
            'and the unfixed defect are stated in the acceptance report)\n' % (
                time.strftime('%Y-%m-%d %H:%M:%S'), rc, rec.get('ok'), rec['data'].get('exit_code'), steps_ok,
                [x for x in rec['data']['output_tail'] if '总耗时' in x][-1].strip() if any('总耗时' in x for x in rec['data']['output_tail']) else '?',
                g.get('status'), len(g.get('core_missing') or []), len(g.get('noncore_missing') or []),
                len(g.get('noncore_degraded') or [])))
print('rc', rc, 'steps ok', steps_ok)
print('gate_a status', g.get('status'), 'core_missing', len(g.get('core_missing') or []), 'noncore_missing',
      len(g.get('noncore_missing') or []), 'noncore_degraded', len(g.get('noncore_degraded') or []))
print('top-level scalar keys:', {k: s[k] for k in s if isinstance(s[k], (str, int, float, bool)) and len(str(s[k])) < 90})
print('gate_a keys:', {k: (v if isinstance(v, (str, int, float, bool)) else 'list[%d]' % len(v)) for k, v in g.items()})
