# 帧织者API文档

## 概述

本文档详细说明了帧织者系统的API接口，供前端开发人员调用。系统提供视频上传、基础帧提取、关键帧提取、风格化处理等功能，支持异步处理和状态查询。

**支持的视频格式**: mp4, mov, avi, mkv, wmv, flv, 3gp
**文件大小限制**: 单个文件最大800MB

## 基础信息

- **基础URL**: `http://服务器地址:5001`
- **响应格式**: 所有API返回JSON格式数据
- **状态码**:
  - 200: 请求成功
  - 400: 请求参数错误
  - 404: 资源不存在
  - 413: 上传文件过大
  - 500: 服务器内部错误

## API接口列表

系统共提供14个API接口，包括视频处理、任务管理、故事生成、风格化处理和错误处理等功能。

### 1. 视频上传

上传一个或多个视频文件，开始处理流程。

- **URL**: `/api/upload/videos`
- **方法**: `POST`
- **Content-Type**: `multipart/form-data`

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| device_id | string | 是 | 设备唯一标识码 |
| videos | file[] | 是 | 要上传的视频文件，支持多文件 |

**响应示例**:

```json
{
  "success": true,
  "message": "视频上传成功",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "device_id": "device_123456",
  "uploaded_files": 2,
  "invalid_files": null
}
```

### 2. 获取任务状态

查询指定任务的处理状态和进度。

- **URL**: `/api/task/status/<task_id>`
- **方法**: `GET`

**路径参数**:

| 参数名 | 类型 | 描述 |
|--------|------|------|
| task_id | string | 任务ID |

**响应示例**:

```json
{
  "success": true,
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "message": "正在处理第 1/2 个视频...",
  "progress": 50,
  "device_id": "device_123456",
  "created_at": "2023-10-15T14:30:15.123456"
}
```

**可能的任务状态**:

- `uploaded`: 视频已上传，等待处理
- `processing`: 正在处理中
- `extracting_base_frames`: 正在提取基础帧
- `base_frames_extracted`: 基础帧提取完成
- `extracting_key_frames`: 正在提取关键帧
- `unified_processing`: 正在进行统一智能处理
- `style_processing`: 正在进行风格化处理
- `style_completed`: 风格化处理完成
- `completed`: 处理完成
- `error`: 处理出错
- `cancelled`: 任务已取消

**注意**: `generating_story` 状态已移除，因为故事生成现在是同步处理。

### 3. 取消任务

取消正在进行的任务。

- **URL**: `/api/task/cancel/<task_id>`
- **方法**: `POST`

**路径参数**:

| 参数名 | 类型 | 描述 |
|--------|------|------|
| task_id | string | 任务ID |

**响应示例**:

```json
{
  "success": true,
  "message": "任务已取消"
}
```

### 4. 获取设备任务历史

获取指定设备的所有任务历史记录。

- **URL**: `/api/device/<device_id>/tasks`
- **方法**: `GET`

**路径参数**:

| 参数名 | 类型 | 描述 |
|--------|------|------|
| device_id | string | 设备唯一标识码 |

**响应示例**:

```json
{
  "success": true,
  "device_id": "device_123456",
  "tasks": [
    {
      "task_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "completed",
      "message": "处理完成",
      "progress": 100,
      "created_at": "2023-10-15T14:30:15.123456",
      "file_count": 2
    },
    {
      "task_id": "550e8400-e29b-41d4-a716-446655440001",
      "status": "error",
      "message": "处理失败: 文件格式不支持",
      "progress": 30,
      "created_at": "2023-10-14T10:20:15.123456",
      "file_count": 1
    }
  ],
  "total_tasks": 2
}
```

### 5. 基础帧提取

从已上传的视频中提取基础帧。

- **URL**: `/api/extract/base-frames`
- **方法**: `POST`
- **Content-Type**: `application/x-www-form-urlencoded`

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| task_id | string | 是 | 任务ID |
| interval | float | 否 | 抽帧时间间隔（秒），默认1.0秒 |

**响应示例**:

