#!/usr/bin/env python3
"""
数据校验器 v2.0
修复：
- 核心比对引擎：真正计算偏差百分比并判断是否超标
- 单位归一化：15.8万/158K/158,000 → 统一为基础数值
- 变化率校验：周涨跌幅也作为锚点
- 空锚点硬中断：锚点不足时中断流水线
"""
import os, sys, re, json, glob
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIN_ANCHOR_COUNT = 20  # 最低锚点数量阈值

# === 单位归一化 ===
def normalize_number(text):
    """
    将各种格式的数字归一化为浮点数
    支持: 15.8万, 158K, 158,000, 2.3万亿, $96.57, 4.31%
    """
    text = text.strip().replace(',', '').replace('$', '').replace('¥', '').replace('%', '')

    multipliers = {
        '万亿': 1e12, '千亿': 1e11, '百亿': 1e10, '十亿': 1e9,
        '亿': 1e8, '千万': 1e7, '百万': 1e6, '十万': 1e5, '万': 1e4,
        'T': 1e12, 'B': 1e9, 'M': 1e6, 'K': 1e3, 'k': 1e3,
    }

    for suffix, mult in multipliers.items():
        if text.endswith(suffix):
            num_part = text[:-len(suffix)]
            try:
                return float(num_part) * mult
            except ValueError:
                continue

    try:
        return float(text)
    except ValueError:
        return None


# === 锚点提取 ===
def flatten_json(data, prefix=''):
    items = {}
    if isinstance(data, dict):
        for k, v in data.items():
            new_key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, (dict, list)):
                items.update(flatten_json(v, new_key))
            else:
                items[new_key] = v
    elif isinstance(data, list):
        for i, v in enumerate(data):
            new_key = f"{prefix}[{i}]"
            if isinstance(v, (dict, list)):
                items.update(flatten_json(v, new_key))
            else:
                items[new_key] = v
    return items


def find_latest_file(pattern):
    full_pattern = os.path.join(ROOT_DIR, pattern)
    files = sorted(glob.glob(full_pattern))
    return files[-1] if files else None


def extract_anchors_from_data():
    anchors = {}

    data_sources = {
        'global_market': 'data/daily/global_*.json',
        'macro': 'data/daily/macro_*.json',
        'rate_economy': 'data/daily/rate_economy_*.json',
        'china': 'data/daily/china_*.json',
        'scorecard': 'data/daily/scorecard_*.json',
    }

    for source_name, pattern in data_sources.items():
        filepath = find_latest_file(pattern)
        if not filepath:
            print(f"⚠️ 未找到数据源: {pattern}")
            continue

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # P0修复(六.5): 锚点补时间元数据 — as_of=采集日(源自文件名),obs_date=观测日(源自兄弟.date字段)
            as_of = '未知'
            m = re.search(r'(\d{8})', os.path.basename(filepath))
            if m:
                as_of = f"{m.group(1)[:4]}-{m.group(1)[4:6]}-{m.group(1)[6:]}"

            flat = flatten_json(data)
            count = 0
            for key, value in flat.items():
                if isinstance(value, (int, float)) and value != 0:
                    anchors[f"{source_name}.{key}"] = {
                        'value': value,
                        'source_file': os.path.basename(filepath),
                        'as_of': as_of,
                        'tolerance_pct': 1.0
                    }
                    count += 1

            # 把形如 xxx.date 的观测日挂到同一父节点下的所有数值锚点上
            # (区分"数据是哪天的"与"哪天抓的")。兼容两种日期格式:
            # ISO "2026-10-09"(FRED/yfinance) 和紧凑 "20261009"(akshare)。
            # 匹配方式: 父节点前缀匹配 — data.SPX.date 覆盖 data.SPX.close/.change等全部兄弟数值
            def _norm_date(s):
                if re.match(r'\d{4}-\d{2}-\d{2}', s):
                    return s[:10]
                m8 = re.match(r'^(\d{4})(\d{2})(\d{2})$', s.strip())
                if m8:
                    return f"{m8.group(1)}-{m8.group(2)}-{m8.group(3)}"
                return None

            dated = 0
            for key, value in flat.items():
                if not (isinstance(value, str) and key.endswith('.date')):
                    continue
                obs = _norm_date(value)
                if not obs:
                    continue
                parent = key[:-5]
                for akey in anchors:
                    if akey in (parent, f"{source_name}.{parent}") \
                       or akey.startswith((f"{parent}.", f"{source_name}.{parent}.")):
                        if 'obs_date' not in anchors[akey]:
                            anchors[akey]['obs_date'] = obs
                            dated += 1
            print(f"✅ {source_name}: 提取 {count} 个数值锚点 (采集日 {as_of}, {dated} 个含观测日)")

        except Exception as e:
            print(f"❌ {source_name} 读取失败: {e}")

    return anchors


