#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P0-1-FIX3 对抗测试(F3缺陷闭环验收)

覆盖:
1. FIX3-01(F2-NEW-001) 非法金融事实fail-closed——链路级: 快照被注入非法结构
   (非对象事实/身份缺失/质量缺失或非法)后, 真实data_assembler拒绝产包(exit 2),
   真实report_generator预检拒绝(verify_research_inputs=False, 全链GLM=0);
   非核心**合法**FAIL继续合理降级(不因fail-closed一律FAIL);
2. FIX3-02(F2-NEW-002) 所有正式报告消费者验证发布状态——真实
   load_previous_report()/data_validator发现入口/monthly_review索引, 不自造
   formal_view(生产读取器rp.formal_report_view为准): 跨日中断/首发布中断/
   摘要失配/.prev.bak混入/状态损坏/同日重发/DEGRADED发布/GateB失败等13类;
3. FIX3-03(F2-NEW-003) 数据包meta.gate_a必须与权威快照重算Gate A一致
   (统一口径rp.verify_meta_gate_a): 9类矩阵, 矛盾→拒绝+GLM=0+零状态回写。

fixture: tests/fixt.py 真实注册表全核心(32 core)SYNTHETIC采集→真实
snapshot_builder/装配/锚点构建; GLM全程mock(零付费零网络); 临时目录隔离,
不触生产数据; 断言全部针对真实函数返回值/磁盘字节/退出码, 无源码字符串扫描。
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
import snapshot_builder as sb             # noqa: E402
import data_assembler as da               # noqa: E402
import data_validator as dv               # noqa: E402
import monthly_review as mr               # noqa: E402
import report_generator as rg             # noqa: E402
import fixt                               # noqa: E402

DAY = '20261024'
DAY1 = '20261023'      # 跨日场景: 上一个发布日
DAY2 = '20261024'      # 跨日场景: 中断日
DAY3 = '20261025'      # 跨日读取日


def _DT(*args):
    """指定日期的datetime替身(generate_weekly_report/load_previous_report用)"""
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
DT_D3 = _DT(2026, 10, 25, 8, 0, 0)


class _GLM:
    def __init__(self, text=None):
        self.text = text or ('# 投资周报(SYNTHETIC测试文本)\n\n' + '本周市场综述与分资产回顾。' * 60)
        self.calls = 0

    def __call__(self, system_prompt, user_prompt, max_tokens=32000, timeout=900):
        self.calls += 1
        return self.text


def run_pub(td, gate_b='PASS', validator_exc=None, status_false=False,
            replace_fail_suffix=None, glm_text=None, dt=DT_DAY, out_subdir='out'):
    """在已构造研究日的td上运行真实generate_weekly_report(可注入故障)。
    返回(exit_code, out_dir, glm, applied)。apply_status_updates记录调用
    (成功发布也**不**触碰生产thesis/views——零回写由applied断言)。
    out_subdir: 周报输出目录父名(默认'out';月报场景用'output'对齐
    monthly_review.gather_month_context的ROOT_DIR/output/weekly布局)。"""
    out_dir = os.path.join(td, out_subdir, 'weekly')
    glm = _GLM(glm_text)
    applied = []

    def _apply(report, classification, anchors=None, **kw):
        applied.append(classification)

    def _validate(md_path, anchors=None, anchors_file=None):
        if validator_exc:
            raise validator_exc
        return (gate_b, ['SYNTHETIC警告'])

    real_replace = os.replace

    def _maybe_fail_replace(src, dst):
        if replace_fail_suffix and str(src).endswith(replace_fail_suffix):
            raise OSError(f'(mock)os.replace失败: {src}')
        return real_replace(src, dst)

    patches = [
        mock.patch.object(rg, 'DATA_DIR', os.path.join(td, 'data')),
        mock.patch.object(rg, 'OUTPUT_DIR', out_dir),
        mock.patch.object(rg, 'datetime', dt),
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
    ]
    if status_false:
        patches.append(mock.patch.object(rg, 'write_report_status',
                                         lambda *a, **kw: False))
    if replace_fail_suffix:
        patches.append(mock.patch.object(rg.os, 'replace', _maybe_fail_replace))
    with contextlib.ExitStack() as stack:
        for p in patches:
            stack.enter_context(p)
        try:
            quiet(rg.generate_weekly_report)
            code = 0
        except SystemExit as e:
            code = e.code
    return code, out_dir, glm, applied


