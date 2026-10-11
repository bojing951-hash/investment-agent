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


def find_latest_file(pattern, data_dir=None):
    base = data_dir or os.path.join(ROOT_DIR, 'data', 'daily')
    files = sorted(glob.glob(os.path.join(base, pattern)))
    return files[-1] if files else None


def extract_anchors_from_data(data_dir=None):
    """data_dir参数供离线fixture测试注入(第二轮#20);默认实时项目目录。"""
    anchors = {}

    data_sources = {
        'global_market': 'global_*.json',
        'macro': 'macro_*.json',
        'rate_economy': 'rate_economy_*.json',
        'china': 'china_*.json',
        'scorecard': 'scorecard_*.json',
    }

    for source_name, pattern in data_sources.items():
        filepath = find_latest_file(pattern, data_dir)
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


# ============================================================================
# 指标ID级联合校验(第二轮审查#6/#8, 2026-10-11)
# 核心数字须"指标ID+观测日+单位+数值"联合验证,并专项拦截"前值当现值"
# (实战事故: 2026-10-09周报把TIPS 10Y上周2.93写成本周2.92当期值方向搞反)
# ============================================================================
INDICATOR_SPECS = [
    # id: 指标ID; alias: 报告提法(正则); cur/prev: 锚点key(精确); unit; tol: 数值容差
    {"id": "TIPS_10Y", "alias": r"(?:TIPS\s*10Y|10Y\s*TIPS|10年(?:期)?TIPS|10年(?:期)?实际利率)",
     "cur": "macro.data.TIPS_10Y.value", "prev": "macro.data.TIPS_10Y.prev",
     "unit": "%", "tol": 0.005},
    {"id": "TIPS_5Y", "alias": r"(?:TIPS\s*5Y|5Y\s*TIPS|5年(?:期)?TIPS|5年(?:期)?实际利率)",
     "cur": "macro.data.TIPS_5Y.value", "prev": "macro.data.TIPS_5Y.prev",
     "unit": "%", "tol": 0.005},
    {"id": "UST_10Y", "alias": r"(?:UST\s*10Y|10Y(?:美债)?(?:收益率|国债)|10年期美债(?:收益率)?)",
     "cur": "macro.data.UST_10Y.value", "prev": "macro.data.UST_10Y.prev",
     "unit": "%", "tol": 0.005},
    {"id": "UST_30Y", "alias": r"(?:UST\s*30Y|30Y(?:美债)?(?:收益率|国债)|30年期美债(?:收益率)?)",
     "cur": "macro.data.UST_30Y.value", "prev": "macro.data.UST_30Y.prev",
     "unit": "%", "tol": 0.005},
    {"id": "HY_OAS", "alias": r"(?:HY\s*OAS|高收益(?:债)?利差|高收益OAS)",
     "cur": "macro.data.HY_OAS.value", "prev": "macro.data.HY_OAS.prev",
     "unit": "%", "tol": 0.10},
    {"id": "CCC_OAS", "alias": r"(?:CCC\s*OAS|CCC利差|CCC(?:评级)?利差)",
     "cur": "macro.data.CCC_OAS.value", "prev": "macro.data.CCC_OAS.prev",
     "unit": "%", "tol": 0.10},
    {"id": "UNRATE", "alias": r"失业率",
     "cur": "rate_economy.real_economy.UNRATE.value", "prev": "rate_economy.real_economy.UNRATE.prev_value",
     "unit": "%", "tol": 0.05},
    {"id": "UMCSENT", "alias": r"(?:消费者信心|密歇根信心|Michigan指数)",
     "cur": "rate_economy.real_economy.UMCSENT.value", "prev": "rate_economy.real_economy.UMCSENT.prev_value",
     "unit": "指数", "tol": 0.5},
]

# 报告引用前值的合法话术: 窗口内出现这些词时,引用prev不算"前值当现值"
_PREV_CONTEXT_RE = re.compile(r"上周|前值|前期|上一?期|previous|prior|prev\b|较[^。；\n]{0,6}变动|变化|环比|同比|从")
# 阈值/条件句语境: "CCC OAS≥10.0""若回落至9.5下方"等引用的是触发器规格而非市场观测值,
# 不参与现值/前值判定(只在既非现值又非前值时豁免报错,不影响✅路径)
_SPEC_CONTEXT_RE = re.compile(r"[≥≤<>]|若|假设|回落|突破|跌破|升破|回升|升至|高于|低于|超过|不及|收复|回到|触及|上方|下方|以内|以上|以下|目标|阈值|触发")


