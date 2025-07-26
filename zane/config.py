"""
连环画剧本创作系统配置文件
"""

import os

# Moonshot AI (Kimi) API配置
MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY", "sk-nGQ50WHDiQYGkOP66oRpJcEnPIOuu3zgFh4bM7qqkcuXs9Th")
MOONSHOT_BASE_URL = "https://api.moonshot.cn/v1"
MOONSHOT_MODEL = "kimi-k2-0711-preview"

# 系统配置
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 2000

# 日志配置
LOG_LEVEL = "INFO"

# 备用配置（当主API不可用时）
ENABLE_FALLBACK = True
FALLBACK_DELAY = 2.0  # 秒

# ModelScope风格化处理API配置
MODELSCOPE_API_URL = "https://api-inference.modelscope.cn/v1/images/generations"
MODELSCOPE_API_KEY = "ms-a2eb2a0e-dded-42eb-b41c-835e3bd447b7"
MODELSCOPE_MODEL = "black-forest-labs/FLUX.1-Kontext-dev"

# 风格化处理默认配置
DEFAULT_STYLE_PROMPT = "Convert to Ink and brushwork style, Chinese style, Yellowed and old, Low saturation, Low brightness"
DEFAULT_IMAGE_SIZE = "1920x1024"
STYLE_PROCESSING_TIMEOUT = 120  # 秒