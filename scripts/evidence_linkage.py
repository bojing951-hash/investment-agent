#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P3-WP-B: 新证据关联与持续跟踪聚合(P3 收尾层第 2 实现包,#33/#34 挂靠)

DESIGN docs/P3_DESIGN.md §7 WP-P3-B 行(L176-L180,基线工作树实读)确定性落地:
- 事件触发器(§4.1 L103,3 类事件): ①新快照经 Gate A 放行落档后②预测裁决落档
  (终态变更时)③新正式周报发布后——触发器**消费门禁后事件流,不轮询原始数据**
  (事件=注入;模块无 daily_dir 参数、零 data/daily 路径引用,结构性不可达采集件);
  事件构造一律 fail-closed: 快照 gate_a.status 经 rp.gate_allows_formal_research
  放行(FAIL/None/未知→ValueError);裁决事件限终态词表 {hit,miss,inconclusive};
  周报事件经 rp.formal_report_view 八条校验链在场复用+绑定快照三重纪律
  (drr._load_snapshot_for_verify 规范加载+rp.digest_snapshot 重算+gate 放行,
  重算 digest 与发布状态声明值失配→ValueError 证据链漂移 fail-loud);
- 匹配器(§4.1 L105-108,第一/二层零 GLM;**不含第三层语义匹配**——PENDING 另拟,
  确认权留用户[DP-4],本模块零 GLM/零网络/零凭证):
  第一层 精确匹配=对象 quant_triggers[].metric(锚键)∈事件锚点键集,条件评估经
  ae._eval_condition_set 在场复用(COMPARATORS 词表),条件态沿用引擎核验词面
  (triggered/not_triggered/sustaining/unverifiable);建议动作映射(P-B-06):
  triggered→提案/sustaining→复核/not_triggered→复核/unverifiable→复核——
  提案=仅生成关联建议条目,实际状态变更走既有门禁,关联面零状态写入;
  第二层 规则匹配=机制类别单轴交叉(ae.mechanism_of+ae.MECHANISM_CATEGORIES
  在场复用,7 类词表),建议动作=忽略;**资产标签轴结构性缺席**(登记发现
  P-B-08: 中文资产标签与 registry asset_class 无在场词表桥接,如实缺席不造值);
- 关联档案(§4.1 L110,append-only 旁路件): LNK-{YYYYMMDD}-{NNN} 同日单调配号,
  集合 evidence_linkages 挂共享档案族根,经 drr._write_records 原子落档
  (重复/改写一律拒);记录零原始数值字段(证据引用落 snapshot_id+digest 重算值
  [要点④]+档键,不复制数值语义为第二事实源,§3.1 L73 纪律延伸);可重建=
  同事件×同对象面纯函数重放逐字节一致;
- 未决触发器与到期裁决聚合视图(§4.2 L115,只读): ①未决触发器跨期清单(❓待验证/
  ⏳持续确认中按对象聚合;views 直经 ae.evaluate_quant_triggers[persist=False
  零副作用]+theses 经只读适配壳同评估器)②到期预测裁决待办(ae.due_predictions
  在场复用,⏰已到期口径)——数据源为状态文件,呈现载体=旁路简报渲染,
  零写入零回写路径(不改周报系统)。

范围排除(DESIGN L177-178): 第三层语义匹配(DP-4 确认面)、WP-P3-A/C/D/E/F
任何范围、自然语言查询(§3.2(b) 停泊面)、W4/W5 工具零接入。

纪律: 零网络(import 面白名单 json/os/re/sys/datetime+项目既有
allocation_engine/deep_research_registrar/research_provenance/snapshot_builder/
research_index);零 GLM/凭证/付费;关联不改任何状态(要点①);对齐上游=复用调用
禁复制分叉。本模块输出为研究关联与跟踪聚合面数据,**不构成投资建议**
(DESIGN §8.3 红线: 禁交易/禁仓位/禁收益承诺)。参数登记: docs/P3_WP_B_REPORT.md
§零.4/§零.5(DP 处置+P-B-01..P-B-16,先登记后实现,运行后禁回改)。
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import allocation_engine as ae       # 机制词表/条件评估/触发器评估/到期口径(复用调用)
import deep_research_registrar as drr  # 写入原语/快照规范加载/集合目录(WP-P2-A)
import research_provenance as rp     # gate 放行/快照指纹/正式周报校验链(R 系)
import research_index as rri         # WP-P3-A 状态记录键前缀词表(依赖面复用)
import snapshot_builder as sb        # build_anchors 快照→锚点兼容桥(单一来源=快照)

# ══ 登记型参数定值(REPORT §零.4/§零.5;登记定值即实现值,运行后禁回改) ═════

