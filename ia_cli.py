#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ia_cli.py — investment-agent Agent Skill 统一工具接口(Skill 化, 2026-11-08)。

供 AI Agent(经 global-macro-research Skill)与用户调用的薄适配层:
不复制引擎,只包装 scripts/workbench_data.py / research_archive /
correlation_calculator / research_history_query 等既有模块,输出结构化 JSON。

八个能力: doctor | update | overview | changes | history | compare | research | archive

输出纪律(与 Skill 研究纪律同源):
  - 数值一律来自本地快照/采集档原值,缺失如实报缺失,绝不填 0;
  - 每个数值携带 单位/单位族/观测日期/来源/身份(代理口径) 字段;
  - 每个变化量携带 变化单位(pp|bp|pct)/基准日/窗口语义/公式;
  - 错误结构化输出(kind/message/hint),永不输出空串或裸 0 充当错误;
  - update 仅显式请求时运行;GLM 调用仅 research --glm 显式请求时发生。

用法: python3 ia_cli.py <能力> [参数]   (json 输出到 stdout; 退出码 0/1/2)
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

# 引擎导入前置(app.py 同模式): workbench_data 惰性裸导入不自插路径的模块
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import workbench_data as wd  # noqa: E402

try:
    import fact_engine as fe  # 单位族的唯一权威分桶源
    RATE_UNITS = set(fe.RATE_UNITS)
    PRICE_LIKE_UNITS = set(fe.PRICE_LIKE_UNITS)
    COUNT_UNITS = set(fe.COUNT_UNITS)
except Exception:  # noqa: BLE001 —— 引擎常量不可用时退化为空集(全部归 other)
    RATE_UNITS, PRICE_LIKE_UNITS, COUNT_UNITS = set(), set(), set()

FX_ASSET_CLASSES = {'fx_rate', 'fx_index'}
CHANGE_WINDOWS = ('week', 'mtd', 'ytd')
ENV_KEYS = (  # doctor 只报"已配置/未配置",永不打印值
    ('GLM_API_KEY', 'AI 解释/周报生成(可选,不配仅影响 AI 功能)'),
    ('FRED_API_KEY', '美联储/FRED 数据(强烈推荐,缺失则 28 个序列采集失败→Gate A FAIL)'),
    ('TUSHARE_TOKEN', '中国市场数据(可选)'),
    ('FINNHUB_API_KEY', '市场数据补充(可选)'),
    ('YF_PROXY', 'yfinance 代理(可选)'),
)
ARCHIVE_DOUBLE_NEST = 'research_archive/query_history'  # research_archive._collection_dir 再拼一层


# ══ 输出信封 ═════════════════════════════════════════════════════════
def envelope(capability, ok=True, data=None, warnings=None, violations=None,
             snapshot=None, error=None):
    out = {'ok': bool(ok), 'capability': capability, 'engine_root': ROOT,
           'snapshot_id': None, 'target_date': None, 'research_as_of': None,
           'gate_a': None, 'data': data if data is not None else {},
           'warnings': warnings or []}
    if violations:
        out['violations'] = violations
    if snapshot:
        meta = wd.snapshot_meta(snapshot)
        out.update({'snapshot_id': snapshot.get('snapshot_id'),
                    'target_date': meta['date'], 'research_as_of': meta['as_of'],
                    'gate_a': meta['gate_a']})
    if error:
        out['error'] = {'kind': error[0], 'message': error[1],
                        'hint': error[2] if len(error) > 2 else None}
    return out


def emit(payload, exit_code=0, pretty=False):
    print(json.dumps(payload, ensure_ascii=False,
                     indent=2 if pretty else None, default=str))
    sys.exit(exit_code)


def load_context():
    """快照+注册表公共入口;无快照时如实返回原因。"""
    snap, note = wd.latest_snapshot(ROOT)
    reg = wd.load_registry(ROOT)
    return snap, reg, note


