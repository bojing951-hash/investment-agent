#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ia_cli.py — investment-agent Agent Skill 统一工具接口(Skill 化, 2026-11-08)。

供 AI Agent(经 global-macro-research Skill)与用户调用的薄适配层:
不复制引擎,只包装 scripts/workbench_data.py / research_archive /
correlation_calculator / research_history_query 等既有模块,输出结构化 JSON。

十个能力: doctor | update | overview | changes | history | compare | analog | research | archive | views

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
import hashlib
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

# 研究档案目录注入缝(批2 WI6;R17 扩环境变量形态): None=模块默认(<引擎根>/
# data/research/…)——生产恒为 None。批2 原注"不引入环境变量面"的决策由 R17
# 修订: 零Key套件 §4 以子进程跑 archive save,在有快照的本地/无头 dev 树会
# 真写生产档案(R16 查明 16 件空档,REMAINING_ISSUES P2-9),进程内 monkeypatch
# 跨不了子进程——须 IA_ARCHIVE_DIR 环境变量形态;未设置时严格 None,
# 默认行为零变化(生产/launchd 均不设此变量)。
_ARCHIVE_DIR = os.environ.get('IA_ARCHIVE_DIR') or None

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
# Audit-R33 任务4: 日档守卫分流行「未覆盖完整档」同列关键行(旧: 只混在
# 40 行 output_tail 里,被后续步骤输出滚掉即不可见)
_CRITICAL_LINE_RE = re.compile(
    r'⛔|❌|Traceback|ERROR|失败|错误|未覆盖完整档', re.IGNORECASE)


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
                         'skipped': s.get('skipped'), 'skip_reason': s.get('skip_reason'),
                         'duration_sec': s.get('duration_sec'),
                         'exit_code': s.get('exit_code'),
                         'fail_reason': s.get('fail_reason'),
                         **({'timeout_sec': s['timeout_sec']} if 'timeout_sec' in s else {})}
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


def _pipeline_ledger_since(t_launch, root=None, tolerance_sec=2.0):
    """Audit-R33 任务4(update 回执带失败步骤/时长/原因): 认领**本次运行**写出的
    流水线台账——logs/pipeline_run_*.json 中 run_at 最新、且不早于本次启动
    时刻−容差的那份(台账 run_at=流水线起始时刻)。返回 (台账 dict|None,
    不可用原因|None, 文件名|None);台账缺失/不可解析/早于本次运行一律回
    None+原因(不拿旧台账冒充本次,不影响退出码透传)。"""
    from datetime import datetime, timedelta
    root = root or ROOT
    best, best_at, best_name = None, None, None
    for p in sorted(glob.glob(os.path.join(root, 'logs', 'pipeline_run_*.json'))):
        try:
            with open(p, encoding='utf-8') as fh:
                led = json.load(fh)
            at = datetime.fromisoformat(str(led.get('run_at')))
        except (OSError, ValueError, TypeError):
            continue
        if best_at is None or at >= best_at:
            best, best_at, best_name = led, at, os.path.basename(p)
    if best is None:
        return None, 'no_readable_ledger', None
    if best_at < t_launch - timedelta(seconds=tolerance_sec):
        return None, 'ledger_predates_this_run', None
    return best, None, best_name


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
    # Audit-R33 任务4: 记启动时刻,运行后据此认领本次运行的流水线台账
    from datetime import datetime as _dt
    t_launch = _dt.now()
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
    # Audit-R33 任务4(失败步骤/时长/原因): ① 日档守卫「未覆盖完整档」分流行
    # 单列(旧: 仅混在 40 行 output_tail 里,被后续步骤输出滚掉即不可见);
    # ② 认领本次运行的流水线台账,逐步骤时长/失败原因入回执;台账不可用
    # 时如实写 steps_note(不拿旧台账冒充本次)。
    guard_diversions = [redact(l) for l in lines if '未覆盖完整档' in l]
    ledger, ledger_note, ledger_file = _pipeline_ledger_since(t_launch)
    data = {
        'exit_code': proc.returncode,
        'exit_semantics': '0=全部关键步骤成功(非关键可降级); 1=任一关键步骤失败或被跳过',
        'output_tail': [redact(l) for l in lines[-40:]],
        'critical_tail': [redact(l) for l in critical_tail],
        'stderr_tail': [redact(l) for l in (proc.stderr or '').strip().splitlines()[-10:]],
        'guard_diversions': guard_diversions,
        'ledger_file': ledger_file}
    if ledger is None:
        data['steps_note'] = (f'本次运行无可用流水线台账({ledger_note}): '
                              '逐步骤时长/失败原因不可得')
    else:
        data['steps'] = [
            {'name': s.get('name'), 'ok': s.get('ok'), 'critical': s.get('critical'),
             'skipped': s.get('skipped'), 'skip_reason': s.get('skip_reason'),
             'duration_sec': s.get('duration_sec'),
             'exit_code': s.get('exit_code'),
             'fail_reason': s.get('fail_reason'),
             **({'timeout_sec': s['timeout_sec']} if 'timeout_sec' in s else {})}
            for s in (ledger.get('steps') or [])]
        data['failed_steps'] = ledger.get('failed_steps')
        data['duration_sec'] = ledger.get('duration_sec')
        data['snapshot_id'] = ledger.get('snapshot_id')
        data['gate_a'] = ledger.get('gate_a')
    payload = envelope('update', proc.returncode == 0, data)
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
    # R7-02: 采集状态随信封贯通(文件写入时间/最后成功采集时间/数据
    # 统期三分);续用与陈旧如实警告——查询层不再静默(old→ok 无警告
    # 曾让故障注入续存档冒充可用)
    cstat = series.get('collection_status')
    if cstat:
        data['series']['collection_status'] = cstat
        if cstat.get('mode') == 'carry_forward':
            warnings.append(
                f"序列为续用非本轮采集(carry_forward 自 "
                f"{cstat.get('carry_forward_from', '?')}): 最后成功采集 "
                f"{cstat.get('last_success_at', '?')},数据统计期至 "
                f"{cstat.get('last_observation_period', '?')}")
        _tgt = str((snap or {}).get('target_date') or '')[:10]
        _lo = str(cstat.get('last_observation_period') or '')[:10]
        if _tgt and _lo:
            try:
                from datetime import date as _d
                _lag = (_d.fromisoformat(_tgt) - _d.fromisoformat(_lo)).days
            except ValueError:
                _lag = None
            if _lag is not None:
                import research_orchestrator as _ro
                _tol = (_ro._WINDOW_TOL_DAYS.get(m.get('frequency')
                                                  or '') or (0, 0))[1]
                if _lag > _tol:
                    warnings.append(
                        f"序列末观测统计期 {_lo} 落后研究时点 {_tgt} "
                        f"{_lag} 天>频率族容忍 {_tol} 天(数据陈旧;"
                        f"采集状态 mode={cstat.get('mode')})")
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
        # C席观察②(2026-11-10): record.snapshot_id 随**注入快照**走,默认取最新;
        # 研究实际基于旧版快照时须 --snapshot-id 显式绑定,读者按指针才能复现
        # (QB-032/033 教训: 正文自述 v4,指针却落 v5)。
        if getattr(args, 'snapshot_id', None):
            sid = args.snapshot_id
            if not sid.startswith('research_snapshot_'):
                sid = 'research_snapshot_' + sid     # 容忍短形 20261110_v4
            chosen, why = ra.load_snapshot_by_id(
                sid, os.path.join(ROOT, 'data', 'daily'))
            if chosen is None:
                emit(envelope('archive', False, {},
                              error=('snapshot_not_found',
                                     f'--snapshot-id 加载失败: {why}',
                                     '查 data/daily/research_snapshot_*.json 在场版本')),
                     exit_code=2)
            snap = chosen
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
                'snapshot_id': snap.get('snapshot_id'),
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


# ══ views(Charter 8, 2026-11-10) ═══════════════════════════════════════
def cmd_views(args):
    """机构观点存储(交付⑦): list/get/lint——只读装载,零写入零网络。

    信封与九能力一致;views 不依赖快照(快照位字段恒 null)。
    get/lint 的隔离件绝不放出(linter 违规=隔离,不降级装载)。"""
    import view_store as vs_m
    action = args.action
    if action == 'list':
        out = vs_m.list_views()
        data = {'schema_version': vs_m.SCHEMA_VERSION,
                'views': out['views'], 'n_views': len(out['views']),
                'n_quarantined': out['n_quarantined'], 'n_files': out['n_files'],
                'views_dir': vs_m.VIEWS_DIR}
        warns = []
        if out['n_quarantined']:
            warns.append(f"{out['n_quarantined']} 份被 linter 隔离(views lint 看违规明细;隔离件不参与任何装载面)")
        emit(envelope('views', True, data, warns))
    elif action == 'get':
        if not args.view_id:
            emit(envelope('views', False, {},
                          error=('missing_view_id', 'views get 需要 --view-id', None)),
                 exit_code=2)
        doc, reason = vs_m.get_view(args.view_id)
        if doc is None:
            emit(envelope('views', False, {},
                          error=('view_not_found_or_quarantined', reason, None)),
                 exit_code=1)
        emit(envelope('views', True, {'view': doc}))
    else:  # lint
        res = vs_m.load_views()
        data = {'schema_version': vs_m.SCHEMA_VERSION,
                'n_compliant': len(res['views']), 'n_quarantined': len(res['quarantined']),
                'n_files': res['n_files'], 'quarantined': res['quarantined']}
        warns = []
        if res['quarantined']:
            rules = sorted({v['rule'] for q in res['quarantined'] for v in q['violations']})
            warns.append(f"违规规则集: {','.join(rules)}(隔离件明细见 data.quarantined)")
        # Charter9 P0-3(裁定③): URL 活性=显式联网档位,默认关(lint 本体零网络)
        if getattr(args, 'verify_urls', False):
            url_res = vs_m.check_urls_online(timeout=getattr(args, 'url_timeout', 10))
            data['url_checks'] = url_res
            unreachable = [c for c in url_res['checks'] if not c.get('reachable')]
            warns.append(f"--verify-urls(联网档位): {url_res['n_reachable']}/"
                         f"{url_res['n_checked']} 可达;不可达≠伪造(链路腐坏/地域墙/"
                         f"改版皆不可达),只披露不隔离: "
                         + '; '.join(f"{c['view_id']}" for c in unreachable[:10]))
        emit(envelope('views', not res['quarantined'], data, warns), exit_code=0 if not res['quarantined'] else 1)


# ══ 入口 ══════════════════════════════════════════════════════════════
def cmd_research_map(args):
    """研究地图(Charter9 P4): 十问确定性扇出证据包(零模型零网络)。

    每问=问题/五层归属+当前确定性数据面+既有能力命令清单;另附
    nomination_inputs(04/05 节矛盾+单源伪共识提名原料,提名归编排层
    Agent)/ART-M·FALS 透传/观察钟透传(引擎只透传不代触发)。"""
    import research_map as rm
    try:
        data = rm.build_map(views_dir=getattr(args, 'views_dir', None))
    except (OSError, ValueError) as e:
        emit(envelope('research-map', False, {},
                      error=('map_unavailable', str(e), None)), exit_code=1)
        return
    warns = []
    ni = data.get('nomination_inputs') or {}
    if ni.get('conflicts'):
        warns.append(f"机构对撞 {len(ni['conflicts'])} 组指标(04 节提名原料,见 data)"
                     + '; '.join(c['metric_id'] for c in ni['conflicts'][:8]))
    if ni.get('pseudo_consensus_subjects'):
        warns.append('单源主题(伪共识风险,05 节提名原料): '
                     + '、'.join(ni['pseudo_consensus_subjects'][:11]))
    art = data.get('art') or {}
    if not art.get('m_table', {}).get('present'):
        warns.append('ART-M 未文件化(终报告内嵌可接受;编排层可建 '
                     'data/research/art_m.json)')
    clock = data.get('observation_clock') or {}
    if not clock.get('present'):
        warns.append('观察钟未建(编排层维护 data/research/'
                     'observation_clock.json;引擎日历门无对外能力)')
    emit(envelope('research-map', True, data, warns))


def cmd_research_run(args):
    """一键研究编排(R2/AC6): Skill 十一步工作流的可执行化(零模型)。

    每步=真 ia_cli 子进程/既有库装载,信封留档;L3 AI推断/L4 条件情景
    恒 declared-not-produced(归编排层 Agent,不代写)。落档默认关
    (--archive 显式开启)。报告落 output/research_runs/<ts>_<slug>/。"""
    import research_orchestrator as ro
    try:
        rep = ro.run_research(args.question, root=ROOT,
                              archive=bool(getattr(args, 'archive', False)),
                              out_dir=getattr(args, 'out_dir', None),
                              fanout=bool(getattr(args, 'fanout', False)))
    except (OSError, ValueError) as e:
        emit(envelope('research-run', False, {},
                      error=('orchestrator_failed', str(e), None)), exit_code=1)
        return
    data = {'report_dir': rep.get('report_dir'),
            'pipeline_version': rep.get('pipeline_version'),
            'steps': [{'step': s['step'], 'ok': s.get('ok'),
                       'executed': s.get('executed'),
                       'note': s.get('note') or s.get('skipped_reason')}
                      for s in rep.get('steps', [])],
            'layers_summary': {
                'L1_available': rep['layers']['L1_事实层']['available'],
                'L1_n_rows': len(rep['layers']['L1_事实层']['rows']),
                'L2_vp_available': rep['layers']['L2_机构观点层']['views'].get('available'),
                'L2_n_views': rep['layers']['L2_机构观点层']['views'].get('n'),
                'L3_produced': rep['layers']['L3_AI推断层']['produced'],
                'L4_produced': rep['layers']['L4_条件情景层']['produced']},
            'n_evidence_rows': len(rep.get('evidence_index', [])),
            'fanout': {'requested': (rep.get('fanout') or {}).get('requested'),
                       'n_rq': (rep.get('fanout') or {}).get('n_rq'),
                       'n_executed': (rep.get('fanout') or {}).get('n_executed'),
                       'n_agent_layer': (rep.get('fanout') or {}).get('n_agent_layer')},
            'archive': {'requested': rep['run']['archive_requested'],
                        'archived_query_id':
                            next((s.get('archived_query_id') for s in rep['steps']
                                  if s.get('step') == 'S11_archive'), None)}}
    warns = list(rep.get('notes') or [])
    if not rep.get('run_ok'):
        failed = [s['step'] for s in rep['steps']
                  if s.get('executed') and not s.get('ok')]
        warns.append(f"部分步骤失败: {','.join(failed)}(信封留档于 report_dir)")
    emit(envelope('research-run', bool(rep.get('run_ok')), data, warns))


def cmd_research_attach(args):
    """Agent Native L3/L4 落位(R23 阶段四/AC6): judgment 纪律机器校验+合并。

    校验器零生成(scripts/agent_judgment.py): 内容全来自 Agent judgment 文件,
    本命令只验纪律结构(归因/竞争性解释/证据绑定/E1-E2-E3/五行情景)并落位;
    校验不过=produced 保持 False,violations 随报告落档供 Agent 修订重提。"""
    import agent_judgment as aj
    try:
        res = aj.attach_judgment(
            args.report_dir, args.judgment, root=ROOT,
            allow_failed_run=bool(getattr(args, 'allow_failed_run', False)))
    except (OSError, ValueError, KeyError) as e:
        emit(envelope('research-attach', False, {},
                      error=('attach_failed', str(e), None)), exit_code=1)
        return
    val = res.get('validation') or {}
    data = {'report_dir': res.get('report_dir'),
            'attached': res.get('attached'),
            'layers_summary': res.get('layers_summary'),
            'blocked': res.get('blocked'),
            'run_ok_at_attach': res.get('run_ok_at_attach'),
            'validation': {'passed': val.get('passed'),
                           'n_violations': len(val.get('violations') or []),
                           'violations': val.get('violations'),
                           'n_contradictions': val.get('n_contradictions'),
                           'n_mechanism_chains': val.get('n_mechanism_chains'),
                           'n_scenarios': val.get('n_scenarios')}}
    warns = [f"{x.get('code')}@{x.get('where')}: {x.get('detail')}"
             for x in (val.get('violations') or [])]
    if res.get('blocked') == 'run_ok_false':
        warns.append('research-run run_ok=False——判断默认不得落在失败证据面'
                     '上;确属诚实拒答类失败且证据面可用时,显式 '
                     '--allow-failed-run 越过(随档可审计)')
    emit(envelope('research-attach', bool(res.get('attached')), data, warns),
         exit_code=0 if res.get('attached') else 1)



