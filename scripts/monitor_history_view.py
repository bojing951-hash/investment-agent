#!/usr/bin/env python3
"""监测回溯查询面(IA-P1-WP-G = P1 收口链 #20;P1_DESIGN §六 L175 + §八.2 范围4)

三张消费面的只读回溯视图:
- 逐经济体窗口回溯(范围4 L233): research_history_query economy 过滤
  (query_window L184-L201)作为监测回溯消费面——payload 自快照 series_store
  装配({metric_id,dates,values,economy},economy=registry 实取),逐经济体
  调上游 query_window 直用;过滤不命中/窗口无观测=上游如实空窗语义,零新逻辑;
- RT- 任务列示: data/research/ 只读扫描(RT-*.json 含 __v{N} 版本档,读
  economy/status/task_id/created_at;零改写——研究状态保护不绕开,本模块
  唯一写面=CLI 输出 Markdown 档(缺省 data/research/monitor_history_{ymd}.md));
- #19 前件消费(依赖 L240): economy_comparison_view.economy_row 评分卡
  在场状态,复用不复制(WP-F 已交付件,层内收口链序 #19→#20)。

回溯窗=DP-G1=② 14 日(冻结章§四;--start/--end 缺省=[ymd−13, ymd] 自然日
两端转 ISO)。缺席纪律: 无快照→窗口面整体如实缺席;指标不在 registry→
economy=None→上游过滤不命中如实空窗;任务档损坏→如实 corrupt 行,禁静默跳过。
监测输出=链路健康描述,非投资建议(MONITOR_DISCLAIMER 登记)。
零网络: import 面纯标准库+项目既有模块。
"""
import argparse
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import research_provenance as rp
import research_history_query as rhq
import economy_comparison_view as ecv
from economy_anomaly_rules import MONITOR_DISCLAIMER
from routine_health_monitor import window_days

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HISTORY_LOOKBACK_DAYS = 14   # DP-G1=②(=routine_health_monitor.HEALTH_LOOKBACK_DAYS 同值)


def default_window(ymd, lookback=HISTORY_LOOKBACK_DAYS):
    """缺省回溯窗: window_days 首末自然日转 ISO([ymd−13, ymd] 含端点)。"""
    days = window_days(ymd, lookback)
    return f"{days[0][:4]}-{days[0][4:6]}-{days[0][6:]}", \
           f"{days[-1][:4]}-{days[-1][4:6]}-{days[-1][6:]}"


def build_payloads(series_store, registry_metrics=None):
    """自快照 series_store 装配 query payload(纯快照消费,零采集档直读)。

    economy=registry 实取(metric_id→economy);指标不在 registry→economy=None
    (上游过滤不命中如实空窗,如实保留不删行)。registry_metrics 可注入合成
    条目(测试 hermetic;缺省=fe.load_registry() 实读)。
    """
    if registry_metrics is None:
        import fact_engine as fe
        registry_metrics = fe.load_registry()['metrics']
    econ_of = {m.get('metric_id'): m.get('economy') for m in registry_metrics}
    out = {}
    for mid, seq in (series_store or {}).items():
        out[mid] = {'metric_id': mid,
                    'dates': [str(d)[:10] for d in seq.get('dates') or []],
                    'values': list(seq.get('values') or []),
                    'economy': econ_of.get(mid)}
    return out


def retrospective_windows(payloads, start, end, economies=None):
    """逐经济体窗口回溯(范围4): 逐指标调上游 rhq.query_window 直用
    (economy 过滤维度),指标 economy 与请求不等=上游如实空窗(L194-L201),
    零新过滤逻辑。返回 {economy: {metric_id: query_window 输出}}。"""
    out = {}
    for econ in (economies or rhq.ECONOMIES):
        rows = {}
        for mid in sorted(payloads):
            w = dict(rhq.query_window(payloads[mid], start, end, economy=econ))
            w['metric_economy'] = payloads[mid].get('economy')
            rows[mid] = w
        out[econ] = rows
    return out


def list_monitor_tasks(research_dir=None):
    """RT- 任务列示(data/research/ 只读扫描;零改写)。含 __v{N} 版本档;
    损坏档→corrupt 行如实,禁静默跳过。返回 (tasks, note)。"""
    rd = research_dir or os.path.join(ROOT_DIR, 'data', 'research')
    if not os.path.isdir(rd):
        return [], f'研究档案目录缺席: {rd}(如实零任务列示)'
    tasks = []
    for name in sorted(n for n in os.listdir(rd)
                       if n.startswith('RT-') and n.endswith('.json')):
        p = os.path.join(rd, name)
        try:
            with open(p, 'r', encoding='utf-8') as f:
                t = json.load(f)
            tasks.append({'file': name, 'task_id': t.get('task_id'),
                          'economy': t.get('economy'), 'status': t.get('status'),
                          'created_at': t.get('created_at')})
        except (OSError, ValueError) as e:
            tasks.append({'file': name, 'corrupt': True,
                          'corrupt_reason': f'{type(e).__name__}: {e}'})
    return tasks, None