# === 核心比对引擎 ===
REPORT_CHECKS = [
    # (名称, 报告中的正则, 锚点key的匹配模式, 容差%, 是否为百分比值)
    ("SPX收盘", r'(?:SPX|标普500)[^0-9%]*?([0-9]{3,5}(?:\.[0-9]+)?)', r'global_market.*(?:SPX|SPY|sp500).*(?:close|price|收盘)', 0.5, False),
    ("WTI油价", r'(?:WTI|油价)\s*(?:收于|收盘|价格|现价|为|至)?\s*\$?([0-9]{2,3}\.[0-9]+)(?!\s*%)', r'global_market.*(?:WTI|CL|oil|原油).*(?:close|price|收盘)', 1.0, False),
    ("黄金价格", r'(?:黄金|GOLD|XAU)[^0-9%]*?([0-9]{3,5}(?:\.[0-9]+)?)(?!\s*%)', r'global_market.*(?:GOLD|GC|gold|黄金).*(?:close|price|收盘)', 0.5, False),
    ("DXY", r'(?:DXY|美元指数)[^0-9%]*?([0-9]{2,3}\.[0-9]+)(?!\s*%)', r'global_market.*(?:DXY|美元).*(?:close|price|收盘)', 0.5, False),
    ("VIX", r'VIX[^0-9%]*?([0-9]{1,3}\.[0-9]+)(?!\s*%)', r'global_market.*VIX.*(?:close|price|收盘)', 2.0, False),
    ("BTC", r'(?:BTC|比特币)[^0-9%]*?([0-9]{4,6}(?:\.[0-9]+)?)(?!\s*%)', r'global_market.*(?:BTC|bitcoin).*(?:close|price|收盘)', 1.0, False),
    ("10Y收益率", r'(?:UST\s*10Y|10Y\s*(?:收益率|利率|国债))[^0-9]*?([0-9]\.[0-9]{2,3})\s*%', r'macro.*(?:UST_10Y|10Y|GS10|DGS10).*(?:value|收益率)', 3.5, True),
    ("30Y收益率", r'(?:UST\s*30Y|30Y\s*(?:收益率|利率|国债))[^0-9]*?([0-9]\.[0-9]{2,3})\s*%', r'macro.*(?:UST_30Y|30Y|GS30|DGS30).*(?:value|收益率)', 2.0, True),
    ("CCC_OAS", r'CCC[^0-9]*?([0-9]{1,2}\.?[0-9]{0,3})\s*%?', r'macro.*(?:CCC|ccc).*(?:value|OAS|利差)', 2.0, True),
    ("HY_OAS", r'(?:HY\s*OAS|高收益利差)[^0-9]*?(?<!-)([0-9]\.[0-9]{2,3})\s*%', r'macro.*(?:HY|high.yield|高收益).*(?:value|OAS|利差)', 2.0, True),
    ("失业率", r'失业率(?!\s*(?:变动|变化|change|delta))[^0-9%]*?([3-9]\.[0-9])\s*%', r'rate_economy.*(?:UNRATE|失业率|unemployment).*(?:value|latest)', 0, True),
    ("消费者信心", r'(?:消费者信心|Michigan|密歇根)[^0-9]*?([0-9]{2,3}\.[0-9])', r'rate_economy.*(?:UMCSENT|消费者信心|michigan|confidence).*(?:value|latest)', 1.0, False),
    ("上证指数", r'(?:上证|上证指数|SSE)[^0-9%]*?([0-9]{3,4}\.[0-9]+)(?!\s*%)', r'china.*(?:上证|SSE|000001).*(?:close|收盘)', 5.0, False),
]

