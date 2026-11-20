#!/usr/bin/env python3
"""Audit-R24(R68)门 — 正式使用前收尾五任务。

任务1 归档一致性: 真实工单(R22/R23)×三序列(直接 archive/report 后/
连续两次 report 后)×三快照(原快照/无外部快照/同名快照端点篡改),
已审正文按原字节读取与归档、落盘==裁决核对、原件保留、摘要三处一致;
更正或重排另建版本(--new-map-version)复审。
后续任务节随修复落地追加。
"""
import copy
import hashlib
import json
import os
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

TMPG = tempfile.mkdtemp(prefix='r24gate_')
RESULTS = []

R22_DIR = os.path.join(
    ROOT, 'docs', 'autonomous-rd', 'r22-evidence', 'acceptance',
    '20261119T153709Z_给我一份全球宏观经济变化地图_美国_中国_欧元区_'
    '日本在12个月前_3个月前和最')
R23_SRC = os.path.join(ROOT, 'docs', 'autonomous-rd',
                       'r23-evidence', 'acceptance')
RUN_FILES = ['report.json', 'report.md', 'FULL_REPORT.md',
             'agent_judgment.json', 'views_digest.json',
             'evidence_index.json', 'AGENT_SEAT_ENVELOPE.json',
             'MAP_REPORT.md', 'MAP_REPORT.sha256']
ORDERS = {
    'r22': {'run_ts': '20261119T153709Z', 'n_verdicts': 1,
            'vdir': os.path.join(R22_DIR, 'verdicts')},
    'r23': {'run_ts': '20261119T173248Z', 'n_verdicts': 3,
            'vdir': os.path.join(R23_SRC, 'verdicts')},
}


def check(name, ok, detail=''):
    RESULTS.append((name, bool(ok), str(detail)[:220]))
    print(('  ✅ ' if ok else ' ❌ ') + name
          + (f' — {detail}' if detail else ''), flush=True)


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def frozen_snapshot_from(rj, snap_id, tamper_spx=False):
    store = {}
    for st in rj.get('steps') or []:
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
    return {'snapshot_id': snap_id, 'series_store': store}


SRC_RD, BOUND_MAP, BOUND_DIGEST = {}, {}, {}
for _o, _meta in ORDERS.items():
    d = os.path.join(TMPG, 'src_' + _o)
    os.makedirs(d)
    base = R22_DIR if _o == 'r22' else R23_SRC
    for f in RUN_FILES:
        shutil.copy2(os.path.join(base, f), d)
    SRC_RD[_o] = d
    for i in range(1, _meta['n_verdicts'] + 1):
        v = json.load(open(os.path.join(
            _meta['vdir'],
            f"20261120__VERDICT-{_meta['run_ts']}-0{i}.json"),
            encoding='utf-8'))
        if i == _meta['n_verdicts']:
            BOUND_MAP[_o] = v.get('map_report_sha256')
            BOUND_DIGEST[_o] = v.get('content_sha256')


def build_tree(tag, order, snap_cond):
    """§1 重放树: config+该工单裁决链+(可选)快照,零活数据依赖。"""
    T = os.path.join(TMPG, 'tree_' + tag)
    os.makedirs(os.path.join(T, 'data', 'daily'))
    os.makedirs(os.path.join(T, 'config'))
    for fn in ('metric_registry.json', 'release_calendar.json'):
        shutil.copy(os.path.join(ROOT, 'config', fn),
                    os.path.join(T, 'config', fn))
    meta = ORDERS[order]
    d = os.path.join(T, 'audit', 'semantic_review', '20261120')
    os.makedirs(d)
    for i in range(1, meta['n_verdicts'] + 1):
        shutil.copy(
            os.path.join(meta['vdir'],
                         f"20261120__VERDICT-{meta['run_ts']}-0{i}.json"),
            os.path.join(d, f"VERDICT-{meta['run_ts']}-0{i}.json"))
    if snap_cond != 'none':
        rj = json.load(open(os.path.join(SRC_RD[order], 'report.json'),
                            encoding='utf-8'))
        snap = frozen_snapshot_from(
            rj, 'research_snapshot_20261119',
            tamper_spx=(snap_cond == 'tamper'))
        with open(os.path.join(T, 'data', 'daily',
                               'research_snapshot_20261119.json'),
                  'w', encoding='utf-8') as f:
            json.dump(snap, f)
    return T


def fresh_rd(tag, order):
    d = os.path.join(TMPG, 'rd_' + tag)
    os.makedirs(d)
    for f in RUN_FILES:
        shutil.copy2(os.path.join(SRC_RD[order], f), d)
    return d


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
        data = {'raw': ((r.stdout or '') + (r.stderr or ''))[-300:]}
    return r.returncode, data