# ══ 数值/变化节点(口径与身份由代码注入,不靠模型自觉) ══════════════════
def unit_family(unit, asset_class=''):
    """unit → (unit_family, unit_subfamily); 未知 unit 归 other(显示层不崩,计算路径在引擎侧已 fail-loud)。"""
    if unit in RATE_UNITS:
        return 'rate', None
    if unit in PRICE_LIKE_UNITS:
        return 'price', ('fx' if asset_class in FX_ASSET_CLASSES else None)
    if unit in COUNT_UNITS:
        return 'count', None
    return 'other', None


def identity_block(metric, fact=None):
    """registry 身份字段贯通到每个输出行(代理口径意识不靠模型自觉)。"""
    ident = dict(metric.get('identity') or (fact or {}).get('identity') or {})
    return {'instrument': ident.get('instrument'),
            'is_proxy': bool(ident.get('is_proxy')),
            'proxy_of': ident.get('proxy_of'),
            'adjustment': ident.get('adjustment'),
            'market_seat': metric.get('market_seat'),
            'economy': metric.get('economy')}


def change_nodes(fact):
    """fact.derived → 变化节点列表(窗口语义/基准日/公式全随行;无则空列表,不猜)。"""
    out = []
    derived = fact.get('derived') or {}
    for win in CHANGE_WINDOWS:
        node = derived.get(win)
        if not isinstance(node, dict):
            continue
        if node.get('pct_change') is not None:
            cu, val = 'pct', node['pct_change']
        elif node.get('pp_change') is not None:
            cu, val = 'pp', node['pp_change']
        elif node.get('bp_change') is not None:
            cu, val = 'bp', node['bp_change']
        else:
            continue
        item = {'window': win, 'change_unit': cu, 'value': val,
                'basis_date': node.get('basis_date'),
                'basis_value': node.get('basis_value'),
                'end_date': fact.get('observation_date'),
                'window_semantics': node.get('window'),
                'sessions_in_window': node.get('sessions_in_window'),
                'expected_sessions': node.get('expected_sessions'),
                'formula': node.get('formula')}
        if node.get('return_semantics'):
            item['return_semantics'] = node['return_semantics']
        if node.get('bp_change') is not None and cu == 'pp':
            item['bp_equivalent'] = node['bp_change']  # 1pp=100bp,双报防换算错
        out.append(item)
    return out


def value_node(metric, facts_by_id, gate_missing_detail, warnings):
    """注册表口径 × 快照事实 → 结构化数值节点;缺失行如实,绝不填 0。"""
    mid = metric['metric_id']
    fam, sub = unit_family(metric.get('unit', ''), metric.get('asset_class', ''))
    if fam == 'other':
        warnings.append(f"指标 {mid} 的单位 '{metric.get('unit')}' 不在引擎单位族枚举内,"
                        '已归 other——引用前须人工核对口径')
    base = {'metric_id': mid, 'display_name': metric.get('display_name'),
            'unit': metric.get('unit'), 'unit_family': fam, 'frequency': metric.get('frequency'),
            'asset_class': metric.get('asset_class'),
            'identity': identity_block(metric), 'calc': metric.get('calc')}
    if sub:
        base['unit_subfamily'] = sub
    fact = facts_by_id.get(mid)
    if fact is None:
        base.update({'value': None, 'presence': 'missing',
                     'absence_reason': gate_missing_detail.get(
                         mid, '快照中无该指标事实(未采集或采集失败)'),
                     'observation_date': None, 'quality_status': 'MISSING',
                     'source': metric.get('source'), 'changes': []})
        return base
    base.update({'value': fact.get('value'), 'presence': 'present',
                 'value_type': fact.get('value_type'),
                 'observation_date': fact.get('observation_date'),
                 'quality_status': fact.get('quality_status', 'unknown'),
                 'issues': fact.get('issues', []),
                 'as_of': fact.get('as_of'),
                 'source': {'collector': (fact.get('source') or {}).get('collector'),
                            'file': (fact.get('source') or {}).get('file')},
                 'changes': change_nodes(fact)})
    return base


