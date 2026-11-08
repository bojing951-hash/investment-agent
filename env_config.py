import os

# API Keys — 全部从环境变量或项目根 .env 文件读取,不落盘(开源版已移除原作者的真实key)
# 配置优先级: 进程环境变量 > 项目根 .env 文件(已被 .gitignore 忽略)
# 运行前请配置以下变量(按需,模板见 .env.example):
#   GLM_API_KEY=...      # 智谱GLM,AI周报/AI研究解释必需(数据采集不需要)
#   TUSHARE_TOKEN=...    # tushare Pro,A股数据(可选)
#   FRED_API_KEY=...     # FRED,宏观数据(可选)
#   FINNHUB_API_KEY=...  # Finnhub,新闻/行情(可选)
#
# 安全纪律(2026-11-08 W8):
#   凭证只从本进程环境变量与项目根 .env 读取;
#   不读取任何其他应用(含其他AI助手)的配置文件,不扫描其配置目录;
#   密钥值不打印、不写日志、不入库。


def load_env_file(path=None):
    """读取 KEY=VALUE 格式的 .env 文件,仅对"环境变量中尚不存在"的键生效。

    进程环境变量优先于 .env 文件。解析失败(文件不存在/编码错误)时静默跳过,
    不影响任何现有环境变量。纯标准库实现,不引入 python-dotenv 依赖。
    """
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    try:
        with open(path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if line.startswith('export '):
                    line = line[len('export '):].strip()
                if '=' not in line:
                    continue
                key, _, value = line.partition('=')
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
    except OSError:
        # 文件不存在或不可读:视作未配置,交由各功能的"缺key提示"处理
        pass


# 模块导入时加载一次项目根 .env(进程环境变量优先,不覆盖)
load_env_file()
DEEPSEEK_API_KEY = os.environ.get("ARK_API_KEY", "")
TUSHARE_TOKEN = os.environ.get("TUSHARE_TOKEN", "")
FRED_API_KEY = os.environ.get("FRED_API_KEY", "")

# === 智谱 GLM API 配置(AI周报生成/AI研究解释) ===
GLM_KEY_MISSING_MESSAGE = (
    "未配置 GLM_API_KEY:AI 周报生成与 AI 研究解释不可用。\n"
    "配置方法: 在项目根创建 .env 文件写入 GLM_API_KEY=你的智谱Key(模板见 .env.example),\n"
    "或运行前 export GLM_API_KEY=... 。Key申请: https://open.bigmodel.cn/ \n"
    "数据采集与本地研究查询不需要该Key。\n"
    "(注意: 密钥只从环境变量与项目根 .env 读取,请勿写入代码或提交到git)"
)


def _load_glm_key():
    """GLM凭证唯一来源: GLM_API_KEY 环境变量(含项目根 .env)。

    2026-11-08 W8 收口: 已删除历史上从其他AI应用本机配置文件回退取Key的
    逻辑——不同服务的API Key不可互换,不在用户未明确授权时读取其他
    应用配置文件。无Key返回空串,由调用方给出明确提示。
    """
    return os.environ.get("GLM_API_KEY", "")


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
