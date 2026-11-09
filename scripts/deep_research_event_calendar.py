#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P2-WP-D: 事件序列数据面(议息/发布事件结构化日历;P2 深研层第 4 实现包,族末)

DESIGN docs/P2_DESIGN.md §七 WP-P2-D 行(L211-L215,基线工作树实读)确定性落地,
消除 P2-G-04(docs/P2_INVENTORY.md L163「事件序列结构化日历零在场(议息/发布日)」):
- 事件档格式(L213「事件档格式」): CalendarEvent 记录=append-only 落共享档案族根
  新集合 calendar_events(经 WP-P2-A deep_research_registrar 写入原语,复用调用
  禁复制分叉);ID 族 CAL-{YYYYMMDD}-{sha256[:8]} 确定性指纹(P-D-02,避开上游
  已占 RT-DR-/HP-/FC-/EV-/EVI-/RD-/TRG-/CON-/DSP-;指纹不含墙钟,重放幂等);
- 来源登记(L215①,DP-5(a) 白名单登记制): SOURCE_WHITELIST 常量=免费公开官方源
  三源(每源 access=free_public/credentials=none/cost=none);事件档 source_id 必须
  在白名单且 source_url 由模块按白名单登记值回填(调用面无 URL 入参,登记值唯一
  来源=白名单常量);**本模块全生存期零访问任何源 URL**(零网络出站,AC-07.4
  绝对边界;真实抓取属预授权③运行面,由操作者另行排程,不在本包);付费源零
  登记零实施(确认权留用户,DP-5(b) PENDING);
- 快照挂载与事件窗对齐计算(L213「快照挂载」+L215②): 一切窗取数经研究快照
  三重纪律(P-D-07: drr._load_snapshot_for_verify 规范加载,结构性不可达
  原始采集档 + rp.digest_snapshot 内容重算绑定(禁采声明值) + rp.
  gate_allows_formal_research 放行核验;Gate A=FAIL→fail-closed 拒收,
  DESIGN §3.1 L80);窗观测=快照 facts 内该 metric 的窗内条目(携 fact_id
  provenance);窗口口径(P-D-06): pre 窗=[event_date-pre_days, event_date-1]
  自然日闭区间不含事件日,post 窗=[event_date, event_date+post_days] 闭区间
  含事件日,两窗结构性不重叠;质量纪律(P-D-08): quality_status=FAIL 的观测
  排除出数值观测并如实入 excluded_fail 清单(不填 0);value 非数值→排除入
  excluded_non_numeric;窗内零合格观测→结构化 DATA_INSUFFICIENT
  (available=False,数据不足如实缺席,DESIGN §八 L228 如实纪律)。

范围排除(DESIGN L213/L214): 事件窗计算的**消费方**在 WP-P2-B(其范围列明文
「事件日历(D3)另包」,本包提供可独立调用的确定性窗计算函数,不改其在场件);
最小集=FOMC 议息日+本注册表高频引用指标发布日(DESIGN L212 提案,登记定值
见 REPORT §零.5 P-D-05: INDICATOR_RELEASE 白名单 {CPI, CORE_CPI, NFP,
NFP_MOM_K},依据=主流水线 8 模块词边界引用计数实取≥2;FOMC_RATE_DECISION
关联 metric∈{None, DFEDTARU, DFEDTARL})。

