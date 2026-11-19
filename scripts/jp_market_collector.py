#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""日本市场采集器(IA-P1-WP-A v1.3) — 免费公开源,零凭证零API key。

通道: jp(research_provenance.SOURCE_FILE_RULES 登记: 规范文件名
jp_YYYYMMDD.json,回退窗5自然日);产出目录 data/daily。

数据源(IA-P1-WP-A-AC §一 白名单域,REPORT §零.12⑩ 定值;均免费公开):
  1. MOF 日本国债收益率曲线 jgbcme(复用 scripts/japan_rate_collector.py 的
     fetch_mof_jgb/_http_get——复用调用优先于扩展,不修改上游件):
     https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/jgbcme.csv
     → jgb.JGB_10Y / jgb.JGB_2Y(DESIGN §三(a-2) L50 键名,=registry JGB10Y/JGB2Y)
  2. FRED fredgraph IRSTCI01JPM156N(复用 fetch_fred_policy_rate):
     https://fred.stlouisfed.org/graph/fredgraph.csv?id=IRSTCI01JPM156N
     → policy_rates.BOJ_POLICY_RATE(=registry JP_POLICY_RATE 同概念)
  3. FRED fredgraph NIKKEI225(同端点形态,仅收盘口径):
     https://fred.stlouisfed.org/graph/fredgraph.csv?id=NIKKEI225
     → prices.NIKKEI225{close,date,high:null,low:null,series}

Audit-R20(2026-11-19)增长/通胀序列面(12组36格四地地图问句的正式使用):
  4. 总务省统计局 stat.go.jp CPI 月次 CSV(官方免费公开,零凭证零API key;
     R19 时点登记为非白名单域——本波随用户 R20 指令(日本 GDP/全国 CPI 优先)
     正式登记入白名单并接线;东京口径与全国口径分别采集,不以全国冒充东京):
     https://www.stat.go.jp/data/cpi/2025/csv/zmi2025aa.csv  (全国,2025基)
     https://www.stat.go.jp/data/cpi/2020/csv/zmi2020aa.csv  (全国,2020基)
     https://www.stat.go.jp/data/cpi/2025/csv/tmi2025aa.csv  (东京都区部,2025基)
     https://www.stat.go.jp/data/cpi/2020/csv/tmi2020aa.csv  (东京都区部,2020基)
     → series.JP_CPI_YOY / series.JP_CPI_TOKYO_YOY
     (総合指数水平→严格同基期内月度同比;双基期各自算同比后拼接,重叠月以
     新基期(2025=100)为准,双基期同比差>0.10pp 时 alert 如实披露)
  5. FRED fredgraph JPNRGDPEXP(实际GDP季频水平,1994+):
     → series.JP_REAL_GDP_YOY(同季去年比=(本季/去年同季−1)×100;
     FRED 载荷=最新修订值,无当时发布版本可比→序列注记 hindsight 口径)

诚实缺席(DESIGN §三(a-2) L58+REPORT §零.12⑩ 定值;键不出现,禁 0 占位):
  - 上述任一源失败→series 节该键缺席+sources_status READ_FAIL+alerts 如实。

产出档形(DESIGN §三(a-2) L45-L52 逐字+观测性附加键,REPORT §零.12⑪):
  顶层 date/generated_at/sources_status + 通道节 policy_rates/jgb/inflation/prices
  + 附加 observations(逐系列观测日)/sources(逐源url口径)/fetched_at/alerts。
  NIKKEI225.series=近端窗口观测 map{"YYYY-MM-DD": close}(窗口=GLOBAL_HISTORY_PERIOD
  对齐 global 档,默认'10y'≈2520 观测,见 nikkei_series_window;Charter6 收尾延期①
  废除旧 251 硬截断);high/low=null
  (FRED该系列仅收盘,禁以 0 占位);prev_value=源端次新观测(不可得→null)。

