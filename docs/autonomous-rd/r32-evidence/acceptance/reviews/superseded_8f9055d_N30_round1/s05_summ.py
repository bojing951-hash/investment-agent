import sys, json
txt = open(sys.argv[1], encoding="utf-8").read()
i = txt.find("\nMISMATCH")
j = txt.find("\nERR")
cut = [x for x in (i, j) if x >= 0]
head = txt if not cut else txt[:min(cut)]
summ = json.loads(head)
print({k: summ[k] for k in summ if k != "per_section"})
for k, v in summ["per_section"].items():
    print("  ", k, v)
rest = txt[min(cut):] if cut else ""
for ln in rest.splitlines()[:int(sys.argv[2]) if len(sys.argv) > 2 else 80]:
    if ln.startswith("MISMATCH") or ln.startswith("ERR"):
        print(ln[:600])
