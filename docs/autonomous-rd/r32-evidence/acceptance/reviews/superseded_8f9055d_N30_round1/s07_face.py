# usage: s07_face.py <report.json> <face: asset_moves|trio|turning|window|cutoff|gaps|dr|gate|frozen|step:NAME> [maxlen]
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
face = sys.argv[2]
maxlen = int(sys.argv[3]) if len(sys.argv) > 3 else 400
def walk(o, p):
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, p + "." + k if p else k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, "%s[%d]" % (p, i))
    else:
        s = o if isinstance(o, str) else json.dumps(o, ensure_ascii=False)
        print("%s = %s" % (p, s[:maxlen]))
rp = d["research_plan"]
if face == "asset_moves": walk(rp["asset_moves"], "")
elif face == "trio": walk(rp["us_rates_trio"], "")
elif face == "turning": walk(rp["turning_candidates"], "")
elif face == "window": walk(rp["question_window"], "")
elif face == "cutoff": walk(rp["cutoff"], "")
elif face == "gaps": walk(rp["dimension_gaps"], "")
elif face == "dr": walk(d["run"]["data_requirements"], "")
elif face == "gate": walk(d["run"]["evidence_gate"], "")
elif face == "frozen": walk(d["run"]["frozen_inputs"], "")
elif face == "clusters": walk(rp["policy_event_clusters"], "")
elif face == "anchors": walk(rp["point_anchors"], "")
elif face.startswith("step:"):
    name = face.split(":", 1)[1]
    for s in d["steps"]:
        if s["step"] == name:
            walk(s, "")
if face == "mapq": walk(rp["map_question"], "")
elif face == "asof": walk(rp["asof_discipline"], "")
elif face == "asdeclared": walk(rp["as_of_declared"], "")
elif face == "spans": walk(rp["consumed_time_spans"], "")
elif face == "anchors_note": walk(rp["anchor_semantics_note"], "")
elif face == "absent": walk(rp["point_values"]["absent"], "")
elif face == "xcf": walk(rp["cross_face_consistency"], "")
elif face == "degr": walk(d["run"]["degradation_policy"], "")
elif face == "notes": walk(d["notes"], "")
