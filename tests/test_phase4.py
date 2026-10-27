#!/usr/bin/env python3
"""第七轮 Phase 4测试 — Gate B重建(全量覆盖/身份解析/待复核/fact_id)与
GLM输入纪律(数据包仅限当日)

数据纪律: 全部fixture为SYNTHETIC构造,临时目录运行,不写真实data目录。
运行: ~/AI内容/venv/bin/python3 tests/test_phase4.py
"""
import os
import sys
import io
import re
import json
import tempfile
import contextlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

PASS, FAIL = 0, 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")


def quiet(fn, *a, **kw):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        return fn(*a, **kw)


def anchors_fixture():
    """快照口径锚点(含fact_id溯源)。SPY=870作为'同族非canonical'锚点。"""
    def rec(v, obs='2026-10-16', fid=None, mid=None):
        return {'value': v, 'obs_date': obs, 'as_of': '2026-10-17',
                'source_file': 'research_snapshot_20261017.json',
                'metric_id': mid, 'fact_id': fid}
    return {
        'global_market.data.SPX.close': rec(7659.44, fid='SPX@2026-10-16', mid='SPX'),
        'global_market.data.SPY.close': rec(870.12, fid='SPY@2026-10-16', mid='SPY'),
        'global_market.data.GOLD.close': rec(4300.0, fid='GOLD_F@2026-10-16', mid='GOLD_F'),
        'global_market.data.GOLD.high': rec(4320.0, fid='GOLD_F@2026-10-16', mid='GOLD_F'),
        'global_market.data.GOLD.prev': rec(4200.0, fid='GOLD_F@2026-10-09', mid='GOLD_F'),
        'macro.data.UST_10Y.value': rec(4.28, fid='UST_10Y@2026-10-16', mid='UST_10Y'),
        'macro.data.UST_30Y.value': rec(4.89, fid='UST_30Y@2026-10-16', mid='UST_30Y'),
        'china.data.上证指数.close': rec(3716.28, fid='SHCOMP@2026-10-16', mid='SHCOMP'),
        'global_market.data.WTI.close': rec(71.5, fid='WTI_F@2026-10-16', mid='WTI_F'),
        'global_market.data.WTI.week_chg': rec(2.1, fid='WTI_F@2026-10-16', mid='WTI_F'),
        'global_market.data.GOLD.week_chg': rec(2.38, fid='GOLD_F@2026-10-16', mid='GOLD_F'),
    }


import data_validator as dv

print("=" * 60)
print("Phase 4: Gate B重建 + GLM输入纪律")
print("=" * 60)

# ══ [1] 全量覆盖: 第二处错误提及必须被抓(旧逻辑只查第一处) ═══
print("\n[1] 全量覆盖(不再首处即止)")
anchors = anchors_fixture()
with tempfile.TemporaryDirectory() as td:
    rp = os.path.join(td, 'weekly_report_20261017.md')
    # 第一处SPX正确(7659.44),第二处错(7500=上周值) — 旧report_matches[0]只查第一处
    open(rp, 'w').write(
        "# 周报\nSPX收于7659.44,创新高。UST 10Y收益率4.28%。\n"
        "回调场景: SPX收于7500。\n")
    warns = quiet(dv.validate_report, rp, anchors)
    check("第二处SPX错误被抓住(全量覆盖)",
          any('SPX' in w and '7500' in w for w in warns), str(warns))
    check("第一处正确值不误报",
          not any('报告=7659' in w for w in warns), str(warns))

# ══ [2] 身份解析: 不得按"最接近锚点"放行 ═══
print("\n[2] 身份纪律(SPX≠SPY)")
with tempfile.TemporaryDirectory() as td:
    rp = os.path.join(td, 'weekly_report_20261017.md')
    # SPX后面跟了SPY的价格870 — 数值上贴近SPY锚点(容差内),
    # 旧"取最接近锚点min|diff|"会拿SPY锚点放行或误判;新逻辑=疑似指标混淆
    open(rp, 'w').write("# 周报\nSPX收于870.12。\n")
    warns = quiet(dv.validate_report, rp, anchors)
    check("SPX位置写SPY价格→疑似指标混淆(🚨)",
          any('疑似指标混淆' in w and 'SPX' in w for w in warns), str(warns))