def economy_view(snapshot, registry, economies, warnings):
    """单/多经济体概览节点集(缺失如实;跨经济体观测窗跨度警示)。"""
    facts_by_id = {f['metric_id']: f for f in (snapshot or {}).get('facts', [])}
    gate = (snapshot or {}).get('gate_a') or {}
    miss_detail = gate.get('noncore_missing_detail', {})
    out, all_obs = {}, []
    for eco in economies:
        wanted = [m for m in registry['metrics']
                  if m.get('economy') == eco and m.get('status') == 'active']
        nodes = [value_node(m, facts_by_id, miss_detail, warnings) for m in wanted]
        out[eco] = {'label': wd.ECONOMY_LABELS.get(eco, eco),
                    'n_metrics': len(nodes),
                    'n_missing': sum(1 for n in nodes if n['presence'] == 'missing'),
                    'metrics': nodes}
        obs = sorted(n['observation_date'] for n in nodes if n.get('observation_date'))
        if obs:
            out[eco]['observation_span'] = {'earliest': obs[0], 'latest': obs[-1]}
            all_obs.extend(obs)
    if len(economies) > 1 and all_obs:
        span = (max(all_obs), min(all_obs))
        days = (span[0] < span[1])  # 仅示意,天数差按 ISO 日历
        from datetime import date
        d_max = date.fromisoformat(max(all_obs))
        d_min = date.fromisoformat(min(all_obs))
        gap = (d_max - d_min).days
        warnings.append(
            f'跨经济体观测窗跨度 {gap} 天(最早 {min(all_obs)} ~ 最晚 {max(all_obs)}):'
            '各指标观测日不同,并排引用时必须逐行携带各自 observation_date,'
            '不得当作同一时点比较')
        del days
    return out


# ══ 研究纪律 lint(对模型可见的 warnings/violations,不静默) ═══════════
CAUSAL_VERBS = ('拖累', '驱动', '导致', '引发', '提振', '施压')
COMPOSITION_RE = re.compile(r'(权重|成分|贡献度?|占比|含[其该本]?[^,。;,\s]{0,8}(权重|敞口))')


def lint_grounded_answer(text):
    """接地作答文本 → (warnings, violations)。
    因果动词=warning(引擎合法文本可能含机制表述);组合成分/权重断言=violation
    (注册表无任何成分数据,此类断言必为编造——EEM 反例的机器可判核心)。"""
    warnings, violations = [], []
    for line in (text or '').splitlines():
        hits = [v for v in CAUSAL_VERBS if v in line]
        if hits:
            warnings.append(f'因果表述({"/".join(hits)})出现在接地作答中——'
                            f'相关≠因果,引用前须核对是否引擎事实原话: {line.strip()[:80]}')
        m = COMPOSITION_RE.search(line)
        if m:
            violations.append({'kind': 'unsupported_composition_claim',
                               'detail': f"组合成分/权重断言'{m.group(0)}'无注册表依据"
                                         '(注册表不含任何成分/权重数据,此断言必为编造)',
                               'line': line.strip()[:80]})
    return warnings, violations


def lint_fact_contract_text(text):
    """带"事实性描述"契约的文本位(如资产表关键信号列)→ violations。
    因果动词在事实位=违约;同一句出现在【假设】/【推断】标记后=该段本分,允许。"""
    violations = []
    for line in (text or '').splitlines():
        seg = re.split(r'【(假设|推断)】', line, maxsplit=1)[0]  # 标记前(或整行)为事实位
        hits = [v for v in CAUSAL_VERBS if v in seg]
        m = COMPOSITION_RE.search(seg)
        if hits:
            violations.append({'kind': 'causal_claim_in_fact_position',
                               'detail': f"事实位含因果动词({'/'.join(hits)}),须移入【推断】/【假设】或删除",
                               'line': line.strip()[:80]})
        if m:
            violations.append({'kind': 'unsupported_composition_claim',
                               'detail': f"事实位成分断言'{m.group(0)}'无数据依据",
                               'line': line.strip()[:80]})
    return violations


