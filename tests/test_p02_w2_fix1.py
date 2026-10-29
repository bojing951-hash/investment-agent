#!/usr/bin/env python3
"""IA-P0-2-W2-FIX1 联合验收测试(IA-P02-W2-DEF-001/002/003 整改证据)。

真实模块+真实文件系统+隔离临时目录;mock仅限外部GLM/时钟(承fix9口径)。

矩阵(对应指令§5.4/§6.6/§7.6/§十):
  A §5.4 非法日期反例表(BTC 2日窗, as_of=2026-10-24): 合法'2026-10-23'/
     后缀垃圾'2026-10-23INVALID'/'2026-10-23xxx'/假日历'2026-02-30'/None/[]/
     未来'2026-10-25'/as_of非法'2026-10-24INVALID' — 同一输入在
     fp.assess / dv.is_fresh_anchor / dv.stale_anchor_warning /
     ae.verify_evidence_items(真实正式消费入口)四处口径一致(不得一方
     INVALID_DATE另一方True);完整ISO时间戳允许且整串先验证,观测日
     语义=纯日期(与P0-1-FIX5冻结原语fe.parse_iso_date一致);
  B §6.6 发布日期十场景(RELEASE_UNKNOWN/非法/先于观测/晚于as_of/正常/
     当日发布/Agent4精确反例 lag53≤60但NOT_AVAILABLE_AT_AS_OF/真实fe入口/
     真实Gate B入口含sb透传与仅拒绝性消费/不伪造发布日期);
  C §7.6 锚点来源-身份反例(global_market.data.CPI.close等跨通道spoof/
     身份冲突/未注册/非规范键/同名跨家族/自报metric_id)+真实sb锚点
     正向回环(合法构建0个UNVERIFIED)+scorecard诊断兼容;
  D §十 联合E2E: 正常研究对照(PASS/合法DEGRADED)/未来发布CPI真实链路
     (快照→Gate A→数据包→周报预检→GLM=0,受控失败)/已发布报告四对象
     SHA-256执行前基线保护/真实锚点文件spoof(P0-1权威重建不可绕过)/
     真实dv+dpo(正式观察消费入口)上的日期异常。
"""
import contextlib
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
from datetime import date, datetime
from unittest import mock

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(_HERE), 'scripts'))
sys.path.insert(0, _HERE)

import fixt                                    # noqa: E402
import freshness_policy as fp                  # noqa: E402
import fact_engine as fe                       # noqa: E402
import data_validator as dv                    # noqa: E402
import snapshot_builder as sb                  # noqa: E402
import research_provenance as rp               # noqa: E402
import allocation_engine as ae                 # noqa: E402
import data_assembler as da                    # noqa: E402
import report_generator as rg                  # noqa: E402
import daily_prediction_observer as dpo        # noqa: E402

DAY = '20261024'
AS_OF = '2026-10-24'
AS_OF_TS = '2026-10-24T08:00:00+08:00'      # 真实锚点文件as_of形态(完整时间戳)
BTC_KEY = 'global_market.data.BTC.close'
CPI_KEY = 'macro.data.CPI.value'
CPI_OBS = '2026-09-01'                      # 月频, 窗60天, lag=53
PASS_N, FAIL_N = 0, 0
_TMPD = tempfile.mkdtemp(prefix='w2fix1-')


def check(name, cond, detail=''):
    global PASS_N, FAIL_N
    if cond:
        PASS_N += 1
        print(f"  ✅ {name}")
    else:
        FAIL_N += 1
        print(f"  ❌ {name}  {detail}")


def quiet(fn, *a, **kw):
    with contextlib.redirect_stdout(io.StringIO()), \
            contextlib.redirect_stderr(io.StringIO()):
        return fn(*a, **kw)


