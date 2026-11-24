# -*- coding: utf-8 -*-
"""rc12: EA_HICP_YOY 发布规则两口径登记(Audit-R32 A round1; 只读)。
用法: /usr/bin/python3 -I rc12_hicp_rules.py <snapshot.json> <run_dir>
背景: 受审稿在传导面政策环写「欧央行决议前最近可见 HICP=2026-04/2026-07 观测
(推定发布 2026-05-16/2026-08-16; 2026-08 观测 3.2 推定发布于 2026-09-16、决议时点尚未可见)」,
采用的是注册表 release_semantics(次月中旬终值)+RELEASE_RULES(月末+16天)口径——已比对一致(见 ④政策面)。
但同一受审稿的历史段(2023-10)与引擎『当时可知面』采用两级发布规则
(快报=观测月末当日可见(推定); 终值=月末+16日)。本脚本按两级规则重算决议时点最近可见观测,
作为口径分歧登记(ok='NA', 非数值比对): 若按两级规则, 两次欧央行决议前最近可见均为持平 2026-05 高点的月份。
所有记录 note 带 [rc12] 标记: 重跑前 /usr/bin/python3 -I rc_clean_mark.py '[rc12] '
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rc_lib as L
import rc_points as P

snap = L.load(sys.argv[1]); RUN = sys.argv[2]
cal = L.load(os.path.join(RUN, 'root_overlay', 'config', 'release_calendar.json'))
reg = L.load(os.path.join(RUN, 'root_overlay', 'config', 'metric_registry.json'))
F = L.Face(snap, cal)
aj = L.load(os.path.join(RUN, 'agent_judgment.json'))

S4 = '④政策面'
_add = P.add
P.add = lambda section, src, computed, reported, ok, note='', where='': _add(
    section, src, computed, reported, ok, note='[rc12] ' + note, where=where)

NAME = 'EA_HICP_YOY'


def vis_two_level(name, asof):
    """两级发布规则: 日历实录条目优先(RC-EA-HICP-*: 快报日=first_publish_on_or_after);
    无条目则快报=观测月末当日(推定)。返回截止日前可见的最新观测。"""
    out = None
    for d, v in F.series(name):
        if d > asof:
            break
        pub, basis = L.release_date(F, name, d)
        if not basis.startswith('calendar:'):
            pub, basis = L.month_end(d[:7]), 'rule:推定(快报月末)'
        if pub <= asof:
            out = {'obs_date': d, 'value': v, 'pub_date': pub, 'basis': basis}
    return out


# 1) 注册表规则文本 + 受审稿历史段所用口径(字符串在场性)
meta = None
for m in reg['metrics']:
    if m.get('metric_id') == NAME:
        meta = m
sem = meta['release_semantics'] if meta else ''
P.add('杂项(引用/日历/结构)', 'metric_registry.metrics[EA_HICP_YOY].release_semantics 含「次月中旬终值」/「保守标注」; 受审稿历史段(2023-10)含「月末快报口径,当日可见」',
      [sem, '次月中旬终值' in sem, '保守标注' in sem],
      ['Eurostat月度HICP(次月中旬终值); …保守标注', True, True],
      '次月中旬终值' in sem and '保守标注' in sem,
      note='注册表口径=终值(月末+16天,保守标注); 引擎历史面另有两级发布规则(快报=观测月末当日可见,推定)——同档两口径并存',
      where='root_overlay/config/metric_registry.json / history_periods[2023-10].other_regions_sync')

hp = [h for h in aj['reader_map']['history_periods'] if h['judgment_cutoff_ym'] == '2023-10'][0]
P.add('杂项(引用/日历/结构)', 'history_periods[2023-10].other_regions_sync "欧元区HICP同比2023-10为2.9(月末快报口径,当日可见…)" 两级规则: 快报日=2023-10-31 <= 截止 2023-10-31',
      {'value_2023-10': F.at(NAME, '2023-10-01'), 'flash_rule_date': L.month_end('2023-10'), 'cutoff': '2023-10-31', 'visible': True},
      {'value_2023-10': 2.9, 'flash_rule_date': '2023-10-31', 'cutoff': '2023-10-31', 'visible': True},
      F.at(NAME, '2023-10-01') == 2.9 and '月末快报口径,当日可见' in hp['other_regions_sync'],
      note='受审稿历史段采用两级规则(与引擎当时可知面一致)')

# 2) 两次欧央行决议日: 两口径并列
JUDG = {'2026-06-11': ('2026-04', 3.0, '2026-05-16'), '2026-09-10': ('2026-07', 2.9, '2026-08-16')}
for dec in ('2026-06-11', '2026-09-10'):
    a = L.visible_latest(F, NAME, dec)          # 注册表/RELEASE_RULES: 月末+16
    b = vis_two_level(NAME, dec)                # 历史面两级规则: 快报=观测月末
    jo, jv, jp = JUDG[dec]
    comp_reg = [a['obs_date'][:7], a['value'], a['pub_date']]
    P.add(S4, 'EA_HICP_YOY 决议时点最近可见观测——注册表口径(月末+16天; 受审稿所述口径)', comp_reg, [jo, jv, jp],
          comp_reg == [jo, jv, jp], note='受审稿所述口径下的复算(与 ④政策面既有记录同值)',
          where='M1.step2 / TR1.step2 / turning_supplement 决议 %s' % dec)
    comp_two = [b['obs_date'][:7], b['value'], b['pub_date'], b['basis']]
    P.add(S4, 'EA_HICP_YOY 决议时点最近可见观测——引擎历史面两级发布规则口径(快报=观测月末当日可见,推定)', comp_two, [jo, jv, jp, 'rule(月末+16)'],
          'NA',
          note=('口径分歧登记(非数值比对): 两级规则下决议 %s 前最近可见为 %s 观测 %s(快报推定 %s), 与受审稿(注册表口径 %s 观测 %s)不同; '
                '%s。序列值为最新修订值,当时快报值不可回溯。') % (
              dec, b['obs_date'][:7], b['value'], b['pub_date'], jo, jv,
              ('该值持平 2026-05 高点 3.2——受审稿「低于 2026-05 高点」的欧央行一腿在此口径下不成立'
               if dec == '2026-09-10' and b['value'] == 3.2 else
               ('该值处上行段(与受审稿对首次决议「处上行段」的方向判断一致, 仅观测月/数值不同)'
                if dec == '2026-06-11' else '该值处上行段(与受审稿方向一致)'))),
          where='M1.step2 / TR1.step2 决议 %s(两级规则对照)' % dec)
    print(dec, '| 注册表口径', comp_reg, '| 两级规则', comp_two)

# 3) 受审稿相应原句在场性(便于操作席定位)
txt = aj['l3']['mechanism_chains'][0]['links'][1]['text']
P.add('杂项(引用/日历/结构)', '受审稿 M1.step2 含「2026-08 观测 3.2 按引擎规则推定发布于 2026-09-16、决议时点尚未可见」与「对美联储与欧央行的动机环证据减弱」',
      [True, True], [True, True],
      '2026-08 观测 3.2 按引擎规则推定发布于 2026-09-16、决议时点尚未可见' in txt and '对美联储与欧央行的动机环证据减弱' in txt,
      note='原句定位(MINOR 条目出处)', where='agent_judgment.l3.mechanism_chains[0].links[1].text')

print('tally', P.tally())