# 周变化率检查
CHANGE_CHECKS = [
    # (名称, 报告中变化率正则, 锚点key模式, 容差绝对值pp)
    ("WTI周涨跌", r'(?:WTI|油价)[^)]*?([+-]?[0-9]{1,3}\.[0-9]+)\s*%', r'global_market.*(?:WTI|CL|oil).*(?:change|涨跌|pct)', 0.6),
    ("黄金周涨跌", r'(?:黄金|GOLD)[^)]*?([+-]?[0-9]{1,3}\.[0-9]+)\s*%', r'global_market.*(?:GOLD|GC|gold|黄金).*(?:change|涨跌|pct)', 0.6),
    ("BTC周涨跌", r'(?:BTC|比特币)[^)]*?([+-]?[0-9]{1,3}\.[0-9]+)\s*%', r'global_market.*(?:BTC|bitcoin).*(?:change|涨跌|pct)', 0.5),
]

# 量级合理性
SANITY_CHECKS = {
    "非农月增": {
        "patterns": [
            r'(?:非农.*?新增|新增.*?非农|payrolls.*?\+)\s*([0-9]{1,4}(?:\.[0-9]+)?)\s*万',
            r'(?:非农.*?新增|新增.*?非农|payrolls.*?\+)\s*([0-9]{1,4}(?:\.[0-9]+)?)\s*[Kk]',
            r'(?:非农.*?新增|新增.*?非农|payrolls.*?\+)\s*([0-9,]{1,10})\s*(?:人|$)',
            r'非农.*?([0-9]{1,4}(?:\.[0-9]+)?)\s*[MmBb]',
        ],
        "normalize_and_check": True,
        "max_value_K": 1000,  # 最大100万人 = 1000K
        "error_msg": "非农月新增不应超过1,000K (100万人)"
    },
    "SPX范围": {
        "patterns": [r'(?:SPX|标普500)[^0-9%]*?([0-9]{3,5}(?:\.[0-9]+)?)(?!\s*%)'],
        "min_value": 2000, "max_value": 10000,
        "error_msg": "SPX收盘价应在2000-10000范围"
    },
    "WTI范围": {
        "patterns": [r'(?:WTI|油价)\s*(?:收于|收盘|价格|现价|为)?\s*\$?([0-9]{2,3}\.[0-9]+)(?!\s*%)'],
        "min_value": 20, "max_value": 200,
        "error_msg": "WTI价格应在$20-$200范围"
    },
    "VIX范围": {
        "patterns": [r'VIX[^0-9%]*?([0-9]{1,3}\.[0-9]+)(?!\s*%)'],
        "min_value": 8, "max_value": 90,
        "error_msg": "VIX应在8-90范围"
    },
    "A股口径": {
        "patterns": [r'((?:成交额|成交量|turnover)[^。\n]{0,30}(?:亿|billion))'],
        "require_scope_label": True,
        "valid_labels": ["全A", "上证", "沪深", "两市", "主板"],
        "error_msg": "A股成交额必须标注口径（全A/上证/沪深两市/主板）"
    },
}


# 禁止用语v2(2026-10-11, 与系统提示词【禁止用语v2】同步)
FORBIDDEN_V2 = ["完美验证", "教科书式", "毫无疑问", "铁板钉钉", "板上钉钉",
                "稳赚", "必涨", "必跌", "零风险", "百分百", "完全证实", "唯一解释",
                "perfectly validated", "textbook", "guaranteed", "inevitable",
                "risk-free", "no doubt", "100% certain"]
# "绝对""必然"是高频字面词,裸匹配会误伤"绝对收益/绝对估值"等合法术语:
# "绝对"仅当其后不接金融惯用名词时计为绝对化表述;"必然"在克制行文中本不应出现,直接计
ABS_RE = re.compile(r"绝对(?!(?:收益|回报|估值|值|水平|金额|数量|仓位|占比|占优|优势|涨幅|跌幅|龙头|超额))")

def forbidden_phrases_in(text):
    """扫描禁止用语v2,返回[(短语,次数)]"""
    found = [(p, text.count(p)) for p in FORBIDDEN_V2 if text.count(p)]
    n_abs = len(ABS_RE.findall(text))
    if n_abs:
        found.append(("绝对(绝对化用法)", n_abs))
    if text.count("必然"):
        found.append(("必然", text.count("必然")))
    return found


def find_anchor_value(anchors, key_pattern):
    """根据正则模式在锚点中查找匹配的值"""
    import re as _re
    matches = []
    for key, info in anchors.items():
        if _re.search(key_pattern, key, _re.IGNORECASE):
            matches.append((key, info['value']))
    return matches


# 日频行情源: 观测日不应明显滞后于报告日(月度FRED序列天然滞后,免检)
DAILY_SOURCES = ('global_market', 'china')
MAX_STALE_DAYS = 5

