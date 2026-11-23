#!/usr/bin/env python3
"""Audit-R32 任务1: 证据口径统一——截止规则放在取数入口。

单一 seam: 运行级环境变量 IA_EVIDENCE_ASOF(ISO 日期)。orchestrator 在第一
次取数前置位(plan 段,与快照/注册表/日历钉死同一生命周期 try/finally 释放);
attach/report/archive/replay 自 report.run.evidence_gate.as_of 重建置位
(agent_judgment.work_order_pins);子进程(S3–S8 各 ia_cli 子命令)继承 env——
workbench_data.latest_snapshot() 与 metric_series() 两个**取数入口**返回截止
视图,S3–S8/L1/L2/证据索引/研究席信封/机器契约/报告/归档/重放共用同一证据
口径(不靠下游各自记得截断)。

三条证据资格规则(任一不满足=不可引用证据,入口即剔除):
  ① 晚观测: 观测日 > as_of;
  ② 晚发布: 观测日 ≤ as_of 但发布日 > as_of——历史截止(as_of 早于快照
     版本日)时发布日=日历实录 first_publish 优先/RELEASE_RULES 推定兜底
     (与点锚面同一 research_map_planner._visible_publish 入口);as_of=快照
     版本日时快照在场本身即当时可得证明(推定规则误差不误剔已采集事实),
     只剔 ①;
  ③ 当时不可得的数据版本: 值来自晚于 as_of 的数据版本——
     a. 数据树有 target_date ≤ as_of 的快照版本→取该版本(as_of_vintage);
     b. 无 as-of 版本: 注册表**未声明修订**的序列值不随版本变
        (not_declared_revised,可引用);注册表声明最新修订口径
        (release_semantics 含 latest_vintage: GDP/HICP/CPI/货币存量/估值
        等 9 项)的序列,观测须**已过首个修订周期**(首发日+首修时滞
        ≤ as_of: 月频 0/季频+1月,见 _REVISION_CYCLE_MONTHS)才可引用
        (vintage=latest_revision_only,
        不得表述为当时首发值);未过首个修订周期的观测=当时只见首发值而
        手头只有最新修订值→数据版本当时不可得,逐点剔除;整条无可引用
        观测=空壳+evidence_gate_excluded 原因(下游「面在场有效 0」如实
        缺席)。采集档通道同理(修订口径序列只取采集日 ≤ as_of 的最新采集
        档,采集日=版本日;无→版本不可得)。

截止视图=源快照深拷贝派生(源字节不变——冻结摘要/归档/重放仍绑源包);
事实(快照 facts)晚于截止/晚发布/版本不可得者自截止序列重建(≤as_of 且
已发布的最新观测,derived 经 fact_engine.compute_period_returns 同一口径
重算,m12=去年同月);无可重建序列者剔除=该格截至 as_of 不可得(如实缺席)。
视图顶层落 evidence_gate 块(规则/剔除计数/版本口径/来源快照身份)随
report.run 落档,读者可核。gate 对同一(as_of, 源快照, 日历, 注册表, 数据树
版本集)确定,重放同算同核。
"""
import copy
import datetime as _dt
import glob
import json
import os
import re

ENV_KEY = 'IA_EVIDENCE_ASOF'
ISO_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
# 规则②只对「发布面可能晚于截止」的近端观测逐点查发布日(推定时滞上限
# 45 天+余量;更早观测按任何在册规则都已发布)——日频 2500 点序列逐点查
# 日历是 O(n×entries) 浪费。
_PUBLISH_HORIZON_DAYS = 62
# 规则③b: 声明修订序列的观测须已过的首个修订周期(按频率族):
# 月频=0——在册发布规则/日历实录已对齐次月中旬终值发布时点(HICP 终值/
# CPI 月中发布),发布即可引用,后续修订罕见且随行标注;季频=+1 月——GDP
# 首发为速报/advance 预估值,次月才有第二估值,未过首修=当时只见预估值而
# 手头只有最新修订值(数据版本当时不可得)。
_REVISION_CYCLE_MONTHS = {'monthly': 0, 'quarterly': 1}


