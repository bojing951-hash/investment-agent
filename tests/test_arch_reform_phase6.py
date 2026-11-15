#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""阶段六: Real-World Acceptance Suite(真实面验收;章程§八)。

A. 金融数值正确性 — R24 真实报告面(55事实身份/单位/时间/变化率/阈值)
   + 历史误判案例复位(Gate B 五缺陷 45 判/迁移门 T8R 31 判)。
B. 研究结论正确性 — 真实证据 vs 错误解释(V4 两 MAJOR)/错误归因/
   机构观点标签纪律/前视偏差守卫/反例集(V5 21 注入)。
C. 一键研究能力 — C-det: R24 真实运行结构面(15步/L3L4 declared/
   零未映射);C-real: 2026-11-15 WALCL×SOFR×DXY 未优化面真跑已毕
   (用户令执行,六判据全过;真跑档=dev 树,本套件 C5 机核其结构/数值/
   零未映射,工件不在场面显式 SKIP=CI 层区分)。
D. 研发系统可靠性 — 八项模拟逐一可复核证据。

判定: 全 PASS 方绿;外部工件(真跑档/V5 集/round.sh)不在场=显式 SKIP
不计判——「不能以离线测试代替真实验收」的诚实形态(CI 面=合成层)。
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

from research_contract import judgment_contract as jc       # noqa: E402

FIX = os.path.join(HERE, 'fixtures', 'v4')
FACE = json.load(open(os.path.join(FIX, 'evidence_face.json')))
DEV_RUN = ('/Users/cast/investment-agent-dev/output/research_runs/'
           '20261113T053316Z_美国高收益债利差_HY_OAS_与_SPX_股价_VIX_'
           '波动率_CURVE_2')
RESULTS = []


def skip(name, why):
    """外部工件不在场(CI 干净克隆)→ 显式 SKIP 不计判(六层区分: 本机
    真实数据层 vs CI 合成层;SKIP≠PASS,不以离线面冒充真实验收)。"""
    print(f"  ⏭️ {name}  [{why}]")


def check(name, ok, detail=''):
    RESULTS.append((name, bool(ok), detail))
    print(f"  {'✅' if ok else '❌'} {name}" + (f"  [{detail}]"
                                                if detail and not ok else ''))


def sh(cmd, cwd=ROOT, timeout=300):
    p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True,
                       text=True, timeout=timeout)
    return p.returncode, p.stdout + p.stderr


# ═══ A. 金融数值正确性 ═══
print("== A. 金融数值正确性(真实报告面) ==")
facts = {f['metric_id']: f for f in FACE['facts']}
check('A1 事实四要素零缺(value/unit/observation_date/as_of 前提)',
      all(f.get('value') is not None and f.get('unit')
          and f.get('observation_date') for f in FACE['facts'])
      and len(FACE['facts']) == 55, f"n={len(FACE['facts'])}")
units = {f['unit'] for f in FACE['facts']}
reg = json.load(open(os.path.join(ROOT, 'config', 'metric_registry.json')))
reg_items = reg.get('metrics') or reg.get('entries') or reg
reg_units = ({v.get('unit') for v in reg_items.values()
              if isinstance(v, dict)} if isinstance(reg_items, dict)
             else {m.get('unit') for m in reg_items})
check('A2 单位族与注册表一致(22 词表权威源)',
      units <= reg_units, str(sorted(units - reg_units)))
check('A3 恒等式复算 REAL_10Y = UST_10Y − BEI_10Y(真实面值)',
      abs(facts['REAL_10Y']['value'] -
          (facts['UST_10Y']['value'] - facts['BEI_10Y']['value'])) < 1e-9,
      f"{facts['REAL_10Y']['value']} vs "
      f"{facts['UST_10Y']['value']}-{facts['BEI_10Y']['value']}")
w = facts['HY_OAS']['derived']['week']
check('A4 周变化率复算 3.34−3.42=−0.08(basis 随档)',
      abs((facts['HY_OAS']['value'] - w['basis_value'])
          - w['pp_change']) < 1e-9 and w['basis_date'] == '2026-11-06',
      f"{w}")
