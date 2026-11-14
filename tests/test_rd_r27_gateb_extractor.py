#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R27 Gate B 提取器误杀修复回归套件(2026-11-14 操作者席登记两期实例)。

修复三缺陷(正道修: 收紧提取器身份/断言语义,零容差放宽):
  (辛) 英文ticker别名标识符边界: "SPX_EPS/PE_TTM滞后166天"的前缀SPX_EPS
       不再当SPX指数 → 166天数据滞后不再被当价格(11-14实例: 97.8%假FAIL);
  (壬) 天数计数守卫: 值后紧跟"天"=时长计数(滞后N天/(N天)),非水平值
       ([年月日]→[年月日天]);
  (癸) 带符号百分数=变化断言非水平: "…10Y收益率大幅上行、美元+1.09%"中邻指标
       美元的周变化不再被当UST_10Y水平(11-14实例: 78.63%假FAIL; TLT同行
       误关联同类); 利率/利差/失业率/信心类捕获组前加符号lookbehind;
  (距离) _SPEC_CONTEXT_RE补"距离": "警告线400bp=4.00%，距离0.80pp"中0.80
       是离阈值距离非HY_OAS水平(11-14实例: [HY_OAS] 0.8假FAIL);
  (子) 语境前视不跨小句边界: "…距离0.59）；WTI 88.92"中上一小句的阈值词
       不得豁免本小句水平断言(距离入_SPEC后的邻句bleed误跳真阳性WTI 88.92)。

