#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P03-E2EB-WP-B1: 模式B查询中间表示(IR)定义与字段级schema校验(纯离线)。

DESIGN docs/P03_E2EB_DESIGN.md §三(a) IR schema 的确定性落地(行号=并入后工作树实读):
- 五结构: StructuredResearchQuery / MetricBinding / Provenance / DerivedOperation /
  UnresolvedEntity(DESIGN L56-106);
- validate_ir(ir, stage) 字段级校验: 枚举/ID格式/必填/跨引用/阶段规则,返回issues
  字符串列表(空列表=合法),不抛出校验异常(调用方决定fail-loud方式);
- 阶段规则(登记型决策点D-B1-01,REPORT §六):
  * stage="mapped"(本包B1映射器产出): 绑定status合法值=ABSENT族+PENDING_EXECUTION
    哨兵;RESOLVED禁止(映射器不取数,DESIGN L212「不含执行器」;伪造provenance=
    违反接地红线L113);派生status合法值={NO_DATA, PENDING_EXECUTION};
    COMPUTED禁止(数值计算属WP-B2,D2);
  * stage="executed"(WP-B2执行器产出): PENDING_EXECUTION零出现;
    RESOLVED→provenance必填(DESIGN L78);COMPUTED→result必为数值且
    calculation_ref必填(DESIGN L98-99);
  * 两阶段共通: ABSENT_*→absence_reason必填+provenance=None(DESIGN L77);
    NO_DATA→result=None(L97-98,L129不部分计算);operands必须引用在场binding_id
    (L94「binding_id 引用列表」);ABSENT_REGISTRY→metric_id=None(查无身份,
    无注册表身份可引用);ABSENT_SOURCE/DATA/WINDOW→metric_id非None(已注册才有
    通道/数据/窗口可言);
- 零网络/纯标准库;不读任何数据档(禁直读原始采集档目录,DESIGN §七1;本模块
  无任何文件IO);一切数值来源由调用方经快照/事实引擎转递(架构v2,D1)。

参数登记: docs/P03_E2EB_B1_REPORT.md §六 P-01..P-14(先登记后实现,运行后禁回改)。

IA-P1-WP-D 扩展(参数登记 docs/P1_WP_D_REPORT.md §零.6 PD-1/PD-2):
- ECONOMIES 枚举常量(US/CN/JP/EA/HK/GLOBAL,DESIGN §四 L133 候选);
- IR 顶层可选键 "economy"(经济体过滤维度;键缺席或 None=不过滤,键在场且非 None
  须枚举成员——向后兼容: 既有无 economy 键的 IR 形态保持合法);
  接地标识强制面(BINDING_KEYS/PROVENANCE_KEYS/RESOLVED→provenance 必填)对
  四经济体统一适用,结构零变更(PD-2 判定)。
