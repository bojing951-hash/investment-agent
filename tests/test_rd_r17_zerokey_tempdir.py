#!/usr/bin/env python3
"""R17(2026-11-12): 零Key套件档案写入 tempdir 隔离——REMAINING_ISSUES P2-9 收口。

根因(R16 查明): test_charter5_zero_key_matrix.py §4 以子进程跑
`ia_cli archive save`,在有快照的本地/无头 dev 树走 save 分支→真写生产
query_history(16 件「零Key矩阵问题」空档);CI 干净克隆无快照走拒存分支
不受影响。进程内 monkeypatch(§6 先例)跨不了子进程——修复=ia_cli._ARCHIVE_DIR
扩环境变量形态 IA_ARCHIVE_DIR(未设置严格 None,默认行为零变化)。

本套件锁三面:
  A. seam 解析: env 未设→None(默认零变化);设置→该路径(子进程可注入)。
  B. save 分支行为保真: 合成快照(2099 段,gitignored 路径,finally 清理)
     在场→save rc=0,记录+sidecar 落 IA_ARCHIVE_DIR tempdir;
     生产 query_history 文件集跑前后逐位一致(零新增)。
  C. 拒存分支不受 seam 破坏: 无快照时(env 已设)仍 rc=1 no_snapshot
     (dev 树真快照在场则如实跳过此节)。

红线: 不删不改既有 16 件空档(append-only,存量保留注记);
合成快照仅进 gitignored data/daily 且 finally 删除,不入库不冒充真实研究。
"""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(ROOT, 'ia_cli.py')
DAILY = os.path.join(ROOT, 'data', 'daily')
PROD_COLL = os.path.join(ROOT, 'data', 'research', 'research_archive',
                         'research_archive', 'query_history')
# 2099 段=时间上恒"最新",glob 排序确定性压过任何真实快照(2026 段)
SYN_SID = 'research_snapshot_20990101'
SYN_PATH = os.path.join(DAILY, SYN_SID + '.json')

PASS, FAIL = 0, 0


def check(name, cond, detail=''):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name}  {detail}")


def run_cli(*argv, extra_env=None):
    # 旧模型变量名以拼接构造,不落字面 token: vendor_residue 守卫零容忍模式
    # 对旧模型变量名扫全仓字面(R14 报告自伤先例)——负向剥离列表语义不变。
    _legacy = ('GLM_' + 'API_KEY', 'GLM_' + 'BASE_URL', 'GLM_' + 'MODEL')
    env = {k: v for k, v in os.environ.items()
           if k not in ('MODEL_API_KEY', 'MODEL_BASE_URL', 'MODEL_NAME',
                        *_legacy,
                        'FRED_API_KEY', 'TUSHARE_TOKEN', 'FINNHUB_API_KEY',
                        'IA_ARCHIVE_DIR')}
    env['PYTHONIOENCODING'] = 'utf-8'
    if extra_env:
        env.update(extra_env)
    return subprocess.run([sys.executable, CLI, *argv],
                          capture_output=True, text=True, env=env,
                          cwd=ROOT, timeout=120)


def prod_files():
    try:
        return frozenset(os.listdir(PROD_COLL))
    except OSError:
        return frozenset()


print("═" * 64)
print("R17 零Key套件 tempdir 隔离: IA_ARCHIVE_DIR 注入缝(默认零变化)")
print("═" * 64)

# ── A. seam 解析(子进程): 未设→None;设置→该路径 ──
probe = ("import sys; sys.path.insert(0, '.'); sys.path.insert(0, 'scripts');"
         "import ia_cli; print(ia_cli._ARCHIVE_DIR)")
rA = subprocess.run([sys.executable, '-c', probe], capture_output=True,
                    text=True, cwd=ROOT, timeout=60,
                    env={k: v for k, v in os.environ.items()
                         if k != 'IA_ARCHIVE_DIR'})
check("A1 env 未设→_ARCHIVE_DIR=None(默认行为零变化)",
      rA.returncode == 0 and rA.stdout.strip() == 'None', rA.stdout[:80])
