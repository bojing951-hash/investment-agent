import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
a = '                    json.dumps(DIAG, ensure_ascii=False, default=str)])'
assert s.count(a) == 1
s = s.replace(a, '                    " ".join(str(i) for i in range(1, len(I["rows"]) + 1)), json.dumps(DIAG, ensure_ascii=False, default=str)])')
open(p, "w", encoding="utf-8").write(s)
print("patched")
