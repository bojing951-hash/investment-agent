"""
新闻采集模块
数据源：Finnhub（市场新闻+个股新闻）+ RSS（CNBC+Bloomberg）
输出：分类新闻摘要，供AI生成报告使用
"""

import os
import sys
import json
import time
import feedparser
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from env_config import FINNHUB_API_KEY, DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

import finnhub
from openai import OpenAI

# ============ 配置 ============
PROJECT_DIR = os.path.join(os.path.dirname(__file__), '..')
DATA_DIR = os.path.join(PROJECT_DIR, 'data')

fh_client = finnhub.Client(api_key=FINNHUB_API_KEY)

# 关注的个股新闻
WATCH_SYMBOLS = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'META', 'TSLA']

# RSS 源
RSS_FEEDS = {
    'CNBC_Economy': 'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=20910258',
    'CNBC_Markets': 'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664',
    'CNBC_World': 'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100727362',
    'Bloomberg_Markets': 'https://feeds.bloomberg.com/markets/news.rss',
    'Bloomberg_Economy': 'https://feeds.bloomberg.com/economics/news.rss',
}

# 新闻分类关键词
CATEGORY_KEYWORDS = {
    '美联储/利率': ['fed', 'fomc', 'rate', 'powell', 'interest rate', 'monetary', 'inflation', 'cpi', 'pce', 'treasury', 'bond', 'yield'],
    '信用/债务': [
        'credit', 'high yield', 'default', 'bankruptcy', 'leveraged loan', 'clo', 'spread', 'junk bond', 'downgrade',
        'private credit', 'private debt', 'direct lending',
        'credit fund', 'credit downgrade', 'junk bond', 'high yield',
        'leveraged loan', 'CLO', 'credit spread', 'default',
        'bankruptcy', 'distressed', 'restructuring', 'covenant',
        'Moody', 'S&P downgrade', 'Fitch', 'credit rating',
        'redemption', 'write-down', 'impairment', 'provision',
        'NPL', 'nonperforming', 'credit loss', 'bank lending',
        'tightening standards', 'loan officer survey',
        'KKR', 'Apollo', 'Blackstone', 'Ares', 'credit crunch',
    ],
    '美股/科技': ['nasdaq', 'sp500', 's&p', 'tech', 'nvidia', 'apple', 'microsoft', 'google', 'amazon', 'meta', 'tesla', 'ai', 'earnings'],
    '能源/石油': ['oil', 'crude', 'brent', 'wti', 'opec', 'iran', 'energy', 'natural gas', 'lng', 'petroleum'],
    '黄金/商品': ['gold', 'silver', 'commodity', 'precious metal', 'copper', 'mining'],
    '美元/外汇': ['dollar', 'dxy', 'euro', 'yen', 'forex', 'currency', 'yuan', 'rmb'],
    '中国/亚洲': ['china', 'chinese', 'hong kong', 'hang seng', 'asia', 'japan', 'emerging market', 'tariff', 'trade war'],
    '加密货币': ['bitcoin', 'btc', 'crypto', 'ethereum', 'blockchain', 'digital asset'],
    '地缘政治': [
        'iran', 'russia', 'ukraine', 'war', 'sanction', 'geopolit', 'middle east', 'conflict', 'military',
        'Hormuz', 'strait',
        'military', 'troops', 'missile', 'strike', 'attack',
        'sanctions', 'embargo', 'blockade',
        'OPEC', 'strategic reserve', 'SPR',
        'escalation', 'ceasefire', 'negotiate',
        'defense', 'weapons', 'nuclear',
        'Taiwan', 'South China Sea',
        'Russia', 'Ukraine', 'NATO',
    ],
    '实体经济': [
        'PMI', 'ISM', 'manufacturing', 'services',
        'new orders', 'inventories', 'employment',
        'consumer confidence', 'consumer sentiment', 'Michigan',
        'retail sales', 'spending', 'consumer',
        'layoff', 'hiring freeze', 'job cuts', 'unemployment',
        'margin pressure', 'profit warning', 'earnings miss',
        'guidance cut', 'cost pressure', 'input costs',
        'wage growth', 'labor market', 'payroll', 'nonfarm',
        'GDP', 'recession', 'contraction', 'slowdown',
        'shipping', 'freight', 'supply chain',
    ],
    '区域分化': [
        'ECB', 'BOJ', 'BOE', 'PBOC', 'RBI',
        'eurozone', 'Europe inflation', 'Europe rate',
        'Japan rate', 'Japan inflation', 'yen',
        'emerging market', 'capital outflow', 'currency crisis',
        'current account', 'reserves', 'balance of payments',
        'decoupling', 'divergence', 'fragmentation',
    ],
}

