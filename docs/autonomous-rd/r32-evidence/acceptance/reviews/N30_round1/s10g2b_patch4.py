import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
a = "    p = sys.argv[8] if len(sys.argv) > 8 else ''"
assert s.count(a) == 1, 'find'
s = s.replace(a, "    p = name")
a2 = "c.diag.append('src: ' + pjc + ' | ' + ptc)"
assert s.count(a2) == 1, 'diag'
s = s.replace(a2, a2 + chr(10) + "for nm, sr in (('jc', jc), ('tc', tcs)):" + chr(10) + "    for i, l in enumerate(sr.split(chr(10))):" + chr(10) + "        if '_lbl in' in l or '(13)' in l or 'ALIASES' in l[:40]:" + chr(10) + "            c.diag.append(nm + ' L' + str(i + 1) + ': ' + l.strip()[:200])")
open(p, 'w', encoding='utf-8').write(s)
print('g2b patched4')
