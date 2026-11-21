#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit-R27(R72)门 — 正式使用验收前置: 四任务核心面回归。

任务1 §B/§C: 点锚修正(显式 YYYY年M月=当期锚+比较结构隐含当期端点;
对照表恒有当期列)+句段作用域地区×维度请求(日本央行政策利率子问=
JP×policy,不摊全域网格)+政策时效第三态 UNVERIFIED(无更晚已证实决议
且无证实间隔超决策周期上限——2024-06-06 ECB 决议复测: 旧值不能因本地
日历没收录新决议就被判新鲜)+当期缺失/未核验→草稿三侧共源(首页横幅/
交付状态/归档 belt)。
任务2 §D: 历史正文当时可知纪律强化——事后日期写回「当时」段拒绝
(expost_date_written_back)+值泄漏判据扩到全部事后数值行(异常延误行)。
任务3 §A: 同日首写并发——查存在/读取/判降级/提交同一把锁;空目录同时
写完整档与缺 CPI 档两种提交顺序均保住完整数据;同计数最新有效观测
回退转存;正常修订/前向追加放行。
任务4 §E: 随包重放面——完整运行 SHA/原问(question_verbatim.txt)/裁决链
(REVISE→UPHELD 两记录)/地图摘要/一条可执行重放命令随包,归档件集含
原问文件;SKILL 草稿纪律扩两类新 blocked_class。
"""
import json
import multiprocessing as _mp
import os
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
import freshness_policy as fp              # noqa: E402
import agent_judgment as aj               # noqa: E402
from judgment_contract import build_face, verify_judgment  # noqa: E402

RESULTS = []
TMPG = tempfile.mkdtemp(prefix='r27gate_')

Q_B = ('对比角度换一个：2026年11月，美国与欧元区的增长和通胀环境相比'
       '3个月前各有什么变化？日本央行政策利率处于什么水平，距离上次'
       '调整过了多久？')
Q_A = ('给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在12个月'
       '前、3个月前和最新一期，分别处于什么增长、通胀和货币政策环境？'
       '过去一年最重要的三个转折是什么，谁先变，谁跟进或背离？证据最'
       '充分的传导机制是什么，还有什么解释，哪个指标能区分它们？历史'
       '上哪些时期结构最像，当时其他经济体是否同步，随后3、6、12个月'
       '经济和主要资产实际怎么走？')


def check(name, ok, detail=''):
    RESULTS.append((name, bool(ok), str(detail)[:220]))
    print(('  ✅ ' if ok else ' ❌ ') + name
          + (f' — {detail}' if detail else ''), flush=True)


# ═══ §A 任务3: 同日首写并发一把锁+时点回退转存 ═════════════════════
def sec_a():
    print('═══ §A 同日首写并发: 一把锁/两序保完整/时点回退转存 ═══')
    full = {'date': '20261121',
            'data': {'CPI': {'dates': ['2026-09-01', '2026-10-01',
                                       '2026-11-01'],
                             'values': [310.0, 310.5, 311.0]},
                     'PCE': {'dates': ['2026-11-01'],
                             'values': [118.5]}}}
    miss_cpi = {'date': '20261121',
                'data': {'PCE': {'dates': ['2026-11-01'],
                                 'values': [118.5]}}}
    # 顺序一: 完整档先到 → 缺 CPI 档按身份丢失转存,规范档保完整
    d1 = os.path.join(TMPG, 'daily_o1')
    _, s1, _ = rp.daily_face_guard_write(d1, 'macro', '20261121', full)
    p2, s2, n2 = rp.daily_face_guard_write(d1, 'macro', '20261121', miss_cpi)
    c1 = json.load(open(os.path.join(d1, 'macro_20261121.json'),
                        encoding='utf-8'))
    check('§A1 顺序一(完整先到): 缺CPI档→degraded_diverted+规范档保完整',
          s1 == 'first' and s2 == 'degraded_diverted'
          and '身份丢失' in n2 and 'CPI' in c1['data']
          and c1['data']['CPI']['values'] == [310.0, 310.5, 311.0],
          f'{s1}/{s2} note={n2[:60]}')
    # 顺序二: 缺 CPI 档先到 → 完整档身份超集且无回退→覆写,规范档=完整
    d2 = os.path.join(TMPG, 'daily_o2')
    _, s3, _ = rp.daily_face_guard_write(d2, 'macro', '20261121', miss_cpi)
    _, s4, n4 = rp.daily_face_guard_write(d2, 'macro', '20261121', full)
    c2 = json.load(open(os.path.join(d2, 'macro_20261121.json'),
                        encoding='utf-8'))
    check('§A2 顺序二(缺CPI先到): 完整档覆写落位+规范档=完整数据',
          s3 == 'first' and s4 == 'overwritten_preserved' and n4 == ''
          and c2['data']['CPI']['values'] == [310.0, 310.5, 311.0],
          f'{s3}/{s4} note={n4[:60]}')
    # 真并发: 空目录两进程同时首写(完整+缺CPI),规范档收敛=完整
    dd = os.path.join(TMPG, 'daily_cc')
    os.makedirs(dd, exist_ok=True)

    def _w(k, qq):
        sys.path.insert(0, os.path.join(ROOT, 'scripts'))
        import research_provenance as _rp
        pl = full if k == 0 else miss_cpi
        qq.put(_rp.daily_face_guard_write(dd, 'macro', '20261121', pl)[1])

    ctx = _mp.get_context('fork')
    q = ctx.Queue()
    ws = [ctx.Process(target=_w, args=(k, q)) for k in range(2)]
    for w in ws:
        w.start()
    sts = sorted(q.get() for _ in range(2))
    for w in ws:
        w.join()
    cc = json.load(open(os.path.join(dd, 'macro_20261121.json'),
                        encoding='utf-8'))
    check('§A3 空目录真并发首写: 规范档=完整数据(任意交错)',
          'CPI' in cc['data'] and cc['data']['CPI']['values'][-1] == 311.0
          and 'first' in sts
          and set(sts) <= {'first', 'overwritten_preserved',
                           'degraded_diverted'},
          f'statuses={sts}')
    # 同计数时点回退: 条数相同但最新有效观测日后移 → 转存
    d3 = os.path.join(TMPG, 'daily_hz')
    rp.daily_face_guard_write(d3, 'macro', '20261121', full)
    back = {'date': '20261121',
            'data': {'CPI': {'dates': ['2026-08-01', '2026-09-01',
                                       '2026-10-01'],
                             'values': [309.5, 310.0, 310.5]},
                     'PCE': {'dates': ['2026-11-01'],
                             'values': [118.5]}}}
    p5, s5, n5 = rp.daily_face_guard_write(d3, 'macro', '20261121', back)
    c5 = json.load(open(os.path.join(d3, 'macro_20261121.json'),
                        encoding='utf-8'))
    check('§A4 同计数时点回退→degraded_diverted(「条数相同」不掩回退)',
          s5 == 'degraded_diverted' and '最新有效观测回退' in n5
          and '2026-11-01→2026-10-01' in n5
          and c5['data']['CPI']['dates'][-1] == '2026-11-01',
          f's={s5} note={n5[:80]}')
    # 正常修订/前向追加放行(回归保全)
    rev = json.loads(json.dumps(full))
    rev['data']['CPI']['values'][-1] = 311.2
    _, s6, n6 = rp.daily_face_guard_write(d3, 'macro', '20261121', rev)
    fwd = json.loads(json.dumps(full))
    fwd['data']['CPI'] = {'dates': ['2026-10-01', '2026-11-01',
                                    '2026-12-01'],
                          'values': [310.5, 311.0, 311.4]}
    _, s7, n7 = rp.daily_face_guard_write(d3, 'macro', '20261121', fwd)
    check('§A5 正常数值修订+前向追加→放行(旧语义保全)',
          s6 == 'overwritten_preserved' and n6 == ''
          and s7 == 'overwritten_preserved' and n7 == '',
          f'{s6}/{s7}')
    # 断网空壳面(null 占位)先落、富面后到: null→富容器提升≠身份丢失
    # (占位 null 叶有效观测=0,不承载数据)——富面须落规范位
    d4 = os.path.join(TMPG, 'daily_null_shell')
    shell = {'date': '20261121', 'version': 2,
             'ah_premium': None, 'margin': None, 'southbound': None,
             'macro': {}, 'series': {},
             'a_share_indices': {'000001': {'close': 1.0}}}
    rich = {'date': '20261121', 'version': 2,
            'ah_premium': {'close': 128.4, 'date': '2026-11-20',
                           'signal': 'neutral'},
            'macro': {'pmi_mfg': {'dates': ['2026-10-01'],
                                  'values': [50.1]}},
            'series': {'CN_CPI_YOY': {'dates': ['2026-10-01'],
                                      'values': [0.3]}},
            'a_share_indices': {'000001': {'close': 1.1}}}
    _, s8, _ = rp.daily_face_guard_write(d4, 'china', '20261121', shell)
    _, s9, n9 = rp.daily_face_guard_write(d4, 'china', '20261121', rich)
    c9 = json.load(open(os.path.join(d4, 'china_20261121.json'),
                        encoding='utf-8'))
    check('§A6 空壳(null占位)先到+富面后到→富面落规范位'
          '(null→容器提升≠身份丢失;验收实测形态)',
          s8 == 'first' and s9 == 'overwritten_preserved' and n9 == ''
          and 'CN_CPI_YOY' in (c9.get('series') or {})
          and c9['ah_premium']['close'] == 128.4,
          f'{s8}/{s9} note={n9[:60]}')
    # 反例保全: 真实数据身份(叶数>0)被删仍判丢失转存
    d5 = os.path.join(TMPG, 'daily_realloss')
    rp.daily_face_guard_write(d5, 'macro', '20261121', full)
    lost = json.loads(json.dumps(full))
    del lost['data']['CPI']
    _, s10, n10 = rp.daily_face_guard_write(d5, 'macro', '20261121', lost)
    check('§A7 真实数据身份被删→仍 degraded_diverted(占位豁免不放松)',
          s10 == 'degraded_diverted' and '身份丢失' in n10
          and 'CPI' in n10, f's={s10} note={n10[:60]}')


# ═══ §B 任务1: 点锚修正+句段作用域请求 ═════════════════════════════
def sec_b():
    print('═══ §B 点锚: 显式年月/比较结构/句段作用域 ═══')
    b_anchors = rmp.parse_point_anchors(Q_B, '2026-11-20')
    labels = [(a['label'], a['months_before'], a.get('explicit_period'))
              for a in b_anchors]
    check('§B1 会话B原问: 当期(2026年11月=截止月)+3个月前双锚',
          labels == [('3个月前', 3, None),
                     ('最新一期', 0, '2026-11')],
          str(labels))
    a_anchors = rmp.parse_point_anchors(Q_A, '2026-11-20')
    check('§B2 会话A原问: 12个月前/3个月前/最新一期三锚不变(零回归)',
          [(a['label'], a['months_before']) for a in a_anchors]
          == [('12个月前', 12), ('3个月前', 3), ('最新一期', 0)])
    h_anchors = rmp.parse_point_anchors(
        '2024年6月美国与欧元区的增长通胀环境相比2023年6月有何不同？',
        '2026-11-20')
    check('§B3 纯历史点问句: 显式历史锚入列+不虚构当期锚',
          [(a['label'], a['months_before']) for a in h_anchors]
          == [('2023年6月', 41), ('2024年6月', 29)]
          and all(a['months_before'] != 0 for a in h_anchors),
          str([(a['label'], a['months_before']) for a in h_anchors]))
    reqs_b = rmp._clause_region_dimension_requests(
        Q_B, ['US', 'EA', 'JP', 'CN'])
    check('§B4 句段作用域: B问=US/EA×增长通胀+JP×policy(无跨段摊派)',
          reqs_b == [('US', 'growth'), ('US', 'inflation'),
                     ('EA', 'growth'), ('EA', 'inflation'),
                     ('JP', 'policy')], str(reqs_b))
    reqs_a = rmp._clause_region_dimension_requests(
        Q_A, ['US', 'EA', 'JP', 'CN'])
    check('§B5 句段作用域: A问单句全组=12组全网格(零回归)',
          len(reqs_a) == 12 and ('CN', 'policy') in reqs_a, str(len(reqs_a)))
    reqs_fb = rmp._clause_region_dimension_requests(
        '增长与通胀的环境如何对比？', ['US', 'CN'])
    reg_by_id = {}
    with open(os.path.join(ROOT, 'config', 'metric_registry.json'),
              encoding='utf-8') as f:
        for m in json.load(f).get('metrics') or []:
            reg_by_id[m['metric_id']] = m
    plan_fb = rmp.plan_map('增长与通胀的环境如何对比？',
                           {'economies': ['US', 'CN']}, reg_by_id,
                           '2026-11-20')
    got_fb = {(e, d) for e, rf in plan_fb['regions'].items()
              for d in rf['dimensions']}
    check('§B6 词形分置无段请求→plan_map 回退全域全维笛卡尔(旧口径)',
          reqs_fb == [] and got_fb == {('US', 'growth'),
                                       ('US', 'inflation'),
                                       ('CN', 'growth'),
                                       ('CN', 'inflation')}, str(got_fb))
    # plan_map 端到端: B问 regions 恰为所请求组
    plan_b = rmp.plan_map(Q_B, {'economies': ['US', 'EA', 'JP']},
                          reg_by_id, '2026-11-20')
    got_pairs = {(e, d) for e, rf in plan_b['regions'].items()
                 for d in rf['dimensions']}
    check('§B7 plan_map(B问): 计划组=请求组(JP×policy在/US×policy不在)',
          got_pairs == {('US', 'growth'), ('US', 'inflation'),
                        ('EA', 'growth'), ('EA', 'inflation'),
                        ('JP', 'policy')}
          and 'JP_POLICY_RATE' in plan_b['metrics'],
          str(sorted(got_pairs)))


# ═══ §C 任务1: 政策时效第三态+当期草稿三侧共源 ═════════════════════
def sec_c():
    print('═══ §C 政策时效 UNVERIFIED+当期缺失/未核验草稿 ═══')
    # 2024-06-06 ECB 决议复测: 旧值 obs 2024-06-05
    v_nc = fp.assess_observation_freshness('ECB_MRO', '2024-06-05',
                                           '2024-12-01')
    check('§C1 复测(本地日历未收录新决议): 旧值不判新鲜→UNVERIFIED',
          v_nc['status'] == 'UNVERIFIED' and v_nc['fresh'] is False
          and '无法核验' in v_nc['reasons'][0]
          and v_nc.get('decision_cycle_bound_days') == 90,
          f'{v_nc["status"]} lag={v_nc["lag_days"]}')
    cal = {'entries': [{'metric_id': 'ECB_MRO', 'obs_from': '2024-06-06',
                        'first_publish_on_or_after': '2024-06-06'}]}
    cal_p = os.path.join(TMPG, 'cal_retest.json')
    with open(cal_p, 'w', encoding='utf-8') as f:
        json.dump(cal, f)
    cd = fp.confirmed_policy_decision_after(
        'ECB_MRO', '2024-06-05', '2024-12-01', calendar_path=cal_p)
    v_wc = fp.assess_observation_freshness(
        'ECB_MRO', '2024-06-05', '2024-12-01', confirmed_later_decision=cd)
    check('§C2 复测(日历收录决议): 确证过期→STALE(不因第三态放松)',
          cd == '2024-06-06' and v_wc['status'] == 'STALE')
    v_b90 = fp.assess_observation_freshness('ECB_MRO', '2026-08-22',
                                            '2026-11-20')
    v_b91 = fp.assess_observation_freshness('ECB_MRO', '2026-08-21',
                                            '2026-11-20')
    check('§C3 边界: 无证实间隔≤90天FRESH/91天UNVERIFIED(利率长期不变'
          '≠无法核验)',
          v_b90['status'] == 'FRESH' and v_b91['status'] == 'UNVERIFIED',
          f'{v_b90["status"]}/{v_b91["status"]}')
    v_a = fp.assess_observation_freshness('ECB_MRO', '2026-09-16',
                                          '2026-11-20')
    check('§C4 会话A形态(滞后65天无证实)→FRESH(不误伤完整交付)',
          v_a['status'] == 'FRESH')
    # current_period_groups 单元
    pv_c = {'cells': [
        {'region': 'EA', 'dimension': 'policy',
         'anchors': {'最新一期': {'status': 'ok',
                                 'freshness': 'unverified'}}},
        {'region': 'EA', 'dimension': 'growth',
         'anchors': {'最新一期': {'status': 'no_published_observation'
                                          '_on_or_before_anchor'},
                     '12个月前': {'status': 'ok'},
                     '3个月前': {'status': 'ok'}}},
        {'region': 'US', 'dimension': 'policy',
         'anchors': {'最新一期': {'status': 'ok'},
                     '3个月前': {'status': 'ok'}}}]}
    pairs_c = {('EA', 'policy'), ('EA', 'growth'), ('US', 'policy')}
    regions_c = {}
    for e, d in sorted(pairs_c):
        regions_c.setdefault(e, {'dimensions': {}})['dimensions'][d] = [{}]
    cur = rmp.current_period_groups(pv_c, pairs_c)
    # (Audit-R28 任务2: 返回结构新增 stale_mix 键——混合形态分组,
    #  R27 两键语义不变;断言随结构扩展更新)
    check('§C5 current_period_groups: 当期缺数/未核验分组(他时点ok不补)',
          cur == {'missing': [('EA', 'growth')],
                  'unverified': [('EA', 'policy')],
                  'stale_mix': []}, str(cur))
    check('§C6 纯历史点问句(无当期锚)不判当期',
          rmp.current_period_groups(pv_c, pairs_c,
                                    has_current_anchor=False)
          == {'missing': [], 'unverified': [], 'stale_mix': []})
    rep_c = {'run_ok': True,
             'layers': {'L1_事实层': {'rows': [{'x': 1}]}},
             'run': {'data_requirements': {'items': []}},
             'steps': [],
             'agent_judgment': {'reader_map_faces': {'complete': True}},
             'research_plan': {'map_question': True,
                               'point_anchors': [
                                   {'label': '最新一期',
                                    'months_before': 0}],
                               'regions': regions_c,
                               'point_values': pv_c}}
    check('§C7 blocked_class_of 共源: 当期缺数→map_current_period_missing',
          aj.blocked_class_of(rep_c) == 'map_current_period_missing',
          str(aj.blocked_class_of(rep_c)))
    pv_c2 = {'cells': [c for c in pv_c['cells']
                       if not (c['region'] == 'EA'
                               and c['dimension'] == 'growth')]}
    rep_c2 = dict(rep_c, research_plan=dict(
        rep_c['research_plan'],
        regions={'EA': {'dimensions': {'policy': [{}]}},
                 'US': {'dimensions': {'policy': [{}]}}},
        point_values=pv_c2))
    check('§C8 blocked_class_of 共源: 当期全未核验→'
          'map_current_period_unverified',
          aj.blocked_class_of(rep_c2) == 'map_current_period_unverified',
          str(aj.blocked_class_of(rep_c2)))
    check('§C9 阻断类目入 BLOCKING(attach/报告/归档同源)',
          {'map_current_period_missing', 'map_current_period_unverified'}
          <= aj.BLOCKING_BLOCKED_CLASSES)
    # 端到端: 空日历树→EA×policy 当期锚 UNVERIFIED(渲染+按时点覆盖+重放面)
    import shutil
    t_c = os.path.join(TMPG, 'tree_c')
    os.makedirs(os.path.join(t_c, 'config'), exist_ok=True)
    shutil.copy(os.path.join(ROOT, 'config', 'metric_registry.json'),
                os.path.join(t_c, 'config', 'metric_registry.json'))
    with open(os.path.join(t_c, 'config', 'release_calendar.json'),
              'w', encoding='utf-8') as f:
        json.dump({'entries': []}, f)
    plan_c = {'regions': {'EA': {'dimensions': {'policy': [
        {'metric_id': 'ECB_MRO', 'display_name': '欧央行主要再融资利率',
         'frequency': 'daily', 'unit': '%',
         'vintage_semantics': '采集时点族',
         'policy_face': rmp.POLICY_FACE.get('ECB_MRO')}]}}},
        'metrics': ['ECB_MRO'], 'context_metrics': [],
        'cutoff': '2026-11-20',
        'point_anchors': [
            {'kind': 'point', 'label': '12个月前', 'as_of': '2025-11-20',
             'months_before': 12},
            {'kind': 'point', 'label': '3个月前', 'as_of': '2026-08-20',
             'months_before': 3},
            {'kind': 'point', 'label': '最新一期', 'as_of': '2026-11-20',
             'months_before': 0}]}
    snap_c = {'series_store': {
        'ECB_MRO': {'dates': ['2025-11-05', '2026-02-11', '2026-05-13'],
                    'values': [3.15, 3.15, 4.0], 'frequency': 'daily',
                    'source': 'test'}}}
    pv_c3 = rmp.point_values(plan_c, snap_c, t_c)
    _cur_la = (pv_c3['cells'][0]['anchors'].get('最新一期') or {})
    check('§C10 端到端: 空日历+滞后191天→当期锚 freshness=unverified',
          _cur_la.get('status') == 'ok'
          and _cur_la.get('freshness') == 'unverified'
          and _cur_la.get('unconfirmed_span_days') == 191,
          str({k: _cur_la.get(k) for k in
               ('status', 'freshness', 'unconfirmed_span_days')}))
    md_c = rmp.render_map_report(
        {'run': {'git_head': 'r27gate0', 'git_head_source': 'test'},
         'research_plan': dict(plan_c, map_question=True,
                               point_values=pv_c3, dimension_gaps=[],
                               cutoff='2026-11-20'),
         'agent_judgment': {'reader_map': {
             'headline_conclusion': 'x', 'regions': [], 'transmission': [],
             'turnings': [], 'history_periods': []}}},
        {}, {'required': False}, root=t_c)
    check('§C11 未核验草稿横幅+归档拒绝口径(首页可见)',
          '当期值**无法核验**' in md_c and 'EA×policy' in md_c
          and 'map_current_period_unverified' in md_c
          and md_c.index('无法核验') < md_c.index('## 一句总判断'))
    check('§C12 对照表/覆盖表 ⚠未核验 标注+按时点统计覆盖行',
          '⚠未核验:最后确认2026-05-13' in md_c
          and md_c.count('⚠未核验') >= 2
          and '按时点统计覆盖' in md_c
          and '12个月前=1/1组ok' in md_c and '最新一期=1/1组ok' in md_c)
    # 当期缺数横幅(注入手造 pv: 历史ok+当期不可得)
    pv_c4 = {'cells': [
        {'region': 'EA', 'dimension': 'growth',
         'anchors': {'最新一期': {'status': 'no_published_observation'
                                          '_on_or_before_anchor'},
                     '12个月前': {'status': 'ok'},
                     '3个月前': {'status': 'ok'}}}],
        'absent': []}
    plan_c4 = dict(plan_c, regions={'EA': {'label': '欧元区',
                                           'dimensions': {'growth': [
                                               {'metric_id': 'EA_REAL_GDP_'
                                                'YOY'}]}}})
    md_c2 = rmp.render_map_report(
        {'run': {'git_head': 'r27gate0', 'git_head_source': 'test'},
         'research_plan': dict(plan_c4, map_question=True,
                               point_values=pv_c4, dimension_gaps=[],
                               cutoff='2026-11-20'),
         'agent_judgment': {'reader_map': {
             'headline_conclusion': 'x', 'regions': [], 'transmission': [],
             'turnings': [], 'history_periods': []}}},
        {}, {'required': False}, root=t_c)
    check('§C13 当期缺数草稿横幅(他时点ok不补当期)',
          '必要维度**当期**缺数' in md_c2 and 'EA×growth' in md_c2
          and 'map_current_period_missing' in md_c2
          and '核心维度组缺数' not in md_c2.split('## 一句总判断')[0])


# ═══ §D 任务2: 当时可知纪律强化(事后日期写回拒绝+延误值泄漏) ═══════
def sec_d():
    print('═══ §D 历史正文: 事后日期写回拒绝+延误行值泄漏 ═══')
    arc = os.path.join(
        ROOT, 'docs', 'autonomous-rd', 'r22-evidence', 'acceptance',
        '20261119T153709Z_给我一份全球宏观经济变化地图_美国_中国_欧元区_'
        '日本在12个月前_3个月前和最')
    with open(os.path.join(arc, 'report.json'), encoding='utf-8') as f:
        RJ = json.load(f)
    with open(os.path.join(arc, 'agent_judgment.json'),
              encoding='utf-8') as f:
        JD0 = json.load(f)
    import copy
    rj_m = copy.deepcopy(RJ)
    rj_m['research_plan']['asof_discipline'] = 'r23'
    face_m = build_face(rj_m)

    def contract(mutate):
        jd = copy.deepcopy(JD0)
        mutate(jd)
        res = verify_judgment(jd, rj_m, face=face_m)
        return res, [f for f in (res.get('map_checks') or [])
                     if f.get('status') != 'VERIFIED']

    def writeback(jd):
        for h in jd['reader_map']['history_periods']:
            cym = str(h.get('judgment_cutoff_ym') or '')
            if len(cym) == 7:
                h['difference'] = (str(h.get('difference') or '')
                                   + f';事后观察: {cym[:5]}'
                                   + str(int(cym[5:7]) + 1).zfill(2)
                                   + '-11 欧央行按兵不动')
                break

    res, bad = contract(writeback)
    wb = [b for b in bad
          if 'expost_date_written_back' in str(b.get('item'))]
    check('§D1 事后日期写回「当时」段→拒绝(expost_date_written_back)',
          res.get('verdict') == 'CONTRADICTED' and len(wb) >= 1
          and '不得写回' in str(wb[0].get('note')),
          str([str(b.get('item'))[:60] for b in wb[:1]]))

    def corrected(jd):
        for h in jd['reader_map']['history_periods']:
            p = rmp.history_asof_face([h], rj_m)['periods'][0]
            parts = [f"{r['label'].split('(')[0]} {r['value']:g}"
                     f"({r['obs_month']},公布{r['visible_from']})"
                     for r in p['known']]
            txt = '当时可知(发布纪律重算): ' + '、'.join(parts)
            h['other_regions_sync'] = txt
            h['similarity'] = txt
            h['difference'] = txt

    res2, bad2 = contract(corrected)
    check('§D2 当时可知改写(含当时日期)→不误伤(VERIFIED)',
          res2.get('verdict') == 'VERIFIED' and not bad2,
          str([str(b.get('note'))[:70] for b in bad2[:1]]))
    # 延误行值泄漏: 截止后异常延误行的值被正文引用 → as_of_leak
    def fake_face(history_periods, rj):
        h = history_periods[0]
        cym = str(h.get('judgment_cutoff_ym')
                  or h.get('anchor_ym') or '2025-03')
        mid, label = 'CN_PPI_YOY', '中国PPI同比'
        return {'periods': [{
            'anchor_ym': h.get('anchor_ym'), 'cutoff_ym': cym,
            'cutoff_end': '2025-03-31',
            'known': [{'metric_id': mid, 'label': label,
                       'obs_month': '2025-01', 'obs_date': '2025-01-01',
                       'value': -2.1, 'visible_from': '2025-02-10',
                       'first_publish': '2025-02-10',
                       'pub_basis': 'rule', 'source': 'test',
                       'revision_note': '', 'note': ''}],
            'aftermath': [
                {'metric_id': mid, 'label': label, 'obs_month': '2025-02',
                 'obs_date': '2025-02-01', 'value': -2.2,
                 'visible_from': '2025-06-01',
                 'first_publish': '2025-06-01', 'pub_basis': 'rule',
                 'source': 'test', 'revision_note': '', 'note': '',
                 'delay_note': '异常延误(首发晚于常轨>45天)'}],
            'absent': []}]}

    def cite_delayed(jd):
        for h in jd['reader_map']['history_periods']:
            h['similarity'] = '当时可知: 中国PPI -2.2(事后才公布)'

    with _mock.patch.object(rmp, 'history_asof_face', fake_face):
        res3, bad3 = contract(cite_delayed)
    lk = [b for b in bad3 if 'as_of_leak' in str(b.get('item'))]
    check('§D3 延误行值(-2.2,首发2025-06-01)被当时正文引用→as_of_leak',
          len(lk) >= 1 and '2025-06-01' in str(lk[0].get('note')),
          str([str(b.get('note'))[:70] for b in lk[:1]]))


# ═══ §E 任务4: 随包重放面 ═══════════════════════════════════════════
def sec_e():
    print('═══ §E 随包重放: SHA/原问/裁决链/摘要/重放命令 ═══')
    ia_src = open(os.path.join(ROOT, 'ia_cli.py'), encoding='utf-8').read()
    check('§E1 report 段落盘 question_verbatim.txt(字节=run.question,'
          '在场异字节拒付)',
          "os.path.join(rd, 'question_verbatim.txt')" in ia_src
          and '与 run.question 字节不等' in ia_src)
    check('§E2 归档件集含原问文件(随包直存)',
          "'question_verbatim.txt'" in ia_src.split('_arc_files +=')[1]
          .split(']')[0] if '_arc_files +=' in ia_src else False)
    t_c = os.path.join(TMPG, 'tree_c')
    plan_c = {'regions': {'EA': {'dimensions': {'policy': [
        {'metric_id': 'ECB_MRO', 'display_name': '欧央行主要再融资利率',
         'frequency': 'daily', 'unit': '%',
         'vintage_semantics': '采集时点族',
         'policy_face': rmp.POLICY_FACE.get('ECB_MRO')}]}}},
        'metrics': ['ECB_MRO'], 'context_metrics': [],
        'cutoff': '2026-11-20',
        'point_anchors': [
            {'kind': 'point', 'label': '最新一期', 'as_of': '2026-11-20',
             'months_before': 0}]}
    snap_c = {'series_store': {
        'ECB_MRO': {'dates': ['2026-05-13'], 'values': [4.0],
                    'frequency': 'daily', 'source': 'test'}}}
    pv_e = rmp.point_values(plan_c, snap_c, t_c)
    md_e = rmp.render_map_report(
        {'run': {'git_head': 'r27gate0', 'git_head_source': 'test'},
         'research_plan': dict(plan_c, map_question=True,
                               point_values=pv_e, dimension_gaps=[],
                               cutoff='2026-11-20'),
         'agent_judgment': {'reader_map': {
             'headline_conclusion': 'x', 'regions': [], 'transmission': [],
             'turnings': [], 'history_periods': []}}},
        {}, {'required': False}, root=t_c)
    check('§E3 重放面四件+可执行命令(SHA/原问/裁决链双记录/摘要)',
          '## 重放(随包可执行)' in md_e
          and '`r27gate0`' in md_e
          and 'question_verbatim.txt' in md_e
          and 'REVISE→UPHELD 时**两条记录都在链**' in md_e
          and 'MAP_REPORT.sha256' in md_e
          and 'ia_cli.py research-one --stage auto' in md_e)
    for p in ('.claude/skills/global-macro-research/SKILL.md',
              '.agents/skills/global-macro-research/SKILL.md'):
        fp = os.path.join(ROOT, p)
        if not os.path.exists(fp):
            # .claude 安装面 gitignored——CI 干净克隆合法缺席(在场性守卫);
            # .agents 仓内跟踪面缺席=真 FAIL
            check(f'§E4 技能面在场守卫({p.split("/")[0]};'
                  '.claude gitignored 缺席合法)',
                  os.path.exists(fp) or p.startswith('.claude'))
            continue
        s = open(fp, encoding='utf-8').read()
        check(f'§E4 SKILL 草稿纪律含两类新 blocked_class({p.split("/")[0]})',
              'map_current_period_missing' in s
              and 'map_current_period_unverified' in s)


def main():
    for sec in (sec_a, sec_b, sec_c, sec_d, sec_e):
        sec()
    n_fail = sum(1 for _, ok, _ in RESULTS if not ok)
    print('\n' + '═' * 60)
    print(f'Audit-R27 门: {len(RESULTS) - n_fail} PASS / {n_fail} FAIL '
          f'(共 {len(RESULTS)} 判据)')
    if n_fail:
        print('失败项: ' + '; '.join(nm for nm, ok, _ in RESULTS
                                     if not ok))
    return 1 if n_fail else 0


if __name__ == '__main__':
    sys.exit(main())