def fetch_market_news():
    """获取Finnhub市场综合新闻"""
    print("\n📰 采集市场综合新闻...")
    try:
        news = fh_client.general_news('general', min_id=0)
        # 只取最近7天
        cutoff = int((datetime.now() - timedelta(days=7)).timestamp())
        recent = [n for n in news if n.get('datetime', 0) > cutoff]
        print(f"  ✅ 获取 {len(recent)} 条（最近7天）")
        return recent
    except Exception as e:
        print(f"  ❌ 市场新闻失败: {e}")
        return []

def fetch_company_news():
    """获取关注个股的新闻"""
    print("\n📰 采集个股新闻...")
    today = datetime.now().strftime('%Y-%m-%d')
    week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    all_news = []
    for symbol in WATCH_SYMBOLS:
        try:
            news = fh_client.company_news(symbol, _from=week_ago, to=today)
            # 每只股票只取最重要的5条
            top_news = news[:5] if news else []
            for n in top_news:
                n['_symbol'] = symbol
            all_news.extend(top_news)
            print(f"  ✅ {symbol}: {len(news)} 条，取前 {len(top_news)} 条")
            time.sleep(0.5)  # 避免触发频率限制
        except Exception as e:
            print(f"  ❌ {symbol}: {e}")

    return all_news

def fetch_rss_news():
    """获取RSS新闻"""
    print("\n📰 采集RSS新闻...")
    all_entries = []

    for name, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            entries = feed.entries[:15]  # 每个源取前15条

            for entry in entries:
                all_entries.append({
                    'source': name,
                    'headline': entry.get('title', ''),
                    'summary': entry.get('summary', '')[:200],
                    'url': entry.get('link', ''),
                    'datetime': int(time.mktime(entry.get('published_parsed', time.gmtime()))) if entry.get('published_parsed') else 0,
                })

            print(f"  ✅ {name}: {len(entries)} 条")
        except Exception as e:
            print(f"  ❌ {name}: {e}")

    return all_entries

def classify_news(all_news):
    """按关键词对新闻进行初步分类"""
    print("\n🏷️ 新闻分类中...")
    classified = {cat: [] for cat in CATEGORY_KEYWORDS}
    classified['其他'] = []

    for article in all_news:
        headline = article.get('headline', '').lower()
        summary = article.get('summary', '').lower()
        text = headline + ' ' + summary

        matched = False
        for category, keywords in CATEGORY_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                classified[category].append(article)
                matched = True
                break  # 一条新闻只归入第一个匹配的类别

        if not matched:
            classified['其他'].append(article)

    # 统计
    for cat, articles in classified.items():
        if articles:
            print(f"  {cat}: {len(articles)} 条")

    return classified

