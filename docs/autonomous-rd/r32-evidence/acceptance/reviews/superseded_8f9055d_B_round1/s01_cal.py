import json, sys
cal = sys.argv[1]
with open(cal) as f: c = json.load(f)
print("version:", c["version"], "created:", c["created"], "updated:", c["updated"])
print("== batches ==")
for b in c["batches"]:
    print(json.dumps(b, ensure_ascii=False))
print("== entries ==")
for e in c["entries"]:
    print(json.dumps(e, ensure_ascii=False))
