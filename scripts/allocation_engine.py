#!/usr/bin/env python3
"""配置研究引擎 v4.0+第六轮最终可靠性补丁 (2026-10-12)

第六轮(正式版冻结前最终补丁,不改架构):
1. P0-1 观察写入与数据验证严格隔离: record_observations对目标/前提锚点做防御性
   校验(观测日缺失/不可解析/未来/超新鲜度窗一律不写入正式观察历史,不得以采集日
   替代实际观测日);观察器侧先过滤无效锚点再传入 — 双侧防线,其他调用路径无法绕过。
2. P0-2 条件预测到期封存: 终态预测加final标记(向后兼容迁移: 旧hit/miss/inconclusive
   记录自动补final;到期未触发终态在引擎落地时写入) — 每日观察任务不得重开终态预测,
   前提只能在有效期内激活(触发观测日须≤截止日,截止日不顺延);GLM不得翻案终态。
3. P0-3 expiry严格结算口径: 裁决只认预定义有效截止交易日(settlement_date,非交易日
   回溯)当日的观测,该日缺失→inconclusive,不得回退用前一交易日价格;GLM引用核验
   与引擎同一结算日(不得拿前一日满足值把inconclusive裁成hit)。

相对v3.0的修复(第四轮P0):
1. 连续观察周数按ISO year-week累计(P0-1): 同一ISO周重复运行最多贡献1个观察周
   (允许修正本周观察但不增加consec);跳周重置;unverifiable周不推进不重置;
   跨年ISO周正确处理;persist=False完全无副作用。
2. 证据方向切分与新增判定(P0-2): supporting/contrary/unexplained三分,反对证据
   不得计入支持数量;同一底层指标不同字段口径(value/prev/变化)按基底去重;
   评级变更门禁只认"本周新增独立支持证据"(旧值重引不算新增,对照证据台账判定)。
3. 5★语义修正(P0-5): 5★不要求存在反证——5项/3类/3期即可;存在未解释重大反证
   才封顶3★。台账分别记录支持/反对/未解释数量。
4. 预测观察与裁决强化(P0-6): 每日观察记录(幂等,含盘中高/低与数据来源);
   price_basis区分close/high/low口径 — 只有收盘价不得证明盘中未触及(缺→无法裁决);
   expiry按预定义有效截止交易日当日观测判定(第六轮P0-3严格化,无容差回退);
   定性预测GLM只能inconclusive研究回顾,不计入客观命中率(qualitative单列)。

相对v2.0的修复(第三轮P0):
1. 评级变更门禁: 模型提出的新评级不再直接写入 — 必须满足
   (a) 引擎核验为"已触发"的同向触发器,或 (b) ≥2项通过程序验证的新增结构化证据。
   不满足时保留原评级,候选提案记入 proposals 留档(含被拒原因),同向提案21天内去重。
2. 触发器v3: 支持 AND(all)/OR(any) 复合条件、sustain_weeks(连续N周)持续确认、
   首次跨越 vs 持续位于阈值之外的区分(连续计数); 观点库内持久化连续周数。
3. 证据分级v2程序化: ALLOCATION_STATUS可附 evidence[] (指标ID+数值+观测日+机制类别),
   程序逐项对照锚点验证(数值容差+观测日一致+逐指标新鲜度),同一底层指标只计一次;
   星级门槛: 1★1项/2★2项/3★3项且2类机制/4★4项且3类机制且2个观察期/
   5★5项且3类机制且3个观察期且反证已解释; 未解释重大反证封顶3★;
   观点key_metrics缺失时封顶2★。确信度上调不得超过程序星级,下调自由。
4. 预测全生命周期: 创建→前提触发(可程序判定的前提规格)→观察期开始(observe_from)
   →数据持续记录(observations按观测日去重)→到期/触及裁决→历史保存。
   verify_mode区分 touch(观察期内触及)与 expiry(截止日水平),二者不混。
   裁决只用观察窗内的观测(禁止窗口后未来数据); expiry未到期不得提前裁决;
   touch触及可提前判hit。前提至截止日未成立→未触发(终态,截止日不顺延)。
5. 裁决权威序: 引擎按观察记录的客观裁决 > GLM附证据裁决。GLM不得覆盖引擎已裁决
   的结果; GLM裁决引用的数值/观测日必须落在观察窗内且与记录吻合。

保留v2.0全部语义: 量表v2、五态、仅确信度变化落盘、无证据裁决拒收、FAIL门禁由调用方执行。
"""
import os
import sys
import re
import json
import shutil
from datetime import datetime, timedelta, date

import freshness_policy as _fp   # FIX1-01: 共享严格时点原语(无环)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_VIEWS_PATH = os.path.join(ROOT_DIR, 'config', 'allocation_views.json')

# ── 评级量表v2 ──────────────────────
ALLOWED_RATINGS = ['超配', '标配', '低配', '观望']
RATING_DEFINITIONS = {
    '超配': '相对理论基准上调(证据分级≥3★方可授予)',
    '标配': '与理论基准一致(即中性仓位,不表达方向倾斜)',
    '低配': '相对理论基准下调',
    '观望': '证据不足或处于触发边缘,暂不表达配置倾向(等待数据)',
}
RATING_RANK = {'低配': -1, '标配': 0, '超配': 1}  # 观望无序(暂停表态)

# ── 预测状态(五态) ──────────────────────
PRED_STATUSES = ['not_yet_triggered', 'observing', 'hit', 'miss', 'inconclusive']
PRED_STATUS_CN = {'not_yet_triggered': '未触发', 'observing': '观察中',
                  'hit': '已命中', 'miss': '已证伪', 'inconclusive': '无法裁决'}
ALLOWED_PRED_VERDICTS = {'hit', 'miss', 'inconclusive'}
VERIFY_MODES = {'touch', 'expiry'}
VERIFY_MODE_CN = {'touch': '观察期内触及', 'expiry': '截止日达到'}
# 价格口径(第四轮P0-6): close=收盘达到; high=盘中最高触及; low=盘中最低触及。
# 只有收盘数据时不得证明"盘中未触及"(判miss须有对应口径数据,缺→无法裁决)。
PRICE_BASES = {'close', 'high', 'low'}
PRICE_BASIS_CN = {'close': '收盘价', 'high': '盘中最高', 'low': '盘中最低'}
# (第六轮P0-3已移除截止日±4天容差: expiry只认预定义有效截止交易日当日观测,
#  结算日数据缺失→inconclusive,不得回退用前一交易日价格裁决)
_PRED_STATUS_MAP = {
    '命中': 'hit', '已命中': 'hit', '验证': 'hit',
    '证伪': 'miss', '已证伪': 'miss', '落空': 'miss', '未命中': 'miss',
    '无法裁决': 'inconclusive', '待定': 'inconclusive', 'inconclusive': 'inconclusive',
    '未触发': 'not_yet_triggered', 'not_yet_triggered': 'not_yet_triggered',
    '观察中': 'observing', '观察': 'observing', '延续': 'observing',
    'open': 'observing',          # v1迁移
    'expired': 'inconclusive',    # v1迁移
}

COMPARATORS = {
    '>=': lambda a, b: a >= b,
    '<=': lambda a, b: a <= b,
    '>': lambda a, b: a > b,
    '<': lambda a, b: a < b,
    '==': lambda a, b: abs(a - b) < 1e-9,
}

# ── 证据机制类别(第三轮P0-3): 每项证据须归入一类,星级按类别覆盖度计 ──────────────
MECHANISM_CATEGORIES = ['增长', '通胀', '利率与流动性', '信用', '避险与估值', '供应与库存', '资金流']
# 指标→默认机制类别(证据项可显式给mechanism覆盖; 未知类别按此表回退,再不行归'增长')
METRIC_MECHANISM = [
    (r'CCC|HY|OAS|信用', '信用'),
    (r'TIPS|UST|rate|RATE|联邦基金|2Y|5Y|10Y|30Y', '利率与流动性'),
    (r'CPI|BEI|通胀|PCE', '通胀'),
    (r'GOLD|VIX|金银', '避险与估值'),
    (r'WTI|原油|油|库存|EIA', '供应与库存'),
    (r'BTC|DXY|美元|资金|流入|流出|稳定币', '资金流'),
    (r'SPX|NASDAQ|失业|UNRATE|就业|非农|PMI|GDP|零售|信心|SENT|上证|CSI|全A', '增长'),
]


def mechanism_of(metric, claimed=None):
    """证据项的机制类别: 显式声明优先(须在允许清单内),否则按指标ID推断。"""
    if claimed in MECHANISM_CATEGORIES:
        return claimed
    for pat, cat in METRIC_MECHANISM:
        if re.search(pat, str(metric)):
            return cat
    return '增长'


# 星级门槛: (星级, 最少独立支持证据, 最少机制类别, 最少观察期)
# 第四轮P0-5修正: 5★不要求"必须存在反证"——是"存在重大反证时须已解释"(未解释封顶3★),
# 无重大反证时满足5项/3类/3期即可授予5★。
STAR_RULES = [
    (5, 5, 3, 3),
    (4, 4, 3, 2),
    (3, 3, 2, 1),
    (2, 2, 1, 1),
    (1, 1, 1, 1),
]
MAX_STAR_UNEXPLAINED_COUNTER = 3   # 存在未解释重大反证 → 封顶3★
MAX_STAR_KEY_EVIDENCE_MISSING = 2  # 观点关键证据缺失 → 封顶2★(不得授予正式评级)
MIN_EVIDENCE_FOR_RATING_CHANGE = 2  # 无触发器时,评级变更所需最少独立"新增支持"证据

# 同向被拒提案的去重窗口(天): 期间重复提交只累计repeat,不新增条目
PROPOSAL_DEDUP_DAYS = 21


def _migrate_views(data):
    """v1/v2→v3就地迁移: 中性→标配、旧状态映射、预测补全新生命周期字段。返回是否改动。"""
    changed = False
    for v in data.get('views', []):
        if v.get('rating') == '中性':
            v['rating'] = '标配'
            changed = True
    if '中性' in (data.get('ratings_scale') or []):
        data['ratings_scale'] = list(ALLOWED_RATINGS)
        changed = True
    for p in data.get('predictions', []):
        if p.get('status') in ('open', 'expired'):
            p['status'] = _PRED_STATUS_MAP[p['status']]
            changed = True
        if 'verify_mode' not in p:
            p['verify_mode'] = 'expiry'          # v2及以前一律按截止日水平裁决
            changed = True
        if 'observations' not in p:
            p['observations'] = []               # 观察期数据持续记录
            changed = True
        if 'data_source' not in p:
            p['data_source'] = 'anchors'
            changed = True
        # 第六轮P0-2向后兼容: 旧终态预测(hit/miss/inconclusive)补final标记 —
        # 不改变任何既有字段,只加布尔标记,旧JSON可无损升级
        if p.get('status') in ('hit', 'miss', 'inconclusive') and 'final' not in p:
            p['final'] = True
            changed = True
    return changed


def load_views(views_path=None):
    path = views_path or DEFAULT_VIEWS_PATH
    if not os.path.exists(path):
        print(f"⚠️ 观点库不存在: {path}")
        return None
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    _migrate_views(data)  # 读侧归一,不落盘(写侧update时才持久化)
    return data


