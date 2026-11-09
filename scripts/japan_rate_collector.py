#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""日本利率采集器(IA-P03-E2EB-WP-B3) — 免费公开源,零凭证零API key。

通道: japan(research_provenance.SOURCE_FILE_RULES 登记: 规范文件名
japan_YYYYMMDD.json,回退窗5自然日);产出目录 data/daily(与既有四通道同住)。

数据源(合同预授权③白名单域,均免费公开无申请):
  1. MOF 日本国债收益率曲线 jgbcme(日频收盘,当月文件,Shift_JIS CSV):
     https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/jgbcme.csv
     → JGB2Y/JGB5Y/JGB10Y(列头 2Y/5Y/10Y;单位%;每营业日约19:00 JST后含当日行)
  2. FRED fredgraph 公开CSV端点(无key):
     https://fred.stlouisfed.org/graph/fredgraph.csv?id=IRSTCI01JPM156N
     → JP_POLICY_RATE(日本无担保隔夜拆借利率月均,OECD/BOJ口径;单位%)

产出家形(镜像 macro 通道 {date,data:{metric_id:value}} 并增逐系列观测日披露):
  {"date": "YYYYMMDD(运行日)", "data": {metric_id: value(percent)},
   "observations": {metric_id: "YYYY-MM-DD"}, "sources": {…逐源url/口径…},
   "fetched_at": "ISO8601 UTC", "alerts": […],
   "series": {metric_id: {"dates": […], "values": […]}}  # Charter6-P1: 全史
   序列节(JP_POLICY_RATE,fredgraph 全行解析;源失败→键不出现)}

诚实语义(合同红线: 不凑数不造数):
  - 各系列取源端**最新已发布观测**;观测日≠运行日属正常(月频系列;当日未到
    MOF发布时刻),逐系列如实记于 observations,不冒充运行日观测;
  - 解析失败/数值非法→该系列缺席+alerts如实记录;单源失败不阻断另一源;
  - 全部系列缺席→exit 1 且**不产出** data 文件(不产空壳冒充采集成功)。