COLLECTION_LINKAGES = "evidence_linkages"       # P-B-09(不占上游已占集合名)
LINKAGE_ID_PREFIX = "LNK-"                      # P-B-09(避开已占 13 前缀)
EVENT_KINDS = ("snapshot", "adjudication", "formal_report")   # P-B-02(§4.1 L103)
TERMINAL_PRED_STATUSES = ("hit", "miss", "inconclusive")      # P-B-03②(终态词表)
LINK_OBJECT_TYPES = ("thesis", "view")          # P-B-10(关联对象面;预测=证据侧/聚合面)
MATCH_LAYERS = (1, 2)                           # 第一/二层(第三层 PENDING 另拟)
CONDITION_STATUSES = ("triggered", "not_triggered", "sustaining", "unverifiable")
SUGGESTED_ACTIONS = ("提案", "复核", "忽略")     # DESIGN L110 词面全集
LAYER1_ACTION_MAP = {"triggered": "提案", "sustaining": "复核",
                     "not_triggered": "复核", "unverifiable": "复核"}   # P-B-06
LAYER2_SUGGESTED_ACTION = "忽略"                 # P-B-08(弱信号,登记供人工筛选)
ADJUDICATION_SUGGESTED_ACTION = "复核"           # P-B-07(裁决=结果型证据,建议复核)
MECHANISM_CATEGORIES = tuple(ae.MECHANISM_CATEGORIES)   # 7 类词表(ae L104 在场引用)
TRIGGER_STATUS_DISPLAY = {"triggered": "✅已触发", "not_triggered": "⬜未触发",
                          "unverifiable": "❓待验证",
                          "sustaining": "⏳持续确认中"}   # ae L1052-1053 词面登记
PENDING_OVERVIEW_STATUSES = ("unverifiable", "sustaining")  # P-B-12(❓/⏳ 两态)
DISCLAIMER_NOTE = ("新证据关联与持续跟踪聚合面(关联不直接改任何状态;建议动作中的"
                   "提案仅生成建议,实际状态变更走既有门禁);研究关联面输出,"
                   "不构成投资建议(禁交易/禁仓位/禁收益承诺)")

# 模块内登记镜像(param_selfcheck 哨兵对照源;与 REPORT §零.5 登记值一致)
_PARAM_REGISTERED = {
    "P-B-02": ("snapshot", "adjudication", "formal_report"),
    "P-B-03.terminal": ("hit", "miss", "inconclusive"),
    "P-B-06": {"triggered": "提案", "sustaining": "复核",
               "not_triggered": "复核", "unverifiable": "复核"},
    "P-B-07": "复核",
    "P-B-08": "忽略",
    "P-B-09.collection": "evidence_linkages",
    "P-B-09.prefix": "LNK-",
}

_SNAPSHOT_ID_RE = re.compile(r"^research_snapshot_(\d{8})(?:_v(\d+))?$")
_YMD8_RE = re.compile(r"^\d{8}$")
_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_LINKAGE_ID_RE = re.compile(r"^LNK-(\d{8})-(\d{3,})$")

_ARCHIVE_RESERVED_COLLECTIONS = (
    "queries", "deep_research_tasks", "hypotheses", "conditions", "events",
    "deep_research_evidence", "rounds", "deep_research_triggers",
    "conclusions", "disposals", "calendar_events", "conclusion_versions")


# ══ 基础件 ═════════════════════════════════════════════════════════════

def _now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _ymd8_of(iso_ts):
    return str(iso_ts)[:10].replace("-", "")


def _ymd8_to_iso(ymd8):
    return f"{ymd8[:4]}-{ymd8[4:6]}-{ymd8[6:]}" if _YMD8_RE.match(ymd8 or "") else None


def _iso_date_ok(s):
    if not isinstance(s, str) or not _ISO_DATE_RE.match(s):
        return False
    try:
        datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        return False
    return True


# ══ 参数自检哨兵(要点③「先登记后运行、禁回改」运行期面) ═══════════════

def registered_param_values():
    """登记型参数活性常量(测试/审计与 REPORT §零.5 登记值对照锚)。"""
    return {
        "P-B-02": tuple(EVENT_KINDS),
        "P-B-03.terminal": tuple(TERMINAL_PRED_STATUSES),
        "P-B-06": dict(LAYER1_ACTION_MAP),
        "P-B-07": ADJUDICATION_SUGGESTED_ACTION,
        "P-B-08": LAYER2_SUGGESTED_ACTION,
        "P-B-09.collection": COLLECTION_LINKAGES,
        "P-B-09.prefix": LINKAGE_ID_PREFIX,
    }


def param_selfcheck():
    """活性常量 vs 模块内登记镜像一致性哨兵;运行后回改任一定值→AssertionError。

    (测试侧另有字面量硬编码断言锚定 REPORT 登记值,三方一致=常量/镜像/登记;
    本哨兵提供运行期检出面,负向测试以 monkeypatch 模拟回改验证检出。)"""
    live = registered_param_values()
    for k, v in _PARAM_REGISTERED.items():
        assert live.get(k) == v, (
            f"{k} 登记定值被回改: 活性={live.get(k)!r}≠登记={v!r}"
            f"(先登记后运行禁回改,REPORT §零.5)")
    assert tuple(sorted(EVENT_KINDS)) == (
        "adjudication", "formal_report", "snapshot"), "EVENT_KINDS 词表漂移(P-B-02)"
    assert set(LAYER1_ACTION_MAP) == set(CONDITION_STATUSES), (
        "第一层建议动作映射未覆盖条件态全集(P-B-06)")
    assert all(a in SUGGESTED_ACTIONS for a in LAYER1_ACTION_MAP.values()), (
        "建议动作词面漂移(DESIGN L110 词面: 复核|提案|忽略)")
    assert COLLECTION_LINKAGES not in _ARCHIVE_RESERVED_COLLECTIONS, (
        "关联档案集合名占用上游已占集合名(P-B-09)")
    assert LINKAGE_ID_PREFIX not in ("QB-", "RT-DR-", "HP-", "FC-", "EV-", "EVI-",
                                     "RD-", "TRG-", "CON-", "DSP-", "CAL-", "VER-",
                                     "PRED-", "THESIS-", "VIEW-"), (
        "关联档案 ID 前缀占用上游已占前缀(P-B-09)")
    assert tuple(MECHANISM_CATEGORIES) == tuple(ae.MECHANISM_CATEGORIES), (
        "机制类别词表与引擎在场词表漂移(P-B-08)")
    return True


