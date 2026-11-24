# -*- coding: utf-8 -*-
"""One-off patcher for the seat's own part scripts: make the section decorator return the function
(it already runs the body once at decoration time) and drop the trailing re-invocation lines."""
import re
import sys
out = sys.argv[1]
for n in ("s7_p1", "s7_p3", "s7_p4a", "s7_p4b", "s7_p5", "s7_p6"):
    p = "%s/%s.py" % (out, n)
    src = open(p, encoding="utf-8").read()
    assert src.count("    return d\n") == 1, n
    src = src.replace("    return d\n", "    return lambda f: (d(f), f)[1]\n")
    lines = [l for l in src.split("\n") if not re.match(r"^[a-z][0-9a-z]*\(\)$", l)]
    open(p, "w", encoding="utf-8").write("\n".join(lines))
    print("patched", n, len(src.split("\n")) - len(lines), "lines removed")
