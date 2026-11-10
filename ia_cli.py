#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ia_cli.py — investment-agent Agent Skill 统一工具接口(Skill 化, 2026-11-08)。

供 AI Agent(经 global-macro-research Skill)与用户调用的薄适配层:
不复制引擎,只包装 scripts/workbench_data.py / research_archive /
correlation_calculator / research_history_query 等既有模块,输出结构化 JSON。

九个能力: doctor | update | overview | changes | history | compare | analog | research | archive

输出纪律(与 Skill 研究纪律同源):
  - 数值一律来自本地快照/采集档原值,缺失如实报缺失,绝不填 0;
  - 每个数值携带 单位/单位族/观测日期/来源/身份(代理口径) 字段;
  - 每个变化量携带 变化单位(pp|bp|pct)/基准日/窗口语义/公式;
  - 错误结构化输出(kind/message/hint),永不输出空串或裸 0 充当错误;
  - update 仅显式请求时运行;模型 API 调用仅 research --explain
    显式请求时发生(v2.1: 中性 MODEL_* 三参;旧厂商别名旗标已彻底删除)。

用法: python3 ia_cli.py <能力> [参数]   (json 输出到 stdout; 退出码 0/1/2)
"""
# D 线终验修复(2): stdout 恒单 JSON 契约——D 线 LibreSSL 环境实测 urllib3
# NotOpenSSLWarning 曾在归档 save 时偶发占用 stdout 前两行,破坏"stdout 单
# JSON"消费前提。本机不可复现→代码面防御: 进程启动即静默全部 warnings,
# 且置于任何引擎 import 之前(warn 时过滤生效,惰性导入同样覆盖)。
import warnings

warnings.filterwarnings('ignore')

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
from redact_secrets import redact  # noqa: E402  P0-4: tail 过脱敏再入 JSON

# 研究档案目录注入缝(批2 WI6): None=模块默认(<引擎根>/data/research/…);
# 生产恒为 None——测试进程内 monkeypatch 指向沙箱,跨进程 e2e 用仓库副本
# 自然隔离(模块路径派生),不引入环境变量面。
_ARCHIVE_DIR = None

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
    # v2.1(Charter 5, 2026-11-09): 模型面唯一凭证面=中性三参 MODEL_*;旧变量行已删除
    ('MODEL_API_KEY', '可选模型 API Key(通用;AI 解释/周报生成/新闻模型摘要共用,'
     'Agent Native 默认无需,不配仅影响 AI 解释/周报叙事层/新闻模型摘要)'),
    ('MODEL_BASE_URL', '可选模型端点(任意 OpenAI 兼容服务;填你的服务地址)'),
    ('MODEL_NAME', '可选模型名(填你的模型服务模型名)'),
    ('IA_NEWS_MODEL_SUMMARY', '新闻模型摘要显式开关(Charter7-7: 默认关闭;'
     '须 =1 且 MODEL_* 三参齐才调用付费模型摘要;不设/非1→新闻走确定性'
     '标题回退,MODEL_* 三参齐也不再自动调用)'),
    ('FRED_API_KEY', '美联储/FRED 数据(强烈推荐,缺失则 28 个序列采集失败→Gate A FAIL)'),
    ('TUSHARE_TOKEN', '中国市场数据(可选)'),
    ('FINNHUB_API_KEY', '市场数据补充(可选)'),
    ('YF_PROXY', 'yfinance 代理(可选)'),
)
ARCHIVE_DOUBLE_NEST = 'research_archive/query_history'  # research_archive._collection_dir 再拼一层
# 任务F(批2 W10, C-4): 拒答导流——未支持问题类型转由 Agent 组合能力自由研究
AGENT_ROUTING_HINT = ('自由研究问题请组合使用 history(列出可用指标)/'
                      'compare(单位感知对齐)/overview/changes,由你的 Agent 组织研究')
# P0-1: update 结果信封的关键行筛(⛔/❌/Traceback/ERROR/失败/错误,大小写兼顾)
_CRITICAL_LINE_RE = re.compile(r'⛔|❌|Traceback|ERROR|失败|错误', re.IGNORECASE)


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
    因果动词在事实位=违约;同一句出现在【假设】/【推断】/【尚未验证】标记后=该段
    本分,允许(批2 W10 D5: 四分=事实/推断/假设/尚未验证)。"""
    violations = []
    for line in (text or '').splitlines():
        # 标记前(或整行)为事实位;【尚未验证】后文字不计事实位(不确定陈述的本位)
        seg = re.split(r'【(假设|推断|尚未验证)】', line, maxsplit=1)[0]
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


# ══ 九个能力 ══════════════════════════════════════════════════════════
def cmd_doctor(args):
    data = {'python': sys.version.split()[0], 'platform': sys.platform}
    import env_config as ec
    ec.load_env_file()
    data['env'] = {k: {'configured': bool(os.environ.get(k)), 'purpose': purpose}
                   for k, purpose in ENV_KEYS}
    # v2.1(Charter 5): 模型面唯一凭证面=MODEL_* 三参;键名改 model_key_note
    # (v2.1 破坏性变更,Release 注记,不做双写过渡),医生面不再有旧变量行
    _mcfg = ec.model_runtime_config()
    if not _mcfg['complete']:
        data['model_key_note'] = ec.MODEL_KEY_MISSING_MESSAGE
    snap, note = wd.latest_snapshot(ROOT)
    meta = wd.snapshot_meta(snap)
    data['snapshot'] = {'available': snap is not None,
                        'note': None if snap else note,
                        'target_date': meta['date'], 'gate_a': meta['gate_a'],
                        'missing': meta['missing'], 'degraded': meta['degraded']}
    if snap:
        data['snapshot']['sources_status'] = snap.get('sources_status', {})
        data['snapshot']['sources_status_note'] = (
            '上表为快照生成时点记录的采集档校验状态;磁盘当前实际在场文件以 '
            'data_freshness 为准(两者可能不一致,如文件事后被移动)')
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
                      {'notice': 'update 会真实运行采集流水线(可能数分钟,含外部数据源调用'
                                 '与新闻采集;含可选模型摘要步骤——默认关闭,须'
                                 ' IA_NEWS_MODEL_SUMMARY=1 且 MODEL_* 三参齐才调用,'
                                 '否则新闻走确定性标题回退)。确认请加 --yes。'
                                 '本命令永不自动触发。'},
                      error=('confirmation_required',
                             'update 需要显式 --yes 确认', 'python3 ia_cli.py update --yes')),
             exit_code=1)
    cmd = [sys.executable, os.path.join(ROOT, 'run_weekly.py')]
    if args.allow_revision:
        cmd.append('--allow-revision')
        if args.revision_reason:
            cmd += ['--revision-reason', args.revision_reason]
    # P0-1 契约修复: stdout 全程只输出一个 JSON 信封(SKILL.md「输出一律为单个
    # JSON 对象」)。开始提示走 stderr(人读进度,机器不解析)。
    print(f'开始运行 run_weekly.py(引擎根 {ROOT}),完成后输出结果摘要(透传退出码)',
          file=sys.stderr)
    try:
        # errors='replace': 子进程输出非 UTF-8 字节时以替换符入 tail,
        # 不让 UnicodeDecodeError 裸崩吞掉结果信封与退出码(2026-11-09 复现缺陷)
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                              errors='replace')
    except OSError as e:
        emit(envelope('update', False, {},
                      error=('spawn_failed', f'无法启动 run_weekly.py: {e}', None)),
             exit_code=1)
    lines = (proc.stdout or '').strip().splitlines()
    # critical_tail: 40 行 output_tail 会滚掉早先的根因行(如步骤9的⛔拒写),
    # 关键行单独留底(大小写兼顾),保证 ⛃/❌/Traceback/ERROR/失败/错误 仍可见。
    # P0-4: 三条 tail 全部过 redact()——采集器异常文本常内嵌含密钥的完整 URL
    critical_tail = [l for l in lines if _CRITICAL_LINE_RE.search(l)][-10:]
    payload = envelope('update', proc.returncode == 0, {
        'exit_code': proc.returncode,
        'exit_semantics': '0=全部关键步骤成功(非关键可降级); 1=任一关键步骤失败或被跳过',
        'output_tail': [redact(l) for l in lines[-40:]],
        'critical_tail': [redact(l) for l in critical_tail],
        'stderr_tail': [redact(l) for l in (proc.stderr or '').strip().splitlines()[-10:]]})
    emit(payload, exit_code=proc.returncode)


