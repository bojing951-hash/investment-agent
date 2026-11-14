#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HK 增量修复测试(2026-11-14, fix/hk-incremental-v1)。

离线套件: 腾讯/yfinance 双源打桩, 持久化档注入 tmpdir(HK_HISTORY_FILE)。
锁三件事:
1. 日常主路=腾讯 320 小窗增量合并(零 yfinance 调用=治限流);
2. 腾讯失败+持久化新鲜→持久化全窗直通(仍零 yfinance);
3. yfinance 仅在持久化缺失/陈旧/深度不足时按需回补;三路皆无→None。

脚本式逐检(仓库惯例): python3 tests/test_hk_incremental.py
"""
import json
import os
import sys
import tempfile
import shutil
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

PASS = FAIL = 0


def check(name, cond, detail=''):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")


import china_market_collector as cmc  # noqa: E402

TMP = tempfile.mkdtemp(prefix='hk_inc_')
os.environ['HK_HISTORY_FILE'] = os.path.join(TMP, 'hk_index_history.json')
os.environ.pop('HK_TX_DAILY_BARS', None)
os.environ.pop('HK_INDEX_HISTORY_BARS', None)
os.environ.pop('HK_HISTORY_MAX_GAP_DAYS', None)

TODAY = datetime.now().strftime('%Y-%m-%d')


def dseq(n, end=None):
    """n 根升序日序列(纯自然日,足够测试语义),返回(dates, values)。"""
    end = end or TODAY
    base = datetime.strptime(end, '%Y-%m-%d')
    dates = [(base - timedelta(days=n - 1 - i)).strftime('%Y-%m-%d')
             for i in range(n)]
    values = [100.0 + i for i in range(n)]
    return dates, values


def patch_tencent(rows_or_none, calls):
    def fake(code, bars=None, retries=2):
        calls.append(bars)
        return rows_or_none
    cmc._tx_kline_rows = fake


def patch_yfinance(result_or_none, calls):
    def fake(ticker, name, retries=1):
        calls.append(ticker)
        if result_or_none is None:
            return None
        dates, values = result_or_none
        m = cmc._hk_metrics_from_daily(dates, values)
        m['series'] = {'dates': dates, 'values': values}
        return m
    cmc._fetch_hk_yfinance = fake


print("=" * 72)
print("[1] 纯函数: hk_daily_bars / 新鲜度 / 合并")
print("=" * 72)

check("hk_daily_bars 默认 320(WAF 上限)", cmc.hk_daily_bars() == 320)
os.environ['HK_TX_DAILY_BARS'] = '200'
check("hk_daily_bars env 覆盖 200", cmc.hk_daily_bars() == 200)
os.environ['HK_TX_DAILY_BARS'] = '9999'
check("hk_daily_bars 越界回落 320", cmc.hk_daily_bars() == 320)
os.environ['HK_TX_DAILY_BARS'] = 'abc'
check("hk_daily_bars 非法回落 320", cmc.hk_daily_bars() == 320)
os.environ.pop('HK_TX_DAILY_BARS', None)

d5, v5 = dseq(5)
s5 = {'dates': d5, 'values': v5}
check("_hk_series_fresh 末观测=今天→True",
      cmc._hk_series_fresh(s5, today=TODAY))
check("_hk_series_fresh 末观测5天前(≤10)→True",
      cmc._hk_series_fresh({'dates': [(datetime.now() - timedelta(days=5)).
                                      strftime('%Y-%m-%d')], 'values': [1.0]},
                           today=TODAY))
check("_hk_series_fresh 末观测11天前(>10)→False",
      not cmc._hk_series_fresh({'dates': [(datetime.now() - timedelta(days=11)).
                                          strftime('%Y-%m-%d')], 'values': [1.0]},
                               today=TODAY))
check("_hk_series_fresh 空序列→False", not cmc._hk_series_fresh(None))

d_old, v_old = dseq(8)
d_new, v_new = dseq(4)          # 尾部4天与 old 重叠, 值不同(新覆写)
merged = cmc._merge_hk_series({'dates': d_old, 'values': v_old},
                              {'dates': d_new, 'values': [500 + i for i in range(4)]})
check("_merge 升序且长度=并集(8+4-4重叠=8)", len(merged['dates']) == 8)
check("_merge 同日新值覆写(末4值=新段)",
      merged['values'][-1] == 503.0 and merged['values'][3] == 103.0)
check("_merge 尾裁 hk_history_bars()(2600)不误伤正常长度",
      len(cmc._merge_hk_series({'dates': d_old, 'values': v_old})['dates']) == 8)
d80, v80 = dseq(80)
os.environ['HK_INDEX_HISTORY_BARS'] = '70'
check("_merge 尾裁 env 覆盖生效(80→70, 合法下限60内取值)",
      len(cmc._merge_hk_series({'dates': d80, 'values': v80})['dates']) == 70)
os.environ.pop('HK_INDEX_HISTORY_BARS', None)

print()
print("=" * 72)
print("[2] fetch_hk_indices 三路行为(双源打桩)")
print("=" * 72)

# 场景A: 腾讯小窗成功 + 无持久化 → 合并落盘, 零 yfinance
os.environ['HK_HISTORY_FILE'] = os.path.join(TMP, 'a.json')
d200, v200 = dseq(200)
tx_calls, yf_calls = [], []
patch_tencent([(d, c) for d, c in zip(d200, v200)], tx_calls)
patch_yfinance(None, yf_calls)
res = cmc.fetch_hk_indices()
check("A: 两指数均成功", len(res) == 2)
check("A: 腾讯请求量=320(hk_daily_bars 默认)",
      all(b == 320 for b in tx_calls) and len(tx_calls) == 2, str(tx_calls))
check("A: 持久化深度不足(200<1300)但回补失败→浅窗如实保留",
      len(res['^HSI']['series']['dates']) == 200)
check("A: 零 yfinance 调用仅当深度足额——此处回补被尝试",
      len(yf_calls) == 2, str(yf_calls))
hist_a = json.load(open(os.path.join(TMP, 'a.json')))
check("A: 持久化档落盘且与产出一致",
      hist_a['^HSI']['dates'] == res['^HSI']['series']['dates'])

# 场景B: 腾讯成功 + 持久化已足深(2600) → 合并, 零 yfinance 回补
os.environ['HK_HISTORY_FILE'] = os.path.join(TMP, 'b.json')
d2600, v2600 = dseq(2600)
cmc._save_hk_history({'^HSI': {'dates': d2600, 'values': v2600},
                      '^HSCE': {'dates': d2600, 'values': v2600}})
tx_calls, yf_calls = [], []
patch_tencent([(d, c) for d, c in zip(d200, v200)], tx_calls)
patch_yfinance(None, yf_calls)
res = cmc.fetch_hk_indices()
check("B: 腾讯小窗并入深史(2600 根保持上限)",
      len(res['^HSI']['series']['dates']) == 2600)
check("B: 深度足额→零 yfinance 回补(治限流核心断言)",
      len(yf_calls) == 0, str(yf_calls))
check("B: 新值覆写同日(末值=新段值)",
      res['^HSI']['series']['values'][-1] == v200[-1])

# 场景C: 腾讯失败 + 持久化新鲜 → 持久化全窗直通, 零 yfinance
os.environ['HK_HISTORY_FILE'] = os.path.join(TMP, 'c.json')
d30, v30 = dseq(30)
cmc._save_hk_history({'^HSI': {'dates': d30, 'values': v30},
                      '^HSCE': {'dates': d30, 'values': v30}})
tx_calls, yf_calls = [], []
patch_tencent([], tx_calls)
patch_yfinance(None, yf_calls)
res = cmc.fetch_hk_indices()
check("C: 腾讯失败仍出数(持久化新鲜兜底)", len(res) == 2)
check("C: 零 yfinance 调用(新鲜即不回补)",
      len(yf_calls) == 0, str(yf_calls))
check("C: series=持久化原样(n=30)", len(res['^HSI']['series']['dates']) == 30)
check("C: date=末观测日(陈旧度如实披露)",
      res['^HSI']['date'] == d30[-1])

# 场景D: 腾讯失败 + 持久化陈旧(11天前) → yfinance 回补, 成功则合并落盘
os.environ['HK_HISTORY_FILE'] = os.path.join(TMP, 'd.json')
stale_end = (datetime.now() - timedelta(days=11)).strftime('%Y-%m-%d')
d_stale, v_stale = dseq(20, end=stale_end)
cmc._save_hk_history({'^HSI': {'dates': d_stale, 'values': v_stale},
                      '^HSCE': {'dates': d_stale, 'values': v_stale}})
d_deep, v_deep = dseq(2600)
tx_calls, yf_calls = [], []
patch_tencent([], tx_calls)
patch_yfinance((d_deep, v_deep), yf_calls)
res = cmc.fetch_hk_indices()
check("D: 陈旧→yfinance 回补成功出数", len(res) == 2)
check("D: yfinance 每指数恰一次", len(yf_calls) == 2, str(yf_calls))
check("D: 回补结果合并落盘",
      json.load(open(os.path.join(TMP, 'd.json')))['^HSI']['dates'][-1] == d_deep[-1])

# 场景E: 三路皆无 → None(诚实缺席, Gate A 兜底)
os.environ['HK_HISTORY_FILE'] = os.path.join(TMP, 'e.json')
tx_calls, yf_calls = [], []
patch_tencent([], tx_calls)
patch_yfinance(None, yf_calls)
res = cmc.fetch_hk_indices()
check("E: 三路皆无→hk_indices 空 dict(Gate A 将 core_missing 拦截)",
      res == {})

# 场景F: 产出结构向后兼容(快照消费契约: close/week_chg/ytd_chg/date/series/name)
os.environ['HK_HISTORY_FILE'] = os.path.join(TMP, 'f.json')
tx_calls, yf_calls = [], []
patch_tencent([(d, c) for d, c in zip(d30, v30)], tx_calls)
patch_yfinance(None, yf_calls)
res = cmc.fetch_hk_indices()
item = res['^HSI']
need = {'name', 'close', 'week_chg', 'ytd_chg', 'date', 'series'}
check("F: 输出键集与修复前契约一致(snapshot_builder 消费面零改动)",
      need <= set(item) and isinstance(item['series'], dict)
      and 'dates' in item['series'] and 'values' in item['series'])

shutil.rmtree(TMP, ignore_errors=True)

print()
print("=" * 72)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 72)
sys.exit(0 if FAIL == 0 else 1)
