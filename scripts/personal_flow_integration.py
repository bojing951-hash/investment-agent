#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P3-WP-E: 个人流程整合接口(P3 收尾层第 5 实现包;#37 挂靠)

DESIGN docs/P3_DESIGN.md §7 WP-P3-E 行(L194-L198,基线工作树实读)确定性落地:
§6.2 接口 3 个(用户 2026-11-08 实批「批准,发车 #37」三接口同批全启,DP-9
确认型——冻结章 §十一 凭证,注入摘要非工作树实读;启用时点=即日):

- 接口(a) 个人技术分析标注: 结构化标注格式(日期/资产/观点/依据,§6.2 L158)
  + 旁路标注档(JSONL append-only,§8.5 L220「标注档只追加」红线);
  rg L545 周报「技术分析部分标注 [待用户补充]」槽位语义的旁路结构化扩展,
  周报系统零触碰(白名单 M=0 结构性保障);
- 接口(b) 个人研究笔记引用: 登记格式=档键+指标引用+日期(L159),source_level
  恒「个人观察」系统强制——与证据分级 v2 词表(rg L518 机制 7 类/evidence
  项字段)严格隔离,不冒充程序验证证据,不参与星级与门禁核验;
- 接口(c) 复盘结论导出: 质量 §6.1 简报+§5 错误模式统计(WP-D 编排面
  report_quality_review() 产出原样承载)单向导出渲染,零回读(L160)。

三红线(随 DP-9 一并实批,§6.2 L155 设计原则):
1. 零主动采集——系统不采集任何用户私有流程数据;一切输入=用户主动推送/标注
   (零网络 import/零目录扫描/零监视;模块级路径常量唯一=_DEV_ROOT 守卫用);
2. 来源等级隔离——个人观察≠程序验证证据(三面隔离: 词表/键集/渲染);
3. 用户数据零落 LIVE——写入域双守卫: LIVE 根四组件序列拒(读写面)+写入
   路径限 DEV 仓或显式 user_root 指定目录(L196「用户数据落 DEV 或用户
   指定路径」)。

快照纪律守卫(§3.1/AC-07.1): data+daily 相邻路径组件 fail-loud(同族
WP-D P-D-04 先例,守卫字面量组件化,源码零连续字面量)。

纪律: 零网络零模型调用零凭证零付费(import 面白名单 json/os/sys+项目既有
report_quality_review);本模块输出为个人流程整合接口面数据,**不构成投资
建议**(§8.3 红线: 禁交易/禁仓位/禁收益承诺;标注/笔记=用户个人观点,系统
零采集零核验零背书)。
参数登记: docs/P3_WP_E_REPORT.md §零.4/§零.5(DP-9+P-E-01..P-E-19,
先登记后实现,运行后禁回改)。
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import report_quality_review as rqr   # WP-P3-D(依赖列前件;STATS_SCHEMA_VERSION 复用锚)

# ══ 登记型参数定值(REPORT §零.4/§零.5;登记定值即实现值,运行后禁回改) ═══

DP9_INTERFACE_SET = ("annotation", "note_reference", "export")   # P-E-02 三接口同批全启
DP9_USER_APPROVAL = "user_approved_2026-11-08_immediate"         # P-E-02 用户实批+即日启用标记

ANNOTATION_SCHEMA_VERSION = 1        # P-E-03
NOTE_SCHEMA_VERSION = 1              # P-E-05
EXPORT_SCHEMA_VERSION = 1            # P-E-07

ANNOTATION_MARKER = "ANN-"           # P-E-12 档键族
NOTE_MARKER = "NOTE-"                # P-E-12
ID_SEQ_MIN, ID_SEQ_MAX = 1, 999      # P-E-12 3 位序号界

NOTE_SOURCE_LEVEL = "个人观察"       # P-E-05/P-E-06 系统强制来源等级
SOURCE_LEVEL_LABEL = ("来源等级=个人观察(证据分级外,不参与星级与门禁核验)")

# P-E-06 隔离对照词表(只读登记锚,rg L518 词面;零评级用途)
EVIDENCE_GRADING_V2_MECHANISMS = ("信用", "避险与估值", "供应与库存",
                                  "利率与流动性", "增长", "通胀", "资金流")
STAR_LEVEL_STRINGS = ("1", "2", "3", "4", "5")
V2_EVIDENCE_ITEM_FIELDS = ("contrary", "explained", "mechanism", "metric",
                           "neutral", "obs_date", "value")

# P-E-03/P-E-05 记录字段封闭集(字典序)
_ANNOTATION_FIELDS = ("annotation_id", "asset", "basis", "date",
                      "schema_version", "view")
