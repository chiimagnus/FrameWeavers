from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import uuid
import threading
import time
import asyncio
from datetime import datetime
from diversity_frame_extractor import DiversityFrameExtractor

app = Flask(__name__)

# 配置
UPLOAD_FOLDER = 'uploads'
FRAMES_FOLDER = 'frames'
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'wmv', 'flv', '3gp'}
MAX_CONTENT_LENGTH = 800 * 1024 * 1024  # 800MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['FRAMES_FOLDER'] = FRAMES_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# 确保上传和帧目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(FRAMES_FOLDER, exist_ok=True)

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

# 创建异步事件循环
async_loop = asyncio.new_event_loop()

def run_async_task(coro):
    """在异步事件循环中运行协程"""
    asyncio.set_event_loop(async_loop)
    return async_loop.run_until_complete(coro)

def start_async_loop():
    """启动异步事件循环"""
    asyncio.set_event_loop(async_loop)
    async_loop.run_forever()

# 在单独的线程中启动异步事件循环
threading.Thread(target=start_async_loop, daemon=True).start()

# ========================= API 路由 =========================

# 1. 视频上传API
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

# 2. 获取任务状态API
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

# 3. 取消任务API
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

# 4. 获取设备任务历史API
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

# 5. 基础帧提取API
@app.route('/api/extract/base-frames', methods=['POST'])
def extract_base_frames():
    """提取视频基础帧"""
    try:
        # 检查是否提供了任务ID
        task_id = request.form.get('task_id')
        if not task_id or task_id not in task_status:
            return jsonify({
                'success': False,
                'message': '任务ID无效或不存在'
            }), 400
            
        # 检查任务状态
        if task_status[task_id]['status'] != 'uploaded' and task_status[task_id]['status'] != 'completed':
            return jsonify({
                'success': False,
                'message': f'任务状态不允许提取帧: {task_status[task_id]["status"]}'
            }), 400
            
        # 获取视频文件
        video_files = task_status[task_id].get('files', [])
        if not video_files:
            return jsonify({
                'success': False,
                'message': '任务中没有可用的视频文件'
            }), 400
            
        # 获取参数
        target_interval = float(request.form.get('interval', 1.0))  # 默认1秒
        
        # 更新任务状态
        task_status[task_id]['status'] = 'extracting_base_frames'
        task_status[task_id]['message'] = '正在提取基础帧...'
        task_status[task_id]['progress'] = 0
        
        # 为每个视频创建单独的输出目录
        results = []
        
        for i, video_file in enumerate(video_files):
            # 更新进度
            progress = int((i / len(video_files)) * 100)
            task_status[task_id]['progress'] = progress
            
            # 创建视频专属的输出目录
            video_name = os.path.splitext(os.path.basename(video_file['filepath']))[0]
            output_dir = os.path.join(app.config['FRAMES_FOLDER'], f"{task_id}_{video_name}")
            os.makedirs(output_dir, exist_ok=True)
            
            # 创建抽帧器
            extractor = DiversityFrameExtractor(output_dir=output_dir)
            
            # 提取基础帧
            base_frames = extractor.extract_uniform_frames(
                video_path=video_file['filepath'],
                target_interval_seconds=target_interval
            )
            
            # 记录结果
            results.append({
                'video_name': video_file['original_name'],
                'base_frames_count': len(base_frames),
                'base_frames_paths': base_frames,
                'output_dir': output_dir
            })
            
            # 更新任务状态
            task_status[task_id]['message'] = f'已处理 {i+1}/{len(video_files)} 个视频'
            task_status[task_id]['progress'] = int(((i+1) / len(video_files)) * 100)
        
        # 更新任务状态
        task_status[task_id]['status'] = 'base_frames_extracted'
        task_status[task_id]['message'] = '基础帧提取完成'
        task_status[task_id]['progress'] = 100
        task_status[task_id]['base_frames_results'] = results
        
        return jsonify({
            'success': True,
            'message': '基础帧提取成功',
            'task_id': task_id,
            'results': results
        }), 200
        
    except Exception as e:
        if task_id in task_status:
            task_status[task_id]['status'] = 'error'
            task_status[task_id]['message'] = f'基础帧提取失败: {str(e)}'
            task_status[task_id]['error'] = str(e)
            
        return jsonify({
            'success': False,
            'message': f'基础帧提取失败: {str(e)}'
        }), 500

