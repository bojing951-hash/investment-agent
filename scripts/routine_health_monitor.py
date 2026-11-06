#!/usr/bin/env python3
"""链路健康常态监测面(IA-P1-WP-G = P1 收口链 #20;P1_DESIGN §六 L175 + §八.2 范围1)

既有 13 步流水线台账(run_weekly.py L217-L238 → logs/pipeline_run_{ymd}.json)
与快照 sources_status/Gate A(snapshot_builder.py L282-L301/L382-L390,经
research_provenance.select_snapshot 确定性版本选择)之上的常态健康视图:
逐通道断点/MISSING 回溯(DP-G3 层2)+新鲜度越限列示(DP-G3 层1)+台账步骤
失败/跳过回溯(DP-G1=14 日窗)。

纯消费面(要点①): 台账+快照+事实层消费,零直读 data/daily/ 采集档、零新数据
通道、零网络;缺席纪律(要点②): 无台账/无快照/事实缺席/序列缺席→如实行在场
(禁0填充禁静默),通道语义与 Gate A DEGRADED/MISSING 一致(消费裁决不改判)。
新鲜度分层口径(DP-G3=②,REPORT §零.5 登记): 非日频 registry 指标逐条对照
其 freshness.max_calendar_lag_days(月频 CPI 族=60[实取·registry v2.3.0]);
日频通道=快照 sources_status MISSING 连续回溯(无快照日=断链如实断开)。
监测输出=链路健康描述,非投资建议(MONITOR_DISCLAIMER 登记)。
"""
import argparse
import json
import os
import sys
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import research_provenance as rp
from economy_anomaly_rules import MONITOR_DISCLAIMER

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── 登记参数(REPORT §零.5;先登记后运行,运行后禁回改) ──────────────────
HEALTH_LOOKBACK_DAYS = 14      # DP-G1=②(冻结章§四);窗口=[ymd−13, ymd] 含端点


def _shift_ymd(ymd, days):
    d = date(int(ymd[:4]), int(ymd[4:6]), int(ymd[6:])) + timedelta(days=days)
    return d.strftime('%Y%m%d')


def window_days(ymd, lookback=HEALTH_LOOKBACK_DAYS):
    """回溯窗日期序列(升序;含端点 lookback 自然日)。"""
    return [_shift_ymd(ymd, -i) for i in range(lookback - 1, -1, -1)]


def _daily_dir(data_dir):
    d = data_dir or os.path.join(ROOT_DIR, 'data')
    return os.path.join(d, 'daily')


def _registry_metrics(registry_metrics=None):
    """registry 非日频指标条目(惰性实读;可注入合成条目——测试 hermetic 面)。"""
    if registry_metrics is not None:
        return registry_metrics
    import fact_engine as fe
    return fe.load_registry()['metrics']


