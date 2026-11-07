#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P3-WP-D: 报告质量评价循环(P3 收尾层第 4 实现包;#36 挂靠)

DESIGN docs/P3_DESIGN.md §7 WP-P3-D 行(L188-L192,基线工作树实读)确定性落地:
- 旁路统计件(月度/季度节奏,§6.1 L142-147 评价维度 5 项):
  ①数值质量(gate_b 通过率与 DEGRADED 率)②覆盖度(核心指标引用覆盖,
  core 集=registry criticality=core)③预测质量(裁决终态分布与错误模式
  统计,承接 §5.2=WP-P3-C prd.review_statistics 复用承载,零重算零改写)
  ④时效(按时发布率,发布事务 generated_at 同日落档口径)⑤论证完整度
  (证据分级星级分布+未解释反证封顶触发次数,rg L521 规则可观测面);
- 简报渲染+校准建议清单: 质量简报(人读)→ 校准建议条目
  (requires_user_confirmation 恒 true);**不含提示词自动注入**(注入须
  用户确认,DP-8 确认权留用户——本模块零注入零回写零周报系统触碰);

取数面(要点③): 周报唯一取数入口=rp.scan_formal_weekly_reports(发布
状态认定: published=True+final_quality∈(PASS,DEGRADED)+身份一致+digest
实算一致,任一不满足即拒);候选/未验证/未发布件一律不入统计;快照纪律
守卫 _reject_raw_data_path(data+daily 路径 fail-loud;DESIGN §3.1 禁直读
原始采集档)。

只读纪律(要点①): 本模块**零文件写入面**(无写模式 open/无 os.replace/
无 json.dump 落盘);report_generator/data_validator/发布事务/主流水线
零触碰(周报系统主流程 diff 为空=白名单 M=0 结构性保障+测试字节级等值
双保险)。

对齐上游=复用调用,禁复制分叉(P-D-15): rp.scan_formal_weekly_reports/
rp.GATES/rp.FORMAL_FINAL_QUALITIES;ae._parse_status_block;prd.
prediction_review_report/review_statistics/hypothesis_warnings/window_bounds。

