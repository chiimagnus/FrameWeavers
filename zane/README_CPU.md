# 连环画剧本创作系统 - 使用指南

## 快速确认

✅ **你的代码已经完全适配CPU环境！**

- 使用 `opencv-python-headless` 库（无头CPU版本）
- 所有图像处理都在CPU上执行
- 已添加CPU性能优化设置
- 支持多核并发处理
- 适配无头服务器环境（Zeabur、Docker等）

## 🚀 快速开始

### 1. 环境变量配置

```bash
# 复制环境变量模板
cp .env.example .env

# 或使用配置助手
python setup_env.py

# 编辑.env文件，填入你的API密钥
# 必需配置：
# MOONSHOT_API_KEY=sk-your-moonshot-key
# MODELSCOPE_API_KEY=ms-your-modelscope-key  
# OPENAI_API_KEY=sk-your-openai-key
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 验证配置

```bash
# 测试环境变量配置
python test_env_config.py

# 测试OpenCV无头环境
python test_headless.py
```

### 4. 启动服务

```bash
python app.py
```

访问 http://localhost:5000/api/config/status 检查配置状态

## 使用方法

### 1. 基础抽帧（推荐）
```python
from diversity_frame_extractor import DiversityFrameExtractor

# 创建抽帧器
extractor = DiversityFrameExtractor(output_dir="frames")

# 智能抽帧
frames = extractor.extract_uniform_frames(
    video_path="你的视频.mp4",
    target_interval_seconds=1.0  # 每秒一帧
)

print(f"提取了 {len(frames)} 个帧")
```

### 2. AI关键帧筛选
```python
# AI智能筛选关键帧
result = extractor.extract_ai_key_frames(
    video_path="你的视频.mp4",
    target_key_frames=8,  # 最终要8个关键帧
    target_interval_seconds=1.0
)

key_frames = result['key_frame_paths']
print(f"筛选出 {len(key_frames)} 个关键帧")
```

## 性能测试

运行性能测试脚本：
```bash
python test_cpu_performance.py
```

这会测试：
- CPU抽帧性能
- 内存使用情况
- 图像处理速度
- OpenCV后端信息

## CPU优化特性

### 自动优化
- ✅ 启用OpenCV CPU优化指令
- ✅ 自动使用所有CPU核心
- ✅ 根据CPU核心数调整并发数
- ✅ 及时释放图像内存

### 性能预期
| 操作 | 预期性能 |
|------|----------|
| 基础抽帧 | 10-50 帧/秒 |
| 图像读写 | 20-100 帧/秒 |
| AI分析 | 1-5 帧/秒 |

## 故障排除

### 如果性能较慢
1. 检查CPU使用率是否过高
2. 确保有足够的可用内存
3. 减少并发数或抽帧频率
4. 使用SSD存储提高I/O性能

### 如果内存不足
1. 减少目标帧数
2. 增加抽帧间隔
3. 及时清理临时文件
4. 考虑分批处理长视频

## 与GPU版本对比

| 特性 | CPU版本 | GPU版本 |
|------|---------|---------|
| 安装难度 | 简单 | 复杂 |
| 硬件要求 | 低 | 高 |
| 基础抽帧 | 快 | 更快 |
| AI分析 | 相同 | 相同 |
| 兼容性 | 高 | 中等 |

## 总结

你的OpenCV代码已经完全在CPU环境下运行，无需任何修改。添加的优化设置将进一步提升性能。对于大多数视频抽帧任务，CPU版本已经足够高效。