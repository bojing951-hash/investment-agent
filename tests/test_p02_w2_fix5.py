#!/usr/bin/env python3
"""IA-P0-2-W2-FIX5 联合验收测试(定向整改: 纯观测时效/点时可得/证据资格三维度独立
+ as_of存在性判断)。

缺陷编号: IA-P02-W2-FIX4-DEF-001(observation_freshness误用fp.assess()综合结论,
发布时序改变纯观测新鲜判定)与IA-P02-W2-FIX4-DEF-002(verify_evidence_items以
真值判断吞掉显式非法as_of,与None诊断路径混同)。
真实模块+真实文件系统+隔离临时目录;mock仅限外部GLM/时钟(承FIX1~FIX4口径)。

矩阵(对应指令FIX5-05 A~E + FIX5-06联合E2E):
  A 三维度独立矩阵(≥7行): 观测新鲜(纯观测,不消费release)/点时可得(B问)/
    证据资格(综合)——FRESH+published→放行, FRESH+RELEASE_UNKNOWN/UNCERTIFIED→
    观测层兼容不认证, FRESH+NOT_AVAILABLE→拒(§5.4强制反例: CPI obs 09-01/
    as_of 10-24/release 10-28/窗60→观测{FRESH,True,53,60}), STALE+published→拒
    (§5.5反向), INVALID_DATE+any→拒, FRESH+INVALID_RELEASE→拒;发布字段变化
    不改变纯观测维度,但改变综合资格(§5.6禁止性捷径双双不成立);
  B 显式非法as_of值表(真实verify_evidence_items): None=唯一进入受限诊断路径的
    值(DIAGNOSTIC_ONLY+AS_OF_UNKNOWN+不认证);''/0/False/[]/{}/纯空白/带后缀/
    非法日历/非法时刻一律整项拒收(含非法研究截止原因,无AS_OF_UNKNOWN路径);
  C 来源身份反绕道: 合法macro.data.CPI.value对照/非法global_market.data.CPI.
    close/键与metric_id冲突/未注册/非法来源+None/非法来源+''——缺研究截止或
    非法研究截止都不能让非法来源获得任何认证(§7.4强制负例);
  D FIX4传播保持: 逐项pit状态+certified布尔/星级desc认证分解/last_change两类/
    台账计数/旧台账兼容/未来发布拒收文案——FIX4成果不被FIX5回退;
  E 负向敏感性(真实重新引入缺陷形态→本套断言必失败): E1 observation_freshness
    改回综合bool(DEF-001回归)→A组纯观测断言必失败; E2 `is None`改回真值判断
    (DEF-002回归)→B组''拒收断言必失败; E3 is_fresh_anchor改判纯观测→已知未来
    发布的正式拒绝(stale_anchor_warning/dpo真实消费方)必失败——经由真实正式
    消费接口,非仅共享原语;
  F 联合E2E(FIX5-06四场景): S1正常发布四对象SHA基线→S2观测新鲜但已知未来发布
    (纯观测FRESH+点时不可得+资格拒+Gate A拦+da/rg exit2+GLM不触发)→S3 as_of=''
    +非法来源锚点(正式核验拒,无评级/论点变化,无长期状态改写)→S4合法未认证
    观测层证据(照常参与+保留限度)→四对象SHA全程不变,合法更新仅落独立合成状态
    文件。
"""
import contextlib
import copy
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
AS_OF_TS = '2026-10-24T08:00:00+08:00'
CPI_KEY = 'macro.data.CPI.value'
CORE_KEY = 'macro.data.CORE_CPI.value'
UNE_KEY = 'macro.data.UNEMPLOYMENT.value'
GM_KEY = 'global_market.data.CPI.close'       # §7.4强制负例: 非法来源身份
CPI_OBS = '2026-09-01'
STALE_OBS = '2026-08-16'                      # lag 70 > CPI窗60(§5.5反向)
TODAY = '2026-10-25'                          # 正式回写日(date-only研究截止)
PASS_N, FAIL_N = 0, 0
_TMPD = tempfile.mkdtemp(prefix='w2fix5-')


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
        return ('# 投资周报(SYNTHETIC测试文本·W2-FIX5)\n\n'
                + '本周市场综述与分资产回顾。' * 60)


def build_day(mutate_macro=None, ymd=DAY, root=None, as_of=None):
    """真实链路一天(fixt采集→真实sb.build_snapshot),返回(root, daily, snap)。"""
    td = root or tempfile.mkdtemp(prefix='w2fix5-day-', dir=_TMPD)
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
print("IA-P0-2-W2-FIX5: 纯观测时效/点时可得/证据资格三维度独立+as_of存在性(DEF-001/002)")
print("═" * 72)

# ══ A. 三维度独立矩阵(FIX5-01, 真实dv适配+ae.verify) ═════════════════════
print("\n[A] 三维度独立矩阵: 观测新鲜(纯观测)/点时可得/证据资格(综合)互不冒充")

EV_CPI = [{'metric': CPI_KEY, 'value': 316.0, 'obs_date': CPI_OBS,
           'mechanism': '通胀'}]


def q_of(release=None, obs=CPI_OBS, as_of=TODAY):
    info = {'value': 316.0, 'obs_date': obs, 'as_of': TODAY, 'metric_id': 'CPI'}
    if release is not None:
        info['release_date'] = release
    return dv.anchor_time_qualification(CPI_KEY, info, as_of), info


