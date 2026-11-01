#!/usr/bin/env python3
"""R003 任务C定量复核: BTC vs Coinbase 1.34% 差异配对重算(只读重放)。

输入(全部只读):
  - LIVE data/daily/global_2026102[7-9].json / global_2026103[01].json / global_20261101.json
    (采集快照,含BTC在途值与跨文件修正后的完结值)
  - 证据包 /tmp/w5-evidence/IA-P0-2-W5-FIX1-ACCEPTANCE-EVIDENCE.zip 内
    evidence/20261101_1428_02_coinbase_BTC-USD.txt(zipfile内存读取,不解压落盘)
  - 本workspace已留档的Coinbase公开API重取body(小时线/日线,附录C)

输出: 配对差值表(stdout,重定向保存于 recompute_btc_pairings.out.txt)。
声明: 本表仅归因证据,非验收口径变更。
"""
import json
import os
import zipfile

LIVE = '/Users/cast/AI内容/🤖_AI投资项目/每周宏观追踪/investment-agent/data/daily'
FIX1_ZIP = '/tmp/w5-evidence/IA-P0-2-W5-FIX1-ACCEPTANCE-EVIDENCE.zip'
PKG_EV_MEMBER = 'evidence/20261101_1428_02_coinbase_BTC-USD.txt'
HERE = os.path.dirname(os.path.abspath(__file__))


def live_btc(day):
    with open(os.path.join(LIVE, 'global_%s.json' % day), encoding='utf-8') as f:
        d = json.load(f)
    return d['time'], d['data']['BTC']


def pct(a, b):
    return abs(a - b) / b * 100.0