# Audit-R33 任务3: 工单产出说明基串(地图/原问直答两族共用;族别追加见下)
_R1_PLAN_PRODUCE_BASE = (
    'judgment JSON(schema v1.0;含结论/竞争性解释/反对证据处理/'
    'E1-E2-E3 证据分级/五行情景含证伪阈值与触发条件)')
_R1_PLAN_PRODUCE_FAMILY = (
    ' + reader_map(原问直答型问句: headline_conclusion 一句总判断 + '
    'policy_question 结构化回声{research_time{as_of,research_month}, '
    'official_targets[{region,status,target,decision_date,effective_date,'
    'first_publish,evidence_refs,note?}], pending_decisions[{region,answer,'
    'confirmed_through,pending[{target,decision_date,effective_date}],'
    'evidence_refs,note?}], inflation_yoy[{region,metric_id,status,value,'
    'observation_month,publish_date,base_value,delta_pp,evidence_refs,'
    'note?}], gaps_echoed[{code,region,metric_id}], comments?}——逐字回声'
    '引擎面 research_plan.policy_question: 值/日期/状态/答案逐位一致,'
    '相左=CONTRADICTED;缺席/多出/引用不可解析=NOT_VERIFIED;自由文字里的'
    '数字须与引擎面数字对应;数据不可得的格明写「数据不可得」+缺口;不得'
    '写五面键(各地区环境走位/传导图/三个转折/历史段/读者对质表))')


def _r1_family_contract(rp):
    """Audit-R33 任务3: 原问直答型工单的 reader_map 契约说明。"""
    blk = rp.get('policy_question') or {}
    return {
        'spec': ('judgment 顶层 reader_map 对象: headline_conclusion(一句总判断)'
                 ' + policy_question 结构化回声{research_time, official_targets[],'
                 ' pending_decisions[], inflation_yoy[], gaps_echoed[]}——逐字回声'
                 '引擎面 research_plan.policy_question(值/日期/状态/答案逐位'
                 '一致,相左=CONTRADICTED;缺席/多出/引用不可解析=NOT_VERIFIED;'
                 '不得写五面键)。核对实现见 scripts/research_contract/'
                 'judgment_contract.py _policy_question_checks'),
        'engine_faces': {
            'question_time': rp.get('question_time'),
            'policy_question': blk,
            'point_values_cells': len(
                (rp.get('point_values') or {}).get('cells') or []),
            'point_values_absent': [
                a.get('metric_id')
                for a in (rp.get('point_values') or {}).get('absent') or []],
            'publication_discipline': ('面内值=发布日≤研究截止日的最新观测;'
                                       '公布日优先取日历实录(calendar:),否则'
                                       '规则推定并标「推定」(缺口面逐项点名)'),
            'as_of_declared': rp.get('as_of_declared'),
            'dimension_gaps': rp.get('dimension_gaps')},
        'discipline': [
            '回声值/日期/状态须与引擎面逐位一致(不可虚构、不以相邻口径冒充)',
            '数据不可得的格须明写「数据不可得」+缺口(回声 gaps_echoed)',
            '官方记录优先: 目标水平取日历实录;序列+惯例推定须标非官方',
            '总判断条件式非预测;「已决议待生效」以官方记录为准,'
            '序列只能给出已生效变动(待生效面不可核验须如实写)',
            '研究年月/回看窗口/同比基期分别对账(同比差=同比读数之差,'
            '单位百分点)']}


def _r1_plan_gaps(rep):
    """Audit-R33 任务3: 计划缺口显式化 → (plan_status, gaps)。

    hard: zero_facts(证据索引零事实行: L1/快照事实/S3 信封/政策记录/计划
    序列点均缺席)|plan_missing(无研究计划且确定性面零指标)|原问直答分面块
    缺席。此类 run 本无法 attach(零证据/缺面必拒)——plan 段即 ok=False、
    rc=1、next 点名缺口,不再以 ok=True+零指标计划放行。"""
    gaps = []
    rep = rep if isinstance(rep, dict) else {}
    rp = rep.get('research_plan')
    ent = next((s.get('deterministic_face') for s in rep.get('steps') or []
                if s.get('step') == 'S1_decompose'), None) or {}
    n_fact = sum(
        1 for r in rep.get('evidence_index') or []
        if (r or {}).get('kind') in (
            'snapshot_fact', 's3_envelope', 'policy_record',
            'plan_series_point'))
    if not n_fact:
        gaps.append({
            'code': 'zero_facts', 'severity': 'hard',
            'detail': ('证据索引零事实行(L1/快照事实/S3 信封/政策记录/计划'
                       '序列点均缺席)——无可核证据,研究计划不可执行')})
    if rp is None and not (ent.get('metrics') or []):
        gaps.append({
            'code': 'plan_missing', 'severity': 'hard',
            'detail': ('无研究计划且确定性面零指标(问句未命中在册经济体/'
                       '维度/指标)——缺必要计划')})
    if isinstance(rp, dict) and rp.get('question_kind') == 'policy_question':
        import policy_question as _pq_g
        _bc = _pq_g.blocked_class(rp.get('policy_question'))
        if _bc == 'policy_question_faces_missing':
            gaps.append({
                'code': _bc, 'severity': 'hard',
                'detail': '原问直答分面块缺席/损坏(%s)' % _pq_g._blocked_text(_bc)})
        elif _bc == 'policy_question_face_missing':
            # 被问及的分量无证据可答: 计划可执行但只能交付草稿(正式归档
            # 拒绝)——非 hard,但缺口显式回传,不以 plan_gaps=[] 放行
            gaps.append({
                'code': _bc, 'severity': 'draft',
                'detail': '原问直答: %s——只能交付草稿(正式归档拒绝)'
                          % _pq_g._blocked_text(_bc)})
    return ('gap' if any(g['severity'] == 'hard' for g in gaps) else 'ok'), gaps


def _r1_plan_core(args, engine_root):
    """plan 段核心(Audit-R1 F09 抽取): research-run 证据面+工单/索引/摘编落盘。

    返回 (rep, rd, error);error 非 None=orchestrator 失败(如实透传)。
    """
    import research_orchestrator as ro
    try:
        rep = ro.run_research(args.question, root=engine_root,
                              archive=bool(getattr(args, 'archive', False)),
                              out_dir=getattr(args, 'out_dir', None),
                              engine_root=engine_root)
    except (OSError, ValueError) as e:
        return None, None, ('orchestrator_failed', str(e), None)
    rd = rep.get('report_dir')
    # 证据索引独立落盘(工单 read_first 引用;report.json 内嵌副本仍在)
    with open(os.path.join(rd, 'evidence_index.json'), 'w', encoding='utf-8') as f:
        json.dump(rep.get('evidence_index', []), f, ensure_ascii=False, indent=2)
    # L2 富内容摘编(确定性装配,零生成): report.json L2 只含 VP sidecar
    # 验证标签;机构观点原文在 views 库——字段选取入 run 目录供 Agent 席读
    views_note = 'views 库在场'
    digest = []
    try:
        import view_store as vs
        for v in vs.load_views(os.path.join(
                engine_root, 'data', 'institutions', 'views'))['views']:
            inst = v.get('institution') or {}
            digest.append({
                k: v.get(k) for k in (
                    'view_id', 'report_title', 'publish_date',
                    'view_horizon', 'subjects', 'core_views',
                    'forecasts', 'risk_factors')})
            digest[-1]['institution_name'] = inst.get('name')
    except (OSError, ValueError, KeyError) as e:
        views_note = f'views 库不可读/缺席: {e}'
    with open(os.path.join(rd, 'views_digest.json'), 'w', encoding='utf-8') as f:
        json.dump({'n': len(digest), 'note': views_note, 'views': digest},
                  f, ensure_ascii=False, indent=2)
    envelope_path = os.path.join(rd, 'AGENT_SEAT_ENVELOPE.json')
    work_order = {
        'role': 'Agent Native 研究席(L3 推断+L4 条件情景真产出)',
        'question': args.question,
        'report_dir': rd,
        'evidence_index_rows': len(rep.get('evidence_index', [])),
        'read_first': [
            os.path.join(rd, 'report.json'),
            os.path.join(rd, 'evidence_index.json'),
            os.path.join(rd, 'views_digest.json') + '   # L2 机构观点富内容(原文摘编)',
            'scripts/agent_judgment.py   # judgment schema v1.1 模块 docstring',
            '.agents/skills/global-macro-research/SKILL.md   # 十步工作流(纪律 15-17)',
        ],
        'produce': _R1_PLAN_PRODUCE_BASE,
        'then': ['ia_cli.py research-one --stage attach --report-dir <rd> --judgment <path>',
                 'ia_cli.py research-one --stage report --report-dir <rd>'],
        'discipline': ['L3/L4 必须真产出: 引用证据行号,答不出=明确披露禁编造',
                       '禁改 report.json 的 produced 字段(attach 校验器唯一写者)',
                       '研究质量十二问逐问答(章程§七)'],
    }
    with open(envelope_path, 'w', encoding='utf-8') as f:
        json.dump(work_order, f, ensure_ascii=False, indent=2)
    # Audit-R18: 地图问句工单追加 reader_map 规格(读者报告五面的真产要求;
    # 对照表/点值/转折候选由引擎 research_plan 给定,判断文字归本席位)
    _rp = rep.get('research_plan') if isinstance(rep, dict) else None
    if _rp and _rp.get('map_question'):
        work_order = json.load(open(envelope_path, encoding='utf-8'))
        # Audit-R29 任务4: 渲染依赖冻结面随工单落档(席位与地图生成/打包
        # 同一份输入身份;终裁 extra.frozen_inputs_sha256 与归档/重放同算)
        _rj_run = {}
        try:
            _rj_run = json.load(open(os.path.join(
                rd, 'report.json'), encoding='utf-8')).get('run') or {}
        except (OSError, ValueError):
            pass
        if _rj_run.get('frozen_inputs'):
            import agent_judgment as _aj_fi
            work_order['frozen_inputs'] = _rj_run.get('frozen_inputs')
            work_order['frozen_inputs_sha256'] = _aj_fi.frozen_inputs_digest(
                _rj_run.get('frozen_inputs'))
        work_order['produce'] += (' + reader_map(地图问句五面: 一句总判断/'
                                  '各地区环境走位/传导图逐环四件套[观察事实/'
                                  '因果假设/竞争解释/区分指标]/三个转折[日期/'
                                  '指标/前后值/谁先变/跟进或背离]/历史段0..3'
                                  '[年月/相似点/关键差异/其他经济体是否同步/'
                                  '随后3、6、12个月实际+样本注记])——Audit-R19: '
                                  '传导须连到资产指标;三转折为不同事件(不同'
                                  '指标-月,至少跨两维度);历史段须带结构化'
                                  'anchor_ym/match_window/judgment_cutoff_ym/'
                                  'aftermath_obs_months(事后窗=锚月+N 月,'
                                  '事后观测不得落回匹配期内);Audit-R20: '
                                  '走位叙述含数字须按地区回贴 anchor_echo'
                                  '[{anchor,metric_id,value,observation_month]'
                                  '(与引擎点值面逐位一致);三利率分解回贴 '
                                  'rates_decomposition{window_from,window_to,'
                                  'nominal_bp,real_bp,bei_bp}(共同交易日面);'
                                  '叙述含回报/涨跌主张须回贴 asset_returns_echo'
                                  '[{metric_id,window_months,chg_pct,window{'
                                  'from,to}}];零段历史类比合法但须 '
                                  'history_zero_case_note(检索范围+原因);'
                                  'Audit-R21: 历史段须给 us_analog 布尔+'
                                  'sample_note 样本注记(样本独立性/与当前窗'
                                  '重叠/修订口径);ex_post 正文资产数字'
                                  '(METRIC ±N.NN%/pp)会被同窗月末口径复算'
                                  '(锚月末→锚+N月月末,相左=CONTRADICTED);'
                                  '走位正文 YYYY-MM 月份须落在引擎面月份集'
                                  '(2030-07 类虚构月份=CONTRADICTED);排序'
                                  '主张(率先/领先/最早…)比对的两个指标变动'
                                  '落在同一观测月时必须写明「先后未定」'
                                  '(月频证据只能支持同步);L4 两情景的触发'
                                  '与失效方向将随读者报告'
                                  '展示(结构面沿既有 l4.scenarios 契约)')
        work_order['reader_map_contract'] = {
            'spec': 'judgment 顶层 reader_map 对象;字段结构与数值回贴核对'
                    '见 scripts/research_contract/judgment_contract.py '
                    '_map_checks(转折前后值按引擎序列月末口径复算,相左='
                    'CONTRADICTED;空正文/缺面=NOT_VERIFIED;Audit-R19 四阻断:'
                    '错用同比基期/提前引用未发布数据/同一转折重复/历史结果'
                    '落在匹配期内)。Audit-R22: ①走位正文「观测 '
                    'YYYY-MM→YYYY-MM(→YYYY-MM)」串须是同地区某点值格锚观测'
                    '序(12个月前→3个月前→最新一期)的保序子序列——锚前'
                    '不可见的观测(停摆延误月)不得入锚序叙述;②ex_post 正文'
                    '中文别名面同受同窗复算(标普500指数/美债十年期/美元指数'
                    '…+上涨/下跌方向词+个百分点/%;方向说反或数值相左='
                    'CONTRADICTED,pp 容差 0.06);③传导环竞争解释在场时宜填 '
                    'main_predicts/competing_predicts(主/竞争解释对同一区分'
                    '指标的不同预期)+face_off_verdict(∈支持主解释/支持竞争'
                    '解释/尚不能区分——证据不足必须如实写尚不能区分,预期'
                    '分立且引擎面观测在场才可裁)',
            'engine_faces': {
                'point_anchors': _rp.get('point_anchors'),
                'ex_post_offsets': _rp.get('ex_post_offsets'),
                'point_values_cells': len(
                    (_rp.get('point_values') or {}).get('cells') or []),
                'point_values_absent': [
                    a.get('metric_id')
                    for a in (_rp.get('point_values') or {}).get('absent') or []],
                'publication_discipline': '锚格值=发布日≤锚日的最新观测;'
                    'publication_date/publication_basis 随格——R20 起日历实录'
                    '条目(config/release_calendar.json,如 2025 停摆延误)'
                    '优先于推定规则,读者可核',
                'yoy_discipline': '月度同比只配去年同月/季度只配去年同季;'
                    '缺基期格 derived_yoy_pct=null+yoy_status='
                    'no_same_period_base+latest_valid_yoy(最近有效同比及月份)',
                'asset_universe': ((_rp.get('point_values') or {})
                                   .get('asset_universe') or []),
                'us_rates_trio': _rp.get('us_rates_trio'),
                'asset_moves': _rp.get('asset_moves'),
                'turning_candidates_top9': [
                    {'metric_id': c.get('metric_id'), 'from_ym': c.get('from_ym'),
                     'to_ym': c.get('to_ym'), 'value_before': c.get('value_before'),
                     'value_after': c.get('value_after'), 'delta': c.get('delta'),
                     'dimension': c.get('dimension')}
                    for c in ((_rp.get('turning_candidates') or {})
                              .get('candidates') or [])],
                'policy_event_clusters': _rp.get('policy_event_clusters'),
                'policy_doc_facts': _rp.get('policy_doc_facts'),
                'dimension_gaps': _rp.get('dimension_gaps')},
            'discipline': ['锚值与转折数值须与引擎面一致(不可虚构)',
                           '数据不可得的格须明写「数据不可得」+检索范围',
                           '总判断条件式非预测;历史段=事后陈述非预测',
                           '同比只可用引擎 ok 基期格的 derived_yoy_pct'
                           '(缺基期=不可得,可另列最近有效同比及月份)',
                           '锚值/转折只可用发布日≤锚日(研究截止日)的观测',
                           'R20 回贴纪律: 走位数字→anchor_echo(值+观测月'
                           '逐位对账,错月=CONTRADICTED);利率分解→'
                           'rates_decomposition(共同交易日同窗);回报数字→'
                           'asset_returns_echo(同窗复算+窗口两端日);'
                           '情景≥2 个各写触发与失效方向;引用引擎事后回顾'
                           '序列(最新修订值)的数字不得表述为当时首发值',
                           'R21 纪律: 历史段 us_analog+sample_note 必填;'
                           'ex_post 资产数字同窗复算(锚月末→锚+N月月末);'
                           '正文月份须在引擎面月份集内;同月变动的两指标'
                           '排序主张须写「先后未定」;传导链区分指标将随'
                           '引擎当前面观测(最新值+近30日变化)渲染'],
        }
        if _rp.get('question_kind') == 'policy_question':
            # Audit-R33 任务3: 原问直答型工单——族别随工单落档,产出规格=
            # 基串+结构化回声(上面地图五面规格不适用,整体覆盖)
            work_order['question_kind'] = 'policy_question'
            work_order['role'] = ('Agent Native 研究席(原问直答型: L3 推断+'
                                  'L4 条件情景真产出+reader_map 总判断与'
                                  '结构化回声)')
            work_order['produce'] = (_R1_PLAN_PRODUCE_BASE
                                     + _R1_PLAN_PRODUCE_FAMILY)
            work_order['reader_map_contract'] = _r1_family_contract(_rp)
        with open(envelope_path, 'w', encoding='utf-8') as f:
            json.dump(work_order, f, ensure_ascii=False, indent=2)
    return rep, rd, None


