#!/usr/bin/env python3
"""IA-P0-1-FIX1 对抗性整改测试(2026-10-27) — 契约IA-P0-1-FIX1-AC-v1.0

14项强制对抗场景,全部**真实行为测试**(临时目录+SYNTHETIC fixture+GLM mock,
不做源码字符串断言;不发起任何付费调用):
 1  数据包数字篡改→预检拒绝            2  锚点数字篡改→拒绝(含sidecar同步改)
 3  锚点prompt替换→拒绝                4  锚点meta摘要被改→拒绝
 5  锚点残留旧指标→拒绝                6  快照文件名/身份冲突/重复版本→整日拒绝
 7  Gate A声明与事实矛盾→拒绝放行      8  非核心单项FAIL→DEGRADED(注册表为权威)
 9  关键采集失败→正式步骤SKIPPED+台账   10 锚点缺quality/非法→观察与引擎双侧拒绝
 11 合格报告覆盖尝试→原有报告不受损    12 Gate B校验器异常→候选隔离不发布
 13 report_status写入失败→不得发布     14 月报/季报无门禁入口→UNVALIDATED草稿

运行: ~/AI内容/venv/bin/python3 tests/test_p01_fix1.py
"""
import os
import sys
import json
import io
import glob
import shutil
import tempfile
import contextlib
import unittest.mock as mock

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


def quiet(fn, *a, **kw):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r = fn(*a, **kw)
    return r


import research_provenance as rp
import snapshot_builder as sb
import data_assembler as da
import report_generator as rg
import daily_prediction_observer as dpo
import allocation_engine as ae
import monthly_review as mr
import quarterly_outlook as qo
import run_weekly

DAY = '20261017'
DAY_ISO = '2026-10-17'
AS_OF = '2026-10-17T08:00:00+08:00'


class _FakeDT:
    @staticmethod
    def now():
        import datetime as _dt
        return _dt.datetime(2026, 10, 17, 8, 0, 0)


# ═══════════ fixture: 快照级研究日(与生产同构的生成路径) ═══════════

def synth_snapshot(ymd=DAY, gate='PASS', rev=None, fail_fact=False, sid=None):
    sid = sid or (f"research_snapshot_{ymd}" + (f"_v{rev}" if rev else ""))
    obs = f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}"
    glob_facts = [('SPX', '标普500', 7659.44), ('NDX', '纳斯达克100', 25631.51),
                  ('VIX', 'VIX恐慌指数', 15.82), ('DXY', '美元指数', 103.21),
                  ('GOLD_F', '黄金期货', 4300.0), ('WTI_F', 'WTI原油期货', 71.28)]
    monthly = [('CPI', 'CPI同比', 2.4), ('CORE_CPI', '核心CPI同比', 2.8),
               ('UNEMPLOYMENT', '失业率', 4.1), ('UMCSENT', '密歇根消费者信心', 68.2)]
    facts = []
    for mid, name, val in glob_facts:
        q = 'FAIL' if (fail_fact and mid == 'GOLD_F') else 'PASS'
        facts.append({'metric_id': mid, 'display_name': name, 'value': val,
                      'unit': '指数点', 'observation_date': obs, 'quality_status': q,
                      'high': round(val * 1.01, 2), 'low': round(val * 0.99, 2),
                      'derived': {'week': {'pct_change': 0.52},
                                  'mtd': {'pct_change': 1.31},
                                  'ytd': {'pct_change': 12.04}},
                      'issues': []})
    for mid, name, val in monthly:
        facts.append({'metric_id': mid, 'display_name': name, 'value': val,
                      'unit': '%', 'observation_date': obs, 'quality_status': 'PASS',
                      'derived': {'m1': {'basis_value': round(val * 0.99, 3),
                                         'pct_change': 0.4, 'pp_change': 0.1},
                                  'm12': {'basis_value': round(val * 0.95, 3),
                                          'pct_change': 2.1, 'pp_change': 0.3}},
                      'issues': []})
    counts = {'PASS': sum(1 for f in facts if f['quality_status'] == 'PASS'),
              'DEGRADED': 0,
              'FAIL': sum(1 for f in facts if f['quality_status'] == 'FAIL')}
    return {
        'snapshot_id': sid, 'research_as_of': AS_OF, 'target_date': ymd,
        'timezone': 'Asia/Shanghai',
        'sources_status': {'global': {'status': 'EXACT', 'file': f"global_{ymd}.json",
                                      'file_date': ymd}},
        'fed_futures_curve': [], 'facts': facts, 'reconciliation': [],
        'quality': {'counts': counts, 'missing_core': [],
                    'fail_metrics': ['GOLD_F'] if fail_fact else []},
        'gate_a': {'status': gate, 'core_missing': [],
                   'core_fail': ['GOLD_F'] if fail_fact else [], 'note': 'synthetic'},
    }


def build_research_day(base, ymd=DAY, gate='PASS', rev=None, fail_fact=False):
    """构造一天完整研究产物(快照/数据包+meta/锚点+meta/prompt),全部真实生成路径。"""
    daily = os.path.join(base, 'daily')
    weekly = os.path.join(base, 'weekly')
    os.makedirs(daily, exist_ok=True)
    os.makedirs(weekly, exist_ok=True)
    snap = synth_snapshot(ymd, gate=gate, rev=rev, fail_fact=fail_fact)
    snap_path = os.path.join(daily, snap['snapshot_id'] + '.json')
    with open(snap_path, 'w', encoding='utf-8') as f:
        json.dump(snap, f, ensure_ascii=False)
    anchors = sb.build_anchors(snap, ymd)
    packfile = os.path.join(weekly, f'data_pack_{ymd}.md')
    with open(packfile, 'w', encoding='utf-8') as f:
        f.write(da.build_markdown(snap, ymd) if gate != 'FAIL' else '# pack')
    rp.write_meta(packfile, {'source': 'snapshot', 'generated_by': 'data_assembler',
                             'pack_file': os.path.basename(packfile),
                             'pack_digest': rp.digest_file(packfile),
                             **rp.provenance_of(snap, snap_path)})
    apath = os.path.join(daily, f'anchors_{ymd}.json')
    with open(apath, 'w', encoding='utf-8') as f:
        json.dump(anchors, f, ensure_ascii=False, indent=1)
    rp.write_meta(apath, {'source': 'snapshot', 'generated_by': 'snapshot_builder',
                          'anchor_count': len(anchors),
                          'anchors_digest': rp.digest_file(apath),
                          **rp.provenance_of(snap, snap_path)})
    from data_validator import generate_anchor_prompt_block
    ppath = os.path.join(daily, f'anchor_prompt_{ymd}.md')
    with open(ppath, 'w', encoding='utf-8') as f:
        f.write(generate_anchor_prompt_block(anchors))
    rp.write_meta(ppath, {'source': 'snapshot', 'generated_by': 'data_validator',
                          'target_date': ymd, 'prompt_digest': rp.digest_file(ppath)})
    return snap, snap_path


