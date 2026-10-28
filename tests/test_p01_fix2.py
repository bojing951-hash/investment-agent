#!/usr/bin/env python3
"""IA-P0-1-FIX2 对抗性整改测试(2026-10-27) — 五项缺陷 + §11兼容项

覆盖FIX2指令的独立对抗矩阵:
- FIX2-01 报告发布事务(IA-DEF-001): 9类故障注入×6维检查(A字节/A状态/正式入口
  认定/无伪装合格产物/错误留痕/退出码);
- FIX2-02 Gate A事实重算(IA-DEF-002): 真实注册表全核心fixture的重算/裁决矩阵
  (缺失/FAIL/非核心/重复/非法质量/计数冲突/合法降级),声明与事实矛盾一律拒绝;
- FIX2-03 步骤依赖与报告授权(IA-DEF-003): 关键采集/评分卡/装配/校验失败传播,
  旧评分卡/旧包不得冒充当日,台账allow_formal_report须有事实依据;
- FIX2-04 快照版本规范(IA-DEF-004): 文件系统级选择器,base/_v2+规范十进制,
  非法表示/身份冲突/日期不符整日拒绝;
- FIX2-05 来源元数据完整一致(IA-DEF-005): verify_anchor_batch必需字段/日期
  三方一致/摘要无条件重算,缺一即拒;
- §11 兼容项: 月报/季报离线mock(--month/--quarter/--dry-run保留,UNVALIDATED
  草稿不冒充合格),遗留日报自证UNVALIDATED身份。

数据纪律: 全部SYNTHETIC fixture(tests/fixt.py真实构建,注册表32核心齐备)+
临时目录隔离,不触真实data/config/output;GLM全程mock,零付费调用。
运行: ~/AI内容/venv/bin/python3 tests/test_p01_fix2.py
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


def subprocess_run(argv):
    return subprocess.run(argv, capture_output=True, text=True).returncode


import research_provenance as rp          # noqa: E402
import snapshot_builder as sb             # noqa: E402
import data_assembler as da               # noqa: E402
import report_generator as rg             # noqa: E402
import run_weekly                         # noqa: E402
import fixt                               # noqa: E402

DAY = '20261024'
DAY_ISO = '2026-10-24'
AS_OF = '2026-10-24T08:00:00+08:00'


class _FakeDT:
    @staticmethod
    def now():
        import datetime as _dt
        return _dt.datetime(2026, 10, 24, 8, 0, 0)

    @staticmethod
    def strptime(s, f):
        import datetime as _dt
        return _dt.datetime.strptime(s, f)


# 模块级真实PASS快照(选择器/重算矩阵复用,变体走deepcopy)
RE_PASS = quiet(fixt.real_snapshot, DAY)


# ════════════════════════════════════════════════════════════════════
# FIX2-01 报告发布事务: 9类故障注入
# ════════════════════════════════════════════════════════════════════
print("=" * 64)
print("IA-P0-1-FIX2 对抗测试: 发布事务/Gate A重算/依赖授权/版本规范/元数据")
print("=" * 64)
print("\n── 1. 发布事务故障注入(FIX2-01/IA-DEF-001)")


class _GLMRecorder:
    def __init__(self, text=None):
        self.text = text or ('# 投资周报(SYNTHETIC测试文本)\n\n' + '本周市场综述与分资产回顾。' * 60)
        self.calls = 0

    def __call__(self, system_prompt, user_prompt, max_tokens=32000, timeout=900):
        self.calls += 1
        return self.text


def run_pub_flow(td, gate_b='PASS', validator_exc=None, cand_status_false=False,
                 status_false=False, replace_fail_suffix=None, glm_text=None):
    """在已构造研究日的td上运行generate_weekly_report(可注入各环节故障)。
    返回(exit_code, out_dir)。replace_fail_suffix: os.replace对该后缀src失败。"""
    out_dir = os.path.join(td, 'out', 'weekly')
    glm = _GLMRecorder(glm_text)
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
    if cand_status_false:
        patches.append(mock.patch.object(rg, 'write_candidate_status',
                                         lambda *a, **kw: False))
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
    return code, out_dir


def formal_view(out_dir, ymd=DAY):
    """FIX3-02: 认定逻辑**直接委托生产读取器** rp.formal_report_view(不再自造
    formal_view——独立验收要求以真实消费者口径断言)。权威=发布状态published
    +final_quality∈(PASS,DEGRADED)+身份一致+内容摘要重算一致。"""
    view, _reason = rp.formal_report_view(os.path.join(out_dir, f'weekly_report_{ymd}.md'))
    return view['status'] if view else None


def no_fake_qualified(out_dir, ymd=DAY):
    """无伪装合格产物: 候选文件不残留/不以正式名存在;UNVALIDATED产物无published
    状态;不存在'正式名文件+无法认定状态'的半发布态。"""
    cand = os.path.join(out_dir, f'weekly_report_{ymd}_CANDIDATE.md')
    if os.path.exists(cand):
        return False
    usp = os.path.join(out_dir, f'report_status_{ymd}_UNVALIDATED.json')
    if os.path.exists(usp):
        try:
            if json.load(open(usp, encoding='utf-8')).get('published'):
                return False
        except (ValueError, OSError):
            return False
    formal = os.path.join(out_dir, f'weekly_report_{ymd}.md')
    fv = formal_view(out_dir, ymd)
    if os.path.exists(formal) and fv is None:
        return False   # 正式名文件存在却无法被权威状态认定=半发布态
    return True


# C1: 首发布+Gate B FAIL
with tempfile.TemporaryDirectory() as td:
    fixt.build_full_day(td, DAY)
    code, out = run_pub_flow(td, gate_b='FAIL')
    formal = os.path.join(out, f'weekly_report_{DAY}.md')
    unval = os.path.join(out, f'weekly_report_{DAY}_UNVALIDATED.md')
    st = json.load(open(os.path.join(out, f'report_status_{DAY}.json')))
    check("C1 GateB FAIL: exit 3", code == 3, f"exit={code}")
    check("C1 正式名不发布(A字节)", not os.path.exists(formal))
    check("C1 候选隔离_UNVALIDATED+主状态FAIL未发布(A状态/错误留痕)",
          os.path.exists(unval) and st['final_quality'] == 'FAIL'
          and st.get('published') is False and st.get('failure_reason'),
          str(st.get('failure_reason')))
    check("C1 正式入口不认定+无伪装合格", formal_view(out) is None
          and no_fake_qualified(out))

# C2: 首发布+校验器异常
with tempfile.TemporaryDirectory() as td:
    fixt.build_full_day(td, DAY)
    code, out = run_pub_flow(td, validator_exc=RuntimeError('校验器崩溃(SYNTHETIC)'))
    formal = os.path.join(out, f'weekly_report_{DAY}.md')
    st = json.load(open(os.path.join(out, f'report_status_{DAY}.json')))
    check("C2 校验器异常: exit 3+正式名不发布+隔离+FAIL留痕",
          code == 3 and not os.path.exists(formal)
          and os.path.exists(os.path.join(out, f'weekly_report_{DAY}_UNVALIDATED.md'))
          and st['final_quality'] == 'FAIL' and st.get('published') is False,
          f"exit={code}")
    check("C2 正式入口不认定+无伪装合格",
          formal_view(out) is None and no_fake_qualified(out))

# C3: 候选状态记录失败 → 不得发布无过程记录的正式报告
with tempfile.TemporaryDirectory() as td:
    fixt.build_full_day(td, DAY)
    code, out = run_pub_flow(td, cand_status_false=True)
    formal = os.path.join(out, f'weekly_report_{DAY}.md')
    check("C3 候选状态失败: exit 3+不发布+隔离+FAIL留痕",
          code == 3 and not os.path.exists(formal)
          and os.path.exists(os.path.join(out, f'weekly_report_{DAY}_UNVALIDATED.md'))
          and json.load(open(os.path.join(out, f'report_status_{DAY}.json'))
                        )['final_quality'] == 'FAIL', f"exit={code}")
    check("C3 正式入口不认定+无伪装合格",
          formal_view(out) is None and no_fake_qualified(out))

# C4: 首发布+主状态写入失败(此前实现会截断状态文件/留下无状态正式报告)
with tempfile.TemporaryDirectory() as td:
    fixt.build_full_day(td, DAY)
    code, out = run_pub_flow(td, status_false=True)
    formal = os.path.join(out, f'weekly_report_{DAY}.md')
    check("C4 主状态写失败(首发布): exit 3+正式名不发布+新报告隔离",
          code == 3 and not os.path.exists(formal)
          and os.path.exists(os.path.join(out, f'weekly_report_{DAY}_UNVALIDATED.md')),
          f"exit={code}")
    check("C4 无伪装合格(不残留半发布态)", no_fake_qualified(out))

# C5: 已有合格报告+主状态写入失败 → 旧报告+旧状态字节级保持有效
with tempfile.TemporaryDirectory() as td:
    fixt.build_full_day(td, DAY)
    code1, out = run_pub_flow(td, gate_b='PASS', glm_text='# 周报V1\n\n' + '正文一。' * 200)
    rep = os.path.join(out, f'weekly_report_{DAY}.md')
    pub_bytes = open(rep, 'rb').read()
    st_bytes = open(os.path.join(out, f'report_status_{DAY}.json'), 'rb').read()
    code2, _ = run_pub_flow(td, gate_b='DEGRADED', status_false=True,
                            glm_text='# 周报V2\n\n' + '正文二。' * 200)
    check("C5 主状态写失败(已有合格): exit 3+旧报告字节未动+旧状态字节未动",
          code2 == 3 and open(rep, 'rb').read() == pub_bytes
          and open(os.path.join(out, f'report_status_{DAY}.json'), 'rb').read() == st_bytes,
          f"exit={code2}")
    check("C5 旧报告仍被正式入口认定为已发布合格",
          formal_view(out) is not None
          and formal_view(out)['report_digest'] == rp.digest_file(rep))
    check("C5 新报告隔离为_UNVALIDATED(不占正式名)+无残留备份",
          os.path.exists(os.path.join(out, f'weekly_report_{DAY}_UNVALIDATED.md'))
          and not os.path.exists(rep + '.prev.bak'))

# C6: 发布替换失败(os.replace OSError) + 隔离改名也失败 → 旧状态不受损
with tempfile.TemporaryDirectory() as td:
    fixt.build_full_day(td, DAY)
    code1, out = run_pub_flow(td, gate_b='PASS', glm_text='# 周报V1\n\n' + '正文一。' * 200)
    rep = os.path.join(out, f'weekly_report_{DAY}.md')
    pub_bytes = open(rep, 'rb').read()
    st_bytes = open(os.path.join(out, f'report_status_{DAY}.json'), 'rb').read()
    code2, _ = run_pub_flow(td, gate_b='PASS', replace_fail_suffix='_CANDIDATE.md',
                            glm_text='# 周报V2\n\n' + '正文二。' * 200)
    check("C6 发布替换失败: exit 3+旧报告/旧主状态字节未动",
          code2 == 3 and open(rep, 'rb').read() == pub_bytes
          and open(os.path.join(out, f'report_status_{DAY}.json'), 'rb').read() == st_bytes,
          f"exit={code2}")
    # 隔离改名同样失败(候选后缀替换均失败)→ 失败详情重定向UNVALIDATED状态;
    # 候选文件可保留(绝不占正式名),绝无published状态指认它
    usp = os.path.join(out, f'report_status_{DAY}_UNVALIDATED.json')
    ust = json.load(open(usp)) if os.path.exists(usp) else None
    check("C6 失败留痕(重定向UNVALIDATED状态,published=False,指向真实文件)",
          ust is not None and ust.get('published') is False
          and os.path.exists(ust.get('report_path') or ''),
          str(ust and ust.get('report_path')))
    check("C6 旧报告仍被正式入口认定+备份已清理",
          formal_view(out) is not None and not os.path.exists(rep + '.prev.bak'))

# C7: 进程中断于替换与写状态之间 → reconcile按权威状态恢复
with tempfile.TemporaryDirectory() as td:
    fixt.build_full_day(td, DAY)
    code1, out = run_pub_flow(td, gate_b='PASS', glm_text='# 周报V1\n\n' + '正文一。' * 200)
    rep = os.path.join(out, f'weekly_report_{DAY}.md')
    old_bytes = open(rep, 'rb').read()
    # 模拟中断: 新报告已替换到正式名,备份在场,主状态仍指向旧报告(权威)
    shutil.copyfile(rep, rep + '.prev.bak')
    with open(rep, 'w', encoding='utf-8') as f:
        f.write('# 中断残留的新报告(SYNTHETIC)\n\n未写状态即崩溃。' * 40)
    with mock.patch.object(rg, 'OUTPUT_DIR', out):
        acts = quiet(rg.reconcile_publication, DAY)
    check("C7 中断恢复: 备份恢复旧报告(字节一致)+中断产物隔离_UNVALIDATED",
          open(rep, 'rb').read() == old_bytes
          and os.path.exists(os.path.join(out, f'weekly_report_{DAY}_UNVALIDATED.md')),
          str(acts))
    check("C7 恢复后正式入口认定旧报告+备份清理",
          formal_view(out) is not None and not os.path.exists(rep + '.prev.bak'))

# C9: 首发布成功 + C8: 同日重发成功(刷新)
with tempfile.TemporaryDirectory() as td:
    fixt.build_full_day(td, DAY)
    code1, out = run_pub_flow(td, gate_b='PASS', glm_text='# 周报V1\n\n' + '正文一。' * 200)
    rep = os.path.join(out, f'weekly_report_{DAY}.md')
    v1_bytes = open(rep, 'rb').read()
    check("C9 首发布: exit 0+正式报告+主状态published+候选/候选状态/备份清理",
          code1 == 0 and os.path.exists(rep)
          and formal_view(out) is not None
          and not os.path.exists(os.path.join(out, f'weekly_report_{DAY}_CANDIDATE.md'))
          and not os.path.exists(rep + '.prev.bak')
          and not os.path.exists(os.path.join(out, f'report_status_{DAY}_candidate.json')),
          f"exit={code1}")
    code2, _ = run_pub_flow(td, gate_b='PASS', glm_text='# 周报V2(同日刷新)\n\n' + '正文二。' * 200)
    v2_bytes = open(rep, 'rb').read()
    fv = formal_view(out)
    check("C8 同日重发: exit 0+新报告替换旧版+状态摘要指向新文件",
          code2 == 0 and v2_bytes != v1_bytes and fv is not None
          and fv['report_digest'] == rp.digest_file(rep)
          and open(rep, 'rb').read() == v2_bytes, f"exit={code2}")
    check("C8 同日重发: 无备份/候选残留+无伪装合格",
          not os.path.exists(rep + '.prev.bak') and no_fake_qualified(out))

# 原语: 序列化失败不得截断既有状态文件
with tempfile.TemporaryDirectory() as td:
    sp = os.path.join(td, 'report_status_X.json')
    with open(sp, 'w', encoding='utf-8') as f:
        f.write('{"published": true, "keep": "me"}')
    before = open(sp, 'rb').read()
    ok = rg._atomic_write_json(sp, {'bad': object()})   # 不可序列化对象
    check("序列化失败→返回False+原文件字节不动+无tmp残留",
          ok is False and open(sp, 'rb').read() == before
          and not glob.glob(os.path.join(td, '*.tmp')))

# ════════════════════════════════════════════════════════════════════
# FIX2-02 Gate A事实重算矩阵(真实注册表全核心fixture)
# ════════════════════════════════════════════════════════════════════
print("\n── 2. Gate A事实重算矩阵(FIX2-02/IA-DEF-002)")


def _fact(snap, mid):
    return next(f for f in snap['facts'] if f.get('metric_id') == mid)


def _illegal_has(rec, mid):
    return any(str(s).startswith(f"{mid}=") for s in rec['illegal_quality'])


# 重算层(直接对rp.recompute_gate_a断言)
rec = rp.recompute_gate_a(RE_PASS)
check("全核心齐备→PASS;计数键集恰为3键(PASS/DEGRADED/FAIL)",
      rec['effective'] == 'PASS' and set(rec['counts']) == {'PASS', 'DEGRADED', 'FAIL'}
      and rec['overall'] == 'PASS', str(rec['counts']))

snap_miss = quiet(fixt.real_snapshot, DAY, missing=('VIX',))
rec = rp.recompute_gate_a(snap_miss)
check("核心缺失(VIX不在采集)→core_missing点名+effective FAIL",
      rec['core_missing'] == ['VIX'] and rec['effective'] == 'FAIL', str(rec['core_missing']))

snap_spx = quiet(fixt.real_snapshot, DAY, gate='FAIL')
rec = rp.recompute_gate_a(snap_spx)
check("核心FAIL(SPX值坏)→core_fail点名+effective FAIL",
      rec['core_fail'] == ['SPX'] and rec['effective'] == 'FAIL', str(rec['core_fail']))

snap_deg = quiet(fixt.real_snapshot, DAY, gate='DEGRADED')
rec = rp.recompute_gate_a(snap_deg)
check("非核心FAIL(UMCSENT值坏)→noncore_fail点名+effective DEGRADED(合理降级)",
      rec['noncore_fail'] == ['UMCSENT'] and rec['effective'] == 'DEGRADED', str(rec))

snap_dup = copy.deepcopy(RE_PASS)
snap_dup['facts'].append(copy.deepcopy(_fact(snap_dup, 'UMCSENT')))
rec = rp.recompute_gate_a(snap_dup)
check("重复metric_id→duplicates点名+effective FAIL(不可确定性分级)",
      rec['duplicates'] == ['UMCSENT'] and rec['effective'] == 'FAIL', str(rec['duplicates']))

snap_illegal_core = copy.deepcopy(RE_PASS)
_fact(snap_illegal_core, 'SPX')['quality_status'] = 'BOGUS'
rec = rp.recompute_gate_a(snap_illegal_core)
check("FIX3-01 核心质量值非法→illegal_quality点名+effective None(fail-closed)",
      _illegal_has(rec, 'SPX') and rec['effective'] is None and rec['reasons'],
      str(rec['illegal_quality']))
got, why = rp.gate_status(snap_illegal_core)
check("FIX3-01 核心质量非法快照→gate_status拒绝(不得放行任何状态)",
      got is None and '非法' in why, f"{got} {why}")

# FIX3-01(F2-NEW-001)反向回归: 本用例在FIX2轮曾错误预期"非核心质量非法→
# noncore_fail→DEGRADED"——独立验收判定该预期与冻结契约冲突(非法≠合法非核心
# FAIL,不得以降级放行非法结构)。按FIX3-01语义修正为fail-closed并保留。
snap_illegal_non = copy.deepcopy(RE_PASS)
_fact(snap_illegal_non, 'BEI_10Y')['quality_status'] = 'WEIRD'
rec = rp.recompute_gate_a(snap_illegal_non)
check("FIX3-01 非核心质量值非法→illegal_quality点名+effective None(不再冒充降级)",
      _illegal_has(rec, 'BEI_10Y') and 'BEI_10Y' not in rec['noncore_fail']
      and rec['effective'] is None and rec['reasons'], str(rec['illegal_quality']))
got, why = rp.gate_status(snap_illegal_non)
check("FIX3-01 非核心质量非法→gate_status拒绝(非法结构不得进入正式研究)",
      got is None and '非法' in why, f"{got} {why}")

snap_illegal_missing_qs = copy.deepcopy(RE_PASS)
_fact(snap_illegal_missing_qs, 'BEI_10Y').pop('quality_status')
rec = rp.recompute_gate_a(snap_illegal_missing_qs)
check("FIX3-01 非核心缺quality_status→illegal_quality(缺失≠有效)+None",
      _illegal_has(rec, 'BEI_10Y') and rec['effective'] is None,
      str(rec['illegal_quality']))

# FIX3-01: 非对象事实(字符串/null/数组)与身份缺失——不得静默跳过后当作完整合格快照
for _label, _badfact in (('字符串', '"garbage"'), ('null', 'None'), ('数组', '[1,2]')):
    snap_bad = copy.deepcopy(RE_PASS)
    snap_bad['facts'].append(_badfact)
    rec = rp.recompute_gate_a(snap_bad)
    check(f"FIX3-01 facts含{_label}→非对象事实点名+effective None",
          any('非对象事实' in s for s in rec['illegal_quality'])
          and rec['effective'] is None, str(rec['illegal_quality']))

snap_noid = copy.deepcopy(RE_PASS)
snap_noid['facts'].append({'value': 42, 'quality_status': 'PASS'})
rec = rp.recompute_gate_a(snap_noid)
check("FIX3-01 事实缺metric_id(身份不可识别)→illegal_quality+None",
      any('身份缺失' in s for s in rec['illegal_quality'])
      and rec['effective'] is None, str(rec['illegal_quality']))
snap_emptyid = copy.deepcopy(RE_PASS)
snap_emptyid['facts'].append({'metric_id': '   ', 'value': 1, 'quality_status': 'PASS'})
rec = rp.recompute_gate_a(snap_emptyid)
check("FIX3-01 metric_id空白串→身份不可识别→None",
      rec['effective'] is None, str(rec['illegal_quality']))

# FIX3-01: 合法WARN事实语义保持(轻度提示,counts不计,不降级)
snap_warn = copy.deepcopy(RE_PASS)
_wf = _fact(snap_warn, 'BEI_10Y')
_wf['quality_status'] = 'WARN'
# FIX5-02: 合法WARN必带WARN issue(真实引擎路径,如release-limit提示)
# ——只改状态不带依据自FIX5-02起按声明矛盾拒绝,属fixture合法化修复
_wf['issues'] = _wf.get('issues', []) + [
    {'category': 'fixture', 'severity': 'WARN', 'message': 'BEI_10Y模拟合法WARN提示'}]
_base_counts = dict(rp.recompute_gate_a(RE_PASS)['counts'])
# 快照由builder从facts重计counts——WARN不计入,合法变更须同步声明counts
snap_warn['quality']['counts']['PASS'] = _base_counts['PASS'] - 1
rec = rp.recompute_gate_a(snap_warn)
check("FIX3-01 合法WARN保持原语义(WARN不计counts,effective不变)",
      rec['counts'] == {'PASS': _base_counts['PASS'] - 1, 'DEGRADED': 0, 'FAIL': 0}
      and rec['effective'] == 'PASS'
      and 'BEI_10Y' not in rec['noncore_fail'] + rec['noncore_degraded'],
      str(rec['counts']))
got, why = rp.gate_status(snap_warn)
check("FIX3-01 合法WARN快照gate_status仍PASS(原有语义不变)", got == 'PASS', f"{got} {why}")

# FIX3-01: 缺失必要质量汇总字段→gate_status拒绝("必需字段缺失不得放行")
bad = copy.deepcopy(RE_PASS)
bad.pop('quality')
got, why = rp.gate_status(bad)
check("FIX3-01 快照缺quality汇总→拒绝(事实质量不可核验)",
      got is None and 'quality' in why, f"{got} {why}")
bad = copy.deepcopy(RE_PASS)
bad['quality'] = {'overall': 'PASS'}
got, why = rp.gate_status(bad)
check("FIX3-01 quality.counts缺失→拒绝", got is None and 'counts' in why, f"{got} {why}")
bad = copy.deepcopy(RE_PASS)
# FIX4: counts取自真实快照(不再硬编码旧34事实时代数字;负向检查"缺overall→拒"不变)
bad['quality'] = {'counts': dict(RE_PASS['quality']['counts'])}
got, why = rp.gate_status(bad)
check("FIX3-01 quality.overall缺失→拒绝", got is None and 'overall' in why, f"{got} {why}")

snap_mix = quiet(fixt.real_snapshot, DAY, missing=('VIX',), break_metric='UMCSENT')
rec = rp.recompute_gate_a(snap_mix)
check("混合(核心缺失+非核心FAIL)→FAIL(核心问题优先)",
      rec['effective'] == 'FAIL' and rec['core_missing'] == ['VIX']
      and rec['noncore_fail'] == ['UMCSENT'], str(rec['effective']))

rec = rp.recompute_gate_a({'facts': '不是列表'})
check("结构损坏(facts非列表)→effective None+原因(不猜测)",
      rec['effective'] is None and rec['reasons'], str(rec['reasons']))

snap_cd = copy.deepcopy(RE_PASS)
_cf = _fact(snap_cd, 'SPX')
_cf['quality_status'] = 'DEGRADED'
# FIX5-02: 合法DEGRADED必带DEGRADED issue(真实引擎路径,如新鲜度窗口降级)
_cf['issues'] = _cf.get('issues', []) + [
    {'category': 'fixture', 'severity': 'DEGRADED', 'message': 'SPX模拟合法降级(观测滞后)'}]
rec = rp.recompute_gate_a(snap_cd)
check("核心事实DEGRADED→counts.DEGRADED计入+effective DEGRADED",
      rec['counts']['DEGRADED'] == 1 and rec['effective'] == 'DEGRADED'
      and rec['overall'] == 'DEGRADED', str(rec['counts']))

# 语义区分: gate_a.status(研究许可) vs quality.overall(最差原始事实等级)
rec_deg = rp.recompute_gate_a(snap_deg)
check("语义区分: 非核心FAIL日 gate=DEGRADED而overall=FAIL(两者不同且各自成立)",
      rec_deg['overall'] == 'FAIL' and rec_deg['effective'] == 'DEGRADED')

snap_unknown = copy.deepcopy(RE_PASS)
snap_unknown['facts'].append({'metric_id': 'ZZZ_UNKNOWN', 'value': 1,
                              'quality_status': 'FAIL'})
rec = rp.recompute_gate_a(snap_unknown)
_rec_pass = rp.recompute_gate_a(RE_PASS)
# FIX4-01语义: 未注册指标不进核心分级,也不冒充非核心研究事实——FAIL仅留
# 诊断桶(non_research_facts)披露,不入counts,不降级不阻断
check("注册表外指标→不进核心分级也不冒充非核心研究事实(FAIL诊断桶,不计数不降级)",
      any('ZZZ_UNKNOWN' in s for s in rec['non_research_facts'])
      and 'ZZZ_UNKNOWN' not in rec['core_fail'] + rec['core_missing']
      and 'ZZZ_UNKNOWN' not in rec['noncore_fail'] + rec['noncore_degraded']
      and rec['counts'] == _rec_pass['counts'] and rec['effective'] == 'PASS',
      str(rec))

# 裁决层(gate_status: 声明↔重算矛盾一律拒绝)
got, why = rp.gate_status(RE_PASS)
check("真实PASS+声明一致→PASS", got == 'PASS', f"{got} {why}")
got, why = rp.gate_status(snap_spx)
check("真实FAIL(SPX坏)+声明FAIL(builder写入)→FAIL", got == 'FAIL', f"{got} {why}")
bad = copy.deepcopy(snap_spx)
bad['gate_a']['status'] = 'PASS'
got, why = rp.gate_status(bad)
check("核心实际FAIL+声明PASS→拒绝(理由含实际FAIL)", got is None and '实际FAIL' in why, why)
bad = copy.deepcopy(snap_spx)
bad['gate_a']['status'] = 'DEGRADED'
got, why = rp.gate_status(bad)
check("核心实际FAIL+声明DEGRADED→拒绝(核心问题必须判FAIL)",
      got is None and '实际FAIL' in why, why)
got, why = rp.gate_status(snap_deg)
check("非核心FAIL+声明DEGRADED(builder写入)→合法降级DEGRADED",
      got == 'DEGRADED' and rp.gate_allows_formal_research(got), f"{got} {why}")
bad = copy.deepcopy(snap_miss)
bad['gate_a']['core_missing'] = []   # 核心缺失未如实写入清单
got, why = rp.gate_status(bad)
check("核心缺失但core_missing清单隐瞒→拒绝", got is None and 'core_missing' in why, why)
bad = copy.deepcopy(RE_PASS)
bad['quality'] = dict(bad.get('quality') or {}, counts={'PASS': 99, 'DEGRADED': 0, 'FAIL': 0})
got, why = rp.gate_status(bad)
check("quality.counts与事实重计冲突→拒绝", got is None and 'counts' in why, why)
bad = copy.deepcopy(RE_PASS)
bad.setdefault('quality', {})['overall'] = 'FAIL'
got, why = rp.gate_status(bad)
check("quality.overall与事实重计冲突→拒绝(overall≠status但须自洽)",
      got is None and 'overall' in why, why)
dup_decl = copy.deepcopy(snap_dup)
dup_decl['gate_a'] = {'status': 'FAIL', 'core_missing': [], 'core_fail': []}
got, why = rp.gate_status(dup_decl)
check("重复metric_id+声明FAIL(如实)→FAIL(清单不涉重复项,由重算裁决)",
      got == 'FAIL', f"{got} {why}")
bad = copy.deepcopy(RE_PASS)
bad['gate_a']['status'] = 'DEGRADED'   # 全PASS事实+声明DEGRADED=矛盾
got, why = rp.gate_status(bad)
check("全PASS事实+声明DEGRADED→拒绝(声明不得劣于事实)", got is None, f"{got} {why}")

# ════════════════════════════════════════════════════════════════════
# FIX2-03 步骤依赖与报告授权(IA-DEF-003)
# ════════════════════════════════════════════════════════════════════
print("\n── 3. 步骤依赖与报告授权(FIX2-03/IA-DEF-003)")


def run_pipeline_main(td, fail_scripts=(), snapshot=None):
    executed = []

    def fake_run_step(step_name, script_name, timeout=900, script_dir=None):
        executed.append(script_name)
        return script_name not in fail_scripts

    with mock.patch.object(run_weekly, 'PROJECT_DIR', td), \
         mock.patch.object(run_weekly, 'SCRIPTS_DIR', os.path.join(td, 'scripts')), \
         mock.patch.object(run_weekly, 'datetime', _FakeDT), \
         mock.patch.object(run_weekly, 'run_step', fake_run_step):
        if snapshot is not None:
            dd = os.path.join(td, 'data', 'daily')
            os.makedirs(dd, exist_ok=True)
            with open(os.path.join(dd, snapshot['snapshot_id'] + '.json'), 'w',
                      encoding='utf-8') as f:
                json.dump(snapshot, f, ensure_ascii=False)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                run_weekly.main()
            code = 0
        except SystemExit as e:
            code = e.code
    ledger = None
    lps = glob.glob(os.path.join(td, 'logs', 'pipeline_run_*.json'))
    if lps:
        ledger = json.load(open(lps[0], encoding='utf-8'))
    return code, executed, ledger


ALL_CRITICAL = ['global_market_collector.py', 'china_market_collector.py',
                'macro_collector.py', 'rate_expectations.py']
for collector in ALL_CRITICAL:
    with tempfile.TemporaryDirectory() as td:
        code, executed, ledger = run_pipeline_main(td, fail_scripts={collector})
        skipped = {s['name']: s.get('skip_reason') for s in ledger['steps'] if s['skipped']}
        check(f"{collector}失败→exit 1+评分卡/装配/校验SKIPPED+台账留原因",
              code == 1 and 'data_assembler.py' not in executed
              and 'data_validator.py' not in executed
              and 'macro_scorecard.py' not in executed
              and all(skipped.values()) and len(skipped) >= 3,
              str(sorted(skipped)))
with tempfile.TemporaryDirectory() as td:
    # Gate A FAIL快照在场(步骤全成)→allow_formal_report=False
    snap = quiet(fixt.real_snapshot, DAY, gate='FAIL')
    code, executed, ledger = run_pipeline_main(td, snapshot=snap)
    check("Gate A FAIL日: allow_formal_report=False(步骤成功不构成放行依据)",
          code == 0 and ledger.get('allow_formal_report') is False
          and ledger.get('gate_a') == 'FAIL' and ledger.get('snapshot_id'),
          f"exit={code} allow={ledger.get('allow_formal_report')} gate={ledger.get('gate_a')}")
with tempfile.TemporaryDirectory() as td:
    # 评分卡(关键)失败→装配/校验SKIPPED(FIX2-03新依赖)+allow=False
    code, executed, ledger = run_pipeline_main(td, fail_scripts={'macro_scorecard.py'},
                                               snapshot=copy.deepcopy(RE_PASS))
    skipped = {s['name'] for s in ledger['steps'] if s['skipped']}
    all_reasons = [s.get('skip_reason') for s in ledger['steps'] if s['skipped']]
    check("评分卡失败→装配/校验SKIPPED(不得用旧评分冒充当日)+allow=False",
          code == 1 and 'data_assembler.py' not in executed
          and 'data_validator.py' not in executed
          and any('数据汇总打包' in n for n in skipped)
          and any('数据校验与锚点生成' in n for n in skipped)
          and ledger.get('allow_formal_report') is False,
          str(sorted(skipped)))
    check("评分卡SKIPPED原因可追溯(装配/校验的跳过原因点名评分卡上游)",
          any('评分卡' in (r or '') for r in all_reasons), str(all_reasons))
with tempfile.TemporaryDirectory() as td:
    # 装配器失败→校验SKIPPED(依赖链)
    code, executed, ledger = run_pipeline_main(td, fail_scripts={'data_assembler.py'},
                                               snapshot=copy.deepcopy(RE_PASS))
    check("装配器失败→校验SKIPPED+allow=False",
          code == 1 and 'data_validator.py' not in executed
          and ledger.get('allow_formal_report') is False)
with tempfile.TemporaryDirectory() as td:
    # 校验器失败→allow=False(评分卡/装配虽成,关键链不完整)
    code, executed, ledger = run_pipeline_main(td, fail_scripts={'data_validator.py'},
                                               snapshot=copy.deepcopy(RE_PASS))
    check("校验器失败→allow=False(证据链不完整不放行)",
          code == 1 and 'data_validator.py' in executed
          and ledger.get('allow_formal_report') is False)
with tempfile.TemporaryDirectory() as td:
    # 非关键(新闻)失败→降级运行: 正式步骤照常+观察记录不被阻止
    code, executed, ledger = run_pipeline_main(td, fail_scripts={'news_collector.py'},
                                               snapshot=copy.deepcopy(RE_PASS))
    check("新闻失败(非关键)→exit 0+装配/校验/观察照常+allow=True",
          code == 0 and 'data_assembler.py' in executed
          and 'data_validator.py' in executed
          and 'daily_prediction_observer.py' in executed
          and ledger.get('allow_formal_report') is True, f"exit={code}")
with tempfile.TemporaryDirectory() as td:
    # 非关键(相关性)失败→同上
    code, executed, ledger = run_pipeline_main(td,
                                               fail_scripts={'correlation_calculator.py'},
                                               snapshot=copy.deepcopy(RE_PASS))
    check("相关性失败(非关键)→exit 0+allow=True(观察不被阻止)",
          code == 0 and 'daily_prediction_observer.py' in executed
          and ledger.get('allow_formal_report') is True, f"exit={code}")
with tempfile.TemporaryDirectory() as td:
    # 合法DEGRADED日(步骤全成)→allow=True(保留合理降级研究能力)
    snap = quiet(fixt.real_snapshot, DAY, gate='DEGRADED')
    code, executed, ledger = run_pipeline_main(td, snapshot=snap)
    check("合法DEGRADED日→allow_formal_report=True(降级不等于禁止)",
          code == 0 and ledger.get('allow_formal_report') is True
          and ledger.get('gate_a') == 'DEGRADED')

# 报告入口: 旧评分卡/评分缺失的当日,文件存在也不得放行
with tempfile.TemporaryDirectory() as td:
    fixt.build_full_day(td, DAY, stale_scorecard_date='20261023')
    with mock.patch.object(rg, 'DATA_DIR', os.path.join(td, 'data')):
        ok, problems, _ = rg.verify_research_inputs(DAY)
    check("仅旧评分卡(滞后1天)→报告入口拒绝(pack meta scorecard_current=False)",
          not ok and any('评分卡' in p for p in problems), str(problems))
    pack = open(os.path.join(td, 'data', 'weekly', f'data_pack_{DAY}.md'),
                encoding='utf-8').read()
    check("旧评分在包内仅为【历史参考】标注(不冒充当日成功评分)",
          '历史参考' in pack and '非本期评分' in pack)
with tempfile.TemporaryDirectory() as td:
    fixt.build_full_day(td, DAY, skip=('scorecard',))
    with mock.patch.object(rg, 'DATA_DIR', os.path.join(td, 'data')):
        ok, problems, _ = rg.verify_research_inputs(DAY)
    check("当日评分缺失→报告入口拒绝+包内显式披露缺失",
          not ok and any('评分卡' in p for p in problems), str(problems))
    pack = open(os.path.join(td, 'data', 'weekly', f'data_pack_{DAY}.md'),
                encoding='utf-8').read()
    check("包内披露'评分卡缺失'", '评分卡缺失' in pack)
with tempfile.TemporaryDirectory() as td:
    # 当日快照FAIL+残留旧包→入口拒绝(Gate A优先)
    fixt.build_full_day(td, DAY, gate='FAIL')
    with mock.patch.object(rg, 'DATA_DIR', os.path.join(td, 'data')):
        ok, problems, _ = rg.verify_research_inputs(DAY)
    check("Gate A FAIL日残留旧包→报告入口拒绝", not ok, str(problems[:2]))

# ════════════════════════════════════════════════════════════════════
# FIX2-04 快照版本规范(文件系统级选择器)
# ════════════════════════════════════════════════════════════════════
print("\n── 4. 快照版本规范(FIX2-04/IA-DEF-004)")


def write_snap(td, name, snap):
    with open(os.path.join(td, name), 'w', encoding='utf-8') as f:
        json.dump(snap, f, ensure_ascii=False)


def variant(rev=None, sid=None, target=DAY):
    s = copy.deepcopy(RE_PASS)
    if sid:
        s['snapshot_id'] = sid
    elif rev:
        s['snapshot_id'] = f'research_snapshot_{DAY}_v{rev}'
    if target != DAY:
        s['target_date'] = target
    return s


with tempfile.TemporaryDirectory() as td:
    write_snap(td, 'research_snapshot_20261024.json', variant())
    snap, path = rp.select_snapshot(DAY, td)
    check("仅base→选base", snap is not None
          and snap['snapshot_id'] == 'research_snapshot_20261024', str(path))
with tempfile.TemporaryDirectory() as td:
    write_snap(td, 'research_snapshot_20261024.json', variant())
    write_snap(td, 'research_snapshot_20261024_v2.json', variant(rev=2))
    snap, path = rp.select_snapshot(DAY, td)
    check("base+_v2(规范)→确定性取_v2", snap['snapshot_id']
          == 'research_snapshot_20261024_v2', str(path))
with tempfile.TemporaryDirectory() as td:
    write_snap(td, 'research_snapshot_20261024.json', variant())
    write_snap(td, 'research_snapshot_20261024_v2.json', variant(rev=2))
    write_snap(td, 'research_snapshot_20261024_v3.json', variant(rev=3))
    snap, path = rp.select_snapshot(DAY, td)
    check("base+_v2+_v3→最高修订版_v3(保留既有规则)",
          snap['snapshot_id'] == 'research_snapshot_20261024_v3', str(path))
for bad_name in ('research_snapshot_20261024_v0.json',
                 'research_snapshot_20261024_v00.json',
                 'research_snapshot_20261024_v1.json',
                 'research_snapshot_20261024_v01.json',
                 'research_snapshot_20261024_v02.json'):
    with tempfile.TemporaryDirectory() as td:
        write_snap(td, 'research_snapshot_20261024.json', variant())
        write_snap(td, bad_name, variant(sid=bad_name[:-5]))
        snap, why = rp.select_snapshot(DAY, td)
        check(f"非法版本{os.path.basename(bad_name)}→整日拒绝(不静默忽略,不回退base)",
              snap is None and '非法版本' in why, why)
with tempfile.TemporaryDirectory() as td:
    write_snap(td, 'research_snapshot_20261024_v2.json',
               variant(sid='research_snapshot_20261024'))   # 文件名↔ID冲突
    snap, why = rp.select_snapshot(DAY, td)
    check("文件名_v2但内部自称base→整日拒绝(身份冲突)", snap is None
          and 'snapshot_id' in why, why)
with tempfile.TemporaryDirectory() as td:
    write_snap(td, 'research_snapshot_20261024_v2.json', variant(rev=2, target='20261010'))
    snap, why = rp.select_snapshot(DAY, td)
    check("_v2内部target_date不符→拒绝", snap is None and 'target_date' in why, why)
with tempfile.TemporaryDirectory() as td:
    write_snap(td, 'research_snapshot_20261024_v2.json', variant(rev=2))
    with open(os.path.join(td, 'research_snapshot_20261024_v3.json'), 'w') as f:
        f.write('{corrupt')   # 最高版损坏→整日拒绝(不猜测降级取_v2)
    snap, why = rp.select_snapshot(DAY, td)
    check("最高修订版损坏→整日拒绝(不猜测回退次高版)", snap is None
          and '不可解析' in why, why)
with tempfile.TemporaryDirectory() as td:
    # 不可变性: 同日重建base→CLI拒绝(exit 3); --allow-revision产_v2
    daily = os.path.join(td, 'daily')
    os.makedirs(daily)
    fixt.write_collectors(daily, DAY)
    quiet(sb.build_snapshot, target_ymd=DAY, data_dir=daily, out_dir=daily,
          trusted_root=td, as_of=AS_OF)
    r = subprocess_run([PY, os.path.join(ROOT, 'scripts', 'snapshot_builder.py'),
                        '--date', DAY, '--data-dir', daily, '--out-dir', daily,
                        '--trusted-root', td])
    check("同日重建base→exit 3(不可变,不覆盖)", r == 3, f"exit={r}")
    r2 = subprocess_run([PY, os.path.join(ROOT, 'scripts', 'snapshot_builder.py'),
                         '--date', DAY, '--data-dir', daily, '--out-dir', daily,
                         '--trusted-root', td,
                         '--allow-revision', '--revision-reason', 'FIX2测试修订'])
    check("--allow-revision→exit 0且产_v2(base保留)",
          r2 == 0 and os.path.exists(os.path.join(daily, f'research_snapshot_{DAY}_v2.json'))
          and os.path.exists(os.path.join(daily, f'research_snapshot_{DAY}.json')),
          f"exit={r2}")

# ════════════════════════════════════════════════════════════════════
# FIX2-05 锚点来源元数据完整一致(IA-DEF-005)
# ════════════════════════════════════════════════════════════════════
print("\n── 5. 来源元数据完整一致(FIX2-05/IA-DEF-005)")
with tempfile.TemporaryDirectory() as td:
    fixt.build_full_day(td, DAY)
    apath = os.path.join(td, 'data', 'daily', f'anchors_{DAY}.json')
    ok, reason = rp.verify_anchor_batch(apath, anchors_date=DAY, trusted_root=td)
    check("基线: 真实构建锚点批次核验通过", ok, reason)
    meta0 = rp.load_meta(apath)
    for field in ('target_date', 'snapshot_id', 'snapshot_digest', 'anchors_digest',
                  'gate_a'):
        meta = dict(meta0)
        meta.pop(field, None)
        rp.write_meta(apath, meta)
        ok, reason = rp.verify_anchor_batch(apath, anchors_date=DAY, trusted_root=td)
        check(f"meta缺{field}→拒绝(必需字段完整性)", ok is False and field in reason,
              reason)
    meta = dict(meta0, target_date='20261010')
    rp.write_meta(apath, meta)
    ok, reason = rp.verify_anchor_batch(apath, anchors_date=DAY, trusted_root=td)
    check("meta.target_date≠请求日期→拒绝(日期三方一致)", ok is False
          and ('冲突' in reason or '不一致' in reason), reason)
    rp.write_meta(apath, meta0)
    ok, reason = rp.verify_anchor_batch(apath, anchors_date='20261023', trusted_root=td)
    check("请求日期≠锚点文件名日期→拒绝", ok is False
          and ('文件名' in reason or '日期' in reason), reason)
    rp.write_meta(apath, meta0)
    ok, reason = rp.verify_anchor_batch(apath, anchors_date=DAY, trusted_root=td)
    check("基线复归: 恢复meta后核验通过", ok, reason)
with tempfile.TemporaryDirectory() as td:
    fixt.build_full_day(td, DAY, gate='DEGRADED')
    apath = os.path.join(td, 'data', 'daily', f'anchors_{DAY}.json')
    ok, reason = rp.verify_anchor_batch(apath, anchors_date=DAY, trusted_root=td)
    check("DEGRADED批次(权威一致)→核验通过", ok, reason)
    meta = rp.load_meta(apath)
    rp.write_meta(apath, dict(meta, gate_a='PASS'))
    ok, reason = rp.verify_anchor_batch(apath, anchors_date=DAY, trusted_root=td)
    check("meta.gate_a谎报PASS(权威DEGRADED)→拒绝", ok is False, reason)
    rp.write_meta(apath, dict(meta, gate_a='FAIL'))
    ok, reason = rp.verify_anchor_batch(apath, anchors_date=DAY, trusted_root=td)
    check("meta.gate_a=FAIL(即便与权威一致)→拒绝(FAIL批次不入正式链)",
          ok is False, reason)
    rp.write_meta(apath, dict(meta, snapshot_digest='deadbeefdeadbeef'))
    ok, reason = rp.verify_anchor_batch(apath, anchors_date=DAY, trusted_root=td)
    check("meta快照digest与权威快照实际内容不符→拒绝(无条件重算)",
          ok is False, reason)
    rp.write_meta(apath, dict(meta, anchors_digest='deadbeefdeadbeef'))
    ok, reason = rp.verify_anchor_batch(apath, anchors_date=DAY, trusted_root=td)
    check("meta锚点digest与锚点文件实际字节不符→拒绝", ok is False, reason)
    rp.write_meta(apath, meta)
    anchors = json.load(open(apath, encoding='utf-8'))
    keys = [k for k in sorted(anchors) if isinstance(anchors[k].get('value'), (int, float))]
    k0 = keys[0]
    anchors[k0]['value'] = (anchors[k0].get('value') or 0) + 1e-6
    with open(apath, 'w', encoding='utf-8') as f:
        json.dump(anchors, f, ensure_ascii=False, indent=1)
    rp.write_meta(apath, dict(meta, anchors_digest=rp.digest_file(apath)))
    ok, reason = rp.verify_anchor_batch(apath, anchors_date=DAY, trusted_root=td)
    check("锚点数字被改+meta摘要同步改→仍拒绝(权威快照确定性重建)",
          ok is False, reason)

# ════════════════════════════════════════════════════════════════════
# §11 兼容项: 月报/季报/遗留日报
# ════════════════════════════════════════════════════════════════════
print("\n── 6. 兼容项(§11): 月报/季报/遗留日报")
import monthly_review as mr       # noqa: E402
import quarterly_outlook as qo    # noqa: E402
# 遗留日报入口import面要求env_config提供DEEPSEEK三键(dev桩仅含API_KEY;
# 生产env_config为本地文件不入库)。测试内对**已加载模块对象**注入空值完成
# 离线行为验证——不修改env_config.py文件,不引入真实密钥。
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
    glm = _GLMRecorder()
    with mock.patch.object(mr, 'ROOT_DIR', td), \
         mock.patch.object(mr, 'DATA_DIR', os.path.join(td, 'data', 'daily')), \
         mock.patch.object(mr, 'OUTPUT_DIR', mdir), \
         mock.patch.object(rg, 'load_prompt', lambda *a, **kw: '系统提示'), \
         mock.patch.object(rg, '_call_glm', glm), \
         mock.patch.object(sys, 'argv', ['monthly_review.py', '--month', '202609',
                                         '--dry-run']):
        quiet(mr.main)
    check("月报dry-run离线: 数据块落盘+零GLM调用",
          os.path.exists(os.path.join(mdir, 'monthly_data_202609.md')) and glm.calls == 0)
    with mock.patch.object(mr, 'ROOT_DIR', td), \
         mock.patch.object(mr, 'DATA_DIR', os.path.join(td, 'data', 'daily')), \
         mock.patch.object(mr, 'OUTPUT_DIR', mdir), \
         mock.patch.object(rg, 'load_prompt', lambda *a, **kw: '系统提示'), \
         mock.patch.object(rg, '_call_glm', glm), \
         mock.patch.object(sys, 'argv', ['monthly_review.py', '--month', '202609']):
        quiet(mr.main)
    draft = os.path.join(mdir, 'monthly_review_202609_UNVALIDATED.md')
    text = open(draft, encoding='utf-8').read()
    check("月报正式路径输出=UNVALIDATED草稿(不占用合格正式名)+可见横幅",
          os.path.exists(draft) and 'UNVALIDATED 研究草稿' in text
          and not os.path.exists(os.path.join(mdir, 'monthly_review_202609.md')))
    check("月报历史装配保留(dry-run与正式路径共用monthly_data,GLM仅正式路径1次)",
          glm.calls == 1)
with tempfile.TemporaryDirectory() as td:
    os.makedirs(os.path.join(td, 'data', 'daily'))
    qdir = os.path.join(td, 'output', 'quarterly')
    glm = _GLMRecorder()
    with mock.patch.object(qo, 'ROOT_DIR', td), \
         mock.patch.object(qo, 'DATA_DIR', os.path.join(td, 'data', 'daily')), \
         mock.patch.object(qo, 'OUTPUT_DIR', qdir), \
         mock.patch.object(rg, 'load_prompt', lambda *a, **kw: '系统提示'), \
         mock.patch.object(rg, '_call_glm', glm), \
         mock.patch.object(sys, 'argv', ['quarterly_outlook.py', '--quarter', '2026Q3',
                                         '--dry-run']):
        quiet(qo.main)
    check("季报dry-run离线: 数据块落盘+零GLM调用",
          os.path.exists(os.path.join(qdir, 'quarterly_data_2026Q3.md'))
          and glm.calls == 0)
with tempfile.TemporaryDirectory() as td:
    # 遗留日报: 产物自证UNVALIDATED身份,不得被误认合格
    out = os.path.join(td, 'daily')
    with mock.patch.object(drg, 'OUTPUT_DIR', out), \
         mock.patch.object(drg, 'datetime', _FakeDT):
        quiet(drg.save_daily_report, 'SYNTHETIC日报正文。' * 80)
    files = glob.glob(os.path.join(out, 'daily_*.md'))
    text = open(files[0], encoding='utf-8').read()
    check("遗留日报: 文件名daily_YYYYMMDD(不与weekly_report合格名冲突)",
          os.path.basename(files[0]) == f'daily_{DAY}.md', str(files))
    check("遗留日报: HTML注释+可见UNVALIDATED横幅双重自证",
          '<!-- UNVALIDATED legacy' in text and 'UNVALIDATED 遗留日报' in text)
    check("遗留日报: 不匹配任何weekly_report合格报告glob",
          not glob.glob(os.path.join(out, 'weekly_report*')))

# ═══ 汇总 ═══════════════════════════════════════════════════════════
print("\n" + "=" * 64)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 64)
sys.exit(1 if FAIL else 0)
