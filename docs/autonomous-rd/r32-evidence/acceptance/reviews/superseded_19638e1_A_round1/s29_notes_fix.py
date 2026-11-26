#!/usr/bin/python3 -I
"""Seat-internal: align the notes field of the verdict file with its items list (NIT count 8 -> 9).

Usage:
  python3 -I s29_notes_fix.py <VERDICT-round1.json>
"""
import json
import sys

A = u';美国 12 个月前锚的 GDP 较欧元区、日本早一季(2025Q3 因停摆延至 2025-12-23 首发而当时不可见,取值正确)未在判断档说明。另 NIT 8 条('
B = u'。另 NIT 9 条('
C = u'、证据引用条数未标范围)。'
D = (u'、证据引用条数未标范围、美国 12 个月前锚的 GDP 较欧元区与日本早一季[2025Q3 因停摆延至 2025-12-23 首发而当时不可见,'
     u'取值正确但未在判断档说明])。')
E = u'故裁 UPHELD,must_fix 为空。'
F = (u'故裁 UPHELD,must_fix 为空。引擎渲染面旁注(不计入问题清单): 判断档 quality_gate_notes 六条(盘中时点、对质面、证伪面、'
     u'Gate A 数据面、政策口径披露、引擎缺口披露)原文仅存于 agent_judgment.json,未渲染入 MAP_REPORT.md、FULL_REPORT.md 与 report.md'
     u'(部分内容由 reader_map 与 L3 文字间接带入),报告内『逐项见质量注记』实为指向判断档;披露本身在判断档内与引擎面一致。')


def once(s, frag):
    assert s.count(frag) == 1, (frag, s.count(frag))
    return s.index(frag)


def main():
    path = sys.argv[1]
    with open(path, 'r', encoding='utf-8') as f:
        v = json.load(f)
    n = v['notes']
    i = once(n, A)
    j = once(n, C)
    assert j > i
    n2 = n[:i] + B + n[i + len(A):j] + D + n[j + len(C):]
    k = once(n2, E)
    assert k + len(E) == len(n2), 'expected closing sentence at the end'
    n2 = n2 + F[len(E):]
    assert 'NIT 8' not in n2
    v['notes'] = n2
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(v, f, ensure_ascii=False, indent=2)
        f.write(u'\n')
    print(n2)


if __name__ == '__main__':
    main()
