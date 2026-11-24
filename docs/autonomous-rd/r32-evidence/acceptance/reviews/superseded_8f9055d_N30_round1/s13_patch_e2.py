import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
a = '("CAT", dict(CAT), dict(OTH))'
assert s.count(a) == 1
s = s.replace(a, '("CAT", (dict(CAT), dict(OTH)))')
open(p, "w", encoding="utf-8").write(s)
p = sys.argv[2]
s = open(p, encoding="utf-8").read()
a = '    return round(dct["%04d-%02d-01" % (y, m_)], 2)'
assert s.count(a) == 1
s = s.replace(a, '    return round(dct["%04d-%02d-01" % (y, m_)], 6)')
open(p, "w", encoding="utf-8").write(s)
print("patched")
