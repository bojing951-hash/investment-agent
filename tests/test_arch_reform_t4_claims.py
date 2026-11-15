#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""架构整改 T4 回归套件(2026-11-14,PHASE3-PLAN 工单T4: claim_factory
确定性六型+claim_bundle 容器)。

覆盖:
  S1-S6  六型真实快照用例(验收原文「每型≥3」): fixture=tests/fixtures/
     t4_claims/snapshot_slice_20261114.json(真实快照垂直切片,出处注记随档),
     逐 claim 值以**套件内独立复算**(非回叫工厂函数)对照;契约字面值五钉:
     HY_OAS 距警告线 0.80(契约§2 示例)/CURVE sign_flip=2024-09-05(§3)/
     JP_POLICY_RATE 滞后74天(§4 STALE 行)/Fed 带 3.75–4.00 与 DXY 带
     100–104(§2 band 例);
  U1  单位代数反例(律3): pp↔bp ×100 精确+错值红/percent→pp 无基准拒/
     「400bp 与 4.00%」两 token 映射同一 threshold claim/跨单位 spread 拒;
  P1  谓词反例(§3 文法): percentile 并列半权手算(Fraction 对照)/min-n 门
     (n<20→INSUFFICIENT_EVIDENCE)/月频 ytd 禁用/crossing_count 手数对照
     (真实 HY_OAS 序列)/last_crossing 独立扫对照/AND 组合;
  Z1  零模型调用断言: 静态(模块源码无模型客户端 import/不读 MODEL_* env/
     无网络无随机)+动态(MODEL_* 环境绊线子进程生成=逐字节同输出;
     生成全程零网络模块载入);
  D1  确定性与 schema 咬合: 双跑逐字节相等/写读往返/七类 schema 变异必红/
     诚实缺席台账(SPX/CPI 无阈值=不产不造)。

