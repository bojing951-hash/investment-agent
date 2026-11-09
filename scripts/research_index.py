#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P3-WP-A: 档案检索与结论版本管理(P3 收尾层第 1 实现包,族首;#31/#32 挂靠)

DESIGN docs/P3_DESIGN.md §7 WP-P3-A 行(L170-L174,基线工作树实读)确定性落地:
- 检索面(§3.2,对象 4 类第一期+O-5 接口预留): ①快照事实(经 rp.select_snapshot
  版本选择+Gate A 放行核验)②正式报告(rp.scan_formal_weekly_reports 在场复用,
  8 条校验链)③论点/观点/预测状态记录(config/thesis.json+config/
  allocation_views.json,门禁后状态文件)④结论版本记录(本包 VER- 族随建随入
  索引);⑤深研任务档案(O-5)=接口预留(词表在场+收录集排除+skipped_reserved
  如实清单,不冒充收录,P0-3 落地后接入);
- 旁路索引器(§3.1+DP-1(a)): 索引=JSON 单文件衍生物,**可随时从权威源确定性
  重建**(逐字节一致);索引构建输入限门禁后正式产物——**结构性不可达原始采集档**
  (快照枚举=严格 glob research_snapshot_*.json 模式,china_/global_/macro_/
  rate_economy_ 等采集件零匹配零读取);索引损坏/漂移→重建,不反向修改任何
  权威档;查询结果引用一律落到源档档键(snapshot_id+digest/报告档键/状态记录
  键/VER- 键),不复制数值语义为第二事实源(§3.1 L73);
- 结构化查询 API(§3.2(a) L82): 离线纯函数,零网络零模型调用;输入=维度过滤器
  (metric_id/时间窗/资产/机制类别/结论状态/档键前缀),输出=档键引用列表
  (非数值本身);确定性排序;
- 版本记录写入挂接(§3.3,DP-3(a) 记录级): 结论版本链=append-only 旁路记录族
  VER-{YYYYMMDD}-{NNN}(DESIGN §3.3 L91 明文族)挂共享档案族根新集合
  conclusion_versions(经 WP-P2-A drr._write_records 写入原语,复用调用禁复制
  分叉);字段 9 项全落(版本键/对象类型/对象 ID/变更类型/changes=[{field,
  before,after}≥1 承载前值+后值+受影响字段清单/门禁依据/快照引用[snapshot_id
  +digest 经三重纪律重算绑定]/时间戳);**不改动既有回写签名,零状态文件写入**
  (旁路,§3.3 L92);
- 修正机制(§3.3 L93): 历史结论修正=修正提案→与现行状态变更完全相同的门禁
  依据(trigger 触发器核验 或 ≥2 项程序验证证据,沿 report_generator L503/L521
  现行门禁语义)→版本链追加;签名**无 bypass/force/skip 类参数**(不设任何弱
  门禁旁路);修正提案 applied=False——实际状态变更仍走既有回写路径门禁族。

范围排除(DESIGN L172): 自然语言查询(§3.2(b),复用模式B NL→IR 停泊面)与
关联扫描(§3.2(c),WP-P3-B 面)不在本包;WP-P3-B..F 任何范围禁提前带入。

纪律: 零网络(import 面白名单 json/os/sys/datetime+项目既有 drr/rp/fe);
零模型调用/凭证/付费;版本记录 append-only(重复/改写一律拒,族先例);快照绑定
三重纪律(drr._load_snapshot_for_verify 规范加载+rp.digest_snapshot 重算+
rp.gate_allows_formal_research 放行,Gate A=FAIL fail-closed);本模块输出为
研究检索面数据,**不构成投资建议**(DESIGN §8.3 红线: 禁交易/禁仓位/禁收益
承诺)。参数登记: docs/P3_WP_A_REPORT.md §零.4/§零.5(DP 处置+P-A-01..P-A-16,
先登记后实现,运行后禁回改)。
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deep_research_registrar as drr   # WP-P2-A 上游(复用调用,只读禁改)
import research_provenance as rp        # select_snapshot/digest_snapshot/gate_allows_formal_research/scan_formal_weekly_reports
import fact_engine as fe                # registry 经 fe.metric() 在场接口

# ══ 登记型参数定值(REPORT §零.4/§零.5;登记定值即实现值,运行后禁回改) ═════

DP1_INDEX_FORM = "bypass_file_incremental"     # DP-1 (a): 旁路索引文件+事件触发增量更新
DP2_OBJECT_SET = "O1_O2_O3_O4_full_four"       # DP-2 (a): 第一期对象集 O-1~O-4 全 4 类(O-5 预留)
DP3_RECORD_GRANULARITY = "record_level"        # DP-3 (a): 记录级(前值+后值+受影响字段清单)

# 模块内登记镜像(dp_selfcheck 哨兵对照源;与 REPORT §零.4 登记值一致)
_DP_REGISTERED = {
    "DP-1": "bypass_file_incremental",
    "DP-2": "O1_O2_O3_O4_full_four",
    "DP-3": "record_level",
}

# ══ 载体与词表(P-A-02/P-A-04/P-A-05/P-A-11) ═══════════════════════════

RESEARCH_INDEX_FILENAME = "research_index.json"      # P-A-02
SCHEMA_VERSION = 1

ARCHIVE_FAMILY = drr.ARCHIVE_FAMILY                  # "research_archive"(复用引用)
DEFAULT_ARCHIVE_DIR = drr.DEFAULT_ARCHIVE_DIR        # data/research/research_archive
COLLECTION_VERSIONS = "conclusion_versions"          # P-A-11(不占上游已占集合名)
VERSION_ID_PREFIX = "VER-"                           # §3.3 L91 明文族
DEFAULT_INDEX_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                 "data", "research")