rc, out = sh('python3 scripts/thresholds_gate.py')
check('A5 阈值三方对账门 G1-G4 全绿(69 键 SIGNED)',
      rc == 0 and '全绿' in out, out[-120:].strip())
rc, out = sh('python3 tests/test_rd_r27_gateb_extractor.py')
check('A6 历史误判案例①Gate B 提取器五缺陷复位(真实报告 0 数值错)',
      rc == 0 and '45 PASS' in out, out.strip().splitlines()[-1])
rc, out = sh('python3 tests/test_arch_reform_t8r.py')
# 启封件在本机(操作者面)→31 判全数;CI 干净克隆→封存段显式 SKIP=30 判
# (六层区分;期望随工件在场性取值,不降门: 两面都必须零 FAIL 才 rc=0)
T8R_QA = '/Users/cast/agent-loop/ARCH-REFORM/QA/heldout-sealed'
t8r_expect = '31 PASS' if os.path.isdir(T8R_QA) else '30 PASS'
check('A7 历史误判案例②迁移门 T8R(含 V1/V2 真实历史故障复位)',
      rc == 0 and t8r_expect in out, out.strip().splitlines()[-1])

# ═══ B. 研究结论正确性 ═══
print("== B. 研究结论正确性(真实证据 vs 错误解释) ==")
JR = json.load(open(os.path.join(FIX, 'judgment_revised.json')))
JP = json.load(open(os.path.join(FIX, 'judgment_pre_audit.json')))
res_p = jc.verify_judgment(JP, None, face=FACE)
res_r = jc.verify_judgment(JR, None, face=FACE)
maj_band = next((c for c in res_p['verdicts']
                 if c['family'] == 'stat_band_claim'
                 and c['status'] == 'CONTRADICTED'), None)
maj_narr = next((c for c in res_p['verdicts']
                 if c['family'] == 'narrative_direction'
                 and c['status'] == 'CONTRADICTED'), None)
check('B1 真实错误解释被拦: 「处年内低位」vs 真实序列 95.6 百分位',
      maj_band is not None and abs(maj_band['expected'] - 95.6) < 0.05,
      str(maj_band and maj_band.get('expected')))
check('B2 真实错误叙事被拦: 「倒挂」vs 序列 2024-09-05 后无负值',
      maj_narr is not None, str(maj_narr and maj_narr.get('note')))
check('B3 修正后真实判定档全绿(错误改对=闭环非只拦)',
      res_r['verdict'] == 'VERIFIED', res_r['verdict'])
opp = [s for s in res_p['six_checks'] + res_r['six_checks']
       if s['check'] == 'opposing']
check('B4 竞争解释方向核(现时式 vs 面内周变;条件式跳过)',
      len(res_r['six_checks']) == 12 and
      all(s['status'] == 'VERIFIED' for s in opp), str(len(opp)))
views = FACE['views']
LABELS = {'SUPPORTING', 'CONTRADICTING', 'MIXED', 'NEUTRAL',
          'INSUFFICIENT_EVIDENCE', 'PARTIALLY_SUPPORTED'}
idx = {e['ref']: e for e in FACE['evidence_index']}
vp_insuff_cited = []
for c in JR['l3']['contradictions']:
    txt = (c.get('statement') or '') + (c.get('basis') or '')
    for r in c.get('evidence_refs') or []:
        e = idx.get(r) or {}
        if e.get('kind') == 'vp_sidecar':
            v = next((x for x in views
                      if x.get('view_id') == (e.get('ref') or '')
                      .replace('VP-', '')), None)
            if v and v.get('view_label') == 'INSUFFICIENT_EVIDENCE':
                vp_insuff_cited.append(bool(jc._INST_CITE_RE.search(txt)))
check('B5 机构观点标签纪律(17 档标签合法;被引 INSUFFICIENT 档均归因式)',
      len(views) == 17 and
      all(v.get('view_label') in LABELS for v in views) and
      all(vp_insuff_cited) and len(vp_insuff_cited) >= 1,
      f"insuff_cited={len(vp_insuff_cited)}")
fals = [s for s in res_r['six_checks'] if s['check'] == 'falsifiable']
check('B6 前视偏差守卫(L4 证伪条件=可观测指标+数字阈值+算术自洽;'
      '前瞻口径不核=EC-4c 常备)', all(s['status'] == 'VERIFIED'
                                       for s in fals), str(len(fals)))