_NOTE_FIELDS = ("archive_key", "date", "metric_refs", "note_id",
                "schema_version", "source_level")
# P-E-07 导出文档字段集(字典序;全 str 键)
_EXPORT_FIELDS = ("as_of", "error_pattern_statistics", "note",
                  "quality_briefing", "schema_version", "suggestions",
                  "window_end", "window_kind", "window_start")

# 三红线常量(P-E-14;§6.2 L155 设计原则词面承载)
ZERO_ACTIVE_COLLECTION = ("零主动采集: 系统不采集用户私有流程数据,"
                          "一切输入=用户主动推送/标注")
SOURCE_LEVEL_ISOLATION = ("来源等级隔离: 个人观察≠程序验证证据,"
                          "证据分级外单列,不参与星级与门禁")
ZERO_LIVE_FALL = "用户数据零落 LIVE: 落 DEV 仓或用户指定路径"

# 快照纪律守卫组件(P-E-11;os.path.join 形拼装比对,源码零连续字面量)
_RAW_DIR_GUARD = ("data", "daily")
# LIVE 根守卫组件(P-E-10;四组件序列比对,源码零连续 LIVE 路径字面量)
_LIVE_ROOT_GUARD = ("AI内容", "🤖_AI投资项目", "每周宏观追踪", "investment-agent")

# 写入域锚(P-E-10): DEV 仓根=本模块所在 scripts/ 上一级(只读推导,零写入用途)
_DEV_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INTEGRATION_NOTE = ("个人流程整合接口(DP-9 用户实批 2026-11-08 三接口同批"
                    "全启[冻结章凭证,注入摘要];三红线: 零主动采集/个人观察"
                    "不冒充程序验证证据/用户数据零落 LIVE;旁路标注档"
                    "append-only;导出单向零回读);标注/笔记=用户个人观点,"
                    "系统零采集零核验零背书;不构成投资建议"
                    "(禁交易/禁仓位/禁收益承诺)")

EXPORT_NOTE = ("个人复盘结论导出(系统→用户单向导出·零回读;质量简报=§6.1"
               "产物 WP-P3-D 原样承载,错误模式统计=§5 产物 WP-P3-C 原样"
               "承载,建议清单 requires_user_confirmation=true 标记随上游"
               "原样携带);不构成投资建议(禁交易/禁仓位/禁收益承诺)")

_ANNOTATION_TAIL = ("标注为用户主动填写的个人观点,系统零采集零核验零背书"
                    "(零主动采集红线);不构成投资建议(禁交易/禁仓位/禁收益承诺)")
_NOTE_TAIL = ("个人观察=用户主动导入的笔记引用,来源等级与程序验证证据严格"
              "隔离(证据分级外,不参与星级与门禁核验);不构成投资建议"
              "(禁交易/禁仓位/禁收益承诺)")
_EXPORT_TAIL = ("本导出为系统→用户个人复盘流程的单向材料(零回读: 用户流程"
                "数据不经本接口回流);不构成投资建议(禁交易/禁仓位/禁收益承诺)")

_NA = "N/A(分母=0,如实缺席)"

# 模块内登记镜像(dp_selfcheck 哨兵对照源;与 REPORT §零.4/§零.5 登记值一致)
_DP_REGISTERED = {
    "DP-9": "annotation+note_reference+export@user_approved_2026-11-08_immediate",
}
_PARAM_REGISTERED = {
    "interface_set": ("annotation", "note_reference", "export"),
    "annotation_schema_version": 1,
    "note_schema_version": 1,
    "export_schema_version": 1,
    "annotation_marker": "ANN-",
    "note_marker": "NOTE-",
    "note_source_level": "个人观察",
    "annotation_fields": ("annotation_id", "asset", "basis", "date",
                          "schema_version", "view"),
    "note_fields": ("archive_key", "date", "metric_refs", "note_id",
                    "schema_version", "source_level"),
    "export_fields": ("as_of", "error_pattern_statistics", "note",
                      "quality_briefing", "schema_version", "suggestions",
                      "window_end", "window_kind", "window_start"),
    "live_guard_seq": ("AI内容", "🤖_AI投资项目", "每周宏观追踪", "investment-agent"),
    "raw_dir_guard": ("data", "daily"),
}


# ══ 基础件与守卫 ═════════════════════════════════════════════════════════

_MDAYS = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
_DIGITS = frozenset("0123456789")


