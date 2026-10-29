#!/usr/bin/env python3
"""IA-P0-2-W2-FIX2 联合验收测试(Gate A严格截止时间与真实发布时间精度整改)。

真实模块+真实文件系统+隔离临时目录;mock仅限外部GLM/时钟(承FIX1口径)。

矩阵(对应指令§9 场景A~F+§9.7敏感性):
  A FIX2-01 Gate A研究截止三态: A合法research_as_of(完整验证,不[:10]) /
    B键真缺席→受控回退**仅**严格YYYYMMDD八位真实日历日期target_date
    (记cutoff_source=target_date_fallback) / C显式存在但非法(后缀垃圾/
    None/空串/非字符串/不可解释时间类型)→直接fail-closed绝不经target_date
    洗白('2026-10-24INVALID'+target_date='20261024'不得形成有效Gate A);
    非法target_date('20261024INVALID'/'20260230'/'2026102400'/非str)不可
    为回退源; 含真实链路(recompute/gate_status/rg周报预检/da数据包)与
    三正向(合法both/缺as_of+合法tgt/非法tgt不可回退);
  B FIX2-02 同日未来发布(CPI obs=2026-09-01, as_of=2026-10-24T08:00+08,
    release=2026-10-24T20:00+08): 共享原语/assess/真实fe.validate_fact/
    真实Gate A/数据包+周报入口全拒, GLM=0, 证据层拒;
  C 同日**早**发布合法(as_of=20:00, release=08:00): 不无条件拒同日,
    绝对时刻判RELEASED_BEFORE(INSTANT), 正常质量检查照走;
  D 跨时区≥2对(表面名义日期序≠绝对时刻序, 两方向各一对);
  E 精度不足边界: date-only release×datetime as_of同日→UNVERIFIED_SAME_DAY
    /含naive的相邻日→UNVERIFIED_TZ——按日粒度可得(兼容)但绝不认证点时,
    亦不FAIL既有数据; 双date-only维持FIX1日粒度语义;
  F 正式保护: 真实发布→四对象(报告/发布状态/thesis/views)SHA-256执行前
    基线→危险run(非法research_as_of快照/非法回退源快照)→四对象不变,
    无非法新发布, GLM=0, 无长期状态回写, 失败可诊断;
  S §9.7敏感性: 代码若重新接受INVALID截止或同日未来发布, 本套必失败。
"""
import contextlib
import hashlib
import io
import json
import os
import shutil
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
import allocation_engine as ae                 # noqa: E402
import data_assembler as da                    # noqa: E402
import report_generator as rg                  # noqa: E402
import daily_prediction_observer as dpo        # noqa: E402

DAY = '20261024'
AS_OF = '2026-10-24'
AS_OF_TS = '2026-10-24T08:00:00+08:00'       # FIX2场景B研究截止(早8点)
REL_FUT_TS = '2026-10-24T20:00:00+08:00'     # 同日未来发布(晚8点)
AS_OF_LATE = '2026-10-24T20:00:00+08:00'     # 场景C研究截止(晚8点)
REL_EARLY_TS = '2026-10-24T08:00:00+08:00'   # 场景C发布(早8点)
CPI_KEY = 'macro.data.CPI.value'
CPI_OBS = '2026-09-01'
PASS_N, FAIL_N = 0, 0
_TMPD = tempfile.mkdtemp(prefix='w2fix2-')


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
        return ('# 投资周报(SYNTHETIC测试文本·W2-FIX2)\n\n'
                + '本周市场综述与分资产回顾。' * 60)


def build_day(mutate_macro=None, ymd=DAY, root=None, as_of=None):
    """真实链路一天(fixt采集→真实sb.build_snapshot),返回(root, daily, snap)。"""
    td = root or tempfile.mkdtemp(prefix='w2fix2-day-', dir=_TMPD)
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
print("IA-P0-2-W2-FIX2: 严格截止三态/同日未来发布/时间精度UTC/跨时区/正式保护")
print("═" * 72)

# ══ A. FIX2-01 Gate A研究截止三态 ════════════════════════════════════
print("\n[A] FIX2-01 研究截止三态: 显式非法绝不经target_date洗白")

