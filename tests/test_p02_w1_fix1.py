#!/usr/bin/env python3
"""IA-P02-W1-FIX1 专项测试 — CORE_PCE基期语义 + 关键字段类型拦截 + 生产加载负向回归

覆盖(IA-P02-W1-FIX1-DEV §九 A~G):
  A CORE_PCE基期: 2017=100官方单位/采集器标签同步/错误2012注入被识别/身份绑定序列
    被换被识别/make_fact与normalize_macro真实路径unit正确/数值观测日不变/无重新定基
  B 关键字段非法类型: status/criticality/frequency/value_type × {123,None,[],{},True}
    每项注入都被识别且点名metric_id+field+实际值; value_type允许缺失(make_fact缺省level)
  C 生产加载: 真实fact_engine.load_registry()加载临时非法注册表→受控RegistrySemanticsError,
    不静默加载,缓存不污染
  D 核心集合: SPX在核心集合; status/criticality非法注册表被拒(而非静默缩core)
  E 审计报告: 81项完整/CORE_PCE=FIXED含官方证据/总分类由程序重算(76/4/1/0)
  F 历史兼容: NVDA/AAPL/MSFT身份保持/合法注册表加载/无效来源fail-closed/镜像集合不漂移
  G 负向敏感性: CORE_PCE回退2012→正式加载失败; SPX.criticality=123→正式加载失败
    (硬断言,失败即本进程exit 1,非"清单非空"式软检查)
全程离线: 零网络、零真实GLM、零生产数据;fixture为SYNTHETIC。
"""
import json
import os
import shutil
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

def expect_errors(probs, mid, rule, field=None, msg_sub=None):
    for p in probs:
        if p['severity'] != 'error' or p['metric_id'] != mid or p['rule'] != rule:
            continue
        if field is not None and p.get('field') != field:
            continue
        if msg_sub is not None and msg_sub not in p.get('message', ''):
            continue
        return p
    return None


print("=" * 64)
print("P0-2 W1-FIX1: CORE_PCE基期 + 关键字段类型拦截 + 生产加载负向回归")
print("=" * 64)

import fact_engine as fe
import macro_collector as mc
import registry_semantics as rsem
import research_provenance as rp

REG_PATH = os.path.join(ROOT, 'config', 'metric_registry.json')
with open(REG_PATH, encoding='utf-8') as f:
    _REG = json.load(f)

def mutate(fn):
    reg = json.loads(json.dumps(_REG))
    fn(reg)
    return rsem.validate_registry(reg)

def set_field(mid, field, value):
    def _f(reg):
        for m in reg['metrics']:
            if m['metric_id'] == mid:
                if value is _MISSING:
                    m.pop(field, None)
                else:
                    m[field] = value
    return _f

class _Missing:
    pass
_MISSING = _Missing()

by_id = {m['metric_id']: m for m in _REG['metrics']}

# ══ A. CORE_PCE 基期 ═══════════════════════════════════════════════
print("\n[A] CORE_PCE 基期(FIX1-01/02)")
check("A1 注册表CORE_PCE: unit=index_point_2017, source_symbol=PCEPILFE",
      by_id['CORE_PCE']['unit'] == 'index_point_2017'
      and by_id['CORE_PCE']['source_symbol'] == 'PCEPILFE',
      f"unit={by_id['CORE_PCE']['unit']}")
check("A2 采集器SERIES_UNITS标签已同步2017=100,官方同步校验零问题",
      mc.SERIES_UNITS['CORE_PCE'] == ('index', '指数点(2017=100)')
      and rsem.collector_official_unit_problems(_REG, mc.SERIES_UNITS) == [],
      str(mc.SERIES_UNITS.get('CORE_PCE')))
p = mutate(set_field('CORE_PCE', 'unit', 'index_point_2012'))
hit = expect_errors(p, 'CORE_PCE', 'R-OFFICIAL-UNIT', 'unit', 'index_point_2017')
check("A3 unit回退index_point_2012→R-OFFICIAL-UNIT点名(消息含期望值与实际值)",
      hit is not None and 'index_point_2012' in hit['message'], str(hit))