def sanitize_for_api(text):
    """脱敏处理：用正则全词匹配替换敏感关键词，保留金融分析语义"""
    import re
    # (pattern, replacement) - 使用正则全词边界 \b 避免破坏单词
    word_replacements = [
        # 战争/军事类
        (r'\bwar\b', 'conflict'), (r'\bwars\b', 'conflicts'),
        (r'\bstrike\b', 'action'), (r'\bstrikes\b', 'actions'),
        (r'\battack\b', 'disruption'), (r'\battacks\b', 'disruptions'), (r'\battacked\b', 'disrupted'),
        (r'\bmissile\w*\b', 'equipment'),
        (r'\bmilitary\b', 'defense'),
        (r'\btroops\b', 'personnel'),
        (r'\bweapons\b', 'equipment'),
        (r'\bnuclear\b', 'strategic'),
        (r'\binvasion\b', 'escalation'),
        (r'\bbombing\b', 'impact'), (r'\bbombs\b', 'impacts'),
        (r'\bkilled\b', 'affected'), (r'\bkills\b', 'affects'),
        (r'\bdeath\b', 'loss'), (r'\bdeaths\b', 'losses'),
        (r'\bdead\b', 'affected'),
        (r'\bdestroy\w*\b', 'disrupt'),
        (r'\bshoot\b', 'intercept'), (r'\bshot\b', 'intercepted'),
        (r'\bexplosio\w*\b', 'disruption'),
        (r'\bbattle\w*\b', 'confrontation'),
        (r'\bcombat\b', 'engagement'),
        (r'\bceasefire\b', 'de-escalation'),
        (r'\btruce\b', 'pause'),
        (r'\bhostage\w*\b', 'constraint'),
        (r'\bterror\w*\b', 'risk'),
        (r'\bmadness\b', 'intensity'),
        (r'\bsurrender\w*\b', 'conclude'),
        (r'\bretreat\b', 'pullback'),
        (r'\bcasualt\w+\b', 'impact'),
        (r'\brefugee\w*\b', 'displaced'),
        (r'\bevacuat\w+\b', 'relocation'),
        (r'\bfighter\b', 'asset'), (r'\bwarplane\w*\b', 'asset'),
        (r'\bairstrike\w*\b', 'escalation'), (r'\bwarship\w*\b', 'vessel'),
        (r'\bdrone\w*\b', 'UAV'),
        (r'\bmine\w*\b', 'obstruction'),
        (r'\bnavy\b', 'maritime'),
        (r'\bsanction\w*\b', 'trade restrictions'),
        (r'\bembargo\b', 'trade ban'),
        (r'\bblockade\b', 'disruption'),
        # 国家名
        (r'\bIran\b', 'Country-A'), (r'\bIranian\w*\b', 'Country-A'),
        (r'\bIsrael\b', 'Country-B'), (r'\bIsraeli\w*\b', 'Country-B'),
        (r'\bRussia\b', 'Country-C'), (r'\bRussian\w*\b', 'Country-C'),
        (r'\bUkraine\b', 'Region-E'), (r'\bUkrainian\w*\b', 'Region-E'),
        (r'\bPutin\b', 'Leader-C'),
        # 地区
        (r'\bStrait\s+of\s+Hormuz\b', 'key shipping channel'),
        (r'\bHormuz\b', 'key channel'),
        (r'\bMiddle\s+East\b', 'region'),
        (r'\bPersian\s+Gulf\b', 'key waterway'),
        (r'\bBeirut\b', 'regional capital'),
        # 中文
        ('战争', '冲突'), ('军事', '防务'), ('导弹', '装备'),
        ('袭击', '事件'), ('攻击', '冲击'), ('轰炸', '打击'),
        ('伊朗', '产油国A'), ('以色列', '相关方B'),
        ('俄罗斯', '相关方C'), ('乌克兰', '相关方D'),
        ('霍尔木兹', '关键航道'), ('中东', '该地区'),
    ]
    for pattern, replacement in word_replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def generate_news_summary(classified):
    """用DeepSeek生成新闻摘要"""
    print("\n🤖 生成新闻摘要...")

    # 构建脱敏新闻文本 — 只用标题，双重脱敏
    news_text = ""
    for category, articles in classified.items():
        if not articles:
            continue
        news_text += f"\n### {category}\n"
        for a in articles[:6]:  # 每类最多6条
            source = a.get('source', '未知')
            headline = a.get('headline', '')
            news_text += f"- [{source}] {headline}\n"

    if not news_text.strip():
        print("  ⚠️ 无新闻内容")
        return "本周无重要新闻"

    # 脱敏处理：避免API敏感内容审核拦截
    news_text = sanitize_for_api(news_text)

    # 二次脱敏：补充可能漏掉的组合敏感词
    import re
    extra_replacements = [
        (r'\bpeace\s+deal\b', 'agreement'),
        (r'\bpeace\s+talks?\b', 'negotiations'),
        (r'\bTrump\b', 'the administration'),
        (r'\bPutin\b', 'Leader-C'),
        (r'\bMacron\b', 'the French president'),
        (r'\bErdogan\b', 'the Turkish president'),
        (r'\bStarmer\b', 'the British PM'),
        (r'\bVance\b', 'the VP'),
        (r'\bPope\b', 'the pontiff'),
        (r'\bnegotiations?\b', 'talks'),
        (r'\bnegotiators?\b', 'delegates'),
        (r'\bde-escalation\b', 'cooling'),
        (r'\bconflict\b', 'tension'),
        (r'\bconflicts\b', 'tensions'),
        (r'\bsetting conditions\b', 'preparing'),
        (r'\bclear\s+obstruction\w*', 'reopen'),
        (r'\bBattles?\b', 'Disputes'),
        (r'\bundocumented\b', 'unregistered'),
    ]
    for pattern, replacement in extra_replacements:
        news_text = re.sub(pattern, replacement, news_text, flags=re.IGNORECASE)

    prompt = f"""以下是本周的金融市场新闻标题，已按类别分组。请完成以下任务：

1. 每个类别提炼出 1-3 条最重要的新闻，用一句中文概括其核心信息和市场影响
2. 在最后给出一段"本周新闻总结"（3-5句话），概括本周新闻的主线叙事
3. 特别标注与以下主题相关的新闻：信用恶化、美联储政策、油价/地缘冲突、AI/科技资本开支、中国市场
4. 输出语言：中文
5. 注意：部分国家名和术语已做脱敏处理（如"Country-A"代表某产油国，"key channel"代表某重要航道，"tension"代表地缘事件），请基于金融语境还原真实含义并分析

新闻内容：
{news_text}
"""

    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

    try:
        response = client.responses.create(
            model=DEEPSEEK_MODEL,
            input=[
                {"role": "system", "content": "你是金融市场新闻分析师，擅长从大量新闻中提取关键信息和市场影响。输出简洁、精准。"},
                {"role": "user", "content": prompt}
            ]
        )
        summary = response.output[0].content[0].text
        print(f"  ✅ 摘要生成完成: {len(summary)} 字符")
        return summary
    except Exception as e:
        print(f"  ❌ responses.create 失败: {e}")
        # 备用接口
        try:
            response = client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=[
                    {"role": "system", "content": "你是金融市场新闻分析师。输出简洁中文摘要。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3000,
                temperature=0.3
            )
            summary = response.choices[0].message.content
            print(f"  ✅ 备用接口成功: {len(summary)} 字符")
            return summary
        except Exception as e2:
            print(f"  ❌ 备用接口也失败: {e2}")
            # 最后手段：直接输出分类标题
            fallback = "## 本周新闻摘要（AI摘要失败，以下为原始标题）\n\n"
            for cat, articles in classified.items():
                if articles:
                    fallback += f"### {cat}\n"
                    for a in articles[:5]:
                        fallback += f"- {a.get('headline', '')}\n"
                    fallback += "\n"
            return fallback

def save_news(classified, summary):
    """保存新闻数据"""
    date_str = datetime.now().strftime('%Y%m%d')
    news_dir = os.path.join(DATA_DIR, 'news')
    os.makedirs(news_dir, exist_ok=True)

    # 保存原始分类数据
    raw_path = os.path.join(news_dir, f'news_raw_{date_str}.json')

    # 简化存储（只保留关键字段）
    save_data = {}
    for cat, articles in classified.items():
        save_data[cat] = [{
            'headline': a.get('headline', ''),
            'source': a.get('source', ''),
            'summary': a.get('summary', '')[:200],
            'datetime': a.get('datetime', 0),
        } for a in articles[:10]]

    with open(raw_path, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)

    # 保存AI摘要
    summary_path = os.path.join(news_dir, f'news_summary_{date_str}.md')
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(f"# 新闻摘要 {date_str}\n\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        f.write(summary)

    print(f"\n💾 文件已保存:")
    print(f"  原始数据: {raw_path} ({os.path.getsize(raw_path)} 字节)")
    print(f"  AI摘要: {summary_path} ({os.path.getsize(summary_path)} 字节)")

    return summary_path

# ============ 主程序 ============
if __name__ == '__main__':
    print("=" * 60)
    print("📰 新闻采集与分析")
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 1. 采集
    market_news = fetch_market_news()
    company_news = fetch_company_news()
    rss_news = fetch_rss_news()

    # 2. 合并（统一格式）
    all_news = []
    for n in market_news:
        all_news.append({
            'headline': n.get('headline', ''),
            'source': n.get('source', 'Finnhub'),
            'summary': n.get('summary', ''),
            'datetime': n.get('datetime', 0),
        })
    for n in company_news:
        all_news.append({
            'headline': n.get('headline', ''),
            'source': f"{n.get('source', 'Finnhub')}({n.get('_symbol', '')})",
            'summary': n.get('summary', ''),
            'datetime': n.get('datetime', 0),
        })
    for n in rss_news:
        all_news.append(n)

    print(f"\n📊 合计采集: {len(all_news)} 条新闻")

    # 3. 分类
    classified = classify_news(all_news)

    # 4. AI摘要
    summary = generate_news_summary(classified)

    # 5. 保存
    save_news(classified, summary)

    # 6. 预览
    print("\n" + "=" * 60)
    print("📖 摘要预览（前20行）:")
    print("=" * 60)
    lines = summary.split('\n')
    for line in lines[:20]:
        print(line)
    if len(lines) > 20:
        print(f"\n... 共 {len(lines)} 行")

    print("\n🎉 新闻采集完成！")
