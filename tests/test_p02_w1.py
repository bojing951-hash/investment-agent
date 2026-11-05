#!/usr/bin/env python3
"""IA-P0-2-W1 专项测试 — 指标身份/金融语义一致性(注册表81项+修复+拦截+事实回归)

覆盖(IA-P0-2-W1-DEV §八):
  A 现有注册表: 81唯一ID/active与core计数/三项修复/全量通过新验证/审计清单覆盖/镜像集合同步
  B 人为注入非法配置: 8类——逐项断言问题定位到实际metric_id+rule+字段(非"清单非空")
  C 合法正向配置: 真实注册表代表性条目全原型通过
  D 事实构建回归: make_fact/normalize_global身份传递、数值/观测日不变、
    非法collector不因identity修复获得授权、Gate A权威集合不变
  E 测试敏感性: 真实文件回退一项个股→etf,生产加载路径load_registry必须抛
    RegistrySemanticsError(非仅validate子程序报问题)
全程离线: 零网络、零真实GLM、零生产数据;fixture为SYNTHETIC。
"""
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

PASS, FAIL = 0, 0

def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")

def expect_errors(probs, mid, rule, field=None, msg_sub=None):
    """problems中存在metric_id==mid且rule==rule(可含field/消息子串)的error项。"""
    for p in probs:
        if p['severity'] != 'error' or p['metric_id'] != mid or p['rule'] != rule:
            continue
        if field is not None and p.get('field') != field:
            continue
        if msg_sub is not None and msg_sub not in p.get('message', ''):
            continue
        return p
    return None


print("=" * 64)
print("P0-2 W1: 指标身份与金融语义一致性")
print("=" * 64)

import fact_engine as fe
import registry_semantics as rsem
import research_provenance as rp
import trading_calendar as tc
from helpers import baseline_locks as bl   # WP-BR三联锁(vintage域)

REG_PATH = os.path.join(ROOT, 'config', 'metric_registry.json')
with open(REG_PATH, encoding='utf-8') as f:
    _REG = json.load(f)

def mutate(fn):
    """深拷贝真实注册表→注入突变→返回validate问题清单(不触生产文件/缓存)。"""
    reg = json.loads(json.dumps(_REG))
    fn(reg)
    return rsem.validate_registry(reg)

by_id = {m['metric_id']: m for m in _REG['metrics']}

# ══ A. 现有注册表 ═════════════════════════════════════════════════
print("\n[A] 现有注册表")
# WP-BR三联锁(#47/#48): 字面81/80/32→T1冻结下限(≥81/≥80/≥32,防缩水)
# +T2实载派生(双射唯一,弃字面常量;合法演进81→85不撞墙)
_ok_a1, _why_a1 = bl.registry_counts_ok(_REG)
_ok_a1u, _why_a1u = bl.ids_unique_bijection_ok(_REG)
check("A1 唯一metric_id集≥81+metrics/by_id双射(T1下限+T2派生)",
      _ok_a1 and _ok_a1u and len(by_id) == len(_REG['metrics']),
      f"got {len(_REG['metrics'])}/{len(by_id)} {_why_a1};{_why_a1u}")
n_active = sum(1 for m in _REG['metrics'] if m.get('status') == 'active')
n_core = sum(1 for m in _REG['metrics'] if m.get('status') == 'active' and m.get('criticality') == 'core')
check("A2 active≥80 / active+core≥32(T1冻结下限,非预期缩水即红)",
      n_active >= bl.ACTIVE_FLOOR and n_core >= bl.CORE_FLOOR,
      f"got active={n_active} core={n_core}")
for mid in ('NVDA', 'AAPL', 'MSFT'):
    m = by_id[mid]
    check(f"A3 {mid}身份修复: single_stock类+instrument=single_stock",
          m['asset_class'] == 'single_stock'
          and m.get('identity', {}).get('instrument') == 'single_stock',
          str(m.get('identity')))
