# 部署指南 - 环境变量配置

## 概述

本项目已将所有API密钥和敏感信息迁移到环境变量中，提高了安全性和部署灵活性。

## 🔧 本地开发设置

### 1. 创建环境变量文件

```bash
# 复制示例文件
cp .env.example .env

# 或使用设置助手
python setup_env.py
```

### 2. 编辑.env文件

打开`.env`文件，将示例值替换为你的真实API密钥：

```env
# Moonshot AI (Kimi) API配置
MOONSHOT_API_KEY=sk-your-actual-moonshot-key-here

# ModelScope风格化处理API配置  
MODELSCOPE_API_KEY=ms-your-actual-modelscope-key-here

# OpenAI兼容API配置（用于视频帧分析）
OPENAI_API_KEY=sk-your-actual-openai-key-here
```

### 3. 验证配置

```bash
# 验证环境变量设置
python setup_env.py

# 或直接测试配置
python -c "from config import validate_config; validate_config()"
```

## 🚀 Zeabur部署

### 1. 环境变量设置

在Zeabur控制台中设置以下环境变量：

#### 必需变量
```
MOONSHOT_API_KEY=sk-your-moonshot-key
MODELSCOPE_API_KEY=ms-your-modelscope-key  
OPENAI_API_KEY=sk-your-openai-key
```

#### 可选变量
```
IMGBB_API_KEY=your-imgbb-key
GITHUB_TOKEN=your-github-token
GITHUB_REPO_OWNER=your-username
GITHUB_REPO_NAME=your-repo-name
```

#### 性能配置（可选）
```
MAX_CONCURRENT_REQUESTS=10
MEMORY_WARNING_THRESHOLD=80
MAX_MEMORY_USAGE=90
CONNECTION_TIMEOUT=300
REQUEST_TIMEOUT=600
```

### 2. 部署步骤

1. **推送代码**到Git仓库
2. **在Zeabur中连接**你的仓库
3. **设置环境变量**（如上所示）
4. **触发部署**

### 3. 验证部署

部署成功后，访问以下端点验证：
- `GET /` - 健康检查
- `GET /api/config/status` - 配置状态检查

## 🐳 Docker部署

### 1. 使用环境变量文件

```bash
# 创建.env文件（如上所示）
docker build -t frame-api .
docker run --env-file .env -p 5000:5000 frame-api
```

### 2. 直接传递环境变量

```bash
docker run -e MOONSHOT_API_KEY=sk-your-key \
           -e MODELSCOPE_API_KEY=ms-your-key \
           -e OPENAI_API_KEY=sk-your-key \
           -p 5000:5000 frame-api
```

## 🔒 安全最佳实践

### 1. 密钥管理
- ✅ 使用强密钥，定期更换
- ✅ 不要在代码中硬编码密钥
- ✅ 不要将.env文件提交到版本控制
- ✅ 使用不同环境的不同密钥

### 2. 权限控制
- ✅ 为API密钥设置最小必要权限
- ✅ 监控API使用情况
- ✅ 设置使用限制和告警

### 3. 环境隔离
- ✅ 开发/测试/生产环境使用不同密钥
- ✅ 使用环境特定的配置文件
- ✅ 定期审查和更新配置

## 🛠️ 故障排除

### 常见问题

#### 1. 环境变量未加载
```bash
# 检查.env文件是否存在
ls -la .env

# 验证环境变量
python -c "import os; print(os.getenv('MOONSHOT_API_KEY'))"
```

#### 2. API密钥无效
```bash
# 测试配置
python setup_env.py

# 检查配置验证
python -c "from config import validate_config; validate_config()"
```

#### 3. 部署时环境变量缺失
- 确认在部署平台正确设置了环境变量
- 检查变量名是否正确（区分大小写）
- 验证变量值没有多余的空格或引号

### 调试命令

```bash
# 显示所有环境变量
env | grep -E "(MOONSHOT|MODELSCOPE|OPENAI)"

# 测试配置导入
python -c "from config import *; print('配置加载成功')"

# 运行完整测试
python test_headless.py
```

## 📝 环境变量参考

### API配置
| 变量名 | 必需 | 描述 | 示例 |
|--------|------|------|------|
| MOONSHOT_API_KEY | ✅ | Moonshot AI API密钥 | sk-xxx |
| MODELSCOPE_API_KEY | ✅ | ModelScope API密钥 | ms-xxx |
| OPENAI_API_KEY | ✅ | OpenAI兼容API密钥 | sk-xxx |
| IMGBB_API_KEY | ⚪ | 图床API密钥 | xxx |

### 性能配置
| 变量名 | 默认值 | 描述 |
|--------|--------|------|
| MAX_CONCURRENT_REQUESTS | 10 | 最大并发请求数 |
| MEMORY_WARNING_THRESHOLD | 80 | 内存警告阈值(%) |
| MAX_MEMORY_USAGE | 90 | 最大内存使用(%) |
| CONNECTION_TIMEOUT | 300 | 连接超时(秒) |
| REQUEST_TIMEOUT | 600 | 请求超时(秒) |

## 🎯 总结

通过环境变量配置，你的应用现在：
- ✅ 更安全（密钥不在代码中）
- ✅ 更灵活（不同环境不同配置）
- ✅ 更易部署（支持各种部署平台）
- ✅ 更易维护（集中配置管理）

如有问题，请参考故障排除部分或运行`python setup_env.py`获取帮助。