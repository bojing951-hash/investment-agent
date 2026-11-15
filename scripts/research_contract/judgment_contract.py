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

def _six_checks(judgment, face):
    out = []
    # 可观测集=面内事实∪序列∪索引实据(报告自身证据声明亦算可观测;
    # 真实面 evidence_index 实据 ⊆ S3 事实,行为不变——宽集只补薄报告)。
    observable = ({f['metric_id'] for f in face.get('facts', [])}
                  | set((face.get('series_store') or {}).keys())
                  | {(e.get('metric_id') or '')
                     for e in face.get('evidence_index') or []
                     if e.get('kind') == 'snapshot_fact'})
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
                     if (index.get(r) or {}).get('kind') == 'snapshot_fact']
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

def verify_judgment(judgment, report, thresholds=None, face=None):
    """判定档 vs 自身证据面 → {'verdicts','six_checks','verdict','stats'}。

    face 已建(如冻结夹具/上游复用)则直用,免重复构建。
    """
    face = face if face is not None else build_face(report)
    thresholds_by = cf.thresholds_by_metric(
        thresholds if thresholds is not None else cf.load_thresholds())
    verdicts, unbound_left = [], []
    n_contra = n_ver = 0
    l3 = ((judgment.get('l3') or {}).get('contradictions')) or []
    for con in l3:
        for field in ('statement', 'basis'):
            text = con.get(field) or ''
            if not text:
                continue
            r = tc.check_text(text, snapshot=face, thresholds=thresholds_by)
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
    if n_contra:
        verdict = 'CONTRADICTED'     # 客观事实错→整体降级,渲染面披露
    elif unbound_left or six_bad:
        verdict = 'NOT_VERIFIED'
    else:
        verdict = 'VERIFIED'
    return {
        'version': JUDGMENT_CONTRACT_VERSION,
        'verdicts': verdicts,
        'six_checks': six,
        'unresolved_unbound': unbound_left,
        'verdict': verdict,
        'stats': {
            'checks': len(verdicts), 'contradicted': n_contra,
            'verified': n_ver, 'unbound': len(unbound_left),
            'six_fail': len(six_bad),
            'n_contradictions': len(l3),
        },
    }
