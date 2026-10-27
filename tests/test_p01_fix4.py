#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P0-1-FIX4 对抗测试(FIX4-01/02/03闭环验收;E2E-12重建在frozen14套件)

覆盖:
1. FIX4-01(FIX3-NEW-001) 金融事实必要字段与注册表身份校验——19例矩阵:
   真实全active fixture快照(80事实,Gate A=PASS)→按make_fact实际结构定点
   篡改单事实→真实recompute_gate_a+gate_status裁决(非法→effective=None),
   代表性案例进入真实下游研究入口(data_assembler拒绝/verify_meta_gate_a/
   周报预检verify_research_inputs);合法FAIL/DEGRADED不误伤;
2. FIX4-02(FIX3-NEW-002) 正式报告身份字段严格核验——16例矩阵: 真实发布
   事务产出的合格报告→定点篡改report_status身份字段→真实formal_report_view
   +真实消费者(rg.load_previous_report/data_validator入口/月度索引
   monthly_review.gather_month_context/正式扫描器)一致拒绝;正常PASS/DEGRADED
   不误伤(路径别名经realpath规范化后仍接受);
3. FIX4-03(FIX3-NEW-003) 非核心指标完全缺失的合理降级与披露——场景A(在场
   值坏)/场景B(完全缺席)不得互替;核心完全缺席→FAIL;月度"尚未发布"(在场
   旧期,新鲜度降级)≠"采集遗漏"(缺席进noncore_missing);来源文件级缺失
   另有归因;deprecated指标不追责;不补零不伪造;有效数据继续研究。