# ═══ §1 任务1 归档一致性(3 序列 × 3 快照 × 2 真实工单) ═══
def sec_1():
    print('═══ §1 归档一致性: 已审正文原字节×三序列×三快照×两工单 ═══')
    matrix = {}
    for order in ('r22', 'r23'):
        for cond in ('orig', 'none', 'tamper'):
            for seq in ('direct', 'r1a', 'r2a'):
                tag = f'{order}_{cond}_{seq}'
                T = build_tree(tag, order, cond)
                rd = fresh_rd(tag, order)
                audited = open(os.path.join(rd, 'MAP_REPORT.md'),
                               'rb').read()
                arc = os.path.join(TMPG, 'arc_' + tag)
                steps = {'direct': ['archive'],
                         'r1a': ['report', 'archive'],
                         'r2a': ['report', 'report', 'archive']}[seq]
                last = None
                for st in steps:
                    last = cli(st, rd, T,
                               arc=arc if st == 'archive' else None)
                    if st != 'archive' and last[0] != 0:
                        break
                rc, data = last
                d = data.get('data') or {}
                cell = {
                    'rc': rc, 'deliverable': d.get('deliverable'),
                    'blocked': d.get('blocked'),
                    'map_audited_bytes': (
                        os.path.isfile(os.path.join(arc, 'MAP_REPORT.md'))
                        and open(os.path.join(arc, 'MAP_REPORT.md'),
                                 'rb').read() == audited),
                    'original_retained': open(
                        os.path.join(rd, 'MAP_REPORT.md'),
                        'rb').read() == audited,
                }
                if os.path.isfile(os.path.join(arc,
                                               'ARCHIVE_MANIFEST.json')):
                    man = json.load(open(os.path.join(
                        arc, 'ARCHIVE_MANIFEST.json'), encoding='utf-8'))
                    cell['manifest'] = man.get('content_sha256')
                    cell['map_bound'] = man.get('map_report_sha256')
                    cell['map_arc'] = man.get('map_content_sha256')
                    cell['drift'] = man.get('map_renderer_drift')
                    cell['legacy'] = man.get('map_legacy_no_binding')
                matrix[(order, cond, seq)] = cell
                print(f"  [{tag}] rc={rc} deliv={cell['deliverable']} "
                      f"blocked={cell.get('blocked')} "
                      f"审字节={cell['map_audited_bytes']} "
                      f"原件={cell['original_retained']}")
    for order in ('r22', 'r23'):
        for cond in ('orig', 'none', 'tamper'):
            cells = [matrix[(order, cond, s)]
                     for s in ('direct', 'r1a', 'r2a')]
            check(f'§1 A1 {order}/{cond} 三序列一致(同放行/同拒绝同因)',
                  len({(c['rc'] == 0, c['deliverable'],
                       c.get('blocked')) for c in cells}) == 1
                  and all(c['rc'] == 0 for c in cells),
                  str([(c['rc'], c.get('blocked')) for c in cells]))
            check(f'§1 A2+A4 {order}/{cond} 已审正文按原字节归档+原件保留',
                  all(c['map_audited_bytes'] and c['original_retained']
                      for c in cells))
            if BOUND_MAP[order]:
                check(f'§1 A3 {order}/{cond} 落盘==裁决绑定(归档内容段=='
                      'map_report_sha256;三快照面不进任何字节)',
                      all(c.get('map_bound') == BOUND_MAP[order]
                          and c.get('map_arc') == c.get('map_bound')
                          for c in cells))
            else:
                check(f'§1 A3 {order}/{cond} legacy 无绑定如实注记'
                      '(map_legacy_no_binding=true,不追溯)',
                      all(c.get('legacy') is True for c in cells))
            check(f'§1 A5 {order}/{cond} 摘要三处一致(manifest==裁决绑定)',
                  all(c.get('manifest') == BOUND_DIGEST[order]
                      for c in cells))
            check(f'§1 漂移披露 {order}/{cond} (渲染器漂移入 manifest,'
                  '受审字节不被改写)',
                  all(c.get('drift') is True for c in cells))
    # ── 更正或重排另建版本复审(--new-map-version 正道) ──
    T = build_tree('nv', 'r23', 'orig')
    rd = fresh_rd('nv', 'r23')
    rc, d = cli('report', rd, T,
                extra=['--new-map-version'])
    dd = d.get('data') or {}
    rj2 = json.load(open(os.path.join(rd, 'report.json'),
                         encoding='utf-8'))
    check('§1 新版本正道: --new-map-version 重渲+map_version=2+本轮不交付'
          '(旧裁决待复审)',
          rc != 0 and dd.get('deliverable') is False
          and dd.get('map_version') == 2
          and (rj2.get('research_plan') or {}).get('map_version') == 2
          and any('新地图版本已渲染' in str(w)
                  for w in (d.get('warnings') or [])),
          str([str(w)[:60] for w in (d.get('warnings') or [])[:2]]))
    rc2, d2 = cli('report', rd, T)
    d2d = d2.get('data') or {}
    check('§1 新版本正道: 旧裁决过期(fresh=False→复跑仍拒)',
          rc2 != 0 and d2d.get('deliverable') is False
          and (d2d.get('review') or {}).get('fresh') is False)
    aj.record_semantic_verdict(T, rd, 'UPHELD',
                               reviewer='r24-gate-复审席',
                               notes='R24 任务1: 新版本复审正道')
    rc3, d3 = cli('report', rd, T)
    arc = os.path.join(TMPG, 'arc_nv')
    rc4, d4 = cli('archive', rd, T, arc=arc)
    man = json.load(open(os.path.join(arc, 'ARCHIVE_MANIFEST.json'),
                         encoding='utf-8'))
    check('§1 新版本正道: 复审落新裁决→交付+归档(map_version=2 随档,'
          '双锚=新版本)',
          rc3 == 0 and (d3.get('data') or {}).get('deliverable') is True
          and rc4 == 0 and man.get('map_version') == 2
          and man.get('map_report_sha256')
          == aj.map_report_content_sha(rd)
          and man.get('map_renderer_drift') is False)