# A1 共享原语parse_temporal_value: 保真解析(原始输入/日期/精度/tz/偏移/时刻)
tv_date = fp.parse_temporal_value('2026-10-24')
tv_ts = fp.parse_temporal_value('2026-10-24T20:00:00+08:00')
tv_z = fp.parse_temporal_value('2026-10-24T12:00:00Z')
tv_naive = fp.parse_temporal_value('2026-10-24 20:00:00')
tv_dt = fp.parse_temporal_value(datetime(2026, 10, 24, 8, 0, 0))
tv_d = fp.parse_temporal_value(date(2026, 10, 24))
check("A1a parse_temporal_value保真: date-only(DATE_ONLY/tz无/instant None)/"
      "带偏移ts(DATETIME/aware/+08:00/instant)/Z(z aware)/空格分隔naive/"
      "datetime与date实例(不bool误判)",
      tv_date['ok'] and tv_date['precision'] == 'DATE_ONLY'
      and tv_date['tz_aware'] is False and tv_date['utc_offset'] is None
      and tv_date['instant'] is None and tv_date['date'] == date(2026, 10, 24)
      and tv_ts['ok'] and tv_ts['precision'] == 'DATETIME'
      and tv_ts['tz_aware'] is True and tv_ts['utc_offset'] == '+08:00'
      and tv_ts['instant'] is not None
      and tv_z['ok'] and tv_z['tz_aware'] is True and tv_z['utc_offset'] == '+00:00'
      and tv_naive['ok'] and tv_naive['precision'] == 'DATETIME'
      and tv_naive['tz_aware'] is False
      and tv_dt['ok'] and tv_dt['precision'] == 'DATETIME'
      and tv_d['ok'] and tv_d['precision'] == 'DATE_ONLY',
      f"date={tv_date} ts={tv_ts} z={tv_z} naive={tv_naive}")
_bad_tv = ['', '2026-10-24INVALID', '2026-10-24xxx', '2026-02-30',
           '2026-10-24T08:00:00+08:00X', '2026-10-24T08:00:00+0800',
           None, 123, [], {}, True, time(12, 0), ' 2026-10-24']
check("A1b parse_temporal_value拒绝表: 后缀垃圾/假日历/无冒号时差/非字符串/"
      "空串/bool(先于数值拒)/time等不可解释时间类型/前后缀空白——ok=False"
      "且带error, 绝不截断救活",
      all(not fp.parse_temporal_value(x)['ok']
          and fp.parse_temporal_value(x).get('error')
          for x in _bad_tv),
      str([repr(x) for x in _bad_tv
           if fp.parse_temporal_value(x)['ok']]))


def ga(**extra):
    base = {'target_date': '20261024', 'facts': []}
    base.update(extra)
    return rp.recompute_gate_a(base)


# A2 三态: 合法both / 缺as_of受控回退 / 显式非法fail-closed
r_ok = ga(research_as_of='2026-10-24T08:00:00+08:00')
r_okd = ga(research_as_of='2026-10-24')
r_fb = ga()
r_fb2 = ga(target_date='20261023')
check("A2 态A(合法research_as_of, ts与date均整串验证): cutoff_source="
      "'research_as_of', 无截止类reason(失败仅因空facts等下游, 与截止无关)",
      r_ok.get('cutoff_source') == 'research_as_of'
      and r_okd.get('cutoff_source') == 'research_as_of'
      and not any('research_as_of' in r for r in r_ok['reasons']),
      f"{r_ok.get('cutoff_source')} {r_ok['reasons'][:1]}")
check("A2b 态B(键真缺席→受控回退): 合法八位YYYYMMDD真实日历日target_date"
      "可用且cutoff_source='target_date_fallback'(回退可诊断)",
      r_fb.get('cutoff_source') == 'target_date_fallback'
      and r_fb2.get('cutoff_source') == 'target_date_fallback'
      and not any('回退不可用' in r for r in r_fb['reasons']),
      f"{r_fb.get('cutoff_source')} {r_fb['reasons'][:1]}")
for bad_asof in ['2026-10-24INVALID', None, '', 123, time(12, 0)]:
    r_c = ga(research_as_of=bad_asof)
    check(f"A3 态C research_as_of={bad_asof!r}: effective=None+reason点名"
          "'显式存在但非法'+'不得经target_date回退洗白'+无cutoff_source"
          "(绝不放行)",
          r_c['effective'] is None
          and r_c.get('cutoff_source') is None
          and any('research_as_of显式存在但非法' in r
                  and '回退洗白' in r for r in r_c['reasons']),
          f"eff={r_c['effective']} src={r_c.get('cutoff_source')} "
          f"{r_c['reasons'][:1]}")
# A4 非法target_date不可为回退源(键缺席时)
for bad_tgt in ['20261024INVALID', '20261024xxx', '20260230', '2026102400',
                20261024, None]:
    r_d = ga(target_date=bad_tgt)
    check(f"A4 缺as_of且target_date={bad_tgt!r}: 回退不可用→effective=None+"
          "reason'缺失且回退不可用'+严格YYYYMMDD要求",
          r_d['effective'] is None and r_d.get('cutoff_source') is None
          and any('research_as_of缺失且回退不可用' in r
                  and 'YYYYMMDD' in r for r in r_d['reasons']),
          f"eff={r_d['effective']} {r_d['reasons'][:1]}")