# ══ 八个能力 ══════════════════════════════════════════════════════════
def cmd_doctor(args):
    data = {'python': sys.version.split()[0], 'platform': sys.platform}
    import env_config as ec
    ec.load_env_file()
    data['env'] = {k: {'configured': bool(os.environ.get(k)), 'purpose': purpose}
                   for k, purpose in ENV_KEYS}
    if not os.environ.get('GLM_API_KEY'):
        data['glm_key_note'] = ec.GLM_KEY_MISSING_MESSAGE
    snap, note = wd.latest_snapshot(ROOT)
    meta = wd.snapshot_meta(snap)
    data['snapshot'] = {'available': snap is not None,
                        'note': None if snap else note,
                        'target_date': meta['date'], 'gate_a': meta['gate_a'],
                        'missing': meta['missing'], 'degraded': meta['degraded']}
    if snap:
        data['snapshot']['sources_status'] = snap.get('sources_status', {})
    daily = os.path.join(ROOT, 'data', 'daily')
    data['data_freshness'] = {}
    for prefix in ('global_', 'macro_', 'china_', 'rate_economy_',
                   'japan_', 'jp_', 'ea_', 'research_snapshot_'):
        files = sorted(glob.glob(os.path.join(daily, f'{prefix}*.json')))
        data['data_freshness'][prefix.rstrip('_')] = (
            os.path.basename(files[-1]) if files else None)
    ledgers = sorted(glob.glob(os.path.join(ROOT, 'logs', 'pipeline_run_*.json')))
    if not ledgers:
        data['last_run'] = {
            'available': False,
            'note': '无流水线台账(当日未运行采集,或台账写入失败——台账写失败不影响采集本身退出码)'}
    else:
        try:
            with open(ledgers[-1], encoding='utf-8') as fh:
                led = json.load(fh)
            critical = [{'step': s.get('name'), 'ok': s.get('ok'),
                         'skipped': s.get('skipped'), 'skip_reason': s.get('skip_reason')}
                        for s in led.get('steps', []) if s.get('critical')]
            data['last_run'] = {
                'available': True, 'ledger_file': os.path.basename(ledgers[-1]),
                'run_at': led.get('run_at'), 'success_count': led.get('success_count'),
                'critical_steps_all_ok': all(s['ok'] for s in critical),
                'gate_a': led.get('gate_a'), 'snapshot_id': led.get('snapshot_id'),
                'allow_formal_report': led.get('allow_formal_report'),
                'critical_steps': critical}
        except (OSError, ValueError) as e:
            data['last_run'] = {'available': False,
                                'note': f'台账存在但解析失败({type(e).__name__}: {e})'}
    src = os.path.join(ROOT, '.agents', 'skills', 'global-macro-research')
    proj = os.path.join(ROOT, '.claude', 'skills', 'global-macro-research')
    data['skill'] = {'source_present': os.path.isdir(src),
                     'project_install_present': os.path.isdir(proj),
                     'note': 'source=.agents/skills/(随仓库); 项目级副本=.claude/skills/(install_skill.py 生成)'}
    emit(envelope('doctor', True, data))


def cmd_update(args):
    if not args.yes:
        emit(envelope('update', False,
                      {'notice': 'update 会真实运行采集流水线(可能数分钟,含外部数据源调用)。'
                                 '确认请加 --yes。本命令永不自动触发。'},
                      error=('confirmation_required',
                             'update 需要显式 --yes 确认', 'python3 ia_cli.py update --yes')),
             exit_code=1)
    cmd = [sys.executable, os.path.join(ROOT, 'run_weekly.py')]
    if args.allow_revision:
        cmd.append('--allow-revision')
    print(json.dumps({'ok': True, 'capability': 'update', 'engine_root': ROOT,
                      'notice': '开始运行 run_weekly.py,完成后输出结果摘要(透传退出码)'},
                     ensure_ascii=False))
    try:
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    except OSError as e:
        emit(envelope('update', False, {},
                      error=('spawn_failed', f'无法启动 run_weekly.py: {e}', None)),
             exit_code=1)
    tail = (proc.stdout or '').strip().splitlines()[-40:]
    payload = envelope('update', proc.returncode == 0, {
        'exit_code': proc.returncode,
        'exit_semantics': '0=全部关键步骤成功(非关键可降级); 1=任一关键步骤失败或被跳过',
        'output_tail': tail,
        'stderr_tail': (proc.stderr or '').strip().splitlines()[-10:]})
    emit(payload, exit_code=proc.returncode)


