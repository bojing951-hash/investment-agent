#!/usr/bin/env python3
"""IA-P0-2-W2-FIX6 联合验收测试(诊断模式观测新鲜度标注NOT_ASSESSED)。

缺陷编号: IA-P02-W2-FIX5-DEF-001(as_of_date=None诊断模式仍把observation_
freshness固定写成FRESH——未评估的时效不得claim新鲜,未知≠新鲜≠过期)。
真实模块+真实文件系统+隔离临时目录;mock仅限外部GLM/时钟(承FIX1~FIX5口径)。

矩阵(对应指令FIX6-03 A~G + FIX6-04联合回归):
  A 固定诊断反例(真实verify_evidence_items,as_of=None): verified可非空,
    身份/数值/观测日核验通过,observation_freshness=NOT_ASSESSED(非FRESH非
    STALE),pit=AS_OF_UNKNOWN,certified=False,DIAGNOSTIC_ONLY明确说明;
  B 锚点自带as_of反例: 锚点含合法as_of="2026-10-25"但调用仍传None——锚点
    元数据不得提升为正式研究截止(不得据此授予新鲜度认证);
  C 诊断/正式对照: 同一锚点与证据,None→NOT_ASSESSED;合法日期→按指标窗口
    真实计算(FRESH/STALE),证明正式时效计算不受本轮修改影响;
  D 来源身份: 合法CPI+None→受限诊断允许;global_market.data.CPI.close+None
    →拒;未注册键+None→拒(诊断模式身份核验照常,FIX5语义保持);
  E 显式非法截止: ''/' '/0/False/[]/{}/带后缀/非法日历/非法时刻→全部拒收,
    不落诊断(DEF-002修复不回归);
  F 正式负向回归(五情形,FIX5既定结果): 未来发布/过期/非法发布/混合精度
    未认证/合法时间戳已认证;
  G 负向敏感性: 重新把诊断模式observation_freshness硬编码成FRESH→A组断言
    必失败(直接检查诊断路径的新鲜度字段,非仅point_in_time_certified);
  H 联合E2E: 正常发布四对象SHA基线→真实锚点None诊断(不声称时效认证,下游
    按未认证读)→显式非法截止拒→未来发布真实链路拒(Gate A FAIL+da/rg exit2
    +GLM不触发)→四对象SHA全程不变。
"""
import contextlib
import hashlib
import io
import json
import os
import sys
import tempfile
from datetime import datetime
from unittest import mock

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(_HERE), 'scripts'))
sys.path.insert(0, _HERE)

import fixt                                    # noqa: E402
import freshness_policy as fp                  # noqa: E402
import data_validator as dv                    # noqa: E402
import snapshot_builder as sb                  # noqa: E402
import research_provenance as rp               # noqa: E402
import data_assembler as da                    # noqa: E402
import report_generator as rg                  # noqa: E402
import allocation_engine as ae                 # noqa: E402

DAY = '20261024'
CPI_KEY = 'macro.data.CPI.value'
GM_KEY = 'global_market.data.CPI.close'
CPI_OBS = '2026-09-01'
STALE_OBS = '2026-08-16'          # lag 70 > CPI窗60
TODAY = '2026-10-25'
PASS_N, FAIL_N = 0, 0
_TMPD = tempfile.mkdtemp(prefix='w2fix6-')


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
        return ('# 投资周报(SYNTHETIC测试文本·W2-FIX6)\n\n'
                + '本周市场综述与分资产回顾。' * 60)


def build_day(mutate_macro=None, ymd=DAY, root=None, as_of=None):
    """真实链路一天(fixt采集→真实sb.build_snapshot),返回(root, daily, snap)。"""
    td = root or tempfile.mkdtemp(prefix='w2fix6-day-', dir=_TMPD)
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


def anchors_of(daily, ymd):
    return json.load(open(os.path.join(daily, f'anchors_{ymd}.json'),
                          encoding='utf-8'))


print("═" * 72)
print("IA-P0-2-W2-FIX6: 诊断模式观测新鲜度=NOT_ASSESSED(未评估≠新鲜≠过期)")
print("═" * 72)

