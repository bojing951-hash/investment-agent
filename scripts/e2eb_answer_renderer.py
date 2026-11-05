#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P03-E2EB-WP-B5: 模式B回答渲染层(接地强制+缺席文本化+质量披露;纯离线零网络)。

DESIGN docs/P03_E2EB_DESIGN.md §六 WP-B5 行(L234-238)的确定性落地(行号=基线
工作树 ac01d072 实读):
- 接地强制(§三(b) L111-116): 进入回答的数值节点必携至少一种完整来源标识
  (L113 三形态);派生/计算值必附 calculation_ref(L114);**无来源标识的数值节点
  =渲染失败 fail-closed,零部分输出不降级为无源输出**(L115);quality_status
  非PASS事实进入回答必随附降级披露(L116,A4纪律);
- 缺席文本化(§三(c) L118-129): A1-A4 四级措辞逐字(L124-127),缺席行恒含
  「无数据」;派生 NO_DATA 不部分计算不近似(L129);
- 质量披露与禁投资建议文案守卫(§七3/L248「回答模板禁止投资建议措辞
  (实现于WP-B5渲染层)」): 守卫复用 B1 eqm.OUT_OF_SCOPE_PATTERNS(禁复制),
  命中→fail-closed;豁免行=unresolved(如实引用超界指称原文,B1 note 自身含
  「不构成投资建议」措辞)与 footer(标准免责声明行);
- 输入面=B2 execute_query 产出({ir,values,snapshot_id,gate_status} 或 refusal
  四键,e2eb_query_executor.py:279-283/358-359);渲染器不信任上游,接地校验
  独立复验(纵深防御,D-B5-02)。

纪律: 零文件IO/零网络/零墙钟(D-B5-12);依赖面恰2个项目模块=qir(B1)+
eqm(仅OUT_OF_SCOPE_PATTERNS复用);缺值如实缺席零填0(§三(c)/§七4);
本模块不取数(B2)、不映射(B1)、不写档案(B4)。

参数登记: docs/P03_E2EB_B5_REPORT.md §六 D-B5-01..D-B5-16(先登记后实现,
运行后禁回改)。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e2eb_query_ir as qir        # B1(复用禁复制: FACT_ID_RE/SNAPSHOT_ID_RE/ISO_DATE_PREFIX_RE/ANSWER_CONSTRAINTS)
import e2eb_query_mapper as eqm    # B1(复用禁复制: OUT_OF_SCOPE_PATTERNS,D-B1-07 词表)


class GroundingError(ValueError):
    """接地校验失败=渲染 fail-closed(D-B5-04,DESIGN L115;零部分输出)。"""


# ══ 接地标识三形态(D-B5-02,DESIGN L113) ═══════════════════════════════

FORM_FACT = "metric_id+fact_id"                    # 形态①(L113①)
FORM_SNAPSHOT_PATH = "snapshot_id+字段路径"         # 形态②(L113②)
FORM_SOURCE_DATE = "source_file+observation_date"  # 形态③(L113③)

FIELD_PATH_LEVEL = "facts[].value"                          # L113 例式
FIELD_PATH_WINDOW = "facts[].derived.{window}.{field}"


def _is_number(v):
    """D-B5-11: bool 非数值;字符串数字不算(qir._is_number 同语义)。"""
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _identifier_forms(provenance, field_path):
    """逐形态核验(D-B5-02);返回满足的形态列表(空=无源)。"""
    if not isinstance(provenance, dict):
        return []
    forms = []
    mid, fid = provenance.get("metric_id"), provenance.get("fact_id")
    if isinstance(mid, str) and mid and isinstance(fid, str) \
            and qir.FACT_ID_RE.match(fid):
        forms.append(FORM_FACT)
    sid = provenance.get("snapshot_id")
    if isinstance(sid, str) and qir.SNAPSHOT_ID_RE.match(sid) \
            and isinstance(field_path, str) and field_path:
        forms.append(FORM_SNAPSHOT_PATH)
    src, obs = provenance.get("source_file"), provenance.get("observation_date")
    if isinstance(src, str) and src and isinstance(obs, str) \
            and qir.ISO_DATE_PREFIX_RE.match(obs):
        forms.append(FORM_SOURCE_DATE)
    return forms


