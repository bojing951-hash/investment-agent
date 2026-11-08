#!/bin/bash
# 每日自动数据采集入口(可移植版,2026-11-08 W7: 不再硬编码任何个人路径)
#
# 用法:
#   bash run_daily.sh                    # 自动探测: 项目内虚拟环境 > 系统 python3
#   PYTHON=/path/to/python3 bash run_daily.sh        # 显式指定解释器(优先级最高)
#   IA_PROJECT_DIR=/path/to/repo bash run_daily.sh   # 显式指定项目根(默认=脚本所在目录)
#
# 调度: macOS 可用 launchd(参考 docs/USER_GUIDE.md),Linux 可用 cron,Windows 可用任务计划
# 程序直接调用 run_weekly.py。脚本本身只做: 定位项目根 → 定位Python → 日志 → 执行 → 透传退出码。

# 项目根 = 本脚本所在目录(可在任意路径克隆/软链;不依赖原作者目录结构)
# dirname 结果兜底为'.'——PATH 残缺时 dirname 可能不可用返回空串,而 cd '' 在
# bash>=5.3 是错误(POSIX 收紧),空转 '.' 保证任何 bash 版本下路径解析可完成
SCRIPT_SOURCE="${BASH_SOURCE[0]:-$0}"
SCRIPT_DIR="$(dirname "$SCRIPT_SOURCE" 2>/dev/null || true)"
PROJECT_DIR="$(cd "${SCRIPT_DIR:-.}" && pwd)"
if [ -n "${IA_PROJECT_DIR:-}" ]; then
    PROJECT_DIR="$IA_PROJECT_DIR"
fi

# 目录存在性检查须在写日志之前——IA_PROJECT_DIR 指错时不产生任何副作用
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ 项目目录不存在: $PROJECT_DIR" >&2
    exit 1
fi

# Python 解释器定位: PYTHON环境变量 > 项目内 .venv/venv > 系统 PATH 中的 python3
PYTHON="${PYTHON:-}"
if [ -z "$PYTHON" ]; then
    for _cand in "$PROJECT_DIR/.venv/bin/python3" "$PROJECT_DIR/venv/bin/python3"; do
        if [ -x "$_cand" ]; then
            PYTHON="$_cand"
            break
        fi
    done
fi
if [ -z "$PYTHON" ]; then
    if command -v python3 >/dev/null 2>&1; then
        PYTHON="$(command -v python3)"
    fi
fi

# 日志机制(与原版一致: 追加写 logs/daily_YYYYMMDD.log;结构化台账另由
# run_weekly.py 写 logs/pipeline_run_YYYYMMDD.json)
LOG_DIR="$PROJECT_DIR/logs"
TODAY=$(date +%Y%m%d)
LOG_FILE="$LOG_DIR/daily_${TODAY}.log"
mkdir -p "$LOG_DIR"

echo "====== 每日采集开始: $(date) ======" >> "$LOG_FILE" 2>&1
echo "Python: ${PYTHON:-<未找到>}" >> "$LOG_FILE" 2>&1
echo "项目: $PROJECT_DIR" >> "$LOG_FILE" 2>&1

# 检查Python是否可用(缺失时给出可照做的修复指引,退出码127=命令未找到;
# 指引用echo内建输出——即使PATH残缺也保证提示可达用户)
if [ -z "$PYTHON" ]; then
    echo "❌ 未找到可用的 Python 解释器。请任选其一:" >&2
    echo "   1) 在项目根创建虚拟环境(推荐):" >&2
    echo "      python3 -m venv .venv && .venv/bin/pip install -r requirements.txt" >&2
    echo "   2) 运行前显式指定: PYTHON=/path/to/python3 bash run_daily.sh" >&2
    echo "   详见 docs/USER_GUIDE.md「安装」一章。" >&2
    echo "❌ 未找到Python解释器(修复指引见stderr)" >> "$LOG_FILE" 2>&1
    exit 127
fi
$PYTHON --version >> "$LOG_FILE" 2>&1 || { echo "❌ Python不可用: $PYTHON" >> "$LOG_FILE" 2>&1; exit 1; }

# 执行数据采集流水线(run_weekly.py 现为13步: 9关键/4非关键;关键步骤失败→退出码1,
# 各步骤语义与依赖见 run_weekly.py steps 注释)
cd "$PROJECT_DIR" || { echo "❌ 无法进入项目目录: $PROJECT_DIR" >> "$LOG_FILE" 2>&1; exit 1; }
"$PYTHON" run_weekly.py >> "$LOG_FILE" 2>&1
RESULT=$?

echo "====== 采集结束: $(date), 退出码: $RESULT ======" >> "$LOG_FILE" 2>&1

# 周报生成说明(2026-10-03修正,2026-11-08 W7随可移植化保留):
# 不在本文本内 nohup 后台启动 report_generator.py——launchd 下主脚本退出会收割
# 整个进程组,后台子进程无法存活。周报生成独立调度(macOS: com.investment.weekly
# 每周六08:00;其他平台见 docs/USER_GUIDE.md「日常使用」),手动出报告随时可跑:
#   python3 scripts/report_generator.py
if [ $RESULT -eq 0 ]; then
    echo "采集完成。周报生成请独立运行: python3 scripts/report_generator.py (详见docs/USER_GUIDE.md)" >> "$LOG_FILE" 2>&1
fi

exit $RESULT
