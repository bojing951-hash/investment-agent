"""
一键生成投资周报
串联：全球数据采集 → A股港股采集 → 宏观数据采集 → 数据汇总 → 报告生成

IA-P0-1(2026-10-27)失败传播修复:
- 步骤依赖图(4元组,兼容旧3元组): 评分卡/相关性/装配器依赖快照构建;
  校验器依赖装配器(预测观察步骤已于 MW-V1 2026-11-08 章程勘误下线);
- 依赖未成功 → 依赖步骤标记SKIPPED并记录原因,不执行危险操作(旧实现无条件
  全部执行: Gate A FAIL后装配器照常打包、校验器照常跑);
- 关键步骤失败或被跳过 → 流水线退出码1(既有行为),跳过原因写入
  logs/pipeline_run_YYYYMMDD.json(AC-11可追溯)。

CLI(P0-2链路修复, 2026-11-09):
  --allow-revision        同日重跑允许修订快照(转发 snapshot_builder,生成_vN原版保留;
                          不带此参数时同日重跑被不可变保护拒绝,step9 exit 3 → 流水线 exit 1)
  --revision-reason TEXT  修订原因(随 --allow-revision 转发写入快照 revision_reason)
"""

import argparse
import subprocess
import sys
import os
import json
from datetime import datetime

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(PROJECT_DIR, 'scripts')

def run_step(step_name, script_name, timeout=900, script_dir=None, extra_args=None):
    """运行一个步骤(默认15分钟超时,防止网络挂死堵住launchd——见a_stock_tracker 2026-10-01事故)。

    extra_args(P0-2): 透传给步骤脚本的附加命令行参数(如 snapshot_builder 的
    --allow-revision);缺省 None=零参(既有行为,接口兼容)。"""
    print(f"\n{'='*50}")
    print(f"▶ 步骤: {step_name}")
    print(f"{'='*50}")

    script_path = os.path.join(script_dir or SCRIPTS_DIR, script_name)

    if not os.path.exists(script_path):
        print(f"❌ 脚本不存在: {script_path}")
        return False

    try:
        result = subprocess.run(
            [sys.executable, script_path] + list(extra_args or []),
            cwd=PROJECT_DIR,
            capture_output=False,
            timeout=timeout
        )
    except subprocess.TimeoutExpired:
        print(f"⏰ {step_name} 超时({timeout}秒),已终止,继续下一步")
        return False

    if result.returncode != 0:
        print(f"⚠️  {step_name} 可能有问题 (返回码: {result.returncode})")
        return False

    print(f"✅ {step_name} 完成")
    return True


class PipelineResults(list):
    """步骤结果列表[(名称, 成功?, 关键?)] + skips{名称: 跳过原因}(IA-P0-1)。

    仍是普通list(3元组解包/索引/计数等既有用法全部兼容),仅附加跳过台账。"""
    def __init__(self, iterable=(), skips=None):
        super().__init__(iterable)
        self.skips = dict(skips or {})


def run_pipeline(steps, script_dir=None, extra_args_by_script=None):
    """顺序执行步骤。steps元素为(名称, 脚本, 关键?)或(名称, 脚本, 关键?, 依赖脚本名列表);
    返回PipelineResults([(名称, 成功?, 关键?)])供退出码判定:
    - 只有**关键**步骤失败才使流水线失败;非关键失败(新闻/相关性)降级运行,
      不影响其余步骤执行;
    - IA-P0-1: 声明了依赖的步骤,任一依赖未成功(失败或自身被跳过)→本步骤
      SKIPPED(结果记False),原因存于.skips并公示——依赖失败后继续跑下游
      只会用未验证数据做危险操作(旧缺陷)。依赖以**脚本名**为标识(步骤显示名
      可变,脚本名稳定),公示时换算回步骤名保持可读。
    - P0-2: extra_args_by_script={脚本名: [附加参数]} 按脚本透传给 run_step
      (缺省 None=全部零参,既有行为不变)。
    """
    results = PipelineResults()
    # 脚本名 → 步骤显示名(依赖公示用);脚本名 → 是否成功(依赖判定用)
    name_by_script = {s[1]: s[0] for s in steps if len(s) >= 2}
    ok_scripts = set()
    for step in steps:
        step_name, script_name, critical = step[0], step[1], step[2]
        deps = list(step[3]) if len(step) > 3 else []
        if deps:
            bad = [d for d in deps if d not in ok_scripts]
            if bad:
                skips = getattr(results, 'skips', {})
                why = '; '.join(
                    f"{name_by_script.get(d, d)}({'已跳过: ' + skips[name_by_script[d]]})"
                    if name_by_script.get(d) in skips
                    else f"{name_by_script.get(d, d)}(失败)"
                    for d in bad)
                reason = f"依赖未成功 → {why}"
                print(f"\n⏭️  SKIPPED {step_name}: {reason}")
                results.skips[step_name] = reason
                results.append((step_name, False, critical))
                continue
        # P0-2 兼容: 仅在确有附加参数时才传 extra_args——零参路径保持旧调用
        # 形状(既有测试/替身的 run_step 签名不含新参,演进不得破坏旧契约)
        extra = (extra_args_by_script or {}).get(script_name)
        if extra is None:
            success = run_step(step_name, script_name, script_dir=script_dir)
        else:
            success = run_step(step_name, script_name, script_dir=script_dir,
                               extra_args=extra)
        results.append((step_name, success, critical))
        if success:
            ok_scripts.add(script_name)
    return results

