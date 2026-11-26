# -*- coding: utf-8 -*-
#!/usr/bin/python3 -I
# s17e: 逐点表「出处」列的最后一处修饰(去重 file·face 同名; 日历算术/算术两类标为直算)。
# 用法: /usr/bin/python3 -I s17e_patch.py S17A
import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
old = '    return f + " · " + fc\n'
new = ('    if f == fc:\n'
       '        return fc\n'
       '    return {"datetime": "直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of)",\n'
       '            "算术": "直算(算术; 输入=已比对的两端值)"}.get(fc, f + " · " + fc)\n')
assert s.count(old) == 1, s.count(old)
open(p, "w", encoding="utf-8").write(s.replace(old, new))
print("patched OK")