with tempfile.TemporaryDirectory() as td:
    rp = os.path.join(td, 'weekly_report_20261017.md')
    open(rp, 'w').write("# 周报\nSPX收于7,659.44。\n")   # 含千分位
    warns = quiet(dv.validate_report, rp, anchors)
    check("正确SPX通过(千分位归一)", not any('SPX' in w for w in warns), str(warns))

# ══ [3] 待复核: 不可核验如实披露,不静默跳过 ═══
print("\n[3] 待复核(不可核验≠跳过)")
partial = {k: v for k, v in anchors.items() if 'VIX' not in k}
with tempfile.TemporaryDirectory() as td:
    rp = os.path.join(td, 'weekly_report_20261017.md')
    open(rp, 'w').write("# 周报\nVIX收于15.2,恐慌情绪可控。BTC报97000。\n")
    warns = quiet(dv.validate_report, rp, partial)
    check("VIX无锚点→待复核(⚠️级)",
          any('待复核' in w and 'VIX' in w for w in warns), str(warns))
    check("BTC无锚点→待复核", any('待复核' in w and 'BTC' in w for w in warns))

# ══ [4] 前值/高点锚点不作为水平值依据 ═══
print("\n[4] 派生/前值锚点排除")
with tempfile.TemporaryDirectory() as td:
    rp = os.path.join(td, 'weekly_report_20261017.md')
    # 黄金写上周值4200(prev锚点)且无前值语境 → 应为偏差错误,不得被prev/high锚点放行
    open(rp, 'w').write("# 周报\n黄金收于4200.00。\n")
    warns = quiet(dv.validate_report, rp, anchors)
    check("黄金前值当现值→偏差错误(不被prev锚点放行)",
          any('黄金' in w and ('❌' in w or '🚨' in w) for w in warns), str(warns))

# ══ [5] 阈值/目标语境豁免(预测目标≠当期断言) ═══
print("\n[5] 阈值/目标语境")
with tempfile.TemporaryDirectory() as td:
    rp = os.path.join(td, 'weekly_report_20261017.md')
    open(rp, 'w').write("# 周报\nSPX收于7659.44。预测#3(SPX收复7900)未兑现。\n")
    warns = quiet(dv.validate_report, rp, anchors)
    check("预测目标7900不判为偏差(语境豁免)",
          not any('7900' in w for w in warns), str(warns))

# ══ [6] 变化率: 全量+canonical+旧键名兼容 ═══
print("\n[6] 周变化率")
with tempfile.TemporaryDirectory() as td:
    rp = os.path.join(td, 'weekly_report_20261017.md')
    open(rp, 'w').write("# 周报\nWTI周涨2.1%,黄金周涨2.38%。\n")
    warns = quiet(dv.validate_report, rp, anchors)
    check("WTI/黄金周变化通过(week_chg锚点)",
          not any('周涨跌' in w for w in warns), str(warns))
with tempfile.TemporaryDirectory() as td:
    rp = os.path.join(td, 'weekly_report_20261017.md')
    open(rp, 'w').write("# 周报\nWTI周涨5.2%(与锚点2.1偏差>0.6pp)。\n")
    warns = quiet(dv.validate_report, rp, anchors)
    check("WTI周变化超容差→❌", any('WTI周涨跌' in w for w in warns), str(warns))
# 旧采集格式键名(.change)兼容
old_style = {'global_market.data.WTI.change': {'value': 2.1, 'obs_date': '2026-10-16'}}
with tempfile.TemporaryDirectory() as td:
    rp = os.path.join(td, 'weekly_report_20261017.md')
    open(rp, 'w').write("# 周报\nWTI周涨2.1%。\n")
    warns = quiet(dv.validate_report, rp, old_style)
    check("旧.change键名兼容", not any('WTI周涨跌' in w for w in warns), str(warns))

