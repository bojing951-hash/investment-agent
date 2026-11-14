# -*- coding: utf-8 -*-
"""ResearchClaim v1.0 bundle 容器/schema/读写(架构整改阶段三 T4,2026-11-14)。

契约权威: docs/autonomous-rd/ARCH_REFORM_PHASE2_CONTRACT.md §2/§5(两席放行 v1.2)。
本模块=**纯容器**: schema 校验+装配+落盘读写。零派生逻辑(派生=claim_factory)、
零模型调用、零网络、零环境变量读取、零时间戳注入(生成时刻非输入函数,注入即
破坏「输入→输出纯函数」;bundle 时间身份=快照 research_as_of/target_date)。

bundle 落盘命名(契约§2): claims_YYYYMMDD.json(快照旁挂,快照/anchors/
data_pack/QB 档零改动)。
"""
from __future__ import annotations

import json
import os
import re

# ── schema 常量(契约§2 逐字对齐;扩展点显式声明,禁静默扩) ──────────────
SCHEMA_VERSION = 'research-claims/1.0'

# 契约顶层八型+新增 statistic/composite_score=十型。工厂产能(T4=六型;
# T6a 补全 statistic=七型,契约§2 十型闭合的系列派生类落地):
# forecast/qualitative_inference=模型提交面[阶段四];composite_score=后续工单。
FACTORY_CLAIM_TYPES = (
    'level', 'change', 'comparison',
    'threshold', 'threshold_distance', 'observation_lag',
    'statistic',
)
RESERVED_CLAIM_TYPES = (
    'forecast', 'qualitative_inference', 'composite_score',
)

SUBTYPES = {
    'level': ('point', 'band'),
    'change': ('relative', 'absolute'),
    'comparison': ('spread', 'diff', 'rank'),
    'threshold': ('edge_relation',),
    'threshold_distance': ('absolute_distance',),
    'observation_lag': ('as_of_minus_observation',),
    'statistic': ('correlation',),
}

WINDOWS = ('week', 'mtd', 'ytd', 'm1', 'm3', 'm6', 'm12')

# 断言层自有单位(非 metric 单位;律3 单位代数适用于 metric 系单位,断言层
# 单位在此显式枚举=禁自由字符串):
#   rank_position  = 排名序数(1 起,同值并列同秩)
#   calendar_day   = 自然日天数(observation_lag 专用)
CLAIM_LAYER_UNITS = ('rank_position', 'calendar_day')

# attribution 词表(契约§2: deterministic=工厂派生|model_inferred=模型提交)。
# T5 增量扩容(申报): 原校验只认 deterministic(T4 波工厂唯一来源);T5 验证面须
# 可携带外部提交 claim(工单T5「bundle 须可携带 origin=model_inferred;阶段四
# 真实入口,本波测试用合成注入」)——本常量=该面落点。deterministic-only bundle
# 的既有校验行为与 attribution_policy 字符串零变化(向后兼容,非破坏性)。
ALLOWED_ATTRIBUTIONS = ('deterministic', 'model_inferred')

BUNDLE_ID_RE = re.compile(r'^claims_\d{8}$')
CLAIM_ID_RE = re.compile(r'^CLM-\d{8}-\d{4}$')

# evidence_refs ref 语法(契约§1 统一 ref 七类):
#   fact_id            kind=snapshot_fact     (如 "HY_OAS@2026-11-12")
#   series_ref         kind=series_ref        (如 "series:HY_OAS" / 基准观测
#                                             "SPX@2026-11-06"(role=basis))
#   VIEW/QB/claim/prior_bundle/reconciliation refs=T5+/阶段四接口预留
EVIDENCE_KINDS = ('snapshot_fact', 'series_ref')


class SchemaError(ValueError):
    """claim/bundle 违反 ResearchClaim v1.0 schema。"""


# ══ 单 claim schema ════════════════════════════════════════════════

