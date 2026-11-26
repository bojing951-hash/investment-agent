#!/usr/bin/python3
"""Dump contract verification + steps index + notes + L1 rows from report.json (read-only).
Usage: python3 -I s04_report_faces.py <report.json> <out.txt>
"""
import json
import sys


def main():
    rp_path, out_path = sys.argv[1], sys.argv[2]
    with open(rp_path, "r", encoding="utf-8") as fh:
        rep = json.load(fh)
    out = []
    aj = rep.get("agent_judgment", {})
    out.append("=== agent_judgment (minus content) ")
    for k, v in aj.items():
        if k in ("contract_verification",):
            continue
        s = json.dumps(v, ensure_ascii=False)
        out.append("%s = %s" % (k, s[:3000]))
    cv = aj.get("contract_verification", {})
    out.append("=== contract_verification keys: %s" % list(cv.keys()))
    out.append("version=%s verdict=%s" % (cv.get("version"), cv.get("verdict")))
    out.append("stats=" + json.dumps(cv.get("stats"), ensure_ascii=False))
    out.append("unresolved_unbound=" + json.dumps(cv.get("unresolved_unbound"), ensure_ascii=False)[:3000])
    out.append("six_checks=" + json.dumps(cv.get("six_checks"), ensure_ascii=False, indent=1)[:12000])
    mv = cv.get("map_checks")
    out.append("map_checks=" + json.dumps(mv, ensure_ascii=False, indent=1)[:12000])
    verd = cv.get("verdicts")
    out.append("=== verdicts type=%s len=%s" % (type(verd).__name__, len(verd) if hasattr(verd, "__len__") else "-"))
    items = verd.items() if isinstance(verd, dict) else enumerate(verd or [])
    for k, v in items:
        s = json.dumps(v, ensure_ascii=False)
        out.append("V %s = %s" % (k, s[:1500]))
    out.append("=== notes")
    for n in rep.get("notes", []):
        out.append(str(n))
    out.append("=== steps")
    for i, st in enumerate(rep.get("steps", [])):
        keys = list(st.keys())
        env = st.get("envelope")
        env_keys = list(env.keys()) if isinstance(env, dict) else type(env).__name__
        out.append("step[%d] %s | keys=%s | envelope_keys=%s" % (i, st.get("step"), keys, env_keys))
    out.append("=== L1 rows")
    for row in rep["layers"]["L1_事实层"]["rows"]:
        out.append(json.dumps(row, ensure_ascii=False))
    out.append("L1 note=" + str(rep["layers"]["L1_事实层"].get("note")))
    out.append("=== semantic_review")
    out.append(json.dumps(rep.get("semantic_review"), ensure_ascii=False, indent=1))
    out.append("=== run.degradation_policy")
    out.append(json.dumps(rep["run"].get("degradation_policy"), ensure_ascii=False))
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    print("wrote", out_path, "lines", len(out))


if __name__ == "__main__":
    main()
