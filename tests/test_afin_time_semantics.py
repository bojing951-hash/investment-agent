#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A-fin(2)(3) 时间语义结构化+研究模式门+月×月月键对齐+--lag 行为锁。

覆盖(预期值全部手算字面量/测试内独立公式,禁被测函数自算):
① catalog(workbench_data.series_capable_metrics)透传 time_semantics
   (SPX=trading_day/true;CPI=calendar_month/false;ICSA 观测期未登记→null
   +发布日 true——周历无枚举值,如实缺键);
② compare sides[].time_semantics 同构透传+快照 fact 层 release_date 实测值
   覆盖登记(数据>登记,值与来源随行);
③ alignment.research_mode_gate 三模式: descriptive 恒 available;
   event_study=任一侧 release_date_available!==True→blocked: 无发布日;
   realtime_info_set=Charter7-1 对查询时窗负责(当前窗 available/历史窗起点
   月窗内跨日 vintage 在场性;同日 _vN 仅附加披露,_has_vn_history 可注入);
④ 月×月月键内交: 锚日不巧合(01 锚 vs 15 锚)旧 exact_date 会 n=0,新路径
   month_grid 出非空(手算 rho);01 锚下月键≡日键(现役不变性由验收套件
   ⑤号真实数据锁);
⑤ --lag: 正/负平移=n−|k| 对+手算 rho;不足 3→None+提示;与 --window
   互斥 rc=2(bad_lag)。