def v_of(info, as_of=TODAY):
    return ae.verify_evidence_items(
        [{'metric': CPI_KEY, 'value': 316.0, 'obs_date': info['obs_date'],
          'mechanism': '通胀'}], {CPI_KEY: info}, as_of)


# A1 FRESH + 已证明发布早于截止 → 资格可用+点时认证
q1, i1 = q_of(release='2026-09-20')
v1, r1 = v_of(i1)
check("A1 FRESH+published(双date-only,发布09-20≤截止10-25): 观测FRESH/"
      "lag54/窗60;点时OK(DAY,certified=True);资格usable=True;verify放行",
      q1['observation_freshness'] == {'fresh': True, 'status': 'FRESH',
                                      'lag_days': 54, 'window': 60}
      and q1['point_in_time']['status'] == 'OK'
      and q1['point_in_time_certified'] is True
      and q1['evidence_eligibility']['usable'] is True
      and len(v1) == 1 and not r1,
      str(q1)[:100])

# A2 FRESH + 缺release → 观测层兼容可用,不认证
q2, i2 = q_of(release=None)
v2, r2 = v_of(i2)
check("A2 FRESH+RELEASE_UNKNOWN(缺release_date): 观测FRESH;点时RELEASE_UNKNOWN"
      "(certified=False);资格usable=True(观测层兼容);verify保留",
      q2['observation_freshness']['fresh'] is True
      and q2['point_in_time']['status'] == 'RELEASE_UNKNOWN'
      and q2['point_in_time_certified'] is False
      and q2['evidence_eligibility']['usable'] is True
      and len(v2) == 1 and not r2,
      str(q2['point_in_time'])[:60])

# A3 FRESH + 精度不足未证明 → 观测层兼容可用,不认证
q3, i3 = q_of(release='2026-10-24T23:59:00')   # naive×date-only→UNVERIFIED_TZ
v3, r3 = v_of(i3)
check("A3 FRESH+UNCERTIFIED(naive发布×date-only截止→UNVERIFIED_TZ): 观测FRESH;"
      "点时POINT_IN_TIME_UNCERTIFIED(certified=False);资格usable=True;verify保留",
      q3['observation_freshness']['fresh'] is True
      and q3['point_in_time']['status'] == 'POINT_IN_TIME_UNCERTIFIED'
      and q3['point_in_time_certified'] is False
      and q3['evidence_eligibility']['usable'] is True
      and len(v3) == 1 and not r3,
      str(q3['point_in_time'])[:60])

# A4 §5.4强制反例: 观测新鲜但已知未来发布 → 资格不可用,verify整项拒
q4, i4 = q_of(release='2026-10-28', as_of='2026-10-24')
v4, r4 = v_of(i4, as_of='2026-10-24')
check("A4 FRESH+NOT_AVAILABLE(§5.4反例: obs 09-01/as_of 10-24/release 10-28/"
      "窗60): **纯观测=FRESH/fresh=True/lag53/窗60**(发布不改变观测维度);"
      "点时RELEASE_AFTER_AS_OF;资格usable=False[NOT_AVAILABLE_AT_AS_OF];"
      "verify整项拒('点时不可得…晚于研究截止')——观测新鲜≠as_of时点可得",
      q4['observation_freshness'] == {'fresh': True, 'status': 'FRESH',
                                      'lag_days': 53, 'window': 60}
      and q4['point_in_time']['status'] == 'RELEASE_AFTER_AS_OF'
      and q4['evidence_eligibility']['usable'] is False
      and q4['evidence_eligibility']['status'] == 'NOT_AVAILABLE_AT_AS_OF'
      and v4 == [] and len(r4) == 1
      and '点时不可得' in r4[0][0] and '晚于研究截止' in r4[0][0],
      f"obs={q4['observation_freshness']} rej={r4[0][0][:50] if r4 else None}")

# A5 §5.5反向: 观测滞后超窗 + 发布已证明早于截止 → 观测STALE,资格不可用
q5, i5 = q_of(release='2026-09-20', obs=STALE_OBS)
v5, r5 = v_of(i5)
check("A5 STALE+published(§5.5反向: obs 08-15/lag70>窗60,发布09-20≤截止): "
      "观测STALE(fresh=False);点时OK(certified=True);资格usable=False[STALE];"
      "verify拒('数据过期…滞后70>60')——已发布不救回过期观测",
      q5['observation_freshness']['fresh'] is False
      and q5['observation_freshness']['status'] == 'STALE'
      and q5['observation_freshness']['lag_days'] == 70
      and q5['point_in_time']['status'] == 'OK'
      and q5['point_in_time_certified'] is True
      and q5['evidence_eligibility']['usable'] is False
      and q5['evidence_eligibility']['status'] == 'STALE'
      and v5 == [] and '数据过期' in r5[0][0] and '70' in r5[0][0],
      f"obs={q5['observation_freshness']} rej={r5[0][0][:40] if r5 else None}")

