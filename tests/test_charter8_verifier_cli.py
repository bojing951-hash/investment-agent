#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Charter8 verifier CLI 快照显式绑定测试(DEFERRED②, 2026-11-10 终验移交)。

锁面:
① _resolve_snapshot: 显式 id→research_archive.load_snapshot_by_id(短形
   容忍/缺失/身份不符);缺省→wd.latest_snapshot(默认行为不变,委托可证)
② main() 显式 --snapshot-id: 沙箱 daily 指定版→envelope.snapshot_id=该版,
   证据数值随该版快照(端到端)
③ 拒绝面(子进程,零数据依赖): 不存在 rc=2 snapshot_not_found /
   缺 view_id rc=2 / 坏 directions rc=2 / 未知参数 rc=2(收紧: 旧版静默忽略)
④ 默认路径: 不带 --snapshot-id→latest_snapshot 被调(注入哨兵可证)

fixture: 合成快照(真实注册表+真实映射,合成 facts/series)+合成 view
(tmp 注入 vs.VIEWS_DIR),零网络零真实 data/ 依赖。
"""
import contextlib
import io
import json
import os
import subprocess
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


import workbench_data as wd   # noqa: E402
import view_store as vs       # noqa: E402
import view_verifier as vv    # noqa: E402


def day(i):
    import datetime
    return (datetime.date(2099, 11, 30) + datetime.timedelta(days=i)).isoformat()


# 序列跨两年(2098-11-29→2100-11-29): 1y 窗起点 2098-12-31 之前有基准观测,
# 线性斜率 10/365/天 → 任意 365 天窗 ≈ +10%
DATES = [day(i) for i in range(-366, 365)]
LEVELS = [100.0 + 10.0 * (i + 366) / 365 for i in range(-366, 365)]


def make_snap(sid, spx_level):
    ymd = sid.replace('research_snapshot_', '').split('_v')[0]
    return {'snapshot_id': sid, 'target_date': ymd,
            'research_as_of': f'{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}T20:00:00+08:00',
            'gate_a': {'status': 'PASS', 'core_missing': [],
                       'noncore_missing': [], 'noncore_missing_detail': {},
                       'noncore_degraded': []},
            'facts': [
                {'metric_id': 'SPX', 'display_name': '标普500',
                 'value': spx_level, 'unit': 'index_point',
                 'observation_date': f'{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}',
                 'quality_status': 'PASS'}],
            'series_store': {'SPX': {'dates': DATES, 'values': LEVELS}}}


V2 = make_snap('research_snapshot_20991231_v2', 110.0)
V3 = make_snap('research_snapshot_20991231_v3', 120.0)   # 值不同,可辨版本

TD = tempfile.mkdtemp(prefix='c8vsnap_')
DAILY = os.path.join(TD, 'data', 'daily')   # _resolve_snapshot 契约: root/data/daily
os.makedirs(DAILY)
with open(os.path.join(DAILY, 'research_snapshot_20991231_v2.json'), 'w',
          encoding='utf-8') as f:
    json.dump(V2, f, ensure_ascii=False)

SYN_VIEW = {
    'schema_version': '1.1', 'view_id': 'VIEW-20991231-001',
    'institution': {'name': 'Synthetic Bank', 'type': 'investment_bank',
                    'department': 'Research'},
    'authors': [], 'report_title': 'Syn', 'source_url': 'https://example.com/x',
    'source_type': 'official_site', 'publish_date': '2099-12-01',
    'fetch_date': '2099-12-31', 'access_level': 'public_full',
    'view_horizon': '6m', 'subjects': ['equities'],
    'core_views': [{'statement': '看多。', 'attribution': 'institution_stated',
                    'basis': 'verbatim_quote', 'quote': 'Bullish.'}],
    'forecasts': [], 'key_assumptions': [], 'evidence_cited': [],
    'mechanism_steps': [], 'risk_factors': [], 'falsification_conditions': [],
    'revisions': [], 'completeness_notes': '合成', 'copyright_note': 'meta+link',
}
VIEWS_TD = os.path.join(TD, 'views')
os.makedirs(VIEWS_TD)
with open(os.path.join(VIEWS_TD, 'VIEW-20991231-001.json'), 'w',
          encoding='utf-8') as f:
    json.dump(SYN_VIEW, f, ensure_ascii=False)

print("═" * 60)
print("[1] _resolve_snapshot 纯函数面")
print("═" * 60)
snap, why = vv._resolve_snapshot('research_snapshot_20991231_v2', root=TD)
check("显式规范 id 加载成功", snap is not None
      and snap['snapshot_id'] == 'research_snapshot_20991231_v2')
snap, why = vv._resolve_snapshot('20991231_v2', root=TD)
check("短形容忍(自动补前缀)", snap is not None
      and snap['snapshot_id'] == 'research_snapshot_20991231_v2')
snap, why = vv._resolve_snapshot('research_snapshot_20991231_v9', root=TD)
check("版本缺失→(None, 快照文件缺失)", snap is None and '缺失' in why, why)
snap, why = vv._resolve_snapshot('research_snapshot_20991231_v1', root=TD)
check("非规范表示(_v1)→(None, 非规范)", snap is None and '非规范' in why, why)
sentinel = make_snap('research_snapshot_SENTINEL', 1.0)
real_latest = wd.latest_snapshot
wd.latest_snapshot = lambda root=None: (sentinel, '哨兵')
try:
    snap, why = vv._resolve_snapshot(None, root=TD)
    check("缺省→委托 wd.latest_snapshot(默认行为不变)",
          snap is sentinel)
finally:
    wd.latest_snapshot = real_latest

print("═" * 60)
print("[2] main() 显式绑定: envelope 与数值随指定版")
print("═" * 60)
real_vdir = vs.VIEWS_DIR
vs.VIEWS_DIR = VIEWS_TD
try:
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = vv.main(['VIEW-20991231-001', '--snapshot-id', '20991231_v2'],
                     data_root=TD)
    env = json.loads(out.getvalue())
    check("rc=0 且 envelope.snapshot_id=显式 v2", rc == 0
          and env['snapshot_id'] == 'research_snapshot_20991231_v2',
          str(env.get('snapshot_id')))
    spx = [e for e in env['evidence'] if e['metric_id'] == 'SPX']
    check("SPX 证据在场(真实注册表+真实映射链)", len(spx) == 1)
    check("level 随 v2 快照(110.0)", spx and spx[0]['level'] == 110.0,
          str(spx and spx[0].get('level')))
    check("1y 区间随该版序列(≈+10%,366 天窗含一天基准偏移)",
          spx and abs(spx[0]['changes']['1y']['pct_change'] - 10.0) < 0.1,
          str(spx and spx[0]['changes'].get('1y')))
    with open(os.path.join(DAILY, 'research_snapshot_20991231_v3.json'), 'w',
              encoding='utf-8') as f:
        json.dump(V3, f, ensure_ascii=False)
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = vv.main(['VIEW-20991231-001',
                      '--snapshot-id', 'research_snapshot_20991231_v3'],
                     data_root=TD)
    env = json.loads(out.getvalue())
    spx = [e for e in env['evidence'] if e['metric_id'] == 'SPX']
    check("换绑 v3→level=120.0(版本可辨,非缓存的 v2)",
          rc == 0 and spx and spx[0]['level'] == 120.0,
          str(spx and spx[0].get('level')))
finally:
    vs.VIEWS_DIR = real_vdir

print("═" * 60)
print("[3] 子进程拒绝面(零数据依赖)")
print("═" * 60)


def run_cli(*args):
    p = subprocess.run(
        [sys.executable, os.path.join(ROOT, 'scripts', 'view_verifier.py'), *args],
        capture_output=True, text=True, timeout=60, cwd=ROOT)
    try:
        payload = json.loads(p.stdout)
    except ValueError:
        payload = None
    return p.returncode, payload, p.stdout


rc, out, raw = run_cli('VIEW-20991231-001', '--snapshot-id', '20991231_v9')
check("不存在版本 rc=2 snapshot_not_found(单 JSON)",
      rc == 2 and out['error']['kind'] == 'snapshot_not_found'
      and raw.strip().startswith('{'), f"rc={rc} {raw[:120]}")
rc, out, _ = run_cli('--snapshot-id', '20991231_v2')
check("缺 view_id rc=2 missing_view_id", rc == 2
      and out['error']['kind'] == 'missing_view_id')
rc, out, _ = run_cli('VIEW-20991231-001', '--directions', 'not-json')
check("坏 directions rc=2 bad_directions", rc == 2
      and out['error']['kind'] == 'bad_directions')
rc, out, _ = run_cli('VIEW-20991231-001', '--bogus-flag')
check("未知参数 rc=2 usage(fail-loud,不再静默忽略)", rc == 2
      and out['error']['kind'] == 'usage')
rc, out, _ = run_cli('VIEW-20991231-001', '--snapshot-id', '   ')
check("空白 snapshot-id rc=2 bad_snapshot_id", rc == 2
      and out['error']['kind'] == 'bad_snapshot_id')

print("═" * 60)
print("[4] 默认路径经 latest(与既有契约一致)")
print("═" * 60)
wd_latest_calls = []
real_latest = wd.latest_snapshot


def spy_latest(root=None):
    wd_latest_calls.append(root)
    return real_latest(root)


wd.latest_snapshot = spy_latest
try:
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        vv.main(['VIEW-NOSUCH-999', '--snapshot-id', '20991231_v2'],
                data_root=TD)
finally:
    wd.latest_snapshot = real_latest
env = json.loads(out.getvalue())
check("显式指定时不再走 latest(0 次调用)", len(wd_latest_calls) == 0)
check("view 缺席仍如实 rc=1 view_not_found(链路完整)",
      env['ok'] is False
      and env['error']['kind'] == 'view_not_found_or_quarantined')

import shutil
shutil.rmtree(TD, ignore_errors=True)
print()
print("═" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("═" * 60)
sys.exit(0 if FAIL == 0 else 1)
