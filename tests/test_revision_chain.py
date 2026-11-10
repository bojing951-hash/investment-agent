#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P0-2 --allow-revision 全链转发测试(Skill 化 v1.1, 2026-11-09)。

历史缺陷: run_weekly.py 零参数解析,ia_cli 转发的 --allow-revision 被静默
吞掉;run_step 恒零参调子脚本 → snapshot_builder 永远收不到修订旗标,
同日重跑必被不可变保护拒绝(step9 exit 3 → 流水线 exit 1),且流水线无任何
同日重跑成功路径。

三层验证(零网络/零真实采集,SYNTHETIC fixture 结构复刻真实采集 JSON):
① run_step extra_args 透传(记录器桩实证子进程 argv);
② run_weekly main() 参数路由(--allow-revision/--revision-reason →
   extra_args_by_script['snapshot_builder.py'],无旗标时零参不变);
③ 沙箱端到端: 全真 run_weekly+snapshot_builder,其余 12 步 exit-0 桩,
   当日 SYNTHETIC 全 core fixture(Gate A=DEGRADED)——首跑建 base →
   同日重跑无旗标→非0+报不可变 → 带旗标→_v2 生成 rc=0 → select_snapshot
   选中 _v2 → reason 落 revision_reason → sources sha256 摘要随修订版完整。
