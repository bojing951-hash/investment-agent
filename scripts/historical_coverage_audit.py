#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""历史覆盖只读审计器(IA-P0-2-W4) — 81项注册指标在已存档数据中的真实历史覆盖

性质(W4-DEV-v1.0 §一): 调查已有数据事实,不采集/不回补/不修改任何输入。
- 只读 --data-dir(授权数据集),只写 --out-dir(必须在数据根之外);
- 无网络/无GLM/不触发采集器/不改研究状态/不写Gate产物;
- 身份映射复用项目既有逻辑(fact_engine._GLOBAL_ID_MAP/_MACRO_ALIAS;
  china代码映射与snapshot_builder._CN_CODE/_HK_CODE及fe.normalize_china同源,
  tests/test_p02_w4.py守护防漂移);
- 日期纪律(§7.1): 只用 series.dates 与真实 observation_date/date 字段;
  严禁以采集文件日期/as_of/retrieved_at/generated_at 补造观测日;
- 数值纪律(§7.2): None/NaN/inf/非法串/日期值长度不一致如实记录,不静默跳过;
- 去重纪律(§7.3): 同一 observation_date 跨文件重复采集只计一次观测日;
  快照(series_store/单点事实)与同源每日文件不重复计数(非权威通道)。

audit_status: COMPLETED(≥1可读文件且输入未变) / NO_INPUT / ALL_UNREADABLE /
INPUT_CHANGED / INVALID_PATH。退出码: 0=COMPLETED; 2=不可宣布完成; 3=输入变化。
"""
import argparse
import glob
import hashlib
import json
import math
import os
import re
import sys
from collections import OrderedDict, deque
from datetime import date, datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import fact_engine as fe          # _GLOBAL_ID_MAP/_MACRO_ALIAS/parse_iso_date/_iso(既有身份与严格日期原语)
import trading_calendar as tc     # 全系统唯一日历权威

TOOL_NAME = 'historical_coverage_audit'
SCHEMA_VERSION = 'w4-coverage-audit/1.0'

# ── 通道文件模式(金融指标机器输入;同前缀.md人读镜像与anchors/scorecard/
#    anchor_prompt/correlation/news等非本审计对象,计数见报告excluded节) ──
CHANNEL_PATTERNS = OrderedDict([
    ('global', 'global_*.json'),
    ('china', 'china_*.json'),
    ('macro', 'macro_*.json'),
    ('rate_economy', 'rate_economy_*.json'),
    ('research_snapshot', 'research_snapshot_*.json'),
])
CHANNEL_COLLECTOR = {'global': 'global_market_collector', 'china': 'china_market_collector',
                     'macro': 'macro_collector', 'rate_economy': 'rate_expectations',
                     'research_snapshot': 'snapshot_builder(Layer3)'}
# 注册表source(权威通道声明) ↔ 采集文件通道
REGISTRY_SOURCE_CHANNEL = {'global_market_collector': 'global', 'macro_collector': 'macro',
                           'china_market_collector': 'china', 'rate_expectations': 'rate_economy'}

# ── 身份映射(与既有实现同源;test_p02_w4以ast解析fe/snapshot_builder源码守护不漂移) ──
GLOBAL_ID_MAP = fe._GLOBAL_ID_MAP        # {"GOLD":"GOLD_F",...,"WTI":"WTI_F"(期货通道)}(模块级)
# fe._MACRO_ALIAS/_CODE_MAP/_HK_MAP为函数内局部变量,此处按同值复刻+测试守护:
MACRO_ALIAS = {'WTI': 'WTI_SPOT_M'}      # 宏观通道WTI=现货月均,与global期货WTI_F分开
CHINA_A_CODE = {"000001.SH": "SHCOMP", "399001.SZ": "SZCI", "399006.SZ": "CHINEXT"}
CHINA_HK_CODE = {"^HSI": "HSI", "^HSCE": "HSCEI", "^HSCEI": "HSCEI"}
CHINA_LEGACY_LABEL = {"上证指数": "SHCOMP", "深证成指": "SZCI", "创业板指": "CHINEXT",
                      "恒生指数": "HSI", "恒生国企指数": "HSCEI", "恒生国企": "HSCEI"}
RATE_REAL_ECONOMY_MAP = {'UNRATE': 'UNEMPLOYMENT', 'PAYEMS': 'NFP', 'UMCSENT': 'UMCSENT',
                         'RSAFS': 'RSAFS', 'INDPRO': 'INDPRO', 'JTSJOL': 'JTSJOL'}

# ── 频率/连续段/稀疏阈值(W4工程描述阈值——自行定义并公开,非金融事实) ──
THRESHOLDS = {
    'segment_break_natural_days': {'daily': 10, 'weekly': 21, 'monthly': 92},
    'sparse_coverage_ratio_below': 0.5,
    'complete_history_min_unique_obs': 60,
    'complete_history_min_ratio': 0.9,
    'recent_only_span_days_max': 30,
    'serious_break_days': {'daily': 10, 'weekly': 21, 'monthly': 92},
}
CALENDAR_LIMITATIONS = {
    'cn': '中国日历仅2026年含精确节假日块,其余年份仅周末近似——日频缺口为近似判断',
    'hk': '港股日历最小集(周末+01-01+12-25),节假日覆盖不完整——缺口为近似判断',
    'fx': '外汇按周一~周五近似(24/5,节假日未建模)',
    'us_rates': 'FRED日频序列按NYSE日历近似(非交易日无新观测,该近似与发布实际一致)',
    'commodity': 'CME商品期货按NYSE近似(半日/全日差异<1自然日)',
    'us_equity': 'NYSE规则日历(周末+固定节+浮动节)',
    'crypto': '7×24,无交易日历限制',
}
BASIS_NOTE = ('上述阈值与分类为W4审计器的工程描述约定(公开定义、可从观测清单与输入文件复算),'
              '不是金融事实;未获授权的阈值不得作为研究充分性结论。')

# ════════════════ 纯函数(负向敏感性测试的注入缝) ════════════════

def to_obs_date(raw):
    """观测日解析: 接受'YYYY-MM-DD'完整ISO与'YYYYMMDD'紧凑(fe._iso同语义);
    其余(非法日历日/带垃圾后缀/None)返回(None,原因)。严禁文件日期/as_of补造。"""
    if raw is None:
        return None, 'obs_date_missing'
    s = fe._iso(str(raw))
    d = fe.parse_iso_date(s)
    if d is None:
        return None, 'obs_date_invalid:%r' % (str(raw)[:32],)
    return d.isoformat(), None


def to_value(raw):
    """数值解析: int/float且有限为有效;None/NaN/inf/bool/非法串→(None,原因)。"""
    if raw is None:
        return None, 'value_missing'
    if isinstance(raw, bool) or not isinstance(raw, (int, float)):
        return None, 'value_not_numeric:%r' % (str(raw)[:32],)
    v = float(raw)
    if math.isnan(v) or math.isinf(v):
        return None, 'value_not_finite:%r' % (str(raw)[:32],)
    return v, None


def dedup_by_date(records):
    """按observation_date聚合: 权威观测建立覆盖,非权威(快照/对账)只登记重复不新增。
    同日多个不同值(round 6位分组)全部保留→冲突候选,不擅自选定"真值"。"""
    out = {}
    for r in records:
        e = out.setdefault(r['obs_date'], {'values': OrderedDict(), 'auth': False,
                                           'files': set(), 'kinds': set(),
                                           'auth_files': set(), 'nonauth_files': set()})
        e['values'].setdefault(repr(round(r['value'], 6)), r['file'])
        e['files'].add(r['file'])
        e['kinds'].add(r['kind'])
        if r['auth']:
            e['auth'] = True
            e['auth_files'].add(r['file'])
        else:
            e['nonauth_files'].add(r['file'])
    return OrderedDict(sorted(out.items()))


def expected_slots(freq, first, last, calendar):
    """预期观测槽位: daily=交易日历(tc权威);weekly=ISO周;monthly=自然月。
    返回(expected键列表, 观测→键函数, 日历限制note或None, 原因或None)。"""
    if freq == 'daily':
        lim = CALENDAR_LIMITATIONS.get(calendar)
        days = tc.expected_trading_days(first, last, calendar)
        if days is None:
            return None, None, lim, '观察窗不可解析,预期槽位无法确定(不假装完整)'
        return days, (lambda d: str(d)[:10]), lim, None
    if freq == 'weekly':
        d0, d1 = date.fromisoformat(first), date.fromisoformat(last)
        weeks, cur = [], d0 - timedelta(days=d0.weekday())
        while cur <= d1:
            weeks.append(cur.isoformat())
            cur += timedelta(days=7)
        return weeks, _iso_week_monday, None, None
    if freq == 'monthly':
        d0, d1 = date.fromisoformat(first), date.fromisoformat(last)
        months, y, m = [], d0.year, d0.month
        while (y, m) <= (d1.year, d1.month):
            months.append('%04d-%02d' % (y, m))
            y, m = (y + 1, 1) if m == 12 else (y, m + 1)
        return months, (lambda d: str(d)[:7]), None, None
    return None, None, None, '频率未知(%r),预期槽位无法确定' % freq


def _iso_week_monday(iso):
    d = date.fromisoformat(str(iso)[:10])
    return (d - timedelta(days=d.weekday())).isoformat()


def segment_split(sorted_dates, freq):
    """连续段划分: 相邻观测日自然日间隔>频率阈值(公开工程阈值)即断段。"""
    if not sorted_dates:
        return []
    brk = THRESHOLDS['segment_break_natural_days'].get(freq, 10)
    segs, cur = [], [sorted_dates[0]]
    for prev, d in zip(sorted_dates, sorted_dates[1:]):
        if (date.fromisoformat(d) - date.fromisoformat(prev)).days > brk:
            segs.append(cur)
            cur = [d]
        else:
            cur.append(d)
    segs.append(cur)
    return [{'start': s[0], 'end': s[-1], 'slots': len(s)} for s in segs]


def max_internal_gap(sorted_dates):
    """相邻观测日最大自然日间隔(0=单点/无间隔)。"""
    if len(sorted_dates) < 2:
        return 0
    return max((date.fromisoformat(b) - date.fromisoformat(a)).days
               for a, b in zip(sorted_dates, sorted_dates[1:]))


def classify(metric, auth_dates, coverage_ratio, all_channel_unreadable):
    """状态分类(语义公开):
    DERIVED_ONLY=仅存在于派生计算; MISSING=未找到权威观测; UNREADABLE=权威通道
    输入存在但全部不可读; SINGLE_OBSERVATION=仅1个观测日;
    SPARSE=槽位覆盖率<0.5; OBSERVED=其余(≥2观测日)。"""
    src = str(metric.get('source')) + str(metric.get('source_symbol'))
    if '(derived)' in src:
        return 'DERIVED_ONLY'
    if not auth_dates:
        return 'UNREADABLE' if all_channel_unreadable else 'MISSING'
    if len(auth_dates) == 1:
        return 'SINGLE_OBSERVATION'
    if coverage_ratio is not None and coverage_ratio < THRESHOLDS['sparse_coverage_ratio_below']:
        return 'SPARSE'
    return 'OBSERVED'


# ════════════════ 路径与输入安全(W4-02 §5.1) ════════════════

def validate_paths(data_dir, out_dir):
    probs = []
    if not os.path.exists(data_dir):
        return ['数据目录不存在: %s' % data_dir]
    if not os.path.isdir(data_dir):
        probs.append('数据路径不是目录: %s' % data_dir)
    dr = os.path.realpath(data_dir)
    orp = os.path.realpath(out_dir)
    if dr == orp:
        probs.append('输出目录与数据目录相同')
    else:
        for a, b, la in ((dr, orp, '数据目录'), (orp, dr, '输出目录')):
            try:
                if os.path.commonpath([a, b]) == a:
                    probs.append('%s包含对方目录(重叠)' % la)
            except ValueError:
                probs.append('路径不可比较: %s vs %s' % (a, b))
    return probs


_FILE_DATE_RE = re.compile(r'_(\d{8})(?:_v\d+)?\.json$')


def discover_files(data_dir):
    """发现5通道机器输入文件(非递归;daily/子目录或data-dir本身)。
    符号链接文件不入清单(防越界,记录于excluded);文件日期取自文件名
    (仅用于观测日前瞻性核对,绝不作为观测日来源)。"""
    root = os.path.realpath(data_dir)
    base = root
    sub = os.path.join(root, 'daily')
    if os.path.isdir(sub) and (glob.glob(os.path.join(sub, 'global_*.json'))
                               or glob.glob(os.path.join(sub, 'macro_*.json'))):
        base = sub
    files, symlink_skipped, by_channel = [], [], {}
    for ch, pat in CHANNEL_PATTERNS.items():
        hits = sorted(glob.glob(os.path.join(base, pat)))
        by_channel[ch] = len(hits)
        for p in hits:
            if os.path.islink(p) or not os.path.isfile(p):
                if os.path.islink(p):
                    symlink_skipped.append(os.path.relpath(p, root))
                continue
            m = _FILE_DATE_RE.search(os.path.basename(p))
            fd = m.group(1) if m else None
            if fd and fe.parse_iso_date(fe._iso(fd)) is None:
                fd = None
            files.append({'path': p, 'relpath': os.path.relpath(p, root),
                          'channel': ch, 'file_date': fd})
    excluded = {'md_mirrors': len(glob.glob(os.path.join(base, '*.md'))),
                'anchors_files': len(glob.glob(os.path.join(base, 'anchors_*'))),
                'scorecard_files': len(glob.glob(os.path.join(base, 'scorecard_*'))),
                'anchor_prompt_files': len(glob.glob(os.path.join(base, 'anchor_prompt_*'))),
                'correlation_files': len(glob.glob(os.path.join(base, 'correlation_*'))),
                'symlink_skipped': symlink_skipped,
                'note': ('同前缀.md为采集器人读镜像,anchors/scorecard/anchor_prompt/'
                         'correlation为研究产物或上下文,news属W3新闻域——均非本审计'
                         '金融指标机器输入,未读入')}
    return files, base, excluded, by_channel


def build_manifest(files):
    """输入清单: 相对路径/大小/mtime_ns/SHA-256/采集器/文件日期/可读性。
    坏JSON不静默: readable=false+error记入清单并进入报告。"""
    manifest = []
    for f in files:
        entry = {'relpath': f['relpath'], 'channel': f['channel'],
                 'collector': CHANNEL_COLLECTOR[f['channel']], 'file_date': f['file_date']}
        try:
            st = os.stat(f['path'])
            entry['size'] = st.st_size
            entry['mtime_ns'] = st.st_mtime_ns
            with open(f['path'], 'rb') as fh:
                raw = fh.read()
            entry['sha256'] = hashlib.sha256(raw).hexdigest()
            try:
                entry['_parsed'] = json.loads(raw.decode('utf-8'))
                entry['readable'] = True
            except Exception as e:
                entry['readable'] = False
                entry['error'] = str(e)[:120]
        except Exception as e:
            entry['readable'] = False
            entry['error'] = 'read_fail:%s' % str(e)[:100]
        manifest.append(entry)
    return manifest


def manifest_digest(manifest):
    core = [{k: e[k] for k in ('relpath', 'size', 'mtime_ns', 'sha256', 'readable')}
            for e in manifest]
    return hashlib.sha256(json.dumps(core, sort_keys=True, ensure_ascii=False)
                          .encode('utf-8')).hexdigest()


# ════════════════ 观测提取(W4-04) ════════════════

class MetricAcc:
    """单指标累积器: 只留计数/日期聚合键/有界样例,不保留全量记录(内存可控)。"""
    __slots__ = ('raw', 'valid', 'auth_raw', 'nonauth_raw', 'invalid_date', 'invalid_value',
                 'length_mismatch', 'same_file_dup', 'out_of_order', 'future_obs',
                 'series_files', 'point_files', 'records', 'examples', 'revision_events')

    def __init__(self):
        self.raw = self.valid = self.auth_raw = self.nonauth_raw = 0
        self.invalid_date = self.invalid_value = self.length_mismatch = 0
        self.same_file_dup = self.out_of_order = self.future_obs = 0
        self.series_files, self.point_files = set(), set()
        self.records = []
        self.examples = {}
        self.revision_events = []

    def note(self, key, text):
        self.examples.setdefault(key, deque(maxlen=5)).append(text)


def _is_auth(metric_source, channel):
    """权威性=采集通道与注册表source声明通道一致;快照(Layer3)与对账通道恒非权威。"""
    if channel == 'research_snapshot':
        return False
    return REGISTRY_SOURCE_CHANNEL.get(metric_source) == channel


def _add_series(acc, series, channel, auth, relpath, fd_iso, kind):
    """series{dates,values}→观测。长度不一致如实记录且该series整体不入观测
    (无法安全配对);同文件重复日期/乱序/非法日/非法值逐项记录。"""
    if not isinstance(series, dict):
        acc.invalid_date += 1
        acc.note('series_shape', '%s series字段非对象' % relpath)
        return
    dates, values = series.get('dates'), series.get('values')
    if not isinstance(dates, list) or not isinstance(values, list):
        acc.invalid_date += 1
        acc.note('series_shape', '%s series.dates/values非列表' % relpath)
        return
    if len(dates) != len(values):
        acc.length_mismatch += 1
        acc.note('length_mismatch',
                 'dates=%d values=%d 不等长,整条不入观测' % (len(dates), len(values)))
        return
    acc.series_files.add(relpath)
    seen, prev_iso = set(), None
    for d_raw, v_raw in zip(dates, values):
        acc.raw += 1
        od, _rsn = to_obs_date(d_raw)
        val, _vsn = to_value(v_raw)
        if od is None:
            acc.invalid_date += 1
            acc.note('invalid_date', 'series %r' % (str(d_raw)[:32]))
            prev_iso = None
            continue
        if val is None:
            acc.invalid_value += 1
            acc.note('invalid_value', 'series %s %r' % (od, str(v_raw)[:24]))
            continue
        if od in seen:
            acc.same_file_dup += 1
        seen.add(od)
        if prev_iso is not None and od < prev_iso:
            acc.out_of_order += 1
            acc.note('out_of_order', '%s排在%s后' % (od, prev_iso))
        prev_iso = od
        if fd_iso and od > fd_iso:
            acc.future_obs += 1
            acc.note('future_obs', '观测日%s晚于文件日%s' % (od, fd_iso))
        acc.valid += 1
        if auth:
            acc.auth_raw += 1
        else:
            acc.nonauth_raw += 1
        acc.records.append({'obs_date': od, 'value': val, 'kind': kind,
                            'channel': channel, 'auth': auth, 'file': relpath})


def _add_point(acc, d_raw, v_raw, channel, auth, relpath, fd_iso, kind):
    acc.raw += 1
    od, _rsn = to_obs_date(d_raw)
    val, _vsn = to_value(v_raw)
    if od is None:
        acc.invalid_date += 1
        acc.note('invalid_date', 'point %r' % (str(d_raw)[:32]))
        return
    if val is None:
        acc.invalid_value += 1
        acc.note('invalid_value', 'point %s %r' % (od, str(v_raw)[:24]))
        return
    if fd_iso and od > fd_iso:
        acc.future_obs += 1
        acc.note('future_obs', '观测日%s晚于文件日%s' % (od, fd_iso))
    acc.valid += 1
    if auth:
        acc.auth_raw += 1
    else:
        acc.nonauth_raw += 1
    acc.point_files.add(relpath)
    acc.records.append({'obs_date': od, 'value': val, 'kind': kind,
                        'channel': channel, 'auth': auth, 'file': relpath})


def _unmapped(unmapped, channel, raw_key, relpath, note):
    e = unmapped.setdefault((channel, raw_key),
                            {'channel': channel, 'raw_key': raw_key, 'files': set(),
                             'note': note})
    e['files'].add(relpath)


def extract_file(entry, accs, unmapped, registry_ids, registry_by_id):
    """单个采集文件→观测/未注册记录。不静默跳过任何发现。"""
    rel, ch = entry['relpath'], entry['channel']
    fd_iso = fe._iso(entry['file_date']) if entry['file_date'] else None
    obj = entry['_parsed']

    def acc(mid):
        return accs.setdefault(mid, MetricAcc())

    def auth_of(mid):
        return _is_auth(registry_by_id[mid]['source'], ch)

    if ch == 'global':
        for aid, item in (obj.get('data') or {}).items():
            mid = GLOBAL_ID_MAP.get(aid, aid)
            if mid not in registry_ids or not isinstance(item, dict):
                _unmapped(unmapped, ch, aid, rel, 'global通道资产未注册或形态异常')
                continue
            a = acc(mid)
            _add_point(a, item.get('date'), item.get('close'), ch, auth_of(mid), rel, fd_iso, 'point')
            if item.get('series') is not None:
                _add_series(a, item.get('series'), ch, auth_of(mid), rel, fd_iso, 'series')
        return

    if ch == 'macro':
        for name, item in (obj.get('data') or {}).items():
            mid = MACRO_ALIAS.get(name, name)
            if mid not in registry_ids or not isinstance(item, dict):
                _unmapped(unmapped, ch, name, rel, 'macro通道序列未注册或形态异常')
                continue
            a = acc(mid)
            _add_point(a, item.get('date'), item.get('value'), ch, auth_of(mid), rel, fd_iso, 'point')
            if item.get('series') is not None:
                _add_series(a, item.get('series'), ch, auth_of(mid), rel, fd_iso, 'series')
            rev = item.get('revision')
            if isinstance(rev, dict) and rev.get('obs_date'):
                a.revision_events.append({'obs_date': rev.get('obs_date'),
                                          'prev_value': rev.get('prev_value'),
                                          'value': rev.get('value'), 'file': rel})
        for dmid, dv in (obj.get('derived') or {}).items():
            if dmid in registry_ids:
                # derived块只有当日计算值,无observation_date字段——不以文件日补造,
                # 如实记为不可用观测日(派生指标本无独立原始历史)。
                a = acc(dmid)
                a.raw += 1
                a.invalid_date += 1
                a.note('invalid_date', 'derived块%s无观测日字段(不以文件日补造)' % dmid)
            else:
                _unmapped(unmapped, ch, 'derived:' + str(dmid), rel, 'macro derived块键未注册')
        return

    if ch == 'china':
        def mapped(key, table, note):
            mid = table.get(key)
            if mid is None or mid not in registry_ids:
                _unmapped(unmapped, ch, key, rel, note)
                return None
            return mid
        for code, item in (obj.get('a_share_indices') or {}).items():
            mid = mapped(code, CHINA_A_CODE, 'A股代码未注册(采集但不入注册表)')
            if mid and isinstance(item, dict):
                a = acc(mid)
                _add_point(a, item.get('date'), item.get('close'), ch, True, rel, fd_iso, 'point')
                if item.get('series') is not None:
                    _add_series(a, item.get('series'), ch, True, rel, fd_iso, 'series')
        for code, item in (obj.get('hk_indices') or {}).items():
            mid = mapped(code, CHINA_HK_CODE, '港股键未注册')
            if mid and isinstance(item, dict):
                a = acc(mid)
                _add_point(a, item.get('date'), item.get('close'), ch, True, rel, fd_iso, 'point')
                if item.get('series') is not None:
                    _add_series(a, item.get('series'), ch, True, rel, fd_iso, 'series')
        for label_key, table, note in (('indices', CHINA_LEGACY_LABEL, '标签代指数未注册'),
                                       ('a_share', CHINA_LEGACY_LABEL, '最旧代a_share标签未注册'),
                                       ('hk', CHINA_LEGACY_LABEL, '最旧代hk标签未注册')):
            for label, item in (obj.get(label_key) or {}).items():
                mid = mapped(label, table, note)
                if mid and isinstance(item, dict):
                    a = acc(mid)
                    if label_key != 'indices':
                        a.note('legacy_format',
                               '最旧代格式(当前fact_engine不消费该格式,历史覆盖仍如实计入)')
                    _add_point(a, item.get('date'), item.get('close'), ch, True, rel, fd_iso,
                               'legacy_point')
        ah = obj.get('ah_premium') or {}
        if isinstance(ah, dict) and ah.get('close') is not None:
            _add_point(acc('HSAHP'), ah.get('date'), ah.get('close'), ch, True, rel, fd_iso, 'point')
        sb = obj.get('southbound') or {}
        if isinstance(sb, dict):
            if sb.get('net_buy') is not None:
                _add_point(acc('SB_FLOW'), sb.get('date'), sb.get('net_buy'),
                           ch, True, rel, fd_iso, 'point')
            elif sb.get('south_money') is not None:
                v, _ = to_value(sb.get('south_money'))
                a = acc('SB_FLOW')
                a.note('unit_transform', 'south_money百万→亿港元(与fe.normalize_china同口径)')
                _add_point(a, sb.get('date'), round(v / 100.0, 2) if v is not None else None,
                           ch, True, rel, fd_iso, 'point')
            elif sb.get('latest') is not None:
                _unmapped(unmapped, ch, 'southbound.latest', rel,
                          '最旧代南向latest字段语义未注册(不入SB_FLOW)')
        mg = obj.get('margin') or {}
        if isinstance(mg, dict):
            if mg.get('balance') is not None:
                _add_point(acc('MARGIN_BAL'), mg.get('date'), mg.get('balance'),
                           ch, True, rel, fd_iso, 'point')
            elif mg.get('rzye_billion') is not None:
                a = acc('MARGIN_BAL')
                a.note('field_semantics',
                       'rzye_billion=融资余额(亿元);注册语义=两融余额存量;且'
                       'fe.normalize_china期望balance键(新格式不被消费→快照缺该事实)')
                _add_point(a, mg.get('date'), mg.get('rzye_billion'), ch, True, rel, fd_iso, 'point')
        val = obj.get('valuation') or {}
        if isinstance(val, dict):
            if isinstance(val.get('pe'), (int, float)):
                _add_point(acc('SH_PE'), val.get('date'), val.get('pe'),
                           ch, True, rel, fd_iso, 'point')
            for code, item in val.items():
                if isinstance(item, dict) and item.get('pe_ttm') is not None:
                    _unmapped(unmapped, ch, 'valuation:%s.pe_ttm' % code, rel,
                              '新格式嵌套估值(仅300/500/1000;注册SH_PE语义=上证PE,非同身份)')
        to = obj.get('turnover') or {}
        if isinstance(to, dict) and to:
            obs, sh, sz = to.get('date'), to.get('sh_amount_billion'), to.get('sz_amount_billion')
            _add_point(acc('SH_AMOUNT'), obs, sh, ch, True, rel, fd_iso, 'point')
            _add_point(acc('SZ_COMPONENT_AMOUNT'), obs, sz, ch, True, rel, fd_iso, 'point')
            if isinstance(sh, (int, float)) and isinstance(sz, (int, float)):
                _add_point(acc('CN_TOTAL_TURNOVER'), obs, round(sh + sz, 2),
                           ch, True, rel, fd_iso, 'point')
            elif to.get('total_amount_billion') is not None:
                a = acc('CN_TOTAL_TURNOVER')
                a.note('field_semantics', 'akshare降级:仅沪市total_amount_billion(fe同口径回退)')
                _add_point(a, obs, to.get('total_amount_billion'), ch, True, rel, fd_iso, 'point')
        if isinstance(obj.get('volume'), dict) and obj['volume'].get('volume') is not None:
            _unmapped(unmapped, ch, 'volume.volume', rel, '最旧代成交量(股)字段未注册')
        return

    if ch == 'rate_economy':
        rate_cur_map = {'FEDFUNDS': 'FED_FUNDS'}  # 通道原始键→注册id(FED_FUNDS权威=macro)
        for key, item in (obj.get('current_rates') or {}).items():
            mid = rate_cur_map.get(key, key)
            if mid not in registry_ids or not isinstance(item, dict):
                _unmapped(unmapped, ch, 'current_rates:' + str(key), rel, 'rate通道current_rates键未注册')
                continue
            # FED_FUNDS注册权威=macro_collector→本通道记录为非权威(不新增覆盖)
            _add_point(acc(mid), item.get('date'), item.get('value'), ch,
                       auth_of(mid), rel, fd_iso, 'point')
        for name, item in (obj.get('real_economy') or {}).items():
            mid = RATE_REAL_ECONOMY_MAP.get(name)
            if mid is None or not isinstance(item, dict):
                _unmapped(unmapped, ch, 'real_economy:' + name, rel, 'rate通道real_economy键未注册')
                continue
            _add_point(acc(mid), item.get('date'), item.get('value'),
                       ch, False, rel, fd_iso, 'recon_point')
        for r in (obj.get('fed_funds_futures') or []):
            if not isinstance(r, dict):
                continue
            tk = str(r.get('ticker'))
            if tk == 'ZQ=F':
                _add_point(acc('ZQ_F1_PRICE'), r.get('date'), r.get('price'),
                           ch, True, rel, fd_iso, 'point')
            elif tk:
                _unmapped(unmapped, ch, 'futures:' + tk, rel,
                          '非主力月份合约未注册(曲线上下文,非独立指标)')
        return

    if ch == 'research_snapshot':
        for f in obj.get('facts') or []:
            if not isinstance(f, dict):
                continue
            mid = f.get('metric_id')
            if mid not in registry_ids:
                _unmapped(unmapped, ch, 'fact:' + str(mid), rel, '快照事实metric未注册')
                continue
            _add_point(acc(mid), f.get('observation_date'), f.get('value'),
                       ch, False, rel, fd_iso, 'snapshot_point')
        for mid, series in (obj.get('series_store') or {}).items():
            if mid not in registry_ids:
                _unmapped(unmapped, ch, 'series_store:' + str(mid), rel, '快照series_store键未注册')
                continue
            _add_series(acc(mid), series, ch, False, rel, fd_iso, 'snapshot_series')
        return


# ════════════════ 指标聚合(W4-03/04/05/06) ════════════════

def build_metric_record(m, accs, channel_unreadable, by_channel):
    mid = m['metric_id']
    a = accs.get(mid)
    reg_channel = REGISTRY_SOURCE_CHANNEL.get(m['source'])
    ch_n = by_channel.get(reg_channel, 0)
    ch_unread = channel_unreadable.get(reg_channel, 0)
    all_unread = ch_n > 0 and ch_unread == ch_n
    rec = {
        'metric_id': mid, 'display_name': m['display_name'], 'source': m['source'],
        'source_symbol': m.get('source_symbol'), 'registry_status': m.get('status'),
        'criticality': m.get('criticality'), 'frequency': m['frequency'],
        'calendar': m['calendar'], 'unit': m.get('unit'), 'identity': m.get('identity'),
        'asset_class': m.get('asset_class'), 'calc': m.get('calc'),
        'authority_channel': reg_channel,
        'research_sufficiency': 'UNDETERMINED',
    }
    if a is None:
        rec['discovery'] = {'found': False,
                            'note': ('派生指标:无独立原始历史存档(由输入序列计算)'
                                     if '(derived)' in str(m['source']) + str(m.get('source_symbol'))
                                     else '数据集中未发现该指标任何记录(含非权威通道)')}
        rec['counts'] = {k: 0 for k in (
            'raw_records', 'valid_records', 'invalid_date_records', 'invalid_value_records',
            'length_mismatch_series', 'authority_raw_records', 'non_authority_records',
            'unique_observation_dates', 'authority_unique_observation_dates',
            'cross_file_duplicate_records', 'same_file_duplicate_dates',
            'out_of_order_records', 'future_dated_observations',
            'distinct_value_conflict_dates', 'revision_events_detected')}
        rec['coverage'] = {'first_observation_date': None, 'last_observation_date': None,
                           'observation_span_days': None, 'total_unique_observations': 0,
                           'expected_observation_slots': None, 'observed_slots': None,
                           'missing_slots_count': None, 'coverage_ratio': None,
                           'longest_continuous_segment_slots': 0, 'continuous_segments': [],
                           'usable_intervals': [], 'calendar_limitations': None,
                           'max_internal_gap_days': None}
        rec['status'] = classify(m, [], None, all_unread)
        return rec

    dates = dedup_by_date(a.records)
    auth_dates = [d for d, e in dates.items() if e['auth']]
    conflicts = [{'obs_date': d, 'distinct_values': list(e['values'].keys()),
                  'first_files': list(e['values'].values())}
                 for d, e in dates.items() if len(e['values']) > 1]
    expected = observed_slots = coverage_ratio = None
    missing_slots, extra_slots, lim_note, slot_reason = [], [], None, None
    segs, longest, gap, span = [], 0, None, None
    if auth_dates:
        first, last = auth_dates[0], auth_dates[-1]
        span = (date.fromisoformat(last) - date.fromisoformat(first)).days
        exp_list, keyfn, lim, reason = expected_slots(m['frequency'], first, last, m['calendar'])
        lim_note, slot_reason = lim, reason
        if exp_list is not None:
            expected = len(exp_list)
            obs_keys = {keyfn(d) for d in auth_dates}
            observed_slots = len(obs_keys & set(exp_list))
            missing_slots = [k for k in exp_list if k not in obs_keys]
            extra_slots = sorted(obs_keys - set(exp_list))
            coverage_ratio = (observed_slots / expected) if expected else None
        segs = segment_split(auth_dates, m['frequency'])
        longest = max((s['slots'] for s in segs), default=0)
        gap = max_internal_gap(auth_dates)
    rec['discovery'] = {
        'found': True,
        'authority_channel_records': a.auth_raw,
        'non_authority_records': a.nonauth_raw,
        'series_available': bool(a.series_files),
        'series_files_sample': sorted(a.series_files)[:3],
        'point_files_sample': sorted(a.point_files)[:3],
        'non_authority_only_dates': [d for d, e in dates.items() if not e['auth']],
        'notes': {k: list(v) for k, v in a.examples.items()},
    }
    rec['counts'] = {
        'raw_records': a.raw, 'valid_records': a.valid,
        'invalid_date_records': a.invalid_date, 'invalid_value_records': a.invalid_value,
        'length_mismatch_series': a.length_mismatch,
        'authority_raw_records': a.auth_raw, 'non_authority_records': a.nonauth_raw,
        'unique_observation_dates': len(dates),
        'authority_unique_observation_dates': len(auth_dates),
        'cross_file_duplicate_records': max(a.auth_raw - len(auth_dates), 0),
        'same_file_duplicate_dates': a.same_file_dup,
        'out_of_order_records': a.out_of_order,
        'future_dated_observations': a.future_obs,
        'distinct_value_conflict_dates': len(conflicts),
        'revision_events_detected': len(a.revision_events),
    }
    rec['coverage'] = {
        'first_observation_date': auth_dates[0] if auth_dates else None,
        'last_observation_date': auth_dates[-1] if auth_dates else None,
        'observation_span_days': span,
        'total_unique_observations': len(auth_dates),
        'expected_observation_slots': expected, 'observed_slots': observed_slots,
        'missing_slots_count': len(missing_slots), 'missing_slots_sample': missing_slots[:10],
        'extra_observations_beyond_calendar': len(extra_slots),
        'coverage_ratio': round(coverage_ratio, 4) if coverage_ratio is not None else None,
        'longest_continuous_segment_slots': longest,
        'continuous_segments': segs,
        'usable_intervals': [s for s in segs if s['slots'] >= 2],
        'calendar_limitations': lim_note, 'slots_unavailable_reason': slot_reason,
        'max_internal_gap_days': gap,
    }
    rec['conflict_candidates'] = conflicts[:10]
    rec['revision_events'] = a.revision_events[:10]
    rec['input_degraded'] = ch_unread > 0
    rec['status'] = classify(m, auth_dates, coverage_ratio, all_unread)
    rec['sufficiency_note'] = ('无既定最小样本阈值;W4不判定"足够支持N年研究"(属W5/研究层),'
                               '仅报告可从本地数据证明的覆盖事实')
    return rec


# ════════════════ 汇总/发现(W4-06/07) ════════════════

def summarize(metrics, unmapped_list=()):
    by_status = {}
    for r in metrics:
        by_status.setdefault(r['status'], []).append(r['metric_id'])
    core_active = [r for r in metrics
                   if r['criticality'] == 'core' and r['registry_status'] == 'active']
    core_by_status = {}
    for r in core_active:
        core_by_status.setdefault(r['status'], []).append(r['metric_id'])
    t = THRESHOLDS
    complete, recent_only, serious = [], [], []
    for r in metrics:
        c = r['coverage']
        ratio, uniq = c['coverage_ratio'], c['total_unique_observations']
        span = c['observation_span_days']
        if r['status'] == 'OBSERVED' and ratio is not None \
                and ratio >= t['complete_history_min_ratio'] \
                and uniq >= t['complete_history_min_unique_obs']:
            complete.append(r['metric_id'])
        if uniq >= 1 and span is not None and span < t['recent_only_span_days_max']:
            recent_only.append(r['metric_id'])
        brk = t['serious_break_days'].get(r['frequency'], 10)
        if uniq >= 2 and c['max_internal_gap_days'] is not None \
                and c['max_internal_gap_days'] > brk:
            serious.append({'metric_id': r['metric_id'],
                            'max_internal_gap_days': c['max_internal_gap_days']})
    with_series = [r['metric_id'] for r in metrics if r['discovery'].get('series_available')]
    point_only = [r['metric_id'] for r in metrics
                  if r['status'] in ('OBSERVED', 'SPARSE', 'SINGLE_OBSERVATION')
                  and not r['discovery'].get('series_available')]
    firsts = [r['coverage']['first_observation_date'] for r in metrics
              if r['coverage']['first_observation_date']]
    findings = OrderedDict()
    findings['1_哪些指标有较完整现有历史'] = {
        'definition': "OBSERVED且coverage_ratio≥%.0f%%且独立观测日≥%d(工程描述阈值)"
                      % (t['complete_history_min_ratio'] * 100, t['complete_history_min_unique_obs']),
        'metrics': complete}
    findings['2_哪些指标只有最近数据'] = {
        'definition': '首末跨度<%d自然日(工程描述阈值)' % t['recent_only_span_days_max'],
        'metrics': recent_only}
    findings['3_哪些指标中间存在严重断点'] = {
        'definition': '相邻观测日最大间隔>频率断段阈值(日%d/周%d/月%d自然日,工程描述阈值)'
                      % (t['serious_break_days']['daily'], t['serious_break_days']['weekly'],
                         t['serious_break_days']['monthly']),
        'metrics': serious}
    findings['4_哪些指标未保存历史'] = {
        'definition': 'MISSING=未找到权威观测;UNREADABLE=输入全不可读;DERIVED_ONLY=仅派生计算',
        'MISSING': by_status.get('MISSING', []),
        'UNREADABLE': by_status.get('UNREADABLE', []),
        'DERIVED_ONLY': by_status.get('DERIVED_ONLY', [])}
    findings['5_哪些数据无法支持研究区间判断'] = (
        '全部指标research_sufficiency=UNDETERMINED(无既定最小样本阈值,不判定'
        '"足够支持N年研究");日历近似限制(cn/hk/fx等)见逐项coverage.calendar_limitations')
    findings['6_现有历史覆盖的主要限制'] = [
        '带原始序列(series)存档的指标%d/%d;全部权威观测最早日=%s——历史边界由'
        'series保存起点与采集回看窗口共同决定,更早历史无法从本存档重建'
        % (len(with_series), len(metrics), min(firsts) if firsts else '无'),
        '仅单点无序列指标%d个(历史窗口研究须等待序列累积或由W5另行授权回补)'
        % len(point_only),
        '未注册原始键%d组独立披露于unmapped_records(不冒充任何注册指标)'
        % len(unmapped_list),
    ]
    summary = {
        'registered_metrics': len(metrics),
        'with_authority_observations': len([r for r in metrics if r['status'] in
                                            ('OBSERVED', 'SPARSE', 'SINGLE_OBSERVATION')]),
        'series_backed': len(with_series),
        'single_observation_only': len(by_status.get('SINGLE_OBSERVATION', [])),
        'no_data': len(by_status.get('MISSING', [])),
        'unreadable': len(by_status.get('UNREADABLE', [])),
        'derived_only': len(by_status.get('DERIVED_ONLY', [])),
        'by_status': {k: len(v) for k, v in sorted(by_status.items())},
        'core_by_status': {k: len(v) for k, v in sorted(core_by_status.items())},
        'core_missing_or_unreadable': [m for s in ('MISSING', 'UNREADABLE')
                                       for m in core_by_status.get(s, [])],
    }
    return summary, findings


def render_markdown(result):
    rid, summary, findings = result['run_id'], result['summary'], result['findings']
    metrics, integ = result['metrics'], result['integrity']
    unmapped, excluded = result['unmapped_records'], result['input']['excluded']
    L = ['# 历史覆盖审计报告 %s' % rid, '',
         '- 工具: %s / %s(只读审计;输出位于数据根之外)' % (TOOL_NAME, SCHEMA_VERSION),
         '- 数据来源说明: %s' % (result['input'].get('source_note') or '(未提供--source-note)'),
         '- 输入完整性: %s' % ('逐文件SHA-256复检一致(审计期间输入未变化)'
                             if not integ['input_changed_during_audit']
                             else '**INPUT_CHANGED_DURING_AUDIT(%d文件变化,结论按非冻结数据集对待)**'
                             % len(integ['changed_files'])),
         '- 阈值定义公开于文末(工程描述约定,非金融事实)', '']
    L += ['## 总体', '| 项 | 数 |', '|---|---|']
    for k, lab in (('registered_metrics', '已注册指标'),
                   ('with_authority_observations', '有权威历史观测(OBSERVED+SPARSE+SINGLE)'),
                   ('series_backed', '其中带原始序列(series)'),
                   ('single_observation_only', '仅单点观测'),
                   ('no_data', '无数据(MISSING)'), ('unreadable', '不可读(UNREADABLE)'),
                   ('derived_only', '仅派生(DERIVED_ONLY)')):
        L.append('| %s | %d |' % (lab, summary[k]))
    L += ['', '状态分布: `%s`' % json.dumps(summary['by_status'], ensure_ascii=False),
          'core(active)分布: `%s`' % json.dumps(summary['core_by_status'], ensure_ascii=False)]
    if summary['core_missing_or_unreadable']:
        L += ['', '**⚠️ core缺失/不可读: %s**' % ', '.join(summary['core_missing_or_unreadable'])]
    L += ['', '输入文件: %d个(%s);排除项(未读入): %s'
          % (result['input']['files'], json.dumps(result['input']['by_channel']),
             json.dumps({k: v for k, v in excluded.items() if k != 'note'}, ensure_ascii=False)),
         '', '## 逐项覆盖(全部%d项注册指标,无数据者也输出)' % len(metrics),
         '| 指标 | 名称 | 状态 | 频率 | 最早 | 最晚 | 独立观测日 | 覆盖率 | 缺槽 | 最长连续段 | 限制 |',
         '|---|---|---|---|---|---|---|---|---|---|---|']
    for r in metrics:
        c, d = r['coverage'], r['discovery']
        ratio = c['coverage_ratio']
        lim = c['calendar_limitations'] or ''
        lim = (lim[:16] + '…') if len(lim) > 18 else lim
        L.append('| %s | %s | %s%s | %s | %s | %s | %d | %s | %s | %s | %s |' % (
            r['metric_id'], r['display_name'], r['status'],
            '⚠️输入降级' if r.get('input_degraded') else '',
            r['frequency'], c['first_observation_date'] or '—',
            c['last_observation_date'] or '—', c['total_unique_observations'],
            ('%.0f%%' % (ratio * 100)) if ratio is not None else '—',
            c['missing_slots_count'] if c['missing_slots_count'] is not None else '—',
            c['longest_continuous_segment_slots'], lim or '—'))
    L += ['', '## 审计发现']
    for k, v in findings.items():
        L.append('**%s**' % k)
        if isinstance(v, dict):
            for kk, vv in v.items():
                if isinstance(vv, list):
                    shown = ', '.join(map(str, vv[:40])) + ('…' if len(vv) > 40 else '')
                    L.append('- %s(%d): %s' % (kk, len(vv), shown))
                else:
                    L.append('- %s: %s' % (kk, vv))
        else:
            L.append('- %s' % v)
        L.append('')
    if unmapped:
        L += ['## 未注册来源记录(unmapped_records,独立披露不丢失)', '| 通道 | 原始键 | 文件数 | 说明 |',
              '|---|---|---|---|']
        for e in unmapped:
            L.append('| %s | %s | %d | %s |' % (e['channel'], e['raw_key'],
                                                 len(e['files']), e['note']))
        L.append('')
    L += ['## 阈值定义与依据(工程描述约定,非金融事实)', '```json',
          json.dumps(result['threshold_definitions'], ensure_ascii=False, indent=2), '```', '',
          BASIS_NOTE, '', '## 日历近似限制']
    for k, v in CALENDAR_LIMITATIONS.items():
        L.append('- %s: %s' % (k, v))
    L += ['', '## 证据限制',
          '- 本报告只证明**本地已存档数据**的覆盖;不证明数值金融真实性(属W5)。',
          '- 单次快照式审计;生产目录若由计划任务持续更新,应在冻结副本上复核(见输入清单)。',
          '- 全部指标 research_sufficiency=UNDETERMINED。',
          '- 逐指标异常明细(非法日/非法值/乱序/冲突/修订/长度不一致)见JSON'
            ' counts/notes/conflict_candidates字段,可由输入文件逐条复算。']
    return '\n'.join(L) + '\n'


# ════════════════ 主流程 ════════════════

def run_audit(data_dir, out_dir, registry_path, source_note=None, log=None):
    """执行审计。返回(result_dict, log_lines, exit_code)。"""
    log = log if log is not None else []

    def wmsg(s):
        log.append('[%s] %s' % (datetime.now(timezone.utc).isoformat(timespec='seconds'), s))

    base_result = {'tool': TOOL_NAME, 'schema_version': SCHEMA_VERSION,
                   'input': {'data_dir': data_dir, 'source_note': source_note}}
    probs = validate_paths(data_dir, out_dir)
    if probs:
        for p in probs:
            wmsg('路径校验失败: ' + p)
        base_result['audit_status'] = 'INVALID_PATH'
        base_result['problems'] = probs
        return base_result, log, 2
    wmsg('数据目录: %s (realpath %s)' % (data_dir, os.path.realpath(data_dir)))
    wmsg('输出目录: %s (realpath %s)' % (out_dir, os.path.realpath(out_dir)))

    with open(registry_path, 'r', encoding='utf-8') as f:
        reg = json.load(f)
    metrics_reg = reg.get('metrics', [])
    registry_ids = {m['metric_id'] for m in metrics_reg}
    registry_by_id = {m['metric_id']: m for m in metrics_reg}
    wmsg('注册表: %s (%d指标)' % (registry_path, len(metrics_reg)))

    files, _base, excluded, by_channel = discover_files(data_dir)
    wmsg('发现输入文件%d个: %s' % (len(files), json.dumps(by_channel)))
    if excluded['symlink_skipped']:
        wmsg('⚠️ 跳过符号链接文件%d个(防越界读取): %s'
             % (len(excluded['symlink_skipped']), excluded['symlink_skipped'][:5]))
    if not files:
        wmsg('无可用输入(0个通道文件)——不得宣布成功完成真实审计')
        base_result.update({'audit_status': 'NO_INPUT', 'by_channel': by_channel,
                            'excluded': excluded})
        return base_result, log, 2

    manifest = build_manifest(files)
    readable = [e for e in manifest if e.get('readable')]
    unreadable = [e for e in manifest if not e.get('readable')]
    wmsg('输入清单: %d文件, 可读%d, 不可读%d' % (len(manifest), len(readable), len(unreadable)))
    for e in unreadable:
        wmsg('  ⚠️ 不可读: %s (%s)' % (e['relpath'], e.get('error', '')[:80]))
    run_id = 'ra_' + manifest_digest(manifest)[:12]
    wmsg('run_id=%s(由输入清单摘要决定: 同输入同ID,输出可复算比对)' % run_id)
    base_result['run_id'] = run_id

    channel_unreadable = {}
    for e in unreadable:
        channel_unreadable[e['channel']] = channel_unreadable.get(e['channel'], 0) + 1

    accs, unmapped = {}, {}
    for e in readable:
        try:
            extract_file(e, accs, unmapped, registry_ids, registry_by_id)
        except Exception as ex:
            wmsg('  ⚠️ 提取异常(%s): %s' % (e['relpath'], str(ex)[:100]))
            e['extract_error'] = str(ex)[:160]
    wmsg('观测提取完成: 出现过的指标%d个, 未注册键%d组' % (len(accs), len(unmapped)))

    metric_records = [build_metric_record(m, accs, channel_unreadable, by_channel)
                      for m in metrics_reg]
    unmapped_list = sorted((dict(v, files=sorted(v['files'])) for v in unmapped.values()),
                           key=lambda x: (x['channel'], x['raw_key']))
    summary, findings = summarize(metric_records, unmapped_list)
    wmsg('指标状态分布: %s' % json.dumps(summary['by_status'], ensure_ascii=False))
    if summary['core_missing_or_unreadable']:
        wmsg('⚠️ core缺失/不可读: %s' % ', '.join(summary['core_missing_or_unreadable']))

    # 输入完整性复检(§5.2): 逐文件重算SHA-256
    sha_by_rel = {e['relpath']: e.get('sha256') for e in manifest}
    changed = []
    for f in files:
        try:
            with open(f['path'], 'rb') as fh:
                h = hashlib.sha256(fh.read()).hexdigest()
            if h != sha_by_rel.get(f['relpath']):
                changed.append(f['relpath'])
        except Exception:
            changed.append(f['relpath'] + '(read_fail)')
    input_changed = bool(changed)
    if input_changed:
        wmsg('⚠️ INPUT_CHANGED_DURING_AUDIT: %d文件在扫描期间变化: %s' % (len(changed), changed[:5]))
    else:
        wmsg('输入完整性复检: %d文件SHA-256全部一致(冻结读取)' % len(files))

    if not readable:
        audit_status, exit_code = 'ALL_UNREADABLE', 2
    elif input_changed:
        audit_status, exit_code = 'INPUT_CHANGED', 3
    else:
        audit_status, exit_code = 'COMPLETED', 0
    manifest_dump = [{k: e.get(k) for k in ('relpath', 'channel', 'collector', 'file_date',
                                            'size', 'mtime_ns', 'sha256', 'readable',
                                            'error', 'extract_error')}
                     for e in manifest]
    result = dict(base_result)
    result.update({
        'audit_status': audit_status,
        'registry': {'path': registry_path, 'version': reg.get('version'),
                     'metric_count': len(metrics_reg)},
        'input': dict(base_result['input'],
                      data_dir_realpath=os.path.realpath(data_dir),
                      files=len(manifest), by_channel=by_channel,
                      unreadable_files=[e['relpath'] for e in unreadable],
                      excluded=excluded),
        'summary': summary, 'metrics': metric_records,
        'unmapped_records': unmapped_list, 'findings': findings,
        'threshold_definitions': dict(THRESHOLDS, basis=BASIS_NOTE,
                                      calendar_limitations=CALENDAR_LIMITATIONS),
        'integrity': {'input_changed_during_audit': input_changed,
                      'changed_files': changed,
                      'manifest_digest': manifest_digest(manifest),
                      'recheck': '审计结束后逐文件SHA-256重算比对清单初值'},
        'manifest': manifest_dump,
    })
    wmsg('audit_status=%s' % audit_status)
    return result, log, exit_code


def main(argv=None):
    ap = argparse.ArgumentParser(description='IA-P0-2-W4 历史覆盖只读审计器(只读数据/只写独立输出)')
    ap.add_argument('--data-dir', required=True, help='授权数据集根(含daily/子目录或即daily目录)')
    ap.add_argument('--out-dir', required=True, help='独立审计输出目录(必须在数据根之外)')
    ap.add_argument('--registry', default=None,
                    help='指标注册表JSON(默认=代码库config/metric_registry.json)')
    ap.add_argument('--source-note', default=None, help='真实数据来源与授权范围说明(记入报告)')
    args = ap.parse_args(argv)
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    registry = args.registry or os.path.join(root, 'config', 'metric_registry.json')
    log = []
    result, log, exit_code = run_audit(args.data_dir, args.out_dir, registry,
                                       source_note=args.source_note, log=log)
    if result['audit_status'] in ('COMPLETED', 'INPUT_CHANGED', 'ALL_UNREADABLE'):
        # 只有拿到run_id的完成类状态才写输出;INVALID_PATH/NO_INPUT不向
        # (可能非法的)out-dir写入任何文件,只打印日志。
        os.makedirs(args.out_dir, exist_ok=True)
        rid = result['run_id']
        manifest_path = os.path.join(args.out_dir, 'input_manifest_%s.json' % rid)
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump({'run_id': rid, 'data_dir': result['input']['data_dir'],
                       'data_dir_realpath': result['input'].get('data_dir_realpath'),
                       'digest': result['integrity']['manifest_digest'],
                       'files': result['manifest']}, f, ensure_ascii=False, indent=1)
        json_path = os.path.join(args.out_dir, 'coverage_audit_%s.json' % rid)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({k: v for k, v in result.items() if k != 'manifest'},
                      f, ensure_ascii=False, indent=1)
        md_path = os.path.join(args.out_dir, 'coverage_audit_%s.md' % rid)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(render_markdown(result))
        outputs = {}
        for p in (manifest_path, json_path, md_path):
            with open(p, 'rb') as fh:
                outputs[os.path.basename(p)] = hashlib.sha256(fh.read()).hexdigest()
        wline = '输出: ' + json.dumps(outputs, ensure_ascii=False)
        log.append(wline)
    log.append('audit_status=%s exit_code=%d' % (result['audit_status'], exit_code))
    if result['audit_status'] in ('COMPLETED', 'INPUT_CHANGED', 'ALL_UNREADABLE'):
        log_path = os.path.join(args.out_dir, 'audit_execution_%s.log' % result['run_id'])
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(log) + '\n')
    print('\n'.join(log[-8:]))
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
