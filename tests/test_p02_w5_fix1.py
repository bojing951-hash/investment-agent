# -*- coding: utf-8 -*-
"""IA-P0-2-W5-FIX1 专项测试(七项确定性缺陷修复的逐项验证+退化敏感性)。

任务: IA-P0-2-W5-FIX1-DEV-v1.0 §十一 | 基线: W5失败Commit 78f4c9a
全部用例真实调用被测脚本 real_data_acceptance(FIX1版)的 sanitize/_
safe_error/_evidence/fetch_*/check_shcomp/recompute_check/evaluate_overall/
run_external_checks/path_conflict/main()——不复制被测算法、不预拼JSON。
密钥纪律: **一律使用虚构密钥**(FAKEKEY…/BOUNDARYKEY…/RAWKEY…),绝不把
真实密钥写入错误日志作为测试;外部API一律Mock,零真实网络。

A组(安全,FIX1-01/05): FRED 401/403/超时失败路径的密钥脱敏与诊断保留;
运行时已知密钥明文(含URL编码形式)脱敏;截断边界不暴露密钥片段;
递归清扫;main输出路径安全(相同/内部/祖先/符号链接/..,零写入零网络)。
B组(金融,FIX1-02/03): 固定反例(基准100/期末110/独立10%): 期末价111/
基准值999/缺基准日期/缺基准值/仅百分比正确→全部FAIL;完整三期复算PASS;
部分复核=INSUFFICIENT_HISTORY不冒充;整体完整性门槛(三期完整≥1等)。
C组(价格语义,FIX1-04): SHCOMP历史日盘中10:30/00:00/无时间→NOT_VERIFIED
(取消历史豁免);已证实收盘口径+吻合→PASS(比较能力保留);错日;超差FAIL。
D组(来源,FIX1-06/07): 八项稳定check_id唯一齐备;ours保留fact.source;
evidence_ids全部可定位(UST共享年度证据/FRED各自/Coinbase各自/无来源为空);
Treasury跨年度两年度请求各自同日匹配;单年失败不抹掉他年数据。
E组(退化敏感性): 对真实源码做七类关键错误逻辑的最小退化替换后importlib
加载,断言退化版与正确版行为分离——恢复任一FIX1缺陷都会使对应断言失败,
证明本套件不是实现自身的复制品。
"""
import contextlib
import copy
import glob
import io
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
sys.path.insert(0, os.path.join(ROOT, 'tests'))

import real_data_acceptance as rda   # 被测的真实验收脚本(FIX1版)
import fixt
import snapshot_builder as sb
from test_p02_w5 import (DAY, OBS, load_variant, make_fact, epoch_of,
                         _ext, _rc, _healthy_lists, _extend_global_history)

import requests


def ust_fact(mid, v, od):
    return {'metric_id': mid, 'value': v, 'observation_date': od,
            'unit': 'percent',
            'source': {'collector': 'macro_collector', 'file': f'macro_{DAY}.json'}}


