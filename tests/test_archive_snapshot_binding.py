#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""归档快照指针显式绑定测试(C席观察②,2026-11-10 协调移交)。

背景: QB-032/033 归档时 record.snapshot_id 取了最新(v5)而研究正文自述
基于 v4——默认入口(ia_cli archive save)恒注入最新快照,指针随注入走。
本套锁:
① research_archive.load_snapshot_by_id 公开面(规范id/缺失/身份不符)
② ia_cli archive save --snapshot-id 显式绑定旧版 → record 落指定版
③ 默认(不带参)行为不变=绑定最新注入快照(语义基线)
④ 显式id不存在 → rc=2 结构化 snapshot_not_found;短形 20261110_v4 容忍

零网络;快照/档案全落沙箱临时目录,不碰真实 data/。
"""
import contextlib
import glob
import io
import json
import os
import shutil
import sys
import tempfile

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


import ia_cli                     # noqa: E402
import workbench_data as wd       # noqa: E402
import research_archive as ra     # noqa: E402
import research_provenance as rp  # noqa: E402


def make_snap(sid, rate):
    ymd = sid.replace('research_snapshot_', '').split('_v')[0]
    return {'snapshot_id': sid, 'target_date': ymd,
            'research_as_of': f'{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}T18:00:00+08:00',
            'gate_a': {'status': 'DEGRADED', 'core_missing': [],
                       'noncore_missing': [], 'noncore_missing_detail': {},
                       'noncore_degraded': []},
            'sources_status': {},
            'facts': [
                {'fact_id': f'DFEDTARU@{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}',
                 'metric_id': 'DFEDTARU',
                 'display_name': '联邦基金目标区间上限', 'value': rate,
                 'unit': 'percent', 'value_type': 'level',
                 'observation_date': f'{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}',
                 'as_of': f'{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}',
                 'source': {'collector': 'rate_expectations',
                            'file': 'synthetic.json'},
                 'quality_status': 'PASS', 'issues': [], 'derived': {}}],
            'series_store': {}}


TD = tempfile.mkdtemp(prefix='snapbind_')
SBX_ROOT = os.path.join(TD, 'proj')            # 沙箱引擎根(data/daily 在此)
ARCH = os.path.join(TD, 'arch')                # 沙箱档案目录
os.makedirs(os.path.join(SBX_ROOT, 'data', 'daily'))
os.makedirs(ARCH)

V2 = make_snap('research_snapshot_20991231_v2', 4.00)   # 研究实际使用的旧版
V3 = make_snap('research_snapshot_20991231_v3', 4.25)   # 更新的"最新"(默认注入)
with open(os.path.join(SBX_ROOT, 'data', 'daily',
                       'research_snapshot_20991231_v2.json'), 'w',
          encoding='utf-8') as f:
    json.dump(V2, f, ensure_ascii=False)

REAL = {}


def run_cli(*argv, latest=V3):
    """进程内跑 ia_cli.main: ROOT/档案目录/load_context 全指沙箱。"""
    for name in ('load_context', '_ARCHIVE_DIR', 'ROOT'):
        REAL[name] = getattr(ia_cli, name)
    ia_cli.load_context = lambda: (latest, wd.load_registry(ROOT), '')
    ia_cli._ARCHIVE_DIR = ARCH
    ia_cli.ROOT = SBX_ROOT
    out, err = io.StringIO(), io.StringIO()
    code = None
    real_argv = sys.argv
    sys.argv = ['ia_cli.py', *argv]
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                ia_cli.main()
            except SystemExit as e:
                code = e.code
    finally:
        sys.argv = real_argv
        for name, val in REAL.items():
            setattr(ia_cli, name, val)
    try:
        payload = json.loads(out.getvalue())
    except ValueError:
        payload = None
    return code, payload


def latest_record():
    recs = sorted(glob.glob(os.path.join(ARCH, '**', 'QB-*.json'),
                            recursive=True))
    with open(recs[-1], encoding='utf-8') as f:
        return json.load(f)


print("═" * 60)
print("[1] load_snapshot_by_id 公开面(唯一快照读取面委托)")
print("═" * 60)
daily = os.path.join(SBX_ROOT, 'data', 'daily')
snap, why = ra.load_snapshot_by_id('research_snapshot_20991231_v2', daily)
check("规范 id 加载成功+身份一致",
      snap is not None and snap['snapshot_id'] == 'research_snapshot_20991231_v2')
snap, why = ra.load_snapshot_by_id('research_snapshot_20991231_v1', daily)
check("_v1 非规范表示拒绝(原因如实)", snap is None and '非规范' in why, why)
snap, why = ra.load_snapshot_by_id('research_snapshot_20991231_v9', daily)
check("版本缺失拒绝(文件缺失)", snap is None and '缺失' in why, why)
with open(os.path.join(daily, 'research_snapshot_20991231_v5.json'), 'w',
          encoding='utf-8') as f:
    json.dump(make_snap('research_snapshot_20991231_v2', 9.99), f,
              ensure_ascii=False)   # 内部身份与文件名不符
snap, why = ra.load_snapshot_by_id('research_snapshot_20991231_v5', daily)
check("内部 snapshot_id 与引用不符拒绝(R1 身份纪律)",
      snap is None and '不符' in why, why)
os.remove(os.path.join(daily, 'research_snapshot_20991231_v5.json'))

print("═" * 60)
print("[2] archive save --snapshot-id: 显式绑定旧版")
print("═" * 60)
code, out = run_cli('archive', 'save', '--question',
                    '美国政策利率水平(合成)', '--snapshot-id',
                    'research_snapshot_20991231_v2')
check("rc=0 保存成功", code == 0 and out and out.get('ok') is True,
      str(out and out.get('error')))
check("data.snapshot_id 随行=显式版",
      out['data']['snapshot_id'] == 'research_snapshot_20991231_v2')
rec = latest_record()
check("record.snapshot_id=显式 v2(读者按指针可复现)",
      rec['snapshot_id'] == 'research_snapshot_20991231_v2',
      rec.get('snapshot_id'))
check("record.digest_snapshot=v2 内容指纹",
      rec['digest_snapshot'] == rp.digest_snapshot(V2),
      rec.get('digest_snapshot'))

print("═" * 60)
print("[3] 默认行为不变: 指针=最新注入快照")
print("═" * 60)
code, out = run_cli('archive', 'save', '--question', '默认口径(合成)')
check("默认 rc=0", code == 0 and out.get('ok') is True)
rec = latest_record()
check("默认 record.snapshot_id=最新注入(语义基线不改)",
      rec['snapshot_id'] == 'research_snapshot_20991231_v3',
      rec.get('snapshot_id'))

print("═" * 60)
print("[4] 拒绝面与短形容忍")
print("═" * 60)
code, out = run_cli('archive', 'save', '--question', 'x', '--snapshot-id',
                    'research_snapshot_20991231_v9')
check("不存在版本 rc=2 snapshot_not_found",
      code == 2 and out['error']['kind'] == 'snapshot_not_found',
      str(out and out.get('error')))
code, out = run_cli('archive', 'save', '--question', '短形(合成)',
                    '--snapshot-id', '20991231_v2')
check("短形 20991231_v2 容忍(自动补前缀)",
      code == 0 and out['data']['snapshot_id'] == 'research_snapshot_20991231_v2',
      str(out and out.get('error')))
code, out = run_cli('archive', 'save', '--question', 'x', '--snapshot-id',
                    '../../etc/passwd')
check("路径注入拒绝(规范分解派生文件名,无原始路径面)",
      code == 2 and out['error']['kind'] == 'snapshot_not_found')

shutil.rmtree(TD, ignore_errors=True)
print()
print("═" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("═" * 60)
sys.exit(0 if FAIL == 0 else 1)
