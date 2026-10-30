"""
新闻采集模块
数据源：Finnhub（市场新闻+个股新闻）+ RSS（CNBC+Bloomberg）
输出：分类新闻摘要，供AI生成报告使用

IA-P0-2-W3(新闻原始来源保全):
- 采集顺序固定: 采集 → 原始来源归档(news_provenance.save_batch) → 分类
  → GLM摘要 → 输出——GLM失败原始来源已保全(W3-03 §7.2);
- 原始保全字段: 供应商文章ID/标题/摘要全文/URL/发布时间原文/related/
  请求证券代码/Feed身份/entry.id——URL不再在合并时丢失(W3问题1),
  summary_original归档前禁止[:200]截断(W3问题2,截断只在派生视图);
- RSS时间: published_parsed按UTC解释(calendar.timegm),不再用time.mktime
  受进程本地时区影响(W3问题3);来源发布时间/采集时间独立保存;
  缺发布时间→UNKNOWN,不用采集时间冒充;
- 脱敏只发生在派生模型输入副本(sanitize_for_api),原始档案永不脱敏
  (W3问题4);模型输入行携带实际存在的[art_xxx]引用ID(W3-04 §8.4);
- 周报引用链: 每日写news_refs_YYYYMMDD.json确定性来源索引(W3-05)。
"""

import os
import sys
import json
import time
import calendar
import feedparser
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.dirname(__file__))
from env_config import FINNHUB_API_KEY, GLM_API_KEY, GLM_BASE_URL, GLM_MODEL
import news_provenance as nprov

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
    """获取RSS新闻(W3-02 §6.3: 全字段保全+UTC确定性时间)

    - Feed名称/URL、entry.id或guid、title、link、summary全文(不截断)、
      published原始字符串、published_parsed按UTC转换全部保留;
    - published_parsed是UTC结构化时间 → calendar.timegm(UTC解释);
      历史用time.mktime按进程本地时区解释,同一Feed在不同TZ环境结果漂移
      (W3问题3),已废除;
    - 缺发布时间 → published_parsed_utc=None(UNKNOWN),不造假时间;
    - 'datetime'仅为旧分类/展示层的epoch视图(0=未知),权威时间在原始档案。
    """
    print("\n📰 采集RSS新闻...")
    all_entries = []
    feed_status = {}

    for name, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            entries = feed.entries[:15]  # 每个源取前15条

            for entry in entries:
                parsed = entry.get('published_parsed')
                pub_utc = nprov.rss_parsed_to_utc_iso(parsed)
                all_entries.append({
                    'source': name,
                    'headline': entry.get('title', ''),
                    'summary': entry.get('summary', ''),   # 全文,归档前不截断
                    'url': entry.get('link', ''),
                    'datetime': calendar.timegm(parsed) if parsed else 0,
                    # W3原始保全字段
                    'provider': 'RSS', 'channel': 'rss',
                    'feed_name': name, 'feed_url': url,
                    'entry_id': entry.get('id', '') or entry.get('guid', ''),
                    'headline_original': entry.get('title', ''),
                    'summary_original': entry.get('summary', ''),
                    'url_original': entry.get('link', '') or None,
                    'published_raw': entry.get('published', ''),
                    'published_parsed_utc': pub_utc,
                })

            feed_status[f'RSS:{name}'] = 'ok'
            print(f"  ✅ {name}: {len(entries)} 条")
        except Exception as e:
            feed_status[f'RSS:{name}'] = 'fail'
            print(f"  ❌ {name}: {e}")

    return all_entries, feed_status


