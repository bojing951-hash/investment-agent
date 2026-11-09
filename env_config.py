import os
import sys

# API Keys — 全部从环境变量或项目根 .env 文件读取,不落盘(开源版已移除原作者的真实key)
# 配置优先级: 进程环境变量 > 项目根 .env 文件(已被 .gitignore 忽略)
# 运行前请配置以下变量(按需,模板见 .env.example):
#   MODEL_API_KEY=...    # 可选通用模型 API(任意 OpenAI 兼容端点);Agent Native 模式不需要
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
TUSHARE_TOKEN = os.environ.get("TUSHARE_TOKEN", "")
FRED_API_KEY = os.environ.get("FRED_API_KEY", "")

# === 遗留弃用(G1.1, 2026-11-09 Model-Agnostic v2) ==========================
# DEEPSEEK_API_KEY 曾死绑 ARK_API_KEY(火山引擎DeepSeek,通道早已下线)——该绑定
# 已删除。三常量保留空值仅为 daily_report_generator.py(遗留弃用入口,不在任何
# 活跃流水线,见其文件头声明)可导入;不得在新代码中使用。
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "")

# === 通用模型 API 配置(Model-Agnostic v2, 2026-11-09) ======================
# 三参 MODEL_API_KEY / MODEL_BASE_URL / MODEL_NAME,默认空 = Agent Native 模式:
# 不配置模型 Key,本地能力(采集/研究问答/工作台/确定性周报)全部可用。
# 任意 OpenAI 兼容端点均可;金融数据源 Key(FRED/tushare/Finnhub)与模型 Key
# 相互独立。智谱预设(历史默认值,已降级为可选预设注释,不再硬编码为默认;
# 如需沿用请显式配置):
#   MODEL_BASE_URL=https://open.bigmodel.cn/api/paas/v4
#   MODEL_NAME=glm-5.3
ZHIPU_PRESET_BASE_URL = 'https://open.bigmodel.cn/api/paas/v4'
ZHIPU_PRESET_MODEL = 'glm-5.3'

MODEL_KEY_MISSING_MESSAGE = (
    "未配置模型 API(可选): 解释层(AI 周报解释/研究 AI 解释)不可用,"
    "系统自动走确定性分支(数据观察周报/确定性标题/如实提示)。\n"
    "配置方法: 在项目根 .env 写入 MODEL_API_KEY/MODEL_BASE_URL/MODEL_NAME 三项"
    "(任意 OpenAI 兼容端点,模板见 .env.example),或运行前逐项 export。\n"
    "可选通用模型 API(任意 OpenAI 兼容端点);Agent Native 模式(默认)不需要"
    "模型 Key;数据采集与本地研究查询也不需要。\n"
    "(注意: 密钥只从环境变量与项目根 .env 读取,请勿写入代码或提交到git)"
)
# 旧常量名兼容别名(历史调用方仍在读;文本已中性化)
GLM_KEY_MISSING_MESSAGE = MODEL_KEY_MISSING_MESSAGE

_legacy_fallback_notice_printed = False


def model_runtime_config():
    """模型 API 三参解析(唯一权威入口;G1.2 条件回退含安全约束)。

    读序: MODEL_API_KEY/MODEL_BASE_URL/MODEL_NAME 优先 → 旧 GLM_* 别名回退。
    回退安全约束(G1.2, 防跨服务 Key 外送): 仅当 MODEL_API_KEY 未设时才考虑
    回退读 GLM_API_KEY,且仅当 MODEL_BASE_URL 未设(或旧 GLM_BASE_URL=智谱预设)
    时才允许该回退——用户显式设了第三方 BASE_URL 而只留旧 GLM Key 时绝不回退,
    按未配置处理。发生回退时向 stderr 打一行迁移提示(每进程至多一次)。
    智谱预设 URL/模型名仅随旧 GLM Key 回退自动套用(保持历史行为);
    显式 MODEL_* 路径无任何硬编码默认,缺任一参数即视为未配置
    (调用点缺任一参数→走无模型分支,不发起调用)。

    返回 dict: {api_key, base_url, model, complete(三参齐备才True),
    legacy_fallback(凭证来自旧 GLM_API_KEY), blocked_reason(可读原因或'')}
    """
    global _legacy_fallback_notice_printed
    m_key = os.environ.get('MODEL_API_KEY', '').strip()
    m_url = os.environ.get('MODEL_BASE_URL', '').strip()
    m_name = os.environ.get('MODEL_NAME', '').strip()
    g_key = os.environ.get('GLM_API_KEY', '').strip()
    g_url = os.environ.get('GLM_BASE_URL', '').strip()
    g_model = os.environ.get('GLM_MODEL', '').strip()

    api_key, base_url, model = m_key, (m_url or g_url), (m_name or g_model)
    legacy_fallback = False
    blocked_reason = ''
    if not m_key and g_key:
        # G1.2: 生效 BASE_URL(MODEL_* 或旧 GLM_*)显式指向第三方(≠未设/≠智谱
        # 预设)时禁止回退——旧 GLM Key 只允许发往智谱端点,防跨服务 Key 外送
        eff_url = m_url or g_url
        third_party = bool(eff_url) and eff_url != ZHIPU_PRESET_BASE_URL
        if third_party:
            blocked_reason = ('生效 MODEL_BASE_URL(或旧 GLM_BASE_URL)已显式设为'
                              '第三方端点,而 MODEL_API_KEY 未配置——旧 GLM_API_KEY '
                              '不跨服务回退(防 Key 外送),请为该端点配置对应的 '
                              'MODEL_API_KEY')
        else:
            api_key = g_key
            legacy_fallback = True
            if not base_url:
                base_url = ZHIPU_PRESET_BASE_URL   # 仅随旧 GLM 回退套用历史预设
            if not model:
                model = ZHIPU_PRESET_MODEL
            if not _legacy_fallback_notice_printed:
                _legacy_fallback_notice_printed = True
                print('使用旧变量 GLM_API_KEY,建议迁移到 MODEL_API_KEY',
                      file=sys.stderr)
    complete = bool(api_key and base_url and model)
    return {'api_key': api_key, 'base_url': base_url, 'model': model,
            'complete': complete, 'legacy_fallback': legacy_fallback,
            'blocked_reason': blocked_reason}


_cfg = model_runtime_config()
MODEL_API_KEY = _cfg['api_key']
MODEL_BASE_URL = _cfg['base_url']
MODEL_NAME = _cfg['model']

# 旧名兼容别名(读序内含 GLM_* 回退;GLM_BASE_URL/GLM_MODEL 不再硬编码智谱值,
# 智谱预设见上方注释与 ZHIPU_PRESET_* 常量)
GLM_API_KEY = os.environ.get('GLM_API_KEY', '')
GLM_BASE_URL = MODEL_BASE_URL
GLM_MODEL = MODEL_NAME

# 数据存储路径
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
CONFIG_DIR = os.path.join(PROJECT_ROOT, "config")

# === Finnhub API 配置 ===
FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY", "")
