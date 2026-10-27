#!/usr/bin/env python3
"""IA-P0-1 E2E-01~14 原版场景端到端复测(FIX2轮,2026-10-27)

按验收指令留存的**14个强制对抗场景原文**逐条做**全链路**复测——每条都从
真实链路起点走到终点,而不是孤立单元探针:
  采集JSON(fixture合成) → snapshot_builder CLI(真实子进程) → macro_scorecard
  (真实main) → data_assembler(真实main,含Gate拒绝语义) → 锚点/prompt(真实
  确定性构建) → report_generator.generate_weekly_report(真实入口,GLM mock)
  → Gate B → 发布事务/状态 → 长期状态保护(thesis/views沙箱字节比对)。

编号说明(诚实声明,与docs/P0_GATE_A_REPAIR_01.md §7一致): 原始E2E-01~14的
逐条编号文本未留存于本仓库,本套件按指令中**文字定义完整**的14个强制场景组织,
每场景对应链路一条;不自行发明第15类,不删减场景。

数据纪律: 全部SYNTHETIC fixture+临时目录;GLM全程mock零付费;不触真实
data/config/output/logs。
运行: ~/AI内容/venv/bin/python3 tests/test_e2e_orig14.py
"""
import os
import sys
import io
import json
import copy
import glob
import shutil
import tempfile
import contextlib
import subprocess
import unittest.mock as mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable

PASS, FAIL = 0, 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")


def quiet(fn, *a, **kw):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r = fn(*a, **kw)
    return r


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
import fixt                               # noqa: E402

DAY = '20261024'


class _FakeDT:
    @staticmethod
    def now():
        import datetime as _dt
        return _dt.datetime(2026, 10, 24, 8, 0, 0)

    @staticmethod
    def strptime(s, f):
        import datetime as _dt
        return _dt.datetime.strptime(s, f)


class _GLM:
    def __init__(self, text=None):
        self.text = text or ('# 投资周报(SYNTHETIC E2E)\n\n' + '本周综述与分资产回顾。' * 60)
        self.calls = 0

    def __call__(self, system_prompt, user_prompt, max_tokens=32000, timeout=900):
        self.calls += 1
        return self.text


print("=" * 64)
print("IA-P0-1 E2E-01~14 原版场景全链路复测(FIX2轮)")
print("=" * 64)


def chain_build(td, ymd=DAY, gate='PASS', break_metric=None, missing=(),
                with_pack=True):
    """全链路前段(真实阶段函数/CLI):
    采集JSON → snapshot_builder CLI → macro_scorecard.main → data_assembler.main
    (Gate FAIL→SystemExit 2,不产正式包) → 锚点prompt。返回(paths dict, sb_exit)。"""
    daily = os.path.join(td, 'data', 'daily')
    weekly = os.path.join(td, 'data', 'weekly')
    os.makedirs(daily, exist_ok=True)
    os.makedirs(weekly, exist_ok=True)
    if break_metric is None:
        break_metric = {'DEGRADED': 'UMCSENT', 'FAIL': 'SPX'}.get(gate)
    fixt.write_collectors(daily, ymd, break_metric=break_metric, missing=missing)
    code, out = cli([os.path.join(ROOT, 'scripts', 'snapshot_builder.py'),
                     '--date', ymd, '--data-dir', daily, '--out-dir', daily])
    snap_file = os.path.join(daily, f'research_snapshot_{ymd}.json')
    if not os.path.exists(snap_file):
        return {'sb_exit': code, 'sb_out': out, 'daily': daily, 'weekly': weekly}, code
    # Gate A FAIL日sb CLI仍落盘快照(exit≠0属合法记录)——链路继续,由装配器/入口裁决
    try:
        quiet(ms.main, date_str=ymd, data_dir=daily)
    except Exception:
        pass   # 评分卡失败不阻断链路构造(其授权语义由fix2套件单独覆盖)
    pack_code = None
    if with_pack:
        try:
            with mock.patch.object(da, 'DATA_DIR', os.path.join(td, 'data')), \
                 mock.patch.object(da, 'datetime', _FakeDT):
                quiet(da.main)
            pack_code = 0
        except SystemExit as e:
            pack_code = e.code
    with open(os.path.join(daily, f'anchors_{ymd}.json'), encoding='utf-8') as f:
        anchors = json.load(f)
    with open(os.path.join(daily, f'anchor_prompt_{ymd}.md'), 'w', encoding='utf-8') as f:
        f.write(dv.generate_anchor_prompt_block(anchors))
    ensure_state_sandbox(td)
    return {'sb_exit': 0, 'daily': daily, 'weekly': weekly,
            'pack_code': pack_code,
            'snapshot': os.path.join(daily, f'research_snapshot_{ymd}.json'),
            'anchors': os.path.join(daily, f'anchors_{ymd}.json'),
            'meta': rp.meta_path_for(os.path.join(daily, f'anchors_{ymd}.json')),
            'pack': os.path.join(weekly, f'data_pack_{ymd}.md'),
            'pack_meta': rp.meta_path_for(os.path.join(weekly, f'data_pack_{ymd}.md')),
            'prompt': os.path.join(daily, f'anchor_prompt_{ymd}.md')}, 0


