#!/usr/bin/env python3
"""跨资产相关性计算(Layer 4研究引擎,2026-10-17第七轮重写)

重构要点(spec §10):
1. 数据入口=研究快照series_store(不再自行yfinance拉取,不在Layer 4直连Layer 1);
2. 身份来自指标注册表: FXI/EZU等ETF代理显式标注,TLT按"债券ETF价格"表述
   (与收益率反向),杜绝'FXI=中国''正相关=股债同跌'类因果/身份冒充;
3. 对齐=两序列共同实际观测日的内连接(交易日历无关的诚实交集),披露样本数与
   实际窗口起止日;样本不足→该对标注数据不足,不出相关系数;
4. 输出描述性统计(相关系数±解读边界),不下因果结论;20日/60日窗口分开;
5. 相关性≠因果关系声明写入输出。

输出: data/daily/correlation_YYYYMMDD.md(研究上下文,由数据包嵌入)
"""
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import fact_engine as fe

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, 'data', 'daily')

# 配对定义: a/b为注册表metric_id; disclosure为身份/口径披露(必 printed)
PAIRS = [
    {"a": "SPX", "b": "TLT", "label": "标普500 vs 20+年国债ETF",
     "disclosure": "TLT为债券**价格**ETF(与长端收益率反向);正相关=股价与债券价格同向,不等于'股债同跌',更非因果"},
    {"a": "SPX", "b": "GOLD_F", "label": "标普500 vs 黄金期货",
     "disclosure": "GOLD_F为COMEX期货主力(非现货)"},
    {"a": "DXY", "b": "SPX", "label": "美元指数 vs 标普500"},
    {"a": "DXY", "b": "GOLD_F", "label": "美元指数 vs 黄金期货"},
    {"a": "WTI_F", "b": "TLT", "label": "WTI期货 vs 国债ETF",
     "disclosure": "TLT价格口径;油价-债券价格相关性,非油价-收益率"},
    {"a": "WTI_F", "b": "EEM", "label": "WTI期货 vs 新兴市场ETF",
     "disclosure": "EEM为MSCI新兴市场代理(美元计价,含汇率影响)"},
    {"a": "SPX", "b": "EZU", "label": "标普500 vs 欧元区ETF",
     "disclosure": "EZU为欧元区股市**代理**(美元计价ETF,非当地股指)"},
    {"a": "SPX", "b": "FXI", "label": "标普500 vs 中国大盘ETF",
     "disclosure": "FXI为中国大盘股**代理**(成分含港股上市中资股,非A股指数;与沪深300口径不同)"},
    {"a": "VIX", "b": "HYG", "label": "VIX vs 高收益债ETF",
     "disclosure": "HYG为高收益债价格代理(与HY_OAS利差反向)"},
    {"a": "BTC", "b": "NDX", "label": "比特币 vs 纳斯达克100"},
    # IA-P1-WP-C(规格L171"相关性新对"): 两跨域配对追加分枝末尾;序列取自快照
    # series_store——NIKKEI225/DAX序列接线为上游WP-B F2延后面,真实运行如缺
    # 该对如实进missing("序列缺失"),非失败非0值;测试以合成快照覆盖全链路。
    {"a": "NIKKEI225", "b": "USDJPY", "label": "日经225 vs 美元/日元",
     "disclosure": "跨域配对(IA-P1-WP-C新增): 日经225为日元计价股指,与USDJPY汇率同表仅示联动,描述统计非因果"},
    {"a": "DAX", "b": "EURUSD", "label": "德国DAX vs 欧元/美元",
     "disclosure": "跨域配对(IA-P1-WP-C新增): DAX为欧元区股指,与EURUSD汇率同表仅示联动,描述统计非因果"},
]


def load_series_store(snapshot):
    return (snapshot or {}).get('series_store') or {}


def unit_change(v0, v1, unit_family):
    """P0-3 单位感知单步变化: 同族口径下 v0→v1 的变化量。

    price → (v1/v0-1)*100(百分比 pct);rate → v1-v0(百分点 pp);
    count → 百分比 pct(基数大,须标注 basis=count 近似);other → None(不可比)。
    """
    if v0 is None or v1 is None:
        return None
    if unit_family == 'price':
        return (v1 / v0 - 1.0) * 100.0
    if unit_family == 'rate':
        return v1 - v0
    if unit_family == 'count':
        return (v1 / v0 - 1.0) * 100.0
    return None


