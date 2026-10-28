#!/usr/bin/env python3
"""IA-P0-1-FIX8 对抗测试: symlink/..信任检查与真实文件访问不一致(IA-F7-DEF-001)。

真实项目模块(research_provenance/snapshot_builder/data_assembler/
report_generator/daily_prediction_observer/real_data_acceptance)+真实文件
系统+临时目录;不mock被测信任原语/Gate A/预检,mock仅限外部API/GLM/时钟。

矩阵:
  A 原始反例精确复现(§8.1): project/alias→outside/child,传入
    project/alias/../data/daily——normpath后词法在project内(FIX7检查对象)、
    realpath经链接落到outside(真实访问对象)、原始路径确实能读到UNTRUSTED
    字节;折叠形态零问题(=修改前会放行的负向前提);新代码从trusted_dir_
    problems/resolve_inputs/sources_status_problems/recompute_gate_a/
    gate_status逐层拒绝;
  B 外部链接重新入根(§8.2): external-link→project/data,传入external-link/
    daily,realpath物理落点在project内仍拒(FIX8-02禁词法越界后自动重新授信);
  C 原FIX6反例(§8.3): project/data→outside继续拒(不因修新问题放开旧路径);
  D 其他反向矩阵(§8.4): daily链接/文件链接/多级祖先/..各形态/项目外绝对
    目录/目录冒充/文件缺失/非规范名/错误通道/根内链接/根外链接/可信根被
    链接重定向/根不存在/根是文件/'..'组件变体与'a..b'不误判;
  E 原始路径类型(§5.3): None/空/空白/bytes/各类非法类型安全拒;PathLike/
    '.'组件/根内相对路径合法放行;相对路径'..'拒;
  F 正常路径回归(§8-05): 平铺沙箱/项目布局四通道EXACT/FALLBACK+5/7/5/7
    窗口边界/macOS前缀形态双向/非核心缺失DEGRADED/sha256内容绑定保持;
  G 完整正式链路(§8-06): 合格报告+发布状态+论点+观点在档,symlink/..越界
    来源经真实snapshot_builder→data_assembler(exit2无包)→report_generator
    预检拒+GLM=0,四类文件字节前后不变,退出码留痕;
  H 内容绑定回归(§11): FIX7-05 sha256检查未削弱;历史无摘要快照如实跳过;
  I 调用端锚定审计(§7.3): build_markdown参数不再自证授权/观察器缺省锚
    拒沙箱/real_data_acceptance缺省拒+显式--trusted-root放行。
"""
import contextlib
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import glob
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
import daily_prediction_observer as dpo        # noqa: E402
import real_data_acceptance as rda             # noqa: E402

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


print("═" * 72)
print("IA-P0-1-FIX8: symlink/.. 信任检查与真实访问一致性(IA-F7-DEF-001)")
print("═" * 72)

# ════════════════════════════════════════════════════════════════════
print("\n── A. 原始反例精确复现(§8.1: project/alias/../data/daily)")

BASE = tempfile.mkdtemp(prefix='fix8-A-')
PROJECT = os.path.join(BASE, 'project')
OUTSIDE = os.path.join(BASE, 'outside')
os.makedirs(os.path.join(PROJECT, 'data', 'daily'))
os.makedirs(os.path.join(OUTSIDE, 'child'))
os.makedirs(os.path.join(OUTSIDE, 'data', 'daily'))
fixt.write_collectors(os.path.join(PROJECT, 'data', 'daily'), DAY)
fixt.write_collectors(os.path.join(OUTSIDE, 'data', 'daily'), DAY)
# 外部文件植入可辨识篡改值(证明"能读"≠"可信")
_tamper = os.path.join(OUTSIDE, 'data', 'daily', f'global_{DAY}.json')
_d = json.load(open(_tamper, encoding='utf-8'))
_d['data']['SPX']['close'] = 99999.0
json.dump(_d, open(_tamper, 'w', encoding='utf-8'))
os.symlink(os.path.join(OUTSIDE, 'child'), os.path.join(PROJECT, 'alias'))

DD = os.path.join(PROJECT, 'alias', '..', 'data', 'daily')   # 反例原始路径
_norm = os.path.normpath(DD)
_real = os.path.realpath(DD)

check("A1a 前提: normpath(原始路径)词法位于project内(修改前检查对象)",
      rp._under(_norm, PROJECT), _norm)
check("A1b 前提: realpath(原始路径)物理位于outside(真实访问对象)",
      rp._under(_real, os.path.realpath(OUTSIDE)), _real)
_with_alias = os.path.join(DD, f'global_{DAY}.json')
check("A1c 前提: 原始路径确实能访问外部文件(读到UNTRUSTED篡改值99999.0)",
      os.path.isfile(_with_alias)
      and json.load(open(_with_alias, encoding='utf-8'))['data']['SPX']['close'] == 99999.0)