def preflight(td):
    with mock.patch.object(rg, 'DATA_DIR', td):
        return rg.verify_research_inputs(DAY)


print("=" * 64)
print("IA-P0-1-FIX1 对抗性整改: 14项强制场景")
print("=" * 64)

# ═══ 1. 数据包数字篡改 ═══════════════════════════════════════════
print("\n── 1. 数据包数字篡改(FIX-01)")
with tempfile.TemporaryDirectory() as td:
    build_research_day(td)
    packfile = os.path.join(td, 'weekly', f'data_pack_{DAY}.md')
    orig = open(packfile, encoding='utf-8').read()
    # 篡改一个数字(黄金4,300.00→9,999.00;数据包表格带千分位),meta摘要不变(旧值)
    assert '4,300.00' in orig
    with open(packfile, 'w', encoding='utf-8') as f:
        f.write(orig.replace('4,300.00', '9,999.00', 1))
    ok, problems, _ = preflight(td)
    check("数据包数字篡改→预检拒绝", not ok and any('数据包' in p for p in problems),
          str(problems))
with tempfile.TemporaryDirectory() as td:
    build_research_day(td)
    packfile = os.path.join(td, 'weekly', f'data_pack_{DAY}.md')
    # 攻击者同步更新meta摘要(声明一致)——仍须拒绝: pack绑定的快照digest失配
    orig = open(packfile, encoding='utf-8').read()
    with open(packfile, 'w', encoding='utf-8') as f:
        f.write(orig.replace('4,300.00', '9,999.00', 1))
    meta = rp.load_meta(packfile)
    meta['pack_digest'] = rp.digest_file(packfile)   # 声明与实际一致
    rp.write_meta(packfile, meta)
    ok, problems, _ = preflight(td)
    check("数据包篡改+meta摘要同步改→仍拒绝(快照内容绑定)",
          not ok, str(problems))

# ═══ 2. 锚点数字篡改 ═════════════════════════════════════════════
print("\n── 2. 锚点数字篡改(FIX-01)")
with tempfile.TemporaryDirectory() as td:
    build_research_day(td)
    apath = os.path.join(td, 'daily', f'anchors_{DAY}.json')
    anchors = json.load(open(apath, encoding='utf-8'))
    key = 'global_market.data.GOLD.close'
    anchors[key]['value'] = 9999.0   # 篡改数字
    with open(apath, 'w', encoding='utf-8') as f:
        json.dump(anchors, f, ensure_ascii=False, indent=1)
    ok, problems, _ = preflight(td)
    check("锚点数字篡改→预检拒绝(摘要重算失配)",
          not ok and any('锚点' in p for p in problems), str(problems))
with tempfile.TemporaryDirectory() as td:
    build_research_day(td)
    apath = os.path.join(td, 'daily', f'anchors_{DAY}.json')
    anchors = json.load(open(apath, encoding='utf-8'))
    anchors['global_market.data.GOLD.close']['value'] = 9999.0
    with open(apath, 'w', encoding='utf-8') as f:
        json.dump(anchors, f, ensure_ascii=False, indent=1)
    meta = rp.load_meta(apath)
    meta['anchors_digest'] = rp.digest_file(apath)   # 摘要声明同步改
    rp.write_meta(apath, meta)
    ok, problems, _ = preflight(td)
    check("锚点篡改+meta摘要同步改→仍拒绝(权威快照确定性重建)",
          not ok and any('重建' in p or '不一致' in p for p in problems), str(problems))

# ═══ 3. 锚点prompt替换 ═══════════════════════════════════════════
print("\n── 3. 锚点prompt替换(FIX-01)")
with tempfile.TemporaryDirectory() as td:
    build_research_day(td)
    ppath = os.path.join(td, 'daily', f'anchor_prompt_{DAY}.md')
    orig = open(ppath, encoding='utf-8').read()
    assert '4300' in orig or '4300.0' in orig
    # 数字替换: 所有4300→9999(prompt数字被改)
    with open(ppath, 'w', encoding='utf-8') as f:
        f.write(orig.replace('4300', '9999'))
    meta = rp.load_meta(ppath)
    meta['prompt_digest'] = rp.digest_file(ppath)
    rp.write_meta(ppath, meta)
    ok, problems, _ = preflight(td)
    check("prompt数字替换(摘要同步改)→预检拒绝(锚点重建比对)",
          not ok and any('prompt' in p for p in problems), str(problems))
with tempfile.TemporaryDirectory() as td:
    build_research_day(td)
    ppath = os.path.join(td, 'daily', f'anchor_prompt_{DAY}.md')
    # 整体替换为另一份合法渲染但锚点集合不同(混入额外指标行)
    with open(ppath, 'a', encoding='utf-8') as f:
        f.write("\n| global_market.data.FAKE.close | 1234.00 | 2026-10-17 |\n")
    meta = rp.load_meta(ppath)
    meta['prompt_digest'] = rp.digest_file(ppath)
    rp.write_meta(ppath, meta)
    ok, problems, _ = preflight(td)
    check("prompt混入额外指标行→预检拒绝", not ok, str(problems))

# ═══ 4. 锚点meta摘要被改 ═════════════════════════════════════════
print("\n── 4. 锚点meta摘要被改(FIX-01)")
with tempfile.TemporaryDirectory() as td:
    build_research_day(td)
    apath = os.path.join(td, 'daily', f'anchors_{DAY}.json')
    meta = rp.load_meta(apath)
    meta['anchors_digest'] = 'deadbeefdeadbeef'   # 声明摘要被改(文件未动)
    rp.write_meta(apath, meta)
    ok, problems, _ = preflight(td)
    check("meta声明摘要与实际文件不符→预检拒绝(重算不信任声明)",
          not ok and any('摘要' in p or '不一致' in p for p in problems), str(problems))
with tempfile.TemporaryDirectory() as td:
    build_research_day(td)
    apath = os.path.join(td, 'daily', f'anchors_{DAY}.json')
    meta = rp.load_meta(apath)
    meta['snapshot_digest'] = 'deadbeefdeadbeef'   # 快照绑定摘要被改
    rp.write_meta(apath, meta)
    ok, problems, _ = preflight(td)
    check("meta快照digest被改→预检拒绝", not ok, str(problems))

