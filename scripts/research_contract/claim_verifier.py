#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""claim_verifier — 六状态确定性验证(架构整改阶段三 T5)。

依据: PHASE2-CONTRACT §4 状态表(权威)+律2/3/6/7/8+§3 分解可加性。
工单验收原文: 「注入违例每状态≥1 反例咬住」。

六状态与发布规则(§4 逐字映射):
  VERIFIED                 ✅ 发布    无披露(computed/delta/tolerance/checker_version 随行)
  CONTRADICTED             ❌ 禁发布  claim 级修订+机械重渲染(非整报隔离);修订记录随档
  INSUFFICIENT_EVIDENCE    ✅ 须披露  证据不足注记随文
  NOT_VERIFIABLE           仅 deterministic 可披露后发布;model_inferred 数值落此态
                           =强制升 SEMANTIC_REVIEW_REQUIRED(v1.1 封死洗数通道);
                           逐 claim 归因{路径/原因枚举/可否次级交叉};禁入【事实】区
  STALE                    ✅ 须披露  滞后÷发布节奏分级(节奏=metric_registry
                           freshness.max_calendar_lag_days 单源);>3 节奏禁入
                           「现状」框架;派生 claim 继承最差输入陈旧度
  SEMANTIC_REVIEW_REQUIRED ⏸ 暂缓    超时策略=剔除存疑项+披露剔除后发布(不无限期卡死)

判定优先级(一 claim 一状态): 数值/证据不符 > 强制语义审 > 无路径 > 证据不足 >
陈旧 > 一致。数值一致但陈旧的 claim=STALE(数值面随行保留 computed/delta)。

独立复算口径: 逐 claim 从 snapshot facts/series_store+两注册表**重算**(不回读
工厂装配值);change 族按 fact_engine 既成舍入位(round 4dp)同位复算,delta
容差=0+1e-9 浮点护栏;level/threshold 族=Fact/注册表层直读零改写,delta=0。
threshold 型除 value 外,relation/since_date/since_note/persistence 顶层字段
逐项镜像重算(工厂口径逐字对照: side_now 同侧取 crossing_date/全窗同侧回窗首
注记/末端侧不一致=如实空);threshold_distance 的 side 同镜像。
谓词经 cf.last_crossing/crossing_count 纯函数重算(其实现另有套件锁;此处
消费重算结果而非工厂缓存值)。

rank 组核验: T4 排名 claim 的名次主体经发射序隐含(claim_id 升序=降序成员
序,见 build_rank_claims);验证=同序重排逐位对照+组多重集对照,两道都过
才算 VERIFIED;组内任一被篡改→组多重集不符=CONTRADICTED。

律7(model_inferred): 数值 claim 有权威源→对照复算,不符=CONTRADICTED;
无路径→NOT_VERIFIABLE 但**禁落此态**,强制升 SEMANTIC_REVIEW_REQUIRED。

纯度: 仅 stdlib+fact_engine(只读)+claim_factory(只读谓词)+claim_bundle;
零模型客户端/零环境变量读取/零网络/零随机(与 T4 同纪律,Z1 面适用)。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date

if __package__ in (None, '') or __package__ == 'research_contract':
    _here = os.path.dirname(os.path.abspath(__file__))
    for _p in (os.path.dirname(_here), _here):
        if _p not in sys.path:
            sys.path.insert(0, _p)

import fact_engine as fe                               # noqa: E402  只读(注册表)
from research_contract import claim_bundle as cb       # noqa: E402
from research_contract import claim_factory as cf      # noqa: E402  只读(谓词/注册表装载)

CHECKER_VERSION = 'claim_verifier 1.0'
EPS = 1e-9                    # 浮点护栏(delta 名义容差=0,同位舍入复算)

STATUSES = ('VERIFIED', 'CONTRADICTED', 'INSUFFICIENT_EVIDENCE',
            'NOT_VERIFIABLE', 'STALE', 'SEMANTIC_REVIEW_REQUIRED')

