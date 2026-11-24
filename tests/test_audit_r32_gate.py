#!/usr/bin/env python3
"""Audit-R32 门 — 正式使用收尾: 统一证据口径/同比与政策核验/冻结-裁决-交付链。

任务1 统一研究截止日和证据资格: 截止规则放在取数入口(latest_snapshot/
metric_series),S3–S8 子进程/L1/证据索引/研究席/契约/报告/归档共用同一
证据口径(IA_EVIDENCE_ASOF 运行级钉死);晚观测/晚发布/当时不可得的数据
版本均不得成为可引用证据;历史类比事后结果明确标注;NEW30 月末未到=
请求月末与实际覆盖日同时披露,研究截止日取实际覆盖日。
任务2 历史同比=去年同月/同季(缺基期即缺证);政策按实体/断言时点/决议
日/生效日核验;问现行官方目标而只有待生效公告=行级缺口/首页草稿/
正式归档拒绝同判。
任务3 plan/attach/report/archive/replay 使用并校验本工单冻结快照/
注册表/日历(overlay 缺件/篡改=拒绝;引擎本地日历被换不影响判定与
重渲);冻结初始化中途失败=清理后下一工单选新快照。
任务4 T3 原问经 --question-file 原样输入(地图问句+官方目标地区=欧日)。
正式验收发现(§L) 裁决后交付状态面: 在场地图与当前装配仅差「分工」行
审查状态短语=状态面等价(裁决绑定有效)→翻新状态面而非冻结;正文差异
照旧冻结/过期/拒绝。裁决后再交付包(运行=执行印章、交付字节=归档印章)
清单落档归档代码 SHA(仅异印章时加键);重放门④对已声明状态面等价的
再交付包认归档代码为录制代码,第三印章照旧拒(显式越过=披露)。
"""
import contextlib
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

import agent_judgment as aj                      # noqa: E402
import evidence_gate as eg                       # noqa: E402
import freshness_policy as fp                    # noqa: E402
import release_calendar as rc                    # noqa: E402
import research_map_planner as rmp               # noqa: E402
import workbench_data as wd                      # noqa: E402

TMPG = tempfile.mkdtemp(prefix='r32gate_')
RESULTS = []
R31_ACC = os.path.join(ROOT, 'docs', 'autonomous-rd', 'r31-evidence',
                       'acceptance')
SNAP_SRC = os.path.join(R31_ACC, 'session_B2_formal', 'root_overlay',
                        'data', 'daily', 'research_snapshot_20261122_v2.json')
AUG_PLAN = os.path.join(R31_ACC, 'aug_plan', 'run_dir', 'report.json')
QDIR = os.path.join(R31_ACC, 'questions')
R23_SRC = os.path.join(ROOT, 'docs', 'autonomous-rd',
                       'r23-evidence', 'acceptance')
RUN_FILES = ['report.json', 'report.md', 'FULL_REPORT.md',
             'agent_judgment.json', 'views_digest.json',
             'evidence_index.json', 'AGENT_SEAT_ENVELOPE.json',
             'MAP_REPORT.md', 'MAP_REPORT.sha256']
