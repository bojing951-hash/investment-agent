#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""install_skill.py — global-macro-research 技能安装器(2026-11-08)。

单一权威源: 仓库 .agents/skills/global-macro-research/(随 git 分发,
Codex 仓库级零安装即发现)。本安装器把源**物理复制**到各宿主目录
(章程: 禁止符号链接作为唯一安装方式;两宿主均支持实体复制):

  project        → <仓库>/.claude/skills/global-macro-research   (Claude Code 项目级)
  personal-cc    → ~/.claude/skills/global-macro-research        (Claude Code 个人级)
  personal-codex → ~/.agents/skills/global-macro-research        (Codex 用户级)

个人级副本写入 engine-path.json(记录引擎根,供 SKILL.md 第三级路径解析);
仓库源永不包含 engine-path.json(不提交个人路径)。
用法: python3 install_skill.py [--target project|personal-cc|personal-codex|all]
                               [--dest DIR](测试: 安装到任意目录)
                               [--uninstall]
"""
import argparse
import json
import os
import shutil
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
SKILL_NAME = 'global-macro-research'
SOURCE = os.path.join(ROOT, '.agents', 'skills', SKILL_NAME)
PATH_FILE = 'engine-path.json'


def die(msg, code=1):
    print(json.dumps({'ok': False, 'error': msg}, ensure_ascii=False))
    sys.exit(code)


def target_dirs(target, dest):
    home = os.path.expanduser('~')
    if dest:  # 测试/自定义: 安装为 <dest>/<skill_name>
        return {'custom': os.path.join(dest, SKILL_NAME)}
    out = {}
    if target in ('project', 'all'):
        out['project'] = os.path.join(ROOT, '.claude', 'skills', SKILL_NAME)
    if target in ('personal-cc', 'all'):
        out['personal-cc'] = os.path.join(home, '.claude', 'skills', SKILL_NAME)
    if target in ('personal-codex', 'all'):
        out['personal-codex'] = os.path.join(home, '.agents', 'skills', SKILL_NAME)
    return out


def is_our_install(path):
    """仅当目录内 SKILL.md 属于本技能才允许卸载(防误删用户其他目录)。"""
    skill_md = os.path.join(path, 'SKILL.md')
    if not os.path.isfile(skill_md):
        return False
    try:
        with open(skill_md, encoding='utf-8') as fh:
            head = fh.read(400)
    except OSError:
        return False
    return f'name: {SKILL_NAME}' in head


def install_one(dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.islink(dest):  # 历史链接残留: 换成实体复制(链接是搬移脆弱点)
        os.unlink(dest)
    elif os.path.isdir(dest):
        if not is_our_install(dest):
            return {'target': dest, 'ok': False,
                    'error': '目标已存在且不属于本技能,拒绝覆盖'}
        shutil.rmtree(dest)
    shutil.copytree(SOURCE, dest)  # 物理复制,非符号链接
    with open(os.path.join(dest, PATH_FILE), 'w', encoding='utf-8') as fh:
        json.dump({'engine_root': ROOT, 'skill': SKILL_NAME,
                   'installed_at': time.strftime('%Y-%m-%dT%H:%M:%S+08:00'),
                   'source': 'install_skill.py(物理复制,重跑可刷新)'}, fh,
                  ensure_ascii=False, indent=2)
    # 安装后自检: 副本与源字节一致 + 引擎入口在场
    src_md = os.path.join(SOURCE, 'SKILL.md')
    dst_md = os.path.join(dest, 'SKILL.md')
    identical = (open(src_md, 'rb').read() == open(dst_md, 'rb').read())
    engine_ok = os.path.isfile(os.path.join(ROOT, 'ia_cli.py'))
    return {'target': dest, 'ok': identical and engine_ok,
            'byte_identical': identical, 'engine_cli_present': engine_ok}


def uninstall_one(dest):
    if os.path.islink(dest):
        os.unlink(dest)
        return {'target': dest, 'ok': True, 'removed': 'symlink'}
    if not os.path.isdir(dest):
        return {'target': dest, 'ok': True, 'removed': None}
    if not is_our_install(dest):
        return {'target': dest, 'ok': False,
                'error': '目标不属于本技能(无对应 SKILL.md),拒绝删除'}
    shutil.rmtree(dest)
    return {'target': dest, 'ok': True, 'removed': 'directory'}


def main():
    ap = argparse.ArgumentParser(description='global-macro-research 技能安装器')
    ap.add_argument('--target', default='all',
                    choices=['project', 'personal-cc', 'personal-codex', 'all'])
    ap.add_argument('--dest', help='安装到自定义目录(测试用;代替 --target)')
    ap.add_argument('--uninstall', action='store_true',
                    help='移除已安装副本(仓库源不受影响)')
    args = ap.parse_args()

    if not os.path.isdir(SOURCE):
        die(f'技能源不存在: {SOURCE}')
    if not os.path.isfile(os.path.join(SOURCE, 'SKILL.md')):
        die('源目录缺 SKILL.md')
    # 源洁净性: 仓库源不得携带 engine-path.json(个人路径零入库)
    if os.path.isfile(os.path.join(SOURCE, PATH_FILE)):
        die(f'源目录含 {PATH_FILE}(安装产物混入源),请删除后重试')

    results = [uninstall_one(d) if args.uninstall else install_one(d)
               for d in target_dirs(args.target, args.dest).values()]
    ok = all(r['ok'] for r in results)
    print(json.dumps({'ok': ok, 'action': 'uninstall' if args.uninstall else 'install',
                      'source': SOURCE, 'results': results}, ensure_ascii=False, indent=2))
    if not args.uninstall:
        print('已安装。Claude Code 重启会话或 /skills 查看;Codex 在仓库内直接可用'
              '(仓库级源零安装)。', file=sys.stderr)
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
