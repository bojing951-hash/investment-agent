#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Charter8 机构观点存储测试(交付①)——schema v1.1 铁律与 linter 拒绝面。

全部合成 fixture,零网络零写入(临时目录装载);真实 11 份 B 席档只做
开发期冒烟,不入本套件(套件不依赖真实库况)。

v1.1 仲裁要点(2026-11-10,协调裁定)逐面锁:
  - 单一版本纪律: schema_version 只认 '1.1'(1.0 拒)
  - quote=任意 basis 可附原文佐证(≤500);verbatim_quote 强制必填
  - falsification_conditions 用 condition 键(v1.0 漂移 statement 拒)
  - revisions 三键 {date,change,source_url}(B 席漂移 {attribution,note} 拒)
  - attribution 硬拦截(机构明示 vs AI 推导,章程核心红线)
  - 空数组+notes 说明=诚实缺席,放行(B 席央行公文实际用法)
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


import view_store as vs  # noqa: E402


def valid_doc():
    """最小合规档(v1.1): 含 verbatim 带引/paraphrase 带引/空数组+notes 三形态。"""
    return {
        'schema_version': '1.1',
        'view_id': 'VIEW-20261110-001',
        'institution': {'name': 'Example Bank', 'type': 'investment_bank',
                        'department': 'Research'},
        'authors': [],
        'report_title': 'Example Outlook',
        'source_url': 'https://example.com/report',
        'source_type': 'official_site',
        'publish_date': '2026-11-01',
        'fetch_date': '2026-11-10',
        'access_level': 'public_full',
        'view_horizon': '6m',
        'subjects': ['US_rates', 'equities'],
        'core_views': [
            {'statement': '机构看多美股。', 'attribution': 'institution_stated',
             'basis': 'verbatim_quote', 'quote': 'We expect equities to rise.'},
            {'statement': '利率将维持高位(转述)。', 'attribution': 'ai_inferred',
             'basis': 'paraphrase', 'quote': 'rates are likely to stay higher'},
        ],
        'forecasts': [{'target': 'SPX_end_2027', 'value_or_direction': '6600',
                       'horizon': 'CY2027', 'attribution': 'institution_stated'}],
        'key_assumptions': [],
        'evidence_cited': [{'statement': '引用了就业数据。', 'attribution':
                            'institution_stated'}],
        'mechanism_steps': [],
        'risk_factors': [],
        'falsification_conditions': [{'condition': '若 CPI<2% 则观点修正',
                                       'attribution': 'institution_stated'}],
        'revisions': [{'date': '2026-08-01', 'change': 'SPX 目标 6400→6600',
                       'source_url': 'https://example.com/aug'}],
        'completeness_notes': 'authors/key_assumptions 等为空: 官方摘要页未署名/未列假设(诚实缺席)。',
        'copyright_note': 'metadata+short_quotes+link_only',
    }


print("═" * 60)
print("[1] schema v1.1 常量与合规基线")
print("═" * 60)
check("SCHEMA_VERSION='1.1'(单一版本纪律)", vs.SCHEMA_VERSION == '1.1')
check("QUOTE_MAX_CHARS=500", vs.QUOTE_MAX_CHARS == 500)
rules = vs.lint_view(valid_doc(), 'VIEW-20261110-001.json')
check("最小合规档零违规", rules == [], str(rules))
d = valid_doc()
d['core_views'][1].pop('quote')          # paraphrase 不带 quote 也合规
check("paraphrase 无 quote 键合规", vs.lint_view(d, 'VIEW-20261110-001.json') == [])

print("═" * 60)
print("[2] v1.0→1.1 仲裁三漂移的拒绝面")
print("═" * 60)
d = valid_doc(); d['schema_version'] = '1.0'
r = vs.lint_view(d, 'VIEW-20261110-001.json')
check("schema_version=1.0 被拒(不做向后兼容)",
      any(v['rule'] == 'schema_version' for v in r), str(r))

d = valid_doc(); d['falsification_conditions'] = [
    {'statement': 'v1.0 漂移键', 'attribution': 'institution_stated'}]
r = vs.lint_view(d, 'VIEW-20261110-001.json')
check("falsification 用 statement 键被拒(condition 定稿)",
      any(v['field'] == 'falsification_conditions[0]' and v['rule'] == 'shape'
          for v in r), str(r))

d = valid_doc(); d['revisions'] = [
    {'attribution': 'ai_inferred', 'note': 'v1.0 漂移形状'}]
r = vs.lint_view(d, 'VIEW-20261110-001.json')
check("revisions {attribution,note} 漂移被拒(三键铁律)",
      any(v['field'] == 'revisions[0]' and v['rule'] == 'shape' for v in r), str(r))

print("═" * 60)
print("[3] attribution 红线与 quote 规则面")
print("═" * 60)
d = valid_doc(); d['core_views'][0].pop('attribution')
r = vs.lint_view(d, 'VIEW-20261110-001.json')
check("core_views 缺 attribution 硬拦截",
      any(v['field'] == 'core_views[0].attribution' and v['rule'] == 'enum_required'
          for v in r), str(r))