REF_KINDS = ("conclusion_version", "formal_report", "prediction", "snapshot",
             "thesis", "view", "deep_research_task")   # 词表全集(含 O-5 预留类)
INDEXED_KINDS = ("conclusion_version", "formal_report", "prediction",
                 "snapshot", "thesis", "view")         # 第一期收录集(DP-2(a): 6 kind)
RESERVED_KINDS = ("deep_research_task",)               # O-5 接口预留(P-A-15)

OBJECT_TYPES = ("thesis", "view", "prediction", "deep_research_conclusion")
OBJECT_ID_PREFIX_BY_TYPE = {"thesis": "THESIS-", "view": "VIEW-",
                            "prediction": "PRED-"}
CHANGE_TYPES = ("status_change", "rating_change", "confidence_change",
                "revision_proposal")                    # §3.3 L91「变更类型」登记词表
GATE_BASIS_KINDS = ("trigger", "program_evidence")
MIN_PROGRAM_EVIDENCE = 2                               # ≥2 项程序验证证据(L503/L521 语义)

THESIS_KEY_PREFIX = "THESIS-"                          # P-A-05 登记型状态记录键
VIEW_KEY_PREFIX = "VIEW-"
PREDICTION_KEY_PREFIX = "PRED-"

_SNAPSHOT_GLOB = "research_snapshot_*.json"            # P-A-06 严格模式(结构性不可达采集件)
_SNAPSHOT_YMD_RE = re.compile(r"^research_snapshot_(\d{8})(?:_v\d+)?\.json$")
_YMD8_RE = re.compile(r"^\d{8}$")
_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_VERSION_ID_RE = re.compile(r"^VER-(\d{8})-(\d{3,})$")

DISCLAIMER_NOTE = ("旁路索引(衍生物,可从权威源确定性重建;查询结果为档键引用,"
                   "不复制数值语义为第二事实源);研究检索面输出,不构成投资建议"
                   "(禁交易/禁仓位/禁收益承诺)")

QUALITY_EXCLUDED_NOTE = "excluded(门禁不放行/候选损坏,如实不入索引,不填冒充值)"


# ══ 基础件 ═════════════════════════════════════════════════════════════

def _now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _ymd8_of(iso_ts):
    return iso_ts[:10].replace("-", "")


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


# ══ DP 自检哨兵(要点③「先登记后运行、禁回改」运行期面) ═════════════════

def registered_dp_values():
    """三 DP 登记定值(活性常量);测试/审计与 REPORT §零.4 登记值对照锚。"""
    return {"DP-1": DP1_INDEX_FORM, "DP-2": DP2_OBJECT_SET,
            "DP-3": DP3_RECORD_GRANULARITY}


def dp_selfcheck():
    """活性常量 vs 模块内登记镜像一致性哨兵;运行后回改任一定值→AssertionError。

    (测试侧另有字面量硬编码断言锚定 REPORT 登记值,三方一致=常量/镜像/登记;
    本哨兵提供运行期检出面,负向测试以 monkeypatch 模拟回改验证检出。)"""
    live = registered_dp_values()
    for k, v in _DP_REGISTERED.items():
        assert live.get(k) == v, (
            f"{k} 登记定值被回改: 活性={live.get(k)!r}≠登记={v!r}"
            f"(先登记后运行禁回改,REPORT §零.4)")
    assert tuple(sorted(INDEXED_KINDS)) == (
        "conclusion_version", "formal_report", "prediction",
        "snapshot", "thesis", "view"), "INDEXED_KINDS 收录集漂移(DP-2(a) 定值)"
    assert MIN_PROGRAM_EVIDENCE >= 2, "MIN_PROGRAM_EVIDENCE 低于门禁语义下限"
    return True


# ══ 条目构造与规范化(P-A-04) ══════════════════════════════════════════