纪律: 零网络(import 面白名单 json/os/sys/datetime+项目既有 drr/rp/fe,
P-D-10);零模型调用/凭证/付费;append-only(重复/改写一律拒,族先例);零墙钟入
指纹;registry 解析经 fe.metric() 复用(P-D-11,零 registry 直读复制);本
模块输出为研究结构面数据,**不构成投资建议**(DESIGN §八 L225 红线承接)。
参数登记: docs/P2_WP_D_REPORT.md §零.4/§零.5(DP 处置+P-D-01..P-D-13,
先登记后实现,运行后禁回改)。
"""
import json
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deep_research_registrar as drr   # WP-P2-A 上游(复用调用,只读禁改)
import research_provenance as rp        # R5 digest_snapshot/R3 gate_allows_formal_research
import fact_engine as fe                # registry 经 fe.metric() 在场接口(P-D-11)

# ══ 载体与集合(P-D-01;挂共享档案族根,不占上游既有集合名) ═══════════════

ARCHIVE_FAMILY = drr.ARCHIVE_FAMILY                    # "research_archive"(复用引用)
COLLECTION_CALENDAR = "calendar_events"
DEFAULT_ARCHIVE_DIR = drr.DEFAULT_ARCHIVE_DIR          # data/research/research_archive

RECORD_TYPE = "calendar_event"
EVENT_ID_PREFIX = "CAL-"            # DP-3: 避开上游已占 RT-DR-/HP-/FC-/EV-/EVI-/RD-/TRG-/CON-/DSP-

# ══ 词表与白名单(P-D-03/P-D-04/P-D-05;登记定值,运行后禁回改) ═══════════

EVENT_TYPES = ("FOMC_RATE_DECISION", "INDICATOR_RELEASE")   # DESIGN L212 最小集两类

# 免费源 URL 白名单(登记制;DP-5(a) 循预授权③;登记不访问,零网络零凭证零付费)。
# url=官方机构公开日历/发布计划页登记值(本模块与测试全生存期零访问);
# supports=该源被登记支持的 event_type 集。
SOURCE_WHITELIST = {
    "SRC_FED": {
        "publisher": "Federal Reserve Board",
        "url": "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
        "access": "free_public", "credentials": "none", "cost": "none",
        "supports": ("FOMC_RATE_DECISION",),
    },
    "SRC_BLS_CPI": {
        "publisher": "U.S. Bureau of Labor Statistics",
        "url": "https://www.bls.gov/schedule/news_release/cpi.htm",
        "access": "free_public", "credentials": "none", "cost": "none",
        "supports": ("INDICATOR_RELEASE",),
    },
    "SRC_BLS_EMPSIT": {
        "publisher": "U.S. Bureau of Labor Statistics",
        "url": "https://www.bls.gov/schedule/news_release/empsit.htm",
        "access": "free_public", "credentials": "none", "cost": "none",
        "supports": ("INDICATOR_RELEASE",),
    },
}

# 最小集指标绑定(P-D-05;registry 高频引用指标,登记定值)
INDICATOR_METRIC_WHITELIST = ("CPI", "CORE_CPI", "NFP", "NFP_MOM_K")
FOMC_METRIC_WHITELIST = ("DFEDTARU", "DFEDTARL")   # FOMC 议息决定的利率目标区间通道(可无绑定)

# 事件窗口径(P-D-06;自然日,pre 不含事件日/post 含事件日)
WINDOW_PRE_DEFAULT = 5
WINDOW_POST_DEFAULT = 5

DISCLAIMER_NOTE = "研究结构面输出,不构成投资建议(禁交易/禁仓位/禁收益承诺)"

QUALITY_REJECTED = ("FAIL",)          # FAIL 事实不得作窗内数值观测(不填 0,如实排除)


# ══ 基础件(上游原语复用;零墙钟入指纹) ═════════════════════════════════

def _now_iso():
    return drr._now_iso()


def _parse_ymd(s):
    """YYYY-MM-DD 严格解析;非法→None(fail-loud 由调用侧拒)。"""
    if not isinstance(s, str):
        return None
    try:
        d = datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        return None
    if d.strftime("%Y-%m-%d") != s:      # 拒 2026-1-5 之类非规范表示
        return None
    return d.date()


def _shift_ymd(s, days):
    """自然日平移(s 合法 YYYY-MM-DD);days 可负。"""
    return (_parse_ymd(s) + timedelta(days=days)).strftime("%Y-%m-%d")


def make_calendar_event_id(source_id, event_type, event_date, metric_id,
                           note, created_at):
    """CAL-{YYYYMMDD}-{sha256[:8]}: 指纹件={source_id, event_type, event_date,
    metric_id, note}(P-D-02;不含墙钟内容——ymd 仅取自 created_at 日期段,
    重放幂等,族先例 EVI- 同款纪律)。"""
    fp = {"source_id": source_id, "event_type": event_type,
          "event_date": event_date, "metric_id": metric_id, "note": note}
    return f"{EVENT_ID_PREFIX}{drr._ymd_of(created_at)}-{drr._hash8(fp)}"


# ══ 事件档校验(P-D-02..P-D-05;issues 列表风格,空=合法) ═════════════════

CALENDAR_KEYS = ("record_type", "event_id", "created_at", "event_type",
                 "event_date", "source_id", "source_url", "metric_id",
                 "note", "history")


def _metric_registry_issue(metric_id, label):
    """registry 在场核验(经 fe.metric 复用,零直读复制)。"""
    if fe.metric(metric_id) is None:
        return (f"{label}={metric_id!r} 不在 metric_registry 在场集"
                f"(经 fe.metric 解析失败,不以相近指标冒充)")
    return None


def validate_calendar_event(record):
    """事件档全量校验(fail-loud;返回 issues 列表,空=合法)。

    覆盖: 记录类型/字段齐备/ID 族前缀与指纹重算一致(防篡改)/事件类型词表/
    event_date 规范日期/来源白名单(source_id 登记+source_url 与登记值逐字相等
    +类型被该源支持)/最小集指标绑定(INDICATOR_RELEASE∈白名单且 registry 在场;
    FOMC∈{None}∪DFEDTAR 通道且在场)/created_at ISO/history 结构。"""
    issues = []
    if not isinstance(record, dict):
        return ["事件档须为dict: " + type(record).__name__]
    if record.get("record_type") != RECORD_TYPE:
        issues.append(f"record_type须为{RECORD_TYPE}: {record.get('record_type')!r}")
    for k in CALENDAR_KEYS:
        if k not in record:
            issues.append(f"事件档缺字段{k}(P-D-02)")
    if issues:
        return issues
    eid = record.get("event_id")
    if not (isinstance(eid, str) and eid.startswith(EVENT_ID_PREFIX)):
        issues.append(f"event_id须为{EVENT_ID_PREFIX}*族: {eid!r}")
    et = record.get("event_type")
    if et not in EVENT_TYPES:
        issues.append(f"event_type非法: {et!r}(词表{EVENT_TYPES},DESIGN L212 最小集)")
    if _parse_ymd(record.get("event_date")) is None:
        issues.append(f"event_date须为规范YYYY-MM-DD: {record.get('event_date')!r}")
    ca = record.get("created_at")
    if not isinstance(ca, str) or len(ca) < 10 or _parse_ymd(ca[:10]) is None:
        issues.append(f"created_at须为ISO时间串: {ca!r}")
    sid = record.get("source_id")
    src = SOURCE_WHITELIST.get(sid)
    if src is None:
        issues.append(f"source_id不在免费源白名单(登记制,DP-5(a)): {sid!r}"
                      f"(已登记源: {sorted(SOURCE_WHITELIST)})")
    else:
        if record.get("source_url") != src["url"]:
            issues.append(f"source_url与白名单登记值不符: {record.get('source_url')!r}"
                          f" ≠ {src['url']!r}(登记值唯一来源=白名单常量)")
        if et not in src["supports"]:
            issues.append(f"源{sid}不支持事件类型{et!r}(登记支持集{src['supports']})")
    mid = record.get("metric_id")
    if et == "INDICATOR_RELEASE":
        if mid not in INDICATOR_METRIC_WHITELIST:
            issues.append(f"INDICATOR_RELEASE的metric_id须∈最小集白名单"
                          f"{INDICATOR_METRIC_WHITELIST}(P-D-05): {mid!r}")
        else:
            m = _metric_registry_issue(mid, "metric_id")
            if m:
                issues.append(m)
    elif et == "FOMC_RATE_DECISION":
        if mid is not None:
            if mid not in FOMC_METRIC_WHITELIST:
                issues.append(f"FOMC_RATE_DECISION的metric_id须为None或"
                              f"∈{FOMC_METRIC_WHITELIST}: {mid!r}")
            else:
                m = _metric_registry_issue(mid, "metric_id")
                if m:
                    issues.append(m)
    # ID 指纹重算一致(防篡改;指纹不含墙钟,重放幂等)
    if isinstance(eid, str) and eid.startswith(EVENT_ID_PREFIX) \
            and isinstance(ca, str) and len(ca) >= 10 \
            and _parse_ymd(record.get("event_date")) is not None:
        expect = make_calendar_event_id(sid, et, record.get("event_date"),
                                        mid, record.get("note"), ca)
        if eid != expect:
            issues.append(f"event_id与指纹重算不符(档被篡改或ID伪造): "
                          f"{eid!r} ≠ 重算{expect!r}")
    if not isinstance(record.get("history"), list) or not record["history"]:
        issues.append("history须为非空list(append-only留痕)")
    return issues


# ══ 事件登记入口(append-only;P-D-12 经 drr 写入原语) ═══════════════════

def register_calendar_event(spec, *, archive_dir=None, created_at=None):
    """日历事件登记(append-only;校验全过→落档,任一不过→拒收零写入)。

    spec={source_id, event_type, event_date, metric_id(可None仅FOMC), note(可None)};
    source_url **无入参**——由模块按白名单登记值回填(登记制,调用面不可伪造)。
    同输入重放→同 event_id→STATUS_REJECTED_DUPLICATE 拒(append-only)。"""
    if not isinstance(spec, dict):
        raise ValueError("事件规格须为dict: " + type(spec).__name__)
    ad = archive_dir or DEFAULT_ARCHIVE_DIR
    ca = created_at or _now_iso()
    sid = spec.get("source_id")
    src = SOURCE_WHITELIST.get(sid)
    if src is None:
        raise ValueError(f"source_id不在免费源白名单(登记制,DP-5(a)): {sid!r}")
    missing = [k for k in ("event_type", "event_date") if k not in spec]
    if missing:
        raise ValueError("事件规格缺字段: " + ",".join(missing))
    event_id = make_calendar_event_id(sid, spec["event_type"],
                                      spec["event_date"], spec.get("metric_id"),
                                      spec.get("note"), ca)
    record = {"record_type": RECORD_TYPE, "event_id": event_id,
              "created_at": ca, "event_type": spec["event_type"],
              "event_date": spec["event_date"], "source_id": sid,
              "source_url": src["url"], "metric_id": spec.get("metric_id"),
              "note": spec.get("note"),
              "history": [{"ts": ca, "note": "日历事件登记入档(append-only;"
                           "免费源白名单登记制;零网络零凭证零付费)"}]}
    issues = validate_calendar_event(record)
    if issues:
        raise ValueError("日历事件校验未过(fail-loud): " + ";".join(issues))
    status, last = drr._write_records(
        [(record, drr._record_path(ad, COLLECTION_CALENDAR, event_id))], ad)
    return {"status": status, "event_id": event_id, "path": last}


def list_calendar_events(archive_dir=None):
    """全部日历事件档(按 event_date,event_id 升序;档内逐条重校验 fail-loud)。"""
    d = os.path.join(str(archive_dir or DEFAULT_ARCHIVE_DIR),
                     ARCHIVE_FAMILY, COLLECTION_CALENDAR)
    out = []
    if os.path.isdir(d):
        for name in sorted(os.listdir(d)):
            if not name.endswith(".json") or name.startswith("."):
                continue
            with open(os.path.join(d, name), 'r', encoding='utf-8') as f:
                rec = json.load(f)
            issues = validate_calendar_event(rec)
            if issues:
                raise ValueError(f"日历事件档内校验失败({name}): "
                                 + ";".join(issues))
            out.append(rec)
    return sorted(out, key=lambda r: (r["event_date"], r["event_id"]))


# ══ 快照三重纪律(P-D-07;挂载与窗计算共用;WP-B/C 同款) ═════════════════

def load_snapshot_disciplined(snapshot_id, snapshot_dir):
    """三重纪律加载: ①drr._load_snapshot_for_verify 规范分解加载(结构性不可达
    原始采集档)②rp.digest_snapshot 内容重算绑定(禁采声明值)③Gate A 放行核验
    (FAIL→fail-closed,DESIGN §3.1 L80)。

    返回 (snapshot, digest, gate_status);任一不过→(None, None, None, err)
    四元组第 4 位为拒收原因(调用侧 fail-loud)。"""
    snap, load_err = drr._load_snapshot_for_verify(snapshot_id, snapshot_dir)
    if snap is None:
        return None, None, None, f"快照接地失败: {load_err}"
    gate_status = (snap.get("gate_a") or {}).get("status")
    if not rp.gate_allows_formal_research(gate_status):
        return None, None, None, (f"Gate A={gate_status!r} 不放行正式研究"
                                  f"(PASS/DEGRADED 之外,DESIGN §3.1 红线),"
                                  f"本快照不得作为深研正式证据源: {snapshot_id}")
    digest = rp.digest_snapshot(snap)
    return snap, digest, gate_status, None


# ══ 事件窗口径(P-D-06) ═════════════════════════════════════════════════

def event_window_bounds(event_date, pre_days, post_days):
    """窗口边界: pre=[event_date-pre_days, event_date-1](不含事件日)、
    post=[event_date, event_date+post_days](含事件日);自然日闭区间。
    event_date 非法或 days 非 int≥0 → ValueError(fail-loud)。"""
    if _parse_ymd(event_date) is None:
        raise ValueError(f"event_date须为规范YYYY-MM-DD: {event_date!r}")
    for name, v in (("pre_days", pre_days), ("post_days", post_days)):
        if isinstance(v, bool) or not isinstance(v, int) or v < 0:
            raise ValueError(f"{name}须为int≥0: {v!r}(P-D-06)")
    return {"pre": (_shift_ymd(event_date, -pre_days),
                    _shift_ymd(event_date, -1)),
            "post": (event_date, _shift_ymd(event_date, post_days))}


def classify_observation(observation_date, bounds):
    """观测归属: observation_date 落 pre 窗→"pre";落 post 窗→"post";
    两窗结构性不重叠;窗外→None。非法日期→ValueError(fail-loud)。"""
    od = _parse_ymd(observation_date)
    if od is None:
        raise ValueError(f"observation_date须为规范YYYY-MM-DD: {observation_date!r}")
    ps, pe = (_parse_ymd(x) for x in bounds["pre"])
    qs, qe = (_parse_ymd(x) for x in bounds["post"])
    if ps <= od <= pe:
        return "pre"
    if qs <= od <= qe:
        return "post"
    return None


# ══ 事件窗对齐计算(DESIGN L215②;事件前后窗口取数经快照) ═══════════════

def event_window_observations(event, snapshot_id, snapshot_dir, *,
                              metric_id=None, pre_days=WINDOW_PRE_DEFAULT,
                              post_days=WINDOW_POST_DEFAULT):
    """事件窗对齐计算: 经快照三重纪律取该 metric 在事件前后窗内的观测集。

    event=已登记事件档(dict);metric_id 缺省取事件绑定(事件无绑定且未显式
    给→ValueError,不以相近指标冒充);窗内观测=快照 facts 中该 metric_id 的
    条目按窗归属分类;每条观测携 fact_id provenance+snapshot_id+digest 绑定;
    FAIL 质量/非数值观测如实排除入清单(不填 0);零合格观测→DATA_INSUFFICIENT
    (available=False)。挂载/窗输出不构成投资建议。"""
    if not isinstance(event, dict):
        raise ValueError("event须为dict(已登记事件档): " + type(event).__name__)
    issues = validate_calendar_event(event)
    if issues:
        raise ValueError("事件档校验未过(fail-loud): " + ";".join(issues))
    mid = metric_id if metric_id is not None else event.get("metric_id")
    if mid is None:
        raise ValueError("事件无 metric 绑定且未显式给定 metric_id"
                         "(不以相近指标冒充,DESIGN §6.1 推导规则①同款纪律)")
    snap, digest, gate_status, err = load_snapshot_disciplined(snapshot_id,
                                                               snapshot_dir)
    if snap is None:
        raise ValueError(f"事件窗计算快照纪律未过(fail-closed): {err}")
    bounds = event_window_bounds(event["event_date"], pre_days, post_days)
    facts = snap.get("facts")
    if not isinstance(facts, list):
        raise ValueError("快照缺facts事实列表(非规范研究快照结构)")
    observations, excluded_fail, excluded_non_numeric = [], [], []
    for fact in facts:
        if not isinstance(fact, dict) or fact.get("metric_id") != mid:
            continue
        od = fact.get("observation_date")
        side = classify_observation(od, bounds)
        if side is None:
            continue
        entry = {"fact_id": fact.get("fact_id"),
                 "observation_date": od, "value": fact.get("value"),
                 "quality_status": fact.get("quality_status"),
                 "window_side": side}
        if fact.get("quality_status") in QUALITY_REJECTED:
            excluded_fail.append(entry)      # 如实排除,不填 0
        elif isinstance(fact.get("value"), bool) or not isinstance(fact.get("value"), (int, float)):
            excluded_non_numeric.append(entry)
        else:
            observations.append(entry)
    observations.sort(key=lambda o: (o["observation_date"], str(o["fact_id"])))
    excluded_fail.sort(key=lambda o: (o["observation_date"], str(o["fact_id"])))
    excluded_non_numeric.sort(key=lambda o: (o["observation_date"], str(o["fact_id"])))
    available = bool(observations)
    return {"event_id": event["event_id"], "metric_id": mid,
            "snapshot_id": snapshot_id, "digest_snapshot": digest,
            "gate_a_status": gate_status,
            "window": {"pre_days": pre_days, "post_days": post_days,
                       "pre": {"start": bounds["pre"][0], "end": bounds["pre"][1]},
                       "post": {"start": bounds["post"][0], "end": bounds["post"][1]}},
            "observations": observations,
            "excluded_fail": excluded_fail,
            "excluded_non_numeric": excluded_non_numeric,
            "available": available,
            "status": "OK" if available else "DATA_INSUFFICIENT",
            "note": DISCLAIMER_NOTE}


# ══ 快照挂载(P-D-09;读侧纯计算面,零写入) ══════════════════════════════

def mount_event_context(events, snapshot_id, snapshot_dir, *,
                        pre_days=WINDOW_PRE_DEFAULT,
                        post_days=WINDOW_POST_DEFAULT, as_of=None):
    """事件上下文挂载到快照(DESIGN L213「快照挂载」;沿 D4 挂载先例,
    DESIGN §3.2 D4 行 L89「经快照/数据包挂载消费」)。

    三重纪律过闸后,把「事件窗与快照观测日期面相交」的事件与快照绑定成
    上下文(供消费方——WP-P2-B 事件窗计算消费面——确定性消费):
    {snapshot_id, digest_snapshot, gate_a_status, event_ids 升序,
    future_excluded(as_of 给定时未来事件如实排除清单), window, note}。
    Gate A=FAIL→fail-closed 拒收;纯计算面零写入。"""
    if not isinstance(events, list):
        raise ValueError("events须为list(事件档列表): " + type(events).__name__)
    for ev in events:
        if not isinstance(ev, dict):
            raise ValueError("events成员须为dict: " + type(ev).__name__)
        issues = validate_calendar_event(ev)
        if issues:
            raise ValueError("事件档校验未过(fail-loud): " + ";".join(issues))
    if as_of is not None and _parse_ymd(as_of) is None:
        raise ValueError(f"as_of须为规范YYYY-MM-DD: {as_of!r}")
    snap, digest, gate_status, err = load_snapshot_disciplined(snapshot_id,
                                                               snapshot_dir)
    if snap is None:
        raise ValueError(f"事件挂载快照纪律未过(fail-closed): {err}")
    facts = snap.get("facts")
    if not isinstance(facts, list):
        raise ValueError("快照缺facts事实列表(非规范研究快照结构)")
    obs_dates = [f.get("observation_date") for f in facts
                 if isinstance(f, dict) and _parse_ymd(f.get("observation_date"))]
    if obs_dates:
        face_min, face_max = min(obs_dates), max(obs_dates)
    else:
        face_min = face_max = None
    included_ids, future_excluded = [], []
    for ev in events:
        bounds = event_window_bounds(ev["event_date"], pre_days, post_days)
        if as_of is not None and ev["event_date"] > as_of:
            future_excluded.append({"event_id": ev["event_id"],
                                    "event_date": ev["event_date"],
                                    "reason": "event_date>as_of(未来事件,如实排除)"})
            continue
        if face_min is not None:
            w_start, w_end = bounds["pre"][0], bounds["post"][1]
            if w_end < face_min or w_start > face_max:
                continue          # 事件窗与快照观测日期面不相交(窗外事件不挂载)
        included_ids.append(ev["event_id"])
    return {"snapshot_id": snapshot_id, "digest_snapshot": digest,
            "gate_a_status": gate_status,
            "event_ids": sorted(included_ids),
            "future_excluded": sorted(future_excluded,
                                      key=lambda x: (x["event_date"], x["event_id"])),
            "window": {"pre_days": pre_days, "post_days": post_days},
            "note": DISCLAIMER_NOTE + ";挂载上下文零写入(读侧纯计算面)"}


# ══ 自检入口(零网络零凭证零付费;python3 scripts/deep_research_event_calendar.py --selfcheck) ══

def _selfcheck():
    ok = []
    for sid, src in SOURCE_WHITELIST.items():
        assert src["access"] == "free_public", sid
        assert src["credentials"] == "none", sid
        assert src["cost"] == "none", sid
        assert src["url"].startswith("https://"), sid
        assert src["supports"] and all(t in EVENT_TYPES for t in src["supports"]), sid
        ok.append(sid)
    print("selfcheck OK: 白名单 %d 源全部免费/零凭证/零付费/https: %s"
          % (len(ok), ",".join(sorted(ok))))


if __name__ == "__main__":
    _selfcheck()
