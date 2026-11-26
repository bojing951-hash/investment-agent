#!/usr/bin/python3 -I
"""Effect of the engine LPR publication-rule quirk on the 2022-06 sync face. usage: s34_lpr.py <snapshot.json>"""
import sys
sys.path.insert(0, "/tmp/r32-accept/review5/A_round1")
import lib
st = lib.Store(lib.load_json(sys.argv[1]))
print("CN_LPR_1Y obs 2022-03..2022-07:", st.in_range("CN_LPR_1Y", "2022-03-01", "2022-07-31"))
print("2022-06-20 weekday (0=Mon):", __import__("datetime").date(2022, 6, 20).weekday(), "; 2022-06-19:", __import__("datetime").date(2022, 6, 19).weekday())