def _obs_staleness_warning(anchor_key, info, report_date):
    """P1(2026-10-11): 时点检查 — 日频行情锚点的观测日若明显滞后于报告日,提示风险。

    ⚠️提示级,不进_has_numeric_errors拦截;月度序列(UNRATE/CPILFESL等)不做此检查。
    防的是"周三的行情数据被周五报告当作现值引用"这类时点错位。
    """
    source = anchor_key.split('.')[0]
    if source not in DAILY_SOURCES:
        return None
    obs = info.get('obs_date')
    if not obs or not report_date:
        return None
    from datetime import date
    try:
        lag = (report_date - date(int(obs[:4]), int(obs[5:7]), int(obs[8:10]))).days
    except (ValueError, TypeError):
        return None
    if lag > MAX_STALE_DAYS:
        return (f"⚠️ 时点滞后 {anchor_key.split('.', 1)[1]}: 观测日{obs}落后报告日{lag}天"
                f" — 报告引用时须标注数据时点")
    return None

def _report_date_from_path(report_path):
    """从 weekly_report_YYYYMMDD.md 文件名解析报告日,失败返回今天"""
    m = re.search(r'(\d{8})', os.path.basename(report_path or ''))
    ref = m.group(1) if m else datetime.now().strftime('%Y%m%d')
    try:
        from datetime import date
        return date(int(ref[:4]), int(ref[4:6]), int(ref[6:8]))
    except ValueError:
        return None


