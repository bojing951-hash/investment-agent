#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P3-WP-D 测试面: 报告质量评价循环(scripts/report_quality_review.py)。

方法学(与 REPORT §零.5 登记一致;WP-C 家族同款):
- 唯一数据源=本文件内合成 fixture 字面量(周报正文+状态 JSON+预测状态文件;
  零真实数据引用,与 /tmp/p3-wp-d/fixture_and_golden.py 字面量逐字节一致,
  fixture 一致性三方裁定=手推黄金==模块输出==首原理 sha256 复算);
- 预期值一律字面量硬编码,**不从被测模块派生**;黄金 sha256=独立首原理
  预计算(/tmp/p3-wp-d/fixture_and_golden.py,零被测模块 import)固化,
  测试内 hashlib 首原理复算逐值相等(双源一致);
- 负向面: 参数回改 monkeypatch 检出/非法输入 fail-loud/快照纪律路径守卫;
- 纯度面: AST 静态扫描(import 白名单/禁网令牌/零写调用/只读 open/零连续
  data/daily 字面量/禁上游主流程模块 import);
- 全部写入仅落 tempfile 沙箱;周报/状态文件/上游模块字节级 sha256 前后
  等值(零回写);1 处 subprocess 受控用途(TestSelfcheckMain)。
"""
import ast
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "scripts")
REPO_ROOT = os.path.dirname(SCRIPTS_DIR)
sys.path.insert(0, SCRIPTS_DIR)
import prediction_review as prd             # 上游复用面(WP-P3-C)  # noqa: E402
import report_quality_review as rqr         # 被测模块  # noqa: E402
import research_provenance as rp            # 上游复用面(发布状态认定)  # noqa: E402

# ══ 合成 fixture 字面量(与 /tmp/p3-wp-d/fixture_and_golden.py 逐字节一致) ═══

FX_AS_OF = "2026-11-30"
FX_PRED_W = ("2025-11-30", "2026-11-30")       # prd DP-5 滚动12个月
FX_MONTH_W = ("2026-11-01", "2026-11-30")      # WP-D monthly
FX_QUART_W = ("2026-10-01", "2026-11-30")      # WP-D quarterly(Q4)
FX_CORE_IDS = ("SYN-A1", "SYN-A2", "SYN-A3", "SYN-A4", "SYN-A5", "SYN-A6")


def _fx_obs(d, v):
    return {"obs_date": d, "value": v, "as_of": d, "retrieved_at": d + "T08:00:00",
            "source": "synthetic_fixture"}


FX_PREDS = [
    # D01 hit | SPX>=6000 | 增长 | hw14→≥9周 | anchor=resolved 2026-09-30(窗内)
    {"pred_id": "D01", "date_made": "2026-06-24", "asset": "美股大盘",
     "direction": "up", "horizon_weeks": 14, "deadline": "2026-09-30",
     "trigger": "SPX 收于 6000 上方", "status": "hit", "metric": "SPX",
     "comparator": ">=", "target": 6000,
     "evidence_ref": "THESIS-SYN-D01", "premise_text": "合成:大盘动能延续",
     "verify_mode": "expiry", "observations": [_fx_obs("2026-06-24", 5900),
                                                _fx_obs("2026-09-30", 6100)],
     "data_source": "synthetic", "note": "hit 样本",
     "resolved_date": "2026-09-30", "resolved_note": "到期收于 6100"},
    # D02 hit | GOLD>=2500 | 避险与估值 | hw11→≥9周 | anchor=resolved 2026-08-19
    {"pred_id": "D02", "date_made": "2026-06-02", "asset": "贵金属",
     "direction": "up", "horizon_weeks": 11, "deadline": "2026-08-19",
     "trigger": "GOLD 收于 2500 上方", "status": "hit", "metric": "GOLD",
     "comparator": ">=", "target": 2500,
     "evidence_ref": "THESIS-SYN-D02", "premise_text": "合成:避险延续",
     "verify_mode": "expiry", "observations": [_fx_obs("2026-06-02", 2400),
                                                _fx_obs("2026-08-19", 2550)],
     "data_source": "synthetic", "note": "hit 样本",
     "resolved_date": "2026-08-19", "resolved_note": "到期收于 2550"},
    # D03 miss·方向错误 | BTC>=120000 | 资金流 | hw13→≥9周 | 118000→115000 跌
    {"pred_id": "D03", "date_made": "2026-04-08", "asset": "数字货币",
     "direction": "up", "horizon_weeks": 13, "deadline": "2026-07-08",
     "trigger": "BTC 收于 120000 上方", "status": "miss", "metric": "BTC",
     "comparator": ">=", "target": 120000,
     "evidence_ref": "THESIS-SYN-D03", "premise_text": "合成:误判方向",
     "verify_mode": "expiry", "observations": [_fx_obs("2026-04-08", 118000),
                                                _fx_obs("2026-07-08", 115000)],
     "data_source": "synthetic", "note": "direction_error 样本",
     "resolved_date": "2026-07-08", "resolved_note": "到期反向"},
    # D04 inconclusive | china.CSI300>=4500 | 增长 | hw4→3-8周 | 前提类单列
    {"pred_id": "D04", "date_made": "2026-07-01", "asset": "A股",
     "direction": "up", "horizon_weeks": 4, "deadline": "2026-07-29",
     "trigger": "CSI300 收于 4500 上方", "status": "inconclusive",
     "metric": "china.CSI300", "comparator": ">=", "target": 4500,
     "evidence_ref": "THESIS-SYN-D04", "premise_text": "合成:无法裁决",
     "verify_mode": "expiry", "observations": [_fx_obs("2026-07-01", 4400)],
     "data_source": "synthetic", "note": "inconclusive 样本",
     "resolved_date": "2026-07-29", "resolved_note": "关键日数据缺失"},
    # D05 not_yet_triggered 终态(deadline 2026-10-31≤as_of) | WTI<=80 | 供应与库存
    {"pred_id": "D05", "date_made": "2025-11-05", "asset": "原油",
     "direction": "down", "horizon_weeks": 49, "deadline": "2026-10-31",
     "trigger": "WTI 跌破 80", "status": "not_yet_triggered", "metric": "WTI",
     "comparator": "<=", "target": 80,
     "evidence_ref": "THESIS-SYN-D05", "premise_text": "合成:前提未发生",
     "verify_mode": "expiry", "observations": [_fx_obs("2025-11-05", 75)],
     "data_source": "synthetic", "note": "前提未发生·终态(nyt 单列)"},
    # D06 not_yet_triggered 未终态(deadline 2027-06-30>as_of) | pending_excluded
    {"pred_id": "D06", "date_made": "2026-09-01", "asset": "美股大盘",
     "direction": "up", "horizon_weeks": 52, "deadline": "2027-06-30",
     "trigger": "SPX 收于 7500 上方", "status": "not_yet_triggered",
     "metric": "SPX", "comparator": ">=", "target": 7500,
     "evidence_ref": "THESIS-SYN-D06", "premise_text": "合成:前提未发生未到期",
     "verify_mode": "expiry", "observations": [_fx_obs("2026-09-01", 6200)],
     "data_source": "synthetic", "note": "nyt 未到期(pending)"},
]

R_1102 = """# 合成周报 20261102(IA-P3-WP-D fixture;非真实报告)

本周合成观测: macro.data.SYN-A1.value 上行;macro.data.SYN-A2.value 持平;
macro.data.SYN-A3.value 回落。合成数据,不构成投资建议。

<!-- THESIS_STATUS
[{"thesis_id": "THESIS-SYN-D01", "statement": "合成论点一", "confidence": 3, "evidence": [{"ref": "E-SYN-1", "contrary": true, "explained": false}]},
 {"thesis_id": "THESIS-SYN-D02", "statement": "合成论点二", "confidence": 2, "evidence": []}]
 THESIS_STATUS -->

<!-- ALLOCATION_STATUS
[{"slot": "syn-equity", "view": "中性", "confidence": 4, "evidence": []}]
 ALLOCATION_STATUS -->
"""

R_1109 = """# 合成周报 20261109(IA-P3-WP-D fixture;非真实报告)

本周合成观测: macro.data.SYN-A1.value 与 macro.data.SYN-A2.value 上行,
macro.data.SYN-A3.value 持平,macro.data.SYN-A4.value 首次纳入。合成数据,
不构成投资建议。

