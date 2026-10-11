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

def run_step(step_name, script_name, timeout=900):
    """运行一个步骤(默认15分钟超时,防止网络挂死堵住launchd——见a_stock_tracker 2026-10-01事故)"""
    print(f"\n{'='*50}")
    print(f"▶ 步骤: {step_name}")
    print(f"{'='*50}")

    script_path = os.path.join(SCRIPTS_DIR, script_name)

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

if __name__ == '__main__':
    start_time = datetime.now()

    print("=" * 60)
    print("📊 投资周报一键生成")
    print(f"🕐 开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    steps = [
        ("1/9 全球市场数据采集", "global_market_collector.py"),
        ("2/9 A股港股数据采集", "china_market_collector.py"),
        ("3/9 宏观数据采集", "macro_collector.py"),
        ("4/9 新闻采集与分析", "news_collector.py"),
        ("5/9 利率预期与实体经济", "rate_expectations.py"),
        ("6/9 宏观体制评分卡", "macro_scorecard.py"),
        # 相关性计算器2026-10-11接线:此前脚本存在但从未进流水线,相关性数据停在2026-04-09。
        # 必须在data_assembler(第8步)之前跑,汇编器会读取correlation_*.md拼进数据包第五节。
        ("7/9 跨资产相关性计算", "correlation_calculator.py"),
        ("8/9 数据汇总打包", "data_assembler.py"),
        ("9/9 数据校验与锚点生成", "data_validator.py"),
    ]

    results = []
    for step_name, script_name in steps:
        success = run_step(step_name, script_name)
        results.append((step_name, success))

    # 汇总
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\n" + "=" * 60)
    print("📋 执行汇总")
    print("=" * 60)
    for step_name, success in results:
        status = "✅" if success else "❌"
        print(f"  {status} {step_name}")

    success_count = sum(1 for _, s in results if s)
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
    if success_count < len(steps):
        failed = [n for n, s in results if not s]
        print(f"\n❌ {len(steps) - success_count} 步失败: {', '.join(failed)}")
        sys.exit(1)
    print("  数据已就绪，请单独运行以下命令生成报告：")
    print("  python3 scripts/report_generator.py")
    print("")
    print("  分开运行可避免超时中断问题。")

    print("\n🎉 完成！")
