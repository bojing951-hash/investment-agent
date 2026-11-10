#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A-fin §6 十案例验收套件(Charter 5 问题三,冻结基线 2026-11-09)。

设计纪律:
- 预期值两类,均**不经被测函数自算**:
  (a) 审计冻结字面量(A-fin §6 表,2026-11-08 数据 vintage 下冻结);
  (b) 测试内独立重算=原始 JSON 直读(data/daily 快照+采集档,零引擎导入)
      →共同观测→手写单位感知变化(pp/pct,零基按族独立)→测试内独立
      pearson 实现,与引擎 CLI 输出比对(案例①方法,任何 vintage 恒适用)。
- 真实数据案例在 data/daily 无快照时(CI)**跳过并打印说明**——CI 面
  只跑合成面案例(⑧⑨,其余真实案例在本机全量套件中执行)。
- 冻结字面量附加 vintage 门: 最新快照 target_date=='20261108' 才断言;
  数据刷新后字面量改为 notice 跳过(独立重算比对仍恒断言)——防 CI 在
  数据正常演进后假红,同时锁死审计时点基线。
- ⑦(利率零基)为构造案例,已在 test_unit_aware_compare.py ⑥b 节锁定,
  本套件交叉引用不重复;⑧⑨ 半合成(fixture),无快照也执行。
