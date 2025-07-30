"""
连环画剧本创作系统配置文件
"""

import os

# Moonshot AI (Kimi) API配置 - 已弃用，改用DeepSeek
MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY", "sk-nGQ50WHDiQYGkOP66oRpJcEnPIOuu3zgFh4bM7qqkcuXs9Th")
MOONSHOT_BASE_URL = "https://api.moonshot.cn/v1"
MOONSHOT_MODEL = "kimi-k2-0711-preview"

# DeepSeek API配置 - 新的主要LLM服务
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-93d348fe6f67439ba9d69d5a533bf979")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL = "deepseek-chat"

# 系统配置
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 2000

# 日志配置
LOG_LEVEL = "INFO"

# 备用配置（当主API不可用时）
ENABLE_FALLBACK = True
FALLBACK_DELAY = 2.0  # 秒


# 图床API配置
IMGBB_API_KEY=os.getenv("IMGBB_API_KEY", "your-imgbb-api-key-here")
IMGBB_UPLOAD_URL=os.getenv("IMGBB_UPLOAD_URL", "https://tuchuan.zeabur.app/api/upload")


# ModelScope风格化处理API配置
MODELSCOPE_API_URL = "https://api-inference.modelscope.cn/v1/images/generations"
MODELSCOPE_API_KEY = "ms-a2eb2a0e-dded-42eb-b41c-835e3bd447b7"
MODELSCOPE_MODEL = "black-forest-labs/FLUX.1-Kontext-dev"

# 风格化处理默认配置
DEFAULT_STYLE_PROMPT = "Convert to Ink and brushwork style, Chinese style, Yellowed and old, Low saturation, Low brightness"
DEFAULT_IMAGE_SIZE = "1780x1024"
STYLE_PROCESSING_TIMEOUT = 3000  # 秒

# 性能和稳定性配置
MAX_CONCURRENT_REQUESTS = 40  # 降低默认并发数量（原来50，现在10）
MEMORY_WARNING_THRESHOLD = 80  # 内存使用超过80%时发出警告
MAX_MEMORY_USAGE = 90  # 内存使用超过90%时停止处理
CONNECTION_TIMEOUT = 3000  # 连接超时时间（秒）
REQUEST_TIMEOUT = 6000  # 请求超时时间（秒）