# 指令§5.1固定反例锚点(含锚点自带as_of——§5.3专项)
FIX_ANCHORS = {CPI_KEY: {'metric_id': 'CPI', 'value': 316.0,
                         'obs_date': CPI_OBS, 'as_of': TODAY}}
FIX_EV = [{'metric': CPI_KEY, 'value': 316.0, 'obs_date': CPI_OBS,
           'mechanism': '通胀'}]

# ══ A. 固定诊断反例(真实verify_evidence_items, as_of_date=None) ═══════════
print("\n[A] 固定诊断反例: None→数值/身份诊断保留,时效如实未评估")

vA, rA = ae.verify_evidence_items(FIX_EV, FIX_ANCHORS, as_of_date=None)
check("A1 §5.1固定反例(as_of_date=None): verified非空+无拒收(数值/观测日/"
      "身份诊断照常),observation_freshness=**NOT_ASSESSED**(≠FRESH,未知不得"
      "claim新鲜),pit=AS_OF_UNKNOWN,certified=False,reason含DIAGNOSTIC_ONLY+"
      "'无法验证观测新鲜度'",
      len(vA) == 1 and not rA
      and vA[0]['observation_freshness'] == 'NOT_ASSESSED'
      and vA[0]['observation_freshness'] not in ('FRESH', 'STALE', 'PASS')
      and vA[0]['point_in_time']['status'] == 'AS_OF_UNKNOWN'
      and vA[0]['point_in_time_certified'] is False
      and 'DIAGNOSTIC_ONLY' in vA[0]['point_in_time']['reason']
      and '无法验证观测新鲜度' in vA[0]['point_in_time']['reason'],
      str(vA[0])[:120] if vA else 'rejected')

check("A2 诊断记录不含任何新鲜度/可得性认证表述: FRESH/PASS/已认证字样不出现在"
      "诊断新鲜度字段与pit reason(负面扫描),verified数值照常(316.0/观测日"
      "2026-09-01)——不因无法判时效而删除合法数值诊断结果",
      vA[0]['value'] == 316.0 and vA[0]['obs_date'] == CPI_OBS
      and 'FRESH' not in json.dumps(vA[0]['point_in_time'], ensure_ascii=False)
      and 'PASS' not in json.dumps(vA[0]['point_in_time'], ensure_ascii=False),
      str(vA[0]['point_in_time'])[:90])

# ══ B. 锚点自带as_of不得偷换正式研究截止(§5.3) ═══════════════════════════
print("\n[B] 锚点as_of边界: 元数据≠调用者提供的正式研究截止")

check("B1 锚点含合法as_of='2026-10-25'但调用仍传None: NOT_ASSESSED(锚点时间"
      "不得自动提升为正式截止并据此授予新鲜度认证);pit.reason明确verified."
      "as_of仅为锚点元数据透传",
      vA[0]['observation_freshness'] == 'NOT_ASSESSED'
      and '锚点元数据透传' in vA[0]['point_in_time']['reason']
      and vA[0]['as_of'] == TODAY,
      str(vA[0]['point_in_time']['reason'])[:80])

# 证明"未提升": 同锚点正式调用才有FRESH——诊断结果与正式结果可区分
vB, rB = ae.verify_evidence_items(FIX_EV, FIX_ANCHORS, as_of_date=TODAY)
check("B2 同锚点同证据+正式as_of='2026-10-25': FRESH(真实窗口计算lag54≤60)"
      "——诊断(NOT_ASSESSED)与正式(FRESH)结果可区分,证明诊断模式确实没有用"
      "锚点as_of偷偷算时效",
      len(vB) == 1 and not rB
      and vB[0]['observation_freshness'] == 'FRESH'
      and vA[0]['observation_freshness'] != vB[0]['observation_freshness'],
      f"diag={vA[0]['observation_freshness']} formal={vB[0]['observation_freshness']}")

