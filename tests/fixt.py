"""IA-P0-1-FIX2 共享测试fixture: 真实注册表齐备的研究日构造器。

FIX2-02测试要求: fixture必须使用**真实指标注册表**生成的完整active/core集合,
不得只构造SPX、UST_10Y等少量指标然后手动声明PASS——本模块写入覆盖全部32个
core指标的采集JSON,经真实snapshot_builder.build_snapshot构建快照(Gate A为
真实计算值),数据包/锚点/锚点prompt全部经真实确定性路径产出。

各测试套件(test_gate_chain_p01/test_p01_fix1/test_p01_fix2/test_e2e_orig14)
import本模块构造合法基线,再按场景需要做篡改/破坏。
"""
import json
import os
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
_SCRIPTS = os.path.join(os.path.dirname(_HERE), 'scripts')
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

import snapshot_builder as sb          # noqa: E402
import data_assembler as da            # noqa: E402
import data_validator as dv            # noqa: E402
import research_provenance as rp       # noqa: E402


def as_of_for(ymd):
    return f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}T08:00:00+08:00"


def obs_for(ymd, lag=1):
    """全球行情观测日: 目标日前一自然日(周六目标=周五收盘)。"""
    from datetime import datetime, timedelta
    d = datetime.strptime(ymd, '%Y%m%d') - timedelta(days=lag)
    return d.strftime('%Y-%m-%d')


def collector_payloads(ymd, obs, break_metric=None, missing=()):
    """全核心齐备的SYNTHETIC采集payload(32个core指标全部在场)。

    - break_metric: 指定指标值置'N/A'(→事实引擎type校验FAIL);
    - missing: 指定指标**整体不出现**(→核心缺失);
    返回{'global':..,'macro':..,'china':..,'rate_economy':..}。"""

    def _val(mid, v):
        if break_metric == mid:
            return 'N/A'
        return v

    def _skip(mid):
        return mid in missing

    def series(d):
        ds = sorted(d)
        return {"dates": ds, "values": [d[k] for k in ds]}

    glob = {"date": ymd, "time": "07:12:00", "count": 7, "data": {}}
    _G = [('SPX', '标普500', 7659.44, 7680.0, 7601.0),
          ('NDX', '纳斯达克100', 25631.5, 25700.0, 25400.0),
          ('VIX', 'VIX恐慌指数', 15.82, 16.4, 15.2),
          ('DXY', '美元指数', 103.21, 103.5, 102.9),
          ('GOLD', '黄金期货', 4300.0, None, None),
          ('WTI', 'WTI原油期货', 71.28, None, None),
          ('BTC', '比特币', 108000.0, None, None)]
    for mid, _n, v, hi, lo in _G:
        if _skip(mid):
            continue
        item = {"close": _val(mid, v), "date": obs,
                "series": series({pday(obs, 7): round(v * 0.985, 2), obs: v})}
        if hi is not None:
            item["high"] = hi
        if lo is not None:
            item["low"] = lo
        glob["data"][mid] = item

    dser_dates = [pday(obs, i) for i in (8, 7, 3, 2, 1, 0)]
    macro = {"date": ymd, "data": {}}
    _MD = [('CCC_OAS', 10.18, 'daily'), ('HY_OAS', 5.20, 'daily'),
           ('TIPS_10Y', 2.31, 'daily'), ('UST_2Y', 3.98, 'daily'),
           ('UST_10Y', 4.28, 'daily'), ('BEI_10Y', 1.97, 'daily'),
           ('FED_FUNDS', 4.33, 'daily')]
    for mid, v, freq in _MD:
        if _skip(mid):
            continue
        macro["data"][mid] = {"value": _val(mid, v), "date": obs, "frequency": freq,
                              "series": {"dates": dser_dates,
                                         "values": [round(v + 0.01 * (len(dser_dates) - i - 1), 3)
                                                    for i in range(len(dser_dates))]}}
    cpi_dates = ['2025-%02d-01' % m for m in range(1, 13)] \
        + ['2026-%02d-01' % m for m in range(1, int(ymd[4:6]))]
    cpi_vals = [300.0 + i * 0.8 for i in range(len(cpi_dates))]
    _MM = [('CPI', cpi_vals[-1] if cpi_vals else 300.0), ('CORE_CPI', 306.0),
           ('CORE_PCE', 118.5), ('UNEMPLOYMENT', 4.2), ('NFP', 160000.0),
           ('NFP_MOM_K', 160.0)]
    prev_m = '2026-%02d-01' % (int(ymd[4:6]) - 1) if int(ymd[4:6]) > 1 else '2025-12-01'
    for mid, v in _MM:
        if _skip(mid):
            continue
        item = {"value": _val(mid, v), "date": prev_m, "frequency": "monthly"}
        if mid == 'CPI':
            item["series"] = {"dates": cpi_dates, "values": cpi_vals}
        macro["data"][mid] = item
    if not _skip('ICSA'):
        macro["data"]["ICSA"] = {"value": _val('ICSA', 221000.0), "date": pday(obs, 1),
                                 "frequency": "weekly"}
    if not _skip('UMCSENT'):
        macro["data"]["UMCSENT"] = {"value": _val('UMCSENT', 68.0), "date": prev_m,
                                    "frequency": "monthly"}
    macro["derived"] = {}

    cn_dates = [month_end(prev_m), pday(obs, 7), pday(obs, 1), obs]

    def cnser(v):
        return {"dates": cn_dates, "values": v}

    china = {"date": ymd, "data": {}, "indices": {
        "上证指数": {"name": "上证指数", "close": _val('SHCOMP', 3716.28), "date": obs,
                    "series": cnser([3800.0, 3790.0, 3797.0, 3716.28])},
        "深证成指": {"name": "深证成指", "close": _val('SZCI', 12256.3), "date": obs,
                    "series": cnser([12400.0, 12380.0, 12350.0, 12256.3])},
        "恒生指数": {"name": "恒生指数", "close": _val('HSI', 24186.83), "date": obs,
                    "via": "tencent", "series": cnser([24400.0, 24380.0, 24350.0, 24186.83])},
        "恒生国企指数": {"name": "恒生国企指数", "close": _val('HSCEI', 8735.2), "date": obs,
                    "series": cnser([8800.0, 8790.0, 8770.0, 8735.2])},
    }, "ah_premium": {"close": _val('HSAHP', 128.56), "date": obs},
       "turnover": {"date": ymd, "sh_amount_billion": 8000.0, "sz_amount_billion": 9000.0,
                    "total_amount_billion": 17000.0}}

    rate = {"date": ymd, "current_rates": {
        "DFF": {"name": "有效联邦基金利率", "value": _val('DFF', 4.33), "date": obs},
        "DFEDTARU": {"name": "目标区间上限", "value": _val('DFEDTARU', 4.50), "date": obs},
        "DFEDTARL": {"name": "目标区间下限", "value": _val('DFEDTARL', 4.25), "date": obs}},
        "fed_funds_futures": [
            {"ticker": "ZQ=F", "name": "FF期货主力", "price": 95.80, "implied_rate": 4.20},
            {"ticker": "ZQZ26.CBT", "name": "2026-12", "price": 95.90, "implied_rate": 4.10}],
        "real_economy": {
            "UNRATE": {"name": "失业率", "value": 4.2, "date": prev_m, "freq": "月度"},
            "UMCSENT": {"name": "消费者信心", "value": 71.0, "date": prev_m, "freq": "月度"}}}
    return {"global": glob, "macro": macro, "china": china, "rate_economy": rate}


