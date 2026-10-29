#!/usr/bin/env python3
"""IA-P0-2-W2 专项测试 — 数据时效规则一致性(统一策略/三问分离/Gate A-B一致)

覆盖(IA-P0-2-W2-DEV §八):
  A 81项规则完整性: 政策矩阵覆盖全部指标且生效值=注册表现值(无静默宽松回退);
    锚点族完整回环(sb.build_anchors真实输出↔canonical映射逐键锁定)
  B 注册表配置实际驱动判定: 改窗→真实validate_fact边界移动(非字符串比较)
  C 月频发布滞后场景: 未发布/已发布旧一期/长期未更新/连缺多期/
    已知发布晚于as_of/发布未知(不得伪造)
  D Gate A/B一致性: 10项强制指标×正常+过期, fp.assess/validate_fact/
    is_fresh_anchor三路同判
  E 身份伪装拒绝: 宽窗指标身份冒充/未映射键冒充/子串伪装——canonical为准
  F 非法输入: 缺观测/非法日期/未来观测/未注册/非法release/缺失或非法窗口
  G 正式研究链: 正常日PASS/合法DEGRADED披露/严重异常FAIL传导/
    Gate B宽不重开Gate A/过期证据不进观察(复用P0-1 fixture构造器)
  H 敏感性: 人工改窗双向被检出/篡改锚点身份→正式批次核验拒绝
全程离线: 零网络/零真实GLM/零生产数据;fixture为SYNTHETIC;隔离临时目录。
"""
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
sys.path.insert(0, os.path.join(ROOT, 'tests'))

PASS, FAIL = 0, 0

def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")

print("=" * 64)
print("P0-2 W2: 数据时效规则一致性")
print("=" * 64)

import fact_engine as fe
import freshness_policy as fp
import data_validator as dv
import snapshot_builder as sb
import research_provenance as rp
import allocation_engine as ae
import fixt

REG_PATH = os.path.join(ROOT, 'config', 'metric_registry.json')
with open(REG_PATH, encoding='utf-8') as f:
    _REG = json.load(f)
_BY = {m['metric_id']: m for m in _REG['metrics']}
AS_OF = '2026-10-24'
AS_OF_ISO = '2026-10-24T08:00:00+08:00'
DAY = '20261024'


def lag_days(n):
    from datetime import date, timedelta
    return (date.fromisoformat(AS_OF) - timedelta(days=n)).isoformat()


def fact_freq_issues(mid, value, obs, collector):
    """真实路径: make_fact→validate_fact,返回frequency/freshness_policy类issues。"""
    m = fe.metric(mid)
    f = fe.make_fact(mid, value, obs, AS_OF_ISO, 'w2_test.json', collector)
    iss = fe.validate_fact(f, {'value': value}, m, as_of_date=AS_OF)
    return [i for i in iss if i['category'] in ('frequency', 'freshness_policy')], f


def load_temp_registry(mutate_fn):
    """深拷贝生产注册表→突变→写入临时文件→经生产加载路径加载(污染缓存,调用方须恢复)。"""
    reg = json.loads(json.dumps(_REG))
    mutate_fn(reg)
    p = os.path.join(_TMPD, 'registry_mut.json')
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(reg, f, ensure_ascii=False)
    return fe.load_registry(p, force=True)


_TMPD = tempfile.mkdtemp(prefix='w2-test-')

# ══ A. 81项规则完整性 ═════════════════════════════════════════════
print("\n[A] 81项规则完整性(政策矩阵+锚点族回环)")
with open(os.path.join(ROOT, 'docs', 'P0_2_W2_FRESHNESS.json'), encoding='utf-8') as f:
    MAT = json.load(f)
items = MAT['items']
mat_by = {i['metric_id']: i for i in items}
check("A1 矩阵覆盖全部81项且与注册表一一对应",
      len(items) == 81 and set(mat_by) == set(_BY) and len(mat_by) == 81)
REQ_FIELDS = ('metric_id', 'source', 'frequency', 'calendar', 'observation_date_semantics',
              'release_date_availability', 'retrieved_at_as_of_usage', 'windows',
              'conflict_pre_w2', 'policy_status', 'approval_basis', 'gate_a_impact',
              'gate_b_impact', 'production_impact')
