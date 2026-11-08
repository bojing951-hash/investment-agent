#!/usr/bin/env python3
"""真实数据验收(IA-P0-2-W5重构版; 前身spec §18第七轮Phase 5)

目的: 用**独立外部可信来源**核验采集-事实引擎-研究快照全链路的真实输出,
并独立复算关键金融计算(周/MTD/YTD口径与基准日语义)。

W5重构(IA-P0-2-W5-DEV-v1.0)八项要点:
- W5-02 八项外部对照(UST 2Y/10Y/30Y, BTC, GOLD_F, SHCOMP, SPX, WTI_F)逐项
  独立结构化: 日期逐指标匹配(不得用10Y日期代替2Y/30Y)、期限列各归各、
  UST以百分点差计bp(|ours_pct−ext_pct|×100≤3bp,绝非相对%);
  FRED SPX必须同观测日,取"最近一条"属错日→NOT_VERIFIED;
  PAXG(现货代币代理)不得按容差证明GOLD_F(COMEX期货)→NOT_COMPARABLE(留参考偏差);
  FRED DCOILWTICO(现货)vs WTI_F(期货)无基差调整证据→NOT_COMPARABLE;
  新浪为实时快照: 日期不匹配或盘中价非收盘→NOT_VERIFIED,同日收盘口径才比较;
  BTC核验UTC日K边界(granularity=86400,K线起点=该UTC日00:00Z)与USD计价。
- W5-03 independent_period_returns强化(输入校验+ISO周跨年/前月末/上年末
  非交易日锚定),复算逐项输出期末/独立基准/引擎基准/公式/两值/差异/容差/判定;
  双方均无基准=INSUFFICIENT_HISTORY(不是成功复算);基准日期不一致=FAIL;
  利率/点差/计数类不得套用价格百分比公式(单位纪律前置拦截)。
- W5-04 综合结果三态 PASS/FAIL/NOT_VERIFIED: 只有真实独立可比通过才计PASS;
  NOT_COMPARABLE/NOT_VERIFIED/INSUFFICIENT_HISTORY/SKIPPED均不算PASS;
  覆盖门槛(利率≥1项UST真PASS+市场≥2项真PASS+外部总PASS≥4+复算PASS≥2)
  不满足→整体NOT_VERIFIED; --skip-external=离线诊断,恒NOT_VERIFIED;
  Gate A非PASS/DEGRADED仍严格阻断(exit 2)。退出码: 0=PASS/2=FAIL/3=NOT_VERIFIED。
- W5-05 证据保全: 代码SHA/执行时间/数据日/研究截止/快照ID/Gate A/输入文件
  SHA-256/指标身份与价格口径/外部来源URL(密钥脱敏)+HTTP状态+正文SHA+字节数
  /外部观测日与实际返回值/获取时间UTC/容差与舍入规则/逐项结果/综合/未验证清单;
  外部历史若已修订,如实注明核验当前取得值。

FIX1(IA-P0-2-W5-FIX1-DEV-v1.0,自失败基线78f4c9a增量,只修七项确定性缺陷):
- FIX1-01 FRED密钥失败路径脱敏: 统一sanitize_text(api_key=查询参数模式+运行时
  已知密钥明文登记,含URL编码形式);异常字符串进结构化证据前先全量脱敏再
  截断(截断边界不得截出密钥片段),保留异常类型/HTTP状态码等必要诊断;
  JSON/MD/LOG/外部原始正文写盘前最终密钥清扫(纵深防御)。
- FIX1-02 收益复算价格字段校验: 期末价格(事实value vs 独立复算close,相对容差
  RECOMPUTE_PRICE_TOL_PCT=0.01%金融数值精度,覆盖采集显示值2位小数舍入)+
  基准价格(引擎basis_value vs 独立basis_value)逐期核对;独立有基准时引擎
  必须提供basis_date与basis_value(缺失即FAIL);收益率百分点一致不得替代
  价格字段一致。
- FIX1-03 完整复算门槛: WEEK/MTD/YTD三期全部独立一致才算完整复算PASS
  (complete_recompute=True);部分成功→INSUFFICIENT_HISTORY+部分复核明细
  (不冒充完整PASS);整体PASS另要求≥1条真实资产序列完成三期完整独立复算
  (原覆盖门槛UST/市场/外部总数/复算数量不降低)。
- FIX1-04 SHCOMP历史盘中价阻断: 取消"仅执行当日才检查收盘时间"的历史日期
  豁免——任意报价日期,无时间字段或时间<15:30:00(北京时间)均无法证明收盘
  口径,一律NOT_VERIFIED;历史报价比较能力保留(日期匹配且收盘口径可证时
  正常进入价格比较)。
- FIX1-05 输出路径安全: --data-dir与--out-dir路径关系检查(相同/输出在输入
  内部/输出为输入祖先/..或符号链接真实路径重叠一律拒绝;realpath+commonpath,
  绝非字符串前缀比较),在任何输出写入/快照构建/真实外部API调用之前执行;
  非法→明确拒绝+exit 2+零写入+零网络请求+不修改输入。
- FIX1-06 八项检查来源绑定: 每检查稳定check_id(EXT-UST-2Y/EXT-UST-10Y/
  EXT-UST-30Y/EXT-BTC/EXT-GOLD-F/EXT-SHCOMP/EXT-SPX/EXT-WTI-F,不重复不
  缺失);ours保留fact既有source;外部侧绑定external_source/source_identity/
  evidence_ids(三UST共享年度官方CSV证据;FRED SPX/WTI各自证据;Coinbase
  BTC/PAXG按真实请求各自记录);无来源明确为空,不构造虚假ID;所有引用的
  evidence_id均可在external_evidence中定位。
- FIX1-07 Treasury跨年度查询: 三期限观测日按年度分组,每年请求官方CSV,
  合并年度日期索引并逐年保留证据;某年失败不抹掉其他年已取得的数据。

数据纪律:
- 本脚本只接受**真实采集数据**(global/macro/china/rate_economy_*.json),
  SYNTHETIC fixture测试在tests/目录,二者严格分离;
- 外部源不可达/缺字段/日期缺失/结果过期→NOT_VERIFIED如实记录诊断,
  绝不以他源冒充、不编造数值、不以旧日期结果补足;
- 不写任何采集数据目录: 快照构建到临时目录,验收报告写--out-dir(默认output/acceptance);
  正式验收的--out-dir应在Git仓库之外(执行日志与来源证据不入库)。

独立来源(与采集通道不同源):
- 美债收益率: home.treasury.gov官方日频收益率曲线 (采集侧=FRED DGS系列)
- BTC: Coinbase Exchange官方candles(UTC日K) (采集侧=yfinance BTC-USD)
- 黄金: Coinbase PAXG(现货代币代理,仅参考对照) vs 采集侧COMEX期货
- 上证指数: hq.sinajs.cn实时/收盘快照 (采集侧=东财/腾讯通道)
- SPX/WTI: FRED SP500/DCOILWTICO (采集侧=yfinance ^GSPC/CL=F)

运行: python3 scripts/real_data_acceptance.py --data-dir <真实data/daily>
      [--trusted-root ROOT] [--out-dir DIR] [--data-day YYYYMMDD] [--skip-external]
"""
import argparse
import csv
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, date, time, timedelta, timezone

import requests

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fact_engine as fe          # noqa: E402  (仅单位类别常量/注册表,不复用其计算)
import snapshot_builder as sb     # noqa: E402

REPORT_SCHEMA = 'w5-real-acceptance/1.0'

# ── 容差与舍入(单一权威定义,随报告输出) ─────────────────────────────
TOLERANCES = {
    'treasury_ust': {
        'kind': 'bp', 'tol': 3.0,
        'rule': 'difference_bp = |our_yield_pct − external_yield_pct| × 100 ≤ 3.0 bp'
                '(收益率百分点差,绝非线性百分比)',
        'rounding': '差值换算bp后四舍五入至0.01bp再比较'},
    'coinbase_btc': {
        'kind': 'pct', 'tol': 0.5,
        'rule': '|our_close − ext_close| / ext_close × 100 ≤ 0.5%'
                '(两侧均为UTC日收盘,USD计价)',
        'rounding': '偏差四舍五入至0.01%再比较'},
    'paxg_gold': {
        'kind': 'reference_only',
        'rule': 'PAXG=现货代币(现货金价代理)≠COMEX期货连续合约: 工具身份不同,'
                '无基差/展期调整证据,不得按容差证明期货报价——NOT_COMPARABLE,'
                '参考偏差仅披露',
        'rounding': '参考偏差披露至0.01%,不参与判定'},
    'sina_shcomp': {
        'kind': 'pct', 'tol': 0.3,
        'rule': '仅当新浪快照日期==目标观测日且为收盘口径(非盘中实时价)时: '
                '|our_close − ext_close| / ext_close × 100 ≤ 0.3%',
        'rounding': '偏差四舍五入至0.01%再比较'},
    'fred_spx': {
        'kind': 'pct', 'tol': 0.5,
        'rule': 'FRED SP500必须存在与目标SPX**相同观测日**的记录: '
                '|our − ext| / ext × 100 ≤ 0.5%;日期不匹配=NOT_VERIFIED'
                '(不得以最近一条历史观测冒充同日值)',
        'rounding': '偏差四舍五入至0.01%再比较'},
    'fred_wti_spot': {
        'kind': 'reference_only',
        'rule': 'FRED DCOILWTICO=WTI现货价 ≠ WTI期货连续(采集口径): 无同合约/'
                '同结算时间/基差调整证据,不得以放宽价格容差代替金融身份验证'
                '——NOT_COMPARABLE,参考偏差仅披露',
        'rounding': '参考偏差披露至0.01%,不参与判定'},
}
RECOMPUTE_TOL_PP = 0.01   # 期间收益复算: 独立值与引擎值差≤0.01个百分点
RECOMPUTE_ROUNDING = '差值取绝对值不四舍五入直接与0.01pp比较(报告值保留4位)'
# FIX1-02: 价格字段校验容差(金融数值精度口径——相对0.01%,覆盖采集显示值
# 2位小数舍入;收益率百分点一致不能替代价格字段本身一致)
RECOMPUTE_PRICE_TOL_PCT = 0.01
# FIX1-06: 八项外部对照的稳定检查标识(不得重复/缺失)
CHECK_IDS = {
    'UST_2Y': 'EXT-UST-2Y', 'UST_10Y': 'EXT-UST-10Y', 'UST_30Y': 'EXT-UST-30Y',
    'BTC': 'EXT-BTC', 'GOLD_F': 'EXT-GOLD-F', 'SHCOMP': 'EXT-SHCOMP',
    'SPX': 'EXT-SPX', 'WTI_F': 'EXT-WTI-F',
}
# 复算对象单位纪律: 仅价格类可用 (期末/基准−1)×100 收益公式
PRICE_UNITS = {'index_point', 'usd', 'usd_per_oz', 'usd_per_barrel'}