def _norm_list(v):
    return None if v is None else sorted({str(x) for x in v})


def _mk_entry(kind, ref, *, date, status=None, metric_ids=None, assets=None,
              mechanisms=None, obs_min=None, obs_max=None, snapshot_id=None,
              digest=None):
    """索引条目(11 键固定;维度面无信息=null 如实缺席,不填 0/空串冒充)。"""
    if kind in RESERVED_KINDS:
        raise ValueError(f"{kind!r}=O-5 接口预留类,第一期不收录(P-A-15;"
                         f"skipped_reserved 如实清单面,禁冒充收录)")
    if kind not in INDEXED_KINDS:
        raise ValueError(f"kind 须为 INDEXED_KINDS 成员: {kind!r}")
    if not isinstance(ref, str) or not ref:
        raise ValueError(f"ref 须为非空 string: {ref!r}")
    if date is not None and not _iso_date_ok(date):
        raise ValueError(f"date 须为规范 YYYY-MM-DD 或 null: {date!r}")
    if obs_min is not None and not _iso_date_ok(obs_min):
        raise ValueError(f"obs_min 非规范: {obs_min!r}")
    if obs_max is not None and not _iso_date_ok(obs_max):
        raise ValueError(f"obs_max 非规范: {obs_max!r}")
    if obs_min and obs_max and obs_min > obs_max:
        raise ValueError(f"观测区间倒置: [{obs_min},{obs_max}]")
    return {"kind": kind, "ref": ref, "date": date, "status": status,
            "metric_ids": _norm_list(metric_ids),
            "assets": _norm_list(assets),
            "mechanisms": _norm_list(mechanisms),
            "obs_min": obs_min, "obs_max": obs_max,
            "snapshot_id": snapshot_id, "digest": digest}


_ENTRY_KEYS = {"kind", "ref", "date", "status", "metric_ids", "assets",
               "mechanisms", "obs_min", "obs_max", "snapshot_id", "digest"}


def _entry_sort_key(e):
    return (e["kind"], e["ref"])


# ══ 索引文件面(P-A-03: 确定性序列化,零时间戳/零过程元数据) ═══════════

def _dump_index_bytes(entries):
    """确定性序列化: canonical JSON(sort_keys+ensure_ascii=False+indent=1);
    同一输入条目集→逐字节一致(要点② 可重建性判据)。"""
    doc = {"schema_version": SCHEMA_VERSION, "note": DISCLAIMER_NOTE,
           "entries": sorted(entries, key=_entry_sort_key)}
    return json.dumps(doc, ensure_ascii=False, sort_keys=True, indent=1)


def _merge_entries(*entry_lists):
    """条目合并: 同 (kind,ref) 后写覆盖(状态对象=最新计算值),不可变对象重放幂等。"""
    by_key = {}
    for lst in entry_lists:
        for e in lst:
            if set(e.keys()) != _ENTRY_KEYS:
                raise ValueError(f"索引条目键集非法(须恰 11 键): {sorted(e.keys())}")
            by_key[_entry_sort_key(e)] = e
    return [by_key[k] for k in sorted(by_key)]


def write_index_file(index_path, entries):
    """索引文件原子落盘(规范化整体重写;索引=衍生物可重写,非 append-only 记录族)。"""
    blob = _dump_index_bytes(_merge_entries(entries))
    os.makedirs(os.path.dirname(os.path.abspath(str(index_path))), exist_ok=True)
    _tmp = str(index_path) + ".tmp"
    with open(_tmp, "w", encoding="utf-8") as f:
        f.write(blob)
    os.replace(_tmp, str(index_path))
    return index_path


def load_index_file(index_path):
    """读索引;结构损坏/条目非法/排序漂移 → ValueError fail-loud(衍生物损坏→重建)。"""
    with open(str(index_path), "r", encoding="utf-8") as f:
        doc = json.load(f)
    if not isinstance(doc, dict) or doc.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"索引文件 schema 非法(须 schema_version={SCHEMA_VERSION})")
    entries = doc.get("entries")
    if not isinstance(entries, list):
        raise ValueError("索引文件缺 entries 列表")
    for e in entries:
        if set(e.keys()) != _ENTRY_KEYS:
            raise ValueError(f"索引条目键集非法: {sorted(e.keys())}")
        if e["kind"] not in INDEXED_KINDS:
            raise ValueError(f"索引条目 kind 非收录集成员: {e['kind']!r}")
    if [ _entry_sort_key(e) for e in entries ] != sorted(_entry_sort_key(e) for e in entries):
        raise ValueError("索引条目排序漂移(损坏嫌疑;请从权威源重建)")
    if len({_entry_sort_key(e) for e in entries}) != len(entries):
        raise ValueError("索引条目 (kind,ref) 重复(损坏嫌疑;请从权威源重建)")
    return doc