V5Q = '/Users/cast/agent-loop/ARCH-REFORM/QA/V5-INJECTIONS.json'
if not os.path.isfile(V5Q):
    skip('B7', 'V5 反例集不在本机(CI 面)——注入矩阵=机器外工件,登记在 PHASE3-LOG T7 节')
else:
    rc, out = sh('python3 tests/run_matrix_dir.py ' + V5Q)
    check('B7 真实衍生反例集 21/21 全拦(漏报=0)',
          rc == 0 and '21/21' in out and 'unmapped=0' in out,
          out.strip().splitlines()[-1])

# ═══ C. 一键研究能力 ═══
print("== C. 一键研究(det=R24 结构面 + real=2026-11-15 WALCL×SOFR×DXY 真跑) ==")

if not os.path.isdir(DEV_RUN):
    skip('C1-det/C2-det/C3-det', 'R24 运行档不在本机(CI 面)—— fixtures/v4 为其锚定副本')
else:
    rep = json.load(open(os.path.join(DEV_RUN, 'report.json')))
    steps = rep.get('steps') or []
    l3 = (rep.get('layers') or {}).get('L3_AI推断层', {})
    check('C1-det 真实运行 15 步 run_ok=True',
          rep.get('run_ok') is True and len(steps) == 15,
          f"steps={len(steps)} run_ok={rep.get('run_ok')}")
    check('C2-det 真实 attach 记录在场(判定层落位=验证后;审计前拦截见 '
          'PHASE4 套件 V4-3)',
          l3.get('produced') is True and
          (rep.get('agent_judgment') or {}).get('attached') is True and
          bool((rep.get('agent_judgment') or {}).get('validation')),
          'R24 报告=agent 判定+修订闭环真实验收面')
    unmapped_probe = json.load(open(os.path.join(
        DEV_RUN, 'judgment.json')))
    res_j = jc.verify_judgment(unmapped_probe, None, face=FACE)
    check('C3-det 真实判定档零未映射(unresolved_unbound=0)',
          res_j['stats']['unbound'] == 0, str(res_j['stats']))

CREAL = ('/Users/cast/investment-agent-dev/output/research_runs/'
         '20261115T014829Z_美元流动性与短端利率_WALCL_缩表进程_SOFR_走势'
         '与_DXY_的组合状态')
check('C4-real 准备件入库(跑台脚本+验收判据=仓内持久权威,/tmp 为易失副本)',
      os.path.isfile(os.path.join(
          ROOT, 'docs/autonomous-rd/phase6c/run_phase6c_real.sh'))
      and os.path.isfile(os.path.join(
          ROOT, 'docs/autonomous-rd/phase6c/PHASE6C-REAL-ACCEPTANCE.md')),
      'docs/autonomous-rd/phase6c/')
if not os.path.isdir(CREAL):
    skip('C5-real', '2026-11-15 真跑档不在本机(CI 面)——真跑记录=PHASE3-LOG 收口节')
else:
    from research_contract import claim_factory as _cf
    from research_contract import text_consistency as _tc
    rr = json.load(open(os.path.join(CREAL, 'report.json')))
    rs = rr.get('steps') or []
    l1r = ((rr.get('layers') or {}).get('L1_事实层') or {}).get('rows') or []
    ids = {r.get('metric_id'): r for r in l1r}
    check('C5a-real 真跑 15 步 run_ok + L3/L4 declared-not-produced(判据1/6)',
          rr.get('run_ok') is True and len(rs) == 15
          and (rr['layers']['L3_AI推断层']['produced'] is False)
          and (rr['layers']['L4_条件情景层']['produced'] is False),
          f"steps={len(rs)}")
    check('C5b-real 三元指标真实在场(判据2: value/unit/obs;WALCL WARN=周频滞后如实)',
          all(m in ids and ids[m].get('value') is not None and ids[m].get('unit')
              and ids[m].get('observation_date') for m in ('WALCL', 'SOFR', 'DXY'))
          and ids['WALCL'].get('quality_status') == 'WARN',
          str({m: ids.get(m, {}).get('observation_date') for m in ids}))
    fface = jc.build_face(rr)
    mdr = open(os.path.join(CREAL, 'report.md'), encoding='utf-8').read()
    sec = '【事实】' + mdr.split('### L1 事实层', 1)[1].split('###', 1)[0]
    rres = _tc.check_text(sec, snapshot=fface,
                          thresholds=_cf.load_thresholds())
    check('C5c-real 数值一致性+零未映射(判据3/4: 事实区 3 查全 VERIFIED,unbound=0)',
          rres['verdict'] == 'VERIFIED'
          and rres['stats']['contradicted'] == 0
          and len(rres['unbound']) == 0,
          json.dumps(rres['stats'], ensure_ascii=False))