# ══ C. 诊断/正式对照(正式时效计算不受影响) ═══════════════════════════════
print("\n[C] 诊断/正式对照: None→未评估;合法截止→按指标窗口真实计算")

stale_anchors = {CPI_KEY: dict(FIX_ANCHORS[CPI_KEY], obs_date=STALE_OBS)}
stale_ev = [{'metric': CPI_KEY, 'value': 316.0, 'obs_date': STALE_OBS,
             'mechanism': '通胀'}]
vC1, rC1 = ae.verify_evidence_items(stale_ev, stale_anchors, as_of_date=None)
vC2, rC2 = ae.verify_evidence_items(stale_ev, stale_anchors, as_of_date=TODAY)
qC2 = dv.anchor_time_qualification(CPI_KEY, stale_anchors[CPI_KEY], TODAY)
check("C1 过期观测对照: None→NOT_ASSESSED保留(未知≠过期,不得预判STALE);"
      "正式→STALE拒收('数据过期…滞后70>60'),适配接口纯观测lag70/窗60——"
      "两个维度各说各话,正式计算精确",
      len(vC1) == 1 and vC1[0]['observation_freshness'] == 'NOT_ASSESSED'
      and vC2 == [] and '数据过期' in rC2[0][0] and '70' in rC2[0][0]
      and qC2['observation_freshness']['lag_days'] == 70
      and qC2['observation_freshness']['window'] == 60
      and qC2['evidence_eligibility']['status'] == 'STALE',
      f"diag={len(vC1)} formal_rej={rC2[0][0][:40] if rC2 else None}")

mix_anchors = {CPI_KEY: dict(FIX_ANCHORS[CPI_KEY],
                             release_date='2026-10-24T23:59:00')}
vC3, rC3 = ae.verify_evidence_items(FIX_EV, mix_anchors, as_of_date=TODAY)
check("C2 混合精度对照(naive发布×date-only截止): UNCERTIFIED保留+certified="
      "False+观测层可用(FIX5既定),observation_freshness=FRESH(正式路径真实"
      "计算)",
      len(vC3) == 1 and not rC3
      and vC3[0]['observation_freshness'] == 'FRESH'
      and vC3[0]['point_in_time']['status'] == 'POINT_IN_TIME_UNCERTIFIED'
      and vC3[0]['point_in_time_certified'] is False,
      str(vC3[0]['point_in_time'])[:70])

# ══ D. 来源身份(诊断模式身份核验照常,FIX5语义保持) ════════════════════════
print("\n[D] 来源身份: 合法+None→受限诊断允许;非法/未注册+None→拒")

vD1, rD1 = ae.verify_evidence_items(FIX_EV, FIX_ANCHORS, as_of_date=None)
check("D1 合法CPI锚点+None: 受限诊断允许(verified非空,NOT_ASSESSED)",
      len(vD1) == 1 and vD1[0]['observation_freshness'] == 'NOT_ASSESSED',
      '')

gm_ev = [{'metric': GM_KEY, 'value': 316.0, 'obs_date': CPI_OBS,
          'mechanism': '通胀'}]
gm_anchors = {GM_KEY: dict(FIX_ANCHORS[CPI_KEY],
                           source_file='global_market.json')}
vD2, rD2 = ae.verify_evidence_items(gm_ev, gm_anchors, as_of_date=None)
check("D2 非法来源(global_market.data.CPI.close)+None: 拒收'身份不可认证'"
      "——诊断模式不得绕过来源身份验证",
      vD2 == [] and len(rD2) == 1 and '身份不可认证' in rD2[0][0],
      rD2[0][0][:60] if rD2 else 'PASS?!')

unreg_ev = [{'metric': 'other.data.NOPE.value', 'value': 1.0,
             'obs_date': CPI_OBS, 'mechanism': 'x'}]
unreg_anchors = {'other.data.NOPE.value': {'value': 1.0, 'obs_date': CPI_OBS,
                                           'as_of': TODAY}}
