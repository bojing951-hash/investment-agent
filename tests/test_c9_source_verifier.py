#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Charter9 P0-3 来源验证引擎测试(source_verifier+装载核验+URL档位)。

锁定面(audit/C9_D_AUDIT_AND_DESIGN §3 × C席 audit/C9_P0_REPRODUCE P0-3):
① 四状态机 VERIFIED/PARTIAL/MISSING/CONFLICTED(C席实测: 伪号
   QB-20990101-999 曾零拦截装载→MISSING 必须可逮);
② 包含核验: 引用 r/n 在归档 answer_text 在场(全角负号规范化);
③ 复算对账: 与 ia_cli compare 同算法重算边 r(C席 3/3 实证→引擎接线,
   本地真实数据 25/25 边 r✓,含 lag 双向命中);
④ 归档缺席(干净clone)如实降级 performed=False,禁静默通过也禁 CI 崩;
⑤ transmission_edges 装载面: 悬空 qb_source raise(硬闸,不入页);
⑥ views lint --verify-urls: 默认关(零网络),显式档位只披露不隔离。
全合成 fixture(归档=公开写入API合成,快照 series_store=受控序列,
指标=注册表真实ID+合成序列——CI 干净 clone 可跑,零真实 data/ 依赖)。
"""
import copy
import glob
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


import research_archive as ra            # noqa: E402
import research_provenance as rp         # noqa: E402
import workbench_data as wd              # noqa: E402
import source_verifier as sv             # noqa: E402
import fixt_c8_archive as fixt           # noqa: E402

Q30 = 'QB-20261110-030'                  # 有 sidecar(VERIFIED 面)
Q31 = 'QB-20261110-031'                  # 仅记录无 sidecar(PARTIAL 面)
AT30 = '| 指标对 | r | n |\n| A×B | +1.0000 | 29 |\n(合成fixture)'


def build_syn_archive(archive_dir):
    """合成归档: Q30(记录+sidecar)/Q31(仅记录)——全公开写入API。"""
    def mk_ir(qid, q):
        ir = copy.deepcopy(fixt.FIX_IR_BASE)
        ir['query_id'] = qid
        ir['question_text'] = q
        return ir
    for qid, q in ((Q30, '合成: A×B 全窗相关'), (Q31, '合成: 无sidecar记录')):
        st, _ = ra.append_query_record(
            mk_ir(qid, q), snapshot=copy.deepcopy(fixt.FIX_SNAP),
            archive_dir=archive_dir, archived_at='2026-11-11T09:00:00+00:00')
        assert st == ra.STATUS_WRITTEN, (qid, st)
    coll = ra._collection_dir(archive_dir)
    full = {
        'record_type': 'research_full_v1', 'query_id': Q30,
        'question_text': '合成: A×B 全窗相关',
        'created_at': fixt.FIX_IR_BASE['created_at'],
        'research_as_of': '2026-11-11T18:00:00+08:00',
        'snapshot_id': fixt.FIX_SNAP['snapshot_id'],
        'digest_snapshot': rp.digest_snapshot(fixt.FIX_SNAP),
        'status': 'answered', 'answer_text': AT30, 'values': None,
        'unresolved': None, 'model': None, 'warnings': [], 'violations': [],
        'user_note': None, 'follow_up_of': None,
        'saved_at': '2026-11-11T19:00:00+00:00',
    }
    st, _ = ra.write_research_full(coll, full)
    assert st == ra.STATUS_WRITTEN, st
    return archive_dir


TD = tempfile.mkdtemp(prefix='c9sv_')
ARCH = build_syn_archive(os.path.join(TD, 'arch'))

print("═" * 60)
print("[1] 四状态机: verify_qb_source")
print("═" * 60)
r = sv.verify_qb_source(Q30, ARCH)
check("在册+sidecar → VERIFIED", r['state'] == 'VERIFIED', str(r))
r = sv.verify_qb_source(Q31, ARCH)
check("在册无 sidecar → PARTIAL", r['state'] == 'PARTIAL', str(r))
r = sv.verify_qb_source('QB-20990101-999', ARCH)
check("伪号不在册 → MISSING(C席实测场景)", r['state'] == 'MISSING', str(r))
r = sv.verify_qb_source('SYNTH:QB-20261110-001', ARCH)
check("SYNTH: 前缀→跳过核验+显式披露",
      r['state'] == 'VERIFIED' and 'SYNTH' in r['detail'], str(r))
r = sv.verify_qb_source(Q30, os.path.join(TD, 'no_such_archive'))
check("归档目录缺席 → PARTIAL(未核验≠通过,如实降级)",
      r['state'] == 'PARTIAL' and '不存在' in r['detail'], str(r))
check("状态枚举恰四态", set(sv.STATES) == {'VERIFIED', 'PARTIAL',
                                          'MISSING', 'CONFLICTED'})

print("═" * 60)
print("[2] 包含核验: 引用数值 vs 归档原文")
print("═" * 60)
c = sv.containment_check('| VIX×SPX | −0.7138 … n=2495', -0.7138, 2495)
check("全角负号规范化后命中(r/n 双 found)",
      c['performed'] and c['r_found'] and c['n_found'], str(c))
c = sv.containment_check('r=+0.8278', 0.8278, 100)
check("带符号书写命中,无关 n 如实 not found",
      c['r_found'] and not c['n_found'], str(c))
c = sv.containment_check('r=+1.0000 n=29', 0.5, 29)
check("r 不在原文 → r_found=False(矛盾信号)",
      not c['r_found'] and c['n_found'], str(c))
c = sv.containment_check(None, 0.1, 1)
check("sidecar 缺失 → performed=False", c['performed'] is False, str(c))
c = sv.containment_check('值 0.5000 在场', 0.5, 3)
check("书写变体(4位小数)命中", c['r_found'], str(c))

print("═" * 60)
print("[3] 边档全量: verify_edges 状态分布")
print("═" * 60)


def edges_doc(rows):
    return {'schema_version': '1.0', 'edges': rows,
            'mechanism_findings': [], 'evidence_grading': {},
            'category_semantics': {}}


def mk_edge(eid, qb, r, n, win='全窗', a='UST_10Y', b='UST_2Y'):
    return {'edge_id': eid, 'from': a, 'to': b, 'channel_label': 'syn',
            'category': 'strong', 'r': r, 'n': n, 'window': win,
            'evidence_level': 'E1', 'qb_source': qb, 'note': '合成'}


EP = os.path.join(TD, 'edges.json')
with open(EP, 'w', encoding='utf-8') as f:
    json.dump(edges_doc([
        mk_edge('E-OK', Q30, 1.0, 29),
        mk_edge('E-CONFLICT', Q30, 0.7, 29),
        mk_edge('E-MISSING', 'QB-20990101-999', 0.1, 5),
        mk_edge('E-PARTIAL', Q31, 0.4, 8),
    ]), f, ensure_ascii=False)
rep = sv.verify_edges(archive_dir=ARCH, edges_path=EP)
by = {x['id']: x for x in rep['results']}
check("r/n 双在场 → VERIFIED", by['E-OK']['state'] == 'VERIFIED',
      str(by['E-OK']))
check("r 不在原文 → CONFLICTED(引用与归档矛盾)",
      by['E-CONFLICT']['state'] == 'CONFLICTED', str(by['E-CONFLICT']))
check("伪号 → MISSING", by['E-MISSING']['state'] == 'MISSING')
check("无 sidecar → PARTIAL", by['E-PARTIAL']['state'] == 'PARTIAL')
check("汇总四态计数", rep['summary'] == {'VERIFIED': 1, 'PARTIAL': 1,
                                        'MISSING': 1, 'CONFLICTED': 1},
      str(rep['summary']))
rep2 = sv.verify_edges(archive_dir=os.path.join(TD, 'absent'),
                       edges_path=EP)
check("归档缺席 → existence performed=False(禁静默通过)",
      rep2['existence_check']['performed'] is False
      and rep2['archive_present'] is False
      and rep2['existence_check']['note'], str(rep2['existence_check']))

print("═" * 60)
print("[4] 复算对账: 同算法重算 r(C席 3/3 实证的引擎接线)")
print("═" * 60)
# 合成快照 series_store(注册表真实ID: UST_10Y/UST_2Y=rate·daily,
# FED_FUNDS=rate·monthly)——受控序列,r 解析可知:
# a 变化=ca[i],b=2a → 变化同向共线 → r=+1.0000(n=变化对数)。
ca = [0.10, -0.05, 0.25, -0.10, 0.30, -0.15, 0.20, 0.05, -0.20, 0.10,
      0.15, -0.05, 0.20, -0.10, 0.05, 0.25, -0.15, 0.10, 0.05, -0.05,
      0.20, -0.10, 0.15, 0.05, -0.20, 0.10, 0.30, -0.15, 0.25, 0.10]


def _cum(deltas, v0=2.0):
    out, v = [], v0
    for d in deltas:
        v += d
        out.append(round(v, 6))
    return out


day_dates = [f'2026-01-{i:02d}' for i in range(1, 31)]
SYN_SNAP = {'snapshot_id': 'research_snapshot_20260130_syn',
            'target_date': '20260130',
            'series_store': {
                'UST_10Y': {'dates': day_dates, 'values': _cum(ca)},
                'UST_2Y': {'dates': day_dates,
                           'values': [round(2 * v, 6) for v in _cum(ca)]},
            }}
REG = wd.load_registry(ROOT)
e = mk_edge('E-RC', Q30, 1.0, 29)
rc = sv.recompute_edge(e, SYN_SNAP, REG, ROOT)
check("日×日全窗复算 r=1.0000 n=29(与边表一致)",
      rc.get('available') and abs(rc['r'] - 1.0) < 1e-9 and rc['n'] == 29,
      str(rc))
rc = sv.recompute_edge(e, None, None, ROOT)
check("无快照 → 如实拒算(available=False)",
      rc.get('available') is False and '快照' in rc.get('reason', ''), str(rc))
e_bad = mk_edge('E-RC2', 'QB-20990101-999', 0.5, 3, a='NO_SUCH_M', b='UST_2Y')
rc = sv.recompute_edge(e_bad, SYN_SNAP, REG, ROOT)
check("指标不在注册表 → 如实拒算", rc.get('available') is False
      and '注册表' in rc.get('reason', ''), str(rc))

# 月网格: FED_FUNDS(月频)×UST_2Y(日频,仅月首观测)——变化共线 → r=1
mca = [0.10, -0.05, 0.20, 0.15, -0.10, 0.25, -0.15, 0.10, 0.05, -0.05,
       0.20]
mon_dates = [f'2025-{m:02d}-01' for m in range(1, 12)]
SYN_SNAP['series_store']['FED_FUNDS'] = {'dates': mon_dates,
                                         'values': _cum(mca, 4.0)}
SYN_SNAP['series_store']['UST_2Y'] = {
    'dates': mon_dates,
    'values': [round(2 * v, 6) for v in _cum(mca, 4.0)]}
e = mk_edge('E-MG', Q30, 1.0, 10, win='月网格', a='FED_FUNDS', b='UST_2Y')
rc = sv.recompute_edge(e, SYN_SNAP, REG, ROOT)
check("月×日月网格对齐复算 r=1.0000 n=10",
      rc.get('available') and rc.get('align') == 'month_grid'
      and abs(rc['r'] - 1.0) < 1e-9 and rc['n'] == 10, str(rc))

# lag6: b 的变化 cb[j]=ca[j+6](前 6 个变化对齐 a 的后段)→ lag+6 方向 r=1
lag_dates = [f'2025-{m:02d}-01' for m in range(1, 13)]
la = [0.1, -0.1, 0.2, 0.05, -0.15, 0.1, 0.25, -0.05, 0.15, 0.1, -0.1, 0.2]
vals_a = _cum(la, 3.0)
lb = la[6:] + [0.05, -0.05, 0.1, -0.1, 0.05]   # 前6=la[6:](对齐面),后5=填充
vals_b, v = [], 2.0
for d in lb:
    v += d
    vals_b.append(round(v, 6))
SYN_SNAP['series_store']['FED_FUNDS'] = {'dates': lag_dates,
                                         'values': vals_a}
SYN_SNAP['series_store']['UST_2Y'] = {'dates': lag_dates, 'values': vals_b}
e = mk_edge('E-LAG', Q30, 1.0, 5, win='月网格 lag6', a='FED_FUNDS',
            b='UST_2Y')
rc = sv.recompute_edge(e, SYN_SNAP, REG, ROOT)
hit = rc.get('lag_candidates', {})
check("lag 边双向候选命中(+6 方向 r≈1)",
      rc.get('available') and any(c['r'] is not None
                                  and abs(c['r'] - 1.0) < 1e-9
                                  for c in hit.values()), str(rc))
check("lag 候选双向都在场(方向未登记→如实双算)",
      set(hit) == {1, -1}, str(sorted(hit)))

# 窗口解析 + 3yr 通用化(horizon_start Ny)
check("parse_window 全窗", sv.parse_window('全窗') == {'start': None, 'lag': 0})
check("parse_window 2016起", sv.parse_window('2016起')
      == {'start': '2016-01-01', 'lag': 0})
check("parse_window 3yr → years_back", sv.parse_window('3yr')
      == {'start': None, 'years_back': 3, 'lag': 0})
check("parse_window 月网格 lag6", sv.parse_window('月网格 lag6')
      == {'start': None, 'lag': 6})
check("horizon_start 3y(20261101→2023-11-01,P0-3 复用面)",
      wd.horizon_start('20261101', '3y') == '2023-11-01')
check("horizon_start 3y 闰年钳制(20240229→2021-02-28)",
      wd.horizon_start('20240229', '3y') == '2021-02-28')
# 篡改边 r=0.5 → 复算矛盾(用日频对快照副本,序列未被月网格段覆写)
SNAP_DAILY = {'snapshot_id': 'research_snapshot_20260130_syn',
              'target_date': '20260130',
              'series_store': {
                  'UST_10Y': {'dates': day_dates, 'values': _cum(ca)},
                  'UST_2Y': {'dates': day_dates,
                             'values': [round(2 * v, 6) for v in _cum(ca)]}}}
et = mk_edge('E-TAMPER', Q30, 0.5, 29)
with open(EP, 'w', encoding='utf-8') as f:
    json.dump(edges_doc([et]), f, ensure_ascii=False)
rep = sv.verify_edges(archive_dir=ARCH, edges_path=EP, recompute=True,
                      snap=SNAP_DAILY, reg=REG)
x = rep['results'][0]
check("篡改边 → CONFLICTED(包含核验与复算至少一路给矛盾证据)",
      x['state'] == 'CONFLICTED' and x.get('conflict'), str(x.get('conflict')))
rep = sv.verify_edges(archive_dir=ARCH, edges_path=EP)
x = rep['results'][0]
check("纯包含核验(不复算)也独立逮住篡改",
      x['state'] == 'CONFLICTED' and '未在归档原文找到' in x['conflict'],
      str(x.get('conflict')))

print("═" * 60)
print("[5] 装载面硬闸: transmission_edges 存在性核验(双轨)")
print("═" * 60)
doc = wd.transmission_edges(archive_dir=ARCH + '_ok' if False else None)
# 真实归档环境(dev/LIVE): performed=True;干净clone: 跳过——两轨都不许崩
if doc.get('archive_check', {}).get('performed'):
    check("真实归档在场 → 存在性核验执行+引用清单随行",
          doc['archive_check']['checked_refs'] == ['QB-20261110-022',
                                                   'QB-20261110-023'],
          str(doc['archive_check']))
else:
    check("归档缺席 → performed=False+原因(干净clone轨)",
          doc['archive_check']['performed'] is False
          and '干净clone' in doc['archive_check']['note'],
          str(doc.get('archive_check')))
FIX_ARCH = fixt.build_archive(tempfile.mkdtemp(prefix='c9sv_fixt_'))
doc2 = wd.transmission_edges(archive_dir=FIX_ARCH)
check("注入含 022/023 的合成归档 → 核验执行+引用清单齐(边+机制+结构)",
      doc2['archive_check']['performed'] is True
      and doc2['archive_check']['checked_refs'] == ['QB-20261110-022',
                                                    'QB-20261110-023']
      and doc2['archive_check']['n_records'] == 2, str(doc2['archive_check']))
try:
    wd.transmission_edges(archive_dir=ARCH)   # 只含 Q30/Q31,真表引用 022/023
    check("悬空 qb_source → raise(伪号不入页)", False)
except ValueError as ex:
    check("悬空 qb_source → raise(伪号不入页,含机制/结构引用)",
          '不存在' in str(ex) and '022' in str(ex) and '023' in str(ex),
          str(ex))
try:
    wd.transmission_edges(archive_dir=os.path.join(TD, 'no_arch'))
    ok = True
except Exception:                          # noqa: BLE001
    ok = False
check("归档目录缺席 → 不 raise(装载降级核验,CI 不崩)", ok)

print("═" * 60)
print("[6] views lint --verify-urls: 默认关+显式档位只披露")
print("═" * 60)
GOOD = {
    'schema_version': '1.1', 'view_id': 'VIEW-20261110-001',
    'institution': {'name': 'Synthetic Bank', 'type': 'investment_bank',
                    'department': 'Research'},
    'authors': [], 'report_title': 'Synthetic Outlook',
    'source_url': 'https://example.com/a', 'source_type': 'official_site',
    'publish_date': '2026-11-01', 'fetch_date': '2026-11-10',
    'access_level': 'public_full', 'view_horizon': '6m',
    'subjects': ['US_rates'],
    'core_views': [{'statement': '利率维持高位。',
                    'attribution': 'institution_stated',
                    'basis': 'verbatim_quote', 'quote': 'Rates stay higher.'}],
    'forecasts': [], 'key_assumptions': [], 'evidence_cited': [],
    'mechanism_steps': [], 'risk_factors': [], 'falsification_conditions': [],
    'revisions': [], 'completeness_notes': '合成', 'copyright_note': 'meta+link',
}
VTD = tempfile.mkdtemp(prefix='c9views_')
with open(os.path.join(VTD, 'VIEW-20261110-001.json'), 'w',
          encoding='utf-8') as f:
    json.dump(GOOD, f, ensure_ascii=False)


def run_cli(args, views_dir, patch):
    code = ("import sys, os; sys.path.insert(0, %r); sys.path.insert(0, %r); "
            "import view_store as vs; "
            "vs.VIEWS_DIR = %r; %s; "
            "sys.argv = ['ia_cli.py'] + %r; "
            "import ia_cli; ia_cli.main()"
            % (ROOT, os.path.join(ROOT, 'scripts'), views_dir, patch, args))
    p = subprocess.run([sys.executable, '-c', code], capture_output=True,
                       text=True, cwd=ROOT)
    try:
        return p.returncode, json.loads(p.stdout), p.stdout
    except ValueError:
        return p.returncode, None, p.stdout


TRIPWIRE = ("import urllib.request as u\n"
            "def _boom(*a, **k):\n"
            "    raise AssertionError('network touched: lint 默认档零网络被破')\n"
            "u.urlopen = _boom")
rc, out, raw = run_cli(['views', 'lint'], VTD, TRIPWIRE)
check("默认档零网络(tripwire 未触发)+ok=true rc=0",
      rc == 0 and out and out['ok'] is True, f"rc={rc} raw={raw[:160]}")
check("默认档无 url_checks 键", 'url_checks' not in out['data'])
FAKE = ("import urllib.request as u\n"
        "class _R:\n"
        "    status = 200\n"
        "    def __enter__(self): return self\n"
        "    def __exit__(self, *a): return False\n"
        "u.urlopen = lambda *a, **k: _R()")
rc, out, _ = run_cli(['views', 'lint', '--verify-urls'], VTD, FAKE)
uc = out['data'].get('url_checks') if out else None
check("--verify-urls 联网档位: url_checks 在场+可达",
      rc == 0 and uc and uc['n_checked'] == 1 and uc['n_reachable'] == 1
      and uc['checks'][0]['reachable'], str(uc))
check("--verify-urls 只披露不隔离(ok 仍 true)",
      out['ok'] is True and not out['data']['quarantined'])
DEAD = ("import urllib.request as u\n"
        "def _dead(*a, **k):\n"
        "    raise OSError('DNS 不存在域名(合成)')\n"
        "u.urlopen = _dead")
rc, out, _ = run_cli(['views', 'lint', '--verify-urls'], VTD, DEAD)
uc = out['data'].get('url_checks') if out else None
check("不可达 → reachable=False+原因,不隔离(ok true)+警告含'不可达≠伪造'",
      rc == 0 and out['ok'] is True and uc
      and uc['n_reachable'] == 0 and uc['checks'][0]['note']
      and any('不可达≠伪造' in w for w in out['warnings']), str(uc))

print("═" * 60)
print("[7] CLI 退出码面")
print("═" * 60)
p = subprocess.run([sys.executable,
                    os.path.join(ROOT, 'scripts', 'source_verifier.py'),
                    '--qb', Q30, '--archive-dir', ARCH],
                   capture_output=True, text=True, cwd=ROOT)
check("--qb 在册 → rc=0 + VERIFIED 行",
      p.returncode == 0 and '[VERIFIED' in p.stdout, p.stdout[:120])
p = subprocess.run([sys.executable,
                    os.path.join(ROOT, 'scripts', 'source_verifier.py'),
                    '--qb', 'QB-20990101-999', '--archive-dir', ARCH],
                   capture_output=True, text=True, cwd=ROOT)
check("--qb 伪号 → rc=1 + MISSING 行",
      p.returncode == 1 and '[MISSING' in p.stdout, p.stdout[:120])

print()
print("═" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("═" * 60)
sys.exit(0 if FAIL == 0 else 1)