def _parse_iso_date(s):
    """规范 YYYY-MM-DD 解析;非法→None(调用方决定 fail 或缺席)。

    规范形守卫(家族先例/R040 续段教训承接): 截断候选须为十位带杠形
    (第 5/8 位为 -)才入日历校验——紧凑形(20261108)与周形拒绝;
    零 datetime 导入(纯字符串+月长表+闰年规则判定,P-E-16 白名单面
    零例外,3.9/3.11 行为一致,P-E-03)。"""
    if not isinstance(s, str):
        return None
    t = s.strip()[:10]
    if len(t) != 10 or t[4] != "-" or t[7] != "-":
        return None
    y, m, d = t[:4], t[5:7], t[8:10]
    if not (set(y) <= _DIGITS and set(m) <= _DIGITS and set(d) <= _DIGITS):
        return None
    yi, mi, di = int(y), int(m), int(d)
    if yi < 1 or not 1 <= mi <= 12:
        return None
    mdays = _MDAYS[mi - 1]
    if mi == 2 and yi % 4 == 0 and (yi % 100 != 0 or yi % 400 == 0):
        mdays = 29
    if not 1 <= di <= mdays:
        return None
    return t


def _require_iso_date(s, name):
    got = _parse_iso_date(s)
    if got is None:
        raise ValueError(f"{name} 须为规范 YYYY-MM-DD: {s!r}")
    return got


def _norm_path(path):
    return os.path.normpath(os.path.abspath(os.path.expanduser(str(path))))


def _reject_raw_data_path(path, name):
    """快照纪律路径守卫(P-E-11/AC-07.1): 路径组件序列含 data+daily 相邻
    组件→ValueError fail-loud(组件以 os.path.join 形拼装比对,源码零连续
    字面量)。"""
    norm = _norm_path(path)
    parts = norm.split(os.sep)
    for i in range(len(parts) - 1):
        if parts[i] == _RAW_DIR_GUARD[0] and parts[i + 1] == _RAW_DIR_GUARD[1]:
            raise ValueError(
                f"{name} 指向原始采集档目录(快照纪律禁直读,DESIGN §3.1/"
                f"AC-07.1): {path!r}")
    return norm


def _reject_live_path(path, name):
    """LIVE 根守卫(P-E-10/要点③): 路径组件序列含 LIVE 根四组件序列
    (组件化 _LIVE_ROOT_GUARD,源码零连续 LIVE 路径字面量)→ValueError
    fail-loud;读写面均适用(用户数据零落 LIVE,绝对红线)。"""
    norm = _norm_path(path)
    parts = norm.split(os.sep)
    n = len(_LIVE_ROOT_GUARD)
    for i in range(len(parts) - n + 1):
        if all(parts[i + j] == _LIVE_ROOT_GUARD[j] for j in range(n)):
            raise ValueError(
                f"{name} 指向 LIVE 生产路径(用户数据零落 LIVE 红线,DESIGN "
                f"§6.2/§8.2;用户数据只落 DEV 仓或用户指定路径): {path!r}")
    return norm


def _write_root_guard(norm, user_root, name):
    """写入域守卫(P-E-10): 规范化路径须在 DEV 仓根(_DEV_ROOT)或显式
    user_root 指定目录之下;user_root 自身不得指向 LIVE(红线绝对性)。"""
    if user_root is not None:
        _reject_live_path(user_root, f"{name}#user_root")
    roots = [_DEV_ROOT]
    if user_root is not None:
        roots.append(_norm_path(user_root))
    for root in roots:
        if norm.startswith(root + os.sep):
            return norm
    raise ValueError(
        f"{name} 须落 DEV 仓({_DEV_ROOT})或显式 user_root 指定目录之下"
        f"(DESIGN §6.2 用户数据落 DEV 或用户指定路径): {norm!r}")


def _guard_read_path(path, name):
    """读取面守卫(P-E-10/P-E-11): 快照纪律+LIVE 根双拒(标注档/笔记档
    读取面)。"""
    return _reject_live_path(_reject_raw_data_path(path, name), name)


def _guard_write_path(path, user_root, name):
    """写入面守卫(P-E-10/P-E-11): 快照纪律+LIVE 根+写入域三重拒
    (标注档/笔记档/导出件三写入面)。"""
    norm = _reject_live_path(_reject_raw_data_path(path, name), name)
    return _write_root_guard(norm, user_root, name)


def _require_nonblank_str(v, name):
    if not isinstance(v, str) or not v.strip():
        raise ValueError(f"{name} 须为非空字符串: {v!r}")
    return v


# ══ 档键 ID 族(P-E-12: ANN-/NOTE-YYYYMMDD-NNN,同日单调配号) ═══════════

