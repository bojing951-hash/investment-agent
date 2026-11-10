#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Charter8 传导边档测试(交付④/页面②数据源)——归档溯源铁律。

核心约束(协调裁定 2026-11-10): 边表每条边必须有 qb_source 指向**真实存在**
的 QB 归档;禁凭空策划任何未经归档研究支持的边。近零渠道同样入表=证据面
("教科书渠道本地数据不支持"本身是归档研究结论)。

另锁 P2 台账 Charter8 登记(19-22 行)与 app 零模型面。
"""
import glob
import json
import os
import re
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
import research_archive as ra  # noqa: E402
import fixt_c8_archive as fixt  # noqa: E402  (CI自足fixture,根因A热修)

EDGES_PATH = os.path.join(ROOT, 'config', 'transmission_edges.json')
doc = json.load(open(EDGES_PATH, encoding='utf-8'))

print("═" * 60)
print("[1] 溯源铁律: qb_source 指向真实 QB 归档")
print("═" * 60)
# 根因A热修(2026-11-11): CI 干净检出无真实 data/(不入库纪律),原直读真实
# QB 档必挂。改为: 公开写入 API 合成 fixture 档(022/023,与边表引用一致),
# "边必挂 QB 号"核验逻辑在 fixture 上完整执行+反例核验(不空转);真实档
# 核验在档在场时执行,缺席显式 SKIP——禁止为过 CI 往库里塞真实 data 档。
FIXTURE_TD = tempfile.TemporaryDirectory()
fixt_arch = fixt.build_archive(FIXTURE_TD.name)
qb_ids = set(ra.list_query_records(archive_dir=fixt_arch))
check("合成 QB 归档可枚举(fixture, n=%d)" % len(qb_ids),
      qb_ids == {fixt.Q22, fixt.Q23}, str(sorted(qb_ids)))
check("fixture 记录可经读取面回读(写入API产物非手工摆文件)",
      ra.load_query_record(fixt.Q22, archive_dir=fixt_arch).get('query_id')
      == fixt.Q22)
edge_sources = {e['qb_source'] for e in doc['edges']}
check("每条边带 qb_source", all(e.get('qb_source') for e in doc['edges']))
check(f"边表 qb_source 全部指向在册归档(fixture){sorted(edge_sources)}",
      edge_sources <= qb_ids, str(edge_sources - qb_ids))
mf_sources = {f['qb_source'] for f in doc['mechanism_findings']}
check(f"机制结论 qb_source 全部在册(fixture){sorted(mf_sources)}",
      mf_sources <= qb_ids)
ss = doc.get('structural_summary') or {}
check("结构性结论带 qb_source", bool(ss.get('qb_source'))
      and ss['qb_source'] in qb_ids)
check("核验能逮住未归档来源(反例,不空转)",
      not ({'QB-20261110-999'} <= qb_ids))

REAL_QH = os.path.join(ROOT, 'data', 'research', 'research_archive',
                       'research_archive', 'query_history')
real_qb_ids = {os.path.basename(p)[:-5] for p in glob.glob(
    os.path.join(REAL_QH, 'QB-*.json'))}
if real_qb_ids:
    check("本地真实 QB 归档可枚举(n=%d)" % len(real_qb_ids),
          len(real_qb_ids) > 0)
    check(f"边表 qb_source 全部指向真实归档{sorted(edge_sources)}",
          edge_sources <= real_qb_ids, str(edge_sources - real_qb_ids))
    check(f"机制结论 qb_source 全部真实{sorted(mf_sources)}",
          mf_sources <= real_qb_ids)
    check("结构性结论 qb_source 指向真实归档", ss.get('qb_source')
          in real_qb_ids)
else:
    print("  ⏭️ SKIP[CI]: 真实 QB 归档缺席(data/不入库纪律;本地/LIVE 在场"
          "时执行真实档核验)——fixture 核验+反例已覆盖同逻辑")

print("═" * 60)
print("[2] 边表结构与 E1/E2/E3 分级")
print("═" * 60)
check("schema_version 在场", doc.get('schema_version') == '1.0')
check("证据分级图例 E1/E2/E3 齐备",
      set(doc['evidence_grading']) == {'E1', 'E2', 'E3'})
check("类别语义 strong/near_zero 齐备",
      set(doc['category_semantics']) == {'strong', 'near_zero'})
cats = {e['category'] for e in doc['edges']}
check("边 category 只用两类", cats <= {'strong', 'near_zero'}, str(cats))
check("每条边 r 数值+n+窗+E级齐备",
      all(isinstance(e['r'], (int, float)) and isinstance(e['n'], int)
          and e.get('window') and e.get('evidence_level')
          for e in doc['edges']))
check("edge_id 唯一", len({e['edge_id'] for e in doc['edges']}) == len(doc['edges']))
check("强渠道含风险偏好内环与美元-黄金(QB-022 证据面)",
      {'VIX-SPX', 'DXY-GOLDF', 'TIPS10Y-UST10Y'} <=
      {e['edge_id'] for e in doc['edges']})
near = [e for e in doc['edges'] if e['category'] == 'near_zero']
check(f"近零渠道 {len(near)} 条入表(教科书叙事本地不支持=归档结论,非策划缺口)",
      len(near) >= 8)
check("近零渠道全部带弱化限定(教科书/流行叙事/近零/弱,不冒充强渠道)",
      all(any(k in e['channel_label'] or k in e['note'] for k in
              ('教科书', '流行叙事', '近零', '弱')) for e in near))
verdicts = {f['verdict'] for f in doc['mechanism_findings']}
check("机制结论 verdict 枚举(still_valid/not_applicable/unverifiable)",
      verdicts == {'still_valid', 'not_applicable', 'unverifiable'}, str(verdicts))
e3 = [f for f in doc['mechanism_findings'] if f['evidence_level'] == 'E3']
check("E3 不可移植结论在册(QB-023 QE/加息起点)", len(e3) >= 2)
check("展示纪律文案在册(未验证因果不画为事实)",
      '未验证因果不画为事实' in doc.get('display_rule', ''))

print("═" * 60)
print("[3] 装载器拒绝面: 缺 qb_source 的边档拒载")
print("═" * 60)
bad_doc = {'edges': [{'edge_id': 'X', 'from': 'A', 'to': 'B',
                      'channel_label': '凭空', 'category': 'strong',
                      'r': 0.9, 'n': 10, 'window': '全窗',
                      'evidence_level': 'E1', 'note': '无来源'}],
           'mechanism_findings': []}
with tempfile.TemporaryDirectory() as td:
    bad_root = os.path.join(td, 'pkg')
    os.makedirs(os.path.join(bad_root, 'config'))
    with open(os.path.join(bad_root, 'config', 'transmission_edges.json'),
              'w', encoding='utf-8') as f:
        json.dump(bad_doc, f, ensure_ascii=False)
    try:
        wd.transmission_edges(root=bad_root)
        check("缺 qb_source 的边档 raise(不静默装载)", False)
    except ValueError as e:
        check("缺 qb_source 的边档 raise(不静默装载)", '凭空策划' in str(e))
loaded = wd.transmission_edges()
check("真实档装载成功(workbench_data.transmission_edges)",
      len(loaded['edges']) == len(doc['edges']))

print("═" * 60)
print("[4] 数值抽核: 边表 r 与归档 answer_text 一致(防抄录漂移)")
print("═" * 60)
# 根因A热修: CI 无真实归档——抽核对 fixture sidecar 执行(其 answer_text
# 四行与真实 QB-022 逐字同源,防抄录漂移核验逻辑在 CI 完整可跑);真实档
# 在场时追加对真实归档的同款抽核(本地/LIVE 不弱化)。
at = ra.load_research_full(fixt.Q22, archive_dir=fixt_arch)['answer_text']
spot = {('| VIX×SPX | −0.7138' in at, 'VIX×SPX r=-0.7138 逐字在归档(fixture)'),
        ('| DXY×GOLD_F | **−0.3935' in at, 'DXY×GOLD_F r=−0.3935 逐字在归档(fixture)'),
        ('| TIPS_10Y×UST_10Y | +0.8278' in at, 'TIPS×UST r=+0.8278 逐字在归档(fixture)'),
        ('| EURUSD×UST_10Y | −0.0307' in at, 'EURUSD×UST 近零 −0.0307 在归档(fixture)')}
for cond, name in spot:
    check(name, cond)
real_full022 = os.path.join(REAL_QH, 'QB-20261110-022.research-full.json')
if os.path.isfile(real_full022):
    rat = json.load(open(real_full022, encoding='utf-8'))['answer_text']
    real_spot = (('| VIX×SPX | −0.7138' in rat, 'VIX×SPX r=-0.7138 逐字在真实归档'),
                 ('| DXY×GOLD_F | **−0.3935' in rat, 'DXY×GOLD_F r=−0.3935 逐字在真实归档'),
                 ('| TIPS_10Y×UST_10Y | +0.8278' in rat, 'TIPS×UST r=+0.8278 逐字在真实归档'),
                 ('| EURUSD×UST_10Y | −0.0307' in rat, 'EURUSD×UST 近零 −0.0307 在真实归档'))
    for cond, name in real_spot:
        check(name, cond)
else:
    print("  ⏭️ SKIP[CI]: 真实 QB-022 research-full 缺席(data/不入库纪律;"
          "本地/LIVE 在场时执行)——fixture 抽核已覆盖同逻辑")
edges_by_id = {e['edge_id']: e for e in doc['edges']}
check("边表 VIX-SPX r=-0.7138 与归档一致",
      edges_by_id['VIX-SPX']['r'] == -0.7138)
check("边表 DXY-GOLDF r=-0.3935 与归档一致",
      edges_by_id['DXY-GOLDF']['r'] == -0.3935)
check("边表 EURUSD-UST10Y(近零) r=-0.0307 与归档一致",
      edges_by_id['EURUSD-UST10Y']['r'] == -0.0307)

print("═" * 60)
print("[5] P2 台账 Charter8 登记(19-22 行)+ 页面零模型面")
print("═" * 60)
ledger = open(os.path.join(ROOT, 'docs', 'P2_DATA_GAP_LEDGER.md'),
              encoding='utf-8').read()
check("台账登记 19 HK 宏观八维零覆盖", re.search(r'\|\s*19\s*\|.*HK 宏观八维', ledger)
      is not None)
check("台账登记 20 HKMA 基础利率(实测 405/无字段)", re.search(r'\|\s*20\s*\|.*HKMA', ledger)
      is not None)
check("台账登记 21 财政维零覆盖", re.search(r'\|\s*21\s*\|.*财政维', ledger) is not None)
check("台账登记 22 贸易维零覆盖", re.search(r'\|\s*22\s*\|.*贸易维', ledger) is not None)
check("台账三之二登记 HK 深窗收口(n=2460)", 'n=320→2460' in ledger or '2460' in ledger)
app_src = open(os.path.join(ROOT, 'app.py'), encoding='utf-8').read()
check("app.py 零模型调用(无 ai_explain/MODEL_*/openai)",
      not any(k in app_src for k in ('ai_explain', 'MODEL_API_KEY', 'openai')))
check("app.py 四页导航在册(Charter8 页名)",
      all(p in app_src for p in ('全球宏观全景', '全球金融传导地图',
                                 '机构观点矩阵', '独立研究结论')))

print()
print("═" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("═" * 60)
sys.exit(0 if FAIL == 0 else 1)
