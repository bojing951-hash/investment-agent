import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
a = "hk = [k for k in c.aj['l4'] if ('hist' in k or 'analog' in k) and isinstance(c.aj['l4'][k], list)]"
b = "hk = ['history_periods']"
assert s.count(a) == 1
s = s.replace(a, b).replace("len(c.aj['l4'][hk[0]]) if hk else -1", "len(c.aj['reader_map'][hk[0]]) if hk else -1")
open(p, 'w', encoding='utf-8').write(s)
print('g2a patched2')
