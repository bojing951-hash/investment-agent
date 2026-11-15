#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V4 判定档夹具构建器(阶段四;确定性,可重跑,幂等)。

从 LIVE 树只读复制 R24 E2E 研究运行的判定档两版(修订版/审计前错误版)
原文,并以 judgment_contract.build_face 从 report.json 构建自包含证据面;
MANIFEST 记源文件 sha256(原 report.json 826KB 不入仓,以哈希锚定)。

用法: python3 tests/build_v4_fixture.py   (源缺失时 fail-closed 退出 1)
"""
import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

from research_contract import judgment_contract as jc          # noqa: E402

SRC = ('/Users/cast/investment-agent-dev/output/research_runs/'
       '20261113T053316Z_美国高收益债利差_HY_OAS_与_SPX_股价_VIX_波动率_'
       'CURVE_2')
DST = os.path.join(HERE, 'fixtures', 'v4')


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for blk in iter(lambda: f.read(1 << 16), b''):
            h.update(blk)
    return h.hexdigest()


def main():
    missing = [n for n in ('report.json', 'judgment.json',
                           'judgment_r24_v1_pre_audit_revision.json')
               if not os.path.exists(os.path.join(SRC, n))]
    if missing:
        print(f'fail-closed: 源缺 {missing} @ {SRC}')
        return 1
    os.makedirs(DST, exist_ok=True)
    report = json.load(open(os.path.join(SRC, 'report.json')))
    face = jc.build_face(report)
    with open(os.path.join(DST, 'evidence_face.json'), 'w') as f:
        json.dump(face, f, ensure_ascii=False, sort_keys=True)
    for src_name, dst_name in (
            ('judgment.json', 'judgment_revised.json'),
            ('judgment_r24_v1_pre_audit_revision.json',
             'judgment_pre_audit.json')):
        shutil.copyfile(os.path.join(SRC, src_name),
                        os.path.join(DST, dst_name))
    lines = ['# V4 冻结夹具 manifest (build_v4_fixture.py 生成)',
             f'source_run: {SRC}',
             'source_files_sha256:']
    for n in ('report.json', 'judgment.json',
              'judgment_r24_v1_pre_audit_revision.json'):
        lines.append(f'  {n}: {sha256(os.path.join(SRC, n))}')
    lines.append('fixture_files_sha256:')
    for n in ('evidence_face.json', 'judgment_revised.json',
              'judgment_pre_audit.json'):
        lines.append(f'  {n}: {sha256(os.path.join(DST, n))}')
    lines.append('note: report.json 全文以源哈希锚定,不整档入仓;'
                 '证据面=S3 概览+S4 序列+L2 观点+evidence_index 提取。')
    with open(os.path.join(DST, 'MANIFEST.sha256'), 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print('fixtures written:', sorted(os.listdir(DST)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
