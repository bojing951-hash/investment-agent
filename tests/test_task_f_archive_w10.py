#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""任务F 跨模型完整成果归档+收尾回归(批2 W10, 2026-11-09)。

覆盖:
① 两种不同风格「模拟 Agent 成果」fixture → archive save(完整成果六参)→
   **独立 python3 子进程** get → 正文/来源/统计/假设/开放问题逐字一致;
② --as-of 落 research_as_of 位;--follow-up-of 关联逐字回读;
③ 成果文本写入前过 redact(内嵌虚构 api_key/Bearer 形态 → 落盘已脱敏);
④ 不带新参 save=旧行为(成果键 null);旧格式 sidecar(缺新键)get 归一 null;
⑤ schema 增补键类型守卫(evidence 非 str → ValueError fail-loud);
⑥ 拒答导流文案(C-4): unmapped/no_registry_identity 拒答文本附 Agent 组合导流行;
⑦ lint 四分(D5): 事实/推断/假设/尚未验证——【尚未验证】后文字不计事实位;
⑧ 四路终审 D-1/D-2: URL 编码形(api_key%3D/%61pi_key=)穿透修补——登记明文
   值级清扫兜底,基档(QB-*.json 含 ir 内嵌)与 sidecar 双层落盘全净;
⑨ 四路终审 R1: monthly_review/quarterly_outlook 模型三参预检——未配齐时
   中性提示 exit 2,不构造客户端不炸栈(零数据/零密钥子进程)。

运行: python3 tests/test_task_f_archive_w10.py(仓库副本+子进程,零网络零真实数据)。
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
from redact_secrets import redact  # noqa: E402

PASS, FAIL = 0, 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")


# ══ 合成快照(同 WI6 套件口径;数值全虚构) ═════════════════════════════
OBS = '2026-11-06'


def _fact(fid, mid, name, val, unit, collector):
    return {'fact_id': f'{fid}@{OBS}', 'metric_id': mid, 'display_name': name,
            'value': val, 'unit': unit, 'value_type': 'level',
            'observation_date': OBS, 'as_of': '2026-11-08',
            'source': {'collector': collector, 'file': 'synthetic_20261108.json'},
            'quality_status': 'PASS', 'issues': [], 'derived': {}}


def make_snap():
    return {'snapshot_id': 'research_snapshot_20261108', 'target_date': '20261108',
            'research_as_of': '2026-11-08T18:00:00+08:00',
            'gate_a': {'status': 'DEGRADED', 'core_missing': [], 'noncore_missing': [],
                       'noncore_missing_detail': {}, 'noncore_degraded': []},
            'sources_status': {},
            'facts': [
                _fact('F1', 'DFEDTARU', '联邦基金目标区间上限', 4.00, 'percent',
                      'rate_expectations'),
                _fact('F2', 'USDJPY', '美元兑日元', 152.35, 'jpy_per_usd',
                      'global_market_collector')],
            'series_store': {}}


# ══ 仓库副本(子进程跨进程归档,档案落副本内) ═══════════════════════════
TD = tempfile.mkdtemp(prefix='w10-taskf-')
PROJ = os.path.join(TD, 'proj')
shutil.copytree(os.path.join(ROOT, 'scripts'), os.path.join(PROJ, 'scripts'))
shutil.copytree(os.path.join(ROOT, 'config'), os.path.join(PROJ, 'config'))
shutil.copy2(os.path.join(ROOT, 'ia_cli.py'), os.path.join(PROJ, 'ia_cli.py'))
os.makedirs(os.path.join(PROJ, 'data', 'daily'))
with open(os.path.join(PROJ, 'data', 'daily', 'research_snapshot_20261108.json'),
          'w', encoding='utf-8') as f:
    json.dump(make_snap(), f, ensure_ascii=False)


def run_proj(*argv):
    """独立 python3 子进程跑副本 ia_cli(重启进程口径)。"""
    r = subprocess.run([sys.executable, os.path.join(PROJ, 'ia_cli.py'), *argv],
                       capture_output=True, text=True, timeout=120, cwd=TD)
    return r.returncode, r.stdout, r.stderr