数据纪律: 引用句取自真实 2026-11-08/2026-11-14 隔离报告存档
(audit/r27_gateb_repro/,锚点=当日真实锚点副本); 合成对抗句显式标注[示意]。
判死红线: 三误杀句嵌入→零数值类错误; 真错值句→照常❌/🚨(修误杀≠放松校验)。
"""
import io
import json
import os
import re
import shutil
import sys
import tempfile
import unittest
import contextlib

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
for p in (ROOT, os.path.join(ROOT, 'scripts')):
    if p not in sys.path:
        sys.path.insert(0, p)

import data_validator as dv  # noqa: E402

PASSED = []
FAILED = []


def check(name, cond, detail=''):
    (PASSED if cond else FAILED).append((name, detail))
    print(('  ✅ ' if cond else '  ❌ ') + name + (f' [{detail}]' if not cond and detail else ''))


FIX = os.path.join(ROOT, 'audit', 'r27_gateb_repro')


def _load_anchors(day):
    with open(os.path.join(FIX, f'anchors_{day}.json'), encoding='utf-8') as f:
        return json.load(f)


def _validate_text(text, anchors, fname='weekly_report_20991231.md'):
    """在tempdir中对给定文本跑完整validate_report,返回(warnings, stdout)。"""
    with tempfile.TemporaryDirectory() as td:
        rp = os.path.join(td, fname)
        with open(rp, 'w', encoding='utf-8') as f:
            f.write(text)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            w = dv.validate_report(rp, anchors)
    return w, buf.getvalue()


def _numeric_errors(warnings):
    return [w for w in warnings if w.startswith(('🚨', '❌'))]


class TestRealInstanceRepro(unittest.TestCase):
    """两期真实隔离报告(当前代码)全量复验: 误杀清零+真阳性保全。"""

    def test_20261114_no_numeric_errors(self):
        anchors = _load_anchors('20261114')
        with open(os.path.join(FIX, 'weekly_report_20261114_UNVALIDATED.md'),
                  encoding='utf-8') as f:
            text = f.read()
        warnings, out = _validate_text(text, anchors, 'weekly_report_20261114.md')
        errs = _numeric_errors(warnings)
        check('11-14真实报告: 数值类错误=0(修复前6条假FAIL)', not errs,
              '; '.join(errs[:3]))

    def test_20261114_true_positives_preserved(self):
        anchors = _load_anchors('20261114')
        with open(os.path.join(FIX, 'weekly_report_20261114_UNVALIDATED.md'),
                  encoding='utf-8') as f:
            text = f.read()
        _, out = _validate_text(text, anchors, 'weekly_report_20261114.md')
        # 修复前已核验通过的真阳性逐名保全(值本身全对=操作者席定性"非编数")
        for frag in ('SPX收盘: 报告=7561.67', 'WTI油价: 报告=88.92',
                     '黄金价格: 报告=3887.6', 'DXY: 报告=103.41',
                     'VIX: 报告=19.3', 'BTC: 报告=71342.97',
                     'CCC_OAS: 报告=13.14', 'HY_OAS: 报告=3.2',
                     '消费者信心: 报告=48.1', '上证指数: 报告=3634.35'):
            check(f'11-14真阳性保全: {frag}', frag in out)

    def test_20261108_no_numeric_errors(self):
        anchors = _load_anchors('20261108')
        with open(os.path.join(FIX, 'weekly_report_20261108_UNVALIDATED.md'),
                  encoding='utf-8') as f:
            text = f.read()
        warnings, _ = _validate_text(text, anchors, 'weekly_report_20261108.md')
        errs = _numeric_errors(warnings)
        check('11-08真实报告: 数值类错误=0(MW-V1后本已绿,防回退)', not errs,
              '; '.join(errs[:3]))


class TestKillOneSixtySix(unittest.TestCase):
    """(辛)+(壬): SPX_EPS前缀误当SPX + 滞后N天当价格。"""

    def setUp(self):
        self.anchors = _load_anchors('20261114')  # SPX.close=7561.67

    def test_real_sentence_line22(self):
        text = ("数据缺口： 无核心通道缺失；但密歇根信心、零售等月频指标观测日滞后"
                "（DEGRADED），SPX_EPS/PE_TTM滞后166天，本月数据的时效性受限。")
        warnings, _ = _validate_text(text, self.anchors)
        check('(辛)真实句L22 "SPX_EPS/PE_TTM滞后166天" 不产生数值错误',
              not _numeric_errors(warnings), '; '.join(_numeric_errors(warnings)))

    def test_real_sentence_line173(self):
        text = ("  - DEGRADED（观测滞后）：US_REAL_GDP（136天）、"
                "SPX_EPS/PE_TTM（166天）。")
        warnings, _ = _validate_text(text, self.anchors)
        check('(辛)真实句L173 "SPX_EPS/PE_TTM（166天）" 不产生数值错误',
              not _numeric_errors(warnings), '; '.join(_numeric_errors(warnings)))

    def test_sanity_spx_range_also_immunized(self):
        text = "SPX_EPS/PE_TTM滞后166天，本月数据的时效性受限。"
        warnings, _ = _validate_text(text, self.anchors)
        check('(辛)量级检查SPX范围同免疫(166不再进范围断言)',
              not any('SPX范围' in w for w in warnings))

    def test_day_count_guard_space_separated(self):
        # [示意] 空格分隔写法: 别名边界护不住,由(壬)天字守卫兜住
        text = "SPX 盘面数据滞后166天，时效性受限。"
        warnings, _ = _validate_text(text, self.anchors)
        check('(壬)[示意] "SPX 滞后166天"(空格式) 不产生数值错误',
              not _numeric_errors(warnings), '; '.join(_numeric_errors(warnings)))

    def test_true_spx_level_still_validated(self):
        text = "SPX 收于7,561.67。"
        warnings, out = _validate_text(text, self.anchors)
        check('(辛)真水平"SPX 收于7,561.67"照常核验通过',
              not _numeric_errors(warnings) and '报告=7561.67' in out)

    def test_wrong_spx_level_still_fails(self):
        text = "SPX 收于7,999.99。"
        warnings, _ = _validate_text(text, self.anchors)
        check('(辛)真错值"SPX 7,999.99"照常报错(修误杀≠放松校验)',
              bool(_numeric_errors(warnings)))

    def test_identifier_boundary_underscore_digit(self):
        # [示意] 下划线/数字续接=另一标识符; 旧(?![a-zA-Z])挡不住下划线
        for ident in ('SPX_EPS', 'SPX50', 'VIX3M', 'DXY_INDEX'):
            src = dv.REPORT_CHECKS
            text = f"{ident} 滞后166天。"
            warnings, _ = _validate_text(text, self.anchors)
            check(f'(辛)[示意] "{ident}" 前缀不当指标别名',
                  not _numeric_errors(warnings), '; '.join(_numeric_errors(warnings)))

    def test_identifier_family_value_not_index(self):
        # [示意] EPS族标识符携带自身价值(非天数): 此处(辛)边界独挡——
        # 旧别名SPX会把"186.50"当SPX价格→97.5%假FAIL(天字守卫护不住此形态)
        text = "SPX_EPS最新报186.50，低于模型预期。"
        warnings, _ = _validate_text(text, self.anchors)
        check('(辛)[示意] "SPX_EPS…186.50"(EPS族值) 不当SPX价格',
              not _numeric_errors(warnings), '; '.join(_numeric_errors(warnings)))


class TestSignedPercentIsChange(unittest.TestCase):
    """(癸): 带符号百分数=变化断言,不作为水平捕获。"""

    def setUp(self):
        self.anchors = _load_anchors('20261114')  # UST_10Y=5.1, HY_OAS=3.2

    def test_real_sentence_dxy_change(self):
        text = ("但同期2Y/10Y收益率大幅上行、美元+1.09%。本周是"
                "“股涨+债收益率升+美元涨”组合。")
        warnings, _ = _validate_text(text, self.anchors)
        check('(癸)真实句 "10Y收益率…美元+1.09%" 不产生数值错误',
              not _numeric_errors(warnings), '; '.join(_numeric_errors(warnings)))

    def test_tlt_class_same_sentence(self):
        # [示意] TLT同行误关联同类: 邻指标带符号周涨幅紧随利率别名
        text = "10Y收益率全曲线下行、TLT +0.10%。"
        warnings, _ = _validate_text(text, self.anchors)
        check('(癸)[示意] "10Y收益率…TLT +0.10%" 不产生数值错误',
              not _numeric_errors(warnings), '; '.join(_numeric_errors(warnings)))

    def test_fullwidth_and_minus_signs(self):
        for s in ('＋', '-', '−'):
            text = f"10Y收益率上行、美元{s}1.09%。"
            warnings, _ = _validate_text(text, self.anchors)
            check(f'(癸)[示意] 符号"{s}"后1.09%不作为UST_10Y水平',
                  not _numeric_errors(warnings), '; '.join(_numeric_errors(warnings)))

    def test_hyoas_oil_change_neighbor(self):
        # [示意] 高收益利差句后邻指标带符号变化(HY_OAS旧守卫只挡"-")
        text = "高收益利差走阔、油价+5.12%。"
        warnings, _ = _validate_text(text, self.anchors)
        check('(癸)[示意] "高收益利差…油价+5.12%" 不产生数值错误',
              not _numeric_errors(warnings), '; '.join(_numeric_errors(warnings)))

    def test_true_level_still_validated(self):
        text = "10Y收益率报5.10%。"
        _, out = _validate_text(text, self.anchors)
        check('(癸)真水平"10Y收益率报5.10%"照常核验通过',
              '10Y收益率: 报告=5.1' in out)

    def test_wrong_level_still_fails(self):
        text = "10Y收益率报5.90%。"
        warnings, _ = _validate_text(text, self.anchors)
        check('(癸)真错值"10Y收益率5.90%"照常报错',
              bool(_numeric_errors(warnings)))

    def test_unrate_and_umcsent_guards(self):
        # [示意] 失业率/信心类同守卫: 邻项带符号值不被当水平; 真水平照常
        a08 = _load_anchors('20261108')
        text = "失业率持平、初请+4.4%。"
        warnings, _ = _validate_text(text, a08)
        check('(癸)[示意] "失业率持平、初请+4.4%" 不产生数值错误',
              not _numeric_errors(warnings), '; '.join(_numeric_errors(warnings)))
        text2 = "失业率降至4.1%。"
        _, out2 = _validate_text(text2, a08)
        check('(癸)真水平"失业率4.1%"照常核验通过', '失业率: 报告=4.1' in out2)


class TestDistanceSpecContext(unittest.TestCase):
    """(距离): 离阈值的距离值不作水平断言;(子): 语境不跨小句边界。"""

    def setUp(self):
        self.anchors = _load_anchors('20261114')  # HY_OAS=3.2

    def test_real_sentence_threshold_distance(self):
        text = ("**关键阈值监控**：HY OAS 3.20%（警告线400bp=4.00%，距离0.80pp）；"
                "CCC OAS 13.14%（恐慌线1000bp=10.00%，已处恐慌区）。")
        warnings, _ = _validate_text(text, self.anchors)
        check('(距离)真实句 "警告线…，距离0.80pp" 不产生数值错误',
              not _numeric_errors(warnings), '; '.join(_numeric_errors(warnings)))

    def test_distance_level_still_validated(self):
        text = "HY OAS 3.20%（警告线400bp=4.00%，距离0.80pp）。"
        _, out = _validate_text(text, self.anchors)
        check('(距离)真水平3.20%照常核验(豁免只及距离值0.80)',
              'HY_OAS: 报告=3.2' in out)

    def test_clause_boundary_no_bleed(self):
        # (子)真实句: 上一小句"距离0.59）；"不得豁免本小句WTI水平断言
        text = ("DXY 103.41（强势阈值104，距离0.59）；WTI 88.92（偏紧区间85-90内）。")
        warnings, out = _validate_text(text, self.anchors)
        check('(子)真实句 "距离0.59）；WTI 88.92" WTI真阳性照常核验',
              'WTI油价: 报告=88.92' in out and not _numeric_errors(warnings),
              '; '.join(_numeric_errors(warnings)))

    def test_spec_context_same_clause_still_exempts(self):
        # [示意] 同小句阈值词豁免仍有效(不因(子)收紧而失效)
        text = "若SPX收复7700关口将改变风险偏好。"
        warnings, _ = _validate_text(text, self.anchors)
        check('(子)[示意] 同小句"若SPX收复7700"豁免仍有效',
              not _numeric_errors(warnings))


class TestChangeCheckClauseBoundary(unittest.TestCase):
    """CHANGE_CHECKS 前视语境同步不跨小句(子案对称面)。"""

    def test_change_exemption_not_bleeding(self):
        a08 = _load_anchors('20261108')
        # [示意] 上一小句的阈值词不豁免本小句的WTI周变化断言
        text = "红线5.0%已突破；WTI周涨5.12%。"
        warnings, _ = _validate_text(text, a08)
        # WTI周变化锚点在11-08批次缺席 → 待复核而非误判通过; 但不得因邻句bleed被豁免
        has_pending = any('WTI周涨跌' in w and '待复核' in w for w in warnings)
        check('(子)[示意] 周变化断言不被上一小句阈值词豁免(仍进比对/待复核)',
              has_pending)


class TestClauseLocalHelper(unittest.TestCase):
    """_clause_local 单元面: 截断语义逐字符级钉死。"""

    def test_truncation_points(self):
        f = dv._clause_local
        check('子:无边界返回全窗', f('abc def', 7, 12) == 'abc def')
        check('子:全角分号截断', f('距离0.59）；WT', 11) == 'WT')
        check('子:句号截断', f('已突破。HY O', 9) == 'HY O')
        check('子:多边界取最近', f('a。b；c）d', 9) == 'd')
        check('子:换行截断', f('a\nWTI 88', 7) == 'WTI 8')
        check('子:窗口不足12取到头', f('WT', 2, 12) == 'WT')

    def test_spec_regex_has_distance(self):
        check('距离: _SPEC_CONTEXT_RE 含"距离"',
              bool(dv._SPEC_CONTEXT_RE.search('，距离0.80')))


def main():
    print('══ R27 Gate B 提取器误杀修复套件 ══')
    print('── Section 1: 两期真实实例全量复验 ──')
    unittest.main(argv=['x', 'TestRealInstanceRepro'], exit=False, verbosity=0)
    print('── Section 2: (辛)+(壬) SPX_EPS/滞后N天 ──')
    unittest.main(argv=['x', 'TestKillOneSixtySix'], exit=False, verbosity=0)
    print('── Section 3: (癸) 带符号百分数=变化 ──')
    unittest.main(argv=['x', 'TestSignedPercentIsChange'], exit=False, verbosity=0)
    print('── Section 4: (距离)+(子) 阈值距离与小句边界 ──')
    unittest.main(argv=['x', 'TestDistanceSpecContext'], exit=False, verbosity=0)
    print('── Section 5: (子) 周变化语境对称面 ──')
    unittest.main(argv=['x', 'TestChangeCheckClauseBoundary'], exit=False, verbosity=0)
    print('── Section 6: _clause_local 单元面 ──')
    unittest.main(argv=['x', 'TestClauseLocalHelper'], exit=False, verbosity=0)

    total, bad = len(PASSED) + len(FAILED), len(FAILED)
    print(f"\n{'='*60}\nR27 Gate B 误杀修复: {len(PASSED)} PASS / {len(FAILED)} FAIL (共{total}判定)")
    if FAILED:
        for n, d in FAILED:
            print(f"  ❌ {n} [{d}]")
        sys.exit(1)
    print('全部通过 ✅')
    sys.exit(0)


if __name__ == '__main__':
    main()