def evidence_asof():
    """运行级研究截止日(ISO)或 None(未置位=原语义,零回归)。"""
    v = os.environ.get(ENV_KEY)
    return v if (v and ISO_RE.match(v)) else None


def _iso_of_ymd(ymd):
    t = str(ymd or '')
    if len(t) >= 8 and t[:8].isdigit():
        return '%s-%s-%s' % (t[:4], t[4:6], t[6:8])
    return None


def _compact(iso):
    return str(iso or '').replace('-', '')[:8]


def _add_months(iso, n):
    """ISO 日期 + n 个自然月(日夹紧到月末)。"""
    import calendar
    d = _dt.date.fromisoformat(iso[:10])
    tot = d.year * 12 + (d.month - 1) + n
    y, m = tot // 12, tot % 12 + 1
    return '%04d-%02d-%02d' % (y, m, min(d.day, calendar.monthrange(y, m)[1]))


def is_historical_view(as_of, snapshot):
    """历史截止=as_of 早于数据版本日(快照 target_date)。无快照/无版本日
    →按历史视图处理(规则②③从严;未截止快照调用方自带时同样受约束)。"""
    if not as_of or not isinstance(snapshot, dict):
        return True
    vtd = _iso_of_ymd(snapshot.get('target_date'))
    return bool(vtd) and as_of < vtd


def _published_by(mid, freq, obs_iso, as_of):
    """规则②: 观测的发布日 ≤ as_of 才当时可得。返回 (ok, publish_iso|None)。"""
    try:
        horizon = (_dt.date.fromisoformat(as_of)
                   - _dt.timedelta(days=_PUBLISH_HORIZON_DAYS)).isoformat()
    except ValueError:
        horizon = as_of
    if obs_iso <= horizon:
        return True, None
    pub, _basis = visible_publish(mid, freq, obs_iso)
    if pub and pub > as_of:
        return False, pub
    return True, pub


def visible_publish(mid, freq, obs_iso):
    """发布日统一入口(日历实录优先/推定兜底;IA_CALENDAR_PIN 钉死在场时读
    冻结副本)。→ (publish_iso|None, basis_text)。"""
    import research_map_planner as rmp
    return rmp._visible_publish(mid, freq, obs_iso)


def version_available_on(mid, freq, obs_iso):
    """规则③b: 声明修订序列的观测「当时可得的版本」=首发后首个修订版
    发布日(首发日+一个发布周期)。→ (version_iso|None, first_publish|None)。"""
    pub, _b = visible_publish(mid, freq, obs_iso)
    if not pub:
        return None, None
    return _add_months(pub, _REVISION_CYCLE_MONTHS.get(freq, 0)), pub


def gate_series(mid, freq, dates, values, as_of, enforce_publication=True,
                revised=False):
    """序列截止视图: 剔晚观测(①)/晚发布(②)/版本不可得(③b)。→ (dates',
    values', info)。revised=注册表声明最新修订口径且无 as-of 版本。

    非规范日期串原样保留(交由 effective_series 清洗,不在此猜测截断);
    info 逐项计数+首个被剔观测(原因+发布日),披露面用。"""
    keep_d, keep_v = [], []
    n_late_obs = n_late_pub = n_version = 0
    first_dropped = None

    def _drop(d, reason, pub=None, extra=None):
        nonlocal first_dropped
        if first_dropped is None:
            first_dropped = {'date': d, 'reason': reason}
            if pub:
                first_dropped['publish'] = pub
            if extra:
                first_dropped.update(extra)
    for d, v in zip(dates or [], values or []):
        ds = str(d)[:10]
        if ISO_RE.match(ds):
            if ds > as_of:
                n_late_obs += 1
                _drop(ds, 'late_observation')
                continue
            if enforce_publication:
                ok, pub = _published_by(mid, freq, ds, as_of)
                if not ok:
                    n_late_pub += 1
                    _drop(ds, 'late_publication', pub)
                    continue
            if revised:
                ver, pub = version_available_on(mid, freq, ds)
                if ver and ver > as_of:
                    n_version += 1
                    _drop(ds, 'data_version_unavailable', pub,
                          {'version_available_on': ver})
                    continue
        keep_d.append(d)
        keep_v.append(v)
    return keep_d, keep_v, {
        'n_in': len(dates or []), 'n_kept': len(keep_d),
        'n_late_observation': n_late_obs, 'n_late_publication': n_late_pub,
        'n_version_unavailable': n_version,
        'first_dropped': first_dropped,
        'last_eligible': keep_d[-1] if keep_d else None}


