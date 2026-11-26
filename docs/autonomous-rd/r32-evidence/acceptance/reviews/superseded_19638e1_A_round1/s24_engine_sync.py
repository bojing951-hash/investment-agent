#!/usr/bin/python3 -I
"""Read-only: locate the engine history sync face in report.json and compare it with
(a) the labels hard-coded in s10_recompute.py (ENGINE_SYNC) and
(b) the inflation-dimension labels written by the judgment (reader_map.history_periods[*].other_regions_sync).

Usage:
  python3 -I s24_engine_sync.py <report.json> <agent_judgment.json> <s10_recompute.py> <out.json>
The out.json file lists the 9 judgment-vs-engine label comparisons (for appending to the ledger).
"""
import json
import re
import sys

LAB = re.compile(u'中国(同步|分化|不同步|缺证)、欧元区(同步|分化|不同步|缺证)、日本(同步|分化|不同步|缺证)')
NAME = {u'中国': 'CN', u'欧元区': 'EA', u'日本': 'JP'}
PERIODS = ['2025-03', '2022-06', '2023-10']


def find_sync(o, path, out, depth=0):
    """collect dicts that look like region x dimension sync rows."""
    if isinstance(o, dict):
        keys = set(o.keys())
        if {'region', 'dimension'} <= keys and ('label' in keys or 'sync_label' in keys or 'sync' in keys):
            out.append((path, o))
        for k, v in o.items():
            if isinstance(v, (dict, list)) and depth < 14:
                find_sync(v, path + '.' + str(k), out, depth + 1)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            if isinstance(v, (dict, list)) and depth < 14:
                find_sync(v, path + '[%d]' % i, out, depth + 1)


def main():
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        rep = json.load(f)
    with open(sys.argv[2], 'r', encoding='utf-8') as f:
        jud = json.load(f)
    src = open(sys.argv[3], encoding='utf-8').read()
    rows = []
    find_sync(rep, 'report', rows)
    print('sync-like dicts found: %d' % len(rows))
    if rows:
        print('first path:', rows[0][0])
        print('first row :', json.dumps(rows[0][1], ensure_ascii=False)[:600])
    # engine labels keyed by (period, region, dimension)
    eng = {}
    for path, r in rows:
        per = r.get('anchor') or r.get('period') or r.get('candidate') or r.get('month') or r.get('as_of') or r.get('date')
        reg = r.get('region')
        dim = r.get('dimension')
        lab = r.get('sync_label') or r.get('label') or r.get('sync')
        eng[(str(per)[:7], reg, dim)] = (lab, path)
    print('engine label cells: %d ; sample keys: %s' % (len(eng), sorted(eng.keys())[:6]))
    # (a) compare with ENGINE_SYNC in the recompute script
    m = re.search(r'ENGINE_SYNC = \{(.*?)\n\}', src, re.S)
    blk = m.group(1)
    hard = {}
    for pm in re.finditer(r"'(\d{4}-\d{2})': \[(.*?)\]", blk, re.S):
        items = re.findall(r"'([A-Z]{2}) (growth|inflation|policy) ([^']+)'", pm.group(2))
        for reg, dim, lab in items:
            hard[(pm.group(1), reg, dim)] = lab
    print('hard-coded labels: %d' % len(hard))
    bad = 0
    if eng:
        for k, lab in hard.items():
            e = eng.get(k)
            # period key in engine may be an as_of month (e.g. 2025-03-31) -> already truncated to 7 chars
            if e is None:
                # try to find by suffix
                cand = [kk for kk in eng if kk[1] == k[1] and kk[2] == k[2] and kk[0].endswith(k[0][5:])]
                e = eng[cand[0]] if cand else None
            ok = e is not None and e[0] == lab
            if not ok:
                bad += 1
                print('  MISMATCH hard-coded vs engine:', k, lab, e)
        print('hard-coded vs engine face mismatches: %d' % bad)
    # (b) judgment inflation labels vs engine inflation cells
    out = []
    hp = jud['reader_map']['history_periods']
    for h in hp:
        txt = h.get('other_regions_sync', '')
        mm = LAB.search(txt)
        an = None
        for p in PERIODS:
            if p in json.dumps(h, ensure_ascii=False)[:400]:
                an = p
                break
        print('--- history period', an, '| lead word:', txt[:12])
        if not mm:
            print('   no label triple found')
            continue
        for nm, lab in zip((u'中国', u'欧元区', u'日本'), mm.groups()):
            reg = NAME[nm]
            e = None
            for k, v in eng.items():
                if k[1] == reg and k[2] == 'inflation' and (k[0] == an or k[0].endswith(an[5:])):
                    e = v
            print('   judgment %s inflation = %s ; engine = %s (%s)' % (reg, lab, None if e is None else e[0], '' if e is None else e[1][-50:]))
            out.append({'period': an, 'region': reg, 'dimension': 'inflation', 'judgment_label': lab,
                        'engine_label': None if e is None else e[0], 'engine_path': None if e is None else e[1]})
    with open(sys.argv[4], 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print('wrote %d comparisons' % len(out))


if __name__ == '__main__':
    main()