# A5 真实链路: 合法快照被注入非法research_as_of+合法target_date(洗白组合)
tdA, dailyA, snapA = build_day()
snapA_pass, reasonA = rp.gate_status(snapA, data_dir=dailyA, trusted_root=tdA)
tamA = json.loads(json.dumps(snapA))
tamA['research_as_of'] = '2026-10-24INVALID'      # 显式非法
tamA['target_date'] = '20261024'                   # 合法回退源在场(洗白诱饵)
st_tam, why_tam = rp.gate_status(tamA, data_dir=dailyA, trusted_root=tdA)
rec_tam = rp.recompute_gate_a(tamA)
check("A5 真实链路洗白组合('2026-10-24INVALID'+target_date='20261024'): "
      "对照快照gate_status=PASS; 注入后gate_status=None(不可用,非PASS/"
      "DEGRADED任何放行态)+recompute fail-closed+reason可诊断",
      snapA_pass == 'PASS' and st_tam is None
      and rec_tam['effective'] is None
      and any('research_as_of显式存在但非法' in r for r in rec_tam['reasons']),
      f"对照={snapA_pass}/{reasonA} 注入={st_tam}/{str(why_tam)[:60]}")
OUTA = os.path.join(tempfile.mkdtemp(prefix='w2fix2-Aout-', dir=_TMPD), 'weekly')
os.makedirs(OUTA, exist_ok=True)
# A5b 磁盘级注入: 正式入口读磁盘快照, 将洗白组合写入快照文件(备份后恢复)
_snapA_path = os.path.join(dailyA, f'research_snapshot_{DAY}.json')
_origA = open(_snapA_path, encoding='utf-8').read()
json.dump(tamA, open(_snapA_path, 'w', encoding='utf-8'), ensure_ascii=False)
_glmA = _GLM()
_appA = []
_rcA = rg_run(rg_harness(_glmA, _appA, os.path.join(tdA, 'data'), OUTA, DAY))
_rcA_da = da_run(os.path.join(tdA, 'data'), DAY)
open(_snapA_path, 'w', encoding='utf-8').write(_origA)
check("A5b 洗白组合在正式入口(磁盘级注入): 真实数据包组装(da)与周报预检(rg)"
      "均拒(exit2+无数据包+GLM=0)——非法截止不得生成任何正式研究产物",
      _rcA == 2 and _rcA_da == 2 and _glmA.calls == 0 and _appA == []
      and not os.path.exists(os.path.join(tdA, 'data', 'weekly',
                                          f'data_pack_{DAY}.md')),
      f"rg={_rcA} da={_rcA_da} glm={_glmA.calls}")
# 注: da/rg读取的是磁盘快照——A5的tamA为内存注入, 用于recompute/gate_status
# 直测; 磁盘级注入(正式入口)见A5b与场景F。

# A6 三正向(FIX2-01要求的正向用例)
snapA2 = json.loads(json.dumps(snapA))
snapA2.pop('research_as_of')                      # 键真缺席+合法target_date
st_fb, why_fb = rp.gate_status(snapA2, data_dir=dailyA, trusted_root=tdA)
snapA3 = json.loads(json.dumps(snapA))
snapA3.pop('research_as_of')
snapA3['target_date'] = '20261024INVALID'         # 键缺席+非法target_date
st_no, why_no = rp.gate_status(snapA3, data_dir=dailyA, trusted_root=tdA)
check("A6 正向三连: 合法both=PASS; 缺as_of+严格八位合法tgt=PASS(受控回退"
      "保持正常研究); 缺as_of+非法tgt=None(非法tgt不得为回退源)",
      snapA_pass == 'PASS' and st_fb == 'PASS' and st_no is None,
      f"both={snapA_pass} fb={st_fb}/{str(why_fb)[:40]} "
      f"badtgt={st_no}/{str(why_no)[:40]}")

# ══ B. FIX2-02 同日未来发布(核心反例) ═══════════════════════════════
print("\n[B] 同日未来发布: obs=2026-09-01/as_of=10-24T08:00+08/release="
      "10-24T20:00+08 全链拒绝")

cmpB = fp.compare_release_availability(REL_FUT_TS, AS_OF_TS)
vB = fp.assess('CPI', CPI_OBS, AS_OF_TS, release_date=REL_FUT_TS)
check("B1 共享原语: compare=RELEASED_AFTER(INSTANT,绝对时刻差+12小时)——"
      "旧parse_instant取日期后'同日相等放行'的漏洞已封; assess="
      "NOT_AVAILABLE_AT_AS_OF+fresh=False+点时RELEASE_AFTER_AS_OF保留偏移",
      cmpB['verdict'] == 'RELEASED_AFTER' and cmpB['granularity'] == 'INSTANT'
      and '12' in cmpB['detail'] and vB['status'] == 'NOT_AVAILABLE_AT_AS_OF'
      and vB['fresh'] is False
      and vB['point_in_time']['status'] == 'RELEASE_AFTER_AS_OF'
      and vB['point_in_time']['granularity'] == 'INSTANT',
      f"{cmpB['verdict']}/{cmpB['granularity']} {vB['status']} "
      f"pit={vB['point_in_time'].get('status')}")
