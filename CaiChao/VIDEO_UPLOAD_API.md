# 视频上传API文档

## 概述
这是一个基于Flask的视频上传和处理API，支持多文件上传、异步处理和实时状态查询。

## 技术特性
- 支持多视频文件同时上传
- 异步后台处理，避免前端长时间等待
- 实时进度查询和状态更新
- 文件类型和大小验证
- 任务取消功能
- 友好的错误处理

## API接口

### 1. 视频上传接口
**POST** `/api/upload/videos`

**请求参数:**
- `device_id`: 设备唯一码 (必填, form-data)
  - 格式要求: 参见[设备唯一码说明](#设备唯一码说明)
  - 示例: `iOS_iPhone14_A1B2C3D4E5F6`
- `videos`: 多个视频文件 (multipart/form-data)
  - 可同时上传多个视频文件
  - 每个文件使用相同的表单字段名 `videos`

**支持格式:** mp4, mov, avi, mkv, wmv, flv, 3gp
**文件大小限制:** 单个文件最大800MB

**响应示例:**
```json
{
    "success": true,
    "message": "视频上传成功",
    "task_id": "123e4567-e89b-12d3-a456-426614174000",
    "device_id": "iOS_iPhone12_A1B2C3D4E5F6",
    "uploaded_files": 2,
    "invalid_files": null
}
```

### 2. 任务状态查询接口
**GET** `/api/task/status/<task_id>`

**响应示例:**
```json
{
    "success": true,
    "task_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "processing",
    "message": "正在处理第 1/2 个视频...",
    "progress": 50,
    "files": [...],
    "device_id": "iOS_iPhone12_A1B2C3D4E5F6",
    "created_at": "2025-01-24T10:30:00"
}
```

**状态说明:**
- `uploaded`: 文件上传完成，准备处理
- `processing`: 正在处理中
- `completed`: 处理完成
- `error`: 处理出错
- `cancelled`: 任务已取消

### 3. 任务取消接口
**POST** `/api/task/cancel/<task_id>`

**响应示例:**
```json
{
    "success": true,
    "message": "任务已取消"
}
```

### 4. 设备任务历史查询接口
**GET** `/api/device/<device_id>/tasks`

**响应示例:**
```json
{
    "success": true,
    "device_id": "iOS_iPhone12_A1B2C3D4E5F6",
    "tasks": [
        {
            "task_id": "123e4567-e89b-12d3-a456-426614174000",
            "status": "completed",
            "message": "回忆织造完成！",
            "progress": 100,
            "created_at": "2025-01-24T10:30:00",
            "file_count": 3
        }
    ],
    "total_tasks": 1
}
```

## 设备唯一码说明

### 设备唯一码格式规范
为确保系统能够正确识别和管理不同设备的上传任务，建议按照以下格式生成设备唯一码：

- **iOS设备**: `iOS_{设备型号}_{UUID前12位}` 
  - 例如: `iOS_iPhone14_A1B2C3D4E5F6`
- **Android设备**: `Android_{设备型号}_{设备ID前12位}`
  - 例如: `Android_SM-G991B_1A2B3C4D5E6F`
- **Web端**: `Web_{浏览器}_{随机码}_{时间戳}`
  - 例如: `Web_Chrome_a1b2c3d4_20250724`

### 设备唯一码获取方法

#### iOS获取设备唯一码
```swift
import UIKit

func getDeviceId() -> String {
    let deviceModel = UIDevice.current.model.replacingOccurrences(of: " ", with: "")
    let deviceId = UIDevice.current.identifierForVendor?.uuidString ?? UUID().uuidString
    let shortId = String(deviceId.prefix(12))
    return "iOS_\(deviceModel)_\(shortId)"
}
```

### 设备唯一码存储建议
- **iOS/Android**: 使用 KeyChain/KeyStore 安全存储
- **Web**: 使用 localStorage 或 IndexedDB 存储，并考虑加密

### 设备唯一码用途
- **用户行为分析**: 跟踪不同设备的使用模式和偏好
- **任务管理**: 按设备分组和管理上传任务
- **防止重复上传**: 检测同一设备的重复上传请求
- **个性化推荐**: 基于设备历史记录提供个性化服务
- **跨设备同步**: 支持用户在不同设备间同步任务状态

### 隐私考虑
- 设备唯一码应被视为个人隐私数据，需遵循相关隐私法规
- 在应用隐私政策中明确说明设备唯一码的收集和使用目的
- 不应将设备唯一码用于用户追踪或广告目的
- 建议实现设备唯一码重置功能，允许用户在需要时重置

## 错误处理

### 常见错误码
- `400`: 请求参数错误（缺少设备唯一码、无文件、文件格式不支持等）
- `404`: 任务不存在
- `413`: 文件过大
- `500`: 服务器内部错误

### 错误响应格式
```json
{
    "success": false,
    "message": "错误描述",
    "invalid_files": ["不支持的文件列表"]
}
```

## 部署建议

### 生产环境配置
1. 使用WSGI服务器（如Gunicorn）
2. 配置反向代理（Nginx）
3. 设置适当的文件上传限制
4. 配置日志记录
5. 添加认证和授权机制

### 性能优化
1. 使用Redis存储任务状态
2. 配置文件存储到云服务（如AWS S3）
3. 添加任务队列（如Celery）
4. 实现断点续传功能

## 安全考虑
1. 文件类型严格验证
2. 文件大小限制
3. 上传频率限制
4. 文件名安全处理
5. 病毒扫描（生产环境推荐）