# ══ 事件构造(P-B-03;门禁后事件流,fail-closed;模块零轮询面) ═══════════

def _verify_snapshot_gate(snapshot, *, face):
    """快照 Gate A 放行核验(P-B-03): FAIL/None/未知→ValueError 零构造。"""
    gate_status = ((snapshot or {}).get("gate_a") or {}).get("status")
    if not rp.gate_allows_formal_research(gate_status):
        raise ValueError(f"[{face}] Gate A={gate_status!r} 不放行正式研究"
                         f"(PASS/DEGRADED 之外,FAIL fail-closed,§3.1 红线),"
                         f"不得作为关联事件证据源")


def _snapshot_ymd8(snapshot_id):
    m = _SNAPSHOT_ID_RE.match(str(snapshot_id or ""))
    return m.group(1) if m else None


def _event_anchors(snapshot, anchors, ymd8, *, face):
    """事件锚点集(P-B-04): 默认 sb.build_anchors 快照单一来源派生;显式注入面。"""
    if anchors is not None:
        if not isinstance(anchors, dict):
            raise ValueError(f"[{face}] anchors 注入须为 dict: {type(anchors).__name__}")
        return dict(anchors)
    return sb.build_anchors(snapshot, ymd8)


def snapshot_event(snapshot, *, anchors=None, ymd=None):
    """事件①新快照经 Gate A 放行落档后(P-B-03①)。

    事件=注入的门禁后快照 dict(触发器消费门禁后事件流,不轮询原始数据——
    本模块无 daily 枚举面);gate FAIL→ValueError(要点②);digest=rp.digest_snapshot
    内容重算(禁采声明值,要点④)。anchors 显式注入面见 P-B-04。"""
    if not isinstance(snapshot, dict):
        raise ValueError(f"[snapshot] snapshot 须为 dict(门禁后事件流注入面): "
                         f"{type(snapshot).__name__}")
    sid = snapshot.get("snapshot_id")
    if not isinstance(sid, str) or drr.ra.parse_snapshot_id(sid) is None:
        raise ValueError(f"[snapshot] snapshot_id 非规范: {sid!r}")
    ymd8 = _snapshot_ymd8(sid)
    _verify_snapshot_gate(snapshot, face="snapshot")
    return {"event_kind": "snapshot",
            "ymd": str(ymd) if ymd is not None else ymd8,
            "evidence_key": sid,
            "snapshot_id": sid,
            "digest": rp.digest_snapshot(snapshot),
            "anchors": _event_anchors(snapshot, anchors, ymd8, face="snapshot"),
            "evidence_keys": None}


def adjudication_event(prediction, snapshot, *, anchors=None, ymd=None):
    """事件②预测裁决落档·终态变更时(P-B-03②)。

    prediction.status∈{hit,miss,inconclusive} 终态词表(not_yet_triggered=前提
    未生效非终态;open/observing=未决态——均→ValueError);新证据=裁决落档的
    预测(其规格 metric/comparator/target);证据接地快照经注入+gate 核验+digest
    重算(要点④);evidence_keys=规格 metric 单键(P-B-07)。"""
    if not isinstance(prediction, dict):
        raise ValueError(f"[adjudication] prediction 须为 dict: "
                         f"{type(prediction).__name__}")
    status = prediction.get("status")
    if status not in TERMINAL_PRED_STATUSES:
        raise ValueError(f"[adjudication] prediction.status={status!r} 非终态词表"
                         f" {TERMINAL_PRED_STATUSES}(未决/前提未生效不构成裁决落档"
                         f"事件,如实拒)")
    pid = prediction.get("pred_id")
    if pid is None or (isinstance(pid, str) and not pid.strip()) \
            or not isinstance(pid, (str, int)):
        raise ValueError(f"[adjudication] pred_id 须为非空标识: {pid!r}")
    if not isinstance(snapshot, dict):
        raise ValueError(f"[adjudication] snapshot 须为 dict(裁决事件证据接地面): "
                         f"{type(snapshot).__name__}")
    sid = snapshot.get("snapshot_id")
    if not isinstance(sid, str) or drr.ra.parse_snapshot_id(sid) is None:
        raise ValueError(f"[adjudication] snapshot_id 非规范: {sid!r}")
    ymd8 = _snapshot_ymd8(sid)
    _verify_snapshot_gate(snapshot, face="adjudication")
    spec_metric = prediction.get("metric")
    return {"event_kind": "adjudication",
            "ymd": str(ymd) if ymd is not None else ymd8,
            "evidence_key": f"{rri.PREDICTION_KEY_PREFIX}{pid}",
            "snapshot_id": sid,
            "digest": rp.digest_snapshot(snapshot),
            "anchors": _event_anchors(snapshot, anchors, ymd8,
                                      face="adjudication"),
            "evidence_keys": {str(spec_metric)} if spec_metric else set()}


