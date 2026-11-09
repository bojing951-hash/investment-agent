# -*- coding: utf-8 -*-
"""
Charter6-P0 采集窗口扩展 回归测试(2026-11-09;A2 §4-P0 规格对应)

覆盖四块:
  一、macro_collector FRED observation_start 参数化(纯函数逐值,含env覆盖/
     非法回落/最小钳制/闰日);结构锁=源码不再含硬编码'2025-01-01'
  二、global_market_collector period 参数化(默认'10y',env 覆盖;结构锁=
     调用点不再硬编码"1y",auto_adjust=True 仍显式)
  三、data_retention 保留策略(90天全量+月度gzip归档+旧档清理;研究层文件
     不动;dry_run;幂等;缺目录零动作)——全部临时目录手造档,期望清单手写
  四、长序列回归(~2500点)——窗口扩到10年后序列长度量级变化,变化计算与
     区间变动须端值正确;期望值全部手算(输入为手造等差/等比序列)
运行: python3 tests/test_charter6_p0_windows.py(脚本式,与CI一致;勿用pytest收集)
"""
import gzip
import os
import re
import shutil
import sys
import tempfile
from datetime import date, datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

PASS = 0
FAIL = 0


def check(name, cond, detail=''):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")


def with_env(kv, fn):
    """临时设置环境变量执行 fn,退出时恢复原状(键序敏感场景由调用方自管)。"""
    old = {}
    for k, v in kv.items():
        old[k] = os.environ.get(k)
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v
    try:
        return fn()
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


print("=" * 64)
print("一、macro_collector observation_start 参数化")
print("=" * 64)
import macro_collector as mc  # noqa: E402

T0 = datetime(2026, 11, 9, 10, 30)
# 手算: 2026-11-09 往前N年(同月同日)
with_env({'MACRO_HISTORY_YEARS': None},
         lambda: check("默认10年: 2026-11-09→2016-11-09",
                       mc.macro_observation_start(T0) == '2016-11-09',
                       mc.macro_observation_start(T0)))
with_env({'MACRO_HISTORY_YEARS': '25'},
         lambda: check("env=25: →2001-11-09",
                       mc.macro_observation_start(T0) == '2001-11-09'))
with_env({'MACRO_HISTORY_YEARS': '3'},
         lambda: check("env=3: →2023-11-09",
                       mc.macro_observation_start(T0) == '2023-11-09'))
with_env({'MACRO_HISTORY_YEARS': 'abc'},
         lambda: check("env非法'abc'回落10年: →2016-11-09",
                       mc.macro_observation_start(T0) == '2016-11-09'))
with_env({'MACRO_HISTORY_YEARS': '0'},
         lambda: check("env=0钳制最小1年: →2025-11-09",
                       mc.macro_observation_start(T0) == '2025-11-09'))
with_env({'MACRO_HISTORY_YEARS': ''},
         lambda: check("env空串按未配置: →2016-11-09",
                       mc.macro_observation_start(T0) == '2016-11-09'))
# 闰日: 2024-02-29 往前10年=2014-02-29不存在→取2014-03-01(窗口多含一天)
with_env({'MACRO_HISTORY_YEARS': None},
         lambda: check("闰日2024-02-29默认10年→2014-03-01",
                       mc.macro_observation_start(datetime(2024, 2, 29)) == '2014-03-01',
                       mc.macro_observation_start(datetime(2024, 2, 29))))
mc_src = open(os.path.join(ROOT, 'scripts', 'macro_collector.py'),
              encoding='utf-8').read()
check("结构锁: 硬编码'2025-01-01'已移除", "'2025-01-01'" not in mc_src)
check("结构锁: fetch_all_macro 使用 macro_observation_start()",
      'observation_start=obs_start' in mc_src
      and 'obs_start = macro_observation_start()' in mc_src)

print("=" * 64)
print("二、global_market_collector period 参数化")
print("=" * 64)
import global_market_collector as gmc  # noqa: E402  (导入含代理探测打印,属预期)

with_env({'GLOBAL_HISTORY_PERIOD': None},
         lambda: check("默认'10y'", gmc.global_history_period() == '10y'))
