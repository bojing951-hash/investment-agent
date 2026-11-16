#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""目标完整性守卫(Product Convergence §4.1 / G0)。

保护对象: 产品目标与验收契约文件——未被登记的变更使 CI 变红。
诚实边界(章程原文明认): 仓库内哈希登记≠真正权限保护(开发Agent可改注册表本身);
真强制力=main 分支保护/Ruleset(外部权限,见 TARGET_PROTECTION_PREP.md 待用户项)。
本守卫的价值: ①任何未同步注册表的目标/验收变更→测试红(CI/本地双口径可见)
②--update 须显式理由,git 历史留痕,配合章程「目标变更必须用户批准」形成审计链。

用法:
  python3 scripts/target_integrity_guard.py --check          # 校验(测试/CI 用,失配 exit 1)
  python3 scripts/target_integrity_guard.py --update --reason "用户批准: <说明>"  # 显式重登记
  python3 scripts/target_integrity_guard.py --show           # 打印登记表
"""
import argparse
import hashlib
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
REGISTRY = os.path.join(ROOT, 'docs', 'autonomous-rd', 'TARGET_INTEGRITY_REGISTRY.json')

# 保护清单: 产品目标+验收契约+本章程 G 门(章程§4.1: 不得擅自改目标/删验收/降阈值)
GUARDED = [
    'docs/autonomous-rd/PRODUCT_GOAL.md',
    'docs/autonomous-rd/FINAL_ACCEPTANCE.md',
    'docs/autonomous-rd/ACCEPTANCE_CRITERIA.md',
    'docs/autonomous-rd/CHARTER_PRODUCT_CONVERGENCE.md',
]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def load_registry():
    if not os.path.exists(REGISTRY):
        return {}
    return json.load(open(REGISTRY, encoding='utf-8'))


def cmd_check(quiet=False):
    reg = load_registry()
    bad_missing, bad_changed, ok = [], [], 0
    for rel in GUARDED:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            bad_missing.append(rel)
            continue
        entry = reg.get(rel)
        if entry is None:
            bad_missing.append(f'{rel} (未登记)')
            continue
        cur = sha256_file(path)
        if cur != entry['sha256']:
            bad_changed.append(f'{rel}: 登记={entry["sha256"][:12]} 当前={cur[:12]} (登记于 {entry["registered_at"]})')
        else:
            ok += 1
    extra = [k for k in reg if k not in GUARDED]
    if not quiet:
        print(f'目标完整性: {ok}/{len(GUARDED)} 一致')
        for m in bad_missing:
            print(f'  ❌ 缺失/未登记: {m}')
        for c in bad_changed:
            print(f'  ❌ 已变更(未经登记): {c}')
        if extra:
            print(f'  ⚠ 注册表含非保护项(清理): {extra}')
        if not bad_missing and not bad_changed:
            print('  ✅ 产品目标与验收契约未被未授权变更')
    return 0 if (not bad_missing and not bad_changed) else 1


def cmd_update(reason):
    if not reason.strip():
        print('refuse: --reason 必填(章程: 目标变更须用户批准,理由入 git 历史)')
        return 1
    reg = load_registry()
    from datetime import datetime, timezone, timedelta
    now = datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
    for rel in GUARDED:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            print(f'skip(不存在): {rel}')
            continue
        reg[rel] = {'sha256': sha256_file(path), 'registered_at': now, 'reason': reason}
    reg.setdefault('_meta', {})['last_update'] = now
    json.dump(reg, open(REGISTRY, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'重登记 {len(GUARDED)} 项 @ {now};理由: {reason}')
    print('提醒: 诚实边界——本登记仍在仓库内,真强制力须 main 保护(见 TARGET_PROTECTION_PREP.md)')
    return 0


def cmd_show():
    reg = load_registry()
    if not reg:
        print('(注册表不存在——首次请 --update 登记)')
        return 0
    for rel in GUARDED:
        e = reg.get(rel)
        print(f'  {rel}: {e["sha256"][:16]}… @{e["registered_at"]} | {e.get("reason", "")}' if e
              else f'  {rel}: ❌ 未登记')
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description='产品目标与验收契约完整性守卫')
    ap.add_argument('--check', action='store_true', help='校验(失配 exit 1)')
    ap.add_argument('--update', action='store_true', help='显式重登记(须 --reason)')
    ap.add_argument('--show', action='store_true', help='打印登记表')
    ap.add_argument('--reason', default='', help='重登记理由(入 git 历史)')
    ap.add_argument('--quiet', action='store_true')
    args = ap.parse_args(argv)
    if args.update:
        return cmd_update(args.reason)
    if args.show:
        return cmd_show()
    return cmd_check(quiet=args.quiet)


if __name__ == '__main__':
    sys.exit(main())