零依赖: 仅标准库(urllib.request/json/datetime);禁第三方包。
"""
import json
import os
import sys
import urllib.request
from datetime import date, datetime, timezone

__all__ = ['MOF_JGBCME_URL', 'FRED_POLICY_URL', 'fetch_mof_jgb',
           'fetch_fred_policy_rate_series', 'fetch_fred_policy_rate',
           'build_payload', 'save_daily', 'main']

MOF_JGBCME_URL = ('https://www.mof.go.jp/english/policy/jgbs/'
                  'reference/interest_rate/jgbcme.csv')
FRED_POLICY_URL = ('https://fred.stlouisfed.org/graph/fredgraph.csv'
                   '?id=IRSTCI01JPM156N')
# MOF列头→注册表 metric_id(config/metric_registry.json D11登记口径)
JGB_TENORS = {'2Y': 'JGB2Y', '5Y': 'JGB5Y', '10Y': 'JGB10Y'}
# 按源UA(2026-11-05实测登记): MOF不挑剔自识UA;FRED(fredgraph端点)对陌生UA
# **挂起不响应**(HTTP/1.1下实测超时),UA须以curl/开头才放行——取
# 'curl/8.0 <自识身份>'形态: 前缀过闸+采集器身份在串内诚实保留
_UA = {
    'mof': {'User-Agent': 'investment-agent-dev-japan-rate-collector/1.0',
            'Connection': 'close'},
    'fred': {'User-Agent':
             'curl/8.0 investment-agent-dev-japan-rate-collector/1.0',
             'Connection': 'close'},
}
_TIMEOUT = 60


def _http_get(url, src='mof'):
    req = urllib.request.Request(url, headers=_UA[src])
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
        return r.read()


def _fetch_or_alert(label, fetcher):
    """单源容错(D10登记语义): 网络异常→(None源哨兵,alerts),不崩全程。"""
    try:
        return fetcher(), []
    except Exception as e:   # timeout/URLError/HTTPError/解码IO等一律如实降级
        return None, [f'{label}源获取失败:{type(e).__name__}:{e}']


def fetch_mof_jgb(raw=None):
    """解析 MOF jgbcme CSV → (obs_date 'YYYY-MM-DD', {metric_id: value}, alerts)。

    形态(2026-11-05实测): 首行=当月标题,次行=列头 Date,1Y..40Y,数据行
    2026/M/D,…;末行注释行。取**最后一个**日期与数值均合法的数据行(=最新
    已发布收盘)。列头驱动的期限映射(不按位置猜列)。raw 供离线测试注入。
    """
    alerts = []
    if raw is None:
        raw, a0 = _fetch_or_alert('MOF', lambda: _http_get(MOF_JGBCME_URL))
        alerts.extend(a0)
        if raw is None:
            return None, {}, alerts
    try:
        text = raw.decode('shift_jis')
    except UnicodeDecodeError:
        text = raw.decode('utf-8', errors='strict')
    header = None
    last = None
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
                float(cells[1])   # 行可解析性探针(首数值列)
            except ValueError:
                alerts.append(f'jgbcme不可解析行跳过:{cells[0]!r}')
                continue
            last = (obs, cells)
    if last is None or header is None:
        return None, {}, ['jgbcme无有效数据行(标题/列头/数据行形态不符)'] + alerts
    obs, cells = last
    out = {}
    for i, col in enumerate(header):
        mid = JGB_TENORS.get(col)
        if mid is None:
            continue
        try:
            v = float(cells[i])
        except (ValueError, IndexError):
            alerts.append(f'jgbcme {col} 列数值非法缺席:{cells[i]!r}')
            continue
        out[mid] = v
    miss = sorted(set(JGB_TENORS.values()) - set(out))
    if miss:
        alerts.append(f'jgbcme关键期限缺席:{miss}')
    return obs, out, alerts


def fetch_fred_policy_rate_series(raw=None):
    """解析 FRED fredgraph CSV **全部行** → (dates, values, alerts)(Charter6-P1,
    A2 §2#3): fredgraph 端点本就返回 IRSTCI01JPM156N 全史(月频 1960s+),此前
    只取末行=有值无史;本函数按行升序全量解析(缺失值'.'行跳过,不造数),
    供 japan_ 档 series 节(长序列研究/analog 六维状态向量利率维输入)。

    形态(2026-11-05实测): 首行 observation_date,<series_id>,其后行
    YYYY-MM-DD,value。raw 供离线测试注入;注入则零网络。"""
    alerts = []
    if raw is None:
        raw, a0 = _fetch_or_alert('FRED', lambda: _http_get(FRED_POLICY_URL,
                                                            'fred'))
        alerts.extend(a0)
        if raw is None:
            return None, None, alerts
    text = raw.decode('utf-8')
    lines = [l for l in text.splitlines() if l.strip()]
    if not lines or not lines[0].startswith('observation_date'):
        return None, None, ['fred形态不符(缺observation_date表头)']
    dates, values = [], []
    for line in lines[1:]:
        cells = line.split(',')
        if len(cells) != 2:
            continue
        d, v = cells[0].strip(), cells[1].strip()
        if not v or v == '.':    # FRED缺失值标记'.'跳过(不造数)
            continue
        try:
            fv = float(v)
        except ValueError:
            alerts.append(f'fred数值非法行跳过:{line!r}')
            continue
        dates.append(d)
        values.append(fv)
    if not dates:
        return None, None, ['fred无有效观测行'] + alerts
    return dates, values, alerts


def fetch_fred_policy_rate(raw=None):
    """解析 FRED fredgraph CSV → (obs_date, value, alerts)=最新已发布期。

    (兼容旧接口;Charter6-P1 起内部委托 fetch_fred_policy_rate_series 全行
    解析取末值——口径不变,历史序列另经 build_payload 的 series 节落档。)"""
    dates, values, alerts = fetch_fred_policy_rate_series(raw)
    if dates is None:
        return None, None, alerts
    return dates[-1], values[-1], alerts


def build_payload(run_date=None, mof_raw=None, fred_raw=None):
    """组装 japan_YYYYMMDD.json 载荷(观测日逐系列如实披露)。

    返回 (payload, n_series);n_series==0 时调用方不得落盘。"""
    rd = run_date or date.today()
    ymd = rd.strftime('%Y%m%d')
    data, observations, alerts = {}, {}, []
    obs, jgb, a1 = fetch_mof_jgb(mof_raw)
    alerts.extend(a1)
    if obs is None:
        alerts.append('MOF源整体失败→JGB三系列缺席(如实,不伪造)')
    for mid, v in jgb.items():
        data[mid] = v
        observations[mid] = obs
    # Charter6-P1(A2 §2#3): fredgraph 全行解析一次,同源同响应同时供
    # 最新值(data/observations)与全史序列(series 节)——零新增请求面
    pdates, pvalues, a2 = fetch_fred_policy_rate_series(fred_raw)
    alerts.extend(a2)
    if pdates is None:
        alerts.append('FRED源整体失败→JP_POLICY_RATE缺席(如实,不伪造)')
    else:
        data['JP_POLICY_RATE'] = pvalues[-1]
        observations['JP_POLICY_RATE'] = pdates[-1]
    payload = {
        'date': ymd,
        'data': data,
        'observations': observations,
        'sources': {
            'JGB': {'url': MOF_JGBCME_URL,
                    'note': 'MOF jgbcme收益率曲线(日频收盘,列头期限映射)'},
            'JP_POLICY_RATE': {'url': FRED_POLICY_URL,
                               'note': 'FRED月频系列(观测日=统计期月;全史'
                                       '月频1960s+,OECD镜像口径)'},
        },
        'fetched_at': datetime.now(timezone.utc).strftime(
            '%Y-%m-%dT%H:%M:%SZ'),
        'alerts': alerts,
    }
    # 全史序列节(升序;供快照 series_store/长序列研究);源失败→键不出现
    if pdates is not None:
        payload['series'] = {
            'JP_POLICY_RATE': {'dates': pdates, 'values': pvalues}}
    return payload, len(data)


def save_daily(data_dir, payload):
    """原子写 data_dir/japan_{date}.json(先tmp后replace,防半写)。"""
    path = os.path.join(data_dir, f"japan_{payload['date']}.json")
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
    print(f"[japan_rate_collector] run_date={payload['date']} "
          f"series={sorted(payload['data'])} "
          f"observations={payload['observations']}")
    for a in payload['alerts']:
        print(f"[japan_rate_collector] ⚠️ {a}")
    if n == 0:
        print('[japan_rate_collector] ❌ 全部系列缺席——不产出文件,exit 1')
        return 1
    path = save_daily(data_dir, payload)
    print(f'[japan_rate_collector] ✅ 写出 {path} ({n}系列)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
