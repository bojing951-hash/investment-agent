#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P2-WP-B: 证据矩阵装配与轮次推进引擎(P2 深研层第 2 实现包,确定性结构)

DESIGN docs/P2_DESIGN.md §七 WP-P2-B 行(L199-L203,基线工作树实读)确定性落地:
- §3.3 证据记录契约(L94): 字段级契约(metric_id/fact_id/value/observation_date/
  snapshot_id+digest/direction 支持|反对|中性/weight 星级 1-5[DP-2]/mechanism
  机制族 7 类/note)+反证解释对 explained/explained_note(L518 证据分级 v2
  explained 语义对齐;§4.3 反证参与封顶需区分已解释/未解释);
- §4.2 证据矩阵(L106-L119): hypotheses/evidence/cells(绑定对稀疏映射)/
  summary(支持数去重[report_generator.py L520]/反证数/未解释重大反证/
  机制覆盖数+star 计算字段);去重/封顶/星级**复用 allocation_engine 既有
  实现件**(_base_metric L562/split_evidence_direction L571/
  star_level_from_evidence L592/STAR_RULES L130/MAX_STAR_UNEXPLAINED_COUNTER
  L137)——要点②「与 L520-521 同构断言」=同一代码路径,非平行重写;
  矩阵由程序从证据记录确定性汇总(L119),模型不参与;
- §4.4 轮次推进/终止(L127-L131): 推进条件任一(新增证据≥1/判据可计算/
  反证检索义务未闭合)+终止条件枚举序①RESOLVED②ALL_FALSIFIED③INCONCLUSIVE
  (预算耗尽,DP-1 硬上界=L65 影响列)④INCONCLUSIVE(数据阻断,经快照
  gate_a 复核实证+阻断登记);轮次记录 append-only(L131),不回改历史轮;
- §3.1 快照纪律(L80): 一切取数经快照绑定——证据六重 fail-closed 接地
  (P-B-05): 快照可载(drr._load_snapshot_for_verify,结构性不可达原始采集档)
  +digest 重算绑定(rp.digest_snapshot,禁采声明值)+Gate A 放行核验
  (rp.gate_allows_formal_research,FAIL 快照不作正式证据源)+事实接地
  (fact_id 命中快照 facts 且 value/observation_date/metric_id 逐一相等)
  +事实质量≠FAIL(fe.grade_issues 词表)+任务面(ACTIVE/假设成员/轮次≤预算);
- e2e 编排入口(P-B-15,DESIGN L202/L203④): write=False 离线快照构建
  (P2-G-06 范式,sb 既有入口只读,本模块零原始采集档路径字面引用)+
  Gate A 如实核验+证据接地如实尝试+轮次收束;产物落 data/research/
  运行产物区(不 commit)。

上游复用(对齐=复用调用,禁复制分叉): WP-P2-A deep_research_registrar
(register_deep_research_task/load_task/current_status/append_lifecycle_event/
四集合载体/append-only 写入原语/DP-1/2/6 定值常量);生命周期迁移全部经
drr.append_lifecycle_event 既有状态保护机制转递(AC-07.5),本包零新增
状态值零改写迁移表。

范围排除(DESIGN L201): 按需配对计算(D2/P2-G-05)沿 E2E-B WP-B2 承接,
本包零实现零复制;事件日历(D3/P2-G-04)属 WP-P2-D;条件程序评估/GLM 属
WP-P2-C(本包消费其判定结果作确定性输入,判据判定锚定任务档登记面)。

