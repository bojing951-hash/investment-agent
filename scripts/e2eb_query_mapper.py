#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P03-E2EB-WP-B1: NL→IR v1映射器(约束式: 词表+注册表检索;纯离线零网络)。

DESIGN §三 映射层职责(L109实读): 词法/实体识别→候选指标检索(注册表
display_name/calc/别名,经E2)→窗口与字段解析(对齐E3口径词表)→绑定或如实登记
unresolved_entities;**只产IR不取数**——一切数值由执行器(WP-B2)从快照/引擎取得
(D2,DESIGN L109)。缺席四级(DESIGN §三(c))中仅A1(ABSENT_REGISTRY)在本层发现
(E2查无身份,L124);A2-A4与RESOLVED属执行器阶段。绑定/派生的映射期状态=
PENDING_EXECUTION哨兵(登记型决策点D-B1-01,REPORT §六;终态枚举不动)。

数据接入面: 仅注册表只读——缺省经 fact_engine.load_registry()(E1)取 by_id 索引,
与 E2 `metric()` 同构(fact_engine.py:75-76实读;DESIGN L213「注册表只读接口E2既有」);
registry 参数=依赖注入面(测试合成fixture唯一数据源,D-B1-11)。
禁直读任何原始采集档(DESIGN §七1;本模块无采集档路径/文件IO);
零网络/零模型调用/零凭证(DESIGN §七3-4;out_of_scope拦截词表=D-B1-07)。