check("A1d 前提(负向基线): 折叠形态normpath(DD)零问题=修改前FIX7代码放行",
      rp.trusted_dir_problems(_norm, PROJECT) == [],
      str(rp.trusted_dir_problems(_norm, PROJECT)[:1]))

pA = rp.trusted_dir_problems(DD, PROJECT)
check("A2 trusted_dir_problems拒绝原始路径(..组件在词法折叠前拒,FIX8-01)",
      bool(pA) and any('..' in p for p in pA), str(pA[:1]))
vA, pA2 = rp.trusted_source_dir(DD, PROJECT)
check("A3 trusted_source_dir: verified=None+可诊断问题(不授予访问路径)",
      vA is None and bool(pA2), str(pA2[:1]))

riA = quiet(sb.resolve_inputs, DAY, DD, trusted_root=PROJECT)
check("A4 resolve_inputs不读取不可信目录任何文件(全通道按缺源)",
      all(riA.get(ch) is None for ch in rp.SOURCE_CHANNELS), str(riA))
riA2 = quiet(sb.resolve_inputs, DAY, DD)     # 缺省可信根(代码位置)
check("A5 resolve_inputs缺省可信根同样fail-closed(测试参数非生产后门)",
      all(riA2.get(ch) is None for ch in rp.SOURCE_CHANNELS), str(riA2))

with tempfile.TemporaryDirectory(prefix='fix8-A-snap-') as td:
    snapA = quiet(sb.build_snapshot, DAY, DD, td, trusted_root=PROJECT,
                  as_of=fixt.as_of_for(DAY))
    sp = os.path.join(td, f'research_snapshot_{DAY}.json')
    check("A6 构建端: symlink/..来源只产诊断快照且Gate A≠PASS(不得形成正式PASS)",
          snapA is not None and os.path.exists(sp)
          and snapA.get('gate_a', {}).get('status') != 'PASS'
          and all(snapA['sources_status'][ch]['status'] == 'MISSING'
                  for ch in rp.SOURCE_CHANNELS),
          str(snapA and snapA.get('gate_a', {}).get('status')))

# 合法快照(SS来自可信project目录)+恶意data_dir复核 → 验证端同规
SNAP = quiet(fixt.real_snapshot, DAY)
_ok_ss = SNAP['sources_status']
pA7 = rp.sources_status_problems(_ok_ss, DAY, DD, trusted_root=PROJECT)
check("A7 sources_status_problems(正式口径)拒绝..路径采集目录",
      bool(pA7) and any('..' in p for p in pA7), str(pA7[:1]))
effA = rp.recompute_gate_a(SNAP, data_dir=DD, trusted_root=PROJECT)['effective']
check("A8 recompute_gate_a: 恶意路径下权威重算不产生PASS(fail-closed)",
      effA in (None, 'FAIL'), str(effA))
stA = rp.gate_status(SNAP, data_dir=DD, trusted_root=PROJECT)
check("A9 gate_status: 声明PASS在恶意路径下不可用(None,不得当PASS)",
      stA[0] is None, str(stA))

# ════════════════════════════════════════════════════════════════════
print("\n── B. 外部链接重新入根(§8.2: external-link→project/data)")

EXT = os.path.join(BASE, 'external-link')
os.symlink(os.path.join(PROJECT, 'data'), EXT)
DDB = os.path.join(EXT, 'daily')
check("B1 前提: realpath(external-link/daily)物理落点在project内"
      "(自动重新授信的诱惑场景)",
      rp._under(os.path.realpath(DDB), os.path.realpath(PROJECT)),
      os.path.realpath(DDB))
pB = rp.trusted_dir_problems(DDB, PROJECT)
check("B2 词法越界后realpath落点在根内不自动授信(FIX8-02)",
      bool(pB) and any('不自动授信' in p for p in pB), str(pB[:1]))
riB = quiet(sb.resolve_inputs, DAY, DDB, trusted_root=PROJECT)
stB = rp.gate_status(SNAP, data_dir=DDB, trusted_root=PROJECT)
check("B3 构建端不选外部链接目录文件+验证端不放行",
      all(riB.get(ch) is None for ch in rp.SOURCE_CHANNELS) and stB[0] is None,
      str(stB))

# ════════════════════════════════════════════════════════════════════
print("\n── C. 原FIX6反例保持(§8.3: project/data→outside)")

with tempfile.TemporaryDirectory(prefix='fix8-C-') as td:
    proj = os.path.join(td, 'project')
    out = os.path.join(td, 'outside')
    os.makedirs(os.path.join(proj, 'datax', 'daily'))
    os.makedirs(os.path.join(out, 'data', 'daily'))
    fixt.write_collectors(os.path.join(out, 'data', 'daily'), DAY)
    os.symlink(out, os.path.join(proj, 'datalink'))       # data→outside
    pC = rp.trusted_dir_problems(os.path.join(proj, 'datalink', 'daily'), proj)
    check("C1 FIX6反例继续拒(祖先链接重定向,不因修新问题放开旧路径)",
          bool(pC) and any('符号链接' in p for p in pC), str(pC[:1]))

