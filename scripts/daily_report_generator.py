"""
每日投资简报生成器
轻量版：市场快照 + 阈值变化 + 新闻要点 + 论点快检
"""

import os
import sys
import json
import glob
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from env_config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

from openai import OpenAI

# ============ 路径配置 ============
PROJECT_DIR = os.path.join(os.path.dirname(__file__), '..')
DATA_DIR = os.path.join(PROJECT_DIR, 'data')
CONFIG_DIR = os.path.join(PROJECT_DIR, 'config')
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'output', 'daily')

def find_latest(directory, prefix):
    """找最新文件（仅JSON）"""
    pattern = os.path.join(directory, f'{prefix}_*.json')
    files = sorted(glob.glob(pattern), reverse=True)
    return files[0] if files else None

def load_json(filepath):
    if not filepath or not os.path.exists(filepath):
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_text(filepath):
    if not filepath or not os.path.exists(filepath):
        return ""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def build_daily_snapshot():
    """构建当日数据快照"""
    lines = []

    # 全球数据
    global_file = find_latest(os.path.join(DATA_DIR, 'daily'), 'global')
    global_data = load_json(global_file)

    if global_data and 'data' in global_data:
        lines.append("### 全球市场")
        lines.append("| 资产 | 收盘 | 周变化 | 信号 |")
        lines.append("|------|------|--------|------|")
        for symbol, a in global_data['data'].items():
            name = a.get('name', symbol)
            close = a.get('close', '-')
            week = a.get('week_chg', '-')
            ma50 = a.get('ma50_signal', '')
            week_str = f"{week:+.2f}%" if isinstance(week, (int, float)) else '-'
            lines.append(f"| {name} | {close} | {week_str} | {ma50} |")
        lines.append("")

    # 中国数据
    china_file = find_latest(os.path.join(DATA_DIR, 'daily'), 'china')
    china_data = load_json(china_file)

    if china_data:
        lines.append("### A股/港股")
        if 'a_share_indices' in china_data:
            for code, info in china_data['a_share_indices'].items():
                name = info.get('name', '')
                close = info.get('close', '-')
                pct = info.get('pct_chg', 0)
                pct_str = f"{pct:+.2f}%" if isinstance(pct, (int, float)) else '-'
                lines.append(f"- {name}: {close} ({pct_str})")

        if 'hk_indices' in china_data:
            for code, info in china_data['hk_indices'].items():
                name = info.get('name', '')
                close = info.get('close', '-')
                lines.append(f"- {name}: {close}")

        if china_data.get('southbound'):
            sb = china_data['southbound']
            lines.append(f"- 南向资金: {sb.get('south_money', '-')} 百万")

        if china_data.get('margin'):
            mg = china_data['margin']
            lines.append(f"- 融资余额: {mg.get('rzye_billion', '-')} 亿元")

        lines.append("")

    # 宏观数据
    macro_file = find_latest(os.path.join(DATA_DIR, 'daily'), 'macro')
    macro_data = load_json(macro_file)

    if macro_data:
        lines.append("### 关键宏观指标")

        key_metrics = [
            ('HY_OAS', '高收益利差'),
            ('CCC_OAS', 'CCC利差'),
            ('IG_OAS', '投资级利差'),
            ('UST_2Y', '2Y国债'),
            ('UST_10Y', '10Y国债'),
            ('UST_30Y', '30Y国债'),
            ('BEI_5Y', '5Y通胀预期'),
            ('BEI_10Y', '10Y通胀预期'),
        ]

        for key, label in key_metrics:
            if key in macro_data:
                item = macro_data[key]
                val = item.get('value', '-')
                chg = item.get('week_chg', '-')
                chg_str = f"({chg:+.2f})" if isinstance(chg, (int, float)) else ''
                lines.append(f"- {label}: {val}% {chg_str}")

        # 衍生指标
        for key in ['REAL_10Y', 'REAL_SHORT', 'HY_IG_DIFF', 'SPREAD_2S10S']:
            if key in macro_data:
                item = macro_data[key]
                val = item.get('value', '-')
                lines.append(f"- {key}: {val}%")

        # 阈值警报
        if macro_data.get('alerts'):
            lines.append("")
            lines.append("### ⚠️ 阈值警报")
            for alert in macro_data['alerts']:
                lines.append(f"- {alert}")

        lines.append("")

    # 阈值距离
    lines.append("### 关键阈值距离")
    if macro_data:
        if 'HY_OAS' in macro_data:
            hy = macro_data['HY_OAS'].get('value', 0)
            if isinstance(hy, (int, float)):
                lines.append(f"- HY OAS → 400bp: 当前 {hy}%，距离 {round(4.0-hy, 2)}%")
        if 'CCC_OAS' in macro_data:
            ccc = macro_data['CCC_OAS'].get('value', 0)
            if isinstance(ccc, (int, float)):
                lines.append(f"- CCC OAS → 1000bp: 当前 {ccc}%，距离 {round(10.0-ccc, 2)}%")
        if 'UST_30Y' in macro_data:
            y30 = macro_data['UST_30Y'].get('value', 0)
            if isinstance(y30, (int, float)):
                lines.append(f"- 30Y → 5.0%红线: 当前 {y30}%，距离 {round(5.0-y30, 2)}%")

    if global_data and 'data' in global_data:
        for symbol, a in global_data['data'].items():
            if symbol == 'VIX':
                vix = a.get('close', 0)
                if isinstance(vix, (int, float)):
                    zone = '极度恐慌' if vix > 30 else '恐慌' if vix > 25 else '紧张' if vix > 20 else '正常'
                    lines.append(f"- VIX: {vix}（{zone}）")
            if symbol == 'DXY':
                dxy = a.get('close', 0)
                if isinstance(dxy, (int, float)):
                    zone = '强势' if dxy > 105 else '中性' if dxy > 100 else '弱势'
                    lines.append(f"- DXY: {dxy}（{zone}）")

    lines.append("")
    return '\n'.join(lines)

