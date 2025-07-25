from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import uuid
import threading
import time
from datetime import datetime

app = Flask(__name__)

# 配置
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'wmv', 'flv', '3gp'}
MAX_CONTENT_LENGTH = 800 * 1024 * 1024  # 500MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 任务状态存储
task_status = {}

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_videos_async(task_id, video_files):
    """异步处理视频的后台任务"""
    try:
        task_status[task_id]['status'] = 'processing'
        task_status[task_id]['message'] = '正在为您织造回忆，请稍候...'
        
        # 模拟视频处理过程
        for i, video_file in enumerate(video_files):
            # 更新进度
            progress = int((i + 1) / len(video_files) * 100)
            task_status[task_id]['progress'] = progress
            task_status[task_id]['message'] = f'正在处理第 {i+1}/{len(video_files)} 个视频...'
            
            # 这里添加实际的视频处理逻辑
            # 例如：调用视频帧提取、AI分析等
            time.sleep(2)  # 模拟处理时间
        
        # 处理完成
        task_status[task_id]['status'] = 'completed'
        task_status[task_id]['message'] = '回忆织造完成！'
        task_status[task_id]['progress'] = 100
        
    except Exception as e:
        task_status[task_id]['status'] = 'error'
        task_status[task_id]['message'] = f'处理失败: {str(e)}'
        task_status[task_id]['error'] = str(e)

@app.route('/api/upload/videos', methods=['POST'])
def upload_videos():
    """视频上传接口"""
    try:
        # 检查设备唯一码
        device_id = request.form.get('device_id')
        if not device_id:
            return jsonify({
                'success': False,
                'message': '缺少设备唯一码'
            }), 400
        
        # 检查是否有文件
        if 'videos' not in request.files:
            return jsonify({
                'success': False,
                'message': '未找到视频文件'
            }), 400
        
        files = request.files.getlist('videos')
        
        if not files or all(file.filename == '' for file in files):
            return jsonify({
                'success': False,
                'message': '未选择任何文件'
            }), 400
        
        # 验证文件
        valid_files = []
        invalid_files = []
        
        for file in files:
            if file and allowed_file(file.filename):
                valid_files.append(file)
            else:
                invalid_files.append(file.filename if file.filename else '未知文件')
        
        if not valid_files:
            return jsonify({
                'success': False,
                'message': '没有有效的视频文件',
                'invalid_files': invalid_files
            }), 400
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 保存文件
        saved_files = []
        for file in valid_files:
            filename = secure_filename(file.filename)
            # 添加时间戳避免文件名冲突
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            saved_files.append({
                'original_name': file.filename,
                'saved_name': filename,
                'filepath': filepath,
                'size': os.path.getsize(filepath)
            })
        
        # 初始化任务状态
        task_status[task_id] = {
            'status': 'uploaded',
            'message': '视频上传成功，准备开始处理...',
            'progress': 0,
            'files': saved_files,
            'device_id': device_id,
            'created_at': datetime.now().isoformat()
        }
        
        # 启动异步处理任务
        thread = threading.Thread(
            target=process_videos_async, 
            args=(task_id, saved_files)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': '视频上传成功',
            'task_id': task_id,
            'device_id': device_id,
            'uploaded_files': len(saved_files),
            'invalid_files': invalid_files if invalid_files else None
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'上传失败: {str(e)}'
        }), 500

@app.route('/api/task/status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """获取任务处理状态"""
    if task_id not in task_status:
        return jsonify({
            'success': False,
            'message': '任务不存在'
        }), 404
    
    return jsonify({
        'success': True,
        'task_id': task_id,
        **task_status[task_id]
    }), 200

@app.route('/api/task/cancel/<task_id>', methods=['POST'])
def cancel_task(task_id):
    """取消任务"""
    if task_id not in task_status:
        return jsonify({
            'success': False,
            'message': '任务不存在'
        }), 404
    
    if task_status[task_id]['status'] in ['completed', 'error']:
        return jsonify({
            'success': False,
            'message': '任务已完成或出错，无法取消'
        }), 400
    
    task_status[task_id]['status'] = 'cancelled'
    task_status[task_id]['message'] = '任务已取消'
    
    return jsonify({
        'success': True,
        'message': '任务已取消'
    }), 200

@app.route('/api/device/<device_id>/tasks', methods=['GET'])
def get_device_tasks(device_id):
    """获取设备的所有任务历史"""
    device_tasks = []
    
    for task_id, task_info in task_status.items():
        if task_info.get('device_id') == device_id:
            device_tasks.append({
                'task_id': task_id,
                'status': task_info['status'],
                'message': task_info['message'],
                'progress': task_info.get('progress', 0),
                'created_at': task_info['created_at'],
                'file_count': len(task_info.get('files', []))
            })
    
    # 按创建时间倒序排列
    device_tasks.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify({
        'success': True,
        'device_id': device_id,
        'tasks': device_tasks,
        'total_tasks': len(device_tasks)
    }), 200

@app.errorhandler(413)
def too_large(e):
    """文件过大错误处理"""
    return jsonify({
        'success': False,
        'message': '文件过大，请选择小于800MB的视频文件'
    }), 413

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)