p = mutate(set_field('CORE_PCE', 'source_symbol', 'CPIAUCSL'))
hit = expect_errors(p, 'CORE_PCE', 'R-OFFICIAL-SERIES', 'source_symbol', 'PCEPILFE')
check("A4 source_symbol换成他系列(CPIAUCSL)→R-OFFICIAL-SERIES身份绑定拦截"
      "(新序列自身合法不等于CORE_PCE换身份获授权)",
      hit is not None and 'CPIAUCSL' in hit['message'], str(hit))
saved = mc.SERIES_UNITS['CORE_PCE']
try:
    mc.SERIES_UNITS['CORE_PCE'] = ('index', '指数点(2012=100)')
    sync = rsem.collector_official_unit_problems(_REG, mc.SERIES_UNITS)
finally:
    mc.SERIES_UNITS['CORE_PCE'] = saved
hit = next((x for x in sync if x['metric_id'] == 'CORE_PCE'
            and x['rule'] == 'R-OFFICIAL-UNIT-SYNC'), None)
check("A5 采集器标签改回2012→R-OFFICIAL-UNIT-SYNC同步失败(点名+含两口径)",
      hit is not None and '2017=100' in hit['message'] and '2012=100' in hit['message'],
      str(sync))
AS_OF = "2026-10-25T08:00:00+08:00"
f1 = fe.make_fact('CORE_PCE', 118.6, '2026-09-30', AS_OF, 'macro_20261025.json',
                  'macro_collector')
check("A6 make_fact真实路径: unit=index_point_2017/数值118.6/观测日不变/value_type沿注册表",
      f1['unit'] == 'index_point_2017' and f1['value'] == 118.6
      and f1['observation_date'] == '2026-09-30' and f1['value_type'] == 'level',
      f"unit={f1['unit']} value={f1['value']}")
mf = fe.normalize_macro({'data': {'CORE_PCE': {'value': 118.6, 'date': '2026-09-30'}}},
                        AS_OF, 'macro_20261025.json')
check("A7 normalize_macro真实规范化路径同unit,数值/观测日不变",
      mf and mf[0]['metric_id'] == 'CORE_PCE' and mf[0]['unit'] == 'index_point_2017'
      and mf[0]['value'] == 118.6 and mf[0]['observation_date'] == '2026-09-30',
      str(mf and {k: mf[0][k] for k in ('unit', 'value', 'observation_date')}))
check("A8 无重新定基: 2017单位属既有价格类口径(PRICE_LIKE_UNITS),"
      "输入数值原样透传(A6/A7已证),无任何基期换算系数介入",
      'index_point_2017' in fe.PRICE_LIKE_UNITS and f1['value'] == 118.6
      and not any('rebase' in str(k) for k in f1))
# 其他4项受保护序列当前配置与官方一致(合法配置仍正常通过)
check("A9 受保护5序列(CPI/CORE_CPI/INDPRO/UMCSENT/CORE_PCE)现配置零官方规则问题",
      not [x for x in rsem.validate_registry(_REG)
           if x['rule'] in ('R-OFFICIAL-UNIT', 'R-OFFICIAL-SERIES')])

# ══ B. 关键字段非法类型 ═════════════════════════════════════════════
print("\n[B] 关键字段非法类型(FIX1-03): 4字段×5非法类型全识别")
ILLEGAL = [123, None, [], {}, True]
TYPE_RULES = {'status': 'R-STATUS-TYPE', 'criticality': 'R-CRITICALITY-TYPE',
              'frequency': 'R-FREQUENCY-TYPE', 'value_type': 'R-VALUETYPE-TYPE'}
b_ok = True
for fld, rule in TYPE_RULES.items():
    for bad in ILLEGAL:
        probs = mutate(set_field('SPX', fld, bad))
        hit = expect_errors(probs, 'SPX', rule, fld)
        if hit is None or repr(bad) not in hit['message']:
            b_ok = False
            print(f"    未识别/未点名: {fld}={bad!r} → {hit}")
check("B1 4字段×{123,None,[],{},True}=20项注入全部R-*-TYPE点名(消息含实际值)",
      b_ok)
probs = mutate(set_field('SPX', 'status', _MISSING))
check("B2 status缺失(键不存在)→R-STATUS-TYPE(Gate A过滤字段不得缺失)",
      expect_errors(probs, 'SPX', 'R-STATUS-TYPE', 'status') is not None)