def _indicator_report_values(report_text, spec):
    """返回[(数值, 前值/变化语境, 阈值/条件语境)] — 逐数值判定语境(局部前视12字符)。

    语境随数值走,不整窗共享: "周变化-0.01%中,实际利率(TIPS 2.93%,-0.01%)"里
    2.93是水平断言(不得因句中"变化"二字豁免), -0.01才是变化值。
    """
    hits = []
    for m in re.finditer(spec["alias"], report_text):
        # 取别名后40字符窗口(约到句读),遇相邻指标名截断(防串到BEI/30Y等的数值)
        win = report_text[m.end():m.end() + 40]
        stop = re.search(r"[。；;\n]", win)
        if stop:
            win = win[:stop.start()]
        stop2 = re.search(r"BEI|CPI|PCE|TIPS|CCC|OAS|UNRATE|UMCSENT|VIX|SPX|GOLD|WTI|非农|失业率|消费者信心|密歇根|[0-9]+Y", win)
        if stop2:
            win = win[:stop2.start()]
        for nm in re.finditer(r"[0-9]+\.[0-9]+", win):
            v = float(nm.group())
            if abs(v) >= 10000:
                continue
            local = win[max(0, nm.start() - 12):nm.start()]
            hits.append((v,
                         bool(_PREV_CONTEXT_RE.search(local)),
                         bool(_SPEC_CONTEXT_RE.search(local))))
    return hits


def check_indicators(report_text, anchors):
    """指标ID联合校验: 报告数值 ↔ 锚点(现值/前值)逐数值比对(语境随数值走)。
    规则:
      - 数值(或bp归一后) ≈ cur → ✅(观测日附注)
      - 数值 ≈ prev 且该数值局部前值语境 → ✅(前值引用正确)
      - 只命中 prev、非前值语境、非阈值语境 → 🚨前值当现值(FAIL级)
      - 阈值/条件语境(≥目标值、"若回落至X") → ⬜跳过(引用的是触发器规格)
      - 变化/前值语境(环比、3月变化)引用变化值 → ⬜跳过(非水平值断言)
      - 都不命中且非任何豁免语境 → ❌偏差
    """
    warnings = []
    for spec in INDICATOR_SPECS:
        cur_info = anchors.get(spec["cur"])
        prev_info = anchors.get(spec["prev"])
        if not cur_info:
            continue  # 锚点侧无此指标,跳过(不误报)
        cur, prev = cur_info["value"], (prev_info or {}).get("value")
        obs = cur_info.get("obs_date", "?")
        for num, is_prev_ctx, is_spec_ctx in _indicator_report_values(report_text, spec):
            # bp形态归一: "1229bp"式引用 ↔ 锚点12.29(%)
            bp = num / 100 if (spec["unit"] == "%" and num > 60) else num
            near_cur = abs(num - cur) <= spec["tol"] or abs(bp - cur) <= spec["tol"]
            near_prev = prev is not None and (
                abs(num - prev) <= spec["tol"] or abs(bp - prev) <= spec["tol"])
            if near_cur:
                print(f"  ✅ [{spec['id']}] 报告值≈现值{cur}{spec['unit']} (观测日{obs})")
            elif near_prev and is_prev_ctx:
                print(f"  ✅ [{spec['id']}] 前值语境引用{prev}{spec['unit']}正确 (现值应为{cur})")
            elif is_spec_ctx:
                print(f"  ⬜ [{spec['id']}] 阈值/条件语境引用[{num}],跳过现值判定")
            elif near_prev:
                msg = (f"🚨 前值当现值 [{spec['id']}]: 报告引用{num}{spec['unit']}为上周前值{prev}"
                       f" — 本周现值是{cur}{spec['unit']}(观测日{obs}),当期值引用错误")
                warnings.append(msg)
                print(f"  {msg}")
            elif is_prev_ctx:
                print(f"  ⬜ [{spec['id']}] 变化/前值语境引用[{num}],非水平值断言,跳过")
            elif prev is not None and abs(abs(num) - abs(cur - prev)) <= max(spec["tol"], 0.05):
                print(f"  ⬜ [{spec['id']}] 周变化值[{num}](=|现值-前值|),非水平断言,跳过")
            elif spec["unit"] == "%" and abs(num) <= 0.5:
                print(f"  ⬜ [{spec['id']}] 小幅变化值[{num}](如周环比),非水平断言,跳过")
            else:
                msg = (f"❌ [{spec['id']}] 偏差: 报告值{num}{spec['unit']} vs 锚点现值{cur}"
                       f"/前值{prev} 均不匹配(容差{spec['tol']})")
                warnings.append(msg)
                print(f"  {msg}")
    return warnings


