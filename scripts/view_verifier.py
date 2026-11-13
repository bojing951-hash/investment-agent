#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""机构观点确定性验证器(Charter 8 交付③)——零 AI 判断,零网络。

职责: 输入 view_id → 读该观点 subjects → 经 config/view_metric_map.json
取注册表现有指标 → 从最新研究快照取数 → 输出支持/反对证据表。

口径纪律(防分叉):
  区间变动一律调 research_history_query.interval_change——与 ia_cli compare
  自配对(P2-2 正式口径)**同一函数同一条 common window 规则**: 基准=严格
  早于窗口起点的最后观测,末值=窗口内最后观测;利率 pp/价格 pct/计数 abs;
  数据不足 available=False+原因,不回退 0(月频 1m 窗无当月新观测→如报
  empty 即诚实缺席)。3m 窗=P2-2 已裁决机制的自然参数(禁新窗口逻辑)。

方向关系(与 view 方向关系):
  本模块不做语义判断。relation 仅在调用方显式传入 directions
  {metric_id: 'up'|'down'} 时机械计算: 窗口内净变动方向与 hint 同号且
  available → 'supports',反号 → 'against',不足/无变化 → 'neutral';
  未传 → None+note(方向提取属 Agent 层,attribution 纪律不进本模块)。

序列来源: workbench_data.metric_series——快照 series_store 优先,缺席时按
注册表 source 回落最新采集档(与工作台历史页/compare 同一条取数路径,
防口径分叉);两级都无序列的指标只报 level+缺席原因(不猜)。

运行: python3 scripts/view_verifier.py VIEW-YYYYMMDD-NNN [--directions '{"SPX":"up"}']
      [--snapshot-id research_snapshot_YYYYMMDD_vN] [--mode A|B|C|all]
输出: 单个 JSON(stdout);rc=0 成功 / 1 执行错(无快照/无 view) / 2 用法错。
快照指针(DEFERRED②, 2026-11-10): 默认=最新;研究针对特定版本时 --snapshot-id
显式指定(archive save 同款: 短形 YYYYMMDD_vN 容忍,不存在/非规范 rc=2
snapshot_not_found)——验证结果与归档指针同版,读者按 envelope.snapshot_id
可复现。
三型验证(Charter9 P0-1, 2026-11-11;缺省=legacy 最新快照行为,已发布契约不变):
  --mode A 提出时证据——vintage 锚定 publish_date(rp.vintage_dates≤publish 最近
           跨日快照;无该时点 vintage→最新快照截断至 publish,DEGRADED 随行);
           trailing 窗以观点时点为窗末(切点日期披露;含 publish 当日观测,≤含)
  --mode B 当前证据更新——最新快照;每指标附 since_publish 区间变动(严格>publish)
  --mode C 到期验证——期限解析(区间取上界/CY→年末/多时点取最晚;UNPARSEABLE
           显式态)→未到期 NOT_YET_TESTABLE/未映射 NOT_MACHINE_VERIFIABLE/
           方向型 supports·against(publish→horizon_end 区间变动);点位型只报告