fB = fe.make_fact('CPI', 316.0, CPI_OBS, AS_OF_TS, 'macro_20261024.json',
                  'macro_collector', release_date=REL_FUT_TS)
issB = fe.validate_fact(fB, {'value': 316.0, 'date': CPI_OBS},
                        fe.metric('CPI'), as_of_date=AS_OF_TS)
check("B2 真实fe.validate_fact(统一消费瞬时可得判断): FAIL(category=release,"
      "NOT_AVAILABLE_AT_AS_OF,消息含原始release与as_of与绝对差)——core CPI"
      "事实质量失败",
      fB.get('release_date') == REL_FUT_TS
      and any(i['severity'] == 'FAIL' and i['category'] == 'release'
              and 'NOT_AVAILABLE_AT_AS_OF' in i['message']
              and REL_FUT_TS in i['message'] and '+12小时' in i['message']
              for i in issB)
      and fe.grade_issues(issB) == 'FAIL',
      str(issB)[:120])
factsB = fe.normalize_macro({'data': {'CPI': {'value': 316.0, 'date': CPI_OBS,
                                              'release_date': REL_FUT_TS}}},
                            AS_OF_TS)
fBn = next(f for f in factsB if f['metric_id'] == 'CPI')
check("B3 真实采集消费入口(normalize_macro): release透传→事实quality FAIL"
      "(非孤立副本)", fBn.get('release_date') == REL_FUT_TS
      and fBn['quality_status'] == 'FAIL'
      and any('NOT_AVAILABLE_AT_AS_OF' in i['message'] for i in fBn['issues']),
      fBn['quality_status'])
tdB, dailyB, snapB = build_day(
    ymd=DAY, mutate_macro=lambda o: o['data']['CPI'].update(
        release_date=REL_FUT_TS))
fcB = fact_of(snapB, 'CPI')
ancB = json.load(open(os.path.join(dailyB, f'anchors_{DAY}.json'),
                      encoding='utf-8'))[CPI_KEY]
# 证据/观察消费入口须用同精度研究截止(时间戳)——点时先后判断方有依据;
# 日期粒度截止下同日ts发布属E1'可得未认证'守恒态(设计语义, 非漏洞)。
warnB = dv.stale_anchor_warning(CPI_KEY, ancB, AS_OF_TS)
check("B4 真实Gate A链路(sb透传): CPI事实FAIL→Gate A=FAIL; 锚点携带原偏移"
      "release; dv.is_fresh=False; 警示披露绝对时刻关系(非'两同日'含糊)",
      snapB['gate_a']['status'] == 'FAIL' and fcB['quality_status'] == 'FAIL'
      and any('NOT_AVAILABLE_AT_AS_OF' in i['message'] for i in fcB['issues'])
      and ancB.get('release_date') == REL_FUT_TS
      and dv.is_fresh_anchor(CPI_KEY, ancB, AS_OF_TS) is False
      and warnB and 'INSTANT' in warnB and '20:00' in warnB,
      f"gate={snapB['gate_a']['status']} q={fcB['quality_status']} "
      f"rel={ancB.get('release_date')} warn={str(warnB)[:60]}")
_rcB_da = da_run(os.path.join(tdB, 'data'), DAY)
OUTB = os.path.join(tempfile.mkdtemp(prefix='w2fix2-Bout-', dir=_TMPD), 'weekly')
os.makedirs(OUTB, exist_ok=True)
_glmB = _GLM()
_appB = []
_rcB = rg_run(rg_harness(_glmB, _appB, os.path.join(tdB, 'data'), OUTB, DAY))
verB, rejB = ae.verify_evidence_items(
    [{'metric': CPI_KEY, 'value': 316.0, 'obs_date': CPI_OBS, 'mechanism': '通胀'}],
    {CPI_KEY: ancB}, AS_OF_TS)
probB = dpo._metric_problem(CPI_KEY, {CPI_KEY: ancB}, AS_OF_TS)
check("B5 正式产物与消费入口: 数据包拒(exit2无包)+周报预检拒(exit2)+GLM=0"
      "+零状态回写+证据层拒(ae)+长期观察拒(dpo)",
      _rcB_da == 2 and not os.path.exists(os.path.join(
          tdB, 'data', 'weekly', f'data_pack_{DAY}.md'))
      and _rcB == 2 and _glmB.calls == 0 and _appB == []
      and verB == [] and rejB and '点时不可得' in rejB[0][0]
      and '晚于研究截止' in rejB[0][0]
      and probB and '不得进入长期观察' in probB,
      f"da={_rcB_da} rg={_rcB} glm={_glmB.calls} ae={len(rejB)} "
      f"dpo={str(probB)[:40]}")

