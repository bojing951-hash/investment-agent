#!/usr/bin/env python3
"""IA-P03-W1 E2E-A: 利率类 vs 黄金类背离检测器(纯计算,零网络零文件IO)

合同 E2EA-AC-02: 合成三情形行为正确——背离在场触发/不在场不触发/临界按登记
规则可复现;规则与代码常量一致并登记;真实回放日志参数 echo=代码常量=报告
登记值(证明未事后调参)。

检测规则 RD-DIV-001(冻结登记于 docs/P03_W1_E2EA_REPORT.md §参数冻结;运行后禁回改):

  输入: 实际利率序列 r(t)(TIPS_10Y,registry 优先级①)与金价序列 g(t)(GOLD_F),
        共同实际观测日内连接(升序交集,算术对齐不假设日历);
  逐期统计(对检测窗口 [start,end] 内每个共同观测日 t_i,且 i>=ROLLING_WINDOW):
    rho(t_i)      = pearson(最近 W=ROLLING_WINDOW 个 Δr, Δg)(日变化相关,round4)
    chg_r_bp(t_i) = round((r(t_i) − r(t_{i−W})) × 100, 1)   (利率 pp→bp,
                    与 fact_engine RATE_UNITS 口径一致 fact_engine.py:128-131)
    chg_g_pct(t_i)= round((g(t_i)/g(t_{i−W}) − 1) × 100, 4) (价格→pct,
                    与 fact_engine PRICE_LIKE_UNITS 口径一致 fact_engine.py:124-127)
  判定式(阈值**含等号**;比较基于 round 后统计值,临界可精确构造复现):
    cond_corr(t) = rho(t) is not None and rho(t) >= +0.30   (相关性符号翻转)
    cond_move(t) = chg_r_bp(t) >= +25.0 and chg_g_pct(t) >= +2.0
                   (实际利率大幅上行而金价坚挺上行)
    triggered(t) = cond_corr(t) or cond_move(t)
  窗口判定: 窗口内存在 >=1 个 triggered(t) → 窗口触发。
"""
import json

RULE_ID = 'RD-DIV-001'
ROLLING_WINDOW = 60          # 共同观测日差分样本数(约一个季度;60d 先例=correlation_calculator)
CORR_THRESHOLD = 0.30        # 日变化相关由正常负相关翻转为显著正相关的阈值(含等号)
RATE_BP_THRESHOLD = 25.0     # 窗口实际利率上行幅度阈值,bp(含等号)
GOLD_PCT_THRESHOLD = 2.0     # 同窗金价坚挺上行阈值,%(含等号)
THRESHOLDS_INCLUSIVE = True  # 登记语义: 各阈值比较均为 >=(等号触发)


def echo_params():
    """冻结参数 echo(真实回放日志第一要素;日志echo=代码常量=报告登记值)。"""
    return {'rule_id': RULE_ID, 'rolling_window': ROLLING_WINDOW,
            'corr_threshold': CORR_THRESHOLD,
            'rate_bp_threshold': RATE_BP_THRESHOLD,
            'gold_pct_threshold': GOLD_PCT_THRESHOLD,
            'thresholds_inclusive': THRESHOLDS_INCLUSIVE,
            'stats_rounding': {'rho': 4, 'chg_r_bp': 1, 'chg_g_pct': 4}}


def _pearson(xs, ys):
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


def detect_divergence(rate_dates, rate_values, gold_dates, gold_values,
                      start, end, params=None):
    """回放检测(纯函数)。

    rate_*/gold_*: 全序列(滚动统计在**全序列**共同观测上计算,窗口前观测自然
    提供预热;调用方无须自行截预热);
    start/end: 检测窗口(YYYY-MM-DD)——仅窗口内的统计行进入 series/判定;
    params: 缺省=冻结常量。
    返回 dict: params/alignment/window/series(逐期)/summary/triggered/trigger_points。
    """
    p = params or echo_params()
    W = p['rolling_window']
    da = dict(zip([str(d)[:10] for d in rate_dates], [float(v) for v in rate_values]))
    db = dict(zip([str(d)[:10] for d in gold_dates], [float(v) for v in gold_values]))
    common_all = sorted(set(da) & set(db))          # 全序列共同观测(预热来源)
    r = [da[d] for d in common_all]
    g = [db[d] for d in common_all]
    in_window = [d for d in common_all if start <= d <= end]

    series, trigger_points = [], []
    for i in range(W, len(common_all)):
        d = common_all[i]
        if not (start <= d <= end):
            continue
        diffs_r = [r[j] - r[j - 1] for j in range(i - W + 1, i + 1)]
        diffs_g = [g[j] - g[j - 1] for j in range(i - W + 1, i + 1)]
        rho_raw = _pearson(diffs_r, diffs_g)
        rho = None if rho_raw is None else round(rho_raw, 4)
        chg_r_bp = round((r[i] - r[i - W]) * 100, 1)
        chg_g_pct = round((g[i] / g[i - W] - 1.0) * 100, 4)
        cond_corr = rho is not None and rho >= p['corr_threshold']
        cond_move = (chg_r_bp >= p['rate_bp_threshold']
                     and chg_g_pct >= p['gold_pct_threshold'])
        row = {'date': d, 'rho': rho, 'chg_r_bp': chg_r_bp,
               'chg_g_pct': chg_g_pct, 'cond_corr': cond_corr,
               'cond_move': cond_move, 'triggered': cond_corr or cond_move}
        series.append(row)
        if row['triggered']:
            trigger_points.append(row)
    if not series:
        return {'rule_id': p['rule_id'], 'params': p,
                'alignment': {'rule': '共同实际观测日内连接(升序交集);'
                                      '滚动统计在全序列共同观测上计算(预热=窗口前观测)',
                              'n_common': len(in_window),
                              'n_common_total': len(common_all)},
                'window': {'start': start, 'end': end},
                'series': [], 'trigger_points': [],
                'summary': {'n_common': len(in_window), 'n_scored': 0,
                            'n_triggered': 0,
                            'reason': (f'窗口内无可评分观测(全序列共同观测'
                                       f'{len(common_all)}须>{W}且窗口内须含'
                                       f'第{W + 1}个及以后的共同观测;如实缺席不造点)')},
                'triggered': False}
    rhos = [x['rho'] for x in series if x['rho'] is not None]
    return {'rule_id': p['rule_id'], 'params': p,
            'alignment': {'rule': '共同实际观测日内连接(升序交集);'
                                  '滚动统计在全序列共同观测上计算(预热=窗口前观测)',
                          'n_common': len(in_window),
                          'n_common_total': len(common_all)},
            'window': {'start': start, 'end': end,
                       'window_first': in_window[0], 'window_last': in_window[-1]},
            'series': series, 'trigger_points': trigger_points,
            'summary': {'n_common': len(in_window), 'n_scored': len(series),
                        'n_triggered': len(trigger_points),
                        'first_trigger_date': trigger_points[0]['date'] if trigger_points else None,
                        'last': series[-1],
                        'rho_min': min(rhos) if rhos else None,
                        'rho_max': max(rhos) if rhos else None},
            'triggered': bool(trigger_points)}


if __name__ == '__main__':
    # 自检入口: 以冻结参数 echo 打印(供人工核对日志echo=常量=登记值)
    print(json.dumps(echo_params(), ensure_ascii=False, sort_keys=True))
