#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-DATA-W2 指标覆盖审计工具(只读诊断)。

对 config/metric_registry.json 登记的全部指标,在指定数据目录(审计窗口=目录内
全部 <channel>_<YYYYMMDD>.json 文件)上逐指标产出**机器可读**的覆盖事实:
数据面存在性 / 字段存在性 / 取值空与非空 / 计数汇总。

设计纪律(IA-DATA-W2-AC-v1.0 W2-AC-02):
- 仅 Python 标准库(import 面零第三方依赖);
- 对 registry 与数据目录**只读**(仅 open(...,'r');唯一写出=调用方显式 --out);
- 本工具不裁决 N/S/B/C/U 研究分类,只输出机械事实;分类学判定见
  docs/DATA_W2_DELIVERY.md §分类规则(判定若依赖代码侧证据,由报告层附 文件:行)。

映射规则出处(读侧面=事实引擎消费路径,写侧面=采集器成功路径):
- global:  fact_engine.py L244-245 _GLOBAL_ID_MAP(文件资产键→注册表ID,本表存其逆);
           L247-272 normalize_global(data[资产键].close)
- macro:   fact_engine.py L281 _MACRO_ALIAS(WTI→WTI_SPOT_M,本表存其逆);
           L275-298 normalize_macro(data[键].value)
- macro(derived): macro_collector.py L257-275 calc_derived → 顶层 derived{ID: 值}
           (normalize_macro 不读该字典;REAL_SHORT 等弃用指标仅存于此)
- rate:    fact_engine.py L417-427 normalize_rate(current_rates[键].value)、
           L437-458 fed_funds_futures 行 ticker=='ZQ=F' 的 price
- china:   fact_engine.py L322-391 normalize_china(a_share_indices/hk_indices/
           ah_premium/southbound/margin/valuation/turnover 各路径)
- 派生:    fact_engine.py L462-500 compute_derived 依赖表(REAL_10Y/REAL_5Y/
           HY_IG_DIFF/ZQ_IMPLIED_AVG/NFP_MOM_K)

退出码: 正常产出报告=0(无论覆盖事实好坏);异常输入(路径不存在/JSON不可解析/
registry 无 metrics 数组等)=2 并向 stderr 报错。语义详见 DELIVERY §用法。
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import sys

SCHEMA_VERSION = 1

# ── 通道文件名模式(审计窗口只收这些;*.md 等非通道文件不入窗) ──────────
CHANNEL_PATTERNS = {
    'global': re.compile(r'^global_(\d{8})\.json$'),
    'macro': re.compile(r'^macro_(\d{8})\.json$'),
    'china': re.compile(r'^china_(\d{8})\.json$'),
    'rate_economy': re.compile(r'^rate_economy_(\d{8})\.json$'),
}

# ── 注册表ID → global 文件资产键(fact_engine L244-245 _GLOBAL_ID_MAP 之逆;其余恒等) ──
GLOBAL_FILE_KEY = {
    'GOLD_F': 'GOLD', 'SILVER_F': 'SILVER', 'WTI_F': 'WTI', 'BRENT_F': 'BRENT',
    'USDJPY': 'JPY=X', 'USDCNY': 'CNY=X', 'GBPUSD': 'GBPUSD=X',
}

# ── 注册表ID → macro 文件 data 键(fact_engine L281 _MACRO_ALIAS 之逆;其余恒等) ──
MACRO_FILE_KEY = {'WTI_SPOT_M': 'WTI'}