def cmd_overview(args):
    snap, reg, note = load_context()
    if snap is None:
        emit(envelope('overview', False, {}, snapshot=None,
                      error=('no_snapshot', note, '先运行 python3 ia_cli.py update --yes 采集数据')),
             exit_code=1)
    economies = [e.strip().upper() for e in re.split(r'[,\s]+', args.economy) if e.strip()]
    bad = [e for e in economies if e not in wd.ECONOMY_LABELS]
    if bad:
        emit(envelope('overview', False, {},
                      error=('bad_economy', f"未知经济体代码: {bad}",
                             f"可选: {sorted(wd.ECONOMY_LABELS)}")), exit_code=2)
    warnings = []
    data = {'economies': economy_view(snap, reg, economies, warnings),
            'supported_hint': wd.SUPPORTED_CONCEPT_HINT}
    emit(envelope('overview', True, data, warnings, snapshot=snap))


def cmd_changes(args):
    snap, reg, note = load_context()
    if snap is None:
        emit(envelope('changes', False, {},
                      error=('no_snapshot', note, '先运行 python3 ia_cli.py update --yes 采集数据')),
             exit_code=1)
    warnings = []
    facts_by_id = {f['metric_id']: f for f in snap.get('facts', [])}
    gate = snap.get('gate_a') or {}
    wanted = [m for m in reg['metrics']
              if m.get('asset_class') in wd.MARKET_ASSET_CLASSES
              and m.get('status') == 'active'
              and (not args.asset_class or m.get('asset_class') in args.asset_class)]
    nodes = [value_node(m, facts_by_id, gate.get('noncore_missing_detail', {}), warnings)
             for m in wanted]
    by_class = {}
    for n in nodes:
        by_class.setdefault(n['asset_class'], []).append(n)
    data = {'n_metrics': len(nodes),
            'n_missing': sum(1 for n in nodes if n['presence'] == 'missing'),
            'by_asset_class': by_class,
            'window_note': '周/月/年内变化各自的窗口语义见每条 changes[].window_semantics'
                           '(如"ISO周之前最后观测为基准"),非"最近7天"'}
    emit(envelope('changes', True, data, warnings, snapshot=snap))


def cmd_history(args):
    snap, reg, _note = load_context()
    warnings = []
    if not args.metric:
        caps = wd.series_capable_metrics(snap, reg)
        data = {'series_capable_metrics': caps,
                'note': '下列指标支持历史序列(快照 series_store ∪ 采集档含序列);'
                        '其余(如 japan_rate_collector 来源)为单点观测,如实不支持'}
        emit(envelope('history', True, data, warnings, snapshot=snap))
    series, err = wd.metric_series(args.metric, snap, ROOT)
    if series is None:
        emit(envelope('history', False, {},
                      error=('no_series', err or '该指标无历史序列',
                             '运行不带 --metric 的 history 查看支持序列的指标')),
             exit_code=1)
    dates, values = series['dates'], series['values']
    lo = hi = None
    if args.start:
        lo = args.start
    if args.end:
        hi = args.end
    idx = [i for i, d in enumerate(dates)
           if (not lo or d >= lo) and (not hi or d <= hi)]
    m = reg['by_id'].get(args.metric) or {}
    fam, sub = unit_family(m.get('unit', ''), m.get('asset_class', ''))
    data = {'series': {
        'metric_id': series['metric_id'], 'label': series['label'],
        'unit': series['unit'], 'unit_family': fam, 'frequency': m.get('frequency'),
        'identity': identity_block(m), 'calc': m.get('calc'),
        'n': len(idx), 'first': dates[idx[0]] if idx else None,
        'last': dates[idx[-1]] if idx else None,
        'dates': [dates[i] for i in idx], 'values': [values[i] for i in idx],
        'source': series['source']}}
    if sub:
        data['series']['unit_subfamily'] = sub
    if not idx:
        data['series']['note'] = f'窗口 {lo}~{hi} 内无观测'
        warnings.append('所请求时间窗内无任何观测,窗口与序列覆盖不重叠')
    emit(envelope('history', True, data, warnings, snapshot=snap))


