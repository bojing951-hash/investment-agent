#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Skill 安装器回归套件(Skill 化 2026-11-08;安全默认收紧 v1.1 2026-11-09)。

行为级(临时目录,零仓库/家目录副作用):
① 安装→物理复制(非符号链接)+全树字节一致+engine-path.json 记录引擎根;
② 源洁净: 安装后源目录不出现 engine-path.json;
③ 幂等重跑刷新(与源一致的副本);
④ 拒绝覆盖无关目录(防误删);
⑤ 卸载移除副本且源完好;卸载对无关目录同样拒绝;
⑥ 默认 --target project(不再默认 all 写家目录);personal 须显式(经 HOME 沙箱实证);
⑦ 装前检查: 源缺失/缺 SKILL.md/源含 engine-path.json → 拒绝;
⑧ 改过副本不静默覆盖 → 拒绝;--force → 先备份 {dest}.bak-时间戳 再替换;
   卸载改过副本同样拒绝,--force 才删;
⑨ 符号链接: --dest 父目录 realpath 归一化(装到解析后实体路径+提示);
   越出预期基目录的 resolved dest 拒绝(path_problem 单元);
⑩ 装后验证升级: 全树逐文件比对+ia_cli.py 在场+engine-path.json 可 json.loads。
"""
import importlib.util
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTALLER = os.path.join(ROOT, 'install_skill.py')
SOURCE = os.path.join(ROOT, '.agents', 'skills', 'global-macro-research')
SKILL = 'global-macro-research'

PASS, FAIL = 0, 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")


def run_installer(*argv, env=None):
    return subprocess.run([sys.executable, INSTALLER, *argv],
                          capture_output=True, text=True, timeout=60, env=env)


def load_installer_with(root, source):
    """加载 install_skill 模块并指向沙箱 ROOT/SOURCE(main 的路径全部随模块全局走)。"""
    spec = importlib.util.spec_from_file_location('isk_sandbox', INSTALLER)
    isk = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(isk)
    isk.ROOT, isk.SOURCE = root, source
    return isk


def make_sandbox_source(sb):
    """沙箱技能源(SKILL.md 带 name 头 + references/ 一份)。"""
    src = os.path.join(sb, '.agents', 'skills', SKILL)
    os.makedirs(os.path.join(src, 'references'))
    with open(os.path.join(src, 'SKILL.md'), 'w', encoding='utf-8') as fh:
        fh.write('---\nname: global-macro-research\n---\n# skill\n')
    with open(os.path.join(src, 'references', 'cli-contract.md'), 'w',
              encoding='utf-8') as fh:
        fh.write('contract\n')
    with open(os.path.join(sb, 'ia_cli.py'), 'w', encoding='utf-8') as fh:  # verify 用
        fh.write('# engine cli\n')
    return src


def main_in_proc(isk, argv):
    """进程内跑 isk.main(),捕获 (exit_code, stdout, stderr)。"""
    real_argv = sys.argv
    sys.argv = argv
    out, err = io.StringIO(), io.StringIO()
    code = None
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                isk.main()
            except SystemExit as e:
                code = e.code
    finally:
        sys.argv = real_argv
    return code, out.getvalue(), err.getvalue()


src_md = open(os.path.join(SOURCE, 'SKILL.md'), 'rb').read()

with tempfile.TemporaryDirectory() as td:
    print("═" * 60)
    print("① 安装(物理复制+全树一致+路径文件) / ⑩ 装后验证")
    print("═" * 60)
    dest = os.path.join(td, 'host', 'skills')
    r = run_installer('--dest', dest)
    d = json.loads(r.stdout)
    check("安装 rc=0 且 ok 且 verified", r.returncode == 0 and d['ok']
          and d['results'][0]['verified'])
    check("装后验证零问题", d['results'][0]['verify_problems'] == [])
    skill_dir = os.path.join(dest, SKILL)
    dst_md_path = os.path.join(skill_dir, 'SKILL.md')
    check("SKILL.md 副本与源字节一致(防漂移)",
          open(dst_md_path, 'rb').read() == src_md)
    check("物理复制,非符号链接(章程: 链接不得为唯一安装方式)",
          not os.path.islink(skill_dir) and not os.path.islink(dst_md_path))
    pf = os.path.join(skill_dir, 'engine-path.json')
    check("engine-path.json 写入副本/指向引擎根/可 json.loads",
          os.path.isfile(pf) and json.load(open(pf))['engine_root'] == ROOT)
    check("references/ 一并复制",
          os.path.isfile(os.path.join(skill_dir, 'references', 'cli-contract.md')))

    print("═" * 60)
    print("② 源洁净 + ③ 幂等(与源一致的副本重跑刷新)")
    print("═" * 60)
    check("源目录未被写入 engine-path.json",
          not os.path.isfile(os.path.join(SOURCE, 'engine-path.json')))
    r2 = run_installer('--dest', dest)
    check("重跑安装 rc=0(幂等刷新)",
          r2.returncode == 0 and json.loads(r2.stdout)['ok']
          and open(dst_md_path, 'rb').read() == src_md)

    print("═" * 60)
    print("④ 拒绝覆盖无关目录")
    print("═" * 60)
    foreign = os.path.join(td, 'foreign', SKILL)
    os.makedirs(foreign)
    with open(os.path.join(foreign, 'SKILL.md'), 'w', encoding='utf-8') as fh:
        fh.write('---\nname: someone-else-skill\n---\n')
    r3 = run_installer('--dest', os.path.join(td, 'foreign'))
    check("目标属于其他技能→拒绝覆盖",
          r3.returncode == 1
          and json.loads(r3.stdout)['ok'] is False
          and open(os.path.join(foreign, 'SKILL.md'), encoding='utf-8').read()
          .startswith('---\nname: someone-else-skill'))

    print("═" * 60)
    print("⑤ 卸载(源完好/无关目录拒绝)")
    print("═" * 60)
    r4 = run_installer('--dest', dest, '--uninstall')
    check("卸载 rc=0,副本目录移除",
          r4.returncode == 0 and json.loads(r4.stdout)['ok']
          and not os.path.exists(skill_dir))
    check("卸载后源完好",
          open(os.path.join(SOURCE, 'SKILL.md'), 'rb').read() == src_md)
    r5 = run_installer('--dest', os.path.join(td, 'foreign'), '--uninstall')
    check("卸载对无关目录拒绝删除",
          r5.returncode == 1 and os.path.exists(foreign))

    print("═" * 60)
    print("⑥ 改过副本: 不静默覆盖 / --force 备份 / 卸载保护")
    print("═" * 60)
    r = run_installer('--dest', dest)  # 重新装一份
    mod_file = os.path.join(dest, SKILL, 'references', 'cli-contract.md')
    with open(mod_file, 'a', encoding='utf-8') as fh:
        fh.write('\n用户本地批注\n')
    r6 = run_installer('--dest', dest)
    d6 = json.loads(r6.stdout)
    check("改过副本重装→拒绝(rc=1)且改动保留",
          r6.returncode == 1 and d6['ok'] is False
          and '用户本地批注' in open(mod_file, encoding='utf-8').read())
    check("拒绝信息披露本地修改文件清单",
          'local_modifications' in d6['results'][0]
          and any('cli-contract' in m for m in d6['results'][0]['local_modifications']))
    r7 = run_installer('--dest', dest, '--force')
    d7 = json.loads(r7.stdout)
    baks = [p for p in os.listdir(dest) if p.startswith(f'{SKILL}.bak-')]
    check("--force → 旧目录先备份再替换(备份在场且含用户改动)",
          r7.returncode == 0 and len(baks) == 1
          and '用户本地批注' in open(os.path.join(
              dest, baks[0], 'references', 'cli-contract.md'), encoding='utf-8').read(),
          str(baks))
    check("--force 替换后副本与源一致(改动不在新副本)",
          open(mod_file, 'rb').read()
          == open(os.path.join(SOURCE, 'references', 'cli-contract.md'), 'rb').read())
    with open(mod_file, 'a', encoding='utf-8') as fh:
        fh.write('\n再改一处\n')
    r8 = run_installer('--dest', dest, '--uninstall')
    check("卸载改过副本→拒绝(防丢改动)",
          r8.returncode == 1 and os.path.exists(os.path.join(dest, SKILL)))
    r9 = run_installer('--dest', dest, '--uninstall', '--force')
    check("卸载 --force → 删除", r9.returncode == 0
          and not os.path.exists(os.path.join(dest, SKILL)))

    print("═" * 60)
    print("⑦ 符号链接: 归一化 + 越界拒绝")
    print("═" * 60)
    realparent = os.path.join(td, 'realparent', 'skills')
    os.makedirs(realparent)
    alias = os.path.join(td, 'alias', 'skills')
    os.makedirs(os.path.dirname(alias))
    os.symlink(realparent, alias)
    r10 = run_installer('--dest', alias)
    check("--dest 父目录为符号链接 → 装到解析后实体路径",
          r10.returncode == 0
          and os.path.isfile(os.path.join(realparent, SKILL, 'SKILL.md')))
    check("stderr 提示解析后安装位置", '解析后安装位置' in r10.stderr
          and os.path.realpath(alias) in r10.stderr)
    # 越界拒绝(path_problem 单元: resolved dest 不在预期基目录内)
    with tempfile.TemporaryDirectory() as sb:
        isk = load_installer_with(sb, os.path.join(sb, '.agents', 'skills', SKILL))
        prob = isk.path_problem(os.path.join(td, 'elsewhere', SKILL),
                                base=os.path.join(sb, '.claude', 'skills'))
        check("resolved dest 越出预期基目录 → 拒绝", prob is not None
              and '越出预期基目录' in prob, str(prob))
        check("基目录内 dest → 放行",
              isk.path_problem(os.path.join(sb, '.claude', 'skills', SKILL),
                               base=os.path.join(sb, '.claude', 'skills')) is None)

    print("═" * 60)
    print("⑧ 装前检查(源缺失/缺 SKILL.md/源被污染)")
    print("═" * 60)
    with tempfile.TemporaryDirectory() as sb:
        isk = load_installer_with(sb, os.path.join(sb, '.agents', 'skills', SKILL))
        code, out, _err = main_in_proc(isk, ['install_skill.py'])
        check("源目录不存在 → die(rc=1)", code == 1 and '技能源不存在' in out)
        src2 = make_sandbox_source(sb)
        code, out, _err = main_in_proc(isk, ['install_skill.py'])
        check("沙箱源齐备 → 默认 target=project 安装成功",
              code == 0 and os.path.isfile(os.path.join(
                  sb, '.claude', 'skills', SKILL, 'SKILL.md')))
        d8 = json.loads(out)
        check("默认仅处理 project 一个目标(不再默认 all 写家目录)",
              len(d8['results']) == 1 and d8['results'][0]['target']
              == os.path.realpath(os.path.join(sb, '.claude', 'skills', SKILL)),
              str(d8['results'][0]['target']))
        with open(os.path.join(src2, 'engine-path.json'), 'w') as fh:
            fh.write('{}')
        code, out, _err = main_in_proc(isk, ['install_skill.py'])
        check("源含 engine-path.json(产物混入)→ die",
              code == 1 and '安装产物混入源' in out)

    print("═" * 60)
    print("⑨ personal 须显式(HOME 沙箱实证)")
    print("═" * 60)
    with tempfile.TemporaryDirectory() as home:
        env = dict(os.environ, HOME=home)
        r11 = run_installer('--target', 'personal-cc', env=env)
        check("--target personal-cc → 装入 $HOME/.claude/skills",
              r11.returncode == 0 and os.path.isfile(os.path.join(
                  home, '.claude', 'skills', SKILL, 'SKILL.md')))
        r12 = run_installer(env=env)  # 默认 project,不碰家目录
        d12 = json.loads(r12.stdout)
        home_touched = os.path.exists(os.path.join(home, '.claude', 'skills', SKILL))
        check("默认运行不写家目录(personal 仅显式时)",
              r12.returncode == 0 and len(d12['results']) == 1
              and not any('skills' in r['target'] and r['target'].startswith(home)
                          for r in d12['results']))

print()
print("═" * 60)
print("⑪ 装机副本防漂移: 零 --glm/零旧键名(D1,2026-11-09)")
print("═" * 60)
# 缺陷回放(D1): ~/.claude 装机副本过期(mtime 11-08),仍教 research --glm
# (旗标已删,照做 rc=2)/glm_key_note/glm?/GLM_API_KEY/bigmodel——源已清而
# 副本漂移。锁: 新装副本+在场装机副本一律零旧键名。
import re as _re

_DRIFT_PATTERNS = [(_re.compile(r'--glm\b'), '--glm 旗标'),
                   (_re.compile(r'GLM_API_KEY'), '旧密钥变量名'),
                   (_re.compile(r'glm_key_note'), '旧医生面键'),
                   (_re.compile(r'\bglm\?'), '旧输出键 glm?'),
                   (_re.compile(r'bigmodel'), '厂商端点')]


def _scan_installed_copy(base, label):
    """扫描装机副本文本文件;返回命中清单(空=洁净)。副本缺席→None。"""
    skill_dir = os.path.join(base, SKILL)
    if not os.path.isdir(skill_dir):
        return None
    hits = []
    for dirpath, _dirnames, filenames in os.walk(skill_dir):
        for fn in filenames:
            if not fn.endswith(('.md', '.json')):
                continue
            fp = os.path.join(dirpath, fn)
            try:
                text = open(fp, encoding='utf-8', errors='replace').read()
            except OSError:
                continue
            for pat, label2 in _DRIFT_PATTERNS:
                for m in pat.finditer(text):
                    hits.append(f'{label}: {os.path.relpath(fp, base)}: {label2}')
    return hits


with tempfile.TemporaryDirectory() as td2:
    dest2 = os.path.join(td2, 'skills')
    r13 = run_installer('--dest', dest2)
    check("新装副本可安装(⑪前置)", r13.returncode == 0)
    hits = _scan_installed_copy(dest2, '新装')
    check("新装副本零 --glm/零旧键名(源洁则副本洁)",
          hits == [], '; '.join(hits[:4]))

for base, label, strict in (
        (os.path.join(ROOT, '.claude', 'skills'), '项目级装机副本', True),
        (os.path.expanduser('~/.claude/skills'), '个人级装机副本', True)):
    hits = _scan_installed_copy(base, label)
    if hits is None:
        print(f"  ℹ️ {label}不在场({base})——跳过(CI 干净克隆属正常)")
    else:
        check(f"{label}零 --glm/零旧键名(防漂移;过期须重装 --force)",
              hits == [], '; '.join(hits[:4]))

print()
print("═" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("═" * 60)
sys.exit(0 if FAIL == 0 else 1)
