#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P3-WP-C 测试面: 预测复盘与错误模式统计(scripts/prediction_review.py)。

方法学(与 REPORT §零.5/§零.10 登记一致):
- 唯一数据源=本文件内合成 fixture 字面量(FX_PREDS/FX_VERSIONS;零真实数据
  引用,与 /tmp/p3-wp-c/fixture_and_golden.py 字面量逐字节一致,fixture
  一致性三方裁定=手推黄金==模块输出==上游 ae 锚定);零网络零 GLM 零凭证;
- 预期值一律字面量硬编码,**不从被测模块派生**;黄金 sha256=独立首原理
  预计算(/tmp/p3-wp-c/fixture_and_golden.py,零被测模块 import)固化,
  测试内 hashlib 首原理复算逐值相等(双源一致);
- 负向面: 参数回改 monkeypatch 检出/非法输入 fail-loud/未知词表拒绝;
- 纯度面: AST 静态扫描(import 白名单/禁网令牌/零写调用/只读 open/零
  data/daily/零 report_generator 依赖/零 load_views);
- 全部写入仅落 tempfile 沙箱;状态文件零回写(字节级 sha256 前后等值);
- 1 处 subprocess 受控用途(TestSelfcheckMain,跑 __main__ 自检入口)。
"""
import ast
import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import date

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "scripts")
sys.path.insert(0, SCRIPTS_DIR)
import allocation_engine as ae            # 上游锚(只读常量/复用面)  # noqa: E402
import research_index as rri              # PRED- 前缀锚(只读常量)  # noqa: E402
import prediction_review as pr             # 被测模块  # noqa: E402

# ══ 合成 fixture 字面量(与 /tmp/p3-wp-c/fixture_and_golden.py 逐字节一致) ═══

FX_AS_OF = "2026-10-31"
FX_W_START, FX_W_END = "2025-10-31", "2026-10-31"


def _fx_obs(d, v, hi=None, lo=None):
    o = {"obs_date": d, "value": v, "as_of": d,
         "retrieved_at": d + "T08:00:00", "source": "synthetic_fixture"}
    if hi is not None:
        o["high"] = hi
    if lo is not None:
        o["low"] = lo
    return o


FX_PREDS = [
    {"pred_id": "C01", "date_made": "2026-06-24", "asset": "美股大盘",
     "direction": "up", "horizon_weeks": 14, "deadline": "2026-09-30",
     "trigger": "SPX 收于 6000 上方", "status": "hit", "metric": "SPX",
     "comparator": ">=", "target": 6000,
     "evidence_ref": "THESIS-SYN-C01", "premise_text": "合成:大盘动能延续",
     "verify_mode": "expiry", "observations": [_fx_obs("2026-06-24", 5900),
                                                _fx_obs("2026-09-30", 6100)],
     "data_source": "synthetic", "note": "hit 样本",
     "resolved_date": "2026-09-30", "resolved_note": "到期收于 6100"},
    {"pred_id": "C02", "date_made": "2026-05-04", "asset": "美股大盘",
     "direction": "up", "horizon_weeks": 16, "deadline": "2026-08-26",
     "trigger": "SPX 收于 6200 上方", "status": "miss", "metric": "SPX",
     "comparator": ">=", "target": 6200,
     "evidence_ref": "THESIS-SYN-C02", "premise_text": "合成:误判方向",
     "verify_mode": "expiry", "observations": [_fx_obs("2026-05-04", 6100),
                                                _fx_obs("2026-08-26", 5800)],
     "data_source": "synthetic", "note": "direction_error 样本",
     "resolved_date": "2026-08-26", "resolved_note": "到期反向"},
    {"pred_id": "C03", "date_made": "2026-01-07", "asset": "美股大盘",
     "direction": "up", "horizon_weeks": 25, "deadline": "2026-06-30",
     "trigger": "SPX 收于 6500 上方", "status": "miss", "metric": "SPX",
     "comparator": ">=", "target": 6500,
     "evidence_ref": "THESIS-SYN-C03", "premise_text": "合成:方向对窗口短",
     "verify_mode": "expiry", "observations": [_fx_obs("2026-01-07", 6000),
                                                _fx_obs("2026-06-30", 6300),
                                                _fx_obs("2026-09-15", 6600)],
     "data_source": "synthetic", "note": "horizon_error 样本(窗后兑现)",
     "resolved_date": "2026-06-30", "resolved_note": "窗口内未达,窗后达标"},
    {"pred_id": "C04", "date_made": "2026-03-03", "asset": "美股科技",
     "direction": "up", "horizon_weeks": 8, "deadline": "2026-09-29",
     "trigger": "SPX 收于 6800 上方", "status": "miss", "metric": "SPX",
     "comparator": ">=", "target": 6800,
     "evidence_ref": "THESIS-SYN-C04", "premise_text": "合成:量级高估",
     "verify_mode": "expiry", "observations": [_fx_obs("2026-03-03", 6000),
                                                _fx_obs("2026-09-29", 6400)],
     "data_source": "synthetic", "note": "magnitude_error 样本",
     "resolved_date": "2026-09-29", "resolved_note": "涨幅不足"},
    {"pred_id": "C05", "date_made": "2026-05-11", "asset": "数字货币",
     "direction": "flat", "horizon_weeks": 13, "deadline": "2026-08-12",
     "trigger": "BTC 精确收于 100000", "status": "miss", "metric": "BTC",
     "comparator": "==", "target": 100000,
     "evidence_ref": "THESIS-SYN-C05", "premise_text": "合成:水平位未达",
     "verify_mode": "expiry", "observations": [_fx_obs("2026-05-11", 95000),
                                                _fx_obs("2026-08-12", 110000)],
     "data_source": "synthetic", "note": "==比较幅度样本",
     "resolved_date": "2026-08-12", "resolved_note": "未停在该水平"},
    {"pred_id": "C06", "date_made": "2026-04-01", "asset": "商品",
     "direction": "up", "horizon_weeks": 15, "deadline": "2026-07-15",
     "trigger": "定性判断", "status": "miss", "metric": "",
     "comparator": ">=", "target": 100,
     "evidence_ref": "THESIS-SYN-C06", "premise_text": "合成:定性预测",
     "verify_mode": "expiry", "observations": [_fx_obs("2026-04-01", 100),
                                                _fx_obs("2026-07-15", 110)],
     "data_source": "synthetic", "note": "规格不可计算样本",
     "resolved_date": "2026-07-15", "resolved_note": "定性,无量化规格"},
    {"pred_id": "C07", "date_made": "2026-02-02", "asset": "贵金属",
     "direction": "up", "horizon_weeks": 14, "deadline": "2026-05-13",
     "trigger": "GOLD 突破 2000", "status": "miss", "metric": "GOLD",
     "comparator": ">", "target": 2000,
     "evidence_ref": "THESIS-SYN-C07", "premise_text": "合成:观测不足",
     "verify_mode": "expiry", "observations": [_fx_obs("2026-02-02", 1900)],
     "data_source": "synthetic", "note": "窗内仅 1 条可用观测",
     "resolved_date": "2026-05-13", "resolved_note": "数据缺失"},
    {"pred_id": "C08", "date_made": "2026-01-14", "asset": "A股",
     "direction": "up", "horizon_weeks": 2, "deadline": "2026-07-29",
     "trigger": "CSI300 收于 4500 上方", "status": "inconclusive",
     "metric": "china.CSI300", "comparator": ">=", "target": 4500,
     "evidence_ref": "THESIS-SYN-C08", "premise_text": "合成:无法裁决",
     "verify_mode": "expiry", "observations": [_fx_obs("2026-01-14", 4400)],
     "data_source": "synthetic", "note": "inconclusive 样本",
     "resolved_date": "2026-07-29", "resolved_note": "关键日数据缺失"},
    {"pred_id": "C09", "date_made": "2025-11-05", "asset": "原油",
     "direction": "down", "horizon_weeks": 49, "deadline": "2026-10-14",
     "trigger": "WTI 跌破 80", "status": "not_yet_triggered", "metric": "WTI",
     "comparator": "<=", "target": 80,
     "evidence_ref": "THESIS-SYN-C09", "premise_text": "合成:前提未发生",
     "verify_mode": "expiry", "observations": [_fx_obs("2025-11-05", 75)],
     "data_source": "synthetic", "note": "前提未发生·终态(nyt 单列)"},
    {"pred_id": "C10", "date_made": "2026-09-01", "asset": "美股大盘",
     "direction": "up", "horizon_weeks": 52, "deadline": "2027-06-30",
     "trigger": "SPX 收于 7500 上方", "status": "not_yet_triggered",
     "metric": "SPX", "comparator": ">=", "target": 7500,
     "evidence_ref": "THESIS-SYN-C10", "premise_text": "合成:前提未发生未到期",
     "verify_mode": "expiry", "observations": [_fx_obs("2026-09-01", 6200)],
     "data_source": "synthetic", "note": "nyt 未到期(pending)"},
    {"pred_id": "C11", "date_made": "2026-10-01", "asset": "数字货币",
     "direction": "up", "horizon_weeks": 8, "deadline": "2026-12-15",
     "trigger": "BTC 收于 150000 上方", "status": "observing", "metric": "BTC",
     "comparator": ">=", "target": 150000,
     "evidence_ref": "THESIS-SYN-C11", "premise_text": "合成:观察中",
     "verify_mode": "expiry", "observations": [_fx_obs("2026-10-01", 130000)],
     "data_source": "synthetic", "note": "observing(pending)"},
    {"pred_id": "C12", "date_made": "2025-01-08", "asset": "贵金属",
     "direction": "up", "horizon_weeks": 24, "deadline": "2025-06-25",
     "trigger": "GOLD 收于 2500 上方", "status": "hit", "metric": "GOLD",
     "comparator": ">=", "target": 2500,
     "evidence_ref": "THESIS-SYN-C12", "premise_text": "合成:窗外样本",
     "verify_mode": "expiry", "observations": [_fx_obs("2025-01-08", 2000),
                                                _fx_obs("2025-06-25", 2600)],
     "data_source": "synthetic", "note": "窗外终态不计入统计",
     "resolved_date": "2025-06-25", "resolved_note": "窗外命中"},
    {"pred_id": "C13", "date_made": "2026-04-08", "asset": "数字货币",
     "direction": "up", "horizon_weeks": 9, "deadline": "2026-07-08",
     "trigger": "BTC 收于 120000 上方", "status": "miss", "metric": "BTC",
     "comparator": ">=", "target": 120000,
     "evidence_ref": "THESIS-SYN-C13", "premise_text": "合成:版本链锚",
     "verify_mode": "expiry", "observations": [_fx_obs("2026-04-08", 110000),
                                                _fx_obs("2026-07-08", 115000)],
     "data_source": "synthetic", "note": "锚定=版本链 created_at"},
    {"pred_id": "C14", "date_made": "2025-12-02", "asset": "数字货币",
     "direction": "up", "horizon_weeks": 3, "deadline": "2026-03-11",
     "trigger": "BTC 收于 130000 上方", "status": "miss", "metric": "BTC",
     "comparator": ">=", "target": 130000,
     "evidence_ref": "THESIS-SYN-C14", "premise_text": "合成:对账失配",
     "verify_mode": "expiry", "observations": [_fx_obs("2025-12-02", 125000),
                                                _fx_obs("2026-03-11", 128000)],
     "data_source": "synthetic", "note": "版本链 after 与状态文件失配",
     "resolved_date": "2026-03-11", "resolved_note": "未达"},
    {"pred_id": "C15", "date_made": "2026-01-05", "asset": "数字货币",
     "direction": "up", "horizon_weeks": 13, "deadline": "2026-04-08",
     "trigger": "BTC 盘中触及 140000", "status": "miss", "metric": "BTC",
     "comparator": ">=", "target": 140000, "price_basis": "high",
     "evidence_ref": "THESIS-SYN-C15", "premise_text": "合成:盘中口径",
     "verify_mode": "touch",
     "observations": [_fx_obs("2026-01-05", 130000, hi=131000),
                      _fx_obs("2026-02-10", 135000, hi=136000),
                      _fx_obs("2026-04-08", 138000, hi=139000)],
     "data_source": "synthetic", "note": "touch/high 口径样本",
     "resolved_date": "2026-04-08", "resolved_note": "未触及"},
    {"pred_id": "C16", "date_made": "2026-02-03", "asset": "美股大盘",
     "direction": "up", "horizon_weeks": 30, "deadline": "2026-09-01",
     "trigger": "SPX 收于 7000 上方", "status": "miss", "metric": "SPX",
     "comparator": ">=", "target": 7000,
     "evidence_ref": "THESIS-SYN-C16", "premise_text": "合成:结算日缺观测",
     "verify_mode": "expiry", "observations": [_fx_obs("2026-02-03", 6200),
                                                _fx_obs("2026-08-28", 6400)],
     "data_source": "synthetic", "note": "settlement 无观测回退样本",
     "resolved_date": "2026-09-01", "resolved_note": "未达"},
    {"pred_id": "C17", "date_made": "2026-06-02", "asset": "美债",
     "direction": "down", "deadline": "2026-08-19",
     "trigger": "美债 10Y 收益率回落至 4.5 下方", "status": "hit",
     "metric": "UST10Y", "comparator": "<=", "target": 4.5,
     "evidence_ref": "THESIS-SYN-C17", "premise_text": "合成:期限轴缺席",
     "verify_mode": "expiry", "observations": [_fx_obs("2026-06-02", 4.6),
                                                _fx_obs("2026-08-19", 4.2)],
     "data_source": "synthetic", "note": "horizon_weeks 缺席样本",
     "resolved_date": "2026-08-19", "resolved_note": "如期回落"},
    {"pred_id": "C18", "date_made": "2026-07-06", "asset": "宏观通胀",
     "direction": "up", "horizon_weeks": "many", "deadline": "2026-10-13",
     "trigger": "CPI 同比突破 3.0", "status": "hit", "metric": "CPI",
     "comparator": ">", "target": 3.0,
     "evidence_ref": "THESIS-SYN-C18", "premise_text": "合成:期限轴非数值",
     "verify_mode": "expiry", "observations": [_fx_obs("2026-07-06", 2.8),
                                                _fx_obs("2026-10-13", 3.2)],
     "data_source": "synthetic", "note": "horizon_weeks 非数值样本",
     "resolved_date": "2026-10-13", "resolved_note": "如期突破"},
]

FX_VERSIONS = [
    {"record_type": "conclusion_version", "version_id": "VER-20260708-001",
     "object_type": "prediction", "object_id": "PRED-C13",
     "change_type": "status_change",
     "changes": [{"field": "status", "before": "observing", "after": "miss"}],
     "gate_basis": {"kind": "trigger", "refs": ["TRIG-SYN-1"]},
     "snapshot_id": "research_snapshot_20260708_0900_v1",
     "digest_snapshot": "aaaaaaaaaaaaaaaa",
     "created_at": "2026-07-08T18:30:00",
     "history": [{"ts": "2026-07-08T18:30:00", "note": "合成"}]},
    {"record_type": "conclusion_version", "version_id": "VER-20260615-001",
     "object_type": "prediction", "object_id": "PRED-C13",
     "change_type": "status_change",
     "changes": [{"field": "status", "before": "open", "after": "observing"}],
     "gate_basis": {"kind": "trigger", "refs": ["TRIG-SYN-0"]},
     "snapshot_id": "research_snapshot_20260615_0900_v1",
     "digest_snapshot": "bbbbbbbbbbbbbbbb",
     "created_at": "2026-06-15T09:00:00",
     "history": [{"ts": "2026-06-15T09:00:00", "note": "合成"}]},
    {"record_type": "conclusion_version", "version_id": "VER-20260801-001",
     "object_type": "prediction", "object_id": "PRED-C13",
     "change_type": "revision_proposal",
     "changes": [{"field": "note", "before": "x", "after": "y"}],
     "gate_basis": {"kind": "program_evidence", "refs": ["E-1", "E-2"]},
     "snapshot_id": "research_snapshot_20260801_0900_v1",
     "digest_snapshot": "cccccccccccccccc",
     "created_at": "2026-08-01T10:00:00",
     "history": [{"ts": "2026-08-01T10:00:00", "note": "合成"}]},
    {"record_type": "conclusion_version", "version_id": "VER-20260311-002",
     "object_type": "prediction", "object_id": "PRED-C14",
     "change_type": "status_change",
     "changes": [{"field": "status", "before": "observing",
                  "after": "inconclusive"}],
     "gate_basis": {"kind": "trigger", "refs": ["TRIG-SYN-2"]},
     "snapshot_id": "research_snapshot_20260311_0900_v1",
     "digest_snapshot": "dddddddddddddddd",
     "created_at": "2026-03-11T20:00:00",
     "history": [{"ts": "2026-03-11T20:00:00", "note": "合成"}]},
    {"record_type": "conclusion_version", "version_id": "VER-20260701-001",
     "object_type": "thesis", "object_id": "THESIS-SYN-C00",
     "change_type": "status_change",
     "changes": [{"field": "status", "before": "a", "after": "b"}],
     "gate_basis": {"kind": "trigger", "refs": ["TRIG-SYN-3"]},
     "snapshot_id": "research_snapshot_20260701_0900_v1",
     "digest_snapshot": "eeeeeeeeeeeeeeee",
     "created_at": "2026-07-01T10:00:00",
     "history": [{"ts": "2026-07-01T10:00:00", "note": "合成"}]},
]

FX_VIEWS = {"schema_version": 3, "predictions": FX_PREDS,
            "note": "合成 fixture(唯一数据源,IA-P3-WP-C)"}

# ══ 手推首原理黄金(独立预计算固化;预期值零模块派生) ═════════════════

GOLDEN_NOTE = (
    "预测复盘与错误模式统计(只读聚合,零改写历史裁决记录;滚动12个月窗口;"
    "四轴归类=方向/期限/幅度/前提类;命中率分母=hit+miss,inconclusive与"
    "not_yet_triggered终态单列不入错误分母[DP-5/DP-6 登记口径]);本统计"
    "不构成投资建议(禁交易/禁仓位/禁收益承诺)")


def _gb(count, hit=0, miss=0, inc=0, nyt=0):
    denom = hit + miss
    return {"count": count, "hit": hit, "miss": miss, "inconclusive": inc,
            "not_yet_triggered_terminal": nyt,
            "hit_rate": (hit / denom) if denom > 0 else None}


GOLDEN_DOC = {
    "schema_version": 1, "note": GOLDEN_NOTE,
    "as_of": FX_AS_OF, "window_start": FX_W_START, "window_end": FX_W_END,
    "counts": {"hit": 3, "miss": 10, "inconclusive": 1,
               "not_yet_triggered_terminal": 1, "hit_rate": 3 / 13,
               "out_of_window_terminal": 1, "non_terminal_excluded": 2},
    "error_patterns": {
        "direction_error": ["C02"], "horizon_error": ["C03"],
        "magnitude_error": ["C14", "C15", "C13", "C05", "C16", "C04"],
        "unclassifiable": ["C07", "C06"]},
    "correct_samples": ["C17", "C01", "C18"],
    "premise_class": {"inconclusive": ["C08"],
                      "not_yet_triggered_terminal": ["C09"]},
    "excluded_pending": ["C10", "C11"],
    "buckets": {
        "asset": {
            "A股": _gb(1, inc=1), "原油": _gb(1, nyt=1),
            "商品": _gb(1, miss=1), "宏观通胀": _gb(1, hit=1),
            "数字货币": _gb(4, miss=4), "美债": _gb(1, hit=1),
            "美股大盘": _gb(4, hit=1, miss=3), "美股科技": _gb(1, miss=1),
            "贵金属": _gb(1, miss=1)},
        "mechanism": {
            None: _gb(1, miss=1), "供应与库存": _gb(1, nyt=1),
            "利率与流动性": _gb(1, hit=1), "增长": _gb(6, hit=1, miss=4, inc=1),
            "资金流": _gb(4, miss=4), "通胀": _gb(1, hit=1),
            "避险与估值": _gb(1, miss=1)},
        "horizon": {
            None: _gb(2, hit=2), "3-8周": _gb(2, miss=2),
            "≤2周": _gb(1, inc=1), "≥9周": _gb(10, hit=1, miss=8, nyt=1)}},
    "discrepancies": [{"pred_id": "C14", "record_status": "miss",
                       "version_after": "inconclusive"}],
}

GOLDEN_WARNINGS = [{
    "mechanism": "资金流", "axis_label": "假设生成警示",
    "consecutive_misses": 4, "miss_pred_ids": ["C14", "C15", "C13", "C05"],
    "threshold": 3, "window_start": FX_W_START, "window_end": FX_W_END,
    "slot": "hypothesis_generation_warning_input_slot"}]

GOLDEN_BRIEFING = "\n".join([
    "预测复盘警示简报(假设生成警示清单·输入槽位)",
    f"窗口: {FX_W_START} ~ {FX_W_END}(滚动12个月,DP-5 登记口径)",
    "窗内终态: hit=3 miss=10 inconclusive=1(单列) "
    "not_yet_triggered终态=1(单列); 命中率=hit/(hit+miss)=0.2308",
    "错误模式: 方向错误=C02 | 期限错误=C03 | "
    "幅度错误=C14,C15,C13,C05,C16,C04 | 无法归类(单列)=C07,C06",
    "警示条目(机制类别末端连续miss≥3,共1条):",
    "- [资金流] 假设生成警示: 连续miss=4 样本=C14,C15,C13,C05 阈值=3 "
    "(slot=hypothesis_generation_warning_input_slot)",
    "版本链对账失配(discrepancies,如实清单,不改判): 1 条",
    "本简报为预测复盘与错误模式统计面输出,只作输入槽位(零注入零回写);"
    "不构成投资建议(禁交易/禁仓位/禁收益承诺)",
])

GOLDEN_DOC_SHA256 = ("2c40919e35d60cc9dd32939adde27504"
                    "cb12be6e33ee8d1f699bbc0b31ac5eb7")
GOLDEN_WARNINGS_SHA256 = ("a3004f5e253bc4051a9b7821cfe6f436abf"
                          "526a120a30cbe0aeed50bfbafd8c2")
GOLDEN_BRIEFING_SHA256 = ("7a9ec406f48c933a381d97e8474ec80b84a0"
                          "1828a5316ac014ecb46c3b63c980")

# 编排面(空版本链)黄金: discrepancies 消隐,C13 锚=deadline(同日 2026-07-08)
GOLDEN_ORCH_DOC = copy.deepcopy(GOLDEN_DOC)
GOLDEN_ORCH_DOC["discrepancies"] = []
GOLDEN_ORCH_BRIEFING = "\n".join(
    line for line in GOLDEN_BRIEFING.split("\n")
    if not line.startswith("版本链对账失配"))

_REPO_CONFIG = os.path.join(os.path.dirname(SCRIPTS_DIR), "config",
                            "allocation_views.json")


def _sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def _module_source():
    with open(os.path.join(SCRIPTS_DIR, "prediction_review.py"), "r",
              encoding="utf-8") as f:
        return f.read()


def setUpModule():
    global _CONFIG_SHA_AT_IMPORT
    with open(_REPO_CONFIG, "rb") as f:
        _CONFIG_SHA_AT_IMPORT = _sha256_bytes(f.read())


def tearDownModule():
    with open(_REPO_CONFIG, "rb") as f:
        assert _sha256_bytes(f.read()) == _CONFIG_SHA_AT_IMPORT, \
            "repo config/allocation_views.json 状态文件被改写(要点①零回写违反)"


# ══ ① 黄金首原理复算(双源一致;零模块派生) ═══════════════════════════

class TestGoldenFirstPrinciples(unittest.TestCase):

    def _canon(self, obj):
        def order(o):
            if isinstance(o, dict):
                return {k: order(o[k]) for k in sorted(
                    o, key=lambda x: (x is None, str(x)))}
            if isinstance(o, (list, tuple)):
                return [order(v) for v in o]
            return o
        return json.dumps(order(obj), ensure_ascii=False, sort_keys=False,
                          indent=1)

    def test_golden_doc_sha256_first_principles(self):
        self.assertEqual(
            _sha256_bytes(self._canon(GOLDEN_DOC).encode("utf-8")),
            GOLDEN_DOC_SHA256)

    def test_golden_warnings_sha256_first_principles(self):
        self.assertEqual(
            _sha256_bytes(json.dumps(GOLDEN_WARNINGS, ensure_ascii=False,
                                     sort_keys=True, indent=1).encode(
                                         "utf-8")),
            GOLDEN_WARNINGS_SHA256)

    def test_golden_briefing_sha256_first_principles(self):
        self.assertEqual(
            _sha256_bytes(GOLDEN_BRIEFING.encode("utf-8")),
            GOLDEN_BRIEFING_SHA256)

    def test_golden_doc_hit_rate_literal(self):
        # 首原理: 3/(3+10) 手算浮点与登记字面量一致
        self.assertEqual(GOLDEN_DOC["counts"]["hit_rate"], 3 / 13)

    def test_fixture_settlement_anchor_via_ae(self):
        # fixture 假设独立复核: 全部 expiry 截止日均为交易日(结算=当日)
        for dl, metric in [("2026-09-30", "SPX"), ("2026-08-26", "SPX"),
                           ("2026-06-30", "SPX"), ("2026-09-29", "SPX"),
                           ("2026-08-12", "BTC"), ("2026-05-13", "GOLD"),
                           ("2026-09-01", "SPX"), ("2026-08-19", "UST10Y"),
                           ("2026-10-13", "CPI"), ("2026-04-08", "BTC"),
                           ("2026-03-11", "BTC"), ("2026-07-08", "BTC"),
                           ("2025-06-25", "GOLD")]:
            self.assertEqual(
                ae.settlement_date(dl, ae.market_of_metric(metric)), dl)

    def test_fixture_mechanism_anchor_via_ae(self):
        for metric, mech in [("SPX", "增长"), ("BTC", "资金流"),
                             ("GOLD", "避险与估值"), ("WTI", "供应与库存"),
                             ("china.CSI300", "增长"),
                             ("UST10Y", "利率与流动性"), ("CPI", "通胀")]:
            self.assertEqual(ae.mechanism_of(metric), mech)


# ══ ② DP/参数登记哨兵(要点②先登记后运行禁回改) ═════════════════════

class TestDPParamRegistration(unittest.TestCase):

    def test_dp_selfcheck_pass(self):
        self.assertTrue(pr.dp_selfcheck())

    def test_registered_dp_values_literals(self):
        self.assertEqual(pr.registered_dp_values(), {
            "DP-5": "four_axis+rolling_12m",
            "DP-6": ("hit_miss_only_inconclusive_"
                     "nyt_listed_separately")})

    def test_registered_param_values_literals(self):
        self.assertEqual(pr.registered_param_values(), {
            "warning_consec_miss_threshold": 3,
            "horizon_buckets": ("≤2周:1-2", "3-8周:3-8", "≥9周:9+"),
            "result_terminal_statuses": ("hit", "miss", "inconclusive"),
            "stats_schema_version": 1})

    def test_module_constants_vs_registered(self):
        self.assertEqual(pr.DP5_ERROR_FRAMEWORK, "four_axis")
        self.assertEqual(pr.DP5_ROLLING_WINDOW_MONTHS, 12)
        self.assertEqual(pr.DP6_DENOMINATOR_SCOPE,
                         "hit_miss_only_inconclusive_nyt_listed_separately")
        self.assertEqual(pr.WARNING_CONSEC_MISS_THRESHOLD, 3)
        self.assertEqual(pr.RESULT_TERMINAL_STATUSES,
                         ("hit", "miss", "inconclusive"))
        self.assertEqual(pr.HORIZON_BUCKETS,
                         (("≤2周", 1, 2), ("3-8周", 3, 8), ("≥9周", 9, None)))
        self.assertEqual(pr.STATS_SCHEMA_VERSION, 1)
        self.assertEqual(pr.WARNING_SLOT,
                         "hypothesis_generation_warning_input_slot")
        self.assertEqual(pr.ERROR_AXES, ("direction_error", "horizon_error",
                                         "magnitude_error", "premise_class"))

    def test_monkeypatch_threshold_detected(self):
        saved = pr.WARNING_CONSEC_MISS_THRESHOLD
        try:
            pr.WARNING_CONSEC_MISS_THRESHOLD = 2
            with self.assertRaises(AssertionError):
                pr.dp_selfcheck()
        finally:
            pr.WARNING_CONSEC_MISS_THRESHOLD = saved

    def test_monkeypatch_window_months_detected(self):
        saved = pr.DP5_ROLLING_WINDOW_MONTHS
        try:
            pr.DP5_ROLLING_WINDOW_MONTHS = 6
            with self.assertRaises(AssertionError):
                pr.dp_selfcheck()
        finally:
            pr.DP5_ROLLING_WINDOW_MONTHS = saved

    def test_monkeypatch_dp6_scope_detected(self):
        saved = pr.DP6_DENOMINATOR_SCOPE
        try:
            pr.DP6_DENOMINATOR_SCOPE = "all_terminal_in_denominator"
            with self.assertRaises(AssertionError):
                pr.dp_selfcheck()
        finally:
            pr.DP6_DENOMINATOR_SCOPE = saved

    def test_monkeypatch_terminal_statuses_detected(self):
        saved = pr.RESULT_TERMINAL_STATUSES
        try:
            pr.RESULT_TERMINAL_STATUSES = ("hit", "miss")
            with self.assertRaises(AssertionError):
                pr.dp_selfcheck()
        finally:
            pr.RESULT_TERMINAL_STATUSES = saved

    def test_monkeypatch_nonmonotonic_buckets_detected(self):
        saved = pr.HORIZON_BUCKETS
        try:
            pr.HORIZON_BUCKETS = (("≤2周", 1, 2), ("3-8周", 5, 8),
                                  ("≥9周", 9, None))
            with self.assertRaises(AssertionError):
                pr.dp_selfcheck()
        finally:
            pr.HORIZON_BUCKETS = saved

    def test_monkeypatch_schema_version_detected(self):
        saved = pr.STATS_SCHEMA_VERSION
        try:
            pr.STATS_SCHEMA_VERSION = 2
            with self.assertRaises(AssertionError):
                pr.dp_selfcheck()
        finally:
            pr.STATS_SCHEMA_VERSION = saved


# ══ ③ 滚动窗口边界(DP-5 窗口半;月末日钳制) ═════════════════════════

class TestWindowBounds(unittest.TestCase):

    def test_main_window(self):
        self.assertEqual(pr.window_bounds("2026-10-31"),
                         ("2025-10-31", "2026-10-31"))

    def test_leap_month_end_clamp(self):
        self.assertEqual(pr.shift_months("2024-02-29", 12), "2023-02-28")

    def test_month_end_to_month_end(self):
        self.assertEqual(pr.shift_months("2026-03-31", 12), "2025-03-31")

    def test_cross_year_clamp(self):
        self.assertEqual(pr.shift_months("2026-01-31", 1), "2025-12-31")

    def test_zero_shift_identity(self):
        self.assertEqual(pr.shift_months("2026-10-31", 0), "2026-10-31")

    def test_bad_as_of_rejected(self):
        with self.assertRaises(ValueError):
            pr.window_bounds("2026/10/31")

    def test_negative_months_rejected(self):
        with self.assertRaises(ValueError):
            pr.shift_months("2026-10-31", -1)


# ══ ④ 终态判定(P-C-02) ═════════════════════════════════════════════

class TestTerminalState(unittest.TestCase):

    def test_result_terminals(self):
        for st in ("hit", "miss", "inconclusive"):
            self.assertEqual(
                pr.terminal_state({"pred_id": "X", "status": st}, FX_AS_OF),
                (True, st))

    def test_nyt_terminal_when_deadline_reached(self):
        self.assertEqual(pr.terminal_state(
            {"pred_id": "X", "status": "not_yet_triggered",
             "deadline": "2026-10-14"}, FX_AS_OF),
            (True, "not_yet_triggered"))

    def test_nyt_pending_when_deadline_future(self):
        self.assertEqual(pr.terminal_state(
            {"pred_id": "X", "status": "not_yet_triggered",
             "deadline": "2027-06-30"}, FX_AS_OF),
            (False, None))

    def test_nyt_deadline_equality_day_is_terminal(self):
        # deadline==as_of 当日到期→终态(闭区间语义)
        self.assertEqual(pr.terminal_state(
            {"pred_id": "X", "status": "not_yet_triggered",
             "deadline": FX_AS_OF}, FX_AS_OF),
            (True, "not_yet_triggered"))

    def test_nyt_missing_deadline_fail_loud(self):
        with self.assertRaises(ValueError):
            pr.terminal_state({"pred_id": "X", "status": "not_yet_triggered"},
                              FX_AS_OF)

    def test_pending_statuses(self):
        for st in ("observing", "open"):
            self.assertEqual(
                pr.terminal_state({"pred_id": "X", "status": st}, FX_AS_OF),
                (False, None))

    def test_unknown_status_fail_loud(self):
        with self.assertRaises(ValueError):
            pr.terminal_state({"pred_id": "X", "status": "cancelled"},
                              FX_AS_OF)

    def test_missing_status_fail_loud(self):
        with self.assertRaises(ValueError):
            pr.terminal_state({"pred_id": "X"}, FX_AS_OF)


# ══ ⑤ 终态锚定(P-C-03;版本记录供终态判定) ═════════════════════════

class TestAnchorDate(unittest.TestCase):

    def test_resolved_date_takes_priority(self):
        anchor, disc = pr.anchor_date_of(
            {"pred_id": "C14", "status": "miss",
             "resolved_date": "2026-03-11", "deadline": "2026-03-11"},
            FX_AS_OF, FX_VERSIONS)
        self.assertEqual(anchor, "2026-03-11")

    def test_version_chain_anchor_when_no_resolved(self):
        anchor, disc = pr.anchor_date_of(
            {"pred_id": "C13", "status": "miss", "deadline": "2026-07-08"},
            FX_AS_OF, FX_VERSIONS)
        self.assertEqual(anchor, "2026-07-08")   # 最新 status_change created_at

    def test_latest_status_change_selected_not_list_position(self):
        # FX_VERSIONS[0]=2026-07-08(status_change) 在 [2]=2026-08-01
        # (revision_proposal)与[1]=2026-06-15 之间取 status_change 最新者
        anchor, _ = pr.anchor_date_of(
            {"pred_id": "C13", "status": "miss", "deadline": "2026-07-08"},
            FX_AS_OF, list(reversed(FX_VERSIONS)))
        self.assertEqual(anchor, "2026-07-08")

    def test_deadline_fallback_when_no_records(self):
        anchor, disc = pr.anchor_date_of(
            {"pred_id": "C09", "status": "not_yet_triggered",
             "deadline": "2026-10-14"}, FX_AS_OF, None)
        self.assertEqual((anchor, disc), ("2026-10-14", None))

    def test_all_sources_missing_fail_loud(self):
        with self.assertRaises(ValueError):
            pr.anchor_date_of({"pred_id": "X", "status": "hit"}, FX_AS_OF, [])

    def test_discrepancy_detected(self):
        anchor, disc = pr.anchor_date_of(
            {"pred_id": "C14", "status": "miss",
             "resolved_date": "2026-03-11"}, FX_AS_OF, FX_VERSIONS)
        self.assertEqual(disc, {"pred_id": "C14", "record_status": "miss",
                                "version_after": "inconclusive"})

    def test_no_discrepancy_when_match(self):
        anchor, disc = pr.anchor_date_of(
            {"pred_id": "C13", "status": "miss", "deadline": "2026-07-08"},
            FX_AS_OF, FX_VERSIONS)
        self.assertIsNone(disc)

    def test_thesis_records_filtered(self):
        anchor, disc = pr.anchor_date_of(
            {"pred_id": "C00", "status": "miss", "deadline": "2026-02-02"},
            FX_AS_OF, FX_VERSIONS)
        self.assertEqual(anchor, "2026-02-02")   # thesis 记录不匹配→deadline

    def test_version_records_validation(self):
        p = {"pred_id": "X", "status": "hit", "resolved_date": "2026-01-01"}
        with self.assertRaises(ValueError):
            pr.anchor_date_of(p, FX_AS_OF, 42)
        with self.assertRaises(ValueError):
            pr.anchor_date_of(p, FX_AS_OF, ["not-a-dict"])
        bad = dict(FX_VERSIONS[0])
        del bad["created_at"]
        with self.assertRaises(ValueError):
            pr.anchor_date_of(p, FX_AS_OF, [bad])

    def test_none_version_records_means_empty(self):
        self.assertEqual(pr._validate_version_records(None), [])


# ══ ⑥ miss 三轴归类规则(P-C-06) ═════════════════════════════════════

class TestClassifyMiss(unittest.TestCase):

    def _row(self, pid):
        return {r["pred_id"]: r for r in pr.classify_predictions(
            FX_VIEWS, FX_AS_OF, FX_VERSIONS)[0]}[pid]

    def test_direction_error_up_pred_fell(self):
        r = self._row("C02")
        self.assertEqual(r["error_axis"], "direction_error")
        self.assertEqual(r["axis_label"], "方向错误")
        self.assertEqual(r["basis"], {
            "window": ["2026-05-04", "2026-08-26"], "price_basis": "close",
            "comparator": ">=", "target": 6200, "n_usable": 2,
            "start_v": 6100.0, "final_v": 5800.0,
            "final_source": "settlement_close", "post_deadline_hits": 0})

    def test_direction_error_down_pred_rose(self):
        p = {"pred_id": "D01", "status": "miss", "metric": "UST10Y",
             "comparator": "<=", "target": 4.0, "date_made": "2026-01-06",
             "deadline": "2026-04-08",
             "observations": [_fx_obs("2026-01-06", 4.1),
                              _fx_obs("2026-04-08", 4.4)]}
        axis, detail = pr.classify_miss(p)
        self.assertEqual(axis, "direction_error")

    def test_direction_priority_over_post_deadline_hit(self):
        # 反向+窗后达标并存→方向错误优先(C03 的对偶面)
        p = {"pred_id": "D02", "status": "miss", "metric": "SPX",
             "comparator": ">=", "target": 6200, "date_made": "2026-05-04",
             "deadline": "2026-08-26",
             "observations": [_fx_obs("2026-05-04", 6100),
                              _fx_obs("2026-08-26", 5800),
                              _fx_obs("2026-09-15", 6300)]}
        axis, detail = pr.classify_miss(p)
        self.assertEqual((axis, detail["post_deadline_hits"]),
                         ("direction_error", 1))

    def test_horizon_error_direction_ok_realized_late(self):
        r = self._row("C03")
        self.assertEqual(r["error_axis"], "horizon_error")
        self.assertEqual(r["axis_label"], "期限错误")
        self.assertEqual(r["basis"], {
            "window": ["2026-01-07", "2026-06-30"], "price_basis": "close",
            "comparator": ">=", "target": 6500, "n_usable": 2,
            "start_v": 6000.0, "final_v": 6300.0,
            "final_source": "settlement_close", "post_deadline_hits": 1})

    def test_post_deadline_obs_not_satisfying_counts_zero(self):
        p = {"pred_id": "D03", "status": "miss", "metric": "SPX",
             "comparator": ">=", "target": 6500, "date_made": "2026-01-07",
             "deadline": "2026-06-30",
             "observations": [_fx_obs("2026-01-07", 6000),
                              _fx_obs("2026-06-30", 6300),
                              _fx_obs("2026-09-15", 6400)]}
        axis, detail = pr.classify_miss(p)
        self.assertEqual((axis, detail["post_deadline_hits"]),
                         ("magnitude_error", 0))

    def test_magnitude_error_up_rose_but_short(self):
        self.assertEqual(self._row("C04")["error_axis"], "magnitude_error")
        self.assertEqual(self._row("C04")["axis_label"], "幅度错误")

    def test_equality_comparator_no_direction_axis(self):
        self.assertEqual(self._row("C05")["error_axis"], "magnitude_error")

    def test_touch_mode_high_basis(self):
        r = self._row("C15")
        self.assertEqual(r["error_axis"], "magnitude_error")
        self.assertEqual(r["basis"], {
            "window": ["2026-01-05", "2026-04-08"], "price_basis": "high",
            "comparator": ">=", "target": 140000, "n_usable": 3,
            "start_v": 131000.0, "final_v": 139000.0,
            "final_source": "last_window_observation",
            "post_deadline_hits": 0})

    def test_expiry_settlement_fallback_last_window_obs(self):
        r = self._row("C16")
        self.assertEqual(r["basis"]["final_source"],
                         "last_window_observation_fallback")
        self.assertEqual(r["basis"]["final_v"], 6400.0)

    def test_spec_not_computable_no_metric(self):
        r = self._row("C06")
        self.assertIsNone(r["error_axis"])
        self.assertEqual(r["basis"]["unclassifiable_reason"],
                         "spec_not_computable")

    def test_spec_not_computable_bad_comparator(self):
        p = {"pred_id": "D04", "status": "miss", "metric": "SPX",
             "comparator": "~", "target": 100, "date_made": "2026-01-06",
             "deadline": "2026-04-08",
             "observations": [_fx_obs("2026-01-06", 100),
                              _fx_obs("2026-04-08", 110)]}
        axis, detail = pr.classify_miss(p)
        self.assertEqual((axis, detail["unclassifiable_reason"]),
                         (None, "spec_not_computable"))

    def test_spec_not_computable_bool_target(self):
        p = {"pred_id": "D05", "status": "miss", "metric": "SPX",
             "comparator": ">=", "target": True, "date_made": "2026-01-06",
             "deadline": "2026-04-08",
             "observations": [_fx_obs("2026-01-06", 100),
                              _fx_obs("2026-04-08", 110)]}
        axis, detail = pr.classify_miss(p)
        self.assertEqual(detail["unclassifiable_reason"], "spec_not_computable")

    def test_insufficient_window_observations(self):
        r = self._row("C07")
        self.assertIsNone(r["error_axis"])
        self.assertEqual(r["basis"]["unclassifiable_reason"],
                         "insufficient_window_observations")
        self.assertEqual(r["basis"]["n_usable"], 1)

    def test_miss_without_deadline_fail_loud(self):
        p = {"pred_id": "D06", "status": "miss", "metric": "SPX",
             "comparator": ">=", "target": 100, "date_made": "2026-01-06",
             "observations": [_fx_obs("2026-01-06", 100),
                              _fx_obs("2026-04-08", 110)]}
        with self.assertRaises(ValueError):
            pr.classify_miss(p)

    def test_window_excludes_pre_start_observations(self):
        p = {"pred_id": "D07", "status": "miss", "metric": "SPX",
             "comparator": ">=", "target": 6800, "date_made": "2026-03-03",
             "deadline": "2026-09-29",
             "observations": [_fx_obs("2026-01-02", 7000),   # 窗外(早于 date_made)
                              _fx_obs("2026-03-03", 6000),
                              _fx_obs("2026-09-29", 6400)]}
        axis, detail = pr.classify_miss(p)
        self.assertEqual((detail["n_usable"], detail["start_v"]),
                         (2, 6000.0))


# ══ ⑦ 归类行(P-C-05) ════════════════════════════════════════════════

class TestClassifyRows(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.rows, cls.discs = pr.classify_predictions(
            FX_VIEWS, FX_AS_OF, FX_VERSIONS)
        cls.by_id = {r["pred_id"]: r for r in cls.rows}

    def test_row_count_and_keys(self):
        self.assertEqual(len(self.rows), 18)
        for r in self.rows:
            self.assertEqual(sorted(r.keys()), sorted(pr._ROW_KEYS))

    def test_row_order_is_input_order(self):
        self.assertEqual([r["pred_id"] for r in self.rows],
                         [p["pred_id"] for p in FX_PREDS])

    def test_hit_sample_row(self):
        r = self.by_id["C01"]
        self.assertEqual((r["category"], r["error_axis"], r["in_window"]),
                         ("hit_sample", None, True))

    def test_pending_rows(self):
        for pid in ("C10", "C11"):
            r = self.by_id[pid]
            self.assertEqual((r["category"], r["terminal"], r["anchor_date"],
                              r["in_window"], r["error_axis"]),
                             ("pending_excluded", False, None, False, None))

    def test_premise_class_rows_dp6a(self):
        for pid in ("C08", "C09"):
            r = self.by_id[pid]
            self.assertEqual((r["category"], r["error_axis"],
                              r["axis_label"]),
                             ("premise_class", "premise_class", "前提类"))
            self.assertTrue(r["in_window"])

    def test_out_of_window_terminal_row(self):
        r = self.by_id["C12"]
        self.assertEqual((r["category"], r["terminal"], r["in_window"]),
                         ("hit_sample", True, False))

    def test_discrepancies_listed(self):
        self.assertEqual(self.discs, GOLDEN_DOC["discrepancies"])

    def test_absent_axes_as_none(self):
        self.assertIsNone(self.by_id["C06"]["mechanism"])
        self.assertIsNone(self.by_id["C17"]["horizon_bucket"])
        self.assertIsNone(self.by_id["C18"]["horizon_bucket"])
        self.assertEqual(self.by_id["C04"]["horizon_bucket"], "3-8周")
        self.assertEqual(self.by_id["C08"]["horizon_bucket"], "≤2周")
        self.assertEqual(self.by_id["C13"]["horizon_bucket"], "≥9周")


# ══ ⑧ 分桶统计黄金(P-C-07/P-C-08;DP-6 分母口径) ════════════════════

class TestStatisticsGolden(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.doc = pr.review_statistics(FX_VIEWS, FX_AS_OF, FX_VERSIONS)

    def test_full_document_equals_golden(self):
        self.assertEqual(self.doc, GOLDEN_DOC)

    def test_dump_statistics_sha256_golden(self):
        self.assertEqual(
            _sha256_bytes(pr.dump_statistics(self.doc).encode("utf-8")),
            GOLDEN_DOC_SHA256)

    def test_dump_deterministic_replay(self):
        d1 = pr.dump_statistics(pr.review_statistics(FX_VIEWS, FX_AS_OF,
                                                     FX_VERSIONS))
        d2 = pr.dump_statistics(pr.review_statistics(FX_VIEWS, FX_AS_OF,
                                                     FX_VERSIONS))
        self.assertEqual(d1, d2)

    def test_counts_fields(self):
        self.assertEqual(self.doc["counts"], GOLDEN_DOC["counts"])
        # DP-6(a) 分母口径: hit_rate=hit/(hit+miss),首原理 3/13
        self.assertEqual(self.doc["counts"]["hit_rate"],
                         self.doc["counts"]["hit"] /
                         (self.doc["counts"]["hit"] +
                          self.doc["counts"]["miss"]))

    def test_premise_class_excluded_from_error_denominator(self):
        # inconclusive 与 nyt 终态不入三轴/不入 correct_samples(DP-6(a) 单列)
        all_lists = (self.doc["error_patterns"]["direction_error"]
                     + self.doc["error_patterns"]["horizon_error"]
                     + self.doc["error_patterns"]["magnitude_error"]
                     + self.doc["error_patterns"]["unclassifiable"]
                     + self.doc["correct_samples"])
        self.assertNotIn("C08", all_lists)
        self.assertNotIn("C09", all_lists)
        self.assertEqual(self.doc["premise_class"]["inconclusive"], ["C08"])
        self.assertEqual(self.doc["premise_class"]
                         ["not_yet_triggered_terminal"], ["C09"])

    def test_unclassifiable_miss_in_denominator_but_listed_separately(self):
        # P-C-05: unclassifiable miss 计入分母(状态面 miss 事实)但三轴外单列
        self.assertIn("C06", self.doc["error_patterns"]["unclassifiable"])
        self.assertEqual(self.doc["buckets"]["asset"]["商品"]["miss"], 1)
        self.assertEqual(self.doc["buckets"]["mechanism"][None]["miss"], 1)
        self.assertEqual(self.doc["counts"]["miss"], 10)

    def test_buckets_asset_golden(self):
        self.assertEqual(self.doc["buckets"]["asset"],
                         GOLDEN_DOC["buckets"]["asset"])

    def test_buckets_mechanism_golden_none_key_first(self):
        self.assertEqual(self.doc["buckets"]["mechanism"],
                         GOLDEN_DOC["buckets"]["mechanism"])
        self.assertIn(None, self.doc["buckets"]["mechanism"])

    def test_buckets_horizon_golden(self):
        self.assertEqual(self.doc["buckets"]["horizon"],
                         GOLDEN_DOC["buckets"]["horizon"])

    def test_empty_predictions_document(self):
        doc = pr.review_statistics({"predictions": []}, FX_AS_OF, None)
        self.assertEqual(doc["counts"], {
            "hit": 0, "miss": 0, "inconclusive": 0,
            "not_yet_triggered_terminal": 0, "hit_rate": None,
            "out_of_window_terminal": 0, "non_terminal_excluded": 0})
        self.assertEqual(doc["error_patterns"], {
            "direction_error": [], "horizon_error": [], "magnitude_error": [],
            "unclassifiable": []})
        self.assertEqual(doc["buckets"], {"asset": {}, "mechanism": {},
                                          "horizon": {}})
        self.assertEqual(doc["excluded_pending"], [])

    def test_zero_denominator_hit_rate_none(self):
        doc = pr.review_statistics({"predictions": [FX_PREDS[7]]},  # 仅 C08
                                   FX_AS_OF, None)
        self.assertIsNone(doc["counts"]["hit_rate"])

    def test_dump_rejects_wrong_schema(self):
        with self.assertRaises(ValueError):
            pr.dump_statistics({"schema_version": 99})


# ══ ⑨ 警示清单(P-C-09;阈值 3 登记定值) ═════════════════════════════

class TestHypothesisWarnings(unittest.TestCase):

    def test_main_fixture_golden(self):
        rows, _ = pr.classify_predictions(FX_VIEWS, FX_AS_OF, FX_VERSIONS)
        self.assertEqual(pr.hypothesis_warnings(rows, FX_AS_OF),
                         GOLDEN_WARNINGS)

    def test_run_exactly_three_fires(self):
        preds = [p for p in FX_PREDS if p["pred_id"] != "C05"]
        rows, _ = pr.classify_predictions({"predictions": preds}, FX_AS_OF,
                                          FX_VERSIONS)
        warns = pr.hypothesis_warnings(rows, FX_AS_OF)
        self.assertEqual(len(warns), 1)
        self.assertEqual((warns[0]["consecutive_misses"],
                          warns[0]["miss_pred_ids"]), (3,
                                                       ["C14", "C15", "C13"]))

    def test_run_two_does_not_fire(self):
        preds = [p for p in FX_PREDS if p["pred_id"] not in ("C05", "C13")]
        rows, _ = pr.classify_predictions({"predictions": preds}, FX_AS_OF,
                                          FX_VERSIONS)
        self.assertEqual(pr.hypothesis_warnings(rows, FX_AS_OF), [])

    def test_trailing_hit_breaks_run(self):
        preds = copy.deepcopy(FX_PREDS)
        for p in preds:
            if p["pred_id"] == "C13":
                p["status"] = "hit"     # 锚 07-08 落 C15 与 C05 之间打断游程
        rows, _ = pr.classify_predictions({"predictions": preds}, FX_AS_OF,
                                          FX_VERSIONS)
        self.assertEqual(pr.hypothesis_warnings(rows, FX_AS_OF), [])

    def test_premise_class_rows_never_form_groups(self):
        preds = [copy.deepcopy(p) for p in FX_PREDS[:1]]   # C01(hit) 占位
        for i, dl in enumerate(("2026-07-01", "2026-07-02", "2026-07-03")):
            preds.append({"pred_id": f"N{i}", "date_made": "2026-01-06",
                          "asset": "数字货币", "horizon_weeks": 10,
                          "deadline": dl, "trigger": "合成", "metric": "BTC",
                          "comparator": ">=", "target": 200000,
                          "status": "not_yet_triggered",
                          "observations": [_fx_obs("2026-01-06", 130000)]})
        rows, _ = pr.classify_predictions({"predictions": preds}, FX_AS_OF,
                                          None)
        self.assertEqual(pr.hypothesis_warnings(rows, FX_AS_OF), [])

    def test_unclassifiable_miss_participates_in_run(self):
        preds = [copy.deepcopy(FX_PREDS[6])]   # C07 miss 无法归类 GOLD 避险
        for i, (dl, tgt) in enumerate((("2026-06-10", 2200),
                                       ("2026-07-20", 2300))):
            preds.append({"pred_id": f"U{i}", "date_made": "2026-02-02",
                          "asset": "贵金属", "horizon_weeks": 12,
                          "deadline": dl, "trigger": "合成", "metric": "GOLD",
                          "comparator": ">", "target": tgt, "status": "miss",
                          "observations": [_fx_obs("2026-02-02", 2100)],
                          "resolved_date": dl})
        rows, _ = pr.classify_predictions({"predictions": preds}, FX_AS_OF,
                                          None)
        warns = pr.hypothesis_warnings(rows, FX_AS_OF)
        self.assertEqual(len(warns), 1)
        self.assertEqual(warns[0]["miss_pred_ids"], ["C07", "U0", "U1"])

    def test_threshold_sentinel_not_read_from_caller(self):
        rows, _ = pr.classify_predictions(FX_VIEWS, FX_AS_OF, FX_VERSIONS)
        saved = pr.WARNING_CONSEC_MISS_THRESHOLD
        try:
            pr.WARNING_CONSEC_MISS_THRESHOLD = 5
            self.assertEqual(pr.hypothesis_warnings(rows, FX_AS_OF), [])
        finally:
            pr.WARNING_CONSEC_MISS_THRESHOLD = saved

    def test_bad_as_of_rejected(self):
        with self.assertRaises(ValueError):
            pr.hypothesis_warnings([], "2026/10/31")


# ══ ⑩ 简报渲染(P-C-09/P-C-14) ══════════════════════════════════════

class TestRenderBriefing(unittest.TestCase):

    def test_main_fixture_golden(self):
        doc = pr.review_statistics(FX_VIEWS, FX_AS_OF, FX_VERSIONS)
        self.assertEqual(pr.render_warning_briefing(doc, GOLDEN_WARNINGS),
                         GOLDEN_BRIEFING)

    def test_no_warnings_variant(self):
        doc = pr.review_statistics(FX_VIEWS, FX_AS_OF, FX_VERSIONS)
        text = pr.render_warning_briefing(doc, [])
        self.assertIn("警示条目: 本窗口无达阈值机制类别(阈值=3,如实呈现)",
                      text)
        self.assertNotIn("[资金流]", text)

    def test_zero_denominator_na_rendering(self):
        doc = pr.review_statistics({"predictions": [FX_PREDS[7]]}, FX_AS_OF,
                                   None)
        text = pr.render_warning_briefing(doc, [])
        self.assertIn("命中率=hit/(hit+miss)=N/A(分母=0,如实缺席)", text)

    def test_no_discrepancy_line_when_empty(self):
        doc = pr.review_statistics(FX_VIEWS, FX_AS_OF, None)  # 空版本链
        self.assertEqual(doc["discrepancies"], [])
        text = pr.render_warning_briefing(doc, GOLDEN_WARNINGS)
        self.assertNotIn("版本链对账失配", text)

    def test_disclaimer_tail_line(self):
        doc = pr.review_statistics(FX_VIEWS, FX_AS_OF, FX_VERSIONS)
        text = pr.render_warning_briefing(doc, GOLDEN_WARNINGS)
        self.assertTrue(text.endswith(
            "不构成投资建议(禁交易/禁仓位/禁收益承诺)"))

    def test_bad_args_rejected(self):
        doc = pr.review_statistics({"predictions": []}, FX_AS_OF, None)
        with self.assertRaises(ValueError):
            pr.render_warning_briefing("not-a-doc", [])
        with self.assertRaises(ValueError):
            pr.render_warning_briefing(doc, "not-a-list")


# ══ ⑪ 只读零写入(P-C-10;要点①) ═════════════════════════════════════

class TestZeroWrite(unittest.TestCase):

    def test_views_file_bytes_unchanged_after_report(self):
        with tempfile.TemporaryDirectory() as td:
            vp = os.path.join(td, "allocation_views.json")
            payload = json.dumps(FX_VIEWS, ensure_ascii=False, indent=1)
            with open(vp, "w", encoding="utf-8") as f:
                f.write(payload)
            with open(vp, "rb") as f:
                before = _sha256_bytes(f.read())
            out = pr.prediction_review_report(vp, as_of=FX_AS_OF,
                                              archive_dir=os.path.join(
                                                  td, "no_such_archive"))
            with open(vp, "rb") as f:
                after = _sha256_bytes(f.read())
            self.assertEqual(before, after)
            self.assertEqual(out["statistics"]["counts"]["hit"], 3)

    def test_archive_dir_not_created(self):
        with tempfile.TemporaryDirectory() as td:
            arch = os.path.join(td, "no_such_archive")
            pr.prediction_review_report(
                self._write_views(td), as_of=FX_AS_OF, archive_dir=arch)
            self.assertFalse(os.path.exists(arch))

    def test_no_files_created_in_sandbox(self):
        with tempfile.TemporaryDirectory() as td:
            self._write_views(td)
            pr.review_statistics(FX_VIEWS, FX_AS_OF, FX_VERSIONS)
            pr.dump_statistics(GOLDEN_DOC)
            self.assertEqual(os.listdir(td), ["allocation_views.json"])

    def test_input_fixture_dicts_not_mutated(self):
        preds_before = json.dumps(FX_PREDS, sort_keys=True)
        vers_before = json.dumps(FX_VERSIONS, sort_keys=True)
        pr.review_statistics(FX_VIEWS, FX_AS_OF, FX_VERSIONS)
        self.assertEqual(json.dumps(FX_PREDS, sort_keys=True), preds_before)
        self.assertEqual(json.dumps(FX_VERSIONS, sort_keys=True),
                         vers_before)

    @staticmethod
    def _write_views(td):
        vp = os.path.join(td, "allocation_views.json")
        with open(vp, "w", encoding="utf-8") as f:
            json.dump(FX_VIEWS, f, ensure_ascii=False)
        return vp


# ══ ⑫ 编排面(P-C-13;唯一墙钟缺省) ═════════════════════════════════

class TestOrchestrator(unittest.TestCase):

    def test_report_equals_golden_with_empty_chain(self):
        with tempfile.TemporaryDirectory() as td:
            vp = TestZeroWrite._write_views(td)
            out = pr.prediction_review_report(
                vp, as_of=FX_AS_OF,
                archive_dir=os.path.join(td, "absent"))
            self.assertEqual(out["statistics"], GOLDEN_ORCH_DOC)
            self.assertEqual(out["warnings"], GOLDEN_WARNINGS)
            self.assertEqual(out["briefing"], GOLDEN_ORCH_BRIEFING)

    def test_report_matches_direct_injected_call(self):
        with tempfile.TemporaryDirectory() as td:
            vp = TestZeroWrite._write_views(td)
            out = pr.prediction_review_report(
                vp, as_of=FX_AS_OF, archive_dir=os.path.join(td, "absent"))
            with open(vp, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            self.assertEqual(out["statistics"], pr.review_statistics(
                loaded, FX_AS_OF, []))

    def test_as_of_default_is_wall_clock_today(self):
        with tempfile.TemporaryDirectory() as td:
            vp = TestZeroWrite._write_views(td)
            out = pr.prediction_review_report(vp,
                                              archive_dir=os.path.join(
                                                  td, "absent"))
            self.assertEqual(out["statistics"]["as_of"],
                             date.today().isoformat())

    def test_bad_as_of_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            vp = TestZeroWrite._write_views(td)
            with self.assertRaises(ValueError):
                pr.prediction_review_report(vp, as_of="20261031")

    def test_missing_views_file_fail_loud(self):
        with self.assertRaises(FileNotFoundError):
            pr.prediction_review_report("/nonexistent/views.json",
                                        as_of=FX_AS_OF)

    def test_malformed_json_fail_loud(self):
        with tempfile.TemporaryDirectory() as td:
            vp = os.path.join(td, "bad.json")
            with open(vp, "w", encoding="utf-8") as f:
                f.write("{not json")
            with self.assertRaises(json.JSONDecodeError):
                pr.prediction_review_report(vp, as_of=FX_AS_OF)

    def test_views_without_predictions_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            vp = os.path.join(td, "views.json")
            with open(vp, "w", encoding="utf-8") as f:
                json.dump({"schema_version": 3}, f)
            with self.assertRaises(ValueError):
                pr.prediction_review_report(vp, as_of=FX_AS_OF)


# ══ ⑬ 静态纯度(P-C-12;AST 面) ══════════════════════════════════════

class TestStaticPurity(unittest.TestCase):

    def _tree_and_strings(self):
        tree = ast.parse(_module_source())
        docs = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef,
                                 ast.ClassDef)):
                body = node.body
                if (body and isinstance(body[0], ast.Expr)
                        and isinstance(body[0].value, ast.Str)):
                    docs.add(body[0].value.s)
        strings = [n.s for n in ast.walk(tree)
                   if isinstance(n, ast.Str) and n.s not in docs]
        return tree, strings, docs

    def test_import_whitelist(self):
        tree = ast.parse(_module_source())
        roots = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                roots.add(node.module.split(".")[0])
        self.assertEqual(roots, {"json", "os", "sys", "datetime",
                                 "allocation_engine", "research_index"})

    def test_no_network_or_process_faces(self):
        tree = ast.parse(_module_source())
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                src = ast.dump(node)
                for banned in ("urllib", "requests", "socket", "http",
                               "httpx", "subprocess", "shutil", "tempfile"):
                    self.assertNotIn(banned, src, f"禁入依赖: {src}")

    def test_open_calls_read_only(self):
        tree = ast.parse(_module_source())
        opens = [n for n in ast.walk(tree)
                 if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Name) and n.func.id == "open"]
        self.assertTrue(opens, "模块须有只读 open(编排面状态文件直载)")
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
        _, strings, _ = self._tree_and_strings()
        joined = "\n".join(strings)
        for banned in ("data/daily", "report_generator", "load_views",
                       "/Users/cast", "https://", "http://"):
            self.assertNotIn(banned, joined)

    def test_source_compiles(self):
        compile(_module_source(), "prediction_review.py", "exec")


# ══ ⑭ 负向输入(P-C-02/P-C-03/P-C-10 fail-loud) ═════════════════════

class TestNegativeInputs(unittest.TestCase):

    def test_views_not_dict_rejected(self):
        with self.assertRaises(ValueError):
            pr.classify_predictions(["not", "a", "dict"], FX_AS_OF, None)

    def test_predictions_missing_rejected(self):
        with self.assertRaises(ValueError):
            pr.classify_predictions({"theses": []}, FX_AS_OF, None)

    def test_predictions_not_list_rejected(self):
        with self.assertRaises(ValueError):
            pr.classify_predictions({"predictions": "no"}, FX_AS_OF, None)

    def test_pred_not_dict_rejected(self):
        with self.assertRaises(ValueError):
            pr.classify_predictions({"predictions": ["x"]}, FX_AS_OF, None)

    def test_pred_without_id_rejected(self):
        with self.assertRaises(ValueError):
            pr.classify_predictions({"predictions": [{"status": "hit"}]},
                                    FX_AS_OF, None)

    def test_bad_as_of_rejected(self):
        with self.assertRaises(ValueError):
            pr.classify_predictions(FX_VIEWS, "2026-13-01", None)

    def test_version_records_wrong_type_rejected(self):
        with self.assertRaises(ValueError):
            pr.review_statistics(FX_VIEWS, FX_AS_OF, version_records={})


# ══ ⑮ __main__ 自检入口(P-C-15;1 处受控 subprocess) ════════════════

class TestSelfcheckMain(unittest.TestCase):

    def test_selfcheck_exit_zero_with_sentinels(self):
        proc = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS_DIR,
                                          "prediction_review.py")],
            capture_output=True, text=True, cwd=os.path.dirname(SCRIPTS_DIR),
            timeout=60)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("dp_selfcheck=True", proc.stdout)
        self.assertIn("axes=4; window_months=12; warning_threshold=3;"
                      " horizon_buckets=3", proc.stdout)
        self.assertIn("不构成投资建议", proc.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=1)