# §4 披露要求 → 发布许可(deterministic 面;model_inferred 数值另受强制升态约束)
PUBLISHABLE = {
    'VERIFIED': True,             # 无披露
    'CONTRADICTED': False,        # claim 级修订,禁直接发布
    'INSUFFICIENT_EVIDENCE': True,    # 须披露
    'NOT_VERIFIABLE': 'deterministic_only',   # 仅工厂产物可披露后发布
    'STALE': True,                # 须披露;>3 节奏另禁入现状框架
    'SEMANTIC_REVIEW_REQUIRED': 'deferred',    # 暂缓;超时=剔除+披露
}

# STALE 分级: ratio=滞后天数 ÷ freshness.max_calendar_lag_days(注册表单源)
#   fresh      ≤1   政策窗内
#   level_1    ≤2   超一档(披露随文)
#   level_2    ≤3   中度(披露;慎入现状框架)
#   level_3    >3   重度(禁入「现状」框架,§4 原文「滞后>2-3 个发布节奏」)
STALE_TIERS = ((1.0, 'fresh'), (2.0, 'stale_level_1'),
               (3.0, 'stale_level_2'), (None, 'stale_level_3'))

CADENCE_FALLBACK_DAYS = {          # freshness 缺失时按 frequency 兜底(如实注记)
    'daily': 1.0, 'weekly': 7.0, 'monthly': 30.4375,
    'quarterly': 91.3125, 'annual': 365.25,
}

# NOT_VERIFIABLE 归因原因枚举(§4 披露要求「逐 claim 归因」)
NV_REASONS = ('evidence_absent', 'no_verifier_path', 'series_absent',
              'predicate_uncomputable', 'rank_group_mismatch')

_GROUP_FAIL = object()   # 组核验失败哨兵(单例;数值哨兵禁每调用新建)


# ── 工具 ───────────────────────────────────────────────────────────

def _days_between(a: str, b: str) -> int:
    return (date.fromisoformat(str(a)[:10]) - date.fromisoformat(str(b)[:10])).days


def _as_of_of(claim: dict, snapshot: dict) -> str:
    a = claim.get('as_of') or snapshot.get('research_as_of')
    return str(a)[:10]


def _close(a, b, tol=0.0) -> bool:
    if a is None or b is None:
        return a is b
    fa, fb = float(a), float(b)
    if fa != fa and fb != fb:
        return True    # NaN↔NaN 同态相等(采集失败=可验证事实,非数值不符)
    return abs(fa - fb) <= tol + EPS


def _stale_grade(lag_days, cadence_days, *, cadence_source):
    """分级+披露串(§4 STALE 行)。缺节奏=cadence_unknown,不拦发布只披露。"""
    if cadence_days is None or lag_days is None:
        return {'tier': 'cadence_unknown', 'ratio': None, 'lag_days': lag_days,
                'cadence_days': None, 'cadence_source': cadence_source,
                'disclosure': '节奏不可得(注册表无 freshness/frequency)→陈旧度不可分级,如实披露'}
    ratio = lag_days / cadence_days if cadence_days > 0 else None
    tier = None
    for bound, name in STALE_TIERS:
        if bound is None or ratio <= bound:
            tier = name
            break
    disc = (f'观测滞后{lag_days}自然日≈{ratio:.1f}个发布节奏'
            f'(registry freshness.max_calendar_lag_days={cadence_days:g},{cadence_source})')
    if tier == 'stale_level_3':
        disc += '→重度陈旧,禁入「现状」框架(§4)'
    return {'tier': tier, 'ratio': ratio, 'lag_days': lag_days,
            'cadence_days': cadence_days, 'cadence_source': cadence_source,
            'disclosure': disc}


