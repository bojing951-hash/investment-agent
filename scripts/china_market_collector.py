"""
A股/港股数据采集模块 v2.1
数据源：Tushare（A股主力）+ 腾讯ifzq直连（港股主通道）+ yfinance（港股备用）+ 新浪直连（AH溢价主通道）
2026-10-17修复：恒指/国企yfinance连续4日429限流、东财push2在当前网络直连/代理双双被断
（SSLError/ProxyError）→ 境内源一律直连不走系统代理，境外源(yfinance)保持走代理。
Audit-R33 任务4(2026-11-25): 采集时间预算+断点续采+随档 collection_status
(见「采集时间预算」节);指数清单/接口/参数/备源回落/61 秒限流间隔零变化。
"""

import os
import sys
import json
import re
import time
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
from contextlib import contextmanager

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from env_config import TUSHARE_TOKEN

import tushare as ts
import yfinance as yf

# ============ 配置 ============
PROJECT_DIR = os.path.join(os.path.dirname(__file__), '..')
DATA_DIR = os.path.join(PROJECT_DIR, 'data')

# tushare pro客户端**惰性初始化**(FIX3-04 CI可移植性): pro_api对空token会回退读
# 本地凭证文件(~/.tushare.yaml),干净机器(CI/新clone)无凭证→模块导入即
# raise 'api init error',离线测试连import都被阻断。改为采集调用点经_pro()取用;
# token在场时行为与原模块级初始化完全一致(同一pro_api同一token)。
_pro_client = None


def _pro():
    global _pro_client
    if _pro_client is None:
        _pro_client = ts.pro_api(TUSHARE_TOKEN)
    return _pro_client


# ============ 方案A限流间隔(W5-RERUN T1/范围D, 2026-11-03) ============
# 实证(FIX3 §六附则/操作者2026-11-01实测): tushare index_daily 对同账号相邻
# 快速连发按"1次/分钟"限流——A_SHARE_INDICES 字典序第2只(399001.SZ)在无
# 间隔连发下必然"频率超限",且SZCI无备源→结构性死路(任何零代码重跑必缺SZCI
# →Gate A core FAIL)。本模块所有 index_daily 调用统一经 _index_daily 发起:
# 全局单调时钟保证任意相邻两次调用(无论成败、无论所在函数)间隔
# ≥ INDEX_DAILY_MIN_INTERVAL_SECONDS;已超出间隔的调用不额外等待。
# 清单/字典序/接口选择/参数/备源回落/import 依赖零变化(仅加间隔)。
INDEX_DAILY_MIN_INTERVAL_SECONDS = 61
_index_daily_last_ts = 0.0


def _index_daily(**kwargs):
    """index_daily 调用闸门(方案A): 相邻调用间隔≥61s;接口与参数零变化。"""
    global _index_daily_last_ts
    wait = INDEX_DAILY_MIN_INTERVAL_SECONDS - (time.monotonic() - _index_daily_last_ts)
    if wait > 0:
        print(f"  ⏳ tushare index_daily 限流间隔(方案A≥61s): 等待{wait:.1f}s")
        time.sleep(wait)
    _index_daily_last_ts = time.monotonic()
    return _pro().index_daily(**kwargs)

# A股指数列表
A_SHARE_INDICES = {
    '000001.SH': '上证指数',
    '399001.SZ': '深证成指',
    '399006.SZ': '创业板指',
    '000300.SH': '沪深300',
    '000905.SH': '中证500',
    '000852.SH': '中证1000',
}

# ============ 方案B东财备源(R049/IA-P0-2-W5-DATASRC-B, 2026-11-04) ============
# 根因(R032 判定件 attempt1_formal_20261104): tushare 同 token index_daily 日配额被
# 外部先在耗尽(判别首调即「5次/天」)→Gate A core 4 项(SHCOMP/SZCI/SH_AMOUNT/
# CN_TOTAL_TURNOVER)结构性缺失。用户实批备源换路;操作者实测: akshare 东财端点
# stock_zh_index_daily_em 免费、无需凭证,完结日 close+amount 可用并与新浪端点交叉
# 一致;旧回落 amount=0 的根因=新浪端点 stock_zh_index_daily 根本没有 amount 列
# (结构性缺陷,非数据源不可用)→旧新浪回落删除,唯一新增通道=东财公开免费端点。
# 纪律: tushare 调用参数/61s 闸门/A_SHARE_INDICES 清单与顺序零变化;零新 token。
# W5-EMWIN(R051, 2026-11-04): 原常量 EM_FALLBACK_MAX_DATE='2026-11-03'(R049 冻结)
# 把 EM 取值行永久钉死 11-03,收盘守卫(要求取值行=运行日)结构性不可满足(R050
# 判定 NV 根因之一,操作者裁定属合同设计缺陷)——经用户方案 B 实批(免费 EM 端点
# 换路,通道后续交易日正常出数=授权固有内容)+操作者裁定动态化: 常量→本函数。
# 阈值 16:10:00 HKT=A股 15:00 收盘后的固定缓冲;前 1 **自然**日(非交易日,周六→周五)。
def _em_max_date(now=None):
    """EM 取值行截止(动态): HKT 已完结交易日——时刻≥16:10:00→当日 ISO,
    否则前 1 自然日 ISO。now 缺省读真实 HKT 钟(UTC+8 无夏令时);仅供测试
    冻结注入。行选择语义(date≤截止,在途行禁用)与 R049 完全一致,仅截止
    随钟动态。"""
    hkt = timezone(timedelta(hours=8))
    if now is None:
        now = datetime.now(hkt)
    elif now.tzinfo is not None:
        now = now.astimezone(hkt)  # aware 输入(任意时区)一律折算 HKT 判定
    cutoff = now.replace(hour=16, minute=10, second=0, microsecond=0)
    return (now.date() if now >= cutoff else now.date() - timedelta(days=1)).isoformat()
EM_MAP = {
    '000001.SH': 'sh000001',
    '399001.SZ': 'sz399001',
    '399006.SZ': 'sz399006',
    '000300.SH': 'sh000300',
    '000905.SH': 'sh000905',
    '000852.SH': 'sh000852',
}


def _em_settled_pairs(df):
    """东财日K完结行选择: [(date_str, 原表行号)] 升序,date≤_em_max_date()
    (在途行禁用)。date 一律字符串化[:10],与端点返回 dtype 无关。"""
    if df is None or len(df) == 0:
        return []
    pairs = sorted(((str(d)[:10], i) for i, d in enumerate(df['date'])),
                   key=lambda p: p[0])
    return [p for p in pairs if p[0] <= _em_max_date()]


def _em_last_settled(df):
    """东财日K取值行: date≤_em_max_date() 的最后一行;无完结行→None。
    返回 (date_str, 行Series)。"""
    settled = _em_settled_pairs(df)
    if not settled:
        return None
    dstr, idx = settled[-1]
    return dstr, df.iloc[idx]


def _em_klines_direct(code, use_system_proxy=False):
    """东财公开 kline 端点直连(push2his;R20 2026-11-19 实测):
    akshare 包装层断连(RemoteDisconnected)期间的**同源等价**路径——同一
    端点同一字段。直连与系统代理两会话各试一轮(当日实测: 出口 IP 被
    端点间歇性断连,两会话命中其一即返回)。返回 [(date, close, volume,
    amount)] 升序完结行(date≤_em_max_date());失败→[]。"""
    em = EM_MAP.get(code)
    if not em:
        return []
    secid = ('1.' if em.startswith('sh') else '0.') + em[2:]
    sess = requests.Session() if use_system_proxy else _direct_session()
    try:
        r = sess.get(
            'https://push2his.eastmoney.com/api/qt/stock/kline/get',
            params={'secid': secid,
                    'fields1': 'f1,f2,f3,f4,f5,f6',
                    'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58',
                    'klt': '101', 'fqt': '0',
                    'beg': '19900101', 'end': '20500101'},
            timeout=20, headers={'User-Agent': 'Mozilla/5.0'})
        klines = ((r.json().get('data') or {}).get('klines')) or []
    except Exception:
        return []
    mx, out = _em_max_date(), []
    for row in klines:
        p = str(row).split(',')
        if len(p) < 7 or p[0] > mx:      # f51日期,f53收盘,f56量,f57额
            continue
        try:
            out.append((p[0], float(p[2]), float(p[5]), float(p[6])))
        except ValueError:
            continue
    return out


# 腾讯 ifzq 日K代码(A股指数;R20 2026-11-19 验证: 收盘与东财逐位一致,
# 2026-11-18 上证 3587.83 两源同值)
TX_INDEX_MAP = {
    '000001.SH': 'sh000001',
    '399001.SZ': 'sz399001',
    '399006.SZ': 'sz399006',
    '000300.SH': 'sh000300',
    '000905.SH': 'sh000905',
    '000852.SH': 'sh000852',
}


def _tx_klines(code):
    """腾讯 ifzq fqkline 日K(A股指数第三路;R20 2026-11-19 增):
    [date,open,close,high,low,volume]——无 amount 列(该路 amount=None,
    如实缺席不造数)。count=320(≈16 个月浅窗;大 count 触发腾讯 WAF,
    港股先例「深窗回补不可得,如实浅窗」);完结行 date≤_em_max_date()。
    返回 [(date, close, volume, None)]。"""
    tx = TX_INDEX_MAP.get(code)
    if not tx:
        return []
    try:
        r = _direct_session().get(
            'https://web.ifzq.gtimg.cn/appstock/app/fqkline/get',
            params={'param': f'{tx},day,,,320,qfq'}, timeout=20)
        d = ((r.json().get('data') or {}).get(tx)) or {}
        bars = d.get('qfqday') or d.get('day') or []
    except Exception:
        return []
    mx, out = _em_max_date(), []
    for b in bars:
        if not isinstance(b, (list, tuple)) or len(b) < 6 or str(b[0]) > mx:
            continue
        try:
            out.append((str(b[0]), float(b[2]), float(b[5]), None))
        except (TypeError, ValueError):
            continue
    return out


def _fetch_index_em(code, name):
    """F1 指数回落(东财/腾讯,仅 tushare 异常时经 fetch_a_share_indices
    进入): 返回与 tushare 路径同 schema 的 item + 新增键 via('em_kline'
    东财直连/'em_kline_proxy'东财系统代理/'tx_ifzq'腾讯浅窗/'akshare_em'
    包装末路);取值行=date≤_em_max_date() 最后一行(在途行禁用);四路皆
    失败/无完结行→None(该指数如实缺失)。单位披露: EM amount 单位=元
    (tushare 千元),volume 语义=成交量;腾讯路无 amount(None 如实缺席)。
    R20: 东财端点当日间歇断连→四路阶梯;腾讯浅窗 ≈16 个月在 item 注明。"""
    rows = _em_klines_direct(code)
    via = 'em_kline'
    if not rows:
        rows = _em_klines_direct(code, use_system_proxy=True)
        via = 'em_kline_proxy'
    if not rows:
        rows = _tx_klines(code)
        via = 'tx_ifzq'
    if not rows:
        try:
            import akshare as ak
            with _no_proxy():
                df = ak.stock_zh_index_daily_em(symbol=EM_MAP[code])
            settled = _em_settled_pairs(df)
            rows = [(d, float(df.iloc[i]['close']),
                     float(df.iloc[i].get('volume', 0) or 0),
                     float(df.iloc[i].get('amount', 0) or 0))
                    for d, i in settled]
            via = 'akshare_em'
        except Exception as e:
            print(f"  ⚠️ {name}({code}) 东财回落失败: {e}")
            return None
    if not rows:
        print(f"  ⚠️ {name}({code}) 东财回落无完结行(date≤{_em_max_date()})")
        return None
    # 数据批1(#10): 与 tushare 主路同窗语义——series=窗口起点起全序列
    # (EM 端点本就返回全史,按 cn_window_start 过滤);周变化规则不变;
    # YTD 基准=窗内**当年**首个收盘(非窗口首根)。
    win_start = cn_window_start(cn_index_history_period()).replace('-', '')
    win = [p for p in rows if p[0].replace('-', '') >= win_start]
    dates = [d for d, *_ in win]
    closes = [c for _, c, _, _ in win]
    close = closes[-1]
    # 周变化与 tushare 路径同规则(倒数第5收盘;不足5根对比首根)
    week_chg = None
    if len(closes) >= 5:
        prev_close = closes[-5]
        week_chg = round((close - prev_close) / prev_close * 100, 2)
    elif len(closes) >= 2:
        prev_close = closes[0]
        week_chg = round((close - prev_close) / prev_close * 100, 2)
    # YTD 基准=窗内当年首个收盘(纯函数 _ytd_base_close,同 tushare 主路)
    ytd_chg = None
    base = _ytd_base_close(dates, closes, dates[-1].replace('-', ''))
    if base:
        ytd_chg = round((close - base) / base * 100, 2)
    # 东财无 pct_chg 列 → 由前一完结收盘推得(EM同列自洽,非跨源拼接)
    pct_chg = 0.0
    if len(closes) >= 2 and closes[-2] > 0:
        pct_chg = round((close - closes[-2]) / closes[-2] * 100, 2)
    last_d, _lc, last_vol, last_amt = win[-1]
    item = {
        'name': name,
        'close': close,
        'pct_chg': pct_chg,
        'week_chg': week_chg,
        'ytd_chg': ytd_chg,
        'volume': last_vol,                                   # 单位: 股
        'amount': last_amt,                                   # 单位: 元;腾讯路 None
        'date': last_d.replace('-', ''),                      # →YYYYMMDD,同tushare规格
        'series': {'dates': dates, 'values': closes},
        'via': via,
    }
    if via == 'tx_ifzq':
        item['note'] = ('腾讯 ifzq 浅窗(≈16 个月,深窗回补不可得,如实浅窗;'
                        '收盘与东财逐位交叉一致;该路无成交额列)')
    return item

# 港股（主通道腾讯直连，yfinance备用）
HK_INDICES = {
    '^HSI': '恒生指数',
    '^HSCE': '恒生国企',
}

# 腾讯ifzq日K代码（2026-10-17验证：收盘值与yfinance逐分一致）
HK_TX_CODE = {
    '^HSI': 'hkHSI',
    '^HSCE': 'hkHSCEI',
}

# ============ 境内源直连工具（2026-10-17修复） ============
# requests默认trust_env=True会读取macOS系统代理(scutil --proxy → 127.0.0.1:7890),
# launchd 07:00运行时经Clash出境: 出口IP被Yahoo限流(429)、东财push2直接被断连
# (SSLError/ProxyError, 且本机直连东财也不通——该通道已整体不可用)。
# 对策: 境内端点(腾讯/新浪)一律直连——raw HTTP用直连会话, akshare调用临时禁用代理。

def _direct_session():
    """直连会话: trust_env=False同时无视环境变量代理与macOS系统代理"""
    s = requests.Session()
    s.trust_env = False
    s.headers.update({'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'})
    return s

@contextmanager
def _no_proxy():
    """临时禁用requests代理读取(akshare内部请求无法注入session,只能patch模块级getproxies)。
    只包裹境内akshare调用; 严禁包住yfinance——境外源依赖代理出境。"""
    orig = requests.utils.getproxies
    requests.utils.getproxies = lambda: {}
    try:
        yield
    finally:
        requests.utils.getproxies = orig

