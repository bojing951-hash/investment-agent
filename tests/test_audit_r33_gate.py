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
任务2 政策时态: 事件 × 断言时点(段内显式「截至 X」优先于研究截止日)×
实施状态逐分句核验;R31/R32 规则按原文照旧;正式 attach 拒收「截至 9 月
20 日，9 月 24 日生效的加息已经实施」、接收「…尚未生效」;官方目标缺证
的草稿处理不变;入库归档判定档(r30–r32 共 14 份)重验零新增违规。
夹具说明: 冻结快照=提交的 R31 B2 overlay 原件(真实);as-of 版本夹具=由该快照
按官方发布日截接的**构造版本**(snapshot_id 前缀 FIXTURE_,fixture_note 随行),
非真实历史快照——只用于核验绑定规则,不作为任何交付的证据。
"""
import contextlib
import copy
import glob
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

import agent_judgment as aj                    # noqa: E402
import evidence_gate as eg                       # noqa: E402
import release_calendar as rc                    # noqa: E402
import research_map_planner as rmp                # noqa: E402
import workbench_data as wd                       # noqa: E402

TMPG = tempfile.mkdtemp(prefix='r33gate_')
_t2_mids = {m['metric_id'] for m in (wd.load_registry(ROOT).get('metrics')
                                       or []) if m.get('metric_id')}
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


FIX_R33 = os.path.join(HERE, 'fixtures_r33')


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


# ═══ 任务2: 政策时态(政策事件 × 断言时点 × 实施状态) ═══
SENT_A = '截至 9 月 20 日，9 月 24 日生效的加息已经实施'
SENT_B = '截至 9 月 20 日，9 月 24 日生效的加息尚未生效'
_POL_Q = ('对比角度换一个：2026年11月，美国与欧元区的增长和通胀环境相比'
          '3个月前各有什么变化？日本央行政策利率处于什么水平，距离上次调整'
          '过了多久？')


def _mk_judgment(text):
    return {'schema_version': '1.1',
            'agent_declaration': {'attribution': 'ai_inferred'},
            'l3': {'contradictions': [
                {'id': 'C1', 'statement': text,
                 'competing_explanations': [
                     {'id': 'E1', 'text': 'a', 'evidence_refs': ['r1']},
                     {'id': 'E2', 'text': 'b', 'evidence_refs': ['r1']}],
                 'evidence_refs': ['r1']}]},
            'l4': {'scenarios': []}, 'reader_map': {}}


def _pol_codes(text, as_of, events):
    res = aj.validate_judgment(_mk_judgment(text), {'r1'},
                               {'JP_POLICY_TARGET'},
                               policy_events=events, as_of=as_of)
    return [v['code'] for v in res['violations']
            if v['code'].startswith('POL')]


def _t2_valid_judgment(mid_a, mid_b, statement):
    """合规判定档母本(与 R36 attach 套件同构): 结构纪律与契约验证全过,
    只换首条陈述——隔离出政策时态单条规则。"""
    return {
        'schema_version': '1.1',
        'agent_declaration': {'attribution': 'ai_inferred',
                              'note': '门夹具'},
        'l3': {
            'contradictions': [{
                'id': 'CON-1', 'statement': statement,
                'basis': '基于证据索引的推断',
                'competing_explanations': ['解释一(基准)', '解释二(反例)'],
                'evidence_refs': ['FACT_A@2026-09-20',
                                  'VP-VIEW-20260920-001']}],
            'mechanism_chains': [{
                'id': 'MECH-1', 'name': '合成链',
                'links': [
                    {'step': 1, 'text': 'E1 环(引擎可验证)',
                     'evidence_level': 'E1',
                     'evidence_refs': ['FACT_A@2026-09-20']},
                    {'step': 3, 'text': 'E3 环(纯叙事)',
                     'evidence_level': 'E3',
                     'falsification_metric': mid_a}]}]},
        'l4': {'scenarios': [
            {'id': 'SCN-A', 'role': '基准', 'rows': {
                'scenario': '情景A(假设非预测): 合成基准情景',
                'asset_direction': {'direction': '上行',
                                    'confidence_tier': '有相关证据',
                                    'text': '合成方向判断',
                                    'evidence_refs': ['FACT_A@2026-09-20']},
                'sensitive_variables': [mid_a],
                'falsification': {'metric_id': mid_b,
                                  'threshold': '突破合成阈值 4.5'},
                'trigger': {'condition': '合成可观测条件',
                            'deadline': '2027-06-30'}}},
            {'id': 'SCN-B', 'role': '反例', 'rows': {
                'scenario': '情景B(假设非预测): 合成反例情景',
                'asset_direction': {'direction': '区间',
                                    'confidence_tier': '纯逻辑推理',
                                    'text': '合成反例方向',
                                    'evidence_refs': []},
                'sensitive_variables': [mid_b],
                'falsification': {'metric_id': mid_a,
                                  'threshold': '跌破合成阈值 2.5'},
                'trigger': {'condition': '合成反例条件',
                            'deadline': '2027-06-30'}}}]},
        'reader_map': {}}


def _t2_synth_run(tag, as_of, statement):
    """合成运行目录(report.json+report.md+判定档);root=带日历/注册表的
    最小树。返回 (tree, run_dir, judgment_path)。"""
    import research_orchestrator as ro
    t, _ = _mk_tree(tag)
    mids = sorted({m['metric_id'] for m in (wd.load_registry(ROOT).get('metrics')
                                            or []) if m.get('metric_id')})
    a, b = mids[0], mids[1]
    rep = {
        'schema_version': '2.0', 'pipeline_version': ro.PIPELINE_VERSION,
        'run': {'question': '合成问题', 'ts_utc': '20260920T000000Z',
                'archive_requested': False, 'git_head': None,
                'evidence_asof': as_of},
        'steps': [], 'fanout': {'requested': False},
        'layers': {
            'L1_事实层': {'available': True, 'snapshot_id': 'SYNTH',
                          'target_date': '2026-09-20', 'n_facts_total': 2,
                          'rows': [], 'note': None},
            'L2_机构观点层': {'views': {'available': True, 'n': 1,
                                        'rows': [{'view_id': 'VIEW-20260920-001',
                                                  'view_label': 'SUPPORTING'}],
                                        'n_bad_quarantined': 0}, 'note': '合成'},
            'L3_AI推断层': {'produced': False, 'note': '零模型管线: 不代写'},
            'L4_条件情景层': {'produced': False, 'note': '零模型管线: 不代写'}},
        'evidence_index': [
            {'ref': 'FACT_A@2026-09-20', 'kind': 'snapshot_fact',
             'metric_id': a},
            {'ref': 'FACT_B@2026-09-20', 'kind': 'snapshot_fact',
             'metric_id': b},
            {'ref': 'VP-VIEW-20260920-001', 'kind': 'vp_sidecar',
             'view_label': '合成观点'}],
        'notes': [], 'run_ok': True}
    rd = os.path.join(TMPG, 'run_' + tag)
    os.makedirs(rd)
    with open(os.path.join(rd, 'report.json'), 'w', encoding='utf-8') as f:
        json.dump(rep, f, ensure_ascii=False, indent=2)
    with open(os.path.join(rd, 'report.md'), 'w', encoding='utf-8') as f:
        f.write(ro._render_md(rep))
    jp = os.path.join(rd, 'judgment.json')
    with open(jp, 'w', encoding='utf-8') as f:
        json.dump(_t2_valid_judgment(a, b, statement), f, ensure_ascii=False,
                  indent=2)
    return t, rd, jp


def _t2_attach_res(rd):
    with open(os.path.join(rd, 'report.json'), encoding='utf-8') as f:
        return json.load(f)


def sec_t2():
    print('═══ 任务2: 政策时态(事件 × 断言时点 × 实施状态) ═══')
    events = aj.collect_policy_events(os.path.join(
        ROOT, 'config', 'release_calendar.json'))
    ev_jp = [e for e in events
             if e['entry_id'] == 'RC-JP-BOJ-TARGET-2026-09']
    check('§T2-0 事件面: JP 2026-09-18 决议(公告 09-18)/09-24 生效/目标 1.25',
          len(ev_jp) == 1 and ev_jp[0]['first_publish'] == '2026-09-18'
          and ev_jp[0]['effective_on'] == '2026-09-24',
          f'{ev_jp}')
    # a. 误句(用户点名的反例): 带空格/不带空格/显式全日期/无 as_of/晚 as_of
    a1 = _pol_codes(SENT_A, '2026-09-20', events)
    a2 = _pol_codes('截至9月20日，9月24日生效的加息已经实施', '2026-09-20',
                    events)
    a3 = _pol_codes('截至 2026 年 9 月 20 日，日本央行 9 月 24 日生效的加息'
                    '已经实施', None, events)
    a4 = _pol_codes(SENT_A, '2026-11-23', events)
    a5 = _pol_codes('截止2026-09-20: 20260924 生效的加息已落地', '2026-09-20',
                    events)
    a6 = _pol_codes('日本央行9月18日决议,9月24日生效,目前利率已升至1.25%',
                    '2026-09-20', events)
    check('§T2-a 误句「截至 9 月 20 日，9 月 24 日生效的加息已经实施」→'
          'POL-EFF-EARLY-CLAIM 恰一条: 空格日期/紧凑日期/无 as_of(年取决议年)/'
          '运行级截止日晚于生效日(段内显式时点优先)/冒号+紧凑日期形;'
          '整段现行口径(c6)仍由逐分句模型产出',
          a1 == ['POL-EFF-EARLY-CLAIM'] and a2 == ['POL-EFF-EARLY-CLAIM']
          and a3 == ['POL-EFF-EARLY-CLAIM'] and a4 == ['POL-EFF-EARLY-CLAIM']
          and a5 == ['POL-EFF-EARLY-CLAIM']
          and a6 == ['POL-EFF-EARLY-CLAIM'],
          f'{a1} {a2} {a3} {a4} {a5} {a6}')
    b1 = _pol_codes('截至 9 月 20 日尚未生效', '2026-09-20', events)
    b2 = _pol_codes(SENT_B, '2026-09-20', events)
    b3 = _pol_codes(SENT_B, '2026-11-23', events)
    b4 = _pol_codes(SENT_B, None, events)
    # 置于决议陈述内的正句(基线第二缺陷: R32 生效日绑定把「9月20日尚未
    # 生效」读成 9 月 20 日生效→POL-EFF-DATE 误拒正确表述)
    b5 = _pol_codes('日本央行9月18日决议加息;时态核对: 截至9月20日尚未'
                   '生效，9月24日生效', '2026-11-23', events)
    b6 = _pol_codes('日本央行 9 月 18 日决议加息至 1.25%，截至 9 月 20 日'
                   '尚未生效，9 月 24 日生效', '2026-09-20', events)
    check('§T2-b 正句「截至 9 月 20 日尚未生效」→零违规: 单句/as_of 在'
          '生效前/生效后/缺席;置于日银决议陈述内(带空格与不带空格)同判'
          '零违规(未然形的「生效」不是生效日标签)',
          b1 == [] and b2 == [] and b3 == [] and b4 == []
          and b5 == [] and b6 == [],
          f'{b1} {b2} {b3} {b4} {b5} {b6}')
    # c. 生效后仍写待生效 / 公告前以既成事实提及
    c1 = _pol_codes('9月24日生效的加息尚未生效', '2026-09-26', events)
    c2 = _pol_codes('9月24日生效的加息尚未生效', '2026-09-20', events)
    c3 = _pol_codes('日本央行9月18日决议加息;公布时该决议尚未生效,'
                    '9月24日生效', '2026-11-23', events)
    c4 = _pol_codes('日本央行9月18日决议加息,9月24日生效,不存在待生效问题',
                    '2026-11-23', events)
    c5 = _pol_codes('日本央行9月18日决议,9月24日生效;截至9月20日尚未生效',
                    '2026-11-23', events)
    check('§T2-c 生效后仍写尚未生效→POL-EFF-LATE-PENDING;生效前同一句零违规;'
          '历史叙述(公布时)/否定语境(不存在待生效问题)/段内显式更早时点豁免',
          c1 == ['POL-EFF-LATE-PENDING'] and c2 == [] and c3 == []
          and c4 == [] and c5 == [],
          f'{c1} {c2} {c3} {c4} {c5}')
    d1 = _pol_codes('日本央行9月18日决议加息至1.25%，9月24日生效',
                    '2026-09-10', events)
    d2 = _pol_codes('市场预期日本央行9月18日可能加息至1.25%', '2026-09-10',
                    events)
    d3 = _pol_codes('日本央行将于9月18日公布利率决议', '2026-09-10', events)
    d4 = _pol_codes('日本央行9月18日召开货币政策会议', '2026-09-10', events)
    check('§T2-d 断言时点早于公告日而以既成事实提及决议→'
          'POL-EFF-DECISION-NOT-YET-KNOWN(恰一条,R31/R32 规则不再跳过);'
          '预期/将然/会议日程口径零违规',
          d1 == ['POL-EFF-DECISION-NOT-YET-KNOWN'] and d2 == [] and d3 == []
          and d4 == [], f'{d1} {d2} {d3} {d4}')
    # e. 不写日期的实施断言
    e1 = _pol_codes('截至9月20日，日本央行加息已经实施', '2026-09-20', events)
    e2 = _pol_codes('截至9月20日，日本央行加息已经实施', '2026-11-23', events)
    e3 = _pol_codes('日本央行加息已经实施', '2026-09-20', events)
    e4 = _pol_codes('日本央行加息已经实施', '2026-09-25', events)
    e5 = _pol_codes('截至9月20日，日本央行9月18日决议,9月24日生效;'
                    '美联储7月降息已实施', '2026-09-20', events)
    check('§T2-e 不写日期的已实施断言(断言时点=该实体唯一待生效决议)→'
          'POL-EFF-EARLY-CLAIM;生效后零违规;别家实体的已实施分句不误判',
          e1 == ['POL-EFF-EARLY-CLAIM'] and e2 == ['POL-EFF-EARLY-CLAIM']
          and e3 == ['POL-EFF-EARLY-CLAIM'] and e4 == [] and e5 == [],
          f'{e1} {e2} {e3} {e4} {e5}')
    # f. 正确的前瞻/条件表述不误判
    f1 = _pol_codes('日本央行9月18日决议,9月24日生效后利率升至1.25%',
                    '2026-09-20', events)
    f2 = _pol_codes('截至9月20日，日本央行9月18日决议加息25bp，目前利率仍为'
                    '0.75%，9月24日生效后升至1.25%', '2026-09-20', events)
    f3 = _pol_codes('日本央行9月18日决议,9月24日生效;目前数据完整',
                    '2026-09-20', events)
    f4 = _pol_codes('日本央行9月24日生效的加息目前适用', '2026-09-20',
                    events)
    f5 = _pol_codes('截至 9 月 20 日，美联储 9 月 24 日生效的降息已经实施',
                    '2026-09-20', events)
    f6 = _pol_codes('截至9月20日，日本央行当前政策利率为1.25%', '2026-11-23',
                    events)
    check('§T2-f 前瞻/条件表述(「X生效后」)/同段无关「目前」零违规;'
          '「X生效的加息目前适用」=提前生效断言;实体不绑照旧;'
          '段内显式时点早于生效日的无日期当前值→POL-EFF-PENDING-AS-CURRENT',
          f1 == [] and f2 == [] and f3 == []
          and f4 == ['POL-EFF-EARLY-CLAIM'] and f5 == []
          and f6 == ['POL-EFF-PENDING-AS-CURRENT'],
          f'{f1} {f2} {f3} {f4} {f5} {f6}')
    # g. R32 既判用例逐条不变(回归锁)
    g = {
        'c1': (_pol_codes('日本央行2026年9月18日决议将政策利率上调至1.25%,'
                          '自决议次日起生效', '2026-09-20', events),
               ['POL-EFF-REL']),
        'c3': (_pol_codes('日本央行2026年9月18日决议上调政策利率至1.25%,'
                          '将于2026年9月24日生效(截至研究时点尚未生效)',
                          '2026-09-20', events), []),
        'c4': (_pol_codes('日本央行当前政策利率为1.25%', '2026-09-20',
                          events), ['POL-EFF-PENDING-AS-CURRENT']),
        'c5': (_pol_codes('日本央行当前政策利率为1.25%', '2026-09-25',
                          events), []),
        'c7': (_pol_codes('日本央行9月18日决议,9月24日生效,目前利率已升至'
                          '1.25%', '2026-09-25', events), []),
        'c11': (_pol_codes('日本央行9月18日决议加息至1.25%', '2026-09-20',
                           events), ['POL-EFF']),
        'c12': (_pol_codes('日本央行2026年9月18日决议(生效2026年9月24日),'
                           '政策利率升至1.25%', '2026-09-25', events), []),
        'c15': (_pol_codes('发布日历实录载政策决议2026-09-18(生效2026-09-24,'
                           '目标水平约1.25%)', '2026-09-25', events), []),
        'c16': (_pol_codes('日本央行2026年9月18日决议生效2026年9月22日',
                           '2026-09-25', events), ['POL-EFF-DATE']),
        'c18': (_pol_codes('日本央行9月18日决议生效', '2026-09-25', events),
                ['POL-EFF-DATE']),
        'c8': (_pol_codes('美联储9月18日决议降息25bp,随后美债收益率下行',
                          '2026-09-20', events), []),
    }
    bad = {k: v for k, v in g.items() if v[0] != v[1]}
    check('§T2-g R32 既判用例(c1/c3/c4/c5/c7/c11/c12/c15/c16/c18/c8)逐条'
          '同判(成对纪律/生效日核对/相对生效/待生效值写成当前值/实体绑定)',
          not bad, json.dumps(bad, ensure_ascii=False))
    # h. 正式 attach(进程内入口,合成运行目录,真实日历与注册表)
    t_a, rd_a, jp_a = _t2_synth_run('t2_a', '2026-09-20', SENT_A)
    r_a = aj.attach_judgment(rd_a, jp_a, root=t_a)
    rep_a = _t2_attach_res(rd_a)
    va = [v['code'] for v in ((rep_a.get('agent_judgment') or {})
                              .get('validation') or {}).get('violations')
          or []]
    t_b, rd_b, jp_b = _t2_synth_run('t2_b', '2026-09-20', SENT_B)
    r_b = aj.attach_judgment(rd_b, jp_b, root=t_b)
    rep_b = _t2_attach_res(rd_b)
    t_c, rd_c, jp_c = _t2_synth_run('t2_c', '2026-09-20', '合成陈述(不含政策)')
    r_c = aj.attach_judgment(rd_c, jp_c, root=t_c)
    check('§T2-h 正式 attach(attach_judgment,as_of=2026-09-20): 误句拒收'
          '(attached=False+POL-EFF-EARLY-CLAIM+L3/L4 produced=False+无判定档'
          '副本);正句接收(attached=True+契约 VERIFIED+L3/L4 produced=True);'
          '不含政策的对照句接收',
          (r_a.get('attached') is False and va == ['POL-EFF-EARLY-CLAIM']
           and not os.path.isfile(os.path.join(rd_a, 'agent_judgment.json'))
           and rep_a['layers']['L3_AI推断层'].get('produced') is False
           and rep_a['layers']['L4_条件情景层'].get('produced') is False)
          and (r_b.get('attached') is True
               and ((rep_b.get('agent_judgment') or {})
                    .get('contract_verification') or {}).get('verdict')
               == 'VERIFIED'
               and rep_b['layers']['L3_AI推断层'].get('produced') is True
               and os.path.isfile(os.path.join(rd_b, 'agent_judgment.json')))
          and r_c.get('attached') is True,
          f"A attached={r_a.get('attached')} codes={va} "
          f"B attached={r_b.get('attached')} contract="
          f"{((rep_b.get('agent_judgment') or {}).get('contract_verification') or {}).get('verdict')} "
          f"ctrl={r_c.get('attached')}")
    # i. 正式 CLI 入口(research-one --stage attach)
    ct, same = _code_tree('t2_cli')
    rc_a, d_a = _cli(['research-one', '--stage', 'attach',
                      '--report-dir', rd_a, '--judgment', jp_a,
                      '--engine-root', ct], cwd=ct)
    rc_b, d_b = _cli(['research-one', '--stage', 'attach',
                      '--report-dir', rd_b, '--judgment', jp_b,
                      '--engine-root', ct], cwd=ct)
    check('§T2-i 正式 CLI(research-one --stage attach --engine-root 注入): '
          '误句 ok=False attached=False violations=[POL-EFF-EARLY-CLAIM];'
          '正句 attached=True validation_passed=True',
          d_a.get('ok') is False and (d_a.get('data') or {}).get('attached')
          is False and [v['code'] for v in (d_a.get('data') or {})
                        .get('violations') or []]
          == ['POL-EFF-EARLY-CLAIM']
          and d_b.get('ok') is True and (d_b.get('data') or {}).get('attached')
          is True and (d_b.get('data') or {}).get('validation_passed') is True,
          f"rc={rc_a}/{rc_b} A={json.dumps(d_a, ensure_ascii=False)[:300]} "
          f"B_ok={d_b.get('ok')}")
    # j. 官方目标缺证的草稿处理不变(R28 任务2 口径)
    cal_empty = os.path.join(TMPG, 'cal_empty_t2.json')
    with open(cal_empty, 'w', encoding='utf-8') as f:
        json.dump({'version': 'fixture', 'entries': []}, f)
    pv_jp = {'cells': [
        {'region': 'JP', 'dimension': 'policy', 'metric_id': 'JP_POLICY_RATE',
         'anchors': {'最新一期': {'status': 'ok', 'freshness': None}}}]}
    face_g = rmp.official_policy_record_face(
        pv_jp, {('JP', 'policy')}, '2026-11-21', question=_POL_Q,
        calendar_path=cal_empty)
    face_ok = rmp.official_policy_record_face(
        pv_jp, {('JP', 'policy')}, '2026-11-21', question=_POL_Q,
        calendar_path=os.path.join(t_a, 'config', 'release_calendar.json'))
    rep_d = {'run_ok': True,
             'layers': {'L1_事实层': {'rows': [{'x': 1}]}},
             'run': {'question': _POL_Q, 'data_requirements': {'items': []}},
             'steps': [],
             'agent_judgment': {'reader_map_faces': {'complete': True}},
             'research_plan': {'map_question': True, 'cutoff': '2026-11-21',
                               'point_anchors': [
                                   {'label': '最新一期', 'months_before': 0}],
                               'regions': {'JP': {'dimensions': {
                                   'policy': [{}]}}},
                               'point_values': pv_jp}}
    bc_g = aj.blocked_class_of(rep_d, calendar_path=cal_empty)
    bc_ok = aj.blocked_class_of(
        rep_d, calendar_path=os.path.join(t_a, 'config',
                                          'release_calendar.json'))
    check('§T2-j 官方目标缺证的草稿处理保留: 点名日银目标×日历无实录→'
          'gaps 点名 JP/JP_POLICY_TARGET+blocked_class=map_official_target_'
          'missing(阻断交付类,归档拒绝);有实录→零缺口+None',
          bool(face_g.get('gaps'))
          and (face_g.get('gaps') or [{}])[0].get('metric_id')
          == 'JP_POLICY_TARGET'
          and '不以市场序列值冒充' in str((face_g.get('gaps') or [{}])[0]
                                           .get('note'))
          and not face_ok.get('gaps')
          and bc_g == 'map_official_target_missing'
          and 'map_official_target_missing' in aj.BLOCKING_BLOCKED_CLASSES
          and bc_ok is None,
          f'bc_g={bc_g} bc_ok={bc_ok} gaps={face_g.get("gaps")}')
    # k. 入库归档判定档重验(真实文本,r30–r32): 零政策违规、结论不变
    n_arc = 0
    arc_bad = []
    for d in sorted(glob.glob(os.path.join(ROOT, 'docs', 'autonomous-rd',
                                           'r3[0-2]-evidence', '**',
                                           'agent_judgment.json'),
                              recursive=True)):
        rp = os.path.join(os.path.dirname(d), 'report.json')
        if not os.path.isfile(rp):
            continue
        with open(rp, encoding='utf-8') as f:
            rep = json.load(f)
        with open(d, encoding='utf-8') as f:
            jud = json.load(f)
        cal = os.path.join(os.path.dirname(d), 'root_overlay', 'config',
                           'release_calendar.json')
        cal = cal if os.path.isfile(cal) else os.path.join(
            ROOT, 'config', 'release_calendar.json')
        as_of = ((rep.get('run') or {}).get('evidence_asof')
                 or (rep.get('research_plan') or {}).get('cutoff'))
        res = aj.validate_judgment(
            jud, {e.get('ref') for e in rep.get('evidence_index') or []
                  if e.get('ref')}, _t2_mids, policy_events=aj.collect_policy_events(cal),
            as_of=as_of if isinstance(as_of, str) else None)
        n_arc += 1
        pol = [v['code'] for v in res['violations']
               if v['code'].startswith('POL')]
        if pol or not res['passed']:
            arc_bad.append((os.path.relpath(os.path.dirname(d), ROOT), pol,
                            [v['code'] for v in res['violations']][:5]))
    check('§T2-k 入库归档判定档重验(r30–r32 正式/降级/换问会话): 逐份零'
          '政策违规且整档照旧通过(新时态模型对真实已接收文本零新增拦截)',
          n_arc >= 14 and not arc_bad, f'n={n_arc} bad={arc_bad[:4]}')


# ══ 任务2补充: 完成态状态断言「(A..T)…已生效」不误拒 ════════════════════════
# 12 月快照重跑 11 月原问(待生效决议在场)的真实席位文本被 R32 成对纪律误拒:
# 「窗内(2026-05-30..2026-11-30)该决议已生效」的完成态「已生效」被读成「本
# 事件于 11-30 生效」。修: 完成态+绑定日期词元是区间端+同实体在端点日已生效
# 的另一决定在段内被提及→按状态断言放行;其余形态(非完成态/非区间端/带事
# 件日期的提前生效断言/端点=本事件决议日)照旧拦截。
F_T2B = ('日本: 发布日历实录载 2026-09-18 决议、2026-09-24 生效,'
         '官方政策目标利率1.25%(2026-10-30 确认维持);')
P_T2B = (';截至研究截止日有一项已决议未生效条目: 2026-11-27 决议、'
         '2026-12-04 生效(目标1.5%)')


def sec_t2b():
    print('═══ 任务2补充: 完成态状态断言「(A..T)…已生效」不误拒 ═══')
    cal = os.path.join(FIX_R33, 'family_calendar_dec.json')
    ev = aj.collect_policy_events(cal)
    real = aj.collect_policy_events(
        os.path.join(ROOT, 'config', 'release_calendar.json'))
    ids = sorted({(e['entry_id'], e.get('decision_date'),
                   e.get('effective_on')) for e in ev if e.get('entity') == 'JP'})
    check('§T2b-0 夹具日历=真实日历+合成日银决议(2026-11-27 决议并公布/'
          '2026-12-04 生效,非真实决议);真实日历无该条',
          ids == [('RC-JP-BOJ-TARGET-2026-09', '2026-09-18', '2026-09-24'),
                  ('RC-JP-BOJ-TARGET-2026-11', '2026-11-27', '2026-12-04')]
          and all(e['entry_id'] != 'RC-JP-BOJ-TARGET-2026-11' for e in real),
          ids)
    # a. 正句(完成态状态断言;区间端连接词两形)零政策违规
    w1 = _pol_codes(F_T2B + '窗内(2026-05-30..2026-11-30)该决议已生效'
                    + P_T2B, '2026-11-30', ev)
    w2 = _pol_codes(F_T2B + '回看窗口 2026-05-30 至 2026-11-30 内已经生效'
                    + P_T2B, '2026-11-30', ev)
    check('§T2b-a 正句「窗内(A..T)该决议已生效」/「A 至 T 内已经生效」'
          '(待生效决议同段提及)→零政策违规(修前误拒 POL-EFF-DATE)',
          w1 == [] and w2 == [], f'w1={w1} w2={w2}')
    # b. 误句照旧拦截
    w3 = _pol_codes(F_T2B + '窗内(2026-05-30..2026-11-30)2026-11-27 决议已生效'
                    '(目标1.5%)', '2026-11-30', ev)
    w4 = _pol_codes('日本央行 2026-09-18 决议、2026-09-24 生效;窗内(2026-09-01..'
                    '2026-09-20)该决议已生效', '2026-09-20', ev)
    w5 = _pol_codes('日本央行 2026-09-18 决议、2026-09-24 生效;窗内(2026-09-01..'
                    '2026-09-18)该决议已生效', '2026-09-20', ev)
    w6 = _pol_codes(F_T2B + '窗内(2026-05-30..2026-11-30)生效的决议共两项'
                    + P_T2B, '2026-11-30', ev)
    w7 = _pol_codes(F_T2B + '截至 2026-11-30 该决议已生效' + P_T2B,
                    '2026-11-30', ev)
    check('§T2b-b 误句照旧拦截: 带事件日期的提前生效(POL-EFF-EARLY-CLAIM)/'
          '窗端早于生效日且无同实体已生效决定(POL-EFF-DATE)/窗端=决议日'
          '(EARLY-CLAIM)/非完成态「生效的决议」(POL-EFF-DATE)/非区间端'
          '「截至 T 该决议已生效」(POL-EFF-DATE,保守)',
          w3 == ['POL-EFF-EARLY-CLAIM'] and w4 == ['POL-EFF-DATE']
          and w5 and w5[0] == 'POL-EFF-EARLY-CLAIM' and w6 == ['POL-EFF-DATE']
          and w7 == ['POL-EFF-DATE'],
          f'w3={w3} w4={w4} w5={w5} w6={w6} w7={w7}')
    # c. 前瞻表述零违规;用户令误句形(真实日期)拒收
    w8 = _pol_codes(F_T2B + '窗内(2026-05-30..2026-11-30)2026-12-04 起生效'
                    + P_T2B, '2026-11-30', ev)
    w9 = _pol_codes('日本央行 2026-09-18 决议、2026-09-24 生效;截至 2026-11-30,'
                    '2026-11-27 决议、2026-12-04 生效的调整已经实施',
                    '2026-11-30', ev)
    check('§T2b-c 「T 起生效」前瞻表述零违规;「截至 11-30,11-27 决议、12-04 '
          '生效的调整已经实施」→POL-EFF-EARLY-CLAIM',
          w8 == [] and w9 == ['POL-EFF-EARLY-CLAIM'], f'w8={w8} w9={w9}')
    # d. 正式 attach(合成运行目录,日历换夹具): 正句接收/误句拒收
    w1c = (F_T2B + '窗内(2026-05-30..2026-11-30)该决议已生效' + P_T2B
           ).replace('1.25%', '百分之一点二五').replace('1.5%', '百分之一点五')
    got = {}
    for key, stmt in (('ok', w1c), ('early', F_T2B + '窗内(2026-05-30..'
                                    '2026-11-30)2026-11-27 决议已生效(目标1.5%)'),
                      ('win', '日本央行 2026-09-18 决议、2026-09-24 生效;窗内'
                              '(2026-09-01..2026-09-20)该决议已生效')):
        asof = '2026-09-20' if key == 'win' else '2026-11-30'
        t, rd, jp = _t2_synth_run('t2b_' + key, asof, stmt)
        shutil.copy2(cal, os.path.join(t, 'config', 'release_calendar.json'))
        r = aj.attach_judgment(rd, jp, root=t)
        rep = _t2_attach_res(rd)
        got[key] = (r.get('attached'),
                    [v['code'] for v in ((rep.get('agent_judgment') or {})
                                         .get('validation') or {}).get('violations') or []],
                    ((rep.get('agent_judgment') or {})
                     .get('contract_verification') or {}).get('verdict'),
                    os.path.isfile(os.path.join(rd, 'agent_judgment.json')))
    check('§T2b-d 正式 attach(attach_judgment,日历含待生效决议): 正句接收'
          '(attached=True+契约 VERIFIED+判定档副本);两误句拒收(attached='
          'False+EARLY-CLAIM/POL-EFF-DATE+无副本)',
          got['ok'][0] is True and got['ok'][1] == []
          and got['ok'][2] == 'VERIFIED' and got['ok'][3] is True
          and got['early'][0] is False
          and got['early'][1] == ['POL-EFF-EARLY-CLAIM']
          and got['early'][3] is False
          and got['win'][0] is False and got['win'][1] == ['POL-EFF-DATE']
          and got['win'][3] is False, json.dumps(got, ensure_ascii=False))


# ══ 任务1 更正: 旧工单重渲染零漂移 ═══════════════════════════════════════
# 入库运行档的读者报告(已裁/待裁两形)按现行代码重渲染,哈希须与清单逐项
# 一致——清单由审计基线 f053afe 代码对同一批入库档生成(tests/fixtures_r33/
# legacy_render_sha.json;渲染与路径无关)。任何令旧工单正文变化的改动在此
# 拦下(任务1 首版 ecba122 曾令 R26 旧工单多出「政策文档事实」表)。
LEGACY_MANIFEST = os.path.join(HERE, 'fixtures_r33', 'legacy_render_sha.json')
_DECIDED_RE = re.compile(r'^- 席位已裁: (\S+)\(裁决链 (\d+) 档\)', re.M)


def _legacy_renders(keys=None):
    """→ {运行档相对路径#已裁|待裁: sha256[:16]}(只渲染清单在场的运行档)。"""
    want = {k.split('#')[0] for k in (keys or ())}
    out = {}
    acc = os.path.join(ROOT, 'docs', 'autonomous-rd')
    for mp in sorted(glob.glob(acc + '/**/MAP_REPORT.md', recursive=True)):
        d = os.path.dirname(mp)
        rel = os.path.relpath(d, ROOT)
        if want and rel not in want:
            continue
        if not (os.path.isfile(os.path.join(d, 'report.json'))
                and os.path.isfile(os.path.join(d, 'agent_judgment.json'))):
            continue
        rj = json.load(open(os.path.join(d, 'report.json'), encoding='utf-8'))
        jd = json.load(open(os.path.join(d, 'agent_judgment.json'),
                            encoding='utf-8'))
        m = _DECIDED_RE.search(open(mp, encoding='utf-8').read())
        root = (os.path.join(d, 'root_overlay')
                if os.path.isdir(os.path.join(d, 'root_overlay')) else None)
        forms = ([('decided', {'verdict': m.group(1),
                                'verdicts_n': int(m.group(2))})] if m else []) \
            + [('pending', None)]
        for form, rs in forms:
            new = rmp.render_map_report(rj, jd, rs, root)
            out[rel + '#' + form] = hashlib.sha256(
                new.encode('utf-8')).hexdigest()[:16]
    return out


def sec_t1_h():
    print('§T1-h 任务1 更正: 旧工单重渲染零漂移(基线代码清单逐项比对)')
    check('§T1-h0 基线代码重渲染清单在场', os.path.isfile(LEGACY_MANIFEST))
    if not os.path.isfile(LEGACY_MANIFEST):
        return
    man = json.load(open(LEGACY_MANIFEST, encoding='utf-8'))
    check('§T1-h1 清单覆盖 r20–r32 入库运行档(≥ 60 项)',
          len(man) >= 60, len(man))
    got = _legacy_renders(man.keys())
    miss = sorted(k for k in man if k not in got)
    bad = sorted(k for k in man if k in got and got[k] != man[k])
    check('§T1-h2 清单内运行档全部在场', not miss, miss[:3])
    check('§T1-h3 旧工单正文逐项零漂移(已裁+待裁两形)', not bad, bad[:3])
    # 定点: R26 旧工单(计划带政策文档事实、无扣留键、无政策行)
    d = os.path.join(ROOT, 'docs', 'autonomous-rd', 'r26-evidence',
                     'session-b-run_dir')
    rj = json.load(open(os.path.join(d, 'report.json'), encoding='utf-8'))
    jd = json.load(open(os.path.join(d, 'agent_judgment.json'),
                        encoding='utf-8'))
    rp = rj.get('research_plan') or {}
    check('§T1-h4 定点旧档=计划带政策文档事实而无扣留键(旧口径)',
          bool(rp.get('policy_doc_facts'))
          and 'policy_doc_withheld' not in rp)
    legacy = rmp.render_map_report(rj, jd, None)
    check('§T1-h5 旧口径档: 政策面缺席分支零新增行(无政策文档事实表)',
          '政策文档事实' not in legacy)
    rj2 = copy.deepcopy(rj)
    rj2['research_plan']['policy_doc_withheld'] = []
    new = rmp.render_map_report(rj2, jd, None)
    check('§T1-h6 新口径档(计划带扣留键): 政策面缺席仍列可见文档清单',
          '**政策文档事实(公告/纪要发布日)**' in new)


def main():
    print('Audit-R33 门 (HEAD %s)' % WORKTREE_HEAD[:12])
    try:
        sec_t2()
        sec_t2b()
        sec_t1_a()
        sec_t1_b()
        sec_t1_c()
        sec_t1_d()
        sec_t1_e()
        sec_t1_f()
        sec_t1_g()
        sec_t1_h()
    finally:
        n_ok = sum(1 for x in RESULTS if x)
        n = len(RESULTS)
        print('=== R33 门: %d/%d ===' % (n_ok, n))
        shutil.rmtree(TMPG, ignore_errors=True)
    return 0 if all(RESULTS) else 1


if __name__ == '__main__':
    sys.exit(main())
