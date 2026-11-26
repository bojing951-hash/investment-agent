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
# Audit-R33 任务1: 规则②对**每个** ≤as_of 观测逐点核发布日,官方发布日
# 优先(日历实录条目),RELEASE_RULES 推定仅兜底。原 62 天视界(观测日 ≤
# as_of−62 天直接放行,不查日历)在月频序列首日戳下(9 月=2025-09-01)把
# 停摆延误的 2025-09 失业率(官方首发 2025-11-20)/工业生产(2025-12-03)/
# 核心 PCE(2025-12-05)在研究时点 2025-11-15 直接放行(误收)——视界
# 按「推定时滞上限」设定,对逐事件延误(停摆/补发)不成立。逐点查询按
# (指标,频率,观测月|观测日) 记忆化(月/季频规则与日历条目只随观测月变;
# 日历身份变=换钉死副本/文件更新即失效)。
_PUBLISH_MEMO = {}
_PUBLISH_MEMO_TOKEN = [None]
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
    """规则②: 观测的发布日 ≤ as_of 才当时可得。返回 (ok, publish_iso|None,
    basis_text|None)。Audit-R33 任务1: 官方发布日优先,逐点核(无视界);
    推定规则只在该观测月/日无日历实录时兜底,basis 随行供披露。"""
    pub, basis = visible_publish(mid, freq, obs_iso)
    if pub and pub > as_of:
        return False, pub, basis
    return True, pub, basis


def _publish_memo_token():
    """日历身份(钉死副本或本地文件的路径+mtime)——变即清记忆。"""
    import release_calendar as rc
    try:
        _c = rc._cache
        return (os.environ.get('IA_CALENDAR_PIN') or '', _c.get('path'),
                _c.get('mtime'))
    except Exception:
        return None


def visible_publish(mid, freq, obs_iso):
    """发布日统一入口(日历实录优先/推定兜底;IA_CALENDAR_PIN 钉死在场时读
    冻结副本)。→ (publish_iso|None, basis_text)。Audit-R33 任务1: 逐点
    调用的记忆化(月/季频按观测月,其余按观测日;日历身份变即失效)。"""
    import release_calendar as rc
    import research_map_planner as rmp
    try:
        rc._load()                 # 先刷新日历缓存,再取身份(文件更新/换钉死副本即失效)
    except Exception:
        pass
    tok = _publish_memo_token()
    if _PUBLISH_MEMO_TOKEN[0] != tok:
        _PUBLISH_MEMO.clear()
        _PUBLISH_MEMO_TOKEN[0] = tok
    key = (mid, freq, obs_iso[:7] if freq in ('monthly', 'quarterly')
           and ISO_RE.match(str(obs_iso)[:10]) else obs_iso)
    hit = _PUBLISH_MEMO.get(key)
    if hit is None:
        hit = rmp._visible_publish(mid, freq, obs_iso)
        _PUBLISH_MEMO[key] = hit
    return hit


def version_available_on(mid, freq, obs_iso):
    """规则③b: 声明修订序列的观测「当时可得的版本」=首发后首个修订版
    发布日。→ (version_iso|None, first_publish|None, final_basis|None)。
    Audit-R33 任务1(快报与终值): 日历条目带终值日(final_publish_on)时,
    首发→终值之间当时只得见快报值,而库内值为终值/最新修订值——该窗口内
    版本当时不可得,可得日=终值日;无终值实录=首发日+一个发布周期
    (_REVISION_CYCLE_MONTHS: 月频 0/季频 +1 月,原口径不变)。"""
    import release_calendar as rc
    pub, _b = visible_publish(mid, freq, obs_iso)
    if not pub:
        return None, None, None
    _cal_obs = (obs_iso[:7] + '-01'
                if freq in ('monthly', 'quarterly') else obs_iso)
    try:
        fin = rc.final_publish(mid, _cal_obs)
    except Exception:
        fin = None
    if isinstance(fin, str) and len(fin) == 10 and fin >= pub:
        return fin, pub, 'calendar:final_publish_on'
    return _add_months(pub, _REVISION_CYCLE_MONTHS.get(freq, 0)), pub, None


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
                ok, pub, basis = _published_by(mid, freq, ds, as_of)
                if not ok:
                    n_late_pub += 1
                    _drop(ds, 'late_publication', pub,
                          {'publish_basis': basis})
                    continue
            if revised:
                ver, pub, vbasis = version_available_on(mid, freq, ds)
                if ver and ver > as_of:
                    n_version += 1
                    _drop(ds, 'data_version_unavailable', pub,
                          {'version_available_on': ver,
                           'version_basis': vbasis,
                           'stored_value': ('final_or_latest_revision'
                                            if vbasis else
                                            'latest_revision')})
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


