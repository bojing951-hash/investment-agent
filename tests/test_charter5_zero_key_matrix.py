#!/usr/bin/env python3
"""Charter 5 S7 新增套件①: 零Key矩阵(红线=零Key环境全能力必须正常)。

用完全剥离模型/数据源 Key 的子进程逐能力跑 ia_cli 八能力面,断言:
- 全部能力 rc=0 或结构化拒绝(rc=1/2 且 stdout 为合法 JSON 信封),
  绝无 Traceback / 裸异常;
- doctor 零旧变量行(唯一模型面=MODEL_* 三参)且不出现任何旧厂商词;
- 旧变量名残留(GLM_API_KEY 等)即使误设也不被读取(env_config 唯一凭证面)。

零Key≠零能力: 采集/研究问答/工作台/确定性周报走本地快照与确定性分支
(Agent Native 模式预期行为)。预期值全部独立硬编码,不用被测模块自算。
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(ROOT, 'ia_cli.py')

STRIP_KEYS = ('MODEL_API_KEY', 'MODEL_BASE_URL', 'MODEL_NAME',
              'GLM_API_KEY', 'GLM_BASE_URL', 'GLM_MODEL',
              'FRED_API_KEY', 'TUSHARE_TOKEN', 'FINNHUB_API_KEY',
              'RUN_MODEL_LIVE', 'RUN_GLM_LIVE')

PASS, FAIL = 0, 0


def check(name, cond, detail=''):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name}  {detail}")


def run_zero_key(*argv, extra_env=None):
    """零Key子进程: 剥离全部模型/数据源 Key 后跑 ia_cli。"""
    env = {k: v for k, v in os.environ.items() if k not in STRIP_KEYS}
    env['PYTHONIOENCODING'] = 'utf-8'
    if extra_env:
        env.update(extra_env)
    return subprocess.run([sys.executable, CLI, *argv],
                          capture_output=True, text=True, env=env,
                          cwd=ROOT, timeout=120)


print("═" * 64)
print("Charter5 S7-① 零Key矩阵: 八能力面全部正常(无 Key 不炸栈不缺能力)")
print("═" * 64)

# ── 1. doctor: 零Key可跑,唯一模型面=MODEL_*,无任何旧厂商词 ──
r = run_zero_key('doctor')
d = json.loads(r.stdout)
check("doctor rc=0 零Key可跑", r.returncode == 0 and d['ok'])
check("doctor env 恰为中性三参+数据源四键(旧变量行删除)",
      set(d['data']['env']) == {'MODEL_API_KEY', 'MODEL_BASE_URL', 'MODEL_NAME',
                                'FRED_API_KEY', 'TUSHARE_TOKEN',
                                'FINNHUB_API_KEY', 'YF_PROXY'},
      str(set(d['data']['env'])))
blob = json.dumps(d, ensure_ascii=False)
check("doctor 全输出无旧厂商词(glm/zhipu/bigmodel 大小写任意)",
      not any(t in blob.lower() for t in ('glm', 'zhipu', 'bigmodel')))
check("doctor 零Key提示=model_key_note(中性配置指引)",
      isinstance(d['data'].get('model_key_note'), str)
      and 'MODEL_API_KEY' in d['data']['model_key_note'])

# ── 2. 只读能力: overview/changes/history/compare 零Key全可用 ──
for cap, argv in (('overview', ['overview', '--economy', 'US']),
                  ('changes', ['changes']),
                  ('history 未知指标→结构化错误', ['history', '--metric', 'NO_SUCH_METRIC'])):
    r = run_zero_key(*argv)
    ok_json = r.stdout.strip().startswith('{')
    check(f"{cap} 零Key: 结构化输出(rc={r.returncode})",
          ok_json and 'Traceback' not in r.stderr,
          r.stderr[:120])

# compare 无模式 rc=2 是契约行为(argparse 用法错误),单独断言
r = run_zero_key('compare')
check("compare 无模式→rc=2 用法提示(零Key不影响契约)",
      r.returncode == 2 and 'Traceback' not in r.stderr
      and ('compare' in r.stderr or 'compare' in r.stdout))

# ── 3. research: 零Key零快照环境下如实拒答(no_snapshot/拒答),不炸栈 ──
r = run_zero_key('research', '--question', '美国政策利率是多少')
ok_json = r.stdout.strip().startswith('{')
check("research 零Key: 结构化输出绝不 Traceback",
      r.returncode in (0, 1) and ok_json and 'Traceback' not in r.stderr,
      r.stderr[:150])

# ── 4. archive save: 有快照→保存成功;零快照环境→no_snapshot 结构化拒存 ──
# (CI 干净克隆=无快照→rc=1 no_snapshot;本地开发仓=有快照→rc=0 落档,
#  两分支都是零Key合法行为,断言=结构化+无 Traceback+分支语义正确)
r = run_zero_key('archive', 'save', '--question', '零Key矩阵问题')
d4 = json.loads(r.stdout) if r.stdout.strip().startswith('{') else {}
if r.returncode == 1:
    check("archive save 零快照环境→no_snapshot 结构化拒存",
          d4.get('error', {}).get('kind') == 'no_snapshot', r.stdout[:150])
else:
    check("archive save 有快照→零Key正常落档(query_id 在场)",
          r.returncode == 0 and d4.get('ok')
          and bool(d4.get('data', {}).get('query_id')), r.stdout[:150])
r = run_zero_key('archive', 'list')
check("archive list 零Key可跑(空列表也合法)",
      r.returncode == 0 and json.loads(r.stdout)['ok'])

# ── 5. 误设旧变量≠配置: GLM_API_KEY 设了也不被读取(唯一凭证面=MODEL_*) ──
r = run_zero_key('doctor', extra_env={'GLM_API_KEY': 'sk-LEGACY-SHOULD-BE-IGNORED'})
d5 = json.loads(r.stdout)
check("误设旧变量不被读取: doctor 三参仍=未配置(model_key_note 在场)",
      d5['data']['env']['MODEL_API_KEY']['configured'] is False
      and 'model_key_note' in d5['data'])

# ── 6. S6 旧档 glm→model 读侧映射回归锁(D2,2026-11-09;A2 手工实证→永久测试) ──
# tempdir 注入 ia_cli._ARCHIVE_DIR(批2 WI6 注入缝),构造 glm 键旧 sidecar
# (write_research_full 前时代的合法旧档)→ archive get 断言: full.model 由旧
# glm 键填充、输出契约恒 model 键(无 glm 键)、**盘上旧档字节零改写**。
print("\n── 6. 旧档 sidecar glm→model 映射 + 盘上字节不动(D2) ──")
import contextlib
import io
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import ia_cli                                   # noqa: E402
import research_archive as ra                   # noqa: E402

QID = 'QB-20261108-001'
with tempfile.TemporaryDirectory() as td:
    coll = os.path.join(td, 'research_archive', 'query_history')
    os.makedirs(coll)
    base_rec = {'record_type': 'query_history', 'query_id': QID,
                'created_at': '2026-11-08T09:00:00+08:00', 'mode': 'CLI',
                'question_text': '旧档映射锁', 'as_of': '2026-11-08',
                'snapshot_id': 'research_snapshot_20261108',
                'digest_snapshot': '0123456789abcdef', 'ir': {}, 'ir_stage': 'map',
                'answer_summary': None, 'promoted_to_task_id': None,
                'archived_at': '2026-11-08T09:05:00+08:00'}
    base_path = os.path.join(coll, QID + '.json')
    with open(base_path, 'w', encoding='utf-8') as f:
        json.dump(base_rec, f, ensure_ascii=False, indent=1, sort_keys=True)
    # 旧档 sidecar: model 缺席而 glm 在场(FULL_LEGACY_KEYS 代位=合法旧格式)
    legacy = {'record_type': 'research_full_v1', 'query_id': QID,
              'question_text': '旧档映射锁',
              'created_at': '2026-11-08T09:00:00+08:00',
              'research_as_of': '2026-11-08T09:00:00+08:00',
              'snapshot_id': 'research_snapshot_20261108',
              'digest_snapshot': '0123456789abcdef', 'status': 'answered',
              'answer_text': '旧档正文', 'values': None,
              'glm': {'provider': 'model-x'}, 'unresolved': None,
              'warnings': [], 'violations': [], 'user_note': None,
              'follow_up_of': None, 'saved_at': '2026-11-08T09:05:00+08:00'}
    check("6a 旧档 payload 过 schema 校验(glm 代位=合法旧格式)",
          ra.validate_research_full(legacy) == [])
    side_path = os.path.join(coll, QID + '.research-full.json')
    with open(side_path, 'w', encoding='utf-8') as f:
        json.dump(legacy, f, ensure_ascii=False, indent=1, sort_keys=True)
    base_before = open(base_path, 'rb').read()
    side_before = open(side_path, 'rb').read()

    real_dir = ia_cli._ARCHIVE_DIR
    ia_cli._ARCHIVE_DIR = td
    out = io.StringIO()
    code = None
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            try:
                ia_cli.main(['archive', 'get', '--query-id', QID])
            except SystemExit as e:
                code = e.code
    finally:
        ia_cli._ARCHIVE_DIR = real_dir
    d6 = json.loads(out.getvalue())
    full6 = d6.get('data', {}).get('full') or {}
    check("6b archive get 旧档成功(full.model 由 glm 键填充)",
          code == 0 and d6.get('ok')
          and full6.get('model') == {'provider': 'model-x'}, out.getvalue()[:200])
    check("6c 输出契约恒 model 键(合并视图无 glm 键)", 'glm' not in full6)
    check("6d 盘上旧档字节零改写(base+sidecar 读后原样)",
          open(base_path, 'rb').read() == base_before
          and open(side_path, 'rb').read() == side_before)

sys.exit(0 if FAIL == 0 else 1)
