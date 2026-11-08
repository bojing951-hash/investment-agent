#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P03-E2EB-WP-B4: 共享研究档案与查询历史存储模块(append-only,纯离线)。

DESIGN docs/P03_E2EB_DESIGN.md §4.1(L180-185)与 §六 WP-B4 行(L228-232)的确定性落地
(行号=基线工作树 b5c33f85 实读):
- query_history 集合: 模式B查询 IR+作答摘要归档,一记录一文件,append-only
  (重复写入/改写被拒,记录不可变不可删改,§四行6 L176);
- ID 引用约定: query_id=QB-YYYYMMDD-NNN(复用 qir.QUERY_ID_RE)/任务引用=RT- 前缀族
  (G3 先例 glm_conclusion_integrator.py:82;DESIGN L183 严格格式为其子集)/
  origin_query_id=严格 QB 格(L184 交叉引用约定;任务侧字段,本模块提供约定校验面,
  不建 E2E-A 任务集合存储——L230「本包只建模式B侧+引用约定」);
- snapshot_id+digest 内容级绑定: 每记录必携完整 snapshot_id(规范
  research_snapshot_YYYYMMDD[_vN])+R5 十六位指纹;append 时模块内经
  rp.digest_snapshot 重算(FIX-01 纪律: 内容绑定必实测重算,禁采声明值);
  verify_* 复算对照,篡改快照→校验拒绝(要点③);
- 同日单调计数与配号: allocate_query_id 承接 B1 D-B1-10「同日单调计数与落盘属
  WP-B4 档案」预留面(make_query_id 仅拼接,scripts/e2eb_query_ir.py:71-85)。

纪律: 零网络(纯标准库+B1/R5 既有模块复用);快照解析面仅打开由 snapshot_id
规范分解派生的 research_snapshot_*.json 文件名,结构性不可达 data/daily 原始
采集档(AC-07.1);零墙钟决策(archived_at 缺省 now 属登记落档时刻,测试显式注入;
seq 决策纯目录扫描)。

参数登记: docs/P03_E2EB_B4_REPORT.md §六 D-B4-01..D-B4-12(先登记后实现,运行后禁回改)。
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e2eb_query_ir as qir          # B1(复用禁复制,DESIGN L231「IR即首类记录」)
import research_provenance as rp     # R5 digest_snapshot(rp:1297-1301)

# ══ 载体与常量(D-B4-01/D-B4-03) ═════════════════════════════════════════

ARCHIVE_FAMILY = "research_archive"        # §4.1 L185 文件族名
ARCHIVE_COLLECTION = "query_history"       # §4.1 L185 模式B集合名
RECORD_TYPE_QUERY = "query_history"        # 记录类型字面量(D-B4-03)
MODE_B_LITERAL = "B"                       # IR L59 透传字面量

DEFAULT_ARCHIVE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'data', 'research', ARCHIVE_FAMILY)    # E2E-A DEFAULT_OUT_DIR 同源根(rtm.py:32-34)

QUERY_RECORD_KEYS = ("record_type", "query_id", "created_at", "mode",
                     "question_text", "as_of", "snapshot_id", "digest_snapshot",
                     "ir", "ir_stage", "answer_summary", "promoted_to_task_id",
                     "archived_at")

TASK_REF_RE = re.compile(r"^RT-\S+$")      # D-B4-02: RT-前缀族(G3 先例;L183 严格格为其子集;非空白余部)
DIGEST_RE = re.compile(r"^[0-9a-f]{16}$")  # R5 十六位小写指纹格式锁
_QUERY_FILE_RE = re.compile(r"^QB-(\d{8})-(\d{3})\.json$")
_SNAPSHOT_ID_PARTS_RE = re.compile(r"^research_snapshot_(\d{8})(?:_v(\d+))?$")

