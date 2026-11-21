#!/usr/bin/env python3
"""Audit-R28 门 — 全球宏观变化地图正式使用收尾四任务。

任务1 默认入口: SKILL.md 问句路由纪律(research-one 全链+新草稿类)。
任务2 政策/日期: 政策实录三态(决议缺档/确认维持刷新/过期未核验混合/
  缺指定官方目标/正常放行)+LPR 官方时刻+距上次调整按生效日——
  全部用临时夹具日历,生产日历条目只作基线对照(验收数值=测试基准)。
任务3 历史回答: 地区×维度同步面标签族+相对日期事后事实双契约规则。
任务4 离线重放: 逐字节严格路径(包与重放代码同版)+重复运行保留原档+
  缺件/篡改拒绝+渲染器漂移披露桥+代码版本门。
"""
import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
sys.path.insert(0, os.path.join(ROOT, 'scripts', 'research_contract'))

import agent_judgment as aj                      # noqa: E402
import freshness_policy as fp                    # noqa: E402
import release_calendar as rc                    # noqa: E402
import research_map_planner as rmp               # noqa: E402
from judgment_contract import build_face, verify_judgment  # noqa: E402

TMPG = tempfile.mkdtemp(prefix='r28gate_')
RESULTS = []
R23_SRC = os.path.join(ROOT, 'docs', 'autonomous-rd',
                       'r23-evidence', 'acceptance')
RUN_FILES = ['report.json', 'report.md', 'FULL_REPORT.md',
             'agent_judgment.json', 'views_digest.json',
             'evidence_index.json', 'AGENT_SEAT_ENVELOPE.json',
             'MAP_REPORT.md', 'MAP_REPORT.sha256']
R23_RUN_TS = '20261119T173248Z'
WORKTREE_HEAD = subprocess.run(
    ['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True,
    text=True, timeout=30).stdout.strip()

Q_B = ('对比角度换一个：2026年11月，美国与欧元区的增长和通胀环境相比'
       '3个月前各有什么变化？日本央行政策利率处于什么水平，距离上次调整'
       '过了多久？')
Q_A = ('给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在12个月'
       '前、3个月前和最新一期，分别处于什么增长、通胀和货币政策环境？'
       '过去一年最重要的三个转折是什么，谁先变，谁跟进或背离？证据最'
       '充分的传导机制是什么，还有什么解释，哪个指标能区分它们？历史'
       '上哪些时期结构最像，当时其他经济体是否同步，随后3、6、12个月'
       '经济和主要资产实际怎么走？')

# 夹具日历(任务2 五情景共用;字段形态=生产 v1.5.0 同 schema)
_JP_DEC = {"entry_id": "FX-JP-DEC", "kind": "policy_decision",
           "metric_id": "JP_POLICY_TARGET", "obs_from": "2026-09-18",
           "obs_to": "2099-12-31", "decision_date": "2026-09-18",
           "effective_on": "2026-09-24", "target_value": 1.25,
           "first_publish_on_or_after": "2026-09-18"}
_JP_MNT = {"entry_id": "FX-JP-MNT", "kind": "policy_maintenance",
           "metric_id": "JP_POLICY_TARGET", "obs_from": "2026-10-30",
           "obs_to": "2099-12-31", "decision_date": "2026-10-30",
           "target_value": 1.25, "first_publish_on_or_after": "2026-10-30"}
_CN_LPR = {"entry_id": "FX-CN-LPR", "metric_id": "CN_LPR_1Y",
           "obs_from": "2026-11-01", "obs_to": "2026-11-30",
           "first_publish_on_or_after": "2026-11-20", "time": "09:00",
           "official": True}
_EA_MNT = {"entry_id": "FX-EA-MNT", "kind": "policy_maintenance",
           "metric_id": "ECB_MRO", "obs_from": "2026-10-30",
           "obs_to": "2099-12-31", "decision_date": "2026-10-30",
           "target_value": 3.15, "first_publish_on_or_after": "2026-10-30"}
CAL_FULL = os.path.join(TMPG, 'cal_full.json')
CAL_EMPTY = os.path.join(TMPG, 'cal_empty.json')
with open(CAL_FULL, 'w', encoding='utf-8') as f:
    json.dump({"version": "fixture", "entries": [_JP_DEC, _JP_MNT,
                                                 _CN_LPR, _EA_MNT]}, f)
with open(CAL_EMPTY, 'w', encoding='utf-8') as f:
    json.dump({"version": "fixture", "entries": [_CN_LPR]}, f)


def check(name, ok, detail=''):
    RESULTS.append((name, bool(ok), str(detail)[:220]))
    print(('  ✅ ' if ok else ' ❌ ') + name
          + (f' — {detail}' if detail else ''), flush=True)


def cli(stage, rd, engine_root, arc=None, extra=None):
    cmd = [sys.executable, 'ia_cli.py', 'research-one', '--stage', stage,
           '--report-dir', rd, '--engine-root', engine_root]
    if arc:
        cmd += ['--archive-dir', arc]
    if extra:
        cmd += extra
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                       timeout=900)
    try:
        data = json.loads(r.stdout)
    except Exception:
        data = {'raw': ((r.stdout or '') + (r.stderr or ''))[-400:]}
    return r.returncode, data


