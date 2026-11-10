#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Charter8 工作台数据层与文档面测试(交付⑥/⑧/⑤锁面)。

锁面:
① 页①数据: market_window_rows(窗口列+缺失行如实)/economy_dimension_matrix
   (覆盖=在场/活跃,不放大)
② 页③数据: views_matrix(只装载合规件,隔离绝不入面;机构×11主题)
③ 页④数据: research_archive_rows 真实档案读取(query_id 链)
④ SKILL.md 研究地图工作流在册+行数上限;docs 3m 自然窗示例(P2-2 口径)
合成快照/注册表零网络;views 用合成 tmp 目录(真实 11 份=B席基线,零依赖)。
"""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

PASS, FAIL = 0, 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")


import workbench_data as wd  # noqa: E402
import view_store as vs      # noqa: E402

# ── 合成注册表/快照(结构对照真实引擎;数值中性) ─────────────────────────
SYN_REG = {'metrics': [
    {'metric_id': 'SPX', 'display_name': '标普500', 'unit': 'index_point',
     'status': 'active', 'asset_class': 'equity_index', 'economy': 'US',
     'source': 'synthetic'},
    {'metric_id': 'GONE_ETF', 'display_name': '缺席代理', 'unit': 'index_point',
     'status': 'active', 'asset_class': 'bond_etf', 'economy': 'EA',
     'source': 'synthetic'},
    {'metric_id': 'RET_METRIC', 'display_name': '已退役', 'unit': 'index_point',
     'status': 'deprecated', 'asset_class': 'equity_index', 'economy': 'US',
     'source': 'synthetic'},
    {'metric_id': 'NFP', 'display_name': '非农', 'unit': 'thousands',
     'status': 'active', 'asset_class': 'macro', 'economy': 'US',
     'source': 'synthetic'},
], 'by_id': {}}
SYN_REG['by_id'] = {m['metric_id']: m for m in SYN_REG['metrics']}


def day(i):
    import datetime
    return (datetime.date(2025, 11, 10) + datetime.timedelta(days=i)).isoformat()


DATES = [day(i) for i in range(-1, 365)]
LEVELS = [100.0 + 10.0 * (i + 1) / 365 for i in range(-1, 365)]
SYN_SNAP = {
    'snapshot_id': 'research_snapshot_20261110_syn', 'target_date': '20261110',
    'facts': [
        {'metric_id': 'SPX', 'display_name': '标普500', 'value': 110.0,
         'unit': 'index_point', 'observation_date': '2026-11-10',
         'quality_status': 'PASS'},
        {'metric_id': 'NFP', 'display_name': '非农', 'value': 200.0,
         'unit': 'thousands', 'observation_date': '2026-11-10',
         'quality_status': 'PASS'},
    ],
    'series_store': {'SPX': {'dates': DATES, 'values': LEVELS}},
}

print("═" * 60)
print("[1] 页① market_window_rows: 窗口列+缺席如实")
print("═" * 60)
rows = wd.market_window_rows(SYN_SNAP, SYN_REG, root=ROOT)
by_id = {r['ID']: r for r in rows}
check("资产类指标入表(SPX/bond_etf 缺席代理)", {'SPX', 'GONE_ETF'} <= set(by_id))
check("非资产类(macro NFP)不入表", 'NFP' not in by_id)
check("退役指标不入表", 'RET_METRIC' not in by_id)
spx = by_id['SPX']
check("窗口列齐备(1m/3m/1y/5y)",
      all(f'{h}变化' in spx for h in ('1m', '3m', '1y', '5y')))
check("SPX 1y 变化为 +xx.xx% 形态(≈+10% 区间变动)",
      spx['1y变化'].endswith('%') and spx['1y变化'].startswith('+')
      and 9.0 < float(spx['1y变化'][1:-1]) < 11.0, str(spx['1y变化']))
check("SPX 序列来源=快照 series_store",
      'series_store' in (spx['序列来源'] or ''), str(spx['序列来源']))
gone = by_id['GONE_ETF']
check("缺席指标行='缺失'(不猜序列)",
      gone['当前值'] == '缺失' and gone['1y变化'] == '缺失'
      and gone['序列来源'] == '—', str(gone))

print("═" * 60)
print("[2] 页① economy_dimension_matrix: 覆盖如实呈现")
print("═" * 60)
mat = wd.economy_dimension_matrix(SYN_SNAP, SYN_REG)
check("返回 rows/asset_classes/note 三件",
      {'rows', 'asset_classes', 'note'} <= set(mat))
check("资产类维度含 equity_index/bond_etf/macro",
      {'equity_index', 'bond_etf', 'macro'} <= set(mat['asset_classes']))
mrow = {r['经济体']: r for r in mat['rows']}
check("经济体行含 美国(US)/欧元区(EA)",
      '美国(US)' in mrow and '欧元区(EA)' in mrow)
check("US equity_index=在场1/活跃1(退役不计)",
      mrow['美国(US)']['equity_index'] == '1/1',
      mrow['美国(US)'].get('equity_index'))
check("US macro=NFP 在场 1/1", mrow['美国(US)']['macro'] == '1/1')
check("EA equity_index 无活跃指标='—'", mrow['欧元区(EA)']['equity_index'] == '—')
check("EA bond_etf=0/1(缺席如实,不放大)", mrow['欧元区(EA)']['bond_etf'] == '0/1')

print("═" * 60)
print("[3] 页③ views_matrix: 只装载合规件,隔离不入面")
print("═" * 60)
GOOD_VIEW = {
    'schema_version': '1.1', 'view_id': 'VIEW-20261110-001',
    'institution': {'name': 'Synthetic Bank', 'type': 'investment_bank',
                    'department': 'Research'},
    'authors': [], 'report_title': 'Syn Outlook',
    'source_url': 'https://example.com/x', 'source_type': 'official_site',
    'publish_date': '2026-11-01', 'fetch_date': '2026-11-10',
    'access_level': 'public_full', 'view_horizon': '6m',
    'subjects': ['US_rates', 'equities'],
    'core_views': [{'statement': '看多。', 'attribution': 'institution_stated',
                    'basis': 'verbatim_quote', 'quote': 'We are bullish.'}],
    'forecasts': [], 'key_assumptions': [], 'evidence_cited': [],
    'mechanism_steps': [], 'risk_factors': [], 'falsification_conditions': [],
    'revisions': [], 'completeness_notes': '合成', 'copyright_note': 'meta+link',
}
BAD_VIEW = dict(GOOD_VIEW, schema_version='1.0', view_id='VIEW-20261110-002')
with tempfile.TemporaryDirectory() as td:
    for doc in (GOOD_VIEW, BAD_VIEW):
        with open(os.path.join(td, doc['view_id'] + '.json'), 'w',
                  encoding='utf-8') as f:
            json.dump(doc, f, ensure_ascii=False)
    vm = wd.views_matrix(views_dir=td)
    check("rows 只含合规件(1)", len(vm['rows']) == 1
          and vm['rows'][0]['view_id'] == 'VIEW-20261110-001')
    check("n_quarantined=1 随行", vm['n_quarantined'] == 1)
    check("schema_version='1.1' 随行", vm['schema_version'] == '1.1')
    check("主题列=11 主题全枚举(章程 subject 集)",
          len(vm['subjects']) == 11 and set(vm['subjects'])
          == set(vs.KNOWN_SUBJECTS))
    mrow = vm['matrix'][0]
    check("矩阵单元格=末三位编号(US_rates→001)", mrow['US_rates'] == '001')
    check("无观点主题='—'(不猜)", mrow['fx'] == '—')
    check("rows 摘要含机构/发布日/核心观点数",
          vm['rows'][0]['机构'] == 'Synthetic Bank'
          and vm['rows'][0]['核心观点数'] == 1)

print("═" * 60)
print("[4] 页④ research_archive_rows: 档案读取(fixture + 真实双轨)")
print("═" * 60)
# 根因A热修(2026-11-11): CI 干净检出无真实 data/(不入库纪律),
# research_archive_rows 默认读真实档→空表 IndexError。改为: 公开写入 API
# 合成 fixture 归档(QB-022带sidecar正文/023无正文但follow_up链在册),
# 全部断言在 fixture 行上执行;真实档在场时同款断言追加(本地/LIVE 不弱化),
# 缺席显式 SKIP。
import fixt_c8_archive as fixt  # noqa: E402
with tempfile.TemporaryDirectory() as _td:
    _arch = fixt.build_archive(_td)
    ra_rows = wd.research_archive_rows(limit=10, archive_dir=_arch)
check("档案行非空(fixture QB 链在册, n=%d)" % len(ra_rows), len(ra_rows) == 2)
check("行含 query_id/创建时间/问题/关联前档四要素",
      all(k in ra_rows[0] for k in ('query_id', '创建时间', '问题', '关联前档')))
check("最新在前(reversed)", ra_rows[0]['query_id'] >= ra_rows[-1]['query_id'])
check("问题摘要≤81 字符(截断纪律,含超长问题行)",
      all(len(r['问题']) <= 81 for r in ra_rows)
      and any(len(r['问题']) == 81 for r in ra_rows))
has_full = [r for r in ra_rows if r['研究正文'] != '—']
check("sidecar 研究正文摘要在场(022 行)", len(has_full) == 1
      and has_full[0]['query_id'] == fixt.Q22)
fu = {r['query_id']: r['关联前档'] for r in ra_rows}
check("follow_up 链在册(023→022)", fu.get(fixt.Q23) == fixt.Q22)

REAL_QH = os.path.join(ROOT, 'data', 'research', 'research_archive',
                       'research_archive', 'query_history')
if os.path.isdir(REAL_QH) and any(f.startswith('QB-')
                                  for f in os.listdir(REAL_QH)):
    real_rows = wd.research_archive_rows(limit=10)
    check("真实档案行非空(本地 QB 链在册, n=%d)" % len(real_rows),
          len(real_rows) > 0)
    check("真实行四要素/最新在前/≤81/正文在场",
          all(k in real_rows[0] for k in ('query_id', '创建时间', '问题', '关联前档'))
          and real_rows[0]['query_id'] >= real_rows[-1]['query_id']
          and all(len(r['问题']) <= 81 for r in real_rows)
          and any(r['研究正文'] != '—' for r in real_rows))
else:
    print("  ⏭️ SKIP[CI]: 真实 QB 归档缺席(data/不入库纪律;本地/LIVE 在场时"
          "执行真实档断言)——fixture 断言已覆盖同逻辑")

print("═" * 60)
print("[5] SKILL.md 研究地图工作流 + docs 3m 自然窗口径")
print("═" * 60)
skill_path = os.path.join(ROOT, '.agents', 'skills',
                          'global-macro-research', 'SKILL.md')
skill = open(skill_path, encoding='utf-8').read()
n_lines = skill.count('\n') + 1
check(f"SKILL.md 行数<500(现{n_lines})", n_lines < 500)
check("十个能力速查标题在册", '十个能力速查' in skill)
check("views 能力行在册(skill 面)",
      'views' in skill and '机构观点' in skill)
check("研究地图工作流节在册(Charter8 交付⑧)",
      '研究地图工作流' in skill)
check("工作流锁 attribution 纪律(明示/AI推导不混)",
      'attribution' in skill or '明示' in skill)
cli_doc = open(os.path.join(ROOT, '.agents', 'skills', 'global-macro-research',
                            'references', 'cli-contract.md'),
               encoding='utf-8').read()
check("cli-contract 3m 自然窗示例(--start 2026-08-10)",
      '--start 2026-08-10 --end 2026-11-10' in cli_doc)
guide = open(os.path.join(ROOT, 'docs', 'USER_GUIDE.md'), encoding='utf-8').read()
check("USER_GUIDE 3m 自然窗示例同口径",
      '2026-08-10' in guide and '2026-11-10' in guide)
check("USER_GUIDE '不存在也不需要单独的窗口逻辑'在册(禁新窗口逻辑)",
      '不存在也不需要单独的窗口逻辑' in guide)
readme = open(os.path.join(ROOT, 'README.md'), encoding='utf-8').read()
check("README 四页速查在册(机构观点/传导地图/独立研究)",
      all(k in readme for k in ('机构观点', '传导', '独立研究')))

print()
print("═" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("═" * 60)
sys.exit(0 if FAIL == 0 else 1)
