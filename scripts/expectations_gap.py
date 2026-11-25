# -*- coding: utf-8 -*-
"""Audit-R33 任务5: 预期差对照面——机构观点 × 同期限市场定价 × 事实(确定性, 零模型)。

审计基线 f053afe 的正式入口(research-one)现状: 一句「市场定价和机构观点之间有
哪些预期差」——计划不登记该分量,机构观点只以摘编(views_digest)随工单走,无逐行
「机构点位—同期限市场定价—事实」对照面;报告没有可复核的对照表,也没有
「证据不足」的显式缺口。

本模块(问什么答什么,逐行可复算):
  asked / is_asked    问句是否问到预期差(「预期差」,或「机构观点」与「市场定价」同问);
  build_block         观点库(发布日≤研究截止日才可见)逐条预测 → 点位解析 → 在册序列
                      映射 → 事实(截止日/发布日/到期日)→ 同期限市场定价(仅联邦基金
                      利率期货有;其余如实缺席)→ 判定 + 缺口点名 + 版本绑定;
  blocked_class       面缺口分级(判定与渲染共源: 观点库缺席/无可对照行=草稿);
  evidence_rows       机构观点行+市场定价行+事实行入证据索引(席位可引用可核);
  render_*            读者报告追加节(地图报告尾部之前;重放=report.json 纯函数)。
  问句族别分流在 research_map_planner.question_kind: 问到预期差=一律按 'map'
  (地图五面: 四地三时点/转折/机制/历史类比/事后表现 + 本面;形状判据不成立时
  地区=问句点名(否则四地全登记)、维度=显式否则全维);未问到=None(旧口径,
  归档问句零漂移)。计划键 research_plan.expectations_gap 先落 asked 标记,
  编排器以本块整体覆盖。

口径纪律(引擎规则,随面披露):
  - 市场定价=30 天期联邦基金利率期货合约月均有效利率(100−价格),**月均口径**,
    不得换算为加息/降息次数;基线=截止日有效利率(DFF),目标区间中点作对照口径。
  - 机构「某月加息 25bp」未给日内日期 → 该月月均落在 [步长/当月天数, 步长](加息
    月初→月末)这个**无效界**内都算一致(无假设界);下一个完整自然月才可与机构
    路径逐 bp 相减。
  - 预期差候选=市场月均落在无效界之外,或整月差 ≥ 半步(12.5bp);候选≠结论,是否
    成立由研究席逐行裁(supported / not_a_gap),引擎只给可复算的数。
  - 机构文字型观点(无数字)引擎不解读——须席位给出解读并标「席位推导」。
  - 无同期限市场定价的指标(增长/通胀/盈利/其他国家利率)=如实缺口,不以「当前
    事实」冒充市场定价。
"""
import calendar
import datetime
import hashlib
import json
import os
import re

SCHEMA = 'r33-expectations-gap'
KIND = 'expectations_gap'
REPORT_TITLE = '# 预期差研究(读者报告)'
DISCIPLINE = 'r33'

GAP_WORDS = ('预期差',)
VIEW_WORDS = ('机构观点', '机构看法', '机构预期', '机构分歧', '一致预期')
PRICING_WORDS = ('市场定价', '市场计价', '已计价', '市场预期', '定价了')

VIEWS_REL = 'data/institutions/views'
TARGET_MAP_REL = 'config/forecast_target_map.json'
PATH_METRIC = 'FED_FUNDS'          # 唯一有同期限市场定价的指标
PATH_INSTRUMENT = '联邦基金利率期货(30 天期;合约月均有效利率口径)'
STEP_BP = 25.0                     # 一次标准加息/降息步长
MATERIAL_GAP_BP = 12.5             # 预期差候选阈值=半步(引擎规则,披露)
BASIS_TOL_BP = 1.0                 # 基线口径差(有效利率 vs 目标区间中点)容差
RATE_TOL = 0.02                    # 利率(%)点位对账容差
BP_TOL = 2.0                       # bp 单位点位对账容差
REL_TOL = 0.005                    # 其余点位的相对容差
CURRENT_STATE_WORDS = ('当前', '会后即刻', '会议间期间', '现阶段', '目前', '现行')

BLOCK_MISSING = 'expectations_gap_block_missing'
VIEWS_ABSENT = 'expectations_gap_views_absent'
NO_COMPARABLES = 'expectations_gap_no_comparables'

_REGION_LABEL = {'US': '美国', 'CN': '中国', 'EA': '欧元区', 'JP': '日本'}
_REGION_ORDER = ('US', 'CN', 'EA', 'JP')
_CB_WORDS = {'JP': ('日本央行', '日银', 'BOJ'),
             'US': ('美联储', 'Fed', 'FOMC'),
             'EA': ('欧央行', 'ECB', '欧洲央行'),
             'CN': ('人民银行', 'PBOC', '中国央行')}

# 补充别名表(引擎模块内;冻结的 config/forecast_target_map.json 不改): 精确目标文本
# → (指标, 映射来源说明)。先于规范表命中;规范表未收录或口径错配的在此补齐。
SUPPLEMENT_TARGETS = {
    'fed_funds_target_range': (
        'DFEDTARU', 'r33_supplement(目标区间: 上限=DFEDTARU,下限=DFEDTARL)'),
    'Fed_further_hike_outlook': (
        'FED_FUNDS', 'r33_supplement(官方预测的机构记述→联邦基金有效利率路径)'),
    'fed_policy_path_baseline': (
        'FED_FUNDS', 'r33_supplement(政策路径基线→联邦基金有效利率路径)'),
    'US_10y_yield_endAug2026': ('UST_10Y', 'r33_supplement'),
    'US_10y_yield_endSep2026': ('UST_10Y', 'r33_supplement'),
    'US_HY_OAS_endSep2026': ('HY_OAS', 'r33_supplement'),
    'BOJ_policy_rate': ('JP_POLICY_RATE',
                        'r33_supplement(注册表在册的政策利率序列)'),
    'ECB_deposit_facility_rate': ('ECB_DFR', 'r33_supplement'),
    'CN_real_GDP_growth_2026': (
        'CN_REAL_GDP_YOY', 'r33_supplement(中国实际GDP同比;注册表暂无此指标→'
        '引擎如实列序列缺席)'),
    'CN_real_GDP_growth_2027': (
        'CN_REAL_GDP_YOY', 'r33_supplement(中国实际GDP同比;注册表暂无此指标→'
        '引擎如实列序列缺席)'),
    '中国GDP增长': (
        'CN_REAL_GDP_YOY', 'r33_supplement(中国实际GDP同比;注册表暂无此指标→'
        '引擎如实列序列缺席)'),
    '美国GDP增长': (
        'US_REAL_GDP', 'r33_supplement(美国实际GDP水平序列;同比由引擎严格同季'
        '派生,多值点位只列背景)'),
    'ECB_main_refi_rate': ('ECB_MRO', 'r33_supplement'),
    'SPX_12m_target': ('SPX', 'r33_supplement'),
    'SPX_EPS_2027': ('SPX_EPS', 'r33_supplement'),
    'SPX_EPS_2028': ('SPX_EPS', 'r33_supplement'),
    '标普500盈利增长': (
        'SPX_EPS', 'r33_supplement(盈利口径;规范表按「标普500」前缀命中价格指数'
        '=口径错配,本模块改指盈利)'),
    '欧元区GDP增长': ('EA_REAL_GDP_YOY',
                      'r33_supplement(年度增速;序列为同比口径)'),
}
RANGE_SECONDARY = {'fed_funds_target_range': 'DFEDTARL'}

# 目标文本 → 地区(按目标名/主题;多地区或无指向=None=全球)
_REGION_TARGET_WORDS = (
    ('US', ('US_', 'Fed', 'fed_', '联邦基金', '标普', 'SPX', '美国', 'hyperscaler')),
    ('EA', ('ECB', 'EA_', '欧元区', '欧洲')),
    ('JP', ('BOJ', 'JP_', '日本', 'JREIT')),
    ('CN', ('CN_', '中国', '社融')))
_REGION_SUBJECTS = {'US_rates': 'US', 'US_growth': 'US', 'EA_macro': 'EA',
                    'JP_macro': 'JP', 'CN_macro': 'CN'}


# ── 问句判别 ────────────────────────────────────────────────────────────

def asked(question):
    q = question or ''
    return {'gap': any(w in q for w in GAP_WORDS),
            'views': any(w in q for w in VIEW_WORDS),
            'pricing': any(w in q for w in PRICING_WORDS)}


def is_asked(question):
    a = asked(question)
    return bool(a['gap'] or (a['views'] and a['pricing']))


def parse_falsification_window(question, cutoff_iso):
    """「未来半年/未来六个月/接下来 3 个月/未来一年半/未来两个季度」→ 窗末
    (研究截止日+N 月;季度=N×3 个月);未指明/不支持(如「半个月」「三个月
    半」)=None。「半年」是一个量词整体(=六个月),不读作「半 × 年」。"""
    q = question or ''
    m = re.search(r'(?:未来|今后|接下来|随后|往后)\s*(半|[一二两三四五六七八九十]{1,2}|'
                  r'\d+)\s*(年|个?月|个?季度)(半)?', q)
    if not m or not cutoff_iso:
        return None
    w, unit, extra = m.group(1), m.group(2), m.group(3)
    unit = unit.lstrip('个')       # 「N 个季度」→ 季度
    if w == '半':
        if unit != '年':
            return None            # 「半个月/半季度」: 不支持=未指明
        n, unit = 6, '月'
    else:
        n = int(w) if w.isdigit() else _cn_int(w)
    if not n:
        return None
    months = n * (12 if unit == '年' else 3 if unit == '季度' else 1)
    if extra:
        if unit != '年':
            return None            # 「N 个月半」: 非整月窗不支持=未指明
        months += 6                # 「一年半」=18 个月
    return {'months': months, 'start': cutoff_iso,
            'end': _shift_months(cutoff_iso, months),
            'source': m.group(0)}


def _cn_int(w):
    """中文数量(一位或两位: 「十」=10、「十一」=11、「十二」=12)。"""
    digits = {'一': 1, '二': 2, '两': 2, '三': 3, '四': 4, '五': 5, '六': 6,
              '七': 7, '八': 8, '九': 9}
    if '十' not in w:
        return digits.get(w, 0)
    tens, _, ones = w.partition('十')
    return (digits.get(tens, 0) if tens else 1) * 10 + digits.get(ones, 0)


def _shift_months(iso, n):
    import datetime as _dt
    d = _dt.date.fromisoformat(str(iso)[:10])
    y, mo = d.year, d.month + int(n)
    while mo > 12:
        mo -= 12
        y += 1
    return _dt.date(y, mo, min(d.day, calendar.monthrange(y, mo)[1])).isoformat()


def plan_regions(question, ent):
    """预期差问句的地区集合: 问句点名的经济体(名称/简称/央行别名);无点名=全部
    在册四地(披露来源)。→ (按 US,CN,EA,JP 排序的地区列表, region_source)"""
    q = question or ''
    ecos = [e for e in ((ent or {}).get('economies') or [])
            if e in _REGION_ORDER]
    for e, words in _CB_WORDS.items():
        if e not in ecos and any(w in q for w in words):
            ecos.append(e)
    for e, lab in _REGION_LABEL.items():
        if e not in ecos and lab in q:
            ecos.append(e)
    if not ecos:
        return list(_REGION_ORDER), 'default_all_registered'
    return sorted(ecos, key=_REGION_ORDER.index), 'question_named'


# ── 观点库/映射/点位解析 ────────────────────────────────────────────────