# 需要估值数据的指数
# IA-DATA-W3(AC-01c, 2026-11-04): 000001.SH(上证指数)纳入估值名单——注册 SH_PE
# 语义=上证指数整体PE(TTM),原名单仅300/500/1000,上证身份缺席(R008 断点③:
# A_SHARE_INDICES 含 000001.SH 而本名单不含)。与 A_SHARE_INDICES 在上证身份上
# 对齐(既有 300/500/1000 成员与顺序零变化,仅首位新增上证)。
VALUATION_INDICES = {
    '000001.SH': '上证指数',
    '000300.SH': '沪深300',
    '000905.SH': '中证500',
    '000852.SH': '中证1000',
}
# SH_PE 扁平桥接的权威身份(注册口径=上证;300/500/1000 不冒充,身份纪律)
SH_PE_IDENTITY = '000001.SH'

def get_trade_dates():
    """获取日期范围"""
    today = datetime.now()
    end_date = today.strftime('%Y%m%d')
    start_date_week = (today - timedelta(days=10)).strftime('%Y%m%d')
    start_date_year = f'{today.year}0101'
    return end_date, start_date_week, start_date_year

# === 数据批1(#10 CN 股指深窗,2026-11-10): 历史窗口参数化 =====================
# 原硬编码 start_date=当年0101 → 指数 series 恒为年内浅窗(台账#10 缺口:
# CN 股指序列仅 2026-01 起)。镜像 global_market_collector Charter6-P0 同款:
# env CN_INDEX_HISTORY_PERIOD(合法集=env_config.HISTORY_PERIOD_LEGAL),默认
# '10y';'ytd'=旧行为精确保留。61s 限流闸门(_index_daily)零变化——窗口加宽
# 只加大单次响应,不增加调用次数。
_CN_PERIOD_DAYS = {'1d': 1, '5d': 5, '1mo': 31, '3mo': 92, '6mo': 183}
_CN_PERIOD_YEARS = {'1y': 1, '2y': 2, '5y': 5, '10y': 10}
_CN_FLOOR_DATE = '19901219'   # 上证基日(1990-12-19);各指数以源端实际可得为准

# Charter8(HK 深度补拉, 2026-11-10): 港股指数深窗与 A 股同档≈10年。
# 腾讯 ifzq 按 bar 数取数(2600根≈10年);WAF 对大 count 可能 501 拦截→
# 上层转 yfinance 深窗备源(见 _fetch_hk_yfinance)。env 可覆盖,非法回落。
def hk_history_bars():
    """港股指数日K bar 数(纯函数,现读 env HK_INDEX_HISTORY_BARS)。"""
    raw = os.environ.get('HK_INDEX_HISTORY_BARS')
    if raw is None or not str(raw).strip():
        return 2600
    try:
        n = int(str(raw).strip())
    except ValueError:
        print(f"  ⚠️ HK_INDEX_HISTORY_BARS 非整数({raw!r}),回落默认 2600")
        return 2600
    if n < 60:
        print(f"  ⚠️ HK_INDEX_HISTORY_BARS={n} 过小(<60 不足以算周变化),回落 2600")
        return 2600
    return n


def cn_index_history_period():
    """CN 指数历史窗口解析(纯函数,现读 env;空白→默认'10y',非法→告警回落)。"""
    from env_config import HISTORY_PERIOD_LEGAL, resolve_history_period
    period, fallback = resolve_history_period(
        os.environ.get('CN_INDEX_HISTORY_PERIOD'), '10y')
    if fallback:
        print(f"  ⚠️ CN_INDEX_HISTORY_PERIOD 非法(合法集 "
              f"{'/'.join(HISTORY_PERIOD_LEGAL)}),回落默认 10y")
    return period


# === HK增量修复(2026-11-14, LIVE Gate A 连续FAIL根因) =========================
# 事故链: 日常采集每日向腾讯请求 2600 根(10y 全窗)→WAF 拒(>320 必拦, C8 已
# 知)→转 yfinance period='10y' →Yahoo 对日频全量拉取限流(YFRateLimitError,
# 11-12 起)→hk_indices 空→Gate A core_missing=[HSI,HSCEI] 三连FAIL→weekly
# 预检拒出。结构性缺陷=HK 深历史无持久化, 每日重拉全窗既是 WAF 拦截面也是
# Yahoo 限流的滥用模式本身。
# 修复(登记冻结):
# - 日常腾讯请求量=HK_TX_DAILY_BARS(默认 320=WAF 实测上限, 夹逼[60,320]);
# - 本地增量持久化 data/daily/hk_index_history.json(按 ticker 存深窗, 增量
#   合并: 新日期覆写同日, 升序, 尾裁至 hk_history_bars() 根);
# - 腾讯小窗成功→合并+落盘+全窗直通(零 Yahoo 调用=治限流);
# - 腾讯失败且持久化新鲜(末观测≤HK_HISTORY_MAX_GAP_DAYS 天, 默认10)→用
#   持久化全窗(指标日期=末观测日, 陈旧如实经 date 字段披露, 不冒充当日);
# - 仅当持久化缺失/陈旧/深度不足(<目标根数一半)时才尝试 yfinance 深窗回补
#   一次(成功同样合并落盘)——从"每日全量"降为"按需回补";
# - 三路皆无→None(诚实缺席, Gate A 兜底)。
def hk_daily_bars():
    """日常腾讯请求 bar 数(纯函数,现读 env HK_TX_DAILY_BARS)。

    默认 320=腾讯 WAF 实测上限(2026-11-14 复测可达);夹逼 [60,320],
    非法回落 320。深窗目标仍由 hk_history_bars() 表达(持久化尾裁用)。"""
    raw = os.environ.get('HK_TX_DAILY_BARS')
    if raw is None or not str(raw).strip():
        return 320
    try:
        n = int(str(raw).strip())
    except ValueError:
        print(f"  ⚠️ HK_TX_DAILY_BARS 非整数({raw!r}),回落默认 320")
        return 320
    if n < 60 or n > 320:
        print(f"  ⚠️ HK_TX_DAILY_BARS={n} 越界(合法 60..320),回落 320")
        return 320
    return n


def hk_history_max_gap_days():
    """持久化新鲜度阈值(纯函数,现读 env HK_HISTORY_MAX_GAP_DAYS,默认10)。"""
    raw = os.environ.get('HK_HISTORY_MAX_GAP_DAYS')
    try:
        n = int(str(raw).strip()) if raw and str(raw).strip() else 10
        return n if n >= 1 else 10
    except ValueError:
        return 10


def _hk_history_path():
    """持久化档路径(env HK_HISTORY_FILE 可覆盖,离线测试用)。"""
    return os.environ.get('HK_HISTORY_FILE') or os.path.join(
        DATA_DIR, 'daily', 'hk_index_history.json')


def _load_hk_history():
    """读持久化档{ticker: {'dates':[...], 'values':[...]}};缺失/损坏→{}。"""
    p = _hk_history_path()
    try:
        with open(p, encoding='utf-8') as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_hk_history(hist):
    """原子写持久化档(先写 .tmp 再 rename,防半写档)。"""
    p = _hk_history_path()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(hist, f, ensure_ascii=False)
    os.replace(tmp, p)


def _merge_hk_series(*series_list):
    """多段 {'dates','values'} 按日合并(后写覆写同日),升序,尾裁 hk_history_bars()。

    纯函数;空段跳过;values 随 dates 对位取自各段原值,零改写零造数。"""
    by_date = {}
    for s in series_list:
        if not s:
            continue
        for d, v in zip(s.get('dates') or [], s.get('values') or []):
            by_date[str(d)[:10]] = v
    dates = sorted(by_date)
    cap = hk_history_bars()
    if len(dates) > cap:
        dates = dates[-cap:]
    return {'dates': dates, 'values': [by_date[d] for d in dates]}


def _hk_series_fresh(series, today=None):
    """持久化新鲜判定: 末观测距今天数 ≤ hk_history_max_gap_days()。

    纯函数;空序列→False。today=YYYY-MM-DD(测试注入)。"""
    if not series or not series.get('dates'):
        return False
    t = today or datetime.now().strftime('%Y-%m-%d')
    try:
        last = datetime.strptime(str(series['dates'][-1])[:10], '%Y-%m-%d')
        now = datetime.strptime(t, '%Y-%m-%d')
    except ValueError:
        return False
    return (now - last).days <= hk_history_max_gap_days()


def cn_window_start(period, today=None):
    """窗口起点 YYYYMMDD(纯函数,离线可测)。

    'ytd'→当年0101(旧行为);'max'→上证基日下限;'Nd/Nmo'→自然日回退;
    'Ny'→年回退(月末日不前移——指数日频无月末语义,年回退取同月日)。"""
    t = today or datetime.now()
    if period == 'ytd':
        return f'{t.year}0101'
    if period == 'max':
        return _CN_FLOOR_DATE
    if period in _CN_PERIOD_DAYS:
        return (t - timedelta(days=_CN_PERIOD_DAYS[period])).strftime('%Y%m%d')
    if period in _CN_PERIOD_YEARS:
        try:
            return t.replace(year=t.year - _CN_PERIOD_YEARS[period]).strftime('%Y%m%d')
        except ValueError:                    # 2/29 润日 → 3/1 同义
            return (t.replace(year=t.year - _CN_PERIOD_YEARS[period],
                              day=28)).strftime('%Y%m%d')
    return f'{t.year}0101'


def _ytd_base_close(trade_dates, closes, last_date_yyyymmdd):
    """YTD 基准收盘(纯函数,数据批1#10 深窗修正)。

    基准=**当年**首个收盘(深窗下序列首根是 N 年前,不得当年初基准);
    当年无行(如 max 窗被源端截断)→退回序列首根并保持非完整YTD语义。
    trade_dates=YYYYMMDD 字符串序列(升序),closes 同长。"""
    year = str(last_date_yyyymmdd)[:4]
    for d, c in zip(trade_dates, closes):
        if str(d).startswith(year):
            return float(c)
    return float(closes[0]) if closes else None


def fetch_a_share_indices(checkpoint=None, budget=None):
    """采集A股指数数据

    Audit-R33 任务4: checkpoint=None/budget=None → 旧行为(逐指数限流取网,
    结果仅随整档写出);checkpoint 给出时逐指数写断点并续采(同交易日窗、
    同历史窗口、当日 bar 已定型——已取到的指数不重复限流等待),budget 给出时逐
    指数开始前做协作式预算检查(耗尽→停止并标记,不丢已取到的指数)。
    阶段状态见 _STAGE_STATUS['a_share_indices']。"""
    print("\n📈 采集A股指数...")
    end_date, start_week, start_year = get_trade_dates()
    period = cn_index_history_period()
    window_start = cn_window_start(period)
    print(f"  历史窗口: {period}(start={window_start};CN_INDEX_HISTORY_PERIOD 可覆盖)")
    results = {}
    fetched_at = {}          # {code: 取数时刻 Unix 秒}(断点可续性判定用)
    _STAGE_STATUS['a_share_indices'] = {'resumed': [], 'cut_by_budget': False}
    if checkpoint is not None:
        results.update(_ashare_checkpoint_load(end_date, window_start))
        obj0 = _ashare_checkpoint_read()
        if obj0 and results:
            fetched_at.update({c: obj0['fetched_at'][c] for c in results})
        _STAGE_STATUS['a_share_indices']['resumed'] = sorted(results)
        if results:
            print(f"  ♻️ 断点续采: {len(results)} 个指数取自运行日内断点"
                  f"({','.join(sorted(results))}),不重复取网")

    for code, name in A_SHARE_INDICES.items():
        if code in results:
            continue
        if budget is not None and budget.exhausted():
            _STAGE_STATUS['a_share_indices']['cut_by_budget'] = True
            print(f"  ⏹️ {name}({code}): 时间预算耗尽,本指数未采"
                  f"(下次运行自断点续采)")
            continue
        try:
            # 数据批1(#10): 单次拉取 window_start 起全序列(原=年初至今),
            # 附加原始series供事实引擎统一口径计算(周/MTD/YTD=期前收盘基准)
            df_year = _index_daily(ts_code=code, start_date=window_start, end_date=end_date)
            if df_year is None or len(df_year) == 0:
                print(f"  ⚠️ {name}({code}): 无数据")
                continue
            df = df_year.sort_values('trade_date')
            latest = df.iloc[-1]
            close = float(latest['close'])

            # 周变化
            week_chg = None
            if len(df) >= 5:
                prev_close = float(df.iloc[-5]['close'])
                week_chg = round((close - prev_close) / prev_close * 100, 2)
            elif len(df) >= 2:
                prev_close = float(df.iloc[0]['close'])
                week_chg = round((close - prev_close) / prev_close * 100, 2)

            # YTD: 基准=窗口内**当年首个**收盘(纯函数 _ytd_base_close;
            # 深窗下 df.iloc[0] 是 N 年前,不得再当年初基准——数据批1#10 修正)
            ytd_chg = None
            year_start = _ytd_base_close(list(df['trade_date']),
                                         list(df['close']),
                                         str(latest['trade_date']))
            if year_start:
                ytd_chg = round((close - year_start) / year_start * 100, 2)

            dates = [f"{str(d)[:4]}-{str(d)[4:6]}-{str(d)[6:]}" for d in df['trade_date']]
            closes = [float(v) for v in df['close']]
            results[code] = {
                'name': name,
                'close': close,
                'pct_chg': float(latest.get('pct_chg', 0)),
                'week_chg': week_chg,
                'ytd_chg': ytd_chg,
                'volume': float(latest.get('vol', 0)),
                'amount': float(latest.get('amount', 0)),
                'date': str(latest['trade_date']),
                'series': {'dates': dates, 'values': closes},
                'via': 'tushare',
            }
            if checkpoint is not None:
                fetched_at[code] = time.time()
                _ashare_checkpoint_save(end_date, window_start, results, fetched_at)
            print(f"  ✅ {name}: {close} (周{week_chg:+.2f}%)" if week_chg else f"  ✅ {name}: {close}")

        except Exception as e:
            print(f"  ❌ {name}({code}): {e}")
            # F1(R049 B-AC-01): tushare 异常→东财回落;上方 tushare 先行路径零变化。
            item = _fetch_index_em(code, name)
            if item is not None:
                results[code] = item
                if checkpoint is not None:
                    fetched_at[code] = time.time()
                    _ashare_checkpoint_save(end_date, window_start, results, fetched_at)
                wc = item.get('week_chg')
                tag = f" (周{wc:+.2f}%)" if wc is not None else ""
                print(f"  ✅ {name}: {item['close']}{tag} [东财回落 akshare_em]")

    if checkpoint is not None:
        # 断点续采后恢复清单序(结果键序与清单一致,与旧路径同形)
        results = {c: results[c] for c in A_SHARE_INDICES if c in results}
    return results