# ═══ 5. 锚点残留旧指标 ═══════════════════════════════════════════
print("\n── 5. 锚点残留旧指标(FIX-01)")
with tempfile.TemporaryDirectory() as td:
    build_research_day(td)
    apath = os.path.join(td, 'daily', f'anchors_{DAY}.json')
    anchors = json.load(open(apath, encoding='utf-8'))
    # 残留一个旧批次指标(键集合多余)
    anchors['global_market.data.OLD_METRIC.close'] = {
        'value': 123.0, 'obs_date': DAY_ISO, 'as_of': DAY_ISO, 'quality': 'PASS'}
    with open(apath, 'w', encoding='utf-8') as f:
        json.dump(anchors, f, ensure_ascii=False, indent=1)
    meta = rp.load_meta(apath)
    meta['anchors_digest'] = rp.digest_file(apath)
    rp.write_meta(apath, meta)
    ok, problems, _ = preflight(td)
    check("锚点残留旧指标(摘要同步改)→预检拒绝(重建键集合比对)",
          not ok and any('残留' in p or '重建' in p for p in problems), str(problems))
    # 观察器同口径: 残留批次→关键FAIL
    vp = os.path.join(td, 'views.json')
    json.dump({'version': 2, 'views': [], 'predictions': []}, open(vp, 'w'))
    ch, n, st = quiet(dpo.observe, views_path=vp, anchors=anchors,
                      today_str=DAY_ISO, anchors_date=DAY, anchors_path=apath)
    check("观察器: 残留锚点批次→关键FAIL不写观察", st == 'FAIL' and ch == [],
          f"{st} {ch}")

# ═══ 6. 快照身份冲突/重复版本 ════════════════════════════════════
print("\n── 6. 快照身份冲突与重复版本(FIX-06)")
with tempfile.TemporaryDirectory() as td:
    # _v2文件内部自称base id
    s2 = synth_snapshot(rev=2)
    s2['snapshot_id'] = 'research_snapshot_20261017'   # 身份与文件名冲突
    json.dump(s2, open(os.path.join(td, 'research_snapshot_20261017_v2.json'), 'w',
                       encoding='utf-8'), ensure_ascii=False)
    snap, why = rp.select_snapshot(DAY, td)
    check("_v2文件自称base id→整日拒绝", snap is None and 'snapshot_id' in why, why)
