#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""复杂度基线(Product Convergence Phase 1 / 章程§四.4)。

只测+只登记,不做任何重构(章程: 本轮不瘦身)。产出/比对:
  python3 scripts/complexity_baseline.py --write docs/autonomous-rd/COMPLEXITY_BASELINE.md
  python3 scripts/complexity_baseline.py --check   # 与在档基线比对,超阈值 exit 1

度量(刻意朴素,可独立复算):
  - 生产代码 py 文件数/总行数(排除 tests/、docs/、audit/)
  - tests/ py 文件数/总行数
  - 最大 10 文件(生产面)
  - 函数数(ast 数,粗粒度)
增长控制: 新增框架/系统/重复模型须过章程§四.4 证明;基线漂移>5% 需在
  CODEBASE_SIMPLIFICATION_BACKLOG 或波次说明里登记理由,否则 --check 红。
"""
import argparse
import ast
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
BASELINE_MD = os.path.join(ROOT, 'docs', 'autonomous-rd', 'COMPLEXITY_BASELINE.md')

EXCLUDE_DIRS = {'docs', 'audit', '.git', 'output', 'data', 'node_modules',
                '__pycache__', 'research_archive', '.claude', 'ops'}  # tests 不剪枝=需分类计数


def collect(dirs_filter_prod=True):
    prod_files, test_files = [], []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        rel = os.path.relpath(dirpath, ROOT)
        parts = set(rel.split(os.sep))
        if parts & EXCLUDE_DIRS:
            dirnames[:] = []
            continue
        for fn in filenames:
            if not fn.endswith('.py'):
                continue
            p = os.path.join(dirpath, fn)
            info = {'path': os.path.relpath(p, ROOT), 'lines': 0, 'funcs': 0}
            try:
                src = open(p, encoding='utf-8').read()
                info['lines'] = src.count('\n') + 1
                info['funcs'] = sum(1 for n in ast.walk(ast.parse(src))
                                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))
            except Exception:
                info['lines'] = -1  # 不可解析如实计
            (test_files if 'tests' in parts else prod_files).append(info)
    return prod_files, test_files


def metrics(prod, test):
    pl = sum(f['lines'] for f in prod)
    tl = sum(f['lines'] for f in test)
    pf = sum(f['funcs'] for f in prod)
    top = sorted((f for f in prod if f['lines'] > 0), key=lambda x: -x['lines'])[:10]
    return {'prod_files': len(prod), 'prod_lines': pl, 'prod_funcs': pf,
            'test_files': len(test), 'test_lines': tl, 'top10': top}


def render(m):
    lines = ['# COMPLEXITY_BASELINE — 复杂度基线(章程§四.4,只测不瘦)', '',
             f'- 生产面: {m["prod_files"]} py 文件 / {m["prod_lines"]} 行 / {m["prod_funcs"]} 函数',
             f'- 测试面: {m["test_files"]} py 文件 / {m["test_lines"]} 行',
             '', '## 最大 10 文件(生产面)', '', '| 文件 | 行数 |', '|---|---|']
    for f in m['top10']:
        lines.append(f'| {f["path"]} | {f["lines"]} |')
    lines += ['', '## 增长控制',
              '- 新增框架/系统/重复模型: 须证明不可复用+登记成本(章程§四.4)',
              '- 基线漂移>5% 未登记理由 → `complexity_baseline.py --check` 红',
              '- 重构候选只进 CODEBASE_SIMPLIFICATION_BACKLOG(DEFERRED,本轮不执行)']
    return '\n'.join(lines) + '\n'


def parse_baseline():
    if not os.path.exists(BASELINE_MD):
        return None
    m = {}
    for line in open(BASELINE_MD, encoding='utf-8'):
        if line.startswith('- 生产面:'):
            seg = line.split()
            m['prod_files'], m['prod_lines'], m['prod_funcs'] = int(seg[2]), int(seg[6]), int(seg[9])
        if line.startswith('- 测试面:'):
            seg = line.split()
            m['test_files'], m['test_lines'] = int(seg[2]), int(seg[6])
    return m or None


def main(argv=None):
    ap = argparse.ArgumentParser(description='复杂度基线(只测不瘦)')
    ap.add_argument('--write', action='store_true', help='写基线档')
    ap.add_argument('--check', action='store_true', help='与在档基线比对(>5%漂移红)')
    args = ap.parse_args(argv)
    m = metrics(*collect())
    if args.write:
        open(BASELINE_MD, 'w', encoding='utf-8').write(render(m))
        print(f'基线已写: 生产 {m["prod_files"]}f/{m["prod_lines"]}L, 测试 {m["test_files"]}f/{m["test_lines"]}L')
        return 0
    base = parse_baseline()
    if base is None:
        print('无基线档——先 --write')
        return 2
    drifts = []
    for k, old in base.items():
        if k == 'top10':
            continue
        new = m.get(k, 0)
        if old > 0:
            drift = (new - old) / old
            if abs(drift) > 0.05:
                drifts.append(f'{k}: {old}→{new} ({drift:+.1%})')
    print(f'当前: 生产 {m["prod_files"]}f/{m["prod_lines"]}L vs 基线 {base["prod_files"]}f/{base["prod_lines"]}L')
    if drifts:
        print('❌ 超 5% 漂移未登记:')
        for d in drifts:
            print('  -', d)
        return 1
    print('✅ 基线内(±5%)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