纪律: 零网络零 GLM 零凭证零付费(import 面白名单 json/os/re/sys/datetime+
项目既有 research_provenance/allocation_engine/prediction_review);一切
日期依赖纯函数显式 as_of 必填(唯一墙钟缺省=编排面 report_quality_review
边缘);本模块输出为报告质量评价循环面数据,**不构成投资建议**(DESIGN
§8.3 红线: 禁交易/禁仓位/禁收益承诺)。
参数登记: docs/P3_WP_D_REPORT.md §零.4/§零.5(DP-7/DP-8+P-D-01..P-D-20,
先登记后实现,运行后禁回改)。
"""
import json
import os
import re
import sys
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import allocation_engine as ae      # 状态块解析复用面(只读禁改)
import prediction_review as prd     # WP-P3-C 预测质量维度承载(复用调用)
import research_provenance as rp    # 发布状态认定取数面(复用调用)

# ══ 登记型参数定值(REPORT §零.4/§零.5;登记定值即实现值,运行后禁回改) ═══

DP7_DIMENSION_SET = 5                                    # DP-7 维度半: 5 维全启
DP7_THRESHOLD_ISSUE = "first_issue"                      # DP-7 阈值半: 首期登记
DP8_INJECTION_POLICY = "user_confirmation_required"      # DP-8: 注入须用户确认(本包零实现)

DIMENSION_LABELS = {                                     # P-D-10 维度键词表(字典序)
    "argument_completeness": "论证完整度",
    "coverage": "覆盖度",
    "numeric_quality": "数值质量",
    "prediction_quality": "预测质量",
    "timeliness": "时效",
}
DIMENSION_KEYS = tuple(sorted(DIMENSION_LABELS))         # ("argument_completeness",
#  "coverage","numeric_quality","prediction_quality","timeliness")
DIMENSION_STATUS = ("OK", "ATTENTION", "NO_DATA")        # P-D-10 状态词表

THRESHOLDS = {                                           # P-D-10 阈值定值(DP-7 首期)
    "numeric_quality.gate_b_pass_rate_min": 0.90,
    "coverage.mean_core_coverage_min": 0.80,
    "prediction_quality.hit_rate_min": 0.30,
    "timeliness.on_time_rate_min": 0.90,
    "argument_completeness.unexplained_contrary_attention_threshold": 2,
}

WINDOW_KINDS = ("monthly", "quarterly")                  # P-D-02 月度/季度节奏
STATS_SCHEMA_VERSION = 1                                 # P-D-13
SUGGESTION_MARKER = "SUG-"                               # P-D-12 建议条目 ID 前缀
REQUIRES_USER_CONFIRMATION = True                        # P-D-12: 恒 true(DP-8 零自决)

STATUS_BLOCK_TAGS = ("THESIS_STATUS", "ALLOCATION_STATUS")   # P-D-09 解析面
STAR_LEVELS = ("1", "2", "3", "4", "5")                  # P-D-09 星级直方图五桶全键

# 模块内登记镜像(dp_selfcheck 哨兵对照源;与 REPORT §零.4/§零.5 登记值一致)
_DP_REGISTERED = {"DP-7": "5_dims+first_issue_thresholds",
                  "DP-8": "user_confirmation_required"}
_PARAM_REGISTERED = {
    "dimension_keys": ("argument_completeness", "coverage", "numeric_quality",
                       "prediction_quality", "timeliness"),
    "threshold_gate_b_pass_rate_min": 0.90,
    "threshold_mean_core_coverage_min": 0.80,
    "threshold_hit_rate_min": 0.30,
    "threshold_on_time_rate_min": 0.90,
    "threshold_unexplained_contrary_attention": 2,
    "dimension_status": ("OK", "ATTENTION", "NO_DATA"),
    "window_kinds": ("monthly", "quarterly"),
    "stats_schema_version": 1,
}

REVIEW_NOTE = ("报告质量评价循环(旁路统计,零注入零回写,周报系统主流程零改动;"
               "月度/季度节奏;评价维度5项[数值质量/覆盖度/预测质量/时效/论证"
               "完整度,DP-7 登记口径];预测质量维度经WP-P3-C复用承载[DP-5/DP-6"
               " 上游登记口径];校准建议注入提示词须用户确认[DP-8,确认权留用户]"
               ");本统计不构成投资建议(禁交易/禁仓位/禁收益承诺)")

_BRIEFING_TAIL = ("本简报为报告质量评价循环面输出(旁路统计,零注入零回写,"
                  "校准建议注入须用户确认[DP-8]);不构成投资建议"
                  "(禁交易/禁仓位/禁收益承诺)")

# 快照纪律守卫组件(P-D-04: 以 os.path.join 拼装比对,源码零连续字面量)
_RAW_DIR_GUARD = ("data", "daily")

_METRIC_REF_CACHE = {}


# ══ 基础件 ═════════════════════════════════════════════════════════════

def _parse_iso_date(s):
    """规范 YYYY-MM-DD 解析;非法→None(调用方决定 fail 或缺席)。

    规范形守卫(WP-C P-C 先例/R040 续段教训承接): 截断候选须为十位带杠形
    (第 5/8 位为 -)才入 date.fromisoformat——Python 3.11+ 起 fromisoformat
    扩收 ISO 8601 基本式(如 20261031)与周形,纯判定随解释器版本漂移
    (本地 3.9 拒/CI 3.11 收);守卫使任一版本行为与登记口径「规范
    YYYY-MM-DD」一致(P-D-17)。"""
    if not isinstance(s, str):
        return None
    t = s.strip()[:10]
    if len(t) != 10 or t[4] != "-" or t[7] != "-":
        return None
    try:
        return date.fromisoformat(t).isoformat()
    except ValueError:
        return None


def _require_iso_date(s, name):
    got = _parse_iso_date(s)
    if got is None:
        raise ValueError(f"{name} 须为规范 YYYY-MM-DD: {s!r}")
    return got


def _now_date_iso():
    return datetime.now().date().isoformat()


def _reject_raw_data_path(path, name):
    """快照纪律路径守卫(P-D-04/AC-07.1): 路径含 data+daily 相邻目录组件
    →ValueError fail-loud(禁直读原始采集档;经正式产物/状态文件/配置
    转递不在此限)。组件以 os.path.join 形拼装比对,源码零连续字面量。"""
    norm = os.path.normpath(os.path.abspath(str(path)))
    parts = norm.split(os.sep)
    for i in range(len(parts) - 1):
        if parts[i] == _RAW_DIR_GUARD[0] and parts[i + 1] == _RAW_DIR_GUARD[1]:
            raise ValueError(
                f"{name} 指向原始采集档目录(快照纪律禁直读,DESIGN §3.1/"
                f"AC-07.1;统计取数须经正式产物[发布状态认定]): {path!r}")
    return norm


def _ymd_to_iso(ymd):
    """ymd(YYYYMMDD)→ISO 日期串;非 8 位数字→ValueError fail-loud。"""
    s = str(ymd)
    if len(s) != 8 or not s.isdigit():
        raise ValueError(f"ymd 须为 8 位数字串(YYYYMMDD): {ymd!r}")
    iso = f"{s[:4]}-{s[4:6]}-{s[6:8]}"
    return _require_iso_date(iso, "ymd")


def window_bounds(as_of, window_kind):
    """统计窗口边界(P-D-02): monthly=[as_of 所在月首日, as_of];
    quarterly=[as_of 所在季度首日, as_of];闭区间(as_of 居中=部分期如实
    呈现)。window_kind 非法→ValueError fail-loud。"""
    end = _require_iso_date(as_of, "as_of")
    if window_kind not in WINDOW_KINDS:
        raise ValueError(f"window_kind 须为 {WINDOW_KINDS}: {window_kind!r}")
    d = date.fromisoformat(end)
    if window_kind == "monthly":
        start = date(d.year, d.month, 1)
    else:   # quarterly
        start = date(d.year, 3 * ((d.month - 1) // 3) + 1, 1)
    return start.isoformat(), end


# ══ DP/参数自检哨兵(要点②「先登记后运行、禁回改」运行期面) ═══════════

def registered_dp_values():
    """DP-7/DP-8 登记定值(活性常量);测试/审计与 REPORT §零.4 登记值对照锚。"""
    return {"DP-7": f"{DP7_DIMENSION_SET}_dims+{DP7_THRESHOLD_ISSUE}_thresholds",
            "DP-8": DP8_INJECTION_POLICY}


def registered_param_values():
    """行内登记型参数活性值(P-D-02/09/10/13);测试字面量三方一致对照锚。"""
    return {
        "dimension_keys": tuple(DIMENSION_KEYS),
        "threshold_gate_b_pass_rate_min":
            THRESHOLDS["numeric_quality.gate_b_pass_rate_min"],
        "threshold_mean_core_coverage_min":
            THRESHOLDS["coverage.mean_core_coverage_min"],
        "threshold_hit_rate_min":
            THRESHOLDS["prediction_quality.hit_rate_min"],
        "threshold_on_time_rate_min":
            THRESHOLDS["timeliness.on_time_rate_min"],
        "threshold_unexplained_contrary_attention":
            THRESHOLDS[
                "argument_completeness.unexplained_contrary_attention_threshold"],
        "dimension_status": tuple(DIMENSION_STATUS),
        "window_kinds": tuple(WINDOW_KINDS),
        "stats_schema_version": STATS_SCHEMA_VERSION,
    }


def dp_selfcheck():
    """活性常量 vs 模块内登记镜像一致性哨兵;运行后回改任一定值→AssertionError。

    (测试侧另有字面量硬编码断言锚定 REPORT 登记值,三方一致=常量/镜像/登记;
    本哨兵提供运行期检出面,负向测试以 monkeypatch 模拟回改验证检出。)"""
    live = dict(registered_dp_values(), **registered_param_values())
    for k, v in _DP_REGISTERED.items():
        assert live.get(k) == v, (
            f"{k} 登记定值被回改: 活性={live.get(k)!r}≠登记={v!r}"
            f"(先登记后运行禁回改,REPORT §零.4)")
    for k, v in _PARAM_REGISTERED.items():
        assert live.get(k) == v, (
            f"参数 {k} 登记定值被回改: 活性={live.get(k)!r}≠登记={v!r}"
            f"(先登记后运行禁回改,REPORT §零.5)")
    assert len(DIMENSION_LABELS) == DP7_DIMENSION_SET, "维度集须 5 项(DP-7)"
    assert tuple(DIMENSION_KEYS) == tuple(sorted(DIMENSION_KEYS)), \
        "维度键词表须字典序(P-D-10)"
    assert REQUIRES_USER_CONFIRMATION is True, \
        "校准建议 requires_user_confirmation 须恒 true(DP-8 零自决,P-D-12)"
    for _k, v in THRESHOLDS.items():
        assert isinstance(v, (int, float)) and not isinstance(v, bool) \
            and 0 <= v, f"阈值定值非法: {_k}={v!r}"
    return True


# ══ 取数面(要点③: 统计取数经正式产物[发布状态认定]) ═══════════════════

def read_formal_reports(weekly_output_dir, as_of, window_kind):
    """窗内正式周报读取(只读,P-D-03): rp.scan_formal_weekly_reports 复用
    调用(发布状态认定链=rp formal_report_view 全链)+窗口过滤+正文读取。

    返回 reports_data=[{ymd,status,text}] 按 ymd 升序;非正式件(候选/
    未验证/未发布/digest 失配)在 rp 侧被拒,不入本清单。零写入。"""
    _reject_raw_data_path(weekly_output_dir, "weekly_output_dir")
    as_of = _require_iso_date(as_of, "as_of")
    w_start, w_end = window_bounds(as_of, window_kind)
    views = rp.scan_formal_weekly_reports(weekly_output_dir)   # 降序
    out = []
    for v in reversed(views):                                  # → 升序
        iso = _ymd_to_iso(v["ymd"])
        if w_start <= iso <= w_end:
            with open(v["path"], "r", encoding="utf-8") as f:
                text = f.read()
            out.append({"ymd": v["ymd"], "status": v["status"], "text": text})
    return out


def load_core_ids(core_metric_ids=None, registry_path=None):
    """core 集载入(P-D-06): 调用方注入优先;否则 registry_path 读取
    (criticality=='core' 且 status=='active');0 项→ValueError fail-loud。"""
    if core_metric_ids is not None:
        ids = [str(x) for x in core_metric_ids]
    else:
        if registry_path is None:
            raise ValueError("core 集须注入 core_metric_ids 或提供 registry_path"
                             "(P-D-06,覆盖度维度不可无 core 集计算)")
        _reject_raw_data_path(registry_path, "registry_path")
        with open(str(registry_path), "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict) or not isinstance(data.get("metrics"), list):
            raise ValueError("registry 须为携 metrics 列表的 dict"
                             f"(config/metric_registry.json 形): {registry_path!r}")
        ids = [str(m.get("metric_id")) for m in data["metrics"]
               if isinstance(m, dict)
               and m.get("criticality") == "core"
               and m.get("status") == "active"
               and m.get("metric_id") is not None]
    ids = list(dict.fromkeys(ids))          # 去重保序(确定性)
    if not ids:
        raise ValueError("core 集 0 项(覆盖度维度不可计算,fail-loud;P-D-06)")
    return tuple(ids)


# ══ 维度计量(纯函数) ═══════════════════════════════════════════════════

def _metric_ref_pattern(metric_id):
    pat = _METRIC_REF_CACHE.get(metric_id)
    if pat is None:
        pat = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(metric_id)
                         + r"(?![A-Za-z0-9_])")
        _METRIC_REF_CACHE[metric_id] = pat
    return pat


def report_coverage(text, core_ids):
    """单报告覆盖度(P-D-06): 词边界正则命中报告全文;返回命中 core id 列表
    (core_ids 序)。锚点形 macro.data.ID.value 中 ID 两侧为非字母数字下划线
    →命中;前缀同形 id(如 SYN-A1 vs SYN-A10)不误命中(负向环视)。"""
    return [mid for mid in core_ids
            if _metric_ref_pattern(mid).search(text)]


def report_argument_rows(text):
    """单报告论证行(P-D-09): ae._parse_status_block 复用解析
    THESIS_STATUS+ALLOCATION_STATUS 两块;返回行列表[{tag,row}]。
    块缺席→零行(如实,不报错不造数)。"""
    rows = []
    for tag in STATUS_BLOCK_TAGS:
        for obj in ae._parse_status_block(text, tag):
            if isinstance(obj, dict):
                rows.append({"tag": tag, "row": obj})
    return rows


def _star_of(row):
    """行级 confidence 星级(P-D-09): 非 1-5 整数→ValueError fail-loud。"""
    conf = row.get("confidence")
    if not isinstance(conf, int) or isinstance(conf, bool) \
            or not 1 <= conf <= 5:
        raise ValueError(f"状态块行 confidence 非法(须 1-5 整数): {conf!r}"
                         f"(词表非法,fail-loud;P-D-09)")
    return conf


def _unexplained_contrary_of(row):
    """行级未解释反证计数(P-D-09): contrary==True(严格布尔)且
    explained!=True 的 evidence 项数(rg L521 未解释反证封顶 3★ 规则
    触发面的正式产物可观测计数)。"""
    n = 0
    ev = row.get("evidence")
    if isinstance(ev, list):
        for e in ev:
            if isinstance(e, dict) and e.get("contrary") is True \
                    and e.get("explained") is not True:
                n += 1
    return n


def evaluate_numeric_quality(reports_data):
    """维度①数值质量(P-D-05): gate_b/gate_a/final_quality 分布+通过率/
    DEGRADED 率;n=0→率 None(NO_DATA);词表外值→ValueError fail-loud。"""
    gate_b = {g: 0 for g in rp.GATES}
    gate_a = {g: 0 for g in rp.GATES}
    final_q = {g: 0 for g in rp.GATES}
    for rec in reports_data:
        st = rec["status"]
        for vocab, field, bucket in ((rp.GATES, "gate_b", gate_b),
                                     (rp.GATES, "gate_a", gate_a),
                                     (rp.GATES, "final_quality", final_q)):
            v = st.get(field)
            if v not in vocab:
                raise ValueError(f"报告{rec['ymd']} {field}={v!r}∉{vocab}"
                                 f"(词表非法,fail-loud;P-D-05)")
            bucket[v] += 1
    n = len(reports_data)
    pass_rate = (gate_b["PASS"] / n) if n else None
    degraded_rate = (gate_b["DEGRADED"] / n) if n else None
    t_min = THRESHOLDS["numeric_quality.gate_b_pass_rate_min"]
    status = "NO_DATA" if n == 0 else (
        "ATTENTION" if pass_rate < t_min else "OK")
    return {"n_reports": n, "gate_b_counts": gate_b, "gate_a_counts": gate_a,
            "final_quality_counts": final_q, "gate_b_pass_rate": pass_rate,
            "degraded_rate": degraded_rate,
            "threshold_gate_b_pass_rate_min": t_min, "status": status}


def evaluate_coverage(reports_data, core_ids):
    """维度②覆盖度(P-D-06): per-report core 引用覆盖+均值;0 报告→
    mean None(NO_DATA);core 集 0 项已由 load_core_ids fail-loud。"""
    per = []
    for rec in reports_data:
        covered = report_coverage(rec["text"], core_ids)
        per.append({"ymd": rec["ymd"], "covered_core": len(covered),
                    "total_core": len(core_ids),
                    "coverage": len(covered) / len(core_ids)})
    n = len(per)
    mean_cov = (sum(p["coverage"] for p in per) / n) if n else None
    t_min = THRESHOLDS["coverage.mean_core_coverage_min"]
    status = "NO_DATA" if n == 0 else (
        "ATTENTION" if mean_cov < t_min else "OK")
    return {"n_reports": n, "per_report": per, "mean_coverage": mean_cov,
            "threshold_mean_core_coverage_min": t_min, "status": status}


def evaluate_prediction_quality(prediction_statistics):
    """维度③预测质量(P-D-07): prd 统计文档 counts/error_patterns/
    correct_samples/premise_class 原样承载(零重算零改写零重开窗);
    hit_rate=None(分母 0)→NO_DATA 如实缺席。"""
    if not isinstance(prediction_statistics, dict) \
            or not isinstance(prediction_statistics.get("counts"), dict):
        raise ValueError("prediction_statistics 须为 prd.review_statistics/"
                         "prediction_review_report 产出统计文档(P-D-07)")
    counts = dict(prediction_statistics["counts"])
    hit_rate = counts.get("hit_rate")
    t_min = THRESHOLDS["prediction_quality.hit_rate_min"]
    status = "NO_DATA" if hit_rate is None else (
        "ATTENTION" if hit_rate < t_min else "OK")
    return {"counts": counts,
            "error_patterns": prediction_statistics.get("error_patterns"),
            "correct_samples": prediction_statistics.get("correct_samples"),
            "premise_class": prediction_statistics.get("premise_class"),
            "hit_rate": hit_rate, "threshold_hit_rate_min": t_min,
            "status": status}


def evaluate_timeliness(reports_data):
    """维度④时效(P-D-08): on-time=generated_at 日期段==target_date
    (发布事务同日落档口径);时间戳缺席/不可解析→late_generated_at_missing
    如实单列(late 计数内,不 fail);n=0→率 None(NO_DATA)。"""
    on_time = late = missing = 0
    for rec in reports_data:
        st = rec["status"]
        target = _ymd_to_iso(rec["ymd"])
        gen = st.get("generated_at")
        gen_date = _parse_iso_date(str(gen)[:10]) if gen is not None else None
        if gen_date is None:
            missing += 1
            late += 1
        elif gen_date == target:
            on_time += 1
        else:
            late += 1
    n = len(reports_data)
    rate = (on_time / n) if n else None
    t_min = THRESHOLDS["timeliness.on_time_rate_min"]
    status = "NO_DATA" if n == 0 else (
        "ATTENTION" if rate < t_min else "OK")
    return {"n_reports": n, "on_time": on_time, "late": late,
            "late_generated_at_missing": missing, "on_time_rate": rate,
            "threshold_on_time_rate_min": t_min, "status": status}


def evaluate_argument_completeness(reports_data):
    """维度⑤论证完整度(P-D-09): 星级直方图(五桶全键)+均值+未解释反证
    事件合计;0 报告或 0 论证行→NO_DATA(计量面缺席,不硬判)。"""
    hist = {lvl: 0 for lvl in STAR_LEVELS}
    n_rows = 0
    total_stars = 0
    unexplained = 0
    for rec in reports_data:
        for item in report_argument_rows(rec["text"]):
            star = _star_of(item["row"])
            hist[str(star)] += 1
            n_rows += 1
            total_stars += star
            unexplained += _unexplained_contrary_of(item["row"])
    mean_conf = (total_stars / n_rows) if n_rows else None
    t_att = THRESHOLDS[
        "argument_completeness.unexplained_contrary_attention_threshold"]
    if len(reports_data) == 0 or n_rows == 0:
        status = "NO_DATA"
    else:
        status = "ATTENTION" if unexplained >= t_att else "OK"
    return {"n_reports": len(reports_data), "n_rows": n_rows,
            "star_histogram": hist, "mean_confidence": mean_conf,
            "unexplained_contrary_events": unexplained,
            "threshold_unexplained_contrary_attention_threshold": t_att,
            "status": status}


# ══ 质量文档装配(P-D-13) ═══════════════════════════════════════════════

def _fmt(x):
    return "N/A(分母=0,如实缺席)" if x is None else f"{x:.4f}"


def build_suggestions(attention_dimensions, hypothesis_warnings):
    """校准建议清单(P-D-12): ATTENTION 维度→建议条目+WP-C 警示→证据
    校准段权重复核建议;requires_user_confirmation 恒 true(DP-8 注入
    须用户确认,零自动执行零注入)。条目序=attention_dimensions(维度键
    字典序)后接警示条目;ID=SUG-01.. 顺序编号。"""
    proposals = {
        "numeric_quality": "数据包/锚点数值质量呈现复核建议",
        "coverage": "数据包核心指标呈现完整性复核建议",
        "prediction_quality": "预测假设生成与证据权重校准复核建议",
        "timeliness": "发布事务排程复核建议",
        "argument_completeness": "证据段权重与反证解释要求复核建议",
    }
    triggers = {
        "numeric_quality": "gate_b 通过率低于阈值(DP-7 登记值)",
        "coverage": "核心指标引用覆盖均值低于阈值(DP-7 登记值)",
        "prediction_quality": "预测命中率低于阈值(DP-7 登记值)",
        "timeliness": "按时发布率低于阈值(DP-7 登记值)",
        "argument_completeness":
            "未解释反证事件数达到阈值(DP-7 登记值)",
    }
    out = []
    seq = 1
    for dim in attention_dimensions:
        if dim not in proposals:
            raise ValueError(f"未知 ATTENTION 维度: {dim!r}(P-D-12)")
        out.append({"suggestion_id": f"{SUGGESTION_MARKER}{seq:02d}",
                    "dimension": dim, "trigger": triggers[dim],
                    "proposal": proposals[dim],
                    "requires_user_confirmation": REQUIRES_USER_CONFIRMATION,
                    "dp8": "确认权留用户"})
        seq += 1
    if hypothesis_warnings:
        out.append({
            "suggestion_id": f"{SUGGESTION_MARKER}{seq:02d}",
            "dimension": "prediction_quality",
            "trigger": f"{len(hypothesis_warnings)}条机制类别连续miss警示"
                       f"(WP-P3-C 假设生成警示清单)",
            "proposal": f"{len(hypothesis_warnings)}条机制类别连续miss警示:"
                        f"证据校准段权重复核建议",
            "requires_user_confirmation": REQUIRES_USER_CONFIRMATION,
            "dp8": "确认权留用户"})
    return out


def build_quality_document(reports_data, prediction_statistics,
                           hypothesis_warnings, as_of, window_kind,
                           core_ids):
    """质量文档装配(P-D-13;纯函数零写入): 五维评价+ATTENTION 清单+
    校准建议;reports_data=read_formal_reports 产出(窗内正式周报,
    ymd 升序);prediction_statistics/hypothesis_warnings=prd 产出原样。"""
    as_of = _require_iso_date(as_of, "as_of")
    if window_kind not in WINDOW_KINDS:
        raise ValueError(f"window_kind 须为 {WINDOW_KINDS}: {window_kind!r}")
    w_start, w_end = window_bounds(as_of, window_kind)
    p_start, p_end = prd.window_bounds(as_of)
    dimensions = {
        "argument_completeness":
            evaluate_argument_completeness(reports_data),
        "coverage": evaluate_coverage(reports_data, core_ids),
        "numeric_quality": evaluate_numeric_quality(reports_data),
        "prediction_quality":
            evaluate_prediction_quality(prediction_statistics),
        "timeliness": evaluate_timeliness(reports_data),
    }
    attention = [k for k in DIMENSION_KEYS
                 if dimensions[k]["status"] == "ATTENTION"]
    return {
        "schema_version": STATS_SCHEMA_VERSION, "note": REVIEW_NOTE,
        "as_of": as_of, "window_kind": window_kind,
        "window_start": w_start, "window_end": w_end,
        "prediction_window": {"start": p_start, "end": p_end,
                              "source": "WP-P3-C DP-5 滚动12个月(上游登记)"},
        "reports": [rec["ymd"] for rec in reports_data],
        "dimensions": dimensions,
        "attention_dimensions": attention,
        "suggestions": build_suggestions(attention, hypothesis_warnings),
    }


def dump_statistics(doc):
    """质量文档确定性序列化(P-D-13;纯函数返回字符串,零写盘)。
    全部 dict 键=字符串(零 None 键),sort_keys=True 全域适用。"""
    if not isinstance(doc, dict) \
            or doc.get("schema_version") != STATS_SCHEMA_VERSION:
        raise ValueError(f"质量文档 schema 非法(须 schema_version="
                         f"{STATS_SCHEMA_VERSION})")
    return json.dumps(doc, sort_keys=True, ensure_ascii=False, indent=1)


# ══ 简报渲染(P-D-11;零注入零回写) ═══════════════════════════════════

def _dimension_metric_line(key, d):
    if key == "numeric_quality":
        return (f"gate_b通过率={_fmt(d['gate_b_pass_rate'])}"
                f"(PASS {d['gate_b_counts']['PASS']}/{d['n_reports']}) "
                f"DEGRADED率={_fmt(d['degraded_rate'])}"
                f"(DEGRADED {d['gate_b_counts']['DEGRADED']}/{d['n_reports']}) "
                f"阈值≥{d['threshold_gate_b_pass_rate_min']}")
    if key == "coverage":
        return (f"核心覆盖均值={_fmt(d['mean_coverage'])}"
                f"({sum(p['covered_core'] for p in d['per_report'])}/"
                f"{sum(p['total_core'] for p in d['per_report'])} 命中/核心) "
                f"阈值≥{d['threshold_mean_core_coverage_min']}")
    if key == "prediction_quality":
        c = d["counts"]
        return (f"命中率={_fmt(d['hit_rate'])}"
                f"(hit {c.get('hit')}/miss {c.get('miss')},分母口径DP-6) "
                f"阈值≥{d['threshold_hit_rate_min']}")
    if key == "timeliness":
        return (f"按时率={_fmt(d['on_time_rate'])}"
                f"(on-time {d['on_time']}/{d['n_reports']},"
                f"时间戳缺席 {d['late_generated_at_missing']}) "
                f"阈值≥{d['threshold_on_time_rate_min']}")
    return (f"星级均值={_fmt(d['mean_confidence'])}({d['n_rows']}行) "
            f"未解释反证事件={d['unexplained_contrary_events']} "
            f"阈值<{d['threshold_unexplained_contrary_attention_threshold']}")


def render_quality_briefing(doc):
    """质量简报旁路渲染(P-D-11/P-D-18): 纯文本呈现,返回字符串零写入。
    零注入零回写;校准建议注入提示词须用户确认(DP-8),本渲染不执行。"""
    if not isinstance(doc, dict) or doc.get("schema_version") != \
            STATS_SCHEMA_VERSION:
        raise ValueError(f"render_quality_briefing(doc): doc 须为质量文档"
                         f" dict(schema_version={STATS_SCHEMA_VERSION})")
    lines = [
        "报告质量评价简报(旁路统计·月度/季度节奏,输入槽位)",
        f"窗口: {doc['window_start']} ~ {doc['window_end']}"
        f"({doc['window_kind']}节奏对齐 monthly_review/quarterly_outlook"
        f" 在场制度;as_of={doc['as_of']})",
        f"预测复盘窗口(DP-5,WP-P3-C 复用承载): "
        f"{doc['prediction_window']['start']} ~ "
        f"{doc['prediction_window']['end']}",
        f"窗内正式周报(发布状态认定): {len(doc['reports'])} 份"
        + (f" [{','.join(doc['reports'])}]" if doc["reports"] else ""),
    ]
    for key in DIMENSION_KEYS:
        d = doc["dimensions"][key]
        lines.append(f"[{DIMENSION_LABELS[key]}] {_dimension_metric_line(key, d)}"
                     f" → 状态={d['status']}")
    att = doc["attention_dimensions"]
    if att:
        lines.append(f"ATTENTION 清单({len(att)} 维): {','.join(att)}")
    else:
        lines.append("ATTENTION 清单: 本窗口无达阈维度(阈值=DP-7 登记值,"
                     "如实呈现)")
    sugs = doc["suggestions"]
    if sugs:
        lines.append(f"校准建议清单({len(sugs)} 条;注入提示词须用户确认[DP-8],"
                     "本包零注入零自动执行):")
        for s in sugs:
            lines.append(f"- [{s['suggestion_id']}] {s['dimension']}: "
                         f"{s['proposal']} (trigger={s['trigger']};"
                         f"requires_user_confirmation="
                         f"{s['requires_user_confirmation']})")
    else:
        lines.append("校准建议清单: 空(无 ATTENTION 维度且无机制类别警示,如实呈现)")
    lines.append(_BRIEFING_TAIL)
    return "\n".join(lines)


# ══ 便利编排面(P-D-17 唯一墙钟缺省;零写入) ═══════════════════════════

def report_quality_review(weekly_output_dir, views_path,
                          core_metric_ids=None, registry_path=None,
                          as_of=None, window_kind="monthly",
                          version_archive_dir=None):
    """编排入口: 正式周报读取(rp 发布状态认定)+预测复盘(WP-P3-C
    prediction_review_report 复用承载,views_path/archive_dir 直通只读)
    → {statistics, suggestions, briefing, prediction_review}。

    全流程零文件写入(P-D-14);路径守卫四输入面(P-D-04)。"""
    as_of = _require_iso_date(as_of or _now_date_iso(), "as_of")
    _reject_raw_data_path(views_path, "views_path")
    if version_archive_dir is not None:
        _reject_raw_data_path(version_archive_dir, "version_archive_dir")
    core_ids = load_core_ids(core_metric_ids, registry_path)
    reports_data = read_formal_reports(weekly_output_dir, as_of, window_kind)
    pred = prd.prediction_review_report(views_path, as_of=as_of,
                                        archive_dir=version_archive_dir)
    doc = build_quality_document(reports_data, pred["statistics"],
                                 pred["warnings"], as_of, window_kind,
                                 core_ids)
    briefing = render_quality_briefing(doc)
    return {"statistics": doc, "suggestions": doc["suggestions"],
            "briefing": briefing,
            "prediction_review": {"statistics": pred["statistics"],
                                  "warnings": pred["warnings"]}}


# ══ 自检入口(零写入;不落默认路径) ═════════════════════════════════════

def _selfcheck():
    ok = dp_selfcheck()
    print(f"report_quality_review selfcheck: dp_selfcheck={ok}; "
          f"dimensions={len(DIMENSION_KEYS)}; "
          f"window_kinds={','.join(WINDOW_KINDS)}; "
          f"thresholds={len(THRESHOLDS)}; "
          f"star_levels={len(STAR_LEVELS)}")
    print(REVIEW_NOTE)
    return ok


if __name__ == "__main__":
    _selfcheck()
