#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R23 阶段四(Charter 10 §六)Agent Native L3/L4 落位与纪律机器校验。

架构分工(§6.1/§6.2,红线):
- Python=确定性引擎: 本模块**只做校验与落位,绝不生成任何判断内容**——
  L3(矛盾综合/推断)与 L4(条件情景)的每个字都来自 Agent 提交的 judgment
  文件;校验器对内容零改写(原文入档),只验证纪律结构是否齐备。
- Agent=经济学判断: Agent 在兼容环境(Claude Code 等)内读完
  research-run 确定性证据面(L1 事实/L2 观点/证据索引)后撰写 judgment,
  经本校验器机器核纪律,attach 合并进报告,L3/L4 produced=True,
  attribution=ai_inferred(永非 institution_stated——机构明示面归 views 库)。

机器可查纪律子集(Skill 纪律 4/15/16 的结构面;判断质量归 Agent 与独立审计)。
已知边界: "假设"采用子串代理(与 E2 检查同口径)——"非假设"类对抗措辞含该
子串会漏拦,语义面归 Skill lint 与独立审计,不在本校验器伪装语义理解:
- ATTR    attribution 必须 ai_inferred(防 Agent 成果冒充机构观点)
- CON-EXP 每条矛盾陈述须并列 >=2 竞争性解释(纪律 4)
- CON-REF 每条矛盾陈述须 >=1 可解析证据引用,或明示免锚
          (no_anchor_reason 非空=R23 审计 MINOR-1: 零引用放行会割裂
          结论-证据绑定;免锚必须显式声明理由,不许静默零锚)
- REF     所有 evidence_refs 必须解析到**本报告证据索引**内的 fact_id/VP id
          (结论-证据绑定,R22 5.3 同源纪律;悬空引用拒收)
- E1-REF  E1 环(引擎直接可验证)须带 >=1 可解析证据引用
- E2-ASSUM E2 环须明写缺失环【假设】(missing_link_note 含"假设")
- E3-FALS E3 环(纯叙事)须给证伪指标(注册表在册 metric_id)
- SCN-FIVE 每情景五行齐备(情景/资产方向判断/敏感变量/证伪指标/触发条件)
- SCN-TYPE 五行类型锁(R23 审计 NIT: scenario=str/asset_direction=dict/
          sensitive_variables=list/falsification=dict/trigger=dict——
          错型原先静默绕过下游检查,现在显式拒收)
- SCN-ASSUM 情景行须含"假设"(明写假设非预测)
- POL-EFF 决议-生效成对(Audit-R31 任务3;policy_events 在场时启用):
          段落含政策词形+已知决议日词形时,须配该决议生效日词形或
          待生效/尚未生效/未生效 标注——次月末才生效不得写成当时已发生
          (Audit-R32 任务2 精化: as_of 在场时按实体/断言时点/决议日/
          生效日逐事件核验——POL-EFF-DATE 生效日写成早于官方生效日/
          POL-EFF-REL 相对生效词形早于官方生效间隔/POL-EFF-EARLY-CLAIM
          生效前「已生效/目前」断言/POL-EFF-PENDING-AS-CURRENT 待生效值
          写成当前值;实体词形不绑=不触发;
          Audit-R33 任务2 逐分句: 断言时点=段内显式「截至 X」优先——
          POL-EFF-EARLY-CLAIM 生效前分句写已实施/POL-EFF-LATE-PENDING
          生效后仍写尚未生效/POL-EFF-DECISION-NOT-YET-KNOWN 公告前以
          既成事实提及决议)
- SCN-DIR 资产方向判断=方向+置信层级(三档枚举: 有历史相似证据/有相关证据/纯逻辑推理)
- SCN-SENS 敏感变量 1-2 个且均为注册表在册 metric_id
- SCN-FALS 证伪指标=在册 metric_id+可观测阈值非空
- SCN-FALS2 复合证伪条件可选副指标(v1.1/R25 NIT V2-5): threshold 文本
          提及多指标时,主 metric_id 之外的指标可经 secondary_metric_ids
          (list,1-3 条,逐条在册)机器锚定——复合条件不再"可读但口径不对称";
          缺席不违规(单指标条件不需要),主锚仍由 metric_id 承担
- SCN-TRIG 触发条件=可观测条件+时限(YYYY-MM-DD)
- SCN-PLURAL >=2 情景并列(基准+反例;单一情景不得单独呈现)

入口: validate_judgment(judgment, evidence_refs, metric_ids) → dict;
      attach_judgment(report_dir, judgment_path, root=None) → dict(校验不过
      则 produced 保持 False,violations 落档,绝不半落位)。
