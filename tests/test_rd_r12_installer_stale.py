#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R12 安装器「装机副本须 --force」坑修复套件(2026-11-12,dev/rd-r12-ac9-clean)。

坑(AC9 已知项,v0.5.0 登记): local_modifications 只对比**当前**源树,分不清
「用户改过已装副本」与「装机面停在源树旧版」——git pull 升级后重装被一律
拒绝逼 --force,常规升级路径被破坏。

修复语义(matches_source_history): 已装副本树(排除 engine-path.json)映射为
{相对路径: git blob sha},与源目录在 git 历史各版本的 ls-tree 比对;命中任一
历史版本=装机面为旧版(内容在仓库逐字节存在过,无用户改动)→ 幂等升级刷新/
径直卸载,不逼 --force 不备份。非 git 环境(archive/ZIP 装机)无历史可查→
保守回落旧语义(仍拒,仍可 --force)。

全部临时目录夹具+真 git 子进程(init/commit,离线),独立期望零真实仓库依赖。
运行: ~/AI内容/venv/bin/python3 tests/test_rd_r12_installer_stale.py
"""
import importlib.util
import io
import json
import contextlib
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTALLER = os.path.join(ROOT, 'install_skill.py')
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


def load_installer(root, source):
    spec = importlib.util.spec_from_file_location('isk_r12', INSTALLER)
    isk = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(isk)
    isk.ROOT, isk.SOURCE = root, source
    return isk


def git(sb, *argv):
    r = subprocess.run(['git', '-C', sb, *argv], capture_output=True, text=True)
    assert r.returncode == 0, (argv, r.stderr)
    return r.stdout


def make_git_sandbox():
    """git 沙箱仓: 源 v1(SKILL.md+references)+ia_cli.py,首提交完成。"""
    sb = tempfile.mkdtemp(prefix='r12_git_')
    src = os.path.join(sb, '.agents', 'skills', SKILL)
    os.makedirs(os.path.join(src, 'references'))
    with open(os.path.join(src, 'SKILL.md'), 'w', encoding='utf-8') as fh:
        fh.write('---\nname: global-macro-research\n---\n# skill v1\n')
    with open(os.path.join(src, 'references', 'cli-contract.md'), 'w',
              encoding='utf-8') as fh:
        fh.write('contract v1\n')
    with open(os.path.join(sb, 'ia_cli.py'), 'w', encoding='utf-8') as fh:
        fh.write('# engine cli\n')
    git(sb, 'init', '-q')
    git(sb, 'add', '-A')
    git(sb, '-c', 'user.email=t@t', '-c', 'user.name=t', 'commit', '-q',
        '-m', 'v1')
    return sb, os.path.join(sb, '.claude', 'skills', SKILL)


def bump_source(sb, text):
    """源版本前滚(SKILL.md 追加)并提交。"""
    p = os.path.join(sb, '.agents', 'skills', SKILL, 'SKILL.md')
    with open(p, 'a', encoding='utf-8') as fh:
        fh.write(text)
    git(sb, 'add', '-A')
    git(sb, '-c', 'user.email=t@t', '-c', 'user.name=t', 'commit', '-q',
        '-m', 'bump')


print("=" * 72)

# ══ [1] 升级路径: 旧版装机面重装零旗标直过 ═══════════════════════════
print("\n[1] 旧版装机面(=源历史版本)重装")
sb, dest = make_git_sandbox()
isk = load_installer(sb, os.path.join(sb, '.agents', 'skills', SKILL))
r1 = isk.install_one(dest)
check("v1 首装 ok+verified", r1.get('ok') and r1.get('verified'), str(r1))
bump_source(sb, '\n<!-- v2 -->\n')
r2 = isk.install_one(dest)
check("源前滚后重装: ok 不再逼 --force", r2.get('ok'), str(r2)[:120])
check("结果带 stale_version_refreshed 标", r2.get('stale_version_refreshed') is True,
      str(r2))
check("无备份目录产生(无用户改动可丢)",
      not any(f.startswith(SKILL + '.bak') for f in os.listdir(os.path.dirname(dest))))
with open(os.path.join(dest, 'SKILL.md'), encoding='utf-8') as fh:
    check("副本内容已升级到 v2", '<!-- v2 -->' in fh.read())

# ══ [2] 用户真修改面: 拒绝/--force 备份语义保持 ═════════════════════
print("\n[2] 用户真修改面语义保持")
with open(os.path.join(dest, 'SKILL.md'), 'a', encoding='utf-8') as fh:
    fh.write('\n我的笔记(任何历史版本都没有的内容)\n')
r3 = isk.install_one(dest)
check("真修改面拒绝+列修改文件", not r3.get('ok')
      and 'local_modifications' in r3, str(r3)[:120])
r4 = isk.install_one(dest, force=True)
check("--force 覆盖 ok+备份目录在场", r4.get('ok') and r4.get('backup')
      and os.path.isdir(r4['backup']), str(r4)[:120])

# ══ [3] 非 git 装机面: 保守回落(仍拒) ═══════════════════════════════
print("\n[3] 非 git 环境(archive/ZIP 装机)")
sb2 = tempfile.mkdtemp(prefix='r12_nogit_')
src2 = os.path.join(sb2, '.agents', 'skills', SKILL)
os.makedirs(os.path.join(src2, 'references'))
with open(os.path.join(src2, 'SKILL.md'), 'w', encoding='utf-8') as fh:
    fh.write('---\nname: global-macro-research\n---\n# v1\n')
with open(os.path.join(sb2, 'ia_cli.py'), 'w', encoding='utf-8') as fh:
    fh.write('# cli\n')
isk2 = load_installer(sb2, src2)
dest2 = os.path.join(sb2, '.claude', 'skills', SKILL)
isk2.install_one(dest2)
with open(os.path.join(src2, 'SKILL.md'), 'a', encoding='utf-8') as fh:
    fh.write('\n<!-- v2 无 git -->\n')
r5 = isk2.install_one(dest2)
check("非 git 漂移面仍拒绝(matches_source_history=False 回落)",
      not r5.get('ok') and 'local_modifications' in r5, str(r5)[:120])
r5f = isk2.install_one(dest2, force=True)
check("非 git --force 仍可覆盖(既有逃生门保持)", r5f.get('ok'), str(r5f)[:120])

# ══ [4] 卸载面: 旧版装机面径直卸载 ═════════════════════════════════
print("\n[4] 卸载面同语义")
sb3, dest3 = make_git_sandbox()
isk3 = load_installer(sb3, os.path.join(sb3, '.agents', 'skills', SKILL))
isk3.install_one(dest3)
bump_source(sb3, '\n<!-- v2b -->\n')
u1 = isk3.uninstall_one(dest3)
check("旧版装机面卸载零旗标 ok", u1.get('ok') and not os.path.exists(dest3),
      str(u1))
sb4, dest4 = make_git_sandbox()
isk4 = load_installer(sb4, os.path.join(sb4, '.agents', 'skills', SKILL))
isk4.install_one(dest4)
with open(os.path.join(dest4, 'SKILL.md'), 'a', encoding='utf-8') as fh:
    fh.write('\n用户改动\n')
u2 = isk4.uninstall_one(dest4)
check("真修改面卸载仍拒绝(回归)", not u2.get('ok') and 'local_modifications' in u2,
      str(u2)[:120])

# ══ [5] 幂等与单元 ═════════════════════════════════════════════════
print("\n[5] 幂等/单元")
sb5, dest5 = make_git_sandbox()
isk5 = load_installer(sb5, os.path.join(sb5, '.agents', 'skills', SKILL))
isk5.install_one(dest5)
r6 = isk5.install_one(dest5)
check("与当前源一致的副本幂等刷新(无 stale 标,既有行为)",
      r6.get('ok') and 'stale_version_refreshed' not in r6, str(r6))
sb6, dest6 = make_git_sandbox()
isk6 = load_installer(sb6, os.path.join(sb6, '.agents', 'skills', SKILL))
isk6.install_one(dest6)
bump_source(sb6, '\n<!-- v2c -->\n')
check("matches_source_history 单元: 旧版面=True",
      isk6.matches_source_history(dest6) is True)
with open(os.path.join(dest6, 'SKILL.md'), 'a', encoding='utf-8') as fh:
    fh.write('\nx\n')
check("matches_source_history 单元: 真修改面=False",
      isk6.matches_source_history(dest6) is False)
with open(os.path.join(dest6, 'extra_new_file.md'), 'w', encoding='utf-8') as fh:
    fh.write('new\n')
os.remove(os.path.join(dest6, 'extra_new_file.md'))
# 删一个历史文件=非任何历史版本 → False
os.remove(os.path.join(dest6, 'references', 'cli-contract.md'))
check("matches_source_history 单元: 缺历史文件面=False",
      isk6.matches_source_history(dest6) is False)
gh = subprocess.run(['git', '-C', sb6, 'hash-object', '--stdin'],
                    input='hello', capture_output=True, text=True).stdout.strip()
check("_blob_sha 与 git hash-object 同口径", isk6._blob_sha(b'hello') == gh,
      f"{isk6._blob_sha(b'hello')} vs {gh}")

print("\n" + "=" * 72)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 72)
sys.exit(0 if FAIL == 0 else 1)