def _date_gap_days(a, b):
    from datetime import date
    try:
        return abs((date.fromisoformat(a) - date.fromisoformat(b)).days)
    except (TypeError, ValueError):
        return None


def cmd_compare(args):
    snap, reg, note = load_context()
    warnings = []
    if snap is None:
        emit(envelope('compare', False, {},
                      error=('no_snapshot', note, '先运行 python3 ia_cli.py update --yes 采集数据')),
             exit_code=1)
    if args.economies:
        ecos = [e.strip().upper() for e in re.split(r'[,\s]+', args.economies) if e.strip()]
        bad = [e for e in ecos if e not in wd.ECONOMY_LABELS]
        if bad or len(ecos) < 2:
            emit(envelope('compare', False, {},
                          error=('bad_economies',
                                 f'需≥2个合法经济体代码,收到: {ecos}',
                                 f"可选: {sorted(wd.ECONOMY_LABELS)}")), exit_code=2)
        data = {'mode': 'economies', 'economies': economy_view(snap, reg, ecos, warnings)}
        emit(envelope('compare', True, data, warnings, snapshot=snap))
    if args.assets:
        import correlation_calculator as cc
        results, missing = cc.compute_all(snap)
        data = {'mode': 'assets', 'pairs': results, 'missing': missing,
                'note': '相关性≠因果;n<15 样本警示已由引擎随行(见各 pair 字段)'}
        emit(envelope('compare', True, data, warnings, snapshot=snap))
    if args.metrics:
        ids = [m.strip() for m in args.metrics.split(',') if m.strip()]
        if len(ids) != 2:
            emit(envelope('compare', False, {},
                          error=('bad_metrics', f'--metrics 需恰好两个指标,收到: {ids}',
                                 '如 --metrics UST_10Y,JGB10Y')), exit_code=2)
        sa, err_a = wd.metric_series(ids[0], snap, ROOT)
        sb, err_b = wd.metric_series(ids[1], snap, ROOT)
        errs = [(ids[i], e) for i, e in enumerate((err_a, err_b)) if e]
        if errs:
            emit(envelope('compare', False, {},
                          error=('no_series', f'序列获取失败: {errs}',
                                 '运行不带 --metric 的 history 查看支持序列的指标')),
                 exit_code=1)
        import correlation_calculator as cc
        paired, common = cc.paired_returns(
            {'dates': sa['dates'], 'values': sa['values']},
            {'dates': sb['dates'], 'values': sb['values']})
        corr = cc.pearson(*paired) if paired else None
        import research_history_query as rhq
        sides = []
        for sid, s in ((ids[0], sa), (ids[1], sb)):
            m = reg['by_id'].get(sid) or {}
            fam, sub = unit_family(m.get('unit', ''), m.get('asset_class', ''))
            node = {'metric_id': sid, 'label': s['label'], 'unit': s['unit'],
                    'unit_family': fam, 'frequency': m.get('frequency'),
                    'identity': identity_block(m), 'calc': m.get('calc'),
                    'n': len(s['dates']), 'first': s['dates'][0], 'last': s['dates'][-1],
                    'source': s['source']}
            if sub:
                node['unit_subfamily'] = sub
            try:
                iv = rhq.interval_change(s['dates'], s['values'], s['unit'],
                                         start=common[0] if common else None,
                                         end=common[-1] if common else None)
            except Exception:  # noqa: BLE001 —— 区间变动失败不阻断对齐结果
                iv = {'available': False, 'reason': 'interval_change 计算失败'}
            node['interval_change_common_window'] = iv
            sides.append(node)
        data = {'mode': 'metrics', 'sides': sides,
                'alignment': {'n_common_observations': len(common),
                              'common_first': common[0] if common else None,
                              'common_last': common[-1] if common else None},
                'pearson_returns': corr}
        if paired and len(paired[0]) < 15:
            warnings.append(f'共同观测日仅 {len(paired[0])} 个(<15),相关性统计意义不足,'
                            '引擎口径要求如实警示')
        gap = _date_gap_days(sa['dates'][-1], sb['dates'][-1])
        if gap is not None and gap > 3:
            warnings.append(f'两侧最新观测日相差 {gap} 天({sa["dates"][-1]} vs '
                            f'{sb["dates"][-1]})——日频指标错位>3天,末端对比须注明各自观测日')
        emit(envelope('compare', True, data, warnings, snapshot=snap))
    emit(envelope('compare', False, {},
                  error=('no_mode', '未指定比较模式',
                         '--metrics A,B | --economies US,JP | --assets 三选一')), exit_code=2)