# ══ C. 同日早发布合法(不无条件拒同日) ═══════════════════════════════
print("\n[C] 同日早发布: as_of=10-24T20:00+08/release=10-24T08:00+08 合法")

cmpC = fp.compare_release_availability(REL_EARLY_TS, AS_OF_LATE)
vC = fp.assess('CPI', CPI_OBS, AS_OF_LATE, release_date=REL_EARLY_TS)
check("C1 共享原语: RELEASED_BEFORE(INSTANT,早12小时)——同日不等于不可用,"
      "先后由绝对时刻判定", cmpC['verdict'] == 'RELEASED_BEFORE'
      and cmpC['granularity'] == 'INSTANT' and '12' in cmpC['detail']
      and vC['status'] == 'FRESH' and vC['fresh'] is True
      and vC['point_in_time']['status'] == 'OK'
      and vC['point_in_time']['granularity'] == 'INSTANT',
      f"{cmpC['verdict']} {vC['status']} pit={vC['point_in_time']}")
tdC, dailyC, snapC = build_day(
    ymd=DAY, as_of=AS_OF_LATE,
    mutate_macro=lambda o: o['data']['CPI'].update(release_date=REL_EARLY_TS))
fcC = fact_of(snapC, 'CPI')
issC = [i for i in fcC['issues'] if i.get('category') == 'release']
check("C2 真实链路(自定义研究截止20:00): 同日早发布CPI质量PASS+无任何"
      "release问题+滞后窗照走(lag53≤60)+Gate A=PASS——B场景同一对输入"
      "在正确时刻语义下正常放行(精度修复不误伤合法同日)",
      snapC['gate_a']['status'] == 'PASS'
      and fcC['quality_status'] == 'PASS' and not issC
      and fcC.get('release_date') == REL_EARLY_TS,
      f"gate={snapC['gate_a']['status']} q={fcC['quality_status']} "
      f"rel_issues={issC}")
_CPI_LAG = fp.assess('CPI', CPI_OBS, AS_OF_LATE)['lag_days']
check("C3 正常质量检查未被跳过: 新鲜度lag仍按研究截止计算(lag=53, 月频窗"
      "60), 同日放行≠放弃时效校验", _CPI_LAG == 53,
      f"lag={_CPI_LAG}")

# ══ D. 跨时区(表面名义日期序≠绝对时刻序) ════════════════════════════
print("\n[D] 跨时区≥2对: 名义日期序与绝对时刻序相反的两方向")

# D1: 表面看release(10-24)晚于as_of(10-23)→该拒; 绝对时刻release早1小时→该放
cD1 = fp.compare_release_availability('2026-10-24T02:00:00+08:00',
                                      '2026-10-23T15:00:00-04:00')
vD1 = fp.assess('CPI', CPI_OBS, '2026-10-23T15:00:00-04:00',
                release_date='2026-10-24T02:00:00+08:00')
check("D1 对1(名义序=晚,绝对序=早): release 10-24T02+08(=10-23T18Z) vs "
      "as_of 10-23T15-04(=19Z)→RELEASED_BEFORE(INSTANT)可用, 按旧日期比较"
      "会误拒", cD1['verdict'] == 'RELEASED_BEFORE'
      and cD1['granularity'] == 'INSTANT' and vD1['fresh'] is True
      and vD1['point_in_time']['status'] == 'OK',
      f"{cD1['verdict']} {vD1['point_in_time']}")
# D2: 表面看release(10-23)早于as_of(10-24)→该放; 绝对时刻release晚7小时→该拒
cD2 = fp.compare_release_availability('2026-10-23T18:00:00-05:00',
                                      '2026-10-24T00:00:00+08:00')
vD2 = fp.assess('CPI', CPI_OBS, '2026-10-24T00:00:00+08:00',
                release_date='2026-10-23T18:00:00-05:00')
fD2 = fe.make_fact('CPI', 316.0, CPI_OBS, '2026-10-24T00:00:00+08:00',
                   'macro.json', 'macro_collector',
                   release_date='2026-10-23T18:00:00-05:00')
issD2 = fe.validate_fact(fD2, {'value': 316.0, 'date': CPI_OBS},
                         fe.metric('CPI'),
                         as_of_date='2026-10-24T00:00:00+08:00')