def load_news_brief():
    """加载新闻摘要"""
    news_dir = os.path.join(DATA_DIR, 'news')
    filepath = find_latest(news_dir, 'news_summary') if os.path.exists(news_dir) else None
    if filepath:
        content = load_text(filepath)
        # 只取前50行
        short = '\n'.join(content.split('\n')[:50])
        return short
    return ""

def load_theses_brief():
    """加载论点简表"""
    thesis_path = os.path.join(CONFIG_DIR, 'thesis.json')
    if not os.path.exists(thesis_path):
        return ""

    with open(thesis_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    lines = ["### 论点状态快检"]
    for t in data.get('theses', []):
        stars = "★" * t.get('confidence', 0) + "☆" * (5 - t.get('confidence', 0))
        lines.append(f"- #{t['id']} {t['title']} | {t['status']} | {stars}")

    return '\n'.join(lines)

def generate_daily_report(snapshot, news, theses):
    """调用DeepSeek生成日报"""

    today_str = datetime.now().strftime('%Y-%m-%d')

    prompt = f"""请基于以下数据生成一份简洁的每日投资简报（{today_str}）。

要求：
- 总长度控制在800字以内
- 用中文
- 结构如下：

### 一、今日一句话（用一句话概括今天市场最核心的变化）

### 二、市场快照要点（3-5个最值得关注的数据变化）

### 三、阈值监控（哪些指标接近关键阈值，距离多远）

### 四、新闻要点（1-3条最重要的新闻及其市场含义）

### 五、论点快检（每个论点用一句话说明今天的数据是支持还是削弱）

### 六、明日关注（1-2个明天需要关注的事件或数据）

注意：简洁、精准、数据驱动。不需要长篇分析。

---

## 市场数据
{snapshot}

## 新闻摘要
{news if news else '无新闻数据'}

## 论点状态
{theses if theses else '无论点数据'}
"""

    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

    try:
        response = client.responses.create(
            model=DEEPSEEK_MODEL,
            input=[
                {"role": "system", "content": "你是投资研究助手，负责生成简洁的每日市场简报。风格：精准、数据驱动、不废话。"},
                {"role": "user", "content": prompt}
            ]
        )
        return response.output[0].content[0].text
    except Exception as e:
        print(f"  ❌ responses.create 失败: {e}")
        try:
            response = client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=[
                    {"role": "system", "content": "你是投资研究助手，生成简洁的每日市场简报。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e2:
            print(f"  ❌ 备用接口也失败: {e2}")
            return None

def save_daily_report(report_text):
    """保存日报"""
    date_str = datetime.now().strftime('%Y%m%d')
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    filepath = os.path.join(OUTPUT_DIR, f'daily_{date_str}.md')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# 每日投资简报 {date_str}\n\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        f.write(report_text)

    print(f"📄 日报已保存: {filepath} ({os.path.getsize(filepath)} 字节)")
    return filepath

# ============ 主程序 ============
if __name__ == '__main__':
    print("=" * 60)
    print("📋 每日投资简报生成器")
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 1. 构建数据快照
    print("\n📊 构建市场快照...")
    snapshot = build_daily_snapshot()
    print(f"  快照: {len(snapshot)} 字符")

    # 2. 加载新闻
    print("\n📰 加载新闻摘要...")
    news = load_news_brief()
    print(f"  新闻: {len(news)} 字符" if news else "  无新闻")

    # 3. 加载论点
    print("\n📌 加载论点...")
    theses = load_theses_brief()
    print(f"  论点: {len(theses)} 字符" if theses else "  无论点")

    # 4. 生成日报
    print("\n🤖 生成日报...")
    report = generate_daily_report(snapshot, news, theses)

    if report:
        save_daily_report(report)

        # 预览
        print("\n" + "=" * 60)
        print("📖 日报预览:")
        print("=" * 60)
        print(report)
        print("\n🎉 日报生成完成！")
    else:
        print("\n❌ 日报生成失败")