# ══ F2-AC-02(IA-P0-2-W5-FIX2-AC-v1.0): EXT-BTC比较口径同源 ══════════════
# 比较日机械规则(固定,无人工挑选空间;随报告输出披露):
#   1. 比较日D = 快照BTC事实observation_date[:10](源=采集记录date字段→事实
#      观测日,机械透传;不接受任何人工指定/漂移的比较日);
#   2. 外部侧 = Coinbase同UTC日K(candles严格按D键取;D±1错日不进入比较,
#      缺D即NOT_VERIFIED;K线起点须UTC日界start_ts%86400==0);
#   3. 双侧完结性: ①D须在运行时刻(UTC)前已完整结束(now_utc ≥ D+1T00:00:00Z;
#      在途UTC日两侧都不存在"完结收盘"→NOT_COMPARABLE,不得以任何时点价
#      冒充完结vs完结);②我侧若携带采集收词元数据close_meta(W5-FIX2修复后
#      采集器随global_*.json持久化),须满足completed_through_utc==D(采集器
#      只产出已完结UTC日收盘;不一致→NOT_COMPARABLE);无close_meta(旧采集
#      产物)→如实披露,我侧完结性仅由①完结窗+0.5%容差比较约束(在途截断价
#      与外部完结收盘的真实差异会如实FAIL——R003实证1.34%)。
BTC_COMPARISON_DAY_RULE = (
    'EXT-BTC比较日D=快照BTC事实observation_date(机械透传,无人工挑选);'
    '外部=Coinbase同UTC日K(严格按D取,D±1错日即NOT_VERIFIED);'
    '双侧完结性: D须于运行时刻(UTC)前完整结束(否则NOT_COMPARABLE),'
    '我侧采集收词元数据close_meta.completed_through_utc须==D(否则NOT_COMPARABLE)')


def _now_utc(now=None):
    """运行时刻(UTC, aware);naive按UTC解释(测试注入确定性时点)。"""
    t = datetime.now(timezone.utc) if now is None else now
    if t.tzinfo is None:
        t = t.replace(tzinfo=timezone.utc)
    return t.astimezone(timezone.utc)


def btc_utc_day_completed(day_iso, now=None):
    """UTC日D在运行时刻前是否已完整结束: D+1T00:00:00Z ≤ now(UTC)。

    F2-AC-02: 在途UTC日不存在"完结收盘",完结vs完结比较不可满足——比较前
    机械判定,任何一侧的时点/截断价不得冒充该UTC日日收盘。
    实现为纯日期比较(D+1的ISO日期≤now(UTC)日期),不经datetime.combine/
    time——tests既有mock只替换datetime类,保持该路径可注入确定性时点。"""
    d = date.fromisoformat(str(day_iso)[:10])
    return (d + timedelta(days=1)) <= _now_utc(now).date()

# 指标身份与价格口径(注册表unit交叉核验后写入报告)
PRICE_BASIS = {
    'UST_2Y': '官方面值收益率(percent,2年期)', 'UST_10Y': '官方面值收益率(percent,10年期)',
    'UST_30Y': '官方面值收益率(percent,30年期)', 'BTC': 'BTC/USD现货价(Coinbase口径比对)',
    'GOLD_F': 'COMEX黄金期货连续(USD/oz)', 'SHCOMP': '上证综指收盘点位',
    'SPX': '标普500收盘点位', 'WTI_F': 'WTI原油期货连续(USD/桶)',
    'HSI': '恒生指数收盘点位',
}
RECOMPUTE_METRICS = ('SPX', 'GOLD_F', 'SHCOMP', 'HSI')

STATUSES = ('PASS', 'FAIL', 'NOT_VERIFIED', 'NOT_COMPARABLE',
            'INSUFFICIENT_HISTORY', 'SKIPPED')


def now_utc_iso():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def sha256_text(t):
    return hashlib.sha256(t.encode('utf-8', 'replace')).hexdigest()


# ── 密钥脱敏(FIX1-01: 统一脱敏函数+运行时已知密钥登记+写盘前最终清扫) ──
# 运行时已知密钥明文登记处(自动含URL编码形式;正式运行由main()登记FRED key;
# 测试只用**虚构**密钥验证机制,绝不用真实密钥做测试)
_KNOWN_SECRETS = []
# P0-4(2026-11-09): 与 scripts/redact_secrets.py 同一参数族与同一 [?&] 锚
# (api_key/apikey/token/key 查询参数形态;锚防 mid-word 误伤如 monkey=)——
# 纵深防御两层口径保持一致,不各自漂移
_UNREDACTED_KEY_PAT = re.compile(
    r"(?i)([?&](?:api_key|apikey|token|key)=)(?!\*\*\*REDACTED\*\*\*)[^&\s'\"]+")


def _register_secret(s):
    """登记运行时已知密钥明文(自动补percent-quote/plus编码形式)。"""
    if not s or not isinstance(s, str):
        return
    import urllib.parse as _up
    for cand in {s, _up.quote(s, safe=''), _up.quote_plus(s)}:
        if cand and cand not in _KNOWN_SECRETS:
            _KNOWN_SECRETS.append(cand)


def sanitize_text(s):
    """统一脱敏: api_key=…查询参数模式 + 已登记密钥明文(含URL编码形式)。
    幂等: 已脱敏文本再过一遍不变;非字符串原样返回。"""
    if not isinstance(s, str):
        return s
    out = _UNREDACTED_KEY_PAT.sub(r'\1***REDACTED***', s)
    for k in _KNOWN_SECRETS:
        if k in out:
            out = out.replace(k, '***REDACTED***')
    return out


def redact_url(u):
    """兼容入口: URL脱敏统一走sanitize_text(同一规则,含已知密钥明文)。"""
    return sanitize_text(u)


def _clip_safe(s, clip=200):
    """截断(仅在**全量脱敏后**调用);截断边界不得截出已知密钥片段——
    尾部若与任一已登记密钥的前缀重叠,回退截断点避开。"""
    if len(s) <= clip:
        return s
    cut = s[:clip]
    for k in _KNOWN_SECRETS:
        for _L in range(min(len(k) - 1, len(cut)), 1, -1):
            if cut.endswith(k[:_L]):
                cut = cut[:len(cut) - _L]
                break
    return cut


def _safe_error(err, clip=200):
    """异常→结构化证据安全文本(FIX1-01): 保留异常类型与HTTP状态码等必要
    诊断;先全量脱敏→再截断→截断后复核,仍残留密钥则整条降级为类型+状态。"""
    if err is None:
        return None
    status = getattr(getattr(err, 'response', None), 'status_code', None)
    head = f"{type(err).__name__}(HTTP {status})" if status is not None \
        else type(err).__name__
    safe = sanitize_text(_clip_safe(sanitize_text(f"{head}: {err}"), clip))
    if find_secret(safe) is not None:
        return f"{head}: (消息含敏感内容,已整体脱敏)"
    return safe


def find_secret(text):
    """最终密钥检查: 返回文本中残留的未脱敏密钥线索(None=干净)。
    匹配api_key=未脱敏模式或任一已登记密钥明文(含编码形式)。"""
    if not isinstance(text, str):
        return None
    m = _UNREDACTED_KEY_PAT.search(text)
    if m:
        return m.group(0)
    for k in _KNOWN_SECRETS:
        if k and k in text:
            return k
    return None


def sweep_secrets(obj):
    """递归净化dict/list/str(写JSON/MD/LOG/ZIP前纵深防御,幂等)。"""
    if isinstance(obj, str):
        return sanitize_text(obj)
    if isinstance(obj, list):
        return [sweep_secrets(v) for v in obj]
    if isinstance(obj, dict):
        return {k: sweep_secrets(v) for k, v in obj.items()}
    return obj


def _num(x):
    """严格数值(拒绝bool/None/字符串数字)。"""
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        return None
    return float(x)


# ══ 独立来源获取(结构化证据;任一失败→空数据+错误诊断,如实降级) ════════
def _evidence(source, url, resp=None, err=None):
    ev = {'source': source, 'url': redact_url(url), 'fetched_at_utc': now_utc_iso()}
    if resp is not None:
        body = getattr(resp, 'text', '') or ''
        ev['http_status'] = getattr(resp, 'status_code', None)
        ev['body_sha256'] = sha256_text(body)
        ev['body_bytes'] = len(body.encode('utf-8', 'replace'))
    if err is not None:
        ev['error'] = _safe_error(err)   # FIX1-01: 先全量脱敏再截断,保类型/HTTP状态
    return ev


def fetch_treasury_ust(year, want_dates):
    """官方CSV → ({iso: row}, evidence, raw_body)。失败→({}, ev, None)。"""
    url = (f"https://home.treasury.gov/resource-center/data-chart-center/interest-rates/"
           f"daily-treasury-rates.csv/{year}/all?type=daily_treasury_yield_curve"
           f"&field_tdr_date_value={year}&page&_format=csv")
    try:
        r = requests.get(url, timeout=25)
        r.raise_for_status()
        out = {}
        for row in csv.DictReader(io.StringIO(r.text)):
            m = re.match(r'(\d{2})/(\d{2})/(\d{4})', row.get('Date', ''))
            if not m:
                continue
            iso = f"{m.group(3)}-{m.group(1)}-{m.group(2)}"
            if iso in want_dates:
                out[iso] = row
        return out, _evidence('home.treasury.gov官方收益率曲线', url, r), r.text
    except Exception as e:
        return {}, _evidence('home.treasury.gov官方收益率曲线', url, err=e), None


