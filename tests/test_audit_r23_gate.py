# -*- coding: utf-8 -*-
"""Audit-R23(R67) 门测试 — 冻结源报告/历史信息截止/正文事实校验/首页转折。

指令四修的确定性判据(离线可复跑+§G 正式入口子进程,零外部数据):
  §A 任务1 冻结源渲染: 正确快照/无外部快照/同名快照端点被改三种情况
     逐字节一致;36 经济行+45 资产行;同观测窗注记分支
  §B 任务1 裁决↔地图内容绑定: record 落 map_report_sha256;被改地图
     不得沿用旧裁决(fresh=False);legacy 档不追溯(旧链零漂移)
  §C 任务2 历史信息截止: 当时可知面逐段重算(五字段绑定)+事后段迁移
     (CN PPI×3/EA HICP 快报/JP CPI/2025 停摆 INDPRO·CPI·GDP·失业)
     +公布前一天/当天逐项翻转
  §D 任务3 正文事实校验: GDP 季度窜写(Q2→Q3)与年度美债 +97bp→−97bp
     均 CONTRADICTED;同义中文正例与原文 VERIFIED 零漂移
  §E 任务2 as_of 泄漏契约: 标记在场=同步性引事后数必拦;改写为当时
     可知值通过;标记缺席=旧档兼容
  §F 任务4 渲染: 首页速览整句不截断/百分比水平 bp 表述/同轮事件并项
     +引擎补选独立转折/当时可知面与事后段表/冻结源披露
  §G 任务1 正式入口三例重放(真实工单 20261119T153709Z 档案):
     三情形 MAP 逐字节一致+锚更新+直渲同源;单改拒付不重写+归档零
     增量;裁决绑定攻击(重挂锚)不得沿用旧裁决且自愈;Q3/−97bp 窜写
     CLI 级「不可交付+归档拒绝」
"""
import copy
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
sys.path.insert(0, os.path.join(ROOT, 'scripts', 'research_contract'))

import agent_judgment as aj                      # noqa: E402
import research_map_planner as rmp               # noqa: E402
from judgment_contract import build_face, verify_judgment  # noqa: E402

TMPG = tempfile.mkdtemp(prefix='r23gate_')
RESULTS = []
ARC_DIR = os.path.join(
    ROOT, 'docs', 'autonomous-rd', 'r22-evidence', 'acceptance',
    '20261119T153709Z_给我一份全球宏观经济变化地图_美国_中国_欧元区_'
    '日本在12个月前_3个月前和最')
RUN_TS = '20261119T153709Z'
SNAP_ID = 'research_snapshot_20261119'
_SR_TWO_KEY = {'verdict': 'UPHELD', 'verdicts_n': 1}


def check(name, ok, detail=''):
    RESULTS.append((name, bool(ok), str(detail)[:220]))
    print(('  ✅ ' if ok else ' ❌ ') + name
          + (f' — {detail}' if detail else ''), flush=True)


def load_arc(name):
    with open(os.path.join(ARC_DIR, name), encoding='utf-8') as f:
        return json.load(f)


RJ = load_arc('report.json')
JD0 = load_arc('agent_judgment.json')


def map_rows(text):
    econ = sum(1 for l in text.splitlines()
               if l.strip().startswith('| 经济指标 |'))
    asset = sum(1 for l in text.splitlines()
                if l.strip().startswith('| 资产表现 |'))
    return econ, asset