def pday(iso, n):
    from datetime import datetime, timedelta
    return (datetime.strptime(iso, '%Y-%m-%d') - timedelta(days=n)).strftime('%Y-%m-%d')


def month_end(ym):
    from datetime import datetime, timedelta
    d = datetime.strptime(ym, '%Y-%m-%d')
    nxt = (d.replace(day=28) + timedelta(days=4)).replace(day=1)
    return (nxt - timedelta(days=1)).strftime('%Y-%m-%d')


def write_collectors(daily_dir, ymd, break_metric=None, missing=()):
    obs = obs_for(ymd)
    os.makedirs(daily_dir, exist_ok=True)
    for name, obj in collector_payloads(ymd, obs, break_metric, missing).items():
        with open(os.path.join(daily_dir, f"{name}_{ymd}.json"), 'w',
                  encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False)


def write_scorecard(daily_dir, ymd, body=None):
    os.makedirs(daily_dir, exist_ok=True)
    p = os.path.join(daily_dir, f'scorecard_{ymd}.md')
    with open(p, 'w', encoding='utf-8') as f:
        f.write(body or f"# 宏观体制评分卡 {ymd}\n\n- 体制判定: 中性偏紧\n"
                       "- 关键信号: 利率高位+通胀降温\n")
    return p