check("A2 每项含§5.2全部必备字段(无占位省略)",
      all(all(k in i for k in REQ_FIELDS) for i in items),
      str([i['metric_id'] for i in items if not all(k in i for k in REQ_FIELDS)][:3]))
check("A3 生效窗口=注册表现值逐项一致(无静默回退/无矩阵自说自话)",
      all(i['windows']['effective_now'] == _BY[i['metric_id']]['freshness']['max_calendar_lag_days']
          for i in items))
eng_leg = {'daily': 7, 'weekly': 16, 'monthly': 92}
check("A4 对照字段如实: 改前引擎=7/16/92硬编码,矩阵记录的是历史值非现值",
      all(i['windows']['engine_legacy_effective_pre_w2'] == eng_leg[i['frequency']] for i in items))
tot = MAT['totals']
recount = {}
for i in items:
    recount[i['policy_status']] = recount.get(i['policy_status'], 0) + 1
check("A5 分类计数与逐项重算一致(总数由items推导)", tot['by_policy_status'] == recount,
      f"{tot['by_policy_status']} vs {recount}")
check("A6a 审批记录三轮在场(第一轮批准+第二轮修正算术错误+FIX1第三轮DFEDTAR复决策)",
      len(MAT['approval']['rounds']) == 3 and '45→60' in MAT['approval']['rounds'][1]['decisions'][0]
      and '45→10' in MAT['approval']['rounds'][2]['decisions'][0])
FOCUS = ['BTC', 'SPX', 'DFF', 'DFEDTARU', 'DFEDTARL', 'CPI', 'CORE_PCE', 'UNEMPLOYMENT',
         'NFP', 'ICSA', 'SH_PE', 'UST_10Y', 'ZQ_F1_PRICE', 'SHCOMP', 'MARGIN_BAL']
check("A6b 指令§5.2强制15项焦点指标全部在场",
      all(m in mat_by for m in FOCUS), str([m for m in FOCUS if m not in mat_by]))
# W2-FIX1-04(用户第三轮批复2026-10-29): DFEDTARU/L 45→10(FRED官方Daily,7-Day
# 逐日发布当日生效值;45窗仅掩盖采集中断)。原预期45已被批准修订取代;
# 新预期=注册表驱动10天,与P0_2_W2_FIX1_POLICY_DFEDTARL.md/APPROVAL_EVIDENCE §5一致。
check("A7 已批准窗口关键值在场: BTC=2/月频=60/大陆=10/DFEDTAR=10(FIX1第三轮)/行情=5",
      mat_by['BTC']['windows']['effective_now'] == 2
      and all(mat_by[m]['windows']['effective_now'] == 60 for m in FOCUS if mat_by[m]['frequency'] == 'monthly')
      and mat_by['SHCOMP']['windows']['effective_now'] == 10
      and mat_by['DFEDTARU']['windows']['effective_now'] == 10
      and mat_by['SPX']['windows']['effective_now'] == 5)

# 锚点族完整回环: 真实sb.build_anchors输出 ↔ canonical映射逐键锁定
facts = []
_AS = [(mid, v) for mid, v in [
    ('SPX', 7659.44), ('GOLD_F', 4300.0), ('BTC', 108000.0), ('NVDA', 189.5),
    ('SHCOMP', 3716.28), ('HSI', 24186.83), ('HSAHP', 128.56), ('SH_AMOUNT', 8000.0),
    ('SZ_COMPONENT_AMOUNT', 9000.0), ('CN_TOTAL_TURNOVER', 17000.0), ('SB_FLOW', 551.87),
    ('MARGIN_BAL', 24026.63), ('SH_PE', 16.4), ('CPI', 310.0), ('TIPS_10Y', 2.31),
    ('UST_10Y', 4.28), ('ICSA', 221000.0), ('UNEMPLOYMENT', 4.2), ('UMCSENT', 68.0),
    ('INDPRO', 103.95), ('REAL_10Y', 1.97), ('ZQ_IMPLIED_AVG', 4.2), ('DFF', 4.33),
    ('DFEDTARU', 4.5), ('DFEDTARL', 4.25)]]
for mid, v in _AS:
    facts.append(fe.make_fact(mid, v, lag_days(1), AS_OF_ISO, 'w2_test.json', 'test'))
