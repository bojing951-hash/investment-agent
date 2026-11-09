#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P1-WP-G 验收件: DESIGN §六 L175 + §八.2 L242-L249 验收要点①②③⑤⑥⑦。

① 监测视图=台账+快照+事实层消费,零直读采集档【测试】——毒丸负向: 采集档
   在场(含毒丸标记)与缺席两变体视图逐字节等值+毒丸标记零出现(健康面/衔接面/
   回溯面三面各证);四模块静态零网络 import;
② 断点/缺席如实列示【测试】——通道连续 MISSING streak(无快照日=断链不脑补)/
   新鲜度越限(严格大于;等号=未越限)/事实缺席行(不填0)/无台账无快照如实;
   DEGRADED 消费不改判(语义与 Gate A 一致);
③ 异常→研究任务衔接 append-only+既有 schema【测试】——SCHEMA_MIN_FIELDS 十字段
   可增不可减全在场;economy 条件写(JP 对→'JP');同 task_id 重放=幂等跳过零写入;
   既有档(诱饵+首写档)字节不动;不触发=如实零任务;零 update_thesis_status;
⑤ 实现参数先登记后运行禁回改【测试】——常量=REPORT §零.5 登记字面量;
⑥⑦ LIVE/通知/GLM 面零实现(确认型 DP 未自决)【测试】——静态面扫描: 四模块
   零 launchd/通知/网络/GLM 客户端面;MONITOR_DISCLAIMER 登记文案逐字。