def sha(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


class _DT:
    """固定时钟: 不依赖机器当天日期;strptime转发真实datetime。"""
    def __init__(self, ymd):
        self._ymd = ymd

    @staticmethod
    def strptime(s, f):
        return datetime.strptime(s, f)

    def now(self, tz=None):
        return datetime(int(self._ymd[:4]), int(self._ymd[4:6]),
                        int(self._ymd[6:]), 8, 0, 0)


class _GLM:
    """外部GLM替身(≥500字,防截断保护误拒);只计数不落盘。"""
    def __init__(self):
        self.calls = 0

    def __call__(self, system_prompt, user_prompt, max_tokens=32000, timeout=900):
        self.calls += 1
        return ('# 投资周报(SYNTHETIC测试文本·W2-FIX1)\n\n'
                + '本周市场综述与分资产回顾。' * 60)


def build_day(mutate_macro=None, break_metric=None, ymd=DAY, root=None):
    """真实链路一天(fixt采集→真实sb.build_snapshot),返回(root, daily, snap)。"""
    td = root or tempfile.mkdtemp(prefix='w2fix1-day-', dir=_TMPD)
    daily = os.path.join(td, 'data', 'daily')
    os.makedirs(daily, exist_ok=True)
    fixt.write_collectors(daily, ymd, break_metric=break_metric)
    if mutate_macro:
        p = os.path.join(daily, f'macro_{ymd}.json')
        obj = json.load(open(p, encoding='utf-8'))
        mutate_macro(obj)
        json.dump(obj, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
    quiet(sb.build_snapshot, ymd, daily, daily, trusted_root=td,
          as_of=fixt.as_of_for(ymd))
    snap = json.load(open(os.path.join(daily, f'research_snapshot_{ymd}.json'),
                          encoding='utf-8'))
    return td, daily, snap


def fact_of(snap, mid):
    return next(f for f in snap['facts'] if f['metric_id'] == mid)


def rg_harness(glm, applied, data_dir, out_dir, ymd):
    """真实generate_weekly_report运行上下文(mock仅限GLM/时钟/外部装载)。"""
    return [
        mock.patch.object(rg, 'DATA_DIR', data_dir),
        mock.patch.object(rg, 'OUTPUT_DIR', out_dir),
        mock.patch.object(rg, 'datetime', _DT(ymd)),
        mock.patch.object(rg, '_call_glm', glm),
        mock.patch.object(rg, 'apply_status_updates',
                          lambda *a, **k: applied.append(1)),
        mock.patch.object(rg, 'validate_generated_report',
                          lambda md, anchors=None, anchors_file=None:
                          ('PASS', ['SYNTHETIC警告'])),
        mock.patch.object(rg.allocation_engine, 'load_views',
                          lambda *a, **k: {'views': [], 'predictions': []}),
        mock.patch.object(rg, 'pending_completed_month', lambda d=None: None),
        mock.patch.object(rg, 'pending_completed_quarter', lambda d=None: None),
        mock.patch.object(rg, 'load_framework', lambda: '框架'),
        mock.patch.object(rg, 'load_theses', lambda: '论点'),
        mock.patch.object(rg, 'load_technical_notes', lambda: ''),
        mock.patch.object(rg, 'load_news_summary', lambda: ''),
        mock.patch.object(rg, 'load_previous_report', lambda: ''),
    ]


def rg_run(harness_list):
    """在harness下运行真实generate_weekly_report,返回exit code(SystemExit)。"""
    with contextlib.ExitStack() as st:
        for h in harness_list:
            st.enter_context(h)
        try:
            quiet(rg.generate_weekly_report)
            return 0
        except SystemExit as e:
            return e.code


def ae_try(obs, as_of=AS_OF, key=BTC_KEY):
    """真实正式证据消费入口(ae.verify_evidence_items,rg/ae生产同路径)。"""
    ev = [{'metric': key, 'value': 93000.0, 'obs_date': obs, 'mechanism': 'FIX1测试'}]
    anc = {key: {'value': 93000.0, 'obs_date': obs}}
    try:
        ver, rej = ae.verify_evidence_items(ev, anc, as_of)
        return len(ver), (rej[0][0] if rej else '')
    except Exception as e:                     # noqa: BLE001 — 异常本身即失败证据
        return -1, f'EXC:{e}'


print("═" * 72)
print("IA-P0-2-W2-FIX1: 非法日期洗白/发布日期消费/锚点来源身份 三缺陷整改")
print("═" * 72)

# ══ A. §5.4 非法日期反例表 ══════════════════════════════════════════
print("\n[A] §5.4 非法日期反例表: 四个正式消费入口口径一致")

_ok_inst = [date(2026, 10, 24), datetime(2026, 10, 24, 8, 0, 0), '2026-10-24',
            '2026-10-24T08:00:00+08:00', '2026-10-24 08:00:00+08:00',
            '2026-10-24T00:00:00Z', '2026-10-24T08:00:00.123456+00:00',
            '2026-10-24T08:00:00']
check("A1a 共享原语fp.parse_instant: date/datetime实例/完整ISO日期/完整ISO"
      "时间戳(T/空格/Z/±HH:MM/微秒/无时区)整串接受",
      all(fp.parse_instant(x) == date(2026, 10, 24) for x in _ok_inst))
_bad_inst = ['', '2026-10-24INVALID', '2026-10-24xxx', '2026-02-30', '2026-13-01',
             '2026-10-24T08:00:00+08:00GARBAGE', '2026-10-24T08:00:00+0800',
             '2026-10-24T25:00:00', None, 123, [], {}, '10-24-2026', ' 2026-10-24']
check("A1b parse_instant: 后缀垃圾/假日历/非法月/部分时间/无冒号时差/前后缀"
      "空白/非字符串一律None(绝不[:10]截断救活)",
      all(fp.parse_instant(x) is None for x in _bad_inst))

# §5.4强制反例表: (obs, assess期望status, fresh期望, ae拒绝理由子串)
TABLE = [
    ('2026-10-23', 'FRESH', True, ''),
    ('2026-10-23INVALID', 'INVALID_DATE', False, '不可解析'),
    ('2026-10-23xxx', 'INVALID_DATE', False, '不可解析'),
    ('2026-02-30', 'INVALID_DATE', False, '不可解析'),
    (None, 'NOT_OBSERVED', False, '缺obs_date'),
    ([], 'INVALID_DATE', False, '不可解析'),
    ('2026-10-25', 'FUTURE_DATE', False, '未来'),
]
for obs, st_exp, fresh_exp, rej_exp in TABLE:
    v = fp.assess('BTC', obs, AS_OF)
    info = {'value': 93000.0, 'obs_date': obs}
    dv_fresh = dv.is_fresh_anchor(BTC_KEY, info, AS_OF)
    warn = dv.stale_anchor_warning(BTC_KEY, info, AS_OF)
    n_ver, rej_msg = ae_try(obs)
    ok = (v['status'] == st_exp and v['fresh'] is fresh_exp
          and dv_fresh is fresh_exp and (n_ver == 1) is fresh_exp
          and (rej_exp in rej_msg) if rej_exp else (rej_msg == '')
          and (warn is None) is fresh_exp
          and ('无法判龄' in warn if (warn and st_exp in ('INVALID_DATE',
                                                           'NOT_OBSERVED'))
               else True)
          and ('未来数据' in warn if (warn and st_exp == 'FUTURE_DATE') else True))
    check(f"A2 obs={obs!r}: assess={st_exp}+dv={fresh_exp}+ae"
          f"{'拒(' + rej_exp + ')' if rej_exp else '过'}+警示一致",
          bool(ok), f"assess={v['status']}/{v['fresh']} dv={dv_fresh} "
                    f"ae={n_ver}:{rej_msg[:40]} warn={str(warn)[:40]}")

# as_of非法(§5.4表末行): 整串验证,不得截断洗白
v_bad_asof = fp.assess('BTC', '2026-10-23', '2026-10-24INVALID')
dv_bad_asof = dv.is_fresh_anchor(BTC_KEY, {'value': 1, 'obs_date': '2026-10-23'},
                                 '2026-10-24INVALID')
w_bad_asof = dv.stale_anchor_warning(BTC_KEY, {'value': 1, 'obs_date': '2026-10-23'},
                                     '2026-10-24INVALID')
n_bad_asof, rej_bad_asof = ae_try('2026-10-23', as_of='2026-10-24INVALID')
check("A3 as_of='2026-10-24INVALID': assess=INVALID_DATE+dv=False+ae拒(研究"
      "截止非法)+警示无法判龄(四处一致拒绝)",
      v_bad_asof['status'] == 'INVALID_DATE' and v_bad_asof['fresh'] is False
      and dv_bad_asof is False and n_bad_asof == 0 and '研究截止' in rej_bad_asof
      and w_bad_asof and '无法判龄' in w_bad_asof and 'INVALID' in w_bad_asof,
      f"assess={v_bad_asof['status']} dv={dv_bad_asof} ae={rej_bad_asof[:40]}")
v_ts_garbage = fp.assess('BTC', '2026-10-23', '2026-10-24T08:00:00+08:00X')
check("A4 as_of=完整时间戳+后缀垃圾('…+08:00X')同样拒绝(时间戳接受≠放松"
      "整串验证)", v_ts_garbage['status'] == 'INVALID_DATE'
      and dv.is_fresh_anchor(BTC_KEY, {'value': 1, 'obs_date': '2026-10-23'},
                             '2026-10-24T08:00:00+08:00X') is False)
check("A5 完整ISO时间戳作as_of正常接受(整串先验证再取日期): "
      f"assess={fp.assess('BTC', '2026-10-23', AS_OF_TS)['status']}, "
      "dv.is_fresh=True",
      fp.assess('BTC', '2026-10-23', AS_OF_TS)['status'] == 'FRESH'
      and dv.is_fresh_anchor(BTC_KEY, {'value': 1, 'obs_date': '2026-10-23'},
                             AS_OF_TS) is True)
obs_ts = fp.assess('BTC', '2026-10-23T08:00:00+08:00', AS_OF)
check("A6 观测日语义=纯日期: 带时间戳obs按INVALID_DATE拒绝,与P0-1-FIX5冻结"
      "原语fe.parse_iso_date(带时间戳→None)同口径(共享原语不分歧)",
      obs_ts['status'] == 'INVALID_DATE'
      and fe.parse_iso_date('2026-10-23T08:00:00+08:00') is None,
      f"assess={obs_ts['status']}")

# ══ B. §6.6 发布日期十场景 ══════════════════════════════════════════
print("\n[B] §6.6 发布日期十场景: 只消费真实采集记录的release_date")

# 场景1: RELEASE_UNKNOWN — 有限新鲜度判断仍允许+披露
v1 = fp.assess('CPI', CPI_OBS, AS_OF)
check("B1 缺release(RELEASE_UNKNOWN): 窗内仍FRESH(有限新鲜度)+点时状态"
      "如实UNKNOWN(不伪造)", v1['status'] == 'FRESH'
      and v1['point_in_time']['status'] == 'RELEASE_UNKNOWN',
      f"{v1['status']}/{v1['point_in_time']['status']}")
f1 = fe.make_fact('CPI', 316.0, CPI_OBS, AS_OF_TS, 'macro_20261024.json',
                  'macro_collector')
m_cpi = fe.metric('CPI')
iss1 = fe.validate_fact(f1, {'value': 316.0, 'date': CPI_OBS}, m_cpi,
                        as_of_date=AS_OF_TS)
check("B1b 真实fe.validate_fact: 月频缺release→WARN披露(RELEASE_UNKNOWN),"
      "不FAIL既有数据", fe.grade_issues(iss1) == 'WARN'
      and any(i['category'] == 'release' and i['severity'] == 'WARN'
              and 'RELEASE_UNKNOWN' in i['message'] for i in iss1),
      str(iss1))
check("B1c dv有限时效判断不受影响: 缺release锚点is_fresh=True(窗内)",
      dv.is_fresh_anchor(CPI_KEY, {'value': 316.0, 'obs_date': CPI_OBS},
                         AS_OF) is True)

# 场景2: release非法
for bad_rel in ['not-a-date', '2026-09-15INVALID']:
    v2 = fp.assess('CPI', CPI_OBS, AS_OF, release_date=bad_rel)
    check(f"B2 release={bad_rel!r}: assess=INVALID_RELEASE+fresh=False",
          v2['status'] == 'INVALID_RELEASE' and v2['fresh'] is False,
          v2['status'])
f2 = fe.make_fact('CPI', 316.0, CPI_OBS, AS_OF_TS, 'macro_20261024.json',
                  'macro_collector', release_date='not-a-date')
iss2 = fe.validate_fact(f2, {'value': 316.0, 'date': CPI_OBS}, m_cpi,
                        as_of_date=AS_OF_TS)
check("B2b 真实validate_fact: 非法release→FAIL(category=release)",
      any(i['severity'] == 'FAIL' and i['category'] == 'release' for i in iss2)
      and fe.grade_issues(iss2) == 'FAIL', str(iss2))

# 场景3: release早于观测
v3 = fp.assess('CPI', CPI_OBS, AS_OF, release_date='2026-08-01')
f3 = fe.make_fact('CPI', 316.0, CPI_OBS, AS_OF_TS, 'macro_20261024.json',
                  'macro_collector', release_date='2026-08-01')
iss3 = fe.validate_fact(f3, {'value': 316.0, 'date': CPI_OBS}, m_cpi,
                        as_of_date=AS_OF_TS)
check("B3 release=2026-08-01早于观测2026-09-01: INVALID_RELEASE/发布先于"
      "观测→validate_fact FAIL", v3['status'] == 'INVALID_RELEASE'
      and any(i['severity'] == 'FAIL' and '发布先于观测' in i['message']
              for i in iss3), f"{v3['status']} {str(iss3)[:80]}")

# 场景4: release晚于as_of → Agent4反例数值(与B7同参,先看单层)
v4 = fp.assess('CPI', CPI_OBS, AS_OF, release_date='2026-10-28')
f4 = fe.make_fact('CPI', 316.0, CPI_OBS, AS_OF_TS, 'macro_20261024.json',
                  'macro_collector', release_date='2026-10-28')
iss4 = fe.validate_fact(f4, {'value': 316.0, 'date': CPI_OBS}, m_cpi,
                        as_of_date=AS_OF_TS)
w4 = dv.stale_anchor_warning(CPI_KEY, {'value': 316.0, 'obs_date': CPI_OBS,
                                       'release_date': '2026-10-28'}, AS_OF)
check("B4 release=2026-10-28晚于as_of: NOT_AVAILABLE_AT_AS_OF+validate_fact"
      " FAIL+警示点时不可得",
      v4['status'] == 'NOT_AVAILABLE_AT_AS_OF' and v4['fresh'] is False
      and any(i['severity'] == 'FAIL' and 'NOT_AVAILABLE_AT_AS_OF' in i['message']
              for i in iss4)
      and w4 and '点时不可得' in w4,
      f"{v4['status']} {str(iss4)[:80]}")

# 场景5/6: 正常发布/当日发布
v5 = fp.assess('CPI', CPI_OBS, AS_OF, release_date='2026-09-15')
f5 = fe.make_fact('CPI', 316.0, CPI_OBS, AS_OF_TS, 'macro_20261024.json',
                  'macro_collector', release_date='2026-09-15')
iss5 = fe.validate_fact(f5, {'value': 316.0, 'date': CPI_OBS}, m_cpi,
                        as_of_date=AS_OF_TS)
v6 = fp.assess('CPI', CPI_OBS, AS_OF, release_date=CPI_OBS)
check("B5 正常release(2026-09-15,观测后as_of前): FRESH+点时OK+validate_fact"
      " 无release问题", v5['status'] == 'FRESH'
      and v5['point_in_time']['status'] == 'OK'
      and not any(i['category'] == 'release' for i in iss5),
      f"{v5['status']} {str(iss5)[:60]}")
check("B6 release==观测日(2026-09-01,当日发布合法): FRESH(仅release<观测"
      "非法)", v6['status'] == 'FRESH'
      and v6['point_in_time']['status'] == 'OK', v6['status'])

# 场景7: Agent 4精确反例 — 观测滞后窗内但点时不可得
v7 = fp.assess('CPI', CPI_OBS, AS_OF, release_date='2026-10-28')
anc7 = {CPI_KEY: {'value': 316.0, 'obs_date': CPI_OBS,
                  'release_date': '2026-10-28'}}
ver7, rej7 = ae.verify_evidence_items(
    [{'metric': CPI_KEY, 'value': 316.0, 'obs_date': CPI_OBS, 'mechanism': '通胀'}],
    anc7, AS_OF)
check("B7 Agent4精确反例(CPI obs=2026-09-01/as_of=2026-10-24/release="
      "2026-10-28): lag53≤60窗内**但**NOT_AVAILABLE_AT_AS_OF不得作当前证据"
      "(assess+dv+ae三入口同拒;W2-FIX4起ae拒收原因如实分流为'点时不可得'"
      "而非误导性'数据过期'——观测并不滞后,不可得的是as_of时点)",
      v7['lag_days'] == 53 and v7['window'] == 60
      and v7['status'] == 'NOT_AVAILABLE_AT_AS_OF' and v7['fresh'] is False
      and dv.is_fresh_anchor(CPI_KEY, anc7[CPI_KEY], AS_OF) is False
      and ver7 == [] and rej7 and '点时不可得' in rej7[0][0]
      and '晚于研究截止' in rej7[0][0],
      f"lag={v7['lag_days']} win={v7['window']} {v7['status']} "
      f"dv={dv.is_fresh_anchor(CPI_KEY, anc7[CPI_KEY], AS_OF)} "
      f"ae={str(rej7)[:60]}")

# 场景8: 真实fe入口(normalize_macro消费采集记录,非孤立副本)
facts_rel = fe.normalize_macro(
    {'data': {'CPI': {'value': 316.0, 'date': CPI_OBS,
                      'release_date': '2026-10-28'}}}, AS_OF_TS)
fr = next(f for f in facts_rel if f['metric_id'] == 'CPI')
facts_ok = fe.normalize_macro(
    {'data': {'CPI': {'value': 316.0, 'date': CPI_OBS,
                      'release_date': '2026-09-15'}}}, AS_OF_TS)
fo = next(f for f in facts_ok if f['metric_id'] == 'CPI')
facts_no = fe.normalize_macro({'data': {'CPI': {'value': 316.0, 'date': CPI_OBS}}},
                              AS_OF_TS)
fn = next(f for f in facts_no if f['metric_id'] == 'CPI')
check("B8 真实fe入口(normalize_macro): 采集记录release透传到fact——未来发布"
      "→FAIL NOT_AVAILABLE_AT_AS_OF;正常发布→无release问题;缺release→"
      "WARN RELEASE_UNKNOWN",
      fr.get('release_date') == '2026-10-28'
      and fr['quality_status'] == 'FAIL'
      and any('NOT_AVAILABLE_AT_AS_OF' in i['message'] for i in fr['issues'])
      and not any(i['category'] == 'release' for i in fo['issues'])
      and fn.get('release_date') is None
      and any(i['severity'] == 'WARN' and 'RELEASE_UNKNOWN' in i['message']
              for i in fn['issues']),
      f"future={fr['quality_status']} ok={fo['quality_status']} "
      f"none={fn['quality_status']}")

# 场景9: 真实Gate B入口(真实链路+sb透传+仅拒绝性消费)
td9, daily9, snap9 = build_day(mutate_macro=lambda o: o['data']['CPI'].update(
    release_date='2026-10-28'))
fc9 = fact_of(snap9, 'CPI')
anc9 = json.load(open(os.path.join(daily9, f'anchors_{DAY}.json'),
                      encoding='utf-8'))[CPI_KEY]
info9 = dv.metric_registry_info(CPI_KEY, anc9)
spoof_past = dict(anc9)
spoof_past.pop('release_date', None)
spoof_past['release_date'] = '2026-09-02'      # 调用方自填过去发布
check("B9 真实Gate B入口: 未来release经sb真实透传→fact FAIL+Gate A FAIL"
      "(CPI核心)+锚点携带release+dv.is_fresh=False",
      fc9['quality_status'] == 'FAIL'
      and any('NOT_AVAILABLE_AT_AS_OF' in i['message'] for i in fc9['issues'])
      and snap9['gate_a']['status'] == 'FAIL'
      and anc9.get('release_date') == '2026-10-28'
      and dv.is_fresh_anchor(CPI_KEY, anc9, AS_OF) is False,
      f"fact={fc9['quality_status']} gate={snap9['gate_a']['status']} "
      f"rel={anc9.get('release_date')}")
check("B9b Gate B仅拒绝性消费: 调用方自填**过去**release不授予任何额外认证"
      "(fresh结论与合法缺release一致;provenance标注未独立核验)",
      dv.is_fresh_anchor(CPI_KEY, spoof_past, AS_OF)
      == dv.is_fresh_anchor(CPI_KEY, {'value': 316.0, 'obs_date': CPI_OBS},
                            AS_OF) is True
      and '未独立核验' in info9['release_provenance'],
      info9['release_provenance'])

# 场景10: 不伪造发布日期(默认真实链路)
td10, daily10, snap10 = build_day()
fc10 = fact_of(snap10, 'CPI')
anc10 = json.load(open(os.path.join(daily10, f'anchors_{DAY}.json'),
                       encoding='utf-8'))[CPI_KEY]
info10 = dv.metric_registry_info(CPI_KEY, anc10)
check("B10 默认链路不伪造release: fact/锚点均无release_date键(不以obs/"
      "retrieved_at/文件日期冒充)+registry披露RELEASE_UNKNOWN+Gate A照常PASS"
      "(缺release不FAIL既有数据)",
      'release_date' not in fc10 and 'release_date' not in anc10
      and info10['release_provenance'].startswith('RELEASE_UNKNOWN')
      and fp.assess('CPI', fc10['observation_date'], AS_OF)['point_in_time']
      ['status'] == 'RELEASE_UNKNOWN'
      and snap10['gate_a']['status'] == 'PASS',
      f"gate={snap10['gate_a']['status']} "
      f"prov={info10['release_provenance'][:40]}")

# ══ C. §7.6 锚点来源-身份反例 + 正向回环 ═══════════════════════════
print("\n[C] §7.6 锚点跨通道spoof八反例 + 真实sb锚点正向回环")

SPOOF = [
    # (key, info, 期望status, 期望reason子串)
    ('global_market.data.CPI.close', {'value': 316.0, 'obs_date': '2026-10-23',
                                      'metric_id': 'CPI'}, 'UNVERIFIED',
     'SOURCE_MISMATCH'),
    ('macro.data.BTC.value', {'value': 93000.0, 'obs_date': '2026-10-23',
                              'metric_id': 'BTC'}, 'UNVERIFIED', 'SOURCE_MISMATCH'),
    ('macro.data.SPX.value', {'value': 5700.0, 'obs_date': '2026-10-23',
                              'metric_id': 'SPX'}, 'UNVERIFIED', 'SOURCE_MISMATCH'),
    ('unregistered.data.BTC.value', {'value': 1.0, 'obs_date': '2026-10-23'},
     'UNMAPPED', ''),
    ('BTC.value', {'value': 93000.0, 'obs_date': '2026-10-23'}, 'UNMAPPED', ''),
    ('china.southbound.BTC.value', {'value': 1.0, 'obs_date': '2026-10-23'},
     'UNMAPPED', ''),
]
for key, info, st_exp, why in SPOOF:
    ident = fp.verify_anchor_identity(key, info)
    fresh = dv.is_fresh_anchor(key, info, AS_OF)
    warn = dv.stale_anchor_warning(key, info, AS_OF)
    ok = ident['status'] == st_exp and fresh is False and warn is not None
    if why:
        ok = ok and why in (ident.get('reason') or '') + (ident.get('basis') or '')
    check(f"C1 spoof {key!r}: identity={st_exp}"
          f"{'(' + why + ')' if why else ''}+is_fresh=False+警示",
          bool(ok), f"{ident['status']}/{ident.get('reason')}/{fresh}")

# 合法键+冲突metric_id(§7.4: 冲突=UNVERIFIED,不再以canonical授予时效)
ident_cf = fp.verify_anchor_identity(BTC_KEY, {'value': 93000.0,
                                               'obs_date': '2026-10-23',
                                               'metric_id': 'CPI'})
check("C2 合法BTC键+调用方自称metric_id='CPI': 身份冲突→UNVERIFIED"
      "(identity_conflict)+is_fresh=False(不记录冲突后返回FRESH)",
      ident_cf['status'] == 'UNVERIFIED'
      and ident_cf.get('reason') == 'identity_conflict'
      and dv.is_fresh_anchor(BTC_KEY, {'value': 93000.0,
                                       'obs_date': '2026-10-23',
                                       'metric_id': 'CPI'}, AS_OF) is False,
      f"{ident_cf['status']}/{ident_cf.get('reason')}")

# 未认证调用方自报metric_id不得授信(未注册键+自称BTC)
ident_self = fp.verify_anchor_identity('unregistered.data.BTC.value',
                                       {'value': 1.0, 'obs_date': '2026-10-23',
                                        'metric_id': 'BTC'})
ident_self2 = fp.verify_anchor_identity('global_market.data.CPI.close',
                                        {'value': 316.0, 'obs_date': '2026-10-23',
                                         'metric_id': 'CPI'})
check("C3 自报metric_id不授信: 未注册键自称BTC仍UNMAPPED;跨通道键自称一致"
      "CPI仍UNVERIFIED(SOURCE_MISMATCH)——注册表权威来源优先于调用方声明",
      ident_self['status'] != 'MAPPED'
      and ident_self2['status'] == 'UNVERIFIED'
      and 'SOURCE_MISMATCH' in ((ident_self2.get('reason') or '')
                                + (ident_self2.get('basis') or '')),
      f"{ident_self['status']}/{ident_self2['status']}"
      f"/{ident_self2.get('reason')}/{ident_self2.get('basis')}")

# 真实sb锚点正向回环: 合法构建0个UNVERIFIED;兼容键全部MAPPED
anchors_c = json.load(open(os.path.join(daily10, f'anchors_{DAY}.json'),
                           encoding='utf-8'))
statuses = {k: fp.verify_anchor_identity(k, v)['status']
            for k, v in anchors_c.items()}
unver = [k for k, s in statuses.items() if s == 'UNVERIFIED']
unmapped_nonlegacy = [k for k, s in statuses.items()
                      if s == 'UNMAPPED' and not k.endswith('.week_chg')]
COMPAT = ['china.southbound.net_buy', 'rate_economy.current_rates.DFF.value',
          'macro.derived.REAL_10Y', 'rate_economy.real_economy.UNRATE.value',
          CPI_KEY, 'rate_economy.fed_funds_futures.0.price', BTC_KEY]
check("C4 真实sb锚点回环: 合法构建{0}UNVERIFIED;UNMAPPED仅限.week_chg诊断"
      "兄弟键;兼容键(southbound/DFF旧名/REAL_10Y派生/UNRATE旧名/CPI/期货"
      "曲线/BTC)全部MAPPED",
      not unver and not unmapped_nonlegacy
      and all(statuses.get(k) == 'MAPPED' for k in COMPAT),
      f"unverified={unver[:3]} unmapped={unmapped_nonlegacy[:3]} "
      f"compat={[statuses.get(k) for k in COMPAT]}")
fresh_daily = all(dv.is_fresh_anchor(k, anchors_c[k], AS_OF) for k in
                  [BTC_KEY, 'rate_economy.current_rates.DFF.value',
                   'china.southbound.net_buy', 'macro.derived.REAL_10Y'])
check("C5 正向兼容: 真实锚点(不带自报metric_id)is_fresh照常True(整改不"
      "破坏合法路径)", fresh_daily)
sc_ok = dv.is_fresh_anchor('scorecard.体制评分', {'obs_date': '2026-10-23'},
                           AS_OF)
sc_old = dv.is_fresh_anchor('scorecard.体制评分', {'obs_date': '2026-10-01'},
                            AS_OF)
check("C6 scorecard保持诊断专用口径(10日窗: 新=True旧=False,不参与注册表"
      "身份)", sc_ok is True and sc_old is False, f"{sc_ok}/{sc_old}")

# ══ D. §十 联合E2E ═════════════════════════════════════════════════
print("\n[D] §十 联合E2E: 正常对照/受控失败/已发布保护/真实锚点spoof/日期异常")

# D1(10.1) 正常研究对照: 真实链路PASS+合法DEGRADED,非全mock
D1ROOT = tempfile.mkdtemp(prefix='w2fix1-D1-', dir=_TMPD)
snap_d1, _snap_path_d1, out_d1 = fixt.build_full_day(D1ROOT, DAY)
pack_d1 = os.path.join(D1ROOT, 'data', 'weekly', f'data_pack_{DAY}.md')
meta_d1 = json.load(open(rp.meta_path_for(pack_d1), encoding='utf-8'))
check("D1 正常对照: 真实build_full_day Gate A=PASS+数据包落盘+meta绑定"
      "snapshot", snap_d1['gate_a']['status'] == 'PASS'
      and os.path.exists(pack_d1) and meta_d1.get('source') == 'snapshot'
      and meta_d1.get('pack_digest'),
      snap_d1['gate_a']['status'])
DAY2 = '20261023'
fixt.build_full_day(D1ROOT, DAY2, gate='DEGRADED')
snap_d1b = json.load(open(os.path.join(D1ROOT, 'data', 'daily',
                                       f'research_snapshot_{DAY2}.json'),
                          encoding='utf-8'))
check("D1b 合法DEGRADED对照: UMCSENT真实降级→Gate A=DEGRADED(披露非阻断)"
      "+当日数据包照常产出",
      snap_d1b['gate_a']['status'] == 'DEGRADED'
      and os.path.exists(os.path.join(D1ROOT, 'data', 'weekly',
                                      f'data_pack_{DAY2}.md')),
      snap_d1b['gate_a']['status'])
buf_d1 = io.StringIO()
with mock.patch.object(da, 'DATA_DIR', os.path.join(D1ROOT, 'data')), \
        mock.patch.object(da, 'datetime', _DT(DAY)), \
        contextlib.redirect_stdout(buf_d1):
    try:
        da.main()
        rc_d1 = 0
    except SystemExit as e:
        rc_d1 = e.code
check("D1c 真实data_assembler.main(时钟=DAY): exit 0正常产出(整改不阻断"
      "合法正式链路)", rc_d1 == 0, f"rc={rc_d1}")

# D2(10.2) 未来发布CPI真实链路: 受控失败,质量门逐层拦截,GLM零调用
D2ROOT = tempfile.mkdtemp(prefix='w2fix1-D2-', dir=_TMPD)
td2, daily2, snap2_d = build_day(root=D2ROOT, mutate_macro=lambda o:
                                 o['data']['CPI'].update(release_date='2026-10-28'))
fc2 = fact_of(snap2_d, 'CPI')
buf_d2 = io.StringIO()
with mock.patch.object(da, 'DATA_DIR', os.path.join(D2ROOT, 'data')), \
        mock.patch.object(da, 'datetime', _DT(DAY)), \
        contextlib.redirect_stdout(buf_d2):
    try:
        da.main()
        rc_d2 = 0
    except SystemExit as e:
        rc_d2 = e.code
OUT2 = os.path.join(tempfile.mkdtemp(prefix='w2fix1-D2out-', dir=_TMPD),
                    'weekly')
os.makedirs(OUT2, exist_ok=True)
glm_d2 = _GLM()
applied_d2 = []
rc_d2b = rg_run(rg_harness(glm_d2, applied_d2, os.path.join(D2ROOT, 'data'),
                           OUT2, DAY))
anc2 = json.load(open(os.path.join(daily2, f'anchors_{DAY}.json'),
                      encoding='utf-8'))[CPI_KEY]
ver_d2, rej_d2 = ae.verify_evidence_items(
    [{'metric': CPI_KEY, 'value': 316.0, 'obs_date': CPI_OBS, 'mechanism': '通胀'}],
    {CPI_KEY: anc2}, AS_OF)
check("D2 未来发布CPI真实链路: 快照Gate A=FAIL(CPI核心)+fact FAIL"
      " NOT_AVAILABLE_AT_AS_OF+真实锚点透传release",
      snap2_d['gate_a']['status'] == 'FAIL'
      and fc2['quality_status'] == 'FAIL'
      and any('NOT_AVAILABLE_AT_AS_OF' in i['message'] for i in fc2['issues'])
      and anc2.get('release_date') == '2026-10-28',
      f"gate={snap2_d['gate_a']['status']} q={fc2['quality_status']}")
check("D2b 数据包层: 真实data_assembler拒绝(exit2无包);周报入口: 真实"
      "generate_weekly_report预检拒(exit2)+GLM零调用+零长期状态回写;"
      "证据层: 未来发布事实不得作当前证据(ae拒)",
      rc_d2 == 2 and not os.path.exists(os.path.join(
          D2ROOT, 'data', 'weekly', f'data_pack_{DAY}.md'))
      and rc_d2b == 2 and glm_d2.calls == 0 and applied_d2 == []
      and ver_d2 == [] and rej_d2,
      f"da={rc_d2} rg={rc_d2b} glm={glm_d2.calls} ae={len(rej_d2)}")

# D3(10.3) 已发布正式报告保护: 四对象执行前基线
D3ROOT = tempfile.mkdtemp(prefix='w2fix1-D3-', dir=_TMPD)
OUTE = os.path.join(D3ROOT, 'output', 'weekly')
CFGE = os.path.join(D3ROOT, 'config')
os.makedirs(OUTE, exist_ok=True)
os.makedirs(CFGE, exist_ok=True)
THE = os.path.join(CFGE, 'thesis.json')
VWE = os.path.join(CFGE, 'allocation_views.json')
open(THE, 'w', encoding='utf-8').write(
    '{"version": 1, "theses": [], "updated_at": "2026-10-24T08:00:00"}')
open(VWE, 'w', encoding='utf-8').write(
    '{"version": 2, "views": [], "predictions": []}')
fixt.build_full_day(D3ROOT, DAY)
glm_pub = _GLM()
applied_pub = []
rc_pub = rg_run(rg_harness(glm_pub, applied_pub, os.path.join(D3ROOT, 'data'),
                           OUTE, DAY))
REPE = os.path.join(OUTE, f'weekly_report_{DAY}.md')
STATE = os.path.join(OUTE, f'report_status_{DAY}.json')
check("D3 前置: 真实发布事务成功(exit0+GLM恰1次+报告/状态落盘)"
      "——否则保护断言无意义", rc_pub == 0 and os.path.exists(REPE)
      and os.path.exists(STATE) and glm_pub.calls == 1,
      f"rc={rc_pub} glm={glm_pub.calls}")
view_pub, reason_pub = rp.formal_report_view(REPE)
check("D3b 前置: formal_report_view接受真实发布报告",
      view_pub is not None, reason_pub)
scan_pub = rp.scan_formal_weekly_reports(OUTE)

# 执行前基线(一切危险操作之前): 报告/发布状态/thesis/views四对象
base_d3 = {p: sha(p) for p in (REPE, STATE, THE, VWE)}

# 危险操作: 根内真实采集日EATK携带未来发布CPI(数据级攻击,非外链)
EATK = '20261025'
daily_e = os.path.join(D3ROOT, 'data', 'daily')
fixt.write_collectors(daily_e, EATK)
_p = os.path.join(daily_e, f'macro_{EATK}.json')
_o = json.load(open(_p, encoding='utf-8'))
_o['data']['CPI']['release_date'] = '2026-11-01'    # 晚于as_of 2026-10-25
json.dump(_o, open(_p, 'w', encoding='utf-8'), ensure_ascii=False)
quiet(sb.build_snapshot, EATK, daily_e, daily_e, trusted_root=D3ROOT,
      as_of=fixt.as_of_for(EATK))
snap_e = json.load(open(os.path.join(daily_e, f'research_snapshot_{EATK}.json'),
                        encoding='utf-8'))
glm_e = _GLM()
applied_e = []
rc_e = rg_run(rg_harness(glm_e, applied_e, os.path.join(D3ROOT, 'data'),
                         OUTE, EATK))
after_d3 = {p: sha(p) for p in (REPE, STATE, THE, VWE)}
view_after, reason_after = rp.formal_report_view(REPE)
_new_d3 = sorted(f for f in os.listdir(OUTE)
                 if (f.startswith('weekly_report_')
                     or f.startswith('report_status_')) and DAY not in f)
_pub_true_d3 = sorted(
    f for f in os.listdir(OUTE) if f.startswith('report_status_')
    and json.load(open(os.path.join(OUTE, f))).get('published') is True)
check("D3c 危险日Gate A=FAIL(受控失败)+周报入口拒(exit2+GLM=0)",
      snap_e['gate_a']['status'] == 'FAIL' and rc_e == 2 and glm_e.calls == 0,
      f"gate={snap_e['gate_a']['status']} rc={rc_e} glm={glm_e.calls}")
check("D3d 保护核验(执行前基线vs执行后): 报告/发布状态/thesis/views四对象"
      "SHA-256不变+发布身份仍有效+无新报告/状态+published=true仅发布日+"
      "无长期状态回写+scan不变",
      base_d3 == after_d3 and view_after is not None and not _new_d3
      and _pub_true_d3 == [f'report_status_{DAY}.json'] and applied_e == []
      and [v['ymd'] for v in rp.scan_formal_weekly_reports(OUTE)]
      == [v['ymd'] for v in scan_pub],
      str({'changed': [k for k in base_d3 if base_d3[k] != after_d3[k]],
           'new': _new_d3, 'pub': _pub_true_d3, 'formal': reason_after}))
with tempfile.TemporaryDirectory(prefix='w2fix1-D3e-') as _td5:
    _f1 = os.path.join(_td5, 'a.json')
    open(_f1, 'w').write('{"a":1}')
    _b = {_f1: sha(_f1)}
    open(_f1, 'w').write('{"a":2}')
    check("D3e 自检: 基线比较机制能发现被篡改对象(方法有效性)",
          sha(_f1) != _b[_f1])

# D4(10.4) 真实锚点文件spoof: P0-1权威重建/批次核验不可绕过
apath_d4 = os.path.join(daily10, f'anchors_{DAY}.json')
orig_d4 = open(apath_d4, encoding='utf-8').read()
ok_orig, _r0 = rp.verify_anchor_batch(apath_d4, anchors_date=DAY,
                                      daily_dir=daily10, trusted_root=td10)
try:
    tam1 = json.loads(orig_d4)
    tam1['global_market.data.CPI.close'] = {'value': 316.0, 'obs_date': '2026-10-23',
                                            'metric_id': 'CPI', 'quality': 'PASS'}
    json.dump(tam1, open(apath_d4, 'w', encoding='utf-8'), ensure_ascii=False)
    ok1, r1 = rp.verify_anchor_batch(apath_d4, anchors_date=DAY,
                                     daily_dir=daily10, trusted_root=td10)
    tam2 = json.loads(orig_d4)
    tam2[BTC_KEY]['metric_id'] = 'CPI'          # 合法键+冲突自报身份
    json.dump(tam2, open(apath_d4, 'w', encoding='utf-8'), ensure_ascii=False)
    ok2, r2 = rp.verify_anchor_batch(apath_d4, anchors_date=DAY,
                                     daily_dir=daily10, trusted_root=td10)
    tam3 = json.loads(orig_d4)
    tam3['macro.data.SPX.value'] = tam3.pop('global_market.data.SPX.close')
    json.dump(tam3, open(apath_d4, 'w', encoding='utf-8'), ensure_ascii=False)
    ok3, r3 = rp.verify_anchor_batch(apath_d4, anchors_date=DAY,
                                     daily_dir=daily10, trusted_root=td10)
finally:
    open(apath_d4, 'w', encoding='utf-8').write(orig_d4)
ok4, r4 = rp.verify_anchor_batch(apath_d4, anchors_date=DAY,
                                 daily_dir=daily10, trusted_root=td10)
check("D4 真实锚点批次核验spoof: 合法批次通过;注入global_market.data.CPI."
      "close/篡改metric_id/键改家族(冒充macro行情)→权威重建比对全拒;"
      "恢复后重过(检测非损坏)",
      ok_orig is True and ok1 is False and ok2 is False and ok3 is False
      and ok4 is True,
      f"orig={ok_orig} add={ok1}({str(r1)[:30]}) id={ok2} key={ok3} "
      f"restore={ok4}")

# D5(10.5) 真实dv/dpo正式消费入口上的日期异常
info_badobs = dv.metric_registry_info(BTC_KEY, {'value': 1,
                                                'obs_date': '2026-10-23INVALID'})
check("D5 真实Gate B披露口径: 非法obs在metric_registry_info如实为None"
      "(不截断洗白;dv经fp.parse_instant与fe.parse_iso_date同判非法)",
      info_badobs['observation_date'] is None
      and fe.parse_iso_date('2026-10-23INVALID') is None
      and fp.parse_instant('2026-10-23INVALID') is None,
      info_badobs['observation_date'])
info_badrel = dv.metric_registry_info(BTC_KEY, {'value': 1,
                                                'obs_date': '2026-10-23',
                                                'release_date': '2026-13-99'})
check("D5b metric_registry_info: 非法release如实披露(None+note点名原始值,"
      "不得转合法日期)", info_badrel['release_date'] is None
      and '非法' in info_badrel.get('note', '')
      and '2026-13-99' in info_badrel.get('note', ''),
      info_badrel.get('note'))
prob_bad = dpo._metric_problem(BTC_KEY, {BTC_KEY: {
    'value': 93000.0, 'obs_date': '2026-10-23INVALID', 'quality': 'PASS'}},
    AS_OF)
prob_fut = dpo._metric_problem(BTC_KEY, {BTC_KEY: {
    'value': 93000.0, 'obs_date': '2026-10-25', 'quality': 'PASS'}}, AS_OF)
prob_today = dpo._metric_problem(BTC_KEY, {BTC_KEY: {
    'value': 93000.0, 'obs_date': '2026-10-23', 'quality': 'PASS'}},
    '2026-10-24INVALID')
check("D5c 真实dpo观察入口(正式长期观察消费路径): obs非法→不可解析不记录;"
      "未来obs→不记录;研究截止非法→不记录(非法日期洗白不得进入观察历史)",
      prob_bad and '不可解析' in prob_bad
      and prob_fut and '未来' in prob_fut
      and prob_today and '非法' in prob_today,
      f"bad={str(prob_bad)[:40]} fut={str(prob_fut)[:30]} "
      f"today={str(prob_today)[:40]}")

shutil.rmtree(_TMPD, ignore_errors=True)
print("\n" + "═" * 72)
print(f"W2-FIX1 结果: {PASS_N}通过 / {FAIL_N}失败")
if FAIL_N:
    sys.exit(1)
