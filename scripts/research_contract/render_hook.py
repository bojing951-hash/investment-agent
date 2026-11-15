# -*- coding: utf-8 -*-
"""确定性渲染钩子(架构整改阶段三 T6b,C1 载重墙)。

契约律6(C1): 渲染器=确定性模板,消费 VERIFIED claim,产出全部数值单元格
+manifest;模型丧失整文数值著作权(叙事文本另行,narrative 槽不含数值)。
manifest 只准由本模板产出——禁模型自报、禁按值反扫重建。

律1: 身份不靠文本——渲染消费 claim 对象(metric_id/claim_type 自带),
manifest=claim_id→(行号,token串,值) 登记位,渲染时刻记录。
律3: 渲染后缀不反推单位——后缀由 claim.unit 决定(显示形态),非解析源。
精度往返: 按单位定渲染位数;值含 ≤4 位小数时显式全位(3.8775→"3.8775"),
更多位按单位默认位(7561.669922→"7,561.67"),round(x,dp) 往返相等断言。

纯度: stdlib+契约内只读;零模型/零网络/零随机/零时钟。
"""
from __future__ import annotations

import json

from research_contract import claim_factory as cf

RENDER_HOOK_VERSION = 'rh-v1'

# 单位族→(默认小数位, 千分位, 后缀显示形态)
# 后缀=显示形态非语义源(律3): percent→'%',percentage_point→'pp',
# basis_point→'bp'(渲染换算 ×100?否——claim 值已按 canonical 单位存,
# bp 显示=pp×100 后缀 'bp';此处 value 已是 claim.value,单位串随 claim)。
_UNIT_DISPLAY = {
    'index_point': (2, True, ''),
    'percent': (2, False, '%'),
    'percentage_point': (2, False, 'pp'),
    'basis_point': (0, True, 'bp'),
    'dimensionless': (2, False, ''),
    'cny_100m': (2, True, '亿元'),
    'hkd_100m': (2, True, '亿港元'),
    'usd_100m': (2, True, '亿美元'),
    'usd': (2, True, '美元'),
    'jpy_per_usd': (2, True, ''),
    'persons': (0, True, ''),
    'persons_thousands': (0, True, '千'),
    'calendar_day': (0, False, '天'),
    'rank_position': (0, False, ''),
    'observation_count': (0, True, ''),
}
_DEFAULT_DISPLAY = (2, False, '')

_WINDOW_WORD = {'week': '周', 'm1': '月', 'm3': '3月', 'm6': '6月',
                'm12': '年', 'mtd': '月内', 'ytd': '年内'}
_RELATION_WORD = {'above': '上方', 'below': '下方', 'at': '线上'}


class RenderError(ValueError):
    """渲染输入违反律6(C1 只准 VERIFIED 入事实区)。"""


def _fmt_value(value, unit, *, explicit_decimals=None):
    """单位族显示形态+精度往返(≤4 位小数显式全位;更多=单位默认位)。"""
    dp, comma, _suffix = _UNIT_DISPLAY.get(unit, _DEFAULT_DISPLAY)
    if explicit_decimals is not None:
        dp = explicit_decimals
    elif isinstance(value, float):
        # 精度往返: 小数尾在 (默认位,4] 区间者升位显式(3.8775→4 位);
        # 不足默认位不降位(percent/pp 恒 ≥2dp: 3.2→'3.20')
        s = repr(value)
        if 'e' not in s and '.' in s:
            dec = len(s.split('.')[1].rstrip('0'))
            if dp < dec <= 4:
                dp = dec
    x = round(float(value), dp)
    body = f'{x:,.{dp}f}' if comma else f'{x:.{dp}f}'
    # 往返断言: 解析回=按显示位舍入值
    if float(body.replace(',', '')) != x:
        raise RenderError(f'精度往返失败: {value!r}→{body}')
    return body


def _suffix(unit):
    return _UNIT_DISPLAY.get(unit, _DEFAULT_DISPLAY)[2]