def cmd_overview(args):
    # 用法校验先于快照加载: rc=2 与环境数据无关(无快照环境同样恒定)
    economies = [e.strip().upper() for e in re.split(r'[,\s]+', args.economy) if e.strip()]
    bad = [e for e in economies if e not in wd.ECONOMY_LABELS]
    if bad:
        emit(envelope('overview', False, {},
                      error=('bad_economy', f"未知经济体代码: {bad}",
                             f"可选: {sorted(wd.ECONOMY_LABELS)}")), exit_code=2)
    snap, reg, note = load_context()
    if snap is None:
        emit(envelope('overview', False, {}, snapshot=None,
                      error=('no_snapshot', note, '先运行 python3 ia_cli.py update --yes 采集数据')),
             exit_code=1)
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


def _reject_blank_window_args(args, cap):
    """D 线终验修复(1): --start/--end 空串/纯空白曾**静默当无界**(假值直通
    if args.start 过滤条件,D 线第一次分段四窗因此全跑成累计窗)——统一
    rc=2 bad_window(与 --window/--lag 用法错误同款;二者 type=int,空串由
    argparse 自身拒 rc=2,无此病)。用法校验先于快照加载,无快照环境恒定。"""
    for flag in ('start', 'end'):
        v = getattr(args, flag, None)
        if v is not None and not str(v).strip():
            emit(envelope(cap, False, {},
                          error=('bad_window',
                                 f'--{flag} 传了空串/纯空白(会被静默当作无界)',
                                 '要无界请省略该旗标;限定窗口请给 YYYY-MM-DD')),
                 exit_code=2)


def cmd_history(args):
    _reject_blank_window_args(args, 'history')  # rc=2 先于快照加载
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


def _has_vn_history(ymd, data_dir=None):
    """A-fin §2: 该日是否存在同日修订版快照(_vN 修订版文件)。

    判据=data/daily 下 research_snapshot_{ymd}_v*.json 文件存在性(引擎已知
    事实,零推断);点时取版由 research_provenance.select_snapshot 承担(同日
    多版本取最高 _vN)。data_dir 可注入(测试用临时目录构造 _vN fixture)。
    Charter7-1: 本函数只回答"当日有无修订版"(作为门的附加披露——当日早版
    不可经 select_snapshot 取回);**realtime_info_set 的可用性判定不再依据
    同日 _vN 在场性**,改为查询起点月窗内的跨日 vintage 在场性
    (research_provenance.vintage_dates + analog_engine.realtime_gate_text)。
    """
    data_dir = data_dir or os.path.join(ROOT, 'data', 'daily')
    return bool(glob.glob(os.path.join(
        data_dir, f'research_snapshot_{ymd}_v*.json')))


def _realtime_window_band(start_iso, end_iso):
    """Charter7-1: realtime 门的查询起点月窗 [win_start, win_end]('YYYYMMDD')。

    无 --start(当前窗)→(None, None): 现役快照即当前时点信息集;
    有 --start→ 起点月窗=[start, min(--end, 起点月末日)]——点时重构的
    as-of 主张锚定在查询起点,起点月内无跨日 vintage 即 blocked。"""
    if not (start_iso or '').strip():
        return None, None
    from datetime import date, timedelta
    try:
        d0 = date.fromisoformat(str(start_iso)[:10])
        month_end = ((d0.replace(day=28) + timedelta(days=8)).replace(day=1)
                     - timedelta(days=1))
        hi = month_end
        if (end_iso or '').strip():
            hi = min(hi, date.fromisoformat(str(end_iso)[:10]))
    except ValueError:
        return None, None
    return d0.strftime('%Y%m%d'), hi.strftime('%Y%m%d')


