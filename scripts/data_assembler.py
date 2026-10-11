"""
数据汇总模块 v2.0
读取全球/中国/宏观三个JSON，合并为Markdown数据包供AI分析
"""

import os
import sys
import json
import glob
from datetime import datetime

PROJECT_DIR = os.path.join(os.path.dirname(__file__), '..')
DATA_DIR = os.path.join(PROJECT_DIR, 'data')

def find_latest_file(prefix):
    """找到指定前缀的最新JSON文件"""
    pattern = os.path.join(DATA_DIR, 'daily', f'{prefix}_*.json')
    files = sorted(glob.glob(pattern), reverse=True)
    if files:
        return files[0]
    return None

def load_json(filepath):
    """加载JSON"""
    if not filepath or not os.path.exists(filepath):
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def build_markdown(global_data, china_data, macro_data):
    """生成Markdown数据包"""
    lines = []
    today = datetime.now().strftime('%Y-%m-%d %H:%M')

    lines.append(f"# 投资数据包 {today}")
    lines.append("")

    # ======== 全球资产 ========
    lines.append("## 一、全球资产表现")
    lines.append("")
    lines.append("| 资产 | 代码 | 收盘 | 周变化 | MTD | YTD | 50D | 200D |")
    lines.append("|------|------|------|--------|-----|-----|-----|------|")

    if global_data and 'data' in global_data:
        for asset_id, asset in global_data['data'].items():
            name = asset_id
            ticker = asset.get('ticker', '')
            close = asset.get('close', '-')
            week = asset.get('week_chg', '-')
            mtd = asset.get('mtd_chg', '-')
            ytd = asset.get('ytd_chg', '-')
            ma50 = asset.get('vs_50d', '-')
            ma200 = asset.get('vs_200d', '-')

            week_str = f"{week:+.2f}%" if isinstance(week, (int, float)) else str(week)
            mtd_str = f"{mtd:+.2f}%" if isinstance(mtd, (int, float)) else str(mtd)
            ytd_str = f"{ytd:+.2f}%" if isinstance(ytd, (int, float)) else str(ytd)

            lines.append(f"| {name} | {ticker} | {close} | {week_str} | {mtd_str} | {ytd_str} | {ma50} | {ma200} |")

    lines.append("")

    # ======== A股/港股 ========
    lines.append("## 二、A股/港股市场")
    lines.append("")

    # A股指数
    lines.append("### A股指数")
    lines.append("| 指数 | 收盘 | 日涨跌 | 周变化 | YTD |")
    lines.append("|------|------|--------|--------|-----|")

    if china_data and 'a_share_indices' in china_data:
        for code, info in china_data['a_share_indices'].items():
            name = info.get('name', code)
            close = info.get('close', '-')
            daily = info.get('pct_chg', '-')
            week = info.get('week_chg', '-')
            ytd = info.get('ytd_chg', '-')

            daily_str = f"{daily:+.2f}%" if isinstance(daily, (int, float)) else '-'
            week_str = f"{week:+.2f}%" if isinstance(week, (int, float)) else '-'
            ytd_str = f"{ytd:+.2f}%" if isinstance(ytd, (int, float)) else '-'

            lines.append(f"| {name} | {close} | {daily_str} | {week_str} | {ytd_str} |")

    lines.append("")

    # 港股指数
    lines.append("### 港股指数")
    lines.append("| 指数 | 收盘 | 周变化 | YTD |")
    lines.append("|------|------|--------|-----|")

    if china_data and 'hk_indices' in china_data:
        for code, info in china_data['hk_indices'].items():
            name = info.get('name', code)
            close = info.get('close', '-')
            week = info.get('week_chg', '-')
            ytd = info.get('ytd_chg', '-')

            week_str = f"{week:+.2f}%" if isinstance(week, (int, float)) else '-'
            ytd_str = f"{ytd:+.2f}%" if isinstance(ytd, (int, float)) else '-'

            lines.append(f"| {name} | {close} | {week_str} | {ytd_str} |")

    lines.append("")

    # 资金与情绪指标
    lines.append("### 资金与情绪指标")
    lines.append("")

    # 南向资金
    if china_data and china_data.get('southbound'):
        sb = china_data['southbound']
        lines.append(f"- **南向资金（港股通）**: {sb.get('south_money', '-')} 百万元（{sb.get('date', '-')}）")
        if 'south_5d_total' in sb:
            lines.append(f"- **南向5日累计**: {sb['south_5d_total']} 百万元")
        lines.append(f"- **北向资金（陆股通）**: {sb.get('north_money', '-')} 百万元")
        if 'north_5d_total' in sb:
            lines.append(f"- **北向5日累计**: {sb['north_5d_total']} 百万元")

    # 融资融券
    if china_data and china_data.get('margin'):
        mg = china_data['margin']
        lines.append(f"- **融资余额**: {mg.get('rzye_billion', '-')} 亿元（{mg.get('date', '-')}）")

    # 成交额
    if china_data and china_data.get('turnover'):
        tv = china_data['turnover']
        scope = tv.get('scope', '沪深两市')
        vol = tv.get('volume_billion', 0)
        sh_vol = tv.get('sh_amount_billion', '-')
        sz_vol = tv.get('sz_amount_billion', '-')
        lines.append(f"- **{scope}成交额**: {vol} 亿元 (沪{sh_vol}+深{sz_vol})")
        if isinstance(vol, (int, float)):
            lines.append(f"- **距底部成交量条件**: {scope} {vol:.0f} 亿（参考阈值: 全A > 25000 亿）")

    # AH溢价
    if china_data and china_data.get('ah_premium'):
        ah = china_data['ah_premium']
        lines.append(f"- **AH溢价指数**: {ah.get('close', '-')}（{ah.get('signal', '-')}）")

    lines.append("")

    # 指数估值
    if china_data and china_data.get('valuation'):
        lines.append("### 指数估值")
        lines.append("| 指数 | PE_TTM | PB | 换手率 |")
        lines.append("|------|--------|-----|--------|")
        for code, info in china_data['valuation'].items():
            name = info.get('name', code)
            pe = info.get('pe_ttm', '-')
            pb = info.get('pb', '-')
            tr = info.get('turnover_rate', '-')
            lines.append(f"| {name} | {pe} | {pb} | {tr}% |")
        lines.append("")

    # ======== 宏观与信用 ========
    lines.append("## 三、宏观与信用数据")
    lines.append("")

    if macro_data and 'data' in macro_data:
        md = macro_data['data']

        # 信用利差
        lines.append("### 信用利差")
        lines.append("| 指标 | 值(%) | 周变化 | 状态 |")
        lines.append("|------|-------|--------|------|")

        credit_keys = ['HY_OAS', 'BB_OAS', 'B_OAS', 'CCC_OAS', 'IG_OAS']
        for key in credit_keys:
            if key in md:
                item = md[key]
                val = item.get('value', 0)
                chg = item.get('week_chg', 0)
                chg_str = f"{chg:+.2f}" if isinstance(chg, (int, float)) else str(chg)
                lines.append(f"| {key} | {val} | {chg_str} | - |")

        lines.append("")

        # 美债收益率
        lines.append("### 美债收益率")
        lines.append("| 期限 | 值(%) | 周变化 |")
        lines.append("|------|-------|--------|")

        rate_keys = ['UST_2Y', 'UST_10Y', 'UST_30Y']
        for key in rate_keys:
            if key in md:
                item = md[key]
                val = item.get('value', 0)
                chg = item.get('week_chg', 0)
                chg_str = f"{chg:+.2f}" if isinstance(chg, (int, float)) else str(chg)
                lines.append(f"| {key} | {val} | {chg_str} |")

        lines.append("")

        # 通胀与实际利率
        lines.append("### 通胀预期与实际利率")
        lines.append("| 指标 | 值 | 周变化 |")
        lines.append("|------|-----|--------|")

        inflation_keys = ['BEI_5Y', 'BEI_10Y', 'CURVE_2S10S']
        for key in inflation_keys:
            if key in md:
                item = md[key]
                val = item.get('value', 0)
                chg = item.get('week_chg', 0)
                chg_str = f"{chg:+.2f}" if isinstance(chg, (int, float)) else str(chg)
                lines.append(f"| {key} | {val} | {chg_str} |")

        # 衍生指标
        if 'derived' in macro_data:
            derived = macro_data['derived']
            if 'REAL_10Y' in derived:
                lines.append(f"| REAL_10Y | {derived['REAL_10Y']}% | - |")
            if 'REAL_SHORT' in derived:
                lines.append(f"| REAL_SHORT | {derived['REAL_SHORT']}% | - |")
            if 'HY_IG_DIFF' in derived:
                lines.append(f"| HY_IG_DIFF | {derived['HY_IG_DIFF']}% | - |")

        lines.append("")

        # 阈值警报
        if 'alerts' in macro_data and macro_data['alerts']:
            lines.append("### ⚠️ 阈值警报")
            for alert in macro_data['alerts']:
                lines.append(f"- {alert}")
            lines.append("")

    # ======== 关键阈值距离 ========
    lines.append("## 四、关键阈值距离")
    lines.append("")

    # 从数据中提取关键变量计算距离
    thresholds = []

    if macro_data and 'data' in macro_data:
        md = macro_data['data']

        if 'HY_OAS' in md:
            hy = md['HY_OAS'].get('value', 0)
            if isinstance(hy, (int, float)):
                dist = round(4.0 - hy, 2)
                thresholds.append(f"- HY OAS → 400bp 卖出阈值: 当前 {hy}%，距离 {dist}%")

        if 'CCC_OAS' in md:
            ccc = md['CCC_OAS'].get('value', 0)
            if isinstance(ccc, (int, float)):
                dist = round(10.0 - ccc, 2)
                thresholds.append(f"- CCC OAS → 1000bp 恐慌线: 当前 {ccc}%，距离 {dist}%")

        if 'UST_30Y' in md:
            y30 = md['UST_30Y'].get('value', 0)
            if isinstance(y30, (int, float)):
                dist = round(5.0 - y30, 2)
                thresholds.append(f"- 30Y 收益率 → 5.0% 红线: 当前 {y30}%，距离 {dist}%")

    if global_data and 'data' in global_data:
        for asset_id, asset in global_data['data'].items():
            if asset_id == 'VIX':
                vix = asset.get('close', 0)
                if isinstance(vix, (int, float)):
                    thresholds.append(f"- VIX 当前 {vix}（>25 恐慌，>30 极度恐慌）")
            if asset_id == 'DXY':
                dxy = asset.get('close', 0)
                if isinstance(dxy, (int, float)):
                    thresholds.append(f"- DXY 当前 {dxy}（<100 弱势，>105 强势）")

    for t in thresholds:
        lines.append(t)

    lines.append("")

    # ======== 跨资产相关性 ========
    lines.append("## 五、跨资产相关性 (20日滚动)")
    lines.append("")

    # 读取相关性数据
    correlation_file = None
    correlation_dir = os.path.join(DATA_DIR, 'daily')
    if os.path.exists(correlation_dir):
        corr_files = sorted([f for f in os.listdir(correlation_dir) if f.startswith('correlation_') and f.endswith('.md')])
        if corr_files:
            correlation_file = os.path.join(correlation_dir, corr_files[-1])

    if correlation_file and os.path.exists(correlation_file):
        with open(correlation_file, 'r', encoding='utf-8') as f:
            corr_content = f.read()
        # 只取表格部分，去掉标题行（避免重复）
        corr_lines = corr_content.split('\n')
        # 跳过前3行（标题和日期）和空行
        start_idx = 0
        for i, line in enumerate(corr_lines):
            if line.startswith('| 资产对'):
                start_idx = i
                break
        if start_idx > 0:
            # 从表格开始添加，跳过"关键发现"部分
            for line in corr_lines[start_idx:]:
                if line.startswith('### 关键发现'):
                    break
                lines.append(line)
            lines.append("")
        print(f"  ✅ 相关性数据已整合: {os.path.basename(correlation_file)}")
    else:
        print("  ⚠️ 未找到相关性数据文件，跳过")

    lines.append("")

    # ======== 利率预期与实体经济 ========
    # 读取利率预期与实体经济数据
    rate_file = None
    if os.path.exists(os.path.join(DATA_DIR, 'daily')):
        rate_files = sorted([f for f in os.listdir(os.path.join(DATA_DIR, 'daily'))
                             if f.startswith('rate_economy_') and f.endswith('.md')])
        if rate_files:
            rate_file = os.path.join(DATA_DIR, 'daily', rate_files[-1])

    if rate_file and os.path.exists(rate_file):
        with open(rate_file, 'r', encoding='utf-8') as f:
            rate_content = f.read()
        # 只取内容部分，去掉标题行
        rate_lines = rate_content.split('\n')
        # 跳过第一行标题
        start_idx = 0
        for i, line in enumerate(rate_lines):
            if line.startswith('##'):
                start_idx = i
                break
        if start_idx > 0:
            # 从内容开始添加
            for line in rate_lines[start_idx:]:
                lines.append(line)
            lines.append("")
        print(f"  ✅ 利率预期数据已整合: {os.path.basename(rate_file)}")
    else:
        print("  ⚠️ 未找到利率预期数据文件，跳过")

    # ======== 宏观体制评分卡 ========
    # 读取宏观评分卡
    scorecard_file = None
    if os.path.exists(os.path.join(DATA_DIR, 'daily')):
        sc_files = sorted([f for f in os.listdir(os.path.join(DATA_DIR, 'daily'))
                           if f.startswith('scorecard_') and f.endswith('.md')])
        if sc_files:
            scorecard_file = os.path.join(DATA_DIR, 'daily', sc_files[-1])

    if scorecard_file and os.path.exists(scorecard_file):
        with open(scorecard_file, 'r', encoding='utf-8') as f:
            sc_content = f.read()
        lines.append("\n\n## 宏观体制评分卡\n\n")
        lines.append(sc_content)
        print(f"  ✅ 宏观评分卡已整合: {os.path.basename(scorecard_file)}")
    else:
        print("  ⚠️ 未找到宏观评分卡文件，跳过")

    lines.append("")
    lines.append("---")
    lines.append(f"*数据包生成时间: {today}*")

    return '\n'.join(lines)