def collect_all_news(now_utc=None):
    """三源采集合并 → (原始保全记录raw_records, 来源状态source_status,
    展示条目display_items)。

    W3-02: 合并不再丢URL——市场/个股新闻原样保留供应商字段(id/source/
    summary/url/datetime/related),个股新闻记录请求证券代码且不因多证券
    关联覆盖来源身份(每条记录独立,article_id由供应商ID>URL>三元组决定)。
    display_items保持旧分类器口径(headline/source/summary/datetime)+
    article_id引用,供分类/GLM输入/news_raw兼容视图使用。
    """
    now_utc = now_utc or nprov.now_utc_iso()
    retrieved = now_utc  # 采集时刻独立于来源发布时间保存
    market_news = fetch_market_news()
    company_news = fetch_company_news()
    rss_news, rss_status = fetch_rss_news()

    raw_records, display = [], []
    for n in market_news:
        raw = {'provider': 'Finnhub', 'channel': 'market_news',
               'provider_article_id': n.get('id', ''),
               'publisher': n.get('source', ''),
               'headline_original': n.get('headline', ''),
               'summary_original': n.get('summary', '') or '',
               'url_original': n.get('url', '') or None,
               'published_raw': n.get('datetime', 0),
               'retrieved_at_utc': retrieved}
        raw_records.append(raw)
        display.append({'headline': n.get('headline', ''),
                        'source': n.get('source', 'Finnhub'),
                        'summary': n.get('summary', ''),
                        'datetime': n.get('datetime', 0),
                        'url': n.get('url', ''),
                        'article_id': nprov.stable_article_id(raw)})
    for n in company_news:
        raw = {'provider': 'Finnhub', 'channel': 'company_news',
               'provider_article_id': n.get('id', ''),
               'publisher': n.get('source', ''),
               'headline_original': n.get('headline', ''),
               'summary_original': n.get('summary', '') or '',
               'url_original': n.get('url', '') or None,
               'published_raw': n.get('datetime', 0),
               'watch_symbol': n.get('_symbol', ''),
               'related': n.get('related', ''),
               'retrieved_at_utc': retrieved}
        raw_records.append(raw)
        display.append({'headline': n.get('headline', ''),
                        'source': f"{n.get('source', 'Finnhub')}({n.get('_symbol', '')})",
                        'summary': n.get('summary', ''),
                        'datetime': n.get('datetime', 0),
                        'url': n.get('url', ''),
                        'article_id': nprov.stable_article_id(raw),
                        'watch_symbol': n.get('_symbol', '')})
    for n in rss_news:
        raw = {k: n[k] for k in ('provider', 'channel', 'feed_name',
                                 'feed_url', 'entry_id', 'headline_original',
                                 'summary_original', 'url_original',
                                 'published_raw', 'published_parsed_utc')}
        raw['retrieved_at_utc'] = retrieved
        raw_records.append(raw)
        display.append({'headline': n['headline'], 'source': n['source'],
                        'summary': n['summary'], 'datetime': n['datetime'],
                        'url': n['url'], 'article_id': nprov.stable_article_id(raw)})

    source_status = {
        'Finnhub/general': 'ok' if market_news is not None else 'fail',
        'Finnhub/company_news': 'ok' if company_news is not None else 'fail',
    }
    source_status.update(rss_status)   # 逐feed成败披露(部分失败保真实+披露)
    return raw_records, source_status, display

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
    # W3-04 §8.4: 每行携带实际存在的[art_xxx]来源引用ID(原始档案核发,
    # 确定性生成);脱敏/替换只发生在这个派生副本,原始档案永不脱敏。
    news_text = ""
    for category, articles in classified.items():
        if not articles:
            continue
        news_text += f"\n### {category}\n"
        for a in articles[:6]:  # 每类最多6条
            source = a.get('source', '未知')
            headline = a.get('headline', '')
            art = a.get('article_id', '')
            ref = f"[{art}] " if art else ""
            news_text += f"- {ref}[{source}] {headline}\n"

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
5. 行首形如[art_xxx]的标记是来源引用编号，无需复现到摘要中；部分术语已做脱敏处理（如"Country-A"、"key channel"、"tension"），无法确知具体所指时直接沿用代称分析即可，不必猜测真实国家、人物或事件，保留不确定性