def build_index_from_sources(*, snapshot_entries=None, report_entries=None,
                             state_entries=None, version_entries=None):
    """从权威源条目集构建索引文档(全量面;与 rebuild_index 同一合并/序列化路径)。"""
    return {"schema_version": SCHEMA_VERSION, "note": DISCLAIMER_NOTE,
            "entries": _merge_entries(snapshot_entries or [], report_entries or [],
                                      state_entries or [], version_entries or [])}


def rebuild_index(index_path, *, snapshot_entries=None, report_entries=None,
                  state_entries=None, version_entries=None):
    """全量重建并覆盖写(删索引→重建→逐字节一致,要点②)。"""
    doc = build_index_from_sources(snapshot_entries=snapshot_entries,
                                   report_entries=report_entries,
                                   state_entries=state_entries,
                                   version_entries=version_entries)
    blob = _dump_index_bytes(doc["entries"])
    os.makedirs(os.path.dirname(os.path.abspath(str(index_path))), exist_ok=True)
    _tmp = str(index_path) + ".tmp"
    with open(_tmp, "w", encoding="utf-8") as f:
        f.write(blob)
    os.replace(_tmp, str(index_path))
    return doc


def update_index_entries(index_path, new_entries):
    """事件触发增量更新(DP-1(a)): 读现有索引→合并(同键替换/新键插入)→规范化重写。"""
    doc = load_index_file(index_path)
    merged = _merge_entries(doc["entries"], new_entries)
    return rebuild_index(index_path, snapshot_entries=merged)


# ══ 索引源①: 快照(P-A-06;严格 glob,结构性不可达原始采集档) ═══════════

def _snapshot_ymds(daily_dir):
    """当日候选发现: 严格 research_snapshot_*.json 模式→8 位 ymd 集。

    china_/global_/macro_/rate_economy_/japan_/jp_/ea_ 等原始采集件与该模式
    零匹配(结构性不可达,§3.1;本函数不打开任何非快照文件)。"""
    out = set()
    for name in sorted(os.listdir(str(daily_dir))):
        m = _SNAPSHOT_YMD_RE.match(name)
        if m:
            out.add(m.group(1))
    return out


def _assets_of_metric_ids(metric_ids):
    """资产维度: 经 fe.metric() registry 在场接口(缺席如实不入,零 registry 直读)。"""
    out = set()
    for mid in metric_ids:
        try:
            m = fe.metric(mid)
        except Exception:
            m = None
        if isinstance(m, dict) and m.get("asset_class"):
            out.add(str(m["asset_class"]))
    return sorted(out)


def index_snapshots(daily_dir):
    """快照索引: 枚举 ymd→rp.select_snapshot 权威版本选择→Gate A 放行核验。

    返回 (entries, excluded);excluded={ymd, reason} 如实清单(FAIL fail-closed/
    无候选/候选损坏不入索引,不填冒充值)。"""
    entries, excluded = [], []
    for ymd in sorted(_snapshot_ymds(daily_dir)):
        snap, _path = rp.select_snapshot(ymd, daily_dir)
        if snap is None:
            excluded.append({"ymd": ymd,
                             "reason": f"select_snapshot 拒绝: {_path}"})
            continue
        gate_status = (snap.get("gate_a") or {}).get("status")
        if not rp.gate_allows_formal_research(gate_status):
            excluded.append({"ymd": ymd,
                             "reason": f"Gate A={gate_status!r} 不放行"
                                       f"(PASS/DEGRADED 之外,FAIL fail-closed)"})
            continue
        entries.append(_snapshot_entry(snap))
    return entries, excluded


def _snapshot_entry(snap):
    sid = str(snap.get("snapshot_id") or "")
    m = re.match(r"^research_snapshot_(\d{8})", sid)
    if not m:
        raise ValueError(f"snapshot_id 非规范: {sid!r}")
    facts = snap.get("facts") or []
    metric_ids = sorted({str(f["metric_id"]) for f in facts
                         if isinstance(f, dict) and f.get("metric_id")})
    obs = sorted({str(f["observation_date"]) for f in facts
                  if isinstance(f, dict) and _iso_date_ok(f.get("observation_date"))})
    return _mk_entry(
        "snapshot", sid, date=_ymd8_to_iso(m.group(1)), status=None,
        metric_ids=metric_ids, assets=_assets_of_metric_ids(metric_ids),
        mechanisms=None, obs_min=obs[0] if obs else None,
        obs_max=obs[-1] if obs else None,
        snapshot_id=sid, digest=rp.digest_snapshot(snap))


# ══ 索引源②: 正式报告(P-A-07;rp 在场 8 条校验链复用) ═════════════════

