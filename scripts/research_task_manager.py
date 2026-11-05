#!/usr/bin/env python3
"""IA-P03-W1 E2E-A: 研究任务管理器(任务结构/append-only 档案/E2E 编排入口)

合同 E2EA-AC-03/AC-04:
- 统一研究任务 schema 最低字段集(可增不可减): task_id/created_at(UTC)/phenomenon/
  status/indicators/window/detection(规则+冻结参数+触发统计)/evidence(接入点+
  产物标识+计算指针+数据质量状态)/falsifiable_conditions(非空)/history(追加式);
- 状态机(登记): pending → active → concluded → tracking;本包实现至
  active=证据装配完毕(concluded 及以后为 P0-3 后续包定义,不实现);
- 档案落 data/research/(允许写入,不 commit),append-only:
  * 同 task_id 重放规则(登记): 指纹一致→**幂等跳过**(不新建不改写既有档);
    指纹不一致(防御路径)→新版本追加 {task_id}__v{N}.json(原档字节不动);
  * 检测统计序列每运行落独立 detection_series 文件(序号递增,永不覆盖);
- E2E-A 编排: 参数echo → 历史查询(登记接入点) → 对齐 → 检测 →
  触发→建任务(pending)→证据装配(真实序列+计算结果档内直读)→落档→active→stdout 摘要;
  不触发→如实输出+分流说明(合同情形(c),合法结果,exit 0)。

零网络;研究档案/统计文件为**自产档案**(非原始采集档),写入仅限 out_dir。
"""
import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import anomaly_detector as ad
import research_history_query as rhq

# 档案输出目录(自产研究档案;默认 DEV data/research/,不 commit)
DEFAULT_OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                               'data', 'research')

SCHEMA_MIN_FIELDS = ['task_id', 'created_at', 'phenomenon', 'status', 'indicators',
                     'window', 'detection', 'evidence', 'falsifiable_conditions',
                     'history']
STATUS_FLOW = ['pending', 'active', 'concluded', 'tracking']   # 本包实现至 active
REPLAY_POLICY = ('idempotent-skip on identical fingerprint; '
                 'new-version-file ({task_id}__v{N}.json) on different fingerprint; '
                 'original archive bytes never rewritten')

RATE_METRIC = 'TIPS_10Y'    # 实际利率(registry 优先级①,直用;登记见 REPORT)
GOLD_METRIC = 'GOLD_F'      # COMEX 黄金期货主力连续


def make_task_id(start, end, rule_id, indicators, params):
    """确定性 task_id(不含时间戳): 同窗口/规则/指标/参数→同 id(重放幂等锚)。"""
    fingerprint = json.dumps({'start': start, 'end': end, 'rule_id': rule_id,
                              'indicators': sorted(indicators), 'params': params},
                             sort_keys=True, ensure_ascii=False)
    return f"RT-{start}~{end}-{rule_id}-{hashlib.sha256(fingerprint.encode('utf-8')).hexdigest()[:8]}"


# IA-P1-GAP08 R47-F1(WP-D REPORT §一.6-F1 承接=DESIGN §四 L143 候选完整落地):
# RT- 任务记录增 economy 字段——取值经 registry.economy 实读推导;恰单经济体
# 才写键(跨经济体不设单过滤维度,形态先例=WP-D PD-4 恰单族命中才写
# ir["economy"]);任务体其余字段含 falsifiable_conditions 不变(L143),
# schema 可增不可减(SCHEMA_MIN_FIELDS 不动)。
RT_ECONOMIES = ("US", "CN", "JP", "EA", "HK", "GLOBAL")   # registry economy 值域实测同集


def _task_economy(indicators):
    """指标族经济体派生: registry.economy 实读集合恰单值→该值;跨经济体/
    零注册指标/零 economy 值→None(不写键,如实无单维度)。"""
    import fact_engine as fe
    econs = set()
    for mid in indicators or []:
        m = fe.metric(mid) if isinstance(mid, str) else None
        e = (m or {}).get('economy')
        if isinstance(e, str) and e.strip():
            econs.add(e)
    if len(econs) == 1 and next(iter(econs)) in RT_ECONOMIES:
        return next(iter(econs))
    return None