def validate_claim(c: dict) -> None:
    """逐字段校验一条 claim(违例抛 SchemaError;工厂产物全过=本波验收面)。"""
    if not isinstance(c, dict):
        raise SchemaError('claim 须为 dict')
    for k in ('claim_id', 'claim_type', 'subtype', 'unit', 'attribution',
              'value', 'evidence_refs', 'derivation', 'observation_date',
              'as_of', 'metric_id', 'metric_ids'):
        if k not in c:
            raise SchemaError(f'缺必填字段 {k}')
    if not CLAIM_ID_RE.match(c['claim_id'] or ''):
        raise SchemaError(f'claim_id 形态非法: {c["claim_id"]!r}(须 CLM-YYYYMMDD-NNNN)')
    if c['claim_type'] not in FACTORY_CLAIM_TYPES:
        raise SchemaError(f'claim_type 非工厂六型: {c["claim_type"]!r}')
    if c['subtype'] not in SUBTYPES[c['claim_type']]:
        raise SchemaError(f'subtype {c["subtype"]!r} 不属 {c["claim_type"]}')
    if c['attribution'] not in ALLOWED_ATTRIBUTIONS:
        raise SchemaError(f"attribution 只准 {ALLOWED_ATTRIBUTIONS}: {c['attribution']!r}")
    if c['attribution'] == 'model_inferred':
        # 外部提交面(T5 验证器消费;真实提交入口=阶段四): 结构校验照走六型
        # schema,验证状态机=claim_verifier(强制 SEMANTIC_REVIEW 面)。
        pass

    # 律2/律3: (claim_type, subtype, unit) 三元组定语义
    ct, st = c['claim_type'], c['subtype']
    if ct == 'change' and st == 'relative' and c['unit'] != 'percent':
        raise SchemaError('change.relative 单位只准 percent(相对变化口径)')
    if ct == 'observation_lag' and c['unit'] != 'calendar_day':
        raise SchemaError('observation_lag 单位只准 calendar_day')
    if ct == 'comparison' and st == 'rank' and c['unit'] != 'rank_position':
        raise SchemaError('comparison.rank 单位只准 rank_position')

    # 律2: change 必带 window+基准值
    if ct == 'change':
        if c.get('window') not in WINDOWS:
            raise SchemaError(f'change 须带合法 window: {c.get("window")!r}')
        if not isinstance(c.get('basis_date'), str) or 'basis_value' not in c:
            raise SchemaError('change 必带 basis_date+basis_value(契约律2)')

    # evidence_refs 必带值(契约§2 设计决策: 引用即携带被引 fact 的值与单位)
    if not isinstance(c['evidence_refs'], list) or not c['evidence_refs']:
        raise SchemaError('evidence_refs 须非空 list')
    for r in c['evidence_refs']:
        if not isinstance(r, dict) or not r.get('ref') or r.get('kind') not in EVIDENCE_KINDS:
            raise SchemaError(f'evidence ref 形态非法: {r!r}')
        if 'value' not in r or not r.get('unit'):
            raise SchemaError(f'evidence ref 必带值与单位(契约§2): {r!r}')

    if not isinstance(c['derivation'], dict) \
            or not isinstance(c['derivation'].get('basis'), list) \
            or not c['derivation']['basis'] \
            or not isinstance(c['derivation'].get('formula'), str):
        raise SchemaError('derivation 须含非空 basis[] 与 formula(str)')

    if ct == 'level' and st == 'band':
        v = c['value']
        if not (isinstance(v, dict) and set(v) >= {'low', 'high'}
                and isinstance(v['low'], (int, float))
                and isinstance(v['high'], (int, float))
                and v['low'] <= v['high']):
            raise SchemaError('level.band value 须为 {low,high} 区间对象(一带两数)')
    if ct == 'level' and st == 'point' and not isinstance(c['value'], (int, float)):
        raise SchemaError('level.point value 须数值')
    if ct == 'change' and not isinstance(c['value'], (int, float)):
        raise SchemaError('change value 须数值')
    if ct == 'observation_lag':
        if not isinstance(c['value'], int) or c['value'] < 0:
            raise SchemaError('observation_lag value 须非负整数(天数)')
        if not isinstance(c.get('as_of_date'), str):
            raise SchemaError('observation_lag 须带 as_of_date')
    if ct == 'comparison':
        if not isinstance(c['metric_ids'], list) or len(c['metric_ids']) < 2:
            raise SchemaError('comparison 须带 ≥2 成员 metric_ids')
        if c['metric_id'] is not None:
            raise SchemaError('comparison 为多成员断言,metric_id 须 None(用 metric_ids)')
        if st == 'rank' and not isinstance(c.get('rank_key'), str):
            raise SchemaError('comparison.rank 须带 rank_key(排名依据)')
    elif ct == 'level' and st == 'band':
        # 区间带=多成员断言(fact 对或注册表双缘),与 comparison 同用 metric_ids;
        # 注册表双缘带(同指标两缘)退化单成员亦合法
        if not isinstance(c['metric_ids'], list) or not c['metric_ids']:
            raise SchemaError('level.band 须带 metric_ids(成员≥1)')
        if c['metric_id'] not in (None,) and c['metric_id'] not in c['metric_ids']:
            raise SchemaError('level.band metric_id 须 None 或为成员之一')
    elif ct == 'statistic':
        # 联合统计量=恰好双成员(配对统计;非跨 N 成员排名面)
        if not isinstance(c['metric_ids'], list) or len(c['metric_ids']) != 2 \
                or not all(isinstance(m, str) and m for m in c['metric_ids']):
            raise SchemaError('statistic 须带恰好 2 成员 metric_ids(配对统计)')
        if c['metric_id'] is not None:
            raise SchemaError('statistic 为双成员断言,metric_id 须 None(用 metric_ids)')
    elif c['metric_ids'] is not None:
        raise SchemaError('单指标断言不得携带 metric_ids(比较型专用)')
    else:
        if not isinstance(c['metric_id'], str) or not c['metric_id']:
            raise SchemaError('单指标断言 metric_id 必填')
    if ct in ('threshold', 'threshold_distance'):
        tr = c.get('threshold_ref')
        if not isinstance(tr, dict) or not tr.get('name') \
                or not isinstance(tr.get('value'), (int, float)) or not tr.get('unit') \
                or not tr.get('provenance'):
            raise SchemaError('threshold/threshold_distance 须带完整 threshold_ref'
                              '{name,value,unit,provenance}')
        if tr['unit'] != c['unit']:
            raise SchemaError('threshold_ref.unit 与 claim.unit 不一致(阈值与水平同单位)')
    if ct == 'threshold' and c.get('relation') not in ('above', 'below', 'at'):
        raise SchemaError('threshold 须带 relation∈{above,below,at}')
    if ct == 'threshold_distance':
        if not isinstance(c['value'], (int, float)) or c['value'] < 0:
            raise SchemaError('threshold_distance value=|level−threshold| 须非负')
        if c.get('side') not in ('above', 'below'):
            raise SchemaError('threshold_distance 须带 side(水平在阈值的哪一侧)')
    if ct == 'statistic':
        # T6a 契约补全(§2 十型): 系列联合统计量。correlation=双侧日收益率
        # 皮尔逊;value=None 专义「窗内含 nan 源→统计量如实不可计算」(禁以
        # 具体数冒充,验证器对该 None 语义有硬校验)。
        if c['unit'] != 'dimensionless':
            raise SchemaError('statistic.correlation 单位只准 dimensionless')
        w = c.get('corr_window_days')
        if not isinstance(w, int) or isinstance(w, bool) or w < 3:
            raise SchemaError('statistic 须带 corr_window_days(int≥3,pearson 最小样本)')
        if c['value'] is not None and not isinstance(c['value'], (int, float)):
            raise SchemaError('statistic value 须数值或 None(nan 如实语义)')
        if c.get('nan_reason') is not None and c['value'] is not None:
            raise SchemaError('nan_reason 只配 value=None(窗含 nan 不可计算时)')