# A6 非法观测日(任意点时) → 拒
q6, i6 = q_of(release='2026-09-20', obs='2026-02-30')
v6, r6 = v_of(i6)
check("A6 INVALID_DATE(obs 2026-02-30)+any: 观测INVALID_DATE(fresh=False);"
      "资格usable=False;verify拒——非法日历日期不得截断救活",
      q6['observation_freshness']['fresh'] is False
      and q6['observation_freshness']['status'] == 'INVALID_DATE'
      and q6['evidence_eligibility']['usable'] is False
      and v6 == [] and len(r6) == 1,
      str(q6['observation_freshness']))

# A7 FRESH + 非法发布字段 → 综合资格不成立
q7, i7 = q_of(release='2026-10-24BAD')
v7, r7 = v_of(i7)
check("A7 FRESH+INVALID_RELEASE(release='2026-10-24BAD'): 观测FRESH(纯观测"
      "不受非法发布字段影响);点时INVALID;资格usable=False[INVALID_RELEASE];"
      "verify拒(时间资格不成立)",
      q7['observation_freshness']['fresh'] is True
      and q7['point_in_time']['status'] == 'INVALID'
      and q7['evidence_eligibility']['usable'] is False
      and q7['evidence_eligibility']['status'] == 'INVALID_RELEASE'
      and v7 == [] and '时间资格不成立' in r7[0][0],
      str(q7['evidence_eligibility'])[:60])

# A8 发布字段变化不改变纯观测维度(同一输入仅release不同)
_qn, in8 = q_of(release=None)
qr_n = dv.anchor_time_qualification(CPI_KEY, in8, TODAY)
qr_b = dv.anchor_time_qualification(
    CPI_KEY, dict(in8, release_date='2026-09-20'), TODAY)
qr_a = dv.anchor_time_qualification(
    CPI_KEY, dict(in8, release_date='2026-10-28'), TODAY)
check("A8 发布无关性: 同一锚点仅release不同(None/已发布/未来发布)→三份"
      "observation_freshness**逐字段相等**(FRESH/True/54/60);综合资格分别为"
      "True/True/False——release只进点时与综合维度,绝不进纯观测维度",
      qr_n['observation_freshness'] == qr_b['observation_freshness']
      == qr_a['observation_freshness']
      and qr_n['observation_freshness']['status'] == 'FRESH'
      and (qr_n['evidence_eligibility']['usable'],
           qr_b['evidence_eligibility']['usable'],
           qr_a['evidence_eligibility']['usable']) == (True, True, False),
      str(qr_a['observation_freshness']))

# A9 §5.6禁止性捷径(负向): 两条"荒谬捷径"都必须不成立
check("A9 §5.6双捷径不成立: ①'未来发布→observation_freshness=False'不成立"
      "(A4纯观测FRESH);②'observation_freshness=True→正式证据一定可用'不成立"
      "(A4资格usable=False且verify拒)——三维度独立即两条捷径同时被证伪",
      q4['observation_freshness']['fresh'] is True
      and q4['evidence_eligibility']['usable'] is False
      and v4 == [],
      '')

# fp层同源: 纯函数无point_in_time键+assess复用同一结论
_pf_pure = fp.assess_observation_freshness('CPI', CPI_OBS, '2026-10-24')
_pf_comp = fp.assess('CPI', CPI_OBS, '2026-10-24', release_date='2026-10-28')
check("A10 fp同源: assess_observation_freshness纯观测(无point_in_time键,"
      "FRESH/53/60);assess()内部复用同一纯观测结论(综合层叠加B问后为"
      "NOT_AVAILABLE)——单一解析与窗口来源,无第二套政策",
      'point_in_time' not in _pf_pure
      and _pf_pure['status'] == 'FRESH' and _pf_pure['lag_days'] == 53
      and _pf_pure['fresh'] is True
      and _pf_comp['status'] == 'NOT_AVAILABLE_AT_AS_OF'
      and _pf_comp['point_in_time']['status'] == 'RELEASE_AFTER_AS_OF',
      str(_pf_pure)[:70])

# ══ B. 显式非法as_of值表(FIX5-02, 真实verify_evidence_items) ════════════
print("\n[B] as_of存在性: 仅None进入受限诊断;其余显式非法值一律拒收")

_ok_info = {'value': 316.0, 'obs_date': CPI_OBS, 'as_of': TODAY,
            'metric_id': 'CPI'}
vn, rn = ae.verify_evidence_items(EV_CPI, {CPI_KEY: _ok_info}, as_of_date=None)
check("B0 None→受限诊断路径(DIAGNOSTIC_ONLY): 数值/观测对齐+身份核验照常,"
      "verified保留;pit=AS_OF_UNKNOWN+理由含DIAGNOSTIC_ONLY;certified=False"
      "(不claim时效认证)",
      len(vn) == 1 and not rn
      and vn[0]['point_in_time']['status'] == 'AS_OF_UNKNOWN'
      and 'DIAGNOSTIC_ONLY' in vn[0]['point_in_time']['reason']
      and vn[0]['point_in_time_certified'] is False,
      str(vn[0]['point_in_time'])[:80] if vn else 'rejected')

_bad_list = ['', ' ', '2026-10-24INVALID', '2026-13-01',
             '2026-10-24T25:00:00', 0, False, [], {}]