# 6. 关键帧提取API
@app.route('/api/extract/key-frames', methods=['POST'])
def extract_key_frames():
    """提取视频关键帧"""
    try:
        # 检查是否提供了任务ID
        task_id = request.form.get('task_id')
        if not task_id or task_id not in task_status:
            return jsonify({
                'success': False,
                'message': '任务ID无效或不存在'
            }), 400
            
        # 检查任务状态
        if task_status[task_id]['status'] != 'base_frames_extracted' and task_status[task_id]['status'] != 'completed':
            return jsonify({
                'success': False,
                'message': f'任务状态不允许提取关键帧: {task_status[task_id]["status"]}'
            }), 400
            
        # 获取参数
        target_key_frames = int(request.form.get('target_frames', 8))  # 默认8个关键帧
        significance_weight = float(request.form.get('significance_weight', 0.6))  # 默认0.6
        quality_weight = float(request.form.get('quality_weight', 0.4))  # 默认0.4
        max_concurrent = int(request.form.get('max_concurrent', 50))  # 默认最大并发50
        
        # 更新任务状态
        task_status[task_id]['status'] = 'extracting_key_frames'
        task_status[task_id]['message'] = '正在提取关键帧...'
        task_status[task_id]['progress'] = 0
        
        # 获取基础帧结果
        base_frames_results = task_status[task_id].get('base_frames_results', [])
        if not base_frames_results:
            return jsonify({
                'success': False,
                'message': '没有找到基础帧提取结果'
            }), 400
            
        # 处理每个视频的关键帧
        key_frames_results = []
        
        for i, result in enumerate(base_frames_results):
            # 更新进度
            progress = int((i / len(base_frames_results)) * 100)
            task_status[task_id]['progress'] = progress
            task_status[task_id]['message'] = f'正在处理第 {i+1}/{len(base_frames_results)} 个视频的关键帧...'
            
            # 获取输出目录和视频名称
            output_dir = result['output_dir']
            video_name = result['video_name']
            
            # 创建抽帧器
            extractor = DiversityFrameExtractor(output_dir=output_dir)
            
            # 获取基础帧路径
            base_frames = result['base_frames_paths']
            
            # 分析基础帧并提取关键帧
            analyzed_frames = run_async_task(
                extractor.analyze_frames_with_ai_async(
                    frame_paths=base_frames,
                    max_concurrent=max_concurrent
                )
            )
            
            # 筛选关键帧
            selected_frames = extractor.select_key_frames_by_ai(
                analyzed_frames=analyzed_frames,
                target_key_frames=target_key_frames,
                significance_weight=significance_weight,
                quality_weight=quality_weight
            )
            
            # 保存关键帧
            key_frame_paths = extractor.save_key_frames(
                selected_frames=selected_frames,
                output_prefix=f"key_{video_name}"
            )
            
            # 保存关键帧信息到JSON
            json_file_path = extractor.save_keyframes_to_json(
                selected_frames=selected_frames,
                video_path=video_name
            )
            
            # 记录结果
            key_frames_results.append({
                'video_name': video_name,
                'base_frames_count': len(base_frames),
                'key_frames_count': len(selected_frames),
                'key_frames_paths': key_frame_paths,
                'json_file_path': json_file_path,
                'output_dir': output_dir
            })
            
            # 更新任务状态
            task_status[task_id]['progress'] = int(((i+1) / len(base_frames_results)) * 100)
        
        # 更新任务状态
        task_status[task_id]['status'] = 'completed'
        task_status[task_id]['message'] = '关键帧提取完成'
        task_status[task_id]['progress'] = 100
        task_status[task_id]['key_frames_results'] = key_frames_results
        
        return jsonify({
            'success': True,
            'message': '关键帧提取成功',
            'task_id': task_id,
            'results': key_frames_results
        }), 200
        
    except Exception as e:
        if task_id in task_status:
            task_status[task_id]['status'] = 'error'
            task_status[task_id]['message'] = f'关键帧提取失败: {str(e)}'
            task_status[task_id]['error'] = str(e)
            
        return jsonify({
            'success': False,
            'message': f'关键帧提取失败: {str(e)}'
        }), 500