def index_formal_reports(output_dir):
    """正式周报索引: rp.scan_formal_weekly_reports(发布状态+身份+digest 校验链)。"""
    entries = []
    for view in rp.scan_formal_weekly_reports(str(output_dir)):
        ymd8 = str(view["ymd"])
        entries.append(_mk_entry(
            "formal_report", f"weekly_report_{ymd8}", date=_ymd8_to_iso(ymd8),
            status=None, metric_ids=None, assets=None, mechanisms=None,
            obs_min=None, obs_max=None, snapshot_id=None, digest=None))
    return entries


# ══ 索引源③: 门禁后状态文件(P-A-08) ═════════════════════════════════

def index_state_files(thesis_path, views_path):
    """论点/观点/预测状态记录索引(门禁后状态文件,§3.1 认可构建输入)。

    mechanisms=null 如实缺席: DEV 在场状态文件无结构化机制标签(登记发现,
    REPORT §零.5 P-A-08);维度与过滤器已实现,数据面如实不造值。"""
    with open(str(thesis_path), "r", encoding="utf-8") as f:
        th = json.load(f)
    with open(str(views_path), "r", encoding="utf-8") as f:
        av = json.load(f)
    entries = []
    last_up = th.get("last_updated") if _iso_date_ok(th.get("last_updated")) else None
    for t in th.get("theses") or []:
        mids = sorted({str(q.get("metric")) for q in t.get("quant_triggers") or []
                       if q.get("metric")})
        entries.append(_mk_entry(
            "thesis", f"{THESIS_KEY_PREFIX}{t['id']}", date=last_up,
            status=t.get("status"), metric_ids=mids, assets=None,
            mechanisms=None, obs_min=None, obs_max=None,
            snapshot_id=None, digest=None))
    av_up = av.get("last_updated") if _iso_date_ok(av.get("last_updated")) else None
    for v in av.get("views") or []:
        mids = sorted({str(q.get("metric")) for q in v.get("quant_triggers") or []
                       if q.get("metric")})
        assets = [str(v["asset"])] if v.get("asset") else []
        entries.append(_mk_entry(
            "view", f"{VIEW_KEY_PREFIX}{v['id']}", date=av_up,
            status=v.get("rating"), metric_ids=mids, assets=assets,
            mechanisms=None, obs_min=None, obs_max=None,
            snapshot_id=None, digest=None))
    for p in av.get("predictions") or []:
        mids = [str(p["metric"])] if p.get("metric") else None
        assets = [str(p["asset"])] if p.get("asset") else []
        entries.append(_mk_entry(
            "prediction", f"{PREDICTION_KEY_PREFIX}{p['pred_id']}",
            date=p.get("date_made") if _iso_date_ok(p.get("date_made")) else None,
            status=p.get("status"), metric_ids=mids, assets=assets,
            mechanisms=None, obs_min=None, obs_max=None,
            snapshot_id=None, digest=None))
    return entries


# ══ 索引源④: 结论版本记录(P-A-09;随建随入,§3.2 检索对象④) ═══════════

def index_conclusion_versions(archive_dir=None):
    """版本记录索引: 读 conclusion_versions 集合全部档(档内逐条重校验 fail-loud)。"""
    return [_version_entry(r) for r in list_conclusion_versions(archive_dir)]


def _version_entry(record):
    return _mk_entry(
        "conclusion_version", record["version_id"],
        date=_ymd8_to_iso(_VERSION_ID_RE.match(record["version_id"]).group(1)),
        status=record["change_type"], metric_ids=None, assets=None,
        mechanisms=None, obs_min=None, obs_max=None,
        snapshot_id=record["snapshot_id"], digest=record["digest_snapshot"])


# ══ O-5 接口预留(P-A-15;skipped_reserved 如实清单,不冒充收录) ════════

def index_reserved_kind(ref):
    """O-5(深研任务档案)接口预留: 返回 skipped_reserved 登记项(非索引条目)。

    第一期收录集(INDEXED_KINDS)不含 deep_research_task;P0-3 共享档案落地后
    接入(DESIGN §2.1 L53/§3.2 L77⑤);本函数不产生索引条目、不冒充已收录。"""
    return {"kind": "deep_research_task", "ref": str(ref),
            "skipped": "reserved_interface_pending_p0_3(O-5 接口预留,第一期不收录)"}


# ══ 版本记录族(P-A-11/P-A-12/P-A-13/P-A-14;append-only 旁路) ═════════

def _versions_dir(archive_dir):
    return drr._collection_dir(archive_dir or DEFAULT_ARCHIVE_DIR,
                               COLLECTION_VERSIONS)