fixture: tests/fixt.py 真实注册表全active(32 core+47 important+1 context)
SYNTHETIC采集→真实snapshot_builder/装配/锚点;GLM全程mock(零付费零网络);
临时目录隔离,不触生产数据;断言全部针对真实函数返回值/磁盘字节/退出码,
无源码字符串扫描。
"""
import os
import sys
import io
import json
import copy
import math
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
import snapshot_builder as sb              # noqa: E402
import data_assembler as da                # noqa: E402
import data_validator as dv                # noqa: E402
import monthly_review as mr                # noqa: E402
import report_generator as rg              # noqa: E402
import fixt                                # noqa: E402

DAY = '20261024'
PREV = '20261023'
_DEL = object()      # 字段删除哨兵


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
DT_NEXT = _DT(2026, 10, 25, 8, 0, 0)


class _GLM:
    """付费GLM调用mock(仅网络侧计数;发布事务/预检/读取器全真实)。"""

    def __init__(self):
        self.text = ('# 投资周报(SYNTHETIC FIX4矩阵)\n\n' + '本周市场综述与分资产回顾。' * 80)
        self.calls = 0

    def __call__(self, system_prompt, user_prompt, max_tokens=32000, timeout=900):
        self.calls += 1
        return self.text


def snap_with(mutator=None, ymd=DAY, **kw):
    """真实构建快照(dict): 全active采集JSON→(可选)注入回调改采集JSON→
    真实snapshot_builder.build_snapshot(Gate A为真实计算值)。"""
    with tempfile.TemporaryDirectory() as tdd:
        fixt.write_collectors(tdd, ymd, break_metric=kw.get('break_metric'),
                              missing=kw.get('missing', ()))
        if mutator:
            mutator(tdd, ymd)
        return sb.build_snapshot(target_ymd=ymd, data_dir=tdd, out_dir=tdd,
                                 as_of=fixt.as_of_for(ymd))


def mutated(base, mid, **fields):
    """deepcopy后定点篡改mid事实字段(_DEL=删除键);返回新快照dict。"""
    snap = copy.deepcopy(base)
    for f in snap['facts']:
        if f.get('metric_id') == mid:
            for k, v in fields.items():
                if v is _DEL:
                    f.pop(k, None)
                else:
                    f[k] = v
            return snap
    raise AssertionError(f'fixture无指标{mid}')


print("=" * 64)
print("IA-P0-1-FIX4 对抗测试: FIX4-01/02/03")
print("=" * 64)

# ════════════════════════════════════════════════════════════════════
# FIX4-01 金融事实必要字段与注册表身份校验(19例矩阵)
# ════════════════════════════════════════════════════════════════════
print("\n── FIX4-01 金融事实必要字段与注册表身份(19例矩阵)")
base = fixt.real_snapshot(DAY)          # 全active在场,Gate A=PASS(真实构建)
rec0 = rp.recompute_gate_a(base)
check("F4-01#01 正常完整事实: effective=PASS+gate_status一致+零非法+非核心零缺失",
      rec0['effective'] == 'PASS' and rp.gate_status(base) == ('PASS', '')
      and rec0['illegal_quality'] == [] and rec0['noncore_missing'] == []
      and rec0['non_research_facts'] == [],
      f"eff={rec0['effective']}")

ILLEGAL_CASES = [
    ('#02 删除value', 'SPX', {'value': _DEL}, 'value非法'),
    ('#03 value=None', 'SPX', {'value': None}, 'value非法'),
    ('#04 value=NaN', 'SPX', {'value': float('nan')}, 'value非有限实数'),
    ('#04 value=Infinity', 'SPX', {'value': float('inf')}, 'value非有限实数'),
    ('#05 value非法类型(字符串)', 'SPX', {'value': '7659.44'}, 'value非法'),
    ('#05 value非法类型(布尔)', 'SPX', {'value': True}, 'value非法'),
    ('#06 删除unit', 'SPX', {'unit': _DEL}, 'unit缺失'),
    ('#07 unit=None', 'SPX', {'unit': None}, 'unit缺失'),
    ('#08 unit与注册表不一致', 'SPX', {'unit': 'pt'}, 'unit与注册表不一致'),
    ('#09 删除observation_date', 'SPX', {'observation_date': _DEL},
     'observation_date缺失'),
    ('#10 observation_date不可解析(日历不存在)', 'SPX', {'observation_date': '2026-13-99'},
     'observation_date非法'),
    ('#11 观测日晚于研究截止(未来观测)', 'SPX', {'observation_date': '2026-10-25'},
     '晚于研究截止'),
    ('#12 删除source', 'SPX', {'source': _DEL}, 'source非对象'),
    ('#13 source非对象(字符串)', 'SPX', {'source': 'global_market_collector'},
     'source非对象'),
    ('#14 source缺collector身份', 'SPX',
     {'source': {'collector': '', 'file': f'global_market_{DAY}.json'}},
     'source.collector缺失'),
    ('#14 source缺file身份', 'SPX',
     {'source': {'collector': 'global_market_collector', 'file': ''}},
     'source.file缺失'),
    ('#15 派生缺calculation_ref', 'REAL_10Y', {'calculation_ref': _DEL},
     '派生事实缺calculation_ref'),
]
for name, mid, fields, msg in ILLEGAL_CASES:
    snap = mutated(base, mid, **fields)
    rec = rp.recompute_gate_a(snap)
    st, why = rp.gate_status(snap)
    check(f"F4-01{name}→effective=None(fail-closed)+点名原因+gate_status不可用",
          rec['effective'] is None and st is None
          and any(msg in s for s in rec['illegal_quality']),
          f"eff={rec['effective']} illegal={rec['illegal_quality'][:2]}")

# #16 未注册指标: 自报PASS=非法;仅FAIL可留诊断记录(不入有效研究事实)
snap = copy.deepcopy(base)
snap['facts'].append({'metric_id': 'FAKE_METRIC_FIX4', 'quality_status': 'PASS',
                      'value': 1.0, 'unit': '指数', 'observation_date': '2026-10-23',
                      'source': {'collector': 'x', 'file': 'y'}})
rec = rp.recompute_gate_a(snap)
check("F4-01#16 未注册指标自报PASS→非法(无注册表身份不得自宣有效)+fail-closed",
      rec['effective'] is None
      and any('未注册' in s and 'FAKE_METRIC_FIX4' in s
              for s in rec['illegal_quality']),
      f"illegal={rec['illegal_quality'][:2]}")
snap = copy.deepcopy(base)
snap['facts'].append({'metric_id': 'FAKE_METRIC_FIX4', 'quality_status': 'FAIL',
                      'value': None})
rec = rp.recompute_gate_a(snap)
check("F4-01#16b 未注册指标仅FAIL→诊断桶披露但不入有效研究事实/不阻断",
      rec['effective'] == 'PASS' and rp.gate_status(snap) == ('PASS', '')
      and any('FAKE_METRIC_FIX4' in s for s in rec['non_research_facts'])
      and rec['counts']['PASS'] == rec0['counts']['PASS'],
      f"eff={rec['effective']} nrf={rec['non_research_facts']}")

# #17/#18/#19 合法质量等级不误伤(真实引擎产出,非改quality_status自宣)
snap_a = fixt.real_snapshot(DAY, gate='DEGRADED')            # UMCSENT值坏'N/A'
rec_a = rp.recompute_gate_a(snap_a)
check("F4-01#17 合法非核心FAIL→DEGRADED(保留异常原值隔离,不升级FAIL不误判非法)",
      rec_a['effective'] == 'DEGRADED' and rp.gate_status(snap_a) == ('DEGRADED', '')
      and 'UMCSENT' in rec_a['noncore_fail'] and rec_a['illegal_quality'] == [],
      f"eff={rec_a['effective']}")
snap_f = fixt.real_snapshot(DAY, gate='FAIL')                # 核心SPX值坏
rec_f = rp.recompute_gate_a(snap_f)
check("F4-01#18 核心FAIL→Gate A=FAIL(合法FAIL事实结构豁免不等于放行)",
      rec_f['effective'] == 'FAIL' and 'SPX' in rec_f['core_fail']
      and rp.gate_status(snap_f) == ('FAIL', ''),
      f"eff={rec_f['effective']}")


def _stale_umc(daily, ymd):
    p = os.path.join(daily, f'macro_{ymd}.json')
    with open(p, encoding='utf-8') as f:
        obj = json.load(f)
    obj['data']['UMCSENT']['date'] = '2026-04-01'   # 月频92天窗外(旧期仍在场)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False)


snap_d = snap_with(_stale_umc)
rec_d = rp.recompute_gate_a(snap_d)
umc_fact = next(f for f in snap_d['facts'] if f.get('metric_id') == 'UMCSENT')
check("F4-01#19 合法DEGRADED(真实引擎新鲜度降级)→DEGRADED不误判非法",
      rec_d['effective'] == 'DEGRADED' and rp.gate_status(snap_d) == ('DEGRADED', '')
      and umc_fact['quality_status'] == 'DEGRADED'
      and 'UMCSENT' in rec_d['noncore_degraded']
      and rec_d['illegal_quality'] == [],
      f"eff={rec_d['effective']} qs={umc_fact['quality_status']}")

# 下游研究入口(代表性案例): 快照在批次生成后被改写→真实装配器/预检拒绝
with tempfile.TemporaryDirectory() as td:
    fixt.build_full_day(td, DAY)
    sp = os.path.join(td, 'data', 'daily', f'research_snapshot_{DAY}.json')
    disk = json.load(open(sp, encoding='utf-8'))
    for f in disk['facts']:
        if f.get('metric_id') == 'SPX':
            del f['value']
    with open(sp, 'w', encoding='utf-8') as f:
        json.dump(disk, f, ensure_ascii=False)
    with mock.patch.object(da, 'DATA_DIR', os.path.join(td, 'data')), \
         mock.patch.object(da, 'datetime', DT_DAY):
        try:
            quiet(da.main)
            asm_code = 0
        except SystemExit as e:
            asm_code = e.code
    with mock.patch.object(rg, 'DATA_DIR', os.path.join(td, 'data')), \
         mock.patch.object(rg, 'datetime', DT_DAY):
        pre_ok, problems = (lambda r: (r[0], r[1]))(quiet(rg.verify_research_inputs))
    pm = rp.load_meta(os.path.join(td, 'data', 'weekly', f'data_pack_{DAY}.md'))
    vok, vwhy = rp.verify_meta_gate_a(pm, disk)
    check("F4-01#下游 非法快照进入真实研究入口: 装配器exit2+周报预检拒"
          "+包meta↔权威快照gate口径失配",
          asm_code == 2 and pre_ok is False and vok is False,
          f"asm={asm_code} pre={pre_ok} meta={vok}")

# ════════════════════════════════════════════════════════════════════
# FIX4-02 正式报告身份字段严格核验(16例矩阵)
# ════════════════════════════════════════════════════════════════════
print("\n── FIX4-02 正式报告身份字段(16例矩阵)")


def publish(td, ymd, gate='PASS', gate_b='PASS', dt=DT_DAY):
    """真实发布: build_full_day(真实快照/锚点/包/评分卡)→真实
    generate_weekly_report发布事务(仅mock付费GLM与Gate B裁决值)。"""
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
    real_apply = rg.apply_status_updates

    def _apply(report, classification, anchors=None, today_str=None,
               thesis_path=None, views_path=None):
        return real_apply(report, classification, anchors=anchors,
                          today_str=today_str, thesis_path=thesis_path,
                          views_path=views_path)

    def _validate(md_path, anchors=None, anchors_file=None):
        return (gate_b, ['SYNTHETIC FIX4警告'])
    patches = [
        mock.patch.object(rg, 'DATA_DIR', os.path.join(td, 'data')),
        mock.patch.object(rg, 'OUTPUT_DIR', out_dir),
        mock.patch.object(rg, 'CONFIG_DIR', cfg),
        mock.patch.object(rg, 'datetime', dt),
        mock.patch.object(rg, '_call_glm', glm),
        mock.patch.object(rg, 'apply_status_updates', _apply),
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
    return code, out_dir


def status_file(out, ymd):
    return os.path.join(out, f'report_status_{ymd}.json')


def tweak_status(out, ymd, raw=None, **fields):
    """定点篡改发布状态(_DEL=删键);raw非None时整文件替换为该字节串。"""
    p = status_file(out, ymd)
    if raw is not None:
        with open(p, 'w', encoding='utf-8') as f:
            f.write(raw)
        return
    with open(p, encoding='utf-8') as f:
        st = json.load(f)
    for k, v in fields.items():
        if v is _DEL:
            st.pop(k, None)
        else:
            st[k] = v
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(st, f, ensure_ascii=False, indent=1)


def consumer_verdicts(td, out, ymd):
    """真实消费者面: formal_view/扫描器/上一期读取/校验入口/月度索引。"""
    md = os.path.join(out, f'weekly_report_{ymd}.md')
    view, _r = rp.formal_report_view(md)
    scanned = ymd in [v['ymd'] for v in rp.scan_formal_weekly_reports(out)]
    lv, _lr = rp.latest_formal_weekly_report(out)
    with mock.patch.object(rg, 'OUTPUT_DIR', out), \
         mock.patch.object(rg, 'datetime', DT_NEXT):
        prev_text = quiet(rg.load_previous_report) or ''
    found, mode = dv.find_latest_report_for_validation(out)
    views_path = os.path.join(td, 'config', 'views.json')
    with mock.patch.object(mr, 'ROOT_DIR', td), \
         mock.patch.object(mr, 'DATA_DIR', os.path.join(td, 'data')):
        ctx = quiet(mr.gather_month_context, ymd[:6], views_path=views_path)
    idx_line = next((l for l in ctx.get('weekly_reports', []) if ymd in l), '')
    return {'view': view, 'scanned': scanned,
            'latest': bool(lv and lv['ymd'] == ymd),
            'prev_formal': ('未验证' not in prev_text and 'SYNTHETIC' in prev_text),
            'dv_mode': mode, 'dv_file': os.path.basename(found) if found else None,
            'idx_tagged': ('未验证档案' in idx_line), 'idx_listed': bool(idx_line)}


with tempfile.TemporaryDirectory() as td:
    code, out = publish(td, DAY)
    v0 = consumer_verdicts(td, out, DAY)
    check("F4-02#15 正常PASS发布→formal认定+全真实消费者采纳(索引无未验证标注)",
          code == 0 and v0['view'] is not None and v0['scanned'] and v0['latest']
          and v0['prev_formal'] and v0['dv_mode'] == 'formal'
          and v0['idx_listed'] and not v0['idx_tagged'],
          f"code={code} view={v0['view'] is not None} dv={v0['dv_mode']}")

REJECT_CASES = [
    ('#01 report_file缺失', {'report_file': _DEL}),
    ('#01 report_file错误', {'report_file': f'weekly_report_{PREV}.md'}),
    ('#02 target_date缺失', {'target_date': _DEL}),
    ('#02 target_date错误', {'target_date': PREV}),
    ('#03 report_path缺失', {'report_path': _DEL}),
    ('#03 report_path指向其他目录', None),
    ('#03 report_path指向另一报告', None),
    ('#03 report_path非规范裸文件名', None),
    ('#04 published=False', {'published': False}),
    ('#05 final_quality=FAIL', {'final_quality': 'FAIL'}),
    ('#06 report_digest不符', {'report_digest': 'deadbeef'}),
]
for name, fields in REJECT_CASES:
    with tempfile.TemporaryDirectory() as td:
        code, out = publish(td, DAY)
        assert code == 0, f'{name}基线发布失败'
        if name.endswith('其他目录'):
            tweak_status(out, DAY, report_path=os.path.join(out, 'elsewhere',
                                                            f'weekly_report_{DAY}.md'))
        elif name.endswith('另一报告'):
            other = os.path.join(out, f'weekly_report_{PREV}.md')
            with open(other, 'w', encoding='utf-8') as f:
                f.write('# 另一份报告\n')
            tweak_status(out, DAY, report_path=other)
        elif name.endswith('裸文件名'):
            tweak_status(out, DAY, report_path=f'weekly_report_{DAY}.md')
        else:
            tweak_status(out, DAY, **fields)
        v = consumer_verdicts(td, out, DAY)
        check(f"F4-02{name}→formal拒绝+全部真实消费者不采纳(不默认放行)",
              v['view'] is None and not v['scanned'] and not v['latest']
              and not v['prev_formal'] and v['dv_mode'] == 'archive'
              and v['idx_listed'] and v['idx_tagged'],
              f"view={v['view']} scan={v['scanned']} dv={v['dv_mode']}")

with tempfile.TemporaryDirectory() as td:
    code, out = publish(td, DAY)
    tweak_status(out, DAY, raw='{"report_file": "weekly_report_20261024.md", '
                              '"broken": ')     # 状态损坏(截断/半写)
    v = consumer_verdicts(td, out, DAY)
    check("F4-02#07 状态损坏(非JSON)→formal拒绝+消费者回退未验证档案",
          v['view'] is None and not v['scanned'] and v['dv_mode'] == 'archive'
          and v['idx_tagged'],
          f"view={v['view'] is not None}")

with tempfile.TemporaryDirectory() as td:
    # #08 首发布中断: 报告文件已替换到位但主状态未写入(仅candidate过程文件)
    code, out = publish(td, DAY)
    st = json.load(open(status_file(out, DAY), encoding='utf-8'))
    os.remove(status_file(out, DAY))
    cand = dict(st, published=False, awaiting_publish=True)
    with open(os.path.join(out, f'report_status_{DAY}_candidate.json'), 'w',
              encoding='utf-8') as f:
        json.dump(cand, f, ensure_ascii=False)
    v = consumer_verdicts(td, out, DAY)
    check("F4-02#08 首发布中断(仅candidate)→该报告不算已发布+消费者回退档案模式",
          v['view'] is None and not v['scanned'] and v['dv_mode'] == 'archive'
          and v['idx_tagged'] and not v['prev_formal'],
          f"view={v['view'] is not None} dv={v['dv_mode']}")

with tempfile.TemporaryDirectory() as td:
    # #09 中断但已有合格旧报告: 当日无效不阻断上一合格期被读取
    code1, out = publish(td, PREV, dt=_DT(2026, 10, 23, 8, 0, 0))
    code2, _ = publish(td, DAY)
    st = json.load(open(status_file(out, DAY), encoding='utf-8'))
    os.remove(status_file(out, DAY))
    with open(os.path.join(out, f'report_status_{DAY}_candidate.json'), 'w',
              encoding='utf-8') as f:
        json.dump(dict(st, published=False, awaiting_publish=True), f,
                  ensure_ascii=False)
    md = os.path.join(out, f'weekly_report_{DAY}.md')
    v_day, r_day = rp.formal_report_view(md)
    with mock.patch.object(rg, 'OUTPUT_DIR', out), \
         mock.patch.object(rg, 'datetime', DT_NEXT):
        prev_text = quiet(rg.load_previous_report) or ''
    check("F4-02#09 当日中断+昨日合格→当日不算formal+真实load_previous_report"
          "回读昨日合格报告(无未验证标注)",
          code1 == 0 and code2 == 0 and v_day is None
          and 'SYNTHETIC' in prev_text and '未验证' not in prev_text,
          f"day_formal={v_day is not None} r={r_day[:60]} "
          f"status_exists={os.path.exists(status_file(out, DAY))}")

with tempfile.TemporaryDirectory() as td:
    # #10 路径规范化不误伤: 同一文件的别名(./与/../回溯)仍接受
    code, out = publish(td, DAY)
    tweak_status(out, DAY,
                 report_path=os.path.join(out, './', f'weekly_report_{DAY}.md'))
    v1, r1 = rp.formal_report_view(os.path.join(out, f'weekly_report_{DAY}.md'))
    tweak_status(out, DAY,
                 report_path=os.path.join(out, 'sub/../', f'weekly_report_{DAY}.md'))
    v2, r2 = rp.formal_report_view(os.path.join(out, f'weekly_report_{DAY}.md'))
    check("F4-02#10 同一文件路径别名(规范化后同一)→不误拒(reliable normalization)",
          v1 is not None and v2 is not None,
          f"alias1={r1[:30]} alias2={r2[:30]}")

with tempfile.TemporaryDirectory() as td:
    # #16 正常DEGRADED发布→同样获formal认定
    code, out = publish(td, DAY, gate='DEGRADED')
    v = consumer_verdicts(td, out, DAY)
    check("F4-02#16 正常DEGRADED发布→formal认定+消费者采纳(身份校验与质量等级无关)",
          code == 0 and v['view'] is not None
          and v['view']['status']['final_quality'] == 'DEGRADED'
          and v['scanned'] and v['dv_mode'] == 'formal' and not v['idx_tagged'],
          f"code={code}")

# ════════════════════════════════════════════════════════════════════
# FIX4-03 非核心指标完全缺失的合理降级与披露
# ════════════════════════════════════════════════════════════════════
print("\n── FIX4-03 非核心完全缺失的降级与披露")
snap_b = fixt.real_snapshot(DAY, missing=('UMCSENT',))       # 场景B: 完全缺席
rec_b = rp.recompute_gate_a(snap_b)
check("F4-03#B 非核心完全缺席→noncore_missing点名+可核查缺失原因+Gate A=DEGRADED",
      rec_b['effective'] == 'DEGRADED'
      and rec_b['noncore_missing'] == ['UMCSENT']
      and '采集遗漏' in rec_b['noncore_missing_detail'].get('UMCSENT', '')
      and rec_b['noncore_fail'] == []                        # 不与场景A互替
      and not any(f.get('metric_id') == 'UMCSENT' for f in snap_b['facts']),
      f"eff={rec_b['effective']} missing={rec_b['noncore_missing']}")
check("F4-03#B2 未补零未伪造(quality.overall不为缺席虚增FAIL计数,Gate A与缺失清单一致)",
      rp.gate_status(snap_b) == ('DEGRADED', '')
      and rec_b['counts']['FAIL'] == 0
      and next(f for f in snap_b['facts']
               if f.get('metric_id') == 'SPX')['quality_status'] == 'PASS',
      f"counts={rec_b['counts']}")
with tempfile.TemporaryDirectory() as td:
    # 真实装配路径产包(fixture只备快照/锚点/评分卡,包由真实data_assembler生成)
    snap, _sp, paths = fixt.build_full_day(td, DAY, missing=('UMCSENT',),
                                           skip=('pack', 'pack_meta'))
    with mock.patch.object(da, 'DATA_DIR', os.path.join(td, 'data')), \
         mock.patch.object(da, 'datetime', DT_DAY):
        quiet(da.main)
    pack = os.path.join(paths['weekly'], f'data_pack_{DAY}.md')
    md = open(os.path.join(paths['daily'], f'research_snapshot_{DAY}.md'),
              encoding='utf-8').read()
    pm = rp.load_meta(pack)
    check("F4-03#B3 缺席逐级披露: 快照MD+数据包正文+包meta记录(其余有效数据继续研究)",
          snap['gate_a']['status'] == 'DEGRADED'
          and '非核心指标缺失' in md and 'UMCSENT' in md
          and 'UMCSENT' in open(pack, encoding='utf-8').read()
          and pm.get('noncore_missing') == ['UMCSENT'] and pm.get('gate_a') == 'DEGRADED',
          f"gate={snap['gate_a']['status']} pm={pm.get('noncore_missing')}")

snap_c = fixt.real_snapshot(DAY, missing=('SPX',))            # 核心完全缺席
rec_c = rp.recompute_gate_a(snap_c)
check("F4-03#C 核心完全缺席→core_missing点名+Gate A=FAIL(不降级放行)",
      rec_c['effective'] == 'FAIL' and rec_c['core_missing'] == ['SPX'],
      f"eff={rec_c['effective']} core={rec_c['core_missing']}")

check("F4-03#M 月度边界: 旧期在场(尚未发布新期)=新鲜度降级披露,≠缺席不进缺失清单",
      rec_d['effective'] == 'DEGRADED'
      and 'UMCSENT' in rec_d['noncore_degraded']
      and 'UMCSENT' not in rec_d['noncore_missing']
      and rec_d['noncore_missing_detail'].get('UMCSENT') is None,
      f"degraded={rec_d['noncore_degraded']} missing={rec_d['noncore_missing']}")


def _drop_china(daily, ymd):
    os.remove(os.path.join(daily, f'china_{ymd}.json'))


snap_s = snap_with(_drop_china)
rec_s = rp.recompute_gate_a(snap_s)
cn_missing = {m: r for m, r in rec_s['noncore_missing_detail'].items()
              if r.startswith('来源文件缺失(china')}
check("F4-03#S 来源文件级缺失: 独立归因'来源文件缺失(china:…)'(与在场缺席区分)"
      "+核心缺席照常FAIL",
      rec_s['effective'] == 'FAIL'
      and len(cn_missing) >= 3
      and all(not r.startswith('来源文件在场') for r in cn_missing.values()),
      f"eff={rec_s['effective']} cn_missing={list(cn_missing)[:3]}")

snap_dep = copy.deepcopy(base)
snap_dep['facts'].append({'metric_id': 'REAL_SHORT', 'quality_status': 'FAIL',
                          'value': None})                     # deprecated注册指标
rec_dep = rp.recompute_gate_a(snap_dep)
check("F4-03#D deprecated指标(REAL_SHORT)不追责: 不入缺失清单,FAIL仅留诊断",
      'REAL_SHORT' not in rec_dep['noncore_missing']
      and any('REAL_SHORT' in s for s in rec_dep['non_research_facts'])
      and rec_dep['effective'] == 'PASS',
      f"eff={rec_dep['effective']}")

snap_nb = copy.deepcopy(base)
snap_nb.pop('sources_status', None)      # 来源状态整体缺失
rec_nb = rp.recompute_gate_a(snap_nb)
# FIX5-04(DEF-F4-002)语义取代FIX4时"显式边界+继续PASS": sources_status缺失
# =采集批次完整性不可证明→fail-closed(effective=None),不得静默跳过非核心
# 缺失判断后照常PASS;失败原因可查(sources_problems),且快照级拒绝不依赖
# 任何单指标缺席——比原边界行为严格,无删除任何负向检查
check("F4-03#N(_FIX5-04收紧) 无sources_status→fail-closed不可证明,原因可查",
      rec_nb['effective'] is None
      and rec_nb.get('sources_problems')
      and 'sources_status' in rec_nb['sources_problems'][0]
      and any('sources_status' in s for s in rec_nb['illegal_quality']),
      f"eff={rec_nb['effective']} probs={rec_nb.get('sources_problems')}")

# ═══ 汇总 ═══════════════════════════════════════════════════════════
print("\n" + "=" * 64)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 64)
sys.exit(1 if FAIL else 0)
