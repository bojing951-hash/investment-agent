#!/usr/bin/python3 -I
"""Read-only on the run directory; rewrites only the seat ledger passed as argv[3].

1. Parse the three engine tables "地区×维度同步面" from MAP_REPORT.md (engine deterministic face).
2. Check every engine cell (3 periods x 12 rows) against the seat's rule-derived label recorded in the ledger
   (section "sync", id "sync <period> <region> <dim> label", field computed).
3. Compare the judgment's inflation-dimension labels (reader_map.history_periods[*].other_regions_sync,
   3 regions x 3 periods = 9) with the engine cells and append 9 counted rows to the ledger.
4. Turn the three trivial "sync labels present" rows (section history) into informational rows.

Usage:
  python3 -I s24_sync_labels.py <MAP_REPORT.md> <agent_judgment.json> <points_all.jsonl> <out.txt>
"""
import json
import re
import sys

DIM = {u'增长': 'growth', u'通胀': 'inflation', u'货币政策': 'policy'}
REG = {u'中国': 'CN', u'欧元区': 'EA', u'日本': 'JP'}
LAB = re.compile(u'中国(同步|分化|不同步|缺证)、欧元区(同步|分化|不同步|缺证)、日本(同步|分化|不同步|缺证)')
DIR = re.compile(u'\\((上行|下行|持平)\\)')


def parse_tables(lines):
    tables = {}
    period = None
    in_tbl = False
    for i, l in enumerate(lines):
        if l.startswith('### ') and re.match(r'### \d{4}-\d{2}', l):
            period = l[4:11]
        if l.startswith('- **地区×维度同步面'):
            in_tbl = True
            tables.setdefault(period, [])
            continue
        if in_tbl:
            if not l.strip():
                if tables[period]:
                    in_tbl = False
                continue
            if l.lstrip().startswith('|') and not set(l.replace('|', '').strip()) <= set('- '):
                cells = [c.strip() for c in l.strip().strip('|').split('|')]
                if len(cells) == 7 and cells[0] in DIM:
                    tables[period].append((i + 1, cells))
            elif not l.lstrip().startswith('|'):
                in_tbl = False
    return tables