def report_run(td, gate_b='PASS', validator_exc=None, status_false=False,
               glm_text=None):
    """链路后段: 真实报告入口(GLM mock,长期状态回写重定向沙箱)。
    返回(exit_code, out_dir, applied, glm)。applied=真实apply收到的分级列表。"""
    out_dir = os.path.join(td, 'output', 'weekly')
    glm = _GLM(glm_text)
    cfg = os.path.join(td, 'config')
    os.makedirs(cfg, exist_ok=True)
    thesis = os.path.join(cfg, 'thesis.json')
    views = os.path.join(cfg, 'views.json')
    if not os.path.exists(thesis):
        with open(thesis, 'w', encoding='utf-8') as f:
            json.dump({'theses': []}, f, ensure_ascii=False)
    if not os.path.exists(views):
        with open(views, 'w', encoding='utf-8') as f:
            json.dump({'views': [], 'predictions': []}, f, ensure_ascii=False)
    applied = []
    real_apply = rg.apply_status_updates

    def _apply(report, classification, anchors=None, today_str=None,
               thesis_path=None, views_path=None):
        applied.append(classification)
        return real_apply(report, classification, anchors=anchors,
                          today_str=today_str, thesis_path=thesis,
                          views_path=views)

    def _validate(md_path, anchors=None, anchors_file=None):
        if validator_exc:
            raise validator_exc
        return (gate_b, ['SYNTHETIC E2E警告'])

    patches = [
        mock.patch.object(rg, 'DATA_DIR', os.path.join(td, 'data')),
        mock.patch.object(rg, 'OUTPUT_DIR', out_dir),
        mock.patch.object(rg, 'datetime', _FakeDT),
        mock.patch.object(rg, '_call_glm', glm),
        mock.patch.object(rg, 'apply_status_updates', _apply),
        mock.patch.object(rg, 'validate_generated_report', _validate),
        mock.patch.object(rg.allocation_engine, 'load_views',
                          lambda *a, **kw: {'views': [], 'predictions': []}),
        mock.patch.object(rg, 'pending_completed_month', lambda d=None: None),
        mock.patch.object(rg, 'pending_completed_quarter', lambda d=None: None),
        mock.patch.object(rg, 'load_framework', lambda: '框架'),
        mock.patch.object(rg, 'load_theses', lambda: '论点'),
        mock.patch.object(rg, 'load_technical_notes', lambda: ''),
        mock.patch.object(rg, 'load_news_summary', lambda: ''),
        mock.patch.object(rg, 'load_previous_report', lambda: ''),
    ]
    if status_false:
        patches.append(mock.patch.object(rg, 'write_report_status',
                                         lambda *a, **kw: False))
    with contextlib.ExitStack() as stack:
        for p in patches:
            stack.enter_context(p)
        try:
            quiet(rg.generate_weekly_report)
            code = 0
        except SystemExit as e:
            code = e.code
    return code, out_dir, applied, glm


def formal_view(out_dir, ymd=DAY):
    sp = os.path.join(out_dir, f'report_status_{ymd}.json')
    if not os.path.exists(sp):
        return None
    st = json.load(open(sp, encoding='utf-8'))
    path = st.get('report_path')
    if not st.get('published') or not path or not os.path.exists(path) \
            or str(path).endswith('_UNVALIDATED.md'):
        return None
    if st.get('report_digest') != rp.digest_file(path):
        return None
    return st


def state_files(td):
    cfg = os.path.join(td, 'config')
    return {f: open(os.path.join(cfg, f), 'rb').read()
            for f in ('thesis.json', 'views.json')
            if os.path.exists(os.path.join(cfg, f))}


def ensure_state_sandbox(td):
    """长期状态沙箱提前物化(report_run也会注入,但前后字节比对须先有基线)。"""
    cfg = os.path.join(td, 'config')
    os.makedirs(cfg, exist_ok=True)
    for name, obj in (('thesis.json', {'theses': []}),
                      ('views.json', {'views': [], 'predictions': []})):
        p = os.path.join(cfg, name)
        if not os.path.exists(p):
            with open(p, 'w', encoding='utf-8') as f:
                json.dump(obj, f, ensure_ascii=False)


