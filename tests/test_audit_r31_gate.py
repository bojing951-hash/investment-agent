#!/usr/bin/env python3
"""Audit-R31 门 — 研究时点统一/冻结三输入/关键证据校验。

任务1 研究截止日与回看窗统一: 裸年月+单一相对窗→一个截止日+一个回看
窗(真冲突仍拒);「以 X 为研究时点」贯穿计划/取数/覆盖检查/政策/报告
(发布可知面: 观测日与首发日均≤时点——10 月观测 11 月发布不入历史
研究)。
任务2 三输入钉死: 第一次取数前固定快照+发布日期历+指标注册表
(IA_SNAPSHOT_PIN/IA_CALENDAR_PIN/IA_REGISTRY_PIN;注册表/日历=入口
字节冻结副本)——计划/核验/历史渲染/发布批次/重放统一读冻结输入;
异常路径同样释放(同进程异常后再跑,新工单选 _v2);钉死文件移除
fail-closed。
任务3 关键证据校验: m12 同比基期=严格去年同月(13 个月前数据=缺基期,
不再冒充同比);判断席事件日-生效日成对(次月末生效不得写成当时已
发生);问句点名当前官方目标而仅有待生效公告→当前值缺证标注。
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import freshness_policy as fp                # noqa: E402
import release_calendar as rc                # noqa: E402
import workbench_data as wd                  # noqa: E402

TMPG = tempfile.mkdtemp(prefix='r31gate_')
RESULTS = []

Q_MAP = '美国、欧元区、中国、日本四地增长与通胀的最新地图对照'
Q_NEW30 = ('2026年11月,日本和欧元区最近六个月的通胀与政策环境有什么'
           '不同?哪些方面分化,哪些证据不足?请给出具体数据和各数据的'
           '公布时间。')
Q_AUG = '以 2026-08-21 为研究时点,日本和欧元区最近六个月的通胀与政策环境'


def check(name, ok, detail=''):
    ok = bool(ok)
    RESULTS.append(ok)
    print(('  ✅ ' if ok else '  ❌ ') + name +
          (' — ' + str(detail) if detail else ''))
    return ok


def _mk_tree():
    """迷你树: config(生产注册表/日历副本)+research_snapshot_20261121。"""
    import research_orchestrator as ro
    t = tempfile.mkdtemp(prefix='r31tree_', dir=TMPG)
    shutil.copytree(os.path.join(ROOT, 'config'),
                    os.path.join(t, 'config'))
    v1 = os.path.join(t, 'data', 'daily', 'research_snapshot_20261121.json')
    os.makedirs(os.path.dirname(v1), exist_ok=True)
    json.dump({'snapshot_id': 'research_snapshot_20261121',
               'target_date': '20261121',
               'facts': [], 'series_store': {}, 'r31_mark': 'V1'},
              open(v1, 'w', encoding='utf-8'))
    return t, v1


def _fake_step_ok(name, argv, timeout=180):
    return {'step': name, 'argv': list(argv), 'executed': True,
            'ok': True, 'exit_code': 0, 'semantic_ok': True,
            'note': None, 'duration_ms': 1, 'envelope': {'ok': True}}


def sec_a():
    """§A 任务2: 三输入钉死+异常安全释放+冻结副本不串号。"""
    import hashlib
    import research_orchestrator as ro
    print('═══ §A 任务2: 三输入钉死(快照/日历/注册表)+异常安全释放 ═══')

    # A1 运行级三钉死+返回后全释放(上游已钉死尊重)
    t, v1 = _mk_tree()
    seen = {}

    def _spy_step(name, argv, timeout=180):
        seen.setdefault('cal', os.environ.get('IA_CALENDAR_PIN'))
        seen.setdefault('reg', os.environ.get('IA_REGISTRY_PIN'))
        seen.setdefault('snap', os.environ.get('IA_SNAPSHOT_PIN'))
        return _fake_step_ok(name, argv, timeout)

    _orig = ro.run_step
    ro.run_step = _spy_step
    try:
        ro.run_research(Q_MAP, root=t,
                        out_dir=os.path.join(TMPG, 'r31_a1'))
    finally:
        ro.run_step = _orig
    check('§A1 运行中三钉死在位(快照/日历/注册表),返回后全部释放',
          bool(seen.get('snap')) and bool(seen.get('cal'))
          and bool(seen.get('reg'))
          and os.environ.get('IA_SNAPSHOT_PIN') is None
          and os.environ.get('IA_CALENDAR_PIN') is None
          and os.environ.get('IA_REGISTRY_PIN') is None,
          f'seen={ {k: bool(v) for k, v in seen.items()} }')
    # A1b 冻结 temp 副本已清理
    _leftover = [p for p in os.listdir(tempfile.gettempdir())
                 if p.startswith('ia_frozen_inputs_')]
    check('§A1b 冻结临时副本收尾清理(无泄漏目录)', not _leftover,
          f'leftover={_leftover[:3]}')
    shutil.rmtree(t, ignore_errors=True)

    # A2 运行中本地日历被改→冻结面仍=入口字节(frozen_inputs 与
    # root_overlay 副本都不吃运行中修改)
    t2, v1b = _mk_tree()
    _cal = os.path.join(t2, 'config', 'release_calendar.json')
    _reg = os.path.join(t2, 'config', 'metric_registry.json')
    _cal_entry = open(_cal, 'rb').read()
    _reg_entry = open(_reg, 'rb').read()
    _edited = [False]

    def _edit_step(name, argv, timeout=180):
        if name.startswith('S3') and not _edited[0]:
            _edited[0] = True
            _doc = json.load(open(_cal, encoding='utf-8'))
            _doc['entries'] = [e for e in _doc.get('entries') or []
                               if e.get('entry_id') != 'RC-EA-HICP-2022M06']
            json.dump(_doc, open(_cal, 'w', encoding='utf-8'),
                      ensure_ascii=False, indent=1)
            _doc2 = json.load(open(_reg, encoding='utf-8'))
            _doc2.setdefault('metrics', []).append(
                {'metric_id': 'R31EDIT_SENTINEL', 'unit': 'ratio',
                 'calendar': 'cn', 'frequency': 'monthly'})
            json.dump(_doc2, open(_reg, 'w', encoding='utf-8'),
                      ensure_ascii=False, indent=1)
        return _fake_step_ok(name, argv, timeout)

    ro.run_step = _edit_step
    try:
        rep = ro.run_research(Q_MAP, root=t2,
                              out_dir=os.path.join(TMPG, 'r31_a2'))
    finally:
        ro.run_step = _orig
    fi = (rep.get('run') or {}).get('frozen_inputs') or {}
    _cal_sha = hashlib.sha256(_cal_entry).hexdigest()[:16]
    _reg_sha = hashlib.sha256(_reg_entry).hexdigest()[:16]
    _ov_cal = os.path.join(rep['report_dir'], 'root_overlay',
                           'config', 'release_calendar.json')
    _ov_reg = os.path.join(rep['report_dir'], 'root_overlay',
                           'config', 'metric_registry.json')
    check('§A2 运行中改本地日历/注册表: frozen_inputs 摘要仍=入口字节'
          '(日历+注册表双件)',
          _edited[0]
          and fi.get('config/release_calendar.json') == _cal_sha
          and fi.get('config/metric_registry.json') == _reg_sha,
          f"fi_cal={fi.get('config/release_calendar.json')} "
          f"want={_cal_sha} fi_reg={fi.get('config/metric_registry.json')} "
          f"want={_reg_sha}")
    check('§A2b root_overlay 归档副本=入口字节(本地修改未入档)',
          os.path.isfile(_ov_cal) and open(_ov_cal, 'rb').read() == _cal_entry
          and os.path.isfile(_ov_reg)
          and open(_ov_reg, 'rb').read() == _reg_entry)
    # 本地确实被改(哨兵在场,证明区分真实)
    check('§A2c 哨兵确认: 本地文件确实被改(区分力证据)',
          b'R31EDIT_SENTINEL' in open(_reg, 'rb').read())
    shutil.rmtree(t2, ignore_errors=True)

    # A3 异常路径释放: S1 后抛异常→三钉死仍释放;同进程再跑(先落 _v2)
    # →新工单选 _v2(IA_SNAPSHOT_PIN 正确释放的直接证据)
    t3, v1c = _mk_tree()

    def _boom_step(name, argv, timeout=180):
        raise RuntimeError('R31 gate: 中途异常(异常释放探针)')

    ro.run_step = _boom_step
    try:
        try:
            ro.run_research(Q_MAP, root=t3,
                            out_dir=os.path.join(TMPG, 'r31_a3'))
            _raised = False
        except RuntimeError:
            _raised = True
    finally:
        ro.run_step = _orig
    check('§A3 异常路径三钉死释放(异常如实上抛,环境无残留)',
          _raised
          and os.environ.get('IA_SNAPSHOT_PIN') is None
          and os.environ.get('IA_CALENDAR_PIN') is None
          and os.environ.get('IA_REGISTRY_PIN') is None)
    # A3b 同进程二次运行选 _v2: 先落同日 _v2,再跑(钉死已释放→重解析)
    v2 = os.path.join(t3, 'data', 'daily',
                      'research_snapshot_20261121_v2.json')
    json.dump({'snapshot_id': 'research_snapshot_20261121_v2',
               'target_date': '20261121',
               'facts': [], 'series_store': {}, 'r31_mark': 'V2'},
              open(v2, 'w', encoding='utf-8'))
    seen2 = {}

    def _spy2_step(name, argv, timeout=180):
        seen2.setdefault('snap', os.environ.get('IA_SNAPSHOT_PIN'))
        return _fake_step_ok(name, argv, timeout)

    ro.run_step = _spy2_step
    try:
        ro.run_research(Q_MAP, root=t3,
                        out_dir=os.path.join(TMPG, 'r31_a3b'))
    finally:
        ro.run_step = _orig
    check('§A3b 异常释放后同进程新工单选 _v2(revision 感知)',
          seen2.get('snap') == v2, f"got={seen2.get('snap')} want={v2}")
    shutil.rmtree(t3, ignore_errors=True)

    # A4 resolver 面: 钉死优先/无钉死原语义/缺席 fail-closed
    os.environ['IA_CALENDAR_PIN'] = '/tmp/r31_no_such_cal.json'
    try:
        rc._load()
        _fc = False
    except FileNotFoundError as e:
        _fc = '拒绝静默回退' in str(e)
    check('§A4 日历钉死缺席=fail-closed(release_calendar._load 拒静默)',
          _fc)
    os.environ.pop('IA_CALENDAR_PIN', None)
    check('§A4b resolver 无钉死=原语义(本地路径),钉死=优先于传参',
          rc.resolved_calendar_path('/tmp/local.json') == '/tmp/local.json'
          and wd.resolved_registry_path(None).endswith(
              'config/metric_registry.json'))

    # A5 fact_engine 注册表钉死=冻结副本面(读钉死文件;显式路径优先
    # 于钉死;既有「显式 load 覆盖默认缓存」语义不破坏=p02_w2 依赖的
    # 污染-恢复机制原样)
    import fact_engine as fe
    _tmpd = tempfile.mkdtemp(prefix='r31fe_', dir=TMPG)
    _base_reg = json.load(open(os.path.join(ROOT, 'config',
                                            'metric_registry.json')))

    def _reg_with(mid):
        # 复制一条在册完整条目改名(语义校验器要求的字段齐全)
        d = json.loads(json.dumps(_base_reg))
        proto = json.loads(json.dumps(
            next(m for m in d['metrics'] if m.get('metric_id') == 'CPI')))
        proto['metric_id'] = mid
        d.setdefault('metrics', []).append(proto)
        return d

    _frozen_reg = os.path.join(_tmpd, 'frozen_reg.json')
    _local_reg = os.path.join(_tmpd, 'local_reg.json')
    json.dump(_reg_with('R31FROZEN_SENTINEL'),
              open(_frozen_reg, 'w', encoding='utf-8'))
    json.dump(_reg_with('R31LOCAL_SENTINEL'),
              open(_local_reg, 'w', encoding='utf-8'))
    fe._REGISTRY_CACHE = None
    os.environ['IA_REGISTRY_PIN'] = _frozen_reg
    r1 = fe.load_registry()
    ok1 = ('R31FROZEN_SENTINEL' in r1['by_id']
           and 'R31LOCAL_SENTINEL' not in r1['by_id'])
    # 显式路径仍优先于钉死(path≠None→钉死不接管;覆盖默认缓存=既有
    # 机制,p02_w2 load_temp_registry 依赖)
    r2 = fe.load_registry(_local_reg, force=True)
    ok2 = 'R31LOCAL_SENTINEL' in r2['by_id']
    # 钉死在场+无显式路径: 读冻结文件(不吃上一步显式污染)
    r3 = fe.load_registry()
    ok3 = ('R31FROZEN_SENTINEL' in r3['by_id']
           and 'R31LOCAL_SENTINEL' not in r3['by_id'])
    # 钉死释放后默认面=最近一次 load 的缓存(既有污染-恢复语义不破坏:
    # 缓存非静默重读本地——调用方须自行恢复,p02_w2 契约原样)
    os.environ.pop('IA_REGISTRY_PIN', None)
    r4 = fe.load_registry()
    ok4 = 'R31FROZEN_SENTINEL' in r4['by_id']
    check('§A5 fact_engine 钉死=冻结副本面;显式路径优先+缓存语义不破坏',
          ok1 and ok2 and ok3 and ok4,
          f'frozen读={ok1} 显式优先={ok2} 污染后回冻结={ok3} '
          f'缓存=末次load={ok4}')
    # 恢复生产注册表缓存(后续节不受哨兵污染)
    fe.load_registry(os.path.join(ROOT, 'config', 'metric_registry.json'),
                     force=True)
    shutil.rmtree(_tmpd, ignore_errors=True)

    # A6 freshness_policy 日历面读冻结副本: 冻结副本独有的决议条目
    # 在 as_of 可见,本地(无该条目)不被消费
    _tmpc = tempfile.mkdtemp(prefix='r31cal_', dir=TMPG)
    _frozen_cal = os.path.join(_tmpc, 'cal.json')
    json.dump({'entries': [
        {'entry_id': 'R31FIX-ONLY-FROZEN', 'kind': 'policy_decision',
         'metric_id': 'JP_POLICY_TARGET', 'basis': 'gate_fixture',
         'first_publish_on_or_after': '2026-01-15',
         'decision_date': '2026-01-15', 'effective_on': '2026-02-28',
         'target_value': 0.5, 'note': '只存在于冻结副本'}]},
        open(_frozen_cal, 'w', encoding='utf-8'))
    os.environ['IA_CALENDAR_PIN'] = _frozen_cal
    st_frozen = fp.policy_decision_state('JP_POLICY_TARGET', '2026-03-01')
    os.environ.pop('IA_CALENDAR_PIN', None)
    st_local = fp.policy_decision_state('JP_POLICY_TARGET', '2026-03-01')
    check('§A6 政策面读冻结副本(冻结独有条目可见,本地不串)',
          st_frozen.get('present') and st_frozen.get('official_target') == 0.5
          and (not st_local.get('present')
               or st_local.get('official_target') != 0.5),
          f"frozen={st_frozen.get('official_target')} "
          f"local={st_local.get('official_target')}")
    shutil.rmtree(_tmpc, ignore_errors=True)


def sec_b():
    """§B 任务1: 研究截止日与回看窗统一(裸年月+单一相对窗)。"""
    import research_orchestrator as ro
    print('═══ §B 任务1: 研究截止日与回看窗统一 ═══')

    # B1 NEW30 形: 裸年月+最近六个月→一个截止日+一个回看窗
    iso, basis = ro._question_asof_declared(Q_NEW30, ())
    spec = ro._question_window(Q_NEW30)
    check('§B1 裸年月+单一相对窗→月末时点+相对窗(NEW30 问句)',
          iso == '2026-11-30' and '裸年月' in basis and '一个截止日+一个回看窗' in basis
          and spec.get('kind') == 'relative_months'
          and spec.get('months') == 6 and spec.get('as_of') == '2026-11-30',
          f"iso={iso} kind={spec.get('kind')} months={spec.get('months')} "
          f"as_of={spec.get('as_of')}")
    # B2 AUG 形: 显式时点标记+最近六个月
    iso2, basis2 = ro._question_asof_declared(Q_AUG, ())
    spec2 = ro._question_window(Q_AUG)
    check('§B2 显式时点标记贯穿(以X为研究时点)',
          iso2 == '2026-08-21' and '显式时点标记' in basis2
          and spec2.get('kind') == 'relative_months'
          and spec2.get('months') == 6 and spec2.get('as_of') == '2026-08-21',
          f"iso={iso2} kind={spec2.get('kind')} as_of={spec2.get('as_of')}")

    # B3 真冲突组合仍拒绝(不合并、不择一)。裸年月+自然年一形: 声明扫描
    # 器不看孤立年份词,但窗口层以区间倒置拒绝→净行为=拒绝(声明时点
    # 不产出报告——计划门在窗解析前阻断);其余五形两层同拒。
    conflicts = [
        ('双裸年月', '2026年11月和2026年10月,日本最近六个月的通胀环境', True),
        ('双时点标记', '以 2026-08-21 为研究时点,又以 2026-09-21 为研究时点,'
                   '日本最近六个月的通胀环境', True),
        ('双相对窗', '2026年11月,日本最近六个月和最近三个月的通胀环境', True),
        ('裸年月+自然年', '2026年11月与2025年日本最近六个月的通胀环境', False),
        ('全日期+相对', '2026-08-21日本最近六个月的通胀环境', True),
        ('显式区间+相对', '2026年1月到2026年6月,日本最近六个月的通胀环境', True),
    ]
    for label, q, want_decl_none in conflicts:
        _iso, _b = ro._question_asof_declared(q, ())
        _sp = ro._question_window(q)
        check(f'§B3 真冲突仍拒: {label}',
              (not want_decl_none or (_iso is None and _b is None))
              and _sp.get('kind') == 'unparseable',
              f"iso={_iso} kind={_sp.get('kind')} "
              f"reason={str(_sp.get('reason'))[:40]}")

    # B4 既有口径零回归: 裸年月单独=显式月窗(R12);相比三个月前=点锚
    # 非相对窗;纯相对窗无 as_of(R10 原样)
    sp_m = ro._question_window('2026年3月美国通胀怎么样')
    check('§B4a 裸年月单独=显式月窗(R12 零回归)',
          sp_m.get('start') == '2026-03-01' and sp_m.get('end') == '2026-03-31'
          and not sp_m.get('as_of'),
          f"start={sp_m.get('start')} end={sp_m.get('end')}")
    sp_p = ro._question_window('2026年11月日本通胀相比三个月前有什么变化?')
    check('§B4b 相比三个月前=点锚短语非相对窗(显式月窗原样)',
          sp_p.get('start') == '2026-11-01' and sp_p.get('end') == '2026-11-30'
          and not sp_p.get('as_of'),
          f"start={sp_p.get('start')} end={sp_p.get('end')}")
    sp_r = ro._question_window('日本最近三个月的通胀环境')
    check('§B4c 纯相对窗无声明时点=快照口径原样(无 as_of)',
          sp_r.get('kind') == 'relative_months' and sp_r.get('months') == 3
          and not sp_r.get('as_of'),
          f"kind={sp_r.get('kind')} months={sp_r.get('months')} "
          f"as_of={sp_r.get('as_of')}")

    # B5 计划级贯穿: 声明时点→cutoff/窗口/点锚(发布可知面: 观测日与
    # 首发日均≤时点——含 10月/11月观测不进入 2026-03-21 历史研究的
    # 直接镜像回归)
    t, v1 = _mk_tree()
    _months = []
    for _y in (2025, 2026):
        for _m in range(1, 13):
            if (_y, _m) <= (2026, 11):
                _months.append('%04d-%02d-01' % (_y, _m))
    _snap = json.load(open(v1, encoding='utf-8'))
    _snap['series_store']['EA_HICP_YOY'] = {
        'dates': _months, 'values': [2.0] * len(_months)}
    json.dump(_snap, open(v1, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    _orig = None

    def _noop_step(name, argv, timeout=180):
        return _fake_step_ok(name, argv, timeout)

    import research_orchestrator as _ro
    _orig = _ro.run_step
    _ro.run_step = _noop_step
    try:
        rep = _ro.run_research(
            '以 2026-03-21 为研究时点,日本和欧元区最近六个月的通胀与政策环境',
            root=t, out_dir=os.path.join(TMPG, 'r31_b5'))
    finally:
        _ro.run_step = _orig
    plan = rep.get('research_plan') or {}
    _ad = plan.get('as_of_declared') or {}
    _wins = ((plan.get('question_window') or {}).get('windows') or [{}])[0]
    check('§B5a 声明时点贯穿计划(cutoff+窗口 2025-09-21..2026-03-21)',
          plan.get('cutoff') == '2026-03-21'
          and _ad.get('as_of') == '2026-03-21'
          and _ad.get('differs_from_snapshot') is True
          and _wins.get('from') == '2025-09-21'
          and _wins.get('to') == '2026-03-21',
          f"cutoff={plan.get('cutoff')} from={_wins.get('from')} "
          f"to={_wins.get('to')}")
    ea = None
    for c in ((plan.get('point_values') or {}).get('cells') or []):
        if c.get('metric_id') == 'EA_HICP_YOY':
            ea = c
            break
    _obs = []
    if ea:
        for _a in (ea.get('anchors') or {}).values():
            _d = _a.get('observation_date')
            if _d:
                _obs.append(_d)
    check('§B5b 点锚观测全≤声明时点(发布可知面)',
          bool(ea) and _obs and all(d <= '2026-03-21' for d in _obs),
          f"obs={_obs}")
    check('§B5c 后来发布不入历史研究(3月观测+10/11月观测均未消费;'
          '最新可见=2026-02)',
          bool(ea) and '2026-03-01' not in _obs and '2026-10-01' not in _obs
          and '2026-11-01' not in _obs
          and ((ea.get('anchors') or {}).get('最新一期') or {})
          .get('observation_date') == '2026-02-01',
          f"latest={((ea.get('anchors') or {}).get('最新一期') or {}).get('observation_date')}")
    shutil.rmtree(t, ignore_errors=True)

    # B6 美债三利率共同日面绑定时点(window.to≤cutoff;无 cutoff=序列
    # 最新,既有口径)
    import research_map_planner as rmp
    _tri = {'series_store': {
        m: {'dates': ['2026-05-29', '2026-06-30', '2026-07-31',
                      '2026-08-29'],
            'values': [4.0, 4.1, 4.2, 4.3]}
        for m in ('UST_10Y', 'TIPS_10Y', 'BEI_10Y')}}
    f_cut = rmp.us_rates_trio_face(_tri, ROOT, cutoff='2026-06-30')
    f_free = rmp.us_rates_trio_face(_tri, ROOT, cutoff=None)
    check('§B6 三利率共同日面绑定时点(to≤cutoff;无 cutoff=序列最新)',
          f_cut.get('status') == 'ok'
          and f_cut['window']['to'] == '2026-06-30'
          and f_free['window']['to'] == '2026-08-29',
          f"cut_to={f_cut.get('window', {}).get('to')} "
          f"free_to={f_free.get('window', {}).get('to')}")


def sec_c():
    """§C 任务3: 关键证据校验(m12 严格同月/决议-生效成对/当前目标缺证)。"""
    import agent_judgment as aj
    import fact_engine as fe
    import research_map_planner as rmp
    import economy_comparison_view as ecv
    print('═══ §C 任务3: 关键证据校验 ═══')

    # C1 m12=同比基期严格去年同月(13 个月前≠同比;月末戳月频仍=同月)
    def _cpr(dates):
        return fe.compute_period_returns(dates, [2.0] * len(dates),
                                         'index', 'us')

    s1 = _cpr(['2025-03-14', '2026-02-27', '2026-03-21'])['m12']
    check('§C1a 同月观测在场→同比基期=去年同月(≤锚日最后观测)',
          s1.get('basis_date') == '2025-03-14'
          and '去年同月2025-03' in s1.get('window', ''),
          f"basis={s1.get('basis_date')} win={s1.get('window', '')[:50]}")
    s2 = _cpr(['2025-02-27', '2026-03-21'])['m12']
    check('§C1b 去年同月无观测(13 个月前)→缺基期如实标注',
          s2.get('available') is False
          and '缺基期' in s2.get('reason', '')
          and '2025-03' in s2.get('reason', '')
          and '最近可得基期=2025-02' in s2.get('reason', ''),
          f"reason={s2.get('reason', '')[:60]}")
    s3 = _cpr(['2025-03-31', '2026-03-15'])['m12']
    check('§C1c 月末戳月频(该月晚于锚日观测)仍=去年同月基期',
          s3.get('basis_date') == '2025-03-31'
          and '晚于锚日' in s3.get('window', ''),
          f"basis={s3.get('basis_date')} win={s3.get('window', '')[:60]}")
    s4 = _cpr(['2025-02-27', '2026-03-21'])['m3']
    check('§C1d m1/m3/m6 宽松口径零回归(缺三月仍取最近可得)',
          s4.get('basis_date') == '2025-02-27',
          f"basis={s4.get('basis_date')}")

    # C2 POL-EFF: 决议日-生效日成对(次月末生效不得写成当时已发生)
    pev = [{'entry_id': 'R31C2', 'kind': 'policy_decision',
            'metric_id': 'JP_POLICY_RATE', 'basis': 'gate_fixture',
            'decision_date': '2026-04-28', 'effective_on': '2026-05-31'}]

    def _pol_eff(text):
        j = {'l3': {'conclusions': [{'text': text}]}, 'l4': {},
             'reader_map': {}}
        r = aj.validate_judgment(j, set(), set(), policy_events=pev)
        return [x for x in r['violations'] if x['code'] == 'POL-EFF']

    cases = [
        ('决议日单独在场(CN 形)', '4月28日决议后政策利率维持', True),
        ('决议日+待生效标注', '4月28日决议加息,待生效(5月31日生效)', False),
        ('决议日+生效日成对', '4月28日决议,5月31日生效,利率升至0.5%', False),
        ('决议日 ISO 形单独', '决议 on 2026-04-28 维持利率', True),
        ('决议日斜杠形单独', '2026/4/28 决议降息', True),
        ('无政策词日期', 'GDP 数据 on 2026-04-28 公布', False),
        ('政策词无日期', '政策利率目标维持不变', False),
    ]
    for label, text, want_bad in cases:
        got = _pol_eff(text)
        check(f'§C2 {label}', bool(got) == want_bad,
              f"violations={len(got)}")
    check('§C2b policy_events 缺席=规则关闭(既有调用方零回归)',
          not _pol_eff_off(pev))

    # C3 问句点名当前官方目标而仅有待生效公告→当前值缺证标注
    _tmpc = tempfile.mkdtemp(prefix='r31c3_', dir=TMPG)
    _cal = os.path.join(_tmpc, 'cal.json')
    json.dump({'entries': [
        {'entry_id': 'R31C3-JP', 'kind': 'policy_decision',
         'metric_id': 'JP_POLICY_TARGET', 'basis': 'gate_fixture',
         'first_publish_on_or_after': '2026-01-15',
         'decision_date': '2026-01-15', 'effective_on': '2026-02-28',
         'target_value': 0.5, 'note': 'R31 门夹具'}]},
        open(_cal, 'w', encoding='utf-8'))
    pv = {'cells': [{'region': 'JP', 'dimension': 'policy',
                     'anchors': {'最新一期': {'status': 'ok'}}}]}
    q_ask = '日本央行当前官方目标利率是多少'
    face = rmp.official_policy_record_face(
        pv, [('JP', 'policy')], '2026-02-10', question=q_ask,
        calendar_path=_cal)
    row = (face.get('rows') or [{}])[0]
    check('§C3a 仅有待生效公告→当前官方目标缺证明标',
          row.get('current_target_missing_evidence') is True
          and row.get('official_target') is None
          and row.get('pending_target') == 0.5
          and '待生效' in row.get('current_target_missing_note', ''),
          f"missing={row.get('current_target_missing_evidence')} "
          f"pending={row.get('pending_target')}")
    face_env = rmp.official_policy_record_face(
        pv, [('JP', 'policy')], '2026-02-10',
        question='日本货币政策环境怎么样', calendar_path=_cal)
    row_env = (face_env.get('rows') or [{}])[0]
    check('§C3b 未点名官方目标(只问环境)→不触发缺证标注(R28 口径原样)',
          'current_target_missing_evidence' not in row_env,
          f"keys={sorted(k for k in row_env if 'missing' in k)}")
    face_eff = rmp.official_policy_record_face(
        pv, [('JP', 'policy')], '2026-03-01', question=q_ask,
        calendar_path=_cal)
    row_eff = (face_eff.get('rows') or [{}])[0]
    check('§C3c 生效日后→官方目标在场(待生效值升格,不缺证)',
          row_eff.get('official_target') == 0.5
          and 'current_target_missing_evidence' not in row_eff,
          f"target={row_eff.get('official_target')}")
    import inspect
    check('§C3d 渲染面缺证文案在场(缺证(仅有待生效公告))',
          '缺证(仅有待生效公告)' in inspect.getsource(rmp.render_map_report))
    shutil.rmtree(_tmpc, ignore_errors=True)

    # C4 关键事实行缺基期原因透传(不以笼统「无派生」掩盖;derived 分支
    # =US/CPI 指数级,EA 走 value 分支)
    _c4_reason = ('缺基期: 去年同月(2025-03)无观测,最近可得基期=2025-02'
                  '——同比基期须同月')
    facts = [{'metric_id': 'CPI', 'observation_date': '2026-03-01',
              'derived': {'m12': {'available': False,
                                  'reason': _c4_reason}}}]
    kf = ecv.key_fact(facts, 'US')
    check('§C4 m12 缺基期原因如实透传(economy_comparison key_fact)',
          kf['inflation_yoy']['available'] is False
          and kf['inflation_yoy']['absence_reason'] == _c4_reason,
          f"reason={str(kf['inflation_yoy']['absence_reason'])[:60]}")


def _pol_eff_off(pev):
    """policy_events=None(缺省)时 POL-EFF 规则关闭的探针。"""
    import agent_judgment as aj
    j = {'l3': {'conclusions': [{'text': '4月28日决议后政策利率维持'}]},
         'l4': {}, 'reader_map': {}}
    r = aj.validate_judgment(j, set(), set(), policy_events=None)
    return [x for x in r['violations'] if x['code'] == 'POL-EFF']


def main():
    os.makedirs(TMPG, exist_ok=True)
    sec_a()
    sec_b()
    sec_c()
    n, ok = len(RESULTS), sum(RESULTS)
    print(f'\n=== R31 门: {ok}/{n} ===')
    sys.exit(1 if (n - ok) else 0)


if __name__ == '__main__':
    main()
