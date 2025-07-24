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
- `videos`: 多个视频文件 (multipart/form-data)

**支持格式:** mp4, mov, avi, mkv, wmv, flv, 3gp
**文件大小限制:** 单个文件最大800MB

**响应示例:**
```json
{
    "success": true,
    "message": "视频上传成功",
    "task_id": "123e4567-e89b-12d3-a456-426614174000",
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

## 使用方法

### 1. 启动服务器
```bash
pip install -r requirements.txt
python video_upload_api.py
```

### 2. 前端集成示例

#### JavaScript上传代码
```javascript
async function uploadVideos(files) {
    const formData = new FormData();
    files.forEach(file => {
        formData.append('videos', file);
    });

    const response = await fetch('/api/upload/videos', {
        method: 'POST',
        body: formData
    });

    const result = await response.json();
    if (result.success) {
        // 开始轮询状态
        pollTaskStatus(result.task_id);
    }
}

async function pollTaskStatus(taskId) {
    const response = await fetch(`/api/task/status/${taskId}`);
    const result = await response.json();
    
    if (result.status === 'completed') {
        console.log('处理完成！');
    } else if (result.status === 'error') {
        console.log('处理失败:', result.message);
    } else {
        // 继续轮询
        setTimeout(() => pollTaskStatus(taskId), 2000);
    }
}
```

#### iOS Swift集成示例
```swift
func uploadVideos(videoURLs: [URL]) {
    let url = URL(string: "http://your-server.com/api/upload/videos")!
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    
    let boundary = UUID().uuidString
    request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
    
    var body = Data()
    
    for videoURL in videoURLs {
        let videoData = try! Data(contentsOf: videoURL)
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"videos\"; filename=\"\(videoURL.lastPathComponent)\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: video/mp4\r\n\r\n".data(using: .utf8)!)
        body.append(videoData)
        body.append("\r\n".data(using: .utf8)!)
    }
    
    body.append("--\(boundary)--\r\n".data(using: .utf8)!)
    request.httpBody = body
    
    URLSession.shared.dataTask(with: request) { data, response, error in
        // 处理响应
    }.resume()
}
```

## 错误处理

### 常见错误码
- `400`: 请求参数错误（无文件、文件格式不支持等）
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