def formal_report_event(report_view, snapshot_dir, *, anchors=None):
    """事件③新正式周报发布后(P-B-03③)。

    report_view={'ymd','path','status'}(rp.scan_formal_weekly_reports/
    formal_report_view 产出);构造器**复验** rp.formal_report_view 八条校验链
    (发布状态/身份/内容摘要——候选/未发布/被替换产物一律拒);维度画像=状态
    记录绑定快照(status.snapshot_id)经 drr._load_snapshot_for_verify 规范加载
    +gate 放行+rp.digest_snapshot 重算,且与状态记录 snapshot_digest 声明值
    一致核验(失配→ValueError 证据链漂移 fail-loud)。"""
    path = (report_view or {}).get("path") if isinstance(report_view, dict) else None
    if not path:
        raise ValueError("[formal_report] report_view 须为携 path 的 dict"
                         "(rp.scan_formal_weekly_reports/formal_report_view 产出)")
    view, reason = rp.formal_report_view(str(path))
    if view is None:
        raise ValueError(f"[formal_report] 正式周报八条校验链复验拒: {reason}")
    st = view.get("status") or {}
    sid = st.get("snapshot_id")
    if not isinstance(sid, str) or not sid.strip():
        raise ValueError("[formal_report] 发布状态缺 snapshot_id 绑定"
                         "(无法接地证据引用,如实拒)")
    snap, load_err = drr._load_snapshot_for_verify(sid, snapshot_dir)
    if snap is None:
        raise ValueError(f"[formal_report] 绑定快照接地失败: {load_err}")
    _verify_snapshot_gate(snap, face="formal_report")
    digest = rp.digest_snapshot(snap)
    claimed = st.get("snapshot_digest")
    if claimed != digest:
        raise ValueError(f"[formal_report] 绑定快照指纹漂移: 重算={digest!r} vs "
                         f"发布状态声明={claimed!r}(证据链漂移 fail-loud,禁采声明值)")
    ymd8 = _snapshot_ymd8(snap.get("snapshot_id"))
    return {"event_kind": "formal_report",
            "ymd": view["ymd"],
            "evidence_key": f"weekly_report_{view['ymd']}",
            "snapshot_id": str(snap.get("snapshot_id")),
            "digest": digest,
            "anchors": _event_anchors(snap, anchors, ymd8,
                                      face="formal_report"),
            "evidence_keys": None}


# ══ 对象面(旧观点/论点=门禁后状态文件,只读) ═════════════════════════

def load_link_objects(thesis_path, views_path):
    """读状态文件→关联对象清单(P-B-11 迭代序: theses 文件序→views 文件序)。

    返回 [{object_type, object_id(THESIS-/VIEW- 键,rri 前缀词表), asset,
    quant_triggers}](只读拷贝,零状态写入)。"""
    with open(str(thesis_path), "r", encoding="utf-8") as f:
        th = json.load(f)
    with open(str(views_path), "r", encoding="utf-8") as f:
        av = json.load(f)
    objects = []
    for t in th.get("theses") or []:
        if t.get("id") is None:
            raise ValueError(f"thesis 缺 id: {t!r}")
        objects.append({"object_type": "thesis",
                        "object_id": f"{rri.THESIS_KEY_PREFIX}{t['id']}",
                        "asset": None,
                        "quant_triggers": list(t.get("quant_triggers") or [])})
    for v in av.get("views") or []:
        if v.get("id") is None:
            raise ValueError(f"view 缺 id: {v!r}")
        objects.append({"object_type": "view",
                        "object_id": f"{rri.VIEW_KEY_PREFIX}{v['id']}",
                        "asset": v.get("asset"),
                        "quant_triggers": list(v.get("quant_triggers") or [])})
    return objects


def _trigger_metric_keys(obj):
    """对象触发器锚键集(非空 metric;None metric 触发器如实不参与键面)。"""
    return [str(t.get("metric")) for t in obj["quant_triggers"]
            if t.get("metric") not in (None, "")]


def _object_mechanisms(obj):
    """对象侧机制画像(P-B-08): 触发器锚键经 ae.mechanism_of 在场规则表派生。"""
    return {ae.mechanism_of(k) for k in _trigger_metric_keys(obj)}


# ══ 匹配器(P-B-05..P-B-08;纯函数,确定性排序) ═══════════════════════