def _record_key(marker, iso_date, seq, name):
    iso = _require_iso_date(iso_date, f"{name}#date")
    if not isinstance(seq, int) or isinstance(seq, bool) \
            or not ID_SEQ_MIN <= seq <= ID_SEQ_MAX:
        raise ValueError(f"{name}#seq 须为 {ID_SEQ_MIN}-{ID_SEQ_MAX} 整数: {seq!r}")
    return f"{marker}{iso.replace('-', '')}-{seq:03d}"


def annotation_record_key(iso_date, seq):
    """标注档键: ANN-YYYYMMDD-NNN(纯函数)。"""
    return _record_key(ANNOTATION_MARKER, iso_date, seq, "annotation_id")


def note_record_key(iso_date, seq):
    """笔记档键: NOTE-YYYYMMDD-NNN(纯函数)。"""
    return _record_key(NOTE_MARKER, iso_date, seq, "note_id")


def _parse_record_id(rid, marker, iso, name):
    """显式传入档键校验: 合法形且日期段==记录日期;非法→ValueError。"""
    _require_nonblank_str(rid, name)
    ymd = iso.replace("-", "")
    prefix = marker + ymd + "-"
    if not rid.startswith(prefix) or len(rid) != len(prefix) + 3 \
            or not rid[len(prefix):].isdigit():
        raise ValueError(f"{name} 须为 {marker}{ymd}-NNN 形且日期段与记录"
                         f"date 一致: {rid!r}")
    return rid


def _next_seq(records, iso_date, id_field, marker, name):
    """同日单调配号(P-E-12): 档内同日已有最大序+1;>999→ValueError。"""
    iso = _require_iso_date(iso_date, f"{name}#date")
    prefix = marker + iso.replace("-", "") + "-"
    best = 0
    for r in records:
        rid = r.get(id_field) if isinstance(r, dict) else None
        if isinstance(rid, str) and rid.startswith(prefix) \
                and rid[len(prefix):].isdigit():
            best = max(best, int(rid[len(prefix):]))
    seq = best + 1
    if seq > ID_SEQ_MAX:
        raise ValueError(f"{name} 同日序号溢出(>{ID_SEQ_MAX},fail-loud): "
                         f"{iso}")
    return seq


# ══ 档读写基础件(P-E-04: JSONL append-only;坏行 fail-loud) ═════════════

