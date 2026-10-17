#!/usr/bin/env python3
"""真实数据验收(spec §18,第七轮Phase 5)

目的: 用**独立外部可信来源**核验采集-事实引擎-研究快照全链路的真实输出,
并独立复算关键金融计算(周/MTD/YTD口径与基准日语义)。

数据纪律:
- 本脚本只接受**真实采集数据**(global/macro/china/rate_economy_*.json),
  SYNTHETIC fixture测试在tests/目录,二者严格分离;
- 外部源不可达时如实标注"待复核",绝不以他源冒充或编造;
- 不写任何采集数据目录: 快照构建到临时目录,验收报告写--out-dir(默认output/acceptance)。

独立来源(与采集通道不同源):
- 美债收益率: home.treasury.gov官方日频收益率曲线 (采集侧=FRED DGS系列)
- BTC: Coinbase Exchange官方candles (采集侧=yfinance BTC-USD)
- 黄金: Coinbase PAXG(黄金代币,现货代理,披露口径) vs 采集侧COMEX期货
- 上证指数: hq.sinajs.cn实时/收盘 (采集侧=东财/腾讯通道)
- SPX/WTI: FRED SP500/DCOILWTICO (采集侧=yfinance ^GSPC/CL=F)
  WTI为期货vs现货口径差,宽容差+披露。

运行: python3 scripts/real_data_acceptance.py --data-dir <真实data/daily> [--out-dir DIR]
"""
import argparse
import csv
import io
import json
import os
import re
import sys
import tempfile
from datetime import datetime, date, timedelta

import requests

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fact_engine as fe          # noqa: E402
import snapshot_builder as sb     # noqa: E402

TOL = {  # (容忍偏差%, 说明)
    'treasury_ust': (0.03, '官方面值收益率vs FRED DGS,同口径,3bp内'),
    'coinbase_btc': (0.5, 'Coinbase收盘vs yfinance收盘,时区/收盘定义差'),
    'paxg_gold': (1.0, 'PAXG现货代理vs COMEX期货,工具口径差,宽容差'),
    'sina_shcomp': (0.3, '新浪通道vs 采集通道,同标的'),
    'fred_spx': (0.5, 'FRED SP500 vs yfinance ^GSPC'),
    'fred_wti_spot': (2.0, 'WTI现货(FRED)vs WTI期货(yfinance),期现口径差'),
}


def latest_real_day(data_dir, today_ymd):
    """最新一个四源齐全的真实采集日(≤today,5天新鲜窗)。"""
    def days_with(prefix):
        out = set()
        for fn in os.listdir(data_dir):
            m = re.match(rf'{prefix}_(\d{{8}})\.json$', fn)
            if m:
                out.add(m.group(1))
        return out
    common = (days_with('global') & days_with('macro')
              & days_with('china') & days_with('rate_economy'))
    eligible = sorted(d for d in common if d <= today_ymd)
    for d in reversed(eligible):
        lag = (date(int(today_ymd[:4]), int(today_ymd[4:6]), int(today_ymd[6:]))
               - date(int(d[:4]), int(d[4:6]), int(d[6:]))).days
        if lag <= 5:
            return d
    return None


# ── 独立来源获取(任一失败→None,如实降级) ─────────────────────────────
def fetch_treasury_ust(year, want_dates):
    """返回{iso_date: {col_name: value}};官方CSV。失败返回{}。"""
    url = (f"https://home.treasury.gov/resource-center/data-chart-center/interest-rates/"
           f"daily-treasury-rates.csv/{year}/all?type=daily_treasury_yield_curve"
           f"&field_tdr_date_value={year}&page&_format=csv")
    try:
        r = requests.get(url, timeout=25)
        r.raise_for_status()
        rows = list(csv.DictReader(io.StringIO(r.text)))
        out = {}
        for row in rows:
            d = row.get('Date', '')
            m = re.match(r'(\d{2})/(\d{2})/(\d{4})', d)
            if not m:
                continue
            iso = f"{m.group(3)}-{m.group(1)}-{m.group(2)}"
            if iso in want_dates:
                out[iso] = row
        return out
    except Exception as e:
        print(f"  ⚠️ Treasury.gov不可达: {e}")
        return {}


