# -*- coding: utf-8 -*-
"""Audit-R20 任务2: 发布日历(版本化事实文件)的读取与查询面。

历史可见性回归的根因: RELEASE_RULES 是「常规节奏」推定,给不出停摆/延误
这类**逐事件**事实——2025-11-18 锚下,规则会把 2025Q3 GDP(规则发布日
2025-10-29)与 2025-09 失业率(规则 2025-10-06)判成「已发布」,而实录是
该日只能看到二季度 GDP 与八月失业率 4.3%。本模块把 config/release_calendar.json
的条目作为**优先于规则**的事实面:

- first_publish(metric_id, obs_date) → 命中条目时返回
  {'first_publish': <最早可见日>, 'entry_id', 'basis', 'note'};未命中→None
  (调用方回落 RELEASE_RULES 推定)。
- 条目语义(与文件 spec 同文): 锚日≤not_published_as_of → 一律不可见;
  锚日>not_published_as_of → 最早可见日=first_publish_on_or_after
  (实际首发日未逐条实录,如实注记,不虚构精确日)。
- 文件缺失/损坏 → 返回空条目并打印告警(fail-open 到规则面+显式披露,
  不静默): 日历是「事实增密」,缺席不构成阻断,但告警必须可见。

零模型纪律: 本模块不生成判断文字;条目内容=版本化文件,修改须经独立
审计席复核(与 metric_registry 同级)。"""

import json
import os
import threading

_CAL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         'config', 'release_calendar.json')
_lock = threading.Lock()
_cache = {'mtime': None, 'entries': [], 'warned': False}


def _load(path=None):
    """读条目(mtime 缓存;失败→空表+一次性告警)。"""
    cal = path or _CAL_PATH
    try:
        mtime = os.path.getmtime(cal)
    except OSError:
        with _lock:
            if not _cache['warned']:
                print(f"⚠️ [release_calendar] 日历文件缺席({cal})——发布日回落"
                      f"RELEASE_RULES 推定(停摆/延误类逐事件事实不可用,如实披露)")
                _cache['warned'] = True
        return []
    with _lock:
        if _cache['mtime'] == mtime and _cache.get('path') == cal:
            return _cache['entries']
    try:
        with open(cal, encoding='utf-8') as f:
            doc = json.load(f)
        entries = doc.get('entries') or []
    except (OSError, ValueError) as e:
        with _lock:
            if not _cache['warned']:
                print(f"⚠️ [release_calendar] 日历文件不可读({cal}: "
                      f"{type(e).__name__})——发布日回落RELEASE_RULES推定")
                _cache['warned'] = True
        return []
    with _lock:
        _cache.update({'mtime': mtime, 'path': cal, 'entries': entries})
    return entries


def first_publish(metric_id, obs_date, path=None):
    """查询条目: (metric_id, obs_date) 命中 → 最早可见日与条目元数据。

    返回 None=无条目(调用方走 RELEASE_RULES 推定);命中返回
    {'first_publish': 'YYYY-MM-DD', 'entry_id', 'basis', 'note',
     'not_published_as_of': 'YYYY-MM-DD'}。obs_date 缺席→None(不推测)。"""
    if not metric_id or not obs_date:
        return None
    # Audit-R24 任务2: 同名命中多条目(精确实录 vs 区间保守界)→取
    # obs_from 最晚(最特定)条目——逐期实录优先于 REST-CONSERVATIVE
    # 推广界,平手按文件序。
    best = None
    for ent in _load(path):
        mids = ent.get('metric_ids') or ([ent['metric_id']] if ent.get('metric_id') else [])
        if metric_id not in mids:
            continue
        if not (ent.get('obs_from') <= obs_date <= ent.get('obs_to')):
            continue
        if best is None or ent.get('obs_from', '') > best.get('obs_from', ''):
            best = ent
    if best is None:
        return None
    return {
        'first_publish': best.get('first_publish_on_or_after'),
        'not_published_as_of': best.get('not_published_as_of'),
        'entry_id': best.get('entry_id'),
        'basis': best.get('basis'),
        'note': best.get('note'),
        'batch_id': best.get('batch_id'),
        # Audit-R28 任务2: 官方发布时刻(HH:MM)+官方实录旗标——仅随
        # 读者面显示(如 LPR 每月20日 09:00);可见性比较仍用日期字段。
        'time': best.get('time'),
        'official': best.get('official'),
    }