# ── china 指标 → 文件内取值路径(fact_engine L322-391 normalize_china) ──
#     路径元组逐层下行;CN_TOTAL_TURNOVER 为主路径 sh+sz 双依赖(引擎 L381-385),
#     akshare 降级单键 total_amount_billion 为备路径(引擎 L386-391)。
CHINA_PATHS = {
    'SHCOMP': [('a_share_indices', '000001.SH', 'close')],
    'SZCI': [('a_share_indices', '399001.SZ', 'close')],
    'CHINEXT': [('a_share_indices', '399006.SZ', 'close')],
    'HSI': [('hk_indices', '^HSI', 'close')],
    'HSCEI': [('hk_indices', '^HSCE', 'close')],
    'HSAHP': [('ah_premium', 'close')],
    'SB_FLOW': [('southbound', 'south_money')],   # 引擎 L357-363: net_buy 优先,
    #              当前采集器只写 south_money(东财/akshare通道),故按实际写侧面取该键
    'MARGIN_BAL': [('margin', 'balance')],        # 引擎 L364-366 期望 balance;
    #              采集器成功路径只写 rzye/rqye/rzye_billion(china_market_collector L314-319)
    'SH_PE': [('valuation', 'pe')],               # 引擎 L367-369 期望扁平 pe;
    #              采集器写 valuation[代码].pe_ttm 嵌套(L344-351),且身份清单无 000001.SH(L88-92)
    'SH_AMOUNT': [('turnover', 'sh_amount_billion')],
    'SZ_COMPONENT_AMOUNT': [('turnover', 'sz_amount_billion')],
    'CN_TOTAL_TURNOVER': [('turnover', 'sh_amount_billion'),
                          ('turnover', 'sz_amount_billion')],
}
CN_TOTAL_FALLBACK = ('turnover', 'total_amount_billion')

# ── margin/valuation 采集端成功路径键(供 B 层机械对照;采集器 L314-319/L344-351) ──
MARGIN_COLLECTOR_KEYS = ['rzye', 'rqye', 'rzye_billion']
VALUATION_PROBE = {'container_keys': True, 'nested_fields': ['pe_ttm', 'pb']}

# ── 派生指标依赖(fact_engine L462-500 compute_derived) ──
DERIVED_DEPS = {
    'REAL_10Y': ['UST_10Y', 'BEI_10Y'],
    'REAL_5Y': ['UST_5Y', 'BEI_5Y'],
    'HY_IG_DIFF': ['HY_OAS', 'IG_OAS'],
    'ZQ_IMPLIED_AVG': ['ZQ_F1_PRICE'],
    'NFP_MOM_K': ['NFP'],      # 引擎 L490-499: 需 NFP 事实的 derived.m1(序列驱动)
}

# 机械状态集(报告层据此+代码侧证据映射 N/S/B/C/U,见 DELIVERY §分类规则)
STATES = ('PRESENT', 'PRESENT_NULL', 'PATH_NULL', 'KEY_ABSENT',
          'FILE_ABSENT', 'DERIVED_READY', 'DERIVED_BLOCKED', 'MAPPING_UNRESOLVED')


def _utcnow():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def _typename(v):
    return type(v).__name__


def _load_json_readonly(path, what):
    if not os.path.isfile(path):
        _fail('%s 不存在: %s' % (what, path))
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (ValueError, OSError) as e:
        _fail('%s JSON 解析失败: %s (%s)' % (what, path, e))


def _fail(msg):
    sys.stderr.write('[metric_coverage_audit] 输入异常: %s\n' % msg)
    sys.exit(2)


# ── 窗口扫描 ────────────────────────────────────────────────────────

def scan_window(data_dir):
    """收集窗口内通道文件(只读),按通道按日期升序。返回 {channel: [fileinfo]}。"""
    if not os.path.isdir(data_dir):
        _fail('数据目录不存在: %s' % data_dir)
    by_channel = {ch: [] for ch in CHANNEL_PATTERNS}
    ignored = []
    for name in sorted(os.listdir(data_dir)):
        p = os.path.join(data_dir, name)
        if not os.path.isfile(p):
            continue
        hit = None
        for ch, pat in CHANNEL_PATTERNS.items():
            m = pat.match(name)
            if m:
                hit = (ch, m.group(1))
                break
        if hit is None:
            if name.endswith('.json'):
                ignored.append(name)   # 非通道命名的 json(如未来新面)如实登记不解释
            continue
        ch, ymd = hit
        by_channel[ch].append({
            'file': name, 'date': ymd, 'path': p,
            'sha256': _sha256_file(p), 'size_bytes': os.path.getsize(p),
            'doc': _load_json_readonly(p, '通道文件 %s' % name),
        })
    for ch in by_channel:
        by_channel[ch].sort(key=lambda x: x['date'])
    return by_channel, sorted(ignored)


# ── 路径探测(机械事实核心) ─────────────────────────────────────────

