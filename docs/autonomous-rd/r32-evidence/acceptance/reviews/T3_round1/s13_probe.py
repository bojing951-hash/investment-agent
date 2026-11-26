# -*- coding: utf-8 -*-
"""Read-only structure probe (no claims recorded). usage: python3 -I s13_probe.py <run_dir> <install_tree> <out_dir>"""
import ast
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def mod(n):
    s = importlib.util.spec_from_file_location(n, os.path.join(HERE, n + ".py"))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


lib = mod("t3lib")
c = lib.build(sys.argv[1], sys.argv[2], sys.argv[3])
J = lambda x: json.dumps(x, ensure_ascii=False)


def show(tag, v, n=900):
    print("%s: %s" % (tag, J(v)[:n]))


def find(obj, key, path=""):
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key:
                out.append((path + "/" + k, v))
            out += find(v, key, path + "/" + k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out += find(v, key, path + "[%d]" % i)
    return out


rep = c.rep
show("rep.keys", list(rep.keys()))
for k, v in rep["layers"].items():
    show("layer " + k, list(v.keys()) if isinstance(v, dict) else type(v).__name__, 300)
show("rep.agent_judgment.keys", list(rep["agent_judgment"].keys()))
show("cv", c.cv, 2600)
show("J.keys", list(c.J.keys()))
show("J.l3.keys", list(c.J["l3"].keys()))
show("J.l4.keys", list(c.J["l4"].keys()))
show("contradiction keys", list(c.J["l3"]["contradictions"][0].keys()))
show("link keys", [list(x.keys()) for x in c.J["l3"]["mechanism_chains"][0]["links"]])
show("decl", {k: c.J[k] for k in c.J if k not in ("l3", "l4", "reader_map", "quality_gate_notes")}, 2600)
show("evi n", len(c.EVI))
show("evi sample", list(c.EVI.items())[:2], 700)
show("evi metrics", sorted(set(k.split("@")[0] for k in c.EVI)))
show("S6 keys", list(c.S6.keys()))
show("S6.data keys", list(c.S6["data"].keys()))
cd = c.S6["data"].get("candidates")
show("S6.candidates", {k: v for k, v in cd.items() if k != "top"} if isinstance(cd, dict) else cd, 500)
show("S6.top0", (cd.get("top") or [None])[0] if isinstance(cd, dict) else None, 700)
for p, v in find(c.plan, "policy_window_path"):
    show("pwp " + p, v, 2200)
show("plan keys", {k: (type(v).__name__, len(J(v))) for k, v in c.plan.items()}, 900)
show("run keys", list(rep.get("run", {}).keys()))
show("run.frozen_inputs", rep.get("run", {}).get("frozen_inputs"), 1200)
show("run.data_requirements", rep.get("run", {}).get("data_requirements"), 1800)
show("STALE in jdump", "STALE" in c.jdump)
show("gap words in jdump", [k for k in ("缺口 6", "任务目标", "无法解析", "多范围", "降级面", "degraded", "noncore_missing") if k in c.jdump])
show("观测日全为周三 in MAP", "观测日全为周三" in c.docs["MAP_REPORT.md"])
for m in ("ECB_MRO", "ECB_DFR"):
    nw = [d for d, _ in lib.series(m) if lib.wd(d) != "Wed"]
    show("nonwed " + m, [len(lib.series(m)), len(nw), nw[:12], lib.series(m)[0]])
for m in ("SPX", "VIX", "DAX", "CAC40", "NIKKEI225", "DFEDTARL", "DFEDTARU", "UST_10Y"):
    show("last " + m, lib.at(m, c.cutoff))
show("policy_doc_facts", c.plan.get("policy_doc_facts"), 900)
show("snap research_as_of/target_date", [c.snap.get("research_as_of"), c.snap.get("target_date")])
show("tz", [lib.tz_hm(c.snap["research_as_of"], z) for z in ("America/New_York", "Europe/Berlin", "Asia/Tokyo", "Asia/Shanghai")])
rj = open(os.path.join(c.run_dir, "report.json"), encoding="utf-8").read()
show("stamp in report.json", [x for x in ("36499bb78a18dea1ff2b027074088b0ba404c3b8", "36499bb7") if x in rj])
for f in ("agent_judgment.json", "report.json", "MAP_REPORT.md"):
    show("sha " + f, lib.sha(os.path.join(c.run_dir, f)))
for rel in ("config/release_calendar.json", "config/metric_registry.json", "data/daily/research_snapshot_20261123.json"):
    show("sha overlay/tree " + rel, [lib.sha(os.path.join(c.run_dir, "root_overlay", rel))[:16], lib.sha(os.path.join(c.tree, rel))[:16]])
try:
    src = open(os.path.join(c.tree, "scripts", "research_contract", "text_consistency.py"), encoding="utf-8").read()
    al = None
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "ALIASES" for t in node.targets):
            al = ast.literal_eval(node.value)
    show("ALIASES type/len", [type(al).__name__, len(al) if al else None])
    show("ALIASES has", {k: (k in al) for k in ("JP_CPI_YOY", "EA_HICP_YOY", "JP_CPI_TOKYO_YOY", "JP_POLICY_TARGET", "ECB_MRO", "USDJPY", "SPX", "VIX", "ECB_DFR", "JP_POLICY_RATE")})
    show("ALIASES CPI", al.get("CPI") if isinstance(al, dict) else None)
    jc = open(os.path.join(c.tree, "scripts", "research_contract", "judgment_contract.py"), encoding="utf-8").read().split("\n")
    hit = [i + 1 for i, l in enumerate(jc) if "'12个月前'" in l and "'最新一期'" in l]
    show("contract line hits", hit)
    for i in hit:
        show("line %d" % i, jc[i - 1].strip()[:300])
        show("line %d" % (i - 1), jc[i - 2].strip()[:300])
except Exception as e:
    show("code probe error", repr(e))