```json
{
  "success": true,
  "message": "基础帧提取成功",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "results": [
    {
      "video_name": "我的视频.mp4",
      "base_frames_count": 30,
      "base_frames_paths": [
        "/path/to/frame1.jpg",
        "/path/to/frame2.jpg",
        "..."
      ],
      "output_dir": "/path/to/frames/directory"
    }
  ]
}
```

### 6. 关键帧提取

从基础帧中提取关键帧。

- **URL**: `/api/extract/key-frames`
- **方法**: `POST`
- **Content-Type**: `application/x-www-form-urlencoded`

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| task_id | string | 是 | 任务ID |
| target_frames | int | 否 | 目标关键帧数量，默认8个 |
| significance_weight | float | 否 | 重要性权重(0-1)，默认0.6 |
| quality_weight | float | 否 | 质量权重(0-1)，默认0.4 |
| max_concurrent | int | 否 | 最大并发数，默认50 |

**响应示例**:

```json
{
  "success": true,
  "message": "关键帧提取成功",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "results": [
    {
      "video_name": "我的视频.mp4",
      "base_frames_count": 30,
      "key_frames_count": 8,
      "key_frames_paths": [
        "/path/to/key_frame1.jpg",
        "/path/to/key_frame2.jpg",
        "..."
      ],
      "json_file_path": "/path/to/keyframes_info.json",
      "output_dir": "/path/to/frames/directory"
    }
  ]
}
```

### 7. 统一智能处理

一键完成从视频到关键帧的全流程处理。

- **URL**: `/api/process/unified`
- **方法**: `POST`
- **Content-Type**: `application/x-www-form-urlencoded`

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| task_id | string | 是 | 任务ID |
| target_frames | int | 否 | 目标关键帧数量，默认8个 |
| interval | float | 否 | 基础帧抽取间隔（秒），默认1.0秒 |
| significance_weight | float | 否 | 重要性权重(0-1)，默认0.6 |
| quality_weight | float | 否 | 质量权重(0-1)，默认0.4 |
| max_concurrent | int | 否 | 最大并发数，默认50 |

**响应示例**:

```json
{
  "success": true,
  "message": "统一智能处理成功",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "results": [
    {
      "video_name": "我的视频.mp4",
      "base_frames_count": 30,
      "key_frames_count": 8,
      "key_frame_paths": [
        "/path/to/unified_key_00.jpg",
        "/path/to/unified_key_01.jpg",
        "..."
      ],
      "json_file_path": "/path/to/keyframes_info.json",
      "output_dir": "/path/to/frames/directory",
      "processing_stats": {
        "total_processing_time": 45.2,
        "base_frames_count": 30,
        "key_frames_count": 8,
        "average_significance_score": 0.75,
        "average_quality_score": 0.82,
        "processing_speed": 0.66
      }
    }
  ]
}
```

### 8. 获取帧图像

获取指定任务的帧图像。

- **URL**: `/api/frames/<task_id>/<filename>`
- **方法**: `GET`

**路径参数**:

| 参数名 | 类型 | 描述 |
|--------|------|------|
| task_id | string | 任务ID |
| filename | string | 图像文件名 |

**响应**:
成功时返回图像文件，失败时返回JSON错误信息。

### 9. 三阶段故事生成（同步）

基于关键帧数据生成完整的故事内容。此API为同步处理，直接返回生成结果。

- **URL**: `/api/generate/story`
- **方法**: `POST`
- **Content-Type**: `application/json`

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| video_info | object | 是 | 视频信息对象 |
| keyframes | array | 是 | 关键帧数据数组 |
| style | string | 否 | 文体风格参数，用于指定故事的创作风格 |

**请求示例**:

```json
{
  "video_info": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "video_name": "我的视频.mp4",
    "video_path": "uploads/20231015_143015_我的视频.mp4",
    "processing_time": "2023-10-15T14:30:15.123456",
    "total_keyframes": 8
  },
  "keyframes": [
    {
      "index": 1,
      "filename": "unified_key_00.jpg",
      "photo_path": "frames/task_123_video/unified_key_00.jpg",
      "combined_score": 0.85,
      "significance_score": 0.8,
      "quality_score": 0.9,
      "description": "一个阳光明媚的早晨，主人公走出家门，脸上带着期待的笑容",
      "timestamp": 0.0,
      "frame_position": 0
    }
  ],
  "style": "古典诗意"
}
```