def frozen_snapshot(tamper_spx=False):
    """由 report.json 冻结信封重建运行快照(任务1 情形1/3 的快照面)。"""
    store = {}
    for st in RJ.get('steps') or []:
        nm = st.get('step') or ''
        if nm.startswith('S4_history_'):
            ser = ((st.get('envelope') or {}).get('data')
                   or {}).get('series') or {}
            if ser.get('dates'):
                store[nm[11:]] = {'dates': list(ser['dates']),
                                  'values': list(ser['values'])}
    if tamper_spx and 'SPX' in store:
        v = store['SPX']['values']
        for i in (len(v) - 1, len(v) // 2):
            if v[i] is not None:
                v[i] = v[i] * 10.0
    return {'snapshot_id': SNAP_ID, 'series_store': store}


def build_tree(tag, snapshot=None, verdicts=True):
    """§G 正式入口重放树: config+裁决(+可选快照),零活数据依赖。"""
    T = os.path.join(TMPG, 'tree_' + tag)
    os.makedirs(os.path.join(T, 'data', 'daily'))
    os.makedirs(os.path.join(T, 'config'))
    for fn in ('metric_registry.json', 'release_calendar.json'):
        shutil.copy(os.path.join(ROOT, 'config', fn),
                    os.path.join(T, 'config', fn))
    if verdicts:
        d = os.path.join(T, 'audit', 'semantic_review', '20261120')
        os.makedirs(d)
        shutil.copy(
            os.path.join(ARC_DIR, 'verdicts',
                         f'20261120__VERDICT-{RUN_TS}-01.json'),
            os.path.join(d, f'VERDICT-{RUN_TS}-01.json'))
    if snapshot is not None:
        with open(os.path.join(T, 'data', 'daily', f'{SNAP_ID}.json'),
                  'w', encoding='utf-8') as f:
            json.dump(snapshot, f)
    return T


def fresh_rd(tag):
    d = os.path.join(TMPG, 'rd_' + tag)
    shutil.copytree(ARC_DIR, d)
    return d


def cli(stage, rd, engine_root, judgment=None, arc=None):
    cmd = [sys.executable, 'ia_cli.py', 'research-one', '--stage', stage,
           '--report-dir', rd, '--engine-root', engine_root]
    if judgment:
        cmd += ['--judgment', judgment]
    if arc:
        cmd += ['--archive-dir', arc]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                       timeout=600)
    try:
        data = json.loads(r.stdout)
    except Exception:
        data = {'raw': ((r.stdout or '') + (r.stderr or ''))[-400:]}
    return r.returncode, data


def cv_of(rd):
    rep = json.load(open(os.path.join(rd, 'report.json'),
                         encoding='utf-8'))
    return rep, ((rep.get('agent_judgment') or {})
                 .get('contract_verification') or {})


def _sha(b):
    return hashlib.sha256(b).hexdigest()


# ═══ §A 任务1 冻结源渲染一致性(离线直渲) ═══
def sec_a():
    print('═══ §A 冻结源渲染: 三情形逐字节一致+36/45 行+同观测注记 ═══')
    r1 = build_tree('a1', frozen_snapshot())
    r2 = build_tree('a2', None)                       # 无外部快照
    r3 = build_tree('a3', frozen_snapshot(tamper_spx=True))
    t1 = rmp.render_map_report(RJ, JD0, _SR_TWO_KEY, root=r1)
    t2 = rmp.render_map_report(RJ, JD0, _SR_TWO_KEY, root=r2)
    t3 = rmp.render_map_report(RJ, JD0, _SR_TWO_KEY, root=r3)
    check('§A 三情形逐字节一致(正确快照=无快照=端点被改快照)',
          t1 == t2 == t3,
          f'len {len(t1)}/{len(t2)}/{len(t3)}')
    e1, a1 = map_rows(t1)
    check('§A 36 经济行+45 资产行(三段×三窗×4/5 指标)',
          (e1, a1) == (36, 45)
          and map_rows(t2) == (36, 45) and map_rows(t3) == (36, 45),
          f'econ={e1} asset={a1}')
    spx = rmp._series_from_report(RJ, 'SPX')
    d0, v0 = rmp._month_end_obs(spx['dates'], spx['values'], '2025-03')
    check('§A SPX 行止值=冻结信封锚月末值(改快照不进任何行)',
          f'{v0:g}' in t1, f'SPX@2025-03={v0:g}')
    # 同观测窗: 锚后无新观测→行保留+注记,不整行缺席
    snap_syn = {'series_store': {
        'DFEDTARU': {'dates': ['2022-05-31', '2022-06-30'],
                     'values': [0.75, 1.00]}}}
    hwf = rmp.history_window_face(
        [{'anchor_ym': '2022-06', 'judgment_cutoff_ym': '2022-06'}],
        snap_syn, ROOT, rj=None)
    w3 = (hwf['periods'][0]['windows'].get('3m') or {}).get('rows') or []
    row = next((r for r in w3 if r['metric_id'] == 'DFEDTARU'), None)
    absent = hwf['periods'][0].get('absent') or []
    check('§A 同观测窗注记: 行保留+变化不可算+不入缺席',
          row is not None and row.get('note') and
          '缺少两期数据' in row['note'] and row.get('change') is None
          and row.get('from_date') == row.get('to_date') == '2022-06-30'
          and 'DFEDTARU' not in ''.join(absent),
          str(row and row.get('note'))[:80])