_allbad = True
_detail = []
for bad in _bad_list:
    vb, rb = ae.verify_evidence_items(EV_CPI, {CPI_KEY: _ok_info},
                                      as_of_date=bad)
    okc = (vb == [] and len(rb) == 1
           and '研究截止非法' in rb[0][0]
           and 'AS_OF_UNKNOWN' not in rb[0][0]
           and '不可用' not in rb[0][0])
    if not okc:
        _allbad = False
        _detail.append(f"{bad!r}→{rb[0][0][:40] if rb else 'PASS?!'}")
check("B1 显式非法值族(9种: ''/纯空白/带后缀/非法日历/非法时刻/0/False/[]/"
      "/{}): 每种均verified为空+拒收含'研究截止非法'+无AS_OF_UNKNOWN路径+"
      "无fail-closed误报(即真值判断缺陷形态已废除,DEF-002)",
      _allbad, '; '.join(_detail))

# ══ C. 来源身份反绕道(§7.4, 真实正式接口) ═══════════════════════════════
print("\n[C] 来源身份反绕道: 缺/非法研究截止都不能让非法来源获得认证")

_gm_ev = [{'metric': GM_KEY, 'value': 316.0, 'obs_date': CPI_OBS,
           'mechanism': '通胀'}]
_gm_info = {'value': 316.0, 'obs_date': CPI_OBS, 'as_of': TODAY,
            'metric_id': 'CPI', 'source_file': 'global_market.json'}
vc1, rc1 = ae.verify_evidence_items(EV_CPI, {CPI_KEY: _ok_info}, TODAY)
check("C1 合法对照(macro.data.CPI.value+合法截止): MAPPED→verify放行——"
      "反绕道检查不误伤合法来源",
      len(vc1) == 1 and not rc1,
      f"ver={len(vc1)} rej={rc1[:1]}")

vc2, rc2 = ae.verify_evidence_items(_gm_ev, {GM_KEY: _gm_info}, TODAY)
check("C2 非法来源(global_market.data.CPI.close,authority=macro_collector"
      "→SOURCE_MISMATCH)+合法截止: 拒收'身份不可认证';适配接口无任何认证",
      vc2 == [] and len(rc2) == 1 and '身份不可认证' in rc2[0][0]
      and dv.anchor_time_qualification(GM_KEY, _gm_info, TODAY)
      ['point_in_time_certified'] is False,
      rc2[0][0][:60] if rc2 else 'PASS?!')

_conf_info = {'value': 306.0, 'obs_date': CPI_OBS, 'as_of': TODAY,
              'metric_id': 'CPI'}      # CORE键自称CPI→IDENTITY_CONFLICT
vc3, rc3 = ae.verify_evidence_items(
    [{'metric': CORE_KEY, 'value': 306.0, 'obs_date': CPI_OBS,
      'mechanism': '通胀'}], {CORE_KEY: _conf_info}, TODAY)
check("C3 键与metric_id冲突(CORE_CPI键自称CPI): 拒收身份冲突,不得借道获得"
      "资格",
      vc3 == [] and len(rc3) == 1 and '身份不可认证' in rc3[0][0],
      rc3[0][0][:60] if rc3 else 'PASS?!')

_unreg_ev = [{'metric': 'other.data.NOPE.value', 'value': 1.0,
              'obs_date': CPI_OBS, 'mechanism': 'x'}]
vc4, rc4 = ae.verify_evidence_items(_unreg_ev,
                                    {'other.data.NOPE.value':
                                     {'value': 1.0, 'obs_date': CPI_OBS,
                                      'as_of': TODAY}}, TODAY)
check("C4 未注册键(other.data.NOPE.value): UNMAPPED拒收('身份不可认证')——"
      "不在81项注册表内的通道不产生证据",
      vc4 == [] and len(rc4) == 1 and '身份不可认证' in rc4[0][0],
      rc4[0][0][:60] if rc4 else 'PASS?!')

vc5, rc5 = ae.verify_evidence_items(_gm_ev, {GM_KEY: _gm_info},
                                    as_of_date=None)
check("C5 非法来源+as_of=None: 受限诊断路径**同样核验身份**——缺研究截止"
      "不是跨来源伪装的通行证(§7.3A)",
      vc5 == [] and len(rc5) == 1 and '身份不可认证' in rc5[0][0],
      rc5[0][0][:60] if rc5 else 'PASS?!')

vc6, rc6 = ae.verify_evidence_items(_gm_ev, {GM_KEY: _gm_info},
                                    as_of_date='')
check("C6 非法来源+as_of=''(§7.4强制负例): verified为空+拒收含'研究截止非法'"
      "+无AS_OF_UNKNOWN路径+身份未被绕过——显式非法截止连诊断兼容路径都"
      "不得进入,更不得借缺失认证通道洗白身份",
      vc6 == [] and len(rc6) == 1 and '研究截止非法' in rc6[0][0]
      and 'AS_OF_UNKNOWN' not in rc6[0][0]
      and dv.anchor_time_qualification(GM_KEY, _gm_info, '')
      ['evidence_eligibility']['usable'] is False,
      rc6[0][0][:60] if rc6 else 'PASS?!')

# ══ D. FIX4传播保持(FIX5-04: 下游披露/持久化不回退) ══════════════════════
print("\n[D] FIX4传播保持: 认证字段/星级分解/last_change/台账/拒收文案原样")