with_env({'GLOBAL_HISTORY_PERIOD': '5y'},
         lambda: check("env='5y'覆盖", gmc.global_history_period() == '5y'))
with_env({'GLOBAL_HISTORY_PERIOD': 'max'},
         lambda: check("env='max'覆盖", gmc.global_history_period() == 'max'))
with_env({'GLOBAL_HISTORY_PERIOD': '  '},
         lambda: check("env空白回落'10y'", gmc.global_history_period() == '10y'))
g_src = open(os.path.join(ROOT, 'scripts', 'global_market_collector.py'),
             encoding='utf-8').read()
check("结构锁: 调用点不再硬编码 period=\"1y\"",
      'period="1y"' not in g_src and "period='1y'" not in g_src)
check("结构锁: __main__ 调用 fetch_all() 无参(走env默认)",
      bool(re.search(r'^\s*all_data, failed = fetch_all\(\)\s*$', g_src, re.M)))
check("结构锁: auto_adjust=True 仍显式(复权口径唯一)",
      'auto_adjust=True' in g_src)

print("=" * 64)
print("三、data_retention 保留策略(90天全量+月度gzip归档)")
print("=" * 64)
import data_retention as dr  # noqa: E402

NOW = datetime(2026, 11, 9, 12, 0)
# 手造档(now=2026-11-09,keep_days=90→cutoff=2026-08-11):
#   近窗(≥cutoff): macro_20261015.json / global_20261105.md → 保留
#   2026年3月 macro 三份 → 月度代表=20260331 归档,0301/0320 删除
#   2026年4月 macro 一份 → 20260402 归档
#   2025年12月 global md → 20251231 归档;2025年6月 china → 归档
#   2025年1月 japan 两份 → 代表=20250121 归档,20250120 删除
#   研究层/同日多版本档: research_snapshot_/anchors_/anchor_prompt_/
#   correlation_/macro_*_v2 → 一律不动
LAYOUT = {
    'macro_20261015.json': '近窗',
    'global_20261105.md': '近窗',
    'macro_20260301.json': '旧-3月非代表',
    'macro_20260320.json': '旧-3月非代表',
    'macro_20260331.json': '旧-3月代表',
    'macro_20260402.json': '旧-4月代表',
    'global_20251231.md': '旧-12月代表',
    'china_20250630.json': '旧-6月代表',
    'japan_20250120.json': '旧-1月非代表',
    'japan_20250121.json': '旧-1月代表',
    'research_snapshot_20250101.json': '研究层',
    'anchors_20250101.json': '研究层',
    'anchor_prompt_20250101.md': '研究层',
    'correlation_20250101.md': '研究层',
    'macro_20261108_v2.json': '同日多版本',
}
EXP_KEPT = ['global_20261105.md', 'macro_20261015.json']
EXP_ARCHIVED = ['china_20250630.json', 'global_20251231.md',
                'japan_20250121.json', 'macro_20260331.json',
                'macro_20260402.json']
EXP_DELETED = ['japan_20250120.json', 'macro_20260301.json',
               'macro_20260320.json']
EXP_UNTOUCHED = ['anchor_prompt_20250101.md', 'anchors_20250101.json',
                 'correlation_20250101.md', 'macro_20261108_v2.json',
                 'research_snapshot_20250101.json']


def make_daily_dir():
    td = tempfile.mkdtemp(prefix='ia_ret_')
    daily = os.path.join(td, 'daily')
    os.makedirs(os.path.join(daily, 'archive'))
    # 模拟既往归档产物(上一轮已归档的代表档)——本轮不得动它
    with open(os.path.join(daily, 'archive', 'macro_20251031.json.gz'),
              'wb') as f:
        f.write(gzip.compress(b'{"prev": true}'))
    for name in LAYOUT:
        with open(os.path.join(daily, name), 'w', encoding='utf-8') as f:
            f.write('{"stub": 1}')
    return daily


daily = make_daily_dir()
rep = dr.prune_daily_archives(daily, keep_days=90, now=NOW)
check("报告: 近窗保留清单(手写期望)",
      sorted(rep['kept']) == EXP_KEPT, rep['kept'])
