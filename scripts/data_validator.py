#!/usr/bin/env python3
"""
数据校验器 v2.0
修复：
- 核心比对引擎：真正计算偏差百分比并判断是否超标
- 单位归一化：15.8万/158K/158,000 → 统一为基础数值
- 变化率校验：周涨跌幅也作为锚点
- 空锚点硬中断：锚点不足时中断流水线

IA-P0-1(2026-10-27)锚点来源分层:
- 主路径: 消费研究快照产出的当日锚点(anchors_YYYYMMDD.json + .meta.json,
  source=snapshot)——不重写该文件及其meta(快照构建器是唯一写入方);
- 遗留路径: 快照缺席时拍平采集JSON自证锚点(legacy)——写入时meta sidecar
  显式标注source=legacy,观察器/报告入口据此拒绝其进入正式研究批次
  (legacy锚点未经Gate A快照链验证,不得产出合格正式输出);
- 报告glob排除 _annotated(标注版)与 _UNVALIDATED(IA-P0-1未通过Gate B的
  待验证报告),二者均非合格正式报告,不得作为"最新报告"被比对/续写。
"""
import os, sys, re, json, glob
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import research_provenance as rp
import freshness_policy as fp

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
            # FIX1-01(DEF-001): 严格解析——'2026-10-23INVALID'等带任意后缀的
            # 字符串不得经[:10]截断洗白成合法观测日(完整时间戳合法则取日期部分)。
            def _norm_date(s):
                if not isinstance(s, str):
                    return None
                t = s.strip()
                if len(t) == 8 and t.isdigit():
                    t = f"{t[:4]}-{t[4:6]}-{t[6:]}"
                d = fp.parse_instant(t)
                return d.isoformat() if d else None

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
# 第七轮Gate B: 第6字段=canonical身份标记(锚点key须包含的指标身份子串);
# 仅与canonical锚点比对,贴近同族其他锚点=疑似指标混淆。
REPORT_CHECKS = [
    # (名称, 报告中的正则, 锚点key的匹配模式, 容差%, 是否为百分比值, canonical)
    ("SPX收盘", r'(?:SPX|标普500)[^0-9%]*?([0-9]{3,5}(?:\.[0-9]+)?)', r'global_market.*(?:SPX|SPY|sp500).*(?:close|price|收盘)', 0.5, False, 'SPX'),
    ("WTI油价", r'(?:WTI(?![a-zA-Z])|油价)\s*(?:收于|收盘|价格|现价|为|至)?\s*\$?([0-9]{2,3}\.[0-9]+)(?!\s*%)', r'global_market.*(?:WTI|CL|oil|原油).*(?:close|price|收盘)', 1.0, False, 'WTI'),
    ("黄金价格", r'(?:黄金|GOLD(?![a-zA-Z])|XAU)[^0-9%]*?([0-9]{3,5}(?:\.[0-9]+)?)(?!\s*[%年])', r'global_market.*(?:GOLD|GC|gold|黄金).*(?:close|price|收盘)', 0.5, False, 'GOLD'),
    ("DXY", r'(?:DXY(?![a-zA-Z])|美元指数)[^0-9%]*?([0-9]{2,3}\.[0-9]+)(?!\s*%)', r'global_market.*(?:DXY|美元).*(?:close|price|收盘)', 0.5, False, 'DXY'),
    ("VIX", r'VIX(?![a-zA-Z])[^0-9%]*?([0-9]{1,3}\.[0-9]+)(?!\s*%)', r'global_market.*VIX.*(?:close|price|收盘)', 2.0, False, 'VIX'),
    ("BTC", r'(?:BTC(?![a-zA-Z])|比特币)[^0-9%]*?([0-9]{4,6}(?:\.[0-9]+)?)(?!\s*%)', r'global_market.*(?:BTC|bitcoin).*(?:close|price|收盘)', 1.0, False, 'BTC'),
    ("10Y收益率", r'(?:UST\s*10Y|10Y\s*(?:收益率|利率|国债))[^0-9]*?([0-9]\.[0-9]{2,3})\s*%', r'macro.*(?:UST_10Y|10Y|GS10|DGS10).*(?:value|收益率)', 3.5, True, 'UST_10Y'),
    ("30Y收益率", r'(?:UST\s*30Y|30Y\s*(?:收益率|利率|国债))[^0-9]*?([0-9]\.[0-9]{2,3})\s*%', r'macro.*(?:UST_30Y|30Y|GS30|DGS30).*(?:value|收益率)', 2.0, True, 'UST_30Y'),
    # CCC水平断言须带单位(%或bp) — 无单位裸数字多为行文元数据(星级/置信/论点编号),
    # 误纳即产生"疑似指标混淆"假阳性。bp形态由两捕获组区分,取值时÷100归一为%
    ("CCC_OAS", r'CCC(?![a-zA-Z])[^0-9%.。；;\n]*?(?:([0-9]{1,2}\.[0-9]+)\s*%|([0-9]{3,5})\s*bp)', r'macro.*(?:CCC|ccc).*(?:value|OAS|利差)', 2.0, True, 'CCC_OAS'),
    ("HY_OAS", r'(?:HY\s*OAS|高收益利差)[^0-9]*?(?<!-)([0-9]\.[0-9]{2,3})\s*%', r'macro.*(?:HY|high.yield|高收益).*(?:value|OAS|利差)', 2.0, True, 'HY_OAS'),
    ("失业率", r'失业率(?!\s*(?:变动|变化|change|delta))[^0-9%]*?([3-9]\.[0-9])\s*%', r'rate_economy.*(?:UNRATE|失业率|unemployment).*(?:value|latest)', 0, True, 'UNRATE'),
    ("消费者信心", r'(?:消费者信心|Michigan|密歇根)[^0-9]*?([0-9]{2,3}\.[0-9])', r'rate_economy.*(?:UMCSENT|消费者信心|michigan|confidence).*(?:value|latest)', 1.0, False, 'UMCSENT'),
    ("上证指数", r'(?:上证|上证指数|SSE(?![a-zA-Z]))[^0-9%]*?([0-9]{3,4}\.[0-9]+)(?!\s*%)', r'china.*(?:上证|SSE|000001).*(?:close|收盘)', 5.0, False, ('上证指数', '000001')),
]

