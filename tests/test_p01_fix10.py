#!/usr/bin/env python3
"""IA-P0-1-FIX10 对抗测试: 代码导入词法别名不得取得来源授权(IA-F9-DEF-001)。

真实项目源码整目录复制到隔离项目, 以**真实子进程标准import**复现两种导入
形态(物理导入 vs 经未批准外部根级符号链接导入), 不以sys.modules缓存模拟;
不mock信任原语/Gate A/预检, mock仅限外部GLM/时钟。

矩阵(§十.A~D):
  A 真实导入形态: 物理导入/外链导入/两形态物理根一致/词法路径不自动授权/
    原物理可信目录双形态放行/前置断言(链接真实存在/词法导入条件真实触发);
  B 外部链接(进程内原语矩阵): →project/→project/data/多级/项目内未批准/
    链接+../正常物理路径;
  C 系统级路径: macOS封闭表双向/Linux无别名/用户级伪别名/导入形态不扩充
    封闭表;
  D 真实研究链: PASS/DEGRADED/FALLBACK正常构建(物理导入子进程) +
    经外链导入的sb(da/rg)全链fail-closed + GLM=0 + 零新发布 + 字节保护。
"""
import contextlib
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from unittest import mock

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(_HERE)
sys.path.insert(0, os.path.join(_REPO, 'scripts'))
sys.path.insert(0, _HERE)

import fixt                                    # noqa: E402
import research_provenance as rp               # noqa: E402
import data_assembler as da                    # noqa: E402
import report_generator as rg                  # noqa: E402

DAY = '20261024'
OLD_DAY = '20261019'          # 恰5天前——global通道fallback窗内
AS_OF = f"{DAY[:4]}-{DAY[4:6]}-{DAY[6:]}T08:00:00+08:00"
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
    with contextlib.redirect_stdout(io.StringIO()) as out, \
            contextlib.redirect_stderr(io.StringIO()):
        try:
            return fn(*a, **kw), out.getvalue()
        except SystemExit as e:
            return e.code, out.getvalue()


