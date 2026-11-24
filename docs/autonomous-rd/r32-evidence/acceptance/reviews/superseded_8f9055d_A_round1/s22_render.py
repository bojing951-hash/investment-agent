#!/usr/bin/python3 -I
"""Is every judgment text leaf (agent_judgment.json) rendered verbatim in the reader reports? (read-only)
usage: s22_render.py <agent_judgment.json> <MAP_REPORT.md> <FULL_REPORT.md> <report.md>"""
import sys
sys.path.insert(0, "/tmp/r32-accept/review5/A_round1")
import json
import lib
jud = lib.load_json(sys.argv[1])
texts = {}
for fp in sys.argv[2:]:
    texts[fp.rsplit("/", 1)[-1]] = open(fp, encoding="utf-8").read()
leaves = []
def walk(o, path):
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, path + "/" + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, path + "[%d]" % i)
    elif isinstance(o, str):
        leaves.append((path, o))
walk(jud, "")
long_leaves = [(p, s) for p, s in leaves if len(s) >= 40]
print("string leaves total:", len(leaves), "len>=40:", len(long_leaves))
for name, txt in texts.items():
    flat = txt.replace("**", "").replace("\\", "")
    found = sum(1 for p, s in long_leaves if s in flat)
    head = sum(1 for p, s in long_leaves if s not in flat and s[:24] in flat)
    print("%-16s verbatim=%d head-found(truncated/rendered-variant)=%d not-found=%d" % (name, found, head, len(long_leaves) - found - head))
# sections of judgment that are fully rendered in MAP_REPORT / FULL_REPORT
flatm = texts["MAP_REPORT.md"].replace("**", "")
flatf = texts["FULL_REPORT.md"].replace("**", "")
sect = {}
for p, s in long_leaves:
    parts = p.split("/")
    top = parts[1] if len(parts) > 1 else p
    sub = parts[2].split("[")[0] if len(parts) > 2 and not parts[2].startswith("[") else ""
    key = top + ("/" + sub if sub else "")
    n, m, f = sect.get(key, (0, 0, 0))
    sect[key] = (n + 1, m + (1 if s in flatm else 0), f + (1 if s in flatf else 0))
for key, (n, m, f) in sorted(sect.items()):
    print("  section %-34s leaves=%-4d verbatim-in-MAP=%-4d verbatim-in-FULL=%d" % (key, n, m, f))
# list not-found leaves in MAP for key narrative sections (to see how they are rendered)
print("## leaves (len>=40) NOT verbatim in MAP_REPORT.md, by section (first 90 chars)")
miss = [(p, s) for p, s in long_leaves if s not in flatm]
print("n=", len(miss))
for p, s in miss[:60]:
    print("  ", p, "::", s[:90].replace("\n", " "))