vD3, rD3 = ae.verify_evidence_items(unreg_ev, unreg_anchors, as_of_date=None)
check("D3 未注册键(other.data.NOPE.value)+None: 拒收(UNMAPPED)",
      vD3 == [] and len(rD3) == 1 and '身份不可认证' in rD3[0][0],
      rD3[0][0][:60] if rD3 else 'PASS?!')

# ══ E. 显式非法截止(不落诊断,DEF-002不回归) ══════════════════════════════
print("\n[E] 显式非法截止: 全部拒收,不重新落入诊断模式")

_bad = ['', ' ', 0, False, [], {}, '2026-10-24INVALID', '2026-13-01',
        '2026-10-24T25:00:00']
_allbad = True
_det = []
for bad in _bad:
    vb, rb = ae.verify_evidence_items(FIX_EV, FIX_ANCHORS, as_of_date=bad)
    if not (vb == [] and len(rb) == 1 and '研究截止非法' in rb[0][0]):
        _allbad = False
        _det.append(f"{bad!r}→{rb[0][0][:36] if rb else 'PASS?!'}")
check("E1 九种显式非法值(''/空白/0/False/[]/{}/带后缀/非法日历/非法时刻): "
      "每种verified空+拒收'研究截止非法'——真值判断绕过不回归",
      _allbad, '; '.join(_det))

# ══ F. 正式负向回归(五情形, FIX5既定结果) ═════════════════════════════════
print("\n[F] 正式负向回归: FIX5五情形结果逐项保持")

fut_anchors = {CPI_KEY: dict(FIX_ANCHORS[CPI_KEY], release_date='2026-10-29')}
vF1, rF1 = ae.verify_evidence_items(FIX_EV, fut_anchors, as_of_date=TODAY)
check("F1 已知未来发布(10-29>10-25): 整项拒'点时不可得…晚于研究截止',纯观测"
      "FRESH+资格拒(FIX5-A4语义)",
      vF1 == [] and '点时不可得' in rF1[0][0] and '晚于研究截止' in rF1[0][0]
      and dv.anchor_time_qualification(CPI_KEY, fut_anchors[CPI_KEY], TODAY)
      ['evidence_eligibility']['usable'] is False,
      rF1[0][0][:50])

check("F2 观测过期(08-16,滞后70>窗60): 拒'数据过期'(C1已证,此处登记为F情形"
      "之一)", vC2 == [] and '数据过期' in rC2[0][0], '')

badrel_anchors = {CPI_KEY: dict(FIX_ANCHORS[CPI_KEY],
                                release_date='2026-10-24BAD')}
vF3, rF3 = ae.verify_evidence_items(FIX_EV, badrel_anchors, as_of_date=TODAY)
check("F3 非法发布时间('2026-10-24BAD'): 拒'时间资格不成立(INVALID_RELEASE…)'",
      vF3 == [] and '时间资格不成立' in rF3[0][0]
      and 'INVALID_RELEASE' in rF3[0][0],
      rF3[0][0][:60])

check("F4 混合精度未认证(naive×date-only): 保留UNCERTIFIED不拒(C2已证)",
      len(vC3) == 1 and vC3[0]['point_in_time_certified'] is False, '')

aware_anchors = {CPI_KEY: dict(FIX_ANCHORS[CPI_KEY],
                               release_date='2026-10-23T20:00:00+08:00')}
vF5, rF5 = ae.verify_evidence_items(FIX_EV, aware_anchors,
                                    as_of_date='2026-10-24T08:00:00+08:00')
check("F5 合法完整时间戳已发布(双aware,10-23T20:00+08<截止10-24T08:00+08): "
      "certified=True+granularity=INSTANT+理由保留'未独立核验'限度",
      len(vF5) == 1 and not rF5
      and vF5[0]['point_in_time_certified'] is True
      and vF5[0]['point_in_time']['granularity'] == 'INSTANT'
      and '未独立核验' in vF5[0]['point_in_time']['reason'],
      str(vF5[0]['point_in_time'])[:80])

# ══ G. 负向敏感性(诊断FRESH硬编码回归→A组必失败) ═════════════════════════
print("\n[G] 负向敏感性: 重新硬编码诊断FRESH→直接检查新鲜度字段的断言必失败")

