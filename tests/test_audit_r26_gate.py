#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit-R26(R70)门 — 正式使用验收前置: 四任务核心面回归。

任务1 §A: 同日采集守卫强化——按指标身份与有效观测判降级(删CPI加新指标
非子集不再漏判/CPI全null观测蒸发/正常数值修订放行)+先写完整并校验候选
再原子替换(候选不符fail-loud规范档不动)+旧档副本保全(任意中断点规范档
始终完整可读)+同日并发互斥(per-file flock,读者任意时刻见完整档)。
任务2 §B: 三日期分离——月/季频窗口自统计期末起算(美欧日Q3 GDP正例/
EA HICP 停 2025-12 反例)+决策驱动政策序列按政策最后确认纪律(无更晚
已证实决议不过期/有之则STALE)+必要维度只剩确证过期值→草稿交付
(map_core_dimension_stale,正式归档拒)+逐组覆盖与实际数据来源表。
任务3 §C: 历史章节当时可知纪律——JP_POLICY_RATE 月均移出政策事件面+
JP_POLICY_TARGET 宣布值入面+BoJ 决议/生效分记只认实录表(2024-03-19
决议/03-21 生效回归;表外生效日=决议日不可推不虚构)。
任务4 §D: 原问逐字纪律——会话首轮第一动作落盘独立原问文件+--question-file
字节直读+计划收 question_verbatim 新原文(第二问验证面)+草稿四类
blocked_class 入口在场。
"""
import json
import multiprocessing as _mp
import os
import subprocess
import sys
import tempfile
import unittest.mock as _mock

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
sys.path.insert(0, os.path.join(ROOT, 'scripts', 'research_contract'))

import research_provenance as rp          # noqa: E402
import research_map_planner as rmp        # noqa: E402
import freshness_policy as fp             # noqa: E402
import agent_judgment as aj               # noqa: E402

RESULTS = []
TMPG = tempfile.mkdtemp(prefix='r26gate_')


def check(name, ok, detail=''):
    RESULTS.append((name, bool(ok), str(detail)[:220]))
    print(('  ✅ ' if ok else ' ❌ ') + name
          + (f' — {detail}' if detail else ''), flush=True)


# ═══ §A 任务1: 指标身份/有效观测/原子替换/副本保全/并发互斥 ═══════════
def sec_a():
    print('═══ §A 采集守卫强化: 身份+有效观测+原子+中断+并发 ═══')
    d = os.path.join(TMPG, 'daily_a')
    full = {'date': '20261120',
            'data': {'CPI': {'dates': ['2026-10-01', '2026-11-01'],
                             'values': [310.0, 310.5]},
                     'PCE': {'dates': ['2026-11-01'],
                             'values': [118.5]}}}
    p1, s1, _ = rp.daily_face_guard_write(d, 'macro', '20261120', full)
    check('§A1 首采直写(first)', s1 == 'first'
          and os.path.basename(p1) == 'macro_20261120.json')
    # 身份判定单元: 前两段=指标身份容器;null 叶计身份计 0 观测
    check('§A2 身份图单元: 前两段身份+null叶计0+空容器不计',
          rp._identity_of('.data.CPI.series.values[]') == ('data', 'CPI')
          and rp.daily_face_identity_map({'data': {'CPI': {'v': [None]}}})
          == {('data', 'CPI'): 0}
          and rp.daily_face_identity_map({'data': {'CPI': {}}}) == {})
    # 删掉 CPI、添加别的指标(非路径子集,旧R25判据漏判)
    swap = {'date': '20261120',
            'data': {'PCE': full['data']['PCE'],
                     'PPI': {'dates': ['2026-11-01'],
                             'values': [140.0]}}}
    p2, s2, n2 = rp.daily_face_guard_write(d, 'macro', '20261120', swap)
    canon = json.load(open(os.path.join(d, 'macro_20261120.json'),
                           encoding='utf-8'))
    check('§A3 删CPI+加新指标→degraded_diverted(身份丢失不因新增补足)',
          s2 == 'degraded_diverted' and '丢失' in n2 and 'data.CPI' in n2
          and 'CPI' in canon['data'] and 'PPI' not in canon['data'],
          f'note={n2}')
    check('§A4 降级版本完整保留在 superseded/', '/superseded/' in
          p2.replace('\\', '/')
          and json.load(open(p2, encoding='utf-8')) == swap)
    # CPI 全改为 null(身份在场,有效观测蒸发)
    nulls = json.loads(json.dumps(full))
    nulls['data']['CPI']['values'] = [None, None]
    p3, s3, n3 = rp.daily_face_guard_write(d, 'macro', '20261120', nulls)
    canon3 = json.load(open(os.path.join(d, 'macro_20261120.json'),
                            encoding='utf-8'))
    check('§A5 CPI全null→degraded_diverted(观测蒸发≠结构变化,null≠有效观测)',
          s3 == 'degraded_diverted' and '叶子' in n3 and 'null≠有效观测' in n3
          and canon3['data']['CPI']['values'] == [310.0, 310.5],
          f'note={n3}')
    # 采集状态/披露区不参与降级判定(carry_forward 键数天然异于fresh;
    # 观测序列逐位不变→放行——实测雷: cn_history 5叶→3叶曾误转存)
    cf = json.loads(json.dumps(full))
    cf['cn_history'] = {'CPI': {'mode': 'carry_forward',
                                'carry_forward_from': 'macro_20261119.json',
                                'carry_forward_reason': '本轮失败续存(披露)'}}
    _, s_cf, n_cf = rp.daily_face_guard_write(d, 'macro', '20261120', cf)
    check('§A5b 披露区键数变化+观测不变→放行(carry_forward续存不误判降级)',
          s_cf == 'overwritten_preserved' and n_cf == '',
          f'status={s_cf} note={n_cf}')
    # 正常数值修订放行(检测重算不是覆盖退化)
    rev = json.loads(json.dumps(full))
    rev['data']['CPI']['values'][-1] = 311.0
    _, s4, _ = rp.daily_face_guard_write(d, 'macro', '20261120', rev)
    canon4 = json.load(open(os.path.join(d, 'macro_20261120.json'),
                            encoding='utf-8'))
    check('§A6 正常数值修订→覆写放行', s4 == 'overwritten_preserved'
          and canon4['data']['CPI']['values'][-1] == 311.0)

    # 写盘中断: json.dump 半途截断→候选校验不符 fail-loud,规范档不动、
    # tmp 不残留、superseded 不新增
    sup_n0 = len([f for f in os.listdir(os.path.join(d, 'superseded'))
                  if not f.startswith('.')])

    def _half_dump(obj, f, *a, **k):
        f.write('{"date": "20261120", "data": {"CPI": {"dates": ["2')

    broke = False
    try:
        with _mock.patch.object(json, 'dump', _half_dump):
            rev2 = json.loads(json.dumps(full))
            rev2['data']['CPI']['values'][-1] = 312.0
            rp.daily_face_guard_write(d, 'macro', '20261120', rev2)
    except (IOError, ValueError) as e:
        broke = True   # 截断候选→回读解析/校验fail-loud,规范档不动
    canon5 = json.load(open(os.path.join(d, 'macro_20261120.json'),
                            encoding='utf-8'))
    tmp_left = [f for f in os.listdir(d) if '.tmp.' in f]
    sup_n1 = len([f for f in os.listdir(os.path.join(d, 'superseded'))
                  if not f.startswith('.')])
    check('§A7 写盘中断→候选校验不符fail-loud(规范档不动/tmp清/superseded不增)',
          broke and canon5['data']['CPI']['values'][-1] == 311.0
          and not tmp_left and sup_n1 == sup_n0,
          f'broke={broke} tmp={tmp_left} sup {sup_n0}→{sup_n1}')

    # 同日并发: 4写者(revision互不降级)+并行读者——规范档任意时刻完整可读
    dd = os.path.join(TMPG, 'daily_c')
    rp.daily_face_guard_write(dd, 'macro', '20261120', full)

    def _writer(k, qq):
        sys.path.insert(0, os.path.join(ROOT, 'scripts'))
        import research_provenance as _rp
        pl = json.loads(json.dumps(full))
        pl['data']['CPI']['values'][-1] = 320.0 + k
        qq.put(_rp.daily_face_guard_write(dd, 'macro', '20261120', pl)[1])

    def _reader(q):
        bad = 0
        for _ in range(300):
            try:
                with open(os.path.join(dd, 'macro_20261120.json'),
                          encoding='utf-8') as f:
                    o = json.load(f)
                if 'CPI' not in o.get('data', {}):
                    bad += 1
            except (OSError, ValueError):
                bad += 1
        q.put(bad)

    ctx = _mp.get_context('fork')
    rq = ctx.Queue()
    rdr = ctx.Process(target=_reader, args=(rq,))
    rdr.start()
    wq = ctx.Queue()
    wrs = [ctx.Process(target=_writer, args=(k, wq)) for k in range(4)]
    for w in wrs:
        w.start()
    statuses = [wq.get() for _ in range(4)]
    for w in wrs:
        w.join()
    rdr.join()
    read_bad = rq.get()
    canon_c = json.load(open(os.path.join(dd, 'macro_20261120.json'),
                             encoding='utf-8'))
    sup_c = [f for f in os.listdir(os.path.join(dd, 'superseded'))
             if not f.startswith('.')]
    sup_ok = all(
        'CPI' in json.load(open(os.path.join(dd, 'superseded', f),
                                encoding='utf-8'))['data']
        for f in sup_c)
    check('§A8 同日并发4写者: 全部正常覆写+规范档=完整新档之一',
          set(statuses) == {'overwritten_preserved'}
          and canon_c['data']['CPI']['values'][-1] in [320.0 + k
                                                       for k in range(4)],
          f'statuses={sorted(set(statuses))}')
    check('§A9 并发窗口旧合格数据始终可读(读者300次零失败)',
          read_bad == 0, f'bad={read_bad}')
    check('§A10 并发转存4份旧档全部完整入superseded/且tmp零残留',
          len(sup_c) == 4 and sup_ok
          and not [f for f in os.listdir(dd) if '.tmp.' in f],
          f'sup={len(sup_c)}')
    # 豁免旗标仍走锁+副本保全路径
    os.environ['IA_DAILY_ALLOW_OVERWRITE'] = '1'
    _, s6, _ = rp.daily_face_guard_write(dd, 'macro', '20261120',
                                         {'tiny': True})
    os.environ.pop('IA_DAILY_ALLOW_OVERWRITE', None)
    canon6 = json.load(open(os.path.join(dd, 'macro_20261120.json'),
                            encoding='utf-8'))
    sup6 = len([f for f in os.listdir(os.path.join(dd, 'superseded'))
                if not f.startswith('.')])
    check('§A11 豁免旗标forced直写(旧档副本仍保留)',
          s6 == 'forced' and canon6 == {'tiny': True} and sup6 == 5)


# ═══ §B 任务2: 三日期分离+草稿规则+覆盖表 ═══════════════════════════
def sec_b():
    print('═══ §B 最新一期: 统计期末/政策确认/草稿/覆盖表 ═══')
    # 正例: 美欧日 Q3 GDP(观测=季首约定,期末09-30,as_of 11-20→期末滞后
    # 51≤120) FRESH;lag_days 仍=as_of−观测日(消费方兼容)
    for mid in ('US_REAL_GDP', 'EA_REAL_GDP_YOY', 'JP_REAL_GDP_YOY'):
        v = fp.assess_observation_freshness(mid, '2026-07-01', '2026-11-20')
        check(f'§B1 {mid}: Q3观测07-01期末09-30→FRESH(旧口径141>120伪STALE)',
              v['fresh'] is True and v['status'] == 'FRESH'
              and v.get('period_end') == '2026-09-30'
              and v.get('period_lag_days') == 51
              and v['lag_days'] == 142,
              f"pe={v.get('period_end')} pel={v.get('period_lag_days')} "
              f"lag={v['lag_days']}")
    # 反例: EA HICP 停在 2025-12(期末12-31,滞后>月窗)→STALE
    v = fp.assess_observation_freshness('EA_HICP_YOY', '2025-12-01',
                                        '2026-11-20')
    check('§B2 EA_HICP停2025-12→STALE(自统计期末起算)',
          v['status'] == 'STALE' and v.get('period_end') == '2025-12-31'
          and v.get('period_lag_days', 0) > v['window'],
          f"pel={v.get('period_lag_days')} w={v['window']}")
    # 决策驱动: ECB_MRO 无更晚证实决议→FRESH;有→STALE
    v1 = fp.assess_observation_freshness('ECB_MRO', '2026-09-16',
                                         '2026-11-20')
    v2 = fp.assess_observation_freshness(
        'ECB_MRO', '2026-09-16', '2026-11-20',
        confirmed_later_decision='2026-11-12')
    check('§B3 ECB_MRO决议驱动: 无更晚证实决议不过期/有之→STALE',
          v1['fresh'] is True
          and v1.get('freshness_basis') == 'policy_confirmation'
          and v2['status'] == 'STALE' and '更晚决议证实' in v2['reasons'][0],
          f"v1={v1['status']} v2={v2['status']}")
    # 注册表四序列声明 decision_dated
    reg = json.load(open(os.path.join(ROOT, 'config',
                                      'metric_registry.json'),
                         encoding='utf-8'))
    dd = {m['metric_id'] for m in reg['metrics']
          if (m.get('freshness') or {}).get('decision_dated')}
    check('§B4 注册表: ECB_MRO/ECB_DFR/DFEDTARU/DFEDTARL声明decision_dated',
          dd == {'ECB_MRO', 'ECB_DFR', 'DFEDTARU', 'DFEDTARL'}, str(sorted(dd)))
    # 草稿规则: 组内最新一期ok锚全stale→组入列;任一非stale即不入
    pv = {'cells': [
        {'region': 'EA', 'dimension': 'inflation',
         'anchors': {'最新一期': {'status': 'ok', 'freshness': 'stale'}}},
        {'region': 'US', 'dimension': 'inflation',
         'anchors': {'最新一期': {'status': 'ok'}}},
        {'region': 'JP', 'dimension': 'growth',
         'anchors': {'最新一期': {'status': 'ok', 'freshness': 'stale'},
                     '12个月前': {'status': 'ok', 'freshness': 'stale'}}}]}
    sg = rmp.stale_only_groups(pv, {('EA', 'inflation'), ('US', 'inflation'),
                                    ('JP', 'growth')})
    check('§B5 stale_only_groups: 全stale组入列/有非stale锚不入/历史锚不参与',
          sg == [('EA', 'inflation'), ('JP', 'growth')], str(sg))
    # blocked_class=map_core_dimension_stale→草稿交付+正式归档拒
    check('§B6 map_core_dimension_stale: 草稿元组+belt阻断类双在场',
          'map_core_dimension_stale' in aj.BLOCKING_BLOCKED_CLASSES
          and 'map_core_dimension_stale' in open(
              os.path.join(ROOT, 'ia_cli.py'), encoding='utf-8').read())
    # 首页草稿横幅+逐组覆盖与实际数据来源表(端到端渲染)
    plan = {'regions': {'EA': {'dimensions': {
        'inflation': [{'metric_id': 'EA_HICP_YOY', 'display_name': 'HICP同比',
                       'frequency': 'monthly'}]}}},
        'metrics': ['EA_HICP_YOY'], 'context_metrics': [],
        'point_anchors': [
            {'kind': 'point', 'label': '12个月前', 'as_of': '2025-11-20',
             'months_before': 12},
            {'kind': 'point', 'label': '最新一期', 'as_of': '2026-11-20',
             'months_before': 0}]}
    snap = {'series_store': {'EA_HICP_YOY': {
        # 10-01观测发布11-16(月末+16推定)≤12个月前锚2025-11-20→历史锚ok;
        # 12-01为末观测,期末12-31滞后>月窗→最新一期⚠过期
        'dates': ['2025-10-01', '2025-11-01', '2025-12-01'],
        'values': [2.4, 2.2, 1.9], 'frequency': 'monthly'}}}
    pv2 = rmp.point_values(plan, snap, ROOT)
    md = rmp.render_map_report(
        {'research_plan': dict(plan, map_question=True, point_values=pv2,
                               dimension_gaps=[], cutoff='2026-11-20'),
         'agent_judgment': {'reader_map': {
             'headline_conclusion': 'x', 'regions': [], 'transmission': [],
             'turnings': [], 'history_periods': []}}},
        {}, {'required': False}, root=ROOT)
    check('§B7 首页草稿横幅: EA×inflation+正式归档拒绝口径',
          '⚠ **草稿(非正式)**' in md and 'EA×inflation' in md
          and 'map_core_dimension_stale' in md
          and md.index('草稿(非正式)') < md.index('## 一句总判断'))
    check('§B8 逐组覆盖与实际数据来源表: 三锚状态+统计期末+发布日期+来源',
          '## 逐组覆盖与实际数据来源' in md and '| ok | ⚠过期 |' in md
          and '2025-12-31' in md and '注册表权威采集器' in md)
    # 判定与渲染共源(草稿判定不靠渲染字符串)
    _pairs = {(_eco, _dim) for _eco, _rf in plan['regions'].items()
              for _dim in _rf['dimensions']}
    check('§B9 判定侧同源: point_values面直接判出同一stale-only组',
          rmp.stale_only_groups(pv2, _pairs) == [('EA', 'inflation')])


# ═══ §C 任务3: 历史章节当时可知+BoJ决议/生效分记 ═════════════════════
def sec_c():
    print('═══ §C 历史章节: 月均移出政策面+BoJ实录表分记 ═══')
    face_ids = {m for m, _ in rmp._AOF_POLICY_METRICS}
    check('§C1 JP_POLICY_RATE(月均)移出政策事件面(月均=市场观测≠决议)',
          'JP_POLICY_RATE' not in face_ids
          and 'JP_POLICY_TARGET' in face_ids
          and rmp.POLICY_FACE['JP_POLICY_RATE']['decision'] is None)
    check('§C2 JP_POLICY_TARGET入面: boj_history+配对市场月均+口径注记',
          (rmp.POLICY_FACE['JP_POLICY_TARGET'].get('decision_kind')
           == 'boj_history')
          and rmp.POLICY_FACE['JP_POLICY_TARGET'].get('market_pair')
          == 'JP_POLICY_RATE')
    check('§C3 实录表锚: 2024-03-19决议/03-21生效(用户验收指令实录)',
          rmp._boj_decision_of('2024-03-21')[0] == '2024-03-19'
          and rmp._boj_decision_of('2024-03-22') is None)
    pd1 = rmp._policy_dates(rmp.POLICY_FACE['JP_POLICY_TARGET'],
                            '2024-03-31', value_change_date='2024-03-21')
    check('§C4 _policy_dates boj_history: 生效=值变更日/决议=实录回溯',
          pd1['effective'] == '2024-03-21' and pd1['decision'] == '2024-03-19'
          and '决议2024-03-19、生效2024-03-21' in pd1['decision_note'],
          str(pd1.get('decision_note'))[:80])
    pd2 = rmp._policy_dates(rmp.POLICY_FACE['JP_POLICY_TARGET'],
                            '2026-11-20', value_change_date='2026-04-01')
    check('§C5 表外生效日→决议日不可推(如实注记不虚构)',
          pd2['decision'] is None and '不可推' in pd2['decision_note']
          and pd2['effective'] == '2026-04-01')
    pd3 = rmp._policy_dates(rmp.POLICY_FACE['JP_POLICY_TARGET'],
                            '2026-11-20', value_change_date=None)
    check('§C6 序列在场期无变更→决议/生效双不可推',
          pd3['decision'] is None and pd3['effective'] is None)
    # R25保留面: 发布日与数字校验在场(回归不回退)
    aj_src = open(os.path.join(ROOT, 'scripts', 'research_map_planner.py'),
                  encoding='utf-8').read()
    check('§C7 R25既得面保留: 当时可知纪律+发布日推定在场',
          '当时可知' in aj_src and '_aof_first_pub' in aj_src)


# ═══ §D 任务4: 原问逐字纪律+验收包结构面 ════════════════════════════
def sec_d():
    print('═══ §D 原问逐字: 首轮落盘+字节直读+新原文入计划 ═══')
    skill = open(os.path.join(ROOT, '.agents', 'skills',
                              'global-macro-research', 'SKILL.md'),
                 encoding='utf-8').read()
    check('§D1 SKILL纪律: 首轮第一动作=当轮消息原样落盘独立原问文件',
          '首轮第一动作' in skill and 'question_verbatim_' in skill
          and '不预置' in skill and '不得复用旧轮文件' in skill
          and '禁止重写' in skill)
    check('§D2 入口纪律: --question-file字节直读优先/内联仅调试',
          '--question-file' in skill and '仅作调试用途' in skill
          and '字节直读' in skill)
    # 字节直读: 全角标点原样入计划(169字工单实雷面)
    import research_orchestrator as ro
    reg = json.load(open(os.path.join(ROOT, 'config',
                                      'metric_registry.json'),
                         encoding='utf-8'))
    orig = ('给我一份截至今日(2026-11-20)的美、欧、日、中四地宏观地图:'
            '增长、通胀、利率、汇率与资产表现——含12个月前、3个月前两个'
            '对照时点。')
    plan_q = rmp.plan_map(orig, ro.map_entities(orig, reg),
                          reg.get('by_id') or {}, '2026-11-20')
    check('§D3 计划收 question_verbatim=原文(含全角标点不重排)',
          plan_q.get('question_verbatim') == orig)
    orig2 = '换成: 2026年11月美联储与欧央行政策利率对比,并给出JP隔夜拆借月均。'
    plan_q2 = rmp.plan_map(orig2, ro.map_entities(orig2, reg),
                           reg.get('by_id') or {}, '2026-11-20')
    check('§D4 第二问→新原文入计划(不复用旧轮原文)',
          plan_q2.get('question_verbatim') == orig2
          and plan_q2.get('question_verbatim') != plan_q.get(
              'question_verbatim'))
    # ia_cli 草稿四类入口(任务1缺口类+任务2确证过期类)
    ia_src = open(os.path.join(ROOT, 'ia_cli.py'), encoding='utf-8').read()
    check('§D5 草稿入口: 缺口类+确证过期类并列+任务1+任务2口径',
          "'map_core_dimension_missing'" in ia_src
          and "'map_anchor_coverage_insufficient'" in ia_src
          and "'map_core_dimension_stale'" in ia_src
          and 'Audit-R25 任务1+Audit-R26 任务2' in ia_src)
    # 空文件拒绝(error=empty_question_file,不静默回落)
    empty = os.path.join(TMPG, 'empty.txt')
    with open(empty, 'w', encoding='utf-8') as f:
        f.write('')
    rc = subprocess.run(
        [sys.executable, os.path.join(ROOT, 'ia_cli.py'), 'research-one',
         '--stage', 'plan', '--question-file', empty],
        capture_output=True, text=True, timeout=600, cwd=ROOT)
    check('§D6 空原问文件→拒绝(empty_question_file不静默)',
          rc.returncode != 0
          and 'empty_question_file' in (rc.stdout + rc.stderr),
          f'rc={rc.returncode}')


def main():
    for sec in (sec_a, sec_b, sec_c, sec_d):
        sec()
    n_pass = sum(1 for _, ok, _ in RESULTS if ok)
    n_fail = len(RESULTS) - n_pass
    print('\n' + '═' * 60)
    print(f'判定: {n_pass} PASS / {n_fail} FAIL')
    if n_fail:
        for name, ok, detail in RESULTS:
            if not ok:
                print(f'  ❌ {name} — {detail}')
    return 1 if n_fail else 0


if __name__ == '__main__':
    sys.exit(main())