# ============================================================================
# 校验分级(第二轮审查#4): PASS / DEGRADED / FAIL
#   FAIL     → 禁止一切长期状态回写(thesis/allocation/prediction)
#   DEGRADED → 数字已验证但存在样式类警告(口径标注/禁语/时点提示),允许回写
#   PASS     → 干净
# ============================================================================
def classify_result(has_anchors, anchors_same_day, warnings, numeric_errors):
    """返回 (classification, reason)。numeric_errors由调用方按其门禁谓词计算。"""
    if not has_anchors:
        return "FAIL", "无锚点文件,数字未经证实"
    if not anchors_same_day:
        return "FAIL", "锚点非报告同日,数字未经证实"
    if numeric_errors:
        return "FAIL", "存在数值类错误(严重错误/偏差/前值当现值)"
    if warnings:
        return "DEGRADED", f"{len(warnings)}项非数值警告(口径/禁语/时点提示)"
    return "PASS", ""


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

# ── 逐指标新鲜度规则(第三轮P0-4): 不得对所有指标用统一过期天数 ──────────────
# 时点口径(如实声明): 本系统可得 observation_date(观测日)与 as_of(采集日=研究截止);
# release_date(发布时间)采集端无此字段 — 月度序列的max_lag已含正常发布滞后(如UNRATE
# 次月初发布→45天上限),即以 lag=as_of−obs_date 的上界近似发布延迟。
# 规则按指标key模式匹配,先命中先用; 未命中者默认14天。
FRESHNESS_RULES = [
    (re.compile(r'\.close$|\.pct_change$|\.change$'), 5, '日频行情'),
    (re.compile(r'^macro\.data\.'), 7, '日频宏观(FRED)'),
    (re.compile(r'^rate_economy\.'), 45, '月度序列(含发布滞后)'),
    (re.compile(r'^china\.'), 7, 'A股日频'),
    (re.compile(r'^scorecard\.'), 10, '周度评分卡'),
]
DEFAULT_MAX_LAG_DAYS = 14


def freshness_rule_for(anchor_key):
    """返回(最大滞后天数, 规则名); 按key模式逐指标匹配。"""
    for pat, max_lag, name in FRESHNESS_RULES:
        if pat.search(anchor_key):
            return max_lag, name
    return DEFAULT_MAX_LAG_DAYS, '默认'


def is_fresh_anchor(anchor_key, info, as_of_date):
    """逐指标新鲜度判定: 观测日距研究截止日(as_of)不超过该指标的规则上限。
    无观测日的锚点无法判龄 → 返回True(新鲜),由数值/观测日联合校验另行把关。
    过期指标不得作为当前有效证据驱动配置观点变化(引擎侧调用)。"""
    if not isinstance(info, dict):
        return True
    obs = info.get('obs_date')
    if not obs or not as_of_date:
        return True
    try:
        from datetime import date
        o = date(int(str(obs)[:4]), int(str(obs)[5:7]), int(str(obs)[8:10]))
        a = date(int(str(as_of_date)[:4]), int(str(as_of_date)[5:7]), int(str(as_of_date)[8:10]))
    except (ValueError, TypeError, IndexError):
        return True
    max_lag, _ = freshness_rule_for(anchor_key)
    return (a - o).days <= max_lag


def stale_anchor_warning(anchor_key, info, as_of_date):
    """过期锚点警告(⚠️级): 供校验报告与引擎证据核验共用。"""
    if is_fresh_anchor(anchor_key, info, as_of_date):
        return None
    obs = info.get('obs_date')
    from datetime import date
    try:
        o = date(int(str(obs)[:4]), int(str(obs)[5:7]), int(str(obs)[8:10]))
        a = date(int(str(as_of_date)[:4]), int(str(as_of_date)[5:7]), int(str(as_of_date)[8:10]))
        lag = (a - o).days
    except (ValueError, TypeError, IndexError):
        return None
    max_lag, name = freshness_rule_for(anchor_key)
    return (f"⚠️ 数据过期 {anchor_key}: 观测日{obs}距研究截止{as_of_date}滞后{lag}天"
            f" 超过{name}规则上限{max_lag}天 — 不得作为当前有效证据")

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

    # === 1.5 指标ID联合校验(第二轮#6/#8: 现值/前值区分) ===
    print("\n🔎 指标ID联合校验(现值/前值):")
    warnings.extend(check_indicators(report_text, anchors))

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
