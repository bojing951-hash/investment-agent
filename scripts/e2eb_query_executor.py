#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P03-E2EB-WP-B2: 模式B查询执行器(IR→数值;纯离线零网络)。

DESIGN docs/P03_E2EB_DESIGN.md §六 WP-B2(L216-220):
- 快照绑定(R1/R3): 目标快照=注入 snapshot(调用方经R1/S1取得)或执行器自取
  (R1 既有快照文件优先 → 无则 S1 build_snapshot(write=False) 离线构建,
  DESIGN L177「只读锚定既有快照/离线构建(write=False)」);门禁=gate_a.status
  经 rp.gate_allows_formal_research(R3)判定,FAIL/None→结构化 refusal 零部分执行;
- 引擎口径取值(E3/E5/E11复用): 一切数值取自快照事实(fact.value/fact.derived,
  E5构造/E3窗口),执行器零自有计算口径;
- spread/level_diff查询期派生(D3,calculation_ref纪律对齐E11);
- 按需配对相关性(C3/C4复用series_store,D4): 复用 correlation_calculator
  paired_returns/pearson,零复制;
- as_of时点只读锚定(D6): ymd=as_of日期部分经fe.parse_iso_date(E4)严格校验;
  绑定后 target_snapshot_id 携带于 executed IR(L177「绑定后不可变」)。

数据入口纪律(DESIGN §七1/L246): 唯一数据入口=rp.select_snapshot(R1)+
rp.gate_allows_formal_research(R3)+sb.build_snapshot(S1);本模块零 open()/
零采集档文件IO(as_of=None时仅以 os.listdir 列举快照层文件名取最大ymd,
D-B2-12);data_dir 参数由调用方注入(测试合成采集文件写tempdir,
tests/test_snapshot.py 同构);禁墙钟(D-B2-01)。
零网络/零模型调用/零凭证;缺值如实缺席零填0(四级缺席 DESIGN §三(c) L118-129)。

参数与决策点全部先登记后运行: docs/P03_E2EB_B2_REPORT.md §六
(D-B2-01..D-B2-14;承接 B1 D-B1-01/12/13;运行后禁回改)。
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fact_engine as fe                                  # E1/E2/E4(既有依赖)
import snapshot_builder as sb                             # S1(write=False 离线构建)
import research_provenance as rp                          # R1/R3(快照选择+门禁)
import e2eb_query_ir as qir                               # B1 IR schema(两阶段校验)
import correlation_calculator as cc                       # C3/C4(配对相关复用)

# D-B2-07: registry source → sources_status 通道映射
# IA-P1-WP-D PD-6: 增 jp/ea 两键(WP-A 采集面 source → rp.SOURCE_FILE_RULES 键
# "jp"/"ea" 实读对齐,research_provenance.py:168-176),使 _mark_channel_absent
# 对 jp/ea 指标可按快照 sources_status 做 A2 通道归因(缺席差距登记结构化);
# economy 过滤本身经 IR 驱动(绑定循环无经济体分支),_refusal/_resolve_binding 零改动。
CHANNEL_OF_SOURCE = {
    "macro_collector": "macro",
    "global_market_collector": "global",
    "rate_expectations": "rate_economy",
    "china_market_collector": "china",
    "jp_market_collector": "jp",
    "ea_market_collector": "ea",
}
# D-B2-12: 快照层文件名(research_snapshot_YYYYMMDD[_vN].json)——仅用于最大ymd枚举
_SNAPSHOT_FILE_RE = re.compile(r"^research_snapshot_(\d{8})(?:_v\d+)?\.json$")

