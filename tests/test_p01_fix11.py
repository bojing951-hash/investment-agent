#!/usr/bin/env python3
"""IA-P0-1-FIX11 联合E2E: 同一外链标准导入子进程中的非法来源拒绝
+ 既有正式报告/长期状态四对象保护(F10-AC-04补证)。

FIX9-E(真实发布保护)与FIX10-A/D(双导入形态)此前分属两组测试;本轮在**同一条
件链**上联合验证: 真实发布的历史正式报告 → 独立子进程经未批准外链根级符号
链接标准import四个模块(词法__file__真实穿过外链) → 同一子进程内采集四对象
执行前SHA-256 → 同一子进程内执行真实非法研究链(sb/da/rg, 仅mock付费GLM与
外部服务) → 同一子进程内复采摘要并验证保护。

阶段: PREPARE → POSITIVE(物理正向对照) → PUBLISH(物理导入真实发布) →
ATTACK(外链导入联合攻击, 单一子进程) → ASSERT → SENSITIVITY。
每阶段失败均使本套件非零退出;不预填成功结论。
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

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(_HERE)
sys.path.insert(0, os.path.join(_REPO, 'scripts'))
sys.path.insert(0, _HERE)

import fixt                                    # noqa: E402
import research_provenance as rp               # noqa: E402

PUB, ATK = '20261024', '20261025'      # 先合格发布, 后非法研究尝试
AS_OF_PUB = f"{PUB[:4]}-{PUB[4:6]}-{PUB[6:]}T08:00:00+08:00"
AS_OF_ATK = f"{ATK[:4]}-{ATK[4:6]}-{ATK[6:]}T08:00:00+08:00"
PASS_N, FAIL_N = 0, 0


def check(name, cond, detail=''):
    global PASS_N, FAIL_N
    if cond:
        PASS_N += 1
        print(f"  ✅ {name}")
    else:
        FAIL_N += 1
        print(f"  ❌ {name}  {detail}")


def sha(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


_DT_SRC = """
import datetime as _dtmod
class _DT:
    def __init__(self, ymd):
        self._ymd = ymd
    @staticmethod
    def strptime(s, f):
        return _dtmod.datetime.strptime(s, f)
    @staticmethod
    def fromisoformat(s):
        return _dtmod.datetime.fromisoformat(s)
    def now(self, tz=None):
        d = _dtmod.datetime.strptime(self._ymd, '%Y%m%d')
        return d.replace(tzinfo=tz) if tz is not None else d
"""

_MOCKS_SRC = """
def _install_publish_mocks(rg, glm_log):
    rg._call_glm = (lambda *a, **k:
                    glm_log.append(1) or ('本周市场综述与分资产回顾。' * 60))
    rg.validate_generated_report = (
        lambda md, anchors=None, anchors_file=None: ('PASS', ['SYNTHETIC警告']))
    rg.allocation_engine.load_views = (
        lambda *a, **k: {'views': [], 'predictions': []})
    rg.pending_completed_month = lambda d=None: None
    rg.pending_completed_quarter = lambda d=None: None
    rg.load_framework = lambda: '框架'
    rg.load_theses = lambda: '论点'
    rg.load_technical_notes = lambda: ''
    rg.load_news_summary = lambda: ''
    rg.load_previous_report = lambda: ''