ANC_MIX = {
    CPI_KEY: {'value': 316.0, 'obs_date': CPI_OBS,
              'release_date': '2026-09-20', 'as_of': TODAY},
    CORE_KEY: {'value': 306.0, 'obs_date': CPI_OBS,
               'release_date': '2026-10-24T23:59:00', 'as_of': TODAY},
    UNE_KEY: {'value': 4.2, 'obs_date': CPI_OBS,
              'release_date': '2026-10-24T20:00:00', 'as_of': TODAY},
}
EV_MIX = [
    {'metric': CPI_KEY, 'value': 316.0, 'obs_date': CPI_OBS, 'mechanism': '通胀'},
    {'metric': CORE_KEY, 'value': 306.0, 'obs_date': CPI_OBS, 'mechanism': '通胀'},
    {'metric': UNE_KEY, 'value': 4.2, 'obs_date': CPI_OBS, 'mechanism': '增长'},
]
verD, rejD = ae.verify_evidence_items(EV_MIX, ANC_MIX, TODAY)
_, descD = ae.star_level_from_evidence(verD)
check("D1 逐项pit状态+certified布尔+星级desc认证分解: 3项verified"
      "(1认证DAY/2未认证UNVERIFIED_TZ),desc='支持项3中已认证1·未认证2(未认证"
      "按观测层证据参与)'——FIX4字段与口径零回退",
      len(verD) == 3 and not rejD
      and sum(1 for i in verD if i['point_in_time_certified']) == 1
      and all('point_in_time' in i and 'point_in_time_certified' in i
              for i in verD)
      and '支持项3中已认证1·未认证2' in descD
      and '未认证按观测层证据参与' in descD,
      descD[-60:])

VWD = os.path.join(_TMPD, 'alloc_views_D.json')
open(VWD, 'w', encoding='utf-8').write(json.dumps({
    'version': 2, 'views': [{'id': 921, 'asset': '美债', 'rating': '标配',
                             'confidence': 1, 'key_metrics': [CPI_KEY],
                             'history': [], 'proposals': []}],
    'predictions': []}, ensure_ascii=False))
REP_D = ('<!--ALLOCATION_STATUS\n'
         + json.dumps({'id': 921, 'rating': '低配', 'confidence': 3,
                       'note': '通胀回落', 'evidence': EV_MIX},
                      ensure_ascii=False)
         + '\nALLOCATION_STATUS-->')
quiet(ae.update_allocation_status, REP_D, views_path=VWD,
      anchors=ANC_MIX, today_str=TODAY)
savedD = json.load(open(VWD, encoding='utf-8'))
vD = next(v for v in savedD['views'] if v['id'] == 921)
ledD = vD.get('evidence_ledger', [])[-1]
check("D2 last_change+台账: via含'未完成点时认证'+'观测层';evidence逐项带"
      "pit+certified;台账point_time_certified=1/uncertified=2(verified全集)",
      vD['rating'] == '低配'
      and '未完成点时认证' in vD['last_change']['via']
      and all('point_in_time_certified' in e
              for e in vD['last_change']['evidence'])
      and ledD.get('point_time_certified') == 1
      and ledD.get('point_time_uncertified') == 2,
      f"via={vD['last_change']['via'][:50]} led={ledD.get('point_time_certified')}")

# 旧台账记录(缺新字段)原样保留
_vw_old = copy.deepcopy(savedD)
_vw_old['views'][0]['evidence_ledger'] = [{
    'date': '2026-09-01', 'rating': '标配', 'verified': 2, 'supporting': 2}]
VWD2 = os.path.join(_TMPD, 'alloc_views_D2.json')
open(VWD2, 'w', encoding='utf-8').write(
    json.dumps(_vw_old, ensure_ascii=False))
open(VWD2, 'w', encoding='utf-8').write(json.dumps(_vw_old, ensure_ascii=False))
check("D3 历史台账兼容: 旧记录缺认证字段按未认证读(uncertified_note非空),"
      "不回填不批量改写",
      ae.uncertified_note([{'metric': CPI_KEY, 'value': 316.0,
                            'obs_date': CPI_OBS}]) != ''
      and _vw_old['views'][0]['evidence_ledger'][0].get(
          'point_time_certified') is None,
      '')

# 未来发布拒收文案保持(FIX4口径)
_fut_info = {'value': 316.0, 'obs_date': CPI_OBS, 'as_of': TODAY,
             'metric_id': 'CPI', 'release_date': '2026-10-29'}
vf, rf = ae.verify_evidence_items(EV_CPI, {CPI_KEY: _fut_info}, TODAY)
check("D4 未来发布拒收文案: '点时不可得…晚于研究截止'(不得回退为误导性"
      "'数据过期')",
      vf == [] and '点时不可得' in rf[0][0] and '晚于研究截止' in rf[0][0]
      and '数据过期' not in rf[0][0],
      rf[0][0][:60])

# ══ E. 负向敏感性(真实重新引入缺陷形态→断言必失败) ══════════════════════
print("\n[E] 负向敏感性: DEF-001/DEF-002/is_fresh_anchor改判三形态必被检出")

# E1: 重新引入DEF-001(observation_freshness改回综合bool) → A4/A8必失败
_real_adapter = dv.anchor_time_qualification