def fetch_coinbase_candles(product, start_iso, end_iso):
    """Coinbase日K → ({iso: {'close','start_ts'}}, ev, raw)。granularity=86400。"""
    url = f'https://api.exchange.coinbase.com/products/{product}/candles'
    try:
        r = requests.get(url, params={'granularity': 86400,
                                      'start': f"{start_iso}T00:00:00Z",
                                      'end': f"{end_iso}T00:00:00Z"}, timeout=20)
        r.raise_for_status()
        out = {}
        for c in r.json():          # [time, low, high, open, close, volume]
            iso = datetime.fromtimestamp(c[0], timezone.utc).date().isoformat()
            out[iso] = {'close': float(c[4]), 'start_ts': int(c[0])}
        return out, _evidence(f'Coinbase Exchange {product} candles(UTC日K,granularity=86400)',
                              r.url, r), r.text
    except Exception as e:
        return {}, _evidence(f'Coinbase Exchange {product} candles', url, err=e), None


def fetch_sina_index(code):
    """新浪指数快照 → ({'close','date','time'}或None, ev, raw)。"""
    url = f'https://hq.sinajs.cn/list={code}'
    try:
        r = requests.get(url, headers={'Referer': 'https://finance.sina.com.cn'}, timeout=15)
        r.encoding = 'gbk'
        ev = _evidence(f'hq.sinajs.cn {code}(实时/收盘快照,GBK)', r.url, r)
        m = re.search(r'"([^"]+)"', r.text)
        if not m:
            return None, dict(ev, error='响应不含引号数据段'), r.text
        parts = m.group(1).split(',')
        if len(parts) < 4:
            return None, dict(ev, error='字段数不足'), r.text
        return {'close': float(parts[3]),
                'date': parts[30] if len(parts) > 30 else None,
                'time': parts[31] if len(parts) > 31 else None}, ev, r.text
    except Exception as e:
        return None, _evidence(f'hq.sinajs.cn {code}', url, err=e), None


def fetch_fred_obs(series_id, api_key, limit=10):
    """FRED序列最近观测(降序) → ([(iso,value)], ev, raw)。失败→([], ev, None)。"""
    url = 'https://api.stlouisfed.org/fred/series/observations'
    try:
        r = requests.get(url, params={'series_id': series_id, 'api_key': api_key,
                                      'file_type': 'json', 'sort_order': 'desc',
                                      'limit': limit}, timeout=20)
        r.raise_for_status()
        obs = [(o['date'], float(o['value'])) for o in r.json().get('observations', [])
               if o.get('value', '.') not in ('.', None)]
        return obs, _evidence(f'FRED {series_id}', r.url, r), r.text   # r.url→ev内脱敏
    except Exception as e:
        return [], _evidence(f'FRED {series_id}', url, err=e), None


def default_fetchers(fred_api_key):
    """正式外部获取器集合(测试注入替代集合,不触网)。"""
    return {
        'treasury': fetch_treasury_ust,
        'coinbase': fetch_coinbase_candles,
        'sina': fetch_sina_index,
        'fred': (lambda sid: fetch_fred_obs(sid, fred_api_key)) if fred_api_key else None,
    }


# ══ 八项外部对照(纯函数,逐项独立结构化) ═══════════════════════════
def _mk(check, mid, ours, ext, comp, verdict, note):
    return {'check': check, 'metric_id': mid, 'category': 'external',
            'ours': ours, 'external': ext, 'comparison': comp,
            'verdict': verdict, 'note': note}


def _ours(fact):
    if not fact:
        return None
    # FIX1-06: 保留fact已有source(collector/file/检索时间)——不得只输出
    # value/date/unit而丢弃来源身份
    return {'value': _num(fact.get('value')),
            'observation_date': str(fact.get('observation_date') or '')[:10] or None,
            'unit': fact.get('unit'),
            'price_basis': PRICE_BASIS.get(fact.get('metric_id')),
            'source': fact.get('source') or None}


def check_ust(mid, fact, rows, col, spec):
    """UST: 日期逐指标匹配+期限列各归各+百分点差bp。rows={iso:row}。"""
    o = _ours(fact)
    if o is None or o['value'] is None:
        return _mk(f'{mid}外部核验', mid, o, None, None, 'SKIPPED', '快照无该事实')
    od = o['observation_date']
    if not rows:
        return _mk(f'{mid}外部核验', mid, o, None, None, 'NOT_VERIFIED',
                   '官方曲线不可达/无数据(诊断见外部证据)——不编造')
    row = rows.get(od)
    if not row or not row.get(col):
        return _mk(f'{mid}外部核验', mid, o, None, None, 'NOT_VERIFIED',
                   f'官方CSV无{mid}观测日{od}记录({col}列)——日期不匹配不得以'
                   '相邻日期冒充(发布节奏/期限各自观测日独立)')
    ext = float(row[col])
    diff_bp = round(abs(o['value'] - ext) * 100, 2)
    verdict = 'PASS' if diff_bp <= spec['tol'] else 'FAIL'
    return _mk(f'{mid}外部核验', mid, o,
               {'value': ext, 'observation_date': od},
               {'metric': 'difference_bp', 'ours_value': o['value'], 'external_value': ext,
                'difference_bp': diff_bp, 'tolerance_bp': spec['tol'],
                'tolerance_rule': spec['rule'], 'rounding': spec['rounding']},
               verdict,
               f'{col}期限列,{od}同日;差{diff_bp}bp'
               + ('(≤3bp)' if verdict == 'PASS' else '(>3bp,真实差异)'))


def check_spx(fact, fred_obs, spec):
    """FRED SP500: 必须同观测日;取最近一条=错日→NOT_VERIFIED。"""
    mid = 'SPX'
    o = _ours(fact)
    if o is None or o['value'] is None:
        return _mk(f'{mid}外部核验', mid, o, None, None, 'SKIPPED', '快照无该事实')
    if not fred_obs:
        return _mk(f'{mid}外部核验', mid, o, None, None, 'NOT_VERIFIED',
                   'FRED SP500不可达/无观测(诊断见外部证据)')
    od = o['observation_date']
    exact = next(((d, v) for d, v in fred_obs if d == od), None)
    if exact is None:
        avail = ', '.join(d for d, _ in fred_obs[:5])
        return _mk(f'{mid}外部核验', mid, o,
                   {'available_dates': [d for d, _ in fred_obs]},
                   None, 'NOT_VERIFIED',
                   f'FRED无{od}同日观测(最近可得: {avail})——日期不匹配不得判PASS,'
                   '不得用最近一条历史值与目标值比较')
    d, ext = exact
    dev = round(abs(o['value'] - ext) / ext * 100, 2)
    verdict = 'PASS' if dev <= spec['tol'] else 'FAIL'
    return _mk(f'{mid}外部核验', mid, o, {'value': ext, 'observation_date': d},
               {'metric': 'relative_pct', 'ours_value': o['value'], 'external_value': ext,
                'difference_pct': dev, 'tolerance_pct': spec['tol'],
                'tolerance_rule': spec['rule'], 'rounding': spec['rounding']},
               verdict, f'{d}同日比对;偏差{dev}%')


def _not_comparable(mid, fact, ext_data, ext_val, note, spec):
    o = _ours(fact)
    if o is None or o['value'] is None:
        return _mk(f'{mid}外部核验', mid, o, None, None, 'SKIPPED', '快照无该事实')
    if ext_val is None:
        return _mk(f'{mid}外部核验', mid, o, None, None, 'NOT_VERIFIED',
                   f'参考源不可达/无该日数据(诊断见外部证据)——参考对照无法执行')
    dev = round(abs(o['value'] - ext_val) / ext_val * 100, 2) if ext_val else None
    return _mk(f'{mid}外部核验', mid, o,
               dict(ext_data, value=ext_val),
               {'metric': 'reference_deviation_pct(不参与判定)', 'ours_value': o['value'],
                'reference_value': ext_val, 'reference_deviation_pct': dev,
                'tolerance_rule': spec['rule'], 'rounding': spec['rounding']},
               'NOT_COMPARABLE', note)


def check_gold_f(fact, paxg_map, spec):
    """PAXG现货代理≠GOLD_F期货: 恒NOT_COMPARABLE(参考偏差披露)。"""
    mid = 'GOLD_F'
    o = _ours(fact) or {}
    od = o.get('observation_date')
    c = paxg_map.get(od) if od else None
    return _not_comparable(
        mid, fact, {'source_quote': 'PAXG-USD(现货代币)',
                    'observation_date': od if c else None},
        c['close'] if c else None,
        'PAXG为黄金现货价格代理(代币),GOLD_F为COMEX期货连续合约——工具身份与'
        '价格口径不同,无基差/展期调整证据,不得按容差直接证明期货报价;'
        '参考偏差仅披露(现货代理保留为参考源)', spec)


def check_wti_f(fact, fred_obs, spec):
    """FRED现货≠WTI_F期货: 恒NOT_COMPARABLE(参考偏差披露)。"""
    mid = 'WTI_F'
    o = _ours(fact) or {}
    od = o.get('observation_date')
    exact = next(((d, v) for d, v in fred_obs if d == od), None) if od else None
    return _not_comparable(
        mid, fact, {'source_quote': 'FRED DCOILWTICO(WTI现货)',
                    'observation_date': exact[0] if exact else None},
        exact[1] if exact else None,
        'FRED DCOILWTICO为WTI现货价格序列,WTI_F为期货连续合约——期现口径不同,'
        '无同合约/同结算时间/基差调整证据,不得放宽价格容差代替金融身份验证;'
        '参考偏差仅披露', spec)


