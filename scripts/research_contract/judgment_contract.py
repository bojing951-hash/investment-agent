#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""judgment_contract — Agent Native 判定档验证契约(架构整改阶段四)。

依据: 章程§六 6.1-6.3 + PHASE4-JUDGMENT-CONTRACT-DESIGN v1.0 + PHASE2 v1.2。
对象: research run 的 judgment.json(L3 矛盾/L4 情景)对**其自身 report 证据面**
(S3 概览指标+S4 序列+L2 观点库+evidence_index)的一致性——自包含,不引外部快照。

三类内容(6.1):
  客观事实  L3 statement/basis 数值断言 → tc.check_text(与周报同一引擎)
  统计结论  百分位/样本数/月内极值/年内区间/无倒挂/前值趋平 → 独立复算(公式钉死)
  经济解释  competing_explanations/L4 情景 → 六查(§2.2,规则+证据读取,零模型)

裁决: 客观事实 CONTRADICTED → 判断档整体降级(DOWNGRADED,渲染面披露);
任一项不可核(NOT_VERIFIED)如实输出,禁强行成结论。
输出 claim 对象(metric_id/claim_type/unit/value/evidence_refs/status)与
周报 render_hook 同构(§3 统一契约)。

纯度: 仅 stdlib + research_contract(tc/cf);零模型/零环境/零网络/零随机。
"""
import bisect
import datetime
import re

from research_contract import claim_factory as cf
from research_contract import text_consistency as tc

JUDGMENT_CONTRACT_VERSION = 'jc-v1.0-phase4'

# ── 证据面构建 ─────────────────────────────────────────────────────

def build_face(report):
    """report(S3 概览+S4 序列+L2 观点+evidence_index)→ tc 兼容自包含面。"""
    facts = []
    # S3 概览按步名定位(真实步名 S3_overview_<economy>,多经济体可重复);
    # 禁位置索引——薄报告(steps 缺位)须得空面而非崩溃(契约全域可判定)。
    eco_steps = [st for st in report.get('steps') or []
                 if str(st.get('step') or '').startswith('S3_overview')]
    eco_items = []
    for st in eco_steps:
        data = ((st.get('envelope') or {}).get('data') or {})
        eco = data.get('economies')
        if isinstance(eco, dict):
            eco_items.extend(eco.values())
        elif isinstance(eco, list):
            eco_items.extend(eco)
    for e in eco_items:
        for m in e.get('metrics', []):
            if m.get('presence') != 'present' or m.get('value') is None:
                continue
            derived = {}
            for c in m.get('changes') or []:
                key = 'pp_change' if c.get('change_unit') == 'pp' \
                    else 'pct_change'
                derived.setdefault(c['window'], {})[key] = c['value']
                derived[c['window']]['basis_date'] = c.get('basis_date')
                derived[c['window']]['basis_value'] = c.get('basis_value')
            f = dict(m)
            f['fact_id'] = f"{m['metric_id']}@{m.get('observation_date')}"
            if derived:
                f['derived'] = derived
            facts.append(f)
    # L1 事实行(问题目标指标)一并入面——S3 概览为选录面,目标指标可能
    # 不在其列(C-real 实证: DXY);与 S3 重复时保留 S3 富结构(含 changes)。
    l1_rows = (((report.get('layers') or {}).get('L1_事实层') or {})
               .get('rows')) or []
    s3_ids = {f['fact_id'] for f in facts}
    for r in l1_rows:
        if r.get('value') is None or not r.get('metric_id'):
            continue
        fid = f"{r['metric_id']}@{r.get('observation_date')}"
        if fid in s3_ids:
            continue
        f = dict(r)
        f['fact_id'] = fid
        facts.append(f)
    # Audit-R33 任务3: 原问直答分面行入面——官方目标水平事实(日历
    # 实录口径)+通胀去年同月基期事实(追加在最新读数之后: 按指标取
    # 事实仍先得最新读数)。旧档无分面块=零新增行。
    _pq = ((report.get('research_plan') or {}).get('policy_question')
           or {})
    if isinstance(_pq, dict) and _pq.get('schema') == 'r33-policy-question':
        _s3_ids2 = {f['fact_id'] for f in facts}
        for _r in ((_pq.get('policy_targets') or {}).get('rows') or []):
            _mid = _r.get('official_metric_id')
            if (_r.get('status') == 'official_record'
                    and _r.get('target') is not None and _mid
                    and _r.get('effective_date')):
                _fid = f"{_mid}@{_r.get('effective_date')}"
                if _fid not in _s3_ids2:
                    facts.append({
                        'metric_id': _mid, 'value': _r.get('target'),
                        'observation_date': _r.get('effective_date'),
                        'fact_id': _fid, 'unit': 'percent',
                        'source': 'policy_question',
                        'policy_decision_date': _r.get('decision_date')})
                    _s3_ids2.add(_fid)
        for _r in ((_pq.get('inflation_yoy') or {}).get('rows') or []):
            _b = _r.get('base') or {}
            if (_b.get('value') is not None
                    and _b.get('observation_date') and _r.get('metric_id')):
                _fid = f"{_r.get('metric_id')}@{_b.get('observation_date')}"
                if _fid not in _s3_ids2:
                    facts.append({
                        'metric_id': _r.get('metric_id'),
                        'value': _b.get('value'),
                        'observation_date': _b.get('observation_date'),
                        'fact_id': _fid, 'unit': 'percent',
                        'source': 'policy_question',
                        'role': 'same_month_last_year_base'})
                    _s3_ids2.add(_fid)
    series = {}
    for st in report.get('steps') or []:
        nm = st.get('step') or ''
        data = (st.get('envelope') or {}).get('data') or {}
        if nm.startswith('S4_history_') and data.get('series'):
            series[nm.replace('S4_history_', '')] = data['series']
    ts = (report.get('run') or {}).get('ts_utc') or '19700101T000000Z'
    as_of = f'{ts[:4]}-{ts[4:6]}-{ts[6:8]}'
    views = ((report.get('layers') or {}).get('L2_机构观点层')
             or {}).get('views') or {}
    return {
        'snapshot_id': 'judgment_face_' + ts,
        'research_as_of': as_of,
        'facts': facts,
        'series_store': series,
        'views': views.get('rows') if isinstance(views, dict) else views,
        'evidence_index': report.get('evidence_index') or [],
    }


# ── 类B: 统计结论独立复算(公式钉死) ────────────────────────────────

def _year_points(face, mid):
    ss = (face.get('series_store') or {}).get(mid) or {}
    if not ss.get('dates'):
        return None, None
    year = str(face.get('research_as_of'))[:4]
    pts = [(d, v) for d, v in zip(ss['dates'], ss['values'])
           if str(d).startswith(year)]
    return pts, year


def _pinned_percentile(pts, cur):
    """钉死口径: pct = 100 × count(v < cur) / n(严格小于/当年样本数)。"""
    n = len(pts)
    if n == 0:
        return None
    return 100.0 * sum(1 for _, v in pts if v < cur) / n


_INST_CITE_RE = re.compile(
    r'VIEW-|VP-VIEW|UBS|MSIM|PIMCO|Vanguard|BIS|Goldman|GS\b|Fed\b|ECB|BOJ|'
    r'美联储|机构|预计|记述|记叙|观点|判断|归因|futures?\s+implied', re.I)


def _nearest_mid(clause, pos, carry=None):
    """子句内统计结论归指标: 前向别名优先(断言随其主语),无前向才取全域
    最近;子句无别名时回落承前指标(分号切句后主语在上句,如
    「…第95.6百分位;自8月低点2.60pp走阔+0.74pp」)。"""
    hits = tc._find_alias(clause)
    best_p, bd_p = None, 1 << 30
    for mid, s, e in hits:
        if e <= pos and pos - e < bd_p:
            best_p, bd_p = mid, pos - e
    if best_p is not None:
        return best_p
    if hits:
        best, bd = None, 1 << 30
        for mid, s, e in hits:
            d = min(abs(pos - s), abs(pos - e))
            if d < bd:
                best, bd = mid, d
        return best
    return carry


def _class_b(text, face):
    """统计结论抽取+复算。返回 (checks, consumed_raws)。"""
    checks, consumed = [], set()
    carry = None                    # 承前指标(分号切句后主语在上句)
    facts = {f['metric_id']: f for f in face.get('facts', [])}

    def cur_of(mid):
        f = facts.get(mid)
        return (f or {}).get('value')

    for clause in tc._clause_split(text):
        pts_cache = {}

        def pts_of(mid):
            if mid not in pts_cache:
                pts_cache[mid] = _year_points(face, mid)[0]
            return pts_cache[mid]

        # B1 样本数 + B2 百分位(公式钉死: 严格小于/n)
        for m in re.finditer(r'(\d+)\s*个观测', clause):
            mid = _nearest_mid(clause, m.start(), carry)
            pts = pts_of(mid) if mid else None
            if not pts:
                continue
            n_claim = int(m.group(1))
            checks.append({
                'family': 'stat_sample_n', 'claim_type': 'statistic',
                'metric_id': mid, 'unit': 'count', 'value': n_claim,
                'expected': len(pts), 'evidence_refs': [mid],
                'status': 'VERIFIED' if abs(n_claim - len(pts)) <= 1
                else 'CONTRADICTED',
                'token': m.group(0),
                'note': f'当年序列 n={len(pts)}'})
            consumed.add(m.group(1))
        for m in re.finditer(r'第\s*([\d.]+)\s*百分位', clause):
            mid = _nearest_mid(clause, m.start(), carry)
            cur, pts = (cur_of(mid) if mid else None), \
                (pts_of(mid) if mid else None)
            if pts is None or cur is None:
                continue
            pct = _pinned_percentile(pts, cur)
            if pct is None:
                continue
            v = float(m.group(1))
            checks.append({
                'family': 'stat_percentile', 'claim_type': 'statistic',
                'metric_id': mid, 'unit': 'percentile', 'value': v,
                'expected': round(pct, 1), 'evidence_refs': [mid],
                'status': 'VERIFIED' if abs(v - pct) <= 0.15
                else 'CONTRADICTED',
                'token': m.group(0),
                'note': f'钉死口径 100×count(v<cur)/n={pct:.1f}'})
            consumed.add(m.group(1))
        # B3/B4 月内极值
        for m in re.finditer(r'(\d{1,2})\s*月(?:份)?(?:内)?(低|高)点'
                             r'(?:\s*(?:为|:|：|@)?\s*([\d.]+))?'
                             r'(?:@(\d{2}-\d{2}))?', clause):
            mid = _nearest_mid(clause, m.start(), carry)
            pts = pts_of(mid) if mid else None
            if not pts or m.group(3) is None:
                continue
            mm, side, v_claim = int(m.group(1)), m.group(2), \
                float(m.group(3))
            sub = [(d, v) for d, v in pts if d[5:7] == f'{mm:02d}']
            if not sub:
                continue
            exp = (min if side == '低' else max)(v for _, v in sub)
            d_exp = (min if side == '低' else max)(sub, key=lambda t: t[1])[0]
            checks.append({
                'family': f'stat_month_{side}', 'claim_type': 'statistic',
                'metric_id': mid, 'unit': 'value', 'value': v_claim,
                'expected': exp, 'evidence_refs': [mid],
                'status': 'VERIFIED' if abs(v_claim - exp) <= 0.005 + 1e-9
                else 'CONTRADICTED', 'token': m.group(0),
                'note': f'{mm}月{side}点 {exp}@{d_exp}'})
            consumed.add(m.group(3))
        # B5 年内区间
        for m in re.finditer(r'年内区间\s*([\d.]+)\s*[–—-]\s*([\d.]+)',
                             clause):
            mid = _nearest_mid(clause, m.start(), carry)
            pts = pts_of(mid) if mid else None
            if not pts:
                continue
            lo, hi = float(m.group(1)), float(m.group(2))
            e_lo = min(v for _, v in pts)
            e_hi = max(v for _, v in pts)
            ok = abs(lo - e_lo) <= 0.005 + 1e-9 and \
                abs(hi - e_hi) <= 0.005 + 1e-9
            checks.append({
                'family': 'stat_year_range', 'claim_type': 'statistic',
                'metric_id': mid, 'unit': 'value',
                'value': [lo, hi], 'expected': [e_lo, e_hi],
                'evidence_refs': [mid],
                'status': 'VERIFIED' if ok else 'CONTRADICTED',
                'token': m.group(0), 'note': f'当年 [{e_lo},{e_hi}]'})
            consumed.update({m.group(1), m.group(2)})
        # B6 无倒挂/无负值(date 后)
        for m in re.finditer(r'(\d{4}-\d{2}-\d{2})\s*后无(?:倒挂|负值)',
                             clause):
            mid = _nearest_mid(clause, m.start(), carry) or 'CURVE_2S10S'
            ss = (face.get('series_store') or {}).get(mid) or {}
            if not ss.get('dates'):
                continue
            d0 = m.group(1)
            neg_after = [(d, v) for d, v in zip(ss['dates'], ss['values'])
                         if d > d0 and v < 0]
            at = [v for d, v in zip(ss['dates'], ss['values']) if d == d0]
            ok = not neg_after
            checks.append({
                'family': 'stat_no_inversion', 'claim_type': 'statistic',
                'metric_id': mid, 'unit': 'bool', 'value': True,
                'expected': not neg_after, 'evidence_refs': [mid],
                'status': 'VERIFIED' if ok else 'CONTRADICTED',
                'token': m.group(0),
                'note': f'{d0}(当日值{at})后负值数={len(neg_after)}'})
        # B7 前值趋平(自 X 单日趋平)
        for m in re.finditer(r'自\s*([\d.]+)\s*(?:pp|点|%)?[\s个单日]*趋平',
                             clause):
            mid = _nearest_mid(clause, m.start(), carry)
            ss = (face.get('series_store') or {}).get(mid) or {}
            if not ss.get('dates'):
                continue
            prev = list(zip(ss['dates'], ss['values']))[-2]
            v = float(m.group(1))
            checks.append({
                'family': 'stat_prev_obs', 'claim_type': 'statistic',
                'metric_id': mid, 'unit': 'value', 'value': v,
                'expected': prev[1], 'evidence_refs': [mid],
                'status': 'VERIFIED' if abs(v - prev[1]) <= 0.005 + 1e-9
                else 'CONTRADICTED', 'token': m.group(0),
                'note': f'前一观测 {prev[1]}@{prev[0]}'})
            consumed.add(m.group(1))
        # B8 年内高/低位带
        for m in re.finditer(r'处\s*年内(高|低)位(?:区)?', clause):
            mid = _nearest_mid(clause, m.start(), carry)
            cur, pts = (cur_of(mid) if mid else None), \
                (pts_of(mid) if mid else None)
            if pts is None or cur is None or len(pts) == 0:
                continue
            pct = _pinned_percentile(pts, cur)
            want_hi = m.group(1) == '高'
            ok = (pct >= 75.0) if want_hi else (pct <= 25.0)
            checks.append({
                'family': 'stat_band_claim', 'claim_type': 'statistic',
                'metric_id': mid, 'unit': 'percentile',
                'value': 75.0 if want_hi else 25.0,
                'expected': round(pct, 1), 'evidence_refs': [mid],
                'status': 'VERIFIED' if ok else 'CONTRADICTED',
                'token': m.group(0),
                'note': f'{m.group(1)}位带 vs 百分位 {pct:.1f}'
                        f'(阈值 75/25)'})
        # B9 年内最平/最陡端(下/上三分位)
        for m in re.finditer(r'年内最(平|陡)端', clause):
            mid = _nearest_mid(clause, m.start(), carry)
            cur, pts = (cur_of(mid) if mid else None), \
                (pts_of(mid) if mid else None)
            if pts is None or cur is None or not pts:
                continue
            lo = min(v for _, v in pts)
            hi = max(v for _, v in pts)
            if hi - lo < 1e-9:
                continue
            frac = (cur - lo) / (hi - lo)
            ok = frac <= 1.0 / 3 if m.group(1) == '平' else frac >= 2.0 / 3
            checks.append({
                'family': 'stat_extreme_end', 'claim_type': 'statistic',
                'metric_id': mid, 'unit': 'fraction', 'value': frac,
                'expected': ('≤1/3' if m.group(1) == '平' else '≥2/3'),
                'evidence_refs': [mid],
                'status': 'VERIFIED' if ok else 'CONTRADICTED',
                'token': m.group(0),
                'note': f'年内位置 frac={frac:.2f} '
                        f'[{lo},{hi}]'})
        # B10 自低点走阔幅度(自 X 走阔 +Y)
        for m in re.finditer(r'自\s*(\d{1,2})\s*月低点\s*([\d.]+)pp?'
                             r'\s*走阔\s*\+?([\d.]+)pp', clause):
            mid = _nearest_mid(clause, m.start(), carry)
            cur, pts = (cur_of(mid) if mid else None), \
                (pts_of(mid) if mid else None)
            if pts is None or cur is None:
                continue
            mm = int(m.group(1))
            sub = [v for d, v in pts if d[5:7] == f'{mm:02d}']
            if not sub:
                continue
            lo_claim, wid_claim = float(m.group(2)), float(m.group(3))
            ok = abs((cur - min(sub)) - wid_claim) <= 0.005 + 1e-9 and \
                abs(min(sub) - lo_claim) <= 0.005 + 1e-9
            checks.append({
                'family': 'stat_widening_from_low', 'claim_type': 'statistic',
                'metric_id': mid, 'unit': 'pp', 'value': wid_claim,
                'expected': round(cur - min(sub), 4),
                'evidence_refs': [mid],
                'status': 'VERIFIED' if ok else 'CONTRADICTED',
                'token': m.group(0),
                'note': f'现值{cur}−{mm}月低点{min(sub)}'
                        f'={cur - min(sub):+.2f}'})
            consumed.update({m.group(2), m.group(3)})
        mids_here = tc._find_alias(clause)
        if mids_here:
            carry = mids_here[-1][0]
    return checks, consumed


# ── 类C: 六查(规则+证据读取,零模型) ────────────────────────────────

# 实据类证据行(Audit-R33 任务3: 原问直答面的 policy_record/
# plan_series_point 两类与 snapshot_fact 同等对待;旧档无此两类=零变化)
_FACT_REF_KINDS = ('snapshot_fact', 'policy_record', 'plan_series_point')


def _six_checks(judgment, face):
    out = []
    # 可观测集=面内事实∪序列∪索引实据(报告自身证据声明亦算可观测;
    # 真实面 evidence_index 实据 ⊆ S3 事实,行为不变——宽集只补薄报告)。
    observable = ({f['metric_id'] for f in face.get('facts', [])}
                  | set((face.get('series_store') or {}).keys())
                  | {(e.get('metric_id') or '')
                     for e in face.get('evidence_index') or []
                     if e.get('kind') in _FACT_REF_KINDS})
    observable.discard('')
    facts = observable
    index = {e.get('ref'): e for e in face.get('evidence_index') or []}
    views = {v.get('view_id'): v for v in (face.get('views') or [])}
    l3 = ((judgment.get('l3') or {}).get('contradictions')) or []
    l4 = ((judgment.get('l4') or {}).get('scenarios')) or []
    decl = (judgment.get('agent_declaration') or {}).get('attribution')

    def add(item_id, check, status, note):
        out.append({'item': item_id, 'check': check, 'status': status,
                    'note': note})

    for con in l3:
        cid = con.get('id')
        stmt = con.get('statement') or ''
        refs = con.get('evidence_refs') or []
        # 1 relevant: 引用可解析+至少一实据(或纯逻辑推理档显式披露)
        unresolved = [r for r in refs if r not in index]
        snap_refs = [r for r in refs
                     if (index.get(r) or {}).get('kind') in _FACT_REF_KINDS]
        if unresolved:
            add(cid, 'relevant', 'NOT_VERIFIED',
                f'引用不在 evidence_index: {unresolved[:3]}')
        elif not snap_refs and decl != 'logic_only':
            add(cid, 'relevant', 'NOT_VERIFIED',
                '零 snapshot_fact 引用且未声明纯逻辑推理档')
        else:
            add(cid, 'relevant', 'VERIFIED',
                f'{len(snap_refs)} 实据引用' if snap_refs else '纯逻辑档披露')
        # 2 supports: 实据=面内指标;观点=库内+标签归因式引用;
        # 被引而未展开=披露(非否决——supports 只裁它能裁的: 内容对得上否)
        bad, disclosed = [], []
        for r in refs:
            e = index.get(r) or {}
            if e.get('kind') == 'snapshot_fact':
                mid = e.get('metric_id')
                if mid not in facts:
                    bad.append(f'{r}:指标不在证据面')
                elif mid not in stmt and mid not in (con.get('basis') or ''):
                    disclosed.append(f'{r} 未在文本展开')
            elif e.get('kind') in ('policy_record', 'plan_series_point'):
                # Audit-R33 任务3: 原问直答面的引擎证据行(日历实录/计划
                # 序列点)自身即实据面——可解析即算;被引未展开=披露
                mid = e.get('metric_id')
                if mid and mid not in stmt and mid not in \
                        (con.get('basis') or ''):
                    disclosed.append(f'{r} 未在文本展开')
            elif e.get('kind') == 'vp_sidecar':
                vid = (e.get('ref') or '').replace('VP-', '')
                v = views.get(vid) or views.get(e.get('ref'))
                if v is None:
                    bad.append(f'{r}:观点不在 L2 库')
                elif v.get('view_label') == 'INSUFFICIENT_EVIDENCE' and \
                        not _INST_CITE_RE.search(stmt):
                    bad.append(f'{r}:标签 INSUFFICIENT 且非归因式引用')
        add(cid, 'supports', 'NOT_VERIFIED' if bad else 'VERIFIED',
            ('; '.join(bad) if bad else '引用逐项对得上')
            + (f'; 披露: {"; ".join(disclosed)}' if disclosed else ''))
        # 3 competing
        n_ce = len(con.get('competing_explanations') or [])
        add(cid, 'competing',
            'VERIFIED' if n_ce >= 2 else 'NOT_VERIFIED',
            f'{n_ce} 并列解释(阈值≥2)')
        # 4 opposing: 被引而未讨论的显著波动=披露;现时式方向断言与面相左=降级
        mentioned = stmt + (con.get('basis') or '')
        cited_unmentioned = []
        for r in snap_refs:
            mid = (index.get(r) or {}).get('metric_id')
            if mid and mid not in mentioned:
                cited_unmentioned.append(mid)
        opposes = []
        for ce in (con.get('competing_explanations') or []):
            if re.search(r'若|情景|假设|将|转入|不再', ce):
                continue          # 条件/未来式不做现时方向核
            for mid, s, e in tc._find_alias(ce):
                f = next((x for x in face['facts']
                          if x['metric_id'] == mid), None)
                wk = ((f or {}).get('derived') or {}).get('week') or {}
                chg = wk.get('pp_change', wk.get('pct_change'))
                if chg is None:
                    continue
                neg = re.search(r'走阔|上涨|回升|上升|涨', ce)
                pos = re.search(r'收窄|下跌|回落|下降|跌', ce)
                if (neg and chg < -0.05) or (pos and chg > 0.05):
                    opposes.append(f'{mid} {chg:+g} vs 解释方向')
        note = ''
        if cited_unmentioned:
            note += f'未讨论的被引指标(披露): {cited_unmentioned}'
        if opposes:
            add(cid, 'opposing', 'NOT_VERIFIED',
                (note + '; ' if note else '') + '现时方向相左: '
                + '; '.join(opposes))
        else:
            add(cid, 'opposing', 'VERIFIED',
                note or '无未消化的相反证据')
    # 5/6 overreach + falsifiable(L4)
    for sc in l4:
        sid = sc.get('id')
        rows = sc.get('rows') or sc
        text = ' '.join(str(v) for v in rows.values() if isinstance(v, str))
        tier = ((rows.get('asset_direction') or {}).get('confidence_tier')
                if isinstance(rows.get('asset_direction'), dict) else None)
        conditional = bool(re.search(r'假设|情景|若|条件', text))
        absolute = bool(re.search(r'必将|必然将|一定会|确定将', text))
        if tier == '纯逻辑推理' and absolute:
            add(sid, 'overreach', 'NOT_VERIFIED',
                '纯逻辑推理档含必然性措辞')
        elif tier == '纯逻辑推理' and not conditional:
            add(sid, 'overreach', 'NOT_VERIFIED',
                '纯逻辑推理档缺条件式框架(假设/情景/若)')
        else:
            add(sid, 'overreach', 'VERIFIED',
                f'tier={tier} 条件式{"✓" if conditional else "—"}')
        fals = rows.get('falsification') or rows.get('failure_conditions')
        trig = rows.get('trigger') or {}
        mids_f = fals.get('metric_id') if isinstance(fals, dict) else None
        thr = str(fals.get('threshold') if isinstance(fals, dict) else fals
                  or '')
        if not fals:
            add(sid, 'falsifiable', 'NOT_VERIFIED', '证伪条件为空')
        elif mids_f and mids_f not in facts:
            add(sid, 'falsifiable', 'NOT_VERIFIED',
                f'证伪指标 {mids_f} 不可观测(不在证据面)')
        elif not re.search(r'\d', thr):
            add(sid, 'falsifiable', 'NOT_VERIFIED', '阈值无数字形态')
        else:
            # 阈值算术一致性(自 X pp 升破 Y pp 且 >Zbp → Y−X==Z/100)
            m = re.search(r'>\s*(\d+)\s*bp.*?自\s*([\d.]+)pp\s*(?:升破|'
                          r'跌破)\s*([\d.]+)pp', thr)
            note = '指标+阈值形态✓'
            if m:
                d = float(m.group(3)) - float(m.group(2))
                if abs(d - int(m.group(1)) / 100.0) > 0.011:
                    add(sid, 'falsifiable', 'NOT_VERIFIED',
                        f'阈值算术断裂: {m.group(3)}−{m.group(2)}'
                        f'={d:.2f}≠{int(m.group(1))}bp')
                    continue
                note += f' 算术{d:.2f}={int(m.group(1))}bp✓'
            if trig and not trig.get('deadline'):
                note += '; trigger 缺 deadline(披露)'
            add(sid, 'falsifiable', 'VERIFIED', note)
    return out


# ── 主入口 ─────────────────────────────────────────────────────────

def _asset_window_basis(report):
    """报告资产月窗行(地图 research_plan.asset_moves 与普通问句顶层
    asset_moves 同构;R21 任务4)。窗口两端实测日=回贴披露面。"""
    rows = {}
    for src in (((report or {}).get('research_plan') or {}).get('asset_moves'),
                (report or {}).get('asset_moves')):
        for r in (src or {}).get('rows') or []:
            if r.get('metric_id'):
                rows[r['metric_id']] = r
    return rows


def _asset_window_recheck(checks, text, rows):
    """Audit-R21 任务4: 变化断言的另一合法基=资产月窗(滚动 N 月最近邻,
    与周/MTD 派生窗并行,二者口径不同不得互证错杀)。

    采信条件(全部满足才改判 VERIFIED): 检查为 CONTRADICTED、指标有
    资产月窗行、声明值与行内 chg_pct/chg_abs 逐位吻合(±0.06)、且
    **该行窗口两端实测日同现于本字段正文**——数字无窗口=不可核
    (R19 纪律),耦合披露是回贴的一部分。其余一律原样保留。"""
    if not rows:
        return checks
    fixed = []
    for ch in checks:
        if (ch.get('status') == 'CONTRADICTED' and ch.get('metric') in rows
                and isinstance(ch.get('value'), (int, float))):
            row = rows[ch['metric']]
            w = row.get('window') or {}
            # 声明带符号: token 原文首字符为负号而数值已归正时,
            # 方向说反(−38.07% vs 面 +38.07)不得借 abs 通道蒙混。
            _tok = str(ch.get('token') or '').strip()
            _eff = float(ch['value'])
            if _tok[:1] in ('−', '-') and _eff > 0:
                _eff = -_eff
            matched = None
            for ref, lbl in ((row.get('chg_pct'), 'chg_pct'),
                             (row.get('chg_abs'), 'chg_abs')):
                if (isinstance(ref, (int, float))
                        and abs(_eff - float(ref)) <= 0.06
                        and str(w.get('from')) in text
                        and str(w.get('to')) in text):
                    matched = (ref, lbl)
                    break
            if matched:
                ref, lbl = matched
                fixed.append(dict(
                    ch, status='VERIFIED',
                    note=(f'资产月窗基复算: {lbl}={ref}(窗口 '
                          f'{w.get("from")}→{w.get("to")},两端实测日同现'
                          '正文——数字+窗口耦合可核;与周/MTD 派生窗'
                          '并行基,R21 任务4)')))
                continue
        fixed.append(ch)
    return fixed


def verify_judgment(judgment, report, thresholds=None, face=None):
    """判定档 vs 自身证据面 → {'verdicts','six_checks','verdict','stats'}。

    face 已建(如冻结夹具/上游复用)则直用,免重复构建。
    """
    face = face if face is not None else build_face(report)
    thresholds_by = cf.thresholds_by_metric(
        thresholds if thresholds is not None else cf.load_thresholds())
    verdicts, unbound_left = [], []
    n_contra = n_ver = 0
    _am_rows = _asset_window_basis(report)
    l3 = ((judgment.get('l3') or {}).get('contradictions')) or []
    for con in l3:
        for field in ('statement', 'basis'):
            text = con.get(field) or ''
            if not text:
                continue
            r = tc.check_text(text, snapshot=face, thresholds=thresholds_by)
            r['checks'] = _asset_window_recheck(r['checks'], text, _am_rows)
            for ch in r['checks']:
                verdicts.append(dict(
                    {'item': f"{con.get('id')}.{field}", 'claim_type':
                     'objective_fact', 'unit': '', 'evidence_refs':
                     [ch['metric']] if ch.get('metric') else []}, **ch))
                n_contra += ch['status'] == 'CONTRADICTED'
                n_ver += ch['status'] == 'VERIFIED'
            # 统计结论复算(类B)+消费
            b_checks, consumed = _class_b(text, face)
            for ch in b_checks:
                verdicts.append(dict(
                    {'item': f"{con.get('id')}.{field}",
                     'evidence_refs': [ch['metric_id']]}, **ch))
                n_contra += ch['status'] == 'CONTRADICTED'
                n_ver += ch['status'] == 'VERIFIED'
            for u in r['unbound']:
                raw = re.sub(r'\s*(?:pp|个百分点|percentage points?|bp|%)$',
                             '', u['raw'].strip().lstrip('+−-'))
                if raw in consumed:
                    continue          # 类B已复算
                if _INST_CITE_RE.search(u['ctx']):
                    continue          # 机构归因式引用(vp_sidecar 域)
                unbound_left.append({'item': f"{con.get('id')}.{field}",
                                     **u})
    six = _six_checks(judgment, face)
    six_bad = [s for s in six if s['status'] != 'VERIFIED']
    map_checks = _map_checks(judgment, face, report)
    map_bad = [s for s in map_checks if s['status'] != 'VERIFIED']
    map_contra = [s for s in map_checks if s['status'] == 'CONTRADICTED']
    n_contra += len(map_contra)
    if n_contra:
        verdict = 'CONTRADICTED'     # 客观事实错→整体降级,渲染面披露
    elif unbound_left or six_bad or map_bad:
        verdict = 'NOT_VERIFIED'
    else:
        verdict = 'VERIFIED'
    return {
        'version': JUDGMENT_CONTRACT_VERSION,
        'verdicts': verdicts,
        'six_checks': six,
        'map_checks': map_checks,
        'unresolved_unbound': unbound_left,
        'verdict': verdict,
        'stats': {
            'checks': len(verdicts), 'contradicted': n_contra,
            'verified': n_ver, 'unbound': len(unbound_left),
            'six_fail': len(six_bad), 'map_fail': len(map_bad),
            'n_contradictions': len(l3),
        },
    }


# ── Audit-R18: 地图问句 reader_map 契约(结构非空+数值回贴核对) ────────

def _rmp_fallback_month_last(dates, values):
    """research_map_planner 不可导入时的月末兜底(同口径,无同比派生)。"""
    out, seen = [], {}
    for dd, vv in zip(dates or [], values or []):
        seen[str(dd)[:7]] = vv
    return [(ym, ym + '-01', v) for ym, v in sorted(seen.items())]


# Audit-R33 任务5(修订): 对质观测窗与结构化复算——传导环可选字段
# observation_window{from,to:'YYYY-MM'[,yoy]} / face_off_check{main,competing:
# {op,value,unit}}。裁决所依据的观测须与预测同窗;两解释预期按冻结序列复算
# 后与 face_off_verdict 对账(同时成立或同时不成立=尚不能区分)。
_FO_OPS = {
    '>=': lambda a, b: a >= b, '>': lambda a, b: a > b,
    '<=': lambda a, b: a <= b, '<': lambda a, b: a < b,
    '==': lambda a, b: abs(a - b) < 1e-9, '!=': lambda a, b: abs(a - b) >= 1e-9}


def _fo_window_points(win, dm, face):
    """对质观测窗内的月末观测点 [(ym, date, value)] 与失败原因 → (pts, why)。

    规则唯一出处=research_map_planner._face_off_window_points(对质表渲染
    _window_obs 同调): 契约与读者面不得各算一套。"""
    ser = (face.get('series_store') or {}).get(dm) or {}
    try:
        import research_map_planner as _rmp
    except ImportError:
        return None, 'research_map_planner 不可导入——观测窗无从复算'
    return _rmp._face_off_window_points(
        ser.get('dates') or [], ser.get('values') or [], ser.get('unit'),
        win, dm)


def _fo_change(pts, unit):
    """观测窗首尾变化: pct=相对幅(%);bp=百分比水平差的基点;pp=百分点差。"""
    v0, v1 = float(pts[0][2]), float(pts[-1][2])
    if unit == 'pct':
        return (v1 / v0 - 1.0) * 100.0 if v0 else None
    if unit == 'bp':
        return (v1 - v0) * 100.0
    if unit == 'pp':
        return v1 - v0
    return None


def _fo_face_off_checks(lk, lid, dm, face, plan, ok, bad):
    win, fck = lk.get('observation_window'), lk.get('face_off_check')
    if win is None and fck is None:
        return
    if not str(lk.get('competing_explanation') or '').strip():
        bad(f'{lid}.observation_window', '对质观测窗/结构化复算须配竞争解释')
        return
    cutoff = str(plan.get('cutoff') or '')[:7]
    pts, why = None, None
    if win is not None:
        wto = str(win.get('to') or '')[:7] if isinstance(win, dict) else ''
        if cutoff and re.fullmatch(r'\d{4}-\d{2}', wto) and wto > cutoff:
            # 先于取数: 截止日之后的观测不得进裁决(读者面 _window_obs 同序)
            bad(f'{lid}.observation_window',
                f'观测窗终点 {wto} 晚于研究截止月 '
                f'{cutoff}——不得用截止日之后的观测裁决')
        else:
            pts, why = _fo_window_points(win, dm, face)
            if pts is None:
                bad(f'{lid}.observation_window', why)
            else:
                ok(f'{lid}.observation_window',
                   f"窗 {pts[0][0]}→{pts[-1][0]} 内 {len(pts)} 期月末观测"
                   f"({pts[0][2]:g}→{pts[-1][2]:g}"
                   f"{';同比空间' if win.get('yoy') else ''})")
    if fck is None:
        return
    if not isinstance(fck, dict) or not isinstance(fck.get('main'), dict) \
            or not isinstance(fck.get('competing'), dict):
        bad(f'{lid}.face_off_check', '结构化对质须含 main 与 competing 两侧预期')
        return
    if pts is None:
        bad(f'{lid}.face_off_check',
            '结构化对质须带可复算的 observation_window' + (f'({why})' if why else ''))
        return
    sides = {}
    for side, lbl in (('main', '主解释'), ('competing', '竞争解释')):
        p = fck[side]
        op, val, unit = str(p.get('op') or ''), p.get('value'), str(p.get('unit') or '')
        if (op not in _FO_OPS or not isinstance(val, (int, float))
                or isinstance(val, bool) or unit not in ('pct', 'bp', 'pp')):
            bad(f'{lid}.face_off_check.{side}',
                f'{lbl}预期须为 {{op: >=/>/<=/</==/!=, value: 数值, '
                'unit: pct/bp/pp}')
            return
        chg = _fo_change(pts, unit)
        if chg is None:
            bad(f'{lid}.face_off_check.{side}',
                f'{lbl}预期按 {unit} 口径不可复算(基期为零或缺席)')
            return
        sides[side] = (op, float(val), unit, chg,
                       bool(_FO_OPS[op](round(chg, 6), float(val))))
    m_ok, c_ok = sides['main'][4], sides['competing'][4]
    expected = ('尚不能区分' if m_ok == c_ok else
                '支持主解释' if m_ok else '支持竞争解释')
    detail = ';'.join(
        f"{lbl}预期 {op} {val:g}{unit}→观测 {chg:+.2f}{unit} "
        f"{'成立' if ok_ else '不成立'}"
        for (op, val, unit, chg, ok_), lbl in zip(
            (sides['main'], sides['competing']), ('主解释', '竞争解释')))
    fv = str(lk.get('face_off_verdict') or '').strip()
    if fv != expected:
        bad(f'{lid}.face_off_verdict',
            f'对质判断与结构化复算不一致: {detail}→应为 {expected}'
            f'(声明 {fv or "空"})', contra=True)
    else:
        ok(f'{lid}.face_off_check', f'{detail}→{expected}')

def _map_checks(judgment, face, report):
    """地图问句判定须含完整 reader_map;数值须与引擎序列回贴一致。

    任务4反例面: 机制正文空/None、必需图表(对照/传导/转折/历史)缺失、
    明确指定指标遗漏——结构缺席或数值与引擎确定性面相左都在此拦;
    空正文/缺图表=NOT_VERIFIED(修档再提),数值相左=CONTRADICTED。"""
    plan = (report or {}).get('research_plan') or {}
    if plan.get('question_kind') == 'policy_question':
        # Audit-R33 任务3: 原问直答型问句走分面回声契约(五面契约不适用)
        return _policy_question_checks(judgment, face, report, plan)
    if not plan.get('map_question'):
        return []
    out = []

    def ok(item, note):
        out.append({'item': item, 'claim_type': 'reader_map',
                    'status': 'VERIFIED', 'note': note,
                    'evidence_refs': []})

    def bad(item, note, contra=False):
        out.append({'item': item, 'claim_type': 'reader_map',
                    'status': 'CONTRADICTED' if contra else 'NOT_VERIFIED',
                    'note': note, 'evidence_refs': []})

    rm = judgment.get('reader_map')
    if not isinstance(rm, dict):
        bad('reader_map', '地图问句判定须含 reader_map 顶层对象'
            '(总判断/走位/传导/转折/历史五面)')
        return out
    if not str(rm.get('headline_conclusion') or '').strip():
        bad('reader_map.headline_conclusion', '一句总判断为空或 None')
    else:
        ok('reader_map.headline_conclusion', '非空')
    planned_regions = set((plan.get('regions') or {}).keys())
    got_regions = {r.get('region') for r in rm.get('regions') or []
                   if isinstance(r, dict)}
    if planned_regions - got_regions:
        bad('reader_map.regions', f'计划地区缺走位条目: '
            f'{sorted(planned_regions - got_regions)}(每地须写清从什么'
            '环境走到什么环境)')
    else:
        ok('reader_map.regions', f'{len(planned_regions)} 地齐')
    for r in rm.get('regions') or []:
        if not str(r.get('from_to') or '').strip():
            bad(f"reader_map.regions[{r.get('region')}].from_to",
                '环境走位为空或 None')
    chains = rm.get('transmission') or []
    if not chains:
        bad('reader_map.transmission', '传导图缺席(至少一条链)')
    for ci, ch in enumerate(chains):
        links = ch.get('links') or []
        if not links:
            bad(f'reader_map.transmission[{ci}].links', '传导链零环')
        for li, lk in enumerate(links):
            lid = f'reader_map.transmission[{ci}].links[{li}]'
            for fld, lbl in (('observed_fact', '观察事实'),
                             ('causal_hypothesis', '因果假设'),
                             ('competing_explanation', '竞争解释'),
                             ('distinguishing_metric', '区分指标')):
                if not str(lk.get(fld) or '').strip():
                    bad(f'{lid}.{fld}', f'传导环{lbl}为空或 None')
            dm = str(lk.get('distinguishing_metric') or '').strip()
            if dm and dm not in (face.get('series_store') or {}) and \
                    dm not in (plan.get('metrics') or []) and \
                    dm not in (plan.get('context_metrics') or []):
                bad(f'{lid}.distinguishing_metric',
                    f'区分指标 {dm} 不在计划指标/证据序列面', contra=True)
            # Audit-R22 任务4(软契约): 竞争解释在场时,主/竞争两侧对同一
            # 区分指标的不同预期(main_predicts/competing_predicts)与判断
            # (face_off_verdict)宜分立——旧档无此字段不判错(原文复放必须
            # 通过),新席应填(渲染层缺席如实注记)。在场时校验形态:
            # verdict 三态闭集;预期只填一侧=分立不完整。
            if str(lk.get('competing_explanation') or '').strip():
                mp_ = str(lk.get('main_predicts') or '').strip()
                cp_ = str(lk.get('competing_predicts') or '').strip()
                if bool(mp_) != bool(cp_):
                    bad(f'{lid}.main_predicts',
                        '主/竞争解释预期只填一侧——对质面须两侧分立'
                        '(或两侧都不填,渲染层记尚不能区分)')
                fv = str(lk.get('face_off_verdict') or '').strip()
                if fv and fv not in ('支持主解释', '支持竞争解释',
                                     '尚不能区分'):
                    bad(f'{lid}.face_off_verdict',
                        f'对质判断三态闭集外({fv!r})——须为 支持主解释/'
                        '支持竞争解释/尚不能区分 之一')
            # Audit-R33 任务5(修订;软契约): 对质观测窗与结构化复算——
            # 字段在场才核(同窗观测复算+预期成立性+与判断对账),旧档不判错。
            _fo_face_off_checks(lk, lid, dm, face, plan, ok, bad)
    turnings = rm.get('turnings') or []
    if len(turnings) != 3:
        bad('reader_map.turnings', f'三个转折须恰为 3(得 {len(turnings)})')
    cands = (plan.get('turning_candidates') or {}).get('candidates') or []
    cand_keys = {(c.get('metric_id'), str(c.get('to_ym'))) for c in cands}
    for ti, t in enumerate(turnings):
        tid = f'reader_map.turnings[{ti}]'
        if not str(t.get('date') or '').strip():
            bad(f'{tid}.date', '转折日期为空')
        for fld, lbl in (('first_mover', '谁先变'),
                         ('follow_or_diverge', '跟进/背离')):
            if not str(t.get(fld) or '').strip():
                bad(f'{tid}.{fld}', f'{lbl}为空或 None')
        mid = t.get('metric_id')
        if mid not in (face.get('series_store') or {}):
            bad(f'{tid}.metric_id', f'转折指标 {mid} 不在证据序列面',
                contra=True)
            continue
        # 数值回贴: 声明的前/后值 vs 引擎序列月末口径复算(水平序列
        # 与引擎候选面同口径=同比空间,指数漂移不作转折值)
        ser = face['series_store'].get(mid) or {}
        dates, values = ser.get('dates') or [], ser.get('values') or []
        try:
            import research_map_planner as _rmp
            _mon_all = _rmp._monthly_series_for_turning(
                dates, values, ser.get('unit'))
        except Exception:
            _mon_all = _rmp_fallback_month_last(dates, values)
        _mon_by_ym = {ymq: v for ymq, _d, v in _mon_all}
        d = str(t.get('date') or '')
        ym = d[:7]
        if len(ym) != 7 or not dates:
            bad(f'{tid}.date', f'转折日期不可解析: {d!r}')
            continue

        def _month_last(ymq):
            if ymq in _mon_by_ym:
                return _mon_by_ym[ymq]
            best = None
            for dd, vv in zip(dates, values):
                if dd[:7] == ymq:
                    best = vv
            return best

        after = _month_last(ym)
        if after is None:
            bad(f'{tid}', f'转折月 {ym} 序列无观测(不可虚构转折)')
            continue
        try:
            stated_after = float(t.get('value_after'))
            if abs(stated_after - float(after)) > 1e-6:
                bad(f'{tid}.value_after', f'后值与引擎月末口径不符'
                    f'(声明 {stated_after} vs 复算 {after})', contra=True)
        except (TypeError, ValueError):
            bad(f'{tid}.value_after', '后值非数值')
        # 前值: 有 before_date 按其月;否则按引擎候选面 3 月窗
        bd = str(t.get('before_date') or '')
        bym = bd[:7]
        if len(bym) != 7:
            match = next((c for c in cands
                          if c.get('metric_id') == mid
                          and str(c.get('to_ym')) == ym), None)
            bym = match['from_ym'] if match else None
        if bym is None:
            bad(f'{tid}.before_date', '前值基准月缺席(给 before_date 或'
                '对齐引擎候选面 3 月窗)')
            continue
        before = _month_last(bym)
        if before is None:
            bad(f'{tid}', f'前值基准月 {bym} 序列无观测')
            continue
        try:
            stated_before = float(t.get('value_before'))
            if abs(stated_before - float(before)) > 1e-6:
                bad(f'{tid}.value_before', f'前值与引擎月末口径不符'
                    f'(声明 {stated_before} vs 复算 {before})', contra=True)
        except (TypeError, ValueError):
            bad(f'{tid}.value_before', '前值非数值')
        if (mid, ym) not in cand_keys:
            bad(f'{tid}', f'转折 ({mid},{ym}) 不在引擎候选面(前9候选)——'
                '须引用候选面或在叙述中说明取舍依据', contra=False)
    hist = rm.get('history_periods') or []
    # Audit-R20 任务3: 历史类比 0..3 段——零段合法但必须写明检索范围与
    # 原因(不许空白交差);1..3 段时逐段结构核验(下同 R19)。
    if len(hist) > 3:
        bad('reader_map.history_periods',
            f'历史栏至多 3 段(得 {len(hist)})')
    if len(hist) == 0 and not str(
            rm.get('history_zero_case_note') or '').strip():
        bad('reader_map.history_zero_case_note',
            '零段类比须给 history_zero_case_note(检索范围+原因——'
            'R20: 历史类比取 0..3 段,零段时如实写明,不以空白交差)')
    for hi, h in enumerate(hist):
        hid = f'reader_map.history_periods[{hi}]'
        for fld, lbl in (('period_label', '时期(年月)'),
                         ('similarity', '相似点'),
                         ('difference', '关键差异'),
                         ('other_regions_sync', '其他经济体是否同步')):
            if not str(h.get(fld) or '').strip():
                bad(f'{hid}.{fld}', f'{lbl}为空或 None')
        ex = h.get('ex_post') or {}
        for k, lbl in (('3m', '随后3个月'), ('6m', '随后6个月'),
                       ('12m', '随后12个月')):
            if not str(ex.get(k) or '').strip():
                bad(f'{hid}.ex_post.{k}', f'{lbl}实际表现为空(不可得须明写'
                    '「数据不可得」而非留空)')
        # ── Audit-R19 任务4: 结构化窗口面(匹配区间/判断截止月/事后窗) ──
        aym = str(h.get('anchor_ym') or '')
        mw = h.get('match_window') or {}
        if len(aym) != 7:
            bad(f'{hid}.anchor_ym', '历史段须给结构化锚月 anchor_ym'
                '(YYYY-MM,事后窗=锚月+N 月的机器核验基准)')
        elif not (isinstance(mw, dict) and str(mw.get('start_ym') or '')
                  and str(mw.get('end_ym') or '')):
            bad(f'{hid}.match_window', '历史段须给匹配区间 match_window'
                '{start_ym,end_ym}(判断只用截至 judgment_cutoff_ym 已发布'
                '的数据;匹配区间与事后窗分记)')
        else:
            try:
                import research_map_planner as _rmp2
                exp = _rmp2.ex_post_windows(aym)
            except Exception:
                exp = {'3m': _ym_shift(aym, 3), '6m': _ym_shift(aym, 6),
                       '12m': _ym_shift(aym, 12)}
            aft = [str(x) for x in (h.get('aftermath_obs_months') or [])]
            if not aft:
                bad(f'{hid}.aftermath_obs_months',
                    '历史段须给事后实际观测月 aftermath_obs_months'
                    '(YYYY-MM 列表——事后窗到达与不落入匹配期两检的基准)')
            else:
                missing = [k for k, v in exp.items() if v not in aft]
                if missing:
                    bad(f'{hid}.ex_post_reach',
                        f'事后窗未到达: 锚{aym} 的 {missing} 应分别到 '
                        f'{[exp[k] for k in missing]}(aftermath_obs_months '
                        '缺该月——3/6/12 月窗必须实测到月,不可止步窗内)')
                end_ym = str(mw.get('end_ym'))
                leaked = [m for m in aft if m <= end_ym]
                if leaked:
                    bad(f'{hid}.aftermath_in_match',
                        f'历史结果落在匹配期内: {leaked} ≤ 匹配区间末月 '
                        f'{end_ym}——事后实际表现须取匹配窗之外(判断截止'
                        '月后)的观测,匹配期内数值不是事后结果', contra=True)
            cut = str(h.get('judgment_cutoff_ym') or '')
            if not cut:
                bad(f'{hid}.judgment_cutoff_ym',
                    '历史段须给判断截止月 judgment_cutoff_ym(YYYY-MM——'
                    '历史对照只用当时已发布数据的时点界)')
            elif cut < str(mw.get('end_ym') or ''):
                bad(f'{hid}.judgment_cutoff_ym',
                    f'判断截止月 {cut} 早于匹配区间末月 {mw.get("end_ym")}'
                    '——匹配窗末月数据在截止月尚未发布,不可引用')

    # ── Audit-R19 任务5: 四阻断器 + 任务3 维度覆盖 ────────────────────
    # (1) 同比基期: 引擎点值面自检——凡给了 derived_yoy_pct 的锚格,基期
    #     必须=去年同月/同季(缺基期格必须是 None+yoy_status 标注)。
    pv = plan.get('point_values') or {}
    for ci, c in enumerate(pv.get('cells') or []):
        for lbl, a in (c.get('anchors') or {}).items():
            if a.get('status') != 'ok' or \
                    not str(a.get('value_kind', '')).startswith('level'):
                continue
            if a.get('derived_yoy_pct') is not None and \
                    a.get('yoy_status') not in (None, 'ok'):
                bad('point_values.yoy_base',
                    f'{c.get("metric_id")}@{lbl}: 同比值在而基期状态非 ok'
                    '(同比基期纪律破坏——缺基期不得给同比数)', contra=True)
            if a.get('derived_yoy_pct') is None and \
                    a.get('yoy_status') != 'no_same_period_base':
                bad('point_values.yoy_base',
                    f'{c.get("metric_id")}@{lbl}: 水平序列同比缺席但未标 '
                    'no_same_period_base(缺基期须标不可得+另列最近有效同比)')
    # (2) 提前引用未发布: 锚格 publication_date 必须 ≤ as_of。
    for ci, c in enumerate(pv.get('cells') or []):
        for lbl, a in (c.get('anchors') or {}).items():
            if a.get('status') != 'ok':
                continue
            pub, as_of = str(a.get('publication_date') or ''), \
                str(a.get('as_of') or '')
            if pub and as_of and pub > as_of:
                bad('point_values.publication',
                    f'{c.get("metric_id")}@{lbl}: 发布日 {pub} 晚于锚日 '
                    f'{as_of}(历史对照只用当时已发布的数据)', contra=True)
    # (3) 同一转折重复三次: 三转折 (metric_id, 月) 两两互异 + 维度覆盖。
    keys = []
    for t in turnings:
        keys.append((t.get('metric_id'), str(t.get('date') or '')[:7]))
    if len(keys) == 3 and len(set(keys)) < 3:
        dup = [k for k in set(keys) if keys.count(k) > 1]
        bad('reader_map.turnings.duplicate',
            f'同一转折重复计数: {dup}(三个转折须为不同事件/不同指标-月)')
    cand_dim = {c.get('metric_id'): c.get('dimension') for c in cands}
    sel_dims = {cand_dim.get(k[0]) for k in keys} - {None}
    pool_dims = {c.get('dimension') for c in cands}
    if len(keys) == 3 and len(pool_dims - {None}) >= 2 and len(sel_dims) < 2:
        bad('reader_map.turnings.dimension_coverage',
            f'三转折维度覆盖不足: 选中 {sorted(sel_dims)} 而候选池跨 '
            f'{sorted(pool_dims)}(增长/通胀/政策都进入候选后,三转折至少'
            '跨两维,不同维度的转折不得互相顶替)')
    # (4) aftermath_in_match 已在历史段逐条拦(contra=True)。
    # 任务3: 传导图须从冲击连到指标与资产(资产面在场时)。
    au = pv.get('asset_universe') or []
    if au:
        blob = []
        for ch in chains:
            for lk in ch.get('links') or []:
                blob.append(str(lk.get('observed_fact') or ''))
                blob.append(str(lk.get('distinguishing_metric') or ''))
        hit = any(a in ' '.join(blob) for a in au)
        if not hit:
            bad('reader_map.transmission.asset_reach',
                f'传导图未连到资产指标(资产面在场 {len(au)} 项,如 '
                f'{au[:4]}…)——传导链须从冲击连到指标与资产,每环标事实'
                '或假设')

    # ── Audit-R20 任务3/任务5: 三类数值回贴 + 情景方向(正文数字须与 ──
    # 引擎确定性面同源对账;错月/错窗/编回报=CONTRADICTED,缺席回贴=
    # NOT_VERIFIED——四个反例中「正文月份错误/编造回报/提前引用」的
    # 确定性拦截路径)。
    # (6) 锚值回贴 anchor_echo: 含数字的走位叙述须按地区回贴锚值
    #     (数值+观测月与引擎点值面逐位一致)。
    engine_cell = {}
    for c in pv.get('cells') or []:
        for lbl, a in (c.get('anchors') or {}).items():
            if a.get('status') == 'ok':
                engine_cell[(c.get('region'), lbl,
                             c.get('metric_id'))] = a
    for r in rm.get('regions') or []:
        region = r.get('region')
        text = str(r.get('from_to') or '')
        echoes = r.get('anchor_echo') or []
        if re.search(r'\d', text) and not echoes:
            bad(f'reader_map.regions[{region}].anchor_echo',
                '走位叙述含数字但未回贴锚值(anchor_echo 缺席——叙述数字'
                '必须可对账引擎点值面,R20 正文月份错误反例的拦截位)')
        for ei, e in enumerate(echoes):
            eid = f'reader_map.regions[{region}].anchor_echo[{ei}]'
            a = engine_cell.get((region, e.get('anchor'), e.get('metric_id')))
            if a is None:
                bad(eid, f'锚格不存在或锚前不可见({e.get("metric_id")}@'
                    f'{e.get("anchor")})——不可虚构不在引擎点值面的锚值'
                    '(提前引用未发布数据反例的拦截位)', contra=True)
                continue
            try:
                if abs(float(e.get('value')) - float(a.get('value'))) > 5e-3:
                    bad(eid, f'锚值与引擎不符(声明 {e.get("value")} vs '
                        f'引擎 {a.get("value")})', contra=True)
                    continue
            except (TypeError, ValueError):
                bad(eid, 'echo 值非数值')
                continue
            obs_m = str(e.get('observation_month') or '')[:7]
            eng_m = str(a.get('observation_date') or '')[:7]
            if obs_m and obs_m != eng_m:
                bad(eid, f'观测月不符(声明 {obs_m} vs 引擎 {eng_m})——'
                    '正文月份错误', contra=True)
    # (7) 三利率分解回贴 rates_decomposition(引擎共同交易日面在场时必答)。
    trio = plan.get('us_rates_trio') or {}
    if trio.get('status') == 'ok':
        rd_echo = rm.get('rates_decomposition') or {}
        chg = trio.get('chg_bp') or {}
        w = trio.get('window') or {}
        need = {'window_from': w.get('from'), 'window_to': w.get('to'),
                'nominal_bp': chg.get('UST_10Y'),
                'real_bp': chg.get('TIPS_10Y'),
                'bei_bp': chg.get('BEI_10Y')}
        if not rd_echo:
            bad('reader_map.rates_decomposition',
                '三利率共同交易日分解面在场但判定未回贴(rates_decomposition'
                ' 缺席——正文利率分解数字必须与引擎同窗复算一致)')
        else:
            for k, ev in need.items():
                rv = rd_echo.get(k)
                if isinstance(ev, (int, float)):
                    try:
                        if abs(float(rv) - float(ev)) > 1e-6:
                            bad('reader_map.rates_decomposition',
                                f'{k} 与引擎不符(声明 {rv} vs 共同交易日'
                                f'复算 {ev})——分量与名义须同窗逐位对账',
                                contra=True)
                    except (TypeError, ValueError):
                        bad('reader_map.rates_decomposition',
                            f'{k} 非数值')
                elif str(rv or '') != str(ev or ''):
                    bad('reader_map.rates_decomposition',
                        f'{k} 与引擎不符(声明 {rv!r} vs {ev!r})', contra=True)
    # (8) 资产回报回贴 asset_returns_echo(叙述含回报/涨跌主张时必答)。
    blob_txt = ' '.join(
        [str(rm.get('headline_conclusion') or '')]
        + [str(r.get('from_to') or '') for r in rm.get('regions') or []]
        + [str(lk.get('observed_fact') or '')
           for ch in chains for lk in ch.get('links') or []])
    if re.search(r'回报|涨幅|跌幅|上涨|下跌|涨|跌', blob_txt):
        ar = rm.get('asset_returns_echo') or []
        if not ar:
            bad('reader_map.asset_returns_echo',
                '叙述含回报/涨跌类主张但未回贴资产回报(asset_returns_echo '
                '缺席——回报数字须可对账引擎同窗复算,R20 编造回报反例的'
                '拦截位)')
        else:
            _cut = str(plan.get('cutoff') or '')
            if not _cut:
                bad('reader_map.asset_returns_echo',
                    '计划截止日缺席,资产回报回贴无法执行')
            else:
                try:
                    import research_map_planner as _rmp3
                    for ei, e in enumerate(ar):
                        eid = f'reader_map.asset_returns_echo[{ei}]'
                        mid = e.get('metric_id')
                        ser = (face.get('series_store') or {}).get(mid)
                        if not ser or not (ser.get('dates')):
                            bad(eid, f'资产 {mid} 不在证据序列面',
                                contra=True)
                            continue
                        try:
                            _m = int(e.get('window_months'))
                        except (TypeError, ValueError):
                            bad(eid, 'window_months 非整数月窗')
                            continue
                        eng = _rmp3.asset_move_rows({mid: ser}, _cut,
                                                    months=_m)
                        row = next((rr for rr in eng.get('rows') or []
                                    if rr.get('metric_id') == mid), None)
                        if row is None:
                            bad(eid, f'{mid} {_m} 个月窗不可复算(端点缺数)'
                                '——不可引用无法复算的回报', contra=True)
                            continue
                        try:
                            if abs(float(e.get('chg_pct'))
                                   - float(row.get('chg_pct'))) > 0.011:
                                bad(eid, f'回报与引擎不符(声明 '
                                    f'{e.get("chg_pct")}% vs 同窗复算 '
                                    f'{row.get("chg_pct")}%)——编造回报数字',
                                    contra=True)
                                continue
                        except (TypeError, ValueError):
                            bad(eid, 'chg_pct 非数值')
                            continue
                        w_echo = e.get('window') or {}
                        if (str(w_echo.get('from') or '')
                                != str((row.get('window') or {}).get('from'))
                                or str(w_echo.get('to') or '')
                                != str((row.get('window') or {}).get('to'))):
                            bad(eid, f'计算窗口与引擎不符(声明 '
                                f'{w_echo.get("from")}..{w_echo.get("to")} vs '
                                f'{(row.get("window") or {}).get("from")}..'
                                f'{(row.get("window") or {}).get("to")})——'
                                '回报主张必须带可复算窗口', contra=True)
                except ImportError:
                    bad('reader_map.asset_returns_echo',
                        'research_map_planner 不可导入,资产回报回贴无法执行')
    # (9) 情景触发/失效方向: L4 scenarios 结构面已由 _six_checks 逐席校验
    # (trigger/falsification 阈值形态+算术一致性);R20 任务3 的读者面
    # 要求=MAP_REPORT 渲染层把两情景的触发与失效方向分别展示
    # (render_map_report l4 段),此处不重复立契约。
    # ── Audit-R21 任务3: 事后正文数值/正文月份/月频时序三阻断 ──────────
    # (10) 事后正文数值回贴 history_prose_echo: 历史段 ex_post 正文里的
    #     「METRIC ±N.NN%(/pp)」须与引擎同窗复算一致——反例①只改正文把
    #     −6.27% 改成 +99.00% 而校验字段原样时,此为唯一确定性拦截位。
    def _month_last_obs(dates, values, ym):
        hi_i = bisect.bisect_right(dates, ym + '-31')
        j = hi_i - 1
        while j >= 0 and values[j] is None:
            j -= 1
        return (dates[j], values[j]) if j >= 0 else (None, None)

    for hi, h in enumerate(hist):
        hid = f'reader_map.history_periods[{hi}]'
        aym = str(h.get('anchor_ym') or '')
        if len(aym) != 7:
            continue
        try:
            import research_map_planner as _rmp4
            exp = _rmp4.ex_post_windows(aym)
        except Exception:
            exp = {'3m': _ym_shift(aym, 3), '6m': _ym_shift(aym, 6),
                   '12m': _ym_shift(aym, 12)}
        ex = h.get('ex_post') or {}
        for k in ('3m', '6m', '12m'):
            txt = str(ex.get(k) or '')
            tgt = exp.get(k)
            if not txt or not tgt:
                continue

            def _eng_recompute(mid, unit):
                """锚月末→tgt 月末引擎复算值(None=不可复算,不判)。"""
                ser = (face.get('series_store') or {}).get(mid)
                if not ser or not ser.get('dates'):
                    return None
                d0, v0 = _month_last_obs(ser['dates'], ser['values'], aym)
                d1, v1 = _month_last_obs(ser['dates'], ser['values'], tgt)
                if v0 is None or v1 is None or d0 == d1:
                    return None
                try:
                    return (((v1 / v0 - 1.0) * 100.0 if unit == '%'
                             else v1 - v0), d0, v0, d1, v1)
                except (TypeError, ZeroDivisionError):
                    return None

            # Audit-R22 任务3: pp 容差收紧 0.6→0.06——0.85pp 写成 0.35pp
            # 这类同量级窜写在旧容差下蒙混(% 容差维持 0.6,日内重定价与
            # 复权噪声留给百分比口径)。
            for mt in re.finditer(
                    r'([A-Z][A-Z0-9_]{1,20})\s*'
                    r'([+\-−]?[0-9]+(?:\.[0-9]+)?)\s*个?(pp|%|指数点)',
                    txt):
                mid, num, unit = mt.group(1), mt.group(2), mt.group(3)
                num = float(num.replace('−', '-'))
                rc = _eng_recompute(mid, unit)
                if rc is None:
                    continue
                eng_num, d0, v0, d1, v1 = rc
                # Audit-R24 任务3: 指数点=水平差的另一合法记法
                # (CPI 266.614→271.903 写 +5.29 指数点或 +1.98% 均可核,
                # 同窗同引擎面;pp/指数点共用 0.06 紧容差)
                tol = 0.06 if unit in ('pp', '指数点') else 0.6
                if abs(num - eng_num) > tol:
                    bad(f'{hid}.ex_post.{k}',
                        f'事后窗数字与引擎不符: {mid} {num:+.2f}{unit} vs '
                        f'锚月{aym}末→{tgt}末复算 {eng_num:+.2f}{unit}'
                        f'({d0}={v0}→{d1}={v1})——编造事后回报',
                        contra=True)
            # Audit-R22 任务3: 中文别名面——「标普500指数上涨99.00%」一类
            # 中文窜写在 ASCII ticker 正则下静默漏检。别名(最长匹配优先)
            # +方向词(上涨/下跌…给隐式符号)+单位词(个百分点=pp)。方向词
            # 与显式符号矛盾=直接判错;无方向词无符号=符号不明不判(诚实
            # 缺省,留读者看原文)。
            _cn = [('标普500指数', 'SPX'), ('标普500', 'SPX'),
                   ('纳斯达克', 'NASDAQ_COMPOSITE'), ('日经225', 'NIKKEI225'),
                   ('日经指数', 'NIKKEI225'), ('美元指数', 'DXY'),
                   ('美国十年期国债收益率', 'UST_10Y'),
                   ('十年期美债收益率', 'UST_10Y'), ('十年期美债', 'UST_10Y'),
                   ('美债十年期', 'UST_10Y'), ('美债收益率', 'UST_10Y'),
                   ('黄金期货', 'GOLD_F'), ('黄金', 'GOLD_F')]
            _up = ('上涨', '上升', '走高', '攀升', '反弹', '上行', '升高',
                   '累涨', '涨')
            _down = ('下跌', '下降', '走低', '回落', '下挫', '下行', '走弱',
                     '累跌', '跌')
            _cn_spans = []
            for alias, mid in _cn:
                for am in re.finditer(re.escape(alias), txt):
                    if any(s0 <= am.start() and am.end() <= e0
                           for s0, e0 in _cn_spans):
                        continue    # 已被更长别名覆盖(标普500⊂标普500指数)
                    _cn_spans.append((am.start(), am.end()))
                    tail = txt[am.end():am.end() + 34]
                    m2 = re.match(
                        r'[^0-9+\-−.]{0,16}?([+\-−]?)([0-9]+(?:\.[0-9]+)?)'
                        r'\s*个?(个百分点|%|指数点)', tail)
                    if not m2:
                        continue
                    sign, num_s, unit_w = m2.groups()
                    unit = ('pp' if unit_w == '个百分点'
                            else ('指数点' if unit_w == '指数点' else '%'))
                    num = float(num_s)
                    gap = tail[:m2.start(1)]
                    v_up = any(w in gap for w in _up)
                    v_dn = any(w in gap for w in _down)
                    if sign:
                        s = -1 if sign in '-−' else 1
                        if v_up and s < 0 or v_dn and s > 0:
                            bad(f'{hid}.ex_post.{k}',
                                f'中文方向词与符号矛盾: 「{alias}'
                                f'{gap}{sign}{num_s}{unit_w}」——方向说反'
                                '不蒙混(与 R21 资产月窗带符号比对同口径)',
                                contra=True)
                            continue
                        num = s * num
                    elif v_up:
                        num = abs(num)
                    elif v_dn:
                        num = -abs(num)
                    else:
                        continue          # 无方向无符号=符号不明,不判
                    rc = _eng_recompute(mid, unit)
                    if rc is None:
                        continue
                    eng_num, d0, v0, d1, v1 = rc
                    tol = 0.06 if unit in ('pp', '指数点') else 0.6
                    if abs(num - eng_num) > tol:
                        bad(f'{hid}.ex_post.{k}',
                            f'事后窗数字与引擎不符(中文面): {alias}({mid}) '
                            f'{num:+.2f}{unit} vs 锚月{aym}末→{tgt}末复算 '
                            f'{eng_num:+.2f}{unit}({d0}={v0}→{d1}={v1})'
                            '——编造事后回报',
                            contra=True)
    # (11) 正文月份扫描: 走位正文里的 YYYY-MM 须落在引擎面月份集(序列
    #     观测月∪锚观测月∪候选窗∪历史结构面∪资产窗)——反例②只把美国
    #     正文观测月改成 2030-07 而校验字段原样时,此为拦截位。
    eng_months = set()
    for _ser in (face.get('series_store') or {}).values():
        eng_months.update(str(d)[:7] for d in _ser.get('dates') or [])
    for _c in (plan.get('point_values') or {}).get('cells') or []:
        for _a in (_c.get('anchors') or {}).values():
            _od = str(_a.get('observation_date') or '')
            if _od:
                eng_months.add(_od[:7])
    for _t in (plan.get('turning_candidates') or {}).get('candidates') or []:
        eng_months.add(str(_t.get('from_ym') or ''))
        eng_months.add(str(_t.get('to_ym') or ''))
    for _h in hist:
        eng_months.add(str(_h.get('anchor_ym') or ''))
        eng_months.add(str(_h.get('judgment_cutoff_ym') or ''))
        _mw = _h.get('match_window') or {}
        eng_months.add(str(_mw.get('start_ym') or ''))
        eng_months.add(str(_mw.get('end_ym') or ''))
        eng_months.update(str(x)[:7]
                          for x in _h.get('aftermath_obs_months') or [])
    for _r2 in (plan.get('asset_moves') or {}).get('rows') or []:
        _w2 = _r2.get('window') or {}
        eng_months.add(str(_w2.get('from') or '')[:7])
        eng_months.add(str(_w2.get('to') or '')[:7])
    eng_months.discard('')
    for r in rm.get('regions') or []:
        for mt in re.finditer(r'\d{4}-\d{2}', str(r.get('from_to') or '')):
            if mt.group(0) not in eng_months:
                bad(f'reader_map.regions[{r.get("region")}].prose_month',
                    f'正文月份 {mt.group(0)} 不在引擎面月份集(序列观测月/'
                    '锚观测月/候选窗/历史窗/资产窗)——正文月份错误'
                    '(2030-07 类虚构月份的拦截位)', contra=True)
    # (12) 月频时序纪律: 月频证据只能支持「同步」时,排序主张(率先/领先/
    #     先变…对同月变动的另一指标)须如实写明「先后未定」——月度观测
    #     分不出同月内先后,超出证据分辨率的排序=对读者的误导。
    _order_kw = re.compile(r'率先|领先|先变|先行|首先|最早|先于|更早于|落后|滞后')
    _tkeys = [(str(t.get('metric_id') or ''), str(t.get('date') or '')[:7])
              for t in turnings]
    _cand_pairs = {(str(c.get('metric_id') or ''), str(c.get('to_ym') or ''))
                   for c in cands}
    for ti, t in enumerate(turnings):
        tid = f'reader_map.turnings[{ti}]'
        own_mid, own_ym = _tkeys[ti]
        blob_order = str(t.get('first_mover') or '') + str(
            t.get('follow_or_diverge') or '')
        if not _order_kw.search(blob_order):
            continue
        cited = {m.group(0) for m in re.finditer(r'\d{4}-\d{2}', blob_order)}
        # 同月他指标变动: 正文引用了本转折月,且该月存在另一指标(≠本
        # 指标)的转折/候选窗终点——两变动落在同一观测月,月频证据只能
        # 支持同步,排序主张须如实写明「先后未定」。
        same_month_peers = {
            mid2 for mid2, ym2 in set(_tkeys) | _cand_pairs
            if mid2 != own_mid and ym2 == own_ym and own_ym in cited}
        if same_month_peers and '先后未定' not in blob_order:
            bad(f'{tid}.ordering_resolution',
                f'排序主张超出证据分辨率: {own_mid}@{own_ym} 与同月变动'
                f'指标({sorted(same_month_peers)})均月频观测,同月内先后'
                '不可分——须如实写明「先后未定」(月频证据只能支持同步时'
                '不得断言谁先谁后)', contra=True)
    # (13) Audit-R22 任务3: 观测月串回贴点值格锚序——地区走位正文里的
    #     「观测 DATE→DATE(→DATE)」串(≥2 个月)须是**同地区某一点值格**
    #     锚观测月序列(12个月前→3个月前→最新一期)的保序子序列。正文
    #     把锚观测月改成「序列在场但锚前不可见」的月份(反例③: 美国 GDP
    #     2025Q2 改 Q3——2025-07 观测在序列 dates 里,月份扫描(11)拦不
    #     住,但其首发 2025-12-23 晚于 2025-11-19 锚,锚格观测=2025-04)
    #     时,此为确定性拦截位。
    _anchor_obs_by_region = {}
    for _c in (plan.get('point_values') or {}).get('cells') or []:
        _seq = []
        for _lbl in ('12个月前', '3个月前', '最新一期'):
            _a = (_c.get('anchors') or {}).get(_lbl) or {}
            if _a.get('status') == 'ok' and _a.get('observation_date'):
                _seq.append(str(_a['observation_date'])[:7])
        if _seq:
            _anchor_obs_by_region.setdefault(_c.get('region'), []).append(_seq)

    def _is_subseq(small, big):
        it = iter(big)
        return all(x in it for x in small)

    for r in rm.get('regions') or []:
        _ft = str(r.get('from_to') or '')
        for mt in re.finditer(
                r'观测\s*(\d{4}-\d{2}(?:-\d{2})?'
                r'(?:\s*→\s*\d{4}-\d{2}(?:-\d{2})?)+)', _ft):
            run = [m[:7] for m in
                   re.findall(r'\d{4}-\d{2}', mt.group(1))]
            if len(set(run)) < 2:
                continue
            seqs = _anchor_obs_by_region.get(r.get('region')) or []
            if not any(_is_subseq(run, sq) for sq in seqs):
                bad(f'reader_map.regions[{r.get("region")}].obs_run',
                    f'观测月串 {"→".join(run)} 不是任何点值格锚观测序'
                    '(12个月前→3个月前→最新一期)的保序子序列——正文引用'
                    '了锚前不可见或不存在的观测月(锚可见性口径;停摆延误'
                    '观测的首发日晚于锚日,不得入锚序叙述)', contra=True)
    # 历史段样本前提(R21 任务4): us_analog 标明+sample_note 样本注记
    # 必填——类比锚定的序列口径与样本独立性是读者判断可比性的前提。
    for hi, h in enumerate(hist):
        hid = f'reader_map.history_periods[{hi}]'
        if not isinstance(h.get('us_analog'), bool):
            bad(f'{hid}.us_analog', '历史段须给 us_analog 布尔(美国指标'
                '类比须标明——三段历史默认锚定美国序列,非美国类比须明示'
                '锚定口径)')
        if not str(h.get('sample_note') or '').strip():
            bad(f'{hid}.sample_note', '历史段须给 sample_note 样本注记'
                '(样本独立性/与当前研究窗重叠/最新修订口径一类前提——'
                '读者报告须显示样本注记)')
    # (14) Audit-R23 任务3: 地区走位正文里的裸季度词元(2025Q2 一类)须为
    #     该地区 GDP 点值格的锚观测季——非锚观测季(观测在序列但首发晚
    #     于锚日、或不存在)不得充当对照端点。月份串已由(13)拦截;括号
    #     内裸季度词元是另一窜写位(反例: 2025Q2 改 2025Q3——Q3 首发
    #     2025-12-23 晚于 2025-11-19 锚,锚格观测季=Q2)。
    _gdp_anchor_quarters = {}
    for _c in (plan.get('point_values') or {}).get('cells') or []:
        if 'GDP' not in str(_c.get('metric_id') or '').upper():
            continue
        for _lbl in ('12个月前', '3个月前', '最新一期'):
            _a = (_c.get('anchors') or {}).get(_lbl) or {}
            _od = str(_a.get('observation_date') or '')
            if _a.get('status') == 'ok' and len(_od) >= 7:
                _gdp_anchor_quarters.setdefault(
                    _c.get('region'), set()).add(
                    '%04dQ%d' % (int(_od[:4]),
                                 (int(_od[5:7]) - 1) // 3 + 1))
    for r in rm.get('regions') or []:
        _ft = str(r.get('from_to') or '')
        _qs_ok = _gdp_anchor_quarters.get(r.get('region')) or set()
        for _qm in re.finditer(r'20\d{2}Q[1-4]', _ft):
            _ctx = _ft[max(0, _qm.start() - 30):_qm.end() + 30]
            if 'GDP' not in _ctx.upper() and '国内生产总值' not in _ctx:
                continue
            if _qs_ok and _qm.group(0) not in _qs_ok:
                bad(f'reader_map.regions[{r.get("region")}].quarter_token',
                    f'季度词元 {_qm.group(0)} 不是该地区 GDP 点值格锚'
                    f'观测季(锚观测季={sorted(_qs_ok)})——正文以锚前未'
                    '发布或不存在的季度充当对照端点(锚可见性口径;发布'
                    '实录首发晚于锚日的季度不得入对照叙述)', contra=True)
    # (15) Audit-R23 任务3 + Audit-R24 任务3: 一句总判断里的基点/百分点
    #     主张按引擎面复算——年度主张对年度窗分解(chg_bp_12m)逐位对账
    #     (符号+显示精度);方向词(上行/下行)与符号矛盾即 CONTRADICTED。
    #     读者看到的那句话里的利率数字必须可对引擎面核(反例: 名义+97bp
    #     被改 −97bp)。R24 扩展见块内注: 分量归属核(对调拒绝)/日本
    #     序列池外复算/pp↔bp 双单位等价。
    _hl = str(rm.get('headline_conclusion') or '')
    _jp_ctx24 = bool(re.search(r'日本|日债|JGB', _hl))
    if (trio.get('status') == 'ok' and
            re.search(r'美债|名义|实际|盈亏平衡|十年期|利率'
                      r'|UST_10Y|TIPS_10Y|BEI_10Y', _hl)) or \
            _jp_ctx24:
        _annual_claim = bool(re.search(r'年度|12个月|十二个月|一年', _hl))
        _bp_pool = set()
        for _src in (('chg_bp_12m',) if _annual_claim
                     else ('chg_bp_12m', 'chg_bp')):
            for _v in (trio.get(_src) or {}).values():
                if isinstance(_v, (int, float)):
                    _bp_pool.add(float(_v))
        # Audit-R24 任务3: ①归属核——上下文点名「名义/实际/盈亏平衡」时按
        #   分量逐一对账(池成员资格不够: 名义+104bp/实际+97bp 对调两值
        #   都在三利率池内,池核放行,归属核拒绝);②池外利率序列——上下文
        #   点名「日本/日债/JGB」时按引擎 JGB/政策利率序列同窗复算
        #   (三利率池只住美债;日本+67bp 不在池≠错);③双单位等价——
        #   +67bp 与 +0.67个百分点 等值对账(精确 pp↔bp 对;无归属的
        #   百分点主张维持不判=旧档复放不动)。
        # Audit-R25 任务3: ①单位三写法——bp/基点/个基点 同为基点族(不乘
        #   100;个百分点仍=精确 pp↔bp 对);②归属别名面扩容——中文指标名
        #   (十年期美债→名义/十年期TIPS→实际/盈亏平衡通胀)与代码名
        #   (UST_10Y/TIPS_10Y/BEI_10Y)入 _ATTR24;就近取胜规则保证
        #   「十年期美债实际」按更近的『实际』归 TIPS。对调拒绝随写法
        #   扩展: 任何写法下 名义+97↔实际+104 互换均被分量对账拒绝。
        _ATTR24 = (('名义', 'UST_10Y'), ('实际', 'TIPS_10Y'),
                   ('盈亏平衡', 'BEI_10Y'),
                   ('UST_10Y', 'UST_10Y'), ('TIPS_10Y', 'TIPS_10Y'),
                   ('BEI_10Y', 'BEI_10Y'),
                   ('十年期美债', 'UST_10Y'), ('10年期美债', 'UST_10Y'),
                   ('美国十年期国债', 'UST_10Y'),
                   ('十年期TIPS', 'TIPS_10Y'), ('通胀保值', 'TIPS_10Y'),
                   ('盈亏平衡通胀', 'BEI_10Y'))
        _ATTRLBL24 = {'UST_10Y': '名义(UST_10Y)', 'TIPS_10Y': '实际(TIPS_10Y)',
                      'BEI_10Y': '盈亏平衡(BEI_10Y)'}

        def _jp_chg_bp24():
            import bisect as _bi
            import datetime as _dtm
            for _jm in ('JGB10Y', 'JGB5Y', 'JGB2Y', 'JP_POLICY_RATE'):
                _js = (face.get('series_store') or {}).get(_jm)
                if not _js or not _js.get('dates'):
                    continue
                _m = {d: v for d, v in zip(_js['dates'], _js['values'])
                      if v is not None}
                if len(_m) < 2:
                    continue
                _d1 = max(_m)
                _tgt = (_dtm.date.fromisoformat(_d1)
                        - _dtm.timedelta(
                            days=365 if _annual_claim else 30)).isoformat()
                _cand = [d for d in _m if d <= _tgt] or \
                    sorted(_m)[:-1]
                _d0 = min(_cand, key=lambda d: abs(
                    (_dtm.date.fromisoformat(d)
                     - _dtm.date.fromisoformat(_tgt)).days))
                return (round((float(_m[_d1]) - float(_m[_d0])) * 100.0, 2),
                        _jm, _d0, _d1)
            return None
        for _bm in re.finditer(
                r'([+−\-±]?)\s*(\d+(?:\.\d+)?)\s*'
                r'(bp|个百分点|个基点|基点)', _hl):
            _claimed = (-1.0 if _bm.group(1) in ('-', '−')
                        else 1.0) * float(_bm.group(2))
            _unit = _bm.group(3)
            if _unit == '个百分点':
                _claimed = _claimed * 100.0     # 精确 pp↔bp 对(67bp≡0.67pp)
            # R25: 基点/个基点 与 bp 同族同值(×1),无换算
            # R25: 无显式符号时前置方向词定号——「下行7个基点」的符号
            # 语义由方向词承担,缺号按正值解读会把方向一致的表述误判
            # 对账不符;显式符号(+7/−7)仍以符号为准(与方向词矛盾由
            # 下方 bp_direction 拦)。
            if _bm.group(1) == '':
                _w_pre = _hl[max(0, _bm.start() - 12):_bm.start()]
                if re.search(r'下行|下降|回落|走低', _w_pre):
                    _claimed = -_claimed
            _ctx = _hl[max(0, _bm.start() - 16):_bm.start()]
            _hits = [(_ctx.rfind(_w), _mid) for _w, _mid in _ATTR24]
            _hits += [(_ctx.rfind(_w), 'JP') for _w in
                      ('日本', '日债', 'JGB', '日国债')]
            _hits = [h for h in _hits if h[0] >= 0]
            _tag = max(_hits)[1] if _hits else None    # 最靠近数字者胜
            _num_ok = False
            if _tag == 'JP':
                _jc = _jp_chg_bp24()
                if _jc is None:
                    bad('reader_map.headline_conclusion.bp_attributed',
                        f'利率主张 {_bm.group(0).strip()} 归属日本利率,但'
                        '引擎面无 JGB10Y/JGB5Y/JGB2Y/JP_POLICY_RATE 序列'
                        '可对账——不可核的利率数字不入总判断(缺序列须写明'
                        '缺席,不留裸数字)', contra=True)
                    continue
                _jbp, _jm, _jd0, _jd1 = _jc
                _num_ok = abs(_claimed - _jbp) <= 1.0
                if not _num_ok:
                    bad('reader_map.headline_conclusion.bp_attributed',
                        f'利率主张 {_bm.group(0).strip()} 与引擎 {_jm} 同窗'
                        f'复算不符({_jd0}→{_jd1} 复算 {_jbp:+g}bp;'
                        + ('年度窗(近365日)' if _annual_claim
                           else '近30日窗')
                        + ')——池外利率序列同窗对账(+67bp≡+0.67个百分点'
                        '双单位等值,含符号,容差 1bp)', contra=True)
                    continue
            elif _tag is not None:
                _av = None
                for _src in (('chg_bp_12m',) if _annual_claim
                             else ('chg_bp', 'chg_bp_12m')):
                    _v = (trio.get(_src) or {}).get(_tag)
                    if isinstance(_v, (int, float)):
                        _av = float(_v)
                        break
                _num_ok = _av is not None and abs(_claimed - _av) <= 1.0
                if not _num_ok:
                    bad('reader_map.headline_conclusion.bp_attributed',
                        f'基点主张 {_bm.group(0).strip()} 归属'
                        f'{_ATTRLBL24.get(_tag, _tag)}与引擎该分量不符'
                        f'({_ATTRLBL24.get(_tag, _tag)}='
                        f'{_av if _av is not None else "该窗无值"};'
                        f'{"年度窗" if _annual_claim else "月度/年度窗"})'
                        '——分量归属后逐一对账: 池内另一分量的值(名义/实际'
                        '/盈亏平衡对调)不蒙混,容差 1bp', contra=True)
                    continue
            else:
                if _unit == '个百分点':
                    continue    # 无归属的百分点主张维持不判(旧档复放不动)
                _num_ok = any(abs(_claimed - _v) <= 1.0 for _v in _bp_pool)
                if not _num_ok:
                    bad('reader_map.headline_conclusion.bp',
                        f'基点主张 {_bm.group(0).strip()} 与引擎三利率分解'
                        f'不符({"年度窗" if _annual_claim else "年度/月度窗"}'
                        f'可对值={sorted(_bp_pool)})——读者看到的那句话里的'
                        '利率分解数字必须与引擎同窗复算一致(含符号与显示'
                        '精度,容差 1bp)', contra=True)
                    continue
            _w = _hl[max(0, _bm.start() - 12):_bm.start()]
            if (re.search(r'下行|下降|回落|走低', _w) and _claimed > 0) or \
                    (re.search(r'上行|上升|走高|抬升', _w) and _claimed < 0):
                bad('reader_map.headline_conclusion.bp_direction',
                    f'方向词与基点符号矛盾({_bm.group(0).strip()} 前文'
                    f'={_w.strip()!r})——方向、单位、符号须与引擎面一致',
                    contra=True)
    # (16) Audit-R23 任务2: 历史段「当时可知」信息截止纪律(as_of 泄漏)
    #     ——相似/差异/同步性叙述所引数字须为判断截止月末前已可知的
    #     观测;引用「观测月=截止月但首发晚于截止」的值(如中国 PPI
    #     六月值于七月上旬才发布、日本 CPI 次月 20 日)即信息截止泄漏,
    #     晚于截止日的数字须移入事后段叙述。新代码面(plan.asof_
    #     discipline 标记)起生效;旧档无标记不追溯(原文复放必须通过)。
    if str(plan.get('asof_discipline') or ''):
        import research_map_planner as _rmp5
        for hi, h in enumerate(hist):
            _cym = str(h.get('judgment_cutoff_ym')
                       or h.get('anchor_ym') or '')
            if len(_cym) != 7:
                continue
            _prose = ' '.join(str(h.get(k) or '') for k in
                              ('similarity', 'difference',
                               'other_regions_sync'))
            if not _prose.strip():
                continue
            try:
                _aop = (_rmp5.history_asof_face([h], report)
                        .get('periods') or [{}])[0]
            except Exception:
                continue
            _known = {r2.get('metric_id'): r2
                      for r2 in _aop.get('known') or []}
            # Audit-R27 任务2: 值泄漏判据自「截止月观测晚于截止公布」扩到
            # **全部事后数值行**(截止后 12 月窗内异常延误行的值在截止时
            # 同样不可知——正文引之即泄漏);政策事件行(阶梯变更值,
            # value_from→value)不入值对账,由日期写回判据与事后段纪律
            # 约束。
            _after = {}
            for r2 in _aop.get('aftermath') or []:
                if r2.get('kind') != 'policy_event' \
                        and isinstance(r2.get('value'), (int, float)):
                    # 首行(截止月观测晚于截止公布——最常见泄漏位)优先,
                    # 其余延误行不覆盖同指标代表行。
                    _after.setdefault(r2.get('metric_id'), r2)
            # Audit-R27 任务2: **事后日期写回「当时」段拒绝**——similarity/
            # difference/other_regions_sync 三字段属当时叙述(逐项只用
            # 截止日前已公布的证据),内文显式日期(YYYY-MM-DD/YYYY-MM/
            # YYYY年M月)严格晚于判断截止月末=事后信息写回当时段,拒绝;
            # 该类日期只能出现在事后段(ex_post)叙述。
            for _dm in re.finditer(
                    r'(\d{4})-(\d{1,2})(?:-(\d{1,2}))?|(\d{4})年(\d{1,2})月',
                    _prose):
                _g = _dm.groups()
                if _g[3]:
                    _y, _mo, _dd = int(_g[3]), int(_g[4]), None
                else:
                    _y, _mo, _dd = int(_g[0]), int(_g[1]), \
                        (int(_g[2]) if _g[2] else None)
                if not (1 <= _mo <= 12):
                    continue
                _d_iso = '%04d-%02d-%02d' % (
                    _y, _mo, _dd if _dd else 1)
                if _d_iso > str(_aop.get('cutoff_end') or '9999-12-31'):
                    bad(f'reader_map.history_periods[{hi}]'
                        '.expost_date_written_back',
                        f'当时叙述含事后日期 {_dm.group(0)}(晚于判断截止'
                        f'月末 {_aop.get("cutoff_end")})——相似/差异/同步'
                        '性逐项只用截止日前已公布的证据,晚于截止的观察'
                        '须移入事后段(ex_post),不得写回「当时」段'
                        '(Audit-R27 任务2)',
                        contra=True)
            # Audit-R28 任务3: **相对日期的事后事实拒绝写回当时段**——
            # 「随后/此后/接下来 N 个月…」一类相对事后引用在 similarity/
            # difference/other_regions_sync 三字段=无绝对日期锚的事后
            # 事实(R27 拦显式事后日期后,相对词形是无日期版的同一泄漏:
            # 读者无法核对该"N 个月"自何处起算)。事后走向一律移入
            # ex_post 段并按锚月末→锚+N 月末口径携带绝对窗口。
            for _rm28 in re.finditer(
                    r'(随后|此后|接下来|之后的)[^。;；\n]{0,8}?'
                    r'(\d+|[一两二三四五六七八九十]{1,3})\s*个月',
                    _prose):
                bad(f'reader_map.history_periods[{hi}]'
                    '.relative_expost_in_asof_segment',
                    f'当时叙述含相对事后引用「{_rm28.group(0)}」——相似/'
                    '差异/同步性逐项只用截止日前已公布的证据;事后走向'
                    '属 ex_post 段(锚月末→锚+N 月末绝对窗口口径),不得'
                    '以无绝对日期的相对词形写回「当时」段'
                    '(Audit-R28 任务3)',
                    contra=True)
            # Audit-R28 任务3: ex_post 段相对引用**必须携带绝对日期锚**
            # ——「随后 N 个月」在事后段合法,但该句须点名绝对年月
            # (锚 YYYY-MM 或窗口端点),否则窗口不可核(哪年哪月起算
            # 由读者猜=复测不可重复)。
            for _ek28, _et28 in (h.get('ex_post') or {}).items():
                _et28 = str(_et28 or '')
                if not _et28.strip():
                    continue
                for _rm28b in re.finditer(
                        r'(随后|此后|接下来|之后的)[^。;；\n]{0,8}?'
                        r'(\d+|[一两二三四五六七八九十]{1,3})\s*个月',
                        _et28):
                    _sent28 = _et28[max(0, _rm28b.start() - 60):
                                    _rm28b.end() + 60]
                    if not re.search(r'\d{4}[-年]\s?\d{1,2}', _sent28):
                        bad(f'reader_map.history_periods[{hi}]'
                            '.ex_post.relative_without_absolute_anchor',
                            f'ex_post[{_ek28}] 含相对窗口「{_rm28b.group(0)}」'
                            '而句内无绝对年月锚——事后段相对引用必须点名'
                            '绝对日期(锚 YYYY-MM 或窗口端点),窗口自何'
                            '处起算须可核(Audit-R28 任务3)',
                            contra=True)
                        break
            for _mid, _aft in _after.items():
                _kn = _known.get(_mid)
                _vis_v = (_kn or {}).get('value')
                if not isinstance(_vis_v, (int, float)):
                    continue
                _aliases = next((al for m2, _l2, al in
                                 _rmp5._AOF_KEY_METRICS if m2 == _mid),
                                [_mid])
                for _al in _aliases:
                    for _am in re.finditer(re.escape(_al), _prose):
                        _seg = _prose[_am.end():_am.end() + 40]
                        for _nm in re.finditer(r'-?\d+(?:\.\d+)?', _seg):
                            try:
                                _v = float(_nm.group(0))
                            except ValueError:
                                continue
                            if _v >= 1900 or _v <= -1900:
                                continue
                            if abs(_v - float(_aft.get('value'))) <= 0.06 \
                                    and abs(_v - _vis_v) > 0.06:
                                bad(f'reader_map.history_periods[{hi}]'
                                    '.as_of_leak',
                                    f'{_al} 引用值 {_v:g} =截止月观测 '
                                    f'{_aft.get("value"):g}(首发 '
                                f'{_aft.get("visible_from")},晚于截止 '
                                f'{_aop.get("cutoff_end")})——当时可知值'
                                f'={_vis_v:g}(观测月 '
                                f'{(_kn or {}).get("obs_month")},首发 '
                                f'{(_kn or {}).get("visible_from")});'
                                '晚于截止日才公布的数字须移入事后段,'
                                '不得充当当时可知(Audit-R23 任务2)',
                                contra=True)
    # (17) Audit-R24 任务4: 并项补选交还判断席——同轮并项后不足三项时
    #     引擎补选的独立转折,判断席须在 reader_map.turning_supplement
    #     逐项写明 谁先变/何时(从多少到多少=候选面已给,席位须引)/哪些
    #     经济体跟进或背离;月频序列无法判断先后须写明分辨率界限,缺
    #     跨国证据须写明缺哪项。新代码面标记(turning_supplement_
    #     discipline)起生效;旧档无标记不追溯(原文复放必须通过)。
    #     并项/补选集合与渲染面同源(turning_merge_and_picks 纯函数)。
    if str(plan.get('turning_supplement_discipline') or ''):
        import research_map_planner as _rmp6
        _eps17, _picks17 = _rmp6.turning_merge_and_picks(
            rm.get('turnings') or [],
            (plan.get('turning_candidates') or {}).get('candidates')
            or [])
        _supp17 = {(str(s.get('metric_id')), str(s.get('to_ym'))): s
                   for s in (rm.get('turning_supplement') or [])
                   if isinstance(s, dict)}
        for _c17 in _picks17:
            _k17 = (str(_c17.get('metric_id')), str(_c17.get('to_ym')))
            _sn17 = _supp17.get(_k17) or {}
            _fm17 = str(_sn17.get('first_mover') or '').strip()
            _fd17 = str(_sn17.get('follow_or_diverge') or '').strip()
            _res17 = str(_sn17.get('resolution_note') or '').strip()
            _gap17 = str(_sn17.get('evidence_gap') or '').strip()
            _honest17 = bool(
                (_res17 and ('分辨率' in _res17 or '月频' in _res17))
                or (_gap17 and ('缺' in _gap17 or '证据' in _gap17)))
            if not _fm17 and not _honest17:
                bad('reader_map.turning_supplement',
                    f'引擎补选转折 {_k17[0]}@{_k17[1]} 未交还判断席——'
                    '补选项须在 turning_supplement 逐项写明 谁先变/何时/'
                    '从多少到多少(候选面已给)/哪些经济体跟进或背离;'
                    '月频无法判断先后写明分辨率,缺跨国证据写明缺哪项'
                    '(Audit-R24 任务4)')
                continue
            if _fm17 and not _fd17 and not _honest17:
                bad('reader_map.turning_supplement',
                    f'补选转折 {_k17[0]}@{_k17[1]} 写了谁先变但缺'
                    '「跟进或背离」——哪些经济体跟进/背离须逐项给出;'
                    '缺跨国证据就写明缺哪项,不得留空')
                continue
            ok('reader_map.turning_supplement',
               f'补选转折 {_k17[0]}@{_k17[1]} 已交还判断席'
               f'(first_mover={_fm17[:24] if _fm17 else "(分辨率/证据说明)"})')
    # (18) Audit-R25 任务3: 首页/转折表/传导链 先后顺序与因果证据一致性。
    #     三个确定性子面: ①日期次序主张自洽+跨面不矛盾——文本中两日期
    #     之间的「早于/先于/晚于」主张须与日期事实一致,同一对日期在
    #     任何两面主张相反次序即 CONTRADICTED;②传导链证据绑定——每条
    #     链至少一环的 distinguishing_metric 须为引擎可观测指标(计划
    #     指标∪上下文指标∪快照序列),纯文本因果链不得入传导面;
    #     ③转折表指标同源——turnings[].metric_id 须出自计划指标或引擎
    #     转折候选面。新代码面标记(cross_face_consistency)起生效;
    #     旧档无标记不追溯(原文复放必须通过)。
    if str(plan.get('cross_face_consistency') or '') == 'r25':
        _hl18 = str(rm.get('headline_conclusion') or '')
        _DATE18 = re.compile(r'\d{4}-\d{2}(?:-\d{2})?')
        _LT18 = re.compile(r'早于|先于')
        _GT18 = re.compile(r'晚于')

        def _cmp18(a, b):
            # 同精度或月精度可判: 返回 -1/1;同月混合精度=不可判(None)
            if a[:7] != b[:7]:
                return -1 if a < b else 1
            if len(a) == len(b):
                return -1 if a < b else (1 if a > b else 0)
            return None

        _faces18 = [('首页(headline)', [_hl18])]
        for _ti, _t in enumerate(rm.get('turnings') or []):
            _faces18.append((f'转折表[{_t.get("metric_id")}]',
                             [str(_t.get(k) or '') for k in
                              ('first_mover', 'follow_or_diverge',
                               'narrative')]))
        for _s in rm.get('turning_supplement') or []:
            _faces18.append((f'转折补选[{_s.get("metric_id")}]',
                             [str(_s.get(k) or '') for k in
                              ('first_mover', 'follow_or_diverge')]))
        for _ch18 in rm.get('transmission') or []:
            for _li, _lk18 in enumerate(_ch18.get('links') or []):
                _faces18.append(
                    (f'传导链[{_ch18.get("chain_id") or _ch18.get("title")}]'
                     f'第{_li + 1}环',
                     [str(_lk18.get(k) or '') for k in
                      ('observed_fact', 'causal_hypothesis',
                       'competing_explanation')]))
        _claims18 = {}     # frozenset{d1,d2} -> {'lt': d, 'gt': d} 主张面
        for _fname, _texts in _faces18:
            for _txt in _texts:
                _ms = list(_DATE18.finditer(_txt or ''))
                for _a, _b in zip(_ms, _ms[1:]):
                    _mid_txt = _txt[_a.end():_b.start()]
                    if len(_mid_txt) > 40:
                        continue
                    _rel = ('lt' if _LT18.search(_mid_txt)
                            else 'gt' if _GT18.search(_mid_txt) else None)
                    if _rel is None:
                        continue
                    _da, _db = _a.group(0), _b.group(0)
                    _c = _cmp18(_da, _db)
                    if _c is None:
                        continue
                    _want = -1 if _rel == 'lt' else 1
                    if _c != _want:
                        bad('reader_map.cross_face_consistency.date_order',
                            f'{_fname}: 「{_da}{"早于" if _rel == "lt" else "晚于"}'
                            f'{_db}」与日期事实矛盾——先后顺序表述必须与'
                            '日期事实一致(Audit-R25 任务3)', contra=True)
                    _key = frozenset((_da, _db))
                    _claims18.setdefault(_key, {}).setdefault(_rel, set()).add(
                        _fname)
        for _key, _dirs in _claims18.items():
            if 'lt' in _dirs and 'gt' in _dirs:
                _d = sorted(_key)
                bad('reader_map.cross_face_consistency.date_order',
                    f'同一对日期 {_d[0]}/{_d[1]} 的先后次序被不同面主张相反'
                    f'(早于={sorted(_dirs["lt"])};晚于={sorted(_dirs["gt"])})'
                    '——首页/转折表/传导链对先后顺序的表述必须一致'
                    '(Audit-R25 任务3)', contra=True)
            else:
                _d = sorted(_key)
                ok('reader_map.cross_face_consistency.date_order',
                   f'日期次序主张一致: {_d[0]}<{_d[1]}'
                   f'({"早于" if "lt" in _dirs else "晚于"},'
                   f'{len(next(iter(_dirs.values())))} 处)')
        _known18 = set(plan.get('metrics') or []) | \
            set(plan.get('context_metrics') or [])
        for _c18 in (plan.get('turning_candidates') or {}).get(
                'candidates') or []:
            if _c18.get('metric_id'):
                _known18.add(_c18['metric_id'])
        _store18 = set((face.get('series_store') or {}).keys())
        for _ch18 in rm.get('transmission') or []:
            _cid = _ch18.get('chain_id') or _ch18.get('title')
            _bound = [str(_lk18.get('distinguishing_metric') or '')
                      for _lk18 in _ch18.get('links') or []]
            _okm = [m for m in _bound if m and (m in _known18 or m in _store18)]
            if not _okm:
                bad('reader_map.cross_face_consistency.chain_evidence',
                    f'传导链[{_cid}] 全部环节的区分指标无一是引擎可观测'
                    '指标(计划∪上下文∪快照序列)——因果证据纯文本化,'
                    '传导面须至少一环绑定引擎可对账指标(Audit-R25 任务3)')
            else:
                ok('reader_map.cross_face_consistency.chain_evidence',
                   f'传导链[{_cid}] 区分指标绑定 {len(_okm)}/'
                   f'{len(_ch18.get("links") or [])} 环')
        for _t in rm.get('turnings') or []:
            _tm = str(_t.get('metric_id') or '')
            if _tm and _tm not in _known18 and _tm not in _store18:
                bad('reader_map.cross_face_consistency.turning_source',
                    f'转折表指标 {_tm} 不在计划指标∪转折候选面∪快照序列'
                    '——转折表须与引擎候选面同源(Audit-R25 任务3)')
        if rm.get('turnings'):
            ok('reader_map.cross_face_consistency.turning_source',
               f'转折表 {len(rm["turnings"])} 项指标与计划/候选面同源')
    # Audit-R33 任务5: 问到预期差——席位预期差判断回声契约(五面契约之后)
    _eg_p = plan.get('expectations_gap')
    if isinstance(_eg_p, dict) and _eg_p.get('asked'):
        out.extend(_expectations_gap_checks(judgment, face, report, plan))
    return out


# ── Audit-R33 任务3: 原问直答型问句 reader_map 分面回声契约 ─────────────

_PQ_SCHEMA = 'r33-policy-question'
# 地图五面(及补充面)键——原问直答型判定不得写(两族契约互斥)
_PQ_FIVE_FACE_KEYS = ('regions', 'transmission', 'turnings',
                      'turning_supplement', 'history_periods',
                      'history_zero_case_note', 'asset_returns_echo',
                      'rates_decomposition')
# 自由文字数字: 阿拉伯数字(字母/下划线/小数点紧随其前者不算: L3/E1/v1.0)
_PQ_NUM_TOKEN = re.compile(r'(?<![A-Za-z_0-9.])\d+(?:\.\d+)?')
_PQ_CN_DIGITS = {'零': 0, '〇': 0, '一': 1, '二': 2, '两': 2, '三': 3,
                 '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}
_PQ_CN_DECIMAL = re.compile(r'[零〇一二两三四五六七八九]点[零〇一二三四五六七八九]+')
_PQ_CN_PERCENT = re.compile(r'百分之[一二两三四五六七八九十]+(?!\s*点)')
_PQ_CN_INT_UNIT = re.compile(
    r'[一二两三四五六七八九十]+(?=\s*(?:个基点|个百分点|个月|天))')
_PQ_CN_YEAR = re.compile(r'[零〇一二三四五六七八九]{4}\s*年')
# 值单位后缀: 紧随其后的数字按值核(不得借日期年/月/日分量放行)
_PQ_VALUE_SUFFIX = re.compile(r'\s*(?:[bB][pP]|个百分点|pp|基点|%)')


def _pq_cn_int(s):
    """中文整数(十/百合成;「十五」=15、「二十四」=24、「一百零五」=105)。"""
    total, cur = 0, 0
    for c in s.replace('〇', '零').replace('两', '二'):
        if c == '十':
            total += (cur or 1) * 10
            cur = 0
        elif c == '百':
            total += (cur or 1) * 100
            cur = 0
        else:
            cur = _PQ_CN_DIGITS.get(c, 0)
    return total + cur


def _pq_cn_number(s):
    if '点' in s:
        a, _, b = s.partition('点')
        frac = ''.join(str(_PQ_CN_DIGITS.get(c, 0)) for c in b)
        return float('%d.%s' % (_pq_cn_int(a) if a else 0, frac))
    return float(_pq_cn_int(s))


def _pq_engine_numbers(blk):
    """引擎分面块内全部数值(含绝对值形)+日期的年/月/日分量。"""
    nums, dates = set(), set()

    def add_num(v):
        if isinstance(v, bool) or not isinstance(v, (int, float)) \
                or v != v or abs(v) > 1e15:
            return
        nums.add(float(v))
        nums.add(abs(float(v)))

    def walk(o):
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
        elif isinstance(o, (int, float)):
            add_num(o)
        elif isinstance(o, str):
            m = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', o[:10])
            if m:
                dates.update((m.group(1), m.group(2), m.group(3),
                              str(int(m.group(2))), str(int(m.group(3)))))

    walk(blk)
    return nums, dates


def _pq_num_in(x, nums):
    return x is not None and any(abs(x - n) < 1e-9 for n in nums)


def _pq_unbound_tokens(text, nums, dates):
    """自由文字里与引擎面不对应的数字(阿拉伯数字/中文小数/百分之X/带量词
    中文整数);年份(四位中文数字+年)不算。空串=无。"""
    if text is None or not str(text).strip():
        return []
    t = _PQ_CN_YEAR.sub('', str(text))
    out = []
    for m in _PQ_NUM_TOKEN.finditer(t):
        tok = m.group(0)
        if tok in dates and not _PQ_VALUE_SUFFIX.match(t, m.end()):
            continue        # 日期分量(年/月/日);带值单位者按值核
        try:
            x = float(tok)
        except ValueError:
            x = None
        if not _pq_num_in(x, nums):
            out.append(tok)
    for m in _PQ_CN_DECIMAL.finditer(t):
        if not _pq_num_in(_pq_cn_number(m.group(0)), nums):
            out.append(m.group(0))
    # 带量词整数扫描前掩掉已识别的中文小数段——否则「零点五五个百分
    # 点」的尾「五五个百分点」会被整数规则再吃一次(55≠引擎面,误报)
    t = _PQ_CN_DECIMAL.sub(lambda m: '·' * len(m.group(0)), t)
    for m in _PQ_CN_PERCENT.finditer(t):
        if not _pq_num_in(_pq_cn_number(m.group(0)[3:]), nums):
            out.append(m.group(0))
    for m in _PQ_CN_INT_UNIT.finditer(t):
        if not _pq_num_in(_pq_cn_number(m.group(0)), nums):
            out.append(m.group(0))
    return out


def _policy_question_checks(judgment, face, report, plan):
    """原问直答型判定的 reader_map 结构化回声契约(确定性逐位核对)。

    回声(reader_map.policy_question)须逐字回声引擎面
    research_plan.policy_question: 值/日期/状态/答案逐位一致——相左=
    CONTRADICTED;缺席/多出/引用不可解析=NOT_VERIFIED;回声自由文字
    (总判断/注记)里的数字须与引擎面数字对应(否则 NOT_VERIFIED);
    地图五面键不得出现。L3/L4 仍走既有客观事实/统计结论/六查。"""
    out = []

    def ok(item, note):
        out.append({'item': item, 'claim_type': 'reader_map',
                    'status': 'VERIFIED', 'note': note, 'evidence_refs': []})

    def bad(item, note, contra=False):
        out.append({'item': item, 'claim_type': 'reader_map',
                    'status': 'CONTRADICTED' if contra else 'NOT_VERIFIED',
                    'note': note, 'evidence_refs': []})

    rm = (judgment or {}).get('reader_map')
    if not isinstance(rm, dict):
        bad('reader_map', '原问直答型判定须含 reader_map 顶层对象'
            '(一句总判断+结构化回声)')
        return out
    head = str(rm.get('headline_conclusion') or '').strip()
    if head:
        ok('reader_map.headline_conclusion', '非空')
    else:
        bad('reader_map.headline_conclusion', '一句总判断为空或 None')
    stray = [k for k in _PQ_FIVE_FACE_KEYS if k in rm]
    if stray:
        bad('reader_map', '原问直答型判定不得写地图五面键'
            f'(分面契约不核五面): {stray}')
    blk = plan.get('policy_question')
    if not isinstance(blk, dict) or blk.get('schema') != _PQ_SCHEMA:
        bad('research_plan.policy_question',
            '引擎分面块缺席/损坏——无可回声面')
        return out
    echo = rm.get('policy_question')
    if not isinstance(echo, dict):
        bad('reader_map.policy_question',
            '结构化回声缺席(须逐字回声引擎面 research_plan.policy_question)')
        return out
    index = {e.get('ref'): e for e in (report.get('evidence_index') or [])}
    qt = blk.get('question_time') or {}
    nums, dates = _pq_engine_numbers(blk)

    def field(item, seat_row, eng_row, key, ekey=None, numeric=False):
        """回声字段(key=回声键,ekey=引擎键,缺省同名): 引擎无值→回声
        须同空(给出=虚构 CONTRADICTED);引擎有值→回声缺席/None=
        NOT_VERIFIED,不等=CONTRADICTED,相等=VERIFIED。"""
        ev = eng_row.get(ekey or key)
        sv = seat_row.get(key)
        if ev is None:
            if sv is None:
                ok(item, '空=空')
            else:
                bad(item, f'引擎面无值而回声给出 {sv!r}(虚构)', contra=True)
            return
        if sv is None:
            bad(item, f'回声缺字段/为空(引擎 {ev!r})')
            return
        if numeric:
            try:
                same = abs(float(sv) - float(ev)) < 1e-9
            except (TypeError, ValueError):
                same = False
        else:
            same = (sv == ev)
        if same:
            ok(item, f'{sv!r} 一致')
        else:
            bad(item, f'回声 {sv!r} ≠ 引擎面 {ev!r}', contra=True)

    def refs_check(item, sr, er):
        refs = sr.get('evidence_refs')
        if (not isinstance(refs, list)
                or not all(isinstance(x, str) for x in refs)):
            bad(item + '.evidence_refs', '引用缺席/非字符串数组')
            return
        if not (er.get('evidence_refs') or []):
            # 引擎行无实据(读数/目标/实录缺席=数据不可得): 回声须为空
            # 引用——引擎行无实据而回声给出引用=无中生有
            if refs:
                bad(item + '.evidence_refs',
                    '引擎行无实据而回声给出引用(虚构)', contra=True)
            else:
                ok(item + '.evidence_refs',
                   '引擎行无实据(数据不可得),回声空引用一致')
            return
        if not refs:
            bad(item + '.evidence_refs', '引用缺席/非字符串数组')
            return
        unres = [x for x in refs if x not in index]
        if unres:
            bad(item + '.evidence_refs',
                f'引用不可解析(不在 evidence_index): {unres[:3]}')
            return
        er_refs = set(er.get('evidence_refs') or [])
        if er_refs and not (set(refs) & er_refs):
            bad(item + '.evidence_refs',
                '回声引用未落在该行引擎实据上(须含 '
                f'{sorted(er_refs)[:3]} 之一)')
            return
        ok(item + '.evidence_refs', f'{len(refs)} 引用可解析且落在引擎行')

    def keyed(rows, keyfn, name):
        if not isinstance(rows, list):
            bad(name, '须为数组')
            return None
        m = {}
        for r in rows:
            if not isinstance(r, dict):
                bad(name, '条目须为对象')
                return None
            k = keyfn(r)
            if k in m:
                bad(f'{name}[{k}]', '重复条目')
            m[k] = r
        return m

    def cover(name, eng, got):
        missing = sorted(str(x) for x in set(eng) - set(got))
        extra = sorted(str(x) for x in set(got) - set(eng))
        if missing or extra:
            bad(name, f'回声不齐: 缺 {missing}; 多出 {extra}')
            return False
        ok(name, f'{len(eng)} 行齐')
        return True

    # research_time
    rt = echo.get('research_time')
    if not isinstance(rt, dict):
        bad('reader_map.policy_question.research_time',
            'research_time 缺席(须回声 {as_of, research_month})')
    else:
        field('reader_map.policy_question.research_time.as_of',
              rt, {'as_of': blk.get('as_of')}, 'as_of')
        field('reader_map.policy_question.research_time.research_month',
              rt, {'research_month': qt.get('research_month')},
              'research_month')

    # official_targets
    eng = {r.get('region'): r
           for r in ((blk.get('policy_targets') or {}).get('rows') or [])
           if isinstance(r, dict)}
    gm = keyed(echo.get('official_targets'), lambda r: r.get('region'),
               'reader_map.policy_question.official_targets')
    if gm is not None and cover(
            'reader_map.policy_question.official_targets', eng, gm):
        for reg, er in eng.items():
            sr = gm.get(reg)
            if sr is None:
                continue
            it = f'reader_map.policy_question.official_targets[{reg}]'
            field(it + '.status', sr, er, 'status')
            field(it + '.target', sr, er, 'target', numeric=True)
            for k in ('decision_date', 'effective_date', 'first_publish'):
                field(it + '.' + k, sr, er, k)
            refs_check(it, sr, er)

    # pending_decisions
    eng = {r.get('region'): r
           for r in ((blk.get('pending_decisions') or {}).get('rows') or [])
           if isinstance(r, dict)}
    gm = keyed(echo.get('pending_decisions'), lambda r: r.get('region'),
               'reader_map.policy_question.pending_decisions')
    if gm is not None and cover(
            'reader_map.policy_question.pending_decisions', eng, gm):
        for reg, er in eng.items():
            sr = gm.get(reg)
            if sr is None:
                continue
            it = f'reader_map.policy_question.pending_decisions[{reg}]'
            field(it + '.answer', sr, er, 'answer')
            field(it + '.confirmed_through', sr, er, 'confirmed_through')
            refs_check(it, sr, er)
            try:
                ep = sorted(
                    (float(p.get('target_value'))
                     if p.get('target_value') is not None else None,
                     str(p.get('decision_date')), str(p.get('effective_on')))
                    for p in (er.get('pending_at_as_of') or [])
                    if isinstance(p, dict))
            except (TypeError, ValueError):
                ep = None
            sp = sr.get('pending')
            if ep is None or not isinstance(sp, list) or \
                    any(not isinstance(x, dict) for x in sp):
                bad(it + '.pending', 'pending 须为数组(条目为对象)')
                continue
            try:
                st = sorted(
                    (float(x.get('target')) if x.get('target') is not None
                     else None, str(x.get('decision_date')),
                     str(x.get('effective_date'))) for x in sp)
            except (TypeError, ValueError):
                bad(it + '.pending', 'pending 条目字段不可解析')
                continue
            fab = [x for x in st if x not in ep]
            drop = [x for x in ep if x not in st]
            if fab:
                bad(it + '.pending',
                    f'回声给出引擎面没有的待生效决定(虚构): {fab}',
                    contra=True)
            if drop:
                bad(it + '.pending', f'回声漏掉引擎面待生效决定: {drop}')
            if not fab and not drop:
                ok(it + '.pending', f'{len(ep)} 条逐条一致')

    # inflation_yoy
    eng = {(r.get('region'), r.get('metric_id')): r
           for r in ((blk.get('inflation_yoy') or {}).get('rows') or [])
           if isinstance(r, dict)}
    gm = keyed(echo.get('inflation_yoy'),
               lambda r: (r.get('region'), r.get('metric_id')),
               'reader_map.policy_question.inflation_yoy')
    if gm is not None and cover(
            'reader_map.policy_question.inflation_yoy', eng, gm):
        for (reg, mid), er in eng.items():
            sr = gm.get((reg, mid))
            if sr is None:
                continue
            it = f'reader_map.policy_question.inflation_yoy[{reg}:{mid}]'
            field(it + '.status', sr, er, 'status')
            field(it + '.value', sr, er, 'value', numeric=True)
            field(it + '.observation_month', sr, er, 'observation_month')
            field(it + '.publish_date', sr, er, 'publish_date')
            field(it + '.base_value', sr, (er.get('base') or {}),
                  'base_value', 'value', numeric=True)
            field(it + '.delta_pp', sr, er, 'delta_pp', numeric=True)
            refs_check(it, sr, er)

    # gaps_echoed(多重集相等)
    from collections import Counter as _Ctr
    eg = _Ctr((g.get('code'), g.get('region'), g.get('metric_id'))
              for g in (blk.get('gaps') or []) if isinstance(g, dict))
    sg = echo.get('gaps_echoed')
    if not isinstance(sg, list) or any(not isinstance(x, dict) for x in sg):
        bad('reader_map.policy_question.gaps_echoed',
            '须为数组(条目 {code, region, metric_id})')
    else:
        sc = _Ctr((x.get('code'), x.get('region'), x.get('metric_id'))
                  for x in sg)
        if sc == eg:
            ok('reader_map.policy_question.gaps_echoed',
               f'{sum(eg.values())} 条逐条一致')
        else:
            bad('reader_map.policy_question.gaps_echoed',
                f'缺口回声不一致: 缺 {sorted(map(str, (eg - sc).elements()))};'
                f' 多出 {sorted(map(str, (sc - eg).elements()))}')

    # 自由文字数字绑定(总判断/注记/评论)
    texts = [('reader_map.headline_conclusion', rm.get('headline_conclusion'))]
    cm = echo.get('comments')
    for i, c in enumerate(cm if isinstance(cm, list) else [cm]):
        texts.append((f'reader_map.policy_question.comments[{i}]', c))
    for face_name in ('official_targets', 'pending_decisions', 'inflation_yoy'):
        for i, r in enumerate(echo.get(face_name) or []):
            if isinstance(r, dict):
                texts.append((f'reader_map.policy_question.{face_name}'
                              f'[{i}].note', r.get('note')))
    # L3 叙述数字绑定(矛盾陈述正文+机制链各环正文): 与回声自由文字
    # 同口径——本族指标多不在通用文本检查器的静态别名表,L3 叙述数值
    # 此前零核验;席位自设阈值属 L4,不在本查。竞争性解释为假设叙述,
    # 不核。
    l3 = (judgment or {}).get('l3') or {}
    for c in l3.get('contradictions') or []:
        if isinstance(c, dict):
            texts.append((f"l3.{c.get('id')}.statement",
                          c.get('statement')))
    for ch in l3.get('mechanism_chains') or []:
        for i, lk in enumerate((ch or {}).get('links') or []):
            texts.append((f"l3.{(ch or {}).get('id')}.links[{i}].text",
                          (lk or {}).get('text')))
    for item, text in texts:
        if item.endswith('headline_conclusion') and not head:
            continue        # 已按空判
        un = _pq_unbound_tokens(text, nums, dates)
        if un:
            bad(item, f'自由文字数字与引擎面不对应: {un[:6]}')
        elif text is not None and str(text).strip():
            ok(item, '数字均与引擎面对应')
    return out


# ── Audit-R33 任务5: 预期差判断回声契约(地图五面契约之后追加) ────────────

_EG_SCHEMA = 'r33-expectations-gap'
_EG_DATE_TOKEN = re.compile(r'\b\d{4}-\d{2}-\d{2}\b')
# 时间词形(日期/年月/年份)里的数字不是阈值——核验数字阈值前先剔除
_EG_TIME_TOKEN = re.compile(
    r'\b\d{4}-\d{2}(?:-\d{2})?\b|(?<![\d.])(?:19|20)\d{2}(?![\d.])\s*年')
_EG_QUOTE_MIN = 8


def _eg_grams(text, n=_EG_QUOTE_MIN):
    t = re.sub(r'\s+', '', str(text or ''))
    return {t[i:i + n] for i in range(0, max(0, len(t) - n + 1))}


def _eg_quotes(quote, source):
    """quote 是否逐字引自 source(≥8 字连续原文;空白不计)。"""
    return bool(_eg_grams(quote) & _eg_grams(source)) or (
        len(re.sub(r'\s+', '', str(source or ''))) < _EG_QUOTE_MIN
        and str(source or '').strip()
        and re.sub(r'\s+', '', str(source)) in re.sub(r'\s+', '', str(quote)))


def _expectations_gap_checks(judgment, face, report, plan):
    """问到预期差的问句: 席位预期差判断(reader_map.expectations_gap)的
    结构化回声契约(确定性逐位核对)。

    回声(as_of/可见文档数/行数/可对账数/引擎候选清单/缺口清单)须与引擎面
    research_plan.expectations_gap 逐位一致;席位判定须逐行覆盖引擎候选与
    须席位推导行(supported|not_a_gap+解读与归因+竞争解释【假设】+证伪
    条件)。与引擎确定性面相左/虚构行号/假托机构原话=CONTRADICTED;缺席/
    引用不可解析/自由文字数字无引擎面对应=NOT_VERIFIED。地图五面契约照旧。"""
    out = []

    def ok(item, note):
        out.append({'item': item, 'claim_type': 'reader_map',
                    'status': 'VERIFIED', 'note': note, 'evidence_refs': []})

    def bad(item, note, contra=False):
        out.append({'item': item, 'claim_type': 'reader_map',
                    'status': 'CONTRADICTED' if contra else 'NOT_VERIFIED',
                    'note': note, 'evidence_refs': []})

    rm = (judgment or {}).get('reader_map')
    if not isinstance(rm, dict):
        bad('reader_map', '预期差判定须含 reader_map 顶层对象(五面+预期差)')
        return out
    blk = plan.get('expectations_gap')
    if not isinstance(blk, dict) or blk.get('schema') != _EG_SCHEMA:
        bad('research_plan.expectations_gap',
            '引擎预期差对照块缺席/损坏——无可回声面')
        return out
    echo = rm.get('expectations_gap')
    if not isinstance(echo, dict):
        bad('reader_map.expectations_gap',
            '席位预期差判断缺席(问到预期差: 须回声引擎面并逐候选行给出判定)')
        return out
    index = {e.get('ref'): e for e in (report.get('evidence_index') or [])}
    sm = blk.get('summary') or {}
    rows = [r for r in (blk.get('rows') or []) if isinstance(r, dict)]
    by_id = {}
    for r in rows:
        by_id.setdefault(r.get('row_id'), r)
    pool = {p.get('id'): p for p in (blk.get('falsification_pool') or [])
            if isinstance(p, dict) and p.get('id')}
    stmts = {}
    for st in (blk.get('view_statements') or []):
        if isinstance(st, dict):
            stmts.setdefault(st.get('view_id'), []).append(st.get('text'))
    # 数字绑定面: 对照块+研究计划(点值面/转折候选/定价曲线均在册)
    nums, dates = _pq_engine_numbers(plan)
    # 可观测量: 对照面指标+规则池观测量+计划指标/上下文指标
    obs = ({r.get('metric_id') for r in rows}
           | {str((p.get('observable') or '')).split('@')[0] for p in pool.values()}
           | set(plan.get('metrics') or [])
           | set(plan.get('context_metrics') or []))
    obs.discard(None)
    obs.discard('')

    def field(item, seat, eng, key, ekey=None, numeric=False):
        ev = eng.get(ekey or key)
        sv = seat.get(key)
        if ev is None:
            if sv is None:
                ok(item, '空=空')
            else:
                bad(item, f'引擎面无值而回声给出 {sv!r}(虚构)', contra=True)
            return
        if sv is None:
            bad(item, f'回声缺字段/为空(引擎 {ev!r})')
            return
        if numeric:
            try:
                same = abs(float(sv) - float(ev)) < 1e-9
            except (TypeError, ValueError):
                same = False
        else:
            same = (sv == ev)
        if same:
            ok(item, f'{sv!r} 一致')
        else:
            bad(item, f'回声 {sv!r} ≠ 引擎面 {ev!r}', contra=True)

    # ── 回声 ──
    it0 = 'reader_map.expectations_gap'
    field(it0 + '.as_of', echo, {'as_of': blk.get('as_of')}, 'as_of')
    for key, ekey in (('n_views_visible', 'n_views_visible'),
                      ('n_rows', 'n_rows'), ('comparable_n', 'comparable_n'),
                      ('engine_candidate_n', 'candidate_n')):
        field(it0 + '.' + key, echo, sm, key, ekey=ekey, numeric=True)
    cands = sorted(str(r.get('row_id')) for r in rows if r.get('candidate') is True)
    ec = echo.get('engine_candidates_echoed')
    if not isinstance(ec, list) or any(not isinstance(x, str) for x in ec):
        bad(it0 + '.engine_candidates_echoed', '须为字符串数组(引擎候选行号)')
    else:
        extra = sorted(set(ec) - set(cands))
        drop = sorted(set(cands) - set(ec))
        if not extra and not drop:
            ok(it0 + '.engine_candidates_echoed', f'{len(cands)} 行逐条一致')
        else:
            bad(it0 + '.engine_candidates_echoed',
                f'候选清单回声不一致: 缺 {drop}; 多出 {extra}',
                contra=any(x not in by_id for x in extra))
    from collections import Counter as _Ctr
    eg_ = _Ctr((g.get('code'), g.get('region'), g.get('metric_id'))
               for g in (blk.get('gaps') or []) if isinstance(g, dict))
    sg = echo.get('gaps_echoed')
    if not isinstance(sg, list) or any(not isinstance(x, dict) for x in sg):
        bad(it0 + '.gaps_echoed', '须为数组(条目 {code, region, metric_id})')
    else:
        sc = _Ctr((x.get('code'), x.get('region'), x.get('metric_id'))
                  for x in sg)
        if sc == eg_:
            ok(it0 + '.gaps_echoed', f'{sum(eg_.values())} 条逐条一致')
        else:
            bad(it0 + '.gaps_echoed',
                f'缺口回声不一致: 缺 {sorted(map(str, (eg_ - sc).elements()))};'
                f' 多出 {sorted(map(str, (sc - eg_).elements()))}')
    ss = echo.get('seat_summary')
    if isinstance(ss, str) and ss.strip():
        ok(it0 + '.seat_summary', '非空')
    else:
        bad(it0 + '.seat_summary',
            '席位总述缺席/为空(问到预期差: 须直接回答「有哪些预期差」)')

    # ── 证伪窗口回声(问句指定窗口时必回声;未指定而回声=虚构) ──
    win = blk.get('falsification_window')
    we = echo.get('window_echo')
    if isinstance(win, dict):
        if not isinstance(we, dict):
            bad(it0 + '.window_echo',
               '问句指定证伪窗口(%s → %s)——席位须回声窗口(月数/起/止)'
               % (win.get('start'), win.get('end')))
        else:
            for key in ('months', 'start', 'end'):
                field(it0 + '.window_echo.' + key, we, win, key)
    elif we is not None:
        bad(it0 + '.window_echo',
            '引擎面无证伪窗口而席位回声给出 %r(虚构)' % (we,), contra=True)

    # ── 席位判定逐行 ──
    must = sorted(set(cands) | {
        str(r.get('row_id')) for r in rows if r.get('status') == 'reading_required'})
    sup = echo.get('supported_gaps')
    if not isinstance(sup, list):
        bad(it0 + '.supported_gaps', '须为数组(逐行席位判定)')
        sup = []
    seen, texts = {}, [(it0 + '.seat_summary', ss)]
    for i, g in enumerate(sup):
        it = f'{it0}.supported_gaps[{i}]'
        if not isinstance(g, dict):
            bad(it, '条目须为对象')
            continue
        rid = g.get('row_id')
        if not isinstance(rid, str) or rid not in by_id:
            bad(it + '.row_id', f'行号不在引擎对照面({rid!r})——虚构行',
                contra=True)
            continue
        if rid in seen:
            bad(it + '.row_id', f'重复判定(首次见 [{seen[rid]}])')
            continue
        seen[rid] = i
        eng = by_id[rid]
        verdict, est = g.get('verdict'), eng.get('status')
        if verdict not in ('supported', 'not_a_gap'):
            bad(it + '.verdict',
                "须为 'supported'(预期差成立)或 'not_a_gap'(判非预期差)")
        elif verdict == 'supported':
            if eng.get('candidate') is True:
                ok(it + '.verdict', '引擎候选行——席位判预期差成立')
            elif est == 'reading_required':
                ok(it + '.verdict', '文字/多值点位行——席位推导判预期差成立')
            elif est in ('consistent', 'consistent_stale_fact',
                         'ex_post_consistent'):
                bad(it + '.verdict',
                    f'引擎面对照为「{_eg_status_cn(est)}」——席位判预期差'
                    '成立与引擎确定性面相左', contra=True)
            else:
                bad(it + '.verdict',
                    f'该行引擎状态为「{_eg_status_cn(est)}」——无事实/同期限'
                    '定价可对账,预期差成立无证据支撑(应判 not_a_gap 并写缺口)')
        else:
            ok(it + '.verdict', '席位判非预期差')
        reading, ra = g.get('reading'), g.get('reading_attribution')
        if not isinstance(reading, str) or not reading.strip():
            bad(it + '.reading', '席位解读缺席/为空')
        elif ra not in ('institution_stated', 'ai_inferred'):
            bad(it + '.reading_attribution',
                "须为 'institution_stated' 或 'ai_inferred'")
        elif (est == 'reading_required'
              and not (ra == 'ai_inferred' and '席位推导' in reading)):
            bad(it + '.reading',
                '文字/多值点位行引擎不解读——解读须 ai_inferred 且正文含'
                '「席位推导」')
        elif ra == 'institution_stated':
            if any(_eg_quotes(reading, q) for q in stmts.get(eng.get('view_id')) or []):
                ok(it + '.reading', f'机构原话(逐字引自 {eng.get("view_id")})')
            else:
                bad(it + '.reading',
                    f'标「机构原话」但未逐字引自该观点文档({eng.get("view_id")})'
                    f'的机构表述(≥{_EG_QUOTE_MIN} 字)——假托机构原话', contra=True)
        else:
            ok(it + '.reading', '席位推导')
        ce = g.get('competing_explanation')
        if not isinstance(ce, str) or not ce.strip():
            bad(it + '.competing_explanation',
                '竞争解释缺席(预期差判定须并列竞争性解释)')
        elif '假设' not in ce:
            bad(it + '.competing_explanation',
                '竞争解释须明写其【假设】(四层标注: 事实/推断/假设/尚未验证)')
        else:
            ok(it + '.competing_explanation', '并列竞争性解释(含假设)')
        reason = g.get('reason')
        if isinstance(reason, str) and reason.strip():
            ok(it + '.reason', '非空')
        else:
            bad(it + '.reason', '判定理由缺席/为空')
        fcs = g.get('falsification_conditions')
        if fcs is None and verdict == 'not_a_gap':
            fcs = []
        if not isinstance(fcs, list):
            bad(it + '.falsification_conditions', '须为数组')
            fcs = []
        elif verdict == 'supported' and not fcs:
            bad(it + '.falsification_conditions',
                '支持的预期差须给出 ≥1 条证伪条件(可观测指标+数字阈值+日期)')
        for j, c in enumerate(fcs):
            cit = it + f'.falsification_conditions[{j}]'
            if not isinstance(c, dict):
                bad(cit, '条目须为对象')
                continue
            cond, ca = c.get('condition'), c.get('attribution')
            if not isinstance(cond, str) or not cond.strip():
                bad(cit + '.condition', '条件文本缺席/为空')
                continue
            if ca == 'ai_inferred':
                if not _PQ_NUM_TOKEN.search(_EG_TIME_TOKEN.sub(' ', cond)):
                    bad(cit, '席位自设证伪条件须含数字阈值(日期/年份之外)')
                elif not _EG_DATE_TOKEN.search(cond):
                    bad(cit, '席位自设证伪条件须含观察截止日期(YYYY-MM-DD)')
                else:
                    hit = [m for m in obs
                           if re.search(r'(?<![A-Za-z0-9_])' + re.escape(str(m))
                                        + r'(?![A-Za-z0-9_])', cond)]
                    if not hit:
                        bad(cit, '席位自设证伪条件须含可观测量(在册指标 id): '
                            f'{cond[:40]}')
                    else:
                        ok(cit, f'可观测({sorted(hit)[:2]})+数字阈值+日期')
            elif ca in ('institution_stated', 'engine_rule'):
                p = pool.get(c.get('source_ref'))
                want = 'view_library' if ca == 'institution_stated' else 'engine_rule'
                if not p or p.get('source') != want or (
                        ca == 'institution_stated'
                        and p.get('attribution') != 'institution_stated'):
                    bad(cit + '.source_ref',
                        f'标「{"机构原话" if ca == "institution_stated" else "引擎规则"}」'
                        '须 source_ref 指向证伪条件池内对应来源条目(pool id)')
                elif not _eg_quotes(cond, p.get('condition')):
                    bad(cit + '.condition',
                        '条件须逐字引自所引'
                        f'{"机构原文" if ca == "institution_stated" else "引擎规则"}'
                        f'(≥{_EG_QUOTE_MIN} 字)', contra=True)
                else:
                    ok(cit, f'{c.get("source_ref")} 逐字引用')
            else:
                bad(cit + '.attribution',
                    "须为 'institution_stated' / 'ai_inferred' / 'engine_rule'")
        refs = g.get('evidence_refs')
        if (not isinstance(refs, list)
                or not all(isinstance(x, str) for x in refs) or not refs):
            bad(it + '.evidence_refs', '引用缺席/非字符串数组')
        else:
            unres = [x for x in refs if x not in index]
            er_refs = set(eng.get('evidence_refs') or [])
            if unres:
                bad(it + '.evidence_refs',
                    f'引用不可解析(不在 evidence_index): {unres[:3]}')
            elif er_refs and not (set(refs) & er_refs):
                bad(it + '.evidence_refs',
                    f'引用未落在该行引擎实据上(须含 {sorted(er_refs)[:3]} 之一)')
            else:
                ok(it + '.evidence_refs', f'{len(refs)} 引用可解析且落在引擎行')
        if isinstance(reading, str) and ra == 'ai_inferred':
            texts.append((it + '.reading', reading))
        texts.append((it + '.reason', reason))
    drop = [x for x in must if x not in seen]
    if drop:
        bad(it0 + '.supported_gaps',
            f'引擎候选/须席位推导行未逐行判定(缺 {drop})')
    elif must:
        ok(it0 + '.supported_gaps', f'{len(must)} 行逐行已判')
    ku = echo.get('key_unknowns')
    if not isinstance(ku, list) or any(not isinstance(x, str) for x in ku):
        bad(it0 + '.key_unknowns', '须为字符串数组')
    elif not ku and (sm.get('gaps') or 0) > 0:
        bad(it0 + '.key_unknowns',
            f'关键未知为空——引擎对照面有 {sm.get("gaps")} 项缺口,'
            '席位须写明哪些未知影响预期差判断')
    else:
        ok(it0 + '.key_unknowns', f'{len(ku)} 条')
        texts += [(f'{it0}.key_unknowns[{i}]', x) for i, x in enumerate(ku)]
    cm = echo.get('comments')
    if cm is None:
        cm = []
    if not isinstance(cm, list) or any(not isinstance(x, str) for x in cm):
        bad(it0 + '.comments', '须为字符串数组')
    else:
        texts += [(f'{it0}.comments[{i}]', x) for i, x in enumerate(cm)]

    # ── 自由文字数字绑定 ──
    for item, text in texts:
        if item.endswith('seat_summary') and not (
                isinstance(text, str) and text.strip()):
            continue        # 已按空判
        un = _pq_unbound_tokens(text, nums, dates)
        if un:
            bad(item, f'自由文字数字与引擎面不对应: {un[:6]}')
        elif isinstance(text, str) and text.strip():
            ok(item, '数字均与引擎面对应')
    return out


_EG_STATUS_CN = {
    'consistent': '一致', 'inconsistent': '不一致(引擎候选)',
    'consistent_stale_fact': '一致(陈旧读数)', 'no_longer_current': '已过时',
    'fact_mismatch': '与事实不符', 'unverifiable': '不可核',
    'context_only': '只列背景', 'reading_required': '须席位推导',
    'series_absent': '序列缺席', 'unmapped': '未映射',
    'ex_post_consistent': '事后一致', 'ex_post_missed': '事后未兑现',
    'not_comparable': '不可对照'}


def _eg_status_cn(status):
    return _EG_STATUS_CN.get(str(status), str(status))




def _ym_shift(ym, n):
    """YYYY-MM ± N 月(无依赖兜底;与 research_map_planner 同语义)。"""
    y, m = int(ym[:4]), int(ym[5:7])
    tot = y * 12 + (m - 1) + n
    return '%04d-%02d' % (tot // 12, tot % 12 + 1)