def due_predictions(views_data, today_str=None):
    """已过deadline仍处于 未触发/观察中 的预测 → 周报须在本期给出裁决(或由引擎自动裁决)"""
    today = today_str or datetime.now().strftime('%Y-%m-%d')
    return [p for p in views_data.get('predictions', [])
            if p.get('status') in ('open', 'observing', 'not_yet_triggered')
            and p.get('deadline', '9999-99-99') <= today]


# ════════════════════════════════════════════════════════════════════
# 触发器核验 v3: 单指标/复合(all|any)/持续(sustain_weeks)/首次跨越
# ════════════════════════════════════════════════════════════════════
def _eval_condition(cond, anchors):
    """单个条件 {metric, op, target} → triggered/not_triggered/unverifiable (+详情)"""
    metric, op, target = cond.get('metric'), cond.get('op'), cond.get('target')
    if metric in (None, '') or op not in COMPARATORS or not isinstance(target, (int, float)):
        return 'unverifiable', f"{metric or '?'} 不可量化"
    info = (anchors or {}).get(metric)
    if not (info and isinstance(info.get('value'), (int, float))):
        return 'unverifiable', f"{metric} 无当日锚点"
    val = float(info['value'])
    fired = COMPARATORS[op](val, float(target))
    detail = f"{metric}={val:g}{cond.get('unit', '')} {op} {target:g}" \
             f"({'✅满足' if fired else '⬜未满足'},观测日{info.get('obs_date', '?')})"
    return ('triggered' if fired else 'not_triggered'), detail


def _eval_condition_set(t, anchors):
    """触发器条件集: 单指标 / all(且) / any(或) → (fired_this_week状态, 详情)。
    复合逻辑: any→任一满足即满足; all→全部满足才满足,任一明确不满足即不满足;
    其余(无可核验数据)→待验证。"""
    if isinstance(t.get('all'), list) and t['all']:
        subs = [_eval_condition(c, anchors) for c in t['all']]
        details = ' 且 '.join(s[1] for s in subs)
        if any(s[0] == 'not_triggered' for s in subs):
            return 'not_triggered', details
        if all(s[0] == 'triggered' for s in subs):
            return 'triggered', details
        return 'unverifiable', details
    if isinstance(t.get('any'), list) and t['any']:
        subs = [_eval_condition(c, anchors) for c in t['any']]
        details = ' 或 '.join(s[1] for s in subs)
        if any(s[0] == 'triggered' for s in subs):
            return 'triggered', details
        if all(s[0] == 'not_triggered' for s in subs):
            return 'not_triggered', details
        return 'unverifiable', details
    return _eval_condition(t, anchors)


def _iso(d):
    return str(d)[:10]


def _iso_week_key(d):
    """观察周标识: ISO year-week 元组 (year, week)。跨年正确(12月末/1月初按ISO周归属年)。"""
    try:
        dt = date.fromisoformat(_iso(d))
        y, w, _ = dt.isocalendar()
        return (y, w)
    except ValueError:
        return None


def _prev_iso_week(yw):
    """上一个ISO周(跨年正确): 2027-W01 的上一周是 2026-W53(或W52,按ISO日历)。"""
    y, w = yw
    if w > 1:
        return (y, w - 1)
    return (y - 1, date(y - 1, 12, 28).isocalendar()[1])


def _consec_days_gap(d1, d2):
    try:
        return abs((date.fromisoformat(_iso(d1)) - date.fromisoformat(_iso(d2))).days)
    except ValueError:
        return 999


def evaluate_quant_triggers(views_data, anchors, today_str=None, persist=False):
    """对每个view.quant_triggers逐条核验(第四轮P0-1: ISO年-周为唯一观察周标识)。

    - 复合/持续条件支持 all/any/sustain_weeks
    - 连续周数按ISO year-week累计: 同一ISO周无论运行多少次最多贡献1个观察周
      (重复运行允许修正本周观察结果,但不增加consec);
      仅当本次评估周恰为存储周(last_week)的下一个ISO周时consec+1;
      跳周(中间观察周缺失)或首次→重置为1(首次跨越); 条件明确不满足→清零。
    - 无可核验数据(unverifiable)的周不推进也不重置状态(数据缺失≠条件失效)。
    - trigger_state[trig_id] = {consec, last_week, last_eval};
      persist=True 写回(更新路径), persist=False 完全无副作用(渲染路径)。
    返回 {view_id: [ {trig_id, direction, status, detail, consec, sustain} ]},
    status ∈ triggered/not_triggered/unverifiable/sustaining(持续确认中)。"""
    today_iso = _iso(today_str or datetime.now().strftime('%Y-%m-%d'))
    wk = _iso_week_key(today_iso)
    results = {}
    for v in views_data.get('views', []):
        rows = []
        st = v.setdefault('trigger_state', {}) if persist else dict(v.get('trigger_state') or {})
        for t in v.get('quant_triggers', []) or []:
            trig_id = t.get('trig_id', '?')
            fired, detail = _eval_condition_set(t, anchors)
            sustain = int(t.get('sustain_weeks') or 0)
            rec = st.get(trig_id) or {}
            consec = int(rec.get('consec', 0))
            state_changed = False
            if fired == 'unverifiable':
                pass  # 数据缺失: 不推进不重置(上周状态原样参与展示)
            elif fired == 'not_triggered':
                if consec != 0:
                    consec = 0
                    state_changed = True
            else:  # triggered
                last_wk = rec.get('last_week')
                if last_wk is None and rec.get('last_eval'):
                    last_wk = _iso_week_key(rec['last_eval'])  # v3状态迁移: 由上次评估日推观察周
                if isinstance(last_wk, list):
                    last_wk = tuple(last_wk)
                if last_wk is not None and last_wk == wk:
                    pass  # 同一ISO周重复运行: 修正本周观察,不增加连续周数
                elif last_wk is not None and last_wk == _prev_iso_week(wk):
                    consec += 1
                    state_changed = True
                else:
                    consec = 1  # 首次跨越或跳周(中间观察周缺失)→重新起算
                    state_changed = True
            if persist and (fired != 'unverifiable'):
                st[trig_id] = {'consec': consec, 'last_week': list(wk) if wk else None,
                               'last_eval': today_iso}
            if fired == 'unverifiable':
                status = 'unverifiable'
            elif fired == 'triggered' and sustain and consec < sustain:
                status = 'sustaining'   # 已满足但未满连续N周 → 待确认,不得当已触发
            elif fired == 'triggered':
                status = 'triggered'
            else:
                status = 'not_triggered'
            tag_sustain = f",连续第{consec}/{sustain}周" if sustain else ''
            first = ',首次跨越' if consec == 1 and fired == 'triggered' else ''
            rows.append({'trig_id': trig_id, 'direction': t.get('direction', '?'),
                         'status': status, 'detail': f"{detail}{tag_sustain}{first}",
                         'consec': consec, 'sustain': sustain})
        results[v['id']] = rows
    return results


# ════════════════════════════════════════════════════════════════════
# 证据分级v2程序校验(第三轮P0-3)
# ════════════════════════════════════════════════════════════════════
def _value_close(claimed, anchor_val):
    """证据数值与锚点比对: 相对0.2%或绝对0.005取大; 兼容bp/百分比形态(1229↔12.29)。"""
    if not isinstance(claimed, (int, float)) or not isinstance(anchor_val, (int, float)):
        return False
    a, b = float(claimed), float(anchor_val)
    cands = [a]
    if a > 60 and abs(b) < 20:
        cands.append(a / 100.0)   # bp形态
    tol = max(abs(b) * 0.002, 0.005)
    return any(abs(c - b) <= tol for c in cands)


def _as_of_mode(as_of_date):
    """W2-FIX5-02(DEF-002): as_of存在性与合法性三态判定——
      'diagnostic': as_of_date is None(调用方未提供→受限诊断路径,DIAGNOSTIC_ONLY);
      'formal'    : 显式提供的合法研究截止(date/datetime实例/完整ISO日期/
                    完整ISO时间戳;同一套fp.parse_instant严格解析,无第二标准);
      'invalid'   : 显式提供的非法值——''/纯空白/0/False/[]/{}/带后缀
                    ('2026-10-24INVALID')/非法日历('2026-13-01')/非法时刻
                    ('2026-10-24T25:00:00')等一律拒收,**绝不因falsy被当成
                    None落入诊断兼容路径**(旧真值判断`if as_of_date`的缺陷)。"""
    if as_of_date is None:
        return 'diagnostic'
    if isinstance(as_of_date, (date, datetime)):
        return 'formal'
    if isinstance(as_of_date, str) and _fp.parse_instant(as_of_date) is not None:
        return 'formal'
    return 'invalid'


