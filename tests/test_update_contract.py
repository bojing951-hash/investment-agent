#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P0-1 update 单 JSON 契约测试(Skill 化 v1.1, 2026-11-09)。

SKILL.md 契约: 「输出一律为单个 JSON 对象(stdout)」。历史缺陷: cmd_update
在子进程前先 print 一条 notice JSON 到 stdout → 消费方 json.loads(stdout)
必失败(Extra data);子进程非 UTF-8 输出还会触发 UnicodeDecodeError 裸崩,
结果信封与退出码一并丢失。

本套件进程内猴补 subprocess.run(零网络/零真实采集),断言:
① --yes 路径 stdout 恰一个 JSON、进度提示在 stderr;
② 退出码透传(0/1/2);
③ critical_tail 筛选 ⛃/❌/Traceback/ERROR/失败/错误(大小写兼顾,末10行);
④ subprocess.run 带 errors='replace'(非 UTF-8 防裸崩);
⑤ 无 --yes → 单 JSON + confirmation_required(既有行为不回归)。
"""
import contextlib
import io
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

PASS, FAIL = 0, 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")


class FakeProc:
    def __init__(self, rc, stdout, stderr=''):
        self.returncode = rc
        self.stdout = stdout
        self.stderr = stderr


def run_cmd_update(argv, fake_proc):
    """进程内驱动 cmd_update: 捕获 stdout/stderr,返回(rc, stdout文本, stderr文本, 调用kwargs)。"""
    import ia_cli
    parser = ia_cli.build_parser()
    args = parser.parse_args(argv)
    captured = {}

    def fake_run(cmd, **kwargs):
        captured['cmd'] = cmd
        captured['kwargs'] = kwargs
        return fake_proc

    real_run = subprocess.run
    ia_cli.subprocess.run = fake_run
    out, err = io.StringIO(), io.StringIO()
    rc = None
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                ia_cli.cmd_update(args)
            except SystemExit as e:
                rc = e.code
    finally:
        ia_cli.subprocess.run = real_run
    return rc, out.getvalue(), err.getvalue(), captured


print("=" * 60)
print("① --yes 路径: stdout 单 JSON + 进度提示在 stderr")
print("=" * 60)
proc = FakeProc(0, "步骤1 ok\n🎉 完成\n", "")
rc, out, err, cap = run_cmd_update(['update', '--yes'], proc)
objs = []
dec = json.JSONDecoder()
pos = 0
while True:
    while pos < len(out) and out[pos] in ' \t\r\n':
        pos += 1
    if pos >= len(out):
        break
    obj, pos = dec.raw_decode(out, pos)
    objs.append(obj)
check("stdout 恰一个顶层 JSON(契约)", len(objs) == 1, f"实际 {len(objs)} 个")
try:
    json.loads(out)
    whole_ok = True
except json.JSONDecodeError:
    whole_ok = False
check("json.loads 整体解析成功", whole_ok)
check("rc=0 透传", rc == 0, f"rc={rc}")
check("信封 ok=true 且含 exit_code", objs and objs[0]['ok'] is True
      and objs[0]['data']['exit_code'] == 0)
check("进度提示走 stderr(不再污染 stdout)",
      '开始运行 run_weekly.py' in err and 'run_weekly.py' not in out)

print()
print("=" * 60)
print("② 退出码透传与失败摘要")
print("=" * 60)
proc = FakeProc(1, "⚠️ 步骤失败\n", "warning line\n")
rc, out, err, _ = run_cmd_update(['update', '--yes'], proc)
d = json.loads(out)
check("rc=1 透传且 ok=false", rc == 1 and d['ok'] is False)
check("exit_code=1 入信封", d['data']['exit_code'] == 1)
check("stderr_tail 携带子进程 stderr 末行", d['data']['stderr_tail'] == ['warning line'])
proc = FakeProc(2, "", "can't open file\n")
rc, out, err, _ = run_cmd_update(['update', '--yes'], proc)
check("rc=2 透传(脚本缺失场景)", rc == 2 and json.loads(out)['data']['exit_code'] == 2)

print()
print("=" * 60)
print("③ critical_tail: 关键行不被 40 行 output_tail 滚掉")
print("=" * 60)
# 40 行普通输出中夹一条 ⛃ 根因行,其后 ≥40 行普通输出把 ⛃ 滚出 tail 窗口
lines = [f"进度行 {i}" for i in range(40)] + ["⛔ 快照已存在且不可变: x.json"] \
    + [f"后续行 {i}" for i in range(45)] + ["❌ 1 个关键步骤失败", "ERROR: boom",
                                            "error: lower case", "Traceback (most recent call last)",
                                            "失败: 中文", "错误: 中文"]
proc = FakeProc(1, "\n".join(lines), "")
rc, out, err, _ = run_cmd_update(['update', '--yes'], proc)
d = json.loads(out)
ot = d['data']['output_tail']
ct = d['data']['critical_tail']
check("output_tail 恰末 40 行", len(ot) == 40 and ot[-1] == "错误: 中文")
check("⛔ 根因行不在 output_tail(被滚掉)", not any('⛔' in l for l in ot))
check("⛔ 根因行保留在 critical_tail", any('⛔' in l for l in ct))
check("critical_tail 含全部六类关键词",
      any('❌' in l for l in ct) and any('ERROR' in l for l in ct)
      and any(l.startswith('error:') for l in ct) and any('Traceback' in l for l in ct)
      and any('失败' in l for l in ct) and any('错误' in l for l in ct))
expected_ct = ["⛔ 快照已存在且不可变: x.json", "❌ 1 个关键步骤失败", "ERROR: boom",
               "error: lower case", "Traceback (most recent call last)",
               "失败: 中文", "错误: 中文"]
check("critical_tail 保序且恰含全部 7 条关键行", ct == expected_ct, str(ct))
# 超过 10 条关键行 → 只留末 10
many = [f"ERROR {i}" for i in range(15)] + ["⛔ last"]
proc = FakeProc(1, "\n".join(many), "")
rc, out, err, _ = run_cmd_update(['update', '--yes'], proc)
ct = json.loads(out)['data']['critical_tail']
check("关键行>10 → 仅末 10 条", len(ct) == 10 and ct[-1] == "⛔ last"
      and ct[0] == "ERROR 6")

print()
print("=" * 60)
print("④ errors='replace'(非 UTF-8 子进程输出防裸崩)")
print("=" * 60)
proc = FakeProc(0, "ok\n", "")
rc, out, err, cap = run_cmd_update(['update', '--yes'], proc)
check("subprocess.run 显式 errors='replace'",
      cap['kwargs'].get('errors') == 'replace', str(cap['kwargs']))
check("子进程命令为引擎 run_weekly.py(cwd=ROOT)",
      cap['cmd'] == [sys.executable, os.path.join(ROOT, 'run_weekly.py')]
      and cap['kwargs'].get('cwd') == ROOT)

print()
print("=" * 60)
print("⑤ 无 --yes(既有确认门不回归)")
print("=" * 60)
rc, out, err, cap = run_cmd_update(['update'], None)
d = json.loads(out)
check("单 JSON + confirmation_required + rc=1",
      rc == 1 and d['error']['kind'] == 'confirmation_required')
check("未触发子进程", 'cmd' not in cap)

print()
print("═" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("═" * 60)
sys.exit(0 if FAIL == 0 else 1)
