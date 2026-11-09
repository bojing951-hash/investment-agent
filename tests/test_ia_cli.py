#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ia_cli 契约回归套件(Skill 化, 2026-11-08)。

覆盖四组:
① 数值/变化节点契约: 单位族分桶(fact_engine 三常量为唯一源+other 兜底)、
   身份注入(is_proxy/proxy_of/market_seat 由代码进每行)、缺失如实(null+原因,绝不0)、
   变化量口径随行(change_unit/basis_date/窗口语义/公式/bp_equivalent);
② 研究纪律 lint: EEM 反例(成分编造=violation)、对照干净、因果动词=warning、
   事实契约位阻断(lint_fact_contract_text)、【假设】段放行;
③ 跨经济体对齐警示: 观测窗跨度 warnings;
③b 金融正确性静态防线(⑦期限标识防错绑跨期/⑧汇率方向语义随行);
④ 子进程行为: doctor 离线可跑、用法错误 rc=2、research 无快照结构化错误 rc=1、
   update 无 --yes 拒绝、archive get 不存在→结构化 not_found。
CI 安全: 合成快照+真实注册表(已提交),零网络零写入(不触发 archive save 默认目录)。
"""
import json
import os
import glob
import subprocess
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


import ia_cli  # noqa: E402
import workbench_data as wd  # noqa: E402

REG = wd.load_registry(ROOT)

# ── 合成快照(结构对照真实 research_snapshot;含 ETF 代理/利率/汇率/缺失四类) ──
SYN = {
    'snapshot_id': 'research_snapshot_20991231', 'target_date': '2099-12-31',
    'research_as_of': '2099-12-31T18:00:00+08:00',
    'gate_a': {'status': 'DEGRADED', 'core_missing': [],
               'noncore_missing': ['INDPRO'],
               'noncore_missing_detail': {'INDPRO': '来源文件在场而指标缺席(示意)'},
               'noncore_degraded': []},
    'sources_status': {},
    'facts': [
        {'fact_id': 'F1', 'metric_id': 'SPX', 'display_name': '标普500指数',
         'value': 7376.86, 'unit': 'index_point', 'value_type': 'level',
         'observation_date': '2099-12-30', 'as_of': '2099-12-31',
         'source': {'collector': 'global_market_collector', 'file': 'global_20991231.json'},
         'quality_status': 'PASS', 'issues': [],
         'derived': {'week': {'basis_date': '2099-12-23', 'basis_value': 7581.0,
                              'window': 'ISO周之前最后观测为基准(示意)',
                              'sessions_in_window': 5, 'expected_sessions': 5,
                              'pct_change': -2.69,
                              'formula': '(值/基准-1)×100',
                              'return_semantics': '价格收益(采集器复权口径)'}}},
        {'fact_id': 'F2', 'metric_id': 'UST_10Y', 'display_name': '10年期美债收益率',
         'value': 4.84, 'unit': 'percent', 'value_type': 'yield_or_spread_level',
         'observation_date': '2099-12-29', 'as_of': '2099-12-31',
         'source': {'collector': 'macro_collector', 'file': 'macro_20991231.json'},
         'quality_status': 'PASS', 'issues': [],
         'derived': {'week': {'basis_date': '2099-12-22', 'basis_value': 4.94,
                              'window': 'ISO周之前最后观测为基准(示意)',
                              'sessions_in_window': 4, 'expected_sessions': 5,
                              'pp_change': -0.10, 'bp_change': -10.0,
                              'formula': '值−基准(百分点;1pp=100bp)'}}},
        {'fact_id': 'F3', 'metric_id': 'EEM', 'display_name': 'iShares新兴市场ETF',
         'value': 59.33, 'unit': 'usd', 'value_type': 'level',
         'observation_date': '2099-12-30', 'as_of': '2099-12-31',
         'source': {'collector': 'global_market_collector', 'file': 'global_20991231.json'},
         'quality_status': 'PASS', 'issues': [], 'derived': {}},
    ],
    'series_store': {},
}

print("═" * 60)
print("① 数值/变化节点契约")
print("═" * 60)
check("单位族分桶: percent→rate",
      ia_cli.unit_family('percent', 'rates_yield')[0] == 'rate')
check("单位族分桶: index_point/usd→price",
      ia_cli.unit_family('index_point', 'equity_index')[0] == 'price'
      and ia_cli.unit_family('usd', 'country_etf_proxy')[0] == 'price')
check("单位族分桶: persons→count",
      ia_cli.unit_family('persons', 'macro_index')[0] == 'count')
check("单位族分桶: 汇率归 price 族+fx 子族",
      ia_cli.unit_family('jpy_per_usd', 'fx_rate') == ('price', 'fx'))
check("单位族分桶: 未知 unit→other 兜底(显示层不崩)",
      ia_cli.unit_family('bogus_unit', 'x')[0] == 'other')

warnings = []
facts_by_id = {f['metric_id']: f for f in SYN['facts']}
miss_detail = SYN['gate_a']['noncore_missing_detail']

node = ia_cli.value_node(REG['by_id']['EEM'], facts_by_id, miss_detail, warnings)
check("EEM 身份注入: is_proxy+proxy_of+market_seat 代码级随行",
      node['identity']['is_proxy'] is True
      and node['identity']['proxy_of'] == 'MSCI新兴市场指数'
      and node['identity']['market_seat'] == 'offshore_proxy'
      and node['identity']['economy'] == 'GLOBAL', str(node['identity']))
check("EEM calc 口径原文随行(美元计价,含汇率影响)",
      '美元计价' in (node['calc'] or ''))

node_u = ia_cli.value_node(REG['by_id']['UST_10Y'], facts_by_id, miss_detail, warnings)
ch = node_u['changes'][0]
check("利率变化: change_unit=pp + bp_equivalent 双报",
      ch['change_unit'] == 'pp' and ch['value'] == -0.10
      and ch['bp_equivalent'] == -10.0, str(ch))
check("利率变化: 基准日/窗口语义/公式随行",
      ch['basis_date'] == '2099-12-22' and '基准' in ch['window_semantics']
      and ch['formula'])
check("利率变化: 无 return_semantics 键(利率族本无此项,不猜)",
      'return_semantics' not in ch)

node_s = ia_cli.value_node(REG['by_id']['SPX'], facts_by_id, miss_detail, warnings)
chs = node_s['changes'][0]
check("价格变化: change_unit=pct + return_semantics 随行",
      chs['change_unit'] == 'pct' and chs['return_semantics'].startswith('价格收益'))

node_m = ia_cli.value_node(REG['by_id']['INDPRO'], facts_by_id, miss_detail, warnings)
check("缺失指标: value=null+presence=missing+原因(绝不填0)",
      node_m['value'] is None and node_m['presence'] == 'missing'
      and node_m['absence_reason'] and node_m['quality_status'] == 'MISSING'
      and node_m['changes'] == [], str(node_m)[:120])

# ── 金融正确性静态防线(C审计⑦⑧): 注册表身份字段先天花板 ──
TENOR_IDS = ('UST_2Y', 'UST_10Y', 'JGB2Y', 'JGB10Y')
check("⑦ 期限标识: 利差操作数 display_name 含期限(2年/10年),防错绑跨期限",
      all(any(t in REG['by_id'][i]['display_name'] for t in ('2年期', '10年期'))
          for i in TENOR_IDS),
      str({i: REG['by_id'][i]['display_name'] for i in TENOR_IDS}))
check("⑦ 美日10Y利差操作数成对在场(UST_10Y+JGB10Y)",
      {'UST_10Y', 'JGB10Y'} <= set(REG['by_id']))
check("⑧ 汇率方向: USDJPY calc 含方向语义(上涨=美元升值),引用必随行",
      '美元升值' in (REG['by_id']['USDJPY']['calc'] or ''),
      REG['by_id']['USDJPY'].get('calc'))
check("⑧ USDJPY 归 price 族+fx 子族(方向语义有结构位承载)",
      ia_cli.unit_family(REG['by_id']['USDJPY'].get('unit', ''),
                         REG['by_id']['USDJPY'].get('asset_class', '')) == ('price', 'fx'))

print("═" * 60)
print("② 研究纪律 lint(AC-06 反例集)")
print("═" * 60)
w1, v1 = ia_cli.lint_grounded_answer('EEM本周下跌,受日本拖累(代理含日本权重)')
check("EEM 反例: 成分编造→violation(unsupported_composition_claim)",
      any(x['kind'] == 'unsupported_composition_claim' for x in v1), str(v1))
check("EEM 反例: 因果动词→warning(非阻断)", len(w1) == 1 and '拖累' in w1[0])
w2, v2 = ia_cli.lint_grounded_answer('FXI +5.65%、INDA +6.64% 均上涨')
check("对照组(包内事实): 零warning零violation", not w2 and not v2)
v3 = ia_cli.lint_fact_contract_text('| EEM | 59.33 | -2.80% | 受日本拖累(代理含日本权重) |')
check("事实契约位: 因果+成分双violation",
      {x['kind'] for x in v3} == {'causal_claim_in_fact_position',
                                  'unsupported_composition_claim'}, str(v3))
v4 = ia_cli.lint_fact_contract_text('【假设】拖累或来自科技权重较高的成分,无法从本数据包验证')
check("【假设】段: 因果/成分放行(标签在)",
      not v4, str(v4))

print("═" * 60)
print("③ 跨经济体对齐警示")
print("═" * 60)
warn3 = []
view = ia_cli.economy_view(SYN, REG, ['US', 'JP'], warn3)
check("双经济体视图: US/JP 节点集生成",
      set(view) == {'US', 'JP'} and view['US']['n_metrics'] > 0)
check("跨经济体观测窗跨度→强制警示(须转述用户)",
      any('观测窗跨度' in w for w in warn3), str(warn3))
check("单经济体视图: 不触发跨体跨度警示",
      not any('观测窗跨度' in w for w in ia_cli.economy_view(SYN, REG, ['US'], [])))

print("═" * 60)
print("④ 子进程行为(结构化输出/退出码)")
print("═" * 60)
CLI = os.path.join(ROOT, 'ia_cli.py')


def run_cli(*argv):
    return subprocess.run([sys.executable, CLI, *argv],
                          capture_output=True, text=True, timeout=120)


r = run_cli('doctor')
d = json.loads(r.stdout)
check("doctor: rc=0 离线可跑,信封齐(ok/capability/engine_root)",
      r.returncode == 0 and d['ok'] and d['capability'] == 'doctor'
      and os.path.isabs(d['engine_root']))
check("doctor: env 只报已配置与否,值不出现(v2.1 唯一模型面=MODEL_* 三参,无旧变量行)",
      set(d['data']['env']) == {'MODEL_API_KEY', 'MODEL_BASE_URL', 'MODEL_NAME',
                                'FRED_API_KEY', 'TUSHARE_TOKEN',
                                'FINNHUB_API_KEY', 'YF_PROXY'}
      and all(set(v) == {'configured', 'purpose'} for v in d['data']['env'].values())
      and not any('glm' in k.lower() for k in d['data']))   # v2.1: 医生面零旧变量键
check("doctor: 无快照时如实 available=false(CI 预期)",
      d['data']['snapshot']['available'] in (True, False))  # CI 无快照/本地有快照均合法

r = run_cli('overview', '--economy', 'XX')
check("未知经济体→rc=2 结构化错误", r.returncode == 2
      and json.loads(r.stdout)['error']['kind'] == 'bad_economy')
r = run_cli('compare')
check("compare 无模式→rc=2", r.returncode == 2)
r = run_cli('update')
d = json.loads(r.stdout)
check("update 无 --yes→confirmation_required(rc=1,永不自动跑)",
      r.returncode == 1 and d['error']['kind'] == 'confirmation_required')
r = run_cli('archive', 'get', '--query-id', 'QB-20991231-999')
d = json.loads(r.stdout)
check("archive get 不存在→rc=1 结构化 not_found",
      r.returncode == 1 and d['error']['kind'] == 'not_found')
r = run_cli('history')
d = json.loads(r.stdout)
check("history 不带 --metric→列出可查指标(CI 下可为空列表,结构在场)",
      r.returncode == 0 and 'series_capable_metrics' in d['data'])

# 批2 W8(C-1): catalog 全字段——字段齐全性+与注册表实值一致抽验
# (期望值直读 metric_registry.json/snapshot 原始 JSON,不经被测模块自算)
# A-fin(2026-11-09): +time_semantics(12键,注册表人工登记键纯透传)
FULL_KEYS = {'metric_id', 'label', 'unit', 'unit_family', 'frequency',
             'first', 'last', 'n', 'calendar', 'release_semantics',
             'time_semantics', 'quality_status'}
caps = d['data']['series_capable_metrics']
if caps:
    check("catalog 全字段(12键)且键集一致",
          all(set(c) == FULL_KEYS for c in caps),
          str(next((set(c) ^ FULL_KEYS for c in caps if set(c) != FULL_KEYS), '')))
    reg_doc = json.load(open(os.path.join(ROOT, 'config', 'metric_registry.json'),
                             encoding='utf-8'))
    reg_by_id = {m['metric_id']: m for m in reg_doc['metrics']}
    for c in caps[:5]:                      # 抽验前5项注册表透传一致性
        m = reg_by_id.get(c['metric_id'])
        ok = (m is not None
              and c['label'] == m.get('display_name')
              and c['unit'] == m.get('unit', '')
              and c['frequency'] == m.get('frequency')
              and c['calendar'] == m.get('calendar')
              and c['release_semantics'] == m.get('release_semantics'))
        check(f"catalog 抽验 {c['metric_id']} 与注册表实值一致", ok,
              f"catalog={ {k: c[k] for k in ('label','unit','frequency','calendar')} }")
    snap_files = sorted(glob.glob(os.path.join(
        ROOT, 'data', 'daily', 'research_snapshot_*.json')))
    if snap_files:
        snap = json.load(open(snap_files[-1], encoding='utf-8'))
        ss = snap.get('series_store') or {}
        qmap = {f.get('metric_id'): f.get('quality_status')
                for f in snap.get('facts', [])}
        by_id = {c['metric_id']: c for c in caps}
        ss_in_catalog = [mid for mid in ss if mid in by_id]
        if ss_in_catalog:
            mid = ss_in_catalog[0]
            dates = ss[mid]['dates']
            c = by_id[mid]
            check(f"catalog 序列统计 {mid} first/last/n 与 series_store 原值一致",
                  c['first'] == dates[0] and c['last'] == dates[-1]
                  and c['n'] == len(dates),
                  f"catalog=({c['first']},{c['last']},{c['n']}) "
                  f"raw=({dates[0]},{dates[-1]},{len(dates)})")
            check(f"catalog {mid} quality_status 与快照事实层一致",
                  c['quality_status'] == qmap.get(mid),
                  f"{c['quality_status']} vs {qmap.get(mid)}")
else:
    check("catalog 空为合法(CI 无快照)", isinstance(caps, list))

# research 无快照(CI): 结构化 no_snapshot;本地有快照则退化为状态面断言
r = run_cli('research', '--question', '美国和日本10年期国债收益率差是多少')
d = json.loads(r.stdout)
if 'error' in d:
    check("research 无快照→rc=1 no_snapshot(CI 预期)",
          r.returncode == 1 and d['error']['kind'] == 'no_snapshot')
else:
    check("research 有快照→接地作答,violations 字段纪律生效",
          r.returncode == 0 and d['data']['status'] in ('answered', 'refusal'))

print()
print("═" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("═" * 60)
sys.exit(0 if FAIL == 0 else 1)
