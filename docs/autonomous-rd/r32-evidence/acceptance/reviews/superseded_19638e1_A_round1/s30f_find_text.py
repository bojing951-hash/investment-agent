#!/usr/bin/python3 -I
"""Read-only: print lines of a text file containing any of the given substrings, with a context window.

Usage:
  python3 -I s30f_find_text.py <file> <width> <substr> [<substr> ...]
"""
import sys


def main():
    path = sys.argv[1]
    width = int(sys.argv[2])
    pats = sys.argv[3:]
    lines = open(path, encoding='utf-8').read().split('\n')
    n = 0
    for i, l in enumerate(lines):
        for p in pats:
            j = l.find(p)
            if j >= 0:
                n += 1
                lo = max(0, j - width)
                hi = min(len(l), j + len(p) + width)
                print('L%d [%s]: ...%s...' % (i + 1, p, l[lo:hi]))
                break
    print('-- %d lines matched' % n)


if __name__ == '__main__':
    main()
