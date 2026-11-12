#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""金融指标方向语义规则(Charter 10 §5.1,R22 2026-11-12)——纯确定性,零 AI。

问题(复现档 audit/R22_FIN_CORRECTNESS_REPRO.py):
  "日元升值"含方向词'升'→机械 hint=up,但 USDJPY 150→145(日元实际升值)
  实际序列方向=down → 旧逻辑判 against=金融语义错判(Charter 原文案)。
  同族: "国债价格上涨"对收益率指标(价格涨=收益率跌)/"欧元升值"对 EURUSD。

规则(config/metric_direction_semantics.json,只登记反向风险指标):
  fx_quote_pair: 措辞主体=计价货币(quote,如 USDJPY 的日元)→ hint 反转;
    主体=基准货币(base,如美元)→ 不反转;报价对名义(美元兑日元/USDJPY)
    → 不反转;相对措辞"A 相对/兑/vs B"→ 主体=A。
  yield_vs_price: 收益率类指标,措辞主体=价格 → 反转;主体=收益率/利率/
    yield 或未指明 → 不反转(N 年期国债上行=市场惯例指收益率)。
  未登记指标: 无反转,方向=指标名义方向(本模块零介入)。

优先级(确定序): pair_patterns > 相对措辞 > 单侧 token > 未识别(直接比对+披露)。
双 token 同现且无报价对名义/相对结构(如"美元与日元均…")= 未识别,直接比对
+披露注——不猜主体。hint=None(点位型/否定护栏拦截)不进本模块。

attribution 纪律: 本模块不做方向*提取*(提取仍=view_verifier._parse_direction
机构明示词表),只做已提取方向 vs 指标报价语义的确定性换算;两者叠加后仍属
institution_stated 机械面。
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEM_PATH = os.path.join(ROOT, 'config', 'metric_direction_semantics.json')

# 相对措辞分隔(A 相对/兑/vs B → 主体=A);EN 词边界防误拆
_REL_SPLIT_RE = re.compile(r'\s*(?:相对|兑|对|vs\.?|/|-)\s*', re.I)

_cache = {}


def load_semantics(path=None):
    """读方向语义表(带缓存;结构校验: rules 非空对象)。"""
    p = path or SEM_PATH
    if p in _cache:
        return _cache[p]
    with open(p, encoding='utf-8') as f:
        sem = json.load(f)
    rules = sem.get('rules')
    if not isinstance(rules, dict) or not rules:
        raise ValueError('metric_direction_semantics.json 须含非空 rules 对象')
    _cache[p] = sem
    return sem


def _rule_for(metric_id, sem):
    r = (sem.get('rules') or {}).get(metric_id)
    if r is None:
        return None
    if r.get('kind') == 'yield_vs_price':      # 共享 token 面(防九处重复)
        shared = sem.get('yield_vs_price_shared') or {}
        return {'kind': 'yield_vs_price', **shared}
    return r


def _tokens_in(text, tokens):
    """EN 词用词边界匹配(与 view_verifier._DIR_*_RE 同纪律),CN 子串。"""
    hits = []
    for t in tokens or []:
        if not t:
            continue
        if re.fullmatch(r'[A-Za-z3-]{2,}', t):
            if re.search(rf'(?<![A-Za-z]){re.escape(t)}(?![A-Za-z])', text,
                         re.I):
                hits.append(t)
        elif t in text:
            hits.append(t)
    return hits


def _relative_subject(text, base_tokens, quote_tokens):
    """相对措辞主体: 'A 相对/兑/vs B' → 主体=A。返回 'base'|'quote'|None。

    扫描所有分隔片段: 主体侧=分隔符之前紧邻出现的币种 token 所在侧;
    仅当全部分隔结构的主体侧一致才判(不一致=未识别,不猜)。"""
    sides = []
    parts = _REL_SPLIT_RE.split(text)
    if len(parts) < 2:
        return None
    # 逐分隔位置: 主体=该分隔符左侧最近片段中出现的币种
    for i in range(len(parts) - 1):
        left = parts[i]
        b = _tokens_in(left, base_tokens)
        q = _tokens_in(left, quote_tokens)
        if b and not q:
            sides.append('base')
        elif q and not b:
            sides.append('quote')
    if sides and len(set(sides)) == 1:
        return sides[0]
    return None


