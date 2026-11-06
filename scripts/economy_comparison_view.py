#!/usr/bin/env python3
"""跨经济体比较视图(IA-P1-WP-F = P1 收口链 #19;P1_DESIGN §六 L174 + §八.1)

独立比较视图模块(DP-F1 定值=形态②: 消费快照+评分卡档,不改数据包/报告模板
——US 面零回归触面最小)。**纯消费面**: 零新数据源、零新采集通道、不重做底图;
数据入口=研究快照(rp.select_snapshot 确定性版本选择)+评分卡存档
(data_assembler.economy_scorecard 上游 helper),零直读采集档
(P1_DESIGN §四 L130 禁直读约束对 jp_/ea_ 档同样生效)。

并置口径(DP-F2 定值=形态②): 增长/通胀总分+制度(regime)+数据状态
(渲染式样沿 data_assembler「经济体观察」节 L277-L301)+关键事实行
(政策利率/通胀同比,metric 映射=REPORT §零.6 登记值)。
跨域对呈现(DP-F3 定值=形态①): 零新增——仅呈现 correlation_calculator.PAIRS
既有两跨域对(NIKKEI225×USDJPY / DAX×EURUSD),复用 compute_all 计算,零扩容。

缺席纪律(P1_DESIGN §七 L184 五层一致): 评分卡档缺席→「未生成」行在场(禁跳过
整行);维度总分非 int→「数据不足」;关键事实缺席→「无数据」;快照缺席→事实/
跨域节整体「无数据」——一律禁 0 占位、禁以离岸代理冒充在岸口径。
DISCLAIMER 沿用 macro_scorecard L32-L33 口径(内部模型观点非客观事实),
本视图不构成投资建议;相关性=描述统计非因果。

零网络: import 面纯标准库+项目既有模块,零真实调用/凭证/付费/出站。
"""
import argparse
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import research_provenance as rp
from correlation_calculator import PAIRS, compute_all
from data_assembler import economy_scorecard
from macro_scorecard import DATA_INSUFFICIENT, DISCLAIMER, ECONOMY_NAMES, fact_of
from research_history_query import query_window

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── 登记参数(REPORT §零.5/§零.6;先登记后运行,运行后禁回改) ──────────
COMPARISON_ECONOMIES = ('US', 'CN', 'JP', 'EA')   # DESIGN L194(INVENTORY a.1 DP-1)
KEY_FACTS = {                                       # registry 实取 v2.3.0/102 条目
    'US': {'policy_rate': 'DFEDTARL', 'inflation_yoy': 'CPI',
           'inflation_field': 'derived_m12_pct'},   # CPI=指数级→同比=derived.m12.pct_change
    'CN': {'policy_rate': 'CN_LPR_1Y', 'inflation_yoy': 'CN_CPI_YOY',
           'inflation_field': 'value'},
    'JP': {'policy_rate': 'JP_POLICY_RATE', 'inflation_yoy': 'JP_CPI_TOKYO_YOY',
           'inflation_field': 'value'},
    'EA': {'policy_rate': 'ECB_DFR', 'inflation_yoy': 'EA_HICP_YOY',
           'inflation_field': 'value'},
}
CROSS_DOMAIN_PAIRS = (('NIKKEI225', 'USDJPY'), ('DAX', 'EURUSD'))  # PAIRS L49/L51(DP-F3①)
# ─────────────────────────────────────────────────────────────────────

NO_DATA = '无数据'
INSUFFICIENT_CELL = '数据不足'        # data_assembler L295-L296 单元格式样
NOT_GENERATED = '未生成'              # data_assembler L291-L292 式样
# 状态名映射: 值=data_assembler L286-L287 _st_names 同值(上游为函数内局部量
# 不可 import,逐字对齐登记,REPORT §零.6)
_REGIME_STATUS_NAMES = {'confirmed': '已确认', 'pending_confirmation': '待确认',
                        'data_insufficient': '数据不足'}
# 跨域对 label 集: 自上游 PAIRS 数据驱动推导(禁硬编码标签文案转写,R061 纪律)
_CROSS_WANTED = {frozenset(p) for p in CROSS_DOMAIN_PAIRS}
_CROSS_LABELS = {p['label'] for p in PAIRS if frozenset((p['a'], p['b'])) in _CROSS_WANTED}


def load_snapshot_for_view(ymd, data_dir=None):
    """快照选择(消费面版): 复用 rp.select_snapshot 确定性版本选择。
    与 macro_scorecard.load_snapshot(L46)的差异=缺席行为: 评分主流程缺快照
    sys.exit(1) 中断,本消费面按比较纪律如实呈现(None→「无数据」节),
    直接取 (None, reason) 分支(登记参数,REPORT §零.6)。"""
    d = data_dir or os.path.join(ROOT_DIR, 'data')
    return rp.select_snapshot(ymd, os.path.join(d, 'daily'))


def _fmt_total(total):
    """总分单元格: int→带符号整数(data_assembler L295-L296 同式);非 int
    (None=无评分,非 0 分)→「数据不足」。"""
    return f"{total:+d}" if isinstance(total, int) else INSUFFICIENT_CELL


