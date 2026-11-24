import json, sys
jud = json.load(open(sys.argv[1]))
print("== C1 statement =="); print(jud["l3"]["contradictions"][0]["statement"])
print("== C1 explanations =="); print(json.dumps(jud["l3"]["contradictions"][0].get("competing_explanations"), ensure_ascii=False, indent=0))
L = jud["reader_map"]["transmission"][0]["links"]
for i, l in enumerate(L):
    print("== transmission link", i, "==")
    for k in ("main_predicts", "competing_predicts", "observed_fact", "face_off_verdict", "verdict_note"):
        print("[%s] %s" % (k, l.get(k)))
M = jud["l3"]["mechanism_chains"][0]["links"]
for i, l in enumerate(M):
    print("== mech link", i, "==")
    for k in ("evidence_level", "text", "missing_link_note"):
        print("[%s] %s" % (k, l.get(k)))
print("== quality_gate_notes =="); print(json.dumps(jud["quality_gate_notes"], ensure_ascii=False, indent=0))
print("== turnings =="); print(json.dumps(jud["reader_map"]["turnings"], ensure_ascii=False, indent=0))
print("== headline =="); print(jud["reader_map"]["headline"])