**style参数说明**:
- `古典诗意`: 采用古典文学的优美词汇和意境，注重韵律和情感深度
- `现代简约`: 使用简洁明快的现代语言，直接表达情感和场景
- `悬疑神秘`: 营造神秘紧张的氛围，使用悬疑小说的叙述技巧
- `温馨治愈`: 使用温暖、治愈的语言，传递正能量和美好情感
- `幽默风趣`: 运用幽默的表达方式，轻松诙谐地叙述故事
- `史诗壮阔`: 使用宏大的叙述风格，营造史诗般的氛围
- `文艺小清新`: 使用清新淡雅的文艺语言，注重细腻的情感表达

如果不指定style参数或传入空值，系统将使用默认的通用风格。也可以传入自定义的风格描述。

**响应示例（成功）**:

```json
{
  "success": true,
  "message": "故事生成完成",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "story_result": {
    "success": true,
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "video_info": {
      "task_id": "550e8400-e29b-41d4-a716-446655440000",
      "video_name": "我的视频.mp4",
      "video_path": "uploads/20231015_143015_我的视频.mp4",
      "processing_time": "2023-10-15T14:30:15.123456",
      "total_keyframes": 8
    },
    "overall_theme": "一个关于成长与希望的温暖故事",
    "final_narrations": [
      {
        "frame_index": 0,
        "frame_path": "frames/task_123_video/unified_key_00.jpg",
        "story_text": "晨光透过窗棂，洒在他年轻的脸庞上，那是一个充满可能性的新开始。"
      }
    ],
    "creation_time": "2023-10-15T14:35:20.456789",
    "json_file_path": "stories/我的视频_story_20231015_143520.json",
    "processing_stats": {
      "start_time": "2023-10-15T14:35:15.123456",
      "architect_completed": true,
      "soul_writer_completed": true,
      "master_editor_completed": true,
      "total_time": 25.3,
      "success": true,
      "errors": []
    },
    "intermediate_results": {
      "architect_output": [...],
      "emotional_output": [...]
    }
  }
}
```

**响应示例（失败）**:

```json
{
  "success": false,
  "message": "故事生成失败: API调用超时",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "error": "API调用超时"
}
```

### 10. 获取文体风格列表

获取系统支持的所有文体风格列表，帮助前端展示可选的风格选项。

- **URL**: `/api/story/styles`
- **方法**: `GET`
- **Content-Type**: `application/json`

**响应示例（成功）**:

```json
{
  "success": true,
  "message": "获取文体风格列表成功",
  "styles": [
    {
      "name": "古典诗意",
      "description": "采用古典文学的优美词汇和意境，注重韵律和情感深度"
    },
    {
      "name": "现代简约",
      "description": "使用简洁明快的现代语言，直接表达情感和场景"
    },
    {
      "name": "悬疑神秘",
      "description": "营造神秘紧张的氛围，使用悬疑小说的叙述技巧"
    },
    {
      "name": "温馨治愈",
      "description": "使用温暖、治愈的语言，传递正能量和美好情感"
    },
    {
      "name": "幽默风趣",
      "description": "运用幽默的表达方式，轻松诙谐地叙述故事"
    },
    {
      "name": "史诗壮阔",
      "description": "使用宏大的叙述风格，营造史诗般的氛围"
    },
    {
      "name": "文艺小清新",
      "description": "使用清新淡雅的文艺语言，注重细腻的情感表达"
    }
  ],
  "total_count": 7
}
```

**响应示例（失败）**:

```json
{
  "success": false,
  "message": "获取文体风格列表失败: 系统错误"
}
```

### 11. 获取故事生成结果（已废弃）

获取故事生成结果的API已废弃，因为故事生成现在是同步处理。

- **URL**: `/api/story/result/<task_id>`
- **方法**: `GET`
- **状态**: 已废弃

**路径参数**:

| 参数名 | 类型 | 描述 |
|--------|------|------|
| task_id | string | 任务ID |

**响应示例**:

```json
{
  "success": false,
  "message": "故事生成现在是同步的，请直接调用 /api/generate/story 获取结果"
}
```

**注意**: 此API仅为兼容性保留，请使用同步的故事生成API (`/api/generate/story`)。