class F1ASecurity(unittest.TestCase):
    """A组: 密钥失败路径脱敏(FIX1-01)+输出路径安全(FIX1-05)。"""

    def setUp(self):
        self._saved = list(rda._KNOWN_SECRETS)

    def tearDown(self):
        rda._KNOWN_SECRETS[:] = self._saved

    def test_a1_fred_401_sanitized_diag_preserved(self):
        # FRED 401(虚构密钥): NOT_VERIFIED+诊断保留,零密钥明文,401仍可确认
        rda._register_secret('FAKEKEY123TEST0000000000000AB')
        err = requests.exceptions.HTTPError(
            '401 Client Error: Unauthorized for url: '
            'https://api.stlouisfed.org/fred/series/observations'
            '?api_key=FAKEKEY123TEST0000000000000AB&file_type=json')
        err.response = mock.Mock(status_code=401)
        with mock.patch.object(rda.requests, 'get', side_effect=err):
            obs, ev, raw = rda.fetch_fred_obs(
                'SP500', 'FAKEKEY123TEST0000000000000AB')
        self.assertEqual(obs, [])
        self.assertIsNone(raw)
        self.assertNotIn('FAKEKEY123TEST0000000000000AB', ev['error'])
        self.assertNotIn('FAKEKEY123TEST0000000000000AB', ev['url'])
        self.assertIn('***REDACTED***', ev['error'])
        self.assertIn('401', ev['error'])            # HTTP状态保留→仍可确认401
        self.assertIn('HTTPError', ev['error'])      # 异常类型保留
        blob = json.dumps(ev, ensure_ascii=False)
        self.assertIsNone(rda.find_secret(blob))
        r = rda.check_spx(make_fact('SPX', 7720.0, OBS, 'index_point'), [],
                          rda.TOLERANCES['fred_spx'])
        self.assertEqual(r['verdict'], 'NOT_VERIFIED')

    def test_a2_403_timeout_generic_sanitized(self):
        for status, msg in ((403, '403 Client Error: Forbidden for url: '
                                  'https://api.stlouisfed.org/x?api_key=K403FAKE&f=j'),
                            (None, 'connect timeout to '
                                   'https://api.stlouisfed.org/x?api_key=KTOFAKE&f=j'),
                            (None, 'weird failure api_key=KGENFAKE tail')):
            if status is not None:
                err = requests.exceptions.HTTPError(msg)
                err.response = mock.Mock(status_code=status)
            else:
                err = TimeoutError(msg)
            with mock.patch.object(rda.requests, 'get', side_effect=err):
                obs, ev, raw = rda.fetch_fred_obs('SP500', 'KFAKE')
            self.assertEqual(obs, [])
            self.assertIsNotNone(ev.get('error'))
            self.assertNotIn('K403FAKE', ev['error'])
            self.assertNotIn('KTOFAKE', ev['error'])
            self.assertNotIn('KGENFAKE', ev['error'])
            if status is not None:
                self.assertIn(str(status), ev['error'])

    def test_a3_known_secret_and_url_encoded_forms(self):
        # 运行时已知密钥明文+URL编码形式(非api_key=模式出现)也脱敏
        rda._register_secret('PLAINSECRET00AA11BB22CC')
        s = 'prefix PLAINSECRET00AA11BB22CC suffix'
        self.assertNotIn('PLAINSECRET00AA11BB22CC', rda.sanitize_text(s))
        enc = ('quoted %s plus %s end' % ('PLAINSECRET00AA11BB22CC',
                                          'PLAINSECRET00AA11BB22CC'))
        # alnum密钥quote后不变;带编码敏感字符的形式由_register_secret补齐
        self.assertNotIn('PLAINSECRET00AA11BB22CC', rda.sanitize_text(enc))
        self.assertIn('***REDACTED***', rda.sanitize_text(s))

    def test_a4_truncation_boundary_no_partial_key(self):
        # 截断边界不得截出密钥片段(尾部与密钥前缀重叠→回退截断点)
        rda._register_secret('BOUNDARYKEY1234567890XYZ')
        s = 'A' * 198 + 'BOUNDARYKEY1234567890XYZTAIL'
        cut = rda._clip_safe(s, 200)
        k = 'BOUNDARYKEY1234567890XYZ'
        for L in range(2, len(k)):
            self.assertFalse(cut.endswith(k[:L]), f'尾部泄漏密钥前缀{L}字符')
        self.assertIsNone(rda.find_secret(cut))
        # _safe_error全链路: 长异常串(密钥非api_key=模式出现)→脱敏+截断后干净
        e = Exception('B' * 190 + 'BOUNDARYKEY1234567890XYZ' + 'C' * 100)
        out = rda._safe_error(e)
        self.assertLessEqual(len(out), 200)
        self.assertNotIn('BOUNDARYKEY', out)

    def test_a5_recursive_sweep_and_find(self):
        rda._register_secret('NESTEDSECRET99AA88BB77')
        obj = {'url': 'https://x/?api_key=NESTEDSECRET99AA88BB77',
               'nested': [{'error': 'boom NESTEDSECRET99AA88BB77',
                           'ok': 'clean'}], 'num': 42, 'none': None}
        swept = rda.sweep_secrets(obj)
        blob = json.dumps(swept, ensure_ascii=False)
        self.assertNotIn('NESTEDSECRET99AA88BB77', blob)
        self.assertIn('***REDACTED***', blob)
        self.assertIsNone(rda.find_secret(blob))
        self.assertEqual(swept['num'], 42)     # 非字符串原样
        # 幂等
        self.assertEqual(rda.sweep_secrets(swept), swept)

    def _run_main(self, td, outdir, extra=('--skip-external',), factory=None):
        fake_now = f'{DAY[:4]}-{DAY[4:6]}-{DAY[6:]}T08:00:00'

        class _DT(datetime):
            @classmethod
            def now(cls, tz=None):
                return cls.fromisoformat(fake_now)
        out = io.StringIO()
        argv = ['rda', '--data-dir', td, '--out-dir', outdir,
                '--data-day', DAY, '--trusted-root', td] + list(extra)
        patches = [mock.patch.object(sys, 'argv', argv),
                   mock.patch.object(rda, 'datetime', _DT),
                   contextlib.redirect_stdout(out)]
        if factory is not None:
            patches.append(mock.patch.object(rda, 'default_fetchers', factory))
        with contextlib.ExitStack() as st:
            for p in patches:
                st.enter_context(p)
            try:
                rda.main()
                rc = 0
            except SystemExit as e:
                rc = e.code
        return rc, out.getvalue()

    def test_a6_path_conflict_unit_rules(self):
        with tempfile.TemporaryDirectory() as td:
            daily = os.path.join(td, 'daily')
            os.makedirs(daily)
            os.symlink(daily, os.path.join(td, 'alias'))
            self.assertIsNotNone(rda.path_conflict(td, td))                     # 相同
            self.assertIsNotNone(rda.path_conflict(td, os.path.join(td, 'a')))  # 输出在输入内
            self.assertIsNotNone(rda.path_conflict(daily, td))                  # 输出为输入祖先
            self.assertIsNotNone(rda.path_conflict(                             # 符号链接真实路径重叠
                daily, os.path.join(td, 'alias', 'sub')))
            self.assertIsNotNone(rda.path_conflict(                             # ..真实路径重叠
                td, os.path.join(td, 'daily', '..', 'out')))
            # 字符串前缀相同但真实路径无关≠冲突(不得仅比较前缀)
            os.makedirs(td + 'unrelated', exist_ok=True)
            self.assertIsNone(rda.path_conflict(td, td + 'unrelated'))
            self.assertIsNone(rda.path_conflict(daily, td + '_out'))

    def test_a7_main_rejects_out_inside_data_no_write_no_net(self):
        # 输出位于输入内部: main明确拒绝+exit2+零写入+零网络+输入不变
        with tempfile.TemporaryDirectory() as td:
            fixt.write_collectors(td, DAY)
            before = {f: open(os.path.join(td, f), 'rb').read()
                      for f in sorted(os.listdir(td))}
            calls = []

            def factory(key):
                calls.append(key)
                raise AssertionError('路径非法时不得触发任何外部请求')
            rc, out = self._run_main(td, os.path.join(td, 'acc'), factory=factory)
            self.assertEqual(rc, 2)
            self.assertIn('输出路径安全检查未通过', out)
            self.assertIn('输出目录位于数据目录内部', out)
            self.assertEqual(calls, [])                       # 零网络
            after = {f: open(os.path.join(td, f), 'rb').read()
                     for f in sorted(os.listdir(td))}
            self.assertEqual(before, after)                   # 输入零修改
            self.assertFalse(os.path.exists(os.path.join(td, 'acc')))

    def test_a8_main_rejects_same_and_ancestor_and_symlink(self):
        with tempfile.TemporaryDirectory() as td:
            fixt.write_collectors(td, DAY)
            # 完全相同
            rc, out = self._run_main(td, td)
            self.assertEqual(rc, 2)
            self.assertIn('完全相同', out)
            # 输出是输入祖先(数据在输出内部)
            sub = os.path.join(td, 'inner')
            os.makedirs(sub)
            fixt.write_collectors(sub, DAY)
            rc, out = self._run_main(sub, td)
            self.assertEqual(rc, 2)
            self.assertIn('祖先', out)
            # 符号链接真实路径重叠
            os.symlink(td, td + '_alias')
            rc, out = self._run_main(td, td + '_alias')
            self.assertEqual(rc, 2)
            self.assertIn('路径安全检查未通过', out)
            # 合法分离目录仍正常运行(对照: exit3离线诊断,报告写在数据目录外)
            with tempfile.TemporaryDirectory() as od:
                rc, out = self._run_main(td, od)
                self.assertEqual(rc, 3)
                self.assertTrue(glob.glob(os.path.join(od, 'real_acceptance_*.json')))