def _buggy_adapter(anchor_key, info, as_of_date):
    """DEF-001回归形态: observation_freshness=fp.assess综合fresh(发布时序
    污染纯观测维度)。"""
    out = _real_adapter(anchor_key, info, as_of_date)
    ident = fp.verify_anchor_identity(anchor_key, info)
    mid = ident['metric_id'] if ident['status'] == 'MAPPED' else anchor_key
    v = fp.assess(mid, (info or {}).get('obs_date'), as_of_date,
                  release_date=(info or {}).get('release_date')
                  if isinstance(info, dict) else None)
    out['observation_freshness'] = {
        'fresh': bool(v['fresh']), 'status': v['status'],
        'lag_days': v.get('lag_days'), 'window': v.get('window')}
    return out


with mock.patch.object(dv, 'anchor_time_qualification', _buggy_adapter):
    _qb = dv.anchor_time_qualification(CPI_KEY, i4, '2026-10-24')
check("E1 DEF-001回归形态(observation_freshness改回bool(assess fresh)): 同一"
      "§5.4输入下buggy fresh=False/status=NOT_AVAILABLE≠真实True/FRESH——"
      "A4纯观测断言与A8发布无关性断言在该形态下必失败(检测依赖真实分离,非"
      "自证常量)",
      _qb['observation_freshness']['fresh'] is False
      and _qb['observation_freshness']['status'] == 'NOT_AVAILABLE_AT_AS_OF'
      and q4['observation_freshness']['fresh'] is True
      and q4['observation_freshness']['status'] == 'FRESH'
      and _qb['observation_freshness'] != q4['observation_freshness'],
      f"buggy={_qb['observation_freshness']}")

# E2: 重新引入DEF-002(`is None`改回真值判断) → B1''拒收必失败
import freshness_policy as _fp_local            # noqa: E402


def _buggy_mode(as_of_date):
    """DEF-002回归形态: `if as_of_date`真值判断——''/0/False等falsy被吞成
    诊断路径。"""
    if not as_of_date:
        return 'diagnostic'
    if isinstance(as_of_date, (ae.date, ae.datetime)):
        return 'formal'
    if isinstance(as_of_date, str) and _fp_local.parse_instant(as_of_date):
        return 'formal'
    return 'invalid'


_vr2, _rr2 = ae.verify_evidence_items(EV_CPI, {CPI_KEY: _ok_info},
                                      as_of_date='')
with mock.patch.object(ae, '_as_of_mode', _buggy_mode):
    _vb2, _rb2 = ae.verify_evidence_items(EV_CPI, {CPI_KEY: _ok_info},
                                          as_of_date='')
check("E2 DEF-002回归形态(_as_of_mode改回真值判断): as_of=''下buggy放行进"
      "verified+AS_OF_UNKNOWN,而真实实现verified空+拒收——B1的''拒收断言在"
      "该形态下必失败(经由真实verify_evidence_items正式接口)",
      _vr2 == [] and '研究截止非法' in _rr2[0][0]
      and len(_vb2) == 1
      and _vb2[0]['point_in_time']['status'] == 'AS_OF_UNKNOWN'
      and _rb2 == [],
      f"buggy_ver={len(_vb2)} real_ver={len(_vr2)}")

# E3: is_fresh_anchor改判纯观测 → 已知未来发布的正式拒绝必失败
def _pure_obs_bool(anchor_key, info, as_of_date):
    """改判形态: 布尔包装只投影纯观测维度(丢综合资格)——未来发布数据将
    返回True。"""
    return dv.anchor_time_qualification(anchor_key, info, as_of_date)[
        'observation_freshness']['fresh']


_fut_anchor = {CPI_KEY: dict(_ok_info, release_date='2026-10-29',
                             quality='PASS')}
_warn_real = dv.stale_anchor_warning(CPI_KEY, _fut_anchor[CPI_KEY], TODAY)
import daily_prediction_observer as dpo           # noqa: E402
_dpo_real = dpo._metric_problem(CPI_KEY, _fut_anchor, TODAY)
with mock.patch.object(dv, 'is_fresh_anchor', _pure_obs_bool):
    _bool_buggy = dv.is_fresh_anchor(CPI_KEY, _fut_anchor[CPI_KEY], TODAY)
    _warn_buggy = dv.stale_anchor_warning(CPI_KEY, _fut_anchor[CPI_KEY], TODAY)
    _dpo_buggy = dpo._metric_problem(CPI_KEY, _fut_anchor, TODAY)
check("E3 is_fresh_anchor改判纯观测形态: 已知未来发布(10-29>10-25)下buggy"
      "返回True+stale_anchor_warning丢'点时不可得'警告(None)+dpo观察放行"
      "(None)≠真实False/警告在场/问题在场——正式消费方(校验报告/长期观察)的"
      "未来发布拒绝断言在该形态下必失败;verify经evidence_eligibility仍拒"
      "(双保险不依赖布尔)",
      _bool_buggy is True
      and dv.is_fresh_anchor(CPI_KEY, _fut_anchor[CPI_KEY], TODAY) is False
      and _warn_buggy is None and _warn_real is not None
      and '点时不可得' in _warn_real
      and _dpo_buggy is None and _dpo_real is not None,
      f"buggy={_bool_buggy} warn_real={(_warn_real or '')[:30]}")

