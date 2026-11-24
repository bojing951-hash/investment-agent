import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
a = "pjc = find(sys.argv[8]); ptc = find(sys.argv[7] if False else 'text_consistency.py')"
b = "pjc = find(sys.argv[7]); ptc = find(sys.argv[8])"
assert s.count(a) == 1
s = s.replace(a, b)
a = "        if os.path.exists(p):\n            return p\n    for root, ds, fs in os.walk(sys.argv[9]):"
assert s.count(a) == 1, 'a2'
s = s.replace(a, "        if os.path.exists(p):\n            return p\n    for root, ds, fs in os.walk(sys.argv[9]):")
# evidence refs: broaden to every leaf path, then report both counts
a3 = "    if 'evid' in p.lower():\n        for m in pat.finditer(s):\n            refs.add(m.group(0))"
assert s.count(a3) == 1, 'a3'
s = s.replace(a3, "    for m in pat.finditer(s):\n        refs.add(m.group(0))\n        if 'evid' not in p.lower():\n            c.diag.append('non-evidence-path ref ' + p + ' = ' + m.group(0))")
open(p, 'w', encoding='utf-8').write(s)
print('g2b patched2')
