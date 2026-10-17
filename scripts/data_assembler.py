#!/usr/bin/env python3
"""数据装配器(Layer 3渲染) — 从研究快照生成GLM数据包(spec §6/§16重构)

2026-10-17第七轮重写: 原实现glob取各源"最新文件"自行拼装(文件最新≠数据最新,
且派生值沿用采集器各自口径)。现改为: 读取当日研究快照(research_snapshot_*.json,
唯一数据入口) → 渲染 data_pack_YYYYMMDD.md。快照缺失时现场构建(经snapshot_builder,
其解析逻辑负责新鲜度窗与fallback披露)。

数值表全部程序确定性生成;相关性/评分卡/新闻作为研究上下文嵌入,附文件日期披露。
"""
import glob
import json
import os
import re
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import fact_engine as fe

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, 'data')


def load_snapshot(date_str=None):
    """读取(必要时构建)目标日期研究快照。"""
    ymd = date_str or datetime.now().strftime('%Y%m%d')
    path = os.path.join(DATA_DIR, 'daily', f"research_snapshot_{ymd}.json")
    if not os.path.exists(path):
        import snapshot_builder as sb
        sb.build_snapshot(target_ymd=ymd)
        if not os.path.exists(path):
            return None, ymd
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f), ymd


def latest_before(pattern, ymd, max_lag=10):
    """指定日期(含)之前最新的匹配文件;返回(路径,滞后天数)或None。替代旧盲取glob最新。"""
    cands = []
    for p in glob.glob(os.path.join(DATA_DIR, pattern)):
        m = re.search(r'(\d{8})', os.path.basename(p))
        if m and m.group(1) <= ymd:
            cands.append((m.group(1), p))
    if not cands:
        return None
    fd, p = sorted(cands)[-1]
    lag = (datetime.strptime(ymd, '%Y%m%d') - datetime.strptime(fd, '%Y%m%d')).days
    return (p, lag) if lag <= max_lag else None


# ══ 渲染 ══════════════════════════════════════════════════════════

def _wk(f):
    d = (f.get('derived') or {}).get('week') or {}
    if not d or d.get('available') is False:
        return '—'
    if 'pct_change' in d:
        return f"{d['pct_change']:+.2f}%"
    if 'pp_change' in d:
        return f"{d['pp_change']:+.2f}pp"
    if 'abs_change' in d:
        return f"{d['abs_change']:+,.1f}"
    return '—'


def _rows(facts, classes, source=None):
    out = []
    for f in facts:
        if not isinstance(f, dict):
            continue
        m = fe.metric(f.get('metric_id', ''))
        if not m:
            continue
        if classes and m.get('asset_class') not in classes:
            continue
        if source and m.get('source') != source:
            continue
        out.append(f)
    return out