def _same_day_max_seq(archive_dir, ymd8):
    """同日单调配号基数: 扫集合目录当日 VER-{ymd}-{NNN} 最大序号(ra 纪律同款)。"""
    best = 0
    d = _versions_dir(archive_dir)
    if not os.path.isdir(d):
        return 0
    for name in os.listdir(d):
        m = _VERSION_ID_RE.match(name[:-5] if name.endswith(".json") else name)
        if m and m.group(1) == str(ymd8):
            best = max(best, int(m.group(2)))
    return best


def _next_version_id(archive_dir, created_at):
    ymd8 = _ymd8_of(created_at)
    if not _YMD8_RE.match(ymd8):
        raise ValueError(f"created_at 须为 ISO8601 字符串: {created_at!r}")
    seq = _same_day_max_seq(archive_dir, ymd8) + 1
    return f"{VERSION_ID_PREFIX}{ymd8}-{seq:03d}"


def _validate_gate_basis(gate_basis):
    """门禁依据强制(P-A-13): trigger 核验已触发 或 ≥2 项程序验证证据;
    不合法→ValueError 零写入;签名无 bypass/force/skip 参数(无弱门禁旁路)。"""
    if not isinstance(gate_basis, dict) or "kind" not in gate_basis:
        raise ValueError(f"gate_basis 须为携 kind 的 dict: {gate_basis!r}"
                         f"(现行门禁语义: 触发器核验已触发 或 ≥2 项程序验证证据)")
    kind = gate_basis.get("kind")
    if kind == "trigger":
        tid = gate_basis.get("trigger_id")
        if not isinstance(tid, str) or not tid.strip():
            raise ValueError("gate_basis.kind=trigger 须携非空 trigger_id")
        return {"kind": "trigger", "trigger_id": tid}
    if kind == "program_evidence":
        refs = gate_basis.get("evidence_refs")
        if not isinstance(refs, list) or len(refs) < MIN_PROGRAM_EVIDENCE:
            raise ValueError(f"gate_basis.kind=program_evidence 须携 ≥{MIN_PROGRAM_EVIDENCE}"
                             f" 项 evidence_refs(程序验证证据不足,门禁不放行)")
        bad = [r for r in refs if not isinstance(r, str) or not r.strip()]
        if bad:
            raise ValueError(f"evidence_refs 含非字符串引用: {bad!r}")
        return {"kind": "program_evidence", "evidence_refs": list(refs)}
    raise ValueError(f"gate_basis.kind 须为 {GATE_BASIS_KINDS}: {kind!r}")


def _validate_changes(changes):
    """DP-3(a) 记录级: [{field,before,after}…≥1];before==after(无变更)拒。"""
    if not isinstance(changes, list) or not changes:
        raise ValueError(f"changes 须为非空列表(记录级粒度,DP-3(a)): {changes!r}")
    for c in changes:
        if not isinstance(c, dict) or set(c.keys()) != {"field", "before", "after"}:
            raise ValueError(f"changes 项须恰含 field/before/after: {c!r}")
        if not isinstance(c["field"], str) or not c["field"]:
            raise ValueError(f"changes[].field 须为非空 string: {c!r}")
        if c["before"] == c["after"]:
            raise ValueError(f"changes 项无实际变更(before==after): {c!r}")
    return [dict(c) for c in changes]


def validate_conclusion_version_record(record):
    """版本记录全量校验(读侧 fail-loud;篡改档→ValueError)。"""
    if not isinstance(record, dict):
        raise ValueError("版本记录须为 dict")
    required = {"record_type", "version_id", "object_type", "object_id",
                "change_type", "changes", "gate_basis", "snapshot_id",
                "digest_snapshot", "created_at", "history"}
    missing = required - set(record.keys())
    if missing:
        raise ValueError(f"版本记录缺字段: {sorted(missing)}")
    if record["record_type"] != "conclusion_version":
        raise ValueError(f"record_type 非法: {record['record_type']!r}")
    m = _VERSION_ID_RE.match(str(record["version_id"]))
    if not m:
        raise ValueError(f"version_id 须为 VER-{{YYYYMMDD}}-{{NNN}}: "
                         f"{record['version_id']!r}")
    if m.group(1) != _ymd8_of(str(record["created_at"])):
        raise ValueError(f"version_id 日期段与 created_at 不符: "
                         f"{record['version_id']!r} vs {record['created_at']!r}")
    if record["object_type"] not in OBJECT_TYPES:
        raise ValueError(f"object_type 须为 {OBJECT_TYPES}: {record['object_type']!r}")
    oid = record["object_id"]
    if not isinstance(oid, str) or not oid:
        raise ValueError(f"object_id 须为非空 string: {oid!r}")
    pref = OBJECT_ID_PREFIX_BY_TYPE.get(record["object_type"])
    if pref and not oid.startswith(pref):
        raise ValueError(f"object_id 须为 {pref}* 族: {oid!r}")
    if record["change_type"] not in CHANGE_TYPES:
        raise ValueError(f"change_type 须为 {CHANGE_TYPES}: {record['change_type']!r}")
    _validate_changes(record["changes"])
    _validate_gate_basis(record["gate_basis"])
    if drr.ra.parse_snapshot_id(str(record["snapshot_id"])) is None:
        raise ValueError(f"snapshot_id 非规范: {record['snapshot_id']!r}")
    if not (isinstance(record["digest_snapshot"], str)
            and len(record["digest_snapshot"]) == 16):
        raise ValueError(f"digest_snapshot 须为 16 位指纹: "
                         f"{record['digest_snapshot']!r}")
    if not isinstance(record["history"], list) or not record["history"]:
        raise ValueError("history 须为非空列表(append-only 记录族惯例)")
    return True


