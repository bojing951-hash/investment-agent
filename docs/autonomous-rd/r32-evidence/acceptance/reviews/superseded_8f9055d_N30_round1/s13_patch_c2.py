import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
R = [
    ('C2 称存款便利利率升至最新水平 2.5%,该处', 'C2 称存款便利利率升至最新水平 2.5%%,该处'),
    ('另 S1 触发阈(≥4.0%%)高于其前提水平(3.5%% 以上),3.5%%–4.0%% 区间', '另 S1 触发阈(≥4.0%)高于其前提水平(3.5% 以上),3.5%–4.0% 区间'),
]
for a, b in R:
    assert s.count(a) == 1, (s.count(a), a[:40])
    s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("patched", len(R))
