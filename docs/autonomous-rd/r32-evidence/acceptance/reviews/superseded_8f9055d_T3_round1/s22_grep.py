#!/usr/bin/python3 -I
"""Read-only probe #8: locate renderer-related phrases in the three report files.
Args: <run_dir>
"""
import os
import sys

run = sys.argv[1]
for fn in ("MAP_REPORT.md", "FULL_REPORT.md", "report.md"):
    lines = open(os.path.join(run, fn), "r", encoding="utf-8").read().split("\n")
    for i, l in enumerate(lines, 1):
        for key in ("见裁定理由", "同轮事件并项", "STALE", "过去一年的三个转折", "待裁", "revision", "verdict"):
            if key in l:
                print("%s:%d [%s] %s" % (fn, i, key, l[:230]))
                break
