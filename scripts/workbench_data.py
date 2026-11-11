#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""研究工作台数据层(W5, 2026-11-08)——纯加载/格式化函数,零 streamlit 依赖。

为 app.py(本地Web工作台)与 tests/test_oss_workbench.py 提供四个页面的数据面:
  全球宏观概览  overview_rows()   —— 快照 facts × 注册表(经济体分组,缺失如实标注)
  金融市场变化  market_rows()     —— 资产类指标 周/月/年内变化
  历史研究      metric_series()   —— 本地真实历史序列(快照 series_store / 采集档 series)
  AI研究        ask_local() / ai_explain() / save_to_archive()
                                 —— 复用 e2eb 查询栈 / model_conclusion_client / research_archive

数据纪律(章程 AC-06): 一切数值来自本地快照与采集档,显示观测日期与来源;
数据缺失时如实标注"缺失",不填充任何虚构数据。研究问题越界(out_of_scope)或
未支持(no_registry_identity/unmapped)时如实返回状态,不猜映射。
重模块(yfinance/e2eb栈)一律函数内惰性导入,保证本模块导入零副作用、轻环境可用。
"""
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.dirname(os.path.abspath(__file__))

ECONOMY_LABELS = {'US': '美国', 'CN': '中国', 'EA': '欧元区', 'JP': '日本',
                  'GLOBAL': '全球', 'HK': '中国香港'}
# 金融市场变化页纳入的资产类(注册表 asset_class 权威口径)
MARKET_ASSET_CLASSES = {
    'equity_index', 'single_stock', 'country_etf_proxy', 'bond_etf',
    'fx_rate', 'fx_index', 'commodity_futures', 'spot_commodity_etf',
    'commodity_futures_etf', 'crypto', 'volatility_index', 'credit_spread',
}
# metric_series 支持的采集档前缀(注册表 source → data/daily 文件前缀;
# japan_rate_collector 为单点无序列,research_history_query 明确不支持)
SERIES_SOURCE_PREFIX = {
    'global_market_collector': 'global_',
    'macro_collector': 'macro_',
    'china_market_collector': 'china_',
    'rate_expectations': 'rate_economy_',
    'jp_market_collector': 'jp_',
    'ea_market_collector': 'ea_',
    'shiller_collector': 'shiller_',   # Charter6-P2: Shiller 估值通道
}

# Charter9 P0-4(C席附加发现): 市场多窗口表原按 MARKET_ASSET_CLASSES 过滤,
# rates_yield/policy_rate/curve_slope 不在集合 → UST/BUND/JGB/2s10s 在
# 多窗口表零显示,"美债 3m 变化"无处可答。纳入利率族(多窗口表专用;
# 页二"金融市场变化"的资产类口径不变)。
RATES_ASSET_CLASSES = {'rates_yield', 'policy_rate', 'curve_slope'}


# ══ 快照与注册表 ══════════════════════════════════════════════════════
def latest_snapshot(root=None):
    """最新研究快照(修订版感知): 返回 (snapshot_dict|None, path或原因)."""
    daily = os.path.join(root or ROOT, 'data', 'daily')
    cands = sorted(glob.glob(os.path.join(daily, 'research_snapshot_*.json')))
    if not cands:
        return None, '本地无研究快照(data/daily/research_snapshot_*.json)——请先运行 python3 run_weekly.py'
    ymd = os.path.basename(cands[-1]).replace('research_snapshot_', '').split('_v')[0][:8]
    import research_provenance as rp
    snap, path_or_reason = rp.select_snapshot(ymd, daily)
    return snap, (path_or_reason if snap else path_or_reason)


def load_registry(root=None):
    """指标注册表(单一权威): 返回 {'metrics': list, 'by_id': {id: metric}}."""
    path = os.path.join(root or ROOT, 'config', 'metric_registry.json')
    with open(path, encoding='utf-8') as f:
        metrics = json.load(f)['metrics']
    return {'metrics': metrics, 'by_id': {m['metric_id']: m for m in metrics}}


def snapshot_meta(snapshot):
    """快照元信息: 日期/Gate A/缺失与降级清单(诚实披露面)."""
    if not snapshot:
        return {'date': None, 'gate_a': '无快照', 'missing': [], 'degraded': [],
                'as_of': None}
    gate = snapshot.get('gate_a') or {}
    return {'date': snapshot.get('target_date'),
            'as_of': snapshot.get('research_as_of'),
            'gate_a': gate.get('status', 'UNKNOWN'),
            'missing': sorted(gate.get('noncore_missing', []) + gate.get('core_missing', [])),
            'degraded': sorted(gate.get('noncore_degraded', []))}


# ══ 格式化 ════════════════════════════════════════════════════════════
def fmt_value(value, unit=''):
    if value is None:
        return '缺失'
    try:
        v = float(value)
    except (TypeError, ValueError):
        return f"{value}" + (f' {unit}' if unit else '')
    if abs(v) >= 1000:          # 千位分隔,不用科学计数法
        s = f"{v:,.0f}"
    elif abs(v) >= 100:
        s = f"{v:,.1f}"
    elif abs(v) >= 1:
        s = f"{v:,.2f}"
    else:
        s = f"{v:,.4f}"
    return s + (f' {unit}' if unit else '')


def fmt_change(derived, key):
    """derived[key] = {pct_change|pp_change|bp_change, ...} → 人读变化串;无则'—'."""
    node = (derived or {}).get(key) if isinstance(derived, dict) else None
    if not isinstance(node, dict):
        return '—'
    if node.get('pct_change') is not None:
        return f"{node['pct_change']:+.2f}%"
    if node.get('pp_change') is not None:
        return f"{node['pp_change']:+.2f}pp"
    if node.get('bp_change') is not None:
        return f"{node['bp_change']:+.0f}bp"
    return '—'


def _fact_rows(snapshot, registry, wanted):
    """注册表口径 wanted(metric列表) × 快照 facts → 概览行(缺失行如实生成)."""
    facts = {f['metric_id']: f for f in (snapshot or {}).get('facts', [])}
    gate = (snapshot or {}).get('gate_a') or {}
    miss_detail = gate.get('noncore_missing_detail', {})
    rows = []
    for m in wanted:
        f = facts.get(m['metric_id'])
        if f is None:
            note = miss_detail.get(m['metric_id'], '快照中无该指标事实')
            rows.append({'指标': m['display_name'], '当前值': '缺失',
                         '观测日期': '—', '周变化': '—', '月变化': '—',
                         '年内变化': '—', '数据质量': '缺失',
                         '来源': f"{m.get('source', '—')} · {note}"})
            continue
        quality = f.get('quality_status', 'unknown')
        if f.get('issues'):
            quality = f"{quality}({len(f['issues'])}项提示)"
        src = f.get('source') or {}
        rows.append({'指标': f.get('display_name') or m['display_name'],
                     '当前值': fmt_value(f.get('value'), f.get('unit')),
                     '观测日期': f.get('observation_date', '—'),
                     '周变化': fmt_change(f.get('derived'), 'week'),
                     '月变化': fmt_change(f.get('derived'), 'mtd'),
                     '年内变化': fmt_change(f.get('derived'), 'ytd'),
                     '数据质量': quality,
                     '来源': src.get('collector') or m.get('source', '—')})
    return rows


def overview_rows(snapshot, registry, economy):
    """页面一: 全球宏观概览(单经济体行集; economy∈US/CN/EA/JP/GLOBAL/HK)."""
    wanted = [m for m in registry['metrics']
              if m.get('economy') == economy and m.get('status') == 'active']
    return _fact_rows(snapshot, registry, wanted)


def market_rows(snapshot, registry):
    """页面二: 金融市场变化(资产类指标; 缺失资产在末尾'缺失'行如实列出)."""
    wanted = [m for m in registry['metrics']
              if m.get('asset_class') in MARKET_ASSET_CLASSES
              and m.get('status') == 'active']
    rows = _fact_rows(snapshot, registry, wanted)
    return rows


# ══ Charter8 研究地图面(2026-11-10) ═══════════════════════════════════
# 窗口区间变动的**唯一实现**在此(纯函数层): app 页①与 scripts/view_verifier
# 共用,防口径分叉。区间计算一律 research_history_query.interval_change——
# 与 ia_cli compare 自配对(P2-2 正式口径)同一函数同一条 common window 规则。
WINDOW_HORIZONS = ('1m', '3m', '1y', '5y')

_MONTH_DAYS = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


def _month_shift(d, months):
    """自然月平移(2026-03-31 −1月→2026-02-28,近端语义)。"""
    import datetime as _dt
    y, mo = d.year, d.month - months
    while mo <= 0:
        mo += 12
        y -= 1
    leap = (y % 4 == 0 and y % 100 != 0) or y % 400 == 0
    day = min(d.day, 29 if (mo == 2 and leap) else _MONTH_DAYS[mo - 1])
    return _dt.date(y, mo, day)


def horizon_start(target_ymd, horizon):
    """窗口起点(target_ymd=YYYYMMDD 或 ISO): Nm 自然月回退,Ny 年回退
    (N 任意正整数——Charter9 P0-3 复算对账需 3yr 边窗,通用化同语义:
    年回退=同月同日,2-29→2-28 钳制;月回退=月末钳制)。"""
    import datetime as _dt
    import re as _re
    s = str(target_ymd)
    d = _dt.date(int(s[:4]), int(s[4:6]) if len(s) == 8 else int(s[5:7]),
                 int(s[6:8]) if len(s) == 8 else int(s[8:10]))
    m = _re.fullmatch(r'(\d+)m', str(horizon))
    if m:
        return _month_shift(d, int(m.group(1))).isoformat()
    m = _re.fullmatch(r'(\d+)y', str(horizon))
    if m:
        years = int(m.group(1))
        day = min(d.day, 28) if (d.month == 2 and d.day == 29) else d.day
        return _dt.date(d.year - years, d.month, day).isoformat()
    raise ValueError(f'未知窗口 {horizon!r}(合法: Nm/Ny 如 1m/3m/6m/1y/3y/5y)')


def metric_window_changes(metric_id, snapshot, unit, target_ymd,
                          horizons=WINDOW_HORIZONS, root=None):
    """单指标多窗口区间变动 → (changes, series_source)。

    序列经 metric_series: 快照 series_store 优先→采集档回落(同一条取数
    路径);两级都无→全窗 available=False+原因(不猜)。采集档标准化层的
    进度打印与本指标无关→捕获丢弃,调用方输出保持单 JSON/单页面契约。"""
    import io
    from contextlib import redirect_stdout
    import research_history_query as rhq
    out = {}
    with redirect_stdout(io.StringIO()):
        series, reason = metric_series(metric_id, snapshot=snapshot,
                                       root=root or ROOT)
    if series is None or not series.get('dates'):
        return ({h: {'available': False, 'reason': reason or '无观测序列'}
                 for h in horizons}, None)
    for h in horizons:
        out[h] = rhq.interval_change(series['dates'], series['values'], unit,
                                     start=horizon_start(target_ymd, h),
                                     end=str(target_ymd))
    return out, series.get('source')


def _fmt_interval(node):
    """区间变动节点 → 展示串('+12.43%' / '+0.31pp' / '±N' / '不可用(原因)')。

    interval_change 契约: 成功节点不带 available 键(带变化值),失败节点
    available=False+reason——判可用=键缺席或非 False。"""
    if not isinstance(node, dict) or node.get('available') is False:
        reason = (node or {}).get('reason', '数据不足')
        return f'不可用({str(reason)[:24]})'
    for key, suffix in (('pp_change', 'pp'), ('pct_change', '%'),
                        ('abs_change', '')):
        if node.get(key) is not None:
            sign = '+' if node[key] > 0 else ''
            return f'{sign}{node[key]:.2f}{suffix}'
    return '不可用(无变化值)'


def market_window_rows(snapshot, registry, root=None, horizons=WINDOW_HORIZONS,
                       include_rates=True):
    """Charter8 页①市场窗口表: 资产类+利率族指标 当前值+1m/3m/1y/5y 区间变动。

    Charter9 P0-4: include_rates=True(缺省)纳入 RATES_ASSET_CLASSES
    (rates_yield/policy_rate/curve_slope)——UST/BUND/JGB/2s10s 的 3m/1y
    变化在此表可答(C席附加发现修复);页二"金融市场变化"口径不动。

    每行: 指标/ID/经济体/当前值/观测日 + 各窗口(fmt) + 序列来源;
    缺失指标如实'缺失'行(不猜序列);全部口径=metric_window_changes。"""
    if not snapshot:
        return []
    target = snapshot.get('target_date')
    facts = {f['metric_id']: f for f in snapshot.get('facts', [])}
    classes = MARKET_ASSET_CLASSES | (RATES_ASSET_CLASSES if include_rates else set())
    wanted = [m for m in registry['metrics']
              if m.get('asset_class') in classes
              and m.get('status') == 'active']
    rows = []
    for m in wanted:
        mid = m['metric_id']
        f = facts.get(mid)
        if f is None:
            rows.append({'指标': m['display_name'], 'ID': mid,
                         '经济体': m.get('economy', '—'), '当前值': '缺失',
                         '观测日期': '—',
                         **{f'{h}变化': '缺失' for h in horizons},
                         '序列来源': '—'})
            continue
        unit = f.get('unit') or m.get('unit', '')
        chg, src = metric_window_changes(mid, snapshot, unit, target,
                                         horizons=horizons, root=root)
        rows.append({'指标': f.get('display_name') or m['display_name'],
                     'ID': mid, '经济体': m.get('economy', '—'),
                     '当前值': fmt_value(f.get('value'), unit),
                     '观测日期': f.get('observation_date', '—'),
                     **{f'{h}变化': _fmt_interval(chg.get(h)) for h in horizons},
                     '序列来源': src or '—'})
    return rows


def economy_dimension_matrix(snapshot, registry):
    """Charter8 页①经济体×维度覆盖表: 行=经济体,列=资产类维度,
    单元格=在场/活跃(如 '12/13';无活跃指标维度='—')。

    覆盖=活跃注册数与快照在场事实数之比——覆盖缺口如实呈现,不放大。"""
    econs, acs = [], []
    for m in registry['metrics']:
        if m.get('status') != 'active':
            continue
        if m.get('economy') not in econs:
            econs.append(m.get('economy'))
        ac = m.get('asset_class')
        if ac and ac not in acs:
            acs.append(ac)
    facts = {f['metric_id'] for f in (snapshot or {}).get('facts', [])}
    cells, rows = {}, []
    for m in registry['metrics']:
        if m.get('status') != 'active' or not m.get('asset_class'):
            continue
        k = (m.get('economy'), m['asset_class'])
        a, p = cells.get(k, (0, 0))
        cells[k] = (a + 1, p + (1 if m['metric_id'] in facts else 0))
    for e in econs:
        row = {'经济体': f'{ECONOMY_LABELS.get(e, e)}({e})'}
        for ac in acs:
            a, p = cells.get((e, ac), (0, 0))
            row[ac] = f'{p}/{a}' if a else '—'
        rows.append(row)
    return {'rows': rows, 'asset_classes': acs,
            'note': '单元格=快照在场/注册活跃(指标数);覆盖缺口如实呈现'}


def transmission_edges(root=None, archive_dir=None):
    """Charter8 页②传导地图静态策划档(config/transmission_edges.json)。

    校验: 每条边必须带 qb_source(指向真实 QB 归档)——缺 qb_source 的
    任何边=策划纪律违规,raise ValueError(不静默装载)。
    Charter9 P0-3(C席实测: 伪号 QB-20990101-999 曾零拦截装载): 归档在场时
    qb_source 存在性核验(不在册即 raise);归档缺席(干净 clone, data/不入库)
    如实降级 archive_check.performed=False——禁静默通过也禁 CI 崩溃。
    全量四状态核验(VERIFIED/PARTIAL/MISSING/CONFLICTED)+复算对账在
    scripts/source_verifier.py(装载面只做硬闸: 悬空引用不入页)。"""
    path = os.path.join(root or ROOT, 'config', 'transmission_edges.json')
    with open(path, encoding='utf-8') as f:
        doc = json.load(f)
    edges = doc.get('edges') or []
    bad = [e.get('edge_id', f'#{i}') for i, e in enumerate(edges)
           if not e.get('qb_source')]
    if bad:
        raise ValueError(f'传导边缺 qb_source(禁凭空策划): {bad}')
    import research_archive as ra
    check_dir = archive_dir or ra.DEFAULT_ARCHIVE_DIR
    cited = {e['qb_source'] for e in edges
             if not str(e['qb_source']).startswith('SYNTH:')}
    for f in doc.get('mechanism_findings') or []:
        if f.get('qb_source'):
            cited.add(f['qb_source'])
    ss = doc.get('structural_summary') or {}
    if ss.get('qb_source'):
        cited.add(ss['qb_source'])
    if not os.path.isdir(check_dir):
        doc['archive_check'] = {
            'performed': False,
            'note': ('研究归档目录不存在(干净clone/无归档环境)——qb_source 存在性'
                     '核验跳过;有归档环境运行 python3 scripts/source_verifier.py')}
        return doc
    known = set(ra.list_query_records(check_dir))
    dangling = sorted(cited - known)
    if dangling:
        raise ValueError(f'传导边 qb_source 指向不存在的研究档案(禁伪号入页): '
                         f'{dangling}')
    doc['archive_check'] = {
        'performed': True, 'n_records': len(known), 'checked_refs': sorted(cited)}
    return doc


def views_matrix(views_dir=None):
    """Charter8 页③机构观点矩阵: 只装载 linter 合规件(view_store)。

    返回 {'rows': 摘要行, 'matrix': 机构×主题单元格, 'subjects': 主题列,
    'n_quarantined': 隔离数, 'schema_version': '1.1'}——隔离件绝不入面。"""
    import view_store as vs
    res = vs.load_views(views_dir)
    subjects = list(vs.KNOWN_SUBJECTS)
    cells = {}
    for d in res['views']:
        name = d['institution']['name']
        for s in d['subjects']:
            cells.setdefault((name, s), []).append(d['view_id'][-3:])
    names = sorted({d['institution']['name'] for d in res['views']})
    matrix = [{'机构': n,
               **{s: ','.join(cells.get((n, s), [])) or '—' for s in subjects}}
              for n in names]
    rows = [{'view_id': d['view_id'], '机构': d['institution']['name'],
             '类型': d['institution']['type'], '发布日': d['publish_date'],
             '期限': d['view_horizon'], '主题': '、'.join(d['subjects']),
             '核心观点数': len(d['core_views']), '标题': d['report_title']}
            for d in res['views']]
    return {'rows': rows, 'matrix': matrix, 'subjects': subjects,
            'n_quarantined': len(res['quarantined']),
            'quarantined': res['quarantined'],
            'schema_version': vs.SCHEMA_VERSION}


# ══ Charter9 P0-4: 历史走势图层日历窗口与族感知 caption(纯函数) ════════
CHART_WINDOW_HORIZON = {'5年': '5y', '1年': '1y', '6个月': '6m',
                        '3个月': '3m', '1个月': '1m'}


def slice_series_window(dates, values, label, end_date=None):
    """历史走势图窗切片(Charter9 P0-4 修复: 固定观测数→日历日期截取)。

    旧缺陷: 切片=尾部 N 个观测(252/126/63/21,日频假设)——月频序列选
    "1年"实显 21 年(C席 CONFIRMED)。新口径: 窗起点=horizon_start(末观测日,
    label 对应窗口)同一实现(自然月/年),dates≥起点 全保留(零频率假设)。
    '全部'→原样;end_date 缺省=序列末观测日。返回 (dates, values, note)。"""
    if label == '全部' or not dates:
        return list(dates), list(values), '全部观测'
    import datetime as _dt
    ds = [str(d)[:10] for d in dates]
    anchor = str(end_date or ds[-1])[:10]
    start = horizon_start(anchor.replace('-', ''), CHART_WINDOW_HORIZON[label])
    keep = [i for i, d in enumerate(ds) if d >= start]
    if not keep:
        return [], [], f'窗口({label},{start}起)内无观测'
    out_d = [dates[i] for i in keep]
    out_v = [values[i] for i in keep]
    n_all = len(ds)
    note = (f'日历窗口 {start} → {ds[keep[-1]]}'
            f'({len(keep)}/{n_all} 观测,日期截取非定点数)')
    return out_d, out_v, note


def series_change_caption(unit, first, last):
    """序列首末变化 caption(Charter9 P0-4: 族感知,与窗口表口径一致)。

    旧缺陷: 一律 (末-首)/|首|×100% ——利率/失业率等显示水平百分变化
    (如失业率 4.7→4.1 显示 -12.77%)与窗口表 pp 约定不一致(C席 CONFIRMED)。
    新口径: rate 族→pp(fact_engine.RATE_UNITS 权威);price 族→pct
    (基准≤0 如实不可算);count/other→绝对差。返回 {'family','text'}。"""
    import fact_engine as fe
    try:
        a, b = float(first), float(last)
    except (TypeError, ValueError):
        return {'family': 'other', 'text': None}
    if unit in fe.RATE_UNITS:
        return {'family': 'rate',
                'text': f'窗口首值 {a:,.4g} → 末值 {b:,.4g}'
                        f'(区间变化 {b - a:+.2f}pp,利率口径)'}
    if unit in fe.PRICE_LIKE_UNITS:
        if a == 0:
            return {'family': 'price',
                    'text': f'窗口首值 {a:,.4g} → 末值 {b:,.4g}'
                            '(基准值为0,百分比变化不可定义)'}
        if a < 0:
            return {'family': 'price',
                    'text': f'窗口首值 {a:,.4g} → 末值 {b:,.4g}'
                            '(基准值为负,价格类百分比变化语义不可用)'}
        return {'family': 'price',
                'text': f'窗口首值 {a:,.4g} → 末值 {b:,.4g}'
                        f'(区间变化 {(b / a - 1.0) * 100.0:+.2f}%)'}
    return {'family': 'count',
            'text': f'窗口首值 {a:,.4g} → 末值 {b:,.4g}'
                    f'(区间变化 {b - a:+,.4g},绝对差)'}


# ══ Charter9 P3: 页④研究十问 + 页②边验证徽标(纯函数/读档,零模型) ═════
def research_questions(path=None):
    """config/research_questions.json: 章程§五研究十问(裁定⑤原文十条)。

    返回 {schema_version, n, layers, layer_note, questions, by_layer};
    校验(FAIL-LOUD): 恰 10 问、id RQ1..RQ10 连续、primary_layer 全在
    五层枚举、五层各至少一问、draws 不越枚举——config 受版本管理,
    破损=安装损坏非数据缺席。"""
    p = path or os.path.join(ROOT, 'config', 'research_questions.json')
    with open(p, encoding='utf-8') as f:
        cfg = json.load(f)
    layers = list(cfg.get('layers') or [])
    qs = cfg.get('questions') or []
    problems = []
    if len(qs) != 10:
        problems.append(f'须恰 10 问(当前 {len(qs)})')
    if [q.get('id') for q in qs] != [f'RQ{i}' for i in range(1, 11)]:
        problems.append('id 须为 RQ1..RQ10 连续')
    for q in qs:
        if q.get('primary_layer') not in layers:
            problems.append(f"{q.get('id')}.primary_layer 越五层枚举")
        for d in q.get('draws') or []:
            if d not in layers:
                problems.append(f"{q.get('id')}.draws 含越枚举层 {d!r}")
    if {q.get('primary_layer') for q in qs} != set(layers):
        problems.append('五层须各至少一问(primary_layer 覆盖)')
    if problems:
        raise ValueError('research_questions.json 破损: ' + '; '.join(problems))
    by_layer = {layer: [q['id'] for q in qs if q['primary_layer'] == layer]
                for layer in layers}
    return {'schema_version': cfg.get('schema_version'),
            'n': len(qs), 'layers': layers,
            'layer_note': cfg.get('layer_note'),
            'questions': qs, 'by_layer': by_layer}


def edge_verification_badge(qb_source, archive_dir=None):
    """页②行详情: 边的 qb_source → source_verifier 四状态徽标行(纯离线)。

    source_verifier 惰性 import(其复算面依赖本模块,顶层互引成环)。
    返回 {'qb_source', 'state', 'badge', 'detail'};state∈四状态,badge=
    展示文案(VERIFIED/PARTIAL/MISSING/CONFLICTED)。"""
    import source_verifier as svf
    r = svf.verify_qb_source(qb_source, archive_dir=archive_dir)
    badge = {'VERIFIED': '✅ 源已核验', 'PARTIAL': '⚠️ 部分核验',
             'MISSING': '❌ 悬空引用', 'CONFLICTED': '⛔ 状态冲突'}
    return {'qb_source': qb_source, 'state': r['state'],
            'badge': badge.get(r['state'], r['state']), 'detail': r['detail']}


def research_archive_rows(limit=50, archive_dir=None):
    """Charter8 页④独立研究结论: 本地研究档案行(QB 链)。

    每行: query_id/创建时间/问题摘要/follow_up 链/sidecar 在场(有则
    answer_text 摘要);零网络零模型,纯读归档。"""
    import research_archive as ra
    qids = ra.list_query_records(archive_dir=archive_dir)
    rows = []
    for qid in reversed(qids[-limit:]):        # 最新在前
        try:
            rec = ra.load_query_record(qid, archive_dir=archive_dir)
        except (OSError, ValueError, KeyError):
            rows.append({'query_id': qid, '创建时间': '—', '问题': '(读取失败)',
                         '关联前档': '—', '研究正文': '—'})
            continue
        ir = rec.get('ir') or {}
        question = str(ir.get('question_text') or '(无问题文本)')
        full = None
        try:
            full = ra.load_research_full(qid, archive_dir=archive_dir)
        except (OSError, ValueError):
            full = None
        at = (full or {}).get('answer_text') if full else None
        rows.append({'query_id': qid,
                     '创建时间': rec.get('created_at', '—'),
                     '问题': question[:80] + ('…' if len(question) > 80 else ''),
                     '关联前档': (full or rec).get('follow_up_of') or '—',
                     '研究正文': (at[:120] + '…') if at else '—'})
    return rows


# ══ 历史研究 ══════════════════════════════════════════════════════════
# supported_stats(问题二 C-2): 由 unit_family 机械推导的可用统计面——
# 描述可做什么,不是对数据的断言;other 族无可靠变化口径,只报 level。
SUPPORTED_STATS = {
    'price': ('level', 'interval_change(pct)', 'unit_aware_change(pct)',
              'pearson(单位感知变化)', 'rolling(单位感知变化)', 'lag(单位感知变化)'),
    'rate': ('level', 'interval_change(pp/bp)', 'unit_aware_change(pp)',
             'pearson(单位感知变化)', 'rolling(单位感知变化)', 'lag(单位感知变化)'),
    'count': ('level', 'interval_change(abs)', 'unit_aware_change(pct,基数大近似)',
              'pearson(单位感知变化)', 'rolling(单位感知变化)', 'lag(单位感知变化)'),
    'other': ('level',),
}


def series_capable_metrics(snapshot, registry):
    """历史研究页可选项+发现所需全字段(C-1, 批2 W8): 快照 series_store ∪
    采集档含 series 的指标。

    字段三层纯透传/纯统计,不推算:
    - 注册表透传: label/unit/frequency/calendar/release_semantics/
      time_semantics(observation_period_kind+release_date_available,
      A-fin 人工登记键,缺键=null 不默认);
    - 序列统计(first/last/n): series_store 优先,仅存采集档的取最新档
      series 原值(同旧版来源优先级,统计口径=该来源序列本身);
    - 口径族(unit_family, 单位感知比较预判用)+supported_stats(由
      unit_family 机械推导的可用统计面)与事实层 quality_status
      (快照 facts,无事实→null,如实标注不猜测)。
    """
    import fact_engine as fe        # 惰性: 单位族常量(重模块函数内导入纪律)
    facts_q = {f.get('metric_id'): f.get('quality_status')
               for f in (snapshot or {}).get('facts', [])}
    stats = {}
    for mid, s in ((snapshot or {}).get('series_store') or {}).items():
        dates = (s or {}).get('dates') or []
        if dates:
            stats[mid] = (dates[0], dates[-1], len(dates))
    daily = os.path.join(ROOT, 'data', 'daily')
    # Charter6-P2: +shiller_(估值序列月频;series 节直通)
    for prefix in ('macro_', 'global_', 'rate_economy_', 'shiller_'):
        files = sorted(glob.glob(os.path.join(daily, f'{prefix}*.json')))
        if not files:
            continue
        try:
            with open(files[-1], encoding='utf-8') as fh:
                doc = json.load(fh)
            data = doc.get('data') or {}
            if isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, dict) and isinstance(v.get('series'), dict) \
                            and v['series'].get('dates'):
                        if k not in stats:      # series_store 优先(快照口径)
                            dates = v['series']['dates']
                            stats[k] = (dates[0], dates[-1], len(dates))
        except (OSError, ValueError):
            continue
    out = []
    for mid in sorted(stats):
        m = registry['by_id'].get(mid) or {}
        unit = m.get('unit', '')
        fam = ('rate' if unit in fe.RATE_UNITS else
               'price' if unit in fe.PRICE_LIKE_UNITS else
               'count' if unit in fe.COUNT_UNITS else 'other')
        first, last, n = stats[mid]
        out.append({'metric_id': mid,
                    'label': m.get('display_name', mid),
                    'unit': unit, 'unit_family': fam,
                    'frequency': m.get('frequency'),
                    'first': first, 'last': last, 'n': n,
                    'calendar': m.get('calendar'),
                    'release_semantics': m.get('release_semantics'),
                    'time_semantics': {'observation_period_kind':
                                       m.get('observation_period_kind'),
                                       'release_date_available':
                                       m.get('release_date_available')},
                    'supported_stats': list(SUPPORTED_STATS[fam]),
                    'quality_status': facts_q.get(mid)})
    return out


def metric_series(metric_id, snapshot=None, root=None):
    """页面三: 本地真实历史序列。优先快照 series_store,否则按注册表 source
    找最新采集档走 research_history_query.load_metric_series。
    返回 {'metric_id','label','unit','dates','values','source'} 或 (None, 原因)。"""
    if isinstance(metric_id, dict):  # UI 下拉传入 option 对象时取其 id(2026-11-08 D验收回归)
        metric_id = metric_id.get('metric_id')
    registry = load_registry(root)
    m = registry['by_id'].get(metric_id)
    if m is None:
        return None, f'注册表无此指标: {metric_id}'
    if snapshot and metric_id in (snapshot.get('series_store') or {}):
        ss = snapshot['series_store'][metric_id]
        return {'metric_id': metric_id, 'label': m['display_name'],
                'unit': m.get('unit', ''), 'dates': list(ss['dates']),
                'values': list(ss['values']), 'source': '研究快照 series_store'}, None
    prefix = SERIES_SOURCE_PREFIX.get(m.get('source'))
    if prefix is None:
        return None, (f"该指标来源({m.get('source')})为单点观测,无历史序列——"
                      '工作台历史页暂不支持')
    files = sorted(glob.glob(os.path.join(root or ROOT, 'data', 'daily', f'{prefix}*.json')))
    if not files:
        return None, f'本地无 {prefix}* 采集档——请先运行 python3 run_weekly.py'
    ymd = os.path.basename(files[-1])[len(prefix):len(prefix) + 8]
    import research_history_query as rhq
    try:
        res = rhq.load_metric_series(metric_id, ymd, data_dir=os.path.dirname(files[-1]))
    except ValueError as e:
        return None, f'该指标无历史序列: {e}'
    dates, values = res.get('dates'), res.get('values')
    if not dates:
        return None, '序列为空'
    return {'metric_id': metric_id, 'label': res.get('display_name') or m['display_name'],
            'unit': res.get('unit') or m.get('unit', ''),
            'dates': list(dates), 'values': list(values),
            'source': f"采集档 {os.path.basename(res.get('source', {}).get('file', files[-1]))}"}, None


# ══ AI研究(复用 e2eb 查询栈 / 可选模型解释层 / 研究档案) ═══════════════
SUPPORTED_CONCEPT_HINT = (
    '当前支持的完整研究问题类型(基于本地快照事实作答):\n'
    '  1) 美日政策利率差(触发词: 政策利率差)\n'
    '  2) 美日10年期国债收益率差(触发词: 10年期/十年期…收益率差;附美端2s10s)\n'
    '  3) 美元兑日元水平与近期走势(触发词: 美元兑日元/USDJPY/日元汇率)\n'
    '  4) 美国政策利率水平(触发词: 联邦基金/美联储利率/美国政策利率)\n'
    '  支持附加: as_of 日期限定 / 单经济体问题转概览。\n'
    '交易、持仓、收益承诺、个股买卖等投资建议类问题属于越界(out_of_scope),'
    '本系统为研究工具,不提供投资建议。'
)


def ask_local(question, snapshot, root=None):
    """页面四: 本地接地作答(e2eb mapper→executor→renderer,零网络零模型调用)。

    返回 {'status': answered|refusal|out_of_scope|no_registry_identity|unmapped|error,
          'answer_text', 'values', 'unresolved', 'ir'}——未支持类型如实报状态,不猜映射。"""
    if not snapshot:
        return {'status': 'error', 'answer_text': '本地无研究快照,无法作答(请先运行采集)',
                'values': {}, 'unresolved': [], 'ir': None}
    try:
        import e2eb_query_mapper as qm
        import e2eb_query_executor as qe
        import e2eb_answer_renderer as ar
        ir = qm.map_question(question)
        unresolved = [u.get('mapping_status') for u in ir.get('unresolved_entities', [])
                      if isinstance(u, dict)]
        if 'out_of_scope' in unresolved:
            return {'status': 'out_of_scope',
                    'answer_text': ('该问题属于投资建议/交易类越界范围,本系统为研究工具不作答。'
                                    '可改问事实类问题,如: ' + SUPPORTED_CONCEPT_HINT),
                    'values': {}, 'unresolved': unresolved, 'ir': ir}
        if 'no_registry_identity' in unresolved:
            return {'status': 'no_registry_identity',
                    'answer_text': ('问题中的指标未能对应到指标注册表中的任何已知指标,'
                                    '暂不支持该问题。\n' + SUPPORTED_CONCEPT_HINT),
                    'values': {}, 'unresolved': unresolved, 'ir': ir}
        if not ir.get('metric_bindings') and not ir.get('operations'):
            return {'status': 'unmapped',
                    'answer_text': ('该问题不在当前支持的研究问题类型内。\n'
                                    + SUPPORTED_CONCEPT_HINT),
                    'values': {}, 'unresolved': unresolved, 'ir': ir}
        execution = qe.execute_query(ir, snapshot=snapshot)
        rendered = ar.render_answer(execution)
        status = 'answered' if rendered.get('kind') == 'grounded' else 'refusal'
        return {'status': status, 'answer_text': rendered.get('answer_text', ''),
                'values': execution.get('values', {}),
                'unresolved': unresolved, 'ir': ir}
    except Exception as e:  # noqa: BLE001 —— 工作台面: 任何栈内错误如实呈现
        return {'status': 'error', 'answer_text': f'查询执行失败: {type(e).__name__}: {e}',
                'values': {}, 'unresolved': [], 'ir': None}


EXPLAIN_SYSTEM = (
    '你是全球宏观研究助理。纪律: 1)只依据用户提供的【已核实事实】作答,'
    '不得编造或引用任何未提供的数值;2)区分【事实】与【推断】,推断须标注;'
    '3)不提供任何投资建议、资产配置倾向或价格预测;4)相关不等于因果;'
    '5)中文作答,Markdown格式。'
)


def ai_explain(question, grounded_text):
    """页面四可选: AI 研究解释(v2.1, 2026-11-09;复用
    model_conclusion_client.call_model_once,模型三参经 env_config.model_runtime_config
    解析——唯一凭证面 MODEL_*,零本机文件回退)。
    返回 {'ok', 'text'|'error'}。"""
    # 先确保项目根 .env 已载入(进程环境变量优先;幂等补载,覆盖会话中途新增的.env),
    # 否则 Key 只写在 .env 时首调会误报缺失
    import env_config as ec
    ec.load_env_file()
    cfg = ec.model_runtime_config()
    if not cfg['complete']:
        return {'ok': False,
                'error': ec.MODEL_KEY_MISSING_MESSAGE}
    import model_conclusion_client as mcc
    user = (f'研究问题: {question}\n\n【已核实事实】(本地快照接地结果,作答唯一数值来源):\n'
            f'{grounded_text}\n\n请基于以上事实给出解释性分析(传导机制/历史比较视角),'
            '并明确区分事实与推断。')
    res = mcc.call_model_once(EXPLAIN_SYSTEM, user, model=cfg['model'])
    if not res.get('ok'):
        return {'ok': False,
                'error': f"模型调用失败({res.get('kind')}): {res.get('error')}"}
    raw = res.get('raw')
    text = raw if isinstance(raw, str) else (
        raw.get('content') if isinstance(raw, dict) else str(raw))
    return {'ok': True, 'text': text or '(模型返回空正文)'}


def save_to_archive(question, snapshot, root=None, archive_dir=None):
    """页面四: 问题+结果 append-only 落研究档案(复用 research_archive;
    重新映射以分配当日单调 query_id)。返回 (query_id|None, status|错误说明)。"""
    if not snapshot:
        return None, '本地无快照,无法归档'
    try:
        from datetime import datetime, timezone, timedelta
        import research_archive as ra
        import e2eb_query_mapper as qm
        import e2eb_query_executor as qe
        created = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
        qid = ra.allocate_query_id(created, archive_dir=archive_dir)
        seq = int(qid.rsplit('-', 1)[-1])
        ir = qm.map_question(question, created_at=created, query_seq=seq)
        execution = qe.execute_query(ir, snapshot=snapshot)
        # executor 会在 IR 上回绑 target_snapshot_id(D-B4-05④一致性:归档须用执行后IR)
        status, _path = ra.append_query_record(execution.get('ir', ir),
                                               snapshot=snapshot,
                                               execution=execution,
                                               archive_dir=archive_dir)
        if status != 'written':
            return None, f'档案拒绝写入: {status}'
        return ir.get('query_id', qid), None
    except Exception as e:  # noqa: BLE001
        return None, f'归档失败: {type(e).__name__}: {e}'