# 周变化率检查(第5字段=canonical;锚点取.week_chg=引擎统一口径的周变化)
# 间隔类排除句读(，。；、)与%, 变化值须与指标同小句 — 防跨小句串到相邻资产数值
# (实战: "WTI周+5.12%...；美股分化(SPX -0.27%但NDX -2.57%)"旧式把NDX当WTI周变化)
CHANGE_CHECKS = [
    # (名称, 报告中变化率正则, 锚点key模式, 容差绝对值pp, canonical)
    ("WTI周涨跌", r'(?:WTI(?![a-zA-Z])|油价)[^)。，；、%]{0,40}?([+-]?[0-9]{1,3}\.[0-9]+)\s*%', r'global_market.*(?:WTI|CL|oil).*(?:change|涨跌|pct|week_chg)', 0.6, 'WTI'),
    ("黄金周涨跌", r'(?:黄金|GOLD(?![a-zA-Z]))[^)。，；、%]{0,40}?([+-]?[0-9]{1,3}\.[0-9]+)\s*%', r'global_market.*(?:GOLD|GC|gold|黄金).*(?:change|涨跌|pct|week_chg)', 0.6, 'GOLD'),
    ("BTC周涨跌", r'(?:BTC(?![a-zA-Z])|比特币)[^)。，；、%]{0,40}?([+-]?[0-9]{1,3}\.[0-9]+)\s*%', r'global_market.*(?:BTC|bitcoin).*(?:change|涨跌|pct|week_chg)', 0.5, 'BTC'),
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
        "patterns": [r'(?:SPX(?![a-zA-Z])|标普500)[^0-9%]*?([0-9]{3,5}(?:\.[0-9]+)?)(?!\s*%)'],
        "min_value": 2000, "max_value": 10000,
        "error_msg": "SPX收盘价应在2000-10000范围"
    },
    "WTI范围": {
        "patterns": [r'(?:WTI(?![a-zA-Z])|油价)\s*(?:收于|收盘|价格|现价|为)?\s*\$?([0-9]{2,3}\.[0-9]+)(?!\s*%)'],
        "min_value": 20, "max_value": 200,
        "error_msg": "WTI价格应在$20-$200范围"
    },
    "VIX范围": {
        "patterns": [r'VIX(?![a-zA-Z])[^0-9%]*?([0-9]{1,3}\.[0-9]+)(?!\s*%)'],
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
_SPEC_CONTEXT_RE = re.compile(r"[≥≤<>]|若|假设|回落|突破|跌破|升破|回升|升至|高于|低于|超过|不及|收复|回到|触及|上方|下方|以内|以上|以下|目标|阈值|触发|站上|站稳|关口|恐慌线|警戒线|红线|支撑|阻力|维持|概率|破[0-9]")


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
            # 第七轮Gate B: 报告确实引用了该指标数值但锚点缺席 → 待复核(不静默跳过)
            hits = _indicator_report_values(report_text, spec)
            if hits:
                msg = (f"⚠️ 待复核 [{spec['id']}]: 报告引用{len(hits)}处数值,当日锚点缺该指标"
                       f"(不可核验,发布前须人工对照独立来源)")
                warnings.append(msg)
                print(f"  {msg}")
            continue
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


def find_latest_report_for_validation(weekly_dir):
    """FIX3-02(F2-NEW-002): 校验对象发现——正式性由可验证的已发布状态决定。

    先取最新**已发布合格**正式周报(rp.latest_formal_weekly_report: 发布状态
    published=True+final_quality∈(PASS,DEGRADED)+身份一致+内容摘要重算一致);
    无合格正式报告时降级最新**未验证档案**(规范文件名;调用方须显式标注——校验
    结果不构成合格认证)。返回(path, 'formal'|'archive')或(None, 原因)。"""
    view, reason = rp.latest_formal_weekly_report(weekly_dir)
    if view is not None:
        return view['path'], 'formal'
    arch = rp.latest_archive_weekly_report(weekly_dir)
    if arch:
        return os.path.join(weekly_dir, arch), 'archive'
    return None, reason


def find_anchor_value(anchors, key_pattern):
    """根据正则模式在锚点中查找匹配的值"""
    import re as _re
    matches = []
    for key, info in anchors.items():
        if _re.search(key_pattern, key, _re.IGNORECASE):
            matches.append((key, info['value']))
    return matches


# ── Gate B身份解析(第七轮P0) ─────────────────────────────────────────
# 旧实现取"与报告值最接近的锚点"再判容差 → 数值碰巧贴近同族错误指标(如SPY/前值/
# 盘中值)也会通过。身份纪律: 每个校验项声明canonical标记(指标身份),只与canonical
# 锚点比对;贴近非canonical锚点=疑似指标混淆(🚨),绝不放行。
def resolve_check_anchors(anchors, key_pattern, canonical, require=None,
                          exclude=('prev', 'high', 'low', 'mom_', 'yoy_', 'mtd_', 'ytd_',
                                   'week_chg')):
    """返回(primary_tuple, others)。

    primary = 匹配key_pattern且含canonical标记的当期水平锚点(排除前值/派生/盘中);
    others = 同pattern下非canonical锚点(仅用于"疑似混淆"判定,不作通过依据)。
    canonical/require均可是str或tuple(任一子串命中即可 — 兼容旧采集格式键名)。
    """
    import re as _re

    def _any(tok):
        toks = tok if isinstance(tok, tuple) else (tok,)
        return any(t.lower() in key.lower() for t in toks)

    prim, others = None, []
    for key, info in anchors.items():
        if not _re.search(key_pattern, key, _re.IGNORECASE):
            continue
        if require and not _any(require):
            continue
        if not require and any(t in key for t in exclude):
            continue
        entry = (key, info['value'])
        if _any(canonical):
            prim = entry
        else:
            others.append(entry)
    return prim, others


# 日频行情源: 观测日不应明显滞后于报告日(月度FRED序列天然滞后,免检)
DAILY_SOURCES = ('global_market', 'china')
MAX_STALE_DAYS = 5

# ── IA-P0-2-W2: 统一时效规则(单一来源=注册表已批准策略,经freshness_policy) ──
# 旧prefix规则废除(W2-DEF-002): macro月度枚举表(漏INDPRO/JTSJOL/RSAFS/UMCSENT,
# 'WTI'键从未匹配实际键WTI_SPOT_M)、rate_economy.*一律月度45(把日频DFF/DFEDTARU/
# DFEDTARL误判月频)、china一律7(与注册表5/10分叉)、未映射默认14信任。
# 现行规则: 锚点身份由canonical键映射(镜像snapshot_builder构造规则)+锚点自带
# metric_id交叉核验决定(冲突以canonical为准,caller身份不得授权放宽);窗口与频率
# 由注册表已批准策略决定(与Gate A/fact_engine同一份)。未映射锚点fail-closed,
# 14仅作为freshness_rule_for的遗留诊断兼容值保留(非时效认证)。
UNMAPPED_LEGACY_DIAGNOSTIC = 14   # 第三轮P0-4遗留诊断值:仅诊断兼容,非认证


def metric_frequency(anchor_key, info=None):
    """指标频率查询(W2统一): 返回(freq, max_lag_days, 说明)。
    身份: 锚点键canonical映射+来源家族绑定→注册表已批准策略;info.metric_id仅交叉核验。
    scorecard为报告内部推导(非注册表指标),维持周度10天遗留规则并显式标注。
    未映射(UNMAPPED)或身份不可认证(UNVERIFIED: 来源家族不符/身份冲突)锚点
    返回('unknown', 14, 说明)——诊断兼容值,fail-closed(is_fresh_anchor直接False)。"""
    ident = fp.verify_anchor_identity(anchor_key, info)
    if ident['status'] == 'MAPPED':
        pol = fp.policy_for(ident['metric_id'])
        if pol is not None:
            note = f"注册表已批准窗口({ident['metric_id']};{ident['basis']})"
            return pol['frequency'], pol['window'], note
    elif ident['family'] == 'scorecard' or (isinstance(anchor_key, str)
                                            and anchor_key.startswith('scorecard.')):
        return 'weekly', 10, '周度评分卡(报告内部推导,非注册表指标;遗留规则)'
    if ident['status'] == 'UNVERIFIED':
        return 'unknown', UNMAPPED_LEGACY_DIAGNOSTIC, \
            f"UNVERIFIED:{ident['basis']}" + (f";{ident['conflict']}" if ident.get('conflict') else "")
    return 'unknown', UNMAPPED_LEGACY_DIAGNOSTIC, \
        'UNMAPPED:锚点未映射到注册表指标(遗留诊断值,非时效认证)'


def metric_registry_info(anchor_key, info=None):
    """指标元数据注册表条目(供校验日志/证据核验披露):
    {metric_id, source, frequency, max_lag_days, observation_date, as_of, retrieved_at,
     release_date, release_provenance, identity_status, identity_basis,
     caller_metric_id_conflict}。
    FIX1-01: 全部日期严格解析(fp.parse_instant,整串验证;不[:10]截断洗白),
    非法输入如实披露为非法,不得转成合法日期。
    FIX1-02: release_date仅披露锚点元数据实际携带的值(采集端目前不携带→
    RELEASE_UNKNOWN,不伪造);披露值标注provenance——Gate B不做来源证明,
    未独立核验,不得表述为已认证发布时间。"""
    ident = fp.verify_anchor_identity(anchor_key, info)
    info = info or {}
    od = fp.parse_instant(info.get('obs_date'))
    ao = fp.parse_instant(info.get('as_of'))
    rel_raw = info.get('release_date')
    rel = fp.parse_instant(rel_raw) if rel_raw is not None else None
    base = {'observation_date': od.isoformat() if od else None,
            'release_date': rel.isoformat() if rel else None,
            'release_provenance': ('anchor_metadata(未独立核验;仅拒绝性消费)'
                                   if rel else
                                   'RELEASE_UNKNOWN(采集端未携带release_date,不伪造发布日期)'),
            'retrieved_at': ao.isoformat() if ao else None,
            'as_of': ao.isoformat() if ao else None,
            'metric_id': ident['metric_id'] or anchor_key,
            'source': anchor_key.split('.')[0] if isinstance(anchor_key, str) else None,
            'identity_status': ident['status'],
            'identity_reason': ident.get('reason'),
            'identity_basis': ident['basis'],
            'caller_metric_id_conflict': ident.get('conflict')}
    if rel_raw is not None and rel is None:
        base['note'] = f"release_date非法:{rel_raw!r}(不截断洗白)"
    pol = fp.policy_for(ident['metric_id']) if ident['metric_id'] else None
    if ident['status'] == 'MAPPED' and pol is not None:
        base.update({'source': 'metric_registry',
                     'frequency': pol['frequency'],
                     'max_lag_days': pol['window'],
                     'note': (base.get('note', '') + ';'
                              if base.get('note') else '')
                             + f"{ident['basis']};已批准窗口{pol['window']}天({pol['frequency']}频)"})
    else:
        freq, max_lag, desc = metric_frequency(anchor_key, info)
        base.update({'frequency': freq, 'max_lag_days': max_lag,
                     'note': (base.get('note', '') + ';' if base.get('note') else '') + desc})
    return base


# 兼容旧接口: 逐指标新鲜度规则(第三轮P0-4) — 现由metric_frequency驱动
FRESHNESS_RULES = []  # 保留符号避免旧引用报错; 逻辑已并入metric_frequency


def freshness_rule_for(anchor_key):
    """返回(最大滞后天数, 规则名); 按指标频率注册表逐指标匹配。"""
    _freq, max_lag, desc = metric_frequency(anchor_key)
    return max_lag, desc


def anchor_time_qualification(anchor_key, info, as_of_date):
    """锚点结构化时间资格(W2-FIX4-01: 轻量适配接口,非第二套时间比较器):
    观测新鲜度(A/C问)与点时认证(B问)**分离返回**,全部复用fp共享原语
    (verify_anchor_identity+assess)与同一份已批准时效策略——数值/观测核验
    与历史点时认证两个维度不得相互冒充。
    返回:
      identity                {status: MAPPED/UNMAPPED/UNVERIFIED, metric_id, reason}
      observation_freshness   {fresh: bool, status, lag_days, window}
                              (status: FRESH/STALE/FUTURE_DATE/NOT_OBSERVED/
                               INVALID_DATE/UNREGISTERED/NOT_AVAILABLE_AT_AS_OF/
                               INVALID_RELEASE;UNMAPPED/身份不可认证时为
                               UNMAPPED/IDENTITY_UNVERIFIED)
      point_in_time           {status, granularity, release_date, reason}
                              OK/POINT_IN_TIME_UNCERTIFIED/RELEASE_UNKNOWN/
                              RELEASE_AFTER_AS_OF/INVALID/RELEASE_BEFORE_OBS;
                              身份不可认证时NOT_ASSESSABLE
      point_in_time_certified bool — 仅point_in_time.status==OK;且OK只证明
                              "锚点元数据声明的发布时间不晚于研究截止"
                              (release_date未独立核验,见reason),不冒充外部独立认证
    is_fresh_anchor为本接口观测维度的布尔投影(同一判定,单一来源)。"""
    out = {'identity': {'status': 'NOT_ASSESSABLE', 'metric_id': None,
                        'reason': None},
           'observation_freshness': {'fresh': False, 'status': None,
                                     'lag_days': None, 'window': None},
           'point_in_time': {'status': 'NOT_ASSESSABLE', 'granularity': None,
                             'release_date': None, 'reason': None},
           'point_in_time_certified': False}
    if not isinstance(info, dict):
        out['observation_freshness']['status'] = 'INVALID_INFO'
        out['point_in_time']['reason'] = '锚点信息非法(非对象),无法判定时间资格'
        return out
    # scorecard: 报告内部推导(非注册表指标)——遗留周度10天规则,日期同样严格;
    # 无外部发布事实→点时如实RELEASE_UNKNOWN,绝不认证
    if isinstance(anchor_key, str) and anchor_key.startswith('scorecard.'):
        o = fp.parse_instant(info.get('obs_date'))
        a = fp.parse_instant(as_of_date)
        ok = bool(o and a and o <= a and (a - o).days <= 10)
        out['identity'] = {'status': 'MAPPED', 'metric_id': anchor_key,
                           'reason': 'scorecard报告内部推导项(遗留周度规则)'}
        out['observation_freshness'] = {
            'fresh': ok, 'status': 'FRESH' if ok else 'STALE',
            'lag_days': (a - o).days if (o and a) else None, 'window': 10}
        out['point_in_time'] = {
            'status': 'RELEASE_UNKNOWN', 'granularity': None,
            'release_date': None,
            'reason': '报告内部推导项,无外部发布事实,点时不可认证'}
        return out
    ident = fp.verify_anchor_identity(anchor_key, info)
    out['identity'] = {'status': ident['status'], 'metric_id': ident['metric_id'],
                       'reason': ident['reason']}
    if ident['status'] != 'MAPPED':
        # UNMAPPED与UNVERIFIED均fail-closed(FIX1-03): 不授予任何时间资格
        out['observation_freshness']['status'] = (
            'UNMAPPED' if ident['status'] == 'UNMAPPED' else 'IDENTITY_UNVERIFIED')
        out['point_in_time']['reason'] = (
            f"锚点身份不可认证({ident['reason']}"
            + (f":{ident['conflict']}" if ident.get('conflict') else '')
            + "),不得授予任何时间资格")
        return out
    v = fp.assess(ident['metric_id'], info.get('obs_date'), as_of_date,
                  release_date=info.get('release_date'))
    pit = v['point_in_time']
    if pit.get('status') == 'OK':
        reason = (f"发布{pit.get('release_date')}不晚于研究截止"
                  f"({pit.get('detail')});锚点元数据声明,未独立核验")
    else:
        reason = (pit.get('detail') or pit.get('note')
                  or (v['reasons'][0] if v.get('reasons') else None))
    out['observation_freshness'] = {
        'fresh': bool(v['fresh']), 'status': v['status'],
        'lag_days': v.get('lag_days'), 'window': v.get('window')}
    out['point_in_time'] = {
        'status': pit.get('status'), 'granularity': pit.get('granularity'),
        'release_date': pit.get('release_date'), 'reason': reason}
    out['point_in_time_certified'] = pit.get('status') == 'OK'
    return out


def is_fresh_anchor(anchor_key, info, as_of_date):
    """逐指标新鲜度判定(W2统一+FIX1-01/02/03): 完全消费fp共享原语——
    身份(canonical键映射+来源家族绑定)→三问分离assess(已观测/点时已发布/新鲜),
    与Gate A同一份政策与同一套严格日期解析。
    - 未映射(UNMAPPED)或身份不可认证(UNVERIFIED: 来源家族不符/身份冲突)
      → False(fail-closed;scorecard等报告内部推导项除外,维持遗留周度规则)
    - 非法日期('2026-10-23INVALID'/'2026-02-30'/缺观测/非法研究截止)→ False
      (FIX1-01: 不再[:10]截断洗白;错误原因见stale_anchor_warning)
    - 未来观测 → False;已知发布日晚于研究截止(NOT_AVAILABLE_AT_AS_OF)→ False
      (FIX1-02: 锚点元数据携带release_date时进入点时判断——仅拒绝性消费:
      该字段只可能使判定更严(发布在未来→拒),缺失时与既有RELEASE_UNKNOWN
      路径一致,调用方伪造发布日期无法借此放宽认证)
    过期指标不得作为当前有效证据。
    W2-FIX4-01: 判定本体在anchor_time_qualification(单一来源),此处为观测
    新鲜维度的布尔投影——点时认证状态须经结构化接口获取,布尔不得冒充。"""
    return anchor_time_qualification(anchor_key, info,
                                     as_of_date)['observation_freshness']['fresh']


def stale_anchor_warning(anchor_key, info, as_of_date):
    """过期/无法判龄/身份不可认证锚点警告(⚠️级): 供校验报告与引擎证据核验共用。
    FIX1-01: 日期严格解析,非法输入如实披露为非法(不截断洗白);
    FIX1-02: 已知发布日晚于研究截止→点时不可得警告;
    FIX1-03: 来源家族不符/身份冲突→身份不可认证(UNVERIFIED)警告。"""
    if is_fresh_anchor(anchor_key, info, as_of_date):
        return None
    if not isinstance(info, dict):
        return f"⚠️ 无法判龄 {anchor_key}: 锚点信息非法(非对象) — 不得默认作为当前有效证据"
    if isinstance(anchor_key, str) and anchor_key.startswith('scorecard.'):
        return (f"⚠️ 数据过期 {anchor_key}: 评分卡锚点观测日缺失/非法/超出遗留周度10天窗"
                f" — 报告内部推导项,待验证")
    ident = fp.verify_anchor_identity(anchor_key, info)
    if ident['status'] == 'UNMAPPED':
        return (f"⚠️ 无法认证时效 {anchor_key}: 锚点未映射到注册表指标(UNMAPPED)"
                f" — 不得默认作为当前有效证据")
    if ident['status'] == 'UNVERIFIED':
        why = ('身份冲突' if ident.get('reason') == 'identity_conflict' else '来源家族不符')
        return (f"⚠️ 无法认证时效 {anchor_key}: {why}({ident['basis']}"
                + (f";{ident['conflict']}" if ident.get('conflict') else "")
                + f") — 指标注册≠该通道可生成,不得默认作为当前有效证据")
    v = fp.assess(ident['metric_id'], info.get('obs_date'), as_of_date,
                  release_date=info.get('release_date'))
    st = v['status']
    if st in ('NOT_OBSERVED', 'INVALID_DATE'):
        return (f"⚠️ 无法判龄 {anchor_key}: 观测日缺失或非法('{info.get('obs_date')}')"
                f"或研究截止非法('{as_of_date}') — 待验证,不得默认作为当前有效证据")
    if st == 'FUTURE_DATE':
        return (f"⚠️ 未来数据 {anchor_key}: 观测日{v['obs_date']}晚于研究截止{v['as_of']}"
                f" — 非法时点,不得使用")
    if st == 'NOT_AVAILABLE_AT_AS_OF':
        pit = v['point_in_time']
        # FIX2-02: 披露**实际时间关系**(完整时刻+粒度+差值),不得只显示两个
        # 相同日期——同日"截止08:00/发布20:00"必须能看出先后依据
        r = pit.get('release_date')
        gran = pit.get('granularity') or 'DAY'
        det = pit.get('detail') or ''
        return (f"⚠️ 点时不可得 {anchor_key}: 已知发布{r}晚于研究截止"
                f"{as_of_date!r}[{gran}{';' + det if det else ''}]"
                f"(NOT_AVAILABLE_AT_AS_OF) — as_of时点该值不可得,不得作为当前研究证据")
    if st == 'INVALID_RELEASE':
        return (f"⚠️ 发布时间非法 {anchor_key}: release_date={info.get('release_date')!r}"
                f"(非完整ISO日期/时间戳或早于观测日) — 不得作为当前研究证据")
    # STALE(或UNREGISTERED等其余不可新鲜态)
    if st == 'STALE':
        return (f"⚠️ 数据过期 {anchor_key}: 观测日{v['obs_date']}距研究截止{v['as_of']}"
                f"滞后{v['lag_days']}天 超过注册表已批准窗口{v['window']}天"
                f"({v['frequency']}频) — 不得作为当前有效证据")
    return (f"⚠️ 无法认证时效 {anchor_key}: {v['status']}({';'.join(v['reasons'])})"
            f" — 不得默认作为当前有效证据")

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

    # Gate B全量覆盖后暴露的边界: 报告正文混有<!--ALLOCATION/PREDICTION_STATUS-->机器块,
    # 状态块中的JSON字段(id/confidence数字)不是散文数值断言,且其数值一致性由
    # 回写门禁(allocation_engine)按锚点另行核验 — 水平值/变化率扫描只针对散文。
    prose = re.sub(r'<!--.*?-->', '', report_text, flags=re.DOTALL)

    # === 1. 核心数值比对(第七轮Gate B: 全量覆盖+身份解析,不再"取最接近锚点") ===
    print("\n🔍 核心数值比对(全量覆盖: 报告每一处提及均核验):")
    for name, report_pattern, anchor_pattern, tolerance_pct, is_pct, canonical in REPORT_CHECKS:
        report_hits = list(re.finditer(report_pattern, prose, re.IGNORECASE))
        if not report_hits:
            print(f"  ⬜ {name}: 报告中未提及")
            continue

        prim, others = resolve_check_anchors(anchors, anchor_pattern, canonical)
        if prim is None:
            # 不可核验 → 待复核(如实披露,不静默跳过,不冒充通过)
            msg = (f"⚠️ 待复核 {name}: 报告提及{len(report_hits)}处数值,当日锚点缺该指标"
                   f"当期值(不可核验,发布前须人工对照独立来源)")
            warnings.append(msg)
            print(f"  {msg}")
            continue

        anchor_key, anchor_val = prim
        a_info = anchors.get(anchor_key, {})
        obs = a_info.get('obs_date', '?')
        fid = a_info.get('fact_id') or a_info.get('metric_id') or ''

        for m in report_hits:
            # 语境豁免: 阈值/目标/条件句(如"SPX收复7700""若回落至X")引用的是
            # 触发器/预测规格,不是当期水平断言 — 跳过水平值判定(与check_indicators同口径)
            # 后视仅认"紧邻"的位置词/动词("4.1%回升至""1000bp上方"),隔标点不豁免
            # ("12.52%,已远超恐慌线"中恐慌线是评述,12.52仍是水平断言)
            ctx = prose[max(0, m.start() - 12):m.start()] + m.group()
            after = prose[m.end():m.end() + 8]
            if _SPEC_CONTEXT_RE.search(ctx) or re.match(
                    r'\s*(?:回升|回落|升至|跌至|上方|下方|以上|以下|以内|关口|恐慌线|警戒线|红线)', after):
                print(f"  ⬜ {name}: 阈值/目标语境[{m.group(1)}],非水平断言,跳过")
                continue
            try:
                raw = m.group(1) if m.group(1) is not None else m.group(2)
                report_val = float(raw.replace(',', ''))
                if m.group(1) is None:      # bp形态(第二捕获组) → ÷100归一为%
                    report_val = report_val / 100.0
            except (ValueError, IndexError):
                continue
            if anchor_val == 0:
                continue

            deviation_pct = abs(report_val - anchor_val) / abs(anchor_val) * 100

            if deviation_pct <= tolerance_pct:
                print(f"  ✅ {name}: 报告={report_val} ≈ 锚点{anchor_val} ({anchor_key}"
                      + (f", 事实{fid}" if fid else "")
                      + f", 观测日{obs}, 偏差{deviation_pct:.2f}% ≤ {tolerance_pct}%)")
                # P1: 时点滞后检查(仅日频行情源,提示级)
                stale = _obs_staleness_warning(anchor_key, a_info, report_date)
                if stale:
                    warnings.append(stale)
                    print(f"  {stale}")
            else:
                # 身份判定: 与canonical不符,却贴近同族其他锚点 → 疑似指标混淆(不按最接近放行)
                # 合并写法"X/Y"(如表格行"HY/CCC | OAS 3.25%/12.82%"):
                # 本臂为同族相邻指标值,另一臂与锚点一致 → 两值各自正确,判通过
                m_next = re.match(r'\s*/\s*([0-9]{1,2}\.[0-9]+)\s*%',
                                  prose[m.end():m.end() + 14])
                if m_next:
                    other_arm = float(m_next.group(1))
                    if abs(other_arm - anchor_val) / abs(anchor_val) * 100 <= tolerance_pct:
                        print(f"  ✅ {name}: 合并写法 报告={report_val}/{other_arm},"
                              f"另一臂≈锚点{anchor_val} ({anchor_key})")
                        continue
                near_other = [k for k, v in others
                              if v and abs(report_val - v) / abs(v) * 100 <= tolerance_pct]
                if near_other:
                    msg = (f"🚨 疑似指标混淆 {name}: 报告={report_val} 与[{canonical}]锚点{anchor_val}"
                           f"偏差{deviation_pct:.2f}%>容差{tolerance_pct}%,却贴近同族锚点"
                           f"{near_other[0]}={anchors[near_other[0]]['value']} — 身份不符"
                           f"(SPX≠SPY/期货≠现货/前值≠现值),不得按'最接近锚点'放行")
                    warnings.append(msg)
                    print(f"  {msg}")
                elif deviation_pct > 20:
                    msg = (f"🚨 严重错误 {name}: 报告={report_val}, 锚点={anchor_val}"
                           f"({anchor_key}) (偏差{deviation_pct:.2f}% — 疑似指标混淆)")
                    warnings.append(msg)
                    print(f"  {msg}")
                else:
                    msg = (f"❌ {name}: 报告={report_val}, 锚点={anchor_val}({anchor_key}) "
                           f"(偏差{deviation_pct:.2f}% > 容差{tolerance_pct}%)")
                    warnings.append(msg)
                    print(f"  {msg}")

    # === 1.5 指标ID联合校验(第二轮#6/#8: 现值/前值区分) ===
    print("\n🔎 指标ID联合校验(现值/前值):")
    warnings.extend(check_indicators(report_text, anchors))

    # === 2. 周变化率比对(全量覆盖+canonical;兼容新.week_chg与旧.change键名) ===
    print("\n📈 周变化率比对:")
    for name, report_pattern, anchor_pattern, tolerance_pp, canonical in CHANGE_CHECKS:
        report_hits = list(re.finditer(report_pattern, prose, re.IGNORECASE))
        if not report_hits:
            print(f"  ⬜ {name}: 报告无数据")
            continue

        prim, others = resolve_check_anchors(anchors, anchor_pattern, canonical,
                                             require=('.week_chg', '.change'))
        if prim is None:
            msg = (f"⚠️ 待复核 {name}: 报告提及{len(report_hits)}处变化值,当日锚点缺"
                   f"该指标周变化(不可核验,发布前人工对照)")
            warnings.append(msg)
            print(f"  {msg}")
            continue

        anchor_key, anchor_val = prim
        for m in report_hits:
            # 异周期守卫: 数值前10字符含年初/同比等周期词 → 引用的是其他期间收益,
            # 非本周变化断言(如"WTI现货(YTD +70.85%)""WTI同比+59.81%"),不参与周变化比对
            pre = prose[max(0, m.start(1) - 10):m.start(1)]
            if re.search(r'YTD|ytd|MTD|mtd|YOY|yoy|MoM|mom|年初|今年|月度|当月|上月|同比|环比|三个月|六个月|3个月|6个月', pre):
                print(f"  ⬜ {name}: 异周期语境[{m.group(1)}%],非周变化断言,跳过")
                continue
            # 条件/阈值语境豁免(与水平检查同口径): "WTI 96美元若传导至BEI>2.6%"
            # 引用的是情景规格而非本周变化断言
            cctx = prose[max(0, m.start() - 12):m.start()] + m.group()
            if _SPEC_CONTEXT_RE.search(cctx):
                print(f"  ⬜ {name}: 阈值/条件语境[{m.group(1)}%],非周变化断言,跳过")
                continue
            try:
                report_val = float(m.group(1))
            except ValueError:
                continue
            deviation = abs(report_val - anchor_val)
            if deviation <= tolerance_pp:
                print(f"  ✅ {name}: 报告={report_val:+.2f}%, 锚点={anchor_val:+.2f}% ({anchor_key}, 偏差{deviation:.2f}pp ≤ {tolerance_pp}pp)")
            else:
                msg = (f"❌ {name}: 报告={report_val:+.2f}%, 锚点={anchor_val:+.2f}% ({anchor_key}, 偏差{deviation:.2f}pp > 容差{tolerance_pp}pp)")
                warnings.append(msg)
                print(f"  {msg}")

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


def save_anchors(anchors, source='legacy'):
    """落盘锚点(遗留路径专用: 拍平采集JSON的自证锚点)。
    IA-P0-1: meta sidecar标注source=legacy——未经Gate A快照链验证的锚点批次,
    观察器/报告入口据此拒绝其进入正式研究(可作诊断,不得冒充合格批次)。"""
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
        if v.get('high') is not None:
            entry['high'] = v['high']
        if v.get('low') is not None:
            entry['low'] = v['low']
        # Gate B溯源(第七轮): 事实标识/指标身份/质量随锚点落盘,校验日志可回指快照事实
        for extra in ('fact_id', 'metric_id', 'quality', 'tolerance_pct'):
            if v.get(extra) is not None:
                entry[extra] = v[extra]
        serializable[k] = entry

    path = os.path.join(data_dir, f'anchors_{today}.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2)
    rp.write_meta(path, {
        'source': source,
        'generated_by': 'data_validator(legacy)',
        'generated_at': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        'anchor_count': len(serializable),
        'note': '原始采集JSON拍平锚点,未经Gate A快照链验证,不得用于正式研究批次',
    })
    print(f"\n💾 数据锚点: {path} ({os.path.getsize(path)} bytes, {len(anchors)} 个锚点)"
          + (" [⚠️ legacy批次-已标注]" if source == 'legacy' else ""))
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
    # 第七轮重构: 优先使用研究快照产出的当日锚点(单一来源,含质量与obs_date/high/low;
    # 采集JSON拍平的同源自证锚点仅在快照缺席的旧路径使用)。
    # IA-P0-1: 快照锚点不重写(快照构建器是anchors_*.json唯一写入方,meta随之保留);
    # legacy路径落盘时meta标注source=legacy,不得冒充快照批次。
    print("\n--- Step 1: 提取数据锚点 ---")
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'daily')
    today_str = datetime.now().strftime('%Y%m%d')
    snap_anchor_path = os.path.join(data_dir, f'anchors_{today_str}.json')
    from_snapshot = os.path.exists(snap_anchor_path)
    if from_snapshot:
        with open(snap_anchor_path, 'r', encoding='utf-8') as f:
            anchors = json.load(f)
        print(f"✅ 使用研究快照锚点: {snap_anchor_path} ({len(anchors)} 个)(不重写)")
    else:
        anchors = extract_anchors_from_data()

    # 硬中断检查
    if len(anchors) < MIN_ANCHOR_COUNT:
        print(f"\n🚨 严重错误: 锚点数量 {len(anchors)} < 最低阈值 {MIN_ANCHOR_COUNT}")
        print(f"   数据源可能全部缺失，中断流水线以防止空锚点注入prompt")
        print(f"   请检查 data/daily/ 目录下的数据文件是否存在")
        sys.exit(1)

    anchor_path = snap_anchor_path if from_snapshot else save_anchors(anchors)

    # Step 2: 生成prompt插入块
    print("\n--- Step 2: 生成Prompt锚点块 ---")
    prompt_block = generate_anchor_prompt_block(anchors)
    prompt_path = os.path.join(ROOT_DIR, 'data', 'daily',
                                f'anchor_prompt_{datetime.now().strftime("%Y%m%d")}.md')
    with open(prompt_path, 'w', encoding='utf-8') as f:
        f.write(prompt_block)
    # FIX-01: prompt来源meta——记录渲染所用锚点批次与prompt实际内容摘要,
    # 报告预检读取实际文件重算并从已核验锚点确定性重建比对
    _pm = {'source': 'snapshot' if from_snapshot else 'legacy',
           'generated_by': 'data_validator', 'target_date': today_str,
           'anchors_file': os.path.basename(anchor_path),
           'prompt_digest': rp.digest_file(prompt_path)}
    if from_snapshot:
        _am = rp.load_meta(anchor_path) or {}
        _pm.update({k: _am.get(k) for k in ('snapshot_id', 'snapshot_digest', 'gate_a')})
        _pm['anchors_digest'] = rp.digest_file(anchor_path)
    rp.write_meta(prompt_path, _pm)
    print(f"💾 Prompt锚点块: {prompt_path} ({os.path.getsize(prompt_path)} bytes)")

    # Step 3: 校验最新报告
    print("\n--- Step 3: 校验最新报告 ---")
    # IA-P0-1-FIX3(FIX3-02/F2-NEW-002): 校验对象发现走find_latest_report_for_validation
    # ——正式性由发布状态决定,不由文件名决定;档案模式须显式标注未验证。
    _weekly_dir = os.path.join(ROOT_DIR, 'output', 'weekly')
    latest_report, _mode = find_latest_report_for_validation(_weekly_dir)
    if latest_report and _mode == 'formal':
        print(f"📄 校验报告(已发布合格): {latest_report}")
    elif latest_report:
        print(f"⚠️ 校验报告(未验证历史档案,无发布状态): {latest_report}")
        print("   校验结果仅供漂移监控参考,不构成合格正式认证(FIX3-02)")
    else:
        print(f"⚠️ 无可校验周报({_mode})")
    if latest_report:
        # 日期匹配: 报告记录的是其生成日观测,须用同日锚点比对;用"今日锚点vs上周报告"
        # 会把正常的数据推进误判为偏差(实战: 周六晨报(周五收盘)vs下周一锚点(周五后
        # 又有新收盘)→SPX/WTI/VIX全误报)。无同日锚点才降级用当前锚点并显式标注跨日。
        rep_anchors = anchors
        m_day = re.search(r'weekly_report_(\d{8})\.md', latest_report)
        if m_day and m_day.group(1) != today_str:
            rep_anchor_path = os.path.join(data_dir, f'anchors_{m_day.group(1)}.json')
            if os.path.exists(rep_anchor_path):
                with open(rep_anchor_path, 'r', encoding='utf-8') as f:
                    rep_anchors = json.load(f)
                print(f"📅 报告日({m_day.group(1)})≠今日 — 改用报告当日锚点: "
                      f"anchors_{m_day.group(1)}.json ({len(rep_anchors)}个)")
            else:
                print(f"⚠️ 报告日({m_day.group(1)})锚点缺席 — 跨日比对,数值漂移≠报告错误,"
                      f"偏差告警仅供漂移监控参考")
        warnings = validate_report(latest_report, rep_anchors)

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
