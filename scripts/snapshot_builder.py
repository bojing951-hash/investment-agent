#!/usr/bin/env python3
"""研究快照构建器(Layer 3) — 全部下游研究的唯一数据入口(spec §6/§13)

职责:
1. 解析当日采集文件(精确日期优先;缺当日文件时回退到新鲜度窗内最新文件并显式披露
   fallback+实际日期 —— 替代旧find_latest_file盲取glob最新的缺陷);
2. 经事实引擎规范化为事实记录(注册表身份/统一收益/12类校验/Gate A分级);
3. 产出不可变 research_snapshot_YYYYMMDD.json + 人读版.md(数值表程序确定性生成);
4. 产出旧格式锚点 anchors_YYYYMMDD.json(兼容桥: allocation_engine触发器/预测、
   每日观察器、Gate B校验继续工作;锚点源自快照事实而非重新拍平采集JSON);

不可变性: 同日已存在快照时拒绝覆盖(退出码3);--allow-revision 生成 _v2 并留修订原因,
原版保留。快照文件不修改、不删除。

Gate A: 事实层校验结果写入快照quality节。core指标FAIL/缺失→gate FAIL
(快照仍落盘,缺失如实披露;缺数据不得进结论,但单个资产缺失不阻断系统)。
"""
import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime, date, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import fact_engine as fe
from trading_calendar import expected_trading_days

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, 'data', 'daily')
TZ_BJ = timezone(timedelta(hours=8))

# 各源文件与其新鲜度窗(自然日): 回退取旧文件时超出窗口视为缺源(不冒充当日)
SOURCES = [
    ('global', 'global_*.json', 5),
    ('macro', 'macro_*.json', 7),
    ('china', 'china_*.json', 5),
    ('rate_economy', 'rate_economy_*.json', 7),
]


def resolve_inputs(target_ymd, data_dir=None):
    """按目标日期解析采集文件: 精确匹配优先;否则新鲜度窗内最新早于目标日的文件(fallback)。"""
    dd = data_dir or DATA_DIR
    out = {}
    for name, pattern, window in SOURCES:
        exact = os.path.join(dd, pattern.replace('*', target_ymd))
        if os.path.exists(exact):
            out[name] = {'file': exact, 'file_date': target_ymd, 'exact': True, 'fallback': False}
            continue
        cands = sorted(glob.glob(os.path.join(dd, pattern)))
        usable = []
        for p in cands:
            m = re.search(r'(\d{8})', os.path.basename(p))
            if not m:
                continue
            fd = m.group(1)
            if fd < target_ymd:
                lag = (date.fromisoformat(f"{target_ymd[:4]}-{target_ymd[4:6]}-{target_ymd[6:]}")
                       - date.fromisoformat(f"{fd[:4]}-{fd[4:6]}-{fd[6:]}")).days
                if lag <= window:
                    usable.append((fd, lag, p))
        if usable:
            fd, lag, p = usable[-1]
            out[name] = {'file': p, 'file_date': fd, 'exact': False, 'fallback': True, 'lag_days': lag}
        else:
            out[name] = None
    return out


# ══ 兼容桥: 快照事实 → 旧锚点键名 ═════════════════════════════════

_GLOBAL_OLD_ID = {'GOLD_F': 'GOLD', 'SILVER_F': 'SILVER', 'WTI_F': 'WTI', 'BRENT_F': 'BRENT',
                  'USDJPY': 'JPY=X', 'USDCNY': 'CNY=X', 'GBPUSD': 'GBPUSD=X'}
_CHINA_LABEL = {'SHCOMP': '上证指数', 'SZCI': '深证成指', 'CHINEXT': '创业板指',
                'HSI': '恒生指数', 'HSCEI': '恒生国企指数'}
_RATE_OLD_NAME = {'UNEMPLOYMENT': 'UNRATE', 'NFP': 'PAYEMS', 'UMCSENT': 'UMCSENT',
                  'RSAFS': 'RSAFS', 'INDPRO': 'INDPRO', 'JTSJOL': 'JTSJOL'}