def _r1_attach_core(args, engine_root):
    """attach 段核心(Audit-R1 F09 抽取): 校验+落位。返回 (res, error)。"""
    import agent_judgment as aj
    try:
        res = aj.attach_judgment(
            args.report_dir, args.judgment, root=engine_root,
            allow_failed_run=bool(getattr(args, 'allow_failed_run', False)))
    except (OSError, ValueError, KeyError) as e:
        return None, ('attach_failed', str(e), None)
    return res, None


def _r1_report_core(args, engine_root):
    """report 段入口(Audit-R32 任务3): 工单冻结输入核对+钉死→装配核心。

    冻结输入缺件/篡改=拒绝交付(fail-closed): 返回 deliverable=False +
    blocked=frozen_inputs_invalid + 核对明细,archive 段据此拒绝(不回落
    引擎本地快照/日历/注册表重渲)。legacy 档(无 frozen_inputs)不钉。"""
    import agent_judgment as _aj_p
    try:
        with _aj_p.work_order_pins(args.report_dir, engine_root) as _pins:
            return _r1_report_core_pinned(args, engine_root, _pins)
    except _aj_p.WorkOrderPinsError as e:
        return False, {
            'stage': 'report', 'deliverable': False,
            'blocked': 'frozen_inputs_invalid',
            'draft_delivered': False,
            'frozen_inputs_check': {'ok': False, 'code': e.code,
                                    'detail': e.detail},
            'generated': False, 'machine_verified': False,
            'copies_consistent': False,
            'full_report': os.path.join(args.report_dir, 'FULL_REPORT.md'),
        }, ['冻结输入核对失败(%s)——拒绝交付与归档,不回落引擎本地'
            '快照/日历/注册表: %s' % (e.code, e.detail)]