def check_shcomp(fact, quote, today_ymd, spec):
    """新浪: 同日+收盘口径才比较;实时/错日→NOT_VERIFIED。"""
    mid = 'SHCOMP'
    o = _ours(fact)
    if o is None or o['value'] is None:
        return _mk(f'{mid}外部核验', mid, o, None, None, 'SKIPPED', '快照无该事实')
    if quote is None:
        return _mk(f'{mid}外部核验', mid, o, None, None, 'NOT_VERIFIED',
                   '新浪通道不可达/响应异常(诊断见外部证据)')
    od = o['observation_date']
    qd, qt = quote.get('date'), quote.get('time')
    if qd != od:
        return _mk(f'{mid}外部核验', mid, o,
                   {'value': quote['close'], 'observation_date': qd, 'quote_time': qt},
                   None, 'NOT_VERIFIED',
                   f'新浪快照日期{qd}≠目标观测日{od}——实时快照无法证明历史日期收盘,'
                   '日期不匹配不得判PASS')
    # FIX1-04: 收盘口径可证性对**任意报价日期**一律要求——取消"仅执行当日
    # 才检查时间"的历史日期豁免。新浪为实时快照接口: 无时间字段或时间
    # <15:30:00(北京时间收盘后)都无法证明该价格为收盘口径,当日与历史日期
    # 一律NOT_VERIFIED(历史报价比较能力保留: 日期匹配且收盘口径可证时
    # 正常进入价格比较;today_ymd参数保留仅为签名兼容,判定不依赖执行日)
    if not qt or qt < '15:30:00':
        return _mk(f'{mid}外部核验', mid, o,
                   {'value': quote['close'], 'observation_date': qd, 'quote_time': qt},
                   None, 'NOT_VERIFIED',
                   f'快照时间{qt or "无时间字段"}未证实收盘口径(收盘须≥15:30:00'
                   '北京时间)——实时/盘中价或无时间戳不能证明收盘价,'
                   '任意报价日期均不得判PASS')
    ext = quote['close']
    dev = round(abs(o['value'] - ext) / ext * 100, 2)
    verdict = 'PASS' if dev <= spec['tol'] else 'FAIL'
    return _mk(f'{mid}外部核验', mid, o,
               {'value': ext, 'observation_date': qd, 'quote_time': qt},
               {'metric': 'relative_pct', 'ours_value': o['value'], 'external_value': ext,
                'difference_pct': dev, 'tolerance_pct': spec['tol'],
                'tolerance_rule': spec['rule'], 'rounding': spec['rounding']},
               verdict, f'{qd}同日收盘口径(报价时间{qt});偏差{dev}%')


def check_btc(fact, candles, spec, now_utc=None, close_meta=None):
    """BTC: Coinbase UTC日K(起点=00:00Z)+USD计价同日比对。

    F2-AC-02(IA-P0-2-W5-FIX2-AC-v1.0): 完结收盘vs完结收盘——比较日D=快照
    BTC事实observation_date(机械透传,无人工挑选);双侧须同为已完结UTC日:
    ①D在运行时刻(UTC)前已完整结束(btc_utc_day_completed;在途UTC日双侧都
    不存在完结收盘→NOT_COMPARABLE,任何时点/截断价不得冒充);②采集元数据
    close_meta(W5-FIX2采集器随global_*.json持久化)的completed_through_utc
    须==D(不一致→NOT_COMPARABLE);无close_meta(旧采集产物)→如实披露,
    不阻断(此时我侧完结性仅由①约束,在途截断价与外部完结收盘的真实差异
    会如实FAIL——R003实证1.34%)。Coinbase侧严格按D取K线,D±1错日不进入
    比较(缺D即NOT_VERIFIED)。容差0.5%不变。"""
    mid = 'BTC'
    o = _ours(fact)
    if o is None or o['value'] is None:
        return _mk(f'{mid}外部核验', mid, o, None, None, 'SKIPPED', '快照无该事实')
    if o['unit'] != 'usd':
        return _mk(f'{mid}外部核验', mid, o, None, None, 'NOT_VERIFIED',
                   f"快照单位{o['unit']}≠usd——非USD计价不可比")
    if not candles:
        return _mk(f'{mid}外部核验', mid, o, None, None, 'NOT_VERIFIED',
                   'Coinbase日K不可达/无数据(诊断见外部证据)')
    od = o['observation_date']
    if not btc_utc_day_completed(od, now_utc):
        return _mk(f'{mid}外部核验', mid, o,
                   {'observation_date': od, 'in_flight_utc_day': True},
                   None, 'NOT_COMPARABLE',
                   f'{od}为运行时刻({_now_utc(now_utc).isoformat(timespec="seconds")})'
                   '前未完整结束的UTC日——双侧均不存在该日完结收盘,在途时点价'
                   '不得冒充完结vs完结(R003实证: 在途23:00Z截断价vs完整UTC日收'
                   '盘差1.34%)')
    if close_meta is not None and close_meta.get('completed_through_utc') != od:
        return _mk(f'{mid}外部核验', mid, o,
                   {'observation_date': od,
                    'collector_completed_through_utc':
                        close_meta.get('completed_through_utc')},
                   None, 'NOT_COMPARABLE',
                   f"采集close_meta.completed_through_utc="
                   f"{close_meta.get('completed_through_utc')}≠比较日{od}"
                   '——采集侧完结口径与快照事实观测日不一致,不可比')
    c = candles.get(od)
    if c is None:
        return _mk(f'{mid}外部核验', mid, o,
                   {'available_dates': sorted(candles)[:5]},
                   None, 'NOT_VERIFIED',
                   f'Coinbase无{od} UTC日K——字符串日期相同不跳过日界判断,'
                   '缺该UTC日K线即不可比')
    if c['start_ts'] % 86400 != 0:
        return _mk(f'{mid}外部核验', mid, o, {'value': c['close']},
                   None, 'NOT_VERIFIED',
                   f"K线起点ts={c['start_ts']}非UTC日界00:00Z——日K口径不可证")
    ext = c['close']
    dev = round(abs(o['value'] - ext) / ext * 100, 2)
    verdict = 'PASS' if dev <= spec['tol'] else 'FAIL'
    meta_note = (f";采集close_meta: completed_through="
                 f"{close_meta.get('completed_through_utc')},retrieved_at="
                 f"{close_meta.get('retrieved_at_utc')},source="
                 f"{close_meta.get('source')}"
                 if close_meta is not None else
                 ';采集产物无close_meta(旧采集器产物)——我侧完结性未经采集'
                 '元数据独立证明,如实披露')
    return _mk(f'{mid}外部核验', mid, o,
               {'value': ext, 'observation_date': od, 'utc_window':
                f"{od}T00:00:00Z–{od}T23:59:59Z(Coinbase Exchange,USD)"},
               {'metric': 'relative_pct', 'ours_value': o['value'], 'external_value': ext,
                'difference_pct': dev, 'tolerance_pct': spec['tol'],
                'tolerance_rule': spec['rule'], 'rounding': spec['rounding']},
               verdict, f'{od}完结UTC日收盘vs同日完结UTC日K(Coinbase Exchange现货,'
               f'USD);偏差{dev}%{meta_note}')


