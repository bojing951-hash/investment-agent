#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""架构整改 T5 回归套件(2026-11-15,PHASE3-PLAN 工单T5: claim_verifier
六状态确定性验证)。

验收原文: 「注入违例每状态≥1 反例咬住」——本套件对六状态逐一注入:

  A  基线: 工厂 clean bundle 111 条→109 VERIFIED+2 STALE,gate_b=True
     (T6a 补全 statistic 型: 切片含 DXY×SPX 对→+2 条,基线随契约扩容);
     JP_POLICY_RATE 滞后74天=stale_level_1(契约§4 STALE 行权威例);
     DFF−JP spread 继承最差输入(成员各自节奏定级,禁跨成员错除);
     observation_lag 型(陈旧度计量本身)永不 STALE。
  B  CONTRADICTED(每型≥1+三重违规面): 九型数值篡改/阈值漂移/证据值不符/
     rank 组换位+组重复(对位+多重集双路)/跨单位 spread(律3)/分解可加性(§3)。
  C  反洗数(律7/v1.1): model_inferred 数值有源→对照复算照常 VERIFIED;
     篡值→CONTRADICTED;证据缺失/无路径→一律强制升 SEMANTIC_REVIEW_REQUIRED
     (禁经 INSUFFICIENT/NOT_VERIFIABLE 披露洗出);deterministic 无路径→
     NOT_VERIFIABLE 带归因{路径/原因枚举/可否次级交叉}。
  D  INSUFFICIENT_EVIDENCE: 空引用/无值引用/所引事实不在快照。
  E  STALE 分级: ratio 阈值 1/2/3 三档(l2=130d,l3=200d 禁入现状框架→
     current_frame_forbidden)+节奏不可得=cadence_unknown 只披露不拦。
  F  裁决写回+超时策略: verification 字段=契约§2 示例形状;双跑逐字节
     相等;timeout_policy 剔除+显式披露。
  G  纯度(Z1 同面): 源码零模型客户端/零环境变量/零网络/零随机;
     MODEL_* 绊线下子进程双跑逐字节同输出;CLI 冒烟。