def _grade_members(mids, claim, snapshot):
    """逐成员按**自身节奏**定级,派生 claim 继承最差输入(§4「派生继承最差
    输入陈旧度」= 各成员 lag÷自身 cadence 后取最差档,禁跨成员错除)。"""
    as_of = _as_of_of(claim, snapshot)
    grades = []
    for mid in mids:
        m = fe.metric(mid) if mid else None
        if not m:
            continue
        fr = (m.get('freshness') or {})
        cad = fr.get('max_calendar_lag_days')
        src = 'freshness'
        if cad is None:
            cad = CADENCE_FALLBACK_DAYS.get(m.get('frequency'))
            src = 'frequency_fallback'
        lags = [_days_between(as_of, x['observation_date'])
                for x in snapshot.get('facts', [])
                if x['metric_id'] == mid]
        if not lags:
            continue
        grades.append(_stale_grade(max(lags), float(cad) if cad is not None else None,
                                   cadence_source=src))
    if not grades:
        return None
    worst = max(grades, key=lambda g: (g['ratio'] is not None, g['ratio'] or 0))
    if len(grades) > 1:
        worst = dict(worst)
        worst['members'] = [{'metric_id': m, 'tier': g['tier'],
                             'ratio': g['ratio']} for m, g in zip(mids, grades)]
        worst['disclosure'] += f'(派生 claim 继承最差输入: {len(grades)} 成员)'
    return worst


# ── 逐型独立复算(返回 (expected, tolerance, note, aux)) ───────────

class _NV(Exception):
    """复算不可达载体。state='INSUFF'(证据缺席→INSUFFICIENT_EVIDENCE)或
    'NV'(无确定性路径→NOT_VERIFIABLE,归因枚举随行)。"""

    def __init__(self, reason, secondary=False, state='NV'):
        super().__init__(reason)
        self.reason = reason
        self.secondary = secondary
        self.state = state


def _fact_by_id(snapshot):
    return {f['fact_id']: f for f in snapshot.get('facts', [])}


def _require_fact(refs, role, facts_by):
    if role is not None:
        for r in refs:
            if r.get('role') == role:
                f = facts_by.get(r['ref'])
                if f is None:
                    raise _NV('evidence_absent', state='INSUFF')
                return f
        raise _NV('evidence_absent', state='INSUFF')
    # role=None: 首条无 role 的事实引用(工厂主事实引用不带 role)
    for r in refs:
        if r.get('kind') == 'snapshot_fact' and not r.get('role'):
            f = facts_by.get(r['ref'])
            if f is None:
                raise _NV('evidence_absent', state='INSUFF')
            return f
    raise _NV('evidence_absent', state='INSUFF')


