#!/usr/bin/python3 -I
"""Read-only probe #7: raw precision of window-start/end values behind headline percentages.
Args: <snapshot.json>
"""
import json
import sys

snap = json.load(open(sys.argv[1], "r", encoding="utf-8"))
ss = snap["series_store"]


def v(mid, day):
    s = ss[mid]
    if day in s["dates"]:
        return repr(s["values"][s["dates"].index(day)])
    return None


def chg(mid, a, b):
    x, y = v(mid, a), v(mid, b)
    if x is None or y is None:
        return None
    return (float(y) / float(x) - 1.0) * 100.0


for mid in ("VIX", "SPX", "NIKKEI225", "DAX", "CAC40", "EURUSD", "USDJPY", "DXY", "GOLD_F", "SHCOMP"):
    print(mid, "10-23", v(mid, "2026-10-23"), "11-20", v(mid, "2026-11-20"), "11-23", v(mid, "2026-11-23"),
          "| chg%", None if chg(mid, "2026-10-23", "2026-11-20") is None else round(chg(mid, "2026-10-23", "2026-11-20"), 4),
          None if chg(mid, "2026-10-23", "2026-11-23") is None else round(chg(mid, "2026-10-23", "2026-11-23"), 4))
print("VIX 11-04", v("VIX", "2026-11-04"), "11-05", v("VIX", "2026-11-05"), "11-11", v("VIX", "2026-11-11"), "11-13", v("VIX", "2026-11-13"))
s = ss["VIX"]
print("VIX raw types sample", s["values"][-8:])
print("VIX keys", list(s.keys()))