def run_external_checks(facts, fetchers, today_ymd, log=None, btc_close_meta=None):
    """执行八项外部对照。fetchers={'treasury','coinbase','sina','fred'(可None)}。
    返回(results, evidences, raw_bodies)。外部获取失败→NOT_VERIFIED+诊断,
    不冒充、不编造。

    F2-AC-02: btc_close_meta=采集器随global_*.json持久化的BTC收盘元数据
    (main()从数据日global文件读取;旧产物无close_meta→None,如实披露),
    透传check_btc作我侧完结性核验(completed_through_utc==比较日)。
    FIX1-06: 每检查稳定check_id+来源绑定(external_source/source_identity/
    evidence_ids): 三UST共享年度官方CSV证据;FRED SPX/WTI各自证据;
    Coinbase BTC/PAXG按真实请求各自记录;无来源明确为空([]/None),不构造
    虚假ID;所有引用的evidence_id均可在external_evidence中定位。
    FIX1-07: UST三期限观测日按**年度分组逐年请求**官方CSV并合并日期索引,
    逐年保留证据;某年失败不抹掉其他年已取得的数据。"""
    def P(msg):
        if log is not None:
            log.append(msg)
        print(msg)

    def fv(mid):
        return facts.get(mid)

    results, evidences, raws = [], [], []

    def rec(ev, raw, name, ev_id, identity=None):
        """证据登记: 赋稳定evidence_id(无证据=fetcher未执行→不登记不造ID)。"""
        if ev:
            ev = dict(ev, evidence_id=ev_id)
            if identity:
                ev['source_identity'] = identity
            evidences.append(ev)
        if raw is not None:
            raws.append((name, raw))
        return ev_id if ev else None

    def bind(result, mid, ext_source, identity, ev_ids):
        """检查行来源绑定: check_id+external_source/source_identity/evidence_ids
        (external为dict时同步镜像,外部结构化字段完整)。"""
        ids = [i for i in ev_ids if i]
        result['check_id'] = CHECK_IDS[mid]
        result['external_source'] = ext_source
        result['source_identity'] = identity
        result['evidence_ids'] = ids
        if isinstance(result.get('external'), dict):
            result['external'].setdefault('external_source', ext_source)
            result['external'].setdefault('source_identity', identity)
            result['external']['evidence_ids'] = ids
        return result

    # A1 UST 2Y/10Y/30Y(FIX1-07: 按年度分组逐年请求+合并;FIX1-06: 共享年度证据)
    ust_ids = ('UST_2Y', 'UST_10Y', 'UST_30Y')
    cols = {'UST_2Y': '2 Yr', 'UST_10Y': '10 Yr', 'UST_30Y': '30 Yr'}
    ust_src = 'home.treasury.gov官方收益率曲线'
    want = {_ours(fv(m))['observation_date'] for m in ust_ids
            if _ours(fv(m)) and _ours(fv(m))['observation_date']}
    years = sorted({d[:4] for d in want}) or [str(date.today().year)]
    P(f"  [A1] Treasury.gov官方曲线 {sorted(want)} → 年度{years}(逐年请求,合并索引)")
    rows, tsy_ids = {}, []
    for year in years:
        yr_want = {d for d in want if d[:4] == year}
        r_, ev, raw = fetchers['treasury'](int(year), yr_want)
        tsy_ids.append(rec(ev, raw, f'treasury_{year}', f'EV-TSY-{year}',
                           f'daily_treasury_yield_curve/{year}.csv'))
        rows.update(r_ or {})   # 某年失败→该年无行,其他年已合并数据不受影响
    tsy_identity = ','.join(f'daily_treasury_yield_curve/{y}.csv' for y in years)
    for mid in ust_ids:
        results.append(bind(check_ust(mid, fv(mid), rows, cols[mid],
                                      TOLERANCES['treasury_ust']),
                            mid, ust_src, tsy_identity, tsy_ids))

    # A2 BTC: Coinbase UTC日K(F2-AC-02: 完结vs完结+close_meta透传)
    o = _ours(fv('BTC')) or {}
    od = o.get('observation_date')
    P(f"  [A2] Coinbase BTC-USD日K (目标{od})")
    _ct = (btc_close_meta or {}).get('completed_through_utc')
    P(f"  [A2-meta] 比较日规则: {BTC_COMPARISON_DAY_RULE}")
    P(f"  [A2-meta] 我侧采集close_meta: completed_through="
      f"{_ct if _ct else '(无close_meta——旧采集器产物,如实披露)'}")
    if od:
        end = (date.fromisoformat(od) + timedelta(days=1)).isoformat()
        candles, ev, raw = fetchers['coinbase']('BTC-USD', od, end)
    else:
        candles, ev, raw = {}, None, None
    btc_id = rec(ev, raw, 'coinbase_BTC-USD', 'EV-CB-BTC-USD',
                 'products/BTC-USD/candles?granularity=86400')
    results.append(bind(check_btc(fv('BTC'), candles, TOLERANCES['coinbase_btc'],
                                  close_meta=btc_close_meta),
                        'BTC', 'Coinbase Exchange BTC-USD(UTC日K)',
                        'products/BTC-USD/candles?granularity=86400', [btc_id]))

    # A3 GOLD_F vs PAXG(参考源,恒NOT_COMPARABLE)
    o = _ours(fv('GOLD_F')) or {}
    od = o.get('observation_date')
    P(f"  [A3] Coinbase PAXG-USD(现货代理,参考) (目标{od})")
    if od:
        end = (date.fromisoformat(od) + timedelta(days=1)).isoformat()
        paxg, ev, raw = fetchers['coinbase']('PAXG-USD', od, end)
    else:
        paxg, ev, raw = {}, None, None
    paxg_id = rec(ev, raw, 'coinbase_PAXG-USD', 'EV-CB-PAXG-USD',
                  'products/PAXG-USD/candles?granularity=86400')
    results.append(bind(check_gold_f(fv('GOLD_F'), paxg, TOLERANCES['paxg_gold']),
                        'GOLD_F', 'Coinbase Exchange PAXG-USD(现货代理,参考)',
                        'products/PAXG-USD/candles?granularity=86400', [paxg_id]))

    # A4 SHCOMP: 新浪实时/收盘快照
    P("  [A4] hq.sinajs.cn sh000001")
    quote, ev, raw = fetchers['sina']('sh000001')
    sina_id = rec(ev, raw, 'sina_sh000001', 'EV-SINA-SH000001',
                  'hq.sinajs.cn/list=sh000001(实时/收盘快照)')
    results.append(bind(check_shcomp(fv('SHCOMP'), quote, today_ymd,
                                     TOLERANCES['sina_shcomp']),
                        'SHCOMP', 'hq.sinajs.cn sh000001(实时/收盘快照)',
                        'hq.sinajs.cn/list=sh000001', [sina_id]))

    # A5/A6 FRED SP500/DCOILWTICO
    if fetchers.get('fred') is None:
        P("  [A5/A6] FRED: 无API密钥——SPX/WTI_F外部核验NOT_VERIFIED(密钥不写入证据)")
        results.append(bind(_mk('SPX外部核验', 'SPX', _ours(fv('SPX')), None, None,
                                'NOT_VERIFIED', '无FRED API密钥——外部核验未执行,不得计PASS'),
                            'SPX', None, None, []))       # 无来源明确为空,不造ID
        results.append(bind(_mk('WTI_F外部核验', 'WTI_F', _ours(fv('WTI_F')), None, None,
                                'NOT_VERIFIED', '无FRED API密钥——外部核验未执行,不得计PASS'),
                            'WTI_F', None, None, []))
    else:
        P("  [A5] FRED SP500(同观测日检索)")
        obs, ev, raw = fetchers['fred']('SP500')
        spx_id = rec(ev, raw, 'fred_SP500', 'EV-FRED-SP500', 'FRED SP500序列观测')
        results.append(bind(check_spx(fv('SPX'), obs, TOLERANCES['fred_spx']),
                            'SPX', 'FRED SP500', 'FRED SP500序列观测', [spx_id]))
        P("  [A6] FRED DCOILWTICO(现货参考,恒NOT_COMPARABLE)")
        obs, ev, raw = fetchers['fred']('DCOILWTICO')
        wti_id = rec(ev, raw, 'fred_DCOILWTICO', 'EV-FRED-DCOILWTICO',
                     'FRED DCOILWTICO序列观测')
        results.append(bind(check_wti_f(fv('WTI_F'), obs, TOLERANCES['fred_wti_spot']),
                            'WTI_F', 'FRED DCOILWTICO(现货)',
                            'FRED DCOILWTICO序列观测', [wti_id]))
    return results, evidences, raws


# ══ 独立复算(与fact_engine独立实现;仅标准库,不调用引擎计算) ════════
def independent_period_returns(dates, values, obs_date):
    """独立复算周/MTD/YTD(基准=期前最后收盘)。W5-03强化版。

    输入校验(fail-loud): dates/values须等长序列;日期须为真实ISO日历日
    (YYYY-MM-DD);数值须为数值(拒bool);重复日期→ValueError(乱序可接受,
    排序后计算——与引擎sorted口径一致)。
    返回: {'obs','close','week','mtd','ytd'};每期为
    {'basis_date','basis_value','pct_change'}或None(基准数据不足);
    无≤obs观测→{'obs':None,'reason':...}。公式=(期末/基准−1)×100(仅价格类)。"""
    try:
        n = len(dates)
    except TypeError:
        raise ValueError(f'dates非序列:{type(dates).__name__}')
    if len(values) != n:
        raise ValueError(f'dates/values长度不等({n} vs {len(values)})')
    parsed = []
    for d, v in zip(dates, values):
        if not isinstance(d, str):
            raise ValueError(f'日期非字符串:{d!r}')
        try:
            dd = date.fromisoformat(d)
        except ValueError:
            raise ValueError(f'日期非真实ISO日历日:{d!r}')
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise ValueError(f'数值非法:{v!r}(@{d})')
        parsed.append((dd.isoformat(), float(v)))
    seen = {}
    for d, _ in parsed:
        if d in seen:
            raise ValueError(f'重复日期:{d}(序列身份不明,拒绝复算)')
        seen[d] = 1
    obs = str(obs_date)[:10]
    try:
        date.fromisoformat(obs)
    except ValueError:
        raise ValueError(f'obs_date非ISO日期:{obs!r}')
    pairs = sorted(parsed)
    prior = [(d, v) for d, v in pairs if d <= obs]
    if not prior:
        return {'obs': None, 'reason': f'序列无≤{obs}的观测'}
    cur_d, cur = prior[-1]

    def last_before(cutoff, strict):
        cands = [(d, v) for d, v in prior if (d < cutoff if strict else d <= cutoff)]
        return cands[-1] if cands else None

    # ISO周一起始日(独立推算,跨年正确): 1月4日所在周的周一 + (w−jw)周
    y, w, _ = date.fromisoformat(cur_d).isocalendar()
    jan4 = date(y, 1, 4)
    jy, jw, _ = jan4.isocalendar()
    week_monday = jan4 + timedelta(weeks=w - jw, days=-jan4.weekday())

    out = {'obs': cur_d, 'close': cur}
    for key, cutoff in (('week', week_monday.isoformat()),
                        ('mtd', f"{cur_d[:7]}-01"),
                        ('ytd', f"{cur_d[:4]}-01-01")):
        b = last_before(cutoff, strict=True)
        out[key] = ({'basis_date': b[0], 'basis_value': b[1],
                     'pct_change': round((cur / b[1] - 1) * 100, 4)}
                    if b and b[1] else None)
    return out


def _price_mismatch_pct(a, b):
    """两价格相对差%(任一非严格数值→None)。FIX1-02金融数值精度口径:
    相对容差RECOMPUTE_PRICE_TOL_PCT(0.01%),覆盖采集显示值2位小数舍入,
    但绝不容忍基准/期末价格字段的真实不一致。"""
    a, b = _num(a), _num(b)
    if a is None or b is None:
        return None
    return abs(a - b) / max(abs(b), 1e-12) * 100