def vintage_snapshot_path(root, as_of, exclude=None):
    """规则③a: 数据树内 target_date ≤ as_of 的最新快照版本(as-of vintage;
    同日修订版 _v2 优先);无→None。exclude=当前冻结源(自身不作 vintage)。"""
    daily = os.path.join(root, 'data', 'daily')
    best = None
    for p in sorted(glob.glob(os.path.join(daily, 'research_snapshot_*.json'))):
        m = re.match(r'research_snapshot_(\d{8})', os.path.basename(p))
        if not m:
            continue
        iso = _iso_of_ymd(m.group(1))
        if iso and iso <= as_of and os.path.abspath(p) != os.path.abspath(exclude or ''):
            if best is None or (iso, p) >= best:
                best = (iso, p)
    return best[1] if best else None


def _file_ymd(path):
    m = re.search(r'(\d{8})', os.path.basename(path or ''))
    return m.group(1) if m else None


def collection_vintage_files(files, as_of):
    """规则③b(采集档通道): 修订口径序列只取采集日 ymd ≤ as_of 的最新采集档
    (采集日=该档版本日)。→ (可用档列表|原列表, 被排除的最新档日|None)。
    非历史视图/as_of 未置位=原列表。"""
    if not as_of or not files:
        return files, None
    ac = _compact(as_of)
    keep = [f for f in files
            if _file_ymd(f) is None or _file_ymd(f) <= ac]
    if len(keep) == len(files):
        return files, None
    return keep, _file_ymd(files[-1])


def is_revised(meta):
    """注册表修订口径: release_semantics 含 latest_vintage(与地图面
    research_map_planner._vintage_semantics 同一判据)=最新修订值,非当时
    首发值。"""
    return 'latest_vintage' in str((meta or {}).get('release_semantics') or '')


def _excluded_shell(ser, as_of, reason, detail):
    """规则③剔除后整条无可引用观测的序列面: 空壳+原因(下游「面在场有效
    0」如实缺席,metric_series 返回原因文本,不回落采集档通道取更晚版本)。"""
    return {'dates': [], 'values': [],
            'evidence_gate_excluded': {
                'as_of': as_of, 'reason': reason, 'detail': detail,
                'source_last': (ser.get('dates') or [None])[-1] if ser else None}}


def _rebuild_fact(fact, meta, dates, values, as_of, vintage_label):
    """晚于截止的快照事实→自截止序列重建(≤as_of 最新有效观测+同口径
    derived);序列无有效观测→None(该格截至 as_of 不可得)。"""
    import fact_engine as fe
    import research_history_query as rhq
    cd, cv, cst = rhq.effective_series(dates, values)
    if not cd:
        return None
    derived = fe.compute_period_returns(
        cd, cv, meta.get('unit'), meta.get('calendar'), as_of=as_of)
    end = derived.get('end') if isinstance(derived, dict) else None
    if not end:
        return None
    nf = copy.deepcopy(fact)
    mid = fact.get('metric_id')
    nf.update(value=end['value'], observation_date=end['date'],
              fact_id=f'{mid}@{end["date"]}', as_of=as_of, derived=derived,
              evidence_gate={
                  'rebuilt_at_as_of': True,
                  'source_observation_date': fact.get('observation_date'),
                  'vintage': vintage_label,
                  'n_series_eligible': cst.get('n_observations', len(cd))})
    nf['issues'] = list(fact.get('issues') or []) + [
        '证据口径(Audit-R32 任务1): 快照事实观测日 %s 晚于研究截止 %s、'
        '发布晚于截止或数据版本当时不可得——按截止序列重建为 ≤截止且'
        '已发布的最新观测 %s' % (fact.get('observation_date'), as_of,
                                end['date'])]
    return nf