数据纪律: fixture 为真实快照**复制提取**垂直切片(源档 sha256+提取日随档内
_fixture_provenance 注记);代码零指向 LIVE 树、零绝对路径、零网络
(CI 干净克隆安全)。
"""
import copy
import json
import os
import subprocess
import sys
import unittest
from datetime import date
from fractions import Fraction

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
for p in (ROOT, os.path.join(ROOT, 'scripts')):
    if p not in sys.path:
        sys.path.insert(0, p)

from research_contract import claim_factory as cf   # noqa: E402
from research_contract import claim_bundle as cb    # noqa: E402

FIXTURE = os.path.join(ROOT, 'tests', 'fixtures', 't4_claims',
                       'snapshot_slice_20261114.json')

PASSED, FAILED = [], []


def check(name, cond, detail=''):
    (PASSED if cond else FAILED).append((name, detail))
    print(('  ✅ ' if cond else '  ❌ ') + name + (f' [{detail}]' if not cond and detail else ''))


def _run_case(cls):
    """R42(RDG-20261116-012): 逐类跑 unittest 且 errors/failures 计入退出码——
    旧 unittest.main(exit=False) 只以 check() 台账定退出,测级异常被吞(exit 0)。"""
    from io import StringIO
    suite = unittest.TestLoader().loadTestsFromTestCase(cls)
    res = unittest.TextTestRunner(stream=StringIO(), verbosity=0).run(suite)
    n = len(res.errors) + len(res.failures)
    print(f'   unittest: {res.testsRun} tests, {n} error/failure' if n
          else f'   unittest: {res.testsRun} tests OK')
    return n


def find(claims, **kw):
    """按字段精确匹配取单条(多匹配/零匹配=测试自败)。"""
    hits = [c for c in claims
            if all(c.get(k) == v for k, v in kw.items())]
    return hits[0] if len(hits) == 1 else None


# ── 独立复算器(禁回叫被测函数,防同义反复) ──────────────────────────
def ind_last_crossing(dates, values, level):
    for i in range(len(values) - 1, 0, -1):
        if (values[i - 1] - level) * (values[i] - level) < 0:
            return dates[i]
    return None


def ind_crossings_since(dates, values, level, since):
    n = 0
    for i in range(1, len(values)):
        if (values[i - 1] - level) * (values[i] - level) < 0 and dates[i] >= since:
            n += 1
    return n


def ind_percentile(values, current):
    less = sum(1 for v in values if v < current)
    ties = sum(1 for v in values if v == current)
    return Fraction(100 * (less + Fraction(1, 2) * ties), len(values))


class BundleBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(FIXTURE, 'r', encoding='utf-8') as f:
            cls.snap = json.load(f)
        cls.bundle = cf.generate_claims_bundle(cls.snap)
        cls.claims = cls.bundle['claims']

    def _fact(self, mid):
        hits = [f for f in self.snap['facts'] if f['metric_id'] == mid]
        return hits[0] if len(hits) == 1 else None


# ══ S1 level ═══════════════════════════════════════════════════════

class TestS1Level(BundleBase):
    def test_s1_point_levels(self):
        for mid, val, unit in (('SPX', 7561.67, 'index_point'),
                               ('UST_10Y', 5.1, 'percent'),
                               ('HY_OAS', 3.2, 'percentage_point'),
                               ('DXY', 103.41, 'index_point'),
                               ('CPI', 337.476, 'index_point_1982_84')):
            c = find(self.claims, claim_type='level', subtype='point', metric_id=mid)
            f = self._fact(mid)
            check(f'S1 level.point {mid} 值直读={val}(Fact 层零改写)',
                  c is not None and c['value'] == val and c['unit'] == unit
                  and c['value'] == f['value'],
                  f"got={None if not c else c['value']}")
            check(f'S1 level.point {mid} 证据 ref 带值带单位({f["fact_id"]})',
                  c is not None and c['evidence_refs'][0]['ref'] == f['fact_id']
                  and c['evidence_refs'][0]['value'] == val
                  and c['evidence_refs'][0]['unit'] == unit)

    def test_s1_band_levels(self):
        fed = find(self.claims, claim_type='level', subtype='band',
                   metric_ids=['DFEDTARL', 'DFEDTARU'])
        check('S1 level.band Fed 目标带={low:3.75,high:4.0} percent'
              '(契约§2 band 例「3.75–4.00%」)',
              fed is not None and fed['value'] == {'low': 3.75, 'high': 4.0}
              and fed['unit'] == 'percent')
        dxy = find(self.claims, claim_type='level', subtype='band', metric_id='DXY')
        check('S1 level.band DXY 带={low:100.0,high:104.0} index_point'
              '(契约§2 band 例「100-104」;注册表 band_edge 对)',
              dxy is not None and dxy['value'] == {'low': 100.0, 'high': 104.0}
              and dxy['unit'] == 'index_point')
        check('S1 level.band 均为一带对象两数(low<=high)',
              fed['value']['low'] <= fed['value']['high']
              and dxy['value']['low'] <= dxy['value']['high'])


# ══ S2 change ══════════════════════════════════════════════════════

class TestS2Change(BundleBase):
    def test_s2_relative(self):
        for mid, win in (('SPX', 'week'), ('CPI', 'm1'), ('NDX', 'ytd')):
            f = self._fact(mid)
            rec = f['derived'][win]
            c = find(self.claims, claim_type='change', subtype='relative',
                     metric_id=mid, window=win)
            expect = round((f['derived']['end']['value'] / rec['basis_value'] - 1) * 100, 4)
            check(f'S2 change.relative {mid}/{win}={rec["pct_change"]} percent'
                  f'(独立复算 (末值/基准−1)×100)',
                  c is not None and c['value'] == rec['pct_change']
                  and c['unit'] == 'percent' and c['value'] == expect,
                  f'expect={expect} got={None if not c else c["value"]}')
            check(f'S2 change.relative {mid}/{win} 律2: basis 必带'
                  f'(basis_date={rec["basis_date"]}/basis_value={rec["basis_value"]})',
                  c is not None and c['basis_date'] == rec['basis_date']
                  and c['basis_value'] == rec['basis_value'])

    def test_s2_absolute(self):
        hy = find(self.claims, claim_type='change', subtype='absolute',
                  metric_id='HY_OAS', window='week')
        f = self._fact('HY_OAS')
        rec = f['derived']['week']
        check('S2 change.absolute HY_OAS/week=−0.22 percentage_point'
              '(独立复算 末值−基准)',
              hy is not None and hy['value'] == rec['pp_change'] == -0.22
              and hy['unit'] == 'percentage_point'
              and hy['value'] == round(f['derived']['end']['value'] - rec['basis_value'], 4))
        check('S2 change.absolute HY_OAS bp 别名=−22.0 basis_point(×100 精确,'
              '与 Fact 层 bp_change 逐字)',
              hy is not None and hy['unit_aliases'] == {'basis_point': -22.0}
              and rec['bp_change'] == -22.0)
        ust = find(self.claims, claim_type='change', subtype='absolute',
                   metric_id='UST_10Y', window='week')
        check('S2 change.absolute UST_10Y/week=+0.24 percentage_point(别名 24.0bp)',
              ust is not None and ust['value'] == 0.24
              and ust['unit_aliases'] == {'basis_point': 24.0})

    def test_s2_dual_track(self):
        """双轨跟随 Fact 层(§0/律3): SPX 无 absolute、UST_10Y/HY_OAS 无 relative。"""
        spx_abs = [c for c in self.claims if c['claim_type'] == 'change'
                   and c['subtype'] == 'absolute' and c['metric_id'] == 'SPX']
        check('S2 双轨: SPX(价格类)零 absolute 变化(不合成另一轨)',
              spx_abs == [], f'n={len(spx_abs)}')
        for mid in ('UST_10Y', 'HY_OAS'):
            rel = [c for c in self.claims if c['claim_type'] == 'change'
                   and c['subtype'] == 'relative' and c['metric_id'] == mid]
            check(f'S2 双轨: {mid}(利率类)零 relative 变化', rel == [],
                  f'n={len(rel)}')

    def test_s2_no_invention(self):
        """变化值只直读 Fact 层 derived(工厂零重算零造轨): 全量逐一核对。"""
        ok = True
        for c in self.claims:
            if c['claim_type'] != 'change':
                continue
            rec = (self._fact(c['metric_id']) or {}).get('derived', {}).get(c['window'], {})
            key = {'relative': 'pct_change', 'absolute': None}.get(c['subtype'])
            if c['subtype'] == 'absolute':
                key = 'pp_change' if c['unit'] == 'percentage_point' else 'abs_change'
            if c['value'] != rec.get(key):
                ok = False
        check('S2 全量 change 值=Fact 层 derived 字段逐字直读(56 条零改写)', ok)


# ══ S3 comparison ══════════════════════════════════════════════════

class TestS3Comparison(BundleBase):
    def test_s3_spreads(self):
        usjp = find(self.claims, claim_type='comparison', subtype='spread',
                    comparison_name='us_jp_rate_spread')
        dff, jp = self._fact('DFF'), self._fact('JP_POLICY_RATE')
        expect = round(dff['value'] - jp['value'], 6)
        check(f'S3 spread 美日利差 DFF−JP={expect} percent(独立复算;同单位 percent)',
              usjp is not None and usjp['value'] == expect == 2.837
              and usjp['unit'] == 'percent')
        check('S3 spread 美日利差 证据=两 fact ref 各带值与单位+各自观测日',
              usjp is not None
              and [r['metric'] if 'metric' in r else r['ref'] for r in usjp['evidence_refs']]
              == ['DFF@2026-11-12', 'JP_POLICY_RATE@2026-09-01']
              and all(r['value'] is not None for r in usjp['evidence_refs']))
        hyig = find(self.claims, claim_type='comparison', subtype='spread',
                    comparison_name='hy_ig_oas_spread')
        check('S3 spread HY−IG=2.31 percentage_point(bp 别名 231.0)'
              '与 Fact 层既成 HY_IG_DIFF=2.31 对账',
              hyig is not None and hyig['value'] == 2.31
              and hyig['unit_aliases'] == {'basis_point': 231.0}
              and self._fact('HY_IG_DIFF')['value'] == 2.31)

    def test_s3_rank(self):
        fam = [(f['metric_id'], f['derived']['week']['pct_change'])
               for f in self.snap['facts']
               if (f.get('derived') or {}).get('week', {}).get('pct_change') is not None
               and f['metric_id'] in ('SPX', 'NDX', 'RUT')]
        fam.sort(key=lambda t: -t[1])
        expect_order = [m for m, _ in fam]
        check(f'S3 rank 独立复算降序={expect_order}(注册表 equity_index 族数据驱动)',
              expect_order == ['NDX', 'SPX', 'RUT'])
        for rank, mid in enumerate(expect_order, start=1):
            c = find(self.claims, claim_type='comparison', subtype='rank',
                     metric_ids=['NDX', 'SPX', 'RUT'])
            hits = [x for x in self.claims if x['claim_type'] == 'comparison'
                    and x['subtype'] == 'rank'
                    and x['derivation']['formula'].startswith(
                        f'周pct_change 降序第{rank}/3({mid}=')]
            check(f'S3 rank {mid}=第{rank}/3 rank_position(rank_key=derived.week.pct_change)',
                  len(hits) == 1 and hits[0]['value'] == rank
                  and hits[0]['unit'] == 'rank_position'
                  and hits[0]['rank_key'] == 'derived.week.pct_change')


# ══ S4 threshold ═══════════════════════════════════════════════════

class TestS4Threshold(BundleBase):
    def test_s4_relations(self):
        cases = [
            ('HY_OAS', 'hy_oas.attention', 'above', 3.0),
            ('HY_OAS', 'hy_oas.warning', 'below', 4.0),
            ('UST_10Y', 'ust_10y.warning', 'above', 4.5),
            ('DXY', 'dxy.weak_bound', 'above', 100.0),
        ]
        for mid, key, rel, tv in cases:
            hits = [x for x in self.claims if x['claim_type'] == 'threshold'
                    and x['metric_id'] == mid and x['threshold_ref']['name'] == key]
            check(f'S4 threshold {key}: relation={rel}(水平 vs {tv} 独立判侧)',
                  len(hits) == 1 and hits[0]['relation'] == rel
                  and hits[0]['threshold_ref']['value'] == tv,
                  f'got={[h.get("relation") for h in hits]}')
            check(f'S4 threshold {key}: threshold_ref.provenance=stable key 指回'
                  f'thresholds-registry(非行号)',
                  len(hits) == 1 and hits[0]['threshold_ref']['provenance']
                  .startswith(f'thresholds-registry:{key}@'))

    def test_s4_since_dates(self):
        """since_date=last_crossing 谓词派生;套件独立扫对照(非回叫)。"""
        store = self.snap['series_store']
        hy = store['HY_OAS']
        for key, tv in (('hy_oas.attention', 3.0), ('hy_oas.warning', 4.0)):
            hits = [x for x in self.claims if x['claim_type'] == 'threshold'
                    and x['threshold_ref']['name'] == key]
            expect = ind_last_crossing(hy['dates'], hy['values'], tv)
            check(f'S4 since_date {key}=独立扫最后穿越 {expect}(持续性=last_crossing)',
                  len(hits) == 1 and hits[0]['since_date'] == expect,
                  f'expect={expect} got={[h.get("since_date") for h in hits]}')
        ust = store['UST_10Y']
        hits = [x for x in self.claims if x['claim_type'] == 'threshold'
                and x['threshold_ref']['name'] == 'ust_10y.warning']
        check('S4 since_date ust_10y.warning=独立扫对照(4.5 线)',
              len(hits) == 1 and hits[0]['since_date']
              == ind_last_crossing(ust['dates'], ust['values'], 4.5))

    def test_s4_honest_edges(self):
        panic = [x for x in self.claims if x['claim_type'] == 'threshold'
                 and x['threshold_ref']['name'] == 'hy_oas.panic'][0]
        check('S4 诚实面: panic(5.0)序列全窗同侧→since=窗首+限界注记(不造穿越日)',
              panic['since_date'] == '2023-11-14'
              and 'since_limited_by_window' in panic['since_note'])
        ig = [x for x in self.claims if x['claim_type'] == 'threshold'
              and x['metric_id'] == 'IG_OAS']
        check('S4 诚实面: IG_OAS 序列不在 store→since=None+series_absent 注记(3 条全同)',
              len(ig) == 3 and all(x['since_date'] is None
                                   and 'series_absent' in x['since_note'] for x in ig))


# ══ S5 threshold_distance ══════════════════════════════════════════

class TestS5Distance(BundleBase):
    def test_s5_distances(self):
        cases = [
            ('HY_OAS', 'hy_oas.attention', 3.0, 0.2, 'above'),
            ('HY_OAS', 'hy_oas.warning', 4.0, 0.8, 'below'),
            ('HY_OAS', 'hy_oas.panic', 5.0, 1.8, 'below'),
            ('UST_10Y', 'ust_10y.warning', 4.5, 0.6, 'above'),
            ('UST_10Y', 'ust_10y.red_line', 5.0, 0.1, 'above'),
            ('DXY', 'dxy.weak_bound', 100.0, 3.41, 'above'),
            ('DXY', 'dxy.strong_bound', 104.0, 0.59, 'below'),
        ]
        for mid, key, tv, dv, side in cases:
            hits = [x for x in self.claims if x['claim_type'] == 'threshold_distance'
                    and x['threshold_ref']['name'] == key]
            lv = self._fact(mid)['value']
            check(f'S5 distance {key}=|{lv}−{tv}|={dv}(独立复算+side={side})',
                  len(hits) == 1 and hits[0]['value'] == dv
                  and hits[0]['value'] == round(abs(lv - tv), 6)
                  and hits[0]['side'] == side,
                  f'got={[h.get("value") for h in hits]}')
        warn = [x for x in self.claims if x['claim_type'] == 'threshold_distance'
                and x['threshold_ref']['name'] == 'hy_oas.warning'][0]
        check('S5 distance hy_oas.warning=0.80 percentage_point(契约§2 示例'
              '「|3.20−4.00|=0.80pp」字面钉)+bp 别名 80.0',
              warn['value'] == 0.8 and warn['unit'] == 'percentage_point'
              and warn['unit_aliases'] == {'basis_point': 80.0})


# ══ S6 observation_lag ═════════════════════════════════════════════

class TestS6Lag(BundleBase):
    def test_s6_lags(self):
        for mid, expect in (('SPX', 1), ('HY_OAS', 2), ('UST_10Y', 2),
                            ('CPI', 44), ('JP_POLICY_RATE', 74)):
            c = find(self.claims, claim_type='observation_lag', metric_id=mid)
            f = self._fact(mid)
            ind = (date.fromisoformat(f['as_of'][:10])
                   - date.fromisoformat(f['observation_date'])).days
            check(f'S6 observation_lag {mid}={expect} 自然日(独立复算 as_of−obs={ind})',
                  c is not None and c['value'] == expect == ind
                  and c['unit'] == 'calendar_day')
        check('S6 observation_lag JP_POLICY_RATE=74 天=契约§4 STALE 行字面'
              '「滞后74天JP利率」钉', True)
        check('S6 observation_lag 全量=快照 fact 数(13 条,逐 fact 一条)',
              sum(1 for c in self.claims if c['claim_type'] == 'observation_lag')
              == len(self.snap['facts']))


# ══ U1 单位代数(律3) ══════════════════════════════════════════════

class TestU1UnitAlgebra(BundleBase):
    def test_u1_pp_bp_exact(self):
        check('U1 pp→bp ×100 精确: 0.80pp→80.0bp / 0.24→24.0 / −0.22→−22.0',
              cf.pp_to_bp(0.8) == 80.0 and cf.pp_to_bp(0.24) == 24.0
              and cf.pp_to_bp(-0.22) == -22.0)
        check('U1 bp→pp ÷100 精确往返: 400→4.0 / 231.0→2.31',
              cf.bp_to_pp(400.0) == 4.0 and cf.bp_to_pp(231.0) == 2.31)
        check('U1 错值对红: (0.80pp,40bp)/(0.80pp,800bp)/(2.31pp,23bp) 均非精确对',
              not cf.is_exact_pp_bp_pair(0.8, 40.0)
              and not cf.is_exact_pp_bp_pair(0.8, 800.0)
              and not cf.is_exact_pp_bp_pair(2.31, 23.0))

    def test_u1_percent_to_pp_refused(self):
        raised = False
        try:
            cf.forbid_percent_to_pp(2.5053)
        except cf.UnitAlgebraError:
            raised = True
        check('U1 percent→pp 无基准拒: SPX 周相对变化 +2.5053% 无 pp 表述(律3)',
              raised)
        check('U1 唯一合法通道=显式基准(水平重述语境)',
              cf.forbid_percent_to_pp(4.5, basis=1.0) == 4.5)

    def test_u1_two_token_same_claim(self):
        warn = [x for x in self.claims if x['claim_type'] == 'threshold'
                and x['threshold_ref']['name'] == 'hy_oas.warning'][0]
        t400 = cf.threshold_token_matches(warn, 400.0, 'bp')
        t400b = cf.threshold_token_matches(warn, 400.0, 'basis_point')
        t4 = cf.threshold_token_matches(warn, 4.00, '%')
        check('U1 「400bp」与「4.00%」两 token 均命中同一 hy_oas.warning claim'
              '(契约律3: 两 token 须映射同一 threshold claim)',
              t400 and t400b and t4 and warn['threshold_ref']['value'] == 4.0)
        check('U1 反例: 40bp/4.05%/4.00 percent-typed 均不命中(错值/裸%不反推'
              'pp 单位/percent 类型排除)',
              not cf.threshold_token_matches(warn, 40.0, 'bp')
              and not cf.threshold_token_matches(warn, 4.05, '%')
              and not cf.threshold_token_matches(warn, 4.00, 'percent'))
        ust = [x for x in self.claims if x['claim_type'] == 'threshold'
               and x['threshold_ref']['name'] == 'ust_10y.warning'][0]
        check('U1 percent 系阈值: 「4.5%」命中而「450bp」不命中(percent 无 bp 代数)'
              '——pp/bp 与 percent 三域分立',
              cf.threshold_token_matches(ust, 4.5, '%')
              and not cf.threshold_token_matches(ust, 450.0, 'bp'))

    def test_u1_cross_unit_spread_refused(self):
        ust, hyo = self._fact('UST_10Y'), self._fact('HY_OAS')
        spec = {'name': 'x', 'left': 'UST_10Y', 'right': 'HY_OAS',
                'subtype': 'spread', 'provenance': '反例'}
        raised = False
        try:
            cf.build_comparison_claim(spec, ust, hyo, self.snap['research_as_of'])
        except cf.UnitAlgebraError as e:
            raised = 'percent' in str(e) and 'percentage_point' in str(e)
        check('U1 跨单位 spread 拒: UST_10Y(percent)−HY_OAS(percentage_point)'
              '→UnitAlgebraError', raised)
        units = {c['unit'] for c in self.claims
                 if c['claim_type'] == 'comparison' and c['subtype'] in ('spread', 'diff')}
        check('U1 bundle 内 spread 证据单位同一(混单位对零入场)',
              all(len({r['unit'] for r in c['evidence_refs']}) == 1
                  for c in self.claims
                  if c['claim_type'] == 'comparison' and c['subtype'] in ('spread', 'diff')))


# ══ P1 谓词(§3 文法) ══════════════════════════════════════════════

class TestP1Predicates(BundleBase):
    def test_p1_percentile_tie_halfweight(self):
        vals = [1.0, 2.0, 2.0, 3.0, 4.0]
        r = cf.percentile_rank(vals, current=2.0)
        exact = ind_percentile(vals, 2.0)
        check(f'P1 percentile 并列半权手算: [1,2,2,3,4] 取2→100×(1+0.5×2)/5={float(exact)}',
              r['strictly_less'] == 1 and r['ties'] == 2
              and r['percentile'] == round(float(exact), 4) == 40.0
              and abs(r['percentile'] - float(exact)) < 1e-9)
        r_all_ties = cf.percentile_rank([5.0] * 30, current=5.0)
        check('P1 percentile 全并列→50.0(并列含当期自身,公式钉死)',
              r_all_ties['percentile'] == 50.0 and r_all_ties['n'] == 30
              and r_all_ties['gate'] == 'OK')

    def test_p1_min_n_gate(self):
        r = cf.percentile_rank([1.0, 2.0, 3.0], current=3.0)
        check('P1 min-n 门: n=3<20→gate=INSUFFICIENT_EVIDENCE(事实性字段仍产出;'
              '分位=100×(2+0.5×1)/3=83.3333)',
              r['gate'] == 'INSUFFICIENT_EVIDENCE'
              and r['percentile'] == round(100 * (2 + 0.5 * 1) / 3, 4) == 83.3333
              and r['n'] == 3)
        spx = self.snap['series_store']['SPX']
        r10 = cf.percentile_rank(spx['values'][:10])
        check('P1 min-n 门(真实序列): SPX 前10观测→INSUFFICIENT_EVIDENCE',
              r10['gate'] == 'INSUFFICIENT_EVIDENCE' and r10['n'] == 10)

    def test_p1_monthly_ytd_forbidden(self):
        cpi = self.snap['series_store']['CPI']
        r = cf.ytd_percentile(cpi['dates'], cpi['values'], frequency='monthly')
        check('P1 月频 ytd 禁用(契约§3 逐字): CPI 月频→refused,零分位产出',
              'refused' in r and 'monthly_ytd_forbidden' in r['refused']
              and 'percentile' not in r)
        led = [p for p in self.bundle['predicate_ledger']
               if p.get('metric_id') == 'CPI']
        check('P1 谓词台账: CPI 条目=refused(与直调一致)', len(led) == 1
              and 'refused' in led[0])

    def test_p1_ytd_window_boundary(self):
        curve = self.snap['series_store']['CURVE_2S10S']
        r = cf.ytd_percentile(curve['dates'], curve['values'], frequency='daily')
        y = int(str(curve['dates'][-1])[:4])
        prior_end = [d for d in curve['dates'] if str(d) < f'{y}-01-01'][-1]
        check(f'P1 ytd 窗界=前一年度末观测含当期: 窗首={prior_end}(2025-12-31)'
              '与 derived.ytd basis 约定一致',
              r['window_first_date'] == prior_end == '2025-12-31')
        exact = ind_percentile(curve['values'][-r['n']:], curve['values'][-1])
        check(f'P1 CURVE ytd 分位={r["percentile"]}(独立 Fraction 复算对照;年内至今)',
              abs(r['percentile'] - float(exact)) < 1e-4 and r['gate'] == 'OK')

    def test_p1_crossing_count_handcount(self):
        hy = self.snap['series_store']['HY_OAS']
        for since in ('2024-01-01', None):
            ind = ind_crossings_since(hy['dates'], hy['values'], 4.0, since) \
                if since else ind_crossings_since(hy['dates'], hy['values'], 4.0,
                                                  hy['dates'][0])
            r = cf.crossing_count(hy['dates'], hy['values'], 4.0, since=since)
            check(f'P1 crossing_count 手数对照: HY_OAS×4.0 since={since}'
                  f'→{ind} 次(独立扫)',
                  r['count'] == ind and r['gate'] == 'OK',
                  f"got={r['count']} expect={ind}")
        r24 = cf.crossing_count(hy['dates'], hy['values'], 4.0, since='2024-01-01')
        check('P1 「2024 年以来第 2 次穿越 4.0 线」=确定性派生(上穿1/下穿1)',
              r24['count'] == 2 and r24['up'] == 1 and r24['down'] == 1)
        thr = [x for x in self.claims if x['claim_type'] == 'threshold'
               and x['threshold_ref']['name'] == 'hy_oas.warning'][0]
        check('P1 threshold claim persistence 携带 crossing_count 全窗结果',
              thr['persistence']['crossing_count_full_window']['count']
              == ind_crossings_since(hy['dates'], hy['values'], 4.0, hy['dates'][0]))
        short = cf.crossing_count(hy['dates'][:15], hy['values'][:15], 4.0)
        check('P1 crossing_count min-n 门: n=15<20→INSUFFICIENT_EVIDENCE',
              short['gate'] == 'INSUFFICIENT_EVIDENCE')

    def test_p1_sign_flip(self):
        curve = self.snap['series_store']['CURVE_2S10S']
        r = cf.sign_flip_date(curve['dates'], curve['values'])
        check('P1 sign_flip_date CURVE_2S10S=2024-09-05(契约§3 字面钉;'
              '最后负值日=「该日之后无倒挂」)',
              r['sign_flip_date'] == '2024-09-05'
              and r['last_opposite_value'] == -0.02
              and r['first_current_side_date'] == '2024-09-06'
              and r['current_side'] == 'above')
        led = [p for p in self.bundle['predicate_ledger']
               if p.get('metric_id') == 'CURVE_2S10S' and p['predicate'] == 'sign_flip_date']
        check('P1 谓词台账携带同值 flip 条目', len(led) == 1
              and led[0]['sign_flip_date'] == '2024-09-05')
        pos = cf.sign_flip_date(['2026-01-01', '2026-01-02'], [1.0, 2.0])
        check('P1 sign_flip 全窗同侧→date=None+注记(不造翻转)', pos['sign_flip_date'] is None)

    def test_p1_and_combine(self):
        curve = self.snap['series_store']['CURVE_2S10S']
        pct = cf.ytd_percentile(curve['dates'], curve['values'], frequency='daily')
        c1 = {'name': 'curve_ytd_low_decile', 'predicate': 'percentile_rank<10',
              'holds': pct['percentile'] < 10}
        flip = cf.sign_flip_date(curve['dates'], curve['values'])
        c2 = {'name': 'curve_no_inversion_since_flip',
              'predicate': 'sign_flip_date is not None',
              'holds': flip['sign_flip_date'] is not None}
        c3 = {'name': 'always_false_component', 'predicate': 'false',
              'holds': False}
        r_true = cf.and_combine(c1, c2)
        r_false = cf.and_combine(c1, c2, c3)
        check('P1 AND 组合: 两真件(年内低位+翻正在案)→holds=True',
              r_true['holds'] is True and r_true['n_components'] == 2)
        check('P1 AND 组合: 注入一假件→holds=False(任一不成立即不成立)',
              r_false['holds'] is False and r_false['n_components'] == 3)
        raised = False
        try:
            cf.and_combine({'name': 'x'})
        except ValueError:
            raised = True
        check('P1 AND 组件形态门: 缺 holds 布尔→拒', raised)


# ══ Z1 零模型调用 ══════════════════════════════════════════════════

FORBIDDEN_TOKENS = ('model_conclusion_client', 'report_generator', 'openai',
                    'requests', 'httpx', 'urllib', 'socket', 'environ',
                    'getenv', 'random', 'subprocess', 'time.time',
                    'datetime.now', 'utcnow')


class TestZ1ZeroModel(BundleBase):
    def test_z1_static(self):
        mods = ['scripts/research_contract/__init__.py',
                'scripts/research_contract/claim_bundle.py',
                'scripts/research_contract/claim_factory.py']
        for m in mods:
            with open(os.path.join(ROOT, m), 'r', encoding='utf-8') as f:
                src = f.read()
            hits = [t for t in FORBIDDEN_TOKENS if t in src]
            check(f'Z1 静态: {m} 零模型客户端/零 env/零网络/零随机/零时钟'
                  f'(违例 token={hits})', hits == [], str(hits))

    def test_z1_dynamic_env_tripwire(self):
        before = set(sys.modules)
        bundle = cf.generate_claims_bundle(self.snap)
        new_mods = {m for m in set(sys.modules) - before
                    if m.split('.')[0] in ('requests', 'openai', 'httpx',
                                           'urllib', 'socket', 'model_conclusion_client')}
        check('Z1 动态: 生成全程零网络/模型模块载入(新增模块交集=空)',
              new_mods == set(), str(sorted(new_mods)[:5]))
        code = (
            "import sys,json;sys.path.insert(0,sys.argv[1]);"
            "from research_contract import claim_factory as cf;"
            "from research_contract import claim_bundle as cb;"
            "print(cb.bundle_to_json(cf.build_from_snapshot_file(sys.argv[2])))"
        )
        env = dict(os.environ)
        env.update({'MODEL_API_KEY': 'TRIPWIRE_T4', 'MODEL_BASE_URL': 'TRIPWIRE_T4',
                    'GLM_API_KEY': 'TRIPWIRE_T4', 'MODEL_PROVIDER': 'TRIPWIRE_T4'})
        proc = subprocess.run([sys.executable, '-c', code,
                               os.path.join(ROOT, 'scripts'), FIXTURE],
                              capture_output=True, text=True, env=env, timeout=120)
        ok = proc.returncode == 0 and proc.stdout.strip() == cb.bundle_to_json(bundle)
        check('Z1 动态: MODEL_* 环境绊线下子进程生成=逐字节同输出(env 未被读取;'
              '跨进程确定性)', ok,
              proc.stderr[-300:] if proc.returncode else 'output differs')


# ══ D1 确定性与 schema 咬合 ════════════════════════════════════════

class TestD1DeterminismSchema(BundleBase):
    def test_d1_determinism(self):
        b2 = cf.generate_claims_bundle(self.snap)
        check('D1 纯函数: 同输入双跑→序列化逐字节相等(零时钟/零随机)',
              cb.bundle_to_json(self.bundle) == cb.bundle_to_json(b2))
        ids = [c['claim_id'] for c in self.claims]
        check('D1 claim_id 唯一且按稳定序编号(CLM-20261114-0001..NNNN)',
              len(ids) == len(set(ids))
              and ids == [f'CLM-20261114-{i:04d}' for i in range(1, len(ids) + 1)])
        fp = self.bundle['registry_fingerprints']
        check('D1 注册表指纹随档(sha256+签字状态;阈值只认注册表的优先级注)',
              len(fp['thresholds']['sha256']) == 64
              and fp['thresholds']['n_entries'] == 69
              and fp['thresholds']['status'].startswith('v1.0-SIGNED')
              and fp['thresholds']['signed_at'] == '2026-11-14'
              and len(fp['metric_registry']['sha256']) == 64
              and isinstance(fp['metric_registry']['version'], str))

    def test_d1_roundtrip(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            p = cb.write_bundle(self.bundle, td)
            check('D1 落盘名=claims_YYYYMMDD.json(快照旁挂;契约§2)',
                  os.path.basename(p) == 'claims_20261114.json')
            back = cb.load_bundle(p)
            check('D1 写读往返=逐字节相等(同一 validator 双过)',
                  cb.bundle_to_json(back) == cb.bundle_to_json(self.bundle))

    def test_d1_schema_mutations(self):
        def must_raise(mutate, label):
            c = copy.deepcopy(find(self.claims, claim_type='level', subtype='point',
                                   metric_id='SPX'))
            mutate(c)
            try:
                cb.validate_claim(c)
                check(f'D1 schema 变异红: {label}', False, '未抛 SchemaError')
            except cb.SchemaError:
                check(f'D1 schema 变异红: {label}', True)
        must_raise(lambda c: c.update(value={'low': 5, 'high': 1}),
                   'level.point 值改区间对象(subtype 不符)')
        band = copy.deepcopy(find(self.claims, claim_type='level', subtype='band',
                                  metric_id='DXY'))
        band['value'] = {'low': 104.0, 'high': 100.0}
        try:
            cb.validate_claim(band)
            check('D1 schema 变异红: level.band low>high', False)
        except cb.SchemaError:
            check('D1 schema 变异红: level.band low>high', True)
        must_raise(lambda c: c.update(claim_type='change', subtype='relative',
                                      window='week', basis_date='2026-11-06',
                                      basis_value=7376.859863, unit='percentage_point'),
                   'change.relative 单位非 percent')
        chg = copy.deepcopy(find(self.claims, claim_type='change', subtype='relative',
                                 metric_id='SPX', window='week'))
        chg.pop('basis_value')
        try:
            cb.validate_claim(chg)
            check('D1 schema 变异红: change 缺 basis_value(律2)', False)
        except cb.SchemaError:
            check('D1 schema 变异红: change 缺 basis_value(律2)', True)
        must_raise(lambda c: c.update(claim_type='observation_lag',
                                      subtype='as_of_minus_observation',
                                      unit='calendar_day', as_of_date='2026-11-14',
                                      value=-1), 'observation_lag 负天数')
        cmp_c = copy.deepcopy(find(self.claims, claim_type='comparison',
                                   subtype='spread', comparison_name='us_jp_rate_spread'))
        cmp_c['metric_id'] = 'DFF'
        try:
            cb.validate_claim(cmp_c)
            check('D1 schema 变异红: comparison 携 metric_id(多成员专用 metric_ids)',
                  False)
        except cb.SchemaError:
            check('D1 schema 变异红: comparison 携 metric_id(多成员专用 metric_ids)',
                  True)
        # R42: HY_OAS 三线(attention/warning/panic)→多匹配;按 relation='above'
        # 判歧取一(T1 落盘前单线时代的老锚,注册表扩线后潜伏 TypeError)。
        thr = copy.deepcopy(find(self.claims, claim_type='threshold',
                                 metric_id='HY_OAS', relation='above'))
        thr['relation'] = 'inside'
        try:
            cb.validate_claim(thr)
            check('D1 schema 变异红: threshold relation 非法词', False)
        except cb.SchemaError:
            check('D1 schema 变异红: threshold relation 非法词', True)
        ev = copy.deepcopy(find(self.claims, claim_type='level', subtype='point',
                                metric_id='SPX'))
        ev['evidence_refs'] = [{'ref': 'SPX@2026-11-13', 'kind': 'snapshot_fact'}]
        try:
            cb.validate_claim(ev)
            check('D1 schema 变异红: evidence ref 缺值(引用必带值=契约§2)', False)
        except cb.SchemaError:
            check('D1 schema 变异红: evidence ref 缺值(引用必带值=契约§2)', True)
        try:
            cb.make_bundle(snapshot_id='x', target_date='20261114',
                           research_as_of='r', claims=[self.claims[0], self.claims[0]],
                           coverage_ledger=[], predicate_ledger=[],
                           registry_fingerprints={})
            check('D1 schema 变异红: claim_id 重复', False)
        except cb.SchemaError:
            check('D1 schema 变异红: claim_id 重复', True)

    def test_d1_honest_absence(self):
        led = self.bundle['coverage_ledger']
        for mid in ('SPX', 'CPI', 'DFF', 'JP_POLICY_RATE'):
            check(f'D1 诚实缺席: {mid} 无注册表条目→ledger 记 no_threshold_entries',
                  any(e.get('metric_id') == mid
                      and 'no_threshold_entries' in e['reason'] for e in led))
        for t in ('threshold', 'threshold_distance'):
            got = [c for c in self.claims if c['claim_type'] == t
                   and c.get('metric_id') in ('SPX', 'CPI', 'DFF', 'JP_POLICY_RATE')]
            check(f'D1 诚实缺席: SPX/CPI/DFF/JP 零 {t} claim(不造阈值)', got == [])
        check('D1 覆盖面如实申报: 69 键注册表对快照 13 指标,缺席逐条入账',
              len([e for e in led if e['scope'] == 'threshold']) == 9)

    def test_d1_fixture_provenance(self):
        prov = self.snap.get('_fixture_provenance', {})
        check('D1 fixture 出处注记: 源快照 id+两源档 sha256+提取日(2026-11-14)',
              prov.get('primary_source', {}).get('snapshot_id')
              == 'research_snapshot_20261114_v2'
              and len(prov.get('primary_source', {}).get('sha256', '')) == 64
              and len(prov.get('series_secondary_source', {}).get('sha256', '')) == 64
              and prov.get('extraction_date') == '2026-11-14')
        n_fact = len(self.snap['facts'])
        check(f'D1 体积克制: 垂直切片 facts={n_fact}(13 指标)+series 6 键'
              '(HY_OAS 全史 785/CURVE 自2024/其余尾窗),非全档复制',
              n_fact == 13 and len(self.snap['series_store']) == 6
              and len(self.snap['series_store']['HY_OAS']['dates']) == 785)


def main():
    print('══ 架构整改 T4 回归套件(claim_factory 六型+claim_bundle)══')
    case_errs = 0
    for cls in (TestS1Level, TestS2Change, TestS3Comparison, TestS4Threshold,
                TestS5Distance, TestS6Lag, TestU1UnitAlgebra, TestP1Predicates,
                TestZ1ZeroModel, TestD1DeterminismSchema):
        print(f'── {cls.__name__} ──')
        case_errs += _run_case(cls)
    total, bad = len(PASSED) + len(FAILED), len(FAILED)
    print(f"\n{'='*60}\nT4 回归: {len(PASSED)} PASS / {len(FAILED)} FAIL (共{total}判定)")
    if FAILED or case_errs:
        for n, d in FAILED:
            print(f"  ❌ {n} [{d}]")
        if case_errs:
            print(f'  ❌ 测级异常×{case_errs}(unittest errors/failures,见上方逐类行)')
        sys.exit(1)
    print('全部通过 ✅')
    sys.exit(0)


if __name__ == '__main__':
    main()
