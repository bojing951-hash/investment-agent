#!/usr/bin/python3 -I
"""Read-only helper: walk a JSON file by a path like steps[61].envelope.data.top[0].

Usage:
  python3 -I s16_path.py <file.json> <path> keys [maxdepth]   -> list nested keys/values up to maxdepth
  python3 -I s16_path.py <file.json> <path> value              -> print the subtree as compact JSON
"""
import json
import re
import sys


def walk(o, path):
    if path == '':
        return o
    for part in re.findall(r'([^.\[\]]+)|\[(\d+)\]', path):
        name, idx = part
        if idx:
            o = o[int(idx)]
        else:
            o = o[name]
    return o


def show(o, depth, maxdepth, prefix):
    if isinstance(o, dict):
        for k in o:
            v = o[k]
            if isinstance(v, (dict, list)) and depth < maxdepth:
                if isinstance(v, list):
                    print('%s%s = <list %d>' % (prefix, k, len(v)))
                    for i, x in enumerate(v[:6]):
                        if isinstance(x, (dict, list)):
                            show(x, depth + 1, maxdepth, prefix + '%s[%d].' % (k, i))
                        else:
                            print('%s%s[%d] = %s' % (prefix, k, i, str(x)[:400]))
                else:
                    print('%s%s = <dict %d>' % (prefix, k, len(v)))
                    show(v, depth + 1, maxdepth, prefix + k + '.')
            else:
                print('%s%s = %s' % (prefix, k, str(v)[:400]))


def main():
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        d = json.load(f)
    o = walk(d, sys.argv[2])
    if sys.argv[3] == 'keys':
        maxdepth = int(sys.argv[4]) if len(sys.argv) > 4 else 2
        show(o, 0, maxdepth, '')
    else:
        print(json.dumps(o, ensure_ascii=False))


if __name__ == '__main__':
    main()
