#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""产品验收隔离 runner(Product Convergence Phase 1 / 章程§四.3)。

四层验收口径的唯一入口区分(不新增管理系统,只做隔离与留痕):
  L1 Development Tests   = tests/ 直跑(exit 口径,CI 同口径)——既有,不经本件
  L2 Regression          = tests/ 中带 RDG/Rxx 回归锚的套件——既有,不经本件
  L3 Product Acceptance  = 净克隆可信基线上跑真实产品动作(本件 --caliber product)
  L4 Independent Eval    = 独立席(章程§九;本件只产材料包,不冒充独立)

用法:
  python3 scripts/product_acceptance_runner.py --caliber product \
      --question "美债10年期利率上行对高收益债利差的传导" \
      --baseline <git-sha|main> [--workdir /tmp/xxx] [--keep]

产出: <workdir>/ACCEPTANCE_PACKET/{run_log.txt, artifacts/, VERDICT.json}
VERDICT.json 字段=机器可核(machine-checkable),诚实面:
  steps[]: 每步 {name, cmd, rc, duration}; any_step_failed 如实记;
  不在 L3 里给「研究质量」结论——那是 G1-G4 门与独立席的职责。
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


def hkt_now():
    return datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S HKT')


def sh(cmd, cwd, log_fh, timeout=1800):
    """跑一步,流式留痕,返回 (rc, duration)。失败不抛——如实入 VERDICT。"""
    t0 = time.time()
    log_fh.write(f'\n$ {cmd}\n')
    log_fh.flush()
    try:
        r = subprocess.run(cmd, shell=True, cwd=cwd, stdout=log_fh, stderr=subprocess.STDOUT,
                           timeout=timeout)
        rc = r.returncode
    except subprocess.TimeoutExpired:
        rc = 124
        log_fh.write(f'[TIMEOUT after {timeout}s]\n')
    d = round(time.time() - t0, 1)
    log_fh.write(f'[rc={rc} {d}s]\n')
    log_fh.flush()
    return rc, d


def caliber_product(args):
    tag = datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%dT%H%M')
    workdir = os.path.abspath(args.workdir or f'/tmp/pa_{tag}')
    if os.path.exists(workdir) and not args.keep:
        print(f'refuse: {workdir} 已存在(--keep 复用或换 --workdir)')
        return 2
    clone_dir = os.path.join(workdir, 'clone')
    packet = os.path.join(workdir, 'ACCEPTANCE_PACKET')
    arts = os.path.join(packet, 'artifacts')
    os.makedirs(arts, exist_ok=True)

    steps = []

    def step(name, cmd, cwd, timeout=1800):
        rc, d = sh(cmd, cwd, LOG, timeout)
        steps.append({'name': name, 'cmd': cmd, 'rc': rc, 'duration_s': d})
        return rc

    with open(os.path.join(packet, 'run_log.txt'), 'w', encoding='utf-8') as LOG:
        LOG.write(f'产品验收 L3 净克隆跑 {hkt_now()}\n基线={args.baseline} 问题={args.question}\n')
        rc = step('clone', f'git clone -q {REPO_ROOT} {clone_dir} && git -C {clone_dir} checkout -q {args.baseline}', workdir, timeout=300)
        if rc == 0:
            rc = step('gate-consistency',
                      'python3 scripts/rd_state_consistency.py --quiet', clone_dir)
            step('gate-checkpoint', 'python3 scripts/rd_checkpoint.py --verify --quiet', clone_dir)
        if rc == 0:
            step('research-run',
                 f'python3 ia_cli.py research-run --question {json.dumps(args.question, ensure_ascii=False)} '
                 f'--out-dir {os.path.join(arts, "research_run")}',
                 clone_dir, timeout=3600)
        # L3 只到确定性研究面+证据包;attach(模型判断)与质量结论=独立席/L4 材料,不在此冒认
        verdict = {
            'caliber': 'L3-product',
            'baseline': args.baseline,
            'question': args.question,
            'started_at': hkt_now(),
            'steps': steps,
            'any_step_failed': any(s['rc'] != 0 for s in steps),
            'honest_boundary': 'L3 只验证净环境可跑+确定性研究面产出;研究质量/真 L3L4 Agent 判断=G 门+独立席职责,不在本 VERDICT 冒认',
        }
        with open(os.path.join(packet, 'VERDICT.json'), 'w', encoding='utf-8') as f:
            json.dump(verdict, f, ensure_ascii=False, indent=2)
    print(f"packet={packet} any_step_failed={verdict['any_step_failed']}")
    return 1 if verdict['any_step_failed'] else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description='产品验收隔离 runner(四层口径隔离)')
    ap.add_argument('--caliber', choices=['product'], default='product')
    ap.add_argument('--question', required=True, help='研究问题(L3 真实产品动作)')
    ap.add_argument('--baseline', default='main', help='可信基线(sha 或分支名)')
    ap.add_argument('--workdir', default=None)
    ap.add_argument('--keep', action='store_true', help='复用已存在 workdir')
    args = ap.parse_args(argv)
    if args.caliber == 'product':
        return caliber_product(args)
    return 0


if __name__ == '__main__':
    sys.exit(main())