class F1BRecomputeIntegrity(unittest.TestCase):
    """B组: 收益复算价格字段校验(FIX1-02)+完整复算门槛(FIX1-03)。"""

    # 固定反例基底: 序列基准100→期末110,独立周收益10.0%
    SER = {'dates': ['2026-10-16', '2026-10-23'], 'values': [100.0, 110.0]}
    WK_OK = {'basis_date': '2026-10-16', 'basis_value': 100.0, 'pct_change': 10.0}

    def _fact(self, value, week):
        return make_fact('SPX', value, '2026-10-23', 'index_point', derived={
            'end': {'date': '2026-10-23', 'value': value},
            'week': week, 'mtd': {'available': False},
            'ytd': {'available': False}})

    def test_b1_fixed_counterexamples_all_fail(self):
        # 基准100/期末110/独立10%: ①期末价111(pct仍10) → FAIL
        r = rda.recompute_check('SPX', self._fact(111.0, self.WK_OK), self.SER)
        self.assertEqual(r['verdict'], 'FAIL')
        self.assertIn('期末价格不一致', r['note'])
        # ②引擎基准值999(pct仍10) → FAIL
        r = rda.recompute_check('SPX', self._fact(110.0, dict(self.WK_OK, basis_value=999.0)),
                                self.SER)
        self.assertEqual(r['verdict'], 'FAIL')
        self.assertIn('基准价格不一致', r['note'])
        # ③引擎缺基准日期 → FAIL
        r = rda.recompute_check('SPX', self._fact(110.0, dict(self.WK_OK, basis_date=None)),
                                self.SER)
        self.assertEqual(r['verdict'], 'FAIL')
        self.assertIn('缺基准日期', r['note'])
        # ④引擎缺基准值 → FAIL
        r = rda.recompute_check('SPX', self._fact(110.0, dict(self.WK_OK, basis_value=None)),
                                self.SER)
        self.assertEqual(r['verdict'], 'FAIL')
        self.assertIn('缺基准值', r['note'])
        # ⑤pct保持10且价格字段全部一致 → 该期PASS(仅week可算→部分复核,见b3)
        r = rda.recompute_check('SPX', self._fact(110.0, self.WK_OK), self.SER)
        self.assertEqual(r['periods']['week']['status'], 'PASS')
        # 期末观测日期不一致 → FAIL(结束观测日期核对)
        f = self._fact(110.0, self.WK_OK)
        f['observation_date'] = '2026-10-22'
        self.assertEqual(rda.recompute_check('SPX', f, self.SER)['verdict'], 'FAIL')

    def _extended_snapshot(self):
        with tempfile.TemporaryDirectory() as td:
            fixt.write_collectors(td, DAY)
            _extend_global_history(td, DAY, {
                'SPX': {'2025-12-31': 6800.0, '2026-09-30': 7300.0},
                'GOLD': {'2025-12-31': 3300.0, '2026-09-30': 3550.0}})
            snap = sb.build_snapshot(target_ymd=DAY, data_dir=td, out_dir=td,
                                     trusted_root=td, as_of=fixt.as_of_for(DAY))
        facts = {f['metric_id']: f for f in snap['facts']}
        return facts, snap.get('series_store') or {}

    def test_b2_full_three_periods_pass(self):
        # 完整三期: WEEK/MTD/YTD全部独立一致(真实引擎快照,非手拼结果)
        facts, store = self._extended_snapshot()
        for mid in ('SPX', 'GOLD_F'):
            r = rda.recompute_check(mid, facts[mid], store[mid])
            self.assertEqual(r['verdict'], 'PASS', f'{mid}: {r["note"]}')
            self.assertTrue(r['complete_recompute'])
            self.assertEqual(r['verified_periods'], ['week', 'mtd', 'ytd'])
            self.assertEqual(r['periods']['mtd']['independent']['basis_date'],
                             '2026-09-30')
            self.assertEqual(r['periods']['ytd']['independent']['basis_date'],
                             '2025-12-31')

    def test_b3_partial_is_insufficient_not_pass(self):
        # 部分复核: 仅WEEK可核 → INSUFFICIENT_HISTORY+明细,不冒充完整PASS
        snap = fixt.real_snapshot(DAY)
        facts = {f['metric_id']: f for f in snap['facts']}
        store = snap.get('series_store') or {}
        r = rda.recompute_check('SPX', facts['SPX'], store['SPX'])
        self.assertEqual(r['verdict'], 'INSUFFICIENT_HISTORY')
        self.assertFalse(r['complete_recompute'])
        self.assertEqual(r['verified_periods'], ['week'])
        self.assertIn('部分复核', r['note'])
        self.assertIn('不冒充完整PASS', r['note'])
        self.assertEqual(r['periods']['week']['status'], 'PASS')  # 已核部分如实标注

    def test_b4_overall_requires_complete_three_period(self):
        # 两资产仅WEEK(部分复核)→整体不得PASS
        ext, _ = _healthy_lists()
        rc = [_rc('SPX', 'INSUFFICIENT_HISTORY'), _rc('GOLD_F', 'INSUFFICIENT_HISTORY')]
        for row in rc:
            row['complete_recompute'] = False
            row['verified_periods'] = ['week']
        o = rda.evaluate_overall(ext, rc, skip_external=False)
        self.assertEqual((o['overall'], o['exit_code']), ('NOT_VERIFIED', 3))
        self.assertIn('三期完整独立复算', ' '.join(o['reasons']))
        self.assertEqual(o['coverage']['recompute_complete'], 0)
        # 一资产完整三期+其他部分历史不足→状态准确(完整≥1但复算PASS<2→NOT_VERIFIED)
        rc2 = [dict(_rc('SPX', 'PASS'), complete_recompute=True,
                    verified_periods=['week', 'mtd', 'ytd']),
               dict(_rc('GOLD_F', 'INSUFFICIENT_HISTORY'), complete_recompute=False,
                    verified_periods=['week'])]
        o2 = rda.evaluate_overall(ext, rc2, skip_external=False)
        self.assertEqual(o2['overall'], 'NOT_VERIFIED')
        self.assertIn('复算PASS1<2', ' '.join(o2['reasons']))
        # 多资产完整三期→门槛满足→PASS
        rc3 = [dict(_rc(m, 'PASS'), complete_recompute=True,
                    verified_periods=['week', 'mtd', 'ytd'])
               for m in ('SPX', 'GOLD_F', 'SHCOMP', 'HSI')]
        o3 = rda.evaluate_overall(ext, rc3, skip_external=False)
        self.assertEqual((o3['overall'], o3['exit_code']), ('PASS', 0))
        self.assertEqual(o3['coverage']['recompute_complete'], 4)
        # 任一周期确定性数值错误→FAIL(整体优先FAIL)
        rc4 = list(rc3)
        rc4[0] = _rc('SPX', 'FAIL')
        o4 = rda.evaluate_overall(ext, rc4, skip_external=False)
        self.assertEqual((o4['overall'], o4['exit_code']), ('FAIL', 2))

    def test_b5_partial_history_not_overstated(self):
        # 部分历史不得虚报研究充分性: 部分复核行的note/字段不得声称完整
        snap = fixt.real_snapshot(DAY)
        facts = {f['metric_id']: f for f in snap['facts']}
        store = snap.get('series_store') or {}
        r = rda.recompute_check('SHCOMP', facts['SHCOMP'], store['SHCOMP'])
        # fixture SHCOMP: week+mtd已核,ytd历史不足 → 仍非完整
        self.assertEqual(r['verdict'], 'INSUFFICIENT_HISTORY')
        self.assertEqual(r['verified_periods'], ['week', 'mtd'])
        self.assertNotIn('完整复算', r['note'])