# ── E2E 场景1: 数据包数字改变 ────────────────────────────────────────
print("\n── E2E场景1: 数据包数字改变(全链: 预检拒绝,零GLM,长期状态不动)")
with tempfile.TemporaryDirectory() as td:
    paths, c = chain_build(td)
    before = state_files(td)
    with open(paths['pack'], encoding='utf-8') as f:
        pack = f.read()
    with open(paths['pack'], 'w', encoding='utf-8') as f:
        f.write(pack.replace('7,659.44', '9,999.99', 1))
    code, out, applied, glm = report_run(td)
    check("S1a 改包数字(meta未动)→入口exit 2+零GLM+无候选/正式文件+状态文件字节不动",
          code == 2 and glm.calls == 0 and applied == []
          and not glob.glob(os.path.join(out, 'weekly_report_*'))
          and state_files(td) == before, f"exit={code} glm={glm.calls}")
with tempfile.TemporaryDirectory() as td:
    paths, c = chain_build(td)
    before = state_files(td)
    with open(paths['pack'], encoding='utf-8') as f:
        pack = f.read()
    tampered = pack.replace('7,659.44', '9,999.99', 1)
    with open(paths['pack'], 'w', encoding='utf-8') as f:
        f.write(tampered)
    meta = rp.load_meta(paths['pack'])
    rp.write_meta(paths['pack'], dict(meta, pack_digest=rp.digest_file(paths['pack'])))
    code, out, applied, glm = report_run(td)
    check("S1b 改包数字+同步改meta摘要→权威快照重建比对仍拒(exit 2,零GLM)",
          code == 2 and glm.calls == 0 and state_files(td) == before,
          f"exit={code} glm={glm.calls}")

# ── E2E 场景2: 锚点数字改变 ────────────────────────────────────────
print("\n── E2E场景2: 锚点数字改变")
with tempfile.TemporaryDirectory() as td:
    paths, c = chain_build(td)
    before = state_files(td)
    anchors = json.load(open(paths['anchors'], encoding='utf-8'))
    k0 = sorted(anchors)[0]
    anchors[k0]['value'] = (anchors[k0].get('value') or 0) + 123.456
    with open(paths['anchors'], 'w', encoding='utf-8') as f:
        json.dump(anchors, f, ensure_ascii=False, indent=1)
    code, out, applied, glm = report_run(td)
    check("S2a 改锚点数字(meta未动)→exit 2+零GLM+长期状态不动",
          code == 2 and glm.calls == 0 and state_files(td) == before,
          f"exit={code} glm={glm.calls}")
with tempfile.TemporaryDirectory() as td:
    paths, c = chain_build(td)
    anchors = json.load(open(paths['anchors'], encoding='utf-8'))
    k0 = sorted(anchors)[0]
    anchors[k0]['value'] = (anchors[k0].get('value') or 0) + 123.456
    with open(paths['anchors'], 'w', encoding='utf-8') as f:
        json.dump(anchors, f, ensure_ascii=False, indent=1)
    meta = rp.load_meta(paths['anchors'])
    rp.write_meta(paths['anchors'], dict(meta, anchors_digest=rp.digest_file(paths['anchors'])))
    code, out, applied, glm = report_run(td)
    check("S2b 改锚点+同步改meta摘要→确定性重建比对拒(exit 2)",
          code == 2 and glm.calls == 0, f"exit={code}")

# ── E2E 场景3: Prompt内容替换 ──────────────────────────────────────
print("\n── E2E场景3: 锚点prompt内容替换")
with tempfile.TemporaryDirectory() as td:
    paths, c = chain_build(td)
    text = open(paths['prompt'], encoding='utf-8').read()
    import re as _re
    nums = _re.findall(r'\d+\.\d+', text)
    if len(nums) >= 2:
        text = text.replace(nums[0], '0.01', 1)
    with open(paths['prompt'], 'w', encoding='utf-8') as f:
        f.write(text)
    code, out, applied, glm = report_run(td)
    check("S3a prompt数字被替换→重建比对拒(exit 2,零GLM)",
          code == 2 and glm.calls == 0, f"exit={code}")
with tempfile.TemporaryDirectory() as td:
    paths, c = chain_build(td)
    with open(paths['prompt'], 'a', encoding='utf-8') as f:
        f.write('\n- AAA_TEST_FAKE | 123.45 | 2026-10-23\n')
    code, out, applied, glm = report_run(td)
    check("S3b prompt追加伪造指标行→重建比对拒(exit 2)", code == 2 and glm.calls == 0,
          f"exit={code}")

# ── E2E 场景4: 锚点摘要被修改 ──────────────────────────────────────
print("\n── E2E场景4: 锚点meta摘要被修改")
for field in ('anchors_digest', 'snapshot_digest'):
    with tempfile.TemporaryDirectory() as td:
        paths, c = chain_build(td)
        meta = rp.load_meta(paths['anchors'])
        rp.write_meta(paths['anchors'], dict(meta, **{field: 'deadbeefdeadbeef'}))
        code, out, applied, glm = report_run(td)
        check(f"S4 meta.{field}改死值→exit 2+零GLM", code == 2 and glm.calls == 0,
              f"exit={code}")