"""
import datetime as dt
import hashlib
import importlib.util
import json
import os
import shutil
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


def run_pipeline_cmd(cwd, *argv):
    return subprocess.run([sys.executable, 'run_weekly.py', *argv], cwd=cwd,
                          capture_output=True, text=True, timeout=300)


# ══ [1] run_step extra_args 透传 ══
print("═" * 60)
print("① run_step extra_args → 子进程 argv")
print("═" * 60)
with tempfile.TemporaryDirectory() as td:
    rec = os.path.join(td, 'recorder.py')
    argv_file = os.path.join(td, 'argv.json')
    with open(rec, 'w', encoding='utf-8') as fh:
        fh.write("import json,sys\n"
                 f"json.dump({{'argv': sys.argv}}, open({argv_file!r}, 'w'))\n")
    spec = importlib.util.spec_from_file_location('rw_step', os.path.join(ROOT, 'run_weekly.py'))
    rw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rw)
    ok = rw.run_step('记录步骤', 'recorder.py', script_dir=td,
                     extra_args=['--allow-revision', '--revision-reason', '链路测试'])
    got = json.load(open(argv_file))['argv']
    check("run_step extra_args 追加到子进程命令行",
          ok and got == [rec, '--allow-revision', '--revision-reason', '链路测试'], str(got))
    ok = rw.run_step('零参步骤', 'recorder.py', script_dir=td)
    got = json.load(open(argv_file))['argv']
    check("extra_args 缺省=零参(接口兼容)", ok and got == [rec], str(got))

# ══ [2] main() 参数路由(猴补 run_pipeline,零副作用) ══
print("═" * 60)
print("② run_weekly main() 参数路由")
print("═" * 60)
with tempfile.TemporaryDirectory() as td:
    shutil.copy(os.path.join(ROOT, 'run_weekly.py'), os.path.join(td, 'run_weekly.py'))
    spec = importlib.util.spec_from_file_location('rw_main', os.path.join(td, 'run_weekly.py'))
    rw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rw)
    captured = {}

    def fake_pipeline(steps, script_dir=None, extra_args_by_script=None):
        captured['extra'] = extra_args_by_script
        return rw.PipelineResults([(s[0], True, s[2]) for s in steps])

    rw.run_pipeline = fake_pipeline
    real_argv = sys.argv
    try:
        sys.argv = ['run_weekly.py']
        rw.main()
        check("无旗标 → extra_args_by_script=None(既有行为不变)",
              captured['extra'] is None)
        sys.argv = ['run_weekly.py', '--allow-revision']
        rw.main()
        check("--allow-revision → 仅快照步骤收旗标",
              captured['extra'] == {'snapshot_builder.py': ['--allow-revision']},
              str(captured['extra']))
        sys.argv = ['run_weekly.py', '--allow-revision', '--revision-reason', '补充采集']
        rw.main()
        check("--revision-reason 随旗标透传",
              captured['extra'] == {'snapshot_builder.py': ['--allow-revision',
                                                            '--revision-reason', '补充采集']},
              str(captured['extra']))
        sys.argv = ['run_weekly.py', '--revision-reason', '孤立原因']
        rw.main()
        check("孤立 --revision-reason(无修订旗标)不透传(builder 语义一致)",
              captured['extra'] is None, str(captured['extra']))
    finally:
        sys.argv = real_argv

# ia_cli 侧转发
import ia_cli
args = ia_cli.build_parser().parse_args(
    ['update', '--yes', '--allow-revision', '--revision-reason', '夜间修订'])
check("ia_cli update 解析 --revision-reason", args.revision_reason == '夜间修订')

# ══ [3] 沙箱端到端 ══
print("═" * 60)
print("③ 沙箱端到端: 全真 run_weekly + snapshot_builder")
print("═" * 60)


def synthetic_full_core_day(daily_dir, ymd, obs):
    """SYNTHETIC 全 core 采集日(结构复刻真实采集 JSON;数值全虚构)。"""
    spx_dates = ['2026-09-30', '2026-10-09', obs]
    global_json = {"date": ymd, "data": {
        "SPX": {"close": 7659.44, "week_chg": 2.13, "date": obs,
                "series": {"dates": spx_dates, "values": [7400.0, 7500.0, 7659.44]}},
        "GOLD": {"close": 4300.0, "week_chg": 2.38, "date": obs},
        "NDX": {"close": 25000.0, "week_chg": 1.0, "date": obs},
        "VIX": {"close": 15.0, "week_chg": -2.0, "date": obs},
        "DXY": {"close": 104.0, "week_chg": 0.3, "date": obs},
        "WTI_F": {"close": 72.0, "week_chg": -1.0, "date": obs},
        "BTC": {"close": 91000.0, "week_chg": 2.0, "date": obs},
    }}
    nfp_dates = ['2025-%02d-01' % m for m in range(1, 13)] + ['2026-%02d-01' % m for m in range(1, 10)]
    nfp_vals = [float(140000 + i * 80) for i in range(len(nfp_dates))]
    macro_json = {"date": ymd, "data": {
        "CCC_OAS": {"value": 10.18, "date": obs, "frequency": "daily"},
        "CPI": {"value": 300.0, "date": "2026-09-01", "frequency": "monthly"},
        "UNEMPLOYMENT": {"value": 4.2, "date": "2026-09-01", "frequency": "monthly"},
        "UST_10Y": {"value": 4.28, "date": obs, "frequency": "daily"},
        "BEI_10Y": {"value": 2.31, "date": obs, "frequency": "daily"},
        "UST_2Y": {"value": 3.85, "date": obs, "frequency": "daily"},
        "HY_OAS": {"value": 3.2, "date": obs, "frequency": "daily"},
        "TIPS_10Y": {"value": 1.97, "date": obs, "frequency": "daily"},
        "FED_FUNDS": {"value": 4.33, "date": "2026-09-01", "frequency": "monthly"},
        "CORE_CPI": {"value": 315.5, "date": "2026-09-01", "frequency": "monthly"},
        "CORE_PCE": {"value": 113.0, "date": "2026-09-01", "frequency": "monthly"},
        "NFP": {"value": nfp_vals[-1], "date": "2026-09-01", "frequency": "monthly",
                "series": {"dates": nfp_dates, "values": nfp_vals}},
        "ICSA": {"value": 218000.0, "date": obs, "frequency": "weekly"},
    }, "derived": {}}
    china_json = {"date": ymd, "data": {}, "indices": {
        "上证指数": {"name": "上证指数", "close": 3716.28, "week_chg": -2.13, "date": obs},
        "深证成指": {"name": "深证成指", "close": 11800.0, "week_chg": 0.5, "date": obs},
        "恒生指数": {"name": "恒生指数", "close": 24186.83, "date": obs},
        "恒生国企指数": {"name": "恒生国企指数", "close": 8600.0, "week_chg": 0.2, "date": obs},
    }, "ah_premium": {"close": 128.56, "date": obs},
        "turnover": {"date": ymd, "sh_amount_billion": 8000.0, "sz_amount_billion": 9000.0,
                     "total_amount_billion": 17000.0}}
    rate_json = {"date": ymd, "current_rates": {
        "DFF": {"name": "有效联邦基金利率", "value": 4.33, "date": obs},
        "DFEDTARU": {"name": "目标区间上限", "value": 4.50, "date": obs},
        "DFEDTARL": {"name": "目标区间下限", "value": 4.25, "date": obs}},
        "fed_funds_futures": [
            {"ticker": "ZQ=F", "name": "FF期货主力", "price": 95.80, "implied_rate": 4.20}],
        "real_economy": {
            "UNRATE": {"name": "失业率", "value": 4.2, "date": "2026-09-01", "freq": "月度"}}}
    for name, payload in (('global', global_json), ('macro', macro_json),
                          ('china', china_json), ('rate_economy', rate_json)):
        with open(os.path.join(daily_dir, f'{name}_{ymd}.json'), 'w', encoding='utf-8') as fh:
            json.dump(payload, fh)


STUB_STEPS = ['global_market_collector', 'china_market_collector', 'macro_collector',
              'news_collector', 'rate_expectations', 'japan_rate_collector',
              'jp_market_collector', 'ea_market_collector', 'macro_scorecard',
              'correlation_calculator', 'data_assembler', 'data_validator']

# CI时间炸弹修复②(2026-11-11,热修): snapshot_builder 以北京时区定日
# (build_snapshot 内 datetime.now(TZ_BJ)),而本测试原用运行机本地日
# (GitHub runner=UTC)。UTC 16:00-23:59 期间两地日期分叉,builder 写
# research_snapshot_{BJ日}.json 而测试找 {UTC日}.json → L213
# FileNotFoundError(主CI 42850982644 于 16:05Z 首次踩中;此前 14 次全在
# 00:00-15:59Z 窗口内两地同日故绿)。预存缺陷非 C8 回归——修法=测试
# 对齐快照权威口径(生产机为北京时区时本就一致):
TZ_BJ = dt.timezone(dt.timedelta(hours=8), name='Asia/Shanghai')
today = dt.datetime.now(TZ_BJ).date()
obs = today - dt.timedelta(days=1)
while obs.weekday() >= 5:
    obs -= dt.timedelta(days=1)
ymd = today.strftime('%Y%m%d')

with tempfile.TemporaryDirectory() as td:
    proj = os.path.join(td, 'proj')
    os.makedirs(os.path.join(proj, 'data', 'daily'))
    shutil.copy(os.path.join(ROOT, 'run_weekly.py'), proj)
    shutil.copytree(os.path.join(ROOT, 'scripts'), os.path.join(proj, 'scripts'))
    shutil.copytree(os.path.join(ROOT, 'config'), os.path.join(proj, 'config'))
    for name in STUB_STEPS:  # 其余 12 步换成 exit-0 桩(链路测试不验采集本身)
        with open(os.path.join(proj, 'scripts', name + '.py'), 'w', encoding='utf-8') as fh:
            fh.write('import sys\nsys.exit(0)\n')
    synthetic_full_core_day(os.path.join(proj, 'data', 'daily'), ymd, obs.isoformat())

    daily = os.path.join(proj, 'data', 'daily')
    base = os.path.join(daily, f'research_snapshot_{ymd}.json')
    v2 = os.path.join(daily, f'research_snapshot_{ymd}_v2.json')

    r1 = run_pipeline_cmd(proj)
    check("首跑 rc=0 且 base 快照生成", r1.returncode == 0 and os.path.isfile(base),
          f"rc={r1.returncode}")

    r2 = run_pipeline_cmd(proj)
    check("① 同日重跑无旗标 → rc=1 且公示不可变拒绝",
          r2.returncode == 1 and '不可变' in r2.stdout and '返回码: 3' in r2.stdout,
          f"rc={r2.returncode}")
    check("① 重跑无旗标不产生新版本文件", not os.path.exists(v2))
    base_bytes_unchanged = open(base, 'rb').read()

    r3 = run_pipeline_cmd(proj, '--allow-revision', '--revision-reason', '链路修订测试')
    check("② 带旗标 → rc=0 且 _v2 生成",
          r3.returncode == 0 and os.path.isfile(v2), f"rc={r3.returncode}")
    check("② 原版 base 保留未动", open(base, 'rb').read() == base_bytes_unchanged)
    v2snap = json.load(open(v2, encoding='utf-8'))
    check("③ select_snapshot 选中 _v2(最高修订版=权威)",
          __import__('research_provenance').select_snapshot(ymd, daily)[1] == v2)
    check("④ reason 透传进 revision_reason 字段",
          v2snap.get('revision_reason') == '链路修订测试', str(v2snap.get('revision_reason')))
    check("④ _v2 内部 snapshot_id 与文件名版本一致",
          v2snap['snapshot_id'] == f'research_snapshot_{ymd}_v2')
    dig_ok = all(
        hashlib.sha256(open(os.path.join(daily, st['file']), 'rb').read()).hexdigest()
        == st['sha256']
        for st in v2snap['sources_status'].values() if st.get('sha256'))
    check("⑤ sources sha256 摘要随修订版完整(逐通道实算一致)", dig_ok
          and sum(1 for st in v2snap['sources_status'].values() if st.get('sha256')) >= 4)

print()
print("═" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("═" * 60)
sys.exit(0 if FAIL == 0 else 1)
