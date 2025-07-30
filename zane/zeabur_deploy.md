# Zeabur部署指南

## 问题解决

### 1. OpenGL库缺失错误
**错误信息**: `ImportError: libGL.so.1: cannot open shared object file: No such file or directory`

**解决方案**: 使用 `opencv-python-headless` 替代 `opencv-python`

### 2. 修改后的requirements.txt
```
Flask==2.3.3
requests==2.31.0
opencv-python-headless==4.8.1.78
Pillow==10.0.1
numpy==1.24.3
openai==1.3.5
aiohttp==3.8.6
psutil>=5.9.0
```

### 3. Dockerfile配置（可选）
如果需要自定义Docker镜像：
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖（用于OpenCV headless版本）
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["python", "app.py"]
```

## 部署步骤

### 1. 确认文件修改
- ✅ requirements.txt 已更新为 opencv-python-headless
- ✅ diversity_frame_extractor.py 已添加无头环境配置

### 2. 重新部署
1. 提交代码更改到Git仓库
2. 在Zeabur控制台触发重新部署
3. 等待部署完成

### 3. 验证部署
部署成功后，应用应该能够正常启动，不再出现OpenGL相关错误。

## 性能优化

### 1. 内存使用
- opencv-python-headless 比完整版本占用更少内存
- 没有GUI相关的依赖，启动更快

### 2. CPU优化
代码中已包含以下优化：
```python
cv2.setUseOptimized(True)  # 启用CPU优化
cv2.setNumThreads(0)       # 使用所有CPU核心
```

### 3. 环境变量
```python
os.environ['OPENCV_IO_ENABLE_OPENEXR'] = '0'  # 禁用不必要的格式支持
os.environ['OPENCV_IO_ENABLE_JASPER'] = '0'
```

## 故障排除

### 如果仍然出现错误
1. 检查requirements.txt是否正确更新
2. 确认使用的是opencv-python-headless而不是opencv-python
3. 清除Zeabur的构建缓存并重新部署

### 测试API
部署成功后，可以测试以下端点：
- GET `/` - 健康检查
- POST `/api/upload/videos` - 视频上传
- GET `/api/task/status/<task_id>` - 任务状态

## 注意事项

1. **无GUI功能**: headless版本不支持cv2.imshow()等GUI功能
2. **功能完整**: 所有图像处理、视频读取功能都正常工作
3. **性能**: 在服务器环境中性能更好，内存占用更少

## 总结

通过使用opencv-python-headless，你的应用现在应该能够在Zeabur等无头服务器环境中正常运行，不再出现OpenGL相关的错误。