# ============ 主程序 ============
if __name__ == '__main__':
    print("=" * 60)
    print("📦 数据汇总打包 v2.0")
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 找最新文件
    global_file = find_latest_file('global')
    china_file = find_latest_file('china')
    macro_file = find_latest_file('macro')

    print(f"\n📂 数据文件:")
    print(f"  全球: {global_file or '未找到'}")
    print(f"  中国: {china_file or '未找到'}")
    print(f"  宏观: {macro_file or '未找到'}")

    # 加载
    global_data = load_json(global_file)
    china_data = load_json(china_file)
    macro_data = load_json(macro_file)

    # 生成
    md = build_markdown(global_data, china_data, macro_data)

    # 保存
    date_str = datetime.now().strftime('%Y%m%d')
    weekly_dir = os.path.join(DATA_DIR, 'weekly')
    os.makedirs(weekly_dir, exist_ok=True)

    filepath = os.path.join(weekly_dir, f'data_pack_{date_str}.md')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(md)

    size = os.path.getsize(filepath)
    print(f"\n✅ 数据包已生成: {filepath}")
    print(f"   大小: {size} 字节")

    # 预览
    print("\n" + "=" * 60)
    print("📖 预览:")
    print("=" * 60)
    preview_lines = md.split('\n')[:40]
    for line in preview_lines:
        print(line)
    if len(md.split('\n')) > 40:
        print(f"\n... 共 {len(md.split(chr(10)))} 行")

    print("\n🎉 汇总完成！")
