import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
a = "close(round(b - a, 2), float(dl)), round(b - a, 2))"
assert s.count(a) == 1
s = s.replace(a, "close(b - a, float(dl), tol=0.00051), round(b - a, 3))")
open(p, 'w', encoding='utf-8').write(s)
print('g3c patched')