def comparison_status(ymd, data_dir=None, facts=None, economies=None):
    """#19 前件消费(依赖 L240): ecv.economy_row 评分卡在场状态,复用不复制。
    快照缺席→facts=[]→上游行内「未生成/无数据」如实语义,不代行评分。"""
    rows = []
    for econ in (economies or ecv.COMPARISON_ECONOMIES):
        r = ecv.economy_row(econ, ymd, data_dir, facts or [])
        rows.append({'economy': econ, 'name': r['name'],
                     'scorecard_present': r['scorecard']['present'],
                     'status_cell': r['scorecard']['status_cell'],
                     'growth_cell': r['scorecard']['growth_cell'],
                     'inflation_cell': r['scorecard']['inflation_cell']})
    return rows


def build_history_view(ymd, start=None, end=None, data_dir=None,
                       research_dir=None, economies=None, snapshot=None,
                       snapshot_why=None, registry_metrics=None):
    """装配监测回溯视图(纯消费面;开档面仅 research_snapshot_*(经 rp.select_snapshot
    规范选择)+data/research/ RT- 档(只读)+评分卡存档(经 ecv.economy_row 上游
    helper)——零采集档直读)。snapshot/snapshot_why 可注入(测试 hermetic 面);
    缺省=rp.select_snapshot 实选。"""
    if start is None or end is None:
        d_start, d_end = default_window(ymd)
        start = start or d_start
        end = end or d_end
    if snapshot is None:
        daily = os.path.join(data_dir or os.path.join(ROOT_DIR, 'data'), 'daily')
        snapshot, snapshot_why = rp.select_snapshot(ymd, daily)
    store = (snapshot or {}).get('series_store') or {}
    payloads = build_payloads(store, registry_metrics)
    windows = retrospective_windows(payloads, start, end, economies)
    tasks, task_note = list_monitor_tasks(research_dir)
    comparison = comparison_status(ymd, data_dir,
                                   facts=(snapshot or {}).get('facts') or [])
    return {
        'view_id': f'monitor_history_{ymd}',
        'date': ymd,
        'generated_at': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'disclaimer': MONITOR_DISCLAIMER,
        'window': {'start': start, 'end': end,
                   'lookback_days': HISTORY_LOOKBACK_DAYS},
        'data_basis': {'snapshot_available': snapshot is not None,
                       'snapshot_id': (snapshot or {}).get('snapshot_id'),
                       'snapshot_path_or_reason': str(snapshot_why) if snapshot is None
                       else os.path.basename(str(snapshot_why))},
        'windows': windows,
        'monitor_tasks': {'tasks': tasks, 'note': task_note,
                          'n_tasks': len(tasks),
                          'n_by_status': _count_by(tasks, 'status'),
                          'n_by_economy': _count_by(tasks, 'economy')},
        'comparison_status': comparison,
        'source_scope': ('快照 series_store+RT- 档只读扫描+评分卡存档消费'
                         '(经 rp.select_snapshot/rhq.query_window/ecv.economy_row'
                         ' 登记接入点),零直读采集档,零研究状态改写'),
    }


def _count_by(rows, key):
    out = {}
    for r in rows:
        if r.get('corrupt'):
            k = '(corrupt)'
        else:
            k = r.get(key)
        out[k] = out.get(k, 0) + 1
    return out