def _r1_report_core_pinned(args, engine_root, pins):
    """report 段核心(Audit-R1 F09): FULL_REPORT **完整装配**。

    完整性契约: L1 表+L2 摘编+L3/L4 **全文内联**(produced 时逐条渲染判断
    原文——旧版仅指路不内联=可交付件不完整)+证据索引表+四态质量门;
    确定性装配零生成,L3/L4 内容归 Agent 席与独立审计。
    返回 (ok, data, warnings)。
    """
    rd = args.report_dir
    rj = json.load(open(os.path.join(rd, 'report.json'), encoding='utf-8'))
    layers = rj.get('layers', {})
    l3, l4 = layers.get('L3_AI推断层', {}), layers.get('L4_条件情景层', {})
    l1_rows = layers.get('L1_事实层', {}).get('rows', [])
    vpf = layers.get('L2_机构观点层', {}).get('views') or {}
    run_meta = rj.get('run') or {}
    out_md = os.path.join(rd, 'FULL_REPORT.md')
    lines = ['# 完整研究报告(一键研究 MVP)', '',
             '- 问题: ' + (run_meta.get('question') or args.question or ''),
             f"- run_ok: {rj.get('run_ok')} | 证据行: {len(rj.get('evidence_index', []))}"
             f" | run.ts_utc: {run_meta.get('ts_utc')}"]
    # Audit-R32 任务1: 研究截止日与证据口径一行(与 report.md 读者面同源;
    # 旧档无 run.evidence_gate=不渲染,归档字节不变)
    _eg_hdr = run_meta.get('evidence_gate') or {}
    from research_orchestrator import _eg_version_label, _eg_prelim_suffix
    if isinstance(_eg_hdr, dict) and _eg_hdr.get('as_of'):
        _c_hdr = _eg_hdr.get('counts') or {}
        lines.append(
            f"- 研究截止日(证据口径 r32): {_eg_hdr.get('as_of')} | "
            f"源快照 {_eg_hdr.get('source_snapshot_id')}(版本日 "
            f"{_eg_hdr.get('source_target_date')}) | 事实: 保留 "
            f"{_c_hdr.get('facts_kept')} / 重建 {_c_hdr.get('facts_rebuilt')}"
            f" / 剔除 {_c_hdr.get('facts_dropped')}+版本 "
            f"{_c_hdr.get('facts_excluded_version')} | 序列剔观测 "
            f"{_c_hdr.get('series_observations_dropped')}"
            + (' | 历史截止(晚观测/晚发布/当时不可得版本不入证据面)'
               if _eg_hdr.get('historical_view')
               else ' | 快照版本日口径(截止日=快照版本日)'))
        # Audit-R33 任务1: 冻结版本绑定与缺口(缺历史版本/截止后回填/已发布
        # 未入所绑版本/采集档晚于截止)——gaps 键在场才渲染(旧档无此键)
        for _g in _eg_hdr.get('gaps') or []:
            if not isinstance(_g, dict):
                continue
            _lst = list(_g.get('series') or [])
            lines.append(
                f"  - 缺口[{_g.get('gap')}]: {_g.get('detail')}"
                + ((f";{len(_lst)} 项: " + '、'.join(_lst[:12])
                    + ('…' if len(_lst) > 12 else '')) if _lst else ''))
        # Audit-R33 任务1: 政策文档按发布日期过滤(与 report.md 同源;键在场
        # 才渲染,旧档归档字节不变)
        _rp_hdr = rj.get('research_plan') if isinstance(
            rj.get('research_plan'), dict) else {}
        _pdf, _pdw = (_rp_hdr.get('policy_doc_facts'),
                      _rp_hdr.get('policy_doc_withheld'))
        if _pdf is not None or _pdw is not None:
            lines.append(
                "  - 政策文档(按发布日期过滤): 可见 %d 份" % len(_pdf or [])
                + (";未纳入(研究时点后发布,不得作为研究时点证据): "
                   + ';'.join(f"{d.get('title')}({d.get('published_on')} 发布)"
                              for d in _pdw) if _pdw else ''))
    lines += ['', '## L1 事实层(引擎确定性产出)', '',
             '| 指标 | 值 | 单位 | 观测日 | 质量 | 证据 ref |',
             '|---|---|---|---|---|---|']
    for r in l1_rows:
        src = r.get('source') or {}
        _rg = r.get('evidence_gate') or {}
        lines.append(f"| {r.get('metric_id')} | {r.get('value')} | "
                     f"{r.get('unit')} | {r.get('observation_date')} | "
                     f"{r.get('quality_status')} | {src.get('id')}"
                     # Audit-R33 任务1: 版本绑定/缺口标记(旧档行无此键)
                     + (' [重建@截止]' if _rg.get('rebuilt_at_as_of') else '')
                     + (f" [{_eg_version_label(_rg.get('version_status'))}]"
                        if _rg.get('version_status') else '')
                     + _eg_prelim_suffix(_rg) + " |")
    lines += ['', '## L2 机构观点层(VP sidecar 验证面+views 库摘编)', '',
              f"- available={vpf.get('available')} n={vpf.get('n')} "
              f"隔离={vpf.get('n_bad_quarantined')}",
              f"- 富内容摘编: views_digest.json(在场机构主张原文,机构面=institution_stated)"]
    vd_path = os.path.join(rd, 'views_digest.json')
    if os.path.exists(vd_path):
        vd = json.load(open(vd_path, encoding='utf-8'))
        for v in vd.get('views', []):
            lines.append(f"  - {v.get('view_id')} · {v.get('institution_name')}"
                         f" · {v.get('publish_date')} · {v.get('report_title')}")

    # ── L3/L4 全文内联(Audit-R1 F09 完整装配: 可交付件自含判断原文) ──
    def _inline_l3(c):
        cons = (c or {}).get('contradictions') or []
        mechs = (c or {}).get('mechanism_chains') or []
        out = []
        for x in cons:
            out.append(f"### {x.get('id')} · {x.get('statement', '')}")
            if x.get('basis'):
                out += ['- 依据: ' + x['basis']]
            for ce in x.get('competing_explanations') or []:
                if isinstance(ce, dict):
                    out.append('- 竞争性解释: ' + str(ce.get('text') or ce))
                else:
                    out.append('- 竞争性解释: ' + str(ce))
        for m in mechs:
            out.append(f"### 机制链 {m.get('id')} · {m.get('name', '')}")
            for lk in m.get('links') or []:
                s = f"- 环{lk.get('step')} [E{str(lk.get('evidence_level', '')).replace('E', '')}] {lk.get('text', '')}"
                if lk.get('missing_link_note'):
                    s += f"\n  - 缺环注记: {lk['missing_link_note']}"
                out.append(s)
        return out

    def _inline_l4(c):
        out = []
        for s in (c or {}).get('scenarios') or []:
            rows = s.get('rows') or {}
            ad = rows.get('asset_direction') or {}
            fals = rows.get('falsification') or {}
            trig = rows.get('trigger') or {}
            out.append(f"### {s.get('id')} · 角色={s.get('role', '')}")
            out.append('- 情景: ' + str(rows.get('scenario', '')))
            out.append(f"- 资产方向: {ad.get('direction', '')} | 置信档: {ad.get('confidence_tier', '')}")
            if ad.get('text'):
                out.append('  - 依据: ' + str(ad['text']))
            out.append('- 敏感变量: ' + ', '.join(rows.get('sensitive_variables') or []))
            out.append(f"- 证伪: 指标={fals.get('metric_id', '')} | 阈值={fals.get('threshold', '')}"
                       + (f" | 次级={','.join(fals.get('secondary_metric_ids') or [])}" if fals.get('secondary_metric_ids') else ''))
            out.append(f"- 触发: {trig.get('condition', '')} | 期限: {trig.get('deadline', '')}")
        return out

    lines += ['', '## L3 AI 推断层(Agent 席真产·全文内联)', '',
              f"- produced={l3.get('produced')} attribution={l3.get('attribution')}"]
    if l3.get('produced') and l3.get('content') is not None:
        lines += _inline_l3(l3.get('content'))
    else:
        lines.append('- (未落位: 判断原文不在场,见 report.md/agent_judgment.json)')
    lines += ['', '## L4 条件情景层(Agent 席真产·全文内联)', '',
              f"- produced={l4.get('produced')} attribution={l4.get('attribution')}"]
    if l4.get('produced') and l4.get('content') is not None:
        lines += _inline_l4(l4.get('content'))
    else:
        lines.append('- (未落位: 情景原文不在场,见 report.md/agent_judgment.json)')

    # 证据索引表(可交付件自含追溯面)
    lines += ['', '## 证据索引', '',
              '| # | kind | ref | 说明 |', '|---|---|---|---|']
    for i, e in enumerate(rj.get('evidence_index') or [], 1):
        lines.append(f"| {i} | {e.get('kind')} | {e.get('ref')} | "
                     f"{str(e.get('note') or e.get('desc') or '')[:80]} |")

    # Audit-R19: 后台已有的历史比较与量化说明确定性入普通读者版
    # (S6 历史相似结构 top-N+S5 日度相关;R24 VIX 样本佐证的读者面缺口)
    try:
        import research_orchestrator as _ro_q
        _q = _ro_q._render_quant_sections(rj)
        if _q:
            lines += [''] + _q
    except Exception:
        pass

    # Audit-R21 任务4: 普通问句资产月窗表(确定性装配零生成;数字+窗口
    # +两端实测值一体——R19 纪律: 正文月窗数字必须可核)。地图问句
    # 同面在读者报告资产表(research_plan.asset_moves),此处补普通
    # 问句(正文数字=同一份可复算事实)。
    _am21 = rj.get('asset_moves')
    if isinstance(_am21, dict) and _am21.get('rows'):
        lines += ['', '## 资产月窗(近一月·滚动窗最近邻)', '',
                  '| 指标 | 窗口 | 两端实测值 | 变化 |', '|---|---|---|---|']
        for _r21 in _am21['rows']:
            _w21 = _r21.get('window') or {}
            lines.append(
                f"| {_r21.get('metric_id')} | {_w21.get('from')}"
                f"..{_w21.get('to')} | {_r21.get('from_value')}"
                f"→{_r21.get('to_value')} | {_r21.get('chg_pct'):+g}%"
                f"({_r21.get('chg_abs'):+g}) |")
        if _am21.get('window_rule'):
            lines += ['', f"窗口规则: {_am21['window_rule']}"]

    # ── Audit-R1 F02 + Audit-R2 条目1/2 + Audit-R4 条目2/5: 四态门 ──
    # (生成≠校验≠审查≠可交付)
    import agent_judgment as aj
    sr = aj._semantic_review_state(rj, engine_root, rd)
    aj_meta = rj.get('agent_judgment') or {}
    # Audit-R4 条目5: 必要/可选数据规则贯通至 report/archive——分类唯一
    # 规范源=aj.blocked_class_of(与 attach 同源)。critical_zero_evidence/
    # required_data_missing 一律拦截;**仅** optional_data_missing 且
    # attach 时显式 --allow-failed-run 随档、冻结数据需求(含披露面)
    # 在场时,允许经有效独立审查(deliverable 合取项)后交付。
    # Audit-R28 任务2: 政策实录面与渲染同树同源——blocked_class_of
    # 读 engine_root 日历(注入树/验收树各自的 config),不回落本仓
    # 默认,判定与地图渲染(同 root)一字不差地一致。
    blocked_class = aj.blocked_class_of(
        rj, calendar_path=(pins.get('calendar_path') or os.path.join(
            engine_root, 'config', 'release_calendar.json')))
    # Audit-R5 条目2: 进程成功(run_ok=true)不再一票豁免数据门——
    # 必要缺口/零证据/关键步骤失败在任何 run_ok 下都阻断交付
    # (反例 2A: history 正常退出+必要指标 n=1<12 曾误放行)。
    blocked_hard = blocked_class in aj.BLOCKING_BLOCKED_CLASSES
    _dr_items = ((((rj.get('run') or {}).get('data_requirements') or {})
                  .get('items')) or [])
    degraded_ok = (blocked_class == 'optional_data_missing'
                   and bool(_dr_items)
                   and aj_meta.get('allow_failed_run') is True)
    run_state_ok = (rj.get('run_ok') is not False)
    machine_verified = bool(
        l3.get('produced') and l4.get('produced')
        and (aj_meta.get('validation') or {}).get('passed')
        # Audit-R2 条目1: 当前运行态为准——attach 后 run_ok 翻 False
        # (改档/重评)不得沿用旧 attach 成功状态;Audit-R4 条目5:
        # optional 级显式降级路径不受此条一刀切拦截
        and (aj_meta.get('run_ok_at_attach') is not False or degraded_ok)
        and (run_state_ok or degraded_ok))
    # Audit-R2 条目1 + Audit-R4 条目2: 多副本一致性(审查与渲染同版)——
    # report.md 必须=report.json 的当前渲染;FULL_REPORT.md 在场时必须=
    # 当前确定性装配(report.json+views_digest.json 同版视图);不一致=
    # 改了源没渲/渲了别的源/视图被单改,拒绝交付(摘要 v3 已把
    # views_digest 纳入绑定,渲染输入任何变化旧裁决即失效)
    copies_consistent = True
    copies_note = None
    try:
        import research_orchestrator as ro
        expect_md = ro._render_md(rj)
        actual_md = open(os.path.join(rd, 'report.md'),
                         encoding='utf-8').read()
        copies_consistent = (expect_md == actual_md)
    except (OSError, ValueError, KeyError) as exc:
        copies_consistent, copies_note = False, repr(exc)
    review_ok = (not sr.get('required')) or (
        not sr.get('error')
        and sr.get('seat_invoked')
        and sr.get('verdict') in aj.REVIEW_APPROVED_VERDICTS
        and sr.get('fresh') is True)
    warnings = []
    if not l3.get('produced') or not l4.get('produced'):
        warnings.append('L3/L4 未全 produced——不冒认完整(G2 门不放过)')
    elif not ((aj_meta.get('validation') or {}).get('passed')):
        warnings.append('机器纪律校验未过(violations 在 agent_judgment 档)')
    elif blocked_class == 'critical_zero_evidence':
        warnings.append('L1 事实行=0(critical_zero_evidence)——任何旗标'
                        '不得放行(Audit-R4 条目5)')
    elif blocked_class == 'required_data_missing':
        warnings.append('必要数据缺口/覆盖不足(required_data_missing)——'
                        '任务目标缺口不得交付;不得事后把必要改判可选'
                        '(Audit-R4 条目5;Audit-R5 条目2: run_ok=true '
                        '同样阻断)')
    elif blocked_class == 'critical_step_failure':
        warnings.append('关键步骤失败/来源校验失败/未知失败'
                        '(critical_step_failure)——质量与完整性缺口,'
                        '不得自动归为可选缺失降级交付(Audit-R5 条目2)')
    elif blocked_class == 'map_anchor_coverage_insufficient':
        warnings.append('地图锚覆盖不足(map_anchor_coverage_insufficient)'
                        '——组内 ok 锚<2 且空锚无经证实延误依据,仅存最新'
                        '单点不构成三时点对照(R21: 草稿可交付,正式归档'
                        '须组内 ok 锚≥2)')
    elif aj_meta.get('run_ok_at_attach') is False and not degraded_ok:
        warnings.append('底座 run_ok=False 且非 optional 级显式降级'
                        '(不可交付级)')
    elif rj.get('run_ok') is False and not degraded_ok:
        warnings.append('当前运行态 run_ok=False——不得沿用旧 attach '
                        '成功状态交付(Audit-R2)')
    elif degraded_ok:
        warnings.append('降级交付(optional_data_missing,显式旗标随档): '
                        '缺口披露于数据需求面,经有效独立审查后可交付'
                        '(Audit-R4 条目5)')
    elif sr.get('required') and sr.get('error'):
        warnings.append(f"裁决链非法({sr.get('error')})——最新档损坏/"
                        '冲突即阻断交付,不回退旧 PASS(Audit-R2/Audit-R4 '
                        '条目1: 裁决先后不因解析失败倒退)')
    elif sr.get('required') and not sr.get('seat_invoked'):
        warnings.append('独立审查 required=true 但裁决缺席——'
                        '不得标记 MVP 完成或可验收交付')
    elif sr.get('required') and sr.get('verdict') not in \
            aj.REVIEW_APPROVED_VERDICTS:
        warnings.append(f"独立审查裁决={sr.get('verdict')}"
                        '(REVISE/FAIL/其他=修订后再交付)')
    elif sr.get('required') and sr.get('fresh') is not True:
        warnings.append('裁决未绑定当前内容摘要或已过期(交付输入修订后须'
                        '复验生成新裁决记录)')
    elif not copies_consistent:
        warnings.append('report.md 与 report.json 渲染不同版(多副本不一致'
                        + (f'; {copies_note}' if copies_note else '')
                        + ')——拒绝交付(Audit-R2/Audit-R4 条目2)')

    # Audit-R4 条目2: FULL_REPORT 视图一致性(在场时)——比对**内容段**
    # (质量状态节之前的全部装配内容: L1/L2 摘编/L3/L4/证据索引)。
    # 内容段=report.json+views_digest.json 的纯函数,与摘要 v3 同源;
    # 质量状态节嵌入活门面(裁决推进/门翻红合法变化),不入比对——
    # 否则席位复审后重跑 report 会误伤(修订链档数翻新≠篡改)。
    # views_digest 或视图内容被单改 → 内容段 ≠ 当前装配 → 拒绝交付。
    _Q_MARKER = '\n## 质量状态'
    content_text = '\n'.join(lines) + '\n'
    prev_full = None
    if os.path.exists(out_md):
        try:
            prev_full = open(out_md, encoding='utf-8').read()
        except OSError as exc:
            copies_consistent, copies_note = False, repr(exc)
    if prev_full is not None and \
            prev_full.split(_Q_MARKER)[0] != content_text:
        copies_consistent = False
        copies_note = (copies_note or '') + ' FULL_REPORT.md 内容段与当前装配不同版'
        warnings.append('FULL_REPORT.md 内容段与当前确定性装配不同版'
                        '(渲染输入/视图被单改)——拒绝交付(Audit-R4 条目2)')

    def _quality_section(copies_val, deliv_val):
        return ['', '## 质量状态(Audit-R1 F02 四态+Audit-R2 绑定面+Audit-R4 '
                '贯通面)', '',
                f"- generated: true(FULL_REPORT 完整装配: L1+L2+L3/L4 全文内联"
                f"+证据索引)",
                f"- machine_verified: {machine_verified}"
                "(L3∧L4 produced+纪律校验过+底座非降级或 optional 级显式"
                "降级随档)",
                f"- run 门(Audit-R4 条目5): blocked_class={blocked_class} "
                f"degraded_ok={degraded_ok}",
                f"- review: required={sr.get('required')} seat_invoked="
                f"{sr.get('seat_invoked')} verdict={sr.get('verdict')} "
                f"fresh={sr.get('fresh')} error={sr.get('error')} "
                f"修订链档数={sr.get('verdicts_n')}",
                f"- copies_consistent(多副本一致): {copies_val}"
                "(report.md=report.json 当前渲染;FULL_REPORT 内容段=当前"
                "确定性装配)",
                f"- deliverable(可交付): {deliv_val}",
                '- 内容绑定(Audit-R4 条目2): content_sha256=canonical'
                '(report.json 剥离 semantic_review)+canonical'
                '(agent_judgment.json)+canonical(views_digest.json)——'
                '机构归属/标题/日期/摘编/事实/L3/L4/run_ok/版本指针任一变化'
                '即失效旧裁决;审查与渲染同源,视图不一致即拒绝交付',
                '', '---', '渲染纪律: 本件只汇编在场事实(确定性装配),不做新增'
                '生成;L3/L4 内容归 Agent 席与独立审计,本段不代写。']

    # Audit-R5 条目2: 数据门为独立合取项——run_ok=true 不再豁免必要缺口
    deliverable = (machine_verified and review_ok and copies_consistent
                   and not blocked_hard)
    # ── Audit-R25 任务1: 必要维度缺失仍交付带缺口的草稿 ──
    # 仅地图**数据面**缺口(map_core_dimension_missing / map_anchor_
    # coverage_insufficient,R20/R21 既档语义=「核心维度缺则交付草稿」)时,
    # 已过机器校验+独立审查+副本一致三门的 MAP_REPORT.md 以草稿形态交付:
    # draft_delivered=true,缺数格如实「数据不可得」+缺口注记随行。正式
    # 交付(deliverable)与正式归档(archive belt 同判拒)仍阻断——草稿≠
    # 正稿;其余阻断类(零证据/必要缺口/关键步骤失败/审查面缺口)不适用,
    # 维持原拒绝路径。
    draft_delivered = False
    if not deliverable and blocked_class in (
            'map_core_dimension_missing',
            'map_anchor_coverage_insufficient',
            'map_core_dimension_stale',
            'map_current_period_missing',
            'map_current_period_unverified',
            'map_current_period_stale_mix',
            'map_official_target_missing',
            # Audit-R33 任务3: 原问直答型被问分量全缺=草稿交付(缺数格如实
            # 标注;正式归档仍阻断)
            'policy_question_face_missing'):
        draft_delivered = (machine_verified and review_ok and copies_consistent)
        if draft_delivered:
            warnings.append(
                '草稿交付(Audit-R25 任务1+Audit-R26 任务2+Audit-R27 '
                '任务1+Audit-R28 任务2): blocked_class=%s——带缺口/过期/'
                '未核验草稿已交付(缺数格如实标注+缺口注记+确证过期维度'
                '首页标草稿+当期缺失/未核验/混合维度首页标草稿+缺官方'
                '目标记录点名缺口);正式交付与正式归档仍阻断'
                '(补数/核验/补录官方实录后重跑续链)' % blocked_class)
    # ── Audit-R18: 地图问句读者报告(MAP_REPORT.md=可直读可核查交付件) ──
    # 渲染面=report.json research_plan(对照表/点值/转折候选)+Agent 席
    # reader_map 原文,确定性装配零生成;在场文件与当前装配不同版=单改/
    # 改源没渲,copies_consistent 翻 False(与 FULL_REPORT 内容段同口径)。
    _rp18 = rj.get('research_plan') or {}
    if _rp18.get('map_question'):
        # ── Audit-R27 任务4: 原问随包落盘(engine-owned;与会话首动作
        #    落盘的树根 question_verbatim_<ts>.txt 分记——本件=运行档内
        #    自包含,重放命令直接引用)。字节=run.question;在场且异字节=
        #    副本不一致(拒付);缺席即写。 ──
        _qv_path = os.path.join(rd, 'question_verbatim.txt')
        _qv_bytes = str((rj.get('run') or {}).get('question')
                        or '').encode('utf-8')
        if os.path.exists(_qv_path):
            try:
                if open(_qv_path, 'rb').read() != _qv_bytes:
                    copies_consistent = False
                    copies_note = (copies_note or '') + \
                        ' question_verbatim.txt 与 run.question 字节不等'
                    warnings.append('question_verbatim.txt 与 run.question '
                                    '字节不等(单改在场文件)——拒绝交付')
                    deliverable = False
            except OSError as exc:
                copies_consistent, copies_note = False, repr(exc)
        else:
            with open(_qv_path, 'wb') as _qvf:
                _qvf.write(_qv_bytes)
        import research_map_planner as rmp18
        _aj_doc = {}
        _aj_path = os.path.join(rd, 'agent_judgment.json')
        if os.path.exists(_aj_path):
            try:
                _aj_doc = json.load(open(_aj_path, encoding='utf-8'))
            except (OSError, ValueError):
                _aj_doc = {}
        map_md_path = os.path.join(rd, 'MAP_REPORT.md')
        map_sha_path = os.path.join(rd, 'MAP_REPORT.sha256')
        # Audit-R23 任务1: 地图渲染用调用方指定的 engine_root(原 ROOT=
        # ia_cli 模块常量——注入树/重放树跑 report 时误读 ia_cli 自有
        # 数据树,快照定位错树);与 _r1_report_core 其余面同根。
        # Audit-R29 任务4: 运行目录携带 root_overlay/(计划段冻结的渲染
        # 依赖: 发布日期历+运行快照)在场时优先——重渲与归档/重放同一份
        # 输入,engine_root 现状(本地日历被换/快照被清)不影响本段字节。
        _ov_root = os.path.join(rd, 'root_overlay')
        map_text = rmp18.render_map_report(
            rj, _aj_doc, sr,
            root=(_ov_root if os.path.isdir(_ov_root) else engine_root))
        _fresh_sha = hashlib.sha256(map_text.encode('utf-8')).hexdigest()
        _prev_sha = None
        if os.path.exists(map_sha_path):
            try:
                _prev_sha = open(map_sha_path, encoding='utf-8').read().\
                    strip().split(' ', 1)[0] or None
            except OSError as exc:
                copies_consistent, copies_note = False, repr(exc)
        _disk_sha = None
        if os.path.exists(map_md_path):
            try:
                _disk_sha = hashlib.sha256(
                    open(map_md_path, 'rb').read()).hexdigest()
            except OSError as exc:
                copies_consistent, copies_note = False, repr(exc)
        # 防篡改锚(旁挂 sha): 磁盘文件≠锚=单改在场文件——拒付且**不重写**
        # (证据保全;归档内部重跑本段同样拒,不洗白)。文件未动而装配变=
        # 合法修订(REVISE 闭环重渲),重写并更新锚。
        # ── Audit-R24 任务1: 已裁正文冻结——最新裁决放行(UPHELD 族)且
        # fresh(主内容锚绑定当前 run)时, 在场 MAP=受审定稿: 受审**内容段**
        # 按原字节读取与归档, 渲染器漂移(同输入异输出=代码已前进)不改写
        # 受审字节; 更正/重排走 --new-map-version 另建版本→内容摘要变→
        # 旧裁决过期→复审后方可交付。内容段与当前装配一致时照常重写
        # (仅翻新审查尾=状态面, 受审部分字节不变)。 ──
        _approved24 = (sr.get('verdict') in aj.REVIEW_APPROVED_VERDICTS
                       and sr.get('fresh') is True and not sr.get('error'))
        _content_split = '\n## 语义审查'
        _cur_content24 = _new_content24 = None
        _cur_map_text24 = None
        if _disk_sha is not None:
            try:
                with open(map_md_path, encoding='utf-8') as _mf:
                    _cur_map_text24 = _mf.read()
                _cur_content24 = hashlib.sha256(
                    _cur_map_text24.split(_content_split)[0]
                    .encode('utf-8')).hexdigest()
            except (OSError, ValueError):
                _cur_content24 = None
        _new_content24 = hashlib.sha256(
            map_text.split(_content_split)[0].encode('utf-8')).hexdigest()
        # ── Audit-R32 正式验收(裁决后交付状态面): 在场地图与当前装配仅差
        # 「分工」行尾审查状态短语(裁决落档前渲染=待裁)时不属渲染器漂移
        # ——照常重写翻新状态面(受审内容段除该短语外逐字节不变,裁决绑定
        # 按状态面等价仍有效)。基线: 冻结分支恒触发,已裁交付件首页与
        # 审查尾仍写「待裁」。正文差异照旧冻结+披露。 ──
        _status_only24 = (_approved24 and _cur_content24 is not None
                          and _cur_content24 != _new_content24
                          and not getattr(args, 'new_map_version', False)
                          and aj.map_content_state_equivalent(
                              _cur_map_text24, map_text))
        _frozen24 = (_approved24 and _cur_content24 is not None
                     and _cur_content24 != _new_content24
                     and not _status_only24
                     and not getattr(args, 'new_map_version', False))
        map_drift24 = False
        map_status_refreshed24 = False
        if _prev_sha and _disk_sha and _disk_sha != _prev_sha:
            copies_consistent = False
            copies_note = (copies_note or '') + \
                ' MAP_REPORT.md 与旁挂锚 SHA 不符(单改在场文件)'
            warnings.append('MAP_REPORT.md 与旁挂锚 MAP_REPORT.sha256 不符'
                            '(在场文件被单改)——拒绝交付且不重写保全证据'
                            '(Audit-R18 任务4反例②:必需图表面以在场文件'
                            '冒充;删除该文件后方可重渲)')
            deliverable = False
            _map18_path = map_md_path
        elif _frozen24:
            map_drift24 = True
            warnings.append(
                '渲染器漂移: 已裁内容段(sha16=%s)≠当前装配(%s)——受审正文'
                '按原字节交付不改写(裁决绑定的受审定稿权威);更正/重排须 '
                '--new-map-version 另建版本复审' % (_cur_content24[:16],
                                                    _new_content24[:16]))
            _map18_path = map_md_path
        else:
            if _status_only24:
                map_status_refreshed24 = True
            with open(map_md_path, 'w', encoding='utf-8') as f:
                f.write(map_text)
            with open(map_sha_path, 'w', encoding='utf-8') as f:
                f.write(_fresh_sha + '  MAP_REPORT.md\n')
            _map18_path = map_md_path
        # ── Audit-R24 任务1: --new-map-version 另建版本复审 ──
        # 显式版本递进: 重渲新版+锚更新+report.json research_plan.map_version
        # +1(内容摘要随 report.json 变→旧裁决主锚自动过期)——本轮不交付,
        # 待独立席复审落新裁决(绑定新版双锚)后方可交付/归档。legacy 旧档
        # 无地图绑定亦经此主锚过期强制复审,不留无绑定即漂的口子。
        if getattr(args, 'new_map_version', False) and \
                _rp18.get('map_question'):
            _mv = int(_rp18.get('map_version') or 1) + 1
            rj['research_plan']['map_version'] = _mv
            aj._atomic_write_text(
                os.path.join(rd, 'report.json'),
                json.dumps(rj, ensure_ascii=False, indent=2, default=str))
            deliverable = False
            warnings.append(
                '新地图版本已渲染(map_version=%d)——内容摘要已变,旧裁决'
                '过期;独立席复审落新裁决后方可交付/归档(更正或重排另建'
                '版本复审,Audit-R24 任务1)' % _mv)
    full_text = content_text + '\n'.join(
        _quality_section(copies_consistent, deliverable)) + '\n'
    with open(out_md, 'w', encoding='utf-8') as f:
        f.write(full_text)
    data = {
        'stage': 'report', 'full_report': out_md,
        'L3_produced': l3.get('produced'),
        'L4_produced': l4.get('produced'),
        'generated': True, 'machine_verified': machine_verified,
        'blocked_class': blocked_class, 'degraded_ok': degraded_ok,
        'review': {'required': sr.get('required'),
                   'seat_invoked': sr.get('seat_invoked'),
                   'verdict': sr.get('verdict'), 'fresh': sr.get('fresh'),
                   'error': sr.get('error'), 'archive': sr.get('archive'),
                   'verdicts_n': sr.get('verdicts_n'),
                   'prior_verdicts': sr.get('prior_verdicts') or [],
                   'record_health': sr.get('record_health') or {}},
        'copies_consistent': copies_consistent,
        'deliverable': deliverable, 'mvp_complete': deliverable,
        'draft_delivered': draft_delivered,
        'draft_blocked_class': blocked_class if draft_delivered else None}
    if _rp18.get('map_question'):
        data['map_report'] = _map18_path
        data['map_renderer_drift'] = map_drift24
        # Audit-R32 正式验收: 本轮重写仅翻新审查状态面(内容段除状态
        # 短语外逐字节不变)——随回执/归档清单可核
        data['map_status_refreshed'] = map_status_refreshed24
        data['map_version'] = (rj.get('research_plan') or {}).get(
            'map_version') or 1
    return deliverable, data, warnings


