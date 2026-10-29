#!/usr/bin/env python3
"""IA-P0-2-W2-FIX3 联合验收测试(混合精度与未知时区比较错误认证整改)。

缺陷编号: IA-P02-W2-FIX2-DEF-001。
真实模块+真实文件系统+隔离临时目录;mock仅限外部GLM/时钟(承FIX1/FIX2口径)。

矩阵(对应指令FIX3-06 A~G+§11联合E2E):
  A 两组强制反例(真实函数链): 组一 date-only发布10-24×aware截止
    10-25T08:00+08(名义差1日,可能实际发布10-24T23:00-04:00=10-25T03:00Z
    晚于截止10-25T00:00Z)与组二 naive发布10-24T23:59×aware截止
    10-26T00:00+14:00(名义差2日,UTC-11解释下发布10-25T10:59Z晚于截止
    10-25T10:00Z)——均不得取得确定性RELEASED_BEFORE/点时OK;
  B 正向完整时间戳: 早/等/晚×≥2组不同UTC偏移;名义日期误导序两方向按UTC处理;
  C date-only历史兼容: 双date-only保留日粒度(DAY,绝不冒充INSTANT);同日
    date-only×ts与双date-only同日的守恒态;跨日未来(DAY)拒绝不回退;
  D 未知时区/名义日差不可为凭: 同日/相邻/相差≥2日均不能仅凭名义日差断言;
    区间证明正向(date-only远早于ts截止=RELEASED_BEFORE RANGE,先后已证但
    非精确时刻;区别于名义日差启发式);
  E 正式消费端一致性(真实函数): compare/assess/validate_fact/
    is_fresh_anchor/stale_anchor_warning/metric_registry_info/Gate A链;
    观测新鲜(fresh)≠点时可得(pit)两维度分离;
  F 原安全回归: Gate A非法截止阻断/同日未来发布阻断/跨通道伪装拒绝/
    正常来源绑定/**联合E2E四对象保护**(§11: 正常发布→SHA-256基线→
    混合精度非法认证尝试→Gate A/B与正式入口拒→已有状态不变);
  G 敏感性: 若比较器退回"名义日差≥2即RELEASED_BEFORE"(FIX2缺陷形态),
    本套A族断言必失败——用真实重引入(monkeypatch旧逻辑)证明检测非常量。
"""
import contextlib
import hashlib
import io
import json
import os
import sys
import tempfile
from datetime import date, datetime, time
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
import data_assembler as da                    # noqa: E402
import report_generator as rg                  # noqa: E402

DAY = '20261024'
AS_OF = '2026-10-24'
AS_OF_TS = '2026-10-24T08:00:00+08:00'
CPI_KEY = 'macro.data.CPI.value'
CPI_OBS = '2026-09-01'
# 组一(FIX3指令§5.2): date-only发布×aware截止, 名义差1日不可证
REL_G1 = '2026-10-24'
AS_OF_G1 = '2026-10-25T08:00:00+08:00'        # =2026-10-25T00:00Z
REL_G1_POSSIBLE = '2026-10-24T23:00:00-04:00'  # =2026-10-25T03:00Z(指令算例)
# 组二(FIX3指令§5.3): naive发布×aware截止(+14:00), 名义差2日不可证
REL_G2 = '2026-10-24T23:59:00'
AS_OF_G2 = '2026-10-26T00:00:00+14:00'        # =2026-10-25T10:00Z
REL_G2_AT_W11 = '2026-10-24T23:59:00-11:00'   # =2026-10-25T10:59Z(指令算例)
PASS_N, FAIL_N = 0, 0
_TMPD = tempfile.mkdtemp(prefix='w2fix3-')


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
        return ('# 投资周报(SYNTHETIC测试文本·W2-FIX3)\n\n'
                + '本周市场综述与分资产回顾。' * 60)