# D-B2-04/D-B2-07: 缺席理由模板(DESIGN §三(c) L124-127 措辞)
REASON_ABSENT_SOURCE = "指标已注册但当日采集缺失(通道{ch}状态{st})"
REASON_ABSENT_DATA = "本期无该指标事实"
REASON_ABSENT_DATA_DERIVED = "本期无该指标事实(派生输入缺席,归因性缺席)"
REASON_ABSENT_WINDOW_NO_SERIES = "事实无窗口派生(序列缺席,窗口不可用)"
REASON_ABSENT_WINDOW_NO_FIELD = "窗口记录无字段{field}(E3未产出该口径)"
# D-B2-08: 执行器侧A1防御
REASON_ABSENT_REGISTRY = "{mid}不在注册表({n}指标)"
# D-B2-09: COMPUTED calculation_ref 模板(E11纪律: 公式+输入观测日+期限匹配)
MATURITY_MATCH = "期限匹配(观测日一致,E11纪律)"
MATURITY_MISMATCH = "观测日不一致({dates}),差异如实披露不混同"
CALC_REF_SPREAD = "公式: {formula};输入观测日{dates};{maturity}"
CALC_REF_LEVEL_DIFF = ("公式: {formula};两时点={obs} vs 窗口基准{basis}"
                       "(同指标level−窗口基准,E3基准日)")
CALC_REF_CORRELATION = ("公式: pearson(日收益率,{a},{b});共同观测窗{first}~{last},"
                        "样本{n}(C3/C4复用)")
NO_DATA_SUFFIX_EXEC = ";operand缺席→NO_DATA不部分计算(执行器,DESIGN §三(c))"
NO_DATA_CORR_NO_STORE = (";序列不在快照series_store(macro通道序列不经store,"
                         "既有结构边界)")


def _refusal(ir, snapshot_id, gate_status, reason):
    """结构化拒绝(D-B2-03): IR原样(mapped态)、零数值、如实原因。"""
    return {"ir": ir, "values": {}, "snapshot_id": snapshot_id,
            "gate_status": gate_status, "refusal": reason}


def _ymd_from_as_of(as_of):
    """D-B2-02: as_of(ISO日期/时间戳)→目标快照YYYYMMDD;E4严格校验,fail-loud。"""
    if as_of is None:
        return None
    d = fe.parse_iso_date(str(as_of)[:10])
    if d is None:
        raise ValueError(f"as_of非法(须ISO日期/时间戳,E4严格校验): {as_of!r}")
    return d.strftime("%Y%m%d")


def _latest_snapshot_ymd(daily_dir):
    """D-B2-12: as_of=None 时枚举快照层文件名取最大ymd(零采集档IO,禁墙钟)。"""
    ymds = []
    try:
        names = os.listdir(daily_dir)
    except OSError:
        return None
    for name in names:
        m = _SNAPSHOT_FILE_RE.match(name)
        if m:
            ymds.append(m.group(1))
    return max(ymds) if ymds else None


def _acquire_snapshot(ir, daily_dir, trusted_root):
    """D-B2-01/D-B2-12: R1既有快照优先→无则S1离线构建(write=False);禁墙钟。"""
    ymd = _ymd_from_as_of(ir.get("as_of"))
    if ymd is not None:
        snap, _path = rp.select_snapshot(ymd, daily_dir)
        if isinstance(snap, dict):
            return snap, None
        snap = sb.build_snapshot(target_ymd=ymd, data_dir=daily_dir, write=False,
                                 as_of=ir.get("as_of"), trusted_root=trusted_root)
        return snap, None
    latest = _latest_snapshot_ymd(daily_dir)
    if latest is None:
        return None, "无可绑定快照: as_of未指定且目录无既有快照(禁墙钟,D-B2-01)"
    snap, reason = rp.select_snapshot(latest, daily_dir)
    if not isinstance(snap, dict):
        return None, f"快照选择失败(R1): {reason}"
    return snap, None


def _mark_resolved(binding, fact, snapshot, values, value, calc_ref):
    """D-B2-05: RESOLVED+provenance装配(source_file仅披露,查询器无直读路径)。"""
    binding["status"] = "RESOLVED"
    binding["provenance"] = {
        "metric_id": binding["metric_id"],
        "snapshot_id": snapshot.get("snapshot_id"),
        "fact_id": fact.get("fact_id"),
        "observation_date": fact.get("observation_date"),
        "source_file": (fact.get("source") or {}).get("file"),
        "quality_status": fact.get("quality_status"),
        "calculation_ref": calc_ref,
    }
    values[binding["binding_id"]] = value


