#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit-R12(R56) 门: P1-① 统一时间要求完整性校验 + P1-② 来源结构不完整
禁止误删证据。基线 f5bc514 反例 → 修复后应然,全部走生产链
(merge_cn_history→load_metric_series→_evaluate_data_requirements;
build_snapshot→prune_daily_archives;ia_cli research-one report/archive)。

§A 六确认反例(T1-T6) §B 性质 a/b/c §C 裸日期/年份族 §D 未支持单位族
§E 护栏与合法对照 §F P1-② 结构损坏×保留策略 §G 生产 report/archive 双门
破坏性操作全部限于临时目录;子进程一律 sys.executable(同解释器)。
"""
import gzip
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import agent_judgment as aj          # noqa: E402
import china_market_collector as cmc  # noqa: E402
import data_retention as drt         # noqa: E402
import macro_collector as mc         # noqa: E402
import research_orchestrator as ro   # noqa: E402
import research_history_query as rhq  # noqa: E402
import snapshot_builder as sb        # noqa: E402

PASS, FAIL = 0, 0


def check(name, cond, detail=''):
    global PASS, FAIL
    print(f"  {'✅' if cond else '❌'} {name}" + (f" — {detail}" if detail and not cond else ''))
    PASS = PASS + (1 if cond else 0)
    FAIL = FAIL + (0 if cond else 1)


# ══════════════════════════════════════════════════════════════════
print('§A P1-① 六确认反例(生产链: 真实 CN_PMI_MFG 隔离副本)')

_REAL = json.load(open(os.path.join(
    ROOT, 'docs/autonomous-rd/cn-task-b-20261117T083954Z/macro_input/',
    'macro_20261117.json')))
_RD = _REAL['data']['CN_PMI_MFG']['series']['dates']
_RV = _REAL['data']['CN_PMI_MFG']['series']['values']
_VMAP = dict(zip(_RD, _RV))


def _sub(pred):
    ds = [d for d in _RD if pred(d)]
    return ds, [_VMAP[d] for d in ds]


C_D, C_V = _sub(lambda d: '2025-01-01' <= d <= '2026-10-01')   # 22 点
E_D, E_V = _sub(lambda d: '2026-01-01' <= d <= '2026-10-01')   # 10 点


def _cn_item(ds, vs):
    return {'date': ds[-1], 'value': vs[-1], 'prev': vs[-2],
            'frequency': 'monthly', 'unit': 'index_point',
            'series': {'dates': ds, 'values': vs},
            'provenance': {'source': 'akshare_em(macro_china)',
                           'fetched_at': '2026-11-17T02:00:00Z',
                           'coverage': {'n': len(ds)}}}


def _new_root():
    d = tempfile.mkdtemp(prefix='r12gate_')
    os.makedirs(os.path.join(d, 'data', 'daily'))
    os.makedirs(os.path.join(d, 'config'))
    shutil.copy(os.path.join(ROOT, 'config', 'metric_registry.json'),
                os.path.join(d, 'config', 'metric_registry.json'))
    return d


def _run_round(d, item):
    mc.DATA_DIR = os.path.join(d, 'data')
    cmc.fetch_macro_history = lambda: {'CN_PMI_MFG':
                                       json.loads(json.dumps(item))}
    results, _ = mc.merge_cn_history({'HY_OAS': {'value': 3.1,
                                                  'date': '2026-11-13',
                                                  'frequency': 'daily'}},
                                     data_dir=mc.DATA_DIR)
    mc.save_macro(results, [], {}, cn_history=_)


def _latest_ymd(d):
    fs = sorted(f for f in os.listdir(os.path.join(d, 'data', 'daily'))
                if f.startswith('macro_'))
    return fs[-1][6:14]


def win_of(r):
    w = (r.get('spec') or {}).get('window')
    return w if isinstance(w, dict) else {}


def eval_item(d, question, as_of):
    res = rhq.load_metric_series(
        'CN_PMI_MFG', _latest_ymd(d),
        data_dir=os.path.join(d, 'data', 'daily'), trusted_root=d)
    env = {'n': len(res['dates']),
           'source': f"采集档 {res['source']['file']}",
           'frequency': res['frequency'],
           'first': res['dates'][0] if res['dates'] else None,
           'last': res['dates'][-1] if res['dates'] else None,
           'dates': res['dates'], 'values': res['values']}
    step = {'step': 'S4_history_CN_PMI_MFG', 'ok': True,
            'envelope': {'data': {'series': env}}}
    return ro._evaluate_data_requirements(
        ['CN_PMI_MFG'], [step], {'target_date': as_of}, [],
        question=question,
        registry={'CN_PMI_MFG': {'frequency': 'monthly'}})[0]


dC, dE, dF = _new_root(), _new_root(), _new_root()
_run_round(dC, _cn_item(C_D, C_V))
_run_round(dE, _cn_item(E_D, E_V))
_run_round(dF, _cn_item(_RD, _RV))

# A1「过去十八月」(无「个」)→ 与「十八个月」同窗 18;不再当未限定误交付
rA1 = eval_item(dF, '研究过去十八月 CN_PMI_MFG 的变化', '2026-11-17')
wA1 = win_of(rA1)
_wA1 = ro._question_window('研究过去十八月 X')
check('A1 过去十八月 → 18 月显式窗+可交付(基线=未限定误交付)',
      _wA1.get('kind') == 'relative_months' and _wA1.get('months') == 18
      and wA1.get('kind') == 'relative_months'
      and wA1.get('start') == '2025-05-17' and wA1.get('end') == '2026-11-17'
      and wA1.get('n_in_window') >= wA1.get('n_floor_in_window', 0)
      and rA1['outcome'] == 'satisfied',
      f"kind={_wA1.get('kind')} m={_wA1.get('months')} "
      f"n_in={wA1.get('n_in_window')} outcome={rA1['outcome']}")

# A2 畸形数量/零值 → 明确拒绝;全角 → 正确解析为 20 年约束(不再未限定)
for _tag, _q, _sub in (
        ('近1.2.3年', '研究近1.2.3年 CN_PMI_MFG 的变化', '残缺数量'),
        ('过去0个月', '研究过去0个月 CN_PMI_MFG 的变化', '零值')):
    _r = eval_item(dF, _q, '2026-11-17')
    _w = ro._question_window(_q)
    check(f'A2 {_tag} → unparseable({_sub}),F 全史也不交付',
          _w.get('kind') == 'unparseable' and _r['outcome'] != 'satisfied',
          f"kind={_w.get('kind')} outcome={_r['outcome']}")
rA2fw = eval_item(dF, '研究近２０年 CN_PMI_MFG 的变化', '2026-11-17')
_wA2fw = ro._question_window('研究近２０年 X')
check('A2 近２０年(全角) → 正确解析 years=20(不再未限定放行)',
      _wA2fw.get('kind') == 'relative' and _wA2fw.get('years') == 20
      and win_of(rA2fw).get('start') == '2006-11-17'
      and rA2fw['outcome'] != 'satisfied',
      f"kind={_wA2fw.get('kind')} y={_wA2fw.get('years')} "
      f"outcome={rA2fw['outcome']}")

# A3「过去六个月半」未消费后缀 → 拒绝(不得静默只取六个月)
rA3 = eval_item(dC, '研究过去六个月半 CN_PMI_MFG 的变化', '2026-11-17')
_wA3 = ro._question_window('研究过去六个月半 X')
check('A3 六个月半 → unparseable(半后缀必须消费)',
      _wA3.get('kind') == 'unparseable' and rA3['outcome'] != 'satisfied'
      and win_of(rA3).get('months') != 6,
      f"kind={_wA3.get('kind')} outcome={rA3['outcome']}")

# A4「过去1.1年」13.2 非整月 → 拒绝(不 round 成 13)
rA4 = eval_item(dC, '研究过去1.1年 CN_PMI_MFG 的变化', '2026-11-17')
_wA4 = ro._question_window('研究过去1.1年 X')
check('A4 1.1年=13.2月非整 → unparseable(不取整不缩短)',
      _wA4.get('kind') == 'unparseable'
      and '13.2' in str(_wA4.get('reason'))
      and win_of(rA4).get('months') != 13 and rA4['outcome'] != 'satisfied',
      f"kind={_wA4.get('kind')} reason={_wA4.get('reason')}")

# A5 明确研究年份 → 显式日历窗(2024 有 12 点→满足;C 缺 2024→阻断)
rA5f = eval_item(dF, '研究2024年 CN_PMI_MFG 的变化', '2026-11-17')
rA5c = eval_item(dC, '研究2024年 CN_PMI_MFG 的变化', '2026-11-17')
wA5f = win_of(rA5f)
check('A5 2024年 → 显式窗 2024-01-01..12-31: F n_in=12 满足, C 阻断',
      wA5f.get('start') == '2024-01-01' and wA5f.get('end') == '2024-12-31'
      and wA5f.get('n_in_window') == 12 and rA5f['outcome'] == 'satisfied'
      and rA5c['outcome'] != 'satisfied',
      f"win={wA5f} F={rA5f['outcome']} C={rA5c['outcome']}")

# A6 多范围(相对+年份)→ 冲突阻断+拆分提示,不再只查其一
rA6 = eval_item(dC, '分别研究过去六个月和2024年 CN_PMI_MFG 的变化',
                '2026-11-17')
_wA6 = ro._question_window('分别研究过去六个月和2024年 X')
check('A6 六个月+2024年 → unparseable+拆分提示',
      _wA6.get('kind') == 'unparseable'
      and '拆分' in str(_wA6.get('hint')) and rA6['outcome'] != 'satisfied',
      f"kind={_wA6.get('kind')} outcome={rA6['outcome']}")

# ══════════════════════════════════════════════════════════════════
print('§B 性质 a/b/c(指令三.6)')

# B1 性质a: 增加必要范围要求不能让覆盖不足的数据变为可交付
# (C 未限定=22点≥族下限=满足; 加 2024 年约束后窗内 0 点=阻断)
_rC0 = eval_item(dC, '研究 CN_PMI_MFG 的变化', '2026-11-17')
check('B1a C 未限定=满足(对照)', _rC0['outcome'] == 'satisfied',
      f"outcome={_rC0['outcome']}")
check('B1b C+2024年窗=阻断(收紧只可能更严,不可能更宽)',
      rA5c['outcome'] == 'insufficient_coverage',
      f"outcome={rA5c['outcome']}")
_rF27 = eval_item(dF, '研究2027年 CN_PMI_MFG 的变化', '2026-11-17')
check('B1c F 全史+2027年(未来窗 0 点)=阻断——完整历史不豁免窗口检查',
      _rF27['outcome'] == 'insufficient_coverage',
      f"outcome={_rF27['outcome']}")

# B2 性质b: 等价表达同一窗口(或同一明确拒绝)
_EQ = ['研究过去十八个月 X', '研究过去十八月 X', '研究过去一年半 X',
       '研究过去1.5年 X', '研究过去１.５年 X']
_wEQ = [ro._question_window(q) for q in _EQ]
_rEQ = [eval_item(dF, q.replace(' X ', ' CN_PMI_MFG '), '2026-11-17')
        for q in _EQ]
_setEQ = {(w.get('kind'), w.get('months')) for w in _wEQ}
_outEQ = {r['outcome'] for r in _rEQ}
_winEQ = {(win_of(r).get('start'), win_of(r).get('end')) for r in _rEQ}
check('B2 十八月=十八个月=一年半=1.5年=全角1.5 → 同窗同界同结论',
      _setEQ == {('relative_months', 18)} and len(_outEQ) == 1
      and len(_winEQ) == 1 and 'satisfied' in _outEQ,
      f"parses={_setEQ} outcomes={_outEQ} windows={_winEQ}")
_wBAD2 = [ro._question_window(q) for q in
          ('研究过去6个月半 X', '研究过去1.1年 X', '研究近1.2.3年 X')]
check('B2b 同类畸形族 → 一致明确拒绝(无一静默放行)',
      all(w.get('kind') == 'unparseable' for w in _wBAD2),
      f"kinds={[w.get('kind') for w in _wBAD2]}")

# B3 性质c: 完整历史足够时也必须检查窗口是否正确(窗界逐字段)
check('B3c F+2024年窗字段逐位(12 点/下限 6/起止精确)',
      wA5f.get('n_in_window') == 12 and wA5f.get('n_floor_in_window') == 6
      and wA5f.get('basis') is not None,
      f"win={wA5f}")

# ══════════════════════════════════════════════════════════════════
print('§C 裸日期/年份族(明确年份纳入要求)')


def _ck(tag, q, kind, start=None, end=None):
    w = ro._question_window(q)
    ok = w.get('kind') == kind and (start is None or w.get('start') == start) \
        and (end is None or w.get('end') == end)
    check(f'C {tag}', ok, f"kind={w.get('kind')} {w.get('start')}..{w.get('end')}")


_ck('2024年→日历年窗', '研究2024年 X', 'explicit', '2024-01-01', '2024-12-31')
_ck('全角２０２４年', '研究２０２４年 X', 'explicit', '2024-01-01', '2024-12-31')
_ck('2026年10月→月窗', '研究2026年10月 X', 'explicit', '2026-10-01', '2026-10-31')
_ck('2026-10→月窗', '研究2026-10 X', 'explicit', '2026-10-01', '2026-10-31')
_ck('2026/10→月窗', '研究2026/10 X', 'explicit', '2026-10-01', '2026-10-31')
_ck('2026-10-15→日窗', '研究2026-10-15 X', 'explicit', '2026-10-15', '2026-10-15')
_ck('2026年10月15日→日窗', '研究2026年10月15日 X', 'explicit',
    '2026-10-15', '2026-10-15')
_ck('20261015→日窗', '研究20261015 X', 'explicit', '2026-10-15', '2026-10-15')
_ck('2024年13月→拒绝(非法月)', '研究2024年13月 X', 'unparseable')
_ck('2024和2025→并年区间(既档X和Y)', '研究2024年和2025年 X', 'explicit',
    '2024-01-01', '2025-12-31')
wC11 = ro._question_window('研究2026年内 X')
check('C 2026年内(四位数字年形态)→ 拒绝(既档语义保持)',
      wC11.get('kind') == 'unparseable', f"kind={wC11.get('kind')}")

# ══════════════════════════════════════════════════════════════════
print('§D 未支持单位族(变体探测补口)')


def _ckd(tag, q):
    w = ro._question_window(q)
    check(f'D {tag} → unparseable', w.get('kind') == 'unparseable',
          f"kind={w.get('kind')}")


_ckd('过去季度(裸)', '研究过去季度 X 的变化')
_ckd('近季度', '研究近季度 X 的变化')
_ckd('近一季度', '研究近一季度 X 的变化')
_ckd('过去星期(裸)', '研究过去星期 X 的变化')
_ckd('近30天', '研究近30天 X 的变化')
_ckd('近三周', '研究近三周 X 的变化')
# 单字单位裸形刻意不收(资产名/常用词误伤),断言不误伤:
check('D 过去日本央行(裸「日」不收)→ 未限定',
      ro._question_window('研究过去日本央行政策的变化') is None)
check('D 过去天量成交(裸「天」不收)→ 未限定',
      ro._question_window('研究过去天量成交的变化') is None)

# ══════════════════════════════════════════════════════════════════
print('§E 护栏与合法对照(既档语义保持)')

check('E1 资产名护栏: 十年期美债≠近十年',
      ro._question_range_years('研究十年期美债收益率的变化') is None)
check('E2 合法无范围 → None',
      ro._question_window('研究 X 与 Y 的相关性') is None)
_rF0 = eval_item(dF, '研究 CN_PMI_MFG 的变化', '2026-11-17')
check('E3 F 无范围(未限定族下限)→ 满足', _rF0['outcome'] == 'satisfied')
_wE4 = ro._question_window('截至2026-10-15 研究 X 的变化')
check('E4 截至→单侧终界窗(R8-02 既档)',
      _wE4.get('kind') == 'explicit' and _wE4.get('end') == '2026-10-15')
_wE5 = ro._question_window('研究去年 X 的变化')
check('E5 去年→calendar_year(R8 既档)', _wE5.get('kind') == 'calendar_year')
check('E6 半年=6 个月(R10 既档)',
      ro._question_window('研究近半年 X').get('months') == 6)
check('E7 十二个月双时点研究(R11 A 案既档)仍拒',
      ro._question_window('研究2025年6月和2025年12月的 CN_PMI_MFG') is not None)

# ══════════════════════════════════════════════════════════════════
print('§F P1-② 来源结构不完整禁止误删证据(正式 build_snapshot 基线)')

TGT_S = '20261117'
NOW_S = datetime(2026, 11, 18, 12, 0)
B_OLD, B_REP = b'{"old": 1}', b'{"rep": 1}'


def _sbuild(mutator=None, post_write=None):
    root = tempfile.mkdtemp(prefix='r12s_')
    daily = os.path.join(root, 'data', 'daily')
    os.makedirs(daily)
    for ch in ('global', 'macro', 'china', 'rate_economy'):
        with open(os.path.join(daily, f'{ch}_{TGT_S}.json'), 'w',
                  encoding='utf-8') as f:
            json.dump({'data': {}, 'saved_at': '2026-11-17T02:00:00'}, f)
    open(os.path.join(daily, 'macro_20260301.json'), 'wb').write(B_OLD)
    open(os.path.join(daily, 'macro_20260315.json'), 'wb').write(B_REP)
    snap = sb.build_snapshot(target_ymd=TGT_S, data_dir=daily, out_dir=daily,
                             trusted_root=root, write=False)
    assert isinstance(snap.get('sources_status'), dict), '正式快照基线失败'
    if mutator:
        mutator(snap)
    with open(os.path.join(daily, f'research_snapshot_{TGT_S}.json'), 'w',
              encoding='utf-8') as f:
        json.dump(snap, f, ensure_ascii=False, indent=1)
    if post_write:
        post_write(daily)
    return root, daily


def _gz(daily, name):
    with gzip.open(os.path.join(daily, 'archive', name + '.gz'), 'rb') as f:
        return f.read()


def _scen(tag, expect_stop, **kw):
    """expect_stop=True: 损坏面→删除停止+字节可恢复; False: 正常清理对照。"""
    root, daily = _sbuild(**kw)
    rep = drt.prune_daily_archives(daily, keep_days=90, now=NOW_S)
    refs, probs = drt.research_referenced_files(daily)
    gone = not os.path.exists(os.path.join(daily, 'macro_20260301.json'))
    try:
        rec = (not gone) or _gz(daily, 'macro_20260301.json') == B_OLD
    except FileNotFoundError:
        rec = False
    if expect_stop:
        ok = bool(probs) and rep['deleted'] == [] and rec \
            and 'macro_20260301.json' in rep['deletion_skipped']
    else:
        ok = probs == [] and rep['deleted'] == ['macro_20260301.json']
    check(f'F {tag}', ok,
          f"probs={len(probs)} deleted={rep['deleted']} "
          f"skipped={rep['deletion_skipped']} rec={rec}")
    shutil.rmtree(root, ignore_errors=True)


_scen('S0 干净快照(对照,正常删)', False)


def _m1(s):
    del s['sources_status']


def _m2(s):
    s['sources_status'] = []


def _m3(s):
    s['sources_status']['macro'] = 'EXACT'


def _m4(s):
    s['sources_status']['macro'] = {'status': 'EXACT', 'file_date': TGT_S}


_scen('S1 sources_status 缺失', True, mutator=_m1)
_scen('S2 sources_status=[]', True, mutator=_m2)
_scen('S3 macro 通道→字符串', True, mutator=_m3)
_scen('S4 macro EXACT file=null', True, mutator=_m4)
_scen('S5 合法MISSING通道(对照,正常删)', False,
      mutator=lambda s: s['sources_status'].update(china={'status': 'MISSING'}))
_scen('S6 JSON 截断', True,
      post_write=lambda d: open(
          os.path.join(d, f'research_snapshot_{TGT_S}.json'), 'wb').write(
          open(os.path.join(d, f'research_snapshot_{TGT_S}.json'),
               'rb').read()[:20]))
_scen('S7 global file=123(错误字段类型)', True,
      mutator=lambda s: s['sources_status']['global'].update(file=123))
check('F 权威校验复用: research_referenced_files 内联调用 '
      'research_provenance.sources_status_problems(不另建弱规则)',
      'research_provenance' in open(os.path.join(
          ROOT, 'scripts', 'data_retention.py')).read()
      and 'sources_status_problems' in open(os.path.join(
          ROOT, 'scripts', 'data_retention.py')).read())

# ══════════════════════════════════════════════════════════════════
print('§G 生产 report/archive 双门(同判据源)')


def make_run(tmp, name, question, req_items):
    make_run.seq += 1
    rd = os.path.join(tmp, name)
    os.makedirs(rd, exist_ok=True)
    rows = [{'metric_id': 'TEST_M%d' % i, 'value': 1.0 * i, 'unit': 'x',
             'observation_date': '2026-11-09', 'quality_status': 'OK',
             'source': {'id': 'src%d' % i, 'kind': 'synthetic'}}
            for i in range(2)]
    report = {
        'schema_version': '2.0', 'pipeline_version': 't',
        'run': {'question': question,
                'ts_utc': '20261118T23%04dZ' % make_run.seq,
                'git_head': 'synthetic', 'degradation_policy': {}},
        'steps': [], 'fanout': {},
        'layers': {
            'L1_事实层': {'rows': rows, 'available': True, 'n': 2,
                         'note': '合成: 无事实行'},
            'L2_机构观点层': {'views': {'available': False, 'n': 0,
                                        'note': '合成: 观点库缺席'}},
            'L3_AI推断层': {'produced': True, 'attribution': 'ai_inferred',
                           'note': '合成: L3 注记'},
            'L4_条件情景层': {'produced': True, 'attribution': 'ai_inferred',
                           'note': '合成: L4 注记'}},
        'evidence_index': [{'kind': 'metric', 'ref': 'TEST_M0@2026-11-09'},
                           {'kind': 'metric', 'ref': 'TEST_M1@2026-11-09'}],
        'notes': [], 'run_ok': True,
        'agent_judgment': {
            'attached': True, 'judgment_file': 'judgment.json',
            'validation': {'passed': True, 'violations': []},
            'run_ok_at_attach': True, 'allow_failed_run': False}}
    report['run']['data_requirements'] = {
        'frozen_at': 'plan(采集前冻结;分类与规格不随采集结果改判)',
        'items': req_items,
        'optional_face': {'tier': 'optional'}}
    json.dump(report, open(os.path.join(rd, 'report.json'), 'w',
                           encoding='utf-8'), ensure_ascii=False)
    json.dump({'schema_version': aj.JUDGMENT_SCHEMA_VERSION,
               'agent_declaration': {'role': 'synthetic'},
               'l3': {'claims': []}, 'l4': {'scenarios': []}},
              open(os.path.join(rd, 'agent_judgment.json'), 'w',
                   encoding='utf-8'), ensure_ascii=False)
    open(os.path.join(rd, 'report.md'), 'w', encoding='utf-8').write(
        ro._render_md(report))
    json.dump({'n': 1, 'note': 'views 库在场', 'views': [
        {'view_id': 'V-2026-001', 'institution_name': '机构A',
         'publish_date': '2026-11-01', 'report_title': '标题',
         'core_views': ['主张'], 'forecasts': [], 'risk_factors': []}]},
        open(os.path.join(rd, 'views_digest.json'), 'w',
             encoding='utf-8'), ensure_ascii=False)
    return rd


make_run.seq = 0


def stage_report(rd, engine_root):
    r = subprocess.run(
        [sys.executable, 'ia_cli.py', 'research-one', '--stage', 'report',
         '--report-dir', rd, '--engine-root', engine_root],
        cwd=ROOT, capture_output=True, text=True, timeout=180)
    return json.loads(r.stdout)['data']


def stage_archive(rd, engine_root, arc):
    return subprocess.run(
        [sys.executable, 'ia_cli.py', 'research-one', '--stage', 'archive',
         '--report-dir', rd, '--engine-root', engine_root,
         '--archive-dir', arc],
        cwd=ROOT, capture_output=True, text=True, timeout=180)


tmpG = tempfile.mkdtemp(prefix='r12gateG_')
eroot = os.path.join(tmpG, 'engine')
os.makedirs(os.path.join(eroot, 'config'), exist_ok=True)
shutil.copy(os.path.join(ROOT, 'config', 'metric_registry.json'),
            os.path.join(eroot, 'config', 'metric_registry.json'))

# G1 十八月误交付案(基线 BUG 面)→ 现为合法 18 月窗,F 全史可交付(正例)
rG1 = eval_item(dF, '研究过去十八月 CN_PMI_MFG 的变化', '2026-11-17')
rdG1 = make_run(tmpG, 'g1', '研究过去十八月 CN_PMI_MFG 的变化', [rG1])
aj.record_semantic_verdict(eroot, rdG1, 'UPHELD', 'R12-GATE')
eG1 = stage_report(rdG1, eroot)
check('G1 过去十八月@F → 正确 18 月窗可交付(不再未限定误判)',
      eG1.get('deliverable') is True
      and win_of(rG1).get('start') == '2025-05-17',
      f"deliv={eG1.get('deliverable')} start={win_of(rG1).get('start')}")

# G2-G5 阻断面: report 拒 + archive 拒
_GCASES = [
    ('g2', '研究近1.2.3年 CN_PMI_MFG 的变化',
     eval_item(dF, '研究近1.2.3年 CN_PMI_MFG 的变化', '2026-11-17'),
     '畸形数量'),
    ('g3', '研究过去六个月半 CN_PMI_MFG 的变化',
     eval_item(dC, '研究过去六个月半 CN_PMI_MFG 的变化', '2026-11-17'),
     '未消费后缀'),
    ('g4', '研究过去1.1年 CN_PMI_MFG 的变化',
     eval_item(dC, '研究过去1.1年 CN_PMI_MFG 的变化', '2026-11-17'),
     '非整月round'),
    ('g5', '分别研究过去六个月和2024年 CN_PMI_MFG 的变化',
     eval_item(dC, '分别研究过去六个月和2024年 CN_PMI_MFG 的变化',
               '2026-11-17'),
     '多范围只查其一'),
    ('g6', '研究2024年 CN_PMI_MFG 的变化',
     eval_item(dC, '研究2024年 CN_PMI_MFG 的变化', '2026-11-17'),
     '明确年份窗内零覆盖'),
    ('g7', '研究过去季度 CN_PMI_MFG 的变化',
     eval_item(dF, '研究过去季度 CN_PMI_MFG 的变化', '2026-11-17'),
     '未支持单位'),
]
for _n, _q, _r, _tag in _GCASES:
    _rd = make_run(tmpG, _n, _q, [_r])
    _e = stage_report(_rd, eroot)
    _a = stage_archive(_rd, eroot, os.path.join(tmpG, 'arc_' + _n))
    check(f'G {_tag}({(_q[:14])}…) → report 拒+archive 拒',
          _e.get('deliverable') is False
          and _e.get('blocked_class') == 'required_data_missing'
          and _a.returncode != 0,
          f"bc={_e.get('blocked_class')} rc={_a.returncode}")

# ══════════════════════════════════════════════════════════════════
print(f"\nR12 gate: {PASS} PASS / {FAIL} FAIL")
sys.exit(1 if FAIL else 0)