def probe_path(doc, path):
    """在已加载 JSON 文档内沿 path(键序列)下行。返回 (state, value, stop)。
    state ∈ PRESENT / PRESENT_NULL / PATH_NULL / KEY_ABSENT:
      PRESENT       叶键在且值非 null
      PRESENT_NULL  叶键在但值为 null
      PATH_NULL     途中某节点为 JSON null(引擎路径不可达,如 margin:null)
      KEY_ABSENT    途中某容器存在(非 null)但下一键缺席(如 valuation:{} 无 'pe')
    """
    node = doc
    for i, key in enumerate(path):
        if node is None:
            return ('PATH_NULL', None, path[i - 1] if i else None)
        if not isinstance(node, dict):
            return ('PATH_NULL', None, key)   # 非字典节点=结构不一致,按不可达登记
        if key not in node:
            return ('KEY_ABSENT', None, key)
        node = node[key]
    if node is None:
        return ('PRESENT_NULL', None, path[-1])
    return ('PRESENT', node, path[-1])


def _obs_date(container, leaf_key):
    """从取值所在子字典尽量提取观测日(仅登记事实,不作判定)。"""
    if isinstance(container, dict):
        for k in ('date',):
            if k in container and isinstance(container[k], (str, int)):
                return str(container[k])
    return None