# ═══ §2 任务2 历史信息截止(逐期官方实录校正) ═══
def sec_2():
    import datetime as _dt
    print('═══ §2 历史信息截止: EA 两级发布实录+INDPRO 改期+事后政策事件 ═══')

    def vf_pub(mid, od):
        return rmp._aof_first_pub(mid, od, 'monthly')

    # EA 2021-05 / 2022-06 逐期官方实录(快报次月1日+终值)
    for od, flash, final in (('2021-05-31', '2021-06-01', '2021-06-17'),
                             ('2022-06-30', '2022-07-01', '2022-07-19')):
        vf, pub, basis, note = vf_pub('EA_HICP_YOY', od)
        check(f'§2 EA@{od[:7]} 官方实录: 快报{flash}+终值{final}'
              '(basis=calendar:user_directive)',
              vf == flash and pub == final
              and basis.startswith('calendar:RC-EA-HICP-')
              and '官方实录' in note,
              f'vf={vf} pub={pub} basis={basis[:40]}')
    # 月末截止泄漏关闭: 截止月当天快报未出→known=上月, 本月移事后段
    rj_ea = {'steps': [
        {'step': 'S4_history_EA_HICP_YOY', 'envelope': {'data': {'series': {
            'dates': ['2021-04-30', '2021-05-31'],
            'values': [1.6, 2.0], 'frequency': 'monthly'}}}}]}
    p = rmp.history_asof_face(
        [{'anchor_ym': '2021-05', 'judgment_cutoff_ym': '2021-05'}],
        rj_ea)['periods'][0]
    check('§2 EA 2021-05 月末截止: 快报未出→已知=2021-04(1.6),'
          '2021-05(2.0)移事后段(发布纪律=当时不可知)',
          p['known'][0]['obs_month'] == '2021-04'
          and p['known'][0]['value'] == 1.6
          and any(r['obs_month'] == '2021-05' and r['value'] == 2.0
                  and r['visible_from'] == '2021-06-01'
                  and '移入事后段' in str(r.get('delay_note'))
                  for r in p['aftermath']),
          str([(r['obs_month'], r['visible_from'])
               for r in p['aftermath'][:2]]))
    # 前一天/当天边界(逐项)
    flips = [
        ('EA_HICP_YOY', '2021-05-31', '2021-06-01'),
        ('EA_HICP_YOY', '2022-06-30', '2022-07-01'),
        ('INDPRO', '2025-09-30', '2025-12-03'),
        ('CPI', '2025-09-30', '2025-10-24'),
        ('CORE_PCE', '2025-10-31', '2026-01-22'),
        ('CORE_PCE', '2025-11-30', '2026-01-22'),
        ('UNEMPLOYMENT', '2025-11-30', '2025-12-16'),
    ]

    def vis(mid, od, asof):
        vf, _p, _b, _n = rmp._aof_first_pub(mid, od, 'monthly')
        return vf is not None and vf <= asof

    for mid, od, pub in flips:
        d1 = (_dt.date.fromisoformat(pub)
              - _dt.timedelta(days=1)).isoformat()
        check(f'§2 {mid}@{od[:7]}: 前一天{d1}不可见/当天{pub}可见',
              not vis(mid, od, d1) and vis(mid, od, pub), f'pub={pub}')
    # INDPRO 精确实录优先于区间保守界
    vf, pub, basis, _ = vf_pub('INDPRO', '2025-09-30')
    check('§2 INDPRO 2025-09: G.17 官方改期实录 2025-12-03 优先于 '
          'REST-CONSERVATIVE 保守界(最特定条目胜)',
          vf == '2025-12-03'
          and basis.startswith('calendar:RC-2025SHUTDOWN-INDPRO-SEP'),
          f'vf={vf} basis={basis[:48]}')
    vf2, _, b2, _ = vf_pub('INDPRO', '2025-10-31')
    check('§2 INDPRO 2025-10: G.17 合并补发实录 2025-12-23(R25 权威日期'
          '修订: 取代旧保守界 2026-01-22——10+11 月一次补发官方公告)',
          vf2 == '2025-12-23'
          and 'INDPRO-OCTNOV' in b2, f'vf={vf2} basis={b2[:52]}')
    # 缺首发证据: 无条目→规则推定且 basis=rule:推定(如实标注,不冒充
    # 官方实录);规则也给不出→unavailable(不虚构精确日)
    vf3, pub3, b3, _ = vf_pub('XX_NO_EVIDENCE', '2026-01-31')
    import release_calendar as _rc
    _u = _rc.visible_publish_date('XX_NO_EVIDENCE', '2026-01-01', None)
    check('§2 缺首发证据: 无条目→rule:推定随格披露(不冒充实录);'
          '规则也给不出→(None,unavailable) 不虚构',
          b3 == 'rule:推定' and '官方实录' not in b3
          and _u == (None, 'unavailable'),
          f'basis={b3} visible_publish_date={_u}')
    rj_gap = {'steps': [
        {'step': 'S4_history_EA_HICP_YOY', 'envelope': {'data': {'series': {
            'dates': ['2021-05-31'],
            'values': [2.0], 'frequency': 'monthly'}}}}]}
    pg = rmp.history_asof_face(
        [{'anchor_ym': '2021-05', 'judgment_cutoff_ym': '2021-05'}],
        rj_gap)['periods'][0]
    check('§2 缺首发证据(面级): 截止月无可知观测→明确缺口'
          '(absent@2021-05 注明「截至截止月无可知观测」),不编上期;'
          '有上期则展示上期已知值(见 2021-05 两观测探针)',
          any('@2021-05' in a and '无可知观测' in a for a in pg['absent'])
          and not pg['known'],
          str(pg['absent']))
    # 快报/终值/修订/事后事件四态区分(EA 行双官方实录+修订口径)
    check('§2 四态分记: EA 行含快报日+终值日+修订口径(最新修订值族);'
          '政策事件行 kind=policy_event 与延误行分形',
          '官方实录' in str(p['aftermath'][0].get('note') or '')
          and vf_pub('EA_HICP_YOY', '2021-05-31')[1] == '2021-06-17'
          and rmp._aof_revision_note('EA_HICP_YOY').startswith('终值'))
    # 2016-12 美联储决议 → 2016-10 类比的事后段(指令点名)
    rj_fed = {'steps': [
        {'step': 'S4_history_DFEDTARU', 'envelope': {'data': {'series': {
            'dates': ['2016-08-31', '2016-10-31', '2016-12-15',
                      '2017-03-16'],
            'values': [0.5, 0.5, 0.75, 1.0]}}}},
        {'step': 'S4_history_CPI', 'envelope': {'data': {'series': {
            'dates': ['2016-08-31', '2016-09-30', '2016-10-31'],
            'values': [1.06, 1.10, 1.15]}}}}]}
    pf = rmp.history_asof_face(
        [{'anchor_ym': '2016-10', 'judgment_cutoff_ym': '2016-10'}],
        rj_fed)['periods'][0]
    ev = [r for r in pf['aftermath'] if r.get('kind') == 'policy_event']
    check('§2 2016-10 类比: 2016-12 美联储加息(0.5→0.75,观测日'
          '2016-12-15)入事后段=事后政策事件,非当时可知;2017-03 再加息'
          '同列',
          any(r['obs_date'] == '2016-12-15'
              and r['value_from'] == 0.5 and r['value'] == 0.75
              and '事后政策事件' in str(r.get('delay_note'))
              for r in ev)
          and any(r['obs_date'] == '2017-03-16' for r in ev)
          and not any(r.get('obs_date', '') <= '2016-10-31'
                      for r in ev),
          str([(r['obs_date'], r.get('value_from'), r['value'])
               for r in ev]))
    # 渲染面: 事后段标题含「截止后决议」+政策事件行 from→to
    # (history_periods 挂 judgment_doc['reader_map']——装配面契约)
    text = rmp.render_map_report(
        {'steps': rj_fed['steps']},
        {'reader_map': {'history_periods': [
            {'anchor_ym': '2016-10', 'judgment_cutoff_ym': '2016-10',
             'period_label': '2016-10(测试)', 'similarity': 's',
             'difference': 'd', 'other_regions_sync': 'o',
             'ex_post': {}}]}}, {}, root=ROOT)
    check('§2 渲染: 事后段表含政策事件行(0.5→0.75(事后政策事件))',
          '0.5→0.75(事后政策事件)' in text
          and '截止日后才公布/截止后决议' in text,
          text[text.find('事后政策事件') - 60:text.find('事后政策事件') + 20]
          if '事后政策事件' in text else 'absent')


