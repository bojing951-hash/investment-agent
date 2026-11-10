#!/usr/bin/env python3
"""IA-P03-W1 E2E-A: 研究历史查询与跨频率对齐(Layer 4 研究底座,纯离线)

职责(P03-W1 合同 E2EA-AC-01):
1. 按指标 ID + 时间区间返回历史序列——数据**只经登记接入点**(见 ACCESS_POINTS),
   不绕开标准化层直读原始采集档;
2. 跨频率对齐: 日频共同观测日内连接(默认,correlation_calculator.paired_returns
   同式)+ ISO 周/自然月网格化(代表值=周/月内最后有效观测;与 fact_engine
   compute_period_returns 的 week/mtd 基准"期开始之前最后有效观测"同构);
3. 区间变动(利率类→pp+bp,价格类→pct;与 fact_engine.RATE_UNITS/PRICE_LIKE_UNITS
   同一分类源)与滚动相关性(参数化);
4. 缺值如实缺席(剔除并登记 n_missing),**绝不填 0**。

数据接入点登记(实读基线 e04c063,合同 §零(iii)):
- macro 通道指标(TIPS_10Y/UST_*/BEI_* 等):
  snapshot_builder.resolve_inputs(scripts/snapshot_builder.py:47)
  → 字节读取+sha256(与 build_snapshot 读取段 snapshot_builder.py:263-269 同语义;
  **经标准化层转递**,合同 E2EA-AC-01 豁免句"经标准化层转递不在此限")
  → fact_engine.normalize_macro(scripts/fact_engine.py:275)身份映射+校验+质量分级
  → 序列提取自标准化层确认的输入结构,结果附事实的 unit/quality_status/observation_date。
- global 通道指标(GOLD_F 等):
  snapshot_builder.build_snapshot(write=False)(scripts/snapshot_builder.py:236)
  → snapshot['series_store'][metric_id](构建段 snapshot_builder.py:358-382;
  旧ID GOLD→GOLD_F 映射 fact_engine.py:244)——快照历史序列,零落盘、零直开。
- IA-P1-GAP08 R47-F3 覆盖面扩展(WP-D REPORT §一.6-F3 承接=DESIGN §四 L130
  "查询覆盖面扩展至新 metric_id"): jp/ea 通道价格序列指标(NIKKEI225/DAX/CAC40,
  registry source=jp/ea_market_collector)经同一快照接入点(series_store,
  F2 接线后在场)载入——jp_/ea_ 原始采集档同禁直读(DESIGN L130 禁直读约束
  原样覆盖新通道,查询只吃快照层);japan_rate_collector 类为 flat 单点无序列
  →无接入点(既有 ValueError 如实)。
- IA-P1-GAP08 R47-F3 economy 过滤维度(L130 "economy 字段可作过滤维度"):
  payload 附 registry.economy echo;query_window 可选 economy 参数——过滤
  不命中=如实空窗披露,不造数据;取值域 ECONOMIES(registry 实测值域)。
- 结构性缺口(登记): series_store 收 global+china+F2 后 jp/ea 价格序列,
  macro 利率序列不经快照任何位置(fact 不保留 series,fact_engine.py:224-227
  仅供派生计算);若要求利率亦走 series_store 须改 snapshot_builder 构建段
  →继续 PENDING 登记于 GAP08 REPORT §四。

零网络: 纯标准库+项目既有模块;不做任何采集/请求。
"""
import argparse
import gzip
import hashlib
import json
import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import fact_engine as fe
import snapshot_builder as sb
import trading_calendar as tc

# 缺省采集目录复用 snapshot_builder 的权威常量(不在本模块出现原始采集目录字样;
# 文件选择一律经 resolve_inputs 规范核验,本模块不 glob/不猜文件名)
DEFAULT_DATA_DIR = None

# macro 采集档 data 键名与注册表 metric_id 的已知差异(fact_engine._MACRO_ALIAS
# 的反向表,登记在案;TIPS_10Y/UST_*/BEI_* 键名一致无需映射)
_MACRO_DATA_KEY = {'WTI_SPOT_M': 'WTI'}

