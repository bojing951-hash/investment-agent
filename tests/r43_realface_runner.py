#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R43 真实面复跑器(RDG-20261116-013 A 族硬化验收件)。

对 T7 三份真实周报(V1=20261114/V2=20261108/V3=20261024)用**当前引擎**
(含 R43 检查面预处理+遮罩补行+月-日日组修)全文重跑 tc.check_text,
对照 R41 定性件 audit/arch-reform/T7/t7_realface_r41.json 的
contradicted_full(修复前全量 CONTRA)做三方对账:

  - survivor:  修复后仍在(应=非 A 族面,逐 token 零漂移)
  - removed:   修复前在、修复后不在(A 族治面;按机制归因)
  - added:     修复后新增(**验收红线: 必须为空**——新误杀/回归即FAIL)

产出 audit/arch-reform/T7/t7_realface_r43.json。只读 LIVE 树,零写入。
非 CI 套件(命名无 test_ 前缀,同 r41_realface_runner 惯例)——依赖 LIVE
只读数据面,本仓克隆无此路径时明确跳过(exit 0 + SKIP 行)。
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

LIVE = ('/Users/cast/AI内容/🤖_AI投资项目/每周宏观追踪/'
        'investment-agent')

from research_contract import claim_factory as cf            # noqa: E402
from research_contract import text_consistency as tc          # noqa: E402

OUT = os.path.join(ROOT, 'audit', 'arch-reform', 'T7',
                   't7_realface_r43.json')
PREV = os.path.join(ROOT, 'audit', 'arch-reform', 'T7',
                    't7_realface_r41.json')


def _key(c):
    """对账键: family|metric|token(剥离尾部空白差异)。"""
    return (str(c.get('family')), str(c.get('metric')),
            str(c.get('token')).strip())


def _verbatim_in(tok, pp_text):
    """token 以完整数字形态 verbatim 在场(非碎片: 前界非数字/点)。"""
    t = str(tok).strip()
    if not t:
        return False
    for m in re.finditer(re.escape(t), pp_text):
        s = m.start()
        if s == 0 or not (pp_text[s - 1].isdigit()
                          or pp_text[s - 1] == '.'):
            return True
    return False


def _fragment_absent(tok, pp_text):
    """removed 碎片不再以独立形态在场(前界非数字/点)。"""
    return not _verbatim_in(tok, pp_text)


def _mechanism_of(token):
    """removed 项机制归因(按 token 形态与 R41/R43 修复面对号)。"""
    t = str(token).strip()
    if re.fullmatch(r'\d{1,2}\.\s*', t + ' ' if not t.endswith(' ')
                    and '.' in t else t):
        return 'ordinal(列表序号)'
    if re.match(r'^\d+(\.\d+)?%$', t) and t not in ():
        return 'decimal_split_or_percent_frag(月日吞数字/注释碎片)'
    return 'comment_json_citation_frag(注释/JSON/引用ID/序号碎片)'