class F1CShcompCloseBasis(unittest.TestCase):
    """C组: SHCOMP收盘口径可证性对任意日期一律要求(FIX1-04)。"""

    F = {'metric_id': 'SHCOMP', 'value': 3272.0, 'observation_date': '2026-10-29',
         'unit': 'index_point'}
    SPEC = rda.TOLERANCES['sina_shcomp']

    def _q(self, date, time, close=3272.0):
        return {'close': close, 'date': date, 'time': time}

    def test_c1_historical_intraday_blocked(self):
        # 核心反例: 目标2026-10-29/执行日2026-10-30/历史报价10:30(差在容差内)
        # → NOT_VERIFIED(历史日期不再豁免收盘口径检查)
        r = rda.check_shcomp(self.F, self._q('2026-10-29', '10:30:00'),
                             '20261030', self.SPEC)
        self.assertEqual(r['verdict'], 'NOT_VERIFIED')
        self.assertIn('收盘口径', r['note'])

    def test_c2_historical_zero_time_blocked(self):
        r = rda.check_shcomp(self.F, self._q('2026-10-29', '00:00:00'),
                             '20261030', self.SPEC)
        self.assertEqual(r['verdict'], 'NOT_VERIFIED')

    def test_c3_same_day_no_time_not_verified(self):
        r = rda.check_shcomp(self.F, self._q('2026-10-29', None),
                             '20261029', self.SPEC)
        self.assertEqual(r['verdict'], 'NOT_VERIFIED')

    def test_c4_confirmed_close_still_compared(self):
        # 已证实收盘口径(≥15:30)+价格吻合 → PASS(历史报价比较能力保留)
        r = rda.check_shcomp(self.F, self._q('2026-10-29', '15:30:00'),
                             '20261030', self.SPEC)
        self.assertEqual(r['verdict'], 'PASS')
        r = rda.check_shcomp(self.F, self._q('2026-10-29', '15:31:00'),
                             '20261029', self.SPEC)
        self.assertEqual(r['verdict'], 'PASS')

    def test_c5_date_mismatch_not_verified(self):
        r = rda.check_shcomp(self.F, self._q('2026-10-30', '15:30:00'),
                             '20261030', self.SPEC)
        self.assertEqual(r['verdict'], 'NOT_VERIFIED')
        self.assertIn('日期', r['note'])

    def test_c6_real_close_beyond_tolerance_fails(self):
        r = rda.check_shcomp(self.F, self._q('2026-10-29', '15:30:00', close=3300.0),
                             '20261030', self.SPEC)
        self.assertEqual(r['verdict'], 'FAIL')