def _hk_metrics_from_daily(dates, closes):
    """由日收盘序列计算指标——与yfinance口径一致:
    week_chg对比倒数第5根收盘, ytd对比当年首个交易日收盘。纯函数便于离线测试。"""
    close = round(float(closes[-1]), 2)
    week_chg = None
    if len(closes) >= 5:
        prev = float(closes[-5])
        week_chg = round((close - prev) / prev * 100, 2)
    year = str(datetime.now().year)
    ytd_chg = None
    year_first = next((c for dt, c in zip(dates, closes) if str(dt)[:4] == year), None)
    if year_first:
        ytd_chg = round((close - year_first) / year_first * 100, 2)
    return {'close': close, 'week_chg': week_chg, 'ytd_chg': ytd_chg, 'date': str(dates[-1])[:10]}

def _tx_kline_rows(code, bars=None, retries=2):
    """腾讯ifzq日K直连,返回升序[(date, close), ...];失败返回[]。

    bars: Charter8(HK深度补拉)——默认取 hk_history_bars()(≈10年,与
    A股深窗 CN_INDEX_HISTORY_PERIOD=10y 同档);腾讯 WAF 对大 count 请求
    可能 501 拦截(2026-11-10 实测 >320 被拦),拦→[]→上层转 yfinance 深窗
    备源,不降级凑短窗。"""
    if bars is None:
        bars = hk_history_bars()
    for attempt in range(retries + 1):
        try:
            r = _direct_session().get(
                'https://ifzq.gtimg.cn/appstock/app/fqkline/get',
                params={'param': f'{code},day,,,{bars},qfq'}, timeout=15)
            d = (r.json().get('data') or {}).get(code) or {}
            days = d.get('day') or d.get('qfqday') or []
            rows = [(x[0], float(x[2])) for x in days if len(x) >= 3]
            if rows:
                return rows
        except Exception as e:
            # IA-DATA-W3(AC-01b): 原静默吞异常→留日志(标识+类型),重试语义零变化
            print(f"  ⚠️ 腾讯日K({code})第{attempt + 1}次失败: {type(e).__name__}: {str(e)[:80]}")
            if attempt < retries:
                time.sleep(2)
    return []

def _fetch_hk_tencent(ticker, name, bars=None):
    """方案1: 腾讯ifzq日K直连(2026-10-17: 恒指/国企连续4日429断供后的可靠主通道)

    bars: HK增量修复(2026-11-14)——默认 None→hk_history_bars()(深窗回补语义
    保留);日常增量路径传 hk_daily_bars()(320=WAF 上限)。"""
    code = HK_TX_CODE.get(ticker)
    if not code:
        return None
    rows = _tx_kline_rows(code, bars=bars)
    if not rows:
        return None
    m = _hk_metrics_from_daily([d for d, _ in rows], [c for _, c in rows])
    # 第七轮Layer2: 附加原始序列(事实引擎统一口径)
    m['series'] = {'dates': [str(d)[:10] for d, _ in rows],
                   'values': [float(c) for _, c in rows]}
    m['name'] = name
    return m

def _fetch_hk_yfinance(ticker, name, retries=1):
    """方案2: yfinance(走系统代理出境)。429限流时重试1次,仍失败交回调用方。

    Charter8(HK 深度补拉, 2026-11-10): 1mo→10y 深窗(与腾讯主路
    hk_history_bars()≈10年同档;腾讯 WAF 拦大 count 时的兜底路径);
    删 tail(400) 截断与额外 ytd 请求——指标改由 _hk_metrics_from_daily
    从全序列统一计算(与腾讯主路同口径),series 全量直通。"""
    last_err = None
    for attempt in range(retries + 1):
        try:
            data = yf.Ticker(ticker)
            hist = data.history(period='10y')
            if hist.empty:
                return None
            dates = [str(d.date()) for d in hist.index]
            closes = [float(v) for v in hist['Close'].values]
            m = _hk_metrics_from_daily(dates, closes)
            return {'name': name, 'close': m['close'], 'week_chg': m['week_chg'],
                    'ytd_chg': m['ytd_chg'], 'date': m['date'],
                    'series': {'dates': dates,
                               'values': [round(v, 6) for v in closes]}}
        except Exception as e:
            last_err = e
            time.sleep(15)
    if last_err:
        # Charter8: 补异常类型(与腾讯主路"标识+类型"纪律一致,AC-01b)
        print(f"  ⚠️ {name} yfinance失败({type(last_err).__name__}: {str(last_err)[:70]})")
    return None

def fetch_hk_indices(checkpoint=None):
    """采集港股指数: 腾讯小窗增量(主) → 持久化全窗(新鲜兜底) → yfinance 深窗(按需回补)

    HK增量修复(2026-11-14): 日常仅向腾讯请求 hk_daily_bars()(320) 小窗,
    与本地持久化 hk_index_history.json 增量合并后全窗直通;yfinance 从每日
    全量降为"持久化缺失/陈旧/深度不足"时的按需回补(治 Yahoo 限流+WAF 拦截
    双面)。三路皆无→None(Gate A 兜底)。

    Audit-R33 任务4: checkpoint=None → 旧行为;给出时逐 ticker 落盘持久化
    (深窗回补结果不因后续时间预算中断而丢失,下次运行续采)。"""
    print("\n📈 采集港股指数...")
    results = {}
    hist = _load_hk_history()
    hist_dirty = False
    target = hk_history_bars()

    for ticker, name in HK_INDICES.items():
        persisted = hist.get(ticker) or None
        # 路径1: 腾讯小窗增量(日常主路)
        fresh_rows = _fetch_hk_tencent(ticker, name, bars=hk_daily_bars())
        if fresh_rows is not None:
            merged = _merge_hk_series(
                persisted, fresh_rows.get('series'))
            hist[ticker] = merged
            hist_dirty = True
            # 深度不足(首跑/持久化丢失)→按需 yfinance 深窗回补一次
            if len(merged['dates']) < target // 2:
                print(f"  ℹ️ {name} 持久化深度不足"
                      f"({len(merged['dates'])}<{target // 2}),尝试深窗回补")
                deep = _fetch_hk_yfinance(ticker, name)
                if deep is not None:
                    merged = _merge_hk_series(merged, deep['series'])
                    hist[ticker] = merged
                    hist_dirty = True
                    src = '腾讯增量+yfinance回补'
                else:
                    src = '腾讯增量(深窗回补不可得,如实浅窗)'
            else:
                src = '腾讯增量'
            m = _hk_metrics_from_daily(merged['dates'], merged['values'])
            m['series'] = merged
            m['name'] = name
            results[ticker] = m
        elif persisted is not None and _hk_series_fresh(persisted):
            # 路径2: 腾讯失败但持久化新鲜→全窗直通,零 Yahoo 调用
            m = _hk_metrics_from_daily(persisted['dates'], persisted['values'])
            m['series'] = persisted
            m['name'] = name
            results[ticker] = m
            src = f"持久化(腾讯失败,末观测{persisted['dates'][-1]})"
        else:
            # 路径3: 按需 yfinance 深窗回补(持久化缺失/陈旧)
            print(f"  ⚠️ {name} 腾讯小窗失败且持久化不可用,转yfinance深窗回补")
            deep = _fetch_hk_yfinance(ticker, name)
            if deep is not None:
                merged = _merge_hk_series(persisted, deep['series'])
                hist[ticker] = merged
                hist_dirty = True
                m = _hk_metrics_from_daily(merged['dates'], merged['values'])
                m['series'] = merged
                m['name'] = name
                results[ticker] = m
                src = 'yfinance回补'
            else:
                print(f"  ❌ {name}: 三路均失败(腾讯小窗/持久化/yfinance)")
                continue
        r = results[ticker]
        wc = r.get('week_chg')
        tag = f" (周{wc:+.2f}%)" if wc is not None else ""
        print(f"  ✅ {name}: {r['close']}{tag} @{r.get('date')} "
              f"[{src}; n={len(r['series']['dates'])}]")
        if checkpoint is not None and hist_dirty:
            _save_hk_history(hist)     # Audit-R33 任务4: 逐 ticker 断点
            hist_dirty = False

    if hist_dirty:
        _save_hk_history(hist)
    return results

# ============ R058 SB_FLOW 备源回落登记(IA-P0-SB-FLOW-BACKUP-AC-v1.0) ============
# 现状(R010 登记): tushare moneyflow_hsgt 对本 token 返回「没有接口访问权限」
# (权限类拒,结构性)→ southbound 恒缺(source-persist)。经用户 L0-5 决策二
# (2026-11-05)+预授权③(东财免费公开源),仿 R049 EM 备源模式增设回落路:
# - 接口(登记冻结): akshare v1.18.64 stock_hsgt_hist_em(symbol='南向资金')
#   (datacenter-web.eastmoney.com, RPT_MUTUAL_DEAL_HISTORY, MUTUAL_TYPE=006,
#   免费公开零凭证);淘汰 stock_hsgt_fund_flow_summary_em——仅当日快照,无带
#   日期历史序列,无法做完结行选择与近5日累计。
# - 字段映射(登记冻结): 日期→YYYYMMDD(同 tushare 规格);当日成交净买额
#   (单位=亿港元,2026-11-05 实测锚定: 南向=港股通沪+港股通深 逐分恰等差
#   0.000000)×100→south_money(百万港元,tushare 路径现行口径);近5完结行
#   合计同系数→south_5d_total;north_* 键缺席如实(EM 北向净买披露 2024-08
#   起停止,summary 端点沪股通/深股通成交净买额实测恒0——不伪造)。
# - 回落条件(登记冻结): 主路三态失败(异常含权限拒/df None/len(df)==0)→
#   进入回落,逐次 print 如实记录;取值行=日期≤_em_max_date()(R051 动态
#   截止,复用 _em_settled_pairs,在途行禁用);回落无完结行/取值行NaN/异常
#   →None(=现行 source-persist 语义,如实缺失,禁假值禁重试凑数)。
# - 诚实标签: 主路产物零改动(不添 source 键);回落产物恰一新增键
#   source='akshare_em'(禁冒充 tushare);fact_engine 侧两值制见
#   scripts/fact_engine.py SB_FLOW 区登记。
def _fetch_southbound_em():
    """南向资金备源回落(东财港股通,akshare,免费公开,R058 登记)。
    仅经 fetch_southbound 在主路权限拒/空返回/异常后进入;返回
    {date(YYYYMMDD), south_money(百万港元), source='akshare_em',
     [south_5d_total(百万港元)]};north_* 不产(披露停止,缺席如实);
    无完结行/取值行缺值/异常→None。"""
    try:
        import akshare as ak
        with _no_proxy():
            df = ak.stock_hsgt_hist_em(symbol='南向资金')
        # 完结行选择复用 R049/R051 冻结 helper(列名桥接: 日期→date)
        settled = _em_settled_pairs(df.rename(columns={'日期': 'date'}))
        if not settled:
            print(f"  ⚠️ 东财南向回落无完结行(date≤{_em_max_date()})")
            return None
        last_d, idx = settled[-1]
        # 单位换算(登记冻结): 亿港元×100→百万港元(tushare 现行口径)
        vals = [pd.to_numeric(df.iloc[i]['当日成交净买额'], errors='coerce')
                for _, i in settled]
        net_yi = vals[-1]
        if pd.isna(net_yi):
            print(f"  ⚠️ 东财南向回落取值行({last_d})当日成交净买额缺失")
            return None
        result = {
            'date': last_d.replace('-', ''),                # 同 tushare 规格
            'south_money': round(float(net_yi) * 100.0, 2),
            'source': 'akshare_em',                          # 恰一新增键,禁冒充
        }
        if len(settled) >= 5:   # 近5完结行累计(同 tushare 路径语义,skipna)
            result['south_5d_total'] = round(
                float(sum(v for v in vals[-5:] if not pd.isna(v))) * 100.0, 2)
        print(f"  ✅ 南向资金(akshare-em): {result['south_money']:.2f} 百万 [{last_d}]")
        return result
    except Exception as e:
        print(f"  ⚠️ 东财南向回落失败: {e}")
        return None

def fetch_southbound():
    """采集南向资金: tushare(主) → 东财EM(备,R058)双通道"""
    print("\n💰 采集南向资金...")
    end_date, start_week, _ = get_trade_dates()

    try:
        df = _pro().moneyflow_hsgt(start_date=start_week, end_date=end_date)
        if df is None or len(df) == 0:
            print("  ⚠️ 无南向资金数据")
        else:
            # 确保数值列为数字类型
            for col in ['south_money', 'north_money']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            df = df.sort_values('trade_date')
            latest = df.iloc[-1]

            south = latest.get('south_money', 0)
            north = latest.get('north_money', 0)

            result = {
                'date': str(latest['trade_date']),
                'south_money': round(float(south), 2) if pd.notna(south) else 0,
                'north_money': round(float(north), 2) if pd.notna(north) else 0,
            }

            # 计算近5日累计
            if len(df) >= 5:
                recent = df.tail(5)
                result['south_5d_total'] = round(float(recent['south_money'].sum(skipna=True)), 2)
                result['north_5d_total'] = round(float(recent['north_money'].sum(skipna=True)), 2)

            print(f"  ✅ 南向资金: {result['south_money']:.2f} 百万")
            print(f"  ✅ 北向资金: {result['north_money']:.2f} 百万")
            return result

    except Exception as e:
        print(f"  ❌ 南向资金: {e}")

    # R058 备源回落(登记见上方): 主路权限拒/空返回/异常→东财EM,逐次如实记录
    print("  ↪️ 南向主路失败/空,转东财EM回落(akshare)")
    return _fetch_southbound_em()

def _fetch_margin_em():
    """G-P1-11 融资融券备源(IA-P1-WP-E, 2026-11-06): tushare 主路不可用→东财
    akshare 两所 margin(上交所 stock_margin_sse+深交所 stock_margin_szse)
    **同一信用交易日期**配对合计(两所同日合计口径,与主路 margin(trade_date)
    汇总同构);产出键与主路 1:1(date/rzye/rqye/rzye_billion/balance,元口径)
    +via='akshare_em' 恰一新增键(诚实源标签,禁冒充 tushare);单所数据缺席/
    配对窗内无共同日→None(如实缺席不填0,不以单所半合计冒充两所口径)。
    SSE 完结行按 _em_max_date() 截止择新,至多 3 候选日逐一配对(深交所单日
    查询,调用有界)。"""
    import akshare as ak
    try:
        with _no_proxy():
            end = datetime.now().strftime('%Y%m%d')
            start = (datetime.now() - timedelta(days=14)).strftime('%Y%m%d')
            sse = ak.stock_margin_sse(start_date=start, end_date=end)
    except Exception as e:
        print(f"  ❌ 融资融券备源上交所(stock_margin_sse): {type(e).__name__}: {str(e)[:120]}")
        return None
    if sse is None or len(sse) == 0 or '信用交易日期' not in getattr(sse, 'columns', []):
        print("  ⚠️ 融资融券备源: 上交所无数据/列漂移")
        return None
    cand = sorted({str(d)[:10].replace('-', '') for d in sse['信用交易日期']
                   if str(d)[:10].replace('-', '') <= _em_max_date().replace('-', '')},
                  reverse=True)[:3]
    for ymd in cand:
        try:
            with _no_proxy():
                szse = ak.stock_margin_szse(date=ymd)
            if szse is None or len(szse) == 0:
                continue
            sse_rows = sse[sse['信用交易日期'].astype(str).str.replace('-', '')
                          .str[:8] == ymd]
            if len(sse_rows) == 0:
                continue
            sse_row = sse_rows.iloc[-1]
            rzye = float(sse_row['融资余额']) + float(szse['融资余额'].sum())
            rqye = float(sse_row['融券余量金额']) + float(szse['融券余额'].sum())
            result = {
                'date': ymd,
                'rzye': round(rzye, 2),
                'rqye': round(rqye, 2),
                'rzye_billion': round(rzye / 1e8, 2),
                'balance': round((rzye + rqye) / 1e8, 2),
                'via': 'akshare_em',
            }
            print(f"  ✅ 融资融券备源(东财两所同日合计): balance={result['balance']} 亿元 ({ymd})")
            return result
        except Exception as e:
            print(f"  ❌ 融资融券备源深交所@{ymd}: {type(e).__name__}: {str(e)[:120]}")
            continue
    print("  ⚠️ 融资融券备源: 无两所同日配对(数据不足,如实缺席)")
    return None