def cmd_compare(args):
    warnings = []
    # 用法校验先于快照加载: rc=2 与环境数据无关(无快照环境同样恒定)
    if not (args.economies or args.assets or args.metrics):
        emit(envelope('compare', False, {},
                      error=('no_mode', '未指定比较模式',
                             '--metrics A,B | --economies US,JP | --assets 三选一')), exit_code=2)
    # D 线终验修复(1): 窗口日期参数空串/纯空白拒收(曾静默当无界)
    _reject_blank_window_args(args, 'compare')
    # 批2 W9: --window 仅 metrics 模式且 N≥2(先于快照加载,恒定 rc=2)
    if args.window is not None:
        if not args.metrics:
            emit(envelope('compare', False, {},
                          error=('bad_window', '--window 仅适用于 --metrics 模式',
                                 '滚动相关需要双指标序列;先给 --metrics A,B')), exit_code=2)
        if args.window < 2:
            emit(envelope('compare', False, {},
                          error=('bad_window', f'--window 须 ≥2,收到 {args.window}',
                                 '窗长=参与每个滚动相关值的变化对数')), exit_code=2)
    # A-fin §4: --lag 滞后相关(单 lag,不扫全域)——仅 metrics 模式,与 --window
    # 互斥(防输出歧义: 滚动窗与滞后平移叠加无单值解读),同 bad_window rc=2 风格
    if args.lag is not None:
        if not args.metrics:
            emit(envelope('compare', False, {},
                          error=('bad_lag', '--lag 仅适用于 --metrics 模式',
                                 '滞后相关需要双指标序列;先给 --metrics A,B')), exit_code=2)
        if args.window is not None:
            emit(envelope('compare', False, {},
                          error=('bad_lag', '--lag 与 --window 互斥(不可同时使用)',
                                 '滞后平移与滚动窗叠加无单值解读;二选一')), exit_code=2)
    ecos = []
    if args.economies:
        ecos = [e.strip().upper() for e in re.split(r'[,\s]+', args.economies) if e.strip()]
        bad = [e for e in ecos if e not in wd.ECONOMY_LABELS]
        if bad or len(ecos) < 2:
            emit(envelope('compare', False, {},
                          error=('bad_economies',
                                 f'需≥2个合法经济体代码,收到: {ecos}',
                                 f"可选: {sorted(wd.ECONOMY_LABELS)}")), exit_code=2)
    ids = []
    if args.metrics:
        ids = [m.strip() for m in args.metrics.split(',') if m.strip()]
        if len(ids) != 2:
            emit(envelope('compare', False, {},
                          error=('bad_metrics', f'--metrics 需恰好两个指标,收到: {ids}',
                                 '如 --metrics SPX,GOLD_F')), exit_code=2)
    snap, reg, note = load_context()
    if snap is None:
        emit(envelope('compare', False, {},
                      error=('no_snapshot', note, '先运行 python3 ia_cli.py update --yes 采集数据')),
             exit_code=1)
    if args.economies:
        data = {'mode': 'economies', 'economies': economy_view(snap, reg, ecos, warnings)}
        emit(envelope('compare', True, data, warnings, snapshot=snap))
    if args.assets:
        import correlation_calculator as cc
        results, missing = cc.compute_all(snap)
        data = {'mode': 'assets', 'pairs': results, 'missing': missing,
                'note': '相关性≠因果;n<15 样本警示已由引擎随行(见各 pair 字段)'}
        emit(envelope('compare', True, data, warnings, snapshot=snap))
    if args.metrics:
        sa, err_a = wd.metric_series(ids[0], snap, ROOT)
        sb, err_b = wd.metric_series(ids[1], snap, ROOT)
        errs = [(ids[i], e) for i, e in enumerate((err_a, err_b)) if e]
        if errs:
            emit(envelope('compare', False, {},
                          error=('no_series', f'序列获取失败: {errs}',
                                 '运行不带 --metric 的 history 查看支持序列的指标')),
                 exit_code=1)
        import correlation_calculator as cc
        import research_history_query as rhq
        metas = []
        for sid in ids:
            metas.append(reg['by_id'].get(sid) or {})
        fam_a, _sa = unit_family(metas[0].get('unit', ''), metas[0].get('asset_class', ''))
        fam_b, _sb = unit_family(metas[1].get('unit', ''), metas[1].get('asset_class', ''))
        # P0-3: other 族无可靠变化口径→结构化拒绝(与无序列拒绝同 rc=1 语义)
        if fam_a == 'other' or fam_b == 'other':
            bad = [{'metric': ids[i], 'unit_family': fam, 'unit': metas[i].get('unit')}
                   for i, fam in ((0, fam_a), (1, fam_b)) if fam == 'other']
            emit(envelope('compare', False, {},
                          error=('incomparable_units',
                                 f'指标单位族不可比(无可靠变化口径,拒绝混算): {bad}',
                                 'other 族不能进单位感知变化相关;换用价格/利率/计数族'
                                 '指标对,或用 history 分别取原序列')),
                 exit_code=1)
        # ── A-fin 交叉审查[中]修复: 窗口过滤会滤掉"严格早于 start 的最后观测"
        # (interval_change 的水平变动基准)→保留过滤前副本,区间变动按原序列
        # +窗口界计算(对齐/相关仍用过滤后序列,窗口语义不变) ──
        sa_raw = {'dates': list(sa['dates']), 'values': list(sa['values'])}
        sb_raw = {'dates': list(sb['dates']), 'values': list(sb['values'])}
        # ── 批2 W9: 指令窗口过滤(建议2)——对齐前作用于两侧原序列 ──
        if args.start or args.end:
            kept = []
            for s in (sa, sb):
                lo = args.start or s['dates'][0]
                hi = args.end or s['dates'][-1]
                idx = [i for i, d in enumerate(s['dates']) if lo <= d <= hi]
                s['dates'] = [s['dates'][i] for i in idx]
                s['values'] = [s['values'][i] for i in idx]
                kept.append(len(idx))
            if min(kept) == 0:
                emit(envelope('compare', False, {},
                              error=('empty_window',
                                     f'窗口 {args.start}~{args.end} 内至少一侧无观测'
                                     f'(各侧保留 {kept[0]}/{kept[1]} 点)',
                                     '放宽窗口,或先用 history 查看序列覆盖区间')),
                     exit_code=1)

        freq_a, freq_b = metas[0].get('frequency'), metas[1].get('frequency')

        # ── 批2 W9: 月度聚合对齐(建议6)——mixed_frequency 且低频侧=月频时默认 ──
        # 高频侧聚合到自然月网格(代表=期内末值,rhq.align_to_month),月键(YYYY-MM)
        # 内交;两侧同频(非月×月)走原精确日内交(alignment.mode=exact_date)。
        # ── A-fin §3: 月×月改月键内交——原 exact_date 仅在双月频锚日巧合(如
        # FRED 统一 01 锚)时可得非空交集,月中/月末锚月频对会 n=0 静默空;两侧
        # 各取 d[:7] 月键、同格多观测取末值(复用 _group_representative 规则,
        # 月×月时通常 no-op),锚日巧合不再作为对齐前提。01 锚下月键≡原日键,
        # 现役月×月数值不变(⑤号验收锁)。──
        align_mode = 'exact_date'
        agg_side = None                      # 被聚合侧标记('a'/'b'/'both'),sides 披露用
        pair_a = {'dates': sa['dates'], 'values': sa['values']}
        pair_b = {'dates': sb['dates'], 'values': sb['values']}
        if (freq_a and freq_b and freq_a != freq_b
                and 'monthly' in (freq_a, freq_b)):
            if freq_a == 'monthly':          # b 侧为高频→聚合 b
                grid = rhq.align_to_month(pair_b)
                pair_b = {'dates': grid['grid_keys'], 'values': grid['values']}
                pair_a = {'dates': [str(d)[:7] for d in pair_a['dates']],
                          'values': pair_a['values']}
                agg_side = 'b'
            else:                            # 聚合 a
                grid = rhq.align_to_month(pair_a)
                pair_a = {'dates': grid['grid_keys'], 'values': grid['values']}
                pair_b = {'dates': [str(d)[:7] for d in pair_b['dates']],
                          'values': pair_b['values']}
                agg_side = 'a'
            align_mode = 'month_grid'
        elif freq_a == freq_b == 'monthly':
            grid_a = rhq.align_to_month(pair_a)
            grid_b = rhq.align_to_month(pair_b)
            pair_a = {'dates': grid_a['grid_keys'], 'values': grid_a['values']}
            pair_b = {'dates': grid_b['grid_keys'], 'values': grid_b['values']}
            agg_side = 'both'
            align_mode = 'month_grid'

        # P0-3 单位感知变化相关: 利率→pp/价格→pct,修复利率×价格混算 pct
        paired, common = cc.paired_unit_changes(pair_a, fam_a, pair_b, fam_b)
        corr = (cc.pearson(paired['changes_a'], paired['changes_b'])
                if paired else None)

        # ── 批2 W9: 跨历掉落披露(建议5)——各自非共同观测计数(月键口径=月数) ──
        a_dropped = len(set(pair_a['dates'])) - len(common)
        b_dropped = len(set(pair_b['dates'])) - len(common)

        # ── 批2 W9: 质量披露并入 sides(建议1)——quality_status(快照事实层)
        # +release_note(注册表 release_semantics 透传;事实层无该字段,口径登记) ──
        facts_by_id = {f.get('metric_id'): f for f in snap.get('facts', [])}
        sides = []
        for k, (sid, s) in enumerate(((ids[0], sa), (ids[1], sb))):
            m = reg['by_id'].get(sid) or {}
            fam, sub = unit_family(m.get('unit', ''), m.get('asset_class', ''))
            # A-fin §1: 时间语义结构化透传(注册表人工登记,缺键=null 不默认);
            # 快照 fact 层实测 release_date 覆盖登记(数据>登记,值随行可查)
            ts = {'observation_period_kind': m.get('observation_period_kind'),
                  'release_date_available': m.get('release_date_available')}
            fact_release = (facts_by_id.get(sid) or {}).get('release_date')
            if fact_release:
                ts['release_date_available'] = True
                ts['release_date'] = fact_release
                ts['release_date_source'] = 'fact(快照实测值,覆盖登记)'
            node = {'metric_id': sid, 'label': s['label'], 'unit': s['unit'],
                    'unit_family': fam, 'frequency': m.get('frequency'),
                    'identity': identity_block(m), 'calc': m.get('calc'),
                    'n': len(s['dates']), 'first': s['dates'][0], 'last': s['dates'][-1],
                    'source': s['source'],
                    'quality_status': (facts_by_id.get(sid) or {}).get('quality_status'),
                    'release_note': m.get('release_semantics'),
                    'time_semantics': ts}
            if sub:
                node['unit_subfamily'] = sub
            if agg_side == ('a' if k == 0 else 'b'):
                node['aggregation'] = ('month_grid: 自然月网格,代表=期内末值'
                                       '(rhq.align_to_month,mixed_frequency 对齐)')
            elif agg_side == 'both':
                node['aggregation'] = ('month_grid: 月×月按月键(YYYY-MM)对齐,'
                                       '同格多观测取末值(_group_representative 同规则;'
                                       '锚日巧合不作为对齐前提)')
            # 月键窗口界: start=共同首月月初, end=共同末月月末串界('YYYY-MM-31'
            # 字典序≥该月任意日且<次月),与 interval_change 纯字符串比较兼容
            if align_mode == 'month_grid' and common:
                w_start, w_end = common[0] + '-01', common[-1] + '-31'
            else:
                w_start = common[0] if common else None
                w_end = common[-1] if common else None
            # 交叉审查[中]: 用未过滤原序列求区间变动(基准=严格早于 w_start 的
            # 最后观测,由 interval_change 自身按 start/end 定位;过滤后序列在
            # 窗口化时必无更早观测,会恒 unavailable)
            s_raw = sa_raw if k == 0 else sb_raw
            try:
                iv = rhq.interval_change(s_raw['dates'], s_raw['values'],
                                         s['unit'], start=w_start, end=w_end)
            except Exception:  # noqa: BLE001 —— 区间变动失败不阻断对齐结果
                iv = {'available': False, 'reason': 'interval_change 计算失败'}
            node['interval_change_common_window'] = iv
            sides.append(node)
        basis_a = 'pp' if fam_a == 'rate' else 'pct'
        basis_b = 'pp' if fam_b == 'rate' else 'pct'
        align_note = ('水平窗=共同观测日数;变化窗=相邻观测对数'
                      '(少一个会话,如实并列);data.n_change_pairs='
                      '剔除 null/零基丢弃后实际参与相关的对数;'
                      '不做异常值处理(原始值直算)')
        if align_mode == 'month_grid':
            if agg_side == 'both':
                align_note += (';本对为月×月: 两侧各按月键(YYYY-MM)对齐,'
                               '同格多观测取末值,锚日巧合不作为对齐前提,'
                               'n_*=共同月份数;a_dropped/b_dropped=各自未进入'
                               '共同窗的观测数(月键口径=月数)')
            else:
                align_note += (';本对为 mixed_frequency(低频侧=月频): 高频侧已聚合到'
                               '自然月网格(代表=期内末值,align_to_month),按月键'
                               '(YYYY-MM)内交,n_*=共同月份数;a_dropped/b_dropped='
                               '各自未进入共同窗的观测数(月键口径=月数)')
        # ── A-fin §2 / Charter7-1: 研究模式门(泄漏三模式的数据条件,机械可
        #    计算部分)──描述性=历史比较永远可算;事件研究=须两侧发布日已知
        # (任一宏观侧无发布日→blocked);当时信息集=**对查询时窗负责**——仅
        # 查询起点月窗内存在跨日 vintage(不同 target_date 的研究快照;同日
        # _vN 修订不算历史 vintage)才 available;无 --start/--end=当前窗
        # (现役快照即当前时点信息集,不据此声称历史可重构)。禁令执行归
        # SKILL 研究纪律(引擎不知道研究者声称什么),此处只报数据条件事实。
        release_known = [bool((s.get('time_semantics') or {})
                              .get('release_date_available')) for s in sides]
        snap_ymd = str(snap.get('target_date') or '')[:10].replace('-', '')
        import research_provenance as _rp
        import analog_engine as _ae
        _vints = _rp.vintage_dates(os.path.join(ROOT, 'data', 'daily'))
        _ws, _we = _realtime_window_band(args.start, args.end)
        research_mode_gate = {
            'descriptive': 'available',
            'event_study': ('available' if all(release_known)
                            else 'blocked: 无发布日, 不得按发布日对齐/'
                                 '不得声称事件研究'),
            'realtime_info_set': _ae.realtime_gate_text(
                _ws, _we, _vints,
                same_day_revision=(_has_vn_history(snap_ymd)
                                   if snap_ymd else False)),
            'realtime_vintage_dates': _vints}
        data = {'mode': 'metrics', 'sides': sides,
                'alignment': {'mode': align_mode,
                              'n_common_observations': len(common),
                              'n_level_observations': len(common),
                              'n_change_pairs': len(common) - 1,
                              'common_first': common[0] if common else None,
                              'common_last': common[-1] if common else None,
                              'a_dropped': a_dropped, 'b_dropped': b_dropped,
                              'research_mode_gate': research_mode_gate,
                              'note': align_note},
                'pearson_returns': corr,
                'change_basis': {'a': basis_a, 'b': basis_b},
                'n_change_pairs': paired['n_change_pairs'] if paired else 0,
                'dropped_null': paired['dropped_null'] if paired else 0,
                'zero_base_dropped': paired['zero_base_dropped'] if paired else 0}
        if fam_a == 'count' or fam_b == 'count':
            warnings.append('count 族序列按百分比(pct)近似,基数大,相对变化仅作'
                            '量级参考(basis=count 近似已随 change_basis 标注)')
        if paired and paired['n_change_pairs'] < 30:
            warnings.append(f"变化对仅 {paired['n_change_pairs']} 对(<30),"
                            '样本不足,短窗相关不外推')
            data['sample_note'] = (f"n_change_pairs={paired['n_change_pairs']}<30,"
                                   '样本不足,短窗相关性不可外推')
        if paired and paired['n_change_pairs'] < 15:
            warnings.append(f"变化对仅 {paired['n_change_pairs']} 个(<15),"
                            '相关性统计意义不足,引擎口径要求如实警示')
        if not paired or paired['n_change_pairs'] == 0:
            # 批2 W9(建议9): n==0 专门文案——区别于样本不足,直说不可计算
            data['sample_note'] = ('n_change_pairs=0: 无可用变化对,相关性不可计算'
                                   '(共同观测<3 或 变化对全部因 null/零基被弃)')
            warnings.append('n_change_pairs=0: 相关性不可计算,勿引用 pearson_returns')
        if freq_a and freq_b and freq_a != freq_b:
            if align_mode == 'month_grid':
                warnings.append(f'mixed_frequency: 两侧频率不同({freq_a} vs {freq_b}),'
                                '已默认按自然月网格聚合对齐(alignment.mode='
                                'month_grid,聚合方式见 alignment.note 与该侧 '
                                'sides[].aggregation)')
            else:
                warnings.append(f'mixed_frequency: 两侧频率不同({freq_a} vs {freq_b}),'
                                '共同观测日交集由低频侧主导,解读须注意')
        # ── 批2 W9: date_gap 阈值频率归一(建议4)——月频参与时 7→45 天
        # (月×月相邻观测~28-31 天,旧 7 天阈值对月频恒误报;缺整月=59+ 天仍报) ──
        gap_threshold = 45 if 'monthly' in (freq_a, freq_b) else 7
        if align_mode == 'exact_date' and len(common) >= 2:
            gaps = [_date_gap_days(common[i - 1], common[i])
                    for i in range(1, len(common))]
            gaps = [g for g in gaps if g is not None]
            if gaps and max(gaps) > gap_threshold:
                warnings.append(f'date_gap: 共同观测窗内相邻观测最大间隔 '
                                f'{max(gaps)} 天(>{gap_threshold},月频参与时阈值'
                                '归一为45天),期间无共同观测,相关序列存在断点')
        elif align_mode == 'month_grid' and len(common) >= 2:
            def _midx(k):
                y, m = k.split('-')
                return int(y) * 12 + int(m)
            mgaps = [_midx(common[i]) - _midx(common[i - 1])
                     for i in range(1, len(common))]
            if mgaps and max(mgaps) > 1:
                warnings.append(f'date_gap(月网格): 共同观测窗内最大间隔 '
                                f'{max(mgaps)} 个月(缺失月份),相关序列存在断点')
        gap = _date_gap_days(sa['dates'][-1], sb['dates'][-1])
        if gap is not None and gap > 3:
            warnings.append(f'两侧最新观测日相差 {gap} 天({sa["dates"][-1]} vs '
                            f'{sb["dates"][-1]})——日频指标错位>3天,末端对比须注明各自观测日')
        # ── 批2 W9: 滚动相关(建议3,C-3)——单位感知变化对上取滚动窗 pearson ──
        # rhq.rolling_correlation 为 diff 基(对输入序列差分): 传入变化序列的
        # 累积和,其相邻差分恰好还原各单位感知变化对,复用零新算式。
        if args.window is not None:
            if paired and paired['n_change_pairs'] >= args.window:
                cum_a = [sum(paired['changes_a'][:i + 1])
                         for i in range(len(paired['changes_a']))]
                cum_b = [sum(paired['changes_b'][:i + 1])
                         for i in range(len(paired['changes_b']))]
                roll = rhq.rolling_correlation(paired['dates'], cum_a, cum_b,
                                                args.window)
                rvals = [r for _, r in roll if r is not None]
                data['rolling'] = {
                    'window': args.window,
                    'n_windows': len(roll),
                    'first': {'as_of': roll[0][0], 'rho': roll[0][1]} if roll else None,
                    'last': {'as_of': roll[-1][0], 'rho': roll[-1][1]} if roll else None,
                    'max': max(rvals) if rvals else None,
                    'min': min(rvals) if rvals else None,
                    'basis': ('滚动窗=最近 N 个单位感知变化对(口径见 change_basis),'
                              'diff 基 pearson(复用 rhq.rolling_correlation);'
                              '首值自第 N+1 个变化日起(需差分样本满 N)')}
                if not roll:
                    warnings.append(f'--window {args.window}: 滚动序列为空'
                                    '(变化对数不足),rolling.n_windows=0')
            else:
                data['rolling'] = {
                    'window': args.window, 'n_windows': 0,
                    'note': f'变化对数({paired["n_change_pairs"] if paired else 0})'
                            f'不足窗长 {args.window},滚动序列为空'}
                warnings.append(f'--window {args.window}: 变化对数不足,滚动序列为空')
        # ── A-fin §4: 滞后相关(--lag k,单 lag 不扫全域)——单位感知变化对上
        # 做索引平移: 配对 (ca[i], cb[i−k]),k>0=B 领先 A k 期(B 的变化先发生),
        # k<0 反向;有效对数 n_lag=n_change_pairs−|k|,<3 → rho=None+提示。
        # pearson 复用,零新统计代码。──
        if args.lag is not None and paired:
            ca, cb = paired['changes_a'], paired['changes_b']
            k = args.lag
            idx = [i for i in range(len(ca)) if 0 <= i - k < len(cb)]
            xa = [ca[i] for i in idx]
            xb = [cb[i - k] for i in idx]
            n_lag = len(xa)
            rho_lag = cc.pearson(xa, xb) if n_lag >= 3 else None
            insufficient = (f'n_lag_pairs={n_lag}<3: 平移 |{k}| 后有效变化对不足,'
                            '滞后相关不可计算(降低 |k| 或换更长样本)') if n_lag < 3 else None
            data['lagged'] = {
                'lag': k, 'rho': rho_lag, 'n_lag_pairs': n_lag,
                'n_lag_expected': paired['n_change_pairs'] - abs(k),
                'basis': ('滞后配对=(A第i个变化, B第i−k个变化);k>0=B领先A k个'
                          '变化对(B先动),k<0=A领先;口径见 change_basis'
                          '(单位感知 pp/pct)'),
                'warning_if_insufficient': insufficient}
            if insufficient:
                warnings.append(f'--lag {k}: {insufficient}')
        emit(envelope('compare', True, data, warnings, snapshot=snap))
    emit(envelope('compare', False, {},
                  error=('no_mode', '未指定比较模式',
                         '--metrics A,B | --economies US,JP | --assets 三选一')), exit_code=2)


