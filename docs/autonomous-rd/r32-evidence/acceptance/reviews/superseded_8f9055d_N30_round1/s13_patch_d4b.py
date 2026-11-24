import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
a = '''s = s[:a] + '"(" + "；".join(MINOR_SUM) + s[b:]'''
b = '''s = s[:a] + '"(" + "；".join(MINOR_SUM) + "' + s[b:]'''
assert s.count(a) == 1
s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("patch script fixed")
