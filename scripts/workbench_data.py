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
}


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


# ══ 历史研究 ══════════════════════════════════════════════════════════
def series_capable_metrics(snapshot, registry):
    """历史研究页可选项+发现所需全字段(C-1, 批2 W8): 快照 series_store ∪
    采集档含 series 的指标。

    字段三层纯透传/纯统计,不推算:
    - 注册表透传: label/unit/frequency/calendar/release_semantics;
    - 序列统计(first/last/n): series_store 优先,仅存采集档的取最新档
      series 原值(同旧版来源优先级,统计口径=该来源序列本身);
    - 口径族(unit_family, 单位感知比较预判用)与事实层 quality_status
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
    for prefix in ('macro_', 'global_', 'rate_economy_'):
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
    """页面四: 本地接地作答(e2eb mapper→executor→renderer,零网络零GLM)。

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
