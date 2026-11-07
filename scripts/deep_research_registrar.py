#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P2-WP-A: 深研任务与假设登记器(P2 深研层第 1 实现包,append-only 记录族)

DESIGN docs/P2_DESIGN.md §七 WP-P2-A 行(L193-L197,并入步带入)确定性落地:
- §二任务模型: 三发起来源入口字段(S-1 异常升级/S-2 用户指定/S-3 跟踪触发,
  §2.1 L39-41,恰一)+生命周期状态机(DRAFT→ACTIVE→终态4种→TRACKING→ARCHIVED,
  §2.2 L46-52,事件溯源 append-only)+共享档案衔接(§2.3 L57-59);
- §4.1 假设登记: ≥2 相互竞争假设(单假设 DRAFT 拒收,L102)+每对假设 ≥1
  区分性判据(DP-6 定值=1,L103/L70);
- §6.1 条件登记: falsifiable_condition 字段五项(metric_id/operator/threshold/
  window/premise,L154-162)+阈值来源档三档(L158)+推导规则①④(L164:
  注册表缺席→ABSENT_REGISTRY 如实标;支持向/反证向);
- 登记型参数先登记后运行禁回改(DP-1 轮次预算双轨 N=5/DP-2 权重量表五级 1-5/
  DP-6 每对 ≥1;DESIGN §2.4 L65/L66/L70)——registered_params 落任务档,
  记录字节不可变+同 id 重放一律拒=结构性禁回改;
- snapshot_id+digest 内容级绑定: 注册时经 rp.digest_snapshot 重算(FIX-01 纪律,
  禁采声明值;B4 先例 research_archive.py:321),校验时快照文件名经
  ra.parse_snapshot_id 规范分解派生,结构性不可达 data/daily 原始采集档。