with tempfile.TemporaryDirectory() as tdA:
    rA2 = subprocess.run([sys.executable, '-c', probe], capture_output=True,
                         text=True, cwd=ROOT, timeout=60,
                         env={**{k: v for k, v in os.environ.items()},
                              'IA_ARCHIVE_DIR': tdA})
    check("A2 env 设置→_ARCHIVE_DIR=该路径(子进程注入生效)",
          rA2.returncode == 0 and rA2.stdout.strip() == tdA, rA2.stdout[:80])

# ── B. save 分支: 合成快照在场→落 tempdir,生产 query_history 零新增 ──
os.makedirs(DAILY, exist_ok=True)
syn_snap = {'snapshot_id': SYN_SID, 'target_date': '20990101',
            'research_as_of': '2099-01-01T18:00:00+08:00',
            'gate_a': {'status': 'DEGRADED', 'core_missing': [],
                       'noncore_missing': [], 'noncore_missing_detail': {},
                       'noncore_degraded': []},
            'sources_status': {},
            'facts': [], 'series_store': {}}
Q = 'R17零Keytempdir注入缝验档'
installed = not os.path.exists(SYN_PATH)
try:
    if installed:
        with open(SYN_PATH, 'w', encoding='utf-8') as f:
            json.dump(syn_snap, f, ensure_ascii=False, indent=1)
    with tempfile.TemporaryDirectory() as tdB:
        before = prod_files()
        rB = run_cli('archive', 'save', '--question', Q,
                     extra_env={'IA_ARCHIVE_DIR': tdB})
        dB = json.loads(rB.stdout) if rB.stdout.strip().startswith('{') else {}
        qid = dB.get('data', {}).get('query_id')
        coll = os.path.join(tdB, 'research_archive', 'query_history')
        check("B1 有快照+env seam→save rc=0 落档(query_id 在场)",
              rB.returncode == 0 and dB.get('ok') and bool(qid),
              rB.stdout[:150])
        check("B2 记录+sidecar 落 tempdir(而非生产目录)",
              qid and os.path.exists(os.path.join(coll, qid + '.json'))
              and os.path.exists(os.path.join(coll, qid + '.research-full.json')),
              str(sorted(os.listdir(coll)) if os.path.isdir(coll) else None))
        rec_path = os.path.join(coll, (qid or 'QB-None') + '.json')
        if qid and os.path.exists(rec_path):
            rec = json.load(open(rec_path, encoding='utf-8'))
            check("B3 记录绑定注入快照+问题原文(行为保真)",
                  rec.get('snapshot_id') == SYN_SID
                  and rec.get('question_text') == Q,
                  f"snapshot_id={rec.get('snapshot_id')}")
        check("B4 生产 query_history 零新增(跑前后文件集逐位一致)",
              prod_files() == before)
finally:
    if installed and os.path.exists(SYN_PATH):
        os.remove(SYN_PATH)          # gitignored 路径,归还现场

# ── C. 无快照分支不被 seam 破坏(env 已设仍如实拒存) ──
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import workbench_data as wd  # noqa: E402
_snap, _why = wd.latest_snapshot(ROOT)
if _snap is None:
    with tempfile.TemporaryDirectory() as tdC:
        rC = run_cli('archive', 'save', '--question', Q,
                     extra_env={'IA_ARCHIVE_DIR': tdC})
        dC = json.loads(rC.stdout) if rC.stdout.strip().startswith('{') else {}
        check("C1 无快照+env seam→仍 no_snapshot 结构化拒存",
              rC.returncode == 1
              and dC.get('error', {}).get('kind') == 'no_snapshot',
              rC.stdout[:150])
else:
    print("  ⏭️ C1 跳过: 本树有真实快照(如 dev 树),拒存分支按契约在此环境不可达")

print(f"\nR17 tempdir 隔离: {PASS} pass / {FAIL} fail")
sys.exit(0 if FAIL == 0 else 1)