def recompute_check(mid, fact, series, tol_pp=RECOMPUTE_TOL_PP):
    """单指标周/MTD/YTD独立复算对照(逐期: 期末/独立基准/引擎基准/公式/两值/差异/判定)。

    FIX1-02: 价格字段本身逐期核对——期末价格(事实value vs 独立复算close)
    与基准价格(引擎basis_value vs 独立basis_value);独立有基准时引擎**必须**
    提供basis_date与basis_value(缺失即FAIL,不得跳过);收益率百分点一致
    不得替代价格字段一致。
    FIX1-03: WEEK/MTD/YTD三期全部独立一致才算完整复算PASS
    (complete_recompute=True);部分成功→INSUFFICIENT_HISTORY+部分复核
    明细(verified_periods),不冒充完整PASS;任一期确定性错误→FAIL。"""
    check_name = f'{mid}周/MTD/YTD独立复算'
    if not fact or not isinstance(series, dict) \
            or 'dates' not in series or 'values' not in series:
        return {'check': check_name, 'metric_id': mid, 'category': 'recompute',
                'ours': None, 'verdict': 'SKIPPED', 'periods': {},
                'complete_recompute': False, 'verified_periods': [],
                'insufficient_periods': [], 'note': '快照无该事实/序列'}
    unit = fact.get('unit')
    base = {'check': check_name, 'metric_id': mid, 'category': 'recompute',
            'unit': unit, 'formula': '(期末值/基准值−1)×100(价格收益,期前收盘基准)',
            'tolerance_pp': tol_pp, 'price_tolerance_pct': RECOMPUTE_PRICE_TOL_PCT,
            'rounding': RECOMPUTE_ROUNDING}
    if unit not in PRICE_UNITS:
        return dict(base, ours=_ours(fact), verdict='FAIL', periods={},
                    complete_recompute=False, verified_periods=[],
                    insufficient_periods=[],
                    note=f'单位{unit}非价格类——利率/点差/计数类不得机械套用'
                         '价格百分比公式(单位纪律),拒绝复算')
    try:
        ind = independent_period_returns(series['dates'], series['values'],
                                         fact.get('observation_date'))
    except ValueError as e:
        return dict(base, ours=_ours(fact), verdict='FAIL', periods={},
                    complete_recompute=False, verified_periods=[],
                    insufficient_periods=[],
                    note=f'序列异常拒绝复算:{e}')
    eng = fact.get('derived') or {}
    eng_end = eng.get('end') or {}
    obs = fact.get('observation_date')
    close = _num(fact.get('value'))
    problems, periods = [], {}
    pkey = {'week': ('week', 'week'), 'mtd': ('mtd', 'mtd'), 'ytd': ('ytd', 'ytd')}

    # 期末语义: 事实观测日 == 独立期末 == 引擎期末(引擎提供end时才核对;
    # china通道事实不填end为既有数据契约,不因FIX1扩为强制)
    if ind.get('obs') != str(obs)[:10]:
        problems.append(f"期末不一致: 独立{ind.get('obs')} vs 事实{obs}")
    if eng_end.get('date') and str(eng_end['date'])[:10] != str(obs)[:10]:
        problems.append(f"期末不一致: 引擎{eng_end.get('date')} vs 事实{obs}")
    # FIX1-02A: 结束价格校验——事实value须与独立复算期末close一致
    # (收益率正确不能掩盖期末价格字段错误,如独立110而事实111)
    _end_dev = _price_mismatch_pct(close, ind.get('close'))
    if _end_dev is not None and _end_dev > RECOMPUTE_PRICE_TOL_PCT:
        problems.append(f"期末价格不一致: 事实{close} vs 独立复算{ind.get('close')}"
                        f"(相对差{round(_end_dev, 4)}%"
                        f">{RECOMPUTE_PRICE_TOL_PCT}%)")

    for period, (ik, ek) in pkey.items():
        iv = ind.get(ik) or {}
        er = eng.get(ek) or {}
        eng_avail = er.get('available') is not False and er.get('pct_change') is not None
        ind_pct = iv.get('pct_change')
        row = {'independent': iv if iv else None,
               'engine': ({'available': er.get('available', eng_avail),
                           'reason': er.get('reason'),
                           'basis_date': er.get('basis_date'),
                           'basis_value': er.get('basis_value'),
                           'pct_change': er.get('pct_change')} if er else None)}
        if eng_avail and ind_pct is not None:
            pfail = []
            # FIX1-02B/C: 基准日期+基准价格双校验——独立有基准时引擎必须提供
            # basis_date与basis_value(缺失即FAIL),百分比一致不得跳过价格核对
            if not er.get('basis_date'):
                pfail.append(f"{period}引擎缺基准日期(独立基准{iv.get('basis_date')})"
                             '——缺字段不得当一致')
            elif str(er.get('basis_date'))[:10] != str(iv.get('basis_date'))[:10]:
                pfail.append(f"{period}基准日期不一致: 引擎{er.get('basis_date')}"
                             f" vs 独立{iv.get('basis_date')}")
            if er.get('basis_value') is None:
                pfail.append(f"{period}引擎缺基准值(独立基准值{iv.get('basis_value')})"
                             '——缺字段不得当一致')
            else:
                _bv_dev = _price_mismatch_pct(er.get('basis_value'),
                                              iv.get('basis_value'))
                if _bv_dev is not None and _bv_dev > RECOMPUTE_PRICE_TOL_PCT:
                    pfail.append(f"{period}基准价格不一致: 引擎{er.get('basis_value')}"
                                 f" vs 独立{iv.get('basis_value')}"
                                 f"(相对差{round(_bv_dev, 4)}%)")
            diff = abs(_num(er.get('pct_change')) - ind_pct)
            row['difference_pp'] = round(diff, 4)
            if diff > tol_pp:
                pfail.append(f"{period}差异{diff:.4f}pp>容差{tol_pp}pp"
                             f"(引擎{er.get('pct_change')} vs 独立{ind_pct})")
            if pfail:
                row['status'] = 'FAIL'
                problems.extend(pfail)
            else:
                row['status'] = 'PASS'
        elif not eng_avail and ind_pct is None:
            row['status'] = 'INSUFFICIENT_HISTORY'
            row['reason'] = er.get('reason') or '双方均无期前基准观测'
        else:
            row['status'] = 'FAIL'
            which = '引擎' if ind_pct is not None else '独立'
            problems.append(f"{period}单侧可算({which}有值,对方无)——双方均未计算的"
                            '情况不得写为成功复算,单侧缺失为不一致')
        periods[period] = row

    verified = [p for p in ('week', 'mtd', 'ytd') if periods[p]['status'] == 'PASS']
    insufficient = [p for p in ('week', 'mtd', 'ytd')
                    if periods[p]['status'] == 'INSUFFICIENT_HISTORY']
    if problems:
        verdict = 'FAIL'                       # 任一期确定性计算/字段错误
    elif len(verified) == 3:
        verdict = 'PASS'                       # 完整复算: 三期全部独立一致
    else:
        verdict = 'INSUFFICIENT_HISTORY'       # 部分复核/全缺: 不冒充完整PASS
    if problems:
        note = '; '.join(problems)
    elif verdict == 'PASS':
        note = ('WEEK/MTD/YTD三期全部独立复算一致(含基准日期/基准价格/期末价格'
                '逐项核对)——完整复算')
    elif verified:
        note = (f"部分复核: {'/'.join(verified).upper()}与引擎一致,"
                f"{'/'.join(insufficient).upper()}历史不足"
                f"(已核{len(verified)}/3期)——非完整三期复算,不冒充完整PASS")
    else:
        note = '双方均无期前基准(历史不足,如实标注)'
    return dict(base, ours={'value': close, 'observation_date': obs,
                            'engine_end': eng_end or None, 'independent_end':
                            {'date': ind.get('obs'), 'value': ind.get('close')}},
                periods=periods, verdict=verdict,
                complete_recompute=(verdict == 'PASS'),
                verified_periods=verified, insufficient_periods=insufficient,
                note=note)


# ══ 综合结果与退出码(W5-04) ══════════════════════════════════════
def evaluate_overall(ext_results, recompute_results, skip_external):
    """三态: PASS/FAIL/NOT_VERIFIED。exit 0/2/3。
    只有真实独立可比通过才计PASS;NOT_COMPARABLE/NOT_VERIFIED/
    INSUFFICIENT_HISTORY/SKIPPED均不算PASS;覆盖门槛不满足→NOT_VERIFIED。"""
    all_res = list(ext_results) + list(recompute_results)
    dist = {s: sum(1 for r in all_res if r.get('verdict') == s) for s in STATUSES}
    n_fail = dist['FAIL']
    if n_fail:
        return {'overall': 'FAIL', 'exit_code': 2, 'distribution': dist,
                'coverage': None,
                'reasons': [f'存在{n_fail}项FAIL(重大数值/口径错误,不得通过)']}
    if skip_external:
        return {'overall': 'NOT_VERIFIED', 'exit_code': 3, 'distribution': dist,
                'coverage': None,
                'reasons': ['离线诊断模式(--skip-external): 真实外部核验未执行,'
                            '不得获得真实外部核验通过结论']}
    ust_ids = {'UST_2Y', 'UST_10Y', 'UST_30Y'}
    mkt_ids = {'BTC', 'SPX', 'SHCOMP'}

    def npass(ids=None, cat=None):
        return sum(1 for r in all_res
                   if r.get('verdict') == 'PASS'
                   and (ids is None or r.get('metric_id') in ids)
                   and (cat is None or r.get('category') == cat))

    # FIX1-03: recompute_check仅在WEEK/MTD/YTD三期全部独立一致时给verdict=PASS
    # (完整复算);外部构造行缺complete_recompute字段时按verdict==PASS视为完整(兼容)
    complete_rc = sum(1 for r in recompute_results
                      if r.get('verdict') == 'PASS'
                      and r.get('complete_recompute', True) is not False)
    cov = {'ust_pass': npass(ust_ids, 'external'),
           'market_pass': npass(mkt_ids, 'external'),
           'external_pass_total': npass(cat='external'),
           'recompute_pass': npass(cat='recompute'),
           'recompute_complete': complete_rc}
    reasons = []
    if cov['ust_pass'] < 1:
        reasons.append('利率类(UST)无任何真实同日可比PASS——利率证据缺失')
    if cov['market_pass'] < 2:
        reasons.append('市场资产类(BTC/SPX/SHCOMP)真实同日可比PASS不足2项——'
                       '其他资产证据缺失')
    if cov['external_pass_total'] < 4:
        reasons.append(f"外部对照总PASS{cov['external_pass_total']}<4——真实独立"
                       '可比证据不足')
    if cov['recompute_pass'] < 2:
        reasons.append(f"收益复算PASS{cov['recompute_pass']}<2——实际历史基准上的"
                       '独立复算不足')
    if cov['recompute_complete'] < 1:
        reasons.append('无任何资产完成WEEK/MTD/YTD三期完整独立复算'
                       f"(完整复算{cov['recompute_complete']}条)——部分复核/"
                       '历史不足不得冒充完整复算证据(至少需1条真实资产序列'
                       '三期全部独立复算一致)')
    if reasons:
        return {'overall': 'NOT_VERIFIED', 'exit_code': 3, 'distribution': dist,
                'coverage': cov, 'reasons': reasons}
    return {'overall': 'PASS', 'exit_code': 0, 'distribution': dist, 'coverage': cov,
            'reasons': [f"真实独立核验覆盖达标: UST×{cov['ust_pass']}/市场×"
                        f"{cov['market_pass']}/外部总PASS×{cov['external_pass_total']}"
                        f"/复算×{cov['recompute_pass']}(完整三期×"
                        f"{cov['recompute_complete']}),零FAIL"]}


