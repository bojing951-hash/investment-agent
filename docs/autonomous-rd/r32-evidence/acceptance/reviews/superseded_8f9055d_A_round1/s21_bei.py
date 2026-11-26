#!/usr/bin/python3 -I
"""Full-precision BEI_10Y check for the '35bp' sentence. usage: s21_bei.py <snapshot.json>"""
import sys
sys.path.insert(0, "/tmp/r32-accept/review5/A_round1")
import json
import lib
snap = lib.load_json(sys.argv[1])
st = lib.Store(snap)
a = st.at("BEI_10Y", "2020-11-30")
b = st.at("BEI_10Y", "2026-11-20")
print("raw BEI_10Y 2020-11-30 = %r ; 2026-11-20 = %r" % (a, b))
print("difference bp (raw) = %.4f ; from rounded = %.1f" % ((b - a) * 100, (2.15 - 1.77) * 100))
print("distance of latest to threshold 1.8 bp = %.4f" % ((b - 1.8) * 100))
# last obs strictly below 1.8 before the cutoff
below = [(d, v) for d, v in st.in_range("BEI_10Y", "2016-01-01", "2026-11-23") if v < 1.8]
print("n obs < 1.8 in store:", len(below), "last:", below[-1] if below else None, "first:", below[0] if below else None)
print("BEI_10Y first obs:", st.first_date("BEI_10Y"))
# any reading 2.12 (which would make 35bp true)?
c = [(d, v) for d, v in st.in_range("BEI_10Y", "2026-01-01", "2026-11-23") if abs(v - 2.12) < 0.005]
print("obs within 0.005 of 2.12 in 2026:", c[-3:], "n=", len(c))
print("last 6 obs:", st.series("BEI_10Y")[-6:])
