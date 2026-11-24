#!/usr/bin/python3 -I
"""Outline of agent_judgment.json top two levels (keys and sizes only). Read-only.
Args: <agent_judgment.json>
"""
import json
import sys

jd = json.load(open(sys.argv[1], "r", encoding="utf-8"))


def desc(v):
    if isinstance(v, dict):
        return "dict(%d)" % len(v)
    if isinstance(v, list):
        return "list(%d)" % len(v)
    if isinstance(v, str):
        return "str(%d)" % len(v)
    return repr(v)


for k, v in jd.items():
    print("%-28s %s" % (k, desc(v)))
    if isinstance(v, dict):
        for k2, v2 in list(v.items())[:40]:
            print("      %-34s %s" % (k2, desc(v2)))
            if isinstance(v2, dict):
                for k3, v3 in list(v2.items())[:30]:
                    print("            %-34s %s" % (k3, desc(v3)))
