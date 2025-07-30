# 连环画剧本创作系统

基于AI的智能视频抽帧和故事生成系统，将视频内容转换为连环画剧本。

## ✨ 特性

- 🎬 **智能视频抽帧**: 基于时间均匀分布的智能抽帧算法
- 🤖 **AI关键帧筛选**: 使用AI分析筛选最重要的关键帧
- 📖 **故事生成**: 基于关键帧生成连环画剧本
- 🎨 **风格化处理**: 将图像转换为水墨画风格
- 🚀 **高性能**: 支持异步并发处理，CPU优化
- 🔒 **安全**: 环境变量管理API密钥
- 🐳 **易部署**: 支持Docker和云平台部署

## 🏗️ 系统架构

```
视频上传 → 智能抽帧 → AI分析 → 关键帧筛选 → 故事生成 → 风格化处理
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <your-repo-url>
cd frame-weavers

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填入你的API密钥
nano .env
```

必需的环境变量：
```env
MOONSHOT_API_KEY=sk-your-moonshot-key
MODELSCOPE_API_KEY=ms-your-modelscope-key
OPENAI_API_KEY=sk-your-openai-key
```

### 3. 验证配置

```bash
# 使用配置助手
python setup_env.py

# 或直接测试
python test_env_config.py
```

### 4. 启动服务

```bash
python app.py
```

服务将在 http://localhost:5000 启动

## 📚 API文档

### 基础端点

- `GET /` - 健康检查
- `GET /api/config/status` - 配置状态检查

### 视频处理

- `POST /api/upload/videos` - 上传视频
- `GET /api/task/status/<task_id>` - 查询任务状态
- `POST /api/extract/frames` - 提取视频帧
- `GET /api/frames/<task_id>/<filename>` - 获取帧图像

### 使用示例

```python
import requests

# 1. 上传视频
files = {'videos': open('video.mp4', 'rb')}
data = {'device_id': 'test-device'}
response = requests.post('http://localhost:5000/api/upload/videos', 
                        files=files, data=data)
task_id = response.json()['task_id']

# 2. 提取帧
data = {'task_id': task_id, 'target_frames': 8, 'interval': 1.0}
response = requests.post('http://localhost:5000/api/extract/frames', data=data)

# 3. 查询状态
response = requests.get(f'http://localhost:5000/api/task/status/{task_id}')
```

## 🔧 配置说明

### 性能配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| MAX_CONCURRENT_REQUESTS | 10 | 最大并发请求数 |
| MEMORY_WARNING_THRESHOLD | 80 | 内存警告阈值(%) |
| MAX_MEMORY_USAGE | 90 | 最大内存使用(%) |
| CONNECTION_TIMEOUT | 300 | 连接超时(秒) |
| REQUEST_TIMEOUT | 600 | 请求超时(秒) |

### AI模型配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| DEFAULT_TEMPERATURE | 0.7 | AI生成温度 |
| DEFAULT_MAX_TOKENS | 2000 | 最大Token数 |
| DEFAULT_STYLE_PROMPT | 水墨画风格 | 默认风格提示词 |

## 🐳 部署指南

### Docker部署

```bash
# 构建镜像
docker build -t frame-api .

# 运行容器
docker run --env-file .env -p 5000:5000 frame-api
```

### Zeabur部署

1. 推送代码到Git仓库
2. 在Zeabur连接仓库
3. 设置环境变量
4. 部署应用

详细部署指南：[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

## 🧪 测试

### 运行测试

```bash
# 环境配置测试
python test_env_config.py

# OpenCV无头环境测试
python test_headless.py

# CPU性能测试
python test_cpu_performance.py

# 风格化API测试
python test_style.py
```

### 测试覆盖

- ✅ 环境变量配置
- ✅ 依赖库导入
- ✅ OpenCV功能
- ✅ API密钥验证
- ✅ Flask应用启动
- ✅ 视频抽帧功能
- ✅ AI分析功能

## 📁 项目结构

```
frame-weavers/
├── app.py                      # Flask主应用
├── config.py                   # 配置管理
├── diversity_frame_extractor.py # 视频抽帧核心
├── story_generation_agents.py  # 故事生成
├── requirements.txt            # 依赖列表
├── .env.example               # 环境变量模板
├── Dockerfile                 # Docker配置
├── setup_env.py              # 环境配置助手
├── test_*.py                 # 测试脚本
├── uploads/                  # 上传目录
├── frames/                   # 帧存储目录
└── stories/                  # 故事输出目录
```

## 🔒 安全说明

- ✅ API密钥通过环境变量管理
- ✅ 不在代码中硬编码敏感信息
- ✅ .env文件已加入.gitignore
- ✅ 支持不同环境的不同配置
- ✅ 提供配置验证和状态检查

## 🛠️ 故障排除

### 常见问题

1. **OpenGL库缺失错误**
   - 解决：使用 `opencv-python-headless` 替代 `opencv-python`

2. **环境变量未加载**
   - 检查 `.env` 文件是否存在
   - 运行 `python test_env_config.py` 验证

3. **API密钥无效**
   - 确认密钥格式正确
   - 检查密钥权限和有效期

4. **内存不足**
   - 调整 `MAX_CONCURRENT_REQUESTS` 参数
   - 增加系统内存或使用更小的视频文件

### 获取帮助

- 运行 `python setup_env.py` 获取配置帮助
- 查看 [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) 了解部署详情
- 访问 `/api/config/status` 检查系统状态

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 联系

如有问题，请通过Issue联系我们。