def _full_facts():
    snap = fixt.real_snapshot(DAY)
    return {f['metric_id']: f for f in snap['facts']}


def _stub_fetchers(facts, treasury_impl=None):
    def _ev(u):
        return {'source': 'stub', 'url': u, 'fetched_at_utc': '2026-10-24T00:00:00',
                'http_status': 200}

    def treasury(year, want):
        if treasury_impl is not None:
            return treasury_impl(year, want)
        rows = {d: {'2 Yr': str(facts['UST_2Y']['value']),
                    '10 Yr': str(facts['UST_10Y']['value']),
                    '30 Yr': str(facts['UST_30Y']['value'])} for d in want}
        return rows, _ev('https://t.gov/curve'), 'raw-treasury'

    def coinbase(product, s, e):
        mid = 'BTC' if product == 'BTC-USD' else 'GOLD_F'
        f = facts.get(mid)
        if not f:
            return {}, _ev('https://c.io/' + product), None
        od = str(f['observation_date'])[:10]
        return {od: {'close': f['value'], 'start_ts': epoch_of(od)}}, \
            _ev('https://c.io/' + product), f'raw-{product}'

    def sina(c):
        f = facts['SHCOMP']
        od = str(f['observation_date'])[:10]
        return {'close': f['value'], 'date': od, 'time': '15:30:00'}, \
            _ev('https://s.cn/' + c), 'raw-sina'

    def fred(sid):
        mid = 'SPX' if sid == 'SP500' else 'WTI_F'
        f = facts[mid]
        od = str(f['observation_date'])[:10]
        return ([(od, f['value'])],
                _ev('https://api.stlouisfed.org/fred/series/observations'
                    '?api_key=RAWKEY42&series_id=' + sid), f'raw-{sid}')

    return {'treasury': treasury, 'coinbase': coinbase, 'sina': sina, 'fred': fred}