WORKTREE_HEAD = subprocess.run(
    ['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True,
    text=True, timeout=30).stdout.strip()
CUT_AUG = '2026-08-21'
Q_T3 = open(os.path.join(QDIR, 'question_T3.txt'),
            encoding='utf-8').read().rstrip('\n')
Q_NEW30 = open(os.path.join(QDIR, 'question_NEW30.txt'),
               encoding='utf-8').read().rstrip('\n')
Q_AUG = open(os.path.join(QDIR, 'question_aug.txt'),
             encoding='utf-8').read().rstrip('\n')
Q_B = open(os.path.join(QDIR, 'question_B.txt'),
           encoding='utf-8').read().rstrip('\n')
Q_A = open(os.path.join(QDIR, 'question_A.txt'),
           encoding='utf-8').read().rstrip('\n')


def check(name, ok, detail=''):
    ok = bool(ok)
    RESULTS.append(ok)
    print(('  ✅ ' if ok else '  ❌ ') + name +
          (' — ' + str(detail)[:300] if detail else ''), flush=True)
    return ok


def _late_count(rows, cutoff, key=None):
    n = 0
    for x in rows or []:
        v = x.get(key) if key else x.get('ref')
        m = re.search(r'@?(\d{4}-\d{2}-\d{2})', str(v or ''))
        if m and m.group(1) > cutoff:
            n += 1
    return n


def _mk_tree(tag, with_snapshot=True):
    """迷你引擎树: config 副本+提交的 11 月冻结快照(R31 B2 overlay 原件)。"""
    t = os.path.join(TMPG, 'tree_' + tag)
    shutil.copytree(os.path.join(ROOT, 'config'), os.path.join(t, 'config'))
    os.makedirs(os.path.join(t, 'data', 'daily'), exist_ok=True)
    snap = None
    if with_snapshot:
        snap = os.path.join(t, 'data', 'daily',
                            'research_snapshot_20261122_v2.json')
        shutil.copy2(SNAP_SRC, snap)
    return t, snap


def _fake_step_ok(name, argv, timeout=180):
    return {'step': name, 'argv': list(argv), 'executed': True,
            'ok': True, 'exit_code': 0, 'semantic_ok': True,
            'note': None, 'duration_ms': 1, 'envelope': {'ok': True}}


def _offline_plan(tag, question, snapshot=True):
    """离线 plan(S 步=替身信封;取数/证据口径/L1/索引走真代码)。"""
    import research_orchestrator as ro
    t, _snap = _mk_tree(tag, with_snapshot=snapshot)
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


def cli(stage, rd, engine_root, arc=None, extra=None):
    cmd = ['research-one', '--stage', stage, '--report-dir', rd,
           '--engine-root', engine_root]
    if arc:
        cmd += ['--archive-dir', arc]
    if extra:
        cmd += extra
    return _cli(cmd)


def replay(pkg, engine_root, out=None, extra=None):
    cmd = ['research-one', '--stage', 'replay', '--package', pkg,
           '--engine-root', engine_root]
    if out:
        cmd += ['--replay-out', out]
    if extra:
        cmd += extra
    return _cli(cmd)


def build_tree(tag):
    T = os.path.join(TMPG, 'eng_' + tag)
    os.makedirs(os.path.join(T, 'data', 'daily'))
    os.makedirs(os.path.join(T, 'config'))
    for fn in ('metric_registry.json', 'release_calendar.json'):
        shutil.copy2(os.path.join(ROOT, 'config', fn),
                     os.path.join(T, 'config', fn))
    return T


def _cal_write(path, entries):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({'version': 'r32gate-fixture', 'entries': entries}, f)


def fresh_pkg_rd(tag, session):
    """R31 交付包→运行目录复本(run 文件+root_overlay+verdicts)。"""
    src = os.path.join(R31_ACC, session)
    d = os.path.join(TMPG, 'rd_' + tag)
    os.makedirs(d)
    for f in RUN_FILES:
        shutil.copy2(os.path.join(src, f), d)
    shutil.copytree(os.path.join(src, 'root_overlay'),
                    os.path.join(d, 'root_overlay'))
    if os.path.isdir(os.path.join(src, 'verdicts')):
        shutil.copytree(os.path.join(src, 'verdicts'),
                        os.path.join(d, 'verdicts'))
    return d, src


def rewrite_head(rd, head):
    import research_orchestrator as ro
    p = os.path.join(rd, 'report.json')
    rj = json.load(open(p, encoding='utf-8'))
    rj['run']['git_head'] = head
    rj['run']['git_head_source'] = 'r32gate_worktree'
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(rj, f, ensure_ascii=False, indent=2, default=str)
    with open(os.path.join(rd, 'report.md'), 'w', encoding='utf-8') as f:
        f.write(ro._render_md(rj))
    fp_ = os.path.join(rd, 'FULL_REPORT.md')
    if os.path.exists(fp_):
        os.remove(fp_)


def _seed_verdicts(T, session):
    """包内裁决链按 ARCHIVE_MANIFEST.source_rel 落引擎树(重渲/报告读)。
    源件优先取 manifest.file;R31 入库包裁决件名缺日目录前缀时按
    basename 回落(内容哈希不变,仅文件名——见 §C0 基线发现)。"""
    man = json.load(open(os.path.join(R31_ACC, session,
                                      'ARCHIVE_MANIFEST.json'),
                         encoding='utf-8'))
    for e in man.get('verdict_chain') or []:
        rel = e.get('source_rel') or ''
        src = os.path.join(R31_ACC, session, e['file'])
        if not os.path.isfile(src):
            src = os.path.join(R31_ACC, session, 'verdicts',
                               os.path.basename(e['file']).split('__', 1)[-1])
        dst = os.path.join(T, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
    return man


def strip_policy_entries(cal_path, metric_ids):
    c = json.load(open(cal_path, encoding='utf-8'))
    c['entries'] = [e for e in c.get('entries', [])
                    if e.get('metric_id') not in metric_ids]
    with open(cal_path, 'w', encoding='utf-8') as f:
        json.dump(c, f, ensure_ascii=False, indent=2)


# ═══ §A 任务1: 统一研究截止日和证据资格 ═══
def sec_a():
    import research_orchestrator as ro
    print('═══ §A 任务1: 统一研究截止日和证据资格 ═══')
    # A1 复现(提交档=不可变证据): R31 aug_plan 以 11 月快照答 8 月问句
    base = json.load(open(AUG_PLAN, encoding='utf-8'))
    cut0 = (base.get('research_plan') or {}).get('cutoff')
    l10 = ((base.get('layers') or {}).get('L1_事实层') or {}).get('rows') or []
    ei0 = base.get('evidence_index') or []
    check('§A1 复现: 提交的 AUG 计划(R31 aug_plan)截止 2026-08-21 而 '
          'L1 事实 31/31、证据引用 56/56 晚于截止日(基线缺陷在档)',
          cut0 == CUT_AUG and len(l10) == 31
          and _late_count(l10, CUT_AUG, 'observation_date') == 31
          and len(ei0) == 56 and _late_count(ei0, CUT_AUG) == 56,
          f'cutoff={cut0} L1={len(l10)} '
          f'late={_late_count(l10, CUT_AUG, "observation_date")} '
          f'EI={len(ei0)} late={_late_count(ei0, CUT_AUG)}')

    # A2 修复: 同一快照+同一 AUG 原问,离线 plan(取数入口截止)
    t, rep, md, seen = _offline_plan('aug', Q_AUG)
    rp = rep.get('research_plan') or {}
    run = rep.get('run') or {}
    l1 = ((rep.get('layers') or {}).get('L1_事实层') or {}).get('rows') or []
    ei = rep.get('evidence_index') or []
    win = ((rp.get('question_window') or {}).get('windows') or [{}])[0]
    check('§A2a 截止日与回看窗: cutoff=2026-08-21,窗 2026-02-21..08-21',
          rp.get('cutoff') == CUT_AUG and win.get('from') == '2026-02-21'
          and win.get('to') == CUT_AUG,
          f"cutoff={rp.get('cutoff')} win={win}")
    check('§A2b L1 事实零晚观测(31/31→0),证据索引零晚引用(56/56→0)',
          len(l1) > 0 and _late_count(l1, CUT_AUG, 'observation_date') == 0
          and len(ei) > 0 and _late_count(ei, CUT_AUG) == 0,
          f'L1={len(l1)} late={_late_count(l1, CUT_AUG, "observation_date")} '
          f'EI={len(ei)} late={_late_count(ei, CUT_AUG)}')
    egb = run.get('evidence_gate') or {}
    ser = egb.get('series') or {}
    check('§A2c run.evidence_gate 在档: as_of/历史截止视图/源快照/逐序列'
          '末合规观测≤截止日',
          egb.get('as_of') == CUT_AUG and egb.get('historical_view') is True
          and egb.get('source_snapshot_id') == 'research_snapshot_20261122_v2'
          and bool(ser)
          and all((v.get('last_eligible') is None
                   or v.get('last_eligible') <= CUT_AUG)
                  for v in ser.values()),
          f"as_of={egb.get('as_of')} series={len(ser)} "
          f"counts={egb.get('counts')}")
    check('§A2d 规则①晚观测: 日频 2026-08-21 收盘当晚未发布→末合规 '
          '2026-08-20(SPX/USDJPY);ECB 09-16 变更日观测剔除(末 06-17)',
          ser.get('SPX', {}).get('last_eligible') == '2026-08-20'
          and ser.get('SPX', {}).get('first_dropped', {}).get('reason')
          == 'late_publication'
          and ser.get('ECB_MRO', {}).get('last_eligible') == '2026-06-17'
          and ser.get('ECB_MRO', {}).get('first_dropped', {}).get('reason')
          == 'late_observation',
          f"SPX={ser.get('SPX', {}).get('last_eligible')} "
          f"MRO={ser.get('ECB_MRO', {}).get('last_eligible')}")
    check('§A2e 规则②晚发布: 8 月 CPI/HICP 观测 9 月才发布→不可引用,末合'
          '规=7 月观测(JP_CPI_YOY 1.97 于 08-20 已发布=可引用)',
          ser.get('JP_CPI_YOY', {}).get('last_eligible') == '2026-07-01'
          and ser.get('JP_CPI_YOY', {}).get('first_dropped', {}).get('reason')
          == 'late_publication'
          and ser.get('EA_HICP_YOY', {}).get('last_eligible') == '2026-07-01'
          and any(c.get('metric_id') == 'JP_CPI_YOY'
                  and (c.get('anchors') or {}).get('最新一期', {}).get('value')
                  == 1.97
                  for c in (rp.get('point_values') or {}).get('cells') or []),
          f"JP={ser.get('JP_CPI_YOY', {}).get('first_dropped')} "
          f"EA={ser.get('EA_HICP_YOY', {}).get('first_dropped')}")
    check('§A2f 规则③数据版本: 注册表声明最新修订口径且无 ≤截止日快照'
          '版本——Q2 GDP 观测当时只有初值,逐点剔除(JP/EA/US_REAL_GDP '
          'reason=data_version_unavailable)',
          all(ser.get(m, {}).get('n_version_unavailable', 0) >= 1
              and ser.get(m, {}).get('first_dropped', {}).get('reason')
              == 'data_version_unavailable'
              for m in ('JP_REAL_GDP_YOY', 'EA_REAL_GDP_YOY',
                        'US_REAL_GDP')),
          f"JP_GDP={ser.get('JP_REAL_GDP_YOY', {}).get('first_dropped')}")
    check('§A2g S 步子进程共用同一口径: 步进程环境 IA_EVIDENCE_ASOF='
          '2026-08-21+快照/日历钉死在位;返回后全部释放',
          seen.get('asof') == CUT_AUG and bool(seen.get('snap'))
          and bool(seen.get('cal'))
          and all(os.environ.get(k) is None for k in aj._PIN_ENV_KEYS),
          f'seen={ {k: bool(v) for k, v in seen.items()} }')
    # A2h 读者面证据口径行(report.md): 版本不可得计数=evidence_gate.counts
    # 的整数观测数(渲染键与计数键同名;读不存在的键=「None 条」——真跑
    # AUG 复验时发现);非历史截止视图收尾不留悬空「快照版本日」
    import copy
    _nv = (egb.get('counts') or {}).get(
        'series_observations_version_unavailable')

    def _hdr(md_):
        return [ln for ln in md_.splitlines()
                if '研究截止日(证据口径 r32)' in ln]
    _h1 = _hdr(md)
    _rep2 = copy.deepcopy(rep)
    _rep2['run']['evidence_gate']['historical_view'] = False
    _h2 = _hdr(ro._render_md(_rep2))
    check('§A2h report.md 证据口径行: 版本不可得剔除=整数观测数(%s 个'
          '观测)、无「None」;历史截止视图尾注在位' % _nv,
          isinstance(_nv, int)
          and len(_h1) == 1
          and ('版本不可得剔除 %d 个观测' % _nv) in _h1[0]
          and 'None' not in _h1[0]
          and _h1[0].rstrip().endswith('当时不可得版本不入证据面)'),
          _h1[0] if _h1 else md[:300])
    check('§A2i 同一行在快照版本日口径(非历史截止)收尾=「快照版本日口径'
          '(截止日=快照版本日)」,无悬空词、无「None」',
          len(_h2) == 1
          and _h2[0].rstrip().endswith('快照版本日口径(截止日=快照版本日)')
          and 'None' not in _h2[0],
          _h2[0] if _h2 else 'no header')
    # A3 真 CLI 步命令(history/overview/changes)在钉死环境下读截止视图
    env = {'IA_SNAPSHOT_PIN': os.path.join(
               t, 'data', 'daily', 'research_snapshot_20261122_v2.json'),
           'IA_EVIDENCE_ASOF': CUT_AUG}
    rc_h, dh = _cli(['history', '--metric', 'SPX'], env=env)
    rc_h2, dh2 = _cli(['history', '--metric', 'JP_CPI_YOY'], env=env)
    rc_o, do = _cli(['overview', '--economy', 'JP'], env=env)
    rc_c, dc = _cli(['changes'], env=env)
    _obs = [m.get('observation_date')
            for m in ((do.get('data') or {}).get('economies') or {})
            .get('JP', {}).get('metrics') or [] if m.get('observation_date')]
    _obc = [r.get('observation_date')
            for rows in ((dc.get('data') or {}).get('by_asset_class')
                         or {}).values() for r in rows or []
            if isinstance(r, dict) and r.get('observation_date')]
    check('§A3 S3/S4 真命令同口径: history SPX 末=08-20/JP_CPI_YOY 末='
          '07-01;overview JP 与 changes 全部观测日≤08-21',
          rc_h == 0 and ((dh.get('data') or {}).get('series') or {})
          .get('dates', [''])[0] is not None
          and ((dh.get('data') or {}).get('series') or {}).get('last')
          == '2026-08-20'
          and rc_h2 == 0 and ((dh2.get('data') or {}).get('series') or {})
          .get('last') == '2026-07-01'
          and rc_o == 0 and bool(_obs) and max(_obs) <= CUT_AUG
          and rc_c == 0 and bool(_obc) and max(_obc) <= CUT_AUG,
          f"SPX={((dh.get('data') or {}).get('series') or {}).get('last')} "
          f"JP={((dh2.get('data') or {}).get('series') or {}).get('last')} "
          f'ov_max={max(_obs) if _obs else None} '
          f'ch_max={max(_obc) if _obc else None}')
    # A4 取数入口单元规则(gate_series)+快照版本日口径(非历史视图)
    d_m = ['2026-06-01', '2026-07-01', '2026-08-01']
    dd, vv, inf = eg.gate_series('CPI', 'monthly', d_m, [1.0, 2.0, 3.0],
                                 CUT_AUG)
    check('§A4a gate_series 规则②: 8 月 CPI 观测(09-13 发布)剔除,6/7 月'
          '保留',
          dd == d_m[:2] and inf.get('n_late_publication') == 1
          and inf.get('first_dropped', {}).get('reason') == 'late_publication',
          f'kept={dd} info={inf}')
    dq = ['2026-01-01', '2026-04-01', '2026-07-01']
    dq2, vq2, infq = eg.gate_series('US_REAL_GDP', 'quarterly', dq,
                                    [1.0, 2.0, 3.0], CUT_AUG, revised=True)
    dq3, _, infq3 = eg.gate_series('US_REAL_GDP', 'quarterly', dq,
                                   [1.0, 2.0, 3.0], CUT_AUG, revised=False)
    check('§A4b gate_series 规则③: 声明修订序列 Q2 观测(07-29 首发,'
          '08-29 首修)当时版本不可得剔除;未声明修订=保留',
          dq2 == ['2026-01-01']
          and infq.get('n_version_unavailable') == 1
          and infq.get('first_dropped', {}).get('reason')
          == 'data_version_unavailable'
          and dq3 == ['2026-01-01', '2026-04-01']
          and infq3.get('n_version_unavailable') == 0,
          f'revised={infq} plain={infq3}')
    snap_raw = json.load(open(SNAP_SRC, encoding='utf-8'))
    n_f = len(snap_raw.get('facts') or [])
    g0 = eg.gate_snapshot(json.loads(json.dumps(snap_raw)), '2026-11-22',
                          root=ROOT)
    g1 = eg.gate_snapshot(json.loads(json.dumps(snap_raw)), CUT_AUG,
                          root=ROOT)
    c0 = (g0.get('evidence_gate') or {}).get('counts') or {}
    c1 = (g1.get('evidence_gate') or {}).get('counts') or {}
    check('§A4c 快照版本日口径(非历史视图)=快照在场即当时可得: 105 事实'
          '零剔除零重建(周频/月频末点不按推定滞后误剔);历史截止视图='
          '晚观测事实全数重建/剔除,零晚观测',
          (g0.get('evidence_gate') or {}).get('historical_view') is False
          and c0.get('facts_rebuilt', 0) == 0
          and c0.get('facts_dropped', 0) == 0
          and c0.get('facts_kept', 0) == n_f
          and len(g0.get('facts') or []) == n_f
          and {(f.get('metric_id'), f.get('observation_date'))
               for f in g0.get('facts') or []}
          == {(f.get('metric_id'), f.get('observation_date'))
              for f in snap_raw.get('facts') or []}
          and (g1.get('evidence_gate') or {}).get('historical_view') is True
          and c1.get('facts_rebuilt', 0) > 0
          and _late_count(
              [{'observation_date': f.get('observation_date')}
               for f in g1.get('facts') or []], CUT_AUG,
              'observation_date') == 0,
          f"v0={c0} v1={c1}")
    # A5 NEW30 月末未到: 请求月末 vs 实际覆盖日
    t2, rep2, md2, _ = _offline_plan('new30', Q_NEW30)
    rp2 = rep2.get('research_plan') or {}
    ad = rp2.get('as_of_declared') or {}
    check('§A5 NEW30: 请求月末 2026-11-30 晚于实际覆盖日 2026-11-22→研究'
          '截止日=实际覆盖日+两侧日期同时披露(clamped_to_coverage)',
          rp2.get('cutoff') == '2026-11-22'
          and ad.get('clamped_to_coverage') is True
          and ad.get('requested_month_end') == '2026-11-30'
          and ad.get('actual_coverage_date') == '2026-11-22'
          and '请求月末 2026-11-30' in md2
          and '实际覆盖日 2026-11-22' in md2
          and (rep2.get('run') or {}).get('evidence_gate', {}).get('as_of')
          == '2026-11-22',
          f"cutoff={rp2.get('cutoff')} ad={ {k: ad.get(k) for k in ('as_of', 'requested_month_end', 'actual_coverage_date', 'clamped_to_coverage')} }")
    # A6 历史类比事后结果标注: r32 报告在场;旧档重渲逐字节不变
    src = os.path.join(R31_ACC, 'session_A4_formal')
    rj = json.load(open(os.path.join(src, 'report.json'), encoding='utf-8'))
    jd = json.load(open(os.path.join(src, 'agent_judgment.json'),
                        encoding='utf-8'))
    man = json.load(open(os.path.join(src, 'ARCHIVE_MANIFEST.json'),
                         encoding='utf-8'))
    sr_mini = {'verdict': man.get('verdict'), 'verdicts_n': man.get('verdicts_n')}
    arch = open(os.path.join(src, 'MAP_REPORT.md'), 'rb').read()
    ov = os.path.join(src, 'root_overlay')
    legacy = rmp.render_map_report(rj, jd, sr_mini, root=ov)
    rj2 = json.loads(json.dumps(rj))
    rj2.setdefault('run', {})['evidence_gate'] = {
        'as_of': '2026-11-22', 'counts': {}}
    gated = rmp.render_map_report(rj2, jd, sr_mini, root=ov)
    check('§A6a 旧档重渲逐字节==归档 MAP_REPORT(A4 正式包,重渲 root=包内 '
          'root_overlay;新行全部 r32 门控,不漂移旧字节)',
          legacy.encode('utf-8') == arch and len(arch) == 102180,
          f"legacy={hashlib.sha256(legacy.encode('utf-8')).hexdigest()[:12]} "
          f"arch={hashlib.sha256(arch).hexdigest()[:12]}")
    check('§A6b r32 报告: 历史类比「事后结果标注」在场(候选期之后=事后实'
          '际,当时不可知≠预测);旧档无此行',
          '事后结果标注' in gated and '事后结果标注' not in legacy
          and '当时不可知' in gated,
          f"n_lines={len(gated.splitlines())}")
    shutil.rmtree(t, ignore_errors=True)
    shutil.rmtree(t2, ignore_errors=True)


# ═══ §B 任务2: 历史同比与政策核验 ═══
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


def sec_b():
    import fact_engine as fe
    print('═══ §B 任务2: 历史同比与政策核验 ═══')
    # B1 同比基期=去年同月(13 个月前观测≠同比)
    s = {'dates': ['2020-06-01', '2021-07-01', '2021-08-01'],
         'values': [100.0, 110.0, 111.0]}
    r, why = rmp._hist_region_reading(s, '2021-08', '2021-08-31', 'CPI',
                                      'level_yoy', 'monthly')
    check('§B1a 反例: 只有 13 个月前观测(2020-06)无去年同月(2020-07)→'
          '缺基期即缺证(None+no_visible_base),不以 13 个月前冒充同比',
          r is None and why == 'no_visible_base', f'r={r} why={why}')
    s2 = {'dates': ['2020-07-01', '2021-07-01', '2021-08-01'],
          'values': [100.0, 110.0, 111.0]}
    r2, why2 = rmp._hist_region_reading(s2, '2021-08', '2021-08-31', 'CPI',
                                        'level_yoy', 'monthly')
    cpr = fe.compute_period_returns(
        ['2020-07-01', '2021-07-01'], [100.0, 110.0], 'index', 'us',
        as_of='2021-08-31')['m12']
    cpr13 = fe.compute_period_returns(
        ['2020-06-01', '2021-07-01'], [100.0, 110.0], 'index', 'us',
        as_of='2021-08-31')['m12']
    check('§B1b 同月在场→同比=+10.0%,与主引擎 m12 同口径(同月基期);主引擎'
          '对 13 个月前反例同判缺基期(available=False)',
          r2 is not None and abs(r2[0] - 10.0) < 1e-9
          and cpr.get('basis_date') == '2020-07-01'
          and abs(float(cpr.get('abs_change', 0)) - 10.0) < 1e-6
          and cpr13.get('available') is False
          and '去年同月' in str(cpr13.get('reason')),
          f'planner={r2} engine_basis={cpr.get("basis_date")} '
          f'engine13={cpr13.get("available")}')
    sq = {'dates': ['2025-01-01', '2026-04-01'], 'values': [100.0, 103.0]}
    rq, whyq = rmp._hist_region_reading(sq, '2026-12', '2026-12-31',
                                        'US_REAL_GDP', 'level_yoy',
                                        'quarterly')
    sq2 = {'dates': ['2025-04-01', '2026-04-01'], 'values': [100.0, 103.0]}
    rq2, _ = rmp._hist_region_reading(sq2, '2026-12', '2026-12-31',
                                      'US_REAL_GDP', 'level_yoy',
                                      'quarterly')
    check('§B1c 季频同季: 只有 2025Q1 无 2025Q2→缺证;2025Q2 在场→+3.0%',
          rq is None and rq2 is not None and abs(rq2[0] - 3.0) < 1e-9,
          f'q_missing={rq} why={whyq} q_ok={rq2}')
    # B2 政策按实体/断言时点/决议日/生效日核验
    events = aj.collect_policy_events(os.path.join(
        ROOT, 'config', 'release_calendar.json'))
    ev_jp = [e for e in events if e['entry_id'] == 'RC-JP-BOJ-TARGET-2026-09']
    check('§B2a 政策事件面: JP 2026-09-18 决议/09-24 生效/目标 1.25 '
          '(实体 JP)',
          len(ev_jp) == 1 and ev_jp[0]['entity'] == 'JP'
          and ev_jp[0]['decision_date'] == '2026-09-18'
          and ev_jp[0]['effective_on'] == '2026-09-24'
          and ev_jp[0]['target_value'] == 1.25,
          f'{ev_jp}')
    c1 = _pol_codes('日本央行2026年9月18日决议将政策利率上调至1.25%,'
                    '自决议次日起生效', '2026-09-20', events)
    c2 = _pol_codes('日本央行2026年9月18日决议,2026年9月22日生效,'
                    '政策利率升至1.25%', '2026-09-20', events)
    c3 = _pol_codes('日本央行2026年9月18日决议上调政策利率至1.25%,'
                    '将于2026年9月24日生效(截至研究时点尚未生效)',
                    '2026-09-20', events)
    c3b = _pol_codes('日本央行2026年9月18日决议,9月24日生效', '2026-09-20',
                     events)
    check('§B2b 用例①相对日期提前生效(as_of 09-20): 「自决议次日起生效」'
          '=09-19 早于官方 09-24→POL-EFF-REL',
          c1 == ['POL-EFF-REL'], f'{c1}')
    check('§B2c 用例②日期齐全但提前生效: 「9月22日生效」早于官方 09-24→'
          'POL-EFF-DATE',
          'POL-EFF-DATE' in c2, f'{c2}')
    check('§B2d 用例③正确待生效: 09-24 生效+尚未生效标注→零违规;成对'
          '无断言→零违规',
          c3 == [] and c3b == [], f'{c3} {c3b}')
    # B2d2 标签前置成对形(R31 A4 正式稿实际词形;正式入口真跑复现的误报):
    # 「决议X(生效Y)」「决议X生效Y」「决议日X、生效日Y」——「生效」是其
    # **后**日期 Y 的标签,原解析按「日期词元后 14 字内出现生效」把 X
    # 读成生效日→POL-EFF-DATE 误报 8 处(全为正确成对表述)。
    c12 = _pol_codes('日本央行2026年9月18日决议(生效2026年9月24日),'
                     '政策利率升至1.25%', '2026-09-25', events)
    c13 = _pol_codes('日本央行决议2026-09-18生效2026-09-24', '2026-09-25',
                     events)
    c14 = _pol_codes('日本央行决议日2026-09-18、生效日2026-09-24',
                     '2026-09-25', events)
    c15 = _pol_codes('发布日历实录载政策决议2026-09-18(生效2026-09-24,'
                     '目标水平约1.25%)', '2026-09-25', events)
    check('§B2d2 标签前置成对形(决议X(生效Y…)/决议X生效Y/决议日X、'
          '生效日Y)→零违规(「生效」绑定其后日期 Y=官方生效日)',
          c12 == [] and c13 == [] and c14 == [] and c15 == [],
          f'{c12} {c13} {c14} {c15}')
    c16 = _pol_codes('日本央行2026年9月18日决议生效2026年9月22日',
                     '2026-09-25', events)
    c17 = _pol_codes('日本央行决议2026-09-18(生效2026-09-22)',
                     '2026-09-25', events)
    c18 = _pol_codes('日本央行9月18日决议生效', '2026-09-25', events)
    check('§B2d3 标签前置但生效日提前(决议X生效Y′/决议X(生效Y′))→'
          'POL-EFF-DATE 恰一条;「X日决议生效」无生效日→POL-EFF-DATE',
          c16 == ['POL-EFF-DATE'] and c17 == ['POL-EFF-DATE']
          and c18 == ['POL-EFF-DATE'], f'{c16} {c17} {c18}')
    c4 = _pol_codes('日本央行当前政策利率为1.25%', '2026-09-20', events)
    c5 = _pol_codes('日本央行当前政策利率为1.25%', '2026-09-25', events)
    c6 = _pol_codes('日本央行9月18日决议,9月24日生效,目前利率已升至1.25%',
                    '2026-09-20', events)
    c7 = _pol_codes('日本央行9月18日决议,9月24日生效,目前利率已升至1.25%',
                    '2026-09-25', events)
    check('§B2e 待生效值写成当前值(无日期)→POL-EFF-PENDING-AS-CURRENT;'
          '生效后同一句→零违规',
          c4 == ['POL-EFF-PENDING-AS-CURRENT'] and c5 == [],
          f'{c4} {c5}')
    check('§B2f 日期成对正确但断言提前(「目前」早于生效日)→'
          'POL-EFF-EARLY-CLAIM;生效后→零违规',
          'POL-EFF-EARLY-CLAIM' in c6 and c7 == [], f'{c6} {c7}')
    c8 = _pol_codes('美联储9月18日决议降息25bp,随后美债收益率下行',
                    '2026-09-20', events)
    c9 = _pol_codes('欧央行9月18日决议维持三大利率不变', '2026-09-20',
                    events)
    c10 = _pol_codes('中国9月18日公布LPR维持不变', '2026-09-20', events)
    c11 = _pol_codes('日本央行9月18日决议加息至1.25%', '2026-09-20', events)
    res31 = aj.validate_judgment(_mk_judgment('日本央行9月18日决议加息至1.25%'),
                                 {'r1'}, {'JP_POLICY_TARGET'},
                                 policy_events=events)
    check('§B2g 实体核验: 美联储/欧央行/中国同日文字不绑日银事件(零违规);'
          '日银决议日无生效无标注→POL-EFF(R31 既档;无 as_of 同判)',
          c8 == [] and c9 == [] and c10 == [] and c11 == ['POL-EFF']
          and 'POL-EFF' in [v['code'] for v in res31['violations']],
          f'us={c8} ea={c9} cn={c10} jp={c11}')
    # B3 T3 官方目标地区=欧日;T3 问句+真实日历(截止 2026-11-22)无缺证
    import research_orchestrator as ro
    reg = wd.load_registry(ROOT)
    ent = ro.map_entities(Q_T3, reg)
    check('§B3a T3 路由: 地图问句+官方目标地区={EA,JP}(「两地央行」指代'
          '绑定);B 问句只绑 JP;A/NEW30 不绑',
          bool(rmp.detect_map_question(Q_T3, ent))
          and set(rmp.question_official_target_regions(Q_T3)) == {'EA', 'JP'}
          and rmp.question_official_target_regions(Q_B) == {'JP'}
          and not rmp.question_official_target_regions(Q_A)
          and not rmp.question_official_target_regions(Q_NEW30),
          f"T3={sorted(rmp.question_official_target_regions(Q_T3))} "
          f"B={sorted(rmp.question_official_target_regions(Q_B))}")
    pairs = {('JP', 'policy'), ('EA', 'policy')}
    # EA 日历无 ECB 实录条目——真管线里 EA 政策格 policy_dates 由序列+惯例
    # 可推(决议 09-10→生效 09-16)=可推地区不触发缺口(R28 既档口径)。
    # Audit-R32 正式入口验收: 规划器把 policy_dates 写在**锚**上(格级键
    # 缺席)——夹具按真管线形状写锚级;格级键仅作旧夹具形状兼容(§B3b4)。
    _ea_pd = {'decision': '2026-09-10', 'effective': '2026-09-16'}
    pv = {'cells': [
        {'region': 'JP', 'dimension': 'policy', 'metric_id': 'JP_POLICY_RATE',
         'anchors': {'最新一期': {'status': 'ok'}}},
        {'region': 'EA', 'dimension': 'policy', 'metric_id': 'ECB_MRO',
         'anchors': {'最新一期': {'status': 'ok',
                                 'policy_dates': dict(_ea_pd)}}}]}
    face_real = rmp.official_policy_record_face(
        pv, pairs, '2026-11-22', question=Q_T3,
        calendar_path=os.path.join(ROOT, 'config', 'release_calendar.json'))
    pv_nod = {'cells': [
        {'region': 'JP', 'dimension': 'policy',
         'anchors': {'最新一期': {'status': 'ok'}}},
        {'region': 'EA', 'dimension': 'policy',
         'anchors': {'最新一期': {'status': 'ok'}}}]}
    face_nd = rmp.official_policy_record_face(
        pv_nod, pairs, '2026-11-22', question=Q_T3,
        calendar_path=os.path.join(ROOT, 'config', 'release_calendar.json'))
    gnd = [g for g in face_nd.get('gaps') or [] if g.get('region') == 'EA']
    _tmp = tempfile.mkdtemp(prefix='r32b3_', dir=TMPG)
    cal_p = os.path.join(_tmp, 'cal_pending.json')
    _cal_write(cal_p, [
        {"entry_id": "FX-JP-PEND", "kind": "policy_decision",
         "metric_id": "JP_POLICY_TARGET", "obs_from": "2026-11-18",
         "obs_to": "2099-12-31", "decision_date": "2026-11-18",
         "effective_on": "2026-12-01", "target_value": 1.5,
         "first_publish_on_or_after": "2026-11-18"},
        {"entry_id": "FX-EA-MNT", "kind": "policy_maintenance",
         "metric_id": "ECB_MRO", "obs_from": "2026-10-30",
         "obs_to": "2099-12-31", "decision_date": "2026-10-30",
         "target_value": 3.15, "first_publish_on_or_after": "2026-10-30"}])
    face_p = rmp.official_policy_record_face(
        pv, pairs, '2026-11-22', question=Q_T3, calendar_path=cal_p)
    gp = [g for g in face_p.get('gaps') or []
          if g.get('gap') == 'current_target_missing_evidence']
    check('§B3b 真实日历(截止 11-22): JP 目标 1.25 已生效→零缺证;EA 无'
          '日历实录但序列面决议/生效日可推→不触发;EA 不可推→缺口点名'
          '「无官方记录」(不以市场序列值冒充)',
          not face_real.get('gaps')
          and face_real.get('required_regions') == ['EA', 'JP']
          and len(gnd) == 1 and '无官方记录' in str(gnd[0].get('note')),
          f'real_gaps={face_real.get("gaps")} ea_noderiv={gnd}')
    # B3b4 锚级键在读(真管线形状)+旧格级键兼容+当期锚非 ok 不算可推
    pv_legacy = {'cells': [
        {'region': 'JP', 'dimension': 'policy',
         'anchors': {'最新一期': {'status': 'ok'}}},
        {'region': 'EA', 'dimension': 'policy',
         'anchors': {'最新一期': {'status': 'ok'}},
         'policy_dates': dict(_ea_pd)}]}
    face_lg = rmp.official_policy_record_face(
        pv_legacy, pairs, '2026-11-22', question=Q_T3,
        calendar_path=os.path.join(ROOT, 'config', 'release_calendar.json'))
    pv_notok = {'cells': [
        {'region': 'JP', 'dimension': 'policy',
         'anchors': {'最新一期': {'status': 'ok'}}},
        {'region': 'EA', 'dimension': 'policy',
         'anchors': {'最新一期': {'status': 'missing',
                                 'policy_dates': dict(_ea_pd)},
                     '3个月前': {'status': 'ok',
                                'policy_dates': dict(_ea_pd)}}}]}
    face_nk = rmp.official_policy_record_face(
        pv_notok, pairs, '2026-11-22', question=Q_T3,
        calendar_path=os.path.join(ROOT, 'config', 'release_calendar.json'))
    gnk = [g for g in face_nk.get('gaps') or [] if g.get('region') == 'EA']
    pv_half = {'cells': [
        {'region': 'JP', 'dimension': 'policy',
         'anchors': {'最新一期': {'status': 'ok'}}},
        {'region': 'EA', 'dimension': 'policy',
         'anchors': {'最新一期': {'status': 'ok', 'policy_dates': {
             'decision': '2026-09-10', 'effective': None}}}}]}
    face_hf = rmp.official_policy_record_face(
        pv_half, pairs, '2026-11-22', question=Q_T3,
        calendar_path=os.path.join(ROOT, 'config', 'release_calendar.json'))
    check('§B3b4 可推性读数: 锚级 policy_dates(真管线形状)判可推;旧格级键'
          '兼容;当期锚非 ok(仅历史锚可推)→不可推=缺口;决议/生效缺一'
          '→不可推=缺口',
          not face_lg.get('gaps') and len(gnk) == 1
          and '无官方记录' in str(gnk[0].get('note'))
          and [g.get('region') for g in face_hf.get('gaps') or []] == ['EA'],
          f'legacy={face_lg.get("gaps")} notok={gnk} half={face_hf.get("gaps")}')
    # B3b3 真管线回归: 真计划点值格(T3 原问×提交的 11 月冻结快照,离线
    # plan,S 步替身)直取后判定——修复前(读格级键)真管线恒判 EA 缺口
    # (正式入口真跑复现: 草稿 map_official_target_missing),修复后零缺口。
    _t3o, _res3o, _md3o, _seen3o = _offline_plan('t3opr', Q_T3)
    rep3o = json.load(open(os.path.join(_res3o['report_dir'], 'report.json'),
                           encoding='utf-8'))
    rp3o = rep3o.get('research_plan') or {}
    pv3o = rp3o.get('point_values') or {}
    pairs3o = {(eco, dim)
               for eco, _rf in (rp3o.get('regions') or {}).items()
               for dim in ((_rf.get('dimensions') or {}) or {})}
    ea3o = [c for c in pv3o.get('cells') or []
            if c.get('region') == 'EA' and c.get('dimension') == 'policy']
    la3o = ((ea3o[0].get('anchors') or {}).get('最新一期') or {}) if ea3o else {}
    pd3o = la3o.get('policy_dates') or {}
    face3o = rmp.official_policy_record_face(
        pv3o, pairs3o, rp3o.get('cutoff'), question=Q_T3,
        calendar_path=os.path.join(_t3o, 'config', 'release_calendar.json'))
    check('§B3b3 真管线回归(T3 原问×冻结快照真计划点值格): EA 政策格 '
          'policy_dates 在锚上(决议 2026-09-10/生效 2026-09-16)、格级键'
          '缺席;官方记录面零缺口、要求地区={EA,JP}(「序列+惯例可推」'
          '回退在真管线生效)',
          len(ea3o) >= 1
          and all('policy_dates' not in c for c in ea3o)
          and pd3o.get('decision') == '2026-09-10'
          and pd3o.get('effective') == '2026-09-16'
          and not face3o.get('gaps')
          and face3o.get('required_regions') == ['EA', 'JP']
          and [r.get('region') for r in face3o.get('rows') or []] == ['JP'],
          f'ea_cells={len(ea3o)} anchor_pd={pd3o.get("decision")}/'
          f'{pd3o.get("effective")} gaps={face3o.get("gaps")}')
    # 真管线对照(修复前后读数面): 抽去锚级 policy_dates(=修复前唯一读到的
    # 格级键缺席)→EA 缺口点名;blocked_class_of 同源同判(真点值格+真地区
    # 计划,R28 门最小 report 形状): 原样→None,抽去→map_official_target_missing
    import copy as _copy_r32
    pv_strip = _copy_r32.deepcopy(pv3o)
    for _c in pv_strip.get('cells') or []:
        for _a in (_c.get('anchors') or {}).values():
            _a.pop('policy_dates', None)

    def _rep_real(pv_x):
        return {'run_ok': True,
                'layers': {'L1_事实层': {'rows': [{'x': 1}]}},
                'run': {'question': Q_T3, 'data_requirements': {'items': []}},
                'steps': [],
                'agent_judgment': {'reader_map_faces': {'complete': True}},
                'research_plan': {'map_question': True,
                                  'cutoff': rp3o.get('cutoff'),
                                  'point_anchors': [{'label': '最新一期',
                                                     'months_before': 0}],
                                  'regions': rp3o.get('regions') or {},
                                  'point_values': pv_x}}

    _cal3o = os.path.join(_t3o, 'config', 'release_calendar.json')
    _face_st = rmp.official_policy_record_face(
        pv_strip, pairs3o, rp3o.get('cutoff'), question=Q_T3,
        calendar_path=_cal3o)
    _bc_real = aj.blocked_class_of(_rep_real(pv3o), calendar_path=_cal3o)
    _bc_strip = aj.blocked_class_of(_rep_real(pv_strip), calendar_path=_cal3o)
    check('§B3b5 真管线对照: 抽去锚级 policy_dates(=修复前读数面)→EA 缺口'
          '点名+blocked_class=map_official_target_missing;原样→零缺口+'
          'blocked_class=None(缺口判定确由锚级读数驱动)',
          [g.get('region') for g in _face_st.get('gaps') or []] == ['EA']
          and not face3o.get('gaps')
          and _bc_strip == 'map_official_target_missing'
          and _bc_real is None,
          f'strip_gaps={_face_st.get("gaps")} bc_real={_bc_real} '
          f'bc_strip={_bc_strip}')
    check('§B3b2 仅有待生效公告(决议 11-18/生效 12-01/目标 1.5)→gaps 点名 '
          'JP current_target_missing_evidence+待生效值/决议日/生效日',
          len(gp) == 1 and gp[0].get('region') == 'JP'
          and gp[0].get('pending_target') == 1.5
          and gp[0].get('pending_decision') == '2026-11-18'
          and gp[0].get('pending_effective_on') == '2026-12-01'
          and '决议日 2026-11-18' in str(gp[0].get('note'))
          and '决议日 None' not in str(gp[0].get('note')),
          f'pending={gp}')
    check('§B3c 行级缺口同判: JP 行 current_target_missing_evidence=True+'
          'official_target=None(待生效值不入官方目标列)',
          any(r.get('region') == 'JP'
              and r.get('current_target_missing_evidence') is True
              and r.get('official_target') is None
              and r.get('pending_target') == 1.5
              for r in face_p.get('rows') or []),
          f"rows={ {r.get('region'): (r.get('official_target'), r.get('pending_target')) for r in face_p.get('rows') or []} }")
    # B4 首页草稿+正式归档拒绝同判(真实管线;R23 基线工单+夹具日历)
    T = build_tree('pending')
    strip_policy_entries(os.path.join(T, 'config', 'release_calendar.json'),
                         {'JP_POLICY_TARGET', 'ECB_MRO', 'ECB_DFR'})
    _c = json.load(open(os.path.join(T, 'config', 'release_calendar.json'),
                        encoding='utf-8'))
    _c['entries'].extend([
        {"entry_id": "FX-JP-PEND", "kind": "policy_decision",
         "metric_id": "JP_POLICY_TARGET", "obs_from": "2026-11-18",
         "obs_to": "2099-12-31", "decision_date": "2026-11-18",
         "effective_on": "2026-12-01", "target_value": 1.5,
         "first_publish_on_or_after": "2026-11-18"},
        {"entry_id": "FX-EA-MNT", "kind": "policy_maintenance",
         "metric_id": "ECB_MRO", "obs_from": "2026-10-30",
         "obs_to": "2099-12-31", "decision_date": "2026-10-30",
         "target_value": 3.15, "first_publish_on_or_after": "2026-10-30"}])
    with open(os.path.join(T, 'config', 'release_calendar.json'), 'w',
              encoding='utf-8') as f:
        json.dump(_c, f, ensure_ascii=False, indent=2)
    rd = os.path.join(TMPG, 'rd_pending')
    os.makedirs(rd)
    for f_ in RUN_FILES:
        shutil.copy2(os.path.join(R23_SRC, f_), rd)
    p = os.path.join(rd, 'report.json')
    rj = json.load(open(p, encoding='utf-8'))
    rj['run']['question'] = Q_T3
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(rj, f, ensure_ascii=False, indent=2, default=str)
    import research_orchestrator as _ro
    with open(os.path.join(rd, 'report.md'), 'w', encoding='utf-8') as f:
        f.write(_ro._render_md(rj))
    if os.path.exists(os.path.join(rd, 'FULL_REPORT.md')):
        os.remove(os.path.join(rd, 'FULL_REPORT.md'))
    # 先重渲(T3 问句版地图;旧裁决不在树内=不受审冻结)再落裁决——R24
    # 已裁正文冻结语义: 裁决后改问句不重写受审字节
    rc0, d0 = cli('report', rd, T)
    dd0 = d0.get('data') or {}
    aj.record_semantic_verdict(T, rd, 'UPHELD', reviewer='r32gate-pending席',
                               notes='R32 任务2: 仅有待生效公告裁决基线')
    rc1, d1 = cli('report', rd, T)
    dd1 = d1.get('data') or {}
    mdir1 = os.path.join(rd, 'MAP_REPORT.md')
    map1 = open(mdir1, encoding='utf-8').read() if os.path.isfile(mdir1) else ''
    full1 = open(os.path.join(rd, 'FULL_REPORT.md'),
                 encoding='utf-8').read() if os.path.isfile(
                     os.path.join(rd, 'FULL_REPORT.md')) else ''
    check('§B4a 真实管线: T3 问句×仅有待生效公告→report rc≠0+草稿交付+'
          'blocked_class=map_official_target_missing(重渲前后同判)',
          rc0 != 0 and dd0.get('blocked_class')
          == 'map_official_target_missing'
          and rc1 != 0 and dd1.get('draft_delivered') is True
          and dd1.get('deliverable') is False
          and dd1.get('blocked_class') == 'map_official_target_missing',
          f"rc0={rc0} bc0={dd0.get('blocked_class')} rc1={rc1} "
          f"draft={dd1.get('draft_delivered')} bc={dd1.get('blocked_class')}")
    check('§B4b 首页草稿同判: 地图首页=「草稿(非正式):缺官方政策目标」+'
          '「当前官方政策目标缺证(仅有待生效公告)」+待生效值/生效日+原问=T3',
          '草稿(非正式)' in map1 and '缺官方政策目标' in map1
          and '当前官方政策目标缺证(仅有待生效公告)' in map1
          and '1.5' in map1 and '2026-12-01' in map1
          and Q_T3[:20] in map1,
          f"map_head={map1[:200]!r}")
    rc2, d2 = cli('archive', rd, T, arc=os.path.join(TMPG, 'arc_pending'))
    check('§B4c 正式归档拒绝同判: blocked=not_deliverable,零归档目录',
          rc2 != 0 and (d2.get('data') or {}).get('blocked')
          == 'not_deliverable'
          and not os.path.isdir(os.path.join(TMPG, 'arc_pending')),
          f"rc={rc2} blocked={(d2.get('data') or {}).get('blocked')}")
    check('§B4d 完整报告面同判: FULL_REPORT 质量状态节 run 门 blocked_class='
          'map_official_target_missing+deliverable(可交付)=False',
          'blocked_class=map_official_target_missing' in full1
          and 'deliverable(可交付): False' in full1,
          f'full_len={len(full1)} tail={full1[-260:]!r}')


# ═══ §C 任务3: 冻结-裁决-交付链 ═══
def sec_c():
    print('═══ §C 任务3: 冻结/裁决/交付链共用本工单冻结输入 ═══')
    # C0 基线发现(不可变证据,源包保持原字节): R31 入库 NEW30 包裁决件
    # 名缺日目录前缀(verdicts/VERDICT-*.json≠manifest.file
    # verdicts/20261123__VERDICT-*.json,内容哈希同值)→重放门①缺档拒
    pk0 = os.path.join(TMPG, 'pkg_r31_new30')
    shutil.copytree(os.path.join(R31_ACC, 'session_NEW30'), pk0)
    rc0, d0 = replay(pk0, ROOT, out=os.path.join(TMPG, 'rp_r31_new30'))
    ck0 = {c.get('check'): c.get('ok') for c in
           ((d0.get('data') or {}).get('checks') or []) if c.get('check')}
    det0 = {c.get('check'): str(c.get('detail')) for c in
            ((d0.get('data') or {}).get('checks') or []) if c.get('check')}
    check('§C0 基线: 入库 R31 NEW30 包按清单原样解包→重放拒绝(rc=1: '
          'completeness_files 裁决链缺档 2+verdict_chain_hashes 缺席),'
          '其余门(冻结件/运行 SHA/内容摘要)全绿——缺件必须拒绝',
          rc0 != 0 and ck0.get('completeness_files') is False
          and ck0.get('verdict_chain_hashes') is False
          and '裁决链缺档' in det0.get('completeness_files', '')
          and ck0.get('frozen_inputs_present') is True
          and ck0.get('run_code_sha_crosscheck') is True
          and ck0.get('content_digest_match') is True
          and ck0.get('verdict_binding_threeway') is False,
          f"rc={rc0} failed={[k for k, v in ck0.items() if v is False]}")
    # C1 工单钉死: 提交的 R31 正式包(NEW30: REVISE→UPHELD 链;旧档无
    # evidence_gate=as_of 不钉,重渲逐字节沿用旧口径)
    rd, src = fresh_pkg_rd('pins', 'session_NEW30')
    saved = {k: os.environ.get(k) for k in aj._PIN_ENV_KEYS}
    with aj.work_order_pins(rd, ROOT) as info:
        inside = {k: os.environ.get(k) for k in aj._PIN_ENV_KEYS}
    after = {k: os.environ.get(k) for k in aj._PIN_ENV_KEYS}
    check('§C1 work_order_pins: overlay 逐件 sha16 核对通过→钉死日历/注册表'
          '/源快照;旧档(无 evidence_gate)as_of 不钉;退出恢复',
          info.get('pinned') is True and bool(info.get('calendar_path'))
          and info.get('calendar_path', '').endswith(
              'root_overlay/config/release_calendar.json')
          and bool(info.get('snapshot_path'))
          and os.path.basename(info.get('snapshot_path') or '') \
          == 'research_snapshot_20261122_v2.json'
          and inside.get('IA_CALENDAR_PIN') == info.get('calendar_path')
          and inside.get('IA_REGISTRY_PIN') == info.get('registry_path')
          and inside.get('IA_SNAPSHOT_PIN') == info.get('snapshot_path')
          and info.get('as_of') is None
          and inside.get('IA_EVIDENCE_ASOF') is None
          and after == saved,
          f"info={ {k: info.get(k) for k in ('pinned', 'calendar_path', 'snapshot_path', 'as_of')} }")
    # C2 缺件/篡改=fail-closed(attach/report/archive 同拒)
    def _pins_err(mutate):
        d = os.path.join(TMPG, 'rd_pins_%d' % int(time.time() * 1000 % 100000))
        shutil.copytree(rd, d)
        mutate(d)
        try:
            with aj.work_order_pins(d, ROOT):
                return None
        except aj.WorkOrderPinsError as e:
            return e.code

    def _rm_cal(d):
        os.remove(os.path.join(d, 'root_overlay', 'config',
                               'release_calendar.json'))

    def _t_cal(d):
        pth = os.path.join(d, 'root_overlay', 'config',
                           'release_calendar.json')
        c = json.load(open(pth, encoding='utf-8'))
        c['entries'] = [e for e in c.get('entries') or []
                        if e.get('entry_id') != 'RC-JP-BOJ-TARGET-2026-09']
        json.dump(c, open(pth, 'w', encoding='utf-8'), ensure_ascii=False)
    check('§C2 缺件→frozen_input_missing;篡改(删一条日历)→'
          'frozen_input_tampered(不回落引擎本地文件)',
          _pins_err(_rm_cal) == 'frozen_input_missing'
          and _pins_err(_t_cal) == 'frozen_input_tampered')
    # C3 report/archive 对篡改包: 拒绝且不改写交付件
    T = build_tree('pins')
    _seed_verdicts(T, 'session_NEW30')
    rd_t = os.path.join(TMPG, 'rd_pins_tamper')
    shutil.copytree(rd, rd_t)
    _t_cal(rd_t)
    before = open(os.path.join(rd_t, 'MAP_REPORT.md'), 'rb').read()
    rc_r, d_r = cli('report', rd_t, T)
    after = open(os.path.join(rd_t, 'MAP_REPORT.md'), 'rb').read()
    rc_a, d_a = cli('archive', rd_t, T,
                    arc=os.path.join(TMPG, 'arc_pins_tamper'))
    da = d_a.get('data') or {}
    check('§C3 report 对篡改冻结件: rc=1+blocked=frozen_inputs_invalid+'
          'code=frozen_input_tampered+MAP_REPORT 字节不变',
          rc_r == 1 and (d_r.get('data') or {}).get('blocked')
          == 'frozen_inputs_invalid'
          and ((d_r.get('data') or {}).get('frozen_inputs_check') or {})
          .get('code') == 'frozen_input_tampered'
          and before == after,
          f"rc={rc_r} data={ {k: (d_r.get('data') or {}).get(k) for k in ('blocked', 'frozen_inputs_check')} }")
    check('§C3b archive 对篡改冻结件: 拒绝(frozen_inputs_invalid+「冻结件与'
          '运行时摘要不符」)+零归档目录',
          rc_a != 0 and da.get('blocked') == 'frozen_inputs_invalid'
          and '冻结件与运行时摘要不符' in str(da.get('error'))
          and not os.path.isdir(os.path.join(TMPG, 'arc_pins_tamper')),
          f"rc={rc_a} blocked={da.get('blocked')} err={da.get('error')}")
    rd_m = os.path.join(TMPG, 'rd_pins_missing')
    shutil.copytree(rd, rd_m)
    _rm_cal(rd_m)
    rc_m, d_m = cli('archive', rd_m, T,
                    arc=os.path.join(TMPG, 'arc_pins_missing'))
    check('§C3c archive 对缺件包: 拒绝(frozen_inputs_invalid+'
          'frozen_input_missing)',
          rc_m != 0 and (d_m.get('data') or {}).get('blocked')
          == 'frozen_inputs_invalid'
          and ((d_m.get('data') or {}).get('frozen_inputs_check') or {})
          .get('code') == 'frozen_input_missing',
          f"rc={rc_m} {(d_m.get('data') or {}).get('frozen_inputs_check')}")
    # C4 引擎本地日历被换→判定与重渲同读 overlay(字节不变)
    rd4, _src4 = fresh_pkg_rd('swap', 'session_NEW30')
    # 夹具: 复本报告补 r32 证据口径(=真 plan 段落的 run.evidence_gate/
    # evidence_asof;此处只验归档/钉死/重放链对 r32 面的贯通,真值见 §D/§A)
    _p4 = os.path.join(rd4, 'report.json')
    _rj4 = json.load(open(_p4, encoding='utf-8'))
    _rj4['run']['evidence_gate'] = {
        'discipline': 'r32', 'as_of': '2026-11-22',
        'source_snapshot_id': 'research_snapshot_20261122_v2',
        'source_target_date': '2026-11-22', 'historical_view': False,
        'counts': {'facts_kept': 105, 'facts_rebuilt': 0,
                   'facts_dropped': 0, 'facts_excluded_version': 0,
                   'series_observations_dropped': 0,
                   'series_observations_version_unavailable': 0,
                   'series_excluded': 0, 'series_n': 90},
        'series': {}}
    _rj4['run']['evidence_asof'] = '2026-11-22'
    with open(_p4, 'w', encoding='utf-8') as f:
        json.dump(_rj4, f, ensure_ascii=False, indent=2, default=str)
    # 运行 SHA 改写+report.md 按当前 report.json 重渲(多副本一致)+旧
    # FULL_REPORT 撤除(质量状态节重装)
    rewrite_head(rd4, WORKTREE_HEAD)
    T4 = build_tree('swap')
    _seed_verdicts(T4, 'session_NEW30')
    rc0, d0 = cli('report', rd4, T4)
    man0 = json.load(open(os.path.join(rd4, 'report.json'),
                          encoding='utf-8'))
    rc_v = aj.record_semantic_verdict(T4, rd4, 'UPHELD',
                                      reviewer='r32gate-swap席',
                                      notes='R32 任务3: 引擎日历被换对照基线')
    rc1, d1 = cli('report', rd4, T4)
    dd1 = d1.get('data') or {}
    map_a = open(os.path.join(rd4, 'MAP_REPORT.md'), 'rb').read()
    T4s = build_tree('swap_stripped')
    _seed_verdicts(T4s, 'session_NEW30')
    _vd = os.path.join(T4s, 'audit', 'semantic_review')
    if os.path.isdir(os.path.join(T4, 'audit', 'semantic_review')):
        shutil.rmtree(_vd, ignore_errors=True)
        shutil.copytree(os.path.join(T4, 'audit', 'semantic_review'), _vd)
    strip_policy_entries(
        os.path.join(T4s, 'config', 'release_calendar.json'),
        {'JP_POLICY_TARGET'})
    rc2, d2 = cli('report', rd4, T4s)
    dd2 = d2.get('data') or {}
    map_b = open(os.path.join(rd4, 'MAP_REPORT.md'), 'rb').read()
    check('§C4a 基线: NEW30 复本(运行 SHA=HEAD+r32 证据口径)report(旧裁决'
          '过期=不可交付)→新裁决 UPHELD 落档→report rc=0 可交付',
          rc0 != 0 and isinstance(rc_v, str) and os.path.isfile(rc_v)
          and rc1 == 0 and dd1.get('deliverable') is True,
          f"rc0={rc0} rc1={rc1} dd1={ {k: dd1.get(k) for k in ('deliverable', 'blocked_class', 'blocked')} }")
    check('§C4b 引擎本地日历被换(删日银 09-18 决议实录): report 仍 rc=0 '
          '可交付(判定读 overlay 冻结日历)+MAP_REPORT 逐字节不变',
          rc2 == 0 and dd2.get('deliverable') is True
          and dd2.get('blocked_class') is None and map_a == map_b,
          f"rc2={rc2} dd2={ {k: dd2.get(k) for k in ('deliverable', 'blocked_class', 'blocked')} } eq={map_a == map_b}")
    _fp = open(os.path.join(rd4, 'FULL_REPORT.md'), encoding='utf-8').read()
    _fh = [ln for ln in _fp.splitlines() if '研究截止日(证据口径 r32)' in ln]
    check('§C4b2 FULL_REPORT 证据口径行(快照版本日口径,report 阶段重渲): '
          '尾注完整,无「None」/悬空「快照版本日」',
          len(_fh) == 1
          and _fh[0].rstrip().endswith('快照版本日口径(截止日=快照版本日)')
          and 'None' not in _fh[0]
          and not any(ln.rstrip().endswith('| 快照版本日')
                      for ln in _fp.splitlines()),
          _fh[0] if _fh else _fp[:300])
    arc = os.path.join(TMPG, 'arc_swap')
    rc3, d3 = cli('archive', rd4, T4, arc=arc)
    man3 = json.load(open(os.path.join(arc, 'ARCHIVE_MANIFEST.json'),
                          encoding='utf-8')) if rc3 == 0 else {}
    check('§C4c archive: 包内带 root_overlay+manifest 记 evidence_gate/'
          'evidence_asof+运行 SHA=HEAD',
          rc3 == 0 and os.path.isdir(os.path.join(arc, 'root_overlay'))
          and isinstance(man3.get('evidence_gate'), dict)
          and man3.get('evidence_asof') == '2026-11-22'
          and man3.get('run_code_git_head') == WORKTREE_HEAD
          and (man3.get('evidence_gate') or {}).get('as_of') == '2026-11-22',
          f"rc3={rc3} keys={sorted(k for k in man3 if 'evidence' in k)}")
    saved4 = {k: os.environ.get(k) for k in aj._PIN_ENV_KEYS}
    with aj.work_order_pins(arc, T4) as info4:
        inside4 = {k: os.environ.get(k) for k in aj._PIN_ENV_KEYS}
    check('§C4d r32 包工单钉死: as_of=2026-11-22 自 run.evidence_gate 带入'
          '(IA_EVIDENCE_ASOF 钉死=研究席/证据索引/重放同口径);退出恢复',
          info4.get('as_of') == '2026-11-22'
          and inside4.get('IA_EVIDENCE_ASOF') == '2026-11-22'
          and inside4.get('IA_CALENDAR_PIN') == os.path.join(
              arc, 'root_overlay', 'config', 'release_calendar.json')
          and {k: os.environ.get(k) for k in aj._PIN_ENV_KEYS} == saved4,
          f"as_of={info4.get('as_of')} inside={ {k: bool(v) for k, v in inside4.items()} }")
    # C5 重放: 引擎本地日历被换/重复/缺件/篡改
    rc4, d4 = replay(arc, T4s, out=os.path.join(TMPG, 'rp_swap'))
    dd4 = d4.get('data') or {}
    time.sleep(1.2)
    rc5, d5 = replay(arc, T4, out=os.path.join(TMPG, 'rp_swap2'))
    dd5 = d5.get('data') or {}
    check('§C5a 重放(引擎日历被换 T4s)rc=0+byte_equal+零失败检查;重复'
          '重放(正常 T4)同=byte_equal(确定性)',
          rc4 == 0 and dd4.get('render_mode') == 'byte_equal'
          and dd4.get('failed_checks') == []
          and rc5 == 0 and dd5.get('render_mode') == 'byte_equal'
          and dd5.get('failed_checks') == [],
          f"rc4={rc4} {dd4.get('render_mode')} {dd4.get('failed_checks')} | "
          f"rc5={rc5} {dd5.get('render_mode')} {dd5.get('failed_checks')}")
    pk_t = os.path.join(TMPG, 'pkg_tamper')
    shutil.copytree(arc, pk_t)
    _c = json.load(open(os.path.join(pk_t, 'root_overlay', 'config',
                                     'release_calendar.json'),
                        encoding='utf-8'))
    _c['entries'] = [e for e in _c.get('entries') or []
                     if e.get('entry_id') != 'RC-JP-BOJ-MAINT-2026-10']
    json.dump(_c, open(os.path.join(pk_t, 'root_overlay', 'config',
                                    'release_calendar.json'), 'w',
                       encoding='utf-8'), ensure_ascii=False)
    rc6, d6 = replay(pk_t, T4, out=os.path.join(TMPG, 'rp_tamper'))
    dd6 = d6.get('data') or {}
    pk_m = os.path.join(TMPG, 'pkg_missing')
    shutil.copytree(arc, pk_m)
    os.remove(os.path.join(pk_m, 'root_overlay', 'data', 'daily',
                           'research_snapshot_20261122_v2.json'))
    rc7, d7 = replay(pk_m, T4, out=os.path.join(TMPG, 'rp_missing'))
    dd7 = d7.get('data') or {}
    check('§C5b 包内冻结日历被改→重放拒绝(冻结摘要不符);快照缺件→拒绝'
          '(fail-closed,不回落引擎本地文件)',
          rc6 != 0 and (dd6.get('failed_checks') or [])
          and rc7 != 0 and (dd7.get('failed_checks') or []),
          f"rc6={rc6} {dd6.get('failed_checks')} | rc7={rc7} "
          f"{dd7.get('failed_checks')}")
    # C6 冻结初始化中途失败=清理(无半套钉死残留)→下一工单选新快照
    import research_orchestrator as ro
    t6, _ = _mk_tree('freeze', with_snapshot=False)
    v1 = os.path.join(t6, 'data', 'daily', 'research_snapshot_20261122.json')
    json.dump({'snapshot_id': 'research_snapshot_20261122',
               'target_date': '20261122', 'facts': [],
               'series_store': {}}, open(v1, 'w', encoding='utf-8'))
    _orig_latest = wd.latest_snapshot
    _calls = [0]

    def _boom_second(root=None):
        _calls[0] += 1
        if _calls[0] == 2:
            raise OSError('r32gate: 冻结初始化中途失败探针')
        return _orig_latest(root)

    def _frozen_dirs():
        return {p for p in os.listdir(tempfile.gettempdir())
                if p.startswith('ia_frozen_inputs_')}
    base_dirs = _frozen_dirs()
    wd.latest_snapshot = _boom_second
    try:
        ro._pin_frozen_inputs(wd, t6)
        raised_a = False
    except OSError:
        raised_a = True
    finally:
        wd.latest_snapshot = _orig_latest
    left_a = sorted(_frozen_dirs() - base_dirs)
    # 场景 b: 临时副本已建+注册表已钉后日历读取失败(权限拒)
    cal6 = os.path.join(t6, 'config', 'release_calendar.json')
    os.chmod(cal6, 0o000)
    try:
        ro._pin_frozen_inputs(wd, t6)
        raised_b = False
    except OSError:
        raised_b = True
    finally:
        os.chmod(cal6, 0o644)
    left_b = sorted(_frozen_dirs() - base_dirs)
    resid_b = [k for k in aj._PIN_ENV_KEYS if os.environ.get(k)]
    v2 = os.path.join(t6, 'data', 'daily', 'research_snapshot_20261122_v2.json')
    json.dump({'snapshot_id': 'research_snapshot_20261122_v2',
               'target_date': '20261122', 'facts': [],
               'series_store': {}}, open(v2, 'w', encoding='utf-8'))
    keys, tmpdir, cov = ro._pin_frozen_inputs(wd, t6)
    pick = os.environ.get('IA_SNAPSHOT_PIN')
    reg_pin = os.environ.get('IA_REGISTRY_PIN')
    ro._release_frozen_inputs(keys, tmpdir)
    left_c = sorted(_frozen_dirs() - base_dirs)
    check('§C6 冻结初始化中途失败两场景(快照已钉后读取异常/临时副本+注册'
          '表已钉后日历读取失败)→异常如实上抛+env 无残留+临时副本清理;'
          '下一工单选新快照 _v2(覆盖日 11-22)后释放复原',
          raised_a and not left_a
          and raised_b and not left_b and not resid_b
          and pick == v2 and cov == '2026-11-22' and bool(reg_pin)
          and not left_c
          and all(os.environ.get(k) is None for k in aj._PIN_ENV_KEYS),
          f'a={raised_a}/{left_a} b={raised_b}/{left_b}/{resid_b} '
          f'pick={pick} cov={cov} left_c={left_c}')


# ═══ §D 任务4: T3 原问经 --question-file 原样输入 ═══
def sec_d():
    import ia_cli
    import research_orchestrator as ro
    print('═══ §D 任务4: T3 原问 --question-file 原样输入 ═══')
    t, _snap = _mk_tree('t3')
    out = os.path.join(t, 'out')
    qf = os.path.join(QDIR, 'question_T3.txt')
    orig = ro.run_step
    ro.run_step = _fake_step_ok
    buf = io.StringIO()
    rc = None
    try:
        with contextlib.redirect_stdout(buf):
            try:
                ia_cli.main(['research-one', '--stage', 'plan',
                             '--question-file', qf, '--engine-root', t,
                             '--out-dir', out])
            except SystemExit as e:
                rc = e.code
    finally:
        ro.run_step = orig
    try:
        d = json.loads(buf.getvalue())
    except Exception:                            # noqa: BLE001
        d = {}
    rdd = (d.get('data') or {}).get('report_dir')
    rj = json.load(open(os.path.join(rdd, 'report.json'),
                        encoding='utf-8')) if rdd else {}
    rp = rj.get('research_plan') or {}
    ad = rp.get('as_of_declared') or {}
    env_doc = json.load(open(os.path.join(rdd, 'AGENT_SEAT_ENVELOPE.json'),
                             encoding='utf-8')) if rdd else {}
    q_bytes = open(qf, 'rb').read()
    check('§D1 plan 段经 --question-file: 问句逐字=文件字节(run.question/'
          'research_plan.question_verbatim/席位信封三处同句;report 段'
          'question_verbatim.txt 同字节——见 §C4 归档包)',
          rc == 0 and (rj.get('run') or {}).get('question') == Q_T3
          and rp.get('question_verbatim') == Q_T3
          and env_doc.get('question') == Q_T3
          and Q_T3.encode('utf-8') == q_bytes.rstrip(b'\n')
          and len(q_bytes) > 100 and b'?' in q_bytes,
          f"rc={rc} len={len(q_bytes)} q={(rj.get('run') or {}).get('question')[:30]!r} "
          f"verbatim={str(rp.get('question_verbatim'))[:30]!r}")
    check('§D2 T3 路由: 地图问句+官方目标地区 {EA,JP} 进计划(计划内政策'
          '对含 JP/EA)+欧日地区在场',
          rp.get('map_question') is True
          and set(rp.get('official_target_regions') or
                  rmp.question_official_target_regions(Q_T3)) == {'EA', 'JP'}
          and {'JP', 'EA'} <= set((rp.get('regions') or {}).keys())
          and ('JP', 'policy') in {(e, d) for e, dims
                                   in (rp.get('regions') or {}).items()
                                   for d in (dims.get('dimensions') or {})},
          f"regions={sorted((rp.get('regions') or {}).keys())} "
          f"otr={rp.get('official_target_regions')}")
    md_d = open(os.path.join(rdd, 'report.md'),
                encoding='utf-8').read() if rdd else ''
    check('§D3 2026年11月=裸年月+双相对约束(最近六个月/去年同月)=R31 既档'
          '不按时点化合并: 截止日=快照版本日 11-22(不晚于该月)+如实点名'
          '裸年月(首页/读者版披露;NEW30 单一相对窗=月末夹紧形,见 §A5)',
          rp.get('cutoff') == '2026-11-22'
          and ad.get('clamped_to_coverage') is False
          and ad.get('bare_year_month') == '2026年11月'
          and ad.get('as_of') == '2026-11-22'
          and '问句含裸年月 2026年11月' in md_d
          and '研究截止日=快照版本日 2026-11-22' in md_d,
          f"cutoff={rp.get('cutoff')} ad={ {k: ad.get(k) for k in ('clamped_to_coverage', 'bare_year_month', 'as_of', 'requested_month_end')} }")
    check('§D4 工单/席位面: AGENT_SEAT_ENVELOPE 在场+证据索引落盘+'
          'run.evidence_gate.as_of=2026-11-22(研究席与证据同口径)',
          bool(rdd) and os.path.isfile(os.path.join(rdd, 'evidence_index.json'))
          and (rj.get('run') or {}).get('evidence_gate', {}).get('as_of')
          == '2026-11-22'
          and isinstance(env_doc, dict)
          and os.path.isdir(os.path.join(rdd, 'root_overlay'))
          and bool((rj.get('run') or {}).get('frozen_inputs'))
          and (rj.get('run') or {}).get('evidence_gate', {}).get('counts',
                                                                 {}).get('facts_dropped', -1) == 0
          and set(((rj.get('run') or {}).get('frozen_inputs') or {})
                  .keys()) == {'config/metric_registry.json',
                               'config/release_calendar.json',
                               'data/daily/research_snapshot_20261122_v2.json'},
          f"rd={rdd} eg={(rj.get('run') or {}).get('evidence_gate', {}).get('as_of')} "
          f"fi={sorted(((rj.get('run') or {}).get('frozen_inputs') or {}).keys())}")
    shutil.rmtree(t, ignore_errors=True)


def sec_h():
    """干净安装真跑实中(2026-11-23 update --yes: 10/15 Gate A 失败,status=None,
    illegal_quality "GOLD_F=quality_status='PASS'与issues重算'DEGRADED'不一致")
    ——基线 72dab1c 同现。根因两处: ①cross_metric_checks 把 DEGRADED issue
    附到已定级 PASS 的事实上不重定级; ②金双载体方向比对不要求同窗(期货
    周一盘中介bar vs ETF 上周五收盘=两个不同的周),方向相反不是异常证据。"""
    from datetime import date, timedelta
    import fact_engine as fe
    import research_provenance as rpv
    import snapshot_builder as sb
    print('═══ §H 真跑实中: 快照质量声明一致性(跨指标重定级+金双载体同窗前提) ═══')
    AS = '2026-11-23T18:00:22+08:00'

    def mk(mid, val, obs, basis, pct):
        f = fe.make_fact(mid, val, obs, AS, 'global_20261123.json',
                         'global_market_collector')
        f['derived'] = {'week': {'basis_date': basis, 'basis_value': 100.0,
                                 'pct_change': pct, 'sessions_in_window': 1,
                                 'expected_sessions': 2}}
        f['issues'] = fe.validate_fact(
            f, {'close': val, 'date': obs}, fe.metric(mid), as_of_date=AS[:10])
        f['quality_status'] = fe.grade_issues(f['issues'])
        return f

    def gold(recon):
        return next((r for r in recon
                     if r.get('check') == '黄金双载体方向'), {})

    # H1 真跑形态: 期货周一盘中(obs 11-23,周基准 11-20,+2.80%) vs
    #    ETF 上周五收盘(obs 11-20,周基准 11-13,−9.17%)——不可比,不附issue
    gf, ge = mk('GOLD_F', 3614.0, '2026-11-23', '2026-11-20', 2.8048), \
        mk('GLD', 322.87, '2026-11-20', '2026-11-13', -9.1659)
    recon = fe.cross_metric_checks([gf, ge])
    g = gold(recon)
    check('§H1 不同周窗口(真跑形态): 金双载体登记 insufficient(写明两基准日)'
          '+GOLD_F 不附跨指标issue+声明=重算 PASS',
          g.get('result') == 'insufficient' and '2026-11-20' in g.get('detail', '')
          and '2026-11-13' in g.get('detail', '')
          and not any(i.get('category') == 'cross-metric' for i in gf['issues'])
          and gf['quality_status'] == 'PASS'
          and rpv.fact_issues_problems(gf, 'GOLD_F') == [],
          f"g={g} status={gf['quality_status']} "
          f"probs={rpv.fact_issues_problems(gf, 'GOLD_F')}")
    # H2 同窗反向=真违规: issue 附上且就地重定级(声明==重算)
    gf, ge = mk('GOLD_F', 3614.0, '2026-11-20', '2026-11-13', 2.8048), \
        mk('GLD', 322.87, '2026-11-20', '2026-11-13', -9.1659)
    recon = fe.cross_metric_checks([gf, ge])
    check('§H2 同窗反向: violation+GOLD_F 就地重定级 DEGRADED(声明==grade_issues)'
          '+fact_issues_problems 空(基线: 声明PASS≠重算DEGRADED)',
          gold(recon).get('result') == 'violation'
          and gf['quality_status'] == 'DEGRADED'
          and gf['quality_status'] == fe.grade_issues(gf['issues'])
          and rpv.fact_issues_problems(gf, 'GOLD_F') == [],
          f"status={gf['quality_status']} probs={rpv.fact_issues_problems(gf, 'GOLD_F')}")
    # H3 同窗同向 / H4 nan 周变化(旧: nan×x<0 恒False→误登"一致")
    gf, ge = mk('GOLD_F', 3614.0, '2026-11-20', '2026-11-13', -2.0), \
        mk('GLD', 322.87, '2026-11-20', '2026-11-13', -9.1659)
    r3 = gold(fe.cross_metric_checks([gf, ge]))
    gf, ge = mk('GOLD_F', 3614.0, '2026-11-20', '2026-11-13', -2.0), \
        mk('GLD', 322.87, '2026-11-20', '2026-11-13', float('nan'))
    r4 = gold(fe.cross_metric_checks([gf, ge]))
    check('§H3 同窗同向=consistent(细节带周基准日); nan 周变化=insufficient',
          r3.get('result') == 'consistent' and '2026-11-13' in r3.get('detail', '')
          and r4.get('result') == 'insufficient',
          f"r3={r3} r4={r4}")
    # H5 check_pair 路径同修: 目标区间下限>上限 → DFEDTARL 重定级
    fl = fe.make_fact('DFEDTARL', 4.25, '2026-11-20', AS,
                      'rate_economy_20261123.json', 'rate_expectations')
    fu = fe.make_fact('DFEDTARU', 4.00, '2026-11-20', AS,
                      'rate_economy_20261123.json', 'rate_expectations')
    for f in (fl, fu):
        f['issues'] = []
        f['quality_status'] = fe.grade_issues(f['issues'])
    r5 = {r.get('check'): r for r in fe.cross_metric_checks([fl, fu])}
    check('§H5 check_pair 同修: 下限>上限 violation + DFEDTARL 重定级 DEGRADED',
          r5.get('目标区间次序', {}).get('result') == 'violation'
          and fl['quality_status'] == 'DEGRADED'
          and rpv.fact_issues_problems(fl, 'DFEDTARL') == [],
          f"status={fl['quality_status']} probs={rpv.fact_issues_problems(fl, 'DFEDTARL')}")
    # H6 正式路径: snapshot_builder.build_snapshot(采集目录=迷你可信根)
    def _series(last, last_val, prev_val=100.0, weeks=8):
        d0 = date.fromisoformat(last) - timedelta(days=7 * weeks)
        ds, vs, d = [], [], d0
        while d <= date.fromisoformat(last):
            if d.weekday() < 5:
                ds.append(d.isoformat())
                vs.append(last_val if d.isoformat() == last else prev_val)
            d += timedelta(days=1)
        return {'dates': ds, 'values': vs}

    def _build(tag, gold_last, gold_val, gld_last, gld_val):
        # 量级取真跑值(GOLD_F 3614/基准 3515.4=+2.80%;GLD 322.87/基准 355.45=−9.17%)
        t, _snap = _mk_tree(tag, with_snapshot=False)
        raw = {'date': '20261123', 'data': {
            'GOLD_F': dict({'close': gold_val, 'date': gold_last},
                           series=_series(gold_last, gold_val, 3515.4)),
            'GLD': dict({'close': gld_val, 'date': gld_last},
                        series=_series(gld_last, gld_val, 355.45))}}
        json.dump(raw, open(os.path.join(t, 'data', 'daily',
                                         'global_20261123.json'), 'w',
                            encoding='utf-8'))
        snap = sb.build_snapshot(target_ymd='20261123',
                                 data_dir=os.path.join(t, 'data', 'daily'),
                                 out_dir=os.path.join(t, 'out'), as_of=AS,
                                 write=True, trusted_root=t)
        ga = snap.get('gate_a') or {}
        gfact = next((f for f in snap.get('facts', [])
                      if f.get('metric_id') == 'GOLD_F'), {})
        return ga, gold(snap.get('reconciliation') or []), gfact

    ga6, g6, f6 = _build('gold_unlike', '2026-11-23', 3614.0, '2026-11-20', 322.87)
    check('§H6 正式路径(真跑形态): build_snapshot Gate A 状态合法(非None)+'
          'illegal_quality 空+金双载体 insufficient+GOLD_F PASS',
          ga6.get('status') in ('PASS', 'DEGRADED', 'FAIL')
          and not ga6.get('illegal_quality')
          and g6.get('result') == 'insufficient'
          and f6.get('quality_status') == 'PASS',
          f"status={ga6.get('status')} illegal={ga6.get('illegal_quality')} "
          f"gold={g6.get('result')} GOLD_F={f6.get('quality_status')}")
    ga7, g7, f7 = _build('gold_like', '2026-11-20', 3614.0, '2026-11-20', 322.87)
    check('§H7 正式路径(同窗反向): Gate A 状态合法+illegal_quality 空+'
          'violation+GOLD_F DEGRADED(基线此处=None: 整份快照非法)',
          ga7.get('status') in ('PASS', 'DEGRADED', 'FAIL')
          and not ga7.get('illegal_quality')
          and g7.get('result') == 'violation'
          and f7.get('quality_status') == 'DEGRADED',
          f"status={ga7.get('status')} illegal={ga7.get('illegal_quality')} "
          f"gold={g7.get('result')} GOLD_F={f7.get('quality_status')}")


# ═══ §I 真跑实中②: 东京CPI发布节奏推定规则(官方实录校正) ═══
# 官方实录(总务省統計局「消費者物価指数(CPI) 結果」页 https://www.stat.go.jp/
# data/cpi/1.html ,2026-11-23 取): 東京都区部 2026年10月分(中旬速報値)
# 〔2026年10月30日公表〕/2026年6月分(中旬速報値)〔2026年6月26日公表〕;
# 全国 2026年10月分〔2026年11月20日公表〕。速报值当月末发布、领先全国口径
# 约三周。
TOKYO_CPI_OFFICIAL = {'2026-10': '2026-10-30', '2026-06': '2026-06-26'}
NATIONAL_CPI_OFFICIAL = {'2026-10': '2026-11-20'}


def sec_i():
    """真跑实中(2026-11-23 T3 判断席备稿): 点值格 JP_CPI_TOKYO_YOY「最新
    一期」取 2026-09(2.69,推定发布 2026-10-25),而同序列月道路径含 2026-10
    (2.73)——两面不一致。基线 RELEASE_RULES 把东京排在「次月下旬(月末
    +25天)」: 比官方实录晚约一个月,且晚于全国口径(+20天)——与引擎自述
    「东京速报领先全国口径发布」相反。后果: ①已发布读数被判锚前不可见
    (格缺最新月);②随格披露的公布日期错约一个月(T3 原问点名「各数据
    的公布时间」);③历史截止视图规则②误剔最新月。"""
    print('═══ §I 真跑实中②: 东京CPI发布节奏推定规则(官方实录校正) ═══')
    pub_oct, rule = rmp._publish_date('JP_CPI_TOKYO_YOY', 'monthly',
                                      '2026-10-01')
    check('§I1 规则校正: 东京 2026-10 观测推定发布日=2026-10-30(基线 '
          '2026-11-25 次月下旬),规则文本=当月末发布',
          pub_oct == '2026-10-30' and '次月下旬' not in (rule or '')
          and '当月末' in (rule or ''),
          f'pub={pub_oct} rule={rule}')
    est = {ym: rmp._publish_date('JP_CPI_TOKYO_YOY', 'monthly',
                                 ym + '-01')[0]
           for ym in TOKYO_CPI_OFFICIAL}
    nat = {ym: rmp._publish_date('JP_CPI_YOY', 'monthly', ym + '-01')[0]
           for ym in NATIONAL_CPI_OFFICIAL}
    check('§I2 官方实录锚: 推定发布日不早于实录(10月分=2026-10-30 逐日'
          '相符;6月分推定 06-29≥实录 06-26=保守),且东京速报早于全国口径'
          '(全国 10月分推定 11-20=实录)',
          est.get('2026-10') == TOKYO_CPI_OFFICIAL['2026-10']
          and est.get('2026-06', '') >= TOKYO_CPI_OFFICIAL['2026-06']
          and all(est[y] < nat[y] for y in est if y in nat)
          and nat.get('2026-10') == NATIONAL_CPI_OFFICIAL['2026-10'],
          f'est={est} nat={nat}')

    def _visible(obs, as_of):
        p, _b = rmp._visible_publish('JP_CPI_TOKYO_YOY', 'monthly', obs)
        return bool(p) and p <= as_of
    check('§I3 可见性边界: 10月分 10-29 不可见/10-30 可见;11月分(推定 '
          '11-29)于研究截止 11-23 不可见',
          not _visible('2026-10-01', '2026-10-29')
          and _visible('2026-10-01', '2026-10-30')
          and not _visible('2026-11-01', '2026-11-23')
          and _visible('2026-11-01', '2026-11-29'),
          f"oct29={_visible('2026-10-01', '2026-10-29')} "
          f"nov23={_visible('2026-11-01', '2026-11-23')}")
    # I4 历史截止视图规则②(提交的 11 月冻结快照内的真实东京序列)
    sr = json.load(open(SNAP_SRC, encoding='utf-8'))['series_store'][
        'JP_CPI_TOKYO_YOY']
    tdates = [str(x)[:10] for x in sr.get('dates') or []]
    tvals = sr.get('values') or []
    last = {}
    for a in ('2026-10-29', '2026-10-30', CUT_AUG):
        _d, _v, inf = eg.gate_series('JP_CPI_TOKYO_YOY', 'monthly', tdates,
                                     tvals, a)
        last[a] = (inf.get('last_eligible'),
                   (inf.get('first_dropped') or {}).get('reason'),
                   (inf.get('first_dropped') or {}).get('publish'))
    check('§I4 历史截止视图规则②(真实序列): 截止 10-29 末合规=09 月观测/'
          '10-30=10 月观测(基线仍 09 月: 推定 11-25 误剔);截止 08-21 末合规'
          '=07 月观测(基线 06 月: 07 月观测推定 08-25 被误剔)',
          '2026-10-01' in tdates
          and last['2026-10-29'][0] == '2026-09-01'
          and last['2026-10-30'][0] == '2026-10-01'
          and last[CUT_AUG][0] == '2026-07-01'
          and last[CUT_AUG][1] == 'late_publication',
          f'last={last}')
    # I5 真实计划点值格: T3 原问×冻结快照(as_of 11-22)
    _t, rep, _md, _seen = _offline_plan('tokyo', Q_T3)
    allc = ((rep.get('research_plan') or {}).get('point_values') or {}
            ).get('cells') or []
    cells = [c for c in allc if c.get('metric_id') == 'JP_CPI_TOKYO_YOY']
    v_new = ((cells[0].get('anchors') or {}).get('最新一期') or {}) \
        if cells else {}

    def _latest(mid):
        return next((((c.get('anchors') or {}).get('最新一期') or {})
                     for c in allc if c.get('metric_id') == mid), {})
    check('§I5 真实计划点值格(T3 原问×冻结快照 as_of 11-22): 东京「最新一期」'
          '=2026-10 观测 2.73/公布 2026-10-30(基线 2026-09 观测 2.69/'
          '公布 2026-10-25)',
          len(cells) == 1 and v_new.get('status') == 'ok'
          and v_new.get('observation_date') == '2026-10-01'
          and v_new.get('value') == 2.73
          and v_new.get('publication_date') == '2026-10-30',
          f'cell={v_new}')
    jp_n, ea = _latest('JP_CPI_YOY'), _latest('EA_HICP_YOY')
    check('§I6 相邻口径不受影响: 全国 CPI「最新一期」仍=2026-10 观测/'
          '公布 11-20(=官方实录),HICP 仍=2026-10 观测/公布 11-16;全网格'
          '公布日>锚日的格=0',
          jp_n.get('observation_date') == '2026-10-01'
          and jp_n.get('publication_date') == '2026-11-20'
          and ea.get('observation_date') == '2026-10-01'
          and ea.get('publication_date') == '2026-11-16'
          and all(x.get('publication_date', '') <= x.get('as_of', '')
                  for c in allc
                  for x in (c.get('anchors') or {}).values()
                  if x.get('status') == 'ok'),
          f"jp={ {k: jp_n.get(k) for k in ('observation_date', 'publication_date')} } "
          f"ea={ {k: ea.get(k) for k in ('observation_date', 'publication_date')} }")


# ═══ §J 真跑验收发现的渲染缺陷(正式入口四问验收运行+独立席范围外观察) ═══
_LEGACY_ANCHOR_LINE = ('- 口径: 三个对照时点=日历点锚(截止日−12月/−3月/最新一期);'
                       '「随后3、6、12个月」=事件后偏移(转折/类比基准日+N月)'
                       '——两类时间含义不同,分记不混同')
_SR0 = {'verdict': None, 'verdicts_n': 0}


def _map_head(rep, root):
    """计划回执→读者报告全文(无研判档形态=plan 段渲染;只读)."""
    return rmp.render_map_report(rep, None, _SR0, root=root)


def _one_line(mm, prefix):
    ls = [l for l in mm.splitlines() if l.startswith(prefix)]
    return ls[0] if len(ls) == 1 else ''


def sec_j():
    print('§J 真跑验收发现的渲染缺陷(请求月末误标研究截止日/对照时点标签/'
          '政策路径净变动)')
    # J1 NEW30 夹紧形: 请求月末只称请求研究时点,研究截止日=实际覆盖日
    t, rep, _md, _ = _offline_plan('j_new30', Q_NEW30)
    rp = rep.get('research_plan') or {}
    ad = rp.get('as_of_declared') or {}
    mm = _map_head(rep, t)
    bl = _one_line(mm, '- 研究时点口径')
    check('§J1a NEW30(夹紧形)读者报告「研究时点口径」行: 请求月末 2026-11-30 只称'
          '请求研究时点,研究截止日=实际覆盖日 2026-11-22,绑定句点名截止日(基线: '
          '同一行写「按月末时点化为研究截止日 2026-11-30…绑定该时点」,与上下两行'
          '的研究截止日相抵)',
          len([l for l in mm.splitlines() if l.startswith('- 研究时点口径')]) == 1
          and '研究截止日 2026-11-30' not in bl
          and '请求研究时点 2026-11-30' in bl
          and '2026-11-22' in bl
          and '绑定研究截止日 2026-11-22' in bl, bl[:260])
    head = mm.splitlines()[:12]
    # 「研究截止日」标签紧邻 2026-11-30(=把请求月末写成研究截止日);
    # 披露行「请求 2026-11-30 | … | 研究截止日=2026-11-22」不在此列
    _mis = [l for l in head
            if re.search(r'研究截止日[=:：\s]*=?\s*2026-11-30', l)]
    check('§J1b 同页头部任何一行不得把 2026-11-30 写成研究截止日;头部无 '
          'None;计划面 as_of_declared.basis 同口径(席位信封/报告/归档同读'
          '该字段)',
          not _mis
          and '研究截止日 2026-11-30' not in str(ad.get('basis'))
          and not any('None' in l for l in head)
          and ad.get('as_of') == '2026-11-22'
          and ad.get('requested_month_end') == '2026-11-30',
          (str(_mis[:1]) + ' | ' + str(ad.get('basis'))[:200]))
    anchors = [(a.get('label'), a.get('months_before')) for a in
               (rp.get('point_anchors') or [])]
    al = _one_line(mm, '- 口径: ')
    check('§J2a 两锚问句(NEW30: 6个月前/最新一期)「口径」行按实际锚渲染——基线'
          '写「三个对照时点=…−12月/−3月/最新一期」(本问无 12 个月前/3 个月前锚)',
          [a[0] for a in anchors] == ['6个月前', '最新一期']
          and al.startswith('- 口径: 两个对照时点=日历点锚(截止日−6个月/最新一期);')
          and '三个对照时点' not in al and '−12月' not in al, al[:200])
    shutil.rmtree(t, ignore_errors=True)
    # J1c 显式时点问(未夹紧): 绑定句点名研究截止日
    t, rep, _md, _ = _offline_plan('j_aug', Q_AUG)
    bl = _one_line(_map_head(rep, t), '- 研究时点口径')
    check('§J1c 显式时点问(AUG,未夹紧): 研究时点口径行=问题声明研究时点 '
          '2026-08-21,绑定句点名研究截止日 2026-08-21(计划/取数/渲染同一截止日)',
          ('问题声明研究时点 2026-08-21' in bl
           and '绑定研究截止日 2026-08-21' in bl), bl[:200])
    shutil.rmtree(t, ignore_errors=True)
    # J1d 显式时点标记晚于覆盖日(非月末形): 同一夹紧规则,披露按请求时点
    # (基线: 请求月末缺席→读者报告/报告渲「请求 None」)
    Q_DEC = '以 2026-12-15 为研究时点，日本和欧元区最近六个月的通胀与政策环境'
    t, rep, md_d, _ = _offline_plan('j_dec', Q_DEC)
    rp_d = rep.get('research_plan') or {}
    ad_d = rp_d.get('as_of_declared') or {}
    mm_d = _map_head(rep, t)
    _dl = _one_line(mm_d, '- 请求研究时点/实际覆盖日: ')
    check('§J1d 显式时点标记晚于覆盖日(2026-12-15>2026-11-22): 研究截止日='
          '实际覆盖日 2026-11-22,读者报告披露行=「请求研究时点/实际覆盖日: '
          '请求 2026-12-15 | 快照实际覆盖 2026-11-22 | 研究截止日=2026-11-22」'
          '(基线渲「请求 None」),报告同步披露且无 None',
          rp_d.get('cutoff') == '2026-11-22'
          and ad_d.get('clamped_to_coverage') is True
          and ad_d.get('requested_month_end') is None
          and ad_d.get('requested_as_of') == '2026-12-15'
          and _dl.startswith('- 请求研究时点/实际覆盖日: 请求 2026-12-15'
                             ' | 快照实际覆盖 2026-11-22 | 研究截止日=2026-11-22')
          and '- 请求月末/实际覆盖日' not in mm_d
          and not any('None' in l for l in mm_d.splitlines()[:12])
          and '- 请求研究时点 2026-12-15 晚于快照实际覆盖日 2026-11-22'
          '(请求时点未到/数据未到)' in md_d
          and '请求 None' not in md_d
          and '请求时点未到/数据未到' in json.dumps(rp_d, ensure_ascii=False),
          f"cutoff={rp_d.get('cutoff')} line={(_dl or _one_line(mm_d, '- 请求月末/实际覆盖日'))[:120]} "
          f"ad={ {k: ad_d.get(k) for k in ('requested_month_end', 'requested_as_of', 'clamped_to_coverage')} }")
    shutil.rmtree(t, ignore_errors=True)
    # J2b 三标准锚问句(A): 「口径」行=旧文本逐字;两锚问句 B 同步
    t, rep, _md, _ = _offline_plan('j_a', Q_A)
    al_a = _one_line(_map_head(rep, t), '- 口径: ')
    shutil.rmtree(t, ignore_errors=True)
    t, rep, _md, _ = _offline_plan('j_b', Q_B)
    al_b = _one_line(_map_head(rep, t), '- 口径: ')
    rj2 = json.loads(json.dumps(rep))
    (rj2.setdefault('run', {})).pop('evidence_gate', None)
    legacy_b = rmp.render_map_report(rj2, None, _SR0, root=t)
    shutil.rmtree(t, ignore_errors=True)
    check('§J2b 三标准锚问句(A)「口径」行=旧文本逐字;两锚问句 B=「两个对照时点'
          '=日历点锚(截止日−3个月/最新一期)」;run 无 evidence_gate 的旧档形态重渲'
          '=旧文本(旧档字节不漂移,§A6a 全文比对同证)',
          al_a == _LEGACY_ANCHOR_LINE
          and al_b.startswith('- 口径: 两个对照时点=日历点锚(截止日−3个月/最新一期);')
          and _one_line(legacy_b, '- 口径: ') == _LEGACY_ANCHOR_LINE,
          f"A={al_a[:80]} B={al_b[:80]}")
    # J3 政策一年窗路径: 净变动=变动点之和(窗启时在值→窗末)
    d3 = ['2025-06-11', '2026-06-17', '2026-09-16']
    v3 = [2.0, 2.25, 2.5]
    wp = rmp._policy_window_path(d3, v3, '2026-11-22', metric_id='ECB_DFR',
                                 carry_start=True)
    wp0 = rmp._policy_window_path(d3, v3, '2026-11-22', metric_id='ECB_DFR')
    check('§J3a 阶梯序列(决议日观测)一年窗: 净变动=窗启时在值→窗末=变动点之和'
          '(+50bp,2.0→2.5);基线口径(窗内首观测→窗末=+25bp)与同列两个 +25bp '
          '变动点不闭合;无证据口径(旧档)口径不变=+25bp',
          wp.get('net_bp') == 50 == sum(e['delta_bp'] for e in wp['events'])
          and wp.get('window_start_value') == 2.0
          and wp.get('window_start_observation') == '2025-06-11'
          and wp0.get('net_bp') == 25
          and wp0.get('window_start_value') == 2.25,
          f"carry={ {k: wp.get(k) for k in ('net_bp', 'window_start_value')} } "
          f"legacy={ {k: wp0.get(k) for k in ('net_bp', 'window_start_value')} }")
    t, rep, _md, _ = _offline_plan('j_t3', Q_T3)
    cells = ((rep.get('research_plan') or {}).get('point_values') or {}
             ).get('cells') or []
    wps = {c['metric_id']: c['policy_window_path'] for c in cells
           if c.get('policy_window_path')}
    sums = {k: sum(e['delta_bp'] for e in (w.get('events') or []))
            for k, w in wps.items()}
    check('§J3b 真实计划(T3 原问×冻结快照): 每条政策一年窗路径 净变动==Σ变动点'
          '(欧央行两序列两次各 +25bp→+50bp,窗启时在值 2.0/2.15);基线: 欧央行净 '
          '+25bp 对两个 +25bp 变动点、日本月均 +67bp 对六变动点之和 75',
          bool(wps) and all(wps[k].get('net_bp') == sums[k] for k in wps)
          and wps.get('ECB_DFR', {}).get('net_bp') == 50
          and wps.get('ECB_MRO', {}).get('net_bp') == 50
          and wps['ECB_DFR'].get('window_start_value') == 2.0
          and wps['ECB_MRO'].get('window_start_value') == 2.15
          and all('变动点之和' in str(w.get('note')) for w in wps.values()),
          f"net={ {k: w.get('net_bp') for k, w in wps.items()} } sums={sums}")
    mm = _map_head(rep, t)
    pl = [l for l in mm.splitlines() if l.startswith('- **政策一年窗路径**')]
    check('§J3c 读者报告政策一年窗路径行: 「净变动 **+50bp**(2.0→2.5;窗启时'
          '在值取 <观测日> 观测)」与变动点逐点闭合,窗启时在值的来源观测日'
          '可核,口径注记写明=变动点之和',
          any(l.startswith('- **政策一年窗路径** 欧央行存款便利利率: ')
              and '净变动 **+50bp**(2.0→2.5;窗启时在值取 ' in l
              and ' 观测)。' in l and '变动点之和' in l
              for l in pl), (pl[0][:300] if pl else 'no policy path line'))
    shutil.rmtree(t, ignore_errors=True)
    # J4 读者页数据门总体状态行(基线: 信封/report.md 载 gate_a=DEGRADED,
    # 读者页零披露——T3 轮一独立审查 #15)
    t, rep, _md, _ = _offline_plan('j_ga', Q_T3)
    mm = _map_head(rep, t)
    _sid = (((rep.get('layers') or {}).get('L1_事实层') or {})
            or {}).get('snapshot_id')
    with open(os.path.join(t, 'data', 'daily', f'{_sid}.json'),
              encoding='utf-8') as _f:
        _gax = json.load(_f).get('gate_a') or {}

    def _lx(_k):
        return '、'.join(_gax.get(_k) or []) or '无'
    _exp = (f"- 数据门(Gate A,源快照采集面): {_gax.get('status')}——核心缺口 "
            f"{_lx('core_missing')} | 核心失败 {_lx('core_fail')} | 非核心失败 "
            f"{_lx('noncore_fail')} | 非核心缺席 {_lx('noncore_missing')} | "
            f"非核心降级 {_lx('noncore_degraded')}——缺席/降级数据不得进入研究"
            "结论;逐指标注记见快照 gate_a.noncore_missing_detail,信封步状态"
            "见步骤台账")
    _gl = _one_line(mm, '- 数据门(Gate A')
    _mml = mm.splitlines()
    _pos_ga = next((i for i, l in enumerate(_mml)
                    if l.startswith('- 数据门(Gate A')), None)
    _pos_ev = next((i for i, l in enumerate(_mml)
                    if l.startswith('- 证据口径(r32)')), None)
    check('§J4a 真实计划(T3×冻结快照)读者报告头部: 「数据门(Gate A,源快照'
          '采集面)」一行=运行快照 gate_a 的状态与五张名单(DEGRADED;非核心'
          '缺席七项含 JP_CPI_TOKYO_YOY;非核心降级八项含 ECB_DFR/ECB_MRO),'
          '紧随证据口径行且全页仅一行(基线: 读者页无数据门状态行)',
          _gl == _exp
          and _gax.get('status') == 'DEGRADED'
          and len(_gax.get('noncore_missing') or []) == 7
          and len(_gax.get('noncore_degraded') or []) == 8
          and 'ECB_DFR' in _gl and 'ECB_MRO' in _gl
          and 'JP_CPI_TOKYO_YOY' in _gl
          and _pos_ev is not None and _pos_ga == _pos_ev + 1,
          _gl[:300])
    rj_noga = json.loads(json.dumps(rep))
    (rj_noga.setdefault('run', {})).pop('evidence_gate', None)
    _leg = rmp.render_map_report(rj_noga, None, _SR0, root=t)
    rj_miss = json.loads(json.dumps(rep))
    rj_miss['layers']['L1_事实层']['snapshot_id'] = 'research_snapshot_absent'
    _mis = _one_line(rmp.render_map_report(rj_miss, None, _SR0, root=t),
                     '- 数据门(Gate A')
    check('§J4b 旧档(无 evidence_gate)重渲无数据门状态行(旧档字节不漂移);'
          '运行快照不在场=如实缺席注记(不跨快照取数)',
          '- 数据门(Gate A' not in _leg
          and _mis.startswith('- 数据门(Gate A): 运行快照文件不在场(')
          and '(总体状态不跨快照取数,如实缺席)' in _mis, _mis[:200])
    # J5 读者报告分工行(基线: 裁决缺席仍写「经独立语义审查」,与同页审查面
    # 「独立席位待裁」矛盾——B 轮一独立审查 NIT)
    _div = _one_line(mm, '- 分工: ')
    check('§J5a 真实计划(T3×冻结快照)裁决缺席: 分工行如实写「独立语义审查待裁」(基线: 裁决缺席即写「经独立语义审查」)',
          _div.endswith('独立语义审查待裁)') and '经独立语义审查' not in _div,
          _div[-60:])
    _mm_rv = rmp.render_map_report(rep, None, {'verdict': 'UPHELD', 'verdicts_n': 1},
                                   root=t)
    _div_rv = _one_line(_mm_rv, '- 分工: ')
    _div_leg = _one_line(_leg, '- 分工: ')
    check('§J5b 裁决在场(席位已裁)=「经独立语义审查」且审查面同页一致;'
          '旧档(无 evidence_gate)裁决缺席仍为原文(旧档字节不漂移)',
          _div_rv.endswith('经独立语义审查)')
          and '- 席位已裁: UPHELD(裁决链 1 档)' in _mm_rv
          and _div_leg.endswith('经独立语义审查)')
          and '- 独立席位待裁' in _leg,
          _div_rv[-40:] + ' | ' + _div_leg[-40:])
    shutil.rmtree(t, ignore_errors=True)


# ═══ §K 正式验收独立席范围外观察(工单A 第1轮 EO-1): LPR 推定发布日早于实际公布日 ═══
LPR_MONTHLY_START = '2019-09-20'      # 月度 LPR 起点(观测日=公布日);此前为逐日报价


def sec_k():
    """正式验收(工单A 独立审查第1轮,引擎面规则观察 EO-1): CN_LPR_1Y 的推定
    发布规则=「观测月末−11天」,只在 31 天月份等于 20 日;该序列按实际公布日
    记观测日(遇非工作日顺延: 2022-02-21、2022-03-21、2022-08-22),故推定日
    比实际公布日早 1–4 天(2019-09 起 87 点中 49 点)。发布日随格披露与 REP
    同步面标签因此写错公布日;转折候选面窗端点月只按推定日过滤——截止日
    落在推定日与公布日之间时,尚未公布的读数入窗(任务1 规则②: 晚发布
    不入;取数入口先剔晚观测,不受影响)。修正两处: 规则改为「观测日=发布
    日,当日可见」(与 CN_OMO_7D 同形);转折候选面补「观测日≤截止日」一道
    (规则面无关的纵深守卫)。日历实录(RC-CN-LPR-*)仍优先。"""
    print('═══ §K 正式验收席观察: LPR 推定发布日早于实际公布日(规则②) ═══')
    kind, days, rule = rmp.RELEASE_RULES['CN_LPR_1Y']
    check('§K1 规则形态: CN_LPR_1Y 推定发布日=观测日(序列按实际公布日记载;'
          '基线「月末−11天」仅 31 天月份=20 日)',
          kind == 'daily' and days == 0 and '观测日=发布日' in (rule or ''),
          'rule=%r' % (rmp.RELEASE_RULES['CN_LPR_1Y'],))
    sr = json.load(open(SNAP_SRC, encoding='utf-8'))['series_store'][
        'CN_LPR_1Y']
    ldates = [str(x)[:10] for x in sr.get('dates') or []]
    lvals = sr.get('values') or []
    monthly = [d for d in ldates if d >= LPR_MONTHLY_START]
    early = [d for d in monthly
             if rmp._publish_date('CN_LPR_1Y', 'monthly', d)[0] != d]
    check('§K2 真实序列逐点: 2019-09 起 87 个月度观测推定发布日全部=实际公布日'
          '(基线 49 点早 1–4 天,如 2022-06-20→06-19、2021-02-20→02-17)',
          len(monthly) == 87 and not early,
          f'early={len(early)} {early[:6]}')
    vis = {d: rmp._visible_publish('CN_LPR_1Y', 'monthly', d)[0]
           for d in ('2022-06-20', '2022-02-21', '2022-08-22', '2026-10-20')}
    check('§K3 规划器可见发布日(REP 同步面同入口): 2022-06 观测=06-20(基线 '
          '06-19)/02-21(基线 02-17)/08-22(基线 08-20)/2026-10 观测=10-20',
          vis == {'2022-06-20': '2022-06-20', '2022-02-21': '2022-02-21',
                  '2022-08-22': '2022-08-22', '2026-10-20': '2026-10-20'},
          f'vis={vis}')
    last = {}
    for a in ('2022-06-19', '2022-06-20'):
        _d, _v, inf = eg.gate_series('CN_LPR_1Y', 'monthly', ldates, lvals, a)
        fd = inf.get('first_dropped') or {}
        last[a] = (inf.get('last_eligible'), fd.get('date'), fd.get('reason'))
    check('§K4 取数入口历史截止视图(真实序列,回归): 截止 2022-06-19 末合规='
          '05-20 观测、首个剔除=06-20 观测(晚观测;入口先剔观测日,规则修正'
          '前后同判);截止 06-20 末合规=06-20',
          last == {'2022-06-19': ('2022-05-20', '2022-06-20',
                                  'late_observation'),
                   '2022-06-20': ('2022-06-20', '2022-07-20',
                                  'late_observation')},
          f'last={last}')

    # 转折候选面(turning_candidates): 窗端点月原只按「推定发布日≤截止日」
    # 过滤、无「观测日≤截止日」一道 → 截止 2020-04-19(周日)时 04-20 公布
    # 的 4 月 LPR(1Y 4.15→3.85)被推定 04-19 放行入窗,并成为最大三月变化
    # 候选(基线实测 to_date=2020-04-20 > 截止日)。
    snap = json.load(open(SNAP_SRC, encoding='utf-8'))
    lplan = {'cutoff': '2020-04-19',
             'regions': {'CN': {'dimensions': {'policy': [
                 {'metric_id': 'CN_LPR_1Y', 'display_name': 'LPR 1Y'}]}}}}

    def _lpr_cand():
        out = rmp.turning_candidates(lplan, snap, ROOT)
        return [c for c in out['candidates']
                if c['metric_id'] == 'CN_LPR_1Y']
    cand = _lpr_cand()
    check('§K5 转折候选面(规则修正后): 截止 2020-04-19 → CN_LPR_1Y 候选窗'
          '端点月 ≤ 截止日(基线把 04-20 才公布的 4 月读数入窗: '
          '2020-01 4.15→2020-04 3.85)',
          len(cand) == 1 and cand[0]['to_date'] <= lplan['cutoff']
          and cand[0]['to_date'] != '2020-04-20',
          f'{[(c["from_ym"], c["to_ym"], c["to_date"], c["value_before"], c["value_after"], c["delta"]) for c in cand]}')
    keep = rmp.RELEASE_RULES.get('CN_LPR_1Y')
    try:
        rmp.RELEASE_RULES['CN_LPR_1Y'] = (
            'monthly', -11,
            'LPR 每月20日09:00公布(观测日=发布日;月末−11天,节假日顺延;'
            'Audit-R29 官方时刻)')
        cand2 = _lpr_cand()
    finally:
        rmp.RELEASE_RULES['CN_LPR_1Y'] = keep
    check('§K6 转折候选面纵深守卫(规则面无关): 把推定规则临时换回「月末−11天」'
          '(推定日早于观测日的任意序列同形),窗端点月仍须观测日≤截止日',
          len(cand2) == 1 and cand2[0]['to_date'] <= lplan['cutoff']
          and cand2[0]['to_date'] == (cand[0]['to_date'] if cand else None),
          f'{[(c["to_ym"], c["to_date"]) for c in cand2]}')
    cal = {d: rmp._visible_publish('CN_LPR_1Y', 'monthly', d)
           for d in ('2025-11-20', '2026-11-20')}
    check('§K7 日历实录仍优先(回归): 2025-11/2026-11 观测发布日=当月 20 日且'
          '口径注明日历条目(RC-CN-LPR-2025M11/2026M11)',
          all(v[0] == k and 'RC-CN-LPR-' in (v[1] or '')
              for k, v in cal.items()),
          f'cal={ {k: (v[0], (v[1] or "")[:40]) for k, v in cal.items()} }')


# ═══ §L 裁决后交付状态面(正式验收发现: 已裁交付件仍写「待裁」) ═══
def _status_line(text):
    for ln in text.split('\n'):
        if ln.startswith('- 分工: '):
            return ln
    return ''


def _body_edit(text):
    """受审正文改一字: 审查节之前、分工行之外的最后一个非空行尾加空格。"""
    seg, split, tail = text.partition('\n## 语义审查')
    lines = seg.split('\n')
    idx = [i for i, ln in enumerate(lines)
           if ln.strip() and not ln.startswith('- 分工: ')]
    lines[idx[-1]] += ' '
    return '\n'.join(lines) + split + tail


# 包装器: 以当前代码跑 research-one, 但渲染器在审查节前多出一行正文
# (=「代码已前进」的真漂移模拟;受审输入不变)
_DRIFT_CLI = r'''
import sys
sys.path.insert(0, __ROOT__)
import ia_cli
import research_map_planner as rmp
_orig = rmp.render_map_report


def _drift(*a, **k):
    head, sep, tail = _orig(*a, **k).partition('\n## 语义审查')
    return head + '\n\n(渲染器前进: 本行为当前代码新增)\n' + sep + tail


rmp.render_map_report = _drift
sys.argv = ['ia_cli.py'] + sys.argv[1:]
sys.exit(ia_cli.main())
'''

# 包装器: 同一份代码,只把「当前代码 HEAD」声明为指定印章(模拟运行目录在
# 执行印章下运行、之后在另一印章下归档/重放)
_HEAD_CLI = r'''
import sys
HEAD = sys.argv[1]
sys.path.insert(0, __ROOT__)
import ia_cli
import research_orchestrator as ro

ro._git_state = lambda root: (HEAD, 'gate_head_wrapper', False)
sys.argv = ['ia_cli.py'] + sys.argv[2:]
sys.exit(ia_cli.main())
'''


def sec_l():
    """正式验收发现(工单 T3/A 在 36499bb 裁决 UPHELD 后归档): report 段
    「渲染器漂移」冻结分支恒触发——分工行尾审查状态短语随裁决在场与否
    翻转(Audit-R32 真跑修复引入)而位于内容段之内,已裁内容段≠当前装配
    →受审正文按原字节交付→首页仍写「独立语义审查待裁」、审查尾仍写
    「独立席位待裁」。修复: 在场地图与当前装配仅差该短语=状态面等价
    (裁决绑定有效)→照常重写翻新状态面;裁决新鲜判定/归档核对/重放
    核对同口径;正文差异照旧冻结(真漂移)/过期(改版)/拒绝(单改)。"""
    print('═══ §L 裁决后交付状态面: 仅差审查状态短语=状态面等价 ═══')
    rd, _src = fresh_pkg_rd('ps', 'session_NEW30')
    # 夹具同 §C4(复本报告补 r32 证据口径: r32 报告头按裁决在场与否渲染)
    _p = os.path.join(rd, 'report.json')
    _rj = json.load(open(_p, encoding='utf-8'))
    _rj['run']['evidence_gate'] = {
        'discipline': 'r32', 'as_of': '2026-11-22',
        'source_snapshot_id': 'research_snapshot_20261122_v2',
        'source_target_date': '2026-11-22', 'historical_view': False,
        'counts': {'facts_kept': 105, 'facts_rebuilt': 0,
                   'facts_dropped': 0, 'facts_excluded_version': 0,
                   'series_observations_dropped': 0,
                   'series_observations_version_unavailable': 0,
                   'series_excluded': 0, 'series_n': 90},
        'series': {}}
    _rj['run']['evidence_asof'] = '2026-11-22'
    with open(_p, 'w', encoding='utf-8') as f:
        json.dump(_rj, f, ensure_ascii=False, indent=2, default=str)
    rewrite_head(rd, WORKTREE_HEAD)
    T = build_tree('ps')
    mpath = os.path.join(rd, 'MAP_REPORT.md')
    rc0, d0 = cli('report', rd, T)
    dd0 = d0.get('data') or {}
    t0 = open(mpath, encoding='utf-8').read()
    check('§L1 前置: 裁决缺席 report rc≠0,当前装配落盘——分工行尾'
          '「独立语义审查待裁)」+审查尾「独立席位待裁」',
          rc0 != 0 and dd0.get('deliverable') is False
          and _status_line(t0).endswith('独立语义审查待裁)')
          and '- 独立席位待裁' in t0,
          f"rc0={rc0} div={_status_line(t0)[-24:]!r}")
    sha0 = aj.map_report_content_sha(rd)
    vp = aj.record_semantic_verdict(T, rd, 'UPHELD',
                                    reviewer='r32gate-status席',
                                    notes='R32 正式验收: 裁决后交付状态面')
    vd = json.load(open(vp, encoding='utf-8'))
    rc1, d1 = cli('report', rd, T)
    dd1 = d1.get('data') or {}
    t1 = open(mpath, encoding='utf-8').read()
    w1 = [str(w) for w in (d1.get('warnings') or [])]
    anchor1 = open(os.path.join(rd, 'MAP_REPORT.sha256'),
                   encoding='utf-8').read().split(' ', 1)[0]
    s0, s1 = t0.split('\n## 语义审查')[0], t1.split('\n## 语义审查')[0]
    dlines = [(a, b) for a, b in zip(s0.split('\n'), s1.split('\n'))
              if a != b]
    check('§L2 裁决 UPHELD 后 report: rc=0 可交付;分工行尾'
          '「经独立语义审查)」+审查尾「席位已裁: UPHELD(裁决链 1 档)」;'
          '全文无「待裁」;无「渲染器漂移」警告(renderer_drift=False,'
          'status_refreshed=True)',
          rc1 == 0 and dd1.get('deliverable') is True
          and _status_line(t1).endswith('经独立语义审查)')
          and '- 席位已裁: UPHELD(裁决链 1 档)' in t1
          and '待裁' not in t1
          and dd1.get('map_renderer_drift') is False
          and dd1.get('map_status_refreshed') is True
          and not any('渲染器漂移' in w for w in w1),
          f"rc1={rc1} deliv={dd1.get('deliverable')} "
          f"drift={dd1.get('map_renderer_drift')} "
          f"refresh={dd1.get('map_status_refreshed')} "
          f"pending={t1.count('待裁')} w={[x[:50] for x in w1]}")
    sha1 = aj.map_report_content_sha(rd)
    check('§L3 受审内容未被改写: 裁决前后内容段逐行对比恰 1 行不同'
          '(=分工行状态短语),其余逐字节相同;旁挂锚=新全文 sha256;裁决'
          '仍新鲜(fresh=True);裁决档绑定=受审时(待裁形)内容段摘要',
          len(s0.split('\n')) == len(s1.split('\n'))
          and len(dlines) == 1 and dlines[0][0].startswith('- 分工: ')
          and anchor1 == hashlib.sha256(t1.encode('utf-8')).hexdigest()
          and (dd1.get('review') or {}).get('fresh') is True
          and vd.get('map_report_sha256') == sha0
          and sha1 == hashlib.sha256(s1.encode('utf-8')).hexdigest()
          and sha1 != sha0,
          f'dlines={len(dlines)} fresh={(dd1.get("review") or {}).get("fresh")}')
    b1 = open(mpath, 'rb').read()
    rc1b, d1b = cli('report', rd, T)
    dd1b = d1b.get('data') or {}
    check('§L4 重复 report 幂等: rc=0,字节不变,不再记状态面翻新',
          rc1b == 0 and open(mpath, 'rb').read() == b1
          and dd1b.get('map_status_refreshed') is False
          and dd1b.get('deliverable') is True,
          f"rc={rc1b} refresh={dd1b.get('map_status_refreshed')}")
    arc = os.path.join(TMPG, 'arc_ps')
    rc2, d2 = cli('archive', rd, T, arc=arc)
    man_p = os.path.join(arc, 'ARCHIVE_MANIFEST.json')
    man = json.load(open(man_p, encoding='utf-8')) if os.path.isfile(
        man_p) else {}
    check('§L5 归档: rc=0;清单 map_binding_status_equivalent=true/'
          'map_renderer_drift=false;归档件==运行目录件;'
          'map_report_sha256=裁决档绑定,map_content_sha256=归档内容段'
          '原字节摘要(待裁形/已裁形两摘要并存,清单注明状态面等价)',
          rc2 == 0 and man.get('map_binding_status_equivalent') is True
          and man.get('map_renderer_drift') is False
          and open(os.path.join(arc, 'MAP_REPORT.md'), 'rb').read() == b1
          and man.get('map_report_sha256') == sha0
          and man.get('map_content_sha256') == aj.map_report_content_sha(arc)
          and man.get('map_content_sha256') == sha1
          and '状态面等价' in str(man.get('correlation')),
          f"rc2={rc2} equiv={man.get('map_binding_status_equivalent')} "
          f"drift={man.get('map_renderer_drift')}")
    rc3, d3 = replay(arc, T, out=os.path.join(TMPG, 'rp_ps'))
    dd3 = d3.get('data') or {}
    ck3 = {c.get('check'): c.get('ok') for c in (dd3.get('checks') or [])
           if c.get('check')}
    check('§L6 重放: rc=0(绑定三方核对按状态面等价通过;当前代码重渲'
          '与归档件逐字节相等)',
          rc3 == 0 and ck3.get('verdict_binding_threeway') is True
          and ck3.get('map_fullfile_anchor') is True
          and dd3.get('render_mode') == 'byte_equal',
          f"rc3={rc3} mode={dd3.get('render_mode')} "
          f"failed={dd3.get('failed_checks')}")
    # ── 反例 a: 裁决后单改正文(旁挂锚未动) ──
    rda = os.path.join(TMPG, 'rd_ps_tamper')
    shutil.copytree(rd, rda)
    ta = _body_edit(t1)
    with open(os.path.join(rda, 'MAP_REPORT.md'), 'w', encoding='utf-8') as f:
        f.write(ta)
    rca, da = cli('report', rda, T)
    dda = da.get('data') or {}
    check('§L7a 裁决后单改正文(旁挂锚未动): 拒绝交付且不重写(保全'
          '证据);警告点名旁挂锚不符;不记状态面翻新',
          rca != 0 and dda.get('deliverable') is False
          and any('旁挂锚' in str(w) for w in (da.get('warnings') or []))
          and open(os.path.join(rda, 'MAP_REPORT.md'),
                   encoding='utf-8').read() == ta
          and dda.get('map_status_refreshed') is False,
          f"rc={rca} deliv={dda.get('deliverable')}")
    # ── 反例 b: 正文改版+重锚(冒充受审定稿) ──
    rdb = os.path.join(TMPG, 'rd_ps_reanchor')
    shutil.copytree(rd, rdb)
    with open(os.path.join(rdb, 'MAP_REPORT.md'), 'w', encoding='utf-8') as f:
        f.write(ta)
    with open(os.path.join(rdb, 'MAP_REPORT.sha256'), 'w',
              encoding='utf-8') as f:
        f.write(hashlib.sha256(ta.encode('utf-8')).hexdigest()
                + '  MAP_REPORT.md\n')
    rcb, db = cli('report', rdb, T)
    ddb = db.get('data') or {}
    rcb2, db2 = cli('report', rdb, T)
    check('§L7b 正文改版+重锚: 裁决过期(fresh=False)→本轮拒绝交付、不记'
          '状态面翻新;改版件被当前装配重渲覆盖(改版不得洗白);下一轮'
          '恢复可交付',
          rcb != 0 and ddb.get('deliverable') is False
          and (ddb.get('review') or {}).get('fresh') is False
          and ddb.get('map_status_refreshed') is False
          and open(os.path.join(rdb, 'MAP_REPORT.md'),
                   encoding='utf-8').read() == t1
          and rcb2 == 0 and (db2.get('data') or {}).get('deliverable')
          is True,
          f"rc={rcb} fresh={(ddb.get('review') or {}).get('fresh')} "
          f"rc2={rcb2}")
    # ── 反例 c: 渲染器真漂移(正文变)照旧冻结 ──
    wrap = os.path.join(TMPG, 'drift_cli.py')
    with open(wrap, 'w', encoding='utf-8') as f:
        f.write(_DRIFT_CLI.replace('__ROOT__', repr(ROOT)))

    def _drift_cli(stage, arc=None):
        cmd = [sys.executable, wrap, 'research-one', '--stage', stage,
               '--report-dir', rd, '--engine-root', T]
        if arc:
            cmd += ['--archive-dir', arc]
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                           timeout=900)
        try:
            return r.returncode, json.loads(r.stdout)
        except Exception:                       # noqa: BLE001
            return r.returncode, {'raw': (r.stdout + r.stderr)[-400:]}

    rcd, dd = _drift_cli('report')
    ddd = dd.get('data') or {}
    arcd = os.path.join(TMPG, 'arc_ps_drift')
    rc4, _d4 = _drift_cli('archive', arc=arcd)
    mand_p = os.path.join(arcd, 'ARCHIVE_MANIFEST.json')
    mand = json.load(open(mand_p, encoding='utf-8')) if os.path.isfile(
        mand_p) else {}
    rc5, d5 = replay(arcd, T, out=os.path.join(TMPG, 'rp_ps_drift'))
    check('§L7c 渲染器真漂移(包装器令当前代码在正文多出一行): 冻结分支'
          '照旧——report rc=0+「渲染器漂移」披露+受审字节不改写'
          '(map_renderer_drift=True,不记状态面翻新);归档 rc=0 清单 '
          'drift=true+状态面等价注记(先前已翻新的受审件);重放 rc=0',
          rcd == 0 and any('渲染器漂移' in str(w)
                           for w in (dd.get('warnings') or []))
          and open(mpath, 'rb').read() == b1
          and ddd.get('map_renderer_drift') is True
          and ddd.get('map_status_refreshed') is False
          and rc4 == 0 and mand.get('map_renderer_drift') is True
          and mand.get('map_binding_status_equivalent') is True
          and open(os.path.join(arcd, 'MAP_REPORT.md'), 'rb').read() == b1
          and rc5 == 0 and (d5.get('data') or {}).get('render_mode') \
          == 'byte_equal',
          f"rc={rcd} drift={ddd.get('map_renderer_drift')} "
          f"rc4={rc4} drift_m={mand.get('map_renderer_drift')} "
          f"rc5={rc5} mode={(d5.get('data') or {}).get('render_mode')}")
    # ── 判定函数(单元面) ──
    other = next(ln for ln in s1.split('\n')
                 if ln.strip() and not ln.startswith('- 分工: '))
    x1 = s1.replace(other, other + ',独立语义审查待裁)', 1)
    x2 = s1.replace(other, other + ',经独立语义审查)', 1)
    tb2 = _body_edit(t1)
    check('§L8 判定函数: 状态面等价只认「分工」行尾短语——裁决前后全文'
          '等价=True;正文改一字=False;状态短语出现在其他行不算状态面;'
          '绑定匹配=原字节/已裁形/待裁形三口径之一',
          aj.map_content_state_equivalent(t0, t1) is True
          and aj.map_content_state_equivalent(t1, tb2) is False
          and aj.map_content_state_equivalent(x1, x2) is False
          and aj.map_binding_matches(t1, sha0) is True
          and aj.map_binding_matches(t0, sha1) is True
          and aj.map_binding_matches(tb2, sha0) is False
          and aj.map_binding_matches(t1, None) is False
          and aj.map_binding_matches(x1, aj._sha256_text(x1)) is True,
          f"eq01={aj.map_content_state_equivalent(t0, t1)} "
          f"eq_x={aj.map_content_state_equivalent(x1, x2)}")
    # ── §L9 裁决后再交付包: 归档代码随清单落档+重放门④认归档代码 ──
    hwrap = os.path.join(TMPG, 'head_cli.py')
    with open(hwrap, 'w', encoding='utf-8') as f:
        f.write(_HEAD_CLI.replace('__ROOT__', repr(ROOT)))

    def _head_cli(head, argv):
        r = subprocess.run([sys.executable, hwrap, head] + argv, cwd=ROOT,
                           capture_output=True, text=True, timeout=900)
        try:
            return r.returncode, json.loads(r.stdout)
        except Exception:                       # noqa: BLE001
            return r.returncode, {'raw': (r.stdout + r.stderr)[-400:]}

    def _ck(d, name):
        for c in ((d.get('data') or {}).get('checks') or []):
            if c.get('check') == name:
                return c
        return {}

    def _jload(p):
        try:
            return json.load(open(p, encoding='utf-8'))
        except Exception:                       # noqa: BLE001
            return {}

    def _read(p):
        return open(p, encoding='utf-8').read() if os.path.isfile(p) else ''

    ARC2, ARC3 = 'a' * 40, 'b' * 40            # 归档印章 / 第三印章(模拟)
    arc2 = os.path.join(TMPG, 'arc_ps_redeliv')
    rc6, d6 = _head_cli(ARC2, ['research-one', '--stage', 'archive',
                               '--report-dir', rd, '--engine-root', T,
                               '--archive-dir', arc2])
    man2_p = os.path.join(arc2, 'ARCHIVE_MANIFEST.json')
    man2 = json.load(open(man2_p, encoding='utf-8')) if os.path.isfile(
        man2_p) else {}
    check('§L9a 归档代码落档: 同印章归档清单无 archive_code_git_head 键'
          '(清单字节不变);另印章下归档 rc=0——清单 archive_code_git_head='
          '归档印章,run_code_git_head=运行印章,correlation 点名「裁决后再'
          '交付」;包内地图==运行目录件',
          'archive_code_git_head' not in man
          and '归档代码' not in str(man.get('correlation'))
          and rc6 == 0
          and man2.get('archive_code_git_head') == ARC2
          and man2.get('run_code_git_head') == WORKTREE_HEAD
          and '裁决后再交付' in str(man2.get('correlation'))
          and man2.get('map_binding_status_equivalent') is True
          and open(os.path.join(arc2, 'MAP_REPORT.md'), 'rb').read() == b1,
          f"rc6={rc6} arc_head={str(man2.get('archive_code_git_head'))[:12]} "
          f"same_stamp_key={'archive_code_git_head' in man}")

    def _rp(head, out, extra=None):
        argv = ['research-one', '--stage', 'replay', '--package', arc2,
                '--engine-root', T, '--replay-out', os.path.join(TMPG, out)]
        return _head_cli(head, argv + (extra or []))

    rc7, d7 = _rp(ARC2, 'rp_ps_redeliv_arc')
    dd7 = d7.get('data') or {}
    c7 = _ck(d7, 'code_version_match')
    rj7 = os.path.join(TMPG, 'rp_ps_redeliv_arc')
    rp7 = _jload(os.path.join(rj7, 'REPLAY_REPORT.json'))
    md7 = _read(os.path.join(rj7, 'REPLAY_REPORT.md'))
    check('§L9b 归档印章代码严格重放: rc=0——门④按「当前=归档代码(裁决后'
          '再交付包,清单已声明)」通过,其余检查全过+逐字节相等;重放报告'
          '落档 package_archive_head 与「归档代码 SHA」行',
          rc7 == 0 and c7.get('ok') is True
          and '归档代码' in str(c7.get('detail'))
          and dd7.get('render_mode') == 'byte_equal'
          and all(c.get('ok') for c in (dd7.get('checks') or []))
          and rp7.get('package_archive_head') == ARC2
          and rp7.get('replay_code_head') == ARC2
          and rp7.get('package_run_head') == WORKTREE_HEAD
          and '归档代码 SHA' in md7,
          f"rc7={rc7} c7={str(c7.get('detail'))[:80]} "
          f"mode={dd7.get('render_mode')}")
    rc8, d8 = replay(arc2, T, out=os.path.join(TMPG, 'rp_ps_redeliv_run'))
    dd8 = d8.get('data') or {}
    check('§L9c 运行印章代码严格重放同一包: rc=0(当前==运行 SHA 的经典'
          '口径照旧成立,逐字节相等)',
          rc8 == 0 and dd8.get('render_mode') == 'byte_equal'
          and _ck(d8, 'code_version_match').get('ok') is True,
          f"rc8={rc8} mode={dd8.get('render_mode')}")
    rc9, d9 = _rp(ARC3, 'rp_ps_redeliv_third')
    rc10, d10 = _rp(ARC3, 'rp_ps_redeliv_third_allow',
                    ['--allow-code-mismatch'])
    check('§L9d 第三印章代码严格重放: 拒(code_version_mismatch);'
          '--allow-code-mismatch: 放行并披露越过',
          rc9 != 0
          and (d9.get('data') or {}).get('blocked') == 'code_version_mismatch'
          and rc10 == 0
          and '披露越过' in str(_ck(d10, 'code_version_match').get('detail')),
          f"rc9={rc9} blocked={(d9.get('data') or {}).get('blocked')} "
          f"rc10={rc10}")
    # ── §L9e–§L9g 两印章同渲染包: 裁决已在场时渲染(状态面未翻新),清单携
    #    archive_code_git_head 而无 map_binding_status_equivalent(正式验收
    #    第三处: 换问 B 工单包=运行印章渲染时裁决已在场,归档印章代码重放
    #    自己归档的包被门④误拒) ──
    vp2 = aj.record_semantic_verdict(T, rd, 'UPHELD',
                                     reviewer='r32gate-status席',
                                     notes='R32 正式验收: 裁决在场时的再裁决')
    vd2 = _jload(vp2)
    rc11, d11 = cli('report', rd, T)
    dd11 = d11.get('data') or {}
    arc4 = os.path.join(TMPG, 'arc_ps_same_render')
    rc12, _d12 = _head_cli(ARC2, ['research-one', '--stage', 'archive',
                                  '--report-dir', rd, '--engine-root', T,
                                  '--archive-dir', arc4])
    man4 = _jload(os.path.join(arc4, 'ARCHIVE_MANIFEST.json'))
    check('§L9e 同渲染两印章包: 裁决在场时的再裁决绑定=已裁形内容段摘要;'
          'report 不记状态面翻新;另印章归档 rc=0——清单携 archive_code_git_head'
          '(=归档印章)而无 map_binding_status_equivalent;裁决链 2 档',
          vd2.get('map_report_sha256') == sha1
          and rc11 == 0 and dd11.get('map_status_refreshed') is False
          and rc12 == 0
          and man4.get('archive_code_git_head') == ARC2
          and man4.get('run_code_git_head') == WORKTREE_HEAD
          and 'map_binding_status_equivalent' not in man4
          and man4.get('verdicts_n') == 2
          and '裁决后再交付' in str(man4.get('correlation')),
          f"rc11={rc11} refresh={dd11.get('map_status_refreshed')} "
          f"rc12={rc12} arc_head={str(man4.get('archive_code_git_head'))[:12]} "
          f"equiv_key={'map_binding_status_equivalent' in man4} "
          f"n={man4.get('verdicts_n')}")

    def _rp4(head, out, extra=None):
        argv = ['research-one', '--stage', 'replay', '--package', arc4,
                '--engine-root', T, '--replay-out', os.path.join(TMPG, out)]
        return _head_cli(head, argv + (extra or []))

    rc13, d13 = _rp4(ARC2, 'rp_ps_same_render_arc')
    dd13 = d13.get('data') or {}
    rp13 = _jload(os.path.join(TMPG, 'rp_ps_same_render_arc',
                               'REPLAY_REPORT.json'))
    check('§L9f 归档印章代码严格重放同渲染包: rc=0——门④认清单声明的归档代码'
          '为录制代码,不以状态面是否翻新为条件(交付字节正是归档代码所产);'
          '其余检查全过+逐字节相等;重放报告落档 package_archive_head',
          rc13 == 0 and _ck(d13, 'code_version_match').get('ok') is True
          and '归档代码' in str(_ck(d13, 'code_version_match').get('detail'))
          and dd13.get('render_mode') == 'byte_equal'
          and all(c.get('ok') for c in (dd13.get('checks') or []))
          and rp13.get('package_archive_head') == ARC2,
          f"rc13={rc13} blocked={dd13.get('blocked')} "
          f"c={str(_ck(d13, 'code_version_match').get('detail'))[:80]}")
    rc14, d14 = replay(arc4, T, out=os.path.join(TMPG, 'rp_ps_same_render_run'))
    rc15, d15 = _rp4(ARC3, 'rp_ps_same_render_third')
    check('§L9g 运行印章代码严格重放同一包: rc=0(同渲染包运行印章/归档印章'
          '两版代码均可严格重放);第三印章照旧拒(code_version_mismatch)',
          rc14 == 0 and (d14.get('data') or {}).get('render_mode') == 'byte_equal'
          and rc15 != 0
          and (d15.get('data') or {}).get('blocked') == 'code_version_mismatch',
          f"rc14={rc14} rc15={rc15}")


def main():
    print('Audit-R32 门 (HEAD %s)' % WORKTREE_HEAD[:12])
    try:
        sec_a()
        sec_b()
        sec_c()
        sec_d()
        sec_h()
        sec_i()
        sec_j()
        sec_k()
        sec_l()
    finally:
        n_ok = sum(1 for x in RESULTS if x)
        n = len(RESULTS)
        print('=== R32 门: %d/%d ===' % (n_ok, n))
        shutil.rmtree(TMPG, ignore_errors=True)
    return 0 if all(RESULTS) else 1


if __name__ == '__main__':
    sys.exit(main())
