#!/usr/bin/env python3
"""Audit-R29 门 — 全球宏观变化地图正式使用续收尾四任务。

任务1 EA 接通: FRED EA GDP 瞬时故障重试(单次 SSL EOF 不再吞整日面)
  + ea 面 series→研究快照 series_store 入库链 + run_daily 常规步在场。
任务2 开放问句: 地区简称(枚举守卫: 、-列表/≥3字并排/双字+数量词)
  +隐含比较维度(宏观环境/分化→全维族)+检测/计划/句段三处同源。
任务3 时点口径: BOJ 决议 09-18/生效 09-24/维持 10-30 只刷核验+
  距上次调整按生效日 58 天(生产日历=基线对照);LPR 官方 09:00 三处
  统一;历史两端各按可知截止+2022-03 锚不泄漏+同比缺基期=缺证+
  同期重复观测确定性+相对日期事后事实绑事件日。
任务4 冻结重放: 渲染依赖(日历+快照+注册表)随运行目录/归档包冻结
  (root_overlay/)+席位终裁绑定冻结摘要+干净目录严格重放逐字节+
  更换本地日历重放不变+重复重放保留原档+缺件/篡改/摘要失配拒绝。
"""
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
import research_orchestrator as ro               # noqa: E402
import workbench_data as wd                      # noqa: E402

TMPG = tempfile.mkdtemp(prefix='r29gate_')
RESULTS = []
R23_SRC = os.path.join(ROOT, 'docs', 'autonomous-rd',
                       'r23-evidence', 'acceptance')
RUN_FILES = ['report.json', 'report.md', 'FULL_REPORT.md',
             'agent_judgment.json', 'views_digest.json',
             'evidence_index.json', 'AGENT_SEAT_ENVELOPE.json',
             'MAP_REPORT.md', 'MAP_REPORT.sha256']
