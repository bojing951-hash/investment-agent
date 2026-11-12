#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""install_skill.py — global-macro-research 技能安装器(2026-11-08;安全收紧 v1.1 2026-11-09)。

单一权威源: 仓库 .agents/skills/global-macro-research/(随 git 分发,
Codex 仓库级零安装即发现)。本安装器把源**物理复制**到各宿主目录
(章程: 禁止符号链接作为唯一安装方式;两宿主均支持实体复制):

  project        → <仓库>/.claude/skills/global-macro-research   (Claude Code 项目级)
  personal-cc    → ~/.claude/skills/global-macro-research        (Claude Code 个人级)
  personal-codex → ~/.agents/skills/global-macro-research        (Codex 用户级)

个人级副本写入 engine-path.json(记录引擎根,供 SKILL.md 第三级路径解析);
仓库源永不包含 engine-path.json(不提交个人路径)。

安全默认(第三轮 P0 收紧):
  - 默认 --target project(此前默认 all 会静默写用户家目录;个人级须显式指定);
  - 已装副本相对源树有本地修改(排除 engine-path.json)→ 拒绝覆盖/卸载,防静默
    丢失用户改动;--force 覆盖前先把旧目录备份为 {dest}.bak-YYYYmmdd-HHMMSS;
  - dest 父目录 realpath 归一化(符号链接别名展开);project/personal 目标
    解析后越出预期基目录 → 拒绝;--dest 自定义路径打印解析后路径;
  - 装后验证=全树逐文件字节比对 + ia_cli.py 存在 + engine-path.json 可解析
    (此前仅验 SKILL.md 单文件字节)。

用法: python3 install_skill.py [--target project|personal-cc|personal-codex|all]
                               [--dest DIR](测试: 安装到任意目录)
                               [--force](覆盖/卸载有本地修改的副本,覆盖前备份)
                               [--uninstall]
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
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


def target_bases(home):
    """project/personal 目标的预期基目录(越界拒绝用);custom 无基目录(用户自担)。"""
    return {'project': os.path.join(ROOT, '.claude', 'skills'),
            'personal-cc': os.path.join(home, '.claude', 'skills'),
            'personal-codex': os.path.join(home, '.agents', 'skills')}


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


def _tree_state(path):
    """目录树状态: {相对路径: 文件字节};排除安装器产物 engine-path.json。"""
    out = {}
    for base, _dirs, files in os.walk(path):
        for fn in files:
            full = os.path.join(base, fn)
            rel = os.path.relpath(full, path)
            if rel == PATH_FILE:
                continue
            with open(full, 'rb') as fh:
                out[rel] = fh.read()
    return out


def local_modifications(dest):
    """已装副本相对源树的本地修改清单(增/删/改,排除 engine-path.json);空=无差异。"""
    src, dst = _tree_state(SOURCE), _tree_state(dest)
    return sorted(set(src) ^ set(dst)) + sorted(
        k for k in set(src) & set(dst) if src[k] != dst[k])


def resolved_dest(dest):
    """dest 父目录 realpath 归一化(展开祖先符号链接别名;dest 自身符号链接由
    install_one/uninstall_one 的 unlink 逻辑处理,不在归一化范围)。"""
    return os.path.join(os.path.realpath(os.path.dirname(dest)),
                        os.path.basename(dest))


def path_problem(dest, base):
    """project/personal 目标越界检查: 解析后 dest 必须仍在预期基目录内。"""
    if base is None:
        return None
    rdest, rbase = resolved_dest(dest), os.path.realpath(base)
    try:
        inside = os.path.commonpath([rdest, rbase]) == rbase
    except ValueError:
        inside = False
    if not inside:
        return (f'解析后目标 {rdest} 越出预期基目录 {rbase}'
                '(祖先符号链接重定向?),拒绝')
    return None