数据纪律: fixture 复用 T4 真实快照垂直切片(出处随档);零绝对路径/
零网络(CI 干净克隆安全)。脚本式逐检(仓库惯例)。
"""
import copy
import json
import os
import subprocess
import sys
import tempfile
from datetime import date

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
for p in (ROOT, os.path.join(ROOT, 'scripts')):
    if p not in sys.path:
        sys.path.insert(0, p)

from research_contract import claim_factory as cf   # noqa: E402
from research_contract import claim_verifier as cv  # noqa: E402

FIXTURE = os.path.join(ROOT, 'tests', 'fixtures', 't4_claims',
                       'snapshot_slice_20261114.json')

PASSED, FAILED = [], []


def check(name, cond, detail=''):
    (PASSED if cond else FAILED).append((name, detail))
    print(('  ✅ ' if cond else ' ❌ ') + name + (f' [{detail}]' if not cond and detail else ''))


def load():
    with open(FIXTURE, 'r', encoding='utf-8') as f:
        snap = json.load(f)
    return cf.generate_claims_bundle(snap), snap


def by_id(b, cid):
    return next(c for c in b['claims'] if c['claim_id'] == cid)


def statuses(res):
    return {v['claim_id']: v['status'] for v in res['verdicts']}


def verify(b, s, **kw):
    return cv.verify_bundle(b, snapshot=s, **kw)


BUNDLE, SNAP = load()
BASE = verify(BUNDLE, SNAP)


def mutated(fn):
    """深拷贝→注入→全量复验(注入闭包签名 (bundle, snapshot))。"""
    b, s = copy.deepcopy(BUNDLE), copy.deepcopy(SNAP)
    fn(b, s)
    return verify(b, s)


# ══ A 基线 ════════════════════════════════════════════════════════
print('=' * 72)
print('[A] 工厂 clean bundle 基线(六状态零误伤)')
print('=' * 72)
check('A1 clean 111 条全量裁决零 CONTRADICTED',
      BASE['summary']['CONTRADICTED'] == 0 and BASE['summary']['total'] == 111,
      json.dumps(BASE['summary']))
check('A2 clean 分布=109 VERIFIED+2 STALE(余状态零)',
      BASE['summary']['VERIFIED'] == 109 and BASE['summary']['STALE'] == 2
      and BASE['summary']['INSUFFICIENT_EVIDENCE'] == 0
      and BASE['summary']['NOT_VERIFIABLE'] == 0
      and BASE['summary']['SEMANTIC_REVIEW_REQUIRED'] == 0)
check('A3 gate_b_numeric_all_verified=True(clean 面发布门开)',
      BASE['publish']['gate_b_numeric_all_verified'] is True)
check('A4 blocked/queue/forbidden 三清单空(clean)',
      not BASE['publish']['blocked_revisions']
      and not BASE['publish']['semantic_review_queue']
      and not BASE['publish']['current_frame_forbidden'])
jp = next(v for v in BASE['verdicts'] if v['claim_id'] == 'CLM-20261114-0012')
check('A5 JP_POLICY_RATE 滞后74天=stale_level_1(契约§4 STALE 行权威例,'
      '74/60≈1.2 节奏)',
      jp['status'] == 'STALE' and jp['stale']['tier'] == 'stale_level_1'
      and jp['stale']['lag_days'] == 74 and jp['stale']['cadence_days'] == 60.0)
spread = next(v for v in BASE['verdicts'] if v['claim_id'] == 'CLM-20261114-0072')
check('A6 DFF−JP spread 继承最差输入=level_1(JP 74/60;DFF 2/10 fresh;'
      '禁跨成员错除)',
      spread['status'] == 'STALE' and spread['stale']['tier'] == 'stale_level_1'
      and len(spread['stale'].get('members', [])) == 2)
check('A7 observation_lag 型(陈旧度计量本身)永不 STALE',
      all(v['status'] == 'VERIFIED'
          for v in BASE['verdicts'] if v['claim_type'] == 'observation_lag'))
check('A8 STALE 必带披露串(§4 须披露)',
      all(v['disclosure'] for v in BASE['verdicts'] if v['status'] == 'STALE'))
check('A9 VERIFIED 零披露(§4 无披露)',
      all(not v['disclosure'] for v in BASE['verdicts']
          if v['status'] == 'VERIFIED'))
check('A10 checker_version=claim_verifier 1.0 全量随行',
      all(v['checker_version'] == 'claim_verifier 1.0'
          for v in BASE['verdicts']))

# ══ B CONTRADICTED 注入(每型≥1) ══════════════════════════════════
print()
print('=' * 72)
print('[B] CONTRADICTED 注入反例(数值篡改/漂移/组核验/律3/§3)')
print('=' * 72)
CASES_B = [
    ('B1 level/point 篡值', 'CLM-20261114-0001',
     lambda b, s: by_id(b, 'CLM-20261114-0001').update(value=999.0)),
    ('B2 change/relative 篡值', 'CLM-20261114-0016',
     lambda b, s: by_id(b, 'CLM-20261114-0016').update(
         value=by_id(b, 'CLM-20261114-0016')['value'] + 0.7)),
    ('B3 change/absolute(pp) 篡值', 'CLM-20261114-0044',
     lambda b, s: by_id(b, 'CLM-20261114-0044').update(
         value=by_id(b, 'CLM-20261114-0044')['value'] + 0.1)),
    ('B4 comparison/spread 篡值', 'CLM-20261114-0072',
     lambda b, s: by_id(b, 'CLM-20261114-0072').update(
         value=by_id(b, 'CLM-20261114-0072')['value'] + 1.0)),
    ('B5 threshold value 篡值(=Fact 值不符)', 'CLM-20261114-0077',
     lambda b, s: by_id(b, 'CLM-20261114-0077').update(value=9.9)),
    ('B6 threshold relation 篡(above→below)', 'CLM-20261114-0077',
     lambda b, s: by_id(b, 'CLM-20261114-0077').update(relation='below')),
    ('B7 threshold since_date 篡', 'CLM-20261114-0077',
     lambda b, s: by_id(b, 'CLM-20261114-0077').update(since_date='2020-01-01')),
    ('B8 threshold_distance 篡值', 'CLM-20261114-0087',
     lambda b, s: by_id(b, 'CLM-20261114-0087').update(value=42.0)),
    ('B9 level/band 篡 low(数值对)', 'CLM-20261114-0014',
     lambda b, s: by_id(b, 'CLM-20261114-0014')['value'].update(low=1.0)),
    ('B10 证据引用带值不符(ref.value≠fact.value)', 'CLM-20261114-0001',
     lambda b, s: by_id(b, 'CLM-20261114-0001')['evidence_refs'][0].update(value=42.0)),
    ('B11 threshold_ref 值漂移(≠注册表)', 'CLM-20261114-0077',
     lambda b, s: by_id(b, 'CLM-20261114-0077')['threshold_ref'].update(value=3.5)),
]
for name, cid, fn in CASES_B:
    r = mutated(fn)
    v = next((x for x in r['verdicts'] if x['claim_id'] == cid), None)
    check(name + '→CONTRADICTED+入修订清单', v is not None
          and v['status'] == 'CONTRADICTED'
          and cid in r['publish']['blocked_revisions'])


def rank_swap(b, s):
    by_id(b, 'CLM-20261114-0074').update(value=3)   # 第1名↔第3名换位
    by_id(b, 'CLM-20261114-0076').update(value=1)


r = mutated(rank_swap)
st = statuses(r)
check('B12 rank 组换位→两条对位不符(多重集仍{1,2,3}由对位路咬住)',
      st.get('CLM-20261114-0074') == 'CONTRADICTED'
      and st.get('CLM-20261114-0076') == 'CONTRADICTED'
      and st.get('CLM-20261114-0075') == 'VERIFIED')

r = mutated(lambda b, s: by_id(b, 'CLM-20261114-0075').update(value=1))
st = statuses(r)
check('B13 rank 组重复(1,1,3)→多重集路咬住全组三条',
      all(st.get(c) == 'CONTRADICTED' for c in
          ('CLM-20261114-0074', 'CLM-20261114-0075', 'CLM-20261114-0076')))


def cross_unit(b, s):
    """律3: 双侧引用与事实一致地改成异单位(绕过逐 ref 一致性,专打 spread 同单位校验)。"""
    c = by_id(b, 'CLM-20261114-0072')
    for x in s['facts']:
        if x['metric_id'] == 'DFF':
            x['unit'] = 'percentage_point'
    for ref in c['evidence_refs']:
        if ref.get('role') == 'left':
            ref['unit'] = 'percentage_point'


r = mutated(cross_unit)
v = next(x for x in r['verdicts'] if x['claim_id'] == 'CLM-20261114-0072')
check('B14 跨单位 spread(律3)=硬不符,禁经 NOT_VERIFIABLE 披露洗出',
      v['status'] == 'CONTRADICTED')


def additivity_break(b, s):
    tgt = next(c for c in b['claims'] if c['claim_type'] == 'change'
               and c['subtype'] == 'absolute' and c['unit'] == 'percentage_point')
    parts = [c for c in b['claims'] if c['claim_type'] == 'change'
             and c['subtype'] == 'absolute' and c['unit'] == 'percentage_point'
             and c is not tgt][:2]
    tgt['derivation']['basis'] = ['claim:' + parts[0]['claim_id'],
                                  'claim:' + parts[1]['claim_id']]
    tgt['value'] = round(parts[0]['value'] + parts[1]['value'] + 0.05, 4)


r = mutated(additivity_break)
v = next(x for x in r['verdicts'] if x['claim_type'] == 'change'
         and any(rs.startswith('additivity:') for rs in x['reasons']))
check('B15 分解可加性(§3)破→CONTRADICTED(reasons 带 additivity 注记)',
      v['status'] == 'CONTRADICTED')

# ══ C 反洗数(律7 model_inferred) ═════════════════════════════════
print()
print('=' * 72)
print('[C] 反洗数: model_inferred 数值禁经 INSUFF/NV 洗出')
print('=' * 72)
r = mutated(lambda b, s: by_id(b, 'CLM-20261114-0001').update(attribution='model_inferred'))
v = next(x for x in r['verdicts'] if x['claim_id'] == 'CLM-20261114-0001')
check('C1 model 数值+权威源在→对照复算一致=VERIFIED(律7 有源即复算,'
      '不因 attribution 一刀切)',
      v['status'] == 'VERIFIED')


def model_tamper(b, s):
    c = by_id(b, 'CLM-20261114-0001')
    c['attribution'] = 'model_inferred'
    c['value'] = c['value'] + 1.0


r = mutated(model_tamper)
v = next(x for x in r['verdicts'] if x['claim_id'] == 'CLM-20261114-0001')
check('C2 model 数值+篡值→CONTRADICTED(复算不符优先于强制升态)',
      v['status'] == 'CONTRADICTED')

r = mutated(lambda b, s: by_id(b, 'CLM-20261114-0001').update(
    attribution='model_inferred', evidence_refs=[]))
v = next(x for x in r['verdicts'] if x['claim_id'] == 'CLM-20261114-0001')
check('C3 model 数值+空引用→强制 SEMANTIC_REVIEW(非 INSUFFICIENT)',
      v['status'] == 'SEMANTIC_REVIEW_REQUIRED'
      and 'CLM-20261114-0001' in r['publish']['semantic_review_queue'])


def drop_hy(b, s):
    s['facts'] = [f for f in s['facts'] if f['fact_id'] != 'HY_OAS@2026-11-12']


r = mutated(drop_hy)
st = statuses(r)
hy_insuff = [c for c in BUNDLE['claims']
             if any(e.get('ref') == 'HY_OAS@2026-11-12'
                    for e in c.get('evidence_refs') or [])]
check('C4 deterministic 所引事实缺席→INSUFFICIENT_EVIDENCE(全族一致)',
      hy_insuff and all(st.get(c['claim_id']) == 'INSUFFICIENT_EVIDENCE'
                        for c in hy_insuff))


def model_no_path(b, s):
    drop_hy(b, s)
    for c in b['claims']:
        if c['claim_type'] == 'level' and c['subtype'] == 'point' \
                and c.get('metric_id') == 'HY_OAS':
            c['attribution'] = 'model_inferred'


r = mutated(model_no_path)
st = statuses(r)
mv = next(x for x in r['verdicts'] if x['claim_id'] == 'CLM-20261114-0005')
check('C5 model 数值+无路径→强制 SEMANTIC_REVIEW(同族 deterministic=INSUFF,'
      '分道不串)',
      mv['status'] == 'SEMANTIC_REVIEW_REQUIRED'
      and any(st.get(c['claim_id']) == 'INSUFFICIENT_EVIDENCE'
              for c in hy_insuff if c['claim_id'] != 'CLM-20261114-0005')
      and r['publish']['gate_b_numeric_all_verified'] is False)


def strip_dxy_band_edge(b, s):
    pass  # 经 thresholds 注入(C8 专用)


th = cf.load_thresholds()
th2 = copy.deepcopy(th)
for e in th2.get('entries', []):
    if e.get('metric_id') == 'DXY':
        e['level'] = [lv for lv in (e.get('level') or []) if lv != 'band_edge']
r = cv.verify_bundle(copy.deepcopy(BUNDLE), snapshot=copy.deepcopy(SNAP),
                     thresholds=th2)
v = next(x for x in r['verdicts'] if x['claim_id'] == 'CLM-20261114-0015')
check('C6 deterministic 无验证路径(band_edge 对被抽)→NOT_VERIFIABLE+归因'
      '{路径/原因枚举/可否次级交叉}',
      v['status'] == 'NOT_VERIFIABLE'
      and v['nv_attribution']['path'] == 'level/band'
      and v['nv_attribution']['reason'] == 'no_verifier_path'
      and v['nv_attribution']['secondary_cross_check_possible'] is True)
check('C7 NV deterministic 单条不关发布门(gate_b 仍 True;model 面才强制)',
      r['publish']['gate_b_numeric_all_verified'] is True)

# ══ D INSUFFICIENT_EVIDENCE ══════════════════════════════════════
print()
print('=' * 72)
print('[D] INSUFFICIENT_EVIDENCE(引用必带值;§2)')
print('=' * 72)
r = mutated(lambda b, s: by_id(b, 'CLM-20261114-0001').update(evidence_refs=[]))
v = next(x for x in r['verdicts'] if x['claim_id'] == 'CLM-20261114-0001')
check('D1 空引用→INSUFFICIENT_EVIDENCE+披露',
      v['status'] == 'INSUFFICIENT_EVIDENCE' and v['disclosure'])

r = mutated(lambda b, s: by_id(b, 'CLM-20261114-0001')['evidence_refs'][0].update(value=None))
v = next(x for x in r['verdicts'] if x['claim_id'] == 'CLM-20261114-0001')
check('D2 无值引用→INSUFFICIENT_EVIDENCE(非证据不符硬红)',
      v['status'] == 'INSUFFICIENT_EVIDENCE')

# ══ E STALE 分级 ═════════════════════════════════════════════════
print()
print('=' * 72)
print('[E] STALE 分级(ratio=lag÷freshness.max_calendar_lag_days)')
print('=' * 72)


def make_stale(newobs):
    def fn(b, s):
        for x in s['facts']:
            if x['metric_id'] == 'JP_POLICY_RATE':
                x['observation_date'] = newobs
                days = (date.fromisoformat('2026-11-14')
                        - date.fromisoformat(newobs)).days
                for c in b['claims']:
                    if c['claim_type'] == 'observation_lag' \
                            and c.get('metric_id') == 'JP_POLICY_RATE':
                        c['value'] = days    # lag 计量同步重算(其主体=lag 本身)
    return fn


r = mutated(make_stale('2026-07-07'))          # 130d/60≈2.17
v = next(x for x in r['verdicts'] if x['claim_id'] == 'CLM-20261114-0012')
check('E1 ratio≈2.2→stale_level_2(130d/60d)',
      v['status'] == 'STALE' and v['stale']['tier'] == 'stale_level_2')

r = mutated(make_stale('2026-04-28'))          # 200d/60≈3.33
v = next(x for x in r['verdicts'] if x['claim_id'] == 'CLM-20261114-0012')
check('E2 ratio≈3.3→stale_level_3+入 current_frame_forbidden(禁入现状框架)',
      v['status'] == 'STALE' and v['stale']['tier'] == 'stale_level_3'
      and 'CLM-20261114-0012' in r['publish']['current_frame_forbidden'])

g = cv._stale_grade(None, None, cadence_source='x')
check('E3 节奏不可得=cadence_unknown(只披露不拦,如实注记)',
      g['tier'] == 'cadence_unknown' and '披露' in g['disclosure'])
check('E4 阈值表边界: ≤1 fresh/≤2 l1/≤3 l2/>3 l3',
      cv._stale_grade(60, 60, cadence_source='t')['tier'] == 'fresh'
      and cv._stale_grade(120, 60, cadence_source='t')['tier'] == 'stale_level_1'
      and cv._stale_grade(180, 60, cadence_source='t')['tier'] == 'stale_level_2'
      and cv._stale_grade(181, 60, cadence_source='t')['tier'] == 'stale_level_3')

# ══ F 写回+超时策略+确定性 ═══════════════════════════════════════
print()
print('=' * 72)
print('[F] apply_verdicts 写回/timeout_policy/双跑确定性')
print('=' * 72)
b2 = copy.deepcopy(BUNDLE)
cv.apply_verdicts(b2, BASE)
c = by_id(b2, 'CLM-20261114-0016')
vf = c['verification']
check('F1 verification 字段=契约§2 示例形状(status/checked_against/'
      'computed/delta/tolerance/checker_version)',
      set(('status', 'checked_against', 'computed', 'delta', 'tolerance',
           'checker_version')) <= set(vf)
      and vf['status'] == 'VERIFIED' and vf['checked_against'] == 'snapshot+thresholds'
      and vf['delta'] == 0.0 and vf['tolerance'] == 0.0
      and vf['checker_version'] == 'claim_verifier 1.0')
check('F2 STALE 写回带 stale 分级与披露',
      by_id(b2, 'CLM-20261114-0012')['verification']['stale']['tier']
      == 'stale_level_1'
      and by_id(b2, 'CLM-20261114-0012')['verification']['disclosure'])

r1 = json.dumps(verify(copy.deepcopy(BUNDLE), SNAP), sort_keys=True)
r2 = json.dumps(verify(copy.deepcopy(BUNDLE), SNAP), sort_keys=True)
check('F3 双跑裁决逐字节相等(零随机/零时钟依赖;as_of 取自快照)',
      r1 == r2)

tp = cv.timeout_policy(mutated(lambda b, s: by_id(
    b, 'CLM-20261114-0001').update(attribution='model_inferred',
                                    evidence_refs=[])))
check('F4 超时策略=剔除+显式披露清单(§4 不无限期卡死)',
      tp['removed_claim_ids'] == ['CLM-20261114-0001']
      and 'CLM-20261114-0001' in tp['disclosure'])
check('F5 空队列超时策略=无剔除披露',
      cv.timeout_policy(BASE)['removed_claim_ids'] == [])

# ══ G 纯度(Z1 同面)+CLI ═════════════════════════════════════════
print()
print('=' * 72)
print('[G] 纯度: 零模型/零环境变量/零网络/零随机+CLI 冒烟')
print('=' * 72)
SRC = open(os.path.join(ROOT, 'scripts', 'research_contract',
                        'claim_verifier.py'), 'r', encoding='utf-8').read()
check('G1 源码零模型客户端 import(openai/zhipu/bigmodel/glm/anthropic)',
      not any(k in SRC for k in ('import openai', 'import zhipu',
                                 'import bigmodel', 'from openai',
                                 'from anthropic', 'anthropic.'))
      and 'claude' not in SRC.lower().replace('checker', ''))
check('G2 源码零环境变量读取/零网络/零随机',
      'environ' not in SRC and 'socket' not in SRC
      and 'urllib' not in SRC and 'requests' not in SRC
      and 'random' not in SRC.replace('randomly', ''))

with tempfile.TemporaryDirectory() as td:
    bp, sp = os.path.join(td, 'b.json'), os.path.join(td, 's.json')
    with open(bp, 'w', encoding='utf-8') as f:
        json.dump(BUNDLE, f, ensure_ascii=False)
    with open(sp, 'w', encoding='utf-8') as f:
        json.dump(SNAP, f, ensure_ascii=False)
    env = dict(os.environ,
               MODEL_API_KEY='tripwire', MODEL_BASE_URL='http://tripwire',
               ANTHROPIC_API_KEY='tripwire', OPENAI_API_KEY='tripwire')
    o1 = subprocess.run([sys.executable, os.path.join(
        ROOT, 'scripts', 'research_contract', 'claim_verifier.py'),
        bp, sp, '--out', os.path.join(td, 'r1.json')],
        capture_output=True, text=True, env=env, cwd=ROOT)
    o2 = subprocess.run([sys.executable, os.path.join(
        ROOT, 'scripts', 'research_contract', 'claim_verifier.py'),
        bp, sp, '--out', os.path.join(td, 'r2.json')],
        capture_output=True, text=True, env=env, cwd=ROOT)
    ok_run = o1.returncode == 0 and o2.returncode == 0
    same = ok_run and open(os.path.join(td, 'r1.json'), 'rb').read() \
        == open(os.path.join(td, 'r2.json'), 'rb').read()
    with open(os.path.join(td, 'r1.json'), 'r', encoding='utf-8') as f:
        summ = json.load(f)['summary']
    check('G3 MODEL_* 绊线子进程双跑: 退出0+逐字节同输出+summary 与进程内一致',
          ok_run and same and summ == BASE['summary'])

print()
print('=' * 72)
print(f'结果: {len(PASSED)}通过 / {len(FAILED)}失败')
print('=' * 72)
if FAILED:
    for n, d in FAILED:
        print(f'  ❌ {n} {d}')
sys.exit(0 if not FAILED else 1)
