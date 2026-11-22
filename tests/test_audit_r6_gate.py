#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit-R6 第六轮审计修复回归: 时间窗口覆盖校验/CN 全史正式采集/裁决链共用校验。

§W(R6-01): 数据要求校验用真实时间边界——任务窗=研究时点(target_date)
          倒推 N 年,序列须跨窗(边界容差按频率族)+窗内有效观测≥半额;
          频率自权威注册表取(快照路径不丢频率);未知频率/时点不可核验
          且问题限定范围→阻断(不回落宽松);总量不替代窗口归属
          (外审反例1: 12 个日频观测满足"近十年";反例2: 3000 个
          1990-1998 观测满足"近十年");真实完整历史/月频发布滞后不误拒;
          report 与 archive 同一套判定。
§C(R6-02): 中国月度全史正式采集——_macro_month_rows 归一(年月份→
          统计期月首锚);merge_cn_history 三态(fresh/carry_forward/
          absent): 成功=provenance 随档(来源/获取时间/覆盖/修订口径);
          失败=最近档续存并如实披露(fresh=False+来源档,fetched_at
          不冒充);净环境失败=如实缺席不造史;同日重跑续存当日档;
          save_macro 档内 cn_history 状态键;美国刷新(FRED 面)不清除
          CN 序列;registry calc 注记指向正式生成器。
§V(R6-03): 裁决链新旧格式共用校验——删首档 revision/predecessor+
          run_ts=WRONG_RUN+overall=UNKNOWN_VERDICT(越表词)阻断;
          digest_algorithm 非现行逐档阻断;合法旧链(legacy 头)+
          复审链照常通过;report/archive 门一致。

全部经生产写档函数/生产判定函数构造(record_semantic_verdict/
_evaluate_data_requirements/merge_cn_history/ia_cli research-one
阶段真跑);判定=逐 check 打印+exit code。
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import agent_judgment as aj          # noqa: E402
import research_orchestrator as ro   # noqa: E402
import china_market_collector as cmc  # noqa: E402
import macro_collector as mc         # noqa: E402

PASS, FAIL = 0, 0
_RUN_SEQ = 600


def check(name, cond, detail=''):
    global PASS, FAIL
    print(f"  {'✅' if cond else '❌'} {name}" + (f" — {detail}" if detail and not cond else ''))
    PASS = PASS + (1 if cond else 0)
    FAIL = FAIL + (0 if cond else 1)