def run_inproc(*argv, snap=None):
    """进程内跑 ia_cli.main(load_context 指合成快照;档案=沙箱)。"""
    real_ctx, real_arch = ia_cli.load_context, ia_cli._ARCHIVE_DIR
    ia_cli.load_context = lambda: (snap or make_snap(), wd.load_registry(ROOT), '')
    ia_cli._ARCHIVE_DIR = os.path.join(TD, 'sbx-arch')
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
    return code, out.getvalue(), err.getvalue()


# ══ 两种风格的模拟 Agent 成果 fixture(手写文本,非引擎产出) ══════════════
ANSWER_A = (
    '【事实】美国政策利率区间上限 4.00%(观测 2026-11-06,rate_expectations 采集);'
    '美元兑日元 152.35(观测 2026-11-06)。\n'
    '【推断】利差维持高位或对日元构成持续压力,但汇率由多因子决定,相关不等于因果。\n'
    '【尚未验证】套息交易平仓规模与本轮日元波动的因果链未在本地数据可证范围。\n'
    '(调试备注: 调试时曾见 api_key=sk-W10FAKEKEY0000000000 形态的配置样例)')
EVIDENCE_A = (
    '来源1: 快照事实 DFEDTARU=4.00 percent(observation_date=2026-11-06)\n'
    '来源2: 快照事实 USDJPY=152.35 jpy_per_usd(observation_date=2026-11-06)\n'
    '(抓包样例头: Authorization: Bearer sk-W10EVIDBEARER00000000 —— 虚构)')
STATS_A = ('区间 2026-01~2026-11: USDJPY 年内 +6.2%(手算复核);'
           '滚动 20 日相关 rho=+0.41(窗内 188 对,<30 样本警告在场时不可外推)')
HYP_A = ('H1(利差主导): 与【推断】一致,证据强;\n'
         'H2(风险偏好主导): 与同期股指同向性部分吻合,证据弱——竞争性假设并列保留。')
OPENQ_A = '日本央行下一步会议(12月)是否调整YCC区间?本地数据无法回答,留开放。'

ANSWER_B = ('- fact: FED target upper 4.00 pct (2026-11-06)\n'
            '- fact: USDJPY 152.35 (2026-11-06)\n'
            '- inference: carry pressure persists; NOT causal\n'
            '- open: BoJ Dec meeting outcome unknown')
EVIDENCE_B = ('snapshot facts DFEDTARU / USDJPY; series_store via ia_cli history')
STATS_B = 'rho_20d=+0.41 (n=188, sample<30 warning applies)'
HYP_B = 'H1 rate-differential dominant; H2 risk-appetite channel (weaker)'
OPENQ_B = 'BoJ December decision'
AS_OF_B = '2026-11-09T20:00:00+08:00'

print("═" * 60)
print("① 两种风格模拟 Agent 成果: save(六参) → 重启进程 get 逐字一致")
print("═" * 60)
rcA, outA, _ = run_proj('archive', 'save', '--question',
                        '美日政策利率差对美元兑日元意味着什么(模拟Agent成果A)',
                        '--answer-text', ANSWER_A, '--evidence', EVIDENCE_A,
                        '--statistics', STATS_A, '--hypotheses', HYP_A,
                        '--open-questions', OPENQ_A,
                        '--note', '风格A: 中文分节研究正文')
dA = json.loads(outA)
check("save A rc=0 saved=True", rcA == 0 and dA['ok'] and dA['data']['saved'])
qidA = dA['data']['query_id']
check("query_id QB 格", bool(re.match(r'^QB-\d{8}-\d{3}$', qidA or '')))
rcB, outB, errB = run_proj('archive', 'save', '--question',
                           'USDJPY note (simulated agent artifact B)',
                           '--answer-text', ANSWER_B, '--evidence', EVIDENCE_B,
                           '--statistics', STATS_B, '--hypotheses', HYP_B,
                           '--open-questions', OPENQ_B, '--as-of', AS_OF_B,
                           '--follow-up-of', qidA, '--note', '风格B: bullet 英文')