STATUS_WRITTEN = "written"
STATUS_REJECTED_DUPLICATE = "rejected-duplicate-query-id"
STATUS_REJECTED_NON_MONOTONIC = "rejected-non-monotonic-seq"

IR_STAGES = ("mapped", "executed")


# ══ ID 引用约定(D-B4-02/D-B4-07;要点②) ════════════════════════════════

def validate_id_conventions(*, query_id=None, origin_query_id=None,
                            task_id=None, promoted_to_task_id=None):
    """ID 引用约定校验(DESIGN §4.1 L183-184;返回 issues 列表,空=合法)。

    query_id/origin_query_id: 严格 QB-YYYYMMDD-NNN(复用 qir.QUERY_ID_RE);
    task_id/promoted_to_task_id: RT- 前缀族(非空余部;G3 在场先例,
    E2E-A 实况 task_id 形态 RT-{start}~{end}-{rule}-{hash8} 为合法成员,
    DESIGN L183 RT-YYYYMMDD-NNN 亦为合法成员——登记发现见 REPORT §七.2)。
    """
    issues = []
    for name, val, strict_qb in (("query_id", query_id, True),
                                 ("origin_query_id", origin_query_id, True),
                                 ("task_id", task_id, False),
                                 ("promoted_to_task_id", promoted_to_task_id, False)):
        if val is None:
            continue
        if not isinstance(val, str):
            issues.append(f"{name}须为string|null: {val!r}")
        elif strict_qb:
            if not qir.QUERY_ID_RE.match(val):
                issues.append(f"{name}格式非法(须QB-YYYYMMDD-NNN,DESIGN L183): {val!r}")
        else:
            if not TASK_REF_RE.match(val):
                issues.append(f"{name}格式非法(须RT-前缀族,DESIGN L183/G3先例): {val!r}")
    return issues


# ══ snapshot_id 规范分解与快照解析(D-B4-08;AC-07.1 纯度面) ═════════════

def parse_snapshot_id(snapshot_id):
    """research_snapshot_YYYYMMDD[_vN] → (ymd, N);base 版 N=1。

    非规范表示(_v0/_v1/前导零/整体不匹配)→ None(FIX2-04 纪律同源,
    rp._version_of:1212-1227;登记于 D-B4-03)。
    """
    if not isinstance(snapshot_id, str):
        return None
    m = _SNAPSHOT_ID_PARTS_RE.match(snapshot_id)
    if not m:
        return None
    ymd, vs = m.group(1), m.group(2)
    if vs is None:
        return ymd, 1
    if vs != str(int(vs)) or int(vs) < 2:   # 规范十进制,vN≥2
        return None
    return ymd, int(vs)


def _snapshot_filename(snapshot_id):
    parsed = parse_snapshot_id(snapshot_id)
    if parsed is None:
        return None
    ymd, ver = parsed
    suffix = "" if ver == 1 else f"_v{ver}"
    return f"research_snapshot_{ymd}{suffix}.json"


def _load_snapshot_for_binding(snapshot_id, snapshot_dir):
    """按 snapshot_id 规范分解派生文件名加载快照(唯一快照读取面)。

    仅构造 research_snapshot_*.json 文件名(派生自规范分解,无任何原始
    采集档文件名构造面);返回 (snapshot_dict, None) 或 (None, 原因)。
    """
    fname = _snapshot_filename(snapshot_id)
    if fname is None:
        return None, f"snapshot_id非规范(须research_snapshot_YYYYMMDD[_vN],vN≥2规范十进制): {snapshot_id!r}"
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
                      f"{snapshot_id!r}不符(R1身份纪律,rp.select_snapshot:1271-1277同款)")
    return snap, None


# ══ IR 阶段探测与确定性摘要(D-B4-04/D-B4-05) ═══════════════════════════

