#!/usr/bin/python3 -I
"""Compact dump of research_plan.point_values.cells + other plan faces.
usage: s01_plan_cells.py <report.json>"""
import json
import sys


def main():
    r = json.load(open(sys.argv[1], encoding="utf-8"))
    rp = r["research_plan"]
    pv = rp["point_values"]
    print("point_values keys:", list(pv.keys()))
    for key in pv:
        if key != "cells":
            print("  [%s] %s" % (key, json.dumps(pv[key], ensure_ascii=False)[:1500]))
    for c in pv["cells"]:
        print("=" * 100)
        print("%s/%s/%s  unit=%s vintage=%s" % (c["region"], c["dimension"], c["metric_id"], c.get("unit"), c.get("vintage_semantics")))
        for extra in c:
            if extra not in ("region", "dimension", "metric_id", "display_name", "unit", "face_note", "source", "anchors", "vintage_semantics", "policy_face"):
                print("   extra.%s = %s" % (extra, json.dumps(c[extra], ensure_ascii=False)[:600]))
        pf = c.get("policy_face")
        if pf:
            print("   policy_face = %s" % json.dumps(pf, ensure_ascii=False)[:700])
        for an, a in c["anchors"].items():
            d = dict(a)
            pd_ = d.pop("policy_dates", None)
            pc = d.pop("policy_confirm_date", None)
            fb = d.pop("freshness_basis", None)
            print("   [%s] %s" % (an, json.dumps(d, ensure_ascii=False)))
            if pd_ is not None:
                print("        policy_dates = %s" % json.dumps(pd_, ensure_ascii=False))
            if pc is not None:
                print("        policy_confirm_date=%s freshness_basis=%s" % (pc, fb))
    for k in ("turning_candidates", "us_rates_trio", "asset_moves", "policy_event_clusters", "policy_doc_facts"):
        print("#" * 100)
        print("research_plan/%s" % k)
        print(json.dumps(rp[k], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
