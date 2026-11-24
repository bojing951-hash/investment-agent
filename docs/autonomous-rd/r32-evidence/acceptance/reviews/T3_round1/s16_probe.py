# -*- coding: utf-8 -*-
"""Read-only probe 2: run status / validation / gap wording in rendered docs / contract history range."""
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
s = importlib.util.spec_from_file_location("t3lib", os.path.join(HERE, "t3lib.py"))
lib = importlib.util.module_from_spec(s)
s.loader.exec_module(lib)
c = lib.build(sys.argv[1], sys.argv[2], sys.argv[3])
J = lambda x, n=700: json.dumps(x, ensure_ascii=False)[:n]
rep = c.rep
print("run_ok:", rep.get("run_ok"), "| allow_failed_run:", rep["agent_judgment"].get("allow_failed_run"), "| attached:", rep["agent_judgment"].get("attached"), rep["agent_judgment"].get("attached_at"))
print("validation:", J(rep["agent_judgment"].get("validation"), 1500))
print("reader_map_faces:", J(rep["agent_judgment"].get("reader_map_faces"), 600))
print("notes:", J(rep.get("notes"), 900))
d = c.docs["report.md"]
for key in ("数据需求", "任务目标缺口", "地图计划指标缺数", "降级面", "blocked"):
    for m in list(re.finditer(key, d))[:2]:
        print("report.md[%s]: %s" % (key, d[max(0, m.start() - 60):m.start() + 260].replace("\n", "\\n")))
m = c.docs["MAP_REPORT.md"]
for key in ("数据不可得", "缺口", "语义审查", "degraded"):
    ms = list(re.finditer(key, m))
    print("MAP count[%s]=%d first: %s" % (key, len(ms), m[max(0, ms[0].start() - 80):ms[0].start() + 160].replace("\n", "\\n") if ms else None))
src = open(os.path.join(c.tree, "scripts", "research_contract", "judgment_contract.py"), encoding="utf-8").read()
for mm in list(re.finditer("history_periods", src))[:12]:
    a = src.rfind("\n", 0, mm.start())
    b = src.find("\n", mm.end())
    print("contract:", src[a + 1:b].strip()[:200])
for key in ("face_off_verdict", "尚不能区分"):
    for mm in list(re.finditer(key, src))[:4]:
        a = src.rfind("\n", 0, mm.start())
        b = src.find("\n", mm.end())
        print("contract[%s]:" % key, src[a + 1:b].strip()[:200])
tab = json.load(open(os.path.join(c.out_dir, "recompute_table.json"), encoding="utf-8"))
for x in tab["rows"]:
    if x["where"] in ("M1.step4",) and x["needle"] and "不超过 0.23%" in x["needle"]:
        print("fx row:", J(x["computed"]), x["note"])
    if x["needle"] and "净 +75bp=六个变动点之和" in x["needle"]:
        print("75bp row:", J(x["computed"]), x["note"])
cats = {}
for x in tab["rows"]:
    cats[x["cat"]] = cats.get(x["cat"], 0) + 1
print("cats:", J(cats))