def make_run(tmp, name, *, run_ok=True, l1_rows=2, produced=True,
             req_items=None, allow_flag=False, steps=None):
    """合成已挂判定 run(结构面与生产 attach 后同形;steps 覆写=失败步面)。"""
    global _RUN_SEQ
    _RUN_SEQ += 1
    run_ts = '20261117T16%04dZ' % _RUN_SEQ
    rd = os.path.join(tmp, name)
    os.makedirs(rd, exist_ok=True)
    rows = [{'metric_id': 'TEST_M%d' % i, 'value': 1.0 * i, 'unit': 'x',
             'observation_date': '2026-11-09', 'quality_status': 'OK',
             'source': {'id': 'src%d' % i, 'kind': 'synthetic'}}
            for i in range(l1_rows)]
    report = {
        'schema_version': '2.0', 'pipeline_version': 't',
        'run': {'question': 'Audit-R6 回归合成问题', 'ts_utc': run_ts,
                'git_head': 'synthetic', 'degradation_policy': {}},
        'steps': steps if steps is not None else [], 'fanout': {},
        'layers': {
            'L1_事实层': {'rows': rows, 'available': l1_rows > 0,
                         'n': l1_rows, 'note': '合成: 无事实行'},
            'L2_机构观点层': {'views': {'available': False, 'n': 0,
                                        'note': '合成: 观点库缺席'}},
            'L3_AI推断层': {'produced': produced, 'attribution': 'ai_inferred',
                           'note': '合成: L3 注记'},
            'L4_条件情景层': {'produced': produced, 'attribution': 'ai_inferred',
                           'note': '合成: L4 注记'}},
        'evidence_index': [{'kind': 'metric', 'ref': 'TEST_M0@2026-11-09'},
                           {'kind': 'metric', 'ref': 'TEST_M1@2026-11-09'}
                           ][:max(l1_rows, 0)],
        'notes': [], 'run_ok': run_ok,
        'agent_judgment': {
            'attached': True, 'judgment_file': 'judgment.json',
            'validation': {'passed': True, 'violations': []},
            'run_ok_at_attach': True if run_ok else False,
            'allow_failed_run': bool(allow_flag and not run_ok)}}
    if req_items is not None:
        report['run']['data_requirements'] = {
            'frozen_at': 'plan(采集前冻结;分类与规格不随采集结果改判)',
            'items': req_items,
            'optional_face': {'tier': 'optional'}}
    json.dump(report, open(os.path.join(rd, 'report.json'), 'w',
                           encoding='utf-8'), ensure_ascii=False)
    json.dump({'schema_version': aj.JUDGMENT_SCHEMA_VERSION,
               'agent_declaration': {'role': 'synthetic'},
               'l3': {'claims': []}, 'l4': {'scenarios': []}},
              open(os.path.join(rd, 'agent_judgment.json'), 'w', encoding='utf-8'),
              ensure_ascii=False)
    open(os.path.join(rd, 'report.md'), 'w', encoding='utf-8').write(
        ro._render_md(report))
    json.dump({'n': 1, 'note': 'views 库在场', 'views': [
        {'view_id': 'V-2026-001', 'institution_name': '机构A',
         'publish_date': '2026-11-01', 'report_title': '标题',
         'core_views': ['主张'], 'forecasts': [], 'risk_factors': []}]},
        open(os.path.join(rd, 'views_digest.json'), 'w', encoding='utf-8'),
        ensure_ascii=False)
    return rd


def stage_report(rd, engine_root):
    r = subprocess.run(
        [sys.executable, 'ia_cli.py', 'research-one', '--stage', 'report',
         '--report-dir', rd, '--engine-root', engine_root],
        cwd=ROOT, capture_output=True, text=True, timeout=180)
    e = json.loads(r.stdout)
    d = e['data']
    d['_warnings'] = e.get('warnings') or []
    return d


def stage_archive(rd, engine_root, arc):
    return subprocess.run(
        [sys.executable, 'ia_cli.py', 'research-one', '--stage', 'archive',
         '--report-dir', rd, '--engine-root', engine_root,
         '--archive-dir', arc],
        cwd=ROOT, capture_output=True, text=True, timeout=180)


def state_of(rd, engine_root):
    rj = json.load(open(os.path.join(rd, 'report.json'), encoding='utf-8'))
    return aj._semantic_review_state(rj, engine_root, rd)


