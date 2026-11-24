# -*- coding: utf-8 -*-
"""Read-only probe 3: calendar provenance fields, contract six_checks statuses, history range in contract."""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
s = importlib.util.spec_from_file_location("t3lib", os.path.join(HERE, "t3lib.py"))
lib = importlib.util.module_from_spec(s)
s.loader.exec_module(lib)
c = lib.build(sys.argv[1], sys.argv[2], sys.argv[3])
J = lambda x, n=700: json.dumps(x, ensure_ascii=False)[:n]
print("cal top keys:", list(c.cal.keys()))
for x in c.CENT:
    print(" ", x["entry_id"], "| basis=%s official=%s kind=%s | source=%s" % (x.get("basis"), x.get("official"), x.get("kind"), str(x.get("source"))[:60]))
sc = c.cv.get("six_checks") or []
print("six_checks:", J([[z["item"], z["check"], z["status"]] for z in sc], 900))
src = open(os.path.join(c.tree, "scripts", "research_contract", "judgment_contract.py"), encoding="utf-8").read().split("\n")
for i, l in enumerate(src):
    if "hist = rm.get('history_periods') or []" in l:
        print("\n".join("%d: %s" % (j + 1, src[j].rstrip()[:170]) for j in range(i, min(i + 9, len(src)))))
print("schema:", c.J.get("schema_version"), "| envelope keys:", J(list(c.env.keys()), 300))
print("gate_a keys:", J(list(c.ga.keys()), 400))
print("quality:", J(c.snap.get("quality"), 500))