def run_assembler(td, ymd, dt=DT_DAY):
    """真实data_assembler.main(当日): 返回退出码"""
    with mock.patch.object(da, 'DATA_DIR', os.path.join(td, 'data')), \
         mock.patch.object(da, 'datetime', dt):
        try:
            quiet(da.main)
            return 0
        except SystemExit as e:
            return e.code


def run_verify(td, dt=DT_DAY):
    """真实verify_research_inputs(当日): 返回(ok, problems)"""
    with mock.patch.object(rg, 'DATA_DIR', os.path.join(td, 'data')), \
         mock.patch.object(rg, 'datetime', dt):
        ok, problems, _ctx = quiet(rg.verify_research_inputs)
    return ok, problems


print("=" * 64)
print("IA-P0-1-FIX3 对抗测试: 非法事实fail-closed/发布状态读取/包Gate A一致")
print("=" * 64)

# ════════════════════════════════════════════════════════════════════
# 1. FIX3-01(F2-NEW-001): 非法事实结构 → 真实装配与报告入口全部拒绝
# ════════════════════════════════════════════════════════════════════
print("\n── 1. 非法金融事实fail-closed(FIX3-01/F2-NEW-001,链路级)")


def corrupt_snapshot(snap_path, mutate):
    snap = json.load(open(snap_path, encoding='utf-8'))
    mutate(snap)
    with open(snap_path, 'w', encoding='utf-8') as f:
        json.dump(snap, f, ensure_ascii=False, indent=1)
    return snap


def _fact_of(snap, mid):
    for f in snap['facts']:
        if isinstance(f, dict) and f.get('metric_id') == mid:
            return f
    return None


ILLEGAL_VARIANTS = [
    ('facts含字符串', lambda s: s['facts'].append('garbage-string')),
    ('facts含null', lambda s: s['facts'].append(None)),
    ('facts含数组', lambda s: s['facts'].append([1, 2, 3])),
    ('事实缺metric_id', lambda s: s['facts'].append({'value': 1, 'quality_status': 'PASS'})),
    ('非核心质量值非法', lambda s: _fact_of(s, 'BEI_10Y').__setitem__('quality_status', 'PROBABLY_OK')),
    ('非核心质量缺失', lambda s: _fact_of(s, 'BEI_10Y').pop('quality_status')),
]
for label, mutate in ILLEGAL_VARIANTS:
    with tempfile.TemporaryDirectory() as td:
        snap, snap_path, paths = fixt.build_full_day(td, DAY)
        corrupt_snapshot(snap_path, mutate)
        # 装配器: 删除既有包后重跑 → 拒绝产包(exit 2)
        os.remove(paths['pack'])
        if os.path.exists(paths['pack'] + '.meta.json'):
            os.remove(paths['pack'] + '.meta.json')
        code = run_assembler(td, DAY)
        pack_made = os.path.exists(paths['pack'])
        # 报告入口预检: 拒绝(GLM之前)
        ok, problems = run_verify(td)
        # 锚点批次核验: 权威快照不可重算 → 拒绝
        okb, whyb = rp.verify_anchor_batch(paths['anchors'], anchors_date=DAY,
                                           daily_dir=os.path.dirname(snap_path),
                                           trusted_root=td)
        check(f"{label}→装配器拒产包(exit2)+预检拒+锚点批次拒",
              code == 2 and not pack_made and ok is False and okb is False
              and any('Gate A' in p or '非法' in p or '不可' in p for p in problems),
              f"asm={code} pack={pack_made} verify={ok} anchor={okb}:{whyb[:40]}")

# 对照组1: 非核心**合法**FAIL → 继续合理降级(不因fail-closed一律FAIL)
with tempfile.TemporaryDirectory() as td:
    snap, snap_path, paths = fixt.build_full_day(td, DAY, gate='DEGRADED')
    os.remove(paths['pack'])
    if os.path.exists(paths['pack'] + '.meta.json'):
        os.remove(paths['pack'] + '.meta.json')
    code = run_assembler(td, DAY)
    meta = rp.load_meta(paths['pack'])
    ok, problems = run_verify(td)
    check("对照: 非核心合法FAIL→装配exit0+包meta.gate_a=DEGRADED+预检通过",
          code == 0 and os.path.exists(paths['pack'])
          and meta.get('gate_a') == 'DEGRADED' and ok,
          f"asm={code} meta_gate={meta.get('gate_a')} verify={ok}:{problems[:1]}")