def _recompute(claim, snapshot, facts_by, thresholds_by, bundle):
    """按 (claim_type, subtype) 重算期望值。

    返回 (expected, tolerance, note, aux): expected 与 claim['value'] 同构;
    aux=需逐项对照的顶层事实性字段(threshold: relation/since_date/
    since_note/persistence;threshold_distance: side)。
    """
    ct, st = claim['claim_type'], claim['subtype']
    refs = claim.get('evidence_refs') or []
    store = snapshot.get('series_store', {})

    if ct == 'level' and st == 'point':
        f = _require_fact(refs, None, facts_by)
        return f['value'], 0.0, f'Fact 直读 {f["fact_id"]}={f["value"]}', None

    if ct == 'level' and st == 'band':
        if claim.get('band_source') == 'fact_pair':
            lo = _require_fact(refs, 'band_low', facts_by)
            hi = _require_fact(refs, 'band_high', facts_by)
            exp = {'low': lo['value'], 'high': hi['value']}
            return exp, 0.0, f'带对象两 fact 对 [{lo["value"]},{hi["value"]}]', None
        mid = claim.get('metric_id')
        below = [e for e in thresholds_by.get(mid, [])
                 if e.get('direction') == 'below' and 'band_edge' in (e.get('level') or [])]
        above = [e for e in thresholds_by.get(mid, [])
                 if e.get('direction') == 'above' and 'band_edge' in (e.get('level') or [])]
        if len(below) != 1 or len(above) != 1:
            raise _NV('no_verifier_path', secondary=True)
        exp = {'low': below[0]['value'], 'high': above[0]['value']}
        return exp, 0.0, f'注册表 band_edge 对 [{exp["low"]},{exp["high"]}]', None

    if ct == 'change':
        f = _require_fact(refs, None, facts_by)
        basis = next((r for r in refs if r.get('role') == 'basis'), None)
        if basis is None or basis.get('value') is None:
            raise _NV('evidence_absent', secondary=True, state='INSUFF')
        b = float(basis['value'])
        # 端值锚 derived.end.value(原始序列值;fact.value 为显示舍入位,
        # 直接用会在舍入边界误伤——T4 同锚独立复算既证)
        end_rec = ((f.get('derived') or {}).get('end') or {})
        v = end_rec.get('value')
        if v is None:
            v = f['value']
        v = float(v)
        if st == 'relative':
            if b == 0:
                raise _NV('predicate_uncomputable', secondary=True)
            return round((v / b - 1.0) * 100.0, 4), 0.0, \
                f'({v:g}/{b:g}−1)×100 同位 4dp 复算(端值=derived.end 原始值)', None
        # absolute: pp 轨/原单位轨(舍入位随 fact_engine 既成)
        return round(v - b, 4), 0.0, f'{v:g}−{b:g} 同位 4dp 复算', None

    if ct == 'comparison' and st == 'spread':
        l = _require_fact(refs, 'left', facts_by)
        r = _require_fact(refs, 'right', facts_by)
        if l['unit'] != r['unit']:
            raise ValueError(                     # 律3 违约=硬不符(篡改面)
                f'跨单位 spread(律3): {l["unit"]} vs {r["unit"]}')
        exp = round(l['value'] - r['value'], cf._ALGEBRA_DECIMALS)
        return exp, 0.0, f'{l["value"]:g}−{r["value"]:g}={exp:g}', None

    if ct == 'comparison' and st == 'rank':
        return _recompute_rank_group(claim, snapshot, bundle)

    if ct == 'threshold':
        f = _require_fact(refs, None, facts_by)
        tref = claim.get('threshold_ref') or {}
        tv = tref.get('value')
        if tv is None:
            raise _NV('no_verifier_path', secondary=True)
        lv = f['value']
        relation = 'above' if lv > tv else ('below' if lv < tv else 'at')
        aux = {'relation': relation, 'since_date': None,
               'since_note': None, 'persistence': None}
        if claim.get('metric_id') in store:
            s = store[claim['metric_id']]
            lc = cf.last_crossing(s['dates'], s['values'], tv)
            cc = cf.crossing_count(s['dates'], s['values'], tv)
            aux['persistence'] = {'last_crossing': lc,
                                  'crossing_count_full_window': cc}
            if lc.get('crossing_date') and lc.get('side_now') == relation:
                aux['since_date'] = lc['crossing_date']
            elif not lc.get('crossing_date'):
                aux['since_date'] = s['dates'][0]
                aux['since_note'] = ('since_limited_by_window'
                                     '(序列全窗同侧,最早仅可追溯至窗首)')
            else:
                aux['since_note'] = ('series_end_side_mismatch_fact'
                                     '(序列末端侧与事实水平侧'
                                     '不一致,since 不派生=如实空)')
        else:
            aux['since_note'] = 'series_absent(序列不在 store,since_date 不可派生=如实空)'
        note = f'{lv:g} vs {tv:g}→relation={relation};since/persistence 镜像重算'
        return lv, 0.0, note, aux

    if ct == 'threshold_distance':
        f = _require_fact(refs, None, facts_by)
        tref = claim.get('threshold_ref') or {}
        if tref.get('value') is None:
            raise _NV('no_verifier_path', secondary=True)
        exp = round(abs(f['value'] - tref['value']), cf._ALGEBRA_DECIMALS)
        side = 'above' if f['value'] > tref['value'] else (
            'below' if f['value'] < tref['value'] else 'at')
        return exp, 0.0, f'|{f["value"]:g}−{tref["value"]:g}|={exp:g}', {'side': side}

    if ct == 'observation_lag':
        f = _require_fact(refs, None, facts_by)
        as_of_d = str(f.get('as_of') or snapshot['research_as_of'])[:10]
        exp = _days_between(as_of_d, f['observation_date'])
        return exp, 0.0, f'as_of({as_of_d})−observation_date={exp} 自然日', None

    if ct == 'statistic' and st == 'correlation':
        # T6a: 联合统计量按 snapshot series_store 独立复算(与工厂同式镜像,
        # 但证据=序列本身,非工厂回声)。nan 语义=通道闭合而统计量不可计算:
        # claim None↔复算 nan 互证=VERIFIED;载具体数=伪造→硬不符。
        mids = claim.get('metric_ids') or []
        if len(mids) != 2:
            raise _NV('no_verifier_path', secondary=True)
        a, b = mids
        sa, sb = store.get(a), store.get(b)
        if not sa or not sb:
            raise _NV('evidence_absent', state='INSUFF')
        pair, _common = cf.paired_daily_returns(sa, sb)
        if not pair:
            raise _NV('insufficient_common_observations', state='INSUFF')
        w = claim.get('corr_window_days')
        if not isinstance(w, int) or w < 3:
            raise _NV('no_verifier_path', secondary=True)
        ra, rb = pair
        r = cf.pearson(ra[-w:], rb[-w:])
        if r is None:
            raise _NV('zero_variance_or_lt3', secondary=True)
        if isinstance(r, float) and r != r:            # NaN 如实传播
            if claim.get('value') is None:
                return None, 0.0, (f'{a}×{b} {w}d 窗含 nan 源→复算=nan,'
                                   'claim=None 同义互证(如实不可计算)'), None
            raise ValueError(
                f'伪造统计量({a}×{b} {w}d 窗含 nan 源,相关不可计算,'
                f'claim 载具体数 {claim["value"]!r})')
        val = claim.get('value')
        if val is None:
            raise ValueError(
                f'统计量缺席冒充({a}×{b} {w}d 复算={r:+.4f} 而 claim=None)')
        return float(r), cf.STATISTIC_TOL, \
            f'pearson(日收益率[-{w}:],{a},{b})={r:+.4f} 独立复算', None

    raise _NV('no_verifier_path')