def _rebuild_fact(fact, meta, dates, values, as_of, vintage_label,
                  version_mark=None):
    """晚于截止的快照事实→自截止序列重建(≤as_of 最新有效观测+同口径
    derived);序列无有效观测→None(该格截至 as_of 不可得)。
    Audit-R33 任务1: dates/values=所绑定的那份冻结版本(as-of 快照版本
    序列,或无 as-of 版本时的较晚版本序列);version_mark=版本绑定/缺口
    标记(随行入 evidence_gate,读者可核)。"""
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
              evidence_gate=dict({
                  'rebuilt_at_as_of': True,
                  'source_observation_date': fact.get('observation_date'),
                  'vintage': vintage_label,
                  'n_series_eligible': cst.get('n_observations', len(cd))},
                  **(version_mark or {})))
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


def _version_mark(status, snapshot):
    """事实/序列/派生值的版本绑定标记(随行入 evidence_gate)。"""
    return {'version_status': status,
            'value_source_snapshot_id': (snapshot or {}).get('snapshot_id'),
            'value_source_target_date': _iso_of_ymd(
                (snapshot or {}).get('target_date'))}


def collector_coverage(reg_by_id, root, as_of, bound):
    """Audit-R33 任务1(采集档通道版本绑定预扫): 不在快照序列面的在册
    序列指标,其历史序列取自数据树 data/daily/<前缀>*.json 采集档。历史
    截止下「当时可得的冻结版本」=采集日 ≤as_of 的最新采集档(采集日=该档
    版本日);数据树最早采集档晚于 as_of=缺历史版本(整段历史=截止后回填,
    序列面逐条标 historical_version_missing)。→ {指标: 版本面}。"""
    import workbench_data as wd
    daily = os.path.join(root or wd.ROOT, 'data', 'daily')
    ac = _compact(as_of)
    out, cache = {}, {}
    for mid, meta in reg_by_id.items():
        if mid in bound:
            continue
        prefix = wd.SERIES_SOURCE_PREFIX.get(
            meta.get('history_source') or meta.get('source'))
        if prefix is None:
            continue
        if prefix not in cache:
            cache[prefix] = sorted(
                y for y in (_file_ymd(p) for p in glob.glob(
                    os.path.join(daily, prefix + '*.json'))) if y)
        ys = cache[prefix]
        le = [y for y in ys if y <= ac]
        out[mid] = {
            'files': len(ys), 'files_first': ys[0] if ys else None,
            'version_file_ymd': le[-1] if le else None,
            'version_status': ('collector_file_le_asof' if le else
                               ('historical_version_missing' if ys
                                else 'no_collector_file'))}
    return out