check("D2 对2(名义序=早,绝对序=晚): release 10-23T18-05(=23Z) vs as_of "
      "10-24T00+08(=10-23T16Z)→RELEASED_AFTER(INSTANT)不可得, 按旧日期比较"
      "会误放; assess+真实validate_fact双拒",
      cD2['verdict'] == 'RELEASED_AFTER' and cD2['granularity'] == 'INSTANT'
      and vD2['status'] == 'NOT_AVAILABLE_AT_AS_OF'
      and vD2['fresh'] is False
      and any(i['severity'] == 'FAIL' and 'NOT_AVAILABLE_AT_AS_OF' in i['message']
              for i in issD2),
      f"{cD2['verdict']} {vD2['status']} grade={fe.grade_issues(issD2)}")
check("D3 UTC偏移保真: parse_temporal_value对-04:00/-05:00/+08:00保留"
      "utc_offset与aware标记(比较依据可审计)",
      fp.parse_temporal_value('2026-10-23T15:00:00-04:00')['utc_offset']
      == '-04:00'
      and fp.parse_temporal_value('2026-10-23T18:00:00-05:00')['utc_offset']
      == '-05:00'
      and fp.parse_temporal_value('2026-10-24T02:00:00+08:00')['utc_offset']
      == '+08:00',
      '')

# ══ E. 精度不足边界(date-only×datetime/naive混合) ═══════════════════
print("\n[E] 精度不足: 不认证点时亦不误伤既有数据")

cE1 = fp.compare_release_availability('2026-10-24', AS_OF_TS)
vE1 = fp.assess('CPI', CPI_OBS, AS_OF_TS, release_date='2026-10-24')
fE1 = fe.make_fact('CPI', 316.0, CPI_OBS, AS_OF_TS, 'macro.json',
                   'macro_collector', release_date='2026-10-24')
issE1 = fe.validate_fact(fE1, {'value': 316.0, 'date': CPI_OBS},
                         fe.metric('CPI'), as_of_date=AS_OF_TS)
check("E1 date-only release×datetime as_of同名义日: UNVERIFIED_SAME_DAY→"
      "按日粒度可得(fresh=True/FRESH日粒度兼容)+点时POINT_IN_TIME_UNCERTIFIED"
      "(绝不认证'已验证点时可得')+fe只INFO披露不FAIL",
      cE1['verdict'] == 'UNVERIFIED_SAME_DAY'
      and vE1['status'] == 'FRESH' and vE1['fresh'] is True
      and vE1['point_in_time']['status'] == 'POINT_IN_TIME_UNCERTIFIED'
      and fe.grade_issues(issE1) != 'FAIL'
      and any(i['severity'] == 'INFO' and '点时未认证' in i['message']
              for i in issE1),
      f"{cE1['verdict']} {vE1['point_in_time'].get('status')} "
      f"grade={fe.grade_issues(issE1)}")
cE2 = fp.compare_release_availability('2026-10-24T08:00:00',
                                      '2026-10-25T08:00:00+08:00')
vE2 = fp.assess('CPI', CPI_OBS, '2026-10-25T08:00:00+08:00',
                release_date='2026-10-24T08:00:00')
fE2 = fe.make_fact('CPI', 316.0, CPI_OBS, '2026-10-25T08:00:00+08:00',
                   'macro.json', 'macro_collector',
                   release_date='2026-10-24T08:00:00')
issE2 = fe.validate_fact(fE2, {'value': 316.0, 'date': CPI_OBS},
                         fe.metric('CPI'),
                         as_of_date='2026-10-25T08:00:00+08:00')
# [FIX3-01期望变更·逐项说明] 原断言UNVERIFIED_TZ(FIX2"相邻日一律不可证")
# 是**欠声称**: naive墙钟10-24T08:00在任何现实时区(−12:00~+14:00)解释下
# 最晚UTC=10-24T20:00Z,严格早于截止10-25T08:00+08:00=10-25T00:00Z——
# FIX3指令§5.5第5条明示"可验证时间范围证明"允许确定性结论。FIX3起该组
# 合判RELEASED_BEFORE(RANGE): 先后已证(区间无交),不冒充精确时刻;粒度
# RANGE区别于INSTANT(组二同名义差2日仍UNVERIFIED_TZ,见test_p02_w2_fix3)。
check("E2 naive release×aware as_of相邻日(FIX3-01区间证明): naive墙钟最晚"
      "可能UTC(10-24T20:00Z)严格早于截止(10-25T00:00Z)→RELEASED_BEFORE"
      "(RANGE)——先后已证但非精确时刻;点时OK(RANGE粒度)+fresh按日粒度True"
      "+fe不FAIL亦无'点时未认证'INFO",
      cE2['verdict'] == 'RELEASED_BEFORE' and cE2['granularity'] == 'RANGE'
      and vE2['point_in_time']['status'] == 'OK'
      and vE2['point_in_time']['granularity'] == 'RANGE'
      and vE2['fresh'] is True and fe.grade_issues(issE2) != 'FAIL'
      and not any('点时未认证' in i['message'] for i in issE2),
      f"{cE2['verdict']}/{cE2['granularity']} "
      f"{vE2['point_in_time'].get('status')}")