def cmd_research(args):
    snap, reg, note = load_context()
    if snap is None:
        emit(envelope('research', False, {},
                      error=('no_snapshot', note, '先运行 python3 ia_cli.py update --yes 采集数据')),
             exit_code=1)
    res = wd.ask_local(args.question, snap, ROOT)
    warnings, violations = lint_grounded_answer(res.get('answer_text'))
    data = {'status': res['status'], 'answer_text': res.get('answer_text'),
            'values': res.get('values', {}), 'unresolved': res.get('unresolved', []),
            'supported_hint': wd.SUPPORTED_CONCEPT_HINT}
    ok = res['status'] == 'answered'
    # 单经济体概览问题路由(mapper 写 ir.economy 而 executor 无分支的已知缺口,此处补):
    if res['status'] == 'unmapped' and (res.get('ir') or {}).get('economy'):
        eco = res['ir']['economy']
        if eco in wd.ECONOMY_LABELS:
            data['economy_fallback'] = economy_view(snap, reg, [eco], warnings)
            data['economy_fallback_note'] = (
                f'问题识别为单经济体({eco})概览类,已附该经济体全部指标节点——'
                '请基于节点原值作答,缺失即缺失')
    if args.glm and ok:
        glm = wd.glm_explain(args.question, res.get('answer_text', ''))
        data['glm'] = glm
        if not glm.get('ok'):
            warnings.append(f"GLM 解释未生成: {glm.get('error', '')[:120]}")
    if args.archive and ok:
        qid, err = wd.save_to_archive(args.question, snap, ROOT)
        if qid:
            data['archived_query_id'] = qid
        else:
            warnings.append(f'归档失败: {err}')
    # 退出码=进程层成败(诚实拒答/未支持也是成功执行);语义成败看 ok 与 data.status
    emit(envelope('research', ok, data, warnings, violations or None, snapshot=snap))


def cmd_archive(args):
    import research_archive as ra
    snap, _reg, _note = load_context()
    if args.action == 'save':
        if snap is None:
            emit(envelope('archive', False, {},
                          error=('no_snapshot', '本地无研究快照,无法归档',
                                 '先运行 python3 ia_cli.py update --yes 采集数据')), exit_code=1)
        qid, err = wd.save_to_archive(args.question, snap, ROOT)
        if not qid:
            emit(envelope('archive', False, {},
                          error=('save_failed', err or '归档失败', None)), exit_code=1)
        emit(envelope('archive', True, {
            'saved': True, 'query_id': qid,
            'note': f'append-only 落档于 <引擎根>/data/research/{ARCHIVE_DOUBLE_NEST}/'},
            snapshot=snap))
    elif args.action == 'list':
        try:
            qids = ra.list_query_records()
        except (OSError, ValueError) as e:
            emit(envelope('archive', True, {'records': [],
                                            'note': f'档案目录不可读或为空: {e}'}))
        records = []
        for qid in qids[-args.limit:]:
            try:
                rec = ra.load_query_record(qid)
                records.append({'query_id': qid,
                                'created_at': rec.get('created_at'),
                                'question_text': (rec.get('question_text') or '')[:80],
                                'snapshot_id': rec.get('snapshot_id'),
                                'ir_stage': rec.get('ir_stage')})
            except (FileNotFoundError, ValueError):
                records.append({'query_id': qid, 'note': '记录读取失败(损坏或不完整)'})
        emit(envelope('archive', True, {'n_total': len(qids), 'records': records}))
    else:  # get
        try:
            rec = ra.load_query_record(args.query_id)
        except FileNotFoundError:
            emit(envelope('archive', False, {},
                          error=('not_found', f'无此档案记录: {args.query_id}',
                                 'archive list 查看已有记录')), exit_code=1)
        except ValueError as e:
            emit(envelope('archive', False, {},
                          error=('corrupt_record', f'档案格式非法: {e}', None)), exit_code=1)
        emit(envelope('archive', True, {'record': rec}))