def _load_records(path, kind, name):
    """档读取(只读): 不存在→[];逐行 json.loads;坏行/非 dict 行/重复
    档键→ValueError fail-loud(档案损坏如实暴露,不静默跳过)。"""
    norm = _guard_read_path(path, name)
    if not os.path.exists(norm):
        return []
    with open(norm, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    out, seen = [], set()
    for ln, line in enumerate(lines, 1):
        s = line.strip()
        if not s:
            continue
        try:
            obj = json.loads(s)
        except ValueError as e:
            raise ValueError(f"{name} 第 {ln} 行非规范 JSON(fail-loud,"
                             f"P-E-04): {e}") from e
        if not isinstance(obj, dict):
            raise ValueError(f"{name} 第 {ln} 行须为 dict 记录: {s[:80]!r}")
        rid = obj.get(kind)
        if rid is None:
            raise ValueError(f"{name} 第 {ln} 行缺档键 {kind}(fail-loud)")
        if rid in seen:
            raise ValueError(f"{name} 第 {ln} 行档键重复(append-only 纪律"
                             f"破坏,fail-loud): {rid!r}")
        seen.add(rid)
        out.append(obj)
    return out


def _append_line_json(record):
    """单行规范 JSON(确定性序列化,P-E-13;零改写既有行由 open 'a' 追加
    模式承载——恰标注档/笔记档两处调用面,P-E-16 记账)。"""
    return json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n"


# ══ 接口(a) 个人技术分析标注(P-E-03/P-E-04;§6.2 L158) ════════════════

def _validate_annotation_record(record, stored):
    """标注记录校验(P-E-03 字段封闭集): 6 键恰等;stored=True(档内读出)
    要求档键非 None。"""
    if not isinstance(record, dict):
        raise ValueError(f"标注记录须为 dict: {record!r}")
    if set(record) != set(_ANNOTATION_FIELDS):
        raise ValueError(f"标注记录字段集须恰为 {sorted(_ANNOTATION_FIELDS)}"
                         f"(封闭集,P-E-03): {sorted(record)}")
    if record["schema_version"] != ANNOTATION_SCHEMA_VERSION:
        raise ValueError(f"标注记录 schema_version 须为 "
                         f"{ANNOTATION_SCHEMA_VERSION}: "
                         f"{record['schema_version']!r}")
    iso = _require_iso_date(record["date"], "annotation#date")
    for k in ("asset", "view", "basis"):
        _require_nonblank_str(record[k], f"annotation#{k}")
    rid = record["annotation_id"]
    if rid is not None:
        _parse_record_id(rid, ANNOTATION_MARKER, iso, "annotation_id")
    elif stored:
        raise ValueError("档内标注记录 annotation_id 不得缺席(fail-loud)")
    return record


def build_annotation(date, asset, view, basis, annotation_id=None):
    """接口(a) 标注记录构造(纯函数,零写入;P-E-03)。

    用户主动填写四字段(日期/资产/观点/依据,DESIGN L158);annotation_id
    缺省由 append_annotation 同日单调配号(P-E-12)。"""
    iso = _require_iso_date(date, "annotation#date")
    rec = {
        "schema_version": ANNOTATION_SCHEMA_VERSION,
        "annotation_id": annotation_id,
        "date": iso,
        "asset": _require_nonblank_str(asset, "annotation#asset"),
        "view": _require_nonblank_str(view, "annotation#view"),
        "basis": _require_nonblank_str(basis, "annotation#basis"),
    }
    return _validate_annotation_record(rec, stored=False)


def append_annotation(archive_path, record, user_root=None):
    """标注入档(P-E-04: append-only 纯追加;重复档键拒;返回落档记录)。"""
    norm = _guard_write_path(archive_path, user_root, "annotation_archive")
    _validate_annotation_record(record, stored=False)
    existing = _load_records(norm, "annotation_id", "annotation_archive")
    for e in existing:
        _validate_annotation_record(e, stored=True)
    stored = dict(record)
    if stored["annotation_id"] is None:
        seq = _next_seq(existing, stored["date"], "annotation_id",
                        ANNOTATION_MARKER, "annotation_id")
        stored["annotation_id"] = annotation_record_key(stored["date"], seq)
    for e in existing:
        if e["annotation_id"] == stored["annotation_id"]:
            raise ValueError(f"标注档键已存在(append-only,重复拒;"
                             f"P-E-04): {stored['annotation_id']!r}")
    with open(norm, "a", encoding="utf-8") as f:   # open 'a' 面 1/2(P-E-16 记账)
        f.write(_append_line_json(stored))
    return stored


def read_annotations(archive_path):
    """标注档读取(只读;返回记录列表,档缺席→[])。"""
    out = _load_records(archive_path, "annotation_id", "annotation_archive")
    for e in out:
        _validate_annotation_record(e, stored=True)
    return out


# ══ 接口(b) 个人研究笔记引用(P-E-05/P-E-06;§6.2 L159) ════════════════

def _validate_note_record(record, stored):
    """笔记引用记录校验(P-E-05 字段封闭集+source_level 恒「个人观察」)。"""
    if not isinstance(record, dict):
        raise ValueError(f"笔记引用记录须为 dict: {record!r}")
    if set(record) != set(_NOTE_FIELDS):
        raise ValueError(f"笔记引用记录字段集须恰为 {sorted(_NOTE_FIELDS)}"
                         f"(封闭集,P-E-05): {sorted(record)}")
    if record["schema_version"] != NOTE_SCHEMA_VERSION:
        raise ValueError(f"笔记引用记录 schema_version 须为 "
                         f"{NOTE_SCHEMA_VERSION}: {record['schema_version']!r}")
    if record["source_level"] != NOTE_SOURCE_LEVEL:
        raise ValueError(f"source_level 须恒为「{NOTE_SOURCE_LEVEL}」(系统"
                         f"强制,用户不可传入;P-E-05/P-E-06 来源等级隔离): "
                         f"{record['source_level']!r}")
    iso = _require_iso_date(record["date"], "note#date")
    _require_nonblank_str(record["archive_key"], "note#archive_key")
    refs = record["metric_refs"]
    if not isinstance(refs, list) or not refs:
        raise ValueError(f"note#metric_refs 须为非空字符串列表(登记格式"
                         f"要求指标引用在场,DESIGN L159): {refs!r}")
    for m in refs:
        _require_nonblank_str(m, "note#metric_refs[]")
    rid = record["note_id"]
    if rid is not None:
        _parse_record_id(rid, NOTE_MARKER, iso, "note_id")
    elif stored:
        raise ValueError("档内笔记记录 note_id 不得缺席(fail-loud)")
    return record


def build_note_reference(date, archive_key, metric_refs, note_id=None):
    """接口(b) 笔记引用记录构造(纯函数,零写入;P-E-05)。

    登记格式=档键+指标引用+日期(DESIGN L159);source_level 由本函数
    系统强制写入「个人观察」(签名无此参数=用户不可传入,P-E-06 隔离
    承载);note_id 缺省由 append_note_reference 同日单调配号(P-E-12)。"""
    iso = _require_iso_date(date, "note#date")
    rec = {
        "schema_version": NOTE_SCHEMA_VERSION,
        "note_id": note_id,
        "date": iso,
        "archive_key": _require_nonblank_str(archive_key, "note#archive_key"),
        "metric_refs": list(metric_refs) if isinstance(metric_refs, list)
        else metric_refs,
        "source_level": NOTE_SOURCE_LEVEL,
    }
    return _validate_note_record(rec, stored=False)


def append_note_reference(archive_path, record, user_root=None):
    """笔记引用入档(P-E-04: append-only 纯追加;重复档键拒;返回落档记录)。"""
    norm = _guard_write_path(archive_path, user_root, "note_archive")
    _validate_note_record(record, stored=False)
    existing = _load_records(norm, "note_id", "note_archive")
    for e in existing:
        _validate_note_record(e, stored=True)
    stored = dict(record)
    if stored["note_id"] is None:
        seq = _next_seq(existing, stored["date"], "note_id",
                        NOTE_MARKER, "note_id")
        stored["note_id"] = note_record_key(stored["date"], seq)
    for e in existing:
        if e["note_id"] == stored["note_id"]:
            raise ValueError(f"笔记档键已存在(append-only,重复拒;"
                             f"P-E-04): {stored['note_id']!r}")
    with open(norm, "a", encoding="utf-8") as f:   # open 'a' 面 2/2(P-E-16 记账)
        f.write(_append_line_json(stored))
    return stored


def read_note_references(archive_path):
    """笔记档读取(只读;返回记录列表,档缺席→[])。"""
    out = _load_records(archive_path, "note_id", "note_archive")
    for e in out:
        _validate_note_record(e, stored=True)
    return out


def source_level_isolation_check():
    """来源等级隔离哨兵(要点②/P-E-06 三面对照;任一破坏→AssertionError)。

    ①词表隔离: 「个人观察」∉ v2 机制 7 类 ∪ 星级串集;②键集隔离: 笔记
    记录键集 ∩ v2 evidence 项字段名集=∅(零 mechanism/confidence/星级
    字段,不参与星级与门禁);③渲染面: 隔离标签词面承载完整性。"""
    assert NOTE_SOURCE_LEVEL not in EVIDENCE_GRADING_V2_MECHANISMS, (
        f"来源等级词面越界 v2 机制词表(隔离破坏): {NOTE_SOURCE_LEVEL!r}")
    assert NOTE_SOURCE_LEVEL not in STAR_LEVEL_STRINGS, (
        f"来源等级词面越界星级词表(隔离破坏): {NOTE_SOURCE_LEVEL!r}")
    assert not (set(_NOTE_FIELDS) & set(V2_EVIDENCE_ITEM_FIELDS)), (
        "笔记记录键集与 v2 evidence 项字段名集相交(隔离破坏): "
        f"{set(_NOTE_FIELDS) & set(V2_EVIDENCE_ITEM_FIELDS)}")
    assert NOTE_SOURCE_LEVEL in SOURCE_LEVEL_LABEL \
        and "证据分级外" in SOURCE_LEVEL_LABEL, (
            f"隔离标签词面不完整(须含来源等级与「证据分级外」): "
            f"{SOURCE_LEVEL_LABEL!r}")
    return True


# ══ 旁路渲染(标注/笔记视图;P-E-14 免责尾行) ═════════════════════════

def render_annotation_view(records):
    """标注视图旁路渲染(纯函数零写入;P-E-14 免责尾行)。"""
    if not isinstance(records, list):
        raise ValueError("render_annotation_view(records): records 须为列表")
    lines = [
        "个人技术分析标注视图(接口(a);旁路标注档 append-only;"
        f"{ZERO_ACTIVE_COLLECTION})",
        f"标注 {len(records)} 条:",
    ]
    for r in records:
        lines.append(f"- [{r['annotation_id']}] {r['date']} "
                     f"资产={r['asset']} 观点={r['view']} 依据={r['basis']}")
    lines.append(_ANNOTATION_TAIL)
    return "\n".join(lines)


def render_note_references(records):
    """笔记引用视图旁路渲染(纯函数零写入;每条强制来源等级隔离标签,
    全渲染面零 ★ 字符——要点②/P-E-06 渲染隔离)。"""
    if not isinstance(records, list):
        raise ValueError("render_note_references(records): records 须为列表")
    lines = [
        "个人研究笔记引用视图(接口(b);登记格式=档键+指标引用+日期;"
        f"{SOURCE_LEVEL_ISOLATION})",
        f"引用 {len(records)} 条:",
    ]
    for r in records:
        lines.append(f"- [{r['note_id']}] {r['date']} 档键={r['archive_key']} "
                     f"指标引用={','.join(r['metric_refs'])} {SOURCE_LEVEL_LABEL}")
    lines.append(_NOTE_TAIL)
    return "\n".join(lines)


# ══ 接口(c) 复盘结论导出(P-E-07/P-E-08;§6.2 L160 单向导出零回读) ═════

def validate_export_input(quality_review_output):
    """导出输入校验(P-E-15 复用调用锚): 须为 WP-D 编排面
    report_quality_review() 返回文档;返回四元组(原样引用,零复制零改写)。"""
    if not isinstance(quality_review_output, dict):
        raise ValueError("quality_review_output 须为 WP-D report_quality_review()"
                         " 返回文档(dict)")
    stats = quality_review_output.get("statistics")
    if not isinstance(stats, dict) \
            or stats.get("schema_version") != rqr.STATS_SCHEMA_VERSION:
        raise ValueError(f"statistics 须为 WP-D 质量文档"
                         f"(schema_version={rqr.STATS_SCHEMA_VERSION},"
                         f"rqr 常量复用锚 P-E-15)")
    briefing = quality_review_output.get("briefing")
    if not isinstance(briefing, str) or not briefing.strip():
        raise ValueError("briefing 须为非空字符串(WP-D 质量简报)")
    suggestions = quality_review_output.get("suggestions")
    if not isinstance(suggestions, list):
        raise ValueError("suggestions 须为列表(WP-D 校准建议清单)")
    pr = quality_review_output.get("prediction_review")
    if not isinstance(pr, dict) or not isinstance(pr.get("statistics"), dict):
        raise ValueError("prediction_review.statistics 须为 dict(WP-C 统计"
                         "文档,经 WP-D 编排面直通承载)")
    return stats, briefing, suggestions, pr["statistics"]


def build_export_document(quality_review_output):
    """接口(c) 导出文档装配(P-E-07 8 键;纯函数,内容面原样承载零重算)。"""
    stats, briefing, suggestions, pred_stats = \
        validate_export_input(quality_review_output)
    return {
        "schema_version": EXPORT_SCHEMA_VERSION,
        "note": EXPORT_NOTE,
        "as_of": stats.get("as_of"),
        "window_kind": stats.get("window_kind"),
        "window_start": stats.get("window_start"),
        "window_end": stats.get("window_end"),
        "quality_briefing": briefing,
        "error_pattern_statistics": pred_stats,
        "suggestions": suggestions,
    }


def dump_export_document(doc):
    """导出文档确定性序列化(P-E-13;纯函数返回字符串,零写盘)。"""
    if not isinstance(doc, dict) \
            or doc.get("schema_version") != EXPORT_SCHEMA_VERSION:
        raise ValueError(f"导出文档 schema 非法(须 schema_version="
                         f"{EXPORT_SCHEMA_VERSION})")
    return json.dumps(doc, sort_keys=True, ensure_ascii=False, indent=1)


def _export_stats_lines(doc):
    pred = doc["error_pattern_statistics"]
    counts = pred.get("counts") or {}
    hr = counts.get("hit_rate")
    hr_txt = _NA if hr is None else f"{hr:.4f}"
    ep = pred.get("error_patterns") or {}

    def _ids(axis):
        return ",".join(map(str, ep.get(axis) or []))

    return [
        f"窗内终态: hit={counts.get('hit')} miss={counts.get('miss')} "
        f"inconclusive={counts.get('inconclusive')}(单列) "
        f"not_yet_triggered终态="
        f"{counts.get('not_yet_triggered_terminal')}(单列); "
        f"命中率=hit/(hit+miss)={hr_txt}(DP-6 上游登记口径)",
        "错误模式: 方向错误=" + _ids("direction_error")
        + " | 期限错误=" + _ids("horizon_error")
        + " | 幅度错误=" + _ids("magnitude_error")
        + " | 无法归类(单列)=" + _ids("unclassifiable"),
    ]


def render_export_briefing(doc):
    """导出渲染(P-E-08;纯函数零写入,返回字符串)。

    单向导出·零回读: 本渲染只产出导出材料,不读取用户个人复盘流程任何
    数据;质量简报原文逐字嵌入(§6.1 产物 WP-P3-D 原样承载)。"""
    if not isinstance(doc, dict) \
            or doc.get("schema_version") != EXPORT_SCHEMA_VERSION:
        raise ValueError(f"render_export_briefing(doc): doc 须为导出文档"
                         f"(schema_version={EXPORT_SCHEMA_VERSION})")
    lines = [
        "个人复盘结论导出(接口(c);系统→用户单向导出·零回读;"
        f"{ZERO_LIVE_FALL})",
        f"窗口: {doc['window_start']} ~ {doc['window_end']}"
        f"({doc['window_kind']};as_of={doc['as_of']})",
        "── 质量简报(§6.1 产物,WP-P3-D 原样承载)──",
        doc["quality_briefing"],
        "── 错误模式统计(§5 产物,WP-P3-C 原样承载)──",
    ]
    lines.extend(_export_stats_lines(doc))
    n_sug = len(doc["suggestions"])
    if n_sug:
        lines.append(f"校准建议清单: {n_sug} 条(注入提示词须用户确认"
                     "[DP-8],requires_user_confirmation=true 标记随上游"
                     "原样携带,本导出零注入)")
    else:
        lines.append("校准建议清单: 空(如实呈现)")
    lines.append(_EXPORT_TAIL)
    return "\n".join(lines)


def write_export_document(export_path, content, user_root=None):
    """导出件写入(P-E-08/P-E-10: 显式路径+三重守卫;open 'w' 唯一写面;
    写入后零回读;返回规范化路径)。"""
    norm = _guard_write_path(export_path, user_root, "export_path")
    if not isinstance(content, str):
        raise ValueError("content 须为字符串(render_export_briefing/"
                         "dump_export_document 产出)")
    with open(norm, "w", encoding="utf-8") as f:
        f.write(content)
    return norm


# ══ DP/参数自检哨兵(要点②「先登记后运行、禁回改」运行期面) ═══════════

def registered_dp_values():
    """DP-9 登记定值(活性常量);测试/审计与 REPORT §零.4 登记值对照锚。"""
    return {"DP-9": "+".join(DP9_INTERFACE_SET) + "@" + DP9_USER_APPROVAL}


def registered_param_values():
    """行内登记型参数活性值(P-E-02..P-E-13);测试字面量三方一致对照锚。"""
    return {
        "interface_set": tuple(DP9_INTERFACE_SET),
        "annotation_schema_version": ANNOTATION_SCHEMA_VERSION,
        "note_schema_version": NOTE_SCHEMA_VERSION,
        "export_schema_version": EXPORT_SCHEMA_VERSION,
        "annotation_marker": ANNOTATION_MARKER,
        "note_marker": NOTE_MARKER,
        "note_source_level": NOTE_SOURCE_LEVEL,
        "annotation_fields": tuple(_ANNOTATION_FIELDS),
        "note_fields": tuple(_NOTE_FIELDS),
        "export_fields": tuple(_EXPORT_FIELDS),
        "live_guard_seq": tuple(_LIVE_ROOT_GUARD),
        "raw_dir_guard": tuple(_RAW_DIR_GUARD),
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
    assert tuple(DP9_INTERFACE_SET) == ("annotation", "note_reference",
                                        "export"), "三接口集须同批全启(DP-9)"
    assert len(DP9_INTERFACE_SET) == 3, "DP-9 实批形态=三接口同批"
    assert len(_LIVE_ROOT_GUARD) == 4, "LIVE 根守卫须四组件序列(P-E-10)"
    assert tuple(_RAW_DIR_GUARD) == ("data", "daily"), \
        "快照纪律守卫组件被回改(P-E-11)"
    assert source_level_isolation_check() is True, "来源等级隔离哨兵(P-E-06)"
    return True


# ══ 自检入口(零写入;不落默认路径) ═════════════════════════════════════

def _selfcheck():
    ok = dp_selfcheck()
    iso = source_level_isolation_check()
    print(f"personal_flow_integration selfcheck: dp_selfcheck={ok}; "
          f"isolation_check={iso}; interfaces={len(DP9_INTERFACE_SET)}; "
          f"annotation/note/export schema={ANNOTATION_SCHEMA_VERSION}/"
          f"{NOTE_SCHEMA_VERSION}/{EXPORT_SCHEMA_VERSION}; "
          f"v2_mechanisms={len(EVIDENCE_GRADING_V2_MECHANISMS)}")
    print(INTEGRATION_NOTE)
    return ok and iso


if __name__ == "__main__":
    _selfcheck()
