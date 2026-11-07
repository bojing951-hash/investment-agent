#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P3-WP-C: 预测复盘与错误模式统计(P3 收尾层第 3 实现包;#35 挂靠)

DESIGN docs/P3_DESIGN.md §7 WP-P3-C 行(L182-L186,基线工作树实读)确定性落地:
- 终态预测归类器(四轴,DP-5=四轴×滚动 12 个月): miss→{方向错误 direction_error
  [判断涨实际跌/反向]/期限错误 horizon_error [方向对窗口错]/幅度错误
  magnitude_error [方向对量级错]}(规格不可计算或窗内可用观测<2 条→unclassifiable
  如实单列,不硬归类);hit→正确模式样本;inconclusive/not_yet_triggered 终态→
  前提类(premise_class)单列**不入错误分母**(DP-6(a): 分母=窗内终态 hit+miss);
- 分桶统计器(§5.2 L132 按资产/机制类别/期限桶分桶): 命中率=hit÷(hit+miss)
  (分母 0→None 如实缺席不填 0);滚动窗口=12 个日历月闭区间(月末日钳制);
- 假设生成警示清单(§5.2 L134): 机制类别末端连续 miss 游程≥3(登记阈值)→警示
  条目;**只作输入槽位**(slot=hypothesis_generation_warning_input_slot)——
  本模块产出=数据结构与旁路渲染文本,零注入零回写零周报系统触碰(周报消费面
  =WP-P3-D 范围,禁提前带入);闭环不自动修改任何论点/观点/预测;
- 版本记录供终态判定(依赖列 L185,WP-P3-A 复用面): 终态锚定日期判定序=
  resolved_date→结论版本链(rri.list_conclusion_versions,object_type=prediction
  +change_type=status_change 最新记录 created_at)→deadline;版本链与状态文件
  失配→discrepancies 如实清单(状态文件=权威载体,不改判不 fail)。

只读纪律(要点①;§5.2 L132「统计为只读聚合,不改写任何历史裁决记录」): 本模块
**零文件写入面**(无写模式 open/无 os.replace/无 json.dump);状态文件只读直载
json.load(不经 ae.load_views——其读侧归一对 dict 就地变更,复盘面禁用);历史
裁决记录(observations/resolved_note/status/resolved_date 等)零改写。

对齐上游=复用调用,禁复制分叉(P-C-11): ae._window_obs/ae._obs_field_value/
ae.COMPARATORS/ae.market_of_metric/ae.settlement_date/ae.mechanism_of/
ae.MECHANISM_CATEGORIES;rri.list_conclusion_versions/rri.PREDICTION_KEY_PREFIX。

