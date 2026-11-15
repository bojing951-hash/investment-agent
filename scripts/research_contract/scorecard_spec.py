# -*- coding: utf-8 -*-
"""评分卡维度规格(单源规格表;T8-R2 遗留③收口,RDG-20261116-011)。

消费方(两侧同源,禁平行枚举):
  - scripts/macro_scorecard.py                评分引擎(阈值键全集由此推导)
  - scripts/research_contract/text_consistency.py  契约侧总分复算
    (_check_score_total 按 SCORECARD_THRESHOLD_KEYS 断言键在场)

行结构(纯数据;本模块零 import——连 typing 都不用,契约纯度律内):
  (metric_id, source, band, keys)
  source: ('level',)                 → fact['value']
          (period, field)            → fact['derived'][period][field]
                                     (引擎统一口径 m1/m3/m12;pct/pp 按单位)
  band:   'std' = 四键升序同构带链(左开右闭: <k0→-2 … ≥k3→+2)
          'rev' = 反向带链(失业率 3 月: 升=负分;键序 p05,p03,m01,m03)
  keys:   4 个签字阈值 stable_key(值唯一权威=config/thresholds.json,
          金融席签字;本表只声明结构,不持有数值)

新增评分卡指标: 本表加一行 + config/thresholds.json 补签字键(重走金融席
签字+G2 对账门),两消费面自动生效——不再双处改控制流。

体制映射键(消费方 determine_regime / _check_score_total 体制段共用):
"""
REGIME_THRESHOLD_KEYS = (
    'regime.inflation_total.stagflation_floor',
    'regime.growth_total.zero',
)

# (维度名, ((metric, source, band, keys), ...))
SCORECARD_DIMENSIONS = (
    ('通胀', (
        ('CORE_CPI', ('m12', 'pct_change'), 'std',
         ('core_cpi.scorecard.m1', 'core_cpi.scorecard.m2',
          'core_cpi.scorecard.p25', 'core_cpi.scorecard.p35')),
        ('BEI_10Y', ('level',), 'std',
         ('bei_10y.scorecard.m15', 'bei_10y.scorecard.m2',
          'bei_10y.scorecard.p23', 'bei_10y.scorecard.p26')),
        ('WTI_F', ('level',), 'std',
         ('wti_f.scorecard.m40', 'wti_f.scorecard.m50',
          'wti_f.scorecard.p70', 'wti_f.scorecard.p90')),
        ('AHE', ('m12', 'pct_change'), 'std',
         ('ahe.scorecard.m2', 'ahe.scorecard.m3',
          'ahe.scorecard.p35', 'ahe.scorecard.p45')),
    )),
    ('增长', (
        ('UMCSENT', ('level',), 'std',
         ('umcsent.scorecard.m50', 'umcsent.scorecard.m60',
          'umcsent.scorecard.p80', 'umcsent.scorecard.p95')),
        ('UNEMPLOYMENT', ('m3', 'pp_change'), 'rev',
         ('unemployment_3m.scorecard.p05', 'unemployment_3m.scorecard.p03',
          'unemployment_3m.scorecard.m01', 'unemployment_3m.scorecard.m03')),
        ('RSAFS', ('m1', 'pct_change'), 'std',
         ('rsafs_mom.scorecard.m1', 'rsafs_mom.scorecard.m05',
          'rsafs_mom.scorecard.p05', 'rsafs_mom.scorecard.p1')),
        ('INDPRO', ('m1', 'pct_change'), 'std',
         ('indpro_mom.scorecard.m1', 'indpro_mom.scorecard.m03',
          'indpro_mom.scorecard.p03', 'indpro_mom.scorecard.p1')),
    )),
)

# 宏评分卡引擎另消费的显示串阈值键(非维度成员;headline 警戒显示用)
EXTRA_ENGINE_KEYS = ('bei_10y.headline_high',)


def dimension_rows():
    """迭代 (维度名, 行)——供复算/对账遍历。"""
    for dim, rows in SCORECARD_DIMENSIONS:
        for row in rows:
            yield dim, row


def threshold_keys():
    """维度键全集(去重保序);不含 REGIME/EXTRA(调用方按需并集)。"""
    seen = set()
    out = []
    for _, (_, _, _, keys) in dimension_rows():
        for k in keys:
            if k not in seen:
                seen.add(k)
                out.append(k)
    return tuple(out)


def spec_version_note():
    return ('scorecard_spec 单源 v1(R41): 8 指标×4 键+2 维度;'
            '键值权威=config/thresholds.json(签字)')