纪律: 零网络(纯标准库+项目既有模块复用调用);零 GLM/凭证/付费;append-only
(重复写入/改写一律拒,不区分内容,B4 §四行6 同款;修订=新记录 revision_of+
revision_reason);零墙钟入指纹(created_at 缺省 now 属登记落档时刻,测试显式注入)。
参数登记: docs/P2_WP_A_REPORT.md §零.4/§零.5(DP-1/2/6+P-A-01..P-A-12,
先登记后实现,运行后禁回改;P-A-04 勘误见 REPORT §三)。
"""
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import research_archive as ra       # WP-B4 共享档案(复用调用: parse_snapshot_id/validate_id_conventions/档案族根)
import research_provenance as rp    # R5(digest_snapshot 重算/复算)

# ══ 登记型参数定值(REPORT §零.4;登记定值即实现值,运行后禁回改) ═══════════

DP1_ROUND_BUDGET_DEFAULT = 5        # DP-1 (c) 双轨: 固定上限 N=5+提前终止
DP2_WEIGHT_SCALE = (1, 5)           # DP-2 (b) 五级=星级 1-5(证据分级 v2 同刻度)
DP6_MIN_DISCRIMINATING_PER_PAIR = 1  # DP-6 (a) 每对假设 ≥1 区分性判据

# ══ 载体与集合(P-A-01;挂共享档案 research_archive/ 族根) ═════════════════

ARCHIVE_FAMILY = ra.ARCHIVE_FAMILY              # "research_archive"(B4 载体先例,复用引用)
COLLECTION_TASKS = "deep_research_tasks"
COLLECTION_HYPOTHESES = "deep_research_hypotheses"
COLLECTION_CONDITIONS = "deep_research_conditions"
COLLECTION_EVENTS = "deep_research_events"
COLLECTIONS = (COLLECTION_TASKS, COLLECTION_HYPOTHESES,
               COLLECTION_CONDITIONS, COLLECTION_EVENTS)

DEFAULT_ARCHIVE_DIR = ra.DEFAULT_ARCHIVE_DIR     # data/research/research_archive(B4 同源根,复用引用)

TASK_RECORD_TYPE = "deep_research_task"
HYPOTHESIS_RECORD_TYPE = "deep_research_hypothesis"
CONDITION_RECORD_TYPE = "deep_research_condition"
EVENT_RECORD_TYPE = "deep_research_event"

TASK_ID_PREFIX = "RT-DR-"          # DP-3: RT- 族成员(满足 ra.TASK_REF_RE ^RT-\S+$)
HYPOTHESIS_ID_PREFIX = "HP-"
CONDITION_ID_PREFIX = "FC-"
EVENT_ID_PREFIX = "EV-"

STATUS_DRAFT = "DRAFT"
STATUS_ACTIVE = "ACTIVE"
TERMINAL_STATUSES = ("RESOLVED", "ALL_FALSIFIED", "INCONCLUSIVE", "SUPERSEDED")
STATUS_TRACKING = "TRACKING"
STATUS_ARCHIVED = "ARCHIVED"
HYPOTHESIS_STATUS_REGISTERED = "REGISTERED"

# §2.2 L46 状态图+§6.3(P-A-08 迁移表;事件溯源,任务档字节不可变)
ALLOWED_TRANSITIONS = {
    STATUS_DRAFT: {STATUS_ACTIVE},
    STATUS_ACTIVE: set(TERMINAL_STATUSES),
    "RESOLVED": {STATUS_TRACKING},
    "ALL_FALSIFIED": {STATUS_TRACKING},
    "INCONCLUSIVE": {STATUS_TRACKING},
    "SUPERSEDED": {STATUS_TRACKING},
    STATUS_TRACKING: {STATUS_ARCHIVED},
    STATUS_ARCHIVED: set(),
}

# ══ 词表(P-A-03/P-A-05;DESIGN §2.1 L41+§6.1 L157-L164 实读) ═══════════

CONDITION_OPERATORS = (">=", "<=", ">", "<")     # L157 沿 pred_op 词表
WINDOW_MODES = ("expiry", "touch")               # L159
THRESHOLD_SOURCES = ("registry_validation", "historical_quantile", "user_explicit")  # L158 三档
CONDITION_DIRECTIONS = ("supporting", "falsifying")  # L164④ 支持向/反证向
ORIGIN_TRIGGER_KINDS = ("thesis_invalidation",          # §2.1 S-3① 论点触发器
                        "prediction_adjudication",      # S-3② 预测到期裁决
                        "rejected_rating_proposal")     # S-3③ 评级提案拒写留档

STATUS_WRITTEN = "written"
STATUS_REJECTED_DUPLICATE = "rejected-duplicate"

CONDITION_FIELD_KEYS = ("metric_id", "operator", "threshold", "window", "premise")

# ══ 基础件(canonical 指纹;零墙钟入指纹) ═════════════════════════════════


def _canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True)


def _hash8(payload):
    return hashlib.sha256(_canonical(payload).encode('utf-8')).hexdigest()[:8]


def _now_iso():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def _ymd_of(created_at):
    return created_at[:10].replace("-", "")


def _collection_dir(archive_dir, collection):
    return os.path.join(str(archive_dir), ARCHIVE_FAMILY, collection)


# ══ ID 构造(P-A-06/P-A-07;确定性,重放幂等锚) ═══════════════════════════

def _origin_fingerprint_part(origin):
    """origin 恰一三类归一为 {kind: …, payload: …} 指纹件(P-A-03)。"""
    if "origin_anomaly" in origin:
        return {"kind": "origin_anomaly", "payload": origin["origin_anomaly"]}
    if "origin_query_id" in origin:
        return {"kind": "origin_query_id", "payload": origin["origin_query_id"]}
    return {"kind": "origin_trigger", "payload": origin["origin_trigger"]}


def make_task_id(question, origin, hypotheses, discriminating_criteria,
                 registered_params, created_at):
    """RT-DR-{YYYYMMDD}-{sha256[:8]}: 指纹=canonical{question,origin 归一,
    假设(statement+mechanism_story)升序集,判据集,registered_params};
    不含时间戳内容(ymd 仅取自 created_at 日期段,E2E-A make_task_id 同款
    确定性重放先例 research_task_manager.py:48-53)。"""
    fp = {
        "question": question,
        "origin": _origin_fingerprint_part(origin),
        "hypotheses": sorted(
            [{"statement": h["statement"], "mechanism_story": h["mechanism_story"]}
             for h in hypotheses], key=_canonical),
        "discriminating_criteria": sorted(
            [{"pair": sorted(c["pair"]), "criterion": c["criterion"]}
             for c in discriminating_criteria], key=_canonical),
        "registered_params": registered_params,
    }
    return f"{TASK_ID_PREFIX}{_ymd_of(created_at)}-{_hash8(fp)}"


def make_hypothesis_id(task_id, statement, mechanism_story, created_at):
    return f"{HYPOTHESIS_ID_PREFIX}{_ymd_of(created_at)}-{_hash8({'task_id': task_id, 'statement': statement, 'mechanism_story': mechanism_story})}"


def make_condition_id(hypothesis_id, cond, created_at):
    fields = {k: cond.get(k) for k in CONDITION_FIELD_KEYS}
    return f"{CONDITION_ID_PREFIX}{_ymd_of(created_at)}-{_hash8({'hypothesis_id': hypothesis_id, 'fields': fields})}"


def make_event_id(task_id, from_status, to_status, note, created_at):
    return f"{EVENT_ID_PREFIX}{_ymd_of(created_at)}-{_hash8({'task_id': task_id, 'from': from_status, 'to': to_status, 'note': note})}"


# ══ 校验件(issues 列表风格,B4 validate_* 同款;空=合法) ═════════════════

def _iso_date_str_ok(s):
    if not isinstance(s, str) or len(s) < 10:
        return False
    try:
        datetime.strptime(s[:10], "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_origin(origin):
    """三发起来源入口字段恰一(P-A-03;DESIGN §2.1 L39-41)。"""
    issues = []
    if not isinstance(origin, dict):
        return [f"origin须为dict: {type(origin).__name__}"]
    present = [k for k in ("origin_anomaly", "origin_query_id", "origin_trigger")
               if k in origin]
    if len(present) != 1:
        issues.append(f"origin入口字段须恰一(origin_anomaly|origin_query_id|"
                      f"origin_trigger),实得{len(present)}个: {sorted(present)}")
        return issues
    extra = set(origin) - {"origin_anomaly", "origin_query_id", "origin_trigger"}
    if extra:
        issues.append(f"origin含未登记键: {sorted(extra)}")
    if "origin_anomaly" in present:                     # S-1 L39
        oa = origin["origin_anomaly"]
        if not isinstance(oa, dict):
            issues.append("origin_anomaly须为dict{metric_id,snapshot_id}")
        else:
            if not isinstance(oa.get("metric_id"), str) or not oa.get("metric_id"):
                issues.append(f"origin_anomaly.metric_id须为非空string: {oa.get('metric_id')!r}")
            sid = oa.get("snapshot_id")
            if not isinstance(sid, str) or ra.parse_snapshot_id(sid) is None:
                issues.append(f"origin_anomaly.snapshot_id非规范"
                              f"(research_snapshot_YYYYMMDD[_vN]): {sid!r}")
    elif "origin_query_id" in present:                  # S-2 L40(严格 QB 格,复用 B4 校验面)
        issues.extend(ra.validate_id_conventions(
            origin_query_id=origin["origin_query_id"]))
    else:                                               # S-3 L41 三入口子类
        ot = origin["origin_trigger"]
        if not isinstance(ot, dict):
            issues.append("origin_trigger须为dict{kind,ref}")
        else:
            if ot.get("kind") not in ORIGIN_TRIGGER_KINDS:
                issues.append(f"origin_trigger.kind须为{'|'.join(ORIGIN_TRIGGER_KINDS)}: "
                              f"{ot.get('kind')!r}")
            if not isinstance(ot.get("ref"), str) or not ot.get("ref"):
                issues.append(f"origin_trigger.ref须为非空string: {ot.get('ref')!r}")
    return issues


def validate_condition(cond):
    """条件 schema 校验(§6.1 字段五项+来源档+方向;P-A-05)。"""
    issues = []
    if not isinstance(cond, dict):
        return [f"条件须为dict: {type(cond).__name__}"]
    if not isinstance(cond.get("metric_id"), str) or not cond.get("metric_id"):
        issues.append(f"metric_id须为非空string: {cond.get('metric_id')!r}")
    if cond.get("operator") not in CONDITION_OPERATORS:
        issues.append(f"operator须为{'|'.join(CONDITION_OPERATORS)}(DESIGN L157 pred_op 词表): "
                      f"{cond.get('operator')!r}")
    th = cond.get("threshold")
    if not isinstance(th, (int, float)) or isinstance(th, bool):
        issues.append(f"threshold须为number: {th!r}")
    w = cond.get("window")
    if not isinstance(w, dict) or w.get("mode") not in WINDOW_MODES:
        issues.append(f"window.mode须为{'|'.join(WINDOW_MODES)}(DESIGN L159): "
                      f"{(w or {}).get('mode') if isinstance(w, dict) else w!r}")
    else:
        extra = set(w) - {"mode", "deadline", "weeks"}
        if extra:
            issues.append(f"window含未登记键: {sorted(extra)}")
        has_deadline = "deadline" in w
        has_weeks = "weeks" in w
        if has_deadline == has_weeks:                   # deadline 或 weeks 恰一(L159「deadline或期限」)
            issues.append(f"window须恰携deadline|weeks之一: {sorted(w)}")
        if has_deadline and not _iso_date_str_ok(w["deadline"]):
            issues.append(f"window.deadline须为ISO日期字符串: {w['deadline']!r}")
        if has_weeks and (not isinstance(w["weeks"], int) or isinstance(w["weeks"], bool)
                          or w["weeks"] < 1):
            issues.append(f"window.weeks须为正整数: {w['weeks']!r}")
    prem = cond.get("premise")
    if prem is not None and (not isinstance(prem, str) or not prem):
        issues.append(f"premise须为非空string|null(DESIGN L160): {prem!r}")
    if cond.get("threshold_source") not in THRESHOLD_SOURCES:
        issues.append(f"threshold_source须为{'|'.join(THRESHOLD_SOURCES)}"
                      f"(DESIGN L158 三档): {cond.get('threshold_source')!r}")
    if cond.get("direction") not in CONDITION_DIRECTIONS:
        issues.append(f"direction须为{'|'.join(CONDITION_DIRECTIONS)}(DESIGN L164④): "
                      f"{cond.get('direction')!r}")
    return issues


def validate_hypothesis_specs(hypotheses):
    """假设规格集校验: 非空 statement/mechanism_story+statement 两两互异
    (结构性竞争代理;P-A-04;DESIGN §4.1 L102)。"""
    issues = []
    if not isinstance(hypotheses, list) or len(hypotheses) < 2:
        return [f"假设集须为list且 ≥2(单假设任务不予立项,DRAFT 校验拒收,"
                f"DESIGN L102/L194): 实得{len(hypotheses) if isinstance(hypotheses, list) else type(hypotheses).__name__}"]
    seen = {}
    for i, h in enumerate(hypotheses):
        if not isinstance(h, dict):
            issues.append(f"假设[{i}]须为dict")
            continue
        if not isinstance(h.get("statement"), str) or not h.get("statement"):
            issues.append(f"假设[{i}].statement须为非空string")
        elif h["statement"] in seen:
            issues.append(f"假设statement两两须互异(相互竞争的结构性代理,"
                          f"DESIGN L102): [{seen[h['statement']]}]与[{i}]同值"
                          f"{h['statement']!r}")
        else:
            seen[h["statement"]] = i
        if not isinstance(h.get("mechanism_story"), str) or not h.get("mechanism_story"):
            issues.append(f"假设[{i}].mechanism_story须为非空string(DESIGN L110)")
        for j, c in enumerate(h.get("conditions") or []):
            for s in validate_condition(c):
                issues.append(f"假设[{i}].conditions[{j}]: {s}")
        if not h.get("conditions"):
            issues.append(f"假设[{i}]须携 ≥1 条 falsifiable_condition"
                          f"(DESIGN L152 每假设 ≥1): 实得0")
    return issues


def validate_discriminating_criteria(hypotheses, criteria):
    """每对假设 ≥1 区分性判据(DP-6 定值=1;DESIGN §4.1 L103/L70)。
    criteria 项={pair:[statement_a,statement_b], criterion:string};
    pair 两成员须命中假设集,全 C(n,2) 对逐对覆盖检查。"""
    issues = []
    if not isinstance(criteria, list):
        return [f"discriminating_criteria须为list: {type(criteria).__name__}"]
    statements = [h["statement"] for h in hypotheses if isinstance(h, dict)]
    covered = set()
    for i, c in enumerate(criteria):
        if not isinstance(c, dict):
            issues.append(f"判据[{i}]须为dict")
            continue
        pair = c.get("pair")
        if (not isinstance(pair, list) or len(pair) != 2
                or not all(isinstance(p, str) for p in pair)):
            issues.append(f"判据[{i}].pair须为两条假设statement的list: {pair!r}")
            continue
        for p in pair:
            if p not in statements:
                issues.append(f"判据[{i}].pair成员未命中假设集: {p!r}")
        if pair[0] == pair[1]:
            issues.append(f"判据[{i}].pair两成员相同(非假设对): {pair!r}")
        if not isinstance(c.get("criterion"), str) or not c.get("criterion"):
            issues.append(f"判据[{i}].criterion须为非空string(若判据E为真则至多"
                          f"一假设存活,DESIGN L103)")
        covered.add(tuple(sorted(pair)))
    n = len(statements)
    for a in range(n):                                  # 全 C(n,2) 对逐对检查
        for b in range(a + 1, n):
            want = tuple(sorted((statements[a], statements[b])))
            hits = sum(1 for t in covered if t == want)
            if hits < DP6_MIN_DISCRIMINATING_PER_PAIR:
                issues.append(f"假设对[{statements[a]!r}×{statements[b]!r}]区分性判据"
                              f"不足(DP-6 定值每对 ≥{DP6_MIN_DISCRIMINATING_PER_PAIR},"
                              f"实得{hits};DESIGN L103)")
    return issues


def _validate_record_binding(record, issues):
    """记录级通用绑定校验: snapshot_id 规范+digest 16 位+id 格式(P-A-10)。"""
    sid = record.get("snapshot_id")
    if not isinstance(sid, str) or ra.parse_snapshot_id(sid) is None:
        issues.append(f"snapshot_id非规范(research_snapshot_YYYYMMDD[_vN]): {sid!r}")
    dg = record.get("digest_snapshot")
    if not isinstance(dg, str) or not ra.DIGEST_RE.match(dg or ""):
        issues.append(f"digest_snapshot格式非法(须R5十六位小写指纹): {dg!r}")
    ca = record.get("created_at")
    if not isinstance(ca, str) or not ra.qir.ISO_DATE_PREFIX_RE.match((ca or "")[:10]):
        issues.append(f"created_at须为ISO8601字符串: {ca!r}")
    return issues


def validate_task_record(record):
    """任务记录级全链校验(P-A-02)。"""
    issues = []
    if not isinstance(record, dict):
        return [f"记录须为dict: {type(record).__name__}"]
    keys = ("record_type", "task_id", "created_at", "status", "origin",
            "question", "hypothesis_ids", "discriminating_criteria",
            "condition_ids", "registered_params", "snapshot_id",
            "digest_snapshot", "history")
    for k in keys:
        if k not in record:
            issues.append(f"记录缺字段{k}(P-A-02)")
    if issues:
        return issues
    if record.get("record_type") != TASK_RECORD_TYPE:
        issues.append(f"record_type恒须字面量{TASK_RECORD_TYPE!r}: {record.get('record_type')!r}")
    if not isinstance(record.get("task_id"), str) or not record["task_id"].startswith(TASK_ID_PREFIX):
        issues.append(f"task_id须为{TASK_ID_PREFIX}*族成员: {record.get('task_id')!r}")
    if record.get("status") != STATUS_DRAFT:
        issues.append(f"任务档初始status恒须{STATUS_DRAFT!r}(迁移走事件记录,"
                      f"P-A-08): {record.get('status')!r}")
    if not isinstance(record.get("question"), str) or not record.get("question"):
        issues.append(f"question须为非空string: {record.get('question')!r}")
    issues.extend(validate_origin(record.get("origin") or {}))
    hp_ids = record.get("hypothesis_ids")
    if not isinstance(hp_ids, list) or len(hp_ids) < 2:
        issues.append(f"hypothesis_ids须为list且 ≥2: {hp_ids!r}")
    rp_ = record.get("registered_params") or {}
    if rp_.get("round_budget") != DP1_ROUND_BUDGET_DEFAULT:
        issues.append(f"registered_params.round_budget须等于登记定值"
                      f"{DP1_ROUND_BUDGET_DEFAULT}(DP-1): {rp_.get('round_budget')!r}")
    if list(rp_.get("weight_scale") or ()) != list(DP2_WEIGHT_SCALE):
        issues.append(f"registered_params.weight_scale须等于登记定值"
                      f"{list(DP2_WEIGHT_SCALE)}(DP-2): {rp_.get('weight_scale')!r}")
    if rp_.get("min_discriminating_per_pair") != DP6_MIN_DISCRIMINATING_PER_PAIR:
        issues.append(f"registered_params.min_discriminating_per_pair须等于登记定值"
                      f"{DP6_MIN_DISCRIMINATING_PER_PAIR}(DP-6): "
                      f"{rp_.get('min_discriminating_per_pair')!r}")
    his = record.get("history")
    if not isinstance(his, list) or not his:
        issues.append("history须为非空list(初始登记条目在场)")
    return _validate_record_binding(record, issues)


def validate_hypothesis_record(record):
    """假设记录级校验(P-A-04;勘误后字段集无 registry_status,见 REPORT §三)。"""
    issues = []
    if not isinstance(record, dict):
        return [f"记录须为dict: {type(record).__name__}"]
    keys = ("record_type", "hypothesis_id", "task_id", "created_at",
            "statement", "mechanism_story", "status", "revision_of",
            "revision_reason", "snapshot_id", "digest_snapshot", "history")
    for k in keys:
        if k not in record:
            issues.append(f"记录缺字段{k}(P-A-04)")
    if issues:
        return issues
    if record.get("record_type") != HYPOTHESIS_RECORD_TYPE:
        issues.append(f"record_type恒须字面量{HYPOTHESIS_RECORD_TYPE!r}")
    if not str(record.get("hypothesis_id", "")).startswith(HYPOTHESIS_ID_PREFIX):
        issues.append(f"hypothesis_id须为{HYPOTHESIS_ID_PREFIX}*族: {record.get('hypothesis_id')!r}")
    issues.extend(ra.validate_id_conventions(task_id=record.get("task_id")))
    if not isinstance(record.get("statement"), str) or not record.get("statement"):
        issues.append("statement须为非空string")
    if not isinstance(record.get("mechanism_story"), str) or not record.get("mechanism_story"):
        issues.append("mechanism_story须为非空string")
    if record.get("status") != HYPOTHESIS_STATUS_REGISTERED:
        issues.append(f"假设档初始status恒须{HYPOTHESIS_STATUS_REGISTERED!r}: "
                      f"{record.get('status')!r}")
    ro, rr = record.get("revision_of"), record.get("revision_reason")
    if (ro is None) != (rr is None):
        issues.append(f"revision_of与revision_reason须同缺省或同在(修订=新记录+原因,"
                      f"DESIGN L183): revision_of={ro!r} revision_reason={rr!r}")
    return _validate_record_binding(record, issues)


def validate_condition_record(record):
    """条件记录级校验(P-A-05;含 registry_status 词表)。"""
    issues = []
    if not isinstance(record, dict):
        return [f"记录须为dict: {type(record).__name__}"]
    keys = ("record_type", "condition_id", "task_id", "hypothesis_id",
            "created_at") + CONDITION_FIELD_KEYS + (
        "threshold_source", "source_note", "direction", "registry_status",
        "revision_of", "revision_reason", "snapshot_id", "digest_snapshot", "history")
    for k in keys:
        if k not in record:
            issues.append(f"记录缺字段{k}(P-A-05)")
    if issues:
        return issues
    if record.get("record_type") != CONDITION_RECORD_TYPE:
        issues.append(f"record_type恒须字面量{CONDITION_RECORD_TYPE!r}")
    if not str(record.get("condition_id", "")).startswith(CONDITION_ID_PREFIX):
        issues.append(f"condition_id须为{CONDITION_ID_PREFIX}*族: {record.get('condition_id')!r}")
    issues.extend(ra.validate_id_conventions(task_id=record.get("task_id")))
    if not str(record.get("hypothesis_id", "")).startswith(HYPOTHESIS_ID_PREFIX):
        issues.append(f"hypothesis_id须为{HYPOTHESIS_ID_PREFIX}*族: {record.get('hypothesis_id')!r}")
    cond_view = {k: record.get(k) for k in CONDITION_FIELD_KEYS}
    cond_view["threshold_source"] = record.get("threshold_source")
    cond_view["direction"] = record.get("direction")
    for s in validate_condition(cond_view):
        issues.append(s)
    if record.get("registry_status") not in ("RESOLVED", "ABSENT_REGISTRY"):
        issues.append(f"registry_status须为RESOLVED|ABSENT_REGISTRY: {record.get('registry_status')!r}")
    ro, rr = record.get("revision_of"), record.get("revision_reason")
    if (ro is None) != (rr is None):
        issues.append(f"revision_of与revision_reason须同缺省或同在: {ro!r}/{rr!r}")
    return _validate_record_binding(record, issues)


def validate_event_record(record):
    """事件记录级校验(P-A-08;过程记录,经 task_id 间接绑定,不带快照绑定面)。"""
    issues = []
    if not isinstance(record, dict):
        return [f"记录须为dict: {type(record).__name__}"]
    keys = ("record_type", "event_id", "task_id", "created_at", "seq",
            "from_status", "to_status", "note", "trigger_ref")
    for k in keys:
        if k not in record:
            issues.append(f"记录缺字段{k}(P-A-08)")
    if issues:
        return issues
    if record.get("record_type") != EVENT_RECORD_TYPE:
        issues.append(f"record_type恒须字面量{EVENT_RECORD_TYPE!r}")
    if not str(record.get("event_id", "")).startswith(EVENT_ID_PREFIX):
        issues.append(f"event_id须为{EVENT_ID_PREFIX}*族: {record.get('event_id')!r}")
    issues.extend(ra.validate_id_conventions(task_id=record.get("task_id")))
    sq = record.get("seq")
    if not isinstance(sq, int) or isinstance(sq, bool) or sq < 1:
        issues.append(f"seq须为正整数(同任务单调序,P-A-08): {sq!r}")
    if (record.get("from_status"), record.get("to_status")) not in _all_transition_pairs():
        issues.append(f"迁移{record.get('from_status')!r}→{record.get('to_status')!r}"
                      f"不在登记迁移表(P-A-08)")
    elif record.get("from_status") is None and sq != 1:
        issues.append(f"初始登记事件(None→DRAFT)恒须seq=1: 实得seq={sq}")
    if not isinstance(record.get("note"), str) or not record.get("note"):
        issues.append("note须为非空string")
    if record.get("trigger_ref") is not None and (not isinstance(record.get("trigger_ref"), str)
                                                  or not record.get("trigger_ref")):
        issues.append(f"trigger_ref须为非空string|null: {record.get('trigger_ref')!r}")
    ca = record.get("created_at")
    if not isinstance(ca, str) or not ra.qir.ISO_DATE_PREFIX_RE.match((ca or "")[:10]):
        issues.append(f"created_at须为ISO8601字符串: {ca!r}")
    return issues


def _all_transition_pairs():
    """登记迁移对全集=初始登记对(None→DRAFT,任务档诞生事件)+迁移表全对。"""
    return ({(None, STATUS_DRAFT)}
            | {(f, t) for f, targets in ALLOWED_TRANSITIONS.items() for t in targets})


# ══ 注册表身份实读(条件 metric_id → RESOLVED|ABSENT_REGISTRY;L164①) ═════


def _registry_status_of(metric_id):
    """经 fact_engine.metric 注册表实读;缺席→ABSENT_REGISTRY 如实标(不以相近
    指标冒充,不拒收——缺席路径语义,DESIGN L164①)。"""
    import fact_engine as fe                    # 惰性导入(rtm.py:67 同款先例)
    try:
        return "RESOLVED" if fe.metric(metric_id) is not None else "ABSENT_REGISTRY"
    except Exception:
        return "ABSENT_REGISTRY"


# ══ append-only 落档(P-A-09;重复写入/改写一律拒,B4 §四行6 同款) ════════


def _write_records(planned, archive_dir):
    """预检全部目标路径不存在后原子落盘(拒绝时零写入,无部分落档)。"""
    for _, path in planned:
        if os.path.exists(path):
            return STATUS_REJECTED_DUPLICATE, path
    for record, path in planned:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        _tmp = path + '.tmp'
        with open(_tmp, 'w', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False, indent=1, sort_keys=True)
        os.replace(_tmp, path)
    return STATUS_WRITTEN, planned[-1][1]


def _record_path(archive_dir, collection, record_id):
    return os.path.join(_collection_dir(archive_dir, collection), f"{record_id}.json")


# ══ 登记入口(DRAFT;§2.2 L49 五要件) ═════════════════════════════════════

def register_deep_research_task(question, origin, hypotheses,
                                discriminating_criteria, snapshot, *,
                                archive_dir=None, created_at=None):
    """深研任务 DRAFT 登记(append-only 记录族一次成套落档)。

    hypotheses=[{statement, mechanism_story, conditions:[条件dict]}];
    discriminating_criteria=[{pair:[statement_a,statement_b], criterion}];
    snapshot=携 snapshot_id 的 dict(digest 由模块经 R5 重算,API 无 digest 入参)。
    校验全过 → 写 假设/条件/任务/初始事件 四类记录;任一 id 已存在 →
    rejected-duplicate(零写入)。schema 违规=ValueError fail-loud。
    返回 {status, task_id, task_path, digest_snapshot, registered_params,
    hypothesis_ids, condition_ids, event_id}。
    """
    # ① 校验面(全部通过才进入写入,无部分落档)
    if not isinstance(question, str) or not question:
        raise ValueError(f"question须为非空string: {question!r}")
    issues = []
    issues += validate_origin(origin)
    issues += validate_hypothesis_specs(hypotheses)
    if not issues:                                        # 假设集合法才检查判据覆盖
        issues += validate_discriminating_criteria(hypotheses, discriminating_criteria)
    if issues:
        raise ValueError("深研任务DRAFT登记未过校验(fail-loud): " + ";".join(issues))
    if not isinstance(snapshot, dict) or not snapshot.get("snapshot_id"):
        raise ValueError("snapshot须为携带snapshot_id的dict(注入绑定面,P-A-10)")
    sid = str(snapshot["snapshot_id"])
    if ra.parse_snapshot_id(sid) is None:
        raise ValueError(f"snapshot.snapshot_id非规范: {sid!r}")
    digest = rp.digest_snapshot(snapshot)                 # R5 重算(FIX-01,禁采声明值)

    # ② 登记型参数(定值即实现值;echo=常量=登记三方一致,REPORT §零.4)
    registered_params = {"round_budget": DP1_ROUND_BUDGET_DEFAULT,
                         "weight_scale": list(DP2_WEIGHT_SCALE),
                         "min_discriminating_per_pair": DP6_MIN_DISCRIMINATING_PER_PAIR}
    ca = created_at or _now_iso()
    task_id = make_task_id(question, origin, hypotheses, discriminating_criteria,
                           registered_params, ca)

    # ③ 记录族构造(假设→条件→任务→初始事件)
    planned = []
    hp_ids, cond_ids, hp_by_statement = [], [], {}
    for h in hypotheses:
        hp_id = make_hypothesis_id(task_id, h["statement"], h["mechanism_story"], ca)
        hp_ids.append(hp_id)
        hp_by_statement[h["statement"]] = hp_id
        planned.append(({"record_type": HYPOTHESIS_RECORD_TYPE,
                         "hypothesis_id": hp_id, "task_id": task_id,
                         "created_at": ca, "statement": h["statement"],
                         "mechanism_story": h["mechanism_story"],
                         "status": HYPOTHESIS_STATUS_REGISTERED,
                         "revision_of": None, "revision_reason": None,
                         "snapshot_id": sid, "digest_snapshot": digest,
                         "history": [{"ts": ca, "note": "DRAFT 登记: 假设登记入档"
                                      "(append-only,不可改写;修订=新记录+原因)"}]},
                        _record_path(archive_dir or DEFAULT_ARCHIVE_DIR,
                                     COLLECTION_HYPOTHESES, hp_id)))
        for c in h["conditions"]:
            fc_id = make_condition_id(hp_id, c, ca)
            cond_ids.append(fc_id)
            fields = {k: c.get(k) for k in CONDITION_FIELD_KEYS}
            planned.append(({"record_type": CONDITION_RECORD_TYPE,
                             "condition_id": fc_id, "task_id": task_id,
                             "hypothesis_id": hp_id, "created_at": ca,
                             **fields,
                             "threshold_source": c["threshold_source"],
                             "source_note": c.get("source_note"),
                             "direction": c["direction"],
                             "registry_status": _registry_status_of(c["metric_id"]),
                             "revision_of": None, "revision_reason": None,
                             "snapshot_id": sid, "digest_snapshot": digest,
                             "history": [{"ts": ca, "note": "DRAFT 登记: falsifiable"
                                          "_condition 登记入档(一经登记禁回改,"
                                          "修订=新条件记录+原因,DESIGN L164)"}]},
                            _record_path(archive_dir or DEFAULT_ARCHIVE_DIR,
                                         COLLECTION_CONDITIONS, fc_id)))
    task_record = {"record_type": TASK_RECORD_TYPE,
                   "task_id": task_id, "created_at": ca, "status": STATUS_DRAFT,
                   "origin": origin, "question": question,
                   "hypothesis_ids": hp_ids,
                   "discriminating_criteria": [
                       {"pair": [hp_by_statement[p] for p in c["pair"]],
                        "criterion": c["criterion"]} for c in discriminating_criteria],
                   "condition_ids": cond_ids,
                   "registered_params": registered_params,
                   "snapshot_id": sid, "digest_snapshot": digest,
                   "history": [{"ts": ca, "from": None, "to": STATUS_DRAFT,
                                "note": "DRAFT 登记: 研究问题+≥2 竞争假设+区分性判据"
                                "+falsifiable_conditions+轮次预算(§2.2 L49 五要件)"}]}
    planned.append((task_record, _record_path(archive_dir or DEFAULT_ARCHIVE_DIR,
                                              COLLECTION_TASKS, task_id)))
    event_id = make_event_id(task_id, None, STATUS_DRAFT,
                             "DRAFT 登记事件(初始)", ca)
    planned.append(({"record_type": EVENT_RECORD_TYPE, "event_id": event_id,
                     "task_id": task_id, "created_at": ca, "seq": 1,
                     "from_status": None, "to_status": STATUS_DRAFT,
                     "note": "DRAFT 登记事件(初始)", "trigger_ref": None},
                    _record_path(archive_dir or DEFAULT_ARCHIVE_DIR,
                                 COLLECTION_EVENTS, event_id)))

    # ④ 记录级校验(写入前全链复检)
    for record, _ in planned:
        _v = {TASK_RECORD_TYPE: validate_task_record,
              HYPOTHESIS_RECORD_TYPE: validate_hypothesis_record,
              CONDITION_RECORD_TYPE: validate_condition_record,
              EVENT_RECORD_TYPE: validate_event_record}[record["record_type"]]
        v_issues = _v(record)
        if v_issues:
            raise ValueError(f"记录未过schema校验(fail-loud) "
                             f"{record.get('task_id') or record.get('event_id')}: "
                             + ";".join(v_issues))

    # ⑤ append-only 落档(预检零存在→原子写;同 id 一律拒)
    ad = archive_dir or DEFAULT_ARCHIVE_DIR
    status, last_path = _write_records(planned, ad)
    return {"status": status, "task_id": task_id,
            "task_path": _record_path(ad, COLLECTION_TASKS, task_id),
            "digest_snapshot": digest, "registered_params": registered_params,
            "hypothesis_ids": hp_ids, "condition_ids": cond_ids,
            "event_id": event_id, "last_path": last_path}


# ══ 生命周期事件(P-A-08;迁移表+当前态推导) ═════════════════════════════


def load_task(task_id, archive_dir=None):
    return _load_record(task_id, COLLECTION_TASKS, archive_dir,
                        "深研任务", validate_task_record)


def _load_record(record_id, collection, archive_dir, label, validator):
    path = _record_path(archive_dir or DEFAULT_ARCHIVE_DIR, collection, record_id)
    if not os.path.exists(path):
        raise FileNotFoundError(f"{label}记录缺档: {record_id}")
    with open(path, 'r', encoding='utf-8') as f:
        record = json.load(f)
    issues = validator(record)
    if issues:
        raise ValueError(f"{label}记录档内校验失败({record_id}): " + ";".join(issues))
    return record


def list_events(task_id, archive_dir=None):
    """任务全部事件记录(按 seq 同任务单调序排序;P-A-08 勘误后定序键)。"""
    d = _collection_dir(archive_dir or DEFAULT_ARCHIVE_DIR, COLLECTION_EVENTS)
    out = []
    if os.path.isdir(d):
        for name in os.listdir(d):
            if not name.endswith(".json") or name.startswith("."):
                continue
            with open(os.path.join(d, name), 'r', encoding='utf-8') as f:
                rec = json.load(f)
            if rec.get("task_id") == task_id:
                out.append(rec)
    return sorted(out, key=lambda r: r.get("seq", 0))


def _next_event_seq(task_id, archive_dir):
    """同任务事件单调配号: 现存最大 seq+1(B4 同日单调先例 research_archive.py:282-290)。"""
    best = 0
    for rec in list_events(task_id, archive_dir):
        s = rec.get("seq")
        if isinstance(s, int) and not isinstance(s, bool):
            best = max(best, s)
    return best + 1


def current_status(task_id, archive_dir=None):
    """当前态=任务档初始 DRAFT+事件流按 seq 折叠(append-only 推导,不改档)。"""
    task = load_task(task_id, archive_dir)
    status = task["status"]
    for ev in list_events(task_id, archive_dir):
        if ev["to_status"] is not None:
            status = ev["to_status"]
    return status


def append_lifecycle_event(task_id, from_status, to_status, note, *,
                           trigger_ref=None, archive_dir=None, created_at=None):
    """迁移事件 append-only 追加: from=当前态(推导)、(from→to)∈登记迁移表。"""
    task = load_task(task_id, archive_dir)                # 任务须在场且档内合法
    cur = current_status(task_id, archive_dir)
    if from_status != cur:
        raise ValueError(f"from_status={from_status!r}与当前推导态{cur!r}不一致"
                         f"(事件溯源,禁跳态)")
    if to_status not in ALLOWED_TRANSITIONS.get(from_status, set()):
        raise ValueError(f"非法迁移{from_status!r}→{to_status!r}(登记迁移表 P-A-08: "
                         f"{ {k: sorted(v) for k, v in ALLOWED_TRANSITIONS.items()} })")
    if not isinstance(note, str) or not note:
        raise ValueError("note须为非空string")
    ca = created_at or _now_iso()
    seq = _next_event_seq(task_id, archive_dir)
    event_id = make_event_id(task_id, from_status, to_status, note, ca)
    record = {"record_type": EVENT_RECORD_TYPE, "event_id": event_id,
              "task_id": task_id, "created_at": ca, "seq": seq,
              "from_status": from_status,
              "to_status": to_status, "note": note, "trigger_ref": trigger_ref}
    issues = validate_event_record(record)
    if issues:
        raise ValueError("事件记录未过schema校验(fail-loud): " + ";".join(issues))
    status, _ = _write_records(
        [(record, _record_path(archive_dir or DEFAULT_ARCHIVE_DIR,
                               COLLECTION_EVENTS, event_id))],
        archive_dir or DEFAULT_ARCHIVE_DIR)
    return {"status": status, "event_id": event_id,
            "from_status": from_status, "to_status": to_status}


# ══ 修订(新记录+原因;DESIGN L183/L164,P-A-09) ═════════════════════════

def revise_hypothesis(task_id, hypothesis_id, statement, mechanism_story,
                      reason, snapshot, *, archive_dir=None, created_at=None):
    """实质新假设=新假设记录+新ID(关联引用原假设;原记录不可改写,L183)。"""
    if not isinstance(reason, str) or not reason:
        raise ValueError("修订必携修订原因(DESIGN L183)")
    _load_record(hypothesis_id, COLLECTION_HYPOTHESES, archive_dir,
                 "假设", validate_hypothesis_record)      # 原记录须在场
    if not isinstance(snapshot, dict) or not snapshot.get("snapshot_id"):
        raise ValueError("snapshot须为携带snapshot_id的dict")
    sid = str(snapshot["snapshot_id"])
    if ra.parse_snapshot_id(sid) is None:
        raise ValueError(f"snapshot.snapshot_id非规范: {sid!r}")
    digest = rp.digest_snapshot(snapshot)
    ca = created_at or _now_iso()
    new_id = make_hypothesis_id(task_id, statement, mechanism_story, ca)
    record = {"record_type": HYPOTHESIS_RECORD_TYPE, "hypothesis_id": new_id,
              "task_id": task_id, "created_at": ca, "statement": statement,
              "mechanism_story": mechanism_story,
              "status": HYPOTHESIS_STATUS_REGISTERED,
              "revision_of": hypothesis_id, "revision_reason": reason,
              "snapshot_id": sid, "digest_snapshot": digest,
              "history": [{"ts": ca, "note": f"修订登记: 承接原假设{hypothesis_id}"
                           f"(新记录+新ID,原记录不可改写;原因: {reason})"}]}
    issues = validate_hypothesis_record(record)
    if issues:
        raise ValueError("修订假设记录未过schema校验: " + ";".join(issues))
    status, _ = _write_records(
        [(record, _record_path(archive_dir or DEFAULT_ARCHIVE_DIR,
                               COLLECTION_HYPOTHESES, new_id))],
        archive_dir or DEFAULT_ARCHIVE_DIR)
    return {"status": status, "hypothesis_id": new_id,
            "revision_of": hypothesis_id}


# ══ 快照绑定校验(要点④;篡改→拒绝) ═════════════════════════════════════

def _load_snapshot_for_verify(snapshot_id, snapshot_dir):
    """按 snapshot_id 规范分解派生文件名加载快照(唯一快照读取面;
    复用 ra.parse_snapshot_id 身份分解,文件名构造结构性不可达 data/daily,
    B4 _load_snapshot_for_binding 同款纪律)。"""
    parsed = ra.parse_snapshot_id(snapshot_id)
    if parsed is None:
        return None, f"snapshot_id非规范: {snapshot_id!r}"
    ymd, ver = parsed
    suffix = "" if ver == 1 else f"_v{ver}"
    fname = f"research_snapshot_{ymd}{suffix}.json"
    path = os.path.join(str(snapshot_dir), fname)
    if not os.path.exists(path):
        return None, f"快照文件缺失: {fname}"
    try:
        with open(path, 'r', encoding='utf-8') as f:
            snap = json.load(f)
    except Exception as e:
        return None, f"快照文件JSON不可解析({fname}): {e}"
    if not isinstance(snap, dict) or not snap.get("snapshot_id"):
        return None, f"快照结构非法(缺snapshot_id): {fname}"
    if str(snap.get("snapshot_id")) != snapshot_id:
        return None, (f"内部snapshot_id={snap.get('snapshot_id')!r}与档案引用"
                      f"{snapshot_id!r}不符(R1身份纪律)")
    return snap, None


def verify_task_bindings(task_id, snapshot_dir, archive_dir=None):
    """任务记录族(任务+假设+条件)快照绑定逐档复核: 记录级校验+快照加载+
    R5 digest 复算对照;→ (ok, issues)。篡改快照→digest 不匹配→拒绝。"""
    issues = []
    try:
        task = load_task(task_id, archive_dir)
    except (FileNotFoundError, ValueError) as e:
        return False, [f"任务记录不可用: {e}"]
    snap, load_err = _load_snapshot_for_verify(task["snapshot_id"], snapshot_dir)
    if snap is None:
        return False, [load_err]
    digest = rp.digest_snapshot(snap)                     # R5 复算
    for label, rec in [("task", task)]:
        if rec.get("digest_snapshot") != digest:
            issues.append(f"{label}记录digest不匹配(快照内容与档案绑定漂移/篡改嫌疑,"
                          f"snapshot_id={rec['snapshot_id']}): 档案登记"
                          f"{rec['digest_snapshot']} vs 实测{digest}")
    ad = archive_dir or DEFAULT_ARCHIVE_DIR
    for hp_id in task["hypothesis_ids"]:
        try:
            hp = _load_record(hp_id, COLLECTION_HYPOTHESES, ad, "假设",
                              validate_hypothesis_record)
        except (FileNotFoundError, ValueError) as e:
            issues.append(f"假设记录不可用({hp_id}): {e}")
            continue
        if hp["digest_snapshot"] != digest:
            issues.append(f"假设记录digest不匹配({hp_id}): 档案登记"
                          f"{hp['digest_snapshot']} vs 实测{digest}")
    for fc_id in task["condition_ids"]:
        try:
            fc = _load_record(fc_id, COLLECTION_CONDITIONS, ad, "条件",
                              validate_condition_record)
        except (FileNotFoundError, ValueError) as e:
            issues.append(f"条件记录不可用({fc_id}): {e}")
            continue
        if fc["digest_snapshot"] != digest:
            issues.append(f"条件记录digest不匹配({fc_id}): 档案登记"
                          f"{fc['digest_snapshot']} vs 实测{digest}")
    return (not issues), issues