def _mark_channel_absent(binding, metric_entry, sources_status):
    """D-B2-07: A2(通道MISSING/READ_FAIL)优先,否则A3(本期无事实)。"""
    ch = CHANNEL_OF_SOURCE.get(metric_entry.get("source"))
    if ch is not None:
        st = (sources_status.get(ch) or {}).get("status")
        if st in ("MISSING", "READ_FAIL"):
            binding["status"] = "ABSENT_SOURCE"
            binding["absence_reason"] = REASON_ABSENT_SOURCE.format(ch=ch, st=st)
            return
    binding["status"] = "ABSENT_DATA"
    binding["absence_reason"] = (REASON_ABSENT_DATA_DERIVED if ch is None
                                 else REASON_ABSENT_DATA)


def _resolve_binding(binding, metric_entry, facts_by_id, sources_status,
                     snapshot, values):
    """D-B2-04: 单绑定执行——level族(事实RESOLVED|A2/A3)与derived_window四级。"""
    mid = binding["metric_id"]
    fact = facts_by_id.get(mid)
    if binding["role"] == "derived_window":
        if fact is None:
            _mark_channel_absent(binding, metric_entry, sources_status)
            return
        window_rec = (fact.get("derived") or {}).get(binding["window"])
        if not isinstance(window_rec, dict):
            binding["status"] = "ABSENT_WINDOW"
            binding["absence_reason"] = REASON_ABSENT_WINDOW_NO_SERIES
            return
        if window_rec.get("available") is False:
            binding["status"] = "ABSENT_WINDOW"
            binding["absence_reason"] = f"E3窗口不可用: {window_rec.get('reason')}"
            return
        field = binding.get("field")
        if window_rec.get(field) is None:
            binding["status"] = "ABSENT_WINDOW"
            binding["absence_reason"] = REASON_ABSENT_WINDOW_NO_FIELD.format(field=field)
            return
        calc_ref = (f"窗口{binding['window']}.{field};"
                    f"基准{window_rec.get('basis_date')}(E3口径)")
        _mark_resolved(binding, fact, snapshot, values, window_rec[field], calc_ref)
        return
    # level / spread_component / correlation_series: E5事实值
    if (fact is None or fact.get("fact_id") is None
            or not isinstance(fact.get("value"), (int, float))):
        _mark_channel_absent(binding, metric_entry, sources_status)
        return
    _mark_resolved(binding, fact, snapshot, values, fact.get("value"),
                   fact.get("calculation_ref"))


def _operand_obs_dates(operand_bindings):
    return [b["provenance"]["observation_date"] for b in operand_bindings]


def _execute_spread(op, operand_bindings, values):
    """D-B2-09: result=v[0]−mean(v[1:])(2=首−次;3=首−其余均值,OP-1中值族)。"""
    vs = [values[b["binding_id"]] for b in operand_bindings]
    result = round(vs[0] - sum(vs[1:]) / len(vs[1:]), 4)
    dates = _operand_obs_dates(operand_bindings)
    uniq = sorted(set(dates))
    maturity = (MATURITY_MATCH if len(uniq) == 1
                else MATURITY_MISMATCH.format(dates=" vs ".join(uniq)))
    op["result"] = result
    op["calculation_ref"] = CALC_REF_SPREAD.format(
        formula=op["formula"], dates=",".join(dates), maturity=maturity)
    op["status"] = "COMPUTED"


