#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Skill 安装器回归套件(Skill 化, 2026-11-08)。

行为级(临时目录,零仓库副作用):
① 安装→物理复制(非符号链接)+SKILL.md 字节一致+engine-path.json 记录引擎根;
② 源洁净: 安装后源目录不出现 engine-path.json;
③ 幂等重跑刷新;④ 卸载移除副本且源完好;⑤ 拒绝覆盖无关目录(防误删);
⑥ 卸载对无关目录同样拒绝。
"""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTALLER = os.path.join(ROOT, 'install_skill.py')
SOURCE = os.path.join(ROOT, '.agents', 'skills', 'global-macro-research')

PASS, FAIL = 0, 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")


def run_installer(*argv):
    return subprocess.run([sys.executable, INSTALLER, *argv],
                          capture_output=True, text=True, timeout=60)


src_md = open(os.path.join(SOURCE, 'SKILL.md'), 'rb').read()

with tempfile.TemporaryDirectory() as td:
    print("═" * 60)
    print("① 安装(物理复制+路径文件)")
    print("═" * 60)
    dest = os.path.join(td, 'host', 'skills')
    r = run_installer('--dest', dest)
    d = json.loads(r.stdout)
    check("安装 rc=0 且 ok", r.returncode == 0 and d['ok'])
    skill_dir = os.path.join(dest, 'global-macro-research')
    dst_md_path = os.path.join(skill_dir, 'SKILL.md')
    check("SKILL.md 副本与源字节一致(防漂移)",
          open(dst_md_path, 'rb').read() == src_md)
    check("物理复制,非符号链接(章程: 链接不得为唯一安装方式)",
          not os.path.islink(skill_dir) and not os.path.islink(dst_md_path))
    pf = os.path.join(skill_dir, 'engine-path.json')
    check("engine-path.json 写入副本并指向引擎根",
          os.path.isfile(pf) and json.load(open(pf))['engine_root'] == ROOT)
    check("references/ 一并复制",
          os.path.isfile(os.path.join(skill_dir, 'references', 'cli-contract.md')))

    print("═" * 60)
    print("② 源洁净 + ③ 幂等")
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
    foreign = os.path.join(td, 'foreign', 'global-macro-research')
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
    print("⑤ 卸载")
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

print()
print("═" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("═" * 60)
sys.exit(0 if FAIL == 0 else 1)
