#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""欧元区市场采集器(IA-P1-WP-A v1.3) — 免费公开源,零凭证零API key。

通道: ea(research_provenance.SOURCE_FILE_RULES 登记: 规范文件名
ea_YYYYMMDD.json,回退窗5自然日);产出目录 data/daily。

数据源(IA-P1-WP-A-AC §一 白名单域,REPORT §零.12⑩ 定值;均免费公开):
  1. ECB Data Portal SDMX(csvdata;ecb.europa.eu 域):
     https://data-api.ecb.europa.eu/service/data/FM/B.U2.EUR.4F.KR.DFR.LEV?format=csvdata&startPeriod=1999-01-01
       → policy_rates.ECB_DFR(存款便利利率,日频)
     https://data-api.ecb.europa.eu/service/data/FM/B.U2.EUR.4F.KR.MRR_FR.LEV?format=csvdata&startPeriod=1999-01-01
       → policy_rates.ECB_MRO(主要再融资固定利率,日频)
     https://data-api.ecb.europa.eu/service/data/ICP/M.U2.N.000000.4.ANR?format=csvdata
       → inflation.EA_HICP_YOY(HICP年度变化率,月频;月统计期 TIME_PERIOD 'YYYY-MM'
         以当月首日表示并注记,统计期=月)
  2. Bundesbank timeseries REST(api.bundesbank.de 域;SDMX csv):
     https://api.bundesbank.de/timeseries/rest/data/BBK01/WU3146?format=csv
       → bund.BUND_10Y(残存期限9-10年档)
     https://api.bundesbank.de/timeseries/rest/data/BBK01/WU3141?format=csv
       → bund.BUND_2Y(**候选键**,REPORT §零.12⑩;口径核验机制见 _bbk_meta_ok:
         同域 format=json 元数据文本中残存期限区间文本可核('…1…2…Jahr'形态)
         方采纳;不可核→节诚实缺席)

诚实缺席(DESIGN §三(a-2) L58+REPORT §零.12⑩ 定值;键不出现,禁 0 占位):
  - prices 节整体缺席: DAX/CAC40 指数口径源(xetra/euronext)不在白名单五域,
    yfinance 不入依赖面(v1.1② 冻结),sources_status 记 MISSING。

产出档形(DESIGN §三(a-2) L45-L57 逐字+观测性附加键,REPORT §零.12⑪):
  顶层 date/generated_at/sources_status + 通道节 policy_rates/bund/inflation/prices
  + 附加 observations/sources/fetched_at/alerts;prev_value=源端次新观测
  (不可得→null);inflation 节增 change(=value−prev_value,pp)/change_period/freq;
  series 节(Charter6-P1)= 政策利率全史序列(DFR/MRO 1999+ 全行入档,升序;
  源失败→键不出现)——A2 §2#2 ECB_DFR 历史化(本通道路线)+§2#8 MRO 对称。