def main():
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')
    with open(sys.argv[2], 'r', encoding='utf-8') as f:
        jud = json.load(f)
    rows = [json.loads(x) for x in open(sys.argv[3], encoding='utf-8') if x.strip()]
    out = []
    tables = parse_tables(lines)
    out.append('engine sync tables parsed: %s' % sorted((k, len(v)) for k, v in tables.items()))
    eng = {}
    for per, rs in tables.items():
        for ln, c in rs:
            dim, reg = DIM[c[0]], c[1]
            m = DIR.findall(c[5])
            dr = m[-1] if m else None
            cell = c[6]
            if reg == 'US':
                lab = dr
                base = cell.startswith(u'基准')
            else:
                lab = u'同步' if cell.startswith(u'同步') else (u'分化' if cell.startswith(u'分化') else (u'缺证' if cell.startswith(u'缺证') else cell))
                base = None
            eng[(per, reg, dim)] = {'dir': dr, 'label': lab, 'base': base, 'line': ln, 'cell': cell}
    out.append('engine cells: %d' % len(eng))
    # 2. compare with seat rule-derived labels in the ledger
    led = {}
    for r in rows:
        if r['section'] == 'sync' and r['id'].endswith(' label'):
            _, per, reg, dim, _ = r['id'].split(' ')
            led[(per, reg, dim)] = r
    n = 0
    bad = 0
    for k, r in sorted(led.items()):
        e = eng.get(k)
        ok = e is not None and e['label'] == r['computed']
        n += 1
        if not ok:
            bad += 1
        out.append('  seat-rule vs engine-table %s %s %s: seat=%s engine=%s (MAP_REPORT.md L%s) %s' % (
            k[0], k[1], k[2], r['computed'], None if e is None else e['label'], '' if e is None else e['line'], 'OK' if ok else 'MISMATCH'))
    out.append('seat-rule labels vs engine table: %d cells, mismatches %d' % (n, bad))
    # direction notes
    nb = 0
    for r in rows:
        if r['section'] == 'sync' and r['id'].endswith(' direction'):
            m = re.search(r'engine: ([A-Z]{2}) (growth|inflation|policy) (上行|下行|持平|同步|分化|缺证|NA)', r['note'])
            if m is None:
                nb += 1
                out.append('  direction note unparsable: %s | %s' % (r['id'], r['note']))
                continue
            per = r['id'].split(' ')[1]
            e = eng.get((per, m.group(1), m.group(2)))
            # US rows carry the direction, other rows carry the label
            if e is None:
                nb += 1
                out.append('  direction note: engine cell not found for %s | %s' % (r['id'], r['note']))
                continue
            want = e['dir'] if m.group(1) == 'US' else e['label']
            if want != m.group(3):
                nb += 1
                out.append('  direction/label note mismatch: %s | %s | table=%s' % (r['id'], r['note'], want))
    out.append('engine direction notes vs engine table: mismatches %d' % nb)
    # 3. judgment inflation labels vs engine
    new_rows = []
    jn = 0
    jbad = 0
    for h in jud['reader_map']['history_periods']:
        per = None
        for key in ('period', 'anchor', 'candidate', 'month', 'id'):
            v = h.get(key)
            if isinstance(v, str) and re.match(r'\d{4}-\d{2}', v):
                per = v[:7]
                break
        if per is None:
            m = re.search(r'(\d{4}-\d{2})', json.dumps(h, ensure_ascii=False)[:300])
            per = m.group(1)
        txt = h['other_regions_sync']
        m = LAB.search(txt)
        lead = txt[:txt.find(u':')] if u':' in txt[:12] else txt[:6]
        if not m:
            out.append('  no label triple in judgment period %s' % per)
            jbad += 1
            continue
        for nm, lab in zip((u'中国', u'欧元区', u'日本'), m.groups()):
            reg = REG[nm]
            e = eng.get((per, reg, 'inflation'))
            el = None if e is None else e['label']
            ok = el == lab
            jn += 1
            if not ok:
                jbad += 1
            out.append('  judgment %s %s inflation=%s ; engine table=%s (L%s) %s ; lead word=%s' % (
                per, reg, lab, el, '' if e is None else e['line'], 'OK' if ok else 'MISMATCH', lead))
            new_rows.append({'section': 'sync', 'id': 'sync %s judgment %s inflation label' % (per, reg),
                             'src': 'MAP_REPORT.md L%s 地区×维度同步面(引擎确定性面)' % ('' if e is None else e['line']),
                             'computed': el, 'reported': lab, 'ok': ok,
                             'note': u'判断档 other_regions_sync 通胀维标签 vs 引擎面(引导词 %s)' % lead})
    out.append('judgment inflation labels vs engine table: %d cells, mismatches %d' % (jn, jbad))
    # 4. rewrite ledger
    changed = 0
    if jn == 9 and bad == 0 and nb == 0:
        for r in rows:
            if r['section'] == 'history' and r['id'].endswith(' sync labels present'):
                if r.get('reported') == 'present':
                    r['reported'] = None
                    r['note'] = u'informational: 标签三联在场(逐格比对见 sync 节 judgment 行)'
                    changed += 1
        have = set(r['id'] for r in rows)
        added = 0
        for nr in new_rows:
            if nr['id'] not in have:
                rows.append(nr)
                added += 1
        with open(sys.argv[3], 'w', encoding='utf-8') as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        cnt = sum(1 for r in rows if not (r.get('reported') is None and r.get('computed') is not None))
        okc = sum(1 for r in rows if not (r.get('reported') is None and r.get('computed') is not None) and r.get('ok'))
        info = sum(1 for r in rows if r.get('reported') is None and r.get('computed') is not None)
        out.append('ledger rewritten: rows=%d counted=%d ok=%d informational=%d (present-rows -> informational: %d, judgment rows added: %d)' % (
            len(rows), cnt, okc, info, changed, added))
    else:
        out.append('ledger NOT rewritten (preconditions failed: jn=%d bad=%d nb=%d)' % (jn, bad, nb))
    txt = '\n'.join(out) + '\n'
    with open(sys.argv[4], 'w', encoding='utf-8') as f:
        f.write(txt)
    print(txt)


if __name__ == '__main__':
    main()