def _check_follow_up(query_id):
    """--follow-up-of 引用校验: QB 格式+前档存在性;返回 (ok, 原因)。"""
    import e2eb_query_ir as qir
    import research_archive as ra
    if not isinstance(query_id, str) or not qir.QUERY_ID_RE.match(query_id or ''):
        return False, f'格式非法(须QB-YYYYMMDD-NNN): {query_id!r}'
    try:
        ra.load_query_record(query_id, archive_dir=_ARCHIVE_DIR)
    except FileNotFoundError:
        return False, f'前档不存在: {query_id}'
    except ValueError as e:
        return False, f'前档读取失败: {e}'
    return True, None


def _write_research_sidecar(qid, snap, question, *, status=None, answer_text=None,
                            values=None, unresolved=None, model=None,
                            warnings_=(), violations=(), user_note=None,
                            follow_up_of=None, evidence=None, statistics=None,
                            hypotheses=None, open_questions=None, as_of=None):
    """research_full_v1 sidecar 旁挂(批2 WI6): 保存**本次用户实际所见**的
    作答正文/AI 解释原文(v2.1: 字段名 model,旧档 glm 键读取层兼容)/warnings/violations/备注/前档链接——只搬运本进程已有
    值,绝不重新生成、绝不补发任何 API 调用。返回 (ok, 详情)。

    任务F(批2 W10): 跨模型完整成果开放输入——archive save 可直传 Agent 产出的
    answer_text/evidence/statistics/hypotheses/open_questions 与 as_of(研究截止,
    落 research_as_of 位;不传=快照口径,旧行为不变)。所有文本过 redact()。"""
    from datetime import datetime, timezone
    import research_archive as ra
    import research_provenance as rp
    if not snap or not snap.get('snapshot_id'):
        return False, '无快照,sidecar 快照绑定字段不可构造'
    saved_at = datetime.now(timezone.utc).isoformat(timespec='seconds')
    try:
        base = ra.load_query_record(qid, archive_dir=_ARCHIVE_DIR)
        created_at = base.get('created_at')
    except (FileNotFoundError, ValueError):
        created_at = saved_at      # 基档不可读时不阻断(sidecar 仍绑定本进程事实)
    # W4(Model-Agnostic v2): 写入时消毒——question/answer/user_note 为用户与
    # 引擎自由文本,模型 error 可能回显端点/头;过 redact() 后落盘。只消毒写入,
    # 读取层(list/detail)不过滤,sidecar 保持"用户实际所见原文"语义(密钥除外);
    # None 如实保 None(无本次作答不编造成空串)。
    # 四路终审 D-1(2026-11-09): 登记明文清扫兜底——redact 为模式匹配,URL 编码形
    # (api_key%3D<KEY> / %61pi_key=<KEY>)可穿透;进程内已配置凭证明文(含
    # percent/plus 编码形)经 real_data_acceptance 既有登记机制直接替换,覆盖任意
    # 编码形(值级清扫,不依赖模式)。
    def _san(v):
        if not isinstance(v, str):
            return v
        import real_data_acceptance as rda
        rda.register_runtime_env_secrets()      # 幂等: 自动补 %xx/+ 编码形
        return rda.sanitize_text(redact(v))
    _model_sanitized = None
    if isinstance(model, dict):
        _model_sanitized = {k: _san(v) for k, v in model.items()}
    payload = {'record_type': ra.FULL_RECORD_TYPE, 'query_id': qid,
               'question_text': _san(question), 'created_at': created_at,
               'research_as_of': _san(as_of) if as_of else snap.get('research_as_of'),
               'snapshot_id': snap.get('snapshot_id'),
               'digest_snapshot': rp.digest_snapshot(snap),
               'status': status, 'answer_text': _san(answer_text),
               'values': values, 'unresolved': unresolved, 'model': _model_sanitized,
               'warnings': list(warnings_), 'violations': list(violations),
               'user_note': _san(user_note), 'follow_up_of': follow_up_of,
               'evidence': _san(evidence), 'statistics': _san(statistics),
               'hypotheses': _san(hypotheses),
               'open_questions': _san(open_questions),
               'saved_at': saved_at}
    try:
        st, _path = ra.write_research_full(
            ra._collection_dir(_ARCHIVE_DIR or ra.DEFAULT_ARCHIVE_DIR), payload)
    except ValueError as e:
        return False, f'schema 拒绝: {e}'
    if st != ra.STATUS_WRITTEN:
        return False, st
    return True, None