def _num(v):
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def key_fact(facts, economy):
    """某经济体关键事实行(DP-F2②): 政策利率+通胀同比,取值口径=REPORT §零.6
    登记映射。缺席→available=False+原因(禁 0 占位);数值必携 metric_id+
    观测日接地标识(P1_DESIGN §四 L134 接地规则)。"""
    spec = KEY_FACTS[economy]
    out = {}
    pr = fact_of(facts, spec['policy_rate'])
    pv = _num((pr or {}).get('value'))
    out['policy_rate'] = {
        'metric_id': spec['policy_rate'],
        'available': pv is not None,
        'value': pv,
        'observation_date': (pr or {}).get('observation_date'),
        'absence_reason': None if pv is not None else f"快照无{spec['policy_rate']}有效事实",
    }
    inf = fact_of(facts, spec['inflation_yoy'])
    if spec['inflation_field'] == 'derived_m12_pct':
        d12 = ((inf or {}).get('derived') or {}).get('m12') or {}
        iv = _num(d12.get('pct_change')) if d12.get('available') is not False else None
        reason = None if iv is not None else f"引擎无{spec['inflation_yoy']} m12 pct 派生"
    else:
        iv = _num((inf or {}).get('value'))
        reason = None if iv is not None else f"快照无{spec['inflation_yoy']}有效事实"
    out['inflation_yoy'] = {
        'metric_id': spec['inflation_yoy'],
        'available': iv is not None,
        'value': iv,
        'observation_date': (inf or {}).get('observation_date'),
        'absence_reason': reason,
    }
    return out


def economy_row(economy, ymd, data_dir, facts):
    """单经济体比较行: 评分卡状态(上游 economy_scorecard helper,缺失返回
    None→如实「未生成」行在场,禁跳行)+关键事实(快照事实,独立于评分卡)。"""
    sc = economy_scorecard(economy, ymd, data_dir)
    if sc is None:
        card = {'present': False,
                'growth_total': None, 'inflation_total': None,
                'regime': None, 'regime_status': None,
                'growth_cell': NOT_GENERATED, 'inflation_cell': NOT_GENERATED,
                'regime_cell': NOT_GENERATED,
                'status_cell': f"{NOT_GENERATED}(当日评分卡不存在)"}
    else:
        gt, it = sc.get('growth_total'), sc.get('inflation_total')
        r_cell = sc.get('confirmed_regime') or sc.get('regime') or '—'   # L297 同式
        st = sc.get('regime_status')
        card = {'present': True,
                'growth_total': gt, 'inflation_total': it,
                'regime': sc.get('regime'), 'regime_status': st,
                'growth_cell': _fmt_total(gt), 'inflation_cell': _fmt_total(it),
                'regime_cell': r_cell,
                'status_cell': (f"本期在场;{_REGIME_STATUS_NAMES.get(st, str(st))}")}
    return {'economy': economy, 'name': ECONOMY_NAMES[economy],
            'scorecard': card, 'key_facts': key_fact(facts, economy)}


def cross_domain_pairs_view(snapshot):
    """比较事实面·跨域对(DP-F3①零新增): 复用 compute_all 全量计算后按登记
    两元组过滤呈现——PAIRS 零扩容,序列零改写;快照缺席→整体「无数据」。"""
    if not snapshot:
        return [], [f"快照缺席: 跨域对呈现整体{NO_DATA}(比较视图不代行快照构建)"]
    results, missing = compute_all(snapshot)
    kept = [r for r in results if frozenset((r['a'], r['b'])) in _CROSS_WANTED]
    miss_kept = [m for m in missing if any(m.startswith(lbl) for lbl in _CROSS_LABELS)]
    return kept, miss_kept


def comparison_query(payloads, start, end, lookback=0, economies=None):
    """查询比较面(范围3,DESIGN L199): economy 过滤维度的比较型查询
    (W-1/W-2 型)。payloads={economy: payload}(payload 形态=load_metric_series
    输出,research_history_query L139-L169 含 economy 字段);逐经济体调上游
    query_window(L184)——过滤不命中=上游如实空窗语义(L194-L201),零新逻辑;
    payload 缺席→「无数据」空窗(不造点)。"""
    out = {}
    for econ in (economies or COMPARISON_ECONOMIES):
        payload = (payloads or {}).get(econ)
        if payload is None:
            out[econ] = {'dates': [], 'values': [],
                         'coverage': {'note': f'{NO_DATA}(该经济体无查询payload)'}}
            continue
        out[econ] = query_window(payload, start, end, lookback=lookback, economy=econ)
    return out