def verify_evidence_items(items, anchors, as_of_date=None):
    """逐项验证结构化证据 [{metric, value, obs_date, mechanism?, contrary?, explained?, neutral?}]。

    验证内容: 指标存在于锚点 / 锚点身份/来源家族合法 / 数值吻合 / 观测日必须与
    锚点观测日一致(采集日as_of不得替代观测日,第四轮P0-3) / 研究截止合法 /
    逐指标新鲜度(过期不得作当前证据) / 点时判断(发布已知时)。
    neutral=true(或stance=neutral)表示"相关但不能直接支持方向": 数值真实性照常
    验证,但不计入支持证据数量(第四轮P0-2)。
    返回 (verified, rejects): verified为通过项(同指标去重后仍全部保留,计数时按
    distinct metric),rejects为(原因, 原始项)列表。anchors为空→全部拒(无锚点即无证据)。
    W2-FIX4: 每项verified附结构化时间资格{observation_freshness, point_in_time
    {status,granularity,release_date,reason}, point_in_time_certified}——数值/观测
    核验通过与点时认证分离: 已知发布晚于截止→整项拒收;精度不足未证明→保留为
    观测层证据并如实标注POINT_IN_TIME_UNCERTIFIED,永不计入"已证实截止时可得";
    缺release_date→RELEASE_UNKNOWN(历史兼容,不伪造认证);未提供as_of(诊断路径)
    →AS_OF_UNKNOWN且不授予认证,observation_freshness=NOT_ASSESSED
    (W2-FIX6-01: 诊断模式未评估观测时效,未知≠新鲜≠过期,不得claim FRESH);
    时间校验模块不可用→fail-closed拒收。
    W2-FIX5(DEF-002): as_of_date用存在性判断(is None)区分——None=受限诊断路径
    (DIAGNOSTIC_ONLY,不做时效门禁但**身份核验照常**);''/0/False/[]/{}/纯空白/
    非法后缀/非法日历等显式非法值一律整项拒收,绝不因falsy被吞成诊断路径。
    W2-FIX5(DEF-001): 正式路径消费**综合证据资格**(evidence_eligibility.usable)
    ——纯观测FRESH但已知未来发布仍整项拒(NOT_AVAILABLE_AT_AS_OF),观测新鲜与
    点时可得/证据资格三维度不得相互冒充。"""
    verified, rejects = [], []
    if not isinstance(items, list):
        return verified, rejects
    for it in items:
        if not isinstance(it, dict):
            rejects.append(('证据项格式错误(非对象)', it))
            continue
        metric = it.get('metric')
        info = (anchors or {}).get(metric)
        if not metric or not info:
            rejects.append((f"指标{metric}不在锚点中(虚构证据嫌疑)", it))
            continue
        # W2-FIX5-02/03步骤2: as_of存在性与合法性先行(DEF-002)——None=受限诊断
        # 路径;其余显式值必须合法,非法即整项拒收(先于身份核验: 截止非法时
        # 一切时间资格无从谈起,rejects必须含非法研究截止原因,不得落入诊断
        # 兼容路径,也不得跳过拒收借道获得任何认证)。
        mode = _as_of_mode(as_of_date)
        tq = None
        if mode == 'invalid':
            rejects.append((f"{metric}研究截止非法({as_of_date!r}),显式非法输入"
                            "不得进入诊断兼容路径,不得核验为正式证据", it))
            continue
        if mode == 'formal':
            # 结构化时间资格(身份/纯观测/点时/综合资格)经dv共享适配接口一次
            # 取齐(复用fp共享原语,不新建第二套比较器);锚点身份/来源家族合法
            # 性先于数值比对——身份不可认证的引用连数值比对资格都没有
            tq = _anchor_time_qualification(metric, info, as_of_date)
            if tq is None:
                rejects.append((f"{metric}时间校验模块不可用,fail-closed不得核验为正式证据", it))
                continue
            if tq['identity']['status'] != 'MAPPED':
                rejects.append((f"{metric}锚点身份不可认证({tq['identity']['status']}:"
                                f"{tq['point_in_time']['reason']}),不得作正式证据", it))
                continue
        else:
            # 受限诊断路径(as_of=None,DIAGNOSTIC_ONLY): 不做时效门禁,但身份/
            # 来源家族核验照常(W2-FIX5-03)——不能因缺研究截止接受跨来源伪装
            ident = _fp.verify_anchor_identity(metric, info)
            if ident['status'] != 'MAPPED':
                rejects.append((f"{metric}锚点身份不可认证({ident['status']}:"
                                f"{ident['basis']}"
                                + (f";{ident['conflict']}" if ident.get('conflict') else '')
                                + "),诊断模式同样不得作正式证据", it))
                continue
        if not _value_close(it.get('value'), info.get('value')):
            rejects.append((f"{metric}数值不符(报告{it.get('value')} vs 锚点{info.get('value')})", it))
            continue
        obs = str(info.get('obs_date') or '')[:10]
        as_of = str(info.get('as_of') or '')[:10]
        # FIX1-01(IA-P02-W2-DEF-001): 证据与锚点日期严格解析——'2026-10-23INVALID'
        # 不得经[:10]截断洗白后当合法观测日通过(整串先验证;合法形态=完整ISO日期
        # 或完整时间戳取日期)。证据obs_date为模型声明字段,缺失/不可解析整项拒收
        # (第五轮P0-3既有语义,此处堵住截断洗白绕道)。
        obs_d = _fp.parse_instant(info.get('obs_date'))
        as_of_d = _fp.parse_instant(info.get('as_of'))
        obs = obs_d.isoformat() if obs_d else None
        as_of = as_of_d.isoformat() if as_of_d else None
        claimed_raw = it.get('obs_date')
        claimed_d = _fp.parse_instant(claimed_raw) if claimed_raw not in (None, '') else None
        claimed_obs = claimed_d.isoformat() if claimed_d else None
        # 第五轮P0-3: 观测日为必填(metric+value+obs_date三项缺一不可) —
        # 缺失/不可解析的证据整项拒收,不得省略后由程序以锚点观测日补全
        # (锚点数值核对是程序责任,日期引用是模型责任;as_of采集日不得替代obs_date)
        if claimed_raw in (None, ''):
            rejects.append((f"{metric}证据缺obs_date(观测日必填,缺失不得参与评级/星级)", it))
            continue
        if claimed_obs is None:
            rejects.append((f"{metric}证据obs_date不可解析('{claimed_raw}';须完整ISO日期,"
                            f"不得带后缀)", it))
            continue
        if not obs:
            rejects.append((f"{metric}锚点无有效观测日(缺失或不可解析),证据无法对齐", it))
            continue
        if claimed_obs != obs:
            rejects.append((f"{metric}观测日不符(引用{claimed_obs} vs 锚点{obs};"
                            f"采集日as_of不得替代经济观测日)", it))
            continue
        # W2-FIX5-04步骤5-7: 研究截止合法→**综合证据资格**(evidence_eligibility)
        # 门禁——纯观测维度(fresh)只描述观测新鲜,绝不单独放行: 观测FRESH但已知
        # 未来发布(NOT_AVAILABLE_AT_AS_OF)仍整项拒;拒收原因按综合状态如实分流
        # (未来发布≠数据过期,不得误导性归因)
        if tq is not None:
            el = tq['evidence_eligibility']
            if not el['usable']:
                st = el['status']
                if st == 'NOT_AVAILABLE_AT_AS_OF':
                    rejects.append((f"{metric}点时不可得:已知发布"
                                    f"{tq['point_in_time']['release_date']}晚于研究截止"
                                    f"{as_of_date}({tq['point_in_time']['reason']})"
                                    f"——as_of时点该值不可得,不得作当前证据", it))
                elif st == 'FUTURE_DATE':
                    rejects.append((f"{metric}观测日{obs}晚于研究截止{as_of_date}(未来数据),不得使用", it))
                elif st == 'STALE':
                    of = tq['observation_freshness']
                    rejects.append((f"{metric}数据过期(观测日{obs},滞后{of['lag_days']}>"
                                    f"{of['window']}天已批准窗),不得作为当前有效证据", it))
                elif st == 'INVALID_DATE':
                    rejects.append((f"{metric}研究截止非法('{as_of_date}'),无法认证时效", it))
                else:
                    rejects.append((f"{metric}时间资格不成立({st}:"
                                    f"{el['reason']}),不得作当前证据", it))
                continue
            pit, certified = tq['point_in_time'], tq['point_in_time_certified']
            # 正式路径: 纯观测时效已真实计算(usable⇒纯观测必为FRESH),如实携带
            obs_fresh_status = 'FRESH'
        else:
            # 受限诊断路径(未提供研究截止as_of,DIAGNOSTIC_ONLY): 不做时效门禁
            # (既有语义);但绝不默认授予点时认证——截止未定,认证无从谈起
            # (W2-FIX4-02);诊断结论不得claim任何形式时效认证(W2-FIX5-03)
            pit = {'status': 'AS_OF_UNKNOWN', 'granularity': None,
                   'release_date': info.get('release_date'),
                   'reason': 'DIAGNOSTIC_ONLY: 未提供研究截止(as_of),无法验证'
                             '观测新鲜度及点时可得性——仅数值/观测对齐+身份核验,'
                             '不做时效门禁,不授予任何时效认证,不得作为已认证正式'
                             '证据;verified.as_of仅为锚点元数据透传,非正式研究截止'}
            certified = False
            # W2-FIX6-01(IA-P02-W2-FIX5-DEF-001): 观测时效在诊断模式下**未评估**
            # ——不得写FRESH(未计算不得claim新鲜),亦不得写STALE(未知≠过期)
            obs_fresh_status = 'NOT_ASSESSED'
        neutral = bool(it.get('neutral')) or str(it.get('stance', '')).lower() == 'neutral'
        # W2-FIX4-01/02步骤8: 结构化时间资格随verified传递——数值/观测核验
        # (进入verified即已通过)与点时认证两维度分离;未认证项按观测层证据
        # 参与下游计数,但永不计入"已证实研究截止时可得",下游按
        # point_in_time_certified区分,缺失字段按False(不推定已认证);
        # 诊断模式observation_freshness=NOT_ASSESSED(W2-FIX6-01: 未知≠新鲜≠过期)
        verified.append({'metric': metric, 'value': float(info['value']),
                         'obs_date': obs, 'as_of': as_of,
                         'mechanism': mechanism_of(metric, it.get('mechanism')),
                         'contrary': bool(it.get('contrary')),
                         'explained': bool(it.get('explained')),
                         'neutral': neutral,
                         'observation_freshness': obs_fresh_status,
                         'point_in_time': dict(pit),
                         'point_in_time_certified': certified})
    return verified, rejects


def _anchor_time_qualification(metric, info, as_of_date):
    """经dv共享适配接口取锚点结构化时间资格(W2-FIX4-02):
    身份/观测新鲜度/点时认证三段一次取齐,复用fp共享原语,不新建比较器。
    时间校验模块不可用→None(fail-closed: 校验缺席不得授权正式证据)。"""
    try:
        from data_validator import anchor_time_qualification
    except ImportError:
        return None
    return anchor_time_qualification(metric, info, as_of_date)


def _anchor_fresh(metric, info, as_of_date):
    """W2-FIX4-02: 时间校验模块不可用时fail-closed——旧ImportError分支返回
    True会在校验缺席时把证据静默放行为"已核验",废除;不可用即不新鲜(拒)。"""
    try:
        from data_validator import is_fresh_anchor
    except ImportError:
        return False
    return is_fresh_anchor(metric, info, as_of_date)


def _obs_period_bucket(obs_date):
    """观察期桶: 观测日所在ISO周(同周重复引用同一月度值只算一个观察期)。"""
    try:
        d = date.fromisoformat(_iso(obs_date))
        y, w, _ = d.isocalendar()
        return f"{y}W{w:02d}"
    except ValueError:
        return str(obs_date)


# 指标的数值字段后缀: 同一底层指标的不同字段(value/prev/各变化口径)不构成独立证据
_METRIC_FIELD_SUFFIXES = {'value', 'prev', 'close', 'high', 'low', 'change', 'pct_change',
                          'week_chg', 'mom_chg', 'yoy_chg', 'mom_pct', 'yoy_pct', 'week_pct',
                          'chg'}


def _base_metric(metric):
    """底层指标身份: 剥离末位数值字段后缀。macro.data.CCC_OAS.value 与 .prev 同基底。"""
    m = str(metric)
    base, _, last = m.rpartition('.')
    if last in _METRIC_FIELD_SUFFIXES and base:
        return base
    return m


def split_evidence_direction(verified_items):
    """按方向切分已验证证据(第四轮P0-2):
    supporting=非反证且非中立项; contrary=反证项(再分已解释/未解释);
    中立项(相关但不能直接支持方向)经验证但不计入支持数量。
    反对证据与中立项都不得计入支持证据数量 — 星级、评级门禁与新增判定只用supporting。"""
    supporting = [i for i in verified_items if not i.get('contrary') and not i.get('neutral')]
    contrary = [i for i in verified_items if i.get('contrary')]
    unexplained = [i for i in contrary if not i.get('explained')]
    neutral = [i for i in verified_items if i.get('neutral') and not i.get('contrary')]
    return supporting, contrary, unexplained, neutral


def uncertified_note(items):
    """W2-FIX4-03: 证据集中未完成点时认证的项数说明(状态变更理由可见性)。
    缺失point_in_time_certified字段的旧记录按未认证计(不推定已认证);
    全部已认证时返回空串(不虚报限制)。"""
    n = sum(1 for i in items or [] if not i.get('point_in_time_certified'))
    return (f";其中{n}项未完成点时认证,按观测层证据参与(非已证实研究截止时可得)"
            if n else '')