def cmd_research(args):
    if args.follow_up_of:
        fu_ok, fu_why = _check_follow_up(args.follow_up_of)
        if not fu_ok:
            emit(envelope('research', False, {},
                          error=('invalid_follow_up',
                                 f'--follow-up-of 校验失败: {fu_why}',
                                 '先 archive list 查看已有 query_id')), exit_code=2)
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
    # 任务F(批2 W10, C-4): 拒答导流——未支持类型除概念提示外,指明可由 Agent
    # 组合其他能力自由组织研究(研究能力不被四类预设问题封死)
    if res['status'] in ('unmapped', 'no_registry_identity'):
        data['answer_text'] = ((res.get('answer_text') or '') + '\n'
                               + AGENT_ROUTING_HINT)
    ok = res['status'] == 'answered'
    # 单经济体概览问题路由(mapper 写 ir.economy 而 executor 无分支的已知缺口,此处补):
    if res['status'] == 'unmapped' and (res.get('ir') or {}).get('economy'):
        eco = res['ir']['economy']
        if eco in wd.ECONOMY_LABELS:
            data['economy_fallback'] = economy_view(snap, reg, [eco], warnings)
            data['economy_fallback_note'] = (
                f'问题识别为单经济体({eco})概览类,已附该经济体全部指标节点——'
                '请基于节点原值作答,缺失即缺失')
    if args.explain and ok:
        explain = wd.ai_explain(args.question, res.get('answer_text', ''))
        data['model'] = explain
        if not explain.get('ok'):
            warnings.append(f"AI 解释未生成: {explain.get('error', '')[:120]}")
    if args.archive and ok:
        qid, err = wd.save_to_archive(args.question, snap, ROOT,
                                      archive_dir=_ARCHIVE_DIR)
        if qid:
            data['archived_query_id'] = qid
            # sidecar=本次用户实际所见原文(先于后续 warnings 追加,快照此刻状态)
            full_ok, full_why = _write_research_sidecar(
                qid, snap, args.question, status=res['status'],
                answer_text=res.get('answer_text'), values=res.get('values', {}),
                unresolved=res.get('unresolved', []), model=data.get('model'),
                warnings_=list(warnings), violations=list(violations or []),
                user_note=args.note, follow_up_of=args.follow_up_of)
            if not full_ok:
                warnings.append(f'research-full sidecar 未落盘: {full_why}')
        else:
            warnings.append(f'归档失败: {err}')
    # 退出码=进程层成败(诚实拒答/未支持也是成功执行);语义成败看 ok 与 data.status
    emit(envelope('research', ok, data, warnings, violations or None, snapshot=snap))