def build_comparison_view(ymd, data_dir=None):
    """装配比较视图(纯消费面): 快照(事实+series_store)+四经济体评分卡存档
    +跨域对呈现→结构化 dict。开档面仅三族: scorecard_*/economy_scorecard_*/
    research_snapshot_*(REPORT §零.6 白名单三族,零采集档 glob)。"""
    snap, path_or_reason = load_snapshot_for_view(ymd, data_dir)
    facts = (snap or {}).get('facts') or []
    rows = [economy_row(e, ymd, data_dir, facts) for e in COMPARISON_ECONOMIES]
    pairs, pairs_missing = cross_domain_pairs_view(snap)
    return {
        'view_id': f'comparison_view_{ymd}',
        'date': ymd,
        'generated_at': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'disclaimer': DISCLAIMER,
        'data_basis': {
            'snapshot_available': snap is not None,
            'snapshot_id': (snap or {}).get('snapshot_id'),
            'snapshot_path_or_reason': None if snap is not None else path_or_reason,
        },
        'economies': rows,
        'cross_domain_pairs': pairs,
        'cross_domain_missing': pairs_missing,
        'source_scope': ('纯快照/事实/评分卡档消费,零直读采集档'
                         '(P1_DESIGN §四 L130 禁直读约束对 jp_/ea_ 档同样生效)'),
        'pair_policy': '跨域对零新增(DP-F3①): 仅呈现 PAIRS 既有两跨域对,描述统计非因果',
    }


def _kf_cell(kf, signed=True):
    """关键事实单元格: 数值+接地标识(metric@观测日);缺席→「无数据」+原因。
    政策利率=水平值(无符号 .2f%),通胀同比=变化(+.2f%)——口径=REPORT §零.6。"""
    if kf['available']:
        num = f"{kf['value']:+.2f}" if signed else f"{kf['value']:.2f}"
        anchor = kf['observation_date'] if kf['observation_date'] else '观测日缺席'
        return f"{num}%({kf['metric_id']}@{anchor})"
    return f"{NO_DATA}({kf['absence_reason']})"


def render_comparison_markdown(view):
    """渲染比较视图 Markdown: 主表式样沿 data_assembler「经济体观察」节
    (L277-L301 表头式样)扩展关键事实行;DISCLAIMER 口径逐字沿用(L32-L33)。"""
    L = [f"# 跨经济体比较视图({view['view_id']})",
         "",
         f"> {view['disclaimer']}",
         "> 本视图不构成投资建议;相关性为描述统计,非因果结论。",
         f"> {view['source_scope']};快照={view['data_basis']['snapshot_id'] or '缺席'}。",
         "",
         "## 经济体并置比较",
         "",
         "| 经济体 | 增长 | 通胀 | 制度 | 数据状态 |",
         "|---|---|---|---|---|"]
    for row in view['economies']:
        c = row['scorecard']
        L.append(f"| {row['name']}({row['economy']}) | {c['growth_cell']} | "
                 f"{c['inflation_cell']} | {c['regime_cell']} | {c['status_cell']} |")
    L.append("")
    L.append("## 关键事实行(政策利率/通胀同比;数值携 metric@观测日接地标识)")
    L.append("")
    L.append("| 经济体 | 政策利率 | 通胀同比 |")
    L.append("|---|---|---|")
    for row in view['economies']:
        kf = row['key_facts']
        L.append(f"| {row['name']}({row['economy']}) | "
                 f"{_kf_cell(kf['policy_rate'], signed=False)} | "
                 f"{_kf_cell(kf['inflation_yoy'], signed=True)} |")
    L.append("")
    L.append("## 跨域对呈现(既有两对,零新增;描述统计非因果)")
    L.append("")
    if view['cross_domain_pairs']:
        L.append("| 配对 | corr(20d) | n(20d) | corr(60d) | n(60d) | 窗口 |")
        L.append("|---|---|---|---|---|---|")
        for p in view['cross_domain_pairs']:
            c20 = '—' if p.get('corr_20d') is None else f"{p['corr_20d']:+.4f}"
            c60 = '—' if p.get('corr_60d') is None else f"{p['corr_60d']:+.4f}"
            L.append(f"| {p['label']} | {c20} | {p.get('n_20d')} | {c60} | "
                     f"{p.get('n_60d')} | {p.get('window_first')}~{p.get('window_last')} |")
        for p in view['cross_domain_pairs']:
            if p.get('disclosure'):
                L.append(f"- 披露: {p['disclosure']}")
    else:
        L.append(f"({NO_DATA}: 无跨域对结果)")
    for m in view['cross_domain_missing']:
        L.append(f"- 缺席披露: {m}")
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description='跨经济体比较视图(IA-P1-WP-F #19;纯消费面)')
    ap.add_argument('--ymd', default=datetime.now().strftime('%Y%m%d'), help='观察日 YYYYMMDD')
    ap.add_argument('--data-dir', default=None, help='数据根(含 daily/ 子目录;缺省=仓库 data/)')
    ap.add_argument('--out', default=None, help='输出 Markdown 路径(缺省=data/research/comparison_view_{ymd}.md)')
    args = ap.parse_args(argv)
    view = build_comparison_view(args.ymd, args.data_dir)
    md = render_comparison_markdown(view)
    out = args.out or os.path.join(ROOT_DIR, 'data', 'research',
                                   f'comparison_view_{args.ymd}.md')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(md)
    print(f"💾 比较视图已保存: {out}")
    print(f"📌 数据基础: 快照={view['data_basis']['snapshot_id'] or '缺席'};"
          f"经济体行={len(view['economies'])};跨域对={len(view['cross_domain_pairs'])}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
