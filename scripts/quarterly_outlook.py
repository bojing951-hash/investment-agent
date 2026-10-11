#!/usr/bin/env python3
"""季度展望生成器 v1.0 (P4, 2026-10-11)

触发: report_generator在季末月(3/6/9/12)最后一个周五生成周报后以子进程启动。
数据口径: 整季三个月 — 每月评分卡(体制/总分)、各月末关键资产水平、
论点状态轨迹、配置观点评级轨迹、已有月报索引。
纪律: 战略层视角,不拼接月报(提示词见 config/prompts/quarterly_outlook_prompt.md)。
用法: python3 quarterly_outlook.py [--dry-run]
"""
import os
import sys
import re
import json
import glob
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, 'data', 'daily')
OUTPUT_DIR = os.path.join(ROOT_DIR, 'output', 'quarterly')

def quarter_months(now=None):
    """返回本季度三个月的YYYYMM列表,如 ['202607','202608','202609']"""
    now = now or datetime.now()
    q_start = ((now.month - 1) // 3) * 3 + 1
    return [f"{now.year}{m:02d}" for m in range(q_start, q_start + 3)]

def month_end_levels(ym):
    """取该月最后一个global文件的关键收盘水平"""
    from data_validator import flatten_json
    levels = {}
    files = sorted(glob.glob(os.path.join(DATA_DIR, f'global_{ym}*.json')))
    if not files:
        return levels
    flat = flatten_json(json.load(open(files[-1])))
    for label, key_re in (('SPX', r'^data\.SPX\.close$'), ('黄金', r'^data\.GOLD\.close$'),
                          ('DXY', r'^data\.DXY\.close$'), ('WTI', r'^data\.WTI\.close$|^data\.CL.*close$'),
                          ('BTC', r'^data\.BTC\.close$'), ('VIX', r'^data\.VIX\.close$')):
        for k, v in flat.items():
            if isinstance(v, (int, float)) and re.search(key_re, k):
                levels[label] = v
                break
    levels['_as_of'] = os.path.basename(files[-1])
    return levels

def scorecard_of_month(ym):
    """该月最后一份评分卡(月末体制快照)"""
    files = sorted(glob.glob(os.path.join(DATA_DIR, f'scorecard_{ym}*.json')))
    if not files:
        return None
    try:
        return json.load(open(files[-1]))
    except Exception:
        return None

def build_data_block():
    months = quarter_months()
    lines = [f"# {months[0][:4]}年Q{(int(months[0][4:6]) - 1) // 3 + 1} 季度数据汇总(自动提取)\n"]
    lines.append("## 各月体制快照(取每月最后一份评分卡)\n")
    for ym in months:
        sc = scorecard_of_month(ym)
        if sc:
            lines.append(f"- {ym}: 计算={sc.get('regime')}, 确认={sc.get('confirmed_regime')}({sc.get('regime_status')}), "
                         f"增长{sc.get('growth_total', 0):+d}/通胀{sc.get('inflation_total', 0):+d}")
        else:
            lines.append(f"- {ym}: (无评分卡)")
    lines.append("\n## 各月末关键资产水平(每月最后一个采集日)\n")
    lines.append("| 月份 | SPX | 黄金 | DXY | WTI | BTC | VIX | 数据日 |")
    lines.append("|------|-----|------|-----|-----|-----|-----|--------|")
    for ym in months:
        lv = month_end_levels(ym)
        if lv:
            lines.append(f"| {ym} | {lv.get('SPX','-')} | {lv.get('黄金','-')} | {lv.get('DXY','-')} | "
                         f"{lv.get('WTI','-')} | {lv.get('BTC','-')} | {lv.get('VIX','-')} | {lv.get('_as_of','?')} |")
        else:
            lines.append(f"| {ym} | - | - | - | - | - | - | 无数据 |")

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

    # 配置观点评级轨迹
    import allocation_engine
    views = allocation_engine.load_views()
    if views:
        lines.append("\n## 配置观点评级轨迹(allocation_views.json history)")
        for v in views.get('views', []):
            hist = v.get('history', [])
            if hist:
                lines.append(f"- {v['asset']}: {'; '.join(hist[-4:])}")
        preds = views.get('predictions', [])
        if preds:
            lines.append("\n## 预测命中统计")
            hits = sum(1 for p in preds if p.get('status') == 'hit')
            misses = sum(1 for p in preds if p.get('status') == 'miss')
            opens = sum(1 for p in preds if p.get('status') == 'open')
            lines.append(f"- 命中{hits} / 证伪{misses} / 未到期{opens}")
            lines.extend(f"- [#{p['pred_id']}][{p['status']}] {p['asset']}: {p['direction'][:60]}" for p in preds)

    # 已有月报索引
    mdir = os.path.join(ROOT_DIR, 'output', 'monthly')
    mfiles = sorted(f for f in (os.listdir(mdir) if os.path.isdir(mdir) else [])
                    if f.startswith('monthly_review_') and f[15:21] in months)
    if mfiles:
        lines.append("\n## 本季月报索引(参考,结论须回溯原始数据)")
        lines.extend(f"- {f}" for f in mfiles)
    return "\n".join(lines)

QUARTERLY_STRUCTURE = """请按以下结构输出季度展望：

### 一、季度宏观体制演化
整季评分卡路径：体制是否实质迁移、烈度变化、关键驱动切换

### 二、各资产季度回顾与战略配置检视
逐资产：季度水平变化路径、评级变化及依据、评级维持/调整建议(附触发条件)

### 三、风险预算与投资政策审视
本季最大回撤源、集中度、相关性结构变化；政策修订建议或明确"维持"

### 四、下季度展望
基准情景+1-2个替代情景、触发器、概率排序、会推翻本展望的证据清单"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true', help='只装配数据不调用GLM')
    args = ap.parse_args()

    months = quarter_months()
    q = f"{months[0][:4]}Q{(int(months[0][4:6]) - 1) // 3 + 1}"
    print("=" * 60)
    print(f"📅 季度展望生成器 ({q}: {months[0]}~{months[2]})")
    print("=" * 60)

    data_block = build_data_block()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    data_path = os.path.join(OUTPUT_DIR, f'quarterly_data_{q}.md')
    with open(data_path, 'w', encoding='utf-8') as f:
        f.write(data_block)
    print(f"💾 季度数据块: {data_path} ({len(data_block)}字符)")

    if args.dry_run:
        print("🏃 dry-run: 跳过GLM调用")
        return

    from report_generator import load_prompt, _call_glm
    system_prompt = load_prompt('quarterly_outlook_prompt.md')
    user_prompt = f"""请基于以下{q}的季度数据汇总，生成季度展望。

{data_block}

{QUARTERLY_STRUCTURE}"""

    print(f"🤖 调用GLM生成季报(输入约{len(system_prompt) + len(user_prompt)}字符)...")
    md = _call_glm(system_prompt, user_prompt)
    if len(md.strip()) < 500:
        print(f"❌ 返回过短({len(md)}字符),放弃")
        sys.exit(1)

    out_path = os.path.join(OUTPUT_DIR, f'quarterly_outlook_{q}.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f"<!-- 季度展望 {datetime.now().strftime('%Y-%m-%d %H:%M')} | investment-agent P4 -->\n\n")
        f.write(md)
    print(f"✅ 季报已保存: {out_path} ({os.path.getsize(out_path)} bytes)")

if __name__ == '__main__':
    main()
