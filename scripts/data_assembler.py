#!/usr/bin/env python3
"""数据装配器(Layer 3渲染) — 从研究快照生成GLM数据包(spec §6/§16重构)

2026-10-17第七轮重写: 原实现glob取各源"最新文件"自行拼装(文件最新≠数据最新,
且派生值沿用采集器各自口径)。现改为: 读取当日研究快照(research_snapshot_*.json,
唯一数据入口) → 渲染 data_pack_YYYYMMDD.md。

IA-P0-1(2026-10-27)收紧:
1. 不再"快照缺失时现场构建"——装配器只消费**已存在且可验证**的快照批次
   (research_provenance.select_snapshot确定性版本选择: 同日多版取最高修订版,
   候选损坏/日期不符一律拒绝),不代行构建职责;
2. Gate A FAIL或状态不可用(缺字段/非法)→拒绝生成正式数据包,退出码2;
   旧实现无任何Gate检查,FAIL快照也照常打包;
3. DEGRADED→继续装配,数据包内显式降级披露(来源fallback+不合格指标逐项列出);
4. 数据包旁挂 data_pack_YYYYMMDD.meta.json(来源快照ID/digest/Gate A状态),
   报告入口据此核验"包↔快照"绑定,杜绝旧包残留冒充与同日版本混用。

退出码: 0=成功 | 1=无有效快照 | 2=Gate A拒绝。
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
import research_provenance as rp

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, 'data')


def load_snapshot(date_str=None):
    """读取目标日期研究快照(确定性版本选择,不自动构建)。

    返回(snapshot, ymd, path);无候选/候选损坏/日期不符 → (None, ymd, 拒绝原因),
    由调用方拒绝——数据包必须绑定一个已存在、可验证的快照批次。"""
    ymd = date_str or datetime.now().strftime('%Y%m%d')
    snap, path_or_reason = rp.select_snapshot(ymd, os.path.join(DATA_DIR, 'daily'))
    return snap, ymd, path_or_reason


def latest_before(pattern, ymd, max_lag=10, data_dir=None):
    """指定日期(含)之前最新的匹配文件;返回(路径,滞后天数)或None。替代旧盲取glob最新。
    data_dir: 显式数据根目录(默认模块DATA_DIR)——报告入口重建比对时传入当日
    DATA_DIR,测试传沙箱目录,不依赖模块全局。"""
    dd = data_dir or DATA_DIR
    cands = []
    for p in glob.glob(os.path.join(dd, pattern)):
        m = re.search(r'(\d{8})', os.path.basename(p))
        if m and m.group(1) <= ymd:
            cands.append((m.group(1), p))
    if not cands:
        return None
    fd, p = sorted(cands)[-1]
    lag = (datetime.strptime(ymd, '%Y%m%d') - datetime.strptime(fd, '%Y%m%d')).days
    return (p, lag) if lag <= max_lag else None


def _lag_days(fd, ymd):
    return (datetime.strptime(ymd, '%Y%m%d') - datetime.strptime(fd, '%Y%m%d')).days


def scorecard_state(ymd, data_dir=None):
    """评分卡状态(FIX2-03): 返回(scorecard_date, is_current)。

    - 当日评分存在 → (ymd, True)——本期有效研究;
    - 仅旧评分(10天内) → (旧日期, False)——只能作历史参考,不冒充当日成功评分;
    - 无 → (None, False)。pack meta记录该状态,报告入口据此核验。"""
    got = latest_before('daily/scorecard_*.md', ymd, data_dir=data_dir)
    if not got:
        return None, False
    p, lag = got
    fd = re.search(r'(\d{8})', os.path.basename(p)).group(1)
    return fd, (lag == 0)


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


def _fv(f, spec=',.2f'):
    """数值安全格式化(FIX2-03): DEGRADED/FAIL事实的value可能是非数值
    (如采集器'N/A'字符串,事实引擎如实保留并判FAIL)——降级日仍须正常装配,
    不得因渲染格式化崩溃;数值路径输出与原格式完全一致。"""
    try:
        return f"{f.get('value'):{spec}}"
    except (TypeError, ValueError):
        return '—(不合格)'


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


def build_markdown(snapshot, ymd, data_dir=None):
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
    # FIX4-03(FIX3-NEW-003): 非核心完全缺失进数据包披露(未补零未伪造;
    # Gate A因此DEGRADED——缺的是"本期应观测而缺席",非数值坏)
    if gm.get('noncore_missing'):
        det = gm.get('noncore_missing_detail') or {}
        L.append("- ⚠️ 非核心指标缺失(本期无事实,采集遗漏/来源缺失,Gate A降级): "
                 + '; '.join(f"{m}({det.get(m, '?')})" for m in gm['noncore_missing']))
    L.append("")

    # IA-P0-1: Gate A=DEGRADED → 显式降级披露(不合格指标逐项点名,进入报告正文)
    # FIX5-01: 与主入口同口径(带采集目录,按当前正式流程核验来源文件在场——
    # 构建端与消费端不出现两套结论)
    gate_a_status = rp.gate_status(
        snapshot, data_dir=os.path.join(data_dir or DATA_DIR, 'daily'))[0]
    if gate_a_status == 'DEGRADED':
        L.append("## ⚠️ 数据质量降级披露(Gate A=DEGRADED)")
        L.append("本数据包基于**已验证但部分降级**的数据生成;以下指标质量不合格,"
                 "相关数值仅供参考,涉及这些指标的结论必须注明降级:")
        degraded = [f for f in facts if isinstance(f, dict)
                    and f.get('quality_status') not in (None, 'PASS')]
        for f in degraded:
            msgs = '; '.join(i.get('message', '') for i in f.get('issues', [])
                             if i.get('severity') in ('DEGRADED', 'FAIL'))
            L.append(f"- {f.get('display_name')}({f.get('quality_status')}): {msgs}")
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
        L.append(f"| {f.get('display_name')} | {_fv(f)} | {_wk(f)} | {f.get('unit')} | "
                 f"{f.get('observation_date')} | {note} |")

    # 汇率与商品
    L.append("")
    L.append("## 汇率与商品")
    L.append("| 资产 | 最新 | 周变化 | 观测日 | 口径 |")
    L.append("|---|---|---|---|---|")
    for f in _rows(facts, ('fx_index', 'fx_rate', 'commodity_futures')):
        L.append(f"| {f.get('display_name')} | {_fv(f)} | {_wk(f)} | "
                 f"{f.get('observation_date')} | {(f.get('calc') or '')[:30]} |")

    # 利率与信用
    L.append("")
    L.append("## 利率与信用(变化一律百分点/pp,bp)")
    L.append("| 指标 | 水平 | 周变化 | 观测日 |")
    L.append("|---|---|---|---|")
    for f in _rows(facts, ('rates_yield', 'credit_spread', 'real_rate', 'inflation_expectation',
                           'curve_slope', 'policy_rate', 'fed_futures')):
        L.append(f"| {f.get('display_name')} | {_fv(f, '.2f')} | {_wk(f)} | "
                 f"{f.get('observation_date')} |")
    for f in _rows(facts, ()):
        if isinstance(f.get('metric_id'), str) and f['metric_id'] in ('REAL_10Y', 'REAL_5Y', 'HY_IG_DIFF'):
            L.append(f"| {f.get('display_name')}(派生) | {_fv(f, '.2f')} | {_wk(f)} | "
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
        L.append(f"| {f.get('display_name')} | {_fv(f)} | {c(m1)} | {c(m12)} | "
                 f"{f.get('observation_date')} |")

    # 中国
    L.append("")
    L.append("## 中国市场")
    L.append("| 指标 | 最新 | 周变化 | 观测日 | 口径备注 |")
    L.append("|---|---|---|---|---|")
    for f in _rows(facts, ('spread_index', 'flow', 'leverage', 'valuation', 'volume_amount')):
        issues = ' '.join(i.get('message', '')[:28] for i in f.get('issues', [])
                          if i.get('severity') in ('DEGRADED', 'FAIL'))
        L.append(f"| {f.get('display_name')} | {_fv(f)} | {_wk(f)} | "
                 f"{f.get('observation_date')} | {issues} |")
    cn_idx = [f for f in facts if f.get('metric_id') in
              ('SHCOMP', 'SZCI', 'CHINEXT', 'HSI', 'HSCEI')]
    for f in cn_idx:
        L.append(f"| {f.get('display_name')} | {_fv(f)} | {_wk(f)} | "
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

    # 研究上下文: 相关性(非关键,滞后披露)
    got = latest_before('daily/correlation_*.md', ymd, data_dir=data_dir)
    if got:
        p, lag = got
        body = open(p, 'r', encoding='utf-8').read()
        L.append("")
        L.append(f"## 跨资产相关性(研究上下文,文件日期滞后{lag}天)")
        L.append(body.rstrip())

    # FIX2-03(IA-DEF-003): 评分卡为**关键步骤**产物——只有**当日**评分卡可作为
    # 本期有效研究;旧评分卡仅可作"历史参考"明确标注(不得冒充当日成功评分);
    # 当日缺失时显式披露缺失。报告入口按pack meta.scorecard_*拒绝非当日评分批次,
    # 数据包文件存在本身不再绕过本期关键研究状态检查。
    sc_date, sc_current = scorecard_state(ymd, data_dir=data_dir)
    if sc_date:
        p = os.path.join(data_dir or DATA_DIR, 'daily', f'scorecard_{sc_date}.md')
        body = open(p, 'r', encoding='utf-8').read()
        L.append("")
        if sc_current:
            L.append(f"## 宏观体制评分卡(本期{sc_date};模型观点,非客观事实)")
        else:
            lag = _lag_days(sc_date, ymd)
            L.append(f"## 宏观体制评分卡【历史参考】(⚠️非本期评分——本期评分缺失/未成功;"
                     f"以下为{sc_date}旧评分,滞后{lag}天,不得当作当日成功评分)")
        L.append(body.rstrip())
    else:
        L.append("")
        L.append("## ⚠️ 本期宏观体制评分卡缺失(当日评分文件不存在;评分步骤失败或未运行;"
                 "正式报告生成将被拒绝,直至当日评分可用)")

    ns = latest_before('news/news_summary_*.md', ymd, max_lag=8, data_dir=data_dir)
    if ns:
        p, lag = ns
        body = open(p, 'r', encoding='utf-8').read()
        L.append("")
        L.append(f"## 新闻摘要(研究上下文,文件滞后{lag}天)")
        L.append(body.rstrip())

    return '\n'.join(L) + '\n'


def main():
    snapshot, ymd, path = load_snapshot()
    if snapshot is None:
        print(f"❌ {ymd}无有效研究快照,数据包未生成({path};先跑snapshot_builder)")
        sys.exit(1)
    status, reason = rp.gate_status(snapshot, data_dir=os.path.dirname(path))
    if not rp.gate_allows_formal_research(status):
        # FAIL / None(缺gate_a字段/状态非法): 均不得生成正式数据包(不得默认PASS)
        print(f"⛔ Gate A {'FAIL' if status == 'FAIL' else '不可用'}"
              f"{'(' + reason + ')' if reason else ''}——拒绝生成正式数据包(退出码2)")
        print(f"   快照: {os.path.basename(path)} | 诊断: {rp.gate_reason_desc(snapshot)}")
        print("   处置: 数据缺失已在快照中披露;修复采集后以--allow-revision生成修订版快照")
        sys.exit(2)
    out = os.path.join(DATA_DIR, 'weekly', f"data_pack_{ymd}.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(build_markdown(snapshot, ymd))
    sc_date, sc_current = scorecard_state(ymd)
    # IA-P0-1: 数据包meta sidecar——包↔快照绑定(报告入口核验),旧包/混版自动失配;
    # FIX-01: 附数据包实际内容摘要——下游读取实际文件重算比对,声明值不被信任;
    # FIX2-03: 附评分卡状态——报告入口拒绝"仅历史参考评分/评分缺失"的正式生成
    rp.write_meta(out, {
        'source': 'snapshot',
        'generated_by': 'data_assembler',
        'generated_at': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        **rp.provenance_of(snapshot, path),
        'pack_file': os.path.basename(out),
        'pack_digest': rp.digest_file(out),
        'scorecard_date': sc_date,
        'scorecard_current': bool(sc_current),
        # FIX4-03: 数据包记录非核心完全缺失(与快照gate_a一致;报告入口的
        # verify_meta_gate_a仍以gate_a为权威,此为披露性冗余记录)
        'noncore_missing': (snapshot.get('gate_a') or {}).get('noncore_missing') or [],
    })
    print(f"✅ 数据包: {out} ({os.path.getsize(out)} bytes)"
          + (" [DEGRADED-已披露]" if status == 'DEGRADED' else ''))


if __name__ == '__main__':
    main()
