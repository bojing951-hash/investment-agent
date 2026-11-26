import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
a = "st['ECB_MRO']['coverage_observed']['n_in_window'], 2)"
b = "st['ECB_MRO'].get('coverage_observed', {}).get('n_in_window', st['ECB_MRO'].get('spec', {}).get('window', {}).get('n_in_window')), 2, 'ECB_MRO item keys=' + str(sorted(st['ECB_MRO'].keys())))"
assert s.count(a) == 1
s = s.replace(a, b)
a2 = """keys = set(re.findall("^[ ]+'([A-Za-z0-9_]+)':[ ]*[[]", blk, re.M))"""
b2 = "keys = set(re.findall(\"^[ ]+'([A-Za-z0-9_]+)':[ ]*.\", blk, re.M))"
assert s.count(a2) == 1, 'a2'
s = s.replace(a2, b2)
open(p, 'w', encoding='utf-8').write(s)
print('g2b patched')