def build_markdown(snapshot, ymd):
    facts = snapshot.get('facts', [])
    L = [f"# 投资数据包 {ymd}",
         "",
         f"> 数据源: 研究快照 {snapshot.get('snapshot_id')}(唯一入口,全部数值经事实引擎统一口径)",
         f"> 研究截止: {snapshot.get('research_as_of')} | Gate A: {snapshot['gate_a']['status']}",
         f"> 周变化口径: 上一ISO周最后收盘为基准;MTD=前月末;YTD=上年末(期前收盘基准)",
         ""]

    # 数据源状态与缺失披露
    L.append("## 数据源状态")
    for name, st in snapshot.get('sources_status', {}).items():
        if st.get('status') != 'EXACT':
            L.append(f"- ⚠️ {name}: {st.get('status')} {st.get('file', '')}"
                     + (f" 滞后{st.get('lag_days')}天" if st.get('lag_days') else ''))
    gm = snapshot.get('gate_a', {})
    if gm.get('core_missing'):
        L.append(f"- ⚠️ core指标缺失(相关结论不得生成): {', '.join(gm['core_missing'])}")
    if gm.get('core_fail'):
        L.append(f"- ❌ core指标FAIL: {', '.join(gm['core_fail'])}")
    L.append("")

    # 全球权益/波动率/加密
    L.append("## 全球市场")
    L.append("| 资产 | 收盘 | 周变化 | 单位 | 观测日 | 备注 |")
    L.append("|---|---|---|---|---|---|")
    for f in _rows(facts, ('equity_index', 'single_stock', 'volatility_index', 'crypto',
                           'country_etf_proxy', 'bond_etf', 'spot_commodity_etf',
                           'commodity_futures_etf')):
        ident = f.get('identity') or {}
        note = '代理' if ident.get('is_proxy') else ''
        if f.get('quality_status') != 'PASS':
            note += f" {f['quality_status']}"
        v = f.get('value')
        L.append(f"| {f.get('display_name')} | {v:,.2f} | {_wk(f)} | {f.get('unit')} | "
                 f"{f.get('observation_date')} | {note} |")

    # 汇率与商品
    L.append("")
    L.append("## 汇率与商品")
    L.append("| 资产 | 最新 | 周变化 | 观测日 | 口径 |")
    L.append("|---|---|---|---|---|")
    for f in _rows(facts, ('fx_index', 'fx_rate', 'commodity_futures')):
        L.append(f"| {f.get('display_name')} | {f.get('value'):,.2f} | {_wk(f)} | "
                 f"{f.get('observation_date')} | {(f.get('calc') or '')[:30]} |")

    # 利率与信用
    L.append("")
    L.append("## 利率与信用(变化一律百分点/pp,bp)")
    L.append("| 指标 | 水平 | 周变化 | 观测日 |")
    L.append("|---|---|---|---|")
    for f in _rows(facts, ('rates_yield', 'credit_spread', 'real_rate', 'inflation_expectation',
                           'curve_slope', 'policy_rate', 'fed_futures')):
        L.append(f"| {f.get('display_name')} | {f.get('value'):.2f} | {_wk(f)} | "
                 f"{f.get('observation_date')} |")
    for f in _rows(facts, ()):
        if isinstance(f.get('metric_id'), str) and f['metric_id'] in ('REAL_10Y', 'REAL_5Y', 'HY_IG_DIFF'):
            L.append(f"| {f.get('display_name')}(派生) | {f.get('value'):.2f} | {_wk(f)} | "
                     f"{f.get('observation_date')} |")

    # 宏观月频
    L.append("")
    L.append("## 宏观指标(月频;观测月=统计期,发布滞后属正常)")
    L.append("| 指标 | 最新 | 环比 | 同比 | 观测日 |")
    L.append("|---|---|---|---|---|")
    for f in _rows(facts, ('macro_index', 'macro_rate', 'macro_count', 'macro_price', 'sentiment',
                           'macro_count_derived')):
        d = f.get('derived') or {}
        m1, m12 = d.get('m1') or {}, d.get('m12') or {}

        def c(rec):
            if not rec or rec.get('available') is False:
                return '—'
            return (f"{rec['pct_change']:+.2f}%" if 'pct_change' in rec
                    else f"{rec['pp_change']:+.2f}pp" if 'pp_change' in rec
                    else f"{rec['abs_change']:+,.1f}")
        L.append(f"| {f.get('display_name')} | {f.get('value'):,.2f} | {c(m1)} | {c(m12)} | "
                 f"{f.get('observation_date')} |")

    # 中国
    L.append("")
    L.append("## 中国市场")
    L.append("| 指标 | 最新 | 周变化 | 观测日 | 口径备注 |")
    L.append("|---|---|---|---|---|")
    for f in _rows(facts, ('spread_index', 'flow', 'leverage', 'valuation', 'volume_amount')):
        issues = ' '.join(i.get('message', '')[:28] for i in f.get('issues', [])
                          if i.get('severity') in ('DEGRADED', 'FAIL'))
        L.append(f"| {f.get('display_name')} | {f.get('value'):,.2f} | {_wk(f)} | "
                 f"{f.get('observation_date')} | {issues} |")
    cn_idx = [f for f in facts if f.get('metric_id') in
              ('SHCOMP', 'SZCI', 'CHINEXT', 'HSI', 'HSCEI')]
    for f in cn_idx:
        L.append(f"| {f.get('display_name')} | {f.get('value'):,.2f} | {_wk(f)} | "
                 f"{f.get('observation_date')} | 指数点位 |")

    # 联邦基金期货
    curve = snapshot.get('fed_futures_curve') or []
    if curve:
        L.append("")
        L.append("## 联邦基金期货(合约=对应日历月**日均**利率隐含;不得换算为降息次数)")
        L.append("| 合约 | 价格 | 隐含日均利率 |")
        L.append("|---|---|---|")
        for c in curve[:8]:
            L.append(f"| {c.get('name') or c.get('ticker')} | {c.get('price')} | "
                     f"{c.get('implied_avg_rate')}% |")

    # 对账摘要
    if snapshot.get('reconciliation'):
        L.append("")
        L.append("## 对账与跨指标核验")
        for r in snapshot['reconciliation']:
            if r.get('result') != 'consistent':
                L.append(f"- [{r.get('result')}] {r.get('check')}: {r.get('detail')}")

    # 研究上下文(嵌入最近文件,附日期披露)
    for title, pattern, kind in (("跨资产相关性(研究上下文)", 'daily/correlation_*.md', 'md'),
                                 ("宏观体制评分卡(模型观点,非客观事实)", 'daily/scorecard_*.md', 'md')):
        got = latest_before(pattern, ymd)
        if got:
            p, lag = got
            body = open(p, 'r', encoding='utf-8').read()
            L.append("")
            L.append(f"## {title}(文件日期滞后{lag}天)")
            L.append(body.rstrip())
    ns = latest_before('news/news_summary_*.md', ymd, max_lag=8)
    if ns:
        p, lag = ns
        body = open(p, 'r', encoding='utf-8').read()
        L.append("")
        L.append(f"## 新闻摘要(研究上下文,文件滞后{lag}天)")
        L.append(body.rstrip())

    return '\n'.join(L) + '\n'


def main():
    snapshot, ymd = load_snapshot()
    if snapshot is None:
        print("❌ 无研究快照,数据包未生成(先跑snapshot_builder)")
        sys.exit(1)
    out = os.path.join(DATA_DIR, 'weekly', f"data_pack_{ymd}.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(build_markdown(snapshot, ymd))
    print(f"✅ 数据包: {out} ({os.path.getsize(out)} bytes)")


if __name__ == '__main__':
    main()
