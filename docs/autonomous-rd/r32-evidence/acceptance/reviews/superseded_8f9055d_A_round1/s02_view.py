#!/usr/bin/python3 -I
"""Print series around key dates. usage: s02_view.py <snapshot> <metric> <from_ym> <to_ym> [step]"""
import sys
sys.path.insert(0, "/tmp/r32-accept/review5/A_round1")
import lib  # seat-owned

snap = lib.load_json(sys.argv[1])
st = lib.Store(snap)
mid = sys.argv[2]
d0 = sys.argv[3]
d1 = sys.argv[4]
step = int(sys.argv[5]) if len(sys.argv) > 5 else 1
s = st.series(mid)
print("%s n=%d first=%s last=%s" % (mid, len(s), s[0][0], s[-1][0]))
a = d0 + "-01" if len(d0) == 7 else d0
b = d1 + "-31" if len(d1) == 7 else d1
sel = [(d, v) for d, v in s if a <= d[:len(a)] and d <= b + "-31" if len(d1) == 7] if False else [(d, v) for d, v in s if d[:7] >= d0 and d[:7] <= d1]
for i, (d, v) in enumerate(sel):
    if i % step == 0:
        print("  %s  %s" % (d, v))