dB = json.loads(outB)
check("save B rc=0(关联前档 A 通过存在性校验)",
      rcB == 0 and dB['ok'] and dB['data']['saved'], errB[-200:] if rcB else '')
qidB = dB['data']['query_id']

rcg, outg, _ = run_proj('archive', 'get', '--query-id', qidA)
gA = json.loads(outg)['data']
fullA = gA['full']
check("get A(独立进程) rc=0,base 保 query_history 身份",
      rcg == 0 and gA['record']['record_type'] == 'query_history')
check("A 正文逐字一致(redact 后口径: 内嵌 api_key 样例已脱敏)",
      fullA['answer_text'] == redact(ANSWER_A), repr(fullA['answer_text'][-60:]))
check("A 来源逐字一致(Bearer 长值样例已脱敏)",
      fullA['evidence'] == redact(EVIDENCE_A))
check("A 统计/假设/开放问题逐字一致",
      fullA['statistics'] == redact(STATS_A)
      and fullA['hypotheses'] == redact(HYP_A)
      and fullA['open_questions'] == redact(OPENQ_A))
check("A 密钥零落盘(原始虚构 Key 不在 sidecar 任何字段)",
      'sk-W10FAKEKEY' not in json.dumps(fullA, ensure_ascii=False)
      and 'sk-W10EVIDBEARER' not in json.dumps(fullA, ensure_ascii=False)
      and '***REDACTED***' in fullA['answer_text']
      and '***REDACTED***' in fullA['evidence'])
check("A 未传 --as-of → research_as_of=快照口径",
      fullA['research_as_of'] == '2026-11-08T18:00:00+08:00')
check("A follow_up_of=null(首档)",
      fullA['follow_up_of'] is None)

rcg, outg, _ = run_proj('archive', 'get', '--query-id', qidB)
fullB = json.loads(outg)['data']['full']
check("B 正文/来源逐字一致(第二种风格)",
      fullB['answer_text'] == ANSWER_B and fullB['evidence'] == EVIDENCE_B)
check("B --as-of 落 research_as_of 位(逐字)",
      fullB['research_as_of'] == AS_OF_B)
check("B --follow-up-of 关联逐字回读(==A 的 query_id)",
      fullB['follow_up_of'] == qidA)

print("═" * 60)
print("④ 不带新参=旧行为;旧格式 sidecar(缺新键)读侧归一 null")
print("═" * 60)
rcL, outL, _ = run_proj('archive', 'save', '--question', '仅问题独立保存(旧口径)')
dL = json.loads(outL)
qidL = dL['data']['query_id']
check("legacy save rc=0", rcL == 0 and dL['ok'])
rcg, outg, _ = run_proj('archive', 'get', '--query-id', qidL)
fullL = json.loads(outg)['data']['full']
check("legacy sidecar: answer 相关字段如实 null,成果键 null(非缺席)",
      fullL['answer_text'] is None and fullL['evidence'] is None
      and fullL['statistics'] is None and fullL['hypotheses'] is None
      and fullL['open_questions'] is None)
sideL = os.path.join(PROJ, 'data', 'research', 'research_archive',
                     'research_archive', 'query_history',
                     f'{qidL}.research-full.json')
doc = json.load(open(sideL, encoding='utf-8'))
for k in ('evidence', 'statistics', 'hypotheses', 'open_questions'):
    del doc[k]                       # 旧格式 sidecar: 无成果键(W10 之前落盘形态)
with open(sideL, 'w', encoding='utf-8') as f:
    json.dump(doc, f, ensure_ascii=False, indent=1, sort_keys=True)
rcg, outg, _ = run_proj('archive', 'get', '--query-id', qidL)
fullL2 = json.loads(outg)['data']['full']
check("旧格式 sidecar 缺键 → get 合并视图归一 null(不报错不破坏)",
      rcg == 0 and fullL2['evidence'] is None
      and fullL2['open_questions'] is None)

