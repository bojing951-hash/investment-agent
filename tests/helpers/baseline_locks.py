# -*- coding: utf-8 -*-
"""WP-BR(IA-P0-BASELINE-RESTRUCT)三联锁共享助手 — T1冻结下限/T2派生完备/T3自洽演进。

设计登记(docs/P0_BASELINE_RESTRUCT_REPORT.md §一,R011 登记型决策点纪律):
- **T1 冻结下限锁**: 集合量≥封版冻结值(REGISTRY_FLOOR=81/ACTIVE_FLOOR=80/
  CORE_FLOOR=32/W4 报告行数下限 82);BASELINE_VINTAGE_IDS=封版 vintage 锚
  (81 项 metric_id 冻结集,机器生成自 BASE-BR 5e9fc88 基线注册表,非手抄;
  语义=「fixture 时点已存在的注册表条目」,仅用于下限/包含判断,禁用于与
  实载注册表的整集相等)——防缩水。
- **T2 派生完备锁**: 一切期望值自实载单一事实源派生(config/metric_registry.json
  实读;快照 facts/sources_status 实载;生产校验器 rp/rsem 实调),弃字面常量
  ——防腐化(注册表自洽破坏/条目重复/映射漂移仍被捕获)。
- **T3 自洽演进锁**: 演进合法仅当三集合同步+新条目全字段合规(源∈KNOWN_SOURCES
  且映射通道∈SOURCE_FILE_RULES、日历∈KNOWN_CALENDARS、单位∈KNOWN_UNITS、
  status∈{active,deprecated,pending})——「静默未登记演进」由此捕获。
- **vintage 判定规则**(登记): 条目属「fixture 时点已存在」iff metric_id ∈
  BASELINE_VINTAGE_IDS;时点后新增(=实载 active 集−vintage 锚)不回溯要求
  (Gate A 正常日断言允许 DEGRADED 仅当 core_missing/core_fail/noncore_fail/
  noncore_degraded 全空且 noncore_missing ⊆ 时点后新增集);
  **基线通道在任何 vintage 均 active 硬要求**: sources_status ⊇ 基线四采集通道
  且逐基线通道处于断言要求的 EXACT/FALLBACK 形态。
- **PENDING 标记形态**(登记): 条目级 status='pending'(先登记后激活;pending
  不计入 active 期望,天然不产生 noncore_missing);通道级 PENDING 不在生产
  词汇表(rp.SOURCE_STATUSES 无此态)——合同提及的「显式 PENDING 登记」由
  条目级承载,不扩生产语义(出入注记见 REPORT §零.2)。
- **通道口径**(登记): 基线四采集通道=sources_status 必需域(冻结
  BASELINE_SOURCE_CHANNELS);基线五通道=数据面通道全集(冻结
  BASELINE_DATA_CHANNELS,=hca.CHANNEL_PATTERNS 基线值,含 research_snapshot)。
"""
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_TESTS = os.path.dirname(_HERE)
ROOT = os.path.dirname(_TESTS)
for _p in (os.path.join(ROOT, 'scripts'), _TESTS):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ── T1 冻结值(合同 §零三联锁规则冻结;运行期禁改) ─────────────────────
REGISTRY_FLOOR = 81          # 注册表全量项数下限(含 deprecated)
ACTIVE_FLOOR = 80            # active 项数下限
CORE_FLOOR = 32              # active+core 项数下限
W4_REPORT_ROWS_FLOOR = 82    # w4 机器报告逐项表行数下限(表头1+81)
BASELINE_SOURCE_CHANNELS = ('global', 'macro', 'china', 'rate_economy')
BASELINE_DATA_CHANNELS = ('global', 'macro', 'china', 'rate_economy',
                          'research_snapshot')
VINTAGE_PROVENANCE = ('机器生成自 BASE-BR 5e9fc88650b9d4a483e83b6638cbc98'
                      '4f8e7b514 基线态 config/metric_registry.json(v2.0.0,'
                      '81项),生成指令见证据包 discovery/vintage_ids.txt')