def _recompute_rank_group(claim, snapshot, bundle):
    """rank=组核验(发射序对位+多重集)。expected 对位本 claim 位置。"""
    members = []
    for mid in claim.get('metric_ids') or []:
        f = next((x for x in snapshot.get('facts', [])
                  if x['metric_id'] == mid), None)
        wk = ((f or {}).get('derived') or {}).get('week') or {}
        if f is None or 'pct_change' not in wk:
            raise _NV('evidence_absent', state='INSUFF')
        members.append((f['metric_id'], wk['pct_change']))
    if len(members) < 2 or claim.get('rank_of') != len(members):
        raise _NV('rank_group_mismatch', secondary=True)
    members.sort(key=lambda t: (-t[1], t[0]))
    ranks = []
    prev_pct, prev_rank = None, None
    for i, (_mid, pct) in enumerate(members, start=1):
        rank = prev_rank if pct == prev_pct else i
        prev_pct, prev_rank = pct, rank
        ranks.append(rank)
    # 组多重集: bundle 内同键 rank claims 的 value 集合须恰=重算集合
    group = [c for c in bundle.get('claims', [])
             if c.get('claim_type') == 'comparison' and c.get('subtype') == 'rank'
             and c.get('rank_key') == claim.get('rank_key')
             and c.get('rank_of') == claim.get('rank_of')]
    if sorted(c['value'] for c in group) != sorted(ranks):
        raise ValueError('rank 组多重集不符(组内至少一条被篡改)')
    # 对位: 组内第 k 条(claim_id 升序=发射序)对应降序第 k 名
    ordered = sorted(group, key=lambda c: c['claim_id'])
    idx = ordered.index(claim)
    return ranks[idx], 0.0, \
        f'组核验: 降序第{ranks[idx]}/{len(ranks)}(发射序对位+多重集双过)', None


def _check_additivity(claim, bundle):
    """§3 分解可加性: derivation.basis 含 claim: 引用的 change claim(名义=实际+通胀)。
    目标=被引各分量之和(同单位);对不上=CONTRADICTED(注记,不覆盖数值主判)。"""
    parts = [b for b in (claim.get('derivation') or {}).get('basis', [])
             if isinstance(b, str) and b.startswith('claim:')]
    if len(parts) < 2:
        return None
    total = None
    for p in parts:
        cid = p.split(':', 1)[1]
        src = next((c for c in bundle.get('claims', [])
                    if c['claim_id'] == cid), None)
        if src is None or src['unit'] != claim['unit']:
            return {'ok': False, 'note': f'分量 {p} 不在 bundle 或单位不一致'}
        total = (total or 0.0) + float(src['value'])
    ok = _close(claim['value'], round(total, 4))
    return {'ok': ok, 'note': f'分解和={round(total, 4)} vs claim={claim["value"]}'
            f'({claim.get("metric_id")};§3 可加性复算)'}


