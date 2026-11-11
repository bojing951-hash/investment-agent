#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R2(autonomous-rd 2026-11-11): 一键研究编排器验收套件(AC6)。

覆盖面:
[1] 确定性实体映射(中文 display_name/metric_id 命中;零命中如实 unmapped;
    经济体词边界——'EA' 不得被 'treasury' 子串误命中)
[2] ia_cli research-run 命令面(build_parser 实解析+真实子进程信封)
[3] 真实数据全管线(run_research 十一步;快照缺席时按惯例 SKIP)
[4] 四层区分(L3 AI推断/L4 条件情景恒 produced=False 且有归属注记)
[5] 逐数证据索引(L1/L2 每行带 fact_id/VP-id 级来源;S10 自检)
[6] 诚实面(S8 拒答透传不加戏;S5 不足两指标如实跳过;S11 落档默认关)
[7] C 契约不动(管线运行前后 VP sidecar 哈希一致)
[8] 确定性(同一问题两跑步骤序列+层摘要一致,时间戳除外)
纪律: 预期值不经被测函数自算;真实面在本机全量套件执行。
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

PASS, FAIL, SKIP = 0, 0, 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")


def section(title):
    print("═" * 64)
    print(f"[{title}]")
    print("═" * 64)


def vp_dir_hash():
    d = os.path.join(ROOT, 'data', 'institutions', 'verification')
    if not os.path.isdir(d):
        return None
    h = hashlib.sha256()
    for fn in sorted(os.listdir(d)):
        if fn.startswith('VP-') and fn.endswith('.json'):
            h.update(fn.encode())
            h.update(open(os.path.join(d, fn), 'rb').read())
    return h.hexdigest()