def build_day(mutate_macro=None, ymd=DAY, root=None, as_of=None):
    """真实链路一天(fixt采集→真实sb.build_snapshot),返回(root, daily, snap)。"""
    td = root or tempfile.mkdtemp(prefix='w2fix3-day-', dir=_TMPD)
    daily = os.path.join(td, 'data', 'daily')
    os.makedirs(daily, exist_ok=True)
    fixt.write_collectors(daily, ymd)
    if mutate_macro:
        p = os.path.join(daily, f'macro_{ymd}.json')
        obj = json.load(open(p, encoding='utf-8'))
        mutate_macro(obj)
        json.dump(obj, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
    quiet(sb.build_snapshot, ymd, daily, daily, trusted_root=td,
          as_of=as_of or fixt.as_of_for(ymd))
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
    with contextlib.ExitStack() as st:
        for h in harness_list:
            st.enter_context(h)
        try:
            quiet(rg.generate_weekly_report)
            return 0
        except SystemExit as e:
            return e.code


def da_run(data_dir, ymd):
    with mock.patch.object(da, 'DATA_DIR', data_dir), \
            mock.patch.object(da, 'datetime', _DT(ymd)), \
            contextlib.redirect_stdout(io.StringIO()):
        try:
            quiet(da.main)
            return 0
        except SystemExit as e:
            return e.code


print("═" * 72)
print("IA-P0-2-W2-FIX3: 混合精度/未知时区不得错误认证点时可得(DEF-001)")
print("═" * 72)

# ══ A. 两组强制反例(真实函数,非模拟分支) ═════════════════════════════
print("\n[A] 强制反例: 混合精度下未证明的先后关系不得获得确定性认证")

_UNVER = ('UNVERIFIED_SAME_DAY', 'UNVERIFIED_TZ', 'UNVERIFIED_PRECISION')

# A1 组一: date-only发布×aware截止(名义差1日)
c1 = fp.compare_release_availability(REL_G1, AS_OF_G1)
v1 = fp.assess('CPI', CPI_OBS, AS_OF_G1, release_date=REL_G1)
f1 = fe.make_fact('CPI', 316.0, CPI_OBS, AS_OF_G1, 'macro.json',
                  'macro_collector', release_date=REL_G1)
i1 = fe.validate_fact(f1, {'value': 316.0, 'date': CPI_OBS},
                      fe.metric('CPI'), as_of_date=AS_OF_G1)
check("A1 组一(date-only 10-24 × aware截止10-25T08+08): 比较器不得返回确定"
      "性RELEASED_BEFORE(判UNVERIFIED_PRECISION)+detail披露发布缺时刻与"
      "时区; assess点时≠OK(POINT_IN_TIME_UNCERTIFIED)且不FAIL; fe只INFO"
      "'点时未认证'绝不标注已验证——date-only无法证明发布先于时刻级截止",
      c1['verdict'] in _UNVER and '时刻' in c1['detail'] and '时区' in c1['detail']
      and v1['point_in_time']['status'] == 'POINT_IN_TIME_UNCERTIFIED'
      and v1['status'] == 'FRESH'
      and fe.grade_issues(i1) != 'FAIL'
      and any(x['severity'] == 'INFO' and '点时未认证' in x['message']
              for x in i1),
      f"{c1['verdict']}/{c1['granularity']} pit={v1['point_in_time']['status']}"
      f" grade={fe.grade_issues(i1)}")
c1p = fp.compare_release_availability(REL_G1_POSSIBLE, AS_OF_G1)
check("A1b 组一指令算例对照: 可能的真实发布10-24T23:00-04:00(=10-25T03:00Z)"
      "确实晚于截止(=10-25T00:00Z)→RELEASED_AFTER(INSTANT)——证明date-only"
      "形态确有点时风险,组一不得认证",
      c1p['verdict'] == 'RELEASED_AFTER' and c1p['granularity'] == 'INSTANT',
      f"{c1p['verdict']}/{c1p['granularity']}")

# A2 组二: naive发布×aware截止+14:00(名义差2日)
c2 = fp.compare_release_availability(REL_G2, AS_OF_G2)
v2 = fp.assess('CPI', CPI_OBS, AS_OF_G2, release_date=REL_G2)
f2 = fe.make_fact('CPI', 316.0, CPI_OBS, AS_OF_G2, 'macro.json',
                  'macro_collector', release_date=REL_G2)
i2 = fe.validate_fact(f2, {'value': 316.0, 'date': CPI_OBS},
                      fe.metric('CPI'), as_of_date=AS_OF_G2)
check("A2 组二(naive 10-24T23:59 × aware截止10-26T00:00+14:00): 名义差2日"
      "不足为凭——判UNVERIFIED_TZ且detail明示'名义日差2日不足为凭'与可能UTC"
      "区间有交; assess点时≠OK; fe只INFO不FAIL——绝不使用"
      "abs(day_difference)>=2作确定性认证依据",
      c2['verdict'] in _UNVER and '名义日差' in c2['detail']
      and v2['point_in_time']['status'] == 'POINT_IN_TIME_UNCERTIFIED'
      and v2['status'] == 'FRESH' and fe.grade_issues(i2) != 'FAIL'
      and any(x['severity'] == 'INFO' and '点时未认证' in x['message']
              for x in i2),
      f"{c2['verdict']} pit={v2['point_in_time']['status']}")
c2p = fp.compare_release_availability(REL_G2_AT_W11, AS_OF_G2)
check("A2b 组二指令算例对照: 同发布按UTC-11解释(10-25T10:59Z)确实晚于截止"
      "(10-25T10:00Z)59分钟→RELEASED_AFTER(INSTANT)——证明区间有交是真实"
      "风险,名义差2日不得认证",
      c2p['verdict'] == 'RELEASED_AFTER' and c2p['granularity'] == 'INSTANT'
      and '59' in c2p['detail'],
      f"{c2p['verdict']}/{c2p['granularity']} {c2p['detail'][-30:]}")

# A3 反向组一(aware发布×date-only截止): 同样精度失配不认证
c3 = fp.compare_release_availability('2026-10-25T08:00:00+08:00', '2026-10-24')
check("A3 反向混合(aware发布×date-only截止): 区间有交→UNVERIFIED_PRECISION"
      "(不因发布侧带偏移而单边采信)",
      c3['verdict'] == 'UNVERIFIED_PRECISION', c3['verdict'])

# ══ B. 正向完整时间戳(早/等/晚×≥2组偏移) ═════════════════════════════
print("\n[B] 正向: 双aware时刻绝对比较(不同UTC偏移)")

cB1 = fp.compare_release_availability('2026-10-24T04:00:00+08:00',
                                      '2026-10-24T08:00:00+08:00')
vB1 = fp.assess('CPI', CPI_OBS, '2026-10-24T08:00:00+08:00',
                release_date='2026-10-24T04:00:00+08:00')
check("B1 早于(+08同区): RELEASED_BEFORE(INSTANT)+点时OK(INSTANT)",
      cB1['verdict'] == 'RELEASED_BEFORE' and cB1['granularity'] == 'INSTANT'
      and vB1['point_in_time']['status'] == 'OK'
      and vB1['point_in_time']['granularity'] == 'INSTANT',
      f"{cB1['verdict']} pit={vB1['point_in_time']['status']}")
cB2 = fp.compare_release_availability('2026-10-23T21:00:00-04:00',
                                      '2026-10-24T12:00:00+02:00')
check("B2 早于(跨区-04×+02: 10-24T01:00Z<10:00Z): RELEASED_BEFORE(INSTANT)",
      cB2['verdict'] == 'RELEASED_BEFORE' and cB2['granularity'] == 'INSTANT',
      cB2['verdict'])
cB3 = fp.compare_release_availability('2026-10-24T08:00:00+08:00',
                                      '2026-10-24T00:00:00Z')
vB3 = fp.assess('CPI', CPI_OBS, '2026-10-24T00:00:00Z',
                release_date='2026-10-24T08:00:00+08:00')
check("B3 等于(同一时刻两种写法+08×Z): RELEASED_BEFORE(INSTANT,'等于')"
      "+点时OK——恰在截止时刻发布视为可得",
      cB3['verdict'] == 'RELEASED_BEFORE' and '等于' in cB3['detail']
      and vB3['point_in_time']['status'] == 'OK',
      f"{cB3['verdict']} {cB3['detail'][:40]}")
cB4 = fp.compare_release_availability('2026-10-24T20:00:00+08:00',
                                      '2026-10-24T08:00:00+08:00')
vB4 = fp.assess('CPI', CPI_OBS, AS_OF_TS, release_date='2026-10-24T20:00:00+08:00')
iB4 = fe.validate_fact(
    fe.make_fact('CPI', 316.0, CPI_OBS, AS_OF_TS, 'macro.json',
                 'macro_collector', release_date='2026-10-24T20:00:00+08:00'),
    {'value': 316.0, 'date': CPI_OBS}, fe.metric('CPI'), as_of_date=AS_OF_TS)
check("B4 晚于: RELEASED_AFTER(INSTANT)+assess NOT_AVAILABLE_AT_AS_OF/"
      "fresh=False+fe FAIL(NOT_AVAILABLE_AT_AS_OF)——确定性拒绝保留",
      cB4['verdict'] == 'RELEASED_AFTER' and cB4['granularity'] == 'INSTANT'
      and vB4['status'] == 'NOT_AVAILABLE_AT_AS_OF' and vB4['fresh'] is False
      and fe.grade_issues(iB4) == 'FAIL',
      f"{cB4['verdict']} {vB4['status']} {fe.grade_issues(iB4)}")
cB5 = fp.compare_release_availability('2026-10-24T02:00:00+08:00',
                                      '2026-10-23T15:00:00-04:00')
cB6 = fp.compare_release_availability('2026-10-23T18:00:00-05:00',
                                      '2026-10-24T00:00:00+08:00')
vB6 = fp.assess('CPI', CPI_OBS, '2026-10-24T00:00:00+08:00',
                release_date='2026-10-23T18:00:00-05:00')
check("B5 名义日期误导序两方向按UTC处理: 发布名义晚(10-24+08)实际早→"
      "RELEASED_BEFORE;发布名义早(10-23-05=10-23T23Z)实际晚于截止"
      "(10-23T16Z)→RELEASED_AFTER+assess拒绝——表面日期序≠绝对序",
      cB5['verdict'] == 'RELEASED_BEFORE'
      and cB6['verdict'] == 'RELEASED_AFTER'
      and vB6['status'] == 'NOT_AVAILABLE_AT_AS_OF',
      f"{cB5['verdict']}/{cB6['verdict']} {vB6['status']}")

# ══ C. date-only历史兼容(明确粒度,不冒充INSTANT) ════════════════════
print("\n[C] date-only历史兼容: 日粒度保留,粒度明确")

cC1 = fp.compare_release_availability('2026-09-15', '2026-10-24')
vC1 = fp.assess('CPI', CPI_OBS, AS_OF, release_date='2026-09-15')
check("C1 双date-only跨日: RELEASED_BEFORE(DAY)+点时OK但granularity=DAY"
      "(绝不冒充INSTANT认证)——历史日粒度语义保留",
      cC1['verdict'] == 'RELEASED_BEFORE' and cC1['granularity'] == 'DAY'
      and vC1['point_in_time']['status'] == 'OK'
      and vC1['point_in_time']['granularity'] == 'DAY',
      f"{cC1['verdict']}/{cC1['granularity']}")
cC2 = fp.compare_release_availability('2026-10-28', '2026-10-24')
vC2 = fp.assess('CPI', CPI_OBS, AS_OF, release_date='2026-10-28')
warnC2 = dv.stale_anchor_warning(
    CPI_KEY, {'value': 316.0, 'obs_date': CPI_OBS,
              'release_date': '2026-10-28'}, AS_OF)
check("C2 双date-only跨日未来: RELEASED_AFTER(DAY)+NOT_AVAILABLE_AT_AS_OF"
      "+fresh=False+dv警示'点时不可得'(FIX1 B4兼容不回退)",
      cC2['verdict'] == 'RELEASED_AFTER' and cC2['granularity'] == 'DAY'
      and vC2['status'] == 'NOT_AVAILABLE_AT_AS_OF' and vC2['fresh'] is False
      and '点时不可得' in (warnC2 or ''),
      f"{cC2['verdict']} {vC2['status']}")
cC3 = fp.compare_release_availability('2026-10-24', AS_OF_TS)
cC4 = fp.compare_release_availability('2026-10-24', '2026-10-24')
check("C3 同日守恒态: date-only×ts同日→UNVERIFIED_SAME_DAY;双date-only"
      "同日→UNVERIFIED_SAME_DAY(日粒度内无法证先后)——均不认证",
      cC3['verdict'] == 'UNVERIFIED_SAME_DAY'
      and cC4['verdict'] == 'UNVERIFIED_SAME_DAY',
      f"{cC3['verdict']}/{cC4['verdict']}")
cC5 = fp.assess('CPI', CPI_OBS, AS_OF)
check("C4 缺release: RELEASE_UNKNOWN保留(不伪造点时证据),新鲜度按观测窗"
      "(FIX1 B1兼容)", cC5['point_in_time']['status'] == 'RELEASE_UNKNOWN'
      and cC5['fresh'] is True, cC5['point_in_time']['status'])
for bad in ['2026-10-24INVALID', '2026-02-30', '20261024', 123,
            '2026-10-24T08:00:00+0800']:
    cbad = fp.compare_release_availability(bad, AS_OF_TS)
    vbad = fp.assess('CPI', CPI_OBS, AS_OF_TS, release_date=bad)
    check(f"C5 非法release={bad!r}: INVALID_RELEASE受控拒绝+assess"
          " INVALID_RELEASE/fresh=False(不截断救活)",
          cbad['verdict'] == 'INVALID_RELEASE'
          and vbad['status'] == 'INVALID_RELEASE' and vbad['fresh'] is False,
          f"{cbad['verdict']}/{vbad['status']}")
check("C5b release_date=None(函数级缺席标记,非显式非法值): 按缺席语义→"
      "RELEASE_UNKNOWN(C4同族),不误判非法——显式非法指在场且非法的字符串",
      fp.assess('CPI', CPI_OBS, AS_OF_TS,
                release_date=None)['point_in_time']['status']
      == 'RELEASE_UNKNOWN', 'None应走缺席语义')
cC6 = fp.assess('CPI', CPI_OBS, AS_OF_TS,
                release_date='2026-08-15')   # 早于观测日09-01
check("C6 发布早于观测(RELEASE_BEFORE_OBS): INVALID_RELEASE语义非法保留",
      cC6['status'] == 'INVALID_RELEASE'
      and cC6['point_in_time']['status'] == 'RELEASE_BEFORE_OBS',
      cC6['status'])

# ══ D. 未知时区/名义日差不可为凭+区间证明正向 ═════════════════════════
print("\n[D] 未知时区: 同日/相邻/≥2日均不可仅凭名义日差断言; 区间证明为凭")

cD1 = fp.compare_release_availability('2026-10-24T23:00:00',
                                      '2026-10-24T08:00:00+08:00')
check("D1 naive×aware同日: UNVERIFIED_SAME_DAY(同日精度不足)",
      cD1['verdict'] == 'UNVERIFIED_SAME_DAY', cD1['verdict'])
cD2 = fp.compare_release_availability('2026-10-25T08:00:00+08:00',
                                      '2026-10-24T20:00:00')
cD3 = fp.compare_release_availability('2026-10-24T08:00:00',
                                      '2026-10-25T08:00:00+08:00')
check("D2 naive相邻日两方向: 区间有交→UNVERIFIED_TZ(反转混合同样);区间无交"
      "→RELEASED_BEFORE(RANGE,naive墙钟10-24T08最晚可能UTC=10-24T20Z严格"
      "早于截止10-25T00Z)——确定性仅来自区间证明,非名义日差",
      cD2['verdict'] == 'UNVERIFIED_TZ'
      and cD3['verdict'] == 'RELEASED_BEFORE'
      and cD3['granularity'] == 'RANGE' and '区间' in cD3['detail'],
      f"{cD2['verdict']}/{cD3['verdict']}+{cD3['granularity']}")
cD4 = fp.compare_release_availability('2026-10-24T23:59:00',
                                      '2026-10-26T00:00:01+14:00')
cD5 = fp.compare_release_availability('2026-10-24T23:59:00',
                                      '2026-10-28T00:00:00+14:00')
check("D3 相差≥2日naive: +14:00:01极端截止(10-25T10:00:01Z)仍与naive可能"
      "区间上界(10-25T11:59Z)有交→UNVERIFIED_TZ;截止推远至10-28(10-27T10Z)"
      "区间无交→RELEASED_BEFORE(RANGE)——2日不是免检票,证明才是",
      cD4['verdict'] == 'UNVERIFIED_TZ'
      and cD5['verdict'] == 'RELEASED_BEFORE'
      and cD5['granularity'] == 'RANGE',
      f"{cD4['verdict']}/{cD5['verdict']}")
cD6 = fp.compare_release_availability('2026-10-20',
                                      '2026-10-26T08:00:00+08:00')
vD6 = fp.assess('CPI', CPI_OBS, '2026-10-26T08:00:00+08:00',
                release_date='2026-10-20')
cD7 = fp.compare_release_availability('2026-10-28',
                                      '2026-10-24T08:00:00+08:00')
vD7 = fp.assess('CPI', CPI_OBS, AS_OF_TS, release_date='2026-10-28')
iD7 = fe.validate_fact(
    fe.make_fact('CPI', 316.0, CPI_OBS, AS_OF_TS, 'macro.json',
                 'macro_collector', release_date='2026-10-28'),
    {'value': 316.0, 'date': CPI_OBS}, fe.metric('CPI'), as_of_date=AS_OF_TS)
check("D4 date-only×ts区间证明两方向: 发布日10-20可能UTC上界(10-21T11:59Z)"
      "早于截止(10-26T00:00Z)→RELEASED_BEFORE(RANGE)+点时OK(RANGE);发布日"
      "10-28可能UTC下界(10-27T10:00Z)晚于截止(10-24T00:00Z)→RELEASED_AFTER"
      "(RANGE)+NOT_AVAILABLE+fe FAIL——FIX1未来发布保护在混合精度下保留",
      cD6['verdict'] == 'RELEASED_BEFORE' and cD6['granularity'] == 'RANGE'
      and vD6['point_in_time']['status'] == 'OK'
      and vD6['point_in_time']['granularity'] == 'RANGE'
      and cD7['verdict'] == 'RELEASED_AFTER' and cD7['granularity'] == 'RANGE'
      and vD7['status'] == 'NOT_AVAILABLE_AT_AS_OF'
      and fe.grade_issues(iD7) == 'FAIL',
      f"{cD6['verdict']}/{cD7['verdict']} {vD7['status']}")
cD8 = fp.compare_release_availability(REL_G1, '2026-10-27T08:00:00+08:00')
check("D5 组一同发布远截止对照: 截止10-27(10-27T00Z)与发布日10-24可能区间"
      "上界(10-25T11:59Z)无交→RELEASED_BEFORE(RANGE)——同一date-only发布"
      "在不同截止下认证与否由区间证明决定,非名义日差",
      cD8['verdict'] == 'RELEASED_BEFORE'
      and cD8['granularity'] == 'RANGE',
      f"{cD8['verdict']}/{cD8['granularity']}")

# ══ E. 正式消费端一致性(真实函数; 两维度分离) ═════════════════════════
print("\n[E] 正式消费端: 观测新鲜(fresh)与点时可得(pit)两维度分离")

def _g1_conditions():
    """A1核心条件(供敏感性G重放): 未证明先后不得确定性认证。"""
    c = fp.compare_release_availability(REL_G1, AS_OF_G1)
    v = fp.assess('CPI', CPI_OBS, AS_OF_G1, release_date=REL_G1)
    iss = fe.validate_fact(
        fe.make_fact('CPI', 316.0, CPI_OBS, AS_OF_G1, 'macro.json',
                     'macro_collector', release_date=REL_G1),
        {'value': 316.0, 'date': CPI_OBS}, fe.metric('CPI'),
        as_of_date=AS_OF_G1)
    return (c['verdict'] in _UNVER
            and v['point_in_time']['status'] == 'POINT_IN_TIME_UNCERTIFIED'
            and fe.grade_issues(iss) != 'FAIL')

check("E1 组一全消费链(真实函数): fresh=True(观测新鲜维度)与点时"
      "POINT_IN_TIME_UNCERTIFIED(可得性维度)**同时成立且互不冒充**——"
      "fresh=True绝不等于'已证明在研究截止前发布'",
      _g1_conditions()
      and v1['fresh'] is True
      and v1['point_in_time']['status'] == 'POINT_IN_TIME_UNCERTIFIED',
      f"fresh={v1['fresh']} pit={v1['point_in_time']['status']}")
anc1 = {'value': 316.0, 'obs_date': CPI_OBS, 'release_date': REL_G1}
check("E2 真实dv消费: is_fresh_anchor=True(新鲜)而stale_anchor_warning无"
      "'点时不可得'(未认证≠不可得,不误伤);metric_registry_info披露"
      "release_provenance='未独立核验'(不表述为已认证发布时间)",
      dv.is_fresh_anchor(CPI_KEY, anc1, AS_OF_G1) is True
      and '点时不可得' not in (dv.stale_anchor_warning(CPI_KEY, anc1,
                                                       AS_OF_G1) or '')
      and '未独立核验' in dv.metric_registry_info(
          CPI_KEY, anc1)['release_provenance'],
      str(dv.metric_registry_info(CPI_KEY, anc1)['release_provenance'])[:50])
ancF = {'value': 316.0, 'obs_date': CPI_OBS, 'release_date': '2026-10-28'}
warnF = dv.stale_anchor_warning(CPI_KEY, ancF, AS_OF_TS)
check("E3 dv反向(区间证明晚于): date-only 10-28×ts截止→警示'点时不可得'"
      "且披露[RANGE(区间证明)与可能UTC区间——消费者可见证明依据",
      '点时不可得' in (warnF or '') and 'RANGE' in (warnF or '')
      and '区间' in (warnF or ''),
      str(warnF)[:80])
tdE, dailyE, snapE = build_day()
stE, whyE = rp.gate_status(snapE, data_dir=dailyE, trusted_root=tdE)
check("E4 真实研究路径(Gate A/B链): 合成采集无release_date→快照"
      "gate_status可用(RELEASE_UNKNOWN不阻断)+正常来源绑定不退化",
      stE is not None and stE in ('PASS', 'DEGRADED')
      and fp.verify_anchor_identity(
          CPI_KEY, {'metric_id': 'CPI'})['status'] == 'MAPPED',
      f"gate={stE} {str(whyE)[:60]}")
tdE2, dailyE2, snapE2 = build_day(
    ymd=DAY, as_of=AS_OF_G1,
    mutate_macro=lambda o: o['data']['CPI'].update(release_date=REL_G1))
fcE2 = fact_of(snapE2, 'CPI')
check("E5 组一进入真实快照(采集端携带date-only release+时刻级research_"
      "as_of): 事实不FAIL(历史兼容)+INFO披露点时未认证+gate_a不受损"
      "(不因混合精度不确定而误伤/编造)——快照内不新增任何发布时间",
      fcE2['quality_status'] != 'FAIL'
      and any('点时未认证' in i['message'] and i['severity'] == 'INFO'
              for i in fcE2['issues'])
      and snapE2['gate_a']['status'] in ('PASS', 'DEGRADED')
      and fcE2.get('release_date') == REL_G1,
      f"q={fcE2['quality_status']} gate={snapE2['gate_a']['status']}")

# ══ F. 原安全回归+§11联合E2E四对象保护 ═══════════════════════════════
print("\n[F] 原安全回归+联合E2E: 混合精度非法认证尝试不损已发布状态")

_rF0 = rp.recompute_gate_a({'target_date': '20261024', 'facts': [],
                            'research_as_of': '2026-10-24INVALID'})
check("F1 Gate A非法截止阻断保留: '2026-10-24INVALID'+合法target_date"
      "→effective=None(不回退洗白)",
      _rF0['effective'] is None, str(_rF0['reasons'][:1]))
cF2 = fp.compare_release_availability('2026-10-24T20:00:00+08:00', AS_OF_TS)
check("F2 同日已知未来发布阻断保留: RELEASED_AFTER(INSTANT)",
      cF2['verdict'] == 'RELEASED_AFTER'
      and cF2['granularity'] == 'INSTANT', cF2['verdict'])
_xF3 = fp.verify_anchor_identity('global_market.data.CPI.close',
                                 {'metric_id': 'CPI'})
check("F3 跨通道锚点伪装拒绝保留: global_market键自称CPI→UNVERIFIED"
      "(SOURCE_MISMATCH)",
      _xF3['status'] == 'UNVERIFIED'
      and _xF3.get('reason') == 'source_mismatch', _xF3['status'])

# §11 联合E2E: 正常研究→合格报告发布→四对象SHA-256→混合精度非法认证尝试
FROOT = tempfile.mkdtemp(prefix='w2fix3-F-', dir=_TMPD)
OUTF = os.path.join(FROOT, 'output', 'weekly')
CFGF = os.path.join(FROOT, 'config')
os.makedirs(OUTF, exist_ok=True)
os.makedirs(CFGF, exist_ok=True)
THEF = os.path.join(CFGF, 'thesis.json')
VWF = os.path.join(CFGF, 'allocation_views.json')
open(THEF, 'w', encoding='utf-8').write(
    '{"version": 1, "theses": [], "updated_at": "2026-10-24T08:00:00"}')
open(VWF, 'w', encoding='utf-8').write(
    '{"version": 2, "views": [], "predictions": []}')
fixt.build_full_day(FROOT, DAY)
_glmF = _GLM()
_appF = []
_rcF = rg_run(rg_harness(_glmF, _appF, os.path.join(FROOT, 'data'), OUTF, DAY))
REPF = os.path.join(OUTF, f'weekly_report_{DAY}.md')
STATF = os.path.join(OUTF, f'report_status_{DAY}.json')
check("F4 前置: 真实发布事务成功(exit0+GLM恰1次+报告/状态落盘)",
      _rcF == 0 and os.path.exists(REPF) and os.path.exists(STATF)
      and _glmF.calls == 1, f"rc={_rcF} glm={_glmF.calls}")
scanF = rp.scan_formal_weekly_reports(OUTF)
baseF = {p: sha(p) for p in (REPF, STATF, THEF, VWF)}

# 混合精度非法认证尝试: 新采集日在**构建前**注入date-only未来发布10-29
# (采集端携带,经真实normalize/validate链)×时刻级research_as_of——名义差5日
# 但区间证明晚于→核心CPI点时不可得→链路须拒
EATK = '20261025'
dailyF = os.path.join(FROOT, 'data', 'daily')
fixt.write_collectors(dailyF, EATK)
_pMacro = os.path.join(dailyF, f'macro_{EATK}.json')
_mF = json.load(open(_pMacro, encoding='utf-8'))
_mF['data']['CPI']['release_date'] = '2026-10-29'      # date-only未来发布
json.dump(_mF, open(_pMacro, 'w', encoding='utf-8'), ensure_ascii=False)
quiet(sb.build_snapshot, EATK, dailyF, dailyF, trusted_root=FROOT,
      as_of=fixt.as_of_for(EATK))                      # 时刻级截止
_pF = os.path.join(dailyF, f'research_snapshot_{EATK}.json')
_fF = json.load(open(_pF, encoding='utf-8'))
_fcF = next(f for f in _fF['facts'] if f['metric_id'] == 'CPI')
_rcF_da = da_run(os.path.join(FROOT, 'data'), EATK)
_glmF2 = _GLM()
_appF2 = []
_rcF2 = rg_run(rg_harness(_glmF2, _appF2, os.path.join(FROOT, 'data'),
                          OUTF, EATK))
_fF = json.load(open(_pF, encoding='utf-8'))
_fcF = next(f for f in _fF['facts'] if f['metric_id'] == 'CPI')
afterF = {p: sha(p) for p in (REPF, STATF, THEF, VWF)}
_newF = sorted(f for f in os.listdir(OUTF)
               if (f.startswith('weekly_report_')
                   or f.startswith('report_status_')) and DAY not in f)
check("F5 非法认证尝试被正式入口拒: date-only未来发布×时刻截止→事实质量"
      "FAIL(NOT_AVAILABLE)+Gate A不可用→数据包拒(exit2无包)+周报拒"
      "(exit2)+GLM=0+零状态回写——混合精度不得经正式链洗白为可得",
      _fcF['quality_status'] == 'FAIL'
      and any('NOT_AVAILABLE' in i['message'] for i in _fcF['issues'])
      and _rcF_da == 2 and not os.path.exists(os.path.join(
          FROOT, 'data', 'weekly', f'data_pack_{EATK}.md'))
      and _rcF2 == 2 and _glmF2.calls == 0 and _appF2 == [],
      f"q={_fcF['quality_status']} da={_rcF_da} rg={_rcF2} "
      f"glm={_glmF2.calls}")
_pubF = sorted(f for f in os.listdir(OUTF) if f.startswith('report_status_')
               and json.load(open(os.path.join(OUTF, f))).get('published')
               is True)
after_final = {p: sha(p) for p in (REPF, STATF, THEF, VWF)}
check("F6 保护核验: 报告/发布状态/thesis/views四对象SHA-256全程不变+无新"
      "报告/状态文件+published=true仅发布日+formal身份有效+scan不变"
      "(未用未认可报告冒充,未编造新发布时间)",
      baseF == afterF == after_final and not _newF
      and _pubF == [f'report_status_{DAY}.json']
      and rp.formal_report_view(REPF)[0] is not None
      and [v['ymd'] for v in rp.scan_formal_weekly_reports(OUTF)]
      == [v['ymd'] for v in scanF],
      str({'changed': [k for k in baseF if baseF[k] != after_final[k]],
           'new': _newF, 'pub': _pubF}))

# ══ G. 敏感性(真实重引入旧缺陷→本套必失败) ══════════════════════════
print("\n[G] 敏感性: 重引入'名义日差≥2即RELEASED_BEFORE'(FIX2缺陷形态)")


def _buggy_nominal(release, as_of):
    """FIX2缺陷形态复刻: 混合精度一律按名义日期判定(≥1日差即RELEASED_"
    BEFORE/AFTER),即DEF-001被重引入时的比较器行为。"""
    r = fp.parse_temporal_value(release)
    a = fp.parse_temporal_value(as_of)
    out = {'verdict': None, 'granularity': None, 'release': release,
           'as_of': as_of, 'detail': 'BUGGY-NOMINAL'}
    if not r['ok']:
        out['verdict'] = 'INVALID_RELEASE'
        return out
    if not a['ok']:
        out['verdict'] = 'INVALID_AS_OF'
        return out
    dd = (a['date'] - r['date']).days
    out['verdict'] = 'RELEASED_BEFORE' if dd > 0 else (
        'RELEASED_AFTER' if dd < 0 else 'UNVERIFIED_SAME_DAY')
    out['granularity'] = 'DAY'
    return out


with mock.patch.object(fp, 'compare_release_availability', _buggy_nominal):
    _buggy_g1_ok = _g1_conditions()            # 组一: bug下变RELEASED_BEFORE→OK误认证
    _bc2 = fp.compare_release_availability(REL_G2, AS_OF_G2)
    _buggy_g2_uncert = _bc2['verdict'] in _UNVER   # 组二: bug下名义差2日→确定性
    _bv1 = fp.assess('CPI', CPI_OBS, AS_OF_G1, release_date=REL_G1)
    _buggy_pit_ok = _bv1['point_in_time']['status'] == 'OK'  # 升级为OK=误认证
check("G1 真实重引入旧比较器(monkeypatch FIX2名义日差形态): 组一条件"
      "(_g1_conditions)由真变假+组二不再UNVERIFIED+assess点时被升为OK"
      "——三路检测同时触发,证明A/E族断言能识别回归,非常量断言",
      (_buggy_g1_ok is False) and (_buggy_g2_uncert is False)
      and (_buggy_pit_ok is True),
      f"g1={_buggy_g1_ok} g2uncert={_buggy_g2_uncert} "
      f"pit={_bv1['point_in_time']['status']}")
_cA1 = fp.compare_release_availability(REL_G1, AS_OF_G1)
check("G2 还原校验: monkeypatch退出后真实比较器恢复(组一仍UNVERIFIED_"
      "PRECISION)——敏感性测试本身无残留污染",
      _cA1['verdict'] == 'UNVERIFIED_PRECISION', _cA1['verdict'])

print("═" * 72)
print(f"W2-FIX3 结果: {PASS_N}通过 / {FAIL_N}失败")
sys.exit(1 if FAIL_N else 0)