def read_ledger(day, logs_dir):
    """单日台账消费(只读)。缺席→None(如实,不视为成功)。"""
    p = os.path.join(logs_dir, f'pipeline_run_{day}.json')
    if not os.path.isfile(p):
        return None
    try:
        with open(p, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return {'corrupt': True}


def _ledger_summary(led):
    """台账摘要: 关键失败/跳过/放行标志(消费 run_weekly L217-L238 写档形态)。"""
    if led is None:
        return {'present': False, 'note': '当日无流水线台账(如实缺席,不视为成功)'}
    if led.get('corrupt'):
        return {'present': False, 'note': '台账损坏不可解析(如实缺席)'}
    steps = led.get('steps') or []
    critical_failed = [s['name'] for s in steps if not s.get('ok') and s.get('critical')]
    skipped = {s['name']: s.get('skip_reason') for s in steps if s.get('skipped')}
    return {'present': True, 'run_at': led.get('run_at'),
            'n_steps': len(steps), 'success_count': led.get('success_count'),
            'critical_failed': critical_failed, 'skipped': skipped,
            'allow_formal_report': led.get('allow_formal_report'),
            'allow_state_writeback': led.get('allow_state_writeback'),
            'snapshot_id': led.get('snapshot_id'),
            'gate_a': led.get('gate_a')}


def _snapshot_summary(day, daily_dir):
    """单日快照消费(经 rp.select_snapshot 确定性版本选择;缺席如实)。"""
    snap, why = rp.select_snapshot(day, daily_dir)
    if snap is None:
        return {'present': False, 'note': str(why)}
    st = {ch: (v or {}).get('status') for ch, v in (snap.get('sources_status') or {}).items()}
    return {'present': True, 'snapshot_id': snap.get('snapshot_id'),
            'file': os.path.basename(why), 'gate_a': (snap.get('gate_a') or {}).get('status'),
            'sources_status': st, '_snapshot': snap}


def _channel_view(days, day_snaps):
    """逐通道断点/MISSING 回溯(DP-G3 层2): streak=自窗口内最近快照日(anchor)
    在场日起向回逐日计数 status=='MISSING' 的连续快照日数;无快照日=断链
    (计数如实断开,不脑补——不跨无快照日继续累加)。"""
    channels = sorted({ch for s in day_snaps.values()
                       if s.get('present') for ch in s.get('sources_status', {})})
    snap_days_desc = [d for d in reversed(days) if day_snaps[d].get('present')]
    anchor = snap_days_desc[0] if snap_days_desc else None
    days_desc = list(reversed(days))
    view = {}
    for ch in channels:
        streak, first_status, first_day = 0, None, None
        if anchor is not None:
            first_status = day_snaps[anchor]['sources_status'].get(ch)
            first_day = anchor
            if first_status == 'MISSING':
                streak = 1
                past_anchor = False
                for d in days_desc:
                    if d == anchor:
                        past_anchor = True
                        continue
                    if not past_anchor:
                        continue
                    if not day_snaps[d].get('present'):
                        break                       # 无快照日=断链(不脑补)
                    if day_snaps[d]['sources_status'].get(ch) == 'MISSING':
                        streak += 1
                    else:
                        break
        view[ch] = {'current_status': first_status, 'current_day': anchor,
                    'missing_streak_days': streak,
                    'history': [(d, day_snaps[d]['sources_status'].get(ch))
                                for d in days if day_snaps[d].get('present')]}
    return view, anchor


def _freshness_view(anchor_day, day_snaps, registry_metrics):
    """新鲜度越限列示(DP-G3 层1): 非日频 registry 指标逐条对照
    freshness.max_calendar_lag_days;lag=(target−observation_date) 自然日差
    严格大于窗→越限;事实缺席→缺席行如实列示(不填0)。"""
    out = {'anchor_day': anchor_day, 'checked': 0, 'violations': [], 'absences': []}
    if anchor_day is None:
        out['note'] = '窗内无在场快照,新鲜度面整体如实缺席(不造检查)'
        return out
    facts = {f.get('metric_id'): f for f in day_snaps[anchor_day]['_snapshot'].get('facts') or []}
    target = date(int(anchor_day[:4]), int(anchor_day[4:6]), int(anchor_day[6:]))
    for m in registry_metrics:
        if m.get('frequency') == 'daily':
            continue
        mid = m.get('metric_id')
        window = ((m.get('freshness') or {}).get('max_calendar_lag_days'))
        row = {'metric_id': mid, 'economy': m.get('economy'),
               'frequency': m.get('frequency'), 'window_days': window}
        out['checked'] += 1
        fact = facts.get(mid)
        obs = (fact or {}).get('observation_date')
        if obs is None:
            row['absent_reason'] = f'快照事实缺席: {mid}(如实缺席,不填0)'
            out['absences'].append(row)
            continue
        try:
            lag = (target - date.fromisoformat(str(obs)[:10])).days
        except ValueError:
            row['absent_reason'] = f'观测日不可解析: {mid} observation_date={obs!r}'
            out['absences'].append(row)
            continue
        row['observation_date'] = str(obs)[:10]
        row['lag_days'] = lag
        row['violated'] = bool(window is not None and lag > window)
        if row['violated']:
            out['violations'].append(row)
    return out


def build_health_view(ymd, data_dir=None, logs_dir=None, registry_metrics=None,
                      lookback=HEALTH_LOOKBACK_DAYS):
    """装配常态健康视图(纯消费面;要素登记 REPORT §零.5)。

    开档面仅两族: logs/pipeline_run_*.json(台账)+research_snapshot_*(经
    rp.select_snapshot 规范选择)——零采集档 glob/直读。registry_metrics 可注入
    合成条目(测试 hermetic;缺省=fe.load_registry() 实读)。
    """
    days = window_days(ymd, lookback)
    daily = _daily_dir(data_dir)
    logs = os.path.normpath(logs_dir or os.path.join(ROOT_DIR, 'logs'))
    ledger_days = {d: _ledger_summary(read_ledger(d, logs)) for d in days}
    day_snaps = {d: _snapshot_summary(d, daily) for d in days}
    channels, anchor = _channel_view(days, day_snaps)
    freshness = _freshness_view(anchor, day_snaps, _registry_metrics(registry_metrics))
    gate_a_history = [{'day': d, 'snapshot_id': day_snaps[d].get('snapshot_id'),
                       'gate_a': day_snaps[d].get('gate_a'),
                       'present': day_snaps[d].get('present', False),
                       **({'note': day_snaps[d]['note']} if not day_snaps[d].get('present') else {})}
                      for d in days]
    n_ledger = sum(1 for v in ledger_days.values() if v.get('present'))
    return {
        'view_id': f'health_monitor_{ymd}',
        'date': ymd,
        'generated_at': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'disclaimer': MONITOR_DISCLAIMER,
        'lookback_days': lookback,
        'window': {'first': days[0], 'last': days[-1], 'n_days': len(days)},
        'pipeline': {
            'n_days_with_ledger': n_ledger,
            'n_days_without_ledger': len(days) - n_ledger,
            'days': [{'day': d, **{k: v for k, v in ledger_days[d].items()}}
                     for d in days],
            'aggregate': {
                'days_with_critical_failure': [d for d in days
                                               if ledger_days[d].get('critical_failed')],
                'days_with_skipped_steps': [d for d in days if ledger_days[d].get('skipped')],
                'days_allowing_state_writeback': [d for d in days
                                                  if ledger_days[d].get('allow_state_writeback')],
            },
        },
        'snapshots': {'n_days_with_snapshot': sum(1 for v in day_snaps.values() if v.get('present')),
                      'anchor_day': anchor,
                      'gate_a_history': gate_a_history},
        'channels': channels,
        'freshness': freshness,
        'source_scope': ('台账+快照+事实层消费(logs/pipeline_run_* 经只读+research_snapshot_*'
                         ' 经 select_snapshot 规范选择),零直读采集档,零新数据通道'),
    }


def render_health_markdown(view):
    """渲染健康视图 Markdown(缺席如实,禁0填充;通道语义与 Gate A 一致)。"""
    L = [f"# 常态链路健康监测({view['view_id']})",
         "",
         f"> {view['disclaimer']}",
         f"> 回溯窗={view['lookback_days']} 日(DP-G1=②): {view['window']['first']}~{view['window']['last']}。",
         f"> {view['source_scope']}。",
         "",
         "## 流水线台账回溯",
         "",
         f"- 有台账日 {view['pipeline']['n_days_with_ledger']}/{view['window']['n_days']}"
         f"(缺席=如实列示,不视为成功);",
         f"- 关键失败日: {view['pipeline']['aggregate']['days_with_critical_failure'] or '无'};",
         f"- 跳步日: {view['pipeline']['aggregate']['days_with_skipped_steps'] or '无'};",
         f"- 允许状态回写日(allow_state_writeback): "
         f"{view['pipeline']['aggregate']['days_allowing_state_writeback'] or '无'}(台账既有放行语义,只读消费)。",
         "",
         "## 快照与 Gate A 回溯",
         "",
         f"- 窗内快照在场 {view['snapshots']['n_days_with_snapshot']}"
         f"/{view['window']['n_days']} 日;锚定快照日={view['snapshots']['anchor_day'] or '无(整体如实缺席)'};",
         "",
         "| 日 | 快照 | Gate A |",
         "|---|---|---|"]
    for g in view['snapshots']['gate_a_history']:
        sid = g.get('snapshot_id') or (g.get('note') or '缺席')
        L.append(f"| {g['day']} | {sid} | {g.get('gate_a') or '—'} |")
    L += ["", "## 逐通道断点/MISSING 回溯(DP-G3 层2;语义与 Gate A 一致)", "",
          "| 通道 | 当前状态 | 连续 MISSING | 回溯序列 |",
          "|---|---|---|---|"]
    for ch, c in sorted(view['channels'].items()):
        hist = ','.join(f"{d[-4:]}:{s or '—'}" for d, s in c['history']) or '(窗内无快照)'
        L.append(f"| {ch} | {c['current_status'] or '—'} | {c['missing_streak_days']} | {hist} |")
    fr = view['freshness']
    L += ["", "## 新鲜度越限列示(DP-G3 层1;非日频 registry 指标)", "",
          f"- 检查面={fr['checked']} 条(锚定快照日={fr.get('anchor_day') or '无'});",
          f"- 越限 {len(fr['violations'])} 条;缺席 {len(fr['absences'])} 条(如实列示,不填0)。"]
    if fr['violations']:
        L += ["", "| 指标 | 经济体 | 频率 | 观测日 | 滞后天数 | 窗(天) |",
              "|---|---|---|---|---|---|"]
        for v in fr['violations']:
            L.append(f"| {v['metric_id']} | {v.get('economy') or '—'} | {v.get('frequency')} | "
                     f"{v['observation_date']} | {v['lag_days']} | {v['window_days']} |")
    if fr['absences']:
        L += ["", "缺席披露:"]
        for a in fr['absences']:
            L.append(f"- {a['absent_reason']}")
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description='链路健康常态监测面(IA-P1-WP-G #20;纯消费面)')
    ap.add_argument('--ymd', default=datetime.now().strftime('%Y%m%d'), help='观察日 YYYYMMDD')
    ap.add_argument('--data-dir', default=None, help='数据根(含 daily/ 子目录;缺省=仓库 data/)')
    ap.add_argument('--logs-dir', default=None, help='台账目录(缺省=仓库 logs/)')
    ap.add_argument('--out', default=None, help='输出 Markdown 路径(缺省=data/research/health_monitor_{ymd}.md)')
    args = ap.parse_args(argv)
    view = build_health_view(args.ymd, data_dir=args.data_dir, logs_dir=args.logs_dir)
    md = render_health_markdown(view)
    out = args.out or os.path.join(ROOT_DIR, 'data', 'research',
                                   f'health_monitor_{args.ymd}.md')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(md)
    print(f"💾 健康监测视图已保存: {out}")
    print(f"📌 回溯窗={view['lookback_days']}日;台账日={view['pipeline']['n_days_with_ledger']}"
          f"/{view['window']['n_days']};快照日={view['snapshots']['n_days_with_snapshot']}"
          f";MISSING 通道={sum(1 for c in view['channels'].values() if c['current_status'] == 'MISSING')}"
          f";新鲜度越限={len(view['freshness']['violations'])} 缺席={len(view['freshness']['absences'])}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
