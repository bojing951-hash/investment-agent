#!/usr/bin/env python3
"""季度展望生成器 v2.0 (第二轮审查重构, 2026-10-11)

相对v1.0的修复(对应第二轮审查第三项):
1. 触发时点: 只复盘**已完结**的自然季(期间结束后第一个周五由report_generator触发,
   或显式 --quarter YYYYQn); 当季未结束只能以【预览】生成——
   v1在季末最后一个周五(如2026-12-25)提前生成Q4季报的缺陷已废除
2. 数据口径: 整季逐日序列聚合(季初→季末/最高/最低,三个月各月末水平),不再只有
   3个月末时点——3时点无法看出季内路径与极值
3. 预测命中统计按统计周期: 只统计deadline/裁决日落在本季的预测(不再全历史混算)
4. 单位纪律同月报: 收益率/利差变化bp,百分点序列pp

用法:
  python3 quarterly_outlook.py --quarter 2026Q4  # 指定季度(已完结→正式,当季→预览)
  python3 quarterly_outlook.py                   # auto: 上一自然季已完结且今天是其后第一个周五
  python3 quarterly_outlook.py --dry-run
"""
import os
import sys
import re
import json
import glob
import argparse
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, 'data', 'daily')
OUTPUT_DIR = os.path.join(ROOT_DIR, 'output', 'quarterly')

from monthly_review import gather_month_series, KEY_SERIES_DICT, _month_bounds

# 季度末水平表里的主力序列(全序列见整季区间表)
MAJOR_SERIES = ['SPX标普500', '黄金', '美元指数DXY', 'WTI原油', 'BTC', 'VIX', 'CCC_OAS利差']


def quarter_months(q):
    """'2026Q4' → ['202610','202611','202612']"""
    y, n = int(q[:4]), int(q[-1])
    return [f"{y}{m:02d}" for m in range(3 * n - 2, 3 * n + 1)]


def quarter_is_complete(q, today=None):
    """季度三个月是否全部自然结束(第二轮#3.4)"""
    today = today or date.today()
    return quarter_months(q)[-1] < today.strftime('%Y%m')


def scorecard_of_month(ym):
    files = sorted(glob.glob(os.path.join(DATA_DIR, f'scorecard_{ym}*.json')))
    if not files:
        return None
    try:
        return json.load(open(files[-1]))
    except Exception:
        return None


def gather_quarter_series(months, data_dir=None):
    """整季聚合: 调用月度采集器逐月取数,再合并(第二轮#3.14: 不再只有3个月末时点)。"""
    by_month = {}
    for ym in months:
        m = gather_month_series(ym, data_dir)
        if m:
            by_month[ym] = m
    quarter = {}
    for label, unit in KEY_SERIES_DICT.items():
        month_stats = [(ym, s) for ym, mm in by_month.items() for lbl, s in mm.items() if lbl == label]
        if len(month_stats) < 2:
            continue
        month_stats.sort()
        first = month_stats[0][1]['first']
        last = month_stats[-1][1]['last']
        lo = min(s['min'] for _, s in month_stats)
        hi = max(s['max'] for _, s in month_stats)
        delta = last - first
        if unit == 'pct':
            chg = f"{delta / abs(first) * 100:+.2f}%" if first else "N/A"
        elif unit == 'bp':
            chg = f"{delta * 100:+.0f}bp"
        else:
            chg = f"{delta:+.2f}pp"
        quarter[label] = {
            'first': first, 'last': last, 'min': lo, 'max': hi, 'chg_str': chg,
            'obs_count': sum(s['obs_count'] for _, s in month_stats),
            'first_obs': month_stats[0][1]['first_obs'], 'last_obs': month_stats[-1][1]['last_obs'],
            'month_ends': {ym: s['last'] for ym, s in month_stats},
        }
    return quarter, by_month