probs_all = rsem.validate_registry(_REG)
errs_all = [p for p in probs_all if p['severity'] == 'error']
revs_all = [p for p in probs_all if p['severity'] == 'review']
check("A4 现有完整注册表通过新验证(0 error)", len(errs_all) == 0, str(errs_all[:3]))
check("A4b 机器review级=0(DXY口径待核为**审计级**REVIEW——机器无规则可判,不伪装成已认证也不误报)",
      len(revs_all) == 0, str(revs_all))
# 审计清单覆盖
with open(os.path.join(ROOT, 'docs', 'P0_2_W1_REGISTRY_AUDIT.json'), encoding='utf-8') as f:
    audit = json.load(f)
aud_ids = [i['metric_id'] for i in audit['items']]
# WP-BR三联锁(#49): 审计工件恰覆盖注册表∩vintage锚(基线81项)——
# 漏项/私货/重复/基线条目被删由唯一+全等+下限三面捕获;演进新增不回溯补录
_ok_a5, _why_a5 = bl.artifact_covers_vintage_baseline(aud_ids)
check("A5 审计报告恰覆盖注册表∩vintage基线(≥81,不重复不遗漏)",
      _ok_a5, _why_a5)
check("A5b 审计分类计数一致(FIX1修订后: 76 VERIFIED/4 FIXED/1 REVIEW/0 BLOCKED;"
      "CORE_PCE基期经官方来源证伪由VERIFIED改判FIXED,总数与逐项重算一致性另由"
      "test_p02_w1_fix1 E3/E4锁定)",
      audit['totals']['results'] == {'VERIFIED_CONSISTENT': 76, 'FIXED': 4,
                                     'REVIEW': 1, 'BLOCKED': 0},
      str(audit['totals']['results']))
# 镜像集合同步(防两处漂移)
check("A6a KNOWN_UNITS == fact_engine单位纪律三集合之并",
      rsem.KNOWN_UNITS == frozenset(fe.PRICE_LIKE_UNITS | fe.RATE_UNITS | fe.COUNT_UNITS))
check("A6b KNOWN_CALENDARS == trading_calendar.MARKETS",
      rsem.KNOWN_CALENDARS == frozenset(tc.MARKETS))
check("A6c KNOWN_SOURCES == rp授权采集器键+deprecated遗留",
      rsem.KNOWN_SOURCES == frozenset(rp._AUTHORIZED_COLLECTORS) | {'macro_collector(derived)'})

# ══ B. 人为注入非法配置(逐项定位metric_id+rule) ═══════════════════
print("\n[B] 非法配置注入(必须可解释地失败)")
def revert_stock(mid):
    def _f(reg):
        for m in reg['metrics']:
            if m['metric_id'] == mid:
                m['identity']['instrument'] = 'etf'
    return _f
for mid in ('NVDA', 'AAPL', 'MSFT'):
    p = mutate(revert_stock(mid))
    hit = expect_errors(p, mid, 'R-STOCK-NOT-ETF', 'identity.instrument')
    check(f"B1-B3 {mid}回退为etf→R-STOCK-NOT-ETF点名", hit is not None, str([x for x in p if x['metric_id'] == mid]))
    check(f"B1-B3b {mid}同时触发R-ETF-EXCLUSIVITY+R-INSTRUMENT-CLASS(多重独立规则)",
          expect_errors(p, mid, 'R-ETF-EXCLUSIVITY') is not None
          and expect_errors(p, mid, 'R-INSTRUMENT-CLASS') is not None)
p = mutate(lambda reg: [m.update({'identity': {**m.get('identity', {}), 'instrument': 'single_stock'}})
                        for m in reg['metrics'] if m['metric_id'] == 'SPX'][0])
hit = expect_errors(p, 'SPX', 'R-INSTRUMENT-CLASS', 'identity.instrument')
check("B4 equity_index(SPX)伪装为个股身份→R-INSTRUMENT-CLASS", hit is not None,
      str([x for x in p if x['metric_id'] == 'SPX']))
