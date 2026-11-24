# s10g3a_mapface.py <snap> <rep> <cal> <reg> <aj> <out> <map>  -- engine-rendered numbers in MAP_REPORT.md
import sys, re
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from rc_common import *
c = Ctx(*sys.argv[1:7])
mp = open(sys.argv[7], encoding='utf-8').read()
def mt(tok, comp, src, tol=None):
    c.ok('MAP', src + ' | 文内 token ' + tok, (tok in mp) and close(comp, float(tok), tol=tol), (tok, comp))
DS = '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
NUM = '[0-9]+(?:[.][0-9]+)?'
SG = '[+-]' + NUM
ROW = '[|] ([A-Z0-9_]+) [|] (' + DS + ')[.][.](' + DS + ') [|] (' + NUM + ')→(' + NUM + ') [|] (' + SG + ')%[(](' + SG + ')[)]'
nrow = 0
for m in re.finditer(ROW, mp):
    mid, d0, d1, v0, v1, pc, dl = m.groups()
    a = c.obe(mid, d0); b = c.obe(mid, d1)
    mt(v0, a[1], mid + ' 起值@' + d0 + '(实际观测 ' + a[0] + ')')
    mt(v1, b[1], mid + ' 末值@' + d1 + '(实际观测 ' + b[0] + ')')
    mt(pc, pct(a[1], b[1]), mid + ' 变动%', tol=0.0051)
    mt(dl, b[1] - a[1], mid + ' 指数点变动', tol=0.0051)
    nrow += 1
c.eq('MAP', 'MAP 资产月窗表行数(L112-L119)', nrow, 8)
mv = re.search('11-13 (' + NUM + ')→11-16 (' + NUM + ')→11-17 (' + NUM + ')→11-18 (' + NUM + ')→11-19 (' + NUM + ')→11-20 (' + NUM + ')', mp)
if mv:
    for d, v in zip(('13', '16', '17', '18', '19', '20'), mv.groups()):
        mt(v, c.at('VIX', '2026-11-' + d), 'VIX 收盘 2026-11-' + d)
else:
    c.ok('MAP', 'MAP VIX 末六个交易日路径在场', False, 'regex 未命中')
for mid, w1 in (('EURUSD', '降至'), ('USDJPY', '升至'), ('DXY', '升至')):
    mm = re.search(mid + ' 由 (' + NUM + ') ' + w1 + ' (' + NUM + ')[(](' + SG + ')%[)]', mp)
    if not mm:
        c.ok('MAP', mid + ' 汇率月窗行', False, 'regex 未命中')
        continue
    a = c.at(mid, '2026-10-23'); b = c.at(mid, '2026-11-20'); l = c.last(mid)
    mt(mm.group(1), a, mid + ' 10-23 收盘')
    mt(mm.group(2), b, mid + ' 11-20 收盘')
    mt(mm.group(3), pct(a, b), mid + ' 至 11-20 变动%', tol=0.0051)
    hits = list(re.finditer(mid + ' (' + NUM + ')[(](' + SG + ')%[)]', mp))
    ok1 = any(close(float(x.group(1)), l[1], tol=0.000051) for x in hits)
    ok2 = any(close(float(x.group(2)), pct(a, l[1]), tol=0.0051) for x in hits)
    c.ok('MAP', mid + ' 截止日盘中值与对 10-23 变动%(引擎当前面)', ok1 and ok2, (l, round(pct(a, l[1]), 3), [x.group(0) for x in hits][:3]))
for m in re.finditer('近30日(' + NUM + ')→(' + NUM + '),(' + SG + ') 指数点[(](' + SG + ')%[)]', mp):
    v = [float(x) for x in m.groups()]
    res = []
    for mid in ('EURUSD', 'VIX'):
        a = c.at(mid, '2026-10-23'); b = c.last(mid)[1]
        res.append((mid, abs(v[0] - a) < 0.00051 and abs(v[1] - b) < 0.00051 and abs(abs(v[2]) - abs(b - a)) < 0.00051 and abs(abs(v[3]) - abs(pct(a, b))) < 0.0051))
    c.ok('MAP', '引擎当前面「近30日 A→B,Δ 指数点(x%)」可由 10-23 观测→截止日观测复算: ' + m.group(0), any(r[1] for r in res), res)
c.ok('MAP', '「2026-11-23=1.09397」=EURUSD 截止日观测', '2026-11-23=1.09397' in mp and close(c.last('EURUSD')[1], 1.09397, tol=0.0000051), c.last('EURUSD'))
c.ok('MAP', '「2026-11-23=27.01」=VIX 截止日观测', '2026-11-23=27.01' in mp and close(c.last('VIX')[1], 27.01, tol=0.0000051), c.last('VIX'))
c.ok('MAP', '「2026-10-01=4」=EA@2026-10 且「2026-09-01=3.8→2026-10-01=4,Δ+20bp」', '2026-10-01=4' in mp and '2026-09-01=3.8→2026-10-01=4,Δ+20bp' in mp and c.mv('EA_HICP_YOY', '2026-10') == 4.0 and c.mv('EA_HICP_YOY', '2026-09') == 3.8, (c.mv('EA_HICP_YOY', '2026-09'), c.mv('EA_HICP_YOY', '2026-10')))
c.save('g3a')