# 对照组2: 全核心PASS正常日
with tempfile.TemporaryDirectory() as td:
    snap, snap_path, paths = fixt.build_full_day(td, DAY)
    ok, problems = run_verify(td)
    meta = rp.load_meta(paths['pack'])
    check("对照: 全核心PASS日→预检通过+包meta.gate_a=PASS(字段在)",
          ok and meta.get('gate_a') == 'PASS', f"{ok}:{problems[:1]}")

# ════════════════════════════════════════════════════════════════════
# 2. FIX3-02(F2-NEW-002): 正式消费者只认可验证的已发布状态
# ════════════════════════════════════════════════════════════════════
print("\n── 2. 正式报告权威读取(FIX3-02/F2-NEW-002,真实消费者)")


def load_prev(td, dt):
    with mock.patch.object(rg, 'OUTPUT_DIR', os.path.join(td, 'out', 'weekly')), \
         mock.patch.object(rg, 'datetime', dt):
        return quiet(rg.load_previous_report)


def pub_pass_day(td, ymd, glm_text=None, dt=None, out_subdir='out'):
    """在td上构造ymd研究日并完成一次PASS发布,返回(out_dir, glm_text)"""
    fixt.build_full_day(td, ymd)
    code, out, glm, applied = run_pub(td, dt=dt or _DT(*(int(ymd[:4]), int(ymd[4:6]), int(ymd[6:]), 8, 0, 0)),
                                      glm_text=glm_text, out_subdir=out_subdir)
    assert code == 0, f'发布失败 code={code}'
    return out


# (1) 当日正常发布 → 真实消费者全部认定
with tempfile.TemporaryDirectory() as td:
    out = pub_pass_day(td, DAY, glm_text='# 周报V1\n\n' + '正文一(SYNTHETIC)。' * 100)
    rep = os.path.join(out, f'weekly_report_{DAY}.md')
    view, vr = rp.formal_report_view(rep)
    check("(1)正常发布PASS→生产读取器认定(published+PASS+摘要一致)",
          view is not None and view['status']['published'] is True
          and view['status']['final_quality'] == 'PASS', vr)
    prev = load_prev(td, DT_D3)
    check("(1)load_previous_report取已发布合格报告(无未验证标注)",
          '周报V1' in prev and '未验证' not in prev, prev[:40])
    p, mode = dv.find_latest_report_for_validation(out)
    check("(1)校验器发现入口→formal模式", mode == 'formal' and p == rep, f"{mode}:{p}")
    check("(1)scan_formal_weekly_reports恰1份", len(rp.scan_formal_weekly_reports(out)) == 1)

# (2) 同日重发 → 读取器认新摘要
with tempfile.TemporaryDirectory() as td:
    out = pub_pass_day(td, DAY, glm_text='# 周报V1\n\n' + '正文一。' * 200)
    code, out, glm, applied = run_pub(td, glm_text='# 周报V2\n\n' + '正文二。' * 200)
    rep = os.path.join(out, f'weekly_report_{DAY}.md')
    view, vr = rp.formal_report_view(rep)
    check("(2)同日重发→正式认定+摘要=当前字节(V2)",
          view is not None and '# 周报V2' in open(rep, encoding='utf-8').read()
          and '# 周报V1' not in open(rep, encoding='utf-8').read(), vr)

