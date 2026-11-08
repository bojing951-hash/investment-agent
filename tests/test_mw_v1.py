#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MW-V1(2026-11-08 章程校准) 回归套件。

覆盖四组修复的契约面:
① Gate B 截断修复: 真实11-08报告句式(涨跌幅%桥+数值)不再被回溯截断成错值
   (VIX "+32.03%至25.64"旧正则捕获"32.0"); 顿号枚举窗口;
② JGB 期限绑定: 概念"JGB 10Y"检索不再首中JGB2Y(计分制: 命中词数→display命中);
③ CN宏观事实归一: china采集档macro节进fact_engine(月度'YYYY-MM'锚月首+calc披露);
④ 金双载体方向核验: GOLD_F/GLD周涨幅符号相反→DEGRADED(sign_match恒真缺陷修复);
⑤ 越位零件下线: 周报prompt/热加载prompt不含状态块指令; generate_report签名收窄;
   generate_weekly_report不调用apply_status_updates(E2E层由三套件反转断言覆盖)。

数据纪律: 引用句取自真实2026-11-08报告存档; 合成值显式标注[示意]。
"""
import inspect
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
for p in (ROOT, os.path.join(ROOT, 'scripts')):
    if p not in sys.path:
        sys.path.insert(0, p)

import data_validator as dv            # noqa: E402
import e2eb_query_mapper as qm         # noqa: E402
import fact_engine as fe               # noqa: E402
import report_generator as rg          # noqa: E402

PASSED = []
FAILED = []


def check(name, cond, detail=''):
    (PASSED if cond else FAILED).append((name, detail))
    print(('  ✅ ' if cond else '  ❌ ') + name + (f' [{detail}]' if not cond and detail else ''))


print('══ ① Gate B 截断修复(真实11-08句式) ══')
# 真实报告句(2026-11-08 weekly): 旧正则 ([0-9]{1,3}\.[0-9]+)(?!\s*%) 在
# "VIX +32.03%至25.64" 上回溯捕获"32.0"(下一个字符'3'通过负向环视)→误报数值错误。
ROW_BY_NAME = {r[0]: r for r in dv.REPORT_CHECKS}


def _row_for(name_frag):
    for name in ROW_BY_NAME:
        if name_frag in name:
            return ROW_BY_NAME[name]
    return None


import re  # noqa: E402

CASES_1108 = [
    # (指标族, 报告句(真实/同构), 期望首捕获)
    ('VIX', 'VIX +32.03%至25.64', '25.64'),
    ('VIX', 'VIX 25.64', '25.64'),
    ('BTC', 'BTC +7.59%至98988.00', '98988.00'),
    ('黄金', '黄金期货(GOLD_F) +0.69%至4116.20', '4116.20'),
    ('WTI', 'WTI -0.19%至73.80', '73.80'),
    ('DXY', '美元指数(DXY) -0.50%至99.63', '99.63'),
    ('SPX', 'SPX涨0.8%至5923.1', '5923.1'),
    ('SPX', '标普500(SPX) +2.01%至6035.61', '6035.61'),
    # MW-V1第二轮(首次真实生成隔离的三个根因句式,取自2026-11-08周报原文):
    # (甲)桥后日期年份: 该句式下2026被守卫拒绝→整处放弃(期望None),
    #    核验留给同报告内下一处真实水平值提及(如"7,376.86")
    ('SPX', 'EZU +0.41% vs SPX -2.68%，同截至 2026-11-06），单周差异不足以支撑结论', None),
    # (乙)桥尾跨从句吞邻指标: VIX涨幅后跨"方向一致，但信用利差…"不得取到0.04
    #    →该句式整处放弃(期望None)
    ('VIX', '（SPX -2.68%、VIX +32.03% 方向一致，但信用利差 HY OAS 仅 +0.04pp 至 3.48%', None),
    # (丙)千分位: 逗号分隔大数必须可读(解析侧replace(',',''))
    ('SPX', 'SPX 周跌 -2.68% 至 7,376.86，VIX 周 +32.03%', '7,376.86'),
    ('黄金', '| COMEX黄金 | 4,074.90 | +4.51% |', '4,074.90'),
    ('上证', '上证收报 3,649.18 点', '3,649.18'),
    # MW-V1第三轮(第二次真实生成隔离的根因句式,同报告原文):
    # (丁)pre-value gap无界跨行: 表格单元"…| 跌幅大于SPX |\n| 罗素2000 |"旧gap
    #     [^0-9%]*?吞换行取到罗素2000指数名当SPX水平值;标题"**美元与黄金**\n
    #     DXY 102.30"同理吞DXY值当金价 → gap限宽{0,16}+禁换行,两处均放弃
    ('SPX', '| 跌幅大于SPX |\n| 罗素2000 | 2,754.11 | −2.05% |', None),
    ('黄金', '**比较3：美元与黄金**\nDXY 102.30（+0.41%）', None),
    # (戊)阈值距离句: "距400bp警告线0.52pp"=触发器距离度量非水平断言
    #     → _SPEC_CONTEXT_RE补警告线/关注区间后按阈值语境豁免(单测见下)
    # MW-V1第四轮(test_phase4[3]回归暴露): (己)值后句读逗号旧守卫误拒→静默放过
    #     ("VIX收于15.2,"既不核验也不进待复核);修后句读逗号放行,逗号+数字仍拒
    ('VIX', 'VIX收于15.2,恐慌情绪可控。', '15.2'),
    ('BTC', 'BTC报75810.73,与NDX同向。', '75810.73'),
    ('SPX', 'SPX -2.68%，报7376.86,其中科技领跌', '7376.86'),
    # 逗号后紧跟数字=千分位/枚举续接形态,守卫仍拒(不得捕获截尾值)
    ('VIX', 'VIX 15.2,3点区间内波动', None),
    # MW-V1第五轮(D'审计P2-1整改): (庚)桥尾改连接词白名单——百分比后无连接词的
    #     邻指标数字不再被当水平值(旧桥尾通配可跨"，罗素"吞2000→误隔离正确报告)
    ('SPX', 'SPX -2.68%，罗素2000 -2.05%', None),
    ('SPX', 'SPX +1.2%，沪深300 +2.0%', None),
    ('BTC', 'BTC -7.6%，以太坊1200美元失守', None),
    # 连接词句式(至/报,含空格)仍正常取水平值
    ('VIX', 'VIX +32.03% 至 25.64，美股普跌', '25.64'),
    ('黄金', '黄金 +4.51% 至 4,074.90，逆势上行', '4,074.90'),
]
# (甲)(乙)期望None=该occurrence整体放弃(守卫拒日期成分/桥尾限宽拒跨从句邻值),
# 水平值核验由同报告内下一处真实提及承接;真实全文回归见下方真实档复验。
for fam, sent, want in CASES_1108:
    row = _row_for(fam)
    pat = row[1] if isinstance(row[1], str) else row[1].pattern
    m = re.search(pat, sent)
    got = m.group(1) if m else None
    check(f"{fam}句式: …{sent[-14:]} → {want}",
          got == want, f"got={got}")

# 顿号枚举窗口: 指标窗口提取(_indicator_report_values)在顿号处截断,
# "失业率4.1、初请22.1万、续请187.3万人"只取[4.1],不吞并列指标值
spec_ue = next((s for s in dv.INDICATOR_SPECS if s.get('id') == 'UNRATE'), None)
if spec_ue is not None:
    vals_ue = dv._indicator_report_values(
        '美国劳动力市场维持稳健：失业率4.1、初请22.1万、续请187.3万人。', spec_ue)
    check('失业率顿号枚举窗口只含[4.1]',
          vals_ue == [(4.1, False, False)], f"vals={vals_ue}")
    vals_ue2 = dv._indicator_report_values(
        '美国劳动力市场维持稳健：失业率4.1，初请22.1万。', spec_ue)
    check('失业率逗号窗口仍只含[4.1]',
          vals_ue2 == [(4.1, False, False)], f"vals={vals_ue2}")
else:
    check('UNRATE指标spec存在(未找到则跳过)', False, 'INDICATOR_SPECS无UNRATE')
# MW-V1第二轮: 逗号从句跨资产吞值——真实句"5Y TIPS 2.33%（周+0.08pp），同期
# 黄金+4.51%"旧窗口(中文黄金不在stop2)把金价4.51吞进TIPS窗口→误报偏差;
# 修复后期望窗口=[2.33, 0.08](4.51留在黄金自己的核验里)
spec_t5 = next((s for s in dv.INDICATOR_SPECS if s.get('id') == 'TIPS_5Y'), None)
if spec_t5 is not None:
    vals_t5 = dv._indicator_report_values(
        '5Y TIPS 2.33%（周 +0.08pp），同期黄金 +4.51%。', spec_t5)
    check('TIPS窗口不吞逗号从句金价',
          [round(v[0], 2) for v in vals_t5] == [2.33, 0.08], f"vals={vals_t5}")
else:
    check('TIPS_5Y指标spec存在', False, 'INDICATOR_SPECS无TIPS_5Y')
# MW-V1第三轮(戊): 阈值距离句"距400bp警告线0.52pp"按阈值语境豁免——
# 真实句"HY OAS 3.48%处于300–400bp关注区间上沿，距400bp警告线0.52pp"里
# 0.52是距警告线的距离度量,不是HY OAS水平断言(旧词表有警戒线无警告线→误报偏差)
spec_hy = next((s for s in dv.INDICATOR_SPECS if s.get('id') == 'HY_OAS'), None)
if spec_hy is not None:
    vals_hy = dv._indicator_report_values(
        'HY OAS 3.48%处于300–400bp关注区间上沿，距400bp警告线0.52pp；CCC 13.20%已处恐慌区间。',
        spec_hy)
    v052 = [v for v in vals_hy if abs(v[0] - 0.52) < 1e-9]
    check('HY窗口0.52按阈值语境豁免(警告线)',
          v052 and v052[0][2] is True, f"vals={vals_hy}")
else:
    check('HY_OAS指标spec存在', False, 'INDICATOR_SPECS无HY_OAS')

print('══ ② JGB期限绑定(计分制) ══')
try:
    reg = fe.load_registry()
    ir = qm.map_question('美国和日本10年期国债收益率差是多少？',
                         created_at='2026-11-08T09:00:00+08:00', registry=reg)
    jgb_binding = [b for b in ir['metric_bindings']
                   if b['role'] == 'spread_component']
    check('概念"JGB 10Y"绑定到JGB10Y(非JGB2Y)',
          len(jgb_binding) == 1 and jgb_binding[0]['metric_id'] == 'JGB10Y',
          f"got={[b.get('metric_id') for b in jgb_binding]}")
except Exception as e:  # noqa: BLE001
    check('JGB绑定映射可执行', False, f'{type(e).__name__}: {e}')

print('══ ③ CN宏观事实归一 ══')
try:
    china_doc = {
        'macro': {
            'lpr_1y': {'date': '2026-10', 'value': 3.10, 'source': 'PBOC[示意]'},
            'cpi_yoy': {'date': '2026-09', 'value': 0.4, 'source': '统计局[示意]'},
        }
    }
    facts = fe.normalize_china(china_doc, as_of='2026-11-08',
                               source_file='china_market_20261108.json')
    lpr = next((f for f in facts if f['metric_id'] == 'CN_LPR_1Y'), None)
    cpi = next((f for f in facts if f['metric_id'] == 'CN_CPI_YOY'), None)
    check('CN_LPR_1Y入facts(值/月度锚月首)',
          lpr is not None and lpr['value'] == 3.10 and lpr['observation_date'] == '2026-10-01',
          f"lpr={lpr and (lpr['value'], lpr['observation_date'])}")
    check('月度锚calc披露在场', lpr is not None and '月首' in (lpr.get('calculation_ref') or ''),
          f"calc={lpr and lpr.get('calculation_ref')}")
    check('CN_CPI_YOY入facts', cpi is not None and cpi['value'] == 0.4
          and cpi['observation_date'] == '2026-09-01',
          f"cpi={cpi and (cpi['value'], cpi['observation_date'])}")
    check('channel透传', lpr is not None
          and lpr['source'].get('channel') == 'PBOC[示意]',
          f"ch={lpr and lpr['source'].get('channel')}")
except Exception as e:  # noqa: BLE001
    check('CN宏观归一可执行', False, f'{type(e).__name__}: {e}')

print('══ ④ 金双载体方向核验(sign_match恒真→真实实现) ══')
try:
    src = inspect.getsource(fe)
    check('sign_match恒真函数已移除', 'def sign_match' not in src, '')
    check('周方向一致性检查在场(GOLD_F×GLD)',
          'pct_change' in src and ('GOLD_F' in src and 'GLD' in src), '')
except Exception as e:  # noqa: BLE001
    check('fe源检查可执行', False, f'{type(e).__name__}: {e}')

print('══ ⑤ 越位零件下线 ══')
try:
    sig = inspect.signature(rg.generate_report)
    check('generate_report签名无theses/views_block',
          'theses' not in sig.parameters and 'views_block' not in sig.parameters,
          f"params={list(sig.parameters)}")
    gsrc = inspect.getsource(rg)
    prompt_zone = gsrc[gsrc.index('user_prompt = f"""'):
                       gsrc.index('user_prompt = f"""') + 2200]
    for kw in ('THESIS_STATUS', 'ALLOCATION_STATUS', 'PREDICTION_STATUS',
               '论点追踪', '配置观点:', '确信度★'):
        check(f'prompt无越位指令: {kw}', kw not in prompt_zone, '')
    wk = inspect.getsource(rg.generate_weekly_report)
    check('主流程不调用apply_status_updates',
          'apply_status_updates(' not in wk, '')
    check('主流程不渲染views_block', 'render_views_block' not in wk, '')