def _chg_from_derived(d, prefer):
    for k in prefer:
        if isinstance(d, dict) and d.get(k) is not None:
            return d[k]
    return None


def build_anchors(snapshot, ymd):
    """从快照事实生成旧格式锚点(单一来源=快照;不再拍平采集JSON)。"""
    anchors = {}
    as_of = f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}"
    reg = fe.load_registry()

    def emit(key, value, fact, obs=None):
        if value is None or not isinstance(value, (int, float)):
            return
        rec = {'value': value, 'source_file': f"research_snapshot_{ymd}.json",
               'as_of': as_of, 'tolerance_pct': 1.0,
               'metric_id': fact.get('metric_id'), 'quality': fact.get('quality_status'),
               'fact_id': fact.get('fact_id')}
        obs = obs or fact.get('observation_date')
        if obs:
            rec['obs_date'] = str(obs)[:10]
        if fact.get('high') is not None:
            rec['high'] = fact['high']
        if fact.get('low') is not None:
            rec['low'] = fact['low']
        anchors[key] = rec

    for f in snapshot.get('facts', []):
        mid = f.get('metric_id')
        m = reg['by_id'].get(mid)
        if not m:
            continue
        freq, unit = m.get('frequency'), m.get('unit')
        d = f.get('derived') or {}
        if mid in _CHINA_LABEL:
            base = f"china.data.{_CHINA_LABEL[mid]}"
            emit(f"{base}.close", f.get('value'), f)
            wk = d.get('week') or {}
            emit(f"{base}.week_chg", wk.get('pct_change'), f)
            emit(f"{base}.ytd_chg", (d.get('ytd') or {}).get('pct_change'), f)
        elif mid in ('HSAHP', 'SH_AMOUNT', 'SZ_COMPONENT_AMOUNT', 'CN_TOTAL_TURNOVER',
                     'SB_FLOW', 'MARGIN_BAL', 'SH_PE'):
            _CN_ANCHOR_KEY = {'HSAHP': 'china.ah_premium.close',
                              'SH_AMOUNT': 'china.turnover.sh_amount_billion',
                              'SZ_COMPONENT_AMOUNT': 'china.turnover.sz_amount_billion',
                              'CN_TOTAL_TURNOVER': 'china.turnover.total_amount_billion',
                              'SB_FLOW': 'china.southbound.net_buy',
                              'MARGIN_BAL': 'china.margin.balance',
                              'SH_PE': 'china.valuation.pe'}
            emit(_CN_ANCHOR_KEY[mid], f.get('value'), f)
            if mid == 'CN_TOTAL_TURNOVER':
                emit('china.turnover.volume_billion', f.get('value'), f)
        elif m.get('source') == 'global_market_collector':
            old = _GLOBAL_OLD_ID.get(mid, mid)
            base = f"global_market.data.{old}"
            emit(f"{base}.close", f.get('value'), f)
            for fld, dkey in (('week_chg', ('pct_change',)), ('mtd_chg', ('pct_change',)),
                              ('ytd_chg', ('pct_change',))):
                v = _chg_from_derived(d.get(dkey[0]) or {}, ('pct_change',)) if dkey else None
                emit(f"{base}.{fld}", v, f)
        elif m.get('source') == 'macro_collector' and m.get('asset_class') not in ('macro_count_derived',):
            base = f"macro.data.{mid}"
            emit(f"{base}.value", f.get('value'), f)
            if freq == 'monthly':
                m1, m12 = d.get('m1') or {}, d.get('m12') or {}
                emit(f"{base}.prev", m1.get('basis_value'), f)
                emit(f"{base}.mom_chg", _chg_from_derived(m1, ('pp_change', 'abs_change')), f)
                emit(f"{base}.mom_pct", m1.get('pct_change'), f)
                emit(f"{base}.yoy_chg", _chg_from_derived(m12, ('pp_change', 'abs_change')), f)
                emit(f"{base}.yoy_pct", m12.get('pct_change'), f)
            elif freq == 'weekly':
                wk = d.get('week') or {}
                emit(f"{base}.prev", wk.get('basis_value'), f)
                emit(f"{base}.week_chg", _chg_from_derived(wk, ('abs_change', 'pp_change')), f)
            else:
                wk = d.get('week') or {}
                emit(f"{base}.prev", wk.get('basis_value'), f)
                emit(f"{base}.week_chg", _chg_from_derived(wk, ('pp_change', 'abs_change', 'pct_change')), f)
        elif m.get('source') in ('fact_engine(derived)',):
            if mid in ('REAL_10Y', 'REAL_5Y', 'HY_IG_DIFF'):
                emit(f"macro.derived.{mid}", f.get('value'), f)
            elif mid == 'ZQ_IMPLIED_AVG':
                emit("rate_economy.fed_funds_futures.implied_rate", f.get('value'), f)
        elif m.get('source') == 'rate_expectations':
            if mid in ('DFF', 'DFEDTARU', 'DFEDTARL'):
                emit(f"rate_economy.current_rates.{mid}.value", f.get('value'), f)
    # rate_economy.real_economy.* — 取macro事实值(单一来源),挂旧键名
    for mid, old in _RATE_OLD_NAME.items():
        f = next((x for x in snapshot.get('facts', []) if x.get('metric_id') == mid), None)
        if f:
            emit(f"rate_economy.real_economy.{old}.value", f.get('value'), f)
            m1 = (f.get('derived') or {}).get('m1') or {}
            emit(f"rate_economy.real_economy.{old}.prev_value", m1.get('basis_value'), f)
    # 联邦基金期货曲线(按月合约,研究上下文)
    for i, c in enumerate(snapshot.get('fed_futures_curve') or []):
        if isinstance(c.get('price'), (int, float)):
            anchors[f"rate_economy.fed_funds_futures.{i}.price"] = {
                'value': c['price'], 'as_of': as_of, 'tolerance_pct': 1.0,
                'source_file': f"research_snapshot_{ymd}.json", 'metric_id': 'ZQ_F1_PRICE'}
        if isinstance(c.get('implied_avg_rate'), (int, float)):
            anchors[f"rate_economy.fed_funds_futures.{i}.implied_rate"] = {
                'value': c['implied_avg_rate'], 'as_of': as_of, 'tolerance_pct': 1.0,
                'source_file': f"research_snapshot_{ymd}.json", 'metric_id': 'ZQ_IMPLIED_AVG'}
    return anchors