# ════════════════════════════════════════════════════════════════════
print("\n── D. 其他反向矩阵(§8.4)")


def _mkproj(td, links=()):
    """td/project/data/daily 四通道齐全;links在project内建链接。"""
    proj = os.path.join(td, 'project')
    daily = os.path.join(proj, 'data', 'daily')
    os.makedirs(daily)
    fixt.write_collectors(daily, DAY)
    return proj, daily


with tempfile.TemporaryDirectory(prefix='fix8-D1-') as td:
    proj, daily = _mkproj(td)
    outd = os.path.join(td, 'out')
    os.makedirs(outd)
    os.symlink(outd, os.path.join(proj, 'data', 'dailylink'))  # daily级链接
    p1 = rp.trusted_dir_problems(os.path.join(proj, 'data', 'dailylink'), proj)
    check("D1 daily目录为符号链接→拒", bool(p1)
          and any('符号链接' in p for p in p1), str(p1[:1]))

with tempfile.TemporaryDirectory(prefix='fix8-D2-') as td:
    proj, daily = _mkproj(td)
    os.remove(os.path.join(daily, f'global_{DAY}.json'))
    os.symlink(os.path.join(td, 'evil.json'),
               os.path.join(daily, f'global_{DAY}.json'))
    open(os.path.join(td, 'evil.json'), 'w').write('{}')
    ss2 = json.loads(json.dumps(_ok_ss))     # 深拷贝合法SS
    p2 = rp.sources_status_problems(ss2, DAY, daily, trusted_root=proj)
    check("D2 最终global文件为符号链接→文件层拒(实体核验经已验证路径)",
          any('符号链接' in p for p in p2), str(p2[:2]))

with tempfile.TemporaryDirectory(prefix='fix8-D3-') as td:
    proj, _daily = _mkproj(td)
    outd = os.path.join(td, 'out', 'deep')
    os.makedirs(outd)
    fixt.write_collectors(outd, DAY)
    os.makedirs(os.path.join(proj, 'x'))
    os.symlink(os.path.join(td, 'out'), os.path.join(proj, 'x', 'y'))  # 多级祖先
    p3 = rp.trusted_dir_problems(os.path.join(proj, 'x', 'y', 'deep'), proj)
    check("D3 多级祖先链接(词法在根内,物理在根外)→拒",
          bool(p3) and any('符号链接' in p for p in p3), str(p3[:1]))

with tempfile.TemporaryDirectory(prefix='fix8-D4-') as td:
    proj, daily = _mkproj(td)
    dd4 = os.path.join(proj, 'data', '..', 'data', 'daily')   # 无害形态../
    p4 = rp.trusted_dir_problems(dd4, proj)
    check("D4 词法无害的data/../data/daily也拒(凡..组件一律拒,FIX8-01)",
          bool(p4) and any('..' in p for p in p4), str(p4[:1]))

with tempfile.TemporaryDirectory(prefix='fix8-D5-') as td:
    proj, daily = _mkproj(td)
    old_cwd = os.getcwd()
    os.chdir(proj)
    try:
        p5 = rp.trusted_dir_problems(os.path.join('alias', '..', 'data', 'daily')
                                     if os.path.exists('alias') else 'data/../daily',
                                     proj)
    finally:
        os.chdir(old_cwd)
    check("D5 相对路径含..→拒(相对形态不豁免穿越组件)",
          bool(p5) and any('..' in p for p in p5), str(p5[:1]))

with tempfile.TemporaryDirectory(prefix='fix8-D6-') as td:
    proj, _ = _mkproj(td)
    other = os.path.join(td, 'other', 'data', 'daily')   # 项目外绝对目录(无链接)
    os.makedirs(other)
    p6 = rp.trusted_dir_problems(other, proj)
    check("D6 项目外绝对目录(无任何链接)→拒(不建外部白名单)",
          bool(p6) and any('不在可信项目根之内' in p for p in p6), str(p6[:1]))

with tempfile.TemporaryDirectory(prefix='fix8-D7-') as td:
    proj, daily = _mkproj(td)
    os.remove(os.path.join(daily, f'global_{DAY}.json'))
    os.mkdir(os.path.join(daily, f'global_{DAY}.json'))     # 目录冒充JSON
    p7 = rp.sources_status_problems(_ok_ss, DAY, daily, trusted_root=proj)
    check("D7 目录冒充JSON采集文件→拒", any('目录' in p for p in p7), str(p7[:2]))