# ═══ §3 任务3 正文数字校验(归属核/池外序列/双单位/指数点/同观测窗) ═══
def sec_3():
    import copy
    print('═══ §3 正文数字校验: 对调拒绝+日本双单位+指数点双记法+无新观测 ═══')
    RJ22 = json.load(open(os.path.join(SRC_RD['r22'], 'report.json'),
                          encoding='utf-8'))
    JD22 = json.load(open(os.path.join(SRC_RD['r22'],
                                       'agent_judgment.json'),
                          encoding='utf-8'))

    def contract(mutate, rj=None):
        jd = copy.deepcopy(JD22)
        mutate(jd)
        _face = build_face(rj or RJ22)
        res = verify_judgment(jd, rj or RJ22, face=_face)
        return res, [f for f in (res.get('map_checks') or [])
                     if f.get('status') != 'VERIFIED']

    res, bad = contract(lambda jd: None)
    check('§3 基线: R22 原文在归属核下仍 VERIFIED(名义97/实际104/'
          '盈亏平衡-7 逐分量对账通过)',
          res.get('verdict') == 'VERIFIED' and not bad,
          f"verdict={res.get('verdict')} bads={[b.get('item') for b in bad]}")

    def swap(jd):
        h = jd['reader_map']['headline_conclusion']
        h = h.replace('名义+97bp', '名义+104bp', 1)
        h = h.replace('实际+104bp', '实际+97bp', 1)
        jd['reader_map']['headline_conclusion'] = h

    res, bad = contract(swap)
    check('§3 反例①: 美债名义+104bp/实际+97bp 对调 → CONTRADICTED'
          '(bp_attributed: 两值都在池内,归属核逐分量对账拒绝)',
          res.get('verdict') == 'CONTRADICTED'
          and any(str(b.get('item')).endswith(
              'headline_conclusion.bp_attributed') for b in bad),
          str([(b.get('item'), str(b.get('note'))[:60]) for b in bad[:2]]))

    # 日本利率: 引擎 JGB10Y 近30日 0.65→1.32 = +67bp
    rj_jp = copy.deepcopy(RJ22)
    rj_jp.setdefault('steps', []).append({
        'step': 'S4_history_JGB10Y',
        'envelope': {'data': {'series': {
            'dates': ['2026-10-16', '2026-10-17', '2026-11-17',
                      '2026-11-18'],
            'values': [0.64, 0.65, 1.31, 1.32],
            'frequency': 'daily'}}}})

    def jp_bp(jd):
        jd['reader_map']['headline_conclusion'] += \
            '；日本利率近30日+67bp'

    res, bad = contract(jp_bp, rj=rj_jp)
    check('§3 正例②: 日本+67bp(池外序列)→ 按引擎 JGB10Y 同窗复算通过'
          '(三利率池只住美债,不在池≠错)',
          res.get('verdict') == 'VERIFIED' and not bad,
          f"bads={[b.get('item') for b in bad]}")

    def jp_pp(jd):
        jd['reader_map']['headline_conclusion'] += \
            '；日本利率近30日上行0.67个百分点'

    res, bad = contract(jp_pp, rj=rj_jp)
    check('§3 正例③: 日本+0.67个百分点 → 精确 pp↔bp 对(×100=67bp)'
          '同窗通过(双单位等价)',
          res.get('verdict') == 'VERIFIED' and not bad,
          f"bads={[b.get('item') for b in bad]}")

    def jp_wrong(jd):
        jd['reader_map']['headline_conclusion'] += \
            '；日本利率近30日上行0.6个百分点'

    res, bad = contract(jp_wrong, rj=rj_jp)
    check('§3 反例④: 日本+0.6个百分点(=60bp≠67bp) → bp_attributed 拦'
          '(双单位等价不放松数值)',
          res.get('verdict') == 'CONTRADICTED'
          and any(str(b.get('item')).endswith(
              'headline_conclusion.bp_attributed') for b in bad),
          str([b.get('item') for b in bad[:2]]))

    # 指数水平双记法: UMCSENT 266.614→271.903 = +5.289 指数点(+1.98%)
    _hp = (JD22['reader_map'].get('history_periods') or [{}])[0]
    _aym = str(_hp.get('judgment_cutoff_ym') or
               _hp.get('anchor_ym') or '')
    _tgt3 = rmp.ex_post_windows(_aym)['3m']
    import calendar as _cal

    def _mend(ym):
        y, m = int(ym[:4]), int(ym[5:7])
        return '%04d-%02d-%02d' % (y, m, _cal.monthrange(y, m)[1])

    def _ym_off(ym, n):
        y, m = int(ym[:4]), int(ym[5:7]) + n
        y += (m - 1) // 12
        m = (m - 1) % 12 + 1
        return '%04d-%02d' % (y, m)

    rj_idx = copy.deepcopy(RJ22)
    rj_idx.setdefault('steps', []).append({
        'step': 'S4_history_UMCSENT',
        'envelope': {'data': {'series': {
            'dates': [_mend(_ym_off(_aym, -3)),
                      _mend(_aym), _mend(_tgt3)],
            'values': [265.0, 266.614, 271.903],
            'frequency': 'monthly'}}}})

    def _exo(txt):
        def f(jd):
            p = jd['reader_map']['history_periods'][0]
            p['ex_post']['3m'] = str(p['ex_post'].get('3m') or '') + txt
        return f

    res, bad = contract(_exo('；UMCSENT +5.29 指数点(266.614→271.903)'),
                        rj=rj_idx)
    check('§3 正例⑤: CPI 类指数主张 +5.29 指数点(水平差)→ 引擎复算 '
          '5.289 通过(0.06 紧容差)',
          res.get('verdict') == 'VERIFIED' and not bad,
          f"bads={[b.get('item') for b in bad]}")
    res, bad = contract(_exo('；UMCSENT +1.98%(266.614→271.903)'),
                        rj=rj_idx)
    check('§3 正例⑥: 同窗 +1.98%(相对幅)→ 复算 1.98% 通过(双记法均可核)',
          res.get('verdict') == 'VERIFIED' and not bad,
          f"bads={[b.get('item') for b in bad]}")
    res, bad = contract(_exo('；UMCSENT +5.29%(266.614→271.903)'),
                        rj=rj_idx)
    check('§3 反例⑦: 指数点值误标 %(5.29%≠1.98%) → ex_post 拦'
          '(单位记法不可互换)',
          res.get('verdict') == 'CONTRADICTED'
          and any('ex_post.3m' in str(b.get('item')) for b in bad),
          str([b.get('item') for b in bad[:2]]))
    res, bad = contract(_exo('；UMCSENT +1.98 指数点(266.614→271.903)'),
                        rj=rj_idx)
    check('§3 反例⑧: 相对幅误标指数点(1.98≠5.289) → ex_post 拦',
          res.get('verdict') == 'CONTRADICTED'
          and any('ex_post.3m' in str(b.get('item')) for b in bad),
          str([b.get('item') for b in bad[:2]]))

    # 渲染面: 同观测窗+指数点记法
    rj_so = {'steps': [{'step': 'S4_history_XX_IDX',
                        'envelope': {'data': {'series': {
                            'dates': ['2026-09-18', '2026-10-18'],
                            'values': [49.2, 49.3],
                            'unit': 'index_point'}}}}]}
    s = rmp._distinguishing_obs(rj_so, '2026-11-19', 'XX_IDX')
    check('§3 同观测窗: 30日窗两端取到同一观测 → 「窗口内无新观测」'
          '+最近两期实际变化另列(不以 0 变化冒充)',
          s and '窗口内无新观测' in s and '最近两期' in s
          and '2026-09-18=49.2→2026-10-18=49.3' in s,
          repr(s))
    rj_rt = {'steps': [{'step': 'S4_history_XX_RT',
                        'envelope': {'data': {'series': {
                            'dates': ['2026-09-18', '2026-10-18'],
                            'values': [2.35, 2.19], 'unit': '%'}}}}]}
    s2 = rmp._distinguishing_obs(rj_rt, '2026-11-19', 'XX_RT')
    check('§3 同观测窗(利率族): 最近两期变化按 bp 记(Δ-16bp),'
          '不误标指数点',
          s2 and '窗口内无新观测' in s and 'Δ-16bp' in s2,
          repr(s2))
    rj_ix = {'steps': [{'step': 'S4_history_XX_IX',
                        'envelope': {'data': {'series': {
                            'dates': ['2026-10-20', '2026-11-18'],
                            'values': [266.614, 271.903],
                            'unit': 'index_point'}}}}]}
    s3 = rmp._distinguishing_obs(rj_ix, '2026-11-19', 'XX_IX')
    check('§3 指数点记法(渲染): 266.614→271.903 写「+5.289 指数点'
          '(+1.98%)」——水平差不再误标 %(Δ5.289% 与 +1.98% 相混的旧缺陷)',
          s3 and '+5.289 指数点(+1.98%)' in s3
          and 'Δ5.289%' not in s3,
          repr(s3))