def paired_unit_changes(series_a, unit_family_a, series_b, unit_family_b):
    """P0-3: 共同观测日上的**单位感知**两侧变化序列。

    与 paired_returns(全按价格 pct)不同,本函数按各自 unit_family 取变化口径
    (rate→pp/price→pct/count→pct近似);pearson 在此变化序列上计算,修复利率×
    价格混算 pct 的口径缺陷(Agent A 独立重算证实)。

    配对纪律:
    - 共同日期升序;任一侧值为 None 的观测对跳过(dropped_null);
    - **双侧联合零基过滤**: 前值任一侧==0 → 该对丢弃(zero_base_dropped)——
      修复两侧独立过滤导致的错位配对(ra[i] 与 rb[j] 不再一一对应)。

    返回 (result|None, common);result:
      {'changes_a', 'changes_b', 'dates'(变化日), 'basis_a'|'basis_b'('pct'|'pp'),
       'family_a'|'family_b', 'n_change_pairs', 'dropped_null', 'zero_base_dropped'}
    共同观测<3 → (None, common)。unit_family 任一侧为 other → ValueError
    (调用方应先做结构化拒绝,此处 fail-loud 防混算溜进统计)。
    """
    for fam in (unit_family_a, unit_family_b):
        if fam not in ('price', 'rate', 'count'):
            raise ValueError(f"unit_family 不可比({fam!r}),拒绝混算(P0-3)")
    da = {str(d)[:10]: v for d, v in zip(series_a.get('dates', []),
                                         series_a.get('values', []))}
    db = {str(d)[:10]: v for d, v in zip(series_b.get('dates', []),
                                         series_b.get('values', []))}
    common = sorted(set(da) & set(db))
    if len(common) < 3:
        return None, common
    ca, cb, dates = [], [], []
    dropped_null = zero_base_dropped = 0
    for i in range(1, len(common)):
        a0, a1 = da[common[i - 1]], da[common[i]]
        b0, b1 = db[common[i - 1]], db[common[i]]
        if a0 is None or a1 is None or b0 is None or b1 is None:
            dropped_null += 1
            continue
        if a0 == 0 or b0 == 0:      # 双侧联合零基: 任一侧前值为0该对整体丢弃
            zero_base_dropped += 1
            continue
        ca.append(unit_change(a0, a1, unit_family_a))
        cb.append(unit_change(b0, b1, unit_family_b))
        dates.append(common[i])
    result = {'changes_a': ca, 'changes_b': cb, 'dates': dates,
              'basis_a': 'pp' if unit_family_a == 'rate' else 'pct',
              'basis_b': 'pp' if unit_family_b == 'rate' else 'pct',
              'family_a': unit_family_a, 'family_b': unit_family_b,
              'n_change_pairs': len(ca),
              'dropped_null': dropped_null,
              'zero_base_dropped': zero_base_dropped}
    return result, common


def paired_returns(series_a, series_b):
    """共同观测日内连接 → 收益率序列(算术对齐,不假设日历)。

    P0-3 同步收紧: None 观测跳过;零基过滤改**双侧联合**(前值任一侧==0→该对
    整体丢弃),修复两侧独立过滤导致的 ra/rb 错位配对(此前 zip 截断静默错位)。
    全价格对(compute_all 12 对)行为基本不变。"""
    da = {str(d)[:10]: v for d, v in zip(series_a.get('dates', []),
                                         series_a.get('values', []))}
    db = {str(d)[:10]: v for d, v in zip(series_b.get('dates', []),
                                         series_b.get('values', []))}
    common = sorted(set(da) & set(db))
    if len(common) < 3:
        return None, common
    ra, rb = [], []
    for i in range(1, len(common)):
        a0, a1 = da[common[i - 1]], da[common[i]]
        b0, b1 = db[common[i - 1]], db[common[i]]
        if a0 is None or a1 is None or b0 is None or b1 is None:
            continue
        if a0 == 0 or b0 == 0:
            continue
        ra.append(a1 / a0 - 1.0)
        rb.append(b1 / b0 - 1.0)
    return (ra, rb), common[1:]