snap = {'snapshot_id': 'research_snapshot_' + DAY, 'facts': [f for f in facts if f],
        'fed_futures_curve': [{'price': 95.8, 'implied_avg_rate': 4.2}]}
anchors = sb.build_anchors(snap, DAY)
check("A8 真实build_anchors产出锚点(各族在场)",
      len(anchors) > 20 and 'macro.data.CPI.value' in anchors
      and 'china.southbound.net_buy' in anchors
      and 'rate_economy.fed_funds_futures.0.price' in anchors)
bad_map = []
for k, v in anchors.items():
    ident = fp.verify_anchor_identity(k, v)
    if ident['status'] != 'MAPPED' or ident['metric_id'] != v.get('metric_id'):
        bad_map.append((k, ident['status'], ident['metric_id'], v.get('metric_id')))
check("A9 锚点族回环: 每个真实锚点键canonical映射=锚点自带metric_id(镜像锁定,无未映射)",
      not bad_map, str(bad_map[:4]))
check("A10 DFF锚点判日频(旧Gate B误判月度45): 窗口=10",
      dv.freshness_rule_for('rate_economy.current_rates.DFF.value')[0] == 10
      and dv.metric_frequency('rate_economy.current_rates.DFF.value')[0] == 'daily')

# ══ B. 注册表配置实际驱动判定 ═════════════════════════════════════
print("\n[B] 注册表窗口变更实际生效(真实判定路径)")
def _narrow_spx(reg):
    for m in reg['metrics']:
        if m['metric_id'] == 'SPX':
            m['freshness']['max_calendar_lag_days'] = 2
try:
    load_temp_registry(_narrow_spx)
    iss3, _ = fact_freq_issues('SPX', 7659.44, lag_days(3), 'global_market_collector')
    iss2, _ = fact_freq_issues('SPX', 7659.44, lag_days(2), 'global_market_collector')
    check("B1 SPX窗5→2: 真实validate_fact对lag3新增DEGRADED且点名2天窗口",
          len(iss3) == 1 and iss3[0]['severity'] == 'DEGRADED' and '2天' in iss3[0]['message'],
          str(iss3))
    check("B2 lag2在批准边界内无披露(边界含端点)", iss2 == [], str(iss2))
finally:
    fe.load_registry(force=True)
iss3b, _ = fact_freq_issues('SPX', 7659.44, lag_days(3), 'global_market_collector')
check("B3 恢复生产注册表后lag3回到有效(5天窗)——判定随配置真实往返", iss3b == [], str(iss3b))

# ══ C. 月频发布滞后场景 ═══════════════════════════════════════════
print("\n[C] 月频发布滞后六场景(三问分离)")
v1 = fp.assess('CPI', '2026-10-01', '2026-10-10')
_c1f = fe.make_fact('CPI', 310.0, '2026-10-01', '2026-10-10T08:00:00+08:00', 'x.json', 'macro_collector')
_c1iss = fe.validate_fact(_c1f, {'value': 310.0}, fe.metric('CPI'), as_of_date='2026-10-10')
check("C1 当月观测未发布: C问新鲜(lag9≤60)+release-limit WARN(引擎真实路径)+点时=RELEASE_UNKNOWN",
      v1['fresh'] is True and v1['point_in_time']['status'] == 'RELEASE_UNKNOWN'
      and any(i['category'] == 'release-limit' and i['severity'] == 'WARN' for i in _c1iss),
      str(v1) + str(_c1iss))
v2 = fp.assess('CPI', '2026-09-01', '2026-10-20')
check("C2 已发布的上一期(观测上月,lag49): 新鲜且无release-limit",
      v2['fresh'] is True and v2['status'] == 'FRESH')
v3 = fp.assess('CPI', lag_days(75), AS_OF)
check("C3 长期未更新(lag75>60): STALE+DEGRADED披露(引擎同判)",
      v3['fresh'] is False and v3['status'] == 'STALE'
      and len(fact_freq_issues('CPI', 310.0, lag_days(75), 'macro_collector')[0]) == 1)