with tempfile.TemporaryDirectory(prefix='fix8-D8-') as td:
    proj, daily = _mkproj(td)
    os.remove(os.path.join(daily, f'china_{DAY}.json'))     # 声明在场实际缺失
    p8 = rp.sources_status_problems(_ok_ss, DAY, daily, trusted_root=proj)
    check("D8 声明EXACT但来源文件不存在→拒", any('不存在' in p for p in p8), str(p8[:2]))

with tempfile.TemporaryDirectory(prefix='fix8-D9-') as td:
    proj, daily = _mkproj(td)
    ss9 = json.loads(json.dumps(_ok_ss))
    ss9['global']['file'] = f'global_{DAY}.json.txt'        # 非规范扩展名
    p9 = rp.sources_status_problems(ss9, DAY, daily, trusted_root=proj)
    check("D9 非规范扩展名→身份层拒", any('规范文件名' in p for p in p9), str(p9[:1]))

with tempfile.TemporaryDirectory(prefix='fix8-D10-') as td:
    proj, daily = _mkproj(td)
    ss10 = json.loads(json.dumps(_ok_ss))
    ss10['global']['file'] = f'macro_{DAY}.json'            # 规范名但错误通道
    p10 = rp.sources_status_problems(ss10, DAY, daily, trusted_root=proj)
    check("D10 规范文件名但错误通道→拒", any('规范文件名' in p for p in p10), str(p10[:1]))

with tempfile.TemporaryDirectory(prefix='fix8-D11-') as td:
    proj, daily = _mkproj(td)
    os.symlink(daily, os.path.join(proj, 'data', 'daily_alias'))  # 根内→根内
    p11 = rp.trusted_dir_problems(os.path.join(proj, 'data', 'daily_alias'), proj)
    check("D11 符号链接指向可信根内其他位置→拒(根内链接同样未经批准)",
          bool(p11) and any('符号链接' in p for p in p11), str(p11[:1]))

with tempfile.TemporaryDirectory(prefix='fix8-D13-') as td:
    proj, daily = _mkproj(td)
    os.symlink(proj, os.path.join(td, 'root-alias'))        # 根本身被链接重定向
    p13 = rp.trusted_dir_problems(daily, os.path.join(td, 'root-alias'))
    check("D13 可信根本身经未经批准链接重定向→拒",
          bool(p13) and any('可信项目根本身是符号链接' in p for p in p13), str(p13[:1]))
    p13b = rp.trusted_dir_problems(daily, os.path.join(td, 'ghost-root'))
    check("D13b 可信根不存在→拒(fail-closed)", bool(p13b), str(p13b[:1]))
    open(os.path.join(td, 'rootfile'), 'w').write('')
    p13c = rp.trusted_dir_problems(daily, os.path.join(td, 'rootfile'))
    check("D13c 可信根是文件而非目录→拒", bool(p13c), str(p13c[:1]))

with tempfile.TemporaryDirectory(prefix='fix8-D16-') as td:
    proj, daily = _mkproj(td)
    os.makedirs(os.path.join(proj, 'a..b', 'daily'))        # 连续两点普通名
    p16a = rp.trusted_dir_problems(os.path.join(proj, 'a..b', 'daily'), proj)
    p16b = rp.trusted_dir_problems(os.path.join(proj, 'data', 'daily', '..'), proj)
    p16c = rp.trusted_dir_problems('..', proj)
    check("D16 '..组件'按路径组件精确判定: a..b目录名不误判;尾随..与裸..拒",
          p16a == [] and bool(p16b) and bool(p16c),
          f"{p16a[:1]} | {p16b[:1]} | {p16c[:1]}")

# ════════════════════════════════════════════════════════════════════
print("\n── E. 原始路径类型与合法形态(§5.3)")

with tempfile.TemporaryDirectory(prefix='fix8-E-') as td:
    proj, daily = _mkproj(td)
    ok_types = all(rp.trusted_dir_problems(v, proj) for v in
                   [None, '', '   ', 123, 3.14, {'a': 1}, ['x'], True, False,
                    b'/tmp/x', b''])
    check("E1 非法类型(None/空/空白/数字/容器/bool/bytes)全部安全拒且不抛异常",
          ok_types)
    import pathlib
    pE2 = rp.trusted_dir_problems(pathlib.Path(daily), proj)
    vE2, _ = rp.trusted_source_dir(pathlib.Path(daily), proj)
    check("E2 PathLike合法输入→零问题+verified为物理路径",
          pE2 == [] and vE2 == os.path.realpath(daily), str((pE2[:1], vE2)))
    pE3 = rp.trusted_dir_problems(os.path.join(proj, '.', 'data', 'daily'), proj)
    check("E3 '.'组件词法恒等→放行(不误伤)", pE3 == [], str(pE3[:1]))
    old_cwd = os.getcwd()
    os.chdir(proj)
    try:
        pE4 = rp.trusted_dir_problems(os.path.join('data', 'daily'), proj)
        pE5 = rp.trusted_dir_problems(os.path.join('..', 'x'), proj)
    finally:
        os.chdir(old_cwd)
    check("E4 根内相对路径解析进可信根→放行;相对..→拒",
          pE4 == [] and bool(pE5) and any('..' in p for p in pE5),
          f"{pE4[:1]} | {pE5[:1]}")