def _deep_copy(obj):
    """快照为纯 JSON 数据(str/int/float/list/dict/None): json 往返深拷贝
    比 copy.deepcopy 快数倍(88 序列×2500 点);失败回落 deepcopy。"""
    try:
        return json.loads(json.dumps(obj))
    except (TypeError, ValueError):
        return copy.deepcopy(obj)


def gate_snapshot(snap, as_of, root=None, registry=None):
    """快照截止视图(取数入口 latest_snapshot 消费)。snap 非 dict/无 as_of
    →原样返回。视图=深拷贝派生,源快照对象不改。"""
    if not isinstance(snap, dict) or not as_of:
        return snap
    import workbench_data as wd
    reg_by_id = registry['by_id'] if registry and registry.get('by_id') \
        else wd.load_registry(root)['by_id']
    src_td = _iso_of_ymd(snap.get('target_date')) or ''
    historical = bool(src_td and as_of < src_td)
    out = _deep_copy(snap)
    # 规则③a: as-of vintage 版本优先(数据树有 ≤as_of 的快照版本时)
    vint_path = vintage_snapshot_path(root, as_of) if (root and historical) \
        else None
    vintage, vint_err = None, None
    if vint_path:
        try:
            with open(vint_path, encoding='utf-8') as f:
                vintage = json.load(f)
        except (OSError, ValueError) as e:
            vintage, vint_err = None, f'{type(e).__name__}: {e}'
    vss = (vintage or {}).get('series_store') or {}
    vfacts = {f.get('metric_id'): f
              for f in (vintage or {}).get('facts') or []}
    ss = out.get('series_store') or {}
    per_series, excluded = {}, []
    n_obs_dropped = n_version_dropped = 0
    for mid in list(ss):
        ser = ss[mid] or {}
        meta = reg_by_id.get(mid) or {}
        freq = meta.get('frequency')
        src = vss.get(mid) if (vintage and mid in vss) else ser
        vkind = ('as_of_vintage' if src is not ser
                 else ('latest_revision_only' if historical
                       else 'snapshot_vintage'))
        revised = (vkind == 'latest_revision_only' and is_revised(meta))
        gd, gv, info = gate_series(
            mid, freq, (src or {}).get('dates'), (src or {}).get('values'),
            as_of, enforce_publication=historical, revised=revised)
        if not gd and (info['n_in'] or 0) > 0:
            # 整条无可引用观测: 空壳+原因(规则③b 版本不可得 / ①② 全剔)
            _why = ('latest_revision_no_version_available'
                    if revised else 'no_eligible_observation')
            ss[mid] = _excluded_shell(
                ser, as_of, _why,
                ('注册表声明最新修订口径(release_semantics=latest_vintage)且'
                 '数据树无 target_date≤%s 的快照版本;序列内观测均未过首个'
                 '修订周期(当时只见首发值)——最新修订值不得作为可引用证据'
                 % as_of) if revised else
                ('截止视图内无 ≤as_of 且已发布的观测(晚观测 %d/晚发布 %d)'
                 % (info['n_late_observation'], info['n_late_publication'])))
            excluded.append(mid)
        else:
            ss[mid] = dict(ser, dates=gd, values=gv)
        # 历史截止无 as-of 版本而注册表未声明修订→值不随版本变(可引用)
        info['vintage'] = ('not_declared_revised'
                           if vkind == 'latest_revision_only'
                           and not revised else vkind)
        info['excluded'] = mid in excluded
        n_obs_dropped += (info['n_late_observation']
                          + info['n_late_publication'])
        n_version_dropped += info['n_version_unavailable']
        per_series[mid] = {k: info[k] for k in (
            'n_in', 'n_kept', 'n_late_observation', 'n_late_publication',
            'n_version_unavailable', 'first_dropped', 'last_eligible',
            'vintage', 'excluded')}
    ex_set = set(excluded)
    # 事实面: ≤as_of 且已发布且版本可得者保留(版本口径随行);其余自截止
    # 序列重建;序列被剔除者=事实不可引用(剔除并计数)
    facts, seen = [], set()
    n_fact_kept = n_fact_rebuilt = n_fact_dropped = n_fact_version = 0
    for f in snap.get('facts') or []:
        mid = f.get('metric_id')
        meta = reg_by_id.get(mid) or {}
        freq = meta.get('frequency')
        od = str(f.get('observation_date') or '')[:10]
        ps = per_series.get(mid) or {}
        if mid in ex_set:
            n_fact_version += 1
            continue

        def _elig(obs_iso, revised):
            # 快照版本日视图(as_of=target_date)=快照在场即当时可得: 只剔晚
            # 观测,发布日推定不适用(周频/月频末点按推定滞后会误剔快照自有
            # 事实);历史截止视图才按规则②核发布日。
            if not (ISO_RE.match(obs_iso) and obs_iso <= as_of):
                return False
            if historical and \
                    not _published_by(mid, freq, obs_iso, as_of)[0]:
                return False
            if revised:
                ver, _p = version_available_on(mid, freq, obs_iso)
                if ver and ver > as_of:
                    return False
            return True
        vf = vfacts.get(mid) if vintage else None
        if (vf is not None
                and str(vf.get('observation_date') or '')[:10] <= as_of
                and _published_by(mid, freq,
                                  str(vf.get('observation_date'))[:10],
                                  as_of)[0]):
            nf = copy.deepcopy(vf)
            nf['evidence_gate'] = {'vintage': 'as_of_vintage',
                                   'source_snapshot_id': vintage.get(
                                       'snapshot_id')}
            facts.append(nf)
            seen.add(mid)
            n_fact_kept += 1
            continue
        if _elig(od, ps.get('vintage') == 'latest_revision_only'):
            nf = copy.deepcopy(f)
            nf['evidence_gate'] = {'vintage': ps.get(
                'vintage', 'snapshot_vintage')}
            facts.append(nf)
            seen.add(mid)
            n_fact_kept += 1
            continue
        if mid in ss and ss[mid].get('dates'):
            nf = _rebuild_fact(
                f, meta, ss[mid]['dates'], ss[mid]['values'], as_of,
                ps.get('vintage', 'snapshot_vintage'))
            if nf is not None:
                facts.append(nf)
                seen.add(mid)
                n_fact_rebuilt += 1
                continue
        n_fact_dropped += 1
        if mid in ex_set or (ps.get('n_version_unavailable') or 0) > 0:
            n_fact_version += 1
    # 无快照事实但在册序列存在的指标(如 DFEDTARU): 不凭空造事实行(原
    # 快照无=原口径无),只随序列面供 S4/点值面消费。
    out['facts'] = facts
    if isinstance(out.get('series_store_clean'), dict):
        out['series_store_clean'] = {
            mid: dict(out['series_store_clean'].get(mid) or {},
                      n_observations=(per_series.get(mid) or {}).get(
                          'n_kept', 0))
            for mid in per_series}
    out['target_date'] = _compact(as_of)
    out['research_as_of'] = as_of
    out['evidence_gate'] = {
        'discipline': 'r32',
        'as_of': as_of,
        'source_snapshot_id': snap.get('snapshot_id'),
        'source_target_date': src_td,
        'historical_view': historical,
        'publication_basis': ('calendar_first_publish|release_rules'
                              if historical else 'snapshot_presence'),
        'rules': ['①观测日≤as_of',
                  '②发布日≤as_of(历史截止: 日历实录优先/RELEASE_RULES 推定)',
                  '③值版本: as-of 快照版本优先;无则注册表未声明修订=值不随'
                  '版本变(可引用);声明最新修订口径=观测须已过首个修订周期'
                  '(首发日+1发布周期≤as_of),否则当时数据版本不可得逐点剔除'],
        'vintage': {
            'basis': ('as_of_vintage' if vintage else
                      ('no_asof_vintage_snapshot' if historical
                       else 'snapshot_vintage')),
            'vintage_snapshot': (os.path.relpath(vint_path, root)
                                 if vint_path and root else vint_path),
            'vintage_snapshot_id': (vintage or {}).get('snapshot_id'),
            'vintage_error': vint_err,
            'revised_series': sorted(
                mid for mid, i in per_series.items()
                if i.get('vintage') == 'latest_revision_only'),
            'excluded_series': sorted(excluded)},
        'counts': {
            'facts_kept': n_fact_kept, 'facts_rebuilt': n_fact_rebuilt,
            'facts_dropped': n_fact_dropped,
            'facts_excluded_version': n_fact_version,
            'series_observations_dropped': n_obs_dropped,
            'series_observations_version_unavailable': n_version_dropped,
            'series_excluded': len(excluded),
            'series_n': len(per_series)},
        'series': per_series,
        'note': ('截止视图(历史截止): 晚观测/晚发布不入证据面;注册表声明'
                 '最新修订口径的序列只引用已过首个修订周期的观测(值=最新'
                 '修订版,不得表述为当时首发值),未过者=当时数据版本不可得'
                 if historical else
                 '截止视图=快照版本日(as_of=target_date): 快照在场即当时'
                 '可得,证据面与源快照一致(只剔晚观测)')}
    return out