d = valid_doc(); d['forecasts'][0]['attribution'] = 'guessed'
r = vs.lint_view(d, 'VIEW-20261110-001.json')
check("forecasts attribution 非法枚举拦截",
      any(v['field'] == 'forecasts[0].attribution' and v['rule'] == 'enum_required'
          for v in r), str(r))

d = valid_doc(); d['core_views'][0].pop('quote')  # verbatim 无 quote
r = vs.lint_view(d, 'VIEW-20261110-001.json')
check("verbatim_quote 无 quote 拦截",
      any(v['rule'] == 'verbatim_requires_quote' for v in r), str(r))

d = valid_doc(); d['core_views'][1]['quote'] = 'x' * 501  # paraphrase 长引
r = vs.lint_view(d, 'VIEW-20261110-001.json')
check("paraphrase 佐证引文>500 拦截(v1.1 放宽仍守长度)",
      any(v['rule'] == 'quote_max_length' for v in r), str(r))

d = valid_doc(); d['core_views'][0]['quote'] = 'y' * 501  # verbatim 长引
r = vs.lint_view(d, 'VIEW-20261110-001.json')
check("verbatim 引文>500 拦截", any(v['rule'] == 'quote_max_length' for v in r))

d = valid_doc(); d['core_views'][1]['quote'] = '   '  # 空白佐证
r = vs.lint_view(d, 'VIEW-20261110-001.json')
check("空白 quote 拦截(quote_nonempty)",
      any(v['rule'] == 'quote_nonempty' for v in r), str(r))

print("═" * 60)
print("[4] 结构性拒绝面(字段/日期/主题/文件名)")
print("═" * 60)
d = valid_doc(); d.pop('copyright_note')
check("顶层必填缺失→required", any(v['rule'] == 'required'
                                    for v in vs.lint_view(d, 'VIEW-20261110-001.json')))

d = valid_doc(); d['publish_date'] = '2026-11-20'; d['fetch_date'] = '2026-11-10'
check("publish_date>fetch_date 拦截", any(v['rule'] == 'publish_le_fetch'
                                           for v in vs.lint_view(d, 'VIEW-20261110-001.json')))

d = valid_doc(); d['subjects'] = ['mars_macro']
check("未登记主题拦截", any(v['rule'] == 'known_subjects'
                             for v in vs.lint_view(d, 'VIEW-20261110-001.json')))

d = valid_doc()
check("view_id 与文件名不一致拦截",
      any(v['rule'] == 'filename_match' for v in vs.lint_view(d, 'VIEW-20261110-002.json')))

d = valid_doc(); d['core_views'] = []
check("core_views 空拦截(空观点≠观点档)", any(v['rule'] == 'nonempty'
                                               for v in vs.lint_view(d, 'VIEW-20261110-001.json')))

d = valid_doc(); d['institution']['type'] = 'hedge_fund_boutique'
check("institution.type 非法枚举拦截", any(v['field'] == 'institution.type'
                                             for v in vs.lint_view(d, 'VIEW-20261110-001.json')))

print("═" * 60)
print("[5] 装载纪律: 隔离不装载,绝不降级")
print("═" * 60)
with tempfile.TemporaryDirectory() as td:
    good = valid_doc()
    with open(os.path.join(td, 'VIEW-20261110-001.json'), 'w', encoding='utf-8') as f:
        json.dump(good, f, ensure_ascii=False)
    bad = valid_doc(); bad['view_id'] = 'VIEW-20261110-002'; bad['schema_version'] = '1.0'
    with open(os.path.join(td, 'VIEW-20261110-002.json'), 'w', encoding='utf-8') as f:
        json.dump(bad, f, ensure_ascii=False)
    with open(os.path.join(td, 'VIEW-20261110-003.json'), 'w', encoding='utf-8') as f:
        f.write('{not json')
    res = vs.load_views(td)
    check("合规件装载(1)", len(res['views']) == 1
          and res['views'][0]['view_id'] == 'VIEW-20261110-001')
    check("违规件隔离(1.0 版)", any(q['view_id'] == 'VIEW-20261110-002'
                                     for q in res['quarantined']))
    check("解析失败件隔离(不崩)", any(q['view_id'] == 'VIEW-20261110-003'
                                       for q in res['quarantined']))
    check("n_files=3(含隔离)", res['n_files'] == 3)
    doc, reason = vs.get_view('VIEW-20261110-002', td)
    check("隔离件 get_view 拒绝(不因点名放出)", doc is None and '隔离' in reason)
    doc, _ = vs.get_view('VIEW-20261110-001', td)
    check("合规件 get_view 放行", doc is not None and doc['view_id'] == 'VIEW-20261110-001')
    doc, reason = vs.get_view('VIEW-19990101-999', td)
    check("不存在件 get_view 如实 None", doc is None)
    rows = vs.list_views(td)
    check("list_views 只列合规件+隔离计数",
          len(rows['views']) == 1 and rows['n_quarantined'] == 2)

print()
print("═" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("═" * 60)
sys.exit(0 if FAIL == 0 else 1)