# 封版 vintage 锚: fixture 时点(封版)已存在的 81 项 metric_id(机器生成零手抄)
BASELINE_VINTAGE_IDS = frozenset((
    'AAPL', 'AHE', 'BB_OAS', 'BEI_10Y', 'BEI_5Y', 'BRENT_F',
    'BTC', 'B_OAS', 'CCC_OAS', 'CHINEXT', 'CN_TOTAL_TURNOVER', 'CORE_CPI',
    'CORE_PCE', 'CPI', 'CURVE_2S10S', 'DFEDTARL', 'DFEDTARU', 'DFF',
    'DXY', 'EEM', 'EURUSD', 'EWG', 'EWJ', 'EWU',
    'EZU', 'FED_FUNDS', 'FEZ', 'FXI', 'GBPUSD', 'GLD',
    'GOLD_F', 'HSAHP', 'HSCEI', 'HSI', 'HYG', 'HY_IG_DIFF',
    'HY_OAS', 'ICSA', 'IEF', 'IG_OAS', 'INDA', 'INDPRO',
    'JTSJOL', 'LQD', 'MARGIN_BAL', 'MSFT', 'NDX', 'NFP',
    'NFP_MOM_K', 'NVDA', 'REAL_10Y', 'REAL_5Y', 'REAL_SHORT', 'RSAFS',
    'RUT', 'SB_FLOW', 'SHCOMP', 'SHY', 'SH_AMOUNT', 'SH_PE',
    'SILVER_F', 'SPX', 'SZCI', 'SZ_COMPONENT_AMOUNT', 'TIPS_10Y', 'TIPS_5Y',
    'TLT', 'UMCSENT', 'UNEMPLOYMENT', 'USDCNY', 'USDJPY', 'USO',
    'UST_10Y', 'UST_2Y', 'UST_30Y', 'UST_5Y', 'VIX', 'WTI_F',
    'WTI_SPOT_M', 'ZQ_F1_PRICE', 'ZQ_IMPLIED_AVG',
))

# T3 演进合法 status 词汇(条目级 PENDING 形态在此承载)
EVOLUTION_LEGAL_STATUS = ('active', 'deprecated', 'pending')

REGISTRY_PATH = os.path.join(ROOT, 'config', 'metric_registry.json')


# ── T2 实载派生(单一事实源=config/metric_registry.json 实读;可注入变体) ──
def registry_doc(reg=None):
    """实载注册表(dict)。默认实读生产注册表文件;reg 给出时用于注入变体
    (负向电池/演进预演),不落盘、不触生产文件。"""
    if reg is not None:
        return reg
    with open(REGISTRY_PATH, encoding='utf-8') as f:
        return json.load(f)


def registry_metric_ids(reg=None):
    """实载注册表全量 metric_id 集(含 deprecated)。"""
    return {m['metric_id'] for m in registry_doc(reg)['metrics']}


def active_metric_ids(reg=None):
    """实载 active metric_id 集。"""
    return {m['metric_id'] for m in registry_doc(reg)['metrics']
            if m.get('status') == 'active'}


def core_metric_ids_loaded(reg=None):
    """实载 active+core metric_id 集。"""
    return {m['metric_id'] for m in registry_doc(reg)['metrics']
            if m.get('status') == 'active' and m.get('criticality') == 'core'}


def expected_registry_count(reg=None):
    """w4 族派生期望: 审计结果项数==实载注册表项数(弃字面 81)。"""
    return len(registry_doc(reg)['metrics'])


# ── T1 冻结下限(防缩水) ────────────────────────────────────────────────
def registry_counts_ok(reg=None):
    """T1: 全量≥81 / active≥80 / core≥32。返回(ok, 说明)。"""
    ms = registry_doc(reg)['metrics']
    n = len(ms)
    n_active = sum(1 for m in ms if m.get('status') == 'active')
    n_core = sum(1 for m in ms
                 if m.get('status') == 'active' and m.get('criticality') == 'core')
    problems = []
    if n < REGISTRY_FLOOR:
        problems.append(f'注册表项数{n}<{REGISTRY_FLOOR}(静默缩水)')
    if n_active < ACTIVE_FLOOR:
        problems.append(f'active项数{n_active}<{ACTIVE_FLOOR}')
    if n_core < CORE_FLOOR:
        problems.append(f'core项数{n_core}<{CORE_FLOOR}')
    return (not problems), '; '.join(problems)


def baseline_removals(reg=None):
    """T1 集合形态: 实载注册表缺失的 vintage 基线条目(必须为空——基线条目
    被删除=缩水,与计数下限互为冗余的双面守护)。"""
    return BASELINE_VINTAGE_IDS - registry_metric_ids(reg)


def vintage_additions(reg=None):
    """vintage 判定: 实载注册表中时点后新增的条目(合法演进不回溯要求)。"""
    return registry_metric_ids(reg) - BASELINE_VINTAGE_IDS