### 12. 获取故事文件

获取生成的故事JSON文件。

- **URL**: `/api/stories/<filename>`
- **方法**: `GET`

**路径参数**:

| 参数名 | 类型 | 描述 |
|--------|------|------|
| filename | string | 故事文件名（如：我的视频_story_20231015_143520.json） |

**响应**:
成功时返回JSON文件内容，失败时返回JSON错误信息。

### 13. 关键帧风格化处理

对关键帧进行风格化处理，使用AI技术将图像转换为指定风格。

- **URL**: `/api/process/style-transform`
- **方法**: `POST`
- **Content-Type**: `application/json`

**请求参数**:

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "style_prompt": "Convert to Ink and brushwork style, Chinese style, Yellowed and old, Low saturation, Low brightness",
  "image_size": "1920x1024",
  "image_urls": [
    {
      "url": "http://localhost:5001/api/frames/task_id/unified_key_00.jpg",
      "local_path": "frames/task_dir/unified_key_00.jpg",
      "filename": "unified_key_00.jpg"
    }
  ]
}
```

**请求参数说明**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| task_id | string | 是 | 任务ID |
| style_prompt | string | 否 | 风格化提示词，默认使用配置的水墨画风格 |
| image_size | string | 否 | 输出图像尺寸，默认1920x1024 |
| image_urls | array | 否 | 要处理的图像信息数组，如果不提供则自动从任务结果中获取关键帧 |

**响应示例（成功）**:

```json
{
  "success": true,
  "message": "风格化处理完成",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "processed_count": 8,
  "successful_count": 7,
  "failed_count": 1,
  "style_prompt": "Convert to Ink and brushwork style, Chinese style, Yellowed and old, Low saturation, Low brightness",
  "style_results": [
    {
      "success": true,
      "original_url": "http://localhost:5001/api/frames/task_id/unified_key_00.jpg",
      "original_filename": "unified_key_00.jpg",
      "styled_path": "frames/task_dir/unified_key_00_styled.jpg",
      "styled_filename": "unified_key_00_styled.jpg",
      "styled_image_url": "https://...",
      "style_prompt": "Convert to Ink and brushwork style, Chinese style, Yellowed and old, Low saturation, Low brightness"
    }
  ]
}
```

**响应示例（失败）**:

```json
{
  "success": false,
  "message": "风格化处理失败: API调用超时"
}
```

**任务状态更新**:
风格化处理过程中，任务状态会更新为以下值：
- `style_processing`: 正在进行风格化处理
- `style_completed`: 风格化处理完成

### 14. 文件过大错误处理

当上传的文件超过800MB限制时，系统会自动返回413错误。

- **错误码**: `413`
- **触发条件**: 上传文件大小超过800MB

**响应示例**:

```json
{
  "success": false,
  "message": "文件过大，请选择小于800MB的视频文件"
}
```

**故事文件结构示例**:

```json
{
  "story_info": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "video_name": "我的视频.mp4",
    "video_path": "uploads/20231015_143015_我的视频.mp4",
    "processing_time": "2023-10-15T14:35:20.456789",
    "overall_theme": "一个关于成长与希望的温暖故事",
    "total_narrations": 8
  },
  "final_narrations": [
    {
      "frame_index": 0,
      "frame_path": "frames/task_123_video/unified_key_00.jpg",
      "story_text": "晨光透过窗棂，洒在他年轻的脸庞上，那是一个充满可能性的新开始。"
    }
  ],
  "intermediate_results": {
    "architect_output": [
      {
        "frame_index": 0,
        "frame_path": "frames/task_123_video/unified_key_00.jpg",
        "story_text": "引入开场：展现主角新一天的开始。"
      }
    ],
    "emotional_output": [
      {
        "frame_index": 0,
        "frame_path": "frames/task_123_video/unified_key_00.jpg",
        "story_text": "内心充满对未来的憧憬与期待。"
      }
    ]
  },
  "processing_stats": {
    "start_time": "2023-10-15T14:35:15.123456",
    "end_time": "2023-10-15T14:35:40.789012",
    "architect_completed": true,
    "soul_writer_completed": true,
    "master_editor_completed": true,
    "total_time": 25.3,
    "success": true,
    "errors": []
  },
  "generation_metadata": {
    "system_version": "1.0",
    "agents_used": ["architect", "soul_writer", "master_editor"],
    "export_time": "2023-10-15T14:35:40.789012"
  }
}
```

## 13. 完整连环画生成API

### 接口概述
**接口路径：** `/api/process/complete-comic`  
**请求方法：** `POST`  
**功能描述：** 一键完成关键帧提取、故事生成、风格化处理，返回完整的连环画数据

这是一个**集成接口**，将三个核心模块整合到一个流程中：
1. **关键帧提取** - 从视频中智能提取关键帧
2. **故事生成** - 为每个关键帧生成故事文本和互动提问  
3. **风格化处理** - 对关键帧进行艺术风格化处理

前端只需要在获取基础帧后调用这一个接口，即可获得最终的连环画数据。

### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `task_id` | string | 是 | - | 视频上传后获得的任务ID |
| `target_frames` | int | 否 | 8 | 目标关键帧数量 |
| `frame_interval` | float | 否 | 1.0 | 基础帧提取间隔（秒） |
| `significance_weight` | float | 否 | 0.6 | 重要性权重 |
| `quality_weight` | float | 否 | 0.4 | 质量权重 |
| `style_prompt` | string | 否 | - | 风格化提示词（可选） |
| `image_size` | string | 否 | - | 输出图像尺寸（可选） |
| `story_style` | string | 否 | - | 故事文体风格（可选） |
| `max_concurrent` | int | 否 | 50 | 最大并发处理数 |

### 请求示例

```bash
# 基础请求
curl -X POST "http://localhost:5001/api/process/complete-comic" \
  -F "task_id=your_task_id_here" \
  -F "target_frames=8" \
  -F "frame_interval=1.0"

