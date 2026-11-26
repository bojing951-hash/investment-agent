import json, sys
p = sys.argv[1]
with open(p) as f: j = json.load(f)
def walk(o, pre=""):
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, pre + "/" + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, pre + "[" + str(i) + "]")
    else:
        s = str(o)
        print(pre, "=", s)
walk(j)
