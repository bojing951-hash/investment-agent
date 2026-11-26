# s10g1_patch1.py <script>: peak = max among readings visible before the 2nd decision date
import sys
p = sys.argv[1]
L = open(p, encoding='utf-8').read().split(chr(10))
new = [
"visp = [x[:7] for x in c.S[EA]['dates'] if x >= '2025-11-01' and c.pub(EA, x[:7]) <= dec2]",
"pk = max(visp, key=lambda y: c.mv(EA, y))",
"tk('决议日前可见读数 2.9 低于 2026-05 峰值 3.2', '3.2', 3.2, c.mv(EA, '2026-05') if pk == '2026-05' else -1, '第二次回推决议日(' + dec2 + ')前可见读数(近十二期)峰值=2026-05')",
]
hit = [i for i, l in enumerate(L) if 'EA 2026-01..2026-09 峰值=2026-05' in l]
assert len(hit) == 1, hit
L[hit[0]:hit[0] + 1] = new
open(p, 'w', encoding='utf-8').write(chr(10).join(L))
print('g1 patched')