# ═══ §B 任务1 裁决↔地图内容绑定 ═══
def sec_b():
    print('═══ §B 裁决绑定: 被改地图不得沿用旧裁决;legacy 不追溯 ═══')
    full = open(os.path.join(ARC_DIR, 'MAP_REPORT.md'), 'rb').read()
    anchor = open(os.path.join(ARC_DIR, 'MAP_REPORT.sha256'),
                  encoding='utf-8').read().strip().split(' ', 1)[0]
    text = full.decode('utf-8')
    c_sha = aj.map_report_content_sha(ARC_DIR)
    check('§B 内容段摘要=全文锚独立(语义审查尾不入内容段摘要)',
          c_sha and c_sha != _sha(full) and anchor == _sha(full)
          and '\n## 语义审查' in text,
          f'content[:12]={str(c_sha)[:12]} anchor[:12]={anchor[:12]}')
    tail_mutated = text.split('\n## 语义审查')[0] + \
        '\n## 语义审查\n- 席位已裁: 任意尾注(不入内容段)\n'
    with open(os.path.join(TMPG, 'b_tail.md'), 'w',
              encoding='utf-8') as f:
        f.write(tail_mutated)
    check('§B 尾段变更不改内容段摘要(裁决跨 待裁→已裁 稳定)',
          hashlib.sha256(tail_mutated.split('\n## 语义审查')[0]
                         .encode('utf-8')).hexdigest() == c_sha)
    # record 落档含绑定 + 被改地图(含重挂锚攻击)不得沿用旧裁决
    T = build_tree('b1', None)
    rd = fresh_rd('b1')
    aj.record_semantic_verdict(T, rd, 'UPHELD', reviewer='r23-gate-绑定席',
                               notes='R23 门 §B 绑定负例(rev=2)')
    v2 = aj._verdicts_for_run(T, RUN_TS)
    doc2 = max((d for _p, d in v2 if isinstance(d, dict)),
               key=lambda d: d.get('revision') or 0)
    check('§B record 落档含 map_report_sha256=当前内容段摘要',
          doc2.get('map_report_sha256') == aj.map_report_content_sha(rd)
          and (doc2.get('revision') or 0) >= 2)
    st0 = aj._semantic_review_state(RJ, T, rd)
    check('§B 干净面: rev=2 绑定在档 fresh=True',
          st0.get('fresh') is True and st0.get('verdict') == 'UPHELD'
          and st0.get('map_report_sha256') == c_sha or
          st0.get('map_report_sha256') ==
          aj.map_report_content_sha(rd),
          f"fresh={st0.get('fresh')} verdict={st0.get('verdict')}")
    # 攻击: 改内容段数字+重挂锚(锚自洽)——内容段摘要≠绑定→旧裁决失效
    mp = os.path.join(rd, 'MAP_REPORT.md')
    tampered = open(mp, encoding='utf-8').read().replace('6.1', '6.7', 1)
    with open(mp, 'w', encoding='utf-8') as f:
        f.write(tampered)
    with open(os.path.join(rd, 'MAP_REPORT.sha256'), 'w',
              encoding='utf-8') as f:
        f.write(_sha(tampered.encode('utf-8')) + '  MAP_REPORT.md\n')
    st1 = aj._semantic_review_state(RJ, T, rd)
    check('§B 重挂锚攻击: 内容段摘要≠裁决绑定→fresh=False(错误版本不'
          '得沿用旧裁决)',
          st1.get('fresh') is False and
          '内容段摘要与裁决绑定不符' in str(st1.get('fresh_note')),
          str(st1.get('fresh_note'))[:100])
    # legacy 档(无 map_report_sha256 键)不追溯——R22 前旧链零漂移保全
    T2 = build_tree('b2', None)
    rd2 = fresh_rd('b2')
    mp2 = os.path.join(rd2, 'MAP_REPORT.md')
    tam2 = open(mp2, encoding='utf-8').read().replace('6.1', '6.7', 1)
    with open(mp2, 'w', encoding='utf-8') as f:
        f.write(tam2)
    st2 = aj._semantic_review_state(RJ, T2, rd2)
    check('§B legacy 档不追溯(历史裁决无绑定键,不因新机制翻旧案)',
          st2.get('map_report_sha256') is None
          and st2.get('fresh') is not False,
          f"fresh={st2.get('fresh')}")


