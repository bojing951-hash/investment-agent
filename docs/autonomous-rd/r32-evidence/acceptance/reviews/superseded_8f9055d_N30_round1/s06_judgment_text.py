# usage: s06_judgment_text.py <agent_judgment.json> [maxlen]
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
maxlen = int(sys.argv[2]) if len(sys.argv) > 2 else 100000
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
walk(d, "")