def _execute_level_diff(op, operand_bindings, values, facts_by_id):
    """D-B2-10: 同指标两时点差=level观测日值−E3窗口基准值。"""
    if len(operand_bindings) != 2:
        raise ValueError("level_diff须恰2 operands(D-B2-10)")
    ba, bb = operand_bindings
    if ba["metric_id"] != bb["metric_id"]:
        raise ValueError(f"level_diff须同指标两绑定: "
                         f"{ba['metric_id']} vs {bb['metric_id']}(D-B2-10)")
    level_b = next((b for b in (ba, bb) if b["role"] == "level"), None)
    window_b = next((b for b in (ba, bb) if b["role"] == "derived_window"), None)
    if level_b is None or window_b is None:
        raise ValueError("level_diff须一level绑定+一derived_window绑定"
                         "(两时点=观测日vs窗口基准日,D-B2-10)")
    fact = facts_by_id[level_b["metric_id"]]
    window_rec = (fact.get("derived") or {}).get(window_b["window"]) or {}
    basis_value = window_rec.get("basis_value")
    if not isinstance(basis_value, (int, float)):
        op["result"] = None
        op["status"] = "NO_DATA"
        op["calculation_ref"] += (";窗口基准值缺席→NO_DATA不部分计算"
                                  "(执行器,DESIGN §三(c))")
        return
    result = round(values[level_b["binding_id"]] - basis_value, 4)
    op["result"] = result
    op["calculation_ref"] = CALC_REF_LEVEL_DIFF.format(
        formula=op["formula"],
        obs=level_b["provenance"]["observation_date"],
        basis=window_rec.get("basis_date"))
    op["status"] = "COMPUTED"


def _execute_correlation(op, operand_bindings, snapshot):
    """D-B2-11: series_store两序列→C3配对+C4相关(复用零复制);样本不足如实NO_DATA。"""
    ba, bb = operand_bindings
    store = snapshot.get("series_store") or {}
    sa = store.get(ba["metric_id"])
    sb_ = store.get(bb["metric_id"])
    if not sa or not sb_:
        op["result"] = None
        op["status"] = "NO_DATA"
        reason = NO_DATA_CORR_NO_STORE if (sa is None or sb_ is None) else \
            ";序列结构非法(缺dates/values)"
        op["calculation_ref"] += reason
        return
    pair, common = cc.paired_returns(sa, sb_)
    if not pair:
        op["result"] = None
        op["status"] = "NO_DATA"
        op["calculation_ref"] += ";共同观测日不足(<3,C3语义)"
        return
    ra, rb = pair
    rho = cc.pearson(ra, rb)
    if rho is None:
        op["result"] = None
        op["status"] = "NO_DATA"
        op["calculation_ref"] += ";零方差或样本不足(C4语义)"
        return
    op["result"] = round(rho, 4)
    op["calculation_ref"] = CALC_REF_CORRELATION.format(
        a=ba["metric_id"], b=bb["metric_id"],
        first=common[0] if common else "", last=common[-1] if common else "",
        n=len(ra))
    op["status"] = "COMPUTED"