def final_publish(metric_id, obs_date, path=None):
    """Audit-R24 任务2: 两级发布(EA 快报/终值)的终值日查询。

    条目带 final_publish_on 时返回该日(官方实录);无条目/无字段→None
    (调用方回落规则推定)。零生成,纯文件面。"""
    return _final_from_entry(metric_id, obs_date, path)


def _final_from_entry(metric_id, obs_date, path):
    for ent in _load(path):
        mids = ent.get('metric_ids') or ([ent['metric_id']] if ent.get('metric_id') else [])
        if metric_id not in mids:
            continue
        if not (ent.get('obs_from') <= obs_date <= ent.get('obs_to')):
            continue
        return ent.get('final_publish_on')
    return None


def visible_publish_date(metric_id, obs_date, rule_publish, path=None):
    """统一入口: 日历条目优先,规则推定兜底。

    返回 (publish_date|None, basis_text)。basis_text 形如
    'calendar:RC-2025SHUTDOWN-GDP-Q3(user_directive)' 或
    'rule:<规则文本>'——随格披露,读者可核。规则面给不出发布日
    (rule_publish=None 且无条目)→(None,'unavailable')。"""
    ent = first_publish(metric_id, obs_date, path=path)
    if ent is not None:
        return (ent['first_publish'],
                f"calendar:{ent['entry_id']}({ent['basis']})")
    if rule_publish:
        return rule_publish, 'rule:推定'
    return None, 'unavailable'


# ── Audit-R22 任务1: 官方发布批次(一次发布事件关联多指标×多观测月) ──────
def _load_doc(path=None):
    """读整个日历文档(mtime 缓存与 _load 同路;失败→空档+告警)。"""
    cal = path or _CAL_PATH
    try:
        mtime = os.path.getmtime(cal)
    except OSError:
        return {}
    try:
        with open(cal, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def batch_of(metric_id, obs_date, path=None):
    """查询 (metric_id, obs_date) 命中条目所属的发布批次。

    返回 None=无批次(条目未挂批/无条目);命中返回批次 dict
    (batch_id/agency/release/published_on/metrics/obs_months/
    backfill_months/note)。批次=一次官方发布事件: 同批多指标
    (CPI 与核心CPI 同一份新闻稿)与一次补发两月(PCE 10+11月同稿)
    都以批次承载——同批指标的可见性整批一致。"""
    ent = first_publish(metric_id, obs_date, path=path)
    bid = (ent or {}).get('batch_id')
    if not bid:
        return None
    for b in _load_doc(path).get('batches') or []:
        if b.get('batch_id') == bid:
            out = dict(b)
            out['via_entry'] = ent['entry_id']
            return out
    return None


# ── Audit-R28 任务2: 政策记录条目面(决议/维持;官方目标核验) ──────────────
def policy_entries(path=None):
    """kind∈{policy_decision, policy_maintenance} 的条目全表。

    政策记录与发布条目同文件同 schema(v1.5.0): 决议条目带
    decision_date/effective_on/target_value;维持条目带 decision_date/
    target_value(确认维持——不改变序列值,但刷新核验覆盖截止)。
    时间语义判定(距上次调整/核验锚)在 freshness_policy.policy_
    decision_state;本面只做纯文件读取。"""
    return [e for e in _load(path)
            if e.get('kind') in ('policy_decision', 'policy_maintenance')]


def publish_instant(metric_id, obs_date, path=None):
    """命中条目的官方发布时刻('HH:MM')|None(条目 time 字段)。

    仅用于读者面显示「日期 时刻(官方实录)」;可见性/先后比较仍用
    日期字段——时刻不改变可见性判定口径(推定条目无时刻,如实缺席)。"""
    ent = first_publish(metric_id, obs_date, path=path)
    return (ent or {}).get('time')