# (3) 跨日: 昨日A已发布, 今日发布在"替换后/状态未写"中断 → 次日读取必须拿A不是B
with tempfile.TemporaryDirectory() as td:
    out = pub_pass_day(td, DAY1, glm_text='# 周报A\n\n' + '正文A(SYNTHETIC)。' * 100,
                       dt=_DT(2026, 10, 23, 8, 0, 0))
    fixt.build_full_day(td, DAY2)   # 今日研究日(不跑发布)
    # 手工构造中断态: 正式文件名下是未发布的B内容, 无主状态(仅候选状态)
    with open(os.path.join(out, f'weekly_report_{DAY2}.md'), 'w', encoding='utf-8') as f:
        f.write('# 周报B(未完成发布)\n\n' + '正文B。' * 50)
    json.dump({'report_file': f'weekly_report_{DAY2}.md', 'published': False,
               'awaiting_publish': True, 'final_quality': 'PASS'},
              open(os.path.join(out, f'report_status_{DAY2}_candidate.json'), 'w'))
    view, vr = rp.formal_report_view(os.path.join(out, f'weekly_report_{DAY2}.md'))
    check("(3)中断产物(替换已执行/主状态未写)→生产读取器拒绝", view is None, vr)
    prev = load_prev(td, DT_D3)
    check("(3)次日load_previous_report取昨日A而非中断B",
          '周报A' in prev and '周报B' not in prev, prev[:40])
    p, mode = dv.find_latest_report_for_validation(out)
    check("(3)校验器发现入口仍认昨日A(formal)", mode == 'formal' and p.endswith(f'weekly_report_{DAY1}.md'),
          f"{mode}:{os.path.basename(str(p))}")

# (4) 首次发布中断(无任何旧状态) → 未验证档案, 不得静默当作合格
with tempfile.TemporaryDirectory() as td:
    out = os.path.join(td, 'out', 'weekly')
    os.makedirs(out)
    with open(os.path.join(out, f'weekly_report_{DAY}.md'), 'w', encoding='utf-8') as f:
        f.write('# 周报B(首次发布中断)\n\n' + '正文B。' * 80)
    view, vr = rp.formal_report_view(os.path.join(out, f'weekly_report_{DAY}.md'))
    check("(4)首发布中断无旧状态→读取器拒绝", view is None, vr)
    prev = load_prev(td, DT_D3)
    check("(4)档案回退但显式标注未验证(不静默赋合格认证)",
          '周报B' in prev and '未验证历史档案' in prev, prev[-60:])
    p, mode = dv.find_latest_report_for_validation(out)
    check("(4)校验器发现入口→archive模式(未验证)", mode == 'archive', mode)

# (5) 旧PASS状态但正式文件已被替换(摘要失配)
with tempfile.TemporaryDirectory() as td:
    out = pub_pass_day(td, DAY, glm_text='# 周报V1\n\n' + '正文一。' * 200)
    rep = os.path.join(out, f'weekly_report_{DAY}.md')
    with open(rep, 'w', encoding='utf-8') as f:
        f.write('# 被替换的内容(非发布事务)\n\n' + 'X。' * 100)
    view, vr = rp.formal_report_view(rep)
    check("(5)状态声明PASS但内容摘要失配→拒绝", view is None and '摘要' in (vr or ''), vr)
    prev = load_prev(td, DT_D3)
    check("(5)档案回退+未验证标注", '被替换的内容' in prev and '未验证' in prev, prev[-40:])

# (6) .prev.bak混在周报目录 → 文件名口径排除, 不误取
with tempfile.TemporaryDirectory() as td:
    out = pub_pass_day(td, DAY, glm_text='# 周报V1\n\n' + '正文一。' * 200)
    rep = os.path.join(out, f'weekly_report_{DAY}.md')
    with open(rep + '.prev.bak', 'w', encoding='utf-8') as f:
        f.write('# 备份残留(更晚排序)\n')
    check("(6)weekly_report_files排除.prev.bak",
          f'weekly_report_{DAY}.md.prev.bak' not in rp.weekly_report_files(out))
    prev = load_prev(td, DT_D3)
    check("(6)load_previous_report不误取备份(取正式A)",
          '周报V1' in prev and '备份残留' not in prev, prev[:40])

# (7) 状态JSON损坏
with tempfile.TemporaryDirectory() as td:
    out = pub_pass_day(td, DAY, glm_text='# 周报V1\n\n' + '正文一。' * 200)
    with open(os.path.join(out, f'report_status_{DAY}.json'), 'w', encoding='utf-8') as f:
        f.write('{"broken": oops')
    view, vr = rp.formal_report_view(os.path.join(out, f'weekly_report_{DAY}.md'))
    check("(7)状态JSON损坏→读取器拒绝", view is None, vr)
    p, mode = dv.find_latest_report_for_validation(out)
    check("(7)校验器→archive模式", mode == 'archive', mode)

