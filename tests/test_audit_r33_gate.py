#!/usr/bin/env python3
"""Audit-R33 门 — 产品收尾五任务(基线 f053afe): 统一历史证据口径/政策时态/
真正的原问/冷启动/预期差研究。

任务1 统一历史证据口径: 规则②官方发布日优先逐点核(无 62 天视界捷径);事实表/
历史序列/派生值绑定同一份当时可得的冻结版本(as-of vintage): 旧快照有序列但缺
事实行→自该版本序列重建;序列不在该版本内=截止后回填→空壳点名;版本日后、
研究时点前已发布的观测不在所绑版本内→缺口点名(不取较晚版本补入);无历史版本
=逐事实 historical_version_missing+顶层缺口;快报与终值=声明修订口径序列在
首发→终值窗口内无冻结版本=当时数据版本不可得,有冻结版本=当时冻结的快报值并
随行标注;采集档通道同口径;政策文档按发布日期过滤。
夹具说明: 冻结快照=提交的 R31 B2 overlay 原件(真实);as-of 版本夹具=由该快照
按官方发布日截接的**构造版本**(snapshot_id 前缀 FIXTURE_,fixture_note 随行),
非真实历史快照——只用于核验绑定规则,不作为任何交付的证据。
"""
import contextlib
import copy
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
sys.path.insert(0, os.path.join(ROOT, 'scripts', 'research_contract'))

import evidence_gate as eg                       # noqa: E402
import release_calendar as rc                    # noqa: E402
import research_map_planner as rmp                # noqa: E402
import workbench_data as wd                       # noqa: E402

TMPG = tempfile.mkdtemp(prefix='r33gate_')
RESULTS = []
R31_ACC = os.path.join(ROOT, 'docs', 'autonomous-rd', 'r31-evidence',
                       'acceptance')
SNAP_SRC = os.path.join(R31_ACC, 'session_B2_formal', 'root_overlay',
                        'data', 'daily', 'research_snapshot_20261122_v2.json')