# ══ 数值节点接地校验(要点①机制面) ═════════════════════════════════════

def validate_value_node(node):
    """单数值节点接地校验(D-B5-02/04/11);返回 issues 列表(空=接地合法)。

    node: {binding_id, metric_id, value, provenance, field_path, window, field}
    """
    issues = []
    bid = node.get("binding_id")
    if not _is_number(node.get("value")):
        issues.append(f"{bid}: 数值节点value须为数值(bool/字符串不算,D-B5-11): "
                      f"{node.get('value')!r}")
        return issues
    forms = _identifier_forms(node.get("provenance"), node.get("field_path"))
    if not forms:
        issues.append(f"{bid}: 数值节点无任何完整来源标识(三形态全缺,DESIGN "
                      f"L113)——fail-closed不降级为无源输出(L115)")
    return issues


def validate_derived_node(node, operand_provenances):
    """派生数值节点接地校验(D-B5-03,DESIGN L114);返回 issues 列表。

    node: {op_id, value, unit, calculation_ref, operands}
    operand_provenances: [(binding_id, provenance, field_path), ...]
    """
    issues = []
    oid = node.get("op_id")
    if not _is_number(node.get("value")):
        issues.append(f"{oid}: 派生数值须为数值(D-B5-11): {node.get('value')!r}")
        return issues
    cr = node.get("calculation_ref")
    if not isinstance(cr, str) or not cr:
        issues.append(f"{oid}: 派生/计算值必附非空calculation_ref(DESIGN L114)")
    for bid, prov, fpath in operand_provenances:
        if not _identifier_forms(prov, fpath):
            issues.append(f"{oid}: operand {bid} provenance 无任何完整来源标识"
                          f"(输入观测链断裂,DESIGN L113-114)")
    return issues


# ══ 禁投资建议守卫(D-B5-08,DESIGN §七3/L248) ═════════════════════════

GUARD_EXEMPT_KINDS = ("unresolved", "footer")   # 豁免行登记(D-B5-08)


def assert_no_advice(lines_with_kind):
    """守卫: 数值/派生/缺席/头部行命中禁语词表→GroundingError fail-closed。

    lines_with_kind: [(kind, text), ...];豁免 kind=GUARD_EXEMPT_KINDS
    (unresolved=如实引用超界指称原文;footer=标准免责声明,其自身含
    「不构成投资建议」措辞——B1 NOTE_OUT_OF_SCOPE 同款语义)。
    词表复用 eqm.OUT_OF_SCOPE_PATTERNS(B1 D-B1-07,禁复制)。
    """
    for kind, text in lines_with_kind:
        if kind in GUARD_EXEMPT_KINDS:
            continue
        for pat in eqm.OUT_OF_SCOPE_PATTERNS:
            if pat in text:
                raise GroundingError(
                    f"回答行命中禁投资建议词表(DESIGN §七3/L248,fail-closed): "
                    f"行[{kind}]含词表词{pat!r}: {text!r}")


# ══ 缺席文本化(D-B5-06/07,DESIGN §三(c) L124-129) ═══════════════════

ABSENCE_PHRASES = {
    "ABSENT_REGISTRY": "该指标不在注册表(无身份定义),无法取数",   # A1(L124)
    "ABSENT_SOURCE": "指标已注册但当日采集缺失",                   # A2(L125)
    "ABSENT_DATA": "本期无该指标事实",                             # A3(L126)
    # A4(L127): absence_reason 原样转述——非模板词(见 _absent_line)
}
NO_DATA_MARK = "无数据"                                          # L129 显式声明
NO_DATA_PHRASE = "不可计算(NO_DATA,operand缺席不部分计算)"        # D-B5-07

QUALITY_DISCLOSURE = " | 质量披露: {status}(非PASS降级披露,A4纪律)"  # D-B5-05(L116)
WINDOW_CALC_SUFFIX = " 口径: {calculation_ref}"                    # D-B5-10
FOOTER_TEMPLATE = ("缺席摘要: 无数据{n_absent}项/不可计算{n_nodata}项;"
                   "缺席如实登记,不以相近指标冒充、不内插、不填0(§三(c))。"
                   "本回答为接地研究信息,不构成投资建议(§七3)。")   # D-B5-10
