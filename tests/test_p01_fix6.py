#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P0-1-FIX6 对抗测试(IA-F5-DEF-001/002/003闭环验收)

覆盖(指令§10矩阵,全部真实模块+临时目录;Mock仅付费GLM网络侧,**不Mock本轮
要验证的来源校验与门禁函数**;金融数据为fixt合成采集产物):
A. 采集文件身份: 四通道规范文件名{prefix}YYYYMMDD.json(真实日历日期/无路径
   成分/纯JSON)——跨通道文件·伪装前后缀·非JSON扩展名·绝对路径·../·子目录·
   目录冒充·符号链接逃逸·文件名日期≠file_date·不存在文件全拒;规范文件+
   状态+事实三者匹配对照过;构建端resolve_inputs同一规范(不选目录/伪装/链接);
B. EXACT/FALLBACK时间一致性: EXACT须文件名日期==file_date==当日;FALLBACK
   须真实早于当日+lag_days==真实差+**不超通道既有窗口**(global/china=5,
   macro/rate_economy=7)——超窗1天/115天自报自洽不豁免;四通道真实构建
   窗口内/边界过,篡改超窗拒;观测日与批次日合法不同不机械强制相等;
C. collector类型安全: None/空串/列表/字典/数字/布尔→可诊断拒绝,**无未受控
   TypeError**(旧代码col not in frozenset对unhashable直接崩);原始/派生两
   分支;source非对象/file非字符串同类假设排查;端到端装配器拒绝;
D. MISSING/READ_FAIL字段互斥: MISSING仅{'status'}(字段缺失与None等价),
   携带file(字符串/列表/字典)/file_date/lag_days全拒;READ_FAIL必须error且
   不得携带file/file_date/lag_days;EXACT携带lag_days/error·FALLBACK携带
   error互斥拒;合法失败状态正常披露(非核心DEGRADED/核心阻断不受误伤);
E. 真实门禁链路: 正常PASS进研究/合法DEGRADED可用/错误通道同步篡改不放行/
   目录冒充不放行/超窗FALLBACK不放行/非法collector不崩/矛盾状态拒/周报
   GLM=0/已合格报告与长期状态保护——拒绝传播至装配exit2+预检拒,非仅低层。
