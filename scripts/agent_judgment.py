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
          写成当前值;实体词形不绑=不触发)
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
    可见日,供研究时点前的决议不参与判定)。

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
                      '后生效', '待实施', '即将生效')
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


def _judgment_text_segments(judgment):
    """判断文档内全部自然语言段(逐条带定位),POL-EFF 子串代理消费。"""
    segs = []

    def _walk(node, where):
        if isinstance(node, str):
            if node.strip():
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
        for where, text in _judgment_text_segments(judgment):
            if not any(w in text for w in _POL_EFF_WORDS):
                continue
            bound = _pol_bound_events(text, policy_events)
            if not bound:
                continue
            _pend = any(m in text for m in _POL_PENDING_MARKS)
            for ev in bound:
                # 公告在研究时点尚不可见的决议不参与判定(当时无从提及)
                if (_asof and ev.get('first_publish')
                        and ev['first_publish'] > _asof):
                    continue
                dec_in = any(f in text
                             for f in _date_word_forms(ev['decision_date']))
                eff_in = any(f in text
                             for f in _date_word_forms(ev['effective_on']))
                if not (dec_in or eff_in):
                    _ent = ev.get('entity')
                    _tv = ev.get('target_value')
                    # POL-EFF-PENDING-AS-CURRENT: 研究时点早于生效日,
                    # 段落写本实体政策目标=待生效目标值而无任何待生效/
                    # 将然标注、无决议/生效日期——把待生效值写成了当前值
                    if (_asof and _ent and _tv is not None
                            and _asof < ev['effective_on'] and not _pend
                            and any(w in text
                                    for w in _POL_ENTITY_WORDS.get(_ent, ()))
                            and _pol_value_in_text(_tv, text)
                            and any(w in text for w in _POL_EFF_WORDS)):
                        bad('POL-EFF-PENDING-AS-CURRENT', where,
                            '研究时点 %s 早于 %s 决议(%s)生效日 %s,正文'
                            '以当前口径写目标值 %s(=待生效值)而无待生效/'
                            '将然标注——待生效值不得写成当时已生效的官方'
                            '目标' % (_asof, ev['metric_id'],
                                      ev['decision_date'],
                                      ev['effective_on'], _tv))
                    continue
                _ddec, _deff = ev['decision_date'], ev['effective_on']
                lag = _pol_days(_ddec, _deff)
                _spec = []
                # POL-EFF-DATE: 正文写出的生效日≠官方实录且早于官方生效日
                # (落在[决议日,生效日)内)——「日期齐全但提前生效」。
                # 「生效」绑定到它所支配的那一个日期词元:
                #   标签前置(生效Y / 生效日Y / 生效于Y)→其后日期 Y;
                #   其余(日期前置 X生效)→其前日期词元(≤14 字、无相对词)。
                # 两向都不把成对表述里的决议日读成生效日:
                # 「9月18日决议,9月22日生效」(日期前置)与
                # 「决议9月18日(生效9月24日)」(标签前置)同判。
                _toks = _pol_date_tokens(text)
                _start_ix = {t[3]: _i for _i, t in enumerate(_toks)}
                for _m in re.finditer('生效', text):
                    _p = _m.start()
                    _gi = None
                    _nx = _POL_EFF_NEXT.match(text, _p + 2)
                    if _nx:
                        _gi = _start_ix.get(_nx.end())
                    if _gi is None:
                        for _i in range(len(_toks) - 1, -1, -1):
                            iso, mm, dd, st_i, endi = _toks[_i]
                            _nxt = (_toks[_i + 1][3] if _i + 1 < len(_toks)
                                    else len(text))
                            if not (endi <= _p
                                    and _p + 2 <= min(_nxt, endi + 14)):
                                continue
                            if any(rw in text[endi:_p]
                                   for rw in _POL_REL_CUT_WORDS):
                                break     # 相对生效词形另由 REL 判
                            _gi = _i
                            break
                    if _gi is None:
                        continue
                    iso, mm, dd, st_i, endi = _toks[_gi]
                    tok = iso or '%s-%02d-%02d' % (_ddec[:4], mm, dd)
                    if tok == _deff or tok == _ddec and _deff == _ddec:
                        continue
                    if tok == _ddec:
                        _spec.append(
                            '正文把 %s 决议日 %s 写成生效日——官方实录'
                            ' 生效日为 %s(决议→生效 %s 天),不得提前'
                            % (ev['metric_id'], _ddec, _deff, lag))
                    elif _ddec <= tok < _deff:
                        _spec.append(
                            '正文生效日 %s 与官方实录不符(早于官方生效日 '
                            '%s;决议日 %s)——%s 决议 %s 生效,不得提前'
                            % (tok, _deff, _ddec, ev['metric_id'], _deff))
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
                        m in text for m in ('待生效', '尚未生效', '未生效')):
                    # R31 成对纪律(原口径): 决议日提及须配生效日或待生效标注
                    bad('POL-EFF', where,
                        '提及决议日 %s(%s)但未配生效日 %s,亦无待生效标注——'
                        '决议与生效分记,次月末才生效不得写成当时已发生'
                        % (_ddec, ev['metric_id'], _deff))
                # POL-EFF-EARLY-CLAIM: 研究时点早于生效日,段落却以现行
                # 口径断言(已生效/现行/目前…)且无待生效/将然标注
                if (_asof and _asof < _deff and not _pend
                        and any(m in text for m in _POL_CURRENT_MARKS)):
                    bad('POL-EFF-EARLY-CLAIM', where,
                        '研究时点 %s 早于 %s 决议(%s)生效日 %s,正文以'
                        '现行/已生效口径断言而无待生效标注——断言时点'
                        '尚未生效' % (_asof, ev['metric_id'], _ddec, _deff))

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


def map_report_content_sha(report_dir):
    """Audit-R23 任务1: MAP_REPORT.md 内容段摘要(裁决↔地图绑定锚)。

    内容段=首个「## 语义审查」节之前的一切(对照表/走位/传导/转折/
    历史类比)——语义审查节在裁决落档后由「待裁」翻「已裁」,属状态面
    非内容面,排除在外使绑定在裁决前后稳定。文件缺席→None(非地图
    问句运行/未渲染,不绑)。
    """
    import hashlib
    p = os.path.join(report_dir or '', 'MAP_REPORT.md')
    try:
        with open(p, encoding='utf-8') as f:
            text = f.read()
    except (OSError, ValueError):
        return None
    return hashlib.sha256(
        text.split('\n## 语义审查')[0].encode('utf-8')).hexdigest()


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
        if cur != map_bound:
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
     'map_official_target_missing'})


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
        if _rp.get('map_question'):
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
    return {
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
    return {'report_dir': report_dir,
            'attached': bool(res['passed'] and contract_ok),
            'validation': res,
            'contract_verification': contract,
            'semantic_review': report['semantic_review'],
            'run_ok_at_attach': run_ok,
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
