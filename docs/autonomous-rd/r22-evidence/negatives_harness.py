# -*- coding: utf-8 -*-
"""Audit-R22 任务3 — 真实工单三窜写+中文同义正例(正式入口逐例)。

前置: /tmp/r22 内已完成 R22 正式验收链(Seat-A),run 目录=本脚本的真实
工单面。指令指定三窜写(只改正文,校验字段原样):
  ① 标普跌 5.28% 写成「标普500指数上涨99.00%」(中文面);
  ② 美债 +0.85pp 改成「上升0.35个百分点」(pp 容差 0.06 必拦);
  ③ 美国 GDP 的 2025Q2 改成 Q3(观测月串锚序,锚前不可见月不可引)。
正例: 含义相同的正确中文表述必须通过(attach VERIFIED 不误伤)。
每例走正式 attach(+report/archive 于反例)入口,断言反例=CONTRADICTED
+不可交付+归档拒绝零增量;正例=VERIFIED。
用法: python3 negatives_harness.py <engine_root> <run_dir>
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/r22'
RD_IN = sys.argv[2]
assert os.path.isfile(os.path.join(RD_IN, 'report.json')), RD_IN
assert os.path.isfile(os.path.join(RD_IN, 'agent_judgment.json'))
ARC = os.path.join(ROOT, 'research_archive')
TMPG = tempfile.mkdtemp(prefix='r22neg_')
RESULTS = []


def check(name, ok, detail=''):
    RESULTS.append((name, bool(ok)))
    print(('  ✅ ' if ok else ' ❌ ') + name
          + (f' — {str(detail)[:200]}' if detail else ''), flush=True)


def n_archive():
    return len([x for x in os.listdir(ARC) if x != '.gitkeep']) \
        if os.path.isdir(ARC) else 0


def fresh_rd(tag):
    d = os.path.join(TMPG, tag)
    shutil.copytree(RD_IN, d)
    return d


def cli(stage, rd, judgment=None, arc=None):
    cmd = [sys.executable, 'ia_cli.py', 'research-one', '--stage', stage,
           '--report-dir', rd, '--engine-root', ROOT]
    if judgment:
        cmd += ['--judgment', judgment]
    if arc:
        cmd += ['--archive-dir', arc]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                       timeout=600)
    try:
        data = json.loads(r.stdout)
    except Exception:
        data = {'raw': ((r.stdout or '') + (r.stderr or ''))[-400:]}
    return r.returncode, data


def load_jd():
    return json.load(open(os.path.join(RD_IN, 'agent_judgment.json'),
                          encoding='utf-8'))


def attach_cv(rd):
    rep = json.load(open(os.path.join(rd, 'report.json'), encoding='utf-8'))
    return rep, ((rep.get('agent_judgment') or {})
                 .get('contract_verification') or {})


def h22(jd):
    hit = [h for h in jd['reader_map']['history_periods']
           if str(h.get('anchor_ym')) == '2022-06']
    assert hit, 'judgment 无 2022-06 类比段'
    return hit[0]


n0 = n_archive()
print(f'归档基线 n={n0}')

# ── ① 标普跌 5.28% 写成「标普500指数上涨99.00%」(中文面) ──────────────
jd = load_jd()
h0 = h22(jd)
old_txt = str(h0['ex_post']['3m'])
m_spx = re.search(r'SPX\s*([−-]\d+(?:\.\d+)?)%', old_txt)
assert m_spx, old_txt
h0['ex_post']['3m'] = old_txt.replace(
    f"SPX {m_spx.group(1)}%", '标普500指数上涨99.00%', 1)
p1 = os.path.join(TMPG, 'neg1_judgment.json')
json.dump(jd, open(p1, 'w', encoding='utf-8'), ensure_ascii=False)
rd1 = fresh_rd('neg1')
rc1, d1 = cli('attach', rd1, judgment=p1)
rep1, cv1 = attach_cv(rd1)
bad1 = [v for v in (cv1.get('verdicts') or []) + (cv1.get('map_checks') or [])
        if v.get('status') not in ('VERIFIED', 'INSUFFICIENT_EVIDENCE')]
check('① attach 拒绝(attached=false+契约 CONTRADICTED)',
      not (d1.get('data') or {}).get('attached')
      and cv1.get('verdict') == 'CONTRADICTED' and bad1
      and any('中文面' in str(v.get('note')) for v in bad1),
      f"verdict={cv1.get('verdict')} 首违={str(bad1[0].get('note'))[:120] if bad1 else ''}")
rc1r, d1r = cli('report', rd1)
check('① report 不可交付', rc1r != 0
      and not (d1r.get('data') or {}).get('deliverable'))
a1 = os.path.join(TMPG, 'arc_neg1')
rc1a, _ = cli('archive', rd1, arc=a1)
check('① 归档拒绝+零增量', rc1a != 0 and n_archive() == n0
      and (not os.path.isdir(a1) or not any(os.scandir(a1))))

# ── ② 美债 +0.85pp 改成「上升0.35个百分点」(pp 容差 0.06) ────────────
jd2 = load_jd()
h0 = h22(jd2)
old_txt = str(h0['ex_post']['3m'])
m_ust = re.search(r'UST_10Y\s*\+?([0-9.]+)pp', old_txt)
assert m_ust, old_txt
h0['ex_post']['3m'] = old_txt.replace(
    f"UST_10Y +{m_ust.group(1)}pp", '美国十年期国债收益率上升0.35个百分点', 1)
p2 = os.path.join(TMPG, 'neg2_judgment.json')
json.dump(jd2, open(p2, 'w', encoding='utf-8'), ensure_ascii=False)
rd2 = fresh_rd('neg2')
rc2, d2 = cli('attach', rd2, judgment=p2)
rep2, cv2 = attach_cv(rd2)
bad2 = [v for v in (cv2.get('verdicts') or []) + (cv2.get('map_checks') or [])
        if v.get('status') not in ('VERIFIED', 'INSUFFICIENT_EVIDENCE')]
check('② attach 拒绝(pp 窜写 0.35 vs 引擎值,容差 0.06)',
      not (d2.get('data') or {}).get('attached')
      and cv2.get('verdict') == 'CONTRADICTED'
      and any('UST_10Y' in str(v.get('note')) for v in bad2),
      f"verdict={cv2.get('verdict')} 首违={str(bad2[0].get('note'))[:120] if bad2 else ''}")
rc2r, d2r = cli('report', rd2)
check('② report 不可交付(fail-closed)', rc2r != 0
      and not (d2r.get('data') or {}).get('deliverable'))
a2 = os.path.join(TMPG, 'arc_neg2')
rc2a, _ = cli('archive', rd2, arc=a2)
check('② 归档拒绝+零增量', rc2a != 0 and n_archive() == n0)

# ── ③ 美国 GDP 的 2025Q2 改成 Q3(观测月串锚序) ────────────────────────
jd3 = load_jd()
rg = [r for r in jd3['reader_map']['regions'] if r.get('region') == 'US'][0]
ft = str(rg.get('from_to'))
m_run = re.search(r'观测\s*(\d{4}-\d{2}(?:-\d{2})?(?:\s*→\s*'
                  r'\d{4}-\d{2}(?:-\d{2})?)+)', ft)
assert m_run, ft
run0 = m_run.group(1)
months0 = re.findall(r'\d{4}-\d{2}', run0)
assert months0, run0
# Q2(2025-04 观测)→Q3=2025-07: 序列在场但 12 个月前锚(2025-11-19)不可见
rg['from_to'] = ft.replace(months0[0], '2025-07', 1)
p3 = os.path.join(TMPG, 'neg3_judgment.json')
json.dump(jd3, open(p3, 'w', encoding='utf-8'), ensure_ascii=False)
rd3 = fresh_rd('neg3')
rc3, d3 = cli('attach', rd3, judgment=p3)
rep3, cv3 = attach_cv(rd3)
bad3 = [v for v in (cv3.get('verdicts') or []) + (cv3.get('map_checks') or [])
        if v.get('status') not in ('VERIFIED', 'INSUFFICIENT_EVIDENCE')]
check('③ attach 拒绝(观测串 2025-07 非锚观测保序子序列)',
      not (d3.get('data') or {}).get('attached')
      and cv3.get('verdict') == 'CONTRADICTED'
      and any('obs_run' in str(v.get('item'))
              or '保序子序列' in str(v.get('note')) for v in bad3),
      f"verdict={cv3.get('verdict')} 首违={str(bad3[0].get('note'))[:120] if bad3 else ''}")
rc3r, d3r = cli('report', rd3)
check('③ report 不可交付(fail-closed)', rc3r != 0
      and not (d3r.get('data') or {}).get('deliverable'))
a3 = os.path.join(TMPG, 'arc_neg3')
rc3a, _ = cli('archive', rd3, arc=a3)
check('③ 归档拒绝+零增量', rc3a != 0 and n_archive() == n0)

# ── ④ 正例: 含义相同的正确中文表述(必须通过) ─────────────────────────
jd4 = load_jd()
h0 = h22(jd4)
old_txt = str(h0['ex_post']['3m'])
m_spx = re.search(r'SPX\s*([−-]\d+(?:\.\d+)?)%', old_txt)
m_ust = re.search(r'UST_10Y\s*\+?([0-9.]+)pp', old_txt)
assert m_spx and m_ust, old_txt
new_txt = old_txt
new_txt = new_txt.replace(
    f"SPX {m_spx.group(1)}%", f"标普500指数下跌{m_spx.group(1).lstrip('−-')}%", 1)
new_txt = new_txt.replace(
    f"UST_10Y +{m_ust.group(1)}pp",
    f"美国十年期国债收益率上升{m_ust.group(1)}个百分点", 1)
h0['ex_post']['3m'] = new_txt
p4 = os.path.join(TMPG, 'pos1_judgment.json')
json.dump(jd4, open(p4, 'w', encoding='utf-8'), ensure_ascii=False)
rd4 = fresh_rd('pos1')
rc4, d4 = cli('attach', rd4, judgment=p4)
rep4, cv4 = attach_cv(rd4)
check('④ 正例: 中文同义表述 → attach VERIFIED(同义改写不误伤)',
      rc4 == 0 and (d4.get('data') or {}).get('attached')
      and cv4.get('verdict') == 'VERIFIED',
      f"verdict={cv4.get('verdict')}")
check('④ 正例: 归档零增量(正例不落档,正式运行本身即正例归档)',
      n_archive() == n0)

n_fail = sum(1 for _n, ok in RESULTS if not ok)
print(f'\nR22 反例+正例: {len(RESULTS) - n_fail} PASS / {n_fail} FAIL '
      f'(归档增量={n_archive() - n0})')
sys.exit(1 if n_fail else 0)