def gate_snapshot(snap, as_of, root=None, registry=None):
    """快照截止视图(取数入口 latest_snapshot 消费)。snap 非 dict/无 as_of
    →原样返回。视图=深拷贝派生,源快照对象不改。

    Audit-R33 任务1(统一历史证据口径):
    - 规则②官方发布日优先,逐点核(无 62 天视界捷径);
    - 事实表/历史序列/派生值绑定**同一份**当时可得的冻结版本: 数据树有
      target_date≤as_of 的快照版本(as-of vintage)时,序列与事实只取该版本
      (as-of 快照有序列但缺事实行→自该版本序列重建,不取较晚版本的事实
      值;序列不在该版本内=截止后回填/后增序列,不可绑定→空壳剔除并点名;
      该版本日后、研究时点前已发布的观测不在所绑版本内→缺口点名);
    - 无 as-of 版本(缺历史版本)=明确标缺证: 逐事实 historical_version_
      missing 标记+顶层 gaps 条目(值取自较晚版本,不得表述为当时首发值);
      采集档通道同样预扫(最早采集档晚于 as_of=缺历史版本);
    - 快报与终值: 声明修订口径序列在首发→终值窗口内只有终值在手=
      版本当时不可得(version_available_on 取日历终值日)。"""
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
    per_series, excluded, not_in_vintage = {}, [], []
    published_after_vintage, prelim = {}, {}
    n_obs_dropped = n_version_dropped = 0
    _ser_keys = list(ss) + [m for m in vss if m not in ss]
    for mid in _ser_keys:
        ser = ss.get(mid) or {}
        meta = reg_by_id.get(mid) or {}
        freq = meta.get('frequency')
        if vintage and not (vss.get(mid) or {}).get('dates'):
            # 序列不在 as-of 冻结版本内(或该版本内无观测)=截止后回填/后增
            # 序列——不得绑定到当时版本,空壳+原因(如实缺席)
            not_in_vintage.append(mid)
            excluded.append(mid)
            ss[mid] = _excluded_shell(
                ser, as_of, 'not_in_as_of_vintage',
                ('数据树 as-of 快照版本 %s(target_date %s)内无此序列的'
                 '观测——较晚版本才出现的序列=截止后回填/后增,不得作为'
                 '研究时点 %s 当时可得的证据'
                 % ((vintage or {}).get('snapshot_id'),
                    _iso_of_ymd((vintage or {}).get('target_date')),
                    as_of)))
            per_series[mid] = {
                'n_in': len(ser.get('dates') or []), 'n_kept': 0,
                'n_late_observation': 0, 'n_late_publication': 0,
                'n_version_unavailable': 0, 'first_dropped': None,
                'last_eligible': None, 'vintage': 'not_in_as_of_vintage',
                'excluded': True}
            continue
        src = vss[mid] if (vintage and mid in vss) else ser
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
            ss[mid] = dict(src, dates=gd, values=gv)
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
        if src is not ser and ser.get('dates'):
            # 截止后回填/版本日后发布: 较晚快照序列内 ≤as_of 且官方发布日
            # ≤as_of(研究时点已发布)而所绑冻结版本内没有的观测——不取
            # 较晚版本补入,逐条点名(缺口 published_observation_not_in_
            # bound_version);同日不同值(后续修订)不在此列,值以所绑版本为准。
            _ld, _lv, _li = gate_series(
                mid, freq, ser.get('dates'), ser.get('values'), as_of,
                enforce_publication=True, revised=revised)
            _vset = set(gd)
            _late_only = [d for d in _ld if d not in _vset]
            if _late_only:
                published_after_vintage[mid] = {
                    'n': len(_late_only), 'first': _late_only[0],
                    'last': _late_only[-1],
                    'first_publish': (_published_by(
                        mid, freq, _late_only[0], as_of)[1] or {})}
                per_series[mid]['published_after_vintage'] = {
                    'n': len(_late_only), 'first': _late_only[0]}
        if (vintage and src is not ser and gd and is_revised(meta)):
            # 快报与终值: 所绑冻结版本内最新观测的终值日在 as_of 之后→
            # 该值=当时冻结的快报/初值(当时可得的就是它),随行标注;无冻结
            # 版本时同一观测按规则③判当时数据版本不可得(见上)。
            _ver, _fp, _fb = version_available_on(mid, freq, gd[-1])
            if _ver and _ver > as_of:
                prelim[mid] = {'value_version': 'flash_or_preliminary',
                               'final_publish_on': _ver,
                               'final_version_basis': _fb}
                per_series[mid].update(prelim[mid])
    ex_set = set(excluded)
    # 事实面(Audit-R33 任务1: 绑定同一份冻结版本)
    #  a. as-of 快照版本在场: 事实只取该版本——有事实行且合格→原值;
    #     无事实行/不合格而该版本序列有合格观测→自该版本序列重建;
    #     该版本既无事实行亦无序列→不可绑定(剔除并计数)。绝不取较晚
    #     版本的事实值冒充当时值。
    #  b. 无 as-of 版本: ≤as_of 且已发布且版本可得者保留(版本口径随行,
    #     并逐行标 historical_version_missing=缺历史版本);其余自截止序列
    #     重建(同标记);序列被剔除者=事实不可引用(剔除并计数)。
    facts, seen = [], set()
    n_fact_kept = n_fact_rebuilt = n_fact_dropped = n_fact_version = 0
    n_fact_vint_series = n_fact_not_in_vintage = 0
    src_fact_list = snap.get('facts') or []
    src_facts = {f.get('metric_id'): f for f in src_fact_list}
    _order = [f.get('metric_id') for f in src_fact_list] + [
        m for m in vfacts if m not in src_facts]
    _missing_mark = (_version_mark('historical_version_missing', snap)
                     if (historical and not vintage) else None)
    eligible_not_bound = []      # 已发布≤as_of 但不在所绑冻结版本内

    def _vmark(mid):
        return dict(_version_mark('as_of_vintage', vintage),
                    **(prelim.get(mid) or {}))
    for mid in _order:
        if mid in seen:
            continue
        f = src_facts.get(mid)
        vf = vfacts.get(mid) if vintage else None
        template = f or vf
        meta = reg_by_id.get(mid) or {}
        freq = meta.get('frequency')
        od = str((f or {}).get('observation_date') or '')[:10]
        if vintage:
            vser = ss.get(mid) or {}
            v_ok = (mid not in ex_set and vser.get('dates'))
            vf_od = str((vf or {}).get('observation_date') or '')[:10]
            # 较晚快照事实行: 观测 ≤as_of 且官方发布日 ≤as_of(研究时点已发布)
            _later_elig = (f is not None and ISO_RE.match(od) and od <= as_of
                           and bool(_published_by(mid, freq, od, as_of)[0]))
            _delivered_od = None
            if (vf is not None and vf_od <= as_of
                    and _published_by(mid, freq, vf_od, as_of)[0]):
                nf = copy.deepcopy(vf)
                nf['evidence_gate'] = dict(
                    {'vintage': 'as_of_vintage',
                     'source_snapshot_id': vintage.get('snapshot_id')},
                    **_vmark(mid))
                facts.append(nf)
                seen.add(mid)
                n_fact_kept += 1
                _delivered_od = vf_od
            elif v_ok:
                nf = _rebuild_fact(
                    template, meta, vser['dates'], vser['values'], as_of,
                    'as_of_vintage', _vmark(mid))
                if nf is not None:
                    facts.append(nf)
                    seen.add(mid)
                    n_fact_rebuilt += 1
                    if vf is None:
                        n_fact_vint_series += 1
                    _delivered_od = str(nf.get('observation_date') or '')[:10]
            else:
                n_fact_dropped += 1
                if vf is None:
                    n_fact_not_in_vintage += 1
            # 所绑版本未含较晚事实行(未交付,或交付的是更早观测)=缺口点名
            if _later_elig and (_delivered_od is None or _delivered_od < od):
                eligible_not_bound.append(mid)
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
                ver, _p, _b = version_available_on(mid, freq, obs_iso)
                if ver and ver > as_of:
                    return False
            return True
        ps = per_series.get(mid) or {}
        if mid in ex_set:
            n_fact_version += 1
            continue
        if _elig(od, ps.get('vintage') == 'latest_revision_only'):
            nf = copy.deepcopy(f)
            nf['evidence_gate'] = dict(
                {'vintage': ps.get('vintage', 'snapshot_vintage')},
                **(_missing_mark or {}))
            facts.append(nf)
            seen.add(mid)
            n_fact_kept += 1
            continue
        if mid in ss and ss[mid].get('dates'):
            nf = _rebuild_fact(
                f, meta, ss[mid]['dates'], ss[mid]['values'], as_of,
                ps.get('vintage', 'snapshot_vintage'), _missing_mark)
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
    gaps = []
    if historical and not vintage:
        gaps.append({
            'gap': 'historical_version_missing',
            'as_of': as_of,
            'detail': ('数据树内无 target_date≤%s 的冻结快照(缺历史版本)'
                       '——本视图的事实/历史序列/派生值均取自较晚版本 %s'
                       '(版本日 %s),可能含后续修订与截止后回填,不得表述为'
                       '当时首发值或当时冻结版;引用须随行标注'
                       % (as_of, snap.get('snapshot_id'), src_td)),
            'affects': 'facts / series / derived',
            'n_facts': len(facts),
            'n_series_with_data': sum(
                1 for i in per_series.values() if (i.get('n_kept') or 0) > 0),
            'fact_mark': 'historical_version_missing'})
    cov = (collector_coverage(reg_by_id, root, as_of, set(per_series))
           if historical else {})
    _cov_missing = sorted(m for m, i in cov.items()
                          if i['version_status'] == 'historical_version_missing')
    if _cov_missing:
        gaps.append({
            'gap': 'collector_files_after_as_of',
            'as_of': as_of,
            'detail': ('下列在册序列不在快照序列面,历史序列取自采集档;'
                       '数据树最早采集档晚于研究时点(缺 ≤%s 的冻结版本,'
                       '整段历史=截止后回填)——序列逐条标 '
                       'historical_version_missing,不得表述为当时冻结版'
                       % as_of),
            'affects': 'series', 'series': _cov_missing,
            'earliest_file': min(
                (i['files_first'] for i in cov.values()
                 if i['files_first']), default=None)})
    if vintage:
        vtd = _iso_of_ymd(vintage.get('target_date'))
        if eligible_not_bound:
            gaps.append({
                'gap': 'published_fact_not_in_bound_version',
                'as_of': as_of,
                'detail': ('下列指标在较晚快照内的事实观测 ≤研究时点且'
                           '官方发布日 ≤研究时点(当时已发布),但不在所绑'
                           '冻结版本 %s(版本日 %s)内——未纳入证据面'
                           '版本日 %s 至研究时点 %s 之间发布的数据不在该'
                           '版本内,如实缺口'
                           % (vintage.get('snapshot_id'), vtd, vtd, as_of)),
                'affects': 'facts / series', 'series': sorted(
                    eligible_not_bound)})
    if published_after_vintage:
        _ex = sorted((m, v['first']) for m, v in published_after_vintage.items())
        # 示例清单: 低频(月/季等官方发布)序列优先——发布日类缺口优先点名,
        # 日频市场序列排后(全量见 series 清单)
        _ex_x = sorted(_ex, key=lambda x: (
            (reg_by_id.get(x[0]) or {}).get('frequency') == 'daily',
            str(published_after_vintage[x[0]].get('first_publish') or ''), x[0]))
        gaps.append({
            'gap': 'published_observation_not_in_bound_version',
            'as_of': as_of,
            'detail': ('较晚快照序列内有观测日 ≤研究时点且官方发布日 ≤研究'
                       '时点(当时已发布)的观测,但不在所绑冻结版本 %s(版本日 '
                       '%s)内——版本日至研究时点 %s 之间发布的数据未入该'
                       '版本,证据面未纳入(不取较晚版本补入),如实缺口;需要'
                       '这些观测须换用版本日更晚且 ≤研究时点的冻结版本'
                       % (vintage.get('snapshot_id'), vtd, as_of)),
            'affects': 'series', 'series': [m for m, _d in _ex],
            'n_series': len(_ex),
            'n_observations': sum(v['n'] for v in
                                  published_after_vintage.values()),
            'examples': [{'metric_id': m, 'observation_date': d,
                          'first_publish': published_after_vintage[m].get(
                              'first_publish')}
                         for m, d in _ex_x[:12]]})
    if not_in_vintage:
        gaps.append({
            'gap': 'series_not_in_as_of_vintage',
            'as_of': as_of,
            'detail': ('序列不在 as-of 冻结版本 %s 内(截止后回填/后增),'
                       '已自证据面剔除,不得作为当时可得的证据'
                       % (vintage or {}).get('snapshot_id')),
            'affects': 'series / facts', 'series': sorted(not_in_vintage)})
    out['evidence_gate'] = {
        'discipline': 'r32',
        'as_of': as_of,
        'source_snapshot_id': snap.get('snapshot_id'),
        'source_target_date': src_td,
        'historical_view': historical,
        'publication_basis': ('calendar_first_publish|release_rules'
                              if historical else 'snapshot_presence'),
        'rules': ['①观测日≤as_of',
                  '②发布日≤as_of(历史截止: 官方发布日优先=日历实录逐点核,'
                  'RELEASE_RULES 推定兜底)',
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
            'excluded_series': sorted(excluded),
            'not_in_vintage_series': sorted(not_in_vintage),
            'preliminary_value_series': sorted(prelim)},
        'gaps': gaps,
        'counts': {
            'facts_kept': n_fact_kept, 'facts_rebuilt': n_fact_rebuilt,
            'facts_dropped': n_fact_dropped,
            'facts_excluded_version': n_fact_version,
            'facts_rebuilt_from_vintage_series': n_fact_vint_series,
            'facts_not_in_vintage': n_fact_not_in_vintage,
            'series_observations_dropped': n_obs_dropped,
            'series_observations_version_unavailable': n_version_dropped,
            'series_excluded': len(excluded),
            'series_not_in_vintage': len(not_in_vintage),
            'series_n': len(per_series)},
        'series': per_series,
        'collector_channel': cov,
        'note': ('截止视图(历史截止): 晚观测/晚发布不入证据面(官方发布日'
                 '优先);注册表声明最新修订口径的序列只引用已过首个修订周期'
                 '的观测(值=最新修订版,不得表述为当时首发值),未过者=当时'
                 '数据版本不可得'
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
    # Audit-R33 任务1: 调用方已带的版本绑定标记(采集档通道 version_status/
    # value_source_file)随行保留——逐观测剔除统计不覆盖版本标记
    s2['evidence_gate'] = dict(s.get('evidence_gate') or {},
                               **{k: info[k] for k in (
                                   'n_in', 'n_kept', 'n_late_observation',
                                   'n_late_publication',
                                   'n_version_unavailable', 'first_dropped',
                                   'last_eligible')}, as_of=as_of)
    if not gd:
        return None, ('数据版本不可得/截止视图内无可引用观测(证据口径 '
                      '%s): %s' % (as_of, json.dumps(
                          info.get('first_dropped'), ensure_ascii=False)))
    return s2, out[1]
