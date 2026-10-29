#!/usr/bin/env python3
"""研究快照构建器(Layer 3) — 全部下游研究的唯一数据入口(spec §6/§13)

职责:
1. 解析当日采集文件(精确日期优先;缺当日文件时回退到新鲜度窗内最新文件并显式披露
   fallback+实际日期 —— 替代旧find_latest_file盲取glob最新的缺陷);
2. 经事实引擎规范化为事实记录(注册表身份/统一收益/12类校验/Gate A分级);
3. 产出不可变 research_snapshot_YYYYMMDD.json + 人读版.md(数值表程序确定性生成);
4. 产出旧格式锚点 anchors_YYYYMMDD.json(兼容桥: allocation_engine触发器/预测、
   每日观察器、Gate B校验继续工作;锚点源自快照事实而非重新拍平采集JSON)
   + anchors_YYYYMMDD.meta.json来源侧挂(source=snapshot/快照ID/digest/Gate A状态),
   并整体替换旧锚点(不与上一版merge,防残留键)——IA-P0-1来源链;

不可变性: 同日已存在快照时拒绝覆盖(退出码3);--allow-revision 生成 _v2 并留修订原因,
原版保留。快照文件不修改、不删除。

Gate A: 事实层校验结果写入快照quality节。core指标FAIL/缺失→gate FAIL
(快照仍落盘,缺失如实披露;缺数据不得进结论,但单个资产缺失不阻断系统)。
"""
import argparse
import glob
import hashlib
import json
import os
import re
import sys
from datetime import datetime, date, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import fact_engine as fe
import research_provenance as rp
from trading_calendar import expected_trading_days

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, 'data', 'daily')
TZ_BJ = timezone(timedelta(hours=8))

# 各源文件与其新鲜度窗(自然日): 回退取旧文件时超出窗口视为缺源(不冒充当日)
# FIX6-01(IA-F5-DEF-001): 规范文件身份/回退窗口**单一权威定义**在
# research_provenance.SOURCE_FILE_RULES——本模块自此推导SOURCES,构建端选择
# 与验证端(research_provenance)同一规则源,不两处独立维护漂移。
SOURCES = [(ch, f"{r['prefix']}*.json", r['max_fallback_days'])
           for ch, r in rp.SOURCE_FILE_RULES.items()]