def validate_report(report_path, anchors):
    if not os.path.exists(report_path):
        print(f"❌ 报告文件不存在: {report_path}")
        return []

    with open(report_path, 'r', encoding='utf-8') as f:
        report_text = f.read()

    warnings = []
    report_date = _report_date_from_path(report_path)

    # === 1. 核心数值比对 ===
    print("\n🔍 核心数值比对:")
    for name, report_pattern, anchor_pattern, tolerance_pct, is_pct in REPORT_CHECKS:
        report_matches = re.findall(report_pattern, report_text, re.IGNORECASE)
        if not report_matches:
            print(f"  ⬜ {name}: 报告中未提及")
            continue

        anchor_matches = find_anchor_value(anchors, anchor_pattern)
        if not anchor_matches:
            print(f"  ⬜ {name}: 报告值={report_matches[0]}, 无对应锚点可比对")
            continue

        try:
            report_val = float(report_matches[0].replace(',', ''))
        except ValueError:
            continue

        # 取最接近的锚点值
        closest_anchor = min(anchor_matches, key=lambda x: abs(x[1] - report_val))
        anchor_val = closest_anchor[1]
        anchor_key = closest_anchor[0]

        if anchor_val == 0:
            continue

        deviation_pct = abs(report_val - anchor_val) / abs(anchor_val) * 100

        if deviation_pct <= tolerance_pct:
            obs = anchors.get(anchor_key, {}).get('obs_date', '?')
            print(f"  ✅ {name}: 报告={report_val}, 锚点={anchor_val} (观测日{obs}, 偏差{deviation_pct:.2f}% ≤ {tolerance_pct}%)")
            # P1: 时点滞后检查(仅日频行情源,提示级)
            stale = _obs_staleness_warning(anchor_key, anchors.get(anchor_key, {}), report_date)
            if stale:
                warnings.append(stale)
                print(f"  {stale}")
        elif deviation_pct > 20:
            msg = f"🚨 严重错误 {name}: 报告={report_val}, 锚点={anchor_val} (偏差{deviation_pct:.2f}% — 疑似指标混淆)"
            warnings.append(msg)
            print(f"  {msg}")
        else:
            msg = f"❌ {name}: 报告={report_val}, 锚点={anchor_val} (偏差{deviation_pct:.2f}% > 容差{tolerance_pct}%)"
            warnings.append(msg)
            print(f"  {msg}")
            print(f"     锚点来源: {anchor_key}")

    # === 2. 周变化率比对 ===
    print("\n📈 周变化率比对:")
    for name, report_pattern, anchor_pattern, tolerance_pp in CHANGE_CHECKS:
        report_matches = re.findall(report_pattern, report_text, re.IGNORECASE)
        anchor_matches = find_anchor_value(anchors, anchor_pattern)

        if not report_matches or not anchor_matches:
            print(f"  ⬜ {name}: {'报告无数据' if not report_matches else '锚点无数据'}")
            continue

        try:
            report_val = float(report_matches[0])
            anchor_val = min(anchor_matches, key=lambda x: abs(x[1] - report_val))[1]
            deviation = abs(report_val - anchor_val)

            if deviation <= tolerance_pp:
                print(f"  ✅ {name}: 报告={report_val:+.2f}%, 锚点={anchor_val:+.2f}% (偏差{deviation:.2f}pp ≤ {tolerance_pp}pp)")
            else:
                msg = f"❌ {name}: 报告={report_val:+.2f}%, 锚点={anchor_val:+.2f}% (偏差{deviation:.2f}pp > 容差{tolerance_pp}pp)"
                warnings.append(msg)
                print(f"  {msg}")
        except (ValueError, IndexError):
            pass

    # === 3. 量级合理性检查 ===
    print("\n📏 量级合理性检查:")
    for check_name, rule in SANITY_CHECKS.items():
        if rule.get('require_scope_label'):
            for pattern in rule['patterns']:
                mentions = re.findall(pattern, report_text, re.IGNORECASE)
                for mention in mentions:
                    has_label = any(label in mention for label in rule['valid_labels'])
                    if not has_label:
                        msg = f"⚠️ {check_name}: \"{mention[:50]}\" — {rule['error_msg']}"
                        warnings.append(msg)
                        print(f"  {msg}")
                    else:
                        print(f"  ✅ {check_name}: 口径已标注")
            continue

        if rule.get('normalize_and_check'):
            for pattern in rule['patterns']:
                matches = re.findall(pattern, report_text, re.IGNORECASE)
                for match in matches:
                    val = normalize_number(match)
                    if val and val > rule['max_value_K'] * 1000:
                        msg = f"❌ {check_name}: {match} 归一化后={val:,.0f}, 超出合理范围 — {rule['error_msg']}"
                        warnings.append(msg)
                        print(f"  {msg}")
                    elif val:
                        print(f"  ✅ {check_name}: {match} (归一化={val:,.0f}, 合理)")
            continue

        for pattern in rule['patterns']:
            matches = re.findall(pattern, report_text, re.IGNORECASE)
            for match in matches:
                try:
                    val = float(match.replace(',', ''))
                    if 'max_value' in rule and val > rule['max_value']:
                        msg = f"❌ {check_name}: {val} > {rule['max_value']} — {rule['error_msg']}"
                        warnings.append(msg)
                        print(f"  {msg}")
                    elif 'min_value' in rule and val < rule['min_value']:
                        msg = f"❌ {check_name}: {val} < {rule['min_value']} — {rule['error_msg']}"
                        warnings.append(msg)
                        print(f"  {msg}")
                    else:
                        print(f"  ✅ {check_name}: {val} (合理)")
                except ValueError:
                    pass

    # === 4. 禁止用语检查(2026-10-11 v2: 与系统提示词【禁止用语v2】同步) ===
    print("\n🚫 禁止用语检查(v2):")
    found = forbidden_phrases_in(report_text)
    for phrase, count in found:
        msg = f"⚠️ 禁止用语v2 \"{phrase}\" 出现 {count} 次"
        warnings.append(msg)
        print(f"  {msg}")
    if not found:
        print(f"  ✅ 未发现禁止用语")

    # === 5. 自动标注版报告 ===
    annotated = report_text
    for phrase in FORBIDDEN_V2:
        annotated = annotated.replace(phrase, f"⚠️【禁止用语: {phrase}】")
    annotated = ABS_RE.sub("⚠️【禁止用语: 绝对】", annotated)
    annotated = annotated.replace("必然", "⚠️【禁止用语: 必然】")

    if annotated != report_text:
        annotated_path = report_path.replace('.md', '_annotated.md')
        with open(annotated_path, 'w', encoding='utf-8') as f:
            f.write(annotated)
        print(f"\n📝 标注版报告已保存: {annotated_path}")

    return warnings