# ══ 代码版本/输入证据(W5-05) ════════════════════════════════════
def git_version():
    def run(*a):
        try:
            return subprocess.run(['git', *a], cwd=ROOT_DIR, capture_output=True,
                                  text=True, timeout=10).stdout.strip()
        except Exception:
            return None
    head = run('rev-parse', 'HEAD')
    st = run('status', '--porcelain')
    return {'head': head, 'branch': run('branch', '--show-current'),
            'worktree_dirty_files': len(st.splitlines()) if st is not None else None}


def latest_real_day(data_dir, today_ymd):
    """最新一个四源齐全的真实采集日(≤today,5天新鲜窗)。"""
    def days_with(prefix):
        out = set()
        for fn in os.listdir(data_dir):
            m = re.match(rf'{prefix}_(\d{{8}})\.json$', fn)
            if m:
                out.add(m.group(1))
        return out
    common = (days_with('global') & days_with('macro')
              & days_with('china') & days_with('rate_economy'))
    eligible = sorted(d for d in common if d <= today_ymd)
    for d in reversed(eligible):
        lag = (date(int(today_ymd[:4]), int(today_ymd[4:6]), int(today_ymd[6:]))
               - date(int(d[:4]), int(d[4:6]), int(d[6:]))).days
        if lag <= 5:
            return d
    return None