"""
import os
import sys
import io
import json
import copy
import shutil
import tempfile
import datetime as _dt
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
TGT = _dt.date(2026, 10, 24)


def _fd(lag):
    return (TGT - _dt.timedelta(days=lag)).strftime('%Y%m%d')


def _DT(*args):
    class _C:
        @staticmethod
        def now():
            return _dt.datetime(*args)

        @staticmethod
        def strptime(s, f):
            return _dt.datetime.strptime(s, f)
    return _C


DT_DAY = _DT(2026, 10, 24, 8, 0, 0)


class _GLM:
    """付费GLM调用mock(仅网络侧;预检/发布事务/读取器全真实)。"""

    def __init__(self):
        self.text = ('# 投资周报(SYNTHETIC FIX6矩阵)\n\n' + '本周市场综述与分资产回顾。' * 80)
        self.calls = 0

    def __call__(self, system_prompt, user_prompt, max_tokens=32000, timeout=900):
        self.calls += 1
        return self.text


def mutated(base, mid, **fields):
    snap = copy.deepcopy(base)
    for f in snap['facts']:
        if f.get('metric_id') == mid:
            for k, v in fields.items():
                f[k] = v
            return snap
    raise AssertionError(f'fixture无指标{mid}')


def mut_col(base, mid, col):
    """只改collector,保留source其余字段。"""
    snap = copy.deepcopy(base)
    for f in snap['facts']:
        if f.get('metric_id') == mid:
            src = copy.deepcopy(f.get('source') or {})
            src['collector'] = col
            f['source'] = src
            return snap
    raise AssertionError(mid)


def no_exception(fn, *a, **kw):
    try:
        return fn(*a, **kw), True
    except Exception:   # noqa: BLE001
        import traceback
        return traceback.format_exc(limit=2), False


# ══ 共享真实基线 ══
BASE = tempfile.mkdtemp(prefix='fix6-base-')
SNAP, SNAP_PATH, PATHS = fixt.build_full_day(BASE, DAY)
BASE_DAILY = PATHS['daily']

_OK_SS = {ch: {'status': 'EXACT', 'file': f'{ch}_{DAY}.json', 'file_date': DAY}
          for ch in rp.SOURCE_CHANNELS}


def ssp(status_dict, data_dir=None, target=DAY):
    return rp.sources_status_problems(status_dict, target, data_dir)


def _snap_with_ss(ss):
    s = copy.deepcopy(SNAP)
    s['sources_status'] = copy.deepcopy(ss)
    return s


def _run_da_main(root):
    with mock.patch.object(da, 'DATA_DIR', os.path.join(root, 'data')), \
         mock.patch.object(da, 'datetime', DT_DAY):
        try:
            quiet(da.main)
            return 0
        except SystemExit as e:
            return e.code


def _preflight(root):
    with mock.patch.object(rg, 'DATA_DIR', os.path.join(root, 'data')), \
         mock.patch.object(rg, 'datetime', DT_DAY):
        r = quiet(rg.verify_research_inputs)
        return r[0], r[1]


def _disk_tamper(snap_path, fn):
    disk = json.load(open(snap_path, encoding='utf-8'))
    fn(disk)
    with open(snap_path, 'w', encoding='utf-8') as f:
        json.dump(disk, f, ensure_ascii=False)


def _run_report(td, out_dir, glm):
    """真实周报入口(预检先行;仅mock付费GLM网络侧)。"""
    patches = [
        mock.patch.object(rg, 'DATA_DIR', os.path.join(td, 'data')),
        mock.patch.object(rg, 'OUTPUT_DIR', out_dir),
        mock.patch.object(rg, 'CONFIG_DIR', os.path.join(td, 'config')),
        mock.patch.object(rg, 'datetime', DT_DAY),
        mock.patch.object(rg, '_call_glm', glm)]
    with contextlib.ExitStack() as stack:
        for p in patches:
            stack.enter_context(p)
        try:
            quiet(rg.generate_weekly_report)
            return 0
        except SystemExit as e:
            return e.code


def publish(td, ymd, dt=DT_DAY):
    """真实发布事务(仅mock付费GLM与GateB裁决;预检/事务/读取器全真实)。"""
    fixt.build_full_day(td, ymd)
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
        return ('PASS', ['SYNTHETIC FIX6警告'])
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
    return code, out_dir, glm


print("=" * 64)
print("IA-P0-1-FIX6: 规范文件身份/EXACT·FALLBACK窗口/collector类型安全/状态互斥")
print("=" * 64)

# ════════════════════════════════════════════════════════════════════
print("\n── A. 采集文件身份(FIX6-01)")

check("A1-A4 四通道规范文件名+实体在场(直调/纯/正式三口径全过)",
      all(rp.canonical_source_file(ch, f'{ch}_{DAY}.json') == DAY
          for ch in rp.SOURCE_CHANNELS)
      and ssp(_OK_SS) == []
      and ssp(_OK_SS, data_dir=BASE_DAILY) == []
      and rp.recompute_gate_a(SNAP, data_dir=BASE_DAILY)['effective'] == 'PASS',
      str(ssp(_OK_SS, data_dir=BASE_DAILY)[:1]))

_A_BAD = [
    ('A5 global声明macro文件', {'file': f'macro_{DAY}.json', 'file_date': DAY},
     '不符通道规范文件名'),
    ('A6 伪装前缀other_global', {'file': f'other_global_{DAY}.json', 'file_date': DAY},
     '不符通道规范文件名'),
    ('A7 文件名日期≠file_date', {'file': 'global_20261023.json', 'file_date': DAY},
     '文件名日期20261023≠file_date20261024'),
    ('A13a 非JSON扩展名(.txt)', {'file': 'global_20261024.txt', 'file_date': DAY},
     '不符通道规范文件名'),
    ('A13b 非JSON扩展名(.json.bak)', {'file': f'global_{DAY}.json.bak', 'file_date': DAY},
     '不符通道规范文件名'),
    ('A11 绝对路径', {'file': f'/tmp/global_{DAY}.json', 'file_date': DAY},
     '含路径成分'),
    ('A12 ../穿越', {'file': f'../global_{DAY}.json', 'file_date': DAY},
     '含路径成分'),
    ('A12b 子目录路径', {'file': f'sub/global_{DAY}.json', 'file_date': DAY},
     '含路径成分'),
    ('A14a 文件名日期非法(13月)', {'file': 'global_20261399.json', 'file_date': '20261399'},
     '不符通道规范文件名'),
    ('A14b 文件名日期非法(02-30)', {'file': 'global_20260230.json', 'file_date': '20260230'},
     '不符通道规范文件名'),
]
for tag, over, kw in _A_BAD:
    ss = copy.deepcopy(_OK_SS)
    ss['global'].update(over)
    probs_pure, ok1 = no_exception(ssp, ss)
    probs_dir, ok2 = no_exception(ssp, ss, BASE_DAILY)
    g, ok3 = no_exception(rp.gate_status, _snap_with_ss(ss))
    check(f"{tag}→纯+正式+gate_status三口径拒,无未受控异常",
          ok1 and ok2 and ok3 and probs_pure and any(kw in p for p in probs_pure)
          and probs_dir and any(kw in p for p in probs_dir)
          and g[0] is None,
          f"pure={str(probs_pure)[:90]} g={g[0] if ok3 else g}")

# A8 不存在文件(规范名): 纯口径结构过(不虚报实体),正式口径拒
ss = copy.deepcopy(_OK_SS)
ss['global'] = {'status': 'FALLBACK', 'file': 'global_20261020.json',
                'file_date': '20261020', 'lag_days': 4}
check("A8 规范名但文件不存在: 纯重验结构过(证据范围显式);正式口径核出不存在拒",
      ssp(ss) == [] and any('在采集目录不存在' in p for p in ssp(ss, BASE_DAILY)),
      str(ssp(ss, BASE_DAILY)[:1]))

# A9/A10 目录冒充/符号链接逃逸(真实文件系统实体篡改)
with tempfile.TemporaryDirectory() as tdd:
    for ch in rp.SOURCE_CHANNELS:
        shutil.copy(os.path.join(BASE_DAILY, f'{ch}_{DAY}.json'), tdd)
    os.remove(os.path.join(tdd, f'global_{DAY}.json'))
    os.mkdir(os.path.join(tdd, f'global_{DAY}.json'))          # 目录冒充
    probs, ok = no_exception(ssp, _OK_SS, tdd)
    check("A9 文件名正确但实际是目录→拒(非普通文件)",
          ok and any('目录' in p for p in probs),
          str(probs[:1]))
with tempfile.TemporaryDirectory() as tds:
    for ch in rp.SOURCE_CHANNELS:
        if ch != 'global':
            shutil.copy(os.path.join(BASE_DAILY, f'{ch}_{DAY}.json'), tds)
    outside = os.path.join(tds, 'outside.json')
    shutil.copy(os.path.join(BASE_DAILY, f'global_{DAY}.json'), outside)
    os.symlink(outside, os.path.join(tds, f'global_{DAY}.json'))   # 链接逃逸
    probs, ok = no_exception(ssp, _OK_SS, tds)
    check("A10 符号链接指向采集目录外→拒(不得经链接逃逸)",
          ok and any('符号链接' in p for p in probs),
          str(probs[:1]))

check("A15 对照: 规范文件+sources_status+fact.source三者匹配→全链PASS"
      "(不能只比字符串相等——身份层先行)",
      rp.recompute_gate_a(SNAP)['effective'] == 'PASS'
      and rp.recompute_gate_a(SNAP, data_dir=BASE_DAILY)['effective'] == 'PASS'
      and next(f for f in SNAP['facts'] if f['metric_id'] == 'SPX')['source']['file']
      == SNAP['sources_status']['global']['file'])

# 构建端同一规范: resolve_inputs不选目录/非规范名/链接,真实规范回退文件照选
with tempfile.TemporaryDirectory() as tdr:
    fixt.write_collectors(tdr, DAY)
    fixt.write_collectors(tdr, _fd(1))
    os.remove(os.path.join(tdr, f'global_{DAY}.json'))
    os.mkdir(os.path.join(tdr, f'global_{DAY}.json'))                  # 目录
    open(os.path.join(tdr, f'other_global_{_fd(1)}.json'), 'w').write('{}')  # 伪装前缀
    open(os.path.join(tdr, f'global_{_fd(1)}.txt'), 'w').write('{}')   # 非JSON
    os.symlink(os.path.join(tdr, f'macro_{_fd(1)}.json'),
               os.path.join(tdr, f'global_{_fd(2)}.json'))             # 链接
    ri, ok = no_exception(sb.resolve_inputs, DAY, tdr)
    check("A16 构建端同规: 目录/伪装前缀/非JSON/链接全不选,真实规范回退文件照选"
          "(global回退到真实global_20261023.json,FALLBACK lag=1)",
          ok and isinstance(ri, dict) and ri['global'] is not None
          and ri['global']['exact'] is False
          and ri['global']['file_date'] == _fd(1) and ri['global']['lag_days'] == 1
          and ri['macro']['exact'] is True and ri['china']['exact'] is True,
          f"global={ri.get('global') if isinstance(ri, dict) else ri}")

# ════════════════════════════════════════════════════════════════════
print("\n── B. EXACT/FALLBACK时间一致性(FIX6-02)")

# 四通道真实构建: 窗口内lag=1与正好边界lag=窗口——来源层接受(无窗口问题,
# 结构可证明);边界时数据陈旧度按既有质量规则另行披露(合法语义,非来源拒)
for ch, rule in rp.SOURCE_FILE_RULES.items():
    w = rule['max_fallback_days']
    for lag, tag, want_pass in ((1, '窗口内lag=1', True),
                                (w, f'正好边界lag={w}', False)):
        with tempfile.TemporaryDirectory() as tdb:
            fixt.write_collectors(tdb, _fd(lag))
            os.makedirs(os.path.join(tdb, 'out'), exist_ok=True)
            snap_b = sb.build_snapshot(target_ymd=DAY, data_dir=tdb,
                                       out_dir=os.path.join(tdb, 'out'),
                                       as_of=fixt.as_of_for(DAY))
            r_pure = rp.recompute_gate_a(snap_b)
            r_form = rp.recompute_gate_a(snap_b, data_dir=tdb)
            st_ok = (snap_b['sources_status'][ch]['status'] == 'FALLBACK'
                     and snap_b['sources_status'][ch]['lag_days'] == lag)
            no_window = (not r_pure.get('sources_problems')
                         and not any('回退窗口' in x or '不符通道规范' in x
                                     for x in r_pure['illegal_quality']))
        if want_pass:
            check(f"B[{ch}] 真实构建{tag}→PASS(纯+正式,回退身份真实)",
                  st_ok and no_window and r_pure['effective'] == 'PASS'
                  and r_form['effective'] == 'PASS',
                  f"ss={snap_b['sources_status'].get(ch)} eff="
                  f"{r_pure['effective']}/{r_form['effective']}")
        else:
            check(f"B[{ch}] 真实构建{tag}→来源层接受(无窗口拒绝,结构可证明;"
                  "数据陈旧度按既有质量语义另行裁决,不冒充来源非法)",
                  st_ok and no_window
                  and r_pure['effective'] in ('PASS', 'DEGRADED', 'FAIL')
                  and r_form['effective'] == r_pure['effective'],
                  f"ss={snap_b['sources_status'].get(ch)} eff="
                  f"{r_pure['effective']}/{r_form['effective']} "
                  f"src={r_pure.get('sources_problems')}")

# 篡改: 超窗1天/115天(自报lag自洽)→拒
for ch, rule in rp.SOURCE_FILE_RULES.items():
    w = rule['max_fallback_days']
    for lag, tag in ((w + 1, f'超窗1天lag={w+1}'), (115, '115天旧文件')):
        ss = copy.deepcopy(_OK_SS)
        ss[ch] = {'status': 'FALLBACK', 'file': f'{ch}_{_fd(lag)}.json',
                  'file_date': _fd(lag), 'lag_days': lag}
        probs, ok = no_exception(ssp, ss)
        g, okg = no_exception(rp.gate_status, _snap_with_ss(ss))
        check(f"B[{ch}] {tag}→拒(自报lag一致不豁免既有窗口)",
              ok and okg and any(f'超{ch}通道回退窗口{w}' in p for p in probs)
              and g[0] is None,
              f"probs={str(probs)[:90]}")

_B_EXACT = [
    ('EXACT前一日文件(fd≠当日)', 'global_20261023.json', '20261023',
     'EXACT但file_date=20261023≠当日'),
    ('EXACT文件名日期与file_date冲突', 'global_20261023.json', DAY,
     '文件名日期20261023≠file_date'),
]
for tag, fil, fd, kw in _B_EXACT:
    ss = copy.deepcopy(_OK_SS)
    ss['global'] = {'status': 'EXACT', 'file': fil, 'file_date': fd}
    probs, ok = no_exception(ssp, ss)
    check(f"B {tag}→拒", ok and any(kw in p for p in probs), str(probs[:1]))

ss = copy.deepcopy(_OK_SS)
ss['global'] = {'status': 'FALLBACK', 'file': f'global_{_fd(1)}.json',
                'file_date': _fd(1)}          # 缺lag_days
probs, ok = no_exception(ssp, ss)
check("B FALLBACK缺lag_days→拒", ok and any('缺/不自洽lag_days' in p for p in probs),
      str(probs[:1]))

ss = copy.deepcopy(_OK_SS)
ss['global'] = {'status': 'FALLBACK', 'file': f'global_{_fd(3)}.json',
                'file_date': _fd(3), 'lag_days': 1}   # 自报≠真实差
probs, ok = no_exception(ssp, ss)
check("B FALLBACK自报lag与真实差不一致→拒",
      ok and any('缺/不自洽lag_days' in p for p in probs), str(probs[:1]))

ss = copy.deepcopy(_OK_SS)
ss['global'] = {'status': 'FALLBACK', 'file': 'global_20261026.json',
                'file_date': '20261026', 'lag_days': 2}   # 未来日期
probs, ok = no_exception(ssp, ss)
check("B FALLBACK未来日期→拒(不早于当日)",
      ok and any('不早于当日' in p for p in probs), str(probs[:1]))

ss = copy.deepcopy(_OK_SS)
ss['global'] = {'status': 'FALLBACK', 'file': 'global_20261399.json',
                'file_date': '20261399', 'lag_days': 9}   # 日期字段非法
probs, ok = no_exception(ssp, ss)
check("B FALLBACK日期字段非法→拒(任一身份层)",
      ok and probs != [], str(probs[:1]))

spx = next(f for f in SNAP['facts'] if f['metric_id'] == 'SPX')
check("B对照: 观测日(周五收盘2026-10-23)与采集批次日(20261024)合法不同→PASS"
      "(周六研究用周五收盘,不机械强制相等)",
      spx['observation_date'] == '2026-10-23'
      and SNAP['sources_status']['global']['file_date'] == DAY
      and rp.recompute_gate_a(SNAP, data_dir=BASE_DAILY)['effective'] == 'PASS')

# ════════════════════════════════════════════════════════════════════
print("\n── C. collector类型安全(FIX6-03)")

_C_RAW = [('合法字符串', 'global_market_collector', True),
          ('空字符串', '', False), ('None', None, False),
          ('列表', ['global_market_collector'], False),
          ('字典', {'collector': 'global_market_collector'}, False),
          ('数字', 123, False), ('布尔', True, False)]
for tag, col, legal in _C_RAW:
    s = mut_col(SNAP, 'SPX', col)
    r, ok = no_exception(rp.recompute_gate_a, s)
    bad = [x for x in (r['illegal_quality'] if ok else []) if 'collector' in x]
    if legal:
        check(f"C[原始SPX] {tag}→无collector问题,无TypeError",
              ok and r['effective'] == 'PASS' and not bad,
              f"eff={r.get('effective') if ok else r} bad={bad[:1]}")
    else:
        check(f"C[原始SPX] {tag}→可诊断拒(collector非法类型/空),无TypeError",
              ok and r['effective'] is None
              and any('collector非法类型/空' in x for x in bad),
              f"eff={r.get('effective') if ok else r} bad={bad[:1]}")

_C_DERIVED = [('合法fact_engine', 'fact_engine', True),
              ('空字符串', '', False), ('None', None, False),
              ('列表', ['fact_engine'], False), ('字典', {'a': 1}, False),
              ('数字', 3.14, False), ('布尔', False, False)]
for tag, col, legal in _C_DERIVED:
    s = mut_col(SNAP, 'REAL_10Y', col)
    r, ok = no_exception(rp.recompute_gate_a, s)
    bad = [x for x in (r['illegal_quality'] if ok else []) if 'collector' in x]
    if legal:
        check(f"C[派生REAL_10Y] {tag}→无collector问题,无TypeError",
              ok and r['effective'] == 'PASS' and not bad,
              f"eff={r.get('effective') if ok else r} bad={bad[:1]}")
    else:
        check(f"C[派生REAL_10Y] {tag}→可诊断拒,无TypeError",
              ok and r['effective'] is None
              and any('collector非法类型/空' in x for x in bad),
              f"eff={r.get('effective') if ok else r} bad={bad[:1]}")

s = mutated(SNAP, 'SPX', source=None)
r, ok = no_exception(rp.recompute_gate_a, s)
check("C source非对象(None)→可诊断拒,无AttributeError",
      ok and r['effective'] is None
      and any('collector' in x or 'source' in x for x in r['illegal_quality']),
      str([x for x in r['illegal_quality']
           if 'collector' in x or 'source' in x][:1]))

s = mutated(SNAP, 'SPX', source={'collector': 'global_market_collector',
                                 'file': ['global_20261024.json']})
r, ok = no_exception(rp.recompute_gate_a, s)
check("C source.file非字符串(列表)→可诊断拒,无未受控异常",
      ok and r['effective'] is None
      and any('source.file非字符串' in x for x in r['illegal_quality']),
      str([x for x in r['illegal_quality'] if 'file' in x][:1]))

with tempfile.TemporaryDirectory() as tdc:
    fixt.build_full_day(tdc, DAY)
    _disk_tamper(os.path.join(tdc, 'data', 'daily', f'research_snapshot_{DAY}.json'),
                 lambda d: [f['source'].update(collector=['global_market_collector'])
                            for f in d['facts'] if f['metric_id'] == 'SPX'])
    code = _run_da_main(tdc)
    pre_ok, problems = _preflight(tdc)
    check("C 端到端: 磁盘注入列表collector→装配器exit2+预检拒(不崩,不放行)",
          code == 2 and pre_ok is False,
          f"code={code} pre={pre_ok} {str(problems)[:80]}")

# ════════════════════════════════════════════════════════════════════
print("\n── D. MISSING/READ_FAIL字段互斥(FIX6-04)")

_D_CASES = [
    ('D1 正常MISSING(仅status)', {'status': 'MISSING'}, True, None),
    ('D1b MISSING file=None(与缺失等价,构建器口径)', {'status': 'MISSING', 'file': None},
     True, None),
    ('D2 MISSING+file字符串', {'status': 'MISSING', 'file': f'global_{DAY}.json'},
     False, 'MISSING但携带file'),
    ('D3 MISSING+file列表', {'status': 'MISSING', 'file': [f'global_{DAY}.json']},
     False, 'MISSING但携带file'),
    ('D4 MISSING+file字典', {'status': 'MISSING', 'file': {'f': 1}},
     False, 'MISSING但携带file'),
    ('D5 MISSING+file_date', {'status': 'MISSING', 'file_date': DAY},
     False, 'MISSING但携带file_date'),
    ('D6 MISSING+lag_days', {'status': 'MISSING', 'lag_days': 1},
     False, 'MISSING但携带lag_days'),
    ('D7 正常READ_FAIL+error', {'status': 'READ_FAIL', 'error': 'Expecting value'},
     True, None),
    ('D8 READ_FAIL缺error', {'status': 'READ_FAIL'}, False, 'READ_FAIL缺error'),
    ('D8b READ_FAIL error非字符串', {'status': 'READ_FAIL', 'error': 42},
     False, 'READ_FAIL缺error'),
    ('D9 READ_FAIL+file', {'status': 'READ_FAIL', 'error': 'x',
                           'file': f'global_{DAY}.json'}, False, 'READ_FAIL携带file'),
    ('D10 READ_FAIL+file_date', {'status': 'READ_FAIL', 'error': 'x',
                                 'file_date': DAY}, False, 'READ_FAIL携带file_date'),
    ('D11 READ_FAIL+lag_days', {'status': 'READ_FAIL', 'error': 'x', 'lag_days': 1},
     False, 'READ_FAIL携带lag_days'),
    ('D12a EXACT正常', dict(_OK_SS['global']), True, None),
    ('D12b EXACT+lag_days(语义互斥)', {'status': 'EXACT', 'file': f'global_{DAY}.json',
                                       'file_date': DAY, 'lag_days': 0},
     False, 'EXACT携带回退字段lag_days'),
    ('D12c EXACT+error(语义互斥)', {'status': 'EXACT', 'file': f'global_{DAY}.json',
                                    'file_date': DAY, 'error': 'x'},
     False, '声明EXACT但携带error'),
    ('D12d FALLBACK正常(窗口内,含disclosure)',
     {'status': 'FALLBACK', 'file': f'global_{_fd(1)}.json',
      'file_date': _fd(1), 'lag_days': 1, 'disclosure': '回退披露'}, True, None),
    ('D12e FALLBACK+error(语义互斥)',
     {'status': 'FALLBACK', 'file': f'global_{_fd(1)}.json',
      'file_date': _fd(1), 'lag_days': 1, 'error': 'x'},
     False, '声明FALLBACK但携带error'),
]
def _snap_ss_nofacts(ss, ch='global'):
    """替换sources_status并移除该通道事实(通道缺席时状态合法性的完整快照口径)。"""
    s = _snap_with_ss(ss)
    pre = f'{ch}_'
    s['facts'] = [f for f in s['facts']
                  if not (isinstance(f.get('source'), dict)
                          and isinstance(f['source'].get('file'), str)
                          and f['source']['file'].startswith(pre))]
    return s


for tag, st, legal, kw in _D_CASES:
    ss = copy.deepcopy(_OK_SS)
    ss['global'] = copy.deepcopy(st)
    probs, ok = no_exception(ssp, ss)
    # 合法结构用"通道事实一并缺席"的完整快照验证(事实在场而声明缺失=另一层
    # 批次冲突语义,由A8/fix5覆盖);非法结构两种形态都必须None
    snap_full = _snap_ss_nofacts(ss) if legal else _snap_with_ss(ss)
    if legal:
        r, okg = no_exception(rp.recompute_gate_a, snap_full)
        check(f"{tag}→合法(直调零问题+完整快照复算结构可证明,无TypeError)",
              ok and okg and probs == []
              and r['effective'] in ('PASS', 'DEGRADED', 'FAIL'),
              f"probs={str(probs)[:80]} eff={r.get('effective') if okg else r}")
    else:
        g, okg = no_exception(rp.gate_status, snap_full)
        check(f"{tag}→拒(失败状态不得冒充成功来源)",
              ok and okg and any(kw in p for p in probs) and g[0] is None,
              f"probs={str(probs)[:90]}")

with tempfile.TemporaryDirectory() as tdm:
    fixt.write_collectors(tdm, DAY, missing=('UMCSENT',))
    os.makedirs(os.path.join(tdm, 'out'), exist_ok=True)
    sm = sb.build_snapshot(target_ymd=DAY, data_dir=tdm,
                           out_dir=os.path.join(tdm, 'out'), as_of=fixt.as_of_for(DAY))
r = rp.recompute_gate_a(sm)
check("D对照: 真实合法非核心缺失(UMCSENT)→DEGRADED披露(fail-closed不误伤)",
      r['effective'] == 'DEGRADED' and r['noncore_missing'] == ['UMCSENT']
      and not r['illegal_quality'],
      f"eff={r['effective']}")
with tempfile.TemporaryDirectory() as tdc2:
    fixt.write_collectors(tdc2, DAY)
    os.remove(os.path.join(tdc2, f'china_{DAY}.json'))
    os.makedirs(os.path.join(tdc2, 'out'), exist_ok=True)
    sc = sb.build_snapshot(target_ymd=DAY, data_dir=tdc2,
                           out_dir=os.path.join(tdc2, 'out'), as_of=fixt.as_of_for(DAY))
r = rp.recompute_gate_a(sc)
check("D对照: 核心通道真正缺失(china)→核心质量规则阻断(FAIL),状态仅{'status'}",
      sc['sources_status']['china'] == {'status': 'MISSING'}
      and r['effective'] == 'FAIL' and not r['illegal_quality'],
      f"eff={r['effective']}")

# ════════════════════════════════════════════════════════════════════
print("\n── E. 真实门禁链路(装配器/周报预检/发布/观察器)")

check("E1 正常PASS进入研究(快照+装配exit0+包meta.gate_a=PASS)",
      SNAP['gate_a']['status'] == 'PASS' and os.path.exists(SNAP_PATH)
      and _run_da_main(BASE) == 0
      and rp.load_meta(os.path.join(BASE, 'data', 'weekly',
                                    f'data_pack_{DAY}.md')).get('gate_a') == 'PASS')

with tempfile.TemporaryDirectory() as td2:
    fixt.build_full_day(td2, DAY, gate='DEGRADED')
    code = _run_da_main(td2)
    body = open(os.path.join(td2, 'data', 'weekly', f'data_pack_{DAY}.md'),
                encoding='utf-8').read()
    check("E2 合法DEGRADED保持可用(exit0+披露在场)",
          code == 0 and '数据质量降级披露' in body, f"code={code}")


def _cross_channel(d):
    """错误通道同步篡改: 状态与全部global事实同时改macro文件(字符串自报一致)。"""
    d['sources_status']['global']['file'] = f'macro_{DAY}.json'
    for f in d['facts']:
        if isinstance(f.get('source'), dict) \
                and f['source'].get('file') == f'global_{DAY}.json':
            f['source']['file'] = f'macro_{DAY}.json'


def _over_window(d):
    """超窗FALLBACK同步篡改: 115天前规范名文件,lag自报自洽。"""
    d['sources_status']['global'] = {'status': 'FALLBACK',
                                     'file': f'global_{_fd(115)}.json',
                                     'file_date': _fd(115), 'lag_days': 115}
    for f in d['facts']:
        if isinstance(f.get('source'), dict) \
                and f['source'].get('file') == f'global_{DAY}.json':
            f['source']['file'] = f'global_{_fd(115)}.json'


def _dir_masquerade(root):
    """采集目录内global文件替换为目录(快照本身不动)。"""
    p = os.path.join(root, 'data', 'daily', f'global_{DAY}.json')
    os.remove(p)
    os.mkdir(p)


_E_TAMPER = [
    ('E3 错误通道(声明与事实同步改)', _cross_channel, '不符通道规范文件名'),
    ('E4b 目录冒充采集文件', None, '目录'),          # 特殊: 目录替换,快照不动
    ('E5 超窗FALLBACK(115天,自报自洽)', _over_window, '超global通道回退窗口5'),
    ('E6 非法collector类型(列表,不崩)', lambda d: [
        f['source'].update(collector=['global_market_collector'])
        for f in d['facts'] if f['metric_id'] == 'SPX'], 'collector非法类型/空'),
    ('E7 MISSING携带file(矛盾)', lambda d: d['sources_status'].update(
        china={'status': 'MISSING', 'file': f'china_{DAY}.json'}),
     'MISSING但携带file'),
]
for tag, mut, kw in _E_TAMPER:
    with tempfile.TemporaryDirectory() as tde:
        fixt.build_full_day(tde, DAY)
        code0 = _run_da_main(tde)
        pk = os.path.join(tde, 'data', 'weekly', f'data_pack_{DAY}.md')
        before = open(pk, 'rb').read()
        sp = os.path.join(tde, 'data', 'daily', f'research_snapshot_{DAY}.json')
        if mut is None:
            _dir_masquerade(tde)
        else:
            _disk_tamper(sp, mut)
        code = _run_da_main(tde)
        pre_ok, problems = _preflight(tde)
        after = open(pk, 'rb').read() if os.path.exists(pk) else None
        allprobs = ' '.join(map(str, problems))
        check(f"{tag}→装配exit2+预检拒+旧包不动(拒绝传播到正式入口)",
              code0 == 0 and code == 2 and pre_ok is False and kw in allprobs
              and after == before,
              f"code={code} pre={pre_ok} {allprobs[:100]}")

with tempfile.TemporaryDirectory() as td8:
    fixt.build_full_day(td8, DAY)
    out8 = os.path.join(td8, 'output', 'weekly')
    _disk_tamper(os.path.join(td8, 'data', 'daily', f'research_snapshot_{DAY}.json'),
                 _cross_channel)
    glm8 = _GLM()
    code8 = _run_report(td8, out8, glm8)
    check("E8 非法来源下周报入口exit2+GLM恰0次(预检先行)",
          code8 == 2 and glm8.calls == 0, f"code={code8} glm={glm8.calls}")

with tempfile.TemporaryDirectory() as td9:
    code9, out9, _g = publish(td9, DAY)
    md = os.path.join(out9, f'weekly_report_{DAY}.md')
    good = open(md, 'rb').read()
    vp = os.path.join(td9, 'config', 'views.json')
    vbytes = open(vp, 'rb').read()
    vok1, _ = rp.formal_report_view(md)
    _disk_tamper(os.path.join(td9, 'data', 'daily', f'research_snapshot_{DAY}.json'),
                 _over_window)
    g2 = _GLM()
    code9b = _run_report(td9, out9, g2)
    vok2, _r2 = rp.formal_report_view(md)
    check("E9 已合格报告保护: 非法来源重跑→exit2+GLM=0+报告/长期状态字节不变"
          "+正式身份仍有效",
          code9 == 0 and code9b == 2 and g2.calls == 0
          and open(md, 'rb').read() == good
          and open(vp, 'rb').read() == vbytes and vok1 and vok2,
          f"pub={code9} retry={code9b} glm={g2.calls}")

with tempfile.TemporaryDirectory() as td10:
    fixt.build_full_day(td10, DAY)
    cfgv = os.path.join(td10, 'config')
    os.makedirs(cfgv, exist_ok=True)
    views_path = os.path.join(cfgv, 'views.json')
    with open(views_path, 'w', encoding='utf-8') as f:
        json.dump({'views': [], 'predictions': [{
            'pred_id': 'P1', 'status': 'observing', 'metric': 'SPX',
            'op': '>=', 'target': 7000, 'created': '2026-10-17'}]},
            f, ensure_ascii=False)
    apath = os.path.join(td10, 'data', 'daily', f'anchors_{DAY}.json')
    vbytes = open(views_path, 'rb').read()
    anchors = json.load(open(apath, encoding='utf-8'))
    ok1, _ = rp.verify_anchor_batch(apath, anchors_date=DAY)
    _disk_tamper(os.path.join(td10, 'data', 'daily',
                              f'research_snapshot_{DAY}.json'), _cross_channel)
    ok2, _w = rp.verify_anchor_batch(apath, anchors_date=DAY)
    ch, n, st = dpo.observe(views_path=views_path, anchors=anchors,
                            today_str='2026-10-24', anchors_date=DAY,
                            anchors_path=apath)
    check("E10 长期状态防御: 破坏前批次核验过;破坏后拒+观察器关键FAIL"
          "+views字节不变(未验证数据不进长期观察)",
          ok1 and ok2 is False and ch == [] and st == 'FAIL'
          and open(views_path, 'rb').read() == vbytes,
          f"b1={ok1} b2={ok2} ch={ch} st={st}")

# ══ 汇总 ═══════════════════════════════════════════════════════════
shutil.rmtree(BASE, ignore_errors=True)
print("\n" + "=" * 64)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 64)
sys.exit(1 if FAIL else 0)
