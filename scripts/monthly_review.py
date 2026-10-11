#!/usr/bin/env python3
"""月度复盘生成器 v1.0 (P4, 2026-10-11)

触发: report_generator在月末最后一个周五生成周报后以子进程启动。
数据口径: 整月原始时序 — 逐日扫描 data/daily/*.json 提取关键序列的
月初/月末/最高/最低,外加论点history、预测状态、本月各期周报摘要。
纪律: 月报不拼接周报结论,回溯原始序列(提示词见 config/prompts/monthly_review_prompt.md)。
用法: python3 monthly_review.py [--dry-run]
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
OUTPUT_DIR = os.path.join(ROOT_DIR, 'output', 'monthly')

# 关键序列: (标签, 文件模式, 键正则) — 数值取.value/.close
KEY_SERIES = [
    ('SPX标普500',    'global_*.json',       r'^data\.SPX\.close$'),
    ('NDX纳斯达克',   'global_*.json',       r'^data\.NDX\.close$'),
    ('黄金',          'global_*.json',       r'^data\.GOLD\.close$'),
    ('美元指数DXY',   'global_*.json',       r'^data\.DXY\.close$'),
    ('VIX',           'global_*.json',       r'^data\.VIX\.close$'),
    ('BTC',           'global_*.json',       r'^data\.BTC\.close$'),
    ('WTI原油',       'global_*.json',       r'^data\.WTI\.close$|^data\.CL.*close$'),
    ('上证指数',      'china_*.json',        r'000001\.SH\.(close|收盘)$'),
    ('HY_OAS高收益利差', 'macro_*.json',     r'^data\.HY_OAS\.value$'),
    ('CCC_OAS利差',   'macro_*.json',        r'^data\.CCC_OAS\.value$'),
    ('UST_10Y',       'macro_*.json',        r'^data\.UST_10Y\.value$|^data\.GS10\.value$'),
    ('UST_30Y',       'macro_*.json',        r'^data\.UST_30Y\.value$|^data\.GS30\.value$'),
]

def gather_month_series(ym):
    """扫描整月daily文件,提取各序列 (月初,月末,最高,最低,样本数)"""
    from data_validator import flatten_json
    series = {label: {'values': [], 'dates': []} for label, _, _ in KEY_SERIES}
    patterns = {p for _, p, _ in KEY_SERIES}
    files_by_pattern = {p: sorted(glob.glob(os.path.join(DATA_DIR, p.replace('*', ym + '*'))))
                        for p in patterns}
    for label, pat, key_re in KEY_SERIES:
        for fp in files_by_pattern[pat]:
            try:
                flat = flatten_json(json.load(open(fp)))
            except Exception:
                continue
            for k, v in flat.items():
                if isinstance(v, (int, float)) and re.search(key_re, k):
                    series[label]['values'].append(v)
                    m = re.search(r'(\d{8})', os.path.basename(fp))
                    series[label]['dates'].append(m.group(1) if m else '?')
                    break  # 每文件取一次
    out = {}
    for label, s in series.items():
        vals = s['values']
        if len(vals) >= 2:
            out[label] = {
                'first': vals[0], 'last': vals[-1],
                'min': min(vals), 'max': max(vals),
                'chg_pct': round((vals[-1] - vals[0]) / abs(vals[0]) * 100, 2) if vals[0] else None,
                'coverage': f"{s['dates'][0]}→{s['dates'][-1]} ({len(vals)}个观测)",
            }
    return out

def gather_month_context(ym):
    """论点history、预测状态、本月周报摘要、评分卡时间线"""
    ctx = {}

    # 论点history(本月条目,如"10/11 ...")
    tp = os.path.join(ROOT_DIR, 'config', 'thesis.json')
    if os.path.exists(tp):
        d = json.load(open(tp))
        month_num = int(ym[4:6])
        lines = []
        for t in d.get('theses', []):
            for h in t.get('history', []):
                if h.startswith(f"{month_num}/"):
                    lines.append(f"#{t['id']}{t.get('name','')}: {h}")
        ctx['thesis_moves'] = lines or ['(本月无论点状态记录)']

    # 预测状态
    import allocation_engine
    views = allocation_engine.load_views()
    if views:
        ctx['predictions'] = [f"[#{p['pred_id']}][{p['status']}] {p['asset']}: {p['direction']}"
                              + (f" → 裁决:{p.get('resolved_note','')}" if p.get('status') in ('hit', 'miss', 'expired') else '')
                              for p in views.get('predictions', [])] or ['(无预测记录)']

    # 本月各期周报摘要(标题+一、本周摘要首150字)
    wk_dir = os.path.join(ROOT_DIR, 'output', 'weekly')
    wk_files = sorted(f for f in os.listdir(wk_dir) if f.startswith(f'weekly_report_{ym}') and not f.endswith('_annotated.md')) if os.path.isdir(wk_dir) else []
    wk_lines = []
    for wf in wk_files:
        text = open(os.path.join(wk_dir, wf), encoding='utf-8').read()
        m = re.search(r'###?\s*一、本周摘要[^\n]*\n(.{0,150})', text, re.DOTALL)
        wk_lines.append(f"- {wf[13:21]}: {(m.group(1).strip().replace(chr(10),' ') if m else '(未找到摘要节)')[:150]}")
    ctx['weekly_reports'] = wk_lines or ['(本月无周报)']

    # 评分卡体制时间线(整月每周取一份: 逢周五或最后一日)
    sc_files = sorted(glob.glob(os.path.join(DATA_DIR, f'scorecard_{ym}*.json')))
    tl = []
    seen_weeks = set()
    for fp in sc_files:
        try:
            d = json.load(open(fp))
        except Exception:
            continue
        import datetime as _dt
        dd = _dt.date(int(ym[:4]), int(ym[4:6]), int(os.path.basename(fp)[-13:-5][6:8]))
        wk = dd.isocalendar()[1]
        if wk in seen_weeks:
            continue
        seen_weeks.add(wk)
        tl.append(f"{d.get('date')}: 计算={d.get('regime')}, 确认={d.get('confirmed_regime')}({d.get('regime_status')}), "
                  f"增长{d.get('growth_total', 0):+d}/通胀{d.get('inflation_total', 0):+d}")
    ctx['scorecard_timeline'] = tl or ['(本月无评分卡)']
    return ctx

def build_data_block(ym):
    series = gather_month_series(ym)
    ctx = gather_month_context(ym)
    lines = [f"# {ym[:4]}年{int(ym[4:6])}月 月度原始数据汇总(自动提取自daily JSON,非周报拼接)\n"]
    lines.append("## 关键资产月度区间(月初→月末,含最高/最低与覆盖区间)\n")
    lines.append("| 序列 | 月初 | 月末 | 最低 | 最高 | 月变化% | 覆盖 |")
    lines.append("|------|------|------|------|------|---------|------|")
    for label, s in series.items():
        lines.append(f"| {label} | {s['first']:.2f} | {s['last']:.2f} | {s['min']:.2f} | {s['max']:.2f} | "
                     f"{s['chg_pct']:+.2f}% | {s['coverage']} |")
    lines.append("\n## 本月体制评分卡时间线(每周一份)")
    lines.extend(f"- {t}" for t in ctx['scorecard_timeline'])
    lines.append("\n## 本月论点状态变更(thesis.json history)")
    lines.extend(f"- {t}" for t in ctx['thesis_moves'])
    lines.append("\n## 预测状态(allocation_views.json)")
    lines.extend(f"- {p}" for p in ctx['predictions'])
    lines.append("\n## 本月各期周报摘要(仅作索引,结论须回溯上方原始数据)")
    lines.extend(ctx['weekly_reports'])
    return "\n".join(lines), series, ctx

MONTHLY_STRUCTURE = """请按以下结构输出月度复盘：