纪律: 零网络零 GLM 零凭证零付费(import 面白名单 json/os/sys/datetime+项目既有
allocation_engine/research_index);一切日期依赖纯函数显式 as_of 必填(唯一墙钟
缺省=编排面 prediction_review_report 边缘);本模块输出为预测复盘与错误模式统计
面数据,**不构成投资建议**(DESIGN §8.3 红线: 禁交易/禁仓位/禁收益承诺)。
参数登记: docs/P3_WP_C_REPORT.md §零.4/§零.5(DP-5/DP-6+P-C-01..P-C-16,先登记
后实现,运行后禁回改)。
"""
import json
import os
import sys
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import allocation_engine as ae   # 引擎读侧面(复用调用,只读禁改)
import research_index as rri     # WP-P3-A 版本记录面(终态判定锚定)

# ══ 登记型参数定值(REPORT §零.4/§零.5;登记定值即实现值,运行后禁回改) ═══

DP5_ERROR_FRAMEWORK = "four_axis"                    # DP-5 轴半: 四轴归类
DP5_ROLLING_WINDOW_MONTHS = 12                       # DP-5 窗口半: 滚动 12 个月
DP6_DENOMINATOR_SCOPE = ("hit_miss_only_inconclusive_"
                         "nyt_listed_separately")    # DP-6 (a): 单列不入分母
WARNING_CONSEC_MISS_THRESHOLD = 3                    # P-C-09 警示阈值(登记定值)

RESULT_TERMINAL_STATUSES = ("hit", "miss", "inconclusive")   # P-C-02(rg L534 前三)
PENDING_STATUSES = ("observing", "open")                     # 未决(ae L191 同源)
NOT_YET_TRIGGERED = "not_yet_triggered"

ERROR_AXES = ("direction_error", "horizon_error",
              "magnitude_error", "premise_class")    # P-C-05 四轴(§5.2 L130)
AXIS_LABELS = {"direction_error": "方向错误", "horizon_error": "期限错误",
               "magnitude_error": "幅度错误", "premise_class": "前提类"}

HORIZON_BUCKETS = (("≤2周", 1, 2), ("3-8周", 3, 8), ("≥9周", 9, None))  # P-C-07
STATS_SCHEMA_VERSION = 1                             # P-C-08
WARNING_KIND_LABEL = "假设生成警示"
WARNING_SLOT = "hypothesis_generation_warning_input_slot"   # P-C-09 输入槽位

UP = (">=", ">")
DOWN = ("<=", "<")

# 模块内登记镜像(dp_selfcheck 哨兵对照源;与 REPORT §零.4/§零.5 登记值一致)
_DP_REGISTERED = {"DP-5": "four_axis+rolling_12m",
                  "DP-6": "hit_miss_only_inconclusive_nyt_listed_separately"}
_PARAM_REGISTERED = {
    "warning_consec_miss_threshold": 3,
    "horizon_buckets": ("≤2周:1-2", "3-8周:3-8", "≥9周:9+"),
    "result_terminal_statuses": ("hit", "miss", "inconclusive"),
    "stats_schema_version": 1,
}

REVIEW_NOTE = ("预测复盘与错误模式统计(只读聚合,零改写历史裁决记录;滚动12个月窗口;"
               "四轴归类=方向/期限/幅度/前提类;命中率分母=hit+miss,inconclusive与"
               "not_yet_triggered终态单列不入错误分母[DP-5/DP-6 登记口径]);本统计"
               "不构成投资建议(禁交易/禁仓位/禁收益承诺)")

_VERSION_RECORD_REQUIRED_KEYS = ("record_type", "version_id", "object_type",
                                 "object_id", "change_type", "changes",
                                 "created_at")

_ROW_KEYS = ("pred_id", "status", "terminal", "category", "error_axis",
             "axis_label", "asset", "mechanism", "horizon_weeks",
             "horizon_bucket", "anchor_date", "in_window", "basis")


# ══ 基础件 ═════════════════════════════════════════════════════════════

def _parse_iso_date(s):
    """规范 YYYY-MM-DD 解析;非法→None(P-C-02/P-C-03 面由调用方决定 fail 或缺席)。"""
    if not isinstance(s, str):
        return None
    t = s.strip()[:10]
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


def shift_months(d_iso, months):
    """日历月位移(月末日钳制: 目标月无同日→当月最后一日;P-C-04)。

    例: 2024-02-29 后移 12 月→2023-02-28;2026-03-31 后移 12 月→2025-03-31。"""
    d = date.fromisoformat(_require_iso_date(d_iso, "d_iso"))
    if not isinstance(months, int) or months < 0:
        raise ValueError(f"months 须为非负整数: {months!r}")
    total = d.year * 12 + (d.month - 1) - months
    y, m0 = divmod(total, 12)
    m = m0 + 1
    if m == 12:
        nxt = date(y + 1, 1, 1)
    else:
        nxt = date(y, m + 1, 1)
    last_day = (nxt - timedelta(days=1)).day
    return date(y, m, min(d.day, last_day)).isoformat()


def window_bounds(as_of):
    """滚动窗口边界(P-C-04): [as_of 减 12 个日历月同日, as_of] 闭区间。"""
    end = _require_iso_date(as_of, "as_of")
    start = shift_months(end, DP5_ROLLING_WINDOW_MONTHS)
    return start, end


# ══ DP/参数自检哨兵(要点②「先登记后运行、禁回改」运行期面) ═══════════

def registered_dp_values():
    """DP-5/DP-6 登记定值(活性常量);测试/审计与 REPORT §零.4 登记值对照锚。"""
    return {"DP-5": f"{DP5_ERROR_FRAMEWORK}+rolling_{DP5_ROLLING_WINDOW_MONTHS}m",
            "DP-6": DP6_DENOMINATOR_SCOPE}


def registered_param_values():
    """行内登记型参数活性值(P-C-02/07/08/09);测试字面量三方一致对照锚。"""
    return {
        "warning_consec_miss_threshold": WARNING_CONSEC_MISS_THRESHOLD,
        "horizon_buckets": tuple(f"{lbl}:{lo}-{hi}" if hi is not None
                                 else f"{lbl}:{lo}+"
                                 for lbl, lo, hi in HORIZON_BUCKETS),
        "result_terminal_statuses": tuple(RESULT_TERMINAL_STATUSES),
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
    assert WARNING_CONSEC_MISS_THRESHOLD >= 1, "警示阈值须≥1"
    assert tuple(RESULT_TERMINAL_STATUSES) == ("hit", "miss", "inconclusive"), \
        "结果终态词表漂移(P-C-02 定值)"
    lo_prev = None
    for _lbl, lo, hi in HORIZON_BUCKETS:
        assert isinstance(lo, int) and lo >= 1
        assert hi is None or (isinstance(hi, int) and lo <= hi)
        if lo_prev is not None:
            assert lo > lo_prev, "期限桶下界须单调递增(P-C-07)"
        lo_prev = hi if hi is not None else lo
    return True


# ══ 终态判定(P-C-02) ═════════════════════════════════════════════════

def terminal_state(p, as_of):
    """预测终态判定: (terminal, status)。status 面以状态文件为权威(O-3 载体)。

    hit/miss/inconclusive=结果终态;not_yet_triggered 且 deadline≤as_of=终态
    未生效(引擎 L913-915 语义);observing/open=未决;nyt 无截止日/未知 status
    →ValueError fail-loud(数据非法)。"""
    status = p.get("status")
    if status in RESULT_TERMINAL_STATUSES:
        return True, status
    if status == NOT_YET_TRIGGERED:
        dl = _parse_iso_date(str(p.get("deadline") or ""))
        if dl is None:
            raise ValueError(f"预测#{p.get('pred_id')}: not_yet_triggered 缺规范"
                             f" deadline,终态不可判定(数据非法,fail-loud)")
        return (dl <= as_of, NOT_YET_TRIGGERED if dl <= as_of else None)
    if status in PENDING_STATUSES:
        return False, None
    raise ValueError(f"预测#{p.get('pred_id')}: 未知 status: {status!r}"
                     f"(词表=hit/miss/inconclusive/not_yet_triggered/"
                     f"observing/open)")


# ══ 版本记录锚定(P-C-03;依赖列 L185「版本记录供终态判定」) ═══════════

def _validate_version_records(version_records):
    """注入面轻校验: 记录形必备字段缺一→ValueError fail-loud(P-C-03)。"""
    if version_records is None:
        return []
    if not isinstance(version_records, (list, tuple)):
        raise ValueError(f"version_records 须为列表(rri.list_conclusion_versions"
                         f" 产出)或 None: {type(version_records).__name__}")
    for r in version_records:
        if not isinstance(r, dict):
            raise ValueError(f"版本记录须为 dict: {r!r}")
        missing = [k for k in _VERSION_RECORD_REQUIRED_KEYS if k not in r]
        if missing:
            raise ValueError(f"版本记录缺字段 {missing}(注入面=已验证记录形,"
                             f"P-C-03): {r!r}")
    return list(version_records)


def _pred_version_anchor(p, version_records):
    """该预测在结论版本链的锚定与对账: (anchor|None, discrepancy|None)。

    取 object_type=prediction+object_id=PRED-{pred_id}+change_type=status_change
    记录中(按 created_at,同刻按 version_id)最新者;anchor=created_at 日期段;
    discrepancy=最新 status_change 的 after 值与状态文件现值失配(如实清单,
    不改判不 fail: 版本链=旁路记录,状态文件=权威载体)。"""
    pid_key = f"{rri.PREDICTION_KEY_PREFIX}{p['pred_id']}"
    recs = [r for r in version_records
            if r.get("object_type") == "prediction"
            and str(r.get("object_id")) == pid_key
            and r.get("change_type") == "status_change"]
    if not recs:
        return None, None
    latest = max(recs, key=lambda r: (str(r.get("created_at") or ""),
                                      str(r.get("version_id") or "")))
    anchor = _parse_iso_date(str(latest.get("created_at") or ""))
    disc = None
    afters = [c.get("after") for c in latest.get("changes") or []
              if isinstance(c, dict) and c.get("field") == "status"]
    if afters and str(afters[-1]) != str(p.get("status")):
        disc = {"pred_id": p["pred_id"], "record_status": p.get("status"),
                "version_after": afters[-1]}
    return anchor, disc


def anchor_date_of(p, as_of, version_records=None):
    """终态锚定日期(P-C-03 判定序): resolved_date→版本链 created_at→deadline。

    (as_of 为词表一致性参数: 终态判定先行,锚定只对终态预测有意义;未决预测
    由 classify_predictions 归 pending_excluded,不经本函数。)
    三源全缺席→ValueError fail-loud(终态不可锚定)。返回 (anchor, discrepancy)。"""
    rd = _parse_iso_date(str(p.get("resolved_date") or ""))
    version_records = _validate_version_records(version_records)
    v_anchor, disc = _pred_version_anchor(p, version_records) \
        if version_records else (None, None)
    if rd is not None:
        return rd, disc
    if v_anchor is not None:
        return v_anchor, disc
    dl = _parse_iso_date(str(p.get("deadline") or ""))
    if dl is None:
        raise ValueError(f"预测#{p.get('pred_id')}: 终态三源锚定全缺席"
                         f"(resolved_date/版本链/deadline),锚定不可判(数据非法)")
    return dl, disc


# ══ 归类器(P-C-05/P-C-06;零 GLM 确定性) ═════════════════════════════

def classify_miss(p):
    """miss 三轴归类(P-C-06): (error_axis|None, basis 明细)。

    axis=None=unclassifiable(basis.unclassifiable_reason 说明);
    终态 miss 缺规范 deadline→ValueError fail-loud(数据非法;归类面不可计算)。"""
    comparator = p.get("comparator")
    target = p.get("target")
    basis_field = p.get("price_basis", "close")
    deadline = _parse_iso_date(str(p.get("deadline") or ""))
    if deadline is None:
        raise ValueError(f"预测#{p.get('pred_id')}: 终态 miss 缺规范 deadline"
                         f"(归类面不可计算,数据非法 fail-loud)")
    obs_w, start_w, end_w = ae._window_obs(p)
    usable = [(str(o.get("obs_date") or "")[:10], ae._obs_field_value(o, basis_field))
              for o in obs_w]
    usable = [(d, float(v)) for d, v in usable if v is not None]
    detail = {"window": [start_w, end_w], "price_basis": basis_field,
              "comparator": comparator, "target": target,
              "n_usable": len(usable), "start_v": None, "final_v": None,
              "final_source": None, "post_deadline_hits": 0}
    spec_ok = bool(p.get("metric")) and comparator in ae.COMPARATORS \
        and isinstance(target, (int, float)) and not isinstance(target, bool)
    if not spec_ok:
        detail["unclassifiable_reason"] = "spec_not_computable"
        return None, detail
    if len(usable) < 2:
        detail["unclassifiable_reason"] = "insufficient_window_observations"
        return None, detail
    start_v = usable[0][1]
    mode = p.get("verify_mode") or "expiry"
    if mode == "expiry":
        settle = ae.settlement_date(deadline, ae.market_of_metric(p.get("metric")))
        same_day = [v for d, v in usable if d == settle]
        if same_day:
            final_v, final_source = same_day[-1], "settlement_close"
        else:
            final_v, final_source = usable[-1][1], \
                "last_window_observation_fallback"
    else:
        final_v, final_source = usable[-1][1], "last_window_observation"
    post_hits = 0
    ftarget = float(target)
    for o in p.get("observations") or []:
        od = str(o.get("obs_date") or "")[:10]
        if od > deadline:
            v = ae._obs_field_value(o, basis_field)
            if v is not None and ae.COMPARATORS[comparator](float(v), ftarget):
                post_hits += 1
    detail.update(start_v=start_v, final_v=final_v, final_source=final_source,
                  post_deadline_hits=post_hits)
    if comparator == "==":
        axis = "magnitude_error"          # 无方向轴: 水平未达
    elif ((comparator in UP and final_v < start_v)
          or (comparator in DOWN and final_v > start_v)):
        axis = "direction_error"          # 判断涨实际跌/反向
    elif post_hits > 0:
        axis = "horizon_error"            # 方向对,兑现迟于窗口
    else:
        axis = "magnitude_error"          # 方向对量级未达
    return axis, detail


def _horizon_bucket(hw):
    """期限桶(P-C-07): ≤2周/3-8周/≥9周;缺席或非数值→None 如实单列。"""
    if isinstance(hw, (int, float)) and not isinstance(hw, bool):
        for lbl, lo, hi in HORIZON_BUCKETS:
            if hw >= lo and (hi is None or hw <= hi):
                return lbl
    return None


def _mechanism_of_prediction(p):
    """机制轴(P-C-07): metric 在场→ae.mechanism_of 复用;定性预测→None 如实缺席。"""
    metric = p.get("metric")
    if not metric:
        return None
    return ae.mechanism_of(str(metric))


def classify_predictions(views_data, as_of, version_records=None):
    """归类器入口(P-C-05): 状态文件 predictions→(归类行列表, discrepancies)。

    行序=输入序(状态文件序,同输入同输出);行 schema 见 _ROW_KEYS;未决→
    pending_excluded(anchor=None,in_window=False);窗口入窗=anchor∈[start,end]。"""
    as_of = _require_iso_date(as_of, "as_of")
    if not isinstance(views_data, dict) or not isinstance(
            views_data.get("predictions"), list):
        raise ValueError("views_data 须为携 predictions 列表的 dict"
                         "(门禁后状态文件直载形,P-C-10)")
    version_records = _validate_version_records(version_records)
    w_start, w_end = window_bounds(as_of)
    rows, discrepancies = [], []
    for p in views_data["predictions"]:
        if not isinstance(p, dict) or "pred_id" not in p:
            raise ValueError(f"预测记录须为携 pred_id 的 dict: {p!r}")
        terminal, tstatus = terminal_state(p, as_of)
        row = {"pred_id": p["pred_id"], "status": p.get("status"),
               "terminal": terminal, "category": None, "error_axis": None,
               "axis_label": None, "asset": p.get("asset"),
               "mechanism": _mechanism_of_prediction(p),
               "horizon_weeks": p.get("horizon_weeks"),
               "horizon_bucket": _horizon_bucket(p.get("horizon_weeks")),
               "anchor_date": None, "in_window": False, "basis": None}
        if not terminal:
            row["category"] = "pending_excluded"
            rows.append(row)
            continue
        anchor, disc = anchor_date_of(p, as_of, version_records)
        if disc is not None:
            discrepancies.append(disc)
        row["anchor_date"] = anchor
        row["in_window"] = w_start <= anchor <= w_end
        if tstatus == "hit":
            row["category"] = "hit_sample"
        elif tstatus == "miss":
            row["category"] = "error_pattern"
            axis, detail = classify_miss(p)
            row["error_axis"] = axis
            row["axis_label"] = AXIS_LABELS[axis] if axis else None
            row["basis"] = detail
        else:   # inconclusive / not_yet_triggered 终态 → 前提类单列(DP-6(a))
            row["category"] = "premise_class"
            row["error_axis"] = "premise_class"
            row["axis_label"] = AXIS_LABELS["premise_class"]
        rows.append(row)
    discrepancies.sort(key=lambda d: str(d["pred_id"]))
    return rows, discrepancies


# ══ 统计器(P-C-07/P-C-08;只读聚合) ═══════════════════════════════════

def _sample_key(r):
    return (r["anchor_date"], str(r["pred_id"]))


def _bucket_rows(rows, key_fn):
    """桶行聚合(仅窗内终态样本;P-C-07 行 schema;桶键字典序,None 排首)。"""
    buckets = {}
    for r in rows:
        if not r["in_window"]:
            continue
        k = key_fn(r)
        b = buckets.setdefault(k, {"count": 0, "hit": 0, "miss": 0,
                                   "inconclusive": 0,
                                   "not_yet_triggered_terminal": 0,
                                   "hit_rate": None})
        b["count"] += 1
        if r["status"] == "hit":
            b["hit"] += 1
        elif r["status"] == "miss":
            b["miss"] += 1
        elif r["status"] == "inconclusive":
            b["inconclusive"] += 1
        elif r["status"] == NOT_YET_TRIGGERED:
            b["not_yet_triggered_terminal"] += 1
    for b in buckets.values():
        denom = b["hit"] + b["miss"]
        b["hit_rate"] = (b["hit"] / denom) if denom > 0 else None
    return {k: buckets[k] for k in sorted(buckets, key=lambda x: (x is None, str(x)))}


def _statistics_from_rows(rows, discrepancies, as_of):
    w_start, w_end = window_bounds(as_of)
    in_win = [r for r in rows if r["in_window"]]

    def _ids(pred):
        return [r["pred_id"] for r in sorted(
            [r for r in in_win if pred(r)], key=_sample_key)]

    counts = {k: 0 for k in ("hit", "miss", "inconclusive",
                             "not_yet_triggered_terminal")}
    for r in in_win:
        if r["status"] == "hit":
            counts["hit"] += 1
        elif r["status"] == "miss":
            counts["miss"] += 1
        elif r["status"] == "inconclusive":
            counts["inconclusive"] += 1
        elif r["status"] == NOT_YET_TRIGGERED:
            counts["not_yet_triggered_terminal"] += 1
    denom = counts["hit"] + counts["miss"]
    counts["hit_rate"] = (counts["hit"] / denom) if denom > 0 else None
    counts["out_of_window_terminal"] = sum(
        1 for r in rows if r["terminal"] and not r["in_window"])
    counts["non_terminal_excluded"] = sum(1 for r in rows if not r["terminal"])
    error_patterns = {ax: _ids(lambda r, ax=ax: r["category"] == "error_pattern"
                              and r["error_axis"] == ax)
                      for ax in ("direction_error", "horizon_error",
                                 "magnitude_error")}
    error_patterns["unclassifiable"] = _ids(
        lambda r: r["category"] == "error_pattern" and r["error_axis"] is None)
    return {
        "schema_version": STATS_SCHEMA_VERSION, "note": REVIEW_NOTE,
        "as_of": as_of, "window_start": w_start, "window_end": w_end,
        "counts": counts,
        "error_patterns": error_patterns,
        "correct_samples": _ids(lambda r: r["category"] == "hit_sample"),
        "premise_class": {
            "inconclusive": _ids(lambda r: r["status"] == "inconclusive"),
            "not_yet_triggered_terminal": _ids(
                lambda r: r["status"] == NOT_YET_TRIGGERED)},
        "excluded_pending": [r["pred_id"] for r in rows
                             if r["category"] == "pending_excluded"],
        "buckets": {
            "asset": _bucket_rows(rows, lambda r: r["asset"]),
            "mechanism": _bucket_rows(rows, lambda r: r["mechanism"]),
            "horizon": _bucket_rows(rows, lambda r: r["horizon_bucket"]),
        },
        "discrepancies": discrepancies,
    }


def review_statistics(views_data, as_of, version_records=None):
    """分桶统计器(P-C-08): 归类+聚合→统计文档(纯函数,只读零写入)。

    返回文档序列化形即确定性 JSON 文档(dict);canonical 序列化由调用方
    json.dumps(sort_keys=True, ensure_ascii=False, indent=1) 承载(P-C-08)。"""
    rows, discrepancies = classify_predictions(views_data, as_of,
                                               version_records)
    return _statistics_from_rows(rows, discrepancies, as_of)


def _canonical_order(obj):
    """递归确定序(P-C-08 字典序口径的 None 键可承载形): dict 键按
    (键为 None, str(键)) 升序重排(None 排首,与 P-C-07 None 单列键相容);
    列表保序。str-only 文档产物与 json.dumps(sort_keys=True) 逐字节一致;
    纯函数零副作用(新 dict,不改输入)。"""
    if isinstance(obj, dict):
        return {k: _canonical_order(obj[k])
                for k in sorted(obj, key=lambda x: (x is None, str(x)))}
    if isinstance(obj, (list, tuple)):
        return [_canonical_order(v) for v in obj]
    return obj


def dump_statistics(doc):
    """统计文档确定性序列化(P-C-08;纯函数,返回字符串,零写盘)。

    实现期口径修正(如实登记,REPORT §零.9): json.dumps(sort_keys=True)
    对 None 键(P-C-07 缺席轴单列键)抛 TypeError 不可排序——先经
    _canonical_order 确定序(None 排首)再 sort_keys=False 序列化,
    str-only 形与登记序列化式逐字节等值。"""
    if not isinstance(doc, dict) or doc.get("schema_version") != STATS_SCHEMA_VERSION:
        raise ValueError(f"统计文档 schema 非法(须 schema_version="
                         f"{STATS_SCHEMA_VERSION})")
    return json.dumps(_canonical_order(doc), ensure_ascii=False,
                      sort_keys=False, indent=1)


# ══ 警示清单生成(P-C-09;只作输入槽位) ═══════════════════════════════

def hypothesis_warnings(rows, as_of):
    """假设生成警示清单(P-C-09): 窗内机制轴(非 None)hit/miss 样本按机制分组,
    组内按 (anchor_date,str(pred_id)) 升序取**末端连续 miss 游程**;游程≥3
    (登记阈值)→警示条目。条目按 mechanism 字典序;只读聚合零写入。"""
    as_of = _require_iso_date(as_of, "as_of")
    w_start, w_end = window_bounds(as_of)
    groups = {}
    for r in rows:
        if r["in_window"] and r["mechanism"] is not None \
                and r["category"] in ("hit_sample", "error_pattern"):
            groups.setdefault(r["mechanism"], []).append(r)
    out = []
    for mech in sorted(groups):
        grp = sorted(groups[mech], key=_sample_key)
        run_ids = []
        for r in reversed(grp):
            if r["status"] == "miss":
                run_ids.insert(0, r["pred_id"])
            else:
                break
        if len(run_ids) >= WARNING_CONSEC_MISS_THRESHOLD:
            out.append({"mechanism": mech, "axis_label": WARNING_KIND_LABEL,
                        "consecutive_misses": len(run_ids),
                        "miss_pred_ids": run_ids,
                        "threshold": WARNING_CONSEC_MISS_THRESHOLD,
                        "window_start": w_start, "window_end": w_end,
                        "slot": WARNING_SLOT})
    return out


def render_warning_briefing(doc, warnings):
    """警示简报旁路渲染(P-C-09/P-C-14): 纯文本输入槽位呈现,返回字符串零写入。

    警示清单只作输入槽位(L134): 本渲染不改周报结构与回写路径;消费面(周报
    证据校准段)=WP-P3-D 范围,本包零注入。"""
    if not isinstance(doc, dict) or not isinstance(warnings, list):
        raise ValueError("render_warning_briefing(doc, warnings): doc 须为统计"
                         "文档 dict,warnings 须为列表")
    c = doc.get("counts") or {}
    hr = c.get("hit_rate")
    hr_txt = "N/A(分母=0,如实缺席)" if hr is None else f"{hr:.4f}"
    lines = [
        "预测复盘警示简报(假设生成警示清单·输入槽位)",
        f"窗口: {doc.get('window_start')} ~ {doc.get('window_end')}"
        f"(滚动{DP5_ROLLING_WINDOW_MONTHS}个月,DP-5 登记口径)",
        f"窗内终态: hit={c.get('hit')} miss={c.get('miss')} "
        f"inconclusive={c.get('inconclusive')}(单列) "
        f"not_yet_triggered终态={c.get('not_yet_triggered_terminal')}(单列); "
        f"命中率=hit/(hit+miss)={hr_txt}",
    ]
    ep = doc.get("error_patterns") or {}
    lines.append("错误模式: 方向错误=" + ",".join(map(str, ep.get(
        "direction_error") or [])) + " | 期限错误=" + ",".join(map(str, ep.get(
            "horizon_error") or [])) + " | 幅度错误=" + ",".join(map(str, ep.get(
                "magnitude_error") or [])) + " | 无法归类(单列)=" + ",".join(
                    map(str, ep.get("unclassifiable") or [])))
    if warnings:
        lines.append(f"警示条目(机制类别末端连续miss≥"
                     f"{WARNING_CONSEC_MISS_THRESHOLD},共{len(warnings)}条):")
        for w in warnings:
            lines.append(
                f"- [{w['mechanism']}] {w['axis_label']}: 连续miss="
                f"{w['consecutive_misses']} 样本="
                f"{','.join(map(str, w['miss_pred_ids']))} 阈值="
                f"{w['threshold']} (slot={w['slot']})")
    else:
        lines.append(f"警示条目: 本窗口无达阈值机制类别(阈值="
                     f"{WARNING_CONSEC_MISS_THRESHOLD},如实呈现)")
    if doc.get("discrepancies"):
        lines.append(f"版本链对账失配(discrepancies,如实清单,不改判): "
                     f"{len(doc['discrepancies'])} 条")
    lines.append("本简报为预测复盘与错误模式统计面输出,只作输入槽位(零注入零回写);"
                 "不构成投资建议(禁交易/禁仓位/禁收益承诺)")
    return "\n".join(lines)


# ══ 便利编排面(P-C-13 唯一墙钟缺省;零写入) ═══════════════════════════

def prediction_review_report(views_path, as_of=None, archive_dir=None):
    """编排入口: 读状态文件(只读直载 json.load,不经 ae.load_views)+版本链
    (rri.list_conclusion_versions,archive_dir 缺省=rri 默认档根,只读)→
    {statistics, warnings, briefing}。全流程零文件写入(P-C-10)。"""
    as_of = _require_iso_date(as_of or _now_date_iso(), "as_of")
    with open(str(views_path), "r", encoding="utf-8") as f:
        views_data = json.load(f)
    version_records = rri.list_conclusion_versions(archive_dir)
    rows, discrepancies = classify_predictions(views_data, as_of,
                                               version_records)
    doc = _statistics_from_rows(rows, discrepancies, as_of)
    warnings = hypothesis_warnings(rows, as_of)
    briefing = render_warning_briefing(doc, warnings)
    return {"statistics": doc, "warnings": warnings, "briefing": briefing}


# ══ 自检入口(零写入;不落默认路径) ═════════════════════════════════════

def _selfcheck():
    ok = dp_selfcheck()
    print(f"prediction_review selfcheck: dp_selfcheck={ok}; "
          f"axes={len(ERROR_AXES)}; window_months={DP5_ROLLING_WINDOW_MONTHS}; "
          f"warning_threshold={WARNING_CONSEC_MISS_THRESHOLD}; "
          f"horizon_buckets={len(HORIZON_BUCKETS)}")
    print(REVIEW_NOTE)
    return ok


if __name__ == "__main__":
    _selfcheck()