def record_conclusion_version(object_type, object_id, change_type, changes,
                              gate_basis, snapshot, *, snapshot_dir,
                              archive_dir=None, created_at=None, note=None):
    """结论版本记录写入挂接(§3.3 旁路,append-only;零状态文件写入)。

    流程: 参数校验(含门禁依据强制)→快照三重纪律(drr._load_snapshot_for_verify
    规范加载+rp.digest_snapshot 重算+rp.gate_allows_formal_research 放行,
    Gate A=FAIL fail-closed)→同日单调配号→drr._write_records 原子落档
    (同 version_id 重放→rejected-duplicate,零写入)。
    snapshot=携 snapshot_id 的 dict(digest 由模块重算,API 无 digest 入参)。
    返回 {status, version_id, record_path, digest_snapshot, applied, note};
    applied 恒 False(实际状态变更仍走既有回写路径门禁族,旁路不改回写签名)。"""
    if object_type not in OBJECT_TYPES:
        raise ValueError(f"object_type 须为 {OBJECT_TYPES}: {object_type!r}")
    if change_type not in CHANGE_TYPES:
        raise ValueError(f"change_type 须为 {CHANGE_TYPES}: {change_type!r}")
    changes = _validate_changes(changes)
    gate_basis = _validate_gate_basis(gate_basis)
    if not isinstance(snapshot, dict) or not snapshot.get("snapshot_id"):
        raise ValueError("snapshot 须为携带 snapshot_id 的 dict(注入绑定面)")
    sid = str(snapshot["snapshot_id"])
    if drr.ra.parse_snapshot_id(sid) is None:
        raise ValueError(f"snapshot.snapshot_id 非规范: {sid!r}")
    created_at = created_at or _now_iso()
    version_id = _next_version_id(archive_dir, created_at)
    record = {"record_type": "conclusion_version",
              "version_id": version_id,
              "object_type": object_type,
              "object_id": object_id,
              "change_type": change_type,
              "changes": changes,
              "gate_basis": gate_basis,
              "snapshot_id": sid,
              "digest_snapshot": None,          # 占位,三重纪律后回填
              "created_at": created_at,
              "history": [{"ts": created_at, "note": note or "结论版本记录(旁路 append-only)"}]}
    # 快照三重纪律(P-A-14)
    snap, load_err = drr._load_snapshot_for_verify(sid, snapshot_dir)
    if snap is None:
        raise ValueError(f"快照接地失败: {load_err}")
    gate_status = (snap.get("gate_a") or {}).get("status")
    if not rp.gate_allows_formal_research(gate_status):
        raise ValueError(f"Gate A={gate_status!r} 不放行正式研究(FAIL fail-closed,"
                         f"§3.1 红线),本快照不得作为版本记录证据源: {sid}")
    record["digest_snapshot"] = rp.digest_snapshot(snap)
    validate_conclusion_version_record(record)
    planned = [(record, drr._record_path(archive_dir or DEFAULT_ARCHIVE_DIR,
                                         COLLECTION_VERSIONS, version_id))]
    status, last_path = drr._write_records(planned,
                                           archive_dir or DEFAULT_ARCHIVE_DIR)
    return {"status": status, "version_id": version_id,
            "record_path": last_path,
            "digest_snapshot": record["digest_snapshot"],
            "applied": False,
            "note": "版本链追加(applied=False;实际状态变更须走既有回写路径"
                    "门禁族,本模块旁路零状态文件写入,不构成投资建议)"}


def revise_conclusion(object_type, object_id, changes, gate_basis, snapshot, *,
                      snapshot_dir, archive_dir=None, created_at=None,
                      note=None):
    """历史结论修正提案(§3.3 L93): 与现行状态变更**完全相同的门禁依据**
    (trigger 核验已触发 或 ≥2 项程序验证证据,无弱门禁旁路)→版本链追加
    revision_proposal 记录;不直接改任何状态(提案≠回写)。"""
    return record_conclusion_version(
        object_type, object_id, "revision_proposal", changes, gate_basis,
        snapshot, snapshot_dir=snapshot_dir, archive_dir=archive_dir,
        created_at=created_at,
        note=note or "修正提案入版本链(提案;状态变更走既有门禁)")


