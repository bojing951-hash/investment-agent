#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P0-1-FIX3 原始冻结编号E2E-01~14(FIX3-05/F2-NEW-005)

按FIX3指令冻结编号表**逐条原样**重建(标题与语义不得改写),每场景固定
六要素文档: [真实入口|合成输入|mock范围|执行模块|文件副作用|预期与断言]。

链路真实性约束(FIX3-05):
- 前段全真实: 采集JSON → snapshot_builder(**真实CLI子进程**) →
  macro_scorecard.main → data_assembler.main → 锚点/提示词构建;
- 后段真实入口 report_generator.generate_weekly_report: Gate A预检
  (verify_research_inputs)、来源核验(verify_anchor_batch/
  verify_meta_gate_a)、正式读取器(rp.formal_report_view/
  load_previous_report)、发布事务(候选→Gate B→状态→原子替换)全部真实执行;
- 唯一mock = 付费GLM(_call_glm)与Gate B裁决值(validate_generated_report
  内部即GLM付费调用,mock其返回=mock付费API;Gate B裁决逻辑本身由
  test_p01_fix1/fix2/fix3套件覆盖);
- config/thesis/views 经 CONFIG_DIR/DEFAULT_VIEWS_PATH 指向沙箱,由**真实
  加载器**读取(load_framework/load_theses/load_views不mock);
- 禁止mock: Gate A、来源核验、正式读取器、发布事务(本套件零mock于此)。

状态: 本套件通过 = "开发者离线E2E通过"; "独立Agent已复核"由Agent4另行
判定,本套件不自declare。

