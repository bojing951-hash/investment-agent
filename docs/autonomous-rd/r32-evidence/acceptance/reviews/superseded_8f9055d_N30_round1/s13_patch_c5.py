import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
a = "EA_MAY_PUB, JP_MAY_PUB = (_me(2026, 5) + dt.timedelta(days=k)).isoformat() for k in (16, 20)"
b = "EA_MAY_PUB, JP_MAY_PUB = [(_me(2026, 5) + dt.timedelta(days=k)).isoformat() for k in (16, 20)]"
assert s.count(a) == 1
s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("fixed")