def build_task(start, end, detection, rate_payload, gold_payload, as_of=None):
    """构造完整 schema 任务档(状态 pending→active 由 run_e2e 驱动;
    evidence.series_window 由 run_e2e 在检测后装配窗口内共同序列)。"""
    now_utc = datetime.now(timezone.utc).isoformat(timespec='seconds')
    p = detection['params']
    task_id = make_task_id(start, end, detection['rule_id'],
                           [RATE_METRIC, GOLD_METRIC], p)
    phenomenon = (f"实际利率({RATE_METRIC})与黄金({GOLD_METRIC})背离: 检测窗口 "
                  f"{start}~{end} 内规则 {detection['rule_id']} 触发——"
                  f"{len(detection['trigger_points'])} 个共同观测日满足判定式"
                  f"(滚动{p['rolling_window']}日相关 rho≥{p['corr_threshold']}"
                  f" 或 实际利率{p['rate_bp_threshold']}bp上行且金价"
                  f"{p['gold_pct_threshold']}%上行,阈值含等号);"
                  f"实际利率上行而金价坚挺,背离经典负相关预期。"
                  if detection['triggered'] else
                  f"实际利率({RATE_METRIC})与黄金({GOLD_METRIC})背离检测: 窗口 "
                  f"{start}~{end} 内规则 {detection['rule_id']} 未触发(如实记录,"
                  f"见 detection.trigger_stats)。")
    indicators = [RATE_METRIC, GOLD_METRIC]
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
            'data_access_points': {'rate': rate_payload['source']['access_point'],
                                   'gold': gold_payload['source']['access_point'],
                                   'registry': 'config/metric_registry.json(只读实读)'},
            'source_artifacts': [
                {'metric_id': RATE_METRIC, 'file': rate_payload['source']['file'],
                 'file_date': rate_payload['source']['file_date'],
                 'sha256': rate_payload['source']['sha256']},
                {'metric_id': GOLD_METRIC, 'file': gold_payload['source']['file'],
                 'file_date': gold_payload['source']['file_date'],
                 'sha256': gold_payload['source']['sha256']}],
            'computation_ref': ('检测=scripts/anomaly_detector.py RD-DIV-001'
                                '(滚动相关/区间变动;单位口径=fact_engine '
                                'RATE_UNITS(pp→bp)/PRICE_LIKE_UNITS(→pct));'
                                '查询与对齐=scripts/research_history_query.py'),
            'series_window': None,   # run_e2e 装配窗口内共同序列(档内直读)
            'data_quality': {
                RATE_METRIC: {'quality_status': rate_payload['quality_status'],
                              'observation_date': rate_payload['observation_date'],
                              'unit': rate_payload['unit'],
                              'value': rate_payload['value'],
                              'series_clean': rate_payload['series_clean']},
                GOLD_METRIC: {'quality_status': gold_payload['quality_status'],
                              'observation_date': gold_payload['observation_date'],
                              'unit': gold_payload['unit'],
                              'value': gold_payload['value'],
                              'series_clean': gold_payload['series_clean']}}},
        'falsifiable_conditions': [
            f"反驳条件A(阈值反证): 若窗口内 {RATE_METRIC} 的{p['rolling_window']}"
            f"共同观测日区间变动 < {p['rate_bp_threshold']}bp 且逐期滚动相关 rho < "
            f"{p['corr_threshold']},则背离判定不成立——本判定可由窗口数据直接复核反驳。",
            f"反驳条件B(现象消解): 若后续窗口 {GOLD_METRIC} 区间变动转负的同时 "
            f"{RATE_METRIC} 继续上行,则'金价坚挺'前提消失,现象随之消解。",
            "反驳条件C(解释竞争): 本检测为统计现象描述而非因果结论;若引入央行购金/"
            "地缘风险/美元信用等控制变量后利率-金价相关性恢复负值,则'利率-金价背离'"
            "作为独立研究主题的必要性不成立。"],
        'history': [{'ts': now_utc, 'from': None, 'to': 'pending',
                     'note': '检测触发,任务建立(E2E-A 自动编排)'}],
    }
    # IA-P1-GAP08 R47-F1: economy 条件写(恰单经济体→顶层键;默认任务
    # TIPS_10Y(US)+GOLD_F(GLOBAL)跨经济体→如实不写键)。
    task_economy = _task_economy(indicators)
    if task_economy is not None:
        task['economy'] = task_economy
    return task