# 完整参数请求
curl -X POST "http://localhost:5001/api/process/complete-comic" \
  -F "task_id=your_task_id_here" \
  -F "target_frames=10" \
  -F "frame_interval=0.8" \
  -F "significance_weight=0.7" \
  -F "quality_weight=0.3" \
  -F "style_prompt=漫画风格，鲜艳色彩" \
  -F "image_size=1920x1024" \
  -F "story_style=童话风格" \
  -F "max_concurrent=30"
```

### 响应格式

#### 成功启动响应 (200)
```json
{
  "success": true,
  "message": "完整连环画生成已启动",
  "task_id": "your_task_id_here",
  "status": "complete_comic_processing",
  "progress": 0,
  "stage": "initializing"
}
```

#### 错误响应
```json
{
  "success": false,
  "message": "任务ID无效或不存在"
}
```

### 处理阶段

连环画生成分为以下阶段，您可以通过进度查询接口监控：

1. **initializing** (0%) - 初始化
2. **extracting_keyframes** (0-30%) - 关键帧提取
3. **generating_story** (30-70%) - 故事生成  
4. **stylizing_frames** (70-100%) - 风格化处理
5. **completed** (100%) - 完成

---

## 14. 获取完整连环画结果API

### 接口概述
**接口路径：** `/api/comic/result/<task_id>`  
**请求方法：** `GET`  
**功能描述：** 获取完整连环画生成结果

### 请求示例

```bash
curl -X GET "http://localhost:5001/api/comic/result/your_task_id_here"
```

### 响应格式

#### 处理中响应 (202)
```json
{
  "success": false,
  "message": "连环画生成尚未完成",
  "status": "complete_comic_processing",
  "progress": 45,
  "stage": "generating_story",
  "current_message": "正在生成故事... (1/1)"
}
```

#### 完成响应 (200)
```json
{
  "success": true,
  "message": "连环画生成完成",
  "task_id": "your_task_id_here",
  "results": {
    "successful_comics": [
      {
        "video_name": "测试视频.mp4",
        "success": true,
        "comic_data": {
          "story_info": {
            "overall_theme": "一段关于勇气与成长的冒险之旅",
            "title": "一段关于勇气与成长的冒险之旅",
            "summary": "一段关于勇气与成长的冒险之旅",
            "total_pages": 8,
            "video_name": "测试视频.mp4",
            "creation_time": "2024-01-15 14:30:00"
          },
          "pages": [
            {
              "page_index": 0,
              "story_text": "阳光透过树叶，洒在年轻探险者的脸上...",
              "original_frame_path": "/path/to/original/frame_0000.jpg",
              "styled_frame_path": "/path/to/styled/styled_frame_0000.jpg",
              "styled_filename": "styled_frame_0000.jpg",
              "frame_index": 0,
              "style_applied": true
            },
            {
              "page_index": 1,
              "story_text": "深深的森林中回响着神秘的声音...",
              "original_frame_path": "/path/to/original/frame_0001.jpg",
              "styled_frame_path": "/path/to/styled/styled_frame_0001.jpg",
              "styled_filename": "styled_frame_0001.jpg",
              "frame_index": 1,
              "style_applied": true
            }
          ],
          "interactive_questions": [
            {
              "question_id": 1,
              "question": "你觉得主人公在这个场景中的心情如何？",
              "options": ["兴奋", "紧张", "好奇", "害怕"],
              "scene_description": "主人公站在森林入口处",
              "question_type": "情感理解"
            },
            {
              "question_id": 2,
              "question": "如果你是主人公，你会选择什么？",
              "options": ["继续前进", "返回村庄", "寻找伙伴", "制作标记"],
              "scene_description": "面临选择的关键时刻",
              "question_type": "决策思考"
            }
          ]
        },
        "processing_info": {
          "keyframes_extracted": 8,
          "story_generated": 8,
          "frames_stylized": 8,
          "keyframes_output_dir": "/path/to/frames/output",
          "story_file_path": "/path/to/story.json",
          "styled_frames_dir": "/path/to/styled/frames"
        }
      }
    ],
    "failed_comics": [],
    "total_processed": 1,
    "success_count": 1,
    "failure_count": 0
  },
  "task_info": {
    "status": "complete_comic_completed",
    "completed_time": "20240115_143000",
    "total_processing_time": "20240115_143000"
  }
}
```

#### 失败响应 (500)
```json
{
  "success": false,
  "message": "连环画生成失败",
  "error": "具体错误信息"
}
```

### 返回数据说明

#### comic_data结构
- **story_info** - 故事基本信息
  - `overall_theme` - 故事主题/标题/概要
  - `title` - 故事标题
  - `summary` - 故事概要
  - `total_pages` - 总页数
  - `creation_time` - 创建时间

- **pages** - 连环画页面数据（**每一帧的完整信息**）
  - `page_index` - 页面索引
  - `story_text` - **每一帧的故事文本**
  - `original_frame_path` - 原始帧路径  
  - `styled_frame_path` - **风格化后的帧文件路径**
  - `styled_filename` - **风格化后的文件名**
  - `style_applied` - 是否成功应用风格化

- **interactive_questions** - **互动提问**
  - `question_id` - 问题ID
  - `question` - 问题内容
  - `options` - 选项
  - `scene_description` - 场景描述
  - `question_type` - 问题类型

---

## 典型使用流程

### 基础视频处理流程

1. **上传视频**：调用视频上传API，获取`task_id`
2. **监控处理进度**：定期调用任务状态API，检查处理进度
3. **选择处理方式**：
   - 基础处理：调用基础帧提取API，然后调用关键帧提取API
   - 一键处理：直接调用统一智能处理API
4. **获取处理结果**：处理完成后，使用帧图像API获取生成的图像

### 完整故事生成流程

1. **上传视频并处理**：按照基础流程完成视频处理，获得关键帧数据
2. **准备故事生成数据**：整理视频信息和关键帧数据（可从关键帧提取结果的JSON文件中获取）
3. **调用故事生成**：调用三阶段故事生成API（同步处理，直接返回结果）
   - 注意：故事生成是同步处理，请求会等待直到生成完成或失败
   - 处理时间通常在20-60秒之间，取决于关键帧数量和AI服务响应速度
4. **获取故事文件**：使用返回的`json_file_path`或通过故事文件API获取完整的故事JSON文件
5. **解析故事内容**：从JSON文件中提取最终旁白、中间结果和处理统计信息

### 关键帧风格化处理流程

1. **完成基础处理**：按照基础流程完成视频处理，获得关键帧图像
2. **调用风格化处理**：调用关键帧风格化处理API
   - 可以指定自定义的风格化提示词和输出尺寸
   - 如果不指定图像URLs，系统会自动从任务结果中获取关键帧
   - 支持批量处理多张关键帧图像
3. **监控处理进度**：通过任务状态API监控风格化处理进度
   - 状态会显示为`style_processing`（处理中）到`style_completed`（完成）
4. **获取风格化结果**：从风格化处理的响应中获取处理后的图像信息
   - 风格化后的图像会保存在原关键帧目录中，文件名添加`_styled`后缀
   - 可以通过帧图像API获取风格化后的图像文件

## 错误处理

所有API在发生错误时会返回带有`success: false`和`message`字段的JSON响应，其中`message`包含错误详情。常见错误包括：

- 参数缺失或无效
- 文件格式不支持
- 文件大小超限（上限800MB）
- 任务不存在或状态不允许操作
- 风格化处理API调用失败或超时
- 服务器内部错误

## 完整工作流程示例

### 步骤1: 上传视频
```bash
curl -X POST "http://localhost:5001/api/upload/videos" \
  -F "video=@your_video.mp4" \
  -F "device_id=web_client_001"