cE3 = fp.compare_release_availability('2026-10-25T08:00:00+08:00',
                                      '2026-10-24T20:00:00')
check("E3 aware release×naive as_of相邻日(反向混合): 同样UNVERIFIED_TZ, "
      "不因release侧带偏移而单边采信",
      cE3['verdict'] == 'UNVERIFIED_TZ', cE3['verdict'])
cE4 = fp.compare_release_availability('2026-09-15', '2026-10-24')
vE4 = fp.assess('CPI', CPI_OBS, AS_OF, release_date='2026-09-15')
check("E4 双date-only(遗留口径): RELEASED_BEFORE(DAY)日粒度判定+点时OK"
      "(FIX1 B5兼容不回退)",
      cE4['verdict'] == 'RELEASED_BEFORE' and cE4['granularity'] == 'DAY'
      and vE4['point_in_time']['status'] == 'OK'
      and vE4['point_in_time']['granularity'] == 'DAY',
      f"{cE4['verdict']}/{cE4['granularity']} "
      f"{vE4['point_in_time'].get('status')}")
cE5 = fp.compare_release_availability('2026-10-28', '2026-10-24')
vE5 = fp.assess('CPI', CPI_OBS, AS_OF, release_date='2026-10-28')
warnE5 = dv.stale_anchor_warning(CPI_KEY, {'value': 316.0,
                                           'obs_date': CPI_OBS,
                                           'release_date': '2026-10-28'}, AS_OF)
check("E5 双date-only跨日未来(DAY粒度NOT_AVAILABLE)与缺release"
      "(RELEASE_UNKNOWN)两态保留(FIX1 B4/B1兼容)——精度扩展未改变旧语义",
      cE5['verdict'] == 'RELEASED_AFTER' and cE5['granularity'] == 'DAY'
      and vE5['status'] == 'NOT_AVAILABLE_AT_AS_OF'
      and vE5['fresh'] is False and '点时不可得' in (warnE5 or '')
      and fp.assess('CPI', CPI_OBS, AS_OF)['point_in_time']['status']
      == 'RELEASE_UNKNOWN',
      f"{vE5['status']} pit兼容OK")

# ══ F. 正式保护(四对象执行前基线) ═══════════════════════════════════
print("\n[F] 正式报告保护: 危险run(非法截止/非法回退源)不损已发布状态")

FROOT = tempfile.mkdtemp(prefix='w2fix2-F-', dir=_TMPD)
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
check("F1 前置: 真实发布事务成功(exit0+GLM恰1次+报告/状态落盘)",
      _rcF == 0 and os.path.exists(REPF) and os.path.exists(STATF)
      and _glmF.calls == 1, f"rc={_rcF} glm={_glmF.calls}")
scanF = rp.scan_formal_weekly_reports(OUTF)
baseF = {p: sha(p) for p in (REPF, STATF, THEF, VWF)}

# 危险run1: 新采集日快照被写入显式非法research_as_of(磁盘级注入)
EATK = '20261025'
dailyF = os.path.join(FROOT, 'data', 'daily')
fixt.write_collectors(dailyF, EATK)
quiet(sb.build_snapshot, EATK, dailyF, dailyF, trusted_root=FROOT,
      as_of=fixt.as_of_for(EATK))
_pF = os.path.join(dailyF, f'research_snapshot_{EATK}.json')
_oF = json.load(open(_pF, encoding='utf-8'))
_oF['research_as_of'] = '2026-10-25INVALID'       # 显式非法截止
_oF['target_date'] = '20261025'                    # 合法回退源(洗白诱饵)
json.dump(_oF, open(_pF, 'w', encoding='utf-8'), ensure_ascii=False)
_rcF_da = da_run(os.path.join(FROOT, 'data'), EATK)
_glmF2 = _GLM()
_appF2 = []
_rcF2 = rg_run(rg_harness(_glmF2, _appF2, os.path.join(FROOT, 'data'),
                          OUTF, EATK))
afterF = {p: sha(p) for p in (REPF, STATF, THEF, VWF)}
_newF = sorted(f for f in os.listdir(OUTF)
               if (f.startswith('weekly_report_')
                   or f.startswith('report_status_')) and DAY not in f)
check("F2 危险run1(显式非法research_as_of): 数据包拒(exit2无包)+周报拒"
      "(exit2)+GLM=0+零状态回写",
      _rcF_da == 2 and not os.path.exists(os.path.join(
          FROOT, 'data', 'weekly', f'data_pack_{EATK}.md'))
      and _rcF2 == 2 and _glmF2.calls == 0 and _appF2 == [],
      f"da={_rcF_da} rg={_rcF2} glm={_glmF2.calls}")