# ══ 快照构建 ══════════════════════════════════════════════════════

def build_snapshot(target_ymd=None, data_dir=None, out_dir=None, as_of=None,
                   write=True, allow_revision=False, revision_reason=None):
    now = datetime.now(TZ_BJ)
    ymd = target_ymd or now.strftime('%Y%m%d')
    as_of = as_of or now.isoformat(timespec='seconds')
    dd = data_dir or DATA_DIR
    od = out_dir or dd

    inputs = resolve_inputs(ymd, dd)
    sources_status = {}
    raw = {}
    for name, info in inputs.items():
        if info is None:
            sources_status[name] = {'status': 'MISSING'}
            continue
        st = {'status': 'EXACT' if info['exact'] else 'FALLBACK',
              'file': os.path.basename(info['file']), 'file_date': info['file_date']}
        if not info['exact']:
            st['lag_days'] = info['lag_days']
            st['disclosure'] = f"当日文件缺失,回退{info['lag_days']}天前文件(数据非当日,不得当作当日观测)"
        sources_status[name] = st
        try:
            with open(info['file'], 'r', encoding='utf-8') as f:
                raw[name] = json.load(f)
        except Exception as e:
            sources_status[name] = {'status': 'READ_FAIL', 'error': str(e)[:100]}

    facts = []
    if 'global' in raw:
        facts += fe.normalize_global(raw['global'].get('data') or {}, as_of,
                                     sources_status['global']['file'])
    if 'macro' in raw:
        facts += fe.normalize_macro(raw['macro'].get('data') or {}, as_of,
                                    sources_status['macro']['file'])
    if 'china' in raw:
        facts += fe.normalize_china(raw['china'].get('data') or raw['china'], as_of,
                                    sources_status['china']['file'])
    rate_recon_extra = []
    curve = []
    if 'rate_economy' in raw:
        rfacts, rinfo = fe.normalize_rate(raw['rate_economy'], as_of,
                                          sources_status['rate_economy']['file'])
        facts += rfacts
        curve = rinfo.get('fed_futures_curve') or []
        # 对账: rate通道real_economy数值 vs macro权威事实
        by_id = {f.get('metric_id'): f for f in facts}
        for r in rinfo.get('recon_inputs') or []:
            mf = by_id.get(r['metric_id'])
            if not mf:
                continue
            if isinstance(r.get('value'), (int, float)) and isinstance(mf.get('value'), (int, float)):
                diff = round(r['value'] - mf['value'], 4)
                rel = abs(diff) / max(abs(mf['value']), 1e-9)
                rate_recon_extra.append({
                    'type': 'source-diff', 'check': f"rate通道 vs macro采集: {r['metric_id']}",
                    'result': 'consistent' if rel < 0.005 else 'diff-needs-review',
                    'detail': f"rate={r['value']} macro={mf['value']} 差{diff:+.4f}"
                              + (f"(观测日不同: rate {r.get('observation_date')} vs macro {mf.get('observation_date')})"
                                 if str(r.get('observation_date'))[:10] != str(mf.get('observation_date'))[:10] else "")})
    facts += fe.compute_derived(facts, as_of)
    recon = fe.cross_metric_checks(facts) + rate_recon_extra
    quality = fe.snapshot_quality_grade(facts)
    by_id = {f.get('metric_id'): f for f in facts}
    core_fail = [mid for mid, f in by_id.items() if f.get('quality_status') == 'FAIL']
    gate_a = {'status': 'FAIL' if (quality['missing_core'] or core_fail) else
                     ('DEGRADED' if quality['counts'].get('DEGRADED') else 'PASS'),
              'core_missing': quality['missing_core'], 'core_fail': core_fail,
              'note': '缺失/失败数据已披露,不得进入研究结论;单个资产缺失不阻断其余研究'}

    snapshot = {
        'snapshot_id': f"research_snapshot_{ymd}",
        'research_as_of': as_of,
        'target_date': ymd,
        'timezone': 'Asia/Shanghai',
        'sources_status': sources_status,
        'fed_futures_curve': curve,
        'facts': facts,
        'reconciliation': recon,
        'quality': quality,
        'gate_a': gate_a,
        'notes': ['全部事实含metric_id/单位/观测日/来源/质量;派生值附calculation_ref',
                  '本快照为唯一研究数据入口;下游不得自行查找最新采集文件'],
    }
    # series_store: 相关性等配对序列研究用(全球行情资产+中国/港股指数,新metric_id为键)
    store = {}
    if 'global' in raw:
        inv_map = {v: k for k, v in _GLOBAL_OLD_ID.items()}
        for aid, item in (raw['global'].get('data') or {}).items():
            mid = inv_map.get(aid, aid)
            if isinstance(item, dict) and isinstance(item.get('series'), dict):
                store[mid] = item['series']
    if 'china' in raw:
        # 新旧两代采集格式的指数序列(代码/中文名→注册表metric_id)
        _CN_CODE = {"000001.SH": "SHCOMP", "399001.SZ": "SZCI", "399006.SZ": "CHINEXT"}
        _CN_NAME = {"上证指数": "SHCOMP", "深证成指": "SZCI", "创业板指": "CHINEXT",
                    "恒生指数": "HSI", "恒生国企指数": "HSCEI"}
        _HK_CODE = {"^HSI": "HSI", "^HSCE": "HSCEI", "^HSCEI": "HSCEI"}
        pools = []
        pools.extend((raw['china'].get('a_share_indices') or {}).items())
        pools.extend((raw['china'].get('hk_indices') or {}).items())
        pools.extend((raw['china'].get('indices') or {}).items())
        for key, item in pools:
            mid = _CN_CODE.get(key) or _HK_CODE.get(key) or _CN_NAME.get(key)
            if mid and isinstance(item, dict) and isinstance(item.get('series'), dict) \
                    and mid not in store:
                store[mid] = item['series']
    if store:
        snapshot['series_store'] = store

    if not write:
        return snapshot

    os.makedirs(od, exist_ok=True)
    json_path = os.path.join(od, f"research_snapshot_{ymd}.json")
    if os.path.exists(json_path):
        if not allow_revision:
            print(f"⛔ 快照已存在且不可变: {json_path}(须--allow-revision生成新版本)")
            return None
        n = 2
        while os.path.exists(os.path.join(od, f"research_snapshot_{ymd}_v{n}.json")):
            n += 1
        json_path = os.path.join(od, f"research_snapshot_{ymd}_v{n}.json")
        snapshot['snapshot_id'] = f"research_snapshot_{ymd}_v{n}"
        snapshot['revision_reason'] = revision_reason or '未注明'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=1)
    md_path = json_path.replace('.json', '.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(render_markdown(snapshot))

    anchors = build_anchors(snapshot, ymd)
    anchors_path = os.path.join(od, f"anchors_{ymd}.json")
    if os.path.exists(anchors_path):
        with open(anchors_path, 'r', encoding='utf-8') as f:
            old = json.load(f)
        old.update(anchors)
        anchors = old
    with open(anchors_path, 'w', encoding='utf-8') as f:
        json.dump(anchors, f, ensure_ascii=False, indent=1)

    print(f"✅ 快照: {json_path}")
    print(f"   MD:   {md_path}")
    print(f"   锚点: {anchors_path} ({len(anchors)}个)")
    print(f"   Gate A: {gate_a['status']} | 事实 {len(facts)} | "
          f"质量 {quality['counts']} | core缺失 {len(quality['missing_core'])}")
    return snapshot


# ══ 人读版渲染(数值表程序确定性生成,§13) ══════════════════════════

_QFLAG = {'PASS': '', 'DEGRADED': ' ⚠️', 'FAIL': ' ❌'}


def _fmt_chg(f, key='week'):
    d = (f.get('derived') or {}).get(key) or {}
    if not d or d.get('available') is False:
        return '—'
    if 'pct_change' in d:
        return f"{d['pct_change']:+.2f}%"
    if 'pp_change' in d:
        return f"{d['pp_change']:+.2f}pp"
    if 'abs_change' in d:
        return f"{d['abs_change']:+,.2f}"
    return '—'


def render_markdown(snap):
    L = [f"# 研究快照 {snap['snapshot_id']}", '',
         f"- 研究截止(research_as_of): **{snap['research_as_of']}** (Asia/Shanghai)",
         f"- Gate A: **{snap['gate_a']['status']}** | 事实质量 {snap['quality']['counts']}",
         f"- 不可变快照;本文件数值表由程序确定性生成(GLM只作解释,不选数/不改数)", '']

    L.append('## 数据源状态')
    L.append('| 源 | 状态 | 文件 | 采集日 | 披露 |')
    L.append('|---|---|---|---|---|')
    for name, st in snap['sources_status'].items():
        L.append(f"| {name} | {st.get('status')} | {st.get('file', '—')} | "
                 f"{st.get('file_date', '—')} | {st.get('disclosure', '')} |")
    if snap['gate_a']['core_missing']:
        L.append('')
        L.append(f"**⚠️ core指标缺失**: {', '.join(snap['gate_a']['core_missing'])} — 相关结论不得生成")
    if snap['gate_a']['core_fail']:
        L.append(f"**❌ core指标FAIL**: {', '.join(snap['gate_a']['core_fail'])}")

    fams = [('权益/波动率', ('equity_index', 'single_stock', 'volatility_index', 'crypto')),
            ('ETF(代理已标注)', ('bond_etf', 'country_etf_proxy', 'spot_commodity_etf',
                                'commodity_futures_etf')),
            ('汇率', ('fx_index', 'fx_rate')),
            ('商品期货', ('commodity_futures',)),
            ('利率与信用(日频)', ('rates_yield', 'credit_spread', 'real_rate',
                                   'inflation_expectation', 'curve_slope', 'policy_rate')),
            ('宏观(月频)', ('macro_index', 'macro_rate', 'macro_count', 'macro_count_derived',
                             'macro_price', 'sentiment')),
            ('中国', ('spread_index', 'flow', 'leverage', 'valuation', 'volume_amount'))]
    for title, classes in fams:
        rows = [f for f in snap['facts']
                if isinstance(f, dict) and fe.metric(f.get('metric_id', ''))
                and fe.metric(f['metric_id']).get('asset_class') in classes]
        if not rows:
            continue
        L.append('')
        L.append(f'## {title}')
        L.append('| 指标 | 收盘/最新 | 单位 | 观测日 | 周变化 | 身份备注 | 质量 |')
        L.append('|---|---|---|---|---|---|---|')
        for f in rows:
            ident = f.get('identity') or {}
            note = ('代理:' + str(ident.get('proxy_of'))[:24]) if ident.get('is_proxy') else ''
            val = f.get('value')
            val_s = f"{val:,.2f}" if isinstance(val, (int, float)) else '—'
            L.append(f"| {f.get('display_name')} | {val_s} | {f.get('unit')} | "
                     f"{f.get('observation_date')} | {_fmt_chg(f)} | {note} | "
                     f"{f.get('quality_status')}{_QFLAG.get(f.get('quality_status'), '')} |")

    if snap.get('reconciliation'):
        L.append('')
        L.append('## 对账与跨指标核验')
        for r in snap['reconciliation']:
            L.append(f"- [{r.get('result')}] {r.get('check')}: {r.get('detail')}")
    if snap.get('fed_futures_curve'):
        L.append('')
        L.append('## 联邦基金期货隐含(合约=对应日历月**日均**利率,非降息次数)')
        L.append('| 合约 | 价格 | 隐含日均利率 |')
        L.append('|---|---|---|')
        for c in snap['fed_futures_curve'][:8]:
            L.append(f"| {c.get('name') or c.get('ticker')} | {c.get('price')} | "
                     f"{c.get('implied_avg_rate')}% |")
    return '\n'.join(L) + '\n'


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='研究快照构建器(Layer 3, Gate A)')
    ap.add_argument('--date', default=None, help='目标日期YYYYMMDD(默认今天)')
    ap.add_argument('--data-dir', default=None, help='采集数据目录(默认data/daily)')
    ap.add_argument('--out-dir', default=None, help='输出目录(默认data/daily)')
    ap.add_argument('--allow-revision', action='store_true', help='同日已存在时生成_v2修订版(原版保留)')
    ap.add_argument('--revision-reason', default=None)
    args = ap.parse_args()
    snap = build_snapshot(target_ymd=args.date, data_dir=args.data_dir, out_dir=args.out_dir,
                          allow_revision=args.allow_revision, revision_reason=args.revision_reason)
    if not snap:
        sys.exit(3)
    # 2026-10-21 P1修复: Gate A FAIL不得再静默exit 0——此前连续多日FAIL但流水线
    # 退出码为0,launchd侧完全无感。FAIL→退出码2(快照仍写盘,只上报失败);
    # DEGRADED是已披露降级,保持0。
    status = (snap.get('gate_a') or {}).get('status')
    if status == 'FAIL':
        print(f"⚠️ Gate A FAIL(core_missing={snap['gate_a'].get('core_missing')}, "
              f"core_fail={snap['gate_a'].get('core_fail')})——快照已保存,本步骤以退出码2上报")
        sys.exit(2)
    sys.exit(0)