ACCESS_POINTS = {
    'macro': ('fact_engine.normalize_macro via snapshot_builder.resolve_inputs '
              '(scripts/fact_engine.py:275; scripts/snapshot_builder.py:47)'),
    'global': ('snapshot.series_store via snapshot_builder.build_snapshot(write=False) '
               '(scripts/snapshot_builder.py:236,358-382)'),
    # IA-P1-GAP08 R47-F3: jp/ea 价格序列指标走同一快照接入点(F2 接线后
    # NIKKEI225/DAX/CAC40 在 store);jp_/ea_ 档禁直读约束原样覆盖。
    'jp': ('snapshot.series_store via snapshot_builder.build_snapshot(write=False) '
           '(scripts/snapshot_builder.py:236,358-382+GAP08-F2)'),
    'ea': ('snapshot.series_store via snapshot_builder.build_snapshot(write=False) '
           '(scripts/snapshot_builder.py:236,358-382+GAP08-F2)'),
    # Charter6-P2(A2 §2#5): Shiller 估值序列(SPX_CAPE/SPX_PE_TTM,月频1871+)
    # 走同一快照接入点(merge_series_sections lift 后在 store)。
    'shiller': ('snapshot.series_store via snapshot_builder.build_snapshot(write=False) '
                '(scripts/snapshot_builder.py:236,358-382+Charter6-P2 shiller通道lift)'),
}

# IA-P1-GAP08 R47-F3: economy 过滤维度取值域(registry economy 字段实测值域
# 同集;先例=e2eb_query_ir.ECONOMIES WP-D PD-1,DESIGN §四 L133 候选 enum)。
ECONOMIES = ("US", "CN", "JP", "EA", "HK", "GLOBAL")


def _clean_series(dates, values):
    """序列清洗: 升序去重(同日保留最后)+缺值剔除(不填0),返回清洗登记。"""
    seen = {}
    n_missing = 0
    for d, v in zip(dates or [], values or []):
        ds = str(d)[:10]
        if v is None:
            n_missing += 1
            continue
        try:
            fv = float(v)
        except (TypeError, ValueError):
            n_missing += 1
            continue
        seen[ds] = fv
    out_dates = sorted(seen)
    return out_dates, [seen[d] for d in out_dates], {'n_missing_dropped': n_missing,
                                                     'n_observations': len(out_dates)}