def _r1_archive_core(args, engine_root):
    """archive 段入口(Audit-R32 任务3): 工单冻结输入核对+钉死→归档核心。

    冻结输入缺件/篡改=拒绝归档(fail-closed,rc≠0,不建归档目录)。"""
    import agent_judgment as _aj_a
    try:
        with _aj_a.work_order_pins(args.report_dir, engine_root) as _pins:
            return _r1_archive_core_pinned(args, engine_root, _pins)
    except _aj_a.WorkOrderPinsError as e:
        # 文案沿用归档既有两族措辞(缺件=「冻结副本运行目录不在场」/
        # 篡改=「冻结件与运行时摘要不符」),既有核验口径不变
        _msg = ('冻结件与运行时摘要不符: ' if e.code == 'frozen_input_tampered'
                else '冻结副本运行目录不在场: ') + e.detail
        return False, {'stage': 'archive', 'blocked':
                       'frozen_inputs_invalid',
                       'frozen_inputs_check': {'ok': False, 'code': e.code,
                                               'detail': e.detail},
                       'error': _msg, 'deliverable': False}, [
            '归档拒绝: ' + _msg]


def _sha_eq_tol(a, b):
    """SHA 比对前缀容忍(印章可能短 SHA,git 恒全 40 位)。"""
    return bool(a and b and (a == b or (len(a) >= 7 and len(b) >= 7
                                        and (a.startswith(b) or b.startswith(a)))))


def _r1_archive_core_pinned(args, engine_root, pins):
    """Audit-R2 条目6: 最终归档=受审版本的完整自包含交付包。

    归档对象=**最终受审版本**: 非 deliverable 一律拒归(先跑 report 门)。
    内容摘要三处核对: content_digest(run 目录)=content_digest(归档目录)
    =最新裁决档 content_sha256——报告、裁决、归档同一摘要锚,不一致即
    拒绝(半写归档目录整体移除,不留毒档)。归档目录 append-only: 已存在
    即拒绝,不覆盖历史。裁链全档随包(verdicts/),失败证据同在。
    """
    import hashlib
    import shutil as _shutil
    import agent_judgment as aj
    import research_orchestrator as ro
    # 经模块级入口(自核对+自钉死;本函数外层 work_order_pins 已置位的键
    # 上游优先不重复置位,嵌套安全)——保持既有可替换缝(R18 §E 等
    # 以 _r1_report_core 为注入点),归档侧仍以本工单 pins 的冻结日历判。
    ok, data, warnings = _r1_report_core(args, engine_root)
    if not ok or not data.get('deliverable'):
        if data.get('blocked') == 'frozen_inputs_invalid':
            return False, dict(data, stage='archive',
                               archive_dir=None), list(warnings or [])
        return False, {'stage': 'archive', 'blocked': 'not_deliverable',
                       'review': data.get('review'),
                       'deliverable': data.get('deliverable')}, \
            (warnings or []) + ['归档拒绝: 可交付门未放行——归档对象='
                                '最终受审版本,先过独立审查']
    rd = args.report_dir
    rj = json.load(open(os.path.join(rd, 'report.json'), encoding='utf-8'))
    # Audit-R18 任务4反例②: 地图问句读者报告缺席=必需交付件缺失,拒归
    if (rj.get('research_plan') or {}).get('map_question') and \
            not os.path.isfile(os.path.join(rd, 'MAP_REPORT.md')):
        return False, {'stage': 'archive',
                       'blocked': 'map_required_face_missing',
                       'note': 'MAP_REPORT.md 缺席(report 段应渲染)'
                       '——必需图表面缺失阻止正式归档'}, \
            (warnings or []) + ['归档拒绝: 地图问句读者报告 MAP_REPORT.md '
                                '缺席(必需图表面缺失)']
    # Audit-R20 任务5反例④: 核心维度(地区×维度组)零 ok 格=草稿面,拒归
    # (与 attach 层 blocked_class_of 同源同判——归档侧 belt、不另立口径)。
    try:
        _bc_r20 = aj.blocked_class_of(
            rj, calendar_path=(pins.get('calendar_path') or os.path.join(
                engine_root, 'config', 'release_calendar.json')))
    except Exception:
        _bc_r20 = None
    if _bc_r20 == 'map_core_dimension_missing':
        _pvx = ((rj.get('research_plan') or {}).get('point_values')
                or {})
        _plp = {(_e, _d) for _e, _rf in
                ((rj.get('research_plan') or {}).get('regions')
                 or {}).items()
                for _d in ((_rf.get('dimensions') or {}) or {})}
        # Audit-R26 验收: 组计算与渲染横幅/attach 判定共源
        # (research_map_planner.missing_core_groups),不另立口径。
        import research_map_planner as _rmp_aj
        _miss = _rmp_aj.missing_core_groups(_pvx, _plp)
        return False, {'stage': 'archive',
                       'blocked': 'map_core_dimension_missing',
                       'missing_groups': sorted(
                           f'{_e}/{_d}' for _e, _d in _miss),
                       'note': '核心维度(地区×维度)整组零 ok 格——'
                               '按用户指令交付草稿,不进正式归档'}, \
            (warnings or []) + ['归档拒绝: 核心维度缺数 '
                                f'{sorted(f"{_e}/{_d}" for _e, _d in _miss)}'
                                '(R20: 草稿可交付,正式归档须 12/12 组齐)']
    # Audit-R21 任务3反例③: 序列在场但一组仅剩最新单点(历史锚空且无经
    # 证实延误依据)=锚覆盖不足——归档侧 belt 同判,零归档增量。
    if _bc_r20 == 'map_anchor_coverage_insufficient':
        _pvx2 = ((rj.get('research_plan') or {}).get('point_values')
                 or {})
        _plp2 = {(_e, _d) for _e, _rf in
                 ((rj.get('research_plan') or {}).get('regions')
                  or {}).items()
                 for _d in ((_rf.get('dimensions') or {}) or {})}
        _sparse_g = [f'{_e}/{_d}' for (_e, _d) in
                     _rmp_aj.sparse_anchor_groups(_pvx2, _plp2)]
        return False, {'stage': 'archive',
                       'blocked': 'map_anchor_coverage_insufficient',
                       'sparse_groups': _sparse_g,
                       'note': '锚覆盖不足: 下列组序列在场但 ok 锚<2 且空锚'
                               '无经证实延误依据——仅存最新单点不构成三时点'
                               '对照,交付草稿不进正式归档'}, \
            (warnings or []) + ['归档拒绝: 锚覆盖不足 ' + str(_sparse_g)
                                + '(R21: 组内 ok 锚≥2 或空锚须有日历实录'
                                '证实依据)']
    run_ts = (rj.get('run') or {}).get('ts_utc') or 'unknown'
    dest = getattr(args, 'archive_dir', None) or os.path.join(
        ROOT, 'research_archive', os.path.basename(rd.rstrip('/')) or run_ts)
    if os.path.exists(dest):
        return False, {'stage': 'archive', 'blocked': 'archive_exists',
                       'archive_dir': dest}, ['归档目录已存在(append-only,'
                                              '不覆盖): ' + dest]
    os.makedirs(dest)
    vd = os.path.join(dest, 'verdicts')
    os.makedirs(vd)
    copies = {}

    def _verdict_copy_name(src_path):
        # Audit-R4 条目4: 跨日同名 basename 冲突——归档名=日目录__basename
        # (全局唯一),日期目录保留在名内;原件路径另记 source_rel
        day = os.path.basename(os.path.dirname(src_path))
        return '%s__%s' % (day, os.path.basename(src_path))

    try:
        _arc_files = ['report.json', 'report.md', 'FULL_REPORT.md',
                      'agent_judgment.json', 'views_digest.json',
                      'evidence_index.json', 'AGENT_SEAT_ENVELOPE.json']
        # Audit-R18: 地图问句读者报告随包归档(读者交付件=归档对象本体)
        # 旁挂锚随包(回读核对=归档侧 sha 与读者侧同锚同判)
        if (rj.get('research_plan') or {}).get('map_question'):
            _arc_files += ['MAP_REPORT.md', 'MAP_REPORT.sha256',
                           'question_verbatim.txt']
        for fname in _arc_files:
            src = os.path.join(rd, fname)
            if os.path.isfile(src):
                _shutil.copy2(src, os.path.join(dest, fname))
                a = open(src, 'rb').read()
                b = open(os.path.join(dest, fname), 'rb').read()
                if a != b:
                    raise OSError('副本核对失败(字节不等): ' + fname)
                copies[fname] = hashlib.sha256(a).hexdigest()[:16]
        # ── Audit-R29 任务4: 渲染依赖随包冻结(root_overlay/)──────────
        # 地图问句包携带运行目录冻结副本(rd/root_overlay/=发布日期历+
        # 运行快照,计划段落位),归档只做逐件字节+摘要核对(与 run.
        # frozen_inputs 比)——运行后被改/副本缺失=拒绝入包;重放以
        # overlay 为重渲 root,与本地日历/快照现状无关。
        frozen_map = {}
        _rj_fi = ((rj.get('run') or {}).get('frozen_inputs') or {})
        if (rj.get('research_plan') or {}).get('map_question') and _rj_fi:
            for _rel, _sha in sorted(_rj_fi.items()):
                _src = os.path.join(rd, 'root_overlay', str(_rel))
                if not os.path.isfile(_src):
                    raise ValueError('冻结副本运行目录不在场: root_overlay/'
                                     '%s(渲染依赖须随包冻结,不得缺席交付;'
                                     '运行目录被清=重跑)' % _rel)
                _dst = os.path.join(dest, 'root_overlay', str(_rel))
                os.makedirs(os.path.dirname(_dst), exist_ok=True)
                _shutil.copy2(_src, _dst)
                if open(_src, 'rb').read() != open(_dst, 'rb').read():
                    raise OSError('冻结件副本核对失败(字节不等): ' + str(_rel))
                _got = hashlib.sha256(
                    open(_dst, 'rb').read()).hexdigest()[:16]
                if _got != str(_sha)[:16]:
                    raise ValueError(
                        '冻结件与运行时摘要不符: %s manifest_run=%s '
                        'actual=%s(运行后被改=归档拒绝,重跑后再归档)'
                        % (_rel, str(_sha)[:16], _got))
                frozen_map[_rel] = _got
        vchain = []
        seen_names = set()
        for p, doc in sorted(
                aj._verdicts_for_run(engine_root, run_ts),
                key=lambda t: aj._verdict_sort_key(t[0], t[1])):
            name = _verdict_copy_name(p)
            # Audit-R4 条目4: 归档前路径冲突检查(同名=链身份破坏,拒绝)
            if name in seen_names or os.path.exists(os.path.join(vd, name)):
                raise OSError('裁决档归档名冲突(非唯一): ' + name)
            seen_names.add(name)
            _shutil.copy2(p, os.path.join(vd, name))
            if open(p, 'rb').read() != open(os.path.join(vd, name),
                                            'rb').read():
                raise OSError('裁决档副本核对失败: ' + name)
            vchain.append({
                'file': 'verdicts/' + name,
                'source_rel': os.path.relpath(p, engine_root),
                'overall': (doc or {}).get('overall'),
                'revision': (doc or {}).get('revision'),
                'predecessor': (doc or {}).get('predecessor'),
                'recorded_at': (doc or {}).get('recorded_at'),
                'sha256': hashlib.sha256(
                    open(p, 'rb').read()).hexdigest()[:16]})
        # ── Audit-R4 条目4: 链完整性核对(数量/唯一/哈希/链关系) ──
        n_src = len(aj._verdicts_for_run(engine_root, run_ts))
        if len(vchain) != n_src or len(seen_names) != n_src:
            raise ValueError('裁决链记录数/唯一性核对失败: 链=%d 唯一名=%d '
                             '源=%d' % (len(vchain), len(seen_names), n_src))
        name_by_source = {e['source_rel']: e['file'] for e in vchain}
        for e in vchain:
            pred = e.get('predecessor')
            if pred is not None and pred not in name_by_source:
                raise ValueError('裁决链 predecessor 不在归档集内: %s -> %r'
                                 % (e['file'], pred))
        # ── 三处摘要核对(run=归档=裁决锚) ──
        sha_run = aj.content_digest(rd)
        sha_arc = aj.content_digest(dest)
        latest = data.get('review') or {}
        arc_vd = None
        if latest.get('archive'):
            arc_vd = os.path.join(
                vd, _verdict_copy_name(
                    os.path.join(engine_root, latest['archive'])))
        latest_doc = _load_json_arc(arc_vd) if arc_vd else None
        sha_bound = (latest_doc or {}).get('content_sha256')
        if not (sha_run == sha_arc and sha_arc == sha_bound):
            raise ValueError('内容摘要三处核对失败: run=%s archive=%s '
                             'bound=%s' % (sha_run[:16], sha_arc[:16],
                                           str(sha_bound)[:16]))
        # ── Audit-R24 任务1: 落盘==裁决核对(地图面) ──
        # 最新裁决带 map_report_sha256 时, 归档 MAP 内容段摘要必须==裁决
        # 绑定(已审正文按原字节读取与归档——report 段冻结已裁内容段,
        # 此处归档侧 belt 复核;不符=归档非受审定稿,拒绝)。legacy 旧档
        # 无地图绑定=历史面如实注记不追溯(manifest 留档)。
        map_bound24 = (latest_doc or {}).get('map_report_sha256')
        map_arc_sha24 = aj.map_report_content_sha(dest)
        # Audit-R32 正式验收: 归档地图与裁决绑定仅差「分工」行尾审查状态
        # 短语(report 段裁决落档后翻新状态面)=同一受审版本——放行并随
        # 清单注记 map_binding_status_equivalent(归档件属性: 与本轮是否
        # 翻新无关——冻结分支下归档先前已翻新的件同样成立);其余不符照旧
        # 拒绝。
        map_binding_equiv = False
        if (rj.get('research_plan') or {}).get('map_question'):
            if map_bound24 and map_arc_sha24 != map_bound24:
                if aj.map_binding_matches(aj._read_map_text(dest),
                                          map_bound24):
                    map_binding_equiv = True
                else:
                    raise ValueError('地图内容段与裁决绑定不符: archive=%s '
                                     'bound=%s(归档非受审定稿)' %
                                     ((map_arc_sha24 or '缺席')[:16],
                                      map_bound24[:16]))
        # ── Audit-R29 任务4: 源摘要匹配终裁──冻结输入集合摘要终裁必须
        # 在档且==归档聚合(席位信封→终裁→归档→重放同算同核;终裁未绑
        # =席位没吃到冻结面输入,交付链不完整,拒绝)。实雷正道修(同
        # 轮): 记录器已机械化自动绑定(席位不抄片段也绑;report 侧单侧
        # 改写由裁决内容摘要门拦,副本侧改写由上方逐件核验拦——两路既
        # 闭,此处只核终裁绑定)。
        _fi_agg = aj.frozen_inputs_digest(frozen_map)
        if frozen_map:
            _v_fi = (latest_doc or {}).get('frozen_inputs_sha256')
            if _v_fi != _fi_agg:
                raise ValueError(
                    '终裁冻结输入摘要不符: verdict=%s archive=%s'
                    '(席位终裁未绑定同一份冻结输入=源摘要失配,拒绝归档;'
                    '席位须以 AGENT_SEAT_ENVELOPE.frozen_inputs_sha256 '
                    '落终裁)' % (str(_v_fi)[:16], str(_fi_agg)[:16]))
        manifest = {
            'stage': 'archive', 'run_ts': run_ts,
            'question': (rj.get('run') or {}).get('question'),
            'archived_at': ro._now_utc(),
            'content_sha256': sha_run,
            # Audit-R22 任务5: 实际运行代码 SHA 随归档清单落档(与
            # report.json run.git_head/MAP_REPORT 头同值,三处可核)
            'run_code_git_head': (rj.get('run') or {}).get('git_head'),
            'digest_algorithm': 'v3(canonical report.json剥离semantic_review'
                                '+canonical agent_judgment.json剥离'
                                'semantic_review+canonical views_digest.json)'
                                ' [Audit-R4 条目2]',
            'verdict': latest.get('verdict'), 'fresh': latest.get('fresh'),
            'verdicts_n': latest.get('verdicts_n'),
            'verdict_chain': vchain, 'copies_sha16': copies,
            # Audit-R29 任务4: 渲染依赖冻结面(地图问句;root_overlay/
            # 布局=包内重渲 root;缺件/篡改/源摘要失配=重放拒)
            'frozen_inputs': frozen_map,
            'frozen_inputs_sha256': _fi_agg,
            'record_health': (data.get('review') or {}).get(
                'record_health') or {},
            'source_report_dir': rd,
            'map_report_sha256': map_bound24,
            'map_content_sha256': map_arc_sha24,
            'map_legacy_no_binding': bool(
                map_bound24 is None
                and (rj.get('research_plan') or {}).get('map_question')),
            'map_renderer_drift': data.get('map_renderer_drift', False),
            'map_version': data.get('map_version', 1),
            'correlation': 'run==archive==verdict-bound(三处一致已核;'
                           '裁决链唯一名逐档哈希+predecessor 链关系已核'
                           ';地图面: 归档内容段==裁决绑定已核/Audit-R24 '
                           '任务1)'}
        if map_binding_equiv:
            # Audit-R32 正式验收: 归档件内容段与裁决绑定仅差状态短语的
            # 归档加注(其余归档清单字节不变)
            manifest['map_binding_status_equivalent'] = True
            manifest['correlation'] = manifest['correlation'].replace(
                '归档内容段==裁决绑定已核/Audit-R24 任务1)',
                '归档内容段==裁决绑定(仅差审查状态短语=状态面等价)已核'
                '/Audit-R32 正式验收)')
        # Audit-R32 正式验收: 裁决后再交付包(运行=执行印章、交付字节=归档
        # 印章,如状态面翻新)随清单落档归档代码 SHA——仅当归档代码≠运行
        # SHA 时加键(同印章归档清单字节不变);重放门④只对已声明状态面
        # 等价的再交付包认归档代码为录制代码,同渲染包仍以运行印章代码
        # 为录制代码(见重放段)
        try:
            _arc_head = ro._git_state(ROOT)[0]
        except Exception:       # noqa: BLE001 印章不可得=不加键
            _arc_head = None
        if _arc_head and not _sha_eq_tol(_arc_head,
                                         manifest['run_code_git_head']):
            manifest['archive_code_git_head'] = _arc_head
            manifest['correlation'] += (
                ';归档代码=%s≠运行代码=%s(裁决后再交付/Audit-R32 正式验收)'
                % (_arc_head[:12], str(manifest['run_code_git_head'])[:12]))
        # Audit-R32 任务1/3: 研究截止日与证据口径块随清单落档(重放/回读
        # 同读;旧档无 run.evidence_gate=不加键,清单字节不变)
        _eg_man = (rj.get('run') or {}).get('evidence_gate')
        if isinstance(_eg_man, dict) and _eg_man:
            manifest['evidence_gate'] = _eg_man
            manifest['evidence_asof'] = (rj.get('run') or {}).get(
                'evidence_asof')
        aj._atomic_write_text(
            os.path.join(dest, 'ARCHIVE_MANIFEST.json'),
            json.dumps(manifest, ensure_ascii=False, indent=2, default=str))
    except (OSError, ValueError) as exc:
        _shutil.rmtree(dest, ignore_errors=True)   # 拒绝交付=不留毒档
        return False, {'stage': 'archive', 'blocked': 'correlation_failed',
                       'error': str(exc)}, ['归档拒绝: ' + str(exc)]
    return True, {'stage': 'archive', 'archive_dir': dest,
                  'content_sha256': sha_run,
                  'verdict': latest.get('verdict'),
                  'verdicts_n': latest.get('verdicts_n'),
                  'files': sorted(copies)}, []