def _detect_ir_stage(ir):
    """executed 过 validate_ir→executed;否则 mapped 过→mapped;双败→ValueError。"""
    issues_exec = qir.validate_ir(ir, stage="executed")
    if not issues_exec:
        return "executed"
    issues_mapped = qir.validate_ir(ir, stage="mapped")
    if not issues_mapped:
        return "mapped"
    raise ValueError("IR未过任一阶段schema校验(fail-loud): "
                     f"executed=[{';'.join(issues_exec)}]; "
                     f"mapped=[{';'.join(issues_mapped)}]")


def build_answer_summary(ir, ir_stage, execution=None):
    """确定性作答摘要(D-B4-04): counts+values+refusal,无数值编造面。"""
    bcounts = {}
    for b in ir.get("metric_bindings", []):
        st = b.get("status")
        bcounts[st] = bcounts.get(st, 0) + 1
    ocounts = {}
    for op in ir.get("derived_operations", []):
        st = op.get("status")
        ocounts[st] = ocounts.get(st, 0) + 1
    refusal = None
    values = {}
    if isinstance(execution, dict):
        if execution.get("refusal") is not None:
            refusal = execution["refusal"]           # B2 D-B2-03 结构化拒绝原样上浮
        elif isinstance(execution.get("values"), dict):
            values = dict(execution["values"])       # 仅 RESOLVED 绑定(B2 D-B2-06)
    return {"ir_stage": ir_stage,
            "refusal": refusal,
            "binding_status_counts": {k: bcounts[k] for k in sorted(bcounts)},
            "op_status_counts": {k: ocounts[k] for k in sorted(ocounts)},
            "n_unresolved": len(ir.get("unresolved_entities", [])),
            "values": values}


# ══ 记录级校验(D-B4-03/D-B4-07) ═════════════════════════════════════════