check("B4b SPX不触发ETF专属规则(问题类别区分)", expect_errors(p, 'SPX', 'R-ETF-EXCLUSIVITY') is None
      and expect_errors(p, 'SPX', 'R-STOCK-NOT-ETF') is None)
p = mutate(lambda reg: [m.update({'unit': 'persons'}) for m in reg['metrics'] if m['metric_id'] == 'UST_10Y'][0])
hit = expect_errors(p, 'UST_10Y', 'R-UNIT-DIMENSION', 'unit')
check("B5 已知利率指标改不兼容单位(persons)→R-UNIT-DIMENSION", hit is not None,
      str([x for x in p if x['metric_id'] == 'UST_10Y']))
p = mutate(lambda reg: [m.update({'source': 'wsj_collector'}) for m in reg['metrics'] if m['metric_id'] == 'GOLD_F'][0])
hit = expect_errors(p, 'GOLD_F', 'R-SOURCE-ENUM', 'source')
check("B6 已知指标改成无法解释的来源→R-SOURCE-ENUM", hit is not None,
      str([x for x in p if x['metric_id'] == 'GOLD_F']))
def dup(reg):
    import copy as _c
    reg['metrics'].append(_c.deepcopy(reg['metrics'][0]))
p = mutate(dup)
hit = expect_errors(p, _REG['metrics'][0]['metric_id'], 'R-ID-DUP')
check("B7 重复metric_id→R-ID-DUP点名", hit is not None, str([x for x in p if x['rule'] == 'R-ID-DUP']))
p = mutate(lambda reg: [m.update({'unit': 123}) for m in reg['metrics'] if m['metric_id'] == 'TLT'][0])
check("B8a unit非法类型(int)→R-FIELD-STR", expect_errors(p, 'TLT', 'R-FIELD-STR', 'unit') is not None)
p = mutate(lambda reg: [m.update({'identity': []}) for m in reg['metrics'] if m['metric_id'] == 'TLT'][0])
check("B8b identity非法类型(list)→R-IDENTITY-TYPE", expect_errors(p, 'TLT', 'R-IDENTITY-TYPE') is not None)
p = mutate(lambda reg: [m.update({'identity': {**m.get('identity', {}), 'instrument': 7}})
                        for m in reg['metrics'] if m['metric_id'] == 'TLT'][0])
check("B8c instrument非法类型(int)→R-INSTRUMENT-TYPE", expect_errors(p, 'TLT', 'R-INSTRUMENT-TYPE') is not None)
p = mutate(lambda reg: [m.update({'freshness': 'weekly'}) for m in reg['metrics'] if m['metric_id'] == 'CPI'][0])
check("B8d freshness非法结构(str)→R-FRESHNESS-TYPE", expect_errors(p, 'CPI', 'R-FRESHNESS-TYPE') is not None)
p = mutate(lambda reg: [m.update({'identity': {'is_proxy': True, 'proxy_of': '   '}})
                        for m in reg['metrics'] if m['metric_id'] == 'EURUSD'][0])
check("B8e is_proxy=true而proxy_of空白→R-PROXY-TARGET", expect_errors(p, 'EURUSD', 'R-PROXY-TARGET') is not None,
      str([x for x in p if x['metric_id'] == 'EURUSD']))
# REVIEW通路:未确认组合只诊断不拦截(未确认≠非法,不编造枚举也不放行成"已认证")
p = mutate(lambda reg: [m.update({'asset_class': 'exotic_derivative'}) for m in reg['metrics'] if m['metric_id'] == 'BTC'][0])
rv = [x for x in p if x.get('severity') == 'review' and x['metric_id'] == 'BTC']
check("B9 未确认asset_class→review级(类别+组合双诊断,不进error不拦截)",
      rv and all(x['rule'] in ('R-ASSETCLASS-UNCONFIRMED', 'R-COMBINATION-UNCONFIRMED') for x in rv)
      and any(x['rule'] == 'R-ASSETCLASS-UNCONFIRMED' for x in rv)
      and not [x for x in p if x['severity'] == 'error' and x['metric_id'] == 'BTC'],
      str(rv))