def sha(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


class _DT:
    """固定时钟(子进程driver与进程内共用形态): now/strptime/fromisoformat。"""
    def __init__(self, ymd):
        self._ymd = ymd

    @staticmethod
    def strptime(s, f):
        return datetime.strptime(s, f)

    @staticmethod
    def fromisoformat(s):
        return datetime.fromisoformat(s)

    def now(self, tz=None):
        d = datetime.strptime(self._ymd, '%Y%m%d')
        return d.replace(tzinfo=tz) if tz is not None else d


_DT_SRC = """
class _DT:
    def __init__(self, ymd):
        self._ymd = ymd
    @staticmethod
    def strptime(s, f):
        return __import__('datetime').datetime.strptime(s, f)
    @staticmethod
    def fromisoformat(s):
        return __import__('datetime').datetime.fromisoformat(s)
    def now(self, tz=None):
        d = __import__('datetime').datetime.strptime(self._ymd, '%Y%m%d')
        return d.replace(tzinfo=tz) if tz is not None else d
"""


# ── 隔离真实项目: 整目录复制真实scripts/+config/+env_config(§8.4: 真实
#    项目源码,非摘抄片段;不重写被测信任函数) ─────────────────────────
def make_project(prefix, missing=(), drop_global_today=False, add_old_day=False):
    iso = tempfile.mkdtemp(prefix=prefix)
    project = os.path.join(iso, 'project')
    shutil.copytree(os.path.join(_REPO, 'scripts'),
                    os.path.join(project, 'scripts'),
                    ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copytree(os.path.join(_REPO, 'config'),
                    os.path.join(project, 'config'),
                    ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copy2(os.path.join(_REPO, 'env_config.py'),
                 os.path.join(project, 'env_config.py'))
    daily = os.path.join(project, 'data', 'daily')
    fixt.write_collectors(daily, DAY, missing=missing)
    if drop_global_today:
        os.remove(os.path.join(daily, f'global_{DAY}.json'))
    if add_old_day:
        fixt.write_collectors(daily, OLD_DAY)
    link = os.path.join(iso, 'UNAPPROVED-external-link-to-project-root')
    os.symlink(project, link)
    return iso, project, daily, link


def sub_run(search_dirs, code, cwd, timeout=180):
    """真实子进程标准import: PYTHONPATH控制导入搜索路径,绝不共享sys.modules。"""
    env = dict(os.environ, PYTHONPATH=os.pathsep.join(search_dirs))
    return subprocess.run([sys.executable, '-c', code], env=env, cwd=cwd,
                          capture_output=True, text=True, timeout=timeout)


def probe_code(link, project):
    return (
        "LINK = " + repr(link) + "\n"
        "PROJECT = " + repr(project) + "\n"
        "import json, os\n"
        "import research_provenance as rp\n"
        "rt = rp.default_trusted_root()\n"
        "ldd = os.path.join(LINK, 'data', 'daily')\n"
        "pdd = os.path.join(PROJECT, 'data', 'daily')\n"
        "print('@P@' + json.dumps({\n"
        " 'file': rp.__file__,\n"
        " 'file_real': os.path.realpath(rp.__file__),\n"
        " 'root': rt,\n"
        " 'entries': sorted(rp._trusted_entry_forms(rt)),\n"
        " 'link_probs': rp.trusted_dir_problems(ldd),\n"
        " 'phys_probs': rp.trusted_dir_problems(pdd),\n"
        " 'link_vsd': rp.trusted_source_dir(ldd)[0],\n"
        " 'phys_vsd': rp.trusted_source_dir(pdd)[0],\n"
        " 'aliases': [list(t) for t in rp._SYSTEM_PREFIX_ALIASES],\n"
        "}))\n"
    )


def run_probe(search, code, cwd):
    r = sub_run([search], code, cwd)
    if r.returncode != 0:
        return None, r
    line = [l for l in r.stdout.splitlines() if l.startswith('@P@')]
    if not line:
        return None, r
    return json.loads(line[0][3:]), r


ISO, PROJECT, DAILY, LINK = make_project('fix10-main-')

# ════════════════════════════════════════════════════════════════════
print("\n── A. 真实子进程双导入形态(§十.A)")

# A0 前置断言: 攻击布局真实成立(链接存在/指向project/文件物理在project内)
check("A0 前置: 外链存在且指向project根, 采集文件物理在project内",
      os.path.islink(LINK) and os.path.realpath(LINK) == os.path.realpath(PROJECT)
      and os.path.isdir(os.path.join(PROJECT, 'scripts'))
      and os.path.exists(os.path.join(DAILY, f'global_{DAY}.json'))
      and not os.path.islink(os.path.join(PROJECT, 'scripts')))

PCODE = probe_code(LINK, PROJECT)
PA, RA = run_probe(os.path.join(PROJECT, 'scripts'), PCODE, ISO)
check("A1(物理导入) 子进程import成功且__file__词法位于project内",
      PA is not None and RA.returncode == 0
      and os.path.dirname(os.path.dirname(PA['file'])) == PROJECT
      and os.path.realpath(PA['file']).startswith(
          os.path.realpath(PROJECT) + os.sep),
      (RA.stderr[-300:] if PA is None else str(PA['file'])))

PB, RB = run_probe(os.path.join(LINK, 'scripts'), PCODE, ISO)
check("A2(外链导入) 子进程import成功且__file__词法**真实穿过外链**"
      "(词法导入条件实际触发, 非sys.modules模拟)",
      PB is not None and RB.returncode == 0
      and os.path.dirname(os.path.dirname(PB['file'])) == LINK,
      (RB.stderr[-300:] if PB is None else str(PB['file'])))
print(f"     观测 __file__(物理导入) = {PA['file'] if PA else '?'}")
print(f"     观测 __file__(外链导入) = {PB['file'] if PB else '?'}")
print(f"     观测 realpath(两形态同物理文件) = {PB['file_real'] if PB else '?'}")

if PA and PB:
    check("A3 两导入形态加载同一物理模块文件(realpath一致), 物理根推导一致",
          PA['file_real'] == PB['file_real'] and PA['root'] == PB['root']
          and os.path.realpath(PROJECT) == PA['root'])
    check("A4 入口集合在两导入形态下**完全一致**(导入路径不改变授权结论)",
          set(PA['entries']) == set(PB['entries']), str(PB['entries']))
    check("A5 词法导入路径上溯根(外链)不在入口集合(IA-F9-DEF-001已修)",
          LINK not in set(PB['entries'])
          and all(os.path.realpath(e) == PB['root'] for e in PB['entries']),
          str(PB['entries']))
    check("A6(物理导入) 原物理可信目录放行, 外链目录拒绝",
          PA['phys_probs'] == [] and PA['link_probs'] != []
          and PA['link_vsd'] is None
          and PA['phys_vsd'].startswith(PA['root'] + os.sep))
    check("A7(外链导入) 同一物理可信目录**仍**放行(不因导入形态误伤), "
          "外链目录拒绝",
          PB['phys_probs'] == [] and PB['link_probs'] != []
          and PB['link_vsd'] is None
          and PB['phys_vsd'].startswith(PB['root'] + os.sep))
    check("A8 外链拒绝消息注明信任边界(FIX10-01/IA-F9-DEF-001)",
          any('不在可信项目根之内' in p for p in PB['link_probs']))

# ════════════════════════════════════════════════════════════════════
print("\n── B. 外部链接矩阵(进程内原语, 显式可信根=" + PROJECT + ")")

check("B1 外链→project根: <link>/data/daily拒绝",
      bool(rp.trusted_dir_problems(os.path.join(LINK, 'data', 'daily'),
                                   PROJECT)))
_lnk_data = os.path.join(ISO, 'fix10-link-to-data')
os.symlink(os.path.join(PROJECT, 'data'), _lnk_data)
check("B2 外链→project/data: <link>/daily拒绝(FIX8反例保持)",
      bool(rp.trusted_dir_problems(os.path.join(_lnk_data, 'daily'),
                                   PROJECT)))
_mid = os.path.join(ISO, 'fix10-mid')
os.makedirs(_mid)
_lnk_multi = os.path.join(_mid, 'fix10-leaf-link')
os.symlink(PROJECT, _lnk_multi)
check("B3 多级路径下的外链: <mid>/<leaf-link>/data/daily拒绝",
      bool(rp.trusted_dir_problems(
          os.path.join(_lnk_multi, 'data', 'daily'), PROJECT)))
_outside = os.path.join(ISO, 'outside', 'data', 'daily')
os.makedirs(_outside)
fixt.write_collectors(_outside, DAY)
os.symlink(os.path.join(ISO, 'outside'), os.path.join(PROJECT, 'datalink'))
check("B4 项目内未批准链接→外部: project/datalink/daily拒绝",
      bool(rp.trusted_dir_problems(os.path.join(PROJECT, 'datalink', 'daily'),
                                   PROJECT)))
check("B5 外链+..: 词法..在任何规范化之前拒绝",
      bool(rp.trusted_dir_problems(
          os.path.join(LINK, '..', 'data', 'daily'), PROJECT)))
check("B6 正常物理路径: project/data/daily放行(收紧不误伤)",
      rp.trusted_dir_problems(DAILY, PROJECT) == [])

# ════════════════════════════════════════════════════════════════════
print("\n── C. 系统级路径兼容(§十.C)")

if sys.platform == 'darwin':
    _td = tempfile.mkdtemp(prefix='fix10-C1-')       # /var/folders/...形态
    _rt = os.path.realpath(_td)
    _ents = rp._trusted_entry_forms(_rt)
    _var_form = '/var' + _rt[len('/private/var'):]
    check("C1(macOS真机) 入口集合恰=物理锚+/var别名形式(封闭表,无第三来源)",
          _ents == {_rt, _var_form}
          and rp.trusted_dir_problems(_td, _td) == []
          and rp.trusted_dir_problems(_rt, _td) == [],
          str(sorted(_ents)))
else:
    _td = tempfile.mkdtemp(prefix='fix10-C1-')
    _rt = os.path.realpath(_td)
    check("C1(Linux CI) 封闭表不适用: 入口集合恰=物理锚(无代码词法/无别名)",
          rp._trusted_entry_forms(_rt) == {_rt})
FC = tempfile.mkdtemp(prefix='fix10-C3-')
_fake = os.path.join(FC, 'fakeReal', 'proj')
os.makedirs(_fake)
for nm in ('fakeTmp', 'fakePrivateTmp'):
    os.symlink(_fake, os.path.join(FC, nm))
check("C3 用户自建伪别名(命名酷似系统别名)不得借封闭表通过",
      bool(rp.trusted_dir_problems(os.path.join(FC, 'fakeTmp', 'data'),
                                   _fake))
      and bool(rp.trusted_dir_problems(
          os.path.join(FC, 'fakePrivateTmp', 'data'), _fake)))
_FROZEN = [['/tmp', '/private/tmp'], ['/var', '/private/var'],
           ['/etc', '/private/etc']]
if PA and PB:
    check("C4 导入形态不扩充封闭表(两形态子进程观测值==冻结常量)",
          PA['aliases'] == _FROZEN and PB['aliases'] == _FROZEN)

# ════════════════════════════════════════════════════════════════════
print("\n── D. 真实研究链(§十.D)")

SB_DRIVER = (
    "import json, os, sys\n"
    "DAY, AS_OF = " + repr(DAY) + ", " + repr(AS_OF) + "\n"
    "import snapshot_builder as sb\n"
    "snap = sb.build_snapshot(target_ymd=DAY, data_dir=" + repr(DAILY) +
    ",\n    out_dir=" + repr(DAILY) + ", as_of=AS_OF)\n"
    "src = snap.get('sources_status') or {}\n"
    "print('@SB@' + json.dumps({'gate': (snap.get('gate_a') or {}).get('status'),\n"
    " 'files': {k: bool((v or {}).get('file')) for k, v in src.items()},\n"
    " 'global': (src.get('global') or {})}, default=str))\n"
)
rD1 = sub_run([os.path.join(PROJECT, 'scripts')], SB_DRIVER, ISO)
try:
    oD1 = json.loads([l for l in rD1.stdout.splitlines()
                      if l.startswith('@SB@')][0][4:])
except Exception:
    oD1 = None
check("D1(物理导入子进程) 真实build_snapshot: Gate A=PASS, 四通道全选中",
      rD1.returncode == 0 and oD1 and oD1['gate'] == 'PASS'
      and all(oD1['files'].get(c) for c in
              ('global', 'macro', 'china', 'rate_economy')),
      rD1.stderr[-300:] if oD1 is None else str(oD1))
SNAP_PATH = os.path.join(DAILY, f'research_snapshot_{DAY}.json')
check("D1b 快照文件真实落盘(供后续外链导入链消费)",
      os.path.isfile(SNAP_PATH))

# D2 DEGRADED / D3 FALLBACK: 独立隔离项目, 物理导入子进程
ISO2, PROJ2, DAILY2, _L2 = make_project('fix10-degraded-', missing=('UMCSENT',))
SB2 = SB_DRIVER.replace(repr(DAILY), repr(DAILY2))
rD2 = sub_run([os.path.join(PROJ2, 'scripts')], SB2, ISO2)
try:
    oD2 = json.loads([l for l in rD2.stdout.splitlines()
                      if l.startswith('@SB@')][0][4:])
except Exception:
    oD2 = None
check("D2(物理导入子进程) 非核心UMCSENT缺失→真实DEGRADED(不误转FAIL)",
      rD2.returncode == 0 and oD2 and oD2['gate'] == 'DEGRADED')

ISO3, PROJ3, DAILY3, _L3 = make_project('fix10-fallback-',
                                        drop_global_today=True,
                                        add_old_day=True)
SB3 = SB_DRIVER.replace(repr(DAILY), repr(DAILY3))
rD3 = sub_run([os.path.join(PROJ3, 'scripts')], SB3, ISO3)
_d3snap = os.path.join(DAILY3, f'research_snapshot_{DAY}.json')
try:
    with open(_d3snap, encoding='utf-8') as f:
        s3 = json.load(f)
    _g = (s3.get('sources_status') or {}).get('global') or {}
except Exception:
    _g = {}
check("D3(物理导入子进程) global当日缺→5天窗内fallback(lag=5, 真实降级披露)",
      rD3.returncode == 0 and _g.get('status') == 'FALLBACK'
      and _g.get('file') == f'global_{OLD_DAY}.json'
      and _g.get('lag_days') == 5
      and ((s3.get('gate_a') or {}).get('status') in ('PASS', 'DEGRADED')),
      json.dumps(_g, ensure_ascii=False)[:200])

# D4 sb经外链导入: 同一物理数据, 导入词法穿过外链→fail-closed
SB4 = (
    "import json, os, sys\n"
    "DAY, AS_OF = " + repr(DAY) + ", " + repr(AS_OF) + "\n"
    "import snapshot_builder as sb\n"
    "assert sb.__file__.startswith(" + repr(LINK + os.sep) + "), sb.__file__\n"
    "out = " + repr(os.path.join(ISO, 'diag-out')) + "\n"
    "snap = sb.build_snapshot(target_ymd=DAY, data_dir=os.path.join(" +
    repr(LINK) + ", 'data', 'daily'), out_dir=out, as_of=AS_OF)\n"
    "src = snap.get('sources_status') or {}\n"
    "print('@SB@' + json.dumps({'gate': (snap.get('gate_a') or {}).get('status'),\n"
    " 'files': {k: bool((v or {}).get('file')) for k, v in src.items()},\n"
    " 'file': sb.__file__}))\n"
)
rD4 = sub_run([os.path.join(LINK, 'scripts')], SB4, ISO)
try:
    oD4 = json.loads([l for l in rD4.stdout.splitlines()
                      if l.startswith('@SB@')][0][4:])
except Exception:
    oD4 = None
check("D4(外链导入子进程) sb对同一物理数据fail-closed: Gate A=FAIL, "
      "四通道全不选(入口授权≠文件内容)",
      rD4.returncode == 0 and oD4
      and oD4['gate'] in (None, 'FAIL')   # 全通道缺源→不可证明/FAIL
      and not any(oD4['files'].values())
      and oD4.get('file', '').startswith(LINK + os.sep),
      rD4.stderr[-300:] if oD4 is None else str(oD4))

# D5 da经外链导入子进程: 模块DATA_DIR词法=<link>/data(真实锚)→Gate拒→exit 2
DA5 = (
    _DT_SRC + "\n"
    "import os, sys\n"
    "import data_assembler as da\n"
    "assert os.path.dirname(str(da.DATA_DIR)) == " + repr(LINK) + \
    ", da.DATA_DIR\n"
    "da.datetime = _DT(" + repr(DAY) + ")\n"
    "try:\n"
    "    da.main()\n"
    "    print('@DA@ rc=0')\n"
    "except SystemExit as e:\n"
    "    print('@DA@ rc=%s' % e.code)\n"
)
rD5 = sub_run([os.path.join(LINK, 'scripts')], DA5, ISO)
_d5line = [l for l in rD5.stdout.splitlines() if l.startswith('@DA@')]
_d5out = rD5.stdout + rD5.stderr
check("D5(外链导入子进程) da: 模块DATA_DIR锚=外链词法形态→Gate A拒, exit 2",
      rD5.returncode == 0 and _d5line and _d5line[0] == '@DA@ rc=2'
      and ('符号链接' in _d5out or '不在可信项目根之内' in _d5out),
      (_d5line[:1] or [rD5.stderr[-300:]])[0])

# D6 rg经外链导入子进程: 预检fail-closed, GLM零调用, 零产出
RG6 = (
    _DT_SRC + "\n"
    "import os, sys\n"
    "import report_generator as rg\n"
    "assert os.path.normpath(os.path.dirname(str(rg.DATA_DIR))) == " +
    repr(LINK) + ", rg.DATA_DIR\n"
    "_calls = []\n"
    "def _glm(*a, **k):\n"
    "    _calls.append(1)\n"
    "    return 'x' * 600\n"
    "rg._call_glm = _glm\n"
    "rg.datetime = _DT(" + repr(DAY) + ")\n"
    "try:\n"
    "    rg.generate_weekly_report()\n"
    "    print('@RG@ rc=0')\n"
    "except SystemExit as e:\n"
    "    print('@RG@ rc=%s' % e.code)\n"
    "print('@RG@ glm=%d' % len(_calls))\n"
)
_WK = os.path.join(PROJECT, 'output', 'weekly')
os.makedirs(_WK, exist_ok=True)
_base_before = sorted(os.listdir(_WK))
_snap_sha_before = sha(SNAP_PATH)
_coll_before = {p: sha(os.path.join(DAILY, p))
                for p in sorted(os.listdir(DAILY))}
rD6 = sub_run([os.path.join(LINK, 'scripts')], RG6, ISO)
_rg_lines = [l for l in rD6.stdout.splitlines() if l.startswith('@RG@')]
check("D6(外链导入子进程) rg预检fail-closed: exit 2, GLM调用=0",
      rD6.returncode == 0 and '@RG@ rc=2' in _rg_lines
      and '@RG@ glm=0' in _rg_lines,
      str(_rg_lines[:2] or rD6.stderr[-300:]))
check("D6b 零新产出: weekly目录无新文件, 快照/采集文件字节不变",
      sorted(os.listdir(_WK)) == _base_before
      and sha(SNAP_PATH) == _snap_sha_before
      and {p: sha(os.path.join(DAILY, p))
           for p in sorted(os.listdir(DAILY))} == _coll_before)
_proj_out = os.path.join(PROJECT, 'output')
_new_reports = [os.path.join(dp, f)
                for dp, _, fs in os.walk(_proj_out) for f in fs
                if f.startswith(('report_status_', 'weekly_report_'))]
check("D6c 全项目范围无新增report_status_*/weekly_report_*",
      _new_reports == [])

# D7 进程内补充: rg.DATA_DIR锚=外链词法(模拟别名导入的模块锚状态)+GLM计数
class _GLM:
    calls = 0

    def __call__(self, *a, **k):
        self.calls += 1
        return '本周市场综述与分资产回顾。' * 60


_glm = _GLM()
with mock.patch.object(rg, 'datetime', _DT(DAY)), \
        mock.patch.object(rg, 'DATA_DIR', os.path.join(LINK, 'data')), \
        mock.patch.object(rg, 'OUTPUT_DIR',
                          os.path.join(ISO, 'fix10-rg-out')), \
        mock.patch.object(rg, '_call_glm', _glm):
    rc_d7, out_d7 = quiet(rg.generate_weekly_report)
check("D7(进程内, 模块锚=外链词法形态) rg exit 2, GLM=0, 无产出目录",
      rc_d7 == 2 and _glm.calls == 0
      and not os.path.exists(os.path.join(ISO, 'fix10-rg-out'))
      and ('符号链接' in out_d7 or '不在可信项目根之内' in out_d7))

# D8 保护复核(全部外链导入攻击后): 无任何新增正式发布记录/长期状态改写
_new_reports8 = [os.path.join(dp, f)
                 for dp, _, fs in os.walk(_proj_out) for f in fs
                 if f.startswith(('report_status_', 'weekly_report_'))]
check("D8 执行后全项目仍无新增发布记录, 采集数据字节保护保持",
      _new_reports8 == [] and _new_reports == []
      and sha(SNAP_PATH) == _snap_sha_before)

# ════════════════════════════════════════════════════════════════════
print(f"\n{'=' * 64}\nFIX10 结果: {PASS_N} 通过 / {FAIL_N} 失败")
for d in (ISO, ISO2, ISO3, FC):
    shutil.rmtree(d, ignore_errors=True)
sys.exit(1 if FAIL_N else 0)