def _load_json_arc(path):
    try:
        return json.load(open(path, encoding='utf-8'))
    except (OSError, ValueError):
        return None


def _r1_replay_core(args, engine_root):
    """Audit-R28 任务4: 离线重放——归档交付包四门自验证+逐字节核对。

    重放对象=archive 段产出的完整交付包(ARCHIVE_MANIFEST.json+九件套+
    地图三件套+verdicts/ 裁决链)。包内自包含重放所需全部输入: 完整运行
    SHA(manifest.run_code_git_head,与 report.json run.git_head 交叉核对)、
    原问(question_verbatim.txt,字节=manifest.question)、冻结输入与快照
    标识(report.json 冻结面+AGENT_SEAT_ENVELOPE.json)、views_digest.json、
    判定(agent_judgment.json)、裁决链(verdicts/ 逐档 sha16)、地图哈希
    (MAP_REPORT.sha256 全文件锚+裁决 map_report_sha256 内容段锚)。

    四道门(任一不过即拒 rc=1,点名细节):
    ① 缺件: 必需件清单逐名在场核验(verdicts/ 按 manifest 链逐档核);
    ② 篡改: manifest.copies_sha16 逐件复算+地图全文件锚+content_digest
       重算+原问逐字节——expected/actual 双值点名;
    ③ 裁决绑定: 链档 sha16+predecessor 关系+最新裁决档 content_sha256
       与 manifest.content_sha256、map_report_sha256 与归档地图内容段
       摘要三面核对;
    ④ 确定性重渲: 以包内冻结输入(report.json+agent_judgment.json+审查
       状态面)按**当前代码**重渲 MAP_REPORT.md,与归档字节逐字节比对。
       代码版本须==manifest.run_code_git_head(逐字节核对只对录制代码
       有意义;--allow-code-mismatch 显式越过并降级为披露;Audit-R32
       正式验收: 清单已声明状态面等价且携 archive_code_git_head 的
       裁决后再交付包,当前代码==归档代码亦成立;同渲染包的录制代码=
       运行印章代码,归档印章代码照旧拒)。manifest
       未声明渲染器漂移(map_renderer_drift=false)时必须逐字节相等;
       声明漂移的包按 R24 纪律以受审冻结字节为准,重渲差异如实披露
       不判负(受审定稿权威)。
       Audit-R29 任务4: 地图包另携渲染依赖冻结面(root_overlay/=发布
       日期历+运行快照,manifest.frozen_inputs 逐件 sha16+聚合 sha256)
       ——在场/摘要/运行面三面核对后,重渲 root 切包内 overlay: 与本地
       日历/快照现状无关(更换本地日历重放仍逐字节一致);最新裁决档
       frozen_inputs_sha256 须==归档聚合(源摘要匹配终裁)。R29 前旧档
       无该键=legacy 重渲 root 不变,零回归。

    输出落独立新目录(--replay-out 或缺省 replay_out/<包名>_<ts>/,
    append-only 已存在即拒;重复运行各开新档,**包内零写入**,写毕复算
    包摘要证原档未动)。"""
    import agent_judgment as aj
    import research_orchestrator as ro
    import research_map_planner as rmp

    pkg = getattr(args, 'package', None)
    if not pkg or not os.path.isdir(pkg):
        return False, {'stage': 'replay', 'blocked': 'bad_args',
                       'note': '--package 缺失或不是目录: %r' % (pkg,)}, \
            ['重放拒绝: --package 缺失或不是目录: %r' % (pkg,)]
    pkg = os.path.abspath(pkg)
    checks = []

    def _chk(name, ok, detail=''):
        checks.append({'check': name, 'ok': bool(ok), 'detail': str(detail)})
        return bool(ok)

    def _sha256_file(path):
        try:
            return hashlib.sha256(open(path, 'rb').read()).hexdigest()
        except OSError:
            return None

    # ── 门0: manifest 在场可解析 ──
    mf_path = os.path.join(pkg, 'ARCHIVE_MANIFEST.json')
    manifest = _load_json_arc(mf_path)
    if not _chk('manifest_present_parseable', bool(manifest), mf_path):
        return False, {'stage': 'replay', 'package': pkg,
                       'blocked': 'manifest_missing_or_corrupt',
                       'checks': checks}, \
            ['重放拒绝: ARCHIVE_MANIFEST.json 缺席或不可解析(' + mf_path
             + ')——包不完整(Audit-R28 任务4 门①)']
    rj = _load_json_arc(os.path.join(pkg, 'report.json')) or {}
    map_q = bool((rj.get('research_plan') or {}).get('map_question'))

    # ── 门①: 缺件(必需清单+裁决链逐档) ──
    base_req = ['ARCHIVE_MANIFEST.json', 'report.json', 'report.md',
                'FULL_REPORT.md', 'agent_judgment.json', 'views_digest.json',
                'evidence_index.json', 'AGENT_SEAT_ENVELOPE.json']
    if map_q:
        base_req += ['MAP_REPORT.md', 'MAP_REPORT.sha256',
                     'question_verbatim.txt']
    missing = [f for f in base_req
               if not os.path.isfile(os.path.join(pkg, f))]
    chain = manifest.get('verdict_chain') or []
    vmiss = [e.get('file') for e in chain
             if not os.path.isfile(os.path.join(pkg, str(e.get('file'))))]
    _chk('completeness_files', not missing and not vmiss,
         '缺件=%s 裁决链缺档=%s' % (missing or '无', vmiss or '无'))
    _chk('verdict_chain_nonempty', bool(chain),
         '链档数=%d(archive 段交付门要求≥1 在案裁决)' % len(chain))

    # ── 门②: 篡改(逐件哈希+地图锚+内容摘要+原问字节) ──
    copies = manifest.get('copies_sha16') or {}
    tamper = []
    for fname, want in sorted(copies.items()):
        got = _sha256_file(os.path.join(pkg, fname))
        got16 = got[:16] if got else None
        if got16 != want:
            tamper.append('%s: manifest=%s actual=%s'
                          % (fname, want, got16))
    unrecorded = [f for f in base_req
                  if f != 'ARCHIVE_MANIFEST.json' and f not in copies]
    _chk('copies_sha16_match', not tamper and not unrecorded,
         '哈希不符=%s 清单漏记=%s' % (tamper or '无', unrecorded or '无'))
    if map_q:
        anchor = None
        try:
            anchor = open(os.path.join(pkg, 'MAP_REPORT.sha256'),
                          encoding='utf-8').read().strip().split(' ', 1)[0]\
                or None
        except OSError:
            pass
        disk = _sha256_file(os.path.join(pkg, 'MAP_REPORT.md'))
        _chk('map_fullfile_anchor', anchor and disk and anchor == disk,
             '锚=%s 实测=%s(旁挂锚=防单改在场文件)' %
             ((anchor or '缺席')[:16], (disk or '缺席')[:16]))
        qv = None
        try:
            qv = open(os.path.join(pkg, 'question_verbatim.txt'),
                      'rb').read()
        except OSError:
            pass
        qv_want = str(manifest.get('question') or '').encode('utf-8')
        _chk('question_verbatim_bytes', qv is not None and qv == qv_want,
             '包内原问 %d 字节 vs manifest.question %d 字节(逐字节)'
             % (len(qv) if qv is not None else -1, len(qv_want)))
    # ── Audit-R29 任务4: 渲染依赖冻结面(root_overlay/)──────────────
    # 门①冻结件在场+门②逐件摘要复算+运行面三面核对;门④重渲 root 切
    # overlay(与本地日历/快照现状无关——更换本地日历重放仍逐字节一致)。
    # 旧档(R29 前)无 frozen_inputs 键=legacy 行为不变(root=engine_root
    # 重渲,零回归);终裁源摘要匹配=最新裁决 frozen_inputs_sha256 须在
    # 档且==归档聚合(席位信封→终裁→归档→重放同算同核)。
    fi = manifest.get('frozen_inputs') or {}
    overlay_root = None
    if fi:
        fmiss = [rel for rel in fi
                 if not os.path.isfile(os.path.join(pkg, 'root_overlay',
                                                    str(rel)))]
        _chk('frozen_inputs_present', not fmiss,
             'overlay 缺件=%s(root_overlay/ 布局=渲染依赖随包冻结)'
             % (fmiss or '无'))
        fbad = []
        for rel, want in sorted(fi.items()):
            _p = os.path.join(pkg, 'root_overlay', str(rel))
            got = (_sha256_file(_p) or '')[:16]
            if got != str(want)[:16]:
                fbad.append('%s: manifest=%s actual=%s'
                            % (rel, str(want)[:16], got or '缺席'))
        _chk('frozen_inputs_digests', not fbad,
             '冻结件摘要不符=%s' % (fbad or '无'))
        rfi = ((rj.get('run') or {}).get('frozen_inputs') or {})
        _d = (('run.frozen_inputs=%s manifest=%s(渲染依赖身份三面之一;'
               '失配=包或报告被单侧改写)'
               % (sorted(rfi.items()), sorted(fi.items())))
              if rfi != fi else '一致')
        _chk('frozen_inputs_match_report', rfi == fi, _d)
        if not fmiss and not fbad:
            overlay_root = os.path.join(pkg, 'root_overlay')
    head_mf = manifest.get('run_code_git_head')
    head_rj = (rj.get('run') or {}).get('git_head')
    # Audit-R28 任务4: R28 前旧档 manifest 无 run_code_git_head 键
    # (未记录≠矛盾)——严格口径照旧拒;--allow-code-mismatch 下随披露
    # 降级(旧档代码身份本就走该旗标的披露路径,不为旧档放宽严格面)。
    _xchk_ok = bool(head_mf and head_mf == head_rj) or (
        head_mf is None and head_rj
        and getattr(args, 'allow_code_mismatch', False))
    _chk('run_code_sha_crosscheck', _xchk_ok,
         'manifest=%s report.json.run=%s(完整运行 SHA 两处一致%s)'
         % (head_mf or '缺席', head_rj or '缺席',
            ';旧档未记录键,--allow-code-mismatch 披露降级'
            if head_mf is None and _xchk_ok else ''))
    try:
        digest_now = aj.content_digest(pkg)
    except Exception as exc:                      # noqa: BLE001
        digest_now = 'error:%r' % (exc,)
    _chk('content_digest_match', digest_now == manifest.get('content_sha256'),
         '重算=%s manifest=%s(摘要算法=manifest.digest_algorithm)'
         % (str(digest_now)[:16],
            str(manifest.get('content_sha256'))[:16]))

    # ── 门③: 裁决绑定(链哈希+predecessor+最新档双锚) ──
    vbad = []
    src_names = {str(e.get('source_rel')) for e in chain}
    for e in chain:
        vf = str(e.get('file'))
        got16 = (_sha256_file(os.path.join(pkg, vf)) or '')[:16]
        if got16 != e.get('sha256'):
            vbad.append('%s: manifest=%s actual=%s'
                        % (vf, e.get('sha256'), got16 or '缺席'))
        pred = e.get('predecessor')
        # predecessor=源树 source_rel(与 archive 段链关系核对同口径),
        # 须落在归档链的 source_rel 集合内
        if pred is not None and pred not in src_names:
            vbad.append('%s: predecessor=%r 不在归档链内'
                        % (vf, pred))
    _chk('verdict_chain_hashes', not vbad, '链档异常=%s' % (vbad or '无'))
    latest_doc, bind_bad = None, []
    _bind_note = False
    if chain:
        # vchain 落 manifest 时已按写入序排序(archive 段),链尾=最新
        latest_e = chain[-1]
        latest_doc = _load_json_arc(
            os.path.join(pkg, str(latest_e.get('file')))) or {}
        if latest_doc.get('content_sha256') != manifest.get('content_sha256'):
            bind_bad.append('最新裁决 content_sha256=%s ≠ manifest=%s'
                            % (str(latest_doc.get('content_sha256'))[:16],
                               str(manifest.get('content_sha256'))[:16]))
        if map_q:
            map_sha_now = aj.map_report_content_sha(pkg)
            bound = latest_doc.get('map_report_sha256')
            # Audit-R32 正式验收: 包内地图与裁决绑定仅差「分工」行尾审查
            # 状态短语时,须清单已声明 map_binding_status_equivalent——
            # 声明与实际互核(不同而未声明=异常;已声明而不等价或无差异=
            # 异常)
            _declared = bool(manifest.get('map_binding_status_equivalent'))
            _state_eq = bool(
                bound and map_sha_now != bound
                and aj.map_binding_matches(aj._read_map_text(pkg), bound))
            if bound and map_sha_now != bound and not (
                    _declared and _state_eq):
                bind_bad.append('地图内容段=%s ≠ 裁决绑定=%s'
                                % ((map_sha_now or '缺席')[:16],
                                   bound[:16]))
            if _declared and not _state_eq:
                bind_bad.append('map_binding_status_equivalent 声明与实际'
                                '不符(内容段=%s 绑定=%s)'
                                % ((map_sha_now or '缺席')[:16],
                                   str(bound)[:16]))
            _bind_note = _state_eq
            if map_sha_now != manifest.get('map_content_sha256'):
                bind_bad.append('地图内容段=%s ≠ manifest.map_content_sha256'
                                '=%s' % ((map_sha_now or '缺席')[:16],
                                         str(manifest.get(
                                             'map_content_sha256'))[:16]))
        if fi:
            # Audit-R29 任务4: 源摘要匹配终裁——最新裁决档冻结输入摘要
            # 须在档且==归档聚合(缺席/失配=席位终裁未绑同一份输入)
            v_fi = (latest_doc or {}).get('frozen_inputs_sha256')
            if v_fi != manifest.get('frozen_inputs_sha256'):
                bind_bad.append('终裁冻结输入摘要=%s ≠ manifest=%s'
                                % ((str(v_fi)[:16] if v_fi else '缺席'),
                                   str(manifest.get(
                                       'frozen_inputs_sha256'))[:16]))
    _chk('verdict_binding_threeway', not bind_bad,
         '绑定异常=%s' % (bind_bad or (
             '无(run=归档=裁决锚三面一致%s)' % (
                 ';地图内容段与裁决绑定仅差审查状态短语,清单已声明'
                 if _bind_note else ''))))

    # ── 门④: 代码版本+确定性重渲逐字节核对 ──
    # 代码身份=**本次重放进程实际运行的代码树**(ia_cli 所在 ROOT,非
    # engine_root 数据树)——git 库优先,git archive 干净树回落
    # CODE_VERSION.json 印章(与 orchestrator._git_state 三级链同源;
    # ROOT 即代码树时 run_root=code_tree 同级命中,印章为终级)。
    # SHA 比对前缀容忍(印章可能短 SHA,git 恒全 40 位)。
    cur_head, _cur_src, _cur_dirty = ro._git_state(ROOT)
    _sha_eq = _sha_eq_tol
    code_match = _sha_eq(cur_head, head_mf)
    # Audit-R32 正式验收: 裁决后再交付包(运行 SHA=执行印章;状态面由归档
    # 印章翻新,清单 map_binding_status_equivalent+archive_code_git_head 已
    # 声明)——当前代码==归档代码时同为"录制代码"(逐字节核对的对象正是
    # 归档代码所产交付字节);其余异版照旧拒。同渲染包(运行印章渲染时
    # 裁决已在场,清单携 archive_code_git_head 而无状态面等价声明):交付
    # 字节全由运行印章代码所产,录制代码=运行印章代码——归档印章代码照旧
    # 拒(归档≠录制: 否则任一旧运行目录经新代码归档即可绕过版本门;
    # --allow-code-mismatch 显式越过并披露)。
    _arc_head = manifest.get('archive_code_git_head')
    _redeliv = bool(not code_match and _arc_head
                    and manifest.get('map_binding_status_equivalent')
                    and _sha_eq(cur_head, _arc_head))
    if not code_match and not _redeliv \
            and not getattr(args, 'allow_code_mismatch', False):
        return False, {'stage': 'replay', 'package': pkg,
                       'blocked': 'code_version_mismatch',
                       'checks': checks,
                       'note': '当前代码 HEAD=%s ≠ 包记录运行 SHA=%s——'
                               '逐字节核对只对录制代码有意义;确要以异版'
                               '代码重放须 --allow-code-mismatch(降级为'
                               '披露)%s'
                               % (cur_head or '(git 不可用)',
                                  head_mf or '缺席',
                                  ';清单另记归档代码 %s(同渲染包: 交付'
                                  '字节即运行印章渲染,须以运行印章代码'
                                  '严格重放)' % _arc_head
                                  if (_arc_head and not manifest.get(
                                      'map_binding_status_equivalent'))
                                  else '')}, \
            ['重放拒绝: 代码版本不符——当前=%s 包=%s(Audit-R28 任务4 门④)'
             % (cur_head or '(git 不可用)', head_mf or '缺席')]
    _chk('code_version_match',
         code_match or _redeliv
         or getattr(args, 'allow_code_mismatch', False),
         '当前=%s 包=%s%s' % (cur_head or '(git 不可用)', head_mf or '缺席',
                              '' if code_match
                              else ('(当前=归档代码 %s: 裁决后再交付包,清单已'
                                    '声明)' % _arc_head if _redeliv
                                    else '(--allow-code-mismatch 披露越过)')))
    render_mode = 'not_map_question'
    if map_q:
        aj_doc = _load_json_arc(
            os.path.join(pkg, 'agent_judgment.json')) or {}
        # 审查状态面从包内重建(渲染尾部唯一消费 verdict/verdicts_n 两键,
        # 与 report 段 sr 同源同值——manifest 两字段即 sr 落档值)
        sr_mini = {'verdict': manifest.get('verdict'),
                   'verdicts_n': manifest.get('verdicts_n')}
        try:
            # Audit-R29 任务4: 重渲 root=包内冻结 overlay(R29+ 包)——
            # 与本地日历/快照现状无关;legacy 旧档无 overlay 时沿用
            # engine_root(旧行为,零回归)。
            # Audit-R32 任务3: 重渲同样经工单冻结输入核对+钉死(日历/
            # 注册表/源快照=包内 overlay;IA_EVIDENCE_ASOF=清单/报告所记
            # 研究截止日)——引擎本地日历被换不影响重放字节;overlay 缺
            # 件/篡改=核对失败→render_error(fail-closed)。
            with aj.work_order_pins(pkg, engine_root):
                map_text = rmp.render_map_report(
                    rj, aj_doc, sr_mini,
                    root=(overlay_root or engine_root))
            archived = open(os.path.join(pkg, 'MAP_REPORT.md'),
                            'rb').read()
            byte_equal = map_text.encode('utf-8') == archived
        except Exception as exc:                  # noqa: BLE001
            map_text, archived, byte_equal = None, None, False
            _chk('deterministic_rerender', False,
                 '重渲异常: %r' % (exc,))
            render_mode = 'render_error'
        else:
            drift_declared = bool(manifest.get('map_renderer_drift'))
            if byte_equal:
                render_mode = 'byte_equal'
                _chk('deterministic_rerender', True,
                     '冻结输入按当前代码重渲与归档 MAP_REPORT.md '
                     '逐字节相等(%d 字节)' % len(archived))
            elif drift_declared:
                render_mode = 'drift_disclosed'
                _chk('deterministic_rerender', True,
                     'manifest 声明渲染器漂移(map_renderer_drift=true)'
                     '——受审冻结字节权威(R24 纪律),重渲差异披露不判负')
            else:
                _chk('deterministic_rerender', False,
                     '重渲≠归档字节而 manifest 未声明漂移——包或代码'
                     '一致性存疑(重渲 sha16=%s 归档 sha16=%s)'
                     % ((hashlib.sha256(
                         map_text.encode('utf-8')).hexdigest())[:16],
                        (hashlib.sha256(archived)).hexdigest()[:16]))

    # ── 汇总+落档(独立新目录,包内零写入) ──
    ok = all(c['ok'] for c in checks)
    out_dir = getattr(args, 'replay_out', None)
    if out_dir is None:
        out_dir = os.path.join(
            os.path.dirname(pkg), 'replay_out',
            '%s_%s' % (os.path.basename(pkg.rstrip('/')) or 'pkg',
                       ro._now_utc()))
    if os.path.exists(out_dir):
        return False, {'stage': 'replay', 'package': pkg,
                       'blocked': 'replay_out_exists', 'checks': checks,
                       'replay_out': out_dir}, \
            ['重放拒绝: 输出目录已存在(append-only 不覆盖): ' + out_dir]
    os.makedirs(out_dir)
    # 写毕后复算包内关键摘要,证重放零写入、原档保留
    post_pkg_digest = None
    try:
        post_pkg_digest = aj.content_digest(pkg)
    except Exception as exc:                      # noqa: BLE001
        post_pkg_digest = 'error:%r' % (exc,)
    untouched = post_pkg_digest == manifest.get('content_sha256')
    checks.append({'check': 'package_untouched_postwrite',
                   'ok': bool(untouched),
                   'detail': '写毕复算包摘要=%s(与 manifest 一致=原档'
                             '未被重放触碰)' % str(post_pkg_digest)[:16]})
    ok = ok and untouched
    replay_doc = {
        'stage': 'replay', 'package': pkg, 'replayed_at': ro._now_utc(),
        'replay_code_head': cur_head, 'package_run_head': head_mf,
        'question': manifest.get('question'),
        'verdict': manifest.get('verdict'), 'verdicts_n':
            manifest.get('verdicts_n'),
        'render_mode': render_mode, 'checks': checks, 'ok': ok,
        'command': ('python3 ia_cli.py research-one --stage replay '
                    '--package %s' % pkg)}
    if _arc_head:
        # Audit-R32 正式验收: 裁决后再交付包随重放报告落档归档代码 SHA
        # (旧档无此键=重放报告字节不变)
        replay_doc['package_archive_head'] = _arc_head
    aj._atomic_write_text(
        os.path.join(out_dir, 'REPLAY_REPORT.json'),
        json.dumps(replay_doc, ensure_ascii=False, indent=2, default=str))
    lines = ['# 离线重放报告(Audit-R28 任务4)', '',
             '- 交付包: `%s`' % pkg,
             '- 完整运行 SHA: `%s`(当前重放代码 `%s`)' % (head_mf,
                                                        cur_head or '(?)'),
             '- 原问: %s' % (manifest.get('question') or '(未记录)'),
             '- 裁决: %s(链 %s 档)' % (manifest.get('verdict'),
                                          manifest.get('verdicts_n')),
             '- 重渲模式: %s' % render_mode, '', '## 检查明细', '']
    if _arc_head:
        # 注记按实际放行路径写: 严格放行且当前代码=归档代码(清单已声明
        # 状态面等价)/严格放行且当前代码=运行印章代码(录制代码)/异版代码
        # 经 --allow-code-mismatch 越过版本门(只作披露,不写该声明)
        if _redeliv:
            _note = ('(裁决后再交付包: 运行=执行印章、交付字节=归档印章;'
                     '清单已声明状态面等价)')
        elif code_match:
            _note = '(清单另记归档代码;本次由运行印章代码=录制代码严格重放)'
        else:
            _note = ('(裁决后再交付包;本次为异版代码经 --allow-code-mismatch '
                     '越过版本门后的披露性重放,非录制代码)')
        lines[4:4] = ['- 归档代码 SHA: `%s`%s' % (_arc_head, _note)]
    for c in checks:
        lines.append('- [%s] %s%s' % ('PASS' if c['ok'] else 'FAIL',
                                      c['check'],
                                      ('——' + c['detail']) if c.get('detail')
                                      else ''))
    lines += ['', '## 结论', '',
              '重放%s: %d 项检查 %d 过 %d 拒。' % (
                  '通过' if ok else '拒绝', len(checks),
                  sum(1 for c in checks if c['ok']),
                  sum(1 for c in checks if not c['ok'])),
              '重复运行另开新档,原包未写入(post-write 摘要复核在档)。']
    aj._atomic_write_text(
        os.path.join(out_dir, 'REPLAY_REPORT.md'),
        '\n'.join(lines) + '\n')
    if map_q and map_text is not None:
        aj._atomic_write_text(
            os.path.join(out_dir, 'MAP_REPLAY_RENDER.md'), map_text)
    return ok, {'stage': 'replay', 'package': pkg, 'replay_out': out_dir,
                'render_mode': render_mode, 'ok': ok,
                'failed_checks': [c['check'] for c in checks
                                  if not c['ok']],
                'checks': checks, 'checks_n': len(checks),
                'command': replay_doc['command']}, \
        ([] if ok else ['重放拒绝: ' + '; '.join(
            '%s(%s)' % (c['check'], c['detail']) for c in checks
            if not c['ok'])])