def fetch_coinbase_close(product, start_iso, end_iso):
    """返回{iso_date_utc: close};granularity=日K。失败返回{}。"""
    try:
        r = requests.get(
            f'https://api.exchange.coinbase.com/products/{product}/candles',
            params={'granularity': 86400,
                    'start': f"{start_iso}T00:00:00Z", 'end': f"{end_iso}T00:00:00Z"},
            timeout=20)
        r.raise_for_status()
        out = {}
        for c in r.json():          # [time, low, high, open, close, volume]
            ts = c[0]
            iso = datetime.utcfromtimestamp(ts).date().isoformat()
            out[iso] = float(c[4])
        return out
    except Exception as e:
        print(f"  ⚠️ Coinbase {product}不可达: {e}")
        return {}


def fetch_sina_index(code):
    """新浪指数快照 → (close, iso_date)或None。"""
    try:
        r = requests.get(f'https://hq.sinajs.cn/list={code}',
                         headers={'Referer': 'https://finance.sina.com.cn'}, timeout=15)
        r.encoding = 'gbk'
        m = re.search(r'"([^"]+)"', r.text)
        if not m:
            return None
        parts = m.group(1).split(',')
        if len(parts) < 4:
            return None
        return float(parts[3]), parts[30] if len(parts) > 30 else None
    except Exception as e:
        print(f"  ⚠️ 新浪不可达: {e}")
        return None


def fetch_fred_obs(series_id, api_key, limit=8):
    """FRED最近观测 → [(iso_date, value)];失败返回[]。"""
    try:
        r = requests.get('https://api.stlouisfed.org/fred/series/observations',
                         params={'series_id': series_id, 'api_key': api_key,
                                 'file_type': 'json', 'sort_order': 'desc',
                                 'limit': limit}, timeout=20)
        return [(o['date'], float(o['value'])) for o in r.json().get('observations', [])
                if o.get('value', '.') not in ('.', None)]
    except Exception as e:
        print(f"  ⚠️ FRED {series_id}不可达: {e}")
        return []