HEADER_TEMPLATE = ("【接地作答|模式B】query_id={qid};研究截止as_of={as_of};"
                   "快照={snapshot_id};门禁={gate_status}")         # D-B5-10
REFUSAL_TEMPLATE = "无法作答: {refusal}"                           # D-B5-09


def _absent_line(binding):
    """缺席行(D-B5-06/10): A1/A2/A3 模板词+A4 原样转述;恒含「无数据」。"""
    bid, status = binding["binding_id"], binding["status"]
    reason = binding.get("absence_reason") or ""
    if status == "ABSENT_WINDOW":                                  # A4: 引擎reason原样
        return f"{bid}: {NO_DATA_MARK}——{reason}(引擎原因原样转述)"
    phrase = ABSENCE_PHRASES[status]
    return f"{bid}: {NO_DATA_MARK}——{phrase}(登记: {reason})"


def _value_line(binding, value):
    """数值行(D-B5-05/10): 值+三标识内联+窗口口径+质量披露。"""
    bid, prov = binding["binding_id"], binding["provenance"]
    window_part = ""
    calc_suffix = ""
    if binding.get("role") == "derived_window":
        window_part = f"[{binding.get('window')}.{binding.get('field')}]"
        if isinstance(prov.get("calculation_ref"), str) and prov["calculation_ref"]:
            calc_suffix = WINDOW_CALC_SUFFIX.format(
                calculation_ref=prov["calculation_ref"])
    line = (f"{bid} {binding.get('metric_id')}{window_part} = {value}"
            f" @{prov.get('observation_date')}(fact {prov.get('fact_id')};"
            f"源 {prov.get('source_file')};快照 {prov.get('snapshot_id')})"
            f"{calc_suffix}")
    if prov.get("quality_status") != "PASS":                       # D-B5-05(L116)
        line += QUALITY_DISCLOSURE.format(status=prov.get("quality_status"))
    return line


# ══ 渲染主入口(要点②;输入面=B2产出) ═════════════════════════════════

def _field_path_of(binding):
    """形态②字段路径(D-B5-02,L113 例式)。"""
    if binding.get("role") == "derived_window":
        return FIELD_PATH_WINDOW.format(window=binding.get("window"),
                                        field=binding.get("field"))
    return FIELD_PATH_LEVEL


