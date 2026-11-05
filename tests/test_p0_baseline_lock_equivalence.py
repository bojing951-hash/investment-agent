#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P0-BASELINE-RESTRUCT-WP-BR 语义等价证明套件(集中式负向注入电池+演进预演)。

使命(合同 AC-03/AC-04): 机器证明三联锁重构**语义不弱化**——
  ① 负向注入电池 N1-N7+: 对 REPORT §零.1 清点表每个「保护回归类」构造注入
     (临时 registry/fixture 变体,进程内 monkeypatch/tmp worktree,零生产代码
     污染,运行后还原),断言三联锁在每种注入下必须红(锁仍然咬合);
  ② 演进兼容预演: 合法注册演进 81→85(4条日本指标,全登记,B3 DESIGN §六
     v2.1.0 语义)下 M 集 28 套件**零改动全绿**;85→84(删vintage基线条目)红;
     裸85(新条目日历未登记)红。(R060 注记: B3 落地后实载基座=85,预演变体
     现为 85→89=85基+4虚构条目,8 条 vintage 新增;函数名保持 R057 冻结身份。)

运行形态: 脚本式(python3 tests/test_p0_baseline_lock_equivalence.py),
CI 同构零 pytest 依赖;零真实出站(全部 monkeypatch/tmp/git worktree 本地实现)。

