#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R12(autonomous-rd 2026-11-12): japan 通道 source_key 补接验收套件。

背景(R11 独立审计 MINOR;docs/autonomous-rd/RESUME.md R12 候选①):
  R11 接线 7 条 source_key 时 japan 通道 4 指标(JP_POLICY_RATE/JGB2Y/
  JGB5Y/JGB10Y)未接——japan_rate_collector 日档**不持久化**子源级
  sources_status(失败仅 alerts 字符串),兜底文案"档内无该指标子源状态
  记录"在「注册表缺映射」「纯重验未读档」两种断点下失准(未读档却归咎
  档内)。jp_market_collector 档内实有 MOF_JGBCME/FRED_POLICY 键
  (与 japan 采集器同上游 URL),词汇可对齐。
  R12=①japan_rate_collector 顶层增子源级 sources_status(键 MOF_JGBCME/
  FRED_POLICY 对齐 jp 采集器词汇;EXACT=取数解析出有效观测/READ_FAIL=
  获取或整体解析失败;列级坏值仍 EXACT 由 alerts 披露;旧档无该节不受
  影响)+②registry v2.8.4 接线 4 条+③recompute 兜底话术按证据链断点
  三分支归因(注册表未登记键/未提供 data_dir/档内无记录)。
  契约不变: noncore_missing 成员/Gate 状态判定/门核验链零变动(纯话术层)。

被测对象: scripts/japan_rate_collector.py R12 增量(build_payload
sources_status 节)、scripts/research_provenance.py(_missing_reason_file_present
三分支归因)、config/metric_registry.json v2.8.4(4 条 source_key)。

数据纪律: 全部离线合成 fixture(采集器面=离线 raw 注入/网络失败 mock,
结构镜像源端真实形态,锚定值复刻 B3 套件常量);零网络零 skip;预期值
字面量硬编码(禁自证恒真)。

锁清单:
[1] 采集器落盘面: 双源成功→sources_status 双 EXACT+遗留字段零变动;
    MOF 网络失败→MOF_JGBCME=READ_FAIL+JGB 键缺席+FRED 不受影响;
    FRED 失败→FRED_POLICY=READ_FAIL+series 节不出现;全失败→n=0 不落盘
    语义+payload 双 READ_FAIL;列级坏值→MOF_JGBCME 仍 EXACT+alerts 披露
[2] 注册表面: v2.8.4/source_key 11 条精确值(japan 4 条键=MOF_JGBCME/
    FRED_POLICY 与 jp 档词汇一致)/110 条/108 active 不变/rsem 零问题
[3] 集成面: japan 档变异(子源 READ_FAIL+JGB 三键缺席)→快照→重算
    →JGB 入 noncore_missing 注记=子源缺席(japan 档记录);
    JP_POLICY_RATE 在场不入清单
[4] 兜底话术三分支归因: 无 source_key→注册表变体/有键无 data_dir→
    未提供采集目录变体/有键有 data_dir 老档(无 sources_status 节)→
    档内无记录变体