def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx <= 0 or vy <= 0:
        return None
    return cov / (vx ** 0.5 * vy ** 0.5)


def compute_all(snapshot):
    """返回(结果列表, 缺失披露列表)。每对: label/a/b/corr20/corr60/n20/n60/dates。"""
    store = load_series_store(snapshot)
    results, missing = [], []
    for p in PAIRS:
        sa, sb = store.get(p['a']), store.get(p['b'])
        if not sa or not sb:
            missing.append(f"{p['label']}: 序列缺失({p['a'] if not sa else p['b']}不在快照series_store)")
            continue
        pair, dates = paired_returns(sa, sb)
        if not pair:
            missing.append(f"{p['label']}: 共同观测日不足(<3)")
            continue
        ra, rb = pair
        rec = {"label": p["label"], "a": p["a"], "b": p["b"],
               "disclosure": p.get("disclosure", ""),
               "corr_20d": pearson(ra[-20:], rb[-20:]),
               "n_20d": min(20, len(ra)),
               "corr_60d": pearson(ra[-60:], rb[-60:]),
               "n_60d": min(60, len(ra)),
               "window_first": dates[max(0, len(dates) - 60)],
               "window_last": dates[-1]}
        results.append(rec)
    return results, missing


def _fmt(c):
    return f"{c:+.2f}" if isinstance(c, (int, float)) else "—"


def generate_markdown(results, missing, as_of_str):
    L = [f"# 跨资产相关性({as_of_str})",
         "",
         "> 数据: 研究快照series_store;对齐=共同实际观测日;收益率为日收盘价变化。",
         "> **相关性≠因果关系**;ETF为代理载体(见各表披露);样本数<15时解读需谨慎。",
         ""]
    L.append("| 资产对 | 20日相关 | 样本 | 60日相关 | 样本 | 窗口 |")
    L.append("|---|---|---|---|---|---|")
    for r in results:
        L.append(f"| {r['label']} | {_fmt(r['corr_20d'])} | {r['n_20d']} | "
                 f"{_fmt(r['corr_60d'])} | {r['n_60d']} | {r['window_first']}~{r['window_last']} |")
    if results:
        L.append("")
        L.append("## 口径披露")
        for r in results:
            if r.get('disclosure'):
                L.append(f"- {r['label']}: {r['disclosure']}")
    if missing:
        L.append("")
        L.append("## 数据缺口(如实披露,不以内插/他源冒充)")
        for m in missing:
            L.append(f"- {m}")
    L.append("")
    L.append("## 解读边界")
    L.append("- 表值为皮尔逊相关系数(日收益率);正相关=两资产日涨跌**统计上同向**,")
    L.append("  不构成方向性/因果性结论;短窗(20日)相关受单一事件影响大。")
    L.append("- 债券ETF价格与收益率反向;VIX与HYG负相关上升通常反映风险偏好回落,")
    L.append("  属**同步现象描述**,机制解释须另行论证。")
    return "\n".join(L) + "\n"


def main(snapshot_path=None, out_path=None):
    today = datetime.now().strftime('%Y%m%d')
    if snapshot_path:
        # 显式指定(测试/回填): 直接加载
        with open(snapshot_path, 'r', encoding='utf-8') as f:
            snapshot = json.load(f)
    else:
        # IA-P0-1: 确定性版本选择——同日多版本取最高修订版(_vN),候选损坏拒绝
        import research_provenance as rp
        snapshot, reason = rp.select_snapshot(today, DATA_DIR)
        if snapshot is None:
            print(f"❌ 当日研究快照不可用: {reason}(先跑snapshot_builder)")
            sys.exit(1)
    results, missing = compute_all(snapshot)
    md = generate_markdown(results, missing, snapshot.get('research_as_of', today))
    out = out_path or os.path.join(DATA_DIR, f"correlation_{today}.md")
    with open(out, 'w', encoding='utf-8') as f:
        f.write(md)
    print(f"✅ 相关性: {out}({len(results)}对,{len(missing)}缺口)")
    return out


if __name__ == '__main__':
    main()