probs = mutate(set_field('SPX', 'criticality', _MISSING))
check("B2b criticality缺失→R-CRITICALITY-TYPE",
      expect_errors(probs, 'SPX', 'R-CRITICALITY-TYPE', 'criticality') is not None)
probs = mutate(set_field('SPX', 'frequency', _MISSING))
check("B2c frequency缺失→R-FREQUENCY-TYPE",
      expect_errors(probs, 'SPX', 'R-FREQUENCY-TYPE', 'frequency') is not None)
# value_type缺失=合法历史兼容(make_fact缺省level),不因可选而放行显式非法类型(B1已证)
probs = mutate(set_field('SPX', 'value_type', _MISSING))
vt_errs = [x for x in probs if x['metric_id'] == 'SPX' and x.get('field') == 'value_type'
           and x['severity'] == 'error']
check("B3 value_type允许缺失(历史兼容:make_fact m.get('value_type','level'))——"
      "缺失零error,在场非法类型才拦截",
      not vt_errs, str(vt_errs))
probs = mutate(set_field('SPX', 'status', 'activ'))
check("B4 合法类型但枚举外('activ')→R-STATUS-ENUM(拼写漂移≠类型错误,分层报告)",
      expect_errors(probs, 'SPX', 'R-STATUS-ENUM', 'status') is not None
      and expect_errors(probs, 'SPX', 'R-STATUS-TYPE', 'status') is None)
probs = mutate(set_field('SPX', 'value_type', 'weird_new_type'))
check("B5 合法字符串value_type未确认词汇→维持review不拦截(不擅自升error)",
      any(x['rule'] == 'R-VALUETYPE-ENUM' and x['severity'] == 'review'
          for x in probs if x['metric_id'] == 'SPX')
      and not [x for x in probs if x['metric_id'] == 'SPX'
               and x.get('field') == 'value_type' and x['severity'] == 'error'])

# ══ C. 生产加载拦截(真实load_registry,临时注册表) ═══════════════════
print("\n[C] 生产加载: 非法临时注册表→受控异常,不静默加载")
tmpd = tempfile.mkdtemp(prefix='w1f1-')

def temp_registry(mutator):
    reg = json.loads(json.dumps(_REG))
    mutator(reg)
    p = os.path.join(tmpd, 'reg_bad.json')
    with open(p, 'w', encoding='utf-8') as fh:
        json.dump(reg, fh, ensure_ascii=False)
    return p

def expect_load_reject(name, mutator, msg_needles):
    path = temp_registry(mutator)
    raised, msg = None, ''
    try:
        fe.load_registry(path, force=True)
    except rsem.RegistrySemanticsError as e:
        raised, msg = True, str(e)
    except Exception as e:
        raised, msg = 'wrong-type', f'{type(e).__name__}: {e}'
    ok = raised is True and all(n in msg for n in msg_needles)
    check(name, ok, msg[:220])
    return ok

try:
    expect_load_reject(
        "C1 CORE_PCE unit回退2012→load_registry抛RegistrySemanticsError"
        "(点名CORE_PCE/R-OFFICIAL-UNIT/期望与实际)",
        set_field('CORE_PCE', 'unit', 'index_point_2012'),
        ['CORE_PCE', 'R-OFFICIAL-UNIT', 'index_point_2017', 'index_point_2012'])
    expect_load_reject(
        "C2 SPX.status=123→load_registry拒绝(R-STATUS-TYPE点名)",
        set_field('SPX', 'status', 123), ['SPX', 'R-STATUS-TYPE', 'status'])
    expect_load_reject(
        "C3 SPX.criticality=123→load_registry拒绝(R-CRITICALITY-TYPE点名)",
        set_field('SPX', 'criticality', 123), ['SPX', 'R-CRITICALITY-TYPE'])
    expect_load_reject(
        "C4 SPX.frequency=123→load_registry拒绝(R-FREQUENCY-TYPE点名)",
        set_field('SPX', 'frequency', 123), ['SPX', 'R-FREQUENCY-TYPE'])
    expect_load_reject(
        "C5 SPX.value_type=123→load_registry拒绝(R-VALUETYPE-TYPE点名)",
        set_field('SPX', 'value_type', 123), ['SPX', 'R-VALUETYPE-TYPE'])
    expect_load_reject(
        "C6 CORE_PCE换序列→load_registry拒绝(R-OFFICIAL-SERIES身份绑定)",
        set_field('CORE_PCE', 'source_symbol', 'INDPRO'),
        ['CORE_PCE', 'R-OFFICIAL-SERIES', 'PCEPILFE', 'INDPRO'])
    # 拒绝后缓存不被污染: 默认注册表仍完好
    fe.load_registry(force=True)
    check("C7 逐项拒绝后默认注册表可正常重载(缓存无污染)",
          len(fe.load_registry()['by_id']) == 81
          and fe.metric('SPX')['criticality'] == 'core'
          and fe.metric('CORE_PCE')['unit'] == 'index_point_2017')