class F1DSourceBinding(unittest.TestCase):
    """D组: 八项检查来源绑定(FIX1-06)+Treasury跨年度(FIX1-07)。"""

    def test_d1_eight_check_ids_unique_complete(self):
        facts = _full_facts()
        res, evs, raws = rda.run_external_checks(
            facts, _stub_fetchers(facts), DAY, log=[])
        ids = [r['check_id'] for r in res]
        self.assertEqual(len(res), 8)
        self.assertEqual(sorted(set(ids)), sorted(rda.CHECK_IDS.values()))  # 不重复
        self.assertEqual(len(ids), len(set(ids)))                           # 无缺失
        for r in res:
            self.assertIn('external_source', r)
            self.assertIn('source_identity', r)
            self.assertIn('evidence_ids', r)

    def test_d2_ours_preserves_fact_source(self):
        facts = _full_facts()
        res, _, _ = rda.run_external_checks(facts, _stub_fetchers(facts), DAY, log=[])
        by_mid = {r['metric_id']: r for r in res}
        for mid in ('UST_10Y', 'SPX', 'SHCOMP', 'BTC'):
            src = facts[mid].get('source')
            self.assertEqual(by_mid[mid]['ours'].get('source'), src,
                             f'{mid} ours.source必须保留fact来源')

    def test_d3_evidence_ids_resolvable(self):
        facts = _full_facts()
        res, evs, raws = rda.run_external_checks(
            facts, _stub_fetchers(facts), DAY, log=[])
        evmap = {e.get('evidence_id') for e in evs}
        by_id = {r['check_id']: r for r in res}
        for r in res:   # 所有实际引用必须能在external_evidence中定位
            for i in r['evidence_ids']:
                self.assertIn(i, evmap, f"{r['check_id']}引用{i}不可定位")
        # 三UST共享年度CSV证据;SPX与WTI各自独立;BTC与PAXG各自独立
        for cid in ('EXT-UST-2Y', 'EXT-UST-10Y', 'EXT-UST-30Y'):
            self.assertIn('EV-TSY-2026', by_id[cid]['evidence_ids'])
        self.assertEqual(by_id['EXT-SPX']['evidence_ids'], ['EV-FRED-SP500'])
        self.assertEqual(by_id['EXT-WTI-F']['evidence_ids'], ['EV-FRED-DCOILWTICO'])
        self.assertEqual(by_id['EXT-BTC']['evidence_ids'], ['EV-CB-BTC-USD'])
        self.assertIn('EV-CB-PAXG-USD', by_id['EXT-GOLD-F']['evidence_ids'])
        self.assertIn('EV-SINA-SH000001', by_id['EXT-SHCOMP']['evidence_ids'])
        # 外部结构化字段镜像(PASS行)
        self.assertIn('evidence_ids', by_id['EXT-SPX']['external'])
        self.assertIn('external_source', by_id['EXT-SPX']['external'])

    def test_d4_treasury_cross_year(self):
        # 固定场景: UST_2Y=2025-12-31,UST_10Y/30Y=2026-01-02 → 必须请求两个年度
        facts = {'UST_2Y': ust_fact('UST_2Y', 4.30, '2025-12-31'),
                 'UST_10Y': ust_fact('UST_10Y', 4.60, '2026-01-02'),
                 'UST_30Y': ust_fact('UST_30Y', 4.90, '2026-01-02'),
                 'BTC': ust_fact('BTC', 71000.0, '2026-01-02'),
                 'GOLD_F': ust_fact('GOLD_F', 2700.0, '2026-01-02'),
                 'SHCOMP': ust_fact('SHCOMP', 3300.0, '2026-01-02'),
                 'SPX': ust_fact('SPX', 7700.0, '2026-01-02'),
                 'WTI_F': ust_fact('WTI_F', 71.0, '2026-01-02')}
        called = []

        def treasury(year, want):
            called.append((year, tuple(sorted(want))))
            rows = {d: {'2 Yr': '4.30', '10 Yr': '4.60', '30 Yr': '4.90'}
                    for d in want}
            return rows, {'source': 't', 'url': 'https://t.gov/x',
                          'fetched_at_utc': 'now'}, 'raw'
        stubs = _stub_fetchers(facts, treasury_impl=treasury)
        stubs['treasury'] = treasury
        res, evs, raws = rda.run_external_checks(facts, stubs, '20260102', log=[])
        years = [y for y, _ in called]
        self.assertIn(2025, years)
        self.assertIn(2026, years)     # 必须发起2025与2026两年度请求
        self.assertEqual(dict(called)[2025], ('2025-12-31',))
        self.assertEqual(dict(called)[2026], ('2026-01-02',))
        verdicts = {r['check_id']: r['verdict'] for r in res}
        self.assertEqual(verdicts['EXT-UST-2Y'], 'PASS')    # 各自同日匹配
        self.assertEqual(verdicts['EXT-UST-10Y'], 'PASS')
        self.assertEqual(verdicts['EXT-UST-30Y'], 'PASS')
        evmap = {e.get('evidence_id') for e in evs}
        self.assertIn('EV-TSY-2025', evmap)                 # 每年证据保留
        self.assertIn('EV-TSY-2026', evmap)

    def test_d5_single_year_failure_keeps_other_year(self):
        # 2025年API失败 → 仅2025日期(UST_2Y)NOT_VERIFIED;2026三期限不受影响
        facts = {'UST_2Y': ust_fact('UST_2Y', 4.30, '2025-12-31'),
                 'UST_10Y': ust_fact('UST_10Y', 4.60, '2026-01-02'),
                 'UST_30Y': ust_fact('UST_30Y', 4.90, '2026-01-02'),
                 'BTC': ust_fact('BTC', 71000.0, '2026-01-02'),
                 'GOLD_F': ust_fact('GOLD_F', 2700.0, '2026-01-02'),
                 'SHCOMP': ust_fact('SHCOMP', 3300.0, '2026-01-02'),
                 'SPX': ust_fact('SPX', 7700.0, '2026-01-02'),
                 'WTI_F': ust_fact('WTI_F', 71.0, '2026-01-02')}

        def treasury(year, want):
            if year == 2025:
                return {}, {'source': 't', 'url': 'https://t.gov/x',
                            'fetched_at_utc': 'now',
                            'error': 'ConnectionError: 2025 CSV不可达'}, None
            rows = {d: {'2 Yr': '4.30', '10 Yr': '4.60', '30 Yr': '4.90'}
                    for d in want}
            return rows, {'source': 't', 'url': 'https://t.gov/x',
                          'fetched_at_utc': 'now'}, 'raw'
        stubs = _stub_fetchers(facts, treasury_impl=treasury)
        stubs['treasury'] = treasury
        res, evs, _ = rda.run_external_checks(facts, stubs, '20260102', log=[])
        verdicts = {r['check_id']: r['verdict'] for r in res}
        self.assertEqual(verdicts['EXT-UST-2Y'], 'NOT_VERIFIED')
        self.assertEqual(verdicts['EXT-UST-10Y'], 'PASS')
        self.assertEqual(verdicts['EXT-UST-30Y'], 'PASS')
        evmap = {e.get('evidence_id') for e in evs}
        self.assertIn('EV-TSY-2025', evmap)   # 失败年证据仍在(诊断留痕)
        self.assertIn('EV-TSY-2026', evmap)

    def test_d6_no_fred_key_empty_not_fabricated(self):
        # 无FRED密钥: SPX/WTI来源明确为空(evidence_ids=[]/external_source=None),
        # external_evidence中无任何伪造的FRED证据ID
        facts = _full_facts()
        stubs = _stub_fetchers(facts)
        stubs['fred'] = None
        res, evs, _ = rda.run_external_checks(facts, stubs, DAY, log=[])
        by_id = {r['check_id']: r for r in res}
        for cid in ('EXT-SPX', 'EXT-WTI-F'):
            self.assertEqual(by_id[cid]['evidence_ids'], [])
            self.assertIsNone(by_id[cid]['external_source'])
            self.assertEqual(by_id[cid]['verdict'], 'NOT_VERIFIED')
        for e in evs:
            self.assertNotIn('FRED', str(e.get('evidence_id', '')))