# ── T2 派生完备(防腐化: 自洽/重复/漂移) ────────────────────────────────
def ids_unique_bijection_ok(reg=None):
    """T2: metrics 列表无重复 metric_id 且 by_id 键集==metrics ID 集(双射)。

    by_id 口径(登记): 生产注册表原始 JSON 不含 by_id(fe.load_registry 加载时
    派生)——无注入时以 fe.load_registry 实载派生为准(T2 单一事实源);注入变体
    自带 by_id 时按注入比对(N3 自洽破坏注入由此红),缺省时按生产同式派生。"""
    doc = registry_doc(reg)
    ids = [m['metric_id'] for m in doc['metrics']]
    problems = []
    if len(ids) != len(set(ids)):
        dup = sorted({i for i in ids if ids.count(i) > 1})
        problems.append(f'metrics重复metric_id:{dup[:5]}')
    if reg is None or 'by_id' not in reg:
        import fact_engine as fe
        by_keys = set(fe.load_registry()['by_id'])
    else:
        by_keys = set(reg['by_id'])
    if by_keys != set(ids):
        only_list = sorted(set(ids) - by_keys)[:5]
        only_map = sorted(by_keys - set(ids))[:5]
        problems.append(f'by_id与metrics不同步: 仅列表有{only_list} 仅映射有{only_map}')
    return (not problems), '; '.join(problems)


def artifact_covers_vintage_baseline(artifact_ids, reg=None):
    """T2(封版工件覆盖锁的 vintage 域形态,用于审计清单/政策矩阵覆盖断言):

    工件(审计清单/政策矩阵)必须**恰覆盖**注册表∩vintage 锚(=时点已存在且
    仍在册的全部基线条目),无重复无私货;时点后新增条目不要求工件回溯补录;
    基线条目被删(注册表缩水)或工件丧行/夹带均红。
    artifact_ids: 可迭代 metric_id(允许重复输入,函数内验唯一)。"""
    ids = list(artifact_ids)
    expected = registry_metric_ids(reg) & BASELINE_VINTAGE_IDS
    problems = []
    if len(ids) != len(set(ids)):
        dup = sorted({i for i in ids if ids.count(i) > 1})
        problems.append(f'工件条目重复:{dup[:5]}')
    if set(ids) != expected:
        miss = sorted(expected - set(ids))[:5]
        extra = sorted(set(ids) - expected)[:5]
        problems.append(f'工件覆盖≠注册表∩vintage: 缺{miss} 多{extra}')
    if len(expected) < REGISTRY_FLOOR:
        problems.append(f'注册表∩vintage={len(expected)}<{REGISTRY_FLOOR}'
                        '(基线条目被删)')
    return (not problems), '; '.join(problems)


# ── T2 全 active 契约的 vintage 域(Gate A 正常日断言) ──────────────────
def gate_vintage_ok(gate, reg=None):
    """fixt 全 active 正常日 Gate A 断言的 vintage 域形态(合同 §零 fixt 重構)。

    gate: 快照 gate_a dict(status)或 recompute 结果 dict(effective);
    合法: PASS(任何 vintage 全齐备恒合法);或 DEGRADED 且
    core_missing/core_fail/noncore_fail/noncore_degraded 全空且
    noncore_missing ⊆ 时点后新增集(vintage_additions)——基线通道/指标静默
    死亡(非新增的缺失)在此红。返回(ok, 说明)。"""
    if not isinstance(gate, dict):
        return False, f'gate非对象:{type(gate).__name__}'
    status = gate['effective'] if 'effective' in gate else gate.get('status')
    if status == 'PASS':
        return True, 'PASS'
    problems = []
    if status != 'DEGRADED':
        problems.append(f'gate={status!r}(非PASS/DEGRADED)')
    for bucket in ('core_missing', 'core_fail', 'noncore_fail',
                   'noncore_degraded'):
        if gate.get(bucket):
            problems.append(f'{bucket}非空:{sorted(gate[bucket])[:5]}')
    missing = set(gate.get('noncore_missing') or [])
    if missing:
        base_lost = sorted(missing - vintage_additions(reg))[:5]
        if base_lost:
            problems.append(f'noncore_missing含vintage基线条目:{base_lost}')
    return (not problems), '; '.join(problems)


