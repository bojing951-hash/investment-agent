#!/usr/bin/env python3
"""异常→研究任务衔接面(IA-P1-WP-G = P1 收口链 #20;P1_DESIGN §六 L175 + §八.2 范围3)

常态化衔接编排入口: 快照序列消费(rp.select_snapshot 规范选择→series_store)
→ 经济体规则检测(economy_anomaly_rules,DP-G2=② 模块)→ 触发→RT- 研究任务
append-only 落档(经 research_task_manager 既有机制)。

上游复用(复用调用,禁复制分叉——REPORT §零.6 登记接入点):
- rtm.SCHEMA_MIN_FIELDS(L36-L38): 任务 schema 最低字段集(可增不可减,构造后校验);
- rtm.make_task_id(L48): 确定性 task_id(同窗口/规则/指标/参数→同 id,重放幂等锚);
- rtm._task_economy(L64): RT- economy 字段既有条件写(registry.economy 恰单值才写);
- rtm.save_task(L164-L185): append-only 落档(同 id 同指纹幂等跳过/异指纹 __v{N}
  追加/原档字节不动)。
新建面(上游 build_task 硬编码 US 对不可参数化复用,泛化构造属本包范围3 语义):
build_monitor_task 泛化任务体(indicators=f×eq 对),falsifiable_conditions 三条
(阈值反证/现象消解/解释竞争——与上游 L139-L147 同族语义,非空可反驳)。

研究状态保护不绕开(§八.2 范围3 L232): 论点状态修改面(report_generator.
update_thesis_status L985)本模块零调用;流水线放行语义(台账 allow_state_writeback)
只读不依赖;本模块唯一写面=新 RT- 档案落 out_dir(append-only)。任务状态迁移
pending→active=证据装配后的任务自体生命周期(上游 run_e2e L258-L273 同构),
非既有研究状态改写。

零网络零真实模型调用(要点⑦: 监测不衔接报告生成——该面=PENDING 用户实批,
本模块未实现);不触发=如实合法结果 exit 0(情形(c));快照/序列缺席=如实零检测。
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import research_provenance as rp
import research_task_manager as rtm
from economy_anomaly_rules import (MONITOR_DISCLAIMER, RULES,
                                   detect_all_from_series_store)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TASK_ORIGIN = 'IA-P1-WP-G 常态监测衔接(E2E-A 任务结构族扩展:economy 专用对)'


def build_monitor_task(economy, detection, fx_series, eq_series, snapshot_meta,
                       as_of=None):
    """构造泛化 RT- 任务档(schema=rtm.SCHEMA_MIN_FIELDS 可增不可减;状态 pending)。

    economy: 规则经济体键;detection: detect_economy_divergence 输出(触发态);
    fx_series/eq_series: {'metric_id','dates','values'}(档内直读装配源);
    snapshot_meta: {'snapshot_id','file'}(快照溯源);as_of: 研究截止 ISO 时点。
    """
    rule = RULES[economy]
    now_utc = datetime.now(timezone.utc).isoformat(timespec='seconds')
    p = detection['params']
    start, end = detection['window']['start'], detection['window']['end']
    indicators = [rule['fx_metric'], rule['eq_metric']]
    task_id = rtm.make_task_id(start, end, detection['rule_id'], indicators, p)
    s = p['expected_corr_sign']
    phenomenon = (f"{rule['fx_metric']}×{rule['eq_metric']} 统计背离({economy} 经济体对): "
                  f"检测窗口 {start}~{end} 内规则 {detection['rule_id']} 触发——"
                  f"{len(detection['trigger_points'])} 个共同观测日满足判定式"
                  f"(滚动{p['rolling_window']}日差分相关 rho×预期符号({s:+d})≤"
                  f"-{p['corr_threshold']},或 驱动{rule['fx_metric']}窗口"
                  f"{p['fx_pct_threshold']}%+ 变动且响应{rule['eq_metric']}按预期反向"
                  f"{p['eq_pct_threshold']}%+,阈值含等号);{rule['rationale']}。"
                  f"统计背离描述非因果结论,见 falsifiable_conditions。")
    task = {
        'task_id': task_id,
        'created_at': now_utc,
        'phenomenon': phenomenon,
        'status': 'pending',
        'indicators': indicators,
        'window': {'start': start, 'end': end, 'source_date': None,
                   'alignment': detection['alignment'],
                   'common_observations': detection['summary']['n_common']},
        'detection': {'rule_id': detection['rule_id'], 'frozen_params': p,
                      'triggered': detection['triggered'],
                      'trigger_points': detection['trigger_points'],
                      'trigger_stats': {'summary': detection['summary'],
                                        'series': detection['series']}},
        'evidence': {
            'data_access_points': {
                'series': ('snapshot.series_store via research_provenance.select_snapshot'
                           '(监测面零直读采集档,P1_DESIGN §八.2 要点①)'),
                'registry': 'config/metric_registry.json(只读实读)'},
            'source_artifacts': [
                {'metric_id': mid, 'snapshot_id': snapshot_meta.get('snapshot_id'),
                 'file': snapshot_meta.get('file')}
                for mid in indicators],
            'computation_ref': (f'检测=scripts/economy_anomaly_rules.py '
                                f'{detection["rule_id"]}(DP-G2=② 规则模块,'
                                '阈值登记结构与 anomaly_detector 同构);'
                                '衔接=scripts/monitor_task_bridge.py(本包)'),
            'series_window': None,   # run_bridge 装配窗口内共同序列(档内直读)
            'data_quality': {
                mid: {'in_series_store': True,
                      'n_observations': len({'fx': fx_series, 'eq': eq_series}[which]['dates'])}
                for mid, which in ((rule['fx_metric'], 'fx'), (rule['eq_metric'], 'eq'))}},
        'falsifiable_conditions': [
            f"反驳条件A(阈值反证): 若窗口内 {rule['fx_metric']} 的{p['rolling_window']}"
            f"共同观测日区间变动 < {p['fx_pct_threshold']}%,且逐期滚动相关 rho×"
            f"预期符号({s:+d}) > -{p['corr_threshold']},则背离判定不成立——本判定"
            "可由窗口数据直接复核反驳。",
            f"反驳条件B(现象消解): 若后续窗口 {rule['eq_metric']} 恢复按登记预期符号"
            f"({s:+d})联动的同时 {rule['fx_metric']} 继续原方向变动,则'背离'前提消失,"
            "现象随之消解。",
            "反驳条件C(解释竞争): 本检测为统计现象描述而非因果结论;若引入风险偏好/"
            "利差/资本流动等控制变量后两序列相关性恢复登记预期符号,则该背离作为"
            "独立研究主题的必要性不成立。"],
        'history': [{'ts': now_utc, 'from': None, 'to': 'pending',
                     'note': f'常态监测规则触发,任务建立({TASK_ORIGIN})'}],
    }
    missing = [k for k in rtm.SCHEMA_MIN_FIELDS if k not in task]
    if missing:
        raise ValueError(f'任务档缺 schema 最低字段(可增不可减): {missing}')
    task_economy = rtm._task_economy(indicators)   # 既有条件写(恰单经济体才写键)
    if task_economy is not None:
        task['economy'] = task_economy
    return task


def run_bridge(ymd, start, end, data_dir=None, out_dir=None, as_of=None,
               detections=None):
    """常态化衔接编排(监测运行面): 快照→规则检测→触发→建任务+装配+落档。

    detections 可注入预计算检测结果(测试面);缺省=自快照 series_store 检测。
    返回 (summary_dict, results)。不触发/快照缺席=如实零任务,exit 语义由调用方
    (CLI 恒 exit 0——不触发是合法结果,情形(c))。
    """
    daily = os.path.join(data_dir or os.path.join(ROOT_DIR, 'data'), 'daily')
    snap, why = rp.select_snapshot(ymd, daily)
    print('[MON:params] ' + json.dumps(
        {e: {'rule_id': r['rule_id'], 'expected_corr_sign': r['expected_corr_sign']}
         for e, r in RULES.items()}, ensure_ascii=False, sort_keys=True))
    if snap is None:
        print(f'[MON:snapshot] 快照缺席: {why}(如实零检测,不代行快照构建)')
        summary = {'ymd': ymd, 'snapshot_available': False,
                   'snapshot_unavailable_reason': str(why),
                   'n_triggered': 0, 'n_tasks_written': 0, 'tasks': [],
                   'disclaimer': MONITOR_DISCLAIMER}
        print('[MON:summary] ' + json.dumps(
            {k: v for k, v in summary.items() if k != 'disclaimer'},
            ensure_ascii=False, sort_keys=True))
        return summary, {}
    store = snap.get('series_store') or {}
    print(f"[MON:snapshot] {snap.get('snapshot_id')} series_store="
          f"{len(store)} 序列(消费面零直读采集档)")
    dets = detections if detections is not None \
        else detect_all_from_series_store(store, start, end)
    results = {}
    n_triggered = n_written = 0
    for econ, det in dets.items():
        rule = RULES[econ]
        if det.get('absent_reason'):
            print(f"[MON:detect:{econ}] {det['absent_reason']}")
            results[econ] = {'triggered': False, 'absent_reason': det['absent_reason'],
                             'task': None}
            continue
        s_ = det['summary']
        print(f"[MON:detect:{econ}] {det['rule_id']} triggered={det['triggered']} "
              f"n_common={det['alignment']['n_common']} n_scored={s_.get('n_scored')} "
              f"n_triggered={s_.get('n_triggered')}")
        if not det['triggered']:
            results[econ] = {'triggered': False, 'task': None}
            continue
        n_triggered += 1
        fx_series = {'metric_id': rule['fx_metric'],
                     'dates': (store.get(rule['fx_metric']) or {}).get('dates') or [],
                     'values': (store.get(rule['fx_metric']) or {}).get('values') or []}
        eq_series = {'metric_id': rule['eq_metric'],
                     'dates': (store.get(rule['eq_metric']) or {}).get('dates') or [],
                     'values': (store.get(rule['eq_metric']) or {}).get('values') or []}
        task = build_monitor_task(econ, det, fx_series, eq_series,
                                  {'snapshot_id': snap.get('snapshot_id'),
                                   'file': os.path.basename(why)}, as_of=as_of)
        fmap = dict(zip(fx_series['dates'], fx_series['values']))
        emap = dict(zip(eq_series['dates'], eq_series['values']))
        common = sorted(d for d in (set(fx_series['dates']) & set(eq_series['dates']))
                        if start <= d <= end)
        task['evidence']['series_window'] = {
            'common_dates': common,
            rule['fx_metric']: [fmap[d] for d in common],
            rule['eq_metric']: [emap[d] for d in common]}
        task['window']['source_date'] = ymd
        task['history'].append({'ts': datetime.now(timezone.utc).isoformat(timespec='seconds'),
                                'from': 'pending', 'to': 'active',
                                'note': '证据装配完毕(快照序列档内直读);'
                                        'concluded 及以后为后续包'})
        task['status'] = 'active'
        od = out_dir or rtm.DEFAULT_OUT_DIR
        status, path = rtm.save_task(task, od)
        if status == 'written':
            n_written += 1
        print(f"[MON:task:{econ}] {status}: {path}")
        if status == 'skipped-idempotent':
            print(f"[MON:task:{econ}] 同task_id重放→幂等跳过(既有档零写入,append-only)")
        results[econ] = {'triggered': True, 'task_id': task['task_id'],
                         'save_status': status, 'task_path': path,
                         'task_status': task['status'], 'economy': task.get('economy')}
    summary = {'ymd': ymd, 'snapshot_available': True,
               'snapshot_id': snap.get('snapshot_id'),
               'window': {'start': start, 'end': end},
               'n_rules': len(RULES), 'n_triggered': n_triggered,
               'n_tasks_written': n_written,
               'tasks': [{'economy': r.get('economy'), 'task_id': r.get('task_id'),
                          'save_status': r.get('save_status')} for r in results.values()
                         if r.get('triggered')],
               'disclaimer': MONITOR_DISCLAIMER,
               'state_protection': ('研究状态保护不绕开: 零 update_thesis_status 调用;'
                                    '落档经 rtm.save_task append-only 既有机制')}
    print('[MON:summary] ' + json.dumps(
        {k: v for k, v in summary.items() if k not in ('disclaimer', 'state_protection')},
        ensure_ascii=False, sort_keys=True))
    return summary, results


def main(argv=None):
    ap = argparse.ArgumentParser(description='异常→研究任务衔接面(IA-P1-WP-G #20;append-only)')
    ap.add_argument('--ymd', required=True, help='观察日 YYYYMMDD(快照选择)')
    ap.add_argument('--start', required=True, help='检测窗口起点 YYYY-MM-DD')
    ap.add_argument('--end', required=True, help='检测窗口终点 YYYY-MM-DD')
    ap.add_argument('--data-dir', default=None, help='数据根(含 daily/ 子目录;缺省=仓库 data/)')
    ap.add_argument('--out-dir', default=None, help=f'研究档案目录(缺省={rtm.DEFAULT_OUT_DIR})')
    ap.add_argument('--as-of', default=None, help='研究截止 ISO 时点(缺省=自然当前,确定性回放可显式传入)')
    args = ap.parse_args(argv)
    run_bridge(args.ymd, args.start, args.end, data_dir=args.data_dir,
               out_dir=args.out_dir, as_of=args.as_of)
    return 0


if __name__ == '__main__':
    sys.exit(main())