# ── E2E 场景5: 锚点残留旧指标 ──────────────────────────────────────
print("\n── E2E场景5: 锚点残留旧指标")
with tempfile.TemporaryDirectory() as td:
    paths, c = chain_build(td)
    before = state_files(td)
    anchors = json.load(open(paths['anchors'], encoding='utf-8'))
    stale_key = 'STALE_OLD_METRIC_20261017'
    anchors[stale_key] = dict(anchors[sorted(anchors)[0]])
    anchors[stale_key]['value'] = 1.23
    with open(paths['anchors'], 'w', encoding='utf-8') as f:
        json.dump(anchors, f, ensure_ascii=False, indent=1)
    meta = rp.load_meta(paths['anchors'])
    rp.write_meta(paths['anchors'],
                  dict(meta, anchors_digest=rp.digest_file(paths['anchors'])))
    code, out, applied, glm = report_run(td)
    # 入口拒绝(重建比对/残留点名);锚点批质量核验在预检内完成
    check("S5 锚点文件残留旧指标键(+meta同步)→exit 2+零GLM+长期状态不动",
          code == 2 and glm.calls == 0 and state_files(td) == before,
          f"exit={code}")
    ok, reason = rp.verify_anchor_batch(paths['anchors'], anchors_date=DAY,
                                        daily_dir=paths['daily'])
    check("S5 批次核验拒绝且原因可定位残留", ok is False and stale_key in reason,
          reason)

# ── E2E 场景6: 快照文件名与内部身份冲突 ────────────────────────────
print("\n── E2E场景6: 快照文件名与内部身份冲突")
with tempfile.TemporaryDirectory() as td:
    paths, c = chain_build(td)
    daily = paths['daily']
    # 6a 同日重建base→CLI exit 3(不可变)
    c6a, _o = cli([os.path.join(ROOT, 'scripts', 'snapshot_builder.py'),
                   '--date', DAY, '--data-dir', daily, '--out-dir', daily])
    check("S6a 同日重建base→snapshot_builder CLI exit 3", c6a == 3, f"exit={c6a}")
    # 6b 合法修订链v2→v3
    c62, _o = cli([os.path.join(ROOT, 'scripts', 'snapshot_builder.py'),
                   '--date', DAY, '--data-dir', daily, '--out-dir', daily,
                   '--allow-revision', '--revision-reason', 'E2E修订v2'])
    c63, _o = cli([os.path.join(ROOT, 'scripts', 'snapshot_builder.py'),
                   '--date', DAY, '--data-dir', daily, '--out-dir', daily,
                   '--allow-revision', '--revision-reason', 'E2E修订v3'])
    snap, why = rp.select_snapshot(DAY, daily)
    check("S6b --allow-revision×2→v2+v3在场,选择器确定性取_v3",
          c62 == 0 and c63 == 0 and snap is not None
          and snap['snapshot_id'] == f'research_snapshot_{DAY}_v3', str(why))
    # 修订后旧包/旧锚点绑base→入口拒绝(批次失配,不得拿旧包冒充)
    code, out, applied, glm = report_run(td)
    check("S6c 修订_v3后旧包仍绑base→报告入口exit 2(零GLM)",
          code == 2 and glm.calls == 0, f"exit={code}")
with tempfile.TemporaryDirectory() as td:
    paths, c = chain_build(td)
    daily = paths['daily']
    base = json.load(open(os.path.join(daily, f'research_snapshot_{DAY}.json'),
                          encoding='utf-8'))
    # 6d 身份冲突: 文件名_v2,内部自称base→整日拒绝
    with open(os.path.join(daily, f'research_snapshot_{DAY}_v2.json'), 'w',
              encoding='utf-8') as f:
        json.dump(base, f, ensure_ascii=False)
    snap, why = rp.select_snapshot(DAY, daily)
    check("S6d 文件名_v2但内部自称base→整日拒绝", snap is None and 'snapshot_id' in why,
          why)
    code, out, applied, glm = report_run(td)
    check("S6d(链) 身份冲突日→报告入口exit 2", code == 2 and glm.calls == 0,
          f"exit={code}")