def replay(pkg, engine_root, out=None, extra=None):
    cmd = [sys.executable, 'ia_cli.py', 'research-one', '--stage', 'replay',
           '--package', pkg, '--engine-root', engine_root]
    if out:
        cmd += ['--replay-out', out]
    if extra:
        cmd += extra
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                       timeout=900)
    try:
        data = json.loads(r.stdout)
    except Exception:
        data = {'raw': ((r.stdout or '') + (r.stderr or ''))[-400:]}
    return r.returncode, data


def build_tree(tag, with_fixture_verdicts=False):
    """重放树: config+可选该工单夹具裁决链,零活数据依赖(r24 同模式)。"""
    T = os.path.join(TMPG, 'tree_' + tag)
    os.makedirs(os.path.join(T, 'data', 'daily'))
    os.makedirs(os.path.join(T, 'config'))
    for fn in ('metric_registry.json', 'release_calendar.json'):
        shutil.copy2(os.path.join(ROOT, 'config', fn),
                     os.path.join(T, 'config', fn))
    d = os.path.join(T, 'audit', 'semantic_review', '20261120')
    os.makedirs(d)
    if with_fixture_verdicts:
        for i in range(1, 4):
            shutil.copy(
                os.path.join(R23_SRC, 'verdicts',
                             f'20261120__VERDICT-{R23_RUN_TS}-0{i}.json'),
                os.path.join(d, f'VERDICT-{R23_RUN_TS}-0{i}.json'))
    return T


def fresh_rd(tag):
    d = os.path.join(TMPG, 'rd_' + tag)
    os.makedirs(d)
    for f in RUN_FILES:
        shutil.copy2(os.path.join(R23_SRC, f), d)
    return d


def rewrite_head(rd, head):
    """包记录运行 SHA=当前工作树 HEAD(重放严格逐字节路径的前提)。

    report.json 变更后同步再生 report.md(_render_md 同版渲染,
    report 段只校验不重写该副本)并移除 FULL_REPORT.md(report 段
    无条件重渲)——多副本一致性自建,不靠两次 report 洗白。"""
    import research_orchestrator as ro
    p = os.path.join(rd, 'report.json')
    rj = json.load(open(p, encoding='utf-8'))
    rj['run']['git_head'] = head
    rj['run']['git_head_source'] = 'r28gate_worktree'
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(rj, f, ensure_ascii=False, indent=2, default=str)
    with open(os.path.join(rd, 'report.md'), 'w', encoding='utf-8') as f:
        f.write(ro._render_md(rj))
    fp = os.path.join(rd, 'FULL_REPORT.md')
    if os.path.exists(fp):
        os.remove(fp)


def strip_policy_entries(cal_path, metric_ids):
    c = json.load(open(cal_path, encoding='utf-8'))
    c['entries'] = [e for e in c.get('entries', [])
                    if e.get('metric_id') not in metric_ids]
    with open(cal_path, 'w', encoding='utf-8') as f:
        json.dump(c, f, ensure_ascii=False, indent=2)


# ═══ §A 任务1: 默认入口纪律(SKILL.md) ═══
def sec_a():
    print('═══ §A 任务1: 默认入口纪律(SKILL.md 问句路由) ═══')
    skill = open(os.path.join(
        ROOT, '.agents', 'skills', 'global-macro-research', 'SKILL.md'),
        encoding='utf-8').read()
    check('§A1 问句路由纪律段在场: 研究问句→research-one 全链'
          '(取证→研判→独立审查→报告交付→停等用户裁定归档)',
          '问句路由纪律' in skill and 'research-one' in skill
          and '停等用户裁定' in skill and '独立语义审查' in skill)
    check('§A2 安装一次后新会话只输入原问(默认入口形态)',
          '只输入原问' in skill)
    check('§A3 草稿纪律收录 R28 两新类(过期未核验混合/缺官方目标)',
          'map_current_period_stale_mix' in skill
          and 'map_official_target_missing' in skill)