def cmd_analog(args):
    """历史相似结构检索(Afin §1, Charter6 块4)——独立能力,与 compare 并列。

    只读零网络: 序列装配=快照 series_store 优先,缺失指标经 wd.metric_series
    按注册表 source 回退采集档;计算全部在 analog_engine 确定性完成。
    拒答(insufficient_history/insufficient_candidates 等)=诚实行为,
    rc=1(数据条件不满足),与用法错误(rc=2)区分。"""
    import analog_engine as ae
    # 用法校验先于快照加载(rc=2 恒定,与数据无关)
    weights = None
    if args.weights is not None:
        parts = [p.strip() for p in args.weights.split(',')]
        try:
            vals = [float(p) for p in parts]
        except ValueError:
            vals = None
        if (vals is None or len(vals) != 6
                or any(v < 0 for v in vals)
                or abs(sum(vals) - 1.0) > 1e-6):
            emit(envelope('analog', False, {},
                          error=('bad_weights',
                                 f'--weights 须为六个非负数(顺序 '
                                 f'growth,inflation,rates,credit,volatility,'
                                 f'valuation)且和=1,收到: {args.weights!r}',
                                 '如 --weights 0.2,0.2,0.2,0.2,0.1,0.1')),
                 exit_code=2)
        weights = dict(zip(ae.DIMENSIONS, vals))
    if args.top is not None and args.top < 1:
        emit(envelope('analog', False, {},
                      error=('bad_top', f'--top 须为≥1 整数,收到: {args.top}',
                             'TOP-N 候选数,默认 5')), exit_code=2)
    if args.anchor is not None and not re.fullmatch(r'\d{4}-\d{2}', args.anchor):
        emit(envelope('analog', False, {},
                      error=('bad_anchor',
                             f'--anchor 须为 YYYY-MM,收到: {args.anchor!r}',
                             '如 --anchor 2026-09(回放历史锚点)')), exit_code=2)
    snap, reg, note = load_context()
    if snap is None:
        emit(envelope('analog', False, {},
                      error=('no_snapshot', note,
                             '先运行 python3 ia_cli.py update --yes 采集数据')),
             exit_code=1)
    # 序列装配: 特征面+事后面指标(只装配这两类;other 族别名不在清单,
    # 结构上不可能进计算路径——Afin §0)
    need = sorted(set(ae.FEATURE_METRICS) | set(ae.AFTERMATH_ASSETS))
    series_map, missing_series = {}, []
    for mid in need:
        s, _err = wd.metric_series(mid, snap, ROOT)
        if s and s.get('dates'):
            series_map[mid] = {'dates': list(s['dates']),
                               'values': list(s['values'])}
        else:
            missing_series.append(mid)
    snap_ymd = str(snap.get('target_date') or '')[:10].replace('-', '')
    # Charter7-1: realtime 门对锚点月查询时窗负责——跨日 vintage 日期由
    # 调用方注入(research_provenance.vintage_dates 单一权威),引擎零文件系统
    import research_provenance as _rp
    _vints = _rp.vintage_dates(os.path.join(ROOT, 'data', 'daily'))
    res = ae.run(series_map, reg, anchor=args.anchor, top=args.top or 5,
                 weights=weights, include_aftermath=not args.no_aftermath,
                 vintage_dates=_vints,
                 same_day_revision=(_has_vn_history(snap_ymd)
                                    if snap_ymd else False))
    warns = list(res['warnings'])
    if missing_series:
        warns.append('序列缺席(如实,不造数): ' + ','.join(missing_series))
    if not res['ok']:
        kind, msg, hint = res['error']
        emit(envelope('analog', False, {}, warns,
                      error=(kind, msg, hint)), exit_code=1)
    emit(envelope('analog', True, res['data'], warns, snapshot=snap))


