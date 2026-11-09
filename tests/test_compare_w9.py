#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""compare 窗口与跨频率能力回归(批2 W9, 2026-11-09;金融审计 D6 建议1-6)。

八个审计案例逐个落测,预期值全部手算/直读原始 JSON,禁止用被测模块自算:
  ① 日×日单位感知回归(线性构造 → rho=1.0)
  ② 日黄金×月通胀 → month_grid 聚合对齐(月键内交/聚合侧披露/样本警告)
  ③ 月×月 date_gap 阈值频率归一(相邻月~31天不误报,缺整月才报,阈值45)
  ④ SHCOMP×SPX 跨历掉落计数(a_dropped/b_dropped 手算)
  ⑤ 样本不足(<30)专门文案
  ⑥ n==0(共同观测<3)专门文案与不可计算提示(建议9)
  ⑦ 合成 _vN fixture 选版(修订版 v2 胜出,compare 消费 v2 序列)
  ⑧ sides 并入 quality_status/release_note(建议1)
另含: --start/--end 指令窗口过滤(建议2)与 --window 滚动相关(建议3,C-3)。

运行: python3 tests/test_compare_w9.py(进程内 monkeypatch,零网络零真实数据)。
"""
import contextlib
import io
import json
import os
import re
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import ia_cli                       # noqa: E402
import workbench_data as wd         # noqa: E402

PASS, FAIL = 0, 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")


def make_snap(series_map, facts=None, ymd='20261107'):
    """合成快照: series_store 直供 metric_series;facts 供质量披露。"""
    return {'snapshot_id': f'research_snapshot_{ymd}', 'target_date': ymd,
            'research_as_of': f'{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}T09:00:00+08:00',
            'gate_a': {'status': 'PASS'},
            'facts': facts or [], 'series_store': series_map}


def run_cmp(*argv, snap=None):
    """进程内跑 ia_cli.main(compare);load_context 指合成快照。"""
    real_ctx = ia_cli.load_context
    ia_cli.load_context = lambda: (snap, wd.load_registry(ROOT), '')
    out = io.StringIO()
    code = None
    real_argv = sys.argv
    sys.argv = ['ia_cli.py', 'compare', *argv]
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            try:
                ia_cli.main()
            except SystemExit as e:
                code = e.code
    finally:
        sys.argv = real_argv
        ia_cli.load_context = real_ctx
    return code, json.loads(out.getvalue())


print("=" * 60)
print("compare 窗口与跨频率(批2 W9,审计8案例)")
print("=" * 60)

# ══ ① 日×日回归: 线性构造 rho=1.0 ═══════════════════════════════════
print("\n[①] 日×日 单位感知回归(SPX×NVDA,rho 手算=1.0)")
D5 = ['2026-01-02', '2026-01-05', '2026-01-06', '2026-01-07', '2026-01-08']
# 价格族→pct 基:乘法构造使 pct 变化恰为 [+1,+2,+1,+2]% × [+2,+4,+2,+4]%
# (比例 1:2 → 线性相关 rho=1;附3 滚动同法)
spx_v, nv_v, va, vb = [100.0], [50.0], [1, 2, 1, 2], [2, 4, 2, 4]
for pa, pb in zip(va, vb):
    spx_v.append(spx_v[-1] * (1 + pa / 100))
    nv_v.append(nv_v[-1] * (1 + pb / 100))
snap1 = make_snap({'SPX': {'dates': D5, 'values': spx_v},
                   'NVDA': {'dates': D5, 'values': nv_v}})
code, d = run_cmp('--metrics', 'SPX,NVDA', snap=snap1)
check("① rc=0", code == 0 and d['ok'])
check("① pearson(pct对[+1,+2,+1,+2]×[+2,+4,+2,+4])=1.0",
      d['data']['pearson_returns'] is not None
      and abs(d['data']['pearson_returns'] - 1.0) < 1e-9,
      str(d['data']['pearson_returns']))
check("① n_change_pairs=4(5观测-1,零基无弃)", d['data']['n_change_pairs'] == 4)
check("① alignment.mode=exact_date(同频不聚合)",
      d['data']['alignment']['mode'] == 'exact_date')
check("① date_basis=price→pct 两侧",
      d['data']['change_basis'] == {'a': 'pct', 'b': 'pct'})

# ══ ② 日×月 → month_grid(建议6) ════════════════════════════════════
print("\n[②] 日黄金×月通胀 → 自然月网格聚合对齐(GOLD_F×CPI)")
# 前置一笔 2025-12 观测: 只在 GOLD 侧 → 供 interval_change 取窗前基准,
# 且因 CPI 无 2025-12 月键不进入共同窗(n_common 仍=4)
g_dates = ['2025-12-15', '2026-01-05', '2026-01-20', '2026-02-03',
           '2026-02-25', '2026-03-04', '2026-04-02']
g_vals = [1900, 2000, 2050, 2100, 2200, 2300, 2400]
c_dates = ['2026-01-15', '2026-02-15', '2026-03-15', '2026-04-15']
c_vals = [310, 311, 312, 313]
snap2 = make_snap({'GOLD_F': {'dates': g_dates, 'values': g_vals},
                   'CPI': {'dates': c_dates, 'values': c_vals}})
code, d = run_cmp('--metrics', 'GOLD_F,CPI', snap=snap2)
al = d['data']['alignment']
check("② rc=0 mode=month_grid", code == 0 and al['mode'] == 'month_grid')
check("② 共同月份数=4(月键 2026-01..04 内交)",
      al['n_common_observations'] == 4, str(al['n_common_observations']))
check("② 聚合后 n_change_pairs=3(4月-1)",
      d['data']['n_change_pairs'] == 3, str(d['data']['n_change_pairs']))
agg = {s['metric_id']: s.get('aggregation') for s in d['data']['sides']}
check("② 高频侧(GOLD_F)披露 month_grid 聚合,月频侧(CPI)无",
      'month_grid' in (agg.get('GOLD_F') or '')
      and agg.get('CPI') is None, str(agg))
check("② mixed_frequency 警告指向 month_grid 口径",
      any('mixed_frequency' in w and 'month_grid' in w for w in d['warnings']))
check("② 聚合后 n<30 仍走样本不足警告",
      d['data'].get('sample_note', '').startswith('n_change_pairs=3<30'))
# 月末代表值=期内末值;interval 基准=窗前末笔(2025-12-15=1900,窗末 2026-04-02=2400)
g_side = next(s for s in d['data']['sides'] if s['metric_id'] == 'GOLD_F')
iv = g_side['interval_change_common_window']
check("② GOLD 窗口区间变动: 基准=窗前末笔 1900,窗末=2026-04-02 的 2400"
      "(手算 +26.3158%)",
      iv.get('available', True) and iv.get('basis_date') == '2025-12-15'
      and iv.get('end_date') == '2026-04-02'
      and abs(iv.get('pct_change', 0) - (2400 / 1900 - 1) * 100) < 5e-5,
      str(iv))
c_side = next(s for s in d['data']['sides'] if s['metric_id'] == 'CPI')
check("② CPI 侧窗前无基准观测 → 如实 unavailable(不编造基准)",
      c_side['interval_change_common_window'].get('available') is False)

# ══ ③ 月×月 date_gap 阈值归一(建议4) ═══════════════════════════════
print("\n[③] 月×月(FED_FUNDS×UNEMPLOYMENT)阈值 7→45 天,缺整月才报")
# A-fin §3(2026-11-09): 月×月改月键内交(锚日巧合不作为对齐前提),mode 由
# exact_date→month_grid;相邻月 28~35 天正常间距在月网格=1 个月步长,唯一
# 断点=缺整月(03→06=3 个月步长),date_gap(月网格) 以月步长计。
f_dates = ['2026-01-15', '2026-02-15', '2026-03-20', '2026-06-15']
snap3 = make_snap({'FED_FUNDS': {'dates': f_dates, 'values': [4.0, 4.0, 3.9, 3.8]},
                   'UNEMPLOYMENT': {'dates': f_dates, 'values': [4.2, 4.1, 4.0, 3.9]}})
code, d = run_cmp('--metrics', 'FED_FUNDS,UNEMPLOYMENT', snap=snap3)
gapw = [w for w in d['warnings'] if 'date_gap' in w]
check("③ A-fin: 月×月按月键对齐(month_grid,锚日巧合非前提)",
      d['data']['alignment']['mode'] == 'month_grid')
check("③ 相邻月不再误报(唯一 date_gap=缺整月 3 个月步长,月网格口径)",
      len(gapw) == 1 and '3 个月' in gapw[0] and '月网格' in gapw[0], str(gapw))
check("③ 利率族 basis=pp 两侧",
      d['data']['change_basis'] == {'a': 'pp', 'b': 'pp'})

# ══ ④ 跨历掉落披露(建议5) ══════════════════════════════════════════
print("\n[④] SHCOMP×SPX 跨历掉落计数(a_dropped/b_dropped 手算=3/3)")
snap4 = make_snap({
    'SPX': {'dates': ['2026-01-02', '2026-01-03', '2026-01-06',
                      '2026-01-09', '2026-01-12', '2026-01-13'],
            'values': [100, 101, 102, 103, 104, 105]},
    'SHCOMP': {'dates': ['2026-01-02', '2026-01-04', '2026-01-06',
                         '2026-01-09', '2026-01-15', '2026-01-16'],
               'values': [3000, 3010, 3020, 3030, 3040, 3050]},
})
code, d = run_cmp('--metrics', 'SPX,SHCOMP', snap=snap4)
al = d['data']['alignment']
check("④ 共同观测=3(01-02/01-06/01-09),a_dropped=3,b_dropped=3",
      al['n_common_observations'] == 3 and al['a_dropped'] == 3
      and al['b_dropped'] == 3,
      f"n={al['n_common_observations']} a={al['a_dropped']} b={al['b_dropped']}")

# ══ ⑤ 样本不足文案(①复用) ══════════════════════════════════════════
print("\n[⑤] 样本不足(<30)专门文案")
code, d = run_cmp('--metrics', 'SPX,NVDA', snap=snap1)
check("⑤ sample_note 与警告都在场",
      d['data'].get('sample_note') == 'n_change_pairs=4<30,样本不足,短窗相关性不可外推'
      and any('样本不足' in w for w in d['warnings']))

# ══ ⑥ n==0 专门文案(建议9) ═════════════════════════════════════════
print("\n[⑥] n==0(共同观测<3): 相关性不可计算,不产伪值")
snap6 = make_snap({'SPX': {'dates': ['2026-01-02', '2026-01-03'],
                           'values': [100, 101]},
                   'NVDA': {'dates': ['2026-01-02', '2026-01-03'],
                            'values': [50, 52]}})
code, d = run_cmp('--metrics', 'SPX,NVDA', snap=snap6)
check("⑥ rc=0(结构化产物,非崩溃)", code == 0 and d['ok'])
check("⑥ pearson_returns=null + n_change_pairs=0",
      d['data']['pearson_returns'] is None and d['data']['n_change_pairs'] == 0)
check("⑥ n==0 专门文案(建议9)",
      d['data'].get('sample_note', '').startswith('n_change_pairs=0')
      and any('不可计算' in w for w in d['warnings']))

# ══ ⑦ _vN 修订版选版 ═══════════════════════════════════════════════
print("\n[⑦] 合成 _vN fixture: compare 消费最高修订版 v2")
with tempfile.TemporaryDirectory() as td:
    os.makedirs(os.path.join(td, 'config'))
    os.makedirs(os.path.join(td, 'data', 'daily'))
    shutil.copy(os.path.join(ROOT, 'config', 'metric_registry.json'),
                os.path.join(td, 'config', 'metric_registry.json'))
    base = make_snap({'SPX': {'dates': D5, 'values': [100, 100, 100, 100, 100]},
                      'NVDA': {'dates': D5, 'values': [50, 50, 50, 50, 50]}},
                     ymd='20261107')
    v2 = make_snap({'SPX': {'dates': D5, 'values': [200, 201, 203, 204, 206]},
                    'NVDA': {'dates': D5, 'values': [60, 62, 66, 68, 72]}},
                   ymd='20261107')
    v2['snapshot_id'] = 'research_snapshot_20261107_v2'
    with open(os.path.join(td, 'data', 'daily',
                           'research_snapshot_20261107.json'), 'w') as f:
        json.dump(base, f)
    with open(os.path.join(td, 'data', 'daily',
                           'research_snapshot_20261107_v2.json'), 'w') as f:
        json.dump(v2, f)
    real_root = ia_cli.ROOT
    real_ctx = ia_cli.load_context
    ia_cli.ROOT = td
    # latest_snapshot 返回 (snap, path_or_reason);load_context 契约 (snap, reg, note)
    _snap7, _why = wd.latest_snapshot(td)
    ia_cli.load_context = lambda: (_snap7, wd.load_registry(td), '')
    out = io.StringIO()
    sys.argv = ['ia_cli.py', 'compare', '--metrics', 'SPX,NVDA']
    code = None
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            try:
                ia_cli.main()
            except SystemExit as e:
                code = e.code
    finally:
        sys.argv = ['ia_cli.py']
        ia_cli.ROOT = real_root
        ia_cli.load_context = real_ctx
    d = json.loads(out.getvalue())
    # 判别式手算: base 版恒值 100/50 → pct 变化全 0,零基过滤后 n_change_pairs=0
    # 且 pearson=null;v2 版有真实变化 → n_change_pairs=4 且 pearson 非 null
    check("⑦ 修订版 v2 胜出(v2 ncp=4/pearson≠null;base 版恒值会是 ncp=0/null)",
          code == 0 and d['data']['n_change_pairs'] == 4
          and d['data']['pearson_returns'] is not None,
          f"ncp={d['data']['n_change_pairs']} rho={d['data']['pearson_returns']}")

# ══ ⑧ sides 质量披露(建议1) ═════════════════════════════════════════
print("\n[⑧] sides 并入 quality_status(事实层)+release_note(注册表透传)")
snap8 = make_snap({'SPX': {'dates': D5, 'values': [100, 101, 103, 104, 106]},
                   'NVDA': {'dates': D5, 'values': [50, 52, 56, 58, 62]}},
                  facts=[{'metric_id': 'SPX', 'quality_status': 'PASS'},
                         {'metric_id': 'NVDA', 'quality_status': 'DEGRADED'}])
code, d = run_cmp('--metrics', 'SPX,NVDA', snap=snap8)
qm = {s['metric_id']: s.get('quality_status') for s in d['data']['sides']}
check("⑧ quality_status 与快照事实层一致",
      qm == {'SPX': 'PASS', 'NVDA': 'DEGRADED'}, str(qm))
reg_doc = json.load(open(os.path.join(ROOT, 'config', 'metric_registry.json'),
                         encoding='utf-8'))
reg_by_id = {m['metric_id']: m for m in reg_doc['metrics']}
rn = {s['metric_id']: s.get('release_note') for s in d['data']['sides']}
check("⑧ release_note=注册表 release_semantics 逐字透传",
      all(rn[mid] == reg_by_id[mid].get('release_semantics') for mid in rn),
      str(rn))

# ══ 窗口过滤(建议2)与滚动相关(建议3) ════════════════════════════════
print("\n[附1] --start/--end 指令窗口过滤(对齐前生效)")
d_long = ['2026-01-02', '2026-01-05', '2026-01-06', '2026-01-07',
          '2026-02-02', '2026-02-03']
snapw = make_snap({'SPX': {'dates': d_long, 'values': [100, 101, 102, 103, 104, 105]},
                   'NVDA': {'dates': d_long, 'values': [50, 51, 52, 53, 54, 55]}})
code, d = run_cmp('--metrics', 'SPX,NVDA', '--start', '2026-01-05',
                  '--end', '2026-01-31', snap=snapw)
al = d['data']['alignment']
check("窗口内共同观测=3(01-05/06/07),窗口外已剔除",
      code == 0 and al['common_first'] == '2026-01-05'
      and al['common_last'] == '2026-01-07'
      and al['n_common_observations'] == 3, str(al))
spx = d['data']['sides'][0]
check("sides.n/first/last 同步为窗口内(4/01-05/01-07…按各自序列)",
      spx['n'] == 3 and spx['first'] == '2026-01-05' and spx['last'] == '2026-01-07')

print("\n[附2] 窗口外无观测 → 结构化 empty_window(rc=1)")
code, d = run_cmp('--metrics', 'SPX,NVDA', '--start', '2027-01-01',
                  '--end', '2027-01-31', snap=snapw)
check("empty_window 结构化拒绝", code == 1
      and d['error']['kind'] == 'empty_window')

print("\n[附3] --window 滚动相关(diff 基,复用 rhq.rolling_correlation)")
# 6 观测/5 变化对(pct [+1,+2,+1,+2,+1]×[+2,+4,+2,+4,+2],比例 1:2);
# 窗长 3:差分窗口 [2,1,2]×[4,2,4] 与 [1,2,1]×[2,4,2] → rho 恒 1.0(rhq.pearson n≥3)
D6 = ['2026-01-02', '2026-01-05', '2026-01-06', '2026-01-07', '2026-01-08',
      '2026-01-09']
sv, nv = [100.0], [50.0]
for pa, pb in zip([1, 2, 1, 2, 1], [2, 4, 2, 4, 2]):
    sv.append(sv[-1] * (1 + pa / 100))
    nv.append(nv[-1] * (1 + pb / 100))
snap1r = make_snap({'SPX': {'dates': D6, 'values': sv},
                    'NVDA': {'dates': D6, 'values': nv}})
code, d = run_cmp('--metrics', 'SPX,NVDA', '--window', '3', snap=snap1r)
roll = d['data'].get('rolling')
check("rolling 摘要在场(窗长/n_windows/首/末/max/min/口径)",
      roll is not None and roll['window'] == 3
      and set(roll) >= {'n_windows', 'first', 'last', 'max', 'min', 'basis'})
check("n_windows=2(5 变化对-窗长 3+1),首=2026-01-08 末=2026-01-09"
      "(首值自第 N+1 个变化日,差分样本≥3)",
      roll['n_windows'] == 2 and roll['first']['as_of'] == '2026-01-08'
      and roll['last']['as_of'] == '2026-01-09', str(roll))
check("线性构造滚动 rho 恒 1.0(手算)",
      roll['first']['rho'] == 1.0 and roll['last']['rho'] == 1.0
      and roll['max'] == 1.0 and roll['min'] == 1.0, str(roll))
code, d = run_cmp('--metrics', 'SPX,NVDA', '--window', '2', snap=snap6)
check("变化对不足 → rolling.n_windows=0 + 警告",
      d['data']['rolling']['n_windows'] == 0
      and any('滚动序列为空' in w for w in d['warnings']))
code, d = run_cmp('--window', '5', snap=snap1)
check("--window 无 --metrics → rc=2 结构化 bad_window",
      code == 2 and d['error']['kind'] in ('no_mode', 'bad_window'))
code, d = run_cmp('--metrics', 'SPX,NVDA', '--window', '1', snap=snap1)
check("--window 1 → rc=2 bad_window(N≥2)", code == 2
      and d['error']['kind'] == 'bad_window')

print("\n[附4] 窗口化 interval_change 基准观测不被滤掉(A-fin 交叉审查[中],2026-11-09)")
# 缺陷回放: 窗口过滤块先于区间变动,s['dates'] 已无 start 前观测 → 任何
# --start 窗口下 interval_change_common_window 恒 unavailable。修复=保留
# 过滤前副本,按原序列+窗口界计算(对齐/相关仍用过滤后序列)。
# 手算: 窗 [01-05,01-31],基准=严格早于 01-05 的末笔=01-02(SPX 100/NVDA 50),
# 窗末=01-07(103/53) → pct=(103/100−1)×100=+3.0% / (53/50−1)×100=+6.0%
code, d = run_cmp('--metrics', 'SPX,NVDA', '--start', '2026-01-05',
                  '--end', '2026-01-31', snap=snapw)
ivm = {s['metric_id']: s['interval_change_common_window']
       for s in d['data']['sides']}
check("窗口下基准观测保留: SPX basis=01-02(100)→end=01-07(103),手算 +3.0%",
      ivm['SPX'].get('available', True) and ivm['SPX'].get('basis_date') == '2026-01-02'
      and ivm['SPX'].get('basis_value') == 100 and ivm['SPX'].get('end_date') == '2026-01-07'
      and abs(ivm['SPX'].get('pct_change', 0) - 3.0) < 5e-5, str(ivm['SPX']))
check("NVDA 同理 basis=01-02(50)→end=01-07(53),手算 +6.0%",
      ivm['NVDA'].get('available', True) and ivm['NVDA'].get('basis_date') == '2026-01-02'
      and abs(ivm['NVDA'].get('pct_change', 0) - 6.0) < 5e-5, str(ivm['NVDA']))
check("对齐/样本口径仍按过滤后序列(共同观测=3,窗口语义不变)",
      d['data']['alignment']['n_common_observations'] == 3
      and d['data']['sides'][0]['n'] == 3)
# 窗起点=序列首笔 → 窗前真无更早观测 → 如实 unavailable(不编造基准)
code, d = run_cmp('--metrics', 'SPX,NVDA', '--start', '2026-01-02',
                  '--end', '2026-01-07', snap=snapw)
iv0 = d['data']['sides'][0]['interval_change_common_window']
check("start=序列首笔 → 窗前确无基准观测 → 如实 unavailable+原因",
      iv0.get('available') is False and '无基准观测' in (iv0.get('reason') or ''),
      str(iv0))

print("\n[附5] 窗口参数空串/纯空白拒收(D 线终验修复1,2026-11-09)")
# 缺陷回放: --end "" 为假值直通 `if args.end:` 过滤条件→静默当无界,
# D 线第一次分段四窗全跑成累计窗。修=空串/纯空白 rc=2 bad_window。
code, d = run_cmp('--metrics', 'SPX,NVDA', '--start', '', snap=snap1)
check("compare --start '' → rc=2 bad_window(不再静默当无界)",
      code == 2 and d['error']['kind'] == 'bad_window', str(d.get('error')))
code, d = run_cmp('--metrics', 'SPX,NVDA', '--end', '   ', snap=snap1)
check("compare --end 纯空白 → rc=2 bad_window",
      code == 2 and d['error']['kind'] == 'bad_window', str(d.get('error')))
code, d = run_cmp('--metrics', 'SPX,NVDA', snap=snap1)
check("不传旗标=正常无界行为不受影响(rc=0)",
      code == 0 and d['data']['alignment']['mode'] == 'exact_date')

print("\n" + "=" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