# ── E2E 场景7: Gate A声明与实际事实冲突 ────────────────────────────
print("\n── E2E场景7: Gate A声明与实际事实冲突")
for gate, declare, label in (('DEGRADED', 'PASS', '非核心FAIL日谎报PASS'),
                             ('FAIL', 'DEGRADED', '核心FAIL日谎报DEGRADED')):
    with tempfile.TemporaryDirectory() as td:
        paths, c = chain_build(td, gate=gate)
        snap_path = paths['snapshot']
        snap = json.load(open(snap_path, encoding='utf-8'))
        snap['gate_a']['status'] = declare
        with open(snap_path, 'w', encoding='utf-8') as f:
            json.dump(snap, f, ensure_ascii=False, indent=1)
        before = state_files(td)
        code, out, applied, glm = report_run(td)
        check(f"S7 {label}→入口exit 2+零GLM+长期状态不动",
              code == 2 and glm.calls == 0 and state_files(td) == before,
              f"exit={code}")
with tempfile.TemporaryDirectory() as td:
    paths, c = chain_build(td, gate='FAIL')
    snap_path = paths['snapshot']
    snap = json.load(open(snap_path, encoding='utf-8'))
    snap['gate_a']['core_fail'] = []   # 隐瞒核心失败清单
    with open(snap_path, 'w', encoding='utf-8') as f:
        json.dump(snap, f, ensure_ascii=False, indent=1)
    got, why = rp.gate_status(snap)
    check("S7 核心失败清单隐瞒→gate_status拒绝", got is None and 'core_fail' in why, why)

# ── E2E 场景8: 非核心单指标失败(真实注册表分级) ────────────────────
print("\n── E2E场景8: 非核心单指标失败→DEGRADED继续;核心失败→阻断")
with tempfile.TemporaryDirectory() as td:
    paths, c = chain_build(td, gate='DEGRADED')
    before = state_files(td)
    check("S8a 非核心(UMCSENT)坏→装配器exit 0(真实da.main)",
          paths['pack_code'] == 0, f"pack_code={paths['pack_code']}")
    pack = open(paths['pack'], encoding='utf-8').read()
    check("S8a 数据包含降级披露", '数据质量降级披露' in pack and 'UMCSENT' in pack.upper()
          or '密歇根' in pack, '')
    code, out, applied, glm = report_run(td, gate_b='PASS')
    rep = os.path.join(out, f'weekly_report_{DAY}.md')
    st = formal_view(out)
    rep_text = open(rep, encoding='utf-8').read()
    check("S8a 链路终点: 合法DEGRADED日发布成功(exit 0,GLM 1,final=DEGRADED,"
          "可见降级页脚,真实apply收到Gate B=PASS)",
          code == 0 and glm.calls == 1 and st is not None
          and st['final_quality'] == 'DEGRADED' and st['gate_a'] == 'DEGRADED'
          and '数据质量降级披露' in rep_text and applied == ['PASS'],
          f"exit={code} applied={applied} fq={st and st.get('final_quality')}")
with tempfile.TemporaryDirectory() as td:
    paths, c = chain_build(td, gate='FAIL')
    check("S8b 核心(SPX)坏→装配器拒绝(真实da.main exit 2,完全不产正式包)",
          paths['pack_code'] == 2 and not os.path.exists(paths['pack']),
          f"pack_code={paths['pack_code']} exists={os.path.exists(paths['pack'])}")
    code, out, applied, glm = report_run(td, gate_b='PASS')
    check("S8b 链路终点: 核心失败日报告入口exit 2+零GLM+无任何报告文件",
          code == 2 and glm.calls == 0
          and not glob.glob(os.path.join(out, 'weekly_report_*')),
          f"exit={code} glm={glm.calls}")

# ── E2E 场景9: 关键采集失败后下游依赖 ──────────────────────────────
print("\n── E2E场景9: 关键采集失败→下游SKIPPED;链路终点报告拒绝")
with tempfile.TemporaryDirectory() as td:
    executed = []

    def fake_step(step_name, script_name, timeout=900, script_dir=None):
        executed.append(script_name)
        return script_name != 'global_market_collector.py'

    with mock.patch.object(run_weekly, 'PROJECT_DIR', td), \
         mock.patch.object(run_weekly, 'SCRIPTS_DIR', os.path.join(td, 'scripts')), \
         mock.patch.object(run_weekly, 'datetime', _FakeDT), \
         mock.patch.object(run_weekly, 'run_step', fake_step):
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                run_weekly.main()
            pcode = 0
        except SystemExit as e:
            pcode = e.code
    ledger = json.load(open(glob.glob(os.path.join(td, 'logs', 'pipeline_run_*.json'))[0],
                            encoding='utf-8'))
    check("S9a 关键采集(global)失败→流水线exit 1+装配/校验未执行+allow=False",
          pcode == 1 and 'data_assembler.py' not in executed
          and 'data_validator.py' not in executed
          and ledger.get('allow_formal_report') is False, f"exit={pcode}")
    code, out, applied, glm = report_run(td)
    check("S9a 链路终点: 采集失败日报告入口exit 2+零GLM(不得凭旧产物放行)",
          code == 2 and glm.calls == 0, f"exit={code} glm={glm.calls}")