def resolve_inputs(target_ymd, data_dir=None, trusted_root=None):
    """按目标日期解析采集文件: 精确匹配优先;否则新鲜度窗内最新早于目标日的文件(fallback)。

    FIX6-01: 只接受**通道规范普通文件**({prefix}YYYYMMDD.json真实日历日期、
    非目录、非符号链接)——目录冒充/伪装前后缀/其他扩展名/链接一律不选,
    构建端与research_provenance验证端同一规范,避免下游验证才发现异常。
    FIX7-01/02(IA-F6-DEF-001): 选取任何文件前先经rp.trusted_dir_problems
    核验**采集目录祖先路径可信边界**(与验证端共用同一原语,§6.3不两处
    漂移)——可信根缺省=rp.default_trusted_root()(可信代码位置推导,
    独立于data_dir,绝不由被校验目录或其realpath自证);祖先符号链接重
    定向/越界路径一律不读取该目录任何文件(全部按缺源处理,快照Gate A
    随之fail-closed),构建端不得先从链接重定向目录选出文件构成PASS快照、
    把发现异常推迟到下游。
    FIX8-01/02/03(IA-F7-DEF-001): 边界核验含**原始路径..组件拒绝**(词法
    折叠前)与**词法越界后realpath自动重新授信禁止**;核验通过后本函数
    一切文件访问(精确匹配/glob/读取)一律改用rp.trusted_source_dir返回的
    **已验证物理路径**——安全检查对象与实际读取对象为同一条路径,不再
    "检查normpath(dd)/IO用原始data_dir"分叉(验收反例:project/alias/..
    折叠后指向TRUSTED、经链接实际读取UNTRUSTED)。
    测试按FIX7-AC §5.3显式传入fixture控制的临时可信根(沙箱授权缝,
    生产入口不传该参数——不构成生产绕过后门)。"""
    dd = data_dir or DATA_DIR
    verified, trust_probs = rp.trusted_source_dir(dd, trusted_root)
    if trust_probs:
        for _p in trust_probs:
            print(f"⛔ [FIX7信任边界] {_p}")
        print(f"⛔ [FIX7信任边界] 采集目录不可信,不读取其任何文件"
              f"(全部按缺源处理): {dd}")
        return {name: None for name, _pat, _w in SOURCES}
    dd = verified   # FIX8-03: 后续一切文件访问=已验证物理路径
    out = {}
    for name, pattern, window in SOURCES:
        exact = os.path.join(dd, pattern.replace('*', target_ymd))
        if os.path.isfile(exact) and not os.path.islink(exact):
            out[name] = {'file': exact, 'file_date': target_ymd, 'exact': True, 'fallback': False}
            continue
        cands = sorted(glob.glob(os.path.join(dd, pattern)))
        usable = []
        for p in cands:
            fd = rp.canonical_source_file(name, os.path.basename(p))
            if fd is None:
                continue   # 非规范文件名(伪装前后缀/非法日期/其他通道样式)
            if os.path.islink(p) or not os.path.isfile(p):
                continue   # 目录/符号链接不是规范采集文件
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
    """从快照事实生成旧格式锚点(单一来源=快照;不再拍平采集JSON)。

    IA-P0-1: source_file记录**实际快照版本文件名**(含_vN后缀),锚点与其来源
    快照精确绑定;修订版生成时旧base锚点会被整体替换(见写入段)。"""
    anchors = {}
    as_of = f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}"
    reg = fe.load_registry()
    # 实际版本文件名: 修订时snapshot_id已带_vN(build_anchors在版本号确定后调用)
    snap_file = f"{snapshot.get('snapshot_id') or 'research_snapshot_' + ymd}.json"

    def emit(key, value, fact, obs=None):
        if value is None or not isinstance(value, (int, float)):
            return
        rec = {'value': value, 'source_file': snap_file,
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
                'source_file': snap_file, 'metric_id': 'ZQ_F1_PRICE'}
        if isinstance(c.get('implied_avg_rate'), (int, float)):
            anchors[f"rate_economy.fed_funds_futures.{i}.implied_rate"] = {
                'value': c['implied_avg_rate'], 'as_of': as_of, 'tolerance_pct': 1.0,
                'source_file': snap_file, 'metric_id': 'ZQ_IMPLIED_AVG'}
    return anchors


# ══ 快照构建 ══════════════════════════════════════════════════════