finally:
    shutil.rmtree(tmpd, ignore_errors=True)
    fe.load_registry(force=True)

# ══ D. 核心集合/Gate A回归 ═════════════════════════════════════════
print("\n[D] Gate A核心集合: 非法注册表被拒,而非静默缩core")
check("D1 对照组合法注册表: 81项/active 80/core 32/SPX属核心",
      len(_REG['metrics']) == 81 and len(rp.core_metric_ids()) == 32
      and 'SPX' in rp.core_metric_ids() and len(rp.active_registry_metrics()) == 80,
      f"core={len(rp.core_metric_ids())}")
tmpd = tempfile.mkdtemp(prefix='w1f1-d')
try:
    # 若非法注册表被静默加载,SPX会被字面'active'过滤逐出core→core=31的"合格"Gate A
    # ——正确行为是加载即拒绝,core集合根本不产生
    path = temp_registry(set_field('SPX', 'criticality', 123))
    tmpd_keep = path  # temp_registry写入tmpd
    rejected = False
    try:
        reg_bad = fe.load_registry(path, force=True)
        core_after = len(rp.core_metric_ids())  # 若加载成功即缺陷
    except rsem.RegistrySemanticsError:
        rejected = True
    check("D2 SPX.criticality=123→整表拒绝,不产生'core静默缩为31'的合法假象",
          rejected, '非法注册表被静默加载!' if not rejected else '')
    check("D3 拒绝后rp.core_metric_ids()仍为32含SPX(权威集合未被污染)",
          len(rp.core_metric_ids()) == 32 and 'SPX' in rp.core_metric_ids())
finally:
    shutil.rmtree(tmpd, ignore_errors=True)
    fe.load_registry(force=True)

# ══ E. 审计报告修订 ════════════════════════════════════════════════
print("\n[E] 审计报告(FIX1-05)")
with open(os.path.join(ROOT, 'docs', 'P0_2_W1_REGISTRY_AUDIT.json'), encoding='utf-8') as f:
    audit = json.load(f)
items = audit['items']
aud_ids = [i['metric_id'] for i in items]
recomputed = {r: sum(1 for i in items if i['result'] == r) for r in
              ('VERIFIED_CONSISTENT', 'FIXED', 'REVIEW', 'BLOCKED')}
check("E1 81项逐项清单完整无重复",
      len(aud_ids) == 81 and len(set(aud_ids)) == 81 and set(aud_ids) == set(by_id))
cp = next(i for i in items if i['metric_id'] == 'CORE_PCE')
check("E2 CORE_PCE记录为FIXED,含原错误单位与官方证据",
      cp['result'] == 'FIXED' and 'index_point_2012' in json.dumps(cp, ensure_ascii=False)
      and 'PCEPILFE' in json.dumps(cp, ensure_ascii=False))
check("E2b 官方证据含来源页与核验日期2026-10-29",
      any('fred.stlouisfed.org/series/PCEPILFE' in json.dumps(e, ensure_ascii=False)
          for e in cp['evidence'])
      and '2026-10-29' in json.dumps(cp, ensure_ascii=False))
check("E3 总分类与81项记录逐项重算一致(不写死冒充审计)",
      audit['totals']['results'] == recomputed, f"{audit['totals']['results']} vs {recomputed}")
check("E4 实际分类=76 VERIFIED/4 FIXED/1 REVIEW/0 BLOCKED",
      recomputed == {'VERIFIED_CONSISTENT': 76, 'FIXED': 4, 'REVIEW': 1, 'BLOCKED': 0},
      str(recomputed))