失败纪律(B3 同款): 源失败→节键不出现+sources_status 该源 READ_FAIL+alerts
如实;全部系列缺席→exit 1 且不产出文件(不产空壳冒充采集成功)。
零依赖: 仅标准库;复用上游件不修改(M-c 条件类未触发)。
"""
import json
import os
import sys
from datetime import date, datetime, timezone

# 仓库根进 sys.path(既有先例: china_market_collector/global_market_collector
# 同款)——`python3 scripts/jp_market_collector.py` 流水线上下文下,
# nikkei_series_window 的延迟 env_config import 才可解析(收尾修复轮①)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import japan_rate_collector as jrc   # B3 上游件: 复用调用,零修改

__all__ = ['FRED_NIKKEI_URL', 'SERIES_WINDOW', 'fetch_nikkei_series',
           'build_payload', 'save_daily', 'main']

FRED_NIKKEI_URL = ('https://fred.stlouisfed.org/graph/fredgraph.csv'
                   '?id=NIKKEI225')
# === Audit-R20(2026-11-19): 日本增长/通胀序列源(官方免费,零凭证) ============
# stat.go.jp=日本总务省统计局官方站(CPI 月次 CSV 直连);FRED fredgraph 同
# 通道既有端点形态。URL 常量登记制: 与 sources 节逐字一致(白名单登记面)。
STATGO_CPI_NATIONAL_2025B = ('https://www.stat.go.jp/data/cpi/2025/csv/'
                             'zmi2025aa.csv')
STATGO_CPI_NATIONAL_2020B = ('https://www.stat.go.jp/data/cpi/2020/csv/'
                             'zmi2020aa.csv')
STATGO_CPI_TOKYO_2025B = ('https://www.stat.go.jp/data/cpi/2025/csv/'
                          'tmi2025aa.csv')
STATGO_CPI_TOKYO_2020B = ('https://www.stat.go.jp/data/cpi/2020/csv/'
                          'tmi2020aa.csv')
FRED_JP_GDP_URL = ('https://fred.stlouisfed.org/graph/fredgraph.csv'
                   '?id=JPNRGDPEXP')
_UA_R20 = {'User-Agent': 'investment-agent-dev-jp-market-collector/1.1',
           'Connection': 'close'}
# === Charter6 收尾(A2 延期①, 2026-11-10): NIKKEI series 窗口与 global 对齐 ====
# 原 SERIES_WINDOW=251 硬截断(历史窗口参数化前的 1 年实况对齐,注释已过期)——
# 改读同一 GLOBAL_HISTORY_PERIOD(env_config 校验,默认'10y'),按近似交易日
# 数映射近端窗口;ytd/max=不截断。零依赖不变: 不 import global 采集器(其引入
# yfinance),只共享 env_config 纯函数。近似口径: 日历月≈21 个交易日/年≈252
# (FRED 日频收盘,节假日缺口由 FRED 端已吸收)。
_NIKKEI_WINDOW_BY_PERIOD = {
    '1d': 1, '5d': 5, '1mo': 21, '3mo': 63, '6mo': 126,
    '1y': 252, '2y': 504, '5y': 1260, '10y': 2520,   # ytd/max→None 不截断
}
SERIES_WINDOW = _NIKKEI_WINDOW_BY_PERIOD['10y']   # 遗留别名: 默认窗口观测数


def nikkei_series_window(period=None):
    """NIKKEI225.series 近端观测数上限(与 global 窗口同一 env/默认)。

    period=None 时读 GLOBAL_HISTORY_PERIOD(经 env_config.resolve_history_period
    校验,非法值回落'10y'并告警);显式传参同规校验。'ytd'/'max'→None=不截断。"""
    from env_config import (HISTORY_PERIOD_LEGAL,
                            resolve_history_period)
    p, fallback = resolve_history_period(
        os.environ.get('GLOBAL_HISTORY_PERIOD') if period is None else period,
        '10y')
    if fallback:
        print(f"  ⚠️ GLOBAL_HISTORY_PERIOD 非法(合法集 "
              f"{'/'.join(HISTORY_PERIOD_LEGAL)}),回落默认 10y(NIKKEI窗口≈2520)")
    return _NIKKEI_WINDOW_BY_PERIOD.get(p)      # ytd/max→None(全量)

_JGB_A2 = {'JGB10Y': 'JGB_10Y', 'JGB2Y': 'JGB_2Y'}   # registry→a-2 键名


def _now_iso():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def _fetch_or_alert(label, fetcher):
    """单源容错(B3 D10 语义同款): 网络异常→(None,alerts),不崩全程。"""
    try:
        return fetcher(), []
    except Exception as e:
        return None, [f'{label}源获取失败:{type(e).__name__}:{e}']


def _parse_fred_series(raw):
    """FRED fredgraph CSV → [(obs 'YYYY-MM-DD', value float), …](升序全序列)。

    形态同 B3 fetch_fred_policy_rate 实测: 首行 observation_date,<series_id>;
    缺失值'.'行跳过。raw 供离线测试注入。"""
    alerts = []
    text = raw.decode('utf-8')
    lines = [l for l in text.splitlines() if l.strip()]
    if not lines or not lines[0].startswith('observation_date'):
        return None, ['fred形态不符(缺observation_date表头)']
    rows = []
    for line in lines[1:]:
        cells = line.split(',')
        if len(cells) != 2:
            continue
        d, v = cells[0].strip(), cells[1].strip()
        if not v or v == '.':
            continue
        try:
            rows.append((d, float(v)))
        except ValueError:
            alerts.append(f'fred数值非法行跳过:{line!r}')
    if not rows:
        return None, ['fred无有效观测行'] + alerts
    return rows, alerts


def fetch_nikkei_series(raw=None):
    """NIKKEI225 序列获取+解析 → (rows, alerts);raw 注入则零网络。"""
    if raw is None:
        raw, a0 = _fetch_or_alert('FRED-NIKKEI', lambda: jrc._http_get(
            FRED_NIKKEI_URL, 'fred'))
        if raw is None:
            return None, a0
    rows, alerts = _parse_fred_series(raw)
    return rows, alerts


# ══ Audit-R20: stat.go.jp CPI 月次 CSV 解析 → 严格同基期月度同比序列 ═════

def _parse_statgo_cpi_levels(raw):
    """stat.go.jp 月次 CSV → 総合指数水平 [('YYYY-MM', level), …](升序)。

    形态实测(2026-11-19, zmi2025aa.csv): 首行=類・品目中日列头,第2列='総合'
    (第1列'類・品目'标签);前几行为名称/代码/权重行(首列非 YYYYMM 形),
    数据行首列='202501' 形 6 位年月、第2列=指数水平(2025基=100/2020基=100)。
    解析纯函数零网络;raw 供离线测试注入(cp932 解码)。"""
    import csv as _csv
    import io
    alerts = []
    try:
        text = raw.decode('cp932')
    except UnicodeDecodeError:
        alerts.append('statgo CPI CSV cp932 解码失败(尝试utf-8)')
        text = raw.decode('utf-8', errors='replace')
    rows = list(_csv.reader(io.StringIO(text)))
    if len(rows) < 6:
        return None, ['statgo CPI CSV 行数不足(形态不符)'] + alerts
    header = rows[0]
    if len(header) < 2 or header[1].strip() != '総合':
        return None, [f'stago CPI 列头不符(第2列={header[1] if len(header) > 1 else "?"!r}'
                       f'≠総合)'] + alerts
    out = {}
    for r in rows[1:]:
        c0 = (r[0] if r else '').strip()
        if len(c0) == 6 and c0.isdigit() and c0[:2] in ('19', '20'):
            try:
                out['%s-%s' % (c0[:4], c0[4:6])] = float(r[1])
            except (IndexError, ValueError):
                alerts.append('statgo CPI 数值非法行跳过:%r' % (c0,))
    if not out:
        return None, ['statgo CPI 无有效观测行'] + alerts
    return [(k, out[k]) for k in sorted(out)], alerts


def _statgo_yoy(levels):
    """同基期内月度同比(严格去年同月;缺基期该月不出数)。

    → [('YYYY-MM', yoy_pct), …] 升序;yoy=round((本月/去年同月−1)×100, 2)。"""
    by = dict(levels)
    out = []
    for ym, v in levels:
        y, m = int(ym[:4]), int(ym[5:7])
        pym = '%04d-%02d' % (y - 1, m)
        base = by.get(pym)
        if base:
            out.append((ym, round((v / base - 1.0) * 100.0, 2)))
    return out


def _merge_two_base_yoy(old_yoy, new_yoy, label, tol_pp=0.10):
    """双基期同比拼接: 重叠月以新基期为准,差>tol_pp 时 alert 如实。

    返回 (merged_sorted, alerts)。两基都缺席→([], alerts)。"""
    alerts = []
    old, new = dict(old_yoy), dict(new_yoy)
    for ym in sorted(set(old) & set(new)):
        if abs(old[ym] - new[ym]) > tol_pp:
            alerts.append('%s 双基期同比差超%.2fpp(%s: 2020基=%.2f 2025基=%.2f,'
                          '取2025基)' % (label, tol_pp, ym, old[ym], new[ym]))
    merged = dict(old)
    merged.update(new)
    return [(k, merged[k]) for k in sorted(merged)], alerts


def fetch_statgo_cpi_yoy(label, url_2025b, url_2020b,
                         raw_2025b=None, raw_2020b=None):
    """stat.go.jp CPI 同比序列获取(全国/东京都区部共用;零凭证直连)。

    → (yoy [('YYYY-MM', pct)], alerts);任一基期源失败→该基期缺席如实
    (两基都失败→(None, alerts))。raw 注入则零网络(离线测试)。"""
    alerts = []
    yoy_parts = []
    for tag, url, raw in (('2025基', url_2025b, raw_2025b),
                          ('2020基', url_2020b, raw_2020b)):
        if raw is None:
            import urllib.request
            try:
                req = urllib.request.Request(url, headers=_UA_R20)
                with urllib.request.urlopen(req, timeout=60) as r:
                    raw = r.read()
            except Exception as e:
                alerts.append('statgo CPI(%s,%s)获取失败:%s:%s'
                              % (label, tag, type(e).__name__, e))
                continue
        levels, a = _parse_statgo_cpi_levels(raw)
        alerts.extend(a)
        if levels:
            yoy_parts.append(_statgo_yoy(levels))
    if not yoy_parts:
        return None, alerts
    if len(yoy_parts) == 1:
        return yoy_parts[0], alerts
    merged, a = _merge_two_base_yoy(yoy_parts[0], yoy_parts[1], label)
    return merged, alerts + a


def _quarterly_yoy(rows):
    """季频水平序列 → 同季去年比 [('YYYY-MM-01', yoy_pct), …]。

    FRED 季度观测日=季首(YYYY-01/04/07/10-01);严格去年同季(−4 季)配基,
    缺基期该季不出数;yoy=round((本季/去年同季−1)×100, 2)。"""
    by = dict(rows)
    out = []
    for d, v in rows:
        y, m = int(d[:4]), int(d[5:7])
        if m not in (1, 4, 7, 10):
            continue
        base_d = '%04d-%02d-01' % (y - 1, m)
        base = by.get(base_d)
        if base:
            out.append((d, round((v / base - 1.0) * 100.0, 2)))
    return out


def fetch_jp_real_gdp_yoy(raw=None):
    """FRED JPNRGDPEXP 实际GDP季频水平→同季去年比序列。

    → (yoy [('YYYY-MM-01', pct)], alerts);raw 注入则零网络。"""
    if raw is None:
        raw, a0 = _fetch_or_alert('FRED-JP-GDP', lambda: jrc._http_get(
            FRED_JP_GDP_URL, 'fred'))
        if raw is None:
            return None, a0
    rows, alerts = _parse_fred_series(raw)
    if rows is None:
        return None, alerts
    return _quarterly_yoy(rows), alerts


def _mof_history(raw):
    """MOF jgbcme 全数据行(升序)→ [(obs, {期限列: 值})];仅次新观测用。

    与 jrc.fetch_mof_jgb 同解析口径(列头驱动/行可解析探针),供 prev_value;
    权威值仍取自 jrc.fetch_mof_jgb(复用,不双轨)。"""
    rows = []
    try:
        text = raw.decode('shift_jis')
    except UnicodeDecodeError:
        text = raw.decode('utf-8', errors='strict')
    header = None
    for line in text.splitlines():
        if not line.strip(', \r'):
            continue
        cells = [c.strip() for c in line.split(',')]
        if cells[0] == 'Date':
            header = cells
            continue
        if header and len(cells) == len(header) and '/' in cells[0]:
            try:
                y, m, d = cells[0].split('/')
                obs = f'{int(y):04d}-{int(m):02d}-{int(d):02d}'
                float(cells[1])
            except ValueError:
                continue
            rows.append((obs, {c: cells[i] for i, c in enumerate(header)
                               if c in jrc.JGB_TENORS}))
    return rows


def _leaf(value, obs, prev):
    """a-2 标量节形态(L49/L50): {value,unit,date,prev_value}。"""
    return {'value': value, 'unit': 'percent', 'date': obs, 'prev_value': prev}


def build_payload(run_date=None, mof_raw=None, fred_policy_raw=None,
                  fred_nikkei_raw=None, series_window=None):
    """组装 jp_YYYYMMDD.json 载荷(a-2 节结构;缺席节键不出现)。

    series_window: NIKKEI series 近端观测数上限;None=经
    nikkei_series_window() 读 GLOBAL_HISTORY_PERIOD(默认'10y'≈2520,
    延期①: 与 global 窗口对齐;旧硬编码 251 已废)。
    返回 (payload, n_series);n_series==0 时调用方不得落盘。"""
    rd = run_date or date.today()
    ymd = rd.strftime('%Y%m%d')
    win = nikkei_series_window() if series_window is None else series_window
    policy_rates, jgb, prices, inflation = {}, {}, {}, {}
    observations, alerts = {}, []
    sources_status = {}

    # ── 源1: MOF jgbcme(复用 B3 fetch_mof_jgb;raw 统一自取供 prev 扫描)────
    if mof_raw is None:
        mof_raw, a = _fetch_or_alert('MOF', lambda: jrc._http_get(
            jrc.MOF_JGBCME_URL))
        alerts.extend(a)
    if mof_raw is not None:
        t0 = _now_iso()
        obs, jgb_map, a = jrc.fetch_mof_jgb(mof_raw)
        alerts.extend(a)
        if obs is None:
            sources_status['MOF_JGBCME'] = {'status': 'READ_FAIL',
                                            'retrieved_at': t0}
            alerts.append('MOF源解析失败→jgb 节缺席(如实,不伪造)')
        else:
            hist = _mof_history(mof_raw)
            prev_row = hist[-2][1] if len(hist) >= 2 else {}
            for reg_id, v in sorted(jgb_map.items()):
                a2 = _JGB_A2.get(reg_id)
                if a2 is None:            # JGB5Y 非 a-2 面,不重复登记
                    continue
                try:
                    prev = float(prev_row.get(reg_id.replace('JGB', '')))
                except (TypeError, ValueError):
                    prev = None
                jgb[a2] = _leaf(v, obs, prev)
                observations[a2] = obs
            sources_status['MOF_JGBCME'] = {'status': 'EXACT',
                                            'retrieved_at': t0}
    else:
        sources_status['MOF_JGBCME'] = {'status': 'READ_FAIL',
                                        'retrieved_at': None}
        alerts.append('MOF源获取失败→jgb 节缺席(如实,不伪造)')

    # ── 源2: FRED IRSTCI01JPM156N(复用 B3 fetch_fred_policy_rate)──────────
    if fred_policy_raw is None:
        fred_policy_raw, a = _fetch_or_alert('FRED-POLICY', lambda: jrc._http_get(
            jrc.FRED_POLICY_URL, 'fred'))
        alerts.extend(a)
    if fred_policy_raw is not None:
        t0 = _now_iso()
        pobs, pv, a = jrc.fetch_fred_policy_rate(fred_policy_raw)
        alerts.extend(a)
        if pobs is None:
            sources_status['FRED_POLICY'] = {'status': 'READ_FAIL',
                                             'retrieved_at': t0}
            alerts.append('FRED政策利率源解析失败→policy_rates 节缺席(如实)')
        else:
            rows, a2 = _parse_fred_series(fred_policy_raw)
            alerts.extend(a2)
            prev = rows[-2][1] if rows and len(rows) >= 2 else None
            policy_rates['BOJ_POLICY_RATE'] = _leaf(pv, pobs, prev)
            observations['BOJ_POLICY_RATE'] = pobs
            sources_status['FRED_POLICY'] = {'status': 'EXACT',
                                             'retrieved_at': t0}
    else:
        sources_status['FRED_POLICY'] = {'status': 'READ_FAIL',
                                         'retrieved_at': None}
        alerts.append('FRED政策利率源获取失败→policy_rates 节缺席(如实)')

    # ── 源3: FRED NIKKEI225(仅收盘口径;high/low=null)────────────────────
    rows = None
    if fred_nikkei_raw is not None:
        rows, a = _parse_fred_series(fred_nikkei_raw)
        alerts.extend(a)
    else:
        raw, a = _fetch_or_alert('FRED-NIKKEI', lambda: jrc._http_get(
            FRED_NIKKEI_URL, 'fred'))
        alerts.extend(a)
        if raw is not None:
            rows, a = _parse_fred_series(raw)
            alerts.extend(a)
    if rows is not None:
        t0 = _now_iso()
        close_d, close_v = rows[-1]
        prev = rows[-2][1] if len(rows) >= 2 else None
        prices['NIKKEI225'] = {
            'close': close_v, 'date': close_d,
            'high': None, 'low': None,      # FRED系列仅收盘→null(禁0占位)
            'series': ({d: v for d, v in rows[-win:]} if win
                       else dict(rows)),   # win=None(ytd/max)→全量不截断
        }
        observations['NIKKEI225'] = close_d
        sources_status['FRED_NIKKEI225'] = {'status': 'EXACT', 'retrieved_at': t0}
    else:
        sources_status['FRED_NIKKEI225'] = {'status': 'READ_FAIL',
                                            'retrieved_at': None}
        alerts.append('FRED日经源失败→prices 节缺席(如实,不伪造)')

    # ── Audit-R20: 日本增长/通胀序列(stat.go.jp CPI + FRED GDP)─────────
    # series 节=snapshot_builder.merge_series_sections('jp' 通道,
    # collector='jp_market_collector' 权属门)直读形态 {'dates','values'}。
    series_out = {}
    inflation['JP_CPI_YOY'] = None      # 占位: 成功后填点值面
    t0 = _now_iso()
    yoy, a = fetch_statgo_cpi_yoy('全国CPI', STATGO_CPI_NATIONAL_2025B,
                                  STATGO_CPI_NATIONAL_2020B)
    alerts.extend(a)
    if yoy:
        series_out['JP_CPI_YOY'] = {
            'dates': ['%s-01' % ym for ym, _ in yoy],
            'values': [v for _, v in yoy]}
        inflation['JP_CPI_YOY'] = _leaf(yoy[-1][1], '%s-01' % yoy[-1][0],
                                        yoy[-2][1] if len(yoy) > 1 else None)
        inflation['JP_CPI_YOY']['freq'] = 'Monthly'
        observations['JP_CPI_YOY'] = '%s-01' % yoy[-1][0]
        sources_status['STATGO_CPI_NATIONAL'] = {'status': 'EXACT',
                                                 'retrieved_at': t0}
    else:
        inflation.pop('JP_CPI_YOY', None)
        sources_status['STATGO_CPI_NATIONAL'] = {'status': 'READ_FAIL',
                                                 'retrieved_at': t0}
        alerts.append('stat.go.jp 全国CPI源失败→series.JP_CPI_YOY 缺席(如实)')
    t0 = _now_iso()
    yoy_t, a = fetch_statgo_cpi_yoy('東京都区部CPI', STATGO_CPI_TOKYO_2025B,
                                    STATGO_CPI_TOKYO_2020B)
    alerts.extend(a)
    if yoy_t:
        series_out['JP_CPI_TOKYO_YOY'] = {
            'dates': ['%s-01' % ym for ym, _ in yoy_t],
            'values': [v for _, v in yoy_t]}
        observations['JP_CPI_TOKYO_YOY'] = '%s-01' % yoy_t[-1][0]
        sources_status['STATGO_CPI_TOKYO'] = {'status': 'EXACT',
                                              'retrieved_at': t0}
    else:
        sources_status['STATGO_CPI_TOKYO'] = {'status': 'READ_FAIL',
                                              'retrieved_at': t0}
        alerts.append('stat.go.jp 東京CPI源失败→series.JP_CPI_TOKYO_YOY 缺席'
                      '(如实)')
    t0 = _now_iso()
    gdp_yoy, a = fetch_jp_real_gdp_yoy()
    alerts.extend(a)
    if gdp_yoy:
        series_out['JP_REAL_GDP_YOY'] = {
            'dates': [d for d, _ in gdp_yoy],
            'values': [v for _, v in gdp_yoy],
            'history_note': 'FRED JPNRGDPEXP 载荷=最新修订值(无当时发布版本'
                            '可比)——研究/渲染面按事后回顾口径标注'}
        observations['JP_REAL_GDP_YOY'] = gdp_yoy[-1][0]
        sources_status['FRED_JP_GDP'] = {'status': 'EXACT', 'retrieved_at': t0}
    else:
        sources_status['FRED_JP_GDP'] = {'status': 'READ_FAIL',
                                         'retrieved_at': t0}
        alerts.append('FRED 日本GDP源失败→series.JP_REAL_GDP_YOY 缺席(如实)')

    payload = {
        'date': ymd,
        'generated_at': _now_iso(),
        'sources_status': sources_status,
        'observations': observations,
        'sources': {
            'MOF_JGBCME': {'url': jrc.MOF_JGBCME_URL,
                           'note': 'MOF jgbcme收益率曲线(复用japan_rate_collector)'},
            'FRED_POLICY': {'url': jrc.FRED_POLICY_URL,
                            'note': 'FRED月频系列IRSTCI01JPM156N(复用B3采集器)'},
            'FRED_NIKKEI225': {'url': FRED_NIKKEI_URL,
                               'note': 'FRED日频系列NIKKEI225(仅收盘口径,'
                                       'high/low=null)'},
            'STATGO_CPI_NATIONAL': {
                'url': STATGO_CPI_NATIONAL_2025B,
                'note': '总务省统计局全国CPI月次CSV(2025基+2020基拼接;'
                        '総合指数水平→同基期内严格同月同比,Audit-R20 接线)'},
            'STATGO_CPI_TOKYO': {
                'url': STATGO_CPI_TOKYO_2025B,
                'note': '总务省统计局東京都区部CPI月次CSV(2025基+2020基拼接;'
                        '东京口径与全国口径分别列示,不以全国冒充东京)'},
            'FRED_JP_GDP': {'url': FRED_JP_GDP_URL,
                            'note': 'FRED季频JPNRGDPEXP实际GDP水平→同季去年比'
                                    '(最新修订值=事后回顾口径,Audit-R20 接线)'},
        },
        'fetched_at': _now_iso(),
        'alerts': alerts,
    }
    for section, obj in (('policy_rates', policy_rates), ('jgb', jgb),
                         ('inflation', inflation), ('prices', prices)):
        if obj:
            payload[section] = obj          # 缺席节键不出现(L58)
    # Audit-R20: 全史序列节(merge_series_sections 'jp' 通道权属门直读)
    if series_out:
        payload['series'] = series_out
    n_series = (len(policy_rates) + len(jgb) + len(inflation) + len(prices)
                + len(series_out))
    return payload, n_series


def save_daily(data_dir, payload):
    """原子写 data_dir/jp_{date}.json(先tmp后replace,防半写)。"""
    path = os.path.join(data_dir, f"jp_{payload['date']}.json")
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)
    return path


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    data_dir = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), 'data', 'daily')
    if '--data-dir' in argv:
        data_dir = argv[argv.index('--data-dir') + 1]
    payload, n = build_payload()
    sections = [k for k in ('policy_rates', 'jgb', 'inflation', 'prices',
                            'series') if k in payload]
    print(f"[jp_market_collector] run_date={payload['date']} "
          f"sections={sections} observations={payload['observations']}")
    for a in payload['alerts']:
        print(f"[jp_market_collector] ⚠️ {a}")
    if n == 0:
        print('[jp_market_collector] ❌ 全部系列缺席——不产出文件,exit 1')
        return 1
    path = save_daily(data_dir, payload)
    print(f'[jp_market_collector] ✅ 写出 {path} ({n}系列)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
