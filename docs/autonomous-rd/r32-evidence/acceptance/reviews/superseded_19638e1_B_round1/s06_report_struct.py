# -*- coding: utf-8 -*-
"""只读: report.json 顶层结构。用法: python3 -I s06_report_struct.py <report_json>"""
import json, sys
p = sys.argv[1]
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)
def sz(o):
    return len(json.dumps(o, ensure_ascii=False))
print("TOP KEYS:")
for k, v in d.items():
    t = type(v).__name__
    extra = ""
    if isinstance(v, dict):
        extra = " subkeys=" + str(list(v.keys())[:60])
    elif isinstance(v, list):
        extra = " len=%d" % len(v)
    print("  %-28s %-6s bytes=%d%s" % (k, t, sz(v), extra))
rp = d.get('research_plan')
if isinstance(rp, dict):
    print("\nRESEARCH_PLAN keys:")
    for k, v in rp.items():
        t = type(v).__name__
        extra = ""
        if isinstance(v, dict):
            extra = " subkeys=" + str(list(v.keys())[:60])
        elif isinstance(v, list):
            extra = " len=%d" % len(v)
        print("  %-28s %-6s bytes=%d%s" % (k, t, sz(v), extra))
aj = d.get('agent_judgment')
print("\nagent_judgment type", type(aj).__name__, (list(aj.keys()) if isinstance(aj, dict) else ""))
st = d.get('steps')
print("\nsteps n=", len(st) if isinstance(st, list) else st)
if isinstance(st, list):
    for s in st:
        if isinstance(s, dict):
            print("  step keys", list(s.keys())[:20], "| name=", s.get('name') or s.get('step') or s.get('id'), "| status=", s.get('status'))