def star_level_from_evidence(verified_items):
    """按证据分级v2计算可授予的最高星级(第四轮P0-5修正)。
    规则: 5★=5项/3类机制/3观察期(无重大反证即足;存在未解释重大反证封顶3★);
    4★=4项/3类/2期; 3★=3项/2类; 2★=2项; 1★=1项。
    只计支持证据(非反证项),同一底层指标去重; 同ISO周=1个观察期。
    返回 (max_star, 说明)。星级衡量证据充分性,≠预测概率,≠资金比例。
    W2-FIX4-03: 说明披露点时认证分解(已认证x·未认证y)——星级门槛不变,
    未认证项仍按观测层证据参与计数,但正式记录可见其未认证,不得表述为
    "已证实研究截止时可得"。"""
    supporting, contrary, unexplained, _neutral = split_evidence_direction(verified_items)
    metrics = {_base_metric(i.get('metric')) for i in supporting if i.get('metric')}
    n = len(metrics)
    cats = {i.get('mechanism') or mechanism_of(i.get('metric', '')) for i in supporting}
    periods = {_obs_period_bucket(i['obs_date']) for i in supporting}
    star = 0
    for s, n_min, c_min, p_min in STAR_RULES:
        if n >= n_min and len(cats) >= c_min and len(periods) >= p_min:
            star = s
            break
    capped = ''
    if star > MAX_STAR_UNEXPLAINED_COUNTER and unexplained:
        star = MAX_STAR_UNEXPLAINED_COUNTER
        capped = f',存在未解释反证{len(unexplained)}项封顶3★'
    uncert = sum(1 for i in supporting if not i.get('point_in_time_certified'))
    cert_n = len(supporting) - uncert
    _pit_desc = (f"/点时认证: 支持项{len(supporting)}中已认证{cert_n}·未认证{uncert}"
                 + ("(未认证按观测层证据参与)" if uncert else ""))
    desc = (f"独立支持证据{n}项({', '.join(sorted(metrics))})/机制{len(cats)}类/"
            f"观察期{len(periods)}个/反对证据{len(contrary)}项(未解释{len(unexplained)})"
            f"{_pit_desc}{capped}")
    return star, desc


def _seen_obs_pairs(ledger):
    """证据台账中已知的(底层指标, 观测日)集合 — 含同日早前运行的条目。"""
    seen = {}
    for led in ledger or []:
        for m, od in led.get('obs_pairs') or []:
            seen.setdefault(_base_metric(m), set()).add(str(od)[:10])
    return seen


def _new_metrics_vs_seen(items, seen):
    """items中相对已知信息集合为"新增"的底层指标 — (指标,观测日)已记录过不算;
    同一指标仅当本次观测日**更新**(新一期数据)才算新增;
    同一观测期的数值修订不算新观察期;首次引用算新增。"""
    new_metrics = set()
    for i in items:
        base, od = _base_metric(i.get('metric')), str(i.get('obs_date'))[:10]
        if base in seen and od in seen[base]:
            continue      # 完全相同的(指标,观测日)已记录过(旧值重引/修订重引)
        if any(od > old for old in seen.get(base, {''})):
            new_metrics.add(base)   # 新观测期(新一期数据)或首次引用
    return new_metrics


def new_supporting_metrics(v, supporting, today_iso=None):
    """本周"新增"独立支持证据的底层指标集合(第四轮P0-2 + 第五轮P1-1):
    与该观点历史证据台账(含同日早前运行写入的条目)相比。
    同批数据同日重跑10次不得产生10次新增: 台账在门禁判定**之后**写入,
    同日早前已计入的(指标,观测日)再次出现时已在已知集合内,不再是新增;
    修订(同一观测期的数值变化)只记录,不算新的经济观察。"""
    return _new_metrics_vs_seen(supporting, _seen_obs_pairs(v.get('evidence_ledger')))


def new_contrary_metrics(v, contrary, today_iso=None):
    """本周新增独立**反证**的底层指标集合(第五轮P0-4: 已验证论点重新开启的门禁口径,
    与支持证据同一套基底/观测日身份规则 — 新增判定与星级用一致的指标身份)。"""
    return _new_metrics_vs_seen(contrary, _seen_obs_pairs(v.get('evidence_ledger')))


def _key_engaged(v, new_support):
    """P0-2.4: 证据路径的评级变更须触及该资产关键传导指标(key_metrics,按基底比对)。
    证据只能证明宏观事实、未触及该资产既定传导通道时,不足以支持具体配置方向
    (保留候选提案)。未定义key_metrics的观点不适用(无既定传导通道,由星级门禁把关)。"""
    keys = v.get('key_metrics') or []
    if not keys:
        return True
    key_bases = {_base_metric(k) for k in keys}
    return any(m in key_bases for m in new_support)


# ════════════════════════════════════════════════════════════════════
# 预测生命周期 v3: 记录观察 → 前提判定 → 到期/触及裁决
# ════════════════════════════════════════════════════════════════════
def _pred_spec(p):
    """预测的结果规格(metric+comparator+target)是否可计算"""
    return (p.get('metric') and p.get('comparator') in COMPARATORS
            and isinstance(p.get('target'), (int, float)))


def _premise_spec(p):
    prem = p.get('premise')
    if isinstance(prem, dict):
        return (prem.get('metric') and prem.get('op') in COMPARATORS
                and isinstance(prem.get('target'), (int, float)))
    return False


def _is_final_prediction(p, today_iso=None):
    """预测是否已形成正式终态(第六轮P0-2): 终态预测不得被每日观察任务重新开启,
    也不得被GLM重复裁决或翻案。判定(按序):
    1. 显式 final 标记(新记录,裁决落地时由引擎写入);
    2. status ∈ hit/miss/inconclusive(三态即终态);
    3. 旧版记录兼容: not_yet_triggered 且已带 resolved_date(到期未触发曾被周报
       终态化)且截止日已过 — 视为终态,不再重开。
    注意: not_yet_triggered + resolved_date 但截止日未到(周报未触发说明注记,
    非终态)不算 — 前提仍可能在有效期内兑现。"""
    if p.get('final'):
        return True
    if p.get('status') in ('hit', 'miss', 'inconclusive'):
        return True
    if p.get('status') == 'not_yet_triggered' and p.get('resolved_date'):
        dl = str(p.get('deadline', ''))[:10]
        today = _iso(today_iso or datetime.now().strftime('%Y-%m-%d'))
        if dl and dl < today:
            return True
    return False


def _anchor_obs_date_valid(info, today_iso):
    """锚点观测日防御检查(第六轮P0-1): 返回(有效观测日 or None, 拒绝原因 or None)。
    观测日缺失/不可解析/晚于今日 → 无效 — 不得以采集日today替代实际观测日写入历史。"""
    od = str(info.get('obs_date') or '')[:10]
    if not od:
        return None, '锚点无观测日(obs_date),无法绑定实际观察日'
    try:
        if date.fromisoformat(od) > date.fromisoformat(today_iso):
            return None, f'观测日{od}晚于今日{today_iso}(未来数据,不得记录)'
    except ValueError:
        return None, f'观测日不可解析({od})'
    return od, None


def record_observations(views_data, anchors, today_str=None):
    """数据持续记录(每期回写时/每日观察任务调用;第四轮P0-6 + 第六轮P0-1/P0-2):
    1) 带前提规格的未触发预测: 前提按锚点程序判定,兑现→转观察中并盖observe_from
       (观察期自前提兑现日起,截止日不变,不顺延)。第六轮P0-2前提激活守卫:
       - 终态预测(第六轮_is_final_prediction)不再参与前提判定,不得重开;
       - 前提观测日须可解析且不晚于今日、不超新鲜度窗(过期数据不得激活前提);
       - 前提观测日须≤截止日 — 截止日后才兑现的前提不得激活(截止日不顺延)。
    2) 观察中且带结果规格的预测: 把本期锚点值记入 observations(按观测日去重,
       同观测日留最新采集),并附盘中高/低(锚点存在兄弟.high/.low键时)与数据来源。
       第六轮P0-1防御: 观测日缺失/不可解析/未来/超新鲜度窗的锚点一律不写入
       正式观察历史(不得以采集日today替代实际观测日) — 即使调用方(观察器)
       已过滤,引擎侧也不放行(其他调用路径不得绕过观察器污染历史)。
    幂等: 同一批锚点重复运行不增加记录(changes只含真实状态变化,跳过说明仅打印,
    重复运行不虚增变更)。
    IA-P0-1-FIX4(IA-DEF-005)引擎侧质量防御: 质量状态为FAIL/缺失/非法的锚点
    一律不写入正式观察历史、不激活前提——与观察器同口径(rp.anchor_quality_problem),
    其他调用路径不得绕过观察器污染长期状态。
    返回变更说明列表。"""
    import research_provenance as _rp
    today_iso = _iso(today_str or datetime.now().strftime('%Y-%m-%d'))
    changes = []
    for p in views_data.get('predictions', []):
        # 前提程序判定
        if p.get('status') == 'not_yet_triggered' and _premise_spec(p) \
                and not _is_final_prediction(p, today_iso):
            prem = p['premise']
            info = (anchors or {}).get(prem['metric'])
            if info and isinstance(info.get('value'), (int, float)):
                q_problem = _rp.anchor_quality_problem(info)
                od, why_bad = _anchor_obs_date_valid(info, today_iso)
                if q_problem:
                    print(f"⚠️ 预测#{p['pred_id']}: 前提锚点{q_problem} — 不激活,本轮跳过")
                    continue
                deadline = str(p.get('deadline', ''))[:10]
                if od and _anchor_fresh(prem['metric'], info, today_iso) \
                        and COMPARATORS[prem['op']](float(info['value']), float(prem['target'])):
                    if deadline and od > deadline:
                        print(f"⚠️ 预测#{p['pred_id']}: 前提{od}才兑现,晚于截止日{deadline}"
                              f" — 预测不激活,截止日不顺延(到期未触发)")
                    else:
                        p['premise_triggered_date'] = od
                        p['status'] = 'observing'
                        p['observe_from'] = od   # 观察期自前提兑现日起
                        changes.append(f"预测#{p['pred_id']}: 前提已程序确认"
                                       f"({prem['metric']}={info['value']:g} {prem['op']} "
                                       f"{prem['target']:g},观测日{od})→转观察中")
                elif why_bad:
                    print(f"⚠️ 预测#{p['pred_id']}: 前提锚点无效本轮跳过 — {why_bad}")
        # 结果观察记录
        if p.get('status') == 'observing' and _pred_spec(p):
            info = (anchors or {}).get(p['metric'])
            if info and isinstance(info.get('value'), (int, float)):
                obs_date, why_bad = _anchor_obs_date_valid(info, today_iso)
                if not obs_date:
                    if why_bad:
                        print(f"⚠️ 预测#{p['pred_id']}: 本轮锚点无效不写入观察历史 — {why_bad}")
                    continue
                q_problem = _rp.anchor_quality_problem(info)
                if q_problem:
                    print(f"⚠️ 预测#{p['pred_id']}: 本轮锚点{q_problem} — 不写入观察历史")
                    continue
                if not _anchor_fresh(p['metric'], info, today_iso):
                    print(f"⚠️ 预测#{p['pred_id']}: 本轮锚点观测日{obs_date}超出新鲜度窗"
                          f"(疑采集失败),不写入观察历史")
                    continue
                obs = {'obs_date': obs_date,
                       'value': float(info['value']),
                       'as_of': str(info.get('as_of') or today_iso)[:10],
                       'retrieved_at': str(info.get('as_of') or today_iso)[:10],
                       'source': str(info.get('source_file') or info.get('source') or 'anchors')}
                # 盘中高/低(兄弟锚点键,供high/low口径的touch裁决;缺失如实不记)
                base = str(p['metric']).rsplit('.', 1)[0]
                for fld in ('high', 'low'):
                    sib = (anchors or {}).get(f"{base}.{fld}")
                    if sib and isinstance(sib.get('value'), (int, float)) and \
                            str(sib.get('obs_date') or '')[:10] == obs_date:
                        obs[fld] = float(sib['value'])
                existing = p.setdefault('observations', [])
                dup = next((o for o in existing if o['obs_date'] == obs_date), None)
                if dup:
                    if obs['as_of'] >= dup.get('as_of', ''):
                        changed = any(dup.get(k) != v for k, v in obs.items())
                        dup.update(obs)
                        if changed:  # 修订/补采(如新增盘中高低): 同观测日更新留最新
                            changes.append(f"预测#{p['pred_id']}: 更新观测日{obs_date}"
                                           f"记录({p['metric']}={obs['value']:g})")
                else:
                    existing.append(obs)
                    changes.append(f"预测#{p['pred_id']}: 新增观测 {p['metric']}"
                                   f"={obs['value']:g}({obs_date})")
    return changes