def load_metric_series(metric_id, source_date_ymd, as_of=None, data_dir=None,
                       trusted_root=None):
    """按指标 ID 自登记接入点载入历史序列(只读)。

    source_date_ymd: 使用哪一天的采集档(resolve_inputs 精确/fallback 规则);
    as_of: 研究截止 ISO 时点(缺省=source_date 日末,北京时间)——供标准化层
    时效判定,保证回放确定性(不用墙钟)。
    返回 dict: metric_id/unit/frequency/calendar/quality_status/observation_date/
    value/dates[]/values[]/series_clean/source{access_point,file,file_date,sha256,exact}。
    """
    m = fe.metric(metric_id)
    if m is None:
        raise ValueError(f"指标 {metric_id} 不在注册表(config/metric_registry.json)")
    if as_of is None:
        as_of = (f"{source_date_ymd[:4]}-{source_date_ymd[4:6]}-"
                 f"{source_date_ymd[6:]}T23:59:59+08:00")
    src = m.get('source')

    if src == 'macro_collector':
        # 接入点A: resolve_inputs(Layer 3 输入解析,FIX7/8 可信边界+规范文件名核验)
        inputs = sb.resolve_inputs(source_date_ymd, data_dir=data_dir or sb.DATA_DIR,
                                   trusted_root=trusted_root)
        info = (inputs or {}).get('macro')
        if not info:
            # Charter7-6: 老日期优雅降级——resolve_inputs 已同步查过采集目录
            # 与其 archive/ 归档(归档在窗内时返回 archived 档,不走到这里);
            # 此处把已查范围如实写进错误,不再裸 LookupError(文件选择仍
            # 一律经 resolve_inputs 规范核验,本模块不 glob/不猜文件名)
            raise LookupError(
                f"{source_date_ymd} 新鲜度窗内无可用 macro 采集档"
                f"(resolve_inputs 已查 {sb.DATA_DIR} 与 archive/ 归档均无窗内"
                "档——历史窗口过期;采集档可全量重拉重建,归档读回路径见"
                " snapshot_builder.resolve_inputs)")
        # 经标准化层转递: 读取动作仅服务于 normalize_macro 的标准化输入
        # (路径来自 resolve_inputs 已验证物理路径,非本模块自行查找);
        # Charter7-6: 归档档(resolve_inputs 标 archived 的 .gz=gzip 容器)
        # 读回后解压,sha256 按解压后原始字节计算(与未压缩口径一致)
        with open(info['file'], 'rb') as f:              # ACCESS_POINT_EXEMPT(标准化层转递)
            raw_bytes = f.read()
        if info.get('archived'):
            raw_bytes = gzip.decompress(raw_bytes)
        sha = hashlib.sha256(raw_bytes).hexdigest()
        raw = json.loads(raw_bytes.decode('utf-8'))
        data = raw.get('data') or {}
        facts = {f.get('metric_id'): f
                 for f in fe.normalize_macro(data, as_of, os.path.basename(info['file']))}
        fact = facts.get(metric_id)
        data_key = _MACRO_DATA_KEY.get(metric_id, metric_id)
        item = data.get(data_key) or {}
        s = item.get('series') or {}
        dates, values, clean = _clean_series(s.get('dates'), s.get('values'))
        return {'metric_id': metric_id, 'unit': m['unit'],
                'frequency': m['frequency'], 'calendar': m['calendar'],
                'economy': m.get('economy'),
                'quality_status': (fact or {}).get('quality_status'),
                'observation_date': (fact or {}).get('observation_date'),
                'value': (fact or {}).get('value'),
                'dates': dates, 'values': values, 'series_clean': clean,
                'source': {'access_point': ACCESS_POINTS['macro'],
                           'file': os.path.basename(info['file']),
                           'file_date': info['file_date'], 'exact': info['exact'],
                           'sha256': sha}}

    if src in ('global_market_collector', 'jp_market_collector',
               'ea_market_collector', 'shiller_collector'):
        # 接入点B: 快照历史序列(write=False 全内存,零落盘)——global 既有,
        # jp/ea 为 IA-P1-GAP08 R47-F3 覆盖面扩展(F2 接线后序列在 store);
        # shiller=Charter6-P2 估值序列(merge_series_sections lift 后在 store)
        ch = {'global_market_collector': 'global', 'jp_market_collector': 'jp',
              'ea_market_collector': 'ea',
              'shiller_collector': 'shiller'}[src]
        snap = sb.build_snapshot(target_ymd=source_date_ymd,
                                 data_dir=data_dir or sb.DATA_DIR, write=False,
                                 as_of=as_of, trusted_root=trusted_root)
        series = (snap.get('series_store') or {}).get(metric_id) or {}
        fact = next((f for f in snap.get('facts', [])
                     if f.get('metric_id') == metric_id), None)
        st = (snap.get('sources_status') or {}).get(ch) or {}
        dates, values, clean = _clean_series(series.get('dates'), series.get('values'))
        return {'metric_id': metric_id, 'unit': m['unit'],
                'frequency': m['frequency'], 'calendar': m['calendar'],
                'economy': m.get('economy'),
                'quality_status': (fact or {}).get('quality_status'),
                'observation_date': (fact or {}).get('observation_date'),
                'value': (fact or {}).get('value'),
                'dates': dates, 'values': values, 'series_clean': clean,
                'source': {'access_point': ACCESS_POINTS[ch],
                           'file': st.get('file'), 'file_date': st.get('file_date'),
                           'exact': st.get('status') == 'EXACT',
                           'sha256': st.get('sha256')}}

    raise ValueError(f"指标 {metric_id} 来源 {src!r} 无登记接入点"
                     f"(本包支持 macro_collector/global_market_collector/"
                     f"jp_market_collector/ea_market_collector/"
                     f"shiller_collector;"
                     f"fact_engine(derived) 类须由上游双输入构造,不在本模块展开;"
                     f"japan_rate_collector 类=flat 单点无序列,无历史查询接入点)")