def cmd_archive(args):
    import research_archive as ra
    snap, _reg, _note = load_context()
    if args.action == 'save':
        if args.follow_up_of:
            fu_ok, fu_why = _check_follow_up(args.follow_up_of)
            if not fu_ok:
                emit(envelope('archive', False, {},
                              error=('invalid_follow_up',
                                     f'--follow-up-of 校验失败: {fu_why}',
                                     '先 archive list 查看已有 query_id')), exit_code=2)
        if snap is None:
            emit(envelope('archive', False, {},
                          error=('no_snapshot', '本地无研究快照,无法归档',
                                 '先运行 python3 ia_cli.py update --yes 采集数据')), exit_code=1)
        qid, err = wd.save_to_archive(args.question, snap, ROOT,
                                      archive_dir=_ARCHIVE_DIR)
        if not qid:
            emit(envelope('archive', False, {},
                          error=('save_failed', err or '归档失败', None)), exit_code=1)
        # 独立保存场景: 无本次作答,answer 相关字段如实 null(备注/前档链接落位);
        # 任务F(W10): --answer-text 等六参开放 Agent 完整成果直存(全过 redact),
        # 不带=旧行为完全不变(成果键 null)
        full_ok, full_why = _write_research_sidecar(
            qid, snap, args.question, warnings_=[], violations=[],
            user_note=args.note, follow_up_of=args.follow_up_of,
            answer_text=args.answer_text, evidence=args.evidence,
            statistics=args.statistics, hypotheses=args.hypotheses,
            open_questions=args.open_questions, as_of=args.as_of)
        data = {'saved': True, 'query_id': qid,
                'note': f'append-only 落档于 <引擎根>/data/research/{ARCHIVE_DOUBLE_NEST}'
                        '/(research_archive 模块双层嵌套,既定行为)'}
        warns = []
        if not full_ok:
            warns.append(f'research-full sidecar 未落盘: {full_why}')
        emit(envelope('archive', True, data, warns, snapshot=snap))
    elif args.action == 'list':
        try:
            qids = ra.list_query_records(archive_dir=_ARCHIVE_DIR)
        except (OSError, ValueError) as e:
            emit(envelope('archive', True, {'records': [],
                                            'note': f'档案目录不可读或为空: {e}'}))
        records = []
        for qid in qids[-args.limit:]:
            try:
                rec = ra.load_query_record(qid, archive_dir=_ARCHIVE_DIR)
            except (FileNotFoundError, ValueError):
                records.append({'query_id': qid, 'note': '记录读取失败(损坏或不完整)'})
                continue
            row = {'query_id': qid,
                   'created_at': rec.get('created_at'),
                   'question_text': (rec.get('question_text') or '')[:80],
                   'snapshot_id': rec.get('snapshot_id'),
                   'ir_stage': rec.get('ir_stage')}
            try:  # sidecar 存在性(损坏不阻断列表,如实标注)
                full = ra.load_research_full(qid, archive_dir=_ARCHIVE_DIR)
            except (OSError, ValueError):
                full = False
            row['has_full'] = bool(full)
            if full and full.get('user_note'):
                row['user_note'] = str(full['user_note'])[:60]
            records.append(row)
        emit(envelope('archive', True, {'n_total': len(qids), 'records': records}))
    else:  # get
        try:
            rec = ra.load_query_record(args.query_id, archive_dir=_ARCHIVE_DIR)
        except FileNotFoundError:
            emit(envelope('archive', False, {},
                          error=('not_found', f'无此档案记录: {args.query_id}',
                                 'archive list 查看已有记录')), exit_code=1)
        except ValueError as e:
            emit(envelope('archive', False, {},
                          error=('corrupt_record', f'档案格式非法: {e}', None)), exit_code=1)
        data = {'record': rec}   # 旧档原样(格式一字不动)
        warns = []
        try:
            full = ra.load_research_full(args.query_id, archive_dir=_ARCHIVE_DIR)
        except ValueError as e:
            full, warns = None, [f'sidecar 读取失败(基档不受影响): {e}']
        if full is not None:     # 并列合并视图(base 身份为准,record_type 不被覆盖)
            merged = dict(rec)
            merged.update({k: v for k, v in full.items() if k != 'record_type'})
            # v2.1(Charter 5 S6): 旧 sidecar 'glm' 键 → 归一映射到 'model'
            # (旧档不重写;输出契约恒用 model 键,原 glm 键不再出现在合并视图)
            if 'glm' in merged:
                merged.setdefault('model', merged.pop('glm'))
            # 任务F(W10): 旧 sidecar 缺成果键 → null(读侧归一,输出契约恒齐)
            for _k in ('evidence', 'statistics', 'hypotheses', 'open_questions'):
                merged.setdefault(_k, None)
            data['full'] = merged
        emit(envelope('archive', True, data, warns))


