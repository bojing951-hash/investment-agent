#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R11(autonomous-rd 2026-11-12): noncore_missing 子源级注记细化验收套件。

背景(P2台账 R10 候选①;docs/autonomous-rd/RESUME.md R11 候选①):
  Gate A noncore_missing 注记「来源文件在场而指标缺席(采集遗漏)」为文件级
  泛化文案——BBK 源站断连(READ_FAIL)/白名单域未采(MISSING)这类**诚实子源
  缺席**被误标"采集遗漏"。ea/jp 采集器日档已持久化子源级 sources_status
  (ea_*.json/jp_*.json 顶层 sources_status 节),信息在档而引擎未用。
  R11=注册表 v2.8.3 新增可选字段 source_key(指标→子源状态键,接线 7 条)+
  recompute_gate_a 分类: 子源非 EXACT=子源缺席(源端不可得/未采,非采集遗漏)
  /子源 EXACT 而指标缺席=采集遗漏/证据不可得=采集遗漏或子源缺席不可区分
  (诚实兜底,不再无证据断言"采集遗漏")。

被测对象: scripts/research_provenance.py R11 增量
  (_channel_subsource_map/_missing_reason_file_present + FIX4-03 分支接线)
  与 config/metric_registry.json v2.8.3(source_key 字段)。

数据纪律: 全部离线合成 fixture(tests/fixt.py 通道 payload 镜像真实采集器
产出形态,含子源 sources_status 节);零网络零 skip;预期值字面量硬编码
(禁自证恒真)。

锁清单:
[1] 注册表面: v2.8.4(锁随升,R12 japan 4 条接线)/source_key 11 条精确值
    /field_semantics 定义/108 active 不变/registry_semantics 校验零 error
[2] 子源 READ_FAIL→子源缺席(BBK 断连主场景)+jp 白名单域 MISSING→子源缺席
    (未变异 fixture 自带)+同档在场指标不受影响