# ══ C. 合法正向配置(真实注册表代表性原型) ═════════════════════════
print("\n[C] 合法正向配置(全原型)")
ARCHETYPES = ['NVDA', 'TLT', 'GLD', 'EEM', 'USO', 'SPX', 'VIX', 'HSI', 'GOLD_F',
              'ZQ_F1_PRICE', 'ZQ_IMPLIED_AVG', 'BTC', 'EURUSD', 'USDJPY', 'USDCNY', 'DXY',
              'UST_10Y', 'BEI_10Y', 'CURVE_2S10S', 'HY_OAS', 'HY_IG_DIFF', 'TIPS_10Y',
              'REAL_10Y', 'REAL_5Y', 'FED_FUNDS', 'DFF', 'DFEDTARU', 'DFEDTARL',
              'CPI', 'CORE_CPI', 'CORE_PCE', 'NFP', 'NFP_MOM_K', 'AHE', 'ICSA', 'JTSJOL',
              'WTI_SPOT_M', 'UMCSENT', 'RSAFS', 'INDPRO', 'UNEMPLOYMENT',
              'SHCOMP', 'SZCI', 'CHINEXT', 'HSCEI', 'HSAHP',
              'SB_FLOW', 'MARGIN_BAL', 'SH_PE', 'SH_AMOUNT', 'SZ_COMPONENT_AMOUNT',
              'CN_TOTAL_TURNOVER', 'REAL_SHORT']
sub = {'version': _REG.get('version'), 'metrics': [by_id[mid] for mid in ARCHETYPES]}
sub_probs = rsem.validate_registry(sub)
check(f"C1 {len(ARCHETYPES)}个真实原型条目(含deprecated)全部0 error",
      not [p for p in sub_probs if p['severity'] == 'error'], str(sub_probs[:3]))
check("C2 原型集合覆盖全部asset_class(29类)",
      {by_id[m]['asset_class'] for m in ARCHETYPES} == {m['asset_class'] for m in _REG['metrics']})
check("C3 修复后个股原型identity含single_stock且保留adjustment口径",
      by_id['NVDA']['identity'] == {'instrument': 'single_stock',
                                    'adjustment': 'auto_adjust(分红复权,近似全收益,非交易所裸价)'},
      str(by_id['NVDA']['identity']))

# ══ D. 事实构建回归 ═══════════════════════════════════════════════
print("\n[D] 事实构建回归(make_fact/normalize/来源授权)")
AS_OF = "2026-10-25T08:00:00+08:00"
f1 = fe.make_fact('NVDA', 140.5, '2026-10-24', AS_OF, 'global_20261025.json',
                  'global_market_collector')
check("D1 make_fact输出修复后identity(逐键复制注册表)",
      f1['identity'] == by_id['NVDA']['identity'] and f1['identity']['instrument'] == 'single_stock',
      str(f1.get('identity')))
check("D2 原始数值/观测日不变,单位/类型沿注册表",
      f1['value'] == 140.5 and f1['observation_date'] == '2026-10-24'
      and f1['unit'] == 'usd' and f1['value_type'] == 'level')
gf = fe.normalize_global({'data': {'NVDA': {'close': 140.5, 'date': '2026-10-24'}}}, AS_OF,
                         'global_20261025.json')
check("D3 normalize_global真实规范化路径同身份(single_stock)",
      gf and gf[0]['identity'].get('instrument') == 'single_stock' and gf[0]['value'] == 140.5,
      str(gf and gf[0].get('identity')))
check("D3b 事实纪律兼容:quality_status在场/来源链完整",
      gf[0]['quality_status'] == 'PASS' and gf[0]['source']['collector'] == 'global_market_collector')
