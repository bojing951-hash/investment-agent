#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R43: 检查面预处理+遮罩补行测试面(RDG-20261116-013 A 族硬化)。

§A check_text 入口预处理: HTML 注释(生成头/校验头)/报告头元数据行/
   独立行 JSON provenance 不进子句域;未闭合注释与坏 JSON 行保守保留。
§B 遮罩表补行: 引用ID(art_hex)/内部引用序号(论点#N/预测#N)/紧凑
   ISO 日期窗/子句首列表序号。
§C 月-日遮罩日组必选: 「11月3.8775%」不再吞「3」出「8775%」碎片。
§D 端到端(era 20261114 真实形态嵌入): 构造物数字零入裁决面,叙事照判。
§E 变异自证: 预处理恒等/遮罩行拆 → 本套件红(锁有牙)。

真实形态来源: LIVE V1/V2 周报(R41 定性件 A 族证据),模型名以
「模型名」占位(厂商词红线;机制与模型名无关)。全合成可跑 CI。
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

from migration_matrix import load_era                    # noqa: E402
from research_contract import text_consistency as tc      # noqa: E402

snap, prior, thr = load_era('20261114')     # DXY=103.41
PASS = FAIL = 0


def check(name, ok, detail=''):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f'  ✅ {name}')
    else:
        FAIL += 1
        print(f'  ❌ {name}' + (f'  [{detail}]' if detail else ''))


def toks(clause):
    """遮蔽后子句 token 原文集。"""
    return [t['raw'].strip() for t in
            tc._extract_tokens(tc._masked_clause(
                clause, tc._find_alias(clause)))]


def run(text):
    return tc.check_text(text, snapshot=snap, thresholds=thr,
                         prior_anchors=prior)


def contra_tokens(r):
    return {str(c.get('token')).strip()
            for c in r['checks'] if c['status'] == 'CONTRADICTED'}


def unbound_tokens(r):
    out = set()
    for u in (r.get('unbound') or []):
        v = u.get('raw') if isinstance(u, dict) else u
        if v:
            out.add(str(v).strip())
    return out


# 真实形态(V2 周报原文;生成头模型名→占位)
COMMENT_GEN = '<!-- 生成: 2026-11-08 16:22:44 | 模型名 | investment-agent -->'
COMMENT_VAL = '<!-- 校验20261108: FAIL(10项警告) 详情: logs/validation_20261108.log -->'
HEADER_TITLE = '# 投资周报 20261102–20261108'
HEADER_TIME = ('生成时间：2026-11-08（数据截至2026-11-06/08数据包，'
               'Gate A: PASS）')
JSON_ROW = ('{"id":1,"status":"已失效","confidence":1,'
            '"note":"实际利率2.60%(2026-11-05)≥2.5%连续三周以上,失效条件满足",'
            '"evidence":[{"metric":"macro.data.TIPS_10Y.value","value":2.6,'
            '"obs_date":"2026-11-05","mechanism":"利率与流动性"}]}')

print('== R43-§A 检查面预处理(注释/报告头行/JSON provenance) ==')

# A1 生成头/校验头注释整体剥离: 注释数字不进 token 域,同句叙事照常
pp = tc._checkface_preprocess(
    COMMENT_GEN + '\n美元指数DXY收于102.30，周涨0.86%。\n' + COMMENT_VAL)
check('A1a 生成头/校验头注释剥离后不在文本',
      COMMENT_GEN not in pp and COMMENT_VAL not in pp)
check('A1b 注释内数字(16:22:44/5.3 类)零 token,叙事值保留',
      toks('美元指数DXY收于102.30，周涨0.86%。')
      == ['102.30', '0.86%'],
      str(toks('美元指数DXY收于102.30，周涨0.86%。')))

# A2 报告头元数据行(标题+生成时间)置换: 「/08数据包」碎片根除
pp2 = tc._checkface_preprocess(
    HEADER_TITLE + '\n\n' + HEADER_TIME + '\n美元指数DXY收于102.30。')
check('A2 头两行(标题/生成时间)置换为空白,正文保留',
      HEADER_TITLE.strip() not in pp2 and '生成时间' not in pp2
      and '美元指数DXY收于102.30' in pp2)

# A3 JSON provenance 行置换;坏 JSON 行保守保留
pp3 = tc._checkface_preprocess(JSON_ROW)
check('A3a 可解析 JSON 对象行置换', JSON_ROW.strip() not in pp3)
pp4 = tc._checkface_preprocess('散户入场 {oops 2.5 未闭合')
check('A3b 非 JSON 行原样保留(诚实保守)', '2.5' in pp4 and 'oops' in pp4)

# A4 未闭合注释保守保留
pp5 = tc._checkface_preprocess('序列 <!-- 未闭合 1.5')
check('A4 未闭合注释不剥离(保守)', '1.5' in pp5)

print('== R43-§B 遮罩表补行(引用ID/#N 序号/紧凑日期窗/列表序号) ==')

# B1 引用ID(V1 真实形态): 9456078 不入 token,叙事值在
t1 = toks('需求走弱[art_9456078c93b846df]）→美元指数102.30')
check('B1 引用ID遮蔽,102.30 保留',
      '9456078' not in t1 and '102.30' in t1, str(t1))

# B2 内部引用序号(V2 真实形态)
t2 = toks('预测#2裁决为已命中（详见第七节），论点#3升级为确认。')
check('B2 论点/预测#N 序号遮蔽', '2' not in t2 and '3' not in t2, str(t2))

