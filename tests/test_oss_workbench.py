#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""开源产品化 W5/W3(2026-11-08)回归套件。

覆盖:
① W5 工作台数据层(workbench_data): 概览行(缺失如实)/市场行/变化格式化/
   序列(快照series_store优先,japan单点如实报不支持)/研究问答状态面
   (越界=拒绝,未支持=如实,不猜映射)/GLM缺Key明确提示/研究档案append-only落档;
② W3 月/季自动级联默认关闭: report_generator源级守卫(IA_AUTO_MONTHLY)。
CI安全: 全部用合成快照/临时档案目录,不依赖本地data/(有真实快照时追加真档冒烟)。
"""
import copy
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

PASSED, FAILED = [], []


def check(name, cond, detail=''):
    (PASSED if cond else FAILED).append((name, detail))
    print(('  ✅ ' if cond else '❌ ') + name + (f' [{detail}]' if not cond and detail else ''))


import workbench_data as wd  # noqa: E402

# ── 合成快照(结构对照真实 research_snapshot_20261108.json 字段) ──
SYN_SNAP = {
    'snapshot_id': 'research_snapshot_20261108',
    'target_date': '2026-11-08', 'research_as_of': '2026-11-08T18:00:00+08:00',
    'gate_a': {'status': 'DEGRADED', 'core_missing': [],
               'noncore_missing': ['INDPRO'],
               'noncore_missing_detail': {'INDPRO': '来源文件在场而指标缺席(示意)'},
               'noncore_degraded': []},
    'sources_status': {},
    'facts': [
        {'fact_id': 'F1', 'metric_id': 'SPX', 'display_name': '标普500指数',
         'value': 7376.86, 'unit': 'index_point', 'value_type': 'level',
         'observation_date': '2026-11-06', 'as_of': '2026-11-08',
         'source': {'collector': 'global_market_collector', 'file': 'global_20261108.json'},
         'quality_status': 'PASS', 'issues': [],
         'derived': {'week': {'pct_change': -2.68}, 'mtd': {'pct_change': -2.68},
                     'ytd': {'pct_change': 7.76}}},
        {'fact_id': 'F2', 'metric_id': 'UMCSENT', 'display_name': '密歇根消费者信心',
         'value': 48.1, 'unit': 'index_point', 'value_type': 'level',
         'observation_date': '2026-09-30', 'as_of': '2026-11-08',
         'source': {'collector': 'macro_collector', 'file': 'macro_20261108.json'},
         'quality_status': 'DEGRADED', 'issues': ['观测滞后'],
         'derived': {'m1': {'pct_change': -6.96}}},
    ],
    'series_store': {'SPX': {'dates': ['2026-11-05', '2026-11-06'],
                             'values': [7581.0, 7376.86]}},
}

print('══ ① 工作台数据层 ══')
registry = wd.load_registry()
check('注册表加载(108项,与文件一致)', len(registry['metrics']) == 108,  # Charter7 P2-3: +SOFR/WALCL
      f"got {len(registry['metrics'])}")

rows = wd.overview_rows(SYN_SNAP, registry, 'US')
active_us = [m for m in registry['metrics']
             if m.get('economy') == 'US' and m.get('status') == 'active']
miss_rows = [r for r in rows if r['当前值'] == '缺失']
check('US概览行数=注册表US活跃指标数', len(rows) == len(active_us),
      f"rows={len(rows)} active={len(active_us)}")
check('缺失指标如实生成缺失行(INDPRO)', any(
    r['指标'] and r['当前值'] == '缺失' and 'INDPRO' not in r['来源']
    for r in miss_rows) and len(miss_rows) == len(active_us) - len(SYN_SNAP['facts']),
    f"miss={len(miss_rows)}")
spx_row = next(r for r in rows if '标普500' in r['指标'])
check('SPX行: 当前值/观测日期/周变化/来源',
      '7,377' in spx_row['当前值'] and spx_row['观测日期'] == '2026-11-06'
      and spx_row['周变化'] == '-2.68%' and spx_row['来源'] == 'global_market_collector',
      str(spx_row))
umc_row = next(r for r in rows if '密歇根' in r['指标'])
check('降级事实带质量提示', 'DEGRADED' in umc_row['数据质量'], umc_row['数据质量'])
check('无derived键的变化列为—', umc_row['周变化'] == '—' and umc_row['年内变化'] == '—')

mrows = wd.market_rows(SYN_SNAP, registry)
check('市场页含SPX且为资产类', any('标普500' in r['指标'] for r in mrows)
      and len(mrows) >= 40, f"rows={len(mrows)}")

check('fmt_change pct/pp/bp/缺',
      wd.fmt_change({'week': {'pct_change': 1.234}}, 'week') == '+1.23%'
      and wd.fmt_change({'week': {'pp_change': -0.5}}, 'week') == '-0.50pp'
      and wd.fmt_change({'week': {'bp_change': 25}}, 'week') == '+25bp'
      and wd.fmt_change({}, 'week') == '—' and wd.fmt_change(None, 'week') == '—')

s, err = wd.metric_series('SPX', SYN_SNAP)
check('序列走快照series_store', s is not None and s['dates'] == SYN_SNAP['series_store']['SPX']['dates']
      and 'series_store' in s['source'], f"s={s and s['source']} err={err}")
# D验收回归(2026-11-08): UI下拉把option dict整个传入不得崩(曾致历史页TypeError)
s_d, _e_d = wd.metric_series({'metric_id': 'SPX', 'label': '标普500', 'unit': '点'}, SYN_SNAP)
check('metric_series接受UI选项dict(D阻断回归)', s_d is not None and s_d['metric_id'] == 'SPX'
      and s_d['dates'] == s['dates'], f"s_d={s_d}")
s2, err2 = wd.metric_series('JGB10Y', SYN_SNAP)
check('japan单点指标如实报无序列',
      s2 is None and ('单点' in err2 or '无历史序列' in err2), err2 or '')

meta = wd.snapshot_meta(SYN_SNAP)
check('快照元信息: 日期/GateA/缺失', meta['date'] == '2026-11-08'
      and meta['gate_a'] == 'DEGRADED' and meta['missing'] == ['INDPRO'])

print('══ ② 研究问答状态面(不猜映射) ══')
res_oos = wd.ask_local('帮我决定买入哪只股票', SYN_SNAP)
check('投资建议类→out_of_scope拒绝', res_oos['status'] == 'out_of_scope', res_oos['status'])
res_un = wd.ask_local('今天午饭吃什么', SYN_SNAP)
check('无关问题→unmapped如实声明', res_un['status'] == 'unmapped', res_un['status'])
res_nosnap = wd.ask_local('美国政策利率是多少', None)
check('无快照→error明确提示先采集', res_nosnap['status'] == 'error'
      and '快照' in res_nosnap['answer_text'])

print('══ ③ 模型Key缺Key明确提示(不打印密钥;Model-Agnostic v2 中性文案) ══')
_saved = {k: os.environ.pop(k, None) for k in ('MODEL_API_KEY',)}
try:
    out = wd.ai_explain('测试问题', '测试事实')
    # 2026-11-09 W1/W5: 提示已中性化(任意 OpenAI 兼容端点;Agent Native 不需要),
    # 不再含厂商注册推荐——断言随语义更新
    check('无模型Key→ok=False+中性配置指引', out['ok'] is False
          and 'MODEL_API_KEY' in out['error'] and 'Agent Native' in out['error'],
          str(out)[:120])
finally:
    for _k, _v in _saved.items():
        if _v is not None:
            os.environ[_k] = _v

print('══ ④ 研究档案append-only落档(临时目录) ══')
real_snap, _note = wd.latest_snapshot()
if real_snap is not None:
    with tempfile.TemporaryDirectory() as td:
        arch = os.path.join(td, 'research_archive')
        qid, err = wd.save_to_archive('美国和日本10年期国债收益率差是多少？',
                                      real_snap, archive_dir=arch)
        check('真实快照→档案写入成功(QB-id)', qid and qid.startswith('QB-'), f"{qid} {err}")
        if qid:
            qid2, _ = wd.save_to_archive('美元兑日元最近走势如何？',
                                         real_snap, archive_dir=arch)
            files = []
            for _d, _f, fn in os.walk(arch):
                files.extend(fn)
            check('档案append-only累积(2条记录)', qid2 is not None and len(files) == 2,
                  f"files={files}")
else:
    print('  ⏭️ 本地无真实快照,档案落档冒烟跳过(CI环境预期)')

print('══ ⑤ W3 月/季自动级联默认关闭 ══')
rg_src = open(os.path.join(ROOT, 'scripts', 'report_generator.py'),
              encoding='utf-8').read()
check('级联由IA_AUTO_MONTHLY守卫', 'IA_AUTO_MONTHLY' in rg_src)
check('月报级联调用点在守卫分支内', 'auto_mq_enabled and done_month' in rg_src)
check('季报级联调用点在守卫分支内', 'auto_mq_enabled and done_quarter' in rg_src)
check('关闭时打印开启指引', 'IA_AUTO_MONTHLY=1' in rg_src)
check('缺模型Key快速失败提示(_call_model;Model-Agnostic v2中性文案)',
      'MODEL_KEY_MISSING_MESSAGE' in rg_src and '模型 API 未配置' in rg_src)

print()
print('═' * 60)
print(f'结果: {len(PASSED)}通过 / {len(FAILED)}失败')
print('═' * 60)
sys.exit(1 if FAILED else 0)
