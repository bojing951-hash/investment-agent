#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit-R1 F03 回归: 验收 runner 命令注入面(argv 隔离)。

外审复现: 旧版把 question 经 json.dumps 拼进 shell=True——JSON 编码不是
shell 转义,命令替换会执行。本套件用**无害负例**(只试触 marker 文件的
命令替换/反引号/引号/换行/空格路径)证明:
  A. 毒问题到达真实进程边界仍是单个 argv 元素(构造面);
  B. 真跑一轮(净克隆→拒答式研究步)毒载荷按字面落日志/VERDICT,
     marker 文件不出现(执行面);
  C. 毒 baseline 被拒于解析步,marker 不出现。
禁止用读凭据/访问外网证明漏洞——只做无害 marker。
"""
import json
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import product_acceptance_runner as par  # noqa: E402

PASS, FAIL = 0, 0


def check(name, cond, detail=''):
    global PASS, FAIL
    print(f"  {'✅' if cond else '❌'} {name}" + (f" — {detail}" if detail and not cond else ''))
    PASS, FAIL = PASS + (1 if cond else 0), FAIL + (0 if cond else 0)


POISON = '$(touch {m}) `touch {m}` "; touch {m} ;\' \n|touch {m}'

print('═' * 64)
print('F03 注入回归: argv 隔离(无害负例,不触网不读凭据)')
print('═' * 64)

# ── A. 构造面: 毒问题作为单 argv 元素到达 sh() 边界 ──
tmp = tempfile.mkdtemp(prefix='f03a_')
marker = os.path.join(tmp, 'pwn_marker')
payload = POISON.format(m=marker)
captured = []
orig_sh = par.sh


def fake_sh(argv, cwd, log_fh, timeout=1800):
    captured.append(list(argv))
    log_fh.write('\n$ (recorded)\n')
    return 0, 0.1


par.sh = fake_sh
orig_resolve = par.resolve_baseline
par.resolve_baseline = lambda b: '0123456789abcdef0123456789abcdef01234567'
import argparse as _ap  # noqa: E402
args = _ap.Namespace(question=payload, baseline='main',
                     workdir=os.path.join(tmp, 'run'), keep=False,
                     caliber='product')
rc = par.caliber_product(args)
par.sh = orig_sh
par.resolve_baseline = orig_resolve
research_argv = None
for a in captured:
    if '--question' in a:
        research_argv = a[a.index('--question') + 1]
check('A1 research-run 问题=单 argv 元素逐字节等值',
      research_argv == payload, repr(research_argv)[:80])
check('A2 全部步骤均为 argv 列表(无 shell 字符串命令)',
      all(isinstance(a, list) for a in captured))
check('A3 clone/checkout 分列两步', [a[0] for a in captured][:2] == ['git', 'git'])
check('A4 marker 未出现(构造面)', not os.path.exists(marker))
check('A5 checkout 用解析后确切 sha',
      any('0123456789abcdef0123456789abcdef01234567' in a for a in captured))

# ── B. 执行面: 真跑一轮,毒载荷字面落档,marker 不出现 ──
tmpb = tempfile.mkdtemp(prefix='f03b_')
marker_b = os.path.join(tmpb, 'pwn_marker')
payload_b = POISON.format(m=marker_b)
r = subprocess.run(
    [sys.executable, os.path.join(ROOT, 'scripts', 'product_acceptance_runner.py'),
     '--caliber', 'product', '--question', payload_b,
     '--baseline', 'dev/audit-fix-r1' if os.system(
         'git -C %s rev-parse dev/audit-fix-r1 >/dev/null 2>&1' % ROOT) == 0
     else 'main', '--workdir', os.path.join(tmpb, 'run')],
    shell=False, capture_output=True, text=True, timeout=900)
log = open(os.path.join(tmpb, 'run', 'ACCEPTANCE_PACKET', 'run_log.txt'),
           encoding='utf-8').read()
v = json.load(open(os.path.join(tmpb, 'run', 'ACCEPTANCE_PACKET', 'VERDICT.json'),
                   encoding='utf-8'))
check('B1 真跑: marker 文件未出现(命令替换未执行)',
      not os.path.exists(marker_b))
check('B2 毒载荷按字面出现在 run_log(未被 shell 改写)',
      '$(touch' in log and '`touch' in log)
check('B3 VERDICT.question 逐字节等值', v['question'] == payload_b)
check('B4 baseline_resolved=40位确切 commit',
      isinstance(v.get('baseline_resolved'), str) and len(v['baseline_resolved']) == 40)
check('B5 拒答式毒问题不产生额外可执行副作用面(仅日志+VERDICT 落档)',
      sorted(os.listdir(os.path.join(tmpb, 'run', 'ACCEPTANCE_PACKET')))
      == ['VERDICT.json', 'artifacts', 'run_log.txt'])

# ── C. baseline 注入负例 ──
tmpc = tempfile.mkdtemp(prefix='f03c_')
marker_c = os.path.join(tmpc, 'pwn_marker')
bad_baseline = 'main; touch %s' % marker_c
r2 = subprocess.run(
    [sys.executable, os.path.join(ROOT, 'scripts', 'product_acceptance_runner.py'),
     '--caliber', 'product', '--question', 'x', '--baseline', bad_baseline,
     '--workdir', os.path.join(tmpc, 'run')],
    shell=False, capture_output=True, text=True, timeout=120)
check('C1 毒 baseline 被拒于解析步(rc=1)',
      r2.returncode == 1 and not os.path.exists(marker_c))
check('C2 拒绝理由入 VERDICT',
      json.load(open(os.path.join(tmpc, 'run', 'ACCEPTANCE_PACKET', 'VERDICT.json'),
                     encoding='utf-8')).get('refused_reason') == 'baseline_unresolvable')

print(f"\nF03 判定: {PASS} PASS / {FAIL} FAIL")
sys.exit(0 if FAIL == 0 else 1)
