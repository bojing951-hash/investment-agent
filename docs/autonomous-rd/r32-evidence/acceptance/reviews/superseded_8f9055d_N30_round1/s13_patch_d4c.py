import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
old1 = '''b = s.index('),均不改结论;NIT " + ', a)
s = s[:a] + '"(" + "；".join(MINOR_SUM) + "' + s[b:]'''
new1 = '''b = s.index('NIT " + str(N_NIT) + " 条(行文/限定语)。', a)
assert s[b - 14:b] == '),均不改结论;"\\n    "', ascii(s[b - 14:b])
s = s[:a] + '"(" + "；".join(MINOR_SUM) + '),均不改结论;"\\n    "' + s[b:]'''
assert s.count(old1) == 1
s = s.replace(old1, new1)
open(p, "w", encoding="utf-8").write(s)
print("patch script fixed")