WORKTREE_HEAD = subprocess.run(
    ['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True,
    text=True, timeout=30).stdout.strip()

Q_OPEN = ('2026年11月,美、欧、中、日四地的宏观环境相比三个月前,哪些'
          '经济体之间出现了明显分化?分化主要体现在哪些维度?请给出具体'
          '数据和各数据的公布时间,并说明哪些维度证据不足以下结论。')
Q_NEW = ('2026年11月,美、日两地的宏观基本面相比三个月前有什么不同?'
         '哪些方面分化最明显,哪些方面证据还不足?请附数据与公布时间。')


def check(name, ok, detail=''):
    ok = bool(ok)
    RESULTS.append(ok)
    print(('  ✅ ' if ok else '  ❌ ') + name +
          (' — ' + str(detail) if detail else ''))
    return ok


# ═══ §A 任务1: EA_REAL_GDP_YOY 接通 ═══
def sec_a():
    print('═══ §A 任务1: EA_REAL_GDP_YOY 接通(重试+入库链+常规步) ═══')
    import ea_market_collector as emc
    # A1 瞬时故障重试: 首次 SSL EOF→重试成功(告警如实记录)
    _raw = (b'observation_date,CLVMEURSCAB1GQEA19\n'
            b'1996-01-01,100.0\n1996-04-01,101.0\n1997-01-01,104.5')
    _calls = {'n': 0}

    def _flaky(url, headers):
        _calls['n'] += 1
        if _calls['n'] == 1:
            import urllib.error
            raise urllib.error.URLError(
                'EOF occurred in violation of protocol (_ssl.c:1129)')
        return _raw

    _orig = emc._open_url_with
    emc._open_url_with = _flaky
    try:
        rows, alerts = emc.fetch_ea_real_gdp_yoy()
    finally:
        emc._open_url_with = _orig
    check('§A1 瞬时 TLS 失败一次→重试成功(123 季链路不再被单次 '
          'SSL EOF 吞掉;重试如实入告警)',
          rows is not None and len(rows) == 1 and _calls['n'] == 2
          and any('第 2 次尝试成功' in a for a in alerts),
          f"n_rows={len(rows) if rows else None} calls={_calls['n']} "
          f"alerts={alerts}")
    # A1b 三次全败→READ_FAIL 如实(不虚构)
    emc._open_url_with = lambda u, h: (_ for _ in ()).throw(
        OSError('boom'))
    try:
        rows2, alerts2 = emc.fetch_ea_real_gdp_yoy()
    finally:
        emc._open_url_with = _orig
    check('§A1b 全部尝试失败→(None,告警点名 3 次)诚实缺席',
          rows2 is None and any('3 次尝试均失败' in a for a in alerts2),
          f"rows={rows2} n_alerts={len(alerts2)}")
    # A2 ea 面 series → 研究快照 series_store 入库链
    d = os.path.join(TMPG, 'eaface')
    dd = os.path.join(d, 'data', 'daily')
    os.makedirs(dd)
    json.dump({'date': '20261121', 'version': 'r29gate',
               'series': {'EA_REAL_GDP_YOY': {
                   'dates': ['2025-07-01', '2026-04-01', '2026-07-01'],
                   'values': [1.2, 1.19, 1.28],
                   'note': 'R29 门合成(离线)'}},
               'synthetic': True},
              open(os.path.join(dd, 'ea_20261121.json'), 'w',
                   encoding='utf-8'), ensure_ascii=False)
    import snapshot_builder as sb
    sb.build_snapshot(target_ymd='20261121', data_dir=dd, out_dir=dd,
                      as_of='2026-11-21T09:00:00+08:00', trusted_root=d)
    snap = json.load(open(os.path.join(
        dd, 'research_snapshot_20261121.json'), encoding='utf-8'))
    e = (snap.get('series_store') or {}).get('EA_REAL_GDP_YOY') or {}
    check('§A2 ea 面 series.EA_REAL_GDP_YOY → 快照 series_store 入库'
          '(常规更新→研究快照同一链;123 季实拉即此通道)',
          e.get('dates') == ['2025-07-01', '2026-04-01', '2026-07-01']
          and e.get('values') == [1.2, 1.19, 1.28],
          f"n={len(e.get('dates') or [])}")
    # A3 常规更新步在场(run_weekly 常规链含 ea 采集)
    rw_txt = open(os.path.join(ROOT, 'run_weekly.py'), encoding='utf-8').read()
    check('§A3 run_weekly 常规步: ea_market_collector 在更新白名单',
          'ea_market_collector' in rw_txt)


# ═══ §B 任务2: 开放问句(简称+隐含维度) ═══
def sec_b():
    print('═══ §B 任务2: 地区简称+隐含比较维度 ═══')
    pos = [('美、欧、中、日四地', ['US', 'EA', 'CN', 'JP']),
           ('美,欧两地', ['US', 'EA']),
           ('美欧中日对比', ['US', 'EA', 'CN', 'JP']),
           ('欧美两地的通胀', ['US', 'EA']),
           ('中美两国增长对比', ['CN', 'US'])]
    for q, want in pos:
        got = wd.economy_abbrev_hits(q)
        check(f'§B1 简称正例「{q}」→ {"/".join(want)}',
              sorted(got) == sorted(want), f"got={got}")
    for q in ('其中完美日子里的数据', '请分析完美的中式餐饮',
              '日本央行政策利率', '美国与欧元区的增长'):
        got = wd.economy_abbrev_hits(q)
        check(f'§B1 简称反例「{q[:12]}…」→ 零命中(枚举守卫防误报)',
              got == [], f"got={got}")
    ent = ro.map_entities(Q_OPEN, wd.load_registry(ROOT))
    check('§B2 orchestrator 经济体识别: 开放问句(简称)→四地全中'
          '(不再漏检成默认面 US+CN)',
          sorted(ent['economies']) == ['CN', 'EA', 'JP', 'US'],
          f"ecos={ent['economies']}")
    check('§B3 detect_map_question(开放问句)→True(隐含全维族+形状词'
          '「环境」)',
          rmp.detect_map_question(Q_OPEN, ent) is True)
    reqs = rmp._clause_region_dimension_requests(
        Q_OPEN, ['US', 'EA', 'CN', 'JP'])
    check('§B4 句段请求: 4 地区×3 维=12 组(隐含展开,零显式维度词形)',
          len(set(reqs)) == 12
          and {d for _e, d in reqs} == {'growth', 'inflation', 'policy'},
          f"n={len(set(reqs))}")
    plan = rmp.plan_map(Q_OPEN, ent, wd.load_registry(ROOT)['by_id'],
                        '2026-11-21')
    check('§B5 plan 落档 dimension_source=implicit_macro_environment'
          '(读者可核网格为何如此)',
          plan.get('dimension_source', '').startswith(
              'implicit_macro_environment'),
          plan.get('dimension_source'))
    check('§B6 未参与调试的新问(美、日+宏观基本面)同形态→识别+12→'
          '2 地区×3 维',
          rmp.detect_map_question(
              Q_NEW, ro.map_entities(Q_NEW, wd.load_registry(ROOT)))
          is True
          and len(set(rmp._clause_region_dimension_requests(
              Q_NEW, ['US', 'JP']))) == 6)
    for q in ('美国、中国、欧元区、日本的情况怎么样',
              '美国12个月前和3个月前的增长和通胀如何'):
        check(f'§B7 近失「{q[:14]}…」→ 非地图(无形状词不误触发)',
              rmp.detect_map_question(
                  q, ro.map_entities(q, wd.load_registry(ROOT))) is False)


# ═══ §C 任务3: 时点口径 ═══
def sec_c():
    print('═══ §C 任务3: BOJ 生效日/LPR 09:00/历史两端+四回归 ═══')
    import freshness_policy as fp
    st = fp.policy_decision_state('JP_POLICY_TARGET', '2026-11-21')
    check('§C1 BOJ: 决议 09-18/生效 09-24/目标 1.25——距上次调整 58 天'
          '按**生效日**(非决议日 64)',
          st.get('last_decision') == '2026-09-18'
          and st.get('last_effective') == '2026-09-24'
          and st.get('official_target') == 1.25
          and st.get('days_since_adjustment') == 58
          and st.get('days_since_decision') == 64,
          f"adj={st.get('days_since_adjustment')} "
          f"dec={st.get('days_since_decision')}")
    check('§C1b 10-30 维持公告只更新确认状态(目标/生效日不动,核验截止'
          '刷新到 10-30;距维持 22 天)',
          st.get('last_maintenance') == '2026-10-30'
          and st.get('last_confirmed_on') == '2026-10-30'
          and st.get('days_since_maintenance') == 22
          and st.get('official_target') == 1.25,
          f"mnt={st.get('last_maintenance')}")
    reg_txt = open(os.path.join(ROOT, 'config', 'metric_registry.json'),
                   encoding='utf-8').read()
    check('§C2 LPR 官方时刻 09:00 三处统一(注册表×2+POLICY_FACE+发布'
          '节奏表零 09:15 残留)',
          reg_txt.count('09:15') == 0
          and '09:00' in rmp.POLICY_FACE['CN_LPR_1Y']['decision']
          and '09:00' in rmp.RELEASE_RULES['CN_LPR_1Y'][2]
          and reg_txt.count('LPR 每月20日 09:00 公布') == 2,
          f"reg_0915={reg_txt.count('09:15')}")
    cal = json.load(open(os.path.join(ROOT, 'config',
                                      'release_calendar.json'),
                         encoding='utf-8'))
    lpr_times = [e.get('time') for e in cal.get('entries', [])
                 if e.get('metric_id') == 'CN_LPR_1Y']
    check('§C2b 日历 LPR 条目 time=09:00(各表同读官方时刻)',
          lpr_times and all(t == '09:00' for t in lpr_times),
          f"times={lpr_times}")

    # ── 历史两端+四回归(合成序列,纯函数面) ──
    def _ser(dates, values):
        return {'dates': dates, 'values': values, 'frequency': 'monthly'}

    # C3 2022-03 锚: 当时可知=可见日≤截止月末(CN_CPI 次月9日发布→
    # 3 月观测 4-09 才可见,截止 03-31 只可见 2 月观测;4 月观测=未来,
    # 不泄漏)
    s = _ser(['2021-11-01', '2022-02-01', '2022-03-01', '2022-04-01'],
             [0.9, 1.1, 1.3, 1.5])
    r1, why1 = rmp._hist_region_reading(
        s, '2022-03', '2022-03-31', 'CN_CPI_YOY', 'direct', 'monthly')
    check('§C3 2022-03 锚不泄漏: 截止 03-31 只见 2 月观测(3 月观测'
          ' 04-09 发布=事后才可知,4 月更不取)',
          r1 is not None and r1[0] == 1.1 and r1[1] == '2022-02-01',
          f"r={r1} why={why1}")
    # C4 同比缺基期: 水平序列基期观测不可见→缺证(no_visible_base),
    # 不虚构同比
    s2 = _ser(['2021-08-01', '2022-05-01'], [100.0, 106.0])
    r2, why2 = rmp._hist_region_reading(
        s2, '2022-06', '2022-06-30', 'CPI', 'level_yoy', 'monthly')
    check('§C4 同比缺基期=缺证(2022-05 观测的 2021-05 基期不在场→'
          'no_visible_base,不编同比)',
          r2 is None and why2 == 'no_visible_base', f"why={why2}")
    # C5 同一期重复观测: 同月多观测取该月最晚观测日(平局后位胜),
    # 确定性=同输入两次调用逐位一致
    s3 = _ser(['2022-01-09', '2022-02-05', '2022-02-28', '2022-02-28'],
              [1.0, 1.2, 1.4, 1.4])
    a1 = rmp._aof_obs_at_month(s3, '2022-02')
    a2 = rmp._aof_obs_at_month(
        _ser(list(s3['dates']), list(s3['values'])), '2022-02')
    check('§C5 同期重复观测确定性: 同月取最晚观测日,重复调用逐位一致'
          '(不随机选值)',
          a1 == ('2022-02-28', 1.4) and a1 == a2, f"a={a1}")
    # C6 相对日期事后事实: 「随后N个月」绑**事件日**前移,非日历截止
    offs = rmp.parse_ex_post_offsets('当时其他经济体是否同步,随后3、6、'
                                     '12个月实际怎么走?')
    check('§C6 相对日期事后事实: 随后3、6、12个月=事件日锚偏移'
          '(anchored_on 事件日,与日历点锚分记)',
          [o['months'] for o in offs] == [3, 6, 12]
          and all(o['kind'] == 'ex_post'
                  and '事件日' in o['anchored_on'] for o in offs))
    # C7 历史两端各按自己的可知截止: 锚−3月端与截止月端分别落位
    # (cutoff 端可见 5 月观测,锚−3月端只见 2 月)
    s4 = _ser(['2022-02-01', '2022-05-01'], [1.1, 1.6])
    rc_, _ = rmp._hist_region_reading(
        s4, '2022-06', '2022-06-30', 'CN_CPI_YOY', 'direct', 'monthly')
    r0_, _ = rmp._hist_region_reading(
        s4, '2022-03', '2022-06-30', 'CN_CPI_YOY', 'direct', 'monthly')
    check('§C7 两端各按可知截止: 截止端=5 月观测/锚−3月端=2 月观测'
          '(不并轨取同一值)',
          rc_[0] == 1.6 and r0_[0] == 1.1,
          f"cutoff={rc_} prior={r0_}")


# ═══ §D 任务4: 冻结输入+严格重放 ═══
def _build_r29_tree(tag):
    T = os.path.join(TMPG, 'tree_' + tag)
    os.makedirs(os.path.join(T, 'data', 'daily'))
    os.makedirs(os.path.join(T, 'config'))
    for fn in ('metric_registry.json', 'release_calendar.json'):
        shutil.copy2(os.path.join(ROOT, 'config', fn),
                     os.path.join(T, 'config', fn))
    return T


def _fresh_rd(tag):
    d = os.path.join(TMPG, 'rd_' + tag)
    os.makedirs(d)
    for f in RUN_FILES:
        shutil.copy2(os.path.join(R23_SRC, f), d)
    return d


def _rewrite_head(rd, head):
    p = os.path.join(rd, 'report.json')
    rj = json.load(open(p, encoding='utf-8'))
    rj['run']['git_head'] = head
    rj['run']['git_head_source'] = 'r29gate_worktree'
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(rj, f, ensure_ascii=False, indent=2, default=str)
    import research_orchestrator as _ro
    with open(os.path.join(rd, 'report.md'), 'w', encoding='utf-8') as f:
        f.write(_ro._render_md(rj))
    fp = os.path.join(rd, 'FULL_REPORT.md')
    if os.path.exists(fp):
        os.remove(fp)


def _inject_frozen(rd, T):
    """R29 冻结面注入: run.frozen_inputs 三件(日历+注册表+运行快照)
    + rd/root_overlay/ 副本(计划段同法;摘要=副本实际字节)。"""
    p = os.path.join(rd, 'report.json')
    rj = json.load(open(p, encoding='utf-8'))
    sid = ((rj.get('layers') or {}).get('L1_事实层') or {}).get(
        'snapshot_id') or 'research_snapshot_20261119'
    snap_path = os.path.join(T, 'data', 'daily', sid + '.json')
    json.dump({'snapshot_id': sid, 'target_date': sid[-8:],
               'series_store': {}, 'synthetic': True,
               'note': 'R29 门冻结面合成快照(离线)'},
              open(snap_path, 'w', encoding='utf-8'), ensure_ascii=False)
    fi = {}
    for rel in ('config/release_calendar.json',
                'config/metric_registry.json',
                'data/daily/%s.json' % sid):
        src = os.path.join(T, rel)
        dst = os.path.join(rd, 'root_overlay', rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        fi[rel] = hashlib.sha256(open(src, 'rb').read()).hexdigest()[:16]
    rj['run']['frozen_inputs'] = fi
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(rj, f, ensure_ascii=False, indent=2, default=str)
    import research_orchestrator as _ro
    with open(os.path.join(rd, 'report.md'), 'w', encoding='utf-8') as f:
        f.write(_ro._render_md(rj))
    return fi


def cli(stage, rd, engine_root, arc=None, extra=None):
    cmd = [sys.executable, 'ia_cli.py', 'research-one', '--stage', stage,
           '--report-dir', rd, '--engine-root', engine_root]
    if arc:
        cmd += ['--archive-dir', arc]
    if extra:
        cmd += extra
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                       timeout=300)
    try:
        return r.returncode, json.loads(r.stdout)
    except (ValueError, TypeError):
        return r.returncode, {'raw': ((r.stdout or '')
                                      + (r.stderr or ''))[-500:]}


def replay(pkg, engine_root, out=None):
    cmd = [sys.executable, 'ia_cli.py', 'research-one', '--stage',
           'replay', '--package', pkg, '--engine-root', engine_root]
    if out:
        cmd += ['--replay-out', out]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                       timeout=300)
    try:
        return r.returncode, json.loads(r.stdout)
    except (ValueError, TypeError):
        return r.returncode, {'raw': ((r.stdout or '')
                                      + (r.stderr or ''))[-500:]}