v4 = fp.assess('CPI', lag_days(130), AS_OF)
check("C4 连缺多期(lag130): STALE(不因更旧而变其他级别)", v4['status'] == 'STALE' and v4['fresh'] is False)
v5 = fp.assess('CPI', '2026-09-01', '2026-10-10', release_date='2026-10-09')
v6 = fp.assess('CPI', '2026-09-01', '2026-10-10', release_date='2026-10-13')
check("C5 已知发布日≤as_of: 点时OK新鲜;发布日>as_of: NOT_AVAILABLE_AT_AS_OF不得作当前证据",
      v5['point_in_time']['status'] == 'OK' and v5['fresh'] is True
      and v6['status'] == 'NOT_AVAILABLE_AT_AS_OF' and v6['fresh'] is False)
v7 = fp.assess('CPI', '2026-09-01', '2026-10-10')
check("C6 发布未知: 如实RELEASE_UNKNOWN(绝不伪造release_date字段),新鲜度按观测窗判定",
      v7['point_in_time']['status'] == 'RELEASE_UNKNOWN'
      and 'release_date' not in v7['point_in_time'] and v7['fresh'] is True)

# ══ D. Gate A/B一致性(10项强制指标×正常+过期) ═════════════════════
print("\n[D] 三路一致: fp.assess ↔ validate_fact ↔ is_fresh_anchor")
D_CASES = [  # (metric, anchor_key, value, collector, 正常lag, 过期lag)
    ('BTC', 'global_market.data.BTC.close', 108000.0, 'global_market_collector', 1, 4),
    ('SPX', 'global_market.data.SPX.close', 7659.44, 'global_market_collector', 4, 6),
    ('CPI', 'macro.data.CPI.value', 310.0, 'macro_collector', 45, 65),
    ('CORE_PCE', 'macro.data.CORE_PCE.value', 118.5, 'macro_collector', 45, 65),
    ('ICSA', 'macro.data.ICSA.value', 221000.0, 'macro_collector', 16, 18),
    ('DFF', 'rate_economy.current_rates.DFF.value', 4.33, 'rate_expectations', 9, 12),
    # W2-FIX1-04: DFEDTARU/L窗口45→10(用户第三轮批复),正常/过期lag随之改
    # 9/12(原44/47按已废止的45天窗设定)
    ('DFEDTARU', 'rate_economy.current_rates.DFEDTARU.value', 4.5, 'rate_expectations', 9, 12),
    ('DFEDTARL', 'rate_economy.current_rates.DFEDTARL.value', 4.25, 'rate_expectations', 9, 12),
    ('SH_PE', 'china.valuation.pe', 16.4, 'china_collector', 9, 12),
    ('UST_10Y', 'macro.data.UST_10Y.value', 4.28, 'macro_collector', 6, 8)]
mismatch = []
for mid, akey, val, col, lag_ok, lag_bad in D_CASES:
    for lag, want_fresh in ((lag_ok, True), (lag_bad, False)):
        obs = lag_days(lag)
        v = fp.assess(mid, obs, AS_OF)['fresh']
        iss, f_ = fact_freq_issues(mid, val, obs, col)
        a_clean = not iss
        b = dv.is_fresh_anchor(akey, {'obs_date': obs}, AS_OF)
        if not (v == a_clean == b == want_fresh):
            mismatch.append((mid, lag, v, a_clean, b, want_fresh))
check("D1 10项指标×正常+过期: 三路判定完全一致且符合批准窗口",
      not mismatch, str(mismatch[:4]))
check("D2 BTC按批准2天窗(lag3即过期,非旧7天)",
      fp.assess('BTC', lag_days(3), AS_OF)['fresh'] is False
      and fp.assess('BTC', lag_days(2), AS_OF)['fresh'] is True)
check("D3 DFEDTARU按10天(W2-FIX1第三轮批复45→10;旧Gate B月度45误频/旧引擎7误紧→现日频10)",
      fp.assess('DFEDTARU', lag_days(9), AS_OF)['fresh'] is True
      and fp.assess('DFEDTARU', lag_days(44), AS_OF)['fresh'] is False
      and dv.metric_frequency('rate_economy.current_rates.DFEDTARU.value')[:2] == ('daily', 10))
check("D4 rate_economy.current_rates.DFF.value不得自动月度(W2-DEF-002)",
      dv.metric_frequency('rate_economy.current_rates.DFF.value')[0] == 'daily')

