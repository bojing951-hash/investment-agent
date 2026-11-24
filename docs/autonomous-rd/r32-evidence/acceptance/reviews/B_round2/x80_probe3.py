# -*- coding: utf-8 -*-
# x80_probe3.py — 终装配前的自检探针(只读; 只打印, 不写任何文件)
# 用法: python3 -I x80_probe3.py <RUN_DIR> <SNAPSHOT_JSON> <B_DIR>
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r00_common import *
import r80a_points

NL = chr(10)


def main():
    RUN, SNAPP, B = sys.argv[1], sys.argv[2], sys.argv[3]
    ERR = []
    out = []
    out.append('run dir listing: %s' % sorted(os.listdir(RUN)))
    ov = os.path.join(RUN, 'root_overlay')
    out.append('root_overlay listing: %s' % (sorted(os.listdir(ov)) if os.path.isdir(ov) else 'ABSENT'))
    for root, ds, fs in os.walk(ov):
        for fn in fs:
            out.append('  overlay file: %s' % os.path.relpath(os.path.join(root, fn), RUN))
    rep = load(os.path.join(RUN, 'report.json'))
    aj = load(os.path.join(RUN, 'agent_judgment.json'))
    calp = None
    for root, ds, fs in os.walk(ov):
        if 'release_calendar.json' in fs:
            calp = os.path.join(root, 'release_calendar.json')
    cal = load(calp) if calp else {}
    out.append('calendar path: %s  type=%s  top keys=%s' % (calp, type(cal).__name__, sorted(cal.keys()) if isinstance(cal, dict) else len(cal)))
    ce = r80a_points.cal_entries(cal)
    out.append('calendar entries: %d' % len(ce))
    for e in ce:
        out.append('   %s | %s | %s' % (e.get('entry_id'), e.get('first_publish_on_or_after'), sorted(e.keys())))
    snap = load(SNAPP)
    sn = Snap(snap)
    RAW = dict((fn, open(os.path.join(RUN, fn), encoding='utf-8').read()) for fn in ('MAP_REPORT.md', 'FULL_REPORT.md', 'report.md'))
    R = r80a_points.build(sn, rep, aj, cal, RAW, B, ERR)
    out.append('ERR: %s' % ERR)
    cnt = {}
    for p in R['ALLP']:
        k = (p['id'][0], p.get('cat'))
        cnt[k] = cnt.get(k, 0) + 1
    for k in sorted(cnt, key=lambda t: (t[0], str(t[1]))):
        out.append('cat %s  n=%d' % (k, cnt[k]))
    out.append('ALL=%d NEW=%d ALLP=%d COUNTED=%d INFO=%s DUP=%s' % (len(R['ALL']), len(R['NEW']), len(R['ALLP']), len(R['COUNTED']), [p['id'] for p in R['INFOP']], [(p['id'], p.get('_dup_of')) for p in R['DUPP']]))
    out.append('non-ok counted: %s' % [p['id'] for p in R['COUNTED'] if not p['ok']])
    out.append('--- NEW points ---')
    for p in R['NEW']:
        out.append('%s ok=%s comp=%s rep=%s cls=%s | %s' % (p['id'], p['ok'], p['computed'], p['reported'], p['_cls'], p['note'][:200] if p.get('note') else ''))
    out.append('--- EX keys ---')
    for k in sorted(R['EX']):
        v = R['EX'][k]
        s = json.dumps(v, ensure_ascii=False, default=str)
        out.append('%s = %s' % (k, s[:600]))
    out.append('--- V ---')
    for k in sorted(R['V']):
        s = json.dumps(R['V'][k], ensure_ascii=False, default=str)
        out.append('%s = %s' % (k, s[:900]))
    out.append('--- AJ DUMP (全文) ---')
    out.append(json.dumps(aj, ensure_ascii=False, indent=1, default=str))
    s6 = R['V']['s6']
    out.append('--- s6 keys ---')
    for k in s6:
        s = json.dumps(s6[k], ensure_ascii=False, default=str)
        out.append('%s = %s' % (k, s[:700]))
    out.append('--- point record sample ---')
    for p in (R['ALL'][0], R['ALL'][-1]):
        out.append(json.dumps(p, ensure_ascii=False, default=str))
    out.append('--- Z ---')
    for z in R['Z']:
        out.append('%s | %s | %s' % (z['name'], z['key'], json.dumps(z['value'], ensure_ascii=False, default=str)[:500]))
    txt = NL.join(out)
    print(txt)
    with open(os.path.join(B, 'x80_probe3.txt'), 'w', encoding='utf-8') as f:
        f.write(txt)


main()