def _fingerprint_params(task):
    return json.dumps(task.get('detection', {}).get('frozen_params'),
                      sort_keys=True, ensure_ascii=False)


def save_task(task, out_dir):
    """append-only 落档。返回 (status, path): status ∈
    written(新档)/skipped-idempotent(同id同指纹,零写入)/
    written-new-version(同id异指纹,追加__v{N},原档不动)。"""
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{task['task_id']}.json")
    new_version = False
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            existing = json.load(f)
        if _fingerprint_params(existing) == _fingerprint_params(task):
            return 'skipped-idempotent', path
        n = 2
        while os.path.exists(os.path.join(out_dir, f"{task['task_id']}__v{n}.json")):
            n += 1
        path = os.path.join(out_dir, f"{task['task_id']}__v{n}.json")
        new_version = True
    _tmp = path + '.tmp'
    with open(_tmp, 'w', encoding='utf-8') as f:
        json.dump(task, f, ensure_ascii=False, indent=1)
    os.replace(_tmp, path)
    return ('written-new-version' if new_version else 'written'), path


def save_detection_series(detection, start, end, out_dir):
    """逐期触发统计序列独立落档(append-only: 同窗序号递增,永不覆盖)。"""
    os.makedirs(out_dir, exist_ok=True)
    prefix = f"detection_series_{start}_{end}_"
    seq = len([n for n in os.listdir(out_dir) if n.startswith(prefix)]) + 1
    path = os.path.join(out_dir, f"{prefix}{seq:03d}.json")
    doc = {'rule_id': detection['rule_id'], 'window': {'start': start, 'end': end},
           'params': detection['params'], 'alignment': detection['alignment'],
           'summary': detection['summary'], 'triggered': detection['triggered'],
           'series': detection['series']}
    _tmp = path + '.tmp'
    with open(_tmp, 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    os.replace(_tmp, path)
    return path


def _sha256_file(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def run_e2e(start, end, source_date, data_dir=None, out_dir=None,
            trusted_root=None, as_of=None, export_series=True):
    """E2E-A 编排(真实回放入口): 查询→对齐→检测→(触发)建任务+装配+落档→摘要。

    返回 (detection, task_path or None, save_status or None)。stdout=运行日志
    (第一行参数 echo;触发与否均 exit 0——不触发是合法结果,合同情形(c))。
    """
    print("[E2E-A:params] " + json.dumps(ad.echo_params(), ensure_ascii=False,
                                         sort_keys=True))
    print(f"[E2E-A:window] start={start} end={end} source_date={source_date} "
          f"as_of={as_of or '(source_date日末)'} replay_policy={REPLAY_POLICY}")
    rate = rhq.load_metric_series(RATE_METRIC, source_date, as_of=as_of,
                                  data_dir=data_dir, trusted_root=trusted_root)
    gold = rhq.load_metric_series(GOLD_METRIC, source_date, as_of=as_of,
                                  data_dir=data_dir, trusted_root=trusted_root)
    for p_ in (rate, gold):
        print(f"[E2E-A:source] {p_['metric_id']} unit={p_['unit']} "
              f"quality={p_['quality_status']} obs={p_['observation_date']} "
              f"n_obs={len(p_['dates'])} file={p_['source']['file']} "
              f"sha256={str(p_['source']['sha256'])[:12]}… "
              f"via={p_['source']['access_point'].split(' via ')[1].split(' (')[0]}")
    det = ad.detect_divergence(rate['dates'], rate['values'], gold['dates'],
                               gold['values'], start, end)
    print(f"[E2E-A:align] {det['alignment']['rule']}; n_common={det['alignment']['n_common']}")
    s = det['summary']
    last = s.get('last')
    if last:
        print(f"[E2E-A:stats] n_scored={s['n_scored']} n_triggered={s['n_triggered']} "
              f"first_trigger={s['first_trigger_date']} "
              f"rho_range=[{s['rho_min']},{s['rho_max']}] "
              f"last=(date={last['date']},rho={last['rho']},"
              f"chg_r_bp={last['chg_r_bp']},chg_g_pct={last['chg_g_pct']})")
    else:
        print(f"[E2E-A:stats] {s}")
    od = out_dir or DEFAULT_OUT_DIR
    series_path = None
    if export_series:
        series_path = save_detection_series(det, start, end, od)
        print(f"[E2E-A:series] 触发统计序列已落档: {series_path} "
              f"(sha256={_sha256_file(series_path)[:12]}…)")
    if not det['triggered']:
        print("[E2E-A:result] NOT TRIGGERED —— 登记窗口内无共同观测日满足判定式;"
              "如实记录(合同§九情形(c):真实不触发是合法结果,不调参重跑凑触发;"
              "补证据轮=补真实重跑或调整登记窗口后的重放,禁新FIX禁重构)。")
        print(f"[E2E-A:summary] window={start}~{end} triggered=False "
              f"n_common={det['alignment']['n_common']} archive=None "
              f"series={series_path}")
        return det, None, None
    task = build_task(start, end, det, rate, gold, as_of)
    # 窗口内共同序列档内直读(装配证据;升序,与检测器对齐口径一致)
    common = sorted(d for d in (set(rate['dates']) & set(gold['dates']))
                    if start <= d <= end)
    rmap, gmap = dict(zip(rate['dates'], rate['values'])), dict(zip(gold['dates'], gold['values']))
    task['evidence']['series_window'] = {
        'common_dates': common,
        RATE_METRIC: [rmap[d] for d in common],
        GOLD_METRIC: [gmap[d] for d in common]}
    task['window']['source_date'] = source_date
    task['history'].append({'ts': datetime.now(timezone.utc).isoformat(timespec='seconds'),
                            'from': 'pending', 'to': 'active',
                            'note': '证据装配完毕(真实序列+计算结果档内直读);'
                                    'concluded 及以后为后续包'})
    task['status'] = 'active'
    status, path = save_task(task, od)
    print(f"[E2E-A:archive] {status}: {path}")
    if status == 'skipped-idempotent':
        print(f"[E2E-A:archive] 同task_id重放→幂等跳过(登记规则;既有档零写入,"
              f"sha256={_sha256_file(path)} 不变)")
    print(f"[E2E-A:archive] task_id={task['task_id']} status={task['status']} "
          f"sha256={_sha256_file(path)}")
    trig = det['trigger_points']
    print("[E2E-A:result] TRIGGERED —— 首触发日 %s 共%d日满足判定式;任务已建立并"
          "装配证据(档内直读: evidence.series_window 窗口内两序列共同观测 + "
          "detection.trigger_stats.series 逐期统计)。" % (s['first_trigger_date'], len(trig)))
    print(f"[E2E-A:summary] window={start}~{end} triggered=True "
          f"n_common={det['alignment']['n_common']} n_triggered={len(trig)} "
          f"task_id={task['task_id']} archive={path} series={series_path}")
    return det, path, status


def _main():
    ap = argparse.ArgumentParser(description='研究任务管理器(E2E-A 编排入口)')
    ap.add_argument('--run-e2e', action='store_true', help='运行 E2E-A 编排(检测→建任务→装配→落档)')
    ap.add_argument('--start', required=True, help='检测窗口起点 YYYY-MM-DD')
    ap.add_argument('--end', required=True, help='检测窗口终点 YYYY-MM-DD')
    ap.add_argument('--source-date', required=True, help='采集档日期 YYYYMMDD(接入点解析)')
    ap.add_argument('--data-dir', default=None, help='采集数据目录(缺省=snapshot_builder 权威常量)')
    ap.add_argument('--out-dir', default=None, help=f'研究档案目录(缺省={DEFAULT_OUT_DIR})')
    ap.add_argument('--trusted-root', default=None,
                    help='采集目录可信根(缺省=代码位置推导项目根;沙箱/测试显式传入)')
    ap.add_argument('--as-of', default=None, help='研究截止 ISO 时点(缺省=source_date 日末,确定性回放)')
    args = ap.parse_args()
    if not args.run_e2e:
        ap.error('本入口当前仅提供 --run-e2e(其余状态机迁移为后续包)')
    run_e2e(args.start, args.end, args.source_date, data_dir=args.data_dir,
            out_dir=args.out_dir, trusted_root=args.trusted_root, as_of=args.as_of)


if __name__ == '__main__':
    _main()