"""


def sub_run(search_dirs, code, cwd, timeout=240):
    env = dict(os.environ, PYTHONPATH=os.pathsep.join(search_dirs))
    return subprocess.run([sys.executable, '-c', code], env=env, cwd=cwd,
                          capture_output=True, text=True, timeout=timeout)


def marker(r, tag):
    lines = [l for l in r.stdout.splitlines() if l.startswith(tag)]
    return json.loads(lines[0][len(tag):]) if lines else None


# ════════════════════════════════════════════════════════════════════
print("\n── PREPARE. 隔离真实项目+非法研究日数据(§FIX11-01)")

ISO = tempfile.mkdtemp(prefix='fix11-')
PROJECT = os.path.join(ISO, 'project')
shutil.copytree(os.path.join(_REPO, 'scripts'),
                os.path.join(PROJECT, 'scripts'),
                ignore=shutil.ignore_patterns('__pycache__'))
shutil.copytree(os.path.join(_REPO, 'config'),
                os.path.join(PROJECT, 'config'),
                ignore=shutil.ignore_patterns('__pycache__'))
shutil.copy2(os.path.join(_REPO, 'env_config.py'),
             os.path.join(PROJECT, 'env_config.py'))
DAILY = os.path.join(PROJECT, 'data', 'daily')
WEEKLY_DATA = os.path.join(PROJECT, 'data', 'weekly')
OUTW = os.path.join(PROJECT, 'output', 'weekly')
os.makedirs(OUTW, exist_ok=True)
LINK = os.path.join(ISO, 'UNAPPROVED-external-link-to-project-root')
os.symlink(PROJECT, LINK)
LINK_DAILY = os.path.join(LINK, 'data', 'daily')
REPORT = os.path.join(OUTW, f'weekly_report_{PUB}.md')
STATUS = os.path.join(OUTW, f'report_status_{PUB}.json')
THE = os.path.join(PROJECT, 'config', 'thesis.json')
VWE = os.path.join(PROJECT, 'config', 'allocation_views.json')
FOUR = {'report': REPORT, 'report_status': STATUS,
        'thesis': THE, 'views': VWE}

fixt.write_collectors(DAILY, ATK)      # 非法研究日: 完整规范合成采集数据
check("P0 布局: 外链指向project根; ATK四通道采集文件物理在项目内且可解析",
      os.path.islink(LINK) and os.path.realpath(LINK) == os.path.realpath(PROJECT)
      and all(os.path.isfile(os.path.join(DAILY, f'{ch}_{ATK}.json'))
              for ch in rp.SOURCE_CHANNELS)
      and all(isinstance(json.load(open(os.path.join(DAILY, f'{ch}_{ATK}.json'))),
                         dict)
              for ch in rp.SOURCE_CHANNELS))

# ════════════════════════════════════════════════════════════════════
print("\n── POSITIVE. 物理导入正向对照(§4.3/§14.9: 文件本身合法)")

POS = (
    _DT_SRC + "\n" + _MOCKS_SRC + "\n"
    "import json, os\n"
    "import research_provenance as rp\n"
    "import snapshot_builder as sb\n"
    "assert rp.__file__.startswith(" + repr(PROJECT + os.sep) + ")\n"
    "out = " + repr(os.path.join(ISO, 'pos-out')) + "\n"
    "snap = sb.build_snapshot(target_ymd=" + repr(ATK) +
    ", data_dir=" + repr(DAILY) + ", out_dir=out,\n"
    "    as_of=" + repr(AS_OF_ATK) + ")\n"
    "src = snap.get('sources_status') or {}\n"
    "print('@POS@' + json.dumps({\n"
    " 'gate': (snap.get('gate_a') or {}).get('status'),\n"
    " 'files': {k: bool((v or {}).get('file')) for k, v in src.items()},\n"
    " 'phys_probs': rp.trusted_dir_problems(" + repr(DAILY) + "),\n"
    " 'root': rp.default_trusted_root()}))\n"
)
r_pos = sub_run([os.path.join(PROJECT, 'scripts')], POS, ISO)
o_pos = marker(r_pos, '@POS@')
check("P1 正向对照(物理导入): 同批ATK文件Gate A=PASS+四通道全选+物理目录无"
      "信任问题——拒绝只能来自路径入口而非数据缺陷",
      r_pos.returncode == 0 and o_pos and o_pos['gate'] == 'PASS'
      and all(o_pos['files'].values()) and o_pos['phys_probs'] == []
      and os.path.realpath(o_pos['root']) == os.path.realpath(PROJECT),
      r_pos.stderr[-300:] if o_pos is None else str(o_pos)[:300])

# ════════════════════════════════════════════════════════════════════
print("\n── PUBLISH. 物理导入真实发布历史合格报告(§FIX11-02)")

PUBD = (
    _DT_SRC + "\n" + _MOCKS_SRC + "\n"
    "import io, json, os, contextlib\n"
    "import research_provenance as rp\n"
    "import snapshot_builder as sb\n"
    "import data_assembler as da\n"
    "import report_generator as rg\n"
    "assert rp.__file__.startswith(" + repr(PROJECT + os.sep) + ")\n"
    "assert rg.__file__.startswith(" + repr(PROJECT + os.sep) + ")\n"
    "import fixt\n"
    "fixt.build_full_day(" + repr(PROJECT) + ", " + repr(PUB) + ")\n"
    "glm_log = []\n"
    "_install_publish_mocks(rg, glm_log)\n"
    "applied = []\n"
    "rg.apply_status_updates = (lambda *a, **k: applied.append(1))\n"
    "rg.datetime = _DT(" + repr(PUB) + ")\n"
    "buf = io.StringIO()\n"
    "rc = 0\n"
    "try:\n"
    "    with contextlib.redirect_stdout(buf):\n"
    "        rg.generate_weekly_report()\n"
    "except SystemExit as e:\n"
    "    rc = e.code\n"
    "rep = os.path.join(" + repr(OUTW) + ", 'weekly_report_" + PUB + ".md')\n"
    "st = os.path.join(" + repr(OUTW) + ", 'report_status_" + PUB + ".json')\n"
    "view, reason_v = rp.formal_report_view(rep)\n"
    "print('@PUB@' + json.dumps({'rc': rc, 'glm': len(glm_log),\n"
    " 'report': os.path.exists(rep), 'status': os.path.exists(st),\n"
    " 'formal': view is not None, 'formal_reason': reason_v or '',\n"
    " 'published': (json.load(open(st)).get('published') if os.path.exists(st) else None),\n"
    " 'applied': len(applied)}))\n"
)
r_pub = sub_run([os.path.join(PROJECT, 'scripts'), _HERE], PUBD, ISO)
o_pub = marker(r_pub, '@PUB@')
check("P2 真实发布事务(物理导入子进程): exit=0+GLM恰1次+报告/状态落盘",
      r_pub.returncode == 0 and o_pub and o_pub['rc'] == 0
      and o_pub['glm'] == 1 and o_pub['report'] and o_pub['status'],
      (r_pub.stderr[-400:] if o_pub is None else str(o_pub)[:300]))
_vpub, _rpub = rp.formal_report_view(REPORT)
_scan_pub = rp.scan_formal_weekly_reports(OUTW)
check("P2b 前置断言: formal_report_view接受真实发布报告+扫描识别为已发布"
      "(失败则本轮联合测试FAIL, 不继续保护断言)",
      _vpub is not None
      and json.load(open(STATUS)).get('published') is True
      and [v['ymd'] for v in _scan_pub] == [PUB], _rpub or 'formal reject')

# ════════════════════════════════════════════════════════════════════
print("\n── ATTACK. 同一外链标准导入子进程: 基线→非法研究链→复采(§FIX11-03/04/05)")

ATKD = (
    _DT_SRC + "\n" + _MOCKS_SRC + "\n"
    "import hashlib, io, contextlib, json, os\n"
    "import research_provenance as rp\n"
    "import snapshot_builder as sb\n"
    "import data_assembler as da\n"
    "import report_generator as rg\n"
    "PROJECT = " + repr(PROJECT) + "\n"
    "LINK = " + repr(LINK) + "\n"
    "LDD = os.path.join(LINK, 'data', 'daily')\n"
    "def sha(p):\n"
    "    return hashlib.sha256(open(p, 'rb').read()).hexdigest()\n"
    "# VERIFY-IMPORT: 四模块词法__file__均真实穿过外链, 物理归属同一项目\n"
    "mods = {'rp': rp, 'sb': sb, 'da': da, 'rg': rg}\n"
    "mf = {k: m.__file__ for k, m in mods.items()}\n"
    "mr = {k: os.path.realpath(m.__file__) for k, m in mods.items()}\n"
    "assert os.path.islink(LINK) and os.path.realpath(LINK) == os.path.realpath(PROJECT)\n"
    "assert all(v.startswith(LINK + os.sep) for v in mf.values()), mf\n"
    "assert all(v.startswith(os.path.realpath(PROJECT) + os.sep) for v in mr.values()), mr\n"
    "root = rp.default_trusted_root()\n"
    "assert os.path.realpath(root) == os.path.realpath(PROJECT), root\n"
    "probs_pre = rp.trusted_dir_problems(LDD)\n"
    "assert probs_pre != []\n"
    "REP = os.path.join(" + repr(OUTW) + ", 'weekly_report_" + PUB + ".md')\n"
    "ST = os.path.join(" + repr(OUTW) + ", 'report_status_" + PUB + ".json')\n"
    "THE = os.path.join(PROJECT, 'config', 'thesis.json')\n"
    "VWE = os.path.join(PROJECT, 'config', 'allocation_views.json')\n"
    "view_b, _rb = rp.formal_report_view(REP)\n"
    "assert view_b is not None\n"
    "# BASELINE: 危险操作之前, 本子进程内采集四对象(物理路径)SHA-256\n"
    "four = {'report': REP, 'report_status': ST, 'thesis': THE, 'views': VWE}\n"
    "before = {k: sha(p) for k, p in four.items()}\n"
    "before_via_link = {k: sha(os.path.join(LINK, 'output', 'weekly', os.path.basename(v)))\n"
    "                   for k, v in (('report', REP), ('report_status', ST))}\n"
    "scan_before = [v['ymd'] for v in rp.scan_formal_weekly_reports(" + repr(OUTW) + ")]\n"
    "# ATTACK-A 来源检查\n"
    "vsd = rp.trusted_source_dir(LDD)\n"
    "# ATTACK-B 快照构建(经外链入口; 诊断快照写回项目输出目录)\n"
    "snap = sb.build_snapshot(target_ymd=" + repr(ATK) + ", data_dir=LDD,\n"
    "    out_dir=LDD, as_of=" + repr(AS_OF_ATK) + ")\n"
    "srcst = snap.get('sources_status') or {}\n"
    "gate = (snap.get('gate_a') or {}).get('status')\n"
    "# ATTACK-C 数据装配(模块锚=外链词法DATA_DIR)\n"
    "assert os.path.normpath(os.path.dirname(str(da.DATA_DIR))) == LINK\n"
    "da.datetime = _DT(" + repr(ATK) + ")\n"
    "buf_c = io.StringIO()\n"
    "rc_c = 0\n"
    "try:\n"
    "    with contextlib.redirect_stdout(buf_c):\n"
    "        da.main()\n"
    "except SystemExit as e:\n"
    "    rc_c = e.code\n"
    "# ATTACK-D 周报预检\n"
    "ok_d, probs_d, _ctx = rg.verify_research_inputs(" + repr(ATK) + ")\n"
    "# ATTACK-E 周报完整入口(仅mock付费GLM/外部服务; 状态更新=透传spy)\n"
    "glm_log = []\n"
    "_install_publish_mocks(rg, glm_log)\n"
    "applied = []\n"
    "_orig_apply = rg.apply_status_updates\n"
    "def _spy_apply(*a, **k):\n"
    "    applied.append(1)\n"
    "    return _orig_apply(*a, **k)\n"
    "rg.apply_status_updates = _spy_apply\n"
    "rg.datetime = _DT(" + repr(ATK) + ")\n"
    "buf_e = io.StringIO()\n"
    "rc_e = 0\n"
    "try:\n"
    "    with contextlib.redirect_stdout(buf_e):\n"
    "        rg.generate_weekly_report()\n"
    "except SystemExit as e:\n"
    "    rc_e = e.code\n"
    "# ASSERT(子进程侧): 复采四对象+正式身份+扫描\n"
    "after = {k: sha(p) for k, p in four.items()}\n"
    "formal_after = rp.formal_report_view(REP)\n"
    "scan_after = [v['ymd'] for v in rp.scan_formal_weekly_reports(" + repr(OUTW) + ")]\n"
    "pub_true = sorted(f for f in os.listdir(" + repr(OUTW) + ")\n"
    "    if f.startswith('report_status_')\n"
    "    and json.load(open(os.path.join(" + repr(OUTW) + ", f))).get('published') is True)\n"
    "new_files = sorted(f for f in os.listdir(" + repr(OUTW) + ")\n"
    "    if (f.startswith('weekly_report_') or f.startswith('report_status_'))\n"
    "    and '" + PUB + "' not in f)\n"
    "print('@ATK@' + json.dumps({\n"
    " 'module_file': mf, 'module_realpath': mr, 'trusted_root': root,\n"
    " 'source_path': LDD, 'source_rejected': bool(probs_pre) and vsd[0] is None,\n"
    " 'reject_msg': (probs_pre or ['-'])[0][:120],\n"
    " 'gate_a': gate, 'sb_sources_missing': all((v or {}).get('status') == 'MISSING'\n"
    "                                            for v in srcst.values()),\n"
    " 'assembler_exit': rc_c, 'assembler_msg': buf_c.getvalue()[-200:],\n"
 " 'assembler_reject_authorized': any(k in buf_c.getvalue() for k in\n"
 "     ('不在可信项目根之内', '符号链接', 'Gate A')),\n"
    " 'verify_ok': ok_d, 'verify_problems': str(probs_d)[:200],\n"
    " 'report_exit': rc_e, 'glm_calls': len(glm_log),\n"
    " 'state_update_calls': len(applied),\n"
    " 'formal_before': view_b is not None,\n"
    " 'formal_after': formal_after is not None,\n"
    " 'four_hashes_before': before, 'four_hashes_after': after,\n"
    " 'before_via_link': before_via_link,\n"
    " 'scan_before': scan_before, 'scan_after': scan_after,\n"
    " 'new_published_count': len([f for f in pub_true if '" + ATK + "' in f]),\n"
    " 'published_only_pub_day': pub_true == ['report_status_" + PUB + ".json'],\n"
    " 'new_files': new_files}))\n"
)
r_atk = sub_run([os.path.join(LINK, 'scripts')], ATKD, ISO)
o_atk = marker(r_atk, '@ATK@')
if o_atk is None:
    check("A0 外链联合攻击子进程运行(驱动断言全过)", False,
          f"rc={r_atk.returncode} {r_atk.stderr[-500:]}")
else:
    check("A0 外链联合攻击子进程运行(驱动内全部前置断言通过)",
          r_atk.returncode == 0)
    print(f"     观测 __file__(外链导入) rp = {o_atk['module_file']['rp']}")
    print(f"     观测 __file__(外链导入) rg = {o_atk['module_file']['rg']}")
    check("A1 四模块词法__file__均穿过外链+物理归属同一项目+物理根=项目根"
          "+链接目录未授权+发布报告在本进程仍被正式读取",
          all(v.startswith(LINK + os.sep)
              for v in o_atk['module_file'].values())
          and all(v.startswith(os.path.realpath(PROJECT) + os.sep)
                  for v in o_atk['module_realpath'].values())
          and os.path.realpath(o_atk['trusted_root'])
          == os.path.realpath(PROJECT)
          and o_atk['source_rejected'] and o_atk['formal_before'])
    check("A2 来源检查拒绝: trusted_dir_problems非空+trusted_source_dir不返"
          "回授权路径, 消息可追踪信任边界",
          o_atk['source_rejected']
          and ('不在可信项目根之内' in o_atk['reject_msg']
               or '符号链接' in o_atk['reject_msg']),
          o_atk['reject_msg'])
    check("A3 快照构建fail-closed: Gate A非PASS(不可证明/FAIL)+四通道全"
          "MISSING(不以物理数据存在绕过)",
          o_atk['gate_a'] in (None, 'FAIL')
          and o_atk['sb_sources_missing'],
          f"gate={o_atk['gate_a']}")
    check("A4 数据装配拒绝: exit=2+全输出含授权/Gate拒绝(无合格正式数据包)",
          o_atk['assembler_exit'] == 2
          and o_atk['assembler_reject_authorized']
          and not os.path.exists(os.path.join(WEEKLY_DATA,
                                              f'data_pack_{ATK}.md')),
          f"rc={o_atk['assembler_exit']} {o_atk['assembler_msg'][-120:]}")
    check("A5 周报预检拒绝: verify_research_inputs不通过, 原因可追踪来源"
          "授权/Gate A",
          o_atk['verify_ok'] is False
          and any(k in o_atk['verify_problems']
                  for k in ('不在可信项目根之内', '符号链接', 'Gate A', 'FAIL')),
          o_atk['verify_problems'])
    check("A6 周报完整入口fail-closed: exit=2+GLM恰0+状态更新0次",
          o_atk['report_exit'] == 2 and o_atk['glm_calls'] == 0
          and o_atk['state_update_calls'] == 0,
          f"rc={o_atk['report_exit']} glm={o_atk['glm_calls']}")
    check("A7 四对象字节保护: before==after逐项相等(报告/状态/thesis/views)",
          o_atk['four_hashes_before'] == o_atk['four_hashes_after'],
          str([k for k in o_atk['four_hashes_before']
               if o_atk['four_hashes_before'][k]
               != o_atk['four_hashes_after'][k]]))
    check("A8 链接路径与物理路径是同一文件(非两个保护对象): 经外链读取的"
          "摘要==物理摘要",
          o_atk['before_via_link']['report']
          == o_atk['four_hashes_before']['report']
          and o_atk['before_via_link']['report_status']
          == o_atk['four_hashes_before']['report_status'])
    check("A9 正式身份保持: formal_after有效+扫描集合前后一致+无新发布日"
          "+published=true仅发布日+无新报告/状态文件",
          o_atk['formal_after']
          and o_atk['scan_after'] == o_atk['scan_before']
          and o_atk['scan_after'] == [PUB]
          and o_atk['new_published_count'] == 0
          and o_atk['published_only_pub_day']
          and o_atk['new_files'] == [],
          str(o_atk['new_files']))

# ════════════════════════════════════════════════════════════════════
print("\n── ASSERT(父进程独立复核) + SENSITIVITY(§FIX11-05/06)")

if o_atk:
    _parent_after = {k: sha(p) for k, p in FOUR.items()}
    check("B1 父进程独立复算四对象摘要==子进程after(证明摘要来自真实文件"
          "而非缓存/常量)",
          _parent_after == o_atk['four_hashes_after'])
    check("B2 诊断产物不冒充正式: EATK诊断快照存在但Gate A非PASS, 输出目录"
          "无EATK正式文件",
          (not os.path.exists(os.path.join(
              DAILY, f'research_snapshot_{ATK}.json')))
          or json.load(open(os.path.join(DAILY, f'research_snapshot_{ATK}.json')))
          ['gate_a']['status'] in (None, 'FAIL'))

with tempfile.TemporaryDirectory(prefix='fix11-sens-') as td:
    sens = {k: os.path.join(td, n) for k, n
            in (('report', 'r.md'), ('report_status', 's.json'),
                ('thesis', 't.json'), ('views', 'v.json'))}
    for k, p in sens.items():
        shutil.copy2(FOUR[k], p)
    b_sens = {p: sha(p) for p in sens.values()}
    with open(sens['thesis'], 'a', encoding='utf-8') as f:
        f.write('\n<!-- tamper -->')          # 有意篡改独立副本
    a_sens = {p: sha(p) for p in sens.values()}
    check("S1 敏感性自检: 复制四对象独立夹具中篡改thesis被摘要比较发现,"
          "且不误报未动对象",
          a_sens[sens['thesis']] != b_sens[sens['thesis']]
          and a_sens[sens['report']] == b_sens[sens['report']]
          and a_sens[sens['report_status']] == b_sens[sens['report_status']]
          and a_sens[sens['views']] == b_sens[sens['views']])

# ════════════════════════════════════════════════════════════════════
# 结构化观测输出(§十: 供独立验收核对;不预填成功结论,全部来自实际运行值)
if o_atk:
    print("\n@FIX11-JSON@ " + json.dumps({
        'module_file_rp': o_atk['module_file']['rp'],
        'module_file_rg': o_atk['module_file']['rg'],
        'module_realpath_root': o_atk['module_realpath']['rp'],
        'trusted_root': o_atk['trusted_root'],
        'source_path': o_atk['source_path'],
        'source_rejected': o_atk['source_rejected'],
        'gate_a': o_atk['gate_a'],
        'assembler_exit': o_atk['assembler_exit'],
        'report_exit': o_atk['report_exit'],
        'glm_calls': o_atk['glm_calls'],
        'state_update_calls': o_atk['state_update_calls'],
        'formal_before': o_atk['formal_before'],
        'formal_after': o_atk['formal_after'],
        'four_hashes_before': o_atk['four_hashes_before'],
        'four_hashes_after': o_atk['four_hashes_after'],
        'scan_before': o_atk['scan_before'],
        'scan_after': o_atk['scan_after'],
        'new_published_count': o_atk['new_published_count'],
    }, ensure_ascii=False))

print(f"\n{'=' * 64}\nFIX11 结果: {PASS_N} 通过 / {FAIL_N} 失败")
shutil.rmtree(ISO, ignore_errors=True)
sys.exit(1 if FAIL_N else 0)