# (8) 完整成功发布DEGRADED → 允许的降级仍被认定
with tempfile.TemporaryDirectory() as td:
    fixt.build_full_day(td, DAY, gate='DEGRADED')
    code, out, glm, applied = run_pub(td, gate_b='PASS',
                                      glm_text='# 周报D\n\n' + '正文D。' * 200)
    rep = os.path.join(out, f'weekly_report_{DAY}.md')
    view, vr = rp.formal_report_view(rep)
    check("(8)DEGRADED发布→读取器认定(final=DEGRADED∈允许集)",
          view is not None and view['status']['final_quality'] == 'DEGRADED', vr)
    prev = load_prev(td, DT_D3)
    check("(8)load_previous_report取DEGRADED已发布报告(无标注)",
          '周报D' in prev and '未验证' not in prev, prev[:40])

# (9) Gate B FAIL → 候选隔离, 消费者零认定
with tempfile.TemporaryDirectory() as td:
    fixt.build_full_day(td, DAY)
    code, out, glm, applied = run_pub(td, gate_b='FAIL', glm_text='# 周报X\n\n' + '正文。' * 200)
    check("(9)GateB FAIL→exit3+GLM恰1次+零回写",
          code == 3 and glm.calls == 1 and applied == [], f"exit={code} glm={glm.calls}")
    check("(9)消费者零认定(无formal,档案不含UNVALIDATED名)",
          rp.scan_formal_weekly_reports(out) == []
          and dv.find_latest_report_for_validation(out)[1] != 'formal'
          and '周报X' not in load_prev(td, DT_D3))

# (10) 发布替换失败(次日重发场景): 昨日A仍为唯一formal
with tempfile.TemporaryDirectory() as td:
    out = pub_pass_day(td, DAY1, glm_text='# 周报A\n\n' + '正文A。' * 200,
                       dt=_DT(2026, 10, 23, 8, 0, 0))
    fixt.build_full_day(td, DAY2)
    code, out, glm, applied = run_pub(td, replace_fail_suffix='_CANDIDATE.md', dt=_DT(2026, 10, 24, 8, 0, 0),
                                      glm_text='# 周报B\n\n' + '正文B。' * 200)
    _v1, _r1 = rp.formal_report_view(os.path.join(out, f'weekly_report_{DAY1}.md'))
    _v2, _r2 = rp.formal_report_view(os.path.join(out, f'weekly_report_{DAY2}.md'))
    check("(10)替换失败→exit3,昨日A字节未动仍formal",
          code == 3 and _v1 is not None and _v2 is None,
          f"exit={code} v1={_r1[:30]} v2={_r2[:30]}")

# (11) 主状态写入失败(次日重发场景)
with tempfile.TemporaryDirectory() as td:
    out = pub_pass_day(td, DAY1, glm_text='# 周报A\n\n' + '正文A。' * 200,
                       dt=_DT(2026, 10, 23, 8, 0, 0))
    fixt.build_full_day(td, DAY2)
    code, out, glm, applied = run_pub(td, status_false=True, dt=_DT(2026, 10, 24, 8, 0, 0),
                                      glm_text='# 周报B\n\n' + '正文B。' * 200)
    _v1, _r1 = rp.formal_report_view(os.path.join(out, f'weekly_report_{DAY1}.md'))
    _v2, _r2 = rp.formal_report_view(os.path.join(out, f'weekly_report_{DAY2}.md'))
    check("(11)状态写失败→exit3,昨日A仍formal,今日B隔离不认定",
          code == 3 and _v1 is not None and _v2 is None,
          f"exit={code} v1={_r1[:30]} v2={_r2[:30]}")

