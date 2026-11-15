#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""语义审计席(R32/T-R32-1): 席位章程+首审归档的机核面。

CI 安全: 全部仓内相对路径,零绝对路径依赖,零网络。
判定: 全 PASS 方绿。
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESULTS = []
VOCAB = {'UPHELD', 'REVISE', 'NOT_VERIFIED', 'REJECT_ENTRY'}


def check(name, ok, detail=''):
    RESULTS.append((name, bool(ok), detail))
    print(f"  {'✅' if ok else '❌'} {name}" + (f"  [{detail}]"
                                                if detail and not ok else ''))


# ═══ A. 席位章程 ═══
DOC = os.path.join(ROOT, 'docs', 'autonomous-rd', 'SEMANTIC-AUDIT-SEAT.md')
doc = open(DOC, encoding='utf-8').read() if os.path.isfile(DOC) else ''
check('A1 席位章程在场(§4b operative 版)',
      bool(doc), 'SEMANTIC-AUDIT-SEAT.md 缺')
check('A2 四唤起点+六查职责+四裁决词表+归档协议齐备',
      all(k in doc for k in ('唤起点', '反方攻击', 'REJECT_ENTRY',
                             'append-only')),
      '关键节缺')
check('A3 独立性明文(真 Subagent/可拒开发者声明/简报不含期望)',
      '无 dev 树上下文' in doc and '可拒开发者声明' in doc
      and '不含开发者期望' in doc, '独立性条款缺')

# ═══ B. 首审归档 ═══
ARCH = os.path.join(ROOT, 'audit', 'semantic_review')
days = sorted(glob.glob(os.path.join(ARCH, '*', ''))) if os.path.isdir(ARCH) \
    else []
check('B1 归档树在场(audit/semantic_review/YYYYMMDD/)', bool(days),
      '无归档目录')
verdicts = []
for d in days:
    verdicts += glob.glob(os.path.join(d, 'VERDICT-*.json'))
check('B2 至少一份裁决档(首审)', len(verdicts) >= 1, f'n={len(verdicts)}')
ok_items, ok_vocab, ok_cx, ok_date = 0, True, True, True
for v in verdicts:
    j = json.load(open(v, encoding='utf-8'))
    if j.get('seat') != 'semantic-audit-seat':
        ok_vocab = False
    if j.get('overall') not in VOCAB:
        ok_vocab = False
    items = j.get('items') or []
    ok_items += len(items)
    for it in items:
        if it.get('verdict') not in VOCAB:
            ok_vocab = False
    if not (j.get('counterexamples_sought') or []):
        ok_cx = False
    day = os.path.basename(os.path.dirname(v))
    if str(j.get('audited_at', '')).replace('-', '') != day:
        ok_date = False
check('B3 裁决词表纪律(seat/overall/逐项 verdict 全合法)',
      ok_vocab, '越表裁决')
check('B4 反例义务(每档 counterexamples_sought 非空)', ok_cx, '空反例')
check('B5 日期一致(audited_at 与归档日目录一致)', ok_date, '错位')
check('B6 裁决覆盖面(l3+l4+narrative 合计≥4 项)',
      ok_items >= 4, f"items={ok_items}")
man = os.path.join(ARCH, 'MANIFEST.md')
check('B7 MANIFEST 在场(逐次唤起记录)',
      os.path.isfile(man) and '20261115' in open(man, encoding='utf-8').read(),
      'MANIFEST 缺或无首审行')

n_pass = sum(1 for _, ok, _ in RESULTS if ok)
print(f"\nSEMANTIC-AUDIT-SEAT 判定: {n_pass} PASS / "
      f"{len(RESULTS) - n_pass} FAIL")
sys.exit(0 if n_pass == len(RESULTS) else 1)