# ═══ §C 任务2 历史信息截止(当时可知面) ═══
def sec_c():
    print('═══ §C 当时可知面: 逐段重算/事后段迁移/前一天-当天翻转 ═══')
    faces = {}
    for h in JD0['reader_map']['history_periods']:
        faces[h['anchor_ym']] = rmp.history_asof_face([h], RJ)['periods'][0]
    p22 = faces['2022-06']
    kn = {r['metric_id']: r for r in p22['known']}
    af = [r for r in p22['aftermath'] if r['metric_id'] == 'CN_PPI_YOY']
    check('§C 2022-06 中国PPI: 已知=2022-05 6.4(公布2022-06-09),'
          '2022-06 6.1 首发2022-07-09 移事后段',
          kn.get('CN_PPI_YOY', {}).get('obs_month') == '2022-05'
          and kn['CN_PPI_YOY']['value'] == 6.4
          and kn['CN_PPI_YOY']['visible_from'] == '2022-06-09'
          and af and af[0]['obs_month'] == '2022-06'
          and af[0]['value'] == 6.1
          and af[0]['visible_from'] == '2022-07-09'
          and '移入事后段' in str(af[0].get('delay_note')),
          f"known={kn.get('CN_PPI_YOY', {}).get('value')} "
          f"after={af[0]['value'] if af else None}")
    ea = kn.get('EA_HICP_YOY') or {}
    check('§C 2022-06 欧元区HICP: 快报2022-06-30 当时可知(推定)+'
          '终值2022-07-16 分记',
          ea.get('obs_month') == '2022-06' and ea.get('value') == 8.6
          and ea.get('visible_from') == '2022-06-30'
          and ea.get('first_publish') == '2022-07-16'
          and '快报' in str(ea.get('note')),
          str(ea.get('note'))[:60])
    jp = kn.get('JP_CPI_YOY') or {}
    jpa = [r for r in p22['aftermath'] if r['metric_id'] == 'JP_CPI_YOY']
    check('§C 2022-06 日本CPI: 已知=2022-05 2.46,2022-06 2.35 首发'
          '2022-07-20 移事后段',
          jp.get('obs_month') == '2022-05' and jp.get('value') == 2.46
          and jpa and jpa[0]['obs_month'] == '2022-06'
          and jpa[0]['value'] == 2.35
          and jpa[0]['visible_from'] == '2022-07-20')
    # 三段×已知行五字段绑定全非空(指标/观测期/值/公布日/来源/修订口径)
    all_ok, n_rows = True, 0
    for aym, p in faces.items():
        for r in p['known']:
            n_rows += 1
            if not (r.get('metric_id') and r.get('obs_month')
                    and isinstance(r.get('value'), (int, float))
                    and r.get('visible_from') and r.get('source')
                    and r.get('revision_note')):
                all_ok = False
    check(f'§C 已知行五字段绑定全非空(三段共{n_rows}行)',
          all_ok and n_rows >= 24, f'n={n_rows}')
    # 2025-03 停摆面
    p25 = faces['2025-03']
    af25 = p25['aftermath']

    def find(mid, om):
        return next((r for r in af25
                     if r['metric_id'] == mid and r['obs_month'] == om),
                    None)
    hole = find('CPI', '2025-10')
    rec = find('CPI', '2025-11')
    ind = find('INDPRO', '2025-09')
    gdp = find('US_REAL_GDP', '2025-07')
    unp = find('UNEMPLOYMENT', '2025-09')
    check('§C 2025 停摆: CPI 2025-10 采集缺口+2025-11 恢复(首发'
          '2025-12-13)',
          hole is not None and hole.get('value') is None
          and '采集缺口' in str(hole.get('delay_note'))
          and rec is not None and rec.get('value') == 325.063
          and rec.get('visible_from') == '2025-12-13'
          and '缺口后恢复' in str(rec.get('delay_note')))
    check('§C 2025 停摆: 工业生产 2025-09 首发2026-01-22(晚常轨99天)'
          '+2025-10 同批(68天)',
          ind is not None and ind.get('first_publish') == '2026-01-22'
          and '99 天' in str(ind.get('delay_note'))
          and find('INDPRO', '2025-10') is not None
          and '68 天' in str(find('INDPRO', '2025-10').get('delay_note')))
    check('§C 2025 停摆: Q3 GDP 首发2025-12-23(晚常轨55天);九月失业率'
          '实录2025-11-20 优先于保守界(晚常轨46天)',
          gdp is not None and gdp.get('first_publish') == '2025-12-23'
          and unp is not None and unp.get('visible_from') == '2025-11-20'
          and '46 天' in str(unp.get('delay_note'))
          and 'user_direc' in str(unp.get('pub_basis')),
          str(unp and unp.get('pub_basis'))[:60])
    gdp_months = {r['obs_month'] for r in af25
                  if r['metric_id'] == 'US_REAL_GDP'}
    check('§C 季频非季月不算缺口(GDP 事后段仅季观测月)',
          gdp_months and gdp_months <= {'2025-04', '2025-07'},
          str(sorted(gdp_months)))
    # 前一天/当天逐项(指令点名: 三段中国PPI/2022-06 HICP/停摆期工业
    # 生产与11月CPI与9月核心PCE;保全就业与 Q3 GDP 用例)
    flips = [
        ('CN_PPI_YOY', '2022-06-30', '2022-07-09'),
        ('CN_PPI_YOY', '2023-10-31', '2023-11-09'),
        ('CN_PPI_YOY', '2025-03-31', '2025-04-09'),
        ('EA_HICP_YOY', '2022-06-30', '2022-06-30'),
        ('INDPRO', '2025-09-30', '2026-01-22'),
        ('CPI', '2025-11-30', '2025-12-13'),
        ('CORE_PCE', '2025-09-30', '2026-01-22'),
        ('UNEMPLOYMENT', '2025-09-30', '2025-11-20'),
        ('US_REAL_GDP', '2025-07-31', '2025-12-23'),
    ]

    def vis(mid, od, asof):
        vf, _pub, _b, _n = rmp._aof_first_pub(mid, od, 'monthly')
        return vf is not None and vf <= asof

    for mid, od, pub in flips:
        d1 = (datetime.date.fromisoformat(pub)
              - datetime.timedelta(days=1)).isoformat()
        check(f'§C {mid} {od[:7]}观测: 前一天{d1}不可见/当天{pub}可见',
              not vis(mid, od, d1) and vis(mid, od, pub),
              f'pub={pub}')