# ════════════════════════════════════════════════════════════════════
print("\n── F. 正常路径回归(FIX8-05: 不得借拒绝一切制造安全)")

with tempfile.TemporaryDirectory(prefix='fix8-F1-') as td:
    fixt.write_collectors(td, DAY)                            # 平铺沙箱
    riF = quiet(sb.resolve_inputs, DAY, td, trusted_root=td)
    check("F1a 平铺沙箱(tempfile无链接自定义采集目录)四通道EXACT全选",
          all(riF[ch] and riF[ch]['exact'] for ch in rp.SOURCE_CHANNELS),
          str({k: v and v.get('exact') for k, v in riF.items()}))
    snapF = quiet(sb.build_snapshot, DAY, td, td, trusted_root=td,
                  as_of=fixt.as_of_for(DAY))
    check("F1b 正常四源日构建Gate A=PASS且记录sha256(FIX7-05保持)",
          snapF['gate_a']['status'] == 'PASS'
          and all(isinstance(snapF['sources_status'][ch].get('sha256'), str)
                  and len(snapF['sources_status'][ch]['sha256']) == 64
                  for ch in rp.SOURCE_CHANNELS),
          snapF['gate_a']['status'])

# F2: 每通道单独沙箱只留该通道文件,验证5/7/5/7回退窗口两侧边界
_WIN = {'global': 5, 'macro': 7, 'china': 5, 'rate_economy': 7}
_f2 = {}
for _ch, _win in _WIN.items():
    for _ymd, _tag in (('20261019' if _win == 5 else '20261017', 'in'),
                       ('20261018' if _win == 5 else '20261016', 'out')):
        _tdx = tempfile.mkdtemp(prefix=f'fix8-F2-{_ch}-{_tag}-')
        fixt.write_collectors(_tdx, _ymd)
        for _f in os.listdir(_tdx):              # 只留被测通道文件
            if not _f.startswith(_ch + '_'):
                os.remove(os.path.join(_tdx, _f))
        _r = quiet(sb.resolve_inputs, DAY, _tdx, trusted_root=_tdx)
        _f2[(_ch, _tag)] = (_r.get(_ch) or {}).get('lag_days')
check("F2 回退窗口5/7/5/7两侧边界原样: 窗内lag日选中,窗外不选",
      all(_f2[(_ch, 'in')] == _win and _f2[(_ch, 'out')] is None
          for _ch, _win in _WIN.items()),
      str(_f2))

with tempfile.TemporaryDirectory(prefix='fix8-F3-') as td:
    proj, daily = _mkproj(td)
    check("F3 macOS系统级前缀形态差异双向不误伤(dd=realpath/根=raw与反之)",
          rp.trusted_dir_problems(os.path.realpath(daily), proj) == []
          and rp.trusted_dir_problems(daily, os.path.realpath(proj)) == [])

with tempfile.TemporaryDirectory(prefix='fix8-F5-') as td:
    fixt.write_collectors(td, DAY, missing=('UMCSENT',))      # 非核心缺失
    snapD = quiet(sb.build_snapshot, DAY, td, td, trusted_root=td,
                  as_of=fixt.as_of_for(DAY))
    check("F5 非核心缺失保持DEGRADED(不因路径收紧变FAIL)",
          snapD['gate_a']['status'] == 'DEGRADED', snapD['gate_a']['status'])

# ════════════════════════════════════════════════════════════════════
print("\n── G. 完整正式链路(§8-06+FIX9-04: 真实发布保护对象+执行前基线)")

PUB_DAY, ATK_DAY = DAY, '20261025'   # 固定研究日(§9.6): 已发布日<攻击日


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
    """GLM计数器(仅mock外部LLM;发布正文为SYNTHETIC占位)。"""
    def __init__(self):
        self.calls = 0

    def __call__(self, system_prompt, user_prompt, max_tokens=32000, timeout=900):
        self.calls += 1
        # ≥500字符: 过短返回按失败处理(真实行为约束,与gate_chain同口径)
        return ('# 投资周报(SYNTHETIC测试文本·FIX9真实发布事务)\n\n'
                + '本周市场综述与分资产回顾。' * 60)


PROOT = tempfile.mkdtemp(prefix='fix8-G-')
OUTW = os.path.join(PROOT, 'output', 'weekly')
CFGD = os.path.join(PROOT, 'config')
os.makedirs(OUTW, exist_ok=True)
os.makedirs(CFGD, exist_ok=True)
THESIS = os.path.join(CFGD, 'thesis.json')
VIEWS = os.path.join(CFGD, 'allocation_views.json')
open(THESIS, 'w', encoding='utf-8').write(
    '{"version": 1, "theses": [], "updated_at": "2026-10-24T08:00:00"}')