# 7. 统一智能处理API
@app.route('/api/process/unified', methods=['POST'])
def unified_smart_process():
    """统一智能处理API - 一键完成所有处理"""
    try:
        # 检查是否提供了任务ID
        task_id = request.form.get('task_id')
        if not task_id or task_id not in task_status:
            return jsonify({
                'success': False,
                'message': '任务ID无效或不存在'
            }), 400
            
        # 检查任务状态
        if task_status[task_id]['status'] != 'uploaded' and task_status[task_id]['status'] != 'completed':
            return jsonify({
                'success': False,
                'message': f'任务状态不允许进行统一处理: {task_status[task_id]["status"]}'
            }), 400
            
        # 获取视频文件
        video_files = task_status[task_id].get('files', [])
        if not video_files:
            return jsonify({
                'success': False,
                'message': '任务中没有可用的视频文件'
            }), 400
            
        # 获取参数
        target_key_frames = int(request.form.get('target_frames', 8))  # 默认8个关键帧
        base_frame_interval = float(request.form.get('interval', 1.0))  # 默认1秒
        significance_weight = float(request.form.get('significance_weight', 0.6))  # 默认0.6
        quality_weight = float(request.form.get('quality_weight', 0.4))  # 默认0.4
        max_concurrent = int(request.form.get('max_concurrent', 50))  # 默认最大并发50
        
        # 更新任务状态
        task_status[task_id]['status'] = 'unified_processing'
        task_status[task_id]['message'] = '正在进行统一智能处理...'
        task_status[task_id]['progress'] = 0
        
        # 处理每个视频
        unified_results = []
        
        for i, video_file in enumerate(video_files):
            # 更新进度
            progress = int((i / len(video_files)) * 100)
            task_status[task_id]['progress'] = progress
            task_status[task_id]['message'] = f'正在处理第 {i+1}/{len(video_files)} 个视频...'
            
            # 创建视频专属的输出目录
            video_name = os.path.splitext(os.path.basename(video_file['filepath']))[0]
            output_dir = os.path.join(app.config['FRAMES_FOLDER'], f"{task_id}_{video_name}")
            os.makedirs(output_dir, exist_ok=True)
            
            # 创建抽帧器
            extractor = DiversityFrameExtractor(output_dir=output_dir)
            
            # 执行统一智能处理
            result = run_async_task(
                extractor.unified_smart_extraction_async(
                    video_path=video_file['filepath'],
                    target_key_frames=target_key_frames,
                    base_frame_interval=base_frame_interval,
                    significance_weight=significance_weight,
                    quality_weight=quality_weight,
                    max_concurrent=max_concurrent
                )
            )
            
            # 记录结果
            if result['success']:
                unified_results.append({
                    'video_name': video_file['original_name'],
                    'base_frames_count': len(result['base_frames']),
                    'key_frames_count': len(result['selected_frames']),
                    'key_frame_paths': result['key_frame_paths'],
                    'json_file_path': result['json_file_path'],
                    'output_dir': output_dir,
                    'processing_stats': result['processing_stats']
                })
            else:
                unified_results.append({
                    'video_name': video_file['original_name'],
                    'success': False,
                    'error': result['error']
                })
            
            # 更新任务状态
            task_status[task_id]['message'] = f'已处理 {i+1}/{len(video_files)} 个视频'
            task_status[task_id]['progress'] = int(((i+1) / len(video_files)) * 100)
        
        # 更新任务状态
        task_status[task_id]['status'] = 'completed'
        task_status[task_id]['message'] = '统一智能处理完成'
        task_status[task_id]['progress'] = 100
        task_status[task_id]['unified_results'] = unified_results
        
        return jsonify({
            'success': True,
            'message': '统一智能处理成功',
            'task_id': task_id,
            'results': unified_results
        }), 200
        
    except Exception as e:
        if task_id in task_status:
            task_status[task_id]['status'] = 'error'
            task_status[task_id]['message'] = f'统一智能处理失败: {str(e)}'
            task_status[task_id]['error'] = str(e)
            
        return jsonify({
            'success': False,
            'message': f'统一智能处理失败: {str(e)}'
        }), 500

# 8. 获取帧图像API
@app.route('/api/frames/<task_id>/<path:filename>', methods=['GET'])
def get_frame_image(task_id, filename):
    """获取帧图像"""
    # 构建可能的路径
    possible_paths = []
    
    # 如果任务存在，尝试查找其所有视频的输出目录
    if task_id in task_status:
        # 检查基础帧结果
        base_frames_results = task_status[task_id].get('base_frames_results', [])
        for result in base_frames_results:
            possible_paths.append(result['output_dir'])
            
        # 检查关键帧结果
        key_frames_results = task_status[task_id].get('key_frames_results', [])
        for result in key_frames_results:
            possible_paths.append(result['output_dir'])
            
        # 检查统一处理结果
        unified_results = task_status[task_id].get('unified_results', [])
        for result in unified_results:
            if isinstance(result, dict) and 'output_dir' in result:
                possible_paths.append(result['output_dir'])
    
    # 添加默认帧目录
    possible_paths.append(app.config['FRAMES_FOLDER'])
    
    # 尝试在所有可能的路径中查找文件
    for path in possible_paths:
        if os.path.exists(os.path.join(path, filename)):
            return send_from_directory(path, filename)
    
    # 如果找不到文件，返回404
    return jsonify({
        'success': False,
        'message': '找不到请求的帧图像'
    }), 404

# 9. 文件过大错误处理
@app.errorhandler(413)
def too_large(e):
    """文件过大错误处理"""
    return jsonify({
        'success': False,
        'message': '文件过大，请选择小于800MB的视频文件'
    }), 413

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