# ══ E. 身份伪装拒绝 ═══════════════════════════════════════════════
print("\n[E] 身份伪装与子串授权拒绝")
obs30 = lag_days(30)
check("E1 键位身份优先: SPX键冒称DFEDTARU身份→冲突不可认证(False)",
      dv.is_fresh_anchor('global_market.data.SPX.close',
                         {'obs_date': obs30, 'metric_id': 'DFEDTARU'}, AS_OF) is False)
info = dv.metric_registry_info('global_market.data.SPX.close',
                               {'obs_date': obs30, 'metric_id': 'DFEDTARU'})
check("E2 冲突披露: metric_registry_info点名caller身份与canonical不符(以canonical为准)",
      info['metric_id'] == 'SPX' and info['caller_metric_id_conflict'] is not None
      and 'DFEDTARU' in info['caller_metric_id_conflict'])
check("E3 未映射键携带registry metric_id仍fail-closed(调用方身份≠授权)",
      dv.is_fresh_anchor('other.foo', {'obs_date': lag_days(1), 'metric_id': 'CPI'}, AS_OF) is False
      and dv.freshness_rule_for('other.foo')[0] == dv.UNMAPPED_LEGACY_DIAGNOSTIC)
check("E4 子串伪装不授权: 'SPXevil'不得借SPX身份/窗口",
      fp.verify_anchor_identity('global_market.data.SPXevil.close')['status'] == 'UNMAPPED'
      and dv.is_fresh_anchor('global_market.data.SPXevil.close',
                             {'obs_date': lag_days(1)}, AS_OF) is False)
# W2-FIX1(§7.4)修订: 原E5断言"冲突caller metric_id下仍True"——该语义被
# 独立验收判为IA-P02-W2-DEF-003: 冲突=身份无法认证(UNVERIFIED),不得仅记录
# conflict后继续授予时效认证。宽度保留语义改由无冲突对照(E5a)锁定。
# W2-FIX1-04: DFEDTARU窗45→10后,无冲突caller的合法锚点以lag9锁定"宽判保留"
# 语义(原lag44按已废止的45天窗设定)
check("E5a 合法锚点无冲突caller照常认证: DFEDTARU锚lag9(≤10)→新鲜",
      dv.is_fresh_anchor('rate_economy.current_rates.DFEDTARU.value',
                         {'obs_date': lag_days(9)}, AS_OF) is True)
check("E5b 冲突caller metric_id→UNVERIFIED不再认证(FIX1-03 §7.4)",
      dv.is_fresh_anchor('rate_economy.current_rates.DFEDTARU.value',
                         {'obs_date': lag_days(44), 'metric_id': 'SPX'}, AS_OF) is False
      and fp.verify_anchor_identity('rate_economy.current_rates.DFEDTARU.value',
                                    {'metric_id': 'SPX'})['status'] == 'UNVERIFIED')

# ══ F. 非法输入 ═══════════════════════════════════════════════════
print("\n[F] 非法输入(未知不得转为有效)")
check("F1 观测缺失→NOT_OBSERVED;非法('2026-10-03INVALID'/'2026-02-30')→INVALID_DATE",
      fp.assess('CPI', None, AS_OF)['status'] == 'NOT_OBSERVED'
      and fp.assess('CPI', '2026-10-03INVALID', AS_OF)['status'] == 'INVALID_DATE'
      and fp.assess('CPI', '2026-02-30', AS_OF)['status'] == 'INVALID_DATE')
check("F2 未来观测→FUTURE_DATE;未注册指标→UNREGISTERED(不得默认有效)",
      fp.assess('CPI', '2026-10-30', AS_OF)['status'] == 'FUTURE_DATE'
      and fp.assess('NOT_A_METRIC', lag_days(1), AS_OF)['status'] == 'UNREGISTERED'
      and fp.assess('NOT_A_METRIC', lag_days(1), AS_OF)['fresh'] is False)
check("F3 非法release_date→INVALID_RELEASE;发布早于观测→INVALID_RELEASE",
      fp.assess('CPI', '2026-09-01', AS_OF, release_date='10月13日')['status'] == 'INVALID_RELEASE'
      and fp.assess('CPI', '2026-09-01', AS_OF, release_date='2026-08-01')['status'] == 'INVALID_RELEASE')