open(VIEWS, 'w', encoding='utf-8').write(
    '{"version": 2, "views": [], "predictions": []}')

# G0a 合格研究日(项目布局,全真实产物)
fixt.build_full_day(PROOT, PUB_DAY)

# G0b 保护对象经**真实发布事务**产生(真generate_weekly_report+真
# write_report_status,非手拼状态fixture——FIX9-04缺陷B)
glm_pub = _GLM()
applied_pub = []
with mock.patch.object(rg, 'DATA_DIR', os.path.join(PROOT, 'data')), \
        mock.patch.object(rg, 'OUTPUT_DIR', OUTW), \
        mock.patch.object(rg, 'datetime', _DT(PUB_DAY)), \
        mock.patch.object(rg, '_call_glm', glm_pub), \
        mock.patch.object(rg, 'apply_status_updates',
                          lambda *a, **k: applied_pub.append(1)), \
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
        rc_pub = 0
    except SystemExit as e:
        rc_pub = e.code
REP = os.path.join(OUTW, f'weekly_report_{PUB_DAY}.md')
STATUS = os.path.join(OUTW, f'report_status_{PUB_DAY}.json')
check("G0 真实发布事务: exit=0+GLM恰1次+报告与状态落盘",
      rc_pub == 0 and os.path.exists(REP) and os.path.exists(STATUS)
      and glm_pub.calls == 1,
      f"rc={rc_pub} glm={glm_pub.calls}")

# G0c 前置断言(§9.2): formal_report_view必须接受该报告,否则本测试FAIL,
# 不得把不合格对象当保护对象
view0, reason0 = rp.formal_report_view(REP)
check("G0b 前置: formal_report_view接受真实发布报告(合格保护对象)",
      view0 is not None, reason0)
scan0 = rp.scan_formal_weekly_reports(OUTW)

# G0d **执行前基线**(§9.3: 一切被测危险操作之前采集)
baseline_before = {p: sha(p) for p in (REP, STATUS, THESIS, VIEWS)}

# 攻击: outside含ATK日四通道文件(SPX篡改99999);project/alias→outside/child
GOUT = os.path.join(PROOT, 'outside-data')
os.makedirs(os.path.join(GOUT, 'child'))
os.makedirs(os.path.join(GOUT, 'data', 'daily'))
fixt.write_collectors(os.path.join(GOUT, 'data', 'daily'), ATK_DAY)
_t = os.path.join(GOUT, 'data', 'daily', f'global_{ATK_DAY}.json')
_g = json.load(open(_t, encoding='utf-8'))
_g['data']['SPX']['close'] = 99999.0
json.dump(_g, open(_t, 'w', encoding='utf-8'))
os.symlink(os.path.join(GOUT, 'child'), os.path.join(PROOT, 'alias'))
MAL_DD = os.path.join(PROOT, 'alias', '..', 'data', 'daily')

# 真实snapshot_builder: 从越界路径构建ATK日快照(写入正式daily目录)
buf = io.StringIO()
with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
    _gsnap = sb.build_snapshot(target_ymd=ATK_DAY, data_dir=MAL_DD,
                               out_dir=os.path.join(PROOT, 'data', 'daily'),
                               trusted_root=PROOT,
                               as_of=fixt.as_of_for(ATK_DAY))
check("G1 真实snapshot_builder经symlink/..路径构建: Gate A≠PASS(诊断快照"
      "允许,失败原因可诊断,不得形成合格正式产物)",
      _gsnap is not None and _gsnap['gate_a']['status'] != 'PASS'
      and '..' in buf.getvalue(), _gsnap and _gsnap['gate_a']['status'])

# 真实data_assembler.main(时钟固定ATK日): 权威快照=恶意来源FAIL快照→exit2不产包
_pack_atk = os.path.join(PROOT, 'data', 'weekly', f'data_pack_{ATK_DAY}.md')
buf2 = io.StringIO()
with mock.patch.object(da, 'DATA_DIR', os.path.join(PROOT, 'data')), \
        mock.patch.object(da, 'datetime', _DT(ATK_DAY)), \
        contextlib.redirect_stdout(buf2):
    try:
        da.main()
        rc_da = 0
    except SystemExit as e:
        rc_da = e.code
check("G2 真实data_assembler: 拒绝生成正式数据包(exit=2,无包文件,原因留痕)",
      rc_da == 2 and not os.path.exists(_pack_atk)
      and ('FAIL' in buf2.getvalue() or '不可用' in buf2.getvalue()),
      f"rc={rc_da} pack={os.path.exists(_pack_atk)}")