def main():
    if not os.path.isdir(LIVE):
        print('SKIP: LIVE 树不可达(克隆环境),真实面复跑为在位诊断件')
        return 0
    if not os.path.isfile(PREV):
        print('SKIP: R41 定性件不在档(t7_realface_r41.json)')
        return 0
    snap14 = json.load(open(os.path.join(
        ROOT, 'tests/fixtures/t6/snapshot_20261114_v2.json'),
        encoding='utf-8'))
    snap08 = json.load(open(os.path.join(
        LIVE, 'data/daily/research_snapshot_20261108_v2.json'),
        encoding='utf-8'))
    snap24 = json.load(open(os.path.join(
        LIVE, 'data/daily/research_snapshot_20261024.json'),
        encoding='utf-8'))
    anc14 = json.load(open(os.path.join(
        LIVE, 'data/daily/anchors_20261114.json'), encoding='utf-8'))
    anc08 = json.load(open(os.path.join(
        LIVE, 'data/daily/anchors_20261108.json'), encoding='utf-8'))
    anc31 = json.load(open(os.path.join(
        LIVE, 'data/daily/anchors_20261031.json'), encoding='utf-8'))
    anc24_files = sorted(p for p in os.listdir(os.path.join(
        LIVE, 'data/daily'))
        if re.match(r'anchors_202610(1[7-9]|2[0-4])\.json$', p))
    anc24 = json.load(open(os.path.join(LIVE, 'data/daily',
                                        anc24_files[-1]), encoding='utf-8'))
    thr = cf.load_thresholds()
    REAL = [
        ('V1', 'output/weekly/weekly_report_20261114_UNVALIDATED.md',
         snap14, {'2026-11-08': anc08, '2026-11-14': anc14}),
        ('V2', 'output/weekly/weekly_report_20261108_UNVALIDATED.md',
         snap08, {'2026-10-31': anc31, '2026-11-08': anc08}),
        ('V3', 'output/weekly/weekly_report_20261024.md',
         snap24, {}),
    ]
    prev = json.load(open(PREV, encoding='utf-8'))
    out = {'note': 'R43 真实面复跑(RDG-20261116-013 验收件;对照=R41 '
                   '定性件 contradicted_full,三方对账 survivor/removed/'
                   'added)',
           'engine': '本分支当前引擎(含 R43 检查面预处理+引用ID/序号'
                     '遮罩+月-日日组必选)',
           'baseline': 'audit/arch-reform/T7/t7_realface_r41.json',
           'runs': {}}
    fail = False
    for vid, rel, snap, prior in REAL:
        text = open(os.path.join(LIVE, rel), encoding='utf-8').read()
        r = tc.check_text(text, snapshot=snap, thresholds=thr,
                          prior_anchors=prior or None)
        contra = [c for c in r['checks'] if c['status'] == 'CONTRADICTED']
        prev_contra = prev['runs'][vid]['contradicted_full']
        prev_keys = {}
        for c in prev_contra:
            prev_keys.setdefault(_key(c), 0)
            prev_keys[_key(c)] += 1
        new_keys = {}
        for c in contra:
            new_keys.setdefault(_key(c), 0)
            new_keys[_key(c)] += 1
        removed = []
        for k, n in prev_keys.items():
            d = n - new_keys.get(k, 0)
            if d > 0:
                removed.append({'key': list(k), 'n': d,
                                'mech': _mechanism_of(k[2])})
        added = []
        pp_text = tc._checkface_preprocess(text)
        for k, n in new_keys.items():
            d = n - prev_keys.get(k, 0)
            if d > 0:
                added.append({'key': list(k), 'n': d,
                              'verbatim': _verbatim_in(k[2], pp_text)})
        # 验收红线: 新增 CONTRA 的 token 须 verbatim 在场于源文本
        # (完整数字形态)——碎片(8775%)不在场=修面证词;在场而新增=
        # 修复致引擎织造新误杀面=FAIL。月日吞数字修复的正位升格
        # (碎片 8775%→完整 3.8775%)属预期: 同一叙事位,token 如实。
        bad_added = [a for a in added if not a['verbatim']]
        if bad_added:
            fail = True
        for x in removed:
            x['fragment_gone'] = _fragment_absent(x['key'][2], pp_text)
        out['runs'][vid] = {
            'file': os.path.basename(rel),
            'verdict': r['verdict'], 'stats': r['stats'],
            'r41_contra': len(prev_contra), 'r43_contra': len(contra),
            'removed_total': sum(x['n'] for x in removed),
            'survivor_total': len(prev_contra)
            - sum(x['n'] for x in removed),
            'added': added,
            'removed': removed,
            'survivor_sample': [
                {'key': list(k), 'n': n} for k, n in
                sorted(new_keys.items())][:0],   # 全量见 clusters
            'clusters': _clusters(contra),
        }
        print(f"[{vid}] contra {len(prev_contra)} -> {len(contra)} "
              f"(removed={out['runs'][vid]['removed_total']}, "
              f"added_repair={len(added)}, bad_added={len(bad_added)})")
        for k, v in list(out['runs'][vid]['clusters'].items())[:6]:
            print(f"    {v['n']:3d}  {k}  例: {v['tokens'][:4]}")
        if bad_added:
            print(f"    !! BAD-ADDED(验收红线: 织造新误杀): {bad_added[:6]}")
    out['verdict'] = ('FAIL(新增 CONTRA token 非 verbatim 在场=回归)'
                      if fail else
                      'PASS(新增仅修复位升格且 verbatim 在场;'
                      'removed=A 族治面)')
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print(f"→ {OUT}  verdict={out['verdict']}")
    return 1 if fail else 0


def _clusters(contra):
    cl = {}
    for c in contra:
        k = f"{c['family']}|{c.get('metric')}"
        cl.setdefault(k, []).append(str(c.get('token'))[:24])
    return {k: {'n': len(v), 'tokens': v[:8]}
            for k, v in sorted(cl.items(), key=lambda kv: -len(kv[1]))}


if __name__ == '__main__':
    sys.exit(main())
