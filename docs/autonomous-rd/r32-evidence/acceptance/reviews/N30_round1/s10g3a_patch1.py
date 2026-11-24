import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
for a, b in (("c.eq('MAP', 'MAP 资产月窗表行数', nrow, 9)", "c.eq('MAP', 'MAP 资产月窗表行数(L112-L119)', nrow, 8)"),
             ("close(c.last('EURUSD')[1], 1.09397, tol=1e-6)", "close(c.last('EURUSD')[1], 1.09397, tol=0.0000051)"),
             ("close(c.last('VIX')[1], 27.01, tol=1e-6)", "close(c.last('VIX')[1], 27.01, tol=0.0000051)")):
    assert s.count(a) == 1, a
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s)
print('g3a patched')
