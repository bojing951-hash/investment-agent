#!/usr/bin/env python3
"""runfacts.py <run_dir> [<run_dir> ...]

Print the engine-side facts of one R32 acceptance run that the acceptance
record quotes (read-only; report.json / evidence_index.json of the run dir).
Every value is read from the run's own files; nothing is recomputed here."""
import hashlib
import json
import os
import sys


def sha16(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()[:16]


def short(v, n=260):
    s = json.dumps(v, ensure_ascii=False)
    return s if len(s) <= n else s[:n] + '…'


for rd in sys.argv[1:]:
    rep = json.load(open(os.path.join(rd, 'report.json'), encoding='utf-8'))
    run = rep['run']
    rp = rep['research_plan']
    eg = run.get('evidence_gate') or {}
    print('==', os.path.basename(rd))
    print('  git_head      ', run.get('git_head'), '| ts_utc', run.get('ts_utc'))
    print('  run_ok        ', rep.get('run_ok'), '| steps', len(rep['steps']),
          'not-ok', sum(1 for s in rep['steps'] if not (isinstance(s, dict) and s.get('ok') is True)))
    print('  question      ', run.get('question'))
    print('  cutoff        ', rp.get('cutoff'), '| as_of_declared', short(rp.get('as_of_declared'), 520))
    print('  frozen_inputs ', short(run.get('frozen_inputs'), 420))
    for k in ('evidence_asof', 'discipline', 'historical_view', 'publication_basis', 'vintage_basis',
              'revised_series', 'excluded_series', 'counts'):
        if k in eg:
            print('  evidence_gate.', k, short(eg[k], 420))
    pv = rp.get('point_values') or {}
    cells = pv.get('cells') or []
    st = {}
    nonok = []
    nanch = 0
    for c in cells:
        for lab, a in (c.get('anchors') or {}).items():
            nanch += 1
            s = a.get('status')
            st[s] = st.get(s, 0) + 1
            if s != 'ok':
                nonok.append('%s@%s: %s %s' % (c.get('metric_id'), lab, s, a.get('reason') or a.get('note') or ''))
    print('  point_values  ', 'cells', len(cells), 'anchors', nanch, 'statuses', st,
          '| planned-but-absent', [(x.get('metric_id'), x.get('gap')) for x in (pv.get('absent') or [])])
    for x in nonok:
        print('      non-ok', x[:330])
    print('  point_anchors ', short(rp.get('point_anchors'), 420))
    regions = {k: {d: [m.get('metric_id') for m in v] for d, v in (r.get('dimensions') or {}).items()}
               for k, r in (rp.get('regions') or {}).items()}
    print('  regions       ', short(regions, 700), '| dimensions', rp.get('dimensions'))
    print('  n metrics     ', len(rp.get('metrics') or []), '| metric ids',
          short([m.get('id') if isinstance(m, dict) else m for m in (rp.get('metrics') or [])], 520))
    print('  dimension_gaps', short(rp.get('dimension_gaps'), 900))
    mq = rp.get('map_question')
    if isinstance(mq, dict):
        print('  map_question  ', short(mq, 900))
    sr = rep.get('semantic_review')
    print('  semantic_review', short(sr, 400))
    for name in ('MAP_REPORT.md', 'FULL_REPORT.md', 'report.md', 'evidence_index.json', 'agent_judgment.json',
                 'AGENT_SEAT_ENVELOPE.json', 'views_digest.json'):
        p = os.path.join(rd, name)
        if os.path.exists(p):
            print('  file %-22s %7d bytes sha16 %s' % (name, os.path.getsize(p), sha16(p)))
    ev = os.path.join(rd, 'evidence_index.json')
    if os.path.exists(ev):
        idx = json.load(open(ev, encoding='utf-8'))
        items = idx if isinstance(idx, list) else (idx.get('items') or idx.get('refs') or [])
        kinds = {}
        late = 0
        cutoff = str(rp.get('cutoff'))
        for it in items:
            if isinstance(it, dict):
                kinds[it.get('kind') or it.get('source')] = kinds.get(it.get('kind') or it.get('source'), 0) + 1
                d = str(it.get('obs_date') or it.get('date') or it.get('as_of') or '')
                if d[:10] > cutoff and d[:4].isdigit():
                    late += 1
        print('  evidence_index items', len(items), 'kinds', kinds, '| date>cutoff', late,
              '| top keys', short(sorted(idx.keys()) if isinstance(idx, dict) else ['<list>'], 300))