print("═" * 60)
print("⑤ schema 增补键类型守卫(可选键在场须 str|null)")
print("═" * 60)
try:
    bad = dict(doc)
    bad['evidence'] = 123             # 非 str 非 null → fail-loud
    ra.write_research_full(ra._collection_dir(os.path.join(TD, 'guard-arch')), bad)
    check("evidence=123 → ValueError", False, '未拒绝')
except ValueError as e:
    check("evidence=123 → ValueError(fail-loud)", 'evidence须为str|null' in str(e))
    ra_ok = ra.validate_research_full(doc)   # 旧格式(缺可选键)仍合法
    check("旧格式 payload(缺可选键)校验仍通过", ra_ok == [])

print("═" * 60)
print("⑥ 拒答导流文案(C-4): unmapped/no_registry_identity 附 Agent 组合导流")
print("═" * 60)
code, out, _ = run_inproc('research', '--question', '意大利面的最佳煮法是什么')
dU = json.loads(out)
check("unmapped 拒答文本末尾附导流行(逐字)",
      dU['data']['status'] == 'unmapped'
      and dU['data']['answer_text'].rstrip().endswith(ia_cli.AGENT_ROUTING_HINT))
code, out, _ = run_inproc('research', '--question', '火星的GDP现在是多少')
dN = json.loads(out)
check("no_registry_identity 拒答文本末尾附导流行(逐字)",
      dN['data']['status'] == 'no_registry_identity'
      and dN['data']['answer_text'].rstrip().endswith(ia_cli.AGENT_ROUTING_HINT))
check("导流行含四能力组合(history/compare/overview/changes)",
      all(w in ia_cli.AGENT_ROUTING_HINT for w in
          ('history', 'compare', 'overview', 'changes', 'Agent')))
code, out, _ = run_inproc('research', '--question', '美国政策利率现在是多少')
dO = json.loads(out)
check("answered 正常作答不附导流行(导流只挂拒答)",
      dO['data']['status'] == 'answered'
      and ia_cli.AGENT_ROUTING_HINT not in dO['data']['answer_text'])

print("═" * 60)
print("⑦ lint 四分(D5): 事实/推断/假设/尚未验证")
print("═" * 60)
L = ia_cli.lint_fact_contract_text
check("事实位因果动词 → 1 violation",
      len(L('非农不及预期,降息预期提振股市')) == 1)
check("【推断】标记后=本分,不计事实位", L('【推断】降息预期提振股市') == [])
check("【假设】标记后=本分", L('【假设】流动性驱动估值扩张') == [])
check("【尚未验证】标记后=本分(四分衔接新增)",
      L('【尚未验证】关税引发汇率波动') == [])
check("同行事实位在标记前: 标记前文本含因果动词仍违约",
      len(L('关税引发股市下跌【尚未验证】后续路径')) == 1)
check("同行事实位在标记前: 标记前文本干净则整行免检",
      L('股市波动加大【尚未验证】关税引发回调') == [])

