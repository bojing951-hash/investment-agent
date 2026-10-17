"""
一键生成投资周报
串联：全球数据采集 → A股港股采集 → 宏观数据采集 → 数据汇总 → 报告生成
"""

import subprocess
import sys
import os
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


def run_pipeline(steps, script_dir=None):
    """顺序执行步骤(单步失败不阻断后续步骤)。steps=[(名称, 脚本, 关键?)];
    返回[(名称, 成功?, 关键?)]供退出码判定: 只有**关键**步骤失败才使流水线失败,
    非关键失败(新闻/相关性)降级运行,不得阻止行情观察记录。"""
    results = []
    for step_name, script_name, critical in steps:
        success = run_step(step_name, script_name, script_dir=script_dir)
        results.append((step_name, success, critical))
    return results

def main():
    start_time = datetime.now()

    print("=" * 60)
    print("📊 投资周报一键生成")
    print(f"🕐 开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

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
        ("7/11 宏观体制评分卡(消费快照)", "macro_scorecard.py", True),
        # 相关性计算器2026-10-11接线:必须在data_assembler之前跑,汇编器会读取
        # correlation_*.md拼进数据包第五节。非关键: 相关性缺失只降级周报第五节。
        ("8/11 跨资产相关性(消费快照)", "correlation_calculator.py", False),
        ("9/11 数据汇总打包", "data_assembler.py", True),
        ("10/11 数据校验与锚点生成", "data_validator.py", True),
        # 每日预测观察(第四轮P0-6 + 第五轮P1-2): 锚点生成后用Python记录观察期内
        # 预测的当期数据,幂等不调GLM;数据质量门禁FAIL(无当日锚点)时exit 2,
        # 作为关键失败向上传播——采集失败时受影响预测的正式状态不得被更新。
        ("11/11 预测观察记录", "daily_prediction_observer.py", True),
    ]

    results = run_pipeline(steps)

    # 汇总
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\n" + "=" * 60)
    print("📋 执行汇总")
    print("=" * 60)
    for step_name, success, critical in results:
        status = "✅" if success else ("❌" if critical else "⚠️(非关键)")
        print(f"  {status} {step_name}")

    success_count = sum(1 for _, s, _c in results if s)
    print(f"\n  结果: {success_count}/{len(steps)} 步骤成功")
    print(f"  总耗时: {duration:.1f} 秒")

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
    critical_failed = [n for n, s, c in results if not s and c]
    noncritical_failed = [n for n, s, c in results if not s and not c]
    if noncritical_failed:
        print(f"\n⚠️ 非关键步骤降级运行: {', '.join(noncritical_failed)}(不阻止观察记录)")
    if critical_failed:
        print(f"\n❌ {len(critical_failed)} 个关键步骤失败: {', '.join(critical_failed)}")
        sys.exit(1)
    print("  数据已就绪，请单独运行以下命令生成报告：")
    print("  python3 scripts/report_generator.py")
    print("")
    print("  分开运行可避免超时中断问题。")

    print("\n🎉 完成！")


if __name__ == '__main__':
    main()