# ── 证据一致性(引用即携带值→「引用存在且值相符」机械验证) ──────────

def _evidence_congruence(claim, facts_by):
    """evidence_refs 逐条对照 snapshot 事实: 缺席/带值不符→硬不符。

    无值引用(value=None)不在此判——那是 §2「引用必带值」结构违约,
    归 INSUFFICIENT_EVIDENCE 薄证据路(model_inferred 数值则强制升语义审)。
    """
    problems = []
    for r in claim.get('evidence_refs') or []:
        if r.get('kind') != 'snapshot_fact' or r.get('value') is None:
            continue
        f = facts_by.get(r.get('ref'))
        if f is None:
            problems.append(('evidence_absent', r.get('ref')))
        elif not _close(r.get('value'), f['value']):
            problems.append(('evidence_value_mismatch', r.get('ref')))
        elif r.get('unit') != f['unit']:
            problems.append(('evidence_unit_mismatch', r.get('ref')))
    return problems


def _threshold_congruence(claim, thresholds_by):
    """threshold_ref(含 band 的 threshold_refs)对照注册表 stable_key。"""
    problems = []
    trefs = list(claim.get('threshold_refs') or [])
    if claim.get('threshold_ref'):
        trefs.append(claim['threshold_ref'])
    by_key = {}
    for mid, entries in thresholds_by.items():
        for e in entries:
            by_key[e['stable_key']] = e
    for t in trefs:
        e = by_key.get(t.get('name'))
        if e is None:
            problems.append(('threshold_key_absent', t.get('name')))
        elif not _close(t.get('value'), e['value']) or t.get('unit') != e['unit']:
            problems.append(('threshold_value_drift', t.get('name')))
    return problems


# ── 主验证流程 ─────────────────────────────────────────────────────