bad_regs = []
for name, mut in [
        ('缺freshness块', lambda r: [m.pop('freshness') for m in r['metrics'] if m['metric_id'] == 'SPX']),
        ('窗口为字符串', lambda r: [m['freshness'].update(max_calendar_lag_days='45')
                                 for m in r['metrics'] if m['metric_id'] == 'SPX']),
        ('窗口为float', lambda r: [m['freshness'].update(max_calendar_lag_days=45.5)
                                for m in r['metrics'] if m['metric_id'] == 'SPX']),
        ('窗口为bool', lambda r: [m['freshness'].update(max_calendar_lag_days=True)
                               for m in r['metrics'] if m['metric_id'] == 'SPX']),
        ('窗口为0', lambda r: [m['freshness'].update(max_calendar_lag_days=0)
                            for m in r['metrics'] if m['metric_id'] == 'SPX']),
        ('频率非法', lambda r: [m.update(frequency='hourly') for m in r['metrics'] if m['metric_id'] == 'SPX'])]:
    reg = json.loads(json.dumps(_REG))
    mut(reg)
    try:
        fp.build_policy(reg)
        bad_regs.append((name, 'no-error'))
    except fp.FreshnessPolicyError:
        pass
check("F4 窗口缺失/字符串/float/bool/0/频率非法→build_policy全部fail-loud", not bad_regs, str(bad_regs))
raised = None
try:
    def _drop(reg):
        for m in reg['metrics']:
            if m['metric_id'] == 'SPX':
                m.pop('freshness')
    load_temp_registry(_drop)
except fp.FreshnessPolicyError:
    raised = True
finally:
    fe.load_registry(force=True)
check("F5 生产加载路径(load_registry)对缺窗注册表fail-loud(不静默回退7/16/92)", raised is True)

# ══ G. 正式研究链(真实链路,隔离临时目录) ═════════════════════════
print("\n[G] 正式研究链: 正常/披露/失败传导/不重开/不污染")


