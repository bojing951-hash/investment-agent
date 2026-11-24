import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
a = "nm = [p for p in pts if not p['ok']]\nprint('TOTAL points'"
assert s.count(a) == 1, 'merge'
s = s.replace(a, "n_b = len(pts)\npts = [p for p in pts if '证据索引各行 value 与 series_store 同日值一致' not in p['src']]\nprint('excluded hollow points', n_b - len(pts))\n" + a)
open(p, 'w', encoding='utf-8').write(s)
p = sys.argv[2]
s = open(p, encoding='utf-8').read()
a = "for tg in ['a', 'b', 'c', 'd']:"
assert s.count(a) == 1, 's21'
s = s.replace(a, "for tg in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'g2a', 'g2b', 'g3a']:")
open(p, 'w', encoding='utf-8').write(s)
print('patched s20/s21')
