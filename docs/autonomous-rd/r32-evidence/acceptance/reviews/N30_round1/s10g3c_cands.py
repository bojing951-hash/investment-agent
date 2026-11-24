# s10g3c_cands.py <snap> <rep> <cal> <reg> <aj> <out> <map>  -- MAP turning-candidate table (engine face) + policy cluster rows
import sys, re
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from rc_common import *
c = Ctx(*sys.argv[1:7])
mp = open(sys.argv[7], encoding='utf-8').read()
DS = '[0-9][0-9][0-9][0-9]-[0-9][0-9]'
NUM = '[0-9]+(?:[.][0-9]+)?'
rows = []
for m in re.finditer('[|] (JP|EA) [|] [a-z_]+ [|] ([A-Z0-9_]+) [|] (' + DS + ')[.][.](' + DS + ') [|] (' + NUM + ')→(' + NUM + ') [|] ([+-]?' + NUM + ') [|]', mp):
    reg, mid, d0, d1, v0, v1, dl = m.groups()
    a = c.mv(mid, d0); b = c.mv(mid, d1)
    c.ok('MAP', mid + ' 候选 ' + d0 + '..' + d1 + ' 起→末(' + v0 + '→' + v1 + ')', close(a, float(v0)) and close(b, float(v1)), (a, b))
    c.ok('MAP', mid + ' 候选变动 ' + dl, close(b - a, float(dl), tol=0.00051), round(b - a, 3))
    rows.append((mid, abs(float(dl))))
c.eq('MAP', 'MAP 候选表行数', len(rows), 4)
top = max(rows, key=lambda x: x[1]) if rows else None
c.ok('G', '「引擎候选面另列日本全国 CPI 2025-11→2026-02…为幅度最大候选」=候选表 |变动| 最大行', top is not None and top[0] == 'JP_CPI_YOY' and close(top[1], 1.63), top)
for m in re.finditer('[|] POLCLUSTER-[0-9]+ [|] (' + DS + '-' + DS + ')[.][.](' + DS + '-' + DS + ') [|] EA [|] 欧央行存款便利利率 (' + DS + '-' + DS + ')→(' + DS + '-' + DS + ')[(]([+]25bp)[)]', mp):
    c.ok('MAP', '政策聚簇行 ' + m.group(0)[:60], m.group(3) in [x[0] for x in c.changes('ECB_DFR') if '2026-05-23' <= x[0] <= c.asof] and close((c.at('ECB_DFR', m.group(3)) - c.at('ECB_DFR', m.group(2))) * 100, 25), m.groups())
c.save('g3c')
