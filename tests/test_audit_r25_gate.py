#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit-R25(R69)门 — 日常采集保全+历史时点+原问正文+归档重放四任务。

任务1 §A: 同日降级重采集守卫(序列丢失面转存 superseded/,完整可重放面
原位保全;升集/值修订正常覆写且旧档保留;IA_DAILY_ALLOW_OVERWRITE 豁免;
八采集写点接线;最新一期锚按发布频率标过期+读者面⚠过期注记;必要维度
缺失→带缺口草稿交付路径(正式归档仍阻断)。
任务2 §B: 官方发布记录四项实录逐项前一天/当天复测(欧元区2025-03 HICP
速报/终值、美国2025-11 CPI、2025-09 核心 PCE、2025-10/11 工业生产合并
补发)+月首口径统一(_visible_publish 与 _aof_first_pub 同约定)。
任务3 §C: 原问逐字入计划(question_verbatim;内部摘要另存)+正文数字
校验三写法(bp/个基点/中文指标名与代码名)对调拒绝/正确表述放行+首页/
转折表/传导链先后顺序与因果证据一致性。
任务4 §D: 仓内真实工单干净目录归档重放(ARCHIVE_MANIFEST 相对路径+裁决
链+受审字节三处核对)+新版独立归档路径保留旧版+R22/R23/R24 重放回归
件在场。
"""
import hashlib
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
sys.path.insert(0, os.path.join(ROOT, 'scripts', 'research_contract'))

import research_provenance as rp          # noqa: E402
import research_map_planner as rmp        # noqa: E402

RESULTS = []
TMPG = tempfile.mkdtemp(prefix='r25gate_')
ORIG_ENV = dict(os.environ)


def check(name, ok, detail=''):
    RESULTS.append((name, bool(ok), str(detail)[:220]))
    print(('  ✅ ' if ok else ' ❌ ') + name
          + (f' — {detail}' if detail else ''), flush=True)


# ═══ §A 任务1: 同日降级重采集守卫 ═════════════════════════════════════
def sec_a():
    print('═══ §A 采集守卫: 降级转存/完整保全/过期标注/草稿交付 ═══')
    d = os.path.join(TMPG, 'daily_a')
    full = {'date': '20261120',
            'indices': {'SHCOMP': {'close': 3500.0}},
            'series': {'M1': {'dates': ['2026-11-18', '2026-11-19',
                                        '2026-11-20'],
                              'values': [1.0, 2.0, 3.0]},
                       'M2': {'dates': ['2026-11-20'], 'values': [9.0]}}}
    p1, s1, n1 = rp.daily_face_guard_write(d, 'china', '20261120', full)
    check('§A1 首采直写规范文件', s1 == 'first'
          and os.path.basename(p1) == 'china_20261120.json')
    # 降级重采集: M2 序列整条丢失
    degraded = {'date': '20261120',
                'indices': {'SHCOMP': {'close': 3500.0}},
                'series': {'M1': {'dates': ['2026-11-18', '2026-11-19',
                                            '2026-11-20'],
                                  'values': [1.0, 2.0, 3.0]}}}
    p2, s2, n2 = rp.daily_face_guard_write(d, 'china', '20261120', degraded)
    canon = json.load(open(os.path.join(d, 'china_20261120.json'),
                           encoding='utf-8'))
    check('§A2 序列丢失面→degraded_diverted(不覆盖完整档)',
          s2 == 'degraded_diverted' and '丢失' in n2
          and '/superseded/' in p2.replace('\\', '/')
          and 'M2' in canon['series'],
          f'status={s2} note={n2}')
    check('§A3 降级版本保留在 superseded/(采集版本不丢弃)',
          json.load(open(p2, encoding='utf-8')) == degraded)
    # 叶子数退化(同构路径、观测变少)
    shrink = json.loads(json.dumps(full))
    shrink['series']['M1']['dates'] = full['series']['M1']['dates'][:1]
    shrink['series']['M1']['values'] = full['series']['M1']['values'][:1]
    p3, s3, n3 = rp.daily_face_guard_write(d, 'china', '20261120', shrink)
    check('§A4 路径同构叶子缩水→degraded_diverted',
          s3 == 'degraded_diverted' and '叶子' in n3, f'note={n3}')
    # 升集: 新增序列 → 正常覆写+旧档保留
    upgrade = json.loads(json.dumps(full))
    upgrade['series']['M3'] = {'dates': ['2026-11-20'], 'values': [7.0]}
    p4, s4, _ = rp.daily_face_guard_write(d, 'china', '20261120', upgrade)
    canon4 = json.load(open(os.path.join(d, 'china_20261120.json'),
                            encoding='utf-8'))
    sup_files = os.listdir(os.path.join(d, 'superseded'))
    check('§A5 升集覆写规范文件+旧档入 superseded/',
          s4 == 'overwritten_preserved' and 'M3' in canon4['series']
          and len(sup_files) == 3, f'superseded={len(sup_files)} 件')
    # 值修订(结构不变) → 覆写放行
    rev = json.loads(json.dumps(upgrade))
    rev['series']['M1']['values'][-1] = 3.5
    _, s5, _ = rp.daily_face_guard_write(d, 'china', '20261120', rev)
    check('§A6 值修订(结构不变)→覆写放行(检测重算不是覆盖退化)',
          s5 == 'overwritten_preserved')
    # 豁免旗标
    os.environ['IA_DAILY_ALLOW_OVERWRITE'] = '1'
    _, s6, _ = rp.daily_face_guard_write(d, 'china', '20261120',
                                         {'tiny': True})
    canon6 = json.load(open(os.path.join(d, 'china_20261120.json'),
                            encoding='utf-8'))
    os.environ.pop('IA_DAILY_ALLOW_OVERWRITE', None)
    check('§A7 IA_DAILY_ALLOW_OVERWRITE=1→forced 直写(旧档仍保留)',
          s6 == 'forced' and canon6 == {'tiny': True}
          and len(os.listdir(os.path.join(d, 'superseded'))) == 5)
    # superseded 档不冒充规范来源
    sup_sample = sorted(os.listdir(os.path.join(d, 'superseded')))[0]
    check('§A8 superseded 档非规范来源身份(canonical_source_file 拒绝)',
          rp.canonical_source_file('china', sup_sample) is None)
    # 八采集写点接线(结构面: 每采集器守卫调用在场)
    sites = ['china_market_collector', 'ea_market_collector',
             'macro_collector', 'global_market_collector',
             'japan_rate_collector', 'jp_market_collector',
             'shiller_collector', 'rate_expectations']
    wired = [m for m in sites
             if 'daily_face_guard_write' in open(
                 os.path.join(ROOT, 'scripts', m + '.py'),
                 encoding='utf-8').read()
             or (m == 'rate_expectations'
                 and 'daily_face_guard_write' in open(
                     os.path.join(ROOT, 'scripts', m + '.py'),
                     encoding='utf-8').read())]
    check('§A9 八采集写点全部接线 daily_face_guard_write',
          len(wired) == 8, f'缺: {sorted(set(sites) - set(wired))}')
    # ── 最新一期锚过期标注(EA HICP 停 2025-12、as_of 2026-11) ──
    import freshness_policy as fp
    fo = fp.assess_observation_freshness('EA_HICP_YOY', '2025-12-01',
                                         '2026-11-20')
    check('§A10 发布频率过期识别(EA_HICP 月频窗, 末观测2025-12-01)',
          fo['status'] == 'STALE' and fo['lag_days'] > fo['window'],
          f"lag={fo['lag_days']} window={fo['window']}")
    plan = {'regions': {'EA': {'dimensions': {
        'inflation': [{'metric_id': 'EA_HICP_YOY',
                       'display_name': 'HICP同比',
                       'frequency': 'monthly'}]}}},
        'metrics': ['EA_HICP_YOY'], 'context_metrics': [],
        'point_anchors': [
            {'kind': 'point', 'label': '12个月前',
             'as_of': '2025-11-20', 'months_before': 12},
            {'kind': 'point', 'label': '最新一期',
             'as_of': '2026-11-20', 'months_before': 0}]}
    snap = {'series_store': {'EA_HICP_YOY': {
        'dates': ['2025-11-01', '2025-12-01'],
        'values': [2.2, 1.9], 'frequency': 'monthly'}}}
    pv = rmp.point_values(plan, snap, ROOT)
    cell = pv['cells'][0]
    latest = cell['anchors']['最新一期']
    hist = cell['anchors']['12个月前']
    check('§A11 最新一期锚带 freshness=stale+末观测日+滞后天数',
          latest.get('freshness') == 'stale'
          and latest.get('observation_date') == '2025-12-01'
          and latest.get('freshness_lag_days', 0) > 0
          and '过期' in latest.get('freshness_note', ''),
          f"note={latest.get('freshness_note', '')[:60]}")
    check('§A12 历史锚不带过期标(时点差≠采集缺陷)',
          'freshness' not in hist)
    md = rmp.render_map_report(
        {'research_plan': dict(plan, map_question=True,
                               point_values=pv, dimension_gaps=[],
                               cutoff='2026-11-20'),
         'agent_judgment': {'reader_map': {
             'headline_conclusion': 'x', 'regions': [],
             'transmission': [], 'turnings': [],
             'history_periods': []}}},
        {}, {'required': False}, root=ROOT)
    check('§A13 读者面渲染⚠过期:末观测+滞后/窗口四要素',
          '⚠过期:末观测2025-12-01' in md and '天>' in md and '天窗口)' in md,
          next((l for l in md.splitlines() if '⚠过期' in l), '')[:90])
    # ── 草稿交付路径(结构+belt 面) ──
    ia_src = open(os.path.join(ROOT, 'ia_cli.py'), encoding='utf-8').read()
    check('§A14 草稿交付路径在场: 数据面缺口类→draft_delivered+exit 0;'
          '正式归档 belt 同判拒',
          "draft_delivered = (machine_verified and review_ok and"
          " copies_consistent)" in ia_src.replace('\n', ' ')
          .replace('    ', ' ').replace('  ', ' ')
          and "'map_core_dimension_missing'" in ia_src
          and '草稿交付(Audit-R25 任务1)' in ia_src)
    aj_src = open(os.path.join(ROOT, 'scripts', 'agent_judgment.py'),
                  encoding='utf-8').read()
    check('§A15 归档侧草稿 belt: map_core_dimension_missing/map_anchor_'
          'coverage_insufficient 拒正式归档(草稿≠正稿)',
          "'map_core_dimension_missing'" in aj_src
          and "'map_anchor_coverage_insufficient'" in aj_src)


# ═══ §B 任务2: 官方发布记录四项实录逐项复测 ═════════════════════════
def sec_b():
    print('═══ §B 历史时点: 四项实录前一天/当天+月首口径统一 ═══')
    cal = json.load(open(os.path.join(ROOT, 'config',
                                      'release_calendar.json'),
                         encoding='utf-8'))
    check('§B1 日历 v1.4.0+14条目+spec 含 R25 修订记事',
          cal['version'] == '1.4.0' and len(cal['entries']) == 14
          and 'v1.4.0' in cal['spec'] and '2025-12-05' in cal['spec'])

    def vis(mid, od, asof):
        vf, _pub, _b, _n = rmp._aof_first_pub(mid, od, 'monthly')
        return vf is not None and vf <= asof

    import datetime as _dt
    flips = [
        ('EA_HICP_YOY', '2025-03-31', '2025-04-01',
         '速报实录(Eurostat 2-01042025-AP)'),
        ('CPI', '2025-11-30', '2025-12-18', 'BLS 改期实录'),
        ('CORE_CPI', '2025-11-30', '2025-12-18', '同批=同日可见'),
        ('CORE_PCE', '2025-09-30', '2025-12-05', 'BEA 25-46 实录'),
        ('INDPRO', '2025-10-31', '2025-12-23', 'G.17 合并补发'),
        ('INDPRO', '2025-11-30', '2025-12-23', '两观测月同日可见'),
    ]
    for mid, od, pub, why in flips:
        d1 = (_dt.date.fromisoformat(pub)
              - _dt.timedelta(days=1)).isoformat()
        check(f'§B2 {mid}@{od[:7]}: 前一天{d1}不可见/当天{pub}可见({why})',
              not vis(mid, od, d1) and vis(mid, od, pub), f'pub={pub}')
    # EA 两级: 速报/终值分记
    vf, pub, basis, note = rmp._aof_first_pub('EA_HICP_YOY',
                                              '2025-03-31', 'monthly')
    check('§B3 EA 2025-03 HICP 速报2025-04-01/终值2025-04-16 两级分记'
          '(官方实录,快报当时可知)',
          vf == '2025-04-01' and pub == '2025-04-16'
          and basis.startswith('calendar:RC-EA-HICP-2025M03')
          and '快报 2025-04-01' in note, f'note={note[:70]}')
    # 9月核心PCE实录优先于保守界
    _v, _p, b4, _ = rmp._aof_first_pub('CORE_PCE', '2025-09-30', 'monthly')
    check('§B4 9月核心PCE 实录2025-12-05 优先于 REST 保守界2026-01-22',
          _v == '2025-12-05' and 'PCE-SEP' in b4
          and 'REST-CONSERVATIVE' not in b4, f'basis={b4[:50]}')
    # 月首口径统一: _visible_publish(月频月末观测)与 _aof_first_pub 同判
    for mid, od in [('EA_HICP_YOY', '2025-03-31'),
                    ('CPI', '2025-11-30'),
                    ('CORE_PCE', '2025-09-30'),
                    ('INDPRO', '2025-10-31')]:
        pv1, b1 = rmp._visible_publish(mid, 'monthly', od)
        vf2, _p2, _b2, _ = rmp._aof_first_pub(mid, od, 'monthly')
        check(f'§B5 {mid}@{od[:7]} 月首口径统一(_visible_publish=='
              f'_aof_first_pub 首见日)', pv1 == vf2, f'{pv1} vs {vf2}')
    # 日频不归一(逐日实录窗按原观测日)
    pv_d, _ = rmp._visible_publish('DFF', 'daily', '2025-10-15')
    check('§B6 日频观测不月首归一(口径分记)',
          pv_d is None or not str(pv_d).endswith('-01'))
    # 无法确认当时值→不虚构官方实录;规则推定须如实标注「推定」
    _u = rmp._visible_publish('XX_NO_EVIDENCE', 'monthly', '2026-01-31')
    check('§B7 无实录条目→规则推定且 basis 如实标「推定」(不虚构实录)',
          _u[0] is not None and '推定' in (_u[1] or '')
          and '实录' not in (_u[1] or ''), str(_u))
    # 日本: 市场月均留在市场观测(decision=None),政策目标宣布值另列;
    # 美欧中决策面带官方决议/生效惯例(decision_kind)
    jp_dims = dict((rmp.REGION_DIMENSION_METRICS or {}).get('JP')
                   or {}).get('policy') or []
    jp_ids = [m for m, _lab in jp_dims]
    check('§B8 日本双轨分列: JP_POLICY_RATE(月均·市场观测,decision=None)'
          '+JP_POLICY_TARGET(宣布值另列);美欧中决策面带官方惯例',
          'JP_POLICY_RATE' in jp_ids and 'JP_POLICY_TARGET' in jp_ids
          and not (rmp.POLICY_FACE.get('JP_POLICY_RATE') or {}).get(
              'decision')
          and all((rmp.POLICY_FACE.get(m) or {}).get('decision_kind')
                  for m in ('DFEDTARU', 'ECB_MRO', 'CN_POLICY_OVERNIGHT')),
          f'JP policy ids={jp_ids}')


# ═══ §C 任务3: 原问逐字+正文三写法+跨面一致性 ═══════════════════════
def sec_c():
    print('═══ §C 原问入计划/三写法对调拒绝/跨面一致性 ═══')
    import research_orchestrator as ro
    from judgment_contract import _map_checks
    Q = ('给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在'
         '12个月前、3个月前和最新一期,分别处于什么增长、通胀和货币'
         '政策环境?过去一年最重要的三个转折,传导机制怎样?历史上'
         '哪些时期结构最像,随后3、6、12个月又怎样?')
    reg = json.load(open(os.path.join(ROOT, 'config',
                                      'metric_registry.json'),
                         encoding='utf-8'))
    ent = ro.map_entities(Q, reg)
    plan = rmp.plan_map(Q, ent, reg.get('by_id') or {}, '2026-11-20')
    check('§C1 plan.question_verbatim 逐字==原问(字节级)',
          plan.get('question_verbatim') == Q)
    check('§C2 内部摘要另存(question_summary≠原文且自声明以原文为准)',
          plan.get('question_summary') != Q
          and 'question_verbatim' in plan.get('question_summary', ''))
    check('§C3 跨面一致性标记入计划(cross_face_consistency=r25)',
          plan.get('cross_face_consistency') == 'r25')

    trio = {'status': 'ok',
            'chg_bp': {'UST_10Y': 104.0, 'TIPS_10Y': 97.0,
                       'BEI_10Y': 7.0},
            'chg_bp_12m': {'UST_10Y': 97.0, 'TIPS_10Y': 104.0,
                           'BEI_10Y': -7.0},
            'window': {}}
    base_plan = {'map_question': True, 'metrics': [], 'context_metrics': [],
                 'us_rates_trio': trio, 'point_anchors': [],
                 'turning_candidates': {'candidates': []},
                 'cross_face_consistency': 'r25',
                 'regions': {}}
    face = {'series_store': {}}

    def mk_rm(headline, turnings=None, chains=None):
        return {'headline_conclusion': headline,
                'regions': [], 'transmission': chains or [],
                'turnings': turnings or [], 'history_periods': []}

    def run(headline, turnings=None, chains=None):
        res = _map_checks({'reader_map': mk_rm(headline, turnings, chains)},
                          face, {'research_plan': base_plan})
        return [c for c in res
                if c.get('status') != 'VERIFIED'
                and ('bp' in c['item'] or 'cross_face' in c['item'])]

    # 对调拒绝×三写法: 年度窗真值 名义+97/实际+104/盈亏平衡−7,
    # 对调=名义+104/实际+97(两值都在池内,池核放行,归属核拒绝)
    swapped = [
        ('bp 写法', '过去一年美债名义+104bp、实际+97bp,盈亏平衡-7bp'),
        ('个基点写法', '过去一年美债名义上行104个基点、实际上行97个基点'),
        ('中文指标名', '过去一年十年期美债上行104个基点,十年期TIPS上行'
         '97个基点'),
        ('代码名', '过去一年UST_10Y +104bp,TIPS_10Y +97bp'),
    ]
    for label, txt in swapped:
        bads = run(txt)
        check(f'§C4 对调拒绝({label}): 名义+104↔实际+97 → CONTRADICTED',
              any('bp_attributed' in b['item']
                  and b['status'] == 'CONTRADICTED' for b in bads),
              str([b['note'][:60] for b in bads][:1]))
    # 正确表述放行×三写法(年度窗真值: 名义+97=实际+104+盈亏平衡−7;
    # 个基点/中文用方向词承载符号——上行97/104、下行7)
    correct = [
        ('bp 写法', '过去一年美债名义+97bp、实际+104bp、盈亏平衡-7bp'),
        ('个基点写法', '过去一年美债名义上行97个基点、实际上行104个'
         '基点、盈亏平衡下行7个基点'),
        ('中文指标名', '过去一年十年期美债上行97个基点、十年期TIPS上行'
         '104个基点、盈亏平衡通胀下行7个基点'),
        ('代码名', '过去一年UST_10Y +97bp、TIPS_10Y +104bp、'
         'BEI_10Y -7bp'),
    ]
    for label, txt in correct:
        bads = run(txt)
        check(f'§C5 正确表述放行({label})',
              not [b for b in bads
                   if 'headline_conclusion.bp' in b['item']],
              str([b['note'][:70] for b in bads][:1]))
    # 跨面: 同一对日期相反次序主张 → CONTRADICTED
    contra_chains = [{'chain_id': 'CH1', 'title': 't', 'links': [
        {'observed_fact': 'ECB 首加(2026-06-11)晚于 Fed(2026-09-16)',
         'causal_hypothesis': '', 'competing_explanation': '',
         'distinguishing_metric': 'EA_HICP_YOY'}]}]
    bads = run('ECB 首加(2026-06-11)早于 Fed(2026-09-16),先后可判。',
               chains=contra_chains)
    check('§C6 跨面日期次序矛盾(首页早于/传导链晚于)→CONTRADICTED',
          any('date_order' in b['item']
              and b['status'] == 'CONTRADICTED' for b in bads),
              str([b['note'][:70] for b in bads][:1]))
    ok_chains = [{'chain_id': 'CH1', 'title': 't', 'links': [
        {'observed_fact': 'ECB 首加(2026-06-11)早于 Fed(2026-09-16)97天',
         'causal_hypothesis': '', 'competing_explanation': '',
         'distinguishing_metric': 'UST_10Y'}]}]
    res = _map_checks({'reader_map': mk_rm(
        'ECB 首加(2026-06-11)早于 Fed(2026-09-16),先后可判。',
        chains=ok_chains)}, face, {'research_plan': base_plan})
    check('§C7 一致次序主张→VERIFIED(日期次序主张一致)',
          any('date_order' in c['item'] and c['status'] == 'VERIFIED'
              for c in res)
          and not [c for c in res if 'date_order' in c['item']
                   and c['status'] != 'VERIFIED'])
    # 传导链证据绑定: 无引擎指标 → 拦
    ghost_chains = [{'chain_id': 'CH9', 'title': 't', 'links': [
        {'observed_fact': 'X 影响 Y', 'causal_hypothesis': '',
         'competing_explanation': '',
         'distinguishing_metric': 'GHOST_METRIC'}]}]
    bads = run('一句话。', chains=ghost_chains)
    check('§C8 传导链区分指标无引擎绑定→NOT_VERIFIED',
          any('chain_evidence' in b['item'] for b in bads),
          str([b['note'][:60] for b in bads][:1]))
    # 转折表指标同源: 指标不在计划/候选/快照 → 拦
    bads = run('一句话。', turnings=[{'metric_id': 'GHOST_TURN', 'date':
                                     '2026-05', 'first_mover': 'x',
                                     'follow_or_diverge': 'y',
                                     'narrative': ''}])
    check('§C9 转折表指标不同源→NOT_VERIFIED',
          any('turning_source' in b['item'] for b in bads))


# ═══ §D 任务4: 干净目录归档重放+新版独立路径 ═══════════════════════
def sec_d():
    print('═══ §D 归档重放: 相对路径/裁决链/受审字节+旧版保全 ═══')
    import agent_judgment as aj
    src = os.path.join(ROOT, 'docs', 'autonomous-rd', 'r24-evidence',
                       'acceptance')
    man = json.load(open(os.path.join(src, 'ARCHIVE_MANIFEST.json'),
                         encoding='utf-8'))
    rj = json.load(open(os.path.join(src, 'report.json'), encoding='utf-8'))
    env = json.load(open(os.path.join(src, 'AGENT_SEAT_ENVELOPE.json'),
                         encoding='utf-8'))
    vf_path = os.path.join(ROOT, 'docs', 'autonomous-rd', 'r24-evidence',
                           'session', 'run_question_verbatim.txt')
    # §D1 旧档问句链: manifest==run==envelope 三处逐字一致 + 原问另存件
    # 在场(R24 档记录的问句是改写版 98字≠原文169字——R25 起 plan.
    # question_verbatim 逐字入计划,新档由 §C1 面收口该缺口)
    q3 = (man.get('question') == (rj.get('run') or {}).get('question')
          == env.get('question'))
    vf = open(vf_path, encoding='utf-8').read().strip()
    check('§D1 旧档问句三处一致(manifest==run==envelope)+原问另存件在场'
          '(R24 记录=改写版如实保留;R25 新档补齐逐字面)',
          q3 and bool(man.get('question')) and vf
          and len(vf) > len(man.get('question') or ''),
          f'vf={len(vf)}字 vs 档内={len(man.get("question") or "")}字')
    # 干净目录重放: 复制归档包到临时目录,全按相对路径核
    play = os.path.join(TMPG, 'replay_d')
    shutil.copytree(src, play)
    vchain = man.get('verdict_chain') or []
    ok_files = all(
        os.path.isfile(os.path.join(play, e['file']))
        and hashlib.sha256(
            open(os.path.join(play, e['file']), 'rb').read()
        ).hexdigest()[:16] == e['sha256']
        for e in vchain)
    check('§D2 裁决链按 ARCHIVE_MANIFEST 相对路径解析+sha256 逐件吻合'
          '(干净目录)', ok_files and len(vchain) >= 2,
          f'链长={len(vchain)}')
    names = {e['file'] for e in vchain}
    preds = {e.get('predecessor') for e in vchain if e.get('predecessor')}
    src_rels = {e['source_rel'] for e in vchain}
    check('§D3 裁决链闭合(唯一名+predecessor 全在源集)',
          len(names) == len(vchain) and preds <= src_rels)
    latest_v = json.load(open(os.path.join(
        play, sorted(e['file'] for e in vchain)[-1]), encoding='utf-8'))
    sha_file = open(os.path.join(play, 'MAP_REPORT.sha256'),
                    encoding='utf-8').read().split()[0]
    sha_full = hashlib.sha256(
        open(os.path.join(play, 'MAP_REPORT.md'), 'rb').read()).hexdigest()
    check('§D4 受审字节绑定三处: manifest.map_content==内容段复算==裁决'
          '绑定;全文sha==旁挂件',
          man.get('map_content_sha256')
          == aj.map_report_content_sha(play)
          == latest_v.get('map_report_sha256')
          and sha_file == sha_full,
          f"{str(man.get('map_content_sha256'))[:12]}")
    check('§D5 旧版保全: R22/R23/R24 重放回归件在场',
          os.path.isdir(os.path.join(
              ROOT, 'docs', 'autonomous-rd', 'r22-evidence',
              'acceptance'))
          and os.path.isdir(os.path.join(
              ROOT, 'docs', 'autonomous-rd', 'r23-evidence',
              'acceptance'))
          and os.path.isdir(src))
    # §D6-§D8 正式入口重放: 引擎树(config+裁决链+冻结快照)+rd 复本
    T = os.path.join(TMPG, 'tree_d')
    os.makedirs(os.path.join(T, 'data', 'daily'))
    os.makedirs(os.path.join(T, 'config'))
    for fn in ('metric_registry.json', 'release_calendar.json'):
        shutil.copy(os.path.join(ROOT, 'config', fn),
                    os.path.join(T, 'config', fn))
    vd = os.path.join(T, 'audit', 'semantic_review', '20261120')
    os.makedirs(vd)
    for e in vchain:
        shutil.copy(os.path.join(play, e['file']),
                    os.path.join(vd, os.path.basename(e['source_rel'])))
    store = {}
    for st in rj.get('steps') or []:
        nm = st.get('step') or ''
        if nm.startswith('S4_history_'):
            ser = ((st.get('envelope') or {}).get('data')
                   or {}).get('series') or {}
            if ser.get('dates'):
                store[nm[11:]] = {'dates': list(ser['dates']),
                                  'values': list(ser['values'])}
    with open(os.path.join(T, 'data', 'daily',
                           'research_snapshot_20261120.json'), 'w',
              encoding='utf-8') as f:
        json.dump({'snapshot_id': 'research_snapshot_20261120',
                   'series_store': store}, f)
    rd = os.path.join(TMPG, 'rd_d')
    shutil.copytree(play, rd)

    def cli_arc(arc):
        r = subprocess.run(
            [sys.executable, 'ia_cli.py', 'research-one', '--stage',
             'archive', '--report-dir', rd, '--engine-root', T,
             '--archive-dir', arc],
            cwd=ROOT, capture_output=True, text=True, timeout=900)
        try:
            data = json.loads(r.stdout)
        except Exception:
            data = {'raw': ((r.stdout or '') + (r.stderr or ''))[-200:]}
        return r.returncode, data

    arc1 = os.path.join(TMPG, 'arc_d_v1')
    rc1, d1 = cli_arc(arc1)
    man1 = {}
    if rc1 == 0:
        man1 = json.load(open(os.path.join(arc1, 'ARCHIVE_MANIFEST.json'),
                              encoding='utf-8'))
    check('§D6 干净树正式入口重放归档: 确定性(内容摘要/地图绑定/问句/'
          '裁决链逐位==原档)', rc1 == 0
          and man1.get('content_sha256') == man.get('content_sha256')
          and man1.get('map_content_sha256')
          == man.get('map_content_sha256')
          and man1.get('question') == man.get('question')
          and [e['sha256'] for e in man1.get('verdict_chain') or []]
          == [e['sha256'] for e in vchain],
          f'rc={rc1} ' + (str((d1.get('data') or {})
                              .get('blocked'))[:60] if rc1 else 'ok'))
    rc2, d2 = cli_arc(arc1)
    check('§D7 归档目录已存在→拒(append-only 不覆盖旧版)',
          rc2 != 0 and (d2.get('data') or {}).get('blocked')
          == 'archive_exists', f'rc={rc2}')
    arc3 = os.path.join(TMPG, 'arc_d_v2')
    rc3, d3 = cli_arc(arc3)
    keep1 = os.path.isfile(os.path.join(arc1, 'ARCHIVE_MANIFEST.json'))
    check('§D8 新版独立归档路径→放行且旧版原样保留(两版并存)',
          rc3 == 0 and keep1, f'rc={rc3}')


sec_a()
sec_b()
sec_c()
sec_d()
n_fail = sum(1 for _, okk, _ in RESULTS if not okk)
print(f'\n判定: {len(RESULTS) - n_fail} PASS / {n_fail} FAIL')
if n_fail:
    print('失败项:', ', '.join(n for n, okk, _ in RESULTS if not okk))
sys.exit(0 if not n_fail else 1)
