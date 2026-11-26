#!/usr/bin/env python3
"""Print context snippets around needles in the three reader reports (read-only).
usage: python3 -I s10_ctx.py <run_dir> <before> <after> <needle> [<needle> ...]
"""
import os
import sys


def main():
    run = sys.argv[1]
    before, after = int(sys.argv[2]), int(sys.argv[3])
    for name in ("MAP_REPORT.md", "FULL_REPORT.md", "report.md"):
        with open(os.path.join(run, name), "r", encoding="utf-8") as fh:
            txt = fh.read()
        for needle in sys.argv[4:]:
            idx = [i for i in range(len(txt)) if txt.startswith(needle, i)]
            print("=== %s : %r : %d hit(s); file len %d" % (name, needle, len(idx), len(txt)))
            for i in idx[:4]:
                print("--- @%d" % i)
                print(txt[max(0, i - before): i + after])


if __name__ == "__main__":
    main()