def render_answer(execution):
    """B2 执行产出 → 接地作答(D-B5-01..16;fail-closed)。

    参数:
      execution: e2eb_query_executor.execute_query 产出——executed 结果
        {"ir", "values", "snapshot_id", "gate_status"} 或 refusal 四键
        (D-B2-03;e2eb_query_executor.py:70-73/358-359)。

    返回: {"kind": "grounded"|"refusal", "answer_text", "lines",
           "value_nodes", "absent", "no_data", "n_grounded_values",
           "quality_disclosures", "gate_status", "snapshot_id"}。

    抛出: GroundingError——任一数值节点无完整来源标识/派生缺calculation_ref/
    回答行命中禁语词表(DESIGN L115 fail-closed,零部分输出)。
    """
    if not isinstance(execution, dict) or "ir" not in execution:
        raise ValueError("execution须为B2 execute_query产出(携ir键,D-B5-01)")
    ir = execution["ir"]
    if not isinstance(ir, dict):
        raise ValueError("execution.ir须为dict")
    if ir.get("answer_constraints", {}).get("grounding_required") is not True:
        raise GroundingError("answer_constraints.grounding_required须为True"
                             "(渲染层防御断言,DESIGN L66/L115)")
    gate_status = execution.get("gate_status")
    snapshot_id = execution.get("snapshot_id")

    if execution.get("refusal") is not None:                       # D-B5-09
        lines_k = [("header", HEADER_TEMPLATE.format(
            qid=ir.get("query_id"), as_of=ir.get("as_of"),
            snapshot_id=snapshot_id, gate_status=gate_status))]
        lines_k.append(("refusal", REFUSAL_TEMPLATE.format(
            refusal=execution["refusal"])))
        lines_k.append(("footer", FOOTER_TEMPLATE.format(n_absent=0, n_nodata=0)))
        assert_no_advice(lines_k)                                  # 守卫照常
        lines = [t for _, t in lines_k]
        return {"kind": "refusal", "answer_text": "\n".join(lines),
                "lines": lines, "value_nodes": [], "absent": [],
                "no_data": [], "n_grounded_values": 0,
                "quality_disclosures": [], "gate_status": gate_status,
                "snapshot_id": snapshot_id}

    values = execution.get("values") or {}
    issues_all = []
    value_nodes, quality_disclosures, absent = [], [], []
    lines_k = [("header", HEADER_TEMPLATE.format(
        qid=ir.get("query_id"), as_of=ir.get("as_of"),
        snapshot_id=snapshot_id, gate_status=gate_status))]

    # ── 绑定行: RESOLVED→数值节点接地校验;ABSENT→缺席文本化 ──
    for b in ir.get("metric_bindings", []):
        if b.get("status") == "RESOLVED":
            value = values.get(b["binding_id"])
            node = {"binding_id": b["binding_id"],
                    "metric_id": b.get("metric_id"), "value": value,
                    "provenance": b.get("provenance"),
                    "field_path": _field_path_of(b),
                    "window": b.get("window"), "field": b.get("field")}
            issues = validate_value_node(node)
            issues_all.extend(issues)
            if not issues:
                value_nodes.append(node)
                prov = b["provenance"]
                if prov.get("quality_status") != "PASS":
                    quality_disclosures.append(
                        f"{b['binding_id']}: {prov.get('quality_status')}")
                lines_k.append(("value", _value_line(b, value)))
        elif str(b.get("status", "")).startswith("ABSENT"):
            absent.append({"binding_id": b["binding_id"],
                           "status": b["status"],
                           "reason": b.get("absence_reason")})
            lines_k.append(("absent", _absent_line(b)))

    # ── 派生行: COMPUTED→派生节点接地校验;NO_DATA→NO_DATA措辞 ──
    bindings_by_id = {b["binding_id"]: b for b in ir.get("metric_bindings", [])}
    no_data = []
    for op in ir.get("derived_operations", []):
        if op.get("status") == "COMPUTED":
            operand_provs = []
            for ref in op.get("operands", []):
                ob = bindings_by_id.get(ref)
                operand_provs.append((ref, (ob or {}).get("provenance"),
                                      _field_path_of(ob) if ob else None))
            issues = validate_derived_node(
                {"op_id": op["op_id"], "value": op.get("result"),
                 "unit": op.get("unit"),
                 "calculation_ref": op.get("calculation_ref"),
                 "operands": op.get("operands")}, operand_provs)
            issues_all.extend(issues)
            if not issues:
                lines_k.append(("derived",
                                f"{op['op_id']} {op['formula']} = "
                                f"{op['result']} {op['unit']}"
                                f"({op['calculation_ref']})"))
        elif op.get("status") == "NO_DATA":
            no_data.append({"op_id": op["op_id"], "formula": op.get("formula")})
            lines_k.append(("no_data", f"{op['op_id']} {op['formula']}: "
                                       f"{NO_DATA_PHRASE}"))

    if issues_all:                                                 # D-B5-04
        raise GroundingError("渲染fail-closed(无源数值/接地链断裂,DESIGN L115): "
                             ";" + ";".join(issues_all))

    # ── 未解析行(如实上浮;守卫豁免kind=unresolved,D-B5-08) ──
    for u in ir.get("unresolved_entities", []):
        lines_k.append(("unresolved",
                        f"未解析指称: 「{u['mention']}」"
                        f"({u['mapping_status']}): {u['note']}"))

    lines_k.append(("footer", FOOTER_TEMPLATE.format(n_absent=len(absent),
                                                     n_nodata=len(no_data))))
    assert_no_advice(lines_k)                                      # D-B5-08 守卫
    lines = [t for _, t in lines_k]
    return {"kind": "grounded", "answer_text": "\n".join(lines),
            "lines": lines, "value_nodes": value_nodes, "absent": absent,
            "no_data": no_data, "n_grounded_values": len(value_nodes),
            "quality_disclosures": quality_disclosures,
            "gate_status": gate_status, "snapshot_id": snapshot_id}