def query_window(payload, start, end, lookback=0, economy=None):
    """区间截取: [start,end] 内观测 + 窗口前 lookback 个预热观测(供滚动计算)。

    economy: 可选经济体过滤(GAP08 R47-F3,取值域 ECONOMIES)——非 None 且与
    payload.economy 不等(含 payload 无 economy 字段)→如实空窗,coverage.note
    披露过滤不命中,不造数据;None=不过滤(既有行为不变)。

    返回 dict(dates/values 自序列末预热点起,window_* 为窗口内首末;缺窗口数据
    如实返回空窗与 coverage 说明,不造点)。
    """
    if economy is not None and payload.get('economy') != economy:
        return {'dates': [], 'values': [], 'coverage': {
            'requested': [start, end], 'n_window': 0, 'n_lookback': 0,
            'economy_filter': {'requested': economy,
                               'metric_economy': payload.get('economy'),
                               'matched': False},
            'note': (f"economy 过滤不命中(指标经济体={payload.get('economy')!r}"
                     f"≠请求 {economy!r});如实空窗,不造数据")}}
    dates, values = payload['dates'], payload['values']
    idx = [i for i, d in enumerate(dates) if start <= d <= end]
    if not idx:
        return {'dates': [], 'values': [], 'coverage': {
            'requested': [start, end], 'n_window': 0, 'n_lookback': 0,
            'note': '窗口内无观测(数据不足如实缺席,不填0)'}}
    i0, i1 = idx[0], idx[-1]
    lo = max(0, i0 - lookback)
    return {'dates': dates[lo:i1 + 1], 'values': values[lo:i1 + 1],
            'coverage': {'requested': [start, end],
                         'window_first': dates[i0], 'window_last': dates[i1],
                         'n_window': i1 - i0 + 1, 'n_lookback': i0 - lo}}


def inner_join(payload_a, payload_b, start=None, end=None):
    """共同实际观测日内连接(升序交集;correlation_calculator.paired_returns 同式,
    算术对齐不假设日历)。可选用 [start,end] 预过滤。"""
    da = dict(zip(payload_a['dates'], payload_a['values']))
    db = dict(zip(payload_b['dates'], payload_b['values']))
    common = sorted(set(da) & set(db))
    if start is not None:
        common = [d for d in common if d >= start]
    if end is not None:
        common = [d for d in common if d <= end]
    return common, [da[d] for d in common], [db[d] for d in common]


def _group_representative(dates, values, key_fn, label):
    """网格化通用: 每格取格内最后有效观测为代表(升序天然保证'最后')。"""
    rep = {}
    for d, v in zip(dates, values):
        rep[key_fn(d)] = (d, v)      # 同格后写覆盖前写=格内最后观测
    keys = sorted(rep)
    return {'dates': [rep[k][0] for k in keys], 'values': [rep[k][1] for k in keys],
            'grid_keys': keys, 'grid': label,
            'rule': f'{label}代表值=该{label}内最后有效观测'}


def align_to_iso_week(payload):
    """ISO 周网格化: 代表=该 ISO 周(周一起)内最后有效观测。
    与 fact_engine week 口径同构(其周基准=本 ISO 周之前最后观测;本函数给出
    周网格代表值,两口径互为对偶,登记于 P03_W1_E2EA_REPORT §对齐规则)。"""
    return _group_representative(payload['dates'], payload['values'],
                                 lambda d: tc.iso_week_bounds(date.fromisoformat(d))[0],
                                 'ISO周')


def align_to_month(payload):
    """自然月网格化: 代表=该自然月内最后有效观测(fact_engine mtd 基准=
    前一自然月最后观测的同构网格)。"""
    return _group_representative(payload['dates'], payload['values'],
                                 lambda d: d[:7], '自然月')