SNAP_LATER = 'research_snapshot_20261122_v2.json'
WORKTREE_HEAD = subprocess.run(
    ['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True,
    text=True, timeout=30).stdout.strip()
# 2025-11-15 工单(任务1/任务2 验收问句;显式研究时点标记)
Q_T1 = ('以 2025-11-15 为研究时点，美国、中国、欧元区、日本在最新一期分别处于'
        '什么增长、通胀和货币政策环境？过去三个月各有什么变化？请给出具体数据'
        '和各数据的公布时间。')
# 真正的原问(R31 首次为空的那一问,逐字;文件件 sha256 随行核对)
T3_VERBATIM = os.path.join(R31_ACC, 'session_T3_first_empty',
                           'question_verbatim.txt')
T3_SHA = '7360732af69f33012f56519c2fb4f928f71ae56a0488868babbc5f8212d109c9'


def check(name, ok, detail=''):
    ok = bool(ok)
    RESULTS.append(ok)
    print(('  ✅ ' if ok else '  ❌ ') + name +
          (' — ' + str(detail)[:300] if detail else ''), flush=True)
    return ok


def _mk_tree(tag, with_snapshot=True):
    """迷你引擎树: config 副本+提交的 11 月冻结快照(R31 B2 overlay 原件)。"""
    t = os.path.join(TMPG, 'tree_' + tag)
    shutil.copytree(os.path.join(ROOT, 'config'), os.path.join(t, 'config'))
    os.makedirs(os.path.join(t, 'data', 'daily'), exist_ok=True)
    snap = None
    if with_snapshot:
        snap = os.path.join(t, 'data', 'daily', SNAP_LATER)
        shutil.copy2(SNAP_SRC, snap)
    for fn in ('ea_20261105.json', 'japan_20261105.json', 'jp_20261105.json'):
        s = os.path.join(ROOT, 'data', 'daily', fn)
        if os.path.isfile(s):     # 干净安装提交的采集档(只读副本)
            shutil.copy2(s, os.path.join(t, 'data', 'daily', fn))
    return t, snap


def _code_tree(tag):
    """可跑正式 CLI 的迷你安装树=_mk_tree 数据面+代码副本(ia_cli.py/
    run_weekly.py/scripts 不含 __pycache__;env_config.py 仅当工作副本与提交
    版逐字节一致才复制——不接受含凭证副本)。→ (tree, env_config_copied)"""
    t, _ = _mk_tree(tag)
    for fn in ('ia_cli.py', 'run_weekly.py'):
        shutil.copy2(os.path.join(ROOT, fn), os.path.join(t, fn))
    shutil.copytree(os.path.join(ROOT, 'scripts'), os.path.join(t, 'scripts'),
                    ignore=shutil.ignore_patterns('__pycache__'))
    committed = subprocess.run(['git', 'show', 'HEAD:env_config.py'], cwd=ROOT,
                               capture_output=True, timeout=30).stdout
    with open(os.path.join(ROOT, 'env_config.py'), 'rb') as fh:
        same = (hashlib.sha256(fh.read()).hexdigest()
                == hashlib.sha256(committed).hexdigest())
    if same:
        shutil.copy2(os.path.join(ROOT, 'env_config.py'),
                     os.path.join(t, 'env_config.py'))
    return t, same


def _vintage(tree, ymd, drop_series=(), drop_facts=(), add_facts=(),
             override=(), base=None):
    """构造 as-of 版本夹具: 由冻结快照按**官方发布日 ≤版本日**截接(序列与
    事实行),可删序列/删事实行/加事实行/改指定观测值。写
    data/daily/research_snapshot_<ymd>.json。→ 路径。"""
    snap = base or json.load(open(SNAP_SRC, encoding='utf-8'))
    iso = '%s-%s-%s' % (ymd[:4], ymd[4:6], ymd[6:])
    reg = wd.load_registry(tree)['by_id']
    v = copy.deepcopy(snap)
    v['snapshot_id'] = 'FIXTURE_research_snapshot_%s' % ymd
    v['target_date'] = ymd
    v['fixture_note'] = ('Audit-R33 门夹具: 由冻结快照按官方发布日截接的构造'
                         '版本(%s),非真实历史快照' % ymd)
    ov = {(m, d): x for m, d, x in override}
    ss = {}
    for mid, s in (v.get('series_store') or {}).items():
        if mid in drop_series:
            continue
        keep = [(d, ov.get((mid, d), x)) for d, x in zip(s['dates'], s['values'])
                if eg._published_by(mid, (reg.get(mid) or {}).get('frequency'),
                                    d, iso)[0]]
        ss[mid] = {'dates': [d for d, _x in keep],
                   'values': [x for _d, x in keep]}
    v['series_store'] = ss
    facts = []
    for f in v.get('facts') or []:
        mid = f.get('metric_id')
        od = str(f.get('observation_date') or '')[:10]
        if mid in drop_facts or not od or od > iso:
            continue
        if eg._published_by(mid, (reg.get(mid) or {}).get('frequency'),
                            od, iso)[0]:
            facts.append(f)
    facts += [copy.deepcopy(x) for x in add_facts]
    v['facts'] = facts
    p = os.path.join(tree, 'data', 'daily',
                     'research_snapshot_%s.json' % ymd)
    with open(p, 'w', encoding='utf-8') as fh:
        json.dump(v, fh, ensure_ascii=False)
    return p


def _fact_of(snap, mid, od, value, **extra):
    f = copy.deepcopy(next(x for x in snap['facts']
                           if x.get('metric_id') == mid))
    f.update(observation_date=od, fact_id='%s@%s' % (mid, od), value=value)
    f.update(extra)
    return f


def _gate(tree, as_of, snap=None):
    reg = wd.load_registry(tree)
    return eg.gate_snapshot(copy.deepcopy(snap or json.load(
        open(SNAP_SRC, encoding='utf-8'))), as_of, root=tree, registry=reg)


def _facts(view, mid):
    return [f for f in view.get('facts') or [] if f.get('metric_id') == mid]


def _gap(view, kind):
    return next((g for g in (view.get('evidence_gate') or {}).get('gaps') or []
                 if g.get('gap') == kind), None)


def _ser(view, mid):
    return ((view.get('evidence_gate') or {}).get('series') or {}).get(mid) or {}


def _fake_step_ok(name, argv, timeout=180):
    return {'step': name, 'argv': list(argv), 'executed': True,
            'ok': True, 'exit_code': 0, 'semantic_ok': True,
            'note': None, 'duration_ms': 1, 'envelope': {'ok': True}}


def _offline_plan(tag, question, vintage=None):
    """离线 plan(S 步=替身信封;取数/证据口径/L1/索引走真代码)。"""
    import research_orchestrator as ro
    t, _snap = _mk_tree(tag)
    if vintage:
        _vintage(t, **vintage)
    seen = {}

    def _spy(name, argv, timeout=180):
        seen.setdefault('asof', os.environ.get('IA_EVIDENCE_ASOF'))
        seen.setdefault('snap', os.environ.get('IA_SNAPSHOT_PIN'))
        seen.setdefault('cal', os.environ.get('IA_CALENDAR_PIN'))
        return _fake_step_ok(name, argv, timeout)

    orig = ro.run_step
    ro.run_step = _spy
    try:
        rep = ro.run_research(question, root=t,
                              out_dir=os.path.join(t, 'out'))
    finally:
        ro.run_step = orig
    md = ''
    p = os.path.join(rep.get('report_dir') or '', 'report.md')
    if os.path.isfile(p):
        md = open(p, encoding='utf-8').read()
    return t, rep, md, seen


def _cli(argv, env=None, cwd=ROOT):
    e = dict(os.environ)
    e.update(env or {})
    r = subprocess.run([sys.executable, 'ia_cli.py'] + argv, cwd=cwd,
                       capture_output=True, text=True, timeout=900, env=e)
    try:
        data = json.loads(r.stdout)
    except Exception:                            # noqa: BLE001
        data = {'raw': ((r.stdout or '') + (r.stderr or ''))[-400:]}
    return r.returncode, data


# ══ 任务1: 统一历史证据口径 ═════════════════════════════════════════════
def sec_t1_a():
    print('§T1-a 延迟发布: 官方发布日优先, 62 天视界不再放行')
    t, _ = _mk_tree('t1a')
    snap = json.load(open(SNAP_SRC, encoding='utf-8'))
    check('§T1-a0 62 天发布视界常量已移除(规则②逐观测核官方发布日)',
          not hasattr(eg, '_PUBLISH_HORIZON_DAYS'))
    v = _gate(t, '2025-10-15', snap)
    s = _ser(v, 'UNEMPLOYMENT')
    check('§T1-a1 观测仅 44 天龄但未发布(9 月失业率 2025-11-20 发布)'
          '→2025-10-15 拒收',
          s.get('last_eligible') == '2025-08-01'
          and s.get('first_dropped', {}).get('date') == '2025-09-01'
          and s.get('first_dropped', {}).get('reason') == 'late_publication'
          and s.get('first_dropped', {}).get('publish') == '2025-11-20',
          json.dumps(s.get('first_dropped'), ensure_ascii=False))
    v = _gate(t, '2025-11-15', snap)
    egb = v['evidence_gate']
    for mid, pub in (('UNEMPLOYMENT', '2025-11-20'),
                     ('INDPRO', '2025-12-03'), ('CORE_PCE', '2025-12-05')):
        s = _ser(v, mid)
        f = _facts(v, mid)
        check(f'§T1-a2 {mid} 9 月值在 2025-11-15 拒收(官方发布日 {pub},'
              f'日历实录)事实行落在 {f[0]["observation_date"] if f else "-"}',
              s.get('last_eligible') == '2025-08-01'
              and s.get('first_dropped', {}).get('date') == '2025-09-01'
              and s.get('first_dropped', {}).get('reason') == 'late_publication'
              and s.get('first_dropped', {}).get('publish') == pub
              and str(s.get('first_dropped', {}).get('publish_basis')
                      ).startswith('calendar:')
              and len(f) == 1 and f[0]['observation_date'] == '2025-08-01'
              and '2025-09-01' not in v['series_store'][mid]['dates'],
              json.dumps(s.get('first_dropped'), ensure_ascii=False))
    check('§T1-a3 10 月 CPI(2025-10-24 已发布)照常入选: CPI@2025-09-01',
          _ser(v, 'CPI').get('last_eligible') == '2025-09-01'
          and _facts(v, 'CPI')[0]['fact_id'] == 'CPI@2025-09-01')
    v = _gate(t, '2025-11-20', snap)
    check('§T1-a4 2025-11-20: 9 月失业率当日发布→入选 4.4;工业生产/核心'
          'PCE 仍拒',
          _facts(v, 'UNEMPLOYMENT')[0]['fact_id'] == 'UNEMPLOYMENT@2025-09-01'
          and _facts(v, 'UNEMPLOYMENT')[0]['value'] == 4.4
          and _facts(v, 'INDPRO')[0]['observation_date'] == '2025-08-01'
          and _facts(v, 'CORE_PCE')[0]['observation_date'] == '2025-08-01')
    v = _gate(t, '2025-12-03', snap)
    check('§T1-a5 2025-12-03: 工业生产 9 月值入选;核心 PCE 仍拒',
          _facts(v, 'INDPRO')[0]['fact_id'] == 'INDPRO@2025-09-01'
          and _facts(v, 'INDPRO')[0]['value'] == 101.668
          and _facts(v, 'CORE_PCE')[0]['observation_date'] == '2025-08-01')
    v = _gate(t, '2025-12-05', snap)
    check('§T1-a6 2025-12-05: 核心 PCE 9 月值入选 126.94',
          _facts(v, 'CORE_PCE')[0]['fact_id'] == 'CORE_PCE@2025-09-01'
          and _facts(v, 'CORE_PCE')[0]['value'] == 126.94)
    v = _gate(t, '2026-01-10', snap)
    s = _ser(v, 'NFP')
    d = v['series_store']['NFP']['dates']
    check('§T1-a7 观测龄 131 天(>62)但未发布: 9/10 月非农在 2026-01-10 '
          '仍拒(日历 2026-01-22),11 月值入选',
          '2025-09-01' not in d and '2025-10-01' not in d
          and '2025-11-01' in d
          and s.get('first_dropped', {}).get('publish') == '2026-01-22')
    v = _gate(t, '2026-01-22', snap)
    check('§T1-a8 2026-01-22(日历发布日): 9/10 月非农入选',
          '2025-09-01' in v['series_store']['NFP']['dates']
          and '2025-10-01' in v['series_store']['NFP']['dates'])
    v = _gate(t, '2025-11-15', snap)
    g = _gap(v, 'historical_version_missing')
    check('§T1-a9 无历史版本: 事实全部 ≤截止且逐行 historical_version_'
          'missing+顶层缺口点名',
          bool(g) and v['facts']
          and all(f['observation_date'] <= '2025-11-15' for f in v['facts'])
          and all((f.get('evidence_gate') or {}).get('version_status')
                  == 'historical_version_missing' for f in v['facts'])
          and v['evidence_gate']['vintage']['basis']
          == 'no_asof_vintage_snapshot', f"n_facts={len(v['facts'])}")
    vis, held = rmp.policy_doc_facts_visible('2025-11-15')
    vis2, held2 = rmp.policy_doc_facts_visible('2026-11-18')
    check('§T1-a10 政策文档按发布日期过滤: 2025-11-15 全部扣留'
          '(FOMC 2026-10 纪要 2026-11-18 发布);2026-11-18 起可见',
          vis == [] and [d['doc_id'] for d in held] == ['FOMC-MINUTES-2026-10']
          and len(vis2) == 1 and held2 == [])
    v = _gate(t, '2026-11-22', snap)
    check('§T1-a11 非历史视图(截止日=快照版本日)证据面与源快照一致',
          len(v['facts']) == len(snap['facts'])
          and v['evidence_gate']['historical_view'] is False)


def sec_t1_b():
    print('§T1-b 快报与终值')
    t, _ = _mk_tree('t1b')
    snap = json.load(open(SNAP_SRC, encoding='utf-8'))
    v = _gate(t, '2025-04-10', snap)
    s = _ser(v, 'EA_HICP_YOY')
    fd = s.get('first_dropped') or {}
    check('§T1-b1 无冻结版本: HICP 2025-03 快报日(04-01)后、终值日'
          '(04-16)前→当时数据版本不可得(终值在手不可冒充)',
          fd.get('date') == '2025-03-01'
          and fd.get('reason') == 'data_version_unavailable'
          and fd.get('version_available_on') == '2025-04-16'
          and fd.get('version_basis') == 'calendar:final_publish_on'
          and s.get('last_eligible') == '2025-02-01'
          and '2025-03-01' not in v['series_store']['EA_HICP_YOY']['dates'],
          json.dumps(fd, ensure_ascii=False))
    v = _gate(t, '2025-04-16', snap)
    check('§T1-b2 终值发布日起入选(终值 2.2)',
          _ser(v, 'EA_HICP_YOY').get('last_eligible') == '2025-03-01'
          and v['series_store']['EA_HICP_YOY']['values'][-1] == 2.2)
    t2, _ = _mk_tree('t1b2')
    _vintage(t2, '20250410',
             add_facts=[_fact_of(snap, 'EA_HICP_YOY', '2025-03-01', 2.4,
                                 derived={'fixture': '快报事实行'})],
             override=[('EA_HICP_YOY', '2025-03-01', 2.4)])
    v = _gate(t2, '2025-04-10', snap)
    s = _ser(v, 'EA_HICP_YOY')
    f = _facts(v, 'EA_HICP_YOY')
    check('§T1-b3 快报期冻结版本在场: 取当时冻结的快报值 2.4(非较晚版本的'
          '终值 2.2),随行标 快报/初值+终值日',
          v['series_store']['EA_HICP_YOY']['values'][-1] == 2.4
          and s.get('vintage') == 'as_of_vintage'
          and s.get('value_version') == 'flash_or_preliminary'
          and s.get('final_publish_on') == '2025-04-16'
          and 'EA_HICP_YOY' in v['evidence_gate']['vintage'][
              'preliminary_value_series']
          and len(f) == 1 and f[0]['value'] == 2.4
          and f[0]['evidence_gate'].get('value_version')
          == 'flash_or_preliminary'
          and f[0]['evidence_gate'].get('final_publish_on') == '2025-04-16'
          and v['evidence_gate']['counts']['facts_kept'] == 1,
          json.dumps(f[0].get('evidence_gate') if f else s,
                     ensure_ascii=False))
    v = _gate(t2, '2025-04-16', snap)
    check('§T1-b4 终值发布日重跑而数据树无更新版本: 仍绑同一冻结版本'
          '(快报值),较晚版本的终值不补入',
          v['series_store']['EA_HICP_YOY']['values'][-1] == 2.4
          and v['evidence_gate']['vintage']['vintage_snapshot_id']
          == 'FIXTURE_research_snapshot_20250410')


def sec_t1_c():
    print('§T1-c 截止后回填')
    t, _ = _mk_tree('t1c')
    snap = json.load(open(SNAP_SRC, encoding='utf-8'))
    _vintage(t, '20251110', drop_series=('EA_HICP_YOY',))
    v = _gate(t, '2025-11-15', snap)
    g = _gap(v, 'series_not_in_as_of_vintage')
    r = wd.metric_series('EA_HICP_YOY', snapshot=v, root=t)
    check('§T1-c1 序列不在 as-of 冻结版本内(较晚版本才回填)→空壳+缺口点名,'
          '不出事实,取数入口返回原因不回落',
          v['series_store']['EA_HICP_YOY']['evidence_gate_excluded'][
              'reason'] == 'not_in_as_of_vintage'
          and bool(g) and 'EA_HICP_YOY' in g['series']
          and not _facts(v, 'EA_HICP_YOY')
          and isinstance(r, tuple) and r[0] is None
          and 'not_in_as_of_vintage' in str(r[1]),
          str(r[1])[:120] if isinstance(r, tuple) else r)
    _vintage(t, '20251201')
    v = _gate(t, '2025-12-05', snap)
    g = _gap(v, 'published_observation_not_in_bound_version')
    ex = {e['metric_id']: e for e in (g or {}).get('examples') or []}
    check('§T1-c2 版本日(12-01)后、研究时点(12-05)前发布的观测(核心 PCE '
          '9 月值 12-05/工业生产 9 月值 12-03)不在所绑版本内→不补入'
          '(末点仍 8 月)+缺口逐条点名',
          _ser(v, 'CORE_PCE').get('last_eligible') == '2025-08-01'
          and _ser(v, 'INDPRO').get('last_eligible') == '2025-08-01'
          and bool(g) and {'CORE_PCE', 'INDPRO'} <= set(g['series'])
          and ex.get('CORE_PCE', {}).get('observation_date') == '2025-09-01'
          and ex.get('CORE_PCE', {}).get('first_publish') == '2025-12-05'
          and ex.get('INDPRO', {}).get('first_publish') == '2025-12-03',
          json.dumps(g, ensure_ascii=False)[:200] if g else None)
    check('§T1-c3 同一时点已入所绑版本的观测照常(9 月失业率 11-20 发布'
          '≤版本日)',
          _facts(v, 'UNEMPLOYMENT')[0]['fact_id'] == 'UNEMPLOYMENT@2025-09-01')


def sec_t1_d():
    print('§T1-d 旧快照有序列但缺事实行')
    t, _ = _mk_tree('t1d')
    snap = json.load(open(SNAP_SRC, encoding='utf-8'))
    _vintage(t, '20251203', drop_facts=('INDPRO', 'CORE_PCE', 'UNEMPLOYMENT'))
    v = _gate(t, '2025-12-05', snap)
    got = {mid: (_facts(v, mid)[0]['fact_id'], _facts(v, mid)[0]['value'],
                 _facts(v, mid)[0]['evidence_gate'])
           for mid in ('INDPRO', 'CORE_PCE', 'UNEMPLOYMENT') if _facts(v, mid)}
    later = {f['metric_id']: f.get('value') for f in snap['facts']}
    check('§T1-d1 事实行缺而序列在: 自所绑版本序列重建(工业生产 9 月/'
          '失业率 9 月/核心 PCE 8 月),逐行标 重建@截止+as-of冻结版本+值来源',
          got.get('INDPRO', (None,))[0] == 'INDPRO@2025-09-01'
          and got.get('INDPRO', (None, None))[1] == 101.668
          and got.get('UNEMPLOYMENT', (None,))[0] == 'UNEMPLOYMENT@2025-09-01'
          and got.get('UNEMPLOYMENT', (None, None))[1] == 4.4
          and got.get('CORE_PCE', (None,))[0] == 'CORE_PCE@2025-08-01'
          and all(m[2].get('rebuilt_at_as_of') is True
                  and m[2].get('version_status') == 'as_of_vintage'
                  and m[2].get('value_source_snapshot_id')
                  == 'FIXTURE_research_snapshot_20251203'
                  and m[2].get('value_source_target_date') == '2025-12-03'
                  for m in got.values())
          and v['evidence_gate']['counts']['facts_rebuilt_from_vintage_series']
          >= 3,
          json.dumps(got, ensure_ascii=False)[:300])
    check('§T1-d2 不取较晚版本的事实值冒充当时值(较晚事实行: 工业生产 '
          '%s/核心 PCE %s/失业率 %s 均不在视图),且无晚于截止的事实'
          % (later.get('INDPRO'), later.get('CORE_PCE'),
             later.get('UNEMPLOYMENT')),
          all(f['observation_date'] <= '2025-12-05' for f in v['facts'])
          and not ({later.get('INDPRO'), later.get('CORE_PCE'),
                    later.get('UNEMPLOYMENT')}
                   & {f.get('value') for f in v['facts']
                      if f.get('metric_id') in got}))
    t2, _ = _mk_tree('t1d2')
    _vintage(t2, '20251110', drop_facts=('UNEMPLOYMENT',),
             add_facts=[_fact_of(snap, 'UNEMPLOYMENT', '2025-08-01', 4.3,
                                 derived={'fixture': 'V1 事实行自带派生'})])
    v = _gate(t2, '2025-11-15', snap)
    f = _facts(v, 'UNEMPLOYMENT')
    check('§T1-d3 所绑版本自有事实行且合格→原值原派生保留(不重建)',
          len(f) == 1 and f[0]['fact_id'] == 'UNEMPLOYMENT@2025-08-01'
          and f[0]['derived'] == {'fixture': 'V1 事实行自带派生'}
          and not f[0]['evidence_gate'].get('rebuilt_at_as_of')
          and f[0]['evidence_gate'].get('version_status') == 'as_of_vintage'
          and v['evidence_gate']['counts']['facts_kept'] == 1,
          json.dumps(f[0].get('evidence_gate') if f else None,
                     ensure_ascii=False))
    later = copy.deepcopy(snap)
    later['facts'].append(_fact_of(
        snap, 'CORE_PCE', '2025-09-01', 126.94, fixture_backfill=True))
    t3, _ = _mk_tree('t1d3')
    _vintage(t3, '20251203')
    v = _gate(t3, '2025-12-05', later)
    g = _gap(v, 'published_fact_not_in_bound_version')
    check('§T1-d4 较晚快照截止后回填的事实行(核心 PCE@2025-09-01,研究时点'
          '已发布但不在所绑版本内)→不交付+缺口点名',
          not [f for f in _facts(v, 'CORE_PCE')
               if f['observation_date'] == '2025-09-01']
          and bool(g) and g['series'] == ['CORE_PCE'],
          json.dumps(g, ensure_ascii=False)[:160] if g else None)


def sec_t1_e():
    print('§T1-e 缺历史版本明标+旧快照渲染(离线 plan)')
    t, rep, md, seen = _offline_plan('t1e', Q_T1)
    rp = rep.get('research_plan') or {}
    rows = ((rep.get('layers') or {}).get('L1_事实层') or {}).get('rows') or []
    idx = rep.get('evidence_index') or []
    bad = [r for r in rows if r['metric_id'] in ('UNEMPLOYMENT', 'INDPRO',
                                                 'CORE_PCE')
           and r['observation_date'] != '2025-08-01']
    refs = {str(e.get('ref')) for e in idx}
    check('§T1-e1 2025-11-15 工单: 研究截止=2025-11-15(运行级钉死),L1 三项'
          '事实行落在 8 月且带缺历史版本标记',
          seen.get('asof') == '2025-11-15'
          and (rep.get('run') or {}).get('evidence_asof') == '2025-11-15'
          and not bad and len([r for r in rows if r['metric_id'] in (
              'UNEMPLOYMENT', 'INDPRO', 'CORE_PCE')]) == 3
          and all((r.get('evidence_gate') or {}).get('version_status')
                  == 'historical_version_missing'
                  for r in rows if r['metric_id'] in ('UNEMPLOYMENT',
                                                      'INDPRO', 'CORE_PCE')),
          f"asof={seen.get('asof')} bad={[(r['metric_id'], r['observation_date']) for r in bad]}")
    check('§T1-e2 证据索引/L1 无 9 月失业率·工业生产·核心 PCE 引用',
          not ({'UNEMPLOYMENT@2025-09-01', 'INDPRO@2025-09-01',
                'CORE_PCE@2025-09-01'} & refs)
          and all('@2025-09-01' not in str(r.get('source', {}).get('id'))
                  for r in rows if r['metric_id'] in ('UNEMPLOYMENT',
                                                      'INDPRO', 'CORE_PCE')))
    check('§T1-e3 report.md 渲染: 缺口行(缺历史版本/采集档晚于时点)+L1 行'
          '后缀[口径:重建@截止][版本:缺历史版本]',
          '缺口[historical_version_missing]' in md
          and '缺口[collector_files_after_as_of]' in md
          and '[口径:重建@截止] [版本:缺历史版本]' in md
          and 'UNEMPLOYMENT = 4.3' in md and '@2025-08-01' in md)
    check('§T1-e4 政策文档按发布日期过滤: 计划面 policy_doc_facts 为空,'
          '扣留清单点名,report.md 渲染未纳入行',
          rp.get('policy_doc_facts') == []
          and [d['doc_id'] for d in (rp.get('policy_doc_withheld') or [])]
          == ['FOMC-MINUTES-2026-10']
          and '政策文档(按发布日期过滤): 可见 0 份' in md
          and 'FOMC 2026年10月会议纪要(2026-11-18 发布)' in md)
    t2, rep2, md2, seen2 = _offline_plan(
        't1e2', '以 2025-12-05 为研究时点，美国、中国、欧元区、日本在最新'
        '一期分别处于什么增长、通胀和货币政策环境？过去三个月各有什么变化？'
        '请给出具体数据和各数据的公布时间。',
        vintage=dict(ymd='20251203',
                     drop_facts=('INDPRO', 'CORE_PCE', 'UNEMPLOYMENT')))
    rows2 = ((rep2.get('layers') or {}).get('L1_事实层') or {}).get('rows') or []
    r = {x['metric_id']: x for x in rows2}
    check('§T1-e5 有 as-of 冻结版本时: L1 行标[版本:as-of冻结版本],渲染'
          '「旧快照有序列但缺事实行」重建行与「截止后回填不补入」缺口行',
          seen2.get('asof') == '2025-12-05'
          and r.get('INDPRO', {}).get('observation_date') == '2025-09-01'
          and (r.get('INDPRO', {}).get('evidence_gate') or {}).get(
              'version_status') == 'as_of_vintage'
          and '缺口[published_observation_not_in_bound_version]' in md2
          and '旧快照有序列但缺事实行' in md2
          and '[口径:重建@截止] [版本:as-of冻结版本]' in md2
          and '缺口[series_not_in_as_of_vintage]' in md2,
          f"asof={seen2.get('asof')} INDPRO={json.dumps(r.get('INDPRO'), ensure_ascii=False)[:160]}")


def sec_t1_f():
    print('§T1-f 采集档通道(提交的 jp_20261105 采集档内 NIKKEI225 序列)')
    src = os.path.join(ROOT, 'data', 'daily', 'jp_20261105.json')
    if not os.path.isfile(src):
        check('§T1-f 采集档夹具在场', False, src)
        return
    k = eg.ENV_KEY
    try:
        os.environ.pop(k, None)
        r0 = wd.metric_series('NIKKEI225', root=ROOT)
        s0 = r0[0]
        ok0 = isinstance(s0, dict) and len(s0.get('dates') or []) > 200
        os.environ[k] = '2026-10-31'
        r1 = wd.metric_series('NIKKEI225', root=ROOT)
        s1 = r1[0]
        r3 = wd.metric_series('EA_HICP_YOY', root=ROOT)
        os.environ[k] = '2026-11-10'
        r2 = wd.metric_series('NIKKEI225', root=ROOT)
        s2 = r2[0]
    finally:
        os.environ.pop(k, None)
    check('§T1-f1 无截止: 采集档通道原样(无版本标记)',
          ok0 and 'evidence_gate' not in s0
          and s0.get('source') == '采集档 jp_20261105.json')
    check('§T1-f2 截止早于唯一采集档(非修订口径序列): 取该档+标 '
          'historical_version_missing(缺历史版本明标)+值来源档,晚观测剔除,'
          '逐观测统计与版本标记并存',
          isinstance(s1, dict)
          and (s1.get('evidence_gate') or {}).get('version_status')
          == 'historical_version_missing'
          and (s1.get('evidence_gate') or {}).get('value_source_file')
          == 'jp_20261105.json'
          and s1['dates'][-1] == '2026-10-30'
          and (s1.get('evidence_gate') or {}).get('n_late_observation') == 3,
          json.dumps((s1.get('evidence_gate') if isinstance(s1, dict)
                      else r1), ensure_ascii=False))
    check('§T1-f3 截止不早于采集档: 标 collector_file_le_asof(版本可确认)',
          isinstance(s2, dict)
          and (s2.get('evidence_gate') or {}).get('version_status')
          == 'collector_file_le_asof')
    check('§T1-f4 修订口径序列(EA_HICP_YOY)无 ≤截止采集档→版本不可得拒答'
          '(不取最新修订值冒充)',
          r3[0] is None and '数据版本不可得' in str(r3[1]), str(r3)[:160])


def sec_t1_g():
    print('§T1-g 正式 CLI plan(真实子进程,代码副本树)@2025-11-15')
    if os.environ.get('IA_R33_GATE_SKIP_CLI') == '1':
        # 开发期跳过开关(仅本机迭代用;CI/正式门恒跑)
        print('  (IA_R33_GATE_SKIP_CLI=1: 本段跳过)')
        return
    t, ec_ok = _code_tree('t1g')
    if not ec_ok:
        check('§T1-g0 env_config.py 工作副本与提交版一致(不含凭证副本)',
              False)
        return
    qf = os.path.join(TMPG, 'q_t1.txt')
    with open(qf, 'w', encoding='utf-8') as fh:
        fh.write(Q_T1)
    t0 = time.time()
    rc, d = _cli(['research-one', '--stage', 'plan', '--question-file', qf,
                  '--engine-root', t])
    dt = time.time() - t0
    data = d.get('data') or {}
    rd = data.get('report_dir') or ''
    check('§T1-g1 plan rc=0/ok/run_ok,报告目录在隔离树内',
          rc == 0 and d.get('ok') and data.get('run_ok')
          and rd.startswith(t + os.sep) and os.path.isdir(rd),
          f"rc={rc} {dt:.0f}s run_ok={data.get('run_ok')} "
          f"{str(d.get('error') or d.get('raw') or '')[:200]}")
    if not os.path.isdir(rd):
        return
    rep = json.load(open(os.path.join(rd, 'report.json'), encoding='utf-8'))
    rows = ((rep.get('layers') or {}).get('L1_事实层') or {}).get('rows') or []
    idx = {str(e.get('ref')) for e in (rep.get('evidence_index') or [])}
    md = open(os.path.join(rd, 'report.md'), encoding='utf-8').read()
    env = json.load(open(os.path.join(rd, 'AGENT_SEAT_ENVELOPE.json'),
                         encoding='utf-8'))
    r = {x['metric_id']: x for x in rows
         if x['metric_id'] in ('UNEMPLOYMENT', 'INDPRO', 'CORE_PCE')}
    bad_steps = [s.get('step') for s in (rep.get('steps') or [])
                 if s.get('executed') and not s.get('ok')
                 and not s.get('honest_refusal')]
    check('§T1-g2 回执研究截止=2025-11-15;S 步全部执行且无失败步',
          (rep.get('run') or {}).get('evidence_asof') == '2025-11-15'
          and not bad_steps, f"bad_steps={bad_steps[:8]}")
    check('§T1-g3 L1/证据索引/席位信封: 三项 9 月值零引用,事实行=8 月值且标'
          '缺历史版本',
          len(r) == 3
          and all(x['observation_date'] == '2025-08-01' for x in r.values())
          and not ({'UNEMPLOYMENT@2025-09-01', 'INDPRO@2025-09-01',
                    'CORE_PCE@2025-09-01'} & idx)
          and 'UNEMPLOYMENT@2025-09-01' not in json.dumps(env)
          and 'INDPRO@2025-09-01' not in json.dumps(env)
          and 'CORE_PCE@2025-09-01' not in json.dumps(env)
          and all((x.get('evidence_gate') or {}).get('version_status')
                  == 'historical_version_missing' for x in r.values()),
          {k: v['observation_date'] for k, v in r.items()})
    check('§T1-g4 report.md 缺口行+政策文档扣留行',
          '缺口[historical_version_missing]' in md
          and '政策文档(按发布日期过滤): 可见 0 份' in md
          and 'FOMC 2026年10月会议纪要(2026-11-18 发布)' in md)
    faces = (((env.get('reader_map_contract') or {}).get('engine_faces'))
             or {})
    check('§T1-g5 席位信封引擎面: 政策文档事实为空(研究时点后发布的纪要'
          '不进信封);点锚=3个月前/最新一期@2025-11-15',
          faces.get('policy_doc_facts') == []
          and [a.get('as_of') for a in (faces.get('point_anchors') or [])]
          == ['2025-08-15', '2025-11-15'],
          json.dumps(faces.get('point_anchors'), ensure_ascii=False))


def main():
    print('Audit-R33 门 (HEAD %s)' % WORKTREE_HEAD[:12])
    try:
        sec_t1_a()
        sec_t1_b()
        sec_t1_c()
        sec_t1_d()
        sec_t1_e()
        sec_t1_f()
        sec_t1_g()
    finally:
        n_ok = sum(1 for x in RESULTS if x)
        n = len(RESULTS)
        print('=== R33 门: %d/%d ===' % (n_ok, n))
        shutil.rmtree(TMPG, ignore_errors=True)
    return 0 if all(RESULTS) else 1


if __name__ == '__main__':
    sys.exit(main())