def probe_direct(doc, channel, metric_id):
    """按通道映射探测一个直接指标的机械事实。"""
    if channel == 'global':
        key = GLOBAL_FILE_KEY.get(metric_id, metric_id)
        path = ['data', key, 'close']
        st, val, stop = probe_path(doc, path)
        item = None
        if isinstance(doc, dict) and isinstance(doc.get('data'), dict) \
                and isinstance(doc['data'].get(key), dict):
            item = doc['data'][key]
        return {'state': st, 'value': val, 'path': path, 'absent_key': stop,
                'observation_date': _obs_date(item, 'close'),
                'value_type': _typename(val)}
    if channel == 'macro':
        key = MACRO_FILE_KEY.get(metric_id, metric_id)
        path = ['data', key, 'value']
        st, val, stop = probe_path(doc, path)
        item = None
        if isinstance(doc, dict) and isinstance(doc.get('data'), dict) \
                and isinstance(doc['data'].get(key), dict):
            item = doc['data'][key]
        series_len = None
        if isinstance(item, dict) and isinstance(item.get('series'), dict):
            series_len = len(item['series'].get('values') or [])
        return {'state': st, 'value': val, 'path': path, 'absent_key': stop,
                'observation_date': _obs_date(item, 'value'),
                'value_type': _typename(val), 'series_len': series_len}
    if channel == 'rate_economy':
        if metric_id in ('DFF', 'DFEDTARU', 'DFEDTARL'):
            path = ['current_rates', metric_id, 'value']
            st, val, stop = probe_path(doc, path)
            item = None
            if isinstance(doc, dict) and isinstance(doc.get('current_rates'), dict) \
                    and isinstance(doc['current_rates'].get(metric_id), dict):
                item = doc['current_rates'][metric_id]
            return {'state': st, 'value': val, 'path': path, 'absent_key': stop,
                    'observation_date': _obs_date(item, 'value'),
                    'value_type': _typename(val)}
        if metric_id == 'ZQ_F1_PRICE':
            rows = doc.get('fed_funds_futures') if isinstance(doc, dict) else None
            if rows is None:
                return {'state': 'PATH_NULL' if 'fed_funds_futures' in (doc or {})
                        else 'KEY_ABSENT', 'value': None,
                        'path': ['fed_funds_futures[ticker=ZQ=F]', 'price'],
                        'absent_key': 'fed_funds_futures',
                        'observation_date': None, 'value_type': 'NoneType'}
            if not isinstance(rows, list):
                return {'state': 'PATH_NULL', 'value': None,
                        'path': ['fed_funds_futures[ticker=ZQ=F]', 'price'],
                        'absent_key': 'fed_funds_futures', 'observation_date': None,
                        'value_type': 'NoneType'}
            row = next((r for r in rows
                        if isinstance(r, dict) and r.get('ticker') == 'ZQ=F'), None)
            if row is None:
                return {'state': 'KEY_ABSENT', 'value': None,
                        'path': ['fed_funds_futures[ticker=ZQ=F]', 'price'],
                        'absent_key': 'ZQ=F', 'observation_date': None,
                        'value_type': 'NoneType'}
            if 'price' not in row:
                return {'state': 'KEY_ABSENT', 'value': None,
                        'path': ['fed_funds_futures[ticker=ZQ=F]', 'price'],
                        'absent_key': 'price', 'observation_date': None,
                        'value_type': 'NoneType'}
            v = row['price']
            st = 'PRESENT_NULL' if v is None else 'PRESENT'
            return {'state': st, 'value': v,
                    'path': ['fed_funds_futures[ticker=ZQ=F]', 'price'],
                    'absent_key': None, 'observation_date': _obs_date(row, 'price'),
                    'value_type': _typename(v)}
        return None
    if channel == 'china':
        spec = CHINA_PATHS.get(metric_id)
        if spec is None:
            return None
        if metric_id == 'CN_TOTAL_TURNOVER':
            probes = []
            for path in spec:
                st, val, stop = probe_path(doc, path)
                probes.append((st, val, path, stop))
            if all(st == 'PRESENT' for st, _, _, _ in probes):
                vals = [v for _, v, _, _ in probes]
                return {'state': 'PRESENT',
                        'value': round(sum(float(v) for v in vals), 2),
                        'path': [list(p) for p in spec], 'absent_key': None,
                        'observation_date': _obs_date(doc.get('turnover')
                                                      if isinstance(doc, dict) else None, None),
                        'value_type': 'float', 'calc': 'sh_amount_billion+sz_amount_billion'}
            fb_st, fb_val, fb_stop = probe_path(doc, CN_TOTAL_FALLBACK)
            if fb_st == 'PRESENT':
                return {'state': 'PRESENT', 'value': fb_val,
                        'path': [list(CN_TOTAL_FALLBACK)], 'absent_key': None,
                        'observation_date': _obs_date(
                            doc.get('turnover') if isinstance(doc, dict) else None, None),
                        'value_type': _typename(fb_val),
                        'calc': 'akshare降级: total_amount_billion(仅沪市)'}
            # 聚合最差状态(PATH_NULL 优先于 KEY_ABSENT:容器null=面在值未取得)
            order = {'PRESENT': 0, 'PRESENT_NULL': 1, 'PATH_NULL': 2, 'KEY_ABSENT': 3}
            worst = max(probes, key=lambda t: order[t[0]])
            return {'state': worst[0], 'value': None,
                    'path': [list(p) for p in spec], 'absent_key': worst[3],
                    'observation_date': None, 'value_type': 'NoneType'}
        path = list(spec[0])
        st, val, stop = probe_path(doc, path)
        out = {'state': st, 'value': val, 'path': path, 'absent_key': stop,
               'value_type': _typename(val)}
        # 观测日: 尝试取叶键所在子字典
        node = doc
        for k in path[:-1]:
            node = node.get(k) if isinstance(node, dict) else None
            if node is None:
                break
        out['observation_date'] = _obs_date(node, path[-1]) if isinstance(node, dict) else None
        # B 层机械对照探针
        if metric_id == 'MARGIN_BAL' and isinstance(doc, dict):
            mg = doc.get('margin')
            out['collector_success_keys'] = (
                {k: (mg.get(k) is not None) for k in MARGIN_COLLECTOR_KEYS}
                if isinstance(mg, dict) else
                {'container': _typename(mg)})
        if metric_id == 'SH_PE' and isinstance(doc, dict):
            val_cont = doc.get('valuation')
            if isinstance(val_cont, dict):
                out['collector_side_codes'] = {
                    'container_keys': sorted(val_cont.keys()),
                    'has_000001SH': '000001.SH' in val_cont,
                    'pe_ttm_values': {k: v.get('pe_ttm')
                                      for k, v in val_cont.items()
                                      if isinstance(v, dict) and 'pe_ttm' in v},
                }
            else:
                out['collector_side_codes'] = {'container': _typename(val_cont)}
        return out
    return None