def _window_obs(p):
    """观察窗内的观测记录(禁止使用窗口外/未来数据): [observe_from|date_made, deadline]"""
    start = str(p.get('observe_from') or p.get('date_made') or '2000-01-01')[:10]
    end = str(p.get('deadline', '9999-12-31'))[:10]
    obs = sorted([o for o in p.get('observations', [])
                  if start <= str(o.get('obs_date', ''))[:10] <= end],
                 key=lambda o: str(o.get('obs_date')))
    return obs, start, end


def _obs_field_value(o, basis):
    """按价格口径取观测值: close→value; high/low→对应盘中字段(缺失返回None)。"""
    if basis in ('high', 'low'):
        v = o.get(basis)
        return float(v) if isinstance(v, (int, float)) else None
    v = o.get('value')
    return float(v) if isinstance(v, (int, float)) else None


def _days_between(d1, d2):
    try:
        return (date.fromisoformat(str(d1)[:10]) - date.fromisoformat(str(d2)[:10])).days
    except ValueError:
        return 999


# ════════════════════════════════════════════════════════════════════
# 市场交易日历与观察窗覆盖(第五轮P0-2)
# 2026-10-17第七轮重构: 日历实现抽取至 trading_calendar.py(全系统唯一日历权威,
# 金融事实引擎Layer 2组件); 本模块转发以保持既有接口与全部测试兼容。
from trading_calendar import (  # noqa: F401  (转发导出)
    is_trading_day, expected_trading_days, months_before,
)


def market_of_metric(metric):
    """指标→市场日历: crypto(BTC等7×24)/cn(A股, china.*前缀)/hk(港股代码)/
    us(global_market的SPX/DXY/ETF/GOLD/WTI期货与macro.data的FRED序列)。"""
    m = str(metric or '')
    if m.startswith('china.'):
        return 'hk' if '.HK' in m else 'cn'
    if 'BTC' in m:
        return 'crypto'
    return 'us'


def settlement_date(deadline, market):
    """预定义截止口径(第五轮P0-2): 截止日(含)往前的最后一个有效交易日 —
    非交易日截止一律**回溯**取前一有效交易日,规则事先固定,不得事后挑选有利日期。"""
    try:
        d = date.fromisoformat(str(deadline)[:10])
    except ValueError:
        return str(deadline)[:10]
    for _ in range(10):
        if is_trading_day(d, market):
            return d.isoformat()
        d -= timedelta(days=1)
    return str(deadline)[:10]


def window_coverage(p, today_str=None):
    """观察窗覆盖体检(第五轮P0-2): 每项预测可确定观察起始/截止/市场/预期有效
    观察日期/已取得观测/缺失日期/覆盖是否充分。判miss须 sufficient 且对应口径
    数据完整;关键日期缺失 → inconclusive(数据缺失≠失败)。"""
    obs, start, end = _window_obs(p)
    market = market_of_metric(p.get('metric'))
    basis = p.get('price_basis', 'close')
    got = {str(o.get('obs_date', ''))[:10] for o in obs
           if _obs_field_value(o, basis) is not None}
    expected = expected_trading_days(start, end, market, upto=today_str)
    missing = sorted(set(expected) - got) if expected is not None else None
    return {'start': start, 'end': end, 'market': market, 'basis': basis,
            'expected': expected, 'got': sorted(got), 'missing': missing,
            'sufficient': expected is not None and not missing}


def evaluate_predictions(views_data, today_str=None, anchors=None):
    """到期/触及裁决(引擎权威;第三轮P0-2 + 第四轮P0-6价格口径/截止日窗口)。

    - 只用观察窗内的 observations; 窗内无记录时回退锚点(仅当锚点obs_date≤deadline)
    - price_basis: close(默认,收盘达到)/high(盘中最高触及)/low(盘中最低触及)。
      touch判miss须整个窗口都有该口径数据 — 只有收盘价不得证明"盘中未触及",
      缺盘中高低价→inconclusive(数据不足不硬判)。
    - touch模式: 窗内任一观测按其口径满足即hit(可提前);全不满足且已到期→miss
    - expiry模式: 已到期,按预定义有效截止交易日(settlement_date,非交易日回溯)
      **当日**的观测判定(第六轮P0-3: 无容差回退);该日无有效观测→inconclusive
    - 前提到截止日未成立 → 未触发(终态)
    - 窗内无数据 → 无法裁决(不硬判)
    返回 [(pred_id, old, new, note)]; 由调用方写回。"""
    today_iso = _iso(today_str or datetime.now().strftime('%Y-%m-%d'))
    verdicts = []
    for p in views_data.get('predictions', []):
        status = p.get('status')
        deadline = str(p.get('deadline', '9999-12-31'))[:10]
        if status == 'not_yet_triggered' and deadline <= today_iso:
            verdicts.append((p['pred_id'], status, 'not_yet_triggered',
                             f"前提条件至截止日{deadline}未成立,预测未生效(截止日不顺延)"))
            continue
        if status != 'observing' or deadline > today_iso:
            # 未到期: touch模式可提前命中(触及是单调事件)
            if status == 'observing' and p.get('verify_mode') == 'touch' and _pred_spec(p):
                basis = p.get('price_basis', 'close')
                obs, start, end = _window_obs(p)
                hits = [o for o in obs
                        if (v := _obs_field_value(o, basis)) is not None
                        and COMPARATORS[p['comparator']](v, float(p['target']))]
                if hits:
                    h = hits[0]
                    hv = _obs_field_value(h, basis)
                    verdicts.append((p['pred_id'], status, 'hit',
                                     f"引擎自动裁决(提前触及): {p['metric']}({PRICE_BASIS_CN[basis]})"
                                     f"于观测日{h['obs_date']}触及{hv:g} {p['comparator']} {p['target']:g}"
                                     f"(观察窗{start}~{end})"))
                    continue
            continue
        if not _pred_spec(p):
            continue  # 无可计算规格 → 定性预测,只能inconclusive研究回顾(不计客观命中率)
        obs, start, end = _window_obs(p)
        if not obs:
            # 回退: 当期锚点若观测日落在窗内,可作为单点观测(仍禁止未来数据)
            info = (anchors or {}).get(p['metric'])
            if info and isinstance(info.get('value'), (int, float)):
                od = str(info.get('obs_date') or '')[:10]
                if od and start <= od <= end:
                    obs = [{'obs_date': od, 'value': float(info['value'])}]
        if not obs:
            verdicts.append((p['pred_id'], status, 'inconclusive',
                             f"观察窗{start}~{end}内无{p['metric']}观测记录,数据不足无法裁决"))
            continue
        mode = p.get('verify_mode') or 'expiry'
        basis = p.get('price_basis', 'close')
        if mode == 'touch':
            usable = [o for o in obs if _obs_field_value(o, basis) is not None]
            hits = [o for o in usable
                    if COMPARATORS[p['comparator']](_obs_field_value(o, basis), float(p['target']))]
            if hits:
                h = hits[0]
                hv = _obs_field_value(h, basis)
                vals = [_obs_field_value(o, basis) for o in usable]
                verdicts.append((p['pred_id'], status, 'hit',
                                 f"引擎自动裁决(观察期内触及): {p['metric']}({PRICE_BASIS_CN[basis]})"
                                 f"于{h['obs_date']}达{hv:g} {p['comparator']} {p['target']:g}"
                                 f"(窗内区间{min(vals):g}~{max(vals):g},共{len(usable)}个观测)"))
            else:
                cov = window_coverage(p)
                if basis != 'close' and len(usable) < len(obs):
                    # 盘中口径缺数据: 只有收盘价不能证明盘中未触及
                    missing = len(obs) - len(usable)
                    verdicts.append((p['pred_id'], status, 'inconclusive',
                                     f"观察窗{start}~{end}内{missing}/{len(obs)}个观测缺{PRICE_BASIS_CN[basis]}"
                                     f"数据,无法证明盘中未触及{p['comparator']}{p['target']:g} — 数据不足不判miss"))
                elif not cov['sufficient']:
                    # 第五轮P0-2: 触及判miss须窗口覆盖充分 — 预期交易日有缺失时,
                    # 缺失日期无法证明未触及(如仅取得3个交易日最高价且都低于目标≠失败)
                    miss_list = ','.join(cov['missing'] or [])
                    verdicts.append((p['pred_id'], status, 'inconclusive',
                                     f"观察窗{start}~{end}({cov['market']}日历)预期{len(cov['expected'] or [])}"
                                     f"个交易日,缺{len(cov['missing'] or [])}天({miss_list[:60]})该口径观测 — "
                                     f"覆盖不足,缺失日期无法证明未{p['comparator']}{p['target']:g},不判miss"))
                else:
                    vals = [_obs_field_value(o, basis) for o in usable]
                    verdicts.append((p['pred_id'], status, 'miss',
                                     f"引擎自动裁决(到期未触及): 观察窗{start}~{end}内{p['metric']}"
                                     f"({PRICE_BASIS_CN[basis]})区间{min(vals):g}~{max(vals):g}"
                                     f"(共{len(usable)}个观测,覆盖{len(cov['expected'])}个交易日完整),"
                                     f"从未满足{p['comparator']}{p['target']:g}"))
        else:
            # expiry(第五轮P0-2预定义截止口径 + 第六轮P0-3严格化):
            # 截止口径=按市场日历预先确定的有效截止交易日(settlement_date,非交易日
            # 截止一律回溯,规则事先固定不事后挑)。裁决**只认该日当日的观测** —
            # 结算日数据缺失判inconclusive,不得回退用前一交易日价格裁决
            # (防止拿截止日前较早的满足值冒充截止水平);crypto 7×24按自然日自洽。
            mkt = market_of_metric(p.get('metric'))
            settle = settlement_date(deadline, mkt)
            same_day = [o for o in obs if str(o.get('obs_date', ''))[:10] == settle
                        and _obs_field_value(o, 'close') is not None]
            if not same_day:
                verdicts.append((p['pred_id'], status, 'inconclusive',
                                 f"截止日{deadline}按{mkt}日历的有效截止交易日{settle}"
                                 f"当日无{p['metric']}有效观测(最近观测{obs[-1]['obs_date']}),"
                                 f"截止时点价格缺失不得以前一交易日价格代替,无法按截止日水平裁决"))
                continue
            last = same_day[-1]
            lv = _obs_field_value(last, 'close')
            fired = COMPARATORS[p['comparator']](lv, float(p['target']))
            verdicts.append((p['pred_id'], status, 'hit' if fired else 'miss',
                             f"引擎自动裁决(截止日水平): {p['metric']}={lv:g}"
                             f"(观测日{last['obs_date']}即有效截止交易日{settle})"
                             f" {p['comparator']} {p['target']:g} → {'满足' if fired else '不满足'}"))
    return verdicts