# ═══ §D 任务3 正文事实校验(离线契约) ═══
def sec_d():
    print('═══ §D 正文窜写: Q2→Q3 与 +97bp→−97bp 均拦;同义正例过 ═══')
    face = build_face(RJ)

    def contract(mutate, rj=None):
        jd = copy.deepcopy(JD0)
        mutate(jd)
        res = verify_judgment(jd, rj or RJ, face=face)
        return res, [f for f in (res.get('map_checks') or [])
                     if f.get('status') != 'VERIFIED']

    res, bad = contract(lambda jd: None)
    check('§D 原文零漂移: VERIFIED+旧档无 asof 标记(泄漏检查不追溯)',
          res.get('verdict') == 'VERIFIED' and not bad
          and not str((RJ.get('research_plan') or {})
                      .get('asof_discipline') or ''),
          f"verdict={res.get('verdict')}")

    def q3(jd):
        for r in jd['reader_map']['regions']:
            if r.get('region') == 'US':
                r['from_to'] = r['from_to'].replace('2025Q2', '2025Q3', 1)

    res, bad = contract(q3)
    check('§D 反例①: 美国 GDP 正文 2025Q2→2025Q3 → CONTRADICTED'
          '(quarter_token: 锚前不可见季度)',
          res.get('verdict') == 'CONTRADICTED'
          and any('quarter_token' in str(b.get('item')) for b in bad),
          str([b.get('item') for b in bad[:2]]))

    def m97(jd):
        jd['reader_map']['headline_conclusion'] = \
            jd['reader_map']['headline_conclusion'].replace(
                '名义+97bp', '名义−97bp', 1)

    res, bad = contract(m97)
    check('§D 反例②: 首页年度名义美债 +97bp→−97bp → CONTRADICTED'
          '(headline_conclusion.bp 对账)',
          res.get('verdict') == 'CONTRADICTED'
          and any(str(b.get('item')).endswith(
              'headline_conclusion.bp') for b in bad),
          str([b.get('item') for b in bad[:2]]))

    def syn(jd):
        jd['reader_map']['headline_conclusion'] = \
            jd['reader_map']['headline_conclusion'].replace(
                '名义+97bp=实际+104bp+盈亏平衡-7bp',
                '名义利率上行97bp=实际利率走高104bp+盈亏平衡通胀下行-7bp',
                1)

    res, bad = contract(syn)
    check('§D 正例: 含义相同的中文表述(上行/走高/下行+bp)→VERIFIED '
          '不误伤',
          res.get('verdict') == 'VERIFIED' and not bad,
          str([str(b.get('note'))[:60] for b in bad[:1]]))