def validate_query_record(record):
    """query_history 记录级全链校验;返回 issues 列表(空=合法),不抛校验异常。"""
    issues = []
    if not isinstance(record, dict):
        return [f"记录须为dict: {type(record).__name__}"]
    for k in QUERY_RECORD_KEYS:
        if k not in record:
            issues.append(f"记录缺字段{k}(D-B4-03)")
    if issues:
        return issues
    if record.get("record_type") != RECORD_TYPE_QUERY:
        issues.append(f"record_type恒须字面量{RECORD_TYPE_QUERY!r}(DESIGN L185集合名): "
                      f"{record.get('record_type')!r}")
    qid = record.get("query_id")
    if not isinstance(qid, str) or not qir.QUERY_ID_RE.match(qid or ""):
        issues.append(f"query_id格式非法(须QB-YYYYMMDD-NNN,DESIGN L183): {qid!r}")
    ca = record.get("created_at")
    if not isinstance(ca, str) or not qir.ISO_DATE_PREFIX_RE.match((ca or "")[:10]):
        issues.append(f"created_at须为ISO8601字符串: {ca!r}")
    if isinstance(ca, str) and isinstance(qid, str) and qir.QUERY_ID_RE.match(qid):
        if qid[3:11] != ca[:10].replace("-", ""):
            issues.append(f"query_id日期段({qid[3:11]})须与created_at日期段"
                          f"({ca[:10].replace('-', '')})一致(B1 make_query_id派生一致性,D-B1-10)")
    if record.get("mode") != MODE_B_LITERAL:
        issues.append(f"mode恒须字面量{MODE_B_LITERAL!r}(IR L59): {record.get('mode')!r}")
    qt = record.get("question_text")
    if not isinstance(qt, str) or not qt:
        issues.append("question_text须为非空string(DESIGN L60)")
    ao = record.get("as_of")
    if ao is not None and (not isinstance(ao, str) or not qir.AS_OF_RE.match(ao)):
        issues.append(f"as_of须为ISO日期/时间戳字符串或None(DESIGN L61): {ao!r}")
    sid = record.get("snapshot_id")
    if parse_snapshot_id(sid) is None:
        issues.append(f"snapshot_id非规范(research_snapshot_YYYYMMDD[_vN],vN≥2规范十进制,"
                      f"DESIGN L182+FIX2-04纪律): {sid!r}")
    dg = record.get("digest_snapshot")
    if not isinstance(dg, str) or not DIGEST_RE.match(dg or ""):
        issues.append(f"digest_snapshot格式非法(须R5十六位小写指纹): {dg!r}")
    stage = record.get("ir_stage")
    if stage not in IR_STAGES:
        issues.append(f"ir_stage须为{'|'.join(IR_STAGES)}: {stage!r}")
    ir = record.get("ir")
    if isinstance(ir, dict) and stage in IR_STAGES:
        ir_issues = qir.validate_ir(ir, stage=stage)
        for s in ir_issues:
            issues.append(f"ir未过{stage}阶段schema校验: {s}")
        # echo 一致性(记录=IR+绑定+摘要,echo 防分叉;D-B4-03)
        for k in ("created_at", "mode", "question_text", "as_of"):
            if k in ir and record.get(k) != ir.get(k):
                issues.append(f"echo字段{k}与ir.{k}不一致: {record.get(k)!r} vs {ir.get(k)!r}")
    elif not isinstance(ir, dict):
        issues.append(f"ir须为dict(DESIGN §三(a)): {type(ir).__name__}")
    pt = record.get("promoted_to_task_id")
    if pt is not None and (not isinstance(pt, str) or not TASK_REF_RE.match(pt or "")):
        issues.append(f"promoted_to_task_id须为null|RT-前缀族(DESIGN L184/G3先例): {pt!r}")
    aa = record.get("archived_at")
    if not isinstance(aa, str) or not qir.ISO_DATE_PREFIX_RE.match((aa or "")[:10]):
        issues.append(f"archived_at须为ISO8601字符串: {aa!r}")
    # IA-P1-WP-D PD-7: economy echo三条校验(可选键;旧记录无键合法)
    rec_econ = record.get("economy")
    if rec_econ is not None and rec_econ not in qir.ECONOMIES:
        issues.append(f"economy须为{qir.ECONOMIES}|None(经济体维度echo,"
                      f"DESIGN §四 L133): {rec_econ!r}")
    ir_econ = ir.get("economy") if isinstance(ir, dict) else None
    if ir_econ is not None and rec_econ is None:
        issues.append(f"ir携economy维度({ir_econ!r})但记录未echo economy键"
                      f"(引用经济体维度必落地,DESIGN §四 L142)")
    if (rec_econ is not None and ir_econ is not None and rec_econ != ir_econ):
        issues.append(f"economy echo与ir.economy不一致: {rec_econ!r} vs {ir_econ!r}")
    return issues


# ══ 同日单调与配号(D-B4-06;承接 D-B1-10) ═══════════════════════════════

def _collection_dir(archive_dir):
    return os.path.join(str(archive_dir), ARCHIVE_FAMILY, ARCHIVE_COLLECTION)


def list_query_records(archive_dir=None, ymd=None):
    """集合内全部 query_id(排序;ymd 给定时过滤同日子集)。"""
    d = _collection_dir(archive_dir or DEFAULT_ARCHIVE_DIR)
    if not os.path.isdir(d):
        return []
    out = []
    for name in os.listdir(d):
        m = _QUERY_FILE_RE.match(name)
        if m and (ymd is None or m.group(1) == str(ymd)):
            out.append(f"QB-{m.group(1)}-{m.group(2)}")
    return sorted(out)


def _same_day_max_seq(collection_dir, ymd):
    best = 0
    if not os.path.isdir(collection_dir):
        return 0
    for name in os.listdir(collection_dir):
        m = _QUERY_FILE_RE.match(name)
        if m and m.group(1) == str(ymd):
            best = max(best, int(m.group(2)))
    return best