纪律: 零网络(纯标准库+项目既有模块);零 GLM/凭证/付费;append-only
(重复/改写一律拒,B4 §四行6 同款);零墙钟入指纹;数据不足不填 0,
缺值如实缺席,数据阻断如实登记(§八 L228 如实纪律)。
参数登记: docs/P2_WP_B_REPORT.md §零.4/§零.5(DP-1/2/6 复用上游定值+
P-B-01..P-B-18,先登记后实现,运行后禁回改)。
"""
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deep_research_registrar as drr   # WP-P2-A 上游(复用调用,只读禁改)
import research_provenance as rp        # R5 digest_snapshot/R3 gate_allows_formal_research
import allocation_engine as ae          # 证据分级 v2 星级/去重/方向原语(同构复用)
import research_archive as ra           # 经 drr 转递(parse_snapshot_id/DIGEST_RE)

# ══ 载体与集合(P-B-01;挂共享档案族根,不占用 WP-A 既有 4 集合名) ═══════

ARCHIVE_FAMILY = drr.ARCHIVE_FAMILY                    # "research_archive"(复用引用)
COLLECTION_EVIDENCE = "deep_research_evidence"
COLLECTION_ROUNDS = "deep_research_rounds"
DEFAULT_ARCHIVE_DIR = drr.DEFAULT_ARCHIVE_DIR          # data/research/research_archive

EVIDENCE_RECORD_TYPE = "deep_research_evidence"
ROUND_RECORD_TYPE = "deep_research_round"

EVIDENCE_ID_PREFIX = "EVI-"        # DP-3: 避开上游已占 RT-DR-/HP-/FC-/EV-
ROUND_ID_PREFIX = "RD-"

# ══ 词表(P-B-02/P-B-03/P-B-04;DESIGN §3.3 L94+L518/L521 实读) ═════════

DIRECTIONS = ("支持", "反对", "中性")                  # DESIGN L94 原文三值
MECHANISM_FAMILIES = tuple(ae.MECHANISM_CATEGORIES)    # 7 类(allocation_engine L104 复用)
FACT_QUALITY_REJECTED = ("FAIL",)                     # FAIL 事实不得作数值证据(P-B-05⑤)
E2E_PRODUCTS_SUBDIR = os.path.join("data", "research", "p2_wp_b_e2e")

# ══ 基础件(上游原语复用;零墙钟入指纹,P-B-17) ═════════════════════════


def _now_iso():
    return drr._now_iso()


def make_evidence_id(task_id, hypothesis_id, round_no, spec, created_at):
    """EVI-{YYYYMMDD}-{sha256[:8]}: 指纹={task_id,hypothesis_id,round,接地数值
    字面(metric_id/fact_id/value/observation_date),direction,weight,mechanism,
    explained};不含墙钟内容(ymd 仅取自 created_at 日期段),重放幂等。"""
    fp = {"task_id": task_id, "hypothesis_id": hypothesis_id, "round": round_no,
          "metric_id": spec["metric_id"], "fact_id": spec["fact_id"],
          "value": spec["value"], "observation_date": spec["observation_date"],
          "direction": spec["direction"], "weight": spec["weight"],
          "mechanism": spec["mechanism"], "explained": bool(spec.get("explained"))}
    return f"{EVIDENCE_ID_PREFIX}{drr._ymd_of(created_at)}-{drr._hash8(fp)}"


def make_round_id(task_id, round_no, evidence_ids, round_input, created_at):
    """RD-{YYYYMMDD}-{sha256[:8]}: 指纹={task_id,round,evidence_ids 升序,
    criterion_judgments,hypotheses_falsified,data_blocking 声明};同轮次同输入
    重放→同 id→append-only 拒收(P-B-12)。"""
    fp = {"task_id": task_id, "round": round_no,
          "evidence_ids": sorted(evidence_ids),
          "criterion_judgments": sorted(
              [{"pair": sorted(j["pair"]), "criterion": j["criterion"],
                "holds": j["holds"]} for j in round_input.get("criterion_judgments") or []],
              key=drr._canonical),
          "hypotheses_falsified": sorted(set(round_input.get("hypotheses_falsified") or [])),
          "data_blocking": round_input.get("data_blocking")}
    return f"{ROUND_ID_PREFIX}{drr._ymd_of(created_at)}-{drr._hash8(fp)}"


# ══ 证据记录校验(P-B-02;issues 列表风格,空=合法) ═════════════════════

EVIDENCE_KEYS = ("record_type", "evidence_id", "task_id", "hypothesis_id",
                 "round", "created_at", "metric_id", "fact_id", "value",
                 "observation_date", "snapshot_id", "digest_snapshot",
                 "direction", "weight", "mechanism", "explained",
                 "explained_note", "note", "history")


def validate_evidence_record(record):
    issues = []
    if not isinstance(record, dict):
        return [f"记录须为dict: {type(record).__name__}"]
    for k in EVIDENCE_KEYS:
        if k not in record:
            issues.append(f"记录缺字段{k}(P-B-02)")
    if issues:
        return issues
    if record.get("record_type") != EVIDENCE_RECORD_TYPE:
        issues.append(f"record_type恒须字面量{EVIDENCE_RECORD_TYPE!r}")
    if not str(record.get("evidence_id", "")).startswith(EVIDENCE_ID_PREFIX):
        issues.append(f"evidence_id须为{EVIDENCE_ID_PREFIX}*族: {record.get('evidence_id')!r}")
    issues.extend(ra.validate_id_conventions(task_id=record.get("task_id")))
    if not str(record.get("hypothesis_id", "")).startswith(drr.HYPOTHESIS_ID_PREFIX):
        issues.append(f"hypothesis_id须为{drr.HYPOTHESIS_ID_PREFIX}*族: "
                      f"{record.get('hypothesis_id')!r}")
    r = record.get("round")
    if not isinstance(r, int) or isinstance(r, bool) or r < 1:
        issues.append(f"round须为正整数: {r!r}")
    ca = record.get("created_at")
    if not isinstance(ca, str) or not drr._iso_date_str_ok(ca):
        issues.append(f"created_at须为ISO8601字符串: {ca!r}")
    if not isinstance(record.get("metric_id"), str) or not record.get("metric_id"):
        issues.append(f"metric_id须为非空string: {record.get('metric_id')!r}")
    v = record.get("value")
    if not isinstance(v, (int, float)) or isinstance(v, bool):
        issues.append(f"value须为number(数据不足不填0,缺值不登记): {v!r}")
    od = record.get("observation_date")
    if not isinstance(od, str) or not drr._iso_date_str_ok(od):
        issues.append(f"observation_date须为ISO日期字符串: {od!r}")
    if record.get("fact_id") != f"{record.get('metric_id')}@{od}":
        issues.append(f"fact_id须为{{metric_id}}@{{observation_date}}(fe.make_fact L211 先例): "
                      f"{record.get('fact_id')!r}")
    sid = record.get("snapshot_id")
    if not isinstance(sid, str) or ra.parse_snapshot_id(sid) is None:
        issues.append(f"snapshot_id非规范(research_snapshot_YYYYMMDD[_vN]): {sid!r}")
    dg = record.get("digest_snapshot")
    if not isinstance(dg, str) or not ra.DIGEST_RE.match(dg or ""):
        issues.append(f"digest_snapshot格式非法(须R5十六位小写指纹): {dg!r}")
    if record.get("direction") not in DIRECTIONS:
        issues.append(f"direction须为{'|'.join(DIRECTIONS)}(DESIGN L94): "
                      f"{record.get('direction')!r}")
    w = record.get("weight")
    if not isinstance(w, int) or isinstance(w, bool) \
            or not (drr.DP2_WEIGHT_SCALE[0] <= w <= drr.DP2_WEIGHT_SCALE[1]):
        issues.append(f"weight须为{list(drr.DP2_WEIGHT_SCALE)}整数(DP-2): {w!r}")
    if record.get("mechanism") not in MECHANISM_FAMILIES:
        issues.append(f"mechanism须为机制族7类之一{list(MECHANISM_FAMILIES)}"
                      f"(L518,不以相近类冒充): {record.get('mechanism')!r}")
    ex = record.get("explained")
    if not isinstance(ex, bool):
        issues.append(f"explained须为bool: {ex!r}")
    elif ex and (not isinstance(record.get("explained_note"), str)
                 or not record.get("explained_note")):
        issues.append("explained=True 须携非空 explained_note(已解释反证的解释留档)")
    if not isinstance(record.get("note"), str) or not record.get("note"):
        issues.append(f"note须为非空string: {record.get('note')!r}")
    his = record.get("history")
    if not isinstance(his, list) or not his:
        issues.append("history须为非空list(初始登记条目在场)")
    return issues


def validate_round_record(record):
    issues = []
    if not isinstance(record, dict):
        return [f"记录须为dict: {type(record).__name__}"]
    keys = ("record_type", "round_id", "task_id", "round", "created_at",
            "evidence_ids", "matrix", "criterion_judgments",
            "hypotheses_falsified", "no_new_evidence_streak", "data_blocking",
            "decision", "blocking")
    for k in keys:
        if k not in record:
            issues.append(f"记录缺字段{k}(P-B-12)")
    if issues:
        return issues
    if record.get("record_type") != ROUND_RECORD_TYPE:
        issues.append(f"record_type恒须字面量{ROUND_RECORD_TYPE!r}")
    if not str(record.get("round_id", "")).startswith(ROUND_ID_PREFIX):
        issues.append(f"round_id须为{ROUND_ID_PREFIX}*族: {record.get('round_id')!r}")
    issues.extend(ra.validate_id_conventions(task_id=record.get("task_id")))
    r = record.get("round")
    if not isinstance(r, int) or isinstance(r, bool) or r < 1:
        issues.append(f"round须为正整数: {r!r}")
    ca = record.get("created_at")
    if not isinstance(ca, str) or not drr._iso_date_str_ok(ca):
        issues.append(f"created_at须为ISO8601字符串: {ca!r}")
    if not isinstance(record.get("evidence_ids"), list):
        issues.append("evidence_ids须为list")
    if not isinstance(record.get("matrix"), dict):
        issues.append("matrix须为dict(本轮汇编矩阵快照)")
    if not isinstance(record.get("criterion_judgments"), list):
        issues.append("criterion_judgments须为list")
    if not isinstance(record.get("hypotheses_falsified"), list):
        issues.append("hypotheses_falsified须为list")
    st = record.get("no_new_evidence_streak")
    if not isinstance(st, int) or isinstance(st, bool) or st < 0:
        issues.append(f"no_new_evidence_streak须为非负整数: {st!r}")
    dec = record.get("decision") or {}
    if not isinstance(dec, dict) or dec.get("action") not in ("advance", "hold", "terminal"):
        issues.append(f"decision.action须为advance|hold|terminal: {dec!r}")
    elif dec.get("action") == "terminal" and dec.get("terminal_status") not in drr.TERMINAL_STATUSES:
        issues.append(f"decision.terminal_status须为{drr.TERMINAL_STATUSES}: "
                      f"{dec.get('terminal_status')!r}")
    elif dec.get("action") != "terminal" and dec.get("terminal_status") is not None:
        issues.append("非terminal决策不得携terminal_status")
    if not isinstance(dec.get("reasons"), list) or not dec.get("reasons"):
        issues.append("decision.reasons须为非空list(判定依据登记)")
    return issues


# ══ 证据六重 fail-closed 接地(P-B-05;要点①) ═══════════════════════════


def _check_task_face(task, hypothesis_id, round_no, archive_dir):
    """接地⑥任务面: 当前态 ACTIVE+假设成员+轮次 ∈ [1, round_budget](DP-1)。"""
    cur = drr.current_status(task["task_id"], archive_dir)
    if cur != drr.STATUS_ACTIVE:
        raise ValueError(f"证据登记须任务处于ACTIVE(R1..Rn 轮次,DESIGN L46): "
                         f"当前推导态={cur}(task={task['task_id']})")
    if hypothesis_id not in task["hypothesis_ids"]:
        raise ValueError(f"hypothesis_id={hypothesis_id!r}不在任务假设集"
                         f"{task['hypothesis_ids']}")
    budget = task["registered_params"]["round_budget"]
    if not isinstance(round_no, int) or isinstance(round_no, bool) \
            or round_no < 1 or round_no > budget:
        raise ValueError(f"round须为[1,{budget}]整数(DP-1 预算,登记定值禁回改): {round_no!r}")


def _fact_index(snap):
    """快照事实索引(真实快照结构 facts=事实dict列表,snapshot_builder L420)。"""
    facts = (snap or {}).get("facts")
    if not isinstance(facts, list):
        return None, "快照缺facts事实列表(非规范研究快照结构)"
    return {f.get("fact_id"): f for f in facts if isinstance(f, dict)}, None


def _ground_and_build_record(task, round_no, spec, snapshot_dir,
                             archive_dir, created_at):
    """六重接地+记录构造;返回 (record, issues),issues 非空=拒收(零写入)。"""
    issues = []
    if not isinstance(spec, dict):
        return None, [f"证据规格须为dict: {type(spec).__name__}"]
    hypothesis_id = spec.get("hypothesis_id")
    try:
        _check_task_face(task, hypothesis_id, round_no, archive_dir)
    except ValueError as e:
        issues.append(str(e))
    for k in ("metric_id", "fact_id", "value", "observation_date",
              "snapshot_id", "direction", "weight", "mechanism", "note"):
        if k not in spec:
            issues.append(f"证据规格缺字段{k}(P-B-02)")
    if issues:
        return None, issues
    # ① 快照可载(经 snapshot_id 规范分解派生文件名,结构性不可达原始采集档)
    snap, load_err = drr._load_snapshot_for_verify(spec["snapshot_id"], snapshot_dir)
    if snap is None:
        issues.append(f"快照接地失败: {load_err}")
        return None, issues
    # ③ Gate A 纪律: FAIL 快照不作深研正式证据源(DESIGN §3.1 L80)
    gate_status = (snap.get("gate_a") or {}).get("status")
    if not rp.gate_allows_formal_research(gate_status):
        issues.append(f"Gate A={gate_status!r} 不放行正式研究(PASS/DEGRADED 之外,"
                      f"DESIGN §3.1 红线),本快照不得作为深研正式证据源: "
                      f"{spec['snapshot_id']}")
    # ② digest 重算绑定(禁采声明值,FIX-01 纪律)
    digest = rp.digest_snapshot(snap)
    # ④⑤ 事实接地+质量
    idx, idx_err = _fact_index(snap)
    if idx is None:
        issues.append(f"事实接地失败: {idx_err}")
    else:
        fact = idx.get(spec["fact_id"])
        if fact is None:
            issues.append(f"数值无 provenance 接地: fact_id={spec['fact_id']!r} "
                          f"不在快照 {spec['snapshot_id']} 事实集(fail-closed,"
                          f"DESIGN §3.3 L94,不得进入证据矩阵)")
        else:
            if fact.get("value") != spec["value"] or isinstance(fact.get("value"), bool):
                issues.append(f"数值与快照事实不符: 记录{spec['value']!r} vs "
                              f"快照{fact.get('value')!r}(fact_id={spec['fact_id']})")
            if str(fact.get("observation_date")) != str(spec["observation_date"]):
                issues.append(f"observation_date与快照事实不符: "
                              f"{spec['observation_date']!r} vs {fact.get('observation_date')!r}")
            if fact.get("metric_id") != spec["metric_id"]:
                issues.append(f"metric_id与快照事实不符: {spec['metric_id']!r} vs "
                              f"{fact.get('metric_id')!r}")
            if fact.get("quality_status") in FACT_QUALITY_REJECTED:
                issues.append(f"事实质量{fact.get('quality_status')!r}(校验失败/数据不足,"
                              f"不得作数值证据;词表=fe.grade_issues): {spec['fact_id']}")
    if issues:
        return None, issues
    ca = created_at or _now_iso()
    evidence_id = make_evidence_id(task["task_id"], hypothesis_id,
                                   round_no, spec, ca)
    record = {"record_type": EVIDENCE_RECORD_TYPE,
              "evidence_id": evidence_id, "task_id": task["task_id"],
              "hypothesis_id": hypothesis_id, "round": round_no,
              "created_at": ca,
              "metric_id": spec["metric_id"], "fact_id": spec["fact_id"],
              "value": spec["value"], "observation_date": spec["observation_date"],
              "snapshot_id": spec["snapshot_id"], "digest_snapshot": digest,
              "direction": spec["direction"], "weight": spec["weight"],
              "mechanism": spec["mechanism"],
              "explained": bool(spec.get("explained")),
              "explained_note": spec.get("explained_note"),
              "note": spec["note"],
              "history": [{"ts": ca, "note": "证据登记入档(append-only;"
                           "六重 fail-closed 接地: 快照可载+digest重算+Gate A"
                           "+事实接地+质量≠FAIL+任务面)"}]}
    issues = validate_evidence_record(record)
    return (record if not issues else None), issues


def register_evidence(task_id, round_no, spec, snapshot_dir, *,
                      archive_dir=None, created_at=None):
    """单条证据登记(公开面;六重接地任一不过即拒,零写入)。"""
    ad = archive_dir or DEFAULT_ARCHIVE_DIR
    task = drr.load_task(task_id, ad)
    record, issues = _ground_and_build_record(task, round_no, spec,
                                              snapshot_dir, ad, created_at)
    if issues:
        raise ValueError("证据接地未过校验(fail-loud): " + ";".join(issues))
    status, _ = drr._write_records(
        [(record, drr._record_path(ad, COLLECTION_EVIDENCE, record["evidence_id"]))], ad)
    return {"status": status, "evidence_id": record["evidence_id"],
            "task_id": task_id, "round": round_no,
            "digest_snapshot": record["digest_snapshot"]}


def list_evidence(task_id, archive_dir=None):
    """任务全部证据记录(按 evidence_id 升序;确定性汇编输入序)。"""
    d = os.path.join(str(archive_dir or DEFAULT_ARCHIVE_DIR),
                     ARCHIVE_FAMILY, COLLECTION_EVIDENCE)
    out = []
    if os.path.isdir(d):
        for name in sorted(os.listdir(d)):
            if not name.endswith(".json") or name.startswith("."):
                continue
            with open(os.path.join(d, name), 'r', encoding='utf-8') as f:
                rec = json.load(f)
            if rec.get("task_id") == task_id:
                issues = validate_evidence_record(rec)
                if issues:
                    raise ValueError(f"证据记录档内校验失败({name}): "
                                     + ";".join(issues))
                out.append(rec)
    return sorted(out, key=lambda r: r["evidence_id"])


def list_rounds(task_id, archive_dir=None):
    """任务全部轮次记录(按 round 升序;append-only 历史)。"""
    d = os.path.join(str(archive_dir or DEFAULT_ARCHIVE_DIR),
                     ARCHIVE_FAMILY, COLLECTION_ROUNDS)
    out = []
    if os.path.isdir(d):
        for name in sorted(os.listdir(d)):
            if not name.endswith(".json") or name.startswith("."):
                continue
            with open(os.path.join(d, name), 'r', encoding='utf-8') as f:
                rec = json.load(f)
            if rec.get("task_id") == task_id:
                issues = validate_round_record(rec)
                if issues:
                    raise ValueError(f"轮次记录档内校验失败({name}): "
                                     + ";".join(issues))
                out.append(rec)
    return sorted(out, key=lambda r: r["round"])


# ══ 矩阵装配(P-B-06/P-B-07/P-B-08;§4.2 程序确定性汇总) ═══════════════


def _to_v2_item(ev):
    """证据记录 → 证据分级 v2 条目形态(P-B-03 映射;L518 contrary/neutral/
    explained 语义;ae.split_evidence_direction/star_level_from_evidence 消费)。"""
    return {"metric": ev["metric_id"], "mechanism": ev["mechanism"],
            "obs_date": ev["observation_date"],
            "contrary": ev["direction"] == "反对",
            "neutral": ev["direction"] == "中性",
            "explained": bool(ev.get("explained"))}


def assemble_matrix(task_id, *, archive_dir=None):
    """证据矩阵确定性汇编: hypotheses(按 hypothesis_id 升序)×evidence(按
    evidence_id 升序)→cells(绑定对稀疏映射)→summary(支持数去重/反证数/
    未解释重大反证/机制覆盖数+star;去重/封顶经 ae 既有实现件,与 L520-521
    同一代码路径)。同输入同输出(字节级: canonical sort_keys 序列化相等)。"""
    ad = archive_dir or DEFAULT_ARCHIVE_DIR
    task = drr.load_task(task_id, ad)
    hypotheses = []
    for hp_id in sorted(task["hypothesis_ids"]):
        hp = drr._load_record(hp_id, drr.COLLECTION_HYPOTHESES, ad, "假设",
                              drr.validate_hypothesis_record)
        hypotheses.append({"hypothesis_id": hp_id, "statement": hp["statement"],
                           "mechanism_story": hp["mechanism_story"],
                           "status": hp["status"]})
    evidence = list_evidence(task_id, ad)
    cells = {}
    by_hp = {}
    for ev in evidence:
        cells[f"{ev['hypothesis_id']}|{ev['evidence_id']}"] = {
            "direction": ev["direction"], "weight": ev["weight"]}
        by_hp.setdefault(ev["hypothesis_id"], []).append(ev)
    summary = {}
    for h in hypotheses:
        evs = by_hp.get(h["hypothesis_id"], [])
        v2 = [_to_v2_item(e) for e in evs]
        supporting, contrary, unexplained, _neutral = ae.split_evidence_direction(v2)
        base_support = {ae._base_metric(i["metric"]) for i in supporting}
        base_contrary = {ae._base_metric(i["metric"]) for i in contrary}
        cats = {i.get("mechanism") for i in supporting}
        star, _desc = ae.star_level_from_evidence(v2)
        summary[h["hypothesis_id"]] = {
            "支持数": len(base_support),
            "反证数": len(base_contrary),
            "未解释重大反证": bool(unexplained),
            "机制覆盖数": len(cats),
            "star": star,
        }
    return {"task_id": task_id, "registered_params": dict(task["registered_params"]),
            "hypotheses": hypotheses, "evidence": evidence, "cells": cells,
            "summary": summary}


# ══ 生命周期衔接(P-B-14;全复用 drr 既有状态保护机制) ═════════════════


def activate_task(task_id, *, archive_dir=None, created_at=None, note=None):
    """DRAFT→ACTIVE(R1..Rn 轮次开启;经 drr.append_lifecycle_event 迁移表)。"""
    return drr.append_lifecycle_event(
        task_id, drr.STATUS_DRAFT, drr.STATUS_ACTIVE,
        note or "轮次引擎激活: 进入 R1..Rn 轮次(§2.2 L46)",
        archive_dir=archive_dir, created_at=created_at)


# ══ 轮次引擎(P-B-09..P-B-13;§4.4 推进/终止确定性判定,要点③) ═════════


def _last_round(task_id, archive_dir):
    rounds = list_rounds(task_id, archive_dir)
    return rounds[-1] if rounds else None


def _registered_criteria_keys(task):
    """任务档已登记区分性判据键集((sorted(pair),criterion);判定锚定面)。"""
    return {tuple(sorted(c["pair"])) + (c["criterion"],)
            for c in task["discriminating_criteria"]}


def _validate_round_input(task, round_input, archive_dir):
    """轮次输入契约校验(P-B-09): 判据判定锚定登记面/证伪与义务成员命中/
    轮次序贯(round=既有+1)/阻断声明形态。"""
    if not isinstance(round_input, dict):
        raise ValueError(f"round_input须为dict: {type(round_input).__name__}")
    tid = task["task_id"]
    cur = drr.current_status(tid, archive_dir)
    if cur != drr.STATUS_ACTIVE:
        raise ValueError(f"轮次引擎须任务处于ACTIVE: 当前推导态={cur}(task={tid})")
    rnd = round_input.get("round")
    budget = task["registered_params"]["round_budget"]
    if not isinstance(rnd, int) or isinstance(rnd, bool) \
            or rnd < 1 or rnd > budget:
        raise ValueError(f"round须为[1,{budget}]整数(DP-1 预算): {rnd!r}")
    last = _last_round(tid, archive_dir)
    prev_no = last["round"] if last else 0
    if rnd != prev_no + 1:
        raise ValueError(f"轮次须序贯append-only(round=既有+1={prev_no + 1}): "
                         f"实得{rnd}(既有{prev_no};历史轮不可改写,DESIGN L131)")
    registered = _registered_criteria_keys(task)
    for i, j in enumerate(round_input.get("criterion_judgments") or []):
        if not isinstance(j, dict):
            raise ValueError(f"criterion_judgments[{i}]须为dict")
        pair = j.get("pair")
        if not isinstance(pair, list) or len(pair) != 2 \
                or not all(isinstance(p, str) for p in pair):
            raise ValueError(f"criterion_judgments[{i}].pair须为两条hypothesis_id的list: {pair!r}")
        if pair[0] == pair[1] or any(p not in task["hypothesis_ids"] for p in pair):
            raise ValueError(f"criterion_judgments[{i}].pair成员未命中任务假设集: {pair!r}")
        if not isinstance(j.get("criterion"), str) or not j["criterion"]:
            raise ValueError(f"criterion_judgments[{i}].criterion须为非空string")
        if not isinstance(j.get("holds"), bool):
            raise ValueError(f"criterion_judgments[{i}].holds须为bool: {j.get('holds')!r}")
        if tuple(sorted(pair)) + (j["criterion"],) not in registered:
            raise ValueError(f"criterion_judgments[{i}]未锚定任务档已登记判据集"
                             f"(判定须引用登记面,DESIGN L103/DP-6): {pair!r}×{j['criterion']!r}")
    for key in ("hypotheses_falsified", "counter_search_open"):
        for i, hp in enumerate(round_input.get(key) or []):
            if hp not in task["hypothesis_ids"]:
                raise ValueError(f"{key}[{i}]未命中任务假设集: {hp!r}")
    if not isinstance(round_input.get("criterion_computable", False), bool):
        raise ValueError("criterion_computable须为bool")
    blocking = round_input.get("data_blocking")
    if blocking is not None and (not isinstance(blocking, dict)
                                 or not isinstance(blocking.get("snapshot_id"), str)
                                 or not blocking.get("snapshot_id")
                                 or not isinstance(blocking.get("detail"), str)
                                 or not blocking.get("detail")):
        raise ValueError("data_blocking须为{snapshot_id,detail}或null")


def _verify_blocking(blocking, snapshot_dir):
    """阻断声明复核(P-B-09/P-B-10④): 经快照 gate_a 实证——快照实为放行态
    而声明阻断→拒收不一致声明;FAIL→阻断成立(携 core_missing/core_fail 登记)。"""
    snap, load_err = drr._load_snapshot_for_verify(blocking["snapshot_id"], snapshot_dir)
    if snap is None:
        return None, [f"阻断声明快照不可载: {load_err}"]
    ga = snap.get("gate_a") or {}
    gate_status = ga.get("status")
    if rp.gate_allows_formal_research(gate_status):
        return None, [f"阻断声明与事实不符: 快照{blocking['snapshot_id']} "
                      f"gate_a={gate_status!r} 放行正式研究,不构成 Gate A 阻断"
                      f"(DESIGN §4.4④ 阻断=快照 Gate A FAIL)"]
    verified = {"snapshot_id": blocking["snapshot_id"],
                "claim": blocking["detail"],
                "gate_a_status": gate_status,
                "core_missing": list(ga.get("core_missing") or []),
                "core_fail": list(ga.get("core_fail") or []),
                "verified_by": "engine_gate_a_recheck"}
    return verified, []


def run_round(task_id, round_input, snapshot_dir, *,
              archive_dir=None, created_at=None):
    """执行一轮: 证据批(两段式: 全量校验后原子落档)→矩阵汇编→§4.4 推进/终止
    判定→轮次记录 append-only(+终态经 drr 事件溯源迁移)。

    返回 {status, round_id, round, evidence_ids, decision, matrix,
    terminal_event};decision.action ∈ advance|hold|terminal。
    """
    ad = archive_dir or DEFAULT_ARCHIVE_DIR
    task = drr.load_task(task_id, ad)
    tid = task["task_id"]
    _validate_round_input(task, round_input, ad)
    rnd = round_input["round"]
    # ── 证据批: 全量六重接地校验(任一不过→零写入 fail-loud) ──
    records = []
    for i, spec in enumerate(round_input.get("evidence") or []):
        rec, issues = _ground_and_build_record(task, rnd, spec, snapshot_dir,
                                               ad, created_at)
        if issues:
            raise ValueError(f"证据[{i}]接地未过校验(批内零写入): " + ";".join(issues))
        records.append(rec)
    # ── 阻断复核(声明经快照 gate_a 实证) ──
    blocking = round_input.get("data_blocking")
    verified_blocking, b_issues = (None, [])
    if blocking is not None:
        verified_blocking, b_issues = _verify_blocking(blocking, snapshot_dir)
        if b_issues:
            raise ValueError("数据阻断声明未过复核(fail-loud): " + ";".join(b_issues))
    # ── 证据批原子落档(预检零存在→rejected-duplicate 零写入) ──
    if records:
        planned = [(rec, drr._record_path(ad, COLLECTION_EVIDENCE,
                                          rec["evidence_id"])) for rec in records]
        w_status, _ = drr._write_records(planned, ad)
        if w_status != drr.STATUS_WRITTEN:
            return {"status": w_status, "round_id": None, "round": rnd,
                    "evidence_ids": [r["evidence_id"] for r in records],
                    "decision": None, "matrix": None, "terminal_event": None,
                    "blocking": None}
    # ── 矩阵汇编(含本轮新证据;程序确定性汇总) ──
    matrix = assemble_matrix(tid, archive_dir=ad)
    evidence_ids = [r["evidence_id"] for r in records]
    # ── §4.4 终止判定(枚举序 ①→②→③→④,登记的确定性平局规则) ──
    judgments = round_input.get("criterion_judgments") or []
    falsified = sorted(set(round_input.get("hypotheses_falsified") or []))
    last = _last_round(tid, ad)
    prev_streak = last["no_new_evidence_streak"] if last else 0
    streak = 0 if evidence_ids else prev_streak + 1
    budget = task["registered_params"]["round_budget"]
    action, terminal_status, rule = None, None, None
    reasons = []
    if any(j["holds"] for j in judgments):
        action, terminal_status = "terminal", "RESOLVED"
        rule = "§4.4①区分性判据判定成立"
        reasons = [f"判据判定成立: {j['criterion'][:60]}" for j in judgments if j["holds"]]
    elif set(falsified) >= set(task["hypothesis_ids"]):
        action, terminal_status = "terminal", "ALL_FALSIFIED"
        rule = "§4.4②全部假设被证伪"
        reasons = [f"证伪假设集=任务假设集: {falsified}"]
    elif rnd >= budget:
        action, terminal_status = "terminal", "INCONCLUSIVE"
        rule = "§4.4③轮次预算耗尽(DP-1 硬上界,§2.4 L65「预算耗尽→INCONCLUSIVE 收束」)"
        reasons = [f"round={rnd}≥预算{budget}", f"连续无新增证据轮数={streak}"]
    elif verified_blocking is not None:
        action, terminal_status = "terminal", "INCONCLUSIVE"
        rule = "§4.4④数据阻断(快照 Gate A FAIL,经引擎复核实证)"
        reasons = [f"阻断登记: gate_a={verified_blocking['gate_a_status']!r}",
                   f"core_missing={verified_blocking['core_missing']}",
                   f"core_fail={verified_blocking['core_fail']}",
                   f"声明: {verified_blocking['claim']}"]
    else:
        if evidence_ids:
            reasons.append(f"§4.4推进①本轮新增可评估证据{len(evidence_ids)}条")
        if round_input.get("criterion_computable"):
            reasons.append("§4.4推进②区分性判据本轮窗口内可计算")
        open_ob = sorted(set(round_input.get("counter_search_open") or []))
        if open_ob:
            reasons.append(f"§4.4推进③反证检索义务未闭合(假设{len(open_ob)}个: {open_ob})")
        action = "advance" if reasons else "hold"
        if action == "hold":
            reasons = ["无推进条件命中且无终止条件触发(§4.4 L129 三项皆无;"
                       "确定性留守输出,由外层驱动决定是否再入轮)"]
    ca = created_at or _now_iso()
    round_id = make_round_id(tid, rnd, evidence_ids, round_input, ca)
    decision = {"action": action, "terminal_status": terminal_status,
                "rule": rule, "reasons": reasons}
    round_record = {"record_type": ROUND_RECORD_TYPE,
                    "round_id": round_id, "task_id": tid, "round": rnd,
                    "created_at": ca, "evidence_ids": evidence_ids,
                    "matrix": matrix, "criterion_judgments": judgments,
                    "hypotheses_falsified": falsified,
                    "no_new_evidence_streak": streak,
                    "data_blocking": round_input.get("data_blocking"),
                    "decision": decision, "blocking": verified_blocking}
    v_issues = validate_round_record(round_record)
    if v_issues:
        raise ValueError("轮次记录未过schema校验(fail-loud): " + ";".join(v_issues))
    w_status, _ = drr._write_records(
        [(round_record, drr._record_path(ad, COLLECTION_ROUNDS, round_id))], ad)
    if w_status != drr.STATUS_WRITTEN:                  # 同id重放→零写入如实返回
        return {"status": w_status, "round_id": round_id, "round": rnd,
                "evidence_ids": evidence_ids, "decision": decision,
                "matrix": matrix, "terminal_event": None,
                "blocking": verified_blocking}
    terminal_event = None
    if action == "terminal":
        terminal_event = drr.append_lifecycle_event(
            tid, drr.STATUS_ACTIVE, terminal_status,
            f"轮次引擎终态: {rule}; " + "; ".join(reasons[:3]),
            archive_dir=ad, created_at=ca)
    return {"status": drr.STATUS_WRITTEN, "round_id": round_id, "round": rnd,
            "evidence_ids": evidence_ids, "decision": decision,
            "matrix": matrix, "terminal_event": terminal_event,
            "blocking": verified_blocking}


# ══ e2e 编排入口(P-B-15;要点④;write=False 离线快照,P2-G-06 范式) ═════

E2E_QUESTION = ("P2-WP-B 授权副本端到端集成: {ymd} 研究快照的证据接地"
                "与轮次收束判定(确定性编排验证,非投资研究,不构成投资建议)")
E2E_H1S = "数据面完整假设: 当日快照核心数据面完整,Gate A 放行,证据接地应通过"
E2E_H1M = "Gate A 放行且事实接地命中时,数值证据可入矩阵并推进轮次"
E2E_H2S = "数据阻断假设: 当日快照核心数据面不完整,任务应按数据阻断收束"
E2E_H2M = "Gate A FAIL 或核心缺失时,证据接地 fail-closed,轮次引擎按 §4.4④ 收束"
E2E_H1C = {"metric_id": "SPX", "operator": ">=", "threshold": 0.0,
           "window": {"mode": "expiry", "weeks": 4}, "premise": None,
           "threshold_source": "user_explicit", "direction": "supporting",
           "source_note": "e2e 合成条件(登记常量)"}
E2E_H2C = {"metric_id": "SHCOMP", "operator": "<=", "threshold": 99999.0,
           "window": {"mode": "expiry", "weeks": 4}, "premise": None,
           "threshold_source": "user_explicit", "direction": "falsifying",
           "source_note": "e2e 合成条件(登记常量)"}
E2E_CRITERION = ("Gate A 状态与核心缺失清单: 放行→数据面完整假设存活;"
                 "FAIL→数据阻断假设存活")


def run_dev_copy_end_to_end(target_ymd="20261102", *, repo_root=None,
                            data_dir=None, trusted_root=None, as_of=None,
                            created_at=None):
    """DEV 授权数据副本端到端(DESIGN L203④+L202;P-B-15)。

    流程: ①sb.build_snapshot(target_ymd, write=False) 离线构建(P2-G-06 范式;
    data_dir 缺省=sb 既有默认入口=授权副本只读——本模块零原始采集档路径字面
    引用;data_dir/trusted_root/as_of 透传参数仅测试沙箱注入用,FIX7-AC §5.3
    fixture 可信根纪律)→②快照物化至运行产物区(允许写入不 commit)→③digest
    重算+Gate A 如实核验→④合成研究任务注册(绑定快照;登记常量)→⑤激活+证据
    接地如实尝试(gate 放行→正向落档;FAIL→fail-closed 拒收并如实记录)→
    ⑥run_round R1(阻断路径经引擎复核)→⑦产物 JSON 落运行产物区。

    返回结果 dict 并打印日志行(原始 stdout 供步骤10采证)。
    """
    import snapshot_builder as sb                      # lazy(P-B-16)
    import io
    from contextlib import redirect_stdout
    root = os.path.abspath(repo_root or os.getcwd())
    products = os.path.join(root, E2E_PRODUCTS_SUBDIR, target_ymd)
    snap_dir = os.path.join(products, "snapshots")
    os.makedirs(snap_dir, exist_ok=True)
    lines = []

    def log(msg):
        print(msg)
        lines.append(msg)

    log(f"[e2e] target_ymd={target_ymd} write=False 离线构建(P2-G-06 范式)")
    buf = io.StringIO()
    with redirect_stdout(buf):
        snap = sb.build_snapshot(target_ymd=target_ymd, write=False,
                                 data_dir=data_dir, trusted_root=trusted_root,
                                 as_of=as_of)
    sid = str(snap.get("snapshot_id"))
    digest = rp.digest_snapshot(snap)
    gate_status = (snap.get("gate_a") or {}).get("status")
    allows = rp.gate_allows_formal_research(gate_status)
    log(f"[e2e] snapshot_id={sid} digest={digest}")
    log(f"[e2e] gate_a.status={gate_status!r} 放行正式研究={allows}")
    with open(os.path.join(snap_dir, f"{sid}.json"), "w", encoding="utf-8") as f:
        json.dump(snap, f, ensure_ascii=False, sort_keys=True, indent=1)
    log(f"[e2e] 快照物化(运行产物区,不 commit): {os.path.join(snap_dir, sid + '.json')}")
    # drr.DEFAULT_ARCHIVE_DIR 为绝对常量(模块位置解析),os.path.join(root,绝对值)
    # 会静默丢弃 root——测试沙箱将逃逸至仓库实档。取其尾部三段相对锚,
    # 档案区恒随 repo_root 落位(测试沙箱内聚,正式运行=仓库运行产物区)。
    _archive_tail = os.sep.join(drr.DEFAULT_ARCHIVE_DIR.split(os.sep)[-3:])
    archive_dir = os.path.join(root, _archive_tail)
    ca = created_at or _now_iso()
    reg = drr.register_deep_research_task(
        E2E_QUESTION.format(ymd=target_ymd),
        {"origin_query_id": f"QB-{target_ymd}-001"},
        [{"statement": E2E_H1S, "mechanism_story": E2E_H1M,
          "conditions": [dict(E2E_H1C)]},
         {"statement": E2E_H2S, "mechanism_story": E2E_H2M,
          "conditions": [dict(E2E_H2C)]}],
        [{"pair": [E2E_H1S, E2E_H2S], "criterion": E2E_CRITERION}],
        snap, archive_dir=archive_dir, created_at=ca)
    task_id = reg["task_id"]
    log(f"[e2e] 任务注册: status={reg['status']} task_id={task_id}")
    activate_task(task_id, archive_dir=archive_dir, created_at=ca)
    log(f"[e2e] 任务激活: DRAFT→ACTIVE(R1 轮次开启)")
    # 证据接地如实尝试: 从快照事实实取一条非FAIL质量事实构造证据规格
    idx, idx_err = _fact_index(snap)
    attempt = {"outcome": "skipped", "reason": idx_err or "无可用事实"}
    ev_spec = None
    if idx is not None:
        for fact in snap.get("facts", []):
            if isinstance(fact, dict) and fact.get("quality_status") \
                    not in FACT_QUALITY_REJECTED \
                    and isinstance(fact.get("value"), (int, float)) \
                    and not isinstance(fact.get("value"), bool):
                ev_spec = {"hypothesis_id": reg["hypothesis_ids"][0],
                           "metric_id": fact["metric_id"],
                           "fact_id": fact["fact_id"],
                           "value": fact["value"],
                           "observation_date": fact["observation_date"],
                           "snapshot_id": sid,
                           "direction": "支持", "weight": 3,
                           "mechanism": ae.mechanism_of(fact["metric_id"]),
                           "note": "e2e 证据接地如实尝试(登记常量方向/权重)"}
                break
    round_evidence = []
    if ev_spec is not None:
        try:
            r = register_evidence(task_id, 1, ev_spec, snap_dir,
                                  archive_dir=archive_dir, created_at=ca)
            attempt = {"outcome": r["status"], "evidence_id": r["evidence_id"],
                       "fact_id": ev_spec["fact_id"]}
            log(f"[e2e] 证据接地尝试: {r['status']} ({ev_spec['fact_id']})")
            if r["status"] == drr.STATUS_WRITTEN:
                round_evidence = []          # 已独立落档,run_round 不重复提交
        except ValueError as e:
            attempt = {"outcome": "rejected-fail-closed",
                       "fact_id": ev_spec["fact_id"], "reason": str(e)}
            log(f"[e2e] 证据接地尝试: rejected-fail-closed")
            log(f"[e2e] 拒收理由: {e}")
    else:
        log(f"[e2e] 证据接地尝试: skipped({attempt['reason']})")
    blocking = None
    if not allows:
        ga = snap.get("gate_a") or {}
        blocking = {"snapshot_id": sid,
                    "detail": (f"Gate A={gate_status!r}; "
                               f"core_missing={ga.get('core_missing') or []}; "
                               f"core_fail={ga.get('core_fail') or []}")}
        log(f"[e2e] 数据阻断输入(如实,不编造): {blocking['detail']}")
    round_res = run_round(task_id, {"round": 1, "evidence": round_evidence,
                                    "criterion_judgments": [],
                                    "hypotheses_falsified": [],
                                    "criterion_computable": False,
                                    "counter_search_open": [],
                                    "data_blocking": blocking},
                          snap_dir, archive_dir=archive_dir, created_at=ca)
    dec = round_res["decision"]
    log(f"[e2e] R1 轮次判定: action={dec['action']} "
        f"terminal={dec['terminal_status']} rule={dec['rule']}")
    cur = drr.current_status(task_id, archive_dir)
    log(f"[e2e] 任务终态推导: {cur}")
    result = {"target_ymd": target_ymd, "snapshot_id": sid, "digest": digest,
              "gate_a_status": gate_status, "gate_allows": allows,
              "task_id": task_id, "hypothesis_ids": reg["hypothesis_ids"],
              "condition_ids": reg["condition_ids"],
              "evidence_attempt": attempt,
              "round": {"round_id": round_res["round_id"],
                        "decision": dec,
                        "no_new_evidence_streak_reasons": None},
              "current_status": cur,
              "events": drr.list_events(task_id, archive_dir),
              "products_dir": products}
    result_path = os.path.join(products, "e2e_result.json")
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, sort_keys=True, indent=1)
    log(f"[e2e] 产物落档(不 commit): {result_path}")
    log("[e2e] 声明: 本编排为确定性集成验证,输出不构成投资建议(禁交易/仓位/收益承诺)")
    result["log"] = lines
    return result