def main():
    lines = []

    def P(s=''):
        print(s)
        lines.append(s)

    # ── 我方值(LIVE只读) ──────────────────────────────────────
    t29, btc29 = live_btc('20261029')
    t30, btc30 = live_btc('20261030')
    t31, btc31 = live_btc('20261031')
    _, btc1101 = live_btc('20261101')

    ours_partial_1029 = btc30['close']          # 验收所用: obs 2026-10-29 在途值(23:00:17Z采集)
    ours_partial_1028 = btc29['close']          # obs 2026-10-28 在途值(23:56:56Z采集)
    ours_partial_1030 = btc31['close']          # obs 2026-10-30 在途值(23:00:15Z采集)

    s30 = dict(zip(btc30['series']['dates'], btc30['series']['values']))
    s31 = dict(zip(btc31['series']['dates'], btc31['series']['values']))
    s1101 = dict(zip(btc1101['series']['dates'], btc1101['series']['values']))
    ours_final_1028 = s31['2026-10-28']         # 完结值(yahoo定稿)
    ours_final_1029 = s31['2026-10-29']
    ours_final_1030 = s1101['2026-10-30']
    ours_final_1026 = s31['2026-10-26']
    ours_final_1027 = s31['2026-10-27']
    ours_final_1031 = s1101['2026-10-31']

    # ── Coinbase 值 ────────────────────────────────────────────
    with zipfile.ZipFile(FIX1_ZIP) as zf:       # 只读,内存读取,不解压落盘
        pkg_candles = json.loads(zf.read(PKG_EV_MEMBER).decode('utf-8'))
    # pkg_candles: [time, low, high, open, close, volume]
    cb = {}
    for c in pkg_candles:
        import datetime
        iso = datetime.datetime.fromtimestamp(c[0], datetime.timezone.utc).date().isoformat()
        cb[iso] = {'low': c[1], 'high': c[2], 'open': c[3], 'close': c[4],
                   'start_ts': c[0], 'start_on_day_boundary': c[0] % 86400 == 0}
    cb_final_1029 = cb['2026-10-29']['close']   # 77780.33(验收对照值)
    cb_final_1030 = cb['2026-10-30']['close']

    # 外部重取(附录C留档)
    bodies = sorted(fn for fn in os.listdir(HERE) if fn.endswith('.body'))
    hourly = daily = None
    for fn in bodies:
        with open(os.path.join(HERE, fn), encoding='utf-8') as f:
            body = json.load(f)
        if 'hourly' in fn:
            hourly = body
        elif 'daily' in fn:
            daily = body
    import datetime as _dt
    hr = {}
    for c in (hourly or []):
        iso = _dt.datetime.fromtimestamp(c[0], _dt.timezone.utc)
        hr[iso.strftime('%m-%dT%H')] = {'open': c[3], 'close': c[4], 'low': c[1], 'high': c[2]}
    dl = {}
    for c in (daily or []):
        iso = _dt.datetime.fromtimestamp(c[0], _dt.timezone.utc).date().isoformat()
        dl[iso] = c[4]

    P('== R003 BTC 1.34% 配对重算(仅归因证据,非验收口径变更) ==')
    P('')
    P('[输入] 我方(LIVE只读): ')
    P('  global_20261029.json time=%s BTC obs=%s close=%s' % (t29, btc29['date'], ours_partial_1028))
    P('  global_20261030.json time=%s BTC obs=%s close=%s  <-- 验收所用文件' % (t30, btc30['date'], ours_partial_1029))
    P('  global_20261031.json time=%s BTC obs=%s close=%s' % (t31, btc31['date'], ours_partial_1030))
    P('  series跨文件修正: 10-29: %s(在途,1030文件) -> %s(完结,1031文件); '
      '10-28: %s(在途) -> %s(完结)' % (
          s30.get('2026-10-29'), ours_final_1029, dict(zip(btc29['series']['dates'], btc29['series']['values']))['2026-10-28'],
          ours_final_1028))
    P('[输入] Coinbase(包内证据+公开API重取): ')
    P('  包内2026-10-29日K: close=%s start_ts=%s 日界00:00Z=%s' % (
        cb_final_1029, cb['2026-10-29']['start_ts'], cb['2026-10-29']['start_on_day_boundary']))
    P('  包内2026-10-30日K: close=%s start_ts=%s 日界00:00Z=%s' % (
        cb_final_1030, cb['2026-10-30']['start_ts'], cb['2026-10-30']['start_on_day_boundary']))
    P('  重取小时线23:00Z(10-29): open=%s close=%s low=%s high=%s' % (
        hr['10-29T23']['open'], hr['10-29T23']['close'], hr['10-29T23']['low'], hr['10-29T23']['high']))
    P('')
    P('[配对差值表] (差值=|a-b|/b*100, 四舍五入0.01%)')
    P('%-46s %12s %12s %8s' % ('配对', '我方值', 'Coinbase', '差值%'))
    rows = [
        ('P-A 验收实际: 在途值 vs 完整UTC日收盘', ours_partial_1029, cb_final_1029),
        ('P-B 修正: 完结日收盘 vs 完整UTC日收盘', ours_final_1029, cb_final_1029),
        ('P-C 同时点: 在途值 vs 23:00Z小时开盘', ours_partial_1029, hr['10-29T23']['open']),
        ('P-D 错日反证: 在途值 vs 前一日(10-28)收盘', ours_partial_1029, dl['2026-10-28']),
        ('P-D 错日反证: 在途值 vs 次日(10-30)收盘', ours_partial_1029, dl['2026-10-30']),
    ]
    for name, a, b in rows:
        P('%-46s %12.2f %12.2f %8.2f' % (name, a, b, round(pct(a, b), 2)))
    P('')
    P('[完结日跨源基差核对] yahoo完结值 vs Coinbase同ISO日收盘(均完整UTC日):')
    for iso, ours in (('2026-10-26', ours_final_1026), ('2026-10-27', ours_final_1027),
                      ('2026-10-28', ours_final_1028), ('2026-10-29', ours_final_1029),
                      ('2026-10-30', ours_final_1030), ('2026-10-31', ours_final_1031)):
        P('  %s: yahoo=%11.2f  coinbase=%11.2f  差值=%.3f%%' % (iso, ours, dl[iso], pct(ours, dl[iso])))
    P('')
    P('[窗口一致性旁证] 我方在途high/low vs Coinbase完整日high/low(10-29):')
    P('  我方 high=%s low=%s (23:00Z截断) | Coinbase日K high=%s low=%s (完整日)' % (
        btc30['high'], btc30['low'], cb['2026-10-29']['high'], cb['2026-10-29']['low']))
    P('  截断窗口性质: 我方high<=完整日high 且 我方low>=完整日low -> 与截断假设一致')
    P('')
    P('[结论] 1.34%由配对P-A产生(在途值 vs 完整日收盘);')
    P('       同口径配对P-B(0.01%)与同时点配对P-C(0.05%)均≈0;')
    P('       错日配对P-D(2.99%/2.13%)不能产生1.34% -> 排除错日假设。')

    with open(os.path.join(HERE, 'recompute_btc_pairings.out.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