```

### 步骤2: 提取基础帧（可选）
```bash
curl -X POST "http://localhost:5001/api/extract/base-frames" \
  -F "task_id=received_task_id" \
  -F "interval=1.0"
```

### 步骤3: 启动完整连环画生成
```bash
curl -X POST "http://localhost:5001/api/process/complete-comic" \
  -F "task_id=received_task_id" \
  -F "target_frames=8" \
  -F "style_prompt=水彩画风格"
```

### 步骤4: 查询处理进度
```bash
curl -X GET "http://localhost:5001/api/task/status/received_task_id"
```

### 步骤5: 获取最终连环画结果
```bash
curl -X GET "http://localhost:5001/api/comic/result/received_task_id"
```

### 完整的前端集成示例

```javascript
class ComicGenerator {
  async generateComic(videoFile, options = {}) {
    try {
      // 1. 上传视频
      const uploadResult = await this.uploadVideo(videoFile);
      const taskId = uploadResult.task_id;
      
      // 2. 可选：提取基础帧
      if (options.extractBaseFrames) {
        await this.extractBaseFrames(taskId);
      }
      
      // 3. 启动完整连环画生成
      const startResult = await this.startComicGeneration(taskId, options);
      
      // 4. 轮询进度
      const finalResult = await this.pollProgress(taskId);
      
      return finalResult;
    } catch (error) {
      console.error('连环画生成失败:', error);
      throw error;
    }
  }
  