def main():
    ap = argparse.ArgumentParser(
        description='投资周报一键流水线(采集→快照→评分→装配→校验)')
    ap.add_argument('--allow-revision', action='store_true',
                    help='同日重跑允许修订快照(转发 snapshot_builder: 生成_vN新版本,'
                         '原版保留);不带时同日重跑被不可变保护拒绝(exit 3→流水线 exit 1)')
    ap.add_argument('--revision-reason', default=None,
                    help='修订原因(随 --allow-revision 转发,写入快照 revision_reason)')
    args = ap.parse_args()

    start_time = datetime.now()

    print("=" * 60)
    print("📊 投资周报一键生成")
    print(f"🕐 开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # IA-P0-1依赖图(第4元=依赖脚本名,前置须成功否则本步骤SKIPPED)+FIX-03收紧:
    # - 快照构建无依赖——采集失败时仍构建快照(如实fallback/降级/FAIL评级),
    #   让Gate A对数据质量做显式裁决,而不是流水线替它隐式跳过;
    # - FIX-03(IA-DEF-003): 正式研究计算/正式数据包/锚点校验不仅依赖快照构建,
    #   还依赖**全部关键采集器**成功——关键采集失败后不得因旧采集文件存在就
    #   自动放行下游正式产物(旧文件回退属快照层的已披露降级能力,须人工/显式
    #   处置,不在自动流水线内冒充当日成功批次);受影响步骤SKIPPED并记录上游名;
    # - 预测观察步骤已下线(MW-V1 章程勘误,见 steps 尾注);无自持门禁步骤。
    _critical_collectors = ["global_market_collector.py", "china_market_collector.py",
                            "macro_collector.py", "rate_expectations.py"]
    _formal_research_deps = ["snapshot_builder.py"] + _critical_collectors
    # FIX2-03(IA-DEF-003): 评分卡是**关键步骤**且其产物(当日评分)被装配进正式
    # 数据包——数据装配与校验不仅依赖快照+关键采集,还依赖评分卡成功;评分卡
    # 失败 → 装配/校验SKIPPED(不得用旧评分冒充当日成功批次,装配器对旧评分
    # 只作"历史参考"标注且报告入口按pack meta拒绝)。
    _pack_deps = ["macro_scorecard.py"] + list(_formal_research_deps)
    steps = [
        ("1/13 全球市场数据采集", "global_market_collector.py", True),
        ("2/13 A股港股数据采集", "china_market_collector.py", True),
        ("3/13 宏观数据采集", "macro_collector.py", True),
        # 非关键(第五轮P1-2): 新闻源失败可降级——原始标题缺失只影响周报叙事,
        # 不影响其余步骤;整体退出码不因非关键失败而转失败。
        ("4/13 新闻采集与分析", "news_collector.py", False),
        ("5/13 利率预期与实体经济", "rate_expectations.py", True),
        # MW-V1(2026-11-08 章程校准): 日欧通道采集挪到快照构建**之前**——原尾部步骤
        # 在快照后执行,jp_/ea_ 当日档结构上进不了当日快照(恒 T-1 回退);同时把
        # japan_rate_collector(JGB 曲线/日政策利率权属,japan_ 档)纳入调度——原
        # 13 步无任何步骤跑它,japan 通道在生产上永缺失(data/daily 仅 11-05 一份
        # 手动档,超 5 天回退窗后 JGB 全 MISSING)。三通道保持非关键: 源失败只登记
        # sources_status/alerts 如实降级,不阻塞主链(IA-P1-WP-A D7 边界口径)。
        ("6/13 日本利率与国债曲线(japan_)", "japan_rate_collector.py", False),
        ("7/13 日本市场数据采集(jp_)", "jp_market_collector.py", False),
        ("8/13 欧元区市场数据采集(ea_)", "ea_market_collector.py", False),
        # 第七轮重构: 采集层之后先建研究快照(唯一数据入口/Gate A),评分卡/相关性/
        # 装配器/校验器均消费快照,不再各自glob"最新文件"或自行拉数(文件最新≠数据最新)。
        ("9/13 研究快照构建(Gate A)", "snapshot_builder.py", True),
        ("10/13 宏观体制评分卡(消费快照)", "macro_scorecard.py", True,
         list(_formal_research_deps)),
        # 相关性计算器2026-10-11接线:必须在data_assembler之前跑,汇编器会读取
        # correlation_*.md拼进数据包第五节。非关键: 相关性缺失只降级周报第五节。
        ("11/13 跨资产相关性(消费快照)", "correlation_calculator.py", False,
         list(_formal_research_deps)),
        ("12/13 数据汇总打包", "data_assembler.py", True,
         list(_pack_deps)),
        ("13/13 数据校验与锚点生成", "data_validator.py", True,
         ["data_assembler.py"] + list(_pack_deps)),
        # MW-V1(2026-11-08 章程勘误): 预测观察步骤下线——预测池/命中裁决/超配低配/
        # 论点星级属越位零件(PRODUCT-GOAL.md 2026-11-08 勘误:观点由用户形成,系统
        # 供证据)。daily_prediction_observer 模块与历史观察档案原样保留(历史研究
        # 记录不删),仅退出自动调度;config/allocation_views.json 冻结为历史档。
    ]

    # P0-2 链路: --allow-revision/--revision-reason 透传到快照构建步骤
    # (此前 run_weekly 零参数解析,ia_cli 转发的旗标被静默吞掉,同日重跑必失败)
    revision_args = []
    if args.allow_revision:
        revision_args.append('--allow-revision')
        if args.revision_reason:
            revision_args += ['--revision-reason', args.revision_reason]

    # 零参路径保持旧调用形状 run_pipeline(steps)(兼容替身签名);仅修订时传新参
    if revision_args:
        results = run_pipeline(
            steps, extra_args_by_script={'snapshot_builder.py': revision_args})
    else:
        results = run_pipeline(steps)

    # 汇总
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    skips = getattr(results, 'skips', {})

    print("\n" + "=" * 60)
    print("📋 执行汇总")
    print("=" * 60)
    for step_name, success, critical in results:
        if step_name in skips:
            status = "⏭️ SKIPPED"
        else:
            status = "✅" if success else ("❌" if critical else "⚠️(非关键)")
        print(f"  {status} {step_name}")
    for step_name, reason in (skips or {}).items():
        print(f"     ↳ {step_name}: {reason}")

    success_count = sum(1 for _, s, _c in results if s)
    print(f"\n  结果: {success_count}/{len(steps)} 步骤成功")
    print(f"  总耗时: {duration:.1f} 秒")

    # IA-P0-1(AC-11)+FIX-08(IA-DEF-008): 流水线运行台账——步骤状态/失败与SKIPPED
    # 原因/**所使用的研究快照身份(版本+摘要+Gate A)**/是否允许正式报告与回写。
    # 台账为诊断记录: 写入失败仅告警,不改变退出码判定,也不得据此把失败静默记成功。
    ledger_provenance = None
    try:
        sys.path.insert(0, SCRIPTS_DIR)
        import research_provenance as rp
        ymd = start_time.strftime('%Y%m%d')
        snap, why = rp.select_snapshot(ymd, os.path.join(PROJECT_DIR, 'data', 'daily'))
        if snap is not None:
            gate_a, _r = rp.gate_status(snap)
            ledger_provenance = {
                'research_target_date': ymd,
                'snapshot_id': snap.get('snapshot_id'),
                'snapshot_file': os.path.basename(why),
                'snapshot_digest': rp.digest_snapshot(snap),
                'gate_a': gate_a,
                'gate_a_reason': _r or None,
            }
        else:
            ledger_provenance = {'research_target_date': ymd,
                                 'snapshot_id': None, 'snapshot_unavailable_reason': why}
    except Exception as e:
        ledger_provenance = {'snapshot_id': None, 'ledger_provenance_error': str(e)[:200]}
    # 台账放行标志: 正式报告/回写须=快照可用+Gate A允许+**关键步骤全部成功**
    # (FIX2-03: 评分卡是关键步骤,其失败必须传导——评分卡失败而装配/校验因故
    # 仍执行时,allow不得为True;步骤名按尾缀匹配,避免硬编码序号)
    def _step_ok(suffix):
        return any(n.endswith(suffix) and s for n, s, _c in results)
    ledger_provenance['allow_formal_report'] = bool(
        ledger_provenance.get('snapshot_id')
        and ledger_provenance.get('gate_a') in ('PASS', 'DEGRADED')
        and _step_ok('宏观体制评分卡(消费快照)')
        and _step_ok('数据汇总打包') and _step_ok('数据校验与锚点生成'))
    ledger_provenance['allow_state_writeback'] = ledger_provenance['allow_formal_report']
    try:
        log_dir = os.path.join(PROJECT_DIR, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, f"pipeline_run_{start_time.strftime('%Y%m%d')}.json")
        # FIX2-01: 台账原子写(先完整序列化后tmp+replace)——异常不截断既有台账
        _blob = json.dumps({
            'run_at': start_time.isoformat(timespec='seconds'),
            'run_date': start_time.strftime('%Y-%m-%d'),
            'duration_sec': round(duration, 1),
            'steps': [{'name': n, 'ok': bool(s), 'critical': bool(c),
                       'skipped': n in skips,
                       'skip_reason': (skips or {}).get(n)}
                      for n, s, c in results],
            'success_count': success_count,
            **ledger_provenance,
        }, ensure_ascii=False, indent=1)
        _tmp = log_path + '.tmp'
        with open(_tmp, 'w', encoding='utf-8') as f:
            f.write(_blob)
        os.replace(_tmp, log_path)
    except OSError as e:
        print(f"⚠️ 流水线台账写入失败(不影响退出码): {e}")

    # 提示输出文件位置(FIX3-02: 规范文件名口径,排除候选/备份/状态JSON等)
    output_dir = os.path.join(PROJECT_DIR, 'output', 'weekly')
    if os.path.exists(output_dir):
        import research_provenance as rp
        files = rp.weekly_report_files(output_dir)
        if files:
            print(f"\n📄 最新报告: {os.path.join(output_dir, files[-1])}")

    print("\n" + "=" * 60)
    print("📝 下一步：生成周报")
    print("=" * 60)

    # 2026-10-11 P0修复: 任一步骤失败必须以非零退出,否则run_daily.sh拿到RESULT=0,
    # 失败被静默吞掉(此前无论成败永远exit 0)
    # 第五轮P1-2修正: 只有**关键**步骤失败才exit 1 — 非关键失败(新闻/相关性)
    # 降级运行,但仍在汇总中如实公示。
    # IA-P0-1: 关键步骤**被跳过**同样计入失败——依赖未成功时依赖步骤不得静默消失。
    critical_failed = [n for n, s, c in results if not s and c]
    noncritical_failed = [n for n, s, c in results if not s and not c]
    if noncritical_failed:
        print(f"\n⚠️ 非关键步骤降级运行: {', '.join(noncritical_failed)}")
    if critical_failed:
        print(f"\n❌ {len(critical_failed)} 个关键步骤失败或被跳过: {', '.join(critical_failed)}")
        sys.exit(1)
    print("  数据已就绪，请单独运行以下命令生成报告：")
    print("  python3 scripts/report_generator.py")
    print("")
    print("  分开运行可避免超时中断问题。")

    print("\n🎉 完成！")


if __name__ == "__main__":
    main()