def fetch_margin():
    """采集融资融券数据"""
    print("\n💳 采集融资融券...")

    # 尝试最近几天（可能有延迟）
    for days_back in range(0, 5):
        try:
            date = (datetime.now() - timedelta(days=days_back)).strftime('%Y%m%d')
            df = _pro().margin(trade_date=date)
            if df is not None and len(df) > 0:
                # 汇总所有交易所
                total_rzye = df['rzye'].sum()  # 融资余额
                total_rqye = df['rqye'].sum()  # 融券余额

                result = {
                    'date': date,
                    'rzye': round(float(total_rzye), 2),       # 融资余额（元）
                    'rqye': round(float(total_rqye), 2),       # 融券余额（元）
                    'rzye_billion': round(float(total_rzye) / 1e8, 2),  # 亿元
                    # IA-DATA-W3(AC-01a, 2026-11-04): 引擎/快照契约键 margin.balance
                    # (fact_engine L364-366 读 mg.get('balance');snapshot_builder 锚
                    # 'china.margin.balance')。口径=两融余额合计(融资rzye+融券rqye)
                    # ÷1e8→亿元,与注册 unit=cny_100m「融资融券余额存量(亿元)」同口径;
                    # 公式授权=IA-DATA-W3-AC-v1.0 §一(a)冻结合同(操作者代批,取代
                    # R008 §1.4-2a「须合同确认」的前置)。rzye/rqye/rzye_billion 原样保留。
                    'balance': round((float(total_rzye) + float(total_rqye)) / 1e8, 2),
                }
                print(f"  ✅ 融资余额: {result['rzye_billion']:.2f} 亿元 ({date})")
                return result
        except Exception as e:
            # IA-DATA-W3(AC-01b): 原裸 except:continue 吞异常(R008 U-1 根因)→
            # 具体异常类型+指标标识+日期留日志,失败可归因;重试语义零变化。
            print(f"  ❌ 融资融券(margin)@{date}: {type(e).__name__}: {str(e)[:120]}")
            continue

    # IA-P1-WP-E(G-P1-11, 2026-11-06): margin 备源切换——tushare 主路全失败→
    # 东财 akshare 两所备源(_fetch_margin_em);备源亦不可用→None(当日该节
    # 键缺席,不填0,§三(c) L81 纪律)。
    print("  ↪️ 融资融券主路不可用,转东财 akshare 备源")
    return _fetch_margin_em()

def _pe_value(row):
    """PE 取值双形态兼容(IA-DATA-W3 AC-01c): 扁平 pe 键(旧产物/部分载荷形态)
    或嵌套 pe_ttm 键(tushare index_dailybasic 实测形态)择一取值;均缺席/不可
    数值化→None(如实缺失,不造 0)。"""
    for k in ('pe', 'pe_ttm'):
        v = row.get(k)
        if v is not None:
            try:
                return round(float(v), 2)
            except (TypeError, ValueError) as e:
                print(f"  ⚠️ 估值PE取值失败(键={k}): {type(e).__name__}: {str(e)[:60]}")
                return None
    return None


def _fetch_valuation_em():
    """G-P1-11 估值备源(IA-P1-WP-E, 2026-11-06): tushare 估值主路无上证 PE
    可取→乐咕 akshare stock_market_pe_lg('上证')「平均市盈率」完结行(date≤
    _em_max_date(),在途行禁用)。范围仅限 SH_PE 扁平桥接 pe/date 两键(+via/
    note 口径披露),嵌套 per-index 对象不越域补造(身份纪律: 300/500/1000
    不冒充);无完结行/值不可数值化→None(如实缺席不填0)。
    口径披露: 乐咕=上证主板平均市盈率,注册 SH_PE=上证整体 PE(TTM) 近似
    代理,口径差异经 note 键如实标注,禁静默混同。"""
    import akshare as ak
    try:
        with _no_proxy():
            df = ak.stock_market_pe_lg(symbol='上证')
        # 完结行选择(乐咕列=「日期」,与东财 date 列名不同→就地选择,不改共享
        # 助手 _em_settled_pairs 的既有契约): date≤_em_max_date(),在途行禁用
        if df is None or len(df) == 0 or '日期' not in getattr(df, 'columns', []):
            print("  ⚠️ 估值备源: 乐咕无数据/列漂移")
            return None
        settled = sorted(((str(d)[:10], i) for i, d in enumerate(df['日期'])),
                         key=lambda p: p[0])
        settled = [p for p in settled if p[0] <= _em_max_date()]
        if not settled:
            print(f"  ⚠️ 估值备源: 乐咕无完结行(date≤{_em_max_date()})")
            return None
        d, idx = settled[-1]
        try:
            pe = round(float(df.iloc[idx]['平均市盈率']), 2)
        except (TypeError, ValueError):
            print(f"  ⚠️ 估值备源: 乐咕平均市盈率不可数值化: {df.iloc[idx]['平均市盈率']!r}")
            return None
        return {
            'pe': pe,
            'date': d.replace('-', ''),
            'via': 'akshare_legu',
            'note': '乐咕上证主板平均市盈率(近似口径;注册 SH_PE=上证整体PE(TTM),口径差异如实披露)',
        }
    except Exception as e:
        print(f"  ❌ 估值备源(stock_market_pe_lg): {type(e).__name__}: {str(e)[:120]}")
        return None


def fetch_valuation():
    """采集指数估值（PE/PB）"""
    print("\n📊 采集指数估值...")
    end_date, start_week, _ = get_trade_dates()
    results = {}
    sh_flat = {}   # SH_PE 扁平桥接键(pe/date),上证成功且 PE 可取时填充

    for code, name in VALUATION_INDICES.items():
        try:
            df = _pro().index_dailybasic(ts_code=code, start_date=start_week, end_date=end_date)
            if df is None or len(df) == 0:
                print(f"  ⚠️ {name}: 无估值数据")
                continue

            df = df.sort_values('trade_date')
            latest = df.iloc[-1]

            results[code] = {
                'name': name,
                'date': str(latest['trade_date']),
                'pe_ttm': round(float(latest.get('pe_ttm', 0)), 2),
                'pb': round(float(latest.get('pb', 0)), 2),
                'turnover_rate': round(float(latest.get('turnover_rate', 0)), 2),
                'total_mv': round(float(latest.get('total_mv', 0)), 2),
            }
            # IA-DATA-W3(AC-01c): 扁平桥接——引擎/快照契约键 valuation.pe+date
            # (fact_engine L367-369 只读扁平 pe;snapshot_builder 锚
            # 'china.valuation.pe')。身份纪律: 一律取上证(SH_PE_IDENTITY,
            # 注册 SH_PE=上证整体PE TTM),pe 取值经 _pe_value 兼容扁平 pe/嵌套
            # pe_ttm 两形态;上证失败或 PE 不可取→不写扁平键(如实缺失,不以
            # 300/500/1000 冒充)。嵌套 per-index 对象原样保留(两形态并存)。
            if code == SH_PE_IDENTITY:
                pe = _pe_value(latest)
                if pe is not None:
                    sh_flat = {'pe': pe, 'date': str(latest['trade_date'])}
            print(f"  ✅ {name}: PE={results[code]['pe_ttm']}, PB={results[code]['pb']}")

        except Exception as e:
            print(f"  ❌ {name}({code})估值: {type(e).__name__}: {str(e)[:120]}")

    if sh_flat:
        results.update(sh_flat)
        print(f"  ✅ 上证PE(扁平桥接 valuation.pe): {sh_flat['pe']} ({sh_flat['date']})")
    else:
        # IA-P1-WP-E(G-P1-11, 2026-11-06): SH_PE 扁平桥接键备源——主路无上证
        # PE 可取→乐咕备源(_fetch_valuation_em);备源亦不可用→扁平键缺席
        # (当日该键缺席,不填0,不以 300/500/1000 冒充上证身份)。
        print("  ↪️ 主路无上证PE,转乐咕 akshare 备源")
        em = _fetch_valuation_em()
        if em is not None:
            results.update(em)
            print(f"  ✅ 上证PE(备源扁平桥接 valuation.pe): {em['pe']} ({em['date']})")

    return results

def fetch_turnover():
    """采集沪深两市成交额"""
    print("\n📊 采集A股成交额...")

    # 方案1: Tushare指数日线 — amount字段单位千元
    try:
        today = datetime.now().strftime('%Y%m%d')
        # 查最近5个交易日
        df = _index_daily(ts_code='000001.SH', start_date=(datetime.now() - timedelta(days=10)).strftime('%Y%m%d'), end_date=today)
        if df is not None and len(df) > 0:
            latest = df.sort_values('trade_date').iloc[-1]
            sh_amount = float(latest.get('amount', 0))  # 千元
            sh_date = str(latest['trade_date'])

            # 同时获取深证成指成交额
            df2 = _index_daily(ts_code='399001.SZ', start_date=(datetime.now() - timedelta(days=10)).strftime('%Y%m%d'), end_date=today)
            sz_amount = 0
            if df2 is not None and len(df2) > 0:
                latest2 = df2.sort_values('trade_date').iloc[-1]
                sz_amount = float(latest2.get('amount', 0))

            total_billion = round((sh_amount + sz_amount) / 1e5, 2)  # 千元→亿元: ÷1e5
            sh_billion = round(sh_amount / 1e5, 2)
            sz_billion = round(sz_amount / 1e5, 2)

            result = {
                'date': sh_date,
                # 2026-10-17口径修正: 深侧来自399001.SZ深证成指(成分口径),
                # 非深市全市场(全市场须399106.SZ) — scope如实标注,不得写"沪深两市"
                'scope': '沪市全市场+深证成指成分(近似沪深两市)',
                'sh_amount_billion': sh_billion,
                'sz_amount_billion': sz_billion,
                'total_amount_billion': total_billion,
                'volume_billion': total_billion,  # 兼容旧字段名
                'label': f'成交额(近似两市): {total_billion:.0f}亿 (沪{sh_billion:.0f}全市场+深{sz_billion:.0f}成指成分)',
            }
            print(f"  ✅ 沪深两市成交额: {total_billion:.2f} 亿 (沪{sh_billion:.0f}+深{sz_billion:.0f})")
            return result
    except Exception as e:
        print(f"  ⚠️ Tushare成交额失败: {e}")

    # 方案2: 东财EM双取(R049 B-AC-02)——旧新浪回落(ak.stock_zh_index_daily)已删除:
    # 该端点根本没有 amount 列,回落 amount 恒=0(结构性缺陷,非数据源不可用)。
    # 本方案双取 sh000001+sz399001(禁代理直连),取值行 date≤_em_max_date()
    # (在途行禁用),amount 单位=元 → ÷1e8 round2 得亿元;source 标记=akshare_em
    # (禁冒充 tushare);口径与方案1一致(沪市全市场+深证成指成分)。
    try:
        import akshare as ak
        with _no_proxy():
            df_sh = ak.stock_zh_index_daily_em(symbol='sh000001')
            df_sz = ak.stock_zh_index_daily_em(symbol='sz399001')
        sh_row = _em_last_settled(df_sh)
        sz_row = _em_last_settled(df_sz)
        if sh_row is None or sz_row is None:
            print(f"  ⚠️ 东财成交额回落无完结行(date≤{_em_max_date()})")
            return None
        sh_date, sh_last = sh_row
        sz_date, sz_last = sz_row
        sh_amount = float(sh_last['amount'])  # 元
        sz_amount = float(sz_last['amount'])  # 元
        sh_billion = round(sh_amount / 1e8, 2)
        sz_billion = round(sz_amount / 1e8, 2)
        total_billion = round(sh_billion + sz_billion, 2)

        result = {
            'date': sh_date.replace('-', ''),  # 同方案1规格(YYYYMMDD)
            # 口径与方案1一致(深侧=399001成指成分,非深市全市场)
            'scope': '沪市全市场+深证成指成分(近似沪深两市)',
            'sh_amount_billion': sh_billion,
            'sz_amount_billion': sz_billion,
            'total_amount_billion': total_billion,
            'volume_billion': total_billion,  # 兼容旧字段名
            'source': 'akshare_em',
            'label': f'成交额(近似两市): {total_billion:.0f}亿 (沪{sh_billion:.0f}全市场+深{sz_billion:.0f}成指成分)',
        }
        print(f"  ✅ 成交额(akshare-em): sh≈{sh_billion:.2f} sz≈{sz_billion:.2f} total≈{total_billion:.2f} 亿")
        return result
    except Exception as e:
        print(f"  ⚠️ 东财成交额回落失败: {e}")

    return None

def _parse_sina_rt_line(line):
    """解析hq.sinajs.cn的rt_hkXXX行 → {close, prev_close, date}或None。
    格式: var hq_str_rt_hkHSI="HSI,恒生指数,开,昨收,高,低,现价,涨跌,涨跌%,...,日期,时间,...";
    字段序在HSI/HSAHP间存在52周高低位差,故日期用正则提取而非固定下标。"""
    try:
        if '"' not in line:
            return None
        p = line.split('"')[1].split(',')
        close, prev = float(p[6]), float(p[3])
        m = re.search(r'(\d{4})/(\d{2})/(\d{2})', line)
        if close <= 0 or not m:
            return None
        return {'close': close, 'prev_close': prev,
                'date': f"{m.group(1)}-{m.group(2)}-{m.group(3)}"}
    except Exception as e:
        # IA-DATA-W3(AC-01b): 原静默return None→留日志(标识+类型),解析契约零变化
        print(f"  ⚠️ 新浪rt行解析失败(rt_hk): {type(e).__name__}: {str(e)[:60]}")
        return None

def _ah_signal(close):
    """AH溢价分层信号(阈值与原逻辑一致)"""
    if close > 140:
        return '港股极度便宜'
    if close > 130:
        return '港股偏便宜'
    if close > 120:
        return '溢价正常'
    return '溢价收敛，港股不再便宜'