def execute_query(ir, *, snapshot=None, daily_dir=None, trusted_root=None,
                  registry=None):
    """mapped IR → 数值(DESIGN §六 WP-B2;参数登记 D-B2-01..13)。

    参数:
      ir:           B1映射器产出的 mapped IR(须过 validate_ir(stage="mapped"));
      snapshot:     显式注入快照(调用方经R1/S1取得;依赖注入面,D-B2-01);
      daily_dir:    快照目录(执行器自取: R1既有快照优先→无则S1 write=False
                    离线构建;as_of=None时枚举既有快照最大ymd,无→refusal);
      trusted_root: 采集目录可信根(S1构建转发,tests/test_snapshot.py同构);
      registry:     注册表dict(缺省=fe.load_registry(),E1;依赖注入面)。

    返回: {"ir": executed_ir, "values": {binding_id: value}, "snapshot_id",
           "gate_status"};门禁不放行/无可绑定快照→{"ir": 原样, "values": {},
           "refusal": 原因}(D-B2-03,零部分执行)。
    输入IR零原地变异(深拷贝,D-B2-06);产出必过 validate_ir(stage="executed")
    (D-B2-13 fail-loud)。
    """
    issues = qir.validate_ir(ir, stage="mapped")
    if issues:
        raise ValueError("输入IR未过mapped schema校验(D-B2-04 fail-loud): "
                         + ";".join(issues))
    if registry is None:
        registry = fe.load_registry()                      # E1
    reg_by_id = registry.get("by_id") or {m.get("metric_id"): m
                                          for m in registry.get("metrics", [])}
    ex_ir = dict(ir)
    ex_ir["metric_bindings"] = [dict(b) for b in ir["metric_bindings"]]
    ex_ir["derived_operations"] = [dict(o) for o in ir["derived_operations"]]
    ex_ir["unresolved_entities"] = [dict(u) for u in ir["unresolved_entities"]]
    ex_ir["answer_constraints"] = dict(ir["answer_constraints"])

    if snapshot is None:
        if daily_dir is None:
            return _refusal(ex_ir, None, None,
                            "无可绑定快照: 未注入snapshot且未提供daily_dir(D-B2-01)")
        snapshot, refuse_reason = _acquire_snapshot(ex_ir, daily_dir, trusted_root)
        if snapshot is None:
            return _refusal(ex_ir, None, None, refuse_reason)
    if not isinstance(snapshot, dict) or not snapshot.get("snapshot_id"):
        return _refusal(ex_ir, None, None, "快照结构非法(缺snapshot_id)")

    gate_status = (snapshot.get("gate_a") or {}).get("status")
    if not rp.gate_allows_formal_research(gate_status):    # R3
        return _refusal(ex_ir, snapshot.get("snapshot_id"), gate_status,
                        f"Gate A状态{gate_status!r}不放行正式研究查询(R3): "
                        f"{rp.gate_reason_desc(snapshot)}")

    ex_ir["target_snapshot_id"] = snapshot.get("snapshot_id")   # L177 绑定后不可变
    facts_by_id = {f.get("metric_id"): f for f in snapshot.get("facts", [])
                   if isinstance(f, dict) and f.get("metric_id")}
    sources_status = snapshot.get("sources_status") or {}
    values = {}

    for b in ex_ir["metric_bindings"]:
        if b["status"] != qir.PENDING_EXECUTION:           # ABSENT族终态原样保留
            continue
        mid = b["metric_id"]
        metric_entry = reg_by_id.get(mid)
        if metric_entry is None:                           # D-B2-08 执行器侧A1防御
            b["metric_id"] = None
            b["status"] = "ABSENT_REGISTRY"
            b["absence_reason"] = REASON_ABSENT_REGISTRY.format(
                mid=mid, n=len(registry.get("metrics", [])))
            continue
        _resolve_binding(b, metric_entry, facts_by_id, sources_status,
                         snapshot, values)

    bindings_by_id = {b["binding_id"]: b for b in ex_ir["metric_bindings"]}
    for op in ex_ir["derived_operations"]:
        if op["status"] != qir.PENDING_EXECUTION:          # NO_DATA终态原样保留
            continue
        operand_bindings = [bindings_by_id[ref] for ref in op["operands"]]
        if any(ob["status"] != "RESOLVED" for ob in operand_bindings):
            op["status"] = "NO_DATA"
            op["result"] = None
            op["calculation_ref"] += NO_DATA_SUFFIX_EXEC
            continue
        if op["op_type"] == "spread":
            _execute_spread(op, operand_bindings, values)
        elif op["op_type"] == "level_diff":
            _execute_level_diff(op, operand_bindings, values, facts_by_id)
        elif op["op_type"] == "correlation":
            _execute_correlation(op, operand_bindings, snapshot)
        else:
            raise ValueError(f"op_type枚举外值: {op['op_type']!r}")

    issues = qir.validate_ir(ex_ir, stage="executed")
    if issues:
        raise ValueError("执行产出IR未过executed schema校验(D-B2-13 fail-loud): "
                         + ";".join(issues))
    return {"ir": ex_ir, "values": values,
            "snapshot_id": snapshot.get("snapshot_id"), "gate_status": gate_status}