def interval_change(dates, values, unit, start=None, end=None):
    """区间变动(单位纪律与 fact_engine.compute_period_returns emit() 同式:
    利率类→pp+bp;价格类→pct;计数/其他→绝对差)。

    基准规则(登记,fact_engine 同口径): end 值=≤end 最后观测;基准=严格早于
    start 的最后观测(不取 start 当日观测,与"期开始之前最后有效观测"一致);
    start=None → 基准=序列首观测。数据不足→available=False+原因(不回退0)。
    """
    if len(dates) != len(values) or not dates:
        return {'available': False, 'reason': '无观测序列'}
    pairs = sorted(zip([str(d)[:10] for d in dates], [float(v) for v in values]))
    ds = [p[0] for p in pairs]
    vs = [p[1] for p in pairs]
    if end is not None:
        cands = [i for i, d in enumerate(ds) if d <= end]
        if not cands:
            return {'available': False, 'reason': f'end({end})之前无观测'}
        end_i = cands[-1]
    else:
        end_i = len(ds) - 1
    if start is not None:
        base_cands = [i for i in range(end_i + 1) if ds[i] < start]
        if not base_cands:
            return {'available': False, 'reason': f'start({start})之前无基准观测'}
        base_i = base_cands[-1]
    else:
        base_i = 0
    d0, v0, d1, v1 = ds[base_i], vs[base_i], ds[end_i], vs[end_i]
    out = {'basis_date': d0, 'basis_value': v0, 'end_date': d1, 'end_value': v1,
           'n_sessions_between': end_i - base_i}
    if unit in fe.RATE_UNITS:
        out['pp_change'] = round(v1 - v0, 4)
        out['bp_change'] = round((v1 - v0) * 100, 1)
        out['formula'] = f'{d1}值−{d0}值(百分点;1pp=100bp)'
    elif unit in fe.PRICE_LIKE_UNITS:
        if v0 == 0:
            return {'available': False, 'reason': '基准值为0,百分比变化不可定义'}
        out['pct_change'] = round((v1 / v0 - 1.0) * 100.0, 4)
        out['formula'] = f'({d1}值/{d0}值−1)×100'
    else:
        out['abs_change'] = round(v1 - v0, 4)
        out['formula'] = f'{d1}值−{d0}值(绝对变化)'
    return out


def pearson(xs, ys):
    """皮尔逊相关(correlation_calculator.pearson 同式;n<3或零方差→None)。"""
    n = len(xs)
    if n != len(ys) or n < 3:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx <= 0 or vy <= 0:
        return None
    return cov / (vx ** 0.5 * vy ** 0.5)


def rolling_correlation(dates, values_a, values_b, window):
    """滚动相关: 对逐观测日差分序列取最近 window 个差分对的 pearson。

    返回 [(as_of_date, rho_round4)],自第 window 个观测起(差分样本≥window)。
    """
    out = []
    for i in range(window, len(dates)):
        da = [values_a[j] - values_a[j - 1] for j in range(i - window + 1, i + 1)]
        db = [values_b[j] - values_b[j - 1] for j in range(i - window + 1, i + 1)]
        rho = pearson(da, db)
        out.append((dates[i], None if rho is None else round(rho, 4)))
    return out


def _main():
    ap = argparse.ArgumentParser(description='研究历史查询(E2E-A;接入点见模块头登记)')
    ap.add_argument('--metric', required=True)
    ap.add_argument('--start', required=True, help='YYYY-MM-DD')
    ap.add_argument('--end', required=True, help='YYYY-MM-DD')
    ap.add_argument('--source-date', required=True, help='采集档日期 YYYYMMDD')
    ap.add_argument('--lookback', type=int, default=0)
    ap.add_argument('--economy', default=None, choices=ECONOMIES,
                    help='可选经济体过滤(R47-F3;非 None 且与指标 economy 不等→如实空窗)')
    args = ap.parse_args()
    payload = load_metric_series(args.metric, args.source_date)
    win = query_window(payload, args.start, args.end, lookback=args.lookback,
                       economy=args.economy)
    print(json.dumps({'metric_id': args.metric, 'unit': payload['unit'],
                      'economy': payload.get('economy'),
                      'economy_filter': args.economy,
                      'quality_status': payload['quality_status'],
                      'observation_date': payload['observation_date'],
                      'source': payload['source'], 'coverage': win['coverage'],
                      'dates': win['dates'], 'values': win['values']},
                     ensure_ascii=False, indent=1))


if __name__ == '__main__':
    _main()