check("E5 修订历史留痕: 首轮误标VERIFIED与FIX1改判均有记录",
      len(audit.get('revision_history', [])) == 2
      and '误标' in json.dumps(audit['revision_history'][0], ensure_ascii=False)
      and 'FIX1' in json.dumps(audit['revision_history'][1], ensure_ascii=False))
oue = audit.get('official_units_evidence', {})
check("E6 官方单位证据块: 5序列独立权威映射(PCEPILFE=index_point_2017)",
      len(oue.get('series', {})) == 5
      and oue['series']['PCEPILFE']['unit'] == 'index_point_2017'
      and oue['series']['CPIAUCSL']['unit'] == 'index_point_1982_84')
check("E7 权威映射独立于注册表(rsem常量与官方证据一致)",
      rsem.OFFICIAL_FRED_INDEX_UNITS == {s: v['unit'] for s, v in oue['series'].items()}
      and rsem.OFFICIAL_METRIC_SERIES == {v['bound_metric']: s for s, v in oue['series'].items()})

# ══ F. 历史兼容(W1正向能力继承) ════════════════════════════════════
print("\n[F] 历史兼容: W1成果不回归")
check("F1 NVDA/AAPL/MSFT身份保持single_stock",
      all(by_id[m]['identity']['instrument'] == 'single_stock'
          for m in ('NVDA', 'AAPL', 'MSFT')))
errs = [p for p in rsem.validate_registry(_REG) if p['severity'] == 'error']
check("F2 合法完整注册表通过全部新规则(0 error)", not errs, str(errs[:3]))
check("F3 默认注册表可正常加载(81项)",
      len(fe.load_registry(force=True)['by_id']) == 81)
f2 = fe.make_fact('CORE_PCE', 118.6, '2026-09-30', AS_OF, 'macro_20261025.json',
                  'shadow_module')
src_probs = rp.fact_source_problems(f2, by_id['CORE_PCE'],
                                    {'status': 'EXACT', 'file': 'macro_20261025.json'},
                                    {'CORE_PCE': f2})
check("F4 无效来源仍fail-closed(基期修复不授予来源授权)",
      any('collector' in p for p in src_probs), str(src_probs))
import trading_calendar as tc
check("F5 镜像集合不因FIX1漂移(单位/日历/来源三锁)",
      rsem.KNOWN_UNITS == frozenset(fe.PRICE_LIKE_UNITS | fe.RATE_UNITS | fe.COUNT_UNITS)
      and rsem.KNOWN_CALENDARS == frozenset(tc.MARKETS)
      and rsem.KNOWN_SOURCES == frozenset(rp._AUTHORIZED_COLLECTORS) | {'macro_collector(derived)'})

# ══ G. 负向敏感性(显式重申两指名场景) ═══════════════════════════════
print("\n[G] 负向敏感性: 指名场景失败必须传导为本测试进程失败")
tmpd = tempfile.mkdtemp(prefix='w1f1-g')
try:
    # G1: 若有人把CORE_PCE.unit改回2012,正式加载必须失败(否则下方check红→exit 1)
    path = temp_registry(set_field('CORE_PCE', 'unit', 'index_point_2012'))
    try:
        fe.load_registry(path, force=True)
        g1 = False
    except rsem.RegistrySemanticsError as e:
        g1 = 'R-OFFICIAL-UNIT' in str(e) and 'CORE_PCE' in str(e)
    check("G1 CORE_PCE回退2012→正式load_registry确实失败(可解释)", g1)
    # G2: SPX.criticality整数→正式加载失败
    path = temp_registry(set_field('SPX', 'criticality', 123))
    try:
        fe.load_registry(path, force=True)
        g2 = False
    except rsem.RegistrySemanticsError as e:
        g2 = 'R-CRITICALITY-TYPE' in str(e) and 'SPX' in str(e)
    check("G2 SPX.criticality=123→正式load_registry确实失败(可解释)", g2)
finally:
    shutil.rmtree(tmpd, ignore_errors=True)
    fe.load_registry(force=True)

print("\n" + "=" * 64)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 64)
sys.exit(0 if FAIL == 0 else 1)
