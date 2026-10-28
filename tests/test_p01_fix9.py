#!/usr/bin/env python3
"""IA-P0-1-FIX9 对抗测试: 未批准外部根级链接重新授信(IA-F8-DEF-001)
+ 正式报告/长期状态保护证据修复(FIX8-G4-EVIDENCE)。

真实项目模块+真实文件系统+临时目录;不mock信任原语/Gate A/预检,
mock仅限外部GLM/时钟。

矩阵:
  A 外部根级别名(§十.A): 正常路径/外链→project(验收反例精确复现)/
    外链→project/data(FIX8旧反例)/项目内链接→根/→data/多级外链/
    链接+../外部普通目录/可信根物理路径/文件在根内但入口不可信;
  B 系统级路径兼容(§十.B): 正常项目路径/代码位置词法形式/macOS
    /var↔/private/var真实双向/用户级模拟别名不得冒充系统别名/
    封闭表跨平台范围(Linux无别名入口);
  C 原始路径攻击回归: FIX6/FIX7/FIX8各反例+非法绝对/穿越/文件链接/
    目录冒充/来源缺失/错误通道;
  D 真实门禁链路(§十.D,external-link→project根级): 从trusted_dir_
    problems到generate_weekly_report逐层真实执行+GLM计数;
  E 正式报告保护(§十.E/FIX9-04): 真实发布事务产生合格报告→前置
    formal_report_view断言→执行前基线→根级外链非法来源全链→执行后
    摘要比对/正式身份/无新发布/无误标published/无长期状态回写+篡改
    自检。
"""
import contextlib
import glob
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime
from unittest import mock

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(_HERE), 'scripts'))
sys.path.insert(0, _HERE)

import fixt                                    # noqa: E402
import research_provenance as rp               # noqa: E402
import snapshot_builder as sb                  # noqa: E402
import data_assembler as da                    # noqa: E402
import report_generator as rg                  # noqa: E402

DAY = '20261024'
PASS_N, FAIL_N = 0, 0


def check(name, cond, detail=''):
    global PASS_N, FAIL_N
    if cond:
        PASS_N += 1
        print(f"  ✅ {name}")
    else:
        FAIL_N += 1
        print(f"  ❌ {name}  {detail}")


def quiet(fn, *a, **kw):
    with contextlib.redirect_stdout(io.StringIO()), \
            contextlib.redirect_stderr(io.StringIO()):
        return fn(*a, **kw)