def _sha256_file(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def load_library(root, views_dir=None):
    """观点库装载(view_store 同一装载器: 违规件隔离不装载)+逐文件 sha256 清单。
    目录不在场=status 'absent'(干净安装常态;缺口显式回传)。"""
    import glob
    import view_store as vs
    d = (views_dir if views_dir is not None
         else (os.path.join(root, VIEWS_REL) if root else None))
    lib = {'status': 'absent', 'dir_rel': VIEWS_REL, 'n_files': 0,
           'n_compliant': 0, 'n_quarantined': 0, 'quarantined': [],
           'docs': [], 'manifest': {}}
    if not d or not os.path.isdir(d):
        return lib
    res = vs.load_views(d)
    for p in sorted(glob.glob(os.path.join(d, 'VIEW-*.json'))):
        lib['manifest'][VIEWS_REL + '/' + os.path.basename(p)] = \
            _sha256_file(p)
    lib.update(
        status='present', n_files=res['n_files'],
        n_compliant=len(res['views']),
        n_quarantined=len(res['quarantined']),
        quarantined=[{'file': q.get('file'), 'view_id': q.get('view_id'),
                      'n_violations': len(q.get('violations') or [])}
                     for q in res['quarantined']],
        docs=res['views'])
    return lib


def load_target_map(root):
    import view_verifier as vv
    p = os.path.join(root, TARGET_MAP_REL) if root else None
    if not p or not os.path.isfile(p):
        return None
    return vv.load_forecast_target_map(p)


def resolve_metric(target, target_map):
    """目标文本 → (指标, 映射来源)。补充别名表先于规范表;均未命中=(None, None)。"""
    t = str(target or '').strip()
    if t in SUPPLEMENT_TARGETS:
        return SUPPLEMENT_TARGETS[t]
    mid = None
    if target_map:
        import view_verifier as vv
        mid = vv._resolve_forecast_metric(t, target_map)
    return (mid, 'canonical:' + TARGET_MAP_REL) if mid else (None, None)


def _region_of(target, doc):
    t = str(target or '')
    hits = set()
    for reg, words in _REGION_TARGET_WORDS:
        if any(w in t for w in words):
            hits.add(reg)
    if not hits:
        subs = [s for s in (doc.get('subjects') or [])
                if s in _REGION_SUBJECTS]
        if subs:
            hits = {_REGION_SUBJECTS[s] for s in subs}
    return sorted(hits, key=_REGION_ORDER.index)[0] if len(hits) == 1 else None


_NUM = r'[+\-−]?\d+(?:\.\d+)?'
_NUM_RE = re.compile(_NUM)
_DATE_UNIT = ('年', '月', '日', '次', '季度')
_QUAL = {'至少': 'at_least', '至多': 'at_most', '最多': 'at_most',
         '不超过': 'at_most', '大约': 'about', '约': 'about',
         '接近': 'about', '大致': 'about'}


def _f(s):
    try:
        return float(str(s).replace('−', '-'))
    except (TypeError, ValueError):
        return None


def _date_part(s, m):
    """数字记号是否为日期成分(ISO 日期的年/日段、四位年份)。"""
    after = s[m.end():m.end() + 6]
    before = s[max(0, m.start() - 7):m.start()]
    if re.match(r'-\d{1,2}-\d{1,2}', after):
        return True
    if re.search(r'\d{4}-\d{1,2}-$', before):
        return True
    tok = m.group(0)
    if (re.fullmatch(r'(19|20)\d{2}', tok) and s[m.end():m.end() + 1] not in
            ('%', 'b', 'B', '$', '万', '亿', '点', '.')):
        return True
    return False


def parse_point(text):
    """机构点位文本 → 类型化点位(确定性;解析不了='text',不猜)。

    kind ∈ hike_count(加息 N 次,带 至少/至多/约 限定)| change_bp(加息/降息
    Xbp)| growth_pct(「2026年+25%」带符号增速)| level_range(区间)|
    level(单值;unit=percent/bp/原文单位)| multi(多值,不逐值对账)| text。"""
    s = str(text or '').strip()
    out = {'kind': 'text', 'value': None, 'raw': s}
    if not s:
        return out
    main = re.split(r'[(（]', s, 1)[0].strip()
    hike = '加息' in s or '上调' in s
    cut = '降息' in s or '下调' in s
    m = re.search(r'(至少|至多|最多|不超过|大约|约|接近|大致)?\s*(?:再|又)?\s*'
                  r'(加息|降息)\s*([一二两三四五六七八九十]|\d+)\s*次', s)
    if m and hike != cut:
        g3 = m.group(3)
        n = int(g3) if g3.isdigit() else _cn_int(g3)
        if n > 0:
            return {'kind': 'hike_count', 'count': n,
                    'sign': 1 if m.group(2) == '加息' else -1,
                    'qualifier': _QUAL.get(m.group(1) or '', 'exact'),
                    'raw': s}
    m = re.search(r'(' + _NUM + r')\s*bp', main, re.I)
    if m and hike != cut:
        v = _f(m.group(1))
        if v is not None:
            val = (-abs(v) if v < 0 else abs(v) * (1 if hike else -1))
            return {'kind': 'change_bp', 'value': round(val, 4), 'raw': s}
    m = re.match(r'\s*(?:\d{4}\s*年\s*)?([+\-−]\d+(?:\.\d+)?)\s*%', main)
    if m:
        return {'kind': 'growth_pct', 'value': round(_f(m.group(1)), 4),
                'raw': s}
    m = re.match(r'\s*[^0-9+\-−(（]{0,8}?(' + _NUM + r')\s*%\s*'
                 r'[-~–—至到]\s*(' + _NUM + r')\s*%', s)
    if m:
        lo, hi = _f(m.group(1)), _f(m.group(2))
        if lo is not None and hi is not None:
            return {'kind': 'level_range', 'lo': min(lo, hi),
                    'hi': max(lo, hi), 'unit': 'percent', 'raw': s}
    yrs = re.findall(r'(?:19|20)\d{2}年[^0-9]{0,6}(' + _NUM + r')', s)
    if len(yrs) >= 2:
        return {'kind': 'multi', 'values': [_f(y) for y in yrs[:12]], 'raw': s}
    for fm in _NUM_RE.finditer(s):
        if _date_part(s, fm):
            continue
        m = re.match(r'(' + _NUM + r')\s*([^\s(（,，;；。]{0,10})',
                     s[fm.start():])
        if m:
            v = _f(m.group(1))
            unit = (m.group(2) or '').strip()
            if v is not None and not unit.startswith(_DATE_UNIT):
                if unit.startswith('%'):
                    u = 'percent'
                elif re.match(r'(?i)bp', unit):
                    u = 'bp'
                else:
                    u = unit or None
                return {'kind': 'level', 'value': v, 'unit': u, 'raw': s}
        break
    vals = []
    for m in _NUM_RE.finditer(s):
        if _date_part(s, m) or s[m.end():m.end() + 1] in _DATE_UNIT:
            continue
        v = _f(m.group(0))
        if v is not None:
            vals.append(v)
    if len(vals) >= 2:
        return {'kind': 'multi', 'values': vals[:12], 'raw': s}
    if len(vals) == 1:
        return {'kind': 'level', 'value': vals[0], 'unit': None, 'raw': s}
    return out


def point_text(pt):
    """点位 → 读者可读短文本(渲染与席位工单同一写法)。"""
    if not isinstance(pt, dict):
        return '—'
    k = pt.get('kind')
    if k == 'hike_count':
        q = {'at_least': '至少', 'at_most': '至多', 'about': '约'}.get(
            pt.get('qualifier'), '')
        return '%s%s%s%d次' % (q, '加息' if pt.get('sign', 1) > 0 else '降息',
                               '' if q else '', pt.get('count') or 0)
    if k == 'change_bp':
        v = float(pt.get('value') or 0)
        return '%+g bp' % v
    if k == 'growth_pct':
        return '%+g%%' % float(pt.get('value') or 0)
    if k == 'level_range':
        return '%g%%–%g%%' % (pt.get('lo'), pt.get('hi'))
    if k == 'level':
        u = {'percent': '%', 'bp': 'bp'}.get(pt.get('unit'), pt.get('unit') or '')
        return '%g%s' % (pt.get('value'), u)
    if k == 'multi':
        return '多值(%s)' % '/'.join('%g' % v for v in pt.get('values') or [])
    return '文字型(无数字点位)'


# ── 事实面 / 市场定价面 / 对照规则(全部确定性,可独立复算) ─────────────────

_CURVE_NAME_RE = re.compile(r'^\s*(\d{4})\s*年\s*(\d{1,2})\s*月')
_MONTHS_RE = re.compile(r'(\d+)\s*m\b')
_LAG_TOL_DAYS = {'daily': 10, 'weekly': 10, 'monthly': 45, 'quarterly': 100}


_TGT_DATE_RE = re.compile(r'end([A-Za-z]{3})(\d{4})', re.I)
_MONTH_ABBR = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
               'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}


def _iso8(td):
    """YYYYMMDD → YYYY-MM-DD(其余原样;None→None)。"""
    t = str(td or '')
    return ('%s-%s-%s' % (t[:4], t[4:6], t[6:8])
            if len(t) == 8 and t.isdigit() else (t or None))


def _date_from_target(target):
    """目标名自带时点(endAug2026 型)→ 该月末日 ISO;解析不出=None。"""
    m = _TGT_DATE_RE.search(str(target or ''))
    if not m:
        return None
    mo = _MONTH_ABBR.get(m.group(1).lower())
    if not mo:
        return None
    y = int(m.group(2))
    return '%04d-%02d-%02d' % (y, mo, calendar.monthrange(y, mo)[1])


def _ymd(v):
    s = str(v or '')
    if re.fullmatch(r'\d{8}', s):
        return '%s-%s-%s' % (s[:4], s[4:6], s[6:])
    return s[:10] if re.match(r'\d{4}-\d{2}-\d{2}', s) else ''


def _month_end(ym):
    return '%s-%02d' % (ym, calendar.monthrange(int(ym[:4]), int(ym[5:7]))[1])


def _prev_month(ym):
    y, m = int(ym[:4]), int(ym[5:7])
    return '%04d-%02d' % ((y, m - 1) if m > 1 else (y - 1, 12))


def _days(ym):
    return calendar.monthrange(int(ym[:4]), int(ym[5:7]))[1]


def _pub_kind(basis_text):
    b = str(basis_text or '')
    if b.startswith('calendar:'):
        return 'calendar'
    if b.startswith('rule:'):
        return 'rule_estimated'
    return 'none'


def view_horizon_end(doc):
    """机构自身展望期终点: view_horizon 'Nm' → 发布日 + N 月;其余=None。"""
    pub = _ymd(doc.get('publish_date'))
    m = _MONTHS_RE.match(str(doc.get('view_horizon') or '').strip().lower())
    if not (pub and m):
        return None
    try:
        return _shift_months(pub, int(m.group(1)))
    except ValueError:
        return None


class Facts(object):
    """事实面取数(一次装配内复用): 指标在截止日/指定日的最新非空观测。

    序列取自传入快照(计划段=证据口径截止视图;发布日≤截止日/版本绑定由
    evidence_gate 统一把关),本类只做「≤日最新非空」定位,不做任何插值。"""

    def __init__(self, snap, root, as_of, reg_by_id=None):
        self.snap, self.root, self.as_of = snap, root, as_of
        self.eg = (snap or {}).get('evidence_gate') or {}
        self.reg = reg_by_id or {}
        self._cache = {}

    def series(self, mid):
        if mid not in self._cache:
            import research_map_planner as rmp
            try:
                s, err = rmp._series(mid, self.snap, self.root)
            except Exception as e:                      # 序列读取失败=缺席
                s, err = None, '%s: %s' % (type(e).__name__, e)
            dates = [str(d)[:10] for d in ((s or {}).get('dates') or [])]
            vals = list((s or {}).get('values') or [])
            n = min(len(dates), len(vals))
            self._cache[mid] = (dates[:n], vals[:n], err,
                                (s or {}).get('unit'))
        return self._cache[mid]

    def at(self, mid, on=None):
        """≤on(默认截止日)的最新非空观测 → 事实行(status ok/missing/unmapped)。"""
        on = on or self.as_of
        meta = self.reg.get(mid) or {}
        out = {'metric_id': mid, 'value': None, 'observation_date': None,
               'unit': meta.get('unit'), 'frequency': meta.get('frequency'),
               'evidence_ref': None, 'status': 'missing', 'note': None,
               'publish_date': None, 'publish_basis': None,
               'vintage': ((self.eg.get('series') or {}).get(mid) or {})
               .get('vintage')}
        if not mid:
            out.update(status='unmapped', note='目标未映射到在册指标')
            return out
        dates, vals, err, unit = self.series(mid)
        out['unit'] = out['unit'] or unit
        if not dates:
            out['note'] = '序列缺席' + ('(%s)' % err if err else '')
            return out
        i = next((k for k in range(len(dates) - 1, -1, -1)
                  if dates[k] <= on and vals[k] is not None), None)
        if i is None:
            out['note'] = '序列无 ≤%s 的非空观测(首观测 %s)' % (on, dates[0])
            return out
        out.update(value=vals[i], observation_date=dates[i], status='ok',
                   evidence_ref='%s@%s' % (mid, dates[i]))
        try:
            import datetime as _dt
            out['age_days'] = (_dt.date.fromisoformat(on)
                               - _dt.date.fromisoformat(dates[i])).days
        except ValueError:
            pass
        _sa = _stale_after(meta.get('frequency'))
        if out.get('age_days') is not None and out['age_days'] > _sa:
            out.update(stale=True, stale_after_days=_sa)
        if meta.get('frequency'):
            import research_map_planner as rmp
            pub, basis = rmp._visible_publish(mid, meta.get('frequency'),
                                              dates[i])
            out.update(publish_date=pub, publish_basis=_pub_kind(basis),
                       publish_basis_text=basis)
        return out


def _lag_days(freq):
    return _LAG_TOL_DAYS.get(str(freq or '').lower(), 45)


def _stale_after(freq):
    """读数距截止日超过该天数=陈旧(日频 10/周频 14/月频 45/季频 100)。"""
    return {'daily': 10, 'weekly': 14, 'monthly': 45,
            'quarterly': 100}.get(str(freq or '').lower(), 45)


def fact_near(fb, mid, on, freq):
    """指定日附近的事实(on 前后各一个滞后容差内最近非空观测);超出=陈旧。"""
    import datetime as _dt
    out = {'metric_id': mid, 'target_date': on, 'value': None,
           'observation_date': None, 'distance_days': None,
           'evidence_ref': None, 'status': 'missing', 'tolerance_days': _lag_days(freq)}
    if not mid:
        out.update(status='unmapped', note='目标未映射到在册指标')
        return out
    dates, vals, err, _u = fb.series(mid)
    if not dates:
        out['note'] = '序列缺席' + ('(%s)' % err if err else '')
        return out
    tol = out['tolerance_days']
    best = None
    for k in range(len(dates) - 1, -1, -1):
        if vals[k] is None:
            continue
        try:
            d = (_dt.date.fromisoformat(dates[k]) - _dt.date.fromisoformat(on)).days
        except ValueError:
            continue
        if abs(d) > tol:
            if d < 0:
                break
            continue
        if best is None or abs(d) < abs(best[0]):
            best = (d, k)
    if best is None:
        out['status'] = 'fact_stale_at_horizon'
        out['note'] = ('序列在 %s ±%d 天内无观测(最近观测 %s)——到期值不可核'
                       % (on, tol, next((dates[k] for k in range(len(dates) - 1, -1, -1) if vals[k] is not None), None)))
        return out
    out.update(value=vals[best[1]], observation_date=dates[best[1]],
               distance_days=best[0], status='ok',
               evidence_ref='%s@%s' % (mid, dates[best[1]]))
    return out


def build_pricing(fb, snap, root, as_of):
    """同期限市场定价面: 联邦基金利率期货合约月均隐含有效利率(快照事实面的
    曲线行)。取数序: 运行快照(target_date≤as_of)→ as-of 版本快照(证据口径门
    指认;历史截止时运行快照是较晚版本,曲线不得回用)→ 缺席(显式缺口)。"""
    import datetime as _dt
    face = {'metric_id': PATH_METRIC, 'instrument': PATH_INSTRUMENT,
            'status': 'absent', 'basis': None, 'source_snapshot_id': None,
            'source_target_date': None, 'observed_at': None, 'rows': [],
            'skipped_rows': [], 'baseline': None, 'midpoint': None,
            'step_bp': STEP_BP, 'material_gap_bp': MATERIAL_GAP_BP,
            'basis_note': ('期货以当月有效联邦基金利率均值交割——曲线为月均口径,'
                           '非时点口径;变动=合约月均隐含利率−截止日有效利率'
                           '(备选基线=目标区间中点),单位 bp'),
            'gaps': []}
    td = _ymd((snap or {}).get('target_date'))
    src, basis = None, None
    if (snap and td and td <= as_of
            and (snap.get('fed_futures_curve') or [])):
        src, basis = snap, 'run_snapshot'
    else:
        vrel = (((snap or {}).get('evidence_gate') or {}).get('vintage')
                or {}).get('vintage_snapshot')
        vsnap = None
        if vrel and root:
            vp = vrel if os.path.isabs(vrel) else os.path.join(root, vrel)
            try:
                with open(vp, encoding='utf-8') as f:
                    vsnap = json.load(f)
            except (OSError, ValueError):
                vsnap = None
        vtd = _ymd((vsnap or {}).get('target_date'))
        if vsnap and vtd and vtd <= as_of and (vsnap.get('fed_futures_curve') or []):
            src, basis = vsnap, 'as_of_vintage_snapshot'
    if src is None:
        face['gaps'].append({
            'code': 'pricing_absent_at_cutoff', 'region': 'US',
            'metric_id': PATH_METRIC, 'severity': 'disclosed',
            'note': ('研究截止日 %s 当时可得的市场定价曲线缺席(运行快照版本日 '
                     '%s;as-of 版本快照内亦无联邦基金利率期货曲线)——同期限市场'
                     '定价对照不可做,不以截止日之后的曲线顶替'
                     % (as_of, td or '无'))})
        return face
    src_td = _ymd(src.get('target_date'))
    face.update(status='present', basis=basis,
                source_snapshot_id=src.get('snapshot_id'),
                source_target_date=src_td,
                observed_at=src.get('research_as_of'))
    base = fb.at('DFF')
    face['baseline'] = base
    hi, lo = fb.at('DFEDTARU'), fb.at('DFEDTARL')
    if hi.get('value') is not None and lo.get('value') is not None:
        face['midpoint'] = {'value': round((hi['value'] + lo['value']) / 2.0, 4),
                            'upper': hi, 'lower': lo}
    if base.get('value') is None:
        face['gaps'].append({
            'code': 'series_absent:DFF', 'region': 'US', 'metric_id': 'DFF',
            'severity': 'disclosed',
            'note': ('截止日 %s 的有效联邦基金利率读数缺席(%s)——定价变动的基线'
                     '缺席,路径对照不可做' % (as_of, base.get('note') or '序列缺席'))})
    seen = set()
    for r in src.get('fed_futures_curve') or []:
        m = _CURVE_NAME_RE.match(str(r.get('name') or ''))
        rate = r.get('implied_avg_rate')
        if not m or not isinstance(rate, (int, float)):
            face['skipped_rows'].append({
                'ticker': r.get('ticker'), 'name': r.get('name'),
                'reason': 'no_contract_month' if not m else 'no_implied_rate'})
            continue
        ym = '%s-%02d' % (m.group(1), int(m.group(2)))
        if ym in seen:
            continue
        seen.add(ym)
        row = {'ticker': r.get('ticker'), 'month': ym,
               'month_end': _month_end(ym),
               'implied_avg_rate': float(rate), 'price': r.get('price'),
               'source': r.get('source'),
               'full_month_ahead': ym + '-01' > as_of,
               'evidence_ref': 'FEDFUNDS_FUT:%s' % r.get('ticker')}
        if base.get('value') is not None:
            row['change_bp'] = round((float(rate) - base['value']) * 100.0, 2)
        if face['midpoint']:
            row['change_bp_mid'] = round(
                (float(rate) - face['midpoint']['value']) * 100.0, 2)
        face['rows'].append(row)
    face['rows'].sort(key=lambda x: x['month'])
    face['full_months_ahead'] = [x['month'] for x in face['rows']
                                 if x['full_month_ahead']]
    face['last_month'] = face['rows'][-1]['month'] if face['rows'] else None
    return face


def _chg(face, ym, key):
    for r in face.get('rows') or []:
        if r['month'] == ym and r.get(key) is not None:
            return float(r[key])
    return None


_BASES = (('change_bp', 'effective'), ('change_bp_mid', 'midpoint'))


def _market_min(face, ym):
    """两种基线下市场累计变动的较小者(任一基线相容即相容)。"""
    vals = [_chg(face, ym, k) for k, _t in _BASES]
    vals = [v for v in vals if v is not None]
    return min(vals) if vals else None


def compare_path_step(face, ym, step_bp):
    """机构「M 月加息/降息 v bp」vs 市场(单步)。

    规则: 若市场把这一步定价在 M 月,M 月均隐含较前一月应落在
    [前月累计 + v/当月天数, 前月累计 + v](首日生效=上限,末日生效=下限;
    降息对称)。两种基线任一在界内=in_bound;不在界=与机构时点不相容,
    距离=越界幅度(bp)。M 月不在曲线/前一月不在曲线=不可判。"""
    prev = _prev_month(ym)
    days = _days(ym)
    out = {'month': ym, 'step_bp': float(step_bp), 'prev_month': prev,
           'market_prev_change_bp': None, 'market_change_bp': None,
           'bound_lo': None, 'bound_hi': None, 'in_bound': None,
           'distance_bp': None, 'bases_checked': 0}
    for key, tag in _BASES:
        a, b = _chg(face, prev, key), _chg(face, ym, key)
        if a is None or b is None:
            continue
        if step_bp >= 0:
            lo, hi = a + step_bp / days, a + step_bp
        else:
            lo, hi = a + step_bp, a + step_bp / days
        out['bases_checked'] += 1
        inb = (lo - BASIS_TOL_BP) <= b <= (hi + BASIS_TOL_BP)
        if inb:
            out['in_bound'] = True
            out['bound_lo'], out['bound_hi'] = round(lo, 2), round(hi, 2)
        d = 0.0 if inb else (lo - b if b < lo else b - hi)
        out['distance_bp'] = (round(d, 2) if out['distance_bp'] is None
                              else min(out['distance_bp'], round(d, 2)))
        if tag == 'effective':
            out['market_prev_change_bp'] = round(a, 2)
            out['market_change_bp'] = round(b, 2)
    if out['in_bound'] is None:
        out['in_bound'] = False if out['bases_checked'] else None
    if out['distance_bp'] is not None:
        out['distance_bp'] = round(out['distance_bp'], 2)
    return out


def compare_hike_count(face, ym, count, sign, qualifier):
    """机构「H 月前至少/至多/约 N 次(每次一步)」vs 市场(月均累计折合步数)。

    以「机构方向上的累计幅度」bb 计(加息=市场累计上调 bp;降息=取反):
    至少 N 次——bb ≥ (N−1)·步长 + 步长/当月天数 才相容(第 N 次最晚月末
    生效的月均下限);至多 N 次——bb ≤ N·步长;约 N 次——落在
    [(N−1)·步长 + 步长/当月天数, N·步长 + 半步] 内。两种基线任一相容即
    相容;越界幅度(distance_bp)=与机构不相容的程度。曲线无 H 月=不可判。"""
    days = _days(ym)
    n = float(count)
    low = (n - 1) * STEP_BP + STEP_BP / days - BASIS_TOL_BP
    out = {'month': ym, 'count': n, 'sign': sign, 'qualifier': qualifier,
           'bound_lo': None, 'bound_hi': None, 'market_change_bp': None,
           'market_hike_equivalents': None, 'consistent': None,
           'distance_bp': None, 'bases_checked': 0}
    if qualifier == 'at_most':
        out['bound_hi'] = round(n * STEP_BP + BASIS_TOL_BP, 2)
    elif qualifier == 'at_least':
        out['bound_lo'] = round(low, 2)
    else:
        out['bound_lo'], out['bound_hi'] = (round(low, 2),
                                            round(n * STEP_BP + MATERIAL_GAP_BP
                                                  + BASIS_TOL_BP, 2))
    for key, tag in _BASES:
        b = _chg(face, ym, key)
        if b is None:
            continue
        out['bases_checked'] += 1
        bb = b * (1 if sign > 0 else -1)
        if qualifier == 'at_most':
            ok, d = bb <= out['bound_hi'], max(0.0, bb - out['bound_hi'])
        elif qualifier == 'at_least':
            ok, d = bb >= out['bound_lo'], max(0.0, out['bound_lo'] - bb)
        else:
            ok = out['bound_lo'] <= bb <= out['bound_hi']
            d = (0.0 if ok else max(out['bound_lo'] - bb,
                                    bb - out['bound_hi']))
        if ok:
            out['consistent'] = True
        out['distance_bp'] = (round(d, 2) if out['distance_bp'] is None
                              else min(out['distance_bp'], round(d, 2)))
        if tag == 'effective':
            out['market_change_bp'] = round(b, 2)
            out['market_hike_equivalents'] = round(bb / STEP_BP, 2)
    if out['consistent'] is None:
        out['consistent'] = False if out['bases_checked'] else None
    return out


# ── 预期差块装配 ────────────────────────────────────────────────────────

_PATH_KINDS = ('change_bp', 'hike_count')
_RATE_UNITS = ('percent', 'percentage_point')
# 只列距离、不做到期判定的指标(点位口径与序列口径不同)
_NO_EX_POST = {
    'SPX_EPS': '点位口径(年度盈利预测)与序列口径(月度 EPS 序列)不同——只列距离,不做到期判定'}
_REGION_POLICY_METRIC = {'US': 'FED_FUNDS', 'CN': 'CN_LPR_1Y',
                         'EA': 'ECB_DFR', 'JP': 'JP_POLICY_RATE'}
_ABSENT_PRICING_NOTE = ('该经济体政策利率指标无同期限市场定价工具(快照内无在册'
                        '利率期货/掉期曲线)——机构政策观点只能对照事实,不能对照'
                        '市场定价')


def _vv():
    import view_verifier as vv
    return vv


def _row_id(view_id, n):
    return '%s#f%d' % (view_id, n)


def _gap(gaps, code, region, metric_id, note, row_id=None):
    g = {'code': code, 'region': region, 'metric_id': metric_id,
         'severity': 'disclosed', 'note': note}
    if row_id:
        g['row_id'] = row_id
    gaps.append(g)


def _scale(pt, meta):
    """点位单位→指标单位换算系数(percent↔percent=1;bp→百分点=0.01;
    无单位数字按指标单位原值)。None=不可换算。"""
    pu, u = pt.get('unit'), (meta or {}).get('unit')
    if pu is None:
        return 1.0
    if pu in ('percent', 'bp') and u == 'percentage_point':
        return 0.01 if pu == 'bp' else 1.0
    if pu == 'bp' and u == 'percent':
        return 0.01
    if pu == 'percent' and u == 'percent':
        return 1.0
    return None


def _level_tol(meta, fact_value):
    """水平对照容差: 利率/利差=绝对(日频 0.02,非日频 0.05——月均序列在
    变动月混合两档利率);其他单位=相对 0.5%。"""
    if (meta or {}).get('unit') in _RATE_UNITS:
        return (RATE_TOL if (meta or {}).get('frequency') == 'daily'
                else RATE_TOL * 2.5)
    try:
        return round(abs(float(fact_value)) * REL_TOL, 6)
    except (TypeError, ValueError):
        return None


def _level_verdict(value, fact, meta):
    """点位值 vs 事实读数 → 判定(matches/differs/unverifiable)+容差。"""
    out = {'value': value, 'fact_value': None, 'diff': None,
           'tolerance': None, 'verdict': 'unverifiable'}
    if not fact or fact.get('value') is None:
        out['note'] = (fact or {}).get('note') or '事实读数缺席'
        return out
    diff = float(value) - float(fact['value'])
    tol = _level_tol(meta, fact['value'])
    out.update(fact_value=fact['value'], diff=round(diff, 4), tolerance=tol,
               verdict=('matches' if tol is not None and abs(diff) <= tol
                        else 'differs'))
    return out


def _horizon_gap(pricing, month, cum_inst, lo_cand, hi_cand):
    """机构累计路径 vs 市场: 机构最后一步所在月之后的首个完整月(曲线月均
    口径;该月不在曲线=不可判)的市场累计变动−机构累计(bp)。

    候选触发方向由 lo_cand/hi_cand 给出(True=该方向越界构成候选;「至少/
    至多 N 次」只有单侧);幅度≥半步(MATERIAL_GAP_BP)才算;两种基线取
    幅度较小者(保守)。"""
    nm = next((r for r in pricing.get('rows') or []
               if r['month'] > month and r['full_month_ahead']), None)
    out = {'month': None, 'assessable': False, 'ticker': None,
           'evidence_ref': None, 'market_change_bp': None,
           'institution_cum_bp': cum_inst, 'gap_bp': None,
           'material': False, 'direction': None}
    if not nm:
        out['note'] = '曲线未覆盖该月之后的完整月——路径终点对照不可判'
        return out
    out.update(month=nm['month'], ticker=nm['ticker'],
               evidence_ref=nm['evidence_ref'],
               market_change_bp=nm.get('change_bp'))
    vals = [_chg(pricing, nm['month'], k) for k, _t in _BASES]
    vals = [round(v - cum_inst, 2) for v in vals if v is not None]
    if not vals:
        out['note'] = '市场变动基线缺席——路径终点对照不可判'
        return out
    g = min(vals, key=abs)
    out.update(assessable=True, gap_bp=g)
    d = ('market_above_institution' if g > 0 else
         'market_below_institution' if g < 0 else None)
    if abs(g) >= MATERIAL_GAP_BP and d:
        if (d == 'market_above_institution' and hi_cand) or \
                (d == 'market_below_institution' and lo_cand):
            out.update(material=True, direction=d)
        else:
            out['direction'] = d + '(至多/至少型声明,该方向不构成预期差)'
    return out


def _pricing_refs(pricing, months):
    return [r['evidence_ref'] for r in pricing.get('rows') or []
            if r['month'] in months]


def _pricing_reference(pricing, horizon_end):
    """文字/多值型点位的同期限定价参考(Audit-R33 任务5 修订): 该指标有市场
    定价时,取到期日当月或之前最后一个合约月的月均隐含累计变动——只附
    参考与证据引用,不解读机构表述(解读归席位)。曲线未覆盖/无到期日→None。"""
    hz = _ymd(horizon_end)
    if not hz or (pricing or {}).get('status') != 'present':
        return None
    best = None
    for r in pricing.get('rows') or []:
        if r.get('month') and r['month'] + '-01' <= hz and isinstance(
                r.get('change_bp'), (int, float)):
            best = r
    if best is None:
        return None
    return {'month': best['month'], 'ticker': best.get('ticker'),
            'change_bp': best['change_bp'],
            'evidence_ref': best.get('evidence_ref'),
            'basis': 'last_contract_month_on_or_before_horizon',
            'note': ('文字/多值型点位——引擎只附到期日当月或之前最后一个合约月'
                     '的月均隐含累计变动(相对截止日有效利率)作同期限定价参考,'
                     '不解读机构表述')}


def _context(pt, fc, scale):
    """远期点位与截止日事实读数的距离(只作背景,不作判定)。"""
    out = {'fact_value': None, 'distance': None, 'distance_pct': None}
    if fc.get('value') is None or scale is None:
        out['note'] = fc.get('note') or '事实读数缺席'
        return out
    try:
        v = (pt.get('value') if pt.get('kind') == 'level' else None)
        if v is None and pt.get('kind') == 'level_range':
            v = (float(pt['lo']) + float(pt['hi'])) / 2.0
        if v is None:
            return out
        v = float(v) * scale
        f = float(fc['value'])
        out.update(fact_value=fc['value'], distance=round(v - f, 4),
                   distance_pct=(round((v / f - 1.0) * 100.0, 2) if f else None))
    except (TypeError, ValueError, ZeroDivisionError):
        pass
    return out


def _path_row(row, pt, h_end, pricing, cum_before):
    """政策路径行(「M 月加息 Xbp」/「H 月前至少/至多 N 次」)对照同期限市场
    定价: 单步相容界 + 路径终点(首个完整月)累计差。"""
    kind, month = pt['kind'], h_end[:7]
    row['comparable_kind'] = ('path_vs_pricing' if kind == 'change_bp'
                              else 'hike_count_vs_pricing')
    cmp_, refs = {}, set()
    if kind == 'change_bp':
        st = compare_path_step(pricing, month, pt['value'])
        cum_inst = round(cum_before + float(pt['value']), 2)
        cmp_.update(step=st, cum_inst_bp=cum_inst)
        sign = 1 if pt['value'] > 0 else -1
        lo_cand = hi_cand = True
        months = {month, st['prev_month']}
        assessed = st['bases_checked'] > 0
    else:
        cc = compare_hike_count(pricing, month, pt['count'], pt['sign'],
                                pt['qualifier'])
        cum_inst = round(pt['sign'] * pt['count'] * STEP_BP, 2)
        cmp_.update(count_check=cc, cum_inst_bp=cum_inst)
        sign = pt['sign']
        lo_cand = pt['qualifier'] in ('at_least', 'about', 'exact')
        hi_cand = pt['qualifier'] in ('at_most', 'about', 'exact')
        months = {month}
        assessed = cc['bases_checked'] > 0
    hg = _horizon_gap(pricing, month, cum_inst, lo_cand, hi_cand)
    cmp_['horizon_gap'] = hg
    row['comparison'], row['cum_inst_bp'] = cmp_, cum_inst
    row['direction'] = 'up' if sign > 0 else 'down'
    if hg.get('month'):
        months.add(hg['month'])
    refs |= set(_pricing_refs(pricing, months))
    if (pricing.get('baseline') or {}).get('evidence_ref'):
        refs.add(pricing['baseline']['evidence_ref'])
    row['comparable'] = bool(assessed)
    row['evidence_refs'] += sorted(refs)
    if not assessed:
        row.update(status='not_comparable',
                   basis_note='曲线无 %s 月(或其前一月)合约——对照不可判' % month)
        return
    cand, reasons, notes = False, [], []
    if kind == 'change_bp':
        st = cmp_['step']
        if not st['in_bound'] and (st['distance_bp'] or 0) >= MATERIAL_GAP_BP:
            cand = True
            reasons.append(
                '%s 月合约月均较前一月变动 %+.2fbp,不在机构「%s」的相容界 '
                '[%.2f, %.2f] 内(越界 %.2fbp)'
                % (month, st['market_change_bp'] - st['market_prev_change_bp'],
                   row['point_text'], st['bound_lo'], st['bound_hi'],
                   st['distance_bp']))
        elif not st['in_bound']:
            notes.append('单步越界幅度 %.2fbp 不足半步,不构成候选'
                         % st['distance_bp'])
    else:
        cc = cmp_['count_check']
        if not cc['consistent'] and (cc['distance_bp'] or 0) >= MATERIAL_GAP_BP:
            cand = True
            reasons.append(
                '%s 月合约月均隐含累计变动 %.2fbp(折合 %.2f 个步长),与机构'
                '「%s」不相容(越界 %.2fbp)'
                % (month, cc['market_change_bp'],
                   cc['market_hike_equivalents'], row['point_text'],
                   cc['distance_bp']))
        elif not cc['consistent']:
            notes.append('次数对照越界幅度 %.2fbp 不足半步,不构成候选'
                         % cc['distance_bp'])
    if hg.get('material'):
        cand = True
        reasons.append(
            '路径终点: %s 月(首个完整月)合约月均隐含累计变动 %.2fbp vs 机构'
            '累计 %+.2fbp——市场较机构%s %.2fbp(≥半步)'
            % (hg['month'], hg['market_change_bp'], cum_inst,
               '多定价' if hg['gap_bp'] > 0 else '少定价', abs(hg['gap_bp'])))
    elif hg.get('assessable'):
        notes.append('路径终点(%s 月)市场−机构 %+.2fbp,不足半步'
                     % (hg['month'], hg['gap_bp']))
    else:
        notes.append(hg.get('note') or '')
    row['candidate'] = cand
    row['status'] = 'inconsistent' if cand else 'consistent'
    row['candidate_reason'] = '; '.join(reasons) or None
    row['basis_note'] = '; '.join(n for n in notes if n) or None


def _rng(pt, scale, meta, hi_fact, lo_fact):
    """区间点位对照: 上限/下限各自判定 → 合并(任一 differs=differs;否则全
    matches=matches;其余 unverifiable)。lo_fact=None(无次指标)=只核上限。"""
    vu = _level_verdict(pt['hi'] * scale, hi_fact, meta)
    vl = (_level_verdict(pt['lo'] * scale, lo_fact, meta)
          if lo_fact is not None else None)
    vs_ = (vu['verdict'], vl['verdict'] if vl else 'matches')
    verdict = ('matches' if all(x == 'matches' for x in vs_)
               else 'differs' if 'differs' in vs_ else 'unverifiable')
    return {'upper': vu, 'lower': vl, 'verdict': verdict,
            'note': vu.get('note') or (vl or {}).get('note') or None}


def _fx(f):
    """事实读数文本: 值(观测日) / 缺席注记。"""
    if not isinstance(f, dict):
        return '—'
    if f.get('status') == 'ok':
        return '%s(%s)' % (f.get('value'), f.get('observation_date'))
    return '缺席(%s)' % (f.get('note') or f.get('status') or '—')


def _current_note(row, cmp_, is_rng, vp, as_of):
    """当前状态型一致注记(读数/观测日随行;区间=上限/下限各自列)。"""
    fa = row.get('facts') or {}
    if is_rng:
        def _side(tag, d):
            if not isinstance(d, dict) or not isinstance(d.get('upper'), dict):
                return '%s读数缺席' % tag
            hi, lo = d['upper'], d.get('lower') or {}
            return ('%s读数 上限 %s / 下限 %s(观测 %s / %s)'
                    % (tag, hi.get('value'), lo.get('value'),
                       hi.get('observation_date'), lo.get('observation_date')))
        return '%s;%s——与区间 %s %s' % (
            _side('发布日 %s ' % row.get('publish_date'), fa.get('at_publish')),
            _side('截止日 %s ' % as_of, fa.get('at_cutoff')),
            row.get('point_text'),
            '一致' if vp == 'matches' else '对照一致(发布日附近读数缺席)')
    fp_ = fa.get('at_publish')
    if vp == 'matches':
        return ('发布日 %s 附近读数 %s;截止日 %s 读数 %s——均与点位 %s 一致'
                % (row.get('publish_date'), _fx(fp_), as_of,
                   _fx(fa.get('at_cutoff')), row.get('point_text')))
    return ('截止日 %s 读数 %s 与点位 %s 对照一致;发布日附近读数 %s'
            % (as_of, _fx(fa.get('at_cutoff')), row.get('point_text'), _fx(fp_)))


def _level_row(row, pt, h_end, fb, fc, meta, gaps, as_of):
    """水平点位行对照事实: 当前状态型→发布日/截止日读数;已到期→到期日附近
    读数(事后表现);远期未到期→无同期限市场定价,只列与截止日读数的距离。
    区间点位(目标区间)上限/下限各自对照(下限=次指标,见 RANGE_SECONDARY)。"""
    kind, mid, region = pt['kind'], row['metric_id'], row['region']
    freq = meta.get('frequency')
    scale = _scale(pt, meta)
    is_rng = kind == 'level_range'
    refs = set()
    if scale is None:
        row.update(status='not_comparable', basis_note=(
            '点位单位「%s」与指标单位「%s」不可换算——只列点位,不对照'
            % (pt.get('unit'), meta.get('unit'))))
        return
    if mid in _NO_EX_POST:
        row.update(status='context_only', basis_note=_NO_EX_POST[mid])
        row['context'] = _context(pt, fc, scale)
        _gap(gaps, 'pricing_absent:' + mid, region, mid,
             '%s——机构点位(%s)无同期限市场定价可对账' % (_NO_EX_POST[mid],
                                                row['row_id']))
        return
    sec = RANGE_SECONDARY.get(row['target']) if is_rng else None
    lo_cut = fb.at(sec) if sec else None
    if sec and lo_cut.get('evidence_ref'):
        refs.add(lo_cut['evidence_ref'])
    mat = row['maturity']
    if mat == 'CURRENT_STATE':
        row['comparable_kind'] = 'level_vs_fact'
        if is_rng:
            fp_hi = fact_near(fb, mid, row['publish_date'], freq)
            fp_lo = fact_near(fb, sec, row['publish_date'], freq)
            row['facts']['at_publish'] = {'upper': fp_hi, 'lower': fp_lo}
            row['facts']['at_cutoff'] = {'upper': fc, 'lower': lo_cut}
            cmp_ = {'at_publish': _rng(pt, scale, meta, fp_hi, fp_lo),
                    'at_cutoff': _rng(pt, scale, meta, fc, lo_cut),
                    'lower_metric_id': sec}
            for _x in (fp_hi, fp_lo):
                if _x.get('evidence_ref'):
                    refs.add(_x['evidence_ref'])
            stale_f = fc if fc.get('stale') else (
                lo_cut if lo_cut.get('stale') else None)
        else:
            fp_ = fact_near(fb, mid, row['publish_date'], freq)
            row['facts']['at_publish'] = fp_
            if fp_.get('evidence_ref'):
                refs.add(fp_['evidence_ref'])
            val = pt['value'] * scale
            cmp_ = {'at_publish': _level_verdict(val, fp_, meta),
                    'at_cutoff': _level_verdict(val, fc, meta)}
            stale_f = fc if fc.get('stale') else None
        row['comparison'] = cmp_
        row['comparable'] = True
        vp, vc = cmp_['at_publish']['verdict'], cmp_['at_cutoff']['verdict']
        stale_note = None
        if stale_f is not None:
            stale_note = ('截止日读数止于 %s(距截止日 %s 天,超过 %s 天)——对照'
                          '基于陈旧读数,不构成对该「当前水平」的当期确认'
                          % (stale_f['observation_date'], stale_f['age_days'],
                             stale_f['stale_after_days']))
            _gap(gaps, 'fact_stale_at_cutoff:' + stale_f['metric_id'],
                 region, stale_f['metric_id'],
                 '指标 %s 截止日读数止于 %s(距截止日 %s 天)——%s「当前水平」'
                 '点位只能对照陈旧读数'
                 % (stale_f['metric_id'], stale_f['observation_date'],
                    stale_f['age_days'], row['institution']),
                 row_id=row['row_id'])
        _dp = cmp_['at_publish'].get('diff')
        _dc = cmp_['at_cutoff'].get('diff')
        if vp == 'differs':
            st_ = 'fact_mismatch'
            note = '发布日附近的事实读数与点位不符%s' % (
                '(差 %s)' % _dp if _dp is not None else '(上限/下限见对照)')
        elif vc == 'matches':
            st_ = 'consistent_stale_fact' if stale_note else 'consistent'
            note = stale_note or _current_note(row, cmp_, is_rng, vp, as_of)
        elif vc == 'differs':
            st_ = 'no_longer_current'
            note = '截止日读数已与点位不同%s——该「当前水平」表述已过时' % (
                '(差 %s)' % _dc if _dc is not None else '(上限/下限见对照)')
        else:
            st_ = 'unverifiable'
            note = (cmp_['at_cutoff'].get('note') or '截止日读数缺席')
            _gap(gaps, 'fact_stale_at_cutoff:' + mid, region, mid,
                 '指标 %s 在截止日 %s 无有效读数(%s)——「当前水平」点位不可核'
                 % (mid, as_of, note), row_id=row['row_id'])
        row.update(status=st_, basis_note=note)
    elif mat == 'MATURED':
        row['comparable_kind'] = 'ex_post_level'
        if is_rng:
            fh_hi = fact_near(fb, mid, h_end, freq)
            fh_lo = fact_near(fb, sec, h_end, freq)
            row['facts']['at_horizon'] = {'upper': fh_hi, 'lower': fh_lo}
            at_h = _rng(pt, scale, meta, fh_hi, fh_lo)
            facts_ = (fh_hi, fh_lo)
        else:
            fh = fact_near(fb, mid, h_end, freq)
            row['facts']['at_horizon'] = fh
            at_h = _level_verdict(pt['value'] * scale, fh, meta)
            facts_ = (fh,)
        for _x in facts_:
            if _x.get('evidence_ref'):
                refs.add(_x['evidence_ref'])
        row['comparison'] = {'at_horizon': at_h}
        row['comparable'] = True
        v, _d = at_h['verdict'], at_h.get('diff')
        if v == 'matches':
            row.update(status='ex_post_consistent',
                       basis_note='到期日 %s 的事实读数与点位一致%s'
                       % (h_end, ('(差 %s,容差 %s)' % (_d, at_h['tolerance'])
                                  if _d is not None else '(上限/下限见对照)')))
        elif v == 'differs':
            row.update(status='ex_post_missed',
                       basis_note='到期日 %s 的事实读数与点位不符%s'
                       % (h_end, ('(差 %s,容差 %s)' % (_d, at_h['tolerance'])
                                  if _d is not None else '(上限/下限见对照)')))
        else:
            row.update(status='unverifiable',
                       basis_note=at_h.get('note') or '到期日附近无读数')
            _gap(gaps, 'fact_stale_at_horizon:' + mid, region, mid,
                 '到期日 %s 附近无 %s 读数——点位事后表现不可核'
                 % (h_end, mid), row_id=row['row_id'])
    else:
        row.update(status='context_only', basis_note=(
            '远期点位(到期 %s)未到期;该指标无同期限市场定价——只列与截止日'
            '读数的距离,不作预期差判定' % h_end))
        row['context'] = _context(pt, fc, scale)
        _gap(gaps, 'pricing_absent:' + mid, region, mid,
             '指标 %s 无同期限市场定价(%s %s 的远期点位只能列与截止日读数的距离)'
             % (mid, row['institution'], row['row_id']))
    row['evidence_refs'] += sorted(refs - set(row['evidence_refs']))


def _build_row(doc, f, n, fb, pricing, as_of, reg, tm, gaps, cum_before):
    """单条机构预测 → 对照行(映射→点位类型→到期日→对照规则→缺口)。"""
    vv = _vv()
    vid = doc.get('view_id')
    pub = _ymd(doc.get('publish_date'))
    rid = _row_id(vid, n)
    inst = ((doc.get('institution') or {}).get('name') or vid)
    text = str(f.get('value_or_direction') or '')
    pt = parse_point(text)
    mid, msrc = resolve_metric(f.get('target'), tm)
    meta = reg.get(mid) or {}
    h_raw = f.get('horizon')
    hz = vv.parse_view_horizon(h_raw, pub)
    h_end = hz.get('horizon_end') if hz.get('state') == 'parsed' else None
    kind = pt.get('kind')
    if h_end is None:
        # 目标名自带时点(endAug2026 型)且期限文本不可解析(「已实现数据」)——
        # 以目标名时点为到期日,依据随行
        _td = _date_from_target(f.get('target'))
        if _td:
            h_end = _td
            hz = {'state': 'parsed', 'horizon_end': _td,
                  'basis': 'target_name(%s→%s)' % (f.get('target'), _td)}
    if (h_end is None and kind in ('level', 'level_range')
            and any(w in str(h_raw or '') for w in CURRENT_STATE_WORDS)):
        maturity = 'CURRENT_STATE'
        h_basis = 'current_state(期限词汇「%s」→点位按发布日状态对照事实)' % h_raw
    elif h_end is None:
        maturity, h_basis = 'UNPARSEABLE', 'unparseable(%s)' % hz.get('basis')
    else:
        maturity = 'MATURED' if h_end < as_of else 'NOT_YET_TESTABLE'
        h_basis = 'horizon_field(%s)' % hz.get('basis')
    txt_all = str(h_raw or '') + text
    row = {
        'row_id': rid, 'view_id': vid, 'institution': inst,
        'institution_type': (doc.get('institution') or {}).get('type'),
        'publish_date': pub, 'report_title': doc.get('report_title'),
        'source_url': doc.get('source_url'),
        'attribution': f.get('attribution'),
        'statement_kind': ('realized_data_claim' if '已实现' in txt_all
                           else 'current_state'
                           if maturity == 'CURRENT_STATE' else 'forecast'),
        'region': _region_of(f.get('target'), doc), 'target': f.get('target'),
        'value_raw': text, 'horizon_raw': h_raw, 'horizon_end': h_end,
        'horizon_basis': h_basis, 'view_horizon_end': view_horizon_end(doc),
        'maturity': maturity, 'point': pt, 'point_text': point_text(pt),
        'metric_id': mid, 'mapping_source': msrc,
        'metric_unit': meta.get('unit'),
        'metric_frequency': meta.get('frequency'),
        'facts': {'at_cutoff': None, 'at_publish': None, 'at_horizon': None},
        'comparison': None, 'context': None, 'comparable': False,
        'comparable_kind': None, 'cum_inst_bp': None,
        'pricing_reference': None,
        'status': 'reading_required', 'candidate': None,
        'candidate_reason': None, 'direction': None, 'basis_note': None,
        'evidence_refs': [vid, rid]}
    if f.get('attribution') != 'institution_stated':
        row.update(status='library_inferred', basis_note=(
            '观点库该行登记为 %s(非机构原话)——不进入数值对照' % f.get('attribution')))
        return row
    if mid is None:
        row['status'] = 'unmapped'
        _gap(gaps, 'target_unmapped', row['region'], None,
             '机构目标「%s」未映射到在册指标(%s %s)——无事实/市场定价可对账'
             % (f.get('target'), inst, rid), row_id=rid)
        return row
    if mid not in reg:
        row['status'] = 'series_absent'
        _gap(gaps, 'series_absent:' + mid, row['region'], mid,
             '指标 %s 不在注册表/无序列——机构点位(%s %s)无事实可对'
             % (mid, inst, rid), row_id=rid)
        return row
    fc = fb.at(mid)
    row['facts']['at_cutoff'] = fc
    if fc.get('status') == 'ok':
        row['evidence_refs'].append(fc['evidence_ref'])
    else:
        _gap(gaps, 'series_absent:' + mid, row['region'], mid,
             '指标 %s 在截止日 %s 无读数(%s)——%s %s 的点位无事实可对'
             % (mid, as_of, fc.get('note'), inst, rid))
    if maturity == 'UNPARSEABLE':
        row['status'] = 'unparseable_horizon'
        _gap(gaps, 'horizon_unparseable', row['region'], mid,
             '期限文本「%s」不可解析为到期日(%s %s)——无到期日,不做对照'
             % (h_raw, inst, rid))
        return row
    if mid == PATH_METRIC and kind in _PATH_KINDS:
        _path_row(row, pt, h_end, pricing, cum_before)
    elif kind in _PATH_KINDS:
        row.update(status='not_comparable', basis_note=(
            '路径型点位所在指标 %s 无同期限市场定价——不可对照' % mid))
        _gap(gaps, 'pricing_absent:' + mid, row['region'], mid,
             '指标 %s 无同期限市场定价(%s %s 的路径点位不可对照)' % (mid, inst, rid))
    elif kind in ('level', 'level_range'):
        _level_row(row, pt, h_end, fb, fc, meta, gaps, as_of)
    elif kind == 'growth_pct':
        row.update(status='context_only', basis_note=(
            '增速型点位: 无同基期的在册市场定价——只列截止日读数作背景'),
            context=_context(pt, fc, 1.0))
        _gap(gaps, 'pricing_absent:' + mid, row['region'], mid,
             '指标 %s 无同期限市场定价(%s %s 的增速点位只列背景)'
             % (mid, inst, rid))
    else:
        row['context'] = _context(pt, fc, 1.0)
        pref = _pricing_reference(pricing, h_end) if mid == PATH_METRIC else None
        row['pricing_reference'] = pref
        if pref and pref.get('evidence_ref'):
            row['evidence_refs'].append(pref['evidence_ref'])
        row.update(status='reading_required', basis_note=(
            '%s型点位——引擎不解读,须席位推导(标「席位推导」)'
            % ('文字' if kind == 'text' else '多值')))
        _gap(gaps, 'point_non_numeric', row['region'], mid,
             '机构点位「%s」为%s型(%s %s)——引擎不解读,须席位推导'
             % (text[:24], '文字' if kind == 'text' else '多值', inst, rid))
    return row


def _tally(rows):
    """事后核验计数(逐行留档: 点位/事实/差值/判定)。"""
    return {
        'n': len(rows),
        'consistent': sum(1 for r in rows if r['status'] == 'ex_post_consistent'),
        'missed': sum(1 for r in rows if r['status'] == 'ex_post_missed'),
        'unverifiable': sum(1 for r in rows if r['status'] == 'unverifiable'),
        'rows': [{
            'row_id': r['row_id'], 'institution': r['institution'],
            'publish_date': r['publish_date'], 'horizon_end': r['horizon_end'],
            'metric_id': r['metric_id'], 'point_text': r['point_text'],
            'fact_value': ((r.get('facts') or {}).get('at_horizon') or {}).get('value'),
            'diff': ((r.get('comparison') or {}).get('at_horizon') or {}).get('diff'),
            'verdict': r['status'], 'evidence_refs': [
                x for x in r['evidence_refs'] if '@' in x]} for r in rows]}


def _disagreements(rows):
    """机构分歧面: 同一指标有 ≥2 家机构的观点行即列;路径型另给各机构在其
    自身到期月的累计幅度差(到期月不同——非同一时点,如实标注)。"""
    by_metric = {}
    for r in rows:
        if r.get('metric_id'):
            by_metric.setdefault(r['metric_id'], []).append(r)
    out = []
    for mid, rs in by_metric.items():
        insts = sorted({r['institution'] for r in rs})
        if len(insts) < 2:
            continue
        d = {'metric_id': mid, 'institutions': insts, 'n_rows': len(rs),
             'rows': [{'row_id': r['row_id'], 'institution': r['institution'],
                       'publish_date': r['publish_date'],
                       'point_text': r['point_text'],
                       'horizon_end': r['horizon_end'],
                       'status': r['status'],
                       'cum_inst_bp': r.get('cum_inst_bp')} for r in rs]}
        nums = [r for r in rs if r.get('cum_inst_bp') is not None]
        if len({r['institution'] for r in nums}) >= 2:
            cums = [r['cum_inst_bp'] for r in nums]
            d.update(numeric_spread_bp=round(max(cums) - min(cums), 2),
                     spread_note=('各机构在其自身到期月的累计路径幅度(max−min);'
                                  '到期月不同,非同一时点的直接分歧'))
        out.append(d)
    return out


def _pools(visible, rows, fb):
    """证伪条件池(观点库登记+引擎规则)/关键假设池/风险池——全部带出处。"""
    fals, assum, risk = [], [], []
    for doc in visible:
        vid = doc.get('view_id')
        inst = ((doc.get('institution') or {}).get('name') or vid)
        for k, fc in enumerate(doc.get('falsification_conditions') or [], 1):
            fals.append({'id': '%s/c%d' % (vid, k), 'source': 'view_library',
                         'view_id': vid, 'institution': inst,
                         'condition': fc.get('condition'),
                         'attribution': fc.get('attribution')})
        for k, a in enumerate(doc.get('key_assumptions') or [], 1):
            assum.append({'id': '%s/a%d' % (vid, k), 'view_id': vid,
                          'institution': inst, 'statement': a.get('statement'),
                          'attribution': a.get('attribution'),
                          'basis': a.get('basis')})
        for k, rf in enumerate(doc.get('risk_factors') or [], 1):
            risk.append({'id': '%s/r%d' % (vid, k), 'view_id': vid,
                         'institution': inst, 'statement': rf.get('statement'),
                         'attribution': rf.get('attribution')})
    base_u = fb.at('DFEDTARU')
    for r in rows:
        pt = r.get('point') or {}
        ck = r.get('comparable_kind')
        if ck in ('path_vs_pricing', 'hike_count_vs_pricing'):
            hg = (r.get('comparison') or {}).get('horizon_gap') or {}
            cum = r.get('cum_inst_bp') or 0.0
            if hg.get('month'):
                hi, lo = cum + MATERIAL_GAP_BP, cum - MATERIAL_GAP_BP
                fals.append({
                    'id': r['row_id'] + '/market', 'source': 'engine_rule',
                    'row_id': r['row_id'], 'rule_kind': 'market_pricing_gap',
                    'observable': hg['evidence_ref'],
                    'date': _month_end(hg['month']),
                    'thresholds_bp': {'above': hi, 'below': lo},
                    'condition': ('若 %s 合约月均隐含利率较截止日有效利率的累计'
                                  '变动 ≥ %+.1fbp 或 ≤ %+.1fbp(机构累计 %+.1fbp '
                                  '± 半步 %gbp)——市场与机构路径之间出现可判的'
                                  '预期差'
                                  % (hg['month'], hi, lo, cum, MATERIAL_GAP_BP))})
            if base_u.get('value') is not None and r.get('horizon_end'):
                f_ = base_u['value'] + (cum - MATERIAL_GAP_BP) / 100.0
                fals.append({
                    'id': r['row_id'] + '/policy', 'source': 'engine_rule',
                    'row_id': r['row_id'], 'rule_kind': 'policy_fact_at_horizon',
                    'observable': 'DFEDTARU@%s' % r['horizon_end'],
                    'date': r['horizon_end'],
                    'baseline': {'value': base_u['value'],
                                 'observation_date': base_u['observation_date']},
                    'pass_min_pct': round(f_, 4),
                    'one_sided': '至少/至多型声明只核单侧',
                    'condition': ('若 %s 的联邦基金目标上限较截止日读数 %s(%.2f%%)'
                                  '的上调不足 %+.1fbp(即 < %.2f%%)——机构路径「%s」'
                                  '未被兑现(事后证伪判据;至多型取反)'
                                  % (r['horizon_end'], base_u['observation_date'],
                                     base_u['value'], cum - MATERIAL_GAP_BP, f_,
                                     r['point_text']))})
        elif (not ck) and r.get('horizon_end') and pt.get('kind') == 'level' \
                and (r.get('context') or {}).get('distance') is not None \
                and r.get('metric_unit') not in _RATE_UNITS:
            fals.append({
                'id': r['row_id'] + '/level', 'source': 'engine_rule',
                'row_id': r['row_id'], 'rule_kind': 'level_at_horizon',
                'observable': '%s@%s' % (r['metric_id'], r['horizon_end']),
                'date': r['horizon_end'], 'value': pt.get('value'),
                'tolerance_rel': REL_TOL,
                'condition': ('若 %s 的 %s 读数较点位 %g 偏离超过 %.1f%%——'
                              '机构点位事后未兑现(事后核验判据)'
                              % (r['horizon_end'], r['metric_id'],
                                 pt.get('value'), REL_TOL * 100))})
    return fals, assum, risk


def _dedupe_gaps(gaps):
    seen, out = set(), []
    for g in gaps:
        k = (g.get('code'), g.get('region'), g.get('metric_id'))
        if k in seen:
            continue
        seen.add(k)
        out.append(g)
    return out


def _aggregate_unmapped(gaps):
    """未映射目标缺口按地区聚合(逐条列目标名与行号;不吞)。"""
    if not any(g.get('code') == 'target_unmapped' for g in gaps):
        return gaps
    out, byreg = [], {}
    for g in gaps:
        if g.get('code') != 'target_unmapped':
            out.append(g)
            continue
        byreg.setdefault(g.get('region'), []).append(g)
        if len(byreg[g.get('region')]) == 1:
            out.append(None)          # 占位: 聚合条放该地区首条原位
    agg = {}
    for regn, gs in byreg.items():
        names = []
        for g in gs:
            m_ = re.search(r'「(.+?)」', g.get('note') or '')
            nm = m_.group(1) if m_ else (g.get('row_id') or '')
            if nm not in names:
                names.append(nm)
        agg[regn] = {
            'code': 'target_unmapped', 'region': regn, 'metric_id': None,
            'severity': 'disclosed', 'n_rows': len(gs),
            'row_ids': [g.get('row_id') for g in gs], 'targets': names,
            'note': ('%d 条机构目标未映射到在册指标(%s)——无事实/市场定价可对账'
                     % (len(gs), '、'.join(names[:8])
                        + ('…' if len(names) > 8 else '')))}
    res, used = [], set()
    for g in out:
        if g is None:
            regn = next(r for r in byreg if r not in used)
            used.add(regn)
            res.append(agg[regn])
        else:
            res.append(g)
    return res


def build_block(plan, snap, root, as_of, question=None, views_dir=None,
                snapshot_rel=None, reg_by_id=None):
    """预期差块(引擎确定性;逐行可独立复算)。

    输入: 计划块(地区/原文)、证据口径截止视图快照、观点库目录(默认
    <root>/data/institutions/views)。输出块随 report.json 落档——渲染/重放
    只读本块,不再读观点库与快照。可见性: publish_date ≤ as_of;地区范围:
    问句点名的经济体(全库行仅在 ≥2 地区时纳入)。"""
    reg = reg_by_id or {}
    q = question if question is not None else (plan.get('question_verbatim') or '')
    regions_ = [e for e in (plan.get('regions') or {}) if e in _REGION_ORDER]
    if not regions_:
        regions_ = plan_regions(q, {})[0]
    multi = len(regions_) >= 2
    gaps = []
    lib = load_library(root, views_dir)
    tm = load_target_map(root)
    fb = Facts(snap, root, as_of, reg)
    pricing = build_pricing(fb, snap, root, as_of)
    for g in pricing['gaps']:
        _gap(gaps, g['code'], g['region'], g['metric_id'], g['note'])
    if lib['status'] != 'present':
        _gap(gaps, VIEWS_ABSENT, None, None,
             '观点库不在场(%s 目录缺席)——机构观点对照不可做;须随迁已授权'
             '观点库(只读副本+sha256 清单)后重跑' % VIEWS_REL)
    if tm is None:
        _gap(gaps, 'target_map_absent', None, None,
             '规范目标映射表缺席(%s)——机构目标无法映射到在册指标' % TARGET_MAP_REL)
    rows, withheld, out_scope, visible = [], [], [], []
    vv = _vv()
    for doc in lib['docs']:
        vid = doc.get('view_id')
        pub = _ymd(doc.get('publish_date'))
        inst = ((doc.get('institution') or {}).get('name') or vid)
        if not pub or pub > as_of:
            withheld.append({'view_id': vid, 'institution': inst,
                             'publish_date': pub or None,
                             'reason': 'publish_after_cutoff' if pub
                             else 'no_publish_date'})
            continue
        visible.append(doc)
        # 同一文档同一政策路径指标上的累计(按到期日先后;仅机构原话的 bp 步)
        steps = {}
        for n, f in enumerate(doc.get('forecasts') or [], 1):
            p = parse_point(f.get('value_or_direction'))
            m_, _s = resolve_metric(f.get('target'), tm)
            hz = vv.parse_view_horizon(f.get('horizon'), pub)
            if (f.get('attribution') == 'institution_stated'
                    and m_ == PATH_METRIC and p.get('kind') == 'change_bp'
                    and hz.get('state') == 'parsed' and hz.get('horizon_end')):
                steps[n] = (hz['horizon_end'], float(p['value']))
        cum_before, run = {}, 0.0
        for n in sorted(steps, key=lambda k: (steps[k][0], k)):
            cum_before[n] = round(run, 2)
            run += steps[n][1]
        for n, f in enumerate(doc.get('forecasts') or [], 1):
            regn = _region_of(f.get('target'), doc)
            if regn not in regions_ and not (regn is None and multi):
                out_scope.append({'row_id': _row_id(vid, n),
                                  'target': f.get('target'), 'region': regn})
                continue
            rows.append(_build_row(doc, f, n, fb, pricing, as_of, reg, tm,
                                   gaps, cum_before.get(n, 0.0)))
    # 观点库机构原话(可见文档的 institution_stated 表述;席位「机构原话」
    # 归因须逐字引自此处——契约按本清单核,渲染/重放不再读观点库)
    stmts = []
    for d in visible:
        _vid = d.get('view_id')
        for _key, _kind, _fld in (
                ('core_views', 'core_view', 'statement'),
                ('key_assumptions', 'assumption', 'statement'),
                ('risk_factors', 'risk', 'statement'),
                ('falsification_conditions', 'falsification', 'condition')):
            for _it in d.get(_key) or []:
                if (isinstance(_it, dict)
                        and _it.get('attribution') == 'institution_stated'
                        and str(_it.get(_fld) or '').strip()):
                    stmts.append({'view_id': _vid, 'kind': _kind,
                                  'text': str(_it[_fld]).strip()})
        for _it in d.get('forecasts') or []:
            if (isinstance(_it, dict)
                    and _it.get('attribution') == 'institution_stated'
                    and str(_it.get('value_or_direction') or '').strip()):
                stmts.append({'view_id': _vid, 'kind': 'forecast',
                              'text': str(_it['value_or_direction']).strip()})
    # 同期限市场定价覆盖面(四地政策利率指标;缺席=如实列出)
    coverage = {}
    for eco in regions_:
        pm = _REGION_POLICY_METRIC[eco]
        if eco == 'US':
            coverage[eco] = {'metric_id': pm, 'status': pricing['status'],
                             'instrument': (PATH_INSTRUMENT
                                            if pricing['status'] == 'present'
                                            else None)}
        else:
            coverage[eco] = {'metric_id': pm, 'status': 'absent',
                             'instrument': None}
            n_rows = sum(1 for r in rows if r.get('region') == eco)
            if n_rows:
                _gap(gaps, 'pricing_absent:' + pm, eco, pm,
                     '%s(该经济体机构观点行 %d 条)' % (_ABSENT_PRICING_NOTE, n_rows))
    gaps = _aggregate_unmapped(_dedupe_gaps(gaps))
    ex_rows = [r for r in rows if r.get('comparable_kind') == 'ex_post_level']
    f_ex = [r for r in ex_rows if r.get('statement_kind') == 'forecast']
    c_ex = [r for r in ex_rows if r.get('statement_kind') != 'forecast']
    pending = [r for r in rows if r.get('maturity') == 'NOT_YET_TESTABLE'
               and r.get('attribution') == 'institution_stated']
    earliest = min((r['horizon_end'] for r in pending if r.get('horizon_end')),
                   default=None)
    ex_post = {
        'forecast_claims': _tally(f_ex), 'realized_data_claims': _tally(c_ex),
        'not_yet_testable': {'n': len(pending), 'earliest_horizon_end': earliest},
        'note': ('到期预测核验=PARTIAL: 库内已到期且可核的机构预测 %d 条、已实现'
                 '数据表述 %d 条(逐行见上),未到期 %d 条(最早到期 %s)——到期后按'
                 '事实读数更新,未到期不做判定'
                 % (len(f_ex), len(c_ex), len(pending), earliest or '无'))}
    fals, assum, risk = _pools(visible, rows, fb)
    # 证伪窗口(问句「未来半年/未来 N 个月什么会证伪」): 窗末=研究截止日+N 月。
    # 逐条列出窗内到期的机构点位行与窗内可核的引擎规则;观点库证伪条件不带
    # 观察日期——只计数,是否落在窗内由席位判断。问句未指明窗口=None。
    _win = (plan.get('expectations_gap') or {}).get('falsification_window')
    window = wt = None
    if isinstance(_win, dict) and _win.get('months') and as_of:
        window = {'months': int(_win['months']), 'start': as_of,
                  'end': _shift_months(as_of, int(_win['months'])),
                  'source': _win.get('source')}
        pend = sorted((r for r in pending if r.get('horizon_end')
                       and as_of < r['horizon_end'] <= window['end']),
                      key=lambda r: (r['horizon_end'], r['row_id']))
        after = [r for r in pending if r.get('horizon_end')
                 and r['horizon_end'] > window['end']]
        wt = {
            'rows_in_window': [
                {'row_id': r.get('row_id'), 'institution': r.get('institution'),
                 'metric_id': r.get('metric_id'),
                 'point_text': r.get('point_text'),
                 'horizon_end': r.get('horizon_end'), 'status': r.get('status'),
                 # 到期可核=引擎有同口径事实/同期限定价可对账的行;只列背景
                 # (口径不同,不做到期判定)/序列缺席/未映射=不可核
                 'testable': r.get('status') in (
                     'consistent', 'inconsistent', 'reading_required',
                     'consistent_stale_fact')}
                for r in pend],
            'n_rows_after_window': len(after),
            'earliest_after_window': min(
                (r['horizon_end'] for r in after), default=None),
            'engine_rules_in_window': [
                p.get('id') for p in fals if p.get('source') == 'engine_rule'
                and p.get('date') and p['date'] <= window['end']],
            'engine_rules_after_window': [
                p.get('id') for p in fals if p.get('source') == 'engine_rule'
                and p.get('date') and p['date'] > window['end']],
            'n_view_library_conditions': sum(
                1 for p in fals if p.get('source') == 'view_library'),
            'note': ('窗口=研究截止日起 N 个月;窗内到期的机构点位到期即按事实/'
                     '同期限定价核验(未到期不判定);观点库证伪条件不带观察日期,'
                     '是否落在窗内由席位判断')}
    eg = (snap or {}).get('evidence_gate')
    eg = eg if isinstance(eg, dict) else {}
    vis_ids = {d.get('view_id') for d in visible}
    frozen = {}
    for rel, sha in sorted(lib['manifest'].items()):
        if os.path.basename(rel)[:-5] in vis_ids:
            frozen[rel] = sha[:16]
    if tm is not None and root:
        frozen[TARGET_MAP_REL] = _sha256_file(os.path.join(root, TARGET_MAP_REL))[:16]
    if snapshot_rel:
        frozen[snapshot_rel] = None        # 由编排器按运行快照字节回填
    comp = [r for r in rows if r.get('comparable')]
    # 对照面用到的在册指标(编排器并入取数/证据面)与缺席指标(S4 如实跳过)
    used, absent = [], []
    if pricing.get('status') == 'present':
        used.append(PATH_METRIC)
    base_m = ((pricing or {}).get('baseline') or {}).get('metric_id')
    if base_m and (pricing.get('baseline') or {}).get('status') == 'ok':
        used.append(base_m)
    for r in rows:
        if r.get('status') == 'unmapped':
            continue
        ids = [r.get('metric_id')]
        _lm = (r.get('comparison') or {}).get('lower_metric_id')
        if _lm:
            ids.append(_lm)
        fc = (r.get('facts') or {}).get('at_cutoff') or {}
        for mid in ids:
            if not mid or mid in used or mid in absent:
                continue
            # 区间行(利率走廊上下限): 截止读数={upper,lower} 两份事实
            _f_mid = fc
            if 'upper' in fc and 'lower' in fc:
                _f_mid = fc.get('lower') if mid == _lm else fc.get('upper')
            _ok = isinstance(_f_mid, dict) and _f_mid.get('status') == 'ok'
            (used if _ok else absent).append(mid)
    summary = {
        'n_views_visible': len(visible), 'n_views_withheld': len(withheld),
        'n_rows': len(rows), 'n_out_of_scope': len(out_scope),
        'comparable_n': len(comp),
        'path_n': sum(1 for r in rows if r.get('comparable_kind') in ('path_vs_pricing', 'hike_count_vs_pricing')),
        'consistent_n': sum(1 for r in rows if r.get('status') == 'consistent'),
        'inconsistent_n': sum(1 for r in rows if r.get('status') == 'inconsistent'),
        'candidate_n': sum(1 for r in rows if r.get('candidate') is True),
        'ex_post_consistent_n': ex_post['forecast_claims']['consistent'] + ex_post['realized_data_claims']['consistent'],
        'ex_post_missed_n': ex_post['forecast_claims']['missed'] + ex_post['realized_data_claims']['missed'],
        'reading_required_n': sum(1 for r in rows if r.get('status') == 'reading_required'),
        'context_only_n': sum(1 for r in rows if r.get('status') == 'context_only'),
        'unmapped_n': sum(1 for r in rows if r.get('status') == 'unmapped'),
        'series_absent_n': sum(1 for r in rows if r.get('status') == 'series_absent'),
        'stale_fact_n': sum(1 for r in rows if r.get('status') == 'consistent_stale_fact'),
        'gaps': len(gaps), 'blocked_class': None}
    block = {
        # asked: 完整块沿用计划标记的「问到」位(plan_asked/plan_block/
        # plan_blocked_class 三个读取口以此识别;替换计划标记后不丢)
        'asked': True,
        'schema': SCHEMA, 'discipline': DISCIPLINE, 'as_of': as_of,
        'question_verbatim': q, 'regions': regions_,
        'region_source': plan.get('region_source') or 'plan_regions',
        'views': {'status': lib['status'], 'dir_rel': VIEWS_REL,
                  'n_files': lib['n_files'], 'n_compliant': lib['n_compliant'],
                  'n_quarantined': lib['n_quarantined'],
                  'quarantined': lib['quarantined'],
                  'manifest': lib['manifest']},
        'withheld_after_cutoff': withheld, 'out_of_scope_rows': out_scope,
        'pricing': pricing, 'pricing_coverage': coverage, 'rows': rows,
        'ex_post': ex_post, 'disagreements': _disagreements(rows),
        'falsification_pool': fals, 'assumption_pool': assum,
        'risk_pool': risk, 'gaps': gaps, 'summary': summary,
        'view_statements': stmts,
        'version_binding': {
            'as_of': eg.get('as_of') or as_of,
            'source_snapshot_id': (eg.get('source_snapshot_id')
                                   or (snap or {}).get('snapshot_id')),
            'source_target_date': (eg.get('source_target_date')
                                   or _iso8((snap or {}).get('target_date'))),
            'historical_view': bool(eg.get('historical_view')),
            'value_version': eg.get('vintage'),
            'pricing_source': pricing['basis'],
            'pricing_source_snapshot_id': pricing['source_snapshot_id'],
            'views_dir': VIEWS_REL, 'views_status': lib['status'],
            'target_map': TARGET_MAP_REL if tm else None},
        'frozen_inputs': frozen,
        'metrics_used': used, 'metrics_absent': absent,
        'falsification_window': window, 'window_testability': wt,
        'rules': [
            '可见性: 机构观点 publish_date ≤ 研究截止日;截止后发布的观点整篇不入',
            '出处: 只取观点库登记为 institution_stated 的行;库内 ai_inferred 行不对照',
            '路径相容界: 机构「M 月加息 Xbp」→ M 月合约月均较前一月应落在 [前月累计+X/当月天数, 前月累计+X]',
            '路径终点: 机构最后一步之后的首个完整月,市场累计−机构累计,幅度≥半步(%gbp)才算预期差' % MATERIAL_GAP_BP,
            '市场定价=联邦基金利率期货合约月均隐含有效利率(月均口径,非时点口径);基线=截止日有效利率(备选=目标区间中点)',
            '文字/多值点位引擎不解读(须席位推导并标「席位推导」);未映射目标/缺席定价/缺席序列逐项列缺口',
            '事后核验只对已到期点位按到期日附近事实读数判定;未到期不判定'],
    }
    block['summary']['blocked_class'] = blocked_class(block)
    return block


def blocked_class(block):
    """缺口分级: None=可交付;views_absent/no_comparables=草稿级(可交草稿,
    归档拒);块缺席由调用方按 expectations_gap_block_missing 处理。"""
    if not isinstance(block, dict) or block.get('schema') != SCHEMA:
        return BLOCK_MISSING
    if (block.get('views') or {}).get('status') != 'present':
        return VIEWS_ABSENT
    if not (block.get('summary') or {}).get('comparable_n'):
        return NO_COMPARABLES
    return None



# ── 计划内块的读取/分级/冻结输入合并(编排器·计划段·attach·渲染共用) ───────

def plan_asked(plan):
    """计划是否问到预期差(计划键 expectations_gap.asked)。"""
    blk = (plan or {}).get('expectations_gap')
    return isinstance(blk, dict) and bool(blk.get('asked'))


def plan_block(plan):
    """计划内预期差对照块(问到且块完整)→块;未问到/块缺席或损坏→None。"""
    blk = (plan or {}).get('expectations_gap')
    if not isinstance(blk, dict) or not blk.get('asked'):
        return None
    return blk if blk.get('schema') == SCHEMA else None


def plan_blocked_class(plan):
    """计划级分级(渲染草稿横幅/attach 阻断/计划段缺口同一判定)。"""
    if not plan_asked(plan):
        return None
    blk = plan_block(plan)
    return blocked_class(blk) if blk is not None else BLOCK_MISSING


def draft_banner(code):
    """首页草稿横幅(与 blocked_class 共源;文案随分级码)。"""
    if code == BLOCK_MISSING:
        return ('> ⚠ **草稿(非正式)**: **预期差对照块缺席**——问到预期差但研究'
                '计划未生成对照块: 机构观点×同期限市场定价×事实的对照不可做;'
                '补齐数据(运行快照)后重跑转正。正式归档对草稿拒绝'
                '(%s)。' % BLOCK_MISSING)
    if code == VIEWS_ABSENT:
        return ('> ⚠ **草稿(非正式)**: **机构观点库不在场**——问到预期差但 '
                '%s 缺席(或无合规文档): 机构观点对照不可做,预期差判定只交'
                '草稿;随迁已授权观点库(只读副本+sha256 清单)后重跑转正。'
                '正式归档对草稿拒绝(%s)。' % (VIEWS_REL, VIEWS_ABSENT))
    if code == NO_COMPARABLES:
        return ('> ⚠ **草稿(非正式)**: **预期差对照无可对账行**——观点库在场,'
                '但问句范围内没有一条机构观点能与同期限市场定价或事实对账'
                '(目标未映射/序列缺席/定价缺席/点位不可解析,逐项见「缺口」);'
                '预期差判定只交草稿。正式归档对草稿拒绝(%s)。' % NO_COMPARABLES)
    return '> ⚠ **草稿(非正式)**: 预期差对照缺口(%s)。' % code


def merge_frozen_inputs(frozen, block, root, snapshot_rel=None,
                        snapshot_sha=None):
    """对照面读过的观点库文件(可见文档)与规范目标映射并入运行冻结输入
    (键=相对 root 的路径,值=sha256 前 16 位;None 值=占位,不并入)。
    运行末尾复核: 本地文件与块内清单摘要不一致=对照面已变→响亮失败。
    运行快照由调用方按运行快照字节回填(placeholder 键先移除)。"""
    out = dict(frozen or {})
    blk_frozen = (block or {}).get('frozen_inputs') or {}
    for rel, sha in sorted(blk_frozen.items()):
        if not sha:
            continue
        fp = os.path.join(root, rel)
        cur = (_sha256_file(fp)[:16] if os.path.isfile(fp) else None)
        if cur != sha:
            raise RuntimeError(
                'expectations_gap_frozen_input_changed: %s 运行期间已变(块内 '
                '%s,盘面 %s)——对照面与冻结输入不一致,本次运行作废后重跑'
                % (rel, sha, cur))
        out[rel] = sha
    if snapshot_rel:
        out[snapshot_rel] = snapshot_sha
    return out


# ── 证据索引 / 页眉数据门对照 ─────────────────────────────────────────

def evidence_rows(block, existing_refs=()):
    """预期差块引用行→证据索引行(按 ref 去重): 观点库文档(institution_view)/
    库内预测行(institution_forecast)/市场定价(market_pricing)/序列读数点
    (plan_series_point)——席位判断的 evidence_refs 可解析、可核。"""
    have = set(existing_refs or ())
    out = []

    def _add(ref, kind, mid):
        if not ref or ref in have:
            return
        have.add(ref)
        out.append({'ref': ref, 'kind': kind, 'metric_id': mid,
                    'role': 'expectations_gap'})

    for r in (block or {}).get('rows') or []:
        for ref in r.get('evidence_refs') or []:
            if ref == r.get('view_id'):
                kind = 'institution_view'
            elif ref == r.get('row_id'):
                kind = 'institution_forecast'
            elif ref.startswith('FEDFUNDS_FUT:'):
                kind = 'market_pricing'
            else:
                kind = 'plan_series_point'
            _add(ref, kind, r.get('metric_id'))
    return out


def gate_note(header_lines, block, snap):
    """页眉数据门(Gate A)记的是源快照的**当日采集面**;预期差对照的事实读数取
    快照**序列面**(series_store)——同一指标两面状态可以不同。本面对照用到
    的指标逐个对照两面,免得页眉「不得进入研究结论」与正文取数互相打架;本面
    指标不在缺席/降级名单=页眉原样。
    → (页眉行的替换行 or None, 追加行列表)"""
    ga = snap.get('gate_a') if isinstance(snap, dict) else None
    if not isinstance(block, dict) or not isinstance(ga, dict):
        return None, []
    miss = (list(ga.get('core_missing') or [])
            + list(ga.get('noncore_missing') or []))
    degr = list(ga.get('noncore_degraded') or [])
    detail = ga.get('noncore_missing_detail') or {}
    use = {}
    for r in block.get('rows') or []:
        mid = r.get('metric_id')
        if not mid or r.get('status') == 'unmapped':
            continue
        fc = (r.get('facts') or {}).get('at_cutoff') or {}
        if fc.get('status') == 'ok':
            use.setdefault(mid, '预期差对照取序列面读数 %s(%s 观测)'
                           % (fc.get('value'), fc.get('observation_date')))
        else:
            use.setdefault(mid, '序列面在截止日无读数→该行按缺口列出')
    items = []
    for mid, role in use.items():
        if mid in miss:
            d = detail.get(mid) if isinstance(detail, dict) else None
            items.append('%s 当日采集面缺席%s——%s'
                         % (mid, '(%s)' % d if d else '', role))
        elif mid in degr:
            items.append('%s 当日采集面降级——%s' % (mid, role))
    if not items:
        return None, []
    old = ('——缺席/降级数据不得进入研究结论;逐指标注记见快照 '
           'gate_a.noncore_missing_detail,信封步状态见步骤台账')
    new = ('——采集面缺席/降级的当日事实不入证据面;本问预期差对照改取序列面'
           '读数的指标见下行两面对照;逐指标注记见快照 gate_a.noncore_'
           'missing_detail,信封步状态见步骤台账')
    for ln in header_lines:
        if ln.startswith('- 数据门(Gate A') and ln.endswith(old):
            return (ln[:-len(old)] + new), [
                '  - 本问指标两面对照(Gate A=当日采集面;预期差对照的事实读数取'
                '快照序列面 series_store,同指标两面状态可不同): '
                + ' | '.join(items)]
    return None, []


# ── 读者报告追加节(纯 report.json 装配: 引擎确定性面 + 席位原文) ─────────

_STATUS_TEXT = {
    'consistent': '一致', 'inconsistent': '不一致(引擎候选)',
    'consistent_stale_fact': '一致(陈旧读数)', 'no_longer_current': '已过时',
    'fact_mismatch': '与事实不符', 'unverifiable': '不可核',
    'not_comparable': '不可对照', 'context_only': '只列背景',
    'reading_required': '须席位推导', 'series_absent': '序列缺席',
    'unmapped': '未映射', 'unparseable_horizon': '期限不可解析',
    'library_inferred': '库内推导行(不对照)',
    'ex_post_consistent': '事后一致', 'ex_post_missed': '事后未兑现'}
_KIND_TEXT = {
    'path_vs_pricing': '政策路径对定价', 'hike_count_vs_pricing': '次数对定价',
    'level_vs_fact': '水平对事实', 'ex_post_level': '到期对事实'}
_ATTR_TEXT = {'institution_stated': '机构原话', 'ai_inferred': '席位推导',
              'engine_rule': '引擎规则'}


def _cell(v):
    t = '' if v is None else str(v)
    return t.replace('|', '\\|').replace('\n', ' ').strip() or '—'


def _spread_txt(d):
    """机构间分歧的数值幅度段(修订 r14,独立审查 NIT-4): 可折算为基点时与
    旧渲染逐字相同(「X bp——说明」);不可折算为基点(点位对增速等口径不同)
    时写明口径,说明缺席时不再输出「———」。"""
    v = d.get('numeric_spread_bp')
    note = _cell(d.get('spread_note'))
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return '%s bp——%s' % (_cell(v), note)
    return '不可折算为基点(口径不同或不可比)' + (
        '' if note in ('—', '-', '') else '——' + note)


def _signed(v, nd=2):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return '—'
    return '%+.*f' % (nd, v)


def _refs_text(refs, n=4):
    refs = [str(x) for x in refs or []]
    if not refs:
        return '—'
    return '; '.join(refs[:n]) + ('(+%d)' % (len(refs) - n) if len(refs) > n
                                  else '')


def render_gap_sections(block, rm):
    """预期差追加节(读者可直读可核查): 口径与规则→市场定价面→逐行对照→
    分歧→事后表现→证伪条件/假设池→缺口→席位判断。block 缺席/损坏=缺席
    注记;渲染只读本块与席位原文,不读观点库与快照(重放=纯函数)。"""
    lines = ['## 预期差对照(机构观点 × 同期限市场定价 × 事实)', '']
    if not isinstance(block, dict) or block.get('schema') != SCHEMA:
        lines += ['**缺席**——研究计划未生成预期差对照块(缺口: 面块缺席)', '']
        return lines
    sm = block.get('summary') or {}
    vw = block.get('views') or {}
    pr = block.get('pricing') or {}
    rows = block.get('rows') or []
    ex = block.get('ex_post') or {}
    n_cs = sum(1 for r in rows
               if r.get('comparable_kind') == 'level_vs_fact')
    n_other = sm.get('n_rows', 0) - sum(
        sm.get(k) or 0 for k in (
            'comparable_n', 'reading_required_n', 'context_only_n',
            'unmapped_n', 'series_absent_n'))
    lines += [
        '- 观点库: 可见 %s 份(发布日 ≤ 研究截止日 %s;目录 %s,隔离 %s 份;'
        '截止后发布扣留 %s 份;范围外 %s 条不列);机构预测/表述 %s 行'
        % (sm.get('n_views_visible'), block.get('as_of'), vw.get('dir_rel'),
           vw.get('n_quarantined'), sm.get('n_views_withheld'),
           sm.get('n_out_of_scope'), sm.get('n_rows')),
        '- 对照结果: 可对账 %s 行(政策路径/次数对定价 %s / 当前水平对事实 %s /'
        ' 已到期点位对事实 %s)——一致 %s,不一致(引擎候选) %s,陈旧读数上一致 %s;'
        '事后核验一致 %s、未兑现 %s'
        % (sm.get('comparable_n'), sm.get('path_n'), n_cs,
           ex.get('forecast_claims', {}).get('n', 0)
           + ex.get('realized_data_claims', {}).get('n', 0),
           sm.get('consistent_n'), sm.get('inconsistent_n'),
           sm.get('stale_fact_n'), sm.get('ex_post_consistent_n'),
           sm.get('ex_post_missed_n')),
        '- 不可对账: 须席位推导 %s,只列背景 %s,未映射目标 %s,序列缺席 %s,'
        '其他 %s——逐行见下,缺口逐项点名'
        % (sm.get('reading_required_n'), sm.get('context_only_n'),
           sm.get('unmapped_n'), sm.get('series_absent_n'), n_other),
        '- 引擎数值候选 %s 条(候选≠结论——是否构成预期差见「Agent 席判断」);'
        '证据缺口 %s 项' % (sm.get('candidate_n'), sm.get('gaps'))]
    bc = blocked_class(block)
    lines.append('- 分级: %s' % (
        '可对照(观点库在场且有可对账行)' if bc is None else
        '草稿(%s)——%s' % (bc, _blocked_text(bc))))
    lines += ['- 规则(引擎,随面披露):'] + [
        '  - %s' % x for x in block.get('rules') or []]
    vb = block.get('version_binding') or {}
    lines.append(
        '- 版本绑定: 研究截止日 %s | 源快照 %s(版本日 %s) | 定价来源 %s(%s) | '
        '观点库 %s(%s) | 规范目标映射 %s | 冻结输入 %s 件(随包 root_overlay)'
        % (vb.get('as_of'), vb.get('source_snapshot_id'),
           vb.get('source_target_date'), vb.get('pricing_source'),
           vb.get('pricing_source_snapshot_id'), vb.get('views_dir'),
           vb.get('views_status'), vb.get('target_map'),
           len([1 for v in (block.get('frozen_inputs') or {}).values()
                if v])))
    lines.append('')
    # 市场定价面
    lines += ['### 市场定价面(同期限)', '']
    if pr.get('status') == 'present':
        base = pr.get('baseline') or {}
        mid = pr.get('midpoint') or {}
        spread = max((abs((r.get('change_bp') or 0.0)
                          - (r.get('change_bp_mid') or 0.0))
                      for r in pr.get('rows') or []), default=0.0)
        lines.append(
            '- 工具: %s | 来源: %s %s(版本日 %s,观测 %s) | 基线=截止日有效利率 '
            '%s %s(%s) | 备选基线=目标区间中点 %s(两口径累计变动最大差 %.1f bp)'
            % (pr.get('instrument'), pr.get('basis'),
               pr.get('source_snapshot_id'), pr.get('source_target_date'),
               pr.get('observed_at'), base.get('value'), base.get('unit'),
               base.get('evidence_ref'), mid.get('value'), spread))
        lines += [
            '', '| 合约月 | 合约 | 隐含月均利率 | 累计变动 bp(有效利率基) | '
            '累计变动 bp(目标中点基) | 截止日后整月 | 证据 |',
            '|---|---|---|---|---|---|---|']
        for r in pr.get('rows') or []:
            lines.append('| %s | %s | %s | %s | %s | %s | %s |' % (
                r.get('month'), r.get('ticker'),
                ('%s%%' % r['implied_avg_rate'])
                if r.get('implied_avg_rate') is not None else '—',
                _signed(r.get('change_bp'), 1), _signed(r.get('change_bp_mid'), 1),
                '是' if r.get('full_month_ahead') else '否(截止当月,不完整)',
                r.get('evidence_ref')))
        for r in pr.get('skipped_rows') or []:
            lines.append('- 未入面合约: %s(%s)——%s'
                         % (r.get('ticker'), r.get('name'), r.get('reason')))
        lines.append('- 口径: %s;步长 %gbp,预期差候选阈值=半步 %gbp(引擎规则)'
                     % (pr.get('basis_note'), pr.get('step_bp'),
                        pr.get('material_gap_bp')))
        for g in pr.get('gaps') or []:
            lines.append('- 定价面缺口: %s' % g.get('note'))
    else:
        for g in pr.get('gaps') or []:
            lines.append('- **同期限市场定价缺席**: %s' % g.get('note'))
    lines.append('')
    cov = block.get('pricing_coverage') or {}
    lines += ['同期限定价覆盖(问句范围内各经济体政策利率):', '',
              '| 经济体 | 政策利率指标 | 同期限市场定价 | 工具 |', '|---|---|---|---|']
    for eco in _REGION_ORDER:
        c = cov.get(eco)
        if not c:
            continue
        lines.append('| %s | %s | %s | %s |' % (
            _REGION_LABEL.get(eco, eco), c.get('metric_id'),
            '在场' if c.get('status') == 'present' else '缺席(无同期限定价工具)',
            c.get('instrument') or '—'))
    lines.append('')
    # 逐行对照
    main_rows = [r for r in rows if r.get('status') != 'unmapped']
    lines += [
        '### 逐行对照(引擎确定性面;每行附证据引用)', '',
        '| 行 | 机构 | 发布日 | 目标 → 指标 | 机构原话 | 点位 | 到期 | 对照口径 | '
        '判定 | 依据 | 证据 |',
        '|---|---|---|---|---|---|---|---|---|---|---|']
    for r in main_rows:
        basis = _cell(r.get('basis_note'))
        if r.get('candidate') is True and r.get('candidate_reason'):
            basis += ';候选原因: %s' % _cell(r.get('candidate_reason'))
        lines.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            _cell(r.get('row_id')), _cell(r.get('institution')),
            _cell(r.get('publish_date')),
            _cell('%s → %s' % (r.get('target'), r.get('metric_id') or '—')),
            _cell(r.get('value_raw')), _cell(r.get('point_text')),
            _cell(r.get('horizon_end')
                  or ('—(当前状态)' if r.get('maturity') == 'CURRENT_STATE'
                      else r.get('horizon_raw'))),
            _KIND_TEXT.get(r.get('comparable_kind'), '—'),
            _STATUS_TEXT.get(r.get('status'), _cell(r.get('status')))
            + (' ⚠ 引擎候选' if r.get('candidate') is True else ''),
            basis, _refs_text(r.get('evidence_refs'))))
    un = [r for r in rows if r.get('status') == 'unmapped']
    lines += ['', '未映射目标行(%d 行;无在册事实/同期限定价可对账——逐行列缺口,'
              '不作预期差判定):' % len(un), '',
              '| 行 | 机构 | 发布日 | 目标 | 原话 | 到期 |', '|---|---|---|---|---|---|']
    for r in un:
        lines.append('| %s | %s | %s | %s | %s | %s |' % (
            _cell(r.get('row_id')), _cell(r.get('institution')),
            _cell(r.get('publish_date')), _cell(r.get('target')),
            _cell(r.get('value_raw')), _cell(r.get('horizon_end') or '—')))
    lines.append('')
    # 机构间分歧
    dis = block.get('disagreements') or []
    lines += ['### 机构间分歧(同指标多机构;引擎只列幅度,不裁对错)', '']
    if not dis:
        lines.append('(问句范围内无同指标多机构行)')
    for d in dis:
        lines += [
            '- **%s**(%s 家机构 %s 行;数值幅度 %s):' % (
                _cell(d.get('metric_id')), len(d.get('institutions') or []),
                d.get('n_rows'), _spread_txt(d))]
        for x in d.get('rows') or []:
            lines.append('  - %s %s「%s」(发布 %s;到期 %s;引擎 %s)' % (
                _cell(x.get('row_id')), _cell(x.get('institution')),
                _cell(x.get('point_text')), _cell(x.get('publish_date')),
                _cell(x.get('horizon_end') or '—'),
                _STATUS_TEXT.get(x.get('status'), _cell(x.get('status')))))
    lines.append('')
    # 事后表现
    lines += ['### 事后表现(到期点位对事实;未到期不判定)', '',
              '- %s' % _cell(ex.get('note')), '',
              '| 行 | 机构 | 发布日 | 指标 | 点位 | 到期日 | 事实读数(观测日) | 差 | 判定 |',
              '|---|---|---|---|---|---|---|---|---|']
    n_ex = 0
    for part in ('forecast_claims', 'realized_data_claims'):
        for x in (ex.get(part) or {}).get('rows') or []:
            n_ex += 1
            lines.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                _cell(x.get('row_id')), _cell(x.get('institution')),
                _cell(x.get('publish_date')), _cell(x.get('metric_id')),
                _cell(x.get('point_text')), _cell(x.get('horizon_end')),
                _cell(x.get('fact_value')), _signed(x.get('diff'), 2),
                _STATUS_TEXT.get(x.get('verdict'), _cell(x.get('verdict')))))
    if not n_ex:
        lines.append('| (无已到期且可核的行) | | | | | | | | |')
    ny = ex.get('not_yet_testable') or {}
    lines += ['- 未到期 %s 条(最早到期 %s):不作判定' % (
                  ny.get('n'), ny.get('earliest_horizon_end') or '—'), '']
    # 证伪窗口(问句指定时)
    win = block.get('falsification_window')
    wt = block.get('window_testability')
    if isinstance(win, dict) and isinstance(wt, dict):
        rw = wt.get('rows_in_window') or []
        lines += ['### 证伪窗口(问句「%s」: 研究截止日 %s → 窗末 %s)' % (
                      _cell(win.get('source')), _cell(win.get('start')),
                      _cell(win.get('end'))), '',
                  '- 窗内到期的机构点位 %s 行(到期即可按事实/同期限定价核验;'
                  '可核性逐行标注):' % len(rw), '',
                  '| 行 | 机构 | 指标 | 点位 | 到期 | 引擎判定 | 到期可核 |',
                  '|---|---|---|---|---|---|---|']
        for x in rw:
            lines.append('| %s | %s | %s | %s | %s | %s | %s |' % (
                _cell(x.get('row_id')), _cell(x.get('institution')),
                _cell(x.get('metric_id')), _cell(x.get('point_text')),
                _cell(x.get('horizon_end')),
                _STATUS_TEXT.get(x.get('status'), _cell(x.get('status'))),
                '是' if x.get('testable') else '否(未映射/缺席/口径不同)'))
        if not rw:
            lines.append('| (无) | | | | | | |')
        lines += [
            '- 窗外到期 %s 行(最早 %s): 窗口内不判定' % (
                wt.get('n_rows_after_window'),
                wt.get('earliest_after_window') or '—'),
            '- 引擎事后核验规则: 窗内 %s 条(%s) / 窗外 %s 条' % (
                len(wt.get('engine_rules_in_window') or []),
                '; '.join(wt.get('engine_rules_in_window') or []) or '无',
                len(wt.get('engine_rules_after_window') or [])),
            '- 观点库证伪条件 %s 条不带观察日期——是否落在窗口内、以何指标观察,'
            '由席位判断(见 Agent 席判断)' % wt.get('n_view_library_conditions'),
            '- 口径: %s' % _cell(wt.get('note')), '']
    # 证伪条件 / 假设 / 风险池
    pool = block.get('falsification_pool') or []
    lib_st = [p for p in pool if p.get('source') == 'view_library'
              and p.get('attribution') == 'institution_stated']
    lib_ai = [p for p in pool if p.get('source') == 'view_library'
              and p.get('attribution') != 'institution_stated']
    eng_r = [p for p in pool if p.get('source') == 'engine_rule']
    assum = block.get('assumption_pool') or []
    risk = block.get('risk_pool') or []
    lines += [
        '### 证伪条件、关键假设与风险(机构原文优先;库内推导与引擎规则分列)', '',
        '- **机构原文证伪条件(%d 条;席位引用须逐字并标「机构原话」)**:' % len(lib_st)]
    lines += ['  - `%s` %s: %s' % (_cell(p.get('id')), _cell(p.get('institution')),
                                   _cell(p.get('condition')))
              for p in lib_st] or ['  - (无)']
    lines.append('- 库内推导证伪条件(%d 条;非机构原话,仅供参考——不得标「机构原话」):'
                 % len(lib_ai))
    lines += ['  - `%s` %s: %s' % (_cell(p.get('id')), _cell(p.get('institution')),
                                   _cell(p.get('condition')))
              for p in lib_ai] or ['  - (无)']
    lines.append('- 引擎事后核验规则(%d 条;已到期判据,随行披露):' % len(eng_r))
    lines += ['  - `%s`: %s' % (_cell(p.get('id')), _cell(p.get('condition')))
              for p in eng_r] or ['  - (无)']
    lines.append('- 机构关键假设(%d 条):' % len(assum))
    lines += ['  - `%s` %s%s: %s' % (
                  _cell(p.get('id')), _cell(p.get('institution')),
                  '' if p.get('attribution') == 'institution_stated'
                  else '(库内推导)', _cell(p.get('statement')))
              for p in assum] or ['  - (无)']
    lines.append('- 机构风险因素(%d 条):' % len(risk))
    lines += ['  - `%s` %s%s: %s' % (
                  _cell(p.get('id')), _cell(p.get('institution')),
                  '' if p.get('attribution') == 'institution_stated'
                  else '(库内推导)', _cell(p.get('statement')))
              for p in risk] or ['  - (无)']
    lines.append('')
    # 缺口
    gaps = block.get('gaps') or []
    lines += ['### 缺口(逐项点名;缺证=缺证,不以推断补)', '',
              '| 缺口 | 经济体 | 指标 | 说明 |', '|---|---|---|---|']
    for g in gaps:
        lines.append('| %s | %s | %s | %s |' % (
            _cell(g.get('code')),
            _REGION_LABEL.get(g.get('region'), g.get('region') or '—'),
            _cell(g.get('metric_id')), _cell(g.get('note'))))
    if not gaps:
        lines.append('| (无) | | | |')
    wh = block.get('withheld_after_cutoff') or []
    if wh:
        lines += ['', '截止后发布、整篇扣留的观点(%d 份;不入对照):' % len(wh)]
        lines += ['  - %s(%s;发布 %s)' % (_cell(x.get('view_id')),
                                           _cell(x.get('institution')),
                                           _cell(x.get('publish_date')))
                  for x in wh]
    oos = block.get('out_of_scope_rows') or []
    if oos:
        lines += ['', '问句范围外的行(%d 条;不对照): %s' % (
            len(oos), '; '.join('%s(%s)' % (x.get('row_id'), x.get('target'))
                                for x in oos))]
    lines.append('')
    lines += render_seat_section(rm, block)
    return lines