# ══ bundle 容器 ════════════════════════════════════════════════════

def make_bundle(*, snapshot_id: str, target_date: str, research_as_of: str,
                claims: list, coverage_ledger: list, predicate_ledger: list,
                registry_fingerprints: dict) -> dict:
    """装配并校验 bundle(装配点唯一;不注入任何生成时刻信息)。"""
    target_date = str(target_date)
    counts = {}
    for c in claims:
        counts[c['claim_type']] = counts.get(c['claim_type'], 0) + 1
    # attribution_policy 随实况派生(T5 增量): 全 deterministic=与 T4 波逐字节同串
    # (向后兼容钉死);携 model_inferred=外部提交面如实申报。
    n_model = sum(1 for c in claims if c.get('attribution') == 'model_inferred')
    if n_model == 0:
        policy = ('deterministic-only(六型全部确定性派生,'
                  '零模型调用;model_inferred 提交面=阶段四)')
    else:
        policy = (f'mixed(deterministic={len(claims) - n_model}'
                  f'+model_inferred={n_model};model_inferred=T5 验证面合成注入,'
                  '真实提交入口=阶段四;验证状态机=claim_verifier 强制 SEMANTIC_REVIEW 面)')
    bundle = {
        'schema_version': SCHEMA_VERSION,
        'bundle_id': f'claims_{target_date}',
        'snapshot_id': snapshot_id,
        'target_date': target_date,
        'research_as_of': research_as_of,
        'attribution_policy': policy,
        'registry_fingerprints': registry_fingerprints,
        'counts': counts,
        'claims': claims,
        'coverage_ledger': coverage_ledger,
        'predicate_ledger': predicate_ledger,
    }
    validate_bundle(bundle)
    return bundle


