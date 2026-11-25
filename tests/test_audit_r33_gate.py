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
任务2补充 r2(最终候选验收 T2 变体 B2/B5 抓到): 纪律绿而契约未全绿的拒收,
attach 回执 blocked/violations 均空(理由只在 report.json)→ 返回值与两路回执
带 blocked=contract_<裁决>+block_note+contract 摘要(零判断原文);其余回执
键形与 rc 口径不变。
夹具说明: 冻结快照=提交的 R31 B2 overlay 原件(真实);as-of 版本夹具=由该快照
按官方发布日截接的**构造版本**(snapshot_id 前缀 FIXTURE_,fixture_note 随行),
非真实历史快照——只用于核验绑定规则,不作为任何交付的证据。
任务3 真正的原问: 原问直答族(政策目标/待生效/通胀同比)判别;研究年月/回看窗口/同比基期分别解析;三面逐行+缺口逐项点名+版本绑定;12 月快照重跑守原问月范围;零事实/缺计划/缺证据→缺口显式回传(plan 段与 auto 段);席位装配脚本与回声契约;正式 CLI 链。族题夹具快照=真实 11-23 快照的族题子集与「12 月快照」合成件(夹具说明随行),不作为任何交付的证据。
任务4 冷启动: 来源备注不计入指标覆盖(日档守卫判定用观测图: 备注/状态/披露区闭集,真实退化仍拦截);流水线台账与 update 回执逐步骤时长/返回码/失败原因,守卫分流行单列;A股港股采集器时间预算(默认 800 秒)+A 股断点续采(同交易日窗且当日 bar 已定型才续,全部阶段完成后清除)+核心阶段截断不写主日档(exit 1)+随档 collection_status。守卫夹具=2026-11-24 真实守卫对的裁剪版(原件 sha256 记于夹具 _fixture)。
任务4修订 r3(终印章验收 run A2 抓到): 步骤自己打印的原因行不进台账/回执(只有 nonzero_exit+返回码,原因行被后续步骤滚出末 40 行)→ run_step 边界改为「透传不变+各流留末 6 个非空行(每行≤240 字)」,未成功步骤(超时/非零退出/被信号终止)把脱敏后的尾部写入 output_tail(台账行、update 回执 steps/failed_steps、doctor critical_steps 同形;成功/缺席/依赖跳过行与旧台账无此键);脱敏器不可导入=失败关闭(留注);孙进程持有管道不挂起。§T4-f/g 的旧判定(含 §T4-g5 行相等)原样保留。
任务5 预期差研究: 问句判别(「预期差」词形,或「机构观点」×「市场定价」并列)→单型研究计划(地图五面+预期差对照块: 机构观点库×同期限市场定价×事实逐行确定性对照,候选≠结论)+席位回声契约(候选行与须推导行逐行裁决;与引擎确定性面相左/虚构行号/假托机构原话=CONTRADICTED;自由文字数字须与引擎面对应);证伪窗口自研究截止日起算;问句研究年月=时点标记(不是序列观测窗);对照面用到的指标并入取数分级(来源随行;旧调用面不变);干净安装无观点库=草稿级缺口(转正办法随行),无运行快照=硬缺口(不再崩溃)。夹具说明: 观点库=tests/fixtures_r33/views 下 5 份**合成**文档(全部虚构机构与表述;1 份发布日晚于研究截止日=扣留,1 份违反 schema=隔离),定价曲线=提交的冻结快照 fed_futures_curve;门内不含任何真实机构观点内容。
任务5修订(独立席首轮 REVISE 后的闭环): 同期限定价参照(到期日当月或之前最后一个有读数的合约月)随行并入证据索引;对质观测窗=同窗首尾读数(月末口径;可取同比空间),引擎当前面只作窗后信息列出、不用于裁决;结构化对质=两侧预期按冻结序列复算,判断与复算不一致=CONTRADICTED;三项均为软契约(字段在场才核),旧档与无该字段工单零变化;席位工具只服务其预设的真实工单,门内只按函数级对照其纯函数面(不执行其模块级取数)。
任务5修订 r14(独立席终审 REVISE 后的闭环): 多窗结构化对质(软字段 face_off_checks,同一区分环在近1个月窗/12个月窗分别复算,各窗一致才给方向;字段不在场=旧档零漂移);席位工具定价曲线形态守卫改按此前运行峰值计、噪声界=半个定价步长且不小于一个最小变动价位(盘中演习面与日终真实面两处误拒更正);机构间分歧段在不可折算为基点时写明口径(旧数值幅度输出逐字不变);席位工具文字修订(证伪条件随行观测日、年度/近月两窗分量各自成句、已实现数据表述未映射行行号入质量门注记)以静态锁对照。
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
import policy_question as pq                    # noqa: E402

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
    return t, _add_code(t)


def _add_code(t):
    """代码副本入树(ia_cli.py/run_weekly.py/scripts 不含 __pycache__;
    env_config.py 仅当工作副本与提交版逐字节一致才复制——不接受含凭证
    副本)。→ env_config_copied"""
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
    return same


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
T3_TEXT = open(T3_VERBATIM, encoding='utf-8').read()


def _family_tree(tag, snapshot, calendar=None, code=False):
    """族题迷你树: config 副本+族题夹具快照(tests/fixtures_r33;版本日由夹具
    定);日历可换族题夹具日历(真实日历+合成日银决议);code=True 另入代码
    副本(可跑正式 CLI)。→ (tree, 快照路径)。"""
    t = os.path.join(TMPG, 'fam_' + tag)
    shutil.copytree(os.path.join(ROOT, 'config'), os.path.join(t, 'config'))
    os.makedirs(os.path.join(t, 'data', 'daily'), exist_ok=True)
    with open(os.path.join(FIX_R33, snapshot), encoding='utf-8') as f:
        snap = json.load(f)
    p = os.path.join(t, 'data', 'daily',
                     '%s.json' % snap['snapshot_id'])
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(snap, f, ensure_ascii=False)
    for fn in ('ea_20261105.json', 'japan_20261105.json', 'jp_20261105.json'):
        s = os.path.join(ROOT, 'data', 'daily', fn)
        if os.path.isfile(s):
            shutil.copy2(s, os.path.join(t, 'data', 'daily', fn))
    if calendar:
        shutil.copy2(os.path.join(FIX_R33, calendar),
                     os.path.join(t, 'config', 'release_calendar.json'))
    if code:
        _add_code(t)
    return t, p


def _plan_on(tree, question):
    """既有树上的离线 plan(S 步=替身信封;取数/证据口径/L1/索引/计划走真
    代码)。→ rep"""
    import research_orchestrator as ro
    orig = ro.run_step
    ro.run_step = _fake_step_ok
    try:
        return ro.run_research(question, root=tree,
                               out_dir=os.path.join(tree, 'out'))
    finally:
        ro.run_step = orig


def _pol_codes_j(jud, rep, cal, as_of):
    """整份判定档的政策纪律码(证据引用面取自 rep 的证据索引)。"""
    res = aj.validate_judgment(
        copy.deepcopy(jud),
        {e.get('ref') for e in (rep.get('evidence_index') or [])
         if e.get('ref')},
        _t2_mids, policy_events=aj.collect_policy_events(cal), as_of=as_of)
    return res['passed'], [v['code'] for v in res['violations']
                           if v['code'].startswith('POL')], res


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
# 修订 r3: 「该决议」归段内前文(可跨句)最近以日期提及的候选事件;区间端=
# 断言时点(早于生效日而写已生效=EARLY-CLAIM,见任务2修订 r3 节)。
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
    # 修订 r3(审查 MAJOR-6/指代归属): w4 区间端=断言时点、早于生效日→
    # EARLY-CLAIM(旧期望 POL-EFF-DATE=按「正文生效日」拒收,码与句义不符);
    # w7「该决议」归同句前文以日期提及的 2026-09-18 决议,断言时点不早于其
    # 生效日→接收(旧期望 POL-EFF-DATE,保守=指代歧义即拒;现指代归最近提及
    # 者,其后才出现的决定不夺走指代)
    check('§T2b-b 误句照旧拦截: 带事件日期的提前生效(POL-EFF-EARLY-CLAIM)/'
          '窗端早于生效日且无同实体已生效决定(区间端=断言时点→'
          'EARLY-CLAIM)/窗端=决议日(EARLY-CLAIM)/非完成态「生效的决议」'
          '(POL-EFF-DATE)/「截至 T 该决议已生效」指代同句前文的 2026-09-18 '
          '决议(已生效)→接收',
          w3 == ['POL-EFF-EARLY-CLAIM'] and w4 == ['POL-EFF-EARLY-CLAIM']
          and w5 and w5[0] == 'POL-EFF-EARLY-CLAIM' and w6 == ['POL-EFF-DATE']
          and w7 == [],
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
          'False+EARLY-CLAIM×2[修订 r3: 区间端早声称句由 POL-EFF-DATE 改为 '
          'EARLY-CLAIM]+无副本)',
          got['ok'][0] is True and got['ok'][1] == []
          and got['ok'][2] == 'VERIFIED' and got['ok'][3] is True
          and got['early'][0] is False
          and got['early'][1] == ['POL-EFF-EARLY-CLAIM']
          and got['early'][3] is False
          and got['win'][0] is False
          and got['win'][1] == ['POL-EFF-EARLY-CLAIM']
          and got['win'][3] is False, json.dumps(got, ensure_ascii=False))
    # e. 真实席位文本(席位装配脚本×12 月夹具): 整档零政策违规;单点扰动拒收
    t2, _p = _family_tree('t2b_dec', 'family_snapshot_20261215.json',
                          'family_calendar_dec.json')
    rep2 = _plan_on(t2, T3_TEXT)
    rd2 = rep2.get('report_dir')
    out_j = os.path.join(TMPG, 'seat_t2b_judgment.json')
    r = subprocess.run(
        [sys.executable, os.path.join(ROOT, 'scripts', 'seat_tools',
                                      'make_family_judgment.py'), t2,
         os.path.join(rd2, 'report.json'), os.path.join(TMPG, 'seat_t2b_x.json'),
         out_j], capture_output=True, text=True, timeout=900)
    with open(out_j, encoding='utf-8') as f:
        jud = json.load(f)
    with open(os.path.join(rd2, 'report.json'), encoding='utf-8') as f:
        rep2 = json.load(f)
    c1 = jud['l3']['contradictions'][0]['statement']
    ok0, p0, _res = _pol_codes_j(jud, rep2, os.path.join(
        t2, 'config', 'release_calendar.json'), '2026-11-30')
    a1 = '2026-12-04 生效(目标百分之一点五)'
    a2 = ('窗内(2026-05-30..2026-11-30)该决议已生效;截至研究截止日有一项'
          '已决议未生效条目: 2026-11-27 决议、2026-12-04 生效(目标百分之一点五)')
    a3 = '窗内(2026-05-30..2026-11-30)该决议已生效'
    pert = {}
    for key, old, new in (
            ('eff_date', a1, a1.replace('2026-12-04', '2026-11-28')),
            ('pending_as_done', a2, '截至研究截止日,2026-11-27 决议、2026-12-04 '
                                    '生效的调整已经实施(目标百分之一点五)'),
            ('event_dated', a3, '窗内(2026-05-30..2026-11-30)2026-11-27 决议已生效')):
        j2 = copy.deepcopy(jud)
        assert old in c1
        j2['l3']['contradictions'][0]['statement'] = c1.replace(old, new)
        pert[key] = _pol_codes_j(j2, rep2, os.path.join(
            t2, 'config', 'release_calendar.json'), '2026-11-30')[1]
    check('§T2b-e 真实席位文本(装配脚本×12 月夹具,as_of=2026-11-30): 整档'
          '零政策违规;单点扰动→生效日改写 POL-EFF-DATE/待生效写成已实施 '
          'EARLY-CLAIM/带事件日期的提前生效 EARLY-CLAIM',
          r.returncode == 0 and ok0 and p0 == []
          and 'POL-EFF-DATE' in pert['eff_date']
          and 'POL-EFF-EARLY-CLAIM' in pert['pending_as_done']
          and pert['event_dated'] == ['POL-EFF-EARLY-CLAIM'],
          f'rc={r.returncode} ok0={ok0} p0={p0} '
          f'pert={json.dumps(pert, ensure_ascii=False)}')


# ══ 任务2修订 r3: 逐分句时态模型(独立审查 6 MAJOR 修订) ══════════════════════
# S2 受审(独立审查席 REVISE: 6 MAJOR/4 MINOR/3 NIT)。根因=断言时点与完成态分句
# 取句级/段级口径: 完成态分句不与事件日期、断言时点同分句时漏核(MAJOR-1);裸
# 「落地/生效」与「加息至+中数词」不在完成态词形表(MAJOR-2);区间端未当断言
# 时点(MAJOR-3);带空格中文日期对日期规则不可见(MAJOR-4);「已生效仍写未生效」
# 被段级完成态豁免整段放行(MAJOR-5);区间端早声称句被旧日期规则按「正文生效日」
# 拒收——码与句义不符(MAJOR-6)。修: 归一文本→句→分句(括注内逗号不分句)→逐
# 分句断言时点(自带标记/继承同句前文/运行级截止日)→逐分句旗标→按 事件×断言
# 时点×实施状态 出码;指代「该决议」归段内前文(可跨句)最近以日期提及的候选
# 事件;日期规则读归一文本,区间端/句内断言时点处「生效」的归属由时态模型定;
# 挂接回执与运行目录记代码版本(MINOR-4)。审查席 87 条预注册探针入仓为离线
# 夹具(tests/fixtures_r33/t2_probe_cases.json: 探针落位处的 l3 陈述全文+底稿
# 其余陈述+日历种类+预注册判定);全副本回放与「仅陈述列表」夹具逐例同码(87/87,
# 见证据包)。期望变更如实记于 §T2b-b(w4/w7)与 §T2b-d(win)。


def _t2_core_of(sent):
    """探针句核心(去掉「(原句不改: …)」一类标注括注)。"""
    for pre in ('(原句不改: ', '(插入句: ', '(替换: '):
        if sent.startswith(pre) and sent.endswith(')'):
            return sent[len(pre):-1]
    return sent


def _t2_probe_run(doc, c, ev, asof):
    """把探针陈述放回底稿陈述列表后整档走函数入口 validate_judgment
    (底稿 FAM=12 月夹具日历;ISO/MAP=真实日历)。"""
    cal = 'dec' if c['base'] == 'FAM' else 'real'
    events, as_of = ev[cal], asof[cal]
    stmts = list(doc['bases'][c['base']])
    stmts[c['at']] = c['stmt']
    # 外壳=合规判定档母本(结构纪律全过);证据面=单一引用 r1
    mid = 'JP_POLICY_TARGET'
    jud = _t2_valid_judgment(mid, mid, stmts[0])
    for sc in jud['l4']['scenarios']:
        sc['rows']['asset_direction']['evidence_refs'] = ['r1']
    for ln in jud['l3']['mechanism_chains'][0]['links']:
        if ln.get('evidence_refs'):
            ln['evidence_refs'] = ['r1']
    jud['l3']['contradictions'] = [
        {'id': 'C%d' % (i + 1), 'statement': s, 'basis': '基于证据索引的推断',
         'competing_explanations': ['解释一(基准)', '解释二(反例)'],
         'evidence_refs': ['r1']} for i, s in enumerate(stmts)]
    return aj.validate_judgment(jud, {'r1'}, {mid},
                                policy_events=events, as_of=as_of)


def sec_t2_l():
    print('═══ 任务2修订 r3: 逐分句时态模型(审查席 87 探针离线回归) ═══')
    with open(os.path.join(FIX_R33, 't2_probe_cases.json'),
              encoding='utf-8') as f:
        doc = json.load(f)
    cases = doc['cases']
    ev = {'real': aj.collect_policy_events(os.path.join(
              ROOT, 'config', 'release_calendar.json')),
          'dec': aj.collect_policy_events(os.path.join(
              FIX_R33, 'family_calendar_dec.json'))}
    asof = {'real': '2026-11-23', 'dec': '2026-11-30'}
    n_acc = sum(1 for c in cases if c['verdict'] == 'ACCEPT')
    n_rej = sum(1 for c in cases if c['verdict'] == 'REJECT')
    check('§T2-l-0 夹具结构: 87 例(接收 29/拒收 58);底稿 FAM/ISO/MAP 各留一个'
          '探针落位空位;探针句在受检陈述内;真实日历仅一条日银决议、12 月夹具'
          '日历两条',
          len(cases) == 87 and n_acc == 29 and n_rej == 58
          and set(doc['bases']) == {'FAM', 'ISO', 'MAP'}
          and all(sum(1 for s in b if s is None) == 1
                  for b in doc['bases'].values())
          and all(_t2_core_of(c['sentence']) in c['stmt'] for c in cases)
          and len([e for e in ev['real'] if e.get('entity') == 'JP']) == 1
          and len([e for e in ev['dec'] if e.get('entity') == 'JP']) == 2,
          f'n={len(cases)} acc={n_acc} rej={n_rej}')
    res = {c['id']: _t2_probe_run(doc, c, ev, asof)
           for c in cases}

    def _ok(c, r):
        pol = [v['code'] for v in r['violations']
               if str(v['code']).startswith('POL')]
        if c['verdict'] == 'ACCEPT':
            return r.get('passed') is True and pol == []
        return (r.get('passed') is False
                and any(x in c['codes'] for x in pol))

    bad = [c['id'] for c in cases if not _ok(c, res[c['id']])]
    check('§T2-l-1 审查席 87 探针逐例符合预注册判定: 接收 29 例=通过且零政策'
          '违规;拒收 58 例=不通过且政策违规码属于预注册码集(修订前引擎: 早声称'
          '误句 7 句被接收、区间端早声称句码不符等,见审查裁决摘要)',
          not bad, f'bad={bad[:8]}')
    wtxt = [(pid, v['code'], v.get('detail') or '')
            for pid in ('MAP_W11', 'MAP_W20', 'FAM_FW01', 'FAM_FW05')
            for v in res[pid]['violations']
            if str(v['code']).startswith('POL')]
    check('§T2-l-2 区间端早声称句(MAP_W11/MAP_W20/FAM_FW01/FAM_FW05): 违规码='
          'POL-EFF-EARLY-CLAIM,detail 写明「区间端 … 为断言时点」且不写「正文生效'
          '日」(审查 MAJOR-6: 旧日期规则按「正文生效日」拒收,码与句义不符)',
          len(wtxt) == 4
          and all(cd == 'POL-EFF-EARLY-CLAIM' for _, cd, _ in wtxt)
          and all('区间端' in d and '为断言时点' in d and '正文生效日' not in d
                  for _, _, d in wtxt),
          f'{[(p, c) for p, c, _ in wtxt]}')
    tb = [(pid, v.get('detail') or '') for pid, r in res.items()
          for v in r['violations']
          if v['code'] in ('POL-EFF-EARLY-CLAIM', 'POL-EFF-LATE-PENDING',
                           'POL-EFF-DECISION-NOT-YET-KNOWN')]
    miss = [p for p, d in tb
            if ('(来源: ' not in d and '为断言时点(「' not in d)]
    check('§T2-l-3 时点类违规(EARLY-CLAIM/LATE-PENDING/DECISION-NOT-YET-KNOWN)'
          '的 detail 一律注明断言时点来源(「来源: 句内/区间端/分句内/同句前文/'
          '运行级截止日」;区间端早声称句直接写「区间端 T 为断言时点(「标记」)」)'
          '(审查 MINOR-2)',
          bool(tb) and not miss, f'n={len(tb)} missing={miss[:6]}')
    # 指代「该决议」: 归段内前文(可跨句)最近以日期提及的候选事件(两事件夹具)
    anov = '日本: 发布日历实录载 2026-11-27 决议、2026-12-04 生效(目标1.5%)'
    asep = '日本: 发布日历实录载 2026-09-18 决议、2026-09-24 生效'
    va = {
        'same_sent_last_is_pending': (
            asep + ';' + anov + ';截至 2026-11-30 该决议已生效',
            ['POL-EFF-EARLY-CLAIM']),
        'same_sent_last_is_effective': (
            anov + ';' + asep + ';截至 2026-11-30 该决议已生效', []),
        'cross_sent_early': (
            anov + '。截至 2026-11-30 该决议已经实施。',
            ['POL-EFF-EARLY-CLAIM']),
        'cross_sent_true_pending': (
            anov + '。截至 2026-11-30 该决议尚未生效。', []),
        'cross_sent_late': (
            asep + '。截至 2026-11-30 该决议尚未生效。',
            ['POL-EFF-LATE-PENDING']),
        'cross_sent_true_effective': (
            asep + '。截至 2026-11-30 该决议已经生效。', []),
    }
    vgot = {k: _pol_codes(s, '2026-11-30', ev['dec']) for k, (s, _) in va.items()}
    check('§T2-l-4 指代「该决议」归段内前文(可跨句)最近以日期提及的候选事件: '
          '同句/跨句·指待生效决议而写已生效→EARLY-CLAIM;指已生效决议而写已生效→'
          '接收;指待生效决议写尚未生效→接收;指已生效决议仍写尚未生效→'
          'LATE-PENDING',
          vgot == {k: x for k, (_, x) in va.items()},
          json.dumps(vgot, ensure_ascii=False))
    vpar = _pol_codes(F_T2B + '已决议待生效的调整(目标1.5%,2026-12-04 生效)如期生效'
                      + P_T2B, '2026-11-30', ev['dec'])
    check('§T2-l-5 括注内逗号不分句: 「已决议待生效的调整(目标x,日期 生效)如期'
          '生效」→零政策违规(未然口径;拆成两分句会把「日期 生效)如期生效」误判'
          '为提前生效)', vpar == [], f'{vpar}')
    # MINOR-4: 挂接回执与运行目录记代码版本(函数入口: 代码树 git;CLI: 印章三级链)
    import research_orchestrator as ro
    st_ok = '日本央行 2026-09-18 决议、2026-09-24 生效;截至 2026-09-30 该加息已经生效。'
    st_bad = '日本央行 2026-09-18 决议、2026-09-24 生效;截至 2026-09-20 该加息已经实施。'
    t, rd, jp = _t2_synth_run('t2l_ok', '2026-09-30', st_ok)
    t2, rd2, jp2 = _t2_synth_run('t2l_bad', '2026-09-20', st_bad)
    r_ok = aj.attach_judgment(rd, jp, root=t)
    r_bad = aj.attach_judgment(rd2, jp2, root=t2)
    exp = ro._git_state(t)
    _isgit = os.path.exists(os.path.join(ROOT, '.git'))
    head = (subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                           capture_output=True, text=True,
                           timeout=30).stdout.strip() if _isgit else None)
    meta = (_t2_attach_res(rd).get('agent_judgment') or {})
    check('§T2-l-6 挂接步骤记代码版本(审查 MINOR-4): attach_judgment 返回值(成功/'
          '纪律拒收两路)与运行目录 agent_judgment 元数据带 code_git_head/'
          'code_git_head_source/code_git_diff_sha256,取值=取码 helper 对运行树的'
          '结果;代码树为 git 库时=其 HEAD(source=code_tree)',
          r_ok.get('attached') is True and r_bad.get('attached') is False
          and (r_ok.get('code_git_head'), r_ok.get('code_git_head_source'),
               r_ok.get('code_git_diff_sha256')) == exp
          and (r_bad.get('code_git_head'), r_bad.get('code_git_head_source'),
               r_bad.get('code_git_diff_sha256')) == exp
          and (meta.get('code_git_head'), meta.get('code_git_head_source'),
               meta.get('code_git_diff_sha256')) == exp
          and (not _isgit or (exp[0] == head and exp[1] == 'code_tree')),
          f'exp={(exp[0][:12] if exp[0] else None, exp[1])} isgit={_isgit} '
          f'r_ok={(r_ok.get("attached"))} r_bad={(r_bad.get("attached"))}')
    ct, _ = _code_tree('t2l_cli')
    _stamp = 'a' * 40                       # 合成印章(仅测试三级链第三级)
    with open(os.path.join(ct, 'CODE_VERSION.json'), 'w',
              encoding='utf-8') as f:
        json.dump({'git_head': _stamp, 'git_diff_sha256': 'b' * 64,
                   'stamped_at': '2026-11-25T00:00:00+08:00'}, f)
    rc1, d1 = _cli(['research-one', '--stage', 'attach', '--report-dir', rd,
                    '--judgment', jp, '--engine-root', ct], cwd=ct)
    rc2, d2 = _cli(['research-one', '--stage', 'attach', '--report-dir', rd2,
                    '--judgment', jp2, '--engine-root', ct], cwd=ct)
    rc3, d3 = _cli(['research-attach', '--report-dir', rd2,
                    '--judgment', jp2], cwd=ct)
    rc4, d4 = _cli(['research-one', '--stage', 'auto', '--report-dir', rd2,
                    '--judgment', jp2, '--engine-root', ct], cwd=ct)
    a1, a2, a3 = (d.get('data') or {} for d in (d1, d2, d3))
    ch4 = [c for c in ((d4.get('data') or {}).get('chain') or [])
           if c.get('stage') == 'attach']
    _pair = lambda a: (a.get('code_git_head'), a.get('code_git_head_source'))  # noqa: E731
    check('§T2-l-7 回执带代码版本: research-one attach(成功/纪律拒收)、旧入口 '
          'research-attach、auto 链 attach 失败行均带 code_git_head+'
          'code_git_head_source;代码副本树无 git 时取根目录印章(source='
          'code_version_stamp)',
          rc1 == 0 and d1.get('ok') is True and _pair(a1) == (_stamp, 'code_version_stamp')
          and rc2 == 0 and d2.get('ok') is False and _pair(a2) == (_stamp, 'code_version_stamp')
          and rc3 == 1 and d3.get('ok') is False and _pair(a3) == (_stamp, 'code_version_stamp')
          and rc4 == 1 and len(ch4) == 1 and ch4[0].get('ok') is False
          and _pair(ch4[0]) == (_stamp, 'code_version_stamp'),
          f'rc={rc1}/{rc2}/{rc3}/{rc4} pairs={_pair(a1)}/{_pair(a2)}/{_pair(a3)}'
          f'/{[_pair(c) for c in ch4]}')
    # 变异自检: 关掉时态模型/日期规则,夹具必须报出(防夹具空转)
    _orig = (aj._pol_tense_violation, aj._pol_date_specs)
    mut = {}
    try:
        aj._pol_tense_violation = lambda *a, **k: None
        mut['tense_off'] = [c['id'] for c in cases
                            if not _ok(c, _t2_probe_run(doc, c, ev, asof))]
        aj._pol_tense_violation, aj._pol_date_specs = _orig[0], lambda *a, **k: []
        mut['date_off'] = [c['id'] for c in cases
                           if not _ok(c, _t2_probe_run(doc, c, ev, asof))]
    finally:
        aj._pol_tense_violation, aj._pol_date_specs = _orig
    check('§T2-l-8 变异自检: 关掉时态模型→拒收探针失守 ≥ 30 例;关掉日期'
          '规则→失守 ≥ 8 例;恢复后 87 例复绿',
          len(mut['tense_off']) >= 30 and len(mut['date_off']) >= 8
          and all(_ok(c, _t2_probe_run(doc, c, ev, asof))
                  for c in cases),
          f'tense_off={len(mut["tense_off"])} date_off={len(mut["date_off"])}')


# ══ 任务2修订 r3 收尾: 顶层定义无重名死副本 ════════════════════════════════════
# 提交前复核发现 scripts/agent_judgment.py 内 4 个时态模型辅助函数各带 3–8 份死副本
# (拼接块逐次前置追加所致;Python 只绑定末次定义——全门、全电池、复杂度基线全绿
# 也看不出)。此段对全部入库生产模块做静态检查;变异自检 = 内存中给该模块末尾追加
# 一份其末次顶层函数(重名)→ 必须报出,原文件必须零报出。


def _t2_dup_defs(src):
    import ast
    names = [n.name for n in ast.parse(src).body
             if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
    return sorted({x for x in names if names.count(x) > 1})


def _t2_prod_modules():
    """入库生产模块: 仓库根 *.py + scripts/**/*.py(不含 tests/ docs/ 与 .venv)。有 .git 时
    以 git ls-files 为准(git archive 导出的安装树无 .git → 按同一范围走目录)。"""
    if os.path.exists(os.path.join(ROOT, '.git')):
        out = subprocess.run(['git', 'ls-files', '*.py'], cwd=ROOT, capture_output=True,
                             text=True, env=dict(os.environ, GIT_OPTIONAL_LOCKS='0')).stdout
        return sorted(p for p in out.split('\n')
                      if p and not p.startswith(('tests/', 'docs/')) and
                      os.path.exists(os.path.join(ROOT, p)))
    mods = [f for f in sorted(os.listdir(ROOT)) if f.endswith('.py')]
    for dp, dns, fns in os.walk(os.path.join(ROOT, 'scripts')):
        dns[:] = [d for d in dns if not d.startswith('.')]
        mods += [os.path.relpath(os.path.join(dp, f), ROOT)
                 for f in sorted(fns) if f.endswith('.py')]
    return mods


def sec_t2_m():
    print('═══ 任务2修订 r3 收尾: 顶层定义无重名死副本 ═══')
    mods = _t2_prod_modules()
    dups = {}
    for p in mods:
        try:
            dups[p] = _t2_dup_defs(io.open(os.path.join(ROOT, p), encoding='utf-8').read())
        except SyntaxError:
            dups[p] = ['<unparsable>']
    bad = {p: d for p, d in dups.items() if d}
    check('§T2-m-1 入库生产模块(根与 scripts/,不含 tests/ docs/)顶层 def/class 无重名: '
          '%d 个模块' % len(mods), len(mods) >= 90 and not bad, bad)
    p = 'scripts/agent_judgment.py'
    src = io.open(os.path.join(ROOT, p), encoding='utf-8').read()
    import ast
    last = [n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef)][-1]
    mut = src.rstrip('\n') + '\n\n\n' + ast.get_source_segment(src, last) + '\n'
    m = _t2_dup_defs(mut)
    check('§T2-m-2 变异自检: 追加一份末次顶层函数的重名副本(%s)→ 报出且只报出它;'
          '原文件零报出' % last.name, m == [last.name] and not _t2_dup_defs(src), m)


# ══ 任务2修订 r4: 状态断言不带事件日期的归属(审查席 83 探针+自对抗) ════════
# 绑定上一候选的独立审查复算 137 点、6 处不符,全部为误收;共同根因=状态断言
# (既成/未然/目标水平)不带事件日期时整段放行: 区间起点日期留作分句内词元
# (带区间的既成句不绑定);生效后未然句只认带事件日期/指代/阿拉伯数字+本实体;
# 公告前「已决议」既成句形无日期不拦;目标水平陈述无「当前」词形或写中数词
# 不拦。修订 r4: 归属加「断言时点的在办事件」一路(_pol_rel),三种状态各自
# 成规则,句首独立日期分句=断言时点,区间整体置「□」,日历可选 direction 字段
# 透传(事件面)。本段=审查席探针离线回归+自对抗+两事件日历+变异自检+局限
# 例的出路。预注册判定不改(局限例 P20 的预注册拒收保留,不计入失守)。


def _t2_r4_ok(c, r):
    """夹具判定: ACCEPT=整档通过且零政策违规;REJECT=不通过且政策违规码属于
    预注册码集(r=validate_judgment 结果;单句探针给 {'codes': [...]} 简形)。"""
    if 'violations' in r:
        ok_all = r.get('passed')
        pol = [v['code'] for v in r['violations']
               if str(v['code']).startswith('POL')]
    else:
        ok_all, pol = (c['verdict'] == 'ACCEPT'), r['codes']
    if c['verdict'] == 'ACCEPT':
        return ok_all is True and pol == []
    return ok_all is not True and bool(set(c['codes']) & set(pol))


def sec_t2_n():
    print('═══ 任务2修订 r4: 状态断言不带事件日期的归属(审查席 83+自对抗 38+'
          '两事件 12) ═══')
    with open(os.path.join(FIX_R33, 't2_r4_cases.json'), encoding='utf-8') as f:
        doc = json.load(f)
    cases, selfc, decc = doc['cases'], doc['self'], doc['dec']
    real_cal = os.path.join(ROOT, 'config', 'release_calendar.json')
    ev = {'real': aj.collect_policy_events(real_cal),
          'dec': aj.collect_policy_events(os.path.join(
              FIX_R33, 'family_calendar_dec.json'))}
    asof = {'real': '2026-11-23', 'dec': '2026-11-30'}

    def _rev():
        return {c['id']: _t2_probe_run(doc, c, ev, asof) for c in cases}

    def _bad(res):
        return sorted(c['id'] for c in cases
                      if not _t2_r4_ok(c, res[c['id']]))

    def _txt(cs, events):
        return {c['id']: {'codes': _pol_codes(c['text'], c['as_of'], events)}
                for c in cs}

    n_acc = sum(1 for c in cases if c['verdict'] == 'ACCEPT')
    n_rej = sum(1 for c in cases if c['verdict'] == 'REJECT')
    n_gray = sum(1 for c in cases if c['gray'])
    n_leg = sum(1 for c in selfc if c.get('legacy'))
    check('§T2-n-0 夹具结构: 审查席 83 例(接收 36/拒收 47;灰区 21 不计入'
          '失守)+自对抗 38 例(接收 19/拒收 19;修订前既有保守规则 3 例)+两事件'
          '日历 12 例(接收 6/拒收 6);底稿 FAM/MAP/MAPc0 各留一个落位空位;探针句'
          '在受检陈述内;已披露局限恰为例 P20;真实日历仅一条日银决议且无 '
          'direction 字段',
          len(cases) == 83 and n_acc == 36 and n_rej == 47 and n_gray == 21
          and set(doc['bases']) == {'FAM', 'MAP', 'MAPc0'}
          and all(sum(1 for s in b if s is None) == 1
                  for b in doc['bases'].values())
          and all(c['sentence'] in c['stmt'] for c in cases)
          and len(selfc) == 38
          and sum(1 for c in selfc if c['verdict'] == 'ACCEPT') == 19
          and n_leg == 3
          and len(decc) == 12
          and sum(1 for c in decc if c['verdict'] == 'ACCEPT') == 6
          and sorted(doc['known_limitation']) == ['P20']
          and len([e for e in ev['real'] if e.get('entity') == 'JP']) == 1
          and all(e.get('direction') is None for e in ev['real']),
          'n=%d acc=%d rej=%d gray=%d self=%d legacy=%d dec=%d'
          % (len(cases), n_acc, n_rej, n_gray, len(selfc), n_leg, len(decc)))
    res = _rev()
    bad = _bad(res)
    byc = {}
    for c in cases:
        for v in res[c['id']]['violations']:
            k = str(v['code'])
            if k.startswith('POL'):
                byc[k] = byc.get(k, 0) + 1
    check('§T2-n-1 审查席 83 探针逐例符合预注册判定(整档走函数入口): 接收 36 例'
          '=通过且零政策违规;拒收 47 例=不通过且政策违规码属于预注册码集;失守='
          '已披露局限例且仅此一例(P20 动作词未然句: 日历无方向字段且无前件,'
          '无从判方向)',
          bad == sorted(doc['known_limitation']) == ['P20'],
          'bad=%s codes=%s' % (bad, byc))
    rs = _txt(selfc, ev['real'])
    bad_s = sorted(c['id'] for c in selfc if not _t2_r4_ok(c, rs[c['id']]))
    check('§T2-n-2 自对抗 38 例: 接收 19 例零政策违规;拒收 19 例命中预注册码'
          '(含修订前既有的保守规则 3 例: 决议-生效成对纪律/待生效值写成当前值'
          '照旧拒收——修订不放宽旧规则)',
          not bad_s and n_leg == 3
          and all(rs[c['id']]['codes'] for c in selfc if c.get('legacy')),
          'bad=%s legacy=%s' % (bad_s, [(c['id'], rs[c['id']]['codes'])
                                        for c in selfc if c.get('legacy')]))
    rd = _txt(decc, ev['dec'])
    bad_d = sorted(c['id'] for c in decc if not _t2_r4_ok(c, rd[c['id']]))
    check('§T2-n-3 两事件日历 12 例(合成日银决议 2026-11-27 决议/2026-12-04 '
          '生效叠在已生效的真实决议之上): 接收 6 例零政策违规;拒收 6 例命中'
          '预注册码(无事件日期的状态断言归属到断言时点的在办事件)',
          not bad_d, 'bad=%s' % bad_d)
    # 四类根因代表句(区间既成/生效后未然/公告前既成/中数词目标水平)+工单原句
    rep = [('A', '回看窗口 2026-09-01 至 2026-09-20 内，日本央行加息已经实施。',
            'POL-EFF-EARLY-CLAIM', '区间端 2026-09-20'),
           ('B', '截至 10 月 30 日，日本央行加息尚未生效。',
            'POL-EFF-LATE-PENDING', ''),
           ('C', '截至 9 月 17 日，日本央行已决议加息。',
            'POL-EFF-DECISION-NOT-YET-KNOWN', ''),
           ('D', '截至 9 月 20 日，日本央行官方政策目标利率为百分之一点二五。',
            'POL-EFF-EARLY-CLAIM', ''),
           ('工单拒收句', '截至 9 月 20 日，9 月 24 日生效的加息已经实施。',
            'POL-EFF-EARLY-CLAIM', ''),
           ('工单接收句', '截至 9 月 20 日，9 月 24 日生效的加息尚未生效。',
            '', '')]
    rep_res = []
    for tag, txt, code, sub in rep:
        v = aj.validate_judgment(
            _mk_judgment(txt), {'r1'}, {'JP_POLICY_TARGET'},
            policy_events=ev['real'], as_of='2026-11-23')
        pol = [x['code'] for x in v['violations']
               if str(x['code']).startswith('POL')]
        det = ''.join(x.get('detail') or '' for x in v['violations'])
        rep_res.append((tag, pol, v.get('passed'), sub in det))
    check('§T2-n-4 四类误收根因代表句(函数入口): 带回看区间的既成句→早声称'
          '(断言时点=区间端 2026-09-20);生效后「尚未生效」→把已生效决定写成'
          '待生效;公告前「已决议加息」→当时无从得知;中数词目标水平(百分之一'
          '点二五)→早声称;工单拒收句→早声称;工单接收句→零政策违规(最小判定档外壳,只看政策类违规码)',
          [x[1] for x in rep_res] == [[r[2]] for r in rep[:5]] + [[]]
          and rep_res[0][3],
          'got=%s win_detail=%s' % ([(x[0], x[1]) for x in rep_res],
                                    rep_res[0][3]))
    # 变异自检: 关掉归属一路/实施状态未然/叙述豁免,夹具必须报出(防空转)
    keep = (aj._pol_rel, aj._pol_clause_flags, aj._pol_narrated)
    extra = {}
    try:
        aj._pol_rel = lambda *a, **k: False
        extra['rel_off'] = [x for x in _bad(_rev()) if x not in bad]
        aj._pol_rel = keep[0]

        def _nostatus(ctext, e, cands=None, gov=()):
            return dict(keep[1](ctext, e, cands, gov), pend_status=False)
        aj._pol_clause_flags = _nostatus
        extra['status_off'] = [x for x in _bad(_rev()) if x not in bad]
        aj._pol_clause_flags = keep[1]
        aj._pol_narrated = lambda *a, **k: False
        extra['narr_off'] = [x for x in _bad(_rev()) if x not in bad]
    finally:
        aj._pol_rel, aj._pol_clause_flags, aj._pol_narrated = keep
    check('§T2-n-5 变异自检: 关掉「在办事件」归属一路→新失守 ≥ 6 例;关掉实施'
          '状态未然(把决定写成未实施)→新失守 ≥ 7 例;关掉叙述性将来豁免→新'
          '失守 ≥ 1 例(误拦);恢复后回到基线(仅局限例)',
          len(extra['rel_off']) >= 6 and len(extra['status_off']) >= 7
          and len(extra['narr_off']) >= 1 and _bad(_rev()) == bad,
          'rel_off=%d status_off=%d narr_off=%d' % (
              len(extra['rel_off']), len(extra['status_off']),
              len(extra['narr_off'])))
    # 局限例的出路: 日历条目补 direction 字段(副本;真实日历未改)
    with open(real_cal, encoding='utf-8') as f:
        cal = json.load(f)
    hit = [e for e in cal['entries']
           if e.get('entry_id') == 'RC-JP-BOJ-TARGET-2026-09']
    for e in hit:
        e['direction'] = 'hike'
    cp = os.path.join(TMPG, 'release_calendar_dir.json')
    with open(cp, 'w', encoding='utf-8') as f:
        json.dump(cal, f, ensure_ascii=False)
    ev_dir = aj.collect_policy_events(cp)
    c20 = [c for c in cases if c['id'] == 'P20'][0]
    r20 = _t2_probe_run(doc, c20, {'real': ev_dir, 'dec': ev['dec']}, asof)
    pol20 = [v['code'] for v in r20['violations']
             if str(v['code']).startswith('POL')]
    check('§T2-n-6 局限例的出路: 日历条目(副本)补 direction 字段→事件面透传,'
          'P20「截至 10 月 30 日，日本央行尚未加息。」由放行转为拒收 '
          'POL-EFF-LATE-PENDING;真实日历未改(该字段的补录=用户裁定项)',
          len(hit) == 1
          and [e.get('direction') for e in ev_dir] == ['hike']
          and pol20 == ['POL-EFF-LATE-PENDING'] and r20.get('passed') is False,
          'hit=%d dir=%s pol=%s' % (
              len(hit), [e.get('direction') for e in ev_dir], pol20))


# ══ 任务2补充 r2: 契约门拒收理由随回执 ════════════════════════════════════
# 最终候选验收(T2 变体 B2/B5: 正句+目标 1.25%)暴露: 纪律绿、契约未全绿的
# 拒收,attach 回执 blocked/violations 均空,理由只在 report.json(回执无理由
# =不可复核)。修: attach_judgment 返回值与 research-one / research-attach
# 两路回执(auto 链 attach 行同)带 blocked=contract_<裁决>+block_note+
# contract{verdict,stats[,error]}(零判断原文);成功/纪律拒收/门槛拒收三路
# 回执键形不变;rc 口径不变(research-one 拒收 rc=0=冻结契约,
# research-attach 拒收 rc=1)。


def sec_t2_k():
    print('═══ 任务2补充 r2: 契约门拒收理由随回执 ═══')
    cal = os.path.join(FIX_R33, 'family_calendar_dec.json')
    stmt_ok = (F_T2B + '窗内(2026-05-30..2026-11-30)该决议已生效' + P_T2B
               ).replace('1.25%', '百分之一点二五').replace('1.5%', '百分之一点五')
    # 契约门拒收档: 同句保留未绑定数字 1.25%(合成证据面无对应序列)
    stmt_cg = (F_T2B + '窗内(2026-05-30..2026-11-30)该决议已生效' + P_T2B
               ).replace('1.5%', '百分之一点五')
    stmt_d = (F_T2B + '窗内(2026-05-30..2026-11-30)2026-11-27 决议已生效'
              '(目标1.5%)').replace('1.25%', '百分之一点二五').replace(
                  '1.5%', '百分之一点五')
    got = {}
    for key, stmt in (('ok', stmt_ok), ('cg', stmt_cg), ('d', stmt_d)):
        t, rd, jp = _t2_synth_run('t2k_' + key, '2026-11-30', stmt)
        shutil.copy2(cal, os.path.join(t, 'config', 'release_calendar.json'))
        got[key] = (aj.attach_judgment(rd, jp, root=t), _t2_attach_res(rd),
                    t, rd, jp)
    r_ok, rep_ok, _t, rd_ok, jp_ok = got['ok']
    r_cg, rep_cg, _t, rd_cg, jp_cg = got['cg']
    r_d, rep_d, _t, rd_d, jp_d = got['d']
    cs = r_cg.get('contract_summary') or {}
    _new = {'blocked', 'block_note', 'contract_summary'}
    check('§T2-k1 attach_judgment 返回值: 契约门拒收(正句+未绑定数字)='
          'attached False+纪律 passed True+blocked=contract_not_verified+'
          'block_note+contract_summary{verdict:NOT_VERIFIED,stats.unbound≥1}'
          '(键⊂{verdict,stats,error},零判断原文)+无判定档副本+与 report.json '
          'agent_judgment.blocked 同值;成功/纪律拒收两路返回值无新增键',
          r_cg.get('attached') is False
          and (r_cg.get('validation') or {}).get('passed') is True
          and r_cg.get('blocked') == 'contract_not_verified'
          and isinstance(r_cg.get('block_note'), str) and bool(r_cg['block_note'])
          and cs.get('verdict') == 'NOT_VERIFIED'
          and (cs.get('stats') or {}).get('unbound', 0) >= 1
          and set(cs) <= {'verdict', 'stats', 'error'}
          and '窗内' not in json.dumps(cs, ensure_ascii=False)
          and not os.path.isfile(os.path.join(rd_cg, 'agent_judgment.json'))
          and (rep_cg.get('agent_judgment') or {}).get('blocked')
          == r_cg.get('blocked')
          and r_ok.get('attached') is True and not (_new & set(r_ok))
          and r_d.get('attached') is False and not (_new & set(r_d))
          and bool((r_d.get('validation') or {}).get('violations')),
          json.dumps({k: {x: v for x, v in got[k][0].items()
                          if x not in ('validation', 'contract_verification')}
                      for k in got}, ensure_ascii=False, default=str)[:700])
    # 正式 CLI(research-one --stage attach)与旧入口(research-attach)回执
    ct, _ = _code_tree('t2k_cli')
    shutil.copy2(cal, os.path.join(ct, 'config', 'release_calendar.json'))
    rc1, d1 = _cli(['research-one', '--stage', 'attach', '--report-dir', rd_cg,
                    '--judgment', jp_cg, '--engine-root', ct], cwd=ct)
    rc2, d2 = _cli(['research-one', '--stage', 'attach', '--report-dir', rd_ok,
                    '--judgment', jp_ok, '--engine-root', ct], cwd=ct)
    rc3, d3 = _cli(['research-one', '--stage', 'attach', '--report-dir', rd_d,
                    '--judgment', jp_d, '--engine-root', ct], cwd=ct)
    a1, a2, a3 = d1.get('data') or {}, d2.get('data') or {}, d3.get('data') or {}
    _newc = {'block_note', 'contract'}
    check('§T2-k2 正式 CLI(research-one --stage attach)回执: 契约门拒收=rc 0'
          '+ok False+attached False+blocked=contract_not_verified+block_note+'
          'contract{verdict,stats}(无判断原文)+validation_passed True+'
          'violations [];成功回执与纪律拒收回执键形不变(无 block_note/contract)',
          rc1 == 0 and d1.get('ok') is False and a1.get('attached') is False
          and a1.get('blocked') == 'contract_not_verified'
          and isinstance(a1.get('block_note'), str) and bool(a1['block_note'])
          and (a1.get('contract') or {}).get('verdict') == 'NOT_VERIFIED'
          and isinstance((a1.get('contract') or {}).get('stats'), dict)
          and set(a1.get('contract') or {}) <= {'verdict', 'stats', 'error'}
          and '窗内' not in json.dumps(a1, ensure_ascii=False)
          and a1.get('validation_passed') is True and a1.get('violations') == []
          and rc2 == 0 and d2.get('ok') is True and a2.get('attached') is True
          and a2.get('blocked') is None and not (_newc & set(a2))
          and rc3 == 0 and d3.get('ok') is False and a3.get('attached') is False
          and not (_newc & set(a3))
          and [v['code'] for v in a3.get('violations') or []]
          == ['POL-EFF-EARLY-CLAIM'],
          f'rc={rc1}/{rc2}/{rc3} '
          f'A={json.dumps(a1, ensure_ascii=False, default=str)[:420]} '
          f'B_keys={sorted(a2)} C_keys={sorted(a3)}')
    rc4, d4 = _cli(['research-attach', '--report-dir', rd_cg,
                    '--judgment', jp_cg], cwd=ct)
    rc5, d5 = _cli(['research-attach', '--report-dir', rd_ok,
                    '--judgment', jp_ok], cwd=ct)
    a4, a5 = d4.get('data') or {}, d5.get('data') or {}
    check('§T2-k3 旧入口 research-attach 回执: 契约门拒收=rc 1+attached False+'
          'blocked=contract_not_verified+block_note+contract;成功回执键形不变',
          rc4 == 1 and d4.get('ok') is False and a4.get('attached') is False
          and a4.get('blocked') == 'contract_not_verified'
          and isinstance(a4.get('block_note'), str) and bool(a4['block_note'])
          and (a4.get('contract') or {}).get('verdict') == 'NOT_VERIFIED'
          and set(a4.get('contract') or {}) <= {'verdict', 'stats', 'error'}
          and rc5 == 0 and a5.get('attached') is True
          and not (_newc & set(a5)),
          f'rc={rc4}/{rc5} A_keys={sorted(a4)} B_keys={sorted(a5)}')
    # 门槛拒收(run_ok=False)优先: 理由仍只有 run_ok_false,不另立契约理由
    t4, rd4, jp4 = _t2_synth_run('t2k_gate', '2026-11-30', stmt_cg)
    rep4 = _t2_attach_res(rd4)
    rep4['run_ok'] = False
    with open(os.path.join(rd4, 'report.json'), 'w', encoding='utf-8') as f:
        json.dump(rep4, f, ensure_ascii=False, indent=2)
    r4 = aj.attach_judgment(rd4, jp4, root=t4)
    rc6, d6 = _cli(['research-one', '--stage', 'attach', '--report-dir', rd4,
                    '--judgment', jp4, '--engine-root', ct], cwd=ct)
    a6 = d6.get('data') or {}
    check('§T2-k4 门槛拒收(run_ok=False)优先且键形不变: blocked=run_ok_false、'
          '无 block_note/contract_summary(契约门不另立理由);CLI 回执同',
          r4.get('attached') is False and r4.get('blocked') == 'run_ok_false'
          and not ({'block_note', 'contract_summary'} & set(r4))
          and rc6 == 0 and d6.get('ok') is False
          and a6.get('blocked') == 'run_ok_false'
          and not (_newc & set(a6)),
          f'r4_keys={sorted(r4)} rc6={rc6} a6_keys={sorted(a6)}')
    import ia_cli as ic
    check('§T2-k5 回执附加键助手: 仅 blocked=contract_* 时附键;None/run_ok_false/'
          '空值返回空 dict(成功/纪律/门槛回执不变)',
          ic._attach_receipt_extra(
              {'blocked': 'contract_not_verified', 'block_note': 'n',
               'contract_summary': {'verdict': 'NOT_VERIFIED'}})
          == {'block_note': 'n', 'contract': {'verdict': 'NOT_VERIFIED'}}
          and ic._attach_receipt_extra({'blocked': None}) == {}
          and ic._attach_receipt_extra({'blocked': 'run_ok_false'}) == {}
          and ic._attach_receipt_extra(None) == {}
          and ic._attach_receipt_extra({}) == {}, '')


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



# ══ 任务3: 真正的原问(逐字件经 --question-file) ══════════════════════════
# 基线 f053afe 正式 CLI 复现(证据包 r33-evidence/t3-baseline): 原问回执
# ok=true/rc=0 而研究计划为空(12 月夹具=0 证据行;真实 11-23 快照=泛宏观
# 总览「问题未词面命中任何指标」)——零事实/缺计划不报缺口。本节核候选:
# 族别与时间分量分记/三面逐行/12 月快照仍守原问 11 月范围/缺口显式回传/
# 席位回声契约/真实步骤正式链。夹具=tests/fixtures_r33(11-23 真实快照的
# 日本/欧元区/美国/中国子集+12 月构造快照;日历=真实日历+合成日银决议)。
T3_MAP_Q = os.path.join(R31_ACC, 'questions', 'question_T3.txt')
T3_JP_ONLY = ('2026年11月，日本的央行当前官方政策目标利率处于什么水平？'
              '最近六个月有无已决议但尚未生效的调整？')
T3_INFL_ONLY = ('2026年11月，日本和欧元区的通胀同比最新读数相比去年同月如何？'
                '请给出具体数据和各数据的公布时间。')
T3_US_CN = T3_TEXT.replace('日本和欧元区', '美国和中国')
FAM_11 = 'family_snapshot_20261123.json'
FAM_DEC = 'family_snapshot_20261215.json'
FAM_CAL_DEC = 'family_calendar_dec.json'


def _jq(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def _kind(q):
    """问句族别(与编排同一实体抽取入口)。"""
    import research_orchestrator as ro
    return rmp.question_kind(q, ro.map_entities(q, wd.load_registry(ROOT)))


def _blk(rep):
    return (rep.get('research_plan') or {}).get('policy_question') or {}


def _row(rows, **kw):
    return next(r for r in rows if all(r.get(k) == v for k, v in kw.items()))


def _codes(blk):
    """分面缺口三元组(排序;None 转字符串免比较崩溃)。"""
    return sorted((g.get('code'), str(g.get('region')), str(g.get('metric_id')))
                  for g in blk.get('gaps') or [])


def _seat(t, rd, out_j, tool=None):
    """席位装配脚本(席位侧脚本;引擎不调用)→ (returncode, judgment|None,
    尾行文本)。判定档写入成功才读取。"""
    if os.path.exists(out_j):
        os.remove(out_j)
    tool = tool or os.path.join(ROOT, 'scripts', 'seat_tools',
                                'make_family_judgment.py')
    r = subprocess.run(
        [sys.executable, tool, t, os.path.join(rd, 'report.json'),
         out_j + '.unused', out_j], capture_output=True, text=True, timeout=900)
    jud = _jq(out_j) if os.path.isfile(out_j) else None
    lines = [x for x in (r.stdout + r.stderr).strip().splitlines()
             if x.strip() and not x.startswith('HEADLINE')]
    return r.returncode, jud, ' | '.join(x[:160] for x in lines[-3:])


def _drop_metrics(p, mids):
    """夹具快照内删指定指标的序列与事实行(构造「该口径缺席」)。"""
    s = _jq(p)
    for m in mids:
        (s.get('series_store') or {}).pop(m, None)
    s['facts'] = [x for x in s.get('facts') or []
                  if x.get('metric_id') not in mids]
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(s, f, ensure_ascii=False)


def _t3_gaps_codes(status_gaps):
    return status_gaps[0], [g['code'] for g in status_gaps[1]]


def sec_t3_a():
    print('═══ 任务3: 真正的原问 ═══')
    print('§T3-a 族别判别与时间分量分记(研究年月/回看窗口/同比基期)')
    check('§T3-a0 原问逐字件 sha256 在册(253 字节;R31 首次为空的那一问)',
          hashlib.sha256(T3_TEXT.encode('utf-8')).hexdigest() == T3_SHA
          and len(T3_TEXT.encode('utf-8')) == 253,
          len(T3_TEXT.encode('utf-8')))
    comp = pq.asked_components(T3_TEXT)
    check('§T3-a1 原问=原问直答型(policy_question);三分量全被问及;研究年月 '
          '2026-11/月末 2026-11-30',
          _kind(T3_TEXT) == 'policy_question'
          and comp == {'policy_targets': True, 'pending_decisions': True,
                       'inflation_yoy': True}
          and pq.research_month(T3_TEXT) == (2026, 11)
          and pq.research_month_end(T3_TEXT) == '2026-11-30',
          f'{_kind(T3_TEXT)} {comp}')
    qt = pq.parse_question_time(T3_TEXT, '2026-11-30')
    qt2 = pq.parse_question_time(T3_TEXT, '2026-11-23')
    check('§T3-a2 时间分量分别解析: 研究年月→研究截止日(月末 11-30);回看窗'
          '「最近六个月」→2026-05-30..2026-11-30(截止日取 11-23 则窗随之);'
          '同比基期「去年同月」;三分量作用面分记',
          qt['research_month'] == '2026-11'
          and qt['research_month_end'] == '2026-11-30'
          and qt['lookback_window'] == {'months': 6, 'from': '2026-05-30',
                                        'to': '2026-11-30',
                                        'source': '最近六个月'}
          and qt2['lookback_window']['from'] == '2026-05-23'
          and qt2['lookback_window']['to'] == '2026-11-23'
          and qt['yoy_base'] == {'kind': 'same_month_last_year',
                                 'source': '去年同月'}
          and qt['applies_to'] == {
              'research_month': ['evidence_as_of'],
              'lookback_window': ['policy_targets', 'pending_decisions'],
              'yoy_base': ['inflation_yoy']},
          json.dumps(qt, ensure_ascii=False))
    with open(T3_MAP_Q, encoding='utf-8') as f:
        q_map = f.read()
    kinds = {k: _kind(q) for k, q in (
        ('map_rephrased', q_map), ('map_t1', Q_T1), ('jp_only', T3_JP_ONLY),
        ('infl_only', T3_INFL_ONLY), ('us_cn', T3_US_CN))}
    ci = pq.asked_components(T3_INFL_ONLY)
    check('§T3-a3 判别边界: R32 改写件(带「通胀与政策环境」形状词)=地图(五面'
          '契约不变);任务1/2 验收问句=地图;单经济体=不入族(既有口径);只问'
          '通胀同比的两地句/美中句=原问直答型(只问通胀=仅通胀分量被问及)',
          kinds == {'map_rephrased': 'map', 'map_t1': 'map', 'jp_only': None,
                    'infl_only': 'policy_question',
                    'us_cn': 'policy_question'}
          and ci == {'policy_targets': False, 'pending_decisions': False,
                     'inflation_yoy': True},
          f'{kinds} {ci}')
    rpm = _plan_on(_family_tree('t3a_map', FAM_11)[0], q_map)
    rpm_plan = rpm.get('research_plan') or {}
    check('§T3-a4 地图问句零回归: R32 改写件计划=地图(question_kind=map,带地图'
          '问句标记),不带原问直答分面块',
          rpm_plan.get('question_kind') == 'map'
          and bool(rpm_plan.get('map_question'))
          and not rpm_plan.get('policy_question'),
          f"{rpm_plan.get('question_kind')} map={bool(rpm_plan.get('map_question'))}")


def sec_t3_b():
    print('§T3-b 三面逐行(11-23 夹具快照+真实发布日历;离线计划)')
    t, _p = _family_tree('t3b', FAM_11)
    rep = _plan_on(t, T3_TEXT)
    rp = rep.get('research_plan') or {}
    blk = _blk(rep)
    ad = rp.get('as_of_declared') or {}
    vb = blk.get('version_binding') or {}
    check('§T3-b0 计划: 族别 policy_question+原问逐字入档+分面块(官方记录源=树内'
          '日历);研究截止=快照实际覆盖日 2026-11-23(请求月末 11-30 晚于覆盖日'
          '→夹紧并如实声明,非静默改判)',
          rp.get('question_kind') == 'policy_question'
          and rp.get('question_verbatim') == T3_TEXT
          and blk.get('schema') == pq.SCHEMA
          and blk.get('as_of') == '2026-11-23'
          and (blk.get('question_time') or {}).get('lookback_window', {})
          .get('from') == '2026-05-23'
          and ad.get('clamped_to_coverage') is True
          and ad.get('requested_as_of') == '2026-11-30'
          and ad.get('scoped_to_question_month') is True
          and str(vb.get('official_record_source') or '').startswith(
              'config/release_calendar.json'),
          f"as_of={blk.get('as_of')} basis={ad.get('basis')}")
    if not blk:
        return
    tgt = blk['policy_targets']['rows']
    pen = blk['pending_decisions']['rows']
    infl = blk['inflation_yoy']['rows']
    jp_t, ea_t = _row(tgt, region='JP'), _row(tgt, region='EA')
    check('§T3-b1 政策目标面: 日本=日历实录 1.25(2026-09-18 决议并公布/09-24 生效/'
          '10-30 确认维持);欧元区=序列+惯例推定(MRO 2.65、DFR 2.5,09-16 生效;决议日'
          '系惯例回推;非官方公布值);行序=问句点名序(日本在前)',
          [r['region'] for r in tgt] == ['JP', 'EA']
          and jp_t.get('status') == 'official_record'
          and jp_t.get('target') == 1.25
          and (jp_t.get('decision_date'), jp_t.get('effective_date'),
               jp_t.get('first_publish'), jp_t.get('last_maintenance'))
          == ('2026-09-18', '2026-09-24', '2026-09-18', '2026-10-30')
          and jp_t.get('decision_basis') == 'calendar_record'
          and [(x['entry_id'], x['kind']) for x in jp_t.get('records') or []]
          == [('RC-JP-BOJ-TARGET-2026-09', 'policy_decision'),
              ('RC-JP-BOJ-MAINT-2026-10', 'policy_maintenance')]
          and ea_t.get('status') == 'series_convention_derived'
          and ea_t.get('target') == 2.65
          and (ea_t.get('decision_date'), ea_t.get('effective_date'))
          == ('2026-09-10', '2026-09-16')
          and ea_t.get('decision_basis') == 'convention:prev_thursday'
          and ea_t.get('official_entry_id') is None
          and sorted((x['metric_id'], x['value'])
                     for x in ea_t.get('series_rows') or [])
          == [('ECB_DFR', 2.5), ('ECB_MRO', 2.65)],
          f"{jp_t.get('status')} {ea_t.get('status')}")
    jp_p, ea_p = _row(pen, region='JP'), _row(pen, region='EA')
    chg = sorted((c['metric_id'], c['date'], c['from'], c['to'], c['delta_bp'])
                 for c in ea_p.get('in_window_changes') or [])
    check('§T3-b2 待生效面(窗 2026-05-23..2026-11-23): 日本=官方实录路径,无待生效'
          '(最近实录 10-30,其后 24 天未确认;未收录≠未发生);窗内已生效决议 1 项+'
          '确认维持 1 项;欧元区=不可核验(无官方实录),窗内序列已生效变动 4 项'
          '(各 +25bp)',
          [r['region'] for r in pen] == ['JP', 'EA']
          and jp_p.get('answer') == 'none_pending'
          and jp_p.get('status') == 'official_record'
          and jp_p.get('pending_at_as_of') == []
          and jp_p.get('confirmed_through') == '2026-10-30'
          and jp_p.get('unconfirmed_days') == 24
          and [d['entry_id'] for d in jp_p.get('in_window_decisions') or []]
          == ['RC-JP-BOJ-TARGET-2026-09']
          and [d['entry_id'] for d in jp_p.get('in_window_maintenance') or []]
          == ['RC-JP-BOJ-MAINT-2026-10']
          and ea_p.get('answer') == 'unverifiable'
          and ea_p.get('status') == 'series_convention_unverifiable'
          and ea_p.get('pending_at_as_of') is None
          and chg == [('ECB_DFR', '2026-06-17', 2.0, 2.25, 25),
                      ('ECB_DFR', '2026-09-16', 2.25, 2.5, 25),
                      ('ECB_MRO', '2026-06-17', 2.15, 2.4, 25),
                      ('ECB_MRO', '2026-09-16', 2.4, 2.65, 25)],
          f"{jp_p.get('answer')}/{ea_p.get('answer')} chg={len(chg)}")
    y0, y1, y2 = infl
    check('§T3-b3 通胀同比面: 日本全国 CPI 2.44(2026-10 观测,公布 11-20)较去年同月 '
          '2.99 低 0.55pp;东京都 2.73(公布 10-30)去年同月基期不在序列→比较不可判'
          '(不以邻近月冒充);欧元区 HICP 4.0(公布 11-16)较去年同月 2.1 高 1.9pp;'
          '公布日=规则推定并逐项标缺口',
          [r['metric_id'] for r in infl]
          == ['JP_CPI_YOY', 'JP_CPI_TOKYO_YOY', 'EA_HICP_YOY']
          and (y0['status'], y0['value'], y0['observation_month'],
               y0['publish_date'], y0['base']['value'], y0['delta_pp'],
               y0['direction'])
          == ('ok', 2.44, '2026-10', '2026-11-20', 2.99, -0.55, 'lower')
          and (y1['status'], y1['value'], y1['observation_month'],
               y1['publish_date'], y1['base']['value'], y1['delta_pp'])
          == ('base_missing', 2.73, '2026-10', '2026-10-30', None, None)
          and (y2['status'], y2['value'], y2['observation_month'],
               y2['publish_date'], y2['base']['value'], y2['delta_pp'],
               y2['direction'])
          == ('ok', 4.0, '2026-10', '2026-11-16', 2.1, 1.9, 'higher')
          and all(r['publish_basis'] == 'rule_estimated'
                  and (r.get('base') or {}).get('kind')
                  == 'same_month_last_year' for r in infl),
          f'{[(r["metric_id"], r["status"], r["value"]) for r in infl]}')
    check('§T3-b4 缺口逐项点名(6 项,披露级;不以相邻口径冒充): 公布日规则推定×3/'
          '东京去年同月基期缺失/欧元区官方实录缺失/待生效不可核验',
          _codes(blk) == sorted([
              ('publication_date_estimated', 'JP', 'JP_CPI_YOY'),
              ('inflation_base_missing', 'JP', 'JP_CPI_TOKYO_YOY'),
              ('publication_date_estimated', 'JP', 'JP_CPI_TOKYO_YOY'),
              ('official_record_missing', 'EA', 'ECB_MRO'),
              ('pending_unverified', 'EA', 'ECB_MRO'),
              ('publication_date_estimated', 'EA', 'EA_HICP_YOY')])
          and pq.blocked_class(blk) is None
          and (blk.get('summary') or {}).get('blocked_class') is None,
          _codes(blk))
    idx = {str(e.get('ref')) for e in rep.get('evidence_index') or []}
    check('§T3-b5 证据索引: 政策实录行(决议/确认维持)+同比基期序列点+东京读数入'
          '索引(席位可引用);版本绑定=研究截止日当日冻结快照(快照值口径)',
          {'POLICY:RC-JP-BOJ-TARGET-2026-09@2026-09-18',
           'POLICY:RC-JP-BOJ-MAINT-2026-10@2026-10-30',
           'JP_CPI_YOY@2025-10-01', 'EA_HICP_YOY@2025-10-01',
           'JP_CPI_TOKYO_YOY@2026-10-01', 'ECB_MRO@2026-09-16',
           'ECB_DFR@2026-09-16'} <= idx
          and vb.get('historical_view') is False
          and (vb.get('value_version') or {}).get('basis') == 'snapshot_vintage'
          and (vb.get('series') or {}).get('JP_CPI_YOY', {}).get('n_kept') == 70
          and (vb.get('series') or {}).get('ECB_MRO', {}).get('n_kept') == 48,
          sorted(idx))
    gap_note = next((g.get('note') for g in rp.get('dimension_gaps') or []
                     if g.get('metric_id') == 'JP_POLICY_TARGET'), '')
    md = open(os.path.join(rep.get('report_dir') or '', 'report.md'),
              encoding='utf-8').read()
    check('§T3-b6 工单: 宣布值口径序列格缺口照列(检索范围+影响照写)并写明去处——'
          '官方目标水平由日历实录回答,不读成「日本政策目标不可得」',
          'registry_absent' in {g.get('gap')
                                for g in rp.get('dimension_gaps') or []}
          and '检索范围' in gap_note and '影响' in gap_note
          and '原问直答型: 本缺口仅指宣布值口径的序列面格' in gap_note
          and gap_note in md,
          gap_note[-80:])


def sec_t3_c():
    print('§T3-c 12 月快照重跑仍守原问 11 月范围;截止后回填不入面;缺历史版本标缺证')
    base = _jq(os.path.join(FIX_R33, FAM_DEC))
    t, _p = _family_tree('t3c', FAM_DEC, FAM_CAL_DEC)
    rep = _plan_on(t, T3_TEXT)
    rp = rep.get('research_plan') or {}
    blk = _blk(rep)
    ad = rp.get('as_of_declared') or {}
    vb = blk.get('version_binding') or {}
    check('§T3-c0 研究截止日=原问研究月末 2026-11-30(早于快照版本日 2026-12-15: '
          '原问月范围优先于快照版本日;与快照不一致如实声明),不随快照漂到 12 月',
          blk.get('as_of') == '2026-11-30'
          and ad.get('scoped_to_question_month') is True
          and ad.get('clamped_to_coverage') is False
          and ad.get('differs_from_snapshot') is True
          and ad.get('snapshot_target_date') == '2026-12-15'
          and (blk.get('question_time') or {}).get('lookback_window')
          == {'months': 6, 'from': '2026-05-30', 'to': '2026-11-30',
              'source': '最近六个月'}
          and vb.get('source_target_date') == '2026-12-15',
          f"as_of={blk.get('as_of')} {ad.get('note')}")
    if not blk:
        return
    jp_p = _row(blk['pending_decisions']['rows'], region='JP')
    jp_t = _row(blk['policy_targets']['rows'], region='JP')
    pend = jp_p.get('pending_at_as_of') or []
    check('§T3-c1 截止日后才生效的已决议调整=待生效(合成日银决议 11-27 决议并公布/'
          '12-04 生效,目标 1.5);现行目标仍 1.25(待生效不改现行水平);窗内已生效'
          '决议仍只列 09-18 一项(12 月才生效的决议不得列为已生效)',
          jp_p.get('answer') == 'pending'
          and [(x['entry_id'], x['first_publish'], x['effective_on'],
                x['target_value']) for x in pend]
          == [('RC-JP-BOJ-TARGET-2026-11', '2026-11-27', '2026-12-04', 1.5)]
          and jp_t.get('target') == 1.25
          and jp_t.get('effective_date') == '2026-09-24'
          and [d['entry_id'] for d in jp_p.get('in_window_decisions') or []]
          == ['RC-JP-BOJ-TARGET-2026-09'],
          f"{jp_p.get('answer')} n={len(pend)}")
    ser = vb.get('series') or {}
    fd = (ser.get('JP_POLICY_RATE') or {}).get('first_dropped') or {}
    yy = {r['metric_id']: r for r in blk['inflation_yoy']['rows']}
    check('§T3-c2 截止后回填不入面: 11 月观测、12 月才公布的日本政策利率月均/全国 CPI '
          '被剔(逐序列计数+首剔行);11-29 已公布的东京 11 月读数入面',
          (ser.get('JP_POLICY_RATE') or {}).get('n_in') == 497
          and (ser.get('JP_POLICY_RATE') or {}).get('n_kept') == 496
          and (ser.get('JP_POLICY_RATE') or {}).get('n_late_publication') == 1
          and fd.get('date') == '2026-11-01'
          and fd.get('reason') == 'late_publication'
          and fd.get('publish') == '2026-12-05'
          and (ser.get('JP_CPI_YOY') or {}).get('n_in') == 71
          and (ser.get('JP_CPI_YOY') or {}).get('n_kept') == 70
          and (yy['JP_CPI_YOY']['observation_month'],
               yy['JP_CPI_YOY']['value']) == ('2026-10', 2.44)
          and (yy['JP_CPI_TOKYO_YOY']['observation_month'],
               yy['JP_CPI_TOKYO_YOY']['value'],
               yy['JP_CPI_TOKYO_YOY']['publish_date'])
          == ('2026-11', 2.6, '2026-11-29'),
          {m: (x.get('n_in'), x.get('n_kept')) for m, x in ser.items()})
    check('§T3-c3 缺历史版本标缺证: 无 2026-11-30 当日冻结快照→顶层一行+声明修订口径'
          '序列(日本全国 CPI/欧元区 HICP)逐条 historical_version_missing;值版本=较晚'
          '快照的截止视图(声明修订口径的序列=最新修订值,非当时首发值)',
          [c for c in _codes(blk) if c[0] == 'historical_version_missing']
          == [('historical_version_missing', 'EA', 'EA_HICP_YOY'),
              ('historical_version_missing', 'JP', 'JP_CPI_YOY'),
              ('historical_version_missing', 'None', 'None')]
          and len(_codes(blk)) == 9
          and vb.get('historical_view') is True
          and (vb.get('value_version') or {}).get('basis')
          == 'no_asof_vintage_snapshot'
          and (vb.get('value_version') or {}).get('revised_series')
          == ['EA_HICP_YOY', 'JP_CPI_YOY']
          and all('最新修订值' in yy[m]['vintage']
                  and '非当时首发值' in yy[m]['vintage']
                  for m in ('JP_CPI_YOY', 'EA_HICP_YOY')),
          (vb.get('value_version') or {}).get('basis'))
    # 截止日后才公布的决议不可见
    cp = os.path.join(t, 'config', 'release_calendar.json')
    cal = _jq(cp)
    hit = 0
    for e in cal['entries']:
        if e.get('entry_id') == 'RC-JP-BOJ-TARGET-2026-11':
            hit += 1
            e.update(decision_date='2026-12-01', obs_from='2026-12-01',
                     not_published_as_of='2026-11-30',
                     first_publish_on_or_after='2026-12-01',
                     effective_on='2026-12-09')
    with open(cp, 'w', encoding='utf-8') as f:
        json.dump(cal, f, ensure_ascii=False)
    jp_p2 = _row(_blk(_plan_on(t, T3_TEXT))['pending_decisions']['rows'],
                 region='JP')
    check('§T3-c4 决议在研究截止日之后才公布→不可见(待生效=无,确认覆盖至 10-30;'
          '不得把后来公布的决议写进当时结论)',
          hit == 1
          and jp_p2.get('answer') == 'none_pending'
          and jp_p2.get('pending_at_as_of') == []
          and jp_p2.get('confirmed_through') == '2026-10-30'
          and jp_p2.get('unconfirmed_days') == 31,
          f"{jp_p2.get('answer')} {jp_p2.get('confirmed_through')}")
    # 有 as-of 版本快照→绑定当日版本,缺证行消失
    t2, _p2 = _family_tree('t3c_v', FAM_DEC, FAM_CAL_DEC)
    _vintage(t2, '20261130', base=base)
    blk3 = _blk(_plan_on(t2, T3_TEXT))
    vb3 = blk3.get('version_binding') or {}
    jp_p3 = _row(blk3['pending_decisions']['rows'], region='JP')
    check('§T3-c5 数据树有研究截止日当日冻结快照→事实/序列/派生值绑定该版本(值版本='
          'as-of 版本快照;晚公布观测已不在该版本内),缺历史版本行不再出现;政策实录'
          '仍走日历(待生效决议照列)',
          not [c for c in _codes(blk3)
               if c[0] == 'historical_version_missing']
          and (vb3.get('value_version') or {}).get('basis') == 'as_of_vintage'
          and (vb3.get('value_version') or {}).get('vintage_snapshot_id')
          == 'FIXTURE_research_snapshot_20261130'
          and (vb3.get('series') or {}).get('JP_POLICY_RATE', {})
          .get('n_kept') == 496
          and (vb3.get('series') or {}).get('JP_CPI_YOY', {}).get('n_kept')
          == 70
          and jp_p3.get('answer') == 'pending',
          (vb3.get('value_version') or {}).get('basis'))


def sec_t3_d():
    print('§T3-d 零事实/缺必要计划/被问分量无证据→缺口显式回传(plan 段)')
    import ia_cli
    got = {}
    # 零事实: 快照序列与事实行全空,日历亦无实录可引
    t, p = _family_tree('t3d_zero', FAM_11)
    s = _jq(p)
    s['series_store'], s['facts'] = {}, []
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(s, f, ensure_ascii=False)
    with open(os.path.join(t, 'config', 'release_calendar.json'), 'w',
              encoding='utf-8') as f:
        json.dump({'version': 'fixture', 'entries': []}, f)
    rep0 = _plan_on(t, T3_TEXT)
    got['zero'] = _t3_gaps_codes(ia_cli._r1_plan_gaps(rep0))
    got['plan_missing'] = _t3_gaps_codes(ia_cli._r1_plan_gaps(
        {'evidence_index': [], 'research_plan': None, 'steps': []}))
    rep_x = dict(rep0, research_plan=dict(
        rep0.get('research_plan') or {}, policy_question=None))
    got['faces'] = _t3_gaps_codes(ia_cli._r1_plan_gaps(rep_x))
    check('§T3-d1 零事实→plan_status=gap: zero_facts(hard);无研究计划且零指标→'
          'plan_missing(hard);分面块缺席/损坏→policy_question_faces_missing(hard)'
          '(基线: 同形零事实问句回执 ok=true/rc=0 且不报缺口)',
          got['zero'][0] == 'gap' and got['zero'][1][0] == 'zero_facts'
          and got['plan_missing'] == (
              'gap', ['zero_facts', 'plan_missing'])
          and got['faces'][0] == 'gap'
          and 'policy_question_faces_missing' in got['faces'][1],
          json.dumps(got, ensure_ascii=False))
    # 被问分量无证据(通胀读数全缺;日本目标仍有日历实录)→草稿级缺口显式回传
    t2, p2 = _family_tree('t3d_face', FAM_11)
    _drop_metrics(p2, ('JP_CPI_YOY', 'JP_CPI_TOKYO_YOY', 'EA_HICP_YOY'))
    rep2 = _plan_on(t2, T3_TEXT)
    blk2 = _blk(rep2)
    st2, gaps2 = ia_cli._r1_plan_gaps(rep2)
    check('§T3-d2 被问及的分量无证据可答(三地通胀序列缺席→读数全缺;政策目标仍有'
          '日历实录)→缺口显式回传(policy_question_face_missing,草稿级: 只能交付草稿,'
          '正式归档拒绝);逐行 inflation_reading_missing',
          st2 == 'ok'
          and [g['code'] for g in gaps2] == ['policy_question_face_missing']
          and gaps2[0]['severity'] == 'draft'
          and pq.blocked_class(blk2) == 'policy_question_face_missing'
          and all(r['status'] == 'missing' and r['value'] is None
                  for r in blk2['inflation_yoy']['rows'])
          and ('inflation_reading_missing', 'JP', 'JP_CPI_YOY') in _codes(blk2),
          f"st={st2} {[g['code'] for g in gaps2]}")
    # 政策目标缺证(欧元区政策序列缺席,无日历实录)→同属草稿级
    t3, p3 = _family_tree('t3d_pol', FAM_11)
    _drop_metrics(p3, ('ECB_MRO', 'ECB_DFR'))
    rep3 = _plan_on(t3, T3_TEXT)
    blk3 = _blk(rep3)
    rc3, jud3, tail3 = _seat(t3, rep3.get('report_dir'),
                             os.path.join(TMPG, 't3d_pol_judgment.json'))
    check('§T3-d3 政策目标缺证(欧元区政策序列缺席且无官方实录)→草稿级缺口+'
          'policy_target_missing/policy_series_missing;席位装配脚本仍可出草稿判定'
          '(交付草稿,归档层拒)',
          pq.blocked_class(blk3) == 'policy_question_face_missing'
          and _t3_gaps_codes(ia_cli._r1_plan_gaps(rep3)) == (
              'ok', ['policy_question_face_missing'])
          and _row(blk3['policy_targets']['rows'], region='EA').get('status')
          == 'missing'
          and {('policy_target_missing', 'EA', 'ECB_MRO'),
               ('policy_series_missing', 'EA', 'ECB_MRO')} <= set(_codes(blk3))
          and rc3 == 0 and bool(jud3),
          f'rc={rc3} {tail3[:160]}')
    # 全缺时席位装配脚本失败关闭(不落判定档)
    rc_x, jud_x, tail_x = _seat(t2, rep2.get('report_dir'),
                                os.path.join(TMPG, 't3d_face_judgment.json'))
    check('§T3-d4 通胀读数全缺: 席位装配脚本失败关闭(不落判定档;须席位另写)',
          rc_x != 0 and jud_x is None
          and not os.path.exists(os.path.join(TMPG, 't3d_face_judgment.json')),
          tail_x[:200])


def sec_t3_e():
    print('§T3-e 席位回声契约(11-23 视图;离线计划+席位装配脚本)')
    from research_contract import judgment_contract as jc
    t, _p = _family_tree('t3e', FAM_11)
    rep = _plan_on(t, T3_TEXT)
    jp = os.path.join(TMPG, 't3e_judgment.json')
    rc, jud, tail = _seat(t, rep.get('report_dir'), jp)
    ok0, p0, res = _pol_codes_j(jud or {}, rep, os.path.join(
        t, 'config', 'release_calendar.json'), '2026-11-23')
    con = jc.verify_judgment(jud, rep) if jud else {}
    fam = con.get('map_checks') or []
    check('§T3-e0 席位装配脚本: 纪律通过+契约 VERIFIED(分面核对≥60)+整档零政策'
          '违规;回声与引擎面逐位一致(研究时点/官方目标/待生效/通胀同比/缺口回声)',
          rc == 0 and res['passed'] and p0 == []
          and con.get('verdict') == 'VERIFIED' and len(fam) >= 60
          and (con.get('stats') or {}).get('unbound') == 0
          and (jud['reader_map']['policy_question'].get('research_time')
               == {'as_of': '2026-11-23', 'research_month': '2026-11'})
          and [(r['region'], r['status'], r['target'])
               for r in jud['reader_map']['policy_question']['official_targets']]
          == [(r['region'], r['status'], r['target'])
              for r in _blk(rep)['policy_targets']['rows']]
          and [(r['region'], r['answer'])
               for r in jud['reader_map']['policy_question']['pending_decisions']]
          == [(r['region'], r['answer'])
              for r in _blk(rep)['pending_decisions']['rows']]
          and [(r['metric_id'], r['value'], r['base_value'], r['delta_pp'])
               for r in jud['reader_map']['policy_question']['inflation_yoy']]
          == [(r['metric_id'], r['value'], r['base']['value'], r['delta_pp'])
              for r in _blk(rep)['inflation_yoy']['rows']]
          and sorted((g['code'], str(g['region']), str(g['metric_id']))
                     for g in jud['reader_map']['policy_question']['gaps_echoed'])
          == _codes(_blk(rep)),
          f'rc={rc} con={con.get("verdict")} fam={len(fam)} {tail[:160]}')
    if not jud:
        return

    def _bad_items(j):
        c = jc.verify_judgment(j, rep)
        return (c['verdict'],
                {x['item']: x['status'] for x in c['map_checks']
                 if x['status'] != 'VERIFIED'})
    j1 = copy.deepcopy(jud)
    j1['reader_map']['policy_question']['inflation_yoy'][0]['value'] = 2.45
    j2 = copy.deepcopy(jud)
    j2['reader_map']['policy_question']['pending_decisions'][0]['pending'] = [
        {'region': 'JP', 'target': 1.5, 'decision_date': '2026-11-20',
         'effective_date': '2026-12-04'}]
    j3 = copy.deepcopy(jud)
    j3['reader_map']['policy_question']['gaps_echoed'] = [
        g for g in j3['reader_map']['policy_question']['gaps_echoed']
        if g.get('code') != 'inflation_base_missing']
    v1, b1 = _bad_items(j1)
    v2, b2 = _bad_items(j2)
    v3, b3 = _bad_items(j3)
    it_v = ('reader_map.policy_question.inflation_yoy'
            '[JP:JP_CPI_YOY].value')
    it_p = 'reader_map.policy_question.pending_decisions[JP].pending'
    check('§T3-e1 回声契约反例(纯函数): 回声值扰动(2.44→2.45)=CONTRADICTED;虚构待生效'
          '决定=CONTRADICTED;漏回声一条缺口=NOT_VERIFIED',
          v1 == 'CONTRADICTED' and b1.get(it_v) == 'CONTRADICTED'
          and v2 == 'CONTRADICTED' and b2.get(it_p) == 'CONTRADICTED'
          and v3 == 'NOT_VERIFIED'
          and b3.get('reader_map.policy_question.gaps_echoed')
          == 'NOT_VERIFIED',
          json.dumps([v1, b1, v2, b2, v3, b3], ensure_ascii=False))


def sec_t3_f():
    print('§T3-f 席位装配脚本守卫与单行情景')
    # a. 问句点名经济体非日本/欧元区(夹具无美中政策序列)→守卫,不落判定档
    t_us, _p = _family_tree('t3f_us', FAM_11)
    rep_us = _plan_on(t_us, T3_US_CN)
    jp_us = os.path.join(TMPG, 't3f_us_judgment.json')
    rc_us, jud_us, tail_us = _seat(t_us, rep_us.get('report_dir'), jp_us)
    check('§T3-f1 守卫: 问句点名经济体非日本/欧元区(夹具无美中政策序列)→席位装配'
          '脚本拒出(rc≠0,不落判定档);计划层照常出分面块',
          rc_us != 0 and jud_us is None
          and not os.path.exists(jp_us)
          and _blk(rep_us).get('schema') == pq.SCHEMA
          and [r['region'] for r in _blk(rep_us)['policy_targets']['rows']]
          == ['US', 'CN'],
          tail_us[:200])
    # b. 报告件分面块 as_of 缺失→守卫
    t2, _p2 = _family_tree('t3f_asof', FAM_11)
    rep2 = _plan_on(t2, T3_TEXT)
    rj_x = os.path.join(TMPG, 't3f_asof_report.json')
    rj = _jq(os.path.join(rep2.get('report_dir') or '', 'report.json'))
    rj['research_plan']['policy_question']['as_of'] = None
    with open(rj_x, 'w', encoding='utf-8') as f:
        json.dump(rj, f, ensure_ascii=False)
    jp_x = os.path.join(TMPG, 't3f_asof_judgment.json')
    r = subprocess.run(
        [sys.executable, os.path.join(ROOT, 'scripts', 'seat_tools',
                                      'make_family_judgment.py'), t2, rj_x,
         jp_x + '.unused', jp_x], capture_output=True, text=True, timeout=900)
    check('§T3-f2 守卫: 分面块研究截止日缺失→席位装配脚本拒出(rc≠0,不落判定档)',
          r.returncode != 0 and not os.path.exists(jp_x),
          (r.stdout + r.stderr).strip()[-200:])
    # c. 单行情景: 日本全国 CPI 序列缺席→通胀面只剩可判一行,情景不带次级指标
    t3, p3 = _family_tree('t3f_single', FAM_11)
    _drop_metrics(p3, ('JP_CPI_YOY',))
    rep3 = _plan_on(t3, T3_TEXT)
    jp3 = os.path.join(TMPG, 't3f_single_judgment.json')
    rc3, jud3, tail3 = _seat(t3, rep3.get('report_dir'), jp3)
    sc = ((jud3 or {}).get('l4') or {}).get('scenarios') or []
    check('§T3-f3 单行情景: 日本全国 CPI 序列缺席(东京基期不可判)→通胀面可判行仅'
          '欧元区 HICP 一行,席位装配脚本照出判定,情景不带次级指标',
          rc3 == 0 and bool(jud3) and len(sc) >= 2
          and all('secondary_metric_ids' not in x for x in sc)
          and [r['status'] for r in _blk(rep3)['inflation_yoy']['rows']]
          == ['missing', 'base_missing', 'ok'],
          f'rc={rc3} n={len(sc)} {tail3[:160]}')


def sec_t3_g():
    print('§T3-g 正式 CLI 链(真实步骤;--question-file 逐字件)')
    if os.environ.get('IA_R33_GATE_SKIP_CLI') == '1':
        print('  (IA_R33_GATE_SKIP_CLI=1: 正式 CLI 段跳过)')
        return
    qf = os.path.join(TMPG, 'q_t3.txt')
    with open(qf, 'w', encoding='utf-8') as fh:
        fh.write(T3_TEXT)

    def one(tag, snapshot, calendar=None):
        return _family_tree(tag, snapshot, calendar, code=True)[0]

    # ── g1. 11-23 视图: plan → 席位装配脚本 → attach(拒收/接收)→ report → archive
    t = one('t3g_11', FAM_11)
    cal = os.path.join(t, 'config', 'release_calendar.json')
    rc_p, d_p = _cli(['research-one', '--stage', 'plan', '--question-file',
                      qf, '--engine-root', t], cwd=t)
    dd = d_p.get('data') or {}
    rd = dd.get('report_dir') or ''
    rj = _jq(os.path.join(rd, 'report.json')) if os.path.isfile(
        os.path.join(rd, 'report.json')) else {}
    env = _jq(os.path.join(rd, 'AGENT_SEAT_ENVELOPE.json')) if os.path.isfile(
        os.path.join(rd, 'AGENT_SEAT_ENVELOPE.json')) else {}
    steps = rj.get('steps') or []
    bad_steps = [s['step'] for s in steps
                 if not s.get('executed') or (s.get('ok') is False
                                              and not s.get('honest_refusal'))]
    check('§T3-g1 正式 CLI plan(真实步骤;逐字件): rc=0/ok=true/run_ok=true/plan_status='
          'ok/plan_gaps=[](基线=空计划不报缺口);步骤全部执行(失败步仅诚实拒答);席位'
          '信封 question=逐字件字节、question_kind=policy_question',
          rc_p == 0 and d_p.get('ok') is True and dd.get('run_ok') is True
          and dd.get('plan_status') == 'ok' and dd.get('plan_gaps') == []
          and rd.startswith(t) and len(steps) >= 10 and not bad_steps
          and env.get('question') == T3_TEXT
          and env.get('question_kind') == 'policy_question'
          and (rj.get('research_plan') or {}).get('question_kind')
          == 'policy_question'
          and bool((rj.get('research_plan') or {}).get('policy_question')),
          f"rc={rc_p} ok={d_p.get('ok')} steps={len(steps)} bad={bad_steps} "
          f"next={str(dd.get('next'))[:120]}")
    if not rd:
        return
    jp = os.path.join(TMPG, 't3g_judgment.json')
    rc_s, jud, tail_s = _seat(
        t, rd, jp, tool=os.path.join(t, 'scripts', 'seat_tools',
                                     'make_family_judgment.py'))
    jp_bad = os.path.join(TMPG, 't3g_judgment_pert.json')
    j_bad = copy.deepcopy(jud) if jud else None
    if j_bad:
        j_bad['reader_map']['policy_question']['inflation_yoy'][0]['value'] = 2.45
        with open(jp_bad, 'w', encoding='utf-8') as fh:
            json.dump(j_bad, fh, ensure_ascii=False)
    rc_b, d_b = _cli(['research-one', '--stage', 'attach', '--question-file',
                      qf, '--report-dir', rd, '--judgment', jp_bad,
                      '--engine-root', t], cwd=t)
    db = d_b.get('data') or {}
    rjb = _jq(os.path.join(rd, 'report.json'))
    cvb = ((rjb.get('agent_judgment') or {}).get('contract_verification') or {})
    it_v = ('reader_map.policy_question.inflation_yoy[JP:JP_CPI_YOY].value')
    st_b = {x['item']: x['status'] for x in cvb.get('map_checks') or []}
    check('§T3-g2 正式 CLI attach 拒收回声扰动(日本全国 CPI 2.44→2.45): rc=0(冻结'
          '契约 R18 §D: 拒收读信封不读 rc)/ok=False/attached=False/violations 点名;'
          'L3/L4 不落位(produced=False);契约=CONTRADICTED 且点名该格',
          rc_s == 0 and bool(jud) and rc_b == 0 and d_b.get('ok') is False
          and db.get('attached') is False
          and cvb.get('verdict') == 'CONTRADICTED'
          and st_b.get(it_v) == 'CONTRADICTED'
          and (rjb.get('layers') or {}).get('L3_AI推断层', {}).get('produced')
          is False
          and not os.path.exists(os.path.join(rd, 'agent_judgment.json')),
          f"seat rc={rc_s} {tail_s[:120]} | attach rc={rc_b} "
          f"cv={cvb.get('verdict')} {str(d_b.get('error'))[:160]}")
    rc_a, d_a = _cli(['research-one', '--stage', 'attach', '--question-file',
                      qf, '--report-dir', rd, '--judgment', jp,
                      '--engine-root', t], cwd=t)
    da = d_a.get('data') or {}
    rja = _jq(os.path.join(rd, 'report.json'))
    check('§T3-g3 正式 CLI attach 接收正确回声(拒收后同目录重提): rc=0/attached='
          'True/违规=[];判定档副本落位且=席位件;L3/L4 落位;整档分类=None',
          rc_a == 0 and d_a.get('ok') is True and da.get('attached') is True
          and da.get('violations') == []
          and os.path.isfile(os.path.join(rd, 'agent_judgment.json'))
          and _jq(os.path.join(rd, 'agent_judgment.json')) == jud
          and (rja.get('layers') or {}).get('L3_AI推断层', {}).get('produced')
          is True
          and aj.blocked_class_of(rja, calendar_path=cal) is None,
          f"rc={rc_a} attached={da.get('attached')} viol={da.get('violations')}")
    rc_r, d_r = _cli(['research-one', '--stage', 'report', '--question-file',
                      qf, '--report-dir', rd, '--engine-root', t], cwd=t)
    dr = d_r.get('data') or {}
    mdp = os.path.join(rd, 'MAP_REPORT.md')
    md = open(mdp, encoding='utf-8').read() if os.path.isfile(mdp) else ''
    rjr = _jq(os.path.join(rd, 'report.json'))
    sha_ok = False
    sp = os.path.join(rd, 'MAP_REPORT.sha256')
    if os.path.isfile(sp):
        with open(sp, encoding='utf-8') as fh:
            sha_ok = hashlib.sha256(md.encode('utf-8')).hexdigest() \
                in fh.read()
    vbf = open(os.path.join(rd, 'question_verbatim.txt'), 'rb').read() if \
        os.path.isfile(os.path.join(rd, 'question_verbatim.txt')) else b''
    check('§T3-g4 正式 CLI report(独立审查待裁): rc=1/generated=true/deliverable='
          'false;读者报告=三面表格+时间分量+缺口+版本绑定+席位原文;页眉数据门行'
          '写明「当日采集面」并附本问指标两面对照(东京 CPI 当日采集缺席而序列面有'
          '读数/欧央行两利率降级);原问逐字随包;摘要锚在册',
          rc_r == 1 and dr.get('generated') is True
          and dr.get('deliverable') is False
          and '## 政策目标' in md and '## 已决议但尚未生效的调整' in md
          and '## 通胀同比' in md and '## 缺口' in md
          and '## 版本绑定' in md
          and '## 研究时点与问句时间分量(分别解析)' in md
          and '## Agent 席判断' in md
          and '| 日本 |' in md and '| 1.25 | 2026-09-18 | 2026-09-24 |'
          in md and '| 2.44 |' in md and '| 2.73 |' in md
          and '采集面缺席/降级的当日事实不入证据面;本问改取序列面读数的指标见'
          '下行两面对照' in md
          and '  - 本问指标两面对照(Gate A=当日采集面;三面取快照序列面 '
          'series_store,同指标两面状态可不同): ' in md
          and 'JP_CPI_TOKYO_YOY 当日采集面缺席' in md
          and 'ECB_MRO 当日采集面降级' in md
          and '缺席/降级数据不得进入研究结论' not in md
          and rjr['run']['question'] == T3_TEXT
          and vbf == T3_TEXT.encode('utf-8')
          and sha_ok,
          f"rc={rc_r} len={len(md)} sha={sha_ok}")
    arc = os.path.join(TMPG, 't3g_arc')
    rc_arc, d_arc = _cli(['research-one', '--stage', 'archive',
                          '--question-file', qf, '--report-dir', rd,
                          '--archive-dir', arc, '--engine-root', t], cwd=t)
    check('§T3-g5 正式归档(独立审查缺席)拒绝: rc≠0/ok=False,隔离归档目录无新件',
          rc_arc != 0 and d_arc.get('ok') is False
          and (not os.path.exists(arc) or not os.listdir(arc)),
          f"rc={rc_arc} "
          f"{json.dumps(d_arc.get('data') or d_arc.get('error'), ensure_ascii=False)[:240]}")

    # ── g6. 12 月安装树正式 plan: 仍守原问 11 月范围
    t6 = one('t3g_dec', FAM_DEC, FAM_CAL_DEC)
    rc6, d6 = _cli(['research-one', '--stage', 'plan', '--question-file',
                    qf, '--engine-root', t6], cwd=t6)
    dd6 = d6.get('data') or {}
    rd6 = dd6.get('report_dir') or ''
    rj6 = _jq(os.path.join(rd6, 'report.json')) if os.path.isfile(
        os.path.join(rd6, 'report.json')) else {}
    rp6 = rj6.get('research_plan') or {}
    check('§T3-g6 12 月安装树正式 plan(真实步骤): 研究截止日仍=原问研究月末 '
          '2026-11-30(run.evidence_asof;快照版本日 2026-12-15);待生效面列 12-04 '
          '生效的决议;rc=0/plan_status=ok',
          rc6 == 0 and d6.get('ok') is True
          and (rj6.get('run') or {}).get('evidence_asof') == '2026-11-30'
          and dd6.get('plan_status') == 'ok'
          and (rp6.get('as_of_declared') or {})
          .get('scoped_to_question_month') is True
          and (rp6.get('policy_question') or {}).get('as_of') == '2026-11-30'
          and _row((rp6.get('policy_question') or {}).get(
              'pending_decisions', {}).get('rows') or [],
              region='JP').get('answer') == 'pending',
          f"rc={rc6} asof={(rj6.get('run') or {}).get('evidence_asof')} "
          f"{str(dd6.get('plan_gaps'))[:160]}")

    # ── g7. 零事实安装树: plan 段 rc=1/ok=False,缺口点名
    t7 = one('t3g_zero', FAM_11)
    p7 = os.path.join(t7, 'data', 'daily',
                      '%s.json' % _jq(os.path.join(FIX_R33, FAM_11))
                      ['snapshot_id'])
    s7 = _jq(p7)
    s7['series_store'], s7['facts'] = {}, []
    with open(p7, 'w', encoding='utf-8') as f:
        json.dump(s7, f, ensure_ascii=False)
    with open(os.path.join(t7, 'config', 'release_calendar.json'), 'w',
              encoding='utf-8') as f:
        json.dump({'version': 'fixture', 'entries': []}, f)
    rc7, d7 = _cli(['research-one', '--stage', 'plan', '--question-file',
                    qf, '--engine-root', t7], cwd=t7)
    dd7 = d7.get('data') or {}
    gaps7 = dd7.get('plan_gaps') or []
    check('§T3-g7 零事实安装树正式 plan: rc=1/ok=False/plan_status=gap,plan_gaps 首项='
          'zero_facts(基线同形回执 ok=true/rc=0);next 点名缺口',
          rc7 == 1 and d7.get('ok') is False
          and dd7.get('plan_status') == 'gap'
          and gaps7 and gaps7[0]['code'] == 'zero_facts'
          and '零事实' in str(dd7.get('next')),
          f"rc={rc7} ok={d7.get('ok')} {json.dumps(gaps7, ensure_ascii=False)[:200]}")

    # ── g8. 草稿级安装树(欧元区政策序列缺席): plan 草稿缺口 → 席位草稿判定
    #      → attach → report(待裁 rc=1;合成裁决落档后=草稿交付 draft_delivered
    #      =true,分段 report 的 rc 随正式交付=false 仍为 1)→ 正式归档拒绝。
    #      合成裁决仅门内夹具(隔离树,非正式验收)。
    t8 = one('t3g_draft', FAM_11)
    cal8 = os.path.join(t8, 'config', 'release_calendar.json')
    p8 = os.path.join(t8, 'data', 'daily',
                      '%s.json' % _jq(os.path.join(FIX_R33, FAM_11))
                      ['snapshot_id'])
    _drop_metrics(p8, ('ECB_MRO', 'ECB_DFR'))
    rc8, d8 = _cli(['research-one', '--stage', 'plan', '--question-file',
                    qf, '--engine-root', t8], cwd=t8)
    dd8 = d8.get('data') or {}
    rd8 = dd8.get('report_dir') or ''
    rj8 = _jq(os.path.join(rd8, 'report.json')) if os.path.isfile(
        os.path.join(rd8, 'report.json')) else {}
    s_cmp = next((x for x in rj8.get('steps') or []
                  if x.get('step') == 'S5_compare'), {})
    gaps8 = dd8.get('plan_gaps') or []
    check('§T3-g8a 草稿级安装树 plan(真实步骤;欧元区两利率序列缺席): plan_gaps='
          '[policy_question_face_missing(草稿级)];命中前 2 序列缺席时 compare '
          '顺延取在场指标、不再硬跑必败步骤(run_ok=true;此前 S5 必败→run_ok='
          'false→attach 须 --allow-failed-run 才可续)',
          rc8 == 0 and d8.get('ok') is True
          and [g['code'] for g in gaps8] == ['policy_question_face_missing']
          and gaps8[0].get('severity') == 'draft'
          and dd8.get('run_ok') is True and rj8.get('run_ok') is True
          and s_cmp.get('executed') is True and s_cmp.get('ok') is True
          and '序列缺席' in str(s_cmp.get('note'))
          and '顺延' in str(s_cmp.get('note'))
          and '草稿级' in str(dd8.get('next')),
          f"rc={rc8} run_ok={dd8.get('run_ok')} gaps={json.dumps(gaps8, ensure_ascii=False)[:160]} "
          f"compare note={str(s_cmp.get('note'))[:160]}")
    jp8 = os.path.join(TMPG, 't3g_draft_judgment.json')
    rc_s8, jud8, tail8 = _seat(
        t8, rd8, jp8, tool=os.path.join(t8, 'scripts', 'seat_tools',
                                        'make_family_judgment.py'))
    rc_a8, d_a8 = _cli(['research-one', '--stage', 'attach', '--question-file',
                        qf, '--report-dir', rd8, '--judgment', jp8,
                        '--engine-root', t8], cwd=t8)
    rc_r8, d_r8 = _cli(['research-one', '--stage', 'report', '--question-file',
                        qf, '--report-dir', rd8, '--engine-root', t8], cwd=t8)
    dr8 = d_r8.get('data') or {}
    # 合成裁决(仅门内夹具: 隔离树,非正式验收)——走与真实席位同一落档接口
    vp8 = aj.record_semantic_verdict(
        t8, rd8, 'UPHELD', 'R33-SYNTHETIC-ISOLATED-TEST',
        notes='门内夹具合成裁决(隔离树;仅验草稿交付路径,非正式验收)')
    rc_r8b, d_r8b = _cli(['research-one', '--stage', 'report', '--question-file',
                          qf, '--report-dir', rd8, '--engine-root', t8], cwd=t8)
    dr8b = d_r8b.get('data') or {}
    arc8 = os.path.join(TMPG, 't3g_arc_draft')
    rc_x8, d_x8 = _cli(['research-one', '--stage', 'archive',
                        '--question-file', qf, '--report-dir', rd8,
                        '--archive-dir', arc8, '--engine-root', t8], cwd=t8)
    rj8b = _jq(os.path.join(rd8, 'report.json'))
    check('§T3-g8b 草稿链: 席位装配脚本出草稿判定(欧元区目标=缺证);attach '
          '接收;report 待裁(rc=1,blocked_class=policy_question_face_missing);'
          '合成裁决(仅门内夹具)落档后=草稿交付(draft_delivered=true,'
          'draft_blocked_class 同名;分段 report 的 rc 随正式交付=false 仍为 1),'
          '正式交付 deliverable 仍 false;正式归档拒绝(rc≠0,隔离归档目录无新件)',
          rc_s8 == 0 and bool(jud8)
          and _row(jud8['reader_map']['policy_question']['official_targets'],
                   region='EA').get('status') == 'missing'
          and rc_a8 == 0 and (d_a8.get('data') or {}).get('attached') is True
          and rc_r8 == 1 and dr8.get('deliverable') is False
          and dr8.get('draft_delivered') is False
          and dr8.get('blocked_class') == 'policy_question_face_missing'
          and os.path.isfile(vp8)
          and rc_r8b == 1 and d_r8b.get('ok') is False
          and dr8b.get('deliverable') is False
          and dr8b.get('draft_delivered') is True
          and dr8b.get('draft_blocked_class') == 'policy_question_face_missing'
          and aj.blocked_class_of(rj8b, calendar_path=cal8)
          == 'policy_question_face_missing'
          and rc_x8 != 0 and d_x8.get('ok') is False
          and (not os.path.exists(arc8) or not os.listdir(arc8)),
          f"seat={rc_s8} attach={rc_a8}/{(d_a8.get('data') or {}).get('attached')} "
          f"pre-review rc={rc_r8} bc={dr8.get('blocked_class')} | post rc={rc_r8b} "
          f"ok={d_r8b.get('ok')} draft={dr8b.get('draft_delivered')} "
          f"{dr8b.get('draft_blocked_class')} dlv={dr8b.get('deliverable')} | "
          f"archive={rc_x8} {json.dumps(d_x8.get('data') or d_x8.get('error'), ensure_ascii=False)[:200]}")

    # ── g9. auto 段与冻结契约对账(R18 §D / R1-F09 §B / R2 条目6——任务3 首版
    #      「缺口即拦」全量电池三红后的收口):
    #      ① 零事实树 auto 无 judgment → [plan, plan_gap, pause]: 缺口点名
    #        (error=plan_gap),同时保留 Agent Native 暂停点条目与 judgment 指令面;
    #      ② 携无效 judgment → 正式 attach 拒收留痕(attach ok=False),不进 report;
    #      ③ 缺口工单携 judgment 竟落位(门内以替身 attach 核模拟「校验未拦」)
    #        → 不推进到 report + 落 PLAN_GAP_HOLD.json;此后已落位续链无 judgment
    #        同拦(正式 CLI);
    #      ④ 已落位 run(无保持标记)续链不重新裁计划缺口——事后口径变化不作废
    #        在案裁决绑定(R2 条目6 续链契约)。
    rc9, d9 = _cli(['research-one', '--stage', 'auto', '--question-file', qf,
                    '--engine-root', t7], cwd=t7)
    dd9 = d9.get('data') or {}
    ch9 = dd9.get('chain') or []
    st9 = [c.get('stage') for c in ch9]
    pa9 = next((c for c in ch9 if c.get('stage') == 'pause'), {})
    er9 = d9.get('error') or {}
    check('§T3-g9① 零事实树 auto(无 judgment): rc=1/[plan, plan_gap, pause]/error='
          'plan_gap(zero_facts);暂停点条目在(note 含「暂停点」+「计划缺口」)、'
          'next 含 judgment 与缺口(R1-F09 §B1 契约保持)',
          rc9 == 1 and d9.get('ok') is False
          and st9 == ['plan', 'plan_gap', 'pause']
          and er9.get('kind') == 'plan_gap' and er9.get('message') == 'zero_facts'
          and '暂停点' in str(pa9.get('note'))
          and '计划缺口' in str(pa9.get('note'))
          and 'judgment' in str(dd9.get('next'))
          and '计划缺口' in str(dd9.get('next')),
          f"rc={rc9} stages={st9} err={json.dumps(er9, ensure_ascii=False)[:160]} "
          f"next={str(dd9.get('next'))[:160]}")
    jp_bad9 = os.path.join(TMPG, 't3g_judgment_bad9.json')
    with open(jp_bad9, 'w', encoding='utf-8') as fh:
        json.dump({'l3': {}, 'l4': {}}, fh, ensure_ascii=False)
    rc9b, d9b = _cli(['research-one', '--stage', 'auto', '--question-file', qf,
                      '--engine-root', t7, '--judgment', jp_bad9], cwd=t7)
    ch9b = (d9b.get('data') or {}).get('chain') or []
    st9b = [c.get('stage') for c in ch9b]
    att9b = next((c for c in ch9b if c.get('stage') == 'attach'), {})
    check('§T3-g9② 零事实树 auto 携无效 judgment: rc=1;attach 条目 ok=False'
          '(正式拒收留痕,R1-F09 §B2 契约保持)+plan_gap 条目;无 report 条目;'
          'error=plan_gap',
          rc9b == 1 and 'attach' in st9b and att9b.get('ok') is False
          and 'plan_gap' in st9b and 'report' not in st9b
          and (d9b.get('error') or {}).get('kind') == 'plan_gap',
          f"rc={rc9b} stages={st9b} attach={json.dumps(att9b, ensure_ascii=False)[:200]} "
          f"err={json.dumps(d9b.get('error'), ensure_ascii=False)[:160]}")
    rd7 = (ch9[0].get('report_dir') if ch9 else '') or dd7.get('report_dir') or ''
    rc9c, st9c, held9c, _capt = None, [], None, ''
    hold9 = os.path.join(rd7, 'PLAN_GAP_HOLD.json')
    if rd7 and os.path.isdir(rd7):
        sys.path.insert(0, ROOT)
        try:
            import ia_cli as _ic
        except Exception as _e:                     # noqa: BLE001
            _ic = None
            rc9c = 'import_failed: %s' % _e
        if _ic is not None:
            jp_any = os.path.join(TMPG, 't3g_judgment_any9.json')
            with open(jp_any, 'w', encoding='utf-8') as fh:
                json.dump({'l3': {'stub': 1}, 'l4': {'stub': 1}}, fh,
                          ensure_ascii=False)
            _orig = _ic._r1_attach_core
            _ic._r1_attach_core = lambda _a, _e: (
                {'attached': True, 'blocked': False, 'report_dir': rd7,
                 'validation': {'passed': True, 'violations': []}}, None)
            _out, sys.stdout = sys.stdout, io.StringIO()
            try:
                _ic.main(['research-one', '--stage', 'auto', '--question-file',
                          qf, '--report-dir', rd7, '--judgment', jp_any,
                          '--engine-root', t7])
            except SystemExit as _e:
                rc9c = _e.code
            finally:
                _capt = sys.stdout.getvalue()
                sys.stdout = _out
                _ic._r1_attach_core = _orig
            try:
                _o9c = json.loads(_capt)
            except ValueError:
                _o9c = {}
            st9c = [c.get('stage') for c in ((_o9c.get('data') or {})
                                             .get('chain') or [])]
            _pg9c = next((c for c in ((_o9c.get('data') or {}).get('chain') or [])
                          if c.get('stage') == 'plan_gap'), {})
            held9c = _pg9c.get('held')
    check('§T3-g9③ 缺口工单携 judgment 竟落位(替身 attach 核,门内夹具): rc=1/'
          '[plan(resumed), attach, plan_gap(held=true)]/无 report 条目;run 目录落 '
          'PLAN_GAP_HOLD.json',
          rc9c == 1 and st9c == ['plan', 'attach', 'plan_gap']
          and held9c is True and os.path.isfile(hold9),
          f"rc={rc9c} stages={st9c} held={held9c} hold_file="
          f"{os.path.isfile(hold9) if rd7 else 'n/a'} {_capt[-200:] if rd7 else ''}")
    rc9d, d9d, st9d = None, {}, []
    if os.path.isfile(hold9):
        rj7p = os.path.join(rd7, 'report.json')
        rj7 = _jq(rj7p)
        _ly7 = rj7.setdefault('layers', {})
        for _k in ('L3_AI推断层', 'L4_条件情景层'):
            _ly7[_k] = dict(_ly7.get(_k) or {}, produced=True)
        rj7['agent_judgment'] = dict(rj7.get('agent_judgment') or {},
                                     attached=True)
        with open(rj7p, 'w', encoding='utf-8') as fh:
            json.dump(rj7, fh, ensure_ascii=False)
        rc9d, d9d = _cli(['research-one', '--stage', 'auto', '--report-dir',
                          rd7, '--engine-root', t7], cwd=t7)
        st9d = [c.get('stage') for c in ((d9d.get('data') or {}).get('chain')
                                         or [])]
    check('§T3-g9④ 保持标记在案的已落位续链(无 judgment,正式 CLI;门内夹具把 '
          'run 标为已落位): rc=1/[plan(resumed), plan_gap(held=true)]/无 attach/'
          'report 条目;error=plan_gap',
          rc9d == 1 and st9d == ['plan', 'plan_gap']
          and (d9d.get('error') or {}).get('kind') == 'plan_gap'
          and ((d9d.get('data') or {}).get('chain') or [{}])[0]
          .get('resumed') is True
          and next((c for c in (d9d.get('data') or {}).get('chain')
                    if c.get('stage') == 'plan_gap'), {}).get('held') is True,
          f"rc={rc9d} stages={st9d} err={json.dumps(d9d.get('error'), ensure_ascii=False)[:160]}")
    # ④ 已落位 run(无保持标记)续链: 事后出现计划缺口也不重新裁——attach 跳过
    rdp = os.path.join(rd, 'report.json')
    rjd = _jq(rdp)
    _already = bool((rjd.get('layers') or {}).get('L3_AI推断层', {}).get('produced')
                    and (rjd.get('layers') or {}).get('L4_条件情景层', {})
                    .get('produced')
                    and (rjd.get('agent_judgment') or {}).get('attached'))
    _n_before = len(rjd.get('evidence_index') or [])
    rjd['evidence_index'] = [
        r for r in (rjd.get('evidence_index') or []) if (r or {}).get('kind')
        not in ('snapshot_fact', 's3_envelope', 'policy_record',
                'plan_series_point')]
    with open(rdp, 'w', encoding='utf-8') as fh:
        json.dump(rjd, fh, ensure_ascii=False)
    rc9e, d9e = _cli(['research-one', '--stage', 'auto', '--question-file', qf,
                      '--report-dir', rd, '--engine-root', t], cwd=t)
    ch9e = (d9e.get('data') or {}).get('chain') or []
    st9e = [c.get('stage') for c in ch9e]
    att9e = next((c for c in ch9e if c.get('stage') == 'attach'), {})
    check('§T3-g9⑤ 已落位 run(g3 接收,无保持标记)事后出现零事实缺口: 续链不'
          '重新裁计划缺口——无 plan_gap 条目、attach 跳过(skipped=true)、plan '
          'resumed=true(R2 条目6 续链契约: 在案裁决绑定不因事后口径变化作废;前置 '
          '条件=run 已落位且缺口已成立)',
          _already and _n_before > len(rjd['evidence_index'])
          and 'plan_gap' not in st9e
          and att9e.get('skipped') is True
          and ch9e and ch9e[0].get('resumed') is True,
          f"already={_already} facts {_n_before}→{len(rjd['evidence_index'])} "
          f"rc={rc9e} stages={st9e} err={json.dumps(d9e.get('error'), ensure_ascii=False)[:160]}")


# ══ 任务4: 冷启动 ════════════════════════════════════════════════════
# 守卫夹具=2026-11-24 真实守卫对的裁剪版(tests/fixtures_r33/china_pair_{old,new}_
# 20261124.json;原件 sha256 记于夹具 _fixture): 规范位=备用源档(三指数估值+via/
# note 来源注记),候选=完整版(四指数估值含上证指数,无注记)。基线把 via/note
# 计为指标身份→完整候选被判「指标身份丢失 2 项」转存 superseded/,规范位留
# 缺上证指数估值一档(回执见 r33-evidence T4_GUARD_BASELINE_f053_repro.txt)。
T4_OLD = os.path.join(HERE, 'fixtures_r33', 'china_pair_old_20261124.json')
T4_NEW = os.path.join(HERE, 'fixtures_r33', 'china_pair_new_20261124.json')
T4_SHA = {'old': 'cb91bd126b5cc5736b0b0f35e32a92b0aa8904d7aeb511145f953a9816b6d8aa',
          'new': 'f2b1957fb0fd13d6ef77e4cdf50289f700b29d62eb960c6bd424ce23ffeeaa76'}
_T4_N11 = '11/15 宏观体制评分卡(消费快照)'


def _t4_pair():
    with open(T4_OLD, encoding='utf-8') as fh:
        old = json.load(fh)
    with open(T4_NEW, encoding='utf-8') as fh:
        new = json.load(fh)
    return old, new


def _t4_bytes(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2).encode('utf-8')


def _t4_json(path):
    with open(path, encoding='utf-8') as fh:
        return json.load(fh)


def _t4_sup(dd):
    sd = os.path.join(dd, 'superseded')
    if not os.path.isdir(sd):
        return []
    return sorted(f for f in os.listdir(sd)
                  if f.endswith('.json') and not f.startswith('.'))


def _t4_guard(tag, seq):
    """空采集目录上依次写 seq 各载荷(china/20261124)→ ([(status, note, path)],
    规范位路径,采集目录)。"""
    import research_provenance as rp
    dd = os.path.join(TMPG, 't4_' + tag, 'data', 'daily')
    os.makedirs(dd)
    out = [(st, note, p) for p, st, note in (
        rp.daily_face_guard_write(dd, 'china', '20261124', p) for p in seq)]
    return out, os.path.join(dd, 'china_20261124.json'), dd


def _t4_degraded(tag, base, mut):
    """规范位=base,再写 mut(base 的变体)→ (退化转存且规范位不动?, 注记)。"""
    cand = copy.deepcopy(base)
    mut(cand)
    res, canon, dd = _t4_guard(tag, [base, cand])
    st, note, p = res[1]
    div = _t4_sup(dd)
    return (st == 'degraded_diverted'
            and open(canon, 'rb').read() == _t4_bytes(base)
            and p != canon and len(div) == 1
            and _t4_json(os.path.join(dd, 'superseded', div[0])) == cand), note


def _t4_remarks(c):
    c['valuation']['via'] = 'akshare_legu'
    c['valuation']['note'] = '乐咕上证主板平均市盈率(近似口径)'
    return c


def _t4_tree_files():
    """被测树文件快照({相对路径: (大小, mtime_ns)};不含 .git/__pycache__)。"""
    out = {}
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in ('.git', '__pycache__')]
        for fn in fns:
            p = os.path.join(dp, fn)
            try:
                stt = os.lstat(p)
            except OSError:
                continue
            out[os.path.relpath(p, ROOT)] = (stt.st_size, stt.st_mtime_ns)
    return out



def sec_t4_a():
    print('§T4-a 真实守卫对(2026-11-24,裁剪夹具): 完整新版换入主日档')
    import research_provenance as rp
    old, new = _t4_pair()
    check('§T4-a0 夹具=真实守卫对裁剪版(原件 sha256 随行): 旧=三指数估值+via/note'
          ' 来源注记(备用源档),新=四指数估值含上证指数(完整候选)',
          old['_fixture']['source_file_sha256'] == T4_SHA['old']
          and new['_fixture']['source_file_sha256'] == T4_SHA['new']
          and sorted(old['valuation']) == ['000300.SH', '000852.SH', '000905.SH',
                                           'date', 'note', 'pe', 'via']
          and sorted(new['valuation']) == ['000001.SH', '000300.SH', '000852.SH',
                                           '000905.SH', 'date', 'pe']
          and new['valuation']['000001.SH']['pe_ttm'] == 15.71)
    res, canon, dd = _t4_guard('a', [old, new])
    check('§T4-a1 旧档首写 first → 完整候选 overwritten_preserved(零退化注记),'
          '落位=规范位 china_20261124.json(非转存)',
          res[0][0] == 'first' and res[1][0] == 'overwritten_preserved'
          and res[1][1] == '' and res[1][2] == canon, res)
    check('§T4-a2 规范位字节=完整候选序列化;旧档副本入 superseded/(内容=旧载荷)',
          open(canon, 'rb').read() == _t4_bytes(new)
          and len(_t4_sup(dd)) == 1
          and _t4_json(os.path.join(dd, 'superseded', _t4_sup(dd)[0])) == old)
    oi, ni = rp.daily_face_observation_map(old), rp.daily_face_observation_map(new)
    li, ln = rp.daily_face_identity_map(old), rp.daily_face_identity_map(new)
    check('§T4-a3 全叶身份图(诊断用)对: 丢 via/note 两身份、增 valuation.000001;'
          '判定用观测图零丢失(仅增 valuation.000001)——来源备注不计入指标覆盖',
          sorted(set(li) - set(ln)) == [('valuation', 'note'), ('valuation', 'via')]
          and set(ln) - set(li) == {('valuation', '000001')}
          and not (set(oi) - set(ni))
          and set(ni) - set(oi) == {('valuation', '000001')}
          and all(len(i) >= 2 for i in ni)
          and not ({('valuation', 'via'), ('valuation', 'note')} & set(ni)),
          (sorted(set(oi) - set(ni)), sorted(set(ni) - set(oi))))


def sec_t4_b():
    print('§T4-b 真实退化仍被拦截(规范位=完整版)')
    _o, new = _t4_pair()

    def drop_index(c):
        del c['valuation']['000905.SH']
    ok, note = _t4_degraded('b_idx', new, drop_index)
    check('§T4-b1 删一项指数估值(中证500)→ degraded_diverted「指标身份丢失 1 项'
          '(valuation.000905)」;规范位不动,候选留 superseded/',
          ok and note.startswith('指标身份丢失 1 项(valuation.000905)'), note)

    def trunc(c):
        s = c['a_share_indices']['000300.SH']['series']
        s['dates'], s['values'] = s['dates'][:-2], s['values'][:-2]
    ok, note = _t4_degraded('b_trunc', new, trunc)
    check('§T4-b2 沪深300历史序列尾部截断(同身份)→「有效观测叶子缩水」',
          ok and note.startswith('有效观测叶子缩水 1 项(a_share_indices.000300:'), note)

    def nulls(c):
        c['macro']['cpi_yoy']['value'] = None
        c['series']['CN_CPI_YOY']['values'] = [None] * len(
            c['series']['CN_CPI_YOY']['values'])
    ok, note = _t4_degraded('b_null', new, nulls)
    check('§T4-b3 观测值置 null(CPI 同比点值+CPI 全史序列)→「有效观测叶子缩水 2 项」',
          ok and note.startswith('有效观测叶子缩水 2 项(macro.cpi_yoy:2→1,'
                                 'series.CN_CPI_YOY:'), note)

    def back(c):
        c['hk_indices']['^HSI']['series']['dates'] = [
            '2026-11-%02d' % d for d in (3, 4, 5, 6, 7)]
    ok, note = _t4_degraded('b_back', new, back)
    hz = new['hk_indices']['^HSI']['series']['dates'][-1]
    check('§T4-b4 条数不变但最新有效观测日回退(恒指 %s→2026-11-07)→'
          '「最新有效观测回退 1 项」' % hz,
          ok and ('最新有效观测回退 1 项(hk_indices.^HSI:%s→2026-11-07' % hz) in note, note)

    def drop_macro(c):
        del c['macro']
    ok, note = _t4_degraded('b_cmacro', new, drop_macro)
    check('§T4-b5 删整个 CN 宏观面容器→「指标身份丢失 7 项(macro.…」',
          ok and note.startswith('指标身份丢失 7 项(macro.'), note)


def sec_t4_c():
    print('§T4-c 来源备注/元数据/披露区不参与升降级判定(两个方向)')
    _o, new = _t4_pair()

    def meta(c):
        c['timestamp'] = '2026-11-24 23:59:59'
        c['collection_status'] = {'budget': {'limit_sec': 800.0},
                                  'stages': {'x': {'status': 'ok'}}}
        c['sources'] = {'a': 'http://x'}
        c['sources_status'] = {'a': 'EXACT'}
        c['alerts'] = ['源失败']
        c['source_version'] = {'v': '2'}
        c['cn_history'] = {'mode': 'carry_forward'}
        return c
    res, canon, dd = _t4_guard('c1', [new, _t4_remarks(copy.deepcopy(new))])
    check('§T4-c1 仅增来源注记(valuation.via/note)→ overwritten_preserved',
          res[1][0] == 'overwritten_preserved' and res[1][1] == ''
          and open(canon, 'rb').read() == _t4_bytes(_t4_remarks(copy.deepcopy(new))),
          res)
    res, canon, dd = _t4_guard('c2', [_t4_remarks(copy.deepcopy(new)), new])
    check('§T4-c2 仅减来源注记(真实对形态: 备用源档在规范位,完整版无注记)→ '
          'overwritten_preserved,规范位=无注记完整版',
          res[1][0] == 'overwritten_preserved' and res[1][1] == ''
          and open(canon, 'rb').read() == _t4_bytes(new), res)
    res, canon, dd = _t4_guard('c3', [new, meta(copy.deepcopy(new))])
    check('§T4-c3 仅改文件级元数据/披露区(timestamp/collection_status/sources/'
          'sources_status/alerts/source_version/cn_history)→ overwritten_preserved',
          res[1][0] == 'overwritten_preserved' and res[1][1] == ''
          and open(canon, 'rb').read() == _t4_bytes(meta(copy.deepcopy(new))), res)
    res, canon, dd = _t4_guard('c4', [meta(copy.deepcopy(new)), new])
    check('§T4-c4 披露区整段消失(续存 3 键→全无的实测雷形态)同上不判降级',
          res[1][0] == 'overwritten_preserved' and res[1][1] == ''
          and open(canon, 'rb').read() == _t4_bytes(new), res)


def sec_t4_d():
    print('§T4-d 备注不掩盖观测蒸发;未登记的备注样键仍按观测叶计(闭集=可审计)')
    _o, new = _t4_pair()

    def d1(c):
        _t4_remarks(c)
        c['valuation']['pe'] = None
    ok, note = _t4_degraded('d1', new, d1)
    check('§T4-d1 注记在场但 valuation.pe 置 null→「有效观测叶子缩水 1 项'
          '(valuation.pe:1→0)」', ok and note.startswith(
              '有效观测叶子缩水 1 项(valuation.pe:1→0;'), note)

    def d2(c):
        c['valuation']['000300.SH']['pe_ttm'] = None
    ok, note = _t4_degraded('d2', new, d2)
    check('§T4-d2 指数估值一项数值置 null→缩水(valuation.000300:5→4)',
          ok and note.startswith('有效观测叶子缩水 1 项(valuation.000300:5→4;'), note)

    def d3(c):
        c['valuation']['000300.SH'] = {'name': '沪深300'}
    ok, note = _t4_degraded('d3', new, d3)
    check('§T4-d3 指数估值容器只剩标注文字(name)→观测叶归零=身份丢失'
          '「指标身份丢失 1 项(valuation.000300)」',
          ok and note.startswith('指标身份丢失 1 项(valuation.000300)'), note)

    def d4(c):
        c['valuation']['comment'] = 'x'
        return c
    res, canon, dd = _t4_guard('d4', [new, d4(copy.deepcopy(new)), new])
    check('§T4-d4 未登记备注样键 valuation.comment 仍计观测叶: 增=overwritten_'
          'preserved;随后撤回=degraded_diverted「指标身份丢失 1 项(valuation.comment)」',
          res[1][0] == 'overwritten_preserved'
          and res[2][0] == 'degraded_diverted'
          and res[2][1].startswith('指标身份丢失 1 项(valuation.comment)')
          and open(canon, 'rb').read() == _t4_bytes(d4(copy.deepcopy(new))), res)


def sec_t4_e():
    print('§T4-e 备注键闭集与判定用观测图口径')
    import research_provenance as rp
    check('§T4-e1 备注键闭集登记(via/note/source/sources/status/url/scope/name/'
          'label…);披露区键=cn_history/alerts/sources/sources_status/source_version/'
          'collection_status',
          {'via', 'note', 'source', 'sources', 'status', 'url', 'name', 'label',
           'scope'} <= set(rp._REMARK_LEAF_KEYS)
          and set(rp._GUARD_STATUS_KEYS) == {
              'cn_history', 'alerts', 'sources', 'sources_status',
              'source_version', 'collection_status'})
    payload = {'timestamp': 'x', 'version': '2.1',
               'data': {'CPI': {'value': 1.0, 'note': 'n',
                                'dates': ['2026-01-01'], 'values': [None]}},
               'ah_premium': None}
    check('§T4-e2 观测图: None 叶计身份在场、有效观测 0;顶层标量(含 None 顶层键)'
          '不计;备注叶不计;全叶身份图仍含备注叶与顶层键(诊断用,保留)',
          rp.daily_face_observation_map(payload) == {('data', 'CPI'): 2}
          and rp.daily_face_identity_map(payload) == {
              ('timestamp',): 1, ('version',): 1, ('data', 'CPI'): 3,
              ('ah_premium',): 0}
          and rp.daily_face_valid_obs_horizon(payload) == {},
          (rp.daily_face_observation_map(payload),
           rp.daily_face_identity_map(payload)))


def sec_t4_f():
    print('§T4-f 流水线台账: 失败步骤/时长/原因(真 run_pipeline + 替身脚本)')
    import run_weekly as rw
    sd = os.path.join(TMPG, 't4f', 'scripts')
    os.makedirs(sd)

    def _w(name, body):
        with open(os.path.join(sd, name), 'w', encoding='utf-8') as fh:
            fh.write(body)
    _w('ok.py', 'import time\ntime.sleep(0.3)\n')
    _w('slow.py', 'import time\ntime.sleep(30)\n')
    _w('exit3.py', 'import sys\nsys.exit(3)\n')
    _w('sig.py', 'import os, signal, time\n'
                 'os.kill(os.getpid(), signal.SIGTERM)\ntime.sleep(30)\n')
    steps = [('s1', 'ok.py', False), ('s2', 'slow.py', True),
             ('s3', 'exit3.py', False), ('s4', 'sig.py', False),
             ('s5', 'missing.py', False), ('s6', 'ok.py', True, ['slow.py'])]
    orig = rw.run_step
    rw.run_step = lambda n, s, timeout=900, script_dir=None, extra_args=None: orig(
        n, s, timeout=1, script_dir=script_dir, extra_args=extra_args)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            res = rw.run_pipeline(steps, script_dir=sd)
    finally:
        rw.run_step = orig
    m = res.meta
    check('§T4-f1 results.meta 逐步骤 {duration_sec, exit_code, fail_reason}: 成功=0/'
          'None;超时=timeout+timeout_sec;非零退出=nonzero_exit;被信号终止=signal:15;'
          '脚本缺席=script_missing;依赖跳过=dependency_skipped',
          0.3 <= m['s1']['duration_sec'] < 5 and m['s1']['exit_code'] == 0
          and m['s1']['fail_reason'] is None
          and m['s2']['fail_reason'] == 'timeout' and m['s2']['timeout_sec'] == 1
          and m['s2']['exit_code'] is None and 1 <= m['s2']['duration_sec'] < 5
          and m['s3']['exit_code'] == 3 and m['s3']['fail_reason'] == 'nonzero_exit'
          and m['s4']['exit_code'] == -15 and m['s4']['fail_reason'] == 'signal:15'
          and m['s5'] == {'duration_sec': 0.0, 'exit_code': None,
                          'fail_reason': 'script_missing'}
          and m['s6'] == {'duration_sec': 0.0, 'exit_code': None,
                          'fail_reason': 'dependency_skipped'}
          and res.skips.get('s6', '').startswith('依赖未成功'), m)

    proj = os.path.join(TMPG, 't4f', 'proj')
    os.makedirs(proj)
    n1, n2, n4 = ('1/15 全球市场数据采集', '2/15 A股港股数据采集', '4/15 新闻采集与分析')
    fake = rw.PipelineResults([(n1, True, True), (n2, False, True),
                               (n4, False, False), (_T4_N11, False, True)])
    fake.meta = {n1: {'duration_sec': 12.0, 'exit_code': 0, 'fail_reason': None},
                 n2: {'duration_sec': 900.3, 'exit_code': None,
                      'fail_reason': 'timeout', 'timeout_sec': 900}}
    fake.skips = {_T4_N11: '依赖未成功 → A股港股数据采集(失败)'}
    _orig_rp, _orig_pd = rw.run_pipeline, rw.PROJECT_DIR
    rw.run_pipeline = lambda steps, *a, **k: fake
    rw.PROJECT_DIR = proj
    out, rc = io.StringIO(), None
    try:
        with contextlib.redirect_stdout(out):
            try:
                rw.main([])
            except SystemExit as e:
                rc = e.code
    finally:
        rw.run_pipeline, rw.PROJECT_DIR = _orig_rp, _orig_pd
    led_files = glob.glob(os.path.join(proj, 'logs', 'pipeline_run_*.json'))
    led = _t4_json(led_files[0]) if led_files else {}
    rows = {r['name']: r for r in led.get('steps') or []}
    check('§T4-f2 main([]) 台账 steps 每行带 duration_sec/exit_code/fail_reason'
          '(未上报=如实 unreported;依赖跳过=dependency_skipped;超时行带 timeout_sec);'
          '顶层 failed_steps 列全部未成功行;关键步骤失败→exit 1;汇总打印原因+时长',
          len(led_files) == 1 and rc == 1
          and rows[n1]['duration_sec'] == 12.0 and rows[n1]['fail_reason'] is None
          and rows[n2]['fail_reason'] == 'timeout' and rows[n2]['timeout_sec'] == 900
          and rows[n4]['fail_reason'] == 'unreported'
          and rows[n4]['duration_sec'] is None
          and rows[_T4_N11]['fail_reason'] == 'dependency_skipped'
          and [r['name'] for r in led.get('failed_steps') or []] == [n2, n4, _T4_N11]
          and isinstance(led.get('duration_sec'), (int, float))
          and '失败原因 超时(上限 900 秒)' in out.getvalue()
          and '失败原因 未上报(步骤替身/旧实现未记录原因)' in out.getvalue(),
          (rc, led.get('failed_steps')))


def sec_t4_g():
    print('§T4-g update 回执: 失败步骤/时长/原因/守卫分流(真 cmd_update → '
          '子进程真 run_weekly.main + 替身脚本)')
    import ia_cli as ic

    def _run(tag, shim_body, files=None, ledger=None):
        tr = os.path.join(TMPG, 't4g_' + tag)
        os.makedirs(tr)
        with open(os.path.join(tr, 'run_weekly.py'), 'w', encoding='utf-8') as fh:
            fh.write(shim_body)
        for name, body in (files or {}).items():
            p = os.path.join(tr, name)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, 'w', encoding='utf-8') as fh:
                fh.write(body)
        if ledger:
            os.makedirs(os.path.join(tr, 'logs'))
            with open(os.path.join(tr, 'logs', ledger[0]), 'w',
                      encoding='utf-8') as fh:
                json.dump(ledger[1], fh, ensure_ascii=False)
        _orig = ic.ROOT
        ic.ROOT = tr
        out, rc = io.StringIO(), None
        try:
            with contextlib.redirect_stdout(out), \
                    contextlib.redirect_stderr(io.StringIO()):
                try:
                    ic.cmd_update(ic.build_parser().parse_args(['update', '--yes']))
                except SystemExit as e:
                    rc = e.code
        finally:
            ic.ROOT = _orig
        return rc, json.loads(out.getvalue()), tr

    fs = {'fake_scripts/global_market_collector.py': 'import time\ntime.sleep(1.2)\n',
          'fake_scripts/china_market_collector.py': 'import time\ntime.sleep(30)\n',
          'fake_scripts/macro_collector.py': 'import sys\nsys.exit(3)\n'}
    guard_line = ('⛔ 守卫: 未覆盖完整档 → superseded/china_20261124_x.json '
                  '(指标身份丢失 1 项)')
    shim = ('import os, sys\n'
            'sys.path.insert(0, %r)\n'
            'import run_weekly as rw\n'
            'here = os.path.dirname(os.path.abspath(__file__))\n'
            'rw.PROJECT_DIR = here\n'
            'sd = os.path.join(here, "fake_scripts")\n'
            '_orig = rw.run_step\n'
            'rw.run_step = lambda n, s, timeout=900, script_dir=None, '
            'extra_args=None: _orig(\n'
            '    n, s, timeout=1, script_dir=sd, extra_args=extra_args)\n'
            'print(%r)\n'
            'print("filler " * 400)\n'
            'rw.main([])\n' % (ROOT, guard_line))
    rc, env, tr = _run('g1', shim, fs)
    d = env.get('data') or {}
    rows = {r['name']: r for r in d.get('steps') or []}
    n2, n3 = '2/15 A股港股数据采集', '3/15 宏观数据采集'
    failed_names = [r['name'] for r in d.get('failed_steps') or []]
    check('§T4-g1 关键步骤超时/非零退出/缺席→rc=1 透传、ok=False;回执 steps 15 行逐行带 '
          'duration_sec/exit_code/fail_reason(A股港股=timeout+timeout_sec;宏观=nonzero_exit+'
          '返回码 3;依赖步骤=dependency_skipped);failed_steps=全部未成功行;duration_sec 在场',
          rc == 1 and env.get('ok') is False and d.get('exit_code') == 1
          and len(d.get('steps') or []) == 15
          and rows[n2]['ok'] is False and rows[n2]['fail_reason'] == 'timeout'
          and rows[n2]['duration_sec'] >= 1
          and rows[n2].get('timeout_sec') == 1 and rows[n2].get('exit_code') is None
          and rows[n3]['fail_reason'] == 'nonzero_exit'
          and rows[n3].get('exit_code') == 3 and 'timeout_sec' not in rows[n3]
          and all('exit_code' in r for r in d['steps'])
          and rows[_T4_N11]['skipped'] is True
          and rows[_T4_N11]['fail_reason'] == 'dependency_skipped'
          and n2 in failed_names and len(failed_names) == sum(
              1 for r in d['steps'] if not r['ok'])
          and isinstance(d.get('duration_sec'), (int, float))
          and d.get('duration_sec') >= 2,
          (rc, d.get('exit_code'), failed_names, rows.get(n2)))
    check('§T4-g2 守卫分流行单列 guard_diversions: 失败多时该行既被后续输出滚出 '
          'output_tail、也排不进 critical_tail 末 10 行(旧回执里彻底不可见),单列后'
          '仍可见;ledger_file 认领本次台账;无快照→snapshot_id None',
          d.get('guard_diversions') == [guard_line]
          and guard_line not in (d.get('critical_tail') or [])
          and guard_line not in (d.get('output_tail') or [])
          and bool(re.fullmatch(r'pipeline_run_\d{8}\.json',
                                str(d.get('ledger_file'))))
          and os.path.isfile(os.path.join(tr, 'logs', str(d.get('ledger_file'))))
          and d.get('snapshot_id') is None and 'steps_note' not in d,
          (d.get('guard_diversions'), d.get('ledger_file'),
           d.get('critical_tail'), d.get('output_tail')[-3:],
           d.get('snapshot_id'), 'steps_note' in d))
    rc, env, tr = _run('g2', 'print("done")\n')
    d = env.get('data') or {}
    check('§T4-g3 无台账→rc=0、ok=True、steps_note=no_readable_ledger(不编造 steps)',
          rc == 0 and env.get('ok') is True and 'steps' not in d
          and 'failed_steps' not in d and 'no_readable_ledger' in str(
              d.get('steps_note')), (rc, d.get('steps_note')))
    from datetime import datetime as _dt, timedelta as _td
    y = (_dt.now() - _td(days=1)).strftime('%Y%m%d')
    rc, env, tr = _run('g3', 'print("done")\n', ledger=(
        'pipeline_run_%s.json' % y,
        {'run_at': (_dt.now() - _td(days=1)).isoformat(timespec='seconds'),
         'steps': [{'name': 'x', 'ok': True}]}))
    d = env.get('data') or {}
    check('§T4-g4 只有更早的台账→steps_note=ledger_predates_this_run(不拿旧台账'
          '冒充本次)',
          rc == 0 and 'steps' not in d and 'ledger_predates_this_run' in str(
              d.get('steps_note')), (rc, d.get('steps_note')))
    okrow = {'name': '1/15 全球市场数据采集', 'ok': True, 'critical': True,
             'skipped': False, 'skip_reason': None, 'duration_sec': 3.5,
             'exit_code': 0, 'fail_reason': None}
    trow = {'name': '2/15 A股港股数据采集', 'ok': False, 'critical': True,
            'skipped': False, 'skip_reason': None, 'duration_sec': 900.0,
            'exit_code': None, 'fail_reason': 'timeout', 'timeout_sec': 900}
    shim_ok = ('import json, os\n'
               'from datetime import datetime\n'
               't0 = datetime.now()\n'
               'here = os.path.dirname(os.path.abspath(__file__))\n'
               'os.makedirs(os.path.join(here, "logs"))\n'
               'rows = json.loads(%r)\n'
               'blob = {"run_at": t0.isoformat(timespec="seconds"), '
               '"duration_sec": 903.5, "steps": rows, "success_count": 1, '
               '"failed_steps": [rows[1]], "snapshot_id": "research_snapshot_x", '
               '"gate_a": "PASS"}\n'
               'json.dump(blob, open(os.path.join(here, "logs", '
               '"pipeline_run_%%s.json" %% t0.strftime("%%Y%%m%%d")), "w"))\n'
               'print("all ok")\n' % json.dumps([okrow, trow], ensure_ascii=False))
    rc, env, tr = _run('g4', shim_ok)
    d = env.get('data') or {}
    check('§T4-g5 台账行原样进回执(含 exit_code;超时行带 timeout_sec)、failed_steps=台账'
          '未成功行、snapshot_id/gate_a 随台账带出(替身脚本自报成功→rc=0/ok=True)',
          rc == 0 and env.get('ok') is True and d.get('steps') == [okrow, trow]
          and d.get('failed_steps') == [trow] and d.get('duration_sec') == 903.5
          and d.get('snapshot_id') == 'research_snapshot_x'
          and d.get('gate_a') == 'PASS' and d.get('guard_diversions') == [],
          (rc, d.get('steps') == [okrow, trow], d.get('failed_steps'),
           d.get('duration_sec'), d.get('snapshot_id'), d.get('gate_a'),
           d.get('guard_diversions'), env.get('ok'), d.get('steps'), okrow, trow))


def sec_t4_h():
    os.environ.setdefault('HK_HISTORY_FILE',
                          os.path.join(TMPG, 'hk_index_history.json'))
    print('§T4-h A股港股采集器: 时间预算/断点续采/核心截断(离线,取网函数替身)')
    import types
    import china_market_collector as cmc
    import pandas as pd
    before = _t4_tree_files()
    T = os.path.join(TMPG, 't4h')
    os.makedirs(T)
    for k in ('PROJECT_DIR', 'DATA_DIR', 'TUSHARE_MONTHLY_CACHE_DIR'):
        setattr(cmc, k, T)
    cmc.ASHARE_CHECKPOINT_PATH = os.path.join(T, 'ckpt.json')
    cmc.PBC_OMO_CACHE_DIR = os.path.join(T, 'pboc')
    saved, calls = [], []
    cmc.get_trade_dates = lambda: ('20261124', '20261114', '20260101')
    cmc.cn_index_history_period = lambda: '10y'
    cmc.cn_window_start = lambda p: '20161124'
    cmc.save_data = lambda d: saved.append(d) or 'saved'
    real_mono, budget0 = time.monotonic, cmc.CN_COLLECTOR_BUDGET_SECONDS
    curl0, parse0 = cmc._curl_get, cmc._pboc_omo_parse_announcement
    em0, ak_mod = cmc._em_series_rows, sys.modules.get('akshare')
    fms0 = cmc.fetch_macro_series      # 真函数(阶段替身安装前留存)
    clock = {'t': 0.0}
    codes = list(cmc.A_SHARE_INDICES)

    def df_small():
        return pd.DataFrame({'trade_date': ['20261120', '20261123', '20261124'],
                             'close': [100.0, 101.0, 102.0],
                             'pct_chg': [0.5, 1.0, 1.0], 'vol': [1.0, 1.0, 1.0],
                             'amount': [1.0, 1.0, 1.0]})

    def stub_others(fn=None):
        for name, v in (('fetch_hk_indices', {'HSI': {'x': 1}}),
                        ('fetch_southbound', {'sb': 1}), ('fetch_margin', {'mg': 1}),
                        ('fetch_valuation', {'pe': 1}), ('fetch_turnover', {'to': 1}),
                        ('fetch_ah_premium', {'ah': 1}), ('fetch_macro', {'m': 1}),
                        ('fetch_macro_series', {'s': 1})):
            setattr(cmc, name, (lambda vv, nm: lambda *a, **k: (
                fn(nm) if fn else None) or vv)(v, name))

    def run_main():
        buf, code = io.StringIO(), None
        with contextlib.redirect_stdout(buf):
            try:
                cmc.main()
            except SystemExit as e:
                code = e.code
        return code, buf.getvalue()

    def fake_clock(t0):
        clock['t'] = t0
        time.monotonic = lambda: clock['t']

    try:
        b_off = cmc.CollectionBudget(limit_sec=0)
        check('§T4-h0 预算默认 800 秒(<900 步骤上限);限流间隔 61 秒不变;阶段表=旧主程序'
              ' 1..9 顺序,核心=A股/港股;预算关闭: remaining/deadline=None、看门狗不武装;'
              '断点不带超龄常量(可续性改按同日+当日 bar 定型判定)',
              cmc._budget_from_env('') == 800.0 and cmc._budget_from_env('abc') == 800.0
              and cmc._budget_from_env('inf') == 800.0
              and cmc._budget_from_env(' 12.5 ') == 12.5
              and cmc.INDEX_DAILY_MIN_INTERVAL_SECONDS == 61
              and not hasattr(cmc, 'ASHARE_CHECKPOINT_TTL_SECONDS')
              and [s[0] for s in cmc._STAGES] == [
                  'a_share_indices', 'hk_indices', 'southbound', 'margin', 'valuation',
                  'turnover', 'ah_premium', 'macro', 'series']
              and [s[0] for s in cmc._STAGES if s[2]] == ['a_share_indices', 'hk_indices']
              and b_off.remaining() is None and b_off.deadline is None
              and b_off.exhausted() is False and cmc._arm_watchdog(b_off) is False)
        cmc.CN_COLLECTOR_BUDGET_SECONDS = 0.0

        def idx_fast(**kw):
            calls.append(kw.get('ts_code'))
            return df_small()
        cmc._index_daily = idx_fast
        stub_others()
        code, o = run_main()
        cs = saved[-1].get('collection_status') if saved else {}
        check('§T4-h1 预算关闭=旧行为: 无退出码、整档一次写出、九阶段全 ok、六指数六次'
              '调用、不写断点;collection_status 随档(limit 0/exhausted false)',
              code is None and len(saved) == 1 and calls == codes
              and all(v['status'] == 'ok' for v in cs.get('stages', {}).values())
              and cs.get('budget', {}).get('limit_sec') == 0.0
              and cs.get('core_cut_by_budget') is False
              and not os.path.exists(cmc.ASHARE_CHECKPOINT_PATH)
              and all(cmc._stage_call(n, b_off) is getattr(cmc, {
                  'southbound': 'fetch_southbound', 'margin': 'fetch_margin',
                  'valuation': 'fetch_valuation', 'turnover': 'fetch_turnover',
                  'ah_premium': 'fetch_ah_premium', 'macro': 'fetch_macro'}[n])
                  for n in ('southbound', 'margin', 'valuation', 'turnover',
                            'ah_premium', 'macro')),
              (code, len(saved), calls, json.dumps(cs, ensure_ascii=False)[:300]))

        def idx_slow(**kw):
            calls.append(kw.get('ts_code'))
            time.sleep(0.2 if len(calls) <= 2 else 10.0)
            return df_small()
        cmc.CN_COLLECTOR_BUDGET_SECONDS = 7.0
        cmc._index_daily = idx_slow
        saved.clear()
        calls.clear()
        t_real = time.time()
        code, o = run_main()
        secs = time.time() - t_real
        logs = os.path.join(T, 'logs')
        diag = (sorted(f for f in os.listdir(logs) if f.startswith('china_partial_'))
                if os.path.isdir(logs) else [])
        ck = (_t4_json(cmc.ASHARE_CHECKPOINT_PATH)
              if os.path.exists(cmc.ASHARE_CHECKPOINT_PATH) else {})
        st = (_t4_json(os.path.join(logs, diag[0]))['collection_status']['stages']
              if diag else {})
        check('§T4-h2 核心阶段(A股)被看门狗截断: exit 1、不写主日档、诊断性部分面写 '
              'logs/china_partial_*.json(a_share=cut_by_budget、其后=skipped_budget)、'
              '看门狗已解除、未被 10 秒慢调用拖住',
              code == 1 and not saved and len(diag) == 1 and secs < 9.5
              and cmc._BUDGET_TIMER['armed'] is False
              and st.get('a_share_indices', {}).get('status') == 'cut_by_budget'
              and all(v['status'] == 'skipped_budget' for k, v in st.items()
                      if k != 'a_share_indices'),
              (code, len(saved), diag, secs, st))
        check('§T4-h3 断点: 已取到的 2 个指数在断点里(第 3 个被中断不在),逐指数带取数'
              '时刻;输出含「不写主日档」与续采提示',
              list(ck.get('items') or {}) == codes[:2]
              and sorted(ck.get('fetched_at') or {}) == sorted(codes[:2])
              and '不写主日档' in o and '续采' in o,
              (list(ck.get('items') or {}), list(ck.get('fetched_at') or {}), o[-200:]))
        ck2_fa = dict(ck.get('fetched_at') or {})

        # ── A 股断点可续规则(固定时刻,不依赖真实钟;口径=EM 取值行截止 16:10 HKT) ──
        import datetime as _dtm
        hkt = _dtm.timezone(_dtm.timedelta(hours=8))

        def ts(y, m, d, hh, mm, ss=0):
            return _dtm.datetime(y, m, d, hh, mm, ss, tzinfo=hkt).timestamp()

        ts_intra, ts_pre, ts_close = (ts(2026, 11, 24, 14, 0), ts(2026, 11, 24, 16, 9, 59),
                                      ts(2026, 11, 24, 16, 10))
        ts_after, ts_late = ts(2026, 11, 24, 17, 0), ts(2026, 11, 25, 9, 0)

        def it(last='2026-11-24'):
            return {'name': 'x', 'close': 1.0, 'date': last.replace('-', ''),
                    'series': {'dates': ['2026-11-20', last], 'values': [1.0, 1.0]},
                    'via': 'tushare'}

        def put(items, fetched, end='20261124', win='20161124'):
            obj = {'end_date': end, 'window_start': win, 'saved_at': ts_after,
                   'items': items}
            if fetched is not None:
                obj['fetched_at'] = fetched
            with open(cmc.ASHARE_CHECKPOINT_PATH, 'w', encoding='utf-8') as fh:
                json.dump(obj, fh)

        c0, c1, c2 = codes[0], codes[1], codes[2]
        check('§T4-h4a 当日 bar 定型口径=EM 取值行截止(16:10 HKT): 收盘前/16:09:59→未定型,'
              '16:10:00/之后→定型;取数时刻不可读→未定型',
              cmc._ashare_bar_settled('20261124', ts_intra) is False
              and cmc._ashare_bar_settled('20261124', ts_pre) is False
              and cmc._ashare_bar_settled('20261124', ts_close) is True
              and cmc._ashare_bar_settled('20261124', ts_after) is True
              and cmc._ashare_bar_settled('20261124', ts_late) is True
              and cmc._ashare_bar_settled('20261124', None) is False
              and cmc._ashare_bar_settled('20261124', 'abc') is False
              and cmc._ashare_bar_settled('20261124', float('nan')) is False,
              [(x, cmc._ashare_bar_settled('20261124', x)) for x in
               (ts_intra, ts_pre, ts_close, ts_after, ts_late, None)])
        put({c0: it(), c1: it('2026-11-23'), c2: it()}, {c0: ts_intra, c1: ts_intra,
                                                        c2: ts_close})
        mixed = cmc._ashare_checkpoint_load('20261124', '20161124')
        check('§T4-h4b 逐指数判定: 收盘前取到的当日 bar(c0)不续;当日尚无 bar(c1,末根 11-23)'
              '可续;16:10 后取到的当日 bar(c2)可续——同一次读里混判',
              sorted(mixed) == sorted([c1, c2]), sorted(mixed))
        put({c0: it()}, None)
        oldfmt = cmc._ashare_checkpoint_load('20261124', '20161124')
        put({c0: it(), c1: it()}, {c0: ts_after})
        miss_one = cmc._ashare_checkpoint_load('20261124', '20161124')
        put({c0: it(), '999999.SH': it()}, {c0: ts_after, '999999.SH': ts_after})
        unlisted = cmc._ashare_checkpoint_load('20261124', '20161124')
        put({c0: it()}, {c0: 'nan'}, win='20200101')
        win_mismatch = cmc._ashare_checkpoint_load('20261124', '20161124')
        put({c0: it()}, {c0: ts_after})
        next_day = cmc._ashare_checkpoint_load('20261125', '20161124')
        same_day_late = cmc._ashare_checkpoint_load('20261124', '20161124',
                                                    now_ts=ts_late + 86400 * 7)
        put({c0: it()}, {c0: ts_after})
        with open(cmc.ASHARE_CHECKPOINT_PATH, 'w', encoding='utf-8') as fh:
            fh.write('{bad')
        badf = cmc._ashare_checkpoint_load('20261124', '20161124')
        check('§T4-h4c 不可续情形: 旧格式断点(无取数时刻)/缺取数时刻/清单外指数/窗口不一致/'
              '换日/坏档→{};同日数小时后再跑仍可续(不再受 1 小时超龄限制)',
              oldfmt == {} and sorted(miss_one) == [c0] and sorted(unlisted) == [c0]
              and win_mismatch == {} and next_day == {} and badf == {}
              and sorted(same_day_late) == [c0],
              (oldfmt, sorted(miss_one), sorted(unlisted), win_mismatch, next_day,
               badf, sorted(same_day_late)))

        # ── 真流程: 截断(h2)留下的断点 → 续采 ──
        put({}, {})
        with open(cmc.ASHARE_CHECKPOINT_PATH, 'w', encoding='utf-8') as fh:
            json.dump({'end_date': '20261124', 'window_start': '20161124',
                       'saved_at': ck2_fa[codes[0]], 'items': ck['items'],
                       'fetched_at': ck2_fa}, fh)
        cmc.CN_COLLECTOR_BUDGET_SECONDS = 60.0
        cmc._index_daily = idx_fast
        calls.clear()
        with contextlib.redirect_stdout(io.StringIO()):
            res4 = cmc.fetch_a_share_indices(
                checkpoint='ckpt', budget=cmc.CollectionBudget(limit_sec=60))
        resumed = list(cmc._STAGE_STATUS['a_share_indices']['resumed'])
        ck4 = _t4_json(cmc.ASHARE_CHECKPOINT_PATH)
        check('§T4-h4d 看门狗截断留下的断点(2 指数)续采: 已断点 2 个指数不再取网(仅余 4 次'
              '调用)、结果=六指数清单序、断点更新为全六指数且逐指数取数时刻在场'
              '(续来的 2 个保留原取数时刻)',
              calls == codes[2:] and list(res4) == codes and resumed == sorted(codes[:2])
              and list(ck4['items']) == codes and sorted(ck4['fetched_at']) == sorted(codes)
              and ck4['fetched_at'][codes[0]] == ck2_fa[codes[0]]
              and ck4['fetched_at'][codes[1]] == ck2_fa[codes[1]]
              and ck4['fetched_at'][codes[2]] > ck4['fetched_at'][codes[1]],
              (calls, resumed, list(ck4.get('items') or {}),
               sorted(ck4.get('fetched_at') or {})))
        with open(cmc.ASHARE_CHECKPOINT_PATH, 'w', encoding='utf-8') as fh:
            fh.write('{bad')
        calls.clear()
        with contextlib.redirect_stdout(io.StringIO()):
            res5 = cmc.fetch_a_share_indices(
                checkpoint='ckpt', budget=cmc.CollectionBudget(limit_sec=0.001))
        check('§T4-h5 预算已耗尽的逐指数协作式检查(无可续断点): 零取网、cut_by_budget=true、'
              '结果空',
              calls == [] and res5 == {}
              and cmc._STAGE_STATUS['a_share_indices']['cut_by_budget'] is True,
              (calls, res5))

        # ── 断点清除规则: 只用于恢复(全部阶段完成→清;仍有阶段未完整执行→留) ──
        put({c: it() for c in codes}, {c: ts_after for c in codes})
        stub_others()
        saved.clear()
        calls.clear()
        code, o = run_main()
        csx = saved[-1].get('collection_status') if saved else {}
        check('§T4-h5b 经 main() 续采(六指数全取自断点,零取网)+全部阶段完成→清断点;'
              '随档 a_share_checkpoint.resumed 列六指数',
              code is None and len(saved) == 1 and calls == []
              and csx.get('a_share_checkpoint', {}).get('resumed') == sorted(codes)
              and not os.path.exists(cmc.ASHARE_CHECKPOINT_PATH)
              and '断点保留' not in o,
              (code, calls, csx.get('a_share_checkpoint'),
               os.path.exists(cmc.ASHARE_CHECKPOINT_PATH), o[-160:]))

        def hook_margin(name):
            if name == 'fetch_margin':
                clock['t'] += 300.0
        put({c: it() for c in codes}, {c: ts_after for c in codes})
        stub_others(hook_margin)
        cmc.CN_COLLECTOR_BUDGET_SECONDS = 250.0
        fake_clock(100.0)
        saved.clear()
        try:
            code, o = run_main()
        finally:
            time.monotonic = real_mono
        csy = saved[-1].get('collection_status') if saved else {}
        check('§T4-h5c 仍有阶段被预算跳过(主日档照写、exit 无): 断点保留并提示'
              '「A股断点保留」——下次运行续采后腾出预算',
              code is None and len(saved) == 1
              and csy.get('stages', {}).get('valuation', {}).get('status') == 'skipped_budget'
              and os.path.exists(cmc.ASHARE_CHECKPOINT_PATH) and 'A股断点保留' in o,
              (code, json.dumps(csy.get('stages'), ensure_ascii=False)[:200],
               os.path.exists(cmc.ASHARE_CHECKPOINT_PATH), o[-160:]))
        cmc.CN_COLLECTOR_BUDGET_SECONDS = 60.0
        stub_others()
        # ── 央行公告走查: 协作式预算(假时钟;回看窗放大到不随运行日期变化) ──
        net = []
        links = ['202611%02d%09d' % (1 + i, 10000 + i) for i in range(12)]
        list_html = ''.join(
            '<a href="/zhengcehuobisi/125207/125213/125431/125475/%s/index.html">x</a>'
            % c for c in links)

        def curl_fake(url, max_time='30'):
            if ('zhengcehuobisi/125207/125213/125431/125475/index.html' in url
                    or '17081-' in url):
                return (list_html if ('index.html' in url and '17081-' not in url)
                        else '').encode('utf-8')
            clock['t'] += 100.0            # 每取一篇公告「耗时」100 秒
            return b'<html>ann</html>'

        def curl_count(url, max_time='30'):
            net.append(url)
            return curl_fake(url, max_time)
        os.makedirs(cmc.PBC_OMO_CACHE_DIR)
        for c in sorted(links, reverse=True)[:2]:       # 最新 2 篇已在缓存
            with open(os.path.join(cmc.PBC_OMO_CACHE_DIR, c + '.html'), 'w',
                      encoding='utf-8') as fh:
                fh.write('cached')
        cmc._curl_get = curl_count
        cmc._pboc_omo_parse_announcement = lambda h: {'7天': 1.5, '隔夜': 1.4}
        fake_clock(1000.0)
        net.clear()
        with contextlib.redirect_stdout(io.StringIO()):
            omo1 = cmc._pboc_omo_walk(back_days=400000, deadline=clock['t'] + 20.0)
        s1 = dict(cmc._OMO_WALK_STATUS)
        check('§T4-h6 走查预算将尽: 已缓存公告不论预算一律处理(cache_hits=2);未缓存'
              '新→旧取 1 篇后止(status=partial/stop_reason=budget/stopped_at 在场/'
              'pending_left=9);列表页照常翻(首页+空次页止)',
              s1.get('status') == 'partial' and s1.get('stop_reason') == 'budget'
              and s1.get('cache_hits') == 2 and s1.get('fetched') == 1
              and s1.get('processed') == 3 and s1.get('pending_left') == 9
              and bool(s1.get('stopped_at')) and s1.get('links_in_window') == 12
              and s1.get('pages') == 2 and len(omo1['7天']) == 3, s1)
        net.clear()
        fake_clock(5000.0)
        with contextlib.redirect_stdout(io.StringIO()):
            omo2 = cmc._pboc_omo_walk(back_days=400000)
        s2 = dict(cmc._OMO_WALK_STATUS)
        check('§T4-h7 无预算=旧行为: 全 12 篇处理(status=complete);已缓存的 3 篇'
              '不取网(fetched=9)',
              s2.get('status') == 'complete' and s2.get('stop_reason') is None
              and s2.get('processed') == 12 and s2.get('fetched') == 9
              and len(omo2['7天']) == 12, s2)
        net.clear()
        fake_clock(777.0)
        with contextlib.redirect_stdout(io.StringIO()):
            cmc._pboc_omo_walk(back_days=400000, deadline=clock['t'] + 3.0)
        s3 = dict(cmc._OMO_WALK_STATUS)
        check('§T4-h8 预算进门即不足(余 3 秒<15 秒单次取网储备): 列表页都不取'
              '(pages=0)、零取网、partial/budget',
              s3.get('pages') == 0 and net == [] and s3.get('status') == 'partial'
              and s3.get('stop_reason') == 'budget', (s3, net[:3]))
        cmc._em_series_rows = lambda url, fld: None
        sys.modules['akshare'] = types.SimpleNamespace(
            macro_china_lpr=lambda: pd.DataFrame())
        try:
            net.clear()
            fake_clock(777.0)
            with contextlib.redirect_stdout(io.StringIO()):
                ser = fms0(
                    budget=cmc.CollectionBudget(limit_sec=3))
        finally:
            cmc._em_series_rows = em0
            if ak_mod is None:
                sys.modules.pop('akshare', None)
            else:
                sys.modules['akshare'] = ak_mod
        check('§T4-h9 宏观全史阶段带预算: 公告走查按预算截止时刻协作式停止(OMO/CN_POLICY_'
              'OVERNIGHT 缺席、状态 partial/budget、零取网);其余端点照常',
              ser == {} and dict(cmc._OMO_WALK_STATUS).get('stop_reason') == 'budget'
              and net == [], (list(ser), dict(cmc._OMO_WALK_STATUS), net[:3]))

        # ── 阶段间协作式停止(假时钟) ───────────────────────────────────────
        def run_stages(limit, hook=None):
            fake_clock(100.0)
            b = cmc.CollectionBudget(limit_sec=limit)
            ad = {}
            with contextlib.redirect_stdout(io.StringIO()):
                stg, cut = cmc._collect_stages(ad, b)
            return ad, stg, cut

        def hook_margin(name):
            if name == 'fetch_margin':
                clock['t'] += 300.0
        stub_others(hook_margin)
        ad9, stg9, cut9 = run_stages(250.0)
        check('§T4-h10 非核心阶段(两融)耗尽预算→其后阶段 skipped_budget、核心阶段未被截断'
              '(cut=False→写主日档口径)',
              cut9 is False and stg9['margin']['status'] == 'ok'
              and all(stg9[k]['status'] == 'skipped_budget'
                      for k in ('valuation', 'turnover', 'ah_premium', 'macro', 'series'))
              and 'valuation' not in ad9 and 'margin' in ad9,
              json.dumps(stg9, ensure_ascii=False)[:300])

        def hook_ashare(name):
            if name == '_ashare_checkpoint_load':
                clock['t'] += 56.0           # A股阶段「耗时」56 秒
        stub_others()
        cmc._index_daily = idx_fast
        calls.clear()
        load0 = cmc._ashare_checkpoint_load
        cmc._ashare_checkpoint_load = lambda e, w, now_ts=None: (
            hook_ashare('_ashare_checkpoint_load') or {})
        try:
            ad10, stg10, cut10 = run_stages(60.0)
        finally:
            cmc._ashare_checkpoint_load = load0
        check('§T4-h11 核心阶段因预算未执行(港股 skipped_budget)同样不得写主日档'
              '(cut=True);A股阶段内逐指数协作式截断=零取网、阶段状态=cut_by_budget'
              '(修订 r2 更正: 原记 ok)',
              cut10 is True and stg10['a_share_indices']['status'] == 'cut_by_budget'
              and stg10['hk_indices']['status'] == 'skipped_budget'
              and calls == [] and ad10.get('a_share_indices') == {}
              and cmc._STAGE_STATUS['a_share_indices']['cut_by_budget'] is True,
              (cut10, calls, json.dumps(stg10, ensure_ascii=False)[:200]))

        def boom():
            raise RuntimeError('source exploded')
        stub_others()
        cmc.fetch_margin = boom
        fake_clock(100.0)
        raised = None
        try:
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    cmc._collect_stages({}, cmc.CollectionBudget(limit_sec=50.0))
            except RuntimeError as e:
                raised = str(e)
        finally:
            time.monotonic = real_mono
        check('§T4-h12 非预算异常照旧外泄(不吞;脚本崩=失败,与旧主程序同口径)',
              raised == 'source exploded', raised)
    finally:
        time.monotonic = real_mono
        cmc._curl_get, cmc._pboc_omo_parse_announcement = curl0, parse0
        cmc._em_series_rows = em0
        if ak_mod is None:
            sys.modules.pop('akshare', None)
        else:
            sys.modules['akshare'] = ak_mod
        cmc.CN_COLLECTOR_BUDGET_SECONDS = budget0
        cmc._disarm_watchdog()
    after = _t4_tree_files()
    check('§T4-h13 离线冒烟零落盘: 被测树文件清单与 mtime 前后一致(部分面/断点/缓存'
          '全在临时目录)',
          after == before, (sorted(set(after) - set(before))[:5],
                            sorted(set(before) - set(after))[:5]))















# ══ 任务5: 预期差研究接入正式入口 ════════════════════════════════════════
# 观点库夹具=tests/fixtures_r33/views(5 份合成文档: 全部虚构机构、虚构表述;
# 其中 1 份发布日晚于研究截止日=整篇不入对照,1 份违反 schema=装载即隔离)。
# 定价曲线=提交的冻结快照 fed_futures_curve。门内核: 问句判别/证伪窗口/地区/
# 点位解析(纯函数)→市场定价面与对照规则(门内独立复算)→对照块(逐行状态+
# 选定行独立复算/缺口/分歧/证伪池/事后表现/窗口可检性/冻结输入)→席位回声
# 契约(合格回声+反例矩阵)→引擎集成(离线 plan)→正式 CLI 链(真实步骤)。
# 覆盖边界: 门内无「attach 接收→report 可交付→归档」的正例(该型判定须完整
# 五面,见既有地图契约);预期差契约正例在函数级核验,真实全链由验收工单证明。
Q_T5 = ('2026年11月，美国、中国、日本和欧元区的宏观环境下，市场定价和机构观点'
        '之间有哪些预期差？未来半年什么会证伪？')
Q_T5_NOSHAPE = '未来半年市场定价和机构观点之间有哪些预期差？'
Q_PLAIN = ('美国、中国、欧元区、日本在最新一期分别处于什么增长、通胀和货币政策'
           '环境？过去三个月各有什么变化？')
VIEWS_FIX = os.path.join(FIX_R33, 'views')
T5_ASOF = '2026-11-22'
T5_METRICS_USED = ['FED_FUNDS', 'DFF', 'SPX', 'UST_10Y', 'JP_POLICY_RATE',
                   'ECB_DFR', 'EA_REAL_GDP_YOY', 'SPX_EPS', 'UNEMPLOYMENT']
T5_FROZEN = ['config/release_calendar.json', 'config/metric_registry.json',
             'data/daily/research_snapshot_20261122_v2.json',
             'config/forecast_target_map.json',
             'data/institutions/views/VIEW-20260905-001.json',
             'data/institutions/views/VIEW-20260915-002.json',
             'data/institutions/views/VIEW-20261120-003.json']
T5_CANDS = ['VIEW-20260915-002#f2', 'VIEW-20260915-002#f13',
            'VIEW-20261120-003#f1']
T5_READING = 'VIEW-20261120-003#f3'
T5_SUMMARY = {'n_views_visible': 3, 'n_views_withheld': 1, 'n_rows': 26,
              'n_out_of_scope': 0, 'comparable_n': 15, 'path_n': 7,
              'consistent_n': 3, 'inconsistent_n': 3, 'candidate_n': 3,
              'ex_post_consistent_n': 2, 'ex_post_missed_n': 3,
              'reading_required_n': 1, 'context_only_n': 3, 'unmapped_n': 2,
              'series_absent_n': 0, 'stale_fact_n': 1, 'gaps': 12,
              'blocked_class': None}
T5_STATUS = {
    'VIEW-20260905-001#f1': 'not_comparable', 'VIEW-20260905-001#f2': 'ex_post_missed',
    'VIEW-20260905-001#f3': 'ex_post_missed', 'VIEW-20260905-001#f4': 'library_inferred',
    'VIEW-20260905-001#f5': 'no_longer_current', 'VIEW-20260905-001#f6': 'ex_post_consistent',
    'VIEW-20260905-001#f7': 'ex_post_consistent', 'VIEW-20260915-002#f1': 'consistent',
    'VIEW-20260915-002#f2': 'inconsistent', 'VIEW-20260915-002#f3': 'consistent',
    'VIEW-20260915-002#f4': 'unparseable_horizon', 'VIEW-20260915-002#f5': 'unverifiable',
    'VIEW-20260915-002#f6': 'not_comparable', 'VIEW-20260915-002#f7': 'context_only',
    'VIEW-20260915-002#f8': 'consistent_stale_fact', 'VIEW-20260915-002#f9': 'fact_mismatch',
    'VIEW-20260915-002#f10': 'unmapped', 'VIEW-20260915-002#f11': 'context_only',
    'VIEW-20260915-002#f12': 'not_comparable', 'VIEW-20260915-002#f13': 'inconsistent',
    'VIEW-20260915-002#f14': 'context_only', 'VIEW-20260915-002#f15': 'unmapped',
    'VIEW-20261120-003#f1': 'inconsistent', 'VIEW-20261120-003#f2': 'ex_post_missed',
    'VIEW-20261120-003#f3': 'reading_required', 'VIEW-20261120-003#f4': 'consistent'}


def _xg():
    import expectations_gap
    return expectations_gap


def _t5_tree(tag, views='all', code=False):
    """预期差迷你树: config 副本+提交的冻结快照+合成观点库夹具(views='clean'
    去掉违反 schema 的那一份使 views lint 步通过;None=不放观点库);code=True
    另入代码副本。→ (tree, 快照路径)"""
    t, snap = _code_tree(tag) if code else _mk_tree(tag)
    if views:
        dst = os.path.join(t, 'data', 'institutions', 'views')
        shutil.copytree(VIEWS_FIX, dst)
        if views == 'clean':
            os.remove(os.path.join(dst, 'VIEW-20261010-005.json'))
    return t, snap


def _t5_block(t, snap_path, q=Q_T5, regions=('US', 'CN', 'EA', 'JP'),
              as_of=T5_ASOF, snap=None):
    """对照块(门内直调引擎;计划面=问句逐字+地区+问句证伪窗口)。"""
    xg = _xg()
    win = xg.parse_falsification_window(q, as_of)
    plan = {'question_verbatim': q, 'regions': list(regions),
            'region_source': 'question_named', 'expectations_gap': {'asked': True}}
    if win:
        plan['expectations_gap']['falsification_window'] = win
    sd = snap if snap is not None else _jq(snap_path)
    return xg.build_block(plan, sd, t, as_of, question=q,
                          reg_by_id=wd.load_registry(t)['by_id'])


def _t5_obs(sd, mid, on=None):
    """门内独立读数: 序列 mid 截至 on(含)的最新非空观测 → (日期, 值)|None。"""
    s = (sd.get('series_store') or {}).get(mid) or {}
    best = None
    for d, v in zip(s.get('dates') or [], s.get('values') or []):
        d = str(d)[:10]
        if v is None or (on and d > on):
            continue
        if best is None or d > best[0]:
            best = (d, v)
    return best


def _t5_curve(sd):
    """门内独立读曲线: 合约月名「YYYY年M月」→ 隐含月均利率;无法定月的行。"""
    curve, skipped = {}, []
    for row in sd.get('fed_futures_curve') or []:
        m = re.match(r'^\s*(\d{4})年(\d{1,2})月', str(row.get('name') or ''))
        rate = row.get('implied_avg_rate')
        if m and isinstance(rate, (int, float)) and rate == rate:
            curve['%s-%02d' % (m.group(1), int(m.group(2)))] = rate
        else:
            skipped.append(row.get('ticker'))
    return curve, skipped


def _t5_ids(items):
    return [x['row_id'] if isinstance(x, dict) else x for x in items or []]


def _t5_gap_codes(gaps):
    return [g if isinstance(g, str) else g.get('code') for g in gaps or []]


def _t5_days(ym):
    import calendar
    return calendar.monthrange(int(ym[:4]), int(ym[5:]))[1]


def _t5_prev(ym):
    y, m = int(ym[:4]), int(ym[5:])
    return '%04d-%02d' % (y - (m == 1), 12 if m == 1 else m - 1)


def _t5_step(chg, ym, v):
    """路径单步对照(门内独立算): 上月市场变动为基,本月整月走完 v bp;
    月内只走 v/天数。→ (下界, 上界, 在界内, 越界幅度 bp)。"""
    p, days, b = chg[_t5_prev(ym)], _t5_days(ym), chg[ym]
    lo, hi = ((p + v / days, p + v) if v >= 0 else (p + v, p + v / days))
    inb = (lo - 1.0) <= b <= (hi + 1.0)
    return (round(lo, 2), round(hi, 2), inb,
            0.0 if inb else round(lo - b if b < lo else b - hi, 2))


def _t5_count(chg, ym, n, sign, qual):
    """次数型对照(门内独立算): n 次=累计 n×25bp;至少=下界,至多=上界,
    约=半步带宽。→ (下界, 上界, 一致, 越界幅度 bp)。"""
    low = round((n - 1) * 25.0 + 25.0 / _t5_days(ym) - 1.0, 2)
    bb = round(chg[ym] * (1 if sign > 0 else -1), 2)
    if qual == 'at_most':
        hi, ok = round(n * 25.0 + 1.0, 2), bb <= round(n * 25.0 + 1.0, 2)
        return None, hi, ok, round(max(0.0, bb - hi), 2)
    if qual == 'at_least':
        ok = bb >= low
        return low, None, ok, round(max(0.0, low - bb), 2)
    hi = round(n * 25.0 + 12.5 + 1.0, 2)
    ok = low <= bb <= hi
    return low, hi, ok, round(0.0 if ok else max(low - bb, bb - hi), 2)


def _t5_hgap(chg, month, cum, lo_c, hi_c):
    """路径终点对照(门内独立算): 机构最后一步之后的首个整月合约,市场累计
    −机构累计;幅度≥半步(12.5bp)且方向不被次数限定词封死才算预期差。
    → (合约月, 差 bp, 成立, 方向)。"""
    fulls = [m for m in sorted(chg) if m + '-01' > T5_ASOF]
    nm = next((m for m in fulls if m > month), None)
    if not nm:
        return None
    g = round(chg[nm] - cum, 2)
    d = ('market_above_institution' if g > 0 else
         'market_below_institution' if g < 0 else None)
    if abs(g) >= 12.5 and d:
        if (d == 'market_above_institution' and hi_c) or \
                (d == 'market_below_institution' and lo_c):
            return nm, g, True, d
        return nm, g, False, d + '(至多/至少型声明,该方向不构成预期差)'
    return nm, g, False, None          # 不足半步: 引擎不标方向


def _t5_echo(blk, rr_supported=False, **over):
    """门内手搭的**合格回声**(仅函数级契约测试;非真实研判;数字只用引擎面
    已有的)。"""
    sm = blk['summary']
    cands = sorted(r['row_id'] for r in blk['rows'] if r.get('candidate') is True)

    def entry(rid, verdict):
        r = _row(blk['rows'], row_id=rid)
        e = {'row_id': rid, 'verdict': verdict,
             'reading': '门夹具席位推导(非真实研判): 该行机构路径与同期限市场定价相左。',
             'reading_attribution': 'ai_inferred',
             'competing_explanation': '门夹具竞争解释【假设】: 机构点位代表少数观点,市场定价已吸收更可能的路径。',
             'reason': '门夹具理由(非真实研判): 引擎确定性面对照为不一致。',
             'falsification_conditions': [{
                 'condition': '若 FED_FUNDS 在 2027-04-30 之前较截止日累计上行不足 12.5bp',
                 'attribution': 'ai_inferred'}],
             'evidence_refs': [rid]}
        if verdict == 'not_a_gap':
            e['falsification_conditions'] = None
        return e

    sup = [entry(c, 'supported') for c in cands]
    for r in blk['rows']:
        if r.get('status') == 'reading_required':
            sup.append(entry(r['row_id'], 'supported' if rr_supported
                             else 'not_a_gap'))
    echo = {'as_of': blk['as_of'], 'n_views_visible': sm['n_views_visible'],
            'n_rows': sm['n_rows'], 'comparable_n': sm['comparable_n'],
            'engine_candidate_n': sm['candidate_n'],
            'engine_candidates_echoed': cands,
            'gaps_echoed': [{'code': g.get('code'), 'region': g.get('region'),
                             'metric_id': g.get('metric_id')}
                            for g in blk.get('gaps') or []],
            'seat_summary': '门夹具席位总述(非真实研判): 引擎候选行逐行判定成立。',
            'supported_gaps': sup,
            'key_unknowns': ['门夹具关键未知: 目标区间上下限序列缺席,当前水平点位不可核。']}
    if isinstance(blk.get('falsification_window'), dict):
        echo['window_echo'] = {k: blk['falsification_window'][k]
                               for k in ('months', 'start', 'end')}
    echo.update(over)
    return echo


def _t5_skel(echo=None):
    """门夹具骨架判定(非真实研判): 只满足结构项(schema/归因/L3≥1/L4≥2),
    reader_map 只带预期差回声(地图五面缺席=既有五面契约照旧报缺)。"""
    rm = {'headline_conclusion': '门夹具骨架(非真实研判)。'}
    if echo is not None:
        rm['expectations_gap'] = echo
    return {
        'schema_version': '1.1',
        'agent_declaration': {
            'attribution': 'ai_inferred',
            'agent': '门夹具骨架(非真实研判;只验契约项与拒收路径)'},
        'l3': {'contradictions': [{
            'id': 'T5-FIX-C1',
            'statement': '门夹具陈述(非真实研判): 以引擎对照面为准。',
            'competing_explanations': ['门夹具解释甲(假设)', '门夹具解释乙(尚未验证)'],
            'evidence_refs': ['VIEW-20260915-002#f1']}],
            'mechanism_chains': []},
        'l4': {'scenarios': [
            {'id': 'T5-FIX-S1', 'role': '门夹具情景甲(假设)',
             'rows': {'scenario': '门夹具情景甲(假设)。'}},
            {'id': 'T5-FIX-S2', 'role': '门夹具情景乙(假设)',
             'rows': {'scenario': '门夹具情景乙(假设)。'}}]},
        'quality_gate_notes': ['门夹具(非真实研判)。'],
        'reader_map': rm}


def sec_t4_i():
    print('§T4-i 阶段行如实状态(修订 r2;2026-11-25 续采演习: 成交额各源失败曾被记为 '
          'ok/items 0 且无原因)')
    import china_market_collector as cmc
    before = _t4_tree_files()
    T = os.path.join(TMPG, 't4i')
    os.makedirs(T)
    names = ('PROJECT_DIR', 'DATA_DIR', 'TUSHARE_MONTHLY_CACHE_DIR',
             'ASHARE_CHECKPOINT_PATH', 'PBC_OMO_CACHE_DIR',
             'CN_COLLECTOR_BUDGET_SECONDS', 'save_data', 'get_trade_dates',
             'a_share_indices', 'hk_indices', 'southbound', 'margin',
             'valuation', 'turnover', 'ah_premium', 'macro', 'series',
             'fetch_a_share_indices', 'fetch_hk_indices', 'fetch_southbound',
             'fetch_margin', 'fetch_valuation', 'fetch_turnover',
             'fetch_ah_premium', 'fetch_macro', 'fetch_macro_series',
             '_ashare_checkpoint_clear', '_STAGE_STATUS')
    keep = {k: getattr(cmc, k, None) for k in names}
    keep_status = dict(cmc._STAGE_STATUS)
    real_out = sys.stdout
    try:
        for k in ('PROJECT_DIR', 'DATA_DIR', 'TUSHARE_MONTHLY_CACHE_DIR'):
            setattr(cmc, k, T)
        cmc.ASHARE_CHECKPOINT_PATH = os.path.join(T, 'ckpt.json')
        cmc.PBC_OMO_CACHE_DIR = os.path.join(T, 'pboc')
        cmc.CN_COLLECTOR_BUDGET_SECONDS = 0.0
        cmc.get_trade_dates = lambda: ('20261124', '20261114', '20260101')
        codes = list(cmc.A_SHARE_INDICES)
        ticks = list(cmc.HK_INDICES)

        def stub(val, prints=(), raise_=None):
            def f(*a, **k):
                for p in prints:
                    print(p)
                if raise_ is not None:
                    raise raise_
                return val() if callable(val) else val
            return f

        def install(**over):
            base = {'fetch_a_share_indices': {c: {'x': 1} for c in codes},
                    'fetch_hk_indices': {t: {'x': 1} for t in ticks},
                    'fetch_southbound': {'sb': 1}, 'fetch_margin': {'mg': 1},
                    'fetch_valuation': {'pe': 1}, 'fetch_turnover': {'to': 1},
                    'fetch_ah_premium': {'ah': 1}, 'fetch_macro': {'m': 1},
                    'fetch_macro_series': {'s': 1}}
            base.update(over)
            for n, v in base.items():
                setattr(cmc, n, v if callable(v) else stub(v))

        def run(limit=0.0):
            ad, buf = {}, io.StringIO()
            cmc._STAGE_STATUS.clear()
            err = None
            with contextlib.redirect_stdout(buf):
                out0 = sys.stdout
                try:
                    stg, cut = cmc._collect_stages(
                        ad, cmc.CollectionBudget(limit_sec=limit))
                except Exception as e:      # noqa: BLE001 — 断言外泄类型
                    stg, cut, err = None, None, e
                restored_inside = sys.stdout is out0
            return ad, stg, cut, buf.getvalue(), err, restored_inside

        # ── i1 续采演习复刻: 成交额两路来源失败(打印警示行后返回 None) ──
        w1 = "  ⚠️ Tushare成交额失败: HTTPConnectionPool(host='127.0.0.1', port=7890): Read timed out. (read timeout=30)"
        w2 = "  ⚠️ 东财成交额回落失败: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))"
        install()
        cmc.fetch_turnover = stub(None, prints=[w1, w2])
        ad1, stg1, cut1, o1, err1, rin1 = run()
        row1 = stg1['turnover']
        check('§T4-i1 阶段函数正常返回但零项(成交额两路来源失败)→ 阶段行 status=empty、'
              'items=0、notes=阶段内两条警示行(原文);stdout 原样透传(两行各出现一次);'
              '核心截断=False;其余阶段 ok',
              err1 is None and cut1 is False
              and row1['status'] == 'empty' and row1['items'] == 0
              and row1['notes'] == [w1.strip(), w2.strip()]
              and o1.count(w1) == 1 and o1.count(w2) == 1
              and ad1.get('turnover') is None
              and all(stg1[n]['status'] == 'ok' for n in (
                  'a_share_indices', 'hk_indices', 'southbound', 'margin',
                  'valuation', 'ah_premium', 'macro', 'series')),
              (err1, json.dumps(stg1, ensure_ascii=False)[:420]))

        # ── i2 静默零项 / 回落成功带原因 / 行数与长度上限 ──
        install()
        cmc.fetch_margin = stub({})
        cmc.fetch_valuation = stub({'pe': 1}, prints=[
            "  ❌ 沪深300估值: ReadTimeout: x", "  ✅ 沪深300估值 [乐咕回落]: PE=12.3"])
        cmc.fetch_ah_premium = stub({'ah': 1}, prints=[
            "  ❌ 第%d项失败 %s" % (i, "y" * 400) for i in range(12)])
        ad2, stg2, cut2, o2, err2, rin2 = run()
        check('§T4-i2 静默零项(两融返回空)→ empty 且 notes=[](空列表也是如实记录);'
              '回落成功的阶段(估值: ❌ 后 ✅[乐咕回落])仍 ok 但 notes 记下失败原因;'
              '警示行至多 8 行、每行截 300 字;✅/⏱️ 等非警示行不入 notes',
              err2 is None and stg2['margin']['status'] == 'empty'
              and stg2['margin']['notes'] == []
              and stg2['valuation']['status'] == 'ok'
              and stg2['valuation']['notes'] == ["❌ 沪深300估值: ReadTimeout: x"]
              and stg2['ah_premium']['status'] == 'ok'
              and len(stg2['ah_premium']['notes']) == 8
              and all(len(x) <= 300 for x in stg2['ah_premium']['notes'])
              and 'notes' not in stg2['southbound']
              and 'notes' not in stg2['a_share_indices'],
              json.dumps({k: stg2.get(k) for k in (
                  'margin', 'valuation', 'ah_premium', 'southbound')},
                  ensure_ascii=False)[:420])

        # ── i3 expected(固定清单阶段) ──
        install(fetch_hk_indices={ticks[0]: {'x': 1}})
        ad3, stg3, cut3, o3, err3, rin3 = run()
        check('§T4-i3 expected=应取项数(仅 A股/港股指数两项有固定清单的阶段): A股 '
              '%d、港股 %d;港股只取到 1 项→ items=1 < expected、仍 ok(缺项由下游 '
              'Gate A 按核心指标缺口处置,不改口径);其余阶段无 expected 键'
              % (len(codes), len(ticks)),
              err3 is None
              and stg3['a_share_indices']['expected'] == len(codes)
              and stg3['a_share_indices']['items'] == len(codes)
              and stg3['hk_indices']['expected'] == len(ticks)
              and stg3['hk_indices']['items'] == 1
              and stg3['hk_indices']['status'] == 'ok'
              and all('expected' not in stg3[n] for n in (
                  'southbound', 'margin', 'valuation', 'turnover', 'ah_premium',
                  'macro', 'series')),
              json.dumps([stg3['a_share_indices'], stg3['hk_indices']]))

        # ── i4 A股逐指数协作式截断(函数正常返回、状态表已标 cut_by_budget) ──
        install()
        cmc.fetch_a_share_indices = stub(
            lambda: cmc._STAGE_STATUS.update(
                {'a_share_indices': {'resumed': [], 'cut_by_budget': True}})
            or {})
        ad4, stg4, cut4, o4, err4, rin4 = run(limit=60.0)
        install()
        cmc.fetch_a_share_indices = stub({})
        ad4b, stg4b, cut4b, o4b, err4b, rin4b = run(limit=60.0)
        check('§T4-i4 A股逐指数协作式截断(函数正常返回、零取网)→ 阶段状态=cut_by_budget'
              '(修订 r2 更正: 原记 ok);状态表未标时同样返回空→ empty',
              err4 is None and stg4['a_share_indices']['status'] == 'cut_by_budget'
              and stg4['a_share_indices']['items'] == 0
              and err4b is None and stg4b['a_share_indices']['status'] == 'empty',
              json.dumps([stg4['a_share_indices'], stg4b['a_share_indices']]))

        # ── i5 看门狗截断行带截断前的警示行;异常外泄时 stdout 复位 ──
        install(fetch_turnover=stub(None, prints=["  ❌ 成交额取网超时"],
                                    raise_=cmc.BudgetExceeded('watchdog')))
        ad5, stg5, cut5, o5, err5, rin5 = run()
        boom = RuntimeError('source exploded')
        install(fetch_margin=stub(None, prints=["  ❌ 两融: x"], raise_=boom))
        ad5b, stg5b, cut5b, o5b, err5b, rin5b = run()
        check('§T4-i5 看门狗截断行(cut_by_budget)带截断前打印的警示行;阶段抛非预算'
              '异常照旧外泄且 sys.stdout 复位为进入阶段前的对象;两次运行后 stdout '
              '均为重定向目标本身(捕获器不残留)',
              err5 is None and cut5 is False
              and stg5['turnover']['status'] == 'cut_by_budget'
              and stg5['turnover']['notes'] == ["❌ 成交额取网超时"]
              and err5b is boom and rin5 and rin5b,
              (err5, json.dumps(stg5 and stg5.get('turnover')),
               type(err5b).__name__, rin5, rin5b))

        # ── i6 捕获器单元: 跨 write 的半行、透传保真、属性转发 ──
        orig = io.StringIO()
        tap = cmc._StageTap(orig)
        n1 = tap.write('  ⚠️ 半行')
        n2 = tap.write(' 继续\n普通行 ✅\n')
        tap.write('  ❌ 尾行无换行')
        tap.close()
        check('§T4-i6 _StageTap: 跨多次 write 的同一行拼成一条;无换行的尾行在 close '
              '入账;透传字节保真;write 返回值为原流返回值;flush/属性转发给原流',
              n1 == len('  ⚠️ 半行') and n2 == len(' 继续\n普通行 ✅\n')
              and orig.getvalue() == '  ⚠️ 半行 继续\n普通行 ✅\n  ❌ 尾行无换行'
              and tap.lines == ['⚠️ 半行 继续', '❌ 尾行无换行']
              and tap.isatty() is orig.isatty() and tap.flush() is None
              and tap.writable() is True,
              (tap.lines, orig.getvalue()))

        # ── i7 经 main(): 零项阶段不阻止清断点;汇总另出一行;退出码不变 ──
        saved, cleared = [], []
        install(fetch_turnover=stub(None, prints=[w1, w2]))
        cmc._STAGE_STATUS.clear()
        cmc.save_data = lambda d: saved.append(d) or 'saved'
        cmc._ashare_checkpoint_clear = lambda: cleared.append(1)
        with open(cmc.ASHARE_CHECKPOINT_PATH, 'w', encoding='utf-8') as fh:
            fh.write('{}')
        buf, code = io.StringIO(), None
        with contextlib.redirect_stdout(buf):
            try:
                cmc.main()
            except SystemExit as e:
                code = e.code
        o = buf.getvalue()
        cs = saved[-1].get('collection_status') if saved else {}
        check('§T4-i7 经 main(): 成交额零项→ 主日档照写(该键缺席)、退出码不变(无 '
              'exit)、阶段行 empty+notes、汇总出现「零项阶段 … 成交额」且不出现'
              '「时间预算」行;零项不阻止清断点(断点清除规则只看预算状态)',
              code is None and len(saved) == 1
              and saved[0].get('turnover') is None
              and cs.get('stages', {}).get('turnover', {}).get('status') == 'empty'
              and cs.get('stages', {}).get('turnover', {}).get('notes')
              == [w1.strip(), w2.strip()]
              and cs.get('core_cut_by_budget') is False
              and '零项阶段: 1 个(成交额)' in o and '时间预算:' not in o
              and 'A股断点保留' not in o and cleared == [1],
              (code, len(saved), json.dumps(cs.get('stages', {}).get('turnover'),
                                            ensure_ascii=False)[:300], o[-260:]))
    finally:
        for k, v in keep.items():
            setattr(cmc, k, v)
        cmc._STAGE_STATUS.clear()
        cmc._STAGE_STATUS.update(keep_status)
        sys.stdout = real_out
    after = _t4_tree_files()
    check('§T4-i8 离线检查零落盘: 被测树文件清单与 mtime 前后一致;采集器模块状态'
          '(路径/替身/状态表)全部复原',
          after == before and dict(cmc._STAGE_STATUS) == keep_status
          and cmc.ASHARE_CHECKPOINT_PATH == keep['ASHARE_CHECKPOINT_PATH'],
          (sorted(set(after) - set(before))[:5],
           sorted(set(before) - set(after))[:5]))


def sec_t4_j():
    print('§T4-j 任务4 修订 r3: 未成功步骤自己的输出尾入台账与回执(真 run_step / '
          '真 cmd_update / 真 cmd_doctor + 替身脚本)')
    import run_weekly as rw
    import ia_cli as ic
    sd = os.path.join(TMPG, 't4j', 'scripts')
    os.makedirs(sd)

    def _w(name, body):
        with open(os.path.join(sd, name), 'w', encoding='utf-8') as fh:
            fh.write(body)
    why = '原因: 同日快照不可变(需要 --allow-revision)'
    secret = 'SKt4jQ9x8L7p6V5b4N3m2C1z0'          # 替身密钥(非真实)
    raw_url = 'url https://h/p?api_key=' + secret
    red_url = 'url https://h/p?api_key=***REDACTED***'
    slow_line = 'slow start reason: waiting for rate limit'
    _w('ok.py', 'import time\nprint("ok line")\ntime.sleep(0.2)\n')
    _w('exit3.py', 'import os, sys\n'
                   'print("stdout progress 1")\n'
                   'print("UNBUF=%%s" %% os.environ.get("PYTHONUNBUFFERED"))\n'
                   'sys.stderr.write(%r + "\\n")\n'
                   'sys.stderr.write(%r + "\\n")\n'
                   'sys.exit(3)\n' % (why, raw_url))
    _w('slow.py', 'import time\nprint(%r)\ntime.sleep(30)\n' % slow_line)
    _w('grand.py', 'import subprocess, sys, time\n'
                   'subprocess.Popen(["sleep", "20"])\n'
                   'print("parent exiting rc=2")\n'
                   'sys.stdout.flush()\n'
                   'time.sleep(0.2)\n'
                   'sys.exit(2)\n')
    _w('flood.py', 'import sys\n'
                   'for i in range(40):\n'
                   '    print("line %02d" % i)\n'
                   '    print("")\n'
                   'print("L" * 600 + " END")\n'
                   'print("last line")\n'
                   'sys.exit(4)\n')
    _w('sig.py', 'import os, signal, time\n'
                 'os.kill(os.getpid(), signal.SIGTERM)\ntime.sleep(30)\n')

    rw.STEP_META.clear()
    cap_out, cap_err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(cap_out), contextlib.redirect_stderr(cap_err):
        r_ok = rw.run_step('s1', 'ok.py', timeout=5, script_dir=sd)
        r_x3 = rw.run_step('s3', 'exit3.py', timeout=5, script_dir=sd)
        t_g = time.monotonic()
        r_gr = rw.run_step('s7', 'grand.py', timeout=30, script_dir=sd)
        g_sec = time.monotonic() - t_g
        r_fl = rw.run_step('s8', 'flood.py', timeout=5, script_dir=sd)
        r_sg = rw.run_step('s4', 'sig.py', timeout=5, script_dir=sd)
        t_s = time.monotonic()
        r_slow = rw.run_step('s2', 'slow.py', timeout=1, script_dir=sd)
        slow_sec = time.monotonic() - t_s
    m = rw.STEP_META
    check('§T4-j1 真 run_step: 成功步骤无 output_tail 键;非零退出步骤带自己的原因行'
          '(stderr 尾);被信号终止的步骤带(可为空的)尾;返回码/原因分类不变',
          r_ok is True and 'output_tail' not in m['s1'] and m['s1']['exit_code'] == 0
          and r_x3 is False and m['s3']['exit_code'] == 3
          and m['s3']['fail_reason'] == 'nonzero_exit'
          and m['s3']['output_tail']['stderr'][0] == why
          and m['s3']['output_tail']['stdout'][0] == 'stdout progress 1'
          and r_sg is False and m['s4']['exit_code'] == -15
          and m['s4']['fail_reason'] == 'signal:15'
          and m['s4']['output_tail'] == {'stdout': [], 'stderr': []},
          {k: m.get(k) for k in ('s1', 's3', 's4')})
    check('§T4-j2 超时步骤: 被终止前已打印的行仍在尾(子进程不缓冲);孙进程继承并'
          '持有管道(本步 2 秒内退出、孙进程 20 秒)时 run_step 不挂起',
          r_slow is False and m['s2']['fail_reason'] == 'timeout'
          and m['s2']['timeout_sec'] == 1 and m['s2']['exit_code'] is None
          and m['s2']['output_tail']['stdout'] == [slow_line] and 1 <= slow_sec < 5
          and r_gr is False and g_sec < 8 and m['s7']['exit_code'] == 2
          and m['s7']['fail_reason'] == 'nonzero_exit'
          and m['s7']['output_tail']['stdout'] == ['parent exiting rc=2']
          and 'UNBUF=1' in m['s3']['output_tail']['stdout'],
          (slow_sec, g_sec, m.get('s2'), m.get('s7')))
    check('§T4-j3 入台账的尾已脱敏(含密钥的 URL→***REDACTED***,密钥字面不在台账'
          '数据内);透传到原输出流的内容不变(与 capture_output=False 同)',
          secret not in json.dumps(m, ensure_ascii=False)
          and m['s3']['output_tail']['stderr'][1] == red_url
          and raw_url in cap_err.getvalue() and why in cap_err.getvalue()
          and 'ok line' in cap_out.getvalue(),
          m.get('s3'))
    t = m['s8']['output_tail']['stdout']
    check('§T4-j4 尾部规模: 每流至多 6 个非空行、每行至多 240 字(空行不计,超长行截断)',
          m['s8']['exit_code'] == 4
          and t == ['line 36', 'line 37', 'line 38', 'line 39', 'L' * 240, 'last line']
          and m['s8']['output_tail']['stderr'] == [],
          t)
    _missing = object()
    _saved = sys.modules.get('redact_secrets', _missing)
    sys.modules['redact_secrets'] = None                # 让导入失败(脱敏器不可用)
    try:
        withheld = rw._tail_redacted({'stdout': ['x'], 'stderr': []})
    finally:
        if _saved is _missing:
            sys.modules.pop('redact_secrets', None)
        else:
            sys.modules['redact_secrets'] = _saved
    check('§T4-j5 汇总行与失败关闭: _tail_lines 每流末 3 行(非尾→[]);脱敏器不可导入'
          '时整段不写(留注,不带出未脱敏尾部),恢复后正常',
          rw._tail_lines({'stdout': ['o1', 'o2'], 'stderr': ['e1', 'e2', 'e3', 'e4']})
          == ['stderr| e2', 'stderr| e3', 'stderr| e4', 'stdout| o1', 'stdout| o2']
          and rw._tail_lines(None) == []
          and withheld == {'note': 'tail_withheld: redaction unavailable'}
          and rw._tail_lines(withheld)
          == ['输出尾未留: tail_withheld: redaction unavailable']
          and rw._tail_redacted({'stdout': ['x'], 'stderr': []})
          == {'stdout': ['x'], 'stderr': []},
          (withheld, rw._tail_redacted({'stdout': ['x'], 'stderr': []})))

    proj = os.path.join(TMPG, 't4j', 'proj')
    os.makedirs(proj)
    n1, n2, n4 = ('1/15 全球市场数据采集', '2/15 A股港股数据采集', '4/15 新闻采集与分析')
    tail_n2 = {'stdout': [], 'stderr': [why, red_url]}
    fake = rw.PipelineResults([(n1, True, True), (n2, False, True), (n4, False, False)])
    fake.meta = {n1: {'duration_sec': 12.0, 'exit_code': 0, 'fail_reason': None,
                      'output_tail': {'stdout': ['成功步骤的尾不得入台账']}},
                 n2: {'duration_sec': 0.7, 'exit_code': 3, 'fail_reason': 'nonzero_exit',
                      'output_tail': tail_n2},
                 n4: {'duration_sec': 1.0, 'exit_code': 1, 'fail_reason': None}}
    _orig_rp, _orig_pd = rw.run_pipeline, rw.PROJECT_DIR
    rw.run_pipeline = lambda steps, *a, **k: fake
    rw.PROJECT_DIR = proj
    out, rc = io.StringIO(), None
    try:
        with contextlib.redirect_stdout(out):
            try:
                rw.main([])
            except SystemExit as e:
                rc = e.code
    finally:
        rw.run_pipeline, rw.PROJECT_DIR = _orig_rp, _orig_pd
    led_files = glob.glob(os.path.join(proj, 'logs', 'pipeline_run_*.json'))
    led = _t4_json(led_files[0]) if led_files else {}
    rows = {r['name']: r for r in led.get('steps') or []}
    failed = led.get('failed_steps') or []
    text = ''
    if led_files:
        with open(led_files[0], encoding='utf-8') as fh:
            text = fh.read()
    check('§T4-j6 台账: 未成功行的 output_tail 随行入 steps 与 failed_steps;成功行'
          '(即使替身 meta 带)与未上报行不写;汇总逐步打印尾行(每流末 3 行)',
          len(led_files) == 1 and rc == 1
          and rows[n2].get('output_tail') == tail_n2
          and 'output_tail' not in rows[n1] and 'output_tail' not in rows[n4]
          and rows[n4]['fail_reason'] == 'unreported'
          and [r['name'] for r in failed] == [n2, n4]
          and failed[0].get('output_tail') == tail_n2
          and '成功步骤的尾不得入台账' not in text
          and ('stderr| ' + why) in out.getvalue()
          and ('stderr| ' + red_url) in out.getvalue(),
          (rc, failed, out.getvalue()[-300:]))

    def _run(tag, shim_body, files=None, ledger=None):
        tr = os.path.join(TMPG, 't4j_' + tag)
        os.makedirs(tr)
        with open(os.path.join(tr, 'run_weekly.py'), 'w', encoding='utf-8') as fh:
            fh.write(shim_body)
        for name, body in (files or {}).items():
            p = os.path.join(tr, name)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, 'w', encoding='utf-8') as fh:
                fh.write(body)
        if ledger:
            os.makedirs(os.path.join(tr, 'logs'))
            with open(os.path.join(tr, 'logs', ledger[0]), 'w',
                      encoding='utf-8') as fh:
                json.dump(ledger[1], fh, ensure_ascii=False)
        _orig = ic.ROOT
        ic.ROOT = tr
        out, rc = io.StringIO(), None
        try:
            with contextlib.redirect_stdout(out), \
                    contextlib.redirect_stderr(io.StringIO()):
                try:
                    ic.cmd_update(ic.build_parser().parse_args(['update', '--yes']))
                except SystemExit as e:
                    rc = e.code
        finally:
            ic.ROOT = _orig
        return rc, json.loads(out.getvalue()), tr

    from datetime import datetime as _dt
    okrow = {'name': '1/15 全球市场数据采集', 'ok': True, 'critical': True,
             'skipped': False, 'skip_reason': None, 'duration_sec': 3.5,
             'exit_code': 0, 'fail_reason': None}
    trow = {'name': '10/15 研究快照构建(Gate A)', 'ok': False, 'critical': True,
            'skipped': False, 'skip_reason': None, 'duration_sec': 0.7,
            'exit_code': 3, 'fail_reason': 'nonzero_exit',
            'output_tail': {'stdout': [], 'stderr': [why, raw_url]}}
    trow_pub = dict(trow, output_tail={'stdout': [], 'stderr': [why, red_url]})
    shim = ('import json, os\n'
            'from datetime import datetime\n'
            't0 = datetime.now()\n'
            'here = os.path.dirname(os.path.abspath(__file__))\n'
            'os.makedirs(os.path.join(here, "logs"))\n'
            'rows = json.loads(%r)\n'
            'blob = {"run_at": t0.isoformat(timespec="seconds"), '
            '"duration_sec": 903.5, "steps": rows, "success_count": 1, '
            '"failed_steps": [rows[1]], "snapshot_id": None, "gate_a": None}\n'
            'json.dump(blob, open(os.path.join(here, "logs", '
            '"pipeline_run_%%s.json" %% t0.strftime("%%Y%%m%%d")), "w"))\n'
            'print("all ok")\n' % json.dumps([okrow, trow], ensure_ascii=False))
    rc, env, tr = _run('upd', shim)
    d = env.get('data') or {}
    check('§T4-j7 update 回执: 台账行的 output_tail 随 steps/failed_steps 行带出并再过'
          '一次脱敏(密钥字面不在信封内);无该键的行形状不变(§T4-g5 的相等判定同受保护)',
          rc == 0 and d.get('steps') == [okrow, trow_pub]
          and d.get('failed_steps') == [trow_pub]
          and 'output_tail' not in d['steps'][0]
          and secret not in json.dumps(env, ensure_ascii=False),
          (rc, d.get('steps'), d.get('failed_steps')))
    led_blob = {'run_at': _dt.now().isoformat(timespec='seconds'),
                'steps': [okrow, trow], 'failed_steps': [trow], 'success_count': 1}
    rc, env, tr = _run('doc', 'print("done")\n', ledger=(
        'pipeline_run_%s.json' % _dt.now().strftime('%Y%m%d'), led_blob))
    _orig = ic.ROOT
    env_before = dict(os.environ)
    dout, drc = io.StringIO(), None
    try:
        ic.ROOT = tr
        with contextlib.redirect_stdout(dout), contextlib.redirect_stderr(io.StringIO()):
            try:
                ic.cmd_doctor(ic.build_parser().parse_args(['doctor']))
            except SystemExit as e:
                drc = e.code
    finally:
        ic.ROOT = _orig
        for k in list(os.environ):
            if k not in env_before:
                os.environ.pop(k, None)
        os.environ.update(env_before)
    lr = ((json.loads(dout.getvalue()).get('data') or {}).get('last_run') or {})
    cs = lr.get('critical_steps') or []
    check('§T4-j8 doctor 的 last_run.critical_steps: 未成功关键行的 output_tail 带出'
          '(已脱敏),成功行无此键',
          drc == 0 and len(cs) == 2 and 'output_tail' not in cs[0]
          and cs[1].get('output_tail') == trow_pub['output_tail']
          and secret not in dout.getvalue(),
          (drc, cs))

    _orig_popen = rw.subprocess.Popen

    def _boom(*a, **k):
        raise OSError('spawn boom (emfile)')
    rw.subprocess.Popen = _boom
    out_sp = io.StringIO()
    try:
        with contextlib.redirect_stdout(out_sp):
            r_sp = rw.run_step('s9', 'ok.py', timeout=5, script_dir=sd)
    finally:
        rw.subprocess.Popen = _orig_popen
    sp = m['s9']
    check('§T4-j9 进程起不来(OSError): 旧实现整轮裸崩无台账;现在该步记 spawn_failed+'
          '系统错误文本(已脱敏)入 output_tail、返回 False、汇总原因可读',
          r_sp is False and sp['exit_code'] is None and sp['fail_reason'] == 'spawn_failed'
          and sp['output_tail']['stderr'] == ['OSError: spawn boom (emfile)']
          and rw._fail_reason_text(sp).startswith('无法启动步骤进程')
          and '无法启动' in out_sp.getvalue(),
          (sp, out_sp.getvalue()[-120:]))


def sec_t5_a():
    print('§T5-a 问句判别/证伪窗口/地区/点位解析(纯函数;门内独立期望)')
    xg = _xg()
    import research_orchestrator as ro
    a = xg.asked(Q_T5)
    check('§T5-a1 问句判别: 「预期差」词形=问到;「机构观点」×「市场定价」并列='
          '问到;普通问句/原问零触发',
          a == {'gap': True, 'views': True, 'pricing': True}
          and xg.asked('机构观点与市场定价差在哪？')
          == {'gap': False, 'views': True, 'pricing': True}
          and xg.asked('有哪些预期差？')
          == {'gap': True, 'views': False, 'pricing': False}
          and not xg.is_asked('机构观点如何？')
          and not xg.is_asked('市场预期如何？')
          and not xg.is_asked(T3_TEXT) and not xg.is_asked(Q_T1)
          and not xg.is_asked(''),
          json.dumps(a, ensure_ascii=False))
    cases = [('未来半年什么会证伪？', 6, '2027-05-22'),
             ('未来六个月', 6, '2027-05-22'), ('接下来 3 个月', 3, '2027-02-22'),
             ('未来一年半', 18, '2028-05-22'),
             ('未来十二个月', 12, '2027-11-22'),
             ('未来 6 个月', 6, '2027-05-22'), ('今后两个月', 2, '2027-01-22'),
             ('未来两个季度', 6, '2027-05-22'),
             ('未来一个季度', 3, '2027-02-22'),
             ('未来2个季度', 6, '2027-05-22'),
             ('未来两季度', 6, '2027-05-22'),
             ('未来 3 个季度', 9, '2027-08-22')]
    got = {q: xg.parse_falsification_window(q, T5_ASOF) for q, _n, _e in cases}
    bad = {q: got[q] for q, n, e in cases
           if not (isinstance(got[q], dict) and got[q].get('months') == n
                   and got[q].get('start') == T5_ASOF and got[q].get('end') == e
                   and got[q].get('source') and got[q]['source'] in q)}
    check('§T5-a2 证伪窗口: 窗=研究截止日起 N 月(半年/六个月/N 个月/一年半/'
          '十二个月/季度=N×3 个月;中文与阿拉伯数字、带不带「个」同解;'
          'source 为问句子串)', not bad, bad)
    none_q = ['过去半年', '过去两个季度', '未来半个月', '未来三个月半', '什么会证伪', '']
    check('§T5-a3 窗口未指明/不支持词形(回看/半个月/三个月半)=None,不臆造',
          all(xg.parse_falsification_window(q, T5_ASOF) is None for q in none_q),
          [q for q in none_q
           if xg.parse_falsification_window(q, T5_ASOF) is not None])
    check('§T5-a4 月末钳制: 2026-08-31+6 月=2027-02-28;2027-01-31+1 月=2027-02-28',
          (xg.parse_falsification_window('未来半年', '2026-08-31') or {})
          .get('end') == '2027-02-28'
          and (xg.parse_falsification_window('未来一个月', '2027-01-31') or {})
          .get('end') == '2027-02-28')
    rcases = [(Q_T5, ['US', 'CN', 'EA', 'JP'], 'question_named'),
              ('日本和欧元区有哪些预期差？', ['EA', 'JP'], 'question_named'),
              ('美国的机构观点和市场定价有何预期差？', ['US'], 'question_named'),
              ('日本央行和欧央行路径上有哪些预期差？', ['EA', 'JP'],
               'question_named'),
              (Q_T5_NOSHAPE, ['US', 'CN', 'EA', 'JP'], 'default_all_registered'),
              ('全球预期差?', ['US', 'CN', 'EA', 'JP'], 'default_all_registered'),
              ('有哪些预期差？', ['US', 'CN', 'EA', 'JP'],
               'default_all_registered')]
    reg = wd.load_registry(ROOT)
    rbad = []
    for q, exp, src in rcases:
        g = xg.plan_regions(q, ro.map_entities(q, reg))
        if [list(g[0]), g[1]] != [exp, src]:
            rbad.append((q[:16], g))
    check('§T5-a5 地区: 问句点名经济体/央行→按问句;无点名→四地全注册'
          '(来源如实标注 default_all_registered)', not rbad, rbad)
    pcases = [('2026年9月加息 25bp', 'change_bp', {'value': 25.0}),
              ('降息 15bp', 'change_bp', {'value': -15.0}),
              ('2027年6月前至少加息2次', 'hike_count',
               {'count': 2, 'sign': 1, 'qualifier': 'at_least'}),
              ('至多加息1次', 'hike_count',
               {'count': 1, 'sign': 1, 'qualifier': 'at_most'}),
              ('约加息2次', 'hike_count',
               {'count': 2, 'sign': 1, 'qualifier': 'about'}),
              ('加息两次', 'hike_count',
               {'count': 2, 'sign': 1, 'qualifier': 'exact'}),
              ('2026年+25%', 'growth_pct', {'value': 25.0}),
              ('-0.5%', 'growth_pct', {'value': -0.5}),
              ('3.75%–4.00%', 'level_range',
               {'lo': 3.75, 'hi': 4.0, 'unit': 'percent'}),
              ('4.25%', 'level', {'value': 4.25, 'unit': 'percent'}),
              ('7500', 'level', {'value': 7500.0, 'unit': None}),
              ('2026年 2.1%，2027年 2.3%', 'multi', {'values': [2.1, 2.3]}),
              ('维持数据依赖立场', 'text', {'value': None}),
              ('2027年3月前加息约2次', 'text', {'value': None})]
    pbad = []
    for txt, kind, exp in pcases:
        p = xg.parse_point(txt)
        if not (isinstance(p, dict) and p.get('kind') == kind
                and all(p.get(k) == v for k, v in exp.items())):
            pbad.append((txt, p))
    check('§T5-a6 点位解析: 幅度型(bp,升为正降为负)/次数型(至少/至多/约/'
          '中文数字)/增速型/区间型/水平型/多年多值=文字型;量词在动词后的'
          '「加息约2次」引擎不解读=文字型(已披露限制)', not pbad, pbad)
    ent = ro.map_entities(Q_T5, reg)
    ent2 = ro.map_entities(Q_T5_NOSHAPE, reg)
    check('§T5-a7 问句族别: 预期差问句(含无地图词形者)=map;普通地图问句维持',
          rmp.question_kind(Q_T5, ent) == 'map'
          and rmp.question_kind(Q_T5_NOSHAPE, ent2) == 'map'
          and rmp.detect_map_question(Q_T5, ent) is True
          and rmp.detect_map_question(Q_T5_NOSHAPE, ent2) is False
          and _kind(Q_PLAIN) == 'map'
          and _kind('美国未来一年增长通胀如何') is None)
    tm = xg.load_target_map(ROOT)
    check('§T5-a8 目标→指标映射: 规范表命中的照旧;补充映射(政策路径基线/'
          '目标区间/日银政策利率/标普目标)带 r33_supplement 来源;未映射=None',
          xg.resolve_metric('美国失业率', tm)
          == ('UNEMPLOYMENT', 'canonical:config/forecast_target_map.json')
          and xg.resolve_metric('fed_policy_path_baseline', tm)[0] == 'FED_FUNDS'
          and xg.resolve_metric('fed_funds_target_range', tm)[0] == 'DFEDTARU'
          and xg.resolve_metric('BOJ_policy_rate', tm)[0] == 'JP_POLICY_RATE'
          and xg.resolve_metric('SPX_12m_target', tm) == ('SPX', 'r33_supplement')
          and xg.resolve_metric('中国贷款市场报价利率', tm) == (None, None)
          and xg.resolve_metric('全球增长前景', tm) == (None, None))
    check('§T5-a9 到期日: 目标名内嵌月份可解;文档期限 Nm=发布日+N 月;其余 None',
          xg._date_from_target('US_10y_yield_endSep2026') == '2026-09-30'
          and xg._date_from_target('SPX_12m_target') is None
          and xg.view_horizon_end({'publish_date': '2026-09-15',
                                   'view_horizon': '12m'}) == '2027-09-15'
          and xg.view_horizon_end({'publish_date': '2026-11-20',
                                   'view_horizon': '6m'}) == '2027-05-20'
          and xg.view_horizon_end({'publish_date': '2026-11-20',
                                   'view_horizon': 'other'}) is None)


def sec_t5_b():
    print('§T5-b 市场定价面与对照规则(门内独立复算)')
    xg = _xg()
    t, snap = _t5_tree('t5b')
    sd = _jq(snap)
    reg = wd.load_registry(t)['by_id']
    curve, skipped = _t5_curve(sd)
    dff = _t5_obs(sd, 'DFF', T5_ASOF)
    chg = {ym: round((r - dff[1]) * 100.0, 2) for ym, r in curve.items()}
    fb = xg.Facts(sd, t, T5_ASOF, reg)
    face = xg.build_pricing(fb, sd, t, T5_ASOF)
    rows = {r['month']: r for r in face['rows']}
    fulls = [m for m in sorted(curve) if m + '-01' > T5_ASOF]
    check('§T5-b1 市场定价面(运行快照,版本日≤截止日): 10 合约月逐点=快照曲线'
          '(门内独立读),变动 bp=隐含−截止日有效利率(DFF@2026-11-19 3.88);'
          '非合约月行跳过并记因;整月在前=次月起;无目标区间=无中点基线',
          len(curve) == 10 and face['status'] == 'present'
          and face['basis'] == 'run_snapshot'
          and face['source_target_date'] == T5_ASOF
          and face['baseline']['evidence_ref'] == 'DFF@2026-11-19'
          and face['baseline']['value'] == dff[1] == 3.88
          and sorted(rows) == sorted(curve)
          and all(rows[m]['implied_avg_rate'] == curve[m]
                  and rows[m]['change_bp'] == chg[m] for m in curve)
          and [s['reason'] for s in face['skipped_rows']]
          == ['no_contract_month'] * len(skipped) and len(skipped) == 1
          and face['full_months_ahead'] == fulls and len(fulls) == 9
          and face['last_month'] == '2027-08' and face['midpoint'] is None
          and not face['gaps'],
          f"n={len(rows)} skipped={skipped} fulls={len(fulls)}")
    scases = [('2026-12', 25), ('2027-03', 25), ('2027-03', -25),
              ('2027-01', -300), ('2027-01', 100), ('2027-02', 5),
              ('2027-02', 1)]
    sbad = []
    for ym, v in scases:
        g = xg.compare_path_step(face, ym, v)
        lo, hi, inb, dist = _t5_step(chg, ym, v)
        if not (g['in_bound'] is inb and g['distance_bp'] == dist
                and g['market_change_bp'] == chg[ym]
                and g['market_prev_change_bp'] == chg[_t5_prev(ym)]
                and g['bases_checked'] == 1
                and (not inb or (g['bound_lo'] == lo and g['bound_hi'] == hi))):
            sbad.append((ym, v, g, (lo, hi, inb, dist)))
    check('§T5-b2 路径单步对照(门内独立算): 升/降/大幅/小幅逐例一致;曲线外'
          '合约月=无基线可核(in_bound None)',
          not sbad
          and xg.compare_path_step(face, '2027-10', 25)['bases_checked'] == 0
          and xg.compare_path_step(face, '2027-10', 25)['in_bound'] is None,
          sbad)
    ccases = [('2027-06', 2, 1, 'at_least'), ('2027-06', 1, 1, 'at_most'),
              ('2027-03', 2, 1, 'about'), ('2027-06', 4, 1, 'at_least'),
              ('2027-01', 1, -1, 'at_least')]
    cbad = []
    for ym, n, sign, qual in ccases:
        g = xg.compare_hike_count(face, ym, n, sign, qual)
        lo, hi, ok, dist = _t5_count(chg, ym, n, sign, qual)
        if not (g['consistent'] is ok and g['distance_bp'] == dist
                and g['bound_lo'] == lo and g['bound_hi'] == hi
                and g['market_change_bp'] == chg[ym]
                and g['market_hike_equivalents']
                == round(chg[ym] * sign / 25.0, 2)):
            cbad.append((ym, n, sign, qual, g, (lo, hi, ok, dist)))
    check('§T5-b3 次数型对照(门内独立算): 至少 N 次=下界/至多 N 次=上界/'
          '约 N 次=半步带宽;降息方向按符号取反;「至少加息 4 次」对市场 '
          '56bp 越界 18.83bp', not cbad
          and xg.compare_hike_count(face, '2027-06', 4, 1, 'at_least')
          ['distance_bp'] == 18.83, cbad)
    hcases = [('2027-03', 25, True, True), ('2026-12', 25, True, True),
              ('2027-03', 75, True, True), ('2027-06', 25, False, True)]
    hbad = []
    for month, cum, lo_c, hi_c in hcases:
        g = xg._horizon_gap(face, month, cum, lo_c, hi_c)
        exp = _t5_hgap(chg, month, cum, lo_c, hi_c)
        if not (g['assessable'] is True and g['month'] == exp[0]
                and g['gap_bp'] == exp[1] and g['material'] is exp[2]
                and g['direction'] == exp[3]
                and g['evidence_ref'] == 'FEDFUNDS_FUT:' + g['ticker']):
            hbad.append((month, cum, g, exp))
    check('§T5-b4 路径终点对照(门内独立算): 机构末步之后首个整月合约;幅度≥'
          '半步 12.5bp 才成立;「至多加息」行市场高于机构不构成预期差(方向'
          '标注);曲线尽头之后=不可评估', not hbad
          and _t5_hgap(chg, '2027-03', 25, True, True)
          == ('2027-04', 23.5, True, 'market_above_institution')
          and _t5_hgap(chg, '2027-03', 75, True, True)
          == ('2027-04', -26.5, True, 'market_below_institution')
          and xg._horizon_gap(face, '2027-08', 25, True, True)['assessable']
          is False, hbad)
    f_old = xg.build_pricing(fb, sd, t, '2025-11-15')
    v = copy.deepcopy(sd)
    v['snapshot_id'] = 'FIXTURE_t5_vintage_20261115'
    v['target_date'] = '2026-11-15'
    v['fixture_note'] = 'Audit-R33 门夹具: 定价版本回退用构造件(非真实)'
    v['fed_futures_curve'] = [{'ticker': 'FIXTURE_ZQZ26', 'name': '2026年12月',
                               'implied_avg_rate': 4.0, 'price': 95.0}]
    vp = os.path.join(t, 'data', 'daily', 'FIXTURE_t5_vintage_20261115.json')
    with open(vp, 'w', encoding='utf-8') as fh:
        json.dump(v, fh, ensure_ascii=False)
    rs = copy.deepcopy(sd)
    rs['target_date'] = '2026-12-01'
    rs['evidence_gate'] = {'vintage': {'vintage_snapshot': vp}}
    f_v = xg.build_pricing(xg.Facts(rs, t, T5_ASOF, reg), rs, t, T5_ASOF)
    v2 = copy.deepcopy(v)
    v2['target_date'] = '2026-12-10'
    with open(vp, 'w', encoding='utf-8') as fh:
        json.dump(v2, fh, ensure_ascii=False)
    f_v2 = xg.build_pricing(xg.Facts(rs, t, T5_ASOF, reg), rs, t, T5_ASOF)
    check('§T5-b5 定价面版本绑定: 研究时点早于运行快照版本日→不借用今日曲线'
          '(缺席+pricing_absent_at_cutoff);运行快照晚于截止日→回退 as-of '
          '版本快照(来源如实标注);版本日亦晚于截止日→缺席',
          f_old['status'] == 'absent'
          and _t5_gap_codes(f_old['gaps']) == ['pricing_absent_at_cutoff']
          and f_v['status'] == 'present'
          and f_v['basis'] == 'as_of_vintage_snapshot'
          and f_v['source_snapshot_id'] == 'FIXTURE_t5_vintage_20261115'
          and f_v['source_target_date'] == '2026-11-15'
          and [(r['month'], r['implied_avg_rate'], r['change_bp'])
               for r in f_v['rows']] == [('2026-12', 4.0, 12.0)]
          and f_v2['status'] == 'absent'
          and _t5_gap_codes(f_v2['gaps']) == ['pricing_absent_at_cutoff'],
          f"old={f_old['status']} {f_old['gaps']} v={f_v['basis']} "
          f"{f_v['rows'][:1]} v2={f_v2['status']} {f_v2['gaps']}")
    ff = _t5_obs(sd, 'FED_FUNDS', T5_ASOF)
    at = fb.at('FED_FUNDS')
    at_d = fb.at('DFF')
    un = _t5_obs(sd, 'UNEMPLOYMENT', '2026-10-31')
    near = xg.fact_near(fb, 'UNEMPLOYMENT', '2026-10-31', 'monthly')
    import datetime as _dt
    age = (_dt.date(2026, 11, 22)
           - _dt.date.fromisoformat(ff[0])).days
    check('§T5-b6 事实读数: 序列≤截止日最新观测(门内独立读)附证据引用/发布'
          '口径/龄期;月频龄期 52 天>45=陈旧;序列缺席=missing;定点邻近读数'
          '带容差与距离;远端到期日=陈旧',
          at['value'] == ff[1] == 3.88 and at['observation_date'] == ff[0]
          == '2026-10-01' and at['evidence_ref'] == 'FED_FUNDS@2026-10-01'
          and at['age_days'] == age and at['stale'] is True
          and at['stale_after_days'] == 45
          and at_d['observation_date'] == '2026-11-19' and at_d['age_days'] == 3
          and 'stale' not in at_d
          and fb.at('DFEDTARU')['status'] == 'missing'
          and near['status'] == 'ok' and near['value'] == un[1] == 4.1
          and near['distance_days'] == -30 and near['tolerance_days'] == 45
          and xg.fact_near(fb, 'FED_FUNDS', '2027-06-30', 'monthly')['status']
          == 'fact_stale_at_horizon'
          and xg.fact_near(fb, 'DFEDTARU', T5_ASOF, 'daily')['status']
          == 'missing',
          f"at={at['value']}@{at['observation_date']} age={at['age_days']} "
          f"near={near}")
    m_d = {'unit': 'percent', 'frequency': 'daily'}
    m_m = {'unit': 'percent', 'frequency': 'monthly'}
    m_i = {'unit': 'index_point', 'frequency': 'daily'}
    spx = _t5_obs(sd, 'SPX', '2026-09-30')
    check('§T5-b7 水平容差: 利率日频 0.02/非日频 0.05 个百分点;其余=读数×0.5%;'
          '事实缺席=unverifiable;频率族陈旧阈值',
          xg._level_verdict(2.5, {'value': 2.5}, m_d)['verdict'] == 'matches'
          and xg._level_verdict(2.5, {'value': 2.5}, m_d)['tolerance'] == 0.02
          and xg._level_verdict(2.56, {'value': 2.5}, m_d)['verdict']
          == 'differs'
          and xg._level_verdict(2.54, {'value': 2.5}, m_m)['verdict']
          == 'matches'
          and xg._level_verdict(2.56, {'value': 2.5}, m_m)['verdict']
          == 'differs'
          and xg._level_verdict(7680.0, {'value': spx[1]}, m_i)['tolerance']
          == round(abs(spx[1]) * 0.005, 6) == 38.2577
          and xg._level_verdict(7680.0, {'value': spx[1]}, m_i)['verdict']
          == 'matches'
          and xg._level_verdict(7690.0, {'value': spx[1]}, m_i)['verdict']
          == 'differs'
          and xg._level_verdict(4.0, None, m_d)['verdict'] == 'unverifiable'
          and [xg._stale_after(f) for f in
               ('daily', 'weekly', 'monthly', 'quarterly', None)]
          == [10, 14, 45, 100, 45],
          f"{spx} {xg._level_verdict(7680.0, {'value': spx[1]}, m_i)}")


def sec_t5_c():
    print('§T5-c 预期差对照块(合成观点库夹具×提交的冻结快照;虚构机构)')
    xg = _xg()
    t, snap = _t5_tree('t5c')
    sd = _jq(snap)
    blk = _t5_block(t, snap)
    rows = {r['row_id']: r for r in blk['rows']}
    curve, _sk = _t5_curve(sd)
    dff = _t5_obs(sd, 'DFF', T5_ASOF)
    chg = {ym: round((r - dff[1]) * 100.0, 2) for ym, r in curve.items()}
    check('§T5-c1 对照块: 单型块(问句逐字/截止日/四地/证伪窗口)+汇总'
          '(可见 3 扣留 1/26 行/可对账 15/候选 3/须推导 1/缺口 12/无阻断)',
          blk['schema'] == xg.SCHEMA and blk['asked'] is True
          and blk['question_verbatim'] == Q_T5 and blk['as_of'] == T5_ASOF
          and blk['regions'] == ['US', 'CN', 'EA', 'JP']
          and blk['region_source'] == 'question_named'
          and blk['falsification_window']
          == {'months': 6, 'start': T5_ASOF, 'end': '2027-05-22',
              'source': '未来半年'}
          and blk['summary'] == T5_SUMMARY,
          json.dumps(blk['summary'], ensure_ascii=False))
    man = {}
    for fn in sorted(os.listdir(VIEWS_FIX)):
        with open(os.path.join(VIEWS_FIX, fn), 'rb') as fh:
            man['data/institutions/views/' + fn] = hashlib.sha256(
                fh.read()).hexdigest()
    vw = blk['views']
    check('§T5-c2 观点库装载: 5 件=合规 4+隔离 1(违反 schema);发布日晚于'
          '截止日的整篇扣留并记因;清单 sha256=门内独立算',
          vw['status'] == 'present' and vw['n_files'] == 5
          and vw['n_compliant'] == 4 and vw['n_quarantined'] == 1
          and vw['quarantined'][0]['view_id'] == 'VIEW-20261010-005'
          and vw['manifest'] == man
          and [(w['view_id'], w['publish_date'], w['reason'])
               for w in blk['withheld_after_cutoff']]
          == [('VIEW-20261201-004', '2026-12-01', 'publish_after_cutoff')]
          and not any('VIEW-20261201-004' in r['view_id']
                      or 'VIEW-20261010-005' in r['view_id']
                      for r in blk['rows']),
          json.dumps(vw['quarantined'], ensure_ascii=False))
    check('§T5-c3 逐行状态(26 行): 到期点位=事后表现/一致·不一致·次数型/'
          '当前水平型对事实/未映射/文字型=须席位推导/背景',
          {k: r['status'] for k, r in rows.items()} == T5_STATUS
          and sorted(r['row_id'] for r in blk['rows'] if r.get('candidate')
                     is True) == sorted(T5_CANDS)
          and [k for k, r in rows.items() if r['status'] == 'reading_required']
          == [T5_READING]
          and all(r.get('candidate_reason') for r in blk['rows']
                  if r.get('candidate') is True),
          {k: r['status'] for k, r in rows.items()
           if T5_STATUS.get(k) != r['status']})
    r = rows['VIEW-20260915-002#f1']
    st = r['comparison']['step']
    hg = r['comparison']['horizon_gap']
    lo, hi, inb, _d = _t5_step(chg, '2026-12', 25)
    check('§T5-c4 路径行独立复算·一致: 2026-12 加息 25bp 对 2026-12 合约'
          '(上月市场变动 0→界 [0.81,25] 含 16);终点 2027-01 市场−机构 −1.0'
          '不足半步=非候选',
          st['in_bound'] is True and st['bound_lo'] == lo == 0.81
          and st['bound_hi'] == hi == 25.0 and st['market_change_bp'] == 16.0
          and hg['month'] == '2027-01' and hg['gap_bp'] == -1.0
          and hg['material'] is False and r['cum_inst_bp'] == 25.0
          and r['status'] == 'consistent' and r['candidate'] is False
          and r['comparable_kind'] == 'path_vs_pricing',
          f"{st} {hg}")
    r = rows['VIEW-20260915-002#f2']
    st = r['comparison']['step']
    hg = r['comparison']['horizon_gap']
    lo, hi, inb, _d = _t5_step(chg, '2027-03', 50)
    check('§T5-c5 路径行独立复算·候选: 2027-03 加息 50bp 单步在界'
          '([38.11,86.5] 含 42);累计 75 对终点 2027-04 市场 48.5=−26.5bp≥'
          '半步=预期差候选(市场低于机构)',
          st['in_bound'] is True and st['bound_lo'] == lo == 38.11
          and st['bound_hi'] == hi == 86.5 and hg['month'] == '2027-04'
          and hg['gap_bp'] == -26.5 and hg['material'] is True
          and hg['direction'] == 'market_below_institution'
          and r['cum_inst_bp'] == 75.0 and r['status'] == 'inconsistent'
          and r['candidate'] is True, f"{st} {hg}")
    r = rows['VIEW-20261120-003#f1']
    st = r['comparison']['step']
    hg = r['comparison']['horizon_gap']
    lo, hi, inb, dist = _t5_step(chg, '2027-01', -25)
    check('§T5-c6 路径行独立复算·候选(降息方向): 2027-01 降息 25bp 对市场 '
          '+24 越界 8.81bp;终点 2027-02 市场 36.5−(−25)=+61.5=候选(市场高于'
          '机构)',
          st['in_bound'] is False and st['distance_bp'] == dist == 8.81
          and st['bound_lo'] is None and hg['month'] == '2027-02'
          and hg['gap_bp'] == 61.5 and hg['material'] is True
          and hg['direction'] == 'market_above_institution'
          and r['cum_inst_bp'] == -25.0 and r['candidate'] is True
          and r['direction'] == 'down', f"{st} {hg}")
    r = rows['VIEW-20260915-002#f13']
    cc = r['comparison']['count_check']
    hg = r['comparison']['horizon_gap']
    lo, hi, ok, dist = _t5_count(chg, '2027-06', 1, 1, 'at_most')
    check('§T5-c7 次数行独立复算·候选: 「2027 年 6 月前至多加息 1 次」上界 '
          '26bp,市场 56bp 越界 30bp;终点 2027-07 差 32.5bp(至多型:市场高于'
          '机构方向成立)',
          cc['consistent'] is False and cc['distance_bp'] == dist == 30.0
          and cc['bound_hi'] == hi == 26.0 and cc['bound_lo'] == lo
          and hg['gap_bp'] == 32.5 and hg['material'] is True
          and r['cum_inst_bp'] == 25.0 and r['candidate'] is True,
          f"{cc} {hg}")
    r = rows['VIEW-20260915-002#f3']
    cc = r['comparison']['count_check']
    hg = r['comparison']['horizon_gap']
    lo, hi, ok, dist = _t5_count(chg, '2027-06', 2, 1, 'at_least')
    check('§T5-c8 次数行独立复算·一致: 「至少加息 2 次」下界 24.83≤市场 56;'
          '终点 2027-07 差 7.5bp 不足半步',
          cc['consistent'] is True and cc['bound_lo'] == lo == 24.83
          and cc['bound_hi'] is None and cc['market_hike_equivalents'] == 2.24
          and hg['month'] == '2027-07' and hg['gap_bp'] == 7.5
          and hg['material'] is False and r['status'] == 'consistent',
          f"{cc} {hg}")
    r = rows['VIEW-20260905-001#f1']
    check('§T5-c9 路径行·到期月不在曲线内(2026-09): 单步无基线;终点 2026-12 '
          '差 −9.0 不足半步=不可对照(不判)',
          r['comparison']['step']['bases_checked'] == 0
          and r['comparison']['horizon_gap']['gap_bp'] == -9.0
          and r['comparison']['horizon_gap']['material'] is False
          and r['status'] == 'not_comparable' and r['candidate'] is None,
          f"{r['comparison']}")
    ex = {x['row_id']: x for k in ('forecast_claims', 'realized_data_claims')
          for x in blk['ex_post'][k]['rows']}
    spx = _t5_obs(sd, 'SPX', '2026-09-30')
    ust = _t5_obs(sd, 'UST_10Y', '2026-09-30')
    unr = _t5_obs(sd, 'UNEMPLOYMENT', '2026-10-31')
    check('§T5-c10 事后表现(已到期点位对到期日事实;门内独立读): 标普 7000 vs '
          '7651.54=未中;7650=命中;十年美债 4.2 vs 5.29=未中;5.29=命中;'
          '失业率 4.0 vs 4.1=未中(容差 0.05)',
          ex['VIEW-20260905-001#f2']['fact_value'] == spx[1]
          and ex['VIEW-20260905-001#f2']['verdict'] == 'ex_post_missed'
          and ex['VIEW-20260905-001#f6']['verdict'] == 'ex_post_consistent'
          and ex['VIEW-20260905-001#f3']['fact_value'] == ust[1]
          and ex['VIEW-20260905-001#f3']['verdict'] == 'ex_post_missed'
          and ex['VIEW-20260905-001#f7']['verdict'] == 'ex_post_consistent'
          and ex['VIEW-20261120-003#f2']['fact_value'] == unr[1]
          and ex['VIEW-20261120-003#f2']['verdict'] == 'ex_post_missed'
          and rows['VIEW-20261120-003#f2']['comparison']['at_horizon']
          ['tolerance'] == 0.05
          and 'SPX@2026-09-30' in rows['VIEW-20260905-001#f2']['evidence_refs']
          and rows['VIEW-20260905-001#f3']['statement_kind'] != 'forecast',
          f"forecast={blk['ex_post']['forecast_claims']['n']} "
          f"realized={blk['ex_post']['realized_data_claims']['n']}")
    check('§T5-c11 事后表现声明=PARTIAL: 未到期 12 条(最早到期 2026-12-31)'
          '不判定,随行写明到期后按事实更新',
          blk['ex_post']['forecast_claims']['n'] == 3
          and blk['ex_post']['forecast_claims']['missed'] == 2
          and blk['ex_post']['realized_data_claims']['n'] == 2
          and blk['ex_post']['not_yet_testable']
          == {'n': 12, 'earliest_horizon_end': '2026-12-31'}
          and 'PARTIAL' in blk['ex_post']['note']
          and '未到期不做判定' in blk['ex_post']['note'])
    dfr = _t5_obs(sd, 'ECB_DFR', T5_ASOF)
    spx_c = _t5_obs(sd, 'SPX', T5_ASOF)
    spx_p = _t5_obs(sd, 'SPX', '2026-09-05')
    r = rows['VIEW-20260915-002#f8']
    check('§T5-c12 当前水平型对事实: 存款便利利率 2.50% 对序列读数 2.5'
          '(观测 2026-09-16,距截止日 67 天=陈旧读数→一致(陈旧));2.00%=与'
          '事实不符;「当前」标普 6900 对截止日读数(容差 0.5%)=一致;发布日'
          '已不符的 7718=已过时',
          r['facts']['at_cutoff']['value'] == dfr[1]
          and r['facts']['at_cutoff']['observation_date'] == '2026-09-16'
          and r['status'] == 'consistent_stale_fact'
          and rows['VIEW-20260915-002#f9']['status'] == 'fact_mismatch'
          and rows['VIEW-20261120-003#f4']['facts']['at_cutoff']['value']
          == spx_c[1] and rows['VIEW-20261120-003#f4']['status'] == 'consistent'
          and rows['VIEW-20260905-001#f5']['facts']['at_publish']['value']
          == spx_p[1]
          and rows['VIEW-20260905-001#f5']['status'] == 'no_longer_current',
          f"dfr={dfr} r8={r['status']} spx_c={spx_c} spx_p={spx_p}")
    r = rows['VIEW-20260915-002#f5']
    check('§T5-c13 不可对账行如实标注: 目标区间上下限序列缺席=不可核;期限'
          '「中期」=不可解析;无地区/未映射目标=未映射;库内 ai_inferred 行'
          '=库内推导;无同期限定价的日银路径=不可对照',
          r['status'] == 'unverifiable'
          and r['facts']['at_cutoff']['upper']['status'] == 'missing'
          and r['comparison']['lower_metric_id'] == 'DFEDTARL'
          and rows['VIEW-20260915-002#f4']['status'] == 'unparseable_horizon'
          and rows['VIEW-20260915-002#f10']['status'] == 'unmapped'
          and rows['VIEW-20260915-002#f10']['region'] == 'CN'
          and rows['VIEW-20260915-002#f15']['status'] == 'unmapped'
          and rows['VIEW-20260915-002#f15']['region'] is None
          and rows['VIEW-20260905-001#f4']['status'] == 'library_inferred'
          and rows['VIEW-20260915-002#f6']['status'] == 'not_comparable',
          f"f5={r['status']} f4={rows['VIEW-20260915-002#f4']['status']}")
    from collections import Counter as _Ctr
    codes = _Ctr(g['code'] for g in blk['gaps'])
    check('§T5-c14 缺口逐项点名(12 项,均带说明): 期限不可解析 1/目标区间'
          '序列缺席+陈旧 2/日银定价缺席 1/存款便利利率陈旧读数 1/未映射 2'
          '(按地区聚合,无地区行单列)/非数值点位 1/四地政策利率与两指标无'
          '同期限定价 5',
          codes == _Ctr({'horizon_unparseable': 1, 'series_absent:DFEDTARU': 1,
                         'fact_stale_at_cutoff:DFEDTARU': 1,
                         'pricing_absent:JP_POLICY_RATE': 1,
                         'fact_stale_at_cutoff:ECB_DFR': 1, 'target_unmapped': 2,
                         'pricing_absent:EA_REAL_GDP_YOY': 1,
                         'pricing_absent:SPX_EPS': 1, 'point_non_numeric': 1,
                         'pricing_absent:CN_LPR_1Y': 1,
                         'pricing_absent:ECB_DFR': 1})
          and all(g.get('severity') == 'disclosed' and g.get('note')
                  for g in blk['gaps'])
          and sorted(str(g['region']) for g in blk['gaps']
                     if g['code'] == 'target_unmapped') == ['CN', 'None'],
          dict(codes))
    dis = {d['metric_id']: d for d in blk['disagreements']}
    pool = {p['id']: p for p in blk['falsification_pool']}
    check('§T5-c15 机构间分歧(只列幅度不裁对错)+证伪条件池(库内原文 1/'
          '引擎规则 6;目标区间缺席=无事后核验规则)+假设池 1+风险池 1',
          set(dis) == {'FED_FUNDS', 'SPX'}
          and dis['FED_FUNDS']['n_rows'] == 9 and len(dis['FED_FUNDS']
                                                        ['institutions']) == 3
          and dis['FED_FUNDS']['numeric_spread_bp'] == 125.0
          and dis['SPX']['n_rows'] == 5
          and pool['VIEW-20260905-001/c1']['source'] == 'view_library'
          and sorted(p['id'] for p in pool.values()
                     if p['source'] == 'engine_rule')
          == sorted(['VIEW-20260905-001#f1/market', 'VIEW-20260915-002#f1/market',
                     'VIEW-20260915-002#f2/market', 'VIEW-20260915-002#f3/market',
                     'VIEW-20260915-002#f13/market',
                     'VIEW-20261120-003#f1/market'])
          and pool['VIEW-20260915-002#f2/market']['observable']
          == 'FEDFUNDS_FUT:ZQJ27.CBT'
          and pool['VIEW-20260915-002#f2/market']['thresholds_bp']
          == {'above': 87.5, 'below': 62.5}
          and len(blk['assumption_pool']) == 1
          and blk['assumption_pool'][0]['attribution'] == 'ai_inferred'
          and len(blk['risk_pool']) == 1,
          f"pool={sorted(pool)}")
    wt = blk['window_testability']
    check('§T5-c16 证伪窗口可检性: 窗内到期 7 行(可检验 4)/窗外 5 行(最早 '
          '2027-06-30)/引擎规则窗内 4 窗外 2/库内证伪条件 1(不带观察日)',
          len(wt['rows_in_window']) == 7
          and sum(1 for x in wt['rows_in_window'] if x['testable']) == 4
          and wt['n_rows_after_window'] == 5
          and wt['earliest_after_window'] == '2027-06-30'
          and len(wt['engine_rules_in_window']) == 4
          and len(wt['engine_rules_after_window']) == 2
          and wt['n_view_library_conditions'] == 1
          and all(x['horizon_end'] <= '2027-05-22'
                  for x in wt['rows_in_window']),
          f"{len(wt['rows_in_window'])}/{wt['n_rows_after_window']}")
    fi = blk['frozen_inputs']
    tm_sha = hashlib.sha256(open(os.path.join(
        ROOT, 'config', 'forecast_target_map.json'), 'rb').read()).hexdigest()
    check('§T5-c17 冻结输入: 只含可见的 3 份观点文档(sha256 前 16 位=门内'
          '独立算)+目标映射表;扣留/隔离世件不在内',
          fi == {'data/institutions/views/VIEW-20260905-001.json': man[
              'data/institutions/views/VIEW-20260905-001.json'][:16],
              'data/institutions/views/VIEW-20260915-002.json': man[
                  'data/institutions/views/VIEW-20260915-002.json'][:16],
              'data/institutions/views/VIEW-20261120-003.json': man[
                  'data/institutions/views/VIEW-20261120-003.json'][:16],
              'config/forecast_target_map.json': tm_sha[:16]},
          fi)
    check('§T5-c18 版本绑定与用到的指标: 截止日/源快照/定价源=运行快照/'
          '观点库在场;对照用到的 9 个在册指标随行;缺席指标点名',
          blk['version_binding'] == {
              'as_of': T5_ASOF, 'source_snapshot_id': 'research_snapshot_20261122_v2',
              'source_target_date': T5_ASOF, 'historical_view': False,
              'value_version': None, 'pricing_source': 'run_snapshot',
              'pricing_source_snapshot_id': 'research_snapshot_20261122_v2',
              'views_dir': 'data/institutions/views', 'views_status': 'present',
              'target_map': 'config/forecast_target_map.json'}
          and blk['metrics_used'] == ['FED_FUNDS', 'DFF', 'SPX', 'UST_10Y',
                                      'JP_POLICY_RATE', 'ECB_DFR',
                                      'EA_REAL_GDP_YOY', 'SPX_EPS',
                                      'UNEMPLOYMENT']
          and blk['metrics_absent'] == ['DFEDTARU', 'DFEDTARL'],
          f"{blk['metrics_used']} {blk['metrics_absent']}")
    b1 = _t5_block(t, snap, regions=['US'])
    b2 = _t5_block(t, snap, regions=['US', 'EA'])
    b3 = _t5_block(t, snap, regions=['JP'])
    check('§T5-c19 地区范围: 只对账问句范围内地区(范围外行逐行列出不计);'
          '无地区行仅在≥2 地时纳入;单地无可对账行=草稿级阻断',
          b1['summary']['n_rows'] == 19 and b1['summary']['n_out_of_scope'] == 7
          and 'VIEW-20260915-002#f15' in _t5_ids(b1['out_of_scope_rows'])
          and b2['summary']['n_rows'] == 23
          and b2['summary']['n_out_of_scope'] == 3
          and b2['summary']['unmapped_n'] == 1
          and b3['summary']['n_rows'] == 2
          and b3['summary']['blocked_class'] == xg.NO_COMPARABLES
          and all(r['region'] in ['US', 'EA'] or r['region'] is None
                  for r in b2['rows']),
          f"{b1['summary']['n_rows']}/{b2['summary']['n_rows']}/"
          f"{b3['summary']['n_rows']} {b3['summary']['blocked_class']}")
    import datetime as _dt_mod
    sd2 = copy.deepcopy(sd)
    for mid, val in (('DFEDTARU', 4.0), ('DFEDTARL', 3.75)):
        d0 = _dt_mod.date(2026, 7, 1)
        sd2['series_store'][mid] = {
            'dates': [(d0 + _dt_mod.timedelta(days=i)).isoformat()
                      for i in range(142)],
            'values': [val] * 142}
    b4 = _t5_block(t, snap, snap=sd2)
    r4 = {r['row_id']: r for r in b4['rows']}['VIEW-20260915-002#f5']
    pol = [p for p in b4['falsification_pool'] if '/policy' in p['id']]
    check('§T5-c20 目标区间上下限序列在场时(门内内存快照补入): 区间行转为'
          '一致(上下限逐项对事实);定价面出现目标区间中点基线;每个路径/次数'
          '行多一条事后核验规则(观测=上限序列@到期月末);相关缺口消失',
          r4['status'] == 'consistent'
          and r4['comparison']['at_publish']['upper']['fact_value'] == 4.0
          and b4['pricing']['midpoint']['value'] == 3.875
          and len(pol) == 7
          and pol[0]['observable'].startswith('DFEDTARU@')
          and 'pass_min_pct' in pol[0]
          and not [g for g in b4['gaps'] if 'DFEDTARU' in g['code']]
          and b4['summary']['gaps'] == 10
          and b4['summary']['candidate_n'] == 3
          and b4['metrics_absent'] == [],
          f"{r4['status']} pol={len(pol)} gaps={b4['summary']['gaps']}")
    b5 = _t5_block(t, snap, as_of='2026-10-01')
    check('§T5-c21 历史研究时点(2026-10-01): 其后才发布的观点整篇扣留(2);'
          '今日定价曲线不借用(缺席+记因);到期事实只取当时可得读数',
          b5['summary']['n_views_visible'] == 2
          and sorted(w['view_id'] for w in b5['withheld_after_cutoff'])
          == ['VIEW-20261120-003', 'VIEW-20261201-004']
          and b5['pricing']['status'] == 'absent'
          and _t5_gap_codes(b5['gaps'])[0] == 'pricing_absent_at_cutoff'
          and b5['version_binding']['as_of'] == '2026-10-01'
          and b5['summary']['candidate_n'] == 0
          and b5['summary']['blocked_class'] is None,
          f"{b5['summary']} {[g['code'] for g in b5['gaps']][:3]}")
    bn = xg.plan_block({'expectations_gap': None})
    bv = xg.build_block({'question_verbatim': Q_T5, 'regions': ['US'],
                         'region_source': 'question_named',
                         'expectations_gap': {'asked': True}}, sd,
                        os.path.join(t, 'noviews'), T5_ASOF, question=Q_T5,
                        reg_by_id=wd.load_registry(t)['by_id'])
    check('§T5-c22 分级: 对照块缺席=硬缺口;观点库不在场=草稿;无可对账行='
          '草稿;草稿横幅逐类点名',
          bn is None and xg.blocked_class(bn) == xg.BLOCK_MISSING
          and xg.plan_blocked_class({}) is None
          and xg.plan_blocked_class({'expectations_gap': {'asked': True}})
          == xg.BLOCK_MISSING
          and bv['views']['status'] == 'absent'
          and xg.blocked_class(bv) == xg.VIEWS_ABSENT
          and xg.plan_blocked_class({'expectations_gap': bv})
          == xg.VIEWS_ABSENT
          and xg.blocked_class(b3) == xg.NO_COMPARABLES
          and xg.blocked_class(blk) is None
          and '预期差对照块缺席' in xg.draft_banner(xg.BLOCK_MISSING)
          and '机构观点库不在场' in xg.draft_banner(xg.VIEWS_ABSENT)
          and '预期差对照无可对账行' in xg.draft_banner(xg.NO_COMPARABLES)
          and '只交草稿' in xg.draft_banner(xg.VIEWS_ABSENT)
          and '正式归档对草稿拒绝' in xg.draft_banner(xg.NO_COMPARABLES),
          f"{bv['views']} ")
    fro = xg.merge_frozen_inputs({}, blk, t,
                                 snapshot_rel='data/daily/x.json',
                                 snapshot_sha='abcd1234567890ab')
    err = ''
    try:
        xg.merge_frozen_inputs({}, dict(blk, frozen_inputs=dict(
            fi, **{'data/institutions/views/VIEW-20260905-001.json': '0' * 16})), t)
    except RuntimeError as e:
        err = str(e)
    fro_none = xg.merge_frozen_inputs(
        {'a/b.json': 'keep'}, dict(blk, frozen_inputs={'a/b.json': None}), t)
    er = xg.evidence_rows(blk)
    kinds = _Ctr((e['kind'], e['role']) for e in er)
    text1 = '\n'.join(xg.render_gap_sections(blk, {}))
    text2 = '\n'.join(xg.render_gap_sections(copy.deepcopy(blk), {}))
    check('§T5-c23 冻结输入并入(摘要与文件不符=报错不静默;空值跳过;快照随'
          '并入)/证据索引行(文档 3+预测 26+定价 9+序列读数点 12,角色='
          'expectations_gap)/对照块渲染确定性且含虚构机构名与状态',
          fro.get('data/institutions/views/VIEW-20260905-001.json')
          == fi['data/institutions/views/VIEW-20260905-001.json']
          and fro.get('data/daily/x.json') == 'abcd1234567890ab'
          and err.startswith('expectations_gap_frozen_input_changed')
          and fro_none == {'a/b.json': 'keep'} and len(er) == 50
          and kinds == _Ctr({('institution_forecast', 'expectations_gap'): 26,
                             ('market_pricing', 'expectations_gap'): 9,
                             ('plan_series_point', 'expectations_gap'): 12,
                             ('institution_view', 'expectations_gap'): 3})
          and len({e['ref'] for e in er}) == 50
          and text1 == text2
          and all(s in text1 for s in (
              '## 预期差对照(机构观点 × 同期限市场定价 × 事实)',
              '南山宏观(虚构机构)', '### 市场定价面(同期限)',
              '### 逐行对照', '### 机构间分歧', '### 事后表现',
              '### 证伪窗口(问句「未来半年」: 研究截止日 2026-11-22 → '
              '窗末 2027-05-22)', '### 缺口(逐项点名;缺证=缺证,不以推断补)'))
          and bool(xg.gate_note([], blk, sd)),
          f"err={err[:60]} kinds={dict(kinds)} len={len(text1)}")


def sec_t5_d():
    print('§T5-d 席位预期差回声契约(函数级;合格回声+反例矩阵)')
    import judgment_contract as jc
    xg = _xg()
    t, snap = _t5_tree('t5d')
    blk = _t5_block(t, snap)
    plan = {'expectations_gap': blk, 'metrics': list(blk['metrics_used']),
            'context_metrics': []}
    rep = {'evidence_index': xg.evidence_rows(blk)}

    def run(jud, pl=plan, b=blk):
        return jc._expectations_gap_checks(
            jud, None, {'evidence_index': xg.evidence_rows(b)}, pl)

    def st(items, suffix):
        hit = [x for x in items if x['item'].endswith(suffix)]
        return (hit[-1]['status'], hit[-1]['note']) if hit else (None, '')

    def mut(fn):
        j = {'reader_map': {'expectations_gap': _t5_echo(blk)}}
        fn(j['reader_map']['expectations_gap'], j)
        return j

    c0 = mut(lambda e, j: None)
    it_all = run(c0)
    bad_v = [x for x in it_all if x['status'] != 'VERIFIED']
    it_b = run({'reader_map': {'expectations_gap': _t5_echo(blk, rr_supported=True)}})
    check('§T5-d1 合格回声(门夹具;非真实研判)全项 VERIFIED: 回声计数/候选'
          '清单/缺口清单/窗口/逐行判定(候选 3 行 supported,须推导行 '
          'not_a_gap 或 supported 两种写法)/关键未知/自由文字数字均对应',
          not bad_v and len(it_all) >= 40
          and all(x['status'] == 'VERIFIED' for x in it_b)
          and st(it_all, '.supported_gaps')[0] == 'VERIFIED',
          f"{[(x['item'][-46:], x['note'][:60]) for x in bad_v][:4]}")
    view_of = lambda rid: _row(blk['rows'], row_id=rid)['view_id']     # noqa: E731
    core = lambda vid: next(                                     # noqa: E731
        s['text'] for s in blk['view_statements']
        if s['view_id'] == vid and s['kind'] == 'core_view')
    pc = next(p for p in blk['falsification_pool'] if p['source'] == 'view_library')
    pm = next(p for p in blk['falsification_pool']
              if p['id'] == 'VIEW-20260915-002#f2/market')['condition']
    NEG = [
        ('回声缺席', lambda e, j: j['reader_map'].pop('expectations_gap'),
         'reader_map.expectations_gap', 'NOT_VERIFIED', '缺席'),
        ('as_of 相左', lambda e, j: e.update(as_of='2026-11-21'),
         '.as_of', 'CONTRADICTED', '≠'),
        ('行数相左', lambda e, j: e.update(n_rows=25), '.n_rows',
         'CONTRADICTED', '≠'),
        ('回声缺字段', lambda e, j: e.pop('n_views_visible'),
         '.n_views_visible', 'NOT_VERIFIED', '回声缺字段'),
        ('候选漏一行', lambda e, j: e.update(
            engine_candidates_echoed=e['engine_candidates_echoed'][:-1]),
         '.engine_candidates_echoed', 'NOT_VERIFIED', '缺'),
        ('候选多出虚构行', lambda e, j: e.update(
            engine_candidates_echoed=e['engine_candidates_echoed']
            + ['VIEW-20990101-001#f1']),
         '.engine_candidates_echoed', 'CONTRADICTED', '多出'),
        ('缺口回声不全', lambda e, j: e.update(gaps_echoed=e['gaps_echoed'][:-1]),
         '.gaps_echoed', 'NOT_VERIFIED', '缺'),
        ('窗口未回声', lambda e, j: e.pop('window_echo'),
         '.window_echo', 'NOT_VERIFIED', '须回声窗口'),
        ('总述为空', lambda e, j: e.update(seat_summary=''),
         '.seat_summary', 'NOT_VERIFIED', '缺席'),
        ('总述数字无对应', lambda e, j: e.update(seat_summary='门夹具总述: 幅度 9876.5bp。'),
         '.seat_summary', 'NOT_VERIFIED', '不对应'),
        ('判定行号虚构', lambda e, j: e['supported_gaps'][0].update(
            row_id='VIEW-20260915-002#f99'),
         '.supported_gaps[0].row_id', 'CONTRADICTED', '虚构行'),
        ('判定重复', lambda e, j: e['supported_gaps'].append(
            copy.deepcopy(e['supported_gaps'][0])),
         '.supported_gaps[4].row_id', 'NOT_VERIFIED', '重复'),
        ('须推导行漏判', lambda e, j: e['supported_gaps'].pop(),
         '.supported_gaps', 'NOT_VERIFIED', '未逐行判定'),
        ('verdict 非法', lambda e, j: e['supported_gaps'][0].update(verdict='maybe'),
         '.supported_gaps[0].verdict', 'NOT_VERIFIED', "须为 'supported'"),
        ('一致行判成立', lambda e, j: e['supported_gaps'].__setitem__(
            0, dict(e['supported_gaps'][0], row_id='VIEW-20260915-002#f1')),
         '.supported_gaps[0].verdict', 'CONTRADICTED', '相左'),
        ('不可对照行判成立', lambda e, j: e['supported_gaps'].__setitem__(
            0, dict(e['supported_gaps'][0], row_id='VIEW-20260905-001#f1')),
         '.supported_gaps[0].verdict', 'NOT_VERIFIED', '无事实/同期限'),
        ('成立而无证伪条件', lambda e, j: e['supported_gaps'][0].update(
            falsification_conditions=[]),
         '.supported_gaps[0].falsification_conditions', 'NOT_VERIFIED', '≥1 条'),
        ('竞争解释无假设标注', lambda e, j: e['supported_gaps'][0].update(
            competing_explanation='门夹具竞争解释: 机构点位代表少数观点。'),
         '.supported_gaps[0].competing_explanation', 'NOT_VERIFIED', '假设'),
        ('假托机构原话', lambda e, j: e['supported_gaps'][0].update(
            reading_attribution='institution_stated',
            reading='门夹具: 这句不是该观点文档里的原话。'),
         '.supported_gaps[0].reading', 'CONTRADICTED', '假托机构原话'),
        ('机构原话逐字引用', lambda e, j: e['supported_gaps'][0].update(
            reading_attribution='institution_stated',
            reading=core(view_of(e['supported_gaps'][0]['row_id']))),
         '.supported_gaps[0].reading', 'VERIFIED', '机构原话'),
        ('须推导行标机构原话', lambda e, j: e['supported_gaps'][3].update(
            reading_attribution='institution_stated',
            reading=core(view_of(e['supported_gaps'][3]['row_id']))),
         '.supported_gaps[3].reading', 'NOT_VERIFIED', '席位推导'),
        ('条件无数字', lambda e, j: e['supported_gaps'][0].update(
            falsification_conditions=[{
                'condition': '若 FED_FUNDS 在 2027-04-30 之前较截止日累计上行不足半步',
                'attribution': 'ai_inferred'}]),
         '.supported_gaps[0].falsification_conditions[0]', 'NOT_VERIFIED', '数字阈值'),
        ('条件无日期', lambda e, j: e['supported_gaps'][0].update(
            falsification_conditions=[{
                'condition': '若 FED_FUNDS 较截止日累计上行不足 12.5bp',
                'attribution': 'ai_inferred'}]),
         '.supported_gaps[0].falsification_conditions[0]', 'NOT_VERIFIED', '日期'),
        ('条件无可观测量', lambda e, j: e['supported_gaps'][0].update(
            falsification_conditions=[{
                'condition': '若 政策利率 在 2027-04-30 之前累计上行不足 12.5bp',
                'attribution': 'ai_inferred'}]),
         '.supported_gaps[0].falsification_conditions[0]', 'NOT_VERIFIED', '可观测量'),
        ('机构条件须引池条目', lambda e, j: e['supported_gaps'][0].update(
            falsification_conditions=[{'condition': pc['condition'],
                                       'attribution': 'institution_stated'}]),
         '.supported_gaps[0].falsification_conditions[0].source_ref',
         'NOT_VERIFIED', 'source_ref'),
        ('机构条件非逐字', lambda e, j: e['supported_gaps'][0].update(
            falsification_conditions=[{
                'condition': '门夹具: 这不是机构原文的证伪条件文本。',
                'attribution': 'institution_stated', 'source_ref': pc['id']}]),
         '.supported_gaps[0].falsification_conditions[0].condition',
         'CONTRADICTED', '逐字引自'),
        ('机构条件逐字引池条目', lambda e, j: e['supported_gaps'][0].update(
            falsification_conditions=[{'condition': pc['condition'],
                                       'attribution': 'institution_stated',
                                       'source_ref': pc['id']}]),
         '.supported_gaps[0].falsification_conditions[0]', 'VERIFIED', '逐字引用'),
        ('引擎规则逐字引用', lambda e, j: e['supported_gaps'][0].update(
            falsification_conditions=[{'condition': pm, 'attribution': 'engine_rule',
                                       'source_ref': 'VIEW-20260915-002#f2/market'}]),
         '.supported_gaps[0].falsification_conditions[0]', 'VERIFIED', '逐字引用'),
        ('引擎规则池条目标成机构', lambda e, j: e['supported_gaps'][0].update(
            falsification_conditions=[{'condition': pm, 'attribution': 'institution_stated',
                                       'source_ref': 'VIEW-20260915-002#f2/market'}]),
         '.supported_gaps[0].falsification_conditions[0].source_ref',
         'NOT_VERIFIED', 'source_ref'),
        ('引用不可解析', lambda e, j: e['supported_gaps'][0].update(
            evidence_refs=['NO_SUCH_REF']),
         '.supported_gaps[0].evidence_refs', 'NOT_VERIFIED', '不可解析'),
        ('引用未落在该行', lambda e, j: e['supported_gaps'][0].update(
            evidence_refs=['VIEW-20260905-001#f2']),
         '.supported_gaps[0].evidence_refs', 'NOT_VERIFIED', '未落在'),
        ('关键未知为空', lambda e, j: e.update(key_unknowns=[]),
         '.key_unknowns', 'NOT_VERIFIED', '为空'),
        ('注记数字无对应', lambda e, j: e.update(comments=['注记: 9876.5']),
         '.comments[0]', 'NOT_VERIFIED', '不对应'),
    ]
    nbad = []
    for name, fn, suffix, want, note in NEG:
        j = mut(fn)
        s, n = st(run(j), suffix)
        if s != want or note not in n:
            nbad.append((name, s, n[:80]))
    check('§T5-d2 反例矩阵(%d 项): 与引擎确定性面相左/虚构行号/假托机构原话/'
          '非逐字引用=CONTRADICTED;缺席/不全/漏判/条件缺数字·日期·观测量/'
          '引用不可解析/数字无对应=NOT_VERIFIED;逐字引用(机构原文/引擎规则)='
          'VERIFIED' % len(NEG), not nbad, nbad)
    e2 = _t5_echo(blk, seat_summary='门夹具总述: 候选阈值 12.5bp。')
    j2 = {'reader_map': {'expectations_gap': e2}}
    qn = xg.parse_falsification_window('市场定价和机构观点之间有哪些预期差？',
                                       T5_ASOF)
    b_nw = _t5_block(t, snap, q='市场定价和机构观点之间有哪些预期差？')
    pl_nw = {'expectations_gap': b_nw, 'metrics': list(b_nw['metrics_used']),
             'context_metrics': []}
    j_nw = {'reader_map': {'expectations_gap': _t5_echo(b_nw, window_echo={
        'months': 6, 'start': T5_ASOF, 'end': '2027-05-22'})}}
    it_nw = run(j_nw, pl_nw, b_nw)
    it_bl = run({'reader_map': {'expectations_gap': _t5_echo(blk)}},
                {'expectations_gap': None}, blk)
    it_rm = run({'reader_map': []})
    check('§T5-d3 边界: 引擎面数字(12.5bp)在自由文字里=对应;问句未指定窗口'
          '而席位回声窗口=虚构(CONTRADICTED);对照块缺席/reader_map 非对象='
          'NOT_VERIFIED',
          qn is None and b_nw.get('falsification_window') is None
          and st(run(j2), '.seat_summary')[0] == 'VERIFIED'
          and st(it_nw, '.window_echo')[0] == 'CONTRADICTED'
          and '虚构' in st(it_nw, '.window_echo')[1]
          and it_bl[0]['item'] == 'research_plan.expectations_gap'
          and it_bl[0]['status'] == 'NOT_VERIFIED'
          and it_rm[0]['item'] == 'reader_map'
          and it_rm[0]['status'] == 'NOT_VERIFIED',
          f"{st(it_nw, '.window_echo')} {it_bl[0]['item']} {it_rm[0]['item']}")


def sec_t5_e():
    print('§T5-e 引擎集成(离线 plan: 单型计划/取数分级/研究年月/冻结输入/证据索引)')
    xg = _xg()
    import inspect
    import research_orchestrator as ro
    t, snap = _t5_tree('t5e')
    rep = _plan_on(t, Q_T5)
    rp = rep.get('research_plan') or {}
    blk = xg.plan_block(rp) or {}
    ad = rp.get('as_of_declared') or {}
    check('§T5-e1 研究计划=单型(kind=map)+对照块: 问句逐字/截止日=快照覆盖日/'
          '四地/证伪窗口/汇总同 §T5-c1;不生成原问直答块',
          rp.get('question_kind') == 'map' and rp.get('question_verbatim') == Q_T5
          and rp.get('cutoff') == T5_ASOF == blk.get('as_of')
          and 'policy_question' not in rp and blk.get('asked') is True
          and blk.get('summary') == T5_SUMMARY
          and blk.get('falsification_window', {}).get('end') == '2027-05-22'
          and blk.get('region_source') == 'plan_regions'
          and blk.get('metrics_used') == T5_METRICS_USED,
          f"{rp.get('question_kind')} {blk.get('summary', {}).get('n_rows')}")
    check('§T5-e2 研究时点与范围分别解析: 问句研究年月 2026-11 按月末请求'
          '(2026-11-30)→钳制到快照实际覆盖日 2026-11-22 并随行说明;该年月='
          '研究时点标记(scoped_to_question_month),非序列观测窗',
          ad.get('requested_as_of') == '2026-11-30'
          and ad.get('clamped_to_coverage') is True
          and ad.get('as_of') == ad.get('coverage_date') == T5_ASOF
          and ad.get('scoped_to_question_month') is True
          and ad.get('question_month') == '2026-11'
          and '实际覆盖日' in (ad.get('note') or ''),
          f"{ad.get('requested_as_of')} {ad.get('as_of')}")
    pa = rp.get('point_anchors') or []
    xo = rp.get('ex_post_offsets') or []
    check('§T5-e3 问句无历史时点词形→默认三时点锚(12 个月前/3 个月前/最新一期)'
          '与事后偏移(3/6/12 月),来源标注 expectations_gap;无显式维度词形→'
          '全维族(来源标注)',
          [a['label'] for a in pa]
          == ['12个月前', '3个月前', '最新一期']
          and [a['months_before'] for a in pa] == [12, 3, 0]
          and [a['as_of'] for a in pa]
          == ['2025-11-22', '2026-08-22', T5_ASOF]
          and all(a.get('default_three_point') == 'expectations_gap'
                  for a in pa[:2])
          and [o['months'] for o in xo] == [3, 6, 12]
          and all(o.get('default_three_point') == 'expectations_gap' for o in xo)
          and rp.get('dimension_source', '').startswith('implicit_macro_environment(')
          and sorted(rp.get('regions') or {}) == ['CN', 'EA', 'JP', 'US'],
          f"{[a['label'] for a in pa]} {[o['months'] for o in xo]}")
    items = ((rep.get('run') or {}).get('data_requirements') or {}).get('items') or []
    by = {i['metric_id']: i for i in items}
    eg_only = sorted(set(blk.get('metrics_used') or []) - set(rp.get('metrics') or []))
    m_q = ro._mask_research_month(Q_T5, '2026-11')
    check('§T5-e4 取数分级: 预期差对照面用到而计划未选的指标并入取数'
          '(planned,来源=对照面指标;陈旧由对照面逐行披露);计划指标来源不变;',
          eg_only == ['FED_FUNDS', 'SPX', 'SPX_EPS', 'UST_10Y']
          and all(by.get(m, {}).get('tier') == 'planned'
                  and (by[m].get('basis') or '').startswith('预期差对照面指标')
                  for m in eg_only)
          and by['SPX_EPS'].get('outcome') == 'stale_for_task'
          and all((by[m].get('basis') or '').startswith('地图研究计划')
                  for m in rp.get('metrics') or [])
          and m_q == Q_T5.replace('2026年11月', '□' * 8)
          and ro._mask_research_month(Q_T5, '2026-10') is None
          and ro._mask_research_month('2026年11月到2027年3月有哪些预期差？', '2026-11')
          is None,
          f"eg_only={eg_only} spx_eps={by.get('SPX_EPS', {}).get('outcome')}")
    reg = wd.load_registry(t)
    l1 = ((rep.get('layers') or {}).get('L1_事实层') or {}).get('rows') or []
    mets = list(rp.get('metrics') or []) + eg_only
    sd = _jq(snap)
    old = ro._evaluate_data_requirements(
        mets, rep.get('steps') or [], sd, l1, question=Q_T5,
        registry=reg['by_id'], map_plan=rp, lexical_metrics=None)
    new = ro._evaluate_data_requirements(
        mets, rep.get('steps') or [], sd, l1, question=Q_T5,
        registry=reg['by_id'], map_plan=rp, lexical_metrics=set())
    check('§T5-e5 旧调用面零变化: 不传词面命中集(lexical_metrics=None)时'
          '对照面指标不按新来源分级;传入时按新来源分级(入参可选)',
          inspect.signature(ro._evaluate_data_requirements).parameters[
              'lexical_metrics'].default is None
          and not [(i['metric_id'], i.get('basis')) for i in old
                   if (i.get('basis') or '').startswith('预期差对照面指标')]
          and all(i.get('tier') == 'planned'
                  and (i.get('basis') or '').startswith('预期差对照面指标')
                  for i in new if i['metric_id'] in eg_only),
          f"old={[(i['metric_id'], i.get('tier')) for i in old if i['metric_id'] in eg_only]}")
    fi = (rep.get('run') or {}).get('frozen_inputs') or {}
    sha_ok = all(
        hashlib.sha256(open(os.path.join(t, rel), 'rb').read()).hexdigest()[:16]
        == v for rel, v in fi.items() if os.path.isfile(os.path.join(t, rel)))
    idx = [e for e in rep.get('evidence_index') or []
           if e.get('role') == 'expectations_gap']
    from collections import Counter as _Ctr2
    rep3 = _plan_on(t, Q_PLAIN)
    rp3 = rep3.get('research_plan') or {}
    check('§T5-e6 冻结输入(含 3 份可见观点文档+目标映射表+快照+日历+注册表;'
          '摘要=门内独立算)与证据索引(对照面 42 行: 预测 26/定价 9/序列点 4/'
          '文档 3)随计划落位;扣留件不在内',
          set(fi) == set(T5_FROZEN) and sha_ok
          and _Ctr2(e.get('kind') for e in idx)
          == _Ctr2({'institution_forecast': 26, 'market_pricing': 9,
                    'plan_series_point': 4, 'institution_view': 3})
          and len({e.get('ref') for e in idx}) == 42,
          f"{sorted(fi)} {dict(_Ctr2(e.get('kind') for e in idx))}")
    check('§T5-e7 非预期差问句零变化: 普通地图问句无对照块/无对照面证据行/'
          '观点文档不入冻结输入/锚点无该来源标注/维度来源照旧',
          'expectations_gap' not in rp3
          and not [e for e in rep3.get('evidence_index') or []
                   if e.get('role') == 'expectations_gap']
          and not [k for k in (rep3.get('run') or {}).get('frozen_inputs') or {}
                   if 'institutions/views' in k]
          and not any(a.get('default_three_point') for a in
                      rp3.get('point_anchors') or [])
          and rp3.get('dimension_source') == 'explicit_words'
          and rp3.get('question_kind') == 'map')
    rep2 = _plan_on(t, Q_T5_NOSHAPE)
    rp2 = rep2.get('research_plan') or {}
    b2 = xg.plan_block(rp2) or {}
    check('§T5-e8 无地图词形的预期差问句同样成单型计划: 问句未点名→四地'
          '(地区取自研究计划)/全维族(来源标注预期差问句)/研究年月未声明则'
          '不标范围',
          rp2.get('question_kind') == 'map'
          and rp2.get('dimension_source', '').startswith('implicit_expectations_gap(')
          and b2.get('region_source') == 'plan_regions'
          and sorted(b2.get('regions') or []) == ['CN', 'EA', 'JP', 'US']
          and sorted(rp2.get('regions') or []) == ['CN', 'EA', 'JP', 'US']
          and (rp2.get('as_of_declared') or {}).get('scoped_to_question_month')
          is not True
          and b2.get('falsification_window', {}).get('months') == 6,
          f"{rp2.get('dimension_source', '')[:30]} {b2.get('region_source')}")


def sec_t5_f():
    print('§T5-f 正式 CLI 链(真实步骤;合成观点库夹具)')
    if os.environ.get('IA_R33_GATE_SKIP_CLI') == '1':
        print('  ⏭ 跳过(IA_R33_GATE_SKIP_CLI=1)')
        return
    xg = _xg()
    import ia_cli as ic
    qf = os.path.join(TMPG, 'q_t5.txt')
    with open(qf, 'w', encoding='utf-8') as fh:
        fh.write(Q_T5 + '\n')
    t, _ = _t5_tree('t5f', views='clean', code=True)
    rc, d = _cli(['research-one', '--stage', 'plan', '--question-file', qf,
                  '--engine-root', t], cwd=t)
    dd = d.get('data') or {}
    rd = dd.get('report_dir') or ''
    rj = _jq(os.path.join(rd, 'report.json')) if os.path.isfile(
        os.path.join(rd, 'report.json')) else {}
    env = _jq(os.path.join(rd, 'AGENT_SEAT_ENVELOPE.json')) if os.path.isfile(
        os.path.join(rd, 'AGENT_SEAT_ENVELOPE.json')) else {}
    rp = rj.get('research_plan') or {}
    blk = rp.get('expectations_gap') or {}
    steps = rj.get('steps') or []
    failed = [s['step'] for s in steps if s.get('ok') is False]
    skipped = {s['step']: (s.get('skipped_reason') or '') for s in steps
               if not s.get('executed')}
    check('§T5-f1 正式 CLI plan(真实步骤): rc=0/ok/run_ok/plan_status=ok/'
          'plan_gaps=[];研究计划=单型带对照块(26 行/候选 3/窗口至 2027-05-22);'
          '问句逐字;步骤无失败(对照面补充指标 DFEDTARU 快照缺席→其历史步'
          '如实跳过并写明原因,仅此一步未执行)',
          rc == 0 and d.get('ok') is True and dd.get('run_ok') is True
          and dd.get('plan_status') == 'ok' and dd.get('plan_gaps') == []
          and rd.startswith(t) and steps and not failed
          and set(skipped) == {'S4_history_DFEDTARU'}
          and '历史序列缺席' in skipped['S4_history_DFEDTARU']
          and rp.get('question_kind') == 'map'
          and rp.get('question_verbatim') == Q_T5
          and 'policy_question' not in rp
          and (blk.get('summary') or {}).get('n_rows') == 26
          and (blk.get('summary') or {}).get('candidate_n') == 3
          and (blk.get('falsification_window') or {}).get('end') == '2027-05-22',
          f"rc={rc} ok={d.get('ok')} steps={len(steps)} failed={failed} "
          f"skip={sorted(skipped)} "
          f"{str(dd.get('plan_gaps'))[:160]}")
    if not rd:
        return
    egc = env.get('expectations_gap') or {}
    ef = egc.get('engine_faces') or {}
    disc = egc.get('discipline') or []
    fi_run = (rj.get('run') or {}).get('frozen_inputs') or {}
    check('§T5-f2 席位工单(AGENT_SEAT_ENVELOPE): expectations_gap=spec/engine_'
          'faces/discipline;面=块在场/截止日/四地/窗口/可见 3 扣留 1/26 行/'
          '可对账 15/候选行号/须推导行/缺口 12/美国定价在场/未到期 12;纪律 '
          '含算得的「未到期(最早到期 2026-12-31)」;冻结输入含 3 份可见文档',
          env.get('question', '').strip() == Q_T5
          and set(egc) == {'spec', 'engine_faces', 'discipline'}
          and ef.get('block_present') is True and ef.get('as_of') == T5_ASOF
          and ef.get('regions') == ['US', 'CN', 'EA', 'JP']
          and ef.get('falsification_window') == {
              'months': 6, 'start': T5_ASOF, 'end': '2027-05-22', 'source': '未来半年'}
          and ef.get('n_views_visible') == 3 and ef.get('n_views_withheld') == 1
          and ef.get('n_rows') == 26 and ef.get('comparable_n') == 15
          and ef.get('engine_candidate_rows') == T5_CANDS
          and ef.get('reading_required_rows') == [T5_READING]
          and len(ef.get('gaps') or []) == 12
          and (ef.get('pricing') or {}).get('status') == 'present'
          and ef.get('ex_post') == {'n': 12, 'earliest_horizon_end': '2026-12-31'}
          and isinstance(disc, list) and len(disc) == 9
          and any(x.startswith('AC3 到期预测保持 PARTIAL: 未到期(最早到期 '
                               '2026-12-31)') for x in disc)
          and 'reader_map.expectations_gap' in json.dumps(env.get('produce'), ensure_ascii=False)
          and set(fi_run) == set(T5_FROZEN)
          and 'VIEW-20261201-004' not in json.dumps(env.get('frozen_inputs')),
          f"keys={sorted(egc)} disc={len(disc)} "
          f"{[x[:44] for x in disc if x.startswith('AC3')]}")
    c0 = ic._r1_gap_contract(rp, None)
    b2 = copy.deepcopy(blk)
    b2['ex_post']['not_yet_testable']['earliest_horizon_end'] = '2027-03-31'
    c2 = ic._r1_gap_contract(rp, b2)
    b3 = copy.deepcopy(blk)
    b3['ex_post']['not_yet_testable'] = {}
    c3 = ic._r1_gap_contract(rp, b3)
    check('§T5-f3 工单契约函数: 对照块缺席(无快照)不再崩溃——面=块不在场/'
          '窗口可检性 None;「最早到期」取自引擎面(改期随之;无则不写)',
          isinstance(c0, dict) and set(c0) == {'spec', 'engine_faces', 'discipline'}
          and c0['engine_faces'].get('block_present') is False
          and c0['engine_faces'].get('window_testability') is None
          and any('未到期(最早到期 2027-03-31)' in x for x in c2['discipline'])
          and not any('2026-12-31' in x for x in c2['discipline'])
          and not any('最早到期' in x for x in c3['discipline'])
          and any(x.startswith('AC3 到期预测保持 PARTIAL: 未到期的预测')
                  for x in c3['discipline']))
    def attach(name, jud):
        jp = os.path.join(TMPG, name)
        with open(jp, 'w', encoding='utf-8') as fh:
            json.dump(jud, fh, ensure_ascii=False)
        r, dd_ = _cli(['research-one', '--stage', 'attach', '--question-file',
                       qf, '--report-dir', rd, '--judgment', jp,
                       '--engine-root', t], cwd=t)
        rj_ = _jq(os.path.join(rd, 'report.json'))
        cv = ((rj_.get('agent_judgment') or {}).get('contract_verification') or {})
        sts = {x['item']: (x['status'], x['note']) for x in cv.get('map_checks') or []}
        return (r, dd_, cv.get('verdict'), sts,
                os.path.exists(os.path.join(rd, 'agent_judgment.json')),
                [v.get('code') for v in (dd_.get('data') or {}).get('violations') or []])
    r1, d1, v1, s1, f1, codes1 = attach('t5f_j1.json', _t5_skel())
    rj1 = _jq(os.path.join(rd, 'report.json'))
    check('§T5-f4 正式 CLI attach 拒收「缺预期差判断」(schema/归因/L3≥1/'
          'L4≥2 结构项齐备的骨架;情景五面内容缺席照旧报缺): rc=0/ok=False/'
          'attached=False/validation_passed=False;结构违规(schema/归因/'
          '情景复数)为零;契约项 reader_map.expectations_gap=NOT_VERIFIED '
          '点名缺席;report.json 的 agent_judgment.attached=False;判定档不落位',
          r1 == 0 and d1.get('ok') is False
          and (d1.get('data') or {}).get('attached') is False
          and (d1.get('data') or {}).get('validation_passed') is False
          and not (set(codes1) & {'SCHEMA', 'ATTR', 'SCN-PLURAL'})
          and s1.get('reader_map.expectations_gap', ('', ''))[0] == 'NOT_VERIFIED'
          and '缺席' in s1.get('reader_map.expectations_gap', ('', ''))[1]
          and (rj1.get('agent_judgment') or {}).get('attached') is False
          and not f1,
          f"rc={r1} cv={v1} codes={codes1[:6]} "
          f"{str(s1.get('reader_map.expectations_gap'))[:120]}")
    eb = _t5_echo(blk)
    eb['supported_gaps'][0]['row_id'] = 'VIEW-20260915-002#f99'
    r2, d2, v2, s2, f2, _c2 = attach('t5f_j2.json', _t5_skel(eb))
    check('§T5-f5 正式 CLI attach 拒收「虚构判定行」: 回声字段逐项 VERIFIED 而'
          '该行号=CONTRADICTED(虚构行);整档=CONTRADICTED;判定档不落位',
          r2 == 0 and d2.get('ok') is False
          and (d2.get('data') or {}).get('attached') is False
          and v2 == 'CONTRADICTED' and not f2
          and s2.get('reader_map.expectations_gap.supported_gaps[0].row_id',
                     ('', ''))[0] == 'CONTRADICTED'
          and s2.get('reader_map.expectations_gap.engine_candidates_echoed',
                     ('', ''))[0] == 'VERIFIED'
          and s2.get('reader_map.expectations_gap.n_rows', ('', ''))[0]
          == 'VERIFIED',
          f"cv={v2} {str(s2.get('reader_map.expectations_gap.supported_gaps[0].row_id'))[:120]}")
    r3, d3 = _cli(['research-one', '--stage', 'report', '--question-file', qf,
                   '--report-dir', rd, '--engine-root', t], cwd=t)
    dr = d3.get('data') or {}
    check('§T5-f6 正式 CLI report(席位判断未落位): rc=1/ok=False/generated='
          'true/L3、L4 未产出/deliverable=false,阻断类=地图必需面缺席'
          '(先于预期差草稿类)',
          r3 == 1 and d3.get('ok') is False and dr.get('generated') is True
          and dr.get('L3_produced') is False and dr.get('L4_produced') is False
          and dr.get('deliverable') is False
          and dr.get('blocked_class') == 'map_required_face_missing',
          f"rc={r3} bc={dr.get('blocked_class')}")
    mdp = os.path.join(rd, 'MAP_REPORT.md')
    md = open(mdp, encoding='utf-8').read() if os.path.isfile(mdp) else ''
    sha_ok = False
    sp = os.path.join(rd, 'MAP_REPORT.sha256')
    if os.path.isfile(sp):
        with open(sp, encoding='utf-8') as fh:
            sha_ok = hashlib.sha256(md.encode('utf-8')).hexdigest() in fh.read()
    check('§T5-f7 读者报告(report 段): 四地三时点/政策四分面/传导/转折/'
          '历史类比+预期差对照七小节(虚构机构名与逐行状态)+事后表现 '
          'PARTIAL+缺口;席位段写明未裁;语义审查段在;sha256 随附一致',
          all(s in md for s in (
              '## 四地三时点环境对照', '## 政策口径四分面', '## 证据最充分的传导机制',
              '## 过去一年的三个转折', '## 历史上结构最像的时期',
              '## 预期差对照(机构观点 × 同期限市场定价 × 事实)',
              '### 市场定价面(同期限)', '### 逐行对照',
              '### 机构间分歧', '### 事后表现(到期点位对事实;未到期不判定)',
              '### 证伪窗口(问句「未来半年」: 研究截止日 2026-11-22 → '
              '窗末 2027-05-22)', '### 缺口(逐项点名;缺证=缺证,不以推断补)',
              '## Agent 席判断(预期差;席位原文,数值与引擎面对账后方可落位)',
              '南山宏观(虚构机构)', '事后未兑现', 'PARTIAL',
              '席位未提交预期差判断——引擎候选 3 条、须席位推导 1 行悬而未裁',
              '### 证伪条件、关键假设与风险(机构原文优先;库内推导与引擎规则分列)',
              '## 语义审查'))
          and sha_ok, f"len={len(md)} sha={sha_ok}")
    arc = os.path.join(TMPG, 't5f_arc')
    r4, d4 = _cli(['research-one', '--stage', 'archive', '--question-file', qf,
                   '--report-dir', rd, '--archive-dir', arc,
                   '--engine-root', t], cwd=t)
    check('§T5-f8 正式归档拒绝(不可交付): rc≠0/ok=False/blocked=not_'
          'deliverable;隔离归档目录无新件',
          r4 != 0 and d4.get('ok') is False
          and (d4.get('data') or {}).get('blocked') == 'not_deliverable'
          and (not os.path.exists(arc) or not os.listdir(arc)),
          f"rc={r4} {json.dumps(d4.get('data') or d4.get('error'), ensure_ascii=False)[:200]}")
    t7, _ = _t5_tree('t5f_nov', views=None, code=True)
    r7, d7 = _cli(['research-one', '--stage', 'plan', '--question-file', qf,
                   '--engine-root', t7], cwd=t7)
    dd7 = d7.get('data') or {}
    rd7 = dd7.get('report_dir') or ''
    rj7 = _jq(os.path.join(rd7, 'report.json')) if os.path.isfile(
        os.path.join(rd7, 'report.json')) else {}
    b7 = xg.plan_block(rj7.get('research_plan') or {}) or {}
    r7a, d7a = _cli(['research-one', '--stage', 'report', '--question-file',
                     qf, '--report-dir', rd7, '--engine-root', t7], cwd=t7)
    md7 = ''
    p7 = os.path.join(rd7, 'MAP_REPORT.md')
    if os.path.isfile(p7):
        md7 = open(p7, encoding='utf-8').read()
    r7b, d7b = _cli(['research-one', '--stage', 'archive', '--question-file',
                     qf, '--report-dir', rd7, '--archive-dir',
                     os.path.join(TMPG, 't5f_arc7'), '--engine-root', t7], cwd=t7)
    check('§T5-f9 干净安装无观点库: plan rc=0 但回执草稿级缺口 '
          'expectations_gap_views_absent(点名机构观点库不在场与转正办法);'
          '对照块 views=absent(0 行);report 段照出读者报告(首部草稿横幅);'
          '正式归档拒绝且不建目录',
          r7 == 0 and d7.get('ok') is True
          and [(g.get('code'), g.get('severity')) for g in dd7.get('plan_gaps') or []]
          == [('expectations_gap_views_absent', 'draft')]
          and dd7.get('plan_status') == 'ok'
          and b7.get('views', {}).get('status') == 'absent'
          and xg.blocked_class(b7) == xg.VIEWS_ABSENT
          and r7a == 1 and d7a.get('ok') is False
          and (d7a.get('data') or {}).get('generated') is True
          and '机构观点库不在场' in md7[:2000] and '只交草稿' in md7[:2000]
          and '## 预期差对照(机构观点 × 同期限市场定价 × 事实)' in md7
          and r7b != 0 and d7b.get('ok') is False
          and (d7b.get('data') or {}).get('blocked') == 'not_deliverable'
          and not os.path.exists(os.path.join(TMPG, 't5f_arc7')),
          f"rc={r7} {str(dd7.get('plan_gaps'))[:200]} md={len(md7)}")
    t8, _ = _t5_tree('t5f_nosnap', views='clean', code=True)
    snap8 = os.path.join(t8, 'data', 'daily', SNAP_LATER)
    if os.path.exists(snap8):
        os.rename(snap8, snap8 + '.off')
    e8 = dict(os.environ)
    pr8 = subprocess.run(
        [sys.executable, 'ia_cli.py', 'research-one', '--stage', 'plan',
         '--question-file', qf, '--engine-root', t8], cwd=t8,
        capture_output=True, text=True, timeout=900, env=e8)
    try:
        d8 = json.loads(pr8.stdout)
    except ValueError:
        d8 = {'raw': ((pr8.stdout or '') + (pr8.stderr or ''))[-400:]}
    dd8 = d8.get('data') or {}
    check('§T5-f10 无运行快照的安装树: plan rc=1/ok=False/plan_status=gap;缺口='
          '零事实+预期差对照块缺席(均硬缺口);无未处理异常(基线此处为 '
          'AttributeError 崩溃)',
          pr8.returncode == 1 and d8.get('ok') is False
          and dd8.get('plan_status') == 'gap'
          and [(g.get('code'), g.get('severity')) for g in dd8.get('plan_gaps') or []]
          == [('zero_facts', 'hard'), ('expectations_gap_block_missing', 'hard')]
          and 'Traceback' not in (pr8.stderr or '')
          and 'raw' not in d8,
          f"rc={pr8.returncode} {str(dd8.get('plan_gaps'))[:200]} "
          f"err={(pr8.stderr or '')[-200:]}")
    t9, _ = _t5_tree('t5f_q', views='all', code=True)
    r9, d9 = _cli(['research-one', '--stage', 'plan', '--question-file', qf,
                   '--engine-root', t9], cwd=t9)
    dd9 = d9.get('data') or {}
    rd9 = dd9.get('report_dir') or ''
    rj9 = _jq(os.path.join(rd9, 'report.json')) if os.path.isfile(
        os.path.join(rd9, 'report.json')) else {}
    b9 = xg.plan_block(rj9.get('research_plan') or {}) or {}
    lint = [s for s in rj9.get('steps') or [] if s.get('step') == 'S9_views_lint']
    v9 = b9.get('views') or {}
    check('§T5-f11 观点库含违规件: 既有 views lint 步响亮失败(exit 1→'
          'ok=False/run_ok=False,plan_status 仍 ok、缺口空);对照块照建'
          '(5 份/合规 4/隔离 1 点名文件;26 行、扣留 1 不变)——隔离件不入'
          '对照,库卫生须先修(未因预期差接线而吞错)',
          r9 == 0 and d9.get('ok') is False and dd9.get('run_ok') is False
          and dd9.get('plan_status') == 'ok' and dd9.get('plan_gaps') == []
          and [s['step'] for s in rj9.get('steps') or [] if s.get('ok') is False]
          == ['S9_views_lint']
          and len(lint) == 1 and lint[0].get('ok') is False
          and lint[0].get('exit_code') == 1
          and v9.get('status') == 'present' and v9.get('n_files') == 5
          and v9.get('n_compliant') == 4 and v9.get('n_quarantined') == 1
          and [q.get('view_id') for q in v9.get('quarantined') or []]
          == ['VIEW-20261010-005']
          and (b9.get('summary') or {}).get('n_rows') == 26
          and (b9.get('summary') or {}).get('n_views_withheld') == 1,
          f"rc={r9} ok={d9.get('ok')} run_ok={dd9.get('run_ok')} "
          f"{[(s.get('step'), s.get('exit_code')) for s in rj9.get('steps') or [] if s.get('ok') is False]}")


def _t5_next(ym):
    y, m = int(ym[:4]), int(ym[5:])
    return '%04d-%02d' % (y + (m == 12), 1 if m == 12 else m + 1)


def _t5_shift(ym, n):
    y, m = int(ym[:4]), int(ym[5:])
    t = y * 12 + (m - 1) + n
    return '%04d-%02d' % (t // 12, t % 12 + 1)


def _t5_months(f, t_):
    out, ym = [], f
    while ym <= t_:
        out.append(ym)
        ym = _t5_next(ym)
    return out


def _t5_steps_with_series(sd, reg, mids, steps=()):
    """门内搭 S4 步骤面: 序列取自冻结快照、单位取注册表(与真实 S4 信封同形),
    替换同名替身步(离线计划的替身信封不带序列)。"""
    out = [s for s in steps or []
           if not (str(s.get('step') or '').startswith('S4_history_')
                   and str(s.get('step'))[11:] in mids)]
    for mid in mids:
        s = (sd.get('series_store') or {}).get(mid) or {}
        out.append({'step': 'S4_history_' + mid, 'ok': True, 'envelope': {
            'ok': True, 'data': {'series': {
                'metric_id': mid, 'dates': list(s.get('dates') or []),
                'values': list(s.get('values') or []),
                'unit': (reg.get(mid) or {}).get('unit')}}}})
    return out


def _t5_syn_step(mid, dates, values, unit):
    return {'step': 'S4_history_' + mid, 'ok': True, 'envelope': {
        'ok': True, 'data': {'series': {
            'metric_id': mid, 'dates': list(dates), 'values': list(values),
            'unit': unit}}}}


def _t5_seat_helpers():
    """席位工具纯函数面: 只取常量 D / PRICING_TICK_BP / PRICING_STEP_BP /
    _COMP_NAME / _HYP / _HZ_TXT
    与白名单函数定义(源码 ast 抽取后执行),不执行模块级守卫/取数——席位工具只
    服务其预设的真实工单,门内不跑整份。"""
    import ast
    src = open(os.path.join(ROOT, 'scripts', 'seat_tools',
                            'make_expectations_gap_judgment.py'),
               encoding='utf-8').read()
    want = {'fmt', 'f2', '_cn_int', 'cn_num', 'cn_amt', 'ym_shift',
            'step_band', 'seg_start_ym', 'comp_txt', 'win_agree_txt',
            '_af_val', '_seg_dir_ok', '_hyp_count', '_hyp_txt', 'horizon_row',
            'month_last', 'pricing_path_rising'}
    body = [n for n in ast.parse(src).body if (
        isinstance(n, ast.FunctionDef) and n.name in want) or (
        isinstance(n, ast.Assign)
        and any(isinstance(tg, ast.Name)
                and tg.id in ('D', 'PRICING_TICK_BP', 'PRICING_STEP_BP',
                              '_COMP_NAME', '_HYP', '_HZ_TXT')
                for tg in n.targets))]
    import bisect
    ns = {'bisect': bisect}
    exec(compile(ast.Module(body=body, type_ignores=[]), 'seat_helpers',
                 'exec'), ns)
    return ns


def sec_t5_g():
    print('§T5-g 任务5修订: 同期限定价参照/对质观测窗/结构化对质'
          '(软契约;旧档与无该字段工单零变化)')
    xg = _xg()
    import research_map_planner as rmp
    import judgment_contract as jc
    t, snap = _t5_tree('t5g')
    sd = _jq(snap)
    reg = wd.load_registry(t)['by_id']
    rep = _plan_on(t, Q_T5)
    rp = rep.get('research_plan') or {}
    blk = rp.get('expectations_gap') or {}
    pr = blk['pricing']
    prow = pr['rows']
    curve, _sk = _t5_curve(sd)
    dff = _t5_obs(sd, 'DFF', T5_ASOF)
    chg = {ym: round((r - dff[1]) * 100.0, 2) for ym, r in curve.items()}

    def exp_month(hz):
        h = str(hz or '')
        if re.fullmatch(r'\d{8}', h):
            h = '%s-%s-%s' % (h[:4], h[4:6], h[6:])
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', h):
            return None
        c = [ym for ym in sorted(curve) if ym + '-01' <= h]
        return c[-1] if c else None
    pbad = []
    for hz in ('2026-10-31', '2026-11-01', '2026-11-30', '2026-12-01',
               '2026-12-15', '2027-01-31', '2027-03-31', '2027-05-15',
               '2027-08-01', '2027-08-31', '2027-09-01', '2027-12-31',
               '20270331', '2026-11', '中期', '', None):
        g_ = xg._pricing_reference(pr, hz)
        e_ = exp_month(hz)
        if e_ is None:
            if g_ is not None:
                pbad.append((hz, g_))
        elif not (g_ and g_.get('month') == e_
                  and g_.get('change_bp') == chg[e_]
                  and g_.get('basis')
                  == 'last_contract_month_on_or_before_horizon'
                  and g_.get('evidence_ref')
                  == 'FEDFUNDS_FUT:' + str(g_.get('ticker'))):
            pbad.append((hz, e_, g_ and g_.get('month')))
    p_abs = dict(pr, status='absent')
    p_gap = dict(pr, rows=[dict(r, change_bp=None) if r['month'] == '2027-03'
                    else r for r in prow])
    check('§T5-g1 同期限定价参照(引擎确定性;门内独立读曲线): 文字/多值型点位的'
          '到期日当月或之前最后一个有读数的合约月;曲线起点之前/期限不可解析/'
          '定价缺席=None;无读数的合约月跳过',
          not pbad and xg._pricing_reference(p_abs, '2027-03-31') is None
          and xg._pricing_reference(pr, None) is None
          and (xg._pricing_reference(p_gap, '2027-03-31') or {}).get('month')
          == '2027-02'
          and (xg._pricing_reference(p_gap, '2027-03-31') or {}).get(
              'change_bp') == chg['2027-02'],
          pbad)
    rows = blk['rows']
    r3 = _row(rows, row_id=T5_READING)
    pref3 = xg._pricing_reference(pr, r3.get('horizon_end'))
    idx = {e.get('ref'): e for e in xg.evidence_rows(blk)}
    doc = _jq(os.path.join(VIEWS_FIX, 'VIEW-20261120-003.json'))
    fb = xg.Facts(sd, t, T5_ASOF, reg)
    tm = xg.load_target_map(t)

    def brow(f, n):
        gp_ = []
        return xg._build_row(doc, f, n, fb, pr, T5_ASOF, reg, tm, gp_, 0.0)
    b_far = brow({'value_or_direction': '2029年3.0%、2030年2.8%',
                  'target': 'fed_policy_path_baseline', 'horizon': '2030-12',
                  'attribution': 'institution_stated'}, 90)
    b_mid = brow({'value_or_direction': '2027年3.0%、2028年2.8%',
                  'target': 'fed_policy_path_baseline', 'horizon': '2027-05',
                  'attribution': 'institution_stated'}, 91)
    b_non = brow({'value_or_direction': '2027年1.5%、2028年1.4%',
                  'target': '欧元区GDP增长', 'horizon': '2028-12',
                  'attribution': 'institution_stated'}, 92)
    check('§T5-g2 参照随行落位(对照块;合成夹具行): 须推导的文字型行(路径指标,'
          '到期 2027-03-31)带 pricing_reference=2027-03 合约(变动=门内独立算)'
          '且其定价引用并入该行证据并进证据索引(market_pricing);其余 25 行'
          '为 None;多值型行同规则(曲线尽头之后=最后一个合约月;非路径指标='
          'None)',
          r3.get('status') == 'reading_required'
          and r3.get('metric_id') == 'FED_FUNDS'
          and r3.get('horizon_end') == '2027-03-31'
          and r3.get('pricing_reference') == pref3
          and pref3.get('month') == '2027-03'
          and pref3.get('change_bp') == chg['2027-03']
          and r3.get('evidence_refs', [None])[-1] == 'FEDFUNDS_FUT:ZQH27.CBT'
          and (idx.get('FEDFUNDS_FUT:ZQH27.CBT') or {}).get('kind')
          == 'market_pricing'
          and sum(1 for r in rows
                  if r.get('pricing_reference') is not None) == 1
          and b_far.get('status') == 'reading_required'
          and (b_far.get('pricing_reference') or {}).get('month') == '2027-08'
          and b_mid.get('status') == 'reading_required'
          and (b_mid.get('pricing_reference') or {}).get('month') == '2027-05'
          and b_non.get('status') == 'reading_required'
          and b_non.get('metric_id') == 'EA_REAL_GDP_YOY'
          and b_non.get('pricing_reference') is None,
          f"r3={r3.get('status')} {pref3 and pref3.get('month')} "
          f"far={(b_far.get('pricing_reference') or {}).get('month')} "
          f"mid={(b_mid.get('pricing_reference') or {}).get('month')} "
          f"non={b_non.get('status')}/{b_non.get('metric_id')}")
    # ── 对质观测窗: 同窗首尾读数(月末口径;门内独立读) ──
    mids = ('DFF', 'SPX', 'CPI', 'UNEMPLOYMENT', 'UST_10Y')
    rj = copy.deepcopy(rep)
    rj['steps'] = _t5_steps_with_series(sd, reg, mids, rep.get('steps') or [])
    cut = rp.get('cutoff')

    def mlast(mid, ym):
        d, v = _t5_obs(sd, mid, ym + '-31')
        return (d, v) if d and d[:7] == ym else (None, None)

    def yoy_pt(mid, ym):
        d, v = mlast(mid, ym)
        base = mlast(mid, _t5_shift(ym, -12))[1]
        return (d, round((float(v) / float(base) - 1.0) * 100.0, 4))

    def exp_win(mid, f, t_, yoy=False, pts=None, pct_level=None):
        """门内独立拼同窗读数文字: 各月最新有效读数(门内按月末日独立取)。"""
        pts = pts or [(yoy_pt if yoy else mlast)(mid, ym)
                      for ym in _t5_months(f, t_)]
        v0, v1 = pts[0][1], pts[-1][1]
        path = ('%.2f→…→%.2f(%d 期)' % (v0, v1, len(pts)) if len(pts) > 8
                else '%.2f@%s→%s%.2f@%s' % (
                    v0, pts[0][0], ''.join('%.2f→' % v for _d, v in pts[1:-1]),
                    v1, pts[-1][0]))
        u = pct_level if pct_level is not None else (
            (reg.get(mid) or {}).get('unit') == 'percent')
        if yoy:
            c_ = '首尾 %+.2fpp' % (round(v1 - v0, 2) + 0.0)
        elif u:
            c_ = '首尾 %+gbp' % round((v1 - v0) * 100)
        else:
            c_ = '首尾 %+.2f%%' % (round((v1 / v0 - 1.0) * 100, 2) + 0.0)
        return '同窗观测(%s→%s,%s口径): %s,%s%s' % (
            f, t_, '同比月末' if yoy else '月末', path, c_,
            ';终点月未满,取截止日前最新观测' if cut and t_ == cut[:7]
            else '')
    exp_dff = exp_win('DFF', '2026-08', '2026-10')
    exp_cpi = exp_win('CPI', '2026-02', '2026-10')
    exp_yoy = exp_win('CPI', '2026-05', '2026-09', yoy=True)
    exp_spx = exp_win('SPX', '2026-09', '2026-11')
    a, c = mlast('DFF', '2026-08'), mlast('DFF', '2026-10')
    ypts = [yoy_pt('CPI', ym) for ym in _t5_months('2026-05', '2026-09')]
    got = {
        'dff': rmp._window_obs_text(rj, 'DFF',
                                    {'from': '2026-08', 'to': '2026-10'}, cut),
        'cpi': rmp._window_obs_text(rj, 'CPI',
                                    {'from': '2026-02', 'to': '2026-10'}, cut),
        'yoy': rmp._window_obs_text(rj, 'CPI', {'from': '2026-05',
                                                'to': '2026-09', 'yoy': True},
                                    cut),
        'spx': rmp._window_obs_text(rj, 'SPX',
                                    {'from': '2026-09', 'to': '2026-11'}, cut),
        'dd': rmp._window_obs_text(rj, 'DFF', {'from': '2026-08-01',
                                               'to': '2026-10-31'}, cut)}
    # 合成序列(非真实数据): 月末 null/零基期/起月缺观测/非数值
    rj2 = copy.deepcopy(rj)
    rj2['steps'] += [
        _t5_syn_step('SYN_NULL', ['2026-08-03', '2026-08-28', '2026-08-31',
                                  '2026-09-01', '2026-10-01'],
                     [1.0, 3.0, None, 5.0, 7.0], 'index_point_2010'),
        _t5_syn_step('SYN_ZERO', ['2026-08-03', '2026-09-01', '2026-10-01'],
                     [0.0, 1.0, 2.0], 'index_point_2010'),
        _t5_syn_step('SYN_GAP', ['2026-08-03', '2026-10-01', '2026-11-02'],
                     [1.0, 2.0, 3.0], 'index_point_2010'),
        _t5_syn_step('SYN_NAN', ['2026-08-03', '2026-09-01', '2026-10-01'],
                     [1.0, float('nan'), 'nan'], 'index_point_2010')]
    syn_txt = {
        'null': rmp._window_obs_text(rj2, 'SYN_NULL',
                                     {'from': '2026-08', 'to': '2026-10'}, cut),
        'zero': rmp._window_obs_text(rj2, 'SYN_ZERO',
                                     {'from': '2026-08', 'to': '2026-10'}, cut),
        'gap': rmp._window_obs_text(rj2, 'SYN_GAP',
                                    {'from': '2026-09', 'to': '2026-11'}, cut),
        'nan': rmp._window_obs_text(rj2, 'SYN_NAN',
                                    {'from': '2026-08', 'to': '2026-10'}, cut)}
    w_none = [rmp._window_obs_text(rj, m, w, cut) for m, w in (
        ('DFF', {'from': '2026-10', 'to': '2026-08'}),      # 起点晚于终点
        ('DFF', {'from': '2026-8', 'to': '2026-10'}),       # 月形非法
        ('DFF', {'from': '2026-08'}),                       # 缺终点
        ('DFF', {'from': '2026-08', 'to': '2026-13'}),      # 非法月份
        ('DFF', {'from': '2026-08', 'to': '2026-10', 'yoy': True}),  # 非水平序列
        ('CPI', {'from': '2026-05', 'to': '2026-11'}),      # 终月无观测
        ('NOPE_X', {'from': '2026-08', 'to': '2026-10'}),   # 序列缺席
        ('DFF', {'from': '2026-08', 'to': '2026-08'}),      # 窗内仅一期
        ('DFF', '2026-08→2026-10'),                         # 非对象
        ('DFF', None))]
    why = {}
    for k_, (m_, w_) in {'shape': ('DFF', {'from': '2026-8', 'to': '2026-10'}),
                         'absent': ('NOPE_X', {'from': '2026-08',
                                               'to': '2026-10'}),
                         'short': ('CPI', {'from': '2026-05', 'to': '2026-11'}),
                         'yoylvl': ('DFF', {'from': '2026-08', 'to': '2026-10',
                                            'yoy': True}),
                         'gap': ('SYN_GAP', {'from': '2026-09', 'to': '2026-11'}),
                         'nan': ('SYN_NAN', {'from': '2026-08', 'to': '2026-10'}),
                         'zero': ('SYN_ZERO', {'from': '2026-08',
                                               'to': '2026-10'})}.items():
        rjx = rj2 if m_.startswith('SYN_') else rj
        why[k_] = rmp._window_obs(rjx, m_, w_, cut)[1]
    check('§T5-g3 对质观测窗同窗读数(_window_obs): 各月最新有效读数(月末口径;'
          '月末 null 不作读数)+首尾变化(百分比水平=bp/指数=相对%/同比空间=pp,'
          '与门内独立读逐字相同);YYYY-MM-DD 形同 YYYY-MM;多于八期只给首尾与期数;'
          '终点月=截止日所在月随行注明;窗形非法/序列缺席/不足两期/起止月无观测'
          '(窗不得静默缩短)/非水平序列声明同比/非数值或首期为零不可算=None 且'
          '给出具体原因(渲染如实回落,不编数)',
          got == {'dff': exp_dff, 'cpi': exp_cpi, 'yoy': exp_yoy,
                  'spx': exp_spx, 'dd': exp_dff}
          and syn_txt['null'] == exp_win(
              'SYN_NULL', '2026-08', '2026-10', pct_level=False,
              pts=[('2026-08-28', 3.0), ('2026-09-01', 5.0), ('2026-10-01', 7.0)])
          and syn_txt['gap'] is None and syn_txt['zero'] is None
          and syn_txt['nan'] is None
          and w_none == [None] * 10
          and why['shape'] == '观测窗起止须为 YYYY-MM 或 YYYY-MM-DD'
          and why['absent'] == '区分指标 NOPE_X 的序列不在证据面——观测窗无从复算'
          and why['short'] == ('观测窗 2026-05→2026-11 的起止月无有效月末观测'
                               '(可复算的仅 2026-05→2026-10)——须按实际可复算的'
                               '窗声明')
          and '不适用于 DFF' in why['yoylvl']
          and '起止月无有效月末观测(可复算的仅 2026-10→2026-11)' in why['gap']
          and '不足两期有效观测(得 1)' in why['nan']
          and '首期读数为零' in why['zero'],
          {'got': {k: (v[:60] if v else v) for k, v in got.items()},
           'syn': {k: (v[:50] if v else v) for k, v in syn_txt.items()},
           'none': w_none, 'why': why})
    dobs = rmp._distinguishing_obs(rj, cut, 'DFF')
    dobs_spx = rmp._distinguishing_obs(rj, cut, 'SPX')
    dobs_ust = rmp._distinguishing_obs(rj, cut, 'UST_10Y')
    cell_w = rmp._face_off_obs_cell(
        rj, cut, {'observation_window': {'from': '2026-08', 'to': '2026-10'}},
        'DFF', dobs)
    cell_nov = rmp._face_off_obs_cell(
        rj, cut, {'observation_window': {'from': '2026-10', 'to': '2026-11'}},
        'DFF', dobs)
    cell_bad = rmp._face_off_obs_cell(
        rj, cut, {'observation_window': {'from': 'x'}}, 'DFF', dobs)
    cell_bad0 = rmp._face_off_obs_cell(
        rj, cut, {'observation_window': {'from': '2026-08', 'to': '2026-10'}},
        'NOPE_X', None)
    leg_same = all(rmp._face_off_obs_cell(rj, cut, lk, dm, d) is d for lk, dm, d in (
        ({}, 'DFF', dobs), ({'face_off_check': {}}, 'SPX', dobs_spx),
        ({}, 'NOPE_X', None), ({'observation_window': 'x'}, 'DFF', dobs)))
    FB = '——如实回落;'
    # ── 渲染: 对质表/传导图(合成判定;非真实研判) ──
    base = {'observed_fact': '门夹具观察事实甲(合成)',
            'causal_hypothesis': '门夹具因果假设(合成)',
            'competing_explanation': '门夹具竞争解释(合成)',
            'distinguishing_metric': 'DFF',
            'main_predicts': '门夹具主解释预期(合成)',
            'competing_predicts': '门夹具竞争解释预期(合成)',
            'face_off_verdict': '尚不能区分'}
    lkA = dict(base, observation_window={'from': '2026-08', 'to': '2026-10'})
    lkB = dict(base, distinguishing_metric='SPX',
               observed_fact='门夹具观察事实乙(合成)')
    lkC = {k: v for k, v in base.items() if k in (
        'observed_fact', 'causal_hypothesis', 'distinguishing_metric')}
    lkC.update(observed_fact='门夹具观察事实丙(合成)',
               distinguishing_metric='NOPE_X')
    lkD = dict(base, distinguishing_metric='UST_10Y',
               observed_fact='门夹具观察事实丁(合成)')
    for _k in ('main_predicts', 'competing_predicts'):
        lkD.pop(_k)

    def jd(links_a, links_b=()):
        return {'reader_map': {
            'headline_conclusion': '门夹具总判断(合成;非真实研判)。',
            'regions': [{'region': r, 'from_to': '门夹具走位(合成)。'}
                        for r in ('US', 'CN', 'EA', 'JP')],
            'transmission': [{'chain_name': '门夹具传导链甲(合成)',
                              'links': list(links_a)},
                             {'chain_name': '门夹具传导链乙(合成)',
                              'links': list(links_b)}],
            'turnings': [], 'history_periods': []}}
    md = rmp.render_map_report(rj, jd([lkA, lkC], [lkB, lkD]), None, root=t)
    rowA = ('| DFF | 门夹具主解释预期(合成) | 门夹具竞争解释预期(合成) | %s | '
            '尚不能区分 |' % cell_w)
    rowB = ('| SPX | 门夹具主解释预期(合成) | 门夹具竞争解释预期(合成) | %s | '
            '尚不能区分 |' % dobs_spx)
    rowD = ('| UST_10Y | (预期未写明——如实缺席) | (预期未写明——如实缺席) | '
            '%s | 尚不能区分 |' % dobs_ust)
    md0 = rmp.render_map_report(rj, jd([lkB, lkD], [lkC]), None, root=t)
    md1 = rmp.render_map_report(rj, jd([dict(lkA, observation_window={
        'from': '2026-10', 'to': '2026-11'})], [lkB]), None, root=t)
    md2 = rmp.render_map_report(rj, jd([dict(lkA, observation_window={
        'from': 'x'})], [lkB]), None, root=t)
    tbl = md1.split('## 主解释 vs 竞争解释(对质表)')[1].split('\n## ')[0]
    check('§T5-g4 对质表/传导图渲染: 带观测窗的行=同窗读数在前、引擎当前面只在'
          '含窗后观测时以「窗后信息(不用于裁决)」附后(窗终月=引擎面所在月则'
          '不附);窗不可复算=给出具体原因后回落;注脚仅在有害观测窗的行时出现'
          '一次;窗为非对象=旧格式原样;无该字段的行=旧格式逐字不变(格=引擎'
          '当前面原对象;门内独立拼行)',
          cell_w == '(' + exp_dff + ';窗后信息(不用于裁决) ' + dobs[1:-1] + ')'
          and cell_nov == '(' + rmp._window_obs_text(
              rj, 'DFF', {'from': '2026-10', 'to': '2026-11'}, cut) + ')'
          and '窗后信息' not in cell_nov
          and cell_bad == ('(同窗观测: 观测窗起止须为 YYYY-MM 或 YYYY-MM-DD'
                           + FB + dobs + ')')
          and cell_bad0 == ('(同窗观测: 区分指标 NOPE_X 的序列不在证据面——'
                            '观测窗无从复算' + FB + '引擎面无观测)')
          and leg_same
          and all(x in md for x in (
              '## 主解释 vs 竞争解释(对质表)', rowA, rowB, rowD,
              '   - 能区分解释的指标: DFF (' + exp_dff + ') ' + dobs,
              '   - 能区分解释的指标: NOPE_X'
              '(引擎面无该序列观测——如实缺席)'))
          and md.count('> 对质观测窗: ') == 1
          and all(x in md0 for x in (rowB, rowD))
          and '同窗观测' not in md0 and '对质观测窗' not in md0
          and md1.count('> 对质观测窗: ') == 1
          and ('| %s | 尚不能区分 |' % cell_nov) in tbl
          and '窗后信息(不用于裁决)' not in tbl
          and ('| %s | 尚不能区分 |' % cell_bad) in md2
          and md2.count('> 对质观测窗: ') == 1,
          f"cell_w=…{cell_w[-75:]} nov_tail={cell_nov[-40:]} "
          f"rows={[x[:24] for x in (rowA, rowB, rowD) if x not in md]} "
          f"tbl_nov={('| %s | 尚不能区分 |' % cell_nov) in tbl}")
    # ── 契约(函数级;软契约: 字段在场才核) ──
    face = jc.build_face(rj)
    face2 = jc.build_face(rj2)

    def st(items, suffix):
        hit = [x for x in items if x['item'].endswith(suffix)]
        return (hit[-1]['status'], hit[-1]['note']) if hit else (None, '')

    def run(link, fc=None):
        j = {'reader_map': {'transmission': [{'links': [link]}]}}
        out = jc._map_checks(j, fc or face, rj)
        return [x for x in out if x['item'].endswith((
            '.observation_window', '.face_off_check', '.face_off_check.main',
            '.face_off_check.competing', '.face_off_verdict'))]
    W = {'from': '2026-08', 'to': '2026-10'}
    wchg = round((c[1] - a[1]) * 100.0, 6)            # 门内独立算: +25bp
    OPS = {'>=': lambda p, q: p >= q, '>': lambda p, q: p > q,
           '<=': lambda p, q: p <= q, '<': lambda p, q: p < q,
           '==': lambda p, q: abs(p - q) < 1e-9,
           '!=': lambda p, q: abs(p - q) >= 1e-9}

    def fck(m_op, m_v, c_op, c_v, unit='bp'):
        return {'main': {'op': m_op, 'value': m_v, 'unit': unit},
                'competing': {'op': c_op, 'value': c_v, 'unit': unit}}

    def exp_verdict(chg_, f_):
        m_ok = OPS[f_['main']['op']](round(chg_, 6), f_['main']['value'])
        c_ok = OPS[f_['competing']['op']](round(chg_, 6),
                                         f_['competing']['value'])
        return ('尚不能区分' if m_ok == c_ok else
                '支持主解释' if m_ok else '支持竞争解释')
    neg = [
        ('旧档形态(无观测窗/无结构化对质)=零新增项', dict(base), '.observation_window',
         None, ''),
        ('观测窗无竞争解释', {k: v for k, v in dict(base, observation_window=W).items()
                          if k != 'competing_explanation'},
         '.observation_window', 'NOT_VERIFIED', '须配竞争解释'),
        ('窗终月晚于研究截止月(合成窗后观测)', dict(
            base, distinguishing_metric='SYN_GAP',
            observation_window={'from': '2026-10', 'to': '2026-12'}),
         '.observation_window', 'NOT_VERIFIED', '晚于研究截止月 2026-11'),
        ('序列缺席', dict(base, distinguishing_metric='NOPE_X',
                        observation_window=W),
         '.observation_window', 'NOT_VERIFIED', '不在证据面'),
        ('窗内不足两期', dict(base, observation_window={'from': '2026-08',
                                                    'to': '2026-08'}),
         '.observation_window', 'NOT_VERIFIED', '不足两期'),
        ('非数值读数不计', dict(base, distinguishing_metric='SYN_NAN',
                              observation_window=W),
         '.observation_window', 'NOT_VERIFIED', '不足两期有效观测(得 1)'),
        ('窗形非法', dict(base, observation_window={'from': '2026-8',
                                                 'to': '2026-10'}),
         '.observation_window', 'NOT_VERIFIED', '须为 YYYY-MM'),
        ('起点晚于终点', dict(base, observation_window={'from': '2026-10',
                                                    'to': '2026-08'}),
         '.observation_window', 'NOT_VERIFIED', '起点晚于终点'),
        ('窗非对象', dict(base, observation_window='x'),
         '.observation_window', 'NOT_VERIFIED', '须为对象'),
        ('窗起止月无观测(月频;不得静默缩短)', dict(
            base, distinguishing_metric='CPI',
            observation_window={'from': '2026-05', 'to': '2026-11'}),
         '.observation_window', 'NOT_VERIFIED', '起止月无有效月末观测'),
        ('同比空间用于非水平序列', dict(base, observation_window={
            'from': '2026-08', 'to': '2026-10', 'yoy': True}),
         '.observation_window', 'NOT_VERIFIED', '不适用于 DFF'),
        ('结构化对质缺观测窗', dict(base, face_off_check=fck('>=', 12.5, '<', 12.5)),
         '.face_off_check', 'NOT_VERIFIED', '须带可复算的 observation_window'),
        ('结构化对质缺一侧', dict(base, observation_window=W,
                                face_off_check={'main': {'op': '>=', 'value': 12.5,
                                                         'unit': 'bp'}}),
         '.face_off_check', 'NOT_VERIFIED', '须含 main 与 competing'),
        ('算子非法', dict(base, observation_window=W,
                        face_off_check=fck('≈', 12.5, '<', 12.5)),
         '.face_off_check.main', 'NOT_VERIFIED', 'op:'),
        ('单位非法', dict(base, observation_window=W,
                        face_off_check=fck('>=', 12.5, '<', 12.5, 'xx')),
         '.face_off_check.main', 'NOT_VERIFIED', 'pct/bp/pp'),
        ('阈值非数值', dict(base, observation_window=W,
                          face_off_check=fck('>=', '12.5', '<', 12.5)),
         '.face_off_check.main', 'NOT_VERIFIED', '数值'),
        ('阈值为布尔', dict(base, observation_window=W,
                          face_off_check=fck('>=', True, '<', 12.5)),
         '.face_off_check.main', 'NOT_VERIFIED', '数值'),
    ]
    nbad = []
    for name, link, suffix, want, note in neg:
        fc_run = face2 if 'SYN_' in str(link.get('distinguishing_metric')) \
            else face
        s, n = st(run(link, fc_run), suffix)
        if s != want or note not in n:
            nbad.append((name, s, n[:60]))
    check('§T5-g5 契约反例(软契约;函数级): 旧档形态零新增项;观测窗无竞争解释/'
          '窗终月晚于截止月/序列缺席/不足两期/非数值不计/窗形非法/窗非对象/'
          '起止月无观测/非水平序列声明同比=NOT_VERIFIED;结构化对质缺观测窗/'
          '缺一侧/算子·单位·阈值非法=NOT_VERIFIED',
          not nbad, nbad)
    pos = [
        ('仅观测窗', dict(base, observation_window=W), 'VERIFIED',
         '窗 2026-08→2026-10 内 3 期月末观测(3.63→3.88)'),
        ('仅同比观测窗', dict(base, distinguishing_metric='CPI',
                            observation_window={'from': '2026-05', 'to': '2026-09',
                                                'yoy': True}), 'VERIFIED',
         '窗 2026-05→2026-09 内 5 期月末观测(%s→%s;同比空间)'
         % ('%g' % ypts[0][1], '%g' % ypts[-1][1])),
        ('窗终月=截止月(含)', dict(base, observation_window={'from': '2026-10',
                                                        'to': '2026-11'}),
         'VERIFIED', '窗 2026-10→2026-11 内 2 期月末观测(3.88→3.88)'),
        ('窗终月早于截止月', dict(base, observation_window={'from': '2026-07',
                                                       'to': '2026-09'}),
         'VERIFIED', '窗 2026-07→2026-09 内 3 期'),
        ('YYYY-MM-DD 形窗', dict(base, observation_window={
            'from': '2026-08-01', 'to': '2026-10-31'}), 'VERIFIED',
         '窗 2026-08→2026-10 内 3 期'),
        ('零基期观测窗本身可复算', dict(base, distinguishing_metric='SYN_ZERO',
                                  observation_window=W), 'VERIFIED',
         '窗 2026-08→2026-10 内 3 期月末观测(0→2)'),
        ('月末 null 不作读数(取当月最新有效)', dict(
            base, distinguishing_metric='SYN_NULL', observation_window=W),
         'VERIFIED', '窗 2026-08→2026-10 内 3 期月末观测(3→7)'),
    ]
    pbad2 = []
    for name, link, want, note in pos:
        fc_run = face2 if 'SYN_' in str(link.get('distinguishing_metric')) \
            else face
        s, n = st(run(link, fc_run), '.observation_window')
        if s != want or note not in n:
            pbad2.append((name, s, n[:70]))
    # 结构化对质: 两侧预期按冻结序列复算后与判断对账
    vcases = [
        ('主成立/竞争不成立→支持主解释', fck('>=', 12.5, '<', 12.5), wchg,
         '支持主解释', 'VERIFIED', ''),
        ('同上但判断写尚不能区分=相左', fck('>=', 12.5, '<', 12.5), wchg,
         '尚不能区分', 'CONTRADICTED', '对质判断与结构化复算不一致'),
        ('同上但判断写支持竞争解释=相左', fck('>=', 12.5, '<', 12.5), wchg,
         '支持竞争解释', 'CONTRADICTED', '对质判断与结构化复算不一致'),
        ('两侧均成立→尚不能区分', fck('>=', 0, '<=', 100), wchg,
         '尚不能区分', 'VERIFIED', ''),
        ('两侧均不成立→尚不能区分', fck('<', 0, '>', 100), wchg,
         '尚不能区分', 'VERIFIED', ''),
        ('主不成立/竞争成立→支持竞争解释', fck('<', 0, '>=', 0), wchg,
         '支持竞争解释', 'VERIFIED', ''),
        ('相对幅口径 pct', fck('>', round(wchg / 400.0, 4), '<',
                              round(wchg / 400.0, 4), 'pct'),
         round((c[1] / a[1] - 1.0) * 100.0, 6), '支持主解释', 'VERIFIED', ''),
        ('百分点口径 pp', fck('<=', 0, '>', 0, 'pp'), round(c[1] - a[1], 6),
         '支持竞争解释', 'VERIFIED', ''),
        ('同比空间 pp', fck('<=', 0, '>', 0, 'pp'),
         round(ypts[-1][1] - ypts[0][1], 6), '支持主解释', 'VERIFIED', ''),
        ('零基期: pp 口径可复算', fck('<=', 0, '>', 0, 'pp'), 2.0,
         '支持竞争解释', 'VERIFIED', 'SYN_ZERO'),
        ('零基期: pct 口径不可复算', fck('>', 0, '<', 0, 'pct'), None,
         '', 'NOT_VERIFIED', 'SYN_ZERO'),
        ('判断为空', fck('>=', 12.5, '<', 12.5), wchg, '', 'CONTRADICTED', ''),
    ]
    vbad = []
    for name, f_, chg_, verdict, want, note in vcases:
        link = dict(base, observation_window=W, face_off_check=f_,
                    face_off_verdict=verdict)
        fc_run = face
        if name == '同比空间 pp':
            link['distinguishing_metric'] = 'CPI'
            link['observation_window'] = {'from': '2026-05', 'to': '2026-09',
                                          'yoy': True}
        elif note == 'SYN_ZERO':
            link['distinguishing_metric'] = 'SYN_ZERO'
            fc_run = face2
        its = run(link, fc_run)
        if chg_ is None:
            s, n = st(its, '.face_off_check.main')
            if not (s == 'NOT_VERIFIED' and '不可复算' in n):
                vbad.append((name, s, n[:60]))
            continue
        ev = exp_verdict(chg_, f_)
        if '相左' in name or name == '判断为空':
            s, n = st(its, '.face_off_verdict')
            if not (s == 'CONTRADICTED' and '→应为 ' + ev in n):
                vbad.append((name, s, n[:70]))
            continue
        s2, n2 = st(its, '.face_off_check')
        if not (s2 == 'VERIFIED' and n2.endswith('→' + ev)
                and ('观测 %+.2f%s' % (chg_, f_['main']['unit'])) in n2):
            vbad.append((name, s2, n2[:80]))
    check('§T5-g6 契约正例: 观测窗 VERIFIED(窗与期数随行;同比空间/终月=截止月/'
          'YYYY-MM-DD 形/零基期/月末 null 均合法);结构化对质两侧预期按冻结序列'
          '复算(门内独立算 bp/pct/pp/同比空间),判断与复算一致=VERIFIED;应为'
          '另态而声明他态或留空=CONTRADICTED;零基期 pct 口径=NOT_VERIFIED',
          not pbad2 and not vbad, pbad2 + vbad)
    # ── 席位工具纯函数面(与引擎同规则) ──
    ns = _t5_seat_helpers()
    hz = ns['horizon_row']
    stp = ns['step_band']
    agree = all(
        (lambda g_, s_: (g_ is None and s_ is None) or (
            g_ is not None and s_ is not None
            and g_.get('month') == s_.get('month')))(
            xg._pricing_reference(pr, h),
            hz(h, prow, xg._pricing_reference(pr, h)))
        for h in ('2026-10-31', '2026-11-01', '2026-11-30', '2026-12-15',
                  '2027-03-31', '2027-05-15', '2027-08-31', '2027-09-01'))
    ns['store'] = face2['series_store']
    seat_mlast = [ns['month_last'](m, ym) for m, ym in (
        ('DFF', '2026-08'), ('DFF', '2026-10'), ('CPI', '2026-09'), ('SPX', '2026-11'))]
    check('§T5-g7 席位工具纯函数面(ast 抽取;不跑整份): 到期同期限参照与引擎'
          '_pricing_reference 同规则(逐到期日同月);无读数合约月跳过;隐含幅度'
          '就近折合到步长整数倍(半步归下一步);中文数字/口语两;年月平移;月末读数'
          '=窗内各月最新有效读数'
          '(与引擎同窗首尾逐值相同)',
          agree and hz('2027-03-31', prow)['month'] == '2027-03'
          and hz('2027-10-06', prow)['month'] == '2027-08'
          and hz('2026-10-31', prow) is None
          and hz('2027-03-31', prow, {'month': '2027-05'})['month'] == '2027-05'
          and hz('2027-03-31', prow, {'month': '2099-01'}) is None
          and hz('2027-03-31', p_gap['rows'])['month'] == '2027-02'
          and [(t_, n_) for t_, n_, _d in (stp(v, 25.0) for v in (
              0.0, 12.4, 12.5, 24.9, 25.0, 37.5, 50.0, 56.5, 58.0, 62.5, 69.0))]
          == [(0, 0), (0, 0), (25, 1), (25, 1), (25, 1), (50, 2), (50, 2),
              (50, 2), (50, 2), (75, 3), (75, 3)]
          and [ns['cn_num'](v) for v in (2, 6.0, 12.5, 25.0, 56.5, 69.0, 1.25)]
          == ['二', '六', '十二点五', '二十五', '五十六点五', '六十九', '一点二五']
          and ns['cn_amt'](2) == '两' and ns['cn_amt'](6.0) == '六'
          and ns['ym_shift']('2026-11', 6) == '2027-05'
          and ns['ym_shift']('2027-01', -1) == '2026-12'
          and ns['fmt'](4.0) == '4' and ns['fmt'](295.5184) == '295.5184'
          and seat_mlast == [mlast('DFF', '2026-08'), mlast('DFF', '2026-10'),
                             mlast('CPI', '2026-09'), mlast('SPX', '2026-11')]
          and ns['month_last']('SYN_NULL', '2026-08') == ('2026-08-28', 3.0),
          f"agree={agree} seat={seat_mlast}")


def sec_t5_h():
    print('§T5-h 席位工具定价曲线形态守卫(报价噪声容半个定价步长且不小于一个最小'
          '变动价位,按此前运行峰值计;只核判定档引用到的最后合约月之前;2026-11-25 '
          '盘中演习面误拒与同日日终真实面末月回落 1bp 误拒两处更正)')
    ns = _t5_seat_helpers()
    ppr = ns['pricing_path_rising']
    tick = ns['PRICING_TICK_BP']
    step = ns['PRICING_STEP_BP']
    band = max(tick, step / 2.0)
    M10 = ['2026-11', '2026-12', '2027-01', '2027-02', '2027-03', '2027-04',
           '2027-05', '2027-06', '2027-07', '2027-08']

    def curve(vals, months=M10, status='present'):
        return {'status': status, 'metric_id': 'FED_FUNDS', 'rows': [
            {'ticker': 'ZQ%d.CBT' % i, 'month': m, 'change_bp': v,
             'implied_avg_rate': round(3.88 + v / 100.0, 4)}
            for i, (m, v) in enumerate(zip(months, vals))]}
    # 2026-11-25 盘中程序演习面(标准 update --yes 后的真实期货报价;首月=当月未走完
    # 合约): 旧内联规则(逐行≥0 且末>首)判否→席位工具误拒
    rh = [-0.25, 18.0, 27.0, 41.0, 48.0, 56.0, 61.5, 65.5, 68.0, 67.5]
    c_rh = curve(rh)
    old_rule = all(x >= 0 for x in rh) and rh[-1] > rh[0]
    # 2026-11-25 日终真实面(同日第二次采集): 末月较此前峰值回落 1bp——r12 的
    # 「相邻月只容一个最小变动价位(0.5bp)」口径误拒→修订 r14 改按运行峰值计、
    # 噪声界=半个定价步长(12.5bp)且不小于一个最小变动价位
    s3 = [0.0, 17.0, 26.5, 39.5, 46.5, 54.0, 58.5, 62.5, 64.5, 63.5]
    got = {
        'rh_all': ppr(c_rh), 'rh_upto': ppr(c_rh, upto='2027-03'),
        'mid_dip': ppr(curve([0.0, 18.0, 27.0, 24.0, 48.0, 56.0])),
        'mid_dip_tick': ppr(curve([0.0, 18.0, 27.0, 26.5, 48.0, 56.0])),
        'flat': ppr(curve([0.0] * 10)),
        'noise_rise': ppr(curve([-0.25, 0.0, 0.25, 0.0, 0.25, -0.25, 0.0,
                                 0.25, 0.0, 0.25])),
        'falling': ppr(curve([30.0, 28.0, 24.0, 18.0, 10.0, 4.0, 1.0, 0.5,
                              0.25, 0.0])),
        'nan': ppr(curve([0.0, 18.0, float('nan'), 27.0, 41.0, 48.0])),
        'bool': ppr(curve([0.0, True, 27.0, 41.0, 48.0, 56.0])),
        'absent': ppr({'status': 'absent', 'rows': []}),
        'short': ppr(curve([0.0, 18.0])),
        'absent_all': ppr(None),
        'tail_dip_upto': ppr(curve([0.0, 18.0, 27.0, 41.0, 48.0, 56.0, 61.5,
                                    65.5, 68.0, 65.0]), upto='2027-05'),
        'tail_dip_all': ppr(curve([0.0, 18.0, 27.0, 41.0, 48.0, 56.0, 61.5,
                                   65.5, 68.0, 65.0])),
        'upto_early': ppr(c_rh, upto='2026-11'),
        's3_face': ppr(curve(s3)),
        's3_upto': ppr(curve(s3), upto='2027-07'),
        'bleed': ppr(curve([0.0, 30.0, 27.0, 24.0, 20.0, 16.0])),
        'deep_dip': ppr(curve([0.0, 30.0, 15.0, 48.0, 56.0, 60.0])),
        'edge_dip': ppr(curve([0.0, 30.0, 17.5, 48.0, 56.0, 60.0])),
        'edge_dip_over': ppr(curve([0.0, 30.0, 17.4, 48.0, 56.0, 60.0])),
        'tail_deep_all': ppr(curve([0.0, 18.0, 27.0, 41.0, 48.0, 56.0, 61.5,
                                    65.5, 68.0, 55.0])),
        'rise_half_step': ppr(curve([0.0, 2.0, 4.0, 6.0, 8.0, 12.5])),
        'rise_over_half': ppr(curve([0.0, 2.0, 4.0, 6.0, 8.0, 13.0])),
        'band_custom': ppr(curve([0.0, 30.0, 20.0, 48.0, 50.0, 52.0]),
                           band_bp=5.0),
        'tick_band': ppr(curve([0.0, 30.0, 20.0, 48.0, 50.0, 52.0]),
                         tick_bp=30.0),
    }
    check('§T5-h1 席位工具 pricing_path_rising(纯函数面): 2026-11-25 演习面(首月 '
          '−0.25bp/末两月 −0.5bp)与日终真实面(末月回落 1bp)判为累计上调路径(旧内联'
          '规则判否=误拒);中段回落 3bp 与恰一个最小变动价位=噪声内通过;平坦/噪声内'
          '升降=flat_or_falling;下行路径=拒;非数值(True/NaN)=non_numeric;缺席/行数'
          '不足=absent',
          got['rh_all'] == (True, 'ok') and got['rh_upto'] == (True, 'ok')
          and got['s3_face'] == (True, 'ok') and got['s3_upto'] == (True, 'ok')
          and old_rule is False
          and got['mid_dip'] == (True, 'ok')
          and got['mid_dip_tick'] == (True, 'ok')
          and got['flat'] == (False, 'flat_or_falling')
          and got['noise_rise'] == (False, 'flat_or_falling')
          and got['falling'][0] is False
          and got['nan'] == (False, 'non_numeric')
          and got['bool'] == (False, 'non_numeric')
          and got['absent'] == (False, 'absent')
          and got['short'] == (False, 'absent')
          and got['absent_all'] == (False, 'absent'),
          json.dumps(got, ensure_ascii=False))
    check('§T5-h2 只核判定档引用到的最后合约月之前: 末段(引用月之后)回落 3bp 的曲线'
          '在 upto=2027-05 下与全曲线下均通过(噪声内);末段回落 13bp(超过噪声界)只在'
          '全曲线下 not_cumulative;upto 早于第二个月=absent(无可判期数)',
          got['tail_dip_upto'] == (True, 'ok')
          and got['tail_dip_all'] == (True, 'ok')
          and got['tail_deep_all'] == (False, 'not_cumulative')
          and got['upto_early'] == (False, 'absent'),
          json.dumps([got['tail_dip_upto'], got['tail_dip_all'],
                      got['tail_deep_all'], got['upto_early']],
                     ensure_ascii=False))
    edge = [
        ('单月跌破此前峰值 4bp 后继续下滑(累计 14bp)=不是累计上调', 'bleed',
         (False, 'not_cumulative')),
        ('单月深回落 15bp=not_cumulative', 'deep_dip', (False, 'not_cumulative')),
        ('单月回落恰等于噪声界 12.5bp=通过(运行峰值 30→17.5)', 'edge_dip',
         (True, 'ok')),
        ('单月回落超过噪声界 0.1bp=not_cumulative', 'edge_dip_over',
         (False, 'not_cumulative')),
        ('首尾净上行恰等于噪声界 12.5bp=flat_or_falling', 'rise_half_step',
         (False, 'flat_or_falling')),
        ('首尾净上行超过噪声界 0.5bp=通过', 'rise_over_half', (True, 'ok')),
        ('band_bp=5 时回落 10bp=not_cumulative', 'band_custom',
         (False, 'not_cumulative')),
        ('tick_bp=30 时噪声界取 30(不小于最小变动价位)=通过', 'tick_band',
         (True, 'ok')),
    ]
    ebad = [(n, got[k]) for n, k, w in edge if got[k] != w]
    src = open(os.path.join(ROOT, 'scripts', 'seat_tools',
                            'make_expectations_gap_judgment.py'),
               encoding='utf-8').read()
    i_def = src.index('def pricing_path_rising(')
    m_call = re.search(r'(?m)^[^\n]*\b_pp_ok, _pp_why = pricing_path_rising\(\s*pr,\s*upto=', src)
    i_write = src.index('json.dump(judgment, open(jp_out')
    check('§T5-h3 静态锁: 旧内联条件(逐行 change_bp≥0 且末>首)退场,顶部只留结构性'
          '检查;形态守卫以引用月末月(upto=编号路径到期月/期限月、同期限参照月、证伪'
          '窗口末个完整合约月的最大者)调用,位于写出判定档之前;函数定义先于调用;'
          '最小变动价位常量=0.5bp、定价步长常量=25bp、噪声界=两者较大者(12.5bp);'
          '回落按此前运行峰值判',
          "x['change_bp'] >= 0 for x in prow" not in src
          and "refuse('联邦基金利率期货定价缺席')" in src
          and bool(m_call) and i_def < m_call.start() < i_write
          and 'step_m, hor_m, hz_m, win_m)' in src[m_call.start():m_call.start() + 260]
          and tick == 0.5 and step == 25.0 and band == 12.5
          and 'PRICING_STEP_BP = 25.0' in src
          and 'band = max(float(tick_bp), PRICING_STEP_BP / 2.0' in src
          and 'if v < peak - band:' in src
          and 'if not vals[-1] - vals[0] > band:' in src,
          'def=%d call=%s write=%d' % (i_def, m_call and m_call.start(), i_write))
    check('§T5-h4 噪声界边界(修订 r14): %d 例' % len(edge), not ebad, ebad)


def sec_t5_i():
    print('§T5-i 席位工具修订 r13(独立预审第二轮折入: 读数月标签/阈值就近折合/'
          '相似证据三段全列;门内只核纯函数与静态锁,整份装配留仓外在真实数据面核)')
    ns = _t5_seat_helpers()
    sb = ns['step_band']
    ss = ns['seg_start_ym']
    _d = ['2025-10-01', '2025-11-01', '2025-12-01', '2026-01-01', None]
    _v = [0.21, 0.478, 0.557, 0.728, None]
    got_band = [sb(69.0, 25.0), sb(56.5, 25.0), sb(12.5, 25.0), sb(2.0, 25.0),
                sb(75.0, 25.0)]
    got_seg = [ss(_d, _v, '2025-12', 0.478), ss(_d, _v, '2026-01', 0.557),
               ss(_d, _v, '2025-11', 0.21), ss(_d, _v, '2025-12', 0.9),
               ss(_d, _v, '2025-10', 0.21), ss(_d, _v, '2025-12', 0.728)]
    check('§T5-i1 step_band: 就近折合(69→75/三次/差 6;56.5→50/两次/差 6.5;半步 12.5'
          '→25/一次;不足半步 2→0 次;恰为步长整数倍→自身)',
          got_band == [(75.0, 3, 6.0), (50.0, 2, 6.5), (25.0, 1, 12.5),
                       (0.0, 0, 2.0), (75.0, 3, 0.0)],
          repr(got_band))
    check('§T5-i2 seg_start_ym: 段首变动点之前最后一个与段首值相等的观测所在月'
          '(2025-12/0.478→2025-11;2026-01/0.557→2025-12;2025-11/0.21→2025-10;'
          '值不在序列/段首之前无观测/等于段首变动点当月或更晚的观测→None;'
          '空值跳过)',
          got_seg == ['2025-11', '2025-12', '2025-10', None, None, None],
          repr(got_seg))
    src = open(os.path.join(ROOT, 'scripts', 'seat_tools',
                            'make_expectations_gap_judgment.py'),
               encoding='utf-8').read()
    flat = re.sub(r'\s+', ' ', src)
    locks = [
        ('阈值两处均用 step_band(向上取整的 steps_of 退场)',
         '_hz_thr, _hz_n, _hz_d = step_band(hz_bp, step_bp)' in src
         and "_wp_thr, _wp_n, _wp_d = step_band(win_p.get('change_bp'), "
         "step_bp)" in src and 'def steps_of(' not in src
         and 'steps_of(' not in src),
        ('起点月由冻结序列查得并须等于段首变动点前月(不符拒绝)',
         "seg_start_ym(_ds, _vs, _g['from_ym'], _g['v0'])" in src
         and "if _st != ym_shift(_g['from_ym'], -1):" in src
         and "'start_ym': _st, 'n': _g['n']," in src),
        ('月均段两处措辞均为「平台到平台上行段: 起点月 月均 A→终点月 月均 B(+Nbp,'
         '经 … 个相邻月变动点)」',
         src.count('月均序列平台到平台上行段') == 1
         and src.count('平台到平台上行段(月均序列)') == 1
         and "cell_name(e.get('metric_id')), e['start_ym']," in src
         and "fmt(e.get('from')), e['to_ym'], fmt(e.get('to'))," in src
         and '月均序列上行段 %s→%s(+%dbp' not in src),
        ('三段全列;三段全部同向才记「有历史相似证据」;标引擎事后表现口径',
         'aligned = all(_dirs)' in src
         and "有历史相似证据' if aligned else '纯逻辑推理'" in src
         and '(引擎事后表现口径,非月末口径;按「段×资产」计,' in src
         and '相似检索第 %s 名 %s 段事后 3 个月(SPX' not in src),
        ('证伪条件就近折合并写互补的另一半;阈值步数与隐含幅度之差均写入',
         '就近折合' in src and 'cn_amt(_wp_n - 1)' in src
         and "fmt(_wp_thr - step_bp)" in src
         and '折合等于或超过%s次加息' not in src),
        ('E-C1 引用含中国政策三指标与四个资产指标',
         "'HY_OAS', 'CN_LPR_1Y', 'CN_OMO_7D', 'CN_POLICY_OVERNIGHT', 'NIKKEI225', "
         "'GOLD_F', 'DXY', 'VIX')}" in flat),
        ('问句逐字引用(改写后加引号的旧句退场);可见文件数旁写有对照行的份数',
         "blk.get('question_verbatim')" in src and 'n_views_rows' in src
         and '问句问的是『市场定价和机构观点之间有哪些预期差' not in src),
        ('G-C3: 推算增速标出处;中国增长预测逐口径并列;全球增长未映射行按年并列',
         '非机构原文给出的增速' in src and '期限不一' not in src
         and '_unmapped_growth_txt' in src),
        ('质量说明: 覆盖状态中文;「N段」无空格;期货引用去重',
         "_COV_CN = {'present': '已入库', 'absent': '未入库'}" in src
         and "'%d 段(%s)'" not in src and 'list(dict.fromkeys(' in src),
        ('情景前提区分假设与事实;三时点读数带观测日',
         '假设读数在转折窗后继续上行' in src and '三锚点间逐期走低' in src
         and "anchor(_gdp_c, lbl).get('observation_date')" in src),
        ('E-C1 利率分句并列近 1 个月窗;分量写文字不写指标编号'
         '(同子句别名重复出现时断言域只遮罩首次,编号内数字会被当读数)',
         ";近1个月窗(%s→%s)UST_10Y " in src
         and 'comp_txt(c12), comp_txt(c1),' in src
         and '两窗各自变动较大的分量为 %s 与 %s' not in src),
    ]
    bad = [name for name, ok in locks if not ok]
    check('§T5-i3 静态锁(席位工具源码): %d 项' % len(locks), not bad,
          '; '.join(bad))
    ct = ns['comp_txt']
    got_ct = [ct({'TIPS_10Y': 30.0, 'BEI_10Y': -19.0}),
              ct({'TIPS_10Y': -11.0, 'BEI_10Y': 19.0}),
              ct({'TIPS_10Y': 11.0, 'BEI_10Y': -11.0}),
              ct({'TIPS_10Y': None, 'BEI_10Y': None}), ct({})]
    wa = ns['win_agree_txt']
    # 用例一=真实数据面形态(3 个月窗: 名义与 TIPS 上行、盈亏平衡下行;近 1 个月窗:
    # 名义与盈亏平衡下行、TIPS 上行)→ TIPS 与盈亏平衡两窗同向,名义不同向
    got_wa = [wa({'UST_10Y': 40.0, 'TIPS_10Y': 30.0, 'BEI_10Y': -10.0},
                 {'UST_10Y': -8.0, 'TIPS_10Y': 11.0, 'BEI_10Y': -19.0}),
              wa({'UST_10Y': 1.0, 'TIPS_10Y': 1.0, 'BEI_10Y': -1.0},
                 {'UST_10Y': 2.0, 'TIPS_10Y': 0.5, 'BEI_10Y': -0.5}),
              wa({}, {})]
    _AL = __import__('research_contract.text_consistency', fromlist=['x'])
    check('§T5-i4 comp_txt/win_agree_txt: 变动较大的分量与两窗方向均写文字'
          '(TIPS 实际收益率/盈亏平衡通胀率/名义收益率);幅度相同与全零/缺值各如实写;'
          '返回文字不命中任何指标别名',
          got_ct == ['TIPS 实际收益率', '盈亏平衡通胀率', '两者变动幅度相同',
                     '两者变动均为零', '两者变动均为零']
          and got_wa == ['两窗同向者: TIPS 实际收益率、盈亏平衡通胀率;不同向者: 名义收益率',
                         '三者两窗同向', '三者两窗同向']
          and not any(_AL._find_alias(x) for x in got_ct + got_wa),
          repr((got_ct, got_wa)))
    sd_ = ns['_seg_dir_ok']
    hc_ = ns['_hyp_count']
    ht_ = ns['_hyp_txt']
    segs = [
        {'aftermath': {'SPX': {'3m': 10.15, '6m': 18.74},
                       'GOLD_F': {'3m': 5.14, '6m': 23.12},
                       'DXY': {'3m': -7.08, '6m': -6.22}}},
        {'aftermath': {'SPX': {'3m': -6.27, '6m': 0.37},
                       'GOLD_F': {'3m': -7.19, '6m': 1.37},
                       'DXY': {'3m': 6.64, '6m': -1.54}}},
        {'aftermath': {'SPX': {'3m': 14.34, '6m': 18.83},
                       'GOLD_F': {'3m': 3.06, '6m': 15.87},
                       'DXY': {'3m': -3.38, '6m': -0.62}}},
    ]
    check('§T5-i5 相似证据计数(段×资产): 事后 3 个月同向 3/相反 6、事后 6 个月'
          '同向 0/相反 9;只有第二段三个资产全同向;读数缺席与零值计入缺席',
          [sd_(x) for x in segs] == [False, True, False]
          and sd_({'aftermath': {'SPX': {'3m': None}}}) is None
          and hc_(segs, '3m') == (3, 6, 0) and hc_(segs, '6m') == (0, 9, 0)
          and hc_(segs[:1] + [{'aftermath': {}}], '6m') == (0, 3, 3)
          and hc_([{'aftermath': {'SPX': {'3m': 0}}}], '3m') == (0, 0, 3)
          and ht_(segs, '6m') == '事后 6 个月与方向假设同向零段、相反九段'
          and ht_(segs[:1] + [{'aftermath': {}}], '6m')
          == '事后 6 个月与方向假设同向零段、相反三段(另有三段读数缺席或为零)',
          repr((hc_(segs, '3m'), hc_(segs, '6m'), ht_(segs, '6m'))))
    print('§T5-i 说明: 席位工具整份装配不在门内跑(工具只服务其预设的真实工单,含'
          '机构观点内容);修订后的装配在仓外真实数据面上逐句比对与正式 attach 核验,'
          '见证据包预审目录与报告。')


def sec_t5_j():
    print('§T5-j 任务5修订 r14(独立席终审 REVISE 后的闭环): 多窗结构化对质'
          '(软字段 face_off_checks;旧档零漂移)/机构间分歧幅度段渲染/席位工具'
          '文字修订静态锁')
    xg = _xg()
    import research_map_planner as rmp
    import judgment_contract as jc
    t, snap = _t5_tree('t5j')
    sd = _jq(snap)
    reg = wd.load_registry(t)['by_id']
    rep = _plan_on(t, Q_T5)
    rp = rep.get('research_plan') or {}
    rj = copy.deepcopy(rep)
    rj['steps'] = _t5_steps_with_series(sd, reg, ('DFF', 'SPX'),
                                        rep.get('steps') or [])
    rj2 = copy.deepcopy(rj)
    rj2['steps'] = rj2['steps'] + [_t5_syn_step(      # 合成序列(非真实数据)
        'SYN_ZERO', ['2026-08-03', '2026-09-01', '2026-10-01'],
        [0.0, 1.0, 2.0], 'index_point_2010')]
    face = jc.build_face(rj)
    face2 = jc.build_face(rj2)
    cut = rp.get('cutoff')
    WA = {'from': '2026-08', 'to': '2026-10'}
    WB = {'from': '2026-10', 'to': '2026-11'}
    OPS = {'>=': lambda p, q: p >= q, '>': lambda p, q: p > q,
           '<=': lambda p, q: p <= q, '<': lambda p, q: p < q,
           '==': lambda p, q: abs(p - q) < 1e-9,
           '!=': lambda p, q: abs(p - q) >= 1e-9}

    def mlast(mid, ym):
        d, v = _t5_obs(sd, mid, ym + '-31')
        return (d, v) if d and d[:7] == ym else (None, None)

    def exp_note(items):
        """门内独立拼多窗复算注记(月末口径;逐月独立取读数)→ (注记, 总裁决)"""
        det, vs = [], []
        for it_ in items:
            w = it_['observation_window']
            segs, spans, holds = [], [], {}
            for side, lbl in (('main', '主解释'), ('competing', '竞争解释')):
                parts, h = [], True
                for mid, cc in it_[side].items():
                    pts = [(ym, p) for ym in _t5_months(w['from'], w['to'])
                           for p in (mlast(mid, ym),) if p[0]]
                    v0, v1 = pts[0][1][1], pts[-1][1][1]
                    u = cc['unit']
                    q = (round((v1 - v0) * 100.0, 6) if u == 'bp'
                         else round(v1 - v0, 6) if u == 'pp'
                         else round((v1 / v0 - 1.0) * 100.0, 6))
                    ok_ = OPS[cc['op']](q, float(cc['value']))
                    h = h and ok_
                    parts.append('%s %s %g%s→观测 %+.2f%s%s' % (
                        mid, cc['op'], cc['value'], u, q, u,
                        '成立' if ok_ else '不成立'))
                    spans.append('%s→%s(%d 期)' % (pts[0][0], pts[-1][0],
                                                   len(pts)))
                holds[side] = h
                segs.append('%s(%s)' % (lbl, '且'.join(parts)))
            vs.append('尚不能区分' if holds['main'] == holds['competing']
                      else '支持主解释' if holds['main'] else '支持竞争解释')
            det.append('窗 %s: %s→%s' % (spans[-1], ';'.join(segs), vs[-1]))
        exp = (vs[0] if all(x == vs[0] for x in vs) else '尚不能区分')
        return ' / '.join(det) + '→' + exp, exp

    def it(win, main, comp):
        return {'observation_window': dict(win), 'main': dict(main),
                'competing': dict(comp)}

    def c(op, value, unit='bp'):
        return {'op': op, 'value': value, 'unit': unit}

    M_UP, M_DN = {'DFF': c('>=', 12.5)}, {'DFF': c('<', 12.5)}
    TWO = [it(WA, M_UP, M_DN), it(WB, M_UP, M_DN)]
    SAME = [it(WA, M_UP, M_DN), it(WA, M_UP, M_DN)]
    BOTH = [it(WA, {'DFF': c('>=', 0)}, {'DFF': c('>=', -100)}),
            it(WB, {'DFF': c('>=', 0)}, {'DFF': c('>=', -100)})]
    AND_T = [it(WA, {'DFF': c('>=', 12.5), 'SPX': c('>', -1000000, 'pct')}, M_DN)]
    AND_F = [it(WA, {'DFF': c('>=', 12.5), 'SPX': c('<', -1000000, 'pct')}, M_DN)]
    base = {'observed_fact': '门夹具观察事实甲(合成)',
            'causal_hypothesis': '门夹具因果假设(合成)',
            'competing_explanation': '门夹具竞争解释(合成)',
            'distinguishing_metric': 'DFF',
            'main_predicts': '门夹具主解释预期(合成)',
            'competing_predicts': '门夹具竞争解释预期(合成)',
            'face_off_verdict': '尚不能区分'}

    def run(link, fc=None):
        j = {'reader_map': {'transmission': [{'links': [link]}]}}
        out = jc._map_checks(j, fc or face, rj2 if fc else rj)
        return [x for x in out if '.face_off_checks' in x['item']
                or x['item'].endswith('.face_off_verdict')]

    pos = [
        ('两窗分别支持两侧→尚不能区分(声明一致)', dict(base, face_off_checks=TWO)),
        ('同上而声明「支持主解释」=CONTRADICTED',
         dict(base, face_off_verdict='支持主解释', face_off_checks=TWO)),
        ('两窗同向支持主解释(声明一致)',
         dict(base, face_off_verdict='支持主解释', face_off_checks=SAME)),
        ('两窗同向而声明「尚不能区分」=CONTRADICTED',
         dict(base, face_off_checks=SAME)),
        ('两侧条件同时成立→尚不能区分', dict(base, face_off_checks=BOTH)),
        ('多指标取且: 第二条件恒真(声明一致)',
         dict(base, face_off_verdict='支持主解释', face_off_checks=AND_T)),
        ('多指标取且: 第二条件不成立→主解释不成立→两侧均不成立(声明相左)',
         dict(base, face_off_verdict='支持主解释', face_off_checks=AND_F)),
        ('同上声明「尚不能区分」=VERIFIED',
         dict(base, face_off_checks=AND_F)),
        ('百分点口径',
         dict(base, face_off_checks=[it(
             WA, {'DFF': c('>=', 0.2, 'pp')}, {'DFF': c('>=', 0.2, 'pp')})])),
        ('百分比口径(声明一致)',
         dict(base, face_off_verdict='支持主解释', face_off_checks=[
             it(WA, {'DFF': c('>=', 5, 'pct')}, {'DFF': c('<', 5, 'pct')})])),
        ('指数序列近 1 个月窗支持竞争解释(声明一致)',
         dict(base, face_off_verdict='支持竞争解释', face_off_checks=[
             it(WB, {'SPX': c('<', -1000000, 'pct')},
              {'SPX': c('>', -1000000, 'pct')})])),
        ('判断缺席=与复算不一致(声明空)',
         {k: v for k, v in dict(base, face_off_checks=[it(WA, M_UP, M_DN)]).items()
          if k != 'face_off_verdict'}),
    ]
    pbad = []
    for name, link in pos:
        want, exp = exp_note(link['face_off_checks'])
        got_ = run(link)
        hit = [x for x in got_ if x['item'].endswith('.face_off_checks')]
        miss = [x for x in got_ if x['item'].endswith('.face_off_verdict')
                and x['status'] == 'CONTRADICTED']
        if link.get('face_off_verdict') == exp:
            okk = (len(hit) == 1 and hit[0]['status'] == 'VERIFIED'
                   and hit[0]['note'] == want and not miss
                   and all(x['status'] == 'VERIFIED' for x in got_))
        else:
            okk = (len(miss) == 1
                   and miss[0]['note'] == (
                       '对质判断与多窗结构化复算不一致: '
                       + want[:-(len(exp) + 1)] + '→应为 ' + exp
                       + '(声明 %s)' % (link.get('face_off_verdict') or '空'))
                   and not hit)
        if not okk:
            pbad.append((name, [(x['status'], x['item'][-28:], x['note'][:60])
                                for x in got_], exp))
    neg = [
        ('空列表', dict(base, face_off_checks=[]), '.face_off_checks',
         'NOT_VERIFIED', '须为非空列表'),
        ('非列表', dict(base, face_off_checks='x'), '.face_off_checks',
         'NOT_VERIFIED', '须为非空列表'),
        ('项非对象', dict(base, face_off_checks=['x']), '.face_off_checks[0]',
         'NOT_VERIFIED', '须带 observation_window'),
        ('项缺观测窗', dict(base, face_off_checks=[{'main': M_UP,
                                                 'competing': M_DN}]),
         '.face_off_checks[0]', 'NOT_VERIFIED', '须带 observation_window'),
        ('未配竞争解释', dict(base, face_off_checks=[it(WA, M_UP, M_DN)]),
         '.face_off_checks', 'NOT_VERIFIED', '须配竞争解释'),
        ('窗终月晚于研究截止月', dict(base, face_off_checks=[it(
            {'from': '2026-10', 'to': '2026-12'}, M_UP, M_DN)]),
         '.face_off_checks[0]', 'NOT_VERIFIED', '晚于研究截止月'),
        ('序列缺席', dict(base, face_off_checks=[it(
            WA, {'NOPE_X': c('>=', 12.5)}, M_DN)]),
         '.face_off_checks[0].main.NOPE_X', 'CONTRADICTED', '不在证据面'),
        ('指标编号非法', dict(base, face_off_checks=[it(
            WA, {'dff': c('>=', 12.5)}, M_DN)]),
         '.face_off_checks[0].main', 'NOT_VERIFIED', '指标编号非法'),
        ('主解释侧为空', dict(base, face_off_checks=[it(WA, {}, M_DN)]),
         '.face_off_checks[0].main', 'NOT_VERIFIED', '须为非空对象'),
        ('竞争解释侧缺席', dict(base, face_off_checks=[
            {'observation_window': dict(WA), 'main': M_UP}]),
         '.face_off_checks[0].competing', 'NOT_VERIFIED', '须为非空对象'),
        ('算子非法', dict(base, face_off_checks=[it(
            WA, {'DFF': c('≈', 12.5)}, M_DN)]),
         '.face_off_checks[0].main.DFF', 'NOT_VERIFIED', 'op:'),
        ('单位非法', dict(base, face_off_checks=[it(
            WA, {'DFF': c('>=', 12.5, 'xx')}, M_DN)]),
         '.face_off_checks[0].main.DFF', 'NOT_VERIFIED', 'pct/bp/pp'),
        ('阈值非数值', dict(base, face_off_checks=[it(
            WA, {'DFF': c('>=', '12.5')}, M_DN)]),
         '.face_off_checks[0].main.DFF', 'NOT_VERIFIED', '数值'),
        ('阈值为布尔', dict(base, face_off_checks=[it(
            WA, {'DFF': c('>=', True)}, M_DN)]),
         '.face_off_checks[0].main.DFF', 'NOT_VERIFIED', '数值'),
        ('窗内不足两期', dict(base, face_off_checks=[it(
            {'from': '2026-08', 'to': '2026-08'}, M_UP, M_DN)]),
         '.face_off_checks[0].observation_window', 'NOT_VERIFIED', '不足两期'),
        ('窗形非法', dict(base, face_off_checks=[it(
            {'from': '2026-8', 'to': '2026-10'}, M_UP, M_DN)]),
         '.face_off_checks[0].observation_window', 'NOT_VERIFIED', 'YYYY-MM'),
        ('首期为零不可算(合成序列)', dict(
            base, face_off_checks=[it(WA, {'SYN_ZERO': c('>=', 1, 'pct')},
                                      {'SYN_ZERO': c('<', 1, 'pct')})]),
         '.face_off_checks[0].main.SYN_ZERO', 'NOT_VERIFIED', '不可复算'),
    ]
    nbad = []
    for i, (name, link, suf, st_, frag) in enumerate(neg):
        link = dict(link)
        if frag == '须配竞争解释':
            link.pop('competing_explanation', None)      # 该例=未配竞争解释
        got_ = run(link, face2 if 'SYN_' in str(link.get('face_off_checks')) else None)
        hit = [x for x in got_ if x['item'].endswith(suf)]
        if not (len(hit) == 1 and hit[0]['status'] == st_ and frag in hit[0]['note']):
            nbad.append((name, [(x['status'], x['item'][-34:], x['note'][:50])
                                for x in got_]))
    check('§T5-j1 多窗结构化对质(契约函数级;冻结快照真序列;门内独立逐月取读数'
          '逐字拼注记): %d 例——同一区分环各窗分别复算,单窗内一侧全部条件成立=该窗'
          '支持该侧(多指标取且),两解释同成立/同不成立=该窗尚不能区分,各窗一致=该侧、'
          '不一致=尚不能区分;声明与复算一致=VERIFIED(注记与门内独立拼逐字相同),'
          '不一致=CONTRADICTED;门内独立算: DFF 2026-08→2026-10 为 %s bp、'
          '2026-10→2026-11 为 %s bp' % (
              len(pos), round((mlast('DFF', '2026-10')[1]
                               - mlast('DFF', '2026-08')[1]) * 100.0, 2),
              round((mlast('DFF', '2026-11')[1] - mlast('DFF', '2026-10')[1])
                    * 100.0, 2)),
          not pbad, pbad)
    check('§T5-j2 多窗对质反例(字段在场才核): %d 例全部拦下并给具体原因(窗晚于'
          '截止月/序列不在证据面/编号·算子·单位·阈值非法/侧为空/窗不可复算/未配'
          '竞争解释/空列表)' % len(neg), not nbad, nbad)
    # ── 旧档零漂移(软字段: 不在场=None=不判、不渲染) ──
    leg_w = dict(base, observation_window=WA)
    o0 = jc._map_checks({'reader_map': {'transmission': [{'links': [dict(base)]}]}},
                        face, rj)
    o1 = jc._map_checks({'reader_map': {'transmission': [{'links': [leg_w]}]}},
                        face, rj)
    o2 = jc._map_checks({'reader_map': {'transmission': [{'links': [
        dict(leg_w, face_off_checks=None)]}]}}, face, rj)
    dobs = rmp._distinguishing_obs(rj, cut, 'DFF')
    cell_1 = rmp._face_off_obs_cell(rj, cut, leg_w, 'DFF', dobs)
    cell_0 = rmp._face_off_obs_cell(rj, cut, dict(base), 'DFF', dobs)
    cell_n = rmp._face_off_obs_cell(rj, cut, dict(leg_w, face_off_checks=None),
                                    'DFF', dobs)
    m_none = [rmp._face_off_multi_obs(rj, cut, lk_, dobs) for lk_ in (
        {}, dict(base), dict(leg_w, face_off_checks=None),
        dict(leg_w, face_off_checks=[]), dict(leg_w, face_off_checks='x'))]

    def jd(links_a, links_b=()):
        return {'reader_map': {
            'headline_conclusion': '门夹具总判断(合成;非真实研判)。',
            'regions': [{'region': r, 'from_to': '门夹具走位(合成)。'}
                        for r in ('US', 'CN', 'EA', 'JP')],
            'transmission': [{'chain_name': '门夹具传导链甲(合成)',
                              'links': list(links_a)},
                             {'chain_name': '门夹具传导链乙(合成)',
                              'links': list(links_b)}],
            'turnings': [], 'history_periods': []}}

    lk_m = dict(base, face_off_checks=TWO)
    lk_s = dict(base, observation_window=WA,
                face_off_checks=[it(WA, M_UP, M_DN)])
    md_m = rmp.render_map_report(rj, jd([lk_m]), None, root=t)
    md_s = rmp.render_map_report(rj, jd([lk_s]), None, root=t)
    md_l = rmp.render_map_report(rj, jd([leg_w], [dict(base)]), None, root=t)
    w1 = rmp._window_obs_text(rj, 'DFF', WA, cut)
    w2 = rmp._window_obs_text(rj, 'DFF', WB, cut)
    inner = '[窗一] DFF %s | [窗二] DFF %s' % (w1, w2)
    multi = '(多窗: ' + inner + ')'
    multi1 = '(多窗: [窗一] DFF %s)' % w1
    row_m = ('| DFF | 门夹具主解释预期(合成) | 门夹具竞争解释预期(合成) | %s | '
             '尚不能区分 |' % multi)
    line_m = '   - 多窗对质观测(各窗分别复算): ' + inner
    tbl = md_m.split('## 主解释 vs 竞争解释(对质表)')[1].split('\n## ')[0]
    check('§T5-j3 渲染(多窗对质): 对质表「已有观测」格=「(多窗: [窗一] … | [窗二] '
          '…)」(各窗文字=旧同窗读数规则,门内独立调用逐字相同);传导图「能区分解释的'
          '指标」行下另起一行「多窗对质观测(各窗分别复算)」;带单窗观测窗又带多窗的'
          '环取多窗;旧格式(无字段)的渲染不含「多窗」',
          row_m in tbl and line_m in md_m
          and md_m.count('多窗对质观测(各窗分别复算): ') == 1
          and ('| %s | 尚不能区分 |' % multi1) in md_s.split(
              '## 主解释 vs 竞争解释(对质表)')[1].split('\n## ')[0]
          and '多窗' not in md_l and '多窗' not in cell_1,
          f"row={row_m in tbl} line={line_m in md_m} "
          f"single={('| %s | 尚不能区分 |' % multi) in md_s} "
          f"tail={multi[-70:]}")
    check('§T5-j4 旧档零漂移(软字段): 无字段与字段=None 的契约产出逐项相同(含带单窗'
          '观测窗的环);旧环零「多窗」项;渲染函数对无字段/None/空列表/非列表返回 '
          'None(调用方走旧输出),单窗观测窗的格与无观测窗的格不因新函数改变',
          o1 == o2 and not [x for x in o0 + o1 if '.face_off_checks' in x['item']]
          and cell_1 == cell_n and cell_0 is dobs and m_none == [None] * 5
          and '多窗' not in md_l,
          f"o_eq={o1 == o2} cell_eq={cell_1 == cell_n} "
          f"m={m_none} cell0={cell_0 is dobs}")
    # ── 机构间分歧段渲染(引擎;旧数值幅度逐字不变) ──
    sp = [
        ('数值幅度+说明', {'numeric_spread_bp': 25.0, 'spread_note': '说明甲(合成)'},
         '%s bp——%s' % (xg._cell(25.0), xg._cell('说明甲(合成)'))),
        ('数值幅度、说明缺席=旧输出逐字不变(含旧短横尾)',
         {'numeric_spread_bp': 25.0, 'spread_note': None},
         '%s bp——%s' % (xg._cell(25.0), xg._cell(None))),
        ('不可折算为基点、说明缺席', {'numeric_spread_bp': None, 'spread_note': None},
         '不可折算为基点(口径不同或不可比)'),
        ('不可折算为基点、带说明', {'numeric_spread_bp': None, 'spread_note': '说明乙(合成)'},
         '不可折算为基点(口径不同或不可比)——说明乙(合成)'),
        ('说明为短横=不加尾', {'numeric_spread_bp': None, 'spread_note': '—'},
         '不可折算为基点(口径不同或不可比)'),
        ('布尔不作数值', {'numeric_spread_bp': True, 'spread_note': None},
         '不可折算为基点(口径不同或不可比)'),
    ]
    spbad = [(n, xg._spread_txt(d), w) for n, d, w in sp if xg._spread_txt(d) != w]
    check('§T5-j5 机构间分歧段(_spread_txt;修订 r14 NIT): 可折算为基点=旧格式逐字'
          '不变;不可折算(点位对增速等口径不同或不可比)=写明口径,说明缺席不再输出'
          '连续短横;布尔不作数值: %d 例' % len(sp), not spbad, spbad)
    # ── 静态锁 ──
    rd_ = lambda *a: open(os.path.join(ROOT, *a), encoding='utf-8').read()
    ssrc = rd_('scripts', 'seat_tools', 'make_expectations_gap_judgment.py')
    esrc = rd_('scripts', 'expectations_gap.py')
    csrc = rd_('scripts', 'research_contract', 'judgment_contract.py')
    rsrc = rd_('scripts', 'research_map_planner.py')
    on = [
        ('多窗对质字段入判定档', "'face_off_checks'", 1),
        ('环一证伪: 截至日/可得读数观测日随行',
         '在 %s 或之前较截止日可得读数(%s 观测 %s)累计上调达到或超过 ', 1),
        ('环四期限推迟逻辑推演: 截止月随行', "'deadline': _e1_dl", 1),
        ('环四期限推迟逻辑推演: 不作幅度主张', '纯逻辑推演,未作幅度主张', 2),
        ('环四期限推迟逻辑推演: 推至截止月后三个月', 'ym_shift(as_of[:7], 3)', 1),
        ('转折: 十二个月窗内其他地区政策事件随行(含早于转折窗起点者)',
         '近十二个月窗内其他地区政策事件(含早于本转折窗起点者,日期随行): ', 1),
        ('东京 CPI 缺席披露', '_gap_mids', 2),
        ('已实现数据表述未映射行: 评论只写行数', '行号见质量门注记;原表述', 1),
        ('已实现数据表述未映射行: 行号入质量门注记', '行号在此点名,不入数值绑定', 1),
        ('已实现数据表述未映射行: 行号只在注记里展开',
         "str(r.get('row_id')) for r in _rd_unm)", 1),
        ('历史类比同步性: 不带花括号',
         "sync = ('%s: 截至%s已发布数据显示,%s。' % (", 1),
        ('历史类比样本注记: 单前缀', "note = ('检索范围=%s 个有效候选", 1),
        ('证伪条件(环二)', '同样未映射、未对账', 1),
        ('对质环甲竞争解释阈值(两窗各不少于五个基点)',
         '各不少于五个基点,阈值为席位自设', 1),
        ('对质环甲解释乙', '通胀预期回落快于名义收益率', 1),
        ('证伪条件(环三)', '差距应明显收窄', 1),
        ('年度窗分量函数', 'def _yr(txt):', 1),
        ('年度/近月两窗分量各自成句', '两窗各自变动较大的分量', 1),
        ('年度/近月两窗分量各自成句(长期窗)', '长期窗为%s,', 1),
        ('年度/近月两窗分量各自成句(近月窗)', '近1个月窗为%s)', 1),
        ('标题利率句改年度窗(「一年前」锚)', '12个月窗变动以%s分量为最大(近1个月窗分解见美债三利率分解节);', 1),
        ('标题利率句改年度窗(取十二个月窗分解)', 'tri12, biggest_component(c12),', 1),
        ('情景乙: 窗内只核路径前段', '窗口内只能核路径前段', 1),
        ('情景乙: 窗外最后完整合约月定价', '证伪窗口(%s→%s)之外,窗内最后一个完整合约月(%s)的定价为路径', 1),
        ('情景甲: 证伪=同口径同期限后差距不收窄', '换到同一口径与同一期限后差距仍不收窄(或随', 1),
    ]
    off = [
        ('情景乙旧通过线表述', '规则池通过线'),
        ('转折旧同步性标题', '同期其他地区政策事件'),
        ('历史类比样本注记旧双前缀', '样本注记: '),
        ('历史类比同步性旧花括号', '{%s}: '),
        ('标题旧近月分量句', '近月变动以%s分量为最大'),
        ('解释乙旧表述', 'BEI_10Y 主导性走低而 TIPS_10Y 转平'),
        ('解释乙旧变量', 'real_up_long'),
        ('环四旧固定截止日', "'deadline': '2027-02-28'"),
    ]
    obad = [(n, ssrc.count(p), w) for n, p, w in on if ssrc.count(p) != w]
    fbad = [(n, ssrc.count(p)) for n, p in off if p in ssrc]
    check('§T5-j6 席位工具修订静态锁(独立席终审 1 MAJOR/3 MINOR/18 NIT 的闭环;门内'
          '不跑整份装配): 已改表述 %d 处在场、旧表述 %d 处退场;契约多窗函数定义先于'
          '调用且在单窗对质之后调用;渲染多窗函数定义一处、调用两处(对质表格+传导图'
          '行);引擎分歧段模板改为经 _spread_txt' % (len(on), len(off)),
          not obad and not fbad
          and csrc.index('def _fo_face_off_checks(')
          < csrc.index('def _fo_face_off_multi_checks(') < csrc.index('def _map_checks(')
          and csrc.count('_fo_face_off_multi_checks(lk, lid, dm, face, plan, ok, bad)') == 2
          and csrc.count('_fo_face_off_checks(lk, lid, dm, face, plan, ok, bad)\n'
                         '            _fo_face_off_multi_checks(') == 1
          and rsrc.count('def _face_off_multi_obs(') == 1
          and rsrc.count('_face_off_multi_obs(') == 3
          and "return '(多窗: ' + multi + ')'" in rsrc
          and rsrc.index('def _face_off_multi_obs(')
          < rsrc.index('def _face_off_obs_cell(')
          and '多窗对质观测(各窗分别复算): ' in rsrc
          and esrc.count('def _spread_txt(') == 1
          and "d.get('n_rows'), _spread_txt(d))" in esrc
          and "d.get('n_rows'), _cell(d.get('numeric_spread_bp'))," not in esrc,
          f"on={obad} off={fbad}")
    print('§T5-j 说明: 修订后的席位工具整份装配不在门内跑(工具只服务其预设的真实'
          '工单,含机构观点内容);装配在仓外真实数据面上经工具自检、契约全量核验与'
          '隔离沙箱正式 attach/报告级渲染核验,见证据包与报告。')


# ══ 任务5修订 r15: 事实端对点位的触及状态(数据更新后正式链不再中断) ═════════
# 最终候选统一验收的网络链实测(上一候选): 真实 update 之后美国实际 GDP 同比
# (年度修订)最新读数由点位之下改到点位之上,席位工具在「最新两期已不低于点位
# 即拒绝装配」处退出——正式链在席位一步中断、无判定档。修订 r15: 触及状态
# (未触发/首次触及/已成立)由纯函数按读数确定,推导、理由、证伪条件尾句与席位
# 摘要随状态如实写明;裁决口径不变(该行无同期限市场定价工具=非预期差);
# 前一季读数不可得才拒绝装配。未触发时各文字与修订前逐字相同(冻结数据零
# 漂移在仓外比对: 修订前后工具对同一冻结运行目录的判定档除写出时间外逐字
# 相同)。修订后的席位工具整份装配不在门内跑(同 §T5-j 说明)。


def _t5_r15_status_texts(state):
    """从席位工具源码抽取三态文字赋值语句(只依赖 _gdp_state)并在给定状态下
    执行 → dict;源码赋值语句不齐=None。"""
    import ast
    src = open(os.path.join(ROOT, 'scripts', 'seat_tools',
                            'make_expectations_gap_judgment.py'),
               encoding='utf-8').read()
    want = ('_gdp_fact', '_gdp_state_txt', '_gdp_reason', '_gdp_sum')
    body = [n for n in ast.parse(src).body
            if isinstance(n, ast.Assign) and len(n.targets) == 1
            and isinstance(n.targets[0], ast.Name)
            and n.targets[0].id in want]
    if [n.targets[0].id for n in body] != list(want):
        return None
    ns = {'_gdp_state': state}
    exec(compile(ast.Module(body=body, type_ignores=[]), 'seat_r15', 'exec'), ns)
    return {k: ns[k] for k in want}


def sec_t5_k():
    print('§T5-k 任务5修订 r15: 事实端对点位的触及状态(纯函数+三态文字)')
    ns = _t5_seat_helpers()
    import ast
    src = open(os.path.join(ROOT, 'scripts', 'seat_tools',
                            'make_expectations_gap_judgment.py'),
               encoding='utf-8').read()
    fn = [n for n in ast.parse(src).body
          if isinstance(n, ast.FunctionDef) and n.name == 'gdp_point_state']
    if len(fn) == 1:
        exec(compile(ast.Module(body=fn, type_ignores=[]), 'seat_r15', 'exec'),
             ns)
    gp = ns.get('gdp_point_state')
    Q = ['2025-04', '2026-04', '2026-07']     # 锚观测月: 三个月前=最新前一季度
    NQ = ['2025-03', '2026-03', '2026-07']    # 锚不相隔一个季度
    got = {
        'below': gp([3.0, 2.1, 2.19], 2.2, Q) if gp else None,
        'first': gp([3.0, 2.1, 2.29], 2.2, Q) if gp else None,
        'both': gp([3.0, 2.3, 2.29], 2.2, Q) if gp else None,
        'nq_path': (gp([3.0, 2.1, 2.29], 2.2, NQ, {'2026-04': 2.3})
                    if gp else None),
        'nq_none': gp([3.0, 2.1, 2.29], 2.2, NQ) if gp else None,
        'nq_below': gp([3.0, 2.1, 2.19], 2.2, NQ) if gp else None,
        'edge': gp([3.0, 2.2, 2.2], 2.2, Q) if gp else None}
    check('§T5-k-1 gdp_point_state(纯函数): 最新一期低于点位→未触发(0);最新一期'
          '不低于、前一季低于→首次触及(1);连续两期不低于→已成立(2);恰等于点位'
          '=不低于;锚不相隔一个季度时前一季读数取同比月路径(路径缺该月=None='
          '调用方拒绝装配);未触发时不依赖前一季读数',
          got == {'below': (0, 2.1), 'first': (1, 2.1), 'both': (2, 2.3),
                  'nq_path': (2, 2.3), 'nq_none': (None, None),
                  'nq_below': (0, 2.1), 'edge': (2, 2.2)}, 'got=%s' % (got,))
    t0 = _t5_r15_status_texts(0)
    t1 = _t5_r15_status_texts(1)
    t2 = _t5_r15_status_texts(2)
    check('§T5-k-2 三态文字: 未触发时推导结论/证伪条件尾句/判非预期差理由/摘要'
          '附注与修订前逐字相同(该行在冻结数据上的判定档零漂移);首次触及与'
          '已成立时四段文字各自写明触及/证伪,理由写明『机构对市场』的预期差'
          '无从建立,摘要附注以「;事实端」起',
          t0 == {'_gdp_fact': '与『增速放缓』的方向判断不矛盾',
                 '_gdp_state_txt': '未触发',
                 '_gdp_reason': '增长预测无同期限市场定价工具;与事实面方向不矛盾。',
                 '_gdp_sum': ''}
          and t1 is not None and t2 is not None
          and all(t1[k] and t2[k] for k in t0)
          and '首季相悖' in t1['_gdp_fact'] and '尚未成立' in t1['_gdp_state_txt']
          and '已在事实端被证伪' in t2['_gdp_fact']
          and '已成立' in t2['_gdp_state_txt']
          and all('『机构对市场』的预期差无从建立' in t[k]
                  for t in (t1, t2) for k in ('_gdp_reason',))
          and all(t['_gdp_sum'].startswith(';事实端') for t in (t1, t2)),
          't1=%s' % {k: (v[:24] if v else v) for k, v in (t1 or {}).items()})
    import judgment_contract as jc
    texts = [v for t in (t0, t1, t2) if t for v in t.values()]
    un = {tx[:16]: jc._pq_unbound_tokens(tx, set(), set()) for tx in texts}
    check('§T5-k-3 三态文字不引入数字(契约自由文字数字绑定在空数池下零未绑定:'
          '期数写「两个季度/首季/前一季」,不写阿拉伯数字与带量词中文整数)',
          len(texts) == 12 and not any(un.values()),
          'un=%s' % {k: v for k, v in un.items() if v})
    check('§T5-k-4 静态锁: 「最新两期已不低于点位即拒绝装配」退场;触及状态经 '
          'gdp_point_state 装配;推导结论/证伪条件尾句/理由/摘要附注四段随状态;'
          '前一季读数不可得才拒绝装配;三时点读数仍各带观测日',
          '最新两期同比已不低于点位' not in src
          and '最新两期已不低于点位即拒绝装配' not in src
          and '_gdp_state, _gdp_prev = gdp_point_state(' in src
          and '        _gdp_fact))' in src
          and '             _gdp_txt, _gdp_state_txt)),' in src
          and "'reason': _gdp_reason," in src
          and '美国增长预测,无同期限定价%s)' in src
          and "refuse('最新一期同比已不低于点位且前一季读数不可得" in src
          and "anchor(_gdp_c, lbl).get('observation_date')" in src
          and src.count('_gdp_state is None') == 1)


def sec_t5():
    print('═══ 任务5: 预期差研究接入正式入口 ═══')
    sec_t5_a()
    sec_t5_b()
    sec_t5_c()
    sec_t5_d()
    sec_t5_e()
    sec_t5_f()
    sec_t5_g()
    sec_t5_h()
    sec_t5_i()
    sec_t5_j()
    sec_t5_k()


def main():
    print('Audit-R33 门 (HEAD %s)' % WORKTREE_HEAD[:12])
    try:
        sec_t2()
        sec_t2b()
        sec_t2_k()
        sec_t2_l()
        sec_t2_m()
        sec_t2_n()
        sec_t1_a()
        sec_t1_b()
        sec_t1_c()
        sec_t1_d()
        sec_t1_e()
        sec_t1_f()
        sec_t1_g()
        sec_t1_h()
        sec_t3_a()
        sec_t3_b()
        sec_t3_c()
        sec_t3_d()
        sec_t3_e()
        sec_t3_f()
        sec_t3_g()
        sec_t4_a()
        sec_t4_b()
        sec_t4_c()
        sec_t4_d()
        sec_t4_e()
        sec_t4_f()
        sec_t4_g()
        sec_t4_h()
        sec_t4_i()
        sec_t4_j()
        sec_t5()
    finally:
        n_ok = sum(1 for x in RESULTS if x)
        n = len(RESULTS)
        print('=== R33 门: %d/%d ===' % (n_ok, n))
        shutil.rmtree(TMPG, ignore_errors=True)
    return 0 if all(RESULTS) else 1


if __name__ == '__main__':
    sys.exit(main())