"""
import contextlib
import copy
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
SCRIPTS = os.path.join(ROOT, 'scripts')
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

JUDGMENT_SCHEMA_VERSION = '1.1'   # v1.0(R23)→v1.1(R25): falsification 增可选 secondary_metric_ids(复合证伪条件副指标锚)
CONFIDENCE_TIERS = ('有历史相似证据', '有相关证据', '纯逻辑推理')
ASSUMPTION_MARK = '假设'
_DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')

SCENARIO_ROWS = ('scenario', 'asset_direction', 'sensitive_variables',
                 'falsification', 'trigger')


def _now_utc():
    return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')


def _load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def collect_policy_events(calendar_path=None):
    """Audit-R31 任务3: 决议-生效成对纪律的**确定性事件面**。

    读发布日期历(经 release_calendar._load——IA_CALENDAR_PIN 钉死在场
    时读冻结副本,与运行/重放同源)的 policy_decision 条目,产出
    [{'metric_id', 'decision_date', 'effective_on', 'entity',
    'target_value', 'entry_id', 'first_publish'}];无日历/无条目=[]
    (规则按缺席处理,不虚构)。生效日=决议日(即时生效)的条目也返回
    (成对口径统一,匹配侧自然放行)。

    Audit-R32 任务2 补: entity(实体=决议归属经济体,由 metric_id 映射,
    供正文实体绑定——美联储段落不因日银决议日同日而误判)、target_value
    (宣布目标水平,供「待生效值写成当前值」判定)、first_publish(公告
    可见日,供研究时点前的决议不参与判定)。Audit-R33 任务2修订 r4
    补: direction(条目可选的方向字段,up/down/hike/cut/raise/lower,
    缺省 None——供方向可定的「尚未加息」类动作词未然句判定)。

    显式路径缺席=直接空面(不触发 _load 的缺席告警 print——该告警走
    stdout 会污染 ia_cli JSON 单流信封,夹具树无日历时 attach 段信封
    解析即碎;R18 §D 实证)。"""
    try:
        import release_calendar as _rc
        if calendar_path is not None and not os.path.isfile(calendar_path):
            return []
        events = []
        for e in _rc._load(calendar_path):
            if e.get('kind') != 'policy_decision':
                continue
            dd, eff = e.get('decision_date'), e.get('effective_on')
            if isinstance(dd, str) and isinstance(eff, str):
                mid = e.get('metric_id')
                tv = e.get('target_value')
                events.append({'metric_id': mid,
                               'decision_date': dd[:10],
                               'effective_on': eff[:10],
                               'entity': _POL_METRIC_ENTITY.get(mid),
                               'target_value': (float(tv)
                                                if isinstance(tv, (int, float))
                                                else None),
                               'entry_id': e.get('entry_id'),
                               'direction': e.get('direction'),
                               'first_publish': str(
                                   e.get('first_publish_on_or_after')
                                   or e.get('decision_date'))[:10]})
        return events
    except Exception:
        return []


# ── Audit-R32 任务2: 政策核验按实体/断言时点/决议日/生效日 ──────────────
# 实体词形(正文绑定: 段落只提别家央行时不套本事件——R31 子串代理无实体
# 绑定,同日决议的美日段落会交叉误判);决议→生效惯例偏移(日):
#   即日/当天/立即=0,次日/翌日=1——相对生效词形折算成隐含生效日与官方
#   实录 effective_on 比对,隐含日早于官方=提前生效。
_POL_METRIC_ENTITY = {'JP_POLICY_TARGET': 'JP', 'ECB_MRO': 'EA',
                      'DFEDTARU': 'US', 'CN_LPR_1Y': 'CN'}
_POL_ENTITY_WORDS = {
    'JP': ('日本央行', '日银', 'BOJ', '日本', '日圆', '日元', '日债'),
    'EA': ('欧央行', '欧洲央行', 'ECB', '欧元区', '欧洲', '欧元'),
    'US': ('美联储', 'Fed', 'FOMC', '美国', '美元', '美债'),
    'CN': ('人民银行', 'PBOC', '中国央行', 'LPR', '中国', '人民币'),
}
_POL_PENDING_MARKS = ('待生效', '尚未生效', '未生效', '将于', '拟于',
                      '计划于', '将升', '将降', '将上调', '将下调', '将调',
                      '将生效', '起将', '将自', '起生效', '日后生效',
                      '后生效', '待实施', '即将生效',
                      '将为', '将是', '将定在', '将设在')   # 修订 r5: 系词/设定形
_POL_CURRENT_MARKS = ('已生效', '已经生效', '生效后', '现行', '目前', '当前',
                      '现在', '现为', '已降至', '已升至', '已上调至',
                      '已下调至', '已调整为', '处于')
_POL_REL_EFF = (                # (正则, 隐含生效偏移日)
    (r'(?:决议|决定|宣布|公布|公告|调整|降息|加息|上调|下调)[^,，。;；:：?？]{0,8}?(次日|翌日|第二天)生效', 1),
    (r'(?:自|从)(?:决议|决定|宣布|公布|公告)(?:日)?(?:起)?(?:的)?(?:次日|翌日|第二天)起?生效', 1),
    (r'(?:决议|决定|宣布|公布|公告|调整|降息|加息|上调|下调)[^,，。;；:：?？]{0,8}?(即日|当天|当日|立即|即刻|即时|随即|马上)生效', 0),
    (r'(?:决议|决定|宣布|公布|公告|调整|降息|加息|上调|下调)(?:即|便|就)生效', 0),
)
_POL_REL_CUT_WORDS = ('次日', '翌日', '第二天', '即日', '当天', '当日',
                      '立即', '即刻', '即时', '随即', '马上', '天后', '日后',
                      '周后', '月后', '小时后')
_POL_NEG_EFF = re.compile(      # 生效前 4 字内的未然/否定前缀(切片尾锚定)
    r'(?:尚未|未|待|即将|将|不会|不能|拟|并不|并未|不曾)$')
_POL_EFF_NEXT = re.compile(     # 「生效」标签前置: 生效(日|于|为|…)+日期词元
    r'(?:日期|日|于|为|是|自|:|：|\s|\(|（){0,3}(?=\d)')
_POL_DATE_TOKEN = re.compile(
    r'(\d{4})年(\d{1,2})月(\d{1,2})日|(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})'
    r'|(\d{4})(\d{2})(\d{2})|(?<![\d年])(\d{1,2})月(\d{1,2})日')


def _pol_bound_events(text, events):
    """正文段绑定到的政策事件(实体绑定: 段落提了别家实体而未提本实体
    →不绑;无实体信息的事件(R31 旧调用方)=按原口径绑)。"""
    out = []
    for ev in events:
        ent = ev.get('entity')
        if ent:
            has_own = any(w in text for w in _POL_ENTITY_WORDS.get(ent, ()))
            has_other = any(
                w in text for k, ws in _POL_ENTITY_WORDS.items()
                if k != ent for w in ws)
            if has_other and not has_own:
                continue
        out.append(ev)
    return out


def _pol_date_tokens(text):
    """正文日期词元 → [(iso|None, month, day, start_idx, end_idx)];
    无年份形(9月24日)iso=None(由调用方按决议日年份折算)。"""
    out = []
    for m in _POL_DATE_TOKEN.finditer(text):
        if m.group(1):
            iso = '%04d-%02d-%02d' % (int(m.group(1)), int(m.group(2)),
                                      int(m.group(3)))
            mm, dd = int(m.group(2)), int(m.group(3))
        elif m.group(4):
            iso = '%04d-%02d-%02d' % (int(m.group(4)), int(m.group(5)),
                                      int(m.group(6)))
            mm, dd = int(m.group(5)), int(m.group(6))
        elif m.group(7):
            iso = '%s-%s-%s' % (m.group(7), m.group(8), m.group(9))
            mm, dd = int(m.group(8)), int(m.group(9))
        else:
            iso, mm, dd = None, int(m.group(10)), int(m.group(11))
        out.append((iso, mm, dd, m.start(), m.end()))
    return out


def _pol_days(a, b):
    try:
        return (datetime.fromisoformat(str(b)[:10]).date()
                - datetime.fromisoformat(str(a)[:10]).date()).days
    except (ValueError, TypeError):
        return None


def _pol_value_in_text(value, text):
    """宣布目标水平在正文以独立数字出现(1.25 / 1.25% / 约1.25%;不匹配
    更长数字的片段,如 11.25 或 1.255)。"""
    forms = set()
    for fmt in ('%g', '%.2f', '%.3f'):
        s = fmt % value
        forms.add(s)
        if s.endswith('.00'):
            forms.add(s[:-3])
        elif s.endswith('0') and '.' in s:
            forms.add(s[:-1])
    for s in forms:
        if re.search(r'(?<![\d.])' + re.escape(s) + r'(?![\d])', text):
            return True
    return False


_POL_CN_DIGIT = {'零': 0, '〇': 0, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4,
                 '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}
_POL_CN_NUM_RE = re.compile(
    r'百分之[零〇一二两三四五六七八九十]{1,4}(?:点[零〇一二两三四五六七八九]{1,4})?'
    r'|[零〇一二两三四五六七八九]点[零〇一二两三四五六七八九]{1,4}')


def _pol_cn2num(s):
    """中数词 → 数值(修订 r4;写法超出「X点YZ / 十 / 百分之…」= None):
    「一点二五」→ 1.25,「百分之十二点五」→ 12.5,「二十」→ 20。"""
    ip, _, fp = s.partition('点')
    val = 0.0
    if ip:
        if '十' in ip:
            a, _, b = ip.partition('十')
            if ((a and a not in _POL_CN_DIGIT)
                    or (b and b != '零' and b not in _POL_CN_DIGIT)):
                return None
            val = (_POL_CN_DIGIT[a] if a else 1) * 10 + (
                _POL_CN_DIGIT[b] if b and b != '零' else 0)
        elif len(ip) == 1 and ip in _POL_CN_DIGIT:
            val = _POL_CN_DIGIT[ip]
        else:
            return None
    if fp:
        if any(ch not in _POL_CN_DIGIT for ch in fp):
            return None
        for i, ch in enumerate(fp):
            val += _POL_CN_DIGIT[ch] * 10.0 ** (-(i + 1))
    elif not ip:
        return None
    return round(val, 6)


def _pol_cn_values(text):
    """正文里的中数词数值集合(目标水平比对用;「百分点」「一点」等不成数)。"""
    out = set()
    for m in _POL_CN_NUM_RE.finditer(text or ''):
        v = _pol_cn2num(m.group(0).replace('百分之', ''))
        if v is not None:
            out.add(v)
    return out


_POL_VAL_CTX_PRE = re.compile(
    r'(?:不低于|不高于|不超过|不少于|至少|至多|高于|低于|超过|不足)(?:约|大约)?\s*$')
_POL_VAL_CTX_POST = ('以下', '以上', '以内', '之外', '下方', '上方')


def _pol_value_spans(value, text):
    """宣布目标水平在正文以独立数字出现的跨度(与 _pol_value_in_text 同形)。"""
    forms = set()
    for fmt in ('%g', '%.2f', '%.3f'):
        s = fmt % value
        forms.add(s)
        if s.endswith('.00'):
            forms.add(s[:-3])
        elif s.endswith('0') and '.' in s:
            forms.add(s[:-1])
    out = []
    for s in forms:
        for m in re.finditer(r'(?<![\d.])' + re.escape(s) + r'(?![\d])',
                             text or ''):
            out.append((m.start(), m.end()))
    return out


def _pol_level_val(ctext, tvf):
    """目标值以「水平」口径出现(修订 r4): 阿拉伯数字或中数词,且不带比较
    语境(「1.25% 以下」「不低于 1.25%」说的不是水平本身)。"""
    if tvf is None:
        return False
    spans = _pol_value_spans(tvf, ctext)
    spans += [(m.start(), m.end()) for m in _POL_CN_NUM_RE.finditer(ctext)
              if _pol_cn2num(m.group(0).replace('百分之', ''))
              == round(tvf, 6)]
    for a, b in spans:
        pre = ctext[max(0, a - 6):a]
        post = ctext[b:].lstrip('%％ ')
        if (post[:2] in _POL_VAL_CTX_POST
                or _POL_VAL_CTX_PRE.search(pre)):
            continue
        return True
    return False


_POL_LEVEL_NONCOMPL_RE = re.compile(
    r'(?:决议|决定|宣布|公布|出炉)(?:将|把)?$'
    r'|(?:将|拟|计划|预期|预计|料|有望|或将|或于|若|如果|一旦|是否|可能|须|需'
    r'|应|要)$')


def _pol_level_stmt(ctext):
    """政策利率名词+系词的「水平陈述」(修订 r4): 名词紧前是「决议/决定/宣布
    (将/把)」「将/拟/若…」非完成词的(「决议将政策利率上调至 x」「若政策利率
    为 x」)说的是决定内容或条件,不算现行口径;「决议的目标利率为 x」仍按
    水平陈述核验(断言时点早于生效日而无未然标注=拒收)。"""
    for m in _POL_LEVEL_RE.finditer(ctext):
        if not _POL_LEVEL_NONCOMPL_RE.search(ctext[:m.start()]):
            return True
    return False


def _pol_pend_marks(ctext):
    """分句内的谓述性未然标记 [(起点, 止, 是否否定型)](修订 r4): 「尚未/未/
    待/即将+生效类动词」与「将…」词形;后接「的」(定语「待生效的决定」)或
    「面/项」(数据面名「待生效面」)的不算;否定型还须是谓述(后接句读、助词
    或连词),「未生效调整」「未生效前」一类题名/时间状语不算;「将于 X 公布/
    召开」日程形不算。"""
    out = []
    for neg, rx in ((True, _POL_PEND_NEG_RE), (False, _POL_PEND_FUT_RE)):
        for m in rx.finditer(ctext):
            if not neg and _POL_SCHED_VERB_RE.match(ctext, m.end()):
                continue          # 日程/公布的将来形: 「将于 18 日公布决议」
            after = ctext[m.end():m.end() + 1]
            if after in ('的', '面', '项'):
                continue          # 定语/数据面名: 「待生效的决定」「待生效面」
            if neg and after and after not in _POL_PRED_AFTER:
                continue          # 题名/时间状语: 「未生效调整」「未生效前」
            out.append((m.start(), m.end(), neg))
    return out


def _pol_dir(ev, cands):
    """事件方向 'up' / 'down' / None(修订 r4): 日历条目带 direction 字段则
    用之;否则与同指标、决议更早的最近一件带目标值的事件比较目标水平;
    无从比较 = None(日历无方向字段且无前件——动作词未然句「尚未加息」不判)。"""
    d = str(ev.get('direction') or '').strip().lower()
    if d in ('up', 'down', 'hike', 'cut', 'raise', 'lower'):
        return 'down' if d in ('down', 'cut', 'lower') else 'up'
    try:
        tv = float(ev.get('target_value'))
    except (TypeError, ValueError):
        return None
    prev = [e for e in cands
            if e is not ev and e.get('metric_id') == ev.get('metric_id')
            and e.get('target_value') is not None and ev.get('decision_date')
            and str(e.get('decision_date')) < str(ev['decision_date'])]
    if not prev:
        return None
    try:
        pv = float(max(prev, key=_pol_ev_key).get('target_value'))
    except (TypeError, ValueError):
        return None
    return 'up' if tv > pv else ('down' if tv < pv else None)


_POL_EFF_WORDS = ('利率', '政策', '加息', '降息', '目标', 'LPR', 'BOJ',
                  '日银', '欧央行', '欧洲央行', '美联储', '央行', '决议',
                  'policy', 'rate')


def _date_word_forms(iso):
    """ISO 日期的中文/紧凑/斜杠词形集(文本子串匹配用,与点锚词形同族)。

    Audit-R31 任务3 补: 补零/不补零两形都收(「2026/4/28」「2026年4月28日」
    与补零形同判——子串代理对零填充不敏感,漏形=漏拦)。"""
    y, m, d = iso[:4], int(iso[5:7]), int(iso[8:10])
    return {iso, '%s/%s/%s' % (y, iso[5:7], iso[8:10]),
            '%s/%d/%d' % (y, m, d), '%s-%d-%d' % (y, m, d),
            '%s年%s月%s日' % (y, iso[5:7], iso[8:10]),
            '%s年%d月%d日' % (y, m, d),
            '%d月%d日' % (m, d), '%02d月%02d日' % (m, d),
            y + iso[5:7] + iso[8:10]}


# ── Audit-R33 任务2: 政策时态=政策事件 × 断言时点 × 实施状态(逐分句) ──
# R32 的时点类规则只认运行级截止日、按整段匹配现行词形:
# 「截至 9 月 20 日，9 月 24 日生效的加息已经实施」——断言时点(段内显式
# 截至 X)早于生效日、「已经实施」不在现行词形表、带空格日期不成词元,
# 整段放行(基线正式入口复现)。本节按分句建模:
#   断言时点 = 分句内显式「截至/截止/断言时点 X」或区间端「窗内(A..T)」
#              > 同句前文分句的时点 > 运行级截止日(as_of);
#   分句状态 = 已实施(完成态实施词形)/ 未然(尚未·将·待生效)/ 现行口径
#   (现行词形+事件目标值或事件日期)/ 预期口径(市场预期·定价·概率);
#   逐事件判定(实体绑定与 R31/R32 规则照旧按原文运行,旧档重放零漂移):
#     POL-EFF-DECISION-NOT-YET-KNOWN 断言时点早于决议公告日,正文以既成
#         事实提及该决议(事后信息;预期/将然口径豁免);
#     POL-EFF-EARLY-CLAIM          断言时点早于生效日,事件分句写已实施,
#         或以现行口径写事件目标值/事件日期而无未然标注;
#     POL-EFF-LATE-PENDING         断言时点不早于生效日,事件分句仍写
#         尚未生效/待生效(历史叙述·预期口径豁免)。
# 修订 r3(独立审查六 MAJOR): 时点辖域=句(以句末标点为界,不跨句);完成态
# 分句与同段的事件日期/断言时点合并理解;裸「落地/生效」与「加息至+中数词」
# 计入完成态;区间端=断言时点;生效后分支不再因同段另有完成态词形整段放行;
# 违规详情注明断言时点来源(MINOR-2);段级旗标只作消歧辅助(MINOR-3)。
# 修订 r4(独立审查六 MAJOR=六条误收,均因状态断言不带事件日期而放行):
# 归属加「断言时点的在办事件」一路;既成句形/实施状态未然/目标水平
# (含中数词)三种状态各自成规则;句首独立日期分句=断言时点;区间整体
# 置「□」。详见 _pol_rel 及各旗标注记。
_POL_IMPL_MARKS = ('已经实施', '已实施', '已经执行', '已执行', '已经落地',
                   '已落地', '已经生效', '已生效', '已开始实施',
                   '已经开始实施', '已开始执行', '已经开始执行',
                   '已经付诸实施', '已付诸实施', '已适用', '已经适用',
                   '已升至', '已降至', '已上调至', '已下调至', '已调整为')
_POL_NOT_YET_MARKS = ('尚未', '未生效', '待生效', '待实施', '即将生效')
_POL_NOT_YET_NEG = re.compile(          # 否定语境=不是在说它还没生效
    r'(?:不存在|并非|不是|已无|没有|并无|而非|不算|不在)[^，,。;；]{0,6}'
    r'(?:尚未|未生效|待生效|待实施|即将生效)'
    r'|(?:无|没有|不存在)(?:任何|已决议的?|已决议而)?(?:尚未生效|未生效'
    r'|待生效|待实施|即将生效)'
    r'|(?:无|没有)(?:已决议(?:而|的)?|尚无[^，,。;；]{0,4})?(?:未生效|待生效)'
    r'[^，,。;；]{0,8}(?:官方记录|记录|可核|实录)'
    r'|不等于(?:未|没有|不会)')
_POL_PEND_RE = re.compile(
    r'将(?:处于|维持|保持|留在|位于|升至|降至|上调|下调|加息|降息|调整'
    r'|生效|于|自|为|是|定在|设在)|有待|仍?待(?:观察|定|公布|决议|落地|实施|生效)')
_POL_CUR_CLAUSE_MARKS = tuple(w for w in _POL_CURRENT_MARKS
                              if w != '生效后')      # 「X生效后」=条件参照
_POL_EXPECT_MARKS = ('预期', '预计', '可能', '或将', '或于', '料将',
                     '市场定价', '隐含', '押注', '有待', '待定', '定价',
                     '概率', '几率', '前景', '假设', '倘若', '如果', '若')
_POL_PAST_CTX_MARKS = ('决议时', '当时', '此前', '时尚未', '时还', '之前尚',
                       '之前未', '前尚', '研究时点早于', '时仍未', '决议前',
                       '生效前', '公布时', '宣布时', '发布时', '公告时')
_POL_POL_CHANGE_WORDS = ('加息', '降息', '上调', '下调', '调整', '决议',
                         '决定', '收紧', '宽松', '政策利率', '目标利率')
_POL_MEETING_WORDS = ('会议', '议息', '召开', '日程', '议程')
_POL_CLAUSE_RE = re.compile(r'[^，,。；;！!？?\n]+')
_POL_SENT_RE = re.compile(r'[^。！!？?\n]+')
_POL_ASOF_RE = re.compile(
    r'(?:截至|截止到|截止于|截止|断言时点|研究时点|as\s*of)\s*[:：=为是]?\s*'
    r'(?:(\d{4})[-/.年](\d{1,2})[-/.月](\d{1,2})日?'
    r'|(\d{4})(\d{2})(\d{2})'
    r'|(\d{1,2})月(\d{1,2})日)')
_POL_DATE_ALTS = (r'(\d{4})[-/.年](\d{1,2})[-/.月](\d{1,2})日?',
                  r'(\d{4})(\d{2})(\d{2})',
                  r'(?<![\d年])(\d{1,2})月(\d{1,2})日')
_POL_ONE_DATE = '(?:' + '|'.join(_POL_DATE_ALTS) + ')'
# 区间端「(A..T)」: 起点组 0–7,终点组 8–15(每个日期形 8 组)
_POL_WIN_RE = re.compile(
    _POL_ONE_DATE + r'\s{0,3}(?:\.\.|…|~|～|—|–|--|至|到)\s{0,3}'
    + _POL_ONE_DATE)          # 起点组 0–7,终点组 8–15
# 局部时点「在/于 X 时」「X 时 / X 当天 / X 以前」
_POL_LOCAL_RE = re.compile(
    r'(?:在|于)\s*' + _POL_ONE_DATE
    + r'\s*日?\s*(?:时|当天|当日|之际|以前|之前)'
    r'|' + _POL_ONE_DATE + r'\s*日?\s*(?:时|当天|当日|之际)(?!间)'
    r'|' + _POL_ONE_DATE + r'\s*日?\s*(?:以前|之前)')
# 局部时点三支的日期组基: 0 / 8 / 16
_POL_ANAPHOR_RE = re.compile(
    r'该决议|该加息|该降息|该决定|该调整|这一决议|此项决议|上述决议'
    r'|这次加息|这次降息')
_POL_DONE_VERB_RE = re.compile(r'(生效|落地|实施|执行|实行)(了|完毕|到位)?')
_POL_DONE_AT_RE = re.compile(
    r'(?:已经|已)(?:于|在|自|从)?\s*' + _POL_ONE_DATE
    + r'\s*日?\s*(?:起)?\s*(?:正式|全面|开始)?'
    r'(?:生效|落地|实施|执行|施行|完成|实行)')
_POL_RAISE_TO_RE = re.compile(r'(?:加息|降息|上调|下调|调整|收紧|宽松)至')
_POL_NONCOMPL_PRE = ('决议', '决定', '宣布', '将', '拟', '计划', '预期',
                     '预计', '或', '料', '有望', '若', '如果', '一旦', '是否',
                     '可能', '可', '须', '需', '应', '要', '并')


# 修订 r4(独立审查六条 MAJOR 均为误收——状态断言不带事件日期时整段放行):
#   归属: 无事件日期的状态断言(既成/未然/目标水平)按「断言时点的在办事件」
#         归属(_pol_rel): 分句指向别的时间/别的事件→不绑;池内(同实体)在办
#         事件须恰为本事件(公告前=其后将公告的最早一件且无待生效者;公告后
#         生效前=t 时待生效者;生效后=t 时已知的最新一件);
#   既成句形: 「已决议/已决定/已宣布」「决议加息」「公布…决议」=公告前既成
#         事实(「决议后」类叙述参照豁免);
#   未然: 实施状态词形(尚未/未/待/即将+生效类动词、将然形;方向可定时的
#         「尚未加息」)才算把已生效的决定写成待生效——宽口径「尚未」只作
#         豁免;叙述性将来(「X 日决议加息,将于 Y 日生效」)豁免;
#   目标水平: 政策利率名词+系词+目标值(阿拉伯数字或中数词)=现行口径;
#   时点: 句首独立日期分句=断言时点;区间「A 至 T」整体置「□」(起点日期
#         不再留作分句内日期词元——此前带区间的既成句因此不绑定)。
_POL_DEC_DONE_RE = re.compile(
    r'(?:已经|已)(?:决议|决定)'
    r'|(?:决议|决定|宣布|公布|发布|出炉|出台|通过|敲定|批准)(?:了)?(?:的)?'
    r'(?:加息|降息|升息|减息|上调|下调|维持利率|利率决议|政策决议|决议|决定'
    r'|政策调整)')   # 「已发布数据」「已通过测试」一类非决议宾语不算
_POL_POST_REF_MARKS = ('决议后', '决定后', '公布后', '发布后', '宣布后',
                       '出炉后', '出台后', '通过后', '决议以来', '公布以来',
                       '宣布以来', '决议之前', '公布之前', '宣布之前', '审议前')
_POL_PEND_NEG_RE = re.compile(
    r'(?:尚未|仍未|暂未|还未|还没有|还没|并未|不曾|尚没|(?<!从)未(?!来)|没)'
    r'[^，,。;；]{0,5}?(?:生效|落地|实施|执行|实行|施行|到位|付诸实施|付诸执行)'
    r'|(?:待|即将)(?:生效|落地|实施|执行|施行)')
_POL_PEND_FUT_RE = re.compile(
    r'将(?:会|要)?(?:处于|维持|保持|留在|位于|升至|降至|上调|下调|加息|降息'
    r'|调整|生效|于|自|为|是|定在|设在)')   # 修订 r5: 系词/设定形「将为/将是/将定在」
# 「将于 X 公布/召开…」=日程/公布的将来形,不是实施状态未然(公告前合法,
# 生效后也不是把已生效的决定写成待生效)
_POL_SCHED_VERB_RE = re.compile(
    r'[^，,。;；]{0,14}?(?:公布|发布|宣布|出炉|召开|举行|审议|议息|会议|揭晓)')
# 否定型未然的「生效/落地…」须是谓述(后接句读、助词或连词),后接名词的
# 「未生效调整」「待生效决定」「未生效前」是定语/题名,不算
_POL_PRED_AFTER = frozenset('，,。；;！!？?、了过并且而或就才即也仍)）】」』”—')
_POL_PEND_SUBJ_GUARD = ('传导', '影响', '效果', '作用', '效应')   # 说的不是决定本身
# 未然标记的主语须是紧邻的决定/动作名词(中间至多两个副词,不得隔连词/系词)——
# 「待生效面」「待生效为空」「…水平与待生效…」一类数据面名、并列不算
_POL_PEND_SUBJ_RE = re.compile(
    r'(?:加息|降息|升息|减息|上调|下调|调整|收紧|宽松|决议|决定|政策目标利率'
    r'|政策利率|目标利率|政策目标|利率决定)[^，,。;；与和及、或是为有无的]{0,2}$')
_POL_ACT_PEND_RE = re.compile(
    r'(?:尚未|仍未|暂未|还未|还没有|还没|并未|不曾|尚没)[^，,。;；]{0,3}?'
    r'(加息|降息|升息|减息|上调|下调|收紧|宽松)(?![至到])')
_POL_ACT_DIR = {'加息': 'up', '升息': 'up', '上调': 'up', '收紧': 'up',
                '降息': 'down', '减息': 'down', '下调': 'down', '宽松': 'down'}
_POL_LEVEL_RE = re.compile(
    r'(?:政策目标利率|政策利率|目标利率|利率目标|政策目标|基准利率|官方利率)'
    r'[^，,。;；]{0,10}?(?:为|是|处于|维持在|维持于|维持|位于|保持在|保持|留在'
    r'|设在|定在|报|立于|等于|达到|来到|站上|升至|上调至|下调至|降至|调至|落在)')
_POL_EFF_VERBS = ('生效', '实施', '落地', '执行', '实行', '施行')   # 生效动词
_POL_DATE_START_RE = re.compile(r'日(?:起|开始|之后|以后|后|当天|当日)')
_POL_AFTER_REF_MARKS = ('生效后', '落地后', '实施后', '执行后', '之后', '以后',
                        '其后', '随后', '届时', '此前')
_POL_OTHER_EV_RE = re.compile(
    r'下一次|新一轮|下一轮|后续|随后|此后|再次|另一次|再度|进一步|第二次|下一期'
    r'|明年初|明年|下一年|年底前|年末前|未来|稍后|晚些')
_POL_YM_RE = re.compile(r'(?<![\d年])(?:([12]\d{3})年)?(\d{1,2})月(?![\d日])')
_POL_YEAR_RE = re.compile(r'(?<!\d)([12]\d{3})年(?!\d)')
_POL_LEAD_DATE_RE = re.compile(_POL_ONE_DATE + r'日?')   # 句首独立日期分句
# 句首标签前缀(修订 r5): 「时态核对: 」「日本央行: 」一类短标签+冒号。标签只许
# 汉字/拉丁字母/括号/间隔号/空白(不含数字),且不得含日期字段词——「生效日期: X」
# 的 X 是事件日期(交日期规则核对),不是断言时点
_POL_LEAD_LABEL_RE = re.compile(
    r'[\u4e00-\u9fffA-Za-z（）()·\s]{1,12}[:：]\s*')
_POL_LEAD_LABEL_BAR = ('生效', '公布', '决议', '实施', '落地', '执行', '日期',
                       '宣布', '发布', '公告')


def _pol_norm_text(text):
    """日期词元内的空白归一(「9 月 24 日」→「9月24日」;只在时态模型的
    副本上做,R31/R32 规则仍读原文)。"""
    return re.sub(r'(?<=[\d年月日])\s+(?=[年月日\d])', '', text or '')


def _pol_asof_match(ntext):
    """段内显式断言时点「截至 X」(归一文本上的 match;无=None)。"""
    for m in _POL_ASOF_RE.finditer(ntext or ''):
        if any(g for g in m.groups()):
            return m
    return None


def _pol_assert_time(text, as_of, events, ev=None):
    """段内断言时点(ISO 日): 显式「截至 X」> 运行级截止日;均无=None。
    月日无年份形按运行级截止日年份与本事件决议年折算——取不晚于截止日
    的最近一年(无截止日=取决议年);带空格日期先归一。"""
    nt = _pol_norm_text(text)
    m = _pol_asof_match(nt)
    fb = as_of[:10] if isinstance(as_of, str) and len(as_of) >= 10 else None
    if not m:
        return fb
    if m.group(1):
        iso = '%04d-%02d-%02d' % (int(m.group(1)), int(m.group(2)),
                                  int(m.group(3)))
    elif m.group(4):
        iso = '%s-%s-%s' % (m.group(4), m.group(5), m.group(6))
    else:
        mm, dd = int(m.group(7)), int(m.group(8))
        dec = str((ev or {}).get('decision_date') or '')
        years = []
        for y in ((fb or '')[:4], dec[:4]):
            if y and y not in years:
                years.append(y)
        if not years:
            return fb
        cands = []
        for y in years:
            try:
                cands.append(datetime.strptime('%s-%02d-%02d' % (y, mm, dd),
                                               '%Y-%m-%d').date())
            except ValueError:
                pass
        if not cands:
            return fb
        if fb:
            try:
                lim = datetime.strptime(fb, '%Y-%m-%d').date()
            except ValueError:
                lim = None
            past = [c for c in cands if lim is not None and c <= lim]
            if past:
                return max(past).isoformat()
        return max(cands).isoformat()
    try:
        return datetime.strptime(iso, '%Y-%m-%d').date().isoformat()
    except ValueError:
        return fb


def _pol_grp_date(m, base):
    """日期 match 自第 base 组起的 8 组(三个日期形)→ (iso|None, 月, 日);
    无年份形 iso=None。"""
    if m.group(base):
        return ('%04d-%02d-%02d' % (int(m.group(base)), int(m.group(base + 1)),
                                   int(m.group(base + 2))),
                int(m.group(base + 1)), int(m.group(base + 2)))
    if m.group(base + 3):
        return ('%s-%s-%s' % (m.group(base + 3), m.group(base + 4),
                             m.group(base + 5)),
                int(m.group(base + 4)), int(m.group(base + 5)))
    return (None, int(m.group(base + 6)), int(m.group(base + 7)))


def _pol_fold_date(iso, mm, dd, fb, dec, delta=0):
    """(iso|None, 月, 日)→ ISO 日: 无年份形取不晚于运行级截止日的最近一年
    (无截止日=取决议年);非法日期=None;delta=相对偏移日(「X 以前」=-1)。"""
    if iso is None:
        years = []
        for y in ((fb or '')[:4], (dec or '')[:4]):
            if y and y not in years:
                years.append(y)
        if not years:
            return None
        cands = []
        for y in years:
            try:
                cands.append(datetime.strptime('%s-%02d-%02d' % (y, mm, dd),
                                               '%Y-%m-%d').date())
            except ValueError:
                pass
        if not cands:
            return None
        lim = None
        if fb:
            try:
                lim = datetime.strptime(fb[:10], '%Y-%m-%d').date()
            except ValueError:
                lim = None
        past = [c for c in cands if lim is not None and c <= lim]
        d = max(past) if past else max(cands)
    else:
        try:
            d = datetime.strptime(iso[:10], '%Y-%m-%d').date()
        except ValueError:
            return None
    return (d + timedelta(days=delta) if delta else d).isoformat()


_POL_TIME_LABEL = {'asof': '句内', 'win': '区间端', 'local': '分句内',
                   'lead': '句首'}
_POL_OPEN, _POL_CLOSE = '(([【〔[', '))】〕]'
_POL_SEP = frozenset('，,。；;！!？?\n')


def _pol_clause_spans(s):
    """句内分句跨度 [(起, 止)]: 以句内「，,；;」为界;括注(圆/方/粗方/龟甲
    括号)内的逗号不分句——「已决议待生效的调整(目标 x,日期 生效)如期生效」
    是一个分句。"""
    out, depth, st = [], 0, 0
    for i, ch in enumerate(s):
        if ch in _POL_OPEN:
            depth += 1
        elif ch in _POL_CLOSE:
            depth = max(0, depth - 1)
        elif ch in _POL_SEP and depth == 0:
            if i > st:
                out.append((st, i))
            st = i + 1
    if len(s) > st:
        out.append((st, len(s)))
    return out


def _pol_marks_in(c):
    """分句文本 c 内的时点标记 → [(起, 止, kind, 标记原文, (iso|None, 月, 日),
    偏移日)],按起点排序;重叠标记起点靠前者优先、同起点长者优先(「截至 X」
    吞并其内的局部形);区间端只取终点 T 的时间值(修订 r4: 标记跨度=
    区间整体,起点日期一并置「□」——否则带区间的既成句不绑定)。"""
    marks = []
    for m in _POL_ASOF_RE.finditer(c):
        if any(g for g in m.groups()):
            marks.append((m.start(), m.end(), 'asof', m.group(0),
                          _pol_grp_date(m, 1), 0))
    for m in _POL_WIN_RE.finditer(c):
        marks.append((m.start(), m.end(), 'win', m.group(0),
                      _pol_grp_date(m, 9), 0))
    for m in _POL_LOCAL_RE.finditer(c):
        if any(m.group(i) is not None for i in range(1, 9)):
            base = 1
        elif any(m.group(i) is not None for i in range(9, 17)):
            base = 9
        else:
            base = 17
        marks.append((m.start(), m.end(), 'local', m.group(0),
                      _pol_grp_date(m, base),
                      -1 if m.group(0).endswith(('以前', '之前')) else 0))
    marks.sort(key=lambda x: (x[0], -(x[1] - x[0])))
    own, last_end = [], -1
    for mk in marks:
        if mk[0] >= last_end:
            own.append(mk)
            last_end = mk[1]
    return own


def _pol_lead_body(c):
    """句首分句去掉标签前缀后的文本(修订 r5;无合法标签=原文)。"""
    m = _POL_LEAD_LABEL_RE.match(c)
    if not m or any(w in m.group(0) for w in _POL_LEAD_LABEL_BAR):
        return c
    return c[m.end():]


def _pol_time_clauses(ntext, fb, dec):
    """归一文本 → 逐分句时点表 [{'sent','s','e','text','masked','t','src',
    'kind','mark'}]。

    辖域=句(句末标点「。！!?？换行」为界,不跨句): 分句内的时点标记——
    显式「截至/截止/断言时点 X」、区间端「(A..T)」的 T、局部时点「在 X 时 /
    X 时 / X 以前」——取该分句最后一个;无标记的分句继承同句前文分句的
    时点;整句无标记=运行级截止日(kind='run',无截止日则 t=None);
    句首的独立日期分句(「9 月 20 日，…」)=该句的断言时点(kind='lead',
    修订 r4),前面带短标签的同样算(「时态核对: 9 月 20 日，…」;修订 r5)。
    masked=时点标记跨度置「□」后的分句文本(下标不变),供分句旗标与
    日期绑定使用(时点日期不得被读成事件日期/生效日);gov=区间起点日期
    的止位(紧随其后 14 字内的完成态词形仍按被区间支配处理,交日期规则
    核对——修订 r4)。"""
    out = []
    for si, sm in enumerate(_POL_SENT_RE.finditer(ntext or '')):
        ss, se = sm.span()
        cur = None
        for ai, (a, b) in enumerate(_pol_clause_spans(ntext[ss:se])):
            s, e = ss + a, ss + b
            c = ntext[s:e]
            masked = list(c)
            own_time = None
            own = _pol_marks_in(c)
            if not own and ai == 0:
                body = _pol_lead_body(c)
                m0 = _POL_LEAD_DATE_RE.fullmatch(body)
                if m0:
                    g = _pol_grp_date(m0, 1)
                    if _pol_fold_date(g[0], g[1], g[2], fb, dec, 0):
                        own = [(len(c) - len(body), len(c), 'lead', body, g, 0)]
            gov = []
            for mw in _POL_WIN_RE.finditer(c):
                if any(mk[2] == 'win' and mk[0] == mw.start()
                       for mk in own):
                    gov.append(mw.end(3 if mw.group(1) else
                                      6 if mw.group(4) else 8))
            for mk in own:
                for i in range(mk[0], mk[1]):
                    masked[i] = '□'
            if own:
                st, en, kind, mtxt, (iso, mm, dd), delta = own[-1]
                t = _pol_fold_date(iso, mm, dd, fb, dec, delta)
                if t:
                    own_time = (t, '%s「%s」' % (_POL_TIME_LABEL[kind],
                                               mtxt[:40]), kind, mtxt[:40])
            rec = {'sent': si, 's': s, 'e': e, 'text': c,
                   'masked': ''.join(masked), 't': None, 'src': '',
                   'kind': '', 'mark': '', 'gov': gov}
            if own_time:
                cur = own_time
                rec.update(t=cur[0], src=cur[1], kind=cur[2], mark=cur[3])
            elif cur:
                rec.update(t=cur[0], src='同句前文%s' % cur[1], kind=cur[2],
                           mark=cur[3])
            else:
                rec.update(t=fb, src='运行级截止日', kind='run', mark='')
            out.append(rec)
    return out


def _pol_time_spans(ntext):
    """归一文本中全部时点标记跨度 [(起, 止)](供日期规则辨认: 绑定到的日期
    词元若是断言时点/区间端,不得读成正文写出的生效日)。"""
    out = []
    for sm in _POL_SENT_RE.finditer(ntext or ''):
        ss = sm.span()[0]
        for a, b in _pol_clause_spans(ntext[sm.start():sm.end()]):
            for mk in _pol_marks_in(ntext[ss + a:ss + b]):
                out.append((ss + a + mk[0], ss + a + mk[1]))
    return out


def _pol_first_time_src(text, fb=None):
    """段内首个显式「截至 X」标记的来源描述(无标记=运行级截止日)——与
    _pol_assert_time 的取法(首个显式标记)同口径。"""
    m = _pol_asof_match(_pol_norm_text(text))
    if m:
        return '句内「%s」' % m.group(0)[:40]
    return '运行级截止日'


def _pol_impl_kind(ctext, toks, gov=()):
    """分句完成态类型: 'mark'=完成态词形/「已于 X 生效」; 'bare'=既成用法
    的裸「落地/生效/实施/执行」(不支配日期词元); 'raise'=「加息至+目标值」
    既成表述(前 8 字无「决议/决定/宣布/将…」等非完成词); 其余=None(未然形
    「尚未生效/将生效」、标签前置「生效日/生效于 X」、「X生效后/前」、相对
    生效形「自决议次日起生效」、被日期词元支配的「9月24日生效」——后者交
    决议-生效日期规则核对;修订 r4: 区间整体置「□」后,紧随区间起点
    日期 14 字内的词形仍按被区间支配处理——gov=起点止位)。"""
    if any(w in ctext for w in _POL_IMPL_MARKS) or _POL_DONE_AT_RE.search(ctext):
        return 'mark'
    cands = []
    for m in _POL_DONE_VERB_RE.finditer(ctext):
        p = m.start()
        if _POL_NEG_EFF.search(ctext[max(0, p - 4):p]):
            continue
        if _POL_EFF_NEXT.match(ctext, m.end()):
            continue
        if ctext[m.end():m.end() + 1] in ('后', '前', '起'):
            continue
        if (re.search(r'(?:自|从)[^，,]{0,8}(?:起|以后|之后)$',
                      ctext[max(0, p - 12):p])
                or any(rw in ctext[max(0, p - 4):p]
                       for rw in _POL_REL_CUT_WORDS)):
            continue
        tok_end = None
        for iso, mm, dd, st_i, endi in reversed(toks):
            if endi <= p and p <= endi + 14:
                tok_end = endi
                break
        if tok_end is None:
            for g in reversed(gov):   # 区间起点(修订前留作分句内词元)
                if g <= p and p <= g + 14:
                    tok_end = g
                    break
        # 本词之前 14 字内无日期词元,或最近的日期词元已被更早的一个完成态
        # 词支配(「9月24日生效的加息落地」: 生效绑日期,落地=裸既成用法)
        unbound = tok_end is None or any(
            tok_end <= cands[j][0] and cands[j][1] <= p
            for j in range(len(cands)))
        cands.append((m.start(), m.end()))
        if unbound:
            return 'bare'
    m = _POL_RAISE_TO_RE.search(ctext)
    if m and not any(w in ctext[max(0, m.start() - 8):m.start()]
                     for w in _POL_NONCOMPL_PRE):
        return 'raise'
    return None


def _pol_tok_is(t, d):
    """日期词元是否为日期 d(无年份形只比月日)。"""
    if not d:
        return False
    return (t[0] == d) if t[0] else (
        (t[1], t[2]) == (int(d[5:7]), int(d[8:10])))


def _pol_clause_flags(ctext, ev, cands=None, gov=()):
    """分句状态旗标(事件日期/目标值/完成态/未然/现行/预期/指代;输入=
    时点标记已置「□」的分句文本——时点日期不得被读成事件日期;gov=区间
    起点日期在分句内的止位)。

    修订 r4: tv 兼认中数词目标值;pend_status=把决定写成未实施的词形(尚未/
    未/待/即将+生效类动词、将然形、方向可定时的「尚未加息」)——宽口径 pend
    只作豁免;dec=「已决议/决议加息/公布…决议」既成句形;level=政策利率名词
    +系词;other_time/other_ev=指向别的时间或别的事件;after_ref=「生效后」
    类条件参照;post_ref=「决议后」类叙述参照。"""
    dec = str(ev.get('decision_date') or '')
    eff = str(ev.get('effective_on') or '')
    toks = _pol_date_tokens(ctext)
    tv = ev.get('target_value')
    ent = ev.get('entity')
    own_w = _POL_ENTITY_WORDS.get(ent, ()) if ent else ()
    other_w = tuple(w for k, ws in _POL_ENTITY_WORDS.items()
                    if k != ent for w in ws)
    try:
        tvf = float(tv) if tv is not None else None
    except (TypeError, ValueError):
        tvf = None
    act = _POL_ACT_PEND_RE.search(ctext)
    pm = _pol_pend_marks(ctext)
    ev_hit = any(_pol_tok_is(t, dec) or _pol_tok_is(t, eff) for t in toks)
    ev_year, ev_months = dec[:4], set()
    if dec and eff:
        try:
            ev_months = {int(dec[5:7]), int(eff[5:7])}
        except ValueError:
            ev_months = set()
    other_time = any((y and y != ev_year) or int(mo) not in ev_months
                     for y, mo in _POL_YM_RE.findall(ctext))
    return {
        'text': ctext[:60],
        'toks': toks,
        'dated': bool(toks),
        'ev_dated': ev_hit,
        'other_dated': any(not _pol_tok_is(t, dec) and not _pol_tok_is(t, eff)
                           for t in toks),
        'tv': (tvf is not None
               and (_pol_value_in_text(tv, ctext)
                    or any(abs(v - tvf) < 1e-6
                           for v in _pol_cn_values(ctext)))),
        'impl': _pol_impl_kind(ctext, toks, gov),
        'pend': ((any(w in ctext for w in _POL_NOT_YET_MARKS)
                  or bool(_POL_PEND_RE.search(ctext)))
                 and not _POL_NOT_YET_NEG.search(ctext)),
        'pend_neg': (any(x[2] for x in pm)
                     and not _POL_NOT_YET_NEG.search(ctext)),
        'pend_status': (((pm
                          and (any(_POL_PEND_SUBJ_RE.search(ctext[:x[0]])
                                  for x in pm)
                               or ev_hit
                               or bool(_POL_ANAPHOR_RE.search(ctext)))
                          and not any(w in ctext
                                      for w in _POL_PEND_SUBJ_GUARD))
                         or (bool(act)
                             and _pol_dir(ev, cands or [])
                             == _POL_ACT_DIR.get(act.group(1))))
                        and not _POL_NOT_YET_NEG.search(ctext)),
        'dec': bool(_POL_DEC_DONE_RE.search(ctext)),
        'dec_dated': any(_pol_tok_is(t, dec) for t in toks),
        'eff_dated': any(_pol_tok_is(t, eff) for t in toks),
        'eff_start': (any(_pol_tok_is(t, eff) for t in toks)
                      and (any(w in ctext for w in _POL_EFF_VERBS)
                           or bool(_POL_DATE_START_RE.search(ctext)))),
        'level': _pol_level_stmt(ctext),
        'level_val': (_pol_level_stmt(ctext)
                      and _pol_level_val(ctext, tvf)),
        'tva': (tvf is not None and _pol_value_in_text(tv, ctext)),
        'other_time': (other_time
                       or any(m.group(1) != ev_year
                              for m in _POL_YEAR_RE.finditer(ctext))),
        'other_ev': bool(_POL_OTHER_EV_RE.search(ctext)),
        'after_ref': any(w in ctext for w in _POL_AFTER_REF_MARKS),
        'post_ref': any(w in ctext for w in _POL_POST_REF_MARKS),
        'expect': any(w in ctext for w in _POL_EXPECT_MARKS),
        'past': any(w in ctext for w in _POL_PAST_CTX_MARKS),
        'pol': any(w in ctext for w in _POL_POL_CHANGE_WORDS),
        'own_ent': any(w in ctext for w in own_w),
        'other_ent': any(w in ctext for w in other_w),
        'meeting': any(w in ctext for w in _POL_MEETING_WORDS),
        'cur': ('生效后' not in ctext
                and any(w in ctext for w in _POL_CUR_CLAUSE_MARKS)),
        'anaphor': bool(_POL_ANAPHOR_RE.search(ctext)),
    }


def _pol_ev_key(e):
    return (str(e.get('first_publish') or e.get('decision_date') or ''),
            str(e.get('effective_on') or ''))


def _pol_ev_named(c, e):
    """分句是否以日期提及事件 e(决议日或生效日的任一词形)。"""
    return any(_pol_tok_is(t, str(e.get('decision_date') or ''))
               or _pol_tok_is(t, str(e.get('effective_on') or ''))
               for t in c['toks'])


def _pol_model(nt, ev, as_of, events, bound=None):
    """归一文本 nt 的逐分句时态模型 → (cands, by_sent): cands=段内候选政策
    事件(段提本实体→同实体事件,否则=全部); by_sent=句号→[(分句时点记录,
    分句旗标)];旗标带段内事件提及轨迹注记 last_named(各分句之前、同段内
    最近被以日期提及的候选事件,跨句累计;未提及任何候选的带日期分句不改写
    轨迹;提及两个以上='ambig')。"""
    dec = str(ev.get('decision_date') or '')
    fb = as_of[:10] if isinstance(as_of, str) and len(as_of) >= 10 else None
    tcs = _pol_time_clauses(nt, fb, dec)
    ent = ev.get('entity')
    own = bool(ent) and any(
        w in nt for w in _POL_ENTITY_WORDS.get(ent, ()))
    pool = list(bound if bound is not None else (events or []))
    # 段级旗标只作消歧辅助(MINOR-3): 段提本实体→候选=同实体事件
    cands = ([e for e in pool if e.get('entity') == ent] if own else pool)
    by_sent = {}
    for tc in tcs:
        by_sent.setdefault(tc['sent'], []).append(
            (tc, _pol_clause_flags(tc['masked'], ev, cands, tc.get('gov'))))
    # 指代的先行词可在同段前一句(「…12-04 生效。截至 11-30 该决议已经实施」)
    last_named = None
    for si in sorted(by_sent):
        for tc, c in by_sent[si]:
            c['last_named'] = last_named
            if c['dated']:
                hit = [e for e in cands if _pol_ev_named(c, e)]
                if hit:
                    last_named = hit[0] if len(hit) == 1 else 'ambig'
    return cands, by_sent


def _pol_pend_c(cands, t):
    """断言时点 t 时待生效(已公告、未生效)的候选事件。"""
    if not t:
        return []
    return [e for e in cands
            if _pol_ev_key(e)[0] <= t < _pol_ev_key(e)[1]]


def _pol_anaph(c, ev, cands, pend_c, t):
    """指代分句「该决议/该加息」是否指本事件: 本分句以日期提及事件=归属由
    日期定→否; 段内提了别家实体而未提本实体→否。段内前文(可跨句)以日期
    提及过候选事件→指代归最近提及者(其后才出现的决定不夺走指代;歧义→
    不绑); 否则:
    候选唯一,或断言时点待生效的候选唯一=本事件且别无当时已生效的候选,
    或无待生效候选且本事件=生效最晚者。"""
    if (not c['anaphor'] or c['ev_dated']
            or (c['other_ent'] and not c['own_ent'])):
        return False
    last = c['last_named']
    if last == 'ambig':
        return False
    if last is not None:
        return last is ev
    if len(cands) == 1:
        return True
    if (len(pend_c) == 1 and pend_c[0] is ev
            and not any(e is not ev and _pol_ev_key(e)[1] <= t
                        for e in cands)):
        return True
    return (not pend_c and bool(cands)
            and max(cands, key=_pol_ev_key) is ev)


def _pol_pool(c, ev, cands):
    """状态断言分句的候选事件池(修订 r4): 分句提了别家实体而未提本实体→空;
    提本实体→同实体事件;未提实体→段内候选全集。"""
    if c['other_ent'] and not c['own_ent']:
        return []
    if c['own_ent']:
        ent = ev.get('entity')
        return [e for e in cands if e.get('entity') == ent]
    return list(cands)


def _pol_foreign(c):
    """分句指向别的时间(事件月分/年份之外的月分、年份)或别的事件(下一次/
    后续…)——无事件日期的状态断言不归属本事件。"""
    return bool(c['other_dated'] or c['other_time'] or c['other_ev'])


def _pol_other_named(c, ev, cands, fl):
    """同句另有分句以日期提及别的候选事件,或段内前文最近以日期提及的不是
    本事件——无事件日期的状态分句不归本事件(指代归那个被提及的事件)。"""
    if c.get('last_named') not in (None, ev):
        return True
    return any(f is not c
               and any(e is not ev and _pol_ev_named(f, e) for e in cands)
               for f in fl)


def _pol_rel(c, tc, ev, cands, fl):
    """无事件日期、无指代的状态断言分句是否归属事件 ev(修订 r4): 分句不指向
    别的时间/别的事件,同句/段内前文未以日期提及别的事件;池=按分句实体缩过
    的候选;池内实体不唯一且分句未提实体→不绑;按断言时点 t 取「在办」事件,
    须恰为本事件——
    t<公告日: 公告日晚于 t 的最早一件,且池内无 t 时待生效者;
    公告日≤t<生效日: t 时待生效者恰为本事件(另有当时已生效的决定时,只有
    写本事件目标水平且与已生效最新一件不同的陈述才归属——其余指代不明);
    t≥生效日: t 时已知的最新一件。"""
    t = tc['t']
    if not t or _pol_foreign(c) or _pol_other_named(c, ev, cands, fl):
        return False
    pool = _pol_pool(c, ev, cands)
    if (not pool or (not c['own_ent']
                     and len({e.get('entity') for e in pool}) > 1)):
        return False
    key = _pol_ev_key
    if t < key(ev)[0]:
        up = [e for e in pool if key(e)[0] > t]
        return (bool(up) and min(up, key=key) is ev
                and not any(key(e)[0] <= t < key(e)[1] for e in pool))
    known = [e for e in pool if key(e)[0] <= t]
    if t < key(ev)[1]:
        pend = [e for e in known if t < key(e)[1]]
        if not (len(pend) == 1 and pend[0] is ev):
            return False
        eff_o = [e for e in known if e is not ev and key(e)[1] <= t]
        if not eff_o or not c['level_val']:
            return not eff_o
        try:
            return (abs(float(max(eff_o, key=key).get('target_value'))
                        - float(ev.get('target_value'))) > 1e-9)
        except (TypeError, ValueError):
            return True
    return bool(known) and max(known, key=key) is ev


def _pol_narrated(c, fl, ci):
    """叙述性将来(修订 r4): 本分句带事件生效日、为将然形(非「尚未/待/即将」
    未然),且同句前文分句以「决议加息」既成句形写本事件并带决议日——「X 日
    决议加息,将于 Y 日生效」是对决定的叙述,不是把已生效的决定写成待生效。"""
    if not c['ev_dated'] or c['pend_neg'] or not c['pend_status']:
        return False
    return any(f['dec'] and f['dec_dated'] for f in fl[:ci])


def _pol_early_bind(c, tc, ev, cands, by_sent):
    """公告后、生效前: 分句的既成口径断言是否指向事件 ev(事件日期在场/
    指代归属/无日期分句且断言时点待生效的候选唯一=本事件——修订 r4: 候选
    池按分句实体缩过,指向别的时间/别的事件的无日期分句不绑)。"""
    t = tc['t']
    pool = _pol_pool(c, ev, cands)
    pend_c = _pol_pend_c(pool, t)
    fl = [x for _, x in by_sent.get(tc['sent'], [])]
    ev_pending_named = any(f['pend'] and f['ev_dated'] for f in fl)
    undated = (not c['dated'] and not c['other_ent'] and not _pol_foreign(c)
               and len(pend_c) == 1 and pend_c[0] is ev
               and not any(e is not ev and _pol_ev_key(e)[1] <= t
                           for e in pool)
               and not ev_pending_named)
    return (c['ev_dated'] or _pol_anaph(c, ev, cands, _pol_pend_c(cands, t), t)
            or undated)


def _pol_tense_violation(text, ev, as_of, events, bound=None):
    """政策时态核验(事件 × 断言时点 × 实施状态)→ (code, detail) | None。
    辖域=句(句末标点「。！!?？换行」为界); 断言时点逐分句取(分句内标记,
    句首的独立日期分句(可带短标签),无则继承同句前文,再无则运行级截止日——
    见 _pol_time_clauses),同句多个断言时点各自生效; 详情注明断言时点的来源。

    修订 r4: 状态断言的归属=事件日期/指代/在办事件(_pol_rel)三路之一;
    目标水平陈述与中数词目标值按现行口径核验;公告前「已决议」既成句形、
    生效后实施状态未然句(含方向可定的动作词)拦截;叙述性将来豁免。

    修订 r5: 正文写出的生效日与官方实录不符时由日期规则先报(调用方以
    _pol_date_mismatch 判断),本模型的发现不顶替 POL-EFF-DATE。"""
    dec = str(ev.get('decision_date') or ''); eff = str(ev.get('effective_on') or '')
    if not (dec and eff):
        return None
    nt = _pol_norm_text(text)
    cands, by_sent = _pol_model(nt, ev, as_of, events, bound)
    if not any(tc['t'] for cls in by_sent.values() for tc, _ in cls):
        return None
    pub = str(ev.get('first_publish') or dec)
    ent = ev.get('entity')
    own = bool(ent) and any(w in nt for w in _POL_ENTITY_WORDS.get(ent, ()))
    name = '%s(%s 公布,%s 生效)' % (ev.get('metric_id'), pub, eff)
    seg_ev = any(c['ev_dated'] for cls in by_sent.values() for _, c in cls)
    # R32 既判「当前值」形(段内无事件日期词形、无任何待生效/将然标注,本实体
    # 词,段首断言时点早于生效日): 违规码留给 R32 既判规则(PENDING-AS-CURRENT),
    # R32 裁决不变
    _r32_t = _pol_assert_time(text, as_of, events, ev)
    r32_txt = (own and _r32_t is not None and _r32_t < eff
               and not any(m in text or m in nt for m in _POL_PENDING_MARKS)
               and not any(f in text or f in nt
                           for d in (dec, eff) for f in _date_word_forms(d))
               and any(w in text for w in _POL_EFF_WORDS))
    for si in sorted(by_sent):
        cls = by_sent[si]
        fl = [c for _, c in cls]
        sent_ev = any(c['ev_dated'] for c in fl)
        for ci, (tc, c) in enumerate(cls):
            t = tc['t']
            if not t:
                continue
            named = (c['ev_dated']
                     or _pol_anaph(c, ev, cands, _pol_pend_c(cands, t), t))
            rel = ((not named) and not _pol_foreign(c)
                   and _pol_rel(c, tc, ev, cands, fl))
            # 决定内容续写(「X 日决议，政策利率升至 x」)且无显式断言时点=说的
            # 是决定,不是现行口径
            decided = (tc['kind'] == 'run'
                       and any(f['dec'] and f['dec_dated'] for f in fl[:ci]))
            # 决议-生效成对在场的决定内容续写(修订 r5): 同句前文以决议日提及
            # 本事件、句内写出官方生效日,水平分句不带现行时间词——「X 日决议，
            # Y 日生效，政策利率升至 x」说的是决定内容(既成口径分句另走
            # impl 一路,照旧拦)
            paired = (tc['kind'] == 'run' and not c['cur']
                      and any(f['dec_dated'] and (f['dec'] or f['pol'])
                              for f in fl[:ci])
                      and any(f['eff_start'] for f in fl))
            # 现行口径(现行词形,或政策利率名词+系词)写事件目标值/事件日期;
            # 无事件日期的水平陈述须归属(指代/在办事件),且目标值不带比较语境
            cur_level = (not c['pend'] and not c['expect'] and not c['after_ref']
                         and (((c['tv'] or c['ev_dated']) and c['cur']
                               and (c['ev_dated'] or sent_ev
                                    or (seg_ev and c['own_ent'])))
                              or (c['level_val']
                                  and not (r32_txt and c['cur'] and c['tva'])
                                  and not decided
                                  and (c['ev_dated'] or sent_ev
                                       or (seg_ev and c['own_ent'])
                                       or named or rel))))
            early_cur = ('POL-EFF-EARLY-CLAIM',
                         '断言时点 %s(来源: %s)早于 %s 决议生效日 %s,正文以'
                         '现行/已生效口径写目标值「%s」而无未然标注——断言时点'
                         '尚未生效' % (t, tc['src'], name, eff, tc['text'][:60]))
            if t < pub:
                known_form = (c['ev_dated'] and not c['expect'] and not c['pend']
                              and not c['past'] and not c['meeting']
                              and (c['pol'] or c['impl'] or c['tv']))
                dec_form = (c['dec'] and not c['ev_dated'] and (named or rel)
                            and not c['post_ref'] and not c['expect']
                            and not c['pend'] and not c['past']
                            and not c['meeting'])
                pend_form = (c['ev_dated'] and c['pend_status']
                             and not c['expect'] and not c['past']
                             and not c['meeting'] and not c['post_ref'])
                if known_form or dec_form or pend_form:
                    return ('POL-EFF-DECISION-NOT-YET-KNOWN',
                            '断言时点 %s(来源: %s)早于 %s 决议公告日 %s,正文以'
                            '既成事实提及「%s」——当时无从得知,须以预期/定价'
                            '口径书写或标明事后信息'
                            % (t, tc['src'], name, pub, tc['text'][:60]))
                if cur_level and not c['ev_dated']:
                    return early_cur       # 公告前即以现行口径写目标水平
                continue
            if t >= eff:
                if (c['pend_status'] and not c['expect'] and not c['past']
                        and (named or (c['tv'] and own) or rel)
                        and not _pol_narrated(c, fl, ci)):
                    return ('POL-EFF-LATE-PENDING',
                            '断言时点 %s(来源: %s)不早于 %s 决议生效日 %s,正文'
                            '仍写「%s」——该决议在断言时点已经生效,不得写成'
                            '待生效'
                            % (t, tc['src'], name, eff, tc['text'][:60]))
                continue
            if (c['impl'] and not c['pend'] and not c['expect']
                    and _pol_early_bind(c, tc, ev, cands, by_sent)):
                if tc['kind'] == 'win':
                    lead = ('区间端 %s 为断言时点(「%s」),早于 %s 决议官方生效日'
                            ' %s——正文以已实施口径写「%s」而无未然标注: 断言时点'
                            '尚未生效(该日期是回看区间的端点,不是正文写出的生效日)'
                            % (t, tc['mark'], name, eff, tc['text'][:60]))
                else:
                    lead = ('断言时点 %s(来源: %s)早于 %s 决议生效日 %s,正文以'
                            '已实施口径写「%s」而无未然标注——断言时点尚未生效'
                            % (t, tc['src'], name, eff, tc['text'][:60]))
                return ('POL-EFF-EARLY-CLAIM', lead)
            if cur_level and not paired:
                return early_cur
    return None


def _pol_date_mismatch(text, ev, bound, as_of=None, t_assert=None):
    """正文写出的生效日与本事件官方实录不符(决议日/生效日之外、早于或晚于
    官方生效日;日期规则 POL-EFF-DATE 的实质规格;区间端/句内断言时点按断言
    时点措辞的那类、把决议日写成生效日的那类不算)→规格列表,否则 []。

    修订 r5: (1) 段内提了官方日期(决议日/生效日任一词形)=原口径; (2) 段内
    未提官方日期,但以「X 日生效」写出了不符的生效日,且断言时点不早于公告日
    (决定已可知)——同样核对: 此前这类句两条规则都不管(「9 月 22 日生效的
    加息已经实施」在 9 月 20 日被放行)。公告在研究时点尚不可见的决议不核
    (当时无从写对;公告前既成句形由时态模型另拦)。

    只认两类规格: 「正文生效日 X 与官方实录不符(早于…)」「正文生效日 X 晚于
    官方实录生效日」。另两类不算——区间端/句内断言时点不是写出的生效日;
    「正文把决议日写成生效日」多出自完成态分句(「X 日决议已生效」),那时
    早声称才是与句义相符的码(修订 r3 独立审查 MAJOR-6 的原则),由时态模型
    先报;时态模型未命中的非完成态形(「生效的决议」)照旧走日期规则。"""
    pub = str(ev.get('first_publish') or ev.get('decision_date') or '')
    if as_of and pub and pub > as_of:
        return []
    nt = _pol_norm_text(text)
    named = any(f in text or f in nt
                for d in (ev['decision_date'], ev['effective_on'])
                for f in _date_word_forms(d))
    if not named and not (t_assert and pub and t_assert >= pub):
        return []
    return [d for d in _pol_date_specs(nt, ev, bound, as_of)
            if d.startswith('正文生效日 ')]


def _pol_claim_binds(work, p, ev, bound, as_of=None):
    """位置 p 处的「生效」若身处既成口径断言分句(完成态词形或指代形),
    返回该断言是否指向事件 ev(True/False); 非完成态(标签/修饰形,如「生效
    的决议」)返回 None——交日期规则按词元核对。"""
    cands, by_sent = _pol_model(work, ev, as_of, None, bound)
    for cls in by_sent.values():
        for tc, c in cls:
            if tc['s'] <= p < tc['e']:
                if not c['impl'] and not c['anaphor']:
                    return None
                return bool(_pol_early_bind(c, tc, ev, cands, by_sent))
    return None


# Audit-R33 任务3(任务2补充): 完成态状态断言「(A..T)…已生效」的区间端识别
_POL_RANGE_END_PRE = re.compile(r'(?:\.\.|…|~|～|—|–|--|至|到)\s*$')
_POL_RANGE_END_POST = re.compile(r'\s{0,3}[)）内以止末期]')


def _pol_state_window_ok(text, p, st_i, endi, tok, ev, bound):
    """「生效」前带「已/已经」、其绑定日期词元是区间端 T(前紧邻区间连接词、
    后紧邻收口字)、T 又不是本事件的决议日/生效日,且段内另提了同实体、在 T
    当日已生效的决定→该句是与实录相符的状态断言,不是「本事件于 T 生效」。
    (指代「该决议」无法确定性消解: 带事件日期的提前生效断言另由时态模型
    拦截,不走本豁免。)"""
    if not (text[p - 1:p] == '已' or text[p - 2:p] == '已经'):
        return False
    if tok in (ev.get('decision_date'), ev.get('effective_on')):
        return False
    if not (_POL_RANGE_END_PRE.search(text[max(0, st_i - 6):st_i])
            and _POL_RANGE_END_POST.match(text, endi)):
        return False
    for e2 in bound:
        if e2 is ev or e2.get('entity') != ev.get('entity'):
            continue
        eff2 = str(e2.get('effective_on') or '')
        if not eff2 or eff2 > tok:
            continue
        if (any(f in text for f in _date_word_forms(e2['decision_date']))
                or any(f in text for f in _date_word_forms(eff2))):
            return True
    return False


def _pol_date_specs(work, ev, bound, as_of=None):
    """POL-EFF-DATE 规格 → [detail](work=原文或空白归一副本)。R32 绑定逻辑
    原样: 标签前置「生效日/生效于 Y」→其后日期 Y;其余(日期前置 X生效)→
    其前 ≤14 字、无相对词的最近日期词元。

    修订 r3(独立审查 MAJOR-4/MAJOR-6): (1) 调用方传空白归一副本——带空格
    的中文日期(「9 月 22 日生效」)同样成词元,生效日写错不再因空格漏核;
    (2) 绑定到的日期词元若是区间端或句内断言时点,按「断言时点」措辞
    (这些句子没有把任何日期写成生效日),不写「正文生效日」;其中既成口径
    断言(完成态词形/指代形)的归属由时态模型定——指向别的事件(如句内更早
    以日期提及的决定)则不是本事件提前生效;(3) 正文
    生效日晚于官方实录、且其前紧邻本事件决议日(同句 ≤40 字)=与官方实录
    不符(此前只拦「早于」)。"""
    _ddec, _deff = ev['decision_date'], ev['effective_on']
    lag = _pol_days(_ddec, _deff)
    spec = []
    _toks = _pol_date_tokens(work)
    _start_ix = {t[3]: _i for _i, t in enumerate(_toks)}
    _tspans = _pol_time_spans(work)
    _ent = ev.get('entity')
    _own = (not _ent) or any(
        w in work for w in _POL_ENTITY_WORDS.get(_ent, ()))
    for _m in re.finditer('生效', work):
        _p = _m.start()
        # 未然/否定形的「生效」(尚未生效/未生效/待生效/即将生效/将生效/
        # 不会生效)不是生效日标签
        if _POL_NEG_EFF.search(work[max(0, _p - 4):_p]):
            continue
        _gi = None
        _nx = _POL_EFF_NEXT.match(work, _p + 2)
        if _nx:
            _gi = _start_ix.get(_nx.end())
        if _gi is None:
            for _i in range(len(_toks) - 1, -1, -1):
                iso, mm, dd, st_i, endi = _toks[_i]
                _nxt = (_toks[_i + 1][3] if _i + 1 < len(_toks)
                        else len(work))
                if not (endi <= _p and _p + 2 <= min(_nxt, endi + 14)):
                    continue
                if any(rw in work[endi:_p] for rw in _POL_REL_CUT_WORDS):
                    break     # 相对生效词形另由 REL 判
                _gi = _i
                break
        if _gi is None:
            continue
        iso, mm, dd, st_i, endi = _toks[_gi]
        tok = iso or '%s-%02d-%02d' % (_ddec[:4], mm, dd)
        if tok == _deff or tok == _ddec and _deff == _ddec:
            continue
        # 「(A..T)…已生效」状态断言(同实体另一决定在 T 已生效且段内被
        # 提及)不读成本事件于 T 提前生效(见 _pol_state_window_ok)
        if _pol_state_window_ok(work, _p, st_i, endi, tok, ev, bound):
            continue
        _rng = bool(_POL_RANGE_END_PRE.search(work[max(0, st_i - 6):st_i])
                    and _POL_RANGE_END_POST.match(work, endi))
        _tmk = any(s <= st_i and endi <= e for s, e in _tspans)
        if (_rng or _tmk) and _ddec <= tok < _deff:
            if _pol_claim_binds(work, _p, ev, bound, as_of) is False:
                continue
            spec.append(
                '%s %s 为断言时点,早于 %s 决议官方生效日 %s——断言时点尚未'
                '生效,不得写成已生效'
                % ('区间端' if _rng else '句内断言时点', tok, ev['metric_id'],
                   _deff))
        elif tok == _ddec:
            spec.append(
                '正文把 %s 决议日 %s 写成生效日——官方实录生效日为 %s'
                '(决议→生效 %s 天),不得提前'
                % (ev['metric_id'], _ddec, _deff, lag))
        elif _ddec <= tok < _deff:
            spec.append(
                '正文生效日 %s 与官方实录不符(早于官方生效日 %s;决议日 %s)'
                '——%s 决议 %s 生效,不得提前'
                % (tok, _deff, _ddec, ev['metric_id'], _deff))
        elif (tok > _deff and not _rng and not _tmk and _ent and _own
              and _gi > 0):
            pis, pmm, pdd, pst_i, pend_ = _toks[_gi - 1]
            prev_dec = ((pis == _ddec) if pis else
                        ((pmm, pdd) == (int(_ddec[5:7]), int(_ddec[8:10]))))
            if (prev_dec and pend_ <= _p and _p - pend_ <= 40
                    and not re.search(r'[。！!？?]', work[pend_:_p])):
                spec.append(
                    '正文生效日 %s 晚于官方实录生效日 %s(决议日 %s)——%s 决议 '
                    '%s 生效,不得改写'
                    % (tok, _deff, _ddec, ev['metric_id'], _deff))
    return spec


def _attach_code_state(root):
    """挂接步骤的代码版本(Audit-R33 任务2 MINOR-4): 沿用运行档的取码
    helper(research_orchestrator._git_state: 运行树/代码树的 git HEAD、
    差异指纹、CODE_VERSION.json 印章),随 attach 元数据(运行目录)与返回值
    (CLI 回执)落档;取不到=None(如实缺席,不猜)。"""
    try:
        import research_orchestrator as _ro
        head, source, diff_sha = _ro._git_state(root)
        return {'code_git_head': head, 'code_git_head_source': source,
                'code_git_diff_sha256': diff_sha}
    except Exception:                       # 取不到=如实缺席
        return {'code_git_head': None, 'code_git_head_source': None,
                'code_git_diff_sha256': None}


def _judgment_text_segments(judgment, identifiers=frozenset()):
    """判断文档内全部自然语言段(逐条带定位),POL-EFF 子串代理消费。

    Audit-R33 任务3: identifiers=本报告证据索引引用集合——逐字等于
    其中一项的字符串是证据标识符而非叙述(REF 规则已逐条解析),不
    入叙述段: 日历实录行标识符内嵌决议日(…@2026-09-18),按叙述
    整段扫描会把「引用官方实录」误报成「提及决议日未配生效日」。
    其余字符串(含不解析的悬空引用,由 REF 规则拒)照扫,零放宽。"""
    segs = []

    def _walk(node, where):
        if isinstance(node, str):
            if node.strip() and node not in identifiers:
                segs.append((where, node))
        elif isinstance(node, dict):
            for k, v in node.items():
                _walk(v, f'{where}.{k}' if where else str(k))
        elif isinstance(node, list):
            for i, v in enumerate(node):
                _walk(v, f'{where}[{i}]')

    for top in ('l3', 'l4', 'reader_map'):
        _walk((judgment or {}).get(top), top)
    return segs


def validate_judgment(judgment, evidence_refs, metric_ids,
                      policy_events=None, as_of=None):
    """纪律结构校验(内容零改写零生成)。

    judgment: Agent 提交的 dict(schema v1.1);evidence_refs: 本报告证据索引
    ref 集合(set);metric_ids: 注册表在册 metric_id 集合(set)。
    policy_events(Audit-R31 任务3,可选): collect_policy_events() 的决议
    事件面——在场时启用 POL-EFF 决议-生效成对纪律;缺席=None 不启用
    (既有调用方零回归)。
    as_of(Audit-R32 任务2,可选): 断言时点=研究截止日(ISO)——在场时
    启用时点类规则(POL-EFF-EARLY-CLAIM / PENDING-AS-CURRENT: 截止日早于
    生效日而正文以现行口径断言);实体绑定与生效日核对(POL-EFF-DATE/
    REL)不依赖时点。None=仅 R31 成对纪律+实体绑定。
    Audit-R33 任务2: 段内显式「截至 X」=该段断言时点(优先于 as_of),
    政策时态按 事件×断言时点×实施状态 逐分句核验(_pol_tense_violation)。
    返回 {'passed', 'violations': [(code, where, detail)], 'n_*'}。
    """
    v = []

    def bad(code, where, detail=''):
        v.append({'code': code, 'where': where, 'detail': detail})

    ev = set(evidence_refs or ())
    mids = set(metric_ids or ())

    # ── 结构与归因 ──────────────────────────────────────────────
    if not isinstance(judgment, dict):
        return {'passed': False,
                'violations': [{'code': 'SCHEMA', 'where': 'root',
                                'detail': 'judgment 非 object'}],
                'n_contradictions': 0, 'n_mechanism_chains': 0,
                'n_scenarios': 0}
    if judgment.get('schema_version') != JUDGMENT_SCHEMA_VERSION:
        bad('SCHEMA', 'schema_version',
            f"须为 {JUDGMENT_SCHEMA_VERSION}(得 {judgment.get('schema_version')!r})")
    decl = judgment.get('agent_declaration') or {}
    if decl.get('attribution') != 'ai_inferred':
        bad('ATTR', 'agent_declaration.attribution',
            f"须 ai_inferred(得 {decl.get('attribution')!r})——Agent 成果"
            '永不得标 institution_stated(机构明示面归 views 库)')

    def refs_ok(where, refs):
        """evidence_refs 逐条解析;返回是否全解析。"""
        ok = True
        for r in (refs or []):
            if r not in ev:
                bad('REF', where, f'悬空证据引用 {r!r}(不在本报告证据索引)')
                ok = False
        return ok

    # ── L3 矛盾综合(纪律 4: 四层标注+竞争性解释并列) ──────────────
    l3 = judgment.get('l3') or {}
    contras = l3.get('contradictions') or []
    if not contras:
        bad('SCHEMA', 'l3.contradictions',
            'L3 须至少 1 条矛盾/综合陈述(无判断内容=无可落位)')
    for c in contras:
        cid = c.get('id') or '?'
        if not (c.get('statement') or '').strip():
            bad('SCHEMA', f'l3.contradictions[{cid}].statement', '陈述为空')
        exps = c.get('competing_explanations') or []
        if len(exps) < 2:
            bad('CON-EXP', f'l3.contradictions[{cid}].competing_explanations',
                f'竞争性解释须 >=2 并列(得 {len(exps)};纪律 4: 数据同样'
                '容纳的其他解释至少列一种)')
        # R23 审计 MINOR-1: 零引用矛盾不再静默放行——须 >=1 可解析引用,
        # 或显式声明免锚理由(no_anchor_reason 非空;渲染面随之披露)
        if not (c.get('evidence_refs') or []):
            if not (c.get('no_anchor_reason') or '').strip():
                bad('CON-REF', f'l3.contradictions[{cid}].evidence_refs',
                    '矛盾陈述须 >=1 可解析证据引用,或以 no_anchor_reason '
                    '非空明示免锚(静默零锚=割裂结论-证据绑定)')
        refs_ok(f'l3.contradictions[{cid}].evidence_refs',
                c.get('evidence_refs'))

    # ── L3 机制链(纪律 15: E1/E2/E3) ────────────────────────────
    chains = l3.get('mechanism_chains') or []
    for ch in chains:
        chid = ch.get('id') or '?'
        links = ch.get('links') or []
        if not links:
            bad('SCHEMA', f'l3.mechanism_chains[{chid}].links', '机制链空')
        for lk in links:
            lid = f'{chid}.link{lk.get("step", "?")}'
            # Audit-R18 任务4反例①: 机制正文为空或 None 曾静默放行(链非空
            # 但环 text 空=读者面空机制)——结构在场≠内容在场,一律拦。
            if not str(lk.get('text') or '').strip():
                bad('SCHEMA', f'l3.mechanism_chains[{lid}].text',
                    '机制环正文为空或 None——空正文不得落位交付/归档')
            lvl = lk.get('evidence_level')
            if lvl not in ('E1', 'E2', 'E3'):
                bad('SCHEMA', f'l3…[{lid}].evidence_level',
                    f'须 E1/E2/E3(得 {lvl!r})')
                continue
            if lvl == 'E1':
                refs = lk.get('evidence_refs') or []
                if not refs or not refs_ok(
                        f'l3.mechanism_chains[{lid}].evidence_refs', refs):
                    bad('E1-REF', f'l3.mechanism_chains[{lid}]',
                        'E1 环(引擎直接可验证)须带 >=1 可解析证据引用')
            elif lvl == 'E2':
                note = lk.get('missing_link_note') or ''
                if ASSUMPTION_MARK not in note:
                    bad('E2-ASSUM', f'l3.mechanism_chains[{lid}]',
                        'E2 环须明写缺失环【假设】(missing_link_note 含"假设")')
                refs_ok(f'l3.mechanism_chains[{lid}].evidence_refs',
                        lk.get('evidence_refs'))
            else:  # E3
                fm = lk.get('falsification_metric')
                if fm not in mids:
                    bad('E3-FALS', f'l3.mechanism_chains[{lid}]',
                        f'E3 环须给注册表在册证伪指标(得 {fm!r})')

    # ── L4 条件情景(纪律 16: 五行强制+并列) ──────────────────────
    l4 = judgment.get('l4') or {}
    scenarios = l4.get('scenarios') or []
    if len(scenarios) < 2:
        bad('SCN-PLURAL', 'l4.scenarios',
            f'须 >=2 情景并列(基准+反例;得 {len(scenarios)};单一情景'
            '不得单独呈现)')
    for s in scenarios:
        sid = s.get('id') or '?'
        rows = s.get('rows') or {}
        for rname in SCENARIO_ROWS:
            if not rows.get(rname):
                bad('SCN-FIVE', f'l4.scenarios[{sid}].rows.{rname}',
                    '五行缺一不可(纪律 16)')
        # R23 审计 NIT: 五行类型锁——错型(如 scenario 传 dict)原先静默
        # 绕过 SCN-ASSUM/SCN-DIR 等下游检查,现在显式拒收
        ROW_TYPES = {'scenario': str, 'asset_direction': dict,
                     'sensitive_variables': list, 'falsification': dict,
                     'trigger': dict}
        type_bad = set()
        for rname, rtype in ROW_TYPES.items():
            rv = rows.get(rname)
            if rv and not isinstance(rv, rtype):
                bad('SCN-TYPE', f'l4.scenarios[{sid}].rows.{rname}',
                    f'类型须 {rtype.__name__}(得 {type(rv).__name__})')
                type_bad.add(rname)
        scen_text = (rows.get('scenario') or '') if isinstance(
            rows.get('scenario'), str) else ''
        if scen_text and ASSUMPTION_MARK not in scen_text:
            bad('SCN-ASSUM', f'l4.scenarios[{sid}].rows.scenario',
                '情景行须含"假设"(明写假设非预测)')
        ad = rows.get('asset_direction') or {}
        if 'asset_direction' not in type_bad and isinstance(ad, dict):
            if not (ad.get('direction') or '').strip():
                bad('SCN-DIR', f'l4.scenarios[{sid}].rows.asset_direction.direction',
                    '方向判断为空')
            if ad.get('confidence_tier') not in CONFIDENCE_TIERS:
                bad('SCN-DIR',
                    f'l4.scenarios[{sid}].rows.asset_direction.confidence_tier',
                    f'置信层级须三档之一 {CONFIDENCE_TIERS}'
                    f'(得 {ad.get("confidence_tier")!r})')
            refs_ok(f'l4.scenarios[{sid}].rows.asset_direction.evidence_refs',
                    ad.get('evidence_refs'))
        sens = rows.get('sensitive_variables') or []
        if 'sensitive_variables' not in type_bad:
            if sens and not (1 <= len(sens) <= 2):
                bad('SCN-SENS', f'l4.scenarios[{sid}].rows.sensitive_variables',
                    f'敏感变量须 1-2 个(得 {len(sens)})')
            for m in sens:
                if m not in mids:
                    bad('SCN-SENS', f'l4.scenarios[{sid}].rows.sensitive_variables',
                        f'{m!r} 不在注册表(须引擎可观测指标)')
        fals = rows.get('falsification') or {}
        if ('falsification' not in type_bad
                and isinstance(fals, dict) and fals):
            if fals.get('metric_id') not in mids:
                bad('SCN-FALS', f'l4.scenarios[{sid}].rows.falsification.metric_id',
                    f'{fals.get("metric_id")!r} 不在注册表(证伪指标须可观测)')
            if not (fals.get('threshold') or '').strip():
                bad('SCN-FALS', f'l4.scenarios[{sid}].rows.falsification.threshold',
                    '可观测阈值为空')
            # R25 NIT V2-5(R24 审计): 复合证伪条件副指标锚(可选;v1.1)。
            # threshold 文本可提及多指标,主锚=metric_id;其余指标经本字段
            # 机器可验,消除"可读但口径不对称"。缺席=单指标条件,不违规。
            sec = fals.get('secondary_metric_ids')
            if sec is not None:
                if not isinstance(sec, list) or not sec:
                    bad('SCN-FALS2',
                        f'l4.scenarios[{sid}].rows.falsification.'
                        'secondary_metric_ids',
                        '副指标须非空 list(单指标条件直接省略本字段)')
                elif not (1 <= len(sec) <= 3):
                    bad('SCN-FALS2',
                        f'l4.scenarios[{sid}].rows.falsification.'
                        'secondary_metric_ids',
                        f'副指标 1-3 条(得 {len(sec)};主锚仍由 metric_id 承担)')
                else:
                    for sm in sec:
                        if sm not in mids:
                            bad('SCN-FALS2',
                                f'l4.scenarios[{sid}].rows.falsification.'
                                'secondary_metric_ids',
                                f'{sm!r} 不在注册表(副指标同须可观测)')
                    # R36 Ni-4(R25 审计遗留): 重复=口径冗余,契约明示拒
                    # (不静默去重——审计可选"去重或明示",本仓纪律=显式)。
                    # 与主锚重复: 主锚由 metric_id 承担,副表再列=同指标
                    # 双口径;内部重复: 列表语义是集合,重复=凑数或笔误。
                    anchor_dup = fals.get('metric_id')
                    if anchor_dup in sec:
                        bad('SCN-FALS2',
                            f'l4.scenarios[{sid}].rows.falsification.'
                            'secondary_metric_ids',
                            f'{anchor_dup!r} 与主锚 metric_id 重复'
                            '(主锚已由 metric_id 承担,副表列其余指标)')
                    for d in sorted({m for m in sec if sec.count(m) > 1}):
                        bad('SCN-FALS2',
                            f'l4.scenarios[{sid}].rows.falsification.'
                            'secondary_metric_ids',
                            f'{d!r} 在副指标列表内重复(去重后再提)')
        trig = rows.get('trigger') or {}
        if 'trigger' not in type_bad and isinstance(trig, dict) and trig:
            if not (trig.get('condition') or '').strip():
                bad('SCN-TRIG', f'l4.scenarios[{sid}].rows.trigger.condition',
                    '可观测条件为空')
            dl = trig.get('deadline') or ''
            # R23 MINOR-2(独立审计): 真日期校验,防 '2027-13-45' 类过纯正则
            try:
                datetime.strptime(str(dl), '%Y-%m-%d')
            except ValueError:
                bad('SCN-TRIG', f'l4.scenarios[{sid}].rows.trigger.deadline',
                    f'时限须真日期 YYYY-MM-DD(得 {dl!r})')

    # ── Audit-R31 任务3: POL-EFF 决议-生效成对纪律 ────────────────
    # 历史正文关联政策事件时,决议日提及须配生效日(或显式待生效标注)
    # ——「次月末才生效」不得写成当时已发生。确定性子串代理(与
    # ASSUMPTION_MARK 同口径): 段落含政策词形+已知决议日词形,而同段
    # 无该决议的生效日词形且无 待生效/尚未生效/未生效 标注=违规。
    # policy_events=None(未传日历面)=规则不启用,既有调用方零回归。
    if policy_events:
        # Audit-R32 任务2: 断言时点=研究截止日(as_of 在场才启用时点类
        # 规则;None=仅 R31 成对纪律+实体绑定,既有调用方零回归)
        _asof = None
        if isinstance(as_of, str) and len(as_of) >= 10:
            try:
                _asof = datetime.fromisoformat(as_of[:10]).date().isoformat()
            except ValueError:
                _asof = None
        for where, text in _judgment_text_segments(judgment, ev):
            if not any(w in text for w in _POL_EFF_WORDS):
                continue
            bound = _pol_bound_events(text, policy_events)
            if not bound:
                continue
            _pend = any(m in text or m in _pol_norm_text(text)
                        for m in _POL_PENDING_MARKS)
            for ev in bound:
                # Audit-R33 任务2: 政策时态(事件×断言时点×实施状态,
                # 逐分句)——断言时点=段内显式「截至 X」优先于研究
                # 截止日;命中即记违规,本事件不再走 R31/R32 规则
                _t_assert = _pol_assert_time(text, _asof, policy_events,
                                             ev)
                _tense = _pol_tense_violation(text, ev, _asof,
                                              policy_events, bound)
                # 修订 r5: 正文写出的生效日与官方实录不符(日期规则实质命中)
                # 时由日期规则先报——时态模型的发现不顶替 POL-EFF-DATE(冻结
                # R32 门用例②的违规码复原;修订 r4 起被早声称顶替)
                _mm = _pol_date_mismatch(text, ev, bound, _asof, _t_assert)
                if _tense and not _mm:
                    bad(_tense[0], where, _tense[1])
                    continue
                # 公告在研究时点尚不可见的决议不参与判定(当时无从提及)
                if (_asof and ev.get('first_publish')
                        and ev['first_publish'] > _asof):
                    continue
                # Audit-R33 任务2修订 r3: 日期词形与待生效标注在原文和空白
                # 归一副本上都认(「9 月 18 日」带空格形同判);日期规则读归一
                # 副本(带空格的中文日期同样成词元——独立审查 MAJOR-4)
                _nt_text = _pol_norm_text(text)
                dec_in = any(f in text or f in _nt_text
                             for f in _date_word_forms(ev['decision_date']))
                eff_in = any(f in text or f in _nt_text
                             for f in _date_word_forms(ev['effective_on']))
                # 修订 r5: 段内未提官方日期,但以「X 日生效」写出了与本事件官方
                # 实录不符的生效日(_mm 非空)→同样走日期规则(此前直接跳到
                # 「无事件日期」一支,写错生效日的既成句两条规则都不管)
                if not (dec_in or eff_in) and not _mm:
                    _ent = ev.get('entity')
                    _tv = ev.get('target_value')
                    # POL-EFF-PENDING-AS-CURRENT: 断言时点早于生效日,段落写
                    # 本实体政策目标=待生效目标值而无任何待生效/将然标注、
                    # 无决议/生效日期——把待生效值写成了当前值
                    if (_t_assert and _ent and _tv is not None
                            and _t_assert < ev['effective_on']
                            and not _pend
                            and any(w in text
                                    for w in _POL_ENTITY_WORDS.get(_ent, ()))
                            and _pol_value_in_text(_tv, text)
                            and any(w in text for w in _POL_EFF_WORDS)):
                        bad('POL-EFF-PENDING-AS-CURRENT', where,
                            '断言时点 %s(来源: %s)早于 %s 决议(%s)生效日 %s,'
                            '正文以当前口径写目标值 %s(=待生效值)而无待生效/'
                            '将然标注——待生效值不得写成当时已生效的官方'
                            '目标' % (_t_assert,
                                      _pol_first_time_src(text, _asof),
                                      ev['metric_id'],
                                      ev['decision_date'],
                                      ev['effective_on'], _tv))
                    continue
                _ddec, _deff = ev['decision_date'], ev['effective_on']
                lag = _pol_days(_ddec, _deff)
                # POL-EFF-DATE: 正文写出的生效日≠官方实录(早于或晚于;见
                # _pol_date_specs——区间端/断言时点按断言时点措辞)
                _spec = _pol_date_specs(_nt_text, ev, bound, _asof)
                # POL-EFF-REL: 相对生效词形折算隐含生效日早于官方生效日
                # (「决议次日起生效」vs 官方 6 天后生效)——相对日期提前生效
                if lag and lag > 0:
                    for pat, off in _POL_REL_EFF:
                        _m = re.search(pat, text)
                        if _m and off < lag:
                            _spec.append(
                                '相对生效词形「%s」隐含决议+%d天生效,早于'
                                '官方实录生效日 %s(决议 %s,+%d天)——不得以'
                                '相对日期提前生效'
                                % (_m.group(0), off, _deff, _ddec, lag))
                            break
                if _spec:
                    for _d in _spec:
                        bad('POL-EFF-DATE' if '相对生效' not in _d
                            else 'POL-EFF-REL', where, _d)
                elif dec_in and not eff_in and not any(
                        m in text or m in _nt_text
                        for m in ('待生效', '尚未生效', '未生效')):
                    # R31 成对纪律(原口径): 决议日提及须配生效日或待生效标注
                    bad('POL-EFF', where,
                        '提及决议日 %s(%s)但未配生效日 %s,亦无待生效标注——'
                        '决议与生效分记,次月末才生效不得写成当时已发生'
                        % (_ddec, ev['metric_id'], _deff))
                # POL-EFF-EARLY-CLAIM(Audit-R33 任务2 起)由上方逐分句
                # 时态模型产出(整段现行词形代理退役: 它既漏「截至 X …
                # 已经实施」,又把同段无关的「目前」误判为生效断言)

    return {'passed': not v, 'violations': v,
            'n_contradictions': len(contras),
            'n_mechanism_chains': len(chains),
            'n_scenarios': len(scenarios)}


def _registry_metric_ids(root):
    import workbench_data as wd
    reg = wd.load_registry(root)
    return {m.get('metric_id') for m in (reg.get('metrics') or [])
            if m.get('metric_id')}


def _canonical(obj):
    """稳定规范化 JSON 串(跨 CPython 3.9-3.12 同文同串)。"""
    return json.dumps(obj, sort_keys=True, ensure_ascii=True,
                      separators=(',', ':'), default=str)


def frozen_inputs_digest(mapping):
    """Audit-R29 任务4: 冻结输入集合摘要(渲染依赖身份锚)。

    输入=relpath→sha16 映射(地图问句运行时实际读的 root 文件逐字节
    摘要: 发布日期历+运行快照);输出=sorted 'rel:sha16' 行以 \\n 连接
    后的 sha256。空映射/非映射→None(非地图问句不绑)。
    五处同算同核: 运行面(report.run.frozen_inputs)→席位信封→
    终裁(extra.frozen_inputs_sha256)→归档(manifest)→重放(复算)——
    任何一处本地文件被改而摘要未随=不一致即拒。"""
    import hashlib
    if not isinstance(mapping, dict) or not mapping:
        return None
    lines = sorted('%s:%s' % (rel, str(sha)[:16])
                   for rel, sha in mapping.items())
    return hashlib.sha256('\n'.join(lines).encode('utf-8')).hexdigest()


# Audit-R2 条目1: 摘要边界内须剥离的易变键(审查机制自身状态面,
# 写入即变——不剥离则裁决落档自噬;其余键全在摘要内,含 attach 台账
# 与版本指针 run.git_head/pipeline_version——重 attach/换引擎版本即
# 失效旧裁决,任一交付输入变化不得沿用旧审查)
_DIGEST_VOLATILE_REPORT_KEYS = ('semantic_review',)
_DIGEST_VOLATILE_JUDGMENT_KEYS = ('semantic_review',)


def content_digest(report_dir, judgment_path=None):
    """Audit-R4 条目2: 唯一规范化内容=**全部实际交付输入源**。

    边界(稳定,禁漂移): canonical(report.json 剥 semantic_review)
    + NUL + canonical(agent_judgment 剥 semantic_review)
    + NUL + canonical(views_digest.json 或 {},缺席稳定)。
    Audit-R2 v2 口径漏了 views_digest.json——它是 FULL_REPORT L2 摘编
    行的**直接渲染输入**(机构归属/标题/日期/原文摘编)且是 Agent 席
    判断输入(read_first),却不在摘要内: 反例=只改 institution_name/
    report_title,FULL_REPORT 已变而摘要/fresh/deliverable/归档全照过
    (审查未覆盖实际交付内容)。v3 收口: 任一渲染输入(机构归属、标题、
    日期、摘编、事实、判断)变化即失效旧裁决。views_digest 由 plan 段
    一次性确定性装配,裁决落档后无人回写——无循环绑定。
    report.md/FULL_REPORT=上述三源的渲染视图,**不入摘要**;视图与源
    的一致性由交付门 copies_consistent 核对(_r1_report_core: report.md
    =report.json 当前渲染,FULL_REPORT=当前确定性装配)。
    裁决档自身(VERDICT-*.json)不在 report_dir 内,天然不在边界
    (Audit-R1 F02 循环依赖切断面保留)。
    """
    import hashlib
    rp = _load_json(os.path.join(report_dir, 'report.json'))
    for k in _DIGEST_VOLATILE_REPORT_KEYS:
        rp.pop(k, None)
    if judgment_path is None:
        for cand in ('agent_judgment.json', 'judgment_mvp.json'):
            p = os.path.join(report_dir, cand)
            if os.path.isfile(p):
                judgment_path = p
                break
    j = _load_json(judgment_path)
    for k in _DIGEST_VOLATILE_JUDGMENT_KEYS:
        j.pop(k, None)
    vd_p = os.path.join(report_dir, 'views_digest.json')
    vd = _load_json(vd_p) if os.path.isfile(vd_p) else {}
    return hashlib.sha256(
        (_canonical(rp) + '\x00' + _canonical(j) + '\x00'
         + _canonical(vd)).encode('utf-8')).hexdigest()


def content_digest_v2(report_dir, judgment_path=None):
    """Audit-R2 v2 口径(report.json+agent_judgment,不含 views_digest)
    ——仅存续供裁决重绑迁移验证旧锚(rebind_verdict_digest),
    不得用于新裁决绑定。"""
    import hashlib
    rp = _load_json(os.path.join(report_dir, 'report.json'))
    for k in _DIGEST_VOLATILE_REPORT_KEYS:
        rp.pop(k, None)
    if judgment_path is None:
        for cand in ('agent_judgment.json', 'judgment_mvp.json'):
            p = os.path.join(report_dir, cand)
            if os.path.isfile(p):
                judgment_path = p
                break
    j = _load_json(judgment_path)
    for k in _DIGEST_VOLATILE_JUDGMENT_KEYS:
        j.pop(k, None)
    return hashlib.sha256(
        (_canonical(rp) + '\x00' + _canonical(j)).encode('utf-8')).hexdigest()


def content_digest_v1(report_dir, judgment_path=None):
    """Audit-R1 旧口径(judgment + report.md 全文)——仅存续供裁决重绑
    迁移验证旧锚(rebind_verdict_digest),不得用于新裁决绑定。"""
    import hashlib
    if judgment_path is None:
        for cand in ('agent_judgment.json', 'judgment_mvp.json'):
            p = os.path.join(report_dir, cand)
            if os.path.isfile(p):
                judgment_path = p
                break
    j = _load_json(judgment_path)
    j.pop('semantic_review', None)
    md = open(os.path.join(report_dir, 'report.md'), encoding='utf-8').read()
    return hashlib.sha256((_canonical(j) + '\x00' + md).encode('utf-8')
                          ).hexdigest()


# Audit-R1 F02: 独立审查可放行档(裁决语汇——席位其余语汇一律不放行)
REVIEW_APPROVED_VERDICTS = ('VERIFIED', 'PASS', 'UPHELD')

# Audit-R2 条目2: 裁决档必填字段(缺任一=损坏档,最新档损坏即阻断,
# 不回退旧 PASS)
VERDICT_REQUIRED_FIELDS = ('overall', 'reviewer', 'run_ts', 'recorded_at')

# R32 席位词表(Audit-R2 收口): 语义审查席裁决档只认章程四词。与四态门
# 放行词(REVIEW_APPROVED_VERDICTS)是两张表——席位席报告词 VERIFIED/PASS
# 须映射为 UPHELD 后落档(同义,-01 档先例),越表词落档即抛(B3 机核面)。
SEAT_VERDICT_VOCAB = ('UPHELD', 'REVISE', 'NOT_VERIFIED', 'REJECT_ENTRY')

# ── Audit-R5 条目4: 裁决档格式与摘要算法版本显式可验证 ──────────────
# 新写档显式携带 format_version+digest_algorithm;读取端: 未知版本按
# 最严处理(不因缺失/未知获得更宽松权限);format_version 缺席=按档形
# 推断时代(revision 在场=现行格式,缺席=legacy)——推断结果与显式声明
# 适用同一套校验,永不更宽。历史口径 algo 仅存续供 rebind 迁移验证。
VERDICT_FORMAT_VERSION = 2
DIGEST_ALGORITHM_CURRENT = 'digest_v3'
DIGEST_ALGORITHMS_HISTORICAL = ('digest_v1', 'digest_v2')
# 三代口径各自覆盖的交付输入(rebind 未覆盖面=机器推导,禁手工漂移):
_ALGO_INPUTS = {
    'digest_v1': ('agent_judgment.json', 'report.md'),
    'digest_v2': ('report.json', 'agent_judgment.json'),
    DIGEST_ALGORITHM_CURRENT: ('report.json', 'agent_judgment.json',
                               'views_digest.json'),
}


def _verdicts_for_run(root, run_ts):
    """按 run_ts 收全裁决档(跨日目录,run_ts 在文件名内)。

    返回 [(path, doc)];doc=None=不可解析(损坏档如实入列,不静默丢)。
    """
    import glob as _glob
    out = []
    for p in sorted(_glob.glob(os.path.join(
            root, 'audit', 'semantic_review', '*', 'VERDICT-*.json'))):
        if run_ts not in os.path.basename(p):
            continue
        try:
            v = _load_json(p)
            if not isinstance(v, dict):
                v = None
        except Exception:
            v = None
        out.append((p, v))
    return out


def _verdict_sort_key(path, doc):
    """裁决写入序(Audit-R4 条目1): (日目录, 文件名 seq, 文件名)。

    排序只读**稳定文件面**——日目录+文件名序号是 append-only 写入纪律
    的事实承载(同日 seq 单调递增,跨日日串递增),mtime 不参与。
    Audit-R2 口径按「有 revision 的内容序、损坏档降 legacy 代」分代——
    反例: 链尾新档(revision=3)截断后解析失败,被降为 legacy 代排到
    全部 revision 档之前,旧 UPHELD(revision=2)回升为最新,fresh=True
    交付照过=**裁决先后关系因解析失败而倒退**。Audit-R4 起统一写入序:
    损坏档占其真实写入位(链尾),最新位损坏即 corrupt_latest 阻断,
    不得跳过错误记录回退旧裁决。revision 作为**校验不变量**而非排序键:
    写入序下有效档 revision 必须递增,倒序/重复=order_conflict/
    duplicate_revision 阻断(_semantic_review_state 校验)。
    """
    day = os.path.basename(os.path.dirname(path))
    name = os.path.basename(path)
    seq = ''
    m = re.search(r'-(\d+)\.json$', name)
    if m:
        seq = '%06d' % int(m.group(1))
    return (day or '00000000', seq, name)


def _verdict_write_positions_disagree(keyed):
    """Audit-R4 条目1 不变量: 写入序下有效档 revision 必须严格递增。

    返回冲突描述串(无冲突=None): 倒序或重复。损坏/legacy 档无 revision
    不参与本不变量(它们占写入位但无从校验号序——正因无从校验,它们
    不得静默充当最新放行档,由 _semantic_review_state 单独处理)。
    """
    seen = {}
    for (_, p, v) in keyed:
        rev = (v or {}).get('revision') if isinstance(v, dict) else None
        if not (isinstance(rev, int) and rev > 0):
            continue
        if rev in seen:
            return ('duplicate_revision: %s 与 %s 同号 revision=%d'
                    % (seen[rev], p, rev))
        seen[rev] = p
    revs = [((v or {}).get('revision'), p) for (_, p, v) in keyed
            if isinstance(v, dict)
            and isinstance((v or {}).get('revision'), int)
            and (v or {}).get('revision') > 0]
    for (r1, p1), (r2, p2) in zip(revs, revs[1:]):
        if r2 <= r1:
            return ('order_conflict: %s(rev=%d) 写入位晚于 %s(rev=%d)'
                    ' 但 revision 未递增' % (p2, r2, p1, r1))
    return None


def _verdict_record_error(root, path, doc, run_ts, ordered_run_paths):
    """Audit-R4 条目1 + Audit-R5 条目4 读取端单档校验: None=有效。

    ordered_run_paths: **写入序**下的本 run 在档相对路径列表(规范序=
    _verdict_sort_key);本档写入位=其在表中的下标。

    两级:
    - 解析级(corrupt): 不可解析/非 dict/缺必填字段(overall/reviewer/
      run_ts/recorded_at)——文件本身不可读,但写入位仍是事实;
    - 语义级(invalid_record): revision 非正整数/裁决词越表/run_ts 字段
      与文件名键不符/format_version 未知/predecessor 缺失或非法——
      语义可判的违规,无论写入位在哪都阻断。

    Audit-R5 条目4 收紧面(反例复现于基线 49fb583):
    - 删除 revision 冒充 legacy 不再放行: legacy 形(无 revision 键)
      只在**首写入位**合法(真 legacy=链头;v1 前史档其放行本就被
      fresh=None 挡死);非首位无 revision=降级攻击,invalid_record;
      首位 legacy 档的时代一致性(锚须为历史口径)由
      _semantic_review_state 的 _legacy_era_error 核验;
    - 非首档 predecessor 必填且必须指向**紧邻前序**(写入位-1)——
      指向自己/后续记录/隔位前序/缺席均=断链,invalid_record;
      首档 predecessor 必须 None(首档无前序,带 pred=指向后续或
      造链,invalid_record);
    - format_version 在场但非已知版本=invalid_record(未知版本按最严
      处理,缺失按档形推断——推断适用同一套校验,永不更宽)。

    Audit-R6 条目3 收紧面(反例复现于基线 dcb4b17):
    - 共用校验(裁决词/任务身份 run_ts/算法版本)先于时代分流,legacy
      形同样过共用面——旧格式仅兼容历史确缺字段(revision/predecessor),
      不跳过共用校验;
    - digest_algorithm 逐档核验(不再只检最新档): 在场而非现行口径=
      invalid_record,任何写入位阻断。
    """
    if not isinstance(doc, dict):
        return 'corrupt: 不可解析/非对象'
    for f in VERDICT_REQUIRED_FIELDS:
        if not doc.get(f):
            return 'corrupt: 缺必填字段 %s' % f
    fmt = doc.get('format_version')
    if fmt is not None and fmt != VERDICT_FORMAT_VERSION:
        return ('invalid_record: format_version=%r 未知(现行=%d;缺失或'
                '未知版本不得获得更宽松权限)' % (fmt, VERDICT_FORMAT_VERSION))
    # ── Audit-R6 条目3: 共用校验(任务身份/合法裁决词/算法版本)先于时代
    # 分流——legacy 形(无 revision)只兼容**历史确缺字段**(revision/
    # predecessor 缺席),不得跳过共用面。反例(基线 dcb4b17 复现): 首档
    # 删 revision 后 run_ts=WRONG_RUN/overall=UNKNOWN_VERDICT 靠 legacy
    # 早退放行;首档 digest_algorithm=UNKNOWN_ALGORITHM 因逐档校验缺算法
    # 版本面而放行——两例均为「只检最新档+legacy 早退」的绕行面。
    if doc.get('overall') not in SEAT_VERDICT_VOCAB:
        return 'invalid_record: 裁决词 %r 越席位词表' % (doc.get('overall'),)
    if doc.get('run_ts') != run_ts:
        return ('invalid_record: run_ts 字段=%r 与文件名键=%r 不符'
                '(错误 run 档)' % (doc.get('run_ts'), run_ts))
    algo = doc.get('digest_algorithm')
    if algo is not None and algo != DIGEST_ALGORITHM_CURRENT:
        # 逐档算法版本: 字段只在现行写入端落档(落档值恒=当时现行口径,
        # 历史档该字段缺席)——在场而非现行值=不可核验口径,按最严阻断;
        # v1/v2 口径仅存续于 rebind 迁移验证(extra.rebind.from_algorithm),
        # 不作为裁决档 digest_algorithm 合法值。
        return ('invalid_record: digest_algorithm=%r 非现行口径(现行=%s;'
                '在场而非现行=不可核验,逐档阻断)' % (algo,
                                                    DIGEST_ALGORITHM_CURRENT))
    own_rel = os.path.normpath(os.path.relpath(path, root))
    try:
        pos = ordered_run_paths.index(own_rel)
    except ValueError:                      # 不在本 run 键下(调用面已滤)
        pos = -1
    if 'revision' not in doc:
        if pos != 0:
            return ('invalid_record: 无 revision 档出现在非首写入位'
                    '(pos=%d;删除 revision 冒充 legacy 的降级)' % pos)
        return None                      # 首位 legacy 形: 时代锚另核
    rev = doc.get('revision')
    if not (isinstance(rev, int) and not isinstance(rev, bool) and rev > 0):
        return 'invalid_record: revision=%r 非正整数' % (rev,)
    pred = doc.get('predecessor')
    if pos == 0:
        if pred is not None:
            return ('invalid_record: 首档 predecessor 必须 None(实=%r;'
                    '首档带前序=造链/指向后续)' % (pred,))
    else:
        if pred is None:
            return ('invalid_record: 非首档(pos=%d)缺 predecessor'
                    '(链断)' % pos)
        p_norm = os.path.normpath(pred)
        if p_norm == own_rel:
            return 'invalid_record: predecessor 指向自己(%r)' % (pred,)
        if p_norm not in ordered_run_paths:
            return ('invalid_record: predecessor=%r 不指向本 run 在档文件'
                    '(跨任务/链外)' % (pred,))
        if ordered_run_paths.index(p_norm) != pos - 1:
            return ('invalid_record: predecessor=%r 未指向紧邻前序'
                    '(指向自己之外的隔位/后续记录=断链)' % (pred,))
    return None


def record_semantic_verdict(root, report_dir, overall, reviewer,
                            notes='', extra=None):
    """Audit-R1 F02 + Audit-R2 条目2: 独立席裁决落档(append-only,带内容绑定)。

    写 root/audit/semantic_review/<YYYYMMDD>/VERDICT-<run_ts>-<seq>.json,
    content_sha256=content_digest(report_dir)(裁决绑定的锚)。修订循环:
    正文修订→摘要变→旧档自动过期(_semantic_review_state 的 fresh=False),
    席位复验后调本函数再写新档——旧失败证据永在档,不覆盖。

    Audit-R2 条目2 定序面: revision=该 run_ts 全档(跨日目录)最大号+1,
    predecessor=前一最新档相对路径(首档=None)——裁决顺序由内容字段
    显式承载,不依赖文件系统 mtime;必填字段(overall/reviewer/run_ts/
    recorded_at)缺失即抛 ValueError,损坏档不落盘。
    Audit-R4 条目1 硬化: revision 赋号下界取 max(在档最大有效号,
    **全档文件数**)——链上存在损坏档(其 revision 无从读取)时,新号
    仍严格大于损坏档可能持有的任何号(append-only 下任一档的号≤其
    写入时的全档数≤当前全档数),复审恢复不与不可读档撞号;写入序
    (_verdict_sort_key)为裁决顺序权威。
    """
    if not overall or not reviewer:
        raise ValueError('裁决必填字段缺失: overall/reviewer 不得为空')
    if overall not in SEAT_VERDICT_VOCAB:
        raise ValueError(f'越表裁决词: {overall!r} 不在 R32 席位词表 '
                         f'{SEAT_VERDICT_VOCAB}(同义映射: '
                         'VERIFIED/PASS→UPHELD)')
    report = _load_json(os.path.join(report_dir, 'report.json'))
    run_ts = (report.get('run') or {}).get('ts_utc') or ''
    if not run_ts:
        raise ValueError('report.json 缺 run.ts_utc,无法绑定裁决')
    day = datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')
    d = os.path.join(root, 'audit', 'semantic_review', day)
    os.makedirs(d, exist_ok=True)
    # R11 P1②: 配号/前序读取/落盘同一跨进程锁临界区(锁域=整个
    # semantic_review 树——跨日目录的 revision 链也在域内);临时文件
    # 独立命名+fsync 后原子发布,终档存在性在锁内复核,不虚报成功。
    import store_lock as sl
    with sl.store_write_lock(os.path.dirname(d)):
        seq = len([f for f in os.listdir(d) if f.startswith(
            'VERDICT-' + run_ts)]) + 1
        path = os.path.join(d, 'VERDICT-%s-%02d.json' % (run_ts, seq))
        if os.path.exists(path):
            raise FileExistsError(
                f'裁决档已存在(锁下配号冲突,拒绝覆盖): {path}')
        prior = _verdicts_for_run(root, run_ts)
        revs = [v.get('revision') for _, v in prior
                if isinstance(v, dict) and isinstance(v.get('revision'), int)]
        # Audit-R4: 号下界=全档数(含不可读档)——复审恢复不与损坏档撞号
        revision = max(revs + [len(prior)]) + 1
        predecessor = None
        if prior:
            latest_p, _ = max(
                prior, key=lambda t: _verdict_sort_key(t[0], t[1]))
            predecessor = os.path.relpath(latest_p, root)
        # Audit-R1 对齐 R32 席位章程 schema: seat 恒为章程名,audited_at=归档日
        # (HKT),counterexamples_sought 非空由调用席自证(B3/B4/B5 机核面)。
        doc = {'seat': 'semantic-audit-seat', 'overall': overall,
               'reviewer': reviewer, 'notes': notes,
               'run_ts': run_ts, 'content_sha256': content_digest(report_dir),
               'audited_at': day[:4] + '-' + day[4:6] + '-' + day[6:],
               'recorded_at': _now_utc(),
               # Audit-R5 条目4: 格式与摘要算法显式可验证(读取端未知版本
               # 按最严处理;缺席=legacy 时代,时代锚另核)
               'format_version': VERDICT_FORMAT_VERSION,
               'digest_algorithm': DIGEST_ALGORITHM_CURRENT,
               'revision': revision, 'predecessor': predecessor,
               # Audit-R23 任务1: 最终 MAP_REPORT.md 内容段摘要随裁决
               # 落档——错误版本(在场地图被改)不得沿用旧裁决: 读取端
               # _semantic_review_state 按此判 fresh,非地图问句/未渲染
               # =None 不绑(旧档无此键=历史面,内容摘要仍为唯一锚)。
               'map_report_sha256': map_report_content_sha(report_dir),
               'counterexamples_sought': ((extra or {}).pop(
                   'counterexamples_sought', None)
                   or ['(未记载: 席位简报须补反例面)'])}
        # Audit-R29 任务4(实雷正道修): 冻结输入摘要绑定机械化——真实
        # 席位按 SKILL 逐字抄 python 片段并不可靠(B 会话实测: 复裁
        # UPHELD 但落裁未带 extra→归档 belt 拒)。绑定是机械面不是判断
        # 面: 记录器从 report.run.frozen_inputs 自动摸出并落
        # frozen_inputs_sha256(席位判断义务不变;extra 显式传值须与
        # 自动值一致,不一致=席位绑了别家的摘要,拒绝落档)。非地图/
        # R29 前旧档 run 无该键=None 不绑(零回归)。
        _fi_auto = frozen_inputs_digest(
            (report.get('run') or {}).get('frozen_inputs'))
        _fi_extra = (extra or {}).get('frozen_inputs_sha256')
        if _fi_auto:
            if _fi_extra and str(_fi_extra) != _fi_auto:
                raise ValueError(
                    '席位冻结摘要与报告冻结面不符: extra=%s 报告=%s '
                    '(席位必须绑定本报告的渲染依赖身份)'
                    % (str(_fi_extra)[:16], _fi_auto[:16]))
            doc['frozen_inputs_sha256'] = _fi_auto
        if extra:
            doc.update(extra)
        sl.atomic_write_json(path, doc, indent=2, sort_keys=False)
    return path


MAP_REVIEW_SECTION_SPLIT = '\n## 语义审查'

# Audit-R32 正式验收(裁决后交付状态面): 地图「分工」行尾的审查状态短语
# 随裁决在场与否翻转(待裁→已裁)——属状态面而非内容面,与「## 语义审查」
# 节同类,但它位于内容段之内。裁决绑定/fresh 判定/归档与重放核对按
# 「内容段除该短语外逐字节相同」视同一受审版本(状态面等价);其余任何
# 差异仍=不同版本(冻结/过期/拒绝口径不变)。短语只认「分工」行的行尾。
MAP_STATUS_PENDING = '独立语义审查待裁'
MAP_STATUS_DECIDED = '经独立语义审查'
_MAP_STATUS_LINE = '- 分工: '
_MAP_STATUS_TAILS = (',' + MAP_STATUS_PENDING + ')',
                     ',' + MAP_STATUS_DECIDED + ')')


def _sha256_text(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def _read_map_text(report_dir):
    """运行目录 MAP_REPORT.md 全文;缺席/不可读→None。"""
    try:
        with open(os.path.join(report_dir or '', 'MAP_REPORT.md'),
                  encoding='utf-8') as f:
            return f.read()
    except (OSError, ValueError):
        return None


def map_content_segment(text):
    """地图全文→内容段(首个「## 语义审查」节之前的一切)。"""
    return (text or '').split(MAP_REVIEW_SECTION_SPLIT)[0]


def _map_status_form(seg, tail_from, tail_to):
    """内容段内「分工」行行尾状态短语 tail_from→tail_to(其余不动)。"""
    out = []
    for ln in seg.split('\n'):
        if (tail_from != tail_to and ln.startswith(_MAP_STATUS_LINE)
                and ln.endswith(tail_from)):
            ln = ln[:-len(tail_from)] + tail_to
        out.append(ln)
    return '\n'.join(out)


def map_content_normalized(text):
    """内容段状态面归一(已裁形): 仅「分工」行尾的待裁短语改写。"""
    seg = map_content_segment(text)
    return _map_status_form(seg, _MAP_STATUS_TAILS[0], _MAP_STATUS_TAILS[1])


def map_content_state_equivalent(a, b):
    """两份地图全文的受审内容是否同一版本(仅差审查状态短语=True)。"""
    return map_content_normalized(a) == map_content_normalized(b)


def map_binding_matches(text, bound):
    """地图全文 text 的内容段是否=裁决落档时绑定的摘要 bound。

    原字节/已裁形/待裁形三口径之一相等即匹配——绑定可落在裁决前(待裁)
    或裁决后(已裁)任一状态;正文任何其他差异均不匹配。
    """
    if not bound:
        return False
    seg = map_content_segment(text)
    cands = {_sha256_text(seg),
             _sha256_text(map_content_normalized(text)),
             _sha256_text(_map_status_form(
                 seg, _MAP_STATUS_TAILS[1], _MAP_STATUS_TAILS[0]))}
    return str(bound) in cands


def map_report_content_sha(report_dir):
    """Audit-R23 任务1: MAP_REPORT.md 内容段摘要(裁决↔地图绑定锚)。

    内容段=首个「## 语义审查」节之前的一切(对照表/走位/传导/转折/
    历史类比)——语义审查节在裁决落档后由「待裁」翻「已裁」,属状态面
    非内容面,排除在外使绑定在裁决前后稳定。文件缺席→None(非地图
    问句运行/未渲染,不绑)。摘要按内容段原字节计算(不归一状态短语);
    裁决前后状态短语不同的两份内容段如何算同一受审版本见
    map_binding_matches(Audit-R32 正式验收)。
    """
    text = _read_map_text(report_dir)
    if text is None:
        return None
    return _sha256_text(map_content_segment(text))


def _sha16_of_file(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()[:16]


def _git_blob_proof(root, report_dir, latest_rel, name):
    """Audit-R5 条目1 git 面可信旧证: 最早含旧裁决档(在案路径)的提交
    里,该交付输入的仓内 blob==当前字节(该提交=旧档在案时点的仓内
    快照)。旧档/文件不在同一仓内、无提交含它、git 不可用→None
    (不可证,上层面按不可证处理)。"""
    import hashlib
    import subprocess
    try:
        top = subprocess.run(
            ['git', '-C', report_dir, 'rev-parse', '--show-toplevel'],
            capture_output=True, text=True, timeout=15).stdout.strip()
        if not top:
            return None
        f_rel = os.path.relpath(os.path.join(report_dir, name), top)
        v_rel = os.path.relpath(
            os.path.join(root, latest_rel), top)
        if f_rel.startswith('..') or v_rel.startswith('..'):
            return None
        commits = subprocess.run(
            ['git', '-C', top, 'log', '--reverse', '--format=%H', '--', v_rel],
            capture_output=True, text=True, timeout=15).stdout.split()
        if not commits:
            return None
        blob = subprocess.run(
            ['git', '-C', top, 'show', '%s:%s' % (commits[0], f_rel)],
            capture_output=True, timeout=15).stdout
        got = hashlib.sha256(blob).hexdigest()[:16] if blob else None
        return ('git:%s:%s' % (commits[0][:12], f_rel), got)
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def _rebind_trusted_proofs(root, report_dir, latest_p, latest, matched_key):
    """Audit-R5 条目1: 旧摘要未覆盖交付输入的可信旧证核验。

    旧口径(v1/v2)锚复配只证明**其覆盖面**未变;未覆盖面(如 v2 之于
    views_digest.json)须另有可信旧证证明自旧裁决在案时点未变,才允许
    把通过状态迁移到覆盖全部交付输入的 v3。可信源(其一即可;均非从
    当前文件临时生成的"旧基准"——禁止自我证明):
    - 归档 manifest: root/research_archive/*/ARCHIVE_MANIFEST.json 且
      verdict_chain 含本旧档(source_rel+sha256 前 16 位双吻合)——
      copies_sha16 为归档时点快照(键缺席=该时点文件缺席,亦为快照事实);
    - git 提交: 最早含本旧档(在案路径)的提交里该文件 blob==当前。
    返回 (proofs{文件: {source, sha256_16}}, problems[str]);
    problems 非空=存在未覆盖输入不可证未变(或已变)。
    """
    uncovered = [n for n in _ALGO_INPUTS[DIGEST_ALGORITHM_CURRENT]
                 if n not in _ALGO_INPUTS[matched_key]]
    proofs, problems = {}, []
    latest_rel = os.path.relpath(latest_p, root)
    latest_sha16 = _sha16_of_file(latest_p)
    manifests = []
    arc_dir = os.path.join(root, 'research_archive')
    if os.path.isdir(arc_dir):
        import glob as _glob
        for mp in sorted(_glob.glob(os.path.join(
                arc_dir, '*', 'ARCHIVE_MANIFEST.json'))):
            try:
                m = _load_json(mp)
            except (OSError, ValueError):
                continue
            if any(isinstance(e, dict)
                   and e.get('source_rel') == latest_rel
                   and e.get('sha256') == latest_sha16
                   for e in (m.get('verdict_chain') or [])):
                manifests.append((os.path.relpath(mp, root), m))
    for name in uncovered:
        p = os.path.join(report_dir, name)
        cur = _sha16_of_file(p) if os.path.isfile(p) else None
        trust = None
        for mrel, m in manifests:
            copies = m.get('copies_sha16') or {}
            trust = ('archive_manifest:%s#copies_sha16' % mrel,
                     copies.get(name))
            break
        if trust is None:
            trust = _git_blob_proof(root, report_dir, latest_rel, name)
        if trust is None:
            problems.append(
                '%s 无可信旧证(归档 manifest 与 git 提交均缺席)——旧审查'
                '是否覆盖该输入不可证' % name)
            continue
        src, old = trust
        if old != cur:
            problems.append('%s 与可信旧证不符(%s 时点 %r→当前 %r)——'
                            '新增范围已被修改' % (name, src, old, cur))
        else:
            proofs[name] = {'source': src, 'sha256_16': cur}
    return proofs, problems


def rebind_verdict_digest(root, report_dir, note):
    """Audit-R2 条目1 + Audit-R4 条目2/6 + Audit-R5 条目1 迁移面。

    机械重绑的**全部**前置(缺一即 ValueError,须重新独立审查):
    1. 旧裁决本身合法有效: 读取端单档校验通过——旧档损坏/违规=旧裁决
       无效,不得继承其通过状态;
    2. 旧锚复配: 最新档 content_sha256 与历史口径 v1/v2 之一在当前
       内容上的复算值一致——证明**旧口径覆盖面**未变;
    3. 未覆盖面可信旧证: v1/v2 不覆盖的交付输入(如 views_digest.json)
       须有可信旧快照(归档 manifest copies_sha16 / git 提交 blob)证明
       自旧裁决在案时点未变——不得从当前文件临时生成"旧基准"自我证明;
    4. 内容边界一致: 未覆盖面=v3 输入−旧口径输入(机器推导,与普通
       report/archive 门同一边界),迁移/报告/归档不各写一套。
    非重审: 判断内容零变化,裁决结论承袭;rebind 块=机器可查的迁移
    证据(uncovered_inputs_proof 逐输入记可信源与哈希)。
    """
    report = _load_json(os.path.join(report_dir, 'report.json'))
    run_ts = (report.get('run') or {}).get('ts_utc') or ''
    if not run_ts:
        raise ValueError('report.json 缺 run.ts_utc,无法重绑')
    hits = _verdicts_for_run(root, run_ts)
    if not hits:
        raise ValueError('无在档裁决可重绑')
    keyed = sorted((_verdict_sort_key(p, v), p, v) for p, v in hits)
    ordered = [os.path.normpath(os.path.relpath(p, root))
               for _, p, _ in keyed]
    latest_p, latest = keyed[-1][1], keyed[-1][2]
    if not isinstance(latest, dict) or not latest.get('content_sha256'):
        raise ValueError('最新档无旧锚,不适用机械重绑')
    # (1) 旧裁决时代合法性(legacy 形最新档=旧口径时代,其时代锚一致性
    # 由 (2) 的复配本身证明)
    err = _verdict_record_error(root, latest_p, latest, run_ts, ordered)
    if err:
        raise ValueError('旧裁决档不合法(%s @ %s)——旧裁决无效不得继承,'
                         '须重新独立审查'
                         % (err, os.path.relpath(latest_p, root)))
    matched_key = None
    for key, algo in (('digest_v1', content_digest_v1),
                      ('digest_v2', content_digest_v2)):
        try:
            if latest['content_sha256'] == algo(report_dir):
                matched_key = key
                break
        except (OSError, ValueError):
            continue
    if matched_key is None:
        raise ValueError('旧锚与当前内容不符(任一历史口径均不复配——'
                         '内容已变)——须独立复验,不得机械重绑')
    # (3) 未覆盖面可信旧证(v2 不覆盖 views_digest;v1 另不覆盖 report.json)
    proofs, problems = _rebind_trusted_proofs(
        root, report_dir, latest_p, latest, matched_key)
    if problems:
        raise ValueError(
            '旧摘要(%s)未覆盖全部交付输入且不可证明未变: %s——旧审查与'
            '当前完整内容的同一性不可证,须重新独立审查,不得机械重绑'
            % (matched_key, '; '.join(problems)))
    return record_semantic_verdict(
        root, report_dir, latest.get('overall'), latest.get('reviewer'),
        notes=(latest.get('notes') or ''),
        extra={'rebind': {
            'from_algorithm': matched_key,
            'to_algorithm': DIGEST_ALGORITHM_CURRENT,
            'verified_old_match': True,
            'uncovered_inputs_proof': proofs,
            'predecessor_archive': os.path.relpath(latest_p, root),
            'note': note}})


def _legacy_era_error(report_dir, doc):
    """Audit-R5 条目4: legacy 形档(无 revision 键)的时代锚核验。

    真 legacy 档=revision 键出现**之前**写入的前史档,锚当时按历史口径
    (v1/v2)计算。**攻击指纹**=revision-less 档的锚恰为现行 v3 口径
    (在当前内容上复配)——真 legacy 不可能持有 v3 锚(v3 出现时新写档
    已强制带 revision),此形=新格式档被删除 revision 冒充 legacy 且
    将以 fresh=True 通过交付门,invalid_record 阻断。
    锚与当前内容任一口径均不复配=被替代的**过时前史裁决**(链中间位
    常态: 修订前后内容不同),fresh 自然 False,不是攻击,放行为历史;
    无 report_dir 可核=非交付门调用面,同样不误伤。
    """
    if report_dir is None:
        return None
    anchor = doc.get('content_sha256')
    if not anchor:
        return None          # 无锚 legacy: 由 fresh=None 挡死,不算降级攻击
    try:
        cur_v3 = content_digest(report_dir)
        if anchor == cur_v3 and anchor not in (content_digest_v1(report_dir),
                                               content_digest_v2(report_dir)):
            return ('invalid_record: legacy 形档锚为现行 v3 口径(疑似'
                    '新格式档删除 revision 的降级)')
    except (OSError, ValueError):
        return ('invalid_record: legacy 档时代锚不可核验(交付输入件缺失)'
                '——不可证=阻断')
    return None


def _semantic_review_state(report, root, report_dir=None):
    """R33-①: 语义审计席状态面(常驻席=SEMANTIC-AUDIT-SEAT;§4b/§8)。

    唤起点(ii): L3(定性推断)/L4(条件情景)落位即 required=True——
    渲染器只标状态+披露(§8 披露开关),真席位调用归编排层(引擎轮读
    report.semantic_review.required 自动唤席)。席位裁决档=
    root/audit/semantic_review/YYYYMMDD/VERDICT-<run_ts>*.json
    (append-only),在案→披露升为裁决摘要;缺席→「叙事语义未经
    独立裁决」。确定性: 纯文件面判定,零模型零网络。

    Audit-R1 F02 绑定面: 裁决档带 content_sha256 时按当前
    content_digest(report_dir) 判 fresh(True/False);无绑定键的旧档
    fresh=None(在场但不冒充新鲜——report 门不放行)。

    Audit-R2 条目2 裁决顺序与非法记录(fail-closed):
    - 定序=**写入序** _verdict_sort_key(日目录+文件名 seq+文件名),
      mtime 不参与——调换裁决文件 mtime 结果不变;
    - 最新档损坏(不可解析/缺 overall)→ error='corrupt_latest',
      verdict=None——**不回退旧 PASS**;
    - revision 同号多档 → error='duplicate_revision'——冲突即阻断;
    - 全史保留: prior_verdicts=除最新外全档(含损坏档,如实披露)。

    Audit-R4 条目1 裁决损坏与缺字段不得放行(收紧):
    - 损坏档占其真实**写入位**,不降代——链尾新档(revision=3)截断后
      不得让旧 UPHELD(revision=2)回升为最新(裁决先后不因解析失败
      倒退,反例复现于基线 5fc5df8);
    - 有效档 revision 是写入序下的校验不变量: 同号=duplicate_revision,
      晚写位不递增=order_conflict(_verdict_write_positions_disagree);
    - 读取端逐档校验(_verdict_record_error): 必填字段/目标 run/
      合法裁决词/revision/predecessor;最新档 corrupt/invalid → 阻断
      (无法确认有效最新裁决);语义级违规任何写入位阻断;解析级损坏
      在非最新位=保留失败历史(record_health 披露),经有效复审
      (更高 revision 新档)可恢复交付;
    - record_health: 逐档健康面(relpath→问题描述),损坏历史如实可见。
    error 非空时 report 门 review_ok=False(阻断交付)。
    """
    layers = report.get('layers') or {}
    l3p = bool((layers.get('L3_AI推断层') or {}).get('produced'))
    l4p = bool((layers.get('L4_条件情景层') or {}).get('produced'))
    reasons = ((['l3_qualitative_inference'] if l3p else [])
               + (['l4_conditional_scenarios'] if l4p else []))
    state = {'required': bool(reasons), 'reasons': reasons,
             'seat_invoked': False, 'verdict': None, 'archive': None,
             'fresh': None, 'verdicts_n': 0, 'prior_verdicts': [],
             'record_health': {}, 'error': None}
    if not reasons:
        return state
    run_ts = (report.get('run') or {}).get('ts_utc') or ''
    if not run_ts:
        return state
    hits = _verdicts_for_run(root, run_ts)
    if not hits:
        return state
    keyed = sorted((_verdict_sort_key(p, v), p, v) for p, v in hits)
    state['verdicts_n'] = len(keyed)
    state['prior_verdicts'] = [os.path.relpath(p, root)
                               for _, p, _ in keyed[:-1]]
    _, latest_p, latest = keyed[-1]
    state['archive'] = os.path.relpath(latest_p, root)
    # ── 链级不变量: 写入序下有效档 revision 严格递增 ──
    conflict = _verdict_write_positions_disagree(keyed)
    if conflict:
        state.update(seat_invoked=True, verdict=None,
                     error=conflict.split(':')[0].strip(),
                     error_detail=conflict)
        return state
    # ── 逐档校验: 语义级违规任何位阻断;解析级损坏仅最新位阻断 ──
    ordered = [os.path.normpath(os.path.relpath(p, root))
               for _, p, _ in keyed]
    for _, p, v in keyed:
        err = _verdict_record_error(root, p, v, run_ts, ordered)
        if err:
            state['record_health'][os.path.relpath(p, root)] = err
            if p == latest_p or err.startswith('invalid_record'):
                state.update(
                    seat_invoked=True, verdict=None,
                    error=('corrupt_latest' if err.startswith('corrupt')
                           else err),
                    error_detail='%s @ %s' % (err, os.path.relpath(p, root)))
                return state
    # ── Audit-R5 条目4: 首位 legacy 档时代锚核验(删除 revision 冒充
    # legacy 的单档链: 锚若为现行 v3 口径=新格式档被降级,阻断;真 legacy
    # 档锚必为历史口径 v1/v2 且在当前内容上复配——无法核验(缺件)亦阻断
    for _, p, v in keyed:
        if isinstance(v, dict) and 'revision' not in v:
            era = _legacy_era_error(report_dir, v)
            if era:
                state['record_health'][os.path.relpath(p, root)] = era
                state.update(seat_invoked=True, verdict=None, error=era,
                             error_detail='%s @ %s'
                             % (era, os.path.relpath(p, root)))
                return state
            break
    state.update(seat_invoked=True, verdict=latest.get('overall'))
    bound = latest.get('content_sha256')
    if bound and report_dir:
        # Audit-R5 条目4: 摘要算法版本显式可验证——在场但非现行口径=
        # 绑定不可核验,fresh=False(缺失=历史档,锚与现行口径比对自然
        # 失效走 rebind 迁移;未知版本不获得更宽松权限)
        algo = latest.get('digest_algorithm')
        if algo is not None and algo != DIGEST_ALGORITHM_CURRENT:
            state['fresh'] = False
            state['fresh_note'] = ('digest_algorithm=%r 非现行口径'
                                   % (algo,))
        else:
            try:
                state['fresh'] = (content_digest(report_dir) == bound)
            except (OSError, ValueError):
                state['fresh'] = False
    elif bound:
        state['fresh'] = None   # 有绑定但无 report_dir 可核=不冒充新鲜
    # ── Audit-R23 任务1: 裁决↔地图内容段绑定——在场 MAP_REPORT.md 与
    # 裁决落档时的内容段摘要不符=地图被单改,旧裁决不得沿用(fresh=
    # False)。旧档无 map_report_sha256 键=历史面不追溯(内容摘要仍为
    # 主锚);绑定键在场且文件缺席=渲染面丢失,同样不冒充新鲜。 ──
    map_bound = latest.get('map_report_sha256')
    state['map_report_sha256'] = map_bound
    if map_bound:
        cur = map_report_content_sha(report_dir) if report_dir else None
        # Audit-R32 正式验收: 在场内容段与绑定仅差「分工」行审查状态短语
        # (裁决落档前=待裁,落档后 report 段翻新=已裁)=同一受审版本,不算
        # 改版;其余不符照旧 fresh=False。
        if not (cur and map_binding_matches(_read_map_text(report_dir),
                                            map_bound)):
            state['fresh'] = False
            state['fresh_note'] = (
                'MAP_REPORT.md 内容段摘要与裁决绑定不符(在场地图与受审'
                '版本不同——错误版本不得沿用旧裁决;cur=%s bound=%s)'
                % ((cur or '缺席')[:12], str(map_bound)[:12]))
    return state


def _atomic_write_text(path, text):
    """R36 Ni-3(R25 审计遗留): 临时文件+os.replace 单文件原子写。

    跨写中断(进程杀/磁盘满)=要么旧全文要么新全文,无半写撕裂视图;
    .tmp 落同目录保证与目标同文件系统(replace 原子性前提)。
    """
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(text)
    os.replace(tmp, path)


def _write_report(report_dir, report, rj_path):
    """report.json + report.md 同步落盘(两视图一原子语义)。

    R25 NIT V1-2(R24 审计): blocked 路径原先只写 json 不重渲 md——md/json
    失同步(旧 md 无门槛拦截记录)。任何改变 report 的路径(含 blocked)退出
    前都经本函数,两视图同步是 attach 的不变式。
    R36 Ni-3: 两文件各经 _atomic_write_text(先渲 md 后落盘,渲染异常时
    两文件都不动——旧视图完整保留,不产生 json 新/md 旧的中间态)。
    """
    import research_orchestrator as ro
    md_text = ro._render_md(report)
    _atomic_write_text(
        rj_path, json.dumps(report, ensure_ascii=False, indent=2,
                            default=str))
    _atomic_write_text(os.path.join(report_dir, 'report.md'), md_text)


def _new_attach_meta(prior, meta):
    """R36 Ni-2(R25 审计遗留): attach 元数据换代保真。

    原实现整 dict 替换——重 attach(修订后再提/拦截后重跑)会把上一轮
    attach 记录从报告面抹掉。现把上一轮压缩进 attach_history 追加链
    (attached/attached_at/judgment_file/schema_version/blocked +
    validation.passed/contract verdict 摘要),最近 5 轮封顶防无界。
    """
    out = dict(meta)
    if isinstance(prior, dict) and prior.get('attached_at'):
        rec = {}
        for k in ('attached', 'attached_at', 'judgment_file',
                  'schema_version', 'blocked'):
            if k in prior:
                rec[k] = prior[k]
        val = prior.get('validation')
        if isinstance(val, dict):
            rec['validation_passed'] = val.get('passed')
        cv = prior.get('contract_verification')
        if isinstance(cv, dict):
            rec['contract_verdict'] = cv.get('verdict')
        hist = list(prior.get('attach_history') or [])
        hist.append(rec)
        out['attach_history'] = hist[-5:]
    return out


# 引擎诚实拒答族(Audit-R5 条目2): envelope error kind 词表——这些失败
# 是"数据面如实缺席/不满足前提"的正确拒答,不是管线完整性缺陷,可按
# 可选降级面处理;词表之外/无信封/进程面失败=未知失败,不得自动归可选。
HONEST_REFUSAL_ERROR_KINDS = frozenset(
    {'no_series', 'insufficient_history', 'insufficient_candidates',
     'anchor_not_complete'})

# 阻断交付的数据门类目(Attach 旗标不可越过;仅 optional_data_missing
# 走显式降级路径)——attach/report/archive 同源引用。
BLOCKING_BLOCKED_CLASSES = frozenset(
    {'critical_zero_evidence', 'required_data_missing',
     'critical_step_failure', 'map_required_face_missing',
     'map_core_dimension_missing', 'map_anchor_coverage_insufficient',
     'map_core_dimension_stale', 'map_current_period_missing',
     'map_current_period_unverified', 'map_current_period_stale_mix',
     'map_official_target_missing',
     # Audit-R33 任务3: 原问直答型(被问分量全缺=草稿交付;分面块缺席)
     'policy_question_face_missing',
     'policy_question_faces_missing',
     # Audit-R33 任务5: 预期差——计划块缺席(硬);观点库缺席/无可对账行
     # (草稿级,plan 段缺口显式回传;交付/归档同源引用)
     'expectations_gap_block_missing',
     'expectations_gap_views_absent',
     'expectations_gap_no_comparables'})


def _step_failure_is_refusal(step):
    """失败步性质判定(Audit-R5 条目2): 诚实拒答=True(可降级面)。

    依据(按信任序): honest_refusal 豁免标记(编排层已判,如 S6 analog
    短历史拒答)> 信封 error.kind∈引擎拒答词表。其余(S10 自检失败/
    来源校验失败/进程失败/超时/未知 kind)=非拒答——关键步骤失败,
    不得自动归为可选缺失。
    """
    if step.get('honest_refusal'):
        return True
    env = step.get('envelope')
    err = env.get('error') if isinstance(env, dict) else None
    return bool(isinstance(err, dict)
                and err.get('kind') in HONEST_REFUSAL_ERROR_KINDS)


def blocked_class_of(report, calendar_path=None):
    """Audit-R4 条目5 + Audit-R5 条目2: 数据缺口/完整性分类唯一规范源
    (attach/report/archive 同源同判,不得各写一套口径)。

    进程成功、必要数据满足、数据质量合格**分别判断**——run_ok 不再
    一票豁免: 必要缺口与零证据在 run_ok=true 时同样阻断(反例 2A:
    history 正常退出+必要指标 n=1 曾误放行)。

    返回 None(无缺口)或:
      critical_zero_evidence  L1 事实行=0——任何旗标不放行;
      required_data_missing   冻结必要项 outcome∈{missing,
                             insufficient_coverage,stale_for_task}
                             (任务目标缺口;run_ok=true 亦阻断;
                             --allow-failed-run 只解 attach 层,交付层
                             仍拦;stale_for_task=R7-02 采集状态贯通
                             判定的数据过期,旧数据不冒充当前研究可用);
      critical_step_failure   run_ok=False 且存在**非诚实拒答**的失败步
                             (S10 自检/来源校验/关键步/进程/未知失败)
                             ——质量与完整性缺口,不得归可选降级;
      optional_data_missing   证据面在场、无必要缺口、失败步全部为诚实
                             拒答(源端缺席类)——显式旗标+充分披露+
                             有效独立审查后可交付。
    地图问句(run_ok=true 分支内)另有两级:
      map_required_face_missing    读者报告必需面缺席;
      map_core_dimension_missing   地区×维度组零 ok 格(R20);
      map_anchor_coverage_insufficient  组内 ok 锚<2 且空锚无经证实延误
                             依据(R21)——「仅存最新单点」不构成三时点对照
                             满足,与 Audit-R4 条目5 同纪律;
      map_current_period_missing   组内当期(最新一期)锚零 ok——他时点
                             ok 不补当期缺口(R27 任务1: 按所请求时间点
                             统计覆盖);计划无当期锚不判;
      map_current_period_unverified 组内当期 ok 锚全部未核验(决策序列
                             无更晚已证实决议且间隔超决策周期上限,
                             R27 任务1)——现值有效性无法核验;
      map_current_period_stale_mix 组内当期 ok 锚全为过期或未核验且
                             两类并存(R28 任务2 混合形态——单一类
                             判定各自遗漏)——混合缺口逐格点名;
      map_official_target_missing 问句指定官方政策目标而日历无政策
                             决议/维持实录条目、序列面决议/生效日亦
                             不可推(R28 任务2)——现值无官方口径可依,
                             不以市场序列值冒充宣布目标。
    原问直答型(question_kind=policy_question,Audit-R33 任务3)分面类:
      map_required_face_missing 判定缺总判断/结构化回声(必需面缺席);
      policy_question_face_missing 被问及的分量无证据可答(政策目标
                             缺证/通胀读数全缺)——交付草稿,正式归档
                             拒绝(判定与渲染共源 policy_question.
                             blocked_class);
      policy_question_faces_missing 分面块缺席/损坏。
    calendar_path=None 时政策实录面读模块默认日历(生产口径);显式
    传路径=测试注入缝(空日历=缺实录反例),生产调用不传。
    「存在最新单点」不构成历史分析需求满足(Audit-R4 条目5)——
    insufficient_coverage 与 missing 同为必要缺口。
    """
    l1_rows = len(((report.get('layers') or {}).get('L1_事实层') or {})
                  .get('rows') or [])
    req_missing = [
        i.get('metric_id') for i in
        (((report.get('run') or {}).get('data_requirements') or {})
         .get('items') or [])
        if i.get('tier') == 'required' and i.get('outcome')
        in ('missing', 'insufficient_coverage', 'stale_for_task')]
    if l1_rows == 0:
        return 'critical_zero_evidence'
    if req_missing:
        return 'required_data_missing'
    # Audit-R29 任务1(C2 实雷): 地图草稿类判定从 run_ok 门下提出——
    # 地图内容缺口(核心维度组/锚覆盖/当期/官方目标)是内容面不是进程
    # 面: TIPS_10Y 等源端诚实缺席把 run_ok 置 False 后,旧序整支跳过
    # → 缺核心维度的地图落 optional 放行归档(与 R20 起草稿合同相反)。
    # 非地图问句行为不变(仍走 run_ok→进程类);地图问句先判内容类,
    # 全绿且 run_ok=False 时照旧落 critical_step_failure/optional。
    if report.get('run_ok') is not False or \
            (report.get('research_plan') or {}).get('map_question'):
        # Audit-R18 任务4反例②③: 地图问句必需图表面(对照/走位/传导/
        # 转折×3/历史)缺席=读者交付件残缺——与必要数据缺口同级阻断
        # (faces 摘要在 attach 成功时随档;缺席=未 attach 或无面)
        _rp = report.get('research_plan') or {}
        if _rp.get('question_kind') == 'policy_question':
            # Audit-R33 任务3: 原问直答型——回声面缺席=必需面缺席;引擎
            # 分面缺口走 policy_question.blocked_class(判定与渲染共源);
            # 全绿时 run_ok 尾段与地图同口径(健康→None;诚实源缺席类
            # run_ok=False→落进程类旗标面)。
            _f = ((report.get('agent_judgment') or {})
                  .get('reader_map_faces')) or {}
            if not _f.get('complete'):
                return 'map_required_face_missing'
            import policy_question as _pq_bc
            _pqc = _pq_bc.blocked_class(_rp.get('policy_question'))
            if _pqc:
                return _pqc
            if report.get('run_ok') is not False:
                return None
        elif _rp.get('map_question'):
            _f = ((report.get('agent_judgment') or {})
                  .get('reader_map_faces')) or {}
            if not _f.get('complete'):
                return 'map_required_face_missing'
            # Audit-R20 任务1/任务5反例④: 12组(地区×维度)每组至少一格
            # ok——核心维度整组缺数=交付**草稿**,不进正式归档(用户指令:
            # 核心维度仍缺则交付草稿;数据面补齐后正例应 12/12 组全绿)。
            _pv = _rp.get('point_values') or {}
            _planned_pairs = {
                (_eco, _dim)
                for _eco, _rf in (_rp.get('regions') or {}).items()
                for _dim in ((_rf.get('dimensions') or {}) or {})}
            # Audit-R26 验收: 缺数/锚覆盖判定改走 research_map_planner
            # 共享实现(missing_core_groups/sparse_anchor_groups)——与
            # 首页草稿横幅同源同判,阻断与渲染不再两套口径。
            import research_map_planner as _rmp_grp
            if _rmp_grp.missing_core_groups(_pv, _planned_pairs):
                return 'map_core_dimension_missing'
            # Audit-R27 任务1: 必要维度**当期**缺数——按所请求时间点统计
            # 覆盖,同一时点多个指标不能替代另一个时点: 组内最新一期
            # 锚零 ok(他时点 ok 不补当期)→交付草稿;计划无当期锚(纯
            # 历史点问句)不判。判定与渲染共源(current_period_groups)。
            _has_cur_anchor = any(
                (a.get('months_before') or 0) == 0
                for a in (_rp.get('point_anchors') or []))
            _cur_r27 = _rmp_grp.current_period_groups(
                _pv, _planned_pairs,
                has_current_anchor=_has_cur_anchor)
            if _cur_r27['missing']:
                return 'map_current_period_missing'
            # Audit-R21 任务3反例③: 序列在场但一组仅剩最新单点(两个历史
            # 时点留空且无经证实延误依据)=锚覆盖不足——「存在最新单点」
            # 不构成三时点对照满足(与 Audit-R4 条目5 同纪律),交付草稿
            # 不进正式归档;经日历实录证实的延误缺口(停摆类)不算未证实。
            if _rmp_grp.sparse_anchor_groups(_pv, _planned_pairs):
                return 'map_anchor_coverage_insufficient'
            # Audit-R26 任务2: 必要维度**只剩确证过期值**——组内最新一期
            # ok 锚全部 freshness=stale(按统计期末/政策最后确认纪律确证),
            # 无任何当期有效读数: 交付草稿(报告首页明确标草稿),正式归档
            # 拒绝;组内任一非过期 ok 锚在场即不触发(过期格标注不改级)。
            # 判定与渲染共源(research_map_planner.stale_only_groups)。
            import research_map_planner as _rmp_st
            if _rmp_st.stale_only_groups(_pv, _planned_pairs):
                return 'map_core_dimension_stale'
            # Audit-R27 任务1: 必要维度当期值全部**无法核验**(无更晚已
            # 证实决议且无证实间隔超决策周期上限——本地日历未收录≠未
            # 发生,2024-06-06 ECB 决议复测锚)→交付草稿;判定与渲染共源。
            if _cur_r27['unverified']:
                return 'map_current_period_unverified'
            # Audit-R28 任务2: 必要维度当期只有**过期与未核验值的混合**
            # (单一类判定各自遗漏的混合形态: all-stale→R26 类/all-
            # unverified→R27 类,混合两不沾)→交付草稿并逐格点名缺口;
            # 判定与渲染共源(current_period_groups['stale_mix'])。
            if _cur_r27.get('stale_mix'):
                return 'map_current_period_stale_mix'
            # Audit-R28 任务2: **缺官方政策目标记录**——问句指定官方目标
            # (央行目标水平/距上次调整)而日历无政策决议/维持实录条目,
            # 序列面决议/生效日亦不可推: 现值无官方口径可依,不以市场
            # 序列值冒充宣布目标→交付草稿点名缺口;判定与渲染共源
            # (official_policy_record_face.gaps)。
            import research_map_planner as _rmp_opr
            _opr_g = _rmp_opr.official_policy_record_face(
                _pv, _planned_pairs, _rp.get('cutoff'),
                question=(report.get('run') or {}).get('question'),
                calendar_path=calendar_path)
            if _opr_g.get('gaps'):
                return 'map_official_target_missing'
            # Audit-R33 任务5: 问到预期差——块缺席(硬)/观点库缺席/
            # 无可对账行(草稿级);判定与渲染共源
            # (expectations_gap.plan_blocked_class,草稿横幅同源)。
            import expectations_gap as _eg_bc
            _eg_cls = _eg_bc.plan_blocked_class(report.get('research_plan') or {})
            if _eg_cls:
                return _eg_cls
        # 地图内容类全绿: run_ok 健康→无缺口;run_ok=False(诚实源缺席
        # 类)→落进程类旗标面(optional/critical),不放空手 None。
        if report.get('run_ok') is not False:
            return None
    non_refusal = [s.get('step') for s in (report.get('steps') or [])
                   if s.get('executed') and s.get('ok') is False
                   and not _step_failure_is_refusal(s)]
    if non_refusal:
        return 'critical_step_failure'
    return 'optional_data_missing'


def _reader_map_faces_summary(judgment, report):
    """Audit-R18: 地图问句判定五面粗检(完整判定=judgment_contract._map_checks)。

    返回 None=非地图问句;否则 {'complete', 粗粒度面计数}——complete=False
    时 blocked_class_of 判 map_required_face_missing(必需图表面缺席与
    必要数据缺口同级阻断)。"""
    plan = report.get('research_plan') or {}
    if plan.get('question_kind') == 'policy_question':
        # Audit-R33 任务3: 原问直答型粗检——总判断+结构化回声在场
        # (逐位核对归 judgment_contract._policy_question_checks)
        _rm = (judgment or {}).get('reader_map') or {}
        _echo = (_rm.get('policy_question')
                 if isinstance(_rm, dict) else None)
        _head = bool(isinstance(_rm, dict)
                      and str(_rm.get('headline_conclusion') or '').strip())
        _has = isinstance(_echo, dict)
        return {
            'complete': bool(_head and _has),
            'question_kind': 'policy_question',
            'headline': _head,
            'echo_present': _has,
            'official_targets_n': (len(_echo.get('official_targets') or [])
                                   if _has else 0),
            'pending_decisions_n': (len(_echo.get('pending_decisions')
                                     or []) if _has else 0),
            'inflation_yoy_n': (len(_echo.get('inflation_yoy') or [])
                                if _has else 0),
            'gaps_echoed_n': (len(_echo.get('gaps_echoed') or [])
                              if _has else 0),
        }
    if not plan.get('map_question'):
        return None
    rm = (judgment or {}).get('reader_map') or {}
    planned = set((plan.get('regions') or {}).keys())
    regions_ok = bool(planned) and planned.issubset(
        {r.get('region') for r in rm.get('regions') or []
         if isinstance(r, dict) and str(r.get('from_to') or '').strip()})
    turnings_n = len(rm.get('turnings') or [])
    history_n = len(rm.get('history_periods') or [])
    # R20 任务3: 历史类比 0..3 段;零段合法但须带零段注记(检索范围+原因)
    history_ok = (1 <= history_n <= 3
                  or (history_n == 0 and str(
                      rm.get('history_zero_case_note') or '').strip()))
    out = {
        'complete': bool(
            str(rm.get('headline_conclusion') or '').strip()
            and regions_ok
            and (rm.get('transmission') or [])
            and turnings_n == 3
            and history_ok),
        'headline': bool(str(rm.get('headline_conclusion') or '').strip()),
        'regions_ok': regions_ok,
        'transmission_chains': len(rm.get('transmission') or []),
        'turnings_n': turnings_n,
        'history_n': history_n,
    }
    # Audit-R33 任务5: 问到预期差才落回声面在场键(契约细查在
    # judgment_contract._expectations_gap_checks)
    _eg_plan = (report.get('research_plan') or {}).get('expectations_gap')
    if isinstance(_eg_plan, dict) and _eg_plan.get('asked'):
        out['expectations_gap_echo'] = isinstance(
            rm.get('expectations_gap'), dict)
    return out


class WorkOrderPinsError(ValueError):
    """Audit-R32 任务3: 工单冻结输入缺件/篡改(attach/report/archive 拒绝,
    fail-closed)。code ∈ {frozen_input_missing, frozen_input_tampered,
    frozen_input_unreadable}。"""

    def __init__(self, code, detail):
        super().__init__(f'{code}: {detail}')
        self.code = code
        self.detail = detail


_PIN_ENV_KEYS = ('IA_SNAPSHOT_PIN', 'IA_CALENDAR_PIN', 'IA_REGISTRY_PIN',
                 'IA_EVIDENCE_ASOF')


@contextlib.contextmanager
def work_order_pins(report_dir, root=None):
    """Audit-R32 任务3: 工单级冻结输入钉死(attach/report/archive/replay 共用)。

    读 <report_dir>/report.json 的 run.frozen_inputs {rel: sha16},逐件核对
    <report_dir>/root_overlay/<rel> 在场且 sha256[:16] 一致;不一致=缺件/
    篡改→WorkOrderPinsError(拒绝交付与归档,不回落引擎本地文件)。核对
    通过后,with 块内置位 IA_SNAPSHOT_PIN / IA_CALENDAR_PIN /
    IA_REGISTRY_PIN → overlay 内对应文件(快照=源快照,evidence_gate.
    source_snapshot_id 指名;as-of 版本快照只作版本依据不作钉死),并置位
    IA_EVIDENCE_ASOF=run.evidence_gate.as_of——同进程内任何日历/注册表/
    快照/取数读取都走本工单冻结字节(引擎本地日历被换不影响判定与重渲)。
    退出 with 恢复原 env(上游已钉死的键不覆盖=尊重上游)。
    legacy 档(无 frozen_inputs,R29 前)=不钉(零回归),yield info 如实记。
    yield info = {'pinned', 'legacy', 'files', 'calendar_path',
    'registry_path', 'snapshot_path', 'as_of', 'upstream_pins'}。"""
    root = root or ROOT
    info = {'pinned': False, 'legacy': False, 'files': {},
            'calendar_path': None, 'registry_path': None,
            'snapshot_path': None, 'as_of': None, 'upstream_pins': {}}
    rp = os.path.join(report_dir, 'report.json')
    if not os.path.isfile(rp):
        raise WorkOrderPinsError('frozen_input_missing',
                                 f'report.json 缺席: {report_dir}')
    rj = _load_json(rp)
    run = rj.get('run') or {}
    fi = run.get('frozen_inputs') or {}
    info['legacy'] = not fi
    saved = {k: os.environ.get(k) for k in _PIN_ENV_KEYS}
    set_keys = []
    try:
        if fi:
            _snaps = []
            for rel, sha in sorted(fi.items()):
                pth = os.path.join(report_dir, 'root_overlay', str(rel))
                if not os.path.isfile(pth):
                    raise WorkOrderPinsError(
                        'frozen_input_missing',
                        f'冻结输入缺件: root_overlay/{rel}(工单冻结面须随'
                        f'运行目录/交付包走,不得以引擎本地文件顶替)')
                try:
                    got = hashlib.sha256(open(pth, 'rb').read()).hexdigest()[:16]
                except OSError as exc:
                    raise WorkOrderPinsError('frozen_input_unreadable',
                                             f'root_overlay/{rel}: {exc}')
                if got != str(sha)[:16]:
                    raise WorkOrderPinsError(
                        'frozen_input_tampered',
                        f'冻结输入摘要不符: root_overlay/{rel} 期望 {sha} '
                        f'实测 {got}(运行后被改或包被篡改)')
                info['files'][rel] = got
                base = os.path.basename(str(rel))
                if base == 'release_calendar.json':
                    info['calendar_path'] = pth
                elif base == 'metric_registry.json':
                    info['registry_path'] = pth
                elif base.startswith('research_snapshot_'):
                    _snaps.append((rel, pth))
            _eg = run.get('evidence_gate') or {}
            _vrel = ((_eg.get('vintage') or {}).get('vintage_snapshot'))
            _src_id = _eg.get('source_snapshot_id')
            _pick = next((pth for rel, pth in _snaps
                          if _src_id and os.path.basename(str(rel))[:-5]
                          == str(_src_id)), None)
            if _pick is None:
                _pick = next((pth for rel, pth in _snaps
                              if str(rel) != str(_vrel)), None)
            if _pick is None and _snaps:
                _pick = max(_snaps, key=lambda x: x[0])[1]
            info['snapshot_path'] = _pick
            for k, pth in (('IA_SNAPSHOT_PIN', _pick),
                           ('IA_CALENDAR_PIN', info['calendar_path']),
                           ('IA_REGISTRY_PIN', info['registry_path'])):
                if not pth:
                    continue
                if os.environ.get(k):
                    info['upstream_pins'][k] = os.environ[k]
                    continue                      # 上游已钉死: 尊重
                os.environ[k] = pth
                set_keys.append(k)
            info['pinned'] = True
        _asof = ((run.get('evidence_gate') or {}).get('as_of')
                 if isinstance(run.get('evidence_gate'), dict) else None)
        if isinstance(_asof, str) and len(_asof) == 10:
            info['as_of'] = _asof
            if not os.environ.get('IA_EVIDENCE_ASOF'):
                os.environ['IA_EVIDENCE_ASOF'] = _asof
                set_keys.append('IA_EVIDENCE_ASOF')
        yield info
    finally:
        for k in set_keys:
            if saved.get(k) is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = saved[k]


def attach_judgment(report_dir, judgment_path, root=None,
                    allow_failed_run=False):
    """校验入口(Audit-R32 任务3): 工单冻结输入核对+钉死后落位。"""
    with work_order_pins(report_dir, root) as _pins:
        return _attach_judgment_pinned(report_dir, judgment_path, root,
                                       allow_failed_run, _pins)


def _attach_judgment_pinned(report_dir, judgment_path, root,
                            allow_failed_run, pins):
    """校验 Agent judgment 并合并进 research-run 报告(半落位=不落位)。

    校验通过: layers L3/L4 produced=True+attribution=ai_inferred+判断原文,
    judgment 副本存 <report_dir>/agent_judgment.json,report.md 重渲(含
    L3/L4 节);校验不过: produced 保持 False,violations 落档供 Agent 修订
    重提,绝不半落位。

    R23 审计 MINOR-4: run_ok=False 的 research-run 默认拒收 judgment——
    判断不得落在失败证据面之上(静默落位=L3/L4 produced=True 掩盖底座红)。
    显式 allow_failed_run=True 才放行(诚实拒答类步骤失败但证据面可用的
    场景;门槛显式越过=可审计)。返回摘要 dict(ia_cli 与测试共用)。
    """
    root = root or ROOT
    # Audit-R33 任务2 MINOR-4: 挂接步骤的代码版本随运行目录与回执落档
    _code_state = _attach_code_state(root)
    rj_path = os.path.join(report_dir, 'report.json')
    report = _load_json(rj_path)
    judgment = _load_json(judgment_path)

    # ── MINOR-4 门槛: 失败底座默认拒收(Audit-R1 F02 分级) ──────────
    # 规则运行前固定(与 plan 段 run.degradation_policy 同文,双写=互证);
    # Audit-R4 条目5 起分类唯一规范源=blocked_class_of(attach/report/
    # archive 同源同判),insufficient_coverage 与 missing 同为必要缺口:
    #   critical_zero_evidence: L1 事实行=0(引擎崩溃/全量采集失败)——
    #     判断无处可落,**任何旗标不得放行**(不用 --allow-failed-run 把
    #     关键失败自动变成成功);
    #   required_data_missing: 运行前冻结的必要指标(问题词面命中)采集
    #     缺席**或覆盖不足**(最新单点≠历史分析需求满足)——任务目标
    #     缺口,默认阻塞;显式 allow_failed_run 才放行并记 degraded
    #     (缺口随档,不得事后把必要改判可选=缩减任务目标);
    #   optional_data_missing: L1 事实面在场、失败步=诚实拒答类(如源端
    #     缺席 no_series)——须显式 allow_failed_run=True,落位记 degraded。
    run_ok = report.get('run_ok')
    blocked_class = blocked_class_of(
        report, calendar_path=(pins.get('calendar_path') or None))
    if run_ok is False and (blocked_class == 'critical_zero_evidence'
                            or not allow_failed_run):
        report['agent_judgment'] = _new_attach_meta(
            report.get('agent_judgment'),
            {
                'attached': False,
                'attached_at': _now_utc(),
                'judgment_file': os.path.basename(judgment_path),
                'schema_version': JUDGMENT_SCHEMA_VERSION,
                'blocked': 'run_ok_false',
                'blocked_class': blocked_class,
                'block_note': ('research-run run_ok=False——判断默认不得落在失败'
                               '证据面上;显式 allow_failed_run=True 只放行'
                               ' optional_data_missing(L1 证据面在场+诚实拒答类'
                               '失败);critical_zero_evidence 任何旗标不放行'
                               if blocked_class == 'critical_zero_evidence' else
                               'research-run run_ok=False——判断默认不得落在失败'
                               '证据面上;显式 allow_failed_run=True 才放行'
                               '(required_data_missing=必要指标缺席/覆盖不足的'
                               '任务目标缺口,critical_step_failure=关键步骤/'
                               '来源校验/未知失败,或 optional_data_missing='
                               '诚实拒答类失败且证据面仍可用,由 Agent 显式'
                               '声明并随档;交付层仍按 blocked_class 分级拦截)'),
                'run_ok_at_attach': run_ok,
                **_code_state,
            })
        # R33-①: blocked 面同样落席位状态键(L3 未落位→required=False,
        # 面键一致;不追溯旧档)
        report['semantic_review'] = _semantic_review_state(
            report, root, report_dir)
        # R25 NIT V1-2: blocked 路径同样重渲 md(拦截记录两视图同步)
        _write_report(report_dir, report, rj_path)
        return {'report_dir': report_dir,
                'attached': False,
                'blocked': 'run_ok_false',
                'blocked_class': blocked_class,
                'run_ok_at_attach': run_ok,
                **_code_state,
                'layers_summary': {
                    'L3_produced': (report.get('layers', {})
                                    .get('L3_AI推断层', {})
                                    .get('produced')),
                    'L4_produced': (report.get('layers', {})
                                    .get('L4_条件情景层', {})
                                    .get('produced'))}}

    ev_refs = {e.get('ref') for e in report.get('evidence_index') or []
               if e.get('ref')}
    mids = _registry_metric_ids(root)
    # Audit-R31 任务3: 决议-生效成对纪律启用——日历面取自运行树
    # (IA_CALENDAR_PIN 钉死在场时经 release_calendar 冻结副本,与
    # 运行/重放同源);无日历=规则按缺席不启用(零回归)。
    # Audit-R32 任务2: 断言时点=本工单研究截止日(run.evidence_asof,
    # 旧档回退 research_plan.cutoff)——政策核验按实体/断言时点/决议日/
    # 生效日四要素。
    _asof = ((report.get('run') or {}).get('evidence_asof')
             or (report.get('research_plan') or {}).get('cutoff'))
    _cal_path = (pins.get('calendar_path')
                 or os.path.join(root, 'config', 'release_calendar.json'))
    res = validate_judgment(
        judgment, ev_refs, mids,
        policy_events=collect_policy_events(_cal_path),
        as_of=_asof if isinstance(_asof, str) else None)

    # ── 阶段四钩子: 判定档 vs 自身证据面契约验证 ─────────────────────
    # 语义全在 research_contract/judgment_contract.py,此处仅挂载+门控:
    # 客观事实相左(CONTRADICTED)或未全证(NOT_VERIFIED)→拒落位,修档再提。
    try:
        from research_contract.judgment_contract import verify_judgment
        contract = verify_judgment(judgment, report)
    except Exception as exc:                        # 异常=如实降级,禁静默放行
        contract = {'verdict': 'NOT_VERIFIED', 'stats': {},
                    'error': f'{type(exc).__name__}: {exc}'}
    contract_ok = contract.get('verdict') == 'VERIFIED'

    layers = report.get('layers') or {}
    if res['passed'] and contract_ok:
        content = copy.deepcopy(judgment)
        for key, layer_key in (('l3', 'L3_AI推断层'), ('l4', 'L4_条件情景层')):
            layers[layer_key]['produced'] = True
            layers[layer_key]['attribution'] = 'ai_inferred'
            layers[layer_key]['content'] = content.get(key)
            layers[layer_key]['note'] = (
                'Agent(编排层)研判落位,attribution=ai_inferred;'
                '纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,'
                '判断质量归 Agent 与独立审计')
        # R36 Ni-3: 判定档副本同原子写(与 report.json 同级防撕裂)
        _atomic_write_text(
            os.path.join(report_dir, 'agent_judgment.json'),
            json.dumps(judgment, ensure_ascii=False, indent=2))
    else:
        # R23 MINOR-3(独立审计): 失败重提时清残留 content——
        # produced=False 与旧 content 并存=语义不一致
        for layer_key in ('L3_AI推断层', 'L4_条件情景层'):
            layers[layer_key]['produced'] = False
            layers[layer_key].pop('content', None)
            layers[layer_key].pop('attribution', None)

    report['layers'] = layers
    # R33-①: 席位状态面随档(确定性面零污染: 新增键,不动
    # steps/evidence_index/run;编排层读 required 自动唤席)
    report['semantic_review'] = _semantic_review_state(
        report, root, report_dir)
    report['agent_judgment'] = _new_attach_meta(
        report.get('agent_judgment'),
        {
            'attached': bool(res['passed'] and contract_ok),
            'attached_at': _now_utc(),
            'judgment_file': os.path.basename(judgment_path),
            'schema_version': JUDGMENT_SCHEMA_VERSION,
            'validation': res,
            'contract_verification': contract,   # 阶段四: 契约验证结果随档
            # MINOR-4: 落位时的底座状态随档(含 allow_failed_run 越过面)
            'run_ok_at_attach': run_ok,
            'allow_failed_run': bool(allow_failed_run and run_ok is False),
            **_code_state,
        })
    # Audit-R18: 地图问句 reader_map 面摘要随档(blocked_class_of 的
    # map_required_face_missing 判据源;深层结构/数值由 judgment_contract
    # _map_checks 在契约层拦,此处只落粗粒度面——attach 成功才有 complete)
    _faces = _reader_map_faces_summary(judgment, report)
    if _faces is not None:
        if res['passed'] and contract_ok:
            report['agent_judgment']['reader_map_faces'] = _faces
        else:
            report['agent_judgment']['reader_map_faces'] = dict(
                _faces, complete=False,
                note='attach 未成功——reader_map 面以缺席论(map_required_'
                     'face_missing 阻断交付/归档)')
    if res['passed'] and not contract_ok:    # 纪律绿但契约未全绿=契约门拦截
        report['agent_judgment']['blocked'] = \
            'contract_' + str(contract.get('verdict')).lower()
        report['agent_judgment']['block_note'] = (
            '判定档与证据面契约验证未全绿(客观事实相左/未全证)——'
            '修档再提;详见 contract_verification')
    _write_report(report_dir, report, rj_path)
    # Audit-R33 任务2补充: 契约门拒收理由随返回值——纪律绿而契约未全绿时
    # blocked=contract_<verdict>+block_note+contract_summary(裁决与计数,零判断
    # 原文)进返回值,CLI 回执据此可读(此前只落 report.json,回执 blocked 为空
    # 且 violations 为空=拒收无理由)。成功/纪律拒收两路返回值键形不变。
    return {'report_dir': report_dir,
            'attached': bool(res['passed'] and contract_ok),
            **({'blocked': report['agent_judgment']['blocked'],
                'block_note': report['agent_judgment'].get('block_note'),
                'contract_summary': {
                    k: contract[k] for k in ('verdict', 'stats', 'error')
                    if contract.get(k) is not None}}
               if res['passed'] and not contract_ok else {}),
            'validation': res,
            'contract_verification': contract,
            'semantic_review': report['semantic_review'],
            'run_ok_at_attach': run_ok,
            **_code_state,
            'layers_summary': {
                'L3_produced': layers['L3_AI推断层']['produced'],
                'L4_produced': layers['L4_条件情景层']['produced']}}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    import argparse
    p = argparse.ArgumentParser(
        description='Agent Native L3/L4 判断落位+纪律机器校验'
                    '(校验器零生成,内容归 Agent)')
    p.add_argument('--report-dir', required=True,
                   help='research-run 报告目录(含 report.json)')
    p.add_argument('--judgment', required=True,
                   help='Agent judgment JSON 文件(schema v1.1)')
    p.add_argument('--root', default=ROOT)
    a = p.parse_args(argv)
    res = attach_judgment(a.report_dir, a.judgment, root=a.root)
    print(json.dumps(res, ensure_ascii=False, indent=2, default=str))
    return 0 if res['attached'] else 1


if __name__ == '__main__':
    sys.exit(main())