# ══ 入口 ══════════════════════════════════════════════════════════════
def build_parser():
    p = argparse.ArgumentParser(
        prog='ia_cli.py',
        description='investment-agent 统一工具接口(Agent Skill 薄适配层,结构化 JSON 输出)')
    sub = p.add_subparsers(dest='capability', required=True)

    sub.add_parser('doctor', help='环境/密钥/数据新鲜度/上次运行 体检(只报已配置与否,不打印值)')

    up = sub.add_parser('update', help='运行采集流水线(显式 --yes 才执行,透传退出码)')
    up.add_argument('--yes', action='store_true', help='确认真实运行(外部数据源调用)')
    up.add_argument('--allow-revision', action='store_true',
                    help='同日重跑允许修订(run_weekly 修订机制)')

    ov = sub.add_parser('overview', help='经济体宏观概览(原始数值节点)')
    ov.add_argument('--economy', required=True,
                    help='经济体代码,逗号分隔: US,CN,EA,JP,GLOBAL,HK')

    ch = sub.add_parser('changes', help='金融市场变化(资产类指标,窗口口径随行)')
    ch.add_argument('--asset-class', action='append',
                    help='按注册表 asset_class 过滤,可重复')

    hi = sub.add_parser('history', help='指标历史序列(不带 --metric 则列出可查指标)')
    hi.add_argument('--metric', help='指标 ID(如 SPX / UST_10Y)')
    hi.add_argument('--start', help='起始日 YYYY-MM-DD')
    hi.add_argument('--end', help='结束日 YYYY-MM-DD')

    cp = sub.add_parser('compare', help='对比: 双指标历史 / 跨经济体 / 跨资产相关性')
    cp.add_argument('--metrics', help='两个指标 ID 逗号分隔(历史对齐+相关性)')
    cp.add_argument('--economies', help='≥2 经济体代码(概览并排)')
    cp.add_argument('--assets', action='store_true', help='引擎固定 12 对资产相关性')

    rs = sub.add_parser('research', help='本地接地研究问答(e2eb 栈,零网络)')
    rs.add_argument('--question', required=True, help='研究问题')
    rs.add_argument('--glm', action='store_true',
                    help='附加 GLM 解释(产生 API 费用,仅用户明确要求时使用)')
    rs.add_argument('--archive', action='store_true', help='同时落研究档案')

    ar = sub.add_parser('archive', help='研究档案: 存/列/取')
    ar.add_argument('action', choices=['save', 'list', 'get'])
    ar.add_argument('--question', help='save: 要归档的研究问题')
    ar.add_argument('--query-id', help='get: QB-YYYYMMDD-NNN')
    ar.add_argument('--limit', type=int, default=20, help='list: 条数上限')
    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    handlers = {'doctor': cmd_doctor, 'update': cmd_update, 'overview': cmd_overview,
                'changes': cmd_changes, 'history': cmd_history, 'compare': cmd_compare,
                'research': cmd_research, 'archive': cmd_archive}
    if args.capability == 'archive':
        if args.action == 'save' and not args.question:
            emit(envelope('archive', False, {},
                          error=('missing_question', 'archive save 需要 --question', None)),
                 exit_code=2)
        if args.action == 'get' and not args.query_id:
            emit(envelope('archive', False, {},
                          error=('missing_query_id', 'archive get 需要 --query-id', None)),
                 exit_code=2)
    handlers[args.capability](args)


if __name__ == '__main__':
    main()
