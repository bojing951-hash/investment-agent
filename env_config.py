import os

# API Keys — 全部从环境变量读取,不落盘(开源版已移除原作者的真实key)
# 运行前请 export 以下变量(按需):
#   export GLM_API_KEY=...      # 智谱GLM,周报生成必需
#   export TUSHARE_TOKEN=...    # tushare Pro,A股数据(可选)
#   export FRED_API_KEY=...     # FRED,宏观数据(可选)
#   export FINNHUB_API_KEY=...  # Finnhub,新闻/行情(可选)
DEEPSEEK_API_KEY = os.environ.get("ARK_API_KEY", "")
TUSHARE_TOKEN = os.environ.get("TUSHARE_TOKEN", "")
FRED_API_KEY = os.environ.get("FRED_API_KEY", "")

# === 智谱 GLM API 配置(周报生成) ===
def _load_glm_key():
    env_key = os.environ.get("GLM_API_KEY")
    if env_key:
        return env_key
    # 兼容原部署:本机 Claude 配置中的智谱 key(仅限原部署机器,开源环境请用环境变量)
    try:
        import json
        with open(os.path.expanduser("~/.claude/settings.json")) as f:
            return json.load(f).get("env", {}).get("ANTHROPIC_API_KEY", "")
    except Exception:
        return ""

GLM_API_KEY = _load_glm_key()
# v4 OpenAI兼容通道 + 流式 + reasoning_effort=low(完整方案见report_generator._call_glm注释)
GLM_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
GLM_MODEL = "glm-5.3"

# 数据存储路径
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
CONFIG_DIR = os.path.join(PROJECT_ROOT, "config")

# === Finnhub API 配置 ===
FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY", "")
