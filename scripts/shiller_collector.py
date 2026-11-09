#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shiller 估值采集器(Charter6-P2, A2 §2#5/§4-P2#9) — 免费公开源,零凭证。

通道: shiller(research_provenance.SOURCE_FILE_RULES 登记: 规范文件名
shiller_YYYYMMDD.json,回退窗35自然日——月频数据+官网不定期更新,窗口放宽
到月度节奏);产出目录 data/daily。

数据源(A2 白名单): Robert Shiller 官网 ie_data.xls(耶鲁,http 直链,
免 Key 单文件下载):
  http://www.econ.yale.edu/~shiller/data/ie_data.xls
  → SPX_CAPE(席勒周期调整市盈率: 价格÷10年平均实际盈利,月频 1871+)
  → SPX_PE_TTM(标普500 TTM 市盈率: P÷E(近12个月盈利),月频 1871+)

诚实缺席(A2 §2#6 宁缺毋假,DESIGN 同款纪律):
  - SPX_PB 不采集不登记序列: ie_data.xls 无 book value;multpl.com 非API
    结构脆弱不入生产;不以任何 proxy 冒充——注册表登记 status=unavailable
    供下游如实披露,本采集器不产出该键;
  - 源列缺失(如新版删 CAPE 列)→ 对应序列缺席+alerts 如实,不猜测不推导。

解析容错(A2 §2#5 "sheet 名/表头变动需容错+源版本注记"):
  - sheet 优先名'Data',否则首个 sheet;
  - 表头行=前15行内首个含'Date'列的行(列头驱动定位,不按位置猜列);
  - CAPE 列=表头恰为'CAPE'(排除'TR CAPE'/'CAPE10'等变体);P/E 若源带
    'P/E'列则直用,否则逐行 P÷E 计算(calc 口径登记);
  - 日期列=数值 YYYY.MM(1871.01 形态;月份=四舍五入((v−年)×100),
    1..12 校验),非法行跳过+告警;同月重复保留最后;
  - 缺失单元格(''/空)该月该序列如实缺席,不插值。

产出档形(镜像 japan_rate_collector flat+series 双节):
  {"date": "YYYYMMDD(运行日)", "data": {SPX_CAPE: value, SPX_PE_TTM: value},
   "observations": {metric_id: "YYYY-MM-01(统计期月首日)"}, "sources": {…},
   "source_version": {sheet/header_row/n_rows/columns_used/first/last_month},
   "fetched_at": "ISO8601 UTC", "alerts": […],
   "series": {metric_id: {"dates": […升序…], "values": […]}}}

失败纪律(B3 同款): 源失败→sources_status READ_FAIL+序列缺席+alerts 如实;
全部序列缺席→exit 1 且不产出文件(不产空壳冒充采集成功)。
依赖: 标准库+xlrd(读 .xls;CI 离线套件已装);解析函数支持字节注入零网络。
"""
import json
import os
import sys
import urllib.request
from datetime import date, datetime, timezone

__all__ = ['SHILLER_IE_URL', 'parse_ie_data', 'build_payload', 'save_daily',
           'main']

SHILLER_IE_URL = 'http://www.econ.yale.edu/~shiller/data/ie_data.xls'
_UA = {'User-Agent': 'investment-agent-dev-shiller-collector/1.0',
       'Connection': 'close'}
_TIMEOUT = 120          # ie_data.xls ~2MB,慢源宽限
_HEADER_SCAN_ROWS = 15  # 表头行容错扫描窗(实册约第7-8行)

# 表头匹配规范(小写去空白;列头驱动,不按位置)
def _hdr(cell):
    return str(cell or '').strip().lower()


def _month_from_shiller_date(v):
    """数值日期 YYYY.MM → 'YYYY-MM-01';非法(非数值/月份越界)返回 None。

    月份=round((v−年)×100)(1871.01→1月,1871.1→10月;浮点尾差由四舍五入
    吸收);统计期=月,以当月首日表示(与 ea HICP 月频口径同构)。"""
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return None
    year = int(v)
    month = round((v - year) * 100)
    if month < 1 or month > 12:
        return None
    return f'{year:04d}-{month:02d}-01'


def _cell_float(v):
    """单元格→float;空/非数值→None(不猜不填)。"""
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if not s or s in ('.', '-', '#N/A', 'NA'):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def parse_ie_data(raw):
    """解析 ie_data.xls 字节 → (series, meta, alerts)。

    series: {SPX_CAPE|SPX_PE_TTM: {'dates':[…升序…], 'values':[…]}}
    (源缺列→键不出现);meta: 源版本注记(sheet/表头行/行数/采用列/首末月);
    raw 供离线测试注入(注入则零网络)。"""
    alerts = []
    series = {}
    meta = {'sheet': None, 'header_row': None, 'n_rows_scanned': 0,
            'columns_used': {}, 'first_month': None, 'last_month': None}
    try:
        import xlrd
    except ImportError:
        return {}, meta, ['xlrd 未安装(pip install xlrd;requirements.txt 已登记)']
    try:
        book = xlrd.open_workbook(file_contents=raw)
    except Exception as e:
        return {}, meta, [f'ie_data.xls 打开失败:{type(e).__name__}:{e}']
    sheet = None
    for name in book.sheet_names():
        if name.strip().lower() == 'data':
            sheet = book.sheet_by_name(name)
            break
    if sheet is None:
        sheet = book.sheet_by_index(0)
        alerts.append(f"未见'Data' sheet,回退首个 sheet:{sheet.name!r}")
    meta['sheet'] = sheet.name

    # 表头行定位(前15行内首个含'Date'列的行;列头驱动;不要求该行
    # 同时含估值列——先定位表头,估值列缺席与否是下一步的独立判定,
    # 两种缺席(无表头/有表头无估值列)分别如实告警)
    header_idx, cols = None, {}
    for r in range(min(_HEADER_SCAN_ROWS, sheet.nrows)):
        cells = [_hdr(sheet.cell_value(r, c))
                 for c in range(sheet.ncols)]
        if 'date' not in cells:
            continue
        cols = {h: c for c, h in enumerate(cells) if h}
        header_idx = r
        break
    if header_idx is None:
        return {}, meta, ['ie_data.xls 表头行未定位(前15行无 Date 列头)']
    meta['header_row'] = header_idx + 1

    use_cape = 'cape' in cols
    use_pe_col = cols.get('p/e')
    use_pe_calc = use_pe_col is None and 'p' in cols and 'e' in cols
    meta['columns_used'] = {
        'CAPE': cols.get('cape'),
        'PE': use_pe_col if use_pe_col is not None else (
            [cols['p'], cols['e']] if use_pe_calc else None),
    }
    if not (use_cape or use_pe_col or use_pe_calc):
        return {}, meta, ['ie_data.xls 无可用估值列(CAPE/P/E 均未在表头定位)']

    cape_m, pe_m = {}, {}
    for r in range(header_idx + 1, sheet.nrows):
        meta['n_rows_scanned'] += 1
        dv = sheet.cell_value(r, cols['date'])
        mkey = _month_from_shiller_date(dv)
        if mkey is None:
            # 末尾汇总行/注释行常见非数值日期——仅对前几行告警,尾部静默
            if meta['n_rows_scanned'] <= 3:
                alerts.append(f'日期列非法行跳过(第{r + 1}行):{dv!r}')
            continue
        if use_cape:
            cv = _cell_float(sheet.cell_value(r, cols['cape']))
            if cv is not None:
                cape_m[mkey] = cv
        if use_pe_col is not None:
            pv = _cell_float(sheet.cell_value(r, use_pe_col))
            if pv is not None:
                pe_m[mkey] = pv
        elif use_pe_calc:
            p = _cell_float(sheet.cell_value(r, cols['p']))
            e = _cell_float(sheet.cell_value(r, cols['e']))
            if p is not None and e is not None and e != 0:
                pe_m[mkey] = p / e
    if cape_m:
        ks = sorted(cape_m)
        series['SPX_CAPE'] = {'dates': ks, 'values': [cape_m[k] for k in ks]}
    if pe_m:
        ks = sorted(pe_m)
        series['SPX_PE_TTM'] = {'dates': ks, 'values': [pe_m[k] for k in ks]}
    months = sorted(set(cape_m) | set(pe_m))
    meta['first_month'], meta['last_month'] = (
        (months[0][:7], months[-1][:7]) if months else (None, None))
    return series, meta, alerts


def _http_get(url):
    req = urllib.request.Request(url, headers=_UA)
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
        return r.read()


def _now_iso():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def build_payload(run_date=None, raw=None):
    """组装 shiller_YYYYMMDD.json 载荷(flat data+observations+全史 series)。

    返回 (payload, n_series);n_series==0 时调用方不得落盘。raw 供离线
    测试注入(注入则零网络)。"""
    rd = run_date or date.today()
    ymd = rd.strftime('%Y%m%d')
    alerts = []
    sources_status = {}
    series, meta, a = {}, {}, []
    if raw is not None:
        series, meta, a = parse_ie_data(raw)
        alerts.extend(a)
    else:
        t0 = _now_iso()
        try:
            raw_bytes = _http_get(SHILLER_IE_URL)
        except Exception as e:
            alerts.append(f'SHILLER_IE源获取失败:{type(e).__name__}:{e}')
            sources_status['SHILLER_IE'] = {'status': 'READ_FAIL',
                                            'retrieved_at': t0}
        else:
            sources_status['SHILLER_IE'] = {'status': 'EXACT',
                                            'retrieved_at': t0}
            series, meta, a = parse_ie_data(raw_bytes)
            alerts.extend(a)
    data, observations = {}, {}
    for mid, s in sorted(series.items()):
        data[mid] = s['values'][-1]
        observations[mid] = s['dates'][-1]
    payload = {
        'date': ymd,
        'generated_at': _now_iso(),
        'sources_status': sources_status,
        'data': data,
        'observations': observations,
        'sources': {
            'SHILLER_IE': {
                'url': SHILLER_IE_URL,
                'note': 'Robert Shiller 官网 ie_data.xls(月频 1871+;'
                        'CAPE=价格÷10年平均实际盈利;PE_TTM=逐行P÷E)'
                        '——最新修订口径(latest_vintage_asof_collected)'},
        },
        # 源版本注记(A2 §2#5: 表头变动容错的观测面,随档落盘供审计)
        'source_version': meta,
        'fetched_at': _now_iso(),
        'alerts': alerts,
    }
    if series:
        payload['series'] = series
    return payload, len(data)


def save_daily(data_dir, payload):
    """原子写 data_dir/shiller_{date}.json(先tmp后replace,防半写)。"""
    path = os.path.join(data_dir, f"shiller_{payload['date']}.json")
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
    print(f"[shiller_collector] run_date={payload['date']} "
          f"series={sorted(payload['data'])} "
          f"observations={payload['observations']}")
    if payload.get('source_version'):
        sv = payload['source_version']
        print(f"[shiller_collector] 源版本: sheet={sv.get('sheet')} "
              f"表头行={sv.get('header_row')} 行={sv.get('n_rows_scanned')} "
              f"首末月={sv.get('first_month')}~{sv.get('last_month')}")
    for a in payload['alerts']:
        print(f"[shiller_collector] ⚠️ {a}")
    if n == 0:
        print('[shiller_collector] ❌ 全部系列缺席——不产出文件,exit 1')
        return 1
    path = save_daily(data_dir, payload)
    print(f'[shiller_collector] ✅ 写出 {path} ({n}系列)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