# ═══ §4 任务4 补齐三个转折(并项后补选交还判断席) ═══
def sec_4():
    import copy
    print('═══ §4 转折补选交还判断席: 同源纯函数+契约强制+渲染面 ═══')
    RJ22 = json.load(open(os.path.join(SRC_RD['r22'], 'report.json'),
                          encoding='utf-8'))
    JD22 = json.load(open(os.path.join(SRC_RD['r22'],
                                       'agent_judgment.json'),
                          encoding='utf-8'))
    _cand = ((RJ22.get('research_plan') or {})
             .get('turning_candidates') or {}).get('candidates') or []
    _turns = (JD22.get('reader_map') or {}).get('turnings') or []
    eps, picks = rmp.turning_merge_and_picks(_turns, _cand)
    check('§4 同源纯函数: R22 工单 并项=2 轮事件+补选=1'
          '(JP_CPI_TOKYO)——与渲染面/R23 门 §F 同判',
          len(eps) == 2 and len(picks) == 1
          and picks[0].get('metric_id') == 'JP_CPI_TOKYO_YOY',
          f'eps={len(eps)} picks={[(p.get("metric_id"), p.get("to_ym")) for p in picks]}')

    def contract(mutate, rj=None):
        jd = copy.deepcopy(JD22)
        mutate(jd)
        _face = build_face(rj or RJ22)
        res = verify_judgment(jd, rj or RJ22, face=_face)
        return res, [f for f in (res.get('map_checks') or [])
                     if f.get('status') != 'VERIFIED']

    # 标记缺席(R22 旧档)→ check17 不追溯
    res, bad = contract(lambda jd: None)
    check('§4 旧档不追溯: 无 turning_supplement_discipline 标记 → '
          'check17 零项(原文复放必须通过)',
          res.get('verdict') == 'VERIFIED'
          and not any('turning_supplement' in str(b.get('item'))
                      for b in (res.get('map_checks') or [])),
          f"verdict={res.get('verdict')}")

    rj_m = copy.deepcopy(RJ22)
    rj_m['research_plan']['turning_supplement_discipline'] = 'r24'

    res, bad = contract(lambda jd: None, rj=rj_m)
    check('§4 反例①: 标记在场+判断席未交还补选 → NOT_VERIFIED'
          '(turning_supplement 逐项强制)',
          res.get('verdict') != 'VERIFIED'
          and any(str(b.get('item')) ==
                  'reader_map.turning_supplement' for b in bad)
          and 'JP_CPI_TOKYO_YOY' in str(bad[0].get('note')),
          str([str(b.get('note'))[:80] for b in bad[:1]]))

    def supp_full(jd):
        jd['reader_map']['turning_supplement'] = [{
            'metric_id': 'JP_CPI_TOKYO_YOY',
            'to_ym': str(picks[0].get('to_ym')),
            'first_mover': '日本先行(东京核心CPI 三个月滚动转正)',
            'follow_or_diverge': '欧元区未跟进(当月核心HICP走平)',
            'resolution_note': '',
            'evidence_gap': ''}]

    res, bad = contract(supp_full, rj=rj_m)
    check('§4 正例②: 补选逐项写明 谁先变+跟进/背离 → VERIFIED',
          res.get('verdict') == 'VERIFIED' and not bad,
          f"bads={[b.get('item') for b in bad]}")

    def supp_honest(jd):
        jd['reader_map']['turning_supplement'] = [{
            'metric_id': 'JP_CPI_TOKYO_YOY',
            'to_ym': str(picks[0].get('to_ym')),
            'first_mover': '',
            'follow_or_diverge': '',
            'resolution_note': '月频序列无法判断中美日先后,分辨率=月',
            'evidence_gap': '缺英国同窗通胀序列,跨国比较证据不全'}]

    res, bad = contract(supp_honest, rj=rj_m)
    check('§4 正例③: 诚实拒答面 → 分辨率界限+缺哪项跨国证据写明即过'
          '(不编谁先变)',
          res.get('verdict') == 'VERIFIED' and not bad,
          f"bads={[b.get('item') for b in bad]}")

    def supp_half(jd):
        jd['reader_map']['turning_supplement'] = [{
            'metric_id': 'JP_CPI_TOKYO_YOY',
            'to_ym': str(picks[0].get('to_ym')),
            'first_mover': '日本先行',
            'follow_or_diverge': '',
            'resolution_note': '', 'evidence_gap': ''}]

    res, bad = contract(supp_half, rj=rj_m)
    check('§4 反例④: 只写谁先变缺「跟进或背离」且无诚实注记 → 拦',
          res.get('verdict') != 'VERIFIED'
          and any(str(b.get('item')) ==
                  'reader_map.turning_supplement' for b in bad),
          str([str(b.get('note'))[:60] for b in bad[:1]]))

    # 渲染面: 补选行交还列(席位供面优先/旧档如实标注)
    T = build_tree('t4', 'r22', 'frozen')

    def _turn_rows(text):
        ls = text.splitlines()
        i0 = next((i for i, l in enumerate(ls)
                   if l.startswith('| 日期 | 指标 |')), None)
        rows = []
        for l in ls[i0 + 1:] if i0 is not None else []:
            if not l.startswith('|'):
                break
            if not l.startswith('|---'):
                rows.append(l)
        return rows

    text_legacy = rmp.render_map_report(RJ22, JD22, None, root=T)
    rows_l = _turn_rows(text_legacy)
    check('§4 渲染(旧档): 补选行如实标「判断席未述此转折」+并项口径'
          '注含交还条款(不虚构席位判断)',
          len(rows_l) == 3
          and any('(引擎补选·非判断席)' in r
                  and '—(判断席未述此转折)' in r for r in rows_l)
          and '补选项交还判断席' in text_legacy,
          f'rows={len(rows_l)}')
    jd_supp = copy.deepcopy(JD22)
    supp_honest(jd_supp)
    jd_supp['reader_map']['turning_supplement'][0].update({
        'first_mover': '日本先行(东京核心CPI 三个月滚动转正)',
        'follow_or_diverge': '欧元区未跟进(当月核心HICP走平)'})
    text_supp = rmp.render_map_report(rj_m, jd_supp, None, root=T)
    rows_s = _turn_rows(text_supp)
    check('§4 渲染(交还面): 补选行 谁先变=日本先行…/跟进或背离=欧元区'
          '未跟进…(席位供面优先,非引擎编)',
          any('(引擎补选·非判断席)' in r and '日本先行' in r
              and '欧元区未跟进' in r for r in rows_s),
          str([r[:110] for r in rows_s if '引擎补选' in r]))
    jd_res = copy.deepcopy(JD22)
    supp_honest(jd_res)
    text_res = rmp.render_map_report(rj_m, jd_res, None, root=T)
    check('§4 渲染(诚实面): 分辨率+缺证据注记进表格(月频…分辨率=月/'
          '缺英国同窗通胀序列)',
          any('引擎补选' in r and '分辨率/证据' in r
              and '分辨率=月' in r and '缺英国同窗通胀序列' in r
              for r in _turn_rows(text_res)),
          str([r[:130] for r in _turn_rows(text_res)
               if '引擎补选' in r]))