# ── T2+T3 sources_status 结构(基线通道硬要求+在场通道结构合法) ──────────
def sources_status_baseline_ok(sources_status, require='EXACT', reg=None):
    """sources_status 结构锁的演进兼容形态(合同 AC-02③):

    ① ⊇基线四采集通道且逐基线通道 status==require('EXACT'正常日/'FALLBACK'
       回退日)——基线通道在任何 vintage 均 active 硬要求;
    ② 每个在场通道结构合法(委托生产校验器 rp.sources_status_problems 结构
       口径,T2 派生不与生产漂移);
    ③ 时点后新增通道若在场: 仅要求②结构合法,不回溯要求 EXACT。
    返回(ok, 问题清单)。"""
    import research_provenance as rp
    problems = []
    if not isinstance(sources_status, dict):
        return False, [f'sources_status非对象:{type(sources_status).__name__}']
    for ch in BASELINE_SOURCE_CHANNELS:
        st = sources_status.get(ch)
        if not isinstance(st, dict):
            problems.append(f'基线通道{ch!r}缺席/非对象')
        elif st.get('status') != require:
            problems.append(f"基线通道{ch!r}status={st.get('status')!r}"
                            f'≠{require!r}')
    problems.extend(rp.sources_status_problems(sources_status))
    return (not problems), problems


# ── T3 自洽演进锁 ──────────────────────────────────────────────────────
def registry_self_consistent(reg=None):
    """T3 前件: 注册表自洽(双射唯一+生产语义校验器零 error)。
    「注册表自洽破坏/条目重复/映射漂移」回归类由此捕获(@任意 N)。"""
    import registry_semantics as rsem
    problems = []
    ok1, why1 = ids_unique_bijection_ok(reg)
    if not ok1:
        problems.append(why1)
    errs = [p for p in rsem.validate_registry(registry_doc(reg))
            if p.get('severity') == 'error']
    if errs:
        problems.append(f'validate_registry错误{len(errs)}条:'
                        + '; '.join(str(e.get('rule', e)) for e in errs[:3]))
    return (not problems), problems


def evolution_legal(reg=None):
    """T3: 演进合法=vintage 后新增条目全字段合规(枚举/日历/单位/通道/status)
    且注册表自洽。「静默未登记演进」(by_id 添加但枚举/日历/通道缺)由此红。
    返回(ok, 问题清单)。"""
    import registry_semantics as rsem
    import research_provenance as rp
    problems = []
    ok0, why0 = registry_self_consistent(reg)
    if not ok0:
        problems.extend([f'自洽破坏:{w}' for w in why0])
    doc = registry_doc(reg)
    by_id = doc.get('by_id') or {m['metric_id']: m for m in doc['metrics']}
    if reg is None:
        import fact_engine as fe
        by_id = fe.load_registry()['by_id']
    known_channels = set(rp.SOURCE_FILE_RULES)
    collector_to_channel = {
        'global_market_collector': 'global', 'macro_collector': 'macro',
        'china_market_collector': 'china', 'rate_expectations': 'rate_economy',
    }
    for mid in sorted(vintage_additions(reg)):
        m = by_id.get(mid)
        if m is None:
            problems.append(f'新增条目{mid!r}不在by_id(三集合不同步)')
            continue
        if m.get('status') not in EVOLUTION_LEGAL_STATUS:
            problems.append(f"{mid}:status={m.get('status')!r}不在"
                            f'{EVOLUTION_LEGAL_STATUS}')
        if m.get('source') not in rsem.KNOWN_SOURCES:
            problems.append(f"{mid}:source={m.get('source')!r}未登记(枚举缺)")
        ch = collector_to_channel.get(m.get('source'))
        if '(derived)' not in str(m.get('source')) and ch not in known_channels:
            problems.append(f"{mid}:source={m.get('source')!r}无采集通道登记"
                            '(SOURCE_FILE_RULES缺)')
        if m.get('calendar') not in rsem.KNOWN_CALENDARS:
            problems.append(f"{mid}:calendar={m.get('calendar')!r}未登记(日历缺)")
        if m.get('unit') not in rsem.KNOWN_UNITS:
            problems.append(f"{mid}:unit={m.get('unit')!r}未登记(单位枚举缺)")
    return (not problems), problems


# ── 注入配套(进程内负向电池/预演用;运行后还原) ─────────────────────────
def reset_registry_caches():
    """重置 fe/rp 注册表派生缓存(fe._REGISTRY_CACHE/rp._CORE_CACHE/
    rp._ACTIVE_CACHE)——monkeypatch fe.load_registry 后必须调用,否则派生集
    仍是旧注册表(注入失真)。"""
    import fact_engine as fe
    import research_provenance as rp
    fe._REGISTRY_CACHE = None
    rp._CORE_CACHE = None
    rp._ACTIVE_CACHE = None
