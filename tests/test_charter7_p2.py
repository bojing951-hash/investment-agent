#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Charter 7 P2 修复轮验收测试(2026-11-10,协调方 P2 指令)。

三项逐条(独立计算预期+边界+回归;不降门槛/不删警告/不改期望值):
  [1] P2-1 排序依据披露(真实缺陷,Case B 实战 QB-20261110-023): 输出顶层
      sort_basis 逐字随行('(n_missing, distance, month)' 键序+名次非纯
      距离序+以 distance 为准)+每条 top 条目 n_missing=缺席特征数=排序
      首键;cli-contract/SKILL/engine-notes 文档锁+QB-023 处置注记;
      **零计算改动**(排序键序与既有排序行为不变,回归);
  [2] P2-2 1m/1y/5y 自配对正式口径(Case A 实战): compare --metrics X,X
      --start T-k --end T 端到端(月×月月键对齐+两侧 interval_change_
      common_window 同值+基准=严格早于窗内首观测)+空窗 empty_window
      rc=1 诚实拒绝(月频 1m 窗无新观测只引水平)+文档锁(三处正式口径);
  [3] P2-3 数据缺口接线(SOFR/WALCL,现有 FRED Key 免费序列,零真实拉取):
      注册表 v2.7.0 结构校验通过+非 core 不改 Gate A 语义;macro_collector
      三张映射接线;compute_series_changes 独立期望(SOFR rate=pp 无 pct/
      WALCL index=水平+百分比);normalize_macro 端到端事实生成+identity/
      单位族;recompute_gate_a 缺席披露(接线后未拉取=noncore_missing 如实
      而非静默);台账文件在场且红线声明。