def _layer1_condition_status(trigger, anchors):
    """第一层条件评估(P-B-05): ae._eval_condition_set 在场复用+sustain 一次性口径。

    一次性评估无 persist 跨周状态载体→按引擎首跨口径 consec=1:
    sustain≤1→triggered(与 ae.evaluate_quant_triggers 空状态口径逐字一致);
    sustain>1 未满 N 周→sustaining(⏳不冒充已触发);数据面词面直通。"""
    fired, _detail = ae._eval_condition_set(trigger, anchors)
    sustain = int(trigger.get("sustain_weeks") or 0)
    if fired == "triggered" and sustain and 1 < sustain:
        return "sustaining"
    return fired              # triggered / not_triggered / unverifiable(引擎词面)


def _match_snapshot_like(event, obj):
    """快照族事件(①③)×单对象匹配(P-B-05/P-B-08)→ 条目列表。"""
    anchors = event["anchors"]
    out = []
    obj_keys = set(_trigger_metric_keys(obj))
    # 第一层: 触发器锚键 ∈ 事件锚点键集(对象触发器列表序)
    for t in obj["quant_triggers"]:
        mkey = t.get("metric")
        if mkey in (None, "") or str(mkey) not in anchors:
            continue
        cond = _layer1_condition_status(t, anchors)
        out.append({"object_type": obj["object_type"],
                    "object_id": obj["object_id"],
                    "match_layer": 1,
                    "anchor_key": str(mkey),
                    "metric_id": _anchor_metric_id(anchors, str(mkey)),
                    "trigger_id": t.get("trig_id"),
                    "condition_status": cond,
                    "suggested_action": LAYER1_ACTION_MAP[cond]})
    # 第二层: 机制类别单轴交叉(锚键字典序;第一层优先去重)
    mechs = _object_mechanisms(obj)
    for key in sorted(set(anchors) - obj_keys):
        if ae.mechanism_of(key) in mechs:
            out.append({"object_type": obj["object_type"],
                        "object_id": obj["object_id"],
                        "match_layer": 2,
                        "anchor_key": key,
                        "metric_id": _anchor_metric_id(anchors, key),
                        "trigger_id": None,
                        "condition_status": None,
                        "suggested_action": LAYER2_SUGGESTED_ACTION})
    return out


def _match_adjudication(event, obj):
    """裁决事件×单对象匹配(P-B-07): spec.metric 等值第一层+机制交叉第二层。"""
    out = []
    obj_keys = set(_trigger_metric_keys(obj))
    mechs = _object_mechanisms(obj)
    for key in sorted(event["evidence_keys"]):
        if key in obj_keys:
            out.append({"object_type": obj["object_type"],
                        "object_id": obj["object_id"],
                        "match_layer": 1,
                        "anchor_key": key,
                        "metric_id": None,
                        "trigger_id": None,
                        "condition_status": None,
                        "suggested_action": ADJUDICATION_SUGGESTED_ACTION})
        elif ae.mechanism_of(key) in mechs:
            out.append({"object_type": obj["object_type"],
                        "object_id": obj["object_id"],
                        "match_layer": 2,
                        "anchor_key": key,
                        "metric_id": None,
                        "trigger_id": None,
                        "condition_status": None,
                        "suggested_action": LAYER2_SUGGESTED_ACTION})
    return out


def _anchor_metric_id(anchors, key):
    rec = anchors.get(key)
    mid = rec.get("metric_id") if isinstance(rec, dict) else None
    return str(mid) if mid else None


def match_event(event, objects):
    """单事件×对象集匹配(P-B-11 确定性): 纯函数,输出按
    (object_type, object_id, anchor_key, match_layer) 字典序。"""
    if not isinstance(event, dict) or event.get("event_kind") not in EVENT_KINDS:
        raise ValueError(f"event 须为事件构造器产出: {event!r}")
    matcher = (_match_adjudication if event["event_kind"] == "adjudication"
               else _match_snapshot_like)
    entries = []
    for obj in objects:
        entries.extend(matcher(event, obj))
    entries.sort(key=lambda e: (e["object_type"], e["object_id"],
                                e["anchor_key"], e["match_layer"]))
    return entries


# ══ 关联档案(P-B-09/P-B-10;append-only 旁路件,可重建) ═══════════════

def _linkages_dir(archive_dir):
    return drr._collection_dir(archive_dir, COLLECTION_LINKAGES)


def _same_day_max_seq(archive_dir, ymd8):
    """同日单调配号基数: 扫集合目录当日 LNK-{ymd}-{NNN} 最大序号(ra/VER- 同款纪律)。"""
    best = 0
    d = _linkages_dir(archive_dir)
    if not os.path.isdir(d):
        return 0
    for name in os.listdir(d):
        m = _LINKAGE_ID_RE.match(name[:-5] if name.endswith(".json") else name)
        if m and m.group(1) == str(ymd8):
            best = max(best, int(m.group(2)))
    return best


def _next_linkage_id(archive_dir, created_at):
    ymd8 = _ymd8_of(created_at)
    if not _YMD8_RE.match(ymd8):
        raise ValueError(f"created_at 须为 ISO8601 字符串: {created_at!r}")
    seq = _same_day_max_seq(archive_dir, ymd8) + 1
    return f"{LINKAGE_ID_PREFIX}{ymd8}-{seq:03d}"


