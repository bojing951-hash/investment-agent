# -*- coding: utf-8 -*-
# x80_fmtcheck.py — 扫描本席脚本源码(只读): 经 % 运算的字符串字面量能否正常格式化,
# 以及字面量内未转义的百分号(会造成 ValueError)。只读本席目录内脚本, 不触碰受审文件。
# 用法: python3 -I x80_fmtcheck.py <脚本路径>...
import ast, sys, re

OK = re.compile('%(?:%|[-+ #0]*[0-9]*(?:[.][0-9]+)?[sdrfxeg])')
SPEC = re.compile('%[-+ #0]*[0-9]*(?:[.][0-9]+)?[sdrfxeg]')


def specs(s):
    return len(SPEC.findall(s.replace('%%', '')))


def main():
    nbad = 0
    for path in sys.argv[1:]:
        src = open(path, encoding='utf-8').read()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod) and isinstance(node.left, ast.Constant) and isinstance(node.left.value, str):
                s = node.left.value
                n = specs(s)
                try:
                    s % tuple([1] * n)
                except Exception as e:
                    nbad += 1
                    print('BAD  %s:%d  %s' % (path.rsplit('/', 1)[-1], node.lineno, e))
                    print('     %s' % s[:160])
        # 字面量内可疑的裸百分号(非格式串里的 % 也一并列出供人工判断)
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                s = node.value
                rest = OK.sub('', s)
                if '%' in rest:
                    i = rest.index('%')
                    nbad += 1
                    print('SUSP %s:%d  …%s…' % (path.rsplit('/', 1)[-1], node.lineno, rest[max(0, i - 20): i + 12]))
    print('problem lines: %d' % nbad)


main()