<!-- THESIS_STATUS
[{"thesis_id": "THESIS-SYN-D03", "statement": "合成论点三", "confidence": 2, "evidence": []},
 {"thesis_id": "THESIS-SYN-D04", "statement": "合成论点四", "confidence": 3, "evidence": []}]
 THESIS_STATUS -->

<!-- ALLOCATION_STATUS
[{"slot": "syn-equity", "view": "温和积极", "confidence": 5, "evidence": []}]
 ALLOCATION_STATUS -->
"""

R_1116 = """# 合成周报 20261116(IA-P3-WP-D fixture;非真实报告)

本周合成观测: macro.data.SYN-A1.value、macro.data.SYN-A2.value、
macro.data.SYN-A3.value、macro.data.SYN-A4.value、macro.data.SYN-A5.value、
macro.data.SYN-A6.value 六项核心全覆盖。合成数据,不构成投资建议。

<!-- THESIS_STATUS
[{"thesis_id": "THESIS-SYN-D05", "statement": "合成论点五", "confidence": 1, "evidence": []},
 {"thesis_id": "THESIS-SYN-D06", "statement": "合成论点六", "confidence": 2, "evidence": [{"ref": "E-SYN-2", "contrary": true, "explained": false}, {"ref": "E-SYN-3", "contrary": true, "explained": true}]},
 {"thesis_id": "THESIS-SYN-D07", "statement": "合成论点七", "confidence": 3, "evidence": []}]
 THESIS_STATUS -->
"""

R_1123 = """# 合成周报 20261123(IA-P3-WP-D fixture;非真实报告)

本周合成观测: macro.data.SYN-A6.value 回落,其余合成指标缺席呈现。
合成数据,不构成投资建议。

<!-- ALLOCATION_STATUS
[{"slot": "syn-equity", "view": "中性", "confidence": 4, "evidence": []}]
 ALLOCATION_STATUS -->
"""

R_1026 = """# 合成周报 20261026(IA-P3-WP-D fixture;非真实报告)

本周合成观测(季度窗首周): macro.data.SYN-A1.value 上行,
macro.data.SYN-A2.value 回落。合成数据,不构成投资建议。

<!-- THESIS_STATUS
[{"thesis_id": "THESIS-SYN-D08", "statement": "合成论点八", "confidence": 5, "evidence": []}]
 THESIS_STATUS -->
"""

R_1105 = """# 合成周报 20261105(IA-P3-WP-D fixture;未发布件)

本周合成观测: macro.data.SYN-A1.value 波动。本件 published=false,
不得计入正式统计(发布状态认定面排除)。
"""

R_1112 = """# 合成周报 20261112(IA-P3-WP-D fixture;digest 失配件)

本周合成观测: macro.data.SYN-A1.value 至 macro.data.SYN-A6.value。
本件状态记录 report_digest 与实际内容不一致(发布中途被替换形),
不得计入正式统计(发布状态认定面排除)。
"""

R_CAND = """# 合成候选件 20261130(IA-P3-WP-D fixture;_CANDIDATE 名)