def allocate_query_id(created_at, archive_dir=None):
    """同日单调配号: QB-{ymd}-{max+1:03d}(D-B1-10 承接;拼接复用 qir.make_query_id)。"""
    if not isinstance(created_at, str) or not qir.ISO_DATE_PREFIX_RE.match(created_at[:10]):
        raise ValueError(f"created_at须为ISO8601字符串: {created_at!r}")
    ymd = created_at[:10].replace("-", "")
    seq = _same_day_max_seq(_collection_dir(archive_dir or DEFAULT_ARCHIVE_DIR), ymd) + 1
    return qir.make_query_id(created_at, seq=seq)


# ══ append(要点①;D-B4-05) ═══════════════════════════════════════════════

def append_query_record(ir, *, snapshot, archive_dir=None, execution=None,
                        promoted_to_task_id=None, archived_at=None):
    """查询记录 append-only 落档;返回 (status, path)。

    status: written | rejected-duplicate-query-id | rejected-non-monotonic-seq
    (重复写入与改写一律拒,不区分内容;记录不可变不可删改,§四行6);
    schema 违规=ValueError fail-loud。digest 由模块经 R5 重算,API 无 digest 入参。
    """
    stage = _detect_ir_stage(ir)                                   # ①
    if not isinstance(snapshot, dict) or not snapshot.get("snapshot_id"):
        raise ValueError("snapshot须为携带snapshot_id的dict(注入绑定面,D-B4-05)")
    sid = str(snapshot["snapshot_id"])
    if parse_snapshot_id(sid) is None:
        raise ValueError(f"snapshot.snapshot_id非规范: {sid!r}")
    if ir.get("target_snapshot_id") is not None and ir["target_snapshot_id"] != sid:
        raise ValueError(f"ir.target_snapshot_id({ir['target_snapshot_id']!r})"
                         f"与注入快照({sid!r})不一致(绑定后不可变,DESIGN L177)")
    digest = rp.digest_snapshot(snapshot)                          # ③ R5 重算
    if isinstance(execution, dict) and "ir" in execution and execution["ir"] != ir:
        raise ValueError("execution.ir与归档ir不一致(D-B4-05④一致性)")
    if archived_at is None:
        archived_at = datetime.now(timezone.utc).isoformat(timespec='seconds')
    record = {"record_type": RECORD_TYPE_QUERY,
              "query_id": ir["query_id"],
              "created_at": ir["created_at"],
              "mode": ir["mode"],
              "question_text": ir["question_text"],
              "as_of": ir["as_of"],
              "snapshot_id": sid,
              "digest_snapshot": digest,
              "ir": ir,
              "ir_stage": stage,
              "answer_summary": build_answer_summary(ir, stage, execution),
              "promoted_to_task_id": promoted_to_task_id,
              "archived_at": archived_at}
    # IA-P1-WP-D PD-7: economy echo条件写(ir携economy维度→记录落地echo;
    # 衔接设计L142「凡引用经济体维度,必附snapshot_id+digest」的QB-侧维度落地;
    # 条件写=旧IR(无economy键)记录零变化,QUERY_RECORD_KEYS必填集不动)
    if ir.get("economy") is not None:
        record["economy"] = ir["economy"]
    issues = validate_query_record(record)                         # ⑥
    if issues:
        raise ValueError("查询记录未过schema校验(fail-loud): " + ";".join(issues))
    collection = _collection_dir(archive_dir or DEFAULT_ARCHIVE_DIR)
    path = os.path.join(collection, f"{record['query_id']}.json")
    if os.path.exists(path):                                       # ⑦ 唯一性
        return STATUS_REJECTED_DUPLICATE, path
    ymd = record["query_id"][3:11]
    seq = int(record["query_id"][12:])
    if seq <= _same_day_max_seq(collection, ymd):                  # ⑦ 同日单调
        return STATUS_REJECTED_NON_MONOTONIC, path
    os.makedirs(collection, exist_ok=True)                         # ⑧ 原子落盘
    _tmp = path + '.tmp'
    with open(_tmp, 'w', encoding='utf-8') as f:
        json.dump(record, f, ensure_ascii=False, indent=1, sort_keys=True)
    os.replace(_tmp, path)
    return STATUS_WRITTEN, path