with tempfile.TemporaryDirectory() as td:
    # 同日重复版本号: _v2与_v02都解析为版本2(内容不同)——无法确定性选择
    json.dump(synth_snapshot(rev=2), open(os.path.join(td, 'research_snapshot_20261017_v2.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    other = synth_snapshot(rev=2)
    other['facts'][0]['value'] = 1111.11
    json.dump(other, open(os.path.join(td, 'research_snapshot_20261017_v02.json'), 'w',
                          encoding='utf-8'), ensure_ascii=False)
    snap, why = rp.select_snapshot(DAY, td)
    check("同日重复版本(_v2与_v02同为v2)→整日拒绝(不猜测取哪个)",
          snap is None and '重复版本' in why, why)
with tempfile.TemporaryDirectory() as td:
    # 非法版本号_v0
    s0 = synth_snapshot(sid='research_snapshot_20261017_v0')
    json.dump(s0, open(os.path.join(td, 'research_snapshot_20261017_v0.json'), 'w',
                       encoding='utf-8'), ensure_ascii=False)
    snap, why = rp.select_snapshot(DAY, td)
    check("非法版本号_v0→拒绝", snap is None, why)
with tempfile.TemporaryDirectory() as td:
    # target_date与文件名不符
    sx = synth_snapshot()
    sx['target_date'] = '20261010'
    json.dump(sx, open(os.path.join(td, 'research_snapshot_20261017.json'), 'w',
                       encoding='utf-8'), ensure_ascii=False)
    snap, why = rp.select_snapshot(DAY, td)
    check("target_date与文件名不符→拒绝", snap is None and 'target_date' in why, why)
with tempfile.TemporaryDirectory() as td:
    # 合法多版本: base+v2+v3 → 取最高版v3
    json.dump(synth_snapshot(), open(os.path.join(td, 'research_snapshot_20261017.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(synth_snapshot(rev=2), open(os.path.join(td, 'research_snapshot_20261017_v2.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(synth_snapshot(rev=3), open(os.path.join(td, 'research_snapshot_20261017_v3.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    snap, path = rp.select_snapshot(DAY, td)
    check("合法多版本→确定性取最高修订版",
          snap is not None and snap['snapshot_id'] == 'research_snapshot_20261017_v3',
          str(snap and snap['snapshot_id']))
    # 修订后旧base锚点批次不得续用(身份链)
    anchors = sb.build_anchors(synth_snapshot(), DAY)   # base批锚点
    os.makedirs(os.path.join(td, 'daily'), exist_ok=True)
    apath = os.path.join(td, 'daily', f'anchors_{DAY}.json')
    with open(apath, 'w', encoding='utf-8') as f:
        json.dump(anchors, f, ensure_ascii=False, indent=1)
    rp.write_meta(apath, {'source': 'snapshot', 'generated_by': 'snapshot_builder',
                          'anchor_count': len(anchors),
                          'anchors_digest': rp.digest_file(apath),
                          **rp.provenance_of(synth_snapshot(),
                                             os.path.join(td, 'research_snapshot_20261017.json'))})
    ok, reason = rp.verify_anchor_batch(apath, anchors_date=DAY)
    check("同日修订_v3后,旧base锚点批次→核验拒绝", ok is False and '批次' in reason,
          reason)

# ═══ 7. Gate A声明与事实矛盾 ═════════════════════════════════════
print("\n── 7. Gate A声明冲突(FIX-05)")
core_sample = sorted(rp.core_metric_ids())[:3]
check("注册表criticality可加载(核心指标非空)", len(rp.core_metric_ids()) >= 30,
      str(len(rp.core_metric_ids())))
snap = synth_snapshot()
snap['gate_a'] = {'status': 'PASS', 'core_fail': ['GOLD_F'], 'core_missing': []}
got, why = rp.gate_status(snap)
check("声明PASS但core_fail非空→拒绝", got is None and 'core_fail' in why, why)
snap = synth_snapshot()
snap['gate_a'] = {'status': 'PASS', 'core_fail': [], 'core_missing': ['VIX']}
got, why = rp.gate_status(snap)
check("声明PASS但core_missing非空→拒绝", got is None and 'core_missing' in why, why)
snap = synth_snapshot(fail_fact=True)   # GOLD_F事实FAIL(核心)
snap['gate_a'] = {'status': 'PASS', 'core_fail': [], 'core_missing': []}
got, why = rp.gate_status(snap)
check("声明PASS但核心事实实际FAIL→拒绝(复核事实层)", got is None and '实际FAIL' in why, why)
snap = synth_snapshot()
snap['quality']['overall'] = 'FAIL'
got, why = rp.gate_status(snap)
check("声明PASS但quality.overall=FAIL→拒绝(状态冲突)", got is None and 'overall' in why, why)
snap = synth_snapshot()
snap['gate_a'] = {'status': 'DEGRADED', 'core_fail': ['GOLD_F'], 'core_missing': []}
got, why = rp.gate_status(snap)
check("声明DEGRADED但core_fail非空→拒绝(核心问题必须判FAIL)",
      got is None and 'core_fail' in why, why)
snap = synth_snapshot()
snap['gate_a'] = {'status': 'PASS', 'core_fail': [], 'core_missing': []}
# 非核心事实FAIL+声明PASS: overall为FAIL时拒绝;overall缺省时核心复核通过
snap['facts'].append({'metric_id': 'UMCSENT_X', 'value': 1, 'quality_status': 'FAIL'})
got, why = rp.gate_status(snap)
check("非核心事实FAIL不触发核心复核拒绝(降级由builder层裁决)",
      got == 'PASS', f"{got} {why}")
for bad in ({'gate_a': {'status': 'maybe'}}, {'gate_a': {'status': ''}},
            {'gate_a': None}, {'gate_a': {'status': None}}):
    got, _ = rp.gate_status(bad)
    check(f"非法/缺失Gate A声明{bad['gate_a']}!r→None不默认PASS", got is None, str(got))

# ═══ 8. 注册表权威: 非核心单项FAIL→DEGRADED ═════════════════════
print("\n── 8. 非核心单项FAIL→DEGRADED(注册表为权威,FIX-05)")


def collector_day(td, break_metric=None):
    """全核心齐备的SYNTHETIC采集日(全部注册表core指标在场,经真实build_snapshot)。"""
    OBS = '2026-10-16'
    YMD = DAY

    def series(d):
        ds = sorted(d)
        return {"dates": ds, "values": [d[k] for k in ds]}

    def _brk(v):
        return "N/A" if break_metric else v

    glob = {"date": YMD, "time": "07:12:00", "count": 7, "data": {
        "SPX": {"close": _brk(7659.44) if break_metric == 'SPX' else 7659.44,
                "high": 7680.0, "low": 7601.0, "date": OBS,
                "series": series({"2026-10-09": 7500.0, "2026-10-16": 7659.44})},
        "NDX": {"close": 25631.5, "high": 25700.0, "low": 25400.0, "date": OBS,
                "series": series({"2026-10-09": 25400.0, "2026-10-16": 25631.5})},
        "VIX": {"close": 15.82, "high": 16.4, "low": 15.2, "date": OBS,
                "series": series({"2026-10-09": 16.0, "2026-10-16": 15.82})},
        "DXY": {"close": 103.21, "high": 103.5, "low": 102.9, "date": OBS,
                "series": series({"2026-10-09": 103.0, "2026-10-16": 103.21})},
        "GOLD": {"close": 4300.0, "date": OBS,
                 "series": series({"2026-10-09": 4250.0, "2026-10-16": 4300.0})},
        "WTI": {"close": 71.28, "date": OBS,
                "series": series({"2026-10-09": 70.5, "2026-10-16": 71.28})},
        "BTC": {"close": 108000.0, "date": OBS,
                "series": series({"2026-10-09": 106000.0, "2026-10-16": 108000.0})},
    }}
    mdates = ['2026-10-08', '2026-10-09', '2026-10-13', '2026-10-14', '2026-10-15', '2026-10-16']

    def dser(vals):
        return {"dates": mdates, "values": vals}

    cpi_dates = ['2025-%02d-01' % m for m in range(1, 13)] + ['2026-%02d-01' % m for m in range(1, 10)]
    cpi_vals = [300.0 + i * 0.8 for i in range(len(cpi_dates))]
    macro = {"date": YMD, "data": {
        "CCC_OAS": {"value": 10.18, "date": OBS, "frequency": "daily",
                    "series": dser([10.12, 10.12, 10.20, 10.30, 10.25, 10.18])},
        "HY_OAS": {"value": 5.20, "date": OBS, "frequency": "daily",
                   "series": dser([5.18, 5.19, 5.21, 5.22, 5.21, 5.20])},
        "TIPS_10Y": {"value": 2.31, "date": OBS, "frequency": "daily",
                     "series": dser([2.30, 2.31, 2.32, 2.31, 2.30, 2.31])},
        "UST_2Y": {"value": 3.98, "date": OBS, "frequency": "daily",
                   "series": dser([3.99, 3.98, 3.98, 3.97, 3.98, 3.98])},
        "UST_10Y": {"value": 4.28, "date": OBS, "frequency": "daily",
                    "series": dser([4.26, 4.27, 4.28, 4.29, 4.28, 4.28])},
        "BEI_10Y": {"value": 1.97, "date": OBS, "frequency": "daily"},
        "FED_FUNDS": {"value": 4.33, "date": OBS, "frequency": "daily"},
        "CPI": {"value": cpi_vals[-1], "date": "2026-09-01", "frequency": "monthly",
                "series": {"dates": cpi_dates, "values": cpi_vals}},
        "CORE_CPI": {"value": 306.0, "date": "2026-09-01", "frequency": "monthly"},
        "CORE_PCE": {"value": 118.5, "date": "2026-09-01", "frequency": "monthly"},
        "UNEMPLOYMENT": {"value": 4.2, "date": "2026-09-01", "frequency": "monthly"},
        "NFP": {"value": 160000.0, "date": "2026-09-01", "frequency": "monthly"},
        "NFP_MOM_K": {"value": 160.0, "date": "2026-09-01", "frequency": "monthly"},
        "ICSA": {"value": 221000.0, "date": "2026-10-15", "frequency": "weekly"},
        "UMCSENT": {"value": _brk(68.0) if break_metric == 'UMCSENT' else 68.0,
                    "date": "2026-09-01", "frequency": "monthly"},
    }, "derived": {}}
    cn_dates = ['2026-09-30', '2026-10-09', '2026-10-15', '2026-10-16']

    def cnser(v):
        return {"dates": cn_dates, "values": v}

    china = {"date": YMD, "data": {}, "indices": {
        "上证指数": {"name": "上证指数", "close": 3716.28, "date": OBS,
                    "series": cnser([3800.0, 3790.0, 3797.0, 3716.28])},
        "深证成指": {"name": "深证成指", "close": 12256.3, "date": OBS,
                    "series": cnser([12400.0, 12380.0, 12350.0, 12256.3])},
        "恒生指数": {"name": "恒生指数", "close": 24186.83, "date": OBS, "via": "tencent",
                    "series": cnser([24400.0, 24380.0, 24350.0, 24186.83])},
        "恒生国企指数": {"name": "恒生国企指数", "close": 8735.2, "date": OBS,
                    "series": cnser([8800.0, 8790.0, 8770.0, 8735.2])},
    }, "ah_premium": {"close": 128.56, "date": OBS},
       "turnover": {"date": YMD, "sh_amount_billion": 8000.0, "sz_amount_billion": 9000.0,
                    "total_amount_billion": 17000.0}}
    rate = {"date": YMD, "current_rates": {
        "DFF": {"name": "有效联邦基金利率", "value": 4.33, "date": OBS},
        "DFEDTARU": {"name": "目标区间上限", "value": 4.50, "date": OBS},
        "DFEDTARL": {"name": "目标区间下限", "value": 4.25, "date": OBS}},
        "fed_funds_futures": [
            {"ticker": "ZQ=F", "name": "FF期货主力", "price": 95.80, "implied_rate": 4.20},
            {"ticker": "ZQZ26.CBT", "name": "2026-12", "price": 95.90, "implied_rate": 4.10}],
        "real_economy": {
            "UNRATE": {"name": "失业率", "value": 4.2, "date": "2026-09-01", "freq": "月度"},
            "UMCSENT": {"name": "消费者信心", "value": 71.0, "date": "2026-09-01", "freq": "月度"}},
    }
    for name, obj in (("global", glob), ("macro", macro), ("china", china),
                      ("rate_economy", rate)):
        json.dump(obj, open(os.path.join(td, f"{name}_{DAY}.json"), 'w',
                            encoding='utf-8'), ensure_ascii=False)


with tempfile.TemporaryDirectory() as td:
    collector_day(td)
    snap = quiet(sb.build_snapshot, target_ymd=DAY, data_dir=td, out_dir=td, as_of=AS_OF)
    check("全核心齐备+无失败→Gate A PASS(基线)",
          snap['gate_a']['status'] == 'PASS', str(snap['gate_a']))
with tempfile.TemporaryDirectory() as td:
    collector_day(td, break_metric='UMCSENT')   # 非核心(信心指数)值坏
    snap = quiet(sb.build_snapshot, target_ymd=DAY, data_dir=td, out_dir=td, as_of=AS_OF)
    ga = snap['gate_a']
    check("非核心单项FAIL→DEGRADED而非FAIL",
          ga['status'] == 'DEGRADED' and ga['noncore_fail'] == ['UMCSENT']
          and ga['core_fail'] == [], str(ga))
    check("非核心失败已披露(noncore_fail清单)", 'UMCSENT' in ga.get('noncore_fail', []))
    check("非核心FAIL日仍允许正式研究(降级披露)",
          rp.gate_allows_formal_research(rp.gate_status(snap)[0]))
with tempfile.TemporaryDirectory() as td:
    collector_day(td, break_metric='SPX')   # 核心资产值坏
    snap = quiet(sb.build_snapshot, target_ymd=DAY, data_dir=td, out_dir=td, as_of=AS_OF)
    ga = snap['gate_a']
    check("核心指标FAIL→Gate A FAIL(不降阈值放行)",
          ga['status'] == 'FAIL' and ga['core_fail'] == ['SPX'], str(ga))
    check("核心FAIL日禁止正式研究",
          not rp.gate_allows_formal_research(rp.gate_status(snap)[0]))
# 非核心FAIL快照经gate_status声明一致性: DEGRADED+非核心清单→合法
snap = synth_snapshot()
snap['facts'].append({'metric_id': 'UMCSENT', 'value': 'N/A',
                      'quality_status': 'FAIL', 'issues': []})
snap['gate_a'] = {'status': 'DEGRADED', 'core_missing': [], 'core_fail': [],
                  'noncore_fail': ['UMCSENT']}
got, why = rp.gate_status(snap)
check("声明DEGRADED+非核心失败→合法降级(与注册表权威一致)", got == 'DEGRADED', why)

# ═══ 9. 关键采集失败→下游正式步骤SKIPPED+台账 ═════════════════════
print("\n── 9. 关键采集失败传播(FIX-03)")


def run_pipeline_main(td, fail_scripts=(), snapshot=None):
    """在td上运行run_weekly.main(): run_step按脚本名模拟成败(不执行真实采集)。"""
    executed = []

    def fake_run_step(step_name, script_name, timeout=900, script_dir=None):
        executed.append(script_name)
        return script_name not in fail_scripts

    logs = os.path.join(td, 'logs')
    with mock.patch.object(run_weekly, 'PROJECT_DIR', td), \
         mock.patch.object(run_weekly, 'SCRIPTS_DIR', os.path.join(td, 'scripts')), \
         mock.patch.object(run_weekly, 'datetime', _FakeDT), \
         mock.patch.object(run_weekly, 'run_step', fake_run_step):
        if snapshot is not None:
            dd = os.path.join(td, 'data', 'daily')
            os.makedirs(dd, exist_ok=True)
            json.dump(snapshot, open(os.path.join(dd, snapshot['snapshot_id'] + '.json'),
                                     'w', encoding='utf-8'), ensure_ascii=False)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                run_weekly.main()
            code = 0
        except SystemExit as e:
            code = e.code
    ledger = None
    lps = glob.glob(os.path.join(logs, 'pipeline_run_*.json'))
    if lps:
        ledger = json.load(open(lps[0], encoding='utf-8'))
    return code, executed, ledger


with tempfile.TemporaryDirectory() as td:
    code, executed, ledger = run_pipeline_main(td, fail_scripts={'global_market_collector.py'})
    skipped = {s['name']: s for s in ledger['steps'] if s['skipped']}
    check("全球采集失败→退出码1", code == 1, f"exit={code}")
    check("快照构建仍执行(让Gate A显式裁决,不隐式跳过)",
          'snapshot_builder.py' in executed)
    formal = ['macro_scorecard.py', 'correlation_calculator.py', 'data_assembler.py',
              'data_validator.py']
    check("正式研究步骤全部SKIPPED(不执行)",
          all(s not in executed for s in formal)
          and all(any(k in n for n in skipped) for k in
                  ('评分卡', '相关性', '数据汇总打包', '数据校验与锚点生成')),
          str(sorted(skipped)))
    check("SKIPPED原因点名失败上游采集步骤",
          any('全球市场数据采集' in r for r in
              (s.get('skip_reason') or '' for s in ledger['steps'])),
          str({n: s.get('skip_reason') for n, s in skipped.items()}))
    check("观察器不被上游依赖阻止(自持门禁,R17)",
          'daily_prediction_observer.py' in executed)
    check("台账含运行日期/研究目标日/快照不可用原因",
          ledger.get('run_date') == '2026-10-17'
          and ledger.get('research_target_date') == '20261017'
          and ledger.get('snapshot_unavailable_reason'),
          str({k: ledger.get(k) for k in ('run_date', 'research_target_date')}))
    check("采集失败日allow_formal_report=False",
          ledger.get('allow_formal_report') is False, str(ledger.get('allow_formal_report')))
with tempfile.TemporaryDirectory() as td:
    # 全部成功+当日权威快照在场(DEGRADED披露)→台账放行正式报告
    snap = synth_snapshot(gate='DEGRADED')
    snap['facts'][4]['quality_status'] = 'DEGRADED'   # GOLD_F降级披露
    code, executed, ledger = run_pipeline_main(td, snapshot=snap)
    check("全步骤成功+快照DEGRADED→退出码0+allow_formal_report=True",
          code == 0 and ledger.get('allow_formal_report') is True,
          f"exit={code} allow={ledger.get('allow_formal_report')}")
    check("台账记录快照身份(版本+digest+Gate A)",
          ledger.get('snapshot_id') == 'research_snapshot_20261017'
          and ledger.get('snapshot_digest') == rp.digest_snapshot(snap)
          and ledger.get('gate_a') == 'DEGRADED',
          str({k: ledger.get(k) for k in ('snapshot_id', 'snapshot_digest', 'gate_a')}))
with tempfile.TemporaryDirectory() as td:
    # Gate A FAIL快照在场(采集成功但数据质量失败)→不放行正式报告
    snap = synth_snapshot(gate='FAIL', fail_fact=True)
    code, executed, ledger = run_pipeline_main(td, snapshot=snap)
    check("Gate A FAIL→allow_formal_report=False(即便步骤全成)",
          ledger.get('allow_formal_report') is False and ledger.get('gate_a') == 'FAIL',
          str(ledger.get('allow_formal_report')))
for failed_collector in ('macro_collector.py', 'china_market_collector.py'):
    with tempfile.TemporaryDirectory() as td:
        code, executed, ledger = run_pipeline_main(td, fail_scripts={failed_collector})
        skipped = {s['name'] for s in ledger['steps'] if s['skipped']}
        check(f"{failed_collector}失败→exit 1+正式步骤SKIPPED",
              code == 1 and 'data_assembler.py' not in executed and skipped,
              f"exit={code}")
with tempfile.TemporaryDirectory() as td:
    # 非关键(新闻)失败→降级运行: 不阻断正式研究与观察,退出码0
    code, executed, ledger = run_pipeline_main(td, fail_scripts={'news_collector.py'})
    check("非关键新闻失败→降级运行exit 0,正式步骤照常",
          code == 0 and 'data_assembler.py' in executed
          and 'daily_prediction_observer.py' in executed, f"exit={code}")
with tempfile.TemporaryDirectory() as td:
    # 有效回退: 当日global文件缺失,回退3天前文件——必须显式披露FALLBACK+滞后天数,
    # 不得冒充当日EXACT采集(快照层既有降级机制,FIX-03要求披露而非放水)
    collector_day(td)
    os.rename(os.path.join(td, f'global_{DAY}.json'),
              os.path.join(td, 'global_20261014.json'))
    snap = quiet(sb.build_snapshot, target_ymd=DAY, data_dir=td, out_dir=td, as_of=AS_OF)
    gs = snap['sources_status']['global']
    check("回退数据→sources_status=FALLBACK+滞后天数+披露语",
          gs['status'] == 'FALLBACK' and gs.get('lag_days') == 3
          and '不得当作当日观测' in gs.get('disclosure', ''), str(gs))
    check("回退日数据包渲染数据源状态披露节",
          'FALLBACK' in da.build_markdown(snap, DAY))
with tempfile.TemporaryDirectory() as td:
    # 无效回退: 旧采集文件超出回退窗口→来源按MISSING处理,核心缺失→Gate A FAIL
    # (旧文件存在≠可用——不得因旧采集文件存在就自动放行,FIX-03)
    collector_day(td)
    os.rename(os.path.join(td, f'global_{DAY}.json'),
              os.path.join(td, 'global_20261006.json'))
    snap = quiet(sb.build_snapshot, target_ymd=DAY, data_dir=td, out_dir=td, as_of=AS_OF)
    check("无效回退(超出回退窗口)→来源MISSING+核心缺失→Gate A FAIL",
          snap['gate_a']['status'] == 'FAIL'
          and 'SPX' in snap['gate_a']['core_missing']
          and snap['sources_status']['global']['status'] == 'MISSING',
          str(snap['gate_a']) + str(snap['sources_status'].get('global')))

# ═══ 10. 锚点缺quality/非法→观察与引擎双侧拒绝 ═══════════════════
print("\n── 10. 预测观察质量门禁(FIX-04,双侧)")


def obs_pred(pid, metric):
    return {'pred_id': pid, 'asset': '黄金' if 'GOLD' in metric else '标普',
            'direction': 'SYNTHETIC测试预测', 'status': 'observing', 'metric': metric,
            'comparator': '>=', 'target': 4250.0, 'observe_from': '2026-10-10',
            'deadline': '2026-12-31', 'observations': []}


def views_file(td, preds):
    vp = os.path.join(td, 'views.json')
    json.dump({'version': 2, 'views': [], 'predictions': preds}, open(vp, 'w'),
              ensure_ascii=False)
    return vp


with tempfile.TemporaryDirectory() as td:
    # 引擎直连路径(不经观察器): 缺quality→拒绝写入观察历史
    vp = views_file(td, [obs_pred(91, 'global_market.data.GOLD.close')])
    data = json.load(open(vp))
    anchors = {'global_market.data.GOLD.close':
               {'value': 4300.0, 'obs_date': DAY_ISO, 'as_of': DAY_ISO}}   # 无quality
    quiet(ae.record_observations, data, anchors, DAY_ISO)
    check("引擎直连: 缺quality→不写入观察历史",
          data['predictions'][0]['observations'] == [],
          str(data['predictions'][0]['observations']))
    data = json.load(open(vp))
    anchors = {'global_market.data.GOLD.close':
               {'value': 4300.0, 'obs_date': DAY_ISO, 'as_of': DAY_ISO,
                'quality': 'PROBABLY_FINE'}}   # 非法值
    quiet(ae.record_observations, data, anchors, DAY_ISO)
    check("引擎直连: 非法quality值→拒绝", data['predictions'][0]['observations'] == [])
    data = json.load(open(vp))
    anchors = {'global_market.data.GOLD.close':
               {'value': 4300.0, 'obs_date': DAY_ISO, 'as_of': DAY_ISO,
                'quality': 'FAIL'}}
    quiet(ae.record_observations, data, anchors, DAY_ISO)
    check("引擎直连: quality=FAIL→拒绝", data['predictions'][0]['observations'] == [])
    data = json.load(open(vp))
    anchors = {'global_market.data.GOLD.close':
               {'value': 4300.0, 'obs_date': DAY_ISO, 'as_of': DAY_ISO,
                'quality': 'WARN'}}
    quiet(ae.record_observations, data, anchors, DAY_ISO)
    check("引擎直连: WARN(轻度提示)→照常记录",
          len(data['predictions'][0]['observations']) == 1,
          str(data['predictions'][0]['observations']))
    data = json.load(open(vp))
    anchors = {'global_market.data.GOLD.close':
               {'value': 4300.0, 'obs_date': DAY_ISO, 'as_of': DAY_ISO,
                'quality': 'DEGRADED'}}
    quiet(ae.record_observations, data, anchors, DAY_ISO)
    check("引擎直连: DEGRADED(已验证+披露)→照常记录",
          len(data['predictions'][0]['observations']) == 1)
with tempfile.TemporaryDirectory() as td:
    # 观察器路径: 无meta锚点→批次拒绝(FIX-04: 无来源证明不入正式观察)
    build_research_day(td)
    apath = os.path.join(td, 'daily', f'anchors_{DAY}.json')
    os.remove(rp.meta_path_for(apath))
    anchors = json.load(open(apath, encoding='utf-8'))
    vp = views_file(td, [obs_pred(91, 'global_market.data.GOLD.close')])
    before = open(vp).read()
    ch, n, st = quiet(dpo.observe, views_path=vp, anchors=anchors,
                      today_str=DAY_ISO, anchors_date=DAY, anchors_path=apath)
    check("观察器: 无meta→关键FAIL不写观察", st == 'FAIL' and open(vp).read() == before,
          f"{st} {ch}")
with tempfile.TemporaryDirectory() as td:
    # 无效指标仅影响其所属预测: 其余预测照常(隔离性)
    build_research_day(td, gate='FAIL', fail_fact=True)
    apath = os.path.join(td, 'daily', f'anchors_{DAY}.json')
    anchors = json.load(open(apath, encoding='utf-8'))
    vp = views_file(td, [obs_pred(91, 'global_market.data.GOLD.close'),
                         obs_pred(92, 'global_market.data.SPX.close')])
    ch, n, st = quiet(dpo.observe, views_path=vp, anchors=anchors,
                      today_str=DAY_ISO, anchors_date=DAY, anchors_path=apath)
    saved = json.load(open(vp))
    p91 = next(p for p in saved['predictions'] if p['pred_id'] == 91)
    p92 = next(p for p in saved['predictions'] if p['pred_id'] == 92)
    check("无效指标只影响自身预测(PARTIAL),同批照常",
          st == 'PARTIAL' and p91['observations'] == []
          and len(p92['observations']) == 1, f"{st} {p91['observations']}")

# ═══ 11-13. 合格报告保护事务(FIX-02) ═════════════════════════════
print("\n── 11/12/13. 合格报告保护(FIX-02)")


class _GLMRecorder:
    def __init__(self, text=None):
        self.text = text or ('# 投资周报(SYNTHETIC测试文本)\n\n' + '本周市场综述。' * 80)
        self.calls = 0

    def __call__(self, system_prompt, user_prompt, max_tokens=32000, timeout=900):
        self.calls += 1
        return self.text


def run_flow(td, gate_b='PASS', validator_exc=None, status_writer=None):
    """在已构造研究日的td上运行generate_weekly_report;返回(exit_code, glm, applied, out_dir)。"""
    glm = _GLMRecorder()
    applied = []

    def _apply(report, classification, anchors=None, **kw):
        applied.append(classification)

    def _validate(md_path, anchors=None, anchors_file=None):
        if validator_exc:
            raise validator_exc
        return (gate_b, ['SYNTHETIC警告'])

    patches = [
        mock.patch.object(rg, 'DATA_DIR', td),
        mock.patch.object(rg, 'OUTPUT_DIR', os.path.join(td, 'out', 'weekly')),
        mock.patch.object(rg, 'datetime', _FakeDT),
        mock.patch.object(rg, '_call_glm', glm),
        mock.patch.object(rg, 'apply_status_updates', _apply),
        mock.patch.object(rg, 'validate_generated_report', _validate),
        mock.patch.object(rg.allocation_engine, 'load_views',
                          lambda *a, **kw: {'views': [], 'predictions': []}),
        mock.patch.object(rg, 'pending_completed_month', lambda d=None: None),
        mock.patch.object(rg, 'pending_completed_quarter', lambda d=None: None),
        mock.patch.object(rg, 'load_framework', lambda: '框架'),
        mock.patch.object(rg, 'load_theses', lambda: '论点'),
        mock.patch.object(rg, 'load_technical_notes', lambda: ''),
        mock.patch.object(rg, 'load_news_summary', lambda: ''),
        mock.patch.object(rg, 'load_previous_report', lambda: ''),
    ]
    if status_writer is not None:
        patches.append(mock.patch.object(rg, 'write_report_status', status_writer))
    with contextlib.ExitStack() as stack:
        for p in patches:
            stack.enter_context(p)
        try:
            quiet(rg.generate_weekly_report)
            code = 0
        except SystemExit as e:
            code = e.code
    return code, glm, applied, os.path.join(td, 'out', 'weekly')


with tempfile.TemporaryDirectory() as td:
    # 11: 先发布合格PASS报告,再以Gate B FAIL重跑→合格报告不得被覆盖/破坏
    build_research_day(td)
    code1, glm1, applied1, out = run_flow(td, gate_b='PASS')
    rep = os.path.join(out, f'weekly_report_{DAY}.md')
    check("前置: PASS报告已发布", code1 == 0 and os.path.exists(rep))
    published_bytes = open(rep, 'rb').read()
    code2, glm2, applied2, _ = run_flow(td, gate_b='FAIL')
    unval = os.path.join(out, f'weekly_report_{DAY}_UNVALIDATED.md')
    status = json.load(open(os.path.join(out, f'report_status_{DAY}.json')))
    check("FAIL重跑: 合格报告原文件逐字节未动",
          open(rep, 'rb').read() == published_bytes)
    check("FAIL重跑: 失败产物入_UNVALIDATED(不占正式名)", os.path.exists(unval))
    check("FAIL重跑: 主status仍为已发布合格(不被失败尝试破坏)",
          status['final_quality'] == 'PASS' and status['published'] is True
          and status['report_digest'] == rp.digest_file(rep), str(status))
    unval_status = json.load(open(os.path.join(out, f'report_status_{DAY}_UNVALIDATED.json')))
    check("FAIL重跑: 失败详情写入UNVALIDATED状态(指向真实文件)",
          unval_status['final_quality'] == 'FAIL'
          and unval_status['report_file'] == os.path.basename(unval)
          and os.path.exists(unval_status['report_path']), str(unval_status))
    check("FAIL重跑: 不回写长期状态", applied2 == [], str(applied2))
    check("FAIL重跑: exit 3", code2 == 3, f"exit={code2}")
with tempfile.TemporaryDirectory() as td:
    # 12: Gate B校验器抛异常→候选按未验证隔离,合格报告不受损
    build_research_day(td)
    code1, _, _, out = run_flow(td, gate_b='PASS')
    rep = os.path.join(out, f'weekly_report_{DAY}.md')
    published_bytes = open(rep, 'rb').read()
    code2, _, applied2, _ = run_flow(td, validator_exc=RuntimeError('校验器崩溃(SYNTHETIC)'))
    check("校验器异常: exit 3+合格报告未动+候选隔离",
          code2 == 3 and open(rep, 'rb').read() == published_bytes
          and os.path.exists(os.path.join(out, f'weekly_report_{DAY}_UNVALIDATED.md')),
          f"exit={code2}")
    check("校验器异常: 不回写长期状态", applied2 == [])
    status = json.load(open(os.path.join(out, f'report_status_{DAY}_UNVALIDATED.json')))
    check("校验器异常: 状态记录指向真实存在的文件",
          os.path.exists(status['report_path']) and status['final_quality'] == 'FAIL',
          str(status))
with tempfile.TemporaryDirectory() as td:
    # 13: report_status写入失败→不得发布无状态记录的正式报告
    build_research_day(td)

    def bad_writer(*a, **kw):
        print('⛔ (mock)report_status写入失败')
        return False

    code, _, applied, out = run_flow(td, gate_b='PASS', status_writer=bad_writer)
    check("status写入失败: exit 3(不得静默记成功)",
          code == 3, f"exit={code}")
    check("status写入失败: 正式报告未发布",
          not os.path.exists(os.path.join(out, f'weekly_report_{DAY}.md')))
    check("status写入失败: 候选隔离为_UNVALIDATED(不伪装合格)",
          os.path.exists(os.path.join(out, f'weekly_report_{DAY}_UNVALIDATED.md')))
    check("status写入失败: 不回写长期状态", applied == [])
with tempfile.TemporaryDirectory() as td:
    # 状态写入失败且当日已有合格报告→合格报告仍不受损
    build_research_day(td)
    code1, _, _, out = run_flow(td, gate_b='PASS')
    rep = os.path.join(out, f'weekly_report_{DAY}.md')
    published_bytes = open(rep, 'rb').read()

    def bad_writer(*a, **kw):
        return False

    code2, _, _, _ = run_flow(td, gate_b='DEGRADED', status_writer=bad_writer)
    check("status写入失败(已有合格): 合格报告未动+exit 3",
          code2 == 3 and open(rep, 'rb').read() == published_bytes, f"exit={code2}")

# ═══ 14. 月报/季报无门禁入口→UNVALIDATED草稿(FIX-07) ═════════════
print("\n── 14. 月报/季报UNVALIDATED(FIX-07)")


class _GLMDraft:
    def __init__(self):
        self.calls = 0

    def __call__(self, system_prompt, user_prompt, max_tokens=32000, timeout=900):
        self.calls += 1
        return '## 月度复盘正文(SYNTHETIC)\n\n' + '逐序列回顾。' * 100


with tempfile.TemporaryDirectory() as td:
    os.makedirs(os.path.join(td, 'output', 'weekly'), exist_ok=True)
    os.makedirs(os.path.join(td, 'data', 'daily'), exist_ok=True)
    os.makedirs(os.path.join(td, 'config'), exist_ok=True)
    json.dump({'theses': []}, open(os.path.join(td, 'config', 'thesis.json'), 'w'))
    mdir = os.path.join(td, 'output', 'monthly')
    os.makedirs(mdir, exist_ok=True)
    # 已有"合格"月报占位(历史遗留正式名)——UNVALIDATED输出不得覆盖
    qualified = os.path.join(mdir, 'monthly_review_202609.md')
    with open(qualified, 'w', encoding='utf-8') as f:
        f.write('# 合格月报(历史正式产物)')
    glm = _GLMDraft()
    with mock.patch.object(mr, 'ROOT_DIR', td), \
         mock.patch.object(mr, 'DATA_DIR', os.path.join(td, 'data', 'daily')), \
         mock.patch.object(mr, 'OUTPUT_DIR', mdir), \
         mock.patch.object(rg, 'load_prompt', lambda *a, **kw: '系统提示'), \
         mock.patch.object(rg, '_call_glm', glm), \
         mock.patch.object(sys, 'argv', ['monthly_review.py', '--month', '202609']):
        try:
            quiet(mr.main)
            code = 0
        except SystemExit as e:
            code = e.code
    draft = os.path.join(mdir, 'monthly_review_202609_UNVALIDATED.md')
    check("月报输出=UNVALIDATED草稿(显式文件名)", code == 0 and os.path.exists(draft),
          f"exit={code}")
    check("月报不覆盖既有合格正式文件",
          open(qualified, encoding='utf-8').read() == '# 合格月报(历史正式产物)')
    text = open(draft, encoding='utf-8').read()
    check("月报草稿含可见UNVALIDATED横幅(非仅注释)",
          'UNVALIDATED 研究草稿' in text and text.index('UNVALIDATED 研究草稿') < 400)
    check("月报历史装配能力保留(monthly_data数据块落盘)",
          os.path.exists(os.path.join(mdir, 'monthly_data_202609.md')))
with tempfile.TemporaryDirectory() as td:
    os.makedirs(os.path.join(td, 'output', 'weekly'), exist_ok=True)
    os.makedirs(os.path.join(td, 'data', 'daily'), exist_ok=True)
    os.makedirs(os.path.join(td, 'config'), exist_ok=True)
    json.dump({'theses': []}, open(os.path.join(td, 'config', 'thesis.json'), 'w'))
    qdir = os.path.join(td, 'output', 'quarterly')
    os.makedirs(qdir, exist_ok=True)
    qualified_q = os.path.join(qdir, 'quarterly_outlook_2026Q3.md')
    with open(qualified_q, 'w', encoding='utf-8') as f:
        f.write('# 合格季报(历史正式产物)')
    glm = _GLMDraft()
    with mock.patch.object(qo, 'ROOT_DIR', td), \
         mock.patch.object(qo, 'DATA_DIR', os.path.join(td, 'data', 'daily')), \
         mock.patch.object(qo, 'OUTPUT_DIR', qdir), \
         mock.patch.object(rg, 'load_prompt', lambda *a, **kw: '系统提示'), \
         mock.patch.object(rg, '_call_glm', glm), \
         mock.patch.object(sys, 'argv', ['quarterly_outlook.py', '--quarter', '2026Q3']):
        try:
            quiet(qo.main)
            code = 0
        except SystemExit as e:
            code = e.code
    draft = os.path.join(qdir, 'quarterly_outlook_2026Q3_UNVALIDATED.md')
    check("季报输出=UNVALIDATED草稿", code == 0 and os.path.exists(draft), f"exit={code}")
    check("季报不覆盖既有合格正式文件",
          open(qualified_q, encoding='utf-8').read() == '# 合格季报(历史正式产物)')
    check("季报草稿含可见UNVALIDATED横幅",
          'UNVALIDATED 研究草稿' in open(draft, encoding='utf-8').read())
    check("季报历史装配能力保留(quarterly_data数据块)",
          os.path.exists(os.path.join(qdir, 'quarterly_data_2026Q3.md')))
with tempfile.TemporaryDirectory() as td:
    # 季报月报索引: UNVALIDATED草稿不得混入合格索引冒充正式产物
    mdir = os.path.join(td, 'output', 'monthly')
    os.makedirs(mdir, exist_ok=True)
    for name in ('monthly_review_202609.md', 'monthly_review_202609_UNVALIDATED.md'):
        with open(os.path.join(mdir, name), 'w', encoding='utf-8') as f:
            f.write('# x')
    os.makedirs(os.path.join(td, 'data', 'daily'), exist_ok=True)
    with mock.patch.object(qo, 'ROOT_DIR', td):
        block, preview = quiet(qo.build_data_block, '2026Q3',
                               data_dir=os.path.join(td, 'data', 'daily'),
                               views_path=os.path.join(td, 'missing_views.json'))
    check("季报月报索引排除UNVALIDATED草稿",
          'monthly_review_202609.md' in block
          and 'monthly_review_202609_UNVALIDATED.md' not in block)

# ═══ 汇总 ═════════════════════════════════════════════════════════
print("\n" + "=" * 64)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 64)
sys.exit(1 if FAIL else 0)