# 真实report_generator全入口(时钟固定ATK日,GLM计数器): 预检拒→GLM=0→exit2
glm_atk = _GLM()
applied_atk = []
with mock.patch.object(rg, 'DATA_DIR', os.path.join(PROOT, 'data')), \
        mock.patch.object(rg, 'OUTPUT_DIR', OUTW), \
        mock.patch.object(rg, 'datetime', _DT(ATK_DAY)), \
        mock.patch.object(rg, '_call_glm', glm_atk), \
        mock.patch.object(rg, 'apply_status_updates',
                          lambda *a, **k: applied_atk.append(1)), \
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
        rc_rg = 0
    except SystemExit as e:
        rc_rg = e.code
check("G3 真实report_generator: 预检拒绝→exit=2且GLM调用0次(不产新正式报告)",
      rc_rg == 2 and glm_atk.calls == 0,
      f"rc={rc_rg} glm={glm_atk.calls}")

# G4 执行后核验(§9.4): 摘要比较+正式身份仍在+无新发布+无误标published
actual_after = {p: sha(p) for p in (REP, STATUS, THESIS, VIEWS)}
view1, reason1 = rp.formal_report_view(REP)
_new_reports = sorted(f for f in os.listdir(OUTW)
                      if (f.startswith('weekly_report_')
                          or f.startswith('report_status_'))
                      and PUB_DAY not in f)
_pub_true = sorted(
    f for f in os.listdir(OUTW)
    if f.startswith('report_status_')
    and isinstance(json.load(open(os.path.join(OUTW, f))), dict)
    and json.load(open(os.path.join(OUTW, f))).get('published') is True)
check("G4 保护对象核验: 4对象摘要=执行前基线;报告仍被formal_report_view"
      "接受;无新报告/状态;published=true仅已发布日;无长期状态回写",
      baseline_before == actual_after and view1 is not None
      and not _new_reports and _pub_true == [f'report_status_{PUB_DAY}.json']
      and applied_atk == [],
      str({'changed': [k for k in baseline_before
                       if baseline_before[k] != actual_after[k]],
           'new': _new_reports, 'pub_true': _pub_true,
           'formal': reason1, 'applied': len(applied_atk)}))

# G5 比较机制自检(§9.5,独立夹具): 篡改必须能被摘要比较发现
with tempfile.TemporaryDirectory(prefix='fix8-G5-') as td5:
    a5, b5 = os.path.join(td5, 'a.json'), os.path.join(td5, 'b.json')
    open(a5, 'w').write('{"v": 1}')
    open(b5, 'w').write('{"v": 2}')
    base5 = {p: sha(p) for p in (a5, b5)}
    open(b5, 'w').write('{"v": 999}')          # 有意篡改其中一个
    after5 = {p: sha(p) for p in (a5, b5)}
    check("G5 自检: 摘要比较能发现被篡改对象且不误报未动对象",
          after5[a5] == base5[a5] and after5[b5] != base5[b5])

# ════════════════════════════════════════════════════════════════════
print("\n── H. 内容绑定回归(§11: FIX7-05 sha256不削弱)")

with tempfile.TemporaryDirectory(prefix='fix8-H1-') as td:
    fixt.write_collectors(td, DAY)
    snapH = quiet(sb.build_snapshot, DAY, td, td, trusted_root=td,
                  as_of=fixt.as_of_for(DAY))
    open(os.path.join(td, f'global_{DAY}.json'), 'w').write('THIS IS NOT JSON')
    pH = rp.sources_status_problems(snapH['sources_status'], DAY, td,
                                    trusted_root=td)
    check("H1 构建后原始文件内容被替换→摘要失配拒(FIX7-05语义原样)",
          any('FIX7-05' in p or '摘要' in p for p in pH), str(pH[:2]))
    snapH.pop('_content_binding_note', None)
    ss_h = json.loads(json.dumps(snapH['sources_status']))
    for ch in rp.SOURCE_CHANNELS:
        ss_h[ch].pop('sha256', None)                          # 历史快照无摘要
    pH2 = rp.sources_status_problems(ss_h, DAY, td, trusted_root=td)
    check("H2 历史快照无sha256字段: 不虚报内容核验(零摘要失配误报)",
          not any('摘要' in p for p in pH2), str(pH2[:2]))

# ════════════════════════════════════════════════════════════════════
print("\n── I. 调用端锚定审计(§7.3: 待校验路径不得自证授权)")

# I1: da.build_markdown的data_dir参数不再成为授权依据
# (DEGRADED快照由真实builder产出: 非核心缺失+sha256内容绑定真实成立)
with tempfile.TemporaryDirectory(prefix='fix8-I1-') as td:
    data_root = os.path.join(td, 'data')
    os.makedirs(os.path.join(data_root, 'daily'))
    fixt.write_collectors(os.path.join(data_root, 'daily'), DAY,
                          missing=('UMCSENT',))
    snap_deg = quiet(sb.build_snapshot, DAY, os.path.join(data_root, 'daily'),
                     td, trusted_root=td, as_of=fixt.as_of_for(DAY))
    md_no_tr = da.build_markdown(snap_deg, DAY, data_dir=data_root)
    md_tr = da.build_markdown(snap_deg, DAY, data_dir=data_root,
                              trusted_root=os.path.dirname(data_root))
    check("I1 build_markdown: 不传trusted_root→模块锚拒绝沙箱(无降级披露块);"
          "显式授权→披露块在(参数自证授权已废除)",
          '数据质量降级披露' not in md_no_tr
          and '数据质量降级披露' in md_tr)