_real_verify = ae.verify_evidence_items


def _buggy_verify(items, anchors, as_of_date=None):
    """FIX5-DEF-001回归形态: 诊断路径verified项observation_freshness硬编码
    回'FRESH'(仅改该字段,pit/certified不动)。"""
    verified, rejects = _real_verify(items, anchors, as_of_date)
    for v in verified:
        if v['point_in_time']['status'] == 'AS_OF_UNKNOWN':
            v['observation_freshness'] = 'FRESH'
    return verified, rejects


with mock.patch.object(ae, 'verify_evidence_items', _buggy_verify):
    _vg, _rgst = ae.verify_evidence_items(FIX_EV, FIX_ANCHORS, as_of_date=None)
check("G1 DEF回归形态(诊断observation_freshness硬编码'FRESH'): buggy值FRESH≠"
      "真实NOT_ASSESSED,且pit/certified两字段在buggy下**不变**——A1对"
      "observation_freshness的断言在该形态下必失败,证明检测直接命中诊断路径"
      "的新鲜度字段(而非仅靠point_in_time_certified=False旁证)",
      _vg[0]['observation_freshness'] == 'FRESH'
      and vA[0]['observation_freshness'] == 'NOT_ASSESSED'
      and _vg[0]['point_in_time_certified']
      == vA[0]['point_in_time_certified'] is False
      and _vg[0]['point_in_time']['status'] == 'AS_OF_UNKNOWN',
      f"buggy={_vg[0]['observation_freshness']} real={vA[0]['observation_freshness']}")

# ══ H. 联合E2E(§FIX6-04: 正式研究可运行/诊断不污染/负向拒/四对象保护) ═════
print("\n[H] 联合E2E: 正常发布→真实锚点诊断→非法截止拒→未来发布链路拒→保护")

GROOT = tempfile.mkdtemp(prefix='w2fix6-H-', dir=_TMPD)
OUTG = os.path.join(GROOT, 'output', 'weekly')
CFG = os.path.join(GROOT, 'config')
os.makedirs(OUTG, exist_ok=True)
os.makedirs(CFG, exist_ok=True)
THG = os.path.join(CFG, 'thesis.json')
VWG = os.path.join(CFG, 'allocation_views.json')
open(THG, 'w', encoding='utf-8').write(
    '{"version": 1, "theses": [], "updated_at": "2026-10-24T08:00:00"}')
open(VWG, 'w', encoding='utf-8').write(
    '{"version": 2, "views": [], "predictions": []}')
fixt.build_full_day(GROOT, DAY)
_glmG = _GLM()
_appG = []
_rcG = rg_run(rg_harness(_glmG, _appG, os.path.join(GROOT, 'data'), OUTG, DAY))
REPG = os.path.join(OUTG, f'weekly_report_{DAY}.md')
STATG = os.path.join(OUTG, f'report_status_{DAY}.json')
check("H1 正常正式研究可运行(Gate A/B无回归): exit0+GLM恰1次+四对象落盘",
      _rcG == 0 and all(os.path.exists(p) for p in (REPG, STATG, THG, VWG))
      and _glmG.calls == 1, f"rc={_rcG} glm={_glmG.calls}")
baseG = {p: sha(p) for p in (REPG, STATG, THG, VWG)}
scanG = rp.scan_formal_weekly_reports(OUTG)

# H2: 真实锚点(真实sb构造)上的None诊断——不声称时效认证,下游按未认证读
tdH2, dailyH2, snapH2 = build_day(
    ymd=DAY, root=tempfile.mkdtemp(prefix='w2fix6-H2-', dir=_TMPD))
ancH2 = anchors_of(dailyH2, DAY)
evH2 = [{'metric': CPI_KEY, 'value': ancH2[CPI_KEY]['value'],
         'obs_date': ancH2[CPI_KEY]['obs_date'], 'mechanism': '通胀'}]
vH2, rH2 = ae.verify_evidence_items(evH2, {CPI_KEY: ancH2[CPI_KEY]},
                                    as_of_date=None)
