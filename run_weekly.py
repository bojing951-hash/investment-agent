"""
一键生成投资周报
串联：全球数据采集 → A股港股采集 → 宏观数据采集 → 数据汇总 → 报告生成

IA-P0-1(2026-10-27)失败传播修复:
- 步骤依赖图(4元组,兼容旧3元组): 评分卡/相关性/装配器依赖快照构建;
  校验器依赖装配器;预测观察无依赖——自持门禁(锚点当日+批次核验),
  采集失败不得阻止观察记录(R17既有行为保持);
- 依赖未成功 → 依赖步骤标记SKIPPED并记录原因,不执行危险操作(旧实现无条件
  全部执行: Gate A FAIL后装配器照常打包、校验器照常跑);
- 关键步骤失败或被跳过 → 流水线退出码1(既有行为),跳过原因写入
  logs/pipeline_run_YYYYMMDD.json(AC-11可追溯)。
"""

import subprocess
import sys
import os
import json
from datetime import datetime

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(PROJECT_DIR, 'scripts')

def run_step(step_name, script_name, timeout=900, script_dir=None):
    """运行一个步骤(默认15分钟超时,防止网络挂死堵住launchd——见a_stock_tracker 2026-10-01事故)"""
    print(f"\n{'='*50}")
    print(f"▶ 步骤: {step_name}")
    print(f"{'='*50}")

    script_path = os.path.join(script_dir or SCRIPTS_DIR, script_name)

    if not os.path.exists(script_path):
        print(f"❌ 脚本不存在: {script_path}")
        return False

    try:
        result = subprocess.run(
            [sys.executable, script_path],
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


def run_pipeline(steps, script_dir=None):
    """顺序执行步骤。steps元素为(名称, 脚本, 关键?)或(名称, 脚本, 关键?, 依赖脚本名列表);
    返回PipelineResults([(名称, 成功?, 关键?)])供退出码判定:
    - 只有**关键**步骤失败才使流水线失败;非关键失败(新闻/相关性)降级运行,
      不得阻止行情观察记录;
    - IA-P0-1: 声明了依赖的步骤,任一依赖未成功(失败或自身被跳过)→本步骤
      SKIPPED(结果记False),原因存于.skips并公示——依赖失败后继续跑下游
      只会用未验证数据做危险操作(旧缺陷)。依赖以**脚本名**为标识(步骤显示名
      可变,脚本名稳定),公示时换算回步骤名保持可读。
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
        success = run_step(step_name, script_name, script_dir=script_dir)
        results.append((step_name, success, critical))
        if success:
            ok_scripts.add(script_name)
    return results

def main():
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
    # - 预测观察无依赖(自持门禁): 采集失败当日锚点缺失,观察器自行exit 2,
    #   不得由上游依赖阻止其余资产观察(R17既有约定)。
    _critical_collectors = ["global_market_collector.py", "china_market_collector.py",
                            "macro_collector.py", "rate_expectations.py"]
    _formal_research_deps = ["snapshot_builder.py"] + _critical_collectors
    steps = [
        ("1/11 全球市场数据采集", "global_market_collector.py", True),
        ("2/11 A股港股数据采集", "china_market_collector.py", True),
        ("3/11 宏观数据采集", "macro_collector.py", True),
        # 非关键(第五轮P1-2): 新闻源失败可降级——原始标题缺失只影响周报叙事,
        # 不得阻止行情观察记录;整体退出码不因非关键失败而转失败。
        ("4/11 新闻采集与分析", "news_collector.py", False),
        ("5/11 利率预期与实体经济", "rate_expectations.py", True),
        # 第七轮重构: 采集层之后先建研究快照(唯一数据入口/Gate A),评分卡/相关性/
        # 装配器/校验器均消费快照,不再各自glob"最新文件"或自行拉数(文件最新≠数据最新)。
        ("6/11 研究快照构建(Gate A)", "snapshot_builder.py", True),
        ("7/11 宏观体制评分卡(消费快照)", "macro_scorecard.py", True,
         list(_formal_research_deps)),
        # 相关性计算器2026-10-11接线:必须在data_assembler之前跑,汇编器会读取
        # correlation_*.md拼进数据包第五节。非关键: 相关性缺失只降级周报第五节。
        ("8/11 跨资产相关性(消费快照)", "correlation_calculator.py", False,
         list(_formal_research_deps)),
        ("9/11 数据汇总打包", "data_assembler.py", True,
         list(_formal_research_deps)),
        ("10/11 数据校验与锚点生成", "data_validator.py", True,
         ["data_assembler.py"] + list(_formal_research_deps)),
        # 每日预测观察(第四轮P0-6 + 第五轮P1-2): 锚点生成后用Python记录观察期内
        # 预测的当期数据,幂等不调GLM;数据质量门禁FAIL(无当日锚点)时exit 2,
        # 作为关键失败向上传播——采集失败时受影响预测的正式状态不得被更新。
        ("11/11 预测观察记录", "daily_prediction_observer.py", True),
    ]

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
    # 台账放行标志: 正式报告/回写须=快照可用+Gate A允许+装配与校验两步成功
    # (步骤名按尾缀匹配,避免硬编码序号)
    def _step_ok(suffix):
        return any(n.endswith(suffix) and s for n, s, _c in results)
    ledger_provenance['allow_formal_report'] = bool(
        ledger_provenance.get('snapshot_id')
        and ledger_provenance.get('gate_a') in ('PASS', 'DEGRADED')
        and _step_ok('数据汇总打包') and _step_ok('数据校验与锚点生成'))
    ledger_provenance['allow_state_writeback'] = ledger_provenance['allow_formal_report']
    try:
        log_dir = os.path.join(PROJECT_DIR, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, f"pipeline_run_{start_time.strftime('%Y%m%d')}.json")
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump({
                'run_at': start_time.isoformat(timespec='seconds'),
                'run_date': start_time.strftime('%Y-%m-%d'),
                'duration_sec': round(duration, 1),
                'steps': [{'name': n, 'ok': bool(s), 'critical': bool(c),
                           'skipped': n in skips,
                           'skip_reason': (skips or {}).get(n)}
                          for n, s, c in results],
                'success_count': success_count,
                **ledger_provenance,
            }, f, ensure_ascii=False, indent=1)
    except OSError as e:
        print(f"⚠️ 流水线台账写入失败(不影响退出码): {e}")

    # 提示输出文件位置
    output_dir = os.path.join(PROJECT_DIR, 'output', 'weekly')
    if os.path.exists(output_dir):
        files = sorted(os.listdir(output_dir), reverse=True)
        if files:
            print(f"\n📄 最新报告: {os.path.join(output_dir, files[0])}")

    print("\n" + "=" * 60)
    print("📝 下一步：生成周报")
    print("=" * 60)

    # 2026-10-11 P0修复: 任一步骤失败必须以非零退出,否则run_daily.sh拿到RESULT=0,
    # 失败被静默吞掉(此前无论成败永远exit 0)
    # 第五轮P1-2修正: 只有**关键**步骤失败才exit 1 — 非关键失败(新闻/相关性)
    # 降级运行且不阻止行情观察记录,但仍在汇总中如实公示。
    # IA-P0-1: 关键步骤**被跳过**同样计入失败——依赖未成功时依赖步骤不得静默消失。
    critical_failed = [n for n, s, c in results if not s and c]
    noncritical_failed = [n for n, s, c in results if not s and not c]
    if noncritical_failed:
        print(f"\n⚠️ 非关键步骤降级运行: {', '.join(noncritical_failed)}(不阻止观察记录)")
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
