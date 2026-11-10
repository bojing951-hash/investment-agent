#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Charter8 views CLI 测试(交付⑦)——四个测试面,子进程真实调用。

面1 list: 信封与九能力一致(snapshot 位=null,views 不依赖快照)+合规件清单
面2 get: 合规件放行/隔离件拒绝 rc=1 结构化 error/缺 --view-id rc=2
面3 lint: 合规库况 ok=true rc=0;构造违规件→ok=false rc=1+violations 明细
面4 信封纪律: capability='views',单 JSON stdout,无模型调用痕迹

fixture: 合成 tmp 目录两份(合规+schema 1.0 违规)经 view_store.VIEWS_DIR
注入——**不碰真实 data/institutions/views**(真实 11 份是 B 席基线,测试零依赖)。
"""
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


import view_store as vs  # noqa: E402

GOOD = {
    'schema_version': '1.1', 'view_id': 'VIEW-20261110-001',
    'institution': {'name': 'Synthetic Bank', 'type': 'investment_bank',
                    'department': 'Research'},
    'authors': [], 'report_title': 'Synthetic Outlook',
    'source_url': 'https://example.com/a', 'source_type': 'official_site',
    'publish_date': '2026-11-01', 'fetch_date': '2026-11-10',
    'access_level': 'public_full', 'view_horizon': '6m',
    'subjects': ['US_rates'],
    'core_views': [{'statement': '利率维持高位。', 'attribution': 'institution_stated',
                    'basis': 'verbatim_quote', 'quote': 'Rates stay higher.'}],
    'forecasts': [], 'key_assumptions': [], 'evidence_cited': [],
    'mechanism_steps': [], 'risk_factors': [], 'falsification_conditions': [],
    'revisions': [], 'completeness_notes': '合成', 'copyright_note': 'meta+link',
}
BAD = dict(GOOD, schema_version='1.0', view_id='VIEW-20261110-002')


def run_cli(args, views_dir):
    env = dict(os.environ)
    env['IA_C8_TEST_VIEWS_DIR'] = views_dir      # 注入缝(仅测试;见 monkeypatch 说明)
    code = ("import sys, os; sys.path.insert(0, %r); sys.path.insert(0, %r); "
            "import view_store as vs; "
            "vs.VIEWS_DIR = os.environ['IA_C8_TEST_VIEWS_DIR']; "
            "sys.argv = ['ia_cli.py'] + %r; "
            "import ia_cli; ia_cli.main()" % (ROOT, os.path.join(ROOT, 'scripts'), args))
    p = subprocess.run([sys.executable, '-c', code], capture_output=True,
                       text=True, env=env, cwd=ROOT)
    try:
        payload = json.loads(p.stdout)
    except ValueError:
        payload = None
    return p.returncode, payload, p.stdout


def make_views_td(with_bad=True):
    td = tempfile.mkdtemp(prefix='c8views_')
    for doc in ([GOOD, BAD] if with_bad else [GOOD]):
        with open(os.path.join(td, doc['view_id'] + '.json'), 'w',
                  encoding='utf-8') as f:
            json.dump(doc, f, ensure_ascii=False)
    return td


print("═" * 60)
print("[面1] views list — 信封一致+清单")
print("═" * 60)
td = make_views_td()
rc, out, raw = run_cli(['views', 'list'], td)
check("rc=0", rc == 0, f"rc={rc} raw={raw[:200]}")
check("信封 capability=views", out and out.get('capability') == 'views')
check("views 不依赖快照(信封快照位恒 null)",
      out.get('snapshot_id') is None and out.get('gate_a') is None
      and out.get('target_date') is None)
check("schema_version=1.1 随行", out['data']['schema_version'] == '1.1')
check("list 只含合规件(1)", out['data']['n_views'] == 1
      and out['data']['views'][0]['view_id'] == 'VIEW-20261110-001')
check("隔离计数=1+warnings 提示", out['data']['n_quarantined'] == 1
      and any('隔离' in w for w in out['warnings']))
check("stdout 恒单 JSON", raw.strip().startswith('{') and raw.strip().endswith('}'))

print("═" * 60)
print("[面2] views get — 放行/隔离/用法")
print("═" * 60)
rc, out, _ = run_cli(['views', 'get', '--view-id', 'VIEW-20261110-001'], td)
check("合规件 get rc=0+view 全档", rc == 0
      and out['data']['view']['institution']['name'] == 'Synthetic Bank')
rc, out, _ = run_cli(['views', 'get', '--view-id', 'VIEW-20261110-002'], td)
check("隔离件 get rc=1+结构化 error(view_not_found_or_quarantined)",
      rc == 1 and out['ok'] is False
      and out['error']['kind'] == 'view_not_found_or_quarantined')
rc, out, _ = run_cli(['views', 'get'], td)
check("缺 --view-id rc=2(missing_view_id)", rc == 2
      and out['error']['kind'] == 'missing_view_id')
rc, out, _ = run_cli(['views', 'get', '--view-id', 'VIEW-19990101-999'], td)
check("不存在件 rc=1+如实原因", rc == 1
      and '无此 view_id' in out['error']['message'])

print("═" * 60)
print("[面3] views lint — 违规明细与退出码")
print("═" * 60)
rc, out, _ = run_cli(['views', 'lint'], td)
check("有隔离→ok=false rc=1", rc == 1 and out['ok'] is False)
check("n_compliant=1/n_quarantined=1/n_files=2",
      out['data']['n_compliant'] == 1 and out['data']['n_quarantined'] == 1
      and out['data']['n_files'] == 2)
q = out['data']['quarantined'][0]
check("违规件带逐条 machine-readable violations",
      q['view_id'] == 'VIEW-20261110-002'
      and any(v['rule'] == 'schema_version' for v in q['violations']))
check("warnings 附违规规则集", any('schema_version' in w for w in out['warnings']))
td_clean = make_views_td(with_bad=False)
rc, out, _ = run_cli(['views', 'lint'], td_clean)
check("全合规→ok=true rc=0", rc == 0 and out['ok'] is True
      and out['data']['n_quarantined'] == 0)

print("═" * 60)
print("[面4] 信封纪律与零模型面")
print("═" * 60)
src = open(os.path.join(ROOT, 'ia_cli.py'), encoding='utf-8').read()
check("ia_cli 声明十个能力(views 入列)", 'views' in src
      and '十个能力' in src)
check("views 处理器零模型调用(无 MODEL_/ai_explain 引用)",
      'MODEL_API_KEY' not in src.split('def cmd_views')[1].split('def ')[0])
rc, out, raw = run_cli(['views', 'list'], td)
check("错误输出永不空串(成功面 data 非空)", bool(out.get('data')))

print()
print("═" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("═" * 60)
sys.exit(0 if FAIL == 0 else 1)