def build_data_block(q, data_dir=None, views_path=None):
    months = quarter_months(q)
    preview = not quarter_is_complete(q)
    header = (f"# {q} 季度数据汇总(整季逐日序列聚合,自动提取)\n"
              "> 数据来源: 原始采集序列直读(IA-P0-1标注: 非研究快照链产物;"
              "季度聚合为历史路径复盘,当日研究结论仍以快照链为准)\n")
    if preview:
        header = ("# 【预览】" + header.lstrip('# ')
                  + "\n> ⚠️ 本报告生成于**季度结束前**,数据覆盖不完整。所有结论为预览性质,"
                    "不得表述为完整季度判断,正式展望须待季度结束后重新生成。\n")
    lines = [header]

    quarter, by_month = gather_quarter_series(months, data_dir)

    lines.append("## 整季区间(季初→季末,含季内最高/最低;收益率/利差变化bp、百分点pp)\n")
    lines.append("| 序列 | 季初 | 季末 | 季内最低 | 季内最高 | 季变化 | 观测数 |")
    lines.append("|------|------|------|----------|----------|--------|--------|")
    for label, s in quarter.items():
        lines.append(f"| {label} | {s['first']:.2f} | {s['last']:.2f} | {s['min']:.2f} | {s['max']:.2f} | "
                     f"{s['chg_str']} | {s['obs_count']} |")

    lines.append("\n## 各月末水平(三个月路径;非仅时点比较,季内极值见上表)\n")
    cols = [l for l in MAJOR_SERIES if l in quarter]
    lines.append("| 月份 | " + " | ".join(cols) + " |")
    lines.append("|------" * (len(cols) + 1) + "|")
    for ym in months:
        row = [ym]
        for c in cols:
            v = quarter[c]['month_ends'].get(ym)
            row.append(f"{v:.2f}" if isinstance(v, (int, float)) else "-")
        lines.append("| " + " | ".join(row) + " |")

    lines.append("\n## 各月体制快照(每月最后一份评分卡)")
    for ym in months:
        sc = scorecard_of_month(ym)
        if sc:
            lines.append(f"- {ym}: 计算={sc.get('regime')}, 确认={sc.get('confirmed_regime')}({sc.get('regime_status')}), "
                         f"增长{sc.get('growth_total', 0):+d}/通胀{sc.get('inflation_total', 0):+d}")
        else:
            lines.append(f"- {ym}: (无评分卡)")

    # 论点状态轨迹(整季history)
    tp = os.path.join(ROOT_DIR, 'config', 'thesis.json')
    if os.path.exists(tp):
        d = json.load(open(tp))
        mnums = {int(m[4:6]) for m in months}
        moves = [f"#{t['id']}{t.get('name','')}: {h}"
                 for t in d.get('theses', []) for h in t.get('history', [])
                 if h.split('/')[0].isdigit() and int(h.split('/')[0]) in mnums]
        lines.append("\n## 本季论点状态变更轨迹")
        lines.extend(f"- {m}" for m in moves or ['(本季无论点变更记录)'])

    # 配置观点评级轨迹 + 周期内预测统计(第二轮#3.16)
    import allocation_engine
    views = allocation_engine.load_views(views_path)
    if views:
        lines.append("\n## 配置观点评级轨迹(allocation_views.json history)")
        for v in views.get('views', []):
            hist = v.get('history', [])
            if hist:
                lines.append(f"- {v['asset']}: {'; '.join(hist[-6:])}")
        start, end = _month_bounds(months[0])[0], _month_bounds(months[-1])[1]
        pp = allocation_engine.predictions_in_period(views, start.strftime('%Y%m%d'), end.strftime('%Y%m%d'))
        cn = allocation_engine.PRED_STATUS_CN
        lines.append("\n## 本季预测到期与裁决(按统计周期,非全历史)")
        lines.append(f"- 本季到期{len(pp['due'])}条 / 本季裁决{len(pp['resolved'])}条"
                     f"(命中{pp['counts']['hit']}/证伪{pp['counts']['miss']}/无法裁决{pp['counts']['inconclusive']})")
        for p in pp['due']:
            mark = f" → 裁决:{p.get('resolved_note','')}" if p.get('status') in ('hit', 'miss', 'inconclusive') else ""
            lines.append(f"- [#{p['pred_id']}][{cn.get(p['status'], p['status'])}] {p['asset']}: {p['direction'][:60]}{mark}")

    mdir = os.path.join(ROOT_DIR, 'output', 'monthly')
    mfiles = sorted(f for f in (os.listdir(mdir) if os.path.isdir(mdir) else [])
                    if f.startswith('monthly_review_') and f[15:21] in months)
    if mfiles:
        lines.append("\n## 本季月报索引(参考,结论须回溯原始数据)")
        lines.extend(f"- {f}" for f in mfiles)
    return "\n".join(lines), preview