参数与决策点全部先登记后运行: docs/P03_E2EB_B1_REPORT.md §六
(D-B1-01..D-B1-13;运行后禁回改)。
"""
import os
import re
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fact_engine as fe                                  # 既有依赖(E1/E4/E3常量)
import e2eb_query_ir as qir                               # 本包IR定义模块

TZ_BJ = timezone(timedelta(hours=8))                      # DESIGN L58(UTC+8)

# ══ 登记词表(REPORT §六;运行后禁回改) ═══════════════════════════════

# D-B1-07: 禁交易/仓位管理/收益承诺类拦截词表(DESIGN §七3)
OUT_OF_SCOPE_PATTERNS = (
    "买入", "卖出", "做多", "做空", "开仓", "平仓", "加仓", "减仓", "仓位",
    "应该买", "该不该买", "能保证", "稳赚", "保证收益", "投资建议",
    "抄底", "逃顶", "止损", "止盈", "杠杆", "赚钱",
)
NOTE_OUT_OF_SCOPE = ("禁交易/仓位管理/收益承诺类指称(out_of_scope);"
                     "本入口仅提供接地研究信息,不构成投资建议(DESIGN §七3红线)")
NOTE_NO_IDENTITY = ("指称未能在注册表检索到身份(v1约束式词表);"
                    "如实上浮,不猜映射(DESIGN §三(a) UnresolvedEntity)")

# D-B1-08: 显式as_of检测(E4严格校验;非法→不设,不猜映射)
AS_OF_CUE_RE = re.compile(r"(?:截至|截止于|截止到|截止|as of)[\s]*"
                          r"(\d{4}-\d{2}-\d{2})", re.IGNORECASE)

# D-B1-02/C: USDJPY 趋势cue(在场→附加week+ytd窗口绑定,对齐DESIGN L138/L151)
TREND_CUE_RE = re.compile(r"最近|走势|表现|怎么样|涨|跌")

# D-B1-09: 剩余指称上浮的指称类后缀(前缀≤8字符)
METRICISH_RE = re.compile(r"[\u4e00-\u9fa5A-Za-z0-9_]{0,8}"
                          r"(?:收益率|利率|利差|指数|汇率|期货|CPI|GDP)")

# IA-P1-WP-D PD-3: NL经济体指称识别词表(DESIGN §四 L133;子串匹配,与
# OUT_OF_SCOPE_PATTERNS 同机制;GLOBAL 不设词表——全球性查询单过滤维度语义不成立)
ECONOMY_CUES = (
    ("EA", ("欧元区", "欧洲央行", "欧央行", "ECB", "HICP", "Bund", "德国国债",
            "DAX", "CAC40", "欧元股")),
    ("JP", ("日本", "日银", "BOJ", "日元", "JGB", "日经", "NIKKEI", "东京CPI")),
    ("CN", ("中国", "人民币", "中资", "A股", "沪深", "LPR", "社融", "逆回购",
            "SHCOMP", "中国央行")),
    ("US", ("美国", "美联储", "联邦基金", "美债", "美股")),
    ("HK", ("香港", "恒生", "港股")),
)

# D-B1-02: 概念规则恰4条(约束式;触发/绑定/缺席概念/派生公式逐项登记)
CONCEPT_RULES = (
    {
        "key": "us_jp_policy_rate_spread",
        "trigger": re.compile(r"政策利率差"),
        "us_bindings": ("DFEDTARL", "DFEDTARU", "DFF"),
        "absent_concepts": (
            {"label": "日本政策利率",
             "search_terms": ("日本政策利率", "日银", "BOJ")},
        ),
        "ops": (
            {"op_label": "美日政策利率差",
             "formula": "日本政策利率 − (DFEDTARL+DFEDTARU)/2(目标区间中值)",
             "operands": ("@absent:日本政策利率", "DFEDTARL", "DFEDTARU"),
             "unit": "percentage_point"},
        ),
    },
    {
        "key": "us_jp_10y_yield_spread",
        "trigger": re.compile(r"(?:10年期|十年期)[\u4e00-\u9fa5]{0,6}收益率差"),
        "us_bindings": ("UST_2Y", "UST_10Y", "CURVE_2S10S"),
        "absent_concepts": (
            {"label": "JGB 10Y",
             "search_terms": ("JGB", "日本国债", "日本10年", "10年期日债")},
        ),
        "ops": (
            {"op_label": "美日10Y收益率差",
             "formula": "JGB 10Y − UST_10Y",
             "operands": ("@absent:JGB 10Y", "UST_10Y"),
             "unit": "percentage_point"},
            {"op_label": "美端2s10s(查询期)",
             "formula": "UST_10Y − UST_2Y(查询期计算,对照注册值CURVE_2S10S)",
             "operands": ("UST_10Y", "UST_2Y"),
             "unit": "percentage_point"},
        ),
    },
    {
        "key": "usdjpy_level",
        "trigger": re.compile(r"美元兑日元|美元日元|USDJPY|USD/JPY|日元汇率"),
        "us_bindings": ("USDJPY",),
        "windows_on_cue": ("week", "ytd"),
    },
    {
        "key": "us_policy_rate_level",
        "trigger": re.compile(r"联邦基金|美联储利率|美国政策利率"),
        "us_bindings": ("DFEDTARL", "DFEDTARU", "DFF"),
    },
)

ABSENT_REASON_TEMPLATE_JP = "{label}不在注册表({n}指标,INVENTORY G-01)"     # D-B1-05
ABSENT_REASON_TEMPLATE_US = "{metric_id}不在注册表({n}指标)"
CALC_REF_TEMPLATE = "公式: {formula};输入观测日与期限匹配由执行器(WP-B2)按E11纪律落定"  # D-B1-13
CALC_REF_NO_DATA_SUFFIX = ";operand缺席→NO_DATA不部分计算(DESIGN §三(c))"


# ══ 纯函数工具 ═════════════════════════════════════════════════════════

def field_for_window(unit):
    """窗口field单位纪律(D-B1-06): 复用fact_engine单位语义常量(零复制)。

    利率/利差类(percent/percentage_point)→pp_change;计数类→abs_change;
    价格类→pct_change(E3单位纪律,DESIGN L88-89/fact_engine.py:33-38);
    未知单位语义→raise不猜映射。
    """
    if unit in fe.RATE_UNITS:
        return "pp_change"
    if unit in fe.COUNT_UNITS:
        return "abs_change"
    if unit in fe.PRICE_LIKE_UNITS:
        return "pct_change"
    raise ValueError(f"未知单位语义,不猜映射(D-B1-06): {unit!r}")


def _spans_overlap(a, b):
    return a[0] < b[1] and b[0] < a[1]


def _search_registry(terms, metrics):
    """候选指标检索(D-B1-04): display_name/calc 关键词命中计分→最高分metric_id。

    对齐DESIGN L109「候选指标检索(注册表display_name/calc/别名,经E2)」;
    零命中→None(=A1缺席的发现机制,非硬编码)。
    MW-V1(2026-11-08) 修期限错绑: 旧"首个命中"在家族指标下按注册表序先中——
    JGB 家族 calc 共享曲线描述词("MOF日本国债收益率曲线…"),概念"JGB 10Y"
    的检索词"日本国债"先命中序号更小的 JGB2Y,公式"JGB 10Y − UST_10Y"实拿
    2年期值=期限错配(真实注册表复现;旧测试 fixture 无家族竞争故未暴露)。
    改为计分制: 每候选按**命中词数**计分(词表含期限词时正确期限候选多得
    一分),平分时 display_name 命中优先于 calc 命中(display=人工身份声明,
    calc=采集描述),仍平分保持注册表序(稳定,不改变无竞争场景的既有结果)。
    """
    best, best_key = None, None
    for m in metrics:
        disp = m.get("display_name") or ""
        calc = m.get("calc") or ""
        n_disp = sum(1 for t in terms if t in disp)
        n_calc = sum(1 for t in terms if t in calc)
        if n_disp + n_calc == 0:
            continue
        key = (n_disp + n_calc, n_disp)      # 命中词数 → display命中数
        if best_key is None or key > best_key:
            best, best_key = m.get("metric_id"), key
    return best


def _merge_spans(spans):
    """重叠span合并(out_of_scope词表重叠命中归并为一个指称,D-B1-07)。"""
    if not spans:
        return []
    ordered = sorted(set(spans))
    merged = [ordered[0]]
    for s, e in ordered[1:]:
        ls, le = merged[-1]
        if s <= le:
            merged[-1] = (ls, max(le, e))
        else:
            merged.append((s, e))
    return merged


# ══ 映射主入口 ═════════════════════════════════════════════════════════

def map_question(question_text, *, created_at=None, query_seq=1, as_of=None,
                 registry=None):
    """NL问题 → StructuredResearchQuery IR(DESIGN §三(a) schema,只产IR不取数)。

    参数:
      question_text: 用户原始自然语言问题(原样保留入IR,DESIGN L60);
      created_at:    受理时刻ISO8601(UTC+8);缺省=now(DESIGN L58;确定性测试须显式注入);
      query_seq:     同日序号(query_id=QB-YYYYMMDD-NNN,D-B1-10;缺省1);
      as_of:         显式研究截止(D6);优先于文本检测;文本「截至/截止+ISO日期」
                     经fe.parse_iso_date(E4)严格校验后透传,非法→不设(D-B1-08);
      registry:      注册表dict(含metrics;by_id可缺省);缺省=fe.load_registry()(E1)。
                     依赖注入面——测试合成fixture唯一数据源(D-B1-11)。

    返回: IR dict;产出即过 validate_ir(stage="mapped") 自检(fail-loud)。
    """
    if not isinstance(question_text, str) or not question_text.strip():
        raise ValueError("question_text须为非空字符串")
    if created_at is None:
        created_at = datetime.now(TZ_BJ).isoformat()
    if registry is None:
        registry = fe.load_registry()                      # E1(与E2同构,见模块docstring)
    metrics = registry.get("metrics", [])
    by_id = registry.get("by_id") or {m.get("metric_id"): m for m in metrics}
    n_metrics = len(metrics)
    consumed_spans = []

    # ── 步骤1: out_of_scope拦截(D-B1-07;如实上浮,不整题拒答) ──
    oos_spans = []
    for pat in OUT_OF_SCOPE_PATTERNS:
        for m in re.finditer(re.escape(pat), question_text):
            oos_spans.append(m.span())
    unresolved = []
    for s, e in _merge_spans(oos_spans):
        consumed_spans.append((s, e))
        unresolved.append({"mention": question_text[s:e],
                           "mapping_status": "out_of_scope",
                           "note": NOTE_OUT_OF_SCOPE})

    # ── 步骤2: 显式as_of检测(D-B1-08;E4严格校验) ──
    if as_of is None:
        m = AS_OF_CUE_RE.search(question_text)
        if m and fe.parse_iso_date(m.group(1)) is not None:
            as_of = m.group(1)

    # ── 步骤3: 概念规则触发(每规则至多1次,D-B1-02) ──
    fired = []
    for rule in CONCEPT_RULES:
        m = rule["trigger"].search(question_text)
        if m:
            consumed_spans.append(m.span())
            fired.append(rule)

    # ── 步骤4: 绑定发射(阶段1 level→阶段2 缺席概念→阶段3 窗口,D-B1-03) ──
    bindings = []
    key_to_bid = {}
    absent_label_to_bid = {}

    def _emit(identity, metric_id, role, window, field, status, absence_reason=None):
        """identity=去重键(意图身份: US意图metric_id或JP概念label,与解析结果无关);
        metric_id=解析后注册表身份(缺席=None)——两者分离,防同问题多缺席概念撞键。"""
        key = (identity, role, window, field)
        if key in key_to_bid:
            return key_to_bid[key]
        bid = "MB-{}".format(len(bindings) + 1)
        bindings.append({"binding_id": bid, "metric_id": metric_id, "role": role,
                         "window": window, "field": field, "status": status,
                         "absence_reason": absence_reason, "provenance": None})
        key_to_bid[key] = bid
        return bid

    for rule in fired:                                     # 阶段1: US/global侧level
        for mid in rule["us_bindings"]:
            if mid in by_id:
                _emit(mid, mid, "level", None, "value", qir.PENDING_EXECUTION)
            else:                                          # A1发现机制(D-B1-04)
                _emit(mid, None, "level", None, "value", "ABSENT_REGISTRY",
                      ABSENT_REASON_TEMPLATE_US.format(metric_id=mid, n=n_metrics))
    for rule in fired:                                     # 阶段2: 缺席概念(注册表检索发现)
        for ac in rule.get("absent_concepts", ()):
            label = ac["label"]
            if label in absent_label_to_bid:
                continue
            hit = _search_registry(ac["search_terms"], metrics)
            if hit is None:
                bid = _emit(label, None, "spread_component", None, "value",
                            "ABSENT_REGISTRY",
                            ABSENT_REASON_TEMPLATE_JP.format(label=label, n=n_metrics))
            else:                                          # 注册表命中→身份解析(非硬编码缺席)
                bid = _emit(label, hit, "spread_component", None, "value",
                            qir.PENDING_EXECUTION)
            absent_label_to_bid[label] = bid
            for term in (label,) + tuple(ac["search_terms"]):   # 消费概念词span
                for m in re.finditer(re.escape(term), question_text):
                    consumed_spans.append(m.span())
    for rule in fired:                                     # 阶段3: 窗口绑定(趋势cue在场)
        windows = rule.get("windows_on_cue")
        if not windows or not TREND_CUE_RE.search(question_text):
            continue
        for mid in rule["us_bindings"]:
            entry = by_id.get(mid)
            if entry is None:
                continue                                   # 缺席指标无单位语义,不猜field
            for w in windows:
                _emit(mid, mid, "derived_window", w,
                      field_for_window(entry.get("unit")), qir.PENDING_EXECUTION)

    # ── 步骤5: 派生操作(operand绑定齐备性→NO_DATA|PENDING_EXECUTION,D-B1-12) ──
    ops = []
    for rule in fired:
        for spec in rule.get("ops", ()):
            op_bids = []
            for ref in spec["operands"]:
                if ref.startswith("@absent:"):
                    op_bids.append(absent_label_to_bid[ref[len("@absent:"):]])
                else:
                    op_bids.append(key_to_bid[(ref, "level", None, "value")])
            any_absent = any(b["status"].startswith("ABSENT")
                             for b in bindings if b["binding_id"] in op_bids)
            status = "NO_DATA" if any_absent else qir.PENDING_EXECUTION
            calc_ref = CALC_REF_TEMPLATE.format(formula=spec["formula"])
            if status == "NO_DATA":
                calc_ref += CALC_REF_NO_DATA_SUFFIX
            ops.append({"op_id": "OP-{}".format(len(ops) + 1),
                        "op_type": "spread", "operands": op_bids,
                        "formula": spec["formula"], "unit": spec["unit"],
                        "status": status, "result": None,
                        "calculation_ref": calc_ref})

    # ── 步骤6: 剩余指称上浮(D-B1-09;已消费span跳过,零命中如实登记) ──
    seen_mentions = {u["mention"] for u in unresolved}
    for m in METRICISH_RE.finditer(question_text):
        if any(_spans_overlap(m.span(), c) for c in consumed_spans):
            continue
        mention = m.group(0)
        if mention in seen_mentions:
            continue
        if _search_registry((mention,), metrics) is not None:
            continue
        seen_mentions.add(mention)
        unresolved.append({"mention": mention,
                           "mapping_status": "no_registry_identity",
                           "note": NOTE_NO_IDENTITY})

    # ── 步骤7: IR装配+自检(fail-loud;产出必须过自身schema校验) ──
    ir = {
        "query_id": qir.make_query_id(created_at, query_seq),
        "created_at": created_at,
        "mode": qir.MODE_B,
        "question_text": question_text,
        "as_of": as_of,
        "target_snapshot_id": None,                        # 快照绑定=R1,属WP-B2(D-B1-08)
        "metric_bindings": bindings,
        "derived_operations": ops,
        "unresolved_entities": unresolved,
        "answer_constraints": dict(qir.ANSWER_CONSTRAINTS),
    }
    # IA-P1-WP-D PD-4: economy识别与条件写——恰单族cue命中且概念规则零触发才写键
    # (跨经济体比较链(fired)与零族/多族不设单过滤维度;向后兼容: 既有问题IR零新键)
    if not fired:
        hit_econs = {econ for econ, cues in ECONOMY_CUES
                     if any(c in question_text for c in cues)}
        if len(hit_econs) == 1:
            ir["economy"] = next(iter(hit_econs))
    issues = qir.validate_ir(ir, stage="mapped")
    if issues:
        raise ValueError("映射产出IR未过schema校验(D-B1 fail-loud): " + ";".join(issues))
    return ir
