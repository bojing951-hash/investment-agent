#!/usr/bin/python3 -I
import json, sys
rows = json.load(open(sys.argv[1], "r", encoding="utf-8"))["rows"]
for r in rows:
    if not r["id"].endswith("X"):
        print(r["id"], r["ok"], r["src"], "|", r["computed"], "|", r["reported"], "| lit_found", r["lit_found"], "|", r["note"][:150])