# ═══ §5 任务5 pytest 与 CI 两入口(51+ 判据真实执行) ═══
def sec_5():
    print('═══ §5 双入口: pytest 收集子进程真实执行 + CI 直跑 rc 同构 ═══')
    # 反伪绿契约根因(R67 审计发现): r23 门尾部无字面 sys.exit( →
    # conftest.SuiteFile 静态查判「不自执行伪绿」→ pytest 入口恒红,
    # 51 判据在 pytest 面上零执行。修复=入口对齐 r20-r22 同款;本节
    # 在干净子进程里复验两入口都真实执行。
    import subprocess as _sp
    # (r24 门自身不做 pytest 自证——§5 子进程会递归再入本门;其 pytest
    # 兼容由静态面判: 入口同款字面 sys.exit(,与 r20-r23 同契约。)
    p = _sp.run([sys.executable, '-m', 'pytest',
                 os.path.join('tests', 'test_audit_r23_gate.py'), '-q'],
                cwd=ROOT, capture_output=True, text=True, timeout=1800)
    _tail = (p.stdout or '').strip().splitlines()[-1:] or ['']
    _errtail = (p.stderr or '').strip().splitlines()[-1:] or ['']
    check('§5 pytest 入口: r23 门收集为 1 用例且子进程直跑真实执行'
          '(conftest.SuiteFile rc==0 判据;51 判据在 pytest 面真实跑)',
          p.returncode == 0 and '1 passed' in (p.stdout or ''),
          f'rc={p.returncode} {_tail[0][:80]}'
          + (f' stderr:{_errtail[0][:60]}' if p.returncode else ''))
    p2 = _sp.run([sys.executable, os.path.join(ROOT, 'tests',
                                               'test_audit_r23_gate.py')],
                 cwd=ROOT, capture_output=True, text=True, timeout=1800)
    _n51 = (p2.stdout or '').count('  ✅')
    check('§5 CI 入口(同构直跑): r23 门 python3 直跑 rc=0 且 51 判据'
          '逐项打点(两入口同一命令面)',
          p2.returncode == 0 and _n51 == 51,
          f'rc={p2.returncode} ✅数={_n51}')
    _conf = open(os.path.join(ROOT, 'tests', 'conftest.py'),
                 encoding='utf-8').read()
    _g23 = open(os.path.join(ROOT, 'tests', 'test_audit_r23_gate.py'),
                encoding='utf-8').read()
    _g24 = open(os.path.join(HERE, 'test_audit_r24_gate.py'),
                encoding='utf-8').read()
    check('§5 静态面: conftest 反伪绿契约在场+r23/r24 门入口均含字面'
          'sys.exit((静态查通过=收集期可判自执行;CI 直跑面 offline-'
          'tests.yml 逐件 python3 同构)',
          '套件不自执行' in _conf
          and 'sys.exit(' in _g23.split("if __name__ == '__main__':")[-1]
          and 'sys.exit(' in _g24.split("if __name__ == '__main__':")[-1],
          'entry-ok' if "if __name__ == '__main__':" in _g23 else 'no-entry')


SECTIONS = [sec_1, sec_2, sec_3, sec_4, sec_5]


def main():
    for s in SECTIONS:
        s()
    n_pass = sum(1 for _, ok, _ in RESULTS if ok)
    print(f"\nAudit-R24 门: {n_pass} PASS / "
          f"{len(RESULTS) - n_pass} FAIL (共 {len(RESULTS)} 判据)")
    for name, ok, detail in RESULTS:
        if not ok:
            print(f'  ❌ {name} — {detail}')
    return 1 if n_pass != len(RESULTS) else 0


if __name__ == '__main__':
    sys.exit(main())