# ═══ §B 任务2: 当期政策与日期(五情景,夹具日历) ═══
def sec_b():
    print('═══ §B 任务2: 政策实录三态+官方时刻+按生效日 ═══')
    # 情景① ECB 2024-06-06 决议: 在场证实→STALE;缺档→UNVERIFIED 不虚构
    r_conf = fp.assess_observation_freshness(
        'ECB_MRO', '2024-05-15', '2024-08-15',
        confirmed_later_decision='2024-06-06', calendar_path=False)
    r_miss = fp.assess_observation_freshness(
        'ECB_MRO', '2024-05-15', '2024-08-15',
        confirmed_later_decision=None, calendar_path=False)
    check('§B1① ECB 决议缺档: 决议在场→确证 STALE 引用官方记录;'
          '缺档→UNVERIFIED(本地日历未收录≠未发生,不虚构过期)',
          r_conf.get('status') == 'STALE'
          and any('更晚决议证实' in x for x in r_conf.get('reasons', []))
          and r_miss.get('status') == 'UNVERIFIED'
          and any('无法核验' in x for x in r_miss.get('reasons', [])),
          f"conf={r_conf.get('status')} miss={r_miss.get('status')}")
    # 情景② 确认维持刷新核验锚
    r_maint = fp.assess_observation_freshness(
        'ECB_MRO', '2026-07-24', '2026-11-21', calendar_path=CAL_FULL)
    r_nomaint = fp.assess_observation_freshness(
        'ECB_MRO', '2026-07-24', '2026-11-21', calendar_path=False)
    check('§B2② 确认维持也更新核验日期: 维持2026-10-30→FRESH 间隔22;'
          '无维持→UNVERIFIED 120(锚=观测日)',
          r_maint.get('status') == 'FRESH'
          and any('确认维持2026-10-30' in x
                  for x in r_maint.get('reasons', []))
          and r_nomaint.get('status') == 'UNVERIFIED',
          f"maint={r_maint.get('status')} "
          f"nomaint={r_nomaint.get('status')}")
    # 情景⑤ 正常放行: 距上次调整按生效日 58(决议64/维持22)
    st = fp.policy_decision_state('JP_POLICY_TARGET', '2026-11-21',
                                  calendar_path=CAL_FULL)
    check('§B3⑤ 日银官方记录面: 目标1.25/决议09-18/生效09-24/维持10-30,'
          '距上次调整=58(按生效日)/距决议64/距维持22',
          st.get('present') is True
          and st.get('official_target') == 1.25
          and st.get('last_decision') == '2026-09-18'
          and st.get('last_effective') == '2026-09-24'
          and st.get('last_maintenance') == '2026-10-30'
          and st.get('days_since_adjustment') == 58
          and st.get('days_since_decision') == 64
          and st.get('days_since_maintenance') == 22,
          str({k: st.get(k) for k in ('official_target',
                                      'days_since_adjustment')}))
    check('§B4 无记录指标→present=False(不虚构官方面)',
          fp.policy_decision_state('XX_NONE', '2026-11-21',
                                   calendar_path=CAL_EMPTY)
          .get('present') is False)
    # LPR 官方发布时刻(各表统一读官方发布时间)
    check('§B5 LPR 官方时刻: 2026-11 观测月 09:00;10 月无条目→None',
          rc.publish_instant('CN_LPR_1Y', '2026-11-05', path=CAL_FULL)
          == '09:00'
          and rc.publish_instant('CN_LPR_1Y', '2026-10-05',
                                 path=CAL_FULL) is None)
    # 情景③ 过期+未核验混合→stale_mix 分组(单元)
    pv_mix = {'cells': [
        {'region': 'EA', 'dimension': 'policy', 'metric_id': 'ECB_MRO',
         'anchors': {'最新一期': {'status': 'ok',
                                 'freshness': 'stale'}}},
        {'region': 'EA', 'dimension': 'policy', 'metric_id': 'ECB_DFR',
         'anchors': {'最新一期': {'status': 'ok',
                                 'freshness': 'unverified'}}},
        {'region': 'US', 'dimension': 'policy', 'metric_id': 'DFEDTARU',
         'anchors': {'最新一期': {'status': 'ok', 'freshness': None}}},
        {'region': 'US', 'dimension': 'growth', 'metric_id': 'US_REAL_GDP',
         'anchors': {'最新一期': {'status': 'ok', 'freshness': None}}}]}
    cur = rmp.current_period_groups(
        pv_mix, {('EA', 'policy'), ('US', 'policy'), ('US', 'growth')})
    check('§B6③ current_period_groups 混合形态: EA/policy 入 stale_mix'
          '(单一类判定各自遗漏),US 两组净',
          cur == {'missing': [], 'unverified': [],
                  'stale_mix': [('EA', 'policy')]}, str(cur))
    # 情景④ 缺指定官方目标: 问句域限定(地区央行词×水平/调整问词)
    pv_jp = {'cells': [
        {'region': 'JP', 'dimension': 'policy', 'metric_id': 'JP_POLICY_RATE',
         'anchors': {'最新一期': {'status': 'ok', 'freshness': None}}}]}
    pairs_jp = {('JP', 'policy')}
    face_g = rmp.official_policy_record_face(
        pv_jp, pairs_jp, '2026-11-21', question=Q_B,
        calendar_path=CAL_EMPTY)
    face_ok = rmp.official_policy_record_face(
        pv_jp, pairs_jp, '2026-11-21', question=Q_B,
        calendar_path=CAL_FULL)
    _g = (face_g.get('gaps') or [{}])[0]
    check('§B7④ 缺指定目标: B 问句(点名日银+水平/距调整)×无实录'
          '→gaps 点名 JP/JP_POLICY_TARGET;有实录→gaps 空+rows 带'
          '官方双日与按生效日 58 天(复测基准 2026-11-21)',
          bool(face_g.get('gaps'))
          and _g.get('region') == 'JP'
          and _g.get('metric_id') == 'JP_POLICY_TARGET'
          and '不以市场序列值冒充' in str(_g.get('note'))
          and not face_ok.get('gaps')
          and any(r.get('official_target') == 1.25
                  and r.get('effective') == '2026-09-24'
                  and r.get('days_since_adjustment') == 58
                  for r in face_ok.get('rows') or []),
          f"gaps={face_g.get('gaps')}")
    check('§B8 问句域限定: A 类环境问句(无央行目标词)不触发官方目标'
          '要求(旧例不改判)',
          rmp.official_policy_record_face(
              pv_jp, pairs_jp, '2026-11-21', question=Q_A,
              calendar_path=CAL_EMPTY).get('gaps') in (None, []))
    # blocked_class_of 同源同判(最小 report 夹具;cutoff=生产形状必带)
    def _rep(q, pv, pairs, cal):
        regions = {}
        for e, d in sorted(pairs):
            regions.setdefault(e, {'dimensions': {}})['dimensions'][d] = [{}]
        rep = {'run_ok': True,
               'layers': {'L1_事实层': {'rows': [{'x': 1}]}},
               'run': {'question': q, 'data_requirements': {'items': []}},
               'steps': [],
               'agent_judgment': {'reader_map_faces': {'complete': True}},
               'research_plan': {'map_question': True,
                                 'cutoff': '2026-11-21',
                                 'point_anchors': [
                                     {'label': '最新一期',
                                      'months_before': 0}],
                                 'regions': regions, 'point_values': pv}}
        return aj.blocked_class_of(rep, calendar_path=cal)
    check('§B9③ blocked_class_of: 混合当期→map_current_period_stale_mix',
          _rep(Q_A, pv_mix,
               {('EA', 'policy'), ('US', 'policy'), ('US', 'growth')},
               CAL_FULL) == 'map_current_period_stale_mix')
    check('§B10④ blocked_class_of: B 问句×无实录→'
          'map_official_target_missing;有实录→None',
          _rep(Q_B, pv_jp, pairs_jp, CAL_EMPTY)
          == 'map_official_target_missing'
          and _rep(Q_B, pv_jp, pairs_jp, CAL_FULL) is None)