# ══ F. 联合E2E(FIX5-06四场景+四对象SHA保护) ═════════════════════════════
print("\n[F] 联合E2E: S1正常基线→S2未来发布→S3空串截止+非法来源→S4未认证兼容"
      "→四对象保护")

GROOT = tempfile.mkdtemp(prefix='w2fix5-F-', dir=_TMPD)
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
check("F1/S1 正常合格研究真实发布: exit0+GLM恰1次+四对象落盘+SHA基线建立",
      _rcG == 0 and all(os.path.exists(p) for p in (REPG, STATG, THG, VWG))
      and _glmG.calls == 1, f"rc={_rcG} glm={_glmG.calls}")
baseG = {p: sha(p) for p in (REPG, STATG, THG, VWG)}
scanG = rp.scan_formal_weekly_reports(OUTG)

# S2: 观测新鲜但已知未来发布(真实链路)
FUT = '20261026'
tdF2, dailyF2, snapF2 = build_day(
    ymd=FUT, root=tempfile.mkdtemp(prefix='w2fix5-S2-', dir=_TMPD),
    mutate_macro=lambda o: o['data']['CPI'].update(release_date='2026-10-29'))
fcF2 = next(f for f in snapF2['facts'] if f['metric_id'] == 'CPI')
ancF2 = anchors_of(dailyF2, FUT)
qF2 = dv.anchor_time_qualification(CPI_KEY, ancF2[CPI_KEY],
                                   fixt.as_of_for(FUT))
vF2, rF2 = ae.verify_evidence_items(
    [{'metric': CPI_KEY, 'value': ancF2[CPI_KEY]['value'],
      'obs_date': ancF2[CPI_KEY]['obs_date'], 'mechanism': '通胀'}],
    {CPI_KEY: ancF2[CPI_KEY]}, fixt.as_of_for(FUT))
_rcF2da = da_run(os.path.join(tdF2, 'data'), FUT)
_glmF2 = _GLM()
_appF2 = []
OUTF2 = os.path.join(tdF2, 'output', 'weekly')
os.makedirs(OUTF2, exist_ok=True)
_rcF2 = rg_run(rg_harness(_glmF2, _appF2, os.path.join(tdF2, 'data'),
                          OUTF2, FUT))
check("F2/S2 观测新鲜但已知未来发布(真实链路): 事实FAIL(NOT_AVAILABLE)+Gate A"
      "不可用→数据包拒(exit2)+周报拒(exit2,GLM不触发);三维度=纯观测FRESH"
      "(lag55≤60)+点时RELEASE_AFTER+资格拒;证据层verify整项拒('点时不可得')",
      fcF2['quality_status'] == 'FAIL'
      and any('NOT_AVAILABLE' in i['message'] for i in fcF2['issues'])
      and snapF2['gate_a']['status'] == 'FAIL'
      and _rcF2da == 2 and _rcF2 == 2 and _glmF2.calls == 0
      and qF2['observation_freshness']['status'] == 'FRESH'
      and qF2['observation_freshness']['fresh'] is True
      and qF2['observation_freshness']['window'] == 60
      and qF2['point_in_time']['status'] == 'RELEASE_AFTER_AS_OF'
      and qF2['evidence_eligibility']['usable'] is False
      and vF2 == [] and '点时不可得' in rF2[0][0],
      f"q={fcF2['quality_status']} obs={qF2['observation_freshness']} "
      f"da={_rcF2da} rg={_rcF2}")

# S3: as_of='' + 非法来源锚点(正式核验+状态层零改写)
SYN_V3 = os.path.join(_TMPD, 'syn_views_S3.json')
open(SYN_V3, 'w', encoding='utf-8').write(json.dumps({
    'version': 2, 'views': [{'id': 931, 'asset': '美债', 'rating': '标配',
                             'confidence': 1, 'history': [], 'proposals': []}],
    'predictions': []}, ensure_ascii=False))
_gm_anchors = {GM_KEY: dict(_gm_info, release_date='2026-09-20')}
vs3, rs3 = ae.verify_evidence_items(_gm_ev, _gm_anchors, as_of_date='')
_sha_v3_before = sha(SYN_V3)
REP_S3 = ('<!--ALLOCATION_STATUS\n'
          + json.dumps({'id': 931, 'rating': '低配', 'confidence': 3,
                        'note': '非法来源+非法截止', 'evidence': _gm_ev},
                       ensure_ascii=False)
          + '\nALLOCATION_STATUS-->')
quiet(ae.update_allocation_status, REP_S3, views_path=SYN_V3,
      anchors=_gm_anchors, today_str='2026-10-26')
sV3 = json.load(open(SYN_V3, encoding='utf-8'))
vv3 = next(v for v in sV3['views'] if v['id'] == 931)
check("F3/S3 as_of=''+非法来源锚点: 正式核验verified空+拒收含'研究截止非法'"
      "(无AS_OF_UNKNOWN);状态层经真实update_allocation_status零改写"
      "(评级保持标配+无last_change+无evidence_ledger写入;拒收提案留档属"
      "合法审计,不是状态变化)——非法输入不得触发任何评级/论点/长期状态变化",
      vs3 == [] and len(rs3) == 1 and '研究截止非法' in rs3[0][0]
      and vv3['rating'] == '标配'
      and 'last_change' not in vv3
      and not vv3.get('evidence_ledger'),
      f"ver={len(vs3)} rating={vv3['rating']} "
      f"led={bool(vv3.get('evidence_ledger'))}")