def build_linkage_records(event, objects, *, created_at=None, note=None):
    """事件→关联记录(纯函数,配号面独立于匹配面;配号按写入序)。

    返回记录列表(未落档);created_at 显式注入(缺省墙钟,测试恒显式)。
    记录零原始数值字段(P-B-10);digest_snapshot=rp.digest_snapshot 重算值
    (事件构造时已重算,此处直取事件字典——构造器禁采声明值在先,要点④)。"""
    created_at = created_at or _now_iso()
    entries = match_event(event, objects)
    records = []
    for i, e in enumerate(entries):
        linkage_id = (f"{LINKAGE_ID_PREFIX}{_ymd8_of(created_at)}"
                      f"-{_same_day_max_seq_seq_placeholder(i):03d}")
        records.append({
            "record_type": "evidence_linkage",
            "linkage_id": linkage_id,
            "event_kind": event["event_kind"],
            "evidence_key": event["evidence_key"],
            "object_type": e["object_type"],
            "object_id": e["object_id"],
            "match_layer": e["match_layer"],
            "anchor_key": e["anchor_key"],
            "metric_id": e["metric_id"],
            "trigger_id": e["trigger_id"],
            "condition_status": e["condition_status"],
            "suggested_action": e["suggested_action"],
            "snapshot_id": event["snapshot_id"],
            "digest_snapshot": event["digest"],
            "created_at": created_at,
            "history": [{"ts": created_at,
                         "note": note or "新证据关联条目(append-only;建议动作不直接改任何状态)"}],
        })
    return records


def _same_day_max_seq_seq_placeholder(i):
    """配号占位(1 起顺序);record_linkages 落档前按集合目录实态重配号。"""
    return i + 1


def validate_linkage_record(record):
    """关联记录全量校验(读侧 fail-loud;篡改档→ValueError)。"""
    if not isinstance(record, dict):
        raise ValueError("关联记录须为 dict")
    required = {"record_type", "linkage_id", "event_kind", "evidence_key",
                "object_type", "object_id", "match_layer", "anchor_key",
                "metric_id", "trigger_id", "condition_status",
                "suggested_action", "snapshot_id", "digest_snapshot",
                "created_at", "history"}
    missing = required - set(record.keys())
    if missing:
        raise ValueError(f"关联记录缺字段: {sorted(missing)}")
    if record["record_type"] != "evidence_linkage":
        raise ValueError(f"record_type 非法: {record['record_type']!r}")
    m = _LINKAGE_ID_RE.match(str(record["linkage_id"]))
    if not m:
        raise ValueError(f"linkage_id 须为 LNK-{{YYYYMMDD}}-{{NNN}}: "
                         f"{record['linkage_id']!r}")
    if m.group(1) != _ymd8_of(str(record["created_at"])):
        raise ValueError(f"linkage_id 日期段与 created_at 不符: "
                         f"{record['linkage_id']!r} vs {record['created_at']!r}")
    if record["event_kind"] not in EVENT_KINDS:
        raise ValueError(f"event_kind 须为 {EVENT_KINDS}: {record['event_kind']!r}")
    if not isinstance(record["evidence_key"], str) or not record["evidence_key"]:
        raise ValueError(f"evidence_key 须为非空 string: {record['evidence_key']!r}")
    if record["object_type"] not in LINK_OBJECT_TYPES:
        raise ValueError(f"object_type 须为 {LINK_OBJECT_TYPES}: "
                         f"{record['object_type']!r}")
    oid = record["object_id"]
    if not isinstance(oid, str) or not oid:
        raise ValueError(f"object_id 须为非空 string: {oid!r}")
    pref = (rri.THESIS_KEY_PREFIX if record["object_type"] == "thesis"
            else rri.VIEW_KEY_PREFIX)
    if not oid.startswith(pref):
        raise ValueError(f"object_id 须为 {pref}* 族: {oid!r}")
    if record["match_layer"] not in MATCH_LAYERS:
        raise ValueError(f"match_layer 须为 {MATCH_LAYERS}: {record['match_layer']!r}")
    if not isinstance(record["anchor_key"], str) or not record["anchor_key"]:
        raise ValueError(f"anchor_key 须为非空 string: {record['anchor_key']!r}")
    if record["trigger_id"] is not None and not (
            isinstance(record["trigger_id"], str) and record["trigger_id"]):
        raise ValueError(f"trigger_id 须为非空 string 或 null: "
                         f"{record['trigger_id']!r}")
    cs = record["condition_status"]
    if record["match_layer"] == 1 and record["event_kind"] in (
            "snapshot", "formal_report") and cs not in CONDITION_STATUSES:
        raise ValueError(f"第一层快照族条件态须为 {CONDITION_STATUSES}: {cs!r}")
    if cs is not None and cs not in CONDITION_STATUSES:
        raise ValueError(f"condition_status 须为 {CONDITION_STATUSES} 或 null: {cs!r}")
    if record["suggested_action"] not in SUGGESTED_ACTIONS:
        raise ValueError(f"suggested_action 须为 {SUGGESTED_ACTIONS}: "
                         f"{record['suggested_action']!r}")
    if record["match_layer"] == 2 and record["suggested_action"] != \
            LAYER2_SUGGESTED_ACTION:
        raise ValueError(f"第二层建议动作须为 {LAYER2_SUGGESTED_ACTION!r}: "
                         f"{record['suggested_action']!r}")
    if drr.ra.parse_snapshot_id(str(record["snapshot_id"])) is None:
        raise ValueError(f"snapshot_id 非规范: {record['snapshot_id']!r}")
    if not (isinstance(record["digest_snapshot"], str)
            and len(record["digest_snapshot"]) == 16):
        raise ValueError(f"digest_snapshot 须为 16 位指纹: "
                         f"{record['digest_snapshot']!r}")
    if not isinstance(record["history"], list) or not record["history"]:
        raise ValueError("history 须为非空列表(append-only 记录族惯例)")
    return True