[3] 子源 EXACT 而指标缺席→采集遗漏(采集器已取到而事实未生成)
[4] 证据不可得→诚实兜底(纯重验无 data_dir;macro 通道档内无子源记录)
[5] 契约锁: 清单成员/Gate 状态/门核验零变动(对照控制快照,纯话术层)
[6] _channel_subsource_map 单元面: sha256 失配/档内无节/无 file/缓存命中
[7] 渲染面: 快照 MD 非核心缺失节含子源缺席行
"""
import json
import os
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
for p in (ROOT, os.path.join(ROOT, 'scripts')):
    if p not in sys.path:
        sys.path.insert(0, p)

import fixt                                    # noqa: E402
import registry_semantics as rsem              # noqa: E402
import research_provenance as rp               # noqa: E402
import snapshot_builder as sb                  # noqa: E402

PASS, FAIL = 0, 0

YMD = '20261106'   # 与 test_p1_gap08 同日(周五,obs=周四)
# 兜底话术(R12 起按证据链断点三分支归因,语义均"不可区分"):
HEDGE_NO_DIR = ('来源文件在场而指标缺席(采集遗漏或子源缺席'
                '——未提供采集目录,子源状态证据不可核,不可区分)')
HEDGE_NO_KEY = ('来源文件在场而指标缺席(采集遗漏或子源缺席'
                '——注册表未登记该指标子源状态键,不可区分)')


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")


def _build(root, ea_mutate=None, missing=()):
    """写全通道采集档(ea 可变异)→真实构建快照→(snap, daily_dir)。"""
    daily = os.path.join(root, 'data', 'daily')
    os.makedirs(daily, exist_ok=True)
    payloads = fixt.collector_payloads(YMD, fixt.obs_for(YMD), missing=missing)
    if ea_mutate is not None:
        ea_mutate(payloads['ea'])
    for name, obj in payloads.items():
        with open(os.path.join(daily, f"{name}_{YMD}.json"), 'w',
                  encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False)
    snap = sb.build_snapshot(target_ymd=YMD, data_dir=daily, out_dir=daily,
                             trusted_root=root, as_of=fixt.as_of_for(YMD))
    return snap, daily


def _drop_bund10y_readfail(ea):
    """BBK 断连场景: 子源 READ_FAIL + bund 节 BUND_10Y 键不出现(镜像真实
    采集器失败纪律: 源失败→节键不出现+sources_status READ_FAIL)。"""
    ea['sources_status']['BBK_WU3146'] = {'status': 'READ_FAIL',
                                          'retrieved_at': None}
    ea['bund'].pop('BUND_10Y')
    ea['observations'].pop('BUND_10Y', None)


def _drop_bund10y_sub_ok(ea):
    """子源成功而指标缺席场景: BBK_WU3146 保持 EXACT 但 bund 节键不出现
    (采集器已取到而事实未生成=真采集遗漏)。"""
    ea['bund'].pop('BUND_10Y')
    ea['observations'].pop('BUND_10Y', None)


# ══ [1] 注册表面 ═════════════════════════════════════════════════════
print("\n[1] 注册表(source_key 可选字段;锁随升 v2.8.4/R11 7条+japan 4条)")
REG_PATH = os.path.join(ROOT, 'config', 'metric_registry.json')
with open(REG_PATH, encoding='utf-8') as f:
    REG = json.load(f)
check("版本 v2.8.4(R12 japan 补接;R11 落位时为 2.8.3)", REG['version'] == '2.8.4',
      REG['version'])
SKEY_EXPECT = {
    'ECB_DFR': 'ECB_FM_DFR', 'ECB_MRO': 'ECB_FM_MRO',
    'BUND_10Y': 'BBK_WU3146', 'BUND_2Y': 'BBK_WU3141',
    'EA_HICP_YOY': 'ECB_ICP_HICP',
    'JP_CPI_TOKYO_YOY': 'JP_CPI_TOKYO', 'NIKKEI225': 'FRED_NIKKEI225',
    'JP_POLICY_RATE': 'FRED_POLICY',
    'JGB2Y': 'MOF_JGBCME', 'JGB5Y': 'MOF_JGBCME', 'JGB10Y': 'MOF_JGBCME'}
got = {m['metric_id']: m.get('source_key') for m in REG['metrics']
       if m.get('source_key')}
check("source_key 11 条精确值(与 ea/jp/japan 采集器档内 sources_status 键一致)",
      got == SKEY_EXPECT, got)
check("field_semantics 含 source_key 定义",
      isinstance(REG.get('field_semantics', {}).get('source_key'), str)
      and '子源' in REG['field_semantics']['source_key'])
check("指标集零变动: 110 条/108 active",
      len(REG['metrics']) == 110
      and sum(1 for m in REG['metrics'] if m.get('status') == 'active') == 108)
probs = rsem.validate_registry(REG)
check("registry_semantics 校验零问题(source_key 新字段不破坏封闭词汇校验)",
      not probs, str(probs)[:120])

# ══ [2] 子源 READ_FAIL/MISSING → 子源缺席 ═══════════════════════════
print("\n[2] 子源缺席分类(BBK 断连 READ_FAIL + jp 白名单域 MISSING)")
with tempfile.TemporaryDirectory() as td:
    snap, daily = _build(td, ea_mutate=_drop_bund10y_readfail)
    rec = rp.recompute_gate_a(snap, data_dir=daily, trusted_root=td)
    check("BUND_10Y 入 noncore_missing", 'BUND_10Y' in rec['noncore_missing'],
          rec['noncore_missing'][:8])
    check("重算注记=子源缺席(READ_FAIL,非采集遗漏)",
          rec['noncore_missing_detail'].get('BUND_10Y')
          == '子源缺席(ea档记录:BBK_WU3146=READ_FAIL——源端不可得/未采,非采集遗漏)',
          rec['noncore_missing_detail'].get('BUND_10Y'))
    check("同档在场 BUND_2Y 不误伤(不在缺失清单)",
          'BUND_2Y' not in rec['noncore_missing'])
    check("jp 白名单域缺席 JP_CPI_TOKYO_YOY=子源缺席(MISSING)",
          rec['noncore_missing_detail'].get('JP_CPI_TOKYO_YOY')
          == '子源缺席(jp档记录:JP_CPI_TOKYO=MISSING——源端不可得/未采,非采集遗漏)',
          rec['noncore_missing_detail'].get('JP_CPI_TOKYO_YOY'))
    check("构建期注记同口径(快照 gate_a 直存子源缺席)",
          snap['gate_a']['noncore_missing_detail'].get('BUND_10Y')
          == rec['noncore_missing_detail'].get('BUND_10Y'))

# ══ [3] 子源 EXACT 而指标缺席 → 采集遗漏 ═══════════════════════════
print("\n[3] 子源成功而指标缺席=采集遗漏")
with tempfile.TemporaryDirectory() as td:
    snap, daily = _build(td, ea_mutate=_drop_bund10y_sub_ok)
    rec = rp.recompute_gate_a(snap, data_dir=daily, trusted_root=td)
    check("注记=采集遗漏(采集器已取到而事实未生成)",
          rec['noncore_missing_detail'].get('BUND_10Y')
          == '来源文件在场且子源BBK_WU3146取数成功而指标缺席'
             '(采集遗漏——采集器已取到而事实未生成)',
          rec['noncore_missing_detail'].get('BUND_10Y'))

# ══ [4] 证据不可得 → 诚实兜底 ═══════════════════════════════════════
print("\n[4] 证据不可得=采集遗漏或子源缺席不可区分(兜底;R12 起按断点归因)")
with tempfile.TemporaryDirectory() as td:
    snap, daily = _build(td, ea_mutate=_drop_bund10y_readfail)
    rec_pure = rp.recompute_gate_a(snap)          # 纯重验: 无 data_dir
    check("纯重验模式(无data_dir)→兜底(未提供采集目录变体)",
          rec_pure['noncore_missing_detail'].get('BUND_10Y') == HEDGE_NO_DIR,
          rec_pure['noncore_missing_detail'].get('BUND_10Y'))
with tempfile.TemporaryDirectory() as td:
    snap, daily = _build(td, missing=('INDPRO',))  # macro 通道无 source_key
    rec = rp.recompute_gate_a(snap, data_dir=daily, trusted_root=td)
    check("无 source_key 指标(INDPRO,macro)→兜底(注册表未登记键变体)",
          rec['noncore_missing_detail'].get('INDPRO') == HEDGE_NO_KEY,
          rec['noncore_missing_detail'].get('INDPRO'))

# ══ [5] 契约锁: 清单成员/Gate 判定零变动 ═════════════════════════════
print("\n[5] 契约锁(纯话术层: 成员/状态/门核验零变动)")
with tempfile.TemporaryDirectory() as td_c, tempfile.TemporaryDirectory() as td_m:
    ctrl, daily_c = _build(td_c)                  # 未变异: BUND_10Y 在场
    mut, daily_m = _build(td_m, ea_mutate=_drop_bund10y_readfail)
    rc = rp.recompute_gate_a(ctrl, data_dir=daily_c, trusted_root=td_c)
    rm = rp.recompute_gate_a(mut, data_dir=daily_m, trusted_root=td_m)
    check("缺失清单差集恰为 {BUND_10Y}(成员判定不受话术影响)",
          set(rm['noncore_missing']) == set(rc['noncore_missing']) | {'BUND_10Y'},
          f"ctrl={sorted(rc['noncore_missing'])[:6]} mut={sorted(rm['noncore_missing'])[:6]}")
    check("core_missing 零变动", rm['core_missing'] == rc['core_missing'] == [])
    check("effective 零变动(均 DEGRADED)",
          rm['effective'] == rc['effective'] == 'DEGRADED',
          f"{rc['effective']}→{rm['effective']}")
    st_decl, why = rp.gate_status(mut, data_dir=daily_m, trusted_root=td_m)
    check("声明↔重算一致性核验通过(子源话术不破坏门链)",
          st_decl == 'DEGRADED', f"{st_decl}:{why}")

# ══ [6] _channel_subsource_map 单元面 ═══════════════════════════════
print("\n[6] 子源档读取单元面(可选证据,只读不加信)")
with tempfile.TemporaryDirectory() as td:
    daily = os.path.join(td, 'data', 'daily')
    os.makedirs(daily)
    ea_doc = {'date': YMD,
              'sources_status': {'BBK_WU3146': {'status': 'READ_FAIL'}}}
    import hashlib
    raw = json.dumps(ea_doc).encode('utf-8')
    fp = os.path.join(daily, f'ea_{YMD}.json')
    with open(fp, 'wb') as f:
        f.write(raw)
    sha_ok = hashlib.sha256(raw).hexdigest()
    st_ok = {'status': 'EXACT', 'file': f'ea_{YMD}.json', 'sha256': sha_ok}
    check("sha 一致→返回子源状态dict",
          rp._channel_subsource_map(st_ok, daily, trusted_root=td)
          == {'BBK_WU3146': {'status': 'READ_FAIL'}})
    st_badsha = {'status': 'EXACT', 'file': f'ea_{YMD}.json',
                 'sha256': '0' * 64}
    check("sha256 失配→None(证据不可用,不虚报)",
          rp._channel_subsource_map(st_badsha, daily, trusted_root=td) is None)
    mac_doc = {'date': YMD, 'data': {}}          # 无 sources_status 节
    with open(os.path.join(daily, f'macro_{YMD}.json'), 'w',
              encoding='utf-8') as f:
        json.dump(mac_doc, f)
    st_mac = {'status': 'EXACT', 'file': f'macro_{YMD}.json',
              'sha256': hashlib.sha256(
                  json.dumps(mac_doc).encode('utf-8')).hexdigest()}
    check("档内无 sources_status 节→None",
          rp._channel_subsource_map(st_mac, daily, trusted_root=td) is None)
    check("无 data_dir(纯重验)→None",
          rp._channel_subsource_map(st_ok, None) is None)
    check("st 缺 file→None",
          rp._channel_subsource_map({'status': 'EXACT'}, daily,
                                    trusted_root=td) is None)
    cache = {}
    a1 = rp._channel_subsource_map(st_ok, daily, trusted_root=td, cache=cache)
    a2 = rp._channel_subsource_map(st_ok, daily, trusted_root=td, cache=cache)
    check("共享缓存命中(同对象,不重复读盘)", a1 is a2 and a1 is not None)

# ══ [7] 渲染面: 快照 MD 非核心缺失节 ═════════════════════════════════
print("\n[7] 快照 MD 渲染(人读面含子源缺席行)")
with tempfile.TemporaryDirectory() as td:
    snap, daily = _build(td, ea_mutate=_drop_bund10y_readfail)
    md_path = os.path.join(daily, f"research_snapshot_{YMD}.md")
    with open(md_path, encoding='utf-8') as f:
        md = f.read()
    check("MD 非核心缺失节含 BUND_10Y 子源缺席行",
          ('- BUND_10Y: 子源缺席(ea档记录:BBK_WU3146=READ_FAIL'
           '——源端不可得/未采,非采集遗漏)') in md)

# ══ 汇总 ═════════════════════════════════════════════════════════════
print(f"\n{'='*60}")
print(f"R11 子源级注记细化: {PASS} PASS / {FAIL} FAIL")
sys.exit(0 if FAIL == 0 else 1)
