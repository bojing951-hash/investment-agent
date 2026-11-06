#!/usr/bin/env python3
"""经济体专用异常规则模块(IA-P1-WP-G = P1 收口链 #20;P1_DESIGN §六 L175 + §八.2 范围2)

DP-G2 定值=形态②(冻结章§四裁定): 新增经济体专用规则模块——纯 A 类新增,
复用既有阈值登记结构(anomaly_detector.py L27-L32 同构: 模块常量+echo_params+
含等号判定+round4 统计)与 registry economy 维度(规则对成员=registry economy
实取推导),零触碰封版件 anomaly_detector.py(US 对 RD-DIV-001 划界,不重复实现)。

规则族(登记于 REPORT §零.5,先登记后运行,运行后禁回改):
  RD-DIV-CN-001  USDCNY × SHCOMP   预期符号 s=−1(人民币走弱↔A股承压,负共动)
  RD-DIV-JP-001  USDJPY × NIKKEI225 预期符号 s=+1(日元走弱↔出口股利好,正共动)
  RD-DIV-EA-001  EURUSD × DAX      预期符号 s=−1(欧元走强↔出口竞争力受损,负共动)

判定式(机械;阈值含等号;逐期统计与 anomaly_detector L80-L98 同构——共同实际
观测日升序交集上滚动 W 日差分 pearson,窗口前观测自然预热):
  cond_corr  = rho is not None and (rho × s) <= −CORR_THRESHOLD
               (相关性显著逆转登记的机械预期符号)
  cond_move  = (chg_fx_pct >= +FX_PCT_THRESHOLD) and (s × chg_eq_pct <= −EQ_PCT_THRESHOLD)
               (驱动窗口变动达阈而响应按预期符号反向达阈)
  triggered  = cond_corr or cond_move

预期符号=登记的机械模型假设(非事实);本模块输出=统计背离描述,非投资建议;
描述统计非因果。纯计算零文件 IO 零网络;序列输入由调用方自快照 series_store
提供(监测面零直读采集档,§八.2 要点①)。
"""
import json

# ── 登记常量(与 anomaly_detector.py L28-L32 阈值登记结构同构;REPORT §零.5) ──
ROLLING_WINDOW = 60          # 共同观测日差分样本数(anomaly_detector W=60 同值先例)
CORR_THRESHOLD = 0.30        # 相关系数逆转阈值(含等号)
FX_PCT_THRESHOLD = 2.0       # 驱动(fx)窗口变动阈值,%(含等号)
EQ_PCT_THRESHOLD = 2.0       # 响应(eq)按预期符号反向变动阈值,%(含等号)
THRESHOLDS_INCLUSIVE = True  # 登记语义: 各阈值比较均含等号

# 规则族登记(registry v2.3.0 实取 economy 字段推导;REPORT §零.5 登记表)
RULES = {
    'CN': {'rule_id': 'RD-DIV-CN-001', 'economy': 'CN',
           'fx_metric': 'USDCNY', 'eq_metric': 'SHCOMP',
           'expected_corr_sign': -1,
           'rationale': '登记机械预期: 人民币走弱(USDCNY↑)↔A股承压(SHCOMP↓),负共动[模型假设非事实]'},
    'JP': {'rule_id': 'RD-DIV-JP-001', 'economy': 'JP',
           'fx_metric': 'USDJPY', 'eq_metric': 'NIKKEI225',
           'expected_corr_sign': +1,
           'rationale': '登记机械预期: 日元走弱(USDJPY↑)↔出口股利好(NIKKEI225↑),正共动[模型假设非事实]'},
    'EA': {'rule_id': 'RD-DIV-EA-001', 'economy': 'EA',
           'fx_metric': 'EURUSD', 'eq_metric': 'DAX',
           'expected_corr_sign': -1,
           'rationale': '登记机械预期: 欧元走强(EURUSD↑)↔出口竞争力受损(DAX↓),负共动[模型假设非事实]'},
}
# US 划界(如实): US 对(TIPS_10Y×GOLD_F)=既有封版 RD-DIV-001(anomaly_detector.py,
# 第一层 P0-3 落地链交付件)——本模块零重复实现零触碰;HK/GLOBAL 无登记规则
# (registry economy 值域内无经典共动对双成员序列在场面,如实缺席不造规则)。
US_PAIR_OWNER = 'RD-DIV-001@anomaly_detector.py(封版件,零触碰划界)'

MONITOR_DISCLAIMER = ('常态监测输出=链路健康/数据新鲜度/统计背离描述,非投资建议;'
                      '缺值如实缺席不填0;规则预期符号为登记的机械模型假设。')


def echo_params(rule):
    """冻结参数 echo(登记=常量=REPORT §零.5 登记值;日志echo=常量=登记,证明未事后调参)。"""
    return {'rule_id': rule['rule_id'], 'economy': rule['economy'],
            'rolling_window': ROLLING_WINDOW,
            'expected_corr_sign': rule['expected_corr_sign'],
            'corr_threshold': CORR_THRESHOLD,
            'fx_pct_threshold': FX_PCT_THRESHOLD,
            'eq_pct_threshold': EQ_PCT_THRESHOLD,
            'thresholds_inclusive': THRESHOLDS_INCLUSIVE,
            'stats_rounding': {'rho': 4, 'chg_fx_pct': 4, 'chg_eq_pct': 4}}


def _pearson_full(xs, ys):
    """皮尔逊相关(anomaly_detector._pearson 同式;n<3或零方差→None)。"""
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