def verify_claim(claim, *, snapshot, thresholds_by, bundle) -> dict:
    """单 claim → 六状态裁决之一(§4 表语义;优先级见模块头)。"""
    facts_by = _fact_by_id(snapshot)
    v = {'claim_id': claim.get('claim_id'),
         'metric_id': claim.get('metric_id'),
         'claim_type': claim['claim_type'], 'subtype': claim['subtype'],
         'attribution': claim.get('attribution', 'deterministic'),
         'status': None, 'computed': None, 'delta': None, 'tolerance': None,
         'checker_version': CHECKER_VERSION,
         'stale': None, 'nv_attribution': None,
         'disclosure': None, 'reasons': []}

    is_numeric = isinstance(claim.get('value'), (int, float)) or \
        isinstance(claim.get('value'), dict)   # band=数值对
    model_num = claim.get('attribution') == 'model_inferred' and is_numeric

    # 1) 证据一致性(硬不符=CONTRADICTED;缺席=NV/INSUFF 的前哨)
    for kind, ref in _evidence_congruence(claim, facts_by):
        v['reasons'].append(f'{kind}:{ref}')
    for kind, ref in _threshold_congruence(claim, thresholds_by):
        v['reasons'].append(f'{kind}:{ref}')

    # 2) 独立复算
    expected, aux = None, None
    try:
        expected, tol, note, aux = _recompute(claim, snapshot, facts_by,
                                              thresholds_by, bundle)
        v['reasons'].append(f'recompute:{note}')
    except _NV as nv:
        v['nv_attribution'] = {'path': f'{claim["claim_type"]}/{claim["subtype"]}',
                               'reason': nv.reason,
                               'reason_enum': nv.reason,
                               'secondary_cross_check_possible': nv.secondary,
                               'state': nv.state}
        v['reasons'].append(f'{nv.state.lower()}:{nv.reason}')
    except ValueError as ve:                       # rank 组多重集被篡改
        v['reasons'].append(f'hard:{ve}')
        expected = _GROUP_FAIL                     # 哨兵:组不符=硬不符

    mismatch = False
    if expected is not None:
        val = claim.get('value')
        if isinstance(expected, dict):
            mismatch = not isinstance(val, dict) or any(
                not _close(val.get(k), want)
                for k, want in expected.items())
        elif expected is not _GROUP_FAIL:
            mismatch = not _close(val, expected, tol)
            v['computed'] = expected
            v['tolerance'] = tol
            v['delta'] = (None if val is None else
                          round(float(val) - float(expected), 10))
        if aux:
            for k, want in aux.items():
                if not _dict_part_matches(claim.get(k), want):
                    mismatch = True
                    v['reasons'].append(f'aux_mismatch:{k} 期望{want!r}')

    # 3) 状态裁决(优先级: 不符 > 证据缺失(含强制升态) > 无路径 > 陈旧 > 一致)
    bad_ev = any(r.startswith(('evidence_value_mismatch', 'evidence_unit_mismatch',
                               'threshold_value_drift', 'hard:'))
                 for r in v['reasons'])
    refs_thin = (not claim.get('evidence_refs')) or any(
        r.get('value') is None for r in claim.get('evidence_refs') or [])
    if bad_ev or (expected is not None and mismatch):
        v['status'] = 'CONTRADICTED'
        v['disclosure'] = 'claim 级修订+机械重渲染(§4;非整报隔离),修订记录随档'
    elif model_num and (refs_thin or v['nv_attribution'] is not None):
        # 律7 反洗数: 数值 model claim 证据缺失或无复算路径,
        # 一律强制升语义审(禁经 INSUFFICIENT/NOT_VERIFIABLE 披露后洗出)
        v['status'] = 'SEMANTIC_REVIEW_REQUIRED'
        v['disclosure'] = ('model_inferred 数值断言证据缺失或无权威复算路径'
                           '→强制升语义审(§4/v1.1)')
        v['reasons'].append('forced_upgrade:model_inferred_numeric')
    elif refs_thin or (v['nv_attribution'] or {}).get('state') == 'INSUFF':
        v['status'] = 'INSUFFICIENT_EVIDENCE'
        v['disclosure'] = ('证据缺失(evidence_refs 为空/无值引用/所引事实'
                           '不在快照;契约: 引用必带值;§2)→证据不足注记随文')
    elif v['nv_attribution'] is not None:
        v['status'] = 'NOT_VERIFIABLE'
        v['nv_attribution'].pop('state', None)
        v['disclosure'] = ('确定性断言无可验证路径,披露后发布;'
                           '禁入【事实】区、禁加粗(§4)')
    else:
        # 4) STALE 分级(数值面已过;observation_lag 型=陈旧度计量本身,不分级)
        v['status'] = 'VERIFIED'
        if claim['claim_type'] != 'observation_lag':
            mids = [m for m in (claim.get('metric_ids') or
                    ([claim['metric_id']] if claim.get('metric_id') else [])) if m]
            g = _grade_members(mids, claim, snapshot) if mids else None
            if g is not None:
                v['stale'] = g
                if g['tier'] not in ('fresh', None):
                    v['status'] = 'STALE'
                    v['disclosure'] = g['disclosure']
    return v


def _dict_part_matches(got, want):
    """顶层事实性字段/嵌套结构对照(relation/since/side/persistence)。"""
    if want is None:
        return got is None
    if isinstance(want, dict):
        return isinstance(got, dict) and all(
            _dict_part_matches(got.get(k), w) for k, w in want.items())
    if isinstance(want, list):
        return isinstance(got, list) and len(got) == len(want) and all(
            _dict_part_matches(g, w) for g, w in zip(got, want))
    return got == want or (isinstance(want, float) and _close(got, want))


