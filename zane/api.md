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

系统共提供13个API接口，包括视频处理、任务管理、故事生成、风格化处理和错误处理等功能。

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
  ]
}
```

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

### 10. 获取故事生成结果（已废弃）

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

### 11. 获取故事文件

获取生成的故事JSON文件。

- **URL**: `/api/stories/<filename>`
- **方法**: `GET`

**路径参数**:

| 参数名 | 类型 | 描述 |
|--------|------|------|
| filename | string | 故事文件名（如：我的视频_story_20231015_143520.json） |

**响应**:
成功时返回JSON文件内容，失败时返回JSON错误信息。

### 12. 关键帧风格化处理

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

### 13. 文件过大错误处理

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