fixture: tests/fixt.py 真实注册表全核心(32 core)SYNTHETIC采集→真实
snapshot_builder/装配/锚点; 临时目录隔离零生产触碰; 断言只针对真实函数
返回值/磁盘字节/退出码,无源码字符串扫描。
"""
import os
import sys
import io
import json
import glob
import subprocess
import tempfile
import contextlib
import unittest.mock as mock

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PY = sys.executable

sys.path.insert(0, os.path.join(ROOT, 'scripts'))
sys.path.insert(0, HERE)

PASS = FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    mark = '✅' if cond else '❌'
    print(f"  {mark} {name}" + (f" [{detail}]" if detail and not cond else ''))
    PASS, FAIL = PASS + (1 if cond else 0), FAIL + (0 if ok_bool(cond) else 1)


def ok_bool(cond):
    return bool(cond)


def quiet(fn, *a, **kw):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **kw)


def cli(argv):
    """真实子进程运行仓库CLI,返回(returncode, stdout+stderr)。"""
    r = subprocess.run([PY] + argv, capture_output=True, text=True, cwd=ROOT)
    return r.returncode, (r.stdout or '') + (r.stderr or '')


import research_provenance as rp          # noqa: E402
import snapshot_builder as sb             # noqa: E402
import data_assembler as da               # noqa: E402
import data_validator as dv               # noqa: E402
import report_generator as rg             # noqa: E402
import run_weekly                         # noqa: E402
import macro_scorecard as ms              # noqa: E402
import daily_prediction_observer as dpo    # noqa: E402
import fixt                               # noqa: E402

DAY = '20261024'        # 本场景日(周六,day>7→pending_month/quarter自然为None)
PREV = '20261023'       # 跨日场景: 上一发布日


def _DT(y, m, d):
    class _C:
        @staticmethod
        def now():
            import datetime as _dt
            return _dt.datetime(y, m, d, 8, 0, 0)

        @staticmethod
        def strptime(s, f):
            import datetime as _dt
            return _dt.datetime.strptime(s, f)
    return _C


DT_DAY = _DT(2026, 10, 24)
DT_PREV = _DT(2026, 10, 23)
DT_NEXT = _DT(2026, 10, 25)


class _GLM:
    """付费GLM调用mock(仅此一处mock网络侧)。"""

    def __init__(self, text=None):
        self.text = text or ('# 投资周报(SYNTHETIC E2E冻结表)\n\n'
                             + '本周市场综述与分资产回顾。' * 80)
        self.calls = 0

    def __call__(self, system_prompt, user_prompt, max_tokens=32000, timeout=900):
        self.calls += 1
        return self.text


print("=" * 64)
print("IA-P0-1 原始冻结编号E2E-01~14(FIX3-05/F2-NEW-005)")
print("=" * 64)


def chain_build(td, ymd=DAY, gate='PASS', break_metric=None, missing=(),
                with_pack=True, post_collectors=None):
    """链路前段(全真实): 采集JSON → snapshot_builder CLI(真实子进程) →
    macro_scorecard.main → data_assembler.main → 锚点prompt。
    Gate FAIL日sb CLI仍落盘快照(exit≠0属合法记录),装配器exit 2不产正式包。
    post_collectors: 写完采集JSON后的注入回调(daily, ymd)——用于构造
    数值型区间外等"合法链路内"的数据形态(如E2E-12的UMCSENT区间外数值,
    经真实事实引擎判FAIL,而非事后人工篡改锚点)。"""
    daily = os.path.join(td, 'data', 'daily')
    weekly = os.path.join(td, 'data', 'weekly')
    os.makedirs(daily, exist_ok=True)
    os.makedirs(weekly, exist_ok=True)
    if break_metric is None:
        break_metric = {'DEGRADED': 'UMCSENT', 'FAIL': 'SPX'}.get(gate)
    fixt.write_collectors(daily, ymd, break_metric=break_metric, missing=missing)
    if post_collectors:
        post_collectors(daily, ymd)
    code, out = cli([os.path.join(ROOT, 'scripts', 'snapshot_builder.py'),
                     '--date', ymd, '--data-dir', daily, '--out-dir', daily,
                     '--trusted-root', td,
                     # IA-P0-2-W2: 钉定研究截止=场景日08:00(此前用真实墙钟,
                     # 时效判定随运行日期漂移——场景日本身的语义即"以该日为
                     # 研究截止",非放松任何门禁;期望语义不变,仅消除时间炸弹)
                     '--as-of', fixt.as_of_for(ymd)])
    snap_file = os.path.join(daily, f'research_snapshot_{ymd}.json')
    if not os.path.exists(snap_file):
        return {'sb_exit': code, 'sb_out': out, 'daily': daily, 'weekly': weekly}, code
    try:
        quiet(ms.main, date_str=ymd, data_dir=daily)
    except Exception:
        pass   # 评分卡异常不阻断链路构造(其授权语义由fix2套件单独覆盖)
    pack_code = None
    if with_pack:
        try:
            with mock.patch.object(da, 'DATA_DIR', os.path.join(td, 'data')), \
                 mock.patch.object(da, 'datetime', DT_DAY):
                quiet(da.main)
            pack_code = 0
        except SystemExit as e:
            pack_code = e.code
    with open(os.path.join(daily, f'anchors_{ymd}.json'), encoding='utf-8') as f:
        anchors = json.load(f)
    with open(os.path.join(daily, f'anchor_prompt_{ymd}.md'), 'w', encoding='utf-8') as f:
        f.write(dv.generate_anchor_prompt_block(anchors))
    ensure_state_sandbox(td)
    # sb_exit=真实CLI退出码(FAIL日快照仍落盘但CLI exit 2——链路继续由装配器/
    # 周报入口裁决,此处只如实记录)
    return {'sb_exit': code, 'daily': daily, 'weekly': weekly,
            'pack_code': pack_code,
            'snapshot': snap_file,
            'anchors': os.path.join(daily, f'anchors_{ymd}.json'),
            'pack': os.path.join(weekly, f'data_pack_{ymd}.md'),
            'pack_meta': rp.meta_path_for(os.path.join(weekly, f'data_pack_{ymd}.md')),
            'prompt': os.path.join(daily, f'anchor_prompt_{ymd}.md')}, code


def ensure_state_sandbox(td):
    """长期状态沙箱物化: 真实apply/真实加载器都指向这里。"""
    cfg = os.path.join(td, 'config')
    os.makedirs(cfg, exist_ok=True)
    for name, obj in (('thesis.json', {'theses': []}),
                      ('views.json', {'views': [], 'predictions': []})):
        p = os.path.join(cfg, name)
        if not os.path.exists(p):
            with open(p, 'w', encoding='utf-8') as f:
                json.dump(obj, f, ensure_ascii=False)


def state_files(td):
    cfg = os.path.join(td, 'config')
    return {f: open(os.path.join(cfg, f), 'rb').read()
            for f in ('thesis.json', 'views.json')
            if os.path.exists(os.path.join(cfg, f))}


def report_run(td, gate_b='PASS', dt=DT_DAY, glm_text=None):
    """链路后段: 真实generate_weekly_report。
    mock范围(仅): 付费GLM(_call_glm)与Gate B裁决值(validate_generated_report
    内部为GLM付费调用); config经CONFIG_DIR/DEFAULT_VIEWS_PATH重定向由真实
    加载器读取; load_previous_report/发布事务/预检/Gate A全部真实。
    返回(exit_code, out_dir, applied, glm)。applied=真实apply收到的分级。"""
    out_dir = os.path.join(td, 'output', 'weekly')
    glm = _GLM(glm_text)
    ensure_state_sandbox(td)
    applied = []
    real_apply = rg.apply_status_updates

    def _apply(report, classification, anchors=None, today_str=None,
               thesis_path=None, views_path=None):
        applied.append(classification)
        return real_apply(report, classification, anchors=anchors,
                          today_str=today_str, thesis_path=thesis_path,
                          views_path=views_path)

    def _validate(md_path, anchors=None, anchors_file=None):
        return (gate_b, ['SYNTHETIC E2E警告'])

    patches = [
        mock.patch.object(rg, 'DATA_DIR', os.path.join(td, 'data')),
        mock.patch.object(rg, 'OUTPUT_DIR', out_dir),
        mock.patch.object(rg, 'CONFIG_DIR', os.path.join(td, 'config')),
        mock.patch.object(rg, 'datetime', dt),
        mock.patch.object(rg, '_call_glm', glm),
        mock.patch.object(rg, 'apply_status_updates', _apply),
        mock.patch.object(rg, 'validate_generated_report', _validate),
        mock.patch.object(rg.allocation_engine, 'DEFAULT_VIEWS_PATH',
                          os.path.join(td, 'config', 'views.json')),
    ]
    with contextlib.ExitStack() as stack:
        for p in patches:
            stack.enter_context(p)
        try:
            quiet(rg.generate_weekly_report)
            code = 0
        except SystemExit as e:
            code = e.code
    return code, out_dir, applied, glm


def run_verify(td, dt=DT_DAY):
    """真实verify_research_inputs(周报预检,零mock): 返回(ok, problems)。"""
    with mock.patch.object(rg, 'DATA_DIR', os.path.join(td, 'data')), \
         mock.patch.object(rg, 'datetime', dt):
        ok, problems, _ctx = quiet(rg.verify_research_inputs)
    return ok, problems


def formal(out_dir, ymd):
    """真实正式读取器认定(FIX3-02): 返回formal_report_view的view(或None)。"""
    view, _r = rp.formal_report_view(os.path.join(out_dir, f'weekly_report_{ymd}.md'))
    return view


# ════════════════════════════════════════════════════════════════════
# E2E-01 完整正常数据进入研究流程
# ────────────────────────────────────────────────────────────────────
# 真实入口: snapshot_builder CLI子进程 → macro_scorecard.main →
#   data_assembler.main → report_generator.generate_weekly_report
# 合成输入: fixt全核心(32core)齐备采集JSON(4通道)
# mock范围: 付费GLM(_call_glm)与Gate B裁决值('PASS');其余零mock
# 执行模块: fact_engine→snapshot_builder→macro_scorecard→data_assembler
#   →research_provenance(来源核验)→report_generator全流程(发布事务真实)
# 文件副作用: 快照/锚点+meta/评分卡/数据包+meta/anchor_prompt落沙箱;
#   weekly_report_DAY.md+report_status_DAY.json(published)落沙箱;
#   生产目录零触碰(临时目录隔离)
# 预期与断言: sb CLI exit0且Gate A=PASS;装配exit0且包meta.gate_a='PASS';
#   周报exit0、GLM恰1次、真实formal_report_view认定(published=True+
#   final_quality='PASS'+'PASS'分级回写1次)
# ════════════════════════════════════════════════════════════════════
print("\n── E2E-01 完整正常数据进入研究流程")
with tempfile.TemporaryDirectory() as td:
    paths, c = chain_build(td, DAY, gate='PASS')
    snap = json.load(open(paths['snapshot'], encoding='utf-8'))
    check("E2E-01a 快照构建(CLI真实子进程)exit0+Gate A=PASS(全核心在场)",
          c == 0 and paths['sb_exit'] == 0 and snap['gate_a']['status'] == 'PASS',
          f"sb={paths['sb_exit']} gate={snap['gate_a']['status']}")
    check("E2E-01b 装配器exit0+正式包在场+包meta.gate_a='PASS'(与权威一致)",
          paths['pack_code'] == 0 and os.path.exists(paths['pack'])
          and rp.load_meta(paths['pack']).get('gate_a') == 'PASS',
          f"pack={paths['pack_code']}")
    code, out, applied, glm = report_run(td, gate_b='PASS')
    v = formal(out, DAY)
    check("E2E-01c 周报全流程exit0+GLM恰1次+真实formal_view认定(published+PASS)",
          code == 0 and glm.calls == 1 and v is not None
          and v['status']['published'] is True
          and v['status']['final_quality'] == 'PASS',
          f"exit={code} glm={glm.calls}")
    check("E2E-01d 分级'PASS'回写调度1次(真实apply,长期状态沙箱内)",
          applied == ['PASS'] and os.path.exists(os.path.join(out, f'weekly_report_{DAY}.md')),
          f"applied={applied}")

# ════════════════════════════════════════════════════════════════════
# E2E-02 部分非核心数据缺失，合理降级
# ────────────────────────────────────────────────────────────────────
# 真实入口: 同E2E-01全链(真实CLI+真实main+真实周报入口)
# 合成输入: 非核心指标UMCSENT两种"缺失"形态——(甲)值坏'N/A'(采集到但不可用)
#   (乙)指标整体缺席(FIX4-03原始场景B:不出现在任何采集文件)
# mock范围: 付费GLM与Gate B裁决值('PASS')
# 执行模块: 同E2E-01(recompute_gate_a真实分级裁决+FIX4-03缺席清单)
# 文件副作用: 沙箱内同E2E-01(甲/乙形态各发布DEGRADED周报)
# 预期与断言: (甲)Gate A=DEGRADED(非核心FAIL→合理降级,不阻断)→装配产包
#   →周报exit0→真实formal_view认定final_quality='DEGRADED';
#   (乙)整体缺席→缺席进noncore_missing清单+快照MD/数据包meta逐级披露,
#   Gate A=DEGRADED(不再无声PASS),未补零未伪造UMCSENT事实,其余有效数据
#   继续装配研究,正式周报保留可见降级解释(点名缺席指标)
# ════════════════════════════════════════════════════════════════════
print("\n── E2E-02 部分非核心数据缺失，合理降级")
with tempfile.TemporaryDirectory() as td:
    paths, c = chain_build(td, DAY, gate='DEGRADED')   # (甲)UMCSENT值坏
    snap = json.load(open(paths['snapshot'], encoding='utf-8'))
    check("E2E-02a 非核心值坏→Gate A=DEGRADED(合理降级,非FAIL)",
          c == 0 and snap['gate_a']['status'] == 'DEGRADED'
          and snap['gate_a']['core_missing'] == [],
          f"gate={snap['gate_a']['status']}")
    check("E2E-02b 装配器继续产包(exit0)+包meta.gate_a='DEGRADED'",
          paths['pack_code'] == 0 and os.path.exists(paths['pack'])
          and rp.load_meta(paths['pack']).get('gate_a') == 'DEGRADED',
          f"pack={paths['pack_code']}")
    code, out, applied, glm = report_run(td, gate_b='PASS')
    v = formal(out, DAY)
    check("E2E-02c 全链exit0+formal_view认定final_quality='DEGRADED'(降级可发布)",
          code == 0 and v is not None and v['status']['final_quality'] == 'DEGRADED',
          f"exit={code}")
with tempfile.TemporaryDirectory() as td:
    # (乙)整体缺席(FIX4-03原始场景B,不得偷换成"值坏"场景甲)
    paths, c = chain_build(td, DAY, missing=('UMCSENT',))
    snap = json.load(open(paths['snapshot'], encoding='utf-8'))
    ga = snap['gate_a']
    fake = [f for f in snap['facts'] if f.get('metric_id') == 'UMCSENT']
    md = open(paths['snapshot'].replace('.json', '.md'), encoding='utf-8').read()
    check("E2E-02d 非核心整体缺席→noncore_missing点名+Gate A=DEGRADED(不再无声PASS)",
          c == 0 and ga['status'] == 'DEGRADED'
          and ga.get('noncore_missing') == ['UMCSENT']
          and 'UMCSENT' not in ga.get('core_fail', [])
          and fake == [],
          f"gate={ga['status']} missing={ga.get('noncore_missing')}")
    check("E2E-02d2 未补零未伪造(无UMCSENT事实)且其余有效数据继续装配研究",
          os.path.exists(paths['pack']) and paths['pack_code'] == 0
          and len(snap['facts']) >= 78
          and '非核心指标缺失' in md and 'UMCSENT' in md
          and 'UMCSENT' in open(paths['pack'], encoding='utf-8').read()
          and rp.load_meta(paths['pack']).get('noncore_missing') == ['UMCSENT'],
          f"facts={len(snap['facts'])} pack={paths['pack_code']}")
    code, out, applied, glm = report_run(td, gate_b='PASS')
    rmd = open(os.path.join(out, f'weekly_report_{DAY}.md'), encoding='utf-8').read() \
        if code == 0 else ''
    check("E2E-02d3 缺席降级可发布(exit0)+正式周报保留可见降级解释(点名缺席指标)",
          code == 0 and formal(out, DAY) is not None
          and '非核心缺失' in rmd and 'UMCSENT' in rmd,
          f"exit={code}")

# ════════════════════════════════════════════════════════════════════
# E2E-03 核心失败导致Gate A FAIL
# ─────────────────═══════════════════════════════════════════════════
# 真实入口: snapshot_builder CLI(核心SPX值坏)
# 合成输入: 核心指标SPX值置'N/A'(类型校验FAIL)
# mock范围: 零mock(纯前段)
# 执行模块: fact_engine类型校验→snapshot_builder真实裁决
# 文件副作用: FAIL快照落盘(合法存证记录);装配器exit2不产正式包
# 预期与断言: Gate A=FAIL(core_fail含SPX);sb CLI exit≠0;装配器exit2且无包
# ════════════════════════════════════════════════════════════════════
print("\n── E2E-03 核心失败导致Gate A FAIL")
with tempfile.TemporaryDirectory() as td:
    paths, c = chain_build(td, DAY, gate='FAIL')
    snap = json.load(open(paths['snapshot'], encoding='utf-8'))
    check("E2E-03a 核心SPX值坏→Gate A=FAIL(core_fail点名SPX)+sb CLI exit≠0(存证仍落盘)",
          snap['gate_a']['status'] == 'FAIL' and 'SPX' in snap['gate_a']['core_fail']
          and paths['sb_exit'] != 0,
          f"gate={snap['gate_a']['status']} sb={paths['sb_exit']}")
    check("E2E-03b 装配器拒绝产正式包(exit2,无data_pack)",
          paths['pack_code'] == 2 and not os.path.exists(paths['pack']),
          f"pack={paths['pack_code']}")

# ════════════════════════════════════════════════════════════════════
# E2E-04 Gate A FAIL后直接运行周报，GLM=0
# ─────────────────════════────────────────═══════════════════════════
# 真实入口: report_generator.generate_weekly_report(接E2E-03的FAIL态目录)
# 合成输入: E2E-03现场(FAIL快照在场,无当日包)
# mock范围: 付费GLM(计数断言用)与Gate B裁决值(不应被触达)
# 执行模块: verify_research_inputs真实预检→Gate A重算FAIL→预检拒绝
# 文件副作用: 无周报/无状态文件落盘
# 预期与断言: exit2+GLM恰0次(预检在GLM之前拦截)+无正式报告
# ════════════════════════════════════════════════════════════════════
print("\n── E2E-04 Gate A FAIL后直接运行周报，GLM=0")
with tempfile.TemporaryDirectory() as td:
    chain_build(td, DAY, gate='FAIL')
    ok, problems = run_verify(td)
    code, out, applied, glm = report_run(td, gate_b='PASS')
    check("E2E-04a 真实预检拒绝且原因点名Gate A",
          ok is False and any('Gate A' in p or 'FAIL' in p for p in problems),
          '; '.join(problems)[:80])
    check("E2E-04b 周报入口exit2+GLM恰0次+无任何正式报告/状态落盘",
          code == 2 and glm.calls == 0 and formal(out, DAY) is None
          and not os.path.exists(os.path.join(out, f'report_status_{DAY}.json')),
          f"exit={code} glm={glm.calls}")

# ════════════════════════════════════════════════════════════════════
# E2E-05 FAIL快照与旧数据包共存
# ─────────────────══────────────────────────────────────────══───────
# 真实入口: 真实装配链构造"FAIL日+无效残留包"→真实周报入口
# 合成输入: 当日FAIL快照+当日无效残留data_pack('#stale pack',模拟旧包未被
#   清理的现场)
# mock范围: 付费GLM(计数)
# 执行模块: verify_research_inputs(Gate A重算+包绑定核验,均真实)
# 文件副作用: 无(入口拒绝,残留包原样保留作诊断)
# 预期与断言: 预检False;周报exit2+GLM=0——不得凭旧包放行
# ════════════════════════════════════════════════════════════════════
print("\n── E2E-05 FAIL快照与旧数据包共存")
with tempfile.TemporaryDirectory() as td:
    snap, snap_path, p5 = fixt.build_full_day(td, DAY, gate='FAIL')  # 留'#stale pack'
    ok, problems = run_verify(td)
    code, out, applied, glm = report_run(td, gate_b='PASS')
    check("E2E-05 FAIL快照+旧残留包共存→预检拒+周报exit2+GLM=0(不凭旧包放行)",
          ok is False and code == 2 and glm.calls == 0
          and os.path.exists(p5['pack']),
          f"verify={ok} exit={code} glm={glm.calls}")

# ════════════════════════════════════════════════════════════════════
# E2E-06 昨日PASS、今日FAIL
# ────────────────────────────────────────────────────────────────────
# 真实入口: 昨日真实发布(PASS)→今日FAIL日真实周报入口
# 合成输入: PREV日全核心齐备+发布;DAY日核心SPX值坏
# mock范围: 付费GLM与Gate B裁决值;datetime指向各日
# 执行模块: 发布事务(昨日,真实)→今日预检Gate A重算FAIL(真实)
# 文件副作用: 昨日weekly_report_PREV.md+published状态;今日无新文件
# 预期与断言: 今日exit2+GLM=0;昨日报告字节未动且仍被真实formal_view认定
#   (唯一合格正式报告)
# ════════════════════════════════════════════════════════════════════
print("\n── E2E-06 昨日PASS、今日FAIL")
with tempfile.TemporaryDirectory() as td:
    fixt.build_full_day(td, PREV)
    code1, out, applied1, glm1 = report_run(td, gate_b='PASS', dt=DT_PREV)
    prev_md = os.path.join(out, f'weekly_report_{PREV}.md')
    assert code1 == 0, f'E2E-06昨日发布失败 code={code1}'
    bytes_before = open(prev_md, 'rb').read()
    fixt.build_full_day(td, DAY, gate='FAIL')
    code, out, applied, glm = report_run(td, gate_b='PASS', dt=DT_DAY)
    v_prev = formal(out, PREV)
    check("E2E-06a 今日FAIL→周报exit2+GLM=0(昨日合格报告不构成放行依据)",
          code == 2 and glm.calls == 0, f"exit={code} glm={glm.calls}")
    check("E2E-06b 昨日报告字节未动+仍被真实formal_view认定(唯一合格正式)",
          open(prev_md, 'rb').read() == bytes_before and v_prev is not None
          and formal(out, DAY) is None,
          f"prev_formal={v_prev is not None}")

# ════════════════════════════════════════════════════════════════════
# E2E-07 同日修订快照版本不匹配
# ────────────────────────────────────────────────────────────────────
# 真实入口: 真实装配链(base版)→写入真实构建的_v2修订快照→真实周报入口
# 合成输入: data_pack绑定base版快照;同日出现_v2修订版(fixt.real_snapshot
#   真实构建,内部snapshot_id同步_v2)
# mock范围: 付费GLM(计数)
# 执行模块: select_snapshot(取最高修订版_v2,真实)→包绑定核验(真实)
# 文件副作用: _v2快照落沙箱;无周报产出
# 预期与断言: 预检False且原因点名包与权威快照不绑定;exit2+GLM=0
# ════════════════════════════════════════════════════════════════════
print("\n── E2E-07 同日修订快照版本不匹配")
with tempfile.TemporaryDirectory() as td:
    snap, snap_path, p7 = fixt.build_full_day(td, DAY)
    snap_v2 = fixt.real_snapshot(DAY, rev=2)
    v2_path = os.path.join(p7['daily'], 'research_snapshot_20261024_v2.json')
    with open(v2_path, 'w', encoding='utf-8') as f:
        json.dump(snap_v2, f, ensure_ascii=False, indent=1)
    ok, problems = run_verify(td)
    code, out, applied, glm = report_run(td, gate_b='PASS')
    check("E2E-07 修订版_v2在场而包绑定base→预检拒(点名不绑定)+exit2+GLM=0",
          ok is False
          and any('不绑定' in p or '权威快照' in p for p in problems)
          and code == 2 and glm.calls == 0,
          f"verify={ok} exit={code} glm={glm.calls}; " + '; '.join(problems)[:60])

# ════════════════════════════════════════════════════════════════════
# E2E-08 数据包与锚点来源不一致
# ─────────────────════────────────────────────────────────────══───────
# 真实入口: 真实装配链→用**另一日真实构建的快照**重建锚点并同步meta摘要
#   →真实verify_anchor_batch+真实周报入口
# 合成输入: 当日包+当日权威快照;anchors_{DAY}.json内容实为PREV日事实构建
#   (meta摘要同步,排除摘要失配干扰,专测**来源不一致**)
# mock范围: 付费GLM(计数)
# 执行模块: verify_anchor_batch权威重建比对(真实)
# 文件副作用: 锚点文件被改写(沙箱);无周报产出
# 预期与断言: 批次核验False;预检False;exit2+GLM=0
# ════════════════════════════════════════════════════════════════════
print("\n── E2E-08 数据包与锚点来源不一致")
with tempfile.TemporaryDirectory() as td:
    snap, snap_path, p8 = fixt.build_full_day(td, DAY)
    snap_other = fixt.real_snapshot(PREV)
    anchors_other = sb.build_anchors(snap_other, DAY)
    with open(p8['anchors'], 'w', encoding='utf-8') as f:
        json.dump(anchors_other, f, ensure_ascii=False, indent=1)
    meta = rp.load_meta(p8['anchors'])
    rp.write_meta(p8['anchors'],
                  dict(meta, anchors_digest=rp.digest_file(p8['anchors'])))
    okb, whyb = rp.verify_anchor_batch(p8['anchors'], anchors_date=DAY,
                                       daily_dir=p8['daily'], trusted_root=td)
    ok, problems = run_verify(td)
    code, out, applied, glm = report_run(td, gate_b='PASS')
    check("E2E-08 锚点来源=另日快照(摘要已同步)→批次核验拒+预检拒+exit2+GLM=0",
          okb is False and ok is False and code == 2 and glm.calls == 0,
          f"batch={okb}:{whyb[:40]} exit={code}")

# ════════════════════════════════════════════════════════════════════
# E2E-09 Gate A DEGRADED、Gate B PASS,最终DEGRADED
# ────────────────────────────────────────────────────────────────────
# 真实入口: 同E2E-01全链(非核心UMCSENT值坏日)
# 合成输入: 非核心值坏(→Gate A=DEGRADED);Gate B裁决值'PASS'
# mock范围: 付费GLM与Gate B裁决值
# 执行模块: 合成分级(Gate A⊕Gate B,真实)→发布事务(真实)→formal_view(真实)
# 文件副作用: DEGRADED周报+published状态(final_quality='DEGRADED')
# 预期与断言: exit0;formal_view认定final_quality='DEGRADED';分级'DEGRADED'
#   回写1次(降级允许发布,不升格不阻断)
# ════════════════════════════════════════════════════════════════════
print("\n── E2E-09 Gate A DEGRADED、Gate B PASS,最终DEGRADED")
with tempfile.TemporaryDirectory() as td:
    chain_build(td, DAY, gate='DEGRADED')
    code, out, applied, glm = report_run(td, gate_b='PASS')
    v = formal(out, DAY)
    # 回写调度按既有契约(=test_gate_chain_p01§DEGRADED→回写继续): Gate B=PASS
    # 授权内容回写,调用恰1次;报告最终质量以状态final_quality='DEGRADED'披露
    check("E2E-09 GateA=DEGRADED+GateB=PASS→exit0+最终DEGRADED发布+回写不被阻断(恰1次)",
          code == 0 and v is not None and v['status']['final_quality'] == 'DEGRADED'
          and len(applied) == 1,
          f"exit={code} final={v and v['status']['final_quality']} applied={applied}")

# ════════════════════════════════════════════════════════════════════
# E2E-10 Gate A PASS、Gate B FAIL,禁止回写
# ─────────────────══────────────────────────────────────────═════════
# 真实入口: 同E2E-01全链(数据侧全PASS),Gate B裁决值'FAIL'
# 合成输入: 全核心齐备日;Gate B裁决'FAIL'
# mock范围: 付费GLM与Gate B裁决值('FAIL')
# 执行模块: 候选生成(真实)→Gate B(裁决值)→FAIL隔离路径+apply(真实,FAIL分支
#   自证零回写)
# 文件副作用: 候选隔离(_UNVALIDATED);主状态FAIL;thesis/views字节不变
# 预期与断言: exit3;GLM恰1次;applied=[](真实apply的FAIL分支);长期状态
#   字节前后一致;无formal认定
# ════════════════════════════════════════════════════════════════════
print("\n── E2E-10 Gate A PASS、Gate B FAIL,禁止回写")
with tempfile.TemporaryDirectory() as td:
    chain_build(td, DAY, gate='PASS')
    before = state_files(td)
    code, out, applied, glm = report_run(td, gate_b='FAIL')
    check("E2E-10a GateB=FAIL→exit3+GLM恰1次+分级回写调度零次(applied=[])",
          code == 3 and glm.calls == 1 and applied == [],
          f"exit={code} glm={glm.calls} applied={applied}")
    check("E2E-10b 长期状态(thesis/views)字节前后一致+无formal认定",
          state_files(td) == before and formal(out, DAY) is None
          and rp.scan_formal_weekly_reports(out) == [],
          "state_changed")

# ════════════════════════════════════════════════════════════════════
# E2E-11 关键步骤失败产生正确SKIPPED
# ─────────────────────────══───────────────────────────────────────────
# 真实入口: run_weekly.main(真实流水线编排;run_step=子进程启动器,外部进程
#   边界注入故障=文件系统/进程故障注入类mock)
# 合成输入: global_market_collector步骤失败(关键);其余步骤真实编排
# mock范围: run_step(子进程执行边界)——业务模块零mock;PROJECT_DIR/SCRIPTS_DIR
#   重定向沙箱
# 执行模块: run_weekly依赖图→下游装配/校验SKIPPED(不执行危险操作)→台账
#   (原子写,真实)
# 文件副作用: logs/pipeline_run_DAY.json台账落沙箱
# 预期与断言: 流水线exit1;台账中装配/校验步骤skipped=True且未执行;
#   allow_formal_report=False;链路终点周报入口exit2+GLM=0
# ════════════════════════════════════════════════════════════════════
print("\n── E2E-11 关键步骤失败产生正确SKIPPED")
with tempfile.TemporaryDirectory() as td:
    executed = []

    def fake_step(step_name, script_name, timeout=900, script_dir=None):
        executed.append(script_name)
        return script_name != 'global_market_collector.py'

    with mock.patch.object(run_weekly, 'PROJECT_DIR', td), \
         mock.patch.object(run_weekly, 'SCRIPTS_DIR', os.path.join(td, 'scripts')), \
         mock.patch.object(run_weekly, 'datetime', DT_DAY), \
         mock.patch.object(run_weekly, 'run_step', fake_step):
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                run_weekly.main()
            pcode = 0
        except SystemExit as e:
            pcode = e.code
    ledger = json.load(open(glob.glob(os.path.join(td, 'logs', 'pipeline_run_*.json'))[0],
                            encoding='utf-8'))
    steps = {s['name']: s for s in ledger['steps']}

    def _skipped(suffix):
        return any(n.endswith(suffix) and s['skipped'] for n, s in steps.items())
    check("E2E-11a 关键采集失败→流水线exit1+装配/校验SKIPPED(未执行)+allow=False",
          pcode == 1 and 'data_assembler.py' not in executed
          and 'data_validator.py' not in executed
          and _skipped('数据汇总打包') and _skipped('数据校验与锚点生成')
          and ledger.get('allow_formal_report') is False,
          f"exit={pcode} allow={ledger.get('allow_formal_report')}")
    code, out, applied, glm = report_run(td, gate_b='PASS')
    check("E2E-11b 链路终点: 采集失败日报告入口exit2+零GLM(不得凭旧产物放行)",
          code == 2 and glm.calls == 0, f"exit={code} glm={glm.calls}")

# ════════════════════════════════════════════════════════════════════
# E2E-12 有效、无效预测指标混合(FIX4-04按原始语义重建)
# ────────────────────────────────────────────────────────────────────
# 真实入口: 真实装配链(采集JSON内UMCSENT数值型区间外9999.9→事实引擎区间
#   校验FAIL→合法Gate A=DEGRADED;非人工篡改锚点/快照)→真实批次核验
#   verify_anchor_batch→真实观察器daily_prediction_observer.observe()
#   +真实状态引擎allocation_engine.record_observations
# 合成输入: 同一可追溯批次内≥2条有效状态预测——A观察中/目标=合法PASS指标
#   (SPX),B观察中/目标=本轮质量FAIL指标(UMCSENT区间外);另有终态预测
#   (hit)与未触发预测(前提合法未兑现+前提无效两种)
# mock范围: 零mock(纯前段+观察器,无GLM调用)
# 执行模块: fact_engine区间校验→snapshot_builder→verify_anchor_batch权威
#   重建比对→observe指标级质量门禁(rp.anchor_quality_problem同口径)
#   →record_observations真实写入长期观察历史(幂等)
# 文件副作用: 沙箱内快照/锚点+meta/数据包;views.json观察记录真实落盘
# 预期与断言: 批次核验通过(合法批次);A记入观察(值/观测日/来源),B因质量
#   FAIL跳过且不进长期历史,终态预测不重开,未触发前提不激活;重复运行
#   幂等(无新增观察/文件不变)
# ════════════════════════════════════════════════════════════════════
print("\n── E2E-12 有效、无效预测指标混合")
with tempfile.TemporaryDirectory() as td:
    def _umc_out_of_range(daily, ymd):
        # 合法链路内构造: 数值型超注册表区间[40,120]→事实引擎区间校验FAIL
        # (锚点仍带数值与quality=FAIL,区别于字符串'N/A'的完全无锚点)
        p = os.path.join(daily, f'macro_{ymd}.json')
        with open(p, encoding='utf-8') as f:
            obj = json.load(f)
        obj['data']['UMCSENT']['value'] = 9999.9
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False)
    paths, c = chain_build(td, DAY, post_collectors=_umc_out_of_range)
    snap = json.load(open(paths['snapshot'], encoding='utf-8'))
    anchors = json.load(open(paths['anchors'], encoding='utf-8'))
    check("E2E-12a 合法可追溯批次: Gate A=DEGRADED(UMCSENT区间外→非核心FAIL)"
          "+批次核验通过(锚点为快照确定性重建,非篡改)",
          c == 0 and snap['gate_a']['status'] == 'DEGRADED'
          and 'UMCSENT' in snap['gate_a'].get('noncore_fail', [])
          and anchors['macro.data.UMCSENT.value']['quality'] == 'FAIL'
          and anchors['global_market.data.SPX.close']['quality'] == 'PASS'
          and rp.verify_anchor_batch(paths['anchors'], anchors_date=DAY,
                                     daily_dir=paths['daily'], trusted_root=td)[0] is True,
          f"gate={snap['gate_a']['status']}")
    views_path = os.path.join(td, 'config', 'views.json')
    ensure_state_sandbox(td)
    preds = {'views': [], 'predictions': [
        # A: 观察中,目标=合法PASS指标(SPX)
        {'pred_id': 'P-A', 'status': 'observing',
         'metric': 'global_market.data.SPX.close', 'comparator': '>=',
         'target': 7000.0, 'observe_from': '2026-10-10',
         'deadline': '2026-12-31', 'observations': []},
        # B: 观察中,目标=本轮质量FAIL指标(UMCSENT区间外)
        {'pred_id': 'P-B', 'status': 'observing',
         'metric': 'macro.data.UMCSENT.value', 'comparator': '<=',
         'target': 80.0, 'observe_from': '2026-10-10',
         'deadline': '2026-12-31', 'observations': []},
        # C: 已终态预测(hit)——不得被每日观察重新开启/追记
        {'pred_id': 'P-C', 'status': 'hit',
         'metric': 'global_market.data.GOLD.close', 'comparator': '>=',
         'target': 4000.0,
         'observations': [{'obs_date': '2026-10-09', 'value': 4210.0}]},
        # D: 未触发预测,前提=合法PASS指标且未兑现(VIX 15.82<30)→保持未触发
        {'pred_id': 'P-D', 'status': 'not_yet_triggered',
         'premise': {'metric': 'global_market.data.VIX.close', 'op': '>=',
                     'target': 30.0},
         'metric': 'global_market.data.SPX.close', 'comparator': '<=',
         'target': 7000.0, 'deadline': '2026-12-31'},
        # E: 未触发预测,前提=本轮质量FAIL指标(UMCSENT)→无效前提不得激活
        {'pred_id': 'P-E', 'status': 'not_yet_triggered',
         'premise': {'metric': 'macro.data.UMCSENT.value', 'op': '<=',
                     'target': 80.0},
         'metric': 'macro.data.CPI.value', 'comparator': '>=',
         'target': 300.0, 'deadline': '2026-12-31'}]}
    with open(views_path, 'w', encoding='utf-8') as f:
        json.dump(preds, f, ensure_ascii=False)
    changes, nwatch, status = dpo.observe(
        views_path=views_path, anchors=anchors, today_str='2026-10-24',
        anchors_date=DAY, anchors_path=paths['anchors'], trusted_root=td)
    with open(views_path, encoding='utf-8') as f:
        after = json.load(f)
    got = {p['pred_id']: p for p in after['predictions']}
    obs_a = got['P-A'].get('observations') or []
    check("E2E-12b 批次内混合预测: A(合法PASS指标)记入观察(值/观测日/来源真实)",
          any('P-A' in ch for ch in changes)
          and len(obs_a) == 1 and obs_a[0]['value'] == 7659.44
          and obs_a[0]['obs_date'] == '2026-10-23'
          and obs_a[0]['source'] == 'research_snapshot_20261024.json',
          f"changes={changes}")
    check("E2E-12c B(质量FAIL指标)本轮跳过不进长期历史(观察列表保持空)",
          status == 'PARTIAL' and got['P-B'].get('observations') == []
          and not any('P-B' in ch for ch in changes),
          f"status={status} obsB={got['P-B'].get('observations')}")
    check("E2E-12d 终态预测不重开+无效前提不激活+合法未触发前提保持未触发",
          got['P-C']['status'] == 'hit'
          and len(got['P-C']['observations']) == 1
          and got['P-E']['status'] == 'not_yet_triggered'
          and 'premise_triggered_date' not in got['P-E']
          and got['P-D']['status'] == 'not_yet_triggered'
          and 'premise_triggered_date' not in got['P-D'],
          f"C={got['P-C']['status']} D={got['P-D']['status']} "
          f"E={got['P-E']['status']}")
    bytes_after = open(views_path, 'rb').read()
    changes2, _, status2 = dpo.observe(
        views_path=views_path, anchors=anchors, today_str='2026-10-24',
        anchors_date=DAY, anchors_path=paths['anchors'], trusted_root=td)
    check("E2E-12e 同批次重复运行幂等(零新增变更,长期状态文件字节不变)",
          changes2 == [] and open(views_path, 'rb').read() == bytes_after,
          f"changes2={len(changes2)}")

# E2E-12x(附加源对抗测试,FIX4-04保留自旧E2E-12实现——不再冒充E2E-12,
# 作为批次来源完整性的额外对抗用例): 锚点文件被剥离quality字段后即便
# 同步meta摘要,权威重建比对仍须整批拒绝。
with tempfile.TemporaryDirectory() as td:
    paths, c = chain_build(td, DAY)
    ok_clean, why_clean = rp.verify_anchor_batch(paths['anchors'], anchors_date=DAY,
                                                 daily_dir=paths['daily'], trusted_root=td)
    anchors = json.load(open(paths['anchors'], encoding='utf-8'))
    k0 = sorted(anchors)[0]
    anchors[k0].pop('quality', None)
    with open(paths['anchors'], 'w', encoding='utf-8') as f:
        json.dump(anchors, f, ensure_ascii=False, indent=1)
    meta = rp.load_meta(paths['anchors'])
    rp.write_meta(paths['anchors'],
                  dict(meta, anchors_digest=rp.digest_file(paths['anchors'])))
    okb, whyb = rp.verify_anchor_batch(paths['anchors'], anchors_date=DAY,
                                       daily_dir=paths['daily'], trusted_root=td)
    ok, problems = run_verify(td)
    code, out, applied, glm = report_run(td, gate_b='PASS')
    check("E2E-12x [附加]锚点篡改(剥离quality+同步摘要)→批次整体拒+对照批次通过"
          "+预检拒+入口exit2+GLM=0",
          ok_clean and okb is False and ok is False and code == 2 and glm.calls == 0,
          f"clean={ok_clean} mixed={okb}:{whyb[:40]} exit={code}")

# ════════════════════════════════════════════════════════════════════
# E2E-13 旧锚点残留指标
# ─────────────────────────══───────────────────────────────────────────
# 真实入口: 真实装配链→锚点文件混入旧残留键(上周指标)+同步meta摘要→真实
#   批次核验+真实周报入口
# 合成输入: STALE_OLD_METRIC_20261017(当日快照已剔除的旧指标)
# mock范围: 付费GLM(计数)
# 执行模块: verify_anchor_batch权威重建比对(真实)
# 文件副作用: 锚点被改写(沙箱);无周报产出
# 预期与断言: 批次False且原因可定位残留键;预检False;exit2+GLM=0
# ════════════════════════════════════════════════════════════════════
print("\n── E2E-13 旧锚点残留指标")
with tempfile.TemporaryDirectory() as td:
    paths, c = chain_build(td, DAY)
    anchors = json.load(open(paths['anchors'], encoding='utf-8'))
    stale_key = 'STALE_OLD_METRIC_20261017'
    anchors[stale_key] = dict(anchors[sorted(anchors)[0]])
    anchors[stale_key]['value'] = 1.23
    with open(paths['anchors'], 'w', encoding='utf-8') as f:
        json.dump(anchors, f, ensure_ascii=False, indent=1)
    meta = rp.load_meta(paths['anchors'])
    rp.write_meta(paths['anchors'],
                  dict(meta, anchors_digest=rp.digest_file(paths['anchors'])))
    okb, whyb = rp.verify_anchor_batch(paths['anchors'], anchors_date=DAY,
                                       daily_dir=paths['daily'], trusted_root=td)
    ok, problems = run_verify(td)
    code, out, applied, glm = report_run(td, gate_b='PASS')
    check("E2E-13 旧锚点残留→批次拒(点名残留键)+预检拒+exit2+GLM=0",
          okb is False and stale_key in whyb and ok is False
          and code == 2 and glm.calls == 0,
          f"batch={okb}:{whyb[:40]} exit={code}")

# ════════════════════════════════════════════════════════════════════
# E2E-14 已有合格报告，后续输入质量失败
# ─────────────────════───────────────────────────────────────────────
# 真实入口: 昨日真实发布(PASS)→今日核心失败日(SPX值坏+旧残留包)真实周报入口;
#   事后再以真实load_previous_report(次日视角)回读
# 合成输入: PREV日合格发布;DAY日核心值坏
# mock范围: 付费GLM与Gate B裁决值;datetime指向各日
# 执行模块: 预检Gate A重算(真实)→拒绝;正式读取器formal_view/
#   load_previous_report(真实,回读昨日)
# 文件副作用: 今日无新报告;昨日报告/状态字节不动
# 预期与断言: 今日exit2+GLM=0;昨日仍为唯一formal;真实load_previous_report
#   取昨日合格报告(无'未验证档案'标注)
# ════════════════════════════════════════════════════════════════════
print("\n── E2E-14 已有合格报告，后续输入质量失败")
with tempfile.TemporaryDirectory() as td:
    fixt.build_full_day(td, PREV)
    code1, out, applied1, glm1 = report_run(td, gate_b='PASS', dt=DT_PREV)
    assert code1 == 0, f'E2E-14昨日发布失败 code={code1}'
    prev_md = os.path.join(out, f'weekly_report_{PREV}.md')
    bytes_before = open(prev_md, 'rb').read()
    fixt.build_full_day(td, DAY, gate='FAIL')
    code, out, applied, glm = report_run(td, gate_b='PASS', dt=DT_DAY)
    with mock.patch.object(rg, 'OUTPUT_DIR', out), \
         mock.patch.object(rg, 'datetime', DT_NEXT):
        prev_text = quiet(rg.load_previous_report)
    check("E2E-14a 后续输入质量失败→exit2+GLM=0+昨日报告字节未动仍唯一formal",
          code == 2 and glm.calls == 0
          and open(prev_md, 'rb').read() == bytes_before
          and formal(out, PREV) is not None and formal(out, DAY) is None,
          f"exit={code} glm={glm.calls}")
    check("E2E-14b 真实load_previous_report回读昨日合格报告(无未验证标注)",
          'SYNTHETIC E2E冻结表' in prev_text and '未验证' not in prev_text,
          prev_text[:50])

# ═══ 汇总 ═══════════════════════════════════════════════════════════
print("\n" + "=" * 64)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 64)
print("复核状态: 本结果=开发者离线E2E通过与否; '独立Agent已复核'由Agent4")
print("另行判定(本套件不得自declare P0-1 PASS)。")
sys.exit(1 if FAIL else 0)
