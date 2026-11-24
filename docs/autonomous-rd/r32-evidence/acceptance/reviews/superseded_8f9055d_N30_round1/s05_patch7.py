#!/usr/bin/python3 -I
# -*- coding: utf-8 -*-
"""patch7: Tokyo month-value presence test must only use formats that round-trip
(1.85 printed as '1.9' must not be matched against an unrelated '1.9')."""
import sys
p = sys.argv[1]
src = open(p, encoding="utf-8").read()
old = '                    inT_ = [bool(re.search(r"(?<![\\d.])" + re.escape(("%." + str(k_) + "f") % f(ym)) + r"(?!\\d)", T)) for k_ in (1, 2, 3)]\n'
new = '                    inT_ = [bool(re.search(r"(?<![\\d.])" + re.escape(x_) + r"(?!\\d)", T)) for k_ in (1, 2, 3) for x_ in [("%." + str(k_) + "f") % f(ym)] if float(x_) == float(f(ym))]\n'
assert src.count(old) == 1, src.count(old)
open(p, "w", encoding="utf-8").write(src.replace(old, new))
print("patch7 applied")
