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