def main():
    global SKIP
    import workbench_data as wd
    snap, snap_note = wd.latest_snapshot(ROOT)
    has_real = snap is not None

    # ── [1] 确定性实体映射 ──────────────────────────────────────────
    section("1 确定性实体映射")
    import research_orchestrator as ro
    reg = wd.load_registry(ROOT)
    ent = ro.map_entities("10年期美债收益率 和 SPX 走势对比", reg)
    check("中文 display_name+metric_id 双命中",
          set(ent['metrics']) == {'SPX', 'UST_10Y'}, f"got {ent['metrics']}")
    ent_en = ro.map_entities("what about treasury yields and SPX", reg)
    check("零语义翻译纪律: 'treasury yields' 不猜映射(只 SPX 词面命中)",
          ent_en['metrics'] == ['SPX'], f"got {ent_en['metrics']}")
    check("零命中如实 unmapped+注记",
          ro.map_entities("美联储下次会议会降息吗", reg)['metrics'] == []
          and ro.map_entities("美联储下次会议会降息吗", reg)['note'],
          "应无指标命中且带降级注记")
    ent_ea = ro.map_entities("US treasury market outlook", reg)
    check("经济体词边界: 'EA' 不被 tr'ea'sury 误命中",
          'EA' not in ent_ea['economies'], f"got {ent_ea['economies']}")
    check("经济体中文标签命中", 'US' in ro.map_entities("美国经济怎么样", reg)['economies'])
    check("经济体代码词边界命中", 'US' in ro.map_entities("US 10Y outlook", reg)['economies'])

    # ── [2] ia_cli research-run 命令面 ──────────────────────────────
    section("2 ia_cli research-run 命令面")
    import ia_cli
    parser = ia_cli.build_parser()
    ns = parser.parse_args(['research-run', '--question', 'q'])
    check('research-run 子命令实解析', ns.capability == 'research-run'
          and ns.question == 'q' and ns.archive is False)
    check('ia_cli handlers 注册 research-run',
          'research-run' in ia_cli.main.__globals__ or
          hasattr(ia_cli, 'cmd_research_run'))

    # ── [3] 真实数据全管线 ──────────────────────────────────────────
    section("3 真实数据全管线(CI 无快照按惯例 SKIP)")
    if not has_real:
        SKIP += 1
        print(f"  ⏭ SKIP: 无快照({snap_note})——真实面在本机全量套件执行")
    else:
        tmp = tempfile.mkdtemp(prefix='rd_r2_rr_')
        try:
            before = vp_dir_hash()
            rep = ro.run_research("10年期美债收益率 和 SPX 走势对比",
                                  root=ROOT, out_dir=tmp)
            step_names = [s['step'] for s in rep['steps']]
            check("十一步台账齐备(S1..S11)",
                  step_names[0] == 'S1_decompose'
                  and step_names[-1] == 'S11_archive'
                  and any(s == 'S10_selfcheck' for s in step_names),
                  f"got {step_names}")
            check("run_ok=True(进程层全绿)", rep['run_ok'] is True)
            check("报告双落盘(report.json+report.md)",
                  os.path.isfile(os.path.join(rep['report_dir'], 'report.json'))
                  and os.path.isfile(os.path.join(rep['report_dir'], 'report.md')))
            check("L1 双指标真值行(非空映射)",
                  {r['metric_id'] for r in rep['layers']['L1_事实层']['rows']}
                  == {'SPX', 'UST_10Y'})
            check("L1 快照标识随行",
                  rep['layers']['L1_事实层']['snapshot_id'] == snap.get('snapshot_id'))
            check("S5 compare 真执行(≥2 命中)",
                  any(s['step'] == 'S5_compare' and s.get('executed')
                      and s.get('ok') for s in rep['steps']))
            gate = next(s for s in rep['steps'] if s['step'] == 'S7_mode_gate')
            check("S7 gate 从信封提取(research_mode_gate 三态)",
                  isinstance(gate.get('gate'), dict)
                  and 'realtime_info_set' in gate['gate'])

            # ── R2.1 修复回归(E席审计 MAJOR-1/2 + MINOR-1/2/3) ──────
            s5 = next(s for s in rep['steps'] if s['step'] == 'S5_compare')
            s5_gate = (((s5.get('envelope') or {}).get('data') or {})
                       .get('alignment') or {}).get('research_mode_gate')
            check("R2.1 MAJOR-1: S7 gate=S5 对齐门逐字段相等(修复前取错来源)",
                  s5_gate is not None and gate['gate'] == s5_gate
                  and gate.get('gate_source')
                  == 'S5_compare:data.alignment.research_mode_gate',
                  f"src={gate.get('gate_source')}")
            l4n = rep['layers']['L4_条件情景层']['note']
            check("R2.1 MAJOR-2: L4 五行=纪律16 权威模板(旧'前提/机制/路径'清除)",
                  all(k in l4n for k in ('情景', '置信层级', '敏感变量',
                                         '证伪指标', '触发条件'))
                  and '前提/机制/路径' not in l4n)
            l3n = rep['layers']['L3_AI推断层']['note']
            check("R2.1 MAJOR-2: L3 补 E1/E2/E3+四层标注指路(纪律15/4)",
                  all(k in l3n for k in ('E1', 'E2', 'E3', '四层标注')))
            check("R2.1 MINOR-1: 诚实拒答豁免(合成: 拒答步不翻 run_ok)",
                  ro._run_ok([{'step': 'X', 'executed': True, 'ok': False,
                               'honest_refusal': True}]) is True
                  and ro._run_ok([{'step': 'X', 'executed': True,
                                   'ok': False}]) is False)
            check("R2.1 MINOR-1: 本机 analog 未拒答则无豁免标记",
                  all('honest_refusal' not in s or s.get('ok')
                      for s in rep['steps']))
            md = open(os.path.join(rep['report_dir'], 'report.md'),
                      encoding='utf-8').read()
            check("R2.1 MINOR-3: report.md 台账含语义列(进程/语义分面)",
                  '[OK |语义✔] S1_decompose' in md.replace('  ', ' ')
                  or ('语义✔' in md and '## 步骤台账' in md))

            rep3 = ro.run_research(
                "10年期美债收益率 SPX 和 美元指数 走势对比",
                root=ROOT, out_dir=os.path.join(tmp, 'three'))
            s5b = next(s for s in rep3['steps'] if s['step'] == 'S5_compare')
            check("R2.1 MINOR-2: 命中>2 时 compare 截断披露(不静默)",
                  s5b.get('executed') and s5b.get('note')
                  and '前 2' in s5b['note'] and 'UST_10Y' in s5b['note'],
                  f"note={s5b.get('note')}")

            # ── R3 十问扇出(fanout=True 追加面) ─────────────────────
            section("9 十问扇出(--fanout;R3)")
            check("默认关: 主台账 run 不带扇出面",
                  rep.get('fanout', {}).get('requested') is False)
            repf = ro.run_research("10年期美债收益率 和 SPX 走势对比",
                                   root=ROOT, out_dir=os.path.join(tmp, 'fan'),
                                   fanout=True)
            fan = repf['fanout']
            check("扇出十问齐备(RQ1..RQ10)", fan['requested']
                  and fan['n_rq'] == 10
                  and [r['id'] for r in fan['rq']] == [f'RQ{i}' for i in
                                                       range(1, 11)])
            rq3 = next(r for r in fan['rq'] if r['id'] == 'RQ3')
            rq9 = next(r for r in fan['rq'] if r['id'] == 'RQ9')
            check("Agent 层问 declared-not-produced(RQ3/RQ9 零步骤+注记)",
                  rq3['agent_layer'] and not rq3['steps']
                  and rq9['agent_layer'] and not rq9['steps']
                  and fan['n_agent_layer'] >= 2)
            ex_bad = [(r['id'], s['step']) for r in fan['rq']
                      for s in r['steps']
                      if s.get('executed') and not s.get('ok')]
            check("扇出可执行步骤全真跑且全 ok(本机真实面)",
                  fan['n_executed'] >= 12 and not ex_bad, str(ex_bad))
            raw_ph = [s['argv'] for r in fan['rq'] for s in r['steps']
                      if s.get('executed')
                      and any('A_ID' in str(a) or 'VIEW-…' in str(a)
                              or 'B_ID' in str(a) for a in s['argv'])]
            check("占位符全部确定性替换(无 A_ID/VIEW-… 裸跑)",
                  not raw_ph, str(raw_ph))
            sub_steps = [s for r in fan['rq'] for s in r['steps']
                         if s.get('substitutions')]
            check("替身披露随行(substitutions 记录)",
                  sub_steps and all(s.get('substitutions') for s in sub_steps)
                  and any('VIEW-' in str(s['argv']) or 'VIEW-2026' in str(
                      s['argv']) for s in sub_steps), f"n={len(sub_steps)}")
            mdf = open(os.path.join(repf['report_dir'], 'report.md'),
                       encoding='utf-8').read()
            check("report.md 十问扇出台账+替身规则披露",
                  '## 十问扇出台账' in mdf and '替身规则' in mdf)
            repf2 = ro.run_research("10年期美债收益率 和 SPX 走势对比",
                                    root=ROOT,
                                    out_dir=os.path.join(tmp, 'fan2'),
                                    fanout=True)
            seq1 = [(r['id'], [s['step'] for s in r['steps']])
                    for r in fan['rq']]
            seq2 = [(r['id'], [s['step'] for s in r['steps']])
                    for r in repf2['fanout']['rq']]
            check("扇出确定性: 两跑十问步骤序列一致",
                  seq1 == seq2)
            p2 = subprocess.run(
                [sys.executable, 'ia_cli.py', 'research-run',
                 '--question', '10年期美债收益率 和 SPX 走势对比',
                 '--fanout', '--out-dir', os.path.join(tmp, 'cli_fan')],
                capture_output=True, text=True, timeout=600, cwd=ROOT)
            envf = json.loads(p2.stdout) if p2.stdout.strip().startswith('{') \
                else {}
            check("ia_cli --fanout 信封带扇出摘要(n_rq/n_executed/n_agent)",
                  envf.get('ok') is True
                  and envf.get('data', {}).get('fanout', {}).get('requested')
                  is True
                  and envf['data']['fanout']['n_rq'] == 10)

            # [4] 四层区分
            section("4 四层区分(零模型诚实面)")
            l3 = rep['layers']['L3_AI推断层']
            l4 = rep['layers']['L4_条件情景层']
            check("L3 produced=False+归属注记",
                  l3['produced'] is False and 'Agent' in l3['note'])
            check("L4 produced=False+不冒充预测注记",
                  l4['produced'] is False and '不冒充预测' in l4['note'])
            md = open(os.path.join(rep['report_dir'], 'report.md'),
                      encoding='utf-8').read()
            check("report.md 四层标题齐备",
                  all(t in md for t in
                      ('L1 事实层', 'L2 机构观点层', 'L3 AI推断层', 'L4 条件情景层')))

            # [5] 逐数证据索引
            section("5 逐数证据索引")
            l1_rows = rep['layers']['L1_事实层']['rows']
            l2_rows = (rep['layers']['L2_机构观点层']['views'].get('rows') or [])
            check("L1 每行带 snapshot_fact 来源",
                  all(r['source']['kind'] == 'snapshot_fact' and r['source']['id']
                      for r in l1_rows))
            check("L2 每行带 VP-sidecar 来源",
                  all(r['source']['kind'] == 'vp_sidecar' and r['source']['id']
                      for r in l2_rows) and len(l2_rows) > 0)
            check("evidence_index 计数=L1+L2 行数",
                  len(rep['evidence_index']) == len(l1_rows) + len(l2_rows))
            sc = next(s for s in rep['steps'] if s['step'] == 'S10_selfcheck')
            check("S10 自检零缺来源行",
                  sc['selfcheck']['ok'] and sc['selfcheck']['n_rows_missing_ref'] == 0)

            # [6] 诚实面
            section("6 诚实面")
            qa = next(s for s in rep['steps'] if s['step'] == 'S8_grounded_qa')
            qa_env = qa.get('envelope') or {}
            check("S8 进程层 ok 与语义层分开记录",
                  qa.get('ok') is True and 'semantic_ok' in qa,
                  f"ok={qa.get('ok')} semantic={qa.get('semantic_ok')}")
            check("S8 信封原样留档(status 在场)",
                  'status' in ((qa_env.get('data') or {})))
            s11 = next(s for s in rep['steps'] if s['step'] == 'S11_archive')
            check("S11 落档默认关+注记",
                  s11['archive_requested'] is False and '默认关' in (s11['note'] or ''))

            # [7] C 契约不动
            section("7 C 契约不动(VP sidecar 逐字节不变)")
            after = vp_dir_hash()
            check("VP 目录哈希前后一致", before == after and before is not None)

            # [8] 确定性
            section("8 确定性(同问题两跑)")
            rep2 = ro.run_research("10年期美债收益率 和 SPX 走势对比",
                                   root=ROOT, out_dir=tmp)

            def fingerprint(r):
                return json.dumps(
                    [[s['step'], s.get('ok'), s.get('executed')] for s in r['steps']],
                    ensure_ascii=False) + json.dumps(
                    {k: {'available': v.get('available'),
                         'n_rows': len(v.get('rows')
                                       or (v.get('views') or {}).get('rows') or [])}
                     for k, v in r['layers'].items()}, ensure_ascii=False)
            check("步骤序列+层摘要指纹一致(时间戳除外)",
                  fingerprint(rep) == fingerprint(rep2))

            # 真实 CLI 面: ia_cli research-run 子进程信封
            section("2b 真实子进程信封")
            p = subprocess.run(
                [sys.executable, os.path.join(ROOT, 'ia_cli.py'),
                 'research-run', '--question', 'SPX 最新值',
                 '--out-dir', os.path.join(tmp, 'cli')],
                capture_output=True, text=True, timeout=600, cwd=ROOT)
            env = json.loads(p.stdout) if p.stdout.strip().startswith('{') else {}
            check("research-run 信封 ok+report_dir+layers_summary",
                  env.get('ok') is True and env.get('data', {}).get('report_dir')
                  and 'L3_produced' in env.get('data', {}).get('layers_summary', {}))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    # 零映射路径(不依赖快照细节,但走真实管线;无快照则 S3 起如实降级)
    section("6b 零映射诚实降级")
    tmp2 = tempfile.mkdtemp(prefix='rd_r2_rr0_')
    try:
        rep0 = ro.run_research("美联储下次会议会降息吗",
                               root=ROOT, out_dir=tmp2)
        s5 = next(s for s in rep0['steps'] if s['step'] == 'S5_compare')
        check("零命中: S5 如实跳过(executed=False+原因)",
              s5.get('executed') is False and s5.get('skipped_reason'))
        check("零命中: L1 不倾倒全量事实(rows=[])",
              rep0['layers']['L1_事实层']['rows'] == [])
        ent0 = rep0['steps'][0]['deterministic_face']
        check("零命中注记进入 run notes",
              ent0['note'] is not None)
    finally:
        shutil.rmtree(tmp2, ignore_errors=True)

    print("═" * 64)
    print(f"结果: {PASS}通过 / {FAIL}失败 / {SKIP}按设计跳过")
    print("═" * 64)
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