def list_conclusion_versions(archive_dir=None):
    """读集合全部版本记录(档内逐条重校验 fail-loud;按 version_id 排序)。"""
    d = _versions_dir(archive_dir)
    out = []
    if not os.path.isdir(d):
        return out
    for name in sorted(os.listdir(d)):
        if not name.endswith(".json"):
            continue
        with open(os.path.join(d, name), "r", encoding="utf-8") as f:
            record = json.load(f)
        validate_conclusion_version_record(record)   # 篡改档→ValueError fail-loud
        out.append(record)
    return out


# ══ 结构化查询 API(P-A-10;离线纯函数,档键引用输出) ══════════════════

def _check_window_args(obs_start, obs_end):
    for name, v in (("obs_start", obs_start), ("obs_end", obs_end)):
        if v is not None and not _iso_date_ok(v):
            raise ValueError(f"{name} 须为规范 YYYY-MM-DD 或 null: {v!r}")
    if obs_start and obs_end and obs_start > obs_end:
        raise ValueError(f"查询窗倒置: [{obs_start},{obs_end}]")


def _date_in_window(d, obs_start, obs_end):
    if obs_start is not None and d < obs_start:
        return False
    if obs_end is not None and d > obs_end:
        return False
    return True


def _range_overlaps_window(lo, hi, obs_start, obs_end):
    wlo = obs_start or "0000-01-01"
    whi = obs_end or "9999-12-31"
    return lo <= whi and hi >= wlo


def query_index(index, *, metric_ids=None, obs_start=None, obs_end=None,
                assets=None, mechanisms=None, statuses=None, key_prefixes=None):
    """结构化查询(§3.2(a)): 维度过滤器→档键引用列表(非数值本身)。

    命中语义(P-A-10): metric_ids/assets/mechanisms=集合交集非空;statuses=
    条目 status 精确等值(任一);key_prefixes=ref 前缀任一;时间窗=条目 date
    落窗 **或** 条目 [obs_min,obs_max] 与窗相交;多过滤器 AND;输出按
    (kind,ref) 排序={kind,ref,snapshot_id,digest}(档键引用)。零网络零模型调用。"""
    if not isinstance(index, dict) or not isinstance(index.get("entries"), list):
        raise ValueError("index 须为携 entries 列表的 dict(load_index_file 产出)")
    _check_window_args(obs_start, obs_end)
    want_metrics = _norm_list(metric_ids)
    want_assets = _norm_list(assets)
    want_mechs = _norm_list(mechanisms)
    if statuses is not None and not isinstance(statuses, (list, tuple)):
        raise ValueError(f"statuses 须为列表或 None: {statuses!r}")
    if key_prefixes is not None:
        if not isinstance(key_prefixes, (list, tuple)) or not all(
                isinstance(p, str) and p for p in key_prefixes):
            raise ValueError(f"key_prefixes 须为非空字符串列表: {key_prefixes!r}")
    window_on = obs_start is not None or obs_end is not None
    out = []
    for e in index["entries"]:
        if want_metrics is not None and not (
                set(want_metrics) & set(e["metric_ids"] or [])):
            continue
        if want_assets is not None and not (
                set(want_assets) & set(e["assets"] or [])):
            continue
        if want_mechs is not None and not (
                set(want_mechs) & set(e["mechanisms"] or [])):
            continue
        if statuses is not None and e["status"] not in statuses:
            continue
        if key_prefixes is not None and not any(
                e["ref"].startswith(p) for p in key_prefixes):
            continue
        if window_on:
            hit = False
            if e["date"] and _date_in_window(e["date"], obs_start, obs_end):
                hit = True
            elif (e["obs_min"] and e["obs_max"]
                  and _range_overlaps_window(e["obs_min"], e["obs_max"],
                                             obs_start, obs_end)):
                hit = True
            if not hit:
                continue
        out.append({"kind": e["kind"], "ref": e["ref"],
                    "snapshot_id": e["snapshot_id"], "digest": e["digest"]})
    out.sort(key=lambda o: (o["kind"], o["ref"]))   # P-A-10 确定性排序
    return out


# ══ 自检入口(零写入;不落默认路径) ═════════════════════════════════════

def _selfcheck():
    ok = dp_selfcheck()
    print(f"research_index selfcheck: dp_selfcheck={ok}; "
          f"INDEXED_KINDS={len(INDEXED_KINDS)}; RESERVED(O-5)={len(RESERVED_KINDS)}; "
          f"MIN_PROGRAM_EVIDENCE={MIN_PROGRAM_EVIDENCE}")
    print(DISCLAIMER_NOTE)
    return ok


if __name__ == "__main__":
    _selfcheck()