def predictions_in_period(views_data, start, end):
    """统计周期内(YYYYMMDD闭区间)按deadline/resolved_date归期的预测。
    counts含qualitative: 定性预测(无可计算规格)的研究性回顾,单列不计入客观命中率。
    返回 {due:[...], resolved:[...], counts:{hit,miss,inconclusive,open,qualitative}}。"""
    s, e = str(start).replace('-', ''), str(end).replace('-', '')
    due, resolved = [], []
    for p in views_data.get('predictions', []):
        dl = str(p.get('deadline', '')).replace('-', '')
        rd = str(p.get('resolved_date', '')).replace('-', '')
        if s <= dl <= e:
            due.append(p)
        if rd and s <= rd <= e:
            resolved.append(p)
    counts = {k: sum(1 for p in resolved if p.get('status') == k)
              for k in ('hit', 'miss', 'inconclusive')}
    counts['open'] = sum(1 for p in due if p.get('status') in ('observing', 'not_yet_triggered', 'open'))
    counts['qualitative'] = sum(1 for p in resolved
                                if not p.get('metric') and p.get('status') == 'inconclusive')
    return {'due': due, 'resolved': resolved, 'counts': counts}


# ════════════════════════════════════════════════════════════════════
# 渲染(进周报prompt)
# ════════════════════════════════════════════════════════════════════
def render_views_block(views_data, today_str=None, anchors=None):
    """观点库 → prompt文本块: 评级定义 + 引擎核验过的触发器状态(含持续确认)
    + 预测生命周期跟踪(模式/观察记录) + 被拒提案(防止模型每周重复提交)"""
    if not views_data:
        return "(观点库缺失,本周跳过配置观点)"
    lines = ["(评级为相对观点而非仓位指令;星级不直接推导仓位)"]
    lines.append("评级量表(只允许以下4级): " + "; ".join(
        f"{r}={d}" for r, d in RATING_DEFINITIONS.items()))

    trig_eval = evaluate_quant_triggers(views_data, anchors, today_str=today_str)
    lines.append("")
    lines.append("| 资产 | 评级 | 确信度 | 核心理由 | 升级触发(引擎核验) | 降级触发(引擎核验) |")
    lines.append("|------|------|--------|----------|----------|----------|")
    for v in views_data.get('views', []):
        stars = "★" * v.get('confidence', 0)
        by_dir = {'upgrade': '待验证(不可量化)', 'downgrade': '待验证(不可量化)'}
        for row in trig_eval.get(v['id'], []):
            mark = {'triggered': '✅已触发', 'not_triggered': '⬜未触发',
                    'unverifiable': '❓待验证', 'sustaining': '⏳持续确认中'}[row['status']]
            by_dir[row['direction']] = f"[{row['trig_id']}]{mark} {row['detail'][:44]}"
        lines.append(f"| {v['asset']} | {v.get('rating','?')} | {stars} | "
                     f"{v.get('rationale','')[:40]}… | {by_dir['upgrade']} | {by_dir['downgrade']} |")

    lines.append("")
    lines.append("⚠️ 触发器纪律: 只有引擎核验为\"✅已触发\"的条件才可在报告中表述为已触发;"
                 "\"❓待验证\"的条件必须原文标注待验证,不得当作已发生;"
                 "\"⏳持续确认中\"的条件须待连续周数满额才算触发。")

    preds = views_data.get('predictions', [])
    if preds:
        lines.append("")
        lines.append("### 预测跟踪(五态: 未触发/观察中/已命中/已证伪/无法裁决)")
        due = {p['pred_id'] for p in due_predictions(views_data, today_str)}
        for p in preds:
            status_cn = PRED_STATUS_CN.get(p.get('status', 'observing'), p.get('status'))
            mark = " ⏰已到期,本周必须裁决" if p['pred_id'] in due else ""
            spec = ""
            if p.get('metric'):
                pb = p.get('price_basis', 'close')
                spec = f" [规格: {p['metric']} {p.get('comparator')} {p.get('target')}" \
                       + (f",{PRICE_BASIS_CN[pb]}" if pb != 'close' else '') + "]"
            mode = VERIFY_MODE_CN.get(p.get('verify_mode', 'expiry'), '')
            obs = p.get('observations') or []
            obs_note = ""
            if p.get('status') == 'observing' and obs:
                lo = min(o['value'] for o in obs)
                hi = max(o['value'] for o in obs)
                obs_note = f" [已记录{len(obs)}个观测,区间{lo:g}~{hi:g}]"
            if p.get('status') == 'observing' and p.get('metric'):
                cov = window_coverage(p, today_str)
                if cov['missing']:
                    obs_note += (f" [⚠️观察窗覆盖不足: {cov['market']}日历预期"
                                 f"{len(cov['expected'])}个交易日,缺{len(cov['missing'])}天"
                                 f"({cov['missing'][0]}起)观察 — 裁决将从严,不得假设未触及]")
            prem = ""
            if p.get('status') == 'not_yet_triggered':
                prem = " [前提未兑现,不启动结果观察期]"
            lines.append(f"- [#{p['pred_id']}][{status_cn}] {p['asset']}: "
                         f"{p['direction'][:60]} (截止{p.get('deadline','?')},{mode}){spec}{obs_note}{prem}{mark}")

    # 被拒提案公示(第三轮P0-1: 留档+防每周重复提交)
    rejected = []
    for v in views_data.get('views', []):
        for pr in (v.get('proposals') or [])[-1:]:
            if pr.get('status') == 'rejected' and pr.get('date') >= _shift(today_str, -21):
                rejected.append(f"{v['asset']}→{pr.get('to','?')}(被拒:{pr.get('reason','')[:40]}"
                                f"{',重复提交' + str(pr.get('repeat', 1)) + '次' if pr.get('repeat', 1) > 1 else ''})")
    if rejected:
        lines.append("")
        lines.append("### 近期被拒提案(证据不足,勿无新证据重复提交)")
        lines.extend(f"- {r}" for r in rejected)
    return "\n".join(lines)


def _shift(today_str, days):
    try:
        return (date.fromisoformat(_iso(today_str or datetime.now().strftime('%Y-%m-%d')))
                + timedelta(days=days)).isoformat()
    except ValueError:
        return '0000-00-00'


def _parse_status_block(report_text, tag):
    """提取 <!--TAG ... TAG--> 内的JSON对象列表(容错:代码围栏/整块/逐行JSON)。
    逐行解析须在扁平正则之前: 带嵌套evidence数组的行会被\\{[^{}]*\\}正则拆碎。"""
    m = re.search(rf'<!--\s*{tag}\s*(.*?)\s*{tag}\s*-->', report_text, re.DOTALL)
    if not m:
        return []
    block = m.group(1).replace('```json', '').replace('```', '')
    try:
        parsed = json.loads(block.strip())
        return parsed if isinstance(parsed, list) else [parsed]
    except Exception:
        pass
    objs = []
    for line in block.split('\n'):
        line = line.strip().rstrip(',')
        if line.startswith('{') and line.endswith('}'):
            try:
                objs.append(json.loads(line))
            except Exception:
                pass
    if objs:
        return objs
    for mm in re.finditer(r'\{[^{}]*\}', block):
        try:
            objs.append(json.loads(mm.group(0)))
        except Exception:
            pass
    return objs


def _hist_append(hist, tag, kind, text):
    """同日同类条目去重: 重跑时替换而非追加。kind: 评级/确信度/维持"""
    line = f"{tag} {kind}: {text}" if kind != '维持' else f"{tag} 维持 {text}"
    prefix = f"{tag} {kind}"
    if hist and hist[-1].startswith(prefix):
        hist[-1] = line
    else:
        hist.append(line)
    return hist[-12:]


def _change_direction(old, new):
    """评级变更方向: downgrade/upgrade/suspend(转观望)/resume(自观望恢复)/None。
    自观望恢复到任何表态(含标配)都是resume — 恢复表态须有证据,不得借降级触发器直接放行。"""
    if old == new:
        return None
    if new == '观望':
        return 'suspend'
    if old == '观望':
        return 'resume'
    return 'downgrade' if RATING_RANK.get(new, 0) < RATING_RANK.get(old, 0) else 'upgrade'


def _record_proposal(v, to_rating, reason, evidence_summary, today_iso):
    """被拒提案留档: 同向提案21天内去重(只累计repeat),防止每周重复生成同一调整提案。"""
    proposals = v.setdefault('proposals', [])
    for pr in proposals:
        if (pr.get('to') == to_rating and pr.get('status') == 'rejected'
                and pr.get('date', '') >= _shift(today_iso, -PROPOSAL_DEDUP_DAYS)):
            pr['repeat'] = int(pr.get('repeat', 1)) + 1
            pr['date'] = today_iso
            pr['last_reason'] = reason
            return pr
    entry = {'date': today_iso, 'to': to_rating, 'status': 'rejected', 'reason': reason,
             'evidence_offered': evidence_summary[:160], 'repeat': 1}
    proposals.append(entry)
    v['proposals'] = proposals[-20:]
    return entry


def _mark_proposals_superseded(v, to_rating, today_iso):
    """评级变更落地时,把已被本次变更超越的同向被拒提案标记superseded。
    反向旧提案不算被超越(降级落地不使被拒的超配提案失效,21天公示期后自然过期)。"""
    for pr in v.get('proposals', []):
        if pr.get('to') == to_rating and pr.get('status') == 'rejected':
            pr['status'] = 'superseded'
            pr['superseded_date'] = today_iso


