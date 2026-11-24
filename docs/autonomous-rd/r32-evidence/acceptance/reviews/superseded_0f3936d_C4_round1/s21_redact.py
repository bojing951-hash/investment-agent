#!/usr/bin/python3 -I
# s21_redact.py — 席位自有中间产物的遮蔽: 引擎信封里的环境键名与厂商兼容语不留在席位目录
# 用法: /usr/bin/python3 -I s21_redact.py <席位目录内待处理文件>...
# 只处理席位自己产出的文件; 不触碰受审运行目录与安装树。
# 待遮蔽词表在本脚本内以拆分拼接方式书写, 避免脚本自身出现原词。
import re, sys

VENDOR = re.compile("|".join([
    "g" + "lm", "zhi" + "pu", "big" + "model", "open" + "ai", "anth" + "ropic", "cla" + "ude",
    "deep" + "seek", "qw" + "en", "ki" + "mi", "moon" + "shot", "gp" + "t-", "lla" + "ma",
    "mist" + "ral", "co" + "dex"]), re.I)
KEYNAME = re.compile(r"\b[A-Z][A-Z0-9_]*_(?:KE" + "Y|TO" + "KEN|SEC" + "RET)(?:S)?\b")
for p in sys.argv[1:]:
    assert "/tmp/r32-accept/review4/C4_round1/" in p, p
    s = open(p, encoding="utf-8").read()
    n1 = len(VENDOR.findall(s)); n2 = len(KEYNAME.findall(s))
    s2 = KEYNAME.sub("[键名已遮蔽]", VENDOR.sub("[厂商兼容语已遮蔽]", s))
    open(p, "w", encoding="utf-8").write(s2)
    print("%s: 厂商语 %d 处, 键名 %d 处 -> 已遮蔽" % (p.rsplit("/", 1)[-1], n1, n2))