# ═══ §E 任务2 as_of 泄漏契约(标记门) ═══
def sec_e():
    print('═══ §E 信息截止泄漏: 标记在场必拦/改写通过/缺席兼容 ═══')
    rj_m = copy.deepcopy(RJ)
    rj_m['research_plan']['asof_discipline'] = 'r23'
    face_m = build_face(rj_m)

    def contract(mutate, rj, face):
        jd = copy.deepcopy(JD0)
        mutate(jd)
        res = verify_judgment(jd, rj, face=face)
        return res, [f for f in (res.get('map_checks') or [])
                     if f.get('status') != 'VERIFIED']

    res, bad = contract(lambda jd: None, rj_m, face_m)
    leaks = [b for b in bad if 'as_of_leak' in str(b.get('item'))]
    anchors = [h.get('anchor_ym')
               for h in JD0['reader_map']['history_periods']]
    cn_periods = set()
    for b in leaks:
        m = re.search(r'history_periods\[(\d+)\]', str(b.get('item')))
        if m and 'PPI' in str(b.get('note')):
            cn_periods.add(anchors[int(m.group(1))])
    check('§E 标记在场+原文: 同步性引事后数 → ≥4 处 as_of_leak+'
          'CN_PPI≥2 段+CONTRADICTED',
          res.get('verdict') == 'CONTRADICTED' and len(leaks) >= 4
          and len(cn_periods) >= 2,
          f'n={len(leaks)} CN段={sorted(cn_periods)}')

    def corrected(jd):
        for h in jd['reader_map']['history_periods']:
            p = rmp.history_asof_face([h], RJ)['periods'][0]
            parts = [f"{r['label'].split('(')[0]} {r['value']:g}"
                     f"({r['obs_month']},公布{r['visible_from']})"
                     for r in p['known']]
            txt = '当时可知(发布纪律重算): ' + '、'.join(parts)
            h['other_regions_sync'] = txt
            h['similarity'] = txt
            h['difference'] = txt

    res, bad = contract(corrected, rj_m, face_m)
    check('§E 标记在场+当时可知改写 → VERIFIED(正路可走通)',
          res.get('verdict') == 'VERIFIED' and not bad,
          str([str(b.get('note'))[:80] for b in bad[:1]]))
    res, bad = contract(lambda jd: None, RJ, build_face(RJ))
    check('§E 标记缺席+原文 → VERIFIED(R22 归档重放零漂移前提)',
          res.get('verdict') == 'VERIFIED' and not bad)


# ═══ §F 任务4 渲染面(首页速览/bp 表述/并项+补选/当时可知表) ═══
def sec_f():
    print('═══ §F 渲染: 整句/bp/同轮并项+独立补选/当时可知表 ═══')
    T = build_tree('f1', frozen_snapshot())
    text = rmp.render_map_report(RJ, JD0, _SR_TWO_KEY, root=T)
    flow = next((l for l in text.splitlines()
                 if '→' in l and l.startswith('**') and 'CPI' in l), '')
    check('§F 首页速览整句: 美国CPI同比 2.434→4.1666 完整入链'
          '(数字不被拦腰截断)',
          '美国CPI同比 2.434→4.1666' in flow
          and not any(flow.endswith(x) for x in
                      ('2.434→4.', '→4.', '-0.9→3.')),
          flow[:120])
    check('§F 百分比水平 bp 表述: 盈亏平衡 2.35→2.19=下降16bp;'
          'TIPS 上升12bp(不再误标相对%)',
          '近30日2.35→2.19,下降16bp' in text
          and '近30日2.77→2.89,上升12bp' in text)
    lines = text.splitlines()
    i0 = next(i for i, l in enumerate(lines)
              if l.startswith('| 日期 | 指标 |'))
    body = []
    for l in lines[i0 + 1:]:
        if not l.startswith('|'):
            break
        if not l.startswith('|---'):
            body.append(l)
    check('§F 同轮并项+引擎补选: 转折表=2 事件行+1 补选行(CN_PPI+CPI '
          '并项,JP_CPI_TOKYO 独立补选|Δ|降序)',
          len(body) == 3
          and any('CN_PPI_YOY+CPI(同轮事件并项)' in l for l in body)
          and any('(引擎补选·非判断席)' in l
                  and 'JP_CPI_TOKYO_YOY' in l for l in body)
          and '并项与补选口径' in text,
          f'rows={len(body)}')
    check('§F 当时可知面表: 三段各一张+事后段表+CN_PPI 事后行逐字'
          '(2022-06|6.1|2022-07-09)',
          text.count('当时可知面(发布纪律重算') == 3
          and text.count('截止日后才公布(事后段') == 3
          and '| 中国PPI同比(CN_PPI_YOY) | 2022-06 | 6.1 | '
          '2022-07-09 |' in text)
    check('§F 逐窗并列序列源披露: 冻结信封优先/运行快照兜底',
          '序列源=report.json 冻结信封优先' in text
          and '运行快照文件不在场' not in text)
    # ── Audit-R23 收口(验收席 Round-1 NIT-2/NIT-4,渲染器修) ──────────
    rj_idx = {'steps': [{'step': 'S4_history_CN_PMI_MFG',
                         'envelope': {'data': {'series': {
                             'dates': ['2026-10-20', '2026-11-18'],
                             'values': [49.2, 49.3],
                             'unit': 'index_point'}}}}]}
    s = rmp._distinguishing_obs(rj_idx, '2026-11-19', 'CN_PMI_MFG')
    check('§F2 NIT-2: 指数序列区分观测括号配平'
          '(引擎当前面: …近30日Δ…%(…))不再缺右括号',
          bool(s) and s.count('(') == s.count(')')
          and s.startswith('(引擎当前面: ') and s.endswith(')'),
          repr(s))
    check('§F2 NIT-4: 对照表指标名不叠套(口径注已含名→单层'
          '制造业PMI(月频),不再「制造业PMI(制造业PMI(月频))」)',
          '制造业PMI(制造业PMI' not in text
          and '| 制造业PMI(月频) |' in text,
          'CN/growth 行单层渲染')