# (12) 读取器分支单元: 身份失配/target_date失配/published=False/final=FAIL
with tempfile.TemporaryDirectory() as td:
    fpath = os.path.join(td, 'weekly_report_20261024.md')
    open(fpath, 'w', encoding='utf-8').write('# 报告\n')
    dg = rp.digest_file(fpath)

    def st(**kw):
        # FIX4-02: report_path为必需身份字段(真实_status_body恒写入)——
        # 手工构造的合法基线须带上(缺失分支的负向覆盖在test_p01_fix4矩阵)
        base = {'report_file': 'weekly_report_20261024.md', 'target_date': '20261024',
                'report_path': fpath,
                'report_digest': dg, 'published': True, 'final_quality': 'PASS'}
        base.update(kw)
        json.dump(base, open(os.path.join(td, 'report_status_20261024.json'), 'w'))

    st(report_file='weekly_report_20261023.md')
    v, r = rp.formal_report_view(fpath)
    check("(12)状态报告身份失配→拒绝", v is None and '身份' in r, r)
    st(target_date='20261023')
    v, r = rp.formal_report_view(fpath)
    check("(12)状态target_date失配→拒绝", v is None and 'target_date' in r, r)
    st(published=False)
    v, r = rp.formal_report_view(fpath)
    check("(12)published=False→拒绝", v is None and 'published' in r, r)
    st(final_quality='FAIL')
    v, r = rp.formal_report_view(fpath)
    check("(12)final=FAIL→拒绝(非合格正式)", v is None and 'final_quality' in r, r)
    st()
    v, r = rp.formal_report_view(fpath)
    check("(12)全字段一致→认定", v is not None, r)

# (13) 月报索引(真实gather_month_context): formal不标注/档案标注/排除特殊名
with tempfile.TemporaryDirectory() as td:
    out = pub_pass_day(td, '20260919', glm_text='# 周报A\n\n### 一、本周摘要\nSYNTHETIC摘要A。\n' + '正文(SYNTHETIC)。' * 100,
                       dt=_DT(2026, 9, 19, 8, 0, 0), out_subdir='output')
    os.makedirs(os.path.join(td, 'config'), exist_ok=True)
    json.dump({'theses': []}, open(os.path.join(td, 'config', 'thesis.json'), 'w'))
    for n in ('weekly_report_20260905_UNVALIDATED.md', 'weekly_report_20260912_annotated.md',
              'weekly_report_20260926_CANDIDATE.md', 'weekly_report_20260926.md.prev.bak'):
        open(os.path.join(out, n), 'w', encoding='utf-8').write('# 排除项\n')
    with open(os.path.join(out, 'weekly_report_20260926.md'), 'w', encoding='utf-8') as f:
        f.write('# 周报\n\n### 一、本周摘要\nSYNTHETIC摘要B。\n')
    with mock.patch.object(mr, 'ROOT_DIR', td):
        ctx = quiet(mr.gather_month_context, '202609')
    idx = '\n'.join(ctx['weekly_reports'])
    check("(13)月报索引: formal(0919)不标注,档案(0926)标注,特殊名全排除",
          all(m not in idx for m in ('_UNVALIDATED', '_annotated', '_CANDIDATE', '.prev.bak'))
          and '20260919:' in idx and '20260926 *(未验证档案)*' in idx, idx)

# ════════════════════════════════════════════════════════════════════
# 3. FIX3-03(F2-NEW-003): pack meta.gate_a ↔ 权威快照重算Gate A
# ════════════════════════════════════════════════════════════════════
print("\n── 3. 数据包gate_a与权威快照一致(FIX3-03/F2-NEW-003)")


def tamper_pack_meta(pack_path, **kv):
    meta = rp.load_meta(pack_path) or {}
    meta.update(kv)
    for k, v in kv.items():
        if v is None:
            meta.pop(k, None)
    rp.write_meta(pack_path, meta)
    return meta


# (a) A=DEGRADED, pack谎报PASS → 预检拒 + 全链GLM=0 + 零回写 + 不产合格报告
with tempfile.TemporaryDirectory() as td:
    snap, snap_path, paths = fixt.build_full_day(td, DAY, gate='DEGRADED')
    tamper_pack_meta(paths['pack'], gate_a='PASS')
    ok, problems = run_verify(td)
    check("(a)A=DEGRADED+pack谎报PASS→预检拒(点名gate_a矛盾)",
          ok is False and any('gate_a' in p or 'Gate A' in p for p in problems),
          str(problems[:2]))
    code, out, glm, applied = run_pub(td, glm_text='# 周报V\n\n' + '正文(SYNTHETIC)。' * 200)
    check("(a)全链: GLM=0+exit2+零回写+无正式报告",
          code == 2 and glm.calls == 0 and applied == []
          and not os.path.exists(os.path.join(out, f'weekly_report_{DAY}.md')),
          f"exit={code} glm={glm.calls}")