# ═══ §B 集成: ③④ 草稿交付+归档拒绝(真实管线路28 基线工单) ═══
def sec_b_pipeline():
    print('═══ §B 集成: 混合/缺实录→草稿交付+归档拒绝(真实管线) ═══')
    # ③ 过期+未核验混合
    T = build_tree('mix')
    rd = fresh_rd('mix')
    p = os.path.join(rd, 'report.json')
    rj = json.load(open(p, encoding='utf-8'))
    for c in (rj['research_plan']['point_values']['cells']):
        if c.get('metric_id') == 'ECB_MRO':
            c['anchors']['最新一期']['freshness'] = 'stale'
        if c.get('metric_id') == 'ECB_DFR':
            c['anchors']['最新一期']['freshness'] = 'unverified'
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(rj, f, ensure_ascii=False, indent=2, default=str)
    aj.record_semantic_verdict(T, rd, 'UPHELD', reviewer='r28gate-mix席',
                               notes='R28 任务2 情景③: 混合当期裁决基线')
    rc1, d1 = cli('report', rd, T)
    dd1 = d1.get('data') or {}
    check('§B11③ 真实管线: 混合当期→rc=1+草稿交付+blocked='
          'map_current_period_stale_mix',
          rc1 != 0 and dd1.get('draft_delivered') is True
          and dd1.get('blocked_class') == 'map_current_period_stale_mix'
          and dd1.get('deliverable') is False,
          f"rc={rc1} draft={dd1.get('draft_delivered')} "
          f"bc={dd1.get('blocked_class')}")
    rc2, d2 = cli('archive', rd, T, arc=os.path.join(TMPG, 'arc_mix'))
    check('§B12③ 归档拒绝: 草稿≠正稿(not_deliverable belt)',
          rc2 != 0 and (d2.get('data') or {}).get('blocked')
          == 'not_deliverable',
          f"rc={rc2} blocked={(d2.get('data') or {}).get('blocked')}")
    # ④ 缺指定官方目标(B 换问×日历无日银实录)——run.question 变更后
    # 同步再生 report.md/移除 FULL_REPORT(多副本一致性自建,§D1 同法)
    T2 = build_tree('gap')
    strip_policy_entries(os.path.join(T2, 'config', 'release_calendar.json'),
                         {'JP_POLICY_TARGET'})
    rd2 = fresh_rd('gap')
    p2 = os.path.join(rd2, 'report.json')
    rj2 = json.load(open(p2, encoding='utf-8'))
    rj2['run']['question'] = Q_B
    with open(p2, 'w', encoding='utf-8') as f:
        json.dump(rj2, f, ensure_ascii=False, indent=2, default=str)
    import research_orchestrator as _ro
    with open(os.path.join(rd2, 'report.md'), 'w', encoding='utf-8') as f:
        f.write(_ro._render_md(rj2))
    _fp2 = os.path.join(rd2, 'FULL_REPORT.md')
    if os.path.exists(_fp2):
        os.remove(_fp2)
    aj.record_semantic_verdict(T2, rd2, 'UPHELD', reviewer='r28gate-gap席',
                               notes='R28 任务2 情景④: 缺实录裁决基线')
    rc3, d3 = cli('report', rd2, T2)
    dd3 = d3.get('data') or {}
    warns3 = ' '.join(str(w) for w in (d3.get('warnings') or []))
    check('§B13④ 真实管线: B 换问×无实录→rc=1+草稿+点名缺口+归档拒绝',
          rc3 != 0 and dd3.get('draft_delivered') is True
          and dd3.get('blocked_class') == 'map_official_target_missing'
          and '官方目标' in warns3
          and cli('archive', rd2, T2,
                  arc=os.path.join(TMPG, 'arc_gap'))[1]
          .get('data', {}).get('blocked') == 'not_deliverable',
          f"rc={rc3} draft={dd3.get('draft_delivered')} "
          f"bc={dd3.get('blocked_class')}")