check("报告: 月度代表归档清单(手写期望)",
      sorted(rep['archived']) == EXP_ARCHIVED, rep['archived'])
check("报告: 旧档删除清单(手写期望)",
      sorted(rep['deleted']) == EXP_DELETED, rep['deleted'])
check("报告: 非采集族不动清单(手写期望)",
      sorted(rep['untouched']) == EXP_UNTOUCHED, rep['untouched'])
for n in EXP_KEPT:
    check(f"文件系统: {n} 原样保留",
          os.path.isfile(os.path.join(daily, n)))
for n in EXP_ARCHIVED:
    gz = os.path.join(daily, 'archive', n + '.gz')
    check(f"文件系统: {n} → archive/{n}.gz 且原档移除",
          os.path.isfile(gz) and not os.path.exists(os.path.join(daily, n)))
with open(os.path.join(daily, 'archive', 'macro_20260331.json.gz'), 'rb') as f:
    body = gzip.decompress(f.read())
check("gzip 内容无损(=原档字节)", body == b'{"stub": 1}')
for n in EXP_DELETED:
    check(f"文件系统: {n} 已删除",
          not os.path.exists(os.path.join(daily, n))
          and not os.path.exists(os.path.join(daily, 'archive', n + '.gz')))
for n in EXP_UNTOUCHED:
    check(f"文件系统: 研究层/多版本 {n} 未动",
          os.path.isfile(os.path.join(daily, n)))
check("既往归档产物不被重复处理",
      os.path.isfile(os.path.join(daily, 'archive', 'macro_20251031.json.gz')))
# 幂等: 第二次运行零动作
rep2 = dr.prune_daily_archives(daily, keep_days=90, now=NOW)
check("幂等: 第二轮归档/删除均为空",
      rep2['archived'] == [] and rep2['deleted'] == [], rep2)
check("幂等: 第二轮近窗清单不变", sorted(rep2['kept']) == EXP_KEPT)

# dry_run: 只报告不动手
daily_d = make_daily_dir()
repd = dr.prune_daily_archives(daily_d, keep_days=90, now=NOW, dry_run=True)
check("dry_run: 报告与实跑清单一致",
      sorted(repd['archived']) == EXP_ARCHIVED
      and sorted(repd['deleted']) == EXP_DELETED
      and sorted(repd['kept']) == EXP_KEPT)
unchanged = all(os.path.isfile(os.path.join(daily_d, n)) for n in LAYOUT)
# archive/ 内只允许预置的既往归档件,不得新增任何 .gz
arc = set(os.listdir(os.path.join(daily_d, 'archive')))
check("dry_run: 零文件系统改动", unchanged and arc == {'macro_20251031.json.gz'},
      arc)

# 缺目录: 零动作不报错
rep3 = dr.prune_daily_archives(os.path.join(tempfile.gettempdir(),
                                            'ia_ret_nonexistent_xyz'),
                               now=NOW)
check("缺目录: 零动作不抛异常",
      rep3['kept'] == [] and rep3['archived'] == [] and rep3['deleted'] == [])
shutil.rmtree(os.path.dirname(daily), ignore_errors=True)
shutil.rmtree(os.path.dirname(daily_d), ignore_errors=True)

# run_weekly 接线: 14步含保留策略(非关键)
rw_src = open(os.path.join(ROOT, 'run_weekly.py'), encoding='utf-8').read()
check("run_weekly: 保留策略已接线(非关键)",
      '("15/15 日档保留策略(90天全量+月度归档)", "data_retention.py", False)'
      in rw_src)
check("run_weekly: 15步分母一致(1/15..15/15)",
      len(re.findall(r'"\d{1,2}/15 ', rw_src)) == 15)

print("=" * 64)
print("四、长序列回归(~2500点,手算期望)")
print("=" * 64)
# (a) 日频2500点: 相邻观测恒隔7天 → week_chg 基准=上一观测(自然日滞后7∈[5,10])
#     值 v_i = 100 + 0.25i(手算: v2498=724.5, v2499=724.75, 差=0.25)
N = 2500
last_day = date(2026, 11, 6)
d_daily = [(last_day - timedelta(days=7 * (N - 1 - i))).isoformat()
           for i in range(N)]
