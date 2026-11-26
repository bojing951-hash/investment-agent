#!/usr/bin/env python3
"""Probe S6_analog / S4 / S3 envelope structure in report.json (read-only).

usage: python3 -I probe4.py <report.json> <out.txt>
"""
import json
import sys

rep_path, out_path = sys.argv[1:3]
rep = json.load(open(rep_path, "r", encoding="utf-8"))
out = open(out_path, "w", encoding="utf-8")


def w(s=""):
    out.write(s + "\n")


def short(obj, n=1500):
    return json.dumps(obj, ensure_ascii=False)[:n]


def walk(obj, depth=0, max_depth=3, key="root"):
    pad = "  " * depth
    if isinstance(obj, dict):
        w(f"{pad}{key}: dict({len(obj)}) keys={list(obj.keys())[:30]}")
        if depth < max_depth:
            for k, v in list(obj.items())[:30]:
                if isinstance(v, (dict, list)):
                    walk(v, depth + 1, max_depth, k)
                else:
                    w(f"{pad}  {k}: {repr(v)[:160]}")
    elif isinstance(obj, list):
        w(f"{pad}{key}: list({len(obj)})")
        if obj and depth < max_depth:
            walk(obj[0], depth + 1, max_depth, key + "[0]")


steps = {s["step"]: s for s in rep["steps"]}
for name in ["S2_doctor", "S3_overview_US", "S3_changes", "S4_history_CPI", "S4_history_JP_POLICY_RATE",
             "S5_compare", "S6_analog", "S8_grounded_qa", "S9_views_lint"]:
    st = steps.get(name)
    w("=" * 20 + f" {name} " + "=" * 20)
    if not st:
        w("missing")
        continue
    w(f"argv={short(st.get('argv'), 600)}")
    w(f"exit_code={st.get('exit_code')} semantic_ok={st.get('semantic_ok')} note={short(st.get('note'), 500)}")
    env = st.get("envelope")
    if isinstance(env, dict):
        w(f"gate_a={short(env.get('gate_a'), 1500)}")
        w(f"warnings={short(env.get('warnings'), 1500)}")
        data = env.get("data")
        walk(data, 1, 2, "data")

cv = rep["agent_judgment"]["contract_verification"]
w("=" * 20 + " contract_verification " + "=" * 20)
w(f"keys={list(cv.keys())}")
for k, v in cv.items():
    if k != "verdicts":
        w(f"{k}: {short(v, 800)}")
w(f"n verdicts={len(cv['verdicts'])}")
from collections import Counter
w(str(Counter((v.get('status'), v.get('family')) for v in cv['verdicts']).most_common()))
for v in cv["verdicts"]:
    w(short(v, 400))
out.close()
print("written", out_path)