def _ah_result(close, date, via):
    signal = _ah_signal(close)
    print(f"  ✅ AH溢价指数(HSAHP): {close:.2f} ({signal}) [{via}]")
    return {
        'index_name': '恒生AH股溢价指数(HSAHP)',
        'date': date,
        'close': round(close, 2),
        'signal': signal,
        'interpretation': f'AH溢价 {close:.1f}，>100表示A股相对H股有溢价',
    }

def fetch_ah_premium():
    """采集恒生AH股溢价指数(HSAHP): 新浪rt直连(主) → 新浪日K(备) → 东财(末选保留)
    2026-10-17修复: 东财push2当前网络不可达; 原新浪spot方案列表里根本没有AH溢价行(从未生效)"""
    print("\n📊 采集AH溢价指数...")

    # 方案1: 新浪rt_hkHSAHP直连(需Referer,GBK编码)
    try:
        r = _direct_session().get('https://hq.sinajs.cn/list=rt_hkHSAHP',
                                  headers={'Referer': 'https://finance.sina.com.cn'},
                                  timeout=10)
        r.encoding = 'gbk'
        parsed = _parse_sina_rt_line(r.text)
        if parsed and 100 < parsed['close'] < 200:
            return _ah_result(parsed['close'], parsed['date'], '新浪直连')
        if parsed:
            print(f"  ⚠️ 新浪HSAHP值异常: {parsed['close']}，尝试备用方案")
    except Exception as e:
        print(f"  ⚠️ 新浪直连失败: {str(e)[:80]}")

    # 方案2: akshare新浪日K(禁代理直连)
    try:
        import akshare as ak
        with _no_proxy():
            df = ak.stock_hk_index_daily_sina(symbol="HSAHP")
        if df is not None and len(df) > 0:
            latest = df.iloc[-1]
            close = float(latest['close'])
            date = pd.to_datetime(latest['date']).strftime('%Y-%m-%d')
            if 100 < close < 200:
                return _ah_result(close, date, '新浪日K')
            print(f"  ⚠️ 新浪日KHSAHP值异常: {close}，尝试备用方案")
    except Exception as e:
        print(f"  ⚠️ 新浪日K失败: {str(e)[:80]}")

    # 方案3: 东财akshare(禁代理;当前网络不可达,保留给东财可达的部署环境)
    try:
        import akshare as ak
        with _no_proxy():
            df = ak.stock_hk_index_daily_em(symbol="HSAHP")
        if df is not None and len(df) > 0:
            latest = df.iloc[-1]
            close = float(latest['latest']) if 'latest' in df.columns else float(latest['close'])
            if 100 < close < 200:
                return _ah_result(close, str(latest['date'])[:10], '东财')
            print(f"  ⚠️ 东财HSAHP值异常: {close}")
    except Exception as e:
        print(f"  ⚠️ 东财方式失败: {str(e)[:80]}")

    print("  ❌ AH溢价指数采集失败")
    return None

# ============ IA-P1-WP-E G-P1-14..18 CN 宏观采集(2026-11-06) ============
# 免费公开源经 akshare(DESIGN §三(b) L73 预授权③直用面);境内端点一律
# _no_proxy() 直连(2026-10-17 修复纪律);逐端点独立 try/except 容错——单端点
# 失败仅该键缺席(§三(c) L81 降级→MISSING 披露,不填0)。月频指标观测日=
# 统计期(月),未发布≠缺失(§三(c) L82,registry freshness 60 天窗)。端点列
# 锚与口径=REPORT §零.6A 终值表(akshare 1.18.47 安装包源码离线实读)。
# 产出键与 registry 新增 8 条目 1:1: lpr_1y/lpr_5y/cpi_yoy/ppi_yoy/pmi_mfg/
# sf_flow/new_loans/omo_7d;各值 {'date','value','source'} 诚实源标签。

def _norm_month(s):
    """中文月份列归一: '2026年10月'→'2026-10';不可解析→None(如实弃行)。"""
    m = re.search(r'(\d{4})\s*年\s*(\d{1,2})', str(s))
    return '%s-%02d' % (m.group(1), int(m.group(2))) if m else None


def _tushare_monthly_last(df, col):
    """tushare 月度宏观行选(R6-D1 纯函数,零网络可注入): month='YYYYMM' 行中
    取 col 有值的最大月→('YYYY-MM-DD' 月末观测日, float)。语义同 _macro_last:
    NaN/不可数值化/月份不可归一跳行,返回序向不依赖;无有值行→None。"""
    if df is None or len(df) == 0:
        return None
    import calendar
    best = None
    for _, row in df.iterrows():
        m = re.fullmatch(r'(\d{4})(\d{2})', str(row.get('month') or '').strip())
        if not m or not 1 <= int(m.group(2)) <= 12:
            continue
        v = row.get(col)
        if v is None:
            continue
        try:
            fv = float(v)
        except (TypeError, ValueError):
            continue
        if fv != fv or fv in (float('inf'), float('-inf')):
            continue                     # R8-01: 非有限值(NaN/±Inf)不入采集史
        ym = (m.group(1), m.group(2))
        if best is None or ym > (best[0], best[1]):
            best = (m.group(1), m.group(2), fv)
    if best is None:
        return None
    y, mo = int(best[0]), int(best[1])
    return ('%04d-%02d-%02d' % (y, mo, calendar.monthrange(y, mo)[1]), best[2])


# ============ tushare 月度宏观跨进程响应缓存(R10, 2026-11-12) ============
# 实证(RESUME 2②/P2 台账"R10 候选"): tushare cn_cpi/cn_ppi 同 api 1 次/分
# 限流(与 index_daily 同族,FIX3 §六附则)。午夜窗自采与流水线=两个独立进程,
# 同分钟各拉一次→第二次必限流拒→cpi_yoy/ppi_yoy 假性缺席→Gate A 误拒
# (生产 07:00 单跑不受影响)。_index_daily 闸门(方案A)是进程内单调钟,护不
# 到跨进程——故加文件级响应缓存: 成功且可解析的响应按 api 落 data/cache/,
# TTL 内(默认600s;月度数据发布周期≥28天,窗口保守)复用免二次直连。
# 纪律: 缓存只做同窗去重,不做陈旧回退——直连失败仍如实缺席(禁0填充不变);
# 缓存读/写任何失败=透明跳过,绝不影响采集主路。
TUSHARE_MONTHLY_CACHE_TTL_SECONDS = 600
TUSHARE_MONTHLY_CACHE_DIR = os.path.join(DATA_DIR, 'cache')


def _monthly_cache_path(api_name):
    """缓存档路径(R10): data/cache/tushare_monthly_{api}.json。api 名白名单
    校验(现役仅 cn_cpi/cn_ppi 两面)防路径注入;目录经模块常量注入=测试密闭。"""
    if api_name not in ('cn_cpi', 'cn_ppi'):
        raise ValueError('unknown monthly api: %r' % (api_name,))
    return os.path.join(TUSHARE_MONTHLY_CACHE_DIR,
                        'tushare_monthly_%s.json' % api_name)