def record_linkages(event, objects, *, archive_dir, created_at=None, note=None):
    """事件关联批写入(P-B-09): 匹配→配号(集合目录实态)→校验→drr._write_records
    原子落档(append-only;同 linkage_id 重放→rejected-duplicate 零写入,
    拒绝时 count/linkage_ids 如实归零)。

    返回 {status, count, linkage_ids, last_path}(count/ids=实写面,拒绝=0/[]);
    **零状态文件写入**(要点①: 不触碰 thesis/views/索引/任何权威档)。"""
    created_at = created_at or _now_iso()
    entries = match_event(event, objects)
    base_seq = _same_day_max_seq(archive_dir, _ymd8_of(created_at))
    ymd8 = _ymd8_of(created_at)
    planned, ids = [], []
    for i, e in enumerate(entries):
        linkage_id = f"{LINKAGE_ID_PREFIX}{ymd8}-{base_seq + 1 + i:03d}"
        record = {
            "record_type": "evidence_linkage",
            "linkage_id": linkage_id,
            "event_kind": event["event_kind"],
            "evidence_key": event["evidence_key"],
            "object_type": e["object_type"],
            "object_id": e["object_id"],
            "match_layer": e["match_layer"],
            "anchor_key": e["anchor_key"],
            "metric_id": e["metric_id"],
            "trigger_id": e["trigger_id"],
            "condition_status": e["condition_status"],
            "suggested_action": e["suggested_action"],
            "snapshot_id": event["snapshot_id"],
            "digest_snapshot": event["digest"],
            "created_at": created_at,
            "history": [{"ts": created_at,
                         "note": note or "新证据关联条目(append-only;建议动作不直接改任何状态)"}],
        }
        validate_linkage_record(record)
        planned.append((record, drr._record_path(archive_dir,
                                                 COLLECTION_LINKAGES, linkage_id)))
        ids.append(linkage_id)
    if not planned:
        return {"status": "noop", "count": 0, "linkage_ids": [],
                "last_path": None}
    status, last_path = drr._write_records(planned, archive_dir)
    written = len(planned) if status == drr.STATUS_WRITTEN else 0
    return {"status": status, "count": written,
            "linkage_ids": ids if written else [],
            "last_path": last_path}


def list_linkages(archive_dir):
    """读关联档案全部记录(档内逐条重校验 fail-loud;按 linkage_id 排序)。"""
    d = _linkages_dir(archive_dir)
    out = []
    if not os.path.isdir(d):
        return out
    for name in sorted(os.listdir(d)):
        if not name.endswith(".json"):
            continue
        with open(os.path.join(d, name), "r", encoding="utf-8") as f:
            record = json.load(f)
        validate_linkage_record(record)   # 篡改档→ValueError fail-loud
        out.append(record)
    return out


# ══ 聚合视图(P-B-12/P-B-13/P-B-14;只读零写入) ═══════════════════════

def _load_views(views_path):
    with open(str(views_path), "r", encoding="utf-8") as f:
        return json.load(f)