# ── 独立复算(口径与fact_engine独立实现,逐行重写非引用) ──────────────────
def independent_period_returns(dates, values, obs_date):
    """独立复算周/MTD/YTD(基准=期前最后收盘)。返回dict或None。"""
    pairs = sorted(zip(dates, values))
    obs = str(obs_date)[:10]
    prior = [(d, v) for d, v in pairs if d <= obs]
    if not prior:
        return None
    cur_d, cur = prior[-1]
    year_start = f"{cur_d[:4]}-01-01"
    month_start = f"{cur_d[:7]}-01"

    def last_before(cutoff_inclusive, strict):
        cands = [(d, v) for d, v in prior if (d < cutoff_inclusive if strict
                                              else d <= cutoff_inclusive)]
        return cands[-1] if cands else None

    # ISO周: 观测日所在ISO周的周一
    y, w, _ = date.fromisoformat(cur_d).isocalendar()
    # ISO周一起始日(独立推算: 1月4日所在周的周一 + (w-1)*7)
    jan4 = date(y, 1, 4)
    jy, jw, _ = jan4.isocalendar()
    week_monday = jan4 + timedelta(weeks=w - jw, days=-jan4.weekday())

    out = {'obs': cur_d, 'close': cur}
    wk = last_before(week_monday.isoformat(), strict=True)
    if wk:
        out['week_pct'] = (cur / wk[1] - 1) * 100 if wk[1] else None
        out['week_basis'] = wk[0]
    mtd = last_before(month_start, strict=False)   # 前月末(含)
    if mtd and mtd[0] < cur_d[:8] + '01':
        out['mtd_pct'] = (cur / mtd[1] - 1) * 100 if mtd[1] else None
        out['mtd_basis'] = mtd[0]
    ytd = last_before(year_start, strict=True)     # 上年末(严格期前)
    if ytd:
        out['ytd_pct'] = (cur / ytd[1] - 1) * 100 if ytd[1] else None
        out['ytd_basis'] = ytd[0]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data-dir', required=True, help='真实采集data/daily目录')
    ap.add_argument('--out-dir', default=os.path.join(ROOT_DIR, 'output', 'acceptance'))
    ap.add_argument('--skip-external', action='store_true', help='跳过外部源(离线复算验收)')
    args = ap.parse_args()

    print("=" * 60)
    print("✅ 真实数据验收(spec §18) — 独立外部来源 + 独立复算")
    print("=" * 60)

    today_ymd = datetime.now().strftime('%Y%m%d')
    day = latest_real_day(args.data_dir, today_ymd)
    if not day:
        print("❌ data-dir内5天窗口内无四源齐全的真实采集日")
        sys.exit(1)
    print(f"\n📌 验收数据日: {day}(真实采集,来源目录{args.data_dir})")

    # 快照构建到临时目录(不污染真实数据目录)
    with tempfile.TemporaryDirectory() as td:
        snap = sb.build_snapshot(target_ymd=day, data_dir=args.data_dir, out_dir=td,
                                 as_of=datetime.now().astimezone().isoformat(timespec='seconds'))
        if snap is None:
            snap_path = os.path.join(td, f'research_snapshot_{day}.json')
            if os.path.exists(snap_path):
                snap = json.load(open(snap_path))
        if snap is None:
            print("❌ 快照构建失败(该日快照已存在→不可变,读取现有)")
            sys.exit(1)
        facts = {f['metric_id']: f for f in snap.get('facts', []) if isinstance(f, dict)}
        store = snap.get('series_store') or {}
        as_of = snap.get('research_as_of', '')

        results = []   # [ {check, ours, external, source, tol_pct, verdict, note} ]

        def add(check, ours, ext, source, tol, verdict, note=''):
            results.append({'check': check, 'ours': ours, 'external': ext,
                            'source': source, 'tol_pct': tol,
                            'verdict': verdict, 'note': note})

        def fact_val(mid):
            f = facts.get(mid)
            return (f or {}).get('value'), (f or {}).get('observation_date')

        if not args.skip_external:
            print("\n── A. 独立外部来源核验 ──")
            # A1 Treasury.gov UST 2Y/10Y/30Y
            ours10, obs10 = fact_val('UST_10Y')
            want = {str(obs10)[:10]} if obs10 else set()
            trows = fetch_treasury_ust(int(day[:4]), want) if want else {}
            tmap = {'UST_10Y': '10 Yr', 'UST_2Y': '2 Yr', 'UST_30Y': '30 Yr'}
            for mid, col in tmap.items():
                v, od = fact_val(mid)
                row = trows.get(str(od)[:10]) if od else None
                if v is None:
                    add(f'{mid}外部核验', None, None, 'treasury.gov', TOL['treasury_ust'][0],
                        'SKIP', '快照无该事实')
                elif row and row.get(col):
                    ext = float(row[col])
                    dev = abs(v - ext) / abs(ext) * 100 if ext else None
                    verdict = ('PASS' if dev is not None and dev <= TOL['treasury_ust'][0]
                               else 'FAIL')
                    add(f'{mid}外部核验', f"{v}%({od})", f"{ext}%", 'treasury.gov官方曲线',
                        TOL['treasury_ust'][0], verdict,
                        f"偏差{dev:.3f}pp内含{TOL['treasury_ust'][1]}" if dev is not None else '')
                else:
                    add(f'{mid}外部核验', f"{v}%({od})", None, 'treasury.gov',
                        TOL['treasury_ust'][0], 'DEGRADED', '官方CSV无该观测日(发布节奏)→待复核')

            # A2 Coinbase BTC
            v, od = fact_val('BTC')
            cc = fetch_coinbase_close('BTC-USD', str(od)[:10] if od else '',
                                      str(date.today().isoformat()))
            ext = cc.get(str(od)[:10]) if od else None
            if v is not None and ext:
                dev = abs(v - ext) / ext * 100
                add('BTC外部核验', f"{v:,.0f}({od})", f"{ext:,.0f}", 'Coinbase Exchange日K',
                    TOL['coinbase_btc'][0], 'PASS' if dev <= TOL['coinbase_btc'][0] else 'FAIL',
                    f"偏差{dev:.2f}%")
            elif v is not None:
                add('BTC外部核验', f"{v:,.0f}({od})", None, 'Coinbase Exchange',
                    TOL['coinbase_btc'][0], 'DEGRADED', '外部源无该日K→待复核')

            # A3 PAXG黄金现货代理 vs GOLD_F期货
            v, od = fact_val('GOLD_F')
            pg = fetch_coinbase_close('PAXG-USD', str(od)[:10] if od else '',
                                      str(date.today().isoformat()))
            ext = pg.get(str(od)[:10]) if od else None
            if v is not None and ext:
                dev = abs(v - ext) / ext * 100
                add('GOLD_F外部核验', f"{v:,.1f}({od})", f"{ext:,.1f}", 'Coinbase PAXG(现货代理)',
                    TOL['paxg_gold'][0], 'PASS' if dev <= TOL['paxg_gold'][0] else 'FAIL',
                    f"{TOL['paxg_gold'][1]};偏差{dev:.2f}%")
            elif v is not None:
                add('GOLD_F外部核验', f"{v:,.1f}({od})", None, 'Coinbase PAXG',
                    TOL['paxg_gold'][0], 'DEGRADED', '外部源无该日K→待复核')

            # A4 新浪上证
            v, od = fact_val('SHCOMP')
            sina = fetch_sina_index('sh000001')
            if v is None:
                add('SHCOMP外部核验', None, None, 'hq.sinajs.cn', TOL['sina_shcomp'][0],
                    'SKIP', '快照无SHCOMP事实(采集缺口,如实记录)')
            elif sina:
                ext, ext_d = sina
                dev = abs(v - ext) / ext * 100
                add('SHCOMP外部核验', f"{v:,.2f}({od})", f"{ext:,.2f}", 'hq.sinajs.cn sh000001',
                    TOL['sina_shcomp'][0],
                    'PASS' if dev <= TOL['sina_shcomp'][0] else 'FAIL',
                    f"偏差{dev:.2f}%(验收时点为实时价,与采集收盘存在日内差)")
            else:
                add('SHCOMP外部核验', f"{v:,.2f}({od})", None, 'hq.sinajs.cn',
                    TOL['sina_shcomp'][0], 'DEGRADED', '新浪通道不可达→待复核')

            # A5 FRED SP500 vs SPX
            v, od = fact_val('SPX')
            try:
                from env_config import FRED_API_KEY
            except ImportError:
                FRED_API_KEY = None
            if v is None:
                add('SPX外部核验', None, None, 'FRED SP500', TOL['fred_spx'][0],
                    'SKIP', '快照无SPX事实')
            elif not FRED_API_KEY:
                add('SPX外部核验', f"{v:,.2f}({od})", None, 'FRED SP500',
                    TOL['fred_spx'][0], 'SKIP', '运行环境无FRED密钥→待复核(在live环境重跑)')
            else:
                obs = fetch_fred_obs('SP500', FRED_API_KEY, 10)
                match = next(((d, val) for d, val in obs), None)
                if match:
                    d, ext = match
                    dev = abs(v - ext) / ext * 100
                    add('SPX外部核验', f"{v:,.2f}({od})", f"{ext:,.2f}({d})",
                        'FRED SP500(独立于Yahoo通道)', TOL['fred_spx'][0],
                        'PASS' if dev <= TOL['fred_spx'][0] else 'FAIL',
                        f"偏差{dev:.2f}%;FRED发布滞后,比对最近可得日" )
                else:
                    add('SPX外部核验', f"{v:,.2f}({od})", None, 'FRED SP500',
                        TOL['fred_spx'][0], 'DEGRADED', 'FRED SP500近期无观测→待复核')

            # A6 FRED WTI现货 vs WTI_F期货
            v, od = fact_val('WTI_F')
            if v is None:
                add('WTI_F外部核验', None, None, 'FRED DCOILWTICO',
                    TOL['fred_wti_spot'][0], 'SKIP', '快照无WTI_F事实')
            elif not FRED_API_KEY:
                add('WTI_F外部核验', f"{v:,.2f}({od})", None, 'FRED DCOILWTICO',
                    TOL['fred_wti_spot'][0], 'SKIP', '运行环境无FRED密钥→待复核')
            else:
                obs = fetch_fred_obs('DCOILWTICO', FRED_API_KEY, 10)
                if obs:
                    d, ext = obs[0]
                    dev = abs(v - ext) / ext * 100
                    add('WTI_F外部核验', f"{v:,.2f}({od})", f"{ext:,.2f}({d})",
                        'FRED DCOILWTICO现货', TOL['fred_wti_spot'][0],
                        'PASS' if dev <= TOL['fred_wti_spot'][0] else 'FAIL',
                        f"{TOL['fred_wti_spot'][1]};偏差{dev:.2f}%")
                else:
                    add('WTI_F外部核验', f"{v:,.2f}({od})", None, 'FRED DCOILWTICO',
                        TOL['fred_wti_spot'][0], 'DEGRADED', 'FRED无近期观测→待复核')

        print("\n── B. 金融计算独立复算(口径:期前收盘基准) ──")
        for mid in ('SPX', 'GOLD_F', 'SHCOMP', 'HSI'):
            f = facts.get(mid)
            s = store.get(mid)
            if not f or not s:
                add(f'{mid}复算', None, None, '独立复算', 0.0, 'SKIP', '快照无该序列')
                continue
            ind = independent_period_returns(s['dates'], s['values'], f['observation_date'])
            d = f.get('derived') or {}
            ok_all, notes = True, []
            for period, key in (('week', 'week_pct'), ('mtd', 'mtd_pct'), ('ytd', 'ytd_pct')):
                eng = (d.get(period) or {})
                if eng.get('available') is False:
                    if ind and ind.get(key) is None:
                        notes.append(f"{period}:双方判数据不足✓")
                    else:
                        ok_all = False
                        notes.append(f"{period}:引擎判不足但复算有值✗")
                    continue
                ev, iv = eng.get('pct_change'), (ind or {}).get(key)
                if ev is None or iv is None or abs(ev - iv) > 0.01:
                    ok_all = False
                    notes.append(f"{period}:引擎{ev}vs复算{round(iv, 2) if iv else None}✗")
                else:
                    notes.append(f"{period}={ev:+.2f}%✓(基准{ind.get(period + '_basis', '?')})")
            add(f'{mid}周/MTD/YTD复算', f"收盘{f.get('value'):,.2f}({f.get('observation_date')})",
                ' | '.join(notes), '本脚本独立实现(非引用fact_engine)', 0.0,
                'PASS' if ok_all else 'FAIL', '基准日期与涨跌幅须与引擎一致')

        print("\n── C. 基准日语义断言 ──")
        s = store.get('SPX')
        f = facts.get('SPX')
        if s and f:
            ind = independent_period_returns(s['dates'], s['values'], f['observation_date'])
            if ind:
                yb, mb, wb = ind.get('ytd_basis'), ind.get('mtd_basis'), ind.get('week_basis')
                yy = str(f['observation_date'])[:4]
                y_ok = yb and yb < f"{yy}-01-01"
                m_ok = mb and mb <= (date(int(yy), int(str(f['observation_date'])[5:7]), 1)
                                     - timedelta(days=1)).isoformat()
                w_ok = wb and wb < ind['obs']
                verdict = 'PASS' if (y_ok and m_ok and w_ok) else 'FAIL'
                add('基准日语义(YTD=上年末/MTD=前月末/WEEK=ISO周前)',
                    f"ytd_basis={yb}", f"mtd_basis={mb} week_basis={wb}",
                    '独立复算', 0.0, verdict,
                    'YTD基准须严格早于1/1;MTD基准≤前月末;周基准=本ISO周前最后观测')

        print("\n── D. Gate A与发布语义 ──")
        ga = snap.get('gate_a') or {}
        add('Gate A状态', ga.get('status', '?'),
            f"core缺失:{','.join(ga.get('core_missing', []) or [])} "
            f"FAIL:{','.join(ga.get('core_fail', []) or [])}",
            '研究快照', 0.0, ga.get('status', 'DEGRADED'),
            'FAIL不阻断但相关结论不得生成')

        # ── 汇总输出 ──
        os.makedirs(args.out_dir, exist_ok=True)
        stamp = datetime.now().strftime('%Y%m%d_%H%M')
        n_pass = sum(1 for r in results if r['verdict'] == 'PASS')
        n_fail = sum(1 for r in results if r['verdict'] == 'FAIL')
        n_deg = sum(1 for r in results if r['verdict'] == 'DEGRADED')
        n_skip = sum(1 for r in results if r['verdict'] == 'SKIP')
        summary = {'acceptance_id': f'real_acceptance_{stamp}',
                   'data_day': day, 'data_dir': args.data_dir,
                   'snapshot_id': snap.get('snapshot_id'), 'research_as_of': as_of,
                   'data_discipline': '真实采集数据验收;fixture测试在tests/目录,二者严格分离;'
                                      '外部源不可达项如实标DEGRADED待复核,不编造',
                   'counts': {'PASS': n_pass, 'FAIL': n_fail, 'DEGRADED': n_deg, 'SKIP': n_skip},
                   'checks': results}
        jpath = os.path.join(args.out_dir, f'real_acceptance_{stamp}.json')
        with open(jpath, 'w', encoding='utf-8') as fh:
            json.dump(summary, fh, ensure_ascii=False, indent=2)
        mpath = os.path.join(args.out_dir, f'real_acceptance_{stamp}.md')
        L = [f"# 真实数据验收报告({stamp})", "",
             f"- 验收数据日: **{day}**(真实采集)| 研究截止: {as_of}",
             f"- 快照: {snap.get('snapshot_id')} | Gate A: {ga.get('status')}",
             f"- 数据纪律: {summary['data_discipline']}", "",
             f"**结果: PASS {n_pass} / FAIL {n_fail} / DEGRADED {n_deg} / SKIP {n_skip}**", "",
             "| 检查项 | 快照值 | 独立值/复算 | 来源 | 容差 | 判定 | 备注 |",
             "|---|---|---|---|---|---|---|"]
        for r in results:
            L.append(f"| {r['check']} | {r['ours']} | {r['external']} | {r['source']} "
                     f"| {r['tol_pct']} | **{r['verdict']}** | {r['note']} |")
        L += ["", "## 判定口径",
              "- PASS: 独立来源/复算与快照在容差内一致;",
              "- FAIL: 超容差(真实错误,须修数据或修代码);",
              "- DEGRADED: 外部源不可达或无该日数据→待复核(如实披露,不冒充通过);",
              "- SKIP: 快照侧缺该指标(记录,不折算为通过)。"]
        with open(mpath, 'w', encoding='utf-8') as fh:
            fh.write('\n'.join(L) + '\n')
        print(f"\n💾 验收报告: {mpath}")
        print(f"💾 JSON: {jpath}")
        print(f"\n结果: PASS {n_pass} / FAIL {n_fail} / DEGRADED {n_deg} / SKIP {n_skip}")
        sys.exit(0 if n_fail == 0 else 2)


if __name__ == '__main__':
    main()