# ══ [7] 机器块不参与散文扫描 ═══
print("\n[7] 状态块隔离")
with tempfile.TemporaryDirectory() as td:
    rp = os.path.join(td, 'weekly_report_20261017.md')
    open(rp, 'w').write(
        "# 周报\nSPX收于7659.44。\n<!--ALLOCATION_STATUS\n"
        '{"id":4,"rating":"低配","confidence":4,"note":"CCC高位"}\n'
        "ALLOCATION_STATUS-->\n")
    warns = quiet(dv.validate_report, rp, anchors)
    check("状态块内JSON数字不误报(id=4不是CCC值)",
          not any('CCC' in w for w in warns), str(warns))

# ══ [8] fact_id随锚点落盘+校验日志溯源 ═══
print("\n[8] fact_id溯源")
prim, others = dv.resolve_check_anchors(anchors, r'global_market.*(?:SPX|SPY).*(?:close)', 'SPX')
check("canonical解析到SPX(非SPY)", prim[0] == 'global_market.data.SPX.close', str(prim))
check("SPY落others(仅作混淆判定)", others and others[0][0].endswith('SPY.close'))
prim_g, _ = dv.resolve_check_anchors(anchors, r'global_market.*GOLD.*(?:close)', 'GOLD')
check("GOLD族排除prev/high只留close", prim_g[0].endswith('GOLD.close'), str(prim_g))
prim_c, _ = dv.resolve_check_anchors(anchors, r'china.*(?:上证|000001).*(?:close)',
                                     ('上证指数', '000001'))
check("上证canonical兼容标签与代码键名", prim_c and prim_c[0].endswith('上证指数.close'))

import snapshot_builder as sb
with tempfile.TemporaryDirectory() as td:
    # save_anchors保留fact_id/metric_id/quality(patch ROOT_DIR与today写临时目录)
    fake_anchor = {'global_market.data.SPX.close': {
        'value': 7659.44, 'source_file': 'x.json', 'as_of': '2026-10-17',
        'obs_date': '2026-10-16', 'fact_id': 'SPX@2026-10-16',
        'metric_id': 'SPX', 'quality': 'PASS', 'tolerance_pct': 1.0}}
    import unittest.mock as mock

    class _FakeDT:
        @staticmethod
        def now():
            class _N:
                @staticmethod
                def strftime(f):
                    return '20261017'
            return _N()

    with mock.patch.object(dv, 'ROOT_DIR', td), \
         mock.patch.object(dv, 'datetime', _FakeDT):
        dv.save_anchors(fake_anchor)
    saved = json.load(open(os.path.join(td, 'data', 'daily', 'anchors_20261017.json')))
    ent = saved.get('global_market.data.SPX.close', {})
    check("save_anchors保留fact_id/metric_id/quality",
          ent.get('fact_id') == 'SPX@2026-10-16' and ent.get('metric_id') == 'SPX'
          and ent.get('quality') == 'PASS', str(ent))

# ══ [9] GLM输入纪律: 数据包仅限当日 ═══
print("\n[9] report_generator.load_data_pack当日纪律")
import report_generator as rg
with tempfile.TemporaryDirectory() as td:
    weekly = os.path.join(td, 'weekly')
    os.makedirs(weekly)
    open(os.path.join(weekly, 'data_pack_20261015.md'), 'w').write('OLD')
    class _FakeDT2:
        @staticmethod
        def now():
            class _N:
                @staticmethod
                def strftime(f):
                    return '20261017'
            return _N()

    with mock.patch.object(rg, 'DATA_DIR', td), \
         mock.patch.object(rg, 'datetime', _FakeDT2):
        out = rg.load_data_pack()
    check("无当日包→拒绝(不回退旧包)", out is None)
    open(os.path.join(weekly, 'data_pack_20261017.md'), 'w').write('TODAY')
    # IA-P0-1修复: 原用例只在首次调用mock datetime,"当日"随真实日期漂移
    # (2026-10-17写死的用例10天后自然腐坏)——三次调用统一固定today=20261017
    with mock.patch.object(rg, 'DATA_DIR', td), \
         mock.patch.object(rg, 'datetime', _FakeDT2):
        out = rg.load_data_pack()
    check("当日包正常加载", out == 'TODAY')
    with mock.patch.object(rg, 'DATA_DIR', td):
        out = rg.load_data_pack('20261015')
    check("显式历史日期仍可加载(重生成历史报告)", out == 'OLD')

print("\n" + "=" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
