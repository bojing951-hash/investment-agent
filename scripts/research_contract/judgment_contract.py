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

def _map_checks(judgment, face, report):
    """地图问句判定须含完整 reader_map;数值须与引擎序列回贴一致。

    任务4反例面: 机制正文空/None、必需图表(对照/传导/转折/历史)缺失、
    明确指定指标遗漏——结构缺席或数值与引擎确定性面相左都在此拦;
    空正文/缺图表=NOT_VERIFIED(修档再提),数值相左=CONTRADICTED。"""
    plan = (report or {}).get('research_plan') or {}
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
    return out


def _ym_shift(ym, n):
    """YYYY-MM ± N 月(无依赖兜底;与 research_map_planner 同语义)。"""
    y, m = int(ym[:4]), int(ym[5:7])
    tot = y * 12 + (m - 1) + n
    return '%04d-%02d' % (tot // 12, tot % 12 + 1)