"""
import re

# ══ 常量(DESIGN §三(a) 抄录;REPORT §六 P-01..P-14) ═══════════════════

MODE_B = "B"                                    # P-01(DESIGN L59)
ROLES = ("level", "derived_window", "spread_component", "correlation_series")   # P-02(L73)
WINDOWS = ("week", "mtd", "ytd", "m1", "m3", "m6", "m12")                        # P-03(L74)
FIELDS = ("value", "pct_change", "pp_change", "bp_change", "abs_change")         # P-04(L75)
BINDING_STATUS_TERMINAL = ("RESOLVED", "ABSENT_REGISTRY", "ABSENT_SOURCE",
                           "ABSENT_DATA", "ABSENT_WINDOW")                        # P-05(L76)
OP_TYPES = ("spread", "level_diff", "correlation")                               # P-09(L93)
OP_STATUS_TERMINAL = ("COMPUTED", "NO_DATA")                                     # P-10(L97)
MAPPING_STATUS = ("no_registry_identity", "ambiguous", "out_of_scope")           # P-11(L104)
QUALITY_STATUS = ("PASS", "DEGRADED", "WARN", "FAIL")                            # P-08(L87)
ANSWER_CONSTRAINTS = {"grounding_required": True,
                      "no_data_policy": "report_absence"}                        # P-12(L66-67)
ABSENCE_LEVELS = {"A1": "ABSENT_REGISTRY", "A2": "ABSENT_SOURCE",               # §三(c) L122-127
                  "A3": "ABSENT_DATA", "A4": "ABSENT_WINDOW"}
ECONOMIES = ("US", "CN", "JP", "EA", "HK", "GLOBAL")   # P1 WP-D PD-1(DESIGN §四 L133 候选enum)
PENDING_EXECUTION = "PENDING_EXECUTION"   # D-B1-01 生命周期哨兵(映射期词汇,终态枚举不动)
BINDING_STATUS_MAPPED = (PENDING_EXECUTION, "ABSENT_REGISTRY", "ABSENT_SOURCE",
                         "ABSENT_DATA", "ABSENT_WINDOW")
OP_STATUS_MAPPED = (PENDING_EXECUTION, "NO_DATA")

QUERY_ID_RE = re.compile(r"^QB-\d{8}-\d{3}$")            # P-13(L57,L183)
BINDING_ID_RE = re.compile(r"^MB-\d+$")                  # P-13(L71)
OP_ID_RE = re.compile(r"^OP-\d+$")                       # P-13(L92)
FACT_ID_RE = re.compile(r"^[A-Za-z0-9_]+@\d{4}-\d{2}-\d{2}$")   # P-13(L84)
SNAPSHOT_ID_RE = re.compile(r"^research_snapshot_\d{8}(_v\d+)?$")  # P-13(L62,L182)
ISO_DATE_PREFIX_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")
AS_OF_RE = re.compile(r"^\d{4}-\d{2}-\d{2}([T ].*)?$")    # L61 ISO日期或时间戳

IR_KEYS = ("query_id", "created_at", "mode", "question_text", "as_of",
           "target_snapshot_id", "metric_bindings", "derived_operations",
           "unresolved_entities", "answer_constraints")
BINDING_KEYS = ("binding_id", "metric_id", "role", "window", "field",
                "status", "absence_reason", "provenance")
PROVENANCE_KEYS = ("metric_id", "snapshot_id", "fact_id", "observation_date",
                   "source_file", "quality_status", "calculation_ref")
OP_KEYS = ("op_id", "op_type", "operands", "formula", "unit", "status",
           "result", "calculation_ref")
UNRESOLVED_KEYS = ("mention", "mapping_status", "note")


def make_query_id(created_at, seq=1):
    """由受理时刻(ISO8601,UTC+8)与同日序号生成 query_id(D-B1-10)。

    格式 QB-YYYYMMDD-NNN(DESIGN L57);同日唯一性计数与落盘属 WP-B4 档案,
    本模块仅做确定性拼接与格式校验。
    """
    if not isinstance(created_at, str) or not ISO_DATE_PREFIX_RE.match(created_at[:10]):
        raise ValueError(f"created_at须为ISO8601字符串: {created_at!r}")
    if not isinstance(seq, int) or isinstance(seq, bool) or seq < 1:
        raise ValueError(f"seq须为≥1整数: {seq!r}")
    ymd = created_at[:10].replace("-", "")
    qid = f"QB-{ymd}-{seq:03d}"
    if not QUERY_ID_RE.match(qid):
        raise ValueError(f"query_id生成失败: {qid!r}")
    return qid


def _is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


# ══ 字段级schema校验 ═══════════════════════════════════════════════════

def _validate_provenance(prov, binding, issues, prefix):
    if not isinstance(prov, dict):
        issues.append(f"{prefix}.provenance须为dict: {type(prov).__name__}")
        return
    for k in PROVENANCE_KEYS:
        if k not in prov:
            issues.append(f"{prefix}.provenance缺字段{k}(DESIGN L81-89)")
    if prov.get("metric_id") != binding.get("metric_id"):
        issues.append(f"{prefix}.provenance.metric_id({prov.get('metric_id')!r})"
                      f"须与binding.metric_id一致(DESIGN L82)")
    if not isinstance(prov.get("snapshot_id"), str) or \
            not SNAPSHOT_ID_RE.match(prov.get("snapshot_id") or ""):
        issues.append(f"{prefix}.provenance.snapshot_id格式非法"
                      f"(须research_snapshot_YYYYMMDD[_vN],DESIGN L83/L182): "
                      f"{prov.get('snapshot_id')!r}")
    if not isinstance(prov.get("fact_id"), str) or \
            not FACT_ID_RE.match(prov.get("fact_id") or ""):
        issues.append(f"{prefix}.provenance.fact_id格式非法"
                      f"(须metric_id@YYYY-MM-DD,DESIGN L84): {prov.get('fact_id')!r}")
    if not ISO_DATE_PREFIX_RE.match(str(prov.get("observation_date") or "")):
        issues.append(f"{prefix}.provenance.observation_date须为ISO日期"
                      f"(DESIGN L85): {prov.get('observation_date')!r}")
    if not isinstance(prov.get("source_file"), str) or not prov.get("source_file"):
        issues.append(f"{prefix}.provenance.source_file须为非空字符串(DESIGN L86)")
    if prov.get("quality_status") not in QUALITY_STATUS:
        issues.append(f"{prefix}.provenance.quality_status枚举外值"
                      f"(合法{QUALITY_STATUS},DESIGN L87): {prov.get('quality_status')!r}")
    cr = prov.get("calculation_ref")
    if cr is not None and not isinstance(cr, str):
        issues.append(f"{prefix}.provenance.calculation_ref须为string|null(DESIGN L88)")


def _validate_binding(b, i, stage, seen_ids, binding_ids, issues):
    prefix = f"metric_bindings[{i}]({b.get('binding_id') if isinstance(b, dict) else '?'})"
    if not isinstance(b, dict):
        issues.append(f"{prefix}须为dict")
        return
    for k in BINDING_KEYS:
        if k not in b:
            issues.append(f"{prefix}缺字段{k}(DESIGN L70-79)")
    bid = b.get("binding_id")
    if not isinstance(bid, str) or not BINDING_ID_RE.match(bid or ""):
        issues.append(f"{prefix}.binding_id格式非法(须MB-N,DESIGN L71): {bid!r}")
    elif bid in seen_ids:
        issues.append(f"{prefix}.binding_id重复: {bid}")
    seen_ids.add(bid)
    mid = b.get("metric_id")
    if mid is not None and (not isinstance(mid, str) or not mid):
        issues.append(f"{prefix}.metric_id须为非空string|null: {mid!r}")
    role = b.get("role")
    if role not in ROLES:
        issues.append(f"{prefix}.role枚举外值(合法{ROLES},DESIGN L73): {role!r}")
    window = b.get("window")
    if window is not None and window not in WINDOWS:
        issues.append(f"{prefix}.window枚举外值(合法{WINDOWS},DESIGN L74): {window!r}")
    if role == "derived_window" and window is None:
        issues.append(f"{prefix}.role=derived_window时window必填(DESIGN L74)")
    if role is not None and role != "derived_window" and window is not None:
        issues.append(f"{prefix}.window仅derived_window可携(DESIGN L74): window={window!r}")
    if b.get("field") not in FIELDS:
        issues.append(f"{prefix}.field枚举外值(合法{FIELDS},DESIGN L75): {b.get('field')!r}")
    status = b.get("status")
    allowed = BINDING_STATUS_MAPPED if stage == "mapped" else BINDING_STATUS_TERMINAL
    if status not in allowed:
        issues.append(f"{prefix}.status非法于stage={stage}(合法{allowed},DESIGN L76+D-B1-01): {status!r}")
        return
    ar = b.get("absence_reason")
    prov = b.get("provenance")
    if status is not None and status.startswith("ABSENT"):
        if not isinstance(ar, str) or not ar:
            issues.append(f"{prefix}.status={status}须absence_reason非空(DESIGN L77)")
        if prov is not None:
            issues.append(f"{prefix}.status={status}时provenance须为None: {prov!r}")
        if status == "ABSENT_REGISTRY" and mid is not None:
            issues.append(f"{prefix}.ABSENT_REGISTRY→metric_id须None(查无身份,D-B1-04): {mid!r}")
        if status in ("ABSENT_SOURCE", "ABSENT_DATA", "ABSENT_WINDOW") and mid is None:
            issues.append(f"{prefix}.{status}→metric_id须非None(已注册指标才谈通道/数据/窗口)")
    if status == PENDING_EXECUTION and prov is not None:
        issues.append(f"{prefix}.PENDING_EXECUTION时provenance须为None(未取数,D-B1-01)")
    if status == "RESOLVED":
        if prov is None:
            issues.append(f"{prefix}.status=RESOLVED时provenance必填(DESIGN L78)")
        else:
            _validate_provenance(prov, b, issues, prefix)
    if mid is None and status is not None and not status.startswith("ABSENT"):
        issues.append(f"{prefix}.metric_id=None仅ABSENT族合法(当前status={status!r})")


def _validate_op(op, i, stage, binding_ids, seen_ops, issues):
    prefix = f"derived_operations[{i}]({op.get('op_id') if isinstance(op, dict) else '?'})"
    if not isinstance(op, dict):
        issues.append(f"{prefix}须为dict")
        return
    for k in OP_KEYS:
        if k not in op:
            issues.append(f"{prefix}缺字段{k}(DESIGN L91-100)")
    oid = op.get("op_id")
    if not isinstance(oid, str) or not OP_ID_RE.match(oid or ""):
        issues.append(f"{prefix}.op_id格式非法(须OP-N,DESIGN L92): {oid!r}")
    elif oid in seen_ops:
        issues.append(f"{prefix}.op_id重复: {oid}")
    seen_ops.add(oid)
    if op.get("op_type") not in OP_TYPES:
        issues.append(f"{prefix}.op_type枚举外值(合法{OP_TYPES},DESIGN L93): {op.get('op_type')!r}")
    operands = op.get("operands")
    if not isinstance(operands, list) or not operands or \
            not all(isinstance(o, str) and o for o in operands):
        issues.append(f"{prefix}.operands须为非空string列表(DESIGN L94)")
    else:
        for ref in operands:
            if ref not in binding_ids:
                issues.append(f"{prefix}.operands引用不存在的binding_id: {ref}")
        if op.get("op_type") == "spread" and len(operands) < 2:
            issues.append(f"{prefix}.spread须≥2 operands(两水平求差,DESIGN L93)")
        if op.get("op_type") == "correlation" and len(operands) != 2:
            issues.append(f"{prefix}.correlation须恰2 operands(两序列相关,DESIGN L93)")
    if not isinstance(op.get("formula"), str) or not op.get("formula"):
        issues.append(f"{prefix}.formula须为非空string(DESIGN L95)")
    if not isinstance(op.get("unit"), str) or not op.get("unit"):
        issues.append(f"{prefix}.unit须为非空string(DESIGN L96)")
    status = op.get("status")
    allowed = OP_STATUS_MAPPED if stage == "mapped" else OP_STATUS_TERMINAL
    if status not in allowed:
        issues.append(f"{prefix}.status非法于stage={stage}(合法{allowed},DESIGN L97+D-B1-01): {status!r}")
        return
    result = op.get("result")
    if status == "NO_DATA" and result is not None:
        issues.append(f"{prefix}.NO_DATA→result须None(不部分计算,DESIGN L97-98/L129): {result!r}")
    if status == PENDING_EXECUTION and result is not None:
        issues.append(f"{prefix}.PENDING_EXECUTION→result须None(未计算,D-B1-01)")
    if status == "COMPUTED":
        if not _is_number(result):
            issues.append(f"{prefix}.COMPUTED→result须为数值(DESIGN L98): {result!r}")
        if not isinstance(op.get("calculation_ref"), str) or not op.get("calculation_ref"):
            issues.append(f"{prefix}.COMPUTED→calculation_ref必填(DESIGN L99/L114)")


def _validate_unresolved(u, i, issues):
    prefix = f"unresolved_entities[{i}]"
    if not isinstance(u, dict):
        issues.append(f"{prefix}须为dict")
        return
    for k in UNRESOLVED_KEYS:
        if k not in u:
            issues.append(f"{prefix}缺字段{k}(DESIGN L102-106)")
    if not isinstance(u.get("mention"), str) or not u.get("mention"):
        issues.append(f"{prefix}.mention须为非空string(DESIGN L103)")
    if u.get("mapping_status") not in MAPPING_STATUS:
        issues.append(f"{prefix}.mapping_status枚举外值(合法{MAPPING_STATUS},DESIGN L104): "
                      f"{u.get('mapping_status')!r}")
    if not isinstance(u.get("note"), str) or not u.get("note"):
        issues.append(f"{prefix}.note须为非空string(DESIGN L105)")


def validate_ir(ir, stage="mapped"):
    """字段级schema校验(DESIGN §三(a));返回issues列表,空列表=合法。

    stage: "mapped"=B1映射器产出(D-B1-01哨兵合法,RESOLVED/COMPUTED禁止);
           "executed"=WP-B2执行器产出(DESIGN终态枚举,哨兵零出现)。
    """
    issues = []
    if stage not in ("mapped", "executed"):
        raise ValueError(f"stage须为mapped|executed: {stage!r}")
    if not isinstance(ir, dict):
        return ["IR须为dict"]
    for k in IR_KEYS:
        if k not in ir:
            issues.append(f"IR缺顶层字段{k}(DESIGN L56-68)")
    if not isinstance(ir.get("query_id"), str) or \
            not QUERY_ID_RE.match(ir.get("query_id") or ""):
        issues.append(f"query_id格式非法(须QB-YYYYMMDD-NNN,DESIGN L57/L183): {ir.get('query_id')!r}")
    ca = ir.get("created_at")
    if not isinstance(ca, str) or not ISO_DATE_PREFIX_RE.match((ca or "")[:10]):
        issues.append(f"created_at须为ISO8601时间戳字符串(UTC+8,DESIGN L58): {ca!r}")
    if ir.get("mode") != MODE_B:
        issues.append(f"mode恒须字面量{MODE_B!r}(DESIGN L59): {ir.get('mode')!r}")
    if not isinstance(ir.get("question_text"), str) or not ir.get("question_text"):
        issues.append("question_text须为非空string(用户原始问题原样保留,DESIGN L60)")
    as_of = ir.get("as_of")
    if as_of is not None and (not isinstance(as_of, str) or not AS_OF_RE.match(as_of)):
        issues.append(f"as_of须为ISO日期/时间戳字符串或None(DESIGN L61): {as_of!r}")
    tsi = ir.get("target_snapshot_id")
    if tsi is not None and (not isinstance(tsi, str) or not SNAPSHOT_ID_RE.match(tsi)):
        issues.append(f"target_snapshot_id格式非法(DESIGN L62): {tsi!r}")
    econ = ir.get("economy")                    # P1 WP-D PD-2: 可选经济体过滤维度键
    if econ is not None and econ not in ECONOMIES:
        issues.append(f"economy须为{ECONOMIES}|None(经济体过滤维度,DESIGN §四 L133,"
                      f"缺席/None=不过滤): {econ!r}")
    if ir.get("answer_constraints") != ANSWER_CONSTRAINTS:
        issues.append(f"answer_constraints恒等值{{'grounding_required': True, "
                      f"'no_data_policy': 'report_absence'}}(DESIGN L66-67): "
                      f"{ir.get('answer_constraints')!r}")
    if not isinstance(ir.get("metric_bindings"), list):
        issues.append("metric_bindings须为list(DESIGN L63)")
        binding_ids = set()
    else:
        seen = set()
        binding_ids = set()
        for i, b in enumerate(ir["metric_bindings"]):
            before = len(issues)
            _validate_binding(b, i, stage, seen, binding_ids, issues)
            if len(issues) == before and isinstance(b, dict):
                binding_ids.add(b.get("binding_id"))
    if not isinstance(ir.get("derived_operations"), list):
        issues.append("derived_operations须为list(DESIGN L64)")
    else:
        seen_ops = set()
        for i, op in enumerate(ir["derived_operations"]):
            _validate_op(op, i, stage, binding_ids, seen_ops, issues)
    if not isinstance(ir.get("unresolved_entities"), list):
        issues.append("unresolved_entities须为list(DESIGN L65)")
    else:
        for i, u in enumerate(ir["unresolved_entities"]):
            _validate_unresolved(u, i, issues)
    return issues