# ═══ §G 任务1 正式入口三例重放+窜写 CLI 级 ═══
def sec_g():
    print('═══ §G 正式入口: 三例重放逐字节一致+单改拒付+绑定自愈+窜写 ═══')
    trees = [build_tree('g1', frozen_snapshot()),
             build_tree('g2', None),
             build_tree('g3', frozen_snapshot(tamper_spx=True))]
    rds = [fresh_rd('g1'), fresh_rd('g2'), fresh_rd('g3')]
    outs = []
    for T, rd in zip(trees, rds):
        rc, d = cli('report', rd, T)
        data = d.get('data') or {}
        outs.append((rc, data, rd,
                     open(os.path.join(rd, 'MAP_REPORT.md'), 'rb').read()))
    ok_all = all(rc == 0 and (data.get('deliverable') is True)
                 and ((data.get('review') or {}).get('verdict')
                      == 'UPHELD')
                 and data.get('copies_consistent') is True
                 for rc, data, _rd, _b in outs)
    check('§G 三例 report 全放行(rc=0+deliverable+UPHELD+副本一致)',
          ok_all,
          str([(rc, (data.get('deliverable')),
                (data.get('review') or {}).get('verdict'))
               for rc, data, _rd, _b in outs]))
    b1, b2, b3 = (o[3] for o in outs)
    check('§G 三例 MAP_REPORT.md 逐字节一致(=指令「前两种逐字节还原'
          '原件,第三种不因同名快照被改而变」)',
          b1 == b2 == b3,
          f'sha16={_sha(b1)[:12]} {_sha(b2)[:12]} {_sha(b3)[:12]}')
    sr_cli = aj._semantic_review_state(RJ, trees[0], rds[0])
    direct = rmp.render_map_report(RJ, JD0, sr_cli,
                                   root=trees[0]).encode('utf-8')
    check('§G 正式入口=新码直渲同源字节(渲染无隐藏输入)',
          b1 == direct, f'{_sha(b1)[:12]} vs {_sha(direct)[:12]}')
    e, a = map_rows(b1.decode('utf-8'))
    arch_map = open(os.path.join(ARC_DIR, 'MAP_REPORT.md'),
                    'rb').read()
    anchor_now = open(os.path.join(rds[0], 'MAP_REPORT.sha256'),
                      encoding='utf-8').read().strip().split(' ', 1)[0]
    check('§G 36/45 行+锚已更新(合法修订: 锚=新文件摘要)+与 R22 归档'
          '版不同(渲染已按四修更新)',
          (e, a) == (36, 45) and anchor_now == _sha(b1)
          and b1 != arch_map,
          f'econ={e} asset={a}')
    # ── 单改负例: 锚未动→拒付+不重写(证据保全)+归档拒绝 ──
    rd4 = fresh_rd('g4')
    T4 = build_tree('g4', frozen_snapshot())
    rc, _ = cli('report', rd4, T4)
    mp4 = os.path.join(rd4, 'MAP_REPORT.md')
    canonical4 = open(mp4, 'rb').read()
    tam = canonical4.decode('utf-8').replace('6.1', '9.9', 1)
    with open(mp4, 'w', encoding='utf-8') as f:
        f.write(tam)
    tam_bytes = tam.encode('utf-8')
    rc4, d4 = cli('report', rd4, T4)
    check('§G 单改负例: report 拒付(rc≠0+deliverable=False+单改警告)',
          rc4 != 0 and not (d4.get('data') or {}).get('deliverable')
          and any('单改' in str(w) for w in (d4.get('warnings') or [])),
          str([str(w)[:60] for w in (d4.get('warnings')
                                     or [])[:2]]))
    check('§G 单改负例: MAP 不被重写(证据保全,在场=篡改版/锚=旧值)',
          open(mp4, 'rb').read() == tam_bytes
          and open(os.path.join(rd4, 'MAP_REPORT.sha256'),
                   encoding='utf-8').read().strip().split(' ', 1)[0]
          == _sha(canonical4))
    arc4 = os.path.join(TMPG, 'arc_g4')
    rc4a, d4a = cli('archive', rd4, T4, arc=arc4)
    check('§G 单改负例: 归档拒绝+零增量(错误版本不新增正式归档)',
          rc4a != 0 and (d4a.get('data') or {}).get('blocked')
          == 'not_deliverable'
          and not (os.path.isdir(arc4) and any(os.scandir(arc4))),
          str((d4a.get('data') or {}).get('blocked')))
    # ── 绑定负例: rev=2 绑定 canonical→改内容段+重挂锚→裁决失效+自愈 ──
    T5, rd5 = trees[0], rds[0]
    aj.record_semantic_verdict(T5, rd5, 'UPHELD',
                               reviewer='r23-gate-绑定席',
                               notes='R23 门 §G 绑定攻击面(rev=2)')
    mp5 = os.path.join(rd5, 'MAP_REPORT.md')
    base5 = open(mp5, encoding='utf-8').read()
    tam5 = base5.replace('6.1', '6.7', 1)
    with open(mp5, 'w', encoding='utf-8') as f:
        f.write(tam5)
    with open(os.path.join(rd5, 'MAP_REPORT.sha256'), 'w',
              encoding='utf-8') as f:
        f.write(_sha(tam5.encode('utf-8')) + '  MAP_REPORT.md\n')
    st5 = aj._semantic_review_state(RJ, T5, rd5)
    rc5, d5 = cli('report', rd5, T5)
    rc5b, d5b = cli('report', rd5, T5)
    healed = open(mp5, encoding='utf-8').read()
    check('§G 绑定负例: 重挂锚后旧裁决失效(fresh=False+绑定注记),当轮'
          '拒付(rc≠0);引擎重渲 canonical 内容段(在场恢复=直渲字节,仅'
          '裁决链页脚合法翻新),复跑放行——错误版本无法沿用裁决/入档',
          st5.get('fresh') is False
          and '内容段摘要与裁决绑定不符' in str(st5.get('fresh_note'))
          and rc5 != 0
          and not (d5.get('data') or {}).get('deliverable')
          and healed.split('\n## 语义审查')[0]
          == direct.decode('utf-8').split('\n## 语义审查')[0]
          and rc5b == 0
          and (d5b.get('data') or {}).get('deliverable') is True,
          f"fresh={st5.get('fresh')} rc={rc5}/{rc5b}")
    # ── 任务3 窜写 CLI 级: 机器识别+不可交付+归档零增量 ──
    for tag, mutate, want_item in (
            ('q3', _tamper_q3, 'quarter_token'),
            ('m97', _tamper_m97, 'headline_conclusion.bp')):
        jd = copy.deepcopy(JD0)
        mutate(jd)
        jp = os.path.join(TMPG, f'g_{tag}_judgment.json')
        with open(jp, 'w', encoding='utf-8') as f:
            json.dump(jd, f, ensure_ascii=False)
        rd = fresh_rd(f'g_{tag}')
        T = build_tree(f'g_{tag}', frozen_snapshot())
        rca, da = cli('attach', rd, T, judgment=jp)
        _rep, cv = cv_of(rd)
        rcr, dr = cli('report', rd, T)
        arcd = os.path.join(TMPG, f'arc_g_{tag}')
        rcx, dx = cli('archive', rd, T, arc=arcd)
        check(f'§G 窜写({want_item}): attach CONTRADICTED+report 不可'
              '交付+归档拒绝零增量',
              not (da.get('data') or {}).get('attached')
              and cv.get('verdict') == 'CONTRADICTED'
              and any(want_item in str((v or {}).get('item'))
                      for v in (cv.get('map_checks') or []))
              and rcr != 0
              and not (dr.get('data') or {}).get('deliverable')
              and rcx != 0
              and not (os.path.isdir(arcd)
                       and any(os.scandir(arcd))),
              f"attach={cv.get('verdict')} rc_report={rcr}")


def _tamper_q3(jd):
    for r in jd['reader_map']['regions']:
        if r.get('region') == 'US':
            r['from_to'] = r['from_to'].replace('2025Q2', '2025Q3', 1)


def _tamper_m97(jd):
    jd['reader_map']['headline_conclusion'] = \
        jd['reader_map']['headline_conclusion'].replace(
            '名义+97bp', '名义−97bp', 1)


def test_audit_r23_gate():
    for fn in (sec_a, sec_b, sec_c, sec_d, sec_e, sec_f, sec_g):
        fn()
    n_fail = sum(1 for _n, ok, _d in RESULTS if not ok)
    print(f'\nAudit-R23 门: {len(RESULTS) - n_fail} PASS / {n_fail} FAIL '
          f'(共 {len(RESULTS)} 判据)')
    if n_fail:
        for n, ok, d in RESULTS:
            if not ok:
                print(f'  ❌ {n} — {d}')
        raise SystemExit(1)


if __name__ == '__main__':
    test_audit_r23_gate()