_, descH2 = ae.star_level_from_evidence(vH2)
check("H2 真实锚点None诊断: 数值/观测日核验通过(verified非空)+时效NOT_ASSESSED"
      "+certified=False;下游不误认正式认证(uncertified_note非空+星级desc计"
      "入未认证'已认证0·未认证1')——诊断仅用于数值与观测日诊断",
      len(vH2) == 1 and not rH2
      and vH2[0]['observation_freshness'] == 'NOT_ASSESSED'
      and vH2[0]['point_in_time_certified'] is False
      and ae.uncertified_note(vH2) != ''
      and '已认证0·未认证1' in descH2,
      f"obs_f={vH2[0]['observation_freshness'] if vH2 else None} "
      f"desc={descH2[-40:]}")

# H3: 显式非法截止在真实锚点上仍拒
vH3, rH3 = ae.verify_evidence_items(evH2, {CPI_KEY: ancH2[CPI_KEY]},
                                    as_of_date='')
check("H3 显式非法截止(''): 真实锚点上同样拒收'研究截止非法',不落诊断",
      vH3 == [] and len(rH3) == 1 and '研究截止非法' in rH3[0][0],
      rH3[0][0][:50] if rH3 else 'PASS?!')

# H4: 已知未来发布真实链路(Gate A→da→rg)
FUT = '20261026'
tdH4, dailyH4, snapH4 = build_day(
    ymd=FUT, root=tempfile.mkdtemp(prefix='w2fix6-H4-', dir=_TMPD),
    mutate_macro=lambda o: o['data']['CPI'].update(release_date='2026-10-29'))
fcH4 = next(f for f in snapH4['facts'] if f['metric_id'] == 'CPI')
_rcH4da = da_run(os.path.join(tdH4, 'data'), FUT)
_glmH4 = _GLM()
_appH4 = []
OUTH4 = os.path.join(tdH4, 'output', 'weekly')
os.makedirs(OUTH4, exist_ok=True)
_rcH4 = rg_run(rg_harness(_glmH4, _appH4, os.path.join(tdH4, 'data'),
                          OUTH4, FUT))
check("H4 已知未来发布仍被拒(真实链路): 事实FAIL(NOT_AVAILABLE)+Gate A FAIL"
      "→数据包拒(exit2)+周报拒(exit2)+GLM不触发(0)",
      fcH4['quality_status'] == 'FAIL'
      and any('NOT_AVAILABLE' in i['message'] for i in fcH4['issues'])
      and snapH4['gate_a']['status'] == 'FAIL'
      and _rcH4da == 2 and _rcH4 == 2 and _glmH4.calls == 0,
      f"q={fcH4['quality_status']} gate={snapH4['gate_a']['status']} "
      f"da={_rcH4da} rg={_rcH4}")

afterG = {p: sha(p) for p in (REPG, STATG, THG, VWG)}
_newG = sorted(f for f in os.listdir(OUTG)
               if (f.startswith('weekly_report_')
                   or f.startswith('report_status_')) and DAY not in f)
_pubG = sorted(f for f in os.listdir(OUTG) if f.startswith('report_status_')
               and json.load(open(os.path.join(OUTG, f))).get('published')
               is True)
check("H5 四对象保护: 诊断/非法截止/未来发布全部场景后四对象SHA-256==基线+"
      "无新报告/状态文件+published=true仅发布日+formal身份有效+scan不变——"
      "本轮无任何合成状态写入需要,长期状态零触碰",
      baseG == afterG and not _newG
      and _pubG == [f'report_status_{DAY}.json']
      and rp.formal_report_view(REPG)[0] is not None
      and [v['ymd'] for v in rp.scan_formal_weekly_reports(OUTG)]
      == [v['ymd'] for v in scanG],
      str({'changed': [k for k in baseG if baseG[k] != afterG[k]],
           'new': _newG}))

print("═" * 72)
print(f"W2-FIX6 结果: {PASS_N}通过 / {FAIL_N}失败")
sys.exit(1 if FAIL_N else 0)
