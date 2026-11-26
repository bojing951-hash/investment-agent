# s20_merge.py <snap> <rep> <cal> <reg> <aj> <out_prefix> <tag...>  -- merge part results, list uncovered numeric tokens
import sys
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from rc_common import *
c = Ctx(*sys.argv[1:7])
pre = sys.argv[6]; tags = sys.argv[7:]
pts = []; diag = []; cc = {}
for tg in tags:
    d = load(pre + '_' + tg + '.json')
    pts += d['points']; diag += d['diag']
    for x in d['cover']:
        cc.setdefault(x[0], set()).update(range(x[1], x[2]))
n_b = len(pts)
pts = [p for p in pts if '证据索引各行 value 与 series_store 同日值一致' not in p['src']]
print('excluded hollow points', n_b - len(pts))
nm = [p for p in pts if not p['ok']]
print('TOTAL points', len(pts), 'mismatch', len(nm))
bysec = {}
for p in pts:
    bysec.setdefault(p['sec'], [0, 0]); bysec[p['sec']][0] += 1
    if not p['ok']: bysec[p['sec']][1] += 1
print('by section', sorted(bysec.items()))
unc = []
for i, (path, s) in enumerate(c.leaves):
    for mt in TOKRE.finditer(s):
        if not any(k in cc.get(i, ()) for k in range(mt.start(), mt.end())):
            unc.append((path, mt.group(0), s[max(0, mt.start() - 16): mt.end() + 10].replace(chr(10), ' ')))
print('uncovered tokens', len(unc))
grp = {}
for path, tok, ctx in unc:
    grp.setdefault(path, []).append(tok + ' {' + ctx + '}')
with open(pre + '_uncovered.txt', 'w', encoding='utf-8') as f:
    for path in grp:
        f.write(path + ' (' + str(len(grp[path])) + ')' + chr(10))
        for x in grp[path]:
            f.write('    ' + x + chr(10))
json.dump({'points': pts, 'diag': diag, 'uncovered': unc}, open(pre + '_all.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('paths with uncovered tokens', len(grp))