# (b) A=PASS, pack谎报DEGRADED → 拒
with tempfile.TemporaryDirectory() as td:
    snap, snap_path, paths = fixt.build_full_day(td, DAY)
    tamper_pack_meta(paths['pack'], gate_a='DEGRADED')
    ok, problems = run_verify(td)
    check("(b)A=PASS+pack报DEGRADED→拒(双向一致才可信)",
          ok is False and any('gate_a' in p for p in problems), str(problems[:2]))

# (c) A=FAIL, 伪造pack(gate_a=PASS) → 拒(装配器根本不产包,手 forg e 也不行)
with tempfile.TemporaryDirectory() as td:
    snap, snap_path, paths = fixt.build_full_day(td, DAY, gate='FAIL')
    os.remove(paths['pack'])
    if os.path.exists(paths['pack'] + '.meta.json'):
        os.remove(paths['pack'] + '.meta.json')
    code = run_assembler(td, DAY)
    # 手工伪造: 用纯函数渲染FAIL快照的包+meta(gate_a谎报PASS,其余字段真实)
    import data_assembler as _dasm
    fake_pack = os.path.join(td, 'data', 'weekly', f'data_pack_{DAY}.md')
    with open(fake_pack, 'w', encoding='utf-8') as f:
        f.write(_dasm.build_markdown(snap, DAY))
    _m = rp.provenance_of(snap, snap_path)
    _m.update({'source': 'snapshot', 'pack_file': os.path.basename(fake_pack),
               'pack_digest': rp.digest_file(fake_pack),
               'scorecard_date': DAY, 'scorecard_current': True, 'gate_a': 'PASS'})
    rp.write_meta(fake_pack, _m)
    ok, problems = run_verify(td)
    check("(c)A=FAIL+装配器拒产包(exit2)+伪造pack(gate_a=PASS)仍被预检拒",
          code == 2 and ok is False
          and any('Gate A' in p for p in problems), f"asm={code}:{problems[:2]}")

# (d) pack缺gate_a → 拒
with tempfile.TemporaryDirectory() as td:
    snap, snap_path, paths = fixt.build_full_day(td, DAY)
    tamper_pack_meta(paths['pack'], gate_a=None)
    ok, problems = run_verify(td)
    check("(d)pack缺gate_a字段→拒(必需来源字段)", ok is False
          and any('gate_a' in p for p in problems), str(problems[:2]))

# (e) pack gate_a非法值 → 拒
with tempfile.TemporaryDirectory() as td:
    snap, snap_path, paths = fixt.build_full_day(td, DAY)
    tamper_pack_meta(paths['pack'], gate_a='MAYBE')
    ok, problems = run_verify(td)
    check("(e)pack gate_a非法值→拒", ok is False
          and any('gate_a' in p for p in problems), str(problems[:2]))

# (f) 包正文被改(摘要失配) → 拒(既有规则保持)
with tempfile.TemporaryDirectory() as td:
    snap, snap_path, paths = fixt.build_full_day(td, DAY)
    with open(paths['pack'], 'a', encoding='utf-8') as f:
        f.write('\n篡改行: SPX=9999\n')
    ok, problems = run_verify(td)
    check("(f)包正文被改→摘要失配拒(既有规则保持)",
          ok is False and any('摘要' in p or '不一致' in p for p in problems),
          str(problems[:2]))

# (g) 正常PASS/DEGRADED日通过(已在§1对照组覆盖,此处汇总)
with tempfile.TemporaryDirectory() as td:
    fixt.build_full_day(td, DAY)
    ok1, _ = run_verify(td)
with tempfile.TemporaryDirectory() as td:
    fixt.build_full_day(td, DAY, gate='DEGRADED')
    ok2, _ = run_verify(td)
check("(g)A=PASS+pack=PASS / A=DEGRADED+pack=DEGRADED → 均通过", ok1 and ok2)

# ═══ 汇总 ═══════════════════════════════════════════════════════════
print("\n" + "=" * 64)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 64)
sys.exit(1 if FAIL else 0)