成熟度护栏: mode A/B/C 下期限未到期或不可解析 → relation 一律压制为证据观察
(未到期不判 supports/against——C席复现 P0-1③ 的机械防线);legacy 模式保持
已发布行为(输出新增 maturity/revision_anchors 披露字段,数值路径零变化)。
revisions[](裁定 2026-11-11): 每条修订=新验证主体锚定其自身 date;原主张
vintage 窗不变——修订后主张的完整验证在其新档(如 009→006 链)。
"""
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import view_store as vs                      # noqa: E402
import research_history_query as rhq         # noqa: E402
import fact_engine as fe                     # noqa: E402
import workbench_data as wd                  # noqa: E402
import direction_semantics as dsem_mod       # noqa: E402

# 到期验证数据新鲜度(Charter 10 §5.2,R22): 到期日附近无新鲜观测=证据不足,
# 不判对错。允许滞后按注册表 frequency(市场序列节假日容忍/月频观测间隔+
# 发布滞后/季频同理);未登记频次保守 60 天。
FRESHNESS_ALLOWED_LAG_DAYS = {'daily': 10, 'weekly': 21, 'monthly': 60,
                              'quarterly': 130}
FRESHNESS_DEFAULT_LAG_DAYS = 60

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP_PATH = os.path.join(ROOT, 'config', 'view_metric_map.json')

HORIZONS = ('1m', '3m', '1y', '5y')          # 页①复用含 5y;verifier 默认前三个


def load_map(map_path=None):
    """读 subject→metric 映射;结构校验(subjects 非空且每 subject 有 metrics)。"""
    with open(map_path or MAP_PATH, encoding='utf-8') as f:
        m = json.load(f)
    subs = m.get('subjects')
    if not isinstance(subs, dict) or not subs:
        raise ValueError('view_metric_map.json 须含非空 subjects 对象')
    for k, v in subs.items():
        if not isinstance(v, dict) or not isinstance(v.get('metrics'), list):
            raise ValueError(f'subject {k} 须含 metrics 列表')
    return m


def interval_table(metric_id, snapshot, unit, target_ymd, horizons=HORIZONS):
    """单指标多窗口区间变动——薄委托 workbench_data.metric_window_changes
    (区间口径唯一实现处,app 页①与本模块共用,防口径分叉)。"""
    return wd.metric_window_changes(metric_id, snapshot, unit, target_ymd,
                                    horizons=horizons, root=ROOT)


def _net_direction(chg):
    """窗口净变动方向: 取可用窗口中最长者(1y>3m>1m);None=无可用。

    interval_change 契约: 成功节点不带 available 键(带变化值),失败节点
    available=False+reason——判可用=键缺席或非 False,判值=三个变化键。"""
    for h in ('1y', '3m', '1m'):
        node = (chg or {}).get(h) or {}
        if node.get('available') is False:
            continue
        for key in ('pp_change', 'pct_change', 'abs_change'):
            if node.get(key) is not None:
                return 'up' if node[key] > 0 else 'down' if node[key] < 0 else 'flat'
    return None


def metric_evidence_table(subjects, snapshot, registry, vmap,
                          horizons=('1m', '3m', '1y'), directions=None,
                          target_ymd=None, extra_metric_ids=None):
    """证据表(纯函数): subjects∪映射指标 × 快照 facts/series_store。

    target_ymd: 窗口锚定日(默认快照 target_date;mode A 传 publish/vintage
    切点——提出时证据的 trailing 窗以观点时点为窗末,防"今天的窗"冒充
    "提出时的证据状态")。
    extra_metric_ids(R5 2026-11-11): 假设层 metric_refs 并入证据面——机构
    观点明确引用的指标即使不在该观点 subjects 的映射面也出证据行
    (subject='hypothesis_ref');不在注册表/非active 的如实进 missing 并注明
    语义层缺口(禁猜,不造映射)。缺省 None=原契约(仅 subjects 映射面)。
    返回 {'evidence': [row...], 'missing': [...], 'notes': [...]}——missing=
    映射在册但快照无事实的指标(缺席如实,不猜)。"""
    directions = directions or {}
    facts = {f['metric_id']: f for f in (snapshot or {}).get('facts', [])}
    by_id = registry['by_id']
    subj_of = {}
    for subj, spec in vmap['subjects'].items():
        if subj in subjects:
            for mid in spec['metrics']:
                subj_of.setdefault(mid, subj)
    evidence, missing, notes = [], [], []
    for mid in sorted(set(extra_metric_ids or []) - set(subj_of)):
        m = by_id.get(mid)
        if m is None:
            missing.append({'metric_id': mid,
                            'reason': '假设引用指标不在注册表'
                                      '(语义层映射缺口,Agent 层待修,禁猜)'})
            continue
        if m.get('status') != 'active':
            missing.append({'metric_id': mid,
                            'reason': f'假设引用指标注册表非active({m.get("status")})'})
            continue
        subj_of[mid] = 'hypothesis_ref'
    for mid in sorted(subj_of):
        m = by_id.get(mid)
        if m is None or m.get('status') != 'active':
            missing.append({'metric_id': mid,
                            'reason': '映射含非注册表/非active指标(映射完整性违规)'})
            continue
        fact = facts.get(mid)
        if fact is None:
            miss_detail = ((snapshot or {}).get('gate_a') or {}).get(
                'noncore_missing_detail', {}).get(mid, '快照无该指标事实')
            missing.append({'metric_id': mid, 'reason': miss_detail})
            continue
        unit = fact.get('unit') or m.get('unit', '')
        fam = ('rate' if unit in fe.RATE_UNITS else
               'price' if unit in fe.PRICE_LIKE_UNITS else
               'count' if unit in fe.COUNT_UNITS else 'other')
        chg, series_source = interval_table(mid, snapshot, unit,
                                            target_ymd or snapshot.get('target_date'),
                                            horizons)
        rel, rel_note = None, '未传 directions→不做方向判断(纯确定性,语义层归 Agent)'
        if mid in directions:
            hint = directions[mid]
            got = _net_direction(chg)
            if hint not in ('up', 'down'):
                rel, rel_note = None, f'directions 值非法({hint!r},须 up/down)'
            elif got is None:
                rel, rel_note = 'neutral', '窗口内无可用变动(诚实缺席)'
            elif got == 'flat':
                rel, rel_note = 'neutral', '窗口净变动=0'
            else:
                rel = 'supports' if got == hint else 'against'
                rel_note = f'净变动方向={got} vs hint={hint}(最长可用窗口机械比对)'
        row = {
            'metric_id': mid, 'subject': subj_of[mid],
            'display_name': fact.get('display_name') or m.get('display_name', mid),
            'unit': unit, 'unit_family': fam,
            'level': fact.get('value'), 'observation_date': fact.get('observation_date'),
            'quality_status': fact.get('quality_status'), 'series_source': series_source,
            'changes': chg, 'relation': rel, 'relation_note': rel_note,
        }
        if fact.get('level_source') is not None:  # R5: mode A 截断尾值近似披露
            row['level_source'] = fact['level_source']
        evidence.append(row)
    if directions and set(directions) - set(subj_of):
        notes.append(f'directions 含映射外指标: '
                     f'{sorted(set(directions) - set(subj_of))}(忽略,防越权拼凑)')
    dir_missing = sorted(m['metric_id'] for m in missing if m['metric_id'] in directions)
    if dir_missing:
        notes.append(f'directions 指标缺席未判方向(如实): {dir_missing}')
    return {'evidence': evidence, 'missing': missing, 'notes': notes}


def verify(view_id, snapshot, registry, vmap, views_dir=None, directions=None,
           mode=None, target_ymd=None, extra_metric_ids=None):
    """完整验证: view → subjects → 证据表。返回输出 JSON dict(不含 AI 文本)。

    Charter9 P0-1 三型(--mode A/B/C;缺省=legacy 最新快照行为,已有契约不变):
      A=提出时证据(vintage 锚定 publish_date,mode 入口在 verify_at_publish);
      B=当前证据更新(最新快照+每指标附 since_publish 区间变动);
      C=到期验证(verify_expiry)。
    本函数为 A/B/legacy 共用证据表面;mode='B' 时逐指标附 since_publish 节点;
    mode∈{A,B,C} 时启用**成熟度护栏**: 观点期限未到期/不可解析 → relation
    一律压为 None+护栏注(未到期不判 supports/against——C席复现③的机械防线);
    仅 mode='C' 且到期,relation 才允许作为预测验证语义(见 verify_expiry)。
    extra_metric_ids(R5): 假设层 metric_refs 并入证据面(见
    metric_evidence_table docstring;build_vp 传入,CLI 缺省不变)。
    revision_anchors(协调裁定 2026-11-11): revisions[] 每条修订=新验证主体
    锚定其自身 date——本档验证仍锚原 publish_date,修订主体随行登记不改变
    原 vintage 窗。"""
    doc, reason = vs.get_view(view_id, views_dir)
    if doc is None:
        return {'ok': False, 'error': {'kind': 'view_not_found_or_quarantined',
                                       'message': reason}}
    anchor_ymd = target_ymd or snapshot.get('target_date')
    tab = metric_evidence_table(doc['subjects'], snapshot, registry, vmap,
                                horizons=('1m', '3m', '1y'), directions=directions,
                                target_ymd=anchor_ymd,
                                extra_metric_ids=extra_metric_ids)
    publish = doc.get('publish_date')
    mat = maturity(doc.get('view_horizon'), publish,
                   snapshot.get('target_date'))
    rel_semantics = None
    if mode in ('A', 'B', 'C'):
        allowed = (mode == 'C' and mat['state'] == 'MATURED')
        rel_semantics = ('到期验证(publish→horizon_end 窗,允许判预测)'
                         if allowed else
                         {'A': '提出时 trailing 窗一致性(E2 类事实,非预测验证)',
                          'B': '当前更新窗一致性(非预测验证)',
                          'C': f'成熟度护栏: {mat["state"]} → 不判 supports/against'}[mode])
        if not allowed:
            for e in tab['evidence']:
                if e.get('relation') is not None:
                    e['relation'] = None
                    e['relation_note'] = (f'成熟度护栏: 期限{mat["state"]}'
                                          '→不判 supports/against(证据观察)')
    if mode == 'B':
        for e in tab['evidence']:
            e['since_publish'] = _since_publish_node(
                e['metric_id'], e.get('unit'), snapshot, publish)
    n_sup = sum(1 for e in tab['evidence'] if e['relation'] == 'supports')
    n_ag = sum(1 for e in tab['evidence'] if e['relation'] == 'against')
    out = {
        'ok': True, 'view_id': view_id, 'mode': mode or 'legacy',
        'institution': doc['institution']['name'],
        'publish_date': doc['publish_date'], 'fetch_date': doc['fetch_date'],
        'subjects': list(doc['subjects']),
        'snapshot_id': snapshot.get('snapshot_id'),
        'target_date': snapshot.get('target_date'),
        'anchor_target': anchor_ymd,
        'research_as_of': snapshot.get('research_as_of'),
        'gate_a': (snapshot.get('gate_a') or {}).get('status'),
        'maturity': mat,
        'revision_anchors': [
            {'date': r.get('date'), 'anchor': 'independent_subject',
             'note': '每条修订=新验证主体,锚定其自身date;原主张vintage窗不变'
                     '(协调裁定 2026-11-11)——修订后主张的完整验证见其新档'}
            for r in (doc.get('revisions') or [])],
        'determinism_note': '全部数值=本地快照事实与 interval_change 区间变动'
                            '(compare 自配对同函数同 common window);relation 仅在'
                            '显式 directions 下机械计算,零 AI 判断',
        'n_evidence': len(tab['evidence']), 'n_missing': len(tab['missing']),
        'n_supports': n_sup, 'n_against': n_ag,
        'evidence': tab['evidence'], 'missing': tab['missing'], 'notes': tab['notes'],
    }
    if rel_semantics:
        out['relation_semantics'] = rel_semantics
    return out


# ══ Charter9 P0-1: 期限解析器+成熟度+三型入口 ══════════════════════════
UNPARSEABLE_HORIZON_VOCAB = ('当前', '未指明', '中期', '持续', '下阶段',
                             '战术配置', '会议间期间', '会后即刻')


def _month_end(y, m):
    import calendar
    return f'{y:04d}-{m:02d}-{calendar.monthrange(y, m)[1]:02d}'


def _add_months(iso_date, months):
    """自然月前移(月末钳制)——horizon 上界推算;与 horizon_start 同族语义。"""
    import datetime as _dt
    d = _dt.date.fromisoformat(str(iso_date)[:10])
    y, mo = d.year, d.month + int(months)
    while mo > 12:
        mo -= 12
        y += 1
    import calendar
    day = min(d.day, calendar.monthrange(y, mo)[1])
    return _dt.date(y, mo, day).isoformat()


def parse_view_horizon(text, publish_date=None):
    """观点期限文本 → 到期日(协调裁定②: 区间取上界;UNPARSEABLE 显式态)。

    CY2026/'2026年(全年)'→该年 12-31;'2027年3月'→该月末;ISO 日期→当日;
    '6-12个月'/'12个月'→publish+上限月数;'1年/两年'→publish+N 年(≤30 视为
    时长,4 位视为日历年);多时点(如 '12月+2027年3月')→取最晚(保守=更晚
    触发到期判定);当前/未指明/中期/持续/下阶段/战术配置/会议间期间→
    UNPARSEABLE。BIS 回顾性刊物无点位(forecasts 空)是真实 NOT_TESTABLE 面,
    由调用方按 forecasts 为空处理。"""
    import re
    s = str(text or '').strip()
    if not s:
        return {'state': 'unparseable', 'horizon_end': None,
                'basis': '期限文本为空'}
    absolutes = []
    m = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', s)
    if m:
        absolutes.append(f'{int(m.group(1)):04d}-{int(m.group(2)):02d}-'
                         f'{int(m.group(3)):02d}')
    # UBS 形 '2026-12'/'2027-03'(年-月无日)→月末;OECD 形裸 '2026'/'2027'
    # (年度点位)→年末(裁定②上界);ISO 前缀不被误拆(前后卫禁 '-数字')。
    m = re.search(r'(?<![\d-])(\d{4})-(\d{1,2})(?![\d-])', s)
    if m:
        absolutes.append(_month_end(int(m.group(1)), int(m.group(2))))
    # OECD 形 '2026-2027'(年度区间)→上界年末(裁定②;ISO 卫不吞两裸年)
    m = re.search(r'(?<![\d-])(\d{4})\s*[-~到至]\s*(\d{4})(?!\d)', s)
    if m:
        absolutes.append(f'{int(m.group(2)):04d}-12-31')
    m = re.search(r'(?<![\d-])(\d{4})(?!\d|-\d|年)', s)
    if m:
        absolutes.append(f'{int(m.group(1)):04d}-12-31')
    for kind, pat in (('cy', r'CY(\d{4})'),
                      ('year_full', r'(\d{4})\s*年(?:全年|年度)')):
        m = re.search(pat, s)
        if m:
            absolutes.append(f'{int(m.group(1)):04d}-12-31')
    m = re.search(r'(\d{4})\s*年\s*(\d{1,2})\s*月', s)
    if m:
        absolutes.append(_month_end(int(m.group(1)), int(m.group(2))))
    else:
        m = re.search(r'(?<!\d)(\d{4})\s*年(?!\d)', s)
        if m and not re.search(r'(\d{1,2})\s*个月|\d-\d+\s*个月', s):
            absolutes.append(f'{int(m.group(1)):04d}-12-31')
    durations = []
    m = re.search(r'(\d{1,2})\s*[-~到至]\s*(\d{1,2})\s*(?:个月|m)(?![a-zA-Z])', s)
    if m:
        durations.append(int(m.group(2)))          # 区间取上界(裁定②)
    else:
        m = re.search(r'(?<!\d)(\d{1,2})\s*(?:个月|m)(?![a-zA-Z0-9])', s)
        if m:
            durations.append(int(m.group(1)))
    years = None
    m = re.search(r'(?<!\d)([一两二三四五六七八九十]{1,2}|\d{1,2})\s*年(?!\d)', s)
    if m:
        cn = {'一': 1, '两': 2, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6,
              '七': 7, '八': 8, '九': 9, '十': 10}
        tok = m.group(1)
        years = cn.get(tok) if not tok.isdigit() else int(tok)
    else:
        m = re.search(r'(?<!\d)(\d{1,2})\s*y(?![a-zA-Z])', s, re.IGNORECASE)
        if m:
            years = int(m.group(1))
    if years is not None and 0 < years <= 30:
        durations.append(years * 12)
    if absolutes:
        return {'state': 'parsed', 'horizon_end': max(absolutes),
                'basis': (f'绝对时点 {len(absolutes)} 个取最晚(保守)'
                          if len(absolutes) > 1 else '绝对时点')}
    if durations and publish_date:
        months = max(durations)
        end = _add_months(publish_date, months)
        return {'state': 'parsed', 'horizon_end': end,
                'basis': f'时长 {months} 个月(区间取上界,publish {publish_date} 起算)'}
    if durations:
        return {'state': 'unparseable', 'horizon_end': None,
                'basis': f'时长型期限缺 publish_date 锚({text!r})'}
    if any(v in s for v in UNPARSEABLE_HORIZON_VOCAB):
        return {'state': 'unparseable', 'horizon_end': None,
                'basis': f'非期限词汇({s!r}∈UNPARSEABLE 词表)'}
    return {'state': 'unparseable', 'horizon_end': None,
            'basis': f'无法解析({s!r})'}


def maturity(horizon_text, publish_date, as_of_ymd):
    """成熟度: 到期日≤验证日=MATURED;未到=NOT_YET_TESTABLE;解析失败=
    UNPARSEABLE(护栏在两种非 MATURED 态都压制 relation)。"""
    p = parse_view_horizon(horizon_text, publish_date)
    if p['state'] != 'parsed':
        return {'state': 'UNPARSEABLE', 'horizon_end': None,
                'as_of': as_of_ymd, 'basis': p['basis']}
    end = p['horizon_end']
    as_of = str(as_of_ymd or '')[:10].replace('-', '') if as_of_ymd else ''
    matured = bool(as_of) and end.replace('-', '') <= as_of
    return {'state': 'MATURED' if matured else 'NOT_YET_TESTABLE',
            'horizon_end': end, 'as_of': as_of_ymd, 'basis': p['basis']}


def _since_publish_node(metric_id, unit, snapshot, publish_date):
    """mode B 专用: publish 之后的区间变动(严格>publish 的证据更新窗)。
    序列取数包 redirect_stdout(与 metric_window_changes 同款——采集档
    标准化进度打印不污染 CLI 单 JSON 契约)。"""
    import io
    from contextlib import redirect_stdout
    with redirect_stdout(io.StringIO()):
        series, err = wd.metric_series(metric_id, snapshot, ROOT)
    if series is None:
        return {'available': False, 'reason': f'无序列: {err}'}
    return rhq.interval_change(series['dates'], series['values'],
                               unit or series.get('unit'),
                               start=publish_date, end=snapshot.get('target_date'))


def _freshness_node(metric_id, snapshot, series_dates, horizon_end, registry):
    """到期验证新鲜度节点(Charter 10 §5.2,R22)。

    披露五要素: 预测到期日/实际观测日期(≤到期日的最后观测)/数据发布面
    (fact 级 release_date 实测优先,未入库如实 null+注册表登记旗标)/
    允许的数据滞后(按 frequency)/数据质量状态。到期日与最后观测的间隔
    超过允许滞后 → fresh=False(调用方须转证据不足,不得判对错)。"""
    m = (registry.get('by_id') or {}).get(metric_id) or {}
    freq = m.get('frequency')
    allowed = FRESHNESS_ALLOWED_LAG_DAYS.get(freq, FRESHNESS_DEFAULT_LAG_DAYS)
    le = [str(d)[:10] for d in series_dates if str(d)[:10] <= str(horizon_end)[:10]]
    last_obs = max(le) if le else None
    gap = None
    if last_obs:
        import datetime as _dt
        gap = (_dt.date.fromisoformat(str(horizon_end)[:10])
               - _dt.date.fromisoformat(last_obs)).days
    fact = next((f for f in (snapshot or {}).get('facts', [])
                 if f.get('metric_id') == metric_id), None)
    node = {
        'prediction_due': horizon_end,
        'actual_observation_date': last_obs,
        'gap_days': gap,
        'frequency': freq,
        'allowed_lag_days': allowed,
        'release_date': (fact or {}).get('release_date'),
        'release_date_available_registry': m.get('release_date_available'),
        'release_date_basis': ('fact 级 release_date 实测' if fact and
                               fact.get('release_date') else
                               '逐观测发布日未入库(观测日替代,vintage 累积中)'),
        'quality_status': (fact or {}).get('quality_status') or 'series_store',
        'fresh': bool(last_obs and gap is not None and gap <= allowed),
    }
    return node


def _filter_snapshot_le(snap, ymd):
    """快照截断到观测日 ≤ymd(R22 §5.4 二次过滤;mode A 两锚共用的唯一实现)。

    facts: obs>ymd 的原版丢弃,但截断序列尾值近似(level_source=
    series_tail_le_publish 家族,DEGRADED 披露,原观测日保留)——与 R5
    approx 分支同款语义;series_store: 逐指标截断日期/值。
    返回 (新 snap dict, {'dropped_series_obs': n, 'dropped_facts': n,
    'approx_facts': n})——vintage 分支凭此披露二次过滤执行面。"""
    series_store, dropped_obs = {}, 0
    for mid, ss in (snap.get('series_store') or {}).items():
        keep = [i for i, d in enumerate(ss.get('dates', []))
                if str(d)[:10].replace('-', '') <= ymd]
        dropped_obs += len(ss.get('dates', [])) - len(keep)
        series_store[mid] = {'dates': [ss['dates'][i] for i in keep],
                             'values': [ss['values'][i] for i in keep]}
    facts, dropped, approx = [], 0, 0
    for f in snap.get('facts') or []:
        if str(f.get('observation_date', ''))[:10].replace('-', '') <= ymd:
            facts.append(f)
            continue
        dropped += 1
        ss = series_store.get(f.get('metric_id')) or {}
        tail = [(d, v) for d, v in zip(ss.get('dates') or [],
                                       ss.get('values') or [])
                if v is not None]
        if tail:
            approx += 1
            facts.append({**f, 'value': tail[-1][1],
                          'observation_date': tail[-1][0],
                          'quality_status': 'DEGRADED',
                          'level_source': 'series_tail_le_publish',
                          'fact_observation_date': f.get('observation_date')})
    snap2 = {**snap, 'facts': facts, 'series_store': series_store}
    return snap2, {'dropped_series_obs': dropped_obs, 'dropped_facts': dropped,
                   'approx_facts': approx}


def verify_at_publish(view_id, registry, vmap, views_dir=None, directions=None,
                      root=ROOT, extra_metric_ids=None):
    """mode A 提出时证据: vintage 锚定 publish_date(裁定①含当日观测≤,
    切点日期随行披露)。

    快照选择: rp.vintage_dates 跨日 vintage 中 ≤publish 的最近日 →
    select_snapshot(同日最高修订);无该时点 vintage → 最新快照截断至
    publish_date(裁定⑦: 当时信息集近似,DEGRADED 标注随行——C席复核实证面);
    连快照都没有(干净clone)→ 如实 unavailable。
    截断近似的事实面(R5 2026-11-11): observation_date>publish 的事实原版
    直接丢弃——但 series_store 截断后仍含 ≤publish 观测(市场日频指标典型),
    遂以截断序列尾值近似 level(observation_date=尾值日期,
    level_source=series_tail_le_publish,quality_status=DEGRADED 随行披露,
    原观测日保留在 fact_observation_date);序列无 ≤publish 观测才真缺席。"""
    doc, reason = vs.get_view(view_id, views_dir)
    if doc is None:
        return {'ok': False, 'error': {'kind': 'view_not_found_or_quarantined',
                                       'message': reason}}
    import research_provenance as rp
    daily = os.path.join(root, 'data', 'daily')
    pymd = str(doc['publish_date']).replace('-', '')
    vints = [d for d in rp.vintage_dates(daily) if d <= pymd]
    vintage_note = None
    snap = None
    if vints:
        ymd = max(vints)
        snap, why = rp.select_snapshot(ymd, daily)
        if snap is not None:
            # R22 §5.4 二次过滤(OPEN_ISSUES R1-MINOR-4 收口): vintage 快照
            # 不盲信——逐观测再截断到 ≤publish(防采集面夹带未来观测前视)。
            snap, filt = _filter_snapshot_le(snap, pymd)
            leaked = filt['dropped_series_obs'] + filt['dropped_facts']
            vintage_note = {'anchor': 'vintage_snapshot', 'cutoff': ymd,
                            'degraded': False,
                            'obs_le_publish_filter': filt,
                            'note': f'≤publish 最近跨日 vintage 快照(切点 {ymd},'
                                    '含当日观测,裁定①);obs≤publish 二次过滤'
                                    f"已执行(滤 {leaked} 项,R22 §5.4)"}
    if snap is None:
        snap, note = wd.latest_snapshot(root)
        if snap is None:
            return {'ok': False, 'mode': 'A',
                    'error': {'kind': 'vintage_unavailable',
                              'message': f'无 vintage≤{pymd} 且无本地快照({note})'
                                         '——干净clone 无历史数据,mode A 不可执行'}}
        snap, filt = _filter_snapshot_le(snap, pymd)
        vintage_note = {'anchor': 'approx_filtered', 'cutoff': doc['publish_date'],
                        'degraded': True,
                        'obs_le_publish_filter': filt,
                        'note': '无该时点 vintage 快照→最新快照截断至 publish_date'
                                '(当时信息集近似,DEGRADED;裁定⑦,C席复核实证面;'
                                'obs>publish 事实以截断序列尾值近似,'
                                'level_source=series_tail_le_publish)'}
    out = verify(view_id, snap, registry, vmap, views_dir=views_dir,
                 directions=directions, mode='A',
                 target_ymd=min(str(snap.get('target_date')), pymd),
                 extra_metric_ids=extra_metric_ids)
    out['mode_a_anchor'] = vintage_note
    return out


def load_forecast_target_map(path=None):
    """config/forecast_target_map.json: forecast.target 文本→metric 种子映射。"""
    p = path or os.path.join(ROOT, 'config', 'forecast_target_map.json')
    with open(p, encoding='utf-8') as f:
        m = json.load(f)
    if not isinstance(m.get('targets'), dict) or not m['targets']:
        raise ValueError('forecast_target_map.json 须含非空 targets 对象')
    return m


def _resolve_forecast_metric(target, target_map):
    """确定性映射: 精确→最长包含;未映射→None(NOT_MACHINE_VERIFIABLE,禁猜)。"""
    t = str(target or '').strip()
    if t in target_map['targets']:
        return target_map['targets'][t]
    hits = [(len(k), v) for k, v in target_map['targets'].items() if k in t]
    return max(hits)[1] if hits else None


_DIR_UP = ('上行', '上调', '升', '涨', '高于', '走高', '加息', '走强')
_DIR_DOWN = ('下行', '下调', '降', '跌', '低于', '走低', '降息', '走弱')
# 否定/停续类表述先拦(E席审计词表护栏,2026-11-11): '不再加息'不得判 up、
# 'no further cuts' 不得判 down——方向不明确如实 None,不猜。
_DIR_NEGATION = ('不再', '停止', '结束', '暂停', '维持', '无进一步')
_DIR_NEGATION_RE = re.compile(r'\b(no further|end of|pause|halt|hold)\b', re.I)
# EN 词用词边界匹配(子串会把 'supply-driven' 判 up——'sup' 含 'up')
_DIR_UP_RE = re.compile(r'\b(up|raises?d?|raising|higher|bullish)\b', re.I)
_DIR_DOWN_RE = re.compile(r'\b(down|cuts?|lower|bearish)\b', re.I)


def _parse_direction(text):
    s = str(text or '')
    if any(k in s for k in _DIR_NEGATION) or _DIR_NEGATION_RE.search(s):
        return None
    up = any(k in s for k in _DIR_UP) or bool(_DIR_UP_RE.search(s))
    down = any(k in s for k in _DIR_DOWN) or bool(_DIR_DOWN_RE.search(s))
    if up and not down:
        return 'up'
    if down and not up:
        return 'down'
    return None


def verify_expiry(view_id, snapshot, registry, vmap, views_dir=None,
                  target_map=None):
    """mode C 到期验证: 每条 forecast 独立判定(六标签聚合在 P0-2 VP sidecar)。

    判定序(确定性): 期限不可解析→UNPARSEABLE_HORIZON;未到期→NOT_YET_TESTABLE;
    target 未映射→NOT_MACHINE_VERIFIABLE;序列不足→INSUFFICIENT_DATA;
    到期日附近观测滞后超允许阈值(frequency 驱动)→INSUFFICIENT_DATA
    (Charter 10 §5.2 新鲜度门,五要素随 freshness 节披露);
    方向不可解析(点位型)→LEVEL_TARGET(报告实际值与点位差,不判对错);
    方向可解析→报价方向语义换算(Charter 10 §5.1: 报价对计价货币侧/
    收益率-价格侧反转,config/metric_direction_semantics.json 驱动,
    direction_hint 语义=指标数值方向)后 supports/against/neutral
    (publish→horizon_end 区间变动,interval_change 同口径)。
    序列取数 root 固定引擎根(metric_series 内部 load_registry(root) 须读到
    config/metric_registry.json;序列本身优先快照 series_store——与
    _since_publish_node 同款,data 沙箱 root 只用于快照解析侧)。"""
    doc, reason = vs.get_view(view_id, views_dir)
    if doc is None:
        return {'ok': False, 'error': {'kind': 'view_not_found_or_quarantined',
                                       'message': reason}}
    publish = doc['publish_date']
    as_of = snapshot.get('target_date')
    view_mat = maturity(doc.get('view_horizon'), publish, as_of)
    rows = []
    for i, f in enumerate(doc.get('forecasts') or [], 1):
        h = parse_view_horizon(f.get('horizon'), publish)
        row = {'index': i, 'target': f.get('target'),
               'value_or_direction': f.get('value_or_direction'),
               'horizon_raw': f.get('horizon'), 'horizon_end': h['horizon_end'],
               'horizon_basis': h['basis']}
        if h['state'] != 'parsed':
            row['verdict'] = 'UNPARSEABLE_HORIZON'
            rows.append(row)
            continue
        if str(h['horizon_end']).replace('-', '') > str(as_of).replace('-', ''):
            row['verdict'] = 'NOT_YET_TESTABLE'
            row['note'] = f"到期 {h['horizon_end']} > 验证日 {as_of}(未到期不判)"
            rows.append(row)
            continue
        metric = (_resolve_forecast_metric(f.get('target'), target_map)
                  if target_map else None)
        if metric is None:
            row['verdict'] = 'NOT_MACHINE_VERIFIABLE'
            row['note'] = 'target 未登记 forecast_target_map(映射扩充=Agent层,禁猜)'
            rows.append(row)
            continue
        row['metric_id'] = metric
        import io
        from contextlib import redirect_stdout
        with redirect_stdout(io.StringIO()):
            series, err = wd.metric_series(metric, snapshot, ROOT)
        if series is None:
            row['verdict'] = 'INSUFFICIENT_DATA'
            row['note'] = f'无序列: {err}'
            rows.append(row)
            continue
        iv = rhq.interval_change(series['dates'], series['values'],
                                 series.get('unit'), start=publish,
                                 end=h['horizon_end'])
        if iv.get('available') is False:
            row['verdict'] = 'INSUFFICIENT_DATA'
            row['note'] = iv.get('reason')
            rows.append(row)
            continue
        row['interval_change'] = iv
        # R22 §5.2 新鲜度门: 到期日附近无足够新鲜观测=证据不足,不判对错
        fresh = _freshness_node(metric, snapshot, series['dates'],
                                h['horizon_end'], registry)
        row['freshness'] = fresh
        if not fresh['fresh']:
            row['verdict'] = 'INSUFFICIENT_DATA'
            row['note'] = (f"到期 {h['horizon_end']} 附近无足够新鲜观测: "
                           f"最后观测 {fresh['actual_observation_date']}"
                           f"(滞后 {fresh['gap_days']} 天 > 允许 "
                           f"{fresh['allowed_lag_days']} 天,"
                           f"{fresh['frequency'] or '未登记'}频)——证据不足,"
                           '不判预测正确或错误(Charter 10 §5.2)')
            rows.append(row)
            continue
        actual = None
        for k in ('pp_change', 'pct_change', 'abs_change'):
            if iv.get(k) is not None:
                actual = 'up' if iv[k] > 0 else 'down' if iv[k] < 0 else 'flat'
                break
        hint = _parse_direction(f.get('value_or_direction'))
        if hint is None:
            row['verdict'] = 'LEVEL_TARGET'
            row['note'] = ('点位/幅度型目标——报告实际区间变动与点位,判对错'
                           '需语义层(六标签聚合在 VP sidecar, P0-2)')
            last = [d for d in series['dates'] if d <= h['horizon_end']]
            if last:
                row['actual_observation'] = {
                    'date': last[-1],
                    'value': series['values'][series['dates'].index(last[-1])]}
        else:
            # R22 §5.1 方向语义: 报价对/收益率类指标,措辞主体与指标数值方向
            # 可能相反("日元升值"=USDJPY 降)。换算确定性(config 驱动),
            # 披露节点随行;direction_hint 语义=指标数值方向(换算后)。
            hint, dnode = dsem_mod.apply_metric_direction_semantics(
                hint, metric, [f.get('target'), f.get('value_or_direction')])
            row['direction_hint'] = hint
            if dnode is not None:
                row['direction_semantics'] = dnode
            row['actual_direction'] = actual
            row['verdict'] = ('supports' if actual == hint else
                              'against' if actual in ('up', 'down') else 'neutral')
        rows.append(row)
    if not (doc.get('forecasts') or []):
        note = 'forecasts 为空(回顾性刊物/纯立场档,如 BIS)——无可到期验证点位'
    else:
        note = None
    return {
        'ok': True, 'view_id': view_id, 'mode': 'C',
        'institution': doc['institution']['name'],
        'publish_date': publish, 'as_of': as_of,
        'snapshot_id': snapshot.get('snapshot_id'),
        'view_maturity': view_mat,
        'n_forecasts': len(doc.get('forecasts') or []),
        'forecast_verdicts': rows,
        'no_forecasts_note': note,
        'revision_anchors': [
            {'date': r.get('date'), 'anchor': 'independent_subject'}
            for r in (doc.get('revisions') or [])],
        'determinism_note': '到期判定=区间变动方向机械比对(publish→horizon_end,'
                            'interval_change 同口径);期限取上界(裁定②);'
                            '未到期/不可解析/未映射一律显式态不猜',
    }


def _resolve_snapshot(snapshot_id=None, root=ROOT):
    """快照解析: 显式 id→research_archive.load_snapshot_by_id(archive save
    同款,短形容忍);缺省→workbench_data.latest_snapshot(默认行为不变)。

    返回 (snapshot|None, 说明)。(None, 原因) 时调用方按 kind 分流:
    显式指定失败=snapshot_not_found(用法错), 缺省无快照=no_snapshot(执行错)。"""
    if not snapshot_id:
        return wd.latest_snapshot(root)
    import research_archive as ra
    sid = snapshot_id
    if not sid.startswith('research_snapshot_'):
        sid = 'research_snapshot_' + sid         # 容忍短形 20261110_v4
    return ra.load_snapshot_by_id(sid, os.path.join(root, 'data', 'daily'))


def main(argv=None, data_root=None):
    """data_root: 快照查找根(默认 ROOT;测试注入沙箱用——注册表/映射仍走
    引擎根,与 verify 的 views_dir 同款注入缝)。"""
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print(__doc__)
        return 2
    view_id = argv[0] if not argv[0].startswith('--') else None
    directions = None
    snapshot_id = None
    mode = None
    rest = argv[1:] if view_id else argv
    j = 0
    while j < len(rest):
        if rest[j] == '--directions' and j + 1 < len(rest):
            try:
                directions = json.loads(rest[j + 1])
                assert isinstance(directions, dict)
            except (ValueError, AssertionError):
                print(json.dumps({'ok': False, 'error': {
                    'kind': 'bad_directions', 'message': '--directions 须为 {"METRIC":"up|down"} JSON'}},
                    ensure_ascii=False))
                return 2
            j += 2
        elif rest[j] == '--mode' and j + 1 < len(rest):
            mode = rest[j + 1].strip().upper()
            if mode not in ('A', 'B', 'C', 'ALL'):
                print(json.dumps({'ok': False, 'error': {
                    'kind': 'bad_mode', 'message': '--mode 须为 A|B|C|all(A=提出时证据'
                            '/B=当前证据更新/C=到期验证;缺省=legacy 最新快照行为)'}},
                    ensure_ascii=False))
                return 2
            j += 2
        elif rest[j] == '--snapshot-id' and j + 1 < len(rest):
            snapshot_id = rest[j + 1].strip()
            if not snapshot_id:
                print(json.dumps({'ok': False, 'error': {
                    'kind': 'bad_snapshot_id', 'message': '--snapshot-id 须为非空 research_snapshot_YYYYMMDD[_vN]'}},
                    ensure_ascii=False))
                return 2
            j += 2
        else:
            print(json.dumps({'ok': False, 'error': {
                'kind': 'usage', 'message': f'无法识别参数: {rest[j]}(用法见 --help 或模块 docstring)'}},
                ensure_ascii=False))
            return 2
    if not view_id:
        print(json.dumps({'ok': False, 'error': {
            'kind': 'missing_view_id', 'message': '首参须为 VIEW-YYYYMMDD-NNN'}},
            ensure_ascii=False))
        return 2
    snap, note = _resolve_snapshot(snapshot_id, data_root or ROOT)
    if snap is None:
        kind = 'snapshot_not_found' if snapshot_id else 'no_snapshot'
        print(json.dumps({'ok': False, 'error': {'kind': kind,
                                                 'message': note}}, ensure_ascii=False))
        return 2 if snapshot_id else 1
    reg = wd.load_registry(ROOT)
    try:
        vmap = load_map()
    except (OSError, ValueError) as e:
        print(json.dumps({'ok': False, 'error': {'kind': 'bad_map',
                                                 'message': str(e)}}, ensure_ascii=False))
        return 1
    if mode in ('A', 'ALL'):
        out_a = verify_at_publish(view_id, reg, vmap, directions=directions,
                                  root=data_root or ROOT)
        if mode == 'A':
            print(json.dumps(out_a, ensure_ascii=False, indent=2, default=str))
            return 0 if out_a.get('ok') else 1
    if mode in ('B', 'ALL'):
        out_b = verify(view_id, snap, reg, vmap, directions=directions,
                       mode='B')
        if mode == 'B':
            print(json.dumps(out_b, ensure_ascii=False, indent=2, default=str))
            return 0 if out_b.get('ok') else 1
    if mode in ('C', 'ALL'):
        try:
            tmap = load_forecast_target_map()
        except (OSError, ValueError) as e:
            print(json.dumps({'ok': False, 'error': {'kind': 'bad_target_map',
                                                     'message': str(e)}},
                             ensure_ascii=False))
            return 1
        out_c = verify_expiry(view_id, snap, reg, vmap, target_map=tmap)
        if mode == 'C':
            print(json.dumps(out_c, ensure_ascii=False, indent=2, default=str))
            return 0 if out_c.get('ok') else 1
    if mode == 'ALL':
        print(json.dumps({'ok': all(o.get('ok') for o in (out_a, out_b, out_c)
                                    if o is not None),
                          'view_id': view_id, 'mode': 'all',
                          'A': out_a, 'B': out_b, 'C': out_c},
                         ensure_ascii=False, indent=2, default=str))
        return 0
    out = verify(view_id, snap, reg, vmap, directions=directions)
    print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
    return 0 if out.get('ok') else 1


if __name__ == '__main__':
    sys.exit(main())