Charter6-P1(A2 P1#7): BBK 源 RemoteDisconnected 偶发断供→重试+指数退避
(3次: 即时/2s/5s;仅网络层异常重试;ECB 源保持单次)。

失败纪律(B3 同款): 源失败→节键不出现+sources_status 该源 READ_FAIL+alerts
如实;全部系列缺席→exit 1 且不产出文件。零依赖: 仅标准库。
"""
import json
import os
import re
import sys
import urllib.error
from datetime import date, datetime, timezone

__all__ = ['ECB_DFR_URL', 'ECB_MRO_URL', 'ECB_HICP_URL', 'BBK_10Y_URL',
           'BBK_2Y_URL', 'build_payload', 'save_daily', 'main']

# Charter6-P1(A2 §1/§2#2): 政策利率两系列 startPeriod 2024→1999(欧元区
# 货币联盟起点,全史 1999+;单文件响应仍轻量,限流宽松)——供 series 节全行
# 解析,长序列研究(利率通道对比/相似期)不再只有末值。
ECB_DFR_URL = ('https://data-api.ecb.europa.eu/service/data/FM/'
               'B.U2.EUR.4F.KR.DFR.LEV?format=csvdata&startPeriod=1999-01-01')
ECB_MRO_URL = ('https://data-api.ecb.europa.eu/service/data/FM/'
               'B.U2.EUR.4F.KR.MRR_FR.LEV?format=csvdata&startPeriod=1999-01-01')
# Audit-R20(2026-11-19): HICP 数据集换轨——旧 ICP 数据集被 ECB 于 2026-02-04
# 停用(响应内嵌公告: "the ECB will also discontinue the current Indices of
# Consumer Prices - ICP dataset and replace it with a new HICP dataset",
# 实测旧键止于 2025-12)。新 HICP 数据流(ECB_ICP3 结构,键
# FREQ.REF_AREA.ADJUSTMENT.ICP_ITEM.DATA_PROVIDER.ICP_SUFFIX)实测含全史
# 1997-01..今(1997-01=2.1,2026-09=3.8,2026-10=4.0),无需双数据集拼接;
# 重叠月 2025-12 有 1.9(旧)→2.0(新)的口径修订,新数据集为权威面。
ECB_HICP_URL = ('https://data-api.ecb.europa.eu/service/data/HICP/'
                'M.U2.N.000000.4D0.ANR?format=csvdata')
ECB_HICP_URL_LEGACY = ('https://data-api.ecb.europa.eu/service/data/ICP/'
                       'M.U2.N.000000.4.ANR?format=csvdata')
# Audit-R20(2026-11-19): 欧元区增长维序列(12组36格四地地图问句正式使用)。
# FRED fredgraph CLVMEURSCAB1GQEA19=欧元区(19国)实际GDP链式量度季频水平
# (1995+,免费公开零凭证);同季去年比=(本季/去年同季−1)×100。FRED 载荷=
# 最新修订值,无当时发布版本可比→序列注记 hindsight 口径。
FRED_EA_GDP_URL = ('https://fred.stlouisfed.org/graph/fredgraph.csv'
                   '?id=CLVMEURSCAB1GQEA19')
# FRED fredgraph 实测(jp 通道 japan_rate_collector 同款结论): 非 curl 形态
# UA 会被源端 RemoteDisconnected 拒——FRED 源一律带 curl 形态 UA。
_UA_FRED = {'User-Agent': 'curl/8.0 investment-agent-dev-ea-market-collector/1.1',
            'Connection': 'close'}
BBK_10Y_URL = 'https://api.bundesbank.de/timeseries/rest/data/BBK01/WU3146?format=csv'
BBK_2Y_URL = 'https://api.bundesbank.de/timeseries/rest/data/BBK01/WU3141?format=csv'

_UA = {'User-Agent': 'investment-agent-dev-ea-market-collector/1.0',
       'Connection': 'close'}
_TIMEOUT = 60


def _now_iso():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


# Charter6-P1(A2 P1#7): Bundesbank 源偶发 RemoteDisconnected(2026-11-08
# 实测 ea_20261108.json alerts: BBK_WU3146源获取失败:RemoteDisconnected)
# ——BBK 请求带重试+指数退避(3次: 即时/2s/5s);仅网络层异常重试,HTTP 4xx/5xx
# 与解析失败不重试(如实降级)。ECB 源稳定,保持单次(不放大请求面)。
_RETRY_SOURCES = frozenset({'bbk'})
_RETRY_DELAYS = (0, 2, 5)


def _open_url(url, headers):
    """单次 HTTP GET(独立小函数,离线测试可注入替身)。"""
    import urllib.request
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
        return r.read()


def _sleep(seconds):
    """退避等待(独立小函数,离线测试可注入替身,不真睡)。"""
    import time
    time.sleep(seconds)


def _http_get(url, src='ecb'):
    last_exc = None
    for attempt, delay in enumerate(_RETRY_DELAYS, start=1):
        if delay and attempt > 1:
            _sleep(delay)
        try:
            return _open_url(url, _UA)
        except urllib.error.HTTPError:
            raise    # 4xx/5xx 不属网络瞬断,不重试(如实降级,不放大请求面)
        except Exception as e:   # 网络层(RemoteDisconnected/URLError/超时)
            last_exc = e
            if src in _RETRY_SOURCES and attempt < len(_RETRY_DELAYS):
                continue
            raise
    raise last_exc


def _fetch_or_alert(label, fetcher):
    """单源容错(B3 D10 语义同款): 网络异常→(None,alerts),不崩全程。"""
    try:
        return fetcher(), []
    except Exception as e:
        return None, [f'{label}源获取失败:{type(e).__name__}:{e}']


def parse_sdmx_csv(raw):
    """SDMX-CSV(ECB csvdata/Bundesbank csv 同族)→ [(obs 'YYYY-MM-DD'|'YYYY-MM', value), …]。

    列头驱动定位 TIME_PERIOD/OBS_VALUE(不按位置猜列);缺失值(''/NaN)行跳过;
    月频 TIME_PERIOD='YYYY-MM' 原样保留(调用方按节语义处理)。raw 供离线注入。"""
    alerts = []
    text = raw.decode('utf-8', errors='strict')
    lines = [l for l in text.splitlines() if l.strip()]
    if not lines:
        return None, ['sdmx空响应']
    header = [c.strip() for c in lines[0].split(',')]
    try:
        i_t = header.index('TIME_PERIOD')
        i_v = header.index('OBS_VALUE')
    except ValueError:
        return None, [f'sdmx形态不符(列头缺TIME_PERIOD/OBS_VALUE):{header[:8]}…']
    rows = []
    for line in lines[1:]:
        cells = line.split(',')
        if len(cells) <= max(i_t, i_v):
            continue
        t, v = cells[i_t].strip(), cells[i_v].strip()
        if not v or v.upper() == 'NaN':
            continue
        try:
            rows.append((t, float(v)))
        except ValueError:
            alerts.append(f'sdmx数值非法行跳过:{line[:60]!r}')
    if not rows:
        return None, ['sdmx无有效观测行'] + alerts
    return rows, alerts


# ══ Audit-R20: FRED fredgraph CSV 解析 → 欧元区 GDP 同季去年比序列 ══════

def parse_fred_csv(raw):
    """FRED fredgraph CSV → [(obs 'YYYY-MM-DD', value), …](升序全序列)。

    形态同 jp 通道 _parse_fred_series 实测: 首行 observation_date,<series_id>;
    缺失值'.'行跳过。raw 供离线注入。"""
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
        base = by.get('%04d-%02d-01' % (y - 1, m))
        if base:
            out.append((d, round((v / base - 1.0) * 100.0, 2)))
    return out


def _open_url_with(url, headers):
    """单次 HTTP GET(指定 headers;离线测试可注入替身)。"""
    import urllib.request
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
        return r.read()


def fetch_ea_real_gdp_yoy(raw=None):
    """FRED CLVMEURSCAB1GQEA19 → 同季去年比序列;raw 注入则零网络。

    → (yoy [('YYYY-MM-01', pct)], alerts);源失败→(None, alerts)。"""
    if raw is None:
        raw, a = _fetch_or_alert('FRED-EA-GDP', lambda: _open_url_with(
            FRED_EA_GDP_URL, _UA_FRED))
        if raw is None:
            return None, a
    rows, alerts = parse_fred_csv(raw)
    if rows is None:
        return None, alerts
    return _quarterly_yoy(rows), alerts


def _month_to_iso(t):
    """月统计期 'YYYY-MM' → 'YYYY-MM-01'(当月首日表示;日频原样返回)。"""
    if re.fullmatch(r'\d{4}-\d{2}', t):
        return f'{t}-01'
    return t


def _bbk_meta_ok(meta_text, lo, hi):
    """Bundesbank 候选键口径核验(同域 format=json 元数据文本): 残存期限区间
    文本可核('…{lo}…{hi}…Jahr…'形态,容忍 bis/–/-/空格)方采纳。不可核→False
    →该节诚实缺席(REPORT §零.12⑩ 候选键纪律:宁缺席,不猜口径)。"""
    if not meta_text:
        return False
    pat = re.compile(rf'{lo}\D{{1,8}}{hi}\D{{0,12}}Jahr', re.IGNORECASE)
    return bool(pat.search(meta_text))


def _leaf(value, obs, prev):
    return {'value': value, 'unit': 'percent', 'date': obs, 'prev_value': prev}


def _daily_section(rows, obs_norm=None):
    """日频节: 末值/次新值;obs_norm 供月期表示转换。返回 (leaf, obs)。"""
    d, v = rows[-1]
    prev = rows[-2][1] if len(rows) >= 2 else None
    obs = obs_norm(d) if obs_norm else d
    return _leaf(v, obs, prev), obs


def build_payload(run_date=None, ecb_dfr_raw=None, ecb_mro_raw=None,
                  ecb_hicp_raw=None, bbk10_raw=None, bbk2_raw=None,
                  bbk10_meta_raw=None, bbk2_meta_raw=None):
    """组装 ea_YYYYMMDD.json 载荷(a-2 节结构;缺席节键不出现)。

    返回 (payload, n_series);n_series==0 时调用方不得落盘。raw 参数供离线
    测试注入(注入则该源零网络);bbk*_meta_raw=候选键口径核验元数据文本。"""
    rd = run_date or date.today()
    ymd = rd.strftime('%Y%m%d')
    policy_rates, bund, inflation = {}, {}, {}
    observations, alerts = {}, []
    sources_status = {}

    # Charter6-P1: 政策利率全史序列节收集(DFR/MRO 1999+;BUND 历史化=A2 P2#12
    # 不在本轮,只修复源故障重试)
    series_out = {}

    def daily_source(label, url, raw, section, key, src='ecb', keep_series=False):
        """公共日频源流: 取raw(或网络)→解析→节登记/缺席登记。

        src('ecb'/'bbk')路由重试策略(BBK=重试+退避);keep_series=True 时全行
        入 series_out[key](SDMX 行序即时序升序,缺失值行已在解析层跳过)。"""
        if raw is None:
            raw, a = _fetch_or_alert(label, lambda: _http_get(url, src))
            alerts.extend(a)
        if raw is None:
            sources_status[label] = {'status': 'READ_FAIL', 'retrieved_at': None}
            alerts.append(f'{label}源获取失败→{key}缺席(如实,不伪造)')
            return
        t0 = _now_iso()
        rows, a = parse_sdmx_csv(raw)
        alerts.extend(a)
        if rows is None:
            sources_status[label] = {'status': 'READ_FAIL', 'retrieved_at': t0}
            alerts.append(f'{label}源解析失败→{key}缺席(如实,不伪造)')
            return
        leaf, obs = _daily_section(rows)
        section[key] = leaf
        observations[key] = obs
        if keep_series and rows:
            series_out[key] = {'dates': [r[0] for r in rows],
                               'values': [r[1] for r in rows]}
        sources_status[label] = {'status': 'EXACT', 'retrieved_at': t0}

    daily_source('ECB_FM_DFR', ECB_DFR_URL, ecb_dfr_raw, policy_rates,
                 'ECB_DFR', keep_series=True)
    daily_source('ECB_FM_MRO', ECB_MRO_URL, ecb_mro_raw, policy_rates,
                 'ECB_MRO', keep_series=True)
    daily_source('BBK_WU3146', BBK_10Y_URL, bbk10_raw, bund, 'BUND_10Y',
                 src='bbk')
    daily_source('BBK_WU3141', BBK_2Y_URL, bbk2_raw, bund, 'BUND_2Y',
                 src='bbk')

    # ── Bundesbank 口径核验(候选键纪律: 不可核→节诚实缺席)────────────────
    for label, key, lo, hi, meta_raw in (
            ('BBK_WU3146', 'BUND_10Y', 9, 10, bbk10_meta_raw),
            ('BBK_WU3141', 'BUND_2Y', 1, 2, bbk2_meta_raw)):
        if key not in bund:
            continue                       # 数据面已缺席,核验无从谈起
        if meta_raw is None:
            meta_raw, a = _fetch_or_alert(f'{label}-META', lambda: _http_get(
                f'https://api.bundesbank.de/timeseries/rest/data/BBK01/'
                f'WU{label[-4:]}?format=json'))
            alerts.extend(a)
        meta_text = None
        if meta_raw is not None:
            meta_text = meta_raw.decode('utf-8', errors='replace')
        if not _bbk_meta_ok(meta_text, lo, hi):
            del bund[key]
            observations.pop(key, None)
            sources_status[label] = {'status': 'READ_FAIL',
                                     'retrieved_at': sources_status[label].get(
                                         'retrieved_at')}
            alerts.append(f'{label}口径核验未通过(元数据不可核{lo}~{hi}年残存期限)'
                          f'→{key}诚实缺席(宁缺席,不猜口径)')

    # ── ECB HICP(月频;月统计期以当月首日表示)──────────────────────────
    if ecb_hicp_raw is None:
        ecb_hicp_raw, a = _fetch_or_alert('ECB_ICP_HICP', lambda: _http_get(
            ECB_HICP_URL))
        alerts.extend(a)
    if ecb_hicp_raw is None:
        sources_status['ECB_ICP_HICP'] = {'status': 'READ_FAIL',
                                          'retrieved_at': None}
        alerts.append('ECB HICP源获取失败→inflation 节缺席(如实,不伪造)')
    else:
        t0 = _now_iso()
        rows, a = parse_sdmx_csv(ecb_hicp_raw)
        alerts.extend(a)
        if rows is None:
            sources_status['ECB_ICP_HICP'] = {'status': 'READ_FAIL',
                                              'retrieved_at': t0}
            alerts.append('ECB HICP源解析失败→inflation 节缺席(如实,不伪造)')
        else:
            leaf, obs = _daily_section(rows, obs_norm=_month_to_iso)
            prev = leaf['prev_value']
            inflation['EA_HICP_YOY'] = dict(
                leaf, change=(round(leaf['value'] - prev, 4)
                              if prev is not None else None),
                change_period='MoM', freq='Monthly')
            observations['EA_HICP_YOY'] = obs
            # Audit-R20: HICP 全史入 series 节(月频序列;月统计期=当月首日)
            series_out['EA_HICP_YOY'] = {
                'dates': [_month_to_iso(r[0]) for r in rows],
                'values': [r[1] for r in rows]}
            sources_status['ECB_ICP_HICP'] = {'status': 'EXACT',
                                              'retrieved_at': t0}

    # ── Audit-R20: 欧元区实际GDP 同季去年比(FRED fredgraph)─────────────
    gdp_yoy, a = fetch_ea_real_gdp_yoy()
    alerts.extend(a)
    if gdp_yoy:
        series_out['EA_REAL_GDP_YOY'] = {
            'dates': [d for d, _ in gdp_yoy],
            'values': [v for _, v in gdp_yoy],
            'history_note': 'FRED CLVMEURSCAB1GQEA19 载荷=最新修订值(无当时'
                            '发布版本可比)——研究/渲染面按事后回顾口径标注'}
        observations['EA_REAL_GDP_YOY'] = gdp_yoy[-1][0]
        sources_status['FRED_EA_GDP'] = {'status': 'EXACT',
                                         'retrieved_at': _now_iso()}
    else:
        sources_status['FRED_EA_GDP'] = {'status': 'READ_FAIL',
                                         'retrieved_at': None}
        alerts.append('FRED 欧元区GDP源失败→series.EA_REAL_GDP_YOY 缺席(如实)')

    # ── 诚实缺席(键不出现): prices 节 ─────────────────────────────────
    sources_status['DAX'] = {'status': 'MISSING', 'retrieved_at': None}
    sources_status['CAC40'] = {'status': 'MISSING', 'retrieved_at': None}
    alerts.append('DAX/CAC40诚实缺席:指数口径源不在白名单五域(xetra/euronext),'
                  'yfinance不入依赖面→prices 节键不出现')

    payload = {
        'date': ymd,
        'generated_at': _now_iso(),
        'sources_status': sources_status,
        'observations': observations,
        'sources': {
            'ECB_FM_DFR': {'url': ECB_DFR_URL,
                           'note': 'ECB Data Portal FM存款便利利率(日频)'},
            'ECB_FM_MRO': {'url': ECB_MRO_URL,
                           'note': 'ECB Data Portal FM主要再融资固定利率(日频)'},
            'ECB_ICP_HICP': {'url': ECB_HICP_URL,
                             'note': 'ECB Data Portal HICP数据流欧元区HICP年'
                                     '变化率(月频;月统计期以当月首日表示;'
                                     '2026-02-04 ICP→HICP 数据集换轨,新数据'
                                     '集含1997+全史,Audit-R20)'},
            'FRED_EA_GDP': {'url': FRED_EA_GDP_URL,
                            'note': 'FRED季频CLVMEURSCAB1GQEA19欧元区实际GDP'
                                    '链式量度水平→同季去年比(最新修订值=事后'
                                    '回顾口径,Audit-R20 接线)'},
            'BBK_WU3146': {'url': BBK_10Y_URL,
                           'note': 'Bundesbank BBK01/WU3146 残存期限9-10年档'
                                   '(10Y代理;口径经同域元数据核验)'},
            'BBK_WU3141': {'url': BBK_2Y_URL,
                           'note': 'Bundesbank BBK01/WU3141 候选键(1-2年档;'
                                   '口径不可核→诚实缺席)'},
            'DAX': {'url': None,
                    'note': '诚实缺席:指数口径源不在白名单域'},
            'CAC40': {'url': None,
                      'note': '诚实缺席:指数口径源不在白名单域'},
        },
        'fetched_at': _now_iso(),
        'alerts': alerts,
    }
    for section, obj in (('policy_rates', policy_rates), ('bund', bund),
                         ('inflation', inflation)):
        if obj:
            payload[section] = obj          # 缺席节键不出现(L58)
    # Charter6-P1: 全史序列节(政策利率 DFR/MRO 1999+;缺席→键不出现)
    if series_out:
        payload['series'] = series_out
    n_series = len(policy_rates) + len(bund) + len(inflation)
    return payload, n_series


def save_daily(data_dir, payload):
    """原子写 data_dir/ea_{date}.json(Audit-R25 任务1: 同日降级重采集
    经 daily_face_guard_write 守卫——序列丢失面转存 superseded/,不覆盖
    同日完整可重放面)。"""
    import research_provenance as rp
    path, status, note = rp.daily_face_guard_write(
        data_dir, 'ea', payload['date'], payload, indent=1)
    if status == 'degraded_diverted':
        print(f'[ea_market_collector] ⚠️ 同日降级面({note})未覆盖完整档,'
              f'转存 {path}')
    return path


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    data_dir = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), 'data', 'daily')
    if '--data-dir' in argv:
        data_dir = argv[argv.index('--data-dir') + 1]
    payload, n = build_payload()
    sections = [k for k in ('policy_rates', 'bund', 'inflation') if k in payload]
    print(f"[ea_market_collector] run_date={payload['date']} "
          f"sections={sections} observations={payload['observations']}")
    for a in payload['alerts']:
        print(f"[ea_market_collector] ⚠️ {a}")
    if n == 0:
        print('[ea_market_collector] ❌ 全部系列缺席——不产出文件,exit 1')
        return 1
    path = save_daily(data_dir, payload)
    print(f'[ea_market_collector] ✅ 写出 {path} ({n}系列)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