def apply_metric_direction_semantics(hint, metric_id, texts, sem=None):
    """已提取方向 hint(up/down)× 指标报价语义 → (metric_hint, 披露节点|None)。

    hint 非 up/down(含 None)→ 原样返回(本模块零介入,点位型不换算)。
    metric 未登记 → 原样返回(None 披露=无反转面,输出不添噪声)。
    texts: 参与主体识别的文本序列(如 [target, value_or_direction])。
    披露节点: {'metric_id','kind','subject_side','inverted','basis',
    'matched_tokens'}——subject_side ∈ pair|base|quote|price|yield|unspecified。"""
    if hint not in ('up', 'down'):
        return hint, None
    sem = sem or load_semantics()
    rule = _rule_for(metric_id, sem)
    if rule is None:
        return hint, None
    text = ' '.join(str(t) for t in texts if t)
    inv = None
    if rule['kind'] == 'fx_quote_pair':
        pair = _tokens_in(text, rule.get('pair_patterns'))
        base = _tokens_in(text, rule.get('base_tokens'))
        quote = _tokens_in(text, rule.get('quote_tokens'))
        if pair:
            side, matched, inv = 'pair', pair, False
        else:
            rel = _relative_subject(text, rule.get('base_tokens'),
                                    rule.get('quote_tokens'))
            if rel == 'base':
                side, matched, inv = 'base', base, False
            elif rel == 'quote':
                side, matched, inv = 'quote', quote, True
            elif quote and not base:
                side, matched, inv = 'quote', quote, True
            elif base and not quote:
                side, matched, inv = 'base', base, False
            else:
                side, matched, inv = 'unspecified', [], False
    elif rule['kind'] == 'yield_vs_price':
        direct = _tokens_in(text, rule.get('direct_tokens'))
        inverse = _tokens_in(text, rule.get('inverse_tokens'))
        if inverse and not direct:
            side, matched, inv = 'price', inverse, True
        elif direct and not inverse:
            side, matched, inv = 'yield', direct, False
        elif direct and inverse:
            side, matched, inv = 'unspecified', direct + inverse, False
        else:
            # 未指明主体: 指标即收益率,市场惯例'N年期国债上行'=收益率方向
            side, matched, inv = 'yield', [], False
    else:
        return hint, None
    metric_hint = ('down' if hint == 'up' else 'up') if inv else hint
    node = {
        'metric_id': metric_id, 'kind': rule['kind'], 'subject_side': side,
        'inverted': bool(inv),
        'basis': (f"措辞主体={side}({'反转' if inv else '直接'}比对); "
                  f"规则={rule.get('basis', rule['kind'])}"),
        'direction_word_meaning': hint, 'metric_direction': metric_hint,
    }
    if matched:
        node['matched_tokens'] = matched
    if side == 'unspecified':
        node['basis'] += '; 主体未识别→按指标名义方向直接比对(不猜主体)'
    return metric_hint, node


def main(argv=None):
    """自检入口: 对示例措辞打印换算表(人工核对语义表用,不进管线)。"""
    argv = argv if argv is not None else []
    cases = [
        ('USDJPY', '日元', '日元升值', 'up'),
        ('USDJPY', '美元兑日元', '美元兑日元将上行', 'up'),
        ('USDJPY', '日元', '日元相对美元走强', 'up'),
        ('EURUSD', '欧元', '欧元升值', 'up'),
        ('EURUSD', '欧元兑美元', 'EURUSD 目标 1.20 方向higher', 'up'),
        ('UST_10Y', '美国10年期国债', '国债价格上涨', 'up'),
        ('UST_10Y', '美国10年期国债', '收益率上行', 'up'),
        ('UST_10Y', '美国10年期国债', '10年期国债上行', 'up'),
        ('SPX', '标普500', '上涨', 'up'),
    ]
    for metric, target, text, hint in cases:
        mh, node = apply_metric_direction_semantics(hint, metric,
                                                    [target, text])
        inv = node and node.get('inverted')
        print(f'{metric:8s} {text!r} hint={hint} → metric={mh}'
              f' inverted={bool(inv)} side={node and node["subject_side"]}')
    if '--strict' in argv:
        # 示例断言(语义表回归锁的极简面;全套锁在 tests/test_rd_r22_*)
        expect = [('USDJPY', 'up', 'down'), ('UST_10Y', 'up', 'down'),
                  ('SPX', 'up', 'up')]
        got = [apply_metric_direction_semantics(h, m, ['x'])[0]
               for m, _, h in expect]
        want = [w for _, w, _ in expect]
        if got != want:
            print(f'STRICT FAIL: {got} != {want}')
            return 1
        print('strict ok')
    return 0


if __name__ == '__main__':
    sys.exit(main())
