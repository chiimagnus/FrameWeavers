# 帧织者API文档

## 概述

本文档详细说明了帧织者系统的API接口，供前端开发人员调用。系统提供视频上传、基础帧提取、关键帧提取等功能，支持异步处理和状态查询。

## 基础信息

- **基础URL**: `http://服务器地址:5000`
- **响应格式**: 所有API返回JSON格式数据
- **状态码**:
  - 200: 请求成功
  - 400: 请求参数错误
  - 404: 资源不存在
  - 413: 上传文件过大
  - 500: 服务器内部错误

## API接口列表

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
- `completed`: 处理完成
- `error`: 处理出错
- `cancelled`: 任务已取消

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

## 典型使用流程

1. **上传视频**：调用视频上传API，获取`task_id`
2. **监控处理进度**：定期调用任务状态API，检查处理进度
3. **选择处理方式**：
   - 基础处理：调用基础帧提取API，然后调用关键帧提取API
   - 一键处理：直接调用统一智能处理API
4. **获取处理结果**：处理完成后，使用帧图像API获取生成的图像

## 错误处理

所有API在发生错误时会返回带有`success: false`和`message`字段的JSON响应，其中`message`包含错误详情。常见错误包括：

- 参数缺失或无效
- 文件格式不支持
- 文件大小超限（上限800MB）
- 任务不存在或状态不允许操作
- 服务器内部错误

## 注意事项

1. 视频处理为异步操作，需要通过任务状态API监控进度
2. 关键帧提取依赖于基础帧提取的结果
3. 统一智能处理API提供一站式服务，适合大多数场景
4. 处理大视频文件时，请耐心等待，并关注任务状态 