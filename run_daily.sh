#!/bin/bash
# 每日自动数据采集脚本
# 由 launchd 每天 07:00 触发

PROJECT_DIR="$HOME/AI内容/🤖_AI投资项目/每周宏观追踪/investment-agent"
PYTHON="$HOME/AI内容/venv/bin/python3"
LOG_DIR="$PROJECT_DIR/logs"
TODAY=$(date +%Y%m%d)
LOG_FILE="$LOG_DIR/daily_${TODAY}.log"

mkdir -p "$LOG_DIR"

echo "====== 每日采集开始: $(date) ======" >> "$LOG_FILE" 2>&1
echo "Python: $PYTHON" >> "$LOG_FILE" 2>&1
echo "项目: $PROJECT_DIR" >> "$LOG_FILE" 2>&1

cd "$PROJECT_DIR" || { echo "❌ 项目目录不存在" >> "$LOG_FILE"; exit 1; }

# 检查Python是否可用
$PYTHON --version >> "$LOG_FILE" 2>&1 || { echo "❌ Python不可用" >> "$LOG_FILE"; exit 1; }

# 执行8步数据采集
$PYTHON run_weekly.py >> "$LOG_FILE" 2>&1
RESULT=$?

echo "====== 采集结束: $(date), 退出码: $RESULT ======" >> "$LOG_FILE" 2>&1

# 周报生成说明(2026-10-03修正):
# 此前方案是周五在本文本内 nohup 后台启动 report_generator.py —— 实测在 launchd 下失败:
# 主脚本退出时 launchd 收割整个进程组,nohup+disown 救不了(report_20261002.log 只有启动横幅,报告没生成)。
# 现改为独立 launchd 任务 com.investment.weekly.plist(每周五 08:00 直接跑 report_generator.py)。
# 手动出报告随时可跑: python3 scripts/report_generator.py
if [ $RESULT -eq 0 ]; then
    echo "采集完成。周报由 com.investment.weekly 于每周五08:00独立生成。" >> "$LOG_FILE" 2>&1
fi

exit $RESULT