### 一、本月宏观体制演化
基于评分卡时间线：体制是否迁移、各维度分数的月内路径、关键驱动指标

### 二、本月证据累积与论点状态复盘
逐个有变动的论点：触发了什么条件、星级路径、反证是否被兑现

### 三、各资产月度表现与归因
用上方月度区间表做归因（β还是α、驱动因子、月内拐点），不逐日复述

### 四、预测裁决与战术再平衡必要性
逐条预测给出命中/证伪/未到期裁决与依据；再平衡只在触发条件被跨越时建议，否则明确"维持"

### 五、下月监控重点
3-5个带具体阈值的前瞻监控点（体制切换/论点触发/预测到期日）"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true', help='只装配数据不调用GLM')
    args = ap.parse_args()

    ym = datetime.now().strftime('%Y%m')
    print("=" * 60)
    print(f"📅 月度复盘生成器 ({ym})")
    print("=" * 60)

    data_block, series, ctx = build_data_block(ym)
    print(f"✅ 数据装配: {len(series)}个序列 / {len(ctx['scorecard_timeline'])}周评分卡 / {len(ctx['weekly_reports'])}期周报")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    data_path = os.path.join(OUTPUT_DIR, f'monthly_data_{ym}.md')
    with open(data_path, 'w', encoding='utf-8') as f:
        f.write(data_block)
    print(f"💾 月度数据块: {data_path}")

    if args.dry_run:
        print("🏃 dry-run: 跳过GLM调用")
        return

    from report_generator import load_prompt, _call_glm
    system_prompt = load_prompt('monthly_review_prompt.md')
    user_prompt = f"""请基于以下{ym[:4]}年{int(ym[4:6])}月的原始数据汇总，生成月度复盘。

注: 本月最后几日的数据若缺失，属正常(月报在月末最后一个周五生成)，覆盖区间以各序列标注为准。

{data_block}

{MONTHLY_STRUCTURE}"""

    print(f"🤖 调用GLM生成月报(输入约{len(system_prompt) + len(user_prompt)}字符)...")
    md = _call_glm(system_prompt, user_prompt)
    if len(md.strip()) < 500:
        print(f"❌ 返回过短({len(md)}字符),放弃")
        sys.exit(1)

    out_path = os.path.join(OUTPUT_DIR, f'monthly_review_{ym}.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f"<!-- 月度复盘 {datetime.now().strftime('%Y-%m-%d %H:%M')} | investment-agent P4 -->\n\n")
        f.write(md)
    print(f"✅ 月报已保存: {out_path} ({os.path.getsize(out_path)} bytes)")

if __name__ == '__main__':
    main()