def validate_bundle(b: dict) -> None:
    """bundle 级校验: id/版本/claim_id 唯一/计数一致/逐 claim schema。"""
    if b.get('schema_version') != SCHEMA_VERSION:
        raise SchemaError(f'schema_version 非本版: {b.get("schema_version")!r}')
    if not BUNDLE_ID_RE.match(b.get('bundle_id') or ''):
        raise SchemaError(f'bundle_id 形态非法: {b.get("bundle_id")!r}')
    ids = [c.get('claim_id') for c in b.get('claims', [])]
    if len(ids) != len(set(ids)):
        dup = sorted({i for i in ids if ids.count(i) > 1})
        raise SchemaError(f'claim_id 重复: {dup}')
    for c in b['claims']:
        validate_claim(c)
    counts = {}
    for c in b['claims']:
        counts[c['claim_type']] = counts.get(c['claim_type'], 0) + 1
    if b.get('counts') and b['counts'] != counts:
        raise SchemaError(f'counts 与 claims 实况不符: {b["counts"]} vs {counts}')
    if not isinstance(b.get('coverage_ledger'), list):
        raise SchemaError('coverage_ledger 须为 list(诚实缺席台账)')
    if not isinstance(b.get('predicate_ledger'), list):
        raise SchemaError('predicate_ledger 须为 list')


def bundle_to_json(b: dict, *, indent: int = 1) -> str:
    """序列化(ensure_ascii=False;字段序=构造序,确定性输出,禁 sort 抖动)。"""
    return json.dumps(b, ensure_ascii=False, indent=indent)


def bundle_filename(b: dict) -> str:
    """契约§2 落盘名: claims_YYYYMMDD.json(快照旁挂)。"""
    return f"claims_{b['target_date']}.json"


def write_bundle(b: dict, out_dir: str) -> str:
    """写 bundle 到目录(文件名=bundle_filename);返回写入路径。"""
    validate_bundle(b)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, bundle_filename(b))
    with open(path, 'w', encoding='utf-8') as f:
        f.write(bundle_to_json(b))
    return path


def load_bundle(path: str) -> dict:
    """读回+校验(读写往返必过同一 validator)。"""
    with open(path, 'r', encoding='utf-8') as f:
        b = json.load(f)
    validate_bundle(b)
    return b