def rewrite(path, **over):
    d = json.load(open(path, encoding='utf-8'))
    for k, v in list(over.items()):
        if v is DELETE:
            d.pop(k, None)
        else:
            d[k] = v
    json.dump(d, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    return d


class _Del:
    pass


DELETE = _Del()


def daterange(d0, d1, days=1):
    out, d = [], d0
    while d <= d1:
        out.append(d.isoformat())
        d += timedelta(days=days)
    return out


def monthrange(y0, m0, y1, m1):
    out, y, m = [], y0, m0
    while (y, m) <= (y1, m1):
        out.append('%04d-%02d-01' % (y, m))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


print('═' * 64)
print('Audit-R6: 时间窗口覆盖 / CN 全史正式采集 / 裁决链共用校验')
print('═' * 64)

tmp = tempfile.mkdtemp(prefix='r6gate_')
eroot = os.path.join(tmp, 'engine')
os.makedirs(os.path.join(eroot, 'config'), exist_ok=True)
shutil.copy(os.path.join(ROOT, 'config', 'metric_registry.json'),
            os.path.join(eroot, 'config', 'metric_registry.json'))

# ══ §W: R6-01 时间范围与历史覆盖校验 ═══════════════════════════════
print('§W 任务窗口真实时间边界(总量不替代窗口归属)')

AS_OF = '2026-11-17'
snapW = lambda store: {'target_date': AS_OF, 'series_store': store}  # noqa: E731
REG_DXY = {'DXY': {'frequency': 'daily'}}


def store(mid, dates):
    return {mid: {'dates': dates,
                  'values': [1.0] * len(dates)}}


# W1 反例1(外审): 近十年问题,快照仅 12 个日频观测(16 天),基线 satisfied
w1 = ro._evaluate_data_requirements(
    ['DXY'], [], snapW(store('DXY', daterange(date(2026, 10, 27),
                                               date(2026, 11, 7)))), [],
    question='近十年 DXY 走势', registry=REG_DXY)[0]
check('W1 12 个日频观测/近十年 → 阻断(基线曾误放行)',
      w1['outcome'] == 'insufficient_coverage'
      and w1['spec']['min_observations'] == 2520
      and w1['spec']['frequency'] == 'daily',
      str(w1['spec']['min_observations']) + w1['outcome'])

# W2 反例2(外审): 3000 个观测全在 1990-01-01..1998-03-19,近十年窗 0 有效
# (R7-01: n_floor 钉值由 252×年数口径(1260)改为日历工作日期望×半额
#  ——窗 2016-11-17..2026-11-17 工作日 2609 → floor 1304;阻断行为不变)
w2 = ro._evaluate_data_requirements(
    ['DXY'], [], snapW(store('DXY', daterange(date(1990, 1, 1),
                                               date(1998, 3, 19)))), [],
    question='近十年 DXY 走势', registry=REG_DXY)[0]
_w2w = w2['spec']['window']
check('W2 3000 个 1990-1998 观测/近十年 → 窗口不归属阻断',
      w2['outcome'] == 'insufficient_coverage'
      and _w2w.get('n_in_window') == 0
      and _w2w.get('n_floor_in_window') == 1304
      and _w2w.get('expected_in_window') == 2609,
      str(_w2w))

# W3 正例: 真实完整十年日频(2016-11-20..2026-11-13)通过
w3 = ro._evaluate_data_requirements(
    ['DXY'], [], snapW(store('DXY', daterange(date(2016, 11, 20),
                                               date(2026, 11, 13)))), [],
    question='近十年 DXY 走势', registry=REG_DXY)[0]
check('W3 真实完整十年日频 → satisfied(不误拒完整历史)',
      w3['outcome'] == 'satisfied', w3['outcome_basis'][:60])

# W4 正例: 月频十年+末观测滞后 72 天(发布滞后容忍,研究时点 2026-11-12)通过
w4 = ro._evaluate_data_requirements(
    ['PM_M'], [], {'target_date': '2026-11-12',
                   'series_store': store('PM_M', monthrange(2016, 10, 2026, 9))},
    [], question='近十年 PM_M 走势',
    registry={'PM_M': {'frequency': 'monthly'}})[0]
check('W4 月频十年+末观测滞后 72 天 → satisfied(发布滞后不误拒)',
      w4['outcome'] == 'satisfied', w4['outcome_basis'][:60])

# W5 反例: 只覆盖后半窗(2019-06 起)总量超半额仍阻断(边界)
w5 = ro._evaluate_data_requirements(
    ['DXY'], [], snapW(store('DXY', daterange(date(2019, 6, 1),
                                               date(2026, 11, 13)))), [],
    question='近十年 DXY 走势', registry=REG_DXY)[0]
check('W5 2019-06 起的后半窗 → 窗起未覆盖阻断',
      w5['outcome'] == 'insufficient_coverage',
      w5['outcome_basis'][:60])

# W6 反例: 未知频率+问题限定范围 → 不回落宽松通过
w6 = ro._evaluate_data_requirements(
    ['UNK_M'], [], snapW(store('UNK_M', daterange(date(2020, 1, 1),
                                                  date(2026, 11, 7)))), [],
    question='近十年 UNK_M 走势', registry={})[0]
check('W6 未知频率+限定范围 → 阻断(窗口不可核验)',
      w6['outcome'] == 'insufficient_coverage',
      w6['outcome_basis'][:60])

# W7 反例: 研究时点不可核验(快照无 target_date)+限定范围 → 阻断
w7 = ro._evaluate_data_requirements(
    ['DXY'], [], {'series_store': store('DXY', daterange(
        date(2016, 11, 20), date(2026, 11, 13)))}, [],
    question='近十年 DXY 走势', registry=REG_DXY)[0]
check('W7 时点不可核验+限定范围 → 阻断',
      w7['outcome'] == 'insufficient_coverage', w7['outcome_basis'][:60])

# W8 正例: 未限定范围维持 max_available(CN 226 月全史不误拒)
w8 = ro._evaluate_data_requirements(
    ['CN_PMI_MFG'], [], snapW(store('CN_PMI_MFG',
                                    monthrange(2008, 1, 2026, 10))), [],
    question='CN_PMI_MFG 全史走势',
    registry={'CN_PMI_MFG': {'frequency': 'monthly'}})[0]
check('W8 未限定范围 226 月全史 → satisfied(max_available 口径保留)',
      w8['outcome'] == 'satisfied'
      and w8['spec']['window'] == 'max_available',
      str(w8['spec'].get('window')))

# W9 S4 信封面: 12 观测/近十年同样阻断(report 与 archive 同一判据源)
w9 = ro._evaluate_data_requirements(
    ['DXY'], [{'step': 'S4_history_DXY', 'ok': True,
               'envelope': {'data': {'series': {
                   'n': 12, 'source': '采集档', 'frequency': 'daily',
                   'first': '2026-10-27', 'last': '2026-11-07'}}}}],
    snapW({}), [], question='近十年 DXY 走势', registry=REG_DXY)[0]
check('W9 S4 信封 12 观测/近十年 → 阻断',
      w9['outcome'] == 'insufficient_coverage')

# W10 生产接线: run_research 调用面传权威注册表(S1 已装载面)
import inspect  # noqa: E402
# Audit-R31 任务2: run_research 拆为钉死包装层+_run_research_body 主体
# (三输入钉死+异常安全释放)——注册表接线在主体,锚随代码实构走
# (契约实质不变: S1 调用面传权威注册表)。
check('W10 run_research 传 registry=权威注册表',
      'registry=reg.get' in (inspect.getsource(ro.run_research)
                             + inspect.getsource(ro._run_research_body)))

# W11 report/archive 同判: 反例1 规格注入 run → 两门同拒
rdW = make_run(tmp, 'w11', req_items=[w1])
eW = stage_report(rdW, eroot)
aW = stage_archive(rdW, eroot, os.path.join(tmp, 'arcW'))
check('W11 窗口不满足 → report 拒交付+archive 拒归档(同一判据)',
      eW.get('deliverable') is False
      and eW.get('blocked_class') == 'required_data_missing'
      and aW.returncode != 0,
      f"bc={eW.get('blocked_class')} deliv={eW.get('deliverable')} "
      f"rc={aW.returncode}")

# ══ §C: R6-02 CN 月度全史正式采集(离线可注入面) ═══════════════════
print('§C CN 全史正式入口(生成/续存/披露)')


class _Df:
    """轻量 DataFrame 替身(iterrows 面),零 pandas 依赖。"""

    def __init__(self, rows):
        self._rows = rows

    def iterrows(self):
        return iter(enumerate(self._rows))

    def __len__(self):
        return len(self._rows)


c1 = cmc._macro_month_rows(_Df([
    {'月份': '2026年10月', '制造业-指数': 49.3},
    {'月份': '2026年9月', '制造业-指数': 50.1},
    {'月份': '2026年10月', '制造业-指数': None},
    {'月份': '坏行', '制造业-指数': 51.0},
    {'月份': '2026年8月', '制造业-指数': '49.4'}]), '月份', '制造业-指数')
check('C1 _macro_month_rows 年月份→月首锚+跳 NaN/坏行+升序',
      c1 == [('2026-08-01', 49.4), ('2026-09-01', 50.1),
             ('2026-10-01', 49.3)], str(c1))

ctmp = tempfile.mkdtemp(prefix='r6cn_')
os.makedirs(os.path.join(ctmp, 'daily'))
CN_ITEM = {'value': 49.3, 'date': '2026-10-01', 'prev': 50.1,
           'frequency': 'monthly', 'unit': 'index_point',
           'series': {'dates': ['2026-09-01', '2026-10-01'],
                      'values': [50.1, 49.3]},
           'provenance': {'source': 'akshare_em(macro_china_pmi)',
                          'fetched_at': '2026-11-16T01:00:00Z'}}


def plant_prior(dd, fname='macro_20261116.json', with_cn=True):
    data = {'HY_OAS': {'value': 3.1, 'date': '2026-11-13',
                       'frequency': 'daily'}}
    if with_cn:
        data['CN_PMI_MFG'] = json.loads(json.dumps(CN_ITEM))
    json.dump({'date': fname[6:14], 'data': data, 'alerts': [],
               'derived': {}},
              open(os.path.join(dd, 'daily', fname), 'w',
                   encoding='utf-8'), ensure_ascii=False)


FAKE = {'CN_PMI_MFG': {'date': '2026-10-01', 'value': 49.3, 'prev': 50.1,
                       'frequency': 'monthly', 'unit': 'index_point',
                       'series': {'dates': ['2026-09-01', '2026-10-01'],
                                  'values': [50.1, 49.3]},
                       'provenance': {
                           'source': 'akshare_em(macro_china_pmi)',
                           'fetched_at': '2026-11-17T02:00:00Z',
                           'coverage': {'n': 2, 'first': '2026-09-01',
                                        'last': '2026-10-01'},
                           'generated_by': 'fetch_macro_history'}}}
_orig_fetch = cmc.fetch_macro_history

# C2 fresh: 正式入口成功 → item+provenance 随档;不在采集面的键如实缺席
cmc.fetch_macro_history = lambda: json.loads(json.dumps(FAKE))
plant_prior(ctmp)
resC, stC = mc.merge_cn_history({'HY_OAS': {'value': 3.1}}, data_dir=ctmp)
check('C2 fresh 成功 → provenance 随档+缺键如实缺席',
      stC['CN_PMI_MFG']['mode'] == 'fresh'
      and resC['CN_PMI_MFG']['provenance']['fetched_at'] ==
      '2026-11-17T02:00:00Z'
      and stC['CN_NEW_LOANS']['mode'] == 'absent'
      and 'CN_NEW_LOANS' not in resC,
      json.dumps(stC, ensure_ascii=False))

# C3 carry_forward: 采集失败+前档在场 → 续存+披露(fresh=False,不冒充新采集)
cmc.fetch_macro_history = lambda: (_ for _ in ()).throw(
    RuntimeError('端点不可达'))
plant_prior(ctmp)
resC3, stC3 = mc.merge_cn_history({'HY_OAS': {'value': 3.2}}, data_dir=ctmp)
_prov3 = resC3['CN_PMI_MFG']['provenance']
check('C3 采集失败 → 最近档续存+fresh=False+来源档披露+原 fetched_at 保真',
      stC3['CN_PMI_MFG']['mode'] == 'carry_forward'
      and _prov3['fresh'] is False
      and _prov3['carry_forward_from'] == 'macro_20261116.json'
      and _prov3['fetched_at'] == '2026-11-16T01:00:00Z',
      json.dumps(stC3, ensure_ascii=False))

# C4 净环境失败 → 如实缺席(不造史/不 0 填充)
c4tmp = tempfile.mkdtemp(prefix='r6cn4_')
os.makedirs(os.path.join(c4tmp, 'daily'))
resC4, stC4 = mc.merge_cn_history({}, data_dir=c4tmp)
check('C4 净环境失败 → 双键 absent,零补造',
      stC4['CN_PMI_MFG']['mode'] == 'absent'
      and stC4['CN_NEW_LOANS']['mode'] == 'absent'
      and not set(resC4) & {'CN_PMI_MFG', 'CN_NEW_LOANS'})

# C5 save_macro: cn_history 状态键入档;旧调用面(不传)不写键(另目录隔离)
# (save_macro 以运行当日命名采集档——当日动态,防跨午夜日期炸弹)
_TODAY_F = 'macro_' + date.today().strftime('%Y%m%d') + '.json'
mc.DATA_DIR = ctmp
mc.save_macro(resC3, [], {}, cn_history=stC3)
dC5 = json.load(open(os.path.join(ctmp, 'daily', _TODAY_F),
                     encoding='utf-8'))
mc.DATA_DIR = c4tmp
mc.save_macro({'HY_OAS': {'value': 1.0}}, [], {})
dC5b = json.load(open(os.path.join(c4tmp, 'daily', _TODAY_F),
                      encoding='utf-8'))
check('C5 档内 cn_history 状态键(传则写/不传不写)',
      dC5['cn_history']['CN_PMI_MFG']['mode'] == 'carry_forward'
      and dC5['data']['CN_PMI_MFG']['series']['dates'] ==
      ['2026-09-01', '2026-10-01']
      and 'cn_history' not in dC5b)

# C6 美国刷新不清 CN: 再来一轮 FRED-only 结果+CN 失败 → 档内 CN 序列仍在
resC6, stC6 = mc.merge_cn_history({'HY_OAS': {'value': 3.3}}, data_dir=ctmp)
check('C6 美国刷新轮(FRED 面+CN 失败) → CN 序列仍在档(遮蔽缺陷关闭)',
      resC6['CN_PMI_MFG']['series']['dates'][-1] == '2026-10-01'
      and stC6['CN_PMI_MFG']['from_file'] == _TODAY_F
      and resC6['HY_OAS']['value'] == 3.3,
      json.dumps(stC6.get('CN_PMI_MFG'), ensure_ascii=False))

# C7 同日重跑: 续存源=当日已写档(更新鲜优先)
check('C7 同日重跑续存当日档',
      stC6['CN_PMI_MFG']['from_file'] == _TODAY_F)

# C8 registry calc 注记指向正式生成器(R5 临时 addendum 废止)
regC = json.load(open(os.path.join(ROOT, 'config',
                                   'metric_registry.json'),
                      encoding='utf-8'))
calcC = {m['metric_id']: m.get('calc', '') for m in regC['metrics']}
check('C8 registry 两 CN 条目 calc 指正式生成器',
      'fetch_macro_history' in calcC.get('CN_PMI_MFG', '')
      and 'fetch_macro_history' in calcC.get('CN_NEW_LOANS', '')
      and 'merge_cn_history' in calcC.get('CN_PMI_MFG', ''))
cmc.fetch_macro_history = _orig_fetch

# ══ §V: R6-03 裁决链新旧格式共用校验 ═══════════════════════════════
print('§V 裁决链共用校验(任务身份/词表/算法版本逐档)')


def chain3(name):
    """生产写路径构造三档链(REVISE→REVISE→UPHELD,档间内容合法演进)。"""
    rd = make_run(tmp, name)
    aj.record_semantic_verdict(eroot, rd, 'REVISE', 'R6-SEAT')
    rp = os.path.join(rd, 'report.json')
    d = json.load(open(rp, encoding='utf-8'))
    d['notes'] = ['第一轮修订注记']
    json.dump(d, open(rp, 'w', encoding='utf-8'), ensure_ascii=False)
    aj.record_semantic_verdict(eroot, rd, 'REVISE', 'R6-SEAT')
    d = json.load(open(rp, encoding='utf-8'))
    d['notes'] = ['第二轮修订注记']
    json.dump(d, open(rp, 'w', encoding='utf-8'), ensure_ascii=False)
    aj.record_semantic_verdict(eroot, rd, 'UPHELD', 'R6-SEAT')
    return rd


def verdicts_of(rd):
    run_ts = json.load(open(os.path.join(rd, 'report.json'),
                            encoding='utf-8'))['run']['ts_utc']
    return aj._verdicts_for_run(eroot, run_ts)


# V0 三档链健全(生产写路径)
rdV0 = chain3('v0')
sV0 = state_of(rdV0, eroot)
check('V0 三档链(生产写) → UPHELD fresh',
      sV0['verdict'] == 'UPHELD' and sV0['fresh'] is True
      and sV0['error'] is None, str(sV0)[:120])

# V1 反例1(外审): 首档删 revision/predecessor+run_ts=WRONG_RUN+
#    overall=UNKNOWN_VERDICT → 共用校验拦(基线曾误放行)
rdV1 = chain3('v1')
v1path = verdicts_of(rdV1)[0][0]
rewrite(v1path, revision=DELETE, predecessor=DELETE,
        run_ts='20260101T00000000Z', overall='UNKNOWN_VERDICT')
sV1 = state_of(rdV1, eroot)
check('V1 首档冒充旧形+错 run 档+越表词 → invalid_record 阻断',
      sV1['verdict'] is None and '越席位词表' in str(sV1['error']),
      str(sV1)[:160])

# V2 反例2(外审): 首档 digest_algorithm=UNKNOWN_ALGORITHM → 逐档拦
rdV2 = chain3('v2')
v2path = verdicts_of(rdV2)[0][0]
rewrite(v2path, digest_algorithm='UNKNOWN_ALGORITHM')
sV2 = state_of(rdV2, eroot)
check('V2 非现行算法版本(任意档位) → 阻断',
      sV2['verdict'] is None and '非现行口径' in str(sV2['error']),
      str(sV2)[:160])

# V3 非首档算法版本同样拦(逐档,不只查最新)
rdV3 = chain3('v3')
v3paths = verdicts_of(rdV3)
rewrite(v3paths[1][0], digest_algorithm='UNKNOWN_ALGORITHM')
sV3 = state_of(rdV3, eroot)
check('V3 第二档非现行算法 → 阻断(逐档校验)',
      sV3['verdict'] is None and '非现行口径' in str(sV3['error']),
      str(sV3)[:160])

# V4 合法旧链(legacy 头=无 revision 首档)+复审档 → 照常通过
rdV4 = chain3('v4')
v4path = verdicts_of(rdV4)[0][0]
rewrite(v4path, revision=DELETE, predecessor=DELETE)
d4 = json.load(open(os.path.join(rdV4, 'report.json'), encoding='utf-8'))
d4['notes'] = ['合法复审内容演进']
json.dump(d4, open(os.path.join(rdV4, 'report.json'), 'w',
                   encoding='utf-8'), ensure_ascii=False)
aj.record_semantic_verdict(eroot, rdV4, 'UPHELD', 'R6-SEAT-RE')
sV4 = state_of(rdV4, eroot)
check('V4 legacy 头+复审 → 健全(恢复能力保留)',
      sV4['verdict'] == 'UPHELD' and sV4['error'] is None,
      str(sV4)[:120])

# V5 report/archive 门一致: 被污染链 → report 拒交付+archive 拒归档
eV5 = stage_report(rdV1, eroot)
aV5 = stage_archive(rdV1, eroot, os.path.join(tmp, 'arcV'))
check('V5 污染链 → 两门同拒(结果一致)',
      eV5.get('deliverable') is False and aV5.returncode != 0,
      json.dumps(eV5, ensure_ascii=False)[:160])

# ══ 汇总 ═══════════════════════════════════════════════════════════
print('═' * 64)
print(f'Audit-R6 判定: {PASS} PASS / {FAIL} FAIL')
print('═' * 64)
sys.exit(1 if FAIL else 0)