# ═══ §C 任务3: 历史回答(同步面+相对日期契约) ═══
def sec_c():
    print('═══ §C 任务3: 地区×维度同步面+相对日期双规则 ═══')
    rj = json.load(open(os.path.join(R23_SRC, 'report.json'),
                        encoding='utf-8'))
    jd = json.load(open(os.path.join(R23_SRC, 'agent_judgment.json'),
                        encoding='utf-8'))
    hp = (jd.get('reader_map') or {}).get('history_periods') or []
    face = rmp.history_region_sync_face(hp, rj)
    ok_lab = {'同步', '同步(双持平)', '分化', '缺证'}
    periods = face.get('periods') or []
    rows_all = [r for p in periods for r in p['rows']]
    check('§C1 同步面: 真实工单逐段 12 行(美中欧日×三维度),标签族='
          '同步/同步(双持平)/分化/缺证,美国行=基准(美国类比锚)或'
          '缺证,非缺证行带两端值+两端公布日',
          len(periods) == len(hp)
          and len(rows_all) == 12 * len(hp)
          and all(r.get('label_sync') in (ok_lab | {'基准(美国类比锚)'})
                  for r in rows_all)
          and all(r.get('label_sync') in ('基准(美国类比锚)', '缺证')
                  for r in rows_all if r.get('region') == 'US')
          and all(r.get('prior_value') is not None
                  and r.get('cutoff_value') is not None
                  and r.get('prior_pub') and r.get('cutoff_pub')
                  for r in rows_all
                  if r.get('label_sync') not in ('缺证',)),
          f"periods={len(periods)} rows={len(rows_all)}")
    # 第一段(2021-04)信封覆盖→全判;第二段(2016-09)截止早于信封
    # 起点→逐行诚实缺证并点名理由(不以相邻维度冒充)
    lab0 = [r.get('label_sync') for r in periods[0]['rows']]
    lab1 = [r.get('label_sync') for r in periods[1]['rows']]
    rs1 = ' '.join(str(r.get('reason')) for r in periods[1]['rows'])
    check('§C2 分段如实: 覆盖段零缺证+分化/同步齐现;未覆盖段全 12 行'
          '缺证+点名(无可见观测/美国同维基准缺证)',
          '缺证' not in lab0 and '分化' in lab0
          and '同步' in [l[:2] for l in lab0]
          and lab1.count('缺证') == 12
          and '无可见观测' in rs1 and '基准缺证' in rs1,
          f"p0={sorted(set(lab0))} p1缺证={lab1.count('缺证')}")
    # 相对日期双规则(r23 夹具;基线含 R25+ 时代既档违例,断言取增量)
    def contract(mutate):
        jd2 = copy.deepcopy(jd)
        mutate(jd2)
        res = verify_judgment(jd2, rj, face=build_face(rj))
        return [str(f.get('item')) for f in (res.get('map_checks') or [])
                if f.get('status') != 'VERIFIED']

    base_items = contract(lambda j: None)
    check('§C3 基线增量干净: r23 夹具基线不含 R28 两规则违例'
          '(既档违例如实在册,非本轮回归)',
          not any('relative_expost_in_asof_segment' in i
                  or 'relative_without_absolute_anchor' in i
                  for i in base_items),
          str([i[:60] for i in base_items][:3]))

    def _sim_rel(j2):
        h = j2['reader_map']['history_periods'][0]
        h['similarity'] = str(h.get('similarity') or '') \
            + ';此后 3 个月继续回落(相对事后引用反例)'

    items = contract(_sim_rel)
    check('§C4 相对事后引用拒绝写回当时段(similarity 含「此后 N 个月」'
          '→contra)',
          any('.relative_expost_in_asof_segment' in i for i in items),
          str([i[:70] for i in items
               if 'relative' in i][:2]))

    def _exo_noanchor(j2):
        h = j2['reader_map']['history_periods'][0]
        h['ex_post']['6m'] = str(h.get('ex_post', {}).get('6m') or '') \
            + ';此后 6 个月口径外未复核。'

    items2 = contract(_exo_noanchor)
    check('§C5 ex_post 相对窗口须携带绝对年月锚(无锚→contra)',
          any('relative_without_absolute_anchor' in i for i in items2),
          str([i[:70] for i in items2 if 'relative' in i][:2]))

    def _exo_anchor(j2):
        h = j2['reader_map']['history_periods'][0]
        h['ex_post']['6m'] = str(h.get('ex_post', {}).get('6m') or '') \
            + ';2021-10 之后此后 6 个月口径外未复核(锚已点名)。'

    items3 = contract(_exo_anchor)
    check('§C6 正例: 同句带绝对年月锚(±60 字窗)→该规则不触发',
          not any('relative_without_absolute_anchor' in i for i in items3),
          str([i[:70] for i in items3 if 'relative' in i][:2]))

    # 渲染冒烟: 真实工单按当前渲染器全量重渲不异常+新面在档
    text = rmp.render_map_report(rj, jd, None, root=ROOT)
    check('§C7 渲染冒烟: 政策官方记录面+按生效日列+同步面全部落版'
          '(r23 历史段早于 LPR 实录月,时刻列缺席=如实)',
          '政策官方记录面' in text and '距上次调整(按生效日)' in text
          and '地区×维度同步面' in text and '无可见观测' in text,
          f"len={len(text)}")


