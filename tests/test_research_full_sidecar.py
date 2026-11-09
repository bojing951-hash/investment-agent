#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P1 研究档案完整保存(research_full sidecar)回归套件(批2 WI6,2026-11-09)。

覆盖:
① research --archive → **两次独立 python3 子进程**(跨进程模拟)→ archive get
   → sidecar answer_text 与首次进程用户所见逐字节一致;
② 旧档无 sidecar → get 只有 base(record 原样),list has_full=false,不报错;
③ 重复 query_id 的 sidecar → 拒绝覆写(append-only,与 base 同纪律);
④ --follow-up-of 链接: 前档不存在→rc=2;存在→sidecar 落位;
⑤ list 不把 sidecar 当独立记录(_QUERY_FILE_RE 不匹配,目录清单实证);
⑥ --note 落位(sidecar user_note + list 摘要);
⑦ AI 解释用 mock(虚构响应文本,调用计数=1),零真实调用;未请求时 model=null;
⑧ 旧 query_history 契约不动(QUERY_RECORD_KEYS 字面量/文件正则/旧档可读)。
"""
import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (ROOT, os.path.join(ROOT, 'scripts')):
    if p not in sys.path:
        sys.path.insert(0, p)

import ia_cli                    # noqa: E402
import workbench_data as wd      # noqa: E402
import research_archive as ra    # noqa: E402

PASS, FAIL = 0, 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")


# ══ 合成快照(结构对照真实快照;数值全虚构;足以让 e2eb 栈 answered) ════════
OBS = '2026-11-06'


def _fact(fid, mid, name, val, unit, collector):
    return {'fact_id': f'{fid}@{OBS}', 'metric_id': mid, 'display_name': name,
            'value': val, 'unit': unit, 'value_type': 'level',
            'observation_date': OBS, 'as_of': '2026-11-08',
            'source': {'collector': collector, 'file': 'synthetic_20261108.json'},
            'quality_status': 'PASS', 'issues': [], 'derived': {}}


def make_snap():
    # target_date 须为 YYYYMMDD 无连字符(select_snapshot 逐字比对文件名 ymd)
    return {'snapshot_id': 'research_snapshot_20261108', 'target_date': '20261108',
            'research_as_of': '2026-11-08T18:00:00+08:00',
            'gate_a': {'status': 'DEGRADED', 'core_missing': [], 'noncore_missing': [],
                       'noncore_missing_detail': {}, 'noncore_degraded': []},
            'sources_status': {},
            'facts': [
                _fact('F1', 'DFEDTARU', '联邦基金目标区间上限', 4.00, 'percent',
                      'rate_expectations'),
                _fact('F2', 'DFEDTARL', '联邦基金目标区间下限', 3.75, 'percent',
                      'rate_expectations'),
                _fact('F3', 'DFF', '有效联邦基金利率', 3.91, 'percent',
                      'rate_expectations'),
                _fact('F4', 'USDJPY', '美元兑日元', 152.35, 'jpy_per_usd',
                      'global_market_collector')],
            'series_store': {}}


Q_POLICY = '美国政策利率现在是多少?'

# ══ 仓库副本(跨进程 e2e: 模块路径派生 → 档案/快照全部落在副本内) ═════════
TD = tempfile.mkdtemp(prefix='wi6-sidecar-')
PROJ = os.path.join(TD, 'proj')
shutil.copy2(os.path.join(ROOT, 'ia_cli.py'), PROJ + '.ia_cli.py')  # 先占位防误并
os.remove(PROJ + '.ia_cli.py')
shutil.copytree(os.path.join(ROOT, 'scripts'), os.path.join(PROJ, 'scripts'))
shutil.copytree(os.path.join(ROOT, 'config'), os.path.join(PROJ, 'config'))
shutil.copy2(os.path.join(ROOT, 'ia_cli.py'), os.path.join(PROJ, 'ia_cli.py'))
os.makedirs(os.path.join(PROJ, 'data', 'daily'))
with open(os.path.join(PROJ, 'data', 'daily', 'research_snapshot_20261108.json'),
          'w', encoding='utf-8') as f:
    json.dump(make_snap(), f, ensure_ascii=False)

SBX = os.path.join(TD, 'sbx-archive')          # 进程内沙箱档案目录


def run_proj(*argv):
    """独立 python3 子进程跑副本 ia_cli(跨进程模拟)。"""
    r = subprocess.run([sys.executable, os.path.join(PROJ, 'ia_cli.py'), *argv],
                       capture_output=True, text=True, timeout=120, cwd=TD)
    return r.returncode, r.stdout, r.stderr


def run_inproc(*argv, snap=None, explain_mock=None):
    """进程内跑 ia_cli.main(load_context 指合成快照/档案指沙箱)。"""
    real_ctx, real_arch = ia_cli.load_context, ia_cli._ARCHIVE_DIR
    real_explain = wd.ai_explain
    ia_cli.load_context = lambda: (snap or make_snap(), wd.load_registry(ROOT), '')
    ia_cli._ARCHIVE_DIR = SBX
    if explain_mock is not None:
        wd.ai_explain = explain_mock
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
        ia_cli.load_context, ia_cli._ARCHIVE_DIR = real_ctx, real_arch
        wd.ai_explain = real_explain
    return code, out.getvalue(), err.getvalue()


print("═" * 60)
print("① 跨进程: research --archive → 独立进程 archive get 逐字节一致")
print("═" * 60)
NOTE1 = '备注: 政策利率水平问题(虚构)'
rc1, out1, _ = run_proj('research', '--question', Q_POLICY, '--archive',
                        '--note', NOTE1)
d1 = json.loads(out1)
check("子进程① research --archive rc=0 已作答",
      rc1 == 0 and d1['ok'] and d1['data']['status'] == 'answered',
      f"rc={rc1} status={d1.get('data', {}).get('status')}")
qid = d1['data'].get('archived_query_id')
answer1 = d1['data'].get('answer_text')
check("archived_query_id 在场(QB 格)", bool(qid) and re.match(r'^QB-\d{8}-\d{3}$', qid))
# 既有既定行为: 模块默认目录已含家族段,_collection_dir 再拼一次 → 双层嵌套
# (cmd_archive 输出的 ARCHIVE_DOUBLE_NEST 提示所指),base 与 sidecar 同目录
coll = os.path.join(PROJ, 'data', 'research', 'research_archive',
                    'research_archive', 'query_history')
check("base 记录与 sidecar 文件并存在副本档案目录",
      os.path.isfile(os.path.join(coll, f'{qid}.json'))
      and os.path.isfile(os.path.join(coll, f'{qid}.research-full.json')))
rc2, out2, _ = run_proj('archive', 'get', '--query-id', qid)
d2 = json.loads(out2)
check("子进程② archive get rc=0", rc2 == 0 and d2['ok'])
check("data.record=旧档原样(query_history)",
      d2['data']['record']['record_type'] == 'query_history'
      and d2['data']['record']['query_id'] == qid)
full2 = d2['data'].get('full')
check("data.full 并列合并视图在场", isinstance(full2, dict))
check("sidecar answer_text 与首进程用户所见**逐字节一致**(绝不重新生成)",
      full2 is not None and full2.get('answer_text') == answer1)
check("sidecar user_note 落位", full2 is not None and full2.get('user_note') == NOTE1)
check("sidecar model=null(未请求 --explain,如实 null)",
      full2 is not None and full2.get('model') is None)
check("sidecar digest 与 base 一致(同一 R5 重算)",
      full2 is not None
      and full2.get('digest_snapshot') == d2['data']['record']['digest_snapshot'])
check("合并视图保 base 身份(record_type 不被 sidecar 覆盖)",
      d2['data']['record']['record_type'] == 'query_history')

print("═" * 60)
print("⑤ list 不把 sidecar 当独立记录 / ⑥ list 摘要")
print("═" * 60)
rc3, out3, _ = run_proj('archive', 'list')
d3 = json.loads(out3)
base_files = [n for n in os.listdir(coll)
              if re.match(r'^QB-\d{8}-\d{3}\.json$', n)]
full_files = [n for n in os.listdir(coll) if n.endswith('.research-full.json')]
check("目录里 base 与 sidecar 文件并存(非零)",
      len(base_files) >= 1 and len(full_files) >= 1)
check("list n_total=base 文件数(sidecar 不算独立记录)",
      d3['data']['n_total'] == len(base_files), f"{d3['data']['n_total']} vs {len(base_files)}")
row = next((r for r in d3['data']['records'] if r['query_id'] == qid), None)
check("该记录 has_full=true", row is not None and row.get('has_full') is True)
check("list 摘要含 user_note 前60字", row is not None
      and row.get('user_note') == NOTE1[:60])

print("═" * 60)
print("② 旧档无 sidecar → 只有 base / ⑧ 旧契约不动")
print("═" * 60)
# 沙箱: 存一条 base 后删掉 sidecar = 模拟功能上线前的旧档
snap_s = make_snap()
qid_old, err = wd.save_to_archive(Q_POLICY, snap_s, ROOT, archive_dir=SBX)
old_sidecar = os.path.join(ra._collection_dir(SBX), f'{qid_old}.research-full.json')
if os.path.exists(old_sidecar):
    os.remove(old_sidecar)
check("沙箱旧档就绪(base 在,sidecar 无)",
      bool(qid_old) and not os.path.exists(old_sidecar), str(err))
code, out, _ = run_inproc('archive', 'get', '--query-id', qid_old)
dg = json.loads(out)
check("旧档 get: record 原样且**无 full 键**", dg['ok']
      and 'record' in dg['data'] and 'full' not in dg['data'])
check("旧档 load_research_full → None(不报错)",
      ra.load_research_full(qid_old, archive_dir=SBX) is None)
code, out, _ = run_inproc('archive', 'list')
dl = json.loads(out)
row_old = next((r for r in dl['data']['records'] if r['query_id'] == qid_old), None)
check("旧档 list: has_full=false 不报错",
      row_old is not None and row_old.get('has_full') is False)
check("QUERY_RECORD_KEYS 旧契约一字不动",
      ra.QUERY_RECORD_KEYS == ("record_type", "query_id", "created_at", "mode",
                               "question_text", "as_of", "snapshot_id",
                               "digest_snapshot", "ir", "ir_stage", "answer_summary",
                               "promoted_to_task_id", "archived_at"))
check("sidecar 文件名不匹配 _QUERY_FILE_RE(不被当 base 记录)",
      not ra._QUERY_FILE_RE.match('QB-20261108-001.research-full.json'))

print("═" * 60)
print("③ 重复 query_id sidecar 拒绝覆写")
print("═" * 60)
coll_sbx = ra._collection_dir(SBX)
rc4, out4, _ = run_inproc('research', '--question', '美元兑日元现在什么水平?',
                          '--archive')
d4 = json.loads(out4)
qid_b = d4['data'].get('archived_query_id')
side_b = os.path.join(coll_sbx, f'{qid_b}.research-full.json')
before = open(side_b, 'rb').read()
st, _p = ra.write_research_full(coll_sbx, json.loads(open(side_b, encoding='utf-8').read()))
check("write_research_full 重复 → rejected-duplicate", st == ra.STATUS_REJECTED_DUPLICATE)
check("拒写后文件字节不变(append-only)", open(side_b, 'rb').read() == before)

print("═" * 60)
print("④ --follow-up-of 链接校验")
print("═" * 60)
code, out, _ = run_inproc('research', '--question', Q_POLICY,
                          '--follow-up-of', 'QB-20990101-001')
check("前档不存在 → rc=2 invalid_follow_up",
      code == 2 and json.loads(out)['error']['kind'] == 'invalid_follow_up')
code, out, _ = run_inproc('research', '--question', '美元兑日元现在什么水平?',
                          '--archive', '--follow-up-of', qid_old)
d5 = json.loads(out)
qid_c = d5['data'].get('archived_query_id')
full_c = ra.load_research_full(qid_c, archive_dir=SBX)
check("有效前档 → rc=0 且 sidecar.follow_up_of=前档 qid",
      code == 0 and full_c is not None and full_c.get('follow_up_of') == qid_old)
code, out, _ = run_inproc('archive', 'save', '--question', '独立保存的问题',
                          '--follow-up-of', 'QB-00000000-001')
check("archive save 前档不存在 → rc=2",
      code == 2 and json.loads(out)['error']['kind'] == 'invalid_follow_up')

print("═" * 60)
print("⑥ archive save --note 落位(answer 字段如实 null)")
print("═" * 60)
code, out, _ = run_inproc('archive', 'save', '--question', '独立保存的问题',
                          '--note', '独立备注XYZ')
d6 = json.loads(out)
qid_d = d6['data']['query_id']
full_d = ra.load_research_full(qid_d, archive_dir=SBX)
check("独立保存 sidecar: user_note 落位", code == 0 and full_d.get('user_note') == '独立备注XYZ')
check("独立保存 sidecar: answer 相关字段=null(无本次作答,不编造)",
      full_d.get('answer_text') is None and full_d.get('status') is None
      and full_d.get('values') is None and full_d.get('model') is None)

print("═" * 60)
print("⑥b W4 写入消毒: 含密钥文本过 redact() 落盘,读取层不过滤")
print("═" * 60)
LEAK_Q = '问一下 ?api_key=FAKESIDEKEY123&x=1 这个端点'
LEAK_NOTE = '备注 token=FAKESIDEKEY456 散文回显,另见 Bearer sk-SIDEKEY' + 'X' * 20
code, out, _ = run_inproc('archive', 'save', '--question', LEAK_Q,
                          '--note', LEAK_NOTE)
d6b = json.loads(out)
qid_6b = d6b['data']['query_id']
full_6b = ra.load_research_full(qid_6b, archive_dir=SBX)
check("消毒落盘: question_text 密钥值消失+REDACTED标记",
      full_6b is not None and 'FAKESIDEKEY123' not in full_6b.get('question_text', '')
      and 'api_key=***REDACTED***' in full_6b.get('question_text', ''))
check("消毒落盘: user_note 密钥值消失+REDACTED标记",
      'FAKESIDEKEY456' not in full_6b.get('user_note', '')
      and 'token=***REDACTED***' in full_6b.get('user_note', ''))
check("消毒落盘: 裸 Bearer 长值(批2W7)脱敏",
      'sk-SIDEKEY' + 'X' * 20 not in full_6b.get('user_note', '')
      and 'Bearer ***REDACTED***' in full_6b.get('user_note', ''))
check("消毒不改结构: 其余字段仍在(question_text 非空)",
      bool(full_6b.get('question_text')))

print("═" * 60)
print("⑦ AI 解释 mock(虚构响应文本,零真实调用)")
print("═" * 60)
explain_calls = []   # v2.1: mock 的是 wd.ai_explain


def mock_ai_explain(question, grounded_text):
    explain_calls.append((question, grounded_text))
    return {'ok': True, 'text': 'MOCK_GLM_RESPONSE_虚构响应文本_绝不联网'}


code, out, _ = run_inproc('research', '--question', Q_POLICY, '--explain',
                          '--archive', explain_mock=mock_ai_explain)
d7 = json.loads(out)
qid_e = d7['data'].get('archived_query_id')
full_e = ra.load_research_full(qid_e, archive_dir=SBX)
check("mock AI 解释恰好调用 1 次(零真实调用)", len(explain_calls) == 1)
check("sidecar.model 原文=本次实际返回(mock 文本逐字节)",
      full_e is not None and full_e.get('model') == {'ok': True,
                                                     'text': 'MOCK_GLM_RESPONSE_虚构响应文本_绝不联网'})
check("research stdout data.model 与 sidecar 一致",
      d7['data']['model']['text'] == full_e['model']['text'])

# 清理: 沙箱与副本整体移除(子进程已全部结束)
shutil.rmtree(TD, ignore_errors=True)

print()
print("═" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("═" * 60)
sys.exit(0 if FAIL == 0 else 1)