[5] 契约锁: 清单成员/Gate 状态/门核验零变动(对照控制快照,纯话术层)
[6] 渲染面: 快照 MD 非核心缺失节含 JGB 子源缺席行
"""
import json
import os
import re
import sys
import tempfile
import unittest.mock as mock
from datetime import date

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
for p in (ROOT, os.path.join(ROOT, 'scripts')):
    if p not in sys.path:
        sys.path.insert(0, p)

import fixt                                    # noqa: E402
import japan_rate_collector as jrc             # noqa: E402
import registry_semantics as rsem              # noqa: E402
import research_provenance as rp               # noqa: E402
import snapshot_builder as sb                  # noqa: E402

PASS, FAIL = 0, 0

YMD = '20261106'   # 与 R11/WP-B 套件同日(周五,obs=周四)
TS_RE = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$')

# 兜底话术三分支(R12 归因精确化;均"采集遗漏或子源缺席不可区分"语义)
HEDGE_NO_KEY = ('来源文件在场而指标缺席(采集遗漏或子源缺席'
                '——注册表未登记该指标子源状态键,不可区分)')
HEDGE_NO_DIR = ('来源文件在场而指标缺席(采集遗漏或子源缺席'
                '——未提供采集目录,子源状态证据不可核,不可区分)')
HEDGE_NO_REC = ('来源文件在场而指标缺席(采集遗漏或子源缺席'
                '——档内无该指标子源状态记录,不可区分)')

# ---- 采集器离线 fixture(锚定值复刻 test_p03_e2eb_b3 常量;结构镜像源端) ----
MOF_BYTES = (
    '2026年11月 中途経過\r\n'
    'Date,1Y,2Y,3Y,4Y,5Y,10Y,20Y,30Y,40Y\r\n'
    '2026/11/2,0.50,1.880,1.990,2.100,2.250,2.840,3.10,3.20,3.30\r\n'
    '2026/11/4,0.51,1.891,2.000,2.110,2.269,2.855,3.11,3.21,3.31\r\n'
    '※末尾コメント行\r\n'
).encode('shift_jis')
MOF_BYTES_10Y_CORRUPT = (
    'Date,1Y,2Y,5Y,10Y\r\n'
    '2026/11/4,0.51,1.891,2.269,XX\r\n'
).encode('shift_jis')
FRED_BYTES = (
    'observation_date,IRSTCI01JPM156N\r\n'
    '2026-07-01,0.860\r\n'
    '2026-08-01,.\r\n'
    '2026-09-01,1.043\r\n'
).encode('utf-8')


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")


def _build(root, japan_mutate=None, missing=()):
    """写全通道采集档(japan 可变异)→真实构建快照→(snap, daily_dir)。"""
    daily = os.path.join(root, 'data', 'daily')
    os.makedirs(daily, exist_ok=True)
    payloads = fixt.collector_payloads(YMD, fixt.obs_for(YMD), missing=missing)
    if japan_mutate is not None:
        japan_mutate(payloads['japan'])
    for name, obj in payloads.items():
        with open(os.path.join(daily, f"{name}_{YMD}.json"), 'w',
                  encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False)
    snap = sb.build_snapshot(target_ymd=YMD, data_dir=daily, out_dir=daily,
                             trusted_root=root, as_of=fixt.as_of_for(YMD))
    return snap, daily


def _jp_mof_readfail(japan):
    """japan 档变异: R12 采集器失败纪律镜像——子源 MOF_JGBCME=READ_FAIL
    +JGB 三系列键不出现(源失败→节键不出现),JP_POLICY_RATE 不受影响。"""
    japan['sources_status'] = {
        'MOF_JGBCME': {'status': 'READ_FAIL', 'retrieved_at': None},
        'FRED_POLICY': {'status': 'EXACT',
                        'retrieved_at': '2026-11-06T16:00:00Z'}}
    for mid in ('JGB2Y', 'JGB5Y', 'JGB10Y'):
        japan['data'].pop(mid, None)
        japan['observations'].pop(mid, None)


def _jp_jgb_absent_legacy(japan):
    """japan 老档形态(改造前,R12 前历史档): 无 sources_status 节,
    JGB 三系列缺席(子源失败时仅 data 键不出现,无子源状态可查)。"""
    for mid in ('JGB2Y', 'JGB5Y', 'JGB10Y'):
        japan['data'].pop(mid, None)
        japan['observations'].pop(mid, None)
    japan.pop('sources_status', None)


# ══ [1] 采集器落盘面(sources_status 子源级状态) ═════════════════════
print("\n[1] japan_rate_collector 顶层 sources_status(键词汇对齐 jp 采集器)")
payload, n = jrc.build_payload(run_date=date(2026, 11, 6),
                               mof_raw=MOF_BYTES, fred_raw=FRED_BYTES)
check("双源成功→n=4 且 data/observations 遗留契约零变动",
      n == 4 and set(payload['data']) == {'JGB2Y', 'JGB5Y', 'JGB10Y',
                                          'JP_POLICY_RATE'}
      and set(payload['observations']) == set(payload['data']),
      (n, sorted(payload['data'])))
ss = payload.get('sources_status')
check("sources_status 双 EXACT(键=MOF_JGBCME/FRED_POLICY,与 jp 档词汇一致)",
      isinstance(ss, dict)
      and ss.get('MOF_JGBCME', {}).get('status') == 'EXACT'
      and ss.get('FRED_POLICY', {}).get('status') == 'EXACT', ss)
check("retrieved_at 形态=ISO8601 UTC(尝试时刻,见模块 docstring 语义)",
      all(TS_RE.match((ss.get(k) or {}).get('retrieved_at') or '')
          for k in ('MOF_JGBCME', 'FRED_POLICY')), ss)
check("遗留顶层字段零变动(date/sources/fetched_at/alerts/series)",
      payload['date'] == '20261106'
      and 'mof.go.jp' in payload['sources']['JGB']['url']
      and TS_RE.match(payload['fetched_at'])
      and payload['alerts'] == []
      and 'JP_POLICY_RATE' in (payload.get('series') or {}))


def _fail(src_fail):
    def _f(url, src='mof'):
        if src == src_fail:
            raise OSError('synthetic outage')
        return MOF_BYTES if src == 'mof' else FRED_BYTES
    return _f


with mock.patch.object(jrc, '_http_get', side_effect=_fail('mof')):
    p2, n2 = jrc.build_payload(run_date=date(2026, 11, 6))
check("MOF 网络失败→MOF_JGBCME=READ_FAIL+JGB 键缺席(单源失败不阻断另源)",
      n2 == 1 and list(p2['data']) == ['JP_POLICY_RATE']
      and p2['sources_status']['MOF_JGBCME']['status'] == 'READ_FAIL'
      and p2['sources_status']['FRED_POLICY']['status'] == 'EXACT',
      (n2, p2.get('sources_status')))
with mock.patch.object(jrc, '_http_get', side_effect=_fail('fred')):
    p3, n3 = jrc.build_payload(run_date=date(2026, 11, 6))
check("FRED 失败→FRED_POLICY=READ_FAIL+series 节不出现",
      n3 == 3 and 'series' not in p3
      and p3['sources_status']['FRED_POLICY']['status'] == 'READ_FAIL'
      and p3['sources_status']['MOF_JGBCME']['status'] == 'EXACT',
      (n3, p3.get('sources_status')))
with mock.patch.object(jrc, '_http_get',
                       side_effect=OSError('synthetic net down')):
    p4, n4 = jrc.build_payload(run_date=date(2026, 11, 6))
check("全失败→n=0(不落盘语义不变)+payload 子源状态如实双 READ_FAIL",
      n4 == 0
      and p4['sources_status']['MOF_JGBCME']['status'] == 'READ_FAIL'
      and p4['sources_status']['FRED_POLICY']['status'] == 'READ_FAIL',
      (n4, p4.get('sources_status')))
p5, n5 = jrc.build_payload(run_date=date(2026, 11, 6),
                           mof_raw=MOF_BYTES_10Y_CORRUPT, fred_raw=FRED_BYTES)
check("列级坏值(10Y=XX)→MOF_JGBCME 仍 EXACT(源已取到),列级缺席由 alerts 披露",
      n5 == 3 and 'JGB10Y' not in p5['data']
      and p5['sources_status']['MOF_JGBCME']['status'] == 'EXACT'
      and any('10Y' in a for a in p5['alerts']),
      (n5, p5.get('sources_status'), p5.get('alerts')))

# ══ [2] 注册表面 ═════════════════════════════════════════════════════
print("\n[2] 注册表 v2.8.4(japan 通道 4 条 source_key 接线)")
REG_PATH = os.path.join(ROOT, 'config', 'metric_registry.json')
with open(REG_PATH, encoding='utf-8') as f:
    REG = json.load(f)
check("版本 v2.8.4", REG['version'] == '2.8.4', REG['version'])
SKEY_EXPECT = {
    'ECB_DFR': 'ECB_FM_DFR', 'ECB_MRO': 'ECB_FM_MRO',
    'BUND_10Y': 'BBK_WU3146', 'BUND_2Y': 'BBK_WU3141',
    'EA_HICP_YOY': 'ECB_ICP_HICP',
    'JP_CPI_TOKYO_YOY': 'JP_CPI_TOKYO', 'NIKKEI225': 'FRED_NIKKEI225',
    'JP_POLICY_RATE': 'FRED_POLICY',
    'JGB2Y': 'MOF_JGBCME', 'JGB5Y': 'MOF_JGBCME', 'JGB10Y': 'MOF_JGBCME'}
got = {m['metric_id']: m.get('source_key') for m in REG['metrics']
       if m.get('source_key')}
check("source_key 11 条精确值(R11 7条+japan 4条;JGB 三期限共键 MOF_JGBCME)",
      got == SKEY_EXPECT, got)
check("指标集零变动: 110 条/108 active",
      len(REG['metrics']) == 110
      and sum(1 for m in REG['metrics'] if m.get('status') == 'active') == 108)
probs = rsem.validate_registry(REG)
check("registry_semantics 校验零问题", not probs, str(probs)[:120])
fs_txt = REG.get('field_semantics', {}).get('source_key', '')
check("field_semantics 词汇面已含 japan 档键(MOF_JGBCME/FRED_POLICY)",
      'MOF_JGBCME' in fs_txt and 'FRED_POLICY' in fs_txt, fs_txt[:80])

# ══ [3] 集成面: 子源分类触达 japan 通道 ═════════════════════════════
print("\n[3] japan 通道子源缺席分类(READ_FAIL,MOF 断连主场景)")
with tempfile.TemporaryDirectory() as td:
    snap, daily = _build(td, japan_mutate=_jp_mof_readfail)
    rec = rp.recompute_gate_a(snap, data_dir=daily, trusted_root=td)
    check("JGB 三期限入 noncore_missing",
          {'JGB2Y', 'JGB5Y', 'JGB10Y'} <= set(rec['noncore_missing']),
          rec['noncore_missing'][:8])
    check("注记=子源缺席(japan 档记录:MOF_JGBCME=READ_FAIL,非采集遗漏)",
          rec['noncore_missing_detail'].get('JGB10Y')
          == '子源缺席(japan档记录:MOF_JGBCME=READ_FAIL'
             '——源端不可得/未采,非采集遗漏)',
          rec['noncore_missing_detail'].get('JGB10Y'))
    check("同档在场 JP_POLICY_RATE 不误伤(不在缺失清单)",
          'JP_POLICY_RATE' not in rec['noncore_missing'])
    check("构建期注记同口径(快照 gate_a 直存子源缺席)",
          snap['gate_a']['noncore_missing_detail'].get('JGB10Y')
          == rec['noncore_missing_detail'].get('JGB10Y'))

# ══ [4] 兜底话术三分支归因(证据链断点精确化) ═══════════════════════
print("\n[4] 兜底三分支: 注册表未登记键/未提供采集目录/档内无记录")
with tempfile.TemporaryDirectory() as td:
    snap, daily = _build(td, missing=('INDPRO',))   # macro 通道无 source_key
    rec = rp.recompute_gate_a(snap, data_dir=daily, trusted_root=td)
    check("无 source_key 指标(INDPRO,macro)→注册表未登记键变体",
          rec['noncore_missing_detail'].get('INDPRO') == HEDGE_NO_KEY,
          rec['noncore_missing_detail'].get('INDPRO'))
with tempfile.TemporaryDirectory() as td:
    snap, daily = _build(td, japan_mutate=_jp_mof_readfail)
    rec_pure = rp.recompute_gate_a(snap)            # 纯重验: 无 data_dir
    check("有 source_key+无 data_dir(JGB10Y 纯重验)→未提供采集目录变体",
          rec_pure['noncore_missing_detail'].get('JGB10Y') == HEDGE_NO_DIR,
          rec_pure['noncore_missing_detail'].get('JGB10Y'))
with tempfile.TemporaryDirectory() as td:
    snap, daily = _build(td, japan_mutate=_jp_jgb_absent_legacy)
    rec = rp.recompute_gate_a(snap, data_dir=daily, trusted_root=td)
    check("有 source_key+老 japan 档(无 sources_status 节)→档内无记录变体",
          rec['noncore_missing_detail'].get('JGB2Y') == HEDGE_NO_REC,
          rec['noncore_missing_detail'].get('JGB2Y'))

# ══ [5] 契约锁: 清单成员/Gate 判定零变动 ═════════════════════════════
print("\n[5] 契约锁(纯话术层: 成员/状态/门核验零变动)")
with tempfile.TemporaryDirectory() as td_c, tempfile.TemporaryDirectory() as td_m:
    ctrl, daily_c = _build(td_c)                    # 未变异: JGB 三期限在场
    mut, daily_m = _build(td_m, japan_mutate=_jp_mof_readfail)
    rc = rp.recompute_gate_a(ctrl, data_dir=daily_c, trusted_root=td_c)
    rm = rp.recompute_gate_a(mut, data_dir=daily_m, trusted_root=td_m)
    check("缺失清单差集恰为 JGB 三期限(成员判定不受话术影响)",
          set(rm['noncore_missing']) == set(rc['noncore_missing'])
          | {'JGB2Y', 'JGB5Y', 'JGB10Y'},
          f"ctrl={sorted(rc['noncore_missing'])[:6]} "
          f"mut={sorted(rm['noncore_missing'])[:6]}")
    check("core_missing 零变动", rm['core_missing'] == rc['core_missing'] == [])
    check("effective 零变动(均 DEGRADED)",
          rm['effective'] == rc['effective'] == 'DEGRADED',
          f"{rc['effective']}→{rm['effective']}")
    st_decl, why = rp.gate_status(mut, data_dir=daily_m, trusted_root=td_m)
    check("声明↔重算一致性核验通过(子源话术不破坏门链)",
          st_decl == 'DEGRADED', f"{st_decl}:{why}")

# ══ [6] 渲染面: 快照 MD 非核心缺失节 ═══════════════════════════════
print("\n[6] 快照 MD 渲染(人读面含 JGB 子源缺席行)")
with tempfile.TemporaryDirectory() as td:
    snap, daily = _build(td, japan_mutate=_jp_mof_readfail)
    md_path = os.path.join(daily, f"research_snapshot_{YMD}.md")
    with open(md_path, encoding='utf-8') as f:
        md = f.read()
    check("MD 非核心缺失节含 JGB10Y 子源缺席行",
          ('- JGB10Y: 子源缺席(japan档记录:MOF_JGBCME=READ_FAIL'
           '——源端不可得/未采,非采集遗漏)') in md)

# ══ 汇总 ═════════════════════════════════════════════════════════════
print(f"\n{'='*60}")
print(f"R12 japan 通道 source_key 补接: {PASS} PASS / {FAIL} FAIL")
sys.exit(0 if FAIL == 0 else 1)