def real_snapshot(ymd, gate='PASS', break_metric=None, missing=(), rev=None,
                  as_of=None):
    """真实构建的注册表齐备快照(dict)。

    gate='PASS' → 全核心有效; 'DEGRADED' → 非核心UMCSENT值坏(真实降级);
    'FAIL' → 核心SPX值坏; 也可用break_metric/missing显式指定破坏方式。
    rev: 给snapshot_id加_vN后缀(用于版本选择fixture;内部ID同步改写)。"""
    if break_metric is None:
        break_metric = {'DEGRADED': 'UMCSENT', 'FAIL': 'SPX'}.get(gate)
    with tempfile.TemporaryDirectory() as tdd:
        write_collectors(tdd, ymd, break_metric=break_metric, missing=missing)
        snap = sb.build_snapshot(target_ymd=ymd, data_dir=tdd, out_dir=tdd,
                                 as_of=as_of or as_of_for(ymd))
    if rev:
        snap['snapshot_id'] = f"research_snapshot_{ymd}_v{rev}"
        snap['revision_reason'] = 'fixture revision'
    return snap


def build_full_day(root, ymd, gate='PASS', break_metric=None, missing=(),
                   skip=(), scorecard=True, stale_scorecard_date=None):
    """构造一天完整研究产物(全部真实路径):

    root/data/daily/{research_snapshot_ymd.json, collectors, anchors+meta,
    anchor_prompt, scorecard} + root/data/weekly/data_pack_ymd.md+meta。
    返回(snap, snap_path, {'daily':..,'weekly':..,'pack':..,'anchors':..,
    'prompt':..,'scorecard':..})。skip: {'pack','pack_meta','anchors',
    'anchors_meta','prompt','scorecard'}。stale_scorecard_date: 写旧日期评分
    (构造"仅历史参考评分"场景)。"""
    data_root = os.path.join(root, 'data')
    daily = os.path.join(data_root, 'daily')
    weekly = os.path.join(data_root, 'weekly')
    os.makedirs(daily, exist_ok=True)
    os.makedirs(weekly, exist_ok=True)
    if break_metric is None:
        break_metric = {'DEGRADED': 'UMCSENT', 'FAIL': 'SPX'}.get(gate)
    write_collectors(daily, ymd, break_metric=break_metric, missing=missing)
    if 'scorecard' not in skip:
        write_scorecard(daily, stale_scorecard_date or ymd)
    snap = sb.build_snapshot(target_ymd=ymd, data_dir=daily, out_dir=daily,
                             as_of=as_of_for(ymd))
    snap_path = os.path.join(daily, snap['snapshot_id'] + '.json')

    paths = {'daily': daily, 'weekly': weekly, 'snapshot': snap_path}
    gate_now = snap['gate_a']['status']
    if 'pack' not in skip and gate_now != 'FAIL':
        packfile = os.path.join(weekly, f'data_pack_{ymd}.md')
        with open(packfile, 'w', encoding='utf-8') as f:
            f.write(da.build_markdown(snap, ymd, data_dir=data_root))
        if 'pack_meta' not in skip:
            sc_date, sc_current = da.scorecard_state(ymd, data_dir=data_root)
            rp.write_meta(packfile, {
                'source': 'snapshot', 'generated_by': 'data_assembler',
                'pack_file': os.path.basename(packfile),
                'pack_digest': rp.digest_file(packfile),
                'scorecard_date': sc_date,
                'scorecard_current': bool(sc_current),
                **rp.provenance_of(snap, snap_path)})
        paths['pack'] = packfile
    if 'pack' not in skip and gate_now == 'FAIL':
        # Gate A FAIL日装配器不会运行——只留一个无效残留包(预检须拒绝)
        packfile = os.path.join(weekly, f'data_pack_{ymd}.md')
        with open(packfile, 'w', encoding='utf-8') as f:
            f.write('# stale pack\n')
        paths['pack'] = packfile
    anchors_path = os.path.join(daily, f'anchors_{ymd}.json')
    if 'anchors' in skip and os.path.exists(anchors_path):
        os.remove(anchors_path)
        if os.path.exists(rp.meta_path_for(anchors_path)):
            os.remove(rp.meta_path_for(anchors_path))
    paths['anchors'] = anchors_path
    if 'prompt' not in skip:
        with open(snap_path, 'r', encoding='utf-8') as f:
            real_snap = json.load(f)
        anchors = sb.build_anchors(real_snap, ymd)
        ppath = os.path.join(daily, f'anchor_prompt_{ymd}.md')
        with open(ppath, 'w', encoding='utf-8') as f:
            f.write(dv.generate_anchor_prompt_block(anchors))
        paths['prompt'] = ppath
    return snap, snap_path, paths