def cmd_research_one(args):
    """一键研究 MVP 单入口(Product Convergence Phase 3/章程§五)。

    自然语言问题→[plan] research-run 证据面+Agent 席工单→(Agent Native 席
    真产 L3/L4,禁 produced 造假)→[attach] 纪律校验+合并→[report] 完整报告。

    三段式而非单进程: L3/L4 恒由 Agent 席(Agent Native)产生——本命令是
    零模型编排层,plan 段产出 AGENT_SEAT_ENVELOPE(工单),attach 段只验
    纪律不代写。--engine-root 注入真实数据树(测试/净环境用注入缝)。

    Audit-R1 F09 --stage auto: 单命令全自动链 plan→attach→report——
    judgment 在场则一命令贯通至 FULL_REPORT;缺席则停 plan 段并给
    Agent 席工单(Agent Native 暂停点,零模型不代写判断,如实披露)。"""
    engine_root = getattr(args, 'engine_root', None) or ROOT
    stage = getattr(args, 'stage', 'plan')

    if stage == 'auto':
        # F09 单命令全自动链 + Audit-R2 条目6(一次输入到最终归档):
        # 幂等续链机——每轮自动推进到最远可自主段,人/席位边界如实暂停。
        # 恢复语义: --report-dir 指既有 run 目录=续链不重新 plan;已 attach
        # 且无新 --judgment=不重挂(重挂改写 attach 台账→摘要变→无谓作废
        # 在案裁决绑定)。归档: deliverable 后携 --archive-dir 即链尾直归。
        if not getattr(args, 'question', None) and \
                not getattr(args, 'report_dir', None):
            emit(envelope('research-one', False, {'stage': 'auto'},
                          error=('bad_args',
                                 'auto 段需 --question(新链)或 --report-dir'
                                 '(恢复既有 run)', None)),
                 exit_code=1)
            return
        chain = []
        rd = getattr(args, 'report_dir', None)
        resuming = bool(rd and os.path.isfile(os.path.join(rd, 'report.json')))
        if resuming:
            chain.append({'stage': 'plan', 'ok': None, 'resumed': True,
                          'report_dir': rd,
                          'note': '恢复既有 run(--report-dir 在场), 不重新 plan'})
        else:
            rep, rd, err = _r1_plan_core(args, engine_root)
            if err:
                emit(envelope('research-one', False, {'stage': 'auto',
                                                      'chain': [
                        {'stage': 'plan', 'ok': False,
                         'error': list(err)}]}, error=err),
                     exit_code=1)
                return
            chain.append({'stage': 'plan', 'ok': bool(rep.get('run_ok')),
                          'report_dir': rd, 'run_ok': rep.get('run_ok'),
                          'agent_seat_envelope': os.path.join(
                              rd, 'AGENT_SEAT_ENVELOPE.json')})
        rj = json.load(open(os.path.join(rd, 'report.json'),
                            encoding='utf-8'))
        _ly = rj.get('layers') or {}
        already = bool(
            (_ly.get('L3_AI推断层') or {}).get('produced')
            and (_ly.get('L4_条件情景层') or {}).get('produced')
            and (rj.get('agent_judgment') or {}).get('attached'))
        _pstatus, _pgaps = _r1_plan_gaps(rj)
        # Audit-R33 任务3: 计划缺口(hard)=零事实/缺必要计划/分面块缺席——
        # 显式点名、链不推进到 report/archive,不以「待裁暂停」口径放行。
        # 拦的对象是**尚未落位**的 run: 已 attach 的续链不重新裁计划缺口
        # (在案裁决的摘要绑定不因事后口径变化作废——R2 条目6 续链契约);
        # 例外=缺口工单携 judgment 落位时落下的保持标记(见下),续链照拦。
        _hold = os.path.isfile(os.path.join(rd, 'PLAN_GAP_HOLD.json'))
        _gap = bool(_pstatus == 'gap' and (not already or _hold))
        _gcode = _pgaps[0]['code'] if _pgaps else None
        _gdet = _pgaps[0]['detail'] if _pgaps else ''

        def _gap_row(held, note):
            return {'stage': 'plan_gap', 'ok': False, 'held': bool(held),
                    'plan_status': _pstatus, 'plan_gaps': _pgaps,
                    'note': note}

        if _gap and already and not getattr(args, 'judgment', None):
            # 已落位+保持标记在案+无新 judgment: 不推进(already 不豁免)
            chain.append(_gap_row(
                True, '计划缺口(保持标记在案)——已落位亦不推进到 report/'
                      'archive(缺口口径先于落位结果;补齐后重跑 plan 生成新 run)'))
            emit(envelope('research-one', False,
                          {'stage': 'auto', 'chain': chain},
                          error=('plan_gap', _gcode, _gdet)), exit_code=1)
            return
        if not getattr(args, 'judgment', None) and not already:
            if _gap:
                chain.append(_gap_row(
                    False, '计划缺口——链不推进到 report/archive(补齐授权'
                           '范围内数据/修正问句后重跑)'))
            chain.append({'stage': 'pause', 'ok': None,
                          'note': (
                              '计划缺口(%s)在案——席位不应对缺口工单产 '
                              'L3/L4;补齐授权范围内数据/修正问句后重跑。'
                              % _gcode if _gap else '')
                          + 'judgment 缺席——Agent Native 暂停点: '
                            'Agent 席按工单真产 L3/L4 后携 --judgment '
                            '以 --report-dir 续链 auto'})
            emit(envelope('research-one', False, {
                'stage': 'auto', 'chain': chain,
                'next': (('计划缺口: %s(补齐授权范围内数据/修正问句后'
                          '重跑);补齐后 ' % _gdet) if _gap else '')
                        + 'Agent 席按 AGENT_SEAT_ENVELOPE.json 真产 judgment → '
                          '--stage auto --report-dir <rd> --judgment <path> '
                          '续链(不重新 plan)'},
                error=(('plan_gap', _gcode, _gdet) if _gap else None)),
                 exit_code=1)
            return
        if getattr(args, 'judgment', None) or not already:
            args.report_dir = rd
            res, err = _r1_attach_core(args, engine_root)
            if err or not (res or {}).get('attached'):
                chain.append({'stage': 'attach', 'ok': False,
                              'error': list(err) if err else 'attached=false',
                              'blocked': (res or {}).get('blocked'),
                              'violations': ((res or {}).get('validation')
                                             or {}).get('violations')})
                if _gap:
                    chain.append(_gap_row(
                        _hold, '计划缺口在案——正式 attach 拒收,链不推进到 '
                               'report/archive(补齐授权范围内数据/修正问句后'
                               '重跑)'))
                emit(envelope('research-one', False,
                              {'stage': 'auto', 'chain': chain},
                              error=(('plan_gap', _gcode, _gdet) if _gap
                                     else err or (
                                         'attach_blocked',
                                         str((res or {}).get('blocked')),
                                         None))),
                     exit_code=1)
                return
            chain.append({'stage': 'attach', 'ok': True,
                          'validation_passed': (res.get('validation') or
                                                {}).get('passed')})
            if _gap:
                # 缺口工单携 judgment 竟落位(attach 校验未拦)——缺口口径先于
                # 落位结果: 不推进到 report;落保持标记,此后无 judgment 续链
                # 同样拦(already 不再豁免),补齐后重跑 plan 生成新 run。
                from datetime import datetime as _dt_g
                try:
                    with open(os.path.join(rd, 'PLAN_GAP_HOLD.json'), 'w',
                              encoding='utf-8') as _fh:
                        json.dump({'code': _gcode, 'detail': _gdet,
                                   'plan_status': _pstatus,
                                   'recorded_at': _dt_g.now().astimezone()
                                   .isoformat(timespec='seconds')}, _fh,
                                  ensure_ascii=False, indent=2)
                except OSError:
                    pass
                chain.append(_gap_row(
                    True, '缺口工单携 judgment 落位——链不推进到 report/'
                          'archive(缺口口径先于落位结果;补齐后重跑 plan '
                          '生成新 run)'))
                emit(envelope('research-one', False,
                              {'stage': 'auto', 'chain': chain},
                              error=('plan_gap', _gcode, _gdet)), exit_code=1)
                return
        else:
            chain.append({'stage': 'attach', 'ok': True, 'skipped': True,
                          'note': '已落位且无新 judgment——不重挂'
                                  '(保在案裁决的摘要绑定)'})
        ok, data, warns = _r1_report_core(args, engine_root)
        chain.append({'stage': 'report', 'ok': ok,
                      'deliverable': data.get('deliverable'),
                      'draft_delivered': data.get('draft_delivered'),
                      'draft_blocked_class': data.get('draft_blocked_class'),
                      'review': data.get('review'),
                      'full_report': data.get('full_report')})
        if not ok and not data.get('draft_delivered'):
            # 独立审查面未放行(缺席/REVISE/裁决链非法/副本不一致)=席位
            # 暂停点,零模型编排层不代裁——复验落新裁决档后重跑 auto 续链
            chain.append({'stage': 'review_pause', 'ok': None,
                          'note': '可交付门未放行(见 report 段 review)——'
                                  '独立席位复验落新裁决档后重跑 auto '
                                  '--report-dir 续链(不重新 plan)'})
            data = dict(data, stage='auto', chain=chain)
            emit(envelope('research-one', False, data, warns or None),
                 exit_code=1)
            return
        if data.get('draft_delivered') and not data.get('deliverable'):
            # Audit-R25 任务1: 带缺口草稿交付(exit 0=读者拿到草稿地图);
            # 正式归档仍阻断(archive belt 对 map_core_dimension_missing/
            # map_anchor_coverage_insufficient 同判拒)——补数后重跑续链
            chain.append({'stage': 'archive', 'ok': None,
                          'note': '草稿交付(数据面缺口 %s)——正式归档仍'
                                  '阻断;补数后重跑 auto --report-dir 续链'
                                  % data.get('draft_blocked_class')})
            data = dict(data, stage='auto', chain=chain)
            emit(envelope('research-one', True, data, warns or None),
                 exit_code=0)
            return
        if getattr(args, 'archive_dir', None):
            aok, adata, awarns = _r1_archive_core(args, engine_root)
            chain.append({'stage': 'archive', 'ok': aok,
                          'archive_dir': adata.get('archive_dir'),
                          'content_sha256': adata.get('content_sha256'),
                          'blocked': adata.get('blocked')})
            ok = bool(ok and aok)
            warns = list(warns or []) + list(awarns or [])
        else:
            chain.append({'stage': 'archive', 'ok': None,
                          'note': 'deliverable=true——归档经 --archive-dir '
                                  '<dir> 随本命令直归,或 --stage archive '
                                  '--archive-dir <dir> 单段归档'})
        data = dict(data, stage='auto', chain=chain)
        emit(envelope('research-one', ok, data, warns or None),
             exit_code=0 if ok else 1)
        return

    if stage == 'plan':
        rep, rd, err = _r1_plan_core(args, engine_root)
        if err:
            emit(envelope('research-one', False, {'stage': 'plan'}, error=err),
                 exit_code=1)
            return
        # Audit-R33 任务3: 计划缺口显式化——零事实/缺必要计划=plan_status=
        # gap,ok=False、rc=1、next 点名缺口(不再以 ok=True+零指标计划放行)
        _pstatus, _pgaps = _r1_plan_gaps(rep)
        _pok = bool(rep.get('run_ok')) and _pstatus == 'ok'
        _draft = [g for g in _pgaps if g.get('severity') == 'draft']
        _next = ('计划缺口: ' + _pgaps[0]['detail']
                 + '(补齐授权范围内数据/修正问句后重跑)'
                 if _pstatus == 'gap' else
                 'Agent 席按 AGENT_SEAT_ENVELOPE.json 真产 L3/L4 → attach 段'
                 + (';计划缺口(草稿级): ' + _draft[0]['detail']
                    if _draft else ''))
        emit(envelope('research-one', _pok, {
            'stage': 'plan', 'report_dir': rd, 'run_ok': rep.get('run_ok'),
            'plan_status': _pstatus, 'plan_gaps': _pgaps,
            'agent_seat_envelope': os.path.join(rd, 'AGENT_SEAT_ENVELOPE.json'),
            'L3_produced': rep['layers']['L3_AI推断层']['produced'],
            'L4_produced': rep['layers']['L4_条件情景层']['produced'],
            'next': _next}),
             exit_code=(1 if _pstatus == 'gap' else 0))
        return

    if stage == 'attach':
        res, err = _r1_attach_core(args, engine_root)
        if err:
            emit(envelope('research-one', False, {'stage': 'attach'}, error=err),
                 exit_code=1)
            return
        # 退出码口径(冻结契约: R18 §D / R1-F09 §B2 / R2 条目6): rc=命令是否
        # 执行,拒收=rc 0 + ok False + attached False + violations(落位与否读
        # 信封 data.attached,不读 rc);rc≠0 只留命令级失败。Audit-R33 任务3
        # 曾把拒收改成 rc=1,全量电池证实破坏在案契约(脚本链以
        # rc==0 且 attached False 认拒收)——已回滚,拒收理由照常落
        # data.violations / data.blocked。
        emit(envelope('research-one', bool(res.get('attached')), {
            'stage': 'attach', 'report_dir': res.get('report_dir'),
            'attached': res.get('attached'),
            'blocked': res.get('blocked'),
            'blocked_class': res.get('blocked_class'),
            'validation_passed': (res.get('validation') or {}).get('passed'),
            'violations': (res.get('validation') or {}).get('violations')}))
        return

    if stage == 'report':
        ok, data, warns = _r1_report_core(args, engine_root)
        emit(envelope('research-one', ok, data, warns or None),
             exit_code=0 if ok else 1)
        return

    if stage == 'replay':
        # Audit-R28 任务4: 离线重放段(交付包四门自验证+确定性重渲
        # 逐字节核对;输出独立新目录,包内零写入)
        rok, rdata, rwarns = _r1_replay_core(args, engine_root)
        emit(envelope('research-one', rok, rdata, rwarns or None),
             exit_code=0 if rok else 1)
        return

    if stage == 'archive':
        # Audit-R2 条目6: 最终归档段(归档对象=最终受审版本,摘要三处核对)
        if not getattr(args, 'report_dir', None):
            emit(envelope('research-one', False, {'stage': 'archive'},
                          error=('bad_args', 'archive 段需 --report-dir',
                                 None)),
                 exit_code=1)
            return
        aok, adata, awarns = _r1_archive_core(args, engine_root)
        emit(envelope('research-one', aok, adata, awarns or None),
             exit_code=0 if aok else 1)
        return


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
    ar.add_argument('--snapshot-id',
                    help='save: 显式绑定快照(默认最新;研究基于旧版时须指定,'
                         '如 research_snapshot_20261110_v4 或短形 20261110_v4)')

    vw = sub.add_parser('views',
                        help='机构观点存储(Charter8): list 摘要 / get 单份(合规件) / lint 违规明细')
    vw.add_argument('action', choices=['list', 'get', 'lint'])
    vw.add_argument('--view-id', help='get: VIEW-YYYYMMDD-NNN(隔离件拒绝并给原因)')
    vw.add_argument('--verify-urls', action='store_true',
                    help='lint: 追加 source_url 活性核验(**联网档位**,默认关;'
                         '不可达≠伪造,只披露不隔离)')
    vw.add_argument('--url-timeout', type=int, default=10,
                    help='--verify-urls 单请求超时秒数(默认 10)')

    rmp = sub.add_parser('research-map',
                         help='研究地图: 章程§五十问确定性扇出证据包'
                              '(数据面+命令清单+提名原料+ART/观察钟透传;零模型)')
    rmp.add_argument('--views-dir', default=None,
                     help='views 目录注入缝(默认 data/institutions/views;测试用)')

    rr = sub.add_parser('research-run',
                        help='一键研究编排(R2/AC6): 十一步确定性管线,零模型;'
                             'L3 AI推断/L4 条件情景恒 declared-not-produced')
    rr.add_argument('--question', default=None,
                    help='研究问题原文(与 --question-file 二选一)')
    rr.add_argument('--question-file', default=None,
                    help='原问逐字文件(Audit-R25 任务3: 优先于 --question,'
                         '字节直读免手打重排标点;仅去尾部换行)')
    rr.add_argument('--archive', action='store_true',
                    help='落档(Skill 第 11 步=用户认可后;默认关)')
    rr.add_argument('--out-dir', default=None,
                    help='报告目录注入缝(默认 output/research_runs/<ts>_<slug>)')
    rr.add_argument('--fanout', action='store_true',
                    help='R3 十问扇出: research_map 十问命令清单逐条真跑'
                         '(Agent 层问 RQ3/RQ9 declared-not-produced)')

    r1 = sub.add_parser('research-one',
                        help='一键研究 MVP 单入口(plan→Agent 席→attach→report;章程 Phase 3)')
    r1.add_argument('--question', default=None, help='研究问题(plan 段必填)')
    r1.add_argument('--question-file', default=None,
                    help='原问逐字文件(Audit-R25 任务3: 优先于 --question,'
                         '字节直读免手打重排标点;仅去尾部换行)')
    r1.add_argument('--stage', choices=['plan', 'attach', 'report', 'auto',
                                        'archive', 'replay'], default='plan',
                    help='plan=research-run+工单;attach=judgment 校验合并;'
                         'report=完整报告汇编(F09: L3/L4 全文内联);'
                         'auto=单命令全自动链 plan→attach→report(Audit-R1 F09;'
                         'Audit-R2 条目6: --report-dir 恢复不重 plan,deliverable '
                         '后携 --archive-dir 直归);'
                         'archive=最终归档段(Audit-R2 条目6: 归档对象=最终'
                         '受审版本,摘要 run=归档=裁决锚三处核对);'
                         'replay=离线重放段(Audit-R28 任务4: 归档交付包'
                         '四门自验证+确定性重渲逐字节核对,--package 指包)')
    r1.add_argument('--report-dir', default=None, help='attach/report/archive 段必填')
    r1.add_argument('--judgment', default=None, help='attach 段必填(judgment JSON)')
    r1.add_argument('--out-dir', default=None, help='报告目录注入缝(plan 段)')
    r1.add_argument('--archive-dir', default=None,
                    help='archive 段/auto 链尾归档目录(缺省=research_archive/'
                         '<run 目录名>;append-only,已存在即拒)')
    r1.add_argument('--engine-root', default=None,
                    help='数据树注入缝(默认=本仓库根;净环境指向真实数据树)')
    r1.add_argument('--allow-failed-run', action='store_true',
                    help='attach 段: run_ok=False 诚实拒答面显式越过(MINOR-4 门槛)')
    r1.add_argument('--new-map-version', action='store_true',
                    help='report/archive 段: 地图正文更正或重排时另建新版本'
                         '(重渲+map_version+1+内容摘要变→旧裁决过期,须复审'
                         '新裁决后方可交付/归档;已裁版本不受渲染器漂移改写'
                         '——Audit-R24 任务1)')
    r1.add_argument('--archive', action='store_true',
                    help='plan 段: 第 11 步归档显式开启(Skill 纪律=默认关,'
                         '正式任务用户认可后郑重选择)')
    r1.add_argument('--package', default=None,
                    help='replay 段必填: 归档交付包目录(含 '
                         'ARCHIVE_MANIFEST.json+九件套+地图三件套+verdicts/)')
    r1.add_argument('--replay-out', default=None,
                    help='replay 段: 输出目录(缺省=<包旁>/replay_out/'
                         '<包名>_<ts>/;append-only 已存在即拒,重复运行'
                         '各开新档,包内零写入)')
    r1.add_argument('--allow-code-mismatch', action='store_true',
                    help='replay 段: 当前代码≠包记录运行 SHA 时显式越过'
                         '(逐字节核对降级为披露;默认拒绝——逐字节相等只对'
                         '录制代码有意义)')
    ra = sub.add_parser('research-attach',
                        help='Agent Native L3/L4 判断落位+纪律机器校验(R23/阶段四): '
                             '校验 Agent judgment 并合并进 research-run 报告;'
                             '校验不过 produced 保持 False(violations 落档)')
    ra.add_argument('--report-dir', required=True,
                    help='research-run 报告目录(含 report.json)')
    ra.add_argument('--judgment', required=True,
                    help='Agent judgment JSON 文件路径(schema v1.0,'
                         '见 scripts/agent_judgment.py 模块docstring)')
    ra.add_argument('--allow-failed-run', action='store_true',
                    help='run_ok=False 的报告显式越过 MINOR-4 门槛'
                         '(诚实拒答类步骤失败但证据面仍可用时由 Agent 声明;'
                         '越过后 run_ok_at_attach+allow_failed_run 随档)')
    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    # Audit-R25 任务3: 原问逐字传递——--question-file 字节直读优先于
    # --question(会话/操作者转述会把全角标点重排为半角,169 字变 168
    # 字的实雷即此;文件仅去尾部换行,其余字节不动)。
    _qf = getattr(args, 'question_file', None)
    if _qf:
        with open(_qf, encoding='utf-8') as f:
            args.question = f.read().rstrip('\n')
        if not args.question:
            emit(envelope(args.capability, False, {},
                          error=('empty_question_file',
                                 '--question-file 内容为空: ' + _qf, None)),
                 exit_code=2)
    elif args.capability == 'research-run' and not args.question:
        emit(envelope('research-run', False, {},
                      error=('missing_question',
                             'research-run 需要 --question 或 --question-file',
                             None)),
             exit_code=2)
    handlers = {'doctor': cmd_doctor, 'update': cmd_update, 'overview': cmd_overview,
                'changes': cmd_changes, 'history': cmd_history, 'compare': cmd_compare,
                'analog': cmd_analog, 'research': cmd_research, 'archive': cmd_archive,
                'views': cmd_views, 'research-map': cmd_research_map,
                'research-run': cmd_research_run,
                'research-attach': cmd_research_attach,
                'research-one': cmd_research_one}
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