class F1EDegradationSensitivity(unittest.TestCase):
    """E组: 七项FIX1缺陷的关键错误逻辑恢复后,对应断言必须能检出(退化注入)。"""

    def setUp(self):
        self._saved = list(rda._KNOWN_SECRETS)

    def tearDown(self):
        rda._KNOWN_SECRETS[:] = self._saved

    def test_e1_fix101_raw_error_leak_caught(self):
        # 恢复FIX1-01缺陷(err原文截断入证据) → 变体泄漏虚构密钥,正确版零泄漏
        rda._register_secret('FAKEKEYE1TEST00000000000ZZ')
        err = requests.exceptions.HTTPError(
            '401 Client Error for url: https://api.stlouisfed.org/x'
            '?api_key=FAKEKEYE1TEST00000000000ZZ&f=json')
        m = load_variant(
            'f1e1',
            "        ev['error'] = _safe_error(err)   # FIX1-01: 先全量脱敏再截断,保类型/HTTP状态",
            "        ev['error'] = str(err)[:200]")
        good = rda._evidence('FRED SP500', 'https://api.stlouisfed.org/x', err=err)
        bad = m._evidence('FRED SP500', 'https://api.stlouisfed.org/x', err=err)
        self.assertNotIn('FAKEKEYE1TEST00000000000ZZ', good['error'])
        self.assertIn('FAKEKEYE1TEST00000000000ZZ', bad['error'])   # 退化版泄漏

    def test_e2_fix102_end_price_check_removed_caught(self):
        # 恢复FIX1-02缺陷(期末价格字段不校验) → 期末111反例变非FAIL
        ser = F1BRecomputeIntegrity.SER
        wk = F1BRecomputeIntegrity.WK_OK
        f = make_fact('SPX', 111.0, '2026-10-23', 'index_point', derived={
            'end': {'date': '2026-10-23', 'value': 111.0},
            'week': dict(wk), 'mtd': {'available': False},
            'ytd': {'available': False}})
        self.assertEqual(rda.recompute_check('SPX', f, ser)['verdict'], 'FAIL')
        m = load_variant(
            'f1e2',
            "    _end_dev = _price_mismatch_pct(close, ind.get('close'))",
            "    _end_dev = None")
        r = m.recompute_check('SPX', f, ser)
        self.assertNotEqual(r['verdict'], 'FAIL')       # 退化版洗白
        self.assertEqual(r['periods']['week']['status'], 'PASS')

    def test_e3_fix103_partial_as_pass_caught(self):
        # 恢复FIX1-03缺陷(部分复核判PASS) → 部分复核反例变PASS+伪complete
        snap = fixt.real_snapshot(DAY)
        facts = {f['metric_id']: f for f in snap['facts']}
        store = snap.get('series_store') or {}
        r = rda.recompute_check('SPX', facts['SPX'], store['SPX'])
        self.assertEqual(r['verdict'], 'INSUFFICIENT_HISTORY')
        self.assertFalse(r['complete_recompute'])
        m = load_variant(
            'f1e3',
            "        verdict = 'INSUFFICIENT_HISTORY'       # 部分复核/全缺: 不冒充完整PASS",
            "        verdict = 'PASS'")
        rv = m.recompute_check('SPX', facts['SPX'], store['SPX'])
        self.assertEqual(rv['verdict'], 'PASS')          # 退化版冒充
        self.assertTrue(rv['complete_recompute'])        # 且伪称完整

    def test_e4_fix104_historical_exemption_restored_caught(self):
        # 恢复FIX1-04缺陷(仅当日才检查收盘时间→历史日期豁免) → 历史10:30变PASS
        f = {'metric_id': 'SHCOMP', 'value': 3272.0,
             'observation_date': '2026-10-29', 'unit': 'index_point'}
        q = {'close': 3272.0, 'date': '2026-10-29', 'time': '10:30:00'}
        spec = rda.TOLERANCES['sina_shcomp']
        self.assertEqual(rda.check_shcomp(f, q, '20261030', spec)['verdict'],
                         'NOT_VERIFIED')
        m = load_variant(
            'f1e4',
            "    if not qt or qt < '15:30:00':",
            "    if (f\"{today_ymd[:4]}-{today_ymd[4:6]}-{today_ymd[6:]}\") == qd"
            " and (not qt or qt < '15:30:00'):")
        self.assertEqual(m.check_shcomp(f, q, '20261030', spec)['verdict'],
                         'PASS')                          # 退化版: 历史日盘中放行

    def test_e5_fix105_path_guard_removed_caught(self):
        # 恢复FIX1-05缺陷(不检查输出路径) → 输出写进数据目录且不拒绝
        with tempfile.TemporaryDirectory() as td:
            fixt.write_collectors(td, DAY)
            fake_now = f'{DAY[:4]}-{DAY[4:6]}-{DAY[6:]}T08:00:00'

            class _DT(datetime):
                @classmethod
                def now(cls, tz=None):
                    return cls.fromisoformat(fake_now)
            m = load_variant(
                'f1e5',
                "    _conflict = path_conflict(args.data_dir, args.out_dir)",
                "    _conflict = None")
            out = io.StringIO()
            argv = ['rda', '--data-dir', td, '--out-dir', os.path.join(td, 'acc'),
                    '--data-day', DAY, '--trusted-root', td, '--skip-external']
            with mock.patch.object(sys, 'argv', argv), \
                    mock.patch.object(m, 'datetime', _DT), \
                    mock.patch.object(m, 'ROOT_DIR', rda.ROOT_DIR), \
                    contextlib.redirect_stdout(out):
                try:
                    m.main()
                    rc = 0
                except SystemExit as e:
                    rc = e.code
            # 退化版: 不拒绝(rc=3离线诊断)且把验收报告写进了数据目录
            self.assertEqual(rc, 3)
            self.assertTrue(glob.glob(os.path.join(td, 'acc', 'real_acceptance_*.json')))
            # 正确版(FIX1): 拒绝exit2零写入
            out2 = io.StringIO()
            argv2 = ['rda', '--data-dir', td, '--out-dir', os.path.join(td, 'acc2'),
                     '--data-day', DAY, '--trusted-root', td, '--skip-external']
            with mock.patch.object(sys, 'argv', argv2), \
                    mock.patch.object(rda, 'datetime', _DT), \
                    contextlib.redirect_stdout(out2):
                try:
                    rda.main()
                    rc2 = 0
                except SystemExit as e:
                    rc2 = e.code
            self.assertEqual(rc2, 2)
            self.assertFalse(os.path.exists(os.path.join(td, 'acc2')))

    def test_e6_fix107_single_year_regression_caught(self):
        # 恢复FIX1-07缺陷(只请求最早观测日所在年度) → 2026期限NOT_VERIFIED
        facts = {'UST_2Y': ust_fact('UST_2Y', 4.30, '2025-12-31'),
                 'UST_10Y': ust_fact('UST_10Y', 4.60, '2026-01-02'),
                 'UST_30Y': ust_fact('UST_30Y', 4.90, '2026-01-02'),
                 'BTC': ust_fact('BTC', 71000.0, '2026-01-02'),
                 'GOLD_F': ust_fact('GOLD_F', 2700.0, '2026-01-02'),
                 'SHCOMP': ust_fact('SHCOMP', 3300.0, '2026-01-02'),
                 'SPX': ust_fact('SPX', 7700.0, '2026-01-02'),
                 'WTI_F': ust_fact('WTI_F', 71.0, '2026-01-02')}

        def treasury(year, want):
            rows = {d: {'2 Yr': '4.30', '10 Yr': '4.60', '30 Yr': '4.90'}
                    for d in want}
            return rows, {'source': 't', 'url': 'https://t.gov/x',
                          'fetched_at_utc': 'now'}, 'raw'
        stubs = _stub_fetchers(facts, treasury_impl=treasury)
        stubs['treasury'] = treasury
        res, _, _ = rda.run_external_checks(facts, stubs, '20260102', log=[])
        ok = {r['check_id']: r['verdict'] for r in res}
        self.assertEqual(ok['EXT-UST-10Y'], 'PASS')
        m = load_variant(
            'f1e6',
            "    years = sorted({d[:4] for d in want}) or [str(date.today().year)]",
            "    years = [sorted(want)[0][:4]] if want else [str(date.today().year)]")
        res2, _, _ = m.run_external_checks(facts, stubs, '20260102', log=[])
        bad = {r['check_id']: r['verdict'] for r in res2}
        self.assertEqual(bad['EXT-UST-2Y'], 'PASS')      # 2025行在(最早年)
        self.assertEqual(bad['EXT-UST-10Y'], 'NOT_VERIFIED')   # 2026被抹掉
        self.assertEqual(bad['EXT-UST-30Y'], 'NOT_VERIFIED')

    def test_e7_fix106_binding_stripped_caught(self):
        # 恢复FIX1-06缺陷(不绑定check_id) → 变体检查行无稳定标识
        facts = _full_facts()
        res, _, _ = rda.run_external_checks(facts, _stub_fetchers(facts), DAY, log=[])
        self.assertTrue(all(r.get('check_id') in rda.CHECK_IDS.values() for r in res))
        m = load_variant(
            'f1e7',
            "        result['check_id'] = CHECK_IDS[mid]",
            "        pass")
        res2, _, _ = m.run_external_checks(facts, _stub_fetchers(facts), DAY, log=[])
        self.assertTrue(any('check_id' not in r for r in res2))   # 退化版缺绑定


if __name__ == '__main__':
    unittest.main(verbosity=2)