with tempfile.TemporaryDirectory() as td:
    def fake_step2(step_name, script_name, timeout=900, script_dir=None):
        return script_name != 'news_collector.py'
    with mock.patch.object(run_weekly, 'PROJECT_DIR', td), \
         mock.patch.object(run_weekly, 'SCRIPTS_DIR', os.path.join(td, 'scripts')), \
         mock.patch.object(run_weekly, 'datetime', _FakeDT), \
         mock.patch.object(run_weekly, 'run_step', fake_step2):
        snap = quiet(fixt.real_snapshot, DAY)
        dd = os.path.join(td, 'data', 'daily')
        os.makedirs(dd, exist_ok=True)
        with open(os.path.join(dd, snap['snapshot_id'] + '.json'), 'w',
                  encoding='utf-8') as f:
            json.dump(snap, f, ensure_ascii=False)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                run_weekly.main()
            pcode = 0
        except SystemExit as e:
            pcode = e.code
    ledger = json.load(open(glob.glob(os.path.join(td, 'logs', 'pipeline_run_*.json'))[0],
                            encoding='utf-8'))
    check("S9b 新闻失败(非关键)→exit 0+allow=True(降级不阻止观察)",
          pcode == 0 and ledger.get('allow_formal_report') is True, f"exit={pcode}")

# ── E2E 场景10: 缺少质量字段的预测观察锚点 ─────────────────────────
print("\n── E2E场景10: 缺质量字段的锚点→批次拒绝")
with tempfile.TemporaryDirectory() as td:
    paths, c = chain_build(td)
    anchors = json.load(open(paths['anchors'], encoding='utf-8'))
    k0 = sorted(anchors)[0]
    anchors[k0].pop('quality', None)   # 剥离质量字段(旧schema/伪造锚点特征)
    with open(paths['anchors'], 'w', encoding='utf-8') as f:
        json.dump(anchors, f, ensure_ascii=False, indent=1)
    meta = rp.load_meta(paths['anchors'])
    rp.write_meta(paths['anchors'],
                  dict(meta, anchors_digest=rp.digest_file(paths['anchors'])))
    ok, reason = rp.verify_anchor_batch(paths['anchors'], anchors_date=DAY,
                                        daily_dir=paths['daily'])
    check("S10 锚点缺quality字段→批次核验拒绝(与权威重建不一致,质量不可证明)",
          ok is False and ('不一致' in reason or 'quality' in reason.lower()
                           or '质量' in reason), reason)
    code, out, applied, glm = report_run(td)
    check("S10(链) 报告入口exit 2+零GLM", code == 2 and glm.calls == 0, f"exit={code}")

# ── E2E 场景11: 既有正式报告被新失败报告尝试覆盖 ────────────────────
print("\n── E2E场景11: 已发布合格报告vs新失败报告")
with tempfile.TemporaryDirectory() as td:
    paths, c = chain_build(td)
    code1, out, applied1, glm1 = report_run(td, gate_b='PASS',
                                            glm_text='# 周报V1\n\n' + '正文一。' * 200)
    rep = os.path.join(out, f'weekly_report_{DAY}.md')
    v1 = open(rep, 'rb').read()
    st1 = open(os.path.join(out, f'report_status_{DAY}.json'), 'rb').read()
    after_pub = state_files(td)
    code2, out, applied2, glm2 = report_run(td, gate_b='FAIL',
                                            glm_text='# 周报V2坏数据\n\n' + '错误数字6.66,结论无效。' * 200)
    st = json.load(open(os.path.join(out, f'report_status_{DAY}.json')))
    usp = os.path.join(out, f'report_status_{DAY}_UNVALIDATED.json')
    ust = json.load(open(usp)) if os.path.exists(usp) else None
    check("S11 新失败报告尝试: exit 3+正式报告字节不变+主状态字节不变(仍published)",
          code2 == 3 and open(rep, 'rb').read() == v1
          and open(os.path.join(out, f'report_status_{DAY}.json'), 'rb').read() == st1
          and st['published'] is True and st['final_quality'] in ('PASS', 'DEGRADED'),
          f"exit={code2}")
    check("S11 失败详情入UNVALIDATED侧车(published=False,指向真实隔离文件)",
          ust is not None and ust.get('published') is False
          and str(ust.get('report_path')).endswith('_UNVALIDATED.md'),
          str(ust and ust.get('report_path')))
    check("S11 长期状态保护: 失败轮零回写(thesis/views字节与发布后一致,apply未收到PASS)",
          state_files(td) == after_pub and applied2 == [],
          f"applied2={applied2}")
    check("S11 正式入口仍认定旧合格报告", formal_view(out) is not None)