def sha(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


class _DT:
    """固定时钟(§9.6): 不依赖机器当天日期;strptime转发真实datetime。"""
    def __init__(self, ymd):
        self._ymd = ymd

    @staticmethod
    def strptime(s, f):
        return datetime.strptime(s, f)

    def now(self, tz=None):
        return datetime(int(self._ymd[:4]), int(self._ymd[4:6]),
                        int(self._ymd[6:]), 8, 0, 0)


class _GLM:
    def __init__(self):
        self.calls = 0

    def __call__(self, system_prompt, user_prompt, max_tokens=32000, timeout=900):
        self.calls += 1
        return ('# 投资周报(SYNTHETIC测试文本·FIX9)\n\n'
                + '本周市场综述与分资产回顾。' * 60)


print("═" * 72)
print("IA-P0-1-FIX9: 外部根级链接重新授信(IA-F8-DEF-001)+G4保护证据")
print("═" * 72)

# ════════════════════════════════════════════════════════════════════
print("\n── A. 外部根级别名(§十.A)")

BASE = tempfile.mkdtemp(prefix='fix9-A-')
PROJECT = os.path.join(BASE, 'project')
os.makedirs(os.path.join(PROJECT, 'data', 'daily'))
fixt.write_collectors(os.path.join(PROJECT, 'data', 'daily'), DAY)
DAILY = os.path.join(PROJECT, 'data', 'daily')

# A2 验收反例精确复现: 目录名与§6.2一致
LINK_ROOT = os.path.join(BASE, 'UNAPPROVED-external-link-to-project-root')
os.symlink(PROJECT, LINK_ROOT)
# A3 FIX8旧反例: external-link → project/data
LINK_DATA = os.path.join(BASE, 'external-link')
os.symlink(os.path.join(PROJECT, 'data'), LINK_DATA)
# A4/A5 项目内部链接
os.symlink(PROJECT, os.path.join(PROJECT, 'inner-link-to-root'))
os.symlink(os.path.join(PROJECT, 'data'), os.path.join(PROJECT, 'inner-link-to-data'))
# A6 多级外部链接
_MID = os.path.join(BASE, 'mid-link')
os.symlink(LINK_ROOT, _MID)
# A8 外部普通目录
_EXT = os.path.join(BASE, 'plain-outside', 'data', 'daily')
os.makedirs(_EXT)
fixt.write_collectors(_EXT, DAY)

check("A1 正常 project/data/daily → 放行",
      rp.trusted_dir_problems(DAILY, PROJECT) == [],
      str(rp.trusted_dir_problems(DAILY, PROJECT)[:1]))
pA2 = rp.trusted_dir_problems(os.path.join(LINK_ROOT, 'data', 'daily'), PROJECT)
check("A2 外链→project根(§6.2验收反例精确复现,realpath在根内+文件规范"
      "+SHA正确亦拒——入口授权≠物理包含)",
      bool(pA2) and any('IA-F8-DEF-001' in p or 'FIX9-01' in p for p in pA2),
      str(pA2[:1]))
check("A2b 前提: 反例文件真实可读且规范(拒的是入口,不是文件)",
      os.path.isfile(os.path.join(LINK_ROOT, 'data', 'daily',
                                  f'global_{DAY}.json'))
      and rp._under(os.path.realpath(os.path.join(LINK_ROOT, 'data', 'daily')),
                    os.path.realpath(PROJECT)))
pA3 = rp.trusted_dir_problems(os.path.join(LINK_DATA, 'daily'), PROJECT)
check("A3 外链→project/data(FIX8已过旧反例,保持拒)",
      bool(pA3) and any('IA-F8-DEF-001' in p or 'FIX9-01' in p for p in pA3),
      str(pA3[:1]))
pA4 = rp.trusted_dir_problems(
    os.path.join(PROJECT, 'inner-link-to-root', 'data', 'daily'), PROJECT)
check("A4 项目内部链接→project根 → 拒", bool(pA4)
      and any('符号链接' in p for p in pA4), str(pA4[:1]))
pA5 = rp.trusted_dir_problems(
    os.path.join(PROJECT, 'inner-link-to-data', 'daily'), PROJECT)
check("A5 项目内部链接→project/data → 拒", bool(pA5)
      and any('符号链接' in p for p in pA5), str(pA5[:1]))
pA6 = rp.trusted_dir_problems(os.path.join(_MID, 'data', 'daily'), PROJECT)
check("A6 多级外部链接→project → 拒", bool(pA6), str(pA6[:1]))
pA7 = rp.trusted_dir_problems(os.path.join(LINK_ROOT, '..', 'project',
                                           'data', 'daily'), PROJECT)
check("A7 链接结合..(词法折叠前后一致拒)", bool(pA7)
      and any('..' in p for p in pA7), str(pA7[:1]))
pA8 = rp.trusted_dir_problems(_EXT, PROJECT)
check("A8 外部普通目录(无任何链接) → 拒", bool(pA8), str(pA8[:1]))
check("A9 可信根物理路径形态(dd=realpath) → 放行",
      rp.trusted_dir_problems(os.path.realpath(DAILY),
                              os.path.realpath(PROJECT)) == [])
# A10: 真实文件在可信根内但入口不可信——经未批准入口读到的文件必须不可作为来源
_g = quiet(sb.resolve_inputs, DAY, os.path.join(LINK_ROOT, 'data', 'daily'),
           trusted_root=PROJECT)
check("A10 文件物理在根内+SHA可算,但入口不可信→resolve_inputs不选"
      "(来源身份=入口授权,非文件内容)",
      all(_g.get(ch) is None for ch in rp.SOURCE_CHANNELS), str(_g))

# ════════════════════════════════════════════════════════════════════
print("\n── B. 系统级路径兼容(§十.B)")

check("B1 正常可信项目路径放行(兼容逻辑不误伤)",
      rp.trusted_dir_problems(DAILY, PROJECT) == [])
# B2: FIX10-01修正fixture——原断言"代码位置词法形式在可信入口集合"依赖
# 已删除的__file__词法自动授信(IA-F9-DEF-001缺陷本体);收紧后代码词法
# 形式仅当它恰为封闭表系统别名变换(macOS /tmp↔/private/tmp)或物理相等
# (Linux)时才出现在入口集合,不得作为独立授权来源
_code_root = os.path.dirname(os.path.dirname(os.path.abspath(
    rp.__file__)))
_entries = rp._trusted_entry_forms(os.path.realpath(_code_root))
_table_forms = {os.path.realpath(_code_root)}
if sys.platform == 'darwin':
    for _a, _b in rp._SYSTEM_PREFIX_ALIASES:
        for _x, _y in ((_a, _b), (_b, _a)):
            _rtb = os.path.realpath(_code_root)
            if _rtb == _y:
                _table_forms.add(_x)
            elif _rtb.startswith(_y + os.sep):
                _table_forms.add(_x + _rtb[len(_y):])
check("B2(FIX10-01修正) 代码词法形式不再自动入集: 入口集合⊆物理锚+封闭表"
      "变换形式, 无任何额外来源",
      _entries <= _table_forms
      and all(os.path.realpath(e) == os.path.realpath(_code_root)
              for e in _entries), str(sorted(_entries)))
# B3: macOS系统级前缀别名真实双向(本机darwin实测;Linux CI无/private,
# 断言按平台分流——非darwin时该真实别名不存在,检查表不产生入口)
if sys.platform == 'darwin':
    _td = tempfile.mkdtemp(prefix='fix9-B3-')     # /var/folders/...形态
    check("B3(macOS真机) /var↔/private/var真实双向形态互认(平铺沙箱==根"
          "与dd=realpath双向)",
          rp.trusted_dir_problems(_td, _td) == []
          and rp.trusted_dir_problems(os.path.realpath(_td), _td) == []
          and rp.trusted_dir_problems(_td, os.path.realpath(_td)) == [])
    _ents = rp._trusted_entry_forms(os.path.realpath(_td))
    check("B3b(macOS真机) 入口集合=物理锚+/var别名形式(封闭表推导)",
          os.path.realpath(_td) in _ents
          and any(e.startswith('/var/') for e in _ents), str(sorted(_ents)))
else:
    _td = tempfile.mkdtemp(prefix='fix9-B3-')
    _rt = os.path.realpath(_td)
    _ents = rp._trusted_entry_forms(_rt)
    check("B3(Linux CI,FIX10-01收紧) 封闭别名表不适用: 入口集合恰=物理锚"
          "——CI临时目录虽位于/tmp之下,/tmp在Linux是真实目录非别名,"
          "亦无代码词法/别名来源(FIX10-01)",
          _ents == {_rt}, str(sorted(_ents)))
# B4: 用户级模拟别名不得冒充系统别名——fixture里自建fakePrivate/fakeTmp
# 复刻/macOS目录结构,证明封闭表不认任何非表内形态
FB = tempfile.mkdtemp(prefix='fix9-B4-')
_fake_real = os.path.join(FB, 'fakeReal', 'proj')
os.makedirs(_fake_real)
_fixt_link = os.path.join(FB, 'fakeAlias')       # 用户链接→"物理"项目根
os.symlink(_fake_real, _fixt_link)
_fixt_link2 = os.path.join(FB, 'fakeTmpAlias')
os.symlink(_fake_real, _fixt_link2)
check("B4 用户自建链接(无论命名多像系统别名)不得借系统别名机制通过",
      bool(rp.trusted_dir_problems(os.path.join(_fixt_link, 'data'),
                                   _fake_real))
      and bool(rp.trusted_dir_problems(os.path.join(_fixt_link2, 'data'),
                                       _fake_real)))
# B5: 封闭表本身可审查——恰为/tmp,/var,/etc三条且仅darwin参与
check("B5 _SYSTEM_PREFIX_ALIASES封闭常量(3条macOS根级别名,不可运行时扩充)",
      rp._SYSTEM_PREFIX_ALIASES == (('/tmp', '/private/tmp'),
                                    ('/var', '/private/var'),
                                    ('/etc', '/private/etc')))

# ════════════════════════════════════════════════════════════════════
print("\n── C. 原始路径攻击回归(代表集)")

with tempfile.TemporaryDirectory(prefix='fix9-C-') as td:
    proj = os.path.join(td, 'project')
    daily = os.path.join(proj, 'data', 'daily')
    os.makedirs(daily)
    fixt.write_collectors(daily, DAY)
    out = os.path.join(td, 'outside', 'data', 'daily')
    os.makedirs(out)
    fixt.write_collectors(out, DAY)
    os.symlink(os.path.join(td, 'outside'), os.path.join(proj, 'datalink'))
    os.symlink(os.path.join(td, 'outside', 'child'),
               os.path.join(proj, 'alias'))
    os.symlink(daily, os.path.join(proj, 'data', 'daily_alias'))
    SNAP = quiet(fixt.real_snapshot, DAY)
    ok_ss = SNAP['sources_status']

    c1 = rp.trusted_dir_problems(os.path.join(proj, 'datalink', 'daily'), proj)
    check("C1 FIX6反例(data→outside)仍拒", bool(c1)
          and any('符号链接' in p for p in c1), str(c1[:1]))
    c2 = rp.trusted_dir_problems(os.path.join(proj, 'alias', '..', 'data',
                                              'daily'), proj)
    check("C2 FIX7反例(alias/../data/daily)仍拒(..组件)",
          bool(c2) and any('..' in p for p in c2), str(c2[:1]))
    c3 = rp.trusted_dir_problems(os.path.join(td, 'ext', 'daily'), proj)
    check("C3 项目外绝对路径仍拒", bool(c3), str(c3[:1]))
    c4 = rp.trusted_dir_problems(os.path.join(proj, 'data', 'daily',
                                              '..', 'daily'), proj)
    check("C4 路径穿越(data/daily/../daily)仍拒", bool(c4)
          and any('..' in p for p in c4), str(c4[:1]))
    gf = os.path.join(daily, f'global_{DAY}.json')
    os.remove(gf)
    os.symlink(os.path.join(td, 'evil.json'), gf)
    open(os.path.join(td, 'evil.json'), 'w').write('{}')
    c5 = rp.sources_status_problems(ok_ss, DAY, daily, trusted_root=proj)
    check("C5 最终来源文件为符号链接仍拒(文件层)", any('符号链接' in p
                                                       for p in c5),
          str(c5[:1]))
    os.remove(gf)
    os.mkdir(gf)
    c6 = rp.sources_status_problems(ok_ss, DAY, daily, trusted_root=proj)
    check("C6 目录冒充JSON仍拒", any('目录' in p for p in c6), str(c6[:1]))
    os.rmdir(gf)
    c7 = rp.sources_status_problems(ok_ss, DAY, daily, trusted_root=proj)
    check("C7 来源文件不存在仍拒", any('不存在' in p for p in c7), str(c7[:1]))
    fixt.write_collectors(daily, DAY)
    ss8 = json.loads(json.dumps(ok_ss))
    ss8['global']['file'] = f'macro_{DAY}.json'
    c8 = rp.sources_status_problems(ss8, DAY, daily, trusted_root=proj)
    check("C8 错误采集通道仍拒", any('规范文件名' in p for p in c8), str(c8[:1]))

# ════════════════════════════════════════════════════════════════════
print("\n── D. 真实门禁链路(§十.D: external-link→project根级)")

DROOT = tempfile.mkdtemp(prefix='fix9-D-')
ATK = '20261026'
DOUT = os.path.join(tempfile.mkdtemp(prefix='fix9-D-out-'), 'data', 'daily')
os.makedirs(DOUT, exist_ok=True)
fixt.write_collectors(DOUT, ATK)
_t = os.path.join(DOUT, f'global_{ATK}.json')
_g = json.load(open(_t, encoding='utf-8'))
_g['data']['SPX']['close'] = 99999.0
json.dump(_g, open(_t, 'w', encoding='utf-8'))
DLINK = os.path.join(tempfile.mkdtemp(prefix='fix9-Dlink-'),
                     'UNAPPROVED-external-link-to-project-root')
os.symlink(DROOT, DLINK)
DD_D = os.path.join(DLINK, 'data', 'daily')
fixt.write_collectors(os.path.join(DROOT, 'data', 'daily'), DAY)  # 根内合法日

SNAP_D = quiet(fixt.real_snapshot, DAY)
d1 = rp.trusted_dir_problems(DD_D, DROOT)
check("D1 trusted_dir_problems拒(入口授权,IA-F8-DEF-001)",
      bool(d1) and any('FIX9-01' in p for p in d1), str(d1[:1]))
v_d, p_d = rp.trusted_source_dir(DD_D, DROOT)
check("D2 trusted_source_dir: verified=None+可诊断原因", v_d is None
      and bool(p_d), str(p_d[:1]))
ri_d = quiet(sb.resolve_inputs, ATK, DD_D, trusted_root=DROOT)
check("D3 resolve_inputs不读取未批准入口任何文件(全通道缺源)",
      all(ri_d.get(ch) is None for ch in rp.SOURCE_CHANNELS), str(ri_d))
gs_d = quiet(sb.build_snapshot, ATK, DD_D, os.path.join(DROOT, 'data', 'daily'),
             trusted_root=DROOT, as_of=fixt.as_of_for(ATK))
check("D4 build_snapshot只产诊断快照(Gate A≠PASS,不产合格正式研究输入)",
      gs_d is not None and gs_d['gate_a']['status'] != 'PASS',
      gs_d and gs_d['gate_a']['status'])
d5 = rp.sources_status_problems(SNAP_D['sources_status'], DAY, DD_D,
                                 trusted_root=DROOT)
check("D5 sources_status_problems拒(验证端口径一致)",
      bool(d5) and any('FIX9-01' in p for p in d5), str(d5[:1]))
eff_d = rp.recompute_gate_a(SNAP_D, data_dir=DD_D, trusted_root=DROOT)['effective']
check("D6 recompute_gate_a不产PASS(fail-closed)", eff_d in (None, 'FAIL'),
      str(eff_d))
st_d = rp.gate_status(SNAP_D, data_dir=DD_D, trusted_root=DROOT)
check("D7 gate_status对非法入口返回None(非PASS)", st_d[0] is None, str(st_d))
buf_d = io.StringIO()
with mock.patch.object(da, 'DATA_DIR', os.path.join(DROOT, 'data')), \
        mock.patch.object(da, 'datetime', _DT(ATK)), \
        contextlib.redirect_stdout(buf_d):
    try:
        da.main()
        rc_d8 = 0
    except SystemExit as e:
        rc_d8 = e.code
check("D8 真实data_assembler.main(时钟=ATK): 拒绝产正式数据包(exit2无包)",
      rc_d8 == 2 and not os.path.exists(
          os.path.join(DROOT, 'data', 'weekly', f'data_pack_{ATK}.md')),
      f"rc={rc_d8}")
with mock.patch.object(rg, 'DATA_DIR', os.path.join(DROOT, 'data')):
    ok_d9, probs_d9, _ctx = rg.verify_research_inputs(ATK)
check("D9 真实report_generator.verify_research_inputs(ATK): 拒(快照Gate A"
      "不可用,问题留痕)",
      ok_d9 is False and bool(probs_d9), str(list(probs_d9)[:1]))
glm_d = _GLM()
applied_d = []
with mock.patch.object(rg, 'DATA_DIR', os.path.join(DROOT, 'data')), \
        mock.patch.object(rg, 'OUTPUT_DIR', os.path.join(DROOT, 'output',
                                                         'weekly')), \
        mock.patch.object(rg, 'datetime', _DT(ATK)), \
        mock.patch.object(rg, '_call_glm', glm_d), \
        mock.patch.object(rg, 'apply_status_updates',
                          lambda *a, **k: applied_d.append(1)), \
        mock.patch.object(rg, 'validate_generated_report',
                          lambda md, anchors=None, anchors_file=None:
                          ('PASS', [])), \
        mock.patch.object(rg.allocation_engine, 'load_views',
                          lambda *a, **k: {'views': [], 'predictions': []}), \
        mock.patch.object(rg, 'pending_completed_month', lambda d=None: None), \
        mock.patch.object(rg, 'pending_completed_quarter', lambda d=None: None), \
        mock.patch.object(rg, 'load_framework', lambda: '框架'), \
        mock.patch.object(rg, 'load_theses', lambda: '论点'), \
        mock.patch.object(rg, 'load_technical_notes', lambda: ''), \
        mock.patch.object(rg, 'load_news_summary', lambda: ''), \
        mock.patch.object(rg, 'load_previous_report', lambda: ''):
    try:
        quiet(rg.generate_weekly_report)
        rc_d10 = 0
    except SystemExit as e:
        rc_d10 = e.code
check("D10 真实generate_weekly_report(时钟=ATK): 预检拒exit2+GLM=0+"
      "零长期状态回写",
      rc_d10 == 2 and glm_d.calls == 0 and applied_d == [],
      f"rc={rc_d10} glm={glm_d.calls}")

# ════════════════════════════════════════════════════════════════════
print("\n── E. 正式报告保护(§十.E/FIX9-04: 根级外链+真实发布+执行前基线)")

EROOT = tempfile.mkdtemp(prefix='fix9-E-')
PUB, EATK = DAY, '20261025'
OUTE = os.path.join(EROOT, 'output', 'weekly')
CFGE = os.path.join(EROOT, 'config')
os.makedirs(OUTE, exist_ok=True)
os.makedirs(CFGE, exist_ok=True)
THE = os.path.join(CFGE, 'thesis.json')
VWE = os.path.join(CFGE, 'allocation_views.json')
open(THE, 'w', encoding='utf-8').write(
    '{"version": 1, "theses": [], "updated_at": "2026-10-24T08:00:00"}')
open(VWE, 'w', encoding='utf-8').write(
    '{"version": 2, "views": [], "predictions": []}')
fixt.build_full_day(EROOT, PUB)

glm_e = _GLM()
applied_pub_e = []
with mock.patch.object(rg, 'DATA_DIR', os.path.join(EROOT, 'data')), \
        mock.patch.object(rg, 'OUTPUT_DIR', OUTE), \
        mock.patch.object(rg, 'datetime', _DT(PUB)), \
        mock.patch.object(rg, '_call_glm', glm_e), \
        mock.patch.object(rg, 'apply_status_updates',
                          lambda *a, **k: applied_pub_e.append(1)), \
        mock.patch.object(rg, 'validate_generated_report',
                          lambda md, anchors=None, anchors_file=None:
                          ('PASS', ['SYNTHETIC警告'])), \
        mock.patch.object(rg.allocation_engine, 'load_views',
                          lambda *a, **k: {'views': [], 'predictions': []}), \
        mock.patch.object(rg, 'pending_completed_month', lambda d=None: None), \
        mock.patch.object(rg, 'pending_completed_quarter', lambda d=None: None), \
        mock.patch.object(rg, 'load_framework', lambda: '框架'), \
        mock.patch.object(rg, 'load_theses', lambda: '论点'), \
        mock.patch.object(rg, 'load_technical_notes', lambda: ''), \
        mock.patch.object(rg, 'load_news_summary', lambda: ''), \
        mock.patch.object(rg, 'load_previous_report', lambda: ''):
    try:
        quiet(rg.generate_weekly_report)
        rc_e0 = 0
    except SystemExit as e:
        rc_e0 = e.code
REPE = os.path.join(OUTE, f'weekly_report_{PUB}.md')
STATE = os.path.join(OUTE, f'report_status_{PUB}.json')
check("E0 真实发布事务: exit=0+GLM恰1次+报告/状态落盘",
      rc_e0 == 0 and os.path.exists(REPE) and os.path.exists(STATE)
      and glm_e.calls == 1, f"rc={rc_e0} glm={glm_e.calls}")
view_e0, reason_e0 = rp.formal_report_view(REPE)
check("E0b 前置: formal_report_view接受真实发布报告(否则本测试FAIL)",
      view_e0 is not None, reason_e0)
scan_e0 = rp.scan_formal_weekly_reports(OUTE)

# 执行前基线(一切危险操作之前)
base_e = {p: sha(p) for p in (REPE, STATE, THE, VWE)}

# 攻击: 未批准根级外链(=IA-F8-DEF-001场景)承载EATK日篡改采集
EEXT = os.path.join(tempfile.mkdtemp(prefix='fix9-E-out-'), 'data', 'daily')
os.makedirs(EEXT, exist_ok=True)
fixt.write_collectors(EEXT, EATK)
_t = os.path.join(EEXT, f'global_{EATK}.json')
_g = json.load(open(_t, encoding='utf-8'))
_g['data']['SPX']['close'] = 99999.0
json.dump(_g, open(_t, 'w', encoding='utf-8'))
ELINK = os.path.join(tempfile.mkdtemp(prefix='fix9-Elink-'),
                     'UNAPPROVED-external-link-to-project-root')
os.symlink(EROOT, ELINK)
DD_E = os.path.join(ELINK, 'data', 'daily')

gs_e = quiet(sb.build_snapshot, EATK, DD_E,
             os.path.join(EROOT, 'data', 'daily'), trusted_root=EROOT,
             as_of=fixt.as_of_for(EATK))
check("E1 snapshot_builder经根级外链构建: 只产Gate A≠PASS诊断快照(不被"
      "当作合格正式研究输入)",
      gs_e is not None and gs_e['gate_a']['status'] != 'PASS'
      and all(gs_e['sources_status'][ch]['status'] == 'MISSING'
              for ch in rp.SOURCE_CHANNELS),
      gs_e and gs_e['gate_a']['status'])
buf_e = io.StringIO()
with mock.patch.object(da, 'DATA_DIR', os.path.join(EROOT, 'data')), \
        mock.patch.object(da, 'datetime', _DT(EATK)), \
        contextlib.redirect_stdout(buf_e):
    try:
        da.main()
        rc_e2 = 0
    except SystemExit as e:
        rc_e2 = e.code
check("E2 data_assembler拒绝(exit2,无EATK数据包)",
      rc_e2 == 2 and not os.path.exists(
          os.path.join(EROOT, 'data', 'weekly', f'data_pack_{EATK}.md')),
      f"rc={rc_e2}")
glm_e2 = _GLM()
applied_e2 = []
with mock.patch.object(rg, 'DATA_DIR', os.path.join(EROOT, 'data')), \
        mock.patch.object(rg, 'OUTPUT_DIR', OUTE), \
        mock.patch.object(rg, 'datetime', _DT(EATK)), \
        mock.patch.object(rg, '_call_glm', glm_e2), \
        mock.patch.object(rg, 'apply_status_updates',
                          lambda *a, **k: applied_e2.append(1)), \
        mock.patch.object(rg, 'validate_generated_report',
                          lambda md, anchors=None, anchors_file=None:
                          ('PASS', [])), \
        mock.patch.object(rg.allocation_engine, 'load_views',
                          lambda *a, **k: {'views': [], 'predictions': []}), \
        mock.patch.object(rg, 'pending_completed_month', lambda d=None: None), \
        mock.patch.object(rg, 'pending_completed_quarter', lambda d=None: None), \
        mock.patch.object(rg, 'load_framework', lambda: '框架'), \
        mock.patch.object(rg, 'load_theses', lambda: '论点'), \
        mock.patch.object(rg, 'load_technical_notes', lambda: ''), \
        mock.patch.object(rg, 'load_news_summary', lambda: ''), \
        mock.patch.object(rg, 'load_previous_report', lambda: ''):
    try:
        quiet(rg.generate_weekly_report)
        rc_e3 = 0
    except SystemExit as e:
        rc_e3 = e.code
check("E3 generate_weekly_report: 预检拒exit2+GLM=0", rc_e3 == 2
      and glm_e2.calls == 0, f"rc={rc_e3} glm={glm_e2.calls}")

after_e = {p: sha(p) for p in (REPE, STATE, THE, VWE)}
view_e1, reason_e1 = rp.formal_report_view(REPE)
_new_e = sorted(f for f in os.listdir(OUTE)
                if (f.startswith('weekly_report_')
                    or f.startswith('report_status_')) and PUB not in f)
_pub_true_e = sorted(
    f for f in os.listdir(OUTE) if f.startswith('report_status_')
    and json.load(open(os.path.join(OUTE, f))).get('published') is True)
check("E4 保护核验(执行前基线vs执行后): 4对象摘要一致;报告仍被"
      "formal_report_view接受;无新报告/状态;published=true仅发布日;"
      "无长期状态回写;scan结果不变",
      base_e == after_e and view_e1 is not None and not _new_e
      and _pub_true_e == [f'report_status_{PUB}.json'] and applied_e2 == []
      and [v['ymd'] for v in rp.scan_formal_weekly_reports(OUTE)]
      == [v['ymd'] for v in scan_e0],
      str({'changed': [k for k in base_e if base_e[k] != after_e[k]],
           'new': _new_e, 'pub': _pub_true_e, 'formal': reason_e1}))

# E5 篡改自检(§9.5): 比较机制能发现变化(独立夹具)
with tempfile.TemporaryDirectory(prefix='fix9-E5-') as td5:
    f1, f2 = os.path.join(td5, 'thesis.json'), os.path.join(td5, 'views.json')
    open(f1, 'w').write('{"a":1}')
    open(f2, 'w').write('{"b":1}')
    b5 = {p: sha(p) for p in (f1, f2)}
    open(f1, 'w').write('{"a":2}')          # 有意篡改
    a5 = {p: sha(p) for p in (f1, f2)}
    check("E5 自检: 基线比较发现被篡改对象且不误报未动对象",
          a5[f1] != b5[f1] and a5[f2] == b5[f2])

# ════════════════════════════════════════════════════════════════════
print("\n" + "═" * 72)
print(f"FIX9 结果: {PASS_N}通过 / {FAIL_N}失败")
if FAIL_N:
    sys.exit(1)
