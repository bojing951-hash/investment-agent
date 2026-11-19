# -*- coding: utf-8 -*-
"""Audit-R21 任务3 — 真实工单三反例(正道不可交付/零归档增量)。

前置: /tmp/r21_accept 内已完成正式验收链(positive),run 目录=本脚本的
真实工单面。三反例均在「只动指令指定单一字段/面、校验字段原样」的
前提下构造,逐例走正式 attach+report+archive 入口,断言:
  ① ex_post.3m 正文 SPX −6.27%→+99.00%(校验字段原样)→ CONTRADICTED;
  ② 美国正文观测月→2030-07(anchor_echo 原样)→ CONTRADICTED;
  ③ JP 增长仅保留最新季度(两历史锚如实空,无日历实录依据)→
     blocked=map_anchor_coverage_insufficient+归档拒绝,增量=0。
用法: python3 /tmp/r21_negatives_harness.py <engine_root> <run_dir>
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/r21_accept'
RD_IN = sys.argv[2]
assert os.path.isfile(os.path.join(RD_IN, 'report.json')), RD_IN
assert os.path.isfile(os.path.join(RD_IN, 'agent_judgment.json'))
ARC = os.path.join(ROOT, 'research_archive')
TMPG = tempfile.mkdtemp(prefix='r21neg_')
RESULTS = []


def check(name, ok, detail=''):
    RESULTS.append((name, bool(ok)))
    print(('  ✅ ' if ok else ' ❌ ') + name + (f' — {str(detail)[:200]}' if detail else ''), flush=True)


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


n0 = n_archive()
print(f'归档基线 n={n0}')

# ── 反例①: 只改 2022-06 类比 ex_post.3m 正文(SPX −6.27%→+99.00%) ──
jd = json.load(open(os.path.join(RD_IN, 'agent_judgment.json'),
                    encoding='utf-8'))
hit = [h for h in jd['reader_map']['history_periods']
       if str(h.get('anchor_ym')) == '2022-06']
assert hit, 'judgment 无 2022-06 类比段'
h0 = hit[0]
old_txt = str(h0['ex_post']['3m'])
m_spx = re.search(r'SPX\s*([−-]\d+(?:\.\d+)?)%', old_txt)
assert m_spx, old_txt
orig_spx = m_spx.group(1)
assert abs(float(orig_spx.replace('−', '-')) - 99.0) > 1, orig_spx
h0['ex_post']['3m'] = old_txt.replace(
    f'SPX {orig_spx}%', 'SPX +99.00%')
p1 = os.path.join(TMPG, 'neg1_judgment.json')
json.dump(jd, open(p1, 'w', encoding='utf-8'), ensure_ascii=False)
rd1 = fresh_rd('neg1')
rc1, d1 = cli('attach', rd1, judgment=p1)
cv1 = ((json.load(open(os.path.join(rd1, 'report.json'), encoding='utf-8'))
        .get('agent_judgment') or {}).get('contract_verification') or {})
bad1 = [v for v in ((cv1.get('verdicts') or []) + (cv1.get('map_checks') or []))
        if v.get('status') not in ('VERIFIED', 'INSUFFICIENT_EVIDENCE')]
check('① attach 拒绝(attached=false+契约 CONTRADICTED)',
      not (d1.get('data') or {}).get('attached')
      and cv1.get('verdict') == 'CONTRADICTED' and bad1,
      f"verdict={cv1.get('verdict')} 首违={bad1[0].get('note', '')[:120] if bad1 else ''}")
rc1r, d1r = cli('report', rd1)
check('① report 不可交付', rc1r != 0
      and not (d1r.get('data') or {}).get('deliverable'))
a1 = os.path.join(TMPG, 'arc_neg1')
rc1a, _ = cli('archive', rd1, arc=a1)
check('① 归档拒绝+零增量', rc1a != 0 and n_archive() == n0
      and (not os.path.isdir(a1) or not any(os.scandir(a1))))

# ── 反例②: 只把美国正文观测月改成 2030-07(anchor_echo 原样) ──
jd2 = json.load(open(os.path.join(RD_IN, 'agent_judgment.json'),
                     encoding='utf-8'))
rg = [r for r in jd2['reader_map']['regions'] if r.get('region') == 'US'][0]
months = re.findall(r'\d{4}-\d{2}', str(rg.get('from_to')))
assert months, rg.get('from_to')
rg['from_to'] = str(rg['from_to']).replace(months[0], '2030-07', 1)
p2 = os.path.join(TMPG, 'neg2_judgment.json')
json.dump(jd2, open(p2, 'w', encoding='utf-8'), ensure_ascii=False)
rd2 = fresh_rd('neg2')
rc2, d2 = cli('attach', rd2, judgment=p2)
cv2 = ((json.load(open(os.path.join(rd2, 'report.json'), encoding='utf-8'))
        .get('agent_judgment') or {}).get('contract_verification') or {})
check('② attach 拒绝(attached=false+契约拦截)', rc2 == 0
      and not (d2.get('data') or {}).get('attached')
      and cv2.get('verdict') == 'CONTRADICTED',
      f"verdict={cv2.get('verdict')}")
rc2r, d2r = cli('report', rd2)
check('② report 不可交付(阻塞即退出非零,fail-closed)',
      not (d2r.get('data') or {}).get('deliverable'),
      f"rc={rc2r} deliverable={(d2r.get('data') or {}).get('deliverable')} "
      f"blocked={(d2r.get('data') or {}).get('blocked_class')}")
a2 = os.path.join(TMPG, 'arc_neg2')
rc2a, _ = cli('archive', rd2, arc=a2)
check('② 归档拒绝+零增量', rc2a != 0 and n_archive() == n0)

# ── 反例③: JP 增长仅保留最新季度(两历史时点如实空) ──
rd3 = fresh_rd('neg3')
rp3 = os.path.join(rd3, 'report.json')
rep = json.load(open(rp3, encoding='utf-8'))
cells = ((rep.get('research_plan') or {}).get('point_values')
         or {}).get('cells') or []
jp = [c for c in cells if c.get('region') == 'JP'
      and c.get('dimension') == 'growth']
assert jp, 'report 无 JP growth 格'
for c in jp:
    for lbl in ('12个月前', '3个月前'):
        a = (c.get('anchors') or {}).get(lbl)
        if a is not None:
            # 如实留空: 非日历实录证实的缺席(无 calendar_blocked_observation)
            c['anchors'][lbl] = {
                'status': 'no_series', 'as_of': a.get('as_of'),
                'note': '序列仅存最新季度(合成反例③: 历史时点如实留空)'}
json.dump(rep, open(rp3, 'w', encoding='utf-8'), ensure_ascii=False)
rc3, d3 = cli('attach', rd3)
b3 = (d3.get('data') or {}).get('blocked') or ''
rc3r, d3r = cli('report', rd3)
b3r = (d3r.get('data') or {}).get('blocked_class')
a3 = os.path.join(TMPG, 'arc_neg3')
rc3a, d3a = cli('archive', rd3, arc=a3)
b3a = json.dumps((d3a.get('data') or {}).get('blocked') or '', ensure_ascii=False)
check('③ 锚覆盖不足阻断(map_anchor_coverage_insufficient)',
      'map_anchor_coverage_insufficient' in (str(b3) + str(b3r) + b3a),
      f'{b3}|{b3r}|{b3a[:120]}')
check('③ 归档拒绝+零增量', rc3a != 0 and n_archive() == n0)

n_pass = sum(1 for _n, ok in RESULTS if ok)
print(f'\nAudit-R21 真实工单三反例: {n_pass}/{len(RESULTS)} PASS'
      f'(归档增量={n_archive() - n0})')
sys.exit(0 if n_pass == len(RESULTS) else 1)
