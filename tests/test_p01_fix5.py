#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P0-1-FIX5 对抗测试(FIX5-01/02/03/04闭环验收;DEF-F4-001/002)

覆盖(指令§十一矩阵,全部真实模块+临时目录,无源码片段复制作通过证据):
A. 来源一致性: collector授权/批次文件匹配/EXACT·FALLBACK身份/派生链追踪/
   data_dir两级口径(当前正式流程核验文件在场,纯重验以持久化状态为准);
B. 事实质量一致性: quality_status↔issues按fact_engine.grade_issues同一函数
   重算一致(双向矛盾均拒);结构非法;合法WARN/DEGRADED/FAIL不误伤;
C. 观测日期严格性: 完整YYYY-MM-DD真实日历日期(无[:10]截断洗白);构建端
   make_fact/validate_fact与核验端同一结论;月频/日频既有语义不破坏;
D. 来源状态fail-closed: 缺失/None/列表/字符串/通道缺失/通道非对象/状态值
   非法/EXACT缺file/FALLBACK缺真实日期→不可证明(effective=None),无未受控
   异常;正常MISSING/FALLBACK/READ_FAIL合法降级披露不误伤;
E. 端到端: 正常构建/PASS进包/合法DEGRADED披露/非法来源·状态·issues·日期
   阻断装配器与周报预检/已有合格报告保护/长期观察状态不被未验证数据修改。