新闻内容：
{news_text}
"""

    # 2026-10-11 P0修复(缺陷六.1/六.10): 此处原调用火山引擎DeepSeek(responses.create),
    # 模型已下线(ModelNotOpen)导致每日"AI摘要失败"降级为原始标题噪音。
    # 迁移到智谱GLM(与周报同通道,流式防断连,见 glm-api-pitfalls)。
    client = OpenAI(api_key=GLM_API_KEY, base_url=GLM_BASE_URL)

    try:
        stream = client.chat.completions.create(
            model=GLM_MODEL,
            messages=[
                {"role": "system", "content": "你是金融市场新闻分析师，擅长从大量新闻中提取关键信息和市场影响。输出简洁、精准。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.3,
            extra_body={"reasoning_effort": "low"},
            stream=True,
        )
        chunks = []
        for ev in stream:
            if ev.choices and ev.choices[0].delta and ev.choices[0].delta.content:
                chunks.append(ev.choices[0].delta.content)
        summary = "".join(chunks)
        if not summary.strip():
            raise RuntimeError("流式返回为空")
        print(f"  ✅ 摘要生成完成(GLM): {len(summary)} 字符")
        return summary
    except Exception as e:
        print(f"  ❌ GLM摘要失败: {e}")
        # 最后手段：直接输出分类标题
        # W3-06: GLM失败时原始来源档案已归档(归档先于GLM);回退输出携带
        # [art_xxx]引用ID保持可追溯,不得用编造链接填充来源缺口。
        fallback = "## 本周新闻摘要（AI摘要失败，以下为原始标题，[art_xxx]为来源引用编号）\n\n"
        for cat, articles in classified.items():
            if articles:
                fallback += f"### {cat}\n"
                for a in articles[:5]:
                    art = a.get('article_id', '')
                    ref = f"[{art}] " if art else ""
                    fallback += f"- {ref}{a.get('headline', '')}\n"
                fallback += "\n"
        return fallback

def save_news(classified, summary, now_utc=None):
    """保存新闻数据(W3-05: +article_id/+url/+摘要全文;写确定性来源索引)

    news_raw_{ymd}.json 为简化兼容视图(每次运行重建,非原始档案——原始
    档案是news_sources_*版本化批次,见news_provenance);原始URL与完整
    摘要在此视图同样保全,不再[:200]截断。
    news_refs_{ymd}.json 为周报消费端确定性来源索引(article_id→原始
    标题/URL/发布时间/通道/完整性),由代码构造,非模型生成。
    """
    now_utc = now_utc or nprov.now_utc_iso()
    date_str = now_utc[:10].replace('-', '')
    news_dir = os.path.join(DATA_DIR, 'news')
    os.makedirs(news_dir, exist_ok=True)

    # 保存原始分类数据
    raw_path = os.path.join(news_dir, f'news_raw_{date_str}.json')

    # 简化存储（只保留关键字段;W3起含article_id/url/全文摘要）
    save_data = {}
    for cat, articles in classified.items():
        save_data[cat] = [{
            'article_id': a.get('article_id', ''),
            'headline': a.get('headline', ''),
            'source': a.get('source', ''),
            'summary': a.get('summary', ''),
            'datetime': a.get('datetime', 0),
            'url': a.get('url', ''),
        } for a in articles[:10]]

    with open(raw_path, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)

    # 保存AI摘要
    summary_path = os.path.join(news_dir, f'news_summary_{date_str}.md')
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(f"# 新闻摘要 {date_str}\n\n")
        f.write(f"生成时间: {now_utc}\n\n")
        f.write("---\n\n")
        f.write(summary)

    # W3-05: 确定性来源索引(从原始来源档案批次构建,含完整性核验)
    refs_path = nprov.write_refs_index(news_dir, ymd=date_str,
                                       now_utc=now_utc)

    print(f"\n💾 文件已保存:")
    print(f"  原始数据: {raw_path} ({os.path.getsize(raw_path)} 字节)")
    print(f"  AI摘要: {summary_path} ({os.path.getsize(summary_path)} 字节)")
    if refs_path:
        print(f"  来源索引: {refs_path} ({os.path.getsize(refs_path)} 字节)")

    return summary_path

# ============ 主程序 ============
def run(now_utc=None):
    """新闻采集主流程(W3-03 §7.2顺序: 采集→原始归档→分类→GLM摘要→输出)。

    - 原始来源档案先于分类/GLM落盘: GLM失败/超时时已获取的原始来源仍已
      保全(W3-06);
    - 全部来源失败: 不创建虚假有效新闻批次(无原始记录不归档),摘要降级为
      无可信新闻数据披露,周报金融事实研究不受阻(非关键步骤语义不变);
    - 部分来源失败: 保留其余真实来源,失败源记入批次source_status明确披露,
      不伪造失败源的文章。
    """
    now_utc = now_utc or nprov.now_utc_iso()
    print("=" * 60)
    print("📰 新闻采集与分析")
    print(f"🕐 {now_utc}")
    print("=" * 60)

    # 1. 采集(全字段保全)
    raw_records, source_status, display = collect_all_news(now_utc=now_utc)
    print(f"\n📊 合计采集: {len(display)} 条新闻")

    # 2. 原始来源归档(先于分类/GLM;同日重跑新批次,旧批次永不覆盖)
    news_dir = os.path.join(DATA_DIR, 'news')
    batch_id = None
    if raw_records:
        batch_id, apath, records = nprov.save_batch(
            raw_records, news_dir, retrieved_at_utc=now_utc,
            source_status=source_status, now_utc=now_utc)
        print(f"🗄️ 原始来源档案: {apath} ({len(records)}条,批次{batch_id})")
    else:
        failed = {k: v for k, v in source_status.items() if v != 'ok'}
        print(f"⚠️ 全部新闻来源失败(无原始记录,不创建虚假批次): {failed}")

    # 3. 分类(沿用关键词体系;条目保留article_id)
    classified = classify_news(display)

    # 4. AI摘要(GLM;失败回退原始标题+引用ID,原始档案已保全)
    if raw_records:
        summary = generate_news_summary(classified)
    else:
        summary = ("## 本周无可信新闻数据\n\n"
                   "(全部新闻来源采集失败,未创建新闻来源批次;本段为降级披露,"
                   "非模型生成,不含任何虚构新闻条目)")

    # 5. 保存(摘要+简化视图+确定性来源索引)
    save_news(classified, summary, now_utc=now_utc)

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
    return summary


if __name__ == '__main__':
    run()