def pending_triggers_overview(thesis_path, views_path, anchors, *, as_of):
    """聚合视图①未决触发器跨期清单(P-B-12): ❓待验证/⏳持续确认中按对象聚合。

    views 直经 ae.evaluate_quant_triggers(persist=False 零副作用渲染路径);
    theses 经只读适配壳同评估器(状态文件无 thesis trigger_state 载体→连续周数
    按评估面如实起算);输出行=仅 unverifiable/sustaining 两态,确定性排序;
    数据源=状态文件(对象集)+注入锚点集(评估面)。"""
    if not isinstance(anchors, dict):
        raise ValueError(f"anchors 须为 dict(注入锚点集): {type(anchors).__name__}")
    if not _iso_date_ok(as_of):
        raise ValueError(f"as_of 须为规范 YYYY-MM-DD: {as_of!r}")
    with open(str(thesis_path), "r", encoding="utf-8") as f:
        th = json.load(f)
    views_data = _load_views(views_path)
    shim = {"views": [{"id": f"{rri.THESIS_KEY_PREFIX}{t['id']}",
                       "quant_triggers": t.get("quant_triggers") or []}
                      for t in th.get("theses") or [] if t.get("id") is not None]}
    rows = []
    thesis_rows = ae.evaluate_quant_triggers(shim, anchors, today_str=as_of,
                                             persist=False)
    for t in th.get("theses") or []:
        key = f"{rri.THESIS_KEY_PREFIX}{t['id']}"
        for r in thesis_rows.get(key) or []:
            if r["status"] in PENDING_OVERVIEW_STATUSES:
                rows.append({"object_type": "thesis", "object_id": key,
                             "asset": None, "trig_id": r["trig_id"],
                             "direction": r["direction"], "status": r["status"],
                             "status_display": TRIGGER_STATUS_DISPLAY[r["status"]],
                             "detail": r["detail"], "consec": r["consec"],
                             "sustain": r["sustain"]})
    view_rows = ae.evaluate_quant_triggers(views_data, anchors, today_str=as_of,
                                           persist=False)
    by_id = {f"{rri.VIEW_KEY_PREFIX}{v['id']}": v
             for v in views_data.get("views") or [] if v.get("id") is not None}
    for v in views_data.get("views") or []:
        key = f"{rri.VIEW_KEY_PREFIX}{v['id']}"
        for r in view_rows.get(v["id"]) or []:
            if r["status"] in PENDING_OVERVIEW_STATUSES:
                rows.append({"object_type": "view", "object_id": key,
                             "asset": (by_id.get(key) or {}).get("asset"),
                             "trig_id": r["trig_id"], "direction": r["direction"],
                             "status": r["status"],
                             "status_display": TRIGGER_STATUS_DISPLAY[r["status"]],
                             "detail": r["detail"], "consec": r["consec"],
                             "sustain": r["sustain"]})
    rows.sort(key=lambda r: (r["object_type"], r["object_id"], r["trig_id"]))
    return rows


def due_adjudications_overview(views_path, *, as_of):
    """聚合视图②到期预测裁决待办(P-B-13): ae.due_predictions 在场复用
    (⏰已到期口径: 未决态且 deadline≤as_of);按 pred_id 排序;只读零写入。"""
    if not _iso_date_ok(as_of):
        raise ValueError(f"as_of 须为规范 YYYY-MM-DD: {as_of!r}")
    views_data = _load_views(views_path)
    rows = [{"pred_id": p.get("pred_id"), "asset": p.get("asset"),
             "status": p.get("status"), "deadline": p.get("deadline"),
             "metric": p.get("metric"), "direction": p.get("direction")}
            for p in ae.due_predictions(views_data, today_str=as_of)]
    rows.sort(key=lambda r: str(r["pred_id"]))
    return rows


def render_tracking_briefing(thesis_path, views_path, anchors=None, *, as_of):
    """旁路简报渲染(P-B-14): 两聚合清单纯文本+免责尾行;零写入零回写路径。"""
    lines = [f"持续跟踪聚合简报(as_of={as_of};旁路简报,不改周报系统回写路径)"]
    pending = (pending_triggers_overview(thesis_path, views_path, anchors,
                                         as_of=as_of)
               if isinstance(anchors, dict) else [])
    lines.append("")
    lines.append(f"## 未决触发器跨期清单(❓待验证/⏳持续确认中;{len(pending)} 项 [实取·本渲染清点])")
    if pending:
        lines.append("| 对象 | 资产 | 触发器 | 方向 | 状态 | 详情 |")
        lines.append("|------|------|--------|------|------|------|")
        for r in pending:
            lines.append(f"| {r['object_id']} | {r['asset'] or '-'} | "
                         f"{r['trig_id']} | {r['direction']} | "
                         f"{r['status_display']} | {r['detail']} |")
    else:
        lines.append("(无未决触发器[如实清点,缺值不冒充];"
                     "未注入锚点集时本清单不渲染[评估面如实缺席])"
                     if not isinstance(anchors, dict) else
                     "(无未决触发器[如实清点,缺值不冒充])")
    due = due_adjudications_overview(views_path, as_of=as_of)
    lines.append("")
    lines.append(f"## 到期预测裁决待办(⏰已到期;{len(due)} 项 [实取·本渲染清点])")
    if due:
        lines.append("| pred_id | 资产 | 状态 | 截止日 | 规格 |")
        lines.append("|---------|------|------|--------|------|")
        for r in due:
            lines.append(f"| {r['pred_id']} | {r['asset'] or '-'} | {r['status']} "
                         f"| {r['deadline']} | {r['metric'] or '-'} |")
    else:
        lines.append("(无到期待办[如实清点,缺值不冒充])")
    lines.append("")
    lines.append(DISCLAIMER_NOTE)
    return "\n".join(lines)


# ══ 自检入口(零写入;不落默认路径) ═══════════════════════════════════

def _selfcheck():
    ok = param_selfcheck()
    print(f"evidence_linkage selfcheck: param_selfcheck={ok}; "
          f"EVENT_KINDS={len(EVENT_KINDS)}; MATCH_LAYERS={MATCH_LAYERS}; "
          f"MECHANISM_CATEGORIES={len(MECHANISM_CATEGORIES)}")
    print(DISCLAIMER_NOTE)
    return ok


if __name__ == "__main__":
    _selfcheck()