def detect_economy_divergence(rule, fx_dates, fx_values, eq_dates, eq_values,
                              start, end, params=None):
    """经济体对背离检测(纯函数;anomaly_detector.detect_divergence 同构)。

    rule: RULES[econ](或同构 dict);fx_*/eq_*: 全序列(滚动统计在全序列共同观测
    上计算,窗口前观测自然预热);start/end: 检测窗口(YYYY-MM-DD)。
    返回 dict: rule_id/economy/params/alignment/window/series(逐期)/summary/
    triggered/trigger_points——缺席(数据不足)如实 reason 不造点。
    """
    p = params or echo_params(rule)
    W = p['rolling_window']
    s = p['expected_corr_sign']
    da = dict(zip([str(d)[:10] for d in fx_dates], [float(v) for v in fx_values]))
    db = dict(zip([str(d)[:10] for d in eq_dates], [float(v) for v in eq_values]))
    common_all = sorted(set(da) & set(db))
    in_window = [d for d in common_all if start <= d <= end]

    series, trigger_points = [], []
    for i in range(W, len(common_all)):
        d = common_all[i]
        if not (start <= d <= end):
            continue
        diffs_f = [da[common_all[j]] - da[common_all[j - 1]]
                   for j in range(i - W + 1, i + 1)]
        diffs_e = [db[common_all[j]] - db[common_all[j - 1]]
                   for j in range(i - W + 1, i + 1)]
        rho_raw = _pearson_full(diffs_f, diffs_e)
        rho = None if rho_raw is None else round(rho_raw, 4)
        fx_i, fx_w = da[d], da[common_all[i - W]]
        eq_i, eq_w = db[d], db[common_all[i - W]]
        chg_fx_pct = round((fx_i / fx_w - 1.0) * 100, 4) if fx_w else None
        chg_eq_pct = round((eq_i / eq_w - 1.0) * 100, 4) if eq_w else None
        cond_corr = rho is not None and (rho * s) <= -p['corr_threshold']
        cond_move = (chg_fx_pct is not None and chg_eq_pct is not None
                     and chg_fx_pct >= p['fx_pct_threshold']
                     and (s * chg_eq_pct) <= -p['eq_pct_threshold'])
        row = {'date': d, 'rho': rho, 'chg_fx_pct': chg_fx_pct,
               'chg_eq_pct': chg_eq_pct, 'cond_corr': cond_corr,
               'cond_move': cond_move, 'triggered': cond_corr or cond_move}
        series.append(row)
        if row['triggered']:
            trigger_points.append(row)
    base = {'rule_id': p['rule_id'], 'economy': p['economy'], 'params': p,
            'alignment': {'rule': '共同实际观测日内连接(升序交集);滚动统计在全序列共同观测上计算(预热=窗口前观测)',
                          'n_common': len(in_window),
                          'n_common_total': len(common_all)},
            'window': {'start': start, 'end': end},
            'series': series, 'trigger_points': trigger_points}
    if not series:
        base['summary'] = {'n_common': len(in_window), 'n_scored': 0,
                           'n_triggered': 0,
                           'reason': (f'窗口内无可评分观测(全序列共同观测{len(common_all)}'
                                      f'须>{W}且窗口内须含第{W + 1}个及以后的共同观测;'
                                      '如实缺席不造点)')}
        base['triggered'] = False
        return base
    rhos = [x['rho'] for x in series if x['rho'] is not None]
    base['window'].update({'window_first': in_window[0], 'window_last': in_window[-1]})
    base['summary'] = {'n_common': len(in_window), 'n_scored': len(series),
                       'n_triggered': len(trigger_points),
                       'first_trigger_date': trigger_points[0]['date'] if trigger_points else None,
                       'last': series[-1],
                       'rho_min': min(rhos) if rhos else None,
                       'rho_max': max(rhos) if rhos else None}
    base['triggered'] = bool(trigger_points)
    return base


def detect_all_from_series_store(series_store, start, end, params_map=None):
    """规则族全量检测(监测面消费入口): 序列自快照 series_store 提取(dict 入 dict 出,
    零文件 IO);任一成员序列缺席→该经济体如实缺席行(triggered=False+absent_reason),
    不造数不跳过。返回 {economy: detection_dict}。"""
    out = {}
    for econ, rule in RULES.items():
        store = series_store or {}
        sfx = store.get(rule['fx_metric']) or {}
        seq = store.get(rule['eq_metric']) or {}
        if not sfx.get('dates') or not seq.get('dates'):
            missing = [m for m, s_ in ((rule['fx_metric'], sfx), (rule['eq_metric'], seq))
                       if not s_.get('dates')]
            out[econ] = {'rule_id': rule['rule_id'], 'economy': econ,
                         'triggered': False, 'absent_reason':
                         f'series_store 序列缺席: {",".join(missing)}(如实缺席,不造序列)',
                         'window': {'start': start, 'end': end}}
            continue
        params = (params_map or {}).get(econ)
        out[econ] = detect_economy_divergence(rule, sfx['dates'], sfx['values'],
                                              seq['dates'], seq['values'],
                                              start, end, params=params)
    return out


if __name__ == '__main__':
    # 自检入口: 登记参数 echo(供人工核对 日志echo=常量=REPORT §零.5 登记值)
    print(json.dumps({e: echo_params(r) for e, r in RULES.items()},
                     ensure_ascii=False, sort_keys=True))