数据纪律: 全部 fixture=合成内存序列/临时目录;零网络零真实数据零凭证
(SOFR/WALCL 真实拉取需协调方批准,本测试只验接线+fixture)。
运行: ~/AI内容/venv/bin/python3 tests/test_charter7_p2.py
"""
import hashlib
import io
import json
import os
import sys
import tempfile
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (ROOT, os.path.join(ROOT, 'scripts')):
    if p not in sys.path:
        sys.path.insert(0, p)

PASS, FAIL = 0, 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}  {detail}")


import ia_cli  # noqa: E402
import macro_collector as mc  # noqa: E402
import fact_engine as fe  # noqa: E402
import research_provenance as rp  # noqa: E402
import registry_semantics as rs  # noqa: E402
import workbench_data as wd  # noqa: E402

REG_JSON = json.load(open(os.path.join(ROOT, 'config', 'metric_registry.json'),
                          encoding='utf-8'))
REG_BY_ID = {m['metric_id']: m for m in REG_JSON['metrics']}
REG_FULL = wd.load_registry(ROOT)   # cmd_compare 消费形态(by_id 键)

print("=" * 72)
print("[1] P2-1 排序依据披露(sort_basis 随行,零计算改动)")
ae = __import__('analog_engine')

# 文案契约: 键序逐字+双句语义(独立于引擎常量书写,防自证)
check("sort_basis 常量: 键序(n_missing, distance, month)+名次非纯距离序"
      "+以 distance 为准 三要素齐",
      '(n_missing, distance, month)' in ae.SORT_BASIS
      and '名次非纯距离序' in ae.SORT_BASIS
      and 'distance 字段为准' in ae.SORT_BASIS
      and '缺席特征多者降位' in ae.SORT_BASIS,
      ae.SORT_BASIS)

# 引擎回归: 排序行为不变(双键序仍按(缺席数,距离,月)——机制无错,纯披露)
# 用纯合成特征字典直接驱动排序路径的最小复算器(不调引擎内部):
cands = [  # (n_missing, D, month) → 声明序: 缺席少者优先,次距离,再月
    {'m': '2020-12', 'D': 1.19, 'miss': 2},
    {'m': '2019-12', 'D': 1.01, 'miss': 7},   # QB-023 实例对: miss7 排后
    {'m': '2021-06', 'D': 1.19, 'miss': 2},
    {'m': '2021-01', 'D': 0.90, 'miss': 2},
]
ordered = [c['m'] for c in sorted(cands, key=lambda x: (x['miss'], x['D'], x['m']))]
check("排序语义回归: (缺席数,距离,月)双键序与 QB-023 实例一致"
      "(2020-12 排 2019-12 前,距离更小者缺数更多不反超)",
      ordered == ['2021-01', '2020-12', '2021-06', '2019-12'],
      str(ordered))

# 文档锁: 三处同步一句+QB-023 处置注记
SKILL = open(os.path.join(ROOT, '.agents/skills/global-macro-research/SKILL.md'),
             encoding='utf-8').read()
CLI_CONTRACT = open(os.path.join(
    ROOT, '.agents/skills/global-macro-research/references/cli-contract.md'),
    encoding='utf-8').read()
ENGINE_NOTES = open(os.path.join(
    ROOT, '.agents/skills/global-macro-research/references/engine-notes.md'),
    encoding='utf-8').read()
check("文档锁: cli-contract+SKILL+engine-notes 均含 sort_basis 披露句",
      all('sort_basis' in t and 'n_missing' in t
          for t in (CLI_CONTRACT, SKILL, ENGINE_NOTES)))
check("文档锁: engine-notes 含 QB-20261110-023 处置注记(机制无错+已加披露)",
      'QB-20261110-023' in ENGINE_NOTES and '机制无错' in ENGINE_NOTES
      and '零计算改动' in ENGINE_NOTES)

print("\n[2] P2-2 自配对 1m/1y/5y 正式口径(Case A 实战路径)")
# 合成 FED_FUNDS 月频序列(01 锚,2025-11..2026-10;独立期望值手算):
ff_dates = ['2025-11-01', '2025-12-01', '2026-01-01', '2026-02-01',
            '2026-03-01', '2026-04-01', '2026-05-01', '2026-06-01',
            '2026-07-01', '2026-08-01', '2026-09-01', '2026-10-01']
ff_vals = [3.50, 3.55, 3.60, 3.62, 3.62, 3.65, 3.70, 3.75, 3.80, 3.85,
           3.88, 3.88]


def run_compare(argv, series_map):
    """进程内 cmd_compare: monkeypatch load_context/metric_series。"""
    saved_lc, saved_ms = ia_cli.load_context, wd.metric_series
    fake_snap = {'snapshot_id': 'research_snapshot_TESTP2',
                 'target_date': '20261110',
                 'research_as_of': '2026-11-10T08:00:00+08:00',
                 'gate_a': {'status': 'DEGRADED'}, 'facts': [],
                 'series_store': {k: {'dates': v[0], 'values': v[1]}
                                  for k, v in series_map.items()}}
    ia_cli.load_context = lambda: (fake_snap, REG_FULL, '')
    wd.metric_series = (lambda mid, s=None, root=None, _sm=fake_snap:
                        ({'metric_id': mid, 'label': mid,
                          'unit': (REG_BY_ID.get(mid) or {}).get('unit', ''),
                          'dates': _sm['series_store'][mid]['dates'],
                          'values': _sm['series_store'][mid]['values'],
                          'source': 'store'}, None)
                        if mid in _sm['series_store'] else (None, '无'))
    parser = ia_cli.build_parser()
    args = parser.parse_args(['compare'] + argv)
    buf = io.StringIO()
    code = 0
    try:
        with redirect_stdout(buf):
            ia_cli.cmd_compare(args)
    except SystemExit as e:
        code = e.code or 0
    finally:
        ia_cli.load_context, wd.metric_series = saved_lc, saved_ms
    try:
        return code, json.loads(buf.getvalue())
    except ValueError:
        return code, {'_raw': buf.getvalue()[:200]}


SMAP = {'FED_FUNDS': (ff_dates, ff_vals)}
# 1y 窗(2025-11-10~2026-11-10): 窗内首观测 2025-12-01 → 基准=严格早于它的
# 2025-11-01(3.50),窗末观测 2026-10-01(3.88)→ pp=+0.38(独立手算)
code, out = run_compare(
    ['--metrics', 'FED_FUNDS,FED_FUNDS',
     '--start', '2025-11-10', '--end', '2026-11-10'], SMAP)
iv = out['data']['sides'][0]['interval_change_common_window'] if out.get('ok') else {}
check("1y 自配对: ok+月×月月键对齐+两侧同指标同区间变动",
      code == 0 and out['ok']
      and out['data']['alignment']['mode'] == 'month_grid'
      and [s['metric_id'] for s in out['data']['sides']]
      == ['FED_FUNDS', 'FED_FUNDS'],
      str(out.get('error')))
check("1y 自配对: interval_change 独立期望(基准=2025-11-01 窗前末笔,"
      "末=2026-10-01,pp=3.88−3.50=+0.38;单位纪律=利率 pp)",
      iv.get('basis_date') == '2025-11-01' and iv.get('basis_value') == 3.50
      and iv.get('end_date') == '2026-10-01' and iv.get('end_value') == 3.88
      and abs(iv.get('pp_change', 9) - 0.38) < 1e-9,
      json.dumps(iv, ensure_ascii=False))
check("1y 自配对: 两侧 interval_change_common_window 全等(自配对无歧义)",
      out.get('ok') and json.dumps(out['data']['sides'][0]['interval_change_common_window'],
                                   sort_keys=True)
      == json.dumps(out['data']['sides'][1]['interval_change_common_window'],
                    sort_keys=True))

# 1m 窗无新观测(2026-10-10~2026-11-10 窗内无 01 锚观测)→ 诚实拒绝
code, out = run_compare(
    ['--metrics', 'FED_FUNDS,FED_FUNDS',
     '--start', '2026-10-10', '--end', '2026-11-10'], SMAP)
check("1m 空窗: empty_window rc=1 诚实拒绝(月频无当月新观测→只引水平,"
      "不以旧观测差硬造变化)",
      code == 1 and out.get('ok') is False
      and out.get('error', {}).get('kind') == 'empty_window',
      str(out.get('error')))

# 跨 2 月窗(2026-09-10~2026-11-10): 窗内观测 2026-10-01 → 基准 2026-09-01
code, out = run_compare(
    ['--metrics', 'FED_FUNDS,FED_FUNDS',
     '--start', '2026-09-10', '--end', '2026-11-10'], SMAP)
iv2 = out['data']['sides'][0]['interval_change_common_window'] if out.get('ok') else {}
check("跨月窗: 基准=窗内首观测前一月(2026-09-01 3.88),pp=3.88−3.88=0.00",
      code == 0 and iv2.get('basis_date') == '2026-09-01'
      and abs(iv2.get('pp_change', 9) - 0.0) < 1e-9,
      json.dumps(iv2, ensure_ascii=False))

USER_GUIDE = open(os.path.join(ROOT, 'docs', 'USER_GUIDE.md'), encoding='utf-8').read()
check("文档锁: cli-contract+SKILL 含 P2-2 正式口径标记+三处含 empty_window"
      "诚实语义+示例命令(cli-contract/USER_GUIDE 含 FED_FUNDS,FED_FUNDS)",
      all('P2-2' in t for t in (CLI_CONTRACT, SKILL))
      and all('empty_window' in t for t in (CLI_CONTRACT, SKILL, USER_GUIDE))
      and all('FED_FUNDS,FED_FUNDS' in t for t in (CLI_CONTRACT, USER_GUIDE))
      and '自配对' in USER_GUIDE and 'interval_change_common_window' in CLI_CONTRACT)

print("\n[3] P2-3 SOFR/WALCL 接线(现有 FRED Key,零真实拉取)")
# 3a. 注册表结构: validate_registry 零新增 error;两条目非 core
probs = rs.validate_registry(REG_JSON)
my_errs = [p for p in probs if p.get('severity') == 'error'
           and p.get('metric_id') in ('SOFR', 'WALCL')]
check("注册表 v2.7.0: SOFR/WALCL 条目零结构 error(单位/日历/来源/身份"
      "枚举全过)", not my_errs, str(my_errs[:2]))
check("注册表: 版本号在册(R25 后 v2.8.5;P2-3 变更注记仍在)",
      REG_JSON['version'] == '2.8.5'
      and any('P2-3' in n and 'SOFR' in n for n in REG_JSON['notes']))
core_ids = rp.core_metric_ids()
check("Gate A 语义不变: SOFR/WALCL 为 important 非 core(缺席=noncore_missing"
      "如实披露,不触发 core FAIL)",
      all(REG_BY_ID[m]['criticality'] == 'important' and REG_BY_ID[m]['status'] == 'active'
          for m in ('SOFR', 'WALCL'))
      and not ({'SOFR', 'WALCL'} & set(core_ids)))
check("单位族: SOFR percent→rate(pp 口径)/WALCL million_usd→price(pct 口径,"
      "缩表扩表=水平变化可复算)",
      ia_cli.unit_family(REG_BY_ID['SOFR']['unit'])[0] == 'rate'
      and ia_cli.unit_family(REG_BY_ID['WALCL']['unit'])[0] == 'price')
# 首跑校准锁(2026-11-10真实拉取前校准): FRED WALCL原始单位=百万美元,
# 管线惯例=存原始值+注册表单位描述原始值(RSAFS同例)→量程须为原始值量级,
# 严禁出现"十亿单位标签配百万原始值"的口径错位
_vw = REG_BY_ID['WALCL']['validation']['range']
check("WALCL 单位校准: million_usd+原始值量程(百万级,防十亿/百万口径错位)",
      REG_BY_ID['WALCL']['unit'] == 'million_usd'
      and _vw[0] >= 1000000 and _vw[1] <= 100000000
      and '百万美元' in mc.SERIES_UNITS['WALCL'][1],
      f"unit={REG_BY_ID['WALCL']['unit']} range={_vw}")

# 3b. 采集器接线: 三张映射(独立读表,期望硬编码)
check("macro_collector: FRED_SERIES/SERIES_FREQ/SERIES_UNITS 三表接线"
      "(SOFR=FRED SOFR 日频 rate;WALCL=FRED WALCL 周频 index)",
      mc.FRED_SERIES.get('SOFR') == 'SOFR' and mc.FRED_SERIES.get('WALCL') == 'WALCL'
      and mc.SERIES_FREQ.get('SOFR') == 'daily'
      and mc.SERIES_FREQ.get('WALCL') == 'weekly'
      and mc.SERIES_UNITS.get('SOFR', (None,))[0] == 'rate'
      and mc.SERIES_UNITS.get('WALCL', (None,))[0] == 'index')

# 3c. compute_series_changes 独立期望(合成序列手算)
# SOFR 日频 rate: week_chg=末值−5~10自然日内最近观测(=2026-02-05 的 4.33)
# → +0.03 pp(百分点),**无** week_pct(rate 族不给百分比变化)
sofr_d = ['2026-02-02', '2026-02-03', '2026-02-04', '2026-02-05',
          '2026-02-06', '2026-02-09', '2026-02-10']
sofr_v = [4.30, 4.31, 4.32, 4.33, 4.34, 4.35, 4.36]
sofr_ch = mc.compute_series_changes(sofr_d, sofr_v, 'daily',
                                    unit=mc.SERIES_UNITS['SOFR'])
check("SOFR 变化口径: week_chg=4.36−4.33=+0.03(pp,基准=2026-02-05)"
      "+无百分比变化(rate 族)",
      abs(sofr_ch.get('week_chg', 9) - 0.03) < 1e-9
      and sofr_ch.get('week_chg_from') == '2026-02-05'
      and 'week_pct' not in sofr_ch,
      json.dumps({k: v for k, v in sofr_ch.items() if k.startswith('week')},
                 ensure_ascii=False))
# WALCL 周频 index: week_chg=水平差+week_pct=百分比(独立手算 6600000/6500000;
# 首跑校准后 fixture 用源端原始单位=百万美元,与真实 FRED 返回量级一致)
walcl_d = ['2026-01-21', '2026-01-28', '2026-02-04']
walcl_v = [6400000.0, 6500000.0, 6600000.0]
walcl_ch = mc.compute_series_changes(walcl_d, walcl_v, 'weekly',
                                     unit=mc.SERIES_UNITS['WALCL'])
check("WALCL 变化口径: week_chg=+100000(百万)+week_pct=6600000/6500000−1="
      "+1.5385%",
      abs(walcl_ch.get('week_chg', 9) - 100000.0) < 1e-6
      and abs(walcl_ch.get('week_pct', 9) - (6600000.0 / 6500000.0 - 1) * 100) < 1e-4,
      json.dumps({k: v for k, v in walcl_ch.items() if k.startswith('week')},
                 ensure_ascii=False))

# 3d. normalize_macro 端到端事实生成(fixture 数据形态=采集档 data 节)
MAC_DATA = {
    'data': {
        'SOFR': {'value': 4.36, 'date': '2026-02-10', 'frequency': 'daily',
                 'series': {'dates': sofr_d, 'values': sofr_v}},
        'WALCL': {'value': 6600000.0, 'date': '2026-02-04', 'frequency': 'weekly',
                  'series': {'dates': walcl_d, 'values': walcl_v}},
    }}
facts = fe.normalize_macro(MAC_DATA, '2026-02-10T08:00:00+08:00',
                           'macro_20260210.json')
fmap = {f['metric_id']: f for f in facts}
check("normalize_macro: SOFR/WALCL 事实生成(值/观测日/序列随行/质量非FAIL)",
      'SOFR' in fmap and 'WALCL' in fmap
      and fmap['SOFR']['value'] == 4.36
      and fmap['SOFR']['observation_date'] == '2026-02-10'
      and fmap['WALCL']['value'] == 6600000.0
      and fmap['WALCL']['observation_date'] == '2026-02-04'
      and all(fmap[m]['quality_status'] != 'FAIL' for m in ('SOFR', 'WALCL')),
      str([(f.get('metric_id'), f.get('quality_status'),
            [i.get('message') for i in f.get('issues', [])[:2]]) for f in facts]))
# derived(fact 层,ISO 周口径独立手算): SOFR week pp=4.36−4.34=+0.02;
# WALCL week pct=6600/6500−1=+1.5385(价格族)
check("derived 口径: SOFR week pp_change=+0.02(无 pct)/WALCL week "
      "pct_change=+1.5385",
      abs((fmap['SOFR'].get('derived') or {}).get('week', {})
          .get('pp_change', 9) - 0.02) < 1e-9
      and 'pct_change' not in (fmap['SOFR'].get('derived') or {}).get('week', {})
      and abs((fmap['WALCL'].get('derived') or {}).get('week', {})
              .get('pct_change', 9) - 1.5385) < 1e-3,
      str([(m, (fmap[m].get('derived') or {}).get('week')) for m in ('SOFR', 'WALCL')]))
check("事实身份: 注册表 economy=US+instrument 一致+单位与注册表一致+"
      "来源=macro_collector(economy 在注册表顶层,经 identity_block 贯通输出)",
      all(REG_BY_ID[m].get('economy') == 'US'
          and (fmap[m].get('identity') or {}).get('instrument')
          == REG_BY_ID[m]['identity']['instrument']
          and fmap[m]['unit'] == REG_BY_ID[m]['unit']
          and fmap[m]['source']['collector'] == 'macro_collector'
          for m in ('SOFR', 'WALCL')),
      str(fmap.get('SOFR', {}).get('identity')))

# 3e. Gate A 缺席披露: 接线后未拉取(事实集无 SOFR/WALCL)→ noncore_missing
#     如实列出(诚实过渡态),非静默;来源档在场而指标缺席=采集遗漏 detail
root3 = tempfile.mkdtemp(prefix='c7p2-')
td3 = os.path.join(root3, 'daily')
os.makedirs(td3)
mac3 = json.dumps({'date': '2026-02-10', 'data': {}}, ensure_ascii=False).encode()
open(os.path.join(td3, 'macro_20260210.json'), 'wb').write(mac3)
SS3 = {ch: {'status': 'MISSING'} for ch in
       ('global', 'macro', 'china', 'rate_economy', 'japan', 'jp', 'ea', 'shiller')}
SS3['macro'] = {'status': 'EXACT', 'file': 'macro_20260210.json',
                'file_date': '20260210',
                'sha256': hashlib.sha256(mac3).hexdigest()}


def _gate(facts_list):
    return rp.recompute_gate_a({'facts': facts_list, 'sources_status': SS3,
                                'research_as_of': '2026-02-10T08:00:00+08:00',
                                'target_date': '20260210'},
                               data_dir=td3, trusted_root=root3)


rec_absent = _gate([])
check("缺席披露: 未拉取时 SOFR/WALCL 进 noncore_missing(来源档在场而指标"
      "缺席=采集遗漏)——不静默",
      'SOFR' in rec_absent['noncore_missing']
      and 'WALCL' in rec_absent['noncore_missing']
      and '采集遗漏' in rec_absent['noncore_missing_detail'].get('SOFR', ''),
      str(rec_absent['noncore_missing'][:6]))
rec_present = _gate(facts)
check("在场即除名: 事实在场后 noncore_missing 不再含 SOFR/WALCL",
      not ({'SOFR', 'WALCL'} & set(rec_present['noncore_missing'])),
      str(rec_present['noncore_missing'][:6]))

# 3f. 台账文件在场+红线声明+已实施项登记
LEDGER = os.path.join(ROOT, 'docs', 'P2_DATA_GAP_LEDGER.md')
check("台账: docs/P2_DATA_GAP_LEDGER.md 在场(评估表落点),含红线声明+"
      "SOFR/WALCL 已实施登记+需协调方批准注记",
      os.path.isfile(LEDGER)
      and '不新增任何凭证' in open(LEDGER, encoding='utf-8').read()
      and '需协调方批准' in open(LEDGER, encoding='utf-8').read())

print("\n" + "=" * 72)
print(f"通过 {PASS} / 失败 {FAIL}")
sys.exit(0 if FAIL == 0 else 1)
