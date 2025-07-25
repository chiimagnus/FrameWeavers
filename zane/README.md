# 连环画生成模块 - 视频抽帧功能

## 功能概述

这个模块实现了连环画生成系统的第一步：视频抽帧功能。它可以从上传的视频文件中提取关键帧，为后续的AI分析和连环画生成做准备。

## 主要特性

- **智能关键帧提取**: 基于场景变化检测算法，自动选择8-12个最具代表性的关键帧
- **普通帧提取**: 支持按固定间隔提取视频帧
- **结构化数据输出**: 生成符合需求的JSON格式数据结构
- **视频信息分析**: 获取视频的基本信息（分辨率、时长、帧率等）
- **API接口**: 提供简洁的API接口，方便前端调用

## 文件结构

```
├── video_frame_extractor.py    # 核心抽帧处理类
├── comic_api.py                # API接口封装
├── test_extractor.py           # 测试脚本
├── requirements.txt            # 依赖包列表
├── frames/                     # 提取的帧文件存储目录
├── custom_frames/              # 自定义输出目录示例
└── uploads/                    # 上传文件目录
```

## 安装依赖

```bash
pip install -r requirements.txt
```

或者手动安装：

```bash
pip install opencv-python numpy
```

## 使用方法

### 1. 基本使用

```python
from video_frame_extractor import VideoFrameExtractor

# 创建抽帧器实例
extractor = VideoFrameExtractor()

# 提取关键帧
key_frames = extractor.extract_key_frames("video.mp4", num_key_frames=10)

# 生成连环画数据结构
comic_data = extractor.generate_comic_data("video.mp4")
```

### 2. API接口使用

```python
from comic_api import ComicAPI

# 创建API实例
api = ComicAPI()

# 获取视频信息
video_info = api.get_video_info("video.mp4")

# 处理视频生成连环画数据
result = api.process_video("video.mp4", num_key_frames=10)

if result["success"]:
    comic_data = result["data"]
    # 保存数据
    api.save_comic_data(comic_data, "output.json")
```

### 3. 命令行测试

```bash
# 运行基本测试
python test_extractor.py

# 运行API测试
python comic_api.py

# 直接处理视频
python video_frame_extractor.py
```

## 输出数据结构

生成的JSON数据结构符合需求文档要求：

```json
{
  "comic_id": "comic_20250724_090619",
  "created_at": "2025-07-24T09:06:21.169421",
  "source_video": "测试.mp4",
  "frames": [
    {
      "image_url": "frames/key_frame_00.jpg",
      "narration": "",
      "width": 960,
      "height": 540,
      "index": 0,
      "file_size": 129511
    }
  ],
  "interactive_questions": [],
  "metadata": {
    "total_frames": 10,
    "video_resolution": "960x540",
    "total_size_kb": 1143.59
  }
}
```

## 核心算法

### 关键帧提取算法

1. **场景变化检测**: 计算相邻帧之间的像素差异
2. **时间分段**: 将视频按时间均匀分成N段
3. **最优选择**: 在每个时间段内选择变化最大的帧作为关键帧
4. **去重排序**: 确保选中的关键帧按时间顺序排列

### 参数说明

- `num_key_frames`: 关键帧数量，建议8-12个
- `max_frames`: 普通抽帧的最大帧数
- `output_dir`: 输出目录路径

## API响应格式

### 成功响应
```json
{
  "success": true,
  "data": { /* 连环画数据 */ }
}
```

### 错误响应
```json
{
  "success": false,
  "error": "错误描述",
  "error_code": "ERROR_CODE"
}
```

## 错误代码

- `FILE_NOT_FOUND`: 视频文件不存在
- `INVALID_FRAME_COUNT`: 关键帧数量不在8-12范围内
- `EXTRACTION_FAILED`: 关键帧提取失败
- `PROCESSING_ERROR`: 处理过程中出现错误
- `SAVE_ERROR`: 保存文件失败

## 性能优化

- 使用OpenCV进行高效的视频处理
- 智能的帧间差异计算，避免重复计算
- 内存友好的逐帧处理方式
- 支持自定义输出目录，便于管理

## 后续扩展

当前实现了视频抽帧功能，后续可以扩展：

1. **多模态大模型集成**: 对关键帧进行AI分析和描述
2. **剧本生成**: 基于关键帧描述生成连贯旁白
3. **风格化处理**: 对关键帧进行复古漫画风格处理
4. **互动问题生成**: AI生成与视频内容相关的问题

## 测试结果

使用测试视频（11.27秒，338帧，30fps）的处理结果：
- 成功提取10个关键帧
- 处理时间：< 1秒
- 输出文件大小：约1.1MB
- 数据结构完整，符合需求规范