except Exception as e:  # noqa: BLE001
    check('越位下线检查可执行', False, f'{type(e).__name__}: {e}')

sys_prompt = open(os.path.join(ROOT, 'config', 'prompts', 'system_prompt.md'),
                  encoding='utf-8').read()
style_prompt = open(os.path.join(ROOT, 'config', 'prompts', 'style_constraints.md'),
                    encoding='utf-8').read()
check('system_prompt无星级门槛指令',
      '★' not in sys_prompt and '证据分级v2' not in sys_prompt, '')
_lines_over = [l for l in sys_prompt.splitlines() if '超配' in l]
check('system_prompt超配仅出现在禁止语境',
      _lines_over and all(('禁止' in l or '不得' in l or '（超配' in l) for l in _lines_over),
      str(_lines_over))
_lines_thesis = [l for l in style_prompt.splitlines() if '论点追踪' in l]
check('style_constraints论点追踪仅出现在移除说明',
      all('移除' in l for l in _lines_thesis) and 'thesis' not in style_prompt,
      str(_lines_thesis))
check('style_constraints保留数值绑定约束(30Y≠房贷)',
      '30年' in style_prompt, '')
check('system_prompt保留禁止用语纪律', '买入' in sys_prompt, '')

print()
print('═' * 60)
print(f'结果: {len(PASSED)}通过 / {len(FAILED)}失败')
print('═' * 60)
sys.exit(1 if FAILED else 0)