# ═══ D. 研发系统可靠性(八项模拟,逐项可复核证据) ═══
print("== D. 研发系统可靠性 ==")
rc, out = sh('python3 scripts/rd_state_consistency.py --quiet')
check('D1 上下文丢失/会话恢复: 检查点块+RESUME 纪律(7/7;恢复套件 5/0)',
      rc == 0 and '7/7 PASS' in out, out.strip().splitlines()[-1])
rc, out = sh('python3 tests/test_rd_r20_recovery.py')
check('D2 检查点过期/悬空提交: 恢复验收五例(含 baseline 非祖先拒)',
      rc == 0 and '5 pass' in out, out.strip().splitlines()[-1])
rc, out = sh('git -C %s status --porcelain' % ROOT)
d3_left = [ln for ln in out.splitlines()
           if ln.strip() and 'test_arch_reform_phase6.py' not in ln]
check('D3 Git 状态变化: 整改树工作面净(除本套件自身)',
      rc == 0 and not d3_left, str(d3_left[:3]))
rc, out = sh('python3 tests/test_rd_r20_state_consistency.py')
check('D4 任务重复: 台账 ID 重复+已毕回流探针全咬住(15 判)',
      rc == 0 and '15 pass' in out, out.strip().splitlines()[-1])
corrupt = {'l3': {'contradictions': [{'id': 'X', 'statement': None,
                                      'basis': None}]},
           'l4': {'scenarios': []}}
try:
    res_c = jc.verify_judgment(corrupt, None, face=FACE)
    d5ok = res_c['verdict'] in ('VERIFIED', 'NOT_VERIFIED', 'CONTRADICTED')
    d5note = res_c['verdict']
except Exception as e:
    d5ok, d5note = False, repr(e)
check('D5 开发失败(输入残缺): 契约验证降级不崩溃(异常=如实降级路径)',
      d5ok, d5note)
exit_ok = True
for t in ('test_arch_reform_phase4', 'test_arch_reform_t8r',
          'test_rd_r20_state_consistency'):
    src = open(os.path.join(HERE, t + '.py')).read()
    if not re.search(r'sys\.exit\(0 if .+ else 1\)', src):
        exit_ok = False
check('D6 测试失败硬拦: 套件 exit 布线(红=退出码1=CI/门拒)',
      exit_ok, '三代表套件结构核')
ROUNDSH = '/Users/cast/agent-loop/headless/round.sh'
if not os.path.isfile(ROUNDSH):
    skip('D7', '引擎轮次脚本不在本仓(CI 面)——资源双上限=引擎树工件')
else:
    rc, out = sh('grep -c "MAX_BUDGET_USD=50\\|MAX_WALL_SEC=9000" ' + ROUNDSH)
    check('D7 资源限制: 轮次 $50/150min 双上限+看门狗在场(round.sh)',
          rc == 0 and out.strip() == '2', out.strip())
rc, out = sh('python3 tests/test_arch_reform_t8r.py | tail -1')
check('D8 证据可复核性: PHASE3-LOG 所引命令重放同结果(t8r 期望判数复现)',
      rc == 0 and t8r_expect in out, out.strip())

n_pass = sum(1 for _, ok, _ in RESULTS if ok)
print(f"\nPHASE6 判定: {n_pass} PASS / {len(RESULTS) - n_pass} FAIL"
      " (外部工件不在场项=显式 SKIP 不计判)")
sys.exit(0 if n_pass == len(RESULTS) else 1)
