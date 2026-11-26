#!/usr/bin/python3 -I
"""席位自写脚本 s00: 只读探测 report.json / 快照 / 注册表的结构(键与规模)."""
import json
import sys


def describe(obj, depth=0, maxdepth=2, prefix=""):
    ind = "  " * depth
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, dict):
                print(f"{ind}{k}: dict({len(v)})")
                if depth < maxdepth:
                    describe(v, depth + 1, maxdepth)
            elif isinstance(v, list):
                t = type(v[0]).__name__ if v else "-"
                print(f"{ind}{k}: list({len(v)}) [{t}]")
            else:
                s = repr(v)
                if len(s) > 160:
                    s = s[:160] + "…"
                print(f"{ind}{k}: {s}")
    elif isinstance(obj, list):
        print(f"{ind}list({len(obj)})")


def main():
    mode = sys.argv[1]
    path = sys.argv[2]
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    if mode == "report":
        print("== report.json top keys ==")
        describe(d, 0, 1)
    elif mode == "snapshot":
        print("== snapshot top keys ==")
        describe(d, 0, 1)
    elif mode == "registry":
        print("== registry top keys ==")
        describe(d, 0, 1)
    else:
        raise SystemExit("unknown mode")


if __name__ == "__main__":
    main()