"""
import glob
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)                 # ia_cli(仅 CLI 进程面+research_provenance)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

PASS, FAIL, SKIP = 0, 0, 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")


def skip_case(name, why):
    global SKIP
    SKIP += 1
    print(f"  ⏭  {name}: {why}")


def ref_pearson(xs, ys):
    """测试内独立 pearson(与引擎实现分开写,防同源自证)。"""
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx <= 0 or vy <= 0:
        return None
    return cov / (vx ** 0.5 * vy ** 0.5)


# ── 原始 JSON 直读(零引擎导入): 快照 series_store + 采集档 series ──
DAILY = os.path.join(ROOT, 'data', 'daily')


def _latest_snapshot_path():
    """最新快照路径(与引擎 select_snapshot 同规则: 最新 target_date,同日
    取最高 _vN——零引擎导入,规则手工镜像)。

    真实数据修复轮②连带(2026-11-10): 旧版把 _vN 从候选中排除,与引擎
    "点时取版取最高 _vN"分叉——同日修订版(_v2)在场时,引擎读新版序列而
    本测试独立重算读旧 base 序列,rho/n 全线假失败。改为同规则取版后,
    独立重算与引擎回到同一数据面。"""
    cands = sorted(glob.glob(os.path.join(DAILY, 'research_snapshot_*.json')))
    if not cands:
        return None

    def _key(p):
        b = os.path.basename(p)[len('research_snapshot_'):-len('.json')]
        base, _, ver = b.rpartition('_v')
        return (base, int(ver) if ver.isdigit() else 0)

    return max(cands, key=_key)


SNAP_PATH = _latest_snapshot_path()
SNAP = json.load(open(SNAP_PATH, encoding='utf-8')) if SNAP_PATH else None
_RT_GATE = None      # ⑧面捕获,⑨真实一致性断言消费(无快照环境保持 None)
VINTAGE = bool(SNAP) and str(SNAP.get('target_date')) == '20261108'
_ARCHIVE = {}
for _p in sorted(glob.glob(os.path.join(DAILY, 'macro_*.json'))):
    _doc = json.load(open(_p, encoding='utf-8'))
    for _k, _v in (_doc.get('data') or {}).items():
        if isinstance(_v, dict) and isinstance(_v.get('series'), dict) \
                and _v['series'].get('dates'):
            _ARCHIVE[_k] = _v['series']       # 后文件覆盖=最新档优先


def raw_series(mid):
    """原始序列直读: 快照 series_store 优先,否则采集档(与 metric_series 同
    来源优先级,但零引擎代码参与)。"""
    s = (SNAP or {}).get('series_store', {}).get(mid)
    if s and s.get('dates'):
        return s
    return _ARCHIVE.get(mid)


def raw_compare(metrics, *extra):
    """CLI 子进程真实调用(与用户面完全一致)。"""
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'ia_cli.py'),
                        'compare', '--metrics', metrics, *extra],
                       capture_output=True, text=True, cwd=ROOT, timeout=300)
    return r.returncode, json.loads(r.stdout)


def indep_changes(sa, fam_a, sb, fam_b, month_keys=False, start=None, end=None):
    """独立对齐+单位感知变化(手写,含 A-fin 零基按族独立与月键规则)。

    start/end=观测窗过滤(与 CLI --start/--end 同语义: 窗内观测内连接,
    变化只在窗内相邻观测间计算,跨界变化不属任何窗——分段口径即此)。
    """
    def _filt(s):
        if start is None and end is None:
            return s
        ds, vs = [], []
        for d, v in zip(s['dates'], s['values']):
            if (start is None or str(d) >= start) and (end is None or str(d) <= end):
                ds.append(d)
                vs.append(v)
        return {'dates': ds, 'values': vs}
    sa, sb = _filt(sa), _filt(sb)
    if month_keys:
        def grid(s):
            rep = {}
            for d, v in zip(s['dates'], s['values']):
                rep[str(d)[:7]] = v          # 同格末值覆盖
            return rep
        ga, gb = grid(sa), grid(sb)
        keys = sorted(set(ga) & set(gb))
        da = {k: ga[k] for k in keys}
        db = {k: gb[k] for k in keys}
    else:
        da = {str(d)[:10]: v for d, v in zip(sa['dates'], sa['values'])}
        db = {str(d)[:10]: v for d, v in zip(sb['dates'], sb['values'])}
        keys = sorted(set(da) & set(db))
    ca, cb = [], []
    for i in range(1, len(keys)):
        a0, a1 = da[keys[i - 1]], da[keys[i]]
        b0, b1 = db[keys[i - 1]], db[keys[i]]
        if a0 is None or a1 is None or b0 is None or b1 is None:
            continue
        if (fam_a in ('price', 'count') and a0 == 0) or \
           (fam_b in ('price', 'count') and b0 == 0):
            continue
        ca.append((a1 - a0) if fam_a == 'rate' else (a1 / a0 - 1) * 100)
        cb.append((b1 - b0) if fam_b == 'rate' else (b1 / b0 - 1) * 100)
    return ca, cb, keys


print("═" * 64)
print("A-fin §6 十案例验收(冻结基线 2026-11-09;数据 vintage "
      f"{(SNAP or {}).get('target_date', '无')})")
print("═" * 64)

if not SNAP:
    skip_case("①-⑥/⑧/⑩ 真实数据案例", "data/daily 无研究快照(CI 环境),"
              "按套件头设计跳过;合成面案例⑧(fixture)/⑨继续")

if SNAP:
    # ── ① 股×股: SPX×NDX,独立重算=原始JSON直读→pct×pct→手写pearson ──
    print("[①] SPX×NDX(独立重算法,无固定常数)")
    ca, cb, keys = indep_changes(raw_series('SPX'), 'price',
                                 raw_series('NDX'), 'price')
    rc, d = raw_compare('SPX,NDX')
    check("① rho=独立重算值(17位全等)",
          d['ok'] and abs(d['data']['pearson_returns'] - ref_pearson(ca, cb)) < 1e-12,
          f"{d['data']['pearson_returns']} vs {ref_pearson(ca, cb)}")
    check("① n_change_pairs=独立计数",
          d['data']['n_change_pairs'] == len(ca),
          f"{d['data']['n_change_pairs']} vs {len(ca)}")

    # ── ② 股×国债收益率: 冻结 -0.27925933087821936, 248/247 ──
    print("[②] SPX×UST_10Y 全窗(pp×pct)")
    ca, cb, keys = indep_changes(raw_series('SPX'), 'price',
                                 raw_series('UST_10Y'), 'rate')
    rc, d = raw_compare('SPX,UST_10Y')
    check("② rho=独立重算值",
          abs(d['data']['pearson_returns'] - ref_pearson(ca, cb)) < 1e-12)
    check("② basis={a:pct,b:pp}",
          d['data']['change_basis'] == {'a': 'pct', 'b': 'pp'})
    if VINTAGE:
        check("② 冻结基线: -0.27925933087821936, n_level=248, n_chg=247",
              d['data']['pearson_returns'] == -0.27925933087821936
              and d['data']['alignment']['n_level_observations'] == 248
              and d['data']['n_change_pairs'] == 247,
              f"{d['data']['pearson_returns']} {d['data']['alignment']['n_level_observations']}/{d['data']['n_change_pairs']}")
    else:
        skip_case("② 冻结字面量", f"vintage={SNAP.get('target_date')}≠20261108"
                  "(独立重算比对已执行)")

    # ── ③ 黄金×实际利率: 全窗+四分季段 ──
    print("[③] GOLD_F×TIPS_10Y(全窗+季度分段;分段口径=季度观测窗,"
          "窗内自基准重算变化,跨界变化不属任何窗=--start/--end 同语义)")
    ga, gt = raw_series('GOLD_F'), raw_series('TIPS_10Y')
    ca, cb, keys = indep_changes(ga, 'price', gt, 'rate')
    rc, d = raw_compare('GOLD_F,TIPS_10Y')
    check("③ 全窗 rho=独立重算值",
          abs(d['data']['pearson_returns'] - ref_pearson(ca, cb)) < 1e-12)
    seg_windows = [(None, '2026-02-28'), ('2026-03-01', '2026-05-31'),
                   ('2026-06-01', '2026-08-31'), ('2026-09-01', None)]
    frozen3 = [-0.05060361737044647, -0.28143527615856034,
               -0.16922960527873113, -0.11247417137670514]
    for (lo, hi), f in zip(seg_windows, frozen3):
        xs, ys, _ = indep_changes(ga, 'price', gt, 'rate', start=lo, end=hi)
        v = ref_pearson(xs, ys)
        if VINTAGE:
            check(f"③ 分段[{lo or '首'}~{hi or '末'}] 独立窗重算=冻结值 {f}",
                  v is not None and abs(v - f) < 1e-12, f"重算={v}")
        else:
            skip_case(f"③ 分段[{lo or '首'}~{hi or '末'}] 冻结字面量",
                      "vintage 非 20261108")

    # ── ④ 日黄金×月CPI: month_grid ──
    print("[④] GOLD_F×CPI(month_grid,双双价格族 pct×pct)")
    ca, cb, keys = indep_changes(raw_series('GOLD_F'), 'price',
                                 raw_series('CPI'), 'price', month_keys=True)
    rc, d = raw_compare('GOLD_F,CPI')
    al = d['data']['alignment']
    check("④ rho=独立月键重算值",
          abs(d['data']['pearson_returns'] - ref_pearson(ca, cb)) < 1e-12,
          f"{d['data']['pearson_returns']} vs {ref_pearson(ca, cb)}")
    check("④ mode=month_grid", al['mode'] == 'month_grid')
    if VINTAGE:
        check("④ 冻结: -0.053494577656193316, 共同 2025-11..2026-09=11月, "
              "n_chg=10, a_drop=2/b_drop=9",
              d['data']['pearson_returns'] == -0.053494577656193316
              and al['n_common_observations'] == 11
              and al['common_first'] == '2025-11' and al['common_last'] == '2026-09'
              and d['data']['n_change_pairs'] == 10
              and al['a_dropped'] == 2 and al['b_dropped'] == 9,
              f"{d['data']['pearson_returns']} {al['n_common_observations']} "
              f"{al['common_first']}..{al['common_last']} {d['data']['n_change_pairs']} "
              f"{al['a_dropped']}/{al['b_dropped']}")
    else:
        skip_case("④ 冻结字面量", "vintage 非 20261108")

    # ── ⑤ 月就业×月通胀: 月×月月键化后数值不变 ──
    print("[⑤] UNEMPLOYMENT×CPI(月×月月键内交,01锚下月键≡日键)")
    ca, cb, keys = indep_changes(raw_series('UNEMPLOYMENT'), 'rate',
                                 raw_series('CPI'), 'price', month_keys=True)
    rc, d = raw_compare('UNEMPLOYMENT,CPI')
    al = d['data']['alignment']
    check("⑤ A-fin 后 mode=month_grid",
          al['mode'] == 'month_grid', al['mode'])
    check("⑤ rho=独立月键重算值",
          abs(d['data']['pearson_returns'] - ref_pearson(ca, cb)) < 1e-12)
    if VINTAGE:
        check("⑤ 冻结不变性: 0.07758861462882527, n_common=20, n_chg=19, "
              "a_drop=1(2026-10 末端独有)",
              d['data']['pearson_returns'] == 0.07758861462882527
              and al['n_common_observations'] == 20
              and d['data']['n_change_pairs'] == 19
              and al['a_dropped'] == 1,
              f"{d['data']['pearson_returns']} {al['n_common_observations']} "
              f"{d['data']['n_change_pairs']} {al['a_dropped']}")
    else:
        skip_case("⑤ 冻结字面量", "vintage 非 20261108")

    # ── ⑥ 跨交易日历: SHCOMP×SPX + 哥伦布日微案例 ──
    print("[⑥] SHCOMP×SPX 跨历掉落+date_gap;UST_10Y×SPX 十月窗哥伦布日")
    ca, cb, keys = indep_changes(raw_series('SHCOMP'), 'price',
                                 raw_series('SPX'), 'price')
    rc, d = raw_compare('SHCOMP,SPX')
    al = d['data']['alignment']
    check("⑥ n_level=独立重算共同观测数",
          al['n_level_observations'] == len(keys),
          f"{al['n_level_observations']} vs {len(keys)}")
    check("⑥ b_dropped>0(美股侧多于共同窗,春节/国庆错位)",
          al['b_dropped'] > 0, str(al['b_dropped']))
    check("⑥ date_gap 警示在场(春节/国庆 11 天断点)",
          any('date_gap' in w for w in (json.loads(json.dumps(d)).get('warnings') or [])),
          str(d.get('warnings')))
    rc, d = raw_compare('UST_10Y,SPX', '--start', '2026-10-01',
                        '--end', '2026-10-31')
    check("⑥附 哥伦布日(2026-10-12 债休股开): 十月窗 b_dropped=1",
          d['data']['alignment']['b_dropped'] == 1,
          str(d['data']['alignment']['b_dropped']))

    # ── ⑧ 泄漏披露三字段(真实 registry 驱动) ──
    print("[⑧] CPI×SPX: release_note+time_semantics+research_mode_gate")
    rc, d = raw_compare('CPI,SPX')
    cpi = [s for s in d['data']['sides'] if s['metric_id'] == 'CPI'][0]
    gate = d['data']['alignment']['research_mode_gate']
    check("⑧ sides.release_note 含'发布日不可得'",
          '发布日不可得' in (cpi.get('release_note') or ''))
    check("⑧ time_semantics={calendar_month, release:false}",
          cpi['time_semantics'] == {'observation_period_kind': 'calendar_month',
                                    'release_date_available': False},
          str(cpi['time_semantics']))
    check("⑧ gate.event_study='blocked: 无发布日…'",
          gate['event_study'].startswith('blocked: 无发布日'))
    # Charter7-1(2026-11-10)回转: 70102d5 把判据校准到"同日 _vN 在场性",
    # 方向反了——正确判据=**查询时窗内跨日 vintage 在场性**(research_snapshot
    # 基础日期)。本案例无 --start=当前窗: 现役快照即当前时点信息集→恒
    # available(同日 _vN 只是附加披露,不构成跨日 vintage);历史窗/同日修订
    # 两形态的边界断言在 ⑨ fixture 完成。
    check("⑧ 当前窗(无 --start)→available(现役快照即当前时点信息集)",
          gate['realtime_info_set'].startswith(
              'available(现役快照即当前时点信息集'),
          gate['realtime_info_set'])
    check("⑧ realtime_vintage_dates=跨日vintage清单随行(非同日_vN判据)",
          isinstance(gate.get('realtime_vintage_dates'), list),
          str(gate.get('realtime_vintage_dates')))
    _RT_GATE = gate['realtime_info_set']

    # ── ⑩ ICSA×SPX 现状锁(不升级 empty_common) ──
    print("[⑩] ICSA×SPX 现状四要素锁(ok/mode=exact_date/n=0/rho=None)")
    rc, d = raw_compare('ICSA,SPX')
    al = d['data']['alignment']
    check("⑩ ok=true + mode=exact_date(周频×日频不走月键,维持现状)",
          d['ok'] and al['mode'] == 'exact_date', al['mode'])
    check("⑩ n_level=n_chg=0, rho=None",
          al['n_level_observations'] == 0 and d['data']['n_change_pairs'] == 0
          and d['data']['pearson_returns'] is None)
    check("⑩ sample_note=不可计算文案",
          (d['data'].get('sample_note') or '').startswith('n_change_pairs=0'))
    if VINTAGE:
        check("⑩ a_dropped=96, b_dropped=251",
              al['a_dropped'] == 96 and al['b_dropped'] == 251,
              f"{al['a_dropped']}/{al['b_dropped']}")
    else:
        skip_case("⑩ a/b_dropped 冻结字面量", "vintage 非 20261108")

    # ── ①附加: --lag 5 独立重算 ──
    print("[①附加] SPX×UST_10Y --lag 5(B 领先 5 个变化对)")
    ca, cb, keys = indep_changes(raw_series('SPX'), 'price',
                                 raw_series('UST_10Y'), 'rate')
    k = 5
    xs = [ca[i] for i in range(len(ca)) if 0 <= i - k < len(cb)]
    ys = [cb[i - k] for i in range(len(ca)) if 0 <= i - k < len(cb)]
    rc, d = raw_compare('SPX,UST_10Y', '--lag', '5')
    lag = d['data']['lagged']
    check("①附 lag5 rho=独立平移重算值, n_lag=独立计数",
          abs(lag['rho'] - ref_pearson(xs, ys)) < 1e-12
          and lag['n_lag_pairs'] == len(xs),
          f"{lag['rho']} vs {ref_pearson(xs, ys)} n={lag['n_lag_pairs']}")

# ── ⑨ _vN 历史版本(fixture 注入,无快照环境也执行) ──
print("[⑨] 同日多版本 + Charter7-1 realtime 门三形态(跨日vintage判据)")
import research_provenance as rp          # noqa: E402 (点时取版受审面)
import ia_cli                             # noqa: E402 (仅 _has_vn_history 助手)
import analog_engine as ae                # noqa: E402 (realtime_gate_text 纯函数)
with tempfile.TemporaryDirectory() as td:
    base = {'snapshot_id': 'research_snapshot_20991231', 'target_date': '20991231',
            'research_as_of': '2099-12-31T18:00:00+08:00'}
    v2 = dict(base, snapshot_id='research_snapshot_20991231_v2',
              note='修订版')
    json.dump(base, open(os.path.join(td, 'research_snapshot_20991231.json'), 'w'))
    json.dump(v2, open(os.path.join(td, 'research_snapshot_20991231_v2.json'), 'w'))
    snap_sel, path_or_reason = rp.select_snapshot('20991231', td)
    check("⑨ 同日 base+_v2 → select_snapshot 取 _v2",
          isinstance(snap_sel, dict)
          and snap_sel.get('snapshot_id') == 'research_snapshot_20991231_v2',
          str(path_or_reason))
    check("⑨ _has_vn_history(_v2 在场)=True",
          ia_cli._has_vn_history('20991231', data_dir=td) is True)
    check("⑨ _has_vn_history(仅 base)=False(同日目录无 _vN)",
          (json.dump(base, open(os.path.join(td, 'research_snapshot_20991231_v2.json'), 'w')),
           os.remove(os.path.join(td, 'research_snapshot_20991231_v2.json')),
           ia_cli._has_vn_history('20991231', data_dir=td) is False)[2])
    # ── Charter7-1: 判据=查询起点月窗内跨日 vintage(基础日期)在场性 ──
    # fixture: 2099-10-31 跨日 vintage + 2099-12-31 base+_v2(同日修订)。
    # 同日 _v2 归并到基础日期,不新增 vintage 日期。
    json.dump({'snapshot_id': 'research_snapshot_20991031',
               'target_date': '20991031'},
              open(os.path.join(td, 'research_snapshot_20991031.json'), 'w'))
    vints = rp.vintage_dates(td)
    check("⑨ vintage_dates=基础日期升序(_vN 归并不新增日期)",
          vints == ['20991031', '20991231'], str(vints))
    # 形态①当前窗(无 --start): available——现役快照即当前时点信息集;
    # 同日 _vN 在场性不参与判定
    check("⑨ 形态① 当前窗→available(现役快照即当前时点信息集)",
          ae.realtime_gate_text(None, None, vints).startswith(
              'available(现役快照即当前时点信息集'),
          ae.realtime_gate_text(None, None, vints))
    # 形态②历史窗: 起点月窗内存在跨日 vintage→available(点时取版)
    g2 = ae.realtime_gate_text('20991201', '20991231', vints,
                               same_day_revision=True)
    check("⑨ 形态② 历史窗(窗内有跨日vintage)→available+同日修订仅披露",
          g2.startswith('available(查询起点月窗内存在跨日vintage快照:20991231')
          and '当日修订版在场' in g2, g2)
    g2b = ae.realtime_gate_text('20991001', '20991031', vints)
    check("⑨ 形态② 10月窗→available(20991031 vintage 在场)",
          g2b.startswith('available(查询起点月窗内存在跨日vintage快照:20991031'),
          g2b)
    # 形态③历史窗无跨日 vintage→blocked(给现存清单+如实原因);同日 _vN
    # 在场也不翻转判定(修订值≠当时值)——70102d5 的"同日_vN⇒available"
    # 方向反转回归锁
    g3 = ae.realtime_gate_text('20990901', '20990930', vints,
                               same_day_revision=True)
    check("⑨ 形态③ 历史窗无跨日vintage→blocked(同日_vN在场也不翻转)",
          g3.startswith('blocked: 查询期20990901~20990930起点月窗内无vintage快照')
          and '不得以今日修订口径冒充当时值' in g3
          and '20991031' in g3 and '20991231' in g3, g3)
    g3b = ae.realtime_gate_text('20990901', '20990930', vints)
    check("⑨ 形态③ 无同日修订披露尾注→同一 blocked 判定(在场性不参与)",
          g3b.startswith('blocked: 查询期20990901~20990930'), g3b)
# 真实面: 用真实 data/daily 的跨日 vintage 清单做同判据边界(纯函数,零
# 数据依赖);无快照环境(CI)同样可跑(空清单→全部历史窗 blocked 仍如实)。
_real_vints = rp.vintage_dates(DAILY)
if _real_vints:
    _vm = _real_vints[0][:6]
    check("⑨ 真实面: 最早vintage起点月窗→available(跨日vintage判据)",
          ae.realtime_gate_text(_vm + '01', _vm + '31',
                                _real_vints).startswith(
              'available(查询起点月窗内存在跨日vintage快照'),
          f"vints={_real_vints[:3]}")
    check("⑨ 真实面: 早于最早vintage的历史窗→blocked+现存清单",
          ae.realtime_gate_text('20000101', '20000131', _real_vints).startswith(
              'blocked: 查询期20000101~20000131起点月窗内无vintage快照'),
          '')
else:
    check("⑨ 真实面: 无快照目录→历史窗 blocked(如实,不造vintage)",
          ae.realtime_gate_text('20990901', '20990930', []).startswith(
              'blocked: 查询期20990901~20990930'), '')

print()
print("═" * 64)
print(f"结果: {PASS}通过 / {FAIL}失败 / {SKIP}按设计跳过")
print("═" * 64)
sys.exit(0 if FAIL == 0 else 1)