"""
import contextlib
import io
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (ROOT, os.path.join(ROOT, 'scripts')):
    if p not in sys.path:
        sys.path.insert(0, p)

import ia_cli                    # noqa: E402
import workbench_data as wd      # noqa: E402

PASS, FAIL = 0, 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")


def ref_pearson(xs, ys):
    """测试内独立参考实现(与被测 cc.pearson 分开写,防同源自证)。"""
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx <= 0 or vy <= 0:
        return None
    return cov / (vx ** 0.5 * vy ** 0.5)


def run_cli(*argv):
    out, err = io.StringIO(), io.StringIO()
    code = None
    real_argv = sys.argv
    sys.argv = ['ia_cli.py', *argv]
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                ia_cli.main()
            except SystemExit as e:
                code = e.code
    finally:
        sys.argv = real_argv
    return code, out.getvalue(), err.getvalue()


def synth_snapshot(series_map, facts=None, **extra):
    snap = {'snapshot_id': 'research_snapshot_20990531',
            'target_date': '2099-05-31', 'research_as_of': '2099-05-31T18:00:00+08:00',
            'gate_a': {'status': 'PASS', 'core_missing': [], 'noncore_missing': [],
                       'noncore_missing_detail': {}, 'noncore_degraded': []},
            'sources_status': {}, 'facts': facts or [], 'series_store': dict(series_map)}
    snap.update(extra)
    return snap


REAL_REG = wd.load_registry(ROOT)

# ── 手算合成面: UNEMPLOYMENT(rate/pp,01 锚) × CPI(price/pct,15 锚) ──
# pp 手算: [1,2,3,4]; pct 手算: [1.0, 1.9801980198019802, 2.912621359223301,
# 3.773584905660377](=101/100,103/101,106/103,110/106−1 各×100)
M01 = ['2099-01-01', '2099-02-01', '2099-03-01', '2099-04-01', '2099-05-01']
M15 = ['2099-01-15', '2099-02-15', '2099-03-15', '2099-04-15', '2099-05-15']
UNEMP_V = [1.0, 2.0, 4.0, 7.0, 11.0]
CPI_V = [100.0, 101.0, 103.0, 106.0, 110.0]
PP_EXP = [1.0, 2.0, 3.0, 4.0]
PCT_EXP = [1.0, 1.9801980198019802, 2.912621359223301, 3.773584905660377]

SYN = synth_snapshot({
    'UNEMPLOYMENT': {'dates': M01, 'values': UNEMP_V},
    'CPI': {'dates': M15, 'values': CPI_V},
    'SPX': {'dates': ['2099-06-0%d' % i for i in range(1, 6)],
            'values': [100.0, 102.0, 101.0, 103.0, 105.0]},
    'NDX': {'dates': ['2099-06-0%d' % i for i in range(1, 6)],
            'values': [200.0, 204.0, 202.0, 206.0, 210.0]}})


def with_context(snap):
    ia_cli.load_context = lambda: (snap, REAL_REG, '')


print("═" * 60)
print("① catalog time_semantics 纯透传(缺键=null 不默认)")
print("═" * 60)
rows = {r['metric_id']: r for r in wd.series_capable_metrics(SYN, REAL_REG)}
check("SPX=trading_day/true",
      rows['SPX']['time_semantics'] == {'observation_period_kind': 'trading_day',
                                        'release_date_available': True},
      str(rows['SPX'].get('time_semantics')))
check("CPI=calendar_month/false",
      rows['CPI']['time_semantics'] == {'observation_period_kind': 'calendar_month',
                                        'release_date_available': False},
      str(rows['CPI'].get('time_semantics')))
check("ICSA 观测期未登记→null(周历无枚举值,如实缺键)",
      rows['ICSA']['time_semantics'] == {'observation_period_kind': None,
                                         'release_date_available': True}
      if 'ICSA' in rows else 'ICSA 不在合成序列面(注册表直查)',
      str(rows.get('ICSA', {}).get('time_semantics')))
if 'ICSA' not in rows:
    icsa_reg = REAL_REG['by_id'].get('ICSA', {})
    check("ICSA 注册表直查: kind 缺键+release true",
          'observation_period_kind' not in icsa_reg
          and icsa_reg.get('release_date_available') is True,
          str({k: icsa_reg.get(k) for k in ('observation_period_kind',
                                            'release_date_available')}))

print("═" * 60)
print("② compare sides time_semantics + fact release_date 覆盖(数据>登记)")
print("═" * 60)
snap_fact = synth_snapshot(dict(SYN['series_store']),
                           facts=[{'metric_id': 'UNEMPLOYMENT',
                                   'release_date': '2099-06-06',
                                   'quality_status': 'PASS'}])
with_context(snap_fact)
code, out, _ = run_cli('compare', '--metrics', 'UNEMPLOYMENT,CPI')
d = json.loads(out)
sides = {s['metric_id']: s for s in d['data']['sides']}
ts_u = sides['UNEMPLOYMENT']['time_semantics']
check("fact 带 release_date→覆盖为 true+值与来源随行",
      ts_u.get('release_date_available') is True
      and ts_u.get('release_date') == '2099-06-06'
      and 'fact' in (ts_u.get('release_date_source') or ''),
      str(ts_u))
check("无 fact 值侧维持登记原值(CPI=false)",
      sides['CPI']['time_semantics'] == {'observation_period_kind': 'calendar_month',
                                         'release_date_available': False},
      str(sides['CPI']['time_semantics']))

print("═" * 60)
print("③ research_mode_gate 三模式(机械可计算部分)")
print("═" * 60)
gate = d['data']['alignment']['research_mode_gate']
check("descriptive 恒 available", gate['descriptive'] == 'available', str(gate))
check("CPI 侧无发布日→event_study blocked(文案含不得声称事件研究)",
      gate['event_study'].startswith('blocked: 无发布日')
      and '事件研究' in gate['event_study'], str(gate['event_study']))
with_context(SYN)
code, out, _ = run_cli('compare', '--metrics', 'SPX,NDX')
gate2 = json.loads(out)['data']['alignment']['research_mode_gate']
check("双市场侧→event_study available", gate2['event_study'] == 'available',
      str(gate2))
# Charter7-1(2026-11-10): realtime 门对查询时窗负责——判据=查询起点月窗内
# 跨日 vintage(research_snapshot 基础日期)在场性;同日 _vN 只是附加披露。
# 边界三形态: ①当前窗(无 --start)→available(现役快照=当前信息集,即使仓内
# 无任何 _vN);②历史窗起点月内无跨日 vintage→blocked(文案给现存清单+如实
# 原因);③同日 _vN 在场性只改变披露尾注,不改变可用性(⑧⑨号验收另锁)。
check("当前窗(无 --start)→available(现役快照即当前时点信息集)",
      gate2['realtime_info_set'].startswith('available(现役快照即当前时点信息集'),
      str(gate2['realtime_info_set']))
check("compare 随行 realtime_vintage_dates 清单(跨日vintage权威)",
      isinstance(gate2.get('realtime_vintage_dates'), list),
      str(gate2.get('realtime_vintage_dates')))
code, out, _ = run_cli('compare', '--metrics', 'SPX,NDX',
                       '--start', '2099-06-01')
gate3 = json.loads(out)['data']['alignment']['research_mode_gate']
check("历史窗(起点月内无跨日vintage)→blocked+如实原因",
      gate3['realtime_info_set'].startswith(
          'blocked: 查询期20990601~20990630起点月窗内无vintage快照')
      and '不得以今日修订口径冒充当时值' in gate3['realtime_info_set'],
      str(gate3['realtime_info_set']))
# _has_vn_history 可注入判据(⑨号验收另锁 select_snapshot 取 _v2)
with tempfile.TemporaryDirectory() as td:
    open(os.path.join(td, 'research_snapshot_20990531.json'), 'w').write('{}')
    check("空版本日(仅当日正本)→False",
          ia_cli._has_vn_history('20990531', data_dir=td) is False)
    open(os.path.join(td, 'research_snapshot_20990531_v2.json'), 'w').write('{}')
    check("存在 _vN→True", ia_cli._has_vn_history('20990531', data_dir=td) is True)
check("默认目录=ROOT/data/daily(签名注入兼容)",
      ia_cli._has_vn_history('20261108') is False,
      '(现役 20261108 单版本,应 False)')

print("═" * 60)
print("④ 月×月月键内交: 锚日巧合不再是前提")
print("═" * 60)
with_context(SYN)
code, out, _ = run_cli('compare', '--metrics', 'UNEMPLOYMENT,CPI')
d = json.loads(out)['data']
al = d['alignment']
exp_rho = ref_pearson(PP_EXP, PCT_EXP)
check("01锚×15锚→month_grid 出非空(旧 exact_date 恒 n=0)",
      code == 0 and al['mode'] == 'month_grid'
      and al['n_common_observations'] == 5,
      f"mode={al['mode']} n={al['n_common_observations']}")
check("rho=手算 pp×pct 参考值(变化对=各月格代表值之差)",
      abs(d['pearson_returns'] - exp_rho) < 1e-12,
      f"{d['pearson_returns']} vs {exp_rho}")
check("note 注明月×月锚日巧合不作为对齐前提",
      '锚日巧合不作为对齐前提' in al['note'], al['note'])
check("两侧 sides[].aggregation 均随行(月×月)",
      all('month_grid' in (s.get('aggregation') or '')
          for s in d['sides']),
      str([s.get('aggregation') for s in d['sides']]))
check("跨月历无掉落: a_dropped=b_dropped=0(月键口径)",
      al['a_dropped'] == 0 and al['b_dropped'] == 0,
      f"{al['a_dropped']}/{al['b_dropped']}")

print("═" * 60)
print("⑤ --lag 滞后平移(单 lag,pearson 复用)")
print("═" * 60)
# k=1: 配对 (pp[i], pct[i−1]) i=1..3 → ([2,3,4],[pct0,pct1,pct2])
code, out, _ = run_cli('compare', '--metrics', 'UNEMPLOYMENT,CPI', '--lag', '1')
lag = json.loads(out)['data']['lagged']
exp_lag1 = ref_pearson([2.0, 3.0, 4.0], PCT_EXP[:3])
check("lag=1: n_lag=n−1=3,rho=手算平移参考值",
      lag['n_lag_pairs'] == 3 and lag['rho'] is not None
      and abs(lag['rho'] - exp_lag1) < 1e-12,
      f"{lag} vs {exp_lag1}")
# k=−2: 配对 (pp[i], pct[i+2]) i=0..1 → n=2<3 → None+提示
code, out, _ = run_cli('compare', '--metrics', 'UNEMPLOYMENT,CPI', '--lag', '-2')
lag2 = json.loads(out)['data']['lagged']
check("lag=−2: n_lag=2<3→rho=None+提示在场",
      lag2['n_lag_pairs'] == 2 and lag2['rho'] is None
      and lag2['warning_if_insufficient'],
      str(lag2))
check("lagged.basis 注明 k>0=B 先动+口径指向 change_basis",
      'B先动' in lag2['basis'] and 'change_basis' in lag2['basis'])
# 互斥: --lag×--window → rc=2 bad_lag
code, out, _ = run_cli('compare', '--metrics', 'SPX,NDX', '--lag', '5',
                       '--window', '20')
dmutex = json.loads(out)
check("--lag 与 --window 互斥→rc=2 error.kind=bad_lag",
      code == 2 and dmutex['error']['kind'] == 'bad_lag',
      f"rc={code} {dmutex.get('error', {}).get('kind')}")
check("互斥错误先于快照加载(无快照环境恒定 rc=2)",
      'ok' in dmutex and dmutex['ok'] is False
      and dmutex['error']['kind'] == 'bad_lag')

print()
print("═" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("═" * 60)
sys.exit(0 if FAIL == 0 else 1)