def render_history_markdown(view):
    """渲染回溯视图 Markdown(缺席如实,禁0填充;空窗语义=上游 coverage.note)。"""
    L = [f"# 监测回溯查询视图({view['view_id']})",
         "",
         f"> {view['disclaimer']}",
         f"> 回溯窗={view['window']['lookback_days']} 日(DP-G1=②): "
         f"{view['window']['start']}~{view['window']['end']}。",
         f"> {view['source_scope']}。",
         "",
         f"- 快照={view['data_basis']['snapshot_id'] or '缺席'}"
         f"({'在场' if view['data_basis']['snapshot_available'] else view['data_basis']['snapshot_path_or_reason']})。",
         "",
         "## 逐经济体窗口回溯(economy 过滤=rhq.query_window 直用)", ""]
    if not view['data_basis']['snapshot_available']:
        L.append(f"(快照缺席: 窗口回溯面整体如实空,不代行快照构建——"
                 f"{view['data_basis']['snapshot_path_or_reason']})")
        L.append("")
    for econ, rows in view['windows'].items():
        L.append(f"### {econ}")
        L.append("")
        L.append("| 指标 | registry economy | 窗内观测 | 窗首 | 窗末 | 说明 |")
        L.append("|---|---|---|---|---|---|")
        for mid, w in sorted(rows.items()):
            cov = w.get('coverage') or {}
            note = cov.get('note')
            L.append(f"| {mid} | {w.get('metric_economy')} "
                     f"| {cov.get('n_window', 0)} | {cov.get('window_first') or '—'} "
                     f"| {cov.get('window_last') or '—'} | {note or '—'} |")
        L.append("")
    mt = view['monitor_tasks']
    L += ["## RT- 研究任务列示(只读扫描,零改写)", "",
          f"- 档案 {mt['n_tasks']} 件;按状态 {_json_cn(mt['n_by_status'])};"
          f"按经济体 {_json_cn(mt['n_by_economy'])}。"
          + (f"({mt['note']})" if mt.get('note') else ''), ""]
    if mt['tasks']:
        L.append("| 档 | task_id | economy | status | created_at |")
        L.append("|---|---|---|---|---|")
        for t in mt['tasks']:
            if t.get('corrupt'):
                L.append(f"| {t['file']} | (corrupt) | — | — | {t['corrupt_reason']} |")
            else:
                L.append(f"| {t['file']} | {t.get('task_id')} | {t.get('economy') or '—'} "
                         f"| {t.get('status')} | {t.get('created_at')} |")
        L.append("")
    L += ["## #19 前件消费: 评分卡在场状态(ecv.economy_row 复用不复制)", "",
          "| 经济体 | 评分卡 | 数据状态 |", "|---|---|---|"]
    for c in view['comparison_status']:
        L.append(f"| {c['name']}({c['economy']}) | "
                 f"{'在场' if c['scorecard_present'] else '未生成'} | {c['status_cell']} |")
    return "\n".join(L) + "\n"


def _json_cn(d):
    return json.dumps(d or {}, ensure_ascii=False, sort_keys=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description='监测回溯查询面(IA-P1-WP-G #20;只读消费面)')
    ap.add_argument('--ymd', default=datetime.now().strftime('%Y%m%d'), help='观察日 YYYYMMDD')
    ap.add_argument('--start', default=None, help='回溯窗起点 YYYY-MM-DD(缺省=ymd−13)')
    ap.add_argument('--end', default=None, help='回溯窗终点 YYYY-MM-DD(缺省=ymd)')
    ap.add_argument('--economies', default=None,
                    help=f'逗号分隔经济体子集(取值域 {",".join(rhq.ECONOMIES)};缺省=全值域)')
    ap.add_argument('--data-dir', default=None, help='数据根(含 daily/ 子目录;缺省=仓库 data/)')
    ap.add_argument('--research-dir', default=None, help='研究档案目录(缺省=仓库 data/research/)')
    ap.add_argument('--out', default=None, help='输出 Markdown 路径(缺省=data/research/monitor_history_{ymd}.md)')
    args = ap.parse_args(argv)
    economies = None
    if args.economies:
        req = [e.strip() for e in args.economies.split(',') if e.strip()]
        bad = [e for e in req if e not in rhq.ECONOMIES]
        if bad:
            ap.error(f'economies 越界: {bad}(取值域 {list(rhq.ECONOMIES)})')
        economies = req
    view = build_history_view(args.ymd, start=args.start, end=args.end,
                              data_dir=args.data_dir, research_dir=args.research_dir,
                              economies=economies)
    md = render_history_markdown(view)
    out = args.out or os.path.join(ROOT_DIR, 'data', 'research',
                                   f'monitor_history_{args.ymd}.md')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(md)
    n_active = view['monitor_tasks']['n_by_status'].get('active', 0)
    n_pending = view['monitor_tasks']['n_by_status'].get('pending', 0)
    print(f"💾 监测回溯视图已保存: {out}")
    print(f"📌 窗口={view['window']['start']}~{view['window']['end']};"
          f"经济体={len(view['windows'])};快照="
          f"{'在场' if view['data_basis']['snapshot_available'] else '缺席'};"
          f"RT-档={view['monitor_tasks']['n_tasks']}(active={n_active},pending={n_pending});"
          f"评分卡在场="
          f"{sum(1 for c in view['comparison_status'] if c['scorecard_present'])}"
          f"/{len(view['comparison_status'])}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