v_daily = [100.0 + 0.25 * i for i in range(N)]
out = mc.compute_series_changes(d_daily, v_daily, 'daily',
                                unit=('rate', '%(测试)'))
check("2500点日频: prev=724.5(手算)", out.get('prev') == 724.5, out.get('prev'))
check("2500点日频: week_chg=0.25百分点(手算)",
      out.get('week_chg') == 0.25, out.get('week_chg'))
check("2500点日频: 基准=上一观测日", out.get('week_chg_from') == d_daily[-2])
check("2500点日频: rate类不给百分比变化",
      'week_pct' not in out and out.get('week_chg_unit') == '百分点(1个百分点=100bp)')

# (b) 月频120点(10年): v_i = 50 + 1.7i(手算: v118=250.6, v119=252.3)
#     mom=1.7; yoy 基准=首个自然日滞后∈[330,400]的观测=2026-01-01(i=108,
#     距2026-12-01滞后334天;11月、10月...依次为30/61/.../303天均<330)→v108=233.6,
#     yoy=18.7; index类百分比: 1.7/250.6×100=0.6784, 18.7/233.6×100=8.0051
M = 120
d_month = []
y, mth = 2017, 1
for _i in range(M):
    d_month.append(f'{y:04d}-{mth:02d}-01')
    mth += 1
    if mth == 13:
        y, mth = y + 1, 1
v_month = [50.0 + 1.7 * i for i in range(M)]
out2 = mc.compute_series_changes(d_month, v_month, 'monthly',
                                 unit=('index', '指数点(测试)'))
check("120点月频: mom_chg=1.7(手算)", out2.get('mom_chg') == 1.7,
      out2.get('mom_chg'))
check("120点月频: yoy_chg=18.7(手算: v119−v108=252.3−233.6)",
      out2.get('yoy_chg') == 18.7, out2.get('yoy_chg'))
check("120点月频: yoy基准=2026-01-01(滞后334天首个入窗)",
      out2.get('yoy_chg_from') == '2026-01-01', out2.get('yoy_chg_from'))
check("120点月频: mom_pct=0.6784(手算 1.7/250.6)",
      out2.get('mom_pct') == 0.6784, out2.get('mom_pct'))
check("120点月频: yoy_pct=8.0051(手算 18.7/233.6)",
      out2.get('yoy_pct') == 8.0051, out2.get('yoy_pct'))
check("120点月频: 月频不给week_chg", 'week_chg' not in out2)

# (c) 区间变动跨2500点长序列(基准=严格早于start的最后观测)
import research_history_query as rhq  # noqa: E402
iv = rhq.interval_change(d_daily, v_daily, 'percent',
                         start=d_daily[101], end=d_daily[200])
# 手算: 基准=i100→125.0, 终值=i200→150.0, pp=25.0, bp=2500
check("长序列区间变动: 基准=125.0(手算)", iv.get('basis_value') == 125.0,
      iv.get('basis_value'))
check("长序列区间变动: pp=+25.0(手算)", iv.get('pp_change') == 25.0,
      iv.get('pp_change'))
check("长序列区间变动: bp=+2500(手算)", iv.get('bp_change') == 2500,
      iv.get('bp_change'))
iv2 = rhq.interval_change(d_daily, v_daily, 'percent', start=None,
                          end=d_daily[N - 1])
# 手算: start=None→基准=首观测100.0, 终值=724.75 → pp=+624.75
check("长序列区间变动(start=None): 基准=首观测100.0",
      iv2.get('basis_value') == 100.0, iv2.get('basis_value'))
check("长序列区间变动(start=None): pp=+624.75(手算)",
      iv2.get('pp_change') == 624.75, iv2.get('pp_change'))

print("=" * 64)
if FAIL == 0:
    print(f"✅ 全部通过: {PASS} 项")
else:
    print(f"❌ 失败 {FAIL} 项 / 通过 {PASS} 项")
    sys.exit(1)
