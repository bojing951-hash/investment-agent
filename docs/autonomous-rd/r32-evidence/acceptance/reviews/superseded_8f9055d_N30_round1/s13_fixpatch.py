import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
i = s.index("a = s.index('\"(ECB")
tail_new = (
    "a = s.index('\"(ECB 序列最新水平一句未带降级限定;')\n"
    "b = s.index('NIT \" + str(N_NIT) + \" 条(行文/限定语)。', a)\n"
    "assert s[b - 15:b] == '),均不改结论;\"\\n    \"', ascii(s[b - 15:b])\n"
    "s = s[:a] + '\"(\" + \"；\".join(MINOR_SUM) + \"),均不改结论;\"\\n    \"' + s[b:]\n"
    "c = s.index('str(N_NIT) + \" 条(行文/限定语)。')\n"
    "k = len('str(N_NIT) + \" 条(行文/限定语)。')\n"
    "s = s[:c] + 'str(N_NIT) + \" 条(\" + \"；\".join(NIT_SUM) + \")。' + s[c + k:]\n"
    "open(p, \"w\", encoding=\"utf-8\").write(s)\n"
    "print(\"part D patched; sg(chg( replaced:\", n_sg)\n"
)
s = s[:i] + tail_new
open(p, "w", encoding="utf-8").write(s)
import ast
ast.parse(s)
print("patch script syntax ok")