def verify_install(dest):
    """装后验证: 全树逐文件字节比对 + 引擎入口在场 + engine-path.json 可解析。"""
    problems = []
    mods = local_modifications(dest)
    if mods:
        problems.append(f'副本与源树字节不一致: {mods[:5]}')
    if not os.path.isfile(os.path.join(ROOT, 'ia_cli.py')):
        problems.append('引擎入口 ia_cli.py 不存在')
    try:
        with open(os.path.join(dest, PATH_FILE), encoding='utf-8') as fh:
            json.load(fh)
    except (OSError, ValueError) as e:
        problems.append(f'{PATH_FILE} 不可解析: {e}')
    return problems


def _git_root():
    """ROOT 所在 git 仓库根;非 git 环境(archive/ZIP 装机)→ None。"""
    try:
        r = subprocess.run(['git', '-C', ROOT, 'rev-parse', '--show-toplevel'],
                           capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def _blob_sha(data):
    """git blob 对象 sha1(内容寻址;与 git ls-tree 的 objectname 同口径)。"""
    return hashlib.sha1(b'blob %d\x00%s' % (len(data), data)).hexdigest()


def matches_source_history(dest, max_commits=64):
    """已装副本是否与源树**任一历史版本**逐字节一致(R12 语义修正)。

    local_modifications 只对比当前源,分不清「用户改过」与「装机面停在旧版」:
    后者是常规升级场景(git pull 后重装),旧语义一律拒装逼 --force(v0.5.0 登记
    的「装机副本须 --force」坑)。本函数把副本树映射为 {相对路径: blob sha},
    与 git 历史中源目录各版本 ls-tree 比对;命中任一历史版本=非用户改动
    (副本内容在仓库里逐字节存在过),可走幂等升级刷新,无需 --force/备份。
    非 git 环境无历史可查 → False(保守回落旧语义)。
    """
    groot = _git_root()
    if not groot:
        return False
    # git 返回的是 realpath(/private/tmp ↔ /tmp);SOURCE 须同口径归一,否则
    # relpath 算出跨符号链接的 ../ 链,git log 路径过滤必空(macOS tmp 夹具踩过)
    rel_src = os.path.relpath(os.path.realpath(SOURCE), groot)
    try:
        log = subprocess.run(
            ['git', '-C', groot, 'log', '--format=%H', '-n', str(max_commits),
             '--', rel_src], capture_output=True, text=True, timeout=30)
        if log.returncode != 0:
            return False
        installed = {}
        for base, _dirs, files in os.walk(dest):
            for fn in files:
                rel = os.path.relpath(os.path.join(base, fn), dest)
                if rel == PATH_FILE:
                    continue
                with open(os.path.join(base, fn), 'rb') as fh:
                    installed[rel] = _blob_sha(fh.read())
        for commit in log.stdout.split():
            ls = subprocess.run(
                ['git', '-C', groot, 'ls-tree', '-r', commit, '--', rel_src],
                capture_output=True, text=True, timeout=30)
            if ls.returncode != 0:
                continue
            hist = {}
            for line in ls.stdout.splitlines():
                meta, path = line.split('\t', 1)
                sha = meta.split()[2]
                hist[os.path.relpath(path, rel_src)] = sha
            if installed == hist:
                return True
    except (OSError, ValueError, subprocess.SubprocessError):
        return False
    return False


def install_one(dest, force=False):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    backup = None
    stale_refresh = False
    if os.path.islink(dest):  # 历史链接残留: 换成实体复制(链接是搬移脆弱点)
        os.unlink(dest)
    elif os.path.isdir(dest):
        if not is_our_install(dest):
            return {'target': dest, 'ok': False,
                    'error': '目标已存在且不属于本技能,拒绝覆盖'}
        mods = local_modifications(dest)
        if mods:
            if matches_source_history(dest):
                # 装机面停在源树某历史版本(非用户改动): 幂等升级刷新
                shutil.rmtree(dest)
                stale_refresh = True
            elif not force:
                return {'target': dest, 'ok': False,
                        'error': '已装副本相对源树有本地修改,拒绝覆盖'
                                 '(防静默丢失改动);确需覆盖用 --force(旧目录先备份)',
                        'local_modifications': mods[:10]}
            else:
                backup = f"{dest}.bak-{time.strftime('%Y%m%d-%H%M%S')}"
                shutil.move(dest, backup)  # 先备份再替换,不静默销毁用户改动
        else:
            shutil.rmtree(dest)  # 与源一致的副本: 幂等刷新
    shutil.copytree(SOURCE, dest)  # 物理复制,非符号链接
    with open(os.path.join(dest, PATH_FILE), 'w', encoding='utf-8') as fh:
        json.dump({'engine_root': ROOT, 'skill': SKILL_NAME,
                   'installed_at': time.strftime('%Y-%m-%dT%H:%M:%S+08:00'),
                   'source': 'install_skill.py(物理复制,重跑可刷新)'}, fh,
                  ensure_ascii=False, indent=2)
    # 装后验证(全树字节级,不再只验 SKILL.md 单文件)
    problems = verify_install(dest)
    out = {'target': dest, 'ok': not problems, 'verified': not problems,
           'verify_problems': problems}
    if backup:
        out['backup'] = backup
    if stale_refresh:
        out['stale_version_refreshed'] = True
    return out


def uninstall_one(dest, force=False):
    if os.path.islink(dest):
        os.unlink(dest)
        return {'target': dest, 'ok': True, 'removed': 'symlink'}
    if not os.path.isdir(dest):
        return {'target': dest, 'ok': True, 'removed': None}
    if not is_our_install(dest):
        return {'target': dest, 'ok': False,
                'error': '目标不属于本技能(无对应 SKILL.md),拒绝删除'}
    mods = local_modifications(dest)
    if mods and not force and not matches_source_history(dest):
        # R12: 停在历史版本的装机面可径直卸载(无用户改动可丢),仅真修改面须 --force
        return {'target': dest, 'ok': False,
                'error': '副本相对源树有本地修改,卸载会丢失;确需卸载用 --force',
                'local_modifications': mods[:10]}
    shutil.rmtree(dest)
    return {'target': dest, 'ok': True, 'removed': 'directory'}


def main():
    ap = argparse.ArgumentParser(description='global-macro-research 技能安装器')
    ap.add_argument('--target', default='project',
                    choices=['project', 'personal-cc', 'personal-codex', 'all'],
                    help='安装目标(默认 project=仅仓库 .claude/skills/;'
                         '个人级/all 影响用户家目录,须显式指定)')
    ap.add_argument('--dest', help='安装到自定义目录(测试用;代替 --target)')
    ap.add_argument('--force', action='store_true',
                    help='副本相对源树有本地修改时仍覆盖/卸载'
                         '(覆盖前旧目录备份为 {dest}.bak-时间戳)')
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

    bases = target_bases(os.path.expanduser('~'))
    results = []
    for label, dest in target_dirs(args.target, args.dest).items():
        base = bases.get(label)
        prob = path_problem(dest, base)
        if prob:
            results.append({'target': dest, 'ok': False, 'error': prob})
            continue
        rdest = resolved_dest(dest)
        if label == 'custom':
            print(f'--dest 解析后安装位置: {rdest}'
                  + ('' if rdest == dest else f'(原路径 {dest} 含符号链接)'),
                  file=sys.stderr)
        elif rdest != dest:
            print(f'目标经符号链接解析: {dest} → {rdest}', file=sys.stderr)
        results.append(uninstall_one(rdest, force=args.force) if args.uninstall
                       else install_one(rdest, force=args.force))
    ok = all(r['ok'] for r in results)
    print(json.dumps({'ok': ok, 'action': 'uninstall' if args.uninstall else 'install',
                      'source': SOURCE, 'results': results}, ensure_ascii=False, indent=2))
    if not args.uninstall:
        print('已安装。Claude Code 重启会话或 /skills 查看;Codex 在仓库内直接可用'
              '(仓库级源零安装)。', file=sys.stderr)
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