# S4: 合法未认证观测层证据(真实链路naive时间戳发布)
EATK = '20261025'
tdF4, dailyF4, snapF4 = build_day(
    ymd=EATK, root=tempfile.mkdtemp(prefix='w2fix5-S4-', dir=_TMPD),
    mutate_macro=lambda o: (o['data']['CPI'].update(
        release_date='2026-10-24T23:59:00'),
        o['data']['CORE_CPI'].update(release_date='2026-10-24T20:00:00')))
ancF4 = anchors_of(dailyF4, EATK)
SYN_V4 = os.path.join(_TMPD, 'syn_views_S4.json')
SYN_T4 = os.path.join(_TMPD, 'syn_thesis_S4.json')
open(SYN_V4, 'w', encoding='utf-8').write(json.dumps({
    'version': 2, 'views': [{'id': 932, 'asset': '美债', 'rating': '标配',
                             'confidence': 1, 'key_metrics': [CPI_KEY],
                             'history': [], 'proposals': []}],
    'predictions': []}, ensure_ascii=False))
open(SYN_T4, 'w', encoding='utf-8').write(json.dumps({
    'version': 1, 'updated_at': '2026-10-24T08:00:00',
    'theses': [{'id': 932, 'name': '通胀回落', 'status': '进行中',
                'confidence': 1, 'related_theses': [], 'history': []}]},
    ensure_ascii=False))
EV_S4 = [
    {'metric': CPI_KEY, 'value': ancF4[CPI_KEY]['value'],
     'obs_date': ancF4[CPI_KEY]['obs_date'], 'mechanism': '通胀'},
    {'metric': CORE_KEY, 'value': ancF4[CORE_KEY]['value'],
     'obs_date': ancF4[CORE_KEY]['obs_date'], 'mechanism': '通胀'},
]
REP_S4 = ('<!--ALLOCATION_STATUS\n'
          + json.dumps({'id': 932, 'rating': '低配', 'confidence': 2,
                        'note': '通胀连续回落', 'evidence': EV_S4},
                       ensure_ascii=False)
          + '\nALLOCATION_STATUS-->\n<!--THESIS_STATUS\n'
          + json.dumps({'id': 932, 'status': '已验证', 'confidence': 2,
                        'note': '两期确认', 'evidence': EV_S4},
                       ensure_ascii=False)
          + '\nTHESIS_STATUS-->')
quiet(ae.update_allocation_status, REP_S4, views_path=SYN_V4,
      anchors=ancF4, today_str='2026-10-25')
quiet(rg.update_thesis_status, REP_S4, thesis_path=SYN_T4,
      today_str='2026-10-25', anchors=ancF4)
sV4 = json.load(open(SYN_V4, encoding='utf-8'))
sT4 = json.load(open(SYN_T4, encoding='utf-8'))
vv4 = next(v for v in sV4['views'] if v['id'] == 932)
tt4 = next(t for t in sT4['theses'] if t['id'] == 932)
check("F4/S4 合法未认证观测层证据: 状态照常更新(评级/论点)且记录保留限度"
      "(via'未完成点时认证'+台账0/2,无伪造认证)——FIX4兼容政策零回退",
      vv4['rating'] == '低配' and tt4['status'] == '已验证'
      and '未完成点时认证' in vv4['last_change']['via']
      and vv4['evidence_ledger'][-1]['point_time_certified'] == 0
      and vv4['evidence_ledger'][-1]['point_time_uncertified'] == 2
      and tt4['evidence_ledger'][-1]['point_time_uncertified'] == 2,
      "rating={} led={}".format(
          vv4['rating'],
          vv4['evidence_ledger'][-1].get('point_time_uncertified')))

afterG = {p: sha(p) for p in (REPG, STATG, THG, VWG)}
_newG = sorted(f for f in os.listdir(OUTG)
               if (f.startswith('weekly_report_')
                   or f.startswith('report_status_')) and DAY not in f)
_pubG = sorted(f for f in os.listdir(OUTG) if f.startswith('report_status_')
               and json.load(open(os.path.join(OUTG, f))).get('published')
               is True)
check("F5 四对象保护: S2/S3/S4全部场景后四对象SHA-256==基线+无新报告/状态"
      "文件+published=true仅发布日+formal身份有效+scan不变——合法更新只发生"
      "在独立合成状态文件(SYN_V3/SYN_V4/SYN_T4)",
      baseG == afterG and not _newG
      and _pubG == [f'report_status_{DAY}.json']
      and rp.formal_report_view(REPG)[0] is not None
      and [v['ymd'] for v in rp.scan_formal_weekly_reports(OUTG)]
      == [v['ymd'] for v in scanG],
      str({'changed': [k for k in baseG if baseG[k] != afterG[k]],
           'new': _newG}))

print("═" * 72)
print(f"W2-FIX5 结果: {PASS_N}通过 / {FAIL_N}失败")
sys.exit(1 if FAIL_N else 0)