def save_anchors(anchors):
    today = datetime.now().strftime('%Y%m%d')
    data_dir = os.path.join(ROOT_DIR, 'data', 'daily')
    os.makedirs(data_dir, exist_ok=True)

    serializable = {}
    for k, v in anchors.items():
        entry = {
            'value': v['value'],
            'source_file': v['source_file'],
        }
        if v.get('as_of'):
            entry['as_of'] = v['as_of']
        if v.get('obs_date'):
            entry['obs_date'] = v['obs_date']
        serializable[k] = entry

    path = os.path.join(data_dir, f'anchors_{today}.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2)
    print(f"\n💾 数据锚点: {path} ({os.path.getsize(path)} bytes, {len(anchors)} 个锚点)")
    return path


def generate_anchor_prompt_block(anchors):
    lines = ["## 数据锚点清单（AI生成报告时只能引用以下数字，不得自行推算或修改）\n"]

    # 易混淆指标警告
    lines.append("### ⚠️ 易混淆指标（必须区分，引用错误将导致报告不合格）")
    lines.append("- **30Y UST收益率（30年期美国国债）≠ 30年固定抵押贷款利率**。报告中'30Y'仅指国债收益率。")
    lines.append("- **非农就业总人数（PAYEMS，单位：千人）≠ 非农月新增人数（单位：千人/万人）**。158,637千人是总量，+178K是月新增。")
    lines.append("- **上证成交额 ≠ 全A成交额 ≠ 沪深两市成交额**。必须使用锚点中标注的口径。")
    lines.append("- **WTI现货价 ≠ WTI周涨跌幅%**。价格和百分比变化不得混用。")
    lines.append("")

    grouped = {}
    for key, info in anchors.items():
        source = key.split('.')[0]
        if source not in grouped:
            grouped[source] = []
        grouped[source].append((key, info['value']))

    source_names = {
        'global_market': '全球资产',
        'macro': '宏观信用',
        'rate_economy': '利率与实体经济',
        'china': 'A股港股',
        'scorecard': '评分卡',
    }

    for source, items in grouped.items():
        lines.append(f"### {source_names.get(source, source)}")
        for key, value in items:
            short_key = key.replace(f"{source}.", "")
            if isinstance(value, float):
                lines.append(f"- {short_key}: {value}")
            elif isinstance(value, int) and abs(value) > 1:
                lines.append(f"- {short_key}: {value}")
        lines.append("")

    return "\n".join(lines)


if __name__ == '__main__':
    print("=" * 60)
    print("📋 数据校验器 v2.0")
    print("=" * 60)

    # Step 1: 提取数据锚点
    print("\n--- Step 1: 提取数据锚点 ---")
    anchors = extract_anchors_from_data()

    # 硬中断检查
    if len(anchors) < MIN_ANCHOR_COUNT:
        print(f"\n🚨 严重错误: 锚点数量 {len(anchors)} < 最低阈值 {MIN_ANCHOR_COUNT}")
        print(f"   数据源可能全部缺失，中断流水线以防止空锚点注入prompt")
        print(f"   请检查 data/daily/ 目录下的数据文件是否存在")
        sys.exit(1)

    anchor_path = save_anchors(anchors)

    # Step 2: 生成prompt插入块
    print("\n--- Step 2: 生成Prompt锚点块 ---")
    prompt_block = generate_anchor_prompt_block(anchors)
    prompt_path = os.path.join(ROOT_DIR, 'data', 'daily',
                                f'anchor_prompt_{datetime.now().strftime("%Y%m%d")}.md')
    with open(prompt_path, 'w', encoding='utf-8') as f:
        f.write(prompt_block)
    print(f"💾 Prompt锚点块: {prompt_path} ({os.path.getsize(prompt_path)} bytes)")

    # Step 3: 校验最新报告
    print("\n--- Step 3: 校验最新报告 ---")
    report_files = sorted([f for f in glob.glob(os.path.join(ROOT_DIR, 'output', 'weekly', 'weekly_report_*.md')) if '_annotated' not in f])
    if report_files:
        latest_report = report_files[-1]
        print(f"📄 校验报告: {latest_report}")
        warnings = validate_report(latest_report, anchors)

        print(f"\n{'='*50}")
        critical_errors = [w for w in warnings if w.startswith("🚨")]
        minor_warnings = [w for w in warnings if not w.startswith("🚨")]

        if critical_errors:
            print(f"🚨 发现 {len(critical_errors)} 个严重错误（报告不可直接发布）:")
            for w in critical_errors:
                print(f"  {w}")
            print(f"\n⛔ 建议：修正数据后重新生成报告，或在发布前人工修正标注位置")
        if minor_warnings:
            print(f"⚠️ 发现 {len(minor_warnings)} 个一般警告:")
            for w in minor_warnings:
                print(f"  {w}")
        if not warnings:
            print("✅ 数据校验全部通过")
        print(f"{'='*50}")
    else:
        print("⚠️ 未找到周报文件，跳过校验")

    print(f"\n校验完成")