# ═══ §D 任务4: 离线重放 ═══
def sec_d():
    print('═══ §D 任务4: 离线重放四门(逐字节/重复/缺件/篡改/漂移/版本) ═══')
    # ── D1 严格逐字节路径: 包与重放代码同版 ──
    T1 = build_tree('d1')
    rd = fresh_rd('d1')
    rewrite_head(rd, WORKTREE_HEAD)
    cli('report', rd, T1)
    aj.record_semantic_verdict(T1, rd, 'UPHELD',
                               reviewer='r28gate-replay席',
                               notes='R28 任务4: 逐字节重放基线裁决')
    rc2, _ = cli('report', rd, T1)
    arc = os.path.join(TMPG, 'arc_d1')
    rc3, d3 = cli('archive', rd, T1, arc=arc)
    man = json.load(open(os.path.join(arc, 'ARCHIVE_MANIFEST.json'),
                         encoding='utf-8'))
    check('§D1a 基线包就绪: report→裁决→report→archive 全链 rc=0'
          '(drift=False,运行 SHA=当前 HEAD)',
          rc2 == 0 and rc3 == 0 and man.get('map_renderer_drift') is False
          and man.get('run_code_git_head') == WORKTREE_HEAD,
          f"rc2={rc2} rc3={rc3} drift={man.get('map_renderer_drift')}")
    rc4, rep = replay(arc, T1, out=os.path.join(TMPG, 'rp_d1a'))
    dd = rep.get('data') or {}
    check('§D1b 一条命令离线重放: rc=0+render_mode=byte_equal+'
          '全检查过+REPLAY_REPORT 落档',
          rc4 == 0 and dd.get('render_mode') == 'byte_equal'
          and dd.get('failed_checks') == []
          and os.path.isfile(os.path.join(TMPG, 'rp_d1a',
                                          'REPLAY_REPORT.json')),
          f"rc={rc4} mode={dd.get('render_mode')} "
          f"failed={dd.get('failed_checks')}")
    # ── D2 重复运行保留原档 ──
    arc_map_sha = hashlib.sha256(
        open(os.path.join(arc, 'MAP_REPORT.md'), 'rb').read()).hexdigest()
    time.sleep(1.2)
    rc5, rep5 = replay(arc, T1)
    dd5 = rep5.get('data') or {}
    out5 = dd5.get('replay_out') or ''
    check('§D2 重复运行: 缺省输出各开新档(时间戳目录)+原包零写入'
          '(MAP 字节/摘要复核)+已存在目录拒绝',
          rc5 == 0 and out5 and out5 != os.path.join(TMPG, 'rp_d1a')
          and os.path.isfile(os.path.join(out5, 'REPLAY_REPORT.json'))
          and hashlib.sha256(
              open(os.path.join(arc, 'MAP_REPORT.md'), 'rb').read()
          ).hexdigest() == arc_map_sha
          and aj.content_digest(arc) == man.get('content_sha256')
          and replay(arc, T1, out=os.path.join(TMPG, 'rp_d1a'))[0] != 0,
          f"out={out5}")
    # ── D3 缺件拒绝 ──
    pkg = os.path.join(TMPG, 'pkg_miss')
    shutil.copytree(arc, pkg)
    os.remove(os.path.join(pkg, 'views_digest.json'))
    rc6, rep6 = replay(pkg, T1, out=os.path.join(TMPG, 'rp_miss'))
    det6 = ' '.join(str(c.get('detail')) for c in
                    ((rep6.get('data') or {}).get('checks') or []))
    check('§D3a 缺件拒绝: rc=1+completeness_files FAIL+点名缺失件',
          rc6 != 0 and 'completeness_files' in (
              (rep6.get('data') or {}).get('failed_checks') or [])
          and 'views_digest.json' in det6, f"rc={rc6}")
    pkg2 = os.path.join(TMPG, 'pkg_vmiss')
    shutil.copytree(arc, pkg2)
    vf = sorted(os.listdir(os.path.join(pkg2, 'verdicts')))[0]
    os.remove(os.path.join(pkg2, 'verdicts', vf))
    rc7, rep7 = replay(pkg2, T1, out=os.path.join(TMPG, 'rp_vmiss'))
    det7 = ' '.join(str(c.get('detail')) for c in
                    ((rep7.get('data') or {}).get('checks') or []))
    check('§D3b 裁决链缺档拒绝: rc=1+点名 verdicts 档名',
          rc7 != 0 and vf in det7, f"rc={rc7} vf={vf}")
    # ── D4 篡改拒绝 ──
    pkg3 = os.path.join(TMPG, 'pkg_tamper_map')
    shutil.copytree(arc, pkg3)
    with open(os.path.join(pkg3, 'MAP_REPORT.md'), 'a',
              encoding='utf-8') as f:
        f.write('\n篡改尾注\n')
    rc8, rep8 = replay(pkg3, T1, out=os.path.join(TMPG, 'rp_tmap'))
    fc8 = (rep8.get('data') or {}).get('failed_checks') or []
    check('§D4a 篡改拒绝(地图): rc=1+全文件锚 FAIL(锚≠实测)',
          rc8 != 0 and 'map_fullfile_anchor' in fc8, str(fc8))
    pkg4 = os.path.join(TMPG, 'pkg_tamper_rj')
    shutil.copytree(arc, pkg4)
    p4 = os.path.join(pkg4, 'report.json')
    rj4 = json.load(open(p4, encoding='utf-8'))
    rj4['run']['ts_utc'] = '19990101T000000Z'
    with open(p4, 'w', encoding='utf-8') as f:
        json.dump(rj4, f, ensure_ascii=False, indent=2, default=str)
    rc9, rep9 = replay(pkg4, T1, out=os.path.join(TMPG, 'rp_trj'))
    fc9 = (rep9.get('data') or {}).get('failed_checks') or []
    check('§D4b 篡改拒绝(冻结输入): rc=1+copies_sha16+content_digest'
          ' 双 FAIL(expected/actual 点名)',
          rc9 != 0 and 'copies_sha16_match' in fc9
          and 'content_digest_match' in fc9, str(fc9))
    # ── D5 渲染器漂移披露桥(变渲染不改摘要的冻结包) ──
    T2 = build_tree('d5')
    rd2 = fresh_rd('d5')
    rewrite_head(rd2, WORKTREE_HEAD)
    cli('report', rd2, T2)
    aj.record_semantic_verdict(T2, rd2, 'UPHELD',
                               reviewer='r28gate-drift席',
                               notes='R28 任务4: 漂移披露基线裁决')
    cli('report', rd2, T2)
    strip_policy_entries(
        os.path.join(T2, 'config', 'release_calendar.json'),
        {'JP_POLICY_TARGET'})
    rcd, dd_d = cli('report', rd2, T2)
    arc5 = os.path.join(TMPG, 'arc_d5')
    rc10, _ = cli('archive', rd2, T2, arc=arc5)
    man5 = json.load(open(os.path.join(arc5, 'ARCHIVE_MANIFEST.json'),
                          encoding='utf-8'))
    check('§D5a 漂移包就绪: 变渲染(日历去实录)不改摘要→冻结分支+'
          'drift=True 归档(rc=0)',
          rcd == 0 and (dd_d.get('data') or {}).get('deliverable') is True
          and rc10 == 0 and man5.get('map_renderer_drift') is True,
          f"rcd={rcd} drift={man5.get('map_renderer_drift')}")
    rc11, rep11 = replay(arc5, T2, out=os.path.join(TMPG, 'rp_d5'))
    check('§D5b 声明漂移的包: 受审冻结字节权威,重渲差异披露不判负'
          '(rc=0+drift_disclosed)',
          rc11 == 0 and (rep11.get('data') or {})
          .get('render_mode') == 'drift_disclosed',
          f"rc={rc11} mode={(rep11.get('data') or {}).get('render_mode')}")
    # ── D6 代码版本门(包≠当前代码) ──
    T6 = build_tree('d6', with_fixture_verdicts=True)
    rd6 = fresh_rd('d6')
    cli('report', rd6, T6)
    arc6 = os.path.join(TMPG, 'arc_d6')
    rc12, _ = cli('archive', rd6, T6, arc=arc6)
    rc13, rep13 = replay(arc6, T6, out=os.path.join(TMPG, 'rp_d6'))
    d13 = rep13.get('data') or {}
    check('§D6a 代码版本门: 包记录 SHA≠当前 HEAD→拒(rc=1+'
          'code_version_mismatch+不落输出目录)',
          rc12 == 0 and rc13 != 0
          and d13.get('blocked') == 'code_version_mismatch'
          and 'replay_out' not in d13,
          f"rc12={rc12} rc13={rc13} blocked={d13.get('blocked')}")
    rc14, rep14 = replay(arc6, T6, out=os.path.join(TMPG, 'rp_d6b'),
                         extra=['--allow-code-mismatch'])
    check('§D6b --allow-code-mismatch: 显式越过降级为披露(rc=0,'
          '版本差异在检查明细)',
          rc14 == 0 and any(
              c.get('check') == 'code_version_match'
              and '披露越过' in str(c.get('detail'))
              for c in ((rep14.get('data') or {}).get('checks') or [])),
          f"rc={rc14}")


def main():
    sec_a()
    sec_b()
    sec_b_pipeline()
    sec_c()
    sec_d()
    n_ok = sum(1 for _, ok, _ in RESULTS if ok)
    print(f"\n==== Audit-R28 gate: {n_ok}/{len(RESULTS)} PASS ====")
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"  FAIL {name} — {detail}")
    return 0 if n_ok == len(RESULTS) else 1


if __name__ == '__main__':
    sys.exit(main())
