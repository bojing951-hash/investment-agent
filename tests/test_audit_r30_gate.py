#!/usr/bin/env python3
"""Audit-R30 门 — 快照钉死/时点口径/自然问窗三修+真历史回归。

任务1 输入钉死: 第一次取数前固定快照(IA_SNAPSHOT_PIN 运行级 seam,
计划/子命令/L1/渲染/裁决/归档同一份)+同日 _v2 中途落盘不串号(旧工单
  全程原版/新工单选新版)+钉死文件移除 fail-closed+raw CSV 注入口
  alerts 初始化(在线 GDP 重试保留)。
任务2 时点: BOJ 2026-09-20 旧目标可核实+新目标 1.25 待生效(09-24
  切换/10-30 维持只刷确认/距上次调整恒≥0);次月末生效窗内旧值在位;
  LPR 2025-11-20 与 2026-11-20 官方日期+09:00 双期在档;2022-03 锚
  **真实历史**回归(两端各按自己的可知截止,发布纪律不泄漏)+同比缺
  基期=缺证+同期重复观测注明无新增观测。
任务3 自然问窗: 「美、欧、中、日过去三个月的增长、通胀和政策哪里
  分化」=12 组计划(含政策维)+问句时间窗落实(窗起锚+当期锚+
  question_window 披露+数据需求窗同源);OPEN2/NEW2 回归不变。
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
import research_map_planner as rmp           # noqa: E402
import research_orchestrator as ro           # noqa: E402
import workbench_data as wd                  # noqa: E402

TMPG = tempfile.mkdtemp(prefix='r30gate_')
RESULTS = []
FIXT = os.path.join(HERE, 'fixtures_r30', 'real_history_2022_anchor.json')

Q_T3 = '美、欧、中、日过去三个月的增长、通胀和政策哪里分化'
Q_OPEN2 = ('2026年11月,美、欧、中、日四地的宏观环境相比三个月前,哪些'
           '经济体之间出现了明显分化?分化主要体现在哪些维度?请给出具体'
           '数据和各数据的公布时间,并说明哪些维度证据不足以下结论。')
Q_NEW2 = ('2026年11月,美、日两地的宏观基本面相比三个月前有什么不同?'
          '哪些方面分化最明显,哪些方面证据还不足?请附数据与公布时间。')


def check(name, ok, detail=''):
    ok = bool(ok)
    RESULTS.append(ok)
    print(('  ✅ ' if ok else '  ❌ ') + name +
          (' — ' + str(detail) if detail else ''))
    return ok


def _mk_tree():
    """迷你树: research_snapshot_20261121.json(V1 印记)。

    snapshot_id 须与文件名一致(research_provenance 身份校验)。"""
    t = tempfile.mkdtemp(prefix='r30pin_', dir=TMPG)
    os.makedirs(os.path.join(t, 'data', 'daily'))
    v1 = os.path.join(t, 'data', 'daily', 'research_snapshot_20261121.json')
    json.dump({'snapshot_id': 'research_snapshot_20261121',
               'target_date': '20261121',
               'facts': [], 'series_store': {}, 'r30_mark': 'V1'},
              open(v1, 'w', encoding='utf-8'))
    return t, v1


def _drop_v2(t):
    v2 = os.path.join(t, 'data', 'daily', 'research_snapshot_20261121_v2.json')
    json.dump({'snapshot_id': 'research_snapshot_20261121_v2',
               'target_date': '20261121',
               'facts': [], 'series_store': {}, 'r30_mark': 'V2'},
              open(v2, 'w', encoding='utf-8'))
    return v2


def sec_a():
    print('═══ §A 任务1: 快照钉死+_v2 不串号+raw 注入 alerts ═══')
    import ea_market_collector as ea
    # A1 raw CSV 注入: alerts 已初始化(R29 只测在线路径,注入路径实雷)
    yoy, alerts = ea.fetch_ea_real_gdp_yoy(raw=(
        b'observation_date,CLVMEURSCAB1GQEA19\n'
        b'2025-01-01,1.0\n2025-04-01,1.2\n2025-07-01,1.3\n'
        b'2026-01-01,1.1\n2026-04-01,1.3\n2026-07-01,1.25\n'))
    check('§A1 raw 注入零 UnboundLocalError: yoy 三季+alerts 列表在位',
          isinstance(yoy, list) and len(yoy) == 3
          and isinstance(alerts, list), f'yoy={yoy} alerts={alerts}')
    y2, a2 = ea.fetch_ea_real_gdp_yoy(raw=b'DATE,WRONG\nx,y')
    check('§A1b raw 注入形态不符: (None, 告警)如实在,不抛异常',
          y2 is None and bool(a2), f'y={y2} a={a2}')

    # A2/A3/A4/A5 钉死 seam
    t, v1 = _mk_tree()
    s1, n1 = wd.latest_snapshot(t)
    os.environ['IA_SNAPSHOT_PIN'] = n1      # orchestrator 入口同型置位
    v2 = _drop_v2(t)                        # S3 期间同日 _v2 落盘
    s2, n2 = wd.latest_snapshot(t)
    check('§A2 旧工单全程原版: 钉死后同日 _v2 落盘,再解析仍=原版',
          n2 == v1 and s2.get('r30_mark') == 'V1',
          f'n2={n2}')
    # A3 新工单=新进程新解析(无钉死)→修订版感知选 _v2
    env_code = ('import sys, json; sys.path.insert(0, %r); '
                'import workbench_data as wd; '
                's, n = wd.latest_snapshot(%r); '
                'print(json.dumps({"sid": (s or {}).get("r30_mark"), '
                '"path": n}))' % (os.path.join(ROOT, 'scripts'), t))
    env_nopin = {k: v for k, v in os.environ.items()
                 if k != 'IA_SNAPSHOT_PIN'}
    p3 = subprocess.run([sys.executable, '-c', env_code],
                        capture_output=True, text=True, timeout=60,
                        env=env_nopin)
    r3 = json.loads(p3.stdout.strip().splitlines()[-1])
    check('§A3 新工单能选新版: 无钉死的新解析选 _v2(revision 感知)',
          r3['sid'] == 'V2' and r3['path'].endswith('_v2.json'),
          f"r3={r3['path']}")
    # A5 子进程 env 继承(run_step 子命令 seam 同型)
    p5 = subprocess.run([sys.executable, '-c', env_code],
                        capture_output=True, text=True, timeout=60,
                        env=dict(os.environ))
    r5 = json.loads(p5.stdout.strip().splitlines()[-1])
    check('§A5 子命令子进程继承钉死: env 携带→子进程读原版',
          r5['sid'] == 'V1' and r5['path'] == v1, f"r5={r5['path']}")
    # A4 fail-closed: 钉死文件被移除→拒绝静默回退
    os.remove(v1)
    s4, n4 = wd.latest_snapshot(t)
    check('§A4 钉死文件移除=fail-closed: 拒绝静默回退文件系统解析',
          s4 is None and '拒绝静默回退' in str(n4), f'n4={n4}')
    os.environ.pop('IA_SNAPSHOT_PIN', None)
    shutil.rmtree(t, ignore_errors=True)

    # A6 运行级钉死+收尾恢复: run_research 入口置位、S3 期间 _v2 落盘、
    # 尾步仍原版、函数返回后环境复原(monkeypatch run_step 零真子进程)
    t6, v1b = _mk_tree()
    shutil.copytree(os.path.join(ROOT, 'config'),
                    os.path.join(t6, 'config'))
    seen_pins, dropped = [], [False]

    def _fake_step(name, argv, timeout=180):
        seen_pins.append(os.environ.get('IA_SNAPSHOT_PIN'))
        if name.startswith('S3') and not dropped[0]:
            dropped[0] = True
            _drop_v2(t6)               # S3 期间发布同日 _v2
        return {'step': name, 'argv': list(argv), 'executed': True,
                'ok': True, 'exit_code': 0, 'semantic_ok': True,
                'note': None, 'duration_ms': 1, 'envelope': {'ok': True}}

    _orig = ro.run_step
    ro.run_step = _fake_step
    try:
        rep = ro.run_research('美国、欧元区、中国、日本四地增长与通胀的'
                              '最新地图对照', root=t6,
                              out_dir=os.path.join(TMPG, 'r30_rr'))
    finally:
        ro.run_step = _orig
    check('§A6 旧工单运行级钉死: 首步已置位且=原版,S3 落 _v2 后尾步'
          '仍原版,返回后环境复原',
          seen_pins and all(p == v1b for p in seen_pins)
          and dropped[0]
          and os.environ.get('IA_SNAPSHOT_PIN') is None,
          f'n_steps={len(seen_pins)} all_v1={all(p == v1b for p in seen_pins)}')
    shutil.rmtree(t6, ignore_errors=True)


def sec_b():
    print('═══ §B 任务2: as-of 政策面+次月末+LPR+2022-03 真实历史 ═══')
    # B1 生产日历时间线(BOJ)
    for d, tgt, pend, dadj, mnt in (
        ('2026-09-19', None, 1.25, None, None),
        ('2026-09-20', None, 1.25, None, None),
        ('2026-09-23', None, 1.25, None, None),
        ('2026-09-24', 1.25, None, 0, None),
        ('2026-10-30', 1.25, None, 36, '2026-10-30'),
        ('2026-11-21', 1.25, None, 58, '2026-10-30'),
    ):
        st = fp.policy_decision_state('JP_POLICY_TARGET', d)
        ok = (st.get('official_target') == tgt
              and st.get('pending_target') == pend
              and st.get('days_since_adjustment') == dadj
              and st.get('last_maintenance') == mnt)
        if not check(f'§B1 BOJ @{d}: 目标={tgt} 待生效={pend}@'
                     f'09-24 距调整={dadj} 维持={mnt}',
                     ok, json.dumps({k: st.get(k) for k in (
                         'official_target', 'pending_target',
                         'pending_effective_on', 'days_since_adjustment',
                         'last_maintenance')}, ensure_ascii=False)):
            break
    # B1b 距上次调整恒≥0(09-01..11-21 逐日)
    import datetime as _dt
    d0, bad = _dt.date(2026, 9, 1), []
    while d0 <= _dt.date(2026, 11, 21):
        st = fp.policy_decision_state('JP_POLICY_TARGET', d0.isoformat())
        v = st.get('days_since_adjustment')
        if v is not None and v < 0:
            bad.append((d0.isoformat(), v))
        d0 += _dt.timedelta(days=1)
    check('§B1b days_since_adjustment 恒≥0(82 日逐日,负数面消除)',
          not bad, f'bad={bad[:3]}')

    # B2 夹具日历: 前决议(2026-01-15 决/2026-02-28 次月末生效/0.75)
    # +09 决议(09-18/09-24/1.25)+10-30 维持→09-20 旧目标可核实
    cal = {'entries': [
        {'entry_id': 'R30FIX-PRIOR', 'kind': 'policy_decision',
         'metric_id': 'JP_POLICY_TARGET', 'basis': 'gate_fixture',
         'first_publish_on_or_after': '2026-01-15',
         'decision_date': '2026-01-15', 'effective_on': '2026-02-28',
         'target_value': 0.75, 'note': '门夹具: 前决议(次月末生效)'},
        {'entry_id': 'RC-JP-BOJ-TARGET-2026-09', 'kind': 'policy_decision',
         'metric_id': 'JP_POLICY_TARGET', 'basis': 'gate_fixture',
         'first_publish_on_or_after': '2026-09-18',
         'decision_date': '2026-09-18', 'effective_on': '2026-09-24',
         'target_value': 1.25, 'note': '门夹具: 09 决议'},
        {'entry_id': 'RC-JP-BOJ-MAINT-2026-10', 'kind': 'policy_maintenance',
         'metric_id': 'JP_POLICY_TARGET', 'basis': 'gate_fixture',
         'first_publish_on_or_after': '2026-10-30',
         'decision_date': '2026-10-30', 'effective_on': '2026-10-30',
         'note': '门夹具: 维持'}]}
    cpath = os.path.join(TMPG, 'r30_fix_cal.json')
    json.dump(cal, open(cpath, 'w', encoding='utf-8'), ensure_ascii=False)
    st20 = fp.policy_decision_state('JP_POLICY_TARGET', '2026-09-20',
                                    calendar_path=cpath)
    check('§B2 BOJ@2026-09-20 旧目标可核实+新目标待生效: 官方目标=0.75'
          '(前决议已生效)/pending 1.25@2026-09-24',
          st20.get('official_target') == 0.75
          and st20.get('pending_target') == 1.25
          and st20.get('pending_effective_on') == '2026-09-24'
          and st20.get('days_since_adjustment') == 204,
          json.dumps({k: st20.get(k) for k in (
              'official_target', 'pending_target', 'pending_effective_on',
              'days_since_adjustment')}, ensure_ascii=False))
    # B2b 次月末生效窗内: 01-15 决/02-28 生效,02-10 仍无生效决议+
    # 0.75 待生效(旧值在位面——夹具无更早决议=如实空缺不虚构)
    stfeb = fp.policy_decision_state('JP_POLICY_TARGET', '2026-02-10',
                                     calendar_path=cpath)
    check('§B2b 次月末生效窗内(01-15 决/02-28 效,@02-10): 无已生效新'
          '决议+0.75 待生效(不提前切换)',
          stfeb.get('official_target') is None
          and stfeb.get('pending_target') == 0.75
          and stfeb.get('pending_effective_on') == '2026-02-28',
          str(stfeb.get('pending_target')))
    stfeb28 = fp.policy_decision_state('JP_POLICY_TARGET', '2026-02-28',
                                       calendar_path=cpath)
    check('§B2c 次月末生效日切换: @02-28 目标=0.75/距调整=0',
          stfeb28.get('official_target') == 0.75
          and stfeb28.get('days_since_adjustment') == 0)

    # B3 LPR 双期官方日期+09:00(日历在档+时刻统一)
    prod = json.load(open(os.path.join(ROOT, 'config',
                                       'release_calendar.json'),
                          encoding='utf-8'))
    lpr = {e.get('entry_id'): e for e in prod['entries']
           if e.get('metric_id') == 'CN_LPR_1Y'}
    check('§B3 LPR 2025-11-20 与 2026-11-20 双期在档且 time=09:00',
          lpr.get('RC-CN-LPR-2025M11', {}).get(
              'first_publish_on_or_after') == '2025-11-20'
          and lpr.get('RC-CN-LPR-2025M11', {}).get('time') == '09:00'
          and lpr.get('RC-CN-LPR-2026M11', {}).get(
              'first_publish_on_or_after') == '2026-11-20'
          and lpr.get('RC-CN-LPR-2026M11', {}).get('time') == '09:00',
          f"ids={sorted(lpr)}")

    # B4 2022-03 锚: 真实历史(fixtures_r30,提取自真实采集快照)
    fx = json.load(open(FIXT, encoding='utf-8'))
    prov = fx.get('_provenance') or {}
    check('§B4 夹具出处: 真实采集快照只读提取(非合成),provenance 在档',
          'research_snapshot' in str(prov.get('source'))
          and '真实观测' in str(prov.get('note')))
    s_cn = fx['CN_CPI_YOY']
    # 截止端 2022-03(own cutoff 03-31): 3 月观测 04-09 才发布→只见 2 月
    r1, why1 = rmp._hist_region_reading(
        s_cn, '2022-03', '2022-03-31', 'CN_CPI_YOY', 'direct', 'monthly')
    check('§B4a 2022-03 锚截止端(真实值): 只见 2022-02 观测(0.9),'
          '3 月观测 04-09 发布不泄漏',
          r1 is not None and r1[1] == '2022-02-01' and r1[0] == 0.9,
          f'r1={r1} why={why1}')
    # 锚−3月端 2021-12(own cutoff 12-31): 12 月观测 22-01-09 发布→
    # 只见 11 月 2.3;旧口径(共用判断截止)会给 12 月 1.5=后视
    r0, why0 = rmp._hist_region_reading(
        s_cn, '2021-12', '2021-12-31', 'CN_CPI_YOY', 'direct', 'monthly')
    check('§B4b 锚−3月端按自己的可知截止(真实值): 只见 2021-11 观测'
          '(2.3)——共用判断截止的旧口径会给 2021-12(1.5)=发布面后视',
          r0 is not None and r0[1] == '2021-11-01' and r0[0] == 2.3
          and r0[0] != 1.5,
          f'r0={r0} why={why0}')
    # 同步面端到端: 判断截止 2022-03 → prior 端=2021-11(2.3) 非 1.5
    # (rj=report.json 形态,序列住 S4_history_<mid> 步信封)
    rj = {'steps': [
        {'step': 'S4_history_CN_CPI_YOY',
         'envelope': {'data': {'series': dict(s_cn)}}}]}
    face = rmp.history_region_sync_face(
        [{'anchor_ym': '2022-03', 'judgment_cutoff_ym': '2022-03'}], rj)
    row = next((r for r in face.get('periods', [{}])[0].get('rows', [])
                if r.get('metric_id') == 'CN_CPI_YOY'), {})
    check('§B4c 同步面两端各按可知截止(真实值): prior=2021-11(2.3)'
          '/cutoff=2022-02(0.9),不并轨',
          row.get('prior_obs') == '2021-11-01'
          and row.get('prior_value') == 2.3
          and row.get('cutoff_obs') == '2022-02-01'
          and row.get('cutoff_value') == 0.9,
          f"row={ {k: row.get(k) for k in ('prior_obs', 'prior_value', 'cutoff_obs', 'cutoff_value')} }")
    # B5 同比缺基期(真实 CPI 水平序列,夹具起 2021-06): 2021-07 读数
    # 基期 2020-07 不在场→缺证
    s_us = fx['CPI']
    r5, why5 = rmp._hist_region_reading(
        s_us, '2021-07', '2021-07-31', 'CPI', 'level_yoy', 'monthly')
    check('§B5 真实水平序列同比缺基期=缺证(2020-07 基期不在场→'
          'no_visible_base,不编同比)',
          r5 is None and why5 == 'no_visible_base', f'why={why5}')

    # B6 同一期重复观测注明无新增观测(点值面,稀疏序列双锚同观测)
    plan = {'regions': {'CN': {'dimensions': {'inflation': [
        {'metric_id': 'CN_CPI_YOY', 'display_name': '中国CPI同比',
         'frequency': 'monthly', 'unit': 'percent'}]}}},
        'dimensions': ['inflation'], 'metrics': ['CN_CPI_YOY'],
        'context_metrics': [], 'cutoff': '2026-11-21',
        'point_anchors': [
            {'kind': 'point', 'label': '6个月前', 'as_of': '2026-05-21',
             'months_before': 6},
            {'kind': 'point', 'label': '3个月前', 'as_of': '2026-08-21',
             'months_before': 3}]}
    snap = {'series_store': {'CN_CPI_YOY': {
        'dates': ['2025-11-01', '2026-11-01'], 'values': [0.3, 0.2],
        'frequency': 'monthly', 'unit': 'percent'}}}
    pv = rmp.point_values(plan, snap, ROOT)
    row6 = (pv.get('cells') or [{}])[0]
    a6 = row6.get('anchors') or {}
    check('§B6 同一期重复观测注明: 双锚同落 2025-11 观测→逐锚注明'
          '"无新增观测"(同一读数不当两时点独立证据)',
          a6.get('6个月前', {}).get('observation_date') == '2025-11-01'
          and a6.get('3个月前', {}).get('observation_date') == '2025-11-01'
          and '无新增观测' in str(
              a6.get('6个月前', {}).get('duplicate_observation_note'))
          and '3个月前' in str(
              a6.get('6个月前', {}).get('duplicate_observation_note')),
          str(a6.get('6个月前', {}).get('duplicate_observation_note')))


def sec_c():
    print('═══ §C 任务3: 自然问窗(12 组+政策维+时间窗落实) ═══')
    import workbench_data as _wd
    reg = _wd.load_registry(ROOT)
    ent = {'economies': ['US', 'EA', 'CN', 'JP'], 'metrics': [],
           'note': None}
    check('§C1 T3 问句判地图问句(分化形+三维+四地)',
          rmp.detect_map_question(Q_T3, ent))
    plan = rmp.plan_map(Q_T3, ent, reg.get('by_id') or {}, '2026-11-21')
    pairs = sorted({(e, d) for e, r in plan['regions'].items()
                    for d in r['dimensions']})
    check('§C2 12 组计划含政策维(4 地区×3 维)',
          len(pairs) == 12 and ('CN', 'policy') in pairs
          and ('JP', 'policy') in pairs, f'n={len(pairs)}')
    check('§C3 dimension_source=explicit_words(显式点名三维)',
          plan.get('dimension_source') == 'explicit_words')
    anchors = plan.get('point_anchors') or []
    check('§C4 时间窗落实: 窗起锚(3个月前,window_start)+当期锚',
          [a['label'] for a in anchors] == ['3个月前', '最新一期']
          and '问句时间窗窗起' in str(
              (anchors[0] if anchors else {}).get('window_start')),
          str(anchors))
    qw = plan.get('question_window') or {}
    w0 = (qw.get('windows') or [{}])[0]
    check('§C5 question_window 披露: months=3/from=2026-08-21/'
          'to=2026-11-21/词形在档',
          w0.get('months') == 3 and w0.get('from') == '2026-08-21'
          and w0.get('to') == '2026-11-21'
          and w0.get('source') == '过去三个月', str(qw))
    check('§C6 数据需求窗同源: _question_window=relative_months 3'
          '(窗不被当点语义消费)',
          (ro._question_window(Q_T3) or {}).get(
              'months') == 3 and rmp.consumed_time_spans(Q_T3) == [])
    # C7 变体+负例
    for q, m in (('近六个月的通胀与增长分化', 6),
                 ('最近12个月政策与通胀怎么样', 12),
                 ('过去 3 个月增长如何', 3)):
        wins = rmp.parse_question_windows(q, '2026-11-21')
        check(f'§C7 窗变体「{q}」→months={m}',
              len(wins) == 1 and wins[0]['months'] == m, str(wins))
    check('§C7b 负例: 「最近有什么变化」无数量不成窗;「过去半年」'
          '非数字词形不虚构',
          rmp.parse_question_windows('最近有什么变化', '2026-11-21') == []
          and rmp.parse_question_windows('过去半年的增长', '2026-11-21') == [])
    # C8 双窗+点锚并存: 窗起标记只落窗月
    a8 = rmp.parse_point_anchors('过去三个月与十二个月前的增长对照',
                                 '2026-11-21')
    check('§C8 窗起与显式点锚并存: months={3,12},window_start 只标'
          '窗起(3个月前)',
          sorted(a['months_before'] for a in a8) == [0, 3, 12]
          and sum(1 for a in a8 if a.get('window_start')) == 1,
          str(a8))
    # C9 OPEN2/NEW2 回归(判形/组数/隐含来源/锚行为不变——R29 基线:
    # 两问句均含「相比三个月前」→锚=[3个月前,最新一期],无窗词形)
    for tag, q, ecos, n in (('OPEN2', Q_OPEN2, ['US', 'EA', 'CN', 'JP'], 12),
                            ('NEW2', Q_NEW2, ['US', 'JP'], 6)):
        ent2 = {'economies': ecos, 'metrics': [], 'note': None}
        det = rmp.detect_map_question(q, ent2)
        pl = rmp.plan_map(q, ent2, reg.get('by_id') or {}, '2026-11-21')
        prs = {(e, d) for e, r in pl['regions'].items()
               for d in r['dimensions']}
        anc = pl.get('point_anchors') or []
        check(f'§C9 {tag} 回归不变: 判形={det}/组数={n}/隐含来源/'
              '锚=R29 基线(相比三个月前)/零窗面',
              det is True and len(prs) == n
              and pl.get('dimension_source', '').startswith(
                  'implicit_macro_environment')
              and [a.get('label') for a in anc] == ['3个月前', '最新一期']
              and not any(a.get('window_start') for a in anc)
              and pl.get('question_window') is None,
              f'n={len(prs)} anchors={[a.get("label") for a in anc]}')


def main():
    print('Audit-R30 门: 快照钉死/时点/自然问窗\n')
    try:
        sec_a()
        sec_b()
        sec_c()
    finally:
        n_ok, n_bad = sum(RESULTS), len(RESULTS) - sum(RESULTS)
        print('\n' + '═' * 60)
        print(f'Audit-R30 门: {n_ok} PASS / {n_bad} FAIL (共 {len(RESULTS)} 判据)')
        shutil.rmtree(TMPG, ignore_errors=True)
    sys.exit(1 if (len(RESULTS) - sum(RESULTS)) else 0)


if __name__ == '__main__':
    main()