def verify_bundle(bundle: dict, *, snapshot: dict, thresholds: dict = None) -> dict:
    """bundle+snapshot(+阈值注册表) → 全量裁决+发布门(纯函数)。"""
    if thresholds is None:
        thresholds = cf.load_thresholds()
    thresholds_by = cf.thresholds_by_metric(thresholds)

    verdicts = [verify_claim(c, snapshot=snapshot,
                             thresholds_by=thresholds_by, bundle=bundle)
                for c in bundle.get('claims', [])]

    # §3 分解可加性(注记级: 对不上=CONTRADICTED 覆盖)
    vmap = {v['claim_id']: v for v in verdicts}
    for c in bundle.get('claims', []):
        if c['claim_type'] != 'change':
            continue
        add = _check_additivity(c, bundle)
        if add and not add['ok']:
            vmap[c['claim_id']]['status'] = 'CONTRADICTED'
            vmap[c['claim_id']]['reasons'].append(f'additivity:{add["note"]}')
            vmap[c['claim_id']]['disclosure'] = '分解可加性复算不符(§3)→claim 级修订'

    summary = {s: 0 for s in STATUSES}
    for v in verdicts:
        summary[v['status']] += 1
    summary['total'] = len(verdicts)

    publish = {
        'gate_b_numeric_all_verified': all(
            v['status'] in ('VERIFIED', 'STALE', 'INSUFFICIENT_EVIDENCE')
            or (v['status'] == 'NOT_VERIFIABLE'
                and v['attribution'] == 'deterministic')
            for v in verdicts),
        'blocked_revisions': [v['claim_id'] for v in verdicts
                              if v['status'] == 'CONTRADICTED'],
        'semantic_review_queue': [v['claim_id'] for v in verdicts
                                  if v['status'] == 'SEMANTIC_REVIEW_REQUIRED'],
        'current_frame_forbidden': [v['claim_id'] for v in verdicts
                                    if (v.get('stale') or {}).get('tier')
                                    == 'stale_level_3'],
        'disclosures': {v['claim_id']: v['disclosure'] for v in verdicts
                        if v['disclosure']},
    }
    return {'checker_version': CHECKER_VERSION,
            'bundle_id': bundle.get('bundle_id'),
            'snapshot_id': bundle.get('snapshot_id'),
            'verdicts': verdicts, 'summary': summary, 'publish': publish}


def apply_verdicts(bundle: dict, result: dict) -> dict:
    """裁决写回 claim.verification(契约§2 示例形状;原位返回)。"""
    vmap = {v['claim_id']: v for v in result.get('verdicts', [])}
    for c in bundle.get('claims', []):
        v = vmap.get(c['claim_id'])
        if v is None:
            continue
        c['verification'] = {
            'status': v['status'],
            'checked_against': 'snapshot+thresholds',
            'computed': v['computed'], 'delta': v['delta'],
            'tolerance': v['tolerance'],
            'checker_version': CHECKER_VERSION,
            'stale': v['stale'],
            'disclosure': v['disclosure'],
            'reasons': v['reasons'],
        }
        if v['nv_attribution']:
            c['verification']['nv_attribution'] = v['nv_attribution']
    return bundle


def timeout_policy(result: dict) -> dict:
    """§4 SEMANTIC_REVIEW 超时策略: 剔除存疑项+披露剔除后发布。"""
    queue = result['publish']['semantic_review_queue']
    if queue:
        return {'removed_claim_ids': list(queue),
                'disclosure': ('以下数值断言未能在时限内完成语义审计,按超时策略'
                               '剔除后发布(清单显式披露,§4): ' + ', '.join(queue))}
    return {'removed_claim_ids': [], 'disclosure': '无超时剔除项(语义审队列空)'}


# ── CLI(操作者验证用;零模型/零网络) ────────────────────────────────

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description='claims 六状态确定性验证(架构整改 T5)')
    ap.add_argument('bundle', help='claims bundle JSON 路径')
    ap.add_argument('snapshot', help='研究快照 JSON 路径')
    ap.add_argument('--out', default=None, help='验证结果输出路径(默认打印)')
    args = ap.parse_args(argv)
    with open(args.bundle, 'r', encoding='utf-8') as f:
        bundle = json.load(f)
    with open(args.snapshot, 'r', encoding='utf-8') as f:
        snap = json.load(f)
    res = verify_bundle(bundle, snapshot=snap)
    out = json.dumps({'summary': res['summary'], 'publish': res['publish']},
                     ensure_ascii=False, indent=1)
    if args.out:
        with open(args.out, 'w', encoding='utf-8') as f:
            json.dump(res, f, ensure_ascii=False, indent=1)
        print(out)
        print(f'→ {args.out}')
    else:
        print(out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