数据纪律(R014-D3/R022): 合成 fixture=唯一数据源(全部 tempfile 临时目录,零读
真实 data/daily/ 与 data/research/);期望值独立手算硬编码[示意],禁自证(不 import
实现侧计算结果充当期望);零网络零模型调用 零凭证零第三方新依赖。定值源=
docs/P1_WP_G_REPORT.md §零.5(登记定值)。fixture→期望值映射: 本文件
make_*_fixture 工厂与 _pair_series/_boundary_series 手算构造器(逐断言组可追溯,
DELIVERY 漂移维护专节登记表同源)。
"""
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest
from datetime import date, timedelta

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
for p in (ROOT, os.path.join(ROOT, 'scripts')):
    if p not in sys.path:
        sys.path.insert(0, p)

import economy_anomaly_rules as ear          # noqa: E402  (被测模块×4=IA-P1-WP-G 交付件)
import monitor_task_bridge as mtb            # noqa: E402
import monitor_history_view as mhv           # noqa: E402
import research_task_manager as rtm          # noqa: E402  (上游既有件)
import routine_health_monitor as rhm         # noqa: E402

YMD = '20990101'                    # [示意] 合成观察日(与真实日历无关)
POISON = 'POISON_G42_MARKER'        # [示意] 采集档毒丸标记(直读即泄漏)

DISCLAIMER_LITERAL = ('常态监测输出=链路健康/数据新鲜度/统计背离描述,非投资建议;'
                      '缺值如实缺席不填0;规则预期符号为登记的机械模型假设。')

D0 = date(2098, 11, 1)              # 序列首日[示意];61 连续自然日→末观测=2098-12-31
DATES61 = [(D0 + timedelta(days=i)).isoformat() for i in range(61)]
LAST = DATES61[-1]                  # '2098-12-31'(61 观测→恰第 61 共同日可评分)
SYNTH_REGISTRY = [                  # [示意] 合成 registry 条目(hermetic;economy=断言锚)
    {'metric_id': 'USDJPY', 'economy': 'JP', 'frequency': 'daily'},
    {'metric_id': 'NIKKEI225', 'economy': 'JP', 'frequency': 'daily'},
    {'metric_id': 'USDCNY', 'economy': 'CN', 'frequency': 'daily'},
    {'metric_id': 'SHCOMP', 'economy': 'CN', 'frequency': 'daily'},
    {'metric_id': 'EURUSD', 'economy': 'EA', 'frequency': 'daily'},
    {'metric_id': 'DAX', 'economy': 'EA', 'frequency': 'daily'},
    {'metric_id': 'CPI', 'economy': 'US', 'frequency': 'monthly',
     'freshness': {'max_calendar_lag_days': 60}},
    {'metric_id': 'FED_FUNDS', 'economy': 'US', 'frequency': 'monthly',
     'freshness': {'max_calendar_lag_days': 60}},
    {'metric_id': 'EA_HICP_YOY', 'economy': 'EA', 'frequency': 'monthly',
     'freshness': {'max_calendar_lag_days': 60}},
]


# ══ 手算序列构造器(唯一数据源;期望值全部独立手算[示意]) ═════════════════

def _pair_series(fx_base, fx_amp, eq_base, eq_amp, dates=DATES61):
    """61 观测构造器: 逐日差分交替 ±amp(奇数日 +amp/偶数日 −amp)。
    fx 差分 = (fx_amp/eq_amp) × eq 差分 → pearson(fx_diff, eq_diff)=±1 精确
    (同因子比例序列,手算非模块生成;60 差分对,交替模式方差>0)。
    60 步净变动=30 对 (+amp,−amp) 相消 → 期末值=期初值 → 窗口变动=0.0%
    (cond_move 恒 False,触发归因唯一落在 cond_corr)。"""
    fx, eq, a, b = [fx_base], [eq_base], fx_base, eq_base
    for i in range(1, len(dates)):
        sign = 1 if i % 2 == 1 else -1
        a += sign * fx_amp
        b += sign * eq_amp
        fx.append(a)
        eq.append(b)
    return {'dates': list(dates), 'values': fx}, {'dates': list(dates), 'values': eq}


def _boundary_series():
    """cond_move 含等号边界构造器(JP): 61 观测;前 60 值线性 +1/日,末日跳变。
    fx=100..159,102 → chg_fx_pct=round((102/100−1)×100,4)=+2.0(恰达阈,含等号);
    eq=200..259,196 → chg_eq_pct=−2.0(s=+1→s×chg_eq=−2.0 恰达反向阈);
    差分两族([+1]×59+大负跳)高度正相关 → rho>0 → JP(s=+1) cond_corr=False
    → triggered 纯经 cond_move 边界等号(手算)。"""
    fx = {'dates': list(DATES61), 'values': [100 + k for k in range(60)] + [102]}
    eq = {'dates': list(DATES61), 'values': [200 + k for k in range(60)] + [196]}
    return fx, eq


def _store(fx, eq, fx_id='USDJPY', eq_id='NIKKEI225'):
    return {fx_id: fx, eq_id: eq}


def _sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()


def _rmtree(p):
    shutil.rmtree(p, ignore_errors=True)


# ══ 合成 fixture 工厂(唯一数据源;全部[示意]) ═══════════════════════════

def _write_snapshot(daily, ymd, sources_status=None, facts=None, series_store=None,
                    snapshot_id=None):
    # sources_status=Gate A 写档形态(通道→{'status': …}dict,snapshot_builder
    # L282-L301 同构);本工厂接受裸字符串映射并包装[示意]
    st = {ch: (v if isinstance(v, dict) else {'status': v})
          for ch, v in (sources_status or {}).items()}
    snap = {'snapshot_id': snapshot_id or f'research_snapshot_{ymd}',
            'target_date': ymd, 'facts': facts or [], 'series_store': series_store or {},
            'sources_status': st, 'gate_a': {'status': 'DEGRADED'}}
    with open(os.path.join(daily, f'research_snapshot_{ymd}.json'), 'w',
              encoding='utf-8') as f:
        json.dump(snap, f, ensure_ascii=False)


def _write_ledger(logs, ymd, critical_fail=False, skipped=False):
    led = {'run_at': f'{ymd}T08:00:00Z',
           'steps': [
               {'name': 'snapshot', 'ok': True, 'critical': True},
               {'name': 'facts', 'ok': not critical_fail, 'critical': True},
               {'name': 'optional_view', 'ok': True, 'critical': False,
                'skipped': skipped, 'skip_reason': 'fixture_skip' if skipped else None}],
           'success_count': 2 if not critical_fail else 1,
           'allow_formal_report': not critical_fail,
           'allow_state_writeback': not critical_fail,
           'snapshot_id': f'research_snapshot_{ymd}', 'gate_a': 'PASS'}
    with open(os.path.join(logs, f'pipeline_run_{ymd}.json'), 'w', encoding='utf-8') as f:
        json.dump(led, f, ensure_ascii=False)


def make_health_fixture(snap_days=None, ledger_days=None, with_collectors=False,
                        anchor_facts=None):
    """健康面 fixture: (data_root, logs_dir)。snap_days={ymd: sources_status};
    anchor_facts=锚定快照日事实(新鲜度面);ledger_days={ymd: kwargs}。"""
    root = tempfile.mkdtemp(prefix='p1wpg_h_')
    daily = os.path.join(root, 'daily')
    logs = os.path.join(root, 'logs')
    os.makedirs(daily)
    os.makedirs(logs)
    for ymd, st in (snap_days or {}).items():
        _write_snapshot(daily, ymd, sources_status=st,
                        facts=anchor_facts if ymd == YMD else None)
    for ymd, kw in (ledger_days or {}).items():
        _write_ledger(logs, ymd, **kw)
    if with_collectors:
        for ch in ('global', 'china', 'jp', 'ea', 'macro', 'rate_economy', 'japan'):
            with open(os.path.join(daily, f'{ch}_{YMD}.json'), 'w', encoding='utf-8') as f:
                json.dump({'data': {'poison': POISON}}, f)
    return root, logs


def make_bridge_fixture(fx, eq, fx_id='USDJPY', eq_id='NIKKEI225'):
    """衔接面 fixture: (data_root, research_dir);快照含规则对序列(+诱饵档)。"""
    root = tempfile.mkdtemp(prefix='p1wpg_b_')
    daily = os.path.join(root, 'daily')
    os.makedirs(daily)
    _write_snapshot(daily, YMD, series_store=_store(fx, eq, fx_id, eq_id),
                    sources_status={'global': 'EXACT', 'jp': 'EXACT'})
    rdir = os.path.join(root, 'research')
    os.makedirs(rdir)
    with open(os.path.join(rdir, 'RT-DECOY-0001.json'), 'w', encoding='utf-8') as f:
        f.write('{"task_id": "RT-DECOY-0001", "status": "concluded"}')
    return root, rdir


def make_history_fixture(with_scorecards=('CN', 'JP')):
    """回溯面 fixture: (data_root, research_dir)。快照含三经济体对序列(USDCNY×
    SHCOMP/DAX×EURUSD 短序列)+RT- 档三件(常规/版本/corrupt)。"""
    root = tempfile.mkdtemp(prefix='p1wpg_v_')
    daily = os.path.join(root, 'daily')
    os.makedirs(daily)
    _write_snapshot(
        daily, YMD,
        sources_status={'global': 'EXACT', 'china': 'EXACT', 'jp': 'EXACT', 'ea': 'EXACT'},
        series_store={
            'USDJPY': {'dates': ['2098-12-30', '2098-12-31'], 'values': [150.0, 151.0]},
            'NIKKEI225': {'dates': ['2098-12-30', '2098-12-31'], 'values': [39000.0, 39100.0]},
            'USDCNY': {'dates': ['2098-12-30', '2098-12-31'], 'values': [7.10, 7.11]},
            'SHCOMP': {'dates': ['2098-12-30', '2098-12-31'], 'values': [3400.0, 3401.0]},
            'DAX': {'dates': ['2098-12-31'], 'values': [20000.0]},
            'EURUSD': {'dates': ['2098-12-31'], 'values': [1.09]},
        })
    for econ in (with_scorecards or ()):
        # 档名=上游大写约定(economy 实参原样): data_assembler L288-L289
        # +test_p1_wp_f L172-L173 契约(R062 CI-红-F1 教训承接)
        with open(os.path.join(daily, f'economy_scorecard_{econ}_{YMD}.json'),
                  'w', encoding='utf-8') as f:
            json.dump({'date': YMD, 'growth_total': None, 'inflation_total': None,
                       'regime': '数据不足不可判', 'regime_status': 'data_insufficient',
                       'economy': econ}, f, ensure_ascii=False)
    rdir = os.path.join(root, 'research')
    os.makedirs(rdir)
    with open(os.path.join(rdir, 'RT-2098TEST~20981231-RD-DIV-JP-001-abcd0001.json'),
              'w', encoding='utf-8') as f:
        json.dump({'task_id': 'RT-2098TEST~20981231-RD-DIV-JP-001-abcd0001',
                   'economy': 'JP', 'status': 'active',
                   'created_at': '2098-12-31T09:00:00+00:00'}, f, ensure_ascii=False)
    with open(os.path.join(rdir, 'RT-2098TEST~20981231-RD-DIV-JP-001-abcd0001__v2.json'),
              'w', encoding='utf-8') as f:
        json.dump({'task_id': 'RT-2098TEST~20981231-RD-DIV-JP-001-abcd0001',
                   'economy': 'JP', 'status': 'pending',
                   'created_at': '2098-12-31T10:00:00+00:00'}, f, ensure_ascii=False)
    with open(os.path.join(rdir, 'RT-CORRUPT-0002.json'), 'w', encoding='utf-8') as f:
        f.write('{"task_id": broken')       # 损坏档(如实 corrupt 行,禁静默跳过)
    return root, rdir


# ══ 要点⑤ 实现参数登记定值(先登记后运行,禁回改) ═══════════════════════

class TestRegisteredParamsFrozen(unittest.TestCase):

    def test_health_and_history_windows(self):
        """DP-G1=② 14 日: 两模块回溯窗常量=登记字面量;窗=含端点 14 自然日。"""
        self.assertEqual(rhm.HEALTH_LOOKBACK_DAYS, 14)
        self.assertEqual(mhv.HISTORY_LOOKBACK_DAYS, 14)
        days = rhm.window_days(YMD)
        self.assertEqual(len(days), 14)
        self.assertEqual(days[0], '20981219')    # 手算: 2099-01-01−13=2098-12-19
        self.assertEqual(days[-1], YMD)
        self.assertEqual(mhv.default_window(YMD), ('2098-12-19', '2099-01-01'))

    def test_rules_constants_and_table(self):
        """阈值登记结构=REPORT §零.5(2) 登记字面量;规则族恰三行 CN/JP/EA。"""
        self.assertEqual(ear.ROLLING_WINDOW, 60)
        self.assertEqual(ear.CORR_THRESHOLD, 0.30)
        self.assertEqual(ear.FX_PCT_THRESHOLD, 2.0)
        self.assertEqual(ear.EQ_PCT_THRESHOLD, 2.0)
        self.assertTrue(ear.THRESHOLDS_INCLUSIVE)
        self.assertEqual({e: (r['rule_id'], r['fx_metric'], r['eq_metric'],
                              r['expected_corr_sign'])
                          for e, r in ear.RULES.items()},
                         {'CN': ('RD-DIV-CN-001', 'USDCNY', 'SHCOMP', -1),
                          'JP': ('RD-DIV-JP-001', 'USDJPY', 'NIKKEI225', 1),
                          'EA': ('RD-DIV-EA-001', 'EURUSD', 'DAX', -1)})
        self.assertNotIn('US', ear.RULES)        # US 对=封版 RD-DIV-001 划界
        self.assertIn('RD-DIV-001@anomaly_detector.py', ear.US_PAIR_OWNER)

    def test_echo_params_matches_registration(self):
        """echo_params=常量 echo(证明未事后调参);JP 例逐字段对登记值。"""
        self.assertEqual(ear.echo_params(ear.RULES['JP']),
                         {'rule_id': 'RD-DIV-JP-001', 'economy': 'JP',
                          'rolling_window': 60, 'expected_corr_sign': 1,
                          'corr_threshold': 0.3, 'fx_pct_threshold': 2.0,
                          'eq_pct_threshold': 2.0, 'thresholds_inclusive': True,
                          'stats_rounding': {'rho': 4, 'chg_fx_pct': 4,
                                             'chg_eq_pct': 4}})

    def test_monitor_disclaimer_registered_literal(self):
        """MONITOR_DISCLAIMER=登记文案逐字(禁投资建议语)。"""
        self.assertEqual(ear.MONITOR_DISCLAIMER, DISCLAIMER_LITERAL)


# ══ 要点① 零直读采集档(毒丸负向+三面等值+静态零网络) ═══════════════════

class TestAcceptance1ZeroDirectRead(unittest.TestCase):

    def test_health_view_collector_presence_changes_nothing(self):
        """健康面: 采集档在场/缺席两变体→视图逐字节等值(剔墙钟 generated_at)。"""
        snap = {YMD: {'global': 'EXACT', 'china': 'EXACT', 'japan': 'MISSING',
                      'jp': 'MISSING', 'ea': 'EXACT', 'macro': 'EXACT',
                      'rate_economy': 'DEGRADED'}}
        root_a, logs_a = make_health_fixture(snap_days=snap, with_collectors=True)
        root_b, logs_b = make_health_fixture(snap_days=snap, with_collectors=False)
        try:
            va = rhm.build_health_view(YMD, data_dir=root_a, logs_dir=logs_a,
                                       registry_metrics=SYNTH_REGISTRY)
            vb = rhm.build_health_view(YMD, data_dir=root_b, logs_dir=logs_b,
                                       registry_metrics=SYNTH_REGISTRY)
            va.pop('generated_at'), vb.pop('generated_at')
            self.assertEqual(json.dumps(va, sort_keys=True, ensure_ascii=False),
                             json.dumps(vb, sort_keys=True, ensure_ascii=False))
            self.assertNotIn(POISON, json.dumps(va, ensure_ascii=False))
            self.assertNotIn(POISON, rhm.render_health_markdown(vb))
        finally:
            _rmtree(root_a), _rmtree(root_b)

    def test_bridge_output_collector_poison_never_leaks(self):
        """衔接面: 毒丸采集档在场→任务档与 stdout 摘要零毒丸泄漏。"""
        fx, eq = _pair_series(150.0, -2.0, 200.0, 1.0)   # JP: rho=−1(手算)
        root, rdir = make_bridge_fixture(fx, eq)
        try:
            daily = os.path.join(root, 'daily')
            for ch in ('global', 'jp'):
                with open(os.path.join(daily, f'{ch}_{YMD}.json'), 'w',
                          encoding='utf-8') as f:
                    json.dump({'data': {'poison': POISON}}, f)
            summary, results = mtb.run_bridge(YMD, LAST, LAST, data_dir=root,
                                              out_dir=rdir)
            self.assertTrue(results['JP']['triggered'])
            self.assertNotIn(POISON, json.dumps(summary, ensure_ascii=False))
            for name in os.listdir(rdir):
                with open(os.path.join(rdir, name), 'r', encoding='utf-8') as f:
                    self.assertNotIn(POISON, f.read())
        finally:
            _rmtree(root)

    def test_history_view_collector_presence_changes_nothing(self):
        """回溯面: 采集档在场/缺席两变体→视图逐字节等值+毒丸零出现。"""
        root_a, rdir_a = make_history_fixture()
        root_b, rdir_b = make_history_fixture()
        try:
            daily = os.path.join(root_a, 'daily')
            for ch in ('global', 'china', 'jp', 'ea'):
                with open(os.path.join(daily, f'{ch}_{YMD}.json'), 'w',
                          encoding='utf-8') as f:
                    json.dump({'data': {'poison': POISON}}, f)
            va = mhv.build_history_view(YMD, LAST, LAST, data_dir=root_a,
                                        research_dir=rdir_a,
                                        registry_metrics=SYNTH_REGISTRY)
            vb = mhv.build_history_view(YMD, LAST, LAST, data_dir=root_b,
                                        research_dir=rdir_b,
                                        registry_metrics=SYNTH_REGISTRY)
            va.pop('generated_at'), vb.pop('generated_at')
            self.assertEqual(json.dumps(va, sort_keys=True, ensure_ascii=False),
                             json.dumps(vb, sort_keys=True, ensure_ascii=False))
            md = mhv.render_history_markdown(vb)
            self.assertNotIn(POISON, json.dumps(vb, ensure_ascii=False))
            self.assertNotIn(POISON, md)
        finally:
            _rmtree(root_a), _rmtree(root_b)

    def test_four_modules_static_offline(self):
        """静态面: 四被测模块源码零网络/进程/凭证 import(AC 面⑤⑥⑦)。"""
        for name in ('routine_health_monitor', 'economy_anomaly_rules',
                     'monitor_task_bridge', 'monitor_history_view'):
            with open(os.path.join(ROOT, 'scripts', f'{name}.py'),
                      'r', encoding='utf-8') as f:
                src = f.read()
            for banned in ('import requests', 'import urllib', 'import socket',
                           'import http', 'import subprocess', 'import smtplib',
                           'import plistlib', 'os.system', 'import websocket',
                           'import GLM', 'zhipuai'):
                self.assertNotIn(banned, src,
                                 f'{name}.py 含禁用面: {banned}')


# ══ 要点② 断点/缺席如实列示(禁0填充禁静默;语义与 Gate A 一致) ═══════════

class TestAcceptance2HonestAbsence(unittest.TestCase):

    def test_missing_streak_and_gate_semantics(self):
        """连续 MISSING streak: japan 两日连续=2 后遇 EXACT 断开;DEGRADED
        消费不改判(current_status 原样回显,非 MISSING 不计数)。"""
        snap = {'20981230': {'japan': 'EXACT', 'global': 'EXACT', 'jp': 'EXACT'},
                '20981231': {'japan': 'MISSING', 'global': 'DEGRADED', 'jp': 'MISSING'},
                YMD: {'japan': 'MISSING', 'global': 'DEGRADED', 'jp': 'MISSING'}}
        root, logs = make_health_fixture(snap_days=snap)
        try:
            view = rhm.build_health_view(YMD, data_dir=root, logs_dir=logs,
                                         registry_metrics=[])
            self.assertEqual(view['snapshots']['anchor_day'], YMD)
            self.assertEqual(view['channels']['japan']['missing_streak_days'], 2)
            self.assertEqual(view['channels']['jp']['missing_streak_days'], 2)
            self.assertEqual(view['channels']['global']['current_status'], 'DEGRADED')
            self.assertEqual(view['channels']['global']['missing_streak_days'], 0)
            md = rhm.render_health_markdown(view)
            self.assertIn('DEGRADED', md)
            self.assertIn('| japan | MISSING | 2 |', md)
        finally:
            _rmtree(root)

    def test_no_snapshot_day_breaks_streak(self):
        """无快照日=断链: 锚日 MISSING+隔一日旧快照 MISSING→streak 恒=1
        (计数如实断开,不跨无快照日脑补累加)。"""
        snap = {'20981230': {'japan': 'MISSING', 'global': 'EXACT'},
                YMD: {'japan': 'MISSING', 'global': 'EXACT'}}   # 20981231 无快照
        root, logs = make_health_fixture(snap_days=snap)
        try:
            view = rhm.build_health_view(YMD, data_dir=root, logs_dir=logs,
                                         registry_metrics=[])
            self.assertEqual(view['channels']['japan']['missing_streak_days'], 1)
        finally:
            _rmtree(root)

    def test_freshness_violation_boundary_and_absence(self):
        """新鲜度分层(DP-G3=②): lag=92>60→越限;lag=27→未越限;等号 lag=60
        →未越限(严格大于);事实缺席→缺席行(不填0非违规)。"""
        facts = [{'metric_id': 'CPI', 'observation_date': '2098-10-01'},
                 {'metric_id': 'FED_FUNDS', 'observation_date': '2098-12-05'},
                 {'metric_id': 'CN_LPR_1Y', 'observation_date': '2098-11-02'}]
        root, logs = make_health_fixture(snap_days={YMD: {'global': 'EXACT'}},
                                         anchor_facts=facts)
        reg = SYNTH_REGISTRY + [
            {'metric_id': 'CN_LPR_1Y', 'economy': 'CN', 'frequency': 'monthly',
             'freshness': {'max_calendar_lag_days': 60}}]
        try:
            view = rhm.build_health_view(YMD, data_dir=root, logs_dir=logs,
                                         registry_metrics=reg)
            fr = view['freshness']
            self.assertEqual(fr['anchor_day'], YMD)
            self.assertEqual(fr['checked'], 4)      # CPI/FED_FUNDS/EA_HICP_YOY/CN_LPR_1Y
            viol = {v['metric_id']: v for v in fr['violations']}
            self.assertEqual(list(viol), ['CPI'])   # lag 92>60 手算: 31+30+31
            self.assertEqual(viol['CPI']['lag_days'], 92)
            self.assertFalse(any(v['metric_id'] == 'FED_FUNDS' for v in fr['violations']))
            # CN_LPR_1Y: 2098-11-02→2099-01-01 = 28+31+1 = 60 手算=等号→未越限
            self.assertFalse(any(v['metric_id'] == 'CN_LPR_1Y' for v in fr['violations']))
            absents = {a['metric_id'] for a in fr['absences']}
            self.assertEqual(absents, {'EA_HICP_YOY'})   # 事实缺席行如实
            md = rhm.render_health_markdown(view)
            self.assertIn('快照事实缺席: EA_HICP_YOY', md)
        finally:
            _rmtree(root)

    def test_no_snapshot_whole_freshness_absent(self):
        """窗内零快照: 新鲜度面整体如实缺席(不造检查);通道面空。"""
        root, logs = make_health_fixture(snap_days={})
        try:
            view = rhm.build_health_view(YMD, data_dir=root, logs_dir=logs,
                                         registry_metrics=SYNTH_REGISTRY)
            self.assertIsNone(view['snapshots']['anchor_day'])
            self.assertIn('如实缺席', view['freshness']['note'])
            self.assertEqual(view['freshness']['checked'], 0)
            self.assertEqual(view['channels'], {})
        finally:
            _rmtree(root)

    def test_no_ledger_honest_not_success(self):
        """无台账=如实 present:False(不视为成功);有台账→关键失败/跳步回溯。"""
        snap = {YMD: {'global': 'EXACT'}}
        root_a, logs_a = make_health_fixture(snap_days=snap)               # 零台账
        root_b, logs_b = make_health_fixture(snap_days=snap,
                                             ledger_days={YMD: dict(critical_fail=True,
                                                                    skipped=True)})
        try:
            va = rhm.build_health_view(YMD, data_dir=root_a, logs_dir=logs_a,
                                       registry_metrics=[])
            self.assertEqual(va['pipeline']['n_days_with_ledger'], 0)
            day = next(d for d in va['pipeline']['days'] if d['day'] == YMD)
            self.assertFalse(day['present'])
            self.assertIn('如实缺席', day['note'])
            self.assertEqual(va['pipeline']['aggregate']['days_with_critical_failure'], [])

            vb = rhm.build_health_view(YMD, data_dir=root_b, logs_dir=logs_b,
                                       registry_metrics=[])
            agg = vb['pipeline']['aggregate']
            self.assertEqual(agg['days_with_critical_failure'], [YMD])
            self.assertEqual(agg['days_with_skipped_steps'], [YMD])
            self.assertEqual(agg['days_allowing_state_writeback'], [])   # fail→不放行
            day_b = next(d for d in vb['pipeline']['days'] if d['day'] == YMD)
            self.assertEqual(day_b['critical_failed'], ['facts'])
            self.assertEqual(day_b['skipped'], {'optional_view': 'fixture_skip'})
        finally:
            _rmtree(root_a), _rmtree(root_b)

    def test_corrupt_ledger_honest(self):
        """台账损坏不可解析→如实 corrupt 行(不视为成功不静默)。"""
        root, logs = make_health_fixture(snap_days={YMD: {'global': 'EXACT'}})
        try:
            with open(os.path.join(logs, f'pipeline_run_{YMD}.json'), 'w',
                      encoding='utf-8') as f:
                f.write('{"steps": broken')
            view = rhm.build_health_view(YMD, data_dir=root, logs_dir=logs,
                                         registry_metrics=[])
            day = next(d for d in view['pipeline']['days'] if d['day'] == YMD)
            self.assertFalse(day['present'])
            self.assertIn('损坏', day['note'])
        finally:
            _rmtree(root)


# ══ 范围2 规则引擎(economy_anomaly_rules;期望值手算硬编码) ═══════════════

class TestRulesEngine(unittest.TestCase):

    def test_jp_corr_trigger_handcomputed(self):
        """JP(s=+1): fx 差分=−2×eq 差分→rho=−1.0(手算)→rho×s=−1.0≤−0.30
        →cond_corr 触发;窗口变动 0.0%<2%→cond_move 恒 False(归因唯一)。"""
        fx, eq = _pair_series(150.0, -2.0, 200.0, 1.0)
        det = ear.detect_economy_divergence(ear.RULES['JP'], fx['dates'],
                                            fx['values'], eq['dates'], eq['values'],
                                            LAST, LAST)
        self.assertTrue(det['triggered'])
        row = det['trigger_points'][0]
        self.assertEqual(row['date'], LAST)
        self.assertEqual(row['rho'], -1.0)
        self.assertEqual(row['chg_fx_pct'], 0.0)
        self.assertEqual(row['chg_eq_pct'], 0.0)
        self.assertTrue(row['cond_corr'])
        self.assertFalse(row['cond_move'])
        self.assertEqual(det['summary']['n_scored'], 1)
        self.assertEqual(det['summary']['n_triggered'], 1)

    def test_ea_cn_sign_semantics(self):
        """同负相关序列: EA(s=−1)→rho×s=+1.0>−0.30 不触发;CN 换正共动序列
        (fx 差分=+2×eq 差分→rho=+1.0)→rho×s=−1.0→触发(预期符号语义手算)。"""
        fx, eq = _pair_series(150.0, -2.0, 200.0, 1.0)
        det_ea = ear.detect_economy_divergence(ear.RULES['EA'], fx['dates'],
                                               fx['values'], eq['dates'], eq['values'],
                                               LAST, LAST)
        self.assertFalse(det_ea['triggered'])
        fxp, eqp = _pair_series(7.1, 0.02, 3400.0, 10.0)   # CN 对: USDCNY×SHCOMP
        det_cn = ear.detect_economy_divergence(ear.RULES['CN'], fxp['dates'],
                                               fxp['values'], eqp['dates'], eqp['values'],
                                               LAST, LAST)
        self.assertTrue(det_cn['triggered'])
        self.assertEqual(det_cn['trigger_points'][0]['rho'], 1.0)
        self.assertEqual(det_cn['economy'], 'CN')

    def test_cond_move_inclusive_boundary(self):
        """cond_move 含等号: chg_fx=+2.0 恰达阈 & s×chg_eq=−2.0 恰达反向阈
        (JP)→触发;rho>0→cond_corr=False→纯边界等号触发(手算构造)。"""
        fx, eq = _boundary_series()
        det = ear.detect_economy_divergence(ear.RULES['JP'], fx['dates'], fx['values'],
                                            eq['dates'], eq['values'], LAST, LAST)
        row = det['trigger_points'][0]
        self.assertEqual(row['chg_fx_pct'], 2.0)
        self.assertEqual(row['chg_eq_pct'], -2.0)
        self.assertTrue(row['cond_move'])
        self.assertFalse(row['cond_corr'])
        self.assertTrue(det['triggered'])

    def test_cond_corr_inclusive_boundary(self):
        """cond_corr 含等号(参数注入面): corr_threshold=1.0 且 rho×s=−1.0
        →−1.0≤−1.0 恰等号→触发(证明比较含等号非严格)。"""
        fx, eq = _pair_series(150.0, -2.0, 200.0, 1.0)
        p = ear.echo_params(ear.RULES['JP'])
        p['corr_threshold'] = 1.0
        det = ear.detect_economy_divergence(ear.RULES['JP'], fx['dates'], fx['values'],
                                            eq['dates'], eq['values'], LAST, LAST,
                                            params=p)
        row = det['trigger_points'][0]
        self.assertEqual(row['rho'] * 1, -1.0)
        self.assertTrue(row['cond_corr'])
        self.assertTrue(det['triggered'])

    def test_window_outside_honest_no_score(self):
        """窗口在序列之外→零可评分观测→summary.reason 如实(不造点)。"""
        fx, eq = _pair_series(150.0, -2.0, 200.0, 1.0)
        det = ear.detect_economy_divergence(ear.RULES['JP'], fx['dates'], fx['values'],
                                            eq['dates'], eq['values'],
                                            '2097-01-01', '2097-01-31')
        self.assertFalse(det['triggered'])
        self.assertEqual(det['summary']['n_scored'], 0)
        self.assertIn('如实缺席', det['summary']['reason'])

    def test_detect_all_absent_series_honest(self):
        """规则族全量: 任一成员序列缺席→该经济体 absent_reason 行(不造序列
        不跳过);在场经济体照常检测。"""
        fx, eq = _pair_series(150.0, -2.0, 200.0, 1.0)
        dets = ear.detect_all_from_series_store(_store(fx, eq), LAST, LAST)
        self.assertEqual(set(dets), {'CN', 'JP', 'EA'})
        self.assertTrue(dets['JP']['triggered'])
        self.assertFalse(dets['CN']['triggered'])
        self.assertIn('SHCOMP', dets['CN']['absent_reason'])
        self.assertIn('如实缺席', dets['CN']['absent_reason'])
        self.assertFalse(dets['EA']['triggered'])
        self.assertIn('EURUSD', dets['EA']['absent_reason'])

    def test_preheat_outside_window_counts(self):
        """滚动统计在全序列共同观测上计算(窗口前观测自然预热): 窗口=仅末日,
        前置 60 观测全部作预热→末日恰可评分(与判定式结构锚一致)。"""
        fx, eq = _pair_series(150.0, -2.0, 200.0, 1.0)
        det = ear.detect_economy_divergence(ear.RULES['JP'], fx['dates'], fx['values'],
                                            eq['dates'], eq['values'], LAST, LAST)
        self.assertEqual(det['alignment']['n_common'], 1)          # 窗内共同观测
        self.assertEqual(det['alignment']['n_common_total'], 61)   # 全序列共同观测
        self.assertEqual(det['window']['window_first'], LAST)


# ══ 要点③ 衔接面 append-only+既有 schema+状态保护 ═══════════════════════

class TestAcceptance3BridgeAppendOnly(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.fx, cls.eq = _pair_series(150.0, -2.0, 200.0, 1.0)   # JP 触发(手算)
        cls.root, cls.rdir = make_bridge_fixture(cls.fx, cls.eq)
        cls.summary, cls.results = mtb.run_bridge(YMD, LAST, LAST, data_dir=cls.root,
                                                  out_dir=cls.rdir)
        cls.task_path = cls.results['JP']['task_path']

    @classmethod
    def tearDownClass(cls):
        _rmtree(cls.root)

    def test_schema_min_fields_all_present(self):
        """schema=SCHEMA_MIN_FIELDS 十字段可增不可减(上游 L36-L38 逐项在场)。"""
        with open(self.task_path, 'r', encoding='utf-8') as f:
            task = json.load(f)
        self.assertEqual([k for k in rtm.SCHEMA_MIN_FIELDS if k not in task], [])
        self.assertEqual(len(task['falsifiable_conditions']), 3)
        for cond in task['falsifiable_conditions']:
            self.assertTrue(cond.strip())

    def test_task_economy_and_lifecycle(self):
        """economy 条件写: JP 对两成员 registry economy=JP→顶层键 'JP';
        状态=pending→active(证据装配后,上游 run_e2e 同构)。"""
        with open(self.task_path, 'r', encoding='utf-8') as f:
            task = json.load(f)
        self.assertEqual(task['economy'], 'JP')
        self.assertEqual(task['status'], 'active')
        self.assertEqual([h['to'] for h in task['history']], ['pending', 'active'])
        self.assertEqual(task['indicators'], ['USDJPY', 'NIKKEI225'])
        self.assertTrue(task['task_id'].startswith(
            f'RT-{LAST}~{LAST}-RD-DIV-JP-001-'))
        self.assertEqual(task['evidence']['series_window']['common_dates'], [LAST])
        self.assertEqual(len(task['evidence']['series_window']['NIKKEI225']), 1)
        self.assertEqual(task['window']['source_date'], YMD)

    def test_task_id_deterministic_across_builds(self):
        """确定性 task_id: 同窗口/规则/指标/参数→同 id(两次构造相等)。"""
        det = ear.detect_economy_divergence(ear.RULES['JP'], self.fx['dates'],
                                            self.fx['values'], self.eq['dates'],
                                            self.eq['values'], LAST, LAST)
        t1 = mtb.build_monitor_task('JP', det, self.fx, self.eq, {})
        t2 = mtb.build_monitor_task('JP', det, self.fx, self.eq, {})
        self.assertEqual(t1['task_id'], t2['task_id'])

    def test_idempotent_replay_zero_rewrite(self):
        """同 task_id 重放=幂等跳过: 第二次 save_status='skipped-idempotent',
        零新档写入,既有档字节不动(含诱饵档)。"""
        before = {n: _sha256(os.path.join(self.rdir, n))
                  for n in sorted(os.listdir(self.rdir))}
        summary2, results2 = mtb.run_bridge(YMD, LAST, LAST, data_dir=self.root,
                                            out_dir=self.rdir)
        self.assertEqual(results2['JP']['save_status'], 'skipped-idempotent')
        self.assertEqual(summary2['n_tasks_written'], 0)
        after = {n: _sha256(os.path.join(self.rdir, n))
                 for n in sorted(os.listdir(self.rdir))}
        self.assertEqual(before, after)
        self.assertIn('RT-DECOY-0001.json', before)   # 诱饵档在场且未动
        n_rt = sum(1 for n in before if n.startswith('RT-') and n != 'RT-DECOY-0001.json')
        self.assertEqual(n_rt, 1)                      # 恰一桥接档

    def test_new_version_on_different_fingerprint(self):
        """同 task_id 异指纹=追加 __v{N} 新版本档,原档字节不动(append-only
        既有机制;task_id 确定性含 params→异指纹经 frozen_params 变体构造)。"""
        import copy
        with open(self.task_path, 'r', encoding='utf-8') as f:
            task = json.load(f)
        task_v2 = copy.deepcopy(task)
        task_v2['detection']['frozen_params']['corr_threshold'] = 0.25   # 异指纹
        with open(self.task_path, 'rb') as f:
            h0 = hashlib.sha256(f.read()).hexdigest()
        status, path = rtm.save_task(task_v2, self.rdir)
        self.assertEqual(status, 'written-new-version')
        self.assertTrue(os.path.basename(path).endswith('__v2.json'))
        with open(self.task_path, 'rb') as f:
            self.assertEqual(hashlib.sha256(f.read()).hexdigest(), h0)  # 原档不动

    def test_not_triggered_zero_tasks(self):
        """不触发=如实零任务(合法结果情形(c));CN/EA 序列缺席→absent_reason 行。"""
        root, rdir = make_bridge_fixture(self.fx, self.eq)
        try:
            store_path = os.path.join(root, 'daily', f'research_snapshot_{YMD}.json')
            with open(store_path, 'r', encoding='utf-8') as f:
                snap = json.load(f)
            # 换成不触发序列(EA 镜像: 同负相关对 s=+1 不触发)
            fx2, eq2 = _pair_series(1.09, -0.002, 20000.0, 100.0)
            snap['series_store'] = _store(fx2, eq2, 'EURUSD', 'DAX')
            with open(store_path, 'w', encoding='utf-8') as f:
                json.dump(snap, f, ensure_ascii=False)
            summary, results = mtb.run_bridge(YMD, LAST, LAST, data_dir=root,
                                              out_dir=rdir)
            self.assertEqual(summary['n_triggered'], 0)
            self.assertEqual(summary['n_tasks_written'], 0)
            self.assertEqual(summary['tasks'], [])
            self.assertFalse(results['JP']['triggered'])   # 序列改 EA 对→JP 缺席
            self.assertIn('USDJPY', results['JP']['absent_reason'])
            new = [n for n in os.listdir(rdir) if n != 'RT-DECOY-0001.json']
            self.assertEqual(new, [])                      # 零新档
            self.assertEqual(summary['disclaimer'], DISCLAIMER_LITERAL)
            self.assertIn('零 update_thesis_status', summary['state_protection'])
        finally:
            _rmtree(root)

    def test_snapshot_absent_zero_detection(self):
        """快照缺席=如实零检测零任务(不代行快照构建)。"""
        root = tempfile.mkdtemp(prefix='p1wpg_s_')
        rdir = os.path.join(root, 'research')
        os.makedirs(os.path.join(root, 'daily'))
        os.makedirs(rdir)
        try:
            summary, results = mtb.run_bridge(YMD, LAST, LAST, data_dir=root,
                                              out_dir=rdir)
            self.assertFalse(summary['snapshot_available'])
            self.assertIn('research_snapshot', summary['snapshot_unavailable_reason'])
            self.assertEqual(summary['n_triggered'], 0)
            self.assertEqual(summary['n_tasks_written'], 0)
            self.assertEqual(os.listdir(rdir), [])
        finally:
            _rmtree(root)

    def test_cli_smoke_exit_zero(self):
        """CLI 冒烟(离线合成 fixture): main 返回 0(不触发也是合法结果)。"""
        root, rdir = make_bridge_fixture(self.fx, self.eq)
        try:
            rc = mtb.main(['--ymd', YMD, '--start', LAST, '--end', LAST,
                           '--data-dir', root, '--out-dir', rdir])
            self.assertEqual(rc, 0)
            rc2 = mtb.main(['--ymd', '20990102', '--start', LAST, '--end', LAST,
                            '--data-dir', root, '--out-dir', rdir])   # 快照缺席
            self.assertEqual(rc2, 0)
        finally:
            _rmtree(root)

    def test_state_protection_static(self):
        """状态保护静态面: 衔接模块零 update_thesis_status 调用。"""
        with open(os.path.join(ROOT, 'scripts', 'monitor_task_bridge.py'),
                  'r', encoding='utf-8') as f:
            src = f.read()
        self.assertNotIn('update_thesis_status(', src)
        self.assertIn('save_task', src)          # 唯一写面=append-only 落档


# ══ 范围4 回溯查询面(economy 过滤消费+RT- 只读列示+#19 前件消费) ═════════

class TestHistoryView(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.root, cls.rdir = make_history_fixture()
        cls.view = mhv.build_history_view(
            YMD, '2098-12-30', '2098-12-31', data_dir=cls.root,
            research_dir=cls.rdir, registry_metrics=SYNTH_REGISTRY)

    @classmethod
    def tearDownClass(cls):
        _rmtree(cls.root)

    def test_retrospective_windows_economy_filter(self):
        """逐经济体窗口=上游 query_window 直用: JP 命中 n_window=2;
        CN 请求对 USDJPY 过滤不命中→如实空窗(metric_economy='JP')。"""
        w = self.view['windows']
        self.assertEqual(w['JP']['USDJPY']['coverage']['n_window'], 2)
        self.assertEqual(w['JP']['USDJPY']['values'], [150.0, 151.0])   # 手算
        self.assertEqual(w['JP']['USDJPY']['coverage']['window_first'], '2098-12-30')
        self.assertEqual(w['JP']['USDJPY']['coverage']['window_last'], '2098-12-31')
        miss = w['CN']['USDJPY']
        self.assertEqual(miss['dates'], [])
        self.assertFalse(miss['coverage']['economy_filter']['matched'])
        self.assertEqual(miss['coverage']['economy_filter']['metric_economy'], 'JP')
        # CN 自有对命中
        self.assertEqual(w['CN']['USDCNY']['coverage']['n_window'], 2)

    def test_tasks_readonly_listing_with_versions(self):
        """RT- 列示=只读扫描: 常规+__v2+corrupt 三件全列;调用后字节不动。"""
        mt = self.view['monitor_tasks']
        self.assertEqual(mt['n_tasks'], 3)
        by_file = {t['file']: t for t in mt['tasks']}
        v1 = by_file['RT-2098TEST~20981231-RD-DIV-JP-001-abcd0001.json']
        v2 = by_file['RT-2098TEST~20981231-RD-DIV-JP-001-abcd0001__v2.json']
        self.assertEqual(v1['status'], 'active')
        self.assertEqual(v1['economy'], 'JP')
        self.assertEqual(v2['status'], 'pending')
        self.assertTrue(by_file['RT-CORRUPT-0002.json']['corrupt'])
        self.assertEqual(mt['n_by_status'], {'active': 1, 'pending': 1, '(corrupt)': 1})
        before = {n: _sha256(os.path.join(self.rdir, n))
                  for n in sorted(os.listdir(self.rdir))}
        mhv.list_monitor_tasks(self.rdir)      # 再扫描=幂等只读
        after = {n: _sha256(os.path.join(self.rdir, n))
                 for n in sorted(os.listdir(self.rdir))}
        self.assertEqual(before, after)

    def test_comparison_status_consumes_wp_f(self):
        """#19 前件消费: ecv.economy_row 复用——CN/JP 评分卡在场(数据不足),
        US/EA 缺席→未生成(禁跳行)。"""
        rows = {c['economy']: c for c in self.view['comparison_status']}
        self.assertEqual(set(rows), {'US', 'CN', 'JP', 'EA'})
        self.assertTrue(rows['CN']['scorecard_present'])
        self.assertTrue(rows['JP']['scorecard_present'])
        self.assertIn('数据不足', rows['CN']['status_cell'])
        self.assertFalse(rows['US']['scorecard_present'])
        self.assertFalse(rows['EA']['scorecard_present'])
        self.assertIn('未生成', rows['EA']['status_cell'])

    def test_default_window_and_render(self):
        """缺省窗=DP-G1 14 日([ymd−13, ymd]);渲染含三节+DISCLAIMER 逐字。"""
        view = mhv.build_history_view(YMD, data_dir=self.root, research_dir=self.rdir,
                                      registry_metrics=SYNTH_REGISTRY)
        self.assertEqual(view['window']['start'], '2098-12-19')
        self.assertEqual(view['window']['end'], '2099-01-01')
        md = mhv.render_history_markdown(view)
        self.assertIn(DISCLAIMER_LITERAL, md)
        self.assertIn('逐经济体窗口回溯', md)
        self.assertIn('RT- 研究任务列示', md)
        self.assertIn('ecv.economy_row', md)
        self.assertEqual(view['disclaimer'], DISCLAIMER_LITERAL)

    def test_absent_research_dir_and_metrics(self):
        """研究目录缺席→如实零任务 note;指标不在 registry→economy None→
        过滤不命中如实空窗(不删行)。"""
        root2 = tempfile.mkdtemp(prefix='p1wpg_v2_')
        rdir2 = os.path.join(root2, 'research')   # 不创建=目录缺席
        daily = os.path.join(root2, 'daily')
        os.makedirs(daily)
        _write_snapshot(daily, YMD,
                        series_store={'SNP': {'dates': ['2098-12-31'],
                                              'values': [6000.0]}})
        try:
            view = mhv.build_history_view(YMD, LAST, LAST, data_dir=root2,
                                          research_dir=rdir2,
                                          registry_metrics=SYNTH_REGISTRY)
            self.assertIn('如实零任务', view['monitor_tasks']['note'])
            self.assertEqual(view['monitor_tasks']['n_tasks'], 0)
            row = view['windows']['US']['SNP']
            self.assertIsNone(row['metric_economy'])
            self.assertFalse(row['coverage']['economy_filter']['matched'])
        finally:
            _rmtree(root2)

    def test_cli_smoke_exit_zero(self):
        """CLI 冒烟: main 返回 0+输出档落 tmp(经济体子集面)。"""
        out = os.path.join(self.root, 'monitor_history_TEST.md')
        rc = mhv.main(['--ymd', YMD, '--start', '2098-12-30', '--end', '2098-12-31',
                       '--economies', 'JP,EA', '--data-dir', self.root,
                       '--research-dir', self.rdir, '--out', out])
        self.assertEqual(rc, 0)
        with open(out, 'r', encoding='utf-8') as f:
            md = f.read()
        self.assertIn('### JP', md)
        self.assertIn('### EA', md)
        self.assertNotIn('### CN', md)      # 子集过滤生效


# ══ 要点⑥⑦ LIVE/通知/GLM 面零实现(确认型 DP 未自决) ═══════════════════

class TestStaticPendingFaces(unittest.TestCase):

    def test_no_live_or_notification_faces(self):
        """⑥⑦: 四模块零 launchd/常驻装载/通知渠道/GLM 客户端调用面。"""
        for name in ('routine_health_monitor', 'economy_anomaly_rules',
                     'monitor_task_bridge', 'monitor_history_view'):
            with open(os.path.join(ROOT, 'scripts', f'{name}.py'),
                      'r', encoding='utf-8') as f:
                src = f.read()
            for banned in ('launchd', 'LaunchAgents', 'sched.add', 'cron',
                           'sendmail', 'webhook', 'push_notify', 'zhipuai',
                           'glm.chat', 'antglm'):
                self.assertNotIn(banned, src,
                                 f'{name}.py 含 LIVE/通知/GLM 面: {banned}')

    def test_health_cli_writes_only_view_doc(self):
        """健康面 CLI 唯一写面=视图输出档(指定 tmp 路径);daily/ 全目录只读。"""
        snap = {YMD: {'global': 'EXACT', 'japan': 'MISSING'}}
        root, logs = make_health_fixture(snap_days=snap, with_collectors=True)
        out = os.path.join(root, 'health_TEST.md')
        try:
            daily = os.path.join(root, 'daily')
            before = {n: _sha256(os.path.join(daily, n))
                      for n in sorted(os.listdir(daily))}
            rc = rhm.main(['--ymd', YMD, '--data-dir', root, '--logs-dir', logs,
                           '--out', out])
            self.assertEqual(rc, 0)
            after = {n: _sha256(os.path.join(daily, n))
                     for n in sorted(os.listdir(daily))}
            self.assertEqual(before, after)
            with open(out, 'r', encoding='utf-8') as f:
                md = f.read()
            self.assertIn(DISCLAIMER_LITERAL, md)
            self.assertIn('| japan | MISSING | 1 |', md)
        finally:
            _rmtree(root)


if __name__ == '__main__':
    unittest.main(verbosity=2)
