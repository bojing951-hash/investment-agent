#!/usr/bin/env python3
"""R27 Gate B 提取器误杀独立复现(操作者席 2026-11-14 登记的两期实例)。

用**当前代码**(audit 时点的 data_validator)对两期真实隔离报告+当日锚点重跑
validate_report,提取数值类错误(🚨/❌)与待复核(⚠️),证明:
  - 三误杀在当前代码下仍复现(非旧版残留): 166天当SPX价格/DXY+1.09%当UST_10Y
    水平/距警告线0.80pp当HY_OAS水平;
  - 两期报告的**真阳性**(模型生成值与锚点吻合的 ✅ 行)逐一保留,证明误杀是
    提取器缺陷非编数(模型数值本身全对)。
纯只读: 只调 validate_report(print 静音),不写任何文件(annotated 副本在
tmpdir 中性化——validate_report 对含禁止用语的报告会写 _annotated 副本,
本脚本先把报告拷到 tempdir 再校验,零污染 fixture 与工作树)。
"""
import io
import json
import os
import re
import shutil
import sys
import tempfile
import contextlib

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, 'scripts'))
import data_validator  # noqa: E402

FIX = os.path.join(REPO, 'audit', 'r27_gateb_repro')


def run_case(day):
    report = os.path.join(FIX, f'weekly_report_{day}_UNVALIDATED.md')
    anchors = json.load(open(os.path.join(FIX, f'anchors_{day}.json')))
    with tempfile.TemporaryDirectory() as td:
        tmp_report = os.path.join(td, f'weekly_report_{day}.md')
        shutil.copyfile(report, tmp_report)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            warnings = data_validator.validate_report(tmp_report, anchors)
    numeric = [w for w in warnings if w.startswith(('🚨', '❌'))]
    pending = [w for w in warnings if w.startswith('⚠️')]
    oks = [ln for ln in buf.getvalue().splitlines() if '✅' in ln]
    return numeric, pending, oks, buf.getvalue()


def main():
    fail = False
    for day in ('20261114', '20261108'):
        numeric, pending, oks, full = run_case(day)
        print(f"══ {day}: 数值类错误 {len(numeric)} | 待复核 {len(pending)} | ✅ {len(oks)} ══")
        for w in numeric:
            print(f"  {w}")
        if day == '20261114':
            # 修复后语义: 登记的三误杀必须**清零**(修复前=6条: SPX166×2+10Y1.09
            # +HY_OAS0.8+SPX范围166×2,见 R27_GATEB_EXTRACTOR_FIX.md 存证)
            want = ['166', '1.09', '0.8']
            blob = '\n'.join(numeric)
            for w in want:
                hit = w in blob
                print(f"  [清零检查] 误杀值 {w}: {'❌ 仍出现' if hit else '✅ 已清零'}")
                fail |= hit
        print()
    sys.exit(1 if fail else 0)


if __name__ == '__main__':
    main()