# 非法collector不因identity修复获得授权(rp既有授权链)
f2 = fe.make_fact('NVDA', 140.5, '2026-10-24', AS_OF, 'global_20261025.json', 'shadow_module')
src_probs = rp.fact_source_problems(f2, by_id['NVDA'],
                                    {'status': 'EXACT', 'file': 'global_20261025.json'},
                                    {'NVDA': f2})
check("D4 非法collector仍被rp拒绝(identity修复不授予来源授权)",
      any('collector' in p for p in src_probs), str(src_probs))
f3 = fe.make_fact('NVDA', 140.5, '2026-10-24', AS_OF, 'global_20261025.json',
                  'global_market_collector')
src_probs2 = rp.fact_source_problems(f3, by_id['NVDA'],
                                     {'status': 'EXACT', 'file': 'global_20261025.json'},
                                     {'NVDA': f3})
check("D5 合法collector+批次经rp零问题(修复不破坏既有授权)", src_probs2 == [], str(src_probs2))
_core_ids_d6 = rp.core_metric_ids()
check("D6 Gate A权威集合下限保持(core≥32含SPX/UST_10Y;active≥80;T1)",
      len(_core_ids_d6) >= bl.CORE_FLOOR and 'SPX' in _core_ids_d6
      and 'UST_10Y' in _core_ids_d6
      and len(rp.active_registry_metrics()) >= bl.ACTIVE_FLOOR)
g = fe.snapshot_quality_grade(gf)
check("D7 快照分级行为保持(注册表active事实计数口径)", g['overall'] == 'PASS'
      and 'NVDA' not in g['missing_core'], str(g))
unk = fe.normalize_global({'data': {'FAKE_X': {'close': 1.0, 'date': '2026-10-24'}}}, AS_OF)
check("D8 未注册资产仍FAIL(identity)——既有边界不因新模块削弱",
      unk[0]['quality_status'] == 'FAIL' and any(i['category'] == 'identity' for i in unk[0]['issues']))

# ══ E. 测试敏感性(生产加载路径) ═══════════════════════════════════
print("\n[E] 敏感性: 真实文件回退一项→生产load_registry必须fail-loud")
tmpd = tempfile.mkdtemp(prefix='w1-sens-')
try:
    bad = json.loads(json.dumps(_REG))
    for m in bad['metrics']:
        if m['metric_id'] == 'AAPL':
            m['identity']['instrument'] = 'etf'
    bad_path = os.path.join(tmpd, 'registry_bad.json')
    with open(bad_path, 'w', encoding='utf-8') as f:
        json.dump(bad, f, ensure_ascii=False)
    raised, msg = None, ''
    try:
        fe.load_registry(bad_path, force=True)
    except rsem.RegistrySemanticsError as e:
        raised, msg = True, str(e)
    except Exception as e:  # 其他异常类型=拦截形态错误
        raised, msg = 'wrong-type', f'{type(e).__name__}: {e}'
    check("E1 回退AAPL→etf后load_registry抛RegistrySemanticsError",
          raised is True, msg[:200])
    check("E2 异常消息点名AAPL与规则R-STOCK-NOT-ETF(可解释失败)",
          'AAPL' in msg and 'R-STOCK-NOT-ETF' in msg, msg[:200])
    check("E3 异常消息含字段路径与修复方向说明",
          'identity.instrument' in msg and 'single_stock' in msg, msg[:200])
finally:
    shutil.rmtree(tmpd, ignore_errors=True)
fe.load_registry(force=True)  # 恢复默认注册表缓存,不影响后续调用方
check("E4 恢复后默认注册表可正常加载(by_id≥81/core≥32;T1下限)",
      len(fe.load_registry()['by_id']) >= bl.REGISTRY_FLOOR
      and len(rp.core_metric_ids()) >= bl.CORE_FLOOR)
check("E5 非法配置不污染缓存:metric('AAPL')仍为修复后身份",
      fe.metric('AAPL')['identity']['instrument'] == 'single_stock')

print("\n" + "=" * 64)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 64)
sys.exit(0 if FAIL == 0 else 1)
