#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P2-WP-C: 跟踪触发与 GLM 综合对接(P2 深研层第 3 实现包,确定性结构)

DESIGN docs/P2_DESIGN.md §七 WP-P2-C 行(L205-L209,基线工作树实读)确定性落地:
- §2.1 S-3 跟踪触发入口(L41,入口子类 3 个): 论点触发器(终态门禁反向面,
  引擎核验已触发者方可入口,report_generator.py L503-504 先例)/预测裁决
  (到期裁决+前提兑现转观察中,四态裁决词表 L534/五态口径 allocation_engine.py
  L1066)/拒写提案(评级变更门禁被拒留档,L522/L1099 先例)——触发监听=事件
  intake+schema 校验+append-only 触发档;「触发后再研究」=经 drr 登记新任务
  (任务档携 origin_trigger,DESIGN L41 记录衔接列);
- §6.2 条件程序评估(L168-L170): 程序判定、观察记录驱动、终态不参与观察;
  口径与每日观察先例一致(daily_prediction_observer.py L122-131 先例)——
  **观察窗内观测才参与裁决**(report_generator.py L537+allocation_engine.py
  L819-L826 _window_obs 同款窗口过滤),touch 触及可提前/expiry 截止日未到
  不得提前裁决(L538 同款)/窗内零可用观测=数据不足不硬判(L903-906 同款),
  premise 兑现才开窗且截止日不顺延(allocation_engine.py L762-L764 同款),
  比较符复用 ae.COMPARATORS(L95-101,同一代码路径);
- §6.3 结论状态机(L174-L185): 未裁决→PARTIAL_SUPPORT(部分支持)/
  PARTIAL_FALSIFIED(部分证伪)(轮次中)→终态 CONFIRMED(窗口内支持向条件
  成立且无未解释重大反证——反证旗经 dm.assemble_matrix 复用汇编)/FALSIFIED
  (证伪向条件触发)/EXPIRED_UNRESOLVED(窗口结束未触发)/INCONCLUSIVE
  (数据阻断);确定性优先序 FALSIFIED>CONFIRMED>EXPIRED_UNRESOLVED>
  INCONCLUSIVE(P-C-10/P-C-11);终态后再评一律拒收(FALSIFIED 不可改写、
  终态不可重开,L183+_is_final_prediction L691-L709 先例);
- §6.3 证伪后处置(L182-L185,路径 3 条): ①标记=FALSIFIED 结论档本身
  (字节不可改写),实质新假设=drr.revise_hypothesis(新记录+新ID+revision_of
  关联引用原假设);②关联论点/观点触发复核=review_request 留档(终态门禁
  正向流程: 触发器被引擎核验或≥2 项新增独立证据,L503 同款;**深研层不直接
  改写状态**,零 thesis/allocation/prediction 状态档读写路径);③跟踪处置=
  TRACKING→ARCHIVED 经 drr.append_lifecycle_event 既有迁移表;可选闭环后续
  任务经 S-3 origin_trigger 发起(触发档先行,模块不发明触发);
- §五 GLM 综合能力级对接(L135-L144)=仅接口预留: 输入构建器(证据矩阵+
  假设集+快照 digest 绑定,字段名与 R019 GLMResearchInput 对齐
  [P03_W2_GLM_DESIGN.md §三(a) L62-L70,跨支只读实读])+轻量输出契约校验
  (≥2 竞争假设+每假设 falsifiable_conditions≥1+confidence 三档+absent_ack,
  R019 §三(c) L102;**R019 WP-G2 结构化输出校验器全量面不在本包重复实现**)
  +适配器协议+PENDING 桩(缺席登记返回,R019 §三(b)3 同款: 不部分产出、
  不静默跳过、状态不因此推进)+显式依赖注入点;**零真实 GLM/LLM 调用、
  零网络出站、零凭证、零付费**(真实调用面=DP-4 确认权留用户,PENDING)。

上游复用(对齐=复用调用,禁复制分叉): WP-P2-A deep_research_registrar
(ORIGIN_TRIGGER_KINDS 词表/DP-1/2/6 定值常量/register_deep_research_task/
revise_hypothesis/append_lifecycle_event/current_status 折叠范式/
_load_snapshot_for_verify/_write_records/_record_path/_hash8/_canonical);
WP-P2-B deep_research_matrix_engine(assemble_matrix summary 未解释重大反证/
FACT_QUALITY_REJECTED 词表);生命周期迁移全经 drr 既有状态保护机制转递,
本包零新增任务状态值零改写迁移表;研究状态(thesis/allocation/prediction)
零直改(§6.2 L169「回写必须经 Gate B 状态保护门禁」,data_validator.py
L372-L377 FAIL→禁止一切长期状态回写先例)。

