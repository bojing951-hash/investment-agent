#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R2 一键研究编排器(AC6): Skill 十一步研究工作流的可执行化。

定位与边界(零模型诚实面):
- 本编排器只执行**确定性步骤**(体检/事实基线/历史/对比/类比/接地问答/
  观点面装载/lint 自检/落档开关),每步=真 ia_cli 子进程或既有库装载,
  信封原样留档——步骤成败与语义成败分开记录。
- 拆问题(自然语言)/主要矛盾综合/条件推演五行=编排层 Agent 工作,
  本管线不产出: L3(AI推断)/L4(条件情景) 两层恒 declared-not-produced,
  报告明示"本层结论须 Agent 补作并标 attribution",绝不代写。
- 实体映射=确定性词面匹配(metric_id/display_name 大小写折叠子串+
  经济体中文标签反查),匹配不到就如实 unmapped,零翻译零猜测。

四层区分(L1-L4)与逐数证据索引(evidence_index: 每个数字行带
fact_id/view_id 级来源)随报告落盘 report.json+report.md。

纯函数入口: run_research(question, root=None, archive=False, out_dir=None,
ia_timeout=180) → dict(ia_cli research-run 与测试共用)。
"""
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
SCRIPTS = os.path.join(ROOT, 'scripts')
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

PIPELINE_VERSION = '2.0'
IA_CLI = os.path.join(ROOT, 'ia_cli.py')
# Audit-R4 条目5 登记值: 必要指标最低覆盖兜底(问题未限定时间范围时的
# 频率族下界)。Audit-R5 条目2 收紧: **不得统一用"至少 N 个观测"替代
# 原任务所需历史范围**——问题词面限定范围(近/过去 N 年)时按
# N 年×频率年观测数推导;月频 10 年≈120、日频年千计,兜底只拦
# 「最新单点/极短序列冒充历史分析面」;冻结进每项
# spec.min_observations(含推导口径),不随采集结果改判。
_REQ_MIN_OBSERVATIONS = 12
_REQ_MIN_OBSERVATIONS_BY_FREQ = {'daily': 60, 'weekly': 26,
                                 'monthly': 12, 'quarterly': 4}
_OBS_PER_YEAR_BY_FREQ = {'daily': 252, 'weekly': 52,
                         'monthly': 12, 'quarterly': 4}
# Audit-R6 条目2(R6-01): 任务窗口边界容忍(天)——研究时点倒推 N 年为
# [start,end],序列须**跨越**该窗(首观测≤start+容差、末观测≥end-容差,
# 且窗内有效观测数≥下界半额)——按真实时间边界+交易日历判,不以
# 252×年数 总量代替窗口归属。容差按频率族: 日频含周末+节假日簇,
# 周频含停发周;月频/季频含**发布滞后**(PMI 月末+1日/贷款月中发布,
# 季频+1月惯例)。未知频率不获宽容差(窗口不可核验即阻断)。
_WINDOW_TOL_DAYS = {'daily': (14, 10), 'weekly': (21, 14),
                    'monthly': (62, 75), 'quarterly': (95, 130)}
# 窗内有效观测下界系数(允许缺口=节假日/停发/合理缺席,至多一半缺失)
_WINDOW_N_FRACTION = 0.5
# 问题词面时间范围提取(Audit-R5 条目2): 仅认**状语性**范围——
# 近/过去/最近 N 年 或 N 年内/N 年以来;「十年期美债」类资产名
# (N 年+期/收益率)与四位年份不匹配,防止把资产名误当任务范围。
_RANGE_YEARS_RE = re.compile(
    r'(?:近|最近|过去)(一|两|二|三|四|五|六|七|八|九|十|\d+)\s*年'
    r'|(?<![\d])(\d+|一|两|二|三|四|五|六|七|八|九|十)\s*年(?:以内|以来|内)')
_CN_NUM = {'一': 1, '两': 2, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6,
           '七': 7, '八': 8, '九': 9, '十': 10}


def _question_range_years(question):
    """问题词面声明的分析年限(None=未限定)。

    只认状语性范围(近/过去/最近 N 年、N 年内/以来)——确定性词面
    匹配,不做语义改写;未限定返回 None(用频率族兜底下界)。
    多个匹配取**最大**(更严),资产名(十年期美债)不匹配。
    """
    years = []
    for m in _RANGE_YEARS_RE.finditer(question or ''):
        tok = m.group(1) or m.group(2)
        if tok is None:
            continue
        y = _CN_NUM.get(tok) if not tok.isdigit() else int(tok)
        if isinstance(y, int) and y > 0:
            years.append(y)
    return max(years) if years else None
# 引擎数据树注入缝(research-one --engine-root;G2 净环境验收同缝):
# 子进程 ia_cli 与 cwd 改指真实数据树;默认=本仓库根(行为零差)。
RUN_ROOT = ROOT


def _now_utc():
    return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')


def _slug(text, maxlen=40):
    s = re.sub(r'[^A-Za-z0-9一-鿿]+', '_', text).strip('_')
    return (s[:maxlen] or 'question')


def _run_proc(name, cmdline, timeout=180, argv_label=None):
    """跑一个真子进程(通用);进程成败/语义成败/信封三层分开记录。"""
    t0 = time.monotonic()
    try:
        p = subprocess.run(cmdline,
                           capture_output=True, text=True, timeout=timeout,
                           cwd=RUN_ROOT)
        rc, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return {'step': name, 'argv': argv_label or cmdline[1:],
                'executed': True,
                'ok': False, 'exit_code': None,
                'note': f'超时(>{timeout}s)', 'duration_ms': None,
                'envelope': None}
    except OSError as e:
        # R4 NIT(E席审计): 进程启动失败(脚本缺席/无解释器)=该步失败留痕,
        # 不炸整条管线(其余步骤照跑,信封面完整)。
        return {'step': name, 'argv': argv_label or cmdline[1:],
                'executed': True, 'ok': False, 'exit_code': None,
                'note': f'进程启动失败: {e}', 'duration_ms': None,
                'envelope': None}
    env = None
    try:
        env = json.loads(out)
    except ValueError:
        pass
    return {'step': name, 'argv': argv_label or cmdline[1:], 'executed': True,
            'ok': rc == 0,
            'exit_code': rc,
            'semantic_ok': bool(env.get('ok')) if isinstance(env, dict) else None,
            'note': (err.strip()[:200] or None) if rc != 0 and env is None else None,
            'duration_ms': int((time.monotonic() - t0) * 1000),
            'envelope': env}


def run_step(name, argv, timeout=180):
    """跑一步真 ia_cli 子进程(十一步管线主路径)。"""
    ia_cli = os.path.join(RUN_ROOT, 'ia_cli.py')
    return _run_proc(name, [sys.executable, ia_cli] + argv, timeout,
                     argv_label=argv)


def skipped_step(name, note):
    return {'step': name, 'argv': [], 'executed': False, 'ok': True,
            'exit_code': None, 'skipped_reason': note, 'envelope': None}


def _run_ok(steps):
    """进程层总判: 全部已执行步骤 ok;诚实拒答步骤豁免(R2.1 MINOR-1,
    E席审计——analog 短历史拒答是引擎正确行为,不是管线失败)。"""
    return all(s.get('ok') for s in steps
               if s.get('executed') and not s.get('honest_refusal'))


def run_fanout(root, ia_timeout, mapped_metrics):
    """R3 十问确定性扇出: QUESTION_COMMANDS 逐条真跑,信封留档。

    纪律: Agent 层问(RQ3/RQ9)=declared-not-produced,本管线绝不代写;
    占位符确定性替身且如实披露——VIEW-…→观点库首条 view_id(相关性选择
    归 Agent),A_ID/B_ID→命中指标前二(不足回落清单原样 UST_10Y,SPX);
    清单原样的 US+CN/RQ2 指标对不做语义改写(替身≠相关性判断)。"""
    import shlex
    import research_map as rm
    import view_store as vs
    import workbench_data as wd
    root = root or ROOT
    try:
        qmeta = {q['id']: q for q in
                 (wd.research_questions().get('questions') or [])}
    except (OSError, ValueError, KeyError):
        qmeta = {}
    try:
        views = vs.load_views(os.path.join(root, 'data', 'institutions',
                                           'views'))['views']
        first_vid = views[0]['view_id'] if views else None
    except (OSError, ValueError, KeyError, IndexError):
        first_vid = None
    pair = list(mapped_metrics[:2]) if len(mapped_metrics) >= 2 else None
    rows = []
    for rq_id in sorted(rm.QUESTION_COMMANDS,
                        key=lambda k: int(''.join(filter(str.isdigit, k)) or 0)):
        meta = qmeta.get(rq_id, {})
        steps, agent_layer_notes = [], []
        for ci, c in enumerate(rm.QUESTION_COMMANDS[rq_id]):
            toks = shlex.split(c)
            if not toks or toks[0].startswith('('):
                agent_layer_notes.append(c.strip('()'))
                continue
            subs = []
            argv, dead = [], False
            for t in toks[1:]:
                if t == 'VIEW-…':
                    if first_vid is None:
                        subs.append('VIEW-… 无观点库可替(如实跳过)')
                        dead = True
                        break
                    subs.append(f'VIEW-…→{first_vid}(首条确定性替身,'
                                '相关性选择归 Agent)')
                    t = first_vid
                elif t == 'A_ID' and pair:
                    t, _ = pair[0], subs.append(f'A_ID→{pair[0]}')
                elif t == 'B_ID' and pair:
                    t, _ = pair[1], subs.append(f'B_ID→{pair[1]}')
                elif t == 'A_ID,B_ID' and pair:
                    t = f'{pair[0]},{pair[1]}'
                    subs.append(f'A_ID,B_ID→{pair[0]},{pair[1]}')
                argv.append(t)
            name = f'{rq_id}_c{ci}'
            if dead:
                steps.append(skipped_step(name, '; '.join(subs)))
                continue
            if toks[0] == 'ia_cli.py':
                st = run_step(name, argv, ia_timeout)
            elif toks[0].startswith('scripts/'):
                st = _run_proc(name, [sys.executable, os.path.join(
                    root, toks[0])] + argv, ia_timeout, argv_label=argv)
            else:
                steps.append(skipped_step(name, f'非可执行清单项: {c}'))
                continue
            if subs:
                st['substitutions'] = subs
            steps.append(st)
        rows.append({'id': rq_id,
                     'text': meta.get('text'),
                     'primary_layer': meta.get('primary_layer'),
                     'agent_layer': bool(agent_layer_notes),
                     'agent_layer_notes': agent_layer_notes or None,
                     'steps': steps})
    n_exec = sum(1 for r in rows for s in r['steps'] if s.get('executed'))
    n_agent = sum(1 for r in rows if r['agent_layer'])
    return {'requested': True, 'n_rq': len(rows), 'n_executed': n_exec,
            'n_agent_layer': n_agent,
            'substitution_rule': ('VIEW-…→首条 view_id;A_ID/B_ID→命中前二'
                                  '(不足=清单原样)——替身≠相关性选择'),
            'rq': rows}


def map_entities(question, reg):
    """确定性实体映射: 指标(metric_id/display_name 折叠子串)+经济体(中文标签反查)。

    匹配不到=如实 unmapped(零翻译零猜测;Agent 可后续补语义层)。"""
    q = question.casefold()
    metrics = []
    for m in (reg.get('metrics') or []):
        mid = (m.get('metric_id') or '')
        names = [mid, m.get('display_name') or '']
        if any(n and n.casefold() in q for n in names):
            metrics.append(mid)
    economies = []
    import workbench_data as wd
    for code, label in (wd.ECONOMY_LABELS or {}).items():
        # 代码用词边界(防 'EA' 命中 tr'ea'sury 类子串误报);中文标签直接子串
        if label and (label in question
                      or re.search(r'\b' + re.escape(code.casefold()) + r'\b', q)):
            economies.append(code)
    note = None
    if not metrics:
        note = ('问题未词面命中任何指标(零模型不做语义翻译);'
                '事实面降级为经济体概览,接地问答步骤仍如实作答/拒答')
    return {'metrics': metrics, 'economies': economies, 'note': note}


def _fact_rows(snap, metric_ids):
    """L1 行: 快照事实直取(逐行 fact_id 证据;不猜不补)。

    无指标命中时不倾倒全量事实(防噪)——基线层只给计数,裸数行须有映射。"""
    if not metric_ids:
        return []
    rows = []
    for f in snap.get('facts') or []:
        if f.get('metric_id') not in metric_ids:
            continue
        rows.append({'metric_id': f.get('metric_id'),
                     'value': f.get('value'), 'unit': f.get('unit'),
                     'observation_date': f.get('observation_date'),
                     'quality_status': f.get('quality_status'),
                     'source': {'kind': 'snapshot_fact', 'id': f.get('fact_id')}})
    return rows


def _s3_envelope_rows(steps, l1_rows):
    """R33-③: S3_changes 信封在场指标行→证据索引行(kind=s3_envelope)。

    索引行 ref 沿 L1 惯例 `{metric_id}@{observation_date}`;与 L1 已有
    metric_id 去重(L1 行权威);presence 非 present/缺观测日行不收
    (缺席数字无可锚面)。
    """
    s3 = next((s for s in steps if s.get('step') == 'S3_changes'), {})
    bac = ((((s3.get('envelope') or {}).get('data') or {})
            .get('by_asset_class')) or {})
    seen = {r.get('metric_id') for r in l1_rows}
    rows = []
    if not isinstance(bac, dict):
        return rows
    for cls_rows in bac.values():
        if not isinstance(cls_rows, list):
            continue
        for row in cls_rows:
            if not isinstance(row, dict):
                continue
            mid = row.get('metric_id')
            obs = row.get('observation_date')
            if (not mid or mid in seen or not obs
                    or row.get('presence', 'present') != 'present'):
                continue
            seen.add(mid)
            rows.append({'ref': f'{mid}@{obs}', 'kind': 's3_envelope',
                         'metric_id': mid})
    return rows


def vp_face(root):
    """L2 原料: VP sidecar 装载(标签/阶段摘要;缺席如实 None)。"""
    try:
        import view_plausibility as vp
        # R4 NIT(E席审计): root 原先未透传,装载落在模块默认路径——
        # 测试注入的隔离 root 拿不到对应 VP;现按 root 定位。
        docs, bad = vp.load_all(vp_dir=os.path.join(
            root, 'data', 'institutions', 'verification'))
    except Exception as e:  # noqa: BLE001 —— 缺席/不可读=如实降级,不阻断管线
        return {'available': False, 'note': f'VP 装载失败: {e}'}
    if not docs:
        note = 'VP sidecar 缺席(data/ 本地层;干净 clone 常态)'
        if bad:
            note += f';另有 {len(bad)} 份坏档隔离不入面'
        return {'available': False, 'note': note}
    rows = []
    for doc in docs:
        vid = doc.get('view_id')
        rows.append({'view_id': vid,
                     'view_label': doc.get('view_label'),
                     'stage_summary': doc.get('stage_summary'),
                     'source': {'kind': 'vp_sidecar', 'id': f'VP-{vid}'}})
    return {'available': True, 'n': len(rows), 'rows': rows,
            'n_bad_quarantined': len(bad)}


def _parse_ymd(s):
    """'YYYY-MM-DD'/'YYYYMMDD' 前缀 → date(None=不可解析)。"""
    if not isinstance(s, str):
        return None
    t = s.strip().replace('-', '')[:8]
    if len(t) == 8 and t.isdigit():
        try:
            return datetime.strptime(t, '%Y%m%d').date()
        except ValueError:
            return None
    return None


def _snap_as_of_date(snap):
    """研究时点(权威=快照 target_date,research_as_of 兜底;None=不可核验)。"""
    for k in ('target_date', 'research_as_of'):
        d = _parse_ymd((snap or {}).get(k) if isinstance(snap, dict) else None)
        if d is not None:
            return d
    return None


def _evaluate_data_requirements(metrics, steps, snap, l1_rows,
                                question=None, registry=None):
    """Audit-R4 条目5 + Audit-R5 条目2 + Audit-R6 条目2(抽函数可测)。

    判据序: 快照 series_store 序列 → **本管线 S4 history 步已探测的信封**
    (与 Agent 席所见同源)→ L1/S3 单点在场。仅查快照会把采集档序列
    (BEI_10Y/UST_10Y 等 macro 源 2400+ 日)误判「仅最新单点在场」;不在
    进程内另行直读外部数据树(FIX7 信任边界: 采集目录越界不读)。
    最新单点≠历史分析需求满足——n<min_observations 即 insufficient_coverage,
    与 missing 同为必要缺口(attach/report/archive 同源三级分类)。

    Audit-R5 条目2: min_observations 按**任务所需历史范围**推导(问题
    词面限定"近/过去 N 年"→ N 年×频率年观测数;未限定→频率族兜底下界)。

    Audit-R6 条目2(R6-01,反例复现于基线 dcb4b17):
    - 频率取**权威注册表**(registry.by_id,调用面传 S1 已装载面)优先,
      S4 信封次之,快照内嵌 registry_by_id 兜底——快照路径(序列在场→
      S4 不跑)不再丢频率(反例1: 12 个日频观测因 freq=None 落 12 兜底
      满足);
    - 时间范围按**真实时间边界**判: 研究时点(快照 target_date)倒推
      N 年为任务窗,序列须跨窗(首观测≤窗起+容差/末观测≥窗止-容差,
      容差按频率族含节假日/发布滞后)+窗内有效观测≥min_obs 半额
      (允许合理缺口)——总数量再大也不替代窗口归属(反例2: 3000 个
      1990-1998 观测对"近十年"窗=0 窗内有效观测);
    - 未知频率/研究时点不可核验且问题限定范围→**不回落宽松通过**
      (窗口不可核验=insufficient_coverage);未限定范围问题维持
      max_available 口径(完整短史不误拒)。
    """
    _fact_mids = {r['metric_id'] for r in l1_rows}
    _ss = (snap or {}).get('series_store') or {}
    _s3_env = ((next((s.get('envelope') for s in steps
                      if s.get('step') == 'S3_changes'), {}) or {})
               .get('data') or {})
    _s3_mids = set()
    for _bk in (_s3_env.get('by_asset_class') or {}).values():
        if isinstance(_bk, dict):
            _s3_mids.update(str(k) for k in _bk)
    _range_years = _question_range_years(question)
    _as_of = _snap_as_of_date(snap)
    _reg_by_id = registry or {}
    req_items = []
    for _mid in metrics:
        _n_series = len((_ss.get(_mid) or {}).get('dates') or [])
        _ser_src = '研究快照 series_store'
        _freq, _first, _last = None, None, None
        _ss_dates = list((_ss.get(_mid) or {}).get('dates') or [])
        if _ss_dates:
            _first, _last = _ss_dates[0], _ss_dates[-1]
        if _n_series == 0:
            _st = next((s for s in steps
                        if s.get('step') == f'S4_history_{_mid}'), None)
            if _st and _st.get('ok'):
                _s4 = (((_st.get('envelope') or {}).get('data')
                        or {}).get('series')) or {}
                if _s4.get('n') is not None:
                    _n_series = int(_s4['n'])
                    _ser_src = str(_s4.get('source') or 'S4 history 探测')
                    _freq = _s4.get('frequency') or _freq
                    _first = _s4.get('first') or _first
                    _last = _s4.get('last') or _last
        # R6-01: 权威注册表优先(快照路径不丢频率),S4 次之,快照内嵌兜底
        _freq = ((_reg_by_id.get(_mid) or {}).get('frequency')
                 or _freq
                 or (((snap or {}).get('registry_by_id') or {})
                     .get(_mid) or {}).get('frequency'))
        # min_observations 推导: 任务词面年限>频率族兜底(谁严取谁)
        if _range_years and _freq in _OBS_PER_YEAR_BY_FREQ:
            _min_obs = _range_years * _OBS_PER_YEAR_BY_FREQ[_freq]
            _min_basis = (f'问题限定 {_range_years} 年×'
                          f'{_freq} 频率年观测 '
                          f'{_OBS_PER_YEAR_BY_FREQ[_freq]}')
        else:
            _min_obs = _REQ_MIN_OBSERVATIONS_BY_FREQ.get(
                _freq, _REQ_MIN_OBSERVATIONS)
            _min_basis = (f'问题未限定范围→{_freq or "未知"}频率族兜底'
                          f'下界(任务范围不得用统一观测数替代)'
                          if _range_years is None else
                          f'问题限定 {_range_years} 年但 {_freq or "?"} '
                          f'频率未知→通用兜底')
        # ── R6-01: 任务窗口(真实时间边界) ──────────────────────────
        _win = None
        if _range_years:
            if _as_of is None:
                _win = {'start': None, 'end': None,
                        'basis': '研究时点不可核验(快照无 target_date/'
                                 'research_as_of)→窗口不可核验'}
            else:
                _ws = _as_of - timedelta(days=int(round(
                    _range_years * 365.25)))
                _win = {'start': _ws.isoformat(), 'end': _as_of.isoformat(),
                        'as_of': _as_of.isoformat(),
                        'basis': f'研究时点 {_as_of.isoformat()} 倒推 '
                                 f'{_range_years} 年(日历边界)'}
        _tol = _WINDOW_TOL_DAYS.get(_freq) if _freq else None
        _n_in_win, _first_in, _last_in = None, None, None
        _win_detail = None
        if _win is not None and _win.get('start'):
            if _ss_dates:                     # 快照路径: 全日期面逐点判
                _in = [d for d in _ss_dates
                       if _win['start'] <= str(d)[:10] <= _win['end']]
                _n_in_win = len(_in)
                if _in:
                    _first_in, _last_in = _in[0], _in[-1]
            else:                              # S4 路径: 信封 first/last 面
                # 重叠判定(首≤窗止 且 末≥窗起=序列与任务窗相交);序列早于
                # 窗起=覆盖窗起(更长历史不得误拒),窗内首点=max(首,窗起)。
                _f_s, _l_s = (str(_first)[:10] if _first else None), \
                            (str(_last)[:10] if _last else None)
                _overlaps = (_f_s is not None and _l_s is not None
                             and _f_s <= _win['end'] and _l_s >= _win['start'])
                if _overlaps:
                    _first_in = (max(_f_s, _win['start']) if _f_s >=
                                 _win['start'] else _win['start'])
                    _last_in = (_l_s if _l_s <= _win['end'] else _win['end'])
                    _n_in_win = _n_series
                else:
                    _n_in_win = None
        # ── 判定序: 窗口不可核验(限定范围+未知频率/时点)先拦 ─────────
        if _win is not None and (_freq is None or _tol is None):
            _outcome = 'insufficient_coverage'
            _basis = (f'问题限定 {_range_years} 年但频率={_freq or "未知"}'
                      f'不可核验→时间窗口无法判定(不回落宽松通过;'
                      f'{_min_basis};源={_ser_src})')
        elif _win is not None and _win.get('start') is None:
            _outcome = 'insufficient_coverage'
            _basis = ('研究时点不可核验→任务窗口无法判定(不回落宽松'
                      '通过;问题限定 %d 年)' % _range_years)
        elif _n_series >= _min_obs and _win is None:
            _outcome = 'satisfied'
            _basis = (f'历史序列 n={_n_series}≥最低覆盖{_min_obs}'
                      f'({_min_basis};源={_ser_src};未限定范围='
                      f'max_available,总量口径)')
        elif _n_series >= _min_obs and _win is not None:
            _fd, _ld = _parse_ymd(_first_in), _parse_ymd(_last_in)
            _wsd = _parse_ymd(_win['start'])
            _wed = _parse_ymd(_win['end'])
            _start_ok = (_fd is not None and _wsd is not None
                         and (_fd - _wsd).days <= _tol[0])
            _end_ok = (_ld is not None and _wed is not None
                       and (_wed - _ld).days <= _tol[1])
            _n_floor = max(1, int(round(_min_obs * _WINDOW_N_FRACTION)))
            _n_ok = (_n_in_win is not None and _n_in_win >= _n_floor)
            if _start_ok and _end_ok and _n_ok:
                _outcome = 'satisfied'
                _basis = (f'历史序列 n={_n_series}≥{_min_obs} 且跨任务窗'
                          f'{_win["start"]}..{_win["end"]}'
                          f'(窗内有效 n={_n_in_win}≥{_n_floor}'
                          f'[{_WINDOW_N_FRACTION:.0%} 允许缺口];'
                          f'边界容差 起+{_tol[0]}天/止-{_tol[1]}天'
                          f'(频率族含节假日/发布滞后);'
                          f'{_min_basis};源={_ser_src})')
            else:
                _why = []
                if not _start_ok:
                    _why.append(f'窗内首观测{_first_in or "缺席"}晚于窗起'
                                f'+{_tol[0]}天容忍(历史未覆盖任务窗起点)')
                if not _end_ok:
                    _why.append(f'窗内末观测{_last_in or "缺席"}早于窗止'
                                f'-{_tol[1]}天容忍(发布滞后外缺口)')
                if not _n_ok:
                    _why.append(f'窗内有效观测 n={_n_in_win or 0}<{_n_floor}'
                                f'(总量{_n_series}不替代窗口归属)')
                _outcome = 'insufficient_coverage'
                _basis = (f'任务窗{_win["start"]}..{_win["end"]}未满足: '
                          + ';'.join(_why)
                          + f'({_min_basis};源={_ser_src})')
            _win_detail = {'n_in_window': _n_in_win,
                           'first_in_window': _first_in,
                           'last_in_window': _last_in,
                           'n_floor_in_window': _n_floor,
                           'tolerance_days': {'start': _tol[0],
                                              'end': _tol[1]}}
        elif _n_series > 0:
            _outcome = 'insufficient_coverage'
            _basis = (f'历史序列 n={_n_series} < 最低覆盖{_min_obs}'
                      f'({_min_basis};源={_ser_src};'
                      f'单点/短序列≠历史分析需求)')
        elif _mid in _fact_mids or _mid in _s3_mids:
            _outcome = 'insufficient_coverage'
            _basis = ('仅最新单点在场(L1/S3),无历史序列——单点≠'
                      '历史分析需求满足')
        else:
            _outcome = 'missing'
            _basis = 'L1/S3/快照序列均缺席'
        _spec_win = None
        if _range_years:
            _spec_win = dict(_win or {})
            _spec_win['question_range_years'] = _range_years
            if _win_detail:
                _spec_win.update(_win_detail)
            _spec_win['allowed_gap'] = {
                'tolerance_days': (_tol if _tol else None),
                'n_fraction_floor': _WINDOW_N_FRACTION,
                'basis': '频率族容差(日频节假日簇/月频发布滞后)+'
                         '窗内半额有效观测下界'}
        req_items.append({'metric_id': _mid, 'tier': 'required',
                          'basis': '问题词面命中(任务目标)',
                          'spec': {'form': 'series',
                                   'window': (_spec_win if _spec_win else
                                              'max_available'),
                                   'frequency': _freq,
                                   'quality': 'snapshot 序列(OK 行)',
                                   'coverage_observed': {
                                       'n': _n_series or None,
                                       'first': _first, 'last': _last,
                                       'n_in_window': _n_in_win,
                                       'first_in_window': _first_in,
                                       'last_in_window': _last_in},
                                   'min_observations': _min_obs,
                                   'min_observations_basis': _min_basis},
                          'outcome': _outcome, 'outcome_basis': _basis})
    return req_items


def run_research(question, root=None, archive=False, out_dir=None,
                 ia_timeout=180, fanout=False, engine_root=None):
    """十一步一键研究管线;返回完整报告 dict(run_ok=进程层,语义面看各步)。

    fanout=True 追加十问扇出面(R3): research_map.QUESTION_COMMANDS 逐条
    真跑+信封留档,Agent 层问(RQ3/RQ9)declared-not-produced。
    engine_root: 子进程 ia_cli 与 cwd 改指真实数据树(注入缝;默认=本仓库,
    行为零差)——净克隆验收/单入口 MVP 用。"""
    global RUN_ROOT
    RUN_ROOT = engine_root or ROOT
    root = root or RUN_ROOT
    import workbench_data as wd
    steps = []
    notes = []

    # ── S1 拆问题(确定性面) ─────────────────────────────────────────
    reg = wd.load_registry(root)
    ent = map_entities(question, reg)
    steps.append({'step': 'S1_decompose', 'executed': True, 'ok': True,
                  'deterministic_face': ent,
                  'agent_face_note': '自然语言深拆/主要矛盾综合=编排层 Agent;'
                                     '本步只给确定性实体映射'})

    # ── S2 doctor 体检 ──────────────────────────────────────────────
    steps.append(run_step('S2_doctor', ['doctor'], ia_timeout))

    # ── S3 事实基线(overview+changes) ───────────────────────────────
    ecos = ent['economies'] or ['US', 'CN']
    if not ent['economies']:
        # R4 NIT(E席审计): 默认面不再静默——US+CN 是清单默认而非问题语义
        notes.append('问题未命中经济体,S3 用默认面 US+CN(清单默认,'
                     '非问题语义判断;Agent 可按需补查其它经济体)')
    for eco in ecos:
        steps.append(run_step(f'S3_overview_{eco}',
                              ['overview', '--economy', eco], ia_timeout))
    steps.append(run_step('S3_changes', ['changes'], ia_timeout))

    # ── S4 历史可得性(命中指标逐个;未命中=跳过如实) ─────────────────
    hist_metrics = ent['metrics'][:4]
    if len(ent['metrics']) > 4:
        notes.append(f"命中 {len(ent['metrics'])} 个指标,历史步骤只取前 4"
                     f"(防噪);其余由 Agent 按需 history --metric 查询")
    for mid in hist_metrics:
        steps.append(run_step(f'S4_history_{mid}',
                              ['history', '--metric', mid], ia_timeout))
    if not hist_metrics:
        steps.append(skipped_step(
            'S4_history', '问题未命中指标——零实体映射时如实跳过(不造数)'))

    # ── S5 对齐自配对(≥2 命中才可比) ────────────────────────────────
    if len(hist_metrics) >= 2:
        steps.append(run_step('S5_compare',
                              ['compare', '--metrics',
                               ','.join(hist_metrics[:2])], ia_timeout))
        # R2.1 MINOR-2(E席审计): compare 仅取命中前 2(注册表序,确定性;
        # 非问题重点序)——如实披露,不静默截断
        if len(hist_metrics) > 2:
            steps[-1]['note'] = (f"命中 {len(hist_metrics)} 个指标,"
                                 f"compare 仅取注册表序前 2("
                                 f"{','.join(hist_metrics[:2])});"
                                 f"其余 {','.join(hist_metrics[2:])} "
                                 f"以 L1 事实行呈现,如需对比另行单跑")
    else:
        steps.append(skipped_step(
            'S5_compare', '命中指标不足 2 个,无可对齐自配对(如实跳过)'))

    # ── S6 历史相似结构(analog;短历史诚实拒答透传) ─────────────────
    steps.append(run_step('S6_analog', ['analog'], ia_timeout))
    # R2.1 MINOR-1(E席审计): analog 数据面诚实拒答(rc=1,engine _refuse)
    # 是正确行为不是管线失败——标记豁免,run_ok 不因它翻 False。
    _s6 = steps[-1]
    _err = ((_s6.get('envelope') or {}).get('error') or {})
    if (not _s6.get('ok')
            and _err.get('kind') in ('insufficient_history',
                                     'insufficient_candidates',
                                     'anchor_not_complete')):
        _s6['honest_refusal'] = True
        _s6['note'] = (f"诚实拒答(engine: {_err.get('kind')}),"
                       f"run_ok 豁免: {_err.get('message')}")

    # ── S7 research_mode_gate(从 compare/analog 信封提取,无独立命令) ─
    # R2.1 MAJOR-1(E席审计): gate 两处来源语义不同——compare 信封
    # data.alignment.research_mode_gate=对齐研究门(权威,本步对象);
    # analog 信封 data 顶层=锚点月窗门(另一语义)。旧实现只探顶层两处,
    # compare 对齐门恒漏(死代码),错取 analog 门甚至落空。现按优先级取并
    # 记 gate_source,可溯。
    gate, gate_src = None, None
    for s in steps:
        if s['step'] != 'S5_compare':
            continue
        d = (s.get('envelope') or {}).get('data')
        g = (d.get('alignment') or {}).get('research_mode_gate') \
            if isinstance(d, dict) else None
        if g is not None:
            gate, gate_src = g, 'S5_compare:data.alignment.research_mode_gate'
    if gate is None:
        for s in steps:
            if s['step'] != 'S6_analog':
                continue
            d = (s.get('envelope') or {}).get('data')
            g = d.get('research_mode_gate') if isinstance(d, dict) else None
            if g is not None:
                gate, gate_src = g, 'S6_analog:data.research_mode_gate'
    gate_note = None
    if gate_src == 'S6_analog:data.research_mode_gate':
        gate_note = 'analog 锚点月窗门(compare 未产出对齐门——命中<2 或被拒)'
    steps.append({'step': 'S7_mode_gate', 'executed': True, 'ok': gate is not None,
                  'gate': gate, 'gate_source': gate_src, 'note': gate_note or
                  (None if gate else 'compare/analog 信封未含 gate'
                          '(本轮无可比对/被拒答)——如实缺席,不编造')})

    # ── S8 接地问答(ia_cli research;archive 开关在此一次性落档) ────
    qa_argv = ['research', '--question', question]
    if archive:
        qa_argv += ['--archive',
                    '--note', 'R2 research-run 一键编排落档']
    steps.append(run_step('S8_grounded_qa', qa_argv, ia_timeout))

    # ── S9 观点面(views lint + VP 装载) ────────────────────────────
    steps.append(run_step('S9_views_lint', ['views', 'lint'], ia_timeout))
    vpf = vp_face(root)

    # ── S10 lint/自检: views 违规数+证据索引完整性 ──────────────────
    lint_step = next((s for s in steps if s['step'] == 'S9_views_lint'), {})
    n_quarantined = ((((lint_step.get('envelope') or {}).get('data'))
                      or {}).get('n_quarantined'))

    snap, snap_note = wd.latest_snapshot(root)
    facts = snap.get('facts') if snap else None
    l1_rows = _fact_rows(snap or {}, set(hist_metrics)) if facts else []

    # ── Audit-R2 条目7: 数据需求声明(分类在采集前冻结,不随结果改判) ──
    # 必要=问题词面命中指标(任务目标本体);可选=上下文面(S3 信封指标/
    # L2 机构观点/经济体概览)。采集后只评 outcome(satisfied/missing),
    # 不得把 missing 的必要项改判可选(事后缩减任务目标=禁止)。
    # 评据: L1 行 / 快照 series_store 序列在场(S4 history 数据源)。
    _req_items = _evaluate_data_requirements(
        ent['metrics'], steps, snap, l1_rows, question=question,
        registry=reg.get('by_id'))
    data_requirements = {
        'frozen_at': 'plan(采集前冻结;分类与规格不随采集结果改判)',
        'items': _req_items,
        'optional_face': {
            'tier': 'optional',
            'scope': 'S3 上下文指标/L2 机构观点/经济体概览',
            'note': '可选缺席=降级披露,不构成任务目标缺口;必要缺席/'
                    '覆盖不足=任务目标缺口,attach 默认阻塞(显式越过须随档)'},
    }
    if any(i['outcome'] in ('missing', 'insufficient_coverage')
           for i in _req_items):
        notes.append('必要数据缺口: ' + '、'.join(
            i['metric_id'] for i in _req_items
            if i['outcome'] in ('missing', 'insufficient_coverage'))
            + '(运行前已声明为任务目标,未事后缩减;补齐授权范围内数据'
              '或按降级面显式越过)')

    layers = {
        'L1_事实层': {
            'available': snap is not None,
            'snapshot_id': (snap or {}).get('snapshot_id'),
            'target_date': (snap or {}).get('target_date'),
            'n_facts_total': len(facts or []),
            'rows': l1_rows,
            'note': None if snap else f'快照缺席: {snap_note}',
        },
        'L2_机构观点层': {
            'views': vpf,
            'note': '标签=证据评价非预测判定;阶段摘要 A/B/C 见 VP sidecar',
        },
        'L3_AI推断层': {
            'produced': False,
            'note': '零模型管线: 本层(矛盾综合/推断)须编排层 Agent 补作,'
                    'attribution=ai_inferred——本管线绝不代写。补作纪律: '
                    '四层标注(事实/推断/假设/尚未验证)+并列竞争性解释'
                    '(Skill 纪律4/第9步);机制链每环标 E1(引擎直接可验证)/'
                    'E2(部分支持,缺环明写【假设】)/E3(纯叙事,须给证伪指标)'
                    '(纪律15)',
        },
        'L4_条件情景层': {
            'produced': False,
            # R2.1 MAJOR-2(E席审计): 五行以 Skill 纪律16 权威模板为准
            # (旧措辞"前提/机制/路径"系 research_map 历史漂移,已一并统一)
            'note': '条件推演五行(纪律16: 情景[明写假设非预测]/资产方向判断'
                    '[方向+置信层级]/敏感变量[1-2 个引擎指标]/证伪指标'
                    '[可观测阈值]/触发条件[可观测条件+时限];单一情景不得'
                    '单独呈现,至少并列基准与反例)归编排层 Agent;'
                    '不冒充预测——本管线绝不代写',
        },
    }

    # 证据索引: 每个数字行必须有 fact_id/view_id 级来源
    evidence_index = []
    for r in l1_rows:
        evidence_index.append({'ref': r['source']['id'],
                               'kind': r['source']['kind'],
                               'metric_id': r['metric_id']})
    for r in (vpf.get('rows') or []):
        evidence_index.append({'ref': r['source']['id'],
                               'kind': r['source']['kind'],
                               'view_label': r['view_label']})
    # R33-③(首审席建议 narr-facts): S3 信封被引数字入索引——L3 叙事
    # 常引 changes 面指标(UST_10Y/TLT 等),旧索引只含问题命中(L1)+VP,
    # 被引数字无可锚行。S3_changes 信封 by_asset_class 全量在场指标入索引
    # (kind=s3_envelope),按 metric_id 与 L1 去重;缺席/缺值行不收。
    evidence_index.extend(_s3_envelope_rows(steps, l1_rows))
    missing_ref = [r['metric_id'] for r in l1_rows if not r['source']['id']]
    selfcheck = {'n_evidence_rows': len(evidence_index),
                 'n_rows_missing_ref': len(missing_ref),
                 'ok': not missing_ref}
    steps.append({'step': 'S10_selfcheck', 'executed': True,
                  'ok': bool(selfcheck['ok']),
                  'n_views_quarantined': n_quarantined,
                  'selfcheck': selfcheck,
                  'note': None if selfcheck['ok'] else f'缺来源行: {missing_ref}'})

    # ── S11 落档(S8 一次性完成;默认关) ─────────────────────────────
    qa_env = next((s.get('envelope') for s in steps
                   if s.get('step') == 'S8_grounded_qa'), {}) or {}
    archived_id = ((qa_env.get('data') or {}).get('archived_query_id')
                   if isinstance(qa_env, dict) else None)
    steps.append({'step': 'S11_archive', 'executed': True,
                  'ok': (archived_id is not None) if archive else True,
                  'archive_requested': bool(archive),
                  'archived_query_id': archived_id,
                  'note': ('已随 S8 落档' if archived_id
                           else '默认关(--archive 显式开启;Skill 第 11 步=用户认可后)')})

    if ent['note']:
        notes.append(ent['note'])

    # R2.1 MINOR-1: 诚实拒答步骤(如 S6 analog 短历史拒答)豁免出 run_ok
    run_ok = _run_ok(steps)

    # ── R3 十问扇出(可选,--fanout;独立于 S1-S11 主台账) ────────────
    fan = ({'requested': False}
           if not fanout else run_fanout(root, ia_timeout,
                                         [m for m in ent['metrics']]))

    report = {
        'schema_version': '2.0',
        'pipeline_version': PIPELINE_VERSION,
        'run': {'question': question, 'ts_utc': _now_utc(),
                'archive_requested': bool(archive),
                'git_head': _git_head(root),
                # Audit-R1 F02: 降级规则**运行前固定**(attach 段同文执行,
                # 双写互证;运行后不得改判)——可选数据缺失与关键失败分级
                'degradation_policy': {
                    'critical_zero_evidence': (
                        'L1 事实行=0(引擎崩溃/全量采集失败)→拒收判断,'
                        '--allow-failed-run 亦不放行'),
                    'required_data_missing': (
                        '运行前声明的必要指标(问题词面命中)采集缺席→'
                        '任务目标缺口,默认阻塞;显式 --allow-failed-run '
                        '才放行,落位记 degraded(缺口随档,不得事后改判可选)'),
                    'optional_data_missing': (
                        'L1 事实面在场、失败步=诚实拒答类(源端缺席 no_series)'
                        '→须显式 --allow-failed-run,落位记 degraded')},
                'data_requirements': data_requirements,
                },
        'steps': steps,
        'fanout': fan,
        'layers': layers,
        'evidence_index': evidence_index,
        'notes': notes,
        'run_ok': run_ok,
    }

    out_root = out_dir or os.path.join(root, 'output', 'research_runs')
    run_dir = os.path.join(out_root, f"{report['run']['ts_utc']}_{_slug(question)}")
    # R4 NIT(E席审计): 时间戳分钟级,同分钟两跑同名目录会互相覆盖——
    # 已存在则追加序号,绝不覆盖历史报告。
    n = 2
    while os.path.exists(run_dir):
        run_dir = os.path.join(
            out_root, f"{report['run']['ts_utc']}_{_slug(question)}_{n}")
        n += 1
    os.makedirs(run_dir)
    with open(os.path.join(run_dir, 'report.json'), 'w',
              encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    with open(os.path.join(run_dir, 'report.md'), 'w',
              encoding='utf-8') as f:
        f.write(_render_md(report))
    report['report_dir'] = run_dir
    return report


def _git_head(root):
    try:
        p = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'],
                           capture_output=True, text=True, timeout=10, cwd=root)
        return p.stdout.strip() if p.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def _render_l3(content):
    """R23: Agent Native L3 判断内容渲染(原文转述,排版不改写语义)。"""
    lines = []
    for c in (content.get('contradictions') or []):
        lines.append(f"- **{c.get('id')}**: {c.get('statement')}")
        if c.get('basis'):
            lines.append(f"  - 依据: {c['basis']}")
        for i, e in enumerate(c.get('competing_explanations') or [], 1):
            lines.append(f"  - 竞争性解释{i}: {e}")
        if c.get('evidence_refs'):
            lines.append(f"  - 证据: {', '.join(c['evidence_refs'])}")
        elif c.get('no_anchor_reason'):
            lines.append(f"  - 证据: 无锚(明示免锚: {c['no_anchor_reason']})")
    for ch in (content.get('mechanism_chains') or []):
        lines.append(f"- **机制链 {ch.get('id')}**: {ch.get('name') or ''}")
        for lk in (ch.get('links') or []):
            tag = lk.get('evidence_level')
            extra = ''
            if tag == 'E1' and lk.get('evidence_refs'):
                extra = f" [证据: {', '.join(lk['evidence_refs'])}]"
            elif tag == 'E2':
                extra = f" [缺失环: {lk.get('missing_link_note') or ''}]"
            elif tag == 'E3':
                extra = f" [证伪指标: {lk.get('falsification_metric') or ''}]"
            lines.append(f"  - {tag} {lk.get('text')}{extra}")
    return lines


def _render_l4(content):
    """R23: Agent Native L4 条件情景渲染(五行结构逐行落纸)。"""
    lines = []
    for s in (content.get('scenarios') or []):
        rows = s.get('rows') or {}
        ad = rows.get('asset_direction') or {}
        fals = rows.get('falsification') or {}
        trig = rows.get('trigger') or {}
        lines.append(f"- **{s.get('id')}**({s.get('role') or ''})")
        lines.append(f"  - 情景: {rows.get('scenario')}")
        lines.append(f"  - 资产方向判断: {ad.get('direction')}"
                     f"(置信: {ad.get('confidence_tier')})"
                     f" {ad.get('text') or ''}")
        lines.append(f"  - 敏感变量: {', '.join(rows.get('sensitive_variables') or [])}")
        lines.append(f"  - 证伪指标: {fals.get('metric_id')} 阈值 {fals.get('threshold')}")
        lines.append(f"  - 触发条件: {trig.get('condition')}(时限 {trig.get('deadline')})")
    return lines


def _render_md(r):
    """人类可读面: 四层区分+步骤台账+(可选)十问扇出台账+证据索引。"""
    def argv_str(step):
        return ' '.join(str(x) for x in (step.get('argv') or [])[:8])
    q = r['run']['question']
    L = r['layers']
    lines = [f"# 一键研究报告(零模型编排 v{r['pipeline_version']})",
             f"- 问题: {q}",
             f"- 运行: {r['run']['ts_utc']} @ {r['run'].get('git_head')}",
             f"- 快照: {L['L1_事实层'].get('snapshot_id')} "
             f"(target {L['L1_事实层'].get('target_date')})"]
    # R33-②(首审席 narr-facts): gate_a 状态披露行——首审发现全部步骤
    # 信封载 gate_a=DEGRADED 而 md 全文零披露。渲染时从各步信封顶层
    # 汇总(旧档重渲同样生效);降级不阻断,但判断层/读者须知。
    gates = [(s.get('step'), (s.get('envelope') or {}).get('gate_a'))
             for s in r.get('steps') or []
             if isinstance(s.get('envelope'), dict)
             and s.get('envelope').get('gate_a') is not None]
    if gates:
        bad = [g for g in gates if g[1] != 'OK']
        if bad:
            kinds = '、'.join(sorted({str(g[1]) for g in bad}))
            lines.append(f"- 数据门(gate_a): {len(bad)}/{len(gates)} "
                         f"信封步非 OK({kinds})——缺口/降级明细见步骤台账"
                         "各步信封 warnings;降级不阻断,判断层须知")
        else:
            lines.append(f"- 数据门(gate_a): OK({len(gates)}/{len(gates)} "
                         "信封步)")
    # Audit-R2 条目7 + Audit-R4 条目5: 数据需求声明(运行前冻结,含规格)
    # ——必要缺席/覆盖不足=任务目标缺口(最新单点≠历史分析需求满足)
    _dr = ((r.get('run') or {}).get('data_requirements') or {})
    if _dr.get('items'):
        _gap = sum(1 for i in _dr['items'] if i.get('outcome')
                   in ('missing', 'insufficient_coverage'))
        lines.append(f"- 数据需求(运行前冻结): 必要 "
                     f"{sum(1 for i in _dr['items'] if i.get('tier') == 'required')}"
                     f" 项(问题命中,规格=序列/最低覆盖"
                     f"{(( _dr['items'][0].get('spec') or {}).get('min_observations'))}"
                     f" 观测),缺口 {_gap} 项;可选面缺席=降级披露不构成缺口")
        for i in _dr['items']:
            if i.get('outcome') in ('missing', 'insufficient_coverage'):
                lines.append(f"  - 任务目标缺口: {i['metric_id']}"
                             f"({i.get('outcome_basis')})——未事后缩减,"
                             "补齐授权范围内数据或按降级面显式越过")
    lines += ['', '## 四层区分', '']
    l1 = L['L1_事实层']
    lines.append(f"### L1 事实层 available={l1['available']}"
                 + ('' if l1['available'] else f"({l1['note']})"))
    for row in l1['rows']:
        # R23 审计 MINOR-5: 质量状态随行渲染(此前只在 json 面,
        # md 读者看不到 DEGRADED 披露)
        q = row.get('quality_status')
        lines.append(f"- {row['metric_id']} = {row['value']} {row['unit'] or ''}"
                     f" @{row['observation_date']}"
                     + (f" [质量:{q}]" if q else '')
                     + f" [来源:{row['source']['kind']}:{row['source']['id']}]")
    vpf = L['L2_机构观点层']['views']
    lines.append(f"\n### L2 机构观点层 "
                 f"available={vpf.get('available')}"
                 + (f" n={vpf['n']}" if vpf.get('available')
                    else f"({vpf.get('note')})"))
    for row in (vpf.get('rows') or []):
        ss = row.get('stage_summary') or {}
        lines.append(f"- {row['view_id']}: view_label={row['view_label']}"
                     f" 阶段摘要={ {k: ss.get(k) for k in ('A', 'B', 'C')} }")
    lines.append(f"\n### L3 AI推断层 produced={L['L3_AI推断层']['produced']}")
    if L['L3_AI推断层'].get('produced') and L['L3_AI推断层'].get('content'):
        lines.append(f"> {L['L3_AI推断层'].get('note') or ''}"
                     f"(attribution={L['L3_AI推断层'].get('attribution')})")
        lines += _render_l3(L['L3_AI推断层']['content'])
    else:
        lines.append(f"> {L['L3_AI推断层']['note']}")
    lines.append(f"\n### L4 条件情景层 produced={L['L4_条件情景层']['produced']}")
    if L['L4_条件情景层'].get('produced') and L['L4_条件情景层'].get('content'):
        lines.append(f"> {L['L4_条件情景层'].get('note') or ''}"
                     f"(attribution={L['L4_条件情景层'].get('attribution')})")
        lines += _render_l4(L['L4_条件情景层']['content'])
    else:
        lines.append(f"> {L['L4_条件情景层']['note']}")
    # R33-①(席位 runtime 接入;章程 §8 披露开关): L3/L4 在文且席位
    # 未裁→「叙事语义未经独立裁决」常设披露;席位裁决档在案→升为裁决
    # 摘要。状态面由 agent_judgment.attach_judgment 写入(旧档无该块
    # =旧面如实,不追溯)。
    sr = r.get('semantic_review') or {}
    if sr.get('required'):
        if sr.get('seat_invoked'):
            lines += ['', '## 语义审查(席位已裁)', '',
                      f"- 席位裁决: {sr.get('verdict')}"
                      f"(档: {sr.get('archive')})"]
        else:
            lines += ['', '## 语义审查(席位待唤起)', '',
                      '- **叙事语义未经独立裁决**——定性推断/条件情景在文;'
                      '常驻席位=SEMANTIC-AUDIT-SEAT,编排层应唤席裁决后'
                      '方可去掉本披露(章程 §4b/§8)']
    # R25 审计 Mi-1: agent_judgment 面入 md(attach/blocked/违规计数)——
    # md-only 读者可见落位状态(旧: 仅 report.json 有,md 零渲染)
    aj = r.get('agent_judgment') or {}
    if aj:
        if aj.get('blocked'):
            lines += ['', '## Agent 判断落位: 未落位(门槛拦截)', '',
                      f"- blocked={aj.get('blocked')}"
                      f"(run_ok={aj.get('run_ok_at_attach')};判断默认不得落在"
                      "失败证据面上,显式 --allow-failed-run 才放行)"]
        else:
            val = aj.get('validation') or {}
            lines += ['', '## Agent 判断落位', '',
                      f"- attached={aj.get('attached')}"
                      f"(schema {aj.get('schema_version')};"
                      f"violations={len(val.get('violations') or [])})"]
    lines += ['', '## 步骤台账', '']
    for s in r['steps']:
        # R39(R25 审计预存观察): executed 优先判——skipped_step 带 ok=True
        # (数据面契约: 跳过≠失败),原序 ok 先判→SKIP 分支死码,跳过步渲
        # [OK |—] 误导(读者以为执行成功)。先判 executed: 跳过步=SKIP+理由。
        tag = ('SKIP' if not s.get('executed') else
               ('OK ' if s.get('ok') else 'FAIL'))
        # R2.1 MINOR-3: 语义面单列(进程 ok ≠ 语义产出;诚实拒答/如实
        # unmapped 不与真失败混渲)。
        # R25 NIT V1-1(R24 审计): 按步骤性质三分——信封步(子进程产 JSON
        # 信封,semantic_ok 在场)才适用语义判定;编排内部步(S1/S7/S10/S11,
        # 无信封无 semantic_ok 键)原渲染恒落「语义✗」=标签噪音(内部步
        # 成败已由进程面 tag 忠实承载,语义层本就不适用)。方向保守:
        # 不藏任何失败——FAIL 仍照渲,只是不再给内部步贴误导读的语义标签。
        if not s.get('executed'):
            sem = '—'
        elif 'semantic_ok' in s:
            if s.get('semantic_ok') is True:
                sem = '语义✔'
            elif s.get('honest_refusal'):
                sem = '诚实拒答'
            else:
                sem = '语义✗'
        else:
            sem = '不适用'
        extra = s.get('skipped_reason') or s.get('note') or ''
        lines.append(f"- [{tag}|{sem}] {s['step']} {extra}")
    fan = r.get('fanout') or {}
    if fan.get('requested'):
        lines += ['', f"## 十问扇出台账(执行 {fan['n_executed']} / "
                  f"Agent 层 {fan['n_agent_layer']} / 共 {fan['n_rq']} 问)",
                  f"> 替身规则: {fan['substitution_rule']}", '']
        for row in fan['rq']:
            head = f"### {row['id']} {row.get('text') or ''} [{row.get('primary_layer')}]"
            lines += [head]
            if row['agent_layer_notes']:
                lines.append(f"- [Agent层|不代写] " + '; '.join(
                    n[:120] for n in row['agent_layer_notes']))
            for s in row['steps']:
                # R39: 同步骤台账 executed 优先判(跳过步不再渲 OK)
                tag = ('SKIP' if not s.get('executed') else
                       ('OK ' if s.get('ok') else 'FAIL'))
                extra = s.get('skipped_reason') or s.get('note') or ''
                sub = '; '.join(s.get('substitutions') or [])
                lines.append(f"- [{tag}] {s['step']} "
                             f"{argv_str(s)}{(' | 替身: ' + sub) if sub else ''}"
                             f"{(' | ' + extra) if extra else ''}")
            lines.append('')
    lines += ['', f"## 证据索引({len(r['evidence_index'])} 行)", '']
    # R33-③: 索引含 S3 信封行后全量渲(旧 60 行截断按 21 行规模设,
    # 现规模 ~60+;截断=被引数字锚面不可见,与③目的相悖)
    for e in r['evidence_index']:
        lines.append(f"- {e['kind']}:{e['ref']}"
                     + (f" → {e['metric_id']}" if e.get('metric_id') else '')
                     + (f" [{e['view_label']}]" if e.get('view_label') else ''))
    if r['notes']:
        lines += ['', '## 注记', ''] + [f"- {n}" for n in r['notes']]
    lines.append('')
    return '\n'.join(lines)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    import argparse
    p = argparse.ArgumentParser(description='一键研究编排(十一步确定性管线,零模型)')
    p.add_argument('--question', required=True)
    p.add_argument('--archive', action='store_true',
                   help='落档(Skill 第 11 步=用户认可后;默认关)')
    p.add_argument('--out-dir', default=None)
    p.add_argument('--root', default=ROOT)
    a = p.parse_args(argv)
    rep = run_research(a.question, root=a.root, archive=a.archive,
                       out_dir=a.out_dir)
    print(json.dumps({'run_ok': rep['run_ok'],
                      'report_dir': rep['report_dir'],
                      'n_steps': len(rep['steps']),
                      'n_evidence_rows': len(rep['evidence_index'])},
                     ensure_ascii=False, indent=2))
    return 0 if rep['run_ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