def build_snapshot(target_ymd=None, data_dir=None, out_dir=None, as_of=None,
                   write=True, allow_revision=False, revision_reason=None,
                   trusted_root=None):
    """trusted_root(FIX7-01): 采集目录可信根(缺省=rp.default_trusted_root(),
    可信代码位置推导);测试显式传入fixture控制的可信根。祖先符号链接重
    定向的采集目录构建即fail-closed(全通道缺源+Gate A不可证明),不得先
    构建PASS快照再由下游发现(§6.3)。"""
    now = datetime.now(TZ_BJ)
    ymd = target_ymd or now.strftime('%Y%m%d')
    as_of = as_of or now.isoformat(timespec='seconds')
    dd = data_dir or DATA_DIR
    od = out_dir or dd

    inputs = resolve_inputs(ymd, dd, trusted_root=trusted_root)
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
            # FIX7-05(IA-F6-RISK-002最小整改): 以字节读取并记录sha256内容
            # 摘要——快照与原始采集**内容**绑定,下游正式核验(data_dir口径)
            # 重算比对,构建后被替换/篡改的文件以摘要失配拒绝
            with open(info['file'], 'rb') as f:
                _bytes = f.read()
            st['sha256'] = hashlib.sha256(_bytes).hexdigest()
            raw[name] = json.loads(_bytes.decode('utf-8'))
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
    # IA-P0-1-FIX5(IA-DEF-006)+FIX2-02(IA-DEF-002): 核心与否以注册表criticality
    # 为唯一权威,且Gate A在写入时即按recompute_gate_a**从事实重算**——
    # 非核心指标FAIL按质量规则降级披露(DEGRADED);核心缺失/失败才判FAIL;
    # 重复metric_id=数据身份冲突判FAIL。写入裁决与下游核验(research_provenance.
    # gate_status)同源同口径,快照声明与事实不可能在构建时就矛盾。
    rec = rp.recompute_gate_a({'facts': facts, 'sources_status': sources_status,
                               'research_as_of': as_of, 'target_date': ymd},
                              data_dir=dd, trusted_root=trusted_root)
    gate_a = {'status': rec['effective'],
              'core_missing': rec['core_missing'], 'core_fail': rec['core_fail'],
              'noncore_fail': rec['noncore_fail'],
              'noncore_missing': rec['noncore_missing'],
              'note': '缺失/失败数据已披露,不得进入研究结论;单个资产缺失不阻断其余研究;'
                      '非核心FAIL按降级披露(注册表criticality为权威)'}
    if rec['duplicates']:
        gate_a['note'] += f';重复metric_id按FAIL处置: {",".join(rec["duplicates"][:6])}'
    if rec['effective'] is None:
        # FIX3-01(F2-NEW-001)fail-closed: 事实集合存在非法/不可证明结构
        # (非对象/身份缺失/质量缺失或非法/FIX4-01必要字段或注册表身份不符)
        # ——快照如实写入非法状态(不可变存证),但不得作为合格快照放行:
        # status=None,下游gate_status/装配/报告全部拒绝
        gate_a['note'] = ('事实结构非法/不可证明('
                          + '; '.join(rec['reasons'][:2])
                          + ')——本快照不得用于正式研究')
        gate_a['illegal_quality'] = rec['illegal_quality']
    # FIX4-03(FIX3-NEW-003): 非核心完全缺失的结构化披露(快照JSON保存缺失
    # 信息+原因;MD另行渲染;Gate A因此至少DEGRADED——见recompute_gate_a)
    if rec['noncore_missing']:
        gate_a['noncore_missing_detail'] = rec['noncore_missing_detail']
    if rec.get('noncore_missing_boundary'):
        gate_a['noncore_missing_boundary'] = rec['noncore_missing_boundary']
    if rec['non_research_facts']:
        gate_a['non_research_facts'] = rec['non_research_facts']
    gate_a['noncore_degraded'] = rec['noncore_degraded']
    gate_a['illegal_quality'] = rec['illegal_quality']

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
    # IA-P0-1: 原子写(tmp+replace)——中途崩溃不留半写快照被误当有效版本
    _tmp = json_path + '.tmp'
    with open(_tmp, 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=1)
    os.replace(_tmp, json_path)
    md_path = json_path.replace('.json', '.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(render_markdown(snapshot))

    # IA-P0-1: 锚点整体替换(不再与旧文件merge)——旧实现old.update(anchors)会把
    # 上一版残留键(当日已剔除的指标/旧观测)留在anchors_{ymd}.json里被下游误用。
    # 锚点唯一来源=本次快照,快照可追溯则锚点可追溯。
    anchors = build_anchors(snapshot, ymd)
    anchors_path = os.path.join(od, f"anchors_{ymd}.json")
    _tmpa = anchors_path + '.tmp'
    with open(_tmpa, 'w', encoding='utf-8') as f:
        json.dump(anchors, f, ensure_ascii=False, indent=1)
    os.replace(_tmpa, anchors_path)
    # 锚点meta sidecar: 声明批次来源,供观察器(任务7)与报告入口(任务5)核验;
    # FIX-01: 附锚点实际内容摘要——下游读取实际文件重算比对,声明值不被信任
    rp.write_meta(anchors_path, {
        'source': 'snapshot',
        'generated_by': 'snapshot_builder',
        'generated_at': as_of,
        **rp.provenance_of(snapshot, json_path, data_dir=dd,
                           trusted_root=trusted_root),
        'anchor_count': len(anchors),
        'anchors_digest': rp.digest_file(anchors_path),
    })

    print(f"✅ 快照: {json_path}")
    print(f"   MD:   {md_path}")
    print(f"   锚点: {anchors_path} ({len(anchors)}个)")
    print(f"   Gate A: {gate_a['status']} | 事实 {len(facts)} | "
          f"质量 {quality['counts']} | core缺失 {len(quality['missing_core'])}"
          + (f" | 非核心缺失 {len(gate_a['noncore_missing'])}项"
             f"({','.join(gate_a['noncore_missing'][:5])})"
             f"{'' if len(gate_a['noncore_missing']) <= 5 else '…'}"
             if gate_a.get('noncore_missing') else ''))
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
    # FIX4-03: 非核心完全缺失披露(本期无事实,采集遗漏/来源缺失——已降级,
    # 未补零未伪造;有效数据继续研究)
    if snap['gate_a'].get('noncore_missing'):
        det = snap['gate_a'].get('noncore_missing_detail') or {}
        L.append('')
        L.append("**⚠️ 非核心指标缺失(本期无事实,Gate A已降级披露)**:")
        for mid in snap['gate_a']['noncore_missing']:
            L.append(f"- {mid}: {det.get(mid, '原因未注明')}")

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
    ap.add_argument('--trusted-root', default=None,
                    help='采集目录可信根(FIX7;默认=代码位置推导的项目根;'
                         '沙箱/诊断显式传入,生产不传。祖先符号链接重定向'
                         '的采集目录一律fail-closed)')
    ap.add_argument('--out-dir', default=None, help='输出目录(默认data/daily)')
    ap.add_argument('--allow-revision', action='store_true', help='同日已存在时生成_v2修订版(原版保留)')
    ap.add_argument('--revision-reason', default=None)
    # IA-P0-2-W2: 可选研究截止时点(默认仍为当前时间,生产不传,行为零变化)——
    # 供测试注入确定性as_of。此前测试以CLI子进程构建快照时只能用真实墙钟,
    # 快照事实的时效判定随运行日期漂移(观测日固定,W2批准窗口收紧至5天后,
    # 场景日+6天起即误触DEGRADED)——时点语义测试须可显式钉定研究截止。
    ap.add_argument('--as-of', default=None,
                    help='研究截止时刻ISO(默认当前时间;测试注入确定性时点,生产不传)')
    args = ap.parse_args()
    snap = build_snapshot(target_ymd=args.date, data_dir=args.data_dir, out_dir=args.out_dir,
                          trusted_root=args.trusted_root,
                          allow_revision=args.allow_revision, revision_reason=args.revision_reason,
                          as_of=args.as_of)
    if not snap:
        sys.exit(3)
    # 2026-10-21 P1修复: Gate A FAIL不得再静默exit 0——此前连续多日FAIL但流水线
    # 退出码为0,launchd侧完全无感。FAIL→退出码2(快照仍写盘,只上报失败);
    # DEGRADED是已披露降级,保持0。
    # IA-P0-1-FIX3(FIX3-01): status=None(事实结构非法/不可证明)同按退出码2
    # 上报——非法结构快照不得以exit 0冒充正常产出。
    status = (snap.get('gate_a') or {}).get('status')
    if status == 'FAIL':
        print(f"⚠️ Gate A FAIL(core_missing={snap['gate_a'].get('core_missing')}, "
              f"core_fail={snap['gate_a'].get('core_fail')})——快照已保存,本步骤以退出码2上报")
        sys.exit(2)
    if status not in ('PASS', 'DEGRADED'):
        print(f"⛔ Gate A非法/不可证明(status={status!r},"
              f"illegal_quality={len(snap['gate_a'].get('illegal_quality') or [])}条)"
              "——快照已存证,本步骤以退出码2上报(FIX3-01 fail-closed)")
        sys.exit(2)
    sys.exit(0)
