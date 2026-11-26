# -*- coding: utf-8 -*-
#!/usr/bin/python3 -I
# s17f: 出处列「datetime/算术」两类改为直算标注(适用于全部行)。用法: /usr/bin/python3 -I s17f_patch.py S17A
import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
old = '        return fc\n    if f == fc:\n'
new = ('        return {"datetime": "直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of)",\n'
       '                "算术": "直算(算术; 输入=已比对的两端值)"}.get(fc, fc)\n'
       '    if f == fc:\n')
assert s.count(old) == 1, s.count(old)
open(p, "w", encoding="utf-8").write(s.replace(old, new))
print("patched OK")