def apply(snapshot, root=None):
    """取数入口统一调用: IA_EVIDENCE_ASOF 在场→截止视图;否则原样。

    不做跨调用缓存(快照对象每次重新装载,按对象身份缓存会串号)。"""
    as_of = evidence_asof()
    if not as_of or not isinstance(snapshot, dict):
        return snapshot
    return gate_snapshot(snapshot, as_of, root=root)


def apply_to_series(out, mid, freq, meta=None, snapshot=None,
                    version_confirmed=False):
    """metric_series 出口截止: 规则①②对调用方自带序列恒适用(采集档通道
    /未截止快照同样受约束;已截止序列幂等——规则②③只在历史截止视图生效,
    与 gate_snapshot 同口径);规则③b 对采集档通道: 调用方选定 ≤as_of 采集档
    后 version_confirmed=True 放行,否则兜底剔除。out=(series|None, err)→同形。"""
    as_of = evidence_asof()
    if not as_of or not out or not out[0]:
        return out
    s = out[0]
    if not isinstance(s, dict) or not s.get('dates'):
        return out
    hist = (True if snapshot is None
            else is_historical_view(as_of, snapshot))
    revised = bool(meta is not None and is_revised(meta))
    if revised and not version_confirmed and hist and snapshot is None:
        # 无快照(版本日不可确认)且注册表声明最新修订口径→不可引用
        return (None, '数据版本不可得: 注册表声明最新修订口径'
                '(release_semantics=latest_vintage),数据版本日晚于研究'
                '截止 %s——%s 当时所见值不可知,不取最新修订值冒充'
                % (as_of, mid))
    gd, gv, info = gate_series(mid, freq, s.get('dates'), s.get('values'),
                               as_of, enforce_publication=hist,
                               revised=(revised and hist))
    if info['n_kept'] == info['n_in']:
        return out
    s2 = dict(s)
    s2['dates'], s2['values'] = gd, gv
    s2['evidence_gate'] = dict({k: info[k] for k in (
        'n_in', 'n_kept', 'n_late_observation', 'n_late_publication',
        'n_version_unavailable', 'first_dropped', 'last_eligible')},
        as_of=as_of)
    if not gd:
        return None, ('数据版本不可得/截止视图内无可引用观测(证据口径 '
                      '%s): %s' % (as_of, json.dumps(
                          info.get('first_dropped'), ensure_ascii=False)))
    return s2, out[1]