# ── E2E 场景12: Gate B校验异常 ─────────────────────────────────────
print("\n── E2E场景12: Gate B校验器异常")
with tempfile.TemporaryDirectory() as td:
    paths, c = chain_build(td)
    before = state_files(td)
    code, out, applied, glm = report_run(td,
                                         validator_exc=RuntimeError('GateB崩溃(SYNTHETIC)'))
    check("S12 校验器异常→exit 3+候选隔离_UNVALIDATED+无正式文件+GLM恰好1次",
          code == 3 and os.path.exists(os.path.join(out, f'weekly_report_{DAY}_UNVALIDATED.md'))
          and not os.path.exists(os.path.join(out, f'weekly_report_{DAY}.md'))
          and glm.calls == 1, f"exit={code} glm={glm.calls}")
    check("S12 长期状态保护: 异常轮零回写", applied == [] and state_files(td) == before)

# ── E2E 场景13: 报告状态写入异常 ───────────────────────────────────
print("\n── E2E场景13: 报告状态写入异常")
with tempfile.TemporaryDirectory() as td:
    paths, c = chain_build(td)
    before = state_files(td)
    code, out, applied, glm = report_run(td, status_false=True)
    check("S13a 首发布状态写失败→exit 3+不发布正式名+新报告隔离+零回写",
          code == 3 and not os.path.exists(os.path.join(out, f'weekly_report_{DAY}.md'))
          and os.path.exists(os.path.join(out, f'weekly_report_{DAY}_UNVALIDATED.md'))
          and applied == [] and state_files(td) == before, f"exit={code}")
with tempfile.TemporaryDirectory() as td:
    paths, c = chain_build(td)
    code1, out, applied1, _g = report_run(td, gate_b='PASS',
                                          glm_text='# 周报V1\n\n' + '正文一。' * 200)
    rep = os.path.join(out, f'weekly_report_{DAY}.md')
    v1 = open(rep, 'rb').read()
    st1 = open(os.path.join(out, f'report_status_{DAY}.json'), 'rb').read()
    code2, out, applied2, _g2 = report_run(td, gate_b='DEGRADED', status_false=True,
                                           glm_text='# 周报V2\n\n' + '正文二。' * 200)
    check("S13b 已有合格+状态写失败→exit 3+旧报告/旧状态字节不变+新报告隔离",
          code2 == 3 and open(rep, 'rb').read() == v1
          and open(os.path.join(out, f'report_status_{DAY}.json'), 'rb').read() == st1
          and os.path.exists(os.path.join(out, f'weekly_report_{DAY}_UNVALIDATED.md')),
          f"exit={code2}")

# ── E2E 场景14: 月报/季报独立入口(无质量门禁) ─────────────────────
print("\n── E2E场景14: 月报/季报/日报独立入口自证身份")
import monthly_review as mr       # noqa: E402
import quarterly_outlook as qo    # noqa: E402
import env_config as _ec          # noqa: E402
for _k in ('DEEPSEEK_API_KEY', 'DEEPSEEK_BASE_URL', 'DEEPSEEK_MODEL'):
    if not hasattr(_ec, _k):
        setattr(_ec, _k, '')
import daily_report_generator as drg   # noqa: E402