# ══ 入口 ══════════════════════════════════════════════════════════════
def build_parser():
    p = argparse.ArgumentParser(
        prog='ia_cli.py',
        description='investment-agent 统一工具接口(Agent Skill 薄适配层,结构化 JSON 输出)')
    sub = p.add_subparsers(dest='capability', required=True)

    sub.add_parser('doctor', help='环境/密钥/数据新鲜度/上次运行 体检(只报已配置与否,不打印值)')

    up = sub.add_parser('update',
                        help='运行采集流水线(显式 --yes 才执行,透传退出码;'
                             '--allow-revision 同日修订,--revision-reason 修订原因)')
    up.add_argument('--yes', action='store_true', help='确认真实运行(外部数据源调用)')
    up.add_argument('--allow-revision', action='store_true',
                    help='同日重跑允许修订(经 run_weekly 转发 snapshot_builder,'
                         '生成 _vN 新版本,原版保留)')
    up.add_argument('--revision-reason', help='修订原因(随 --allow-revision 透传,'
                                              '写入快照 revision_reason 字段)')

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
    cp.add_argument('--start', help='metrics 模式: 窗口起始日 YYYY-MM-DD(对齐前先过滤)')
    cp.add_argument('--end', help='metrics 模式: 窗口结束日 YYYY-MM-DD(对齐前先过滤)')
    cp.add_argument('--window', type=int,
                    help='metrics 模式: 滚动相关窗长 N≥2(单位感知变化对,diff 基;'
                    '输出 rolling 摘要,不改全窗 pearson_returns)')
    cp.add_argument('--lag', type=int,
                    help='metrics 模式: 滞后相关平移 k 期(整数可负,单位=变化对;'
                    'k>0=B 领先 A k 期先动,k<0 反向;与 --window 互斥)')

    rs = sub.add_parser('research', help='本地接地研究问答(e2eb 栈,零网络)')
    rs.add_argument('--question', required=True, help='研究问题')
    rs.add_argument('--explain', dest='explain', action='store_true',
                    help='附加 AI 解释(可选模型 API,产生 API 费用,仅用户明确'
                    '要求时使用)')
    rs.add_argument('--archive', action='store_true', help='同时落研究档案')
    rs.add_argument('--note', help='用户备注(随 research-full sidecar 落档)')
    rs.add_argument('--follow-up-of',
                    help='关联前档 query_id(QB-YYYYMMDD-NNN;存在性校验失败 rc=2)')

    an = sub.add_parser('analog',
                        help='历史相似结构检索(六维状态向量+expanding z+'
                             '加权z距离+事后演变;短历史下诚实拒答)')
    an.add_argument('--anchor', help='锚点月 YYYY-MM(缺省=最新完整月;回放合法)')
    an.add_argument('--top', type=int, help='TOP-N 候选数(默认5)')
    an.add_argument('--weights',
                    help='六维权重 g,i,r,c,v,val 逗号分隔(非负,和=1;'
                         '缺省=六维等权,实值随行)')
    an.add_argument('--no-aftermath', action='store_true',
                    help='不输出事后演变块(不影响排序——排序与事后严格分离)')

    ar = sub.add_parser('archive', help='研究档案: 存/列/取')
    ar.add_argument('action', choices=['save', 'list', 'get'])
    ar.add_argument('--question', help='save: 要归档的研究问题')
    ar.add_argument('--query-id', help='get: QB-YYYYMMDD-NNN')
    ar.add_argument('--limit', type=int, default=20, help='list: 条数上限')
    ar.add_argument('--note', help='save: 用户备注(随 sidecar 落档)')
    ar.add_argument('--follow-up-of',
                    help='save: 关联前档 query_id(存在性校验失败 rc=2)')
    ar.add_argument('--answer-text',
                    help='save: 完整研究正文(Agent 成果直存;落 sidecar answer_text)')
    ar.add_argument('--evidence', help='save: 事实证据与来源')
    ar.add_argument('--statistics', help='save: 统计结果')
    ar.add_argument('--hypotheses', help='save: 竞争性假设')
    ar.add_argument('--open-questions', help='save: 未解决问题')
    ar.add_argument('--as-of', help='save: 研究截止时间(落 sidecar research_as_of 位)')
    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    handlers = {'doctor': cmd_doctor, 'update': cmd_update, 'overview': cmd_overview,
                'changes': cmd_changes, 'history': cmd_history, 'compare': cmd_compare,
                'analog': cmd_analog, 'research': cmd_research, 'archive': cmd_archive}
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
