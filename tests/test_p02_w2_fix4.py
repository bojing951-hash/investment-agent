#!/usr/bin/env python3
"""IA-P0-2-W2-FIX4 联合验收测试(点时认证状态在正式证据链的传递与消费)。

缺陷编号: IA-P02-W2-FIX3-DEF-001(POINT_IN_TIME_UNCERTIFIED在正式证据链丢失)。
真实模块+真实文件系统+隔离临时目录;mock仅限外部GLM/时钟(承FIX1~FIX3口径)。

矩阵(对应指令FIX4-05 A~F + FIX4-04固定反例 + FIX4-06联合E2E):
  A 接口完备性+固定反例: 反例1(date-only发布×aware截止→FRESH+UNCERTIFIED,
    不丢弃不冒充)/反例2(naive发布×+14:00截止→不认证,精度与理由保留到正式
    接口)/反例3(aware发布晚于aware截止→拒收,不得进qualified支持集)/
    正向对照(双aware早于截止→正常认证INSTANT,不无据拒收)/历史兼容
    (缺release→RELEASE_UNKNOWN可用不伪造)/诊断路径(无as_of→AS_OF_UNKNOWN
    绝不默认授予认证);
  B 正式传播: dv适配接口→ae.verify_evidence_items→方向切分→星级统计→
    last_change→evidence_ledger→rg.update_thesis_status(真实模块,合成沙箱);
  C 计数纪律: 两项"有效但未认证"合成证据不计入已认证;按观测层参与时记录
    必须写明观测层证据;新披露字段不重复计数;反证/中立/同周/同基底去重保持;
  D 失败防护: 未来发布/身份冲突/来源家族伪装/非法日期/过期拒绝;时间校验
    模块模拟不可用→fail-closed(旧ImportError静默授权废除);
  E 历史兼容: 无release_date研究照常运行(观测层+如实认证级别);旧台账/
    旧证据记录缺字段→按未认证读,不推定不回填;
  F 敏感性: 从verified删除点时字段、或把未认证重计为已认证→本套断言必失败;
  G 联合E2E(§FIX4-06): 正常合格研究发布四对象基线→"未认证但新鲜"场景经
    正式证据核验进入观点/论点状态更新(独立合成状态文件,不冒充污染)→
    未来发布负向场景(证据层拒+状态保持+提案留档)→已发布历史与长期状态保护。
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
import fact_engine as fe                       # noqa: E402
import data_validator as dv                    # noqa: E402
import snapshot_builder as sb                  # noqa: E402
import research_provenance as rp               # noqa: E402
import data_assembler as da                    # noqa: E402
import report_generator as rg                  # noqa: E402
import allocation_engine as ae                 # noqa: E402

DAY = '20261024'
AS_OF = '2026-10-24'
AS_OF_TS = '2026-10-24T08:00:00+08:00'
CPI_KEY = 'macro.data.CPI.value'
CORE_KEY = 'macro.data.CORE_CPI.value'
UNE_KEY = 'macro.data.UNEMPLOYMENT.value'
TIPS_KEY = 'macro.data.TIPS_10Y.value'
CPI_OBS = '2026-09-01'
# FIX4-04固定反例时间参(与FIX3同源,口径一致)
REL1 = '2026-10-24'                       # 反例1: date-only发布
AS_OF1 = '2026-10-25T08:00:00+08:00'      # 反例1: aware截止(=10-25T00:00Z)
REL2 = '2026-10-24T23:59:00'              # 反例2: naive发布
AS_OF2 = '2026-10-26T00:00:00+14:00'      # 反例2: aware截止+14:00(=10-25T10:00Z)
REL3 = '2026-10-24T20:00:00+08:00'        # 反例3: aware发布(=10-24T12:00Z)
AS_OF3 = '2026-10-24T08:00:00+08:00'      # 反例3: aware截止(=10-24T00:00Z)
TODAY = '2026-10-25'                      # 正式回写日(date-only研究截止)
PASS_N, FAIL_N = 0, 0
_TMPD = tempfile.mkdtemp(prefix='w2fix4-')


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
        return ('# 投资周报(SYNTHETIC测试文本·W2-FIX4)\n\n'
                + '本周市场综述与分资产回顾。' * 60)


def build_day(mutate_macro=None, ymd=DAY, root=None, as_of=None):
    """真实链路一天(fixt采集→真实sb.build_snapshot),返回(root, daily, snap)。"""
    td = root or tempfile.mkdtemp(prefix='w2fix4-day-', dir=_TMPD)
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
print("IA-P0-2-W2-FIX4: 点时认证状态传递到正式证据/统计/持久化(DEF-001)")
print("═" * 72)

# ══ A. 接口完备性+FIX4-04固定反例(真实模块) ═══════════════════════════
print("\n[A] 接口完备性+固定反例: 结构化时间资格随证据传递,两维度不互冒充")

anc1 = {CPI_KEY: {'value': 316.0, 'obs_date': CPI_OBS, 'release_date': REL1}}
q1 = dv.anchor_time_qualification(CPI_KEY, anc1[CPI_KEY], AS_OF1)
check("A0 dv适配接口结构(FIX4-01): 四段返回(identity/observation_freshness/"
      "point_in_time/point_in_time_certified),pit四键齐备,身份MAPPED——"
      "全部复用fp共享原语,无第二套比较器",
      set(q1) == {'identity', 'observation_freshness', 'point_in_time',
                  'point_in_time_certified'}
      and set(q1['point_in_time']) == {'status', 'granularity',
                                       'release_date', 'reason'}
      and q1['identity']['status'] == 'MAPPED'
      and q1['point_in_time']['status'] == 'POINT_IN_TIME_UNCERTIFIED'
      and q1['point_in_time_certified'] is False,
      str(q1)[:90])

ev1 = [{'metric': CPI_KEY, 'value': 316.0, 'obs_date': CPI_OBS,
        'mechanism': '通胀'}]
ver1, rej1 = ae.verify_evidence_items(ev1, anc1, AS_OF1)
check("A1 反例1(date-only发布10-24×aware截止10-25T08+08,obs 09-01,value"
      " 316.0): FRESH+POINT_IN_TIME_UNCERTIFIED——verify不丢弃(进verified),"
      "逐项携带observation_freshness/pit{status,granularity=DAY,release_date,"
      "reason}/certified=False;星级统计不宣称认证(已认证0·未认证1)",
      len(ver1) == 1 and not rej1
      and ver1[0]['observation_freshness'] == 'FRESH'
      and ver1[0]['point_in_time']['status'] == 'POINT_IN_TIME_UNCERTIFIED'
      and ver1[0]['point_in_time']['granularity'] == 'DAY'
      and ver1[0]['point_in_time']['release_date'] == REL1
      and ver1[0]['point_in_time']['reason']
      and ver1[0]['point_in_time_certified'] is False
      and '支持项1中已认证0·未认证1' in ae.star_level_from_evidence(ver1)[1],
      f"ver={len(ver1)} rej={len(rej1)} "
      f"pit={ver1[0]['point_in_time'] if ver1 else None}")

anc2 = {CORE_KEY: {'value': 306.0, 'obs_date': CPI_OBS, 'release_date': REL2}}
ev2 = [{'metric': CORE_KEY, 'value': 306.0, 'obs_date': CPI_OBS,
        'mechanism': '通胀'}]
ver2, rej2 = ae.verify_evidence_items(ev2, anc2, AS_OF2)
check("A2 反例2(naive发布10-24T23:59×aware截止10-26T00:00+14:00): 不认证"
      "(POINT_IN_TIME_UNCERTIFIED经UNVERIFIED_TZ)且**精度与拒证理由保留到"
      "正式接口**——verified项pit.reason含时区不确定披露,granularity=DAY",
      len(ver2) == 1 and not rej2
      and ver2[0]['point_in_time']['status'] == 'POINT_IN_TIME_UNCERTIFIED'
      and ver2[0]['point_in_time_certified'] is False
      and ver2[0]['point_in_time']['granularity'] == 'DAY'
      and '时区' in (ver2[0]['point_in_time']['reason'] or ''),
      str(ver2[0]['point_in_time'])[:90] if ver2 else 'rejected')

anc3 = {CPI_KEY: {'value': 316.0, 'obs_date': CPI_OBS, 'release_date': REL3}}
ev3 = [{'metric': CPI_KEY, 'value': 316.0, 'obs_date': CPI_OBS,
        'mechanism': '通胀'}]
ver3, rej3 = ae.verify_evidence_items(ev3, anc3, AS_OF3)
q3 = dv.anchor_time_qualification(CPI_KEY, anc3[CPI_KEY], AS_OF3)
check("A3 反例3(aware发布10-24T20:00+08=12:00Z晚于aware截止10-24T08:00+08="
      "00:00Z): NOT_AVAILABLE_AT_AS_OF→**整项拒收**(不进verified,不得入"
      "qualified支持集,不能支撑评级/星级/论点升级);拒收原因如实为'点时不可得"
      "…晚于研究截止',适配接口fresh=False",
      ver3 == [] and len(rej3) == 1
      and '点时不可得' in rej3[0][0] and '晚于研究截止' in rej3[0][0]
      and q3['observation_freshness']['fresh'] is False
      and q3['observation_freshness']['status'] == 'NOT_AVAILABLE_AT_AS_OF',
      f"ver={len(ver3)} rej={rej3[0][0][:60] if rej3 else None}")

anc4 = {UNE_KEY: {'value': 4.2, 'obs_date': CPI_OBS,
                  'release_date': '2026-10-23T20:00:00+08:00'}}
ev4 = [{'metric': UNE_KEY, 'value': 4.2, 'obs_date': CPI_OBS,
        'mechanism': '增长'}]
ver4, rej4 = ae.verify_evidence_items(ev4, anc4, AS_OF3)
check("A4 正向对照(双aware,发布10-23T20:00+08早于截止10-24T08:00+08): 正常"
      "核验+完整资格认证(certified=True,granularity=INSTANT,理由保留来源限度"
      "'未独立核验')——不无据拒收,亦不冒充外部独立认证",
      len(ver4) == 1 and not rej4
      and ver4[0]['point_in_time_certified'] is True
      and ver4[0]['point_in_time']['granularity'] == 'INSTANT'
      and '未独立核验' in ver4[0]['point_in_time']['reason'],
      str(ver4[0]['point_in_time'])[:80] if ver4 else 'rejected')

anc5 = {CPI_KEY: {'value': 316.0, 'obs_date': CPI_OBS}}
ver5, rej5 = ae.verify_evidence_items(ev1, anc5, AS_OF1)
check("A5 历史兼容(锚点缺release_date): RELEASE_UNKNOWN——现有当前分析照常"
      "运行(不拒收,观测层参与)且绝不伪造认证(certified=False,理由如实标注)",
      len(ver5) == 1 and not rej5
      and ver5[0]['point_in_time']['status'] == 'RELEASE_UNKNOWN'
      and ver5[0]['point_in_time_certified'] is False
      and ver5[0]['point_in_time']['reason'],
      str(ver5[0]['point_in_time'])[:80] if ver5 else 'rejected')

ver6, rej6 = ae.verify_evidence_items(ev1, anc5, None)
check("A6 诊断路径(未提供研究截止as_of): 不做时效门禁(既有语义)但**绝不默认"
      "授予点时认证**——pit=AS_OF_UNKNOWN,certified=False",
      len(ver6) == 1 and not rej6
      and ver6[0]['point_in_time']['status'] == 'AS_OF_UNKNOWN'
      and ver6[0]['point_in_time_certified'] is False,
      str(ver6[0]['point_in_time'])[:70] if ver6 else 'rejected')

# ══ B. 正式传播(真实模块: dv→ae→切分→星级→last_change→台账→rg论点) ══
print("\n[B] 正式传播: 认证级别流入状态记录与持久化台账")

# 混合集(研究截止=date-only 10-25,与正式回写today_iso同形态):
#   CPI  发布09-20(双date-only)→DAY粒度已认证;CORE/UNE发布为naive时间戳
#   ×date-only截止→UNVERIFIED_TZ未认证(观测新鲜照常)
ANC_MIX = {
    CPI_KEY: {'value': 316.0, 'obs_date': CPI_OBS, 'release_date': '2026-09-20',
              'as_of': TODAY},
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
verB, rejB = ae.verify_evidence_items(EV_MIX, ANC_MIX, TODAY)
supB, conB, unxB, neuB = ae.split_evidence_direction(verB)
starB, descB = ae.star_level_from_evidence(verB)
check("B1 传播起点verify: 3项全过数值/观测核验,认证分解=已认证1(CPI,DAY)/"
      "未认证2(CORE,UNE,UNVERIFIED_TZ)——分离不改变核验结果本身",
      len(verB) == 3 and not rejB
      and sum(1 for i in verB if i['point_in_time_certified']) == 1
      and next(i for i in verB if i['metric'] == CPI_KEY)
      ['point_in_time']['granularity'] == 'DAY'
      and all(i['point_in_time']['status'] == 'POINT_IN_TIME_UNCERTIFIED'
              for i in verB if i['metric'] in (CORE_KEY, UNE_KEY))
      and len(supB) == 3 and starB == 3
      and '支持项3中已认证1·未认证2(未认证按观测层证据参与)' in descB,
      f"star={starB} desc={descB[:80]}")

VWF = os.path.join(_TMPD, 'alloc_views_B.json')
open(VWF, 'w', encoding='utf-8').write(json.dumps({
    'version': 2, 'views': [{'id': 901, 'asset': '美债', 'rating': '标配',
                             'confidence': 1,
                             'key_metrics': [CPI_KEY],
                             'history': [], 'proposals': []}],
    'predictions': []}, ensure_ascii=False))
REP_B = ('<!--ALLOCATION_STATUS\n'
         + json.dumps({'id': 901, 'rating': '低配', 'confidence': 3,
                       'note': '通胀回落就业走弱',
                       'evidence': EV_MIX}, ensure_ascii=False)
         + '\nALLOCATION_STATUS-->')
updB = quiet(ae.update_allocation_status, REP_B, views_path=VWF,
             anchors=ANC_MIX, today_str=TODAY)
savedB = json.load(open(VWF, encoding='utf-8'))
vB = next(v for v in savedB['views'] if v['id'] == 901)
ledB = vB.get('evidence_ledger', [])[-1]
check("B2 观点状态更新(ae.update_allocation_status真实路径): 评级经证据路径"
      "变更(门槛不变: 3新增≥2);last_change.via可见未认证参与('未完成点时认证'"
      "+'观测层'),**不宣称'已完成点时认证'**;last_change.evidence逐项保留认证"
      "状态(pit dict+certified布尔)",
      vB['rating'] == '低配'
      and '未完成点时认证' in vB['last_change']['via']
      and '观测层' in vB['last_change']['via']
      and '点时认证' not in vB['last_change']['via'].replace('未完成点时认证', '')
      and all(('point_in_time' in e and 'point_in_time_certified' in e)
              for e in vB['last_change']['evidence'])
      and any(e['point_in_time_certified'] is False
              for e in vB['last_change']['evidence']),
      str(vB.get('last_change', {}).get('via'))[:90])
check("B3 观点证据台账持久化: point_time_certified=1/point_time_uncertified=2"
      "(verified全集口径),verified=3/supporting=3(计数不被新字段重复计入),"
      "desc含认证分解",
      ledB.get('point_time_certified') == 1
      and ledB.get('point_time_uncertified') == 2
      and ledB.get('verified') == 3 and ledB.get('supporting') == 3
      and '已认证1·未认证2' in ledB.get('desc', ''),
      str({k: ledB.get(k) for k in ('verified', 'point_time_certified',
                                    'point_time_uncertified')}))

THF = os.path.join(_TMPD, 'thesis_B.json')
open(THF, 'w', encoding='utf-8').write(json.dumps({
    'version': 1, 'updated_at': '2026-10-24T08:00:00',
    'theses': [{'id': 901, 'name': '通胀回落论', 'status': '进行中',
                'confidence': 1, 'related_theses': [], 'history': []}]},
    ensure_ascii=False))
REP_T = ('<!--THESIS_STATUS\n'
         + json.dumps({'id': 901, 'status': '已验证', 'confidence': 3,
                       'note': '两期数据确认',
                       'evidence': EV_MIX}, ensure_ascii=False)
         + '\nTHESIS_STATUS-->')
updT = quiet(rg.update_thesis_status, REP_T, thesis_path=THF,
             today_str=TODAY, anchors=ANC_MIX)
savedT = json.load(open(THF, encoding='utf-8'))
tB = next(t for t in savedT['theses'] if t['id'] == 901)
ledT = tB.get('evidence_ledger', [])[-1]
check("B4 论点状态更新(rg.update_thesis_status真实路径): ≥2新增支持证据门槛"
      "不变照常通过(观测层),last_change.via含未认证披露,last_change.evidence"
      "逐项带认证状态,台账持久化认证计数(1/2)与观点同构",
      tB['status'] == '已验证'
      and '未完成点时认证' in tB['last_change']['via']
      and all(('point_in_time' in e and 'point_in_time_certified' in e)
              for e in tB['last_change']['evidence'])
      and ledT.get('point_time_certified') == 1
      and ledT.get('point_time_uncertified') == 2,
      f"status={tB['status']} via={tB.get('last_change', {}).get('via', '')[:70]}")

# ══ C. 计数纪律 ═══════════════════════════════════════════════════════
print("\n[C] 计数纪律: 未认证不得计入已认证;披露字段不重复计数;既有去重保持")

ANC_U = {
    CORE_KEY: {'value': 306.0, 'obs_date': CPI_OBS,
               'release_date': '2026-10-24T23:59:00', 'as_of': TODAY},
    UNE_KEY: {'value': 4.2, 'obs_date': CPI_OBS,
              'release_date': '2026-10-24T20:00:00', 'as_of': TODAY},
    'macro.data.CORE_CPI.prev': {'value': 305.2, 'obs_date': CPI_OBS,
                                 'release_date': '2026-10-24T23:59:00',
                                 'as_of': TODAY},
    TIPS_KEY: {'value': 2.31, 'obs_date': '2026-10-24', 'as_of': TODAY},
}
EV_U = [
    {'metric': CORE_KEY, 'value': 306.0, 'obs_date': CPI_OBS, 'mechanism': '通胀'},
    {'metric': UNE_KEY, 'value': 4.2, 'obs_date': CPI_OBS, 'mechanism': '增长'},
    {'metric': 'macro.data.CORE_CPI.prev', 'value': 305.2, 'obs_date': CPI_OBS,
     'mechanism': '通胀'},
    {'metric': TIPS_KEY, 'value': 2.31, 'obs_date': '2026-10-24',
     'mechanism': '利率与流动性', 'contrary': True},
    {'metric': TIPS_KEY, 'value': 2.31, 'obs_date': '2026-10-24',
     'mechanism': '利率与流动性', 'neutral': True},
]
verC, rejC = ae.verify_evidence_items(EV_U, ANC_U, TODAY)
starC, descC = ae.star_level_from_evidence(verC)
supC, conC, unxC, neuC = ae.split_evidence_direction(verC)
check("C1 两项有效但未认证证据(CORE/UNE两基底,含.prev重复项): 均不计入已认证"
      "(certified计0),按观测层参与时记录写明观测层(desc明确'未认证按观测层"
      "证据参与'),verified=5/supporting=3——新披露字段不产生任何重复计数",
      len(verC) == 5 and not rejC
      and sum(1 for i in verC if i['point_in_time_certified']) == 0
      and '支持项3中已认证0·未认证3(未认证按观测层证据参与)' in descC
      and len(supC) == 3 and len(conC) == 1 and len(neuC) == 1,
      f"star={starC} desc={descC[:90]}")
check("C2 既有身份/去重规则原样保持: CORE_CPI.prev与CORE_CPI同基底只计1项"
      "(star按distinct base=2→2★门槛不降);反证不进支持数;中立不计入;"
      "同ISO周多证据=1个观察期;未解释反证封顶规则未动",
      starC == 2 and 'CORE_CPI' in descC
      and ae._base_metric('macro.data.CORE_CPI.prev') == ae._base_metric(CORE_KEY)
      and len({ae._obs_period_bucket(i['obs_date']) for i in supC}) == 1,
      f"star={starC}")

# ══ D. 失败防护 ═══════════════════════════════════════════════════════
print("\n[D] 失败防护: 未来发布/身份/非法日期/过期拒绝;校验缺席fail-closed")

ancD = {CPI_KEY: {'value': 316.0, 'obs_date': CPI_OBS,
                  'release_date': '2026-10-29', 'as_of': TODAY},
        CORE_KEY: {'value': 306.0, 'obs_date': CPI_OBS,
                   'metric_id': 'CPI', 'as_of': TODAY},
        'global_market.data.CPI.close': {'value': 316.0, 'obs_date': CPI_OBS,
                                         'metric_id': 'CPI', 'as_of': TODAY},
        UNE_KEY: {'value': 4.2, 'obs_date': '2026-02-30', 'as_of': TODAY},
        TIPS_KEY: {'value': 2.31, 'obs_date': '2026-06-01', 'as_of': TODAY}}
evD = [
    {'metric': CPI_KEY, 'value': 316.0, 'obs_date': CPI_OBS, 'mechanism': '通胀'},
    {'metric': CORE_KEY, 'value': 306.0, 'obs_date': CPI_OBS, 'mechanism': '通胀'},
    {'metric': 'global_market.data.CPI.close', 'value': 316.0,
     'obs_date': CPI_OBS, 'mechanism': '通胀'},
    {'metric': UNE_KEY, 'value': 4.2, 'obs_date': CPI_OBS, 'mechanism': '增长'},
    {'metric': TIPS_KEY, 'value': 2.31, 'obs_date': '2026-06-01',
     'mechanism': '利率与流动性'},
]
verD, rejD = ae.verify_evidence_items(evD, ancD, TODAY)
_reasons = ' | '.join(r for r, _ in rejD)
check("D1 拒收族: 未来发布(date-only 10-29>10-25)→点时不可得;身份冲突"
      "(CORE键自称metric_id=CPI)与来源家族伪装(global_market键自称CPI)→"
      "身份不可认证;非法观测日(2026-02-30)与过期(2026-06-01滞后>窗)→拒;"
      "五项全拒,verified为空",
      verD == [] and len(rejD) == 5
      and '点时不可得' in _reasons and '身份不可认证' in _reasons
      and ('无有效观测日' in _reasons or '不可解析' in _reasons)
      and '数据过期' in _reasons,
      _reasons[:160])
verD2, rejD2 = ae.verify_evidence_items(
    [{'metric': CPI_KEY, 'value': 316.0, 'obs_date': CPI_OBS,
      'mechanism': '通胀'}],
    {CPI_KEY: {'value': 316.0, 'obs_date': CPI_OBS}}, '2026-10-25BAD')
check("D2 非法研究截止: '2026-10-25BAD'→整项拒('研究截止非法'),不得默认认证",
      verD2 == [] and rejD2 and '研究截止非法' in rejD2[0][0],
      rejD2[0][0][:60] if rejD2 else None)
with mock.patch.dict(sys.modules, {'data_validator': None}):
    verD3, rejD3 = ae.verify_evidence_items(
        [{'metric': CPI_KEY, 'value': 316.0, 'obs_date': CPI_OBS,
          'mechanism': '通胀'}],
        {CPI_KEY: {'value': 316.0, 'obs_date': CPI_OBS}}, TODAY)
    freshD3 = ae._anchor_fresh(CPI_KEY, {'value': 316.0, 'obs_date': CPI_OBS},
                               TODAY)
check("D3 时间校验模块模拟不可用(sys.modules阻断import): verify fail-closed"
      "全部拒('时间校验模块不可用'),_anchor_fresh=False——旧ImportError分支"
      "返回True的静默授权已被废除,校验缺席不得放行正式证据",
      verD3 == [] and rejD3 and '时间校验模块不可用' in rejD3[0][0]
      and freshD3 is False,
      f"ver={len(verD3)} fresh={freshD3} "
      f"{rejD3[0][0][:50] if rejD3 else None}")
verD4, rejD4 = ae.verify_evidence_items(
    [{'metric': CPI_KEY, 'value': 316.0, 'obs_date': CPI_OBS,
      'mechanism': '通胀'}],
    {CPI_KEY: {'value': 316.0, 'obs_date': CPI_OBS}}, TODAY)
check("D4 还原校验: 模块恢复后同输入正常核验(无残留污染)",
      len(verD4) == 1 and verD4[0]['point_in_time']['status'] == 'RELEASE_UNKNOWN',
      str(verD4[0]['point_in_time'])[:60] if verD4 else 'rejected')

# ══ E. 历史兼容 ═══════════════════════════════════════════════════════
print("\n[E] 历史兼容: 无release研究照常运行;旧记录缺字段按未认证读")

ANC_E = {CPI_KEY: {'value': 316.0, 'obs_date': CPI_OBS, 'as_of': TODAY},
         CORE_KEY: {'value': 306.0, 'obs_date': CPI_OBS, 'as_of': TODAY},
         UNE_KEY: {'value': 4.2, 'obs_date': CPI_OBS, 'as_of': TODAY}}
EV_E = [
    {'metric': CPI_KEY, 'value': 316.0, 'obs_date': CPI_OBS, 'mechanism': '通胀'},
    {'metric': CORE_KEY, 'value': 306.0, 'obs_date': CPI_OBS, 'mechanism': '通胀'},
    {'metric': UNE_KEY, 'value': 4.2, 'obs_date': CPI_OBS, 'mechanism': '增长'},
]
VWF_E = os.path.join(_TMPD, 'alloc_views_E.json')
open(VWF_E, 'w', encoding='utf-8').write(json.dumps({
    'version': 2, 'views': [{'id': 902, 'asset': '黄金', 'rating': '标配',
                             'confidence': 1, 'history': [],
                             'proposals': [],
                             # 旧版台账: 无点时认证字段(历史记录原样)
                             'evidence_ledger': [{'date': '2026-09-25',
                                                  'verified': 1,
                                                  'obs_pairs':
                                                  [[CPI_KEY, CPI_OBS]]}]}],
    'predictions': []}, ensure_ascii=False))
REP_E = ('<!--ALLOCATION_STATUS\n'
         + json.dumps({'id': 902, 'rating': '超配', 'confidence': 2,
                       'note': '通胀企稳',
                       'evidence': EV_E}, ensure_ascii=False)
         + '\nALLOCATION_STATUS-->')
quiet(ae.update_allocation_status, REP_E, views_path=VWF_E,
      anchors=ANC_E, today_str=TODAY)
savedE = json.load(open(VWF_E, encoding='utf-8'))
vE = next(v for v in savedE['views'] if v['id'] == 902)
ledE = vE['evidence_ledger']
check("E1 无release_date研究(全部RELEASE_UNKNOWN): 当前分析照常运行——评级"
      "经观测层证据路径变更(新增≥2: CPI为旧台账已知观测不计新增,CORE/UNE计),"
      "认证级别如实(台账certified=0/uncertified=3,via披露未认证),旧台账记录"
      "原样保留在队首(不回填不批量改写)",
      vE['rating'] == '超配'
      and ledE[0].get('point_time_certified') is None   # 旧记录未被动过
      and ledE[-1]['point_time_certified'] == 0
      and ledE[-1]['point_time_uncertified'] == 3
      and sorted(ledE[-1]['new_support']) == ['macro.data.CORE_CPI',
                                              'macro.data.UNEMPLOYMENT']
      and '未完成点时认证' in vE['last_change']['via'],
      f"rating={vE['rating']} via={vE['last_change']['via'][:70]}")
_legacy_ev = [{'metric': CPI_KEY, 'value': 316.0, 'obs_date': CPI_OBS}]
check("E2 旧证据记录缺认证字段→按未认证读(不推定已认证): uncertified_note"
      "对旧形态非空;对新形态已认证项为空串(不虚报限制)",
      ae.uncertified_note(_legacy_ev) != ''
      and ae.uncertified_note([{'metric': UNE_KEY, 'value': 4.2,
                                'obs_date': CPI_OBS,
                                'point_in_time_certified': True}]) == '',
      repr(ae.uncertified_note(_legacy_ev))[:60])

# ══ F. 敏感性(删除字段/重计为已认证→本套必失败) ═════════════════════
print("\n[F] 敏感性: 删除点时字段或把未认证重计为已认证→B/C断言必失败")

_stripped = [{k: v for k, v in copy.deepcopy(e).items()
              if k not in ('point_in_time', 'point_in_time_certified',
                           'observation_freshness')} for e in verB]
_starS, descS = ae.star_level_from_evidence(_stripped)
_tampered = copy.deepcopy(verB)
for e in _tampered:
    e['point_in_time_certified'] = True
_cert_tamp = sum(1 for i in _tampered if i.get('point_in_time_certified'))
_cert_real = sum(1 for i in verB if i.get('point_in_time_certified'))
check("F1 删除传播字段(模拟下游丢字段): 真实desc含'已认证1·未认证2',剥离后"
      "认证分解失真为'已认证0·未认证3'(已认证项也丢据降级)且台账计数表达式"
      "由1变0——B1/B3的desc与point_time_certified断言在剥离形态下必失败,"
      "证明检测依赖真实传播而非自证常量",
      '支持项3中已认证1·未认证2' in descB
      and '已认证1·未认证2' not in descS
      and '支持项3中已认证0·未认证3' in descS
      and sum(1 for i in _stripped if i.get('point_in_time_certified')) == 0,
      f"real={descB[-40:]} stripped={descS[-40:]}")
check("F2 篡改重计(未认证项certified强改True): 台账计数表达式由真实1变3"
      "(≠真实1)——B3的point_time_certified==1断言在篡改形态下必失败",
      _cert_real == 1 and _cert_tamp == 3 and _cert_tamp != _cert_real,
      f"real={_cert_real} tampered={_cert_tamp}")

# ══ G. 联合E2E(FIX4-06): 四对象保护+未认证场景经正式入口 ══════════════
print("\n[G] 联合E2E: 正常发布四对象基线→未认证经正式核验→负向拒→历史保护")

GROOT = tempfile.mkdtemp(prefix='w2fix4-G-', dir=_TMPD)
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
check("G1 前置: 正常合格研究真实发布(exit0+GLM恰1次+四对象落盘)",
      _rcG == 0 and all(os.path.exists(p) for p in (REPG, STATG, THG, VWG))
      and _glmG.calls == 1, f"rc={_rcG} glm={_glmG.calls}")
baseG = {p: sha(p) for p in (REPG, STATG, THG, VWG)}
scanG = rp.scan_formal_weekly_reports(OUTG)

# G2: "未认证但新鲜"经正式证据核验进入状态更新——独立合成状态文件
# (采集端naive时间戳发布×date-only研究截止→UNVERIFIED_TZ,观测新鲜)
EATK = '20261025'
tdG2, dailyG2, snapG2 = build_day(
    ymd=EATK, root=tempfile.mkdtemp(prefix='w2fix4-G2-', dir=_TMPD),
    mutate_macro=lambda o: (o['data']['CPI'].update(
        release_date='2026-10-24T23:59:00'),
        o['data']['CORE_CPI'].update(release_date='2026-10-24T20:00:00')))
fcG2 = next(f for f in snapG2['facts'] if f['metric_id'] == 'CPI')
ancG2 = anchors_of(dailyG2, EATK)
check("G2a 真实快照链: 采集端naive时间戳发布→事实不FAIL(历史兼容)+INFO披露"
      "'点时未认证'+Gate A不受损+锚点如实透传release(不编造不剥离)",
      fcG2['quality_status'] != 'FAIL'
      and any('点时未认证' in i['message'] and i['severity'] == 'INFO'
              for i in fcG2['issues'])
      and snapG2['gate_a']['status'] in ('PASS', 'DEGRADED')
      and ancG2[CPI_KEY].get('release_date') == '2026-10-24T23:59:00',
      f"q={fcG2['quality_status']} gate={snapG2['gate_a']['status']} "
      f"rel={ancG2[CPI_KEY].get('release_date')}")
SYN_V = os.path.join(_TMPD, 'syn_views_G.json')
SYN_T = os.path.join(_TMPD, 'syn_thesis_G.json')
open(SYN_V, 'w', encoding='utf-8').write(json.dumps({
    'version': 2, 'views': [{'id': 910, 'asset': '美债', 'rating': '标配',
                             'confidence': 1, 'key_metrics': [CPI_KEY],
                             'history': [], 'proposals': []}],
    'predictions': []}, ensure_ascii=False))
open(SYN_T, 'w', encoding='utf-8').write(json.dumps({
    'version': 1, 'updated_at': '2026-10-24T08:00:00',
    'theses': [{'id': 910, 'name': '通胀回落', 'status': '进行中',
                'confidence': 1, 'related_theses': [], 'history': []}]},
    ensure_ascii=False))
EV_G2 = [
    {'metric': CPI_KEY, 'value': ancG2[CPI_KEY]['value'],
     'obs_date': ancG2[CPI_KEY]['obs_date'], 'mechanism': '通胀'},
    {'metric': CORE_KEY, 'value': ancG2[CORE_KEY]['value'],
     'obs_date': ancG2[CORE_KEY]['obs_date'], 'mechanism': '通胀'},
]
REP_G2 = ('<!--ALLOCATION_STATUS\n'
          + json.dumps({'id': 910, 'rating': '低配', 'confidence': 2,
                        'note': '通胀连续回落', 'evidence': EV_G2},
                       ensure_ascii=False)
          + '\nALLOCATION_STATUS-->\n<!--THESIS_STATUS\n'
          + json.dumps({'id': 910, 'status': '已验证', 'confidence': 2,
                        'note': '两期确认', 'evidence': EV_G2},
                       ensure_ascii=False)
          + '\nTHESIS_STATUS-->')
quiet(ae.update_allocation_status, REP_G2, views_path=SYN_V,
      anchors=ancG2, today_str='2026-10-25')
quiet(rg.update_thesis_status, REP_G2, thesis_path=SYN_T,
      today_str='2026-10-25', anchors=ancG2)
sV = json.load(open(SYN_V, encoding='utf-8'))
sT = json.load(open(SYN_T, encoding='utf-8'))
vv = next(v for v in sV['views'] if v['id'] == 910)
tt = next(t for t in sT['theses'] if t['id'] == 910)
check("G2b 未认证但新鲜经正式证据核验进入状态更新(独立合成状态文件,不冒充"
      "污染已发布四对象): 真实锚点→verify保留两项均为POINT_IN_TIME_"
      "UNCERTIFIED(certified=False);评级/论点状态按观测层证据照常更新且"
      "记录保留认证限度(via未认证披露+台账0/2)",
      vv['rating'] == '低配' and tt['status'] == '已验证'
      and all(e['point_in_time']['status'] == 'POINT_IN_TIME_UNCERTIFIED'
              and e['point_in_time_certified'] is False
              for e in vv['last_change']['evidence'])
      and '未完成点时认证' in vv['last_change']['via']
      and vv['evidence_ledger'][-1]['point_time_certified'] == 0
      and vv['evidence_ledger'][-1]['point_time_uncertified'] == 2
      and tt['evidence_ledger'][-1]['point_time_uncertified'] == 2,
      f"rating={vv['rating']} status={tt['status']} "
      f"led={vv['evidence_ledger'][-1].get('point_time_uncertified')}")

# G3: 未来发布负向场景(真实链路+证据层+状态保持)
FUT = '20261026'
tdG3, dailyG3, snapG3 = build_day(
    ymd=FUT, root=tempfile.mkdtemp(prefix='w2fix4-G3-', dir=_TMPD),
    mutate_macro=lambda o: o['data']['CPI'].update(release_date='2026-10-29'))
fcG3 = next(f for f in snapG3['facts'] if f['metric_id'] == 'CPI')
ancG3 = anchors_of(dailyG3, FUT)
_rcG3da = da_run(os.path.join(tdG3, 'data'), FUT)
_glmG3 = _GLM()
_appG3 = []
OUTG3 = os.path.join(tdG3, 'output', 'weekly')
os.makedirs(OUTG3, exist_ok=True)
_rcG3 = rg_run(rg_harness(_glmG3, _appG3, os.path.join(tdG3, 'data'),
                          OUTG3, FUT))
SYN_V3 = os.path.join(_TMPD, 'syn_views_G3.json')
open(SYN_V3, 'w', encoding='utf-8').write(json.dumps({
    'version': 2, 'views': [{'id': 911, 'asset': '美债', 'rating': '标配',
                             'confidence': 1, 'history': [], 'proposals': []}],
    'predictions': []}, ensure_ascii=False))
EV_G3 = [
    {'metric': CPI_KEY, 'value': ancG3[CPI_KEY]['value'],
     'obs_date': ancG3[CPI_KEY]['obs_date'], 'mechanism': '通胀'},
    {'metric': UNE_KEY, 'value': ancG3[UNE_KEY]['value'],
     'obs_date': ancG3[UNE_KEY]['obs_date'], 'mechanism': '增长'},
]
REP_G3 = ('<!--ALLOCATION_STATUS\n'
          + json.dumps({'id': 911, 'rating': '低配', 'confidence': 2,
                        'note': '未来发布数据', 'evidence': EV_G3},
                       ensure_ascii=False)
          + '\nALLOCATION_STATUS-->')
quiet(ae.update_allocation_status, REP_G3, views_path=SYN_V3,
      anchors=ancG3, today_str='2026-10-26')
sV3 = json.load(open(SYN_V3, encoding='utf-8'))
vv3 = next(v for v in sV3['views'] if v['id'] == 911)
check("G3 未来发布负向(真实链路): 事实FAIL(NOT_AVAILABLE)+Gate A不可用→"
      "数据包拒(exit2)+周报拒(exit2,GLM=0);证据层CPI拒收(点时不可得)→"
      "新增支持仅1项<2→评级变更被拒留档提案(reason含拒收原因),评级保持标配"
      "——不可得证据不得支撑评级/论点升级",
      fcG3['quality_status'] == 'FAIL'
      and any('NOT_AVAILABLE' in i['message'] for i in fcG3['issues'])
      and _rcG3da == 2 and _rcG3 == 2 and _glmG3.calls == 0
      and vv3['rating'] == '标配'
      and any('点时不可得' in (p.get('reason') or '')
              for p in vv3.get('proposals', [])),
      f"q={fcG3['quality_status']} da={_rcG3da} rg={_rcG3} "
      f"rating={vv3['rating']}")
afterG = {p: sha(p) for p in (REPG, STATG, THG, VWG)}
_newG = sorted(f for f in os.listdir(OUTG)
               if (f.startswith('weekly_report_')
                   or f.startswith('report_status_')) and DAY not in f)
_pubG = sorted(f for f in os.listdir(OUTG) if f.startswith('report_status_')
               and json.load(open(os.path.join(OUTG, f))).get('published')
               is True)
check("G4 已发布历史与长期状态保护: 攻击日后四对象SHA-256全程不变+无新报告"
      "/状态文件+published=true仅发布日+formal身份有效+scan不变——负向与"
      "未认证场景的全部合法写入只发生在独立合成状态文件",
      baseG == afterG and not _newG
      and _pubG == [f'report_status_{DAY}.json']
      and rp.formal_report_view(REPG)[0] is not None
      and [v['ymd'] for v in rp.scan_formal_weekly_reports(OUTG)]
      == [v['ymd'] for v in scanG],
      str({'changed': [k for k in baseG if baseG[k] != afterG[k]],
           'new': _newG}))

print("═" * 72)
print(f"W2-FIX4 结果: {PASS_N}通过 / {FAIL_N}失败")
sys.exit(1 if FAIL_N else 0)
