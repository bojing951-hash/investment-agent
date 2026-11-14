#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""架构整改 T1+T2 回归套件(2026-11-14,章程§九 PHASE3-PLAN 合并波)。

覆盖:
  S1  thresholds.json v1.0-SIGNED 完整性(69键/唯一/pendng=4全ISM/元数据/
      逐键值=签字稿数值=旧硬编码常量数值——金融席只签不改值);
  S2  macro_scorecard.py 行为等价(带边界扫描: 新TH()读注册表 vs 测试内转录的
      旧硬编码常量逐点比对)+BEI显示串真修复(低通胀<1.5%|高通胀>2.5%,旧串
      低侧1.5误写为2是唯一申报行为差)+体制映射边界+fail-closed;
  S3  data_validator.py 行为等价(11-14真实报告0数值错)+注册表归一化区间
      逐键差(SPX/VIX/WTI/非农——仅差带申报)+A股口径词汇规则显式保留;
  S4  G1-G4 对账门: 现行仓全绿+每门≥1变异红(防对账门本身腐化成橡皮图章);
  S5  framework.md 四处修改在场性(对齐+漂移注记非静默)。

数据纪律: 真实件=audit/r27_gateb_repro/(当日真实锚点副本);旧常量=整改前
macro_scorecard.py v2.0 源码转录(行为基线=operative truth,裁定#1-6)。
"""
import contextlib
import copy
import io
import json
import os
import re
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
for p in (ROOT, os.path.join(ROOT, 'scripts')):
    if p not in sys.path:
        sys.path.insert(0, p)

import data_validator as dv            # noqa: E402
import macro_scorecard as ms           # noqa: E402
import thresholds_gate as tg           # noqa: E402

PASSED, FAILED = [], []


def check(name, cond, detail=''):
    (PASSED if cond else FAILED).append((name, detail))
    print(('  ✅ ' if cond else '  ❌ ') + name + (f' [{detail}]' if not cond and detail else ''))


TH_DOC = json.load(open(os.path.join(ROOT, 'config', 'thresholds.json'), encoding='utf-8'))
ENTRIES = TH_DOC['entries']
FW_TEXT = open(os.path.join(ROOT, 'config', 'framework.md'), encoding='utf-8').read()
DRAFT_PATH = '/Users/cast/agent-loop/ARCH-REFORM/thresholds-registry-draft.json'

# 旧硬编码常量(整改前 macro_scorecard.py v2.0 源码逐字转录——行为基线)
OLD = {
    'umcsent.scorecard.m50': 50, 'umcsent.scorecard.m60': 60,
    'umcsent.scorecard.p80': 80, 'umcsent.scorecard.p95': 95,
    'unemployment_3m.scorecard.p05': 0.5, 'unemployment_3m.scorecard.p03': 0.3,
    'unemployment_3m.scorecard.m01': -0.1, 'unemployment_3m.scorecard.m03': -0.3,
    'rsafs_mom.scorecard.m1': -1.0, 'rsafs_mom.scorecard.m05': -0.5,
    'rsafs_mom.scorecard.p05': 0.5, 'rsafs_mom.scorecard.p1': 1.0,
    'indpro_mom.scorecard.m1': -1.0, 'indpro_mom.scorecard.m03': -0.3,
    'indpro_mom.scorecard.p03': 0.3, 'indpro_mom.scorecard.p1': 1.0,
    'core_cpi.scorecard.m1': 1.0, 'core_cpi.scorecard.m2': 2.0,
    'core_cpi.scorecard.p25': 2.5, 'core_cpi.scorecard.p35': 3.5,
    'bei_10y.scorecard.m15': 1.5, 'bei_10y.scorecard.m2': 2.0,
    'bei_10y.scorecard.p23': 2.3, 'bei_10y.scorecard.p26': 2.6,
    'bei_10y.headline_high': 2.5,
    'wti_f.scorecard.m40': 40, 'wti_f.scorecard.m50': 50,
    'wti_f.scorecard.p70': 70, 'wti_f.scorecard.p90': 90,
    'ahe.scorecard.m2': 2.0, 'ahe.scorecard.m3': 3.0,
    'ahe.scorecard.p35': 3.5, 'ahe.scorecard.p45': 4.5,
    'regime.inflation_total.stagflation_floor': 3, 'regime.growth_total.zero': 0,
}

# 旧评分函数(同源转录;边界语义=代码既成口径,左开右闭)
def _old_band(v, edges, scores):
    for e, s in zip(edges, scores):
        if v < e:
            return s
    return scores[-1]

def old_score(key, v):
    if key == 'umcsent':
        return _old_band(v, (50, 60, 80, 95), (-2, -1, 0, 1, 2))
    if key == 'unemployment':   # 下降沿: change>e 落下档
        for e, s in zip((0.5, 0.3, -0.1, -0.3), (-2, -1, 0, 1, 2)):
            if v > e:
                return s
        return 2
    if key == 'rsafs':
        return _old_band(v, (-1.0, -0.5, 0.5, 1.0), (-2, -1, 0, 1, 2))
    if key == 'indpro':
        return _old_band(v, (-1.0, -0.3, 0.3, 1.0), (-2, -1, 0, 1, 2))
    if key == 'core_cpi':
        return _old_band(v, (1.0, 2.0, 2.5, 3.5), (-2, -1, 0, 1, 2))
    if key == 'bei':
        return _old_band(v, (1.5, 2.0, 2.3, 2.6), (-2, -1, 0, 1, 2))
    if key == 'wti':
        return _old_band(v, (40, 50, 70, 90), (-2, -1, 0, 1, 2))
    if key == 'ahe':
        return _old_band(v, (2.0, 3.0, 3.5, 4.5), (-2, -1, 0, 1, 2))
    raise KeyError(key)


class TestS1ThresholdsRegistry(unittest.TestCase):
    """A: thresholds.json v1.0-SIGNED 落盘完整性。"""

    def test_structure(self):
        keys = [e['stable_key'] for e in ENTRIES]
        check('S1 条目数=69', len(ENTRIES) == 69, str(len(ENTRIES)))
        check('S1 stable_key 唯一', len(set(keys)) == 69)
        pend = [e['stable_key'] for e in ENTRIES if e.get('status') == 'pending']
        check('S1 pending=4 全ISM', pend == ['ism_pmi.scorecard.m48', 'ism_pmi.scorecard.m50',
                                             'ism_pmi.scorecard.p52', 'ism_pmi.scorecard.p55'], str(pend))

    def test_metadata(self):
        check('S1 status=v1.0-SIGNED', 'v1.0-SIGNED' in TH_DOC['status'], TH_DOC['status'][:40])
        check('S1 signed_at=2026-11-14', TH_DOC['signed_at'] == '2026-11-14')
        check('S1 signed_by 含金融席终签', '金融席' in TH_DOC['signed_by'])
        check('S1 adjudication_ref 非空', bool(TH_DOC.get('adjudication_ref')))
        for sec in ('schema', 'boundary_convention', 'unit_policy', 'two_level_model',
                    'kind_vocabulary', 'conflicts'):
            check(f'S1 章节在场: {sec}', sec in TH_DOC)
        check('S1 边界约定=左开右闭', '左开右闭' in json.dumps(TH_DOC['boundary_convention'], ensure_ascii=False))
        check('S1 BEI 双级冲突在 conflicts', 'bei' in json.dumps(TH_DOC['conflicts'], ensure_ascii=False).lower())
        check('S1 entries 不含 validation 字段(G3隔离)',
              all('validation' not in e for e in ENTRIES))

    def test_values_equal_old_code_constants(self):
        """金融席签字只签不改值: 注册表值须与整改前硬编码常量逐键相等。"""
        bad = [k for k, v in OLD.items() if ms.TH(k) != v]
        check('S1 34键值=旧常量逐键相等(零值变)', not bad, str(bad))

    def test_draft_fidelity_local(self):
        """本地在场时对照签字草稿: 全部非 provenance 字段逐字相等;
        provenance 仅授权维护项差异(G1锚同步,裁定 S1-3a)。CI 无该文件→跳过。"""
        if not os.path.exists(DRAFT_PATH):
            print('  ⏭️ 签字草稿不在场(CI 环境),跳过对照')
            return
        draft = json.load(open(DRAFT_PATH, encoding='utf-8'))
        de = {e['stable_key']: e for e in draft['entries']}
        bad = []
        for e in ENTRIES:
            d = de[e['stable_key']]
            for f in e:
                if f != 'provenance' and e[f] != d.get(f):
                    bad.append(f"{e['stable_key']}.{f}: {e[f]!r} != {d.get(f)!r}")
        check('S1 69键非provenance字段=签字稿逐字相等', not bad, '; '.join(bad[:3]))
        edited = sorted(e['stable_key'] for e in ENTRIES
                        if e.get('provenance') != de[e['stable_key']].get('provenance'))
        expect = sorted(['indpro_mom.scorecard.m1', 'indpro_mom.scorecard.m03',
                         'indpro_mom.scorecard.p03', 'indpro_mom.scorecard.p1',
                         'scenario.growth.strong_floor', 'scenario.growth.neutral_floor',
                         'regime.inflation_total.stagflation_floor', 'cn_turnover.bottom_confirm',
                         'sb_flow.5d_cumulative_inflow', 'ahe.scorecard.m2', 'ahe.scorecard.m3',
                         'ahe.scorecard.p45'])
        check('S1 provenance差异=授权锚同步12键(闭合清单)', edited == expect,
              f'实差{len(edited)}: {edited}')


def _run_score(fn, facts):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        scores, total, missing = fn(facts)
    return scores, total, missing


def _score_for(builder, fn, out_key, v):
    return _run_score(fn, builder(v))[0].get(out_key, {}).get('score')


class TestS2ScorecardEquivalence(unittest.TestCase):
    """D: macro_scorecard 行为等价(带边界扫描)+BEI显示真修复。"""

    BUILDERS = [
        ('umcsent', lambda v: [{'metric_id': 'UMCSENT', 'value': v}], ms.score_growth, 'consumer_confidence'),
        ('unemployment', lambda v: [{'metric_id': 'UNEMPLOYMENT', 'derived': {'m3': {'pp_change': v}}}],
         ms.score_growth, 'unemployment_change'),
        ('rsafs', lambda v: [{'metric_id': 'RSAFS', 'derived': {'m1': {'pct_change': v}}}],
         ms.score_growth, 'retail_sales_mom'),
        ('indpro', lambda v: [{'metric_id': 'INDPRO', 'derived': {'m1': {'pct_change': v}}}],
         ms.score_growth, 'industrial_production'),
        ('core_cpi', lambda v: [{'metric_id': 'CORE_CPI', 'derived': {'m12': {'pct_change': v}}}],
         ms.score_inflation, 'core_cpi_yoy'),
        ('bei', lambda v: [{'metric_id': 'BEI_10Y', 'value': v}], ms.score_inflation, 'bei_10y'),
        ('wti', lambda v: [{'metric_id': 'WTI_F', 'value': v}], ms.score_inflation, 'wti_oil'),
        ('ahe', lambda v: [{'metric_id': 'AHE', 'derived': {'m12': {'pct_change': v}}}],
         ms.score_inflation, 'ahe_yoy'),
    ]
    EDGES = {'umcsent': (50, 60, 80, 95), 'unemployment': (0.5, 0.3, -0.1, -0.3),
             'rsafs': (-1.0, -0.5, 0.5, 1.0), 'indpro': (-1.0, -0.3, 0.3, 1.0),
             'core_cpi': (1.0, 2.0, 2.5, 3.5), 'bei': (1.5, 2.0, 2.3, 2.6),
             'wti': (40, 50, 70, 90), 'ahe': (2.0, 3.0, 3.5, 4.5)}

    def test_band_boundary_sweep(self):
        """每指标: 边界点±0.001+极端值逐点比对新旧评分(裁定#6: (+0.1,+0.3]=0)。"""
        eps = 0.001
        for key, build, fn, out in self.BUILDERS:
            probes = []
            for e in self.EDGES[key]:
                probes += [e - eps, e, e + eps]
            probes += [-9999.0, 9999.0, 0.0]
            bad = []
            for v in probes:
                got = _score_for(build, fn, out, v)
                want = old_score(key, v)
                if got != want:
                    bad.append(f'v={v}: 新{got}≠旧{want}')
            check(f'S2 带边界等价: {key}({len(probes)}探针)', not bad, '; '.join(bad[:3]))

    def test_unemployment_gap_band_ruling6(self):
        """裁定#6: (+0.1,+0.3]=0(左开右闭)——+0.3本身=0,刚超+0.3=-1。"""
        build = dict(self.BUILDERS)['unemployment'][1] if False else None
        b = [x for x in self.BUILDERS if x[0] == 'unemployment'][0]
        got03 = _score_for(b[1], ms.score_growth, 'unemployment_change', 0.3)
        got301 = _score_for(b[1], ms.score_growth, 'unemployment_change', 0.3 + 1e-9)
        check('S2 失业率3m: +0.3=0分(右闭归属上档)', got03 == 0, str(got03))
        check('S2 失业率3m: 刚超+0.3=-1分', got301 == -1, str(got301))

    def test_bei_display_true_fix(self):
        """唯一申报行为差: BEI显示串低侧旧串误写『高通胀>2』→真修复
        『低通胀<1.5% | 高通胀>2.5%』(headline 2.5 叙述级)。"""
        scores, _, _ = _run_score(ms.score_inflation, [{'metric_id': 'BEI_10Y', 'value': 2.45}])
        disp = scores['bei_10y']['thresholds']
        check('S2 BEI显示串=低通胀<1.5% | 高通胀>2.5%', disp == '低通胀<1.5% | 高通胀>2.5%', disp)
        dist = scores['bei_10y']['distance_to_switch']
        check('S2 BEI距离按band_edge 2.6计算(2.45→0.15)', dist == '距高通胀线: 0.15%', dist)
        s255, _, _ = _run_score(ms.score_inflation, [{'metric_id': 'BEI_10Y', 'value': 2.55}])
        check('S2 BEI 2.55(<2.6)仍距线未越线(band_edge语义)',
              s255['bei_10y']['distance_to_switch'] == '距高通胀线: 0.05%',
              s255['bei_10y']['distance_to_switch'])

    def test_determine_regime_boundaries(self):
        cases = [((1, 3), '类滞胀'), ((0, 3), '滞胀'), ((1, 2), '再通胀'),
                 ((0, 2), '衰退'), ((1, 2.999), '再通胀'), ((0.001, 3), '类滞胀')]
        for (g, i), want in cases:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                got = ms.determine_regime(g, i)
            check(f'S2 体制映射 g={g} i={i}→{want}', want in got, got)

    def test_fail_closed(self):
        try:
            ms.TH('no.such.key')
            check('S2 fail-closed: 缺键→RuntimeError', False, '未抛异常')
        except RuntimeError as e:
            check('S2 fail-closed: 缺键→RuntimeError', True)
        tmp = os.path.join(tempfile.mkdtemp(), 't.json')
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump({'entries': [{'stable_key': 'a', 'value': 1}]}, f)
        try:
            ms.load_thresholds.cache_clear()
            ms.load_thresholds(tmp)
            ok = False
        except RuntimeError:
            ok = True
        finally:
            ms.load_thresholds.cache_clear()
        check('S2 fail-closed: 常量键缺席于注册表文件→RuntimeError', ok)


FIX = os.path.join(ROOT, 'audit', 'r27_gateb_repro')


def _validate_text(text, anchors, fname='weekly_report_20991231.md'):
    with tempfile.TemporaryDirectory() as td:
        rp = os.path.join(td, fname)
        with open(rp, 'w', encoding='utf-8') as f:
            f.write(text)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            w = dv.validate_report(rp, anchors)
    return w, buf.getvalue()


class TestS3ValidatorEquivalence(unittest.TestCase):
    """C: data_validator 数值词典退役——真实件等价+申报区间差+词汇规则保留。"""

    @classmethod
    def setUpClass(cls):
        with open(os.path.join(FIX, 'anchors_20261114.json'), encoding='utf-8') as f:
            cls.anchors = json.load(f)

    def test_real_report_zero_numeric_errors(self):
        with open(os.path.join(FIX, 'weekly_report_20261114_UNVALIDATED.md'), encoding='utf-8') as f:
            text = f.read()
        warnings, out = _validate_text(text, self.anchors, 'weekly_report_20261114.md')
        errs = [w for w in warnings if w.startswith(('🚨', '❌'))]
        check('S3 11-14真实报告数值类错误=0(等价)', not errs, '; '.join(errs[:3]))
        check('S3 真实件量级检查走注册表(WTI区间[10,300])',
              'WTI范围: 88.92' in out and '[10,300]' in out)

    def test_registry_intervals_and_fail_closed(self):
        for mid, lo, hi in (('SPX', 1000, 30000), ('VIX', 5, 100),
                            ('WTI_F', 10, 300), ('NFP_MOM_K', -2500, 1500)):
            got = dv.metric_validation_range(mid)
            check(f'S3 注册表区间 {mid}=[{lo},{hi}]', got == (lo, hi), str(got))
        try:
            dv.metric_validation_range('NO_SUCH_METRIC')
            check('S3 fail-closed: 未知指标→RuntimeError', False)
        except RuntimeError:
            check('S3 fail-closed: 未知指标→RuntimeError', True)

    def _sanity_only(self, text):
        """隔离量级检查: 置空 REPORT/CHANGE 检查,量级段独立跑。"""
        rc, cc = dv.REPORT_CHECKS, dv.CHANGE_CHECKS
        dv.REPORT_CHECKS, dv.CHANGE_CHECKS = [], []
        try:
            return _validate_text(text, self.anchors)
        finally:
            dv.REPORT_CHECKS, dv.CHANGE_CHECKS = rc, cc

    def test_registry_normalized_differences(self):
        """申报行为差(注册表归一化区间 vs 旧硬编码)逐键验证——仅差带变化。
        注: 非农模式下界-2500K 经现有正则不可达(捕获组仅无符号数,负值不匹配
        旧词典亦不匹配)——注册表下界为纵深防御,非行为差;行为差仅上限面。"""
        cases = [
            ('标普500指数报12000点', True, 'SPX 12000: 旧[2000,10000]❌→注册表[1000,30000]✅'),
            ('VIX收报95', True, 'VIX 95: 旧max90❌→注册表[5,100]✅'),
            ('WTI报250美元', True, 'WTI 250: 旧max200❌→注册表[10,300]✅'),
            ('非农新增120万,就业强劲', True, '非农120万(=1200K): 旧max1000K❌→注册表[-2500,1500]✅'),
        ]
        for text, should_pass, why in cases:
            warnings, out = self._sanity_only(text)
            range_errs = [w for w in warnings if '范围' in w or '非农月增' in w]
            check(f'S3 区间差带: {why}', (not range_errs) == should_pass,
                  '; '.join(range_errs[:2]))

    def test_equivalence_on_real_bands(self):
        """真实带内值: 新旧行为等价(两代区间都放行)。"""
        for text in ('标普500指数报7561点', 'VIX收报19', 'WTI报88美元', '非农新增90万'):
            warnings, _ = self._sanity_only(text)
            check(f'S3 真实带内等价放行: {text}',
                  not [w for w in warnings if ('范围' in w or '非农月新增' in w)],
                  '; '.join(warnings[:2]))

    def test_vocab_rule_kept(self):
        """S1-2a: A股口径词汇规则显式保留(词汇校验,在数值注册表范围之外)。"""
        rule = dv.SANITY_CHECKS.get('A股口径')
        check('S3 A股口径规则在场', rule is not None and 'valid_labels' in (rule or {}))
        check('S3 A股口径规则无数值界字段',
              not (set((rule or {}).keys()) & {'min_value', 'max_value', 'max_value_K'}))
        warnings, out = self._sanity_only('A股成交额达1.5万亿')
        check('S3 无口径标注→⚠️', any('A股口径' in w for w in warnings))
        # 口径标签须落在捕获窗内(成交额→亿 30字窗): 窗外后缀不豁免
        warnings, out = self._sanity_only('A股成交额(全A)1.5万亿')
        check('S3 有口径标注(窗内)→放行', not any('A股口径' in w for w in warnings))
        src = open(os.path.join(ROOT, 'scripts', 'data_validator.py'), encoding='utf-8').read()
        check('S3 源码注释: 词汇规则=词典退役显式例外',
              '词汇' in src and 'S1-2a' in src)


class TestS4Gate(unittest.TestCase):
    """E: G1-G4 现行仓全绿+每门变异红。"""

    def test_all_green_on_repo(self):
        report, pending = tg.run()
        for gate, fails in report.items():
            check(f'S4 门绿: {gate}', not fails, '; '.join(fails[:2]))
        check('S4 pending键显式列出(4 ISM)', len(pending) == 4)

    def _tmp(self, content, suffix):
        p = os.path.join(tempfile.mkdtemp(), suffix)
        with open(p, 'w', encoding='utf-8') as f:
            f.write(content if isinstance(content, str) else json.dumps(content, ensure_ascii=False))
        return p

    def _run_paths(self, **kw):
        args = dict(thresholds_path=os.path.join(ROOT, 'config', 'thresholds.json'),
                    framework_path=os.path.join(ROOT, 'config', 'framework.md'),
                    metrics_path=os.path.join(ROOT, 'config', 'metric_registry.json'),
                    scorecard_path=os.path.join(ROOT, 'scripts', 'macro_scorecard.py'),
                    validator_path=os.path.join(ROOT, 'scripts', 'data_validator.py'))
        args.update(kw)
        report, _ = tg.run(**args)
        return report

    def test_gate_mutations_red(self):
        th = copy.deepcopy(TH_DOC)
        fw = FW_TEXT
        sc = open(os.path.join(ROOT, 'scripts', 'macro_scorecard.py'), encoding='utf-8').read()
        dvs = open(os.path.join(ROOT, 'scripts', 'data_validator.py'), encoding='utf-8').read()
        mr = json.load(open(os.path.join(ROOT, 'config', 'metric_registry.json'), encoding='utf-8'))

        # G1 正向×2: quote篡改 / framework暗改
        t = copy.deepcopy(th); t['entries'][0]['provenance']['quote'] = 'HY OAS | <999bp'
        r = self._run_paths(thresholds_path=self._tmp(t, 'th.json'))
        check('S4 变异红: G1f quote篡改', bool(r['G1_forward']))
        r = self._run_paths(framework_path=self._tmp(fw.replace('<300bp | 300-400bp', '<300bp | 350-400bp'), 'fw.md'))
        check('S4 变异红: G1f framework暗改(改值未改注册表)', bool(r['G1_forward']))
        # G1 反向×2: 孤儿数值 / 未注册行族
        r = self._run_paths(framework_path=self._tmp(fw.replace('| WTI油价 | <50 | >90 |', '| WTI油价 | <45 | >90 |'), 'fw.md'))
        check('S4 变异红: G1r 孤儿阈值数值', bool(r['G1_reverse']))
        r = self._run_paths(framework_path=self._tmp(fw.replace('| 零售销售MoM |', '| 招聘指数MoM |', 1), 'fw.md'))
        check('S4 变异红: G1r 未注册指标行族', bool(r['G1_reverse']))
        # G2×3: 键typo / 声明键被删 / 注册表键无实施(fam向)
        r = self._run_paths(scorecard_path=self._tmp(sc.replace("TH('umcsent.scorecard.m50')", "TH('umcsent.scorecard.m99')"), 'ms.py'))
        check('S4 变异红: G2 TH引用typo键', bool(r['G2']))
        r = self._run_paths(scorecard_path=self._tmp(sc.replace("'umcsent.scorecard.m50', ", ''), 'ms.py'))
        check('S4 变异红: G2 声明键被删(引用漂移)', bool(r['G2']))
        sc2 = sc.replace("'umcsent.scorecard.m50', ", '').replace("TH('umcsent.scorecard.m50')", '50')
        r = self._run_paths(scorecard_path=self._tmp(sc2, 'ms.py'))
        check('S4 变异红: G2 注册表键退回硬编码无实施+G4裸常量',
              bool(r['G2']) and bool(r['G4']))
        # G3×2: 值误收metric range端点 / validation新档位字段
        t = copy.deepcopy(th)
        for e in t['entries']:
            if e['stable_key'] == 'umcsent.scorecard.m50':
                e['metric_id'], e['value'] = 'SPX', 1000.0
        r = self._run_paths(thresholds_path=self._tmp(t, 'th.json'))
        check('S4 变异红: G3 误收validation.range端点值', bool(r['G3']))
        m = copy.deepcopy(mr); m['metrics'][0]['validation'] = dict(m['metrics'][0].get('validation') or {}, band_edge=3)
        r = self._run_paths(metrics_path=self._tmp(m, 'mr.json'))
        check('S4 变异红: G3 metric_registry新增档位字段', bool(r['G3']))
        # G4×3: 退役词典复活 / 校验器裸常量 / 评分卡裸常量
        r = self._run_paths(validator_path=self._tmp(
            dvs.replace('"range_metric_id": "WTI_F"', '"max_value": 200, "range_metric_id": "WTI_F"'), 'dv.py'))
        check('S4 变异红: G4 数值界字段复活(min/max)', bool(r['G4']))
        r = self._run_paths(validator_path=self._tmp(dvs.replace('if val > hi or val < lo:', 'if val > hi or val < 45:'), 'dv.py'))
        check('S4 变异红: G4 校验器阈值位裸数值', bool(r['G4']))
        r = self._run_paths(scorecard_path=self._tmp(
            sc.replace("if v < TH('wti_f.scorecard.m50'):", 'if v < 45.0:'), 'ms.py'))
        check('S4 变异红: G4 评分卡阈值位裸数值', bool(r['G4']))

    def test_gate_cli_exit_code(self):
        rc = os.system(f'{sys.executable} {os.path.join(ROOT, "scripts", "thresholds_gate.py")} > /dev/null 2>&1')
        check('S4 CLI 现行仓退出码=0', rc == 0, str(rc))


class TestS5FrameworkEdits(unittest.TestCase):
    """B: framework.md 四处修改在场性(对齐+漂移注记,非静默)。"""

    def test_growth_table(self):
        check('S5 工业生产MoM(INDPRO)行对齐代码(裁定#5)', '工业生产MoM(INDPRO) | <-0.3% | >+0.3%' in FW_TEXT)
        check('S5 INDPRO评分规则与代码口径一致', '±0.3%=0, +0.3~1%=+1, >+1%=+2' in FW_TEXT)
        check('S5 ISM行保留为待采注记(未删)', '| ISM制造业PMI | <50 | >52 |' in FW_TEXT)
        check('S5 ISM行标注未激活+日期', '待采:未激活,2026-11-14架构整改注' in FW_TEXT)
        check('S5 失业率3m空洞带补行(裁定#6)', '+0.1~+0.3%=0(左开右闭)' in FW_TEXT)
        check('S5 漂移注记#5在场(非静默)', '裁定#5' in FW_TEXT and 'ISM' in FW_TEXT)

    def test_bei_double_level_note(self):
        check('S5 BEI双级注记(裁定#1)', 'bei_10y.headline_high=2.5' in FW_TEXT and 'bei_10y.scorecard.p26=2.6' in FW_TEXT)
        check('S5 BEI评分按band_edge 2.6注记', 'band_edge=2.6' in FW_TEXT)

    def test_scenario_typo_fix(self):
        check('S5 §八 增长中性(+1~+3)笔误修正', '**增长中性 (+1~+3)**' in FW_TEXT)
        check('S5 §八 修正注记(S1-3a)在场', 'S1-3a' in FW_TEXT and '±1~+3' in FW_TEXT)


def main():
    print('══ 架构整改 T1+T2 回归套件(thresholds v1.0 落盘+G1-G4 门)══')
    for cls in (TestS1ThresholdsRegistry, TestS2ScorecardEquivalence,
                TestS3ValidatorEquivalence, TestS4Gate, TestS5FrameworkEdits):
        print(f'── {cls.__name__} ──')
        unittest.main(argv=['x', cls.__name__], exit=False, verbosity=0)
    total, bad = len(PASSED) + len(FAILED), len(FAILED)
    print(f"\n{'='*60}\nT1+T2 回归: {len(PASSED)} PASS / {len(FAILED)} FAIL (共{total}判定)")
    if FAILED:
        for n, d in FAILED:
            print(f"  ❌ {n} [{d}]")
        sys.exit(1)
    print('全部通过 ✅')
    sys.exit(0)


if __name__ == '__main__':
    main()
