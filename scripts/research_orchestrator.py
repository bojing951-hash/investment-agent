#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R2 一键研究编排器(AC6): Skill 十一步研究工作流的可执行化。

定位与边界(零模型诚实面):
- 本编排器只执行**确定性步骤**(体检/事实基线/历史/对比/类比/接地问答/
  观点面装载/lint 自检/落档开关),每步=真 ia_cli 子进程或既有库装载,
  信封原样留档——步骤成败与语义成败分开记录。
- 拆问题(自然语言)/主要矛盾综合/条件推演五行=编排层 Agent 工作,
  本管线不产出: L3(AI推断)/L4(条件情景) 两层恒 declared-not-produced,
  报告明示"本层结论须 Agent 补作并标 attribution",绝不代写。
- 实体映射=确定性词面匹配(metric_id/display_name 大小写折叠子串+
  经济体中文标签反查),匹配不到就如实 unmapped,零翻译零猜测。

四层区分(L1-L4)与逐数证据索引(evidence_index: 每个数字行带
fact_id/view_id 级来源)随报告落盘 report.json+report.md。

纯函数入口: run_research(question, root=None, archive=False, out_dir=None,
ia_timeout=180) → dict(ia_cli research-run 与测试共用)。
"""
import json
import os
import re
import subprocess
import sys
import time
from datetime import date, datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
SCRIPTS = os.path.join(ROOT, 'scripts')
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

PIPELINE_VERSION = '2.0'
IA_CLI = os.path.join(ROOT, 'ia_cli.py')
# Audit-R4 条目5 登记值: 必要指标最低覆盖兜底(问题未限定时间范围时的
# 频率族下界)。Audit-R5 条目2 收紧: **不得统一用"至少 N 个观测"替代
# 原任务所需历史范围**——问题词面限定范围(近/过去 N 年)时按
# N 年×频率年观测数推导;月频 10 年≈120、日频年千计,兜底只拦
# 「最新单点/极短序列冒充历史分析面」;冻结进每项
# spec.min_observations(含推导口径),不随采集结果改判。
_REQ_MIN_OBSERVATIONS = 12
_REQ_MIN_OBSERVATIONS_BY_FREQ = {'daily': 60, 'weekly': 26,
                                 'monthly': 12, 'quarterly': 4}
_OBS_PER_YEAR_BY_FREQ = {'daily': 252, 'weekly': 52,
                         'monthly': 12, 'quarterly': 4}
# Audit-R6 条目2(R6-01): 任务窗口边界容忍(天)——研究时点倒推 N 年为
# [start,end],序列须**跨越**该窗(首观测≤start+容差、末观测≥end-容差,
# 且窗内有效观测数≥下界半额)——按真实时间边界+交易日历判,不以
# 252×年数 总量代替窗口归属。容差按频率族: 日频含周末+节假日簇,
# 周频含停发周;月频/季频含**发布滞后**(PMI 月末+1日/贷款月中发布,
# 季频+1月惯例)。未知频率不获宽容差(窗口不可核验即阻断)。
_WINDOW_TOL_DAYS = {'daily': (14, 10), 'weekly': (21, 14),
                    'monthly': (62, 75), 'quarterly': (95, 130)}
# 窗内有效观测下界系数(允许缺口=节假日/停发/合理缺席,至多一半缺失)
_WINDOW_N_FRACTION = 0.5
# Audit-R7 条目1(R7-01)严重断档容忍(天): 窗内相邻有效观测最大间距
# 超过频率族上限=严重断档(连续缺席),即便总量过半也阻断——日频容
# 节假日簇+停市周(30天),周频容停发月,月频容+1季发布停滞,季频容
# +半年。缺口容忍规则显式登记于此,不隐式摊在总量里。
_WINDOW_MAX_GAP_DAYS = {'daily': 30, 'weekly': 60,
                        'monthly': 130, 'quarterly': 260}
# 问题词面时间范围提取(Audit-R5 条目2): 仅认**状语性**范围——
# 近/过去/最近 N 年 或 N 年内/N 年以来;「十年期美债」类资产名
# (N 年+期/收益率)与四位年份不匹配,防止把资产名误当任务范围。
_RANGE_YEARS_RE = re.compile(
    r'(?:近|最近|过去)(一|两|二|三|四|五|六|七|八|九|十|\d+)\s*年'
    r'|(?<![\d])(\d+|一|两|二|三|四|五|六|七|八|九|十)\s*年(?:以内|以来|内)')
# R9-02: 相对月数词形(近/最近/过去 N 个月;N 个月以内/以来/内)——与
# 年限词形同构,单位=月;判定器按研究时点倒推 N 个自然月(研究时点
# 不可核验=窗口不可核验,不回落 max_available)。
_RANGE_MONTHS_RE = re.compile(
    r'(?:近|最近|过去)(一|两|二|三|四|五|六|七|八|九|十|\d+)\s*个月'
    r'|(?<![\d])(\d+|一|两|二|三|四|五|六|七|八|九|十)\s*个月(?:以内|以来|内)')
# R9-02: 时间意图在场但表达未支持——诚实失败(unparseable 阻断),
# 不与「没有时间要求」混同退化为 max_available。确定性词面匹配,
# 资产名护栏: 上/本周不带「期」(防「上周期」);年序词不含十年期类
# 期限(需 年初/年中/年末 等完整词);季度须带上/本/下限定词。
_QTIME_UNSUPPORTED_RE = re.compile(
    r'(今年|明年|后年|大前年|上半年|下半年|年初|年中|年末|月初|月底|月末'
    r'|上(?:个)?季度|本季度|下(?:个)?季度|这(?:个)?季度'
    r'|上周(?!期)|本周(?!期)|这周(?!期)|下周(?!期)'
    r'|上(?:个)?月|本月|这(?:个)?月|下(?:个)?月|当月'
    r'|(?:近|最近|过去)\s*(?:\d+|[一两二三四五六七八九十])+\s*(?:周|星期|天|日)'
    r'|(?:\d+|[一两二三四五六七八九十])+\s*(?:周|星期|天|日)(?:以内|以来|内)'
    r'|(?:未来|接下来|此后)\s*(?:\d+|[一两二三四五六七八九十])+\s*'
    r'(?:年|个?月|周|星期|天|日))')
_CN_NUM = {'一': 1, '两': 2, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6,
           '七': 7, '八': 8, '九': 9, '十': 10}


def _question_range_years(question):
    """问题词面声明的分析年限(None=未限定)。

    只认状语性范围(近/过去/最近 N 年、N 年内/以来)——确定性词面
    匹配,不做语义改写;未限定返回 None(用频率族兜底下界)。
    多个匹配取**最大**(更严),资产名(十年期美债)不匹配。
    """
    years = []
    for m in _RANGE_YEARS_RE.finditer(question or ''):
        tok = m.group(1) or m.group(2)
        if tok is None:
            continue
        y = _CN_NUM.get(tok) if not tok.isdigit() else int(tok)
        if isinstance(y, int) and y > 0:
            years.append(y)
    return max(years) if years else None


def _question_range_months(question):
    """R9-02: 问题词面声明的相对月数(None=未限定)。

    与 _question_range_years 同构(近/最近/过去 N 个月、N 个月以内/
    以来/内);多个匹配取最大(更严);「六个月内」类资产/频率词不
    含「个月」量词不匹配。"""
    months = []
    for m in _RANGE_MONTHS_RE.finditer(question or ''):
        tok = m.group(1) or m.group(2)
        if tok is None:
            continue
        n = _CN_NUM.get(tok) if not tok.isdigit() else int(tok)
        if isinstance(n, int) and n > 0:
            months.append(n)
    return max(months) if months else None


def _shift_months(d, n):
    """自然月平移(负数=倒推;日按目标月长收敛,如 3/31−1月=2/28)。

    R9-02 相对月窗用——月粒度边界不引入日历库依赖,负向平移日不越界。"""
    y, m = d.year, d.month - 1 + n
    y, m = y + m // 12, m % 12 + 1
    import calendar as _cal
    day = min(d.day, _cal.monthrange(y, m)[1])
    return date(y, m, day)


# ── Audit-R7 条目1(R7-01): 明确日期区间解析 ─────────────────────────
# 日期词形(确定性词面,零语义改写): ISO 全日期/8位紧凑/中文年月日/
# 年月/年月横线/**斜杠日期**(R8-02: 2020/01/01 全日期与 2020/01 年月,
# 与横线同判)。裸四位数字**不认**(防把 2520 等数量词误当日份),
# 须带年字或全日期形态。数值词形带 (?<!\d)/(?!\d) 防从长数字串中
# 切出假日期。无法归一为合法日期(如 2020-13-45)=指定了但无法解析
# →阻断,不回落 max_available。
_QDATE_TOKEN_RE = re.compile(
    r'(?<!\d)(\d{4}-\d{1,2}-\d{1,2})(?!\d)|(?<!\d)(\d{4}/\d{1,2}/\d{1,2})(?!\d)|'
    r'(?<!\d)(\d{8})(?!\d)|'
    r'(\d{4}年(?:\d{1,2}月)?(?:\d{1,2}日)?)|(?<!\d)(\d{4}-\d{1,2})(?![-\d])|'
    r'(?<!\d)(\d{4}/\d{1,2})(?![\d/])')


def _norm_qdate(tok, side):
    """日期词形→(y, mo, d|None)三元组(不合法月份/日期直接 ValueError
    语义: 返回 None)。side 决定缺省侧: 'start'缺月日补期首;'end'
    缺月补 12/缺日补该月末日(「到2025年12月」=2025-12-31)。"""
    t = tok.strip()
    y = mo = d = None
    m = re.fullmatch(r'(\d{4})-(\d{1,2})-(\d{1,2})', t)
    if not m:
        m = re.fullmatch(r'(\d{4})/(\d{1,2})/(\d{1,2})', t)   # R8-02 斜杠全日期
    if not m:
        m = re.fullmatch(r'(?<!\d)(\d{4})(\d{2})(\d{2})(?!\d)', t)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
    else:
        m = re.fullmatch(r'(\d{4})年(?:(\d{1,2})月)?(?:(\d{1,2})日)?', t)
        if m:
            y = int(m.group(1))
            mo = int(m.group(2)) if m.group(2) else None
            d = int(m.group(3)) if m.group(3) else None
        else:
            m = re.fullmatch(r'(?<!\d)(\d{4})-(\d{1,2})(?![-\d])', t)
            if m is None:
                m = re.fullmatch(r'(?<!\d)(\d{4})/(\d{1,2})(?![\d/])', t)  # R8-02 斜杠年月
            if m:
                y, mo = int(m.group(1)), int(m.group(2))
    if y is None:
        return None
    if mo is not None and not (1 <= mo <= 12):
        return None
    if d is not None and not (1 <= d <= 31):
        return None
    if side == 'end':
        if mo is None:
            mo = 12
        if d is None:
            import calendar as _cal
            d = _cal.monthrange(y, mo)[1]
    else:
        mo = mo or 1
        d = d or 1
    try:
        return date(y, mo, d).isoformat()
    except ValueError:
        return None


def _valid_iso_date(s):
    try:
        date.fromisoformat(str(s)[:10])
        return True
    except (ValueError, TypeError):
        return False


def _question_window(question):
    """R7-01: 问题词面时间范围统一解析(相对年限+明确日期区间);
    R8-02: 斜杠日期词形+「去年」(自然年,绑定研究时点);
    R9-02: 三态固定——①未指定范围(None)②已指定且成功解析③已指定
    但无法解析(unparseable 阻断)。**只有①允许 max_available**;
    时间意图识别与窗口解析分离: 意图在场(日期词形/相对词形/未支持
    时间词)但窗口拿不出=③,不与①混同。

    返回:
      None                          未指定范围(max_available 口径)
      {'kind':'relative','years':N} 近/过去 N 年(端点=研究时点)
      {'kind':'relative_months',    近/过去 N 个月(端点=研究时点,
       'months':N}                  R9-02;时点不可核验=窗口不可核验)
      {'kind':'calendar_year',      「去年/前年」=研究时点上一/上上
       'offset':-1|-2,'raw':str}    自然年(相对词形绑定研究时点)
      {'kind':'explicit',           明确日期区间(start/end 任一侧可无界:
       'start':ISO|None,             'X以来'=起界无终界→end=研究时点;
       'end':ISO|None,               '截至X'=终界无起界→窗起=实际
       'raw':str}                     序列首观测,判定期数据面回填)
      {'kind':'unparseable',         指定了范围但无法解析/区间倒置/
       'reason':str,'raw':str}       表达未支持——阻断,不回落宽松
    显式区间与相对年限并存时显式区间胜(更具体,相对年限记入 basis)。
    未支持时间词(今年/明年/后年/季度/周天粒度/未来等)→unparseable
    带改写提示,诚实失败不猜(R9-02;不做自然语言全覆盖)。
    """
    q = question or ''
    toks = [(m.start(), m.end(), m.group(0))
            for m in _QDATE_TOKEN_RE.finditer(q)]
    parsed = []
    bad = []
    for (s, e, raw) in toks:
        iso = _norm_qdate(raw, 'start')      # 有效性试探(期首口径)
        if iso is None:
            bad.append(raw)
        else:
            parsed.append((s, e, raw))
    if bad:
        return {'kind': 'unparseable',
                'reason': f'日期词形 {bad[0]!r} 无法归一为合法日期',
                'raw': bad[0]}
    _unsup = _QTIME_UNSUPPORTED_RE.search(q)
    if not parsed:
        # 无日期词形→时间意图识别在先,窗口解析在后(R9-02 三态):
        # 未支持时间词→③阻断(先于支持词形判,混合表达不放过);
        # 相对月数(更紧)先于相对年限;自然年词形次之;无范围词=①。
        if _unsup:
            return {'kind': 'unparseable',
                    'reason': f'时间表达 {_unsup.group(0)!r} 未支持',
                    'raw': _unsup.group(0),
                    'hint': '请改用明确日期区间或受支持表达'
                            '(近/过去 N 年·N 个月、去年/前年、'
                            'X以来/截至X、ISO 或斜杠日期)'}
        _rm = _question_range_months(q)
        if _rm:
            return {'kind': 'relative_months', 'months': _rm}
        _ry = _question_range_years(q)
        if _ry:
            return {'kind': 'relative', 'years': _ry}
        if '去年' in q:
            # R8-02: 「去年」=上一自然年(确定性词形,零语义改写)
            return {'kind': 'calendar_year', 'offset': -1, 'raw': '去年'}
        if re.search(r'(?<!大)前年', q):
            # R9-02: 「前年」=上上自然年(反例A 词形;负向后视防
            # 「大前年」误切——大前年在未支持表)
            return {'kind': 'calendar_year', 'offset': -2, 'raw': '前年'}
        return None
    if len(parsed) == 1:
        s, e, raw = parsed[0]
        after = q[e:e + 6]
        before = q[max(0, s - 8):s]
        if re.match(r'\s*(以来|起|开始)', after):
            return {'kind': 'explicit',
                    'start': _norm_qdate(raw, 'start'), 'end': None,
                    'raw': raw + '以来'}
        if re.search(r'(截至|截止|直到)(于)?\s*$', before):
            return {'kind': 'explicit', 'start': None,
                    'end': _norm_qdate(raw, 'end'), 'raw': '截至' + raw}
        if _unsup:
            # 单日期提及≠区间,但未支持时间词在场=时间意图未解析
            # (R9-02: 不退化为 max_available)
            return {'kind': 'unparseable',
                    'reason': f'时间表达 {_unsup.group(0)!r} 未支持',
                    'raw': _unsup.group(0),
                    'hint': '请改用明确日期区间或受支持表达'
                            '(近/过去 N 年·N 个月、去年/前年、'
                            'X以来/截至X、ISO 或斜杠日期)'}
        return None                      # 单日期提及≠区间(如「2026-10的PMI」)
    # ≥2 个日期词形: 取词面首末(词序倒置=错误区间,不静默重排)
    first, last = parsed[0], parsed[-1]
    iso_first, iso_last = (_norm_qdate(first[2], 'start'),
                           _norm_qdate(last[2], 'end'))
    if iso_first and iso_last and iso_first > iso_last:
        return {'kind': 'unparseable',
                'reason': (f'区间倒置: 首词 {first[2]}({iso_first}) 晚于 '
                           f'末词 {last[2]}({iso_last})'),
                'raw': f'{first[2]}..{last[2]}'}
    return {'kind': 'explicit', 'start': iso_first, 'end': iso_last,
            'raw': f'{first[2]}..{last[2]}'}


# ── Audit-R7 条目1(R7-01): 日历期望观测数(交易日历口径) ──────────────
def _count_weekdays(d0, d1):
    """[d0,d1] 闭区间自然日中的工作日数(周一~周五;节假日不在日历内,
    由缺口容忍系数吸收)——日频期望的分母用真实星期构成,不用 252×年数
    硬标(真实十年日频常因节假日少数十点,如 BEI_10Y 2499<2520)。"""
    if d1 < d0:
        return 0
    days = (d1 - d0).days + 1
    full_weeks, rem = divmod(days, 7)
    n = full_weeks * 5
    for i in range(rem):
        if (d0 + timedelta(days=full_weeks * 7 + i)).weekday() < 5:
            n += 1
    return n


def _count_months(d0, d1):
    return (d1.year - d0.year) * 12 + (d1.month - d0.month) + 1


def _count_quarters(d0, d1):
    q0 = d0.year * 4 + (d0.month - 1) // 3
    q1 = d1.year * 4 + (d1.month - 1) // 3
    return q1 - q0 + 1


def _count_iso_weeks(d0, d1):
    import trading_calendar as _tc
    weeks = set()
    d = d0
    while d <= d1:
        weeks.add(_tc.iso_week_bounds(d)[0])
        d += timedelta(days=1)
    return max(1, len(weeks))


def _expected_in_window(freq, d0, d1):
    """频率族日历期望(闭区间): daily=工作日数/weekly=ISO 周数/
    monthly=自然月数/quarterly=自然季数;未知频率 None。"""
    if d0 is None or d1 is None or d1 < d0:
        return None
    if freq == 'daily':
        return _count_weekdays(d0, d1)
    if freq == 'weekly':
        return _count_iso_weeks(d0, d1)
    if freq == 'monthly':
        return _count_months(d0, d1)
    if freq == 'quarterly':
        return _count_quarters(d0, d1)
    return None


def _effective_window_obs(dates, values, start, end):
    """实际 dates/values → 窗内**有效去重**观测(Audit-R7 条目1:
    从实际序列计算,不制首末、不用总量冒充;Audit-R8 R8-01 统一有效性)。

    有效=合法日期+**有限数值**(与采集/清洗/查询同口径: 缺值/不可数值化/
    NaN/±Infinity 一律无效)——values=None=无有效数值面,**禁 1.0 占位**
    (占位曾把缺值序列判成满覆盖放行);同日去重;窗=[start,end] 闭区间
    ISO 字符串比较;长度错配如实登记。返回 (sorted_dates, stats)。"""
    dl = list(dates or [])
    vl = list(values) if values is not None else [None] * len(dl)
    seen = {}
    n_invalid = n_dup = 0
    for d, v in zip(dl, vl):
        ds = str(d)[:10]
        if not _valid_iso_date(ds):
            n_invalid += 1
            continue
        if not (start <= ds <= end):
            continue
        if v is None:
            n_invalid += 1
            continue
        try:
            fv = float(v)
        except (TypeError, ValueError):
            n_invalid += 1
            continue
        if fv != fv or fv in (float('inf'), float('-inf')):
            n_invalid += 1
            continue
        if ds in seen:
            n_dup += 1
        seen[ds] = True
    return sorted(seen), {'n_invalid_dropped': n_invalid,
                          'n_duplicate_dates': n_dup,
                          'n_length_mismatch': abs(len(dl) - len(vl))}


# ── Audit-R7 条目2(R7-02): 采集状态贯通+任务时效判定 ──────────────────
def _collection_status_for(mid, snap, steps):
    """采集状态提取(快照 series_provenance 平节优先;S4 信封
    collection_status 次之——ia_cli history 信封自 wd.metric_series
    双路携带)。返回规范化 dict 或 None(无状态档不造状态)。"""
    prov = ((snap or {}).get('series_provenance') or {}).get(mid)
    if isinstance(prov, dict) and prov:
        return _norm_cstat(prov)
    _st = next((s for s in (steps or [])
                if s.get('step') == f'S4_history_{mid}'), None)
    if _st and _st.get('ok'):
        cs = ((((_st.get('envelope') or {}).get('data') or {})
               .get('series')) or {}).get('collection_status')
        if isinstance(cs, dict) and cs:
            return _norm_cstat(cs)
    return None


def _norm_cstat(cs):
    """provenance/已规范化状态 → 规范形态(与 rhq.collection_status_of
    同口径;orchestrator 侧轻量内联避免运行时反向依赖查询模块)。"""
    mode = cs.get('mode') or ('carry_forward' if cs.get('fresh') is False
                              else ('fresh' if cs.get('fetched_at')
                                    else 'unknown'))
    out = {'mode': mode,
           'last_success_at': cs.get('last_success_at')
           or cs.get('fetched_at'),
           'last_observation_period': cs.get('last_observation_period'),
           'carry_forward_from': cs.get('carry_forward_from'),
           'carry_forward_reason': cs.get('carry_forward_reason')}
    return {k: v for k, v in out.items() if v is not None}


def _freshness_vs_task(cstat, win, as_of, freq, last_obs_fallback):
    """任务时效判定(R7-02): 参考端=任务窗止(限定范围;历史回放=回放
    窗止)或研究时点(max_available);末观测=采集状态数据统计期(无则
    序列末观测);容忍=频率族止侧容差(发布滞后已含)。

    返回 None(参考端/频率/末观测不可得=不可判)或
    {'stale','reference','last_observation','lag_days','tolerance_days',
     'detail'}——**陈旧≠一律失败**: 仍满足任务窗的续用数据由调用面
    披露放行,超出容忍的陈旧数据=stale_for_task 阻断交付。"""
    ref_iso = (win or {}).get('end') if win else None
    ref_kind = '任务窗止'
    if not ref_iso and as_of is not None:
        ref_iso = as_of.isoformat()
        ref_kind = '研究时点'
    if not ref_iso:
        return None
    tol = _WINDOW_TOL_DAYS.get(freq)
    if not tol:
        return None
    last_obs = (cstat or {}).get('last_observation_period') \
        or last_obs_fallback
    if not last_obs:
        return None
    rd = _parse_ymd(str(ref_iso)[:10])
    ld = _parse_ymd(str(last_obs)[:10])
    if rd is None or ld is None:
        return None
    lag = (rd - ld).days
    stale = lag > tol[1]
    detail = (f'末观测统计期 {ld.isoformat()} 落后{ref_kind} '
              f'{rd.isoformat()} {lag} 天>容忍 {tol[1]} 天(数据过期'
              f'不得冒充当前研究可用)' if stale
              else f'末观测统计期 {ld.isoformat()} 距{ref_kind} '
                   f'{rd.isoformat()} {lag} 天≤容忍 {tol[1]} 天'
                   f'(含发布滞后)')
    return {'stale': stale, 'reference': rd.isoformat(),
            'last_observation': ld.isoformat(), 'lag_days': lag,
            'tolerance_days': tol[1], 'detail': detail}

# 引擎数据树注入缝(research-one --engine-root;G2 净环境验收同缝):
# 子进程 ia_cli 与 cwd 改指真实数据树;默认=本仓库根(行为零差)。
RUN_ROOT = ROOT


def _now_utc():
    return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')


def _slug(text, maxlen=40):
    s = re.sub(r'[^A-Za-z0-9一-鿿]+', '_', text).strip('_')
    return (s[:maxlen] or 'question')


def _run_proc(name, cmdline, timeout=180, argv_label=None):
    """跑一个真子进程(通用);进程成败/语义成败/信封三层分开记录。"""
    t0 = time.monotonic()
    try:
        p = subprocess.run(cmdline,
                           capture_output=True, text=True, timeout=timeout,
                           cwd=RUN_ROOT)
        rc, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return {'step': name, 'argv': argv_label or cmdline[1:],
                'executed': True,
                'ok': False, 'exit_code': None,
                'note': f'超时(>{timeout}s)', 'duration_ms': None,
                'envelope': None}
    except OSError as e:
        # R4 NIT(E席审计): 进程启动失败(脚本缺席/无解释器)=该步失败留痕,
        # 不炸整条管线(其余步骤照跑,信封面完整)。
        return {'step': name, 'argv': argv_label or cmdline[1:],
                'executed': True, 'ok': False, 'exit_code': None,
                'note': f'进程启动失败: {e}', 'duration_ms': None,
                'envelope': None}
    env = None
    try:
        env = json.loads(out)
    except ValueError:
        pass
    return {'step': name, 'argv': argv_label or cmdline[1:], 'executed': True,
            'ok': rc == 0,
            'exit_code': rc,
            'semantic_ok': bool(env.get('ok')) if isinstance(env, dict) else None,
            'note': (err.strip()[:200] or None) if rc != 0 and env is None else None,
            'duration_ms': int((time.monotonic() - t0) * 1000),
            'envelope': env}


def run_step(name, argv, timeout=180):
    """跑一步真 ia_cli 子进程(十一步管线主路径)。"""
    ia_cli = os.path.join(RUN_ROOT, 'ia_cli.py')
    return _run_proc(name, [sys.executable, ia_cli] + argv, timeout,
                     argv_label=argv)


def skipped_step(name, note):
    return {'step': name, 'argv': [], 'executed': False, 'ok': True,
            'exit_code': None, 'skipped_reason': note, 'envelope': None}


def _run_ok(steps):
    """进程层总判: 全部已执行步骤 ok;诚实拒答步骤豁免(R2.1 MINOR-1,
    E席审计——analog 短历史拒答是引擎正确行为,不是管线失败)。"""
    return all(s.get('ok') for s in steps
               if s.get('executed') and not s.get('honest_refusal'))


def run_fanout(root, ia_timeout, mapped_metrics):
    """R3 十问确定性扇出: QUESTION_COMMANDS 逐条真跑,信封留档。

    纪律: Agent 层问(RQ3/RQ9)=declared-not-produced,本管线绝不代写;
    占位符确定性替身且如实披露——VIEW-…→观点库首条 view_id(相关性选择
    归 Agent),A_ID/B_ID→命中指标前二(不足回落清单原样 UST_10Y,SPX);
    清单原样的 US+CN/RQ2 指标对不做语义改写(替身≠相关性判断)。"""
    import shlex
    import research_map as rm
    import view_store as vs
    import workbench_data as wd
    root = root or ROOT
    try:
        qmeta = {q['id']: q for q in
                 (wd.research_questions().get('questions') or [])}
    except (OSError, ValueError, KeyError):
        qmeta = {}
    try:
        views = vs.load_views(os.path.join(root, 'data', 'institutions',
                                           'views'))['views']
        first_vid = views[0]['view_id'] if views else None
    except (OSError, ValueError, KeyError, IndexError):
        first_vid = None
    pair = list(mapped_metrics[:2]) if len(mapped_metrics) >= 2 else None
    rows = []
    for rq_id in sorted(rm.QUESTION_COMMANDS,
                        key=lambda k: int(''.join(filter(str.isdigit, k)) or 0)):
        meta = qmeta.get(rq_id, {})
        steps, agent_layer_notes = [], []
        for ci, c in enumerate(rm.QUESTION_COMMANDS[rq_id]):
            toks = shlex.split(c)
            if not toks or toks[0].startswith('('):
                agent_layer_notes.append(c.strip('()'))
                continue
            subs = []
            argv, dead = [], False
            for t in toks[1:]:
                if t == 'VIEW-…':
                    if first_vid is None:
                        subs.append('VIEW-… 无观点库可替(如实跳过)')
                        dead = True
                        break
                    subs.append(f'VIEW-…→{first_vid}(首条确定性替身,'
                                '相关性选择归 Agent)')
                    t = first_vid
                elif t == 'A_ID' and pair:
                    t, _ = pair[0], subs.append(f'A_ID→{pair[0]}')
                elif t == 'B_ID' and pair:
                    t, _ = pair[1], subs.append(f'B_ID→{pair[1]}')
                elif t == 'A_ID,B_ID' and pair:
                    t = f'{pair[0]},{pair[1]}'
                    subs.append(f'A_ID,B_ID→{pair[0]},{pair[1]}')
                argv.append(t)
            name = f'{rq_id}_c{ci}'
            if dead:
                steps.append(skipped_step(name, '; '.join(subs)))
                continue
            if toks[0] == 'ia_cli.py':
                st = run_step(name, argv, ia_timeout)
            elif toks[0].startswith('scripts/'):
                st = _run_proc(name, [sys.executable, os.path.join(
                    root, toks[0])] + argv, ia_timeout, argv_label=argv)
            else:
                steps.append(skipped_step(name, f'非可执行清单项: {c}'))
                continue
            if subs:
                st['substitutions'] = subs
            steps.append(st)
        rows.append({'id': rq_id,
                     'text': meta.get('text'),
                     'primary_layer': meta.get('primary_layer'),
                     'agent_layer': bool(agent_layer_notes),
                     'agent_layer_notes': agent_layer_notes or None,
                     'steps': steps})
    n_exec = sum(1 for r in rows for s in r['steps'] if s.get('executed'))
    n_agent = sum(1 for r in rows if r['agent_layer'])
    return {'requested': True, 'n_rq': len(rows), 'n_executed': n_exec,
            'n_agent_layer': n_agent,
            'substitution_rule': ('VIEW-…→首条 view_id;A_ID/B_ID→命中前二'
                                  '(不足=清单原样)——替身≠相关性选择'),
            'rq': rows}


def map_entities(question, reg):
    """确定性实体映射: 指标(metric_id/display_name 折叠子串)+经济体(中文标签反查)。

    匹配不到=如实 unmapped(零翻译零猜测;Agent 可后续补语义层)。"""
    q = question.casefold()
    metrics = []
    for m in (reg.get('metrics') or []):
        mid = (m.get('metric_id') or '')
        names = [mid, m.get('display_name') or '']
        if any(n and n.casefold() in q for n in names):
            metrics.append(mid)
    economies = []
    import workbench_data as wd
    for code, label in (wd.ECONOMY_LABELS or {}).items():
        # 代码用词边界(防 'EA' 命中 tr'ea'sury 类子串误报);中文标签直接子串
        if label and (label in question
                      or re.search(r'\b' + re.escape(code.casefold()) + r'\b', q)):
            economies.append(code)
    note = None
    if not metrics:
        note = ('问题未词面命中任何指标(零模型不做语义翻译);'
                '事实面降级为经济体概览,接地问答步骤仍如实作答/拒答')
    return {'metrics': metrics, 'economies': economies, 'note': note}


def _fact_rows(snap, metric_ids):
    """L1 行: 快照事实直取(逐行 fact_id 证据;不猜不补)。

    无指标命中时不倾倒全量事实(防噪)——基线层只给计数,裸数行须有映射。"""
    if not metric_ids:
        return []
    rows = []
    for f in snap.get('facts') or []:
        if f.get('metric_id') not in metric_ids:
            continue
        rows.append({'metric_id': f.get('metric_id'),
                     'value': f.get('value'), 'unit': f.get('unit'),
                     'observation_date': f.get('observation_date'),
                     'quality_status': f.get('quality_status'),
                     'source': {'kind': 'snapshot_fact', 'id': f.get('fact_id')}})
    return rows


def _s3_envelope_rows(steps, l1_rows):
    """R33-③: S3_changes 信封在场指标行→证据索引行(kind=s3_envelope)。

    索引行 ref 沿 L1 惯例 `{metric_id}@{observation_date}`;与 L1 已有
    metric_id 去重(L1 行权威);presence 非 present/缺观测日行不收
    (缺席数字无可锚面)。
    """
    s3 = next((s for s in steps if s.get('step') == 'S3_changes'), {})
    bac = ((((s3.get('envelope') or {}).get('data') or {})
            .get('by_asset_class')) or {})
    seen = {r.get('metric_id') for r in l1_rows}
    rows = []
    if not isinstance(bac, dict):
        return rows
    for cls_rows in bac.values():
        if not isinstance(cls_rows, list):
            continue
        for row in cls_rows:
            if not isinstance(row, dict):
                continue
            mid = row.get('metric_id')
            obs = row.get('observation_date')
            if (not mid or mid in seen or not obs
                    or row.get('presence', 'present') != 'present'):
                continue
            seen.add(mid)
            rows.append({'ref': f'{mid}@{obs}', 'kind': 's3_envelope',
                         'metric_id': mid})
    return rows


def vp_face(root):
    """L2 原料: VP sidecar 装载(标签/阶段摘要;缺席如实 None)。"""
    try:
        import view_plausibility as vp
        # R4 NIT(E席审计): root 原先未透传,装载落在模块默认路径——
        # 测试注入的隔离 root 拿不到对应 VP;现按 root 定位。
        docs, bad = vp.load_all(vp_dir=os.path.join(
            root, 'data', 'institutions', 'verification'))
    except Exception as e:  # noqa: BLE001 —— 缺席/不可读=如实降级,不阻断管线
        return {'available': False, 'note': f'VP 装载失败: {e}'}
    if not docs:
        note = 'VP sidecar 缺席(data/ 本地层;干净 clone 常态)'
        if bad:
            note += f';另有 {len(bad)} 份坏档隔离不入面'
        return {'available': False, 'note': note}
    rows = []
    for doc in docs:
        vid = doc.get('view_id')
        rows.append({'view_id': vid,
                     'view_label': doc.get('view_label'),
                     'stage_summary': doc.get('stage_summary'),
                     'source': {'kind': 'vp_sidecar', 'id': f'VP-{vid}'}})
    return {'available': True, 'n': len(rows), 'rows': rows,
            'n_bad_quarantined': len(bad)}


def _parse_ymd(s):
    """'YYYY-MM-DD'/'YYYYMMDD' 前缀 → date(None=不可解析)。"""
    if not isinstance(s, str):
        return None
    t = s.strip().replace('-', '')[:8]
    if len(t) == 8 and t.isdigit():
        try:
            return datetime.strptime(t, '%Y%m%d').date()
        except ValueError:
            return None
    return None


def _snap_as_of_date(snap):
    """研究时点(权威=快照 target_date,research_as_of 兜底;None=不可核验)。"""
    for k in ('target_date', 'research_as_of'):
        d = _parse_ymd((snap or {}).get(k) if isinstance(snap, dict) else None)
        if d is not None:
            return d
    return None


def _evaluate_data_requirements(metrics, steps, snap, l1_rows,
                                question=None, registry=None):
    """Audit-R4 条目5 + Audit-R5 条目2 + Audit-R6 条目2(抽函数可测)。

    判据序: 快照 series_store 序列 → **本管线 S4 history 步已探测的信封**
    (与 Agent 席所见同源)→ L1/S3 单点在场。仅查快照会把采集档序列
    (BEI_10Y/UST_10Y 等 macro 源 2400+ 日)误判「仅最新单点在场」;不在
    进程内另行直读外部数据树(FIX7 信任边界: 采集目录越界不读)。
    最新单点≠历史分析需求满足——n<min_observations 即 insufficient_coverage,
    与 missing 同为必要缺口(attach/report/archive 同源三级分类)。

    Audit-R5 条目2: min_observations 按**任务所需历史范围**推导(问题
    词面限定"近/过去 N 年"→ N 年×频率年观测数;未限定→频率族兜底下界)。

    Audit-R6 条目2(R6-01,反例复现于基线 dcb4b17):
    - 频率取**权威注册表**(registry.by_id,调用面传 S1 已装载面)优先,
      S4 信封次之,快照内嵌 registry_by_id 兜底——快照路径(序列在场→
      S4 不跑)不再丢频率(反例1: 12 个日频观测因 freq=None 落 12 兜底
      满足);
    - 时间范围按**真实时间边界**判: 研究时点(快照 target_date)倒推
      N 年为任务窗,序列须跨窗(首观测≤窗起+容差/末观测≥窗止-容差,
      容差按频率族含节假日/发布滞后)+窗内有效观测≥min_obs 半额
      (允许合理缺口)——总数量再大也不替代窗口归属(反例2: 3000 个
      1990-1998 观测对"近十年"窗=0 窗内有效观测);
    - 未知频率/研究时点不可核验且问题限定范围→**不回落宽松通过**
      (窗口不可核验=insufficient_coverage);未限定范围问题维持
      max_available 口径(完整短史不误拒)。
    """
    _fact_mids = {r['metric_id'] for r in l1_rows}
    import research_history_query as rhq   # R9-01: 唯一有效观测清洗规则
    _ss = (snap or {}).get('series_store') or {}
    _s3_env = ((next((s.get('envelope') for s in steps
                      if s.get('step') == 'S3_changes'), {}) or {})
               .get('data') or {})
    _s3_mids = set()
    for _bk in (_s3_env.get('by_asset_class') or {}).values():
        if isinstance(_bk, dict):
            _s3_mids.update(str(k) for k in _bk)
    _range_years = _question_range_years(question)
    _qw = _question_window(question)          # R7-01: 显式区间优先
    _as_of = _snap_as_of_date(snap)
    _reg_by_id = registry or {}
    req_items = []
    for _mid in metrics:
        _n_series = 0
        _ser_src = '研究快照 series_store'
        _freq, _first, _last = None, None, None
        _ser_face_present = False          # R8-01: 序列面在场但可 0 有效
        _ss_dates = list((_ss.get(_mid) or {}).get('dates') or [])
        if _ss_dates:
            _ser_face_present = True
        # R9-01: 建档清洗后未入 store(全 NaN/±Inf/非法日期)的序列,
        # 其「面在场、有效 0」事实由快照核验披露节携带——判定器消费
        # 该披露据实分类,不误标「均缺席」。
        elif isinstance(((snap or {}).get('series_store_clean') or {})
                        .get(_mid), dict):
            _ser_face_present = True
        # R9-01: 快照直读过唯一有效观测清洗(rhq.effective_series,
        # 与查询 loader/工作台同一实现)——n/first/last 取自最终有效
        # 序列,不信任原始数组长度。
        if _ss_dates:
            _cd, _cv, _cst = rhq.effective_series(_ss_dates,
                                                  (_ss.get(_mid) or {}).get('values'))
            _n_series = len(_cd)
            if _cd:
                _first, _last = _cd[0], _cd[-1]
        if _n_series == 0:
            _st = next((s for s in steps
                        if s.get('step') == f'S4_history_{_mid}'), None)
            if _st and _st.get('ok'):
                _s4 = (((_st.get('envelope') or {}).get('data')
                        or {}).get('series')) or {}
                # R9-01: 信封面吃日期/值数组经同一清洗,不信任声明
                # n/first/last(生产 ia_cli cmd_history 信封恒携带
                # 全长 dates/values 数组,声字段仅披露用)。dates 为
                # list(含空)=序列面在场(S4 探测发生过,清洗后有效 0
                # 走据实分支,不误标均缺席);dates 缺席=无面,声明 n
                # 不采信(覆盖不可核验,n 保持 0)。
                _s4_dates = _s4.get('dates')
                if isinstance(_s4_dates, list):
                    _ser_face_present = True
                    _cd, _cv, _cst = rhq.effective_series(
                        _s4_dates, _s4.get('values'))
                    _n_series = len(_cd)
                    if _cd:
                        _ser_src = str(_s4.get('source') or 'S4 history 探测')
                        _freq = _s4.get('frequency') or _freq
                        _first = _cd[0]
                        _last = _cd[-1]
                    else:
                        _ser_src = str(_s4.get('source') or 'S4 history 探测')
                        _freq = _s4.get('frequency') or _freq
        # R6-01: 权威注册表优先(快照路径不丢频率),S4 次之,快照内嵌兜底
        _freq = ((_reg_by_id.get(_mid) or {}).get('frequency')
                 or _freq
                 or (((snap or {}).get('registry_by_id') or {})
                     .get(_mid) or {}).get('frequency'))
        # min_observations 推导: 任务词面年限>频率族兜底(谁严取谁)
        if _range_years and _freq in _OBS_PER_YEAR_BY_FREQ:
            _min_obs = _range_years * _OBS_PER_YEAR_BY_FREQ[_freq]
            _min_basis = (f'问题限定 {_range_years} 年×'
                          f'{_freq} 频率年观测 '
                          f'{_OBS_PER_YEAR_BY_FREQ[_freq]}')
        else:
            _min_obs = _REQ_MIN_OBSERVATIONS_BY_FREQ.get(
                _freq, _REQ_MIN_OBSERVATIONS)
            _min_basis = (f'问题未限定范围→{_freq or "未知"}频率族兜底'
                          f'下界(任务范围不得用统一观测数替代)'
                          if _range_years is None else
                          f'问题限定 {_range_years} 年但 {_freq or "?"} '
                          f'频率未知→通用兜底')
        # ── R7-01: 任务窗口(真实时间边界,统一解析) ────────────────
        # 相对年限来源: _question_window 的 relative 词形;其返回 None 时
        # 回落 _question_range_years(近/过去 N 年);显式区间优先于相对。
        _rel_years = None
        if _qw is not None and _qw['kind'] == 'relative':
            _rel_years = _qw['years']
        elif _qw is None:
            _rel_years = _range_years
        _win = None
        if _qw is not None and _qw['kind'] == 'unparseable':
            _win = {'start': None, 'end': None, 'kind': 'unparseable',
                    'basis': (f'问题指定了时间范围但无法解析: '
                              f'{_qw["reason"]}'
                              + (f';{_qw["hint"]}' if _qw.get('hint')
                                 else ''))}
        elif _qw is not None and _qw['kind'] == 'calendar_year':
            # R8-02: 「去年」=研究时点上一自然年(相对词形绑定研究时点;
            # 时点不可核验=窗口不可核验,不回落 max_available)
            if _as_of is None:
                _win = {'start': None, 'end': None, 'kind': 'calendar_year',
                        'basis': '研究时点不可核验→「去年」自然年窗口'
                                 '无法判定'}
            else:
                _cy = _as_of.year + int(_qw.get('offset', -1))
                _win = {'start': '%04d-01-01' % _cy,
                        'end': '%04d-12-31' % _cy,
                        'as_of': _as_of.isoformat(),
                        'kind': 'calendar_year',
                        'basis': f'研究时点 {_as_of.isoformat()} 的'
                                 f'「去年」={_cy} 自然年(词形绑定研究时点)'}
        elif _qw is not None and _qw['kind'] == 'relative_months':
            # R9-02: 近/过去 N 个月=研究时点倒推 N 个自然月(相对词形
            # 绑定研究时点,不用系统当前时间;时点不可核验=窗口不可
            # 核验,不回落 max_available)
            if _as_of is None:
                _win = {'start': None, 'end': None,
                        'kind': 'relative_months',
                        'basis': '研究时点不可核验(快照无 target_date/'
                                 'research_as_of)→相对月窗无法判定'}
            else:
                _wm_s = _shift_months(_as_of, -int(_qw['months']))
                _win = {'start': _wm_s.isoformat(),
                        'end': _as_of.isoformat(),
                        'as_of': _as_of.isoformat(),
                        'kind': 'relative_months',
                        'basis': (f'研究时点 {_as_of.isoformat()} 倒推 '
                                  f'{int(_qw["months"])} 个自然月'
                                  f'({_wm_s.isoformat()}..'
                                  f'{_as_of.isoformat()})')}
        elif _rel_years:
            if _as_of is None:
                _win = {'start': None, 'end': None, 'kind': 'relative',
                        'basis': '研究时点不可核验(快照无 target_date/'
                                 'research_as_of)→窗口不可核验'}
            else:
                _ws = _as_of - timedelta(days=int(round(
                    _rel_years * 365.25)))
                _win = {'start': _ws.isoformat(), 'end': _as_of.isoformat(),
                        'as_of': _as_of.isoformat(), 'kind': 'relative',
                        'basis': f'研究时点 {_as_of.isoformat()} 倒推 '
                                 f'{_rel_years} 年(日历边界)'}
        elif _qw is not None and _qw['kind'] == 'explicit':
            _ws_iso = _qw.get('start')
            _we_iso = _qw.get('end')
            if _we_iso is None:               # 「X以来」→ 终界=研究时点
                if _as_of is None:
                    _win = {'start': _ws_iso, 'end': None,
                            'kind': 'explicit',
                            'basis': '问题限定 X 以来但研究时点不可核验'
                                     '→窗口终界无法判定'}
                else:
                    _we_iso = _as_of.isoformat()
            if _we_iso is not None and _ws_iso is not None \
                    and _ws_iso > _we_iso:
                _win = {'start': None, 'end': None, 'kind': 'unparseable',
                        'basis': f'错误区间: 起 {_ws_iso} 晚于止 {_we_iso}'}
            elif _we_iso is not None:
                _win = {'start': _ws_iso, 'end': _we_iso,
                        'kind': 'explicit',
                        'as_of': (_as_of.isoformat() if _as_of else None),
                        'basis': (f'问题明确日期区间 {_qw["raw"]}'
                                  f'(词面边界)'
                                  + (';单侧终界(「截至X」): 起点不限'
                                     if _ws_iso is None else '')
                                  + (f';并存相对年限 {_range_years} 年'
                                     f'(显式区间优先)' if _range_years else ''))}
            elif _win is None:
                _win = {'start': None, 'end': None, 'kind': 'explicit',
                        'basis': '问题区间词形无法构成窗口'}
        _tol = _WINDOW_TOL_DAYS.get(_freq) if _freq else None
        _n_in_win, _first_in, _last_in = None, None, None
        _win_detail = None
        _dates_face = None
        # R8-02: 单侧终界(「截至X」,start=None)——已声明支持的单侧边界
        # 不因 start 缺席必然拒绝: 日期面在场时窗起=实际序列首观测
        # (起点不限,数据驱动=与 max_available 起点同口径;起侧覆盖恒
        # 满足,终侧按频率族容差核验)。无日期面=窗口成员不可核验→阻断。
        _win_single_end = (_win is not None
                           and _win.get('end') is not None
                           and _win.get('start') is None
                           and _win.get('kind') == 'explicit')
        if _win is not None and _win.get('end') is not None \
                and (_win.get('start') or _win_single_end):
            # 实际日期面: 快照序列优先;否则 S4 信封 dates(ia_cli 真实
            # 输出恒带;合成信封无 dates=窗口成员不可核验→阻断,不猜)
            if _ss_dates:
                _dates_face = (_ss_dates,
                               ((_ss.get(_mid) or {}).get('values')))
                _ser_face = '快照 series_store 实际 dates/values'
            else:
                _s4d = None
                _st2 = next((s for s in steps
                             if s.get('step') == f'S4_history_{_mid}'), None)
                if _st2 and _st2.get('ok'):
                    _s4s = (((_st2.get('envelope') or {}).get('data')
                             or {}).get('series')) or {}
                    _s4d = _s4s.get('dates')
                    if _s4d is not None:
                        _dates_face = (_s4d, _s4s.get('values'))
                        _ser_face = 'S4 信封实际 dates/values'
                if _dates_face is None:
                    _ser_face = None
            if _dates_face is not None and _win_single_end:
                _face_ds = sorted(str(x)[:10] for x in _dates_face[0]
                                  if _valid_iso_date(str(x)[:10]))
                if _face_ds:
                    _win['start'] = _face_ds[0]
                    _win['basis'] += (f';单侧终界: 窗起=实际序列首观测'
                                      f' {_face_ds[0]}(起点不限,R8-02)')
            if _dates_face is not None and _win.get('start'):
                _in, _in_stats = _effective_window_obs(
                    _dates_face[0], _dates_face[1],
                    _win['start'], _win['end'])
                _n_in_win = len(_in)
                if _in:
                    _first_in, _last_in = _in[0], _in[-1]
                _win['_obs_stats'] = _in_stats
                _win['_ser_face'] = _ser_face
        # ── 判定序: 范围不可核验(无法解析/限定+未知频率/时点)先拦 ────
        if _win is not None and _win.get('kind') == 'unparseable':
            _outcome = 'insufficient_coverage'
            _basis = (f'{_win["basis"]}(指定了范围但无法解析=阻断,'
                      f'不回落 max_available;源={_ser_src})')
        elif _win is not None and (_freq is None or _tol is None):
            _outcome = 'insufficient_coverage'
            _basis = (f'问题限定时间范围但频率={_freq or "未知"}'
                      f'不可核验→时间窗口无法判定(不回落宽松通过;'
                      f'{_min_basis};源={_ser_src})')
        elif _win is not None and (_win.get('start') is None
                                   or _win.get('end') is None):
            _outcome = 'insufficient_coverage'
            _basis = (f'{_win.get("basis") or "任务窗口不可核验"}'
                      f'(不回落宽松通过)')
        elif _win is not None and _dates_face is None:
            _outcome = 'insufficient_coverage'
            _basis = (f'任务窗{_win["start"]}..{_win["end"]}窗口成员'
                      f'不可核验(快照无序列且 S4 信封无实际 dates——'
                      f'不得凭 first/last 裁剪或总量冒充窗内观测;'
                      f'源={_ser_src})')
        elif _win is not None:
            _fd, _ld = _parse_ymd(_first_in), _parse_ymd(_last_in)
            _wsd, _wed = _parse_ymd(_win['start']), _parse_ymd(_win['end'])
            _start_ok = (_fd is not None and _wsd is not None
                         and (_fd - _wsd).days <= _tol[0])
            _end_ok = (_ld is not None and _wed is not None
                       and (_wed - _ld).days <= _tol[1])
            _expected = _expected_in_window(_freq, _wsd, _wed)
            _n_floor = (max(1, int(round(_expected * _WINDOW_N_FRACTION)))
                        if _expected else
                        max(1, int(round(_REQ_MIN_OBSERVATIONS_BY_FREQ.get(
                            _freq, _REQ_MIN_OBSERVATIONS)
                            * _WINDOW_N_FRACTION))))
            _n_ok = (_n_in_win is not None and _n_in_win >= _n_floor)
            # R7-01 严重断档: 窗内相邻有效观测**逐对最大间距**(真实
            # dates 计算;双段密集中隔多年长洞必被抓住)超频率族上限=阻断
            _gap_ok, _obs_max_gap, _obs_avg_gap = True, None, None
            if len(_in) >= 2:
                _ds_in = [_parse_ymd(d) for d in _in]
                _gaps = [(_ds_in[i + 1] - _ds_in[i]).days
                         for i in range(len(_ds_in) - 1)]
                _obs_max_gap = max(_gaps)
                _obs_avg_gap = round(
                    sum(_gaps) / len(_gaps), 1)
            _gap_limit = _WINDOW_MAX_GAP_DAYS.get(_freq)
            if _obs_max_gap is not None and _gap_limit is not None:
                _gap_ok = _obs_max_gap <= _gap_limit
            if _start_ok and _end_ok and _n_ok and _gap_ok:
                _outcome = 'satisfied'
                _basis = (f'任务窗{_win["start"]}..{_win["end"]}跨窗满足: '
                          f'窗内有效去重 n={_n_in_win}'
                          f'(日历期望{_expected}×{_WINDOW_N_FRACTION:.0%}'
                          f'下界{_n_floor};边界容差 起+{_tol[0]}天/'
                          f'止-{_tol[1]}天;最大间距{_obs_max_gap}天'
                          f'≤{_gap_limit}天;总量 n={_n_series};'
                          f'{_min_basis};判定面={_win.get("_ser_face")})')
            else:
                _why = []
                if not _start_ok:
                    _why.append(f'窗内首观测{_first_in or "缺席"}晚于窗起'
                                f'+{_tol[0]}天容忍(历史未覆盖任务窗起点)')
                if not _end_ok:
                    _why.append(f'窗内末观测{_last_in or "缺席"}早于窗止'
                                f'-{_tol[1]}天容忍(发布滞后外缺口)')
                if not _n_ok:
                    _why.append(f'窗内有效观测 n={_n_in_win or 0}<{_n_floor}'
                                f'(日历期望{_expected}×半额;总量'
                                f'{_n_series}不替代窗口归属)')
                if not _gap_ok:
                    _why.append(f'窗内观测最大相邻间距{_obs_max_gap}天>'
                                f'频率族断档上限{_gap_limit}天(严重断档)')
                _outcome = 'insufficient_coverage'
                _basis = (f'任务窗{_win["start"]}..{_win["end"]}未满足: '
                          + ';'.join(_why)
                          + f'({_min_basis};判定面={_win.get("_ser_face")})')
            _win_detail = {'n_in_window': _n_in_win,
                           'first_in_window': _first_in,
                           'last_in_window': _last_in,
                           'expected_in_window': _expected,
                           'n_floor_in_window': _n_floor,
                           'max_adjacent_gap_days': _obs_max_gap,
                           'max_gap_limit_days': _gap_limit,
                           'tolerance_days': {'start': _tol[0],
                                              'end': _tol[1]}}
        elif _n_series >= _min_obs:
            _outcome = 'satisfied'
            _basis = (f'历史序列 n={_n_series}≥最低覆盖{_min_obs}'
                      f'({_min_basis};源={_ser_src};未限定范围='
                      f'max_available,总量口径)')
        elif _n_series > 0:
            _outcome = 'insufficient_coverage'
            _basis = (f'历史序列 n={_n_series} < 最低覆盖{_min_obs}'
                      f'({_min_basis};源={_ser_src};'
                      f'单点/短序列≠历史分析需求)')
        elif _mid in _fact_mids or _mid in _s3_mids:
            _outcome = 'insufficient_coverage'
            _basis = ('仅最新单点在场(L1/S3),无历史序列——单点≠'
                      '历史分析需求满足')
        elif _ser_face_present:
            # R8-01: 序列面在场但有效观测 0(NaN/±Inf/缺失/非法日期
            # 全剔)≠「均缺席」——按实际有效数量如实判不足,禁占位
            _outcome = 'insufficient_coverage'
            _basis = (f'序列面在场但有效观测 0(无效数值/非法日期'
                      f'全剔;源={_ser_src})')
        else:
            _outcome = 'missing'
            _basis = 'L1/S3/快照序列均缺席'
        # ── R7-02: 采集状态贯通+任务时效判定(仅 satisfied 面再检; ─────
        # 缺口类 outcome 已阻断)。参考端=任务窗止/研究时点——合法历史
        # 回放(as_of 钉住)参考端即回放时点不误判;仍满足任务窗的续用
        # 数据=披露放行;超出容忍的陈旧=stale_for_task 阻断交付。
        _cstat = _collection_status_for(_mid, snap, steps)
        _fresh = None
        if _outcome == 'satisfied':
            _fresh = _freshness_vs_task(
                _cstat, _win, _as_of, _freq, _last_in or _last)
            if _fresh and _fresh['stale']:
                _outcome = 'stale_for_task'
                _basis = (f'采集状态贯通判定数据过期: {_fresh["detail"]}'
                          f'(源={_ser_src}'
                          + (f';mode={_cstat["mode"]}' if _cstat else '')
                          + ';文件写入时间≠最后成功采集时间≠数据统计期'
                          '三分披露;R7-02)')
            elif _cstat and _cstat.get('mode') == 'carry_forward':
                _basis += (';续用披露: 本轮采集失败续存非新采集(最后成功'
                           f'采集 {_cstat.get("last_success_at")},续存自 '
                           f'{_cstat.get("carry_forward_from")})——仍满足'
                           '任务窗故可用')
        _spec_win = None
        if _win is not None:
            _spec_win = {k: v for k, v in _win.items()
                         if not k.startswith('_')}
            if _range_years:
                _spec_win['question_range_years'] = _range_years
            if _win_detail:
                _spec_win.update(_win_detail)
            _spec_win['allowed_gap'] = {
                'tolerance_days': (_tol if _tol else None),
                'n_fraction_floor': _WINDOW_N_FRACTION,
                'max_adjacent_gap_days': _WINDOW_MAX_GAP_DAYS.get(_freq),
                'basis': '频率族容差(日频节假日簇/月频发布滞后)+'
                         '窗内半额有效观测下界+相邻断档上限(R7-01)'}
        req_items.append({'metric_id': _mid, 'tier': 'required',
                          'basis': '问题词面命中(任务目标)',
                          'spec': {'form': 'series',
                                   'window': (_spec_win if _spec_win else
                                              'max_available'),
                                   'frequency': _freq,
                                   'quality': 'snapshot 序列(OK 行)',
                                   'coverage_observed': {
                                       'n': _n_series or None,
                                       'first': _first, 'last': _last,
                                       'n_in_window': _n_in_win,
                                       'first_in_window': _first_in,
                                       'last_in_window': _last_in},
                                   'min_observations': _min_obs,
                                   'min_observations_basis': _min_basis},
                          'outcome': _outcome, 'outcome_basis': _basis})
        if _cstat is not None:            # R7-02: 采集状态+时效随规格入档
            _cs = dict(_cstat)
            if _fresh:
                _cs['freshness'] = {k: _fresh[k] for k in (
                    'reference', 'last_observation', 'lag_days',
                    'tolerance_days')}
            req_items[-1]['spec']['collection_status'] = _cs
    return req_items


def run_research(question, root=None, archive=False, out_dir=None,
                 ia_timeout=180, fanout=False, engine_root=None):
    """十一步一键研究管线;返回完整报告 dict(run_ok=进程层,语义面看各步)。

    fanout=True 追加十问扇出面(R3): research_map.QUESTION_COMMANDS 逐条
    真跑+信封留档,Agent 层问(RQ3/RQ9)declared-not-produced。
    engine_root: 子进程 ia_cli 与 cwd 改指真实数据树(注入缝;默认=本仓库,
    行为零差)——净克隆验收/单入口 MVP 用。"""
    global RUN_ROOT
    RUN_ROOT = engine_root or ROOT
    root = root or RUN_ROOT
    import workbench_data as wd
    steps = []
    notes = []

    # ── S1 拆问题(确定性面) ─────────────────────────────────────────
    reg = wd.load_registry(root)
    ent = map_entities(question, reg)
    steps.append({'step': 'S1_decompose', 'executed': True, 'ok': True,
                  'deterministic_face': ent,
                  'agent_face_note': '自然语言深拆/主要矛盾综合=编排层 Agent;'
                                     '本步只给确定性实体映射'})

    # ── S2 doctor 体检 ──────────────────────────────────────────────
    steps.append(run_step('S2_doctor', ['doctor'], ia_timeout))

    # ── S3 事实基线(overview+changes) ───────────────────────────────
    ecos = ent['economies'] or ['US', 'CN']
    if not ent['economies']:
        # R4 NIT(E席审计): 默认面不再静默——US+CN 是清单默认而非问题语义
        notes.append('问题未命中经济体,S3 用默认面 US+CN(清单默认,'
                     '非问题语义判断;Agent 可按需补查其它经济体)')
    for eco in ecos:
        steps.append(run_step(f'S3_overview_{eco}',
                              ['overview', '--economy', eco], ia_timeout))
    steps.append(run_step('S3_changes', ['changes'], ia_timeout))

    # ── S4 历史可得性(命中指标逐个;未命中=跳过如实) ─────────────────
    hist_metrics = ent['metrics'][:4]
    if len(ent['metrics']) > 4:
        notes.append(f"命中 {len(ent['metrics'])} 个指标,历史步骤只取前 4"
                     f"(防噪);其余由 Agent 按需 history --metric 查询")
    for mid in hist_metrics:
        steps.append(run_step(f'S4_history_{mid}',
                              ['history', '--metric', mid], ia_timeout))
    if not hist_metrics:
        steps.append(skipped_step(
            'S4_history', '问题未命中指标——零实体映射时如实跳过(不造数)'))

    # ── S5 对齐自配对(≥2 命中才可比) ────────────────────────────────
    if len(hist_metrics) >= 2:
        steps.append(run_step('S5_compare',
                              ['compare', '--metrics',
                               ','.join(hist_metrics[:2])], ia_timeout))
        # R2.1 MINOR-2(E席审计): compare 仅取命中前 2(注册表序,确定性;
        # 非问题重点序)——如实披露,不静默截断
        if len(hist_metrics) > 2:
            steps[-1]['note'] = (f"命中 {len(hist_metrics)} 个指标,"
                                 f"compare 仅取注册表序前 2("
                                 f"{','.join(hist_metrics[:2])});"
                                 f"其余 {','.join(hist_metrics[2:])} "
                                 f"以 L1 事实行呈现,如需对比另行单跑")
    else:
        steps.append(skipped_step(
            'S5_compare', '命中指标不足 2 个,无可对齐自配对(如实跳过)'))

    # ── S6 历史相似结构(analog;短历史诚实拒答透传) ─────────────────
    steps.append(run_step('S6_analog', ['analog'], ia_timeout))
    # R2.1 MINOR-1(E席审计): analog 数据面诚实拒答(rc=1,engine _refuse)
    # 是正确行为不是管线失败——标记豁免,run_ok 不因它翻 False。
    _s6 = steps[-1]
    _err = ((_s6.get('envelope') or {}).get('error') or {})
    if (not _s6.get('ok')
            and _err.get('kind') in ('insufficient_history',
                                     'insufficient_candidates',
                                     'anchor_not_complete')):
        _s6['honest_refusal'] = True
        _s6['note'] = (f"诚实拒答(engine: {_err.get('kind')}),"
                       f"run_ok 豁免: {_err.get('message')}")

    # ── S7 research_mode_gate(从 compare/analog 信封提取,无独立命令) ─
    # R2.1 MAJOR-1(E席审计): gate 两处来源语义不同——compare 信封
    # data.alignment.research_mode_gate=对齐研究门(权威,本步对象);
    # analog 信封 data 顶层=锚点月窗门(另一语义)。旧实现只探顶层两处,
    # compare 对齐门恒漏(死代码),错取 analog 门甚至落空。现按优先级取并
    # 记 gate_source,可溯。
    gate, gate_src = None, None
    for s in steps:
        if s['step'] != 'S5_compare':
            continue
        d = (s.get('envelope') or {}).get('data')
        g = (d.get('alignment') or {}).get('research_mode_gate') \
            if isinstance(d, dict) else None
        if g is not None:
            gate, gate_src = g, 'S5_compare:data.alignment.research_mode_gate'
    if gate is None:
        for s in steps:
            if s['step'] != 'S6_analog':
                continue
            d = (s.get('envelope') or {}).get('data')
            g = d.get('research_mode_gate') if isinstance(d, dict) else None
            if g is not None:
                gate, gate_src = g, 'S6_analog:data.research_mode_gate'
    gate_note = None
    if gate_src == 'S6_analog:data.research_mode_gate':
        gate_note = 'analog 锚点月窗门(compare 未产出对齐门——命中<2 或被拒)'
    steps.append({'step': 'S7_mode_gate', 'executed': True, 'ok': gate is not None,
                  'gate': gate, 'gate_source': gate_src, 'note': gate_note or
                  (None if gate else 'compare/analog 信封未含 gate'
                          '(本轮无可比对/被拒答)——如实缺席,不编造')})

    # ── S8 接地问答(ia_cli research;archive 开关在此一次性落档) ────
    qa_argv = ['research', '--question', question]
    if archive:
        qa_argv += ['--archive',
                    '--note', 'R2 research-run 一键编排落档']
    steps.append(run_step('S8_grounded_qa', qa_argv, ia_timeout))

    # ── S9 观点面(views lint + VP 装载) ────────────────────────────
    steps.append(run_step('S9_views_lint', ['views', 'lint'], ia_timeout))
    vpf = vp_face(root)

    # ── S10 lint/自检: views 违规数+证据索引完整性 ──────────────────
    lint_step = next((s for s in steps if s['step'] == 'S9_views_lint'), {})
    n_quarantined = ((((lint_step.get('envelope') or {}).get('data'))
                      or {}).get('n_quarantined'))

    snap, snap_note = wd.latest_snapshot(root)
    facts = snap.get('facts') if snap else None
    l1_rows = _fact_rows(snap or {}, set(hist_metrics)) if facts else []

    # ── Audit-R2 条目7: 数据需求声明(分类在采集前冻结,不随结果改判) ──
    # 必要=问题词面命中指标(任务目标本体);可选=上下文面(S3 信封指标/
    # L2 机构观点/经济体概览)。采集后只评 outcome(satisfied/missing),
    # 不得把 missing 的必要项改判可选(事后缩减任务目标=禁止)。
    # 评据: L1 行 / 快照 series_store 序列在场(S4 history 数据源)。
    _req_items = _evaluate_data_requirements(
        ent['metrics'], steps, snap, l1_rows, question=question,
        registry=reg.get('by_id'))
    data_requirements = {
        'frozen_at': 'plan(采集前冻结;分类与规格不随采集结果改判)',
        'items': _req_items,
        'optional_face': {
            'tier': 'optional',
            'scope': 'S3 上下文指标/L2 机构观点/经济体概览',
            'note': '可选缺席=降级披露,不构成任务目标缺口;必要缺席/'
                    '覆盖不足=任务目标缺口,attach 默认阻塞(显式越过须随档)'},
    }
    if any(i['outcome'] in ('missing', 'insufficient_coverage',
                            'stale_for_task')
           for i in _req_items):
        notes.append('必要数据缺口: ' + '、'.join(
            i['metric_id'] for i in _req_items
            if i['outcome'] in ('missing', 'insufficient_coverage',
                                'stale_for_task'))
            + '(运行前已声明为任务目标,未事后缩减;补齐授权范围内数据'
              '或按降级面显式越过)')
    # R7-02: 陈旧必要数据单独点名(采集状态贯通判定;旧数据冒充当前
    # 研究可用=阻断交付,非普通覆盖缺口)
    _stale_mids = [i['metric_id'] for i in _req_items
                   if i['outcome'] == 'stale_for_task']
    if _stale_mids:
        notes.append('必要数据陈旧(采集状态贯通,R7-02): ' + '、'.join(
            _stale_mids) + '(末观测统计期落后任务窗止/研究时点超出频率族'
            '容忍;合法历史回放不受影响——参考端即回放时点)')

    layers = {
        'L1_事实层': {
            'available': snap is not None,
            'snapshot_id': (snap or {}).get('snapshot_id'),
            'target_date': (snap or {}).get('target_date'),
            'n_facts_total': len(facts or []),
            'rows': l1_rows,
            'note': None if snap else f'快照缺席: {snap_note}',
        },
        'L2_机构观点层': {
            'views': vpf,
            'note': '标签=证据评价非预测判定;阶段摘要 A/B/C 见 VP sidecar',
        },
        'L3_AI推断层': {
            'produced': False,
            'note': '零模型管线: 本层(矛盾综合/推断)须编排层 Agent 补作,'
                    'attribution=ai_inferred——本管线绝不代写。补作纪律: '
                    '四层标注(事实/推断/假设/尚未验证)+并列竞争性解释'
                    '(Skill 纪律4/第9步);机制链每环标 E1(引擎直接可验证)/'
                    'E2(部分支持,缺环明写【假设】)/E3(纯叙事,须给证伪指标)'
                    '(纪律15)',
        },
        'L4_条件情景层': {
            'produced': False,
            # R2.1 MAJOR-2(E席审计): 五行以 Skill 纪律16 权威模板为准
            # (旧措辞"前提/机制/路径"系 research_map 历史漂移,已一并统一)
            'note': '条件推演五行(纪律16: 情景[明写假设非预测]/资产方向判断'
                    '[方向+置信层级]/敏感变量[1-2 个引擎指标]/证伪指标'
                    '[可观测阈值]/触发条件[可观测条件+时限];单一情景不得'
                    '单独呈现,至少并列基准与反例)归编排层 Agent;'
                    '不冒充预测——本管线绝不代写',
        },
    }

    # 证据索引: 每个数字行必须有 fact_id/view_id 级来源
    evidence_index = []
    for r in l1_rows:
        evidence_index.append({'ref': r['source']['id'],
                               'kind': r['source']['kind'],
                               'metric_id': r['metric_id']})
    for r in (vpf.get('rows') or []):
        evidence_index.append({'ref': r['source']['id'],
                               'kind': r['source']['kind'],
                               'view_label': r['view_label']})
    # R33-③(首审席建议 narr-facts): S3 信封被引数字入索引——L3 叙事
    # 常引 changes 面指标(UST_10Y/TLT 等),旧索引只含问题命中(L1)+VP,
    # 被引数字无可锚行。S3_changes 信封 by_asset_class 全量在场指标入索引
    # (kind=s3_envelope),按 metric_id 与 L1 去重;缺席/缺值行不收。
    evidence_index.extend(_s3_envelope_rows(steps, l1_rows))
    missing_ref = [r['metric_id'] for r in l1_rows if not r['source']['id']]
    selfcheck = {'n_evidence_rows': len(evidence_index),
                 'n_rows_missing_ref': len(missing_ref),
                 'ok': not missing_ref}
    steps.append({'step': 'S10_selfcheck', 'executed': True,
                  'ok': bool(selfcheck['ok']),
                  'n_views_quarantined': n_quarantined,
                  'selfcheck': selfcheck,
                  'note': None if selfcheck['ok'] else f'缺来源行: {missing_ref}'})

    # ── S11 落档(S8 一次性完成;默认关) ─────────────────────────────
    qa_env = next((s.get('envelope') for s in steps
                   if s.get('step') == 'S8_grounded_qa'), {}) or {}
    archived_id = ((qa_env.get('data') or {}).get('archived_query_id')
                   if isinstance(qa_env, dict) else None)
    steps.append({'step': 'S11_archive', 'executed': True,
                  'ok': (archived_id is not None) if archive else True,
                  'archive_requested': bool(archive),
                  'archived_query_id': archived_id,
                  'note': ('已随 S8 落档' if archived_id
                           else '默认关(--archive 显式开启;Skill 第 11 步=用户认可后)')})

    if ent['note']:
        notes.append(ent['note'])

    # R2.1 MINOR-1: 诚实拒答步骤(如 S6 analog 短历史拒答)豁免出 run_ok
    run_ok = _run_ok(steps)

    # ── R3 十问扇出(可选,--fanout;独立于 S1-S11 主台账) ────────────
    fan = ({'requested': False}
           if not fanout else run_fanout(root, ia_timeout,
                                         [m for m in ent['metrics']]))

    _gh, _gh_src, _gh_dirty = _git_state(root)
    report = {
        'schema_version': '2.0',
        'pipeline_version': PIPELINE_VERSION,
        'run': {'question': question, 'ts_utc': _now_utc(),
                'archive_requested': bool(archive),
                'git_head': _gh,
                # R7-03: 版本绑定三级链(run_root→code_tree→
                # CODE_VERSION.json 印章)+执行树未提交差异指纹——
                # 引擎树(代码副本)运行不再 git_head=null 失绑
                'git_head_source': _gh_src,
                'git_diff_sha256': _gh_dirty,
                # Audit-R1 F02: 降级规则**运行前固定**(attach 段同文执行,
                # 双写互证;运行后不得改判)——可选数据缺失与关键失败分级
                'degradation_policy': {
                    'critical_zero_evidence': (
                        'L1 事实行=0(引擎崩溃/全量采集失败)→拒收判断,'
                        '--allow-failed-run 亦不放行'),
                    'required_data_missing': (
                        '运行前声明的必要指标(问题词面命中)采集缺席→'
                        '任务目标缺口,默认阻塞;显式 --allow-failed-run '
                        '才放行,落位记 degraded(缺口随档,不得事后改判可选)'),
                    'optional_data_missing': (
                        'L1 事实面在场、失败步=诚实拒答类(源端缺席 no_series)'
                        '→须显式 --allow-failed-run,落位记 degraded')},
                'data_requirements': data_requirements,
                },
        'steps': steps,
        'fanout': fan,
        'layers': layers,
        'evidence_index': evidence_index,
        'notes': notes,
        'run_ok': run_ok,
    }

    out_root = out_dir or os.path.join(root, 'output', 'research_runs')
    run_dir = os.path.join(out_root, f"{report['run']['ts_utc']}_{_slug(question)}")
    # R4 NIT(E席审计): 时间戳分钟级,同分钟两跑同名目录会互相覆盖——
    # 已存在则追加序号,绝不覆盖历史报告。
    n = 2
    while os.path.exists(run_dir):
        run_dir = os.path.join(
            out_root, f"{report['run']['ts_utc']}_{_slug(question)}_{n}")
        n += 1
    os.makedirs(run_dir)
    with open(os.path.join(run_dir, 'report.json'), 'w',
              encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    with open(os.path.join(run_dir, 'report.md'), 'w',
              encoding='utf-8') as f:
        f.write(_render_md(report))
    report['report_dir'] = run_dir
    return report


def _git_head(root):
    try:
        p = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'],
                           capture_output=True, text=True, timeout=10, cwd=root)
        return p.stdout.strip() if p.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def _git_state(root):
    """R7-03: 执行源码版本绑定三级链(新 B run.git_head=null 根因=引擎树
    为代码副本无 .git,单级 rev-parse 落空)。

    1. 运行树自身 git 库(run_root);
    2. 代码树(scripts 所在仓——引擎树=代码副本时,副本无 git 但其
       源仓可指认;若本进程即自仓运行则与 1 同级命中);
    3. 运行树根 CODE_VERSION.json 印章(引擎树建造时写入:
       git_head/git_diff_sha256/stamped_at——建造侧对源仓的快照指纹)。
    返回 (head|None, source|None, diff_sha256|None)——三级全空=(None,
    None,None)如实不造版本;diff_sha256=命中仓**未提交差异+未跟踪源码**
    联合指纹(R8-03: git diff HEAD 不含未跟踪件——新增源码参与执行时
    指纹必须随之变化,否则同 SHA 不同代码不可区分)。"""
    import hashlib as _hl
    _code_tree = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _seen = set()
    for cand, label in ((root, 'run_root'), (_code_tree, 'code_tree')):
        if not cand or not os.path.isdir(cand) or cand in _seen:
            continue
        _seen.add(cand)
        try:
            p = subprocess.run(['git', 'rev-parse', 'HEAD'],
                               capture_output=True, text=True, timeout=10,
                               cwd=cand)
            if p.returncode == 0:
                d = subprocess.run(['git', 'diff', 'HEAD'],
                                   capture_output=True, timeout=10, cwd=cand)
                h = _hl.sha256()
                h.update(d.stdout or b'')
                # R8-03: 未跟踪件(尊重 .gitignore)逐件内容哈希入指纹
                u = subprocess.run(
                    ['git', 'ls-files', '--others', '--exclude-standard'],
                    capture_output=True, text=True, timeout=10, cwd=cand)
                for rel in sorted(
                        (u.stdout or '').splitlines()):
                    rel = rel.strip()
                    if not rel:
                        continue
                    h.update(('\n::untracked:%s::' % rel).encode('utf-8'))
                    try:
                        with open(os.path.join(cand, rel), 'rb') as _f:
                            h.update(_hl.sha256(_f.read()).digest())
                    except OSError:
                        h.update(b'::unreadable::')
                return (p.stdout.strip(), label, h.hexdigest())
        except (OSError, subprocess.SubprocessError):
            pass
    stamp = os.path.join(root or '', 'CODE_VERSION.json')
    if os.path.isfile(stamp):
        try:
            j = json.load(open(stamp, encoding='utf-8'))
            if j.get('git_head'):
                return (j['git_head'], 'code_version_stamp',
                        j.get('git_diff_sha256'))
        except (OSError, ValueError):
            pass
    return None, None, None


def _render_l3(content):
    """R23: Agent Native L3 判断内容渲染(原文转述,排版不改写语义)。"""
    lines = []
    for c in (content.get('contradictions') or []):
        lines.append(f"- **{c.get('id')}**: {c.get('statement')}")
        if c.get('basis'):
            lines.append(f"  - 依据: {c['basis']}")
        for i, e in enumerate(c.get('competing_explanations') or [], 1):
            lines.append(f"  - 竞争性解释{i}: {e}")
        if c.get('evidence_refs'):
            lines.append(f"  - 证据: {', '.join(c['evidence_refs'])}")
        elif c.get('no_anchor_reason'):
            lines.append(f"  - 证据: 无锚(明示免锚: {c['no_anchor_reason']})")
    for ch in (content.get('mechanism_chains') or []):
        lines.append(f"- **机制链 {ch.get('id')}**: {ch.get('name') or ''}")
        for lk in (ch.get('links') or []):
            tag = lk.get('evidence_level')
            extra = ''
            if tag == 'E1' and lk.get('evidence_refs'):
                extra = f" [证据: {', '.join(lk['evidence_refs'])}]"
            elif tag == 'E2':
                extra = f" [缺失环: {lk.get('missing_link_note') or ''}]"
            elif tag == 'E3':
                extra = f" [证伪指标: {lk.get('falsification_metric') or ''}]"
            lines.append(f"  - {tag} {lk.get('text')}{extra}")
    return lines


def _render_l4(content):
    """R23: Agent Native L4 条件情景渲染(五行结构逐行落纸)。"""
    lines = []
    for s in (content.get('scenarios') or []):
        rows = s.get('rows') or {}
        ad = rows.get('asset_direction') or {}
        fals = rows.get('falsification') or {}
        trig = rows.get('trigger') or {}
        lines.append(f"- **{s.get('id')}**({s.get('role') or ''})")
        lines.append(f"  - 情景: {rows.get('scenario')}")
        lines.append(f"  - 资产方向判断: {ad.get('direction')}"
                     f"(置信: {ad.get('confidence_tier')})"
                     f" {ad.get('text') or ''}")
        lines.append(f"  - 敏感变量: {', '.join(rows.get('sensitive_variables') or [])}")
        lines.append(f"  - 证伪指标: {fals.get('metric_id')} 阈值 {fals.get('threshold')}")
        lines.append(f"  - 触发条件: {trig.get('condition')}(时限 {trig.get('deadline')})")
    return lines


def _render_md(r):
    """人类可读面: 四层区分+步骤台账+(可选)十问扇出台账+证据索引。"""
    def argv_str(step):
        return ' '.join(str(x) for x in (step.get('argv') or [])[:8])
    q = r['run']['question']
    L = r['layers']
    lines = [f"# 一键研究报告(零模型编排 v{r['pipeline_version']})",
             f"- 问题: {q}",
             f"- 运行: {r['run']['ts_utc']} @ {r['run'].get('git_head')}",
             f"- 快照: {L['L1_事实层'].get('snapshot_id')} "
             f"(target {L['L1_事实层'].get('target_date')})"]
    # R33-②(首审席 narr-facts): gate_a 状态披露行——首审发现全部步骤
    # 信封载 gate_a=DEGRADED 而 md 全文零披露。渲染时从各步信封顶层
    # 汇总(旧档重渲同样生效);降级不阻断,但判断层/读者须知。
    gates = [(s.get('step'), (s.get('envelope') or {}).get('gate_a'))
             for s in r.get('steps') or []
             if isinstance(s.get('envelope'), dict)
             and s.get('envelope').get('gate_a') is not None]
    if gates:
        bad = [g for g in gates if g[1] != 'OK']
        if bad:
            kinds = '、'.join(sorted({str(g[1]) for g in bad}))
            lines.append(f"- 数据门(gate_a): {len(bad)}/{len(gates)} "
                         f"信封步非 OK({kinds})——缺口/降级明细见步骤台账"
                         "各步信封 warnings;降级不阻断,判断层须知")
        else:
            lines.append(f"- 数据门(gate_a): OK({len(gates)}/{len(gates)} "
                         "信封步)")
    # Audit-R2 条目7 + Audit-R4 条目5: 数据需求声明(运行前冻结,含规格)
    # ——必要缺席/覆盖不足=任务目标缺口(最新单点≠历史分析需求满足)
    _dr = ((r.get('run') or {}).get('data_requirements') or {})
    if _dr.get('items'):
        _gap = sum(1 for i in _dr['items'] if i.get('outcome')
                   in ('missing', 'insufficient_coverage', 'stale_for_task'))
        lines.append(f"- 数据需求(运行前冻结): 必要 "
                     f"{sum(1 for i in _dr['items'] if i.get('tier') == 'required')}"
                     f" 项(问题命中,规格=序列/最低覆盖"
                     f"{(( _dr['items'][0].get('spec') or {}).get('min_observations'))}"
                     f" 观测),缺口 {_gap} 项;可选面缺席=降级披露不构成缺口")
        for i in _dr['items']:
            if i.get('outcome') in ('missing', 'insufficient_coverage',
                                    'stale_for_task'):
                _label = ('数据陈旧(采集状态贯通判定)' if i.get('outcome')
                          == 'stale_for_task' else '任务目标缺口')
                lines.append(f"  - {_label}: {i['metric_id']}"
                             f"({i.get('outcome_basis')})——未事后缩减,"
                             "补齐授权范围内数据或按降级面显式越过")
            # R7-02: 采集状态随项披露(续用/陈旧在报告面可见,非仅 json)
            _cs = (i.get('spec') or {}).get('collection_status')
            if _cs and _cs.get('mode') == 'carry_forward' \
                    and i.get('outcome') == 'satisfied':
                lines.append(
                    f"  - 续用披露: {i['metric_id']} 本轮采集失败续存非新"
                    f"采集(最后成功采集 {_cs.get('last_success_at')},续存自"
                    f" {_cs.get('carry_forward_from')},数据统计期至"
                    f" {_cs.get('last_observation_period')})——仍满足任务窗"
                    f"故可用")
    lines += ['', '## 四层区分', '']
    l1 = L['L1_事实层']
    lines.append(f"### L1 事实层 available={l1['available']}"
                 + ('' if l1['available'] else f"({l1['note']})"))
    for row in l1['rows']:
        # R23 审计 MINOR-5: 质量状态随行渲染(此前只在 json 面,
        # md 读者看不到 DEGRADED 披露)
        q = row.get('quality_status')
        lines.append(f"- {row['metric_id']} = {row['value']} {row['unit'] or ''}"
                     f" @{row['observation_date']}"
                     + (f" [质量:{q}]" if q else '')
                     + f" [来源:{row['source']['kind']}:{row['source']['id']}]")
    vpf = L['L2_机构观点层']['views']
    lines.append(f"\n### L2 机构观点层 "
                 f"available={vpf.get('available')}"
                 + (f" n={vpf['n']}" if vpf.get('available')
                    else f"({vpf.get('note')})"))
    for row in (vpf.get('rows') or []):
        ss = row.get('stage_summary') or {}
        lines.append(f"- {row['view_id']}: view_label={row['view_label']}"
                     f" 阶段摘要={ {k: ss.get(k) for k in ('A', 'B', 'C')} }")
    lines.append(f"\n### L3 AI推断层 produced={L['L3_AI推断层']['produced']}")
    if L['L3_AI推断层'].get('produced') and L['L3_AI推断层'].get('content'):
        lines.append(f"> {L['L3_AI推断层'].get('note') or ''}"
                     f"(attribution={L['L3_AI推断层'].get('attribution')})")
        lines += _render_l3(L['L3_AI推断层']['content'])
    else:
        lines.append(f"> {L['L3_AI推断层']['note']}")
    lines.append(f"\n### L4 条件情景层 produced={L['L4_条件情景层']['produced']}")
    if L['L4_条件情景层'].get('produced') and L['L4_条件情景层'].get('content'):
        lines.append(f"> {L['L4_条件情景层'].get('note') or ''}"
                     f"(attribution={L['L4_条件情景层'].get('attribution')})")
        lines += _render_l4(L['L4_条件情景层']['content'])
    else:
        lines.append(f"> {L['L4_条件情景层']['note']}")
    # R33-①(席位 runtime 接入;章程 §8 披露开关): L3/L4 在文且席位
    # 未裁→「叙事语义未经独立裁决」常设披露;席位裁决档在案→升为裁决
    # 摘要。状态面由 agent_judgment.attach_judgment 写入(旧档无该块
    # =旧面如实,不追溯)。
    sr = r.get('semantic_review') or {}
    if sr.get('required'):
        if sr.get('seat_invoked'):
            lines += ['', '## 语义审查(席位已裁)', '',
                      f"- 席位裁决: {sr.get('verdict')}"
                      f"(档: {sr.get('archive')})"]
        else:
            lines += ['', '## 语义审查(席位待唤起)', '',
                      '- **叙事语义未经独立裁决**——定性推断/条件情景在文;'
                      '常驻席位=SEMANTIC-AUDIT-SEAT,编排层应唤席裁决后'
                      '方可去掉本披露(章程 §4b/§8)']
    # R25 审计 Mi-1: agent_judgment 面入 md(attach/blocked/违规计数)——
    # md-only 读者可见落位状态(旧: 仅 report.json 有,md 零渲染)
    aj = r.get('agent_judgment') or {}
    if aj:
        if aj.get('blocked'):
            lines += ['', '## Agent 判断落位: 未落位(门槛拦截)', '',
                      f"- blocked={aj.get('blocked')}"
                      f"(run_ok={aj.get('run_ok_at_attach')};判断默认不得落在"
                      "失败证据面上,显式 --allow-failed-run 才放行)"]
        else:
            val = aj.get('validation') or {}
            lines += ['', '## Agent 判断落位', '',
                      f"- attached={aj.get('attached')}"
                      f"(schema {aj.get('schema_version')};"
                      f"violations={len(val.get('violations') or [])})"]
    lines += ['', '## 步骤台账', '']
    for s in r['steps']:
        # R39(R25 审计预存观察): executed 优先判——skipped_step 带 ok=True
        # (数据面契约: 跳过≠失败),原序 ok 先判→SKIP 分支死码,跳过步渲
        # [OK |—] 误导(读者以为执行成功)。先判 executed: 跳过步=SKIP+理由。
        tag = ('SKIP' if not s.get('executed') else
               ('OK ' if s.get('ok') else 'FAIL'))
        # R2.1 MINOR-3: 语义面单列(进程 ok ≠ 语义产出;诚实拒答/如实
        # unmapped 不与真失败混渲)。
        # R25 NIT V1-1(R24 审计): 按步骤性质三分——信封步(子进程产 JSON
        # 信封,semantic_ok 在场)才适用语义判定;编排内部步(S1/S7/S10/S11,
        # 无信封无 semantic_ok 键)原渲染恒落「语义✗」=标签噪音(内部步
        # 成败已由进程面 tag 忠实承载,语义层本就不适用)。方向保守:
        # 不藏任何失败——FAIL 仍照渲,只是不再给内部步贴误导读的语义标签。
        if not s.get('executed'):
            sem = '—'
        elif 'semantic_ok' in s:
            if s.get('semantic_ok') is True:
                sem = '语义✔'
            elif s.get('honest_refusal'):
                sem = '诚实拒答'
            else:
                sem = '语义✗'
        else:
            sem = '不适用'
        extra = s.get('skipped_reason') or s.get('note') or ''
        lines.append(f"- [{tag}|{sem}] {s['step']} {extra}")
    fan = r.get('fanout') or {}
    if fan.get('requested'):
        lines += ['', f"## 十问扇出台账(执行 {fan['n_executed']} / "
                  f"Agent 层 {fan['n_agent_layer']} / 共 {fan['n_rq']} 问)",
                  f"> 替身规则: {fan['substitution_rule']}", '']
        for row in fan['rq']:
            head = f"### {row['id']} {row.get('text') or ''} [{row.get('primary_layer')}]"
            lines += [head]
            if row['agent_layer_notes']:
                lines.append(f"- [Agent层|不代写] " + '; '.join(
                    n[:120] for n in row['agent_layer_notes']))
            for s in row['steps']:
                # R39: 同步骤台账 executed 优先判(跳过步不再渲 OK)
                tag = ('SKIP' if not s.get('executed') else
                       ('OK ' if s.get('ok') else 'FAIL'))
                extra = s.get('skipped_reason') or s.get('note') or ''
                sub = '; '.join(s.get('substitutions') or [])
                lines.append(f"- [{tag}] {s['step']} "
                             f"{argv_str(s)}{(' | 替身: ' + sub) if sub else ''}"
                             f"{(' | ' + extra) if extra else ''}")
            lines.append('')
    lines += ['', f"## 证据索引({len(r['evidence_index'])} 行)", '']
    # R33-③: 索引含 S3 信封行后全量渲(旧 60 行截断按 21 行规模设,
    # 现规模 ~60+;截断=被引数字锚面不可见,与③目的相悖)
    for e in r['evidence_index']:
        lines.append(f"- {e['kind']}:{e['ref']}"
                     + (f" → {e['metric_id']}" if e.get('metric_id') else '')
                     + (f" [{e['view_label']}]" if e.get('view_label') else ''))
    if r['notes']:
        lines += ['', '## 注记', ''] + [f"- {n}" for n in r['notes']]
    lines.append('')
    return '\n'.join(lines)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    import argparse
    p = argparse.ArgumentParser(description='一键研究编排(十一步确定性管线,零模型)')
    p.add_argument('--question', required=True)
    p.add_argument('--archive', action='store_true',
                   help='落档(Skill 第 11 步=用户认可后;默认关)')
    p.add_argument('--out-dir', default=None)
    p.add_argument('--root', default=ROOT)
    a = p.parse_args(argv)
    rep = run_research(a.question, root=a.root, archive=a.archive,
                       out_dir=a.out_dir)
    print(json.dumps({'run_ok': rep['run_ok'],
                      'report_dir': rep['report_dir'],
                      'n_steps': len(rep['steps']),
                      'n_evidence_rows': len(rep['evidence_index'])},
                     ensure_ascii=False, indent=2))
    return 0 if rep['run_ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
