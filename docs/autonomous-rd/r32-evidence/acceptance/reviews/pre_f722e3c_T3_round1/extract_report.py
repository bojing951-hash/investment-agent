#!/usr/bin/env python3
"""Seat-owned read-only report.json extractor.
Usage: python3 -I extract_report.py <report.json> <mode> [args]
 modes: keys, run, plan_keys, plan <key>, cv_keys, cv, steps, envelope <step_name_substr>, l1, top <key>
"""
import json
import sys


def main(argv):
    path = argv[0]
    mode = argv[1]
    with open(path, "r", encoding="utf-8") as fh:
        rep = json.load(fh)
    out = sys.stdout
    if mode == "keys":
        out.write(repr(list(rep.keys())) + "\n")
        return
    if mode == "run":
        out.write(json.dumps(rep.get("run"), ensure_ascii=False, indent=1)[:6000] + "\n")
        return
    if mode == "plan_keys":
        rp = rep.get("research_plan") or {}
        for k, v in rp.items():
            t = type(v).__name__
            n = len(v) if isinstance(v, (list, dict, str)) else ""
            out.write(f"{k}: {t}[{n}]\n")
        return
    if mode == "plan":
        rp = rep.get("research_plan") or {}
        for k in argv[2:]:
            out.write(f"## research_plan.{k}\n")
            out.write(json.dumps(rp.get(k), ensure_ascii=False, indent=1) + "\n")
        return
    if mode == "l1":
        rows = ((rep.get("layers") or {}).get("L1_事实层") or {}).get("rows") or []
        out.write(json.dumps(rows, ensure_ascii=False, indent=1) + "\n")
        return
    if mode == "top":
        for k in argv[2:]:
            out.write(f"## top.{k}\n")
            out.write(json.dumps(rep.get(k), ensure_ascii=False, indent=1)[:20000] + "\n")
        return
    if mode == "cv_keys":
        cv = ((rep.get("agent_judgment") or {}).get("contract_verification")) or {}
        for k, v in cv.items():
            out.write(f"{k}: {type(v).__name__}[{len(v) if isinstance(v,(list,dict,str)) else ''}]\n")
        return
    if mode == "cv":
        cv = ((rep.get("agent_judgment") or {}).get("contract_verification")) or {}
        out.write(json.dumps(cv, ensure_ascii=False, indent=1)[:30000] + "\n")
        return
    if mode == "steps":
        for i, st in enumerate(rep.get("steps") or []):
            env = st.get("envelope") if isinstance(st, dict) else None
            name = st.get("name") or st.get("step") or st.get("id") if isinstance(st, dict) else None
            keys = list(st.keys()) if isinstance(st, dict) else None
            envkeys = list(env.keys()) if isinstance(env, dict) else None
            out.write(f"[{i}] name={name} keys={keys} envkeys={envkeys}\n")
        return
    if mode == "envelope":
        sub = argv[2]
        for i, st in enumerate(rep.get("steps") or []):
            name = str(st.get("name") or st.get("step") or st.get("id"))
            if sub in name:
                out.write(f"===== [{i}] {name} =====\n")
                out.write(json.dumps(st.get("envelope"), ensure_ascii=False, indent=1)[:12000] + "\n")
        return
    out.write("unknown mode\n")


if __name__ == "__main__":
    main(sys.argv[1:])