def path_conflict(data_dir, out_dir):
    """FIX1-05: --data-dir与--out-dir路径关系安全检查(在任何输出写入/快照
    构建/真实外部API调用之前执行)。返回冲突描述(None=安全)。

    拒绝: 完全相同 / 输出位于输入内部 / 输出是输入的祖先(数据位于输出内部)
    / ..路径重叠 / 符号链接真实路径重叠。用realpath+commonpath做真实路径
    归一化比较,绝不做字符串前缀比较。"""
    try:
        d = os.path.realpath(os.path.abspath(data_dir))
        o = os.path.realpath(os.path.abspath(out_dir))
    except OSError as e:
        return f'路径解析失败:{e}'
    if d == o:
        return '输出目录与数据目录完全相同'
    try:
        cp = os.path.commonpath([d, o])
    except ValueError:
        return None    # 不同盘符等无法比较——不构成包含关系
    if cp == d:
        return '输出目录位于数据目录内部(验收产物会写进输入树)'
    if cp == o:
        return ('输出目录是数据目录的祖先(数据目录位于输出内部,产物写入会'
                '覆盖输入树的父层级)')
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data-dir', required=True, help='真实采集data/daily目录')
    ap.add_argument('--trusted-root', default=None,
                    help='采集可信项目根(缺省=代码位置推导的本仓库根;从隔离副本'
                         '验收真实数据时须显式传入该副本根——FIX8-03:不由--data-dir'
                         '自身推导父目录作授权依据)')
    ap.add_argument('--out-dir', default=os.path.join(ROOT_DIR, 'output', 'acceptance'))
    ap.add_argument('--data-day', default=None,
                    help='显式指定验收数据日YYYYMMDD(缺省=5天窗内最新四源齐全日;'
                         '显式选择留痕审计,如某最新日Gate A FAIL时选取前一日)')
    ap.add_argument('--skip-external', action='store_true',
                    help='跳过外部源(仅离线复算诊断;综合结果恒NOT_VERIFIED,'
                         '不得作为真实验收结论)')
    args = ap.parse_args()

    LOG = []

    def P(msg):
        LOG.append(msg)
        print(msg)

    # FIX1-05: 输出路径安全前置检查——在任何输出写入/快照构建/真实外部API
    # 调用之前;非法→明确拒绝+exit 2+零写入+零网络请求+不修改输入
    _conflict = path_conflict(args.data_dir, args.out_dir)
    if _conflict:
        P(f"❌ 输出路径安全检查未通过: {_conflict} "
          f"(data-dir={args.data_dir}, out-dir={args.out_dir})"
          "——拒绝执行: 不写任何文件/不构建快照/不触发外部请求/不修改输入")
        sys.exit(2)

    P("=" * 60)
    P("✅ 真实数据验收(W5版) — 独立外部来源 + 独立复算 + 三态综合")
    P("=" * 60)
    executed_at = now_utc_iso()

    gv = git_version()
    script_sha = hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest()

    today_ymd = datetime.now().strftime('%Y%m%d')
    if args.data_day:
        day = args.data_day
        lag = (date(int(today_ymd[:4]), int(today_ymd[4:6]), int(today_ymd[6:]))
               - date(int(day[:4]), int(day[4:6]), int(day[6:]))).days
        selection = f'--data-day显式指定(lag={lag}天)'
        need = {'global', 'macro', 'china', 'rate_economy'}
        have = {p for p in need if os.path.exists(os.path.join(args.data_dir, f'{p}_{day}.json'))}
        if have != need:
            P(f"❌ 指定数据日{day}四源不齐(缺:{sorted(need - have)})")
            sys.exit(1)
    else:
        day = latest_real_day(args.data_dir, today_ymd)
        if not day:
            P("❌ data-dir内5天窗口内无四源齐全的真实采集日")
            sys.exit(1)
        lag = (date(int(today_ymd[:4]), int(today_ymd[4:6]), int(today_ymd[6:]))
               - date(int(day[:4]), int(day[4:6]), int(day[6:]))).days
        selection = f'自动最新四源齐全日(lag={lag}天)'
    P(f"\n📌 验收数据日: {day}({selection};来源目录{args.data_dir})")

    fred_api_key = os.environ.get('FRED_API_KEY')
    if not fred_api_key:
        try:
            from env_config import FRED_API_KEY as _K
            fred_api_key = _K or None
        except ImportError:
            fred_api_key = None
    # FIX1-01: 运行时已知密钥明文登记(含URL编码形式)——进入一切脱敏/清扫路径
    if fred_api_key:
        _register_secret(fred_api_key)

    with tempfile.TemporaryDirectory() as td:
        snap = sb.build_snapshot(target_ymd=day, data_dir=args.data_dir, out_dir=td,
                                 trusted_root=args.trusted_root,
                                 as_of=datetime.now().astimezone().isoformat(timespec='seconds'))
        if snap is None:
            snap_path = os.path.join(td, f'research_snapshot_{day}.json')
            if os.path.exists(snap_path):
                snap = json.load(open(snap_path))
        if snap is None:
            P("❌ 快照构建失败")
            sys.exit(1)
        # FIX8-03沿用: Gate A非PASS/DEGRADED严格阻断(信任边界)
        _ga_status = (snap.get('gate_a') or {}).get('status')
        if _ga_status not in ('PASS', 'DEGRADED'):
            P(f"❌ 当日研究快照Gate A={_ga_status}(采集目录不可信或核心来源缺失)"
              "——该数据集不得通过真实数据验收")
            sys.exit(2)
        facts = {f['metric_id']: f for f in snap.get('facts', []) if isinstance(f, dict)}
        store = snap.get('series_store') or {}
        as_of = snap.get('research_as_of', '')
        ga = snap.get('gate_a') or {}

        # F2-AC-02: 读采集器随数据日global_*.json持久化的BTC收盘元数据
        # (sources_status.global.file=快照实际引用的输入文件名;旧采集产物
        # 无close_meta→None——如实披露,不构造)
        btc_close_meta = None
        _gfile = ((snap.get('sources_status') or {}).get('global') or {}).get('file')
        if _gfile:
            try:
                with open(os.path.join(args.data_dir, _gfile),
                          encoding='utf-8') as _gf:
                    btc_close_meta = (((json.load(_gf)).get('data') or {})
                                      .get('BTC') or {}).get('close_meta')
            except Exception:
                btc_close_meta = None
        if btc_close_meta:
            P(f"  [A2-meta] 读取global输入{_gfile}: BTC close_meta "
              f"source={btc_close_meta.get('source')}, "
              f"completed_through={btc_close_meta.get('completed_through_utc')}, "
              f"retrieved_at={btc_close_meta.get('retrieved_at_utc')}, "
              f"dropped={btc_close_meta.get('dropped_incomplete_utc_days')}")
        else:
            P(f"  [A2-meta] global输入{_gfile or '(未知)'}无BTC close_meta"
              "——旧采集器产物,我侧完结性无采集元数据证明,如实披露")

        results_ext, evidences, raws = [], [], []
        if args.skip_external:
            P("\n── A. 独立外部来源核验: 跳过(--skip-external离线诊断) ──")
        else:
            P("\n── A. 独立外部来源核验 ──")
            results_ext, evidences, raws = run_external_checks(
                facts, default_fetchers(fred_api_key), today_ymd, log=LOG,
                btc_close_meta=btc_close_meta)

        P("\n── B. 金融计算独立复算(周/MTD/YTD,期前收盘基准) ──")
        results_rc = []
        for mid in RECOMPUTE_METRICS:
            r = recompute_check(mid, facts.get(mid), store.get(mid))
            results_rc.append(r)
            P(f"  {mid}: {r['verdict']}"
              + (f" — {r['note'][:120]}" if r.get('note') else ''))

        overall = evaluate_overall(results_ext, results_rc, args.skip_external)

        # 纵深防御: 证据URL在写入前统一脱敏(即使注入的fetcher遗漏)
        for _ev in evidences:
            if isinstance(_ev, dict) and _ev.get('url'):
                _ev['url'] = redact_url(_ev['url'])
            if isinstance(_ev, dict) and _ev.get('error'):
                _ev['error'] = sanitize_text(_ev['error'])

        # Gate A行(历史兼容: 报告含'Gate A状态'检查行)
        gate_row = {'check': 'Gate A状态', 'metric_id': None, 'category': 'gate',
                    'ours': ga.get('status', '?'),
                    'external': f"core缺失:{','.join(ga.get('core_missing', []) or [])} "
                                f"FAIL:{','.join(ga.get('core_fail', []) or [])}",
                    'comparison': None, 'verdict': ga.get('status', 'DEGRADED'),
                    'note': 'PASS/DEGRADED方可进入验收;FAIL/缺失严格阻断(exit 2)'}

        checks = results_ext + results_rc + [gate_row]

        # ── 输出(Git外out-dir: JSON+MD+LOG+外部原始证据) ──
        os.makedirs(args.out_dir, exist_ok=True)
        stamp = datetime.now().strftime('%Y%m%d_%H%M')
        ev_files = []
        if raws:
            evdir = os.path.join(args.out_dir, 'evidence')
            os.makedirs(evdir, exist_ok=True)
            for i, (name, body) in enumerate(raws, 1):
                # FIX1-01: 外部原始正文写盘前密钥检查(命中→脱敏后落盘并留痕)
                if find_secret(body) is not None:
                    body = sanitize_text(body)
                    P(f"  ⚠ 外部原始正文含密钥残留,已脱敏后落盘: {name}")
                fn = f"{stamp}_{i:02d}_{name}.txt"
                with open(os.path.join(evdir, fn), 'w', encoding='utf-8') as fh:
                    fh.write(body)
                ev_files.append({'file': f'evidence/{fn}', 'source': name,
                                 'sha256': sha256_text(body),
                                 'bytes': len(body.encode('utf-8', 'replace'))})
                P(f"  外部原始证据: evidence/{fn}")

        unverified = [{'check': r['check'], 'verdict': r.get('verdict'),
                       'reason': (r.get('note') or '')[:200]}
                      for r in checks if r.get('verdict') != 'PASS']
        summary = {
            'report_schema': REPORT_SCHEMA,
            'acceptance_id': f'real_acceptance_{stamp}',
            'executed_at_utc': executed_at,
            'overall': overall['overall'],
            'exit_code': overall['exit_code'],
            'acceptance_mode': 'offline_diagnostic(--skip-external)' if args.skip_external
                               else 'formal_external_verification',
            'code_version': {'git': gv,
                             'script': {'path': os.path.abspath(__file__),
                                        'sha256': script_sha}},
            'data': {'data_day': day, 'lag_days': lag, 'selection': selection,
                     'data_dir': args.data_dir,
                     'data_dir_realpath': os.path.realpath(args.data_dir),
                     'trusted_root': args.trusted_root or '(缺省=代码位置推导)'},
            'snapshot': {'snapshot_id': snap.get('snapshot_id'),
                         'research_as_of': as_of,
                         'target_date': snap.get('target_date'),
                         'gate_a': {k: ga.get(k) for k in
                                    ('status', 'core_missing', 'core_fail',
                                     'noncore_missing', 'noncore_fail')},
                         'sources_status': snap.get('sources_status')},
            'btc_close_caliber': {
                'comparison_day_rule': BTC_COMPARISON_DAY_RULE,
                'close_meta': btc_close_meta,
                'close_meta_provenance': (
                    f'data_dir/{_gfile} → data.BTC.close_meta'
                    if _gfile else '(global输入文件名未知)'),
            },
            'inputs': {'metric_registry': {
                'path': os.path.join(ROOT_DIR, 'config', 'metric_registry.json'),
                'sha256': hashlib.sha256(
                    open(os.path.join(ROOT_DIR, 'config', 'metric_registry.json'),
                         'rb').read()).hexdigest(),
                'metric_count': len(fe.load_registry()['by_id'])}},
            'external_evidence': evidences,
            'external_evidence_files': ev_files,
            'tolerances': dict(TOLERANCES, recompute={
                'kind': 'pp', 'tol': RECOMPUTE_TOL_PP,
                'rule': f'|引擎pct_change − 独立pct_change| ≤ {RECOMPUTE_TOL_PP}个百分点'
                        '(基准日期必须一致,不核对基准日期的复算不算复算);'
                        f'FIX1-02价格字段: 期末价格(事实value vs 独立close)与基准价格'
                        f'(引擎basis_value vs 独立basis_value)相对差≤'
                        f'{RECOMPUTE_PRICE_TOL_PCT}%(金融数值精度),独立有基准时'
                        '引擎必须提供basis_date/basis_value(缺失即FAIL);'
                        'FIX1-03: 仅WEEK/MTD/YTD三期全部独立一致算完整复算PASS'
                        '(complete_recompute),部分复核=INSUFFICIENT_HISTORY不冒充',
                'rounding': RECOMPUTE_ROUNDING}),
            'checks': checks,
            'external_results': results_ext,
            'recompute_results': results_rc,
            'distribution': overall['distribution'],
            'coverage': overall['coverage'],
            'reasons': overall['reasons'],
            'unverified': unverified,
            'data_discipline': '真实采集数据验收;fixture测试在tests/目录,二者严格分离;'
                               '外部源不可达/缺字段/日期缺失/结果过期→NOT_VERIFIED如实'
                               '记录,不以他源冒充、不编造、不以旧日期结果补足',
            'notes': ['外部历史序列若已被修订,本报告核验的是**当前取得**的历史值,'
                      '不虚报当时信息可得性',
                      'FRED API密钥仅用于请求,URL在证据中脱敏(api_key=***REDACTED***),'
                      '密钥不写入任何证据文件',
                      '新浪为实时快照接口: 仅同日收盘口径可比较,历史日期无法经该接口证明'],
        }
        # FIX1-01: JSON/MD写盘前最终密钥清扫(纵深防御,幂等;MD由清扫后的
        # summary值构建,LOG在写盘时逐行再清扫)
        summary = sweep_secrets(summary)
        jpath = os.path.join(args.out_dir, f'real_acceptance_{stamp}.json')
        with open(jpath, 'w', encoding='utf-8') as fh:
            json.dump(summary, fh, ensure_ascii=False, indent=2)
        mpath = os.path.join(args.out_dir, f'real_acceptance_{stamp}.md')
        L = [f"# 真实数据验收报告({stamp})", "",
             f"- 综合结果: **{overall['overall']}** | 退出码: **{overall['exit_code']}**",
             f"- 验收数据日: **{day}**({selection})| 研究截止: {as_of}",
             f"- 快照: {snap.get('snapshot_id')} | Gate A: {ga.get('status')}",
             f"- 代码: HEAD={gv.get('head')} 脏文件={gv.get('worktree_dirty_files')} |"
             f" 脚本SHA256={script_sha[:16]}…",
             f"- 数据纪律: {summary['data_discipline']}", "",
             f"**状态分布: {overall['distribution']}**", ""]
        if overall.get('coverage'):
            L += [f"覆盖门槛: {overall['coverage']}", ""]
        L += ["## A. 外部来源对照(八项)", "",
              "| 检查项 | 快照值(观测日) | 外部值(观测日) | 来源 | 判定 | 备注 |",
              "|---|---|---|---|---|---|"]
        for r in results_ext:
            o, e = r.get('ours') or {}, r.get('external') or {}
            L.append(f"| {r['check']} | {o.get('value')}({o.get('observation_date')}) "
                     f"| {e.get('value', e.get('available_dates', '—'))}"
                     f"({e.get('observation_date', '')}) "
                     f"| — | **{r['verdict']}** | {(r.get('note') or '')[:160]} |")
        L += ["", "## B. 周/MTD/YTD独立复算", ""]
        for r in results_rc:
            _comp = '完整三期复算' if r.get('complete_recompute') else \
                (f"部分复核({','.join(r.get('verified_periods') or [])}已核)"
                 if r.get('verified_periods') else '非完整复算')
            L.append(f"### {r['check']} — **{r['verdict']}**({_comp})")
            L.append(f"- {r.get('note') or ''}")
            for p, row in (r.get('periods') or {}).items():
                ind = (row or {}).get('independent') or {}
                eng = (row or {}).get('engine') or {}
                L.append(f"- {p}: 独立基准{ind.get('basis_date')}@{ind.get('basis_value')}"
                         f"={ind.get('pct_change')}% | 引擎基准{eng.get('basis_date')}"
                         f"@{eng.get('basis_value')}={eng.get('pct_change')}%"
                         f" | 差{row.get('difference_pp', '—')}pp → {row.get('status')}")
            L.append("")
        L += ["## 综合判定",
              f"- **{overall['overall']}**(exit {overall['exit_code']})"]
        for reason in overall['reasons']:
            L.append(f"  - {reason}")
        L += ["", "## 判定口径",
              "- PASS: 独立来源/独立复算与快照在容差内一致(真实可比);",
              "- FAIL: 超容差/口径不一致(真实错误);",
              "- NOT_VERIFIED: 外部源不可达/缺字段/日期不匹配/结果过期/无密钥——"
              "如实记录,不得以最近观测或他源冒充;",
              "- NOT_COMPARABLE: 工具/口径身份不同(PAXG现货代理vs期货、WTI现货vs期货)"
              "——保留参考偏差,不得按容差证明;",
              "- INSUFFICIENT_HISTORY: 双方均无期前基准(历史不足,非成功复算);",
              "- SKIPPED: 快照侧缺该指标;",
              "- 综合: FAIL>NOT_VERIFIED>PASS;覆盖门槛(UST≥1真PASS+市场≥2真PASS+"
              "外部总PASS≥4+复算PASS≥2,且≥1条真实资产序列完成WEEK/MTD/YTD三期"
              "完整独立复算)不满足→NOT_VERIFIED;--skip-external恒NOT_VERIFIED;"
              "部分复算=INSUFFICIENT_HISTORY不冒充完整PASS。"]
        with open(mpath, 'w', encoding='utf-8') as fh:
            fh.write('\n'.join(L) + '\n')
        lpath = os.path.join(args.out_dir, f'real_acceptance_{stamp}.log')
        with open(lpath, 'w', encoding='utf-8') as fh:
            fh.write('\n'.join(sanitize_text(x) for x in LOG) + '\n')
        P(f"\n💾 验收报告: {mpath}")
        P(f"💾 JSON: {jpath}")
        P(f"💾 执行日志: {lpath}")
        P(f"\n综合结果: {overall['overall']} | 状态分布: {overall['distribution']}")
        for reason in overall['reasons']:
            P(f"  · {reason}")
        sys.exit(overall['exit_code'])


if __name__ == '__main__':
    main()