def _cache_load_rows(path, now_ts, ttl=TUSHARE_MONTHLY_CACHE_TTL_SECONDS):
    """读月度响应缓存(纯文件面,零网络): {'fetched_at','rows'} 且 0≤age≤ttl
    →rows(list[dict]);其余(缺档/坏JSON/rows 非list或空/fetched_at 坏值/
    超龄/钟偏未来)→None。零异常外泄。"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            obj = json.load(f)
        rows = obj.get('rows')
        fetched_at = obj.get('fetched_at')
        if (isinstance(rows, list) and rows
                and isinstance(fetched_at, (int, float))
                and 0 <= now_ts - float(fetched_at) <= ttl):
            return rows
    except Exception:
        pass
    return None


def _cache_save_rows(path, df, now_ts):
    """写月度响应缓存(尽力而为): DataFrame→records(NaN→None,JSON 严格可序列
    化)+fetched_at,先写 .tmp.{pid} 再 os.replace 原子换名(两进程并发写=后写
    者胜,两者皆合法)。任何失败→False,不外泄不影响主路。"""
    try:
        rows = df.astype(object).where(df.notna(), None).to_dict('records')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = '%s.tmp.%d' % (path, os.getpid())
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump({'fetched_at': now_ts, 'rows': rows}, f,
                      ensure_ascii=False)
        os.replace(tmp, path)
        return True
    except Exception:
        return False


MOFCOM_SHRZGM_URL = 'https://data.mofcom.gov.cn/datamofcom/front/gnmy/shrzgmQuery'

# ══ Audit-R20(2026-11-19): CN 宏观全史序列(EM 直连 + PBOC 公告走查) ════════
# 12组36格四地地图问句正式使用: CN_CPI_YOY/CN_PPI_YOY/CN_LPR_1Y/CN_OMO_7D
# 需要历史序列(旧 fetch_macro 只出当期点值)。源:
#  - 东方财富 datacenter API(keyless;与 akshare macro_china_* 同源端点
#    家族,R9 mofcom curl 直取同款先例): RPT_ECONOMY_CPI.NATIONAL_SAME /
#    RPT_ECONOMY_PPI.BASE_SAME = 全国同比(%)。实测 2026-11-19: CPI 226 月
#    (2007-10..2026-10,2026-10=0.7 与 tushare 点值一致),PPI 250 月
#    (2006-01..2026-10,2026-10=5.7 一致)。
#  - PBOC 公开市场业务交易公告页(www.pbc.gov.cn,官方免费;urllib 直连
#    502→curl 子进程直取同 R9 先例): 列表页/17081-N.html 翻页,逐公告解析
#    表格 期限/操作利率 行,7天行→中标利率。公告逐日缓存
#    data/cache/pboc_omo/ 防生产每日重走全史(首回填后日增量≈1 页)。
#  - LPR: akshare macro_china_lpr 全量 df(与点值通道同端点,只加全史面)。
EM_CPI_URL = ('https://datacenter-web.eastmoney.com/api/data/v1/get'
              '?reportName=RPT_ECONOMY_CPI&columns=ALL&pageSize=500'
              '&pageNumber=1&sortColumns=REPORT_DATE&sortTypes=-1')
EM_PPI_URL = ('https://datacenter-web.eastmoney.com/api/data/v1/get'
              '?reportName=RPT_ECONOMY_PPI&columns=ALL&pageSize=500'
              '&pageNumber=1&sortColumns=REPORT_DATE&sortTypes=-1')
PBC_OMO_LIST_URL = ('http://www.pbc.gov.cn/zhengcehuobisi/125207/125213/'
                    '125431/125475/index.html')
PBC_OMO_PAGE_URL = ('http://www.pbc.gov.cn/zhengcehuobisi/125207/125213/'
                    '125431/125475/17081-{page}.html')
PBC_OMO_CACHE_DIR = os.path.join(DATA_DIR, 'cache', 'pboc_omo')
# 走查回看窗(自然日): 覆盖地图问句 12 个月前锚+缓冲;env 可覆盖
# (生产若嫌重可调小——公告缓存使增量日耗≈当日 1 公告)。
_OMO_BACKFILL_DAYS = int(os.environ.get('CN_OMO_HISTORY_DAYS') or 500)


# ============ 采集时间预算(Audit-R33 任务4,2026-11-25) =====================
# 冷启动无缓存复现(R32 基线 f053afe,2026-11-24 21:43 本机): 步骤2 ≈710 秒
# (步骤上限 900 秒;A 股 6 指数×61 秒限流间隔≈305 秒+港股首跑深窗回补+央行
# 公告走查 291 篇≈111 秒),余量≈190 秒;旧实现只在整个采集结束后写一次档,
# 步骤超时被杀=**整档丢失**,且 A 股进度无断点——源端迟缓时每次冷跑都从零
# 重来,核心采集可能永远完不成。
# 修法(登记冻结):
# - 本采集器自带时间预算: 默认 800 秒,env CN_COLLECTOR_BUDGET_SECONDS 可覆盖;
#   须低于 run_weekly 步骤上限 900 秒(留解释器启动/导入与被中断的 curl 子进程
#   收尾余量;≥880 视为配置不当,启动时告警)。
# - 到期处置依次: ① 阶段间/逐项协作式停止(未开始阶段=skipped_budget;A 股逐
#   指数、公告走查逐公告——已取到的不丢);② 看门狗(SIGALRM)兜底——卡在无
#   超时的网络调用里也按时返回;③ 断点: A 股逐指数进度写
#   data/cache/china_a_share_ckpt.json(同交易日窗、同历史窗口,且该项当日
#   bar 已定型才可续——收盘前取到的当日 bar 不续;已取到的指数不重复限流
#   等待;全部阶段完成后清除),港股全窗与央行公告沿用既有持久化
#   (data/daily/hk_index_history.json、data/cache/pboc_omo/),下次运行接着采。
# - 核心阶段(A股/港股指数)被截断 → 不写主日档(明知不完整的核心面不得充当
#   当日采集;下游按「采集失败」既有口径处置),诊断性部分面写 logs/,退出码 1;
#   其后阶段(南向/两融/估值/成交额/AH溢价/宏观)被截断 → 写主日档并随档披露
#   collection_status,退出码 0(与既有「非核心端点失败=该键缺席」同口径)。
# - 预算≤0 或平台无 SIGALRM → 预算关闭/看门狗关闭,行为同旧实现。
def _budget_from_env(raw, default=800.0):
    """env 预算秒数解析: 空/非数/非有限 → 默认(不因配置笔误让采集崩)。"""
    try:
        v = float(str(raw).strip())
    except (TypeError, ValueError):
        return default
    return v if v == v and v not in (float('inf'), float('-inf')) else default


CN_COLLECTOR_BUDGET_SECONDS = _budget_from_env(
    os.environ.get('CN_COLLECTOR_BUDGET_SECONDS'))
_CN_STAGE_RESERVE_SECONDS = 5.0          # 阶段开始/逐指数开始前至少剩余的秒数
_CN_OMO_FETCH_RESERVE_SECONDS = 15.0     # 公告走查单次取网前至少剩余的秒数
# A 股断点只用于恢复(不作同日再跑的缓存): 可续=同交易日窗+同历史窗口+逐指数有
# 取数时刻+该项最后一根 bar 已定型(沿用 EM 取值行截止口径 _em_max_date 16:10 HKT:
# 收盘前取到的当日 bar 未定型,不续);旧格式断点(无取数时刻)不续;全部阶段完成后清除。
ASHARE_CHECKPOINT_PATH = os.path.join(DATA_DIR, 'cache', 'china_a_share_ckpt.json')
_STAGE_STATUS = {}        # 阶段内断点/截断状态(函数返回值契约不变,状态走此表)
_OMO_WALK_STATUS = {}     # 央行公告走查状态(随 collection_status 披露)


class BudgetExceeded(BaseException):
    """时间预算耗尽(看门狗/协作式检查抛出)。继承 BaseException: 采集函数内
    大量 `except Exception` 端点容错分支不得吞掉它之后继续取网。"""


class CollectionBudget:
    """采集时间预算(单调钟): limit_sec≤0 → 关闭(remaining 恒为 None=不限)。"""

    def __init__(self, limit_sec=None):
        self.limit_sec = (CN_COLLECTOR_BUDGET_SECONDS if limit_sec is None
                          else float(limit_sec or 0))
        self.t0 = time.monotonic()

    def elapsed(self):
        return time.monotonic() - self.t0

    def remaining(self):
        if self.limit_sec <= 0:
            return None
        return self.limit_sec - self.elapsed()

    @property
    def deadline(self):
        """协作式截止时刻(单调钟;预算关闭→None)。"""
        return self.t0 + self.limit_sec if self.limit_sec > 0 else None

    def exhausted(self, reserve=_CN_STAGE_RESERVE_SECONDS):
        """协作式检查: 预算开启且剩余<reserve → True。"""
        rem = self.remaining()
        return rem is not None and rem < reserve


_BUDGET_TIMER = {'armed': False}


def _arm_watchdog(budget):
    """看门狗: 预算开启且平台有 SIGALRM → 定时器到期在主线程抛 BudgetExceeded
    (只在本脚本主线程调用;不可用=静默跳过,协作式检查仍在)。返回是否已武装。"""
    import signal
    _BUDGET_TIMER['armed'] = False
    rem = budget.remaining()
    if rem is None or not hasattr(signal, 'SIGALRM') or rem <= 0:
        return False

    def _on_alarm(signum, frame):
        raise BudgetExceeded('time budget exhausted (%.0fs)' % budget.limit_sec)

    try:
        signal.signal(signal.SIGALRM, _on_alarm)
        signal.setitimer(signal.ITIMER_REAL, rem)
    except (ValueError, OSError, AttributeError):
        return False
    _BUDGET_TIMER['armed'] = True
    return True


def _disarm_watchdog():
    """解除看门狗(保存/退出前必须调用,避免写入途中被预算打断)。"""
    import signal
    if not _BUDGET_TIMER['armed']:
        return
    try:
        signal.setitimer(signal.ITIMER_REAL, 0)
    except (ValueError, OSError, AttributeError):
        pass
    _BUDGET_TIMER['armed'] = False


def _ashare_checkpoint_read():
    """读 A 股断点原件(缺档/坏档→None;不报错、不取网)。"""
    try:
        with open(ASHARE_CHECKPOINT_PATH, 'r', encoding='utf-8') as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def _ashare_bar_settled(end_date, fetched_ts):
    """取数时刻 fetched_ts(Unix 秒)下,end_date(YYYYMMDD)当日 bar 是否已定型:
    沿用 EM 取值行截止口径(_em_max_date: 时刻≥16:10 HKT→当日已完结)——截止日
    ≥end_date 即定型;时刻不可读→False(不续)。"""
    hkt = timezone(timedelta(hours=8))
    try:
        cut = _em_max_date(datetime.fromtimestamp(float(fetched_ts), hkt))
        return cut >= '%s-%s-%s' % (str(end_date)[:4], str(end_date)[4:6],
                                    str(end_date)[6:8])
    except (TypeError, ValueError, OverflowError, OSError):
        return False


def _ashare_checkpoint_usable(obj, end_date, window_start):
    """断点里可续的指数集合: ①断点窗与本次一致(同交易日窗 end_date+同历史
    窗口,即仅同日可续)②指数在清单内③有取数时刻④该项最后一根 bar 已定型
    (最后一根 bar 不是 end_date 当日=休市日/当日尚无 bar;或是当日 bar 但取数
    时刻已达当日完结口径)。旧格式断点(无取数时刻)一律不续。"""
    if not (obj and obj.get('end_date') == end_date
            and obj.get('window_start') == window_start
            and isinstance(obj.get('items'), dict)):
        return set()
    fetched_all = obj.get('fetched_at')
    fetched_all = fetched_all if isinstance(fetched_all, dict) else {}
    out = set()
    for code, item in obj['items'].items():
        if code not in A_SHARE_INDICES or not isinstance(item, dict):
            continue
        try:
            fetched = float(fetched_all.get(code))
        except (TypeError, ValueError):
            continue
        if fetched != fetched or fetched in (float('inf'), float('-inf')):
            continue
        series = item.get('series')
        dates = series.get('dates') if isinstance(series, dict) else None
        last_bar = str(dates[-1]).replace('-', '') if dates else ''
        if last_bar == str(end_date) and not _ashare_bar_settled(end_date, fetched):
            continue
        out.add(code)
    return out


def _ashare_checkpoint_load(end_date, window_start, now_ts=None):
    """读 A 股断点里可续的指数 → {code: item}(缺档/坏档/窗不一致/未定型→{}:
    不续,不报错,不取网)。now_ts 仅为旧签名兼容,不参与判定。"""
    obj = _ashare_checkpoint_read()
    if not obj:
        return {}
    usable = _ashare_checkpoint_usable(obj, end_date, window_start)
    # 清单序返回(断点内顺序不定,结果与旧路径同形)
    return {c: obj['items'][c] for c in A_SHARE_INDICES if c in usable}


def _ashare_checkpoint_save(end_date, window_start, items, fetched_at=None):
    """写 A 股断点(原子换名;任何失败=透明跳过,不影响采集主路)。
    fetched_at={code: 取数时刻 Unix 秒}——可续性据它判定(见 _ashare_checkpoint_usable)。"""
    try:
        os.makedirs(os.path.dirname(ASHARE_CHECKPOINT_PATH), exist_ok=True)
        tmp = '%s.tmp.%d' % (ASHARE_CHECKPOINT_PATH, os.getpid())
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump({'end_date': end_date, 'window_start': window_start,
                       'saved_at': time.time(), 'items': items,
                       'fetched_at': dict(fetched_at or {})}, f,
                      ensure_ascii=False)
        os.replace(tmp, ASHARE_CHECKPOINT_PATH)
    except Exception:
        pass


def _ashare_checkpoint_clear():
    """清 A 股断点(采集全部阶段完成后调用;断点只用于恢复)。任何失败=透明跳过。"""
    try:
        os.remove(ASHARE_CHECKPOINT_PATH)
    except OSError:
        pass


def _curl_get(url, max_time='30'):
    """curl 子进程 GET(R9 mofcom 先例: 本机 python ssl 栈与部分境内源
    TLS 协商即断,curl 可通)。失败→None。"""
    import subprocess
    try:
        r = subprocess.run(['curl', '-s', '-L', '--noproxy', '*', '--max-time',
                            max_time, '-H', 'User-Agent: Mozilla/5.0', url],
                           capture_output=True, timeout=40)
        if r.returncode != 0 or not r.stdout:
            return None
        return r.stdout
    except Exception:
        return None


def _em_series_rows(url, value_field):
    """EM datacenter API → [('YYYY-MM-01', value)] 升序(纯解析+单页拉取;
    pageSize=500>源端全量 250 行,无翻页需求;失败→None)。"""
    raw = _curl_get(url)
    if raw is None:
        return None
    try:
        data = json.loads(raw.decode('utf-8'))
        rows = ((data.get('result') or {}).get('data')) or []
    except Exception:
        return None
    out = {}
    for row in rows:
        d = (row.get('REPORT_DATE') or '')[:7]
        v = row.get(value_field)
        if len(d) == 7 and v is not None:
            try:
                fv = float(v)
            except (TypeError, ValueError):
                continue
            if fv == fv and fv not in (float('inf'), float('-inf')):
                out['%s-01' % d] = fv
    if not out:
        return None
    return [(k, out[k]) for k in sorted(out)]


def _pboc_rate_cell_value(cell):
    """利率单元格 → 数值;带量纲(亿元等)或空→None。

    Audit-R21 任务2: 操作量为零的公告日,表格行形=期限|投标量|中标量
    (无操作利率列),首量格 '0亿元' 曾被旧解析误读为利率 0.0——序列里
    23 个零值全部来源于此。修法=利率格必须为纯数值(可带 %),含
    量纲字样一律拒收(该期限当日无成交利率,如实无观测)。"""
    if not cell or re.search(r'亿元|万亿', cell):
        return None
    m = re.fullmatch(r'([0-9]+(?:\.[0-9]+)?)%?', cell)
    if not m:
        return None
    v = float(m.group(1))
    # 政策操作利率无 0 值形态(注册表校验域 [0.1,5]):裸 '0' 量格(零操作
    # 日无量纲变体)同样拒收,不产 0.0 观测。
    return None if v == 0.0 else v


def _pboc_omo_parse_announcement(html_text):
    """单篇公告 HTML → {'7天': rate|None, '隔夜': rate|None}。

    表格行形(2026-11-19 实测): 期限|操作利率|投标量|中标量,如
    ['7天', '1. 40 %', '…亿元', '…亿元'](操作利率含空格变体→剥离后解析;
    操作量为零日=期限|投标量|中标量,利率列缺席→该期限 None——
    Audit-R21: 2026-08-19 等日操作量为零,当日成交利率留空,禁以 0 冒充)。
    2026-11-02 换锚后公告含 隔夜 行(操作利率列)→ '隔夜' 键产出
    CN_POLICY_OVERNIGHT 序列。同篇同期限多行不同率→取首见(源端无此形,
    防御)。"""
    rows = re.findall(r'<tr[^>]*>([\s\S]*?)</tr>', html_text or '')
    out = {'7天': None, '隔夜': None}
    for r in rows:
        cells = [re.sub(r'<[^>]+>|&nbsp;|\s+', '', c)
                 for c in re.findall(r'<t[dh][^>]*>([\s\S]*?)</t[dh]>', r)]
        if len(cells) >= 2 and cells[0] in ('7天', '隔夜') \
                and out.get(cells[0]) is None:
            v = _pboc_rate_cell_value(cells[1])
            if v is not None:
                out[cells[0]] = v
    return out


def _pboc_omo_walk(back_days=None, deadline=None):
    """PBOC 公告走查 → {'7天': [(date, rate)], '隔夜': [(date, rate)]} 升序。

    列表页 index.html + 17081-N.html 翻页(每页 20 条,新→旧),取公告
    链接(URL 17 位日期码);回看窗=公告日≥today−back_days(默认 500 自然
    日,覆盖地图 12 个月前锚);逐公告先查本地缓存(data/cache/pboc_omo/
    YYYYMMDD.html)命中不取网,未中→curl 取+写缓存。窗口内无该期限行的
    公告日不产观测;操作量为零日=无成交利率(解析层拒收量纲格,
    Audit-R21 任务2——七天序列 23 个 0.0 伪影的根修,08-19 等日利率
    留空)。隔夜行自 2026-11-02 换锚后在场 → CN_POLICY_OVERNIGHT。

    Audit-R33 任务4: deadline(单调钟时刻)给出时为协作式时间预算——取网
    前剩余不足则停(列表页: 停止翻页;公告: 新→旧逐篇,止于当前篇,余下
    留待下次运行——已取公告在缓存=断点),已缓存公告不论预算一律处理;
    状态入 _OMO_WALK_STATUS(status complete/partial、stop_reason
    budget、stopped_at、各计数)。"""
    import datetime as _dt
    import time as _time
    back_days = back_days if back_days is not None else _OMO_BACKFILL_DAYS
    today = _dt.date.today()
    floor = (today - _dt.timedelta(days=back_days)).isoformat()
    _t0 = _time.monotonic()
    _OMO_WALK_STATUS.clear()
    _OMO_WALK_STATUS.update({'status': 'running', 'stop_reason': None,
                             'requested_from': floor})

    def _out_of_time():
        return deadline is not None and (
            _time.monotonic() + _CN_OMO_FETCH_RESERVE_SECONDS > deadline)

    links = {}
    pages = 0
    list_stop = False
    for page in range(1, 40):
        if _out_of_time():
            list_stop = True
            break
        url = PBC_OMO_LIST_URL if page == 1 else PBC_OMO_PAGE_URL.format(
            page=page)
        html = (_curl_get(url) or b'').decode('utf-8', errors='ignore')
        pages += 1
        got = re.findall(
            r'href="(/zhengcehuobisi/125207/125213/125431/125475/'
            r'(\d{17,})/index\.html)"', html)
        new = 0
        for href, code in got:
            iso = '%s-%s-%s' % (code[:4], code[4:6], code[6:8])
            if iso >= floor and href not in links:
                links[href] = iso
                new += 1
        oldest = min(links.values()) if links else None
        if new == 0 or (oldest and oldest < floor):
            break
        _time.sleep(0.15)
    out = {'7天': {}, '隔夜': {}}
    processed = []

    def _absorb(html_text, iso):
        rates = _pboc_omo_parse_announcement(html_text)
        for tenor, rate in rates.items():
            if rate is not None:
                out[tenor][iso] = rate
        processed.append(iso)

    pending = []
    cache_hits = 0
    for href, iso in sorted(links.items(), key=lambda x: x[1], reverse=True):
        code = href.rstrip('/').split('/')[-2]   # …/{17位日期码}/index.html
        cache = os.path.join(PBC_OMO_CACHE_DIR, '%s.html' % code)
        html_text = None
        try:
            with open(cache, 'r', encoding='utf-8', errors='ignore') as f:
                html_text = f.read()
        except Exception:
            pass
        if html_text is None:
            pending.append((href, iso, code))
        else:
            cache_hits += 1
            _absorb(html_text, iso)
    fetched = failed = 0
    stop_reason = 'budget' if list_stop else None
    stopped_at = None
    for href, iso, code in pending:      # 新→旧;预算到期即止,余下留待下次
        if _out_of_time():
            stop_reason = 'budget'
            stopped_at = iso
            print(f"  ⏹️ 央行公告走查: 时间预算耗尽,止于 {iso}"
                  f"(余 {len(pending) - fetched - failed} 篇待续,"
                  f"下次运行自缓存续采)")
            break
        cache = os.path.join(PBC_OMO_CACHE_DIR, '%s.html' % code)
        raw = _curl_get('http://www.pbc.gov.cn' + href)
        if raw is None:
            failed += 1
            continue
        html_text = raw.decode('utf-8', errors='ignore')
        try:
            os.makedirs(PBC_OMO_CACHE_DIR, exist_ok=True)
            tmp = '%s.tmp.%d' % (cache, os.getpid())
            with open(tmp, 'w', encoding='utf-8') as f:
                f.write(html_text)
            os.replace(tmp, cache)
        except Exception:
            pass
        _time.sleep(0.15)
        fetched += 1
        _absorb(html_text, iso)
    _OMO_WALK_STATUS.update({
        'status': 'complete' if stop_reason is None else 'partial',
        'stop_reason': stop_reason, 'stopped_at': stopped_at,
        'pages': pages, 'links_in_window': len(links),
        'cache_hits': cache_hits, 'fetched': fetched, 'fetch_failed': failed,
        'processed': len(processed),
        'covered_from': min(processed) if processed else None,
        'pending_left': len(pending) - fetched - failed,
        'sec': round(_time.monotonic() - _t0, 1)})
    return {k: [(d, v) for d, v in sorted(vs.items())]
            for k, vs in out.items()}

def fetch_macro_series(budget=None):
    """Audit-R20: CN 宏观四序列全史(→顶层 series 节;与点值通道并存,
    点值权威不变)。返回 {metric_id: {'dates','values'}};逐端点容错,
    失败→该键缺席(禁 0 填充)。

    Audit-R33 任务4: budget 给出时央行公告走查按其截止时刻协作式停止
    (状态见 _OMO_WALK_STATUS);其余端点零变化。"""
    out = {}

    rows = _em_series_rows(EM_CPI_URL, 'NATIONAL_SAME')
    if rows:
        out['CN_CPI_YOY'] = {'dates': [d for d, _ in rows],
                             'values': [v for _, v in rows]}
        print(f"  ✅ series.CN_CPI_YOY: n={len(rows)} "
              f"({rows[0][0]}..{rows[-1][0]}, 末值 {rows[-1][1]})")
    else:
        print("  ⚠️ series.CN_CPI_YOY: EM 源失败/无有效行(缺席)")

    rows = _em_series_rows(EM_PPI_URL, 'BASE_SAME')
    if rows:
        out['CN_PPI_YOY'] = {'dates': [d for d, _ in rows],
                             'values': [v for _, v in rows]}
        print(f"  ✅ series.CN_PPI_YOY: n={len(rows)} "
              f"({rows[0][0]}..{rows[-1][0]}, 末值 {rows[-1][1]})")
    else:
        print("  ⚠️ series.CN_PPI_YOY: EM 源失败/无有效行(缺席)")

    try:
        import akshare as ak
        with _no_proxy():
            df = ak.macro_china_lpr()
        lpr = []
        for _, row in df.iterrows():
            raw_d = str(row.get('TRADE_DATE')).strip()
            if re.fullmatch(r'\d{8}', raw_d):      # 'YYYYMMDD' 归一防御
                raw_d = '%s-%s-%s' % (raw_d[:4], raw_d[4:6], raw_d[6:])
            d = _norm_date(raw_d)
            v = row.get('LPR1Y')
            if d is None or v is None:
                continue
            try:
                fv = float(v)
            except (TypeError, ValueError):
                continue
            if fv == fv and fv not in (float('inf'), float('-inf')):
                lpr.append((d, fv))
        lpr.sort()
        if lpr:
            dedup = {}
            for d, v in lpr:
                dedup[d] = v          # 同日多行取末(源端无此形,防御)
            ks = sorted(dedup)
            out['CN_LPR_1Y'] = {'dates': ks, 'values': [dedup[k] for k in ks]}
            print(f"  ✅ series.CN_LPR_1Y: n={len(ks)} "
                  f"({ks[0]}..{ks[-1]}, 末值 {dedup[ks[-1]]})")
        else:
            print("  ⚠️ series.CN_LPR_1Y: 无有效行(macro_china_lpr.LPR1Y)")
    except Exception as e:
        print(f"  ❌ series.CN_LPR_1Y(macro_china_lpr): "
              f"{type(e).__name__}: {str(e)[:120]}")

    omo = _pboc_omo_walk(deadline=(budget.deadline if budget is not None
                                   else None))
    seven = omo.get('7天') if isinstance(omo, dict) else omo
    if seven:
        out['CN_OMO_7D'] = {'dates': [d for d, _ in seven],
                            'values': [v for _, v in seven]}
        _zeros = sum(1 for _, v in seven if v == 0)
        print(f"  ✅ series.CN_OMO_7D: n={len(seven)} "
              f"({seven[0][0]}..{seven[-1][0]}, 末值 {seven[-1][1]}"
              f"{', 零值=' + str(_zeros) + '(应为0——操作量为零日无成交利率,不产观测)' if _zeros else ''})")
    else:
        print("  ⚠️ series.CN_OMO_7D: 公告走查无 7 天行(缺席)")
    on = omo.get('隔夜') if isinstance(omo, dict) else None
    if on:
        # Audit-R21 任务2: 2026-11-02 换锚——隔夜逆回购成为操作目标锚,
        # 七天工具与 LPR 单列(registry/地图政策面同口径)。
        out['CN_POLICY_OVERNIGHT'] = {'dates': [d for d, _ in on],
                                      'values': [v for _, v in on]}
        print(f"  ✅ series.CN_POLICY_OVERNIGHT: n={len(on)} "
              f"({on[0][0]}..{on[-1][0]}, 末值 {on[-1][1]})")
    else:
        print("  ⚠️ series.CN_POLICY_OVERNIGHT: 公告走查无隔夜行"
              "(2026-11-02 前形态,缺席)")
    return out


def _shrzgm_rows():
    """社融增量源端直取(R9,2026-11-12;商务部 mofcom POST;curl 子进程)。

    为何不经 akshare.macro_china_shrzgm(): 本机 python ssl 栈=LibreSSL 2.8.3,
    与 mofcom TLS 协商即断(SSLError 'No cipher can be selected'/握手 EOF,
    2026-11-12 实测;curl 走 LibreSSL 3.3.6 可通)——同一端点经系统 curl 取
    (零第三方依赖,curl=系统工具;境内源 --noproxy 直连与 _no_proxy 同理)。
    失败(非 0/空响应/非 JSON 数组)→None,调用方如实缺席。"""
    import subprocess
    try:
        r = subprocess.run(['curl', '-s', '--noproxy', '*', '-X', 'POST',
                            MOFCOM_SHRZGM_URL, '--max-time', '25'],
                           capture_output=True, timeout=35)
        if r.returncode != 0 or not r.stdout:
            return None
        rows = json.loads(r.stdout.decode('utf-8'))
        return rows if isinstance(rows, list) else None
    except Exception:
        return None


def _shrzgm_last(rows):
    """mofcom 社融行选(R9 纯函数,零网络可注入): rows(list[dict])中取
    tiosfs(社会融资规模增量,亿元;键序↔akshare 1.18.47 macro_china_shrzgm
    列序:date/ndbab/entrustloan/forcloan/rmblaon/bibae/tiosfs/sfinfe/
    trustloan)有值的最大 date('YYYYMM')→('YYYY-MM', float)。语义同
    _macro_last_month: NaN/不可数值化/月份不可归一跳行,序向不依赖;
    无有值行→None。"""
    if not rows:
        return None
    best = None
    for row in rows:
        m = re.fullmatch(r'(\d{4})(\d{2})', str(row.get('date') or '').strip())
        if not m or not 1 <= int(m.group(2)) <= 12:
            continue
        v = row.get('tiosfs')
        if v is None:
            continue
        try:
            fv = float(v)
        except (TypeError, ValueError):
            continue
        if fv != fv or fv in (float('inf'), float('-inf')):
            continue                     # R8-01: 非有限值(NaN/±Inf)不入采集史
        ym = m.group(1) + '-' + m.group(2)
        if best is None or ym > best[0]:
            best = (ym, fv)
    return best


def _norm_date(s):
    """宏观日期列归一(序向/格式不依赖): 'YYYY-MM-DD'/'YYYY/M/D'/'2026年10月
    10日'→'YYYY-MM-DD';月粒度('2026年10月'/'2026-10')→'YYYY-MM'(观测日=
    统计期,月频语义);不可解析→None。"""
    s = str(s).strip()
    m = re.search(r'(\d{4})\s*[-/年]\s*(\d{1,2})(?:\s*[-/月]\s*(\d{1,2})\s*日?)?', s)
    if not m:
        return None
    y, mo, d = m.group(1), int(m.group(2)), m.group(3)
    return '%s-%02d-%02d' % (y, mo, int(d)) if d else '%s-%02d' % (y, mo)


def _macro_last(df, date_col, value_col):
    """宏观序列最新有值观测(全行扫描取最大归一日期,端点返回序向不依赖;
    值不可数值化/NaN/日期不可归一→跳行;全无有值行→None)。"""
    if df is None or len(df) == 0:
        return None
    best = None
    for _, row in df.iterrows():
        d = _norm_date(row.get(date_col))
        v = row.get(value_col)
        if d is None or v is None:
            continue
        try:
            fv = float(v)
        except (TypeError, ValueError):
            continue
        if fv != fv or fv in (float('inf'), float('-inf')):
            continue                     # R8-01: 非有限值(NaN/±Inf)不入采集史
        if best is None or d > best[0]:
            best = (d, fv)
    return best


def _macro_last_month(df, month_col, value_col):
    """月度宏观序列最新有值观测(月份列 '2026年10月' 形态→'YYYY-MM' 归一;
    语义同 _macro_last: NaN/不可数值化跳行,序向不依赖)。"""
    if df is None or len(df) == 0:
        return None
    best = None
    for _, row in df.iterrows():
        d = _norm_month(row.get(month_col))
        v = row.get(value_col)
        if d is None or v is None:
            continue
        try:
            fv = float(v)
        except (TypeError, ValueError):
            continue
        if fv != fv or fv in (float('inf'), float('-inf')):
            continue                     # R8-01: 非有限值(NaN/±Inf)不入采集史
        if best is None or d > best[0]:
            best = (d, fv)
    return best


def _parse_omo_rows(lines, today=None):
    """央行公开市场业务交易公告行纯解析(G-P1-18;可注入零网络): 行序列中
    过滤 7 天期逆回购操作行→[(日期, 利率)] 升序去重。行形锚(公告短语形态,
    测试合成 fixture 同构): '2026年11月5日 …7天期逆回购操作…中标利率1.80'。
    today='YYYY-MM-DD' 给出→仅取观测行≤今日(测试冻结钟);无'7天'/'逆回购'
    词对/利率不可解→该行跳过(如实缺席);无有效行→[]。"""
    rows = {}
    for line in lines:
        s = str(line)
        if ('7天' not in s) or ('逆回购' not in s):
            continue
        d = _norm_date(s)
        m = re.search(r'中标利率[^0-9]{0,6}([0-9]+(?:\.[0-9]+)?)', s)
        if d is None or m is None:
            continue
        if today is not None and d > today:
            continue
        rows[d] = float(m.group(1))
    return [(d, rows[d]) for d in sorted(rows)]


def _omo_rows_default():
    """G-P1-18 源默认装载器: 免费公开现成接口缺席(akshare 1.18.47 源码 grep
    逆回购零命中[实取·离线])→PENDING 披露返回 None(禁造数禁网络;接线留
    后续轮,操作者排程面)。"""
    print("  ⏳ CN_OMO_7D 源未接线(PENDING): 公告装载待后续轮接线,本节如实缺席")
    return None


def fetch_omo_7d(rows=None, today=None):
    """G-P1-18 采集点: rows=公告行序列注入(纯解析面);rows=None→默认装载器
    (_omo_rows_default)。返回 {'date','value','source':'pboc_omo'} 或 None。"""
    if rows is None:
        rows = _omo_rows_default()
        if rows is None:
            return None
    parsed = _parse_omo_rows(rows, today=today)
    if not parsed:
        return None
    d, v = parsed[-1]
    return {'date': d, 'value': round(v, 2), 'source': 'pboc_omo'}


def fetch_macro():
    """采集 CN 宏观序列(G-P1-14..17+G-P1-18 装配点;IA-P1-WP-E): 返回 dict,
    产出键与 registry 新增 8 条目 1:1(lpr_1y/lpr_5y/cpi_yoy/ppi_yoy/pmi_mfg/
    sf_flow/new_loans/omo_7d);逐端点容错,单端点失败→该键缺席(禁 0 填充)。"""
    print("\n🏦 采集 CN 宏观序列...")
    import akshare as ak
    out = {}

    # G-P1-14 LPR(东财;TRADE_DATE/LPR1Y/LPR5Y 列锚)
    try:
        with _no_proxy():
            df = ak.macro_china_lpr()
        for key, col in (('lpr_1y', 'LPR1Y'), ('lpr_5y', 'LPR5Y')):
            got = _macro_last(df, 'TRADE_DATE', col)
            if got is not None:
                out[key] = {'date': got[0], 'value': round(got[1], 2),
                            'source': 'akshare_em'}
                print(f"  ✅ {key}: {out[key]['value']} ({out[key]['date']})")
            else:
                print(f"  ⚠️ {key}: 无有值行(macro_china_lpr.{col})")
    except Exception as e:
        print(f"  ❌ LPR(macro_china_lpr): {type(e).__name__}: {str(e)[:120]}")

    # G-P1-15 CPI/PPI 同比(R6-D1 换源: 金十 macro_china_cpi/ppi_yearly 停更于
    # 2025-08[R5 盘点;akshare 1.18.47 金十族实测 cpi 尾 2008-02/ppi 尾 2006-01/
    # cpi_monthly 尾 2025-09 皆死]→tushare pro cn_cpi.nt_yoy/cn_ppi.ppi_yoy
    # (现有 token/现有依赖;月度→月末观测日;失败=如实缺席,不回退停更源)。
    # R10 跨进程缓存: TTL 内复用成功响应免同分钟双耗限流(见缓存节注释);
    # 仅缓存"可解析"响应(got 非 None),列漂移/空表不入缓存。
    for key, api_name, col in (('cpi_yoy', 'cn_cpi', 'nt_yoy'),
                               ('ppi_yoy', 'cn_ppi', 'ppi_yoy')):
        try:
            cache_path = _monthly_cache_path(api_name)
            cached = _cache_load_rows(cache_path, time.time())
            if cached is not None:
                df = pd.DataFrame(cached, columns=['month', col])
                got = _tushare_monthly_last(df, col)
                if got is not None:
                    print(f"  ♻️ {key}: tushare 月度缓存命中"
                          f"(age≤{TUSHARE_MONTHLY_CACHE_TTL_SECONDS}s,免同分钟限流直连)")
            else:
                with _no_proxy():
                    df = getattr(_pro(), api_name)(
                        start_date='20200101', end_date=datetime.now().strftime('%Y%m%d'))
                got = _tushare_monthly_last(df, col)
                if got is not None:
                    _cache_save_rows(cache_path, df, time.time())
            if got is not None:
                out[key] = {'date': got[0], 'value': round(got[1], 2),
                            'source': 'tushare_pro'}
                print(f"  ✅ {key}: {out[key]['value']} ({out[key]['date']})")
            else:
                print(f"  ⚠️ {key}: 无有值行({api_name}.{col})")
        except Exception as e:
            print(f"  ❌ {key}({api_name}): {type(e).__name__}: {str(e)[:120]}")

    # G-P1-16 制造业 PMI(东财;月份/制造业-指数 列锚,中文月份归一)
    try:
        with _no_proxy():
            df = ak.macro_china_pmi()
        got = _macro_last_month(df, '月份', '制造业-指数')
        if got is not None:
            out['pmi_mfg'] = {'date': got[0], 'value': round(got[1], 2),
                              'source': 'akshare_em'}
            print(f"  ✅ pmi_mfg: {out['pmi_mfg']['value']} ({out['pmi_mfg']['date']})")
        else:
            print("  ⚠️ pmi_mfg: 无有值行(macro_china_pmi.制造业-指数)")
    except Exception as e:
        print(f"  ❌ PMI(macro_china_pmi): {type(e).__name__}: {str(e)[:120]}")

    # G-P1-17 社融增量(商务部 mofcom 直取 R9;date='YYYYMM'/tiosfs 列锚)
    try:
        got = _shrzgm_last(_shrzgm_rows())
        if got is not None:
            out['sf_flow'] = {'date': got[0], 'value': round(got[1], 2),
                              'source': 'mofcom_direct'}
            print(f"  ✅ sf_flow: {out['sf_flow']['value']} ({out['sf_flow']['date']})")
        else:
            print("  ⚠️ sf_flow: 无有值行(mofcom.shrzgmQuery.tiosfs)")
    except Exception as e:
        print(f"  ❌ 社融(mofcom.shrzgmQuery): {type(e).__name__}: {str(e)[:120]}")

    # G-P1-17 新增人民币贷款(东财;月份/当月 列锚)
    try:
        with _no_proxy():
            df = ak.macro_china_new_financial_credit()
        got = _macro_last_month(df, '月份', '当月')
        if got is not None:
            out['new_loans'] = {'date': got[0], 'value': round(got[1], 2),
                                'source': 'akshare_em'}
            print(f"  ✅ new_loans: {out['new_loans']['value']} ({out['new_loans']['date']})")
        else:
            print("  ⚠️ new_loans: 无有值行(macro_china_new_financial_credit.当月)")
    except Exception as e:
        print(f"  ❌ 新增贷款(macro_china_new_financial_credit): {type(e).__name__}: {str(e)[:120]}")

    # G-P1-18 7天逆回购(无现成接口→身份预注册;公告行纯解析可注入)
    try:
        got = fetch_omo_7d()
        if got is not None:
            out['omo_7d'] = got
            print(f"  ✅ omo_7d: {got['value']} ({got['date']})")
    except Exception as e:
        print(f"  ❌ omo_7d: {type(e).__name__}: {str(e)[:120]}")

    return out


# ── Audit-R6 条目3(R6-02): CN 月度全史正式生成器 ──────────────────────
# 基线 dcb4b17 缺口: fetch_macro 单点通道丢弃全史(macro_china_pmi/
# macro_china_new_financial_credit 端点本返全量行,仅取末行);历史依赖
# macro_20261117.json 手工 cn_history_addendum 补丁,下一日 FRED 刷新档
# 不含 CN 键→历史加载 0 行。本函数=正式入口: 全史拉取+归一(月度锚=
# 统计期月首 YYYY-MM-01,与 R5 既有 226 月序列口径逐位一致)+口径/来源/
# 获取时间/修订口径随档;由 macro_collector.merge_cn_history 随每档续存
# (美国宏观刷新不遮蔽中国历史)。
_CN_HISTORY_SPEC = [
    # (registry_id, akshare 端点, 月份列, 值列, 单位, 定义, 源注记, 修订口径)
    ('CN_PMI_MFG', 'macro_china_pmi', '月份', '制造业-指数', 'index_point',
     '国家统计局制造业 PMI(制造业-指数列)',
     'akshare macro_china_pmi(东方财富),与 fetch_macro 单点通道同源端点',
     'PMI 不追溯修订(统计局初值即终值口径)'),
    ('CN_NEW_LOANS', 'macro_china_new_financial_credit', '月份', '当月',
     'cny_100m',
     '对实体经济发放的人民币贷款当月新增(人民银行社融口径,'
     '非全口径新增贷款——全口径对照见 registry calc 注记)',
     'akshare macro_china_new_financial_credit(东方财富),与 fetch_macro '
     '单点通道同源端点',
     '贷款按央行初值,不追溯修订'),
]


def _macro_month_rows(df, month_col, value_col):
    """月度宏观全史行(Audit-R6 R6-02 纯函数,零网络可注入): 月份列
    '2026年10月'→统计期月首 'YYYY-MM-01' 锚;NaN/不可数值化/月份不可归一
    跳行;同月多行取首见(源端无此形,防御);升序去重输出。"""
    if df is None or len(df) == 0:
        return []
    rows = {}
    for _, row in df.iterrows():
        d = _norm_month(row.get(month_col))
        v = row.get(value_col)
        if d is None or v is None:
            continue
        try:
            fv = float(v)
        except (TypeError, ValueError):
            continue
        if fv != fv or fv in (float('inf'), float('-inf')):
            continue                     # R8-01: 非有限值(NaN/±Inf)不入采集史
        key = '%s-01' % d
        if key not in rows:
            rows[key] = fv
    return [(k, rows[k]) for k in sorted(rows)]


def fetch_macro_history():
    """R6-02: CN_PMI_MFG/CN_NEW_LOANS 月度全史正式生成(采集+归一+口径)。

    返回 {registry_id: item}(端点失败→该键缺席,禁 0 填充/禁造史);item 形
    与 R5 addendum 既有消费面同构(date/value/prev/frequency/unit/definition/
    source_note/series)并增 provenance(source/fetched_at/coverage/
    revision_policy/generated_by)——版本与来源可追溯(验收 §4)。
    """
    import akshare as ak
    out = {}
    fetched_at = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    for (rid, api, mcol, vcol, unit, definition, source_note,
         rev_policy) in _CN_HISTORY_SPEC:
        try:
            with _no_proxy():
                df = getattr(ak, api)()
            rows = _macro_month_rows(df, mcol, vcol)
            if not rows:
                print(f"  ⚠️ {rid}: 全史无有值行({api}.{vcol})")
                continue
            dates = [r[0] for r in rows]
            values = [r[1] for r in rows]   # 源值直存(不预舍入): 与 R5 已核
            # 验 226 月序列逐位一致(舍入会引入第 5 位小数起漂移,2015 段
            # 源值自带小数;锚点核验口径=源端发布精度)
            out[rid] = {
                'date': dates[-1], 'value': values[-1],
                'prev': values[-2] if len(values) > 1 else None,
                'frequency': 'monthly', 'unit': unit,
                'definition': definition, 'source_note': source_note,
                'series': {'dates': dates, 'values': values},
                'provenance': {
                    'source': 'akshare_em(%s)' % api,
                    'fetched_at': fetched_at,
                    'coverage': {'n': len(dates), 'first': dates[0],
                                 'last': dates[-1]},
                    'revision_policy': rev_policy,
                    'observation_anchor': '统计期月首(YYYY-MM-01)',
                    'generated_by': 'china_market_collector.fetch_macro_history'
                                    '(Audit-R6 R6-02 正式入口)',
                },
            }
            print(f"  ✅ {rid}: 全史 n={len(dates)} "
                  f"({dates[0]}..{dates[-1]}, 末值 {values[-1]})")
        except Exception as e:
            print(f"  ❌ {rid}({api}): {type(e).__name__}: {str(e)[:120]}")
    return out


def save_data(all_data):
    """保存数据(Audit-R25 任务1: 同日降级重采集经 daily_face_guard_write
    守卫——序列丢失面转存 superseded/,不覆盖同日完整可重放面)。"""
    import research_provenance as rp
    date_str = datetime.now().strftime('%Y%m%d')
    daily_dir = os.path.join(DATA_DIR, 'daily')

    filepath, status, note = rp.daily_face_guard_write(
        daily_dir, 'china', date_str, all_data, indent=2)
    if status == 'degraded_diverted':
        print(f"\n⚠️ 同日降级面({note})未覆盖完整档,转存: {filepath}")
        return filepath

    size = os.path.getsize(filepath)
    print(f"\n💾 数据已保存: {filepath} ({size} 字节)")
    return filepath

# ============ 阶段表与主程序(Audit-R33 任务4) ============================
# 阶段顺序与旧主程序 1..9 逐步一致;核心阶段=A股/港股指数(Gate A 核心面)。
_STAGES = (
    ('a_share_indices', 'A股指数', True),
    ('hk_indices', '港股指数', True),
    ('southbound', '南向资金', False),
    ('margin', '融资融券', False),
    ('valuation', '指数估值', False),
    ('turnover', '成交额', False),
    ('ah_premium', 'AH溢价', False),
    ('macro', 'CN宏观序列', False),
    ('series', 'CN宏观全史序列', False),
)


def _stage_call(name, budget):
    """阶段调用工厂: 仅三个阶段带新参(A股断点+预算/港股断点/宏观全史预算),
    其余零参调用与旧主程序同形。预算关闭(≤0)→三阶段同样零参=旧行为
    (不写断点、不逐 ticker 落盘)。"""
    on = budget.remaining() is not None
    if name == 'a_share_indices':
        if not on:
            return fetch_a_share_indices
        return lambda: fetch_a_share_indices(checkpoint='ckpt', budget=budget)
    if name == 'hk_indices':
        if not on:
            return fetch_hk_indices
        return lambda: fetch_hk_indices(checkpoint='ckpt')
    if name == 'series':
        if not on:
            return fetch_macro_series
        return lambda: fetch_macro_series(budget=budget)
    return {'southbound': fetch_southbound, 'margin': fetch_margin,
            'valuation': fetch_valuation, 'turnover': fetch_turnover,
            'ah_premium': fetch_ah_premium, 'macro': fetch_macro}[name]


def _count_items(got):
    if isinstance(got, dict):
        return len(got)
    return 1 if got else 0


def _collect_stages(all_data, budget):
    """按阶段表顺序采集,逐阶段记 {sec, items, status}。

    status ∈ ok / cut_by_budget(看门狗在本阶段内触发)/ skipped_budget(预算
    已耗尽,本阶段未执行)。返回 (stages, 核心阶段被截断?——含核心阶段因
    预算未执行的情形)。非预算异常照旧
    外泄(脚本崩=失败,不吞;与旧主程序同口径)。"""
    stages = {}
    stopped = False
    core_cut = False
    for name, label, core in _STAGES:
        if not stopped and budget.exhausted():
            stopped = True
        if stopped:
            if core:
                core_cut = True     # 核心阶段未执行=同样不得写主日档
            stages[name] = {'sec': 0.0, 'items': None, 'status': 'skipped_budget'}
            print(f"\n⏭️  {label}: 时间预算已耗尽,本阶段未执行")
            continue
        rem = budget.remaining()
        print("\n⏱️  [%s] 开始(剩余预算 %s)" % (
            label, "不限" if rem is None else "%.0f 秒" % rem))
        if name == 'series':
            _OMO_WALK_STATUS.clear()     # 本阶段走查状态从头记
        t_s = time.monotonic()
        try:
            got = _stage_call(name, budget)()
        except BudgetExceeded:
            stopped = True
            if core:
                core_cut = True
            stages[name] = {'sec': round(time.monotonic() - t_s, 1),
                            'items': None, 'status': 'cut_by_budget'}
            print(f"⏹️  {label}: 时间预算耗尽,本阶段中断"
                  f"(已取到的进度在断点/缓存,下次运行续采)")
            continue
        stages[name] = {'sec': round(time.monotonic() - t_s, 1),
                        'items': _count_items(got), 'status': 'ok'}
        all_data[name] = got
    return stages, core_cut


def _collection_status(budget, stages, core_cut):
    """随档披露的采集状态节(纯装配): 预算/阶段表/A股断点/公告走查。"""
    ash = dict(_STAGE_STATUS.get('a_share_indices') or {})
    walk = dict(_OMO_WALK_STATUS)
    if walk.get('status') == 'running':
        # 走查途中被看门狗中断(函数未返回): 如实记 partial
        walk.update({'status': 'partial', 'stop_reason': 'budget(watchdog)'})
    return {
        'budget': {'limit_sec': budget.limit_sec,
                   'elapsed_sec': round(budget.elapsed(), 1),
                   'exhausted': bool(budget.exhausted(0.0))},
        'stages': stages,
        'core_cut_by_budget': bool(core_cut or ash.get('cut_by_budget')),
        'a_share_checkpoint': {'resumed': list(ash.get('resumed') or []),
                               'cut_by_budget': bool(ash.get('cut_by_budget'))},
        'omo_walk': (walk if walk and 'series' in stages
                     and stages['series']['status'] != 'skipped_budget' else None),
    }


def main():
    print("=" * 60)
    print("📊 A股/港股数据采集 v2.1")
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("数据源: Tushare + 腾讯/新浪直连 + yfinance(备) + akshare")
    print("=" * 60)

    all_data = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'version': '2.1',
    }

    # Audit-R33 任务4: 采集时间预算(协作式检查+看门狗);保存前必须解除看门狗
    budget = CollectionBudget()
    if CN_COLLECTOR_BUDGET_SECONDS >= 880:
        print(f"⚠️ CN_COLLECTOR_BUDGET_SECONDS={CN_COLLECTOR_BUDGET_SECONDS:.0f} "
              f"已到流水线步骤上限(900 秒)余量: 预算起不到保护作用")
    _arm_watchdog(budget)
    try:
        stages, core_cut = _collect_stages(all_data, budget)
    finally:
        _disarm_watchdog()
    all_data['collection_status'] = _collection_status(budget, stages, core_cut)

    if all_data['collection_status']['core_cut_by_budget']:
        # 核心阶段被预算截断: 不写主日档(明知不完整的核心面不得充当当日采集;
        # 下游按「采集失败」既有口径处置);诊断性部分面写 logs/,退出码 1。
        try:
            log_dir = os.path.join(PROJECT_DIR, 'logs')
            os.makedirs(log_dir, exist_ok=True)
            diag = os.path.join(log_dir, 'china_partial_%s.json'
                                % datetime.now().strftime('%Y%m%dT%H%M%S'))
            with open(diag, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            where = f"诊断性部分面: {diag}"
        except OSError as e:
            where = f"诊断性部分面写入失败: {e}"
        print(f"\n❌ 核心阶段(A股/港股)被时间预算截断: 不写主日档;{where}")
        print("⚠️ 下次运行自断点续采(A股逐指数断点/港股全窗持久化)")
        sys.exit(1)

    # 保存
    save_data(all_data)

    # Audit-R33 任务4: 全部阶段完成→清 A 股断点(断点只用于恢复;同日再跑=
    # 重新取网,与旧行为同形);仍有阶段未完整执行→保留,下次运行续采后腾出预算。
    if all(st.get('status') == 'ok' for st in stages.values()):
        _ashare_checkpoint_clear()
    else:
        print("♻️ A股断点保留(仍有阶段未完整执行): 下次运行续采")

    # 汇总
    print("\n" + "=" * 60)
    print("📋 采集汇总")
    print("=" * 60)
    a_count = len(all_data.get('a_share_indices', {}))
    hk_count = len(all_data.get('hk_indices', {}))
    print(f"  A股指数: {a_count} 个")
    print(f"  港股指数: {hk_count} 个")
    print(f"  南向资金: {'✅' if all_data.get('southbound') else '❌'}")
    print(f"  融资融券: {'✅' if all_data.get('margin') else '❌'}")
    print(f"  指数估值: {'✅' if all_data.get('valuation') else '❌'}")
    print(f"  成交额:   {'✅' if all_data.get('turnover') else '❌'}")
    print(f"  AH溢价:   {'✅' if all_data.get('ah_premium') else '❌'}")
    print(f"  CN宏观:   {len(all_data.get('macro') or {})} 项")
    cut = [n for n, st in stages.items() if st['status'] != 'ok']
    if cut:
        print(f"\n⚠️ 时间预算: {len(cut)} 个阶段未完整执行({', '.join(cut)}),"
              f"详见随档 collection_status;下次运行续采")
    print("\n🎉 采集完成！")


if __name__ == '__main__':
    main()