with tempfile.TemporaryDirectory() as td:
    os.makedirs(os.path.join(td, 'data', 'daily'))
    os.makedirs(os.path.join(td, 'config'))
    with open(os.path.join(td, 'config', 'thesis.json'), 'w', encoding='utf-8') as f:
        json.dump({'theses': []}, f)
    mdir = os.path.join(td, 'output', 'monthly')
    qdir = os.path.join(td, 'output', 'quarterly')
    glm = _GLM()
    with mock.patch.object(mr, 'ROOT_DIR', td), \
         mock.patch.object(mr, 'DATA_DIR', os.path.join(td, 'data', 'daily')), \
         mock.patch.object(mr, 'OUTPUT_DIR', mdir), \
         mock.patch.object(qo, 'ROOT_DIR', td), \
         mock.patch.object(qo, 'DATA_DIR', os.path.join(td, 'data', 'daily')), \
         mock.patch.object(qo, 'OUTPUT_DIR', qdir), \
         mock.patch.object(rg, 'load_prompt', lambda *a, **kw: '系统提示'), \
         mock.patch.object(rg, '_call_glm', glm), \
         mock.patch.object(sys, 'argv', ['monthly_review.py', '--month', '202609',
                                         '--dry-run']):
        quiet(mr.main)
    check("S14a 月报dry-run: monthly_data落盘+零GLM",
          os.path.exists(os.path.join(mdir, 'monthly_data_202609.md')) and glm.calls == 0)
    with mock.patch.object(mr, 'ROOT_DIR', td), \
         mock.patch.object(mr, 'DATA_DIR', os.path.join(td, 'data', 'daily')), \
         mock.patch.object(mr, 'OUTPUT_DIR', mdir), \
         mock.patch.object(rg, 'load_prompt', lambda *a, **kw: '系统提示'), \
         mock.patch.object(rg, '_call_glm', glm), \
         mock.patch.object(sys, 'argv', ['monthly_review.py', '--month', '202609']):
        quiet(mr.main)
    mtext = open(os.path.join(mdir, 'monthly_review_202609_UNVALIDATED.md'),
                 encoding='utf-8').read()
    check("S14a 月报正式路径: UNVALIDATED草稿名+横幅+不占合格正式名",
          'UNVALIDATED 研究草稿' in mtext
          and not os.path.exists(os.path.join(mdir, 'monthly_review_202609.md')))
    with mock.patch.object(qo, 'ROOT_DIR', td), \
         mock.patch.object(qo, 'DATA_DIR', os.path.join(td, 'data', 'daily')), \
         mock.patch.object(qo, 'OUTPUT_DIR', qdir), \
         mock.patch.object(rg, 'load_prompt', lambda *a, **kw: '系统提示'), \
         mock.patch.object(rg, '_call_glm', glm), \
         mock.patch.object(sys, 'argv', ['quarterly_outlook.py', '--quarter', '2026Q3']):
        quiet(qo.main)
    qtext = open(os.path.join(qdir, 'quarterly_outlook_2026Q3_UNVALIDATED.md'),
                 encoding='utf-8').read()
    check("S14b 季报: UNVALIDATED草稿名+横幅+quarterly_data保留",
          'UNVALIDATED 研究草稿' in qtext
          and os.path.exists(os.path.join(qdir, 'quarterly_data_2026Q3.md'))
          and not os.path.exists(os.path.join(qdir, 'quarterly_outlook_2026Q3.md')))
    # 月度索引排除规则改为**行为**断言(FIX3: 不得只扫源码字符串判断功能实现):
    # 沙箱周报目录混入候选/未验证/标注/备份文件+1份带发布状态的合格正式周报
    # +1份无状态档案 → gather_month_context索引只列规范名,档案带未验证标注
    wkdir = os.path.join(td, 'output', 'weekly')
    os.makedirs(wkdir, exist_ok=True)
    _open_w = lambda n, c='# 周报\n\n### 一、本周摘要\nSYNTHETIC摘要。\n': \
        open(os.path.join(wkdir, n), 'w', encoding='utf-8').write(c)
    _open_w('weekly_report_20260905_UNVALIDATED.md')
    _open_w('weekly_report_20260912_annotated.md')
    _open_w('weekly_report_20260919_CANDIDATE.md')
    _open_w('weekly_report_20260926.md.prev.bak', '# 备份残留\n')
    _open_w('weekly_report_20260926.md')     # 无状态→档案
    _open_w('weekly_report_20260919.md')     # 带发布状态→合格正式
    _st = {'report_file': 'weekly_report_20260919.md',
           'report_path': os.path.join(wkdir, 'weekly_report_20260919.md'),
           'report_digest': rp.digest_file(os.path.join(wkdir, 'weekly_report_20260919.md')),
           'gate_a': 'PASS', 'gate_b': 'PASS', 'final_quality': 'PASS',
           'published': True, 'target_date': '20260919'}
    json.dump(_st, open(os.path.join(wkdir, 'report_status_20260919.json'), 'w',
                        encoding='utf-8'), ensure_ascii=False)
    with mock.patch.object(mr, 'ROOT_DIR', td):
        _ctx = quiet(mr.gather_month_context, '202609')
    _idx = '\n'.join(_ctx['weekly_reports'])
    check("S14c 月度索引行为: 排除UNVALIDATED/annotated/CANDIDATE/.bak,档案带未验证标注",
          all(m not in _idx for m in ('_UNVALIDATED', '_annotated', '_CANDIDATE',
                                      '.prev.bak', '20260926: '))
          and '20260919:' in _idx and '未验证档案' in _idx
          and _idx.index('20260919') < _idx.index('未验证档案'), _idx)
    dout = os.path.join(td, 'daily')
    with mock.patch.object(drg, 'OUTPUT_DIR', dout), \
         mock.patch.object(drg, 'datetime', _FakeDT):
        quiet(drg.save_daily_report, 'SYNTHETIC遗留日报。' * 80)
    dtext = open(glob.glob(os.path.join(dout, 'daily_*.md'))[0], encoding='utf-8').read()
    check("S14d 遗留日报: daily_名+HTML注释与可见横幅双重UNVALIDATED自证",
          '<!-- UNVALIDATED legacy' in dtext and 'UNVALIDATED 遗留日报' in dtext)

# ═══ 汇总 ═══════════════════════════════════════════════════════════
print("\n" + "=" * 64)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 64)
sys.exit(1 if FAIL else 0)