# ════════════════════════════════════════════════════════════════════
# 回写(评级变更门禁 + 证据星级门禁 + 预测生命周期)
# ════════════════════════════════════════════════════════════════════
def update_allocation_status(report_text, views_path=None, anchors=None, today_str=None):
    """解析ALLOCATION_STATUS+PREDICTION_STATUS回写观点库(第三轮v3)。

    门禁:
    - 评级变更: 须引擎同向触发器"已触发",或≥2项程序验证的新增evidence;
      否则保留原评级,提案留档(proposals)。转/自"观望"放宽为≥1项。
    - 确信度上调: 不得超过程序验证星级(证据分级v2);关键证据缺失封顶2★;下调自由。
    - 预测: 先记录观察+程序判前提,再按 权威序=引擎>GLM 裁决;
      GLM不得覆盖引擎结果;expiry未到期不得提前裁决;touch触及可提前hit;
      GLM裁决note引用的数值须与观察窗内记录吻合。
    - 无证据(无note/无数值)的hit/miss一律拒收(v2保留)。

    返回更新摘要列表。"""
    path = views_path or DEFAULT_VIEWS_PATH
    alloc_objs = _parse_status_block(report_text, 'ALLOCATION_STATUS')
    pred_objs = _parse_status_block(report_text, 'PREDICTION_STATUS')
    if not alloc_objs and not pred_objs:
        print("⚠️ 报告中未找到ALLOCATION_STATUS/PREDICTION_STATUS块,观点库未回写")
        return []

    if not os.path.exists(path):
        print(f"⚠️ 观点库不存在,无法回写: {path}")
        return []
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if _migrate_views(data):
        print("   观点库迁移: 中性→标配 / 预测生命周期字段补全(verify_mode/observations)")

    today = datetime.strptime(today_str, '%Y-%m-%d') if today_str else datetime.now()
    today_iso = today.strftime('%Y-%m-%d')
    tag = f"{today.month}/{today.day}"
    updates = []
    valid_alloc_lines = 0

    # 本周触发器评估(持久化连续周数)
    trig_eval = evaluate_quant_triggers(data, anchors, today_str=today_iso, persist=True)

    # --- 观点评级回写(门禁) ---
    for o in alloc_objs:
        vid = o.get('id')
        v = next((x for x in data.get('views', []) if x.get('id') == vid), None)
        if v is None:
            continue
        valid_alloc_lines += 1
        new_rating = str(o.get('rating', '')).strip()
        conf = o.get('confidence')
        note = str(o.get('note', '')).strip()[:60]

        # 证据程序验证(第三轮P0-3 + 第四轮P0-2方向切分/新增判定)
        verified, ev_rejects = verify_evidence_items(o.get('evidence'), anchors, today_iso)
        supporting, contrary, unexplained, neutral_ev = split_evidence_direction(verified)
        star_max, star_desc = star_level_from_evidence(verified)
        key_metrics = v.get('key_metrics') or []
        support_metrics = {_base_metric(i['metric']) for i in supporting}
        key_missing = [k for k in key_metrics if _base_metric(k) not in support_metrics]
        if key_missing and star_max > MAX_STAR_KEY_EVIDENCE_MISSING:
            star_max = MAX_STAR_KEY_EVIDENCE_MISSING
            star_desc += f";关键证据缺失({','.join(key_missing)})封顶{MAX_STAR_KEY_EVIDENCE_MISSING}★"
        # 本周新增独立支持证据(旧值重引不算新增,第四轮P0-2)
        new_support = new_supporting_metrics(v, supporting, today_iso)
        for rj, _item in ev_rejects[:3]:
            print(f"   ⚠️ #{vid}证据被拒: {rj}")

        rating_changed = False
        if new_rating in ALLOWED_RATINGS and new_rating != v.get('rating'):
            direction = _change_direction(v.get('rating'), new_rating)
            # 门禁: 同向触发器已触发,或足量验证证据
            fired = [r for r in trig_eval.get(vid, [])
                     if r['direction'] == direction and r['status'] == 'triggered']
            min_ev = 1 if direction in ('suspend', 'resume') else MIN_EVIDENCE_FOR_RATING_CHANGE
            if fired:
                old = v.get('rating')
                v['rating'] = new_rating
                rating_changed = True
                via = f"触发器{'+'.join(r['trig_id'] for r in fired)}(引擎核验已触发)"
                v['last_change'] = {'date': today_iso, 'from': old, 'to': new_rating,
                                    'via': via, 'evidence': verified[:5], 'note': note}
                _mark_proposals_superseded(v, new_rating, today_iso)
                updates.append(f"#{vid}{v['asset']}: 评级 {old}→{new_rating} (经{via})")
                v['history'] = _hist_append(v.setdefault('history', []), tag, '评级',
                                            f"{old}→{new_rating} [{via}] {note}".rstrip())
            elif len(new_support) >= min_ev and _key_engaged(v, new_support):
                old = v.get('rating')
                v['rating'] = new_rating
                rating_changed = True
                via = (f"新增独立支持证据{len(new_support)}项经验证({star_desc[:60]})"
                       + uncertified_note(supporting))
                v['last_change'] = {'date': today_iso, 'from': old, 'to': new_rating,
                                    'via': via, 'evidence': supporting[:5], 'note': note}
                _mark_proposals_superseded(v, new_rating, today_iso)
                updates.append(f"#{vid}{v['asset']}: 评级 {old}→{new_rating} (经{via})")
                v['history'] = _hist_append(v.setdefault('history', []), tag, '评级',
                                            f"{old}→{new_rating} [新增证据{len(new_support)}项] {note}".rstrip())
            elif len(new_support) >= min_ev:
                # P0-2.4: 证据足量但未触及关键传导指标 — 只能证明宏观事实,
                # 不能充分支持该资产的配置方向 → 保留候选提案
                reason = (f"新增独立支持证据{len(new_support)}项均未触及资产关键传导指标"
                          f"{key_metrics}(证据只能证明宏观事实,不能充分支持该配置方向;"
                          f"{star_desc[:60]})")
                pr = _record_proposal(v, new_rating, reason,
                                      json.dumps(o.get('evidence'), ensure_ascii=False)[:160],
                                      today_iso)
                updates.append(f"#{vid}{v['asset']}: 评级→{new_rating}降为候选提案"
                               f"[{reason[:70]}],保留{v.get('rating')}")
                print(f"   🚫 #{vid}评级变更保留为候选提案: {reason}")
            else:
                reason = (f"无引擎核验已触发的{direction}条件,本周新增独立支持证据{len(new_support)}项"
                          f"<{min_ev}项(支持{len(supporting)}/反对{len(contrary)},"
                          f"其中重复旧值{len(support_metrics) - len(new_support)}项;{star_desc[:60]})")
                if ev_rejects:
                    reason += "; 证据拒收: " + "; ".join(rj for rj, _ in ev_rejects[:3])
                pr = _record_proposal(v, new_rating, reason,
                                      json.dumps(o.get('evidence'), ensure_ascii=False)[:160],
                                      today_iso)
                rep = f"(累计重复{pr['repeat']}次)" if pr.get('repeat', 1) > 1 else ''
                updates.append(f"#{vid}{v['asset']}: 评级→{new_rating}被拒[{reason[:60]}]{rep},保留{v.get('rating')}")
                print(f"   🚫 #{vid}评级变更被拒: {reason}")

        conf_changed = False
        if isinstance(conf, (int, float)) and conf == int(conf) and 1 <= int(conf) <= 5:
            conf = int(conf)
            if conf != v.get('confidence'):
                old_c = v.get('confidence')
                if conf > (v.get('confidence') or 0):
                    # 上调须程序星级支撑(第三轮P0-3); 下调自由
                    if conf <= star_max:
                        v['confidence'] = conf
                        conf_changed = True
                        updates.append(f"#{vid}{v['asset']}: 确信度 {old_c}★→{conf}★ ({star_desc[:50]})")
                        v['history'] = _hist_append(v.setdefault('history', []), tag, '确信度',
                                                    f"{old_c}★→{conf}★ [{star_desc[:60]}]".rstrip())
                    else:
                        reason = f"证据仅支撑{star_max}★({star_desc[:60]}),不足以授予{conf}★"
                        _record_proposal(v, f"确信度{conf}★", reason,
                                         json.dumps(o.get('evidence'), ensure_ascii=False)[:160],
                                         today_iso)
                        updates.append(f"#{vid}{v['asset']}: 确信度→{conf}★被拒[{reason[:60]}],保留{old_c}★")
                        print(f"   🚫 #{vid}确信度上调被拒: {reason}")
                else:
                    v['confidence'] = conf
                    conf_changed = True
                    updates.append(f"#{vid}{v['asset']}: 确信度 {old_c}★→{conf}★")
                    v['history'] = _hist_append(v.setdefault('history', []), tag, '确信度',
                                                f"{old_c}★→{conf}★ {note}".rstrip())

        if not rating_changed and not conf_changed:
            v['history'] = _hist_append(v.setdefault('history', []), tag, '维持',
                                        f"{v.get('rating','?')} {v.get('confidence',0)}★ {note}".rstrip())

        # 证据台账写入(第五轮P1-1: 放在门禁判定**之后** — 同日重跑时,
        # 早前运行写入的(指标,观测日)已在已知集合内,同批数据不会再次计为新增)
        if verified:
            # W2-FIX4-03: 台账持久化点时认证计数(verified全集口径;desc内为支持
            # 集口径)——旧台账记录无此字段=当时未认证维度的如实缺席,读取侧
            # 一律按未认证处理,不回填不推定,不批量改写历史台账
            _cert_n = sum(1 for i in verified if i.get('point_in_time_certified'))
            ledger = v.setdefault('evidence_ledger', [])
            ledger.append({'date': today_iso, 'verified': len(verified),
                           'supporting': len(supporting), 'contrary': len(contrary),
                           'unexplained': len(unexplained), 'neutral': len(neutral_ev),
                           'new_support': sorted(new_support),
                           'point_time_certified': _cert_n,
                           'point_time_uncertified': len(verified) - _cert_n,
                           'star_max': star_max, 'desc': star_desc[:200],
                           'obs_pairs': sorted({(i['metric'], str(i.get('obs_date'))[:10])
                                                for i in verified})})
            v['evidence_ledger'] = ledger[-12:]

        # 评级变更行附带pred → 登记新预测(生命周期字段)
        if rating_changed and o.get('pred') and o.get('pred_weeks'):
            try:
                weeks = int(o['pred_weeks'])
            except (TypeError, ValueError):
                weeks = 0
            if weeks > 0:
                new_id = max([p.get('pred_id', 0) for p in data.get('predictions', [])] or [0]) + 1
                deadline = (today + timedelta(weeks=weeks)).strftime('%Y-%m-%d')
                entry = {
                    'pred_id': new_id,
                    'date_made': today_iso,
                    'asset': v['asset'],
                    'direction': str(o['pred']).strip()[:120],
                    'horizon_weeks': weeks,
                    'deadline': deadline,
                    'trigger': new_rating,
                    'status': 'observing',
                    'observe_from': today_iso,
                    'verify_mode': str(o.get('pred_mode', 'expiry')).strip() or 'expiry',
                    'data_source': 'anchors',
                    'observations': [],
                    'resolved_note': '',
                }
                if entry['verify_mode'] not in VERIFY_MODES:
                    entry['verify_mode'] = 'expiry'
                # 价格口径(第四轮P0-6): close(默认)/high/low — 盘中触及判定需对应口径数据
                pb = str(o.get('pred_basis', 'close')).strip() or 'close'
                entry['price_basis'] = pb if pb in PRICE_BASES else 'close'
                metric, op, target = o.get('pred_metric'), o.get('pred_op'), o.get('pred_target')
                if metric and op in COMPARATORS and isinstance(target, (int, float)):
                    entry['metric'] = str(metric)
                    entry['comparator'] = op
                    entry['target'] = float(target)
                    entry['evidence_ref'] = str(o.get('pred_evidence', '')).strip()[:80] or metric
                elif any((metric, op, target)):
                    print(f"   ⚠️ 预测#{new_id}规格不完整(metric/op/target),仅存文本形式(到期须人工裁决)")
                # 前提规格: 条件预测(前提兑现才开始结果观察期)
                pm, pop, pt = o.get('pred_premise_metric'), o.get('pred_premise_op'), o.get('pred_premise_target')
                if pm and pop in COMPARATORS and isinstance(pt, (int, float)):
                    entry['premise'] = {'metric': str(pm), 'op': pop, 'target': float(pt)}
                    entry['status'] = 'not_yet_triggered'
                    entry.pop('observe_from', None)
                    entry['premise_text'] = str(o.get('pred_premise', '')).strip()[:80]
                data.setdefault('predictions', []).append(entry)
                updates.append(f"新增预测#{new_id}({v['asset']}, 截止{deadline},{entry['verify_mode']}模式"
                               + (f", 规格{entry.get('metric')} {entry.get('comparator')} {entry.get('target')}" if 'metric' in entry else ", 无量化规格")
                               + (", 带前提规格" if 'premise' in entry else "") + ")")

    # --- 预测: 先记录观察+程序判前提 ---
    for ch in record_observations(data, anchors, today_iso):
        updates.append(ch)

    # --- 引擎权威裁决(GLM处理前先算,防模型覆盖客观结果) ---
    engine_verdicts = {pid: (new, note) for pid, old, new, note
                       in evaluate_predictions(data, today_str=today_iso, anchors=anchors)}

    # --- GLM裁决回写(受限: 不得覆盖引擎;expiry未到期拒提前;引用须在观察窗内) ---
    glm_resolved_today = set()
    for o in pred_objs:
        pid = o.get('pred_id')
        p = next((x for x in data.get('predictions', []) if x.get('pred_id') == pid), None)
        if p is None:
            continue
        status = str(o.get('status', '')).strip().lower()
        status = _PRED_STATUS_MAP.get(status, status)
        note = str(o.get('note', '')).strip()
        deadline = str(p.get('deadline', '9999-12-31'))[:10]
        today_iso_ = today_iso

        # 第六轮P0-2: 已形成正式终态的预测,每日/每周回写路径都不得重开或翻案 —
        # GLM不得对final预测改判或重复注记(hit/miss/inconclusive三态终局,
        # 重复运行不随意改变;重复注记会刷新原始裁决日期,破坏审计)
        if _is_final_prediction(p, today_iso_):
            if status != p.get('status'):
                updates.append(f"预测#{pid}: GLM裁决'{status}'被拒 — 该预测已形成正式终态"
                               f"({p.get('status')}),不得重复裁决或翻案")
                print(f"   🚫 预测#{pid}: 终态预测({p.get('status')})不得被GLM重新裁决")
            continue

        if status in ALLOWED_PRED_VERDICTS and p.get('status') != status:
            # 引擎已有客观裁决(hit/miss) → 模型只能附和,不得覆盖;
            # inconclusive是"无数据"而非客观结果,允许GLM附窗内证据补位(仍走引用核验)
            eng = engine_verdicts.get(pid)
            if eng and eng[0] != status and eng[0] != 'inconclusive':
                updates.append(f"预测#{pid}: GLM裁决'{status}'被拒 — 引擎已按观察记录裁决为'{eng[0]}',模型不可覆盖")
                print(f"   🚫 预测#{pid}: GLM试图将引擎裁决{eng[0]}改为{status},已拒绝")
                continue
            # 第四轮P0-6: 无可计算规格的定性预测,GLM不得判hit/miss
            # (文字说明不能替代观察记录;只能inconclusive研究回顾,不计入客观命中率)
            if not p.get('metric') and status in ('hit', 'miss'):
                updates.append(f"预测#{pid}: GLM裁决'{status}'被拒 — 定性预测无可计算规格/观察记录,"
                               f"只能以inconclusive作研究性回顾(不计入客观命中率)")
                print(f"   🚫 预测#{pid}: 无规格预测不得判hit/miss,只能inconclusive研究回顾")
                continue
            if not note:
                print(f"   ⚠️ 预测#{pid}裁决'{status}'未附note证据,已拒绝(无证据不得裁决命中/证伪)")
                updates.append(f"预测#{pid}: 裁决被拒(无证据)")
                continue
            if status in ('hit', 'miss') and not re.search(r'[0-9]', note):
                print(f"   ⚠️ 预测#{pid}裁决note无具体数值('{note[:30]}'),已拒绝(证据须引用数值)")
                updates.append(f"预测#{pid}: 裁决被拒(note无数值)")
                continue
            # expiry模式未到期 → 不得提前裁决; touch提前hit已由引擎处理,GLM同口径
            if deadline > today_iso_ and p.get('verify_mode') != 'touch':
                updates.append(f"预测#{pid}: GLM裁决'{status}'被拒 — 截止日{deadline}未到(expiry模式不得提前裁决)")
                print(f"   🚫 预测#{pid}: expiry模式未到期(截止{deadline}),拒绝提前裁决")
                continue
            # 引擎无法裁决(无规格/无记录/数据不足)时GLM补位 — 第五轮P0-1:
            # 可量化预测的hit/miss必须有有效观察记录支撑,空观察记录不得放行GLM裁决;
            # note引用的数值与观测日必须与观察窗内**同一条**实际记录吻合 —
            # 仅数值正确而日期错误→拒;仅日期正确而数值错误→拒;as_of采集日不算观测日;
            # hit引用的记录还须实际满足预测条件;miss须窗口覆盖充分(与引擎同口径);
            # expiry引用须落在有效截止交易日附近(不得拿窗内早期值证明截止水平)
            if (eng is None or eng[0] == 'inconclusive') and p.get('metric'):
                obs, start, end = _window_obs(p)
                basis_pb = p.get('price_basis', 'close')
                nums = [float(x) for x in re.findall(r'[0-9]+(?:\.[0-9]+)?', note)
                        if abs(float(x)) < 1e7]
                cited = None          # (数值, 观测日) — 与窗内同一条记录吻合的引用
                for o in obs:
                    od = str(o['obs_date'])[:10]
                    if od not in note:
                        continue      # 该记录的观测日未被引用 → 不是有效配对
                    ov = _obs_field_value(o, basis_pb)
                    if ov is None:
                        continue
                    if any(_value_close(x, ov) for x in nums):
                        cited = (ov, od)
                        break
                if cited and (p.get('verify_mode') or 'expiry') == 'expiry':
                    settle = settlement_date(deadline, market_of_metric(p['metric']))
                    if cited[1] != settle:
                        cited = None   # 第六轮P0-3: 只认有效截止交易日**当日**的记录
                        # (与引擎同一结算口径 — Python判inconclusive时GLM不得拿
                        #  前一交易日的满足值把同批数据裁成hit)
                if status in ('hit', 'miss'):
                    if cited is None:
                        why = (f"观察窗{start}~{end}内无{p['metric']}有效观察记录,不得仅凭文字宣判"
                               if not obs else
                               f"note引用的数值与观测日未同时与观察窗{start}~{end}内同一条记录吻合"
                               f"(数值与观测日须来自同一条实际记录)")
                        updates.append(f"预测#{pid}: GLM裁决被拒 — {why}")
                        print(f"   🚫 预测#{pid}: GLM裁决引用核验不通过(窗内{len(obs)}个观测)")
                        continue
                    if status == 'hit' and not COMPARATORS[p['comparator']](cited[0], float(p['target'])):
                        updates.append(f"预测#{pid}: GLM裁决hit被拒 — 引用记录{cited[0]:g}(观测日{cited[1]})"
                                       f"并未满足{p['comparator']}{p['target']:g},不能判命中")
                        print(f"   🚫 预测#{pid}: GLM引用记录不满足预测条件却判hit,已拒绝")
                        continue
                    if status == 'miss':
                        cov = window_coverage(p)
                        if not cov['sufficient']:
                            updates.append(f"预测#{pid}: GLM裁决miss被拒 — "
                                           f"观察窗覆盖不足({cov['market']}日历预期"
                                           f"{len(cov['expected'] or [])}个交易日缺{len(cov['missing'] or [])}天),"
                                           f"GLM与引擎同口径: 缺失日期无法证明未触及,不得判miss")
                            print(f"   🚫 预测#{pid}: 覆盖不足,GLM miss被拒(数据缺失≠失败)")
                            continue
            old = p.get('status')
            p['status'] = status
            p['resolved_note'] = note[:120]
            p['resolved_date'] = today_iso_
            p['final'] = True   # 第六轮P0-2: 终态落地即封存,后续运行不得重开/翻案
            glm_resolved_today.add(pid)
            updates.append(f"预测#{pid}: {old}→{status} ({note[:40]})")
        elif status == 'not_yet_triggered' and p.get('status') in ('observing', 'not_yet_triggered'):
            # 前提未兑现判定(定性前提由GLM判断,须附说明;带前提规格且已程序触发者不得改回)
            if _premise_spec(p):
                prem = p['premise']
                info = (anchors or {}).get(prem['metric'])
                if info and isinstance(info.get('value'), (int, float)) and \
                        COMPARATORS[prem['op']](float(info['value']), float(prem['target'])):
                    updates.append(f"预测#{pid}: GLM'未触发'判定被拒 — 前提{prem['metric']}已程序确认触发")
                    print(f"   🚫 预测#{pid}: 前提已程序触发,GLM不得改判未触发")
                    continue
            if not note:
                print(f"   ⚠️ 预测#{pid}'未触发'判定未附note说明,忽略")
                continue
            p['status'] = 'not_yet_triggered'
            p['resolved_note'] = note[:120]
            p['resolved_date'] = today_iso_
            updates.append(f"预测#{pid}: →未触发 ({note[:40]})")
        elif status == 'observing' and p.get('status') == 'not_yet_triggered':
            # 定性前提兑现(GLM判断): 观察期自今日起算,截止日不变
            if pid in engine_verdicts and engine_verdicts[pid][0] == 'not_yet_triggered':
                updates.append(f"预测#{pid}: GLM'转观察中'被拒 — 前提规格至截止日未程序触发,预测已终态未生效")
                print(f"   🚫 预测#{pid}: 引擎已终态裁决(前提未成立),不得再转观察中")
                continue
            if deadline < today_iso_:
                updates.append(f"预测#{pid}: GLM'转观察中'被拒 — 截止日{deadline}已过,前提迟于截止日兑现→预测未生效")
                print(f"   🚫 预测#{pid}: 前提到截止日未兑现,截止日不顺延")
                continue
            if not note:
                print(f"   ⚠️ 预测#{pid}'转观察中'未附note说明,忽略")
                continue
            p['status'] = 'observing'
            p['premise_triggered_date'] = today_iso_
            p['observe_from'] = today_iso_
            p['resolved_note'] = ''
            p.pop('resolved_date', None)
            updates.append(f"预测#{pid}: 未触发→观察中 (前提兑现,观察期自今日起,截止日不变)")

    # --- 补记: GLM刚将定性前提转"观察中"的预测,其确认周观测也在观察窗内,须记录 ---
    # (幂等: record_observations按观测日去重;仅新增observing状态的本周观测)
    for ch in record_observations(data, anchors, today_iso):
        updates.append(ch)

    # --- 应用引擎裁决(未被GLM合法处理的) ---
    for pid, (new, note) in engine_verdicts.items():
        if pid in glm_resolved_today:
            continue
        p = next(x for x in data['predictions'] if x.get('pred_id') == pid)
        old = p.get('status')
        if old == new:
            # 第六轮P0-2: not_yet_triggered到期未触发终态(状态不变但已终局) —
            # 落final标记,此后每日观察任务不得重开(前提迟到兑现也不再激活)
            p['final'] = True
            p.setdefault('resolved_note', '')
            p['resolved_note'] = note[:120]
            p['resolved_date'] = today_iso
            updates.append(f"预测#{pid}: 到期未触发终态落盘(截止日不顺延,不再重开)")
            continue
        p['status'], p['resolved_note'], p['resolved_date'] = new, note[:120], today_iso
        p['final'] = True   # 第六轮P0-2: 终态封存
        updates.append(f"预测#{pid}: {old}→{new} (引擎自动: {note[:50]})")

    if not valid_alloc_lines and not updates:
        print("⚠️ 状态块无可识别内容,观点库未改动")
        return []

    data['last_updated'] = today_iso

    shutil.copy(path, path + '.bak')
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)

    print(f"✅ allocation_views.json 已回写(备份: allocation_views.json.bak)")
    for u in updates:
        print(f"   {u}")
    return updates


if __name__ == '__main__':
    views = load_views()
    if views:
        print(render_views_block(views))
        due = due_predictions(views)
        print(f"\n到期待裁决: {len(due)} 条")
    else:
        sys.exit(1)
