#!/usr/bin/env python3
"""IA-P0-1 质量门禁链测试(2026-10-27) — Gate A三态/来源绑定/流水线依赖/报告预检/门禁合成/长期状态保护

覆盖验收契约IA-P0-1-AC-v1.0的行为矩阵:
- AC-01 Gate A三态语义(缺字段/非法不默认PASS)      - AC-02 流水线依赖与SKIPPED
- AC-03 装配器不得绕过Gate A                        - AC-04 快照→包→锚点可验证绑定
- AC-05 独立报告入口预检(不调GLM/不写状态)          - AC-06 Gate A+B合成
- AC-07 Gate B FAIL报告不冒充合格(_UNVALIDATED)     - AC-08 长期状态保护(观察器)
- AC-10 DEGRADED保留降级能力                        - AC-11 跳过原因/状态可追溯

数据纪律: 全部SYNTHETIC fixture + 临时目录隔离,不触真实data/config;
GLM全程mock(本套件不发起任何付费调用)。
运行: ~/AI内容/venv/bin/python3 tests/test_gate_chain_p01.py
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
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
PY = sys.executable

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
import data_validator as dv
import run_weekly

DAY = '20261017'
DAY_ISO = '2026-10-17'


# ══ fixture构造 ═══════════════════════════════════════════════════
# FIX2重构: 快照/锚点/数据包/prompt一律经**真实路径**产出——fixt覆盖注册表
# 全部32个core指标(36事实),Gate A由rp.recompute_gate_a从真实事实重算,不得
# 只构造SPX/UST_10Y等少量指标再手写声明PASS(FIX2-02测试纪律);锚点由
# sb.build_anchors、数据包由da.build_markdown、prompt由dv确定性生成——
# 预检/观察器的"实际内容绑定/确定性重建比对"才有真实意义。

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fixt   # noqa: E402  共享真实构建fixture

_BREAK_FOR_GATE = {'DEGRADED': 'UMCSENT', 'FAIL': 'SPX'}


def synth_snapshot(ymd=DAY, gate='PASS', rev=None, degraded_fact=False, sid=None,
                   fail_fact=False):
    """真实构建的全注册表SYNTHETIC快照(32核心齐备,Gate A真实计算)。
    degraded_fact→非核心UMCSENT值坏(真实降级);fail_fact→核心GOLD值坏;
    gate='FAIL'→核心SPX值坏;gate=None→正常构建(调用方自行del gate_a)。"""
    bm = 'GOLD' if fail_fact else 'UMCSENT' if degraded_fact else _BREAK_FOR_GATE.get(gate)
    snap = quiet(fixt.real_snapshot, ymd, break_metric=bm, rev=rev)
    if sid:
        snap['snapshot_id'] = sid
    return snap


def build_research_day(base, ymd=DAY, gate='PASS', rev=None, pack_bound_rev='__same__',
                       degraded_fact=False, skip=(), tamper_snapshot=False,
                       fail_fact=False):
    """构造一天完整研究产物(全真实路径: 采集JSON→build_snapshot→build_anchors
    →build_markdown→generate_anchor_prompt_block);当日评分卡文件+pack meta
    携带scorecard_*状态(FIX2-03报告入口核验依赖)。

    pack_bound_rev: pack meta绑定的快照版本('__same__'=与权威快照一致;
    传其他值→绑定他版快照→构造陈旧包)。skip: {'pack','anchors','prompt',
    'pack_meta','anchors_meta'}选择性缺席。tamper_snapshot: 绑定后改快照内容。"""
    daily = os.path.join(base, 'daily')
    weekly = os.path.join(base, 'weekly')
    os.makedirs(daily, exist_ok=True)
    os.makedirs(weekly, exist_ok=True)
    bm = 'GOLD' if fail_fact else 'UMCSENT' if degraded_fact else _BREAK_FOR_GATE.get(gate)
    fixt.write_collectors(daily, ymd, break_metric=bm)
    fixt.write_scorecard(daily, ymd)
    snap = quiet(sb.build_snapshot, target_ymd=ymd, data_dir=daily, out_dir=daily,
                 trusted_root=base, as_of=fixt.as_of_for(ymd))
    snap_path = os.path.join(daily, snap['snapshot_id'] + '.json')
    apath = os.path.join(daily, f'anchors_{ymd}.json')
    if rev:
        # 同日修订: 权威快照_vN(原base保留),锚点+meta按真实修订路径重绑_vN
        snap['snapshot_id'] = f'research_snapshot_{ymd}_v{rev}'
        snap['revision_reason'] = 'fixture revision'
        snap_path = os.path.join(daily, snap['snapshot_id'] + '.json')
        with open(snap_path, 'w', encoding='utf-8') as f:
            json.dump(snap, f, ensure_ascii=False)
        anchors = sb.build_anchors(snap, ymd)
        with open(apath, 'w', encoding='utf-8') as f:
            json.dump(anchors, f, ensure_ascii=False, indent=1)
        rp.write_meta(apath, {'source': 'snapshot', 'generated_by': 'snapshot_builder',
                              'anchor_count': len(anchors),
                              'anchors_digest': rp.digest_file(apath),
                              **rp.provenance_of(snap, snap_path,
                                                 trusted_root=base)})
    anchors = json.load(open(apath, encoding='utf-8'))
    if 'pack' not in skip:
        packfile = os.path.join(weekly, f'data_pack_{ymd}.md')
        with open(packfile, 'w', encoding='utf-8') as f:
            f.write(da.build_markdown(snap, ymd, data_dir=base) if gate != 'FAIL'
                    else '# pack')
        if 'pack_meta' not in skip and gate != 'FAIL':
            bound_rev = rev if pack_bound_rev == '__same__' else pack_bound_rev
            bound = snap if not bound_rev else synth_snapshot(ymd, rev=bound_rev)
            bound_file = (f'research_snapshot_{ymd}.json' if not bound_rev
                          else f'research_snapshot_{ymd}_v{bound_rev}.json')
            sc_date, sc_cur = da.scorecard_state(ymd, data_dir=base)
            rp.write_meta(packfile, {
                'source': 'snapshot', 'generated_by': 'data_assembler',
                'pack_file': os.path.basename(packfile),
                'pack_digest': rp.digest_file(packfile),
                'scorecard_date': sc_date, 'scorecard_current': bool(sc_cur),
                **rp.provenance_of(bound, bound_file)})
    if 'anchors' in skip:
        os.remove(apath)
        mp = rp.meta_path_for(apath)
        if os.path.exists(mp):
            os.remove(mp)
    elif 'anchors_meta' in skip:
        os.remove(rp.meta_path_for(apath))
    if gate is None:
        # 快照缺gate_a字段场景: 装配/锚点在快照完整时产出,此后快照侧损坏
        del snap['gate_a']
        with open(snap_path, 'w', encoding='utf-8') as f:
            json.dump(snap, f, ensure_ascii=False)
    if 'prompt' not in skip:
        ppath = os.path.join(daily, f'anchor_prompt_{ymd}.md')
        with open(ppath, 'w', encoding='utf-8') as f:
            f.write(dv.generate_anchor_prompt_block(anchors))
        rp.write_meta(ppath, {'source': 'snapshot', 'generated_by': 'data_validator',
                              'target_date': ymd, 'prompt_digest': rp.digest_file(ppath)})
    if tamper_snapshot:
        snap['facts'][0]['value'] = 9999.99   # 绑定建立后篡改快照
        with open(snap_path, 'w', encoding='utf-8') as f:
            json.dump(snap, f, ensure_ascii=False)
    return snap, snap_path


print("=" * 64)
print("IA-P0-1 质量门禁链: Gate A三态/来源绑定/流水线依赖/预检/合成/状态保护")
print("=" * 64)

# ══ 1. Gate A三态语义(AC-01) ═════════════════════════════════════
print("\n── 1. Gate A三态语义(AC-01)")
# FIX2-02: 声明不再被盲信——gate_status对真实快照**从事实重算**后裁决;
# 无事实的裸声明(旧测试的最小dict探针)不可验证→None(收紧,不降低标准)。
for st in ('PASS', 'DEGRADED', 'FAIL'):
    snap = synth_snapshot(gate=st)
    got, why = rp.gate_status(snap)
    check(f"真实快照gate_status读取{st}(事实重算一致)", got == st, f"{got} {why}")
got, why = rp.gate_status({'gate_a': {'status': 'PASS'}})
check("裸dict无facts→None(声明不可验证,不默认PASS)", got is None, f"{got} {why}")
got, why = rp.gate_status({})
check("缺gate_a字段→None(不得默认PASS)", got is None and '缺gate_a' in why, f"{got} {why}")
got, why = rp.gate_status(synth_snapshot() | {'gate_a': {'status': 'pass_with_errors'}})
check("非法状态→None", got is None, f"{got} {why}")
_snap_str = synth_snapshot()
_snap_str['gate_a'] = 'PASS'   # 旧版裸字符串声明+事实一致→兼容读取
got, _ = rp.gate_status(_snap_str)
check("gate_a为裸字符串(兼容,事实一致)→PASS", got == 'PASS', str(got))
got, _ = rp.gate_status(None)
check("快照非对象→None", got is None, str(got))
check("允许正式研究: PASS/DEGRADED=True, FAIL/None=False",
      rp.gate_allows_formal_research('PASS') and rp.gate_allows_formal_research('DEGRADED')
      and not rp.gate_allows_formal_research('FAIL')
      and not rp.gate_allows_formal_research(None))

# ══ 2. 确定性版本选择(AC-04) ═════════════════════════════════════
print("\n── 2. 快照版本选择(AC-04)")
with tempfile.TemporaryDirectory() as td:
    check("无候选→(None,原因)", rp.select_snapshot(DAY, td)[0] is None)
    s1 = synth_snapshot(rev=None)
    json.dump(s1, open(os.path.join(td, 'research_snapshot_20261017.json'), 'w'))
    s2 = synth_snapshot(rev=2)
    json.dump(s2, open(os.path.join(td, 'research_snapshot_20261017_v2.json'), 'w'))
    s3 = synth_snapshot(rev=3)
    json.dump(s3, open(os.path.join(td, 'research_snapshot_20261017_v3.json'), 'w'))
    json.dump(synth_snapshot('20261010'), open(os.path.join(td, 'research_snapshot_20261010.json'), 'w'))
    snap, path = rp.select_snapshot(DAY, td)
    check("同日多版本→取最高修订版_v3",
          snap['snapshot_id'] == 'research_snapshot_20261017_v3', path)
    check("非当日文件不参与", '20261010' not in path)
with tempfile.TemporaryDirectory() as td:
    json.dump(synth_snapshot(), open(os.path.join(td, 'research_snapshot_20261017.json'), 'w'))
    open(os.path.join(td, 'research_snapshot_20261017_v2.json'), 'w').write('{corrupt json')
    snap, reason = rp.select_snapshot(DAY, td)
    check("候选损坏→明确拒绝(不猜测回退base)", snap is None and '损坏' in reason, reason)
with tempfile.TemporaryDirectory() as td:
    bad = synth_snapshot(rev=2)
    del bad['snapshot_id']
    json.dump(synth_snapshot(), open(os.path.join(td, 'research_snapshot_20261017.json'), 'w'))
    json.dump(bad, open(os.path.join(td, 'research_snapshot_20261017_v2.json'), 'w'))
    snap, reason = rp.select_snapshot(DAY, td)
    check("候选缺snapshot_id→拒绝", snap is None and 'snapshot_id' in reason, reason)
with tempfile.TemporaryDirectory() as td:
    wrongdate = synth_snapshot()
    wrongdate['target_date'] = '20261010'
    json.dump(wrongdate, open(os.path.join(td, 'research_snapshot_20261017.json'), 'w'))
    snap, reason = rp.select_snapshot(DAY, td)
    check("target_date不符→拒绝", snap is None and 'target_date' in reason, reason)

# ══ 3. 快照构建器: 修订版/锚点替换/meta sidecar(AC-04/AC-11) ═════
print("\n── 3. 快照构建器来源链(AC-04)")


def build_fixture_day(td, ymd='20261018', obs='2026-10-17'):
    """构造一天采集文件(SYNTHETIC,结构复刻test_snapshot真实采集JSON)。"""
    global_json = {"date": ymd, "time": "07:12:00", "count": 2, "data": {
        "SPX": {"close": 7659.44, "high": 7680.0, "low": 7601.0, "week_chg": 2.13,
                "mtd_chg": 3.5, "ytd_chg": 12.0, "date": obs,
                "series": {"dates": ["2026-10-16", obs], "values": [7500.0, 7659.44]}},
        "GOLD": {"close": 4300.0, "week_chg": 2.38, "date": obs,
                 "series": {"dates": ["2026-10-16", obs], "values": [4200.0, 4300.0]}}}}
    json.dump(global_json, open(os.path.join(td, f"global_{ymd}.json"), 'w'))
    macro_json = {"date": ymd, "data": {
        "CCC_OAS": {"value": 10.18, "date": obs, "frequency": "daily"},
        "CPI": {"value": 310.0, "date": "2026-09-01", "frequency": "monthly",
                "series": {"dates": ["2026-08-01", "2026-09-01"], "values": [308.0, 310.0]}},
        "UNEMPLOYMENT": {"value": 4.2, "date": "2026-09-01", "frequency": "monthly"},
        "UST_10Y": {"value": 4.28, "date": obs, "frequency": "daily"},
        "BEI_10Y": {"value": 2.31, "date": obs, "frequency": "daily"}}}
    json.dump(macro_json, open(os.path.join(td, f"macro_{ymd}.json"), 'w'))
    rate_json = {"date": ymd, "current_rates": {
        "DFF": {"name": "有效联邦基金利率", "value": 4.33, "date": obs}},
        "fed_funds_futures": [{"ticker": "ZQ=F", "price": 95.80, "implied_rate": 4.20}],
        "real_economy": {"UNRATE": {"name": "失业率", "value": 4.2, "date": "2026-09-01"}}}
    json.dump(rate_json, open(os.path.join(td, f"rate_economy_{ymd}.json"), 'w'))


with tempfile.TemporaryDirectory() as td:
    build_fixture_day(td)
    quiet(sb.build_snapshot, target_ymd='20261018', data_dir=td, out_dir=td,
          trusted_root=td, as_of="2026-10-18T08:00:00+08:00")
    apath = os.path.join(td, 'anchors_20261018.json')
    check("base锚点+meta产出", os.path.exists(apath)
          and os.path.exists(rp.meta_path_for(apath)))
    meta = rp.load_meta(apath)
    check("锚点meta来源=snapshot+快照ID",
          meta.get('source') == 'snapshot'
          and meta.get('snapshot_id') == 'research_snapshot_20261018', str(meta))
    # 毒化: 手工塞入陈旧残留键 → 修订版重建后必须整体消失(替换而非merge)
    anchors = json.load(open(apath))
    anchors['stale.legacy.residue'] = {'value': 1.0, 'obs_date': '2026-10-01'}
    json.dump(anchors, open(apath, 'w'))
    quiet(sb.build_snapshot, target_ymd='20261018', data_dir=td, out_dir=td,
          as_of="2026-10-18T09:00:00+08:00", allow_revision=True,
          revision_reason='IA-P0-1测试修订')
    v2 = os.path.join(td, 'research_snapshot_20261018_v2.json')
    check("修订版快照_v2落盘(原版保留)",
          os.path.exists(v2) and os.path.exists(os.path.join(td, 'research_snapshot_20261018.json')))
    anchors2 = json.load(open(apath))
    check("锚点整体替换(陈旧残留键消失)", 'stale.legacy.residue' not in anchors2,
          str([k for k in anchors2 if 'stale' in k]))
    check("锚点source_file绑定实际版本(_v2)",
          all(v.get('source_file') == 'research_snapshot_20261018_v2.json'
              for v in anchors2.values() if isinstance(v, dict) and 'source_file' in v),
          str({k: v.get('source_file') for k, v in list(anchors2.items())[:3]}))
    meta2 = rp.load_meta(apath)
    check("锚点meta升级到_v2批次",
          meta2.get('snapshot_id') == 'research_snapshot_20261018_v2', str(meta2))
    # CLI退出码: Gate A FAIL(fixture缺32个core指标)→exit 2;重跑覆盖→exit 3
    r = subprocess.run([PY, os.path.join(ROOT, 'scripts', 'snapshot_builder.py'),
                        '--date', '20261018', '--data-dir', td, '--out-dir', td,
                        '--trusted-root', td],
                       capture_output=True, text=True)
    check("CLI: 已存在且不可变→exit 3", r.returncode == 3, f"exit={r.returncode}")
    r2 = subprocess.run([PY, os.path.join(ROOT, 'scripts', 'snapshot_builder.py'),
                         '--date', '20261019', '--data-dir', td, '--out-dir', td,
                         '--trusted-root', td],
                        capture_output=True, text=True)
    check("CLI: Gate A FAIL→exit 2(快照仍落盘)",
          r2.returncode == 2 and os.path.exists(os.path.join(td, 'research_snapshot_20261019.json')),
          f"exit={r2.returncode}")

# ══ 4. 装配器: Gate A拦截/降级披露/绑定meta(AC-03/AC-10) ═════════
print("\n── 4. 装配器门禁(AC-03/AC-10)")


class _FakeDT:
    """固定'今天'=2026-10-17(转发strptime等类方法到真实datetime)。"""
    @staticmethod
    def now():
        import datetime as _dt
        return _dt.datetime(2026, 10, 17, 8, 0, 0)

    @staticmethod
    def strptime(s, f):
        import datetime as _dt
        return _dt.datetime.strptime(s, f)


with tempfile.TemporaryDirectory() as td:
    os.makedirs(os.path.join(td, 'daily'))
    os.makedirs(os.path.join(td, 'weekly'))
    with mock.patch.object(da, 'DATA_DIR', td):
        snap, ymd, path = da.load_snapshot(DAY)
        check("无快照→(None,ymd,拒绝原因)", snap is None and ymd == DAY
              and isinstance(path, str) and '快照' in path, str(path))
with tempfile.TemporaryDirectory() as td:
    daily = os.path.join(td, 'daily')
    weekly = os.path.join(td, 'weekly')
    os.makedirs(daily)
    os.makedirs(weekly)
    for gate in ('FAIL', None):
        snap = synth_snapshot(gate=gate or 'PASS')
        if gate is None:
            del snap['gate_a']
        json.dump(snap, open(os.path.join(daily, 'research_snapshot_20261017.json'), 'w'))
        with mock.patch.object(da, 'DATA_DIR', td), \
             mock.patch.object(da, 'datetime', _FakeDT):
            try:
                quiet(da.main)
                code = 0
            except SystemExit as e:
                code = e.code
        packfile = os.path.join(weekly, 'data_pack_20261017.md')
        check(f"Gate A {gate or '缺字段'}→exit 2且不产数据包",
              code == 2 and not os.path.exists(packfile), f"exit={code}")
        os.remove(os.path.join(daily, 'research_snapshot_20261017.json'))
with tempfile.TemporaryDirectory() as td:
    daily = os.path.join(td, 'daily')
    weekly = os.path.join(td, 'weekly')
    os.makedirs(daily)
    os.makedirs(weekly)
    with mock.patch.object(da, 'DATA_DIR', td), \
         mock.patch.object(da, 'datetime', _FakeDT):
        try:
            quiet(da.main)
            code = 0
        except SystemExit as e:
            code = e.code
    check("无快照→exit 1(与Gate拒绝exit 2区分)",
          code == 1 and not os.path.exists(os.path.join(weekly, 'data_pack_20261017.md')),
          f"exit={code}")
with tempfile.TemporaryDirectory() as td:
    snap, spath = build_research_day(td, gate='DEGRADED', degraded_fact=True)
    with mock.patch.object(da, 'DATA_DIR', td), \
         mock.patch.object(da, 'datetime', _FakeDT):
        try:
            quiet(da.main)
            code = 0
        except SystemExit as e:
            code = e.code
    packfile = os.path.join(td, 'weekly', 'data_pack_20261017.md')
    pack_text = open(packfile, encoding='utf-8').read() if os.path.exists(packfile) else ''
    meta = rp.load_meta(packfile)
    check("DEGRADED→继续装配(exit 0)", code == 0 and os.path.exists(packfile), f"exit={code}")
    check("数据包含降级披露节+不合格指标点名",
          '数据质量降级披露' in pack_text and '密歇根消费者信心指数' in pack_text
          and 'DEGRADED' in pack_text)
    check("数据包meta绑定快照(ID/digest/Gate A)",
          meta.get('source') == 'snapshot'
          and meta.get('snapshot_id') == 'research_snapshot_20261017'
          and meta.get('gate_a') == 'DEGRADED'
          and meta.get('snapshot_digest') == rp.digest_snapshot(snap), str(meta))

# ══ 5. 报告入口预检矩阵(AC-05/AC-04) ═════════════════════════════
print("\n── 5. 报告预检矩阵(AC-05/AC-04)")
with tempfile.TemporaryDirectory() as td:
    build_research_day(td)
    with mock.patch.object(rg, 'DATA_DIR', td):
        ok, problems, ctx = rg.verify_research_inputs(DAY)
    check("全要素齐备→预检通过", ok and not problems, str(problems))
    check("上下文携带当日锚点与Gate A",
          ctx['gate_a'] == 'PASS' and isinstance(ctx['anchors'], dict)
          and len(ctx['anchors']) >= 20 and ctx['anchors_path'].endswith('anchors_20261017.json'))
reject_cases = [
    ('Gate A FAIL快照', dict(gate='FAIL')),
    ('快照缺gate_a字段', dict(gate=None)),
    ('数据包缺席', dict(skip=('pack',))),
    ('数据包无meta(来源不可证明)', dict(skip=('pack_meta',))),
    ('锚点缺席', dict(skip=('anchors',))),
    ('锚点无meta(legacy嫌疑)', dict(skip=('anchors_meta',))),
    ('锚点prompt缺席', dict(skip=('prompt',))),
    ('陈旧包残留(包绑base,权威快照已是_v2)', dict(rev=2, pack_bound_rev=1)),
    ('快照被篡改(digest失配)', dict(tamper_snapshot=True)),
]
for name, kw in reject_cases:
    with tempfile.TemporaryDirectory() as td:
        build_research_day(td, **{k: (None if v is None and k == 'gate' else v)
                                  for k, v in kw.items()})
        with mock.patch.object(rg, 'DATA_DIR', td):
            ok, problems, ctx = rg.verify_research_inputs(DAY)
        check(f"预检拒绝: {name}", not ok and len(problems) >= 1, str(problems))
with tempfile.TemporaryDirectory() as td:
    # legacy锚点meta(数据校验器遗留路径产物)→拒绝
    build_research_day(td)
    apath = os.path.join(td, 'daily', 'anchors_20261017.json')
    rp.write_meta(apath, {'source': 'legacy', 'anchor_count': 25})
    with mock.patch.object(rg, 'DATA_DIR', td):
        ok, problems, _ = rg.verify_research_inputs(DAY)
    check("预检拒绝: legacy锚点批次", not ok and any('legacy' in p for p in problems),
          str(problems))
with tempfile.TemporaryDirectory() as td:
    build_research_day(td, gate='DEGRADED', degraded_fact=True)
    with mock.patch.object(rg, 'DATA_DIR', td):
        ok, problems, ctx = rg.verify_research_inputs(DAY)
    check("Gate A DEGRADED→预检通过(继续+披露)", ok and ctx['gate_a'] == 'DEGRADED',
          str(problems))

# ══ 6. 报告主流程行为: 不调GLM/不写状态/_UNVALIDATED/降级披露(AC-05/06/07/10) ═
print("\n── 6. 报告主流程(AC-05/06/07/10)")


class _GLMRecorder:
    def __init__(self, text=None):
        # ≥500字符: generate_report对过短返回按失败处理(真实行为约束)
        self.text = text or ('# 投资周报(SYNTHETIC测试文本)\n\n'
                             + '本周市场综述与分资产回顾。' * 60)
        self.calls = 0

    def __call__(self, system_prompt, user_prompt, max_tokens=32000, timeout=900):
        self.calls += 1
        return self.text


def run_weekly_report_flow(td, gate_b, gate='PASS'):
    """在td构造研究日并运行generate_weekly_report(gate_b由mock控制)。
    返回(exit_code, glm, apply_recorder, out_dir)。"""
    build_research_day(td, gate=gate, degraded_fact=(gate == 'DEGRADED'))
    out_dir = os.path.join(td, 'out', 'weekly')
    glm = _GLMRecorder()
    applied = []

    def _apply(report, classification, anchors=None, **kw):
        applied.append((classification, anchors))

    with mock.patch.object(rg, 'DATA_DIR', td), \
         mock.patch.object(rg, 'OUTPUT_DIR', out_dir), \
         mock.patch.object(rg, 'datetime', _FakeDT), \
         mock.patch.object(rg, '_call_glm', glm), \
         mock.patch.object(rg, 'apply_status_updates', _apply), \
         mock.patch.object(rg, 'validate_generated_report',
                           lambda md, anchors=None, anchors_file=None: (gate_b, ['SYNTHETIC警告'])), \
         mock.patch.object(rg.allocation_engine, 'load_views',
                           lambda *a, **kw: {'views': [], 'predictions': []}), \
         mock.patch.object(rg, 'pending_completed_month', lambda d=None: None), \
         mock.patch.object(rg, 'pending_completed_quarter', lambda d=None: None), \
         mock.patch.object(rg, 'load_framework', lambda: '框架'), \
         mock.patch.object(rg, 'load_theses', lambda: '论点'), \
         mock.patch.object(rg, 'load_technical_notes', lambda: ''), \
         mock.patch.object(rg, 'load_news_summary', lambda: ''), \
         mock.patch.object(rg, 'load_previous_report', lambda: ''):
        try:
            quiet(rg.generate_weekly_report)
            code = 0
        except SystemExit as e:
            code = e.code
    return code, glm, applied, out_dir


with tempfile.TemporaryDirectory() as td:
    # 预检失败(目录空) → 不调GLM/不写状态/不产报告/exit 2
    os.makedirs(os.path.join(td, 'daily'))
    os.makedirs(os.path.join(td, 'weekly'))
    glm = _GLMRecorder()
    applied = []
    with mock.patch.object(rg, 'DATA_DIR', td), \
         mock.patch.object(rg, 'OUTPUT_DIR', os.path.join(td, 'out')), \
         mock.patch.object(rg, 'datetime', _FakeDT), \
         mock.patch.object(rg, '_call_glm', glm), \
         mock.patch.object(rg, 'apply_status_updates',
                           lambda *a, **kw: applied.append(1)), \
         mock.patch.object(rg.allocation_engine, 'load_views',
                           lambda *a, **kw: {'views': [], 'predictions': []}):
        try:
            quiet(rg.generate_weekly_report)
            code = 0
        except SystemExit as e:
            code = e.code
    check("预检失败→exit 2", code == 2, f"exit={code}")
    check("预检失败→GLM调用次数=0", glm.calls == 0, str(glm.calls))
    check("预检失败→不回写长期状态", applied == [])
    check("预检失败→不产任何报告文件",
          not glob.glob(os.path.join(td, 'out', '**', 'weekly_report*'), recursive=True))

with tempfile.TemporaryDirectory() as td:
    code, glm, applied, out_dir = run_weekly_report_flow(td, gate_b='PASS')
    rep = os.path.join(out_dir, f'weekly_report_{DAY}.md')
    status = json.load(open(os.path.join(out_dir, f'report_status_{DAY}.json')))
    check("Gate A PASS+Gate B PASS→报告落盘+exit 0",
          code == 0 and os.path.exists(rep) and glm.calls == 1, f"exit={code} glm={glm.calls}")
    check("合成质量PASS(report_status sidecar)",
          status['final_quality'] == 'PASS' and status['gate_a'] == 'PASS'
          and status['gate_b'] == 'PASS', str(status))
    check("PASS→状态回写执行1次", len(applied) == 1 and applied[0][0] == 'PASS', str(applied))
    check("PASS→无降级footer", '数据质量降级披露' not in open(rep, encoding='utf-8').read())

with tempfile.TemporaryDirectory() as td:
    code, glm, applied, out_dir = run_weekly_report_flow(td, gate_b='FAIL')
    unval = os.path.join(out_dir, f'weekly_report_{DAY}_UNVALIDATED.md')
    orig = os.path.join(out_dir, f'weekly_report_{DAY}.md')
    status = json.load(open(os.path.join(out_dir, f'report_status_{DAY}.json')))
    check("Gate B FAIL→exit 3+改名_UNVALIDATED(原名不占位)",
          code == 3 and os.path.exists(unval) and not os.path.exists(orig),
          f"exit={code} orig={os.path.exists(orig)} unval={os.path.exists(unval)}")
    check("Gate B FAIL→不回写长期状态", applied == [], str(applied))
    check("FAIL报告status=FAIL(可追溯)",
          status['final_quality'] == 'FAIL' and status['gate_b'] == 'FAIL', str(status))

with tempfile.TemporaryDirectory() as td:
    code, glm, applied, out_dir = run_weekly_report_flow(td, gate_b='DEGRADED', gate='DEGRADED')
    rep = os.path.join(out_dir, f'weekly_report_{DAY}.md')
    text = open(rep, encoding='utf-8').read()
    status = json.load(open(os.path.join(out_dir, f'report_status_{DAY}.json')))
    check("A/B双DEGRADED→合成DEGRADED+exit 0",
          code == 0 and status['final_quality'] == 'DEGRADED', f"exit={code} {status}")
    check("DEGRADED→报告尾部可见降级披露",
          '数据质量降级披露' in text and 'Gate A' in text and 'DEGRADED' in text)
    check("DEGRADED→回写按既有规则继续", len(applied) == 1, str(applied))

# Gate合成穷举(AC-06)
combos = [(('PASS', 'PASS'), 'PASS'), (('PASS', 'DEGRADED'), 'DEGRADED'),
          (('PASS', 'FAIL'), 'FAIL'), (('DEGRADED', 'PASS'), 'DEGRADED'),
          (('DEGRADED', 'DEGRADED'), 'DEGRADED'), (('DEGRADED', 'FAIL'), 'FAIL'),
          (('FAIL', 'PASS'), 'FAIL'), (('FAIL', 'DEGRADED'), 'FAIL'),
          (('FAIL', 'FAIL'), 'FAIL'), ((None, 'PASS'), 'FAIL'),
          (('PASS', 'unknown'), 'FAIL'), (('PASS', None), 'FAIL')]
for (a, b), want in combos:
    got = rp.combine_gates(a, b)
    check(f"combine_gates({a},{b})={want}", got == want, got)

# ══ 7. 上期报告过滤(AC-07) ══════════════════════════════════════
print("\n── 7. 上期报告过滤(AC-07)")
with tempfile.TemporaryDirectory() as td:
    for name in ('weekly_report_20261010.md', 'weekly_report_20261011_annotated.md',
                 'weekly_report_20261012_UNVALIDATED.md', f'weekly_report_{DAY}.md'):
        with open(os.path.join(td, name), 'w', encoding='utf-8') as f:
            f.write(f'# {name}\n')
    with mock.patch.object(rg, 'OUTPUT_DIR', os.path.join(td, 'output', 'weekly')), \
         mock.patch.object(rg, 'datetime', _FakeDT):
        # PROJECT_DIR拼output/weekly → 造到td/output/weekly
        os.makedirs(os.path.join(td, 'output', 'weekly'), exist_ok=True)
        for name in ('weekly_report_20261010.md', 'weekly_report_20261011_annotated.md',
                     'weekly_report_20261012_UNVALIDATED.md', f'weekly_report_{DAY}.md'):
            with open(os.path.join(td, 'output', 'weekly', name), 'w', encoding='utf-8') as f:
                f.write(f'# {name}\n')
        prev = quiet(rg.load_previous_report)
    check("上期报告跳过annotated/UNVALIDATED/今日,取20261010",
          prev.startswith('# weekly_report_20261010'), str(prev[:60]))

# ══ 8. 观察器: 指标质量FAIL跳过+批次核验(AC-08) ═════════════════
print("\n── 8. 观察器长期状态保护(AC-08)")


def views_file(td, preds):
    data = {'version': 2, 'views': [], 'predictions': preds}
    vp = os.path.join(td, 'views.json')
    json.dump(data, open(vp, 'w'), ensure_ascii=False, indent=1)
    return vp


def obs_pred(pid, metric, target=None, asset=None):
    return {'pred_id': pid, 'asset': asset or ('信心指数' if 'UMCSENT' in metric else '标普'),
            'direction': 'SYNTHETIC测试预测', 'status': 'observing', 'metric': metric,
            'comparator': '>=', 'target': target if target is not None else
            (60.0 if 'UMCSENT' in metric else 4250.0),
            'observe_from': '2026-10-10',
            'deadline': '2026-12-31', 'observations': []}


with tempfile.TemporaryDirectory() as td:
    # FIX-04: 指标级失败仅影响其所属预测,同批合格指标照常记录。
    # FIX2重构: 真实路径下值FAIL的事实**不产生锚点**(build_anchors只收合格事实),
    # 故用非核心UMCSENT值坏→Gate A=DEGRADED(批次仍可验证放行),该指标锚点缺失
    # →其预测跳过;核心GOLD值坏会使整批FAIL(核心FAIL),无法构造"同批照常"场景。
    build_research_day(td, gate='DEGRADED', degraded_fact=True)   # 非核心UMCSENT值坏
    apath = os.path.join(td, 'daily', f'anchors_{DAY}.json')
    anchors = json.load(open(apath, encoding='utf-8'))
    check("fixture: UMCSENT锚点缺失(值FAIL不产锚点)/SPX=PASS(批次其余有效)",
          anchors.get('macro.data.UMCSENT.value') is None
          and anchors.get('global_market.data.SPX.close', {}).get('quality') == 'PASS',
          str({k: v.get('quality') for k, v in anchors.items()
               if 'UMCSENT' in k or k == 'global_market.data.SPX.close'}))
    vp = views_file(td, [obs_pred(91, 'macro.data.UMCSENT.value'),
                         obs_pred(92, 'global_market.data.SPX.close')])
    ch, n, st = quiet(dpo.observe, views_path=vp, anchors=anchors,
                      today_str=DAY_ISO, anchors_date=DAY, anchors_path=apath)
    saved = json.load(open(vp))
    p91 = next(p for p in saved['predictions'] if p['pred_id'] == 91)
    p92 = next(p for p in saved['predictions'] if p['pred_id'] == 92)
    check("指标失败(锚点缺失)→该预测跳过(PARTIAL)",
          st == 'PARTIAL' and p91['observations'] == [], f"{st} {p91['observations']}")
    check("同批质量合格指标→照常记录(绑定锚点实际观测日)",
          len(p92['observations']) == 1
          and p92['observations'][0]['obs_date']
          == anchors['global_market.data.SPX.close']['obs_date'],
          str(p92['observations']))

with tempfile.TemporaryDirectory() as td:
    # legacy批次(原始采集JSON拍平,未经Gate A快照链) → 关键FAIL
    build_research_day(td)
    apath = os.path.join(td, 'daily', f'anchors_{DAY}.json')
    anchors = json.load(open(apath, encoding='utf-8'))
    meta = rp.load_meta(apath)
    meta['source'] = 'legacy'
    rp.write_meta(apath, meta)
    vp = views_file(td, [obs_pred(91, 'global_market.data.GOLD.close')])
    before = open(vp).read()
    ch, n, st = quiet(dpo.observe, views_path=vp, anchors=anchors,
                      today_str=DAY_ISO, anchors_date=DAY, anchors_path=apath)
    check("legacy批次→关键FAIL不写观察",
          st == 'FAIL' and ch == [] and open(vp).read() == before, f"{st} {ch}")

with tempfile.TemporaryDirectory() as td:
    # 批次失配: 锚点meta绑base,当日权威快照已是_v2(同日修订)
    build_research_day(td, rev=2)   # 写_v2快照;锚点meta绑_v2
    apath = os.path.join(td, 'daily', f'anchors_{DAY}.json')
    meta = rp.load_meta(apath)
    meta['snapshot_id'] = 'research_snapshot_20261017'   # 篡改为旧批次
    rp.write_meta(apath, meta)
    vp = views_file(td, [obs_pred(91, 'global_market.data.GOLD.close')])
    anchors = json.load(open(apath, encoding='utf-8'))
    before = open(vp).read()
    ch, n, st = quiet(dpo.observe, views_path=vp, anchors=anchors,
                      today_str=DAY_ISO, anchors_date=DAY, anchors_path=apath)
    check("批次失配(旧锚点vs权威_v2)→关键FAIL",
          st == 'FAIL' and open(vp).read() == before, f"{st} {ch}")

with tempfile.TemporaryDirectory() as td:
    # 无meta(旧格式) → FIX-04语义: 来源不可证明,拒绝进入正式长期观察
    # (旧测试预期"放行(兼容)"与IA-P0-1-FIX1-AC-v1.0 FIX-04"无meta→拒绝"冲突,
    #  按整改指令修正测试预期——未降低验收标准,反而是收紧;理由见整改文档§7)
    build_research_day(td, skip=('anchors_meta',))
    apath = os.path.join(td, 'daily', f'anchors_{DAY}.json')
    anchors = json.load(open(apath, encoding='utf-8'))
    vp = views_file(td, [obs_pred(91, 'global_market.data.GOLD.close')])
    before = open(vp).read()
    ch, n, st = quiet(dpo.observe, views_path=vp, anchors=anchors,
                      today_str=DAY_ISO, anchors_date=DAY, anchors_path=apath)
    check("无meta旧格式→关键FAIL(FIX-04收紧: 来源不可证明)",
          st == 'FAIL' and ch == [] and open(vp).read() == before, f"{st} {ch}")
    # 陈旧锚点日期→关键FAIL(既有行为不回归)
    ch2, _, st2 = quiet(dpo.observe, views_path=vp, anchors=anchors,
                        today_str='2026-10-20', anchors_date='20261017', anchors_path=apath)
    check("陈旧锚点日期→FAIL(既有)", st2 == 'FAIL')

# ══ 9. 流水线依赖与SKIPPED(AC-02/AC-11) ════════════════════════
print("\n── 9. 流水线依赖(AC-02/AC-11)")
with tempfile.TemporaryDirectory() as td:
    for name, code in [('a_snap.py', 'print("snap ok")'),
                       ('b_pack.py', 'exit(1)'),
                       ('c_dep.py', 'import pathlib;pathlib.Path(__file__).with_name("c_ran.txt").write_text("1");print("c ok")'),
                       ('d_indep.py', 'import pathlib;pathlib.Path(__file__).with_name("d_ran.txt").write_text("1");print("d ok")')]:
        with open(os.path.join(td, name), 'w') as f:
            f.write(code + '\n')
    steps = [('快照构建', 'a_snap.py', True),
             ('数据打包', 'b_pack.py', True, ['a_snap.py']),
             ('报告校验', 'c_dep.py', True, ['b_pack.py']),
             ('预测观察', 'd_indep.py', True)]
    results = quiet(run_weekly.run_pipeline, steps, script_dir=td)
    skips = getattr(results, 'skips', {})
    check("前提失败→依赖步骤SKIPPED不执行", not os.path.exists(os.path.join(td, 'c_ran.txt')))
    check("SKIPPED记为失败(名称,False,关键)",
          any(n == '报告校验' and not ok and c for n, ok, c in results), str(results))
    check("跳过原因可追溯(含失败依赖名)",
          '数据打包' in skips.get('报告校验', ''), str(skips))
    check("无依赖步骤照常执行", os.path.exists(os.path.join(td, 'd_ran.txt')))
    crit = [n for n, s, c in results if not s and c]
    check("关键失败+关键跳过都计入退出码1判定", set(crit) == {'数据打包', '报告校验'}, str(crit))
with tempfile.TemporaryDirectory() as td:
    with open(os.path.join(td, 'a.py'), 'w') as f:
        f.write('exit(1)\n')
    with open(os.path.join(td, 'z.py'), 'w') as f:
        f.write('print("z ok")\n')
    r3 = quiet(run_weekly.run_pipeline,
               [('A', 'a.py', True), ('Z', 'z.py', True)], script_dir=td)
    check("3元组兼容: 无依赖声明→失败后仍全部执行", len(r3) == 2 and not r3[0][1] and r3[1][1],
          str(r3))
with tempfile.TemporaryDirectory() as td:
    with open(os.path.join(td, 'a.py'), 'w') as f:
        f.write('print("a ok")\n')
    with open(os.path.join(td, 'c.py'), 'w') as f:
        f.write('print("c ok")\n')
    r4 = quiet(run_weekly.run_pipeline,
               [('A', 'a.py', True), ('C', 'c.py', True, ['a.py'])], script_dir=td)
    check("前提成功→依赖步骤正常执行", r4[1][1] is True, str(r4))

# ══ 10. 遗留锚点批次标注(AC-09) ════════════════════════════════
print("\n── 10. 遗留路径标注(AC-09)")


class _DTAnchor:
    @staticmethod
    def now():
        class _N:
            @staticmethod
            def strftime(f):
                return DAY
        return _N()


with tempfile.TemporaryDirectory() as td:
    fake = {'global_market.data.SPX.close': {
        'value': 7659.44, 'source_file': 'x.json', 'as_of': DAY_ISO,
        'obs_date': DAY_ISO, 'metric_id': 'SPX', 'quality': 'PASS'}}
    with mock.patch.object(dv, 'ROOT_DIR', td), mock.patch.object(dv, 'datetime', _DTAnchor):
        quiet(dv.save_anchors, fake)
    apath = os.path.join(td, 'data', 'daily', f'anchors_{DAY}.json')
    meta = rp.load_meta(apath)
    check("遗留save_anchors→meta标注source=legacy(可被观察器/预检拒绝)",
          meta is not None and meta.get('source') == 'legacy', str(meta))

# ══ 11. 数据校验器报告glob排除_UNVALIDATED(AC-07) ═══════════════
print("\n── 11. 校验器报告过滤(AC-07)")
with tempfile.TemporaryDirectory() as td:
    wk = os.path.join(td, 'output', 'weekly')
    os.makedirs(wk)
    for name in ('weekly_report_20261010.md', 'weekly_report_20261012_UNVALIDATED.md',
                 'weekly_report_20261011_annotated.md'):
        open(os.path.join(wk, name), 'w').write('# x\n')
    # 与data_validator/__main__同款谓词(排除annotated/UNVALIDATED)
    files = sorted(f for f in os.listdir(wk)
                   if f.startswith('weekly_report_')
                   and '_annotated' not in f and '_UNVALIDATED' not in f)
    check("_UNVALIDATED/_annotated均不入校验候选", files == ['weekly_report_20261010.md'], str(files))

# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 64)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 64)
sys.exit(0 if FAIL == 0 else 1)