# I2: dpo.observe缺省锚=可信代码位置,沙箱锚点批次须显式授权
with tempfile.TemporaryDirectory(prefix='fix8-I2-') as td:
    snap2, _sp2, p2 = fixt.build_full_day(td, DAY)
    apath2 = p2['anchors']
    anchors2 = json.load(open(apath2, encoding='utf-8'))
    vp2 = os.path.join(td, 'views.json')
    json.dump({'version': 2, 'views': [],
               'predictions': [{'pred_id': 'PX', 'asset': '标普',
                                'direction': 't', 'status': 'observing',
                                'metric': 'global_market.data.SPX.close',
                                'comparator': '>=', 'target': 4000.0,
                                'observe_from': '2026-10-10',
                                'deadline': '2026-12-31', 'observations': []}]},
              open(vp2, 'w', encoding='utf-8'))
    ch_no, _n, st_no = quiet(dpo.observe, views_path=vp2, anchors=anchors2,
                             today_str='2026-10-24', anchors_date=DAY,
                             anchors_path=apath2)
    json.dump({'version': 2, 'views': [],
               'predictions': [{'pred_id': 'PX', 'asset': '标普',
                                'direction': 't', 'status': 'observing',
                                'metric': 'global_market.data.SPX.close',
                                'comparator': '>=', 'target': 4000.0,
                                'observe_from': '2026-10-10',
                                'deadline': '2026-12-31', 'observations': []}]},
              open(vp2, 'w', encoding='utf-8'))
    ch_ok, _n2, st_ok = quiet(dpo.observe, views_path=vp2, anchors=anchors2,
                              today_str='2026-10-24', anchors_date=DAY,
                              anchors_path=apath2, trusted_root=td)
    check("I2 观察器: 缺省锚拒沙箱批次(关键FAIL不写观察);显式授权→真实记录",
          st_no == 'FAIL' and ch_no == [] and st_ok in ('PASS', 'PARTIAL')
          and any('PX' in c for c in ch_ok),
          f"no={st_no} ok={st_ok}")

# I3: real_data_acceptance缺省拒外部--data-dir;显式--trusted-root放行
with tempfile.TemporaryDirectory(prefix='fix8-I3-') as td:
    fixt.write_collectors(td, DAY)
    fake_now = f'{DAY[:4]}-{DAY[4:6]}-{DAY[6:]}T08:00:00'

    class _DT(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls.fromisoformat(fake_now)

    def _run_rda(out_sub, extra):
        out = io.StringIO()
        argv = ['rda', '--data-dir', td, '--out-dir',
                os.path.join(td, out_sub), '--skip-external'] + extra
        with mock.patch.object(sys, 'argv', argv), \
                mock.patch.object(rda, 'datetime', _DT), \
                contextlib.redirect_stdout(out):
            try:
                rda.main()
                rc = 0
            except SystemExit as e:
                rc = e.code
        return rc, out.getvalue()

    rc1, out1 = _run_rda('acc1', [])                        # 缺省可信根
    rc2, out2 = _run_rda('acc2', ['--trusted-root', td])    # 显式授权
    _acc = sorted(glob.glob(os.path.join(td, 'acc2', '*.json')))[-1]
    _checks = {r['check']: r['verdict']
               for r in json.load(open(_acc))['checks']}
    _fails2 = [r['check'] for r in json.load(open(_acc))['checks']
               if r['verdict'] == 'FAIL']
    check("I3 real_data_acceptance: --data-dir不再自证授权——缺省可信根下"
          "Gate A≠PASS→exit 2且留信任边界原因;显式--trusted-root→快照PASS"
          "进入真实验收,验收记录Gate A=PASS且无信任拒绝",
          rc1 == 2 and '不在可信项目根之内' in out1
          and _checks.get('Gate A状态') == 'PASS'
          and '不在可信项目根之内' not in out2,
          f"no-root={rc1} with-root={rc2} fails2={_fails2}")
    print(f"     (退出码留痕: 无授权={rc1}; 显式授权={rc2}"
          f";授权态FAIL项={_fails2 or '无'}——fixture合成序列无2026年前"
          "观测,YTD基准语义检查为数据属性非信任属性)")

# ════════════════════════════════════════════════════════════════════
print("\n" + "═" * 72)
print(f"FIX8 结果: {PASS_N}通过 / {FAIL_N}失败")
if FAIL_N:
    sys.exit(1)