def _alias_of(metric_id, registry=None):
    """指标显示名(注册表 display 名优先;缺席回退 metric_id 本串)。"""
    if registry:
        m = registry.get(metric_id) or {}
        for k in ('display_name', 'name_cn', 'name'):
            if m.get(k):
                return m[k]
    return metric_id


def render_report(verdicts, bundle, *, snapshot=None, registry=None,
                  thresholds=None):
    """VERIFIED→【事实】区;其余六态→【披露】区。

    verdicts: claim_verifier.verify_bundle()['verdicts'] 列表。
    bundle: claim_bundle 装配产物(claims 按 claim_id 索引)。
    返回 {'markdown', 'manifest', 'stats'}: manifest.spans=事实区登记位
    (行号,token串,值,claim_id),disclosure_spans=披露区登记位——渲染
    时刻记录,禁反扫重建(C1)。
    """
    claims_by_id = {c['claim_id']: c for c in bundle.get('claims', [])}
    reg = registry if registry is not None else \
        (cf.fe.metric_registry() if hasattr(cf.fe, 'metric_registry')
         else None)
    lines_fact = []
    spans, disc_spans = [], []

    def _emit_fact(text, tokens):
        """tokens=[(token_str, value, claim_id)] 数值登记位(行号=追加后)。"""
        lines_fact.append(text)
        line_no = len(lines_fact) - 1
        for tok, v, cid in tokens:
            spans.append((line_no, tok, v, cid))

    _NUM_LITE = __import__('re').compile(
        r'[+\-−]?\d[\d,]*(?:\.\d+)?')

    def _emit_disclosure(text, tokens, cid=None):
        """披露行: 理由串内数值(复算值等)一并登记 disclosure_spans——
        披露≠免检,数值仍须可溯源(律8 游离扫描零豁免)。"""
        lines_fact.append('  ' + text)          # 披露行缩进两格
        line_no = len(lines_fact) - 1
        for tok, v, c_ in tokens:
            disc_spans.append((line_no, tok, v, c_))
        if cid:
            for m in _NUM_LITE.finditer(text):
                raw = m.group(0)
                try:
                    val = float(raw.replace(',', '').replace('−', '-'))
                except ValueError:
                    val = None
                disc_spans.append((line_no, raw, val, cid))

    for v in verdicts:
        c = claims_by_id.get(v.get('claim_id'))
        if c is None:
            continue
        status = v.get('status')
        mid = c.get('metric_id')
        mids = c.get('metric_ids') or []
        label = _alias_of(mid, reg) if mid else \
            '×'.join(_alias_of(m, reg) for m in mids)
        unit = c['unit']
        if status == 'VERIFIED':
            ct = c['claim_type']
            if ct == 'level':
                if c['subtype'] == 'band':
                    lo = _fmt_value(c['value']['low'], unit)
                    hi = _fmt_value(c['value']['high'], unit)
                    tok = f'{lo}–{hi}{_suffix(unit)}'
                    _emit_fact(f'- 【事实】{label} 区间 {tok}'
                               f'（{c["observation_date"]}）',
                               [(lo, c['value']['low'], c['claim_id']),
                                (hi, c['value']['high'], c['claim_id'])])
                else:
                    tok = _fmt_value(c['value'], unit) + _suffix(unit)
                    _emit_fact(f'- 【事实】{label} {tok}'
                               f'（{c["observation_date"]}）',
                               [(tok, c['value'], c['claim_id'])])
            elif ct == 'change':
                w = _WINDOW_WORD.get(c.get('window'), c.get('window'))
                vraw = c['value']
                sign = '+' if vraw >= 0 else '−'
                body = _fmt_value(abs(vraw), unit)
                tok = f'{sign}{body}{_suffix(unit)}'
                btok = _fmt_value(c['basis_value'], c['unit'])
                _emit_fact(f'- 【事实】{label} {w}变化 {tok}'
                           f'（基准 {c["basis_date"]}={btok}）',
                           [(tok, vraw, c['claim_id']),
                            (btok, c['basis_value'], c['claim_id'])])
            elif ct == 'threshold_distance':
                tok = _fmt_value(c['value'], unit) + (_suffix(unit) or '')
                lv = _fmt_value(_level_of(c, v), unit) + _suffix(unit)
                _emit_fact(f'- 【事实】{label} 距{c["threshold_ref"]["name"]}'
                           f' {tok}（水平 {lv}）',
                           [(tok, c['value'], c['claim_id']),
                            (lv, _level_of(c, v), c['claim_id'])])
            elif ct == 'observation_lag':
                tok = _fmt_value(c['value'], unit) + _suffix(unit)
                _emit_fact(f'- 【事实】{label} 观测滞后 {tok}'
                           f'（as_of {c["as_of_date"]}）',
                           [(tok, c['value'], c['claim_id'])])
            elif ct == 'statistic':
                if c['value'] is None:
                    tok = 'nan'
                    _emit_fact(f'- 【事实】{label} '
                               f'{c["corr_window_days"]}日相关 {tok}'
                               f'（{c.get("nan_reason") or "窗含nan源"}）',
                               [(tok, None, c['claim_id'])])
                else:
                    tok = _fmt_value(c['value'], unit, explicit_decimals=2)
                    tok_s = f'{c["value"]:+.2f}'
                    _emit_fact(f'- 【事实】{label} '
                               f'{c["corr_window_days"]}日相关 {tok_s}',
                               [(tok_s, c['value'], c['claim_id'])])
            elif ct == 'threshold':
                tok = _fmt_value(c['threshold_ref']['value'],
                                 unit) + _suffix(unit)
                _emit_fact(f'- 【事实】{label} 处{c["threshold_ref"]["name"]}'
                           f'{_RELATION_WORD.get(c["relation"], "")} '
                           f'{tok}', [(tok, c['threshold_ref']['value'],
                                       c['claim_id'])])
            elif ct == 'comparison':
                if c['subtype'] == 'rank':
                    _emit_fact(f'- 【事实】{label} 排名断言 '
                               f'（rank_key={c.get("rank_key")}）', [])
                else:
                    tok = _fmt_value(c['value'], unit) + (_suffix(unit) or '')
                    _emit_fact(f'- 【事实】{label} {c["subtype"]} {tok}',
                               [(tok, c['value'], c['claim_id'])])
            else:
                _emit_fact(f'- 【事实】{label} {c["claim_type"]} 断言', [])
        else:
            # 律6: 未验证不冒充——六态非 VERIFIED 全部入披露区
            note = ';'.join(v.get('reasons', [])[:1])
            _emit_disclosure(f'- [{status}] {label} '
                             f'({c["claim_type"]}/{c.get("subtype")}) {note}',
                             [], cid=c['claim_id'])
    markdown = '\n'.join(lines_fact)
    fact_ids = {cid for _, _, _, cid in spans}
    return {'markdown': markdown,
            'manifest': {'spans': spans, 'disclosure_spans': disc_spans,
                         'render_hook_version': RENDER_HOOK_VERSION},
            'stats': {'fact_claims': len(fact_ids),
                      'disclosure_lines': sum(
                          1 for l in lines_fact if l.startswith('  ')),
                      'total_verdicts': len(verdicts)}}


def _level_of(c, v):
    """threshold_distance 的水平端: 从 evidence snapshot_fact 取值。"""
    for r in c.get('evidence_refs', []):
        if r.get('kind') == 'snapshot_fact' and isinstance(
                r.get('value'), (int, float)):
            return r['value']
    return v.get('computed') if v.get('computed') is not None else 0


def render_narrative_slot(*, title='叙事', note='模型叙事槽:禁自报数值,'
                          '数值一律引用【事实】区'):
    """narrative 槽占位(模型叙事面;数值著作权=渲染器,C1)。"""
    return {'slot': 'narrative', 'title': title, 'note': note,
            'allowed_claim_roles': ('narrative_reference',)}


def load_manifest(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)
