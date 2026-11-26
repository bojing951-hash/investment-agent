#!/usr/bin/env python3
"""Seat-owned read-only extractor: pretty-dumps the judgment (reader_map / l3 / l4 / notes / declaration)
so that quoted sentences can be copied verbatim.
Usage: python3 -I extract_exact.py <agent_judgment.json>
"""
import json
import sys

with open(sys.argv[1], "r", encoding="utf-8") as fh:
    aj = json.load(fh)
print("schema_version=%s" % aj.get("schema_version"))
for k in ("reader_map", "l3", "l4", "quality_gate_notes", "agent_declaration"):
    print("##### %s" % k)
    print(json.dumps(aj.get(k), ensure_ascii=False, indent=1))
extra = sorted(set(aj.keys()) - {"reader_map", "l3", "l4", "quality_gate_notes", "agent_declaration", "schema_version"})
print("##### other top-level keys: %s" % extra)