  async startComicGeneration(taskId, options) {
    const formData = new FormData();
    formData.append('task_id', taskId);
    formData.append('target_frames', options.targetFrames || 8);
    formData.append('style_prompt', options.stylePrompt || '');
    formData.append('story_style', options.storyStyle || '');
    
    const response = await fetch('/api/process/complete-comic', {
      method: 'POST',
      body: formData
    });
    
    return await response.json();
  }
  
  async pollProgress(taskId) {
    while (true) {
      const statusResponse = await fetch(`/api/task/status/${taskId}`);
      const status = await statusResponse.json();
      
      // 更新UI进度
      this.updateProgress(status.progress, status.stage, status.message);
      
      if (status.status === 'complete_comic_completed') {
        // 获取最终结果
        const resultResponse = await fetch(`/api/comic/result/${taskId}`);
        return await resultResponse.json();
      }
      
      if (status.status === 'complete_comic_failed') {
        throw new Error(status.error || '生成失败');
      }
      
      // 等待2秒后再次查询
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  }
  
  updateProgress(progress, stage, message) {
    console.log(`进度: ${progress}% - ${stage} - ${message}`);
    // 更新进度条UI
  }
}

// 使用示例
const generator = new ComicGenerator();
generator.generateComic(videoFile, {
  targetFrames: 10,
  stylePrompt: '手绘漫画风格，温暖色调',
  storyStyle: '童话风格',
  extractBaseFrames: true
}).then(result => {
  console.log('连环画生成完成:', result);
  // 处理最终结果，显示连环画
}).catch(error => {
  console.error('生成失败:', error);
});
```