fixture: tests/fixt.py 真实注册表全active(32 core+47 important+1 context)
SYNTHETIC采集→真实snapshot_builder/装配/锚点/观察器;GLM全程mock(零付费
零网络);临时目录隔离不触生产;断言针对真实函数返回值/磁盘字节/退出码。
"""
import os
import sys
import io
import json
import copy
import shutil
import tempfile
import contextlib
import unittest.mock as mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts'))

PASS = FAIL = 0


def check(name, ok, detail=''):
    global PASS, FAIL
    mark = '✅' if ok else '❌'
    print(f"  {mark} {name}" + (f" [{detail}]" if detail and not ok else ''))
    PASS, FAIL = PASS + (1 if ok else 0), FAIL + (0 if ok else 1)


def quiet(fn, *a, **kw):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **kw)


import research_provenance as rp          # noqa: E402
import fact_engine as fe                  # noqa: E402
import snapshot_builder as sb             # noqa: E402
import data_assembler as da               # noqa: E402
import report_generator as rg             # noqa: E402
import daily_prediction_observer as dpo   # noqa: E402
import fixt                                # noqa: E402

DAY = '20261024'
PREV_D = '20261023'
DEL = object()      # 字段删除哨兵


def _DT(*args):
    class _C:
        @staticmethod
        def now():
            import datetime as _dt
            return _dt.datetime(*args)

        @staticmethod
        def strptime(s, f):
            import datetime as _dt
            return _dt.datetime.strptime(s, f)
    return _C


DT_DAY = _DT(2026, 10, 24, 8, 0, 0)


class _GLM:
    """付费GLM调用mock(仅网络侧;发布事务/预检/读取器全真实)。"""

    def __init__(self):
        self.text = ('# 投资周报(SYNTHETIC FIX5矩阵)\n\n' + '本周市场综述与分资产回顾。' * 80)
        self.calls = 0

    def __call__(self, system_prompt, user_prompt, max_tokens=32000, timeout=900):
        self.calls += 1
        return self.text


def mutated(base, mid, **fields):
    """deepcopy后定点篡改mid事实字段(DEL=删除键)。"""
    snap = copy.deepcopy(base)
    for f in snap['facts']:
        if f.get('metric_id') == mid:
            for k, v in fields.items():
                if v is DEL:
                    f.pop(k, None)
                else:
                    f[k] = v
            return snap
    raise AssertionError(f'fixture无指标{mid}')


def illegal_has(rec, kw):
    return rec['effective'] is None and any(kw in s for s in rec['illegal_quality'])


def no_exception(fn, *a, **kw):
    """返回(结果, 是否无未受控异常)。"""
    try:
        return fn(*a, **kw), True
    except Exception:   # noqa: BLE001
        return None, False


# ══ 共享真实基线: 全active真实构建日(磁盘保留,供data_dir口径/E矩阵) ══
BASE = tempfile.mkdtemp(prefix='fix5-base-')
SNAP, SNAP_PATH, PATHS = fixt.build_full_day(BASE, DAY)
BASE_DAILY = PATHS['daily']


def _run_da_main(root):
    """真实data_assembler.main(补丁DATA_DIR/datetime);返回退出码。"""
    with mock.patch.object(da, 'DATA_DIR', os.path.join(root, 'data')), \
         mock.patch.object(da, 'datetime', DT_DAY):
        try:
            quiet(da.main)
            return 0
        except SystemExit as e:
            return e.code


def _preflight(root):
    """真实周报预检verify_research_inputs;返回(ok, problems)。"""
    with mock.patch.object(rg, 'DATA_DIR', os.path.join(root, 'data')), \
         mock.patch.object(rg, 'datetime', DT_DAY):
        r = quiet(rg.verify_research_inputs)
        return r[0], r[1]


def _disk_tamper(snap_path, fn):
    disk = json.load(open(snap_path, encoding='utf-8'))
    fn(disk)
    with open(snap_path, 'w', encoding='utf-8') as f:
        json.dump(disk, f, ensure_ascii=False)


print("=" * 64)
print("IA-P0-1-FIX5 对抗测试: 来源一致性/quality-issues一致/严格日期/来源状态fail-closed")
print("=" * 64)

# ════════════════════════════════════════════════════════════════════
print("\n── A. 来源一致性(FIX5-01)")

rec = rp.recompute_gate_a(SNAP, data_dir=BASE_DAILY, trusted_root=BASE)
check("A0 对照: 真实全active构建(带采集目录)→PASS零非法",
      # W2-FIX1(§6.4)修订: 月频事实WARN档不计入counts桶——全active零FAIL/零
      # DEGRADED且PASS+WARN总数覆盖全部active(78)即"全部合格"
      rec['effective'] == 'PASS' and rec['illegal_quality'] == []
      and rec['counts']['PASS'] + sum(
          1 for f in SNAP['facts']
          if f.get('quality_status') == 'WARN') >= 78
      and rec['counts']['FAIL'] == 0 and rec['counts']['DEGRADED'] == 0,
      f"eff={rec['effective']} illegal={rec['illegal_quality'][:2]}")

s = mutated(SNAP, 'SPX', **{'source': {'collector': 'fictitious_collector',
                                       'file': 'global_20261024.json'}})
r = rp.recompute_gate_a(s)
check("A1 伪造collector(fictitious_collector)→不可证明+点名权威来源",
      illegal_has(r, 'collector与指标权威来源不符') and 'fictitious_collector' in r['illegal_quality'][0],
      str(r['illegal_quality'][:1]))

s = mutated(SNAP, 'SPX', **{'source': {'collector': 'macro_collector',
                                       'file': 'global_20261024.json'}})
r = rp.recompute_gate_a(s)
check("A2 collector为他人合法通道(macro_collector冒充SPX)→与指标来源不符拒",
      illegal_has(r, 'collector与指标权威来源不符'),
      str(r['illegal_quality'][:1]))

s = mutated(SNAP, 'SPX', **{'source': {'collector': 'global_market_collector',
                                       'file': 'file_does_not_exist.json'}})
r = rp.recompute_gate_a(s)
check("A3 source.file与当次采集批次不一致(不存在文件)→拒",
      illegal_has(r, 'source.file与当次采集批次不一致'),
      str(r['illegal_quality'][:1]))

s = mutated(SNAP, 'SPX', **{'source': {'collector': 'global_market_collector',
                                       'file': 'macro_20261024.json'}})
r = rp.recompute_gate_a(s)
check("A4 事实声明他人通道批次文件(macro_*)→批次不一致拒",
      illegal_has(r, 'source.file与当次采集批次不一致'),
      str(r['illegal_quality'][:1]))

check("A5 对照: 真实EXACT通道(file_date==当日,事实file==批次file)",
      all(st.get('status') == 'EXACT' and st.get('file_date') == DAY
          for st in SNAP['sources_status'].values())
      and all(f['source']['file'] == SNAP['sources_status']['global']['file']
              for f in SNAP['facts'] if f['metric_id'] == 'SPX'))

with tempfile.TemporaryDirectory() as tdf:
    fixt.write_collectors(tdf, PREV_D)      # 前一日文件名→当日目标回退
    # 目标日无精确文件,但payload观测日=obs_for(DAY)=前一日收盘
    os.makedirs(os.path.join(tdf, 'out'), exist_ok=True)
    snap_fb = sb.build_snapshot(target_ymd=DAY, data_dir=tdf, trusted_root=tdf,
                                out_dir=os.path.join(tdf, 'out'),
                                as_of=fixt.as_of_for(DAY))
r = rp.recompute_gate_a(snap_fb)
check("A6 对照: 真实FALLBACK(保留真实旧文件日期+lag_days,事实file=回退文件)→PASS",
      r['effective'] == 'PASS'
      and all(st['status'] == 'FALLBACK' and st['file_date'] == PREV_D
              and st['lag_days'] == 1 for st in snap_fb['sources_status'].values())
      and next(f for f in snap_fb['facts'] if f['metric_id'] == 'SPX')['source']['file']
      == snap_fb['sources_status']['global']['file'],
      f"eff={r['effective']} ss={ {k: v.get('status') for k, v in snap_fb['sources_status'].items()} }")

s = copy.deepcopy(snap_fb)
for st in s['sources_status'].values():
    st['status'] = 'EXACT'      # 旧文件批次冒充当日EXACT(file_date仍是前一日)
r = rp.recompute_gate_a(s)
check("A7 FALLBACK冒充EXACT(file_date≠当日)→批次身份不可证明拒",
      illegal_has(r, 'EXACT但file_date'),
      str([x for x in r['illegal_quality'] if 'EXACT' in x][:1]))

s = copy.deepcopy(SNAP)
s['sources_status']['china'] = {'status': 'MISSING'}   # 通道声明缺失而事实在场
r = rp.recompute_gate_a(s)
check("A8 通道声明MISSING而事实在场→批次冲突拒(不作为有效证据)",
      illegal_has(r, '批次冲突'),
      str([x for x in r['illegal_quality'] if '批次冲突' in x][:1]))

r10 = next(f for f in SNAP['facts'] if f['metric_id'] == 'REAL_10Y')
r = rp.recompute_gate_a(SNAP)
check("A9 对照: 合法派生来源(REAL_10Y collector=fact_engine+calc_ref+输入在场)",
      r10['source']['collector'] == 'fact_engine'
      and bool(r10.get('calculation_ref'))
      and r['effective'] == 'PASS'
      and not any('REAL_10Y' in x for x in r['illegal_quality']))

s = mutated(SNAP, 'REAL_10Y', **{'source': {'collector': 'macro_collector',
                                            'file': 'derived'}})
r = rp.recompute_gate_a(s)
check("A10a 派生指标collector非法(REAL_10Y冒充macro_collector)→拒",
      illegal_has(r, 'collector非法'),
      str([x for x in r['illegal_quality'] if 'collector' in x][:1]))

s = mutated(SNAP, 'REAL_10Y', calculation_ref=DEL)
r = rp.recompute_gate_a(s)
check("A10b 派生缺calculation_ref(计算模块/依据不可追溯)→拒",
      illegal_has(r, '派生事实缺calculation_ref'),
      str([x for x in r['illegal_quality'] if 'calculation_ref' in x][:1]))

s = copy.deepcopy(SNAP)
s['facts'] = [f for f in s['facts'] if f['metric_id'] != 'NFP']
r = rp.recompute_gate_a(s)
check("A10c NFP_MOM_K缺输入事实NFP(计算依据不可追踪)→拒",
      illegal_has(r, '派生输入事实NFP不在场'),
      str([x for x in r['illegal_quality'] if '派生输入' in x][:1]))

# A11 data_dir两级口径: 假批次内部完全自洽(**规范文件名**FALLBACK——FIX6后
# 非规范名在两种口径都被身份层拒,ghost_20261024.json已不可构造此对照)——
# 纯重验口径下结构通过(持久化证据自洽),当前正式流程口径(data_dir)下文件
# 不存在→拒。部分篡改(只改个别事实)在两种口径下都会被批次一致性核出(A3/A16)
s = copy.deepcopy(SNAP)
_real_g = s['sources_status']['global']['file']
s['sources_status']['global'] = {'status': 'FALLBACK',
                                 'file': 'global_20261020.json',
                                 'file_date': '20261020', 'lag_days': 4}
_n = 0
for f in s['facts']:
    if isinstance(f.get('source'), dict) and f['source'].get('file') == _real_g:
        f['source']['file'] = 'global_20261020.json'
        _n += 1
r_pure = rp.recompute_gate_a(s)                     # 纯重验(无目录)
r_formal = rp.recompute_gate_a(s, data_dir=BASE_DAILY, trusted_root=BASE)   # 当前正式流程
check("A11 内部自洽的幽灵批次: 纯重验口径结构通过;正式口径核出文件不存在→拒"
      "(两级口径职责差异显式可验,不矛盾: 后者多验'文件在场'这一事实)",
      _n >= 30 and r_pure['effective'] == 'PASS'
      and r_formal['effective'] is None
      and any('来源文件在采集目录不存在' in p
              for p in r_formal.get('sources_problems', [])),
      f"renamed={_n} pure={r_pure['effective']} formal={r_formal['effective']}")

# ════════════════════════════════════════════════════════════════════
print("\n── B. 事实质量一致性(FIX5-02)")

check("B1 对照: PASS+无严重issues(真实构建)→PASS",
      rp.recompute_gate_a(SNAP)['effective'] == 'PASS')

_FAIL_ISSUE = [{'category': 'fixture', 'severity': 'FAIL', 'message': '模拟严重问题'}]
_DEG_ISSUE = [{'category': 'fixture', 'severity': 'DEGRADED', 'message': '模拟降级'}]
_WARN_ISSUE = [{'category': 'fixture', 'severity': 'WARN', 'message': '模拟提示'}]

s = mutated(SNAP, 'SPX', quality_status='PASS', issues=_FAIL_ISSUE)
r = rp.recompute_gate_a(s)
check("B2 PASS+FAIL issue→声明与依据矛盾拒",
      illegal_has(r, 'quality_status') and "与issues重算'FAIL'不一致" in r['illegal_quality'][0],
      str(r['illegal_quality'][:1]))

s = mutated(SNAP, 'UMCSENT', quality_status='DEGRADED', issues=_FAIL_ISSUE)
r = rp.recompute_gate_a(s)
check("B3 DEGRADED+FAIL issue(应为FAIL)→拒",
      illegal_has(r, '与issues重算'),
      str(r['illegal_quality'][:1]))

s = mutated(SNAP, 'BEI_10Y', quality_status='WARN', issues=_WARN_ISSUE)
r = rp.recompute_gate_a(s)
# W2-FIX1(§6.4)修订: 基线SNAP的13个月频事实已为WARN档(不计入counts桶),
# 期望计数自SNAP实际counts推导(BEI_10Y原为PASS→WARN则PASS-1),不再硬编码77
_b4_pass = SNAP['quality']['counts']['PASS'] - (
    1 if next(f for f in SNAP['facts']
              if f['metric_id'] == 'BEI_10Y').get('quality_status') == 'PASS' else 0)
check("B4 对照: WARN+WARN issue→合法(WARN为独立档位不计入counts不降级,"
      "声明与重算一致,既有语义)",
      r['effective'] == 'PASS'
      and r['counts'] == {'PASS': _b4_pass, 'DEGRADED': 0, 'FAIL': 0}
      and 'BEI_10Y' not in r['noncore_fail'] + r['noncore_degraded']
      and not r['illegal_quality'],
      f"eff={r['effective']} counts={r['counts']}")

s = mutated(SNAP, 'UMCSENT', quality_status='FAIL', issues=_FAIL_ISSUE)
_c = copy.deepcopy(SNAP['quality']['counts'])
# W2-FIX1(§6.4)修订: UMCSENT(月频)基线已为WARN档(不在PASS计数桶内),
# 仅当原档位为PASS时才递减(同fix1套件§7修正,断言语义不变)
if next(f for f in SNAP['facts'] if f['metric_id'] == 'UMCSENT').get('quality_status') == 'PASS':
    _c['PASS'] -= 1
_c['FAIL'] += 1
s['quality']['counts'] = _c
s['quality']['overall'] = 'FAIL'
s['gate_a']['status'] = 'DEGRADED'
r = rp.recompute_gate_a(s)
g, why = rp.gate_status(s)
check("B5 对照: FAIL+FAIL issue→合法非核心FAIL(降级披露,不升级全局FAIL)",
      r['noncore_fail'] == ['UMCSENT'] and r['effective'] == 'DEGRADED'
      and not any('UMCSENT=quality_status' in x for x in r['illegal_quality'])
      and g == 'DEGRADED',
      f"eff={r['effective']} gate={g} {why[:60]}")

s = mutated(SNAP, 'UMCSENT', quality_status='FAIL', issues=[])
r = rp.recompute_gate_a(s)
check("B6 无FAIL依据虚报FAIL→拒(反向矛盾同样不可证明)",
      illegal_has(r, '与issues重算'),
      str(r['illegal_quality'][:1]))

s = mutated(SNAP, 'SPX', issues=DEL)
r = rp.recompute_gate_a(s)
check("B7 issues缺失(键删除)→质量依据不可核验拒",
      illegal_has(r, 'issues缺失/非列表'),
      str(r['illegal_quality'][:1]))

s = mutated(SNAP, 'SPX', issues='无问题')
r = rp.recompute_gate_a(s)
check("B8 issues非对象(字符串)→拒",
      illegal_has(r, 'issues缺失/非列表'),
      str(r['illegal_quality'][:1]))

s = mutated(SNAP, 'SPX', issues=[{'category': 'x', 'severity': 'FATAL', 'message': 'm'}])
r = rp.recompute_gate_a(s)
check("B9 issue.severity非法(FATAL)→拒",
      illegal_has(r, 'severity非法'),
      str(r['illegal_quality'][:1]))

s = mutated(SNAP, 'SPX', quality_status='PASS',
            issues=_WARN_ISSUE + _DEG_ISSUE)
r = rp.recompute_gate_a(s)
s2 = mutated(SNAP, 'SPX', quality_status='DEGRADED',
             issues=_WARN_ISSUE + _DEG_ISSUE)
r2 = rp.recompute_gate_a(s2)
check("B10 混合severity: PASS+[WARN,DEGRADED]→拒;DEGRADED+[WARN,DEGRADED]→合法"
      "(重算取最严重,与grade_issues同函数)",
      illegal_has(r, '与issues重算') and r2['counts']['DEGRADED'] == 1
      and r2['effective'] == 'DEGRADED',
      f"r1={r['effective']} r2={r2['effective']}")

check("B11 复用既有分级: fact_issues_problems重算==fe.grade_issues(同一函数无第二套)",
      all(fe.grade_issues(f.get('issues', [])) == f['quality_status']
          for f in SNAP['facts']
          if f.get('metric_id') in rp.active_registry_metrics()
          and f.get('quality_status') in rp.FACT_QUALITY))

# ════════════════════════════════════════════════════════════════════
print("\n── C. 观测日期严格性(FIX5-03)")

for tag, od, kw in (
        ('C2 非法后缀INVALID', '2026-10-23INVALID', 'observation_date非法'),
        ('C3 非法后缀abc', '2026-10-23abc', 'observation_date非法'),
        ('C4 日历不存在(2026-02-30)', '2026-02-30', 'observation_date非法'),
        ('C5 空字符串', '', 'observation_date缺失'),
        ('C6 None', None, 'observation_date缺失'),
        ('C7 非字符串(123)', 123, 'observation_date缺失'),
        ('C8 未来观测日', '2026-10-25', '晚于研究截止')):
    s = mutated(SNAP, 'SPX', observation_date=od)
    r = rp.recompute_gate_a(s)
    check(f"{tag}→拒", r['effective'] is None
          and any(kw in x for x in r['illegal_quality']),
          str([x for x in r['illegal_quality'] if 'observation_date' in x
               or '晚于' in x][:1]))

check("C1 对照: 合法ISO日期(真实构建全部事实)→PASS(零日期非法)",
      rp.recompute_gate_a(SNAP)['effective'] == 'PASS'
      and not any('observation_date' in x for x in
                  rp.recompute_gate_a(SNAP)['illegal_quality']))

f_bad = fe.make_fact('SPX', 7659.44, '2026-10-23abc', fixt.as_of_for(DAY),
                     'global_20261024.json', 'global_market_collector')
iss = fe.validate_fact(f_bad, {'close': 7659.44, 'date': '2026-10-23abc'},
                       fe.metric('SPX'), as_of_date='2026-10-24')
check("C9 构建端同一结论: make_fact不截断原样保留+validate_fact按FAIL披露"
      "(规范化在make_fact,下游无二次猜测)",
      f_bad['observation_date'] == '2026-10-23abc'
      and any(i['severity'] == 'FAIL' and '观测日' in i['message'] for i in iss)
      and rp.parse_iso_date('2026-10-23abc') is None
      and rp.parse_iso_date('2026-02-30') is None
      and rp.parse_iso_date('2026-10-23') is not None)

m = next(f for f in SNAP['facts'] if f['metric_id'] == 'UMCSENT')
w = next(f for f in SNAP['facts'] if f['metric_id'] == 'ICSA')
# W2-FIX1(§6.4)修订: 无release_date的月频事实现为WARN档(发布时间未验证披露,
# 独立合法档位不降级)——"既有语义不破坏"=无FAIL/DEGRADED;周频ICSA无此披露
check("C10 对照: 月频(观测日=上月)/周频(滞后2日)既有语义不破坏"
      "(月频按W2-FIX1以WARN披露发布时间未验证)",
      m['observation_date'] == '2026-09-01' and w['observation_date'] == '2026-10-22'
      and m['quality_status'] == 'WARN'
      and any(i['category'] == 'release' and 'RELEASE_UNKNOWN' in i['message']
              for i in m['issues'])
      and w['quality_status'] == 'PASS')

f8 = fe.make_fact('SPX', 7659.44, '20261023', fixt.as_of_for(DAY),
                  'global_20261024.json', 'global_market_collector')
check("C11 YYYYMMDD在规范化阶段转ISO(采集端语义不变)",
      f8['observation_date'] == '2026-10-23')

# ════════════════════════════════════════════════════════════════════
print("\n── D. 来源状态fail-closed(FIX5-04)")

check("D1 对照: 合法完整sources_status→PASS",
      rp.recompute_gate_a(SNAP)['effective'] == 'PASS')

with tempfile.TemporaryDirectory() as tdm:
    fixt.write_collectors(tdm, DAY, missing=('UMCSENT',))
    os.makedirs(os.path.join(tdm, 'out'), exist_ok=True)
    snap_m = sb.build_snapshot(target_ymd=DAY, data_dir=tdm, trusted_root=tdm,
                               out_dir=os.path.join(tdm, 'out'),
                               as_of=fixt.as_of_for(DAY))
r = rp.recompute_gate_a(snap_m)
check("D2 对照: 合法非核心缺失(macro在场而UMCSENT缺席)→DEGRADED+采集遗漏点名"
      "(正常降级不因fail-closed误伤)",
      r['effective'] == 'DEGRADED' and r['noncore_missing'] == ['UMCSENT']
      and '采集遗漏' in r['noncore_missing_detail'].get('UMCSENT', ''),
      f"eff={r['effective']} miss={r['noncore_missing']}")

with tempfile.TemporaryDirectory() as tdc:
    fixt.write_collectors(tdc, DAY)
    os.remove(os.path.join(tdc, f'china_{DAY}.json'))   # china来源级缺失
    os.makedirs(os.path.join(tdc, 'out'), exist_ok=True)
    snap_c = sb.build_snapshot(target_ymd=DAY, data_dir=tdc, trusted_root=tdc,
                               out_dir=os.path.join(tdc, 'out'),
                               as_of=fixt.as_of_for(DAY))
r = rp.recompute_gate_a(snap_c)
cn_miss = [m for m in r['noncore_missing']
           if '来源文件缺失(china' in r['noncore_missing_detail'].get(m, '')]
check("D3 对照: 单通道MISSING(真实构建)→结构合法无illegal,非核心按来源缺失"
      "披露;该通道含核心指标→核心缺失按既有语义Gate A=FAIL(非fail-closed误伤)",
      snap_c['sources_status']['china']['status'] == 'MISSING'
      and r['effective'] == 'FAIL' and len(cn_miss) >= 3
      and not r['illegal_quality'] and not r.get('sources_problems'),
      f"eff={r['effective']} cn={cn_miss[:3]}")

with tempfile.TemporaryDirectory() as tdr:
    fixt.write_collectors(tdr, DAY)
    with open(os.path.join(tdr, f'china_{DAY}.json'), 'w', encoding='utf-8') as f:
        f.write('{broken json')      # 解析失败→READ_FAIL
    os.makedirs(os.path.join(tdr, 'out'), exist_ok=True)
    snap_rf = sb.build_snapshot(target_ymd=DAY, data_dir=tdr, trusted_root=tdr,
                                out_dir=os.path.join(tdr, 'out'),
                                as_of=fixt.as_of_for(DAY))
r = rp.recompute_gate_a(snap_rf)
check("D4 对照: 合法READ_FAIL(error留痕)→结构合法无illegal,非核心按来源缺失"
      "披露;通道含核心指标→核心缺失Gate A=FAIL(既有语义,非fail-closed误伤)",
      snap_rf['sources_status']['china']['status'] == 'READ_FAIL'
      and snap_rf['sources_status']['china'].get('error')
      and r['effective'] == 'FAIL' and not r['illegal_quality']
      and not r.get('sources_problems'),
      f"eff={r['effective']} ss={snap_rf['sources_status']['china']}")

_D_BAD = [
    ('D5 sources_status整体缺失', lambda d: d.pop('sources_status', None), 'sources_status缺失/非对象'),
    ('D6 sources_status=None', lambda d: d.update(sources_status=None), 'sources_status缺失/非对象'),
    ('D7 sources_status=[]', lambda d: d.update(sources_status=[]), 'sources_status缺失/非对象'),
    ('D8 sources_status="unknown"', lambda d: d.update(sources_status='unknown'), 'sources_status缺失/非对象'),
    ('D9 必需通道缺失(pop china)', lambda d: d['sources_status'].pop('china'), '缺必需来源通道:china'),
    ('D10 通道状态为字符串', lambda d: d['sources_status'].update(china='broken'), "['china']非对象"),
    ('D11 状态值非法(OK)', lambda d: d['sources_status']['china'].update(status='OK'), 'status非法'),
    ('D12 EXACT缺file', lambda d: d['sources_status']['global'].pop('file'), '缺file'),
    ('D13 FALLBACK缺file_date', lambda d: (
        d['sources_status']['global'].update(
            {'status': 'FALLBACK', 'file': 'global_20261023.json', 'lag_days': 1}),
        d['sources_status']['global'].pop('file_date', None)), '缺/非法file_date'),
]
for tag, mut, kw in _D_BAD:
    s = copy.deepcopy(SNAP)
    mut(s)
    r, ok = no_exception(rp.recompute_gate_a, s)
    check(f"{tag}→fail-closed不可证明,无未受控异常",
          ok and r['effective'] is None
          and r.get('sources_problems')
          and any(kw in p for p in r['sources_problems']),
          f"exc={not ok} eff={r and r['effective']} probs={r and r.get('sources_problems')[:1]}")

s = copy.deepcopy(SNAP)
s['sources_status']['global']['status'] = 'FALLBACK'   # EXACT改口FALLBACK但file_date=当日
r, ok = no_exception(rp.recompute_gate_a, s)
check("D14 FALLBACK但不早于当日(file_date=当日)→回退身份矛盾拒",
      ok and r['effective'] is None
      and any('不早于当日' in p for p in r.get('sources_problems', [])),
      str(r.get('sources_problems', [])[:1]))

s = copy.deepcopy(SNAP)
s['sources_status']['global']['lag_days'] = 9          # 与日期差不自洽
s['sources_status']['global']['status'] = 'FALLBACK'
s['sources_status']['global']['file'] = 'global_20261023.json'
s['sources_status']['global']['file_date'] = '20261023'
r, ok = no_exception(rp.recompute_gate_a, s)
check("D15 FALLBACK lag_days与日期差不自洽→真实回退窗口不可证明拒",
      ok and r['effective'] is None
      and any('不自洽lag_days' in p for p in r.get('sources_problems', [])),
      str(r.get('sources_problems', [])[:1]))

s = copy.deepcopy(SNAP)
# 批次改名(规范名FALLBACK自洽——FIX6后非规范名会先被来源身份层拒,
# 用规范名才能直达事实层失配路径),事实未跟
s['sources_status']['global'] = {'status': 'FALLBACK',
                                 'file': 'global_20261023.json',
                                 'file_date': '20261023', 'lag_days': 1}
r = rp.recompute_gate_a(s)
check("D16 sources_status与事实source.file不一致→事实批次不一致拒",
      illegal_has(r, 'source.file与当次采集批次不一致'),
      str([x for x in r['illegal_quality'] if '批次不一致' in x][:1]))

s = copy.deepcopy(SNAP)
s['sources_status']['china'].update(status='MISSING', file='china_20261024.json')
r = rp.recompute_gate_a(s)
check("D17 声明MISSING却携带file(伪装在场)→拒",
      r['effective'] is None
      and any('MISSING但携带file' in p for p in r.get('sources_problems', [])),
      str(r.get('sources_problems', [])[:1]))

# ════════════════════════════════════════════════════════════════════
print("\n── E. 端到端(真实装配器/周报预检/发布/观察器)")

check("E1 正常有效快照可以构建(Gate A=PASS)",
      SNAP['gate_a']['status'] == 'PASS'
      and os.path.exists(SNAP_PATH))

code = _run_da_main(BASE)
pack = os.path.join(BASE, 'data', 'weekly', f'data_pack_{DAY}.md')
pm = rp.load_meta(pack)
check("E2 Gate A PASS正常进入数据包(exit0+包在场+meta.gate_a=PASS)",
      code == 0 and os.path.exists(pack) and pm.get('gate_a') == 'PASS',
      f"code={code} meta_gate={pm and pm.get('gate_a')}")

with tempfile.TemporaryDirectory() as td3:
    snap3, sp3, p3 = fixt.build_full_day(td3, DAY, gate='DEGRADED')
    code3 = _run_da_main(td3)
    body = open(os.path.join(td3, 'data', 'weekly', f'data_pack_{DAY}.md'),
                encoding='utf-8').read()
    check("E3 合法DEGRADED继续研究并披露(exit0+包内降级披露在场)",
          code3 == 0 and '数据质量降级披露' in body and 'UMCSENT' in body,
          f"code={code3}")

_E_TAMPER = [
    ('E4 非法事实来源', lambda d: [f['source'].update(collector='fictitious_collector')
                                 for f in d['facts'] if f['metric_id'] == 'SPX'],
     ['collector与指标权威来源不符', 'collector']),
    ('E5 来源状态不完整', lambda d: d.update(sources_status=['bogus']),
     ['sources_status', 'Gate A']),
    ('E6 非法quality/issues', lambda d: [
        f.update(quality_status='PASS',
                 issues=[{'category': 'x', 'severity': 'FAIL', 'message': 'm'}])
        for f in d['facts'] if f['metric_id'] == 'SPX'],
     ['不一致', 'Gate A']),
    ('E7 非法日期', lambda d: [f.update(observation_date='2026-10-23INVALID')
                             for f in d['facts'] if f['metric_id'] == 'SPX'],
     ['observation_date', 'Gate A']),
]
for tag, mut, kws in _E_TAMPER:
    with tempfile.TemporaryDirectory() as tde:
        fixt.build_full_day(tde, DAY)
        sp = os.path.join(tde, 'data', 'daily', f'research_snapshot_{DAY}.json')
        pk = os.path.join(tde, 'data', 'weekly', f'data_pack_{DAY}.md')
        before = open(pk, 'rb').read()
        _disk_tamper(sp, mut)
        code = _run_da_main(tde)
        pre_ok, problems = _preflight(tde)
        after = open(pk, 'rb').read() if os.path.exists(pk) else None
        check(f"{tag}→装配器exit2+预检拒+不合格正式包不产出/旧包不被改写",
              code == 2 and pre_ok is False
              and any(all(k in ' '.join(map(str, problems)) for k in kws[:1])
                      or any(k in str(p) for p in problems) for k in kws)
              and after == before,
              f"code={code} pre={pre_ok} problems={str(problems)[:120]}")


def publish(td, ymd, gate='PASS', dt=DT_DAY):
    """真实发布事务(仅mock付费GLM与Gate B裁决;其余全真实)。"""
    fixt.build_full_day(td, ymd, gate=gate)
    out_dir = os.path.join(td, 'output', 'weekly')
    cfg = os.path.join(td, 'config')
    os.makedirs(cfg, exist_ok=True)
    for name, obj in (('thesis.json', {'theses': []}),
                      ('views.json', {'views': [], 'predictions': []})):
        p = os.path.join(cfg, name)
        if not os.path.exists(p):
            with open(p, 'w', encoding='utf-8') as f:
                json.dump(obj, f, ensure_ascii=False)
    glm = _GLM()

    def _validate(md_path, anchors=None, anchors_file=None):
        return ('PASS', ['SYNTHETIC FIX5警告'])
    patches = [
        mock.patch.object(rg, 'DATA_DIR', os.path.join(td, 'data')),
        mock.patch.object(rg, 'OUTPUT_DIR', out_dir),
        mock.patch.object(rg, 'CONFIG_DIR', cfg),
        mock.patch.object(rg, 'datetime', dt),
        mock.patch.object(rg, '_call_glm', glm),
        mock.patch.object(rg, 'validate_generated_report', _validate),
        mock.patch.object(rg.allocation_engine, 'DEFAULT_VIEWS_PATH',
                          os.path.join(cfg, 'views.json'))]
    with contextlib.ExitStack() as stack:
        for p in patches:
            stack.enter_context(p)
        try:
            quiet(rg.generate_weekly_report)
            code = 0
        except SystemExit as e:
            code = e.code
    return code, out_dir, glm, os.path.join(cfg, 'views.json')


with tempfile.TemporaryDirectory() as td9:
    code9, out_dir, glm9, _vp = publish(td9, DAY)
    md = os.path.join(out_dir, f'weekly_report_{DAY}.md')
    good_bytes = open(md, 'rb').read()
    view_ok, _ = rp.formal_report_view(md)
    # 当日快照被破坏后再跑发布→exit2且合格报告字节不变、正式身份仍有效
    sp9 = os.path.join(td9, 'data', 'daily', f'research_snapshot_{DAY}.json')
    _disk_tamper(sp9, lambda d: d['sources_status'].update(china='broken'))
    patches = [
        mock.patch.object(rg, 'DATA_DIR', os.path.join(td9, 'data')),
        mock.patch.object(rg, 'OUTPUT_DIR', out_dir),
        mock.patch.object(rg, 'CONFIG_DIR', os.path.join(td9, 'config')),
        mock.patch.object(rg, 'datetime', DT_DAY),
        mock.patch.object(rg, '_call_glm', _GLM()),
    ]
    with contextlib.ExitStack() as stack:
        for p in patches:
            stack.enter_context(p)
        try:
            quiet(rg.generate_weekly_report)
            code9b = 0
        except SystemExit as e:
            code9b = e.code
    view_ok2, _r2 = rp.formal_report_view(md)
    check("E9 已有合格报告保护: 破坏输入后重跑→exit2+GLM前拒+报告字节不变"
          "+正式身份仍有效",
          code9 == 0 and code9b == 2 and open(md, 'rb').read() == good_bytes
          and view_ok and view_ok2,
          f"pub={code9} retry={code9b} view={bool(view_ok)}/{bool(view_ok2)}")

with tempfile.TemporaryDirectory() as td10:
    fixt.build_full_day(td10, DAY)
    cfgv = os.path.join(td10, 'config')
    os.makedirs(cfgv, exist_ok=True)
    views_path = os.path.join(cfgv, 'views.json')
    with open(views_path, 'w', encoding='utf-8') as f:
        json.dump({'views': [], 'predictions': [{
            'pred_id': 'P1', 'status': 'observing',
            'metric': 'SPX', 'op': '>=', 'target': 7000,
            'created': '2026-10-17'}]}, f, ensure_ascii=False)
    apath = os.path.join(td10, 'data', 'daily', f'anchors_{DAY}.json')
    vbytes = open(views_path, 'rb').read()
    anchors = json.load(open(apath, encoding='utf-8'))
    ok_batch, _ = rp.verify_anchor_batch(apath, anchors_date=DAY, trusted_root=td10)
    _disk_tamper(os.path.join(td10, 'data', 'daily', f'research_snapshot_{DAY}.json'),
                 lambda d: d.update(sources_status='unknown'))
    ok_batch2, why2 = rp.verify_anchor_batch(apath, anchors_date=DAY, trusted_root=td10)
    ch, n, st = dpo.observe(views_path=views_path, anchors=anchors,
                            today_str='2026-10-24', anchors_date=DAY,
                            anchors_path=apath, trusted_root=td10)
    check("E10 长期状态防御: 破坏前批次核验过;破坏后批次核验拒+观察器关键FAIL"
          "+views字节不变(未验证数据不进长期观察)",
          ok_batch and ok_batch2 is False and ch == [] and st == 'FAIL'
          and open(views_path, 'rb').read() == vbytes,
          f"b1={ok_batch} b2={ok_batch2} ch={ch} st={st}")

# ═══ 汇总 ═══════════════════════════════════════════════════════════
shutil.rmtree(BASE, ignore_errors=True)
print("\n" + "=" * 64)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 64)
sys.exit(1 if FAIL else 0)