def channel_of(source, source_symbol):
    """registry source/source_symbol → (通道, 映射种类)。"""
    if source == 'global_market_collector':
        return 'global', 'direct'
    if source == 'macro_collector':
        if 'derived' in str(source_symbol):
            return 'macro', 'dependency'
        return 'macro', 'direct'
    if source == 'macro_collector(derived)':
        return 'macro', 'macro_derived_dict'
    if source == 'rate_expectations':
        return 'rate_economy', 'direct'
    if source == 'china_market_collector':
        return 'china', 'direct'
    if source == 'fact_engine(derived)':
        return None, 'dependency'
    return None, None


def build_audit(registry_path, data_dir):
    reg = _load_json_readonly(registry_path, 'registry')
    if not isinstance(reg, dict) or not isinstance(reg.get('metrics'), list):
        _fail('registry 结构非法: 缺 metrics 数组 (%s)' % registry_path)
    by_channel, ignored = scan_window(data_dir)

    metrics = []
    for m in reg['metrics']:
        if not isinstance(m, dict) or not m.get('metric_id'):
            _fail('registry 含无 metric_id 的非法条目')
        metrics.append(m)

    records = []
    for m in metrics:
        mid = m['metric_id']
        source = m.get('source', '')
        sym = m.get('source_symbol', '')
        channel, kind = channel_of(source, sym)
        rec = {
            'metric_id': mid,
            'registry_status': m.get('status'),
            'source': source,
            'source_symbol': sym,
            'frequency': m.get('frequency'),
            'criticality': m.get('criticality'),
        }
        if kind is None:
            rec.update({'mapping_kind': 'unresolved',
                        'state': 'MAPPING_UNRESOLVED',
                        'reason': 'registry source 未登记映射规则: %r' % source})
            records.append(rec)
            continue
        if kind == 'macro_derived_dict':
            files = by_channel['macro']
            rec['mapping_kind'] = 'macro_derived_dict'
            rec['path'] = ['derived', mid]
            if not files:
                rec['state'] = 'FILE_ABSENT'
                rec['files'] = []
            else:
                per = []
                for fi in files:
                    st, val, stop = probe_path(fi['doc'], ['derived', mid])
                    per.append({'file': fi['file'], 'date': fi['date'],
                                'sha256': fi['sha256'], 'state': st,
                                'value': val, 'absent_key': stop})
                newest = per[-1]
                rec['state'] = newest['state']
                rec['value'] = newest.get('value')
                rec['files'] = per
            records.append(rec)
            continue
        if kind == 'dependency':
            deps = DERIVED_DEPS.get(mid)
            if deps is None:
                rec.update({'mapping_kind': 'dependency',
                            'state': 'MAPPING_UNRESOLVED',
                            'reason': '派生依赖表无 %s(引擎 compute_derived 亦不产该指标)' % mid})
                records.append(rec)
                continue
            rec['mapping_kind'] = 'dependency'
            rec['deps'] = deps
            dep_states = {}
            for d in deps:
                dr = next((r for r in records if r['metric_id'] == d), None)
                dep_states[d] = dr['state'] if dr else 'MAPPING_UNRESOLVED'
            rec['dep_states'] = dep_states
            if all(s == 'PRESENT' for s in dep_states.values()):
                rec['state'] = 'DERIVED_READY'
            elif any(s in ('FILE_ABSENT', 'MAPPING_UNRESOLVED') for s in dep_states.values()):
                rec['state'] = 'DERIVED_BLOCKED'
            else:
                rec['state'] = 'DERIVED_BLOCKED'
            # NFP_MOM_K 序列面附加事实(引擎需 NFP.derived.m1,序列驱动)
            if mid == 'NFP_MOM_K':
                nfp_rec = next((r for r in records if r['metric_id'] == 'NFP'), None)
                if nfp_rec and nfp_rec.get('files'):
                    rec['dep_series_len_latest'] = nfp_rec['files'][-1].get('series_len')
            records.append(rec)
            continue
        # direct
        files = by_channel[channel]
        rec['mapping_kind'] = 'direct'
        rec['channel'] = channel
        if not files:
            rec['state'] = 'FILE_ABSENT'
            rec['files'] = []
            records.append(rec)
            continue
        per = []
        for fi in files:
            fact = probe_direct(fi['doc'], channel, mid)
            entry = {'file': fi['file'], 'date': fi['date'], 'sha256': fi['sha256'],
                     'state': fact['state']}
            if fact['state'] == 'PRESENT':
                entry['value'] = fact['value']
                entry['value_type'] = fact['value_type']
            if fact.get('observation_date') is not None:
                entry['observation_date'] = fact['observation_date']
            if fact.get('absent_key') is not None:
                entry['absent_key'] = fact['absent_key']
            if fact.get('series_len') is not None:
                entry['series_len'] = fact['series_len']
            for extra_key in ('collector_success_keys', 'collector_side_codes', 'calc'):
                if extra_key in fact:
                    entry[extra_key] = fact[extra_key]
            per.append(entry)
        newest = per[-1]
        rec['state'] = newest['state']
        if newest['state'] == 'PRESENT':
            rec['value'] = newest.get('value')
            rec['value_type'] = newest.get('value_type')
            rec['observation_date'] = newest.get('observation_date')
        if 'calc' in newest:
            rec['calc'] = newest['calc']
        if 'collector_success_keys' in newest:
            rec['collector_success_keys'] = newest['collector_success_keys']
        if 'collector_side_codes' in newest:
            rec['collector_side_codes'] = newest['collector_side_codes']
        rec['files'] = per
        records.append(rec)

    state_counts = {}
    for r in records:
        state_counts[r['state']] = state_counts.get(r['state'], 0) + 1
    by_state_by_channel = {}
    for r in records:
        ch = r.get('channel') or ('(derived)' if r.get('mapping_kind') == 'dependency'
                                  else r.get('mapping_kind', '?'))
        by_state_by_channel.setdefault(ch, {}).setdefault(r['state'], 0)
        by_state_by_channel[ch][r['state']] += 1

    report = {
        'schema_version': SCHEMA_VERSION,
        'generated_utc': _utcnow(),
        'tool': 'scripts/metric_coverage_audit.py (IA-DATA-W2, 只读)',
        'registry': {
            'path': registry_path,
            'sha256': _sha256_file(registry_path),
            'version': reg.get('version'),
            'metric_count': len(metrics),
            'status_counts': _count(metrics, 'status'),
        },
        'data_dir': data_dir,
        'window': {
            'files_total': sum(len(v) for v in by_channel.values()),
            'by_channel': {ch: [{'file': f['file'], 'date': f['date'],
                                 'sha256': f['sha256'], 'size_bytes': f['size_bytes']}
                                for f in fl]
                           for ch, fl in by_channel.items()},
            'ignored_nonchannel_json': ignored,
        },
        'metrics': records,
        'summary': {
            'state_counts': state_counts,
            'by_channel': by_state_by_channel,
            'non_present': [r['metric_id'] for r in records if r['state'] != 'PRESENT'
                            and r['state'] != 'DERIVED_READY'],
        },
    }
    return report