QUARTERLY_STRUCTURE = """请按以下结构输出季度展望：

### 一、季度宏观体制演化
整季评分卡路径：体制是否实质迁移、烈度变化、关键驱动切换

### 二、各资产季度回顾与理论配置倾向检视
逐资产：用整季区间(季初→季末/极值)复盘路径与归因、评级变化及依据、
评级维持/调整建议(附触发条件;只有引擎核验已触发的条件可作为调整依据,其余标注待验证)

### 三、风险与反证审视
本季最大回撤源、相关性结构变化(如有数据)、未兑现的空头/多头叙事、当前评级体系的反证

### 四、下季度展望
基准情景+1-2个替代情景、触发器、概率排序(不强行量化)、会推翻本展望的证据清单

若数据块标注【预览】：本季尚未结束，所有结论降一档表述并写明覆盖限制。"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--quarter', help="YYYYQn,指定季度(当季未完结则按【预览】生成)")
    ap.add_argument('--dry-run', action='store_true', help='只装配数据不调用GLM')
    args = ap.parse_args()

    if args.quarter:
        q = args.quarter
    else:
        try:
            from report_generator import pending_completed_quarter
        except ImportError:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from report_generator import pending_completed_quarter
        q = pending_completed_quarter()
        if not q:
            print("非季度展望触发日(须为期间结束后第一个周五),如需强制生成请用 --quarter YYYYQn")
            return

    months = quarter_months(q)
    print("=" * 60)
    print(f"📅 季度展望生成器 ({q}: {months[0]}~{months[2]})")
    print("=" * 60)

    data_block, preview = build_data_block(q)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    data_path = os.path.join(OUTPUT_DIR, f'quarterly_data_{q}.md')
    with open(data_path, 'w', encoding='utf-8') as f:
        f.write(data_block)
    print(f"💾 季度数据块: {data_path} ({len(data_block)}字符)"
          + (" ⚠️季度未完结,预览模式" if preview else ""))

    if args.dry_run:
        print("🏃 dry-run: 跳过GLM调用")
        return

    from report_generator import load_prompt, _call_glm
    system_prompt = load_prompt('quarterly_outlook_prompt.md')
    tag = "【预览】" if preview else ""
    user_prompt = f"""请基于以下{q}的季度数据汇总，生成{tag}季度展望。

{data_block}

{QUARTERLY_STRUCTURE}"""

    print(f"🤖 调用GLM生成季报(输入约{len(system_prompt) + len(user_prompt)}字符)...")
    md = _call_glm(system_prompt, user_prompt)
    if len(md.strip()) < 500:
        print(f"❌ 返回过短({len(md)}字符),放弃")
        sys.exit(1)

    out_path = os.path.join(OUTPUT_DIR, f'quarterly_outlook_{q}.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f"<!-- {tag}季度展望 {datetime.now().strftime('%Y-%m-%d %H:%M')} | investment-agent P4v2"
                + (" | PREVIEW_PERIOD_INCOMPLETE" if preview else "") + " -->\n\n")
        f.write(md)
    print(f"✅ 季报已保存: {out_path} ({os.path.getsize(out_path)} bytes)")

if __name__ == '__main__':
    main()