def _blocked_text(code):
    return {VIEWS_ABSENT: '观点库不在场——机构观点对照不可做;须随迁已授权观点库'
             '(只读副本+sha256 清单)后重跑',
            NO_COMPARABLES: '观点库在场但无可对账行——机构观点与市场定价/'
            '事实的对照未成立,只能交草稿'}.get(code, '预期差对照块缺席')


def render_seat_section(rm, block=None):
    """席位预期差判断节(席位原文照录;逐行带引擎面的机构/目标,便于对照)。
    席位未提交=如实注记(引擎候选与须推导行悬而未裁)。"""
    lines = ['## Agent 席判断(预期差;席位原文,数值与引擎面对账后方可落位)', '']
    egs = (rm or {}).get('expectations_gap')
    if not isinstance(egs, dict) or not egs:
        sm = (block or {}).get('summary') or {}
        lines.append('(席位未提交预期差判断——引擎候选 %s 条、须席位推导 %s 行悬而'
                     '未裁)' % (sm.get('candidate_n'), sm.get('reading_required_n')))
        return lines + ['']
    by_id = {r.get('row_id'): r for r in (block or {}).get('rows') or []}
    lines += ['席位总述: %s' % _cell(egs.get('seat_summary')), '']
    we = egs.get('window_echo')
    if isinstance(we, dict) and we.get('start') and we.get('end'):
        lines.append('- 席位证伪窗口回声: 研究截止日 %s → 窗末 %s(%s 个月)'
                     % (_cell(we.get('start')), _cell(we.get('end')),
                        _cell(we.get('months'))))
    sup = [g for g in egs.get('supported_gaps') or [] if isinstance(g, dict)]
    lines += ['### 席位判定(逐行)', '',
              '| 行 | 机构 / 目标 | 席位判定 | 席位解读 | 竞争解释 | 证伪条件 | '
              '理由 — 证据 |',
              '|---|---|---|---|---|---|---|']
    for g in sup:
        r = by_id.get(g.get('row_id')) or {}
        conds = []
        for c in g.get('falsification_conditions') or []:
            if isinstance(c, dict):
                conds.append('%s(%s%s)' % (
                    _cell(c.get('condition')),
                    _ATTR_TEXT.get(c.get('attribution'),
                                   c.get('attribution') or '—'),
                    ';%s' % c['source_ref'] if c.get('source_ref') else ''))
        verdict = ('支持(预期差成立)' if g.get('verdict') == 'supported'
                   else '判非预期差' if g.get('verdict') == 'not_a_gap'
                   else _cell(g.get('verdict')))
        reading = _cell('%s(%s)' % (
            g.get('reading'),
            _ATTR_TEXT.get(g.get('reading_attribution'),
                           g.get('reading_attribution') or '—')))
        lines.append('| %s | %s | %s | %s | %s | %s | %s — 证据: %s |' % (
            _cell(g.get('row_id')),
            _cell('%s / %s' % (r.get('institution'), r.get('target'))),
            verdict, reading, _cell(g.get('competing_explanation')),
            _cell('; '.join(conds) or '—'), _cell(g.get('reason')),
            _refs_text(g.get('evidence_refs'))))
    if not sup:
        lines.append('| (无) | | | | | | |')
    lines.append('')
    ku = [x for x in egs.get('key_unknowns') or [] if str(x).strip()]
    lines.append('关键未知(%d):' % len(ku))
    lines += ['- %s' % _cell(x) for x in ku] or ['- (无)']
    cm = [x for x in egs.get('comments') or [] if str(x).strip()]
    if cm:
        lines.append('')
        lines.append('席位补充说明:')
        lines += ['- %s' % _cell(x) for x in cm]
    lines.append('')
    return lines