def _count(items, key):
    out = {}
    for it in items:
        k = it.get(key) if isinstance(it, dict) else None
        out[k] = out.get(k, 0) + 1
    return out


def main(argv=None):
    # --registry/--data-dir 为必选(不设仓库内默认路径: 工具不隐式触碰任何真实
    # 数据面,调用方显式授权输入;缺参=argparse报错退出码2,语义见DELIVERY§用法)
    ap = argparse.ArgumentParser(
        description='指标覆盖审计(只读): registry 全部指标 × 数据目录逐指标机械覆盖事实')
    ap.add_argument('--registry', required=True,
                    help='registry 路径(如 config/metric_registry.json)')
    ap.add_argument('--data-dir', required=True,
                    help='数据目录(如 data/daily;审计窗口=目录内全部通道 *.json)')
    ap.add_argument('--out', default=None, help='报告输出路径(缺省打印 stdout)')
    args = ap.parse_args(argv)

    report = build_audit(args.registry, args.data_dir)
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        with open(args.out, 'w', encoding='utf-8') as f:
            f.write(text + '\n')
        sys.stderr.write('[metric_coverage_audit] 报告已写出: %s (指标 %d, 窗口文件 %d)\n'
                         % (args.out, report['registry']['metric_count'],
                            report['window']['files_total']))
    else:
        print(text)
    return 0


if __name__ == '__main__':
    sys.exit(main())