# B3 紧凑 ISO 日期窗(非头行形态)
t3 = toks('期间20261102–20261108风险偏好回升。')
check('B3 紧凑日期窗遮蔽', '20261102' not in t3
      and '20261108' not in t3, str(t3))

# B4 子句首列表序号(V2 真实形态): 序号死,句内真值活
t4 = toks('1. 美伊博弈剧烈摇摆主导油价，WTI期货周-12.76%至90.83美元。')
check('B4 序号遮蔽,-12.76%/90.83 保留',
      '1.' not in [x for x in t4] and '-12.76%' in t4
      and '90.83' in t4, str(t4))

# B5 反误杀: 小数不受序号遮蔽牵连
t5 = toks('10月CPI同比3.5%，次月升至3.8775%。')
check('B5 小数 3.5%/3.8775% 不吞(反误杀)', '3.5%' in t5
      and '3.8775%' in t5, str(t5))

print('== R43-§C 月-日日组必选(小数误切分根治) ==')

# C1 V1 真实句: 修复前 masked='    路径从    .8775%升至        .33%'
t6 = toks('期货隐含路径从11月3.8775%升至2027年5月4.33%')
check('C1 双碎片(8775%/33%)根除,完整值在场',
      '8775%' not in t6 and '33%' not in t6
      and '3.8775%' in t6 and '4.33%' in t6, str(t6))

# C2 日组带「日」仍遮蔽;数值断言不受影响
t7 = toks('10月15日当周初请失业金人数22.1万人。')
check('C2 10月15日整遮,22.1 在场', '10' not in t7 and '15' not in t7
      and '22.1' in t7, str(t7))

# C3 月无日: 只遮月
t8 = toks('10月CPI同比0.9%，11月PPI同比5.0%。')
check('C3 无日月形只遮月,数值断言保留',
      '10' not in t8 and '11' not in t8 and '0.9%' in t8
      and '5.0%' in t8, str(t8))

print('== R43-§D 端到端(era 20261114 真实形态嵌入) ==')

# D1 构造物密集文本: 唯一叙事错值(DXY 报 99.99≠快照 103.41)应 CONTRA;
# 构造物数字零入裁决面(CONTRA+unbound)
D1_TEXT = '\n'.join([
    COMMENT_GEN, '', HEADER_TITLE, '', HEADER_TIME, '',
    '1. 美伊博弈主导油价，WTI期货周-12.76%至90.83美元。',
    '需求走弱[art_9456078c93b846df]）→美元指数DXY报99.99。',
    '期货隐含路径从11月3.8775%升至2027年5月4.33%。',
    JSON_ROW, '',
])
r1 = run(D1_TEXT)
ct = contra_tokens(r1) | unbound_tokens(r1)
check('D1a 构造物数字零入裁决面(16/22/44/1./9456078/8775%/2.6/1 等)',
      not (ct & {'16', '22', '44', '1.', '9456078', '8775%',
                 '33%', '2.6', '2.60%', '1', '20261108'}),
      str(sorted(ct)))
check('D1b 叙事错值照判(DXY 99.99 CONTRA)',
      any(c.get('metric') == 'DXY' and c['status'] == 'CONTRADICTED'
          for c in r1['checks']))

# D2 构造物剥离不改正确叙事的裁决(正位值+带语境)
r2 = run(COMMENT_GEN + '\n美元指数DXY收于103.41。')
check('D2 正位叙事值不受预处理影响(零 CONTRA)',
      not contra_tokens(r2))

print('== R43-§E 变异自证(锁有牙) ==')

# E1 预处理恒等变异 → 构造物数字回涌(红)
orig_pre = tc._checkface_preprocess
try:
    tc._checkface_preprocess = lambda x: x
    rm = run(D1_TEXT)
    ctm = contra_tokens(rm) | unbound_tokens(rm)
    check('E1 预处理恒等→构造物数字回涌(变异红)',
          bool(ctm & {'16', '22', '44', '9456078', '2.6', '1'}), str(
              sorted(x for x in ctm
                     if x in {'16', '22', '44', '9456078', '2.6', '1'})))
finally:
    tc._checkface_preprocess = orig_pre

# E2 遮罩行拆(引用ID/序号/日期窗) → B 面形态回涌(红)
orig_pats = tc._STRUCT_PATTERNS
try:
    tc._STRUCT_PATTERNS = [p for p in orig_pats
                           if not any(s in p.pattern
                                      for s in ('art_', '#\\s*', '20261102',
                                                '周报', '\\d{8}', '^\\d{1,2}'))]
    check('E2 遮罩行拆→引用ID/序号/日期窗回涌(变异红)',
          '9456078' in toks('需求走弱[art_9456078c93b846df]）→美元指数102.30')
          or '1.' in toks('1. 美伊博弈主导油价。')
          or '20261102' in toks('期间20261102–20261108风险偏好回升。'))
finally:
    tc._STRUCT_PATTERNS = orig_pats

# E3 月-日日组回退变异(日? 可选) → 碎片回涌(红)
old_month = re.compile(r'\d{1,2}\s*月(?:\d{1,2}\s*日?)?')
try:
    tc._STRUCT_PATTERNS = [old_month if '月(?:' in p.pattern else p
                           for p in orig_pats]
    tm = toks('期货隐含路径从11月3.8775%升至2027年5月4.33%')
    check('E3 日组可选回退→碎片 8775% 回涌(变异红)',
          '8775%' in tm, str(tm))
finally:
    tc._STRUCT_PATTERNS = orig_pats

print(f'\nR43 判定: {PASS} PASS / {FAIL} FAIL')
sys.exit(1 if FAIL else 0)