def build_day(mutate_macro=None, break_metric=None):
    td = tempfile.mkdtemp(prefix='w2-chain-', dir=_TMPD)
    daily = os.path.join(td, 'daily')
    fixt.write_collectors(daily, DAY, break_metric=break_metric)
    if mutate_macro:
        p = os.path.join(daily, f'macro_{DAY}.json')
        obj = json.load(open(p, encoding='utf-8'))
        mutate_macro(obj)
        json.dump(obj, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
    sb.build_snapshot(target_ymd=DAY, data_dir=daily, out_dir=daily,
                      trusted_root=td, as_of=fixt.as_of_for(DAY))
    snap = json.load(open(os.path.join(daily, f'research_snapshot_{DAY}.json'), encoding='utf-8'))
    return td, daily, snap


td1, daily1, snap1 = build_day()
g1 = (snap1.get('gate_a') or {}).get('status')
apath1 = os.path.join(daily1, f'anchors_{DAY}.json')
check("G1 正常日: 真实链路Gate A=PASS且批次核验通过",
      g1 == 'PASS' and rp.verify_anchor_batch(apath1, daily_dir=daily1, trusted_root=td1) == (True, ''),
      f"gate={g1}")

td2, daily2, snap2 = build_day(mutate_macro=lambda o: o['data']['CPI'].update(date='2026-08-10'))
g2 = (snap2.get('gate_a') or {}).get('status')
cpi2 = next(f for f in snap2['facts'] if f['metric_id'] == 'CPI')
check("G2 合法DEGRADED: CPI滞后75天>60→DEGRADED披露,快照照常产出(披露非阻断,不丢证据)",
      g2 == 'DEGRADED' and any(i['category'] == 'frequency' and i['severity'] == 'DEGRADED'
                               for i in cpi2['issues'])
      and cpi2['quality_status'] == 'DEGRADED', f"gate={g2} q={cpi2['quality_status']}")

td3, daily3, snap3 = build_day(break_metric='SPX')
g3 = (snap3.get('gate_a') or {}).get('status')
check("G3 严重异常传导: core指标值'N/A'→type FAIL→Gate A=FAIL(快照存证)",
      g3 == 'FAIL' and any(f['quality_status'] == 'FAIL' and f['metric_id'] == 'SPX'
                           for f in snap3['facts']), f"gate={g3}")

def _umc_bad(o):
    o['data']['UMCSENT']['value'] = 9999.9   # 区间外,观测日新鲜
td4, daily4, snap4 = build_day(mutate_macro=_umc_bad)
umc = next(f for f in snap4['facts'] if f['metric_id'] == 'UMCSENT')
umc_anchor = json.load(open(os.path.join(daily4, f'anchors_{DAY}.json'),
                            encoding='utf-8')).get('macro.data.UMCSENT.value')
g4 = (snap4.get('gate_a') or {}).get('status')
check("G4 Gate B宽不重开Gate A: UMCSENT观测新鲜(is_fresh=True)但数值区间外FAIL→事实仍FAIL",
      umc['quality_status'] == 'FAIL'
      and not any(i['category'] == 'frequency' for i in umc['issues'])
      and dv.is_fresh_anchor('macro.data.UMCSENT.value',
                             {'obs_date': umc['observation_date']}, AS_OF) is True
      and umc_anchor is not None and umc_anchor.get('quality') == 'FAIL' and g4 == 'DEGRADED',
      f"q={umc['quality_status']} gate={g4}")

stale_obs = lag_days(30)
ev = [{'metric': 'macro.data.CCC_OAS.value', 'value': 10.18, 'obs_date': stale_obs, 'mechanism': '信用'}]
anchors_stub = {'macro.data.CCC_OAS.value': {'value': 10.18, 'obs_date': stale_obs, 'as_of': AS_OF}}
verified, rejects = ae.verify_evidence_items(ev, anchors_stub, AS_OF)
check("G5 过期证据不进观察: 日频滞后30天→验证拒绝(不污染views/长期观察)",
      verified == [] and len(rejects) == 1 and '过期' in rejects[0][0], str(rejects))

# ══ H. 敏感性 ═════════════════════════════════════════════════════
print("\n[H] 敏感性: 改窗双向检出+锚点身份篡改拒绝")
try:
    load_temp_registry(lambda r: [m['freshness'].update(max_calendar_lag_days=2)
                                  for m in r['metrics'] if m['metric_id'] == 'SPX'])
    check("H1 人工收窄SPX→2: lag3从有效变披露(检出收紧方向)",
          len(fact_freq_issues('SPX', 7659.44, lag_days(3), 'global_market_collector')[0]) == 1)
finally:
    fe.load_registry(force=True)
try:
    load_temp_registry(lambda r: [m['freshness'].update(max_calendar_lag_days=120)
                                  for m in r['metrics'] if m['metric_id'] == 'CPI'])
    check("H2 人工放宽CPI→120: lag75从披露变有效(检出放宽方向,非单向锁死)",
          fact_freq_issues('CPI', 310.0, lag_days(75), 'macro_collector')[0] == [])
finally:
    fe.load_registry(force=True)

apath = os.path.join(daily1, f'anchors_{DAY}.json')
orig = open(apath, encoding='utf-8').read()
try:
    tam = json.loads(orig)
    tam['macro.data.CPI.value']['value'] = 999.0          # 数值篡改
    tam['macro.data.CPI.value']['metric_id'] = 'DFEDTARU'  # 身份伪装
    json.dump(tam, open(apath, 'w', encoding='utf-8'), ensure_ascii=False)
    ok, reason = rp.verify_anchor_batch(apath, daily_dir=daily1, trusted_root=td1)
    check("H3 篡改锚点数值+身份→正式批次核验拒绝(权威重建比对)",
          ok is False and reason, str(reason)[:120])
finally:
    open(apath, 'w', encoding='utf-8').write(orig)
ok2, reason2 = rp.verify_anchor_batch(apath, daily_dir=daily1, trusted_root=td1)
check("H4 恢复原始锚点后核验重新通过(篡改检测非损坏)",
      ok2 is True and reason2 == '', f"ok={ok2} reason={str(reason2)[:200]}")

shutil.rmtree(_TMPD, ignore_errors=True)
print("\n" + "=" * 64)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 64)
sys.exit(0 if FAIL == 0 else 1)