# ══ 读回与验证(D-B4-08/D-B4-09;要点③) ═══════════════════════════════════

def load_query_record(query_id, archive_dir=None):
    """读回单条记录(缺档 FileNotFoundError)。"""
    if not isinstance(query_id, str) or not qir.QUERY_ID_RE.match(query_id or ""):
        raise ValueError(f"query_id格式非法: {query_id!r}")
    path = os.path.join(_collection_dir(archive_dir or DEFAULT_ARCHIVE_DIR),
                        f"{query_id}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"查询记录缺档: {query_id}")
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


# ══ research_full 旁挂(sidecar;批2 WI6 2026-11-09) ═══════════════════════
# 设计约束: 旧 query_history 格式**一字不动**(QUERY_RECORD_KEYS/digest 重算/
# 不可变/拒绝重复全部保留);完整研究内容(用户实际所见的作答正文/GLM 原文/
# warnings/violations/用户备注/前档链接)旁挂新文件,命名
# {query_id}.research-full.json——_QUERY_FILE_RE(^QB-\d{8}-\d{3}\.json$)不匹配,
# list_query_records/_same_day_max_seq 天然无视 sidecar(已实证),旧档案可无
# sidecar 存在(读侧缺失→None,不报错)。

FULL_RECORD_TYPE = "research_full_v1"
RESEARCH_FULL_SUFFIX = ".research-full.json"
FULL_KEYS = ("record_type", "query_id", "question_text", "created_at",
             "research_as_of", "snapshot_id", "digest_snapshot", "status",
             "answer_text", "values", "unresolved", "glm", "warnings",
             "violations", "user_note", "follow_up_of", "saved_at")


def _research_full_path(collection_dir, query_id):
    return os.path.join(str(collection_dir), f"{query_id}{RESEARCH_FULL_SUFFIX}")


def validate_research_full(payload):
    """sidecar 记录校验;返回 issues 列表(空=合法)。answer 相关字段允许 None
    (独立保存场景),但键必须齐(schema 明示,null≠缺席)。"""
    issues = []
    if not isinstance(payload, dict):
        return [f"payload须为dict: {type(payload).__name__}"]
    for k in FULL_KEYS:
        if k not in payload:
            issues.append(f"sidecar缺字段{k}(research_full_v1 schema)")
    if issues:
        return issues
    if payload.get("record_type") != FULL_RECORD_TYPE:
        issues.append(f"record_type恒须字面量{FULL_RECORD_TYPE!r}: "
                      f"{payload.get('record_type')!r}")
    qid = payload.get("query_id")
    if not isinstance(qid, str) or not qir.QUERY_ID_RE.match(qid or ""):
        issues.append(f"query_id格式非法(须QB-YYYYMMDD-NNN): {qid!r}")
    for k in ("question_text",):
        v = payload.get(k)
        if not isinstance(v, str) or not v:
            issues.append(f"{k}须为非空string: {v!r}")
    for k in ("created_at", "saved_at"):
        v = payload.get(k)
        if not isinstance(v, str) or not qir.ISO_DATE_PREFIX_RE.match((v or "")[:10]):
            issues.append(f"{k}须为ISO8601字符串: {v!r}")
    if parse_snapshot_id(payload.get("snapshot_id")) is None:
        issues.append(f"snapshot_id非规范: {payload.get('snapshot_id')!r}")
    dg = payload.get("digest_snapshot")
    if not isinstance(dg, str) or not DIGEST_RE.match(dg or ""):
        issues.append(f"digest_snapshot格式非法(须R5十六位小写指纹): {dg!r}")
    for k in ("values", "glm"):
        v = payload.get(k)
        if v is not None and not isinstance(v, dict):
            issues.append(f"{k}须为dict|null: {type(v).__name__}")
    # unresolved=作答相关(独立保存场景 null 如实);warnings/violations=进程自产恒为list
    v = payload.get("unresolved")
    if v is not None and not isinstance(v, list):
        issues.append(f"unresolved须为list|null: {type(v).__name__}")
    for k in ("warnings", "violations"):
        v = payload.get(k)
        if not isinstance(v, list):
            issues.append(f"{k}须为list(可空,不可null缺席): {type(v).__name__}")
    fu = payload.get("follow_up_of")
    if fu is not None and (not isinstance(fu, str)
                           or not qir.QUERY_ID_RE.match(fu or "")):
        issues.append(f"follow_up_of须为null|QB-YYYYMMDD-NNN: {fu!r}")
    return issues


def write_research_full(collection_dir, payload):
    """research_full sidecar 落盘(append-only: 已存在一律拒写,与 base 同纪律)。

    返回 (status, path): written | rejected-duplicate-query-id。
    schema 违规=ValueError fail-loud。answer 相关字段(status/answer_text/
    values/unresolved/glm)允许 None(archive save 独立保存场景)。
    """
    issues = validate_research_full(payload)
    if issues:
        raise ValueError("research_full sidecar未过schema校验(fail-loud): "
                         + ";".join(issues))
    collection = str(collection_dir)
    path = _research_full_path(collection, payload["query_id"])
    if os.path.exists(path):
        return STATUS_REJECTED_DUPLICATE, path
    os.makedirs(collection, exist_ok=True)
    _tmp = path + '.tmp'
    with open(_tmp, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=1, sort_keys=True)
    os.replace(_tmp, path)
    return STATUS_WRITTEN, path


def load_research_full(query_id, archive_dir=None):
    """读回 sidecar;缺失返回 None(旧档案无 sidecar 属正常,不报错)。"""
    if not isinstance(query_id, str) or not qir.QUERY_ID_RE.match(query_id or ""):
        raise ValueError(f"query_id格式非法: {query_id!r}")
    path = _research_full_path(_collection_dir(archive_dir or DEFAULT_ARCHIVE_DIR),
                               query_id)
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def verify_query_record(record, snapshot_dir, archive_dir=None):
    """单记录验证: 记录级校验+快照解析+R5 digest 复算对照;→ (ok, issues)。"""
    if isinstance(record, str):
        record = load_query_record(record, archive_dir=archive_dir)
    issues = validate_query_record(record)
    if issues:
        return False, issues
    snap, load_err = _load_snapshot_for_binding(record["snapshot_id"], snapshot_dir)
    if snap is None:
        return False, [load_err]
    actual = rp.digest_snapshot(snap)                              # R5 复算
    if actual != record["digest_snapshot"]:
        return False, [f"digest不匹配(快照内容与档案绑定漂移/篡改嫌疑,snapshot_id="
                       f"{record['snapshot_id']}): 档案登记{record['digest_snapshot']}"
                       f" vs 实测{actual}"]
    return True, []


def verify_archive(archive_dir, snapshot_dir):
    """全档案逐档复核;→ {n_records, n_ok, failures:[{query_id, issues}]}。"""
    qids = list_query_records(archive_dir)
    n_ok = 0
    failures = []
    for qid in qids:
        try:
            rec = load_query_record(qid, archive_dir=archive_dir)
        except Exception as e:
            failures.append({"query_id": qid, "issues": [f"档案文件不可读: {e}"]})
            continue
        ok, issues = verify_query_record(rec, snapshot_dir, archive_dir=archive_dir)
        if ok:
            n_ok += 1
        else:
            failures.append({"query_id": qid, "issues": issues})
    return {"n_records": len(qids), "n_ok": n_ok, "failures": failures}