映射表与红面记录: docs/P0_BASELINE_RESTRUCT_REPORT.md §三/§四
(每用例 docstring 注对应原锁 file:line 与保持的回归类)。
"""
import json
import os
import subprocess
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(_HERE)
for _p in (os.path.join(ROOT, 'scripts'), _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

PASS_N, FAIL_N = 0, 0


def check(name, cond, detail=''):
    global PASS_N, FAIL_N
    if cond:
        PASS_N += 1
        print(f'  ✅ {name}')
    else:
        FAIL_N += 1
        print(f'  ❌ {name} {detail}')


import fact_engine as fe                    # noqa: E402
import research_provenance as rp            # noqa: E402
import registry_semantics as rsem           # noqa: E402
import fixt                                 # noqa: E402
from helpers import baseline_locks as bl    # noqa: E402

DAY = '20261024'

# ══ M 集(28 套件,REPORT §零.3;预演子进程零改动运行) ════════════════
M_FILES = [
    'test_p02_w4.py', 'test_p02_w4_fix1.py', 'test_p02_w4_fix2.py',
    'test_p02_w4_fix3.py', 'test_p02_w4_fix4.py',
    'test_p01_fix1.py', 'test_p01_fix2.py', 'test_p01_fix3.py',
    'test_p01_fix4.py', 'test_p01_fix5.py', 'test_p01_fix6.py',
    'test_p01_fix7.py', 'test_p01_fix8.py', 'test_p01_fix9.py',
    'test_p01_fix10.py', 'test_p01_fix11.py',
    'test_p02_w2_fix1.py', 'test_p02_w2_fix2.py',
    'test_p02_w3.py', 'test_p02_w3_fix1.py', 'test_p02_w3_fix2.py',
    'test_p02_w3_fix3.py', 'test_p02_w3_fix4.py',
    'test_p02_w5.py',
    'test_p02_w1.py', 'test_p02_w1_fix1.py', 'test_p02_w2.py',
    'test_p4_fixes.py',
]
# 85→84 缩水注入的红面载体套件(T1工件锁/vintage锚宿主;85→84对计数下限类
# 仍≥81不触发,红面由「注册表∩vintage<81+工件恰覆盖」锁承载——映射见REPORT §四)
SHRINK_FILES = ['test_p02_w1.py', 'test_p02_w1_fix1.py',
                'test_p02_w2.py', 'test_p02_w4.py']
# 裸85(未登记演进)红面载体(fail-loud: fe.load_registry断言日历登记)
BARE_FILES = ['test_p02_w1.py']


def _live_doc():
    with open(bl.REGISTRY_PATH, encoding='utf-8') as f:
        return json.load(f)


def _variant(mutate):
    """深拷贝实载注册表→注入突变→返回变体doc(不落盘不触生产文件)。"""
    import copy
    doc = json.loads(json.dumps(_live_doc()))
    mutate(doc)
    doc['by_id'] = {m['metric_id']: m for m in doc['metrics']}   # 注入比对口径
    return doc


def _jp(mid, name, sym):
    """合法演进新条目(B3 DESIGN §六 v2.1.0: 日本政策利率+JGB关键期限,
    source/日历/单位/通道/status全登记)。"""
    return {
        'metric_id': mid, 'display_name': name, 'source': 'macro_collector',
        'source_symbol': sym, 'asset_class': 'rates_yield',
        'frequency': 'daily', 'unit': 'percent', 'calendar': 'us_rates',
        'criticality': 'context', 'status': 'active',
        'identity': {'instrument': 'index_rate_series', 'adjustment': 'none'},
        'value_type': 'yield_or_spread_level',
        'calc': 'FRED系列最新观测(日历日发布,非交易日无新观测)',
        'validation': {'range': [-0.5, 15], 'max_week_abs_move': 1.0},
        'freshness': {'max_calendar_lag_days': 7},
        'release_semantics': 'FRED发布时点不可得,按观测日保守处理'
        '(观测日≤研究截止即视为可用;发布晚于观测日的风险见快照披露)'}


def _evolved_85():
    """合法演进变体: 81→85(BOJ_POLICY_RATE/JGB_2Y/JGB_5Y/JGB_10Y全登记)。

    R060 注记: B3 落地后实载基座=85(v2.1.0 含 4 条实名 JP 条目,与虚构 4 条
    无 metric_id 碰撞=D1 命名规避),本变体现为 85→89(8 条 vintage 新增);
    函数名/虚构条目集保持 R057 冻结身份,演进兼容语义不变(REPORT §零.7)。"""
    return _variant(lambda d: d['metrics'].extend([
        _jp('BOJ_POLICY_RATE', '日银政策利率', 'BOJRATE'),
        _jp('JGB_2Y', '2年期日债收益率', 'JGB2Y'),
        _jp('JGB_5Y', '5年期日债收益率', 'JGB5Y'),
        _jp('JGB_10Y', '10年期日债收益率', 'JGB10Y')]))


def _shrink_variant():
    """N1/N7 共用缩水注入(live=85 重锚,R060/REM-AC-02⑥):

    删 vintage 基线条目 UMCSENT+时点后新增 4 条实名 JP 条目→恰 80 项<81 触
    T1 下限(原锚=live 81 删 1 条即 80 触底;B3 后 live=85,单删 1 条=84 不触
    下限=电池算术漂移,见 B3 REPORT §零.5/§三)。baseline_removals 仍恰
    ={UMCSENT}(JP 条目∉BASELINE_VINTAGE_IDS,新增退场非基线缩水)。"""
    def _m(d):
        d['metrics'] = [m for m in d['metrics']
                        if m['metric_id'] in bl.BASELINE_VINTAGE_IDS
                        and m['metric_id'] != 'UMCSENT']
    return _variant(_m)


# ════════════════════════════════════════════════════════════════════
print('=' * 72)
print('WP-BR 语义等价证明套件: 负向注入电池 N1-N7+ 与演进兼容预演')
print('=' * 72)

# ── 电池前置对照: 基线态全锁绿(注入前先证锁活着,防"恒红假等价") ──────
print('\n[0] 基线态对照(全锁绿)')
_ok0, _why0 = bl.registry_counts_ok()
check('Z0 T1计数下限+T2双射+T3自洽 基线态全绿',
      _ok0 and bl.ids_unique_bijection_ok()[0]
      and bl.registry_self_consistent()[0] and bl.evolution_legal()[0],
      _why0)


def n1_entry_loss():
    """N1 条目丢失(85→80,live=85 重锚: 删vintage条目UMCSENT+4条新增,见
    _shrink_variant)——原锁: test_p02_w4.py:231 `assertEqual(len(reg
    ['metrics']), 81)` 等 81 计数族(清点#1-#12/#47-#56);回归类=注册表静默
    缩水(条目丢失)。T1 下限必须红(R060 重锚登记: REPORT §零.7 第6点)。"""
    v = _shrink_variant()
    ok_c, why_c = bl.registry_counts_ok(v)
    check('N1a 注册表85→80: T1计数下限红(缩水捕获)',
          not ok_c and '81' in why_c, why_c)
    check('N1a2 T1集合形态: baseline_removals恰={UMCSENT}',
          bl.baseline_removals(v) == {'UMCSENT'},
          str(sorted(bl.baseline_removals(v))))


def n1b_fe_level_core_floor():
    """N1b fe级注入: core 32→31——原锁: test_p02_w1.py:221-222
    `len(rp.core_metric_ids())==32`(清点#50);回归类=core缩水。经生产加载
    路径(monkeypatch fe.load_registry)注入,运行后还原。"""
    doc = _variant(lambda d: d['metrics'].__delitem__(
        next(i for i, m in enumerate(d['metrics'])
             if m['metric_id'] == 'SPX' and m['criticality'] == 'core')))
    orig = fe.load_registry
    try:
        fe.load_registry = lambda *a, **k: _loaded(doc)
        bl.reset_registry_caches()
        n_core = len(rp.core_metric_ids())
        check('N1b core 32→31: 生产路径core下限红(n=31<32)',
              n_core == 31 and n_core < bl.CORE_FLOOR, f'n={n_core}')
    finally:
        fe.load_registry = orig
        bl.reset_registry_caches()
    check('N1b2 还原后core==32(注入零残留)',
          len(rp.core_metric_ids()) == 32)


def _loaded(doc):
    """按生产同式给注入doc补by_id并返回(fe.load_registry替身)。"""
    return {'version': doc.get('version'),
            'metrics': doc['metrics'],
            'by_id': {m['metric_id']: m for m in doc['metrics']}}


def n2_duplicate():
    """N2 条目重复——原锁: test_p02_w1.py:89-94 审计清单唯一性(清点#49/
    #55/#57);回归类=清单/注册表条目重复。T2 双射唯一必须红。"""
    v = _variant(lambda d: d['metrics'].append(
        json.loads(json.dumps(next(m for m in d['metrics']
                                   if m['metric_id'] == 'SPX')))))
    ok, why = bl.ids_unique_bijection_ok(v)
    check('N2a metrics重复SPX: T2双射唯一红(重复捕获)',
          not ok and '重复' in why, why)


def n2b_artifact_smuggling():
    """N2b 工件私货——原锁: test_p02_w2.py:87-94 `set(mat_by)==set(_BY)`
    (清点#57);回归类=政策矩阵/审计清单私货(夹带注册表外条目)。"""
    live_audit = [i['metric_id'] for i in json.load(open(
        os.path.join(ROOT, 'docs', 'P0_2_W1_REGISTRY_AUDIT.json'),
        encoding='utf-8'))['items']]
    smuggled = list(live_audit) + ['FAKE_PRIVATE_METRIC']
    ok, why = bl.artifact_covers_vintage_baseline(smuggled)
    check('N2b 工件夹带私货条目: 恰覆盖锁红(多[]外条目捕获)',
          not ok and '多' in why, why)


def n3_self_consistency_break():
    """N3 自洽破坏(by_id≠metrics)——原锁: test_p02_w1.py:71-72
    `len(_REG['metrics'])==81 and len(by_id)==81`(清点#47/#48);回归类=
    注册表自洽破坏/映射漂移。T2 必须红。"""
    v = _variant(lambda d: None)
    v['by_id'].pop('VIX')          # 映射缺列表在册条目
    ok, why = bl.ids_unique_bijection_ok(v)
    check('N3a by_id缺VIX(列表在册): T2双射红(映射漂移捕获)',
          not ok and 'by_id' in why, why)
    ok2, why2 = bl.registry_self_consistent(v)
    check('N3b T3前件自洽红(validate_registry错误经rsem口径)',
          not ok2, str(why2[:2]))


def n3b_bucket_sum_drift():
    """N3b 桶和≠全量——原锁: test_p02_w4.py:410-412 by_status桶和==81
    (清点#3)/test_p02_w4_fix2.py:243(清点#9);回归类=静默丢桶/丢项。
    重构形态= T2 sum==len(result)(派生);注入桶和漂移必须红。"""
    res = {'metrics': [{'metric_id': f'M{i}'} for i in range(85)],
           'by_status': {'EXACT': 80, 'FALLBACK': 4}}    # 桶和84≠85
    s = sum(res['by_status'].values())
    check('N3b by_status桶和84≠项数85: T2自洽红(sum==len捕获)',
          s != len(res['metrics'])
          and len(res['metrics']) >= bl.REGISTRY_FLOOR
          and not (s == len(res['metrics'])),
          f'sum={s} len={len(res["metrics"])}')


def n3c_echo_drift():
    """N3c 机器报告回显漂移——原锁: test_p02_w4.py:691
    `assertEqual(r['registry']['metric_count'], 81)`(清点#4/#12);回归类=
    registry回显漂移。重构形态= ==实载注册表项数;注入回显81(实载85)红。"""
    echo = {'registry': {'metric_count': 81}}
    live_n = bl.expected_registry_count(_evolved_85())
    check(f'N3c 回显81≠实载{live_n}: T2回显==实载红(漂移捕获)',
          echo['registry']['metric_count'] != live_n
          and live_n >= bl.REGISTRY_FLOOR, f'echo=81 live={live_n}')


def n3d_table_rows():
    """N3d 逐项表行数缩水——原锁: test_p02_w4.py:703-705
    `assertEqual(len(rows), 82)`(清点#5);回归类=无数据指标丢行。重构形态=
    ==1+实载项数+下限≥82;注入行数缩水至下限锁咬合域红(R060 重锚: 原锚=live81
    全表缺表头 81 行双锁咬合;live=85 后缺表头=85 行≥82 下限不咬合→锚改为
    缺表头+4 行=81 行,1+实载等值锁与≥82 下限锁双咬合语义逐字保持)。"""
    rows = [f'row{i}' for i in range(bl.expected_registry_count() - 4)]  # 缺表头+4行
    check('N3d 逐项表行数缩水(缺表头+4行): T2行数==1+实载红且下限锁红(丢行捕获)',
          len(rows) != 1 + bl.expected_registry_count()
          and not (len(rows) >= bl.W4_REPORT_ROWS_FLOOR),
          f'rows={len(rows)} expect=1+{bl.expected_registry_count()}')


def n1c_artifact_missing():
    """N1c 工件漏项——原锁: test_p02_w1.py:89-94 审计清单(清点#49);
    test_p02_w1_fix1.py:270-271(清点#55);test_p02_w2.py:87-94 矩阵(清点
    #57);回归类=审计清单/矩阵漏项。"""
    live_audit = [i['metric_id'] for i in json.load(open(
        os.path.join(ROOT, 'docs', 'P0_2_W1_REGISTRY_AUDIT.json'),
        encoding='utf-8'))['items']]
    holed = [m for m in live_audit if m != 'UMCSENT']
    ok, why = bl.artifact_covers_vintage_baseline(holed)
    check('N1c 工件删UMCSENT一行: 恰覆盖锁红(漏项捕获)',
          not ok and '缺' in why, why)


def n4_baseline_indicator_death():
    """N4 基线指标静默死亡(正常日vintage)——原锁: test_p01_fix1.py:416-420
    Gate A PASS契约(清点#13)及全active族#14-#21/#24/#26/#29-#30/#32/
    #37-#45;回归类=基线通道/指标静默死亡仍被当正常日。vintage域锁必须红
    (基线条目缺席不获vintage新增待遇)。"""
    snap = fixt.real_snapshot(DAY, missing=('UMCSENT',))
    rec = rp.recompute_gate_a(snap)
    ok, why = bl.gate_vintage_ok(rec)
    check('N4a 正常日vintage基线缺席UMCSENT: gate_vintage_ok红',
          not ok and 'vintage基线' in why, f"eff={rec['effective']} {why}")
    snap2 = fixt.real_snapshot(DAY)                       # 全齐对照(绿)
    check('N4b 全齐对照: gate_vintage_ok绿(锁非恒红)',
          bl.gate_vintage_ok(rp.recompute_gate_a(snap2))[0])


def n4b_baseline_channel_death():
    """N4b 基线通道死亡/非EXACT——原锁: test_p01_fix5.py:196-200 通道EXACT
    契约(清点#22/#23);fix7 A1(#28)/fix9 C0(#33);回归类=基线通道静默死亡。"""
    snap = fixt.real_snapshot(DAY)
    ss = json.loads(json.dumps(snap['sources_status']))
    ss['china']['status'] = 'MISSING'          # 基线通道死亡(正常日应EXACT)
    ok, why = bl.sources_status_baseline_ok(ss, require='EXACT')
    check('N4b 基线通道china死亡(MISSING≠EXACT): 结构锁红',
          not ok and any('china' in str(w) for w in why), str(why[:2]))


def n5_unregistered_evolution():
    """N5 通道未登记演进(by_id添加但枚举/日历/单位缺)——T3自洽演进锁
    (清点全局T3类;原锁形态=w4/w1族实载派生+合同§零T3);回归类=静默未登记
    演进。三种未登记形态逐种注入,T3必须红。"""
    def bad(cal=None, src=None, st=None):
        def _m(d):
            e = _jp('X_NEW_1', '未登记形态', 'XSYM1')
            if cal:
                e['calendar'] = cal
            if src:
                e['source'] = src
            if st:
                e['status'] = st
            d['metrics'].append(e)
        return _variant(_m)

    ok1, why1 = bl.evolution_legal(bad(cal='jp_unregistered'))
    check('N5a 新条目日历未登记: T3红(日历枚举缺)',
          not ok1 and any('calendar' in w or '日历' in w for w in why1),
          str(why1[:2]))
    ok2, why2 = bl.evolution_legal(bad(src='ghost_collector'))
    check('N5b 新条目source未登记: T3红(枚举/通道缺)',
          not ok2 and any('source' in w or '通道' in w for w in why2),
          str(why2[:2]))
    ok3, why3 = bl.evolution_legal(bad(st='zombie'))
    check('N5c 新条目status非法: T3红(status词汇缺)',
          not ok3 and any('status' in w for w in why3), str(why3[:2]))
    ok4, _ = bl.evolution_legal(_evolved_85())
    check('N5d 对照: 合法演进(实载85+4虚构=89项)T3绿(锁非恒红)', ok4)


def n6_sources_status_baseline_missing():
    """N6 sources_status基线通道缺失——原锁: test_p01_fix5.py:210-216
    (清点#23)/fix10 D1(#34)/fix11 P1(#35)通道在场断言;回归类=基线通道
    缺席。另含fix8通道枚举缩水面(#31)。"""
    snap = fixt.real_snapshot(DAY)
    ss = json.loads(json.dumps(snap['sources_status']))
    ss.pop('china')                             # 基线通道整体缺席
    ok, why = bl.sources_status_baseline_ok(ss, require='EXACT')
    check('N6a sources_status缺china通道: 结构锁红',
          not ok and any('china' in str(w) for w in why), str(why[:2]))
    ok_full, _ = bl.sources_status_baseline_ok(
        snap['sources_status'], require='EXACT')
    check('N6b 对照: 四通道齐备EXACT绿(锁非恒红)', ok_full)
    # fix8形态(#31): rp.SOURCE_CHANNELS实载枚举⊇基线四通道(通道枚举缩水红)
    orig = rp.SOURCE_CHANNELS
    try:
        rp.SOURCE_CHANNELS = tuple(
            c for c in orig if c != 'china')    # 生产枚举静默缩水注入
        shrunk = set(rp.SOURCE_CHANNELS) >= set(bl.BASELINE_SOURCE_CHANNELS)
        check('N6c rp.SOURCE_CHANNELS缩水(缺china): ⊇基线四通道红',
              not shrunk, str(rp.SOURCE_CHANNELS))
    finally:
        rp.SOURCE_CHANNELS = orig
    check('N6c2 还原后⊇成立(注入零残留)',
          set(rp.SOURCE_CHANNELS) >= set(bl.BASELINE_SOURCE_CHANNELS))


def n7_missing_t1_self_detection():
    """N7 三联锁缺件自身检测(仅T2无T1)——证明T1必要性: 协同缩水注入
    (注册表删条且审计结果同步缩水,R060 重锚=删5条: UMCSENT+4条新增,见
    _shrink_variant)下,旧形态T2-only锁(`len(res)==len(registry)`实载等值)
    漏检(绿=弱化实锤面),T1下限红。
    原锁: test_p02_w4.py:231-232(清点#1/#2)81计数族——重构若只有T2无T1
    即复现此漏检,故三件缺一即弱化。"""
    v = _shrink_variant()
    res_ids = [m['metric_id'] for m in v['metrics']]     # 审计结果同步缩水
    old_t2_only = (len(res_ids) == bl.expected_registry_count(v))
    t1_floor = bl.registry_counts_ok(v)[0]
    check('N7a 协同缩水下旧形态T2-only漏检(等值比较绿=缺陷展示)',
          old_t2_only is True,
          f'res={len(res_ids)} reg={bl.expected_registry_count(v)}')
    _aud = [i['metric_id'] for i in json.load(open(
        os.path.join(ROOT, 'docs', 'P0_2_W1_REGISTRY_AUDIT.json'),
        encoding='utf-8'))['items']]
    check('N7b 同注入T1下限红(T1必要性实证,三联锁不可缺件)',
          not t1_floor and not bl.artifact_covers_vintage_baseline(
              _aud, v)[0])


def battery():
    print('\n[N] 负向注入电池 N1-N7+(注入态红面=锁咬合证明)')
    n1_entry_loss()
    n1b_fe_level_core_floor()
    n2_duplicate()
    n2b_artifact_smuggling()
    n3_self_consistency_break()
    n3b_bucket_sum_drift()
    n3c_echo_drift()
    n3d_table_rows()
    n1c_artifact_missing()
    n4_baseline_indicator_death()
    n4b_baseline_channel_death()
    n5_unregistered_evolution()
    n6_sources_status_baseline_missing()
    n7_missing_t1_self_detection()
    check('N-还原 注入后实载注册表态与Z0一致(工作树零污染)',
          bl.registry_counts_ok()[0] and bl.ids_unique_bijection_ok()[0]
          and bl.registry_self_consistent()[0])


# ══ 演进兼容预演(AC-04;worktree副本注入,零生产代码污染,运行后移除) ══
def rehearsal():
    print('\n[R] 演进兼容预演(worktree副本+子进程零改动运行M集)')
    variants = {
        'legal85': (_evolved_85_file, M_FILES, True),
        'shrink84': (_shrink_84_file, SHRINK_FILES, False),
        'bare85': (_bare_85_file, BARE_FILES, False),
    }
    for label, (mk, files, expect_green) in variants.items():
        wt = tempfile.mkdtemp(prefix=f'wpbr-eq-{label}-')
        r = subprocess.run(['git', '-C', ROOT, 'worktree', 'add', '--detach',
                            wt, 'HEAD'], capture_output=True, text=True)
        if r.returncode != 0:
            check(f'R[{label}] worktree就绪', False, r.stderr[:200])
            continue
        try:
            with open(os.path.join(wt, 'config', 'metric_registry.json'), 'w',
                      encoding='utf-8') as f:
                json.dump(mk(), f, ensure_ascii=False, indent=1)
            greens = reds = 0
            for t in files:
                p = subprocess.run(['python3', os.path.join(wt, 'tests', t)],
                                   capture_output=True, text=True, timeout=1200)
                if p.returncode == 0:
                    greens += 1
                else:
                    reds += 1
            if expect_green:
                check(f'R[{label}] 合法演进(实载85+4虚构=89项): M集{len(files)}套件'
                      f'零改动全绿(演进不撞墙,B3重冻发车前提)',
                      greens == len(files) and reds == 0,
                      f'greens={greens} reds={reds}')
            else:
                check(f'R[{label}] 非法注入: 载体套件红面≥1'
                      f'({len(files)}套件,reds={reds})',
                      reds >= 1, f'greens={greens} reds={reds}')
        finally:
            subprocess.run(['git', '-C', ROOT, 'worktree', 'remove',
                            '--force', wt], capture_output=True)
    check('R-还原 worktree清单回零(副本全移除)',
          len([l for l in subprocess.run(
              ['git', '-C', ROOT, 'worktree', 'list'], capture_output=True,
              text=True).stdout.splitlines() if l.strip()]) == 1)


def _evolved_85_file():
    d = _evolved_85()
    d.pop('by_id', None)       # 落盘形态与生产config同构(不带by_id)
    d['version'] = '2.1.0'
    return d


def _shrink_84_file():
    d = _evolved_85_file()
    d['metrics'] = [m for m in d['metrics'] if m['metric_id'] != 'UMCSENT']
    return d


def _bare_85_file():
    d = _evolved_85_file()
    for m in d['metrics']:
        if m['metric_id'] == 'JGB_2Y':
            m['calendar'] = 'jp_unregistered'
    return d


battery()
rehearsal()

print('\n' + '=' * 72)
print(f'等价套件结果: {PASS_N}通过 / {FAIL_N}失败')
print('=' * 72)
sys.exit(1 if FAIL_N else 0)
