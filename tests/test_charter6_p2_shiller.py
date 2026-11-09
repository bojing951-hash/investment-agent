#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Charter6-P2 测试 — Shiller CAPE 采集通道(免 Key 估值维)

覆盖(A2 §2#5/§2#6 + 协调方 Round4 块3规格):
  一、ie_data.xls 解析: 手造二进制 fixture 逐值核对(期望值全部手算,
     不用被测函数算自身答案);TR CAPE 变体列排除;缺月诚实缺席;
     同月重复保留最后;表头容错定位+源版本注记。
  二、日期换算边界: 1871.01→1月/1871.1→10月(浮点尾差)/月份越界/
     非数值/布尔 全部如实拒绝。
  三、P/E 直用列变体: 源带 P/E 列则直用(≠逐行 P÷E 计算值,可证)。
  四、诚实缺席: 无估值列表头→零序列+告警;非 xls 字节→打开失败;
     全序列缺席→不落盘不产空壳(exit 1)。
  五、payload/落盘: flat data+observations+series 全史+source_version。
  六、快照接线 E2E: shiller_ 档→EXACT 来源状态→SPX_CAPE/SPX_PE_TTM
     事实(质量/单位/采集器权属)+series_store lift;缺源→MISSING+
     noncore_missing 如实;SPX_PB(status=unavailable)永不产事实。
  七、下游接入: rhq.load_metric_series 接入点B;workbench 序列能力行;
     retention shiller_ 前缀月度归档。
  八、注册表锁: v2.6.0/106/104活跃/US=52;SPX_PB 不可得登记纪律;
     语义校验零 error 零 review;vintage_additions 25。

数据纪律: 全部 fixture 为 SYNTHETIC 二进制(.xls, dev-only xlwt 预生成
入库;测试只读);零网络零真实数据目录;运行时档案只在临时目录。
运行: ~/AI内容/venv/bin/python3 tests/test_charter6_p2_shiller.py
"""
import gzip
import json
import os
import sys
import tempfile
from datetime import datetime, date

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


FIX1 = os.path.join(ROOT, 'tests', 'fixtures', 'charter6_shiller_min.xls')
FIX2 = os.path.join(ROOT, 'tests', 'fixtures', 'charter6_shiller_pe_col.xls')
FIX3 = os.path.join(ROOT, 'tests', 'fixtures', 'charter6_shiller_nocol.xls')

print("=" * 64)
print("Charter6-P2: Shiller CAPE 采集通道(ie_data.xls,免 Key,月频 1871+)")
print("=" * 64)

import shiller_collector as sc  # noqa: E402

# ══ [1] 主 fixture 解析(手算期望) ═══════════════════════════════
print("\n[1] parse_ie_data(fixture1: 表头容错/TR CAPE排除/缺月/重复月)")
raw1 = open(FIX1, 'rb').read()
series, meta, alerts = sc.parse_ie_data(raw1)

# 手算期望(fixture1 数据行,2023.11-2024.06;2024.04 CAPE 空缺;
# 2024.06 重复行保留最后4760/220/31.9;TR CAPE 列存在但须被排除):
EXP_CAPE_D = ['2023-11-01', '2023-12-01', '2024-01-01', '2024-02-01',
              '2024-03-01', '2024-05-01', '2024-06-01']
EXP_CAPE_V = [30.5, 31.0, 31.5, 31.8, 32.0, 31.5, 31.9]
# P/E=逐行 P÷E(测试独立手算,不调被测代码):
EXP_PE_D = ['2023-11-01', '2023-12-01', '2024-01-01', '2024-02-01',
            '2024-03-01', '2024-04-01', '2024-05-01', '2024-06-01']
EXP_PE_V = [4500 / 190, 4600 / 195, 4700 / 200, 4750 / 205, 4800 / 210,
            4650 / 210, 4700 / 215, 4760 / 220]
check("SPX_CAPE 序列=手算7值(2024.04缺月如实缺席)",
      series.get('SPX_CAPE', {}).get('dates') == EXP_CAPE_D
      and all(abs(a - b) < 1e-9 for a, b in
              zip(series['SPX_CAPE']['values'], EXP_CAPE_V)),
      str(series.get('SPX_CAPE')))
check("SPX_PE_TTM 序列=手算 P÷E 8值(重复月保留最后4760/220)",
      series.get('SPX_PE_TTM', {}).get('dates') == EXP_PE_D
      and all(abs(a - b) < 1e-9 for a, b in
              zip(series['SPX_PE_TTM']['values'], EXP_PE_V)),
      str(series.get('SPX_PE_TTM')))
check("TR CAPE 变体列被排除(表头恰为'cape'才采用)",
      meta['columns_used'].get('CAPE') == 12
      and 31.9 in series['SPX_CAPE']['values'])
check("源版本注记随解析产出(sheet/表头行/首末月)",
      meta['sheet'] == 'Data' and meta['header_row'] == 3
      and meta['first_month'] == '2023-11' and meta['last_month'] == '2024-06',
      str(meta))
check("P/E 采用列=计算口径[P列,E列]",
      meta['columns_used'].get('PE') == [1, 3], str(meta['columns_used']))
check("头部垃圾行告警(前3行内非法日期)",
      len(alerts) == 1 and '非法行跳过' in alerts[0], str(alerts))
check("尾部汇总行静默(仅头部告警,不刷屏)",
      meta['n_rows_scanned'] == 11, str(meta['n_rows_scanned']))  # 垃圾行1+数据9+尾部1

# ══ [2] 日期换算边界 ═════════════════════════════════════════════
print("\n[2] _month_from_shiller_date 边界(YYYY.MM 浮点形态)")
f = sc._month_from_shiller_date
check("1871.01→1月(整数月尾差=0)", f(1871.01) == '1871-01-01', str(f(1871.01)))
check("1871.1→10月(浮点尾差四舍五入吸收)", f(1871.1) == '1871-10-01',
      str(f(1871.1)))
check("2024.06→6月(实册形态)", f(2024.06) == '2024-06-01', str(f(2024.06)))
check("月份越界13→None(不猜)", f(1871.13) is None)
check("月份0(纯年份)→None", f(2024.0) is None)
check("非数值('Avg'汇总行)→None", f('Avg') is None and f(None) is None)
check("布尔(True是int子类)→None", f(True) is None)

# ══ [3] P/E 直用列变体 ═══════════════════════════════════════════
print("\n[3] fixture2: 源带 P/E 列直用(≠逐行计算值)")
series2, meta2, _ = sc.parse_ie_data(open(FIX2, 'rb').read())
check("P/E 直用源列值[25.5,26.0,26.5](若误算P÷E则为25.0等,可证)",
      series2.get('SPX_PE_TTM', {}).get('values') == [25.5, 26.0, 26.5],
      str(series2.get('SPX_PE_TTM')))
check("P/E 采用列=直用列索引(非[P,E]计算形态)",
      meta2['columns_used'].get('PE') == 3, str(meta2['columns_used']))
check("fixture2 SPX_CAPE 同步解析",
      series2.get('SPX_CAPE', {}).get('values') == [31.5, 31.8, 32.0])

# ══ [4] 诚实缺席/失败纪律 ═══════════════════════════════════════
print("\n[4] 诚实缺席与不产空壳")
series3, meta3, alerts3 = sc.parse_ie_data(open(FIX3, 'rb').read())
check("无估值列表头→零序列+告警(不猜不推导)",
      series3 == {} and any('无可用估值列' in a for a in alerts3)
      and meta3.get('header_row') == 3,   # 表头已定位,缺席判定在列面
      str((series3, alerts3)))
sj, mj, aj = sc.parse_ie_data(b'this is not an xls workbook')
check("非 xls 字节→打开失败告警+零序列",
      sj == {} and any('打开失败' in a for a in aj), str(aj))
payload0, n0 = sc.build_payload(run_date=date(2024, 6, 30), raw=b'junk')
check("全序列缺席→n=0且data空(不产空壳)",
      n0 == 0 and payload0['data'] == {} and 'series' not in payload0)
_orig_bp = sc.build_payload
sc.build_payload = lambda **k: (payload0, 0)   # 离线注入失败载荷(零网络)
td0 = tempfile.mkdtemp(prefix='ia_p2_fail_')
rc = sc.main(['--data-dir', td0])
sc.build_payload = _orig_bp
check("main 全序列缺席→exit 1 且不产出文件",
      rc == 1 and not any(x.startswith('shiller_') for x in os.listdir(td0)))

# ══ [5] payload 组装与原子落盘 ══════════════════════════════════
print("\n[5] build_payload + save_daily")
payload, n = sc.build_payload(run_date=date(2024, 6, 30), raw=raw1)
check("n=2(SPX_CAPE+SPX_PE_TTM)", n == 2)
check("flat data=各序列末值(手算: CAPE=31.9, PE=4760/220)",
      abs(payload['data']['SPX_CAPE'] - 31.9) < 1e-9
      and abs(payload['data']['SPX_PE_TTM'] - 4760 / 220) < 1e-9,
      str(payload['data']))
check("observations=统计期月首日口径",
      payload['observations'] == {'SPX_CAPE': '2024-06-01',
                                  'SPX_PE_TTM': '2024-06-01'})
check("series 全史随档落盘(月频1871+口径的离线缩影)",
      len(payload['series']['SPX_CAPE']['dates']) == 7
      and len(payload['series']['SPX_PE_TTM']['dates']) == 8)
check("source_version 源版本注记随档(payload面)",
      payload['source_version'].get('last_month') == '2024-06'
      and payload['source_version'].get('sheet') == 'Data')
check("sources 含 URL 与 latest_vintage_asof_collected 口径注记",
      payload['sources']['SHILLER_IE']['url'] == sc.SHILLER_IE_URL
      and 'latest_vintage_asof_collected' in payload['sources']['SHILLER_IE']['note'])
td1 = tempfile.mkdtemp(prefix='ia_p2_daily_')
p1 = sc.save_daily(td1, payload)
check("save_daily 原子落盘 shiller_20240630.json",
      p1 == os.path.join(td1, 'shiller_20240630.json')
      and os.path.isfile(p1) and not os.path.exists(p1 + '.tmp')
      and json.load(open(p1))['date'] == '20240630')

# ══ [6] 快照接线 E2E ════════════════════════════════════════════
print("\n[6] snapshot_builder 接线(shiller 通道)")
import snapshot_builder as sb  # noqa: E402
import fact_engine as fe  # noqa: E402

AS_OF = '2024-06-30T08:00:00+08:00'
snap = sb.build_snapshot(target_ymd='20240630', data_dir=td1, out_dir=td1,
                         trusted_root=td1, as_of=AS_OF)
st = snap['sources_status'].get('shiller')
check("来源状态 EXACT+文件名披露",
      st and st['status'] == 'EXACT' and st['file'] == 'shiller_20240630.json',
      str(st))
facts = {f['metric_id']: f for f in snap['facts']}
cape = facts.get('SPX_CAPE')
check("SPX_CAPE 事实在场(值/单位/观测期)",
      cape and abs(cape['value'] - 31.9) < 1e-9 and cape['unit'] == 'ratio'
      and cape['observation_date'] == '2024-06-01', str(cape and cape['value']))
check("采集器权属=shiller_collector(与 registry source 同符号)",
      cape and cape.get('source', {}).get('collector') == 'shiller_collector')
# 质量=WARN(诚实披露): registry 明示 release_date_available=false
# (ie_data.xls 无逐版发布日)→ RELEASE_UNKNOWN 点时可得性未认证告警,
# 值域/时效均过——与 japan/ea 通道同款纪律(WARN 不掩成 PASS)。
check("质量=WARN(仅release未认证告警;值域时效均过)",
      cape and cape.get('quality_status') == 'WARN'
      and all(i['category'] == 'release' for i in cape['issues'])
      and all(i['severity'] == 'WARN' for i in cape['issues']),
      str(cape and cape.get('issues')))
pe = facts.get('SPX_PE_TTM')
check("SPX_PE_TTM 事实在场且质量WARN(同款release披露)",
      pe and abs(pe['value'] - 4760 / 220) < 1e-9
      and pe.get('quality_status') == 'WARN')
check("series_store lift 全史(CAPE7点/PE8点,首点2023-11)",
      len((snap['series_store'].get('SPX_CAPE') or {}).get('dates', [])) == 7
      and snap['series_store']['SPX_CAPE']['dates'][0] == '2023-11-01'
      and len((snap['series_store'].get('SPX_PE_TTM') or {}).get('dates', [])) == 8)
check("SPX_PB 永不产事实(status=unavailable,宁缺毋假)",
      'SPX_PB' not in facts and 'SPX_PB' not in snap['series_store'])

# 缺源场景: 空目录→MISSING+noncore_missing 如实(不填0)
td2 = tempfile.mkdtemp(prefix='ia_p2_empty_')
snap2 = sb.build_snapshot(target_ymd='20240630', data_dir=td2, out_dir=td2,
                          trusted_root=td2, as_of=AS_OF)
check("缺源→sources_status.shiller=MISSING",
      (snap2['sources_status'].get('shiller') or {}).get('status') == 'MISSING')
nm = snap2['gate_a'].get('noncore_missing') or []
check("缺源→SPX_CAPE/SPX_PE_TTM 进 noncore_missing 如实",
      'SPX_CAPE' in nm and 'SPX_PE_TTM' in nm, str(nm[:5]))
check("SPX_PB(unavailable)不进缺失清单(Gate A 零消费)",
      'SPX_PB' not in nm)

# ══ [7] 下游接入 ════════════════════════════════════════════════
print("\n[7] 下游: rhq 接入点B / workbench 序列能力 / retention")
import research_history_query as rhq  # noqa: E402
r = rhq.load_metric_series('SPX_CAPE', '20240630', as_of=AS_OF,
                           data_dir=td1, trusted_root=td1)
check("rhq.load_metric_series(SPX_CAPE) 经快照 store 取全史",
      len(r['dates']) == 7 and abs(r['values'][-1] - 31.9) < 1e-9
      and r['observation_date'] == '2024-06-01', str(r.get('dates')))
check("接入点披露=快照序列面(shiller)",
      'shiller' in r['source']['access_point'], r['source']['access_point'])
check("quality_status 透传事实层(WARN如实)", r['quality_status'] == 'WARN')
try:
    rhq.load_metric_series('SPX_PB', '20240630', data_dir=td1, trusted_root=td1)
    pb_err = ''
except ValueError as e:
    pb_err = str(e)
check("SPX_PB 查询被注册表层拒绝(不可得指标无序列接入)",
      pb_err == '' or 'SPX_PB' in pb_err, pb_err)

import workbench_data as wd  # noqa: E402
reg = fe.load_registry()
rows = {x['metric_id']: x for x in wd.series_capable_metrics(
    {'facts': snap['facts'], 'series_store': snap['series_store']}, reg)}
row = rows.get('SPX_CAPE')
check("workbench 序列能力行在场(月频/首末月/n=7)",
      row and row.get('frequency') == 'monthly'
      and row.get('n') == 7 and row.get('first') == '2023-11-01', str(row))
check("序列能力行含 time_semantics(月度统计期)与质量透传",
      (row.get('time_semantics') or {}).get('observation_period_kind')
      == 'calendar_month' and row.get('quality_status') == 'WARN', str(row))
check("SPX_PB 不在序列能力面(无序列即无行)", 'SPX_PB' not in rows)

import data_retention as dr  # noqa: E402
tdr = tempfile.mkdtemp(prefix='ia_p2_ret_')
os.makedirs(os.path.join(tdr, 'archive'))
for name in ('shiller_20250301.json', 'shiller_20250331.json',
             'shiller_20261015.json'):
    with open(os.path.join(tdr, name), 'w', encoding='utf-8') as fh:
        fh.write('{"stub": 1}')
rep = dr.prune_daily_archives(tdr, keep_days=90, now=datetime(2026, 11, 9))
check("retention: shiller_ 近窗保留(20261015 距今25天)",
      'shiller_20261015.json' in rep['kept'], str(rep['kept']))
check("retention: shiller_ 月度代表归档(20250331)+非代表删除(20250301)",
      'shiller_20250331.json' in rep['archived']
      and 'shiller_20250301.json' in rep['deleted'],
      str((rep['archived'], rep['deleted'])))
check("retention: 归档为 gzip(月度档案)",
      os.path.isfile(os.path.join(tdr, 'archive', 'shiller_20250331.json.gz')))

# ══ [8] 注册表锁 ════════════════════════════════════════════════
print("\n[8] 注册表锁(v2.6.0)与语义校验")
regj = json.load(open(os.path.join(ROOT, 'config', 'metric_registry.json'),
                      encoding='utf-8'))
ms = regj['metrics']
check("版本 v2.6.0(Charter6-P2)", regj.get('version') == '2.6.0')
check("106项(103+CAPE/PE_TTM/PB)", len(ms) == 106, str(len(ms)))
active = [m for m in ms if m.get('status') == 'active']
check("活跃104项", len(active) == 104, str(len(active)))
us = [m for m in active if m.get('economy') == 'US']
check("US 活跃51项(SPX_PB=unavailable不计入)", len(us) == 51, str(len(us)))
pb = next(m for m in ms if m['metric_id'] == 'SPX_PB')
check("SPX_PB=unavailable 登记(宁缺毋假,不以proxy冒充)",
      pb.get('status') == 'unavailable' and 'proxy' in pb.get('calc', '')
      and 'unavailable' in pb.get('calc', ''), pb.get('status'))
check("SPX_PB 无观测即无统计期(时间键未登记)",
      'observation_period_kind' not in pb and 'release_date_available' not in pb)
check("SPX_PB release_semantics 留空(无发布可谈)",
      not pb.get('release_semantics'))
for mid, sym in (('SPX_CAPE', 'ie_data.xls!CAPE'),
                 ('SPX_PE_TTM', 'ie_data.xls!P/E')):
    m = next(x for x in ms if x['metric_id'] == mid)
    check(f"{mid}: source=shiller_collector/月频/calendar_month/US",
          m['source'] == 'shiller_collector' and m['frequency'] == 'monthly'
          and m['observation_period_kind'] == 'calendar_month'
          and m['economy'] == 'US', str(m.get('source')))
    check(f"{mid}: source_symbol={sym}", m.get('source_symbol') == sym)
    check(f"{mid}: release_semantics 披露最新修订口径",
          'latest_vintage_asof_collected' in m.get('release_semantics', ''))
import registry_semantics as rsem  # noqa: E402
check("语义词汇表: unavailable 状态+shiller_collector 源",
      'unavailable' in rsem.STATUS_VALUES
      and 'shiller_collector' in rsem.KNOWN_SOURCES)
res = rsem.validate_registry(regj)
errs = [x for x in res if x.get('severity') == 'error']
revs = [x for x in res if x.get('severity') == 'review']
check("registry_semantics 校验零 error", errs == [], str(errs[:3]))
check("registry_semantics 校验零 review", revs == [], str(revs[:3]))
import research_provenance as rp  # noqa: E402
check("SOURCE_FILE_RULES['shiller']=前缀+35日回退窗(月度节奏)",
      rp.SOURCE_FILE_RULES.get('shiller') == {'prefix': 'shiller_',
                                              'max_fallback_days': 35})
check("_SOURCE_TO_INPUT 映射 shiller_collector→shiller",
      rp._SOURCE_TO_INPUT.get('shiller_collector') == 'shiller')
sys.path.insert(0, os.path.join(ROOT, 'tests'))
from helpers import baseline_locks as bl  # noqa: E402
va = bl.vintage_additions(fe.load_registry())
check("vintage_additions=25(含新4项;unavailable同属时点后新增)",
      len(va) == 25 and {'SPX_CAPE', 'SPX_PE_TTM', 'SPX_PB',
                         'US_REAL_GDP'} <= va, str(sorted(va)))

print("\n" + "=" * 64)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 64)
sys.exit(0 if FAIL == 0 else 1)