# 危险run2: research_as_of键剔除+target_date非法(回退源污染)
_oF2 = json.load(open(_pF, encoding='utf-8'))
_oF2.pop('research_as_of')
_oF2['target_date'] = '20261025GARBAGE'
json.dump(_oF2, open(_pF, 'w', encoding='utf-8'), ensure_ascii=False)
_glmF3 = _GLM()
_rcF3 = rg_run(rg_harness(_glmF3, [], os.path.join(FROOT, 'data'), OUTF, EATK))
afterF2 = {p: sha(p) for p in (REPF, STATF, THEF, VWF)}
check("F3 危险run2(缺as_of+非法回退源target_date): 周报入口同样拒"
      "(exit2+GLM=0)", _rcF3 == 2 and _glmF3.calls == 0,
      f"rc={_rcF3} glm={_glmF3.calls}")
_pubF = sorted(f for f in os.listdir(OUTF) if f.startswith('report_status_')
               and json.load(open(os.path.join(OUTF, f))).get('published')
               is True)
after_final = {p: sha(p) for p in (REPF, STATF, THEF, VWF)}
check("F4 保护核验: 报告/发布状态/thesis/views四对象SHA-256全程不变+无新"
      "报告/状态文件+published=true仅发布日+formal身份有效+scan不变",
      baseF == afterF == afterF2 == after_final and not _newF
      and _pubF == [f'report_status_{DAY}.json']
      and rp.formal_report_view(REPF)[0] is not None
      and [v['ymd'] for v in rp.scan_formal_weekly_reports(OUTF)]
      == [v['ymd'] for v in scanF],
      str({'changed': [k for k in baseF if baseF[k] != after_final[k]],
           'new': _newF, 'pub': _pubF}))
_stF, _whyF = rp.gate_status(_oF)
check("F5 失败可诊断: 危险快照gate_status=None且reason点名非法截止(非静默"
      "不可解)", _stF is None and _whyF
      and ('显式存在但非法' in _whyF or '回退不可用' in _whyF),
      str(_whyF)[:80])

# ══ S. §9.7 敏感性 ══════════════════════════════════════════════════
print("\n[S] §9.7 敏感性: 代码若重新接受非法截止或同日未来发布, 以下必失败")

_sensA = rp.recompute_gate_a({'target_date': '20261024', 'facts': [],
                              'research_as_of': '2026-10-24INVALID'})
check("S1 若代码重新接受'2026-10-24INVALID'(cutoff被洗白为10-24且无诊断"
      "reason)本测试失败: 现实现cutoff_source=None+reason在场",
      _sensA.get('cutoff_source') is None and _sensA['effective'] is None
      and any('显式存在但非法' in r for r in _sensA['reasons']),
      f"src={_sensA.get('cutoff_source')}")
_sensB = fp.compare_release_availability(REL_FUT_TS, AS_OF_TS)
check("S2 若比较器对同日未来发布改判RELEASED_BEFORE/UNVERIFIED(退回日期"
      "相等放行)本测试失败: 现判定RELEASED_AFTER(INSTANT)",
      _sensB['verdict'] == 'RELEASED_AFTER'
      and _sensB['granularity'] == 'INSTANT', _sensB['verdict'])
_sensC = fe.validate_fact(
    fe.make_fact('CPI', 316.0, CPI_OBS, AS_OF_TS, 'm.json', 'macro_collector',
                 release_date=REL_FUT_TS),
    {'value': 316.0, 'date': CPI_OBS}, fe.metric('CPI'), as_of_date=AS_OF_TS)
check("S3 若fe对同日未来发布改判非FAIL本测试失败: 现FAIL(NOT_AVAILABLE_"
      "AT_AS_OF)", fe.grade_issues(_sensC) == 'FAIL'
      and any('NOT_AVAILABLE_AT_AS_OF' in i['message'] for i in _sensC),
      fe.grade_issues(_sensC))
_sensE = fp.assess('CPI', CPI_OBS, AS_OF_TS, release_date='2026-10-24')
check("S4 若精度不足被误升为点时认证(OK)或误伤(FAIL/fresh=False)本测试"
      "失败: 现POINT_IN_TIME_UNCERTIFIED+fresh=True",
      _sensE['point_in_time']['status'] == 'POINT_IN_TIME_UNCERTIFIED'
      and _sensE['fresh'] is True and _sensE['status'] == 'FRESH',
      f"{_sensE['point_in_time'].get('status')}/{_sensE['status']}")

shutil.rmtree(_TMPD, ignore_errors=True)
print("\n" + "═" * 72)
print(f"W2-FIX2 结果: {PASS_N}通过 / {FAIL_N}失败")
if FAIL_N:
    sys.exit(1)