def sec_d():
    print('═══ §D 任务4: 渲染依赖随包冻结+严格重放五步 ═══')
    T = _build_r29_tree('d1')
    rd = _fresh_rd('d1')
    _rewrite_head(rd, WORKTREE_HEAD)
    fi = _inject_frozen(rd, T)
    agg = aj.frozen_inputs_digest(fi)
    rc_r, d_r = cli('report', rd, T)
    aj.record_semantic_verdict(
        T, rd, 'UPHELD', 'r29gate-seat',
        extra={'frozen_inputs_sha256': agg})
    arc = os.path.join(TMPG, 'arc_d1')
    rc_a, d_a = cli('archive', rd, T, arc=arc)
    man = json.load(open(os.path.join(arc, 'ARCHIVE_MANIFEST.json'),
                         encoding='utf-8'))
    check('§D1 归档携冻结面: root_overlay/ 三件+manifest.frozen_inputs'
          '+聚合摘要==终裁绑定(源摘要匹配终裁)',
          (d_r.get('data') or {}).get('generated') and rc_a == 0
          and sorted(man.get('frozen_inputs') or {}) == sorted(fi)
          and man.get('frozen_inputs_sha256') == agg
          and all(os.path.isfile(os.path.join(arc, 'root_overlay', r))
                  for r in fi),
          f"gen={(d_r.get('data') or {}).get('generated')} "
          f"rc_a={rc_a} n={len(man.get('frozen_inputs') or {})}")
    # D2 干净目录严格重放: 同代码+冻结输入→逐字节
    out2 = os.path.join(TMPG, 'rp_d2')
    rc2, rep2 = replay(arc, T, out=out2)
    d2 = rep2.get('data') or {}
    checks2 = {c.get('check'): c.get('ok') for c in (d2.get('checks') or [])}
    check('§D2 严格重放绿: 逐字节相等+冻结三查+终裁三面绑定全 ok',
          rc2 == 0 and d2.get('render_mode') == 'byte_equal'
          and checks2.get('frozen_inputs_present')
          and checks2.get('frozen_inputs_digests')
          and checks2.get('frozen_inputs_match_report')
          and checks2.get('verdict_binding_threeway')
          and checks2.get('deterministic_rerender'),
          f"rc={rc2} mode={d2.get('render_mode')} "
          f"bad={[k for k, v in checks2.items() if not v]}")
    map_bytes_1 = open(os.path.join(out2, 'MAP_REPLAY_RENDER.md'),
                       'rb').read() \
        if os.path.isfile(os.path.join(out2, 'MAP_REPLAY_RENDER.md')) \
        else None
    pkg_map = open(os.path.join(arc, 'MAP_REPORT.md'), 'rb').read()
    # D3 更换本地日历→重放不变(重渲 root=包内 overlay,非本地)
    cal = os.path.join(T, 'config', 'release_calendar.json')
    orig_cal = open(cal, 'rb').read()
    cdoc = json.loads(orig_cal)
    cdoc['entries'] = (cdoc.get('entries') or []) + [{
        'entry_id': 'R29-SWAP', 'metric_id': 'CN_LPR_1Y',
        'obs_from': '2026-11-01', 'obs_to': '2026-11-30',
        'first_publish_on_or_after': '2026-11-99', 'time': '23:59'}]
    json.dump(cdoc, open(cal, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)
    out3 = os.path.join(TMPG, 'rp_d3')
    rc3, rep3 = replay(arc, T, out=out3)
    d3 = rep3.get('data') or {}
    map_bytes_3 = open(os.path.join(out3, 'MAP_REPLAY_RENDER.md'),
                       'rb').read() \
        if os.path.isfile(os.path.join(out3, 'MAP_REPLAY_RENDER.md')) \
        else b''
    check('§D3 更换本地日历→重放仍逐字节一致(本地现状零影响;且==包内'
          '原档)',
          rc3 == 0 and d3.get('render_mode') == 'byte_equal'
          and map_bytes_1 and map_bytes_3 == map_bytes_1
          and map_bytes_1 == pkg_map,
          f"rc={rc3} mode={d3.get('render_mode')}")
    open(cal, 'wb').write(orig_cal)
    # D4 重复重放: 新输出目录+包零写入
    out4 = os.path.join(TMPG, 'rp_d4')
    rc4, rep4 = replay(arc, T, out=out4)
    d4 = rep4.get('data') or {}
    checks4 = {c.get('check'): c.get('ok') for c in (d4.get('checks') or [])}
    check('§D4 重复重放一致+原档未被触碰(package_untouched_postwrite)',
          rc4 == 0 and d4.get('render_mode') == 'byte_equal'
          and checks4.get('package_untouched_postwrite'),
          f"rc={rc4}")
    # D5 缺件: 摘冻结件→拒
    pkg5 = os.path.join(TMPG, 'arc_d5')
    shutil.copytree(arc, pkg5)
    os.remove(os.path.join(pkg5, 'root_overlay', 'config',
                           'release_calendar.json'))
    rc5, rep5 = replay(pkg5, T, out=os.path.join(TMPG, 'rp_d5'))
    c5 = {c.get('check'): c.get('ok') for c in
          ((rep5.get('data') or {}).get('checks') or [])}
    check('§D5 缺件拒绝: frozen_inputs_present FAIL 在场+整体 rc=1',
          rc5 != 0 and c5.get('frozen_inputs_present') is False,
          f"rc={rc5} present={c5.get('frozen_inputs_present')}")
    # D6 篡改冻结件→拒
    pkg6 = os.path.join(TMPG, 'arc_d6')
    shutil.copytree(arc, pkg6)
    _cp = os.path.join(pkg6, 'root_overlay', 'config',
                       'release_calendar.json')
    _cd = json.load(open(_cp, encoding='utf-8'))
    _cd['version'] = 'tampered'
    json.dump(_cd, open(_cp, 'w', encoding='utf-8'), ensure_ascii=False)
    rc6, rep6 = replay(pkg6, T, out=os.path.join(TMPG, 'rp_d6'))
    c6 = {c.get('check'): c.get('ok') for c in
          ((rep6.get('data') or {}).get('checks') or [])}
    check('§D6 篡改冻结日历→frozen_inputs_digests FAIL+整体拒',
          rc6 != 0 and c6.get('frozen_inputs_digests') is False,
          f"rc={rc6}")
    # D7 manifest 摘要失配(单侧改写 run↔manifest)→拒
    pkg7 = os.path.join(TMPG, 'arc_d7')
    shutil.copytree(arc, pkg7)
    mp7 = os.path.join(pkg7, 'ARCHIVE_MANIFEST.json')
    man7 = json.load(open(mp7, encoding='utf-8'))
    man7['frozen_inputs']['config/release_calendar.json'] = 'deadbeef'
    json.dump(man7, open(mp7, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2, default=str)
    rc7, rep7 = replay(pkg7, T, out=os.path.join(TMPG, 'rp_d7'))
    c7 = {c.get('check'): c.get('ok') for c in
          ((rep7.get('data') or {}).get('checks') or [])}
    check('§D7 manifest 冻结摘要单侧改写→digests/match_report 拒',
          rc7 != 0 and (c7.get('frozen_inputs_digests') is False
                        or c7.get('frozen_inputs_match_report') is False),
          f"rc={rc7}")
    # D8 终裁未绑冻结摘要→归档拒绝(席位没吃到冻结面=交付链不完整)
    T8 = _build_r29_tree('d8')
    rd8 = _fresh_rd('d8')
    _rewrite_head(rd8, WORKTREE_HEAD)
    _inject_frozen(rd8, T8)
    cli('report', rd8, T8)
    aj.record_semantic_verdict(T8, rd8, 'UPHELD', 'r29gate-seat-nobind')
    rc8, d8 = cli('archive', rd8, T8, arc=os.path.join(TMPG, 'arc_d8'))
    _d8 = d8.get('data') or {}
    check('§D8 终裁未绑冻结摘要→归档拒(correlation_failed+点名)',
          rc8 != 0 and _d8.get('blocked') == 'correlation_failed'
          and '冻结输入摘要' in str(_d8.get('error')),
          f"rc={rc8} err={str(_d8.get('error'))[:80]}")


sec_a()
sec_b()
sec_c()
sec_d()
n_fail = RESULTS.count(False)
print()
print('════════════════════════════════════════════════════════════')
print(f'Audit-R29 门: {len(RESULTS) - n_fail} PASS / {n_fail} FAIL '
      f'(共 {len(RESULTS)} 判据)')
sys.exit(1 if n_fail else 0)