print("═" * 60)
print("⑧ D-1/D-2: URL 编码形穿透修补(登记明文清扫,基档+sidecar 双层)")
print("═" * 60)
os.environ['FINNHUB_API_KEY'] = 'sk-FINNURLFAKE00000'   # 虚构值(登记清扫锚点)
try:
    Q_D = ('调试: api_key%3Dsk-FINNURLFAKE00000 与 %61pi_key=sk-FINNURLFAKE00000'
           ' 双形(四路终审 D-1 实测形态)')
    rcD, outD, _ = run_proj('archive', 'save', '--question', Q_D,
                            '--answer-text', '正文 Bearer sk-D1BODYFAKE0000000 原样')
    dD = json.loads(outD)
    qidD = dD['data']['query_id']
    collD = os.path.join(PROJ, 'data', 'research', 'research_archive',
                         'research_archive', 'query_history')
    base_raw = open(os.path.join(collD, f'{qidD}.json'), encoding='utf-8').read()
    full_raw = open(os.path.join(collD, f'{qidD}.research-full.json'),
                    encoding='utf-8').read()
    check("D-1 sidecar: 双 URL 编码形全清扫(值级,含 %3D 与 %61 前缀)",
          'sk-FINNURLFAKE' not in full_raw
          and full_raw.count('***REDACTED***') >= 2, full_raw[:0])
    check("D-1 基档: 双 URL 编码形同样清扫(redact 模式外的登记明文兜底)",
          'sk-FINNURLFAKE' not in base_raw)
    check("D-2 基档: question_text 与 ir 内嵌问题串的 URL 形已脱敏"
          "(Bearer 在 answer_text,随 sidecar 层走)",
          'sk-D1BODYFAKE' not in base_raw
          and 'api_key%3D***REDACTED***' in base_raw)
    # 双入口单点验证: research --archive 与 archive save 同经 append_query_record,
    # 以真实 mapper 产 IR(问题串嵌 Bearer 形)直调写入层,证明通道无关
    import e2eb_query_mapper as qm
    _snapD = make_snap()
    _qD = '研究通道题: Authorization: Bearer sk-D2RESFAKE00000000'
    _dirD = os.path.join(TD, 'd2-direct')
    _createdD = '2099-01-01T00:00:00+00:00'
    _qidD = ra.allocate_query_id(_createdD, archive_dir=_dirD)
    _irD = qm.map_question(_qD, created_at=_createdD,
                           query_seq=int(_qidD.rsplit('-', 1)[-1]))
    _st, _ = ra.append_query_record(_irD, snapshot=_snapD, archive_dir=_dirD)
    _raw = open(os.path.join(_dirD, 'research_archive', 'query_history',
                             f'{_qidD}.json'), encoding='utf-8').read()
    check("D-2 写入层单点: 直调 append_query_record 基档同样脱敏(通道无关)",
          _st == 'written' and 'sk-D2RESFAKE' not in _raw
          and 'Bearer ***REDACTED***' in _raw)
finally:
    os.environ.pop('FINNHUB_API_KEY', None)

print("═" * 60)
print("⑨ R1: 月/季报模型三参预检(未配齐 → 中性提示 exit 2,不炸栈)")
print("═" * 60)
R1TD = tempfile.mkdtemp(prefix='w10-r1-')
R1PROJ = os.path.join(R1TD, 'proj')
shutil.copytree(os.path.join(ROOT, 'scripts'), os.path.join(R1PROJ, 'scripts'))
shutil.copytree(os.path.join(ROOT, 'config'), os.path.join(R1PROJ, 'config'))
shutil.copy2(os.path.join(ROOT, 'env_config.py'), os.path.join(R1PROJ, 'env_config.py'))
# 不复制 .env;子进程剥离 MODEL_*/GLM_* 环境变量 → 三参不齐口径
r1env = {k: v for k, v in os.environ.items()
         if not k.startswith(('MODEL_', 'GLM_'))}
for script, flag in (('monthly_review.py', '--month'), ('quarterly_outlook.py', '--quarter')):
    r = subprocess.run([sys.executable, os.path.join(R1PROJ, 'scripts', script),
                        flag, '202610' if flag == '--month' else '2026Q3'],
                       capture_output=True, text=True, timeout=120, cwd=R1TD, env=r1env)
    tail = (r.stderr + r.stdout)
    check(f"{script}: 未配三参 → exit 2(中性退出)",
          r.returncode == 2, f"rc={r.returncode}")
    check(f"{script}: 中性提示在场(data-only 周报可用 + MODEL_* 三参指引)",
          'data-only' in tail and 'MODEL_API_KEY' in tail)
    check(f"{script}: 无 Traceback(不构造客户端不炸栈)",
          'Traceback' not in tail and 'RuntimeError' not in tail)
shutil.rmtree(R1TD, ignore_errors=True)

print("═" * 60)
shutil.rmtree(TD, ignore_errors=True)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("═" * 60)
sys.exit(0 if FAIL == 0 else 1)