纪律: 零网络(import 面纯标准库+项目既有模块,零 requests/urllib/socket/
http/openai);零 GLM/凭证/付费;append-only(同 id 重放一律拒,零部分写入);
零墙钟入指纹(ymd 仅取 created_at 日期段;评估 as_of 为显式必填参数,禁墙钟
判定);快照纪律(一切快照读取经 drr._load_snapshot_for_verify 规范分解派生,
结构性不可达 data/daily 原始采集档,源码零路径字面);数据不足不填 0,缺值
条件 DATA_INSUFFICIENT 不硬判(§八 L228 如实纪律);本包任何输出不构成投资
建议(DESIGN §八 L225 红线)。
参数登记: docs/P2_WP_C_REPORT.md §零.4/§零.5(DP-1/2/6 复用上游定值+
P-C-01..P-C-18,先登记后实现,运行后禁回改)。
"""
import json
import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deep_research_registrar as drr   # WP-P2-A 上游(复用调用,只读禁改)
import deep_research_matrix_engine as dm  # WP-P2-B 上游(复用调用,只读禁改)
import research_provenance as rp        # R5 digest_snapshot/R3 gate_allows_formal_research
import allocation_engine as ae          # COMPARATORS/ALLOWED_RATINGS(同构复用)
import research_archive as ra           # 经 drr 转递(parse_snapshot_id/DIGEST_RE)

# ══ 载体与集合(P-C-01;挂共享档案族根,不占用上游既有 6 集合名) ═════════

ARCHIVE_FAMILY = drr.ARCHIVE_FAMILY                    # "research_archive"(复用引用)
COLLECTION_TRIGGERS = "deep_research_triggers"
COLLECTION_CONCLUSIONS = "deep_research_conclusions"
COLLECTION_DISPOSALS = "deep_research_disposals"
DEFAULT_ARCHIVE_DIR = drr.DEFAULT_ARCHIVE_DIR          # data/research/research_archive

TRIGGER_RECORD_TYPE = "deep_research_trigger"
CONCLUSION_RECORD_TYPE = "deep_research_conclusion"
DISPOSAL_RECORD_TYPE = "deep_research_disposal"

TRIGGER_ID_PREFIX = "TRG-"        # DP-3: 避开上游已占 RT-DR-/HP-/FC-/EV-/EVI-/RD-
CONCLUSION_ID_PREFIX = "CON-"
DISPOSAL_ID_PREFIX = "DSP-"

# ══ 词表(P-C-03/P-C-04;DESIGN §2.1 L41+先例锚点实读) ═════════════════

TRIGGER_KINDS = tuple(drr.ORIGIN_TRIGGER_KINDS)   # 3 子类(上游 WP-A P-A-03 登记)
THESIS_ENGINE_STATUS_REQUIRED = "triggered"       # S-3①: 仅引擎核验已触发者入口(L503)
PREDICTION_EVENTS = ("adjudicated", "premise_fulfilled")   # S-3②: 到期裁决/前提兑现转观察中
PREDICTION_VERDICTS = ("hit", "miss", "inconclusive", "not_yet_triggered")  # L534 四态
PROPOSAL_GATE_STATUS_REQUIRED = "rejected"        # S-3③: 被拒提案留档(L522/L1099)
RATING_VOCABULARY = tuple(ae.ALLOWED_RATINGS)     # 评级 4 档(allocation_engine L63)

# 结论状态机(P-C-10;DESIGN §6.3 L174-L180 逐字枚举)
CONCLUSION_STATUS_UNADJUDICATED = "UNADJUDICATED"          # 未裁决(无记录默认)
CONCLUSION_INTERMEDIATE = ("PARTIAL_SUPPORT", "PARTIAL_FALSIFIED")  # 部分支持/部分证伪(轮次中)
CONCLUSION_TERMINAL = ("CONFIRMED", "FALSIFIED", "EXPIRED_UNRESOLVED", "INCONCLUSIVE")
CONCLUSION_STATUSES = (CONCLUSION_STATUS_UNADJUDICATED,) + CONCLUSION_INTERMEDIATE + CONCLUSION_TERMINAL

# 条件评估结局词表(P-C-07/P-C-08)
COND_TRIGGERED = "TRIGGERED"                 # 窗口内成立(touch 触及/expiry 期终满足)
COND_NOT_TRIGGERED = "NOT_TRIGGERED"         # 窗口闭合且不成立(数据充分)
COND_PENDING = "PENDING"                     # 窗口未闭合,不得提前裁决(expiry)
COND_NOT_YET_IN_WINDOW = "NOT_YET_IN_WINDOW"  # 带前提未兑现,观察期未开始
COND_NOT_ACTIVATED = "NOT_ACTIVATED"         # 前提晚于截止日兑现,不激活不顺延
COND_DATA_INSUFFICIENT = "DATA_INSUFFICIENT"  # 窗内零可用观测,数据不足不硬判
COND_OUTCOMES = (COND_TRIGGERED, COND_NOT_TRIGGERED, COND_PENDING,
                 COND_NOT_YET_IN_WINDOW, COND_NOT_ACTIVATED, COND_DATA_INSUFFICIENT)
_COND_DECIDED = (COND_TRIGGERED, COND_NOT_TRIGGERED, COND_DATA_INSUFFICIENT)  # 窗口已闭合类

# GLM 接口预留(P-C-14;R019 定稿字段面对齐,跨支只读实读 2026-11-07)
GLM_INPUT_CONTRACT_VERSION = "p2-gsi-1.0"     # 输入契约版本(标识符,非数据值)
GLM_OUTPUT_CONFIDENCE_LEVELS = ("high", "medium", "low")   # R019 §三(c) L102 三档
GLM_PENDING_STATUS = "ABSENT_PENDING_APPROVAL"             # 缺席登记(R019 §三(b)3)
GLM_MIN_COMPETING_HYPOTHESES = 2             # 强制项(DESIGN L141 ≥2)
GLM_REAL_CALL_FACE = "PENDING_USER_APPROVAL(DP-4)"         # 真实调用面=未批零调用


# ══ 基础件(上游原语复用;零墙钟入指纹,P-C-02/P-C-18) ══════════════════


def _now_iso():
    return drr._now_iso()


def make_trigger_id(kind, ref, payload, created_at):
    """TRG-{YYYYMMDD}-{sha256[:8]}: 指纹={kind,ref,payload} canonical;不含墙钟
    (ymd 仅取自 created_at 日期段),同事件重放幂等。"""
    fp = {"kind": kind, "ref": ref, "payload": payload}
    return f"{TRIGGER_ID_PREFIX}{drr._ymd_of(created_at)}-{drr._hash8(fp)}"


def make_conclusion_id(task_id, hypothesis_id, status, evaluations, created_at):
    """CON-{YYYYMMDD}-{sha256[:8]}: 指纹={task_id,hypothesis_id,status,evaluations
    (condition_id+outcome+evidence 键)};同评估重放→同 id→append-only 拒收。"""
    ev = [{"condition_id": e["condition_id"], "outcome": e["outcome"],
           "evidence": e.get("evidence")} for e in evaluations]
    fp = {"task_id": task_id, "hypothesis_id": hypothesis_id,
          "status": status, "evaluations": ev}
    return f"{CONCLUSION_ID_PREFIX}{drr._ymd_of(created_at)}-{drr._hash8(fp)}"


def make_disposal_id(task_id, hypothesis_id, paths, created_at):
    """DSP-{YYYYMMDD}-{sha256[:8]}: 指纹={task_id,hypothesis_id,paths}(三路径
    结果件);同处置重放→同 id→append-only 拒收。"""
    fp = {"task_id": task_id, "hypothesis_id": hypothesis_id, "paths": paths}
    return f"{DISPOSAL_ID_PREFIX}{drr._ymd_of(created_at)}-{drr._hash8(fp)}"


# ══ S-3 触发监听(P-C-03/P-C-04/P-C-05;要点①) ═════════════════════════


def validate_trigger_payload(kind, payload):
    """触发 payload 按子类 schema 校验(issues 列表风格,空=合法;P-C-04)。"""
    issues = []
    if kind not in TRIGGER_KINDS:
        return [f"kind须为{'|'.join(TRIGGER_KINDS)}(S-3 入口子类恰 3 个,"
                f"DESIGN §2.1 L41): {kind!r}"]
    if not isinstance(payload, dict):
        return [f"payload须为dict: {type(payload).__name__}"]
    if kind == "thesis_invalidation":                     # S-3① 论点触发器
        extra = set(payload) - {"target", "trigger_id", "engine_status", "verified_by"}
        if extra:
            issues.append(f"payload含未登记键(thesis_invalidation): {sorted(extra)}")
        for k in ("target", "trigger_id", "verified_by"):
            if not isinstance(payload.get(k), str) or not payload.get(k):
                issues.append(f"payload.{k}须为非空string: {payload.get(k)!r}")
        if payload.get("engine_status") != THESIS_ENGINE_STATUS_REQUIRED:
            issues.append(f"engine_status恒须{THESIS_ENGINE_STATUS_REQUIRED!r}"
                          f"(终态门禁: 失效/升级触发器须被引擎核验为已触发方可入口,"
                          f"report_generator.py L503;not_triggered/sustaining/"
                          f"unverifiable 一律拒收): {payload.get('engine_status')!r}")
    elif kind == "prediction_adjudication":               # S-3② 预测裁决
        extra = set(payload) - {"pred_ref", "event", "verdict", "adjudicated_by"}
        if extra:
            issues.append(f"payload含未登记键(prediction_adjudication): {sorted(extra)}")
        if not isinstance(payload.get("pred_ref"), str) or not payload.get("pred_ref"):
            issues.append(f"pred_ref须为非空string: {payload.get('pred_ref')!r}")
        if not isinstance(payload.get("adjudicated_by"), str) or not payload.get("adjudicated_by"):
            issues.append(f"adjudicated_by须为非空string: {payload.get('adjudicated_by')!r}")
        ev = payload.get("event")
        if ev not in PREDICTION_EVENTS:
            issues.append(f"event须为{'|'.join(PREDICTION_EVENTS)}(到期裁决/前提兑现"
                          f"转观察中,DESIGN L41②): {ev!r}")
        verdict = payload.get("verdict")
        if ev == "adjudicated":
            if verdict not in PREDICTION_VERDICTS:
                issues.append(f"event=adjudicated 时 verdict须为"
                              f"{'|'.join(PREDICTION_VERDICTS)}(裁决四态,"
                              f"report_generator.py L534): {verdict!r}")
        elif verdict is not None:
            issues.append(f"event=premise_fulfilled 时 verdict恒须null(前提兑现非裁决,"
                          f"仅转观察中): {verdict!r}")
    else:                                                 # S-3③ 拒写提案
        extra = set(payload) - {"view_ref", "proposed_rating", "gate_status", "reason"}
        if extra:
            issues.append(f"payload含未登记键(rejected_rating_proposal): {sorted(extra)}")
        for k in ("view_ref", "reason"):
            if not isinstance(payload.get(k), str) or not payload.get(k):
                issues.append(f"payload.{k}须为非空string: {payload.get(k)!r}")
        if payload.get("proposed_rating") not in RATING_VOCABULARY:
            issues.append(f"proposed_rating须为评级4档之一{list(RATING_VOCABULARY)}"
                          f"(allocation_engine.py L63): {payload.get('proposed_rating')!r}")
        if payload.get("gate_status") != PROPOSAL_GATE_STATUS_REQUIRED:
            issues.append(f"gate_status恒须{PROPOSAL_GATE_STATUS_REQUIRED!r}"
                          f"(评级变更门禁被拒提案留档,report_generator.py L522): "
                          f"{payload.get('gate_status')!r}")
    return issues


def validate_trigger_record(record):
    issues = []
    if not isinstance(record, dict):
        return [f"记录须为dict: {type(record).__name__}"]
    keys = ("record_type", "trigger_id", "kind", "ref", "payload",
            "created_at", "note", "history")
    for k in keys:
        if k not in record:
            issues.append(f"记录缺字段{k}(P-C-04)")
    if issues:
        return issues
    if record.get("record_type") != TRIGGER_RECORD_TYPE:
        issues.append(f"record_type恒须字面量{TRIGGER_RECORD_TYPE!r}")
    if not str(record.get("trigger_id", "")).startswith(TRIGGER_ID_PREFIX):
        issues.append(f"trigger_id须为{TRIGGER_ID_PREFIX}*族: {record.get('trigger_id')!r}")
    issues.extend(validate_trigger_payload(record.get("kind"), record.get("payload") or {}))
    if not isinstance(record.get("ref"), str) or not record.get("ref"):
        issues.append(f"ref须为非空string(触发器/裁决/提案引用,DESIGN L41): {record.get('ref')!r}")
    ca = record.get("created_at")
    if not isinstance(ca, str) or not drr._iso_date_str_ok(ca):
        issues.append(f"created_at须为ISO8601字符串: {ca!r}")
    if not isinstance(record.get("note"), str) or not record.get("note"):
        issues.append("note须为非空string")
    if not isinstance(record.get("history"), list) or not record.get("history"):
        issues.append("history须为非空list(初始登记条目在场)")
    return issues


def register_tracking_trigger(kind, ref, payload, *, archive_dir=None,
                              created_at=None, note=None):
    """S-3 触发事件 intake(append-only 落档;schema 违规 fail-loud 零写入)。

    kind ∈ TRIGGER_KINDS(3 子类);ref=触发器/裁决/提案引用;payload 按子类
    schema(P-C-04)。返回 {status, trigger_id, trigger_path}。
    """
    if not isinstance(ref, str) or not ref:
        raise ValueError(f"ref须为非空string: {ref!r}")
    issues = validate_trigger_payload(kind, payload)
    if issues:
        raise ValueError("触发事件未过schema校验(fail-loud): " + ";".join(issues))
    ca = created_at or _now_iso()
    trigger_id = make_trigger_id(kind, ref, payload, ca)
    record = {"record_type": TRIGGER_RECORD_TYPE, "trigger_id": trigger_id,
              "kind": kind, "ref": ref, "payload": payload, "created_at": ca,
              "note": note or f"S-3 触发登记: {kind}(append-only,事件引用={ref})",
              "history": [{"ts": ca, "note": f"S-3 触发监听 intake: kind={kind}"}]}
    v = validate_trigger_record(record)
    if v:
        raise ValueError("触发记录未过schema校验(fail-loud): " + ";".join(v))
    ad = archive_dir or DEFAULT_ARCHIVE_DIR
    status, last_path = drr._write_records(
        [(record, drr._record_path(ad, COLLECTION_TRIGGERS, trigger_id))], ad)
    return {"status": status, "trigger_id": trigger_id,
            "trigger_path": drr._record_path(ad, COLLECTION_TRIGGERS, trigger_id),
            "kind": kind, "ref": ref, "last_path": last_path}


def load_trigger(trigger_id, archive_dir=None):
    return _load_scoped_record(trigger_id, COLLECTION_TRIGGERS, archive_dir,
                               "触发", validate_trigger_record, None)


def list_triggers(archive_dir=None):
    """全部触发记录(按 trigger_id 升序;确定性序)。"""
    return _list_collection(COLLECTION_TRIGGERS, validate_trigger_record,
                            archive_dir, None)


def spawn_research_from_trigger(trigger_id, question, hypotheses,
                                discriminating_criteria, snapshot, *,
                                archive_dir=None, created_at=None):
    """触发后再研究(P-C-05): 经触发档 origin_trigger 登记新深研任务。

    origin 恰一 origin_trigger{kind,ref} 取自触发档(任务档携 origin_trigger,
    DESIGN §2.1 L41 记录衔接列);DRAFT 五要件校验经 drr 兜底复用。
    """
    trig = load_trigger(trigger_id, archive_dir)
    origin = {"origin_trigger": {"kind": trig["kind"], "ref": trig["ref"]}}
    res = drr.register_deep_research_task(
        question, origin, hypotheses, discriminating_criteria, snapshot,
        archive_dir=archive_dir, created_at=created_at)
    res["trigger_id"] = trigger_id
    return res


# ══ 条件程序评估(P-C-06..P-C-09/P-C-12;要点②,§6.2 程序判定) ══════════


def _observations_from_snapshot(snap):
    """快照事实→{metric_id: [(obs_date, value)] 升序}(P-C-12;质量≠FAIL 且
    value 为 number,fact_engine 口径数据不足不填 0: 缺值不造数)。"""
    facts = (snap or {}).get("facts")
    if not isinstance(facts, list):
        return None
    out = {}
    for f in facts:
        if not isinstance(f, dict):
            continue
        if f.get("quality_status") in dm.FACT_QUALITY_REJECTED:
            continue
        v = f.get("value")
        if not isinstance(v, (int, float)) or isinstance(v, bool):
            continue
        mid = f.get("metric_id")
        od = str(f.get("observation_date") or "")[:10]
        if not isinstance(mid, str) or not mid or not od:
            continue
        out.setdefault(mid, []).append((od, float(v)))
    for mid in out:
        out[mid].sort()
    return out


def _condition_window(cond, premise_fulfilled_on):
    """→ (window_start|None, deadline, problem|None)(P-C-06/P-C-08)。

    window_start=premise 兑现日(带前提且已兑现)否则条件档 created_at 日期段;
    deadline=window.deadline 或 created_at+weeks×7;前提未兑现→NOT_YET_IN_WINDOW;
    兑现日晚于 deadline→NOT_ACTIVATED(不激活,截止日不顺延)。
    """
    w = cond.get("window") or {}
    ca_date = str(cond.get("created_at") or "")[:10]
    if "deadline" in w:
        deadline = str(w["deadline"])[:10]
    else:
        try:
            deadline = (date.fromisoformat(ca_date)
                        + timedelta(weeks=int(w.get("weeks", 0)))).isoformat()
        except ValueError:
            deadline = ca_date
    if cond.get("premise") is not None:
        pf = premise_fulfilled_on
        if pf is None:
            return None, deadline, COND_NOT_YET_IN_WINDOW
        pf = str(pf)[:10]
        if pf > deadline:
            return None, deadline, COND_NOT_ACTIVATED
        return pf, deadline, None
    return ca_date, deadline, None


def _evaluate_condition(cond, obs_by_metric, as_of, premise_fulfilled_on):
    """单条件程序评估(P-C-07/P-C-08): 观察窗内观测才参与裁决(每日观察先例
    口径);touch 触及可提前/expiry 不得提前裁决/窗内零观测=数据不足不硬判。"""
    start, deadline, problem = _condition_window(cond, premise_fulfilled_on)
    result = {"condition_id": cond.get("condition_id"),
              "metric_id": cond.get("metric_id"),
              "direction": cond.get("direction"),
              "mode": (cond.get("window") or {}).get("mode"),
              "window_start": start, "deadline": deadline,
              "outcome": None, "evidence": None, "adverse_obs": None}
    if problem is not None:
        result["outcome"] = problem
        return result
    op = ae.COMPARATORS[cond["operator"]]
    threshold = cond["threshold"]
    all_obs = obs_by_metric.get(cond["metric_id"]) or []
    in_window = [(od, v) for od, v in all_obs if start <= od <= deadline]
    hits = [(od, v) for od, v in in_window if op(v, threshold)]
    if result["mode"] == "touch":
        if hits:                                           # 触及即可提前(单调事件)
            result["outcome"] = COND_TRIGGERED
            result["evidence"] = {"obs_date": hits[0][0], "value": hits[0][1]}
        elif as_of > deadline:                             # 窗口闭合
            if in_window:
                result["outcome"] = COND_NOT_TRIGGERED
                result["evidence"] = {"obs_date": in_window[-1][0],
                                      "value": in_window[-1][1]}
            else:
                result["outcome"] = COND_DATA_INSUFFICIENT
        else:
            result["outcome"] = COND_PENDING
    else:                                                  # expiry: 截止日达到
        if as_of < deadline:                               # 不得提前裁决
            result["outcome"] = COND_PENDING
            if hits:                                       # 部分证伪信号(待期终)
                result["adverse_obs"] = {"obs_date": hits[0][0], "value": hits[0][1]}
        else:
            if in_window:                                  # 窗内≤deadline 最新观测
                od, v = in_window[-1]
                result["outcome"] = COND_TRIGGERED if op(v, threshold) else COND_NOT_TRIGGERED
                result["evidence"] = {"obs_date": od, "value": v}
            else:
                result["outcome"] = COND_DATA_INSUFFICIENT
    return result


def evaluate_hypothesis_conditions(task_id, hypothesis_id, snapshot_id,
                                   snapshot_dir, *, as_of,
                                   premise_fulfilled=None, archive_dir=None):
    """假设条件集程序评估(§6.2 L168 程序判定,观察记录驱动)。

    快照纪律三重(P-C-12): drr._load_snapshot_for_verify 可载+rp.digest_snapshot
    重算+rp.gate_allows_formal_research 放行;任一不过→blocked 如实返回(零写入,
    不编造观测)。as_of=评估日(显式必填,禁墙钟);premise_fulfilled=
    {condition_id: 兑现日}(引擎核验产物,P-C-08)。
    返回 {blocked, blocking, snapshot_id, digest_snapshot, as_of, evaluations}。
    """
    if not isinstance(as_of, str) or not drr._iso_date_str_ok(as_of):
        raise ValueError(f"as_of须为ISO日期字符串(评估日,显式必填禁墙钟): {as_of!r}")
    ad = archive_dir or DEFAULT_ARCHIVE_DIR
    task = drr.load_task(task_id, ad)
    if hypothesis_id not in task["hypothesis_ids"]:
        raise ValueError(f"hypothesis_id={hypothesis_id!r}不在任务假设集"
                         f"{task['hypothesis_ids']}")
    snap, load_err = drr._load_snapshot_for_verify(snapshot_id, snapshot_dir)
    if snap is None:
        return {"blocked": True,
                "blocking": {"stage": "snapshot_load", "detail": load_err},
                "snapshot_id": snapshot_id, "digest_snapshot": None,
                "as_of": as_of, "evaluations": []}
    digest = rp.digest_snapshot(snap)                      # R5 重算(禁采声明值)
    gate_status = (snap.get("gate_a") or {}).get("status")
    if not rp.gate_allows_formal_research(gate_status):    # Gate A FAIL→阻断如实
        return {"blocked": True,
                "blocking": {"stage": "gate_a", "gate_a_status": gate_status,
                             "detail": f"Gate A={gate_status!r} 不放行正式研究,"
                                       f"该快照不得作为深研正式评估源(DESIGN §3.1)"},
                "snapshot_id": snapshot_id, "digest_snapshot": digest,
                "as_of": as_of, "evaluations": []}
    obs_by_metric = _observations_from_snapshot(snap)
    if obs_by_metric is None:
        return {"blocked": True,
                "blocking": {"stage": "facts_structure",
                             "detail": "快照缺facts事实列表(非规范研究快照结构)"},
                "snapshot_id": snapshot_id, "digest_snapshot": digest,
                "as_of": as_of, "evaluations": []}
    premise_fulfilled = premise_fulfilled or {}
    evaluations = []
    for fc_id in task["condition_ids"]:
        fc = drr._load_record(fc_id, drr.COLLECTION_CONDITIONS, ad, "条件",
                              drr.validate_condition_record)
        if fc["hypothesis_id"] != hypothesis_id:
            continue
        evaluations.append(_evaluate_condition(
            fc, obs_by_metric, str(as_of)[:10], premise_fulfilled.get(fc_id)))
    return {"blocked": False, "blocking": None, "snapshot_id": snapshot_id,
            "digest_snapshot": digest, "as_of": str(as_of)[:10],
            "gate_a_status": gate_status, "evaluations": evaluations}


# ══ 结论状态机(P-C-10/P-C-11;§6.3 append-only 结论档) ═════════════════

CONCLUSION_KEYS = ("record_type", "conclusion_id", "task_id", "hypothesis_id",
                   "created_at", "status", "prior_status", "snapshot_id",
                   "digest_snapshot", "as_of", "evaluations",
                   "unexplained_major_counter", "decision_rule", "reasons",
                   "history")


def validate_conclusion_record(record):
    issues = []
    if not isinstance(record, dict):
        return [f"记录须为dict: {type(record).__name__}"]
    for k in CONCLUSION_KEYS:
        if k not in record:
            issues.append(f"记录缺字段{k}(P-C-10)")
    if issues:
        return issues
    if record.get("record_type") != CONCLUSION_RECORD_TYPE:
        issues.append(f"record_type恒须字面量{CONCLUSION_RECORD_TYPE!r}")
    if not str(record.get("conclusion_id", "")).startswith(CONCLUSION_ID_PREFIX):
        issues.append(f"conclusion_id须为{CONCLUSION_ID_PREFIX}*族: "
                      f"{record.get('conclusion_id')!r}")
    issues.extend(ra.validate_id_conventions(task_id=record.get("task_id")))
    if not str(record.get("hypothesis_id", "")).startswith(drr.HYPOTHESIS_ID_PREFIX):
        issues.append(f"hypothesis_id须为{drr.HYPOTHESIS_ID_PREFIX}*族: "
                      f"{record.get('hypothesis_id')!r}")
    if record.get("status") not in CONCLUSION_INTERMEDIATE + CONCLUSION_TERMINAL:
        issues.append(f"status须为{'|'.join(CONCLUSION_INTERMEDIATE + CONCLUSION_TERMINAL)}"
                      f"(§6.3 L175-L180;未裁决=无记录默认): {record.get('status')!r}")
    prior = record.get("prior_status")
    if prior not in (CONCLUSION_STATUS_UNADJUDICATED,) + CONCLUSION_INTERMEDIATE:
        issues.append(f"prior_status须为未裁决或轮次中态(终态不可为前态,"
                      f"终态后再评一律拒收): {prior!r}")
    if not isinstance(record.get("as_of"), str) or not drr._iso_date_str_ok(record.get("as_of") or ""):
        issues.append(f"as_of须为ISO日期字符串: {record.get('as_of')!r}")
    sid = record.get("snapshot_id")
    if not isinstance(sid, str) or ra.parse_snapshot_id(sid) is None:
        issues.append(f"snapshot_id非规范(research_snapshot_YYYYMMDD[_vN]): {sid!r}")
    dg = record.get("digest_snapshot")
    if not isinstance(dg, str) or not ra.DIGEST_RE.match(dg or ""):
        issues.append(f"digest_snapshot格式非法(须R5十六位小写指纹): {dg!r}")
    evs = record.get("evaluations")
    if not isinstance(evs, list) or not evs:
        issues.append("evaluations须为非空list(每假设 ≥1 条件,WP-A DRAFT 校验)")
    else:
        for i, e in enumerate(evs):
            if not isinstance(e, dict):
                issues.append(f"evaluations[{i}]须为dict")
                continue
            if not str(e.get("condition_id", "")).startswith(drr.CONDITION_ID_PREFIX):
                issues.append(f"evaluations[{i}].condition_id须为"
                              f"{drr.CONDITION_ID_PREFIX}*族: {e.get('condition_id')!r}")
            if e.get("direction") not in drr.CONDITION_DIRECTIONS:
                issues.append(f"evaluations[{i}].direction须为"
                              f"{'|'.join(drr.CONDITION_DIRECTIONS)}: {e.get('direction')!r}")
            if e.get("outcome") not in COND_OUTCOMES:
                issues.append(f"evaluations[{i}].outcome须为{'|'.join(COND_OUTCOMES)}: "
                              f"{e.get('outcome')!r}")
    if not isinstance(record.get("unexplained_major_counter"), bool):
        issues.append("unexplained_major_counter须为bool(矩阵反证旗,经 dm 复用汇编)")
    if not isinstance(record.get("decision_rule"), str) or not record.get("decision_rule"):
        issues.append("decision_rule须为非空string(确定性判定规则登记)")
    if not isinstance(record.get("reasons"), list) or not record.get("reasons"):
        issues.append("reasons须为非空list(判定依据登记)")
    ca = record.get("created_at")
    if not isinstance(ca, str) or not drr._iso_date_str_ok(ca):
        issues.append(f"created_at须为ISO8601字符串: {ca!r}")
    if not isinstance(record.get("history"), list) or not record.get("history"):
        issues.append("history须为非空list(初始登记条目在场)")
    return issues


def _decide_status(evaluations, unexplained_major_counter):
    """§6.3 终态/轮次中确定性判定(P-C-11;优先序 FALSIFIED>CONFIRMED>
    EXPIRED_UNRESOLVED>INCONCLUSIVE;返回 (status|None, rule, reasons))。"""
    falsifying = [e for e in evaluations if e["direction"] == "falsifying"]
    supporting = [e for e in evaluations if e["direction"] == "supporting"]
    f_trig = [e for e in falsifying if e["outcome"] == COND_TRIGGERED]
    s_trig = [e for e in supporting if e["outcome"] == COND_TRIGGERED]
    if f_trig:                                             # ①证伪向条件触发
        return ("FALSIFIED", "§6.3 FALSIFIED: 证伪向条件触发",
                [f"证伪向条件成立: {e['condition_id']}({e['metric_id']} "
                 f"{e.get('evidence')})" for e in f_trig])
    if s_trig and not unexplained_major_counter:           # ②支持向成立且无未解释重大反证
        return ("CONFIRMED", "§6.3 CONFIRMED: 窗口内支持向条件成立且无未解释重大反证",
                [f"支持向条件成立: {e['condition_id']}({e['metric_id']} "
                 f"{e.get('evidence')})" for e in s_trig]
                + ["矩阵未解释重大反证=False(经 dm.assemble_matrix 复用汇编)"])
    windows_closed = all(e["outcome"] in _COND_DECIDED for e in evaluations)
    if windows_closed:
        if any(e["outcome"] == COND_DATA_INSUFFICIENT for e in evaluations):
            return ("INCONCLUSIVE", "§6.3 INCONCLUSIVE: 数据阻断(窗内零可用观测,"
                    "数据不足不硬判)",
                    [f"窗口闭合且数据不足: {e['condition_id']}({e['metric_id']})"
                     for e in evaluations if e["outcome"] == COND_DATA_INSUFFICIENT])
        if s_trig:                                         # ③支持向已成立但反证未解释
            return ("PARTIAL_SUPPORT", "§6.3 部分支持(轮次中): 支持向条件成立但存在"
                    "未解释重大反证,终态判据被阻断(反证义务未闭合,§4.3)",
                    [f"支持向条件成立: {e['condition_id']}" for e in s_trig]
                    + ["未解释重大反证=True(经 dm.assemble_matrix 复用汇编)"])
        return ("EXPIRED_UNRESOLVED", "§6.3 EXPIRED_UNRESOLVED: 窗口结束未触发",
                [f"窗口闭合且未触发: {e['condition_id']}({e['metric_id']} "
                 f"outcome={e['outcome']})" for e in evaluations])
    adverse = [e for e in falsifying
               if e["outcome"] == COND_PENDING and e.get("adverse_obs")]
    if adverse:                                            # ④部分证伪(expiry 待期终)
        return ("PARTIAL_FALSIFIED", "§6.3 部分证伪(轮次中): 证伪向条件窗内已现不利"
                "观测,expiry 待期终裁决",
                [f"不利观测: {e['condition_id']}({e['metric_id']} {e['adverse_obs']})"
                 for e in adverse])
    if s_trig:                                             # ⑤部分支持(窗口未闭合)
        return ("PARTIAL_SUPPORT", "§6.3 部分支持(轮次中): 支持向条件成立但存在"
                "未解释重大反证(窗口未闭合)",
                [f"支持向条件成立: {e['condition_id']}" for e in s_trig]
                + ["未解释重大反证=True(经 dm.assemble_matrix 复用汇编)"])
    return (None, "§6.3 未裁决维持(无部分信号无终态命中,零追加记录)", [])


def adjudicate_conclusion(task_id, hypothesis_id, evaluation, *,
                          archive_dir=None, created_at=None):
    """结论裁决 append-only 落档(§6.3;终态后再评一律拒收)。

    evaluation=evaluate_hypothesis_conditions 返回件(blocked 评估拒收);
    未解释重大反证旗经 dm.assemble_matrix 复用汇编取
    summary[hypothesis_id]["未解释重大反证"]。返回 {status, conclusion_id,
    new_status, prior_status, decision_rule}。
    """
    ad = archive_dir or DEFAULT_ARCHIVE_DIR
    task = drr.load_task(task_id, ad)
    if hypothesis_id not in task["hypothesis_ids"]:
        raise ValueError(f"hypothesis_id={hypothesis_id!r}不在任务假设集")
    if not isinstance(evaluation, dict) or evaluation.get("blocked"):
        raise ValueError("评估件不可用或为阻断态(blocked 评估不得入结论裁决,"
                         "数据阻断如实登记不编造: " + str((evaluation or {}).get("blocking")))
    evs = evaluation.get("evaluations")
    if not isinstance(evs, list) or not evs:
        raise ValueError("评估件缺 evaluations(每假设 ≥1 条件)")
    prior = current_conclusion_status(task_id, hypothesis_id, ad)
    if prior in CONCLUSION_TERMINAL:
        raise ValueError(f"假设{hypothesis_id}结论已处终态{prior!r}——终态后再评一律"
                         f"拒收(FALSIFIED 不可改写/终态不可重开,DESIGN §6.3 L183"
                         f"+_is_final_prediction 终态纪律先例)")
    matrix = dm.assemble_matrix(task_id, archive_dir=ad)  # 复用上游汇编(禁复制分叉)
    unexplained = bool(matrix["summary"].get(hypothesis_id, {})
                       .get("未解释重大反证", False))
    new_status, rule, reasons = _decide_status(evs, unexplained)
    if new_status is None:                                # 未裁决维持: 零追加记录
        return {"status": "unchanged", "conclusion_id": None,
                "new_status": CONCLUSION_STATUS_UNADJUDICATED,
                "prior_status": prior, "decision_rule": rule, "reasons": reasons}
    ca = created_at or _now_iso()
    conclusion_id = make_conclusion_id(task_id, hypothesis_id, new_status, evs, ca)
    record = {"record_type": CONCLUSION_RECORD_TYPE,
              "conclusion_id": conclusion_id, "task_id": task_id,
              "hypothesis_id": hypothesis_id, "created_at": ca,
              "status": new_status, "prior_status": prior,
              "snapshot_id": evaluation["snapshot_id"],
              "digest_snapshot": evaluation["digest_snapshot"],
              "as_of": evaluation["as_of"], "evaluations": evs,
              "unexplained_major_counter": unexplained,
              "decision_rule": rule, "reasons": reasons,
              "history": [{"ts": ca, "note": f"结论裁决入档(append-only): "
                           f"{prior}→{new_status}(程序判定,观察记录驱动)"}]}
    v = validate_conclusion_record(record)
    if v:
        raise ValueError("结论记录未过schema校验(fail-loud): " + ";".join(v))
    w_status, _ = drr._write_records(
        [(record, drr._record_path(ad, COLLECTION_CONCLUSIONS, conclusion_id))], ad)
    return {"status": w_status, "conclusion_id": conclusion_id,
            "new_status": new_status, "prior_status": prior,
            "decision_rule": rule, "reasons": reasons}


def current_conclusion_status(task_id, hypothesis_id, archive_dir=None):
    """假设当前结论态=结论记录流确定性折叠(按 created_at+conclusion_id 排序;
    无记录默认 UNADJUDICATED;append-only 推导不改档,drr.current_status 同款范式)。"""
    records = [r for r in list_conclusions(task_id, archive_dir)
               if r["hypothesis_id"] == hypothesis_id]
    return records[-1]["status"] if records else CONCLUSION_STATUS_UNADJUDICATED


# ══ 证伪后处置(P-C-13;§6.3 L182-L185 路径 3 条,要点③) ════════════════

DISPOSAL_KEYS = ("record_type", "disposal_id", "task_id", "hypothesis_id",
                 "created_at", "conclusion_id", "paths", "note", "history")
REVIEW_REQUEST_REQUIRES = ("engine_verified_trigger", "gte2_new_independent_evidence")


def validate_disposal_record(record):
    issues = []
    if not isinstance(record, dict):
        return [f"记录须为dict: {type(record).__name__}"]
    for k in DISPOSAL_KEYS:
        if k not in record:
            issues.append(f"记录缺字段{k}(P-C-13)")
    if issues:
        return issues
    if record.get("record_type") != DISPOSAL_RECORD_TYPE:
        issues.append(f"record_type恒须字面量{DISPOSAL_RECORD_TYPE!r}")
    if not str(record.get("disposal_id", "")).startswith(DISPOSAL_ID_PREFIX):
        issues.append(f"disposal_id须为{DISPOSAL_ID_PREFIX}*族: {record.get('disposal_id')!r}")
    issues.extend(ra.validate_id_conventions(task_id=record.get("task_id")))
    if not str(record.get("hypothesis_id", "")).startswith(drr.HYPOTHESIS_ID_PREFIX):
        issues.append(f"hypothesis_id须为{drr.HYPOTHESIS_ID_PREFIX}*族: "
                      f"{record.get('hypothesis_id')!r}")
    if not str(record.get("conclusion_id", "")).startswith(CONCLUSION_ID_PREFIX):
        issues.append(f"conclusion_id须为{CONCLUSION_ID_PREFIX}*族(FALSIFIED 结论档): "
                      f"{record.get('conclusion_id')!r}")
    paths = record.get("paths")
    if not isinstance(paths, dict):
        issues.append("paths须为dict(三路径一次成套)")
    else:
        mark = paths.get("mark") or {}
        if not isinstance(mark, dict) or not str(mark.get("conclusion_id", "")) \
                .startswith(CONCLUSION_ID_PREFIX) or mark.get("immutable") is not True:
            issues.append("paths.mark须为{conclusion_id: CON-*, immutable: True}"
                          "(路径①: 标记=FALSIFIED 结论档本身,不可改写)")
        revision = paths.get("revision")
        if revision is not None and (
                not isinstance(revision, dict)
                or not str(revision.get("new_hypothesis_id", "")).startswith(drr.HYPOTHESIS_ID_PREFIX)
                or not str(revision.get("revision_of", "")).startswith(drr.HYPOTHESIS_ID_PREFIX)):
            issues.append("paths.revision须为null或{new_hypothesis_id, revision_of}"
                          "(路径①: 实质新假设=新记录+新ID 关联引用原假设)")
        review = paths.get("review_request") or {}
        if not isinstance(review, dict) \
                or not isinstance(review.get("target"), str) or not review.get("target") \
                or list(review.get("requires") or ()) != list(REVIEW_REQUEST_REQUIRES) \
                or review.get("decided_by") != "gate" \
                or review.get("deep_research_layer_writes_state") is not False:
            issues.append("paths.review_request须为{target, requires=[engine_verified"
                          "_trigger, gte2_new_independent_evidence], decided_by='gate',"
                          " deep_research_layer_writes_state: False}(路径②: 走终态门禁"
                          "正向流程,由门禁裁决,深研层不直接改写状态)")
        tracking = paths.get("tracking") or {}
        if not isinstance(tracking, dict) or not isinstance(tracking.get("archived"), bool):
            issues.append("paths.tracking须为{archived: bool, ...}(路径③: 原 TRACKING "
                          "终止;非 TRACKING 态如实登记不适用)")
        followup = paths.get("followup")
        if followup is not None and (
                not isinstance(followup, dict)
                or not str(followup.get("followup_task_id", "")).startswith(drr.TASK_ID_PREFIX)):
            issues.append("paths.followup须为null或{followup_task_id: RT-DR-*}"
                          "(路径③: 经 S-3 跟踪触发发起新深研任务,闭环)")
    if not isinstance(record.get("note"), str) or not record.get("note"):
        issues.append("note须为非空string")
    ca = record.get("created_at")
    if not isinstance(ca, str) or not drr._iso_date_str_ok(ca):
        issues.append(f"created_at须为ISO8601字符串: {ca!r}")
    if not isinstance(record.get("history"), list) or not record.get("history"):
        issues.append("history须为非空list(初始登记条目在场)")
    return issues


def apply_falsification_disposal(task_id, hypothesis_id, *, review_target,
                                 review_evidence, archive_tracking=True,
                                 revision=None, followup=None,
                                 archive_dir=None, snapshot_dir=None,
                                 created_at=None):
    """证伪后处置(§6.3 L182-L185,三路径一次成套 append-only 落档)。

    前置: 该假设当前结论恒为 FALSIFIED(未证伪/未终态→拒收)。
    路径①: mark=FALSIFIED 结论档引用(字节不可改写);revision={statement,
    mechanism_story, reason, snapshot}→经 drr.revise_hypothesis 新记录+新ID;
    路径②: review_request 留档(正向流程要求=触发器被引擎核验或≥2 项新增独立
    证据,L503 同款;深研层不直接改写状态——本模块零研究状态档写路径);
    路径③: archive_tracking 且任务当前态 TRACKING→经 drr.append_lifecycle_event
    迁移 ARCHIVED(既有迁移表);followup={trigger_id, question, hypotheses,
    criteria}→经 spawn_research_from_trigger 发起新任务(origin_trigger 闭环;
    快照取任务档绑定快照经 snapshot_dir 加载)。
    """
    ad = archive_dir or DEFAULT_ARCHIVE_DIR
    task = drr.load_task(task_id, ad)
    if hypothesis_id not in task["hypothesis_ids"]:
        raise ValueError(f"hypothesis_id={hypothesis_id!r}不在任务假设集")
    current = current_conclusion_status(task_id, hypothesis_id, ad)
    if current != "FALSIFIED":
        raise ValueError(f"证伪后处置前置失败: 假设当前结论={current!r}(恒须 FALSIFIED,"
                         f"DESIGN §6.3 L177/L182)")
    if not isinstance(review_target, str) or not review_target:
        raise ValueError(f"review_target须为非空string(关联论点/观点标识): {review_target!r}")
    if not isinstance(review_evidence, list) or not review_evidence \
            or not all(isinstance(r, str) and r for r in review_evidence):
        raise ValueError("review_evidence须为非空 string list(复核证据引用;"
                         "门禁裁决[触发器引擎核验或≥2 项新增独立证据]由门禁自裁)")
    falsified = [r for r in list_conclusions(task_id, ad)
                 if r["hypothesis_id"] == hypothesis_id and r["status"] == "FALSIFIED"][-1]
    ca = created_at or _now_iso()
    # 路径①: 标记=FALSIFIED 结论档本身(不可改写);可选实质新假设(新记录+新ID)
    mark = {"conclusion_id": falsified["conclusion_id"], "immutable": True,
            "marked_by": "falsified_conclusion_record"}
    revision_out = None
    if revision is not None:
        if not isinstance(revision, dict):
            raise ValueError("revision须为dict{statement, mechanism_story, reason, snapshot}")
        res = drr.revise_hypothesis(task_id, hypothesis_id,
                                    revision["statement"],
                                    revision["mechanism_story"],
                                    revision["reason"], revision["snapshot"],
                                    archive_dir=ad, created_at=ca)
        revision_out = {"new_hypothesis_id": res["hypothesis_id"],
                        "revision_of": hypothesis_id}
    # 路径②: 关联论点/观点触发复核(走终态门禁正向流程,由门禁裁决)
    review_request = {"target": review_target,
                      "path": "terminal_gate_forward_flow",
                      "requires": list(REVIEW_REQUEST_REQUIRES),
                      "evidence_refs": list(review_evidence),
                      "decided_by": "gate",
                      "deep_research_layer_writes_state": False}
    # 路径③: 跟踪处置(TRACKING→ARCHIVED 经既有迁移表)+可选闭环后续任务
    tracking = {"archived": False, "task_status_at_disposal": None,
                "archive_event_id": None}
    cur_task_status = drr.current_status(task_id, ad)
    tracking["task_status_at_disposal"] = cur_task_status
    if archive_tracking and cur_task_status == drr.STATUS_TRACKING:
        ev = drr.append_lifecycle_event(
            task_id, drr.STATUS_TRACKING, drr.STATUS_ARCHIVED,
            "证伪后处置: 原 TRACKING 终止(§6.3 L185 路径③)",
            trigger_ref=falsified["conclusion_id"], archive_dir=ad, created_at=ca)
        tracking["archived"] = True
        tracking["archive_event_id"] = ev["event_id"]
    elif archive_tracking:
        tracking["not_applicable_reason"] = (f"任务当前态={cur_task_status!r} 非 TRACKING,"
                                             f"路径③归档不适用,如实登记")
    followup_out = None
    if followup is not None:
        if not isinstance(followup, dict):
            raise ValueError("followup须为dict{trigger_id, question, hypotheses, criteria}")
        snap, load_err = drr._load_snapshot_for_verify(
            task["snapshot_id"], snapshot_dir)
        if snap is None:
            raise ValueError(f"闭环后续任务快照不可载(任务档绑定快照): {load_err}")
        spawn = spawn_research_from_trigger(
            followup["trigger_id"], followup["question"], followup["hypotheses"],
            followup["criteria"], snap, archive_dir=ad, created_at=ca)
        followup_out = {"followup_task_id": spawn["task_id"],
                        "followup_trigger_id": followup["trigger_id"]}
    paths = {"mark": mark, "revision": revision_out,
             "review_request": review_request, "tracking": tracking,
             "followup": followup_out}
    disposal_id = make_disposal_id(task_id, hypothesis_id, paths, ca)
    record = {"record_type": DISPOSAL_RECORD_TYPE, "disposal_id": disposal_id,
              "task_id": task_id, "hypothesis_id": hypothesis_id,
              "created_at": ca, "conclusion_id": falsified["conclusion_id"],
              "paths": paths,
              "note": "证伪后处置三路径一次成套(§6.3 L182-L185): "
                      "①标记=FALSIFIED 结论档(不可改写)"
                      +("+实质新假设新ID" if revision_out else "")
                      +"②关联论点/观点复核提案(走门禁,深研层不改写状态)"
                      +"③跟踪处置(TRACKING 终止"
                      +("+闭环新任务" if followup_out else "")+")",
              "history": [{"ts": ca, "note": "证伪后处置登记入档(append-only)"}]}
    v = validate_disposal_record(record)
    if v:
        raise ValueError("处置记录未过schema校验(fail-loud): " + ";".join(v))
    w_status, _ = drr._write_records(
        [(record, drr._record_path(ad, COLLECTION_DISPOSALS, disposal_id))], ad)
    return {"status": w_status, "disposal_id": disposal_id, "paths": paths,
            "conclusion_id": falsified["conclusion_id"]}


# ══ GLM 综合接口预留(P-C-14;§五能力级,R019 定稿对齐,零调用) ══════════


class GLMSynthesisAdapter:
    """GLM 综合适配器能力级协议(DESIGN §五 L135-L144;仅接口预留)。

    真实调用面=GLM_REAL_CALL_FACE(PENDING_USER_APPROVAL)——本模块不提供任何
    真实出站实现;注入点=
    synthesize_competing_hypotheses(adapter=…) 显式依赖注入(测试一律本地
    合成桩,禁任何真实出站)。
    """

    def synthesize(self, payload):
        raise NotImplementedError(
            "能力级接口预留: 适配器须经显式依赖注入提供(真实调用面="
            + GLM_REAL_CALL_FACE + ",零调用)")


class PendingGLMAdapter(GLMSynthesisAdapter):
    """PENDING 桩: 缺席登记返回(R019 §三(b)3 同款)——不部分产出、不静默跳过、
    任务状态不因此推进;零调用零网络零凭证零付费。"""

    def synthesize(self, payload):
        payload = payload or {}
        return {"status": GLM_PENDING_STATUS,
                "contract_version": GLM_INPUT_CONTRACT_VERSION,
                "task_ref": payload.get("task_ref"),
                "snapshot_binding": payload.get("snapshot_binding"),
                "absent_reason": "真实 GLM 调用与费用=DP-4 确认权留用户"
                                 "(未批;本包零调用零网络零凭证零付费)",
                "absent_policy": "缺席登记: 本轮无 GLM 结论,不部分产出、"
                                 "不静默跳过,任务状态不因此推进"
                                 "(R019 §三(b)3 同款)",
                "called": False, "network": False}


PENDING_GLM_ADAPTER = PendingGLMAdapter()


def build_glm_synthesis_input(task_id, *, snapshot_dir=None, archive_dir=None):
    """GLM 综合输入构建(DESIGN §五 L139: 证据矩阵+假设集+快照 digest 绑定;
    字段名与 R019 GLMResearchInput 对齐[contract_version/mode/snapshot_binding/
    task_ref/prompt_contract])。

    快照纪律: 经 drr._load_snapshot_for_verify 加载+rp.digest_snapshot 重算
    +Gate A 放行核验(FAIL 快照不得进入 GLM 正式输入,DESIGN §3.1 承接);
    数值面=矩阵经 dm.assemble_matrix 复用汇编(模型不直接改写矩阵数值,
    DESIGN L119 同款纪律)。
    """
    ad = archive_dir or DEFAULT_ARCHIVE_DIR
    task = drr.load_task(task_id, ad)
    snap, load_err = drr._load_snapshot_for_verify(task["snapshot_id"], snapshot_dir)
    if snap is None:
        raise ValueError(f"GLM 输入构建快照不可载: {load_err}")
    gate_status = (snap.get("gate_a") or {}).get("status")
    if not rp.gate_allows_formal_research(gate_status):
        raise ValueError(f"Gate A={gate_status!r} 不放行正式研究,该快照不得进入"
                         f"GLM 正式输入(DESIGN §3.1)")
    digest = rp.digest_snapshot(snap)
    matrix = dm.assemble_matrix(task_id, archive_dir=ad)
    return {"contract_version": GLM_INPUT_CONTRACT_VERSION, "mode": "A",
            "snapshot_binding": {"snapshot_id": task["snapshot_id"],
                                 "snapshot_digest": digest,
                                 "gate_a": gate_status,
                                 "research_as_of": snap.get("as_of")},
            "task_ref": {"task_id": task_id, "question": task["question"]},
            "hypotheses": matrix["hypotheses"],
            "evidence_matrix": {"cells": matrix["cells"],
                                "summary": matrix["summary"],
                                "registered_params": matrix["registered_params"]},
            "prompt_contract": {"language": "zh",
                                "counter_evidence_required": True,
                                "min_competing_hypotheses": GLM_MIN_COMPETING_HYPOTHESES,
                                "numeric_grounding_required": True}}


def validate_glm_synthesis_output(payload):
    """预留输出契约轻量校验(DESIGN L140-L141 强制项+R019 §三(c) L102 三档)。

    校验面边界(承接登记): 本校验仅覆盖 P2 侧强制项(≥2 竞争假设/每假设
    falsifiable_conditions ≥1/confidence 词表/absent_ack 在场);R019 WP-G2
    结构化输出校验器全量面(竞争性判定/区分性判据/阈值来源约束/数值接地核对)
    不在本包重复实现。
    """
    issues = []
    if not isinstance(payload, dict):
        return [f"输出须为dict: {type(payload).__name__}"]
    hyps = payload.get("hypotheses")
    if not isinstance(hyps, list) or len(hyps) < GLM_MIN_COMPETING_HYPOTHESES:
        issues.append(f"hypotheses须为list且 ≥{GLM_MIN_COMPETING_HYPOTHESES}"
                      f"(强制项,DESIGN L141): "
                      f"实得{len(hyps) if isinstance(hyps, list) else type(hyps).__name__}")
    else:
        for i, h in enumerate(hyps):
            if not isinstance(h, dict):
                issues.append(f"hypotheses[{i}]须为dict")
                continue
            if not isinstance(h.get("statement"), str) or not h.get("statement"):
                issues.append(f"hypotheses[{i}].statement须为非空string")
            fc = h.get("falsifiable_conditions")
            if not isinstance(fc, list) or not fc:
                issues.append(f"hypotheses[{i}].falsifiable_conditions须为非空list"
                              f"(强制项,DESIGN L141)")
            if h.get("confidence") not in GLM_OUTPUT_CONFIDENCE_LEVELS:
                issues.append(f"hypotheses[{i}].confidence须为"
                              f"{'|'.join(GLM_OUTPUT_CONFIDENCE_LEVELS)}(R019 三档): "
                              f"{h.get('confidence')!r}")
    if not isinstance(payload.get("absent_ack"), list):
        issues.append("absent_ack须为list(缺席逐项承接,R019 §三(c)")
    return issues


def synthesize_competing_hypotheses(*, task_id=None, payload=None,
                                    adapter=None, snapshot_dir=None,
                                    archive_dir=None):
    """GLM 综合能力级入口(**注入点**: adapter 显式依赖注入,缺省=PENDING 桩)。

    零调用纪律: 缺省 PENDING_GLM_ADAPTER 返回缺席登记(不部分产出/不静默
    跳过/状态不因此推进);注入桩亦为本地合成对象,禁任何真实出站。
    返回 {adapter, result, output_valid, issues}(零写入,不改任务状态)。
    """
    if payload is None:
        if not task_id:
            raise ValueError("task_id 与 payload 须至少其一(输入契约面)")
        payload = build_glm_synthesis_input(task_id, snapshot_dir=snapshot_dir,
                                            archive_dir=archive_dir)
    active_adapter = adapter if adapter is not None else PENDING_GLM_ADAPTER
    result = active_adapter.synthesize(payload)
    if result.get("status") == GLM_PENDING_STATUS:
        return {"adapter": type(active_adapter).__name__, "result": result,
                "output_valid": None,
                "issues": ["缺席登记(真实调用面=" + GLM_REAL_CALL_FACE
                           + ",零调用);输出契约校验不适用于缺席产物"]}
    issues = validate_glm_synthesis_output(result)
    return {"adapter": type(active_adapter).__name__, "result": result,
            "output_valid": not issues, "issues": issues}


# ══ 集合读取件(上游 dm.list_evidence 同款范式;确定性排序) ═══════════════


def _list_collection(collection, validator, archive_dir, task_id):
    d = os.path.join(str(archive_dir or DEFAULT_ARCHIVE_DIR),
                     ARCHIVE_FAMILY, collection)
    out = []
    if os.path.isdir(d):
        for name in sorted(os.listdir(d)):
            if not name.endswith(".json") or name.startswith("."):
                continue
            with open(os.path.join(d, name), 'r', encoding='utf-8') as f:
                rec = json.load(f)
            if task_id is None or rec.get("task_id") == task_id:
                issues = validator(rec)
                if issues:
                    raise ValueError(f"记录档内校验失败({collection}/{name}): "
                                     + ";".join(issues))
                out.append(rec)
    return out


def _load_scoped_record(record_id, collection, archive_dir, label, validator, task_id):
    path = drr._record_path(archive_dir or DEFAULT_ARCHIVE_DIR, collection, record_id)
    if not os.path.exists(path):
        raise FileNotFoundError(f"{label}记录缺档: {record_id}")
    with open(path, 'r', encoding='utf-8') as f:
        record = json.load(f)
    issues = validator(record)
    if issues:
        raise ValueError(f"{label}记录档内校验失败({record_id}): " + ";".join(issues))
    return record


def list_conclusions(task_id, archive_dir=None):
    """任务全部结论记录(按 created_at+conclusion_id 确定性排序;append-only)。"""
    return sorted(_list_collection(COLLECTION_CONCLUSIONS,
                                   validate_conclusion_record,
                                   archive_dir, task_id),
                  key=lambda r: (r["created_at"], r["conclusion_id"]))


def list_disposals(task_id, archive_dir=None):
    """任务全部处置记录(按 created_at+disposal_id 确定性排序)。"""
    return sorted(_list_collection(COLLECTION_DISPOSALS,
                                   validate_disposal_record,
                                   archive_dir, task_id),
                  key=lambda r: (r["created_at"], r["disposal_id"]))
