import sys, re
path = sys.argv[1]
src = open(path, encoding="utf-8").read()
# replace the single line starting with 'mm = gfl(r"日本' up to end of line
m = re.search(r'    mm = gfl\(r"日本 .*?\)\n', src)
assert m, "mm line not found"
print("OLD:", m.group(0).strip())
new = (r'''    mm = (lambda m_: [float(x) for x in m_.groups()] if m_ else None)(
        re.search(r"\| 日本 \| 1\.25 \| — \| 2026-09-18 \| 2026-09-24 \| 2026-10-30 \| 2026-10-30 \| (\d+)天 \| (\d+)天 \| (\d+)天 ", MAPTXT))
''')
src = src[:m.start()] + new + src[m.end():]
open(path, "w", encoding="utf-8").write(src)
print("ok")