候选文件名 weekly_report_20261130_CANDIDATE.md 不匹配规范正式名,
rp.weekly_report_files 正则面天然排除,无对应状态文件。
"""

# (ymd, 正文, gate_a, gate_b, final_quality, published, generated_at, digest_ok)
WEEKLY_FILES = [
    ("20261102", R_1102, "PASS", "PASS", "PASS", True,
     "2026-11-02T18:05:00", True),
    ("20261109", R_1109, "PASS", "PASS", "PASS", True,
     "2026-11-09T19:40:00", True),
    ("20261116", R_1116, "DEGRADED", "DEGRADED", "DEGRADED", True,
     "2026-11-16T18:00:00", True),
    ("20261123", R_1123, "PASS", "PASS", "PASS", True,
     "2026-11-24T09:00:00", True),      # 次日落档→late
    ("20261026", R_1026, "PASS", "PASS", "PASS", True,
     "2026-10-26T18:30:00", True),      # 窗外(monthly)/窗内(quarterly)
    ("20261105", R_1105, "PASS", "PASS", "PASS", False,
     "2026-11-05T18:00:00", True),      # 未发布→排除
    ("20261112", R_1112, "PASS", "PASS", "PASS", True,
     "2026-11-12T18:00:00", False),     # digest 失配→排除
]


def _digest16(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def write_fixture(root):
    """fixture 树落盘(与 /tmp/p3-wp-d/fixture_and_golden.py write_fixture
    逐字节一致): weekly/ 9 文件+6 状态 JSON、views.json、空档案目录。"""
    weekly = os.path.join(root, "weekly")
    os.makedirs(weekly, exist_ok=True)
    os.makedirs(os.path.join(root, "archive"), exist_ok=True)
    for ymd, text, ga, gb, fq, pub, gen, ok in WEEKLY_FILES:
        fname = f"weekly_report_{ymd}.md"
        with open(os.path.join(weekly, fname), "w", encoding="utf-8") as f:
            f.write(text)
        st = {"gate_a": ga, "gate_b": gb, "final_quality": fq,
              "published": pub, "generated_at": gen,
              "report_file": fname, "target_date": ymd,
              "report_path": os.path.join(weekly, fname),
              "report_digest": _digest16(text) if ok else "0" * 16,
              "snapshot_id": f"synthetic_snapshot_{ymd}_v1"}
        with open(os.path.join(weekly, f"report_status_{ymd}.json"), "w",
                  encoding="utf-8") as f:
            json.dump(st, f, ensure_ascii=False, indent=1, sort_keys=True)
    with open(os.path.join(weekly, "weekly_report_20261130_CANDIDATE.md"),
              "w", encoding="utf-8") as f:
        f.write(R_CAND)
    views_path = os.path.join(root, "views.json")
    with open(views_path, "w", encoding="utf-8") as f:
        json.dump({"predictions": FX_PREDS}, f, ensure_ascii=False,
                  indent=1, sort_keys=True)
    return weekly, views_path, os.path.join(root, "archive")


# ══ 手推首原理黄金(与 /tmp/p3-wp-d/fixture_and_golden.py 独立孪生) ═══════

GOLDEN_PRD_NOTE = ("预测复盘与错误模式统计(只读聚合,零改写历史裁决记录;滚动12个月"
                   "窗口;四轴归类=方向/期限/幅度/前提类;命中率分母=hit+miss,"
                   "inconclusive与not_yet_triggered终态单列不入错误分母"
                   "[DP-5/DP-6 登记口径]);本统计不构成投资建议"
                   "(禁交易/禁仓位/禁收益承诺)")


def _gb(count, hit=0, miss=0, inc=0, nyt=0):
    denom = hit + miss
    return {"count": count, "hit": hit, "miss": miss, "inconclusive": inc,
            "not_yet_triggered_terminal": nyt,
            "hit_rate": (hit / denom) if denom > 0 else None}


# 窗内终态 5: hit D01(09-30),D02(08-19) | miss D03(07-08,方向错误)
#          | inc D04(07-29) | nyt 终态 D05(anchor=deadline 10-31);未决 1: D06
GOLDEN_PRD_STATISTICS = {
    "schema_version": 1,
    "note": GOLDEN_PRD_NOTE,
    "as_of": FX_AS_OF,
    "window_start": FX_PRED_W[0], "window_end": FX_PRED_W[1],
    "counts": {"hit": 2, "miss": 1, "inconclusive": 1,
               "not_yet_triggered_terminal": 1,
               "hit_rate": 2 / 3,
               "out_of_window_terminal": 0, "non_terminal_excluded": 1},
    "error_patterns": {"direction_error": ["D03"], "horizon_error": [],
                       "magnitude_error": [], "unclassifiable": []},
    "correct_samples": ["D02", "D01"],
    "premise_class": {"inconclusive": ["D04"],
                      "not_yet_triggered_terminal": ["D05"]},
    "excluded_pending": ["D06"],
    "buckets": {
        "asset": {
            "A股": _gb(1, inc=1),
            "原油": _gb(1, nyt=1),
            "数字货币": _gb(1, miss=1),
            "美股大盘": _gb(1, hit=1),
            "贵金属": _gb(1, hit=1)},
        "mechanism": {
            "增长": _gb(2, hit=1, inc=1),
            "供应与库存": _gb(1, nyt=1),
            "资金流": _gb(1, miss=1),
            "避险与估值": _gb(1, hit=1)},
        "horizon": {
            "3-8周": _gb(1, inc=1),
            "≥9周": _gb(4, hit=2, miss=1, nyt=1)}},
    "discrepancies": [],
}

GOLDEN_NOTE = ("报告质量评价循环(旁路统计,零注入零回写,周报系统主流程零改动;"
               "月度/季度节奏;评价维度5项[数值质量/覆盖度/预测质量/时效/论证"
               "完整度,DP-7 登记口径];预测质量维度经WP-P3-C复用承载[DP-5/DP-6"
               " 上游登记口径];校准建议注入提示词须用户确认[DP-8,确认权留用户]"
               ");本统计不构成投资建议(禁交易/禁仓位/禁收益承诺)")


def _dim_numeric(n, pass_n, deg_n, ga_pass, ga_deg, fq_pass, fq_deg):
    return {"n_reports": n,
            "gate_b_counts": {"PASS": pass_n, "DEGRADED": deg_n, "FAIL": 0},
            "gate_a_counts": {"PASS": ga_pass, "DEGRADED": ga_deg, "FAIL": 0},
            "final_quality_counts": {"PASS": fq_pass, "DEGRADED": fq_deg,
                                     "FAIL": 0},
            "gate_b_pass_rate": pass_n / n, "degraded_rate": deg_n / n,
            "threshold_gate_b_pass_rate_min": 0.90,
            "status": "ATTENTION" if pass_n / n < 0.90 else "OK"}


def _per(ymd, cov):
    return {"ymd": ymd, "covered_core": cov, "total_core": 6,
            "coverage": cov / 6}


def _dim_argument(n_reports, stars, unexplained):
    hist = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
    for s in stars:
        hist[str(s)] += 1
    return {"n_reports": n_reports, "n_rows": len(stars),
            "star_histogram": hist, "mean_confidence": sum(stars) / len(stars),
            "unexplained_contrary_events": unexplained,
            "threshold_unexplained_contrary_attention_threshold": 2,
            "status": "ATTENTION" if unexplained >= 2 else "OK"}


def _suggestion(seq, dim, trigger, proposal):
    return {"suggestion_id": f"SUG-{seq:02d}", "dimension": dim,
            "trigger": trigger, "proposal": proposal,
            "requires_user_confirmation": True, "dp8": "确认权留用户"}


GOLDEN_ATTENTION = ["argument_completeness", "coverage", "numeric_quality",
                    "timeliness"]
GOLDEN_SUGGESTIONS = [
    _suggestion(1, "argument_completeness",
                "未解释反证事件数达到阈值(DP-7 登记值)",
                "证据段权重与反证解释要求复核建议"),
    _suggestion(2, "coverage", "核心指标引用覆盖均值低于阈值(DP-7 登记值)",
                "数据包核心指标呈现完整性复核建议"),
    _suggestion(3, "numeric_quality", "gate_b 通过率低于阈值(DP-7 登记值)",
                "数据包/锚点数值质量呈现复核建议"),
    _suggestion(4, "timeliness", "按时发布率低于阈值(DP-7 登记值)",
                "发布事务排程复核建议"),
]


def _golden_doc(window_kind):
    monthly = window_kind == "monthly"
    reports = (["20261102", "20261109", "20261116", "20261123"] if monthly
               else ["20261026", "20261102", "20261109", "20261116",
                     "20261123"])
    n = len(reports)
    dims = {
        "argument_completeness": _dim_argument(
            n, [3, 2, 4, 2, 3, 5, 1, 2, 3, 4] if monthly
            else [3, 2, 4, 2, 3, 5, 1, 2, 3, 4, 5], 2),
        "coverage": {
            "n_reports": n,
            "per_report": ([_per("20261102", 3), _per("20261109", 4),
                            _per("20261116", 6), _per("20261123", 1)]
                           if monthly else
                           [_per("20261026", 2), _per("20261102", 3),
                            _per("20261109", 4), _per("20261116", 6),
                            _per("20261123", 1)]),
            "mean_coverage": sum(p["coverage"] for p in (
                [_per("20261102", 3), _per("20261109", 4),
                 _per("20261116", 6), _per("20261123", 1)] if monthly else
                [_per("20261026", 2), _per("20261102", 3),
                 _per("20261109", 4), _per("20261116", 6),
                 _per("20261123", 1)])) / n,   # 逐报告覆盖率均值(P-D-06 口径)
            "threshold_mean_core_coverage_min": 0.80,
            "status": "ATTENTION"},
        "numeric_quality": _dim_numeric(
            n, n - 1, 1, n - 1, 1, n - 1, 1),
        "prediction_quality": {
            "counts": dict(GOLDEN_PRD_STATISTICS["counts"]),
            "error_patterns": GOLDEN_PRD_STATISTICS["error_patterns"],
            "correct_samples": GOLDEN_PRD_STATISTICS["correct_samples"],
            "premise_class": GOLDEN_PRD_STATISTICS["premise_class"],
            "hit_rate": 2 / 3, "threshold_hit_rate_min": 0.30,
            "status": "OK"},
        "timeliness": {
            "n_reports": n, "on_time": n - 1, "late": 1,
            "late_generated_at_missing": 0, "on_time_rate": (n - 1) / n,
            "threshold_on_time_rate_min": 0.90,
            "status": "ATTENTION"},
    }
    return {
        "schema_version": 1, "note": GOLDEN_NOTE,
        "as_of": FX_AS_OF, "window_kind": window_kind,
        "window_start": FX_MONTH_W[0] if monthly else FX_QUART_W[0],
        "window_end": FX_MONTH_W[1],
        "prediction_window": {"start": FX_PRED_W[0], "end": FX_PRED_W[1],
                              "source": "WP-P3-C DP-5 滚动12个月(上游登记)"},
        "reports": reports,
        "dimensions": dims,
        "attention_dimensions": list(GOLDEN_ATTENTION),
        "suggestions": [dict(s) for s in GOLDEN_SUGGESTIONS],
    }


GOLDEN_MONTHLY_DOC = _golden_doc("monthly")
GOLDEN_QUARTERLY_DOC = _golden_doc("quarterly")

GOLDEN_MONTHLY_DOC_SHA256 = (
    "5e5e5e96161a49b104abb8031c9bef14dee56568454548d438b19059dbddd5f2")
GOLDEN_QUARTERLY_DOC_SHA256 = (
    "ff3c41fe89ba709da72f7e66d104b6c2d4369139068e6d2582484c0a65a2b4eb")
GOLDEN_PRD_STATISTICS_SHA256 = (
    "66b7cd70ce88fdbe264ceedcb7cf744251673500d5c288859fcaecf0dddd3919")
GOLDEN_SUGGESTIONS_SHA256 = (
    "80ab64e66a76912655e32bb453a7ed71eee5fcd0702a730458283d76bf54275f")
GOLDEN_MONTHLY_BRIEFING_SHA256 = (
    "3ef24d3a100bfd0c1f459c26a57a5058cfee30e615845b3d91b54dae752f020f")

GOLDEN_MONTHLY_BRIEFING = "\n".join([
    "报告质量评价简报(旁路统计·月度/季度节奏,输入槽位)",
    "窗口: 2026-11-01 ~ 2026-11-30(monthly节奏对齐 monthly_review/"
    "quarterly_outlook 在场制度;as_of=2026-11-30)",
    "预测复盘窗口(DP-5,WP-P3-C 复用承载): 2025-11-30 ~ 2026-11-30",
    "窗内正式周报(发布状态认定): 4 份 [20261102,20261109,20261116,20261123]",
    "[论证完整度] 星级均值=2.9000(10行) 未解释反证事件=2 阈值<2 → 状态=ATTENTION",
    "[覆盖度] 核心覆盖均值=0.5833(14/24 命中/核心) 阈值≥0.8 → 状态=ATTENTION",
    "[数值质量] gate_b通过率=0.7500(PASS 3/4) DEGRADED率=0.2500(DEGRADED 1/4)"
    " 阈值≥0.9 → 状态=ATTENTION",
    "[预测质量] 命中率=0.6667(hit 2/miss 1,分母口径DP-6) 阈值≥0.3 → 状态=OK",
    "[时效] 按时率=0.7500(on-time 3/4,时间戳缺席 0) 阈值≥0.9 → 状态=ATTENTION",
    "ATTENTION 清单(4 维): argument_completeness,coverage,numeric_quality,"
    "timeliness",
    "校准建议清单(4 条;注入提示词须用户确认[DP-8],本包零注入零自动执行):",
    "- [SUG-01] argument_completeness: 证据段权重与反证解释要求复核建议 "
    "(trigger=未解释反证事件数达到阈值(DP-7 登记值);"
    "requires_user_confirmation=True)",
    "- [SUG-02] coverage: 数据包核心指标呈现完整性复核建议 "
    "(trigger=核心指标引用覆盖均值低于阈值(DP-7 登记值);"
    "requires_user_confirmation=True)",
    "- [SUG-03] numeric_quality: 数据包/锚点数值质量呈现复核建议 "
    "(trigger=gate_b 通过率低于阈值(DP-7 登记值);"
    "requires_user_confirmation=True)",
    "- [SUG-04] timeliness: 发布事务排程复核建议 "
    "(trigger=按时发布率低于阈值(DP-7 登记值);requires_user_confirmation=True)",
    "本简报为报告质量评价循环面输出(旁路统计,零注入零回写,"
    "校准建议注入须用户确认[DP-8]);不构成投资建议"
    "(禁交易/禁仓位/禁收益承诺)",
])


def _sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def _module_source():
    with open(os.path.join(SCRIPTS_DIR, "report_quality_review.py"), "r",
              encoding="utf-8") as f:
        return f.read()


_UPSTREAM_GUARD_FILES = ("report_generator.py", "data_validator.py",
                         "prediction_review.py", "research_provenance.py",
                         "allocation_engine.py")
_UPSTREAM_SHA_AT_IMPORT = {}


def setUpModule():
    for name in _UPSTREAM_GUARD_FILES:
        with open(os.path.join(SCRIPTS_DIR, name), "rb") as f:
            _UPSTREAM_SHA_AT_IMPORT[name] = _sha256_bytes(f.read())
    with open(os.path.join(REPO_ROOT, "config", "metric_registry.json"),
              "rb") as f:
        _UPSTREAM_SHA_AT_IMPORT["metric_registry.json"] = \
            _sha256_bytes(f.read())


def tearDownModule():
    for name in _UPSTREAM_GUARD_FILES:
        with open(os.path.join(SCRIPTS_DIR, name), "rb") as f:
            assert _sha256_bytes(f.read()) == _UPSTREAM_SHA_AT_IMPORT[name], \
                f"上游模块 {name} 被改写(要点①零回写违反)"
    with open(os.path.join(REPO_ROOT, "config", "metric_registry.json"),
              "rb") as f:
        assert _sha256_bytes(f.read()) == \
            _UPSTREAM_SHA_AT_IMPORT["metric_registry.json"], \
            "config/metric_registry.json 被改写(要点①零回写违反)"


# ══ ① 黄金首原理复算(双源一致;零模块派生) ═══════════════════════════

class TestGoldenFirstPrinciples(unittest.TestCase):

    def _canon(self, obj):
        return json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=1)

    def test_golden_monthly_doc_sha256_first_principles(self):
        self.assertEqual(
            _sha256_bytes(self._canon(GOLDEN_MONTHLY_DOC).encode("utf-8")),
            GOLDEN_MONTHLY_DOC_SHA256)

    def test_golden_quarterly_doc_sha256_first_principles(self):
        self.assertEqual(
            _sha256_bytes(self._canon(GOLDEN_QUARTERLY_DOC).encode("utf-8")),
            GOLDEN_QUARTERLY_DOC_SHA256)

    def test_golden_prd_statistics_sha256_first_principles(self):
        def order(o):
            if isinstance(o, dict):
                return {k: order(o[k]) for k in sorted(
                    o, key=lambda x: (x is None, str(x)))}
            if isinstance(o, (list, tuple)):
                return [order(v) for v in o]
            return o
        s = json.dumps(order(GOLDEN_PRD_STATISTICS), ensure_ascii=False,
                       sort_keys=False, indent=1)
        self.assertEqual(_sha256_bytes(s.encode("utf-8")),
                         GOLDEN_PRD_STATISTICS_SHA256)

    def test_golden_suggestions_sha256_first_principles(self):
        self.assertEqual(
            _sha256_bytes(self._canon(GOLDEN_SUGGESTIONS).encode("utf-8")),
            GOLDEN_SUGGESTIONS_SHA256)

    def test_golden_briefing_sha256_first_principles(self):
        self.assertEqual(
            _sha256_bytes(GOLDEN_MONTHLY_BRIEFING.encode("utf-8")),
            GOLDEN_MONTHLY_BRIEFING_SHA256)

    def test_golden_rate_literals(self):
        # 首原理: 2/(2+1) 命中率、逐报告覆盖率均值(P-D-06 口径=先比率后均值)、
        # 29/10 星级均值
        self.assertEqual(GOLDEN_PRD_STATISTICS["counts"]["hit_rate"], 2 / 3)
        self.assertEqual(
            GOLDEN_MONTHLY_DOC["dimensions"]["coverage"]["mean_coverage"],
            (3 / 6 + 4 / 6 + 6 / 6 + 1 / 6) / 4)
        self.assertEqual(GOLDEN_MONTHLY_DOC["dimensions"]
                         ["argument_completeness"]["mean_confidence"], 29 / 10)


# ══ ② DP/参数登记定值(REPORT §零.4/§零.5;先登记后运行禁回改) ═════════

class TestDPParamRegistration(unittest.TestCase):

    def test_registered_dp_values(self):
        self.assertEqual(rqr.registered_dp_values(),
                         {"DP-7": "5_dims+first_issue_thresholds",
                          "DP-8": "user_confirmation_required"})

    def test_registered_param_values(self):
        self.assertEqual(rqr.registered_param_values(), {
            "dimension_keys": ("argument_completeness", "coverage",
                               "numeric_quality", "prediction_quality",
                               "timeliness"),
            "threshold_gate_b_pass_rate_min": 0.90,
            "threshold_mean_core_coverage_min": 0.80,
            "threshold_hit_rate_min": 0.30,
            "threshold_on_time_rate_min": 0.90,
            "threshold_unexplained_contrary_attention": 2,
            "dimension_status": ("OK", "ATTENTION", "NO_DATA"),
            "window_kinds": ("monthly", "quarterly"),
            "stats_schema_version": 1})

    def test_dp_selfcheck_passes(self):
        self.assertTrue(rqr.dp_selfcheck())

    def test_tamper_dp7_dimension_set_detected(self):
        orig = rqr.DP7_DIMENSION_SET
        try:
            rqr.DP7_DIMENSION_SET = 4
            with self.assertRaises(AssertionError):
                rqr.dp_selfcheck()
        finally:
            rqr.DP7_DIMENSION_SET = orig

    def test_tamper_threshold_detected(self):
        orig = rqr.THRESHOLDS["numeric_quality.gate_b_pass_rate_min"]
        try:
            rqr.THRESHOLDS["numeric_quality.gate_b_pass_rate_min"] = 0.5
            with self.assertRaises(AssertionError):
                rqr.dp_selfcheck()
        finally:
            rqr.THRESHOLDS["numeric_quality.gate_b_pass_rate_min"] = orig

    def test_tamper_dimension_keys_detected(self):
        orig = rqr._PARAM_REGISTERED["dimension_keys"]
        try:
            rqr._PARAM_REGISTERED["dimension_keys"] = ("a", "b")
            with self.assertRaises(AssertionError):
                rqr.dp_selfcheck()
        finally:
            rqr._PARAM_REGISTERED["dimension_keys"] = orig

    def test_requires_user_confirmation_constant_true(self):
        self.assertIs(rqr.REQUIRES_USER_CONFIRMATION, True)


# ══ ③ 统计窗口边界(P-D-02) ════════════════════════════════════════════

class TestWindowBounds(unittest.TestCase):

    def test_monthly_bounds(self):
        self.assertEqual(rqr.window_bounds("2026-11-30", "monthly"),
                         ("2026-11-01", "2026-11-30"))

    def test_quarterly_bounds(self):
        self.assertEqual(rqr.window_bounds("2026-11-30", "quarterly"),
                         ("2026-10-01", "2026-11-30"))

    def test_quarterly_rollovers(self):
        self.assertEqual(rqr.window_bounds("2026-02-15", "quarterly"),
                         ("2026-01-01", "2026-02-15"))
        self.assertEqual(rqr.window_bounds("2026-08-01", "quarterly"),
                         ("2026-07-01", "2026-08-01"))

    def test_invalid_window_kind_rejected(self):
        with self.assertRaises(ValueError):
            rqr.window_bounds("2026-11-30", "weekly")

    def test_compact_as_of_rejected(self):
        with self.assertRaises(ValueError):
            rqr.window_bounds("20261130", "monthly")


# ══ ④ 正式产物取数面(P-D-03;rp 发布状态认定复用) ═════════════════════

class TestFormalSourcing(unittest.TestCase):

    def _reports(self, td, window_kind="monthly"):
        weekly, _, _ = write_fixture(td)
        return rqr.read_formal_reports(weekly, FX_AS_OF, window_kind)

    def test_golden_monthly_four_reports_ascending(self):
        with tempfile.TemporaryDirectory() as td:
            recs = self._reports(td)
            self.assertEqual([r["ymd"] for r in recs],
                             ["20261102", "20261109", "20261116", "20261123"])

    def test_unpublished_excluded(self):
        with tempfile.TemporaryDirectory() as td:
            ymds = [r["ymd"] for r in self._reports(td)]
            self.assertNotIn("20261105", ymds)   # published=False

    def test_digest_mismatch_excluded(self):
        with tempfile.TemporaryDirectory() as td:
            ymds = [r["ymd"] for r in self._reports(td)]
            self.assertNotIn("20261112", ymds)   # report_digest 失配

    def test_candidate_filename_excluded(self):
        with tempfile.TemporaryDirectory() as td:
            weekly, _, _ = write_fixture(td)
            self.assertNotIn("20261130",
                             [v["ymd"] for v in
                              rp.scan_formal_weekly_reports(weekly)])

    def test_out_of_window_monthly_excluded_quarterly_included(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertNotIn("20261026",
                             [r["ymd"] for r in self._reports(td)])
            self.assertIn("20261026",
                          [r["ymd"] for r in self._reports(td, "quarterly")])

    def test_status_and_text_carried(self):
        with tempfile.TemporaryDirectory() as td:
            recs = self._reports(td)
            first = recs[0]
            self.assertEqual(first["status"]["gate_b"], "PASS")
            self.assertEqual(first["text"], R_1102)

    def test_empty_dir_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as td:
            empty = os.path.join(td, "weekly")
            os.makedirs(empty)
            self.assertEqual(
                rqr.read_formal_reports(empty, FX_AS_OF, "monthly"), [])


# ══ ⑤ core 集载入(P-D-06) ═════════════════════════════════════════════

class TestCoreIds(unittest.TestCase):

    def _registry(self, td):
        reg = {"registry_version": "synthetic",
               "metrics": [
                   {"metric_id": "R1", "criticality": "core",
                    "status": "active"},
                   {"metric_id": "R2", "criticality": "core",
                    "status": "retired"},
                   {"metric_id": "R3", "criticality": "secondary",
                    "status": "active"},
                   {"metric_id": "R4", "criticality": "core",
                    "status": "active"},
                   {"metric_id": "R4", "criticality": "core",
                    "status": "active"}]}
        p = os.path.join(td, "metric_registry.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump(reg, f)
        return p

    def test_injection_wins_and_dedupes(self):
        self.assertEqual(rqr.load_core_ids(["B", "A", "B", 1]),
                         ("B", "A", "1"))

    def test_empty_injection_rejected(self):
        with self.assertRaises(ValueError):
            rqr.load_core_ids([])

    def test_neither_source_rejected(self):
        with self.assertRaises(ValueError):
            rqr.load_core_ids(None, None)

    def test_registry_filters_core_active(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(rqr.load_core_ids(None, self._registry(td)),
                             ("R1", "R4"))

    def test_registry_bad_shape_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "bad.json")
            with open(p, "w", encoding="utf-8") as f:
                f.write('{"no_metrics": []}')
            with self.assertRaises(ValueError):
                rqr.load_core_ids(None, p)


# ══ ⑥ 覆盖度维度(P-D-06) ══════════════════════════════════════════════

class TestCoverage(unittest.TestCase):

    def test_report_coverage_literal_hits(self):
        self.assertEqual(rqr.report_coverage(R_1102, FX_CORE_IDS),
                         ["SYN-A1", "SYN-A2", "SYN-A3"])
        self.assertEqual(rqr.report_coverage(R_1116, FX_CORE_IDS),
                         list(FX_CORE_IDS))
        self.assertEqual(rqr.report_coverage(R_1123, FX_CORE_IDS), ["SYN-A6"])

    def test_word_boundary_no_prefix_or_suffix_hits(self):
        text = "SYN-A1X 与 XSYN-A1 与 SYN-A10 与 macro.data.SYN-A1.value"
        self.assertEqual(rqr.report_coverage(text, ("SYN-A1", "SYN-A10")),
                         ["SYN-A1", "SYN-A10"])   # 仅词边界内两处合法命中

    def test_evaluate_coverage_golden(self):
        recs = [{"ymd": "20261102", "status": {}, "text": R_1102},
                {"ymd": "20261109", "status": {}, "text": R_1109},
                {"ymd": "20261116", "status": {}, "text": R_1116},
                {"ymd": "20261123", "status": {}, "text": R_1123}]
        self.assertEqual(
            rqr.evaluate_coverage(recs, FX_CORE_IDS),
            GOLDEN_MONTHLY_DOC["dimensions"]["coverage"])

    def test_evaluate_coverage_no_data(self):
        out = rqr.evaluate_coverage([], FX_CORE_IDS)
        self.assertEqual(out["n_reports"], 0)
        self.assertIsNone(out["mean_coverage"])
        self.assertEqual(out["status"], "NO_DATA")

    def test_pattern_cache_repeat_call_consistent(self):
        a = rqr.report_coverage(R_1109, FX_CORE_IDS)
        b = rqr.report_coverage(R_1109, FX_CORE_IDS)
        self.assertEqual(a, b)
        self.assertEqual(a, ["SYN-A1", "SYN-A2", "SYN-A3", "SYN-A4"])


# ══ ⑦ 论证完整度维度(P-D-09;ae._parse_status_block 复用) ══════════════

class TestArgumentRows(unittest.TestCase):

    def _fixture_recs(self):
        return [{"ymd": "20261102", "status": {}, "text": R_1102},
                {"ymd": "20261109", "status": {}, "text": R_1109},
                {"ymd": "20261116", "status": {}, "text": R_1116},
                {"ymd": "20261123", "status": {}, "text": R_1123},
                {"ymd": "20261026", "status": {}, "text": R_1026}]

    def test_row_counts_and_tags(self):
        counts = {r["ymd"]: [(i["tag"], i["row"]["confidence"])
                             for i in
                             rqr.report_argument_rows(r["text"])]
                  for r in self._fixture_recs()}
        self.assertEqual(counts["20261102"],
                         [("THESIS_STATUS", 3), ("THESIS_STATUS", 2),
                          ("ALLOCATION_STATUS", 4)])
        self.assertEqual(counts["20261109"],
                         [("THESIS_STATUS", 2), ("THESIS_STATUS", 3),
                          ("ALLOCATION_STATUS", 5)])
        self.assertEqual(counts["20261116"],
                         [("THESIS_STATUS", 1), ("THESIS_STATUS", 2),
                          ("THESIS_STATUS", 3)])
        self.assertEqual(counts["20261123"], [("ALLOCATION_STATUS", 4)])
        self.assertEqual(counts["20261026"], [("THESIS_STATUS", 5)])

    def test_absent_blocks_zero_rows(self):
        self.assertEqual(rqr.report_argument_rows("无状态块的普通文本"), [])

    def test_star_validation_rejects_non_int_range(self):
        for bad in (True, "3", 0, 6, 3.0, None):
            with self.assertRaises(ValueError):
                rqr._star_of({"confidence": bad})

    def test_unexplained_conrary_strict_bool_semantics(self):
        row = {"confidence": 3, "evidence": [
            {"contrary": True, "explained": False},     # 计
            {"contrary": True, "explained": True},      # 已解释不计
            {"contrary": "yes", "explained": False},    # 非严格布尔不计
            {"contrary": True},                          # explained 缺席=计
            {"contrary": False, "explained": False}]}    # 非反证不计
        self.assertEqual(rqr._unexplained_contrary_of(row), 2)

    def test_evaluate_argument_golden_monthly(self):
        recs = self._fixture_recs()[:4]
        self.assertEqual(
            rqr.evaluate_argument_completeness(recs),
            GOLDEN_MONTHLY_DOC["dimensions"]["argument_completeness"])

    def test_evaluate_argument_golden_quarterly_hist(self):
        out = rqr.evaluate_argument_completeness(self._fixture_recs())
        self.assertEqual(out["n_rows"], 11)
        self.assertEqual(out["star_histogram"],
                         {"1": 1, "2": 3, "3": 3, "4": 2, "5": 2})
        self.assertEqual(out["mean_confidence"], 34 / 11)

    def test_evaluate_argument_no_data_zero_rows(self):
        out = rqr.evaluate_argument_completeness(
            [{"ymd": "20261102", "status": {}, "text": "无块"}])
        self.assertEqual(out["n_rows"], 0)
        self.assertEqual(out["status"], "NO_DATA")


# ══ ⑧ 数值质量维度(P-D-05) ════════════════════════════════════════════

class TestNumericQuality(unittest.TestCase):

    def _recs(self):
        def st(ga, gb, fq):
            return {"gate_a": ga, "gate_b": gb, "final_quality": fq}
        return [
            {"ymd": "20261102", "status": st("PASS", "PASS", "PASS"),
             "text": ""},
            {"ymd": "20261109", "status": st("PASS", "PASS", "PASS"),
             "text": ""},
            {"ymd": "20261116", "status": st("DEGRADED", "DEGRADED",
                                             "DEGRADED"), "text": ""},
            {"ymd": "20261123", "status": st("PASS", "PASS", "PASS"),
             "text": ""}]

    def test_evaluate_numeric_golden(self):
        self.assertEqual(
            rqr.evaluate_numeric_quality(self._recs()),
            GOLDEN_MONTHLY_DOC["dimensions"]["numeric_quality"])

    def test_fail_bucket_is_legal_vocab(self):
        recs = [{"ymd": "20261130",
                 "status": {"gate_a": "FAIL", "gate_b": "FAIL",
                            "final_quality": "FAIL"}, "text": ""}]
        out = rqr.evaluate_numeric_quality(recs)
        self.assertEqual(out["gate_b_counts"]["FAIL"], 1)
        self.assertEqual(out["gate_b_pass_rate"], 0.0)
        self.assertEqual(out["status"], "ATTENTION")

    def test_out_of_vocab_rejected(self):
        recs = [{"ymd": "20261130",
                 "status": {"gate_a": "PASS", "gate_b": "WEAK",
                            "final_quality": "PASS"}, "text": ""}]
        with self.assertRaises(ValueError):
            rqr.evaluate_numeric_quality(recs)

    def test_no_data(self):
        out = rqr.evaluate_numeric_quality([])
        self.assertIsNone(out["gate_b_pass_rate"])
        self.assertEqual(out["status"], "NO_DATA")


# ══ ⑨ 时效维度(P-D-08) ════════════════════════════════════════════════

class TestTimeliness(unittest.TestCase):

    def _rec(self, ymd, gen):
        return {"ymd": ymd, "status": {"generated_at": gen}, "text": ""}

    def test_evaluate_timeliness_golden(self):
        recs = [self._rec("20261102", "2026-11-02T18:05:00"),
                self._rec("20261109", "2026-11-09T19:40:00"),
                self._rec("20261116", "2026-11-16T18:00:00"),
                self._rec("20261123", "2026-11-24T09:00:00")]
        self.assertEqual(
            rqr.evaluate_timeliness(recs),
            GOLDEN_MONTHLY_DOC["dimensions"]["timeliness"])

    def test_missing_timestamp_counts_late_and_missing(self):
        out = rqr.evaluate_timeliness([self._rec("20261102", None)])
        self.assertEqual(out["late_generated_at_missing"], 1)
        self.assertEqual(out["late"], 1)
        self.assertEqual(out["on_time"], 0)

    def test_garbage_timestamp_counts_missing_not_fail(self):
        out = rqr.evaluate_timeliness([self._rec("20261102", "garbage")])
        self.assertEqual(out["late_generated_at_missing"], 1)
        self.assertEqual(out["status"], "ATTENTION")

    def test_all_on_time_ok(self):
        recs = [self._rec("20261102", "2026-11-02T23:59:00"),
                self._rec("20261109", "2026-11-09T00:01:00")]
        self.assertEqual(rqr.evaluate_timeliness(recs)["status"], "OK")

    def test_no_data(self):
        out = rqr.evaluate_timeliness([])
        self.assertIsNone(out["on_time_rate"])
        self.assertEqual(out["status"], "NO_DATA")


# ══ ⑩ 预测质量维度(P-D-07;prd 产出原样承载) ═══════════════════════════

class TestPredictionQuality(unittest.TestCase):

    def test_evaluate_prediction_golden_passthrough(self):
        self.assertEqual(
            rqr.evaluate_prediction_quality(GOLDEN_PRD_STATISTICS),
            GOLDEN_MONTHLY_DOC["dimensions"]["prediction_quality"])

    def test_ok_status_at_threshold(self):
        self.assertEqual(
            rqr.evaluate_prediction_quality(GOLDEN_PRD_STATISTICS)["status"],
            "OK")

    def test_none_hit_rate_no_data(self):
        stats = dict(GOLDEN_PRD_STATISTICS)
        stats["counts"] = {"hit": 0, "miss": 0, "inconclusive": 1,
                           "not_yet_triggered_terminal": 0, "hit_rate": None,
                           "out_of_window_terminal": 0,
                           "non_terminal_excluded": 0}
        out = rqr.evaluate_prediction_quality(stats)
        self.assertEqual(out["status"], "NO_DATA")

    def test_low_hit_rate_attention(self):
        stats = dict(GOLDEN_PRD_STATISTICS)
        stats["counts"] = {"hit": 1, "miss": 4, "inconclusive": 0,
                           "not_yet_triggered_terminal": 0,
                           "hit_rate": 0.2, "out_of_window_terminal": 0,
                           "non_terminal_excluded": 0}
        self.assertEqual(
            rqr.evaluate_prediction_quality(stats)["status"], "ATTENTION")

    def test_bad_input_rejected(self):
        with self.assertRaises(ValueError):
            rqr.evaluate_prediction_quality({"no_counts": {}})
        with self.assertRaises(ValueError):
            rqr.evaluate_prediction_quality(["not", "dict"])


# ══ ⑪ 校准建议清单(P-D-12;DP-8 确认权留用户) ═════════════════════════

class TestSuggestions(unittest.TestCase):

    def test_golden_four_suggestions(self):
        self.assertEqual(
            rqr.build_suggestions(GOLDEN_ATTENTION, []), GOLDEN_SUGGESTIONS)

    def test_warnings_append_fifth_entry(self):
        warns = [{"mechanism": "资金流", "axis_label": "假设生成警示",
                  "consecutive_misses": 3, "miss_pred_ids": ["A", "B", "C"],
                  "threshold": 3, "window_start": "2025-11-30",
                  "window_end": "2026-11-30",
                  "slot": "hypothesis_generation_warning_input_slot"}]
        out = rqr.build_suggestions(["prediction_quality"], warns)
        self.assertEqual(len(out), 2)
        fifth = out[1]
        self.assertEqual(fifth["suggestion_id"], "SUG-02")
        self.assertEqual(fifth["dimension"], "prediction_quality")
        self.assertEqual(fifth["trigger"],
                         "1条机制类别连续miss警示(WP-P3-C 假设生成警示清单)")
        self.assertEqual(fifth["proposal"],
                         "1条机制类别连续miss警示:证据校准段权重复核建议")
        self.assertIs(fifth["requires_user_confirmation"], True)

    def test_empty_attention_no_warnings_empty_list(self):
        self.assertEqual(rqr.build_suggestions([], []), [])

    def test_unknown_dimension_rejected(self):
        with self.assertRaises(ValueError):
            rqr.build_suggestions(["mystery_dim"], [])

    def test_all_entries_carry_dp8_marker(self):
        for s in rqr.build_suggestions(GOLDEN_ATTENTION,
                                       ["w1", "w2"]):
            self.assertIs(s["requires_user_confirmation"], True)
            self.assertEqual(s["dp8"], "确认权留用户")


# ══ ⑫ 质量文档装配与序列化(P-D-13) ═══════════════════════════════════

class TestDocumentAssembly(unittest.TestCase):

    def _reports_data(self, td, window_kind="monthly"):
        weekly, _, _ = write_fixture(td)
        return rqr.read_formal_reports(weekly, FX_AS_OF, window_kind)

    def test_build_quality_document_golden_monthly(self):
        with tempfile.TemporaryDirectory() as td:
            doc = rqr.build_quality_document(
                self._reports_data(td), GOLDEN_PRD_STATISTICS, [],
                FX_AS_OF, "monthly", FX_CORE_IDS)
            self.assertEqual(doc, GOLDEN_MONTHLY_DOC)

    def test_build_quality_document_golden_quarterly(self):
        with tempfile.TemporaryDirectory() as td:
            doc = rqr.build_quality_document(
                self._reports_data(td, "quarterly"), GOLDEN_PRD_STATISTICS,
                [], FX_AS_OF, "quarterly", FX_CORE_IDS)
            self.assertEqual(doc, GOLDEN_QUARTERLY_DOC)

    def test_dump_statistics_canonical_sha(self):
        self.assertEqual(
            _sha256_bytes(rqr.dump_statistics(
                GOLDEN_MONTHLY_DOC).encode("utf-8")),
            GOLDEN_MONTHLY_DOC_SHA256)

    def test_dump_statistics_rejects_bad_schema(self):
        with self.assertRaises(ValueError):
            rqr.dump_statistics({"schema_version": 99})

    def test_build_rejects_invalid_window_kind(self):
        with self.assertRaises(ValueError):
            rqr.build_quality_document([], GOLDEN_PRD_STATISTICS, [],
                                       FX_AS_OF, "weekly", FX_CORE_IDS)


# ══ ⑬ 简报渲染(P-D-11;零注入零回写) ══════════════════════════════════

class TestBriefing(unittest.TestCase):

    def test_golden_monthly_briefing_byte_equality(self):
        self.assertEqual(
            rqr.render_quality_briefing(GOLDEN_MONTHLY_DOC),
            GOLDEN_MONTHLY_BRIEFING)

    def test_quarterly_window_line_literal(self):
        b = rqr.render_quality_briefing(GOLDEN_QUARTERLY_DOC)
        self.assertIn(
            "窗口: 2026-10-01 ~ 2026-11-30(quarterly节奏对齐 "
            "monthly_review/quarterly_outlook 在场制度;as_of=2026-11-30)", b)
        self.assertIn("窗内正式周报(发布状态认定): 5 份 "
                      "[20261026,20261102,20261109,20261116,20261123]", b)

    def test_none_metric_renders_na(self):
        b = rqr.render_quality_briefing(GOLDEN_MONTHLY_DOC)
        self.assertNotIn("N/A", b)   # 黄金月度无缺席计量
        empty_doc = rqr.build_quality_document(
            [], GOLDEN_PRD_STATISTICS, [], FX_AS_OF, "monthly", FX_CORE_IDS)
        b2 = rqr.render_quality_briefing(empty_doc)
        self.assertIn("N/A(分母=0,如实缺席)", b2)
        self.assertIn("本窗口无达阈维度", b2)

    def test_disclaimer_tail_is_last_line(self):
        lines = rqr.render_quality_briefing(GOLDEN_MONTHLY_DOC).split("\n")
        self.assertEqual(
            lines[-1],
            "本简报为报告质量评价循环面输出(旁路统计,零注入零回写,"
            "校准建议注入须用户确认[DP-8]);不构成投资建议"
            "(禁交易/禁仓位/禁收益承诺)")

    def test_rejects_non_document(self):
        with self.assertRaises(ValueError):
            rqr.render_quality_briefing({"schema_version": 2})


# ══ ⑭ 零回写(P-D-14;字节级 sha256 前后等值) ══════════════════════════

class TestZeroWrite(unittest.TestCase):

    @staticmethod
    def _tree_map(root):
        out = {}
        for dirpath, _dirs, files in os.walk(root):
            for fn in files:
                p = os.path.join(dirpath, fn)
                with open(p, "rb") as f:
                    out[os.path.relpath(p, root)] = _sha256_bytes(f.read())
        return out

    def test_fixture_tree_bytes_unchanged_after_report(self):
        with tempfile.TemporaryDirectory() as td:
            weekly, views, archive = write_fixture(td)
            before = self._tree_map(td)
            rqr.report_quality_review(weekly, views,
                                      core_metric_ids=list(FX_CORE_IDS),
                                      as_of=FX_AS_OF, window_kind="monthly",
                                      version_archive_dir=archive)
            self.assertEqual(self._tree_map(td), before)

    def test_no_files_created_in_sandbox(self):
        with tempfile.TemporaryDirectory() as td:
            weekly, views, _ = write_fixture(td)
            before = set(self._tree_map(td))
            rqr.report_quality_review(weekly, views,
                                      core_metric_ids=list(FX_CORE_IDS),
                                      as_of=FX_AS_OF,
                                      version_archive_dir=os.path.join(
                                          td, "absent_archive"))
            self.assertEqual(set(self._tree_map(td)), before)
            self.assertFalse(os.path.exists(
                os.path.join(td, "absent_archive")))

    def test_input_structures_not_mutated(self):
        preds_before = json.dumps(FX_PREDS, sort_keys=True)
        stats = json.loads(json.dumps(GOLDEN_PRD_STATISTICS))
        stats_before = json.dumps(stats, sort_keys=True)
        rqr.build_quality_document([], stats, [], FX_AS_OF, "monthly",
                                   FX_CORE_IDS)
        rqr.evaluate_prediction_quality(stats)
        self.assertEqual(json.dumps(stats, sort_keys=True), stats_before)
        self.assertEqual(json.dumps(FX_PREDS, sort_keys=True), preds_before)

    def test_registry_read_only_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            reg = os.path.join(td, "reg.json")
            with open(reg, "w", encoding="utf-8") as f:
                json.dump({"metrics": [{"metric_id": "X1",
                                        "criticality": "core",
                                        "status": "active"}]}, f)
            with open(reg, "rb") as f:
                before = _sha256_bytes(f.read())
            rqr.load_core_ids(None, reg)
            with open(reg, "rb") as f:
                self.assertEqual(_sha256_bytes(f.read()), before)


# ══ ⑮ 编排面(P-D-17;唯一墙钟缺省;上游直通只读) ══════════════════════

class TestOrchestrator(unittest.TestCase):

    def test_full_report_equals_golden_monthly(self):
        with tempfile.TemporaryDirectory() as td:
            weekly, views, archive = write_fixture(td)
            out = rqr.report_quality_review(
                weekly, views, core_metric_ids=list(FX_CORE_IDS),
                as_of=FX_AS_OF, window_kind="monthly",
                version_archive_dir=archive)
            self.assertEqual(out["statistics"], GOLDEN_MONTHLY_DOC)
            self.assertEqual(out["suggestions"], GOLDEN_SUGGESTIONS)
            self.assertEqual(out["briefing"], GOLDEN_MONTHLY_BRIEFING)
            self.assertEqual(out["prediction_review"]["statistics"],
                             GOLDEN_PRD_STATISTICS)
            self.assertEqual(out["prediction_review"]["warnings"], [])

    def test_full_report_equals_golden_quarterly(self):
        with tempfile.TemporaryDirectory() as td:
            weekly, views, archive = write_fixture(td)
            out = rqr.report_quality_review(
                weekly, views, core_metric_ids=list(FX_CORE_IDS),
                as_of=FX_AS_OF, window_kind="quarterly",
                version_archive_dir=archive)
            self.assertEqual(out["statistics"], GOLDEN_QUARTERLY_DOC)

    def test_core_ids_injection_beats_registry(self):
        with tempfile.TemporaryDirectory() as td:
            weekly, views, archive = write_fixture(td)
            reg = os.path.join(td, "reg.json")
            with open(reg, "w", encoding="utf-8") as f:
                json.dump({"metrics": [{"metric_id": "SYN-A6",
                                        "criticality": "core",
                                        "status": "active"}]}, f)
            out = rqr.report_quality_review(
                weekly, views, core_metric_ids=list(FX_CORE_IDS),
                registry_path=reg, as_of=FX_AS_OF,
                version_archive_dir=archive)
            self.assertEqual(
                out["statistics"]["dimensions"]["coverage"]["per_report"][0]
                ["total_core"], 6)   # 注入 6 项而非 registry 1 项

    def test_registry_path_load_path(self):
        with tempfile.TemporaryDirectory() as td:
            weekly, views, archive = write_fixture(td)
            reg = os.path.join(td, "reg.json")
            with open(reg, "w", encoding="utf-8") as f:
                json.dump({"metrics": [{"metric_id": "SYN-A6",
                                        "criticality": "core",
                                        "status": "active"}]}, f)
            out = rqr.report_quality_review(
                weekly, views, registry_path=reg, as_of=FX_AS_OF,
                version_archive_dir=archive)
            per = out["statistics"]["dimensions"]["coverage"]["per_report"]
            self.assertTrue(all(p["total_core"] == 1 for p in per))
            self.assertEqual(per[0]["covered_core"], 0)   # 1102 无 SYN-A6

    def test_as_of_default_uses_wall_clock_monkeypatched(self):
        with tempfile.TemporaryDirectory() as td:
            weekly, views, archive = write_fixture(td)
            orig = rqr._now_date_iso
            try:
                rqr._now_date_iso = lambda: FX_AS_OF
                out = rqr.report_quality_review(
                    weekly, views, core_metric_ids=list(FX_CORE_IDS),
                    version_archive_dir=archive)
            finally:
                rqr._now_date_iso = orig
            self.assertEqual(out["statistics"], GOLDEN_MONTHLY_DOC)

    def test_invalid_window_kind_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            weekly, views, _ = write_fixture(td)
            with self.assertRaises(ValueError):
                rqr.report_quality_review(
                    weekly, views, core_metric_ids=list(FX_CORE_IDS),
                    as_of=FX_AS_OF, window_kind="weekly")


# ══ ⑯ 静态纯度(AST;import 白名单/禁网/零写/只读 open) ════════════════

class TestStaticPurity(unittest.TestCase):

    def _strings(self):
        tree = ast.parse(_module_source())
        docs = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.FunctionDef,
                                 ast.AsyncFunctionDef, ast.ClassDef)):
                body = node.body
                if (body and isinstance(body[0], ast.Expr)
                        and isinstance(body[0].value, ast.Str)):
                    docs.add(body[0].value.s)
        return [n.s for n in ast.walk(tree)
                if isinstance(n, ast.Str) and n.s not in docs]

    def test_import_whitelist(self):
        tree = ast.parse(_module_source())
        roots = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                roots.add(node.module.split(".")[0])
        self.assertEqual(roots, {"json", "os", "re", "sys", "datetime",
                                 "allocation_engine", "prediction_review",
                                 "research_provenance"})

    def test_no_network_or_process_faces(self):
        tree = ast.parse(_module_source())
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                src = ast.dump(node)
                for banned in ("urllib", "requests", "socket", "http",
                               "httpx", "subprocess", "shutil", "tempfile"):
                    self.assertNotIn(banned, src, f"禁入依赖: {src}")

    def test_upstream_mainflow_modules_not_imported(self):
        tree = ast.parse(_module_source())
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                src = ast.dump(node)
                for banned in ("report_generator", "data_validator",
                               "monthly_review", "quarterly_outlook",
                               "snapshot_builder"):
                    self.assertNotIn(banned, src, f"主流程依赖禁入: {src}")

    def test_open_calls_read_only(self):
        tree = ast.parse(_module_source())
        opens = [n for n in ast.walk(tree)
                 if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Name) and n.func.id == "open"]
        self.assertTrue(opens, "模块须有只读 open(取数面)")
        for call in opens:
            mode = None
            if len(call.args) >= 2:
                mode = getattr(call.args[1], "s", None)
            for kw in call.keywords:
                if kw.arg == "mode":
                    mode = getattr(kw.value, "s", None)
            self.assertIn(mode, (None, "r"), f"非只读 open: {ast.dump(call)}")

    def test_zero_write_calls(self):
        tree = ast.parse(_module_source())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = None
                if isinstance(node.func, ast.Name):
                    name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    name = node.func.attr
                self.assertNotIn(name, (
                    "write", "dump", "replace", "rename", "remove", "unlink",
                    "mkdir", "makedirs", "rmdir"), f"写调用面: {name}")

    def test_no_banned_strings(self):
        joined = "\n".join(self._strings())
        for banned in ("data/daily", "/Users/cast", "https://", "http://",
                       "load_views", "update_allocation_status"):
            self.assertNotIn(banned, joined)

    def test_source_compiles(self):
        compile(_module_source(), "report_quality_review.py", "exec")


# ══ ⑰ 负向输入与快照纪律守卫(P-D-04/P-D-17 fail-loud) ═════════════════

class TestNegativeInputs(unittest.TestCase):

    def _raw_path(self, td):
        p = os.path.join(td, "data", "daily")
        os.makedirs(p)
        return p

    def test_weekly_dir_raw_data_path_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                rqr.read_formal_reports(self._raw_path(td), FX_AS_OF,
                                        "monthly")

    def test_views_path_raw_data_path_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            weekly, _, _ = write_fixture(td)
            with self.assertRaises(ValueError):
                rqr.report_quality_review(
                    weekly, os.path.join(self._raw_path(td), "v.json"),
                    core_metric_ids=list(FX_CORE_IDS), as_of=FX_AS_OF)

    def test_registry_path_raw_data_path_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                rqr.load_core_ids(None, os.path.join(self._raw_path(td),
                                                     "reg.json"))

    def test_archive_dir_raw_data_path_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            weekly, views, _ = write_fixture(td)
            with self.assertRaises(ValueError):
                rqr.report_quality_review(
                    weekly, views, core_metric_ids=list(FX_CORE_IDS),
                    as_of=FX_AS_OF,
                    version_archive_dir=self._raw_path(td))

    def test_compact_as_of_rejected_everywhere(self):
        # 3.11+ 扩收形族全拒(R040 续段守卫承接;规范形收/扩收形拒)
        for bad in ("20261130", "2026-W48", "2026W48", "2026-W48-1"):
            with self.assertRaises(ValueError):
                rqr.window_bounds(bad, "monthly")
        with tempfile.TemporaryDirectory() as td:
            weekly, views, _ = write_fixture(td)
            with self.assertRaises(ValueError):
                rqr.report_quality_review(
                    weekly, views, core_metric_ids=list(FX_CORE_IDS),
                    as_of="20261130")

    def test_canonical_form_accepted(self):
        self.assertEqual(rqr._parse_iso_date("2026-11-30"), "2026-11-30")
        self.assertEqual(rqr._parse_iso_date("2026-11-30T09:30:00"),
                         "2026-11-30")

    def test_malformed_ymd_rejected(self):
        for bad in ("202611", "2026113A", 2026113, "20261100"):
            with self.assertRaises(ValueError):
                rqr._ymd_to_iso(bad)   # "20261100" 8 位但月份非法(fail-loud)


# ══ ⑱ __main__ 自检入口(P-D-19;1 处受控 subprocess) ══════════════════

class TestSelfcheckMain(unittest.TestCase):

    def test_selfcheck_exit_zero_with_sentinels(self):
        proc = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS_DIR,
                                          "report_quality_review.py")],
            capture_output=True, text=True, cwd=REPO_ROOT, timeout=60)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("dp_selfcheck=True", proc.stdout)
        self.assertIn("dimensions=5; window_kinds=monthly,quarterly;"
                      " thresholds=5; star_levels=5", proc.stdout)
        self.assertIn("不构成投资建议", proc.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=1)
