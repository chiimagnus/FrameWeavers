from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import uuid
import threading
import time
import asyncio
from datetime import datetime
from diversity_frame_extractor import DiversityFrameExtractor
import requests
import json
from PIL import Image
from io import BytesIO
import config
import logging
import traceback
import psutil  # 添加系统监控库
import gc  # 添加垃圾回收库
import atexit  # 添加程序退出处理库

app = Flask(__name__)

# 配置
UPLOAD_FOLDER = 'uploads'
FRAMES_FOLDER = 'frames'
STORIES_FOLDER = 'stories'
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'wmv', 'flv', '3gp'}
MAX_CONTENT_LENGTH = 1024 * 1024 * 1024  # 1GB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['FRAMES_FOLDER'] = FRAMES_FOLDER
app.config['STORIES_FOLDER'] = STORIES_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# 确保上传和帧目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(FRAMES_FOLDER, exist_ok=True)
os.makedirs(STORIES_FOLDER, exist_ok=True)

# 任务状态存储
task_status = {}

# 内存监控函数
def check_memory_usage():
    """
    检查系统内存使用情况
    
    Returns:
        dict: 包含内存信息的字典
    """
    try:
        memory = psutil.virtual_memory()
        memory_info = {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percentage': memory.percent
        }
        
        # 发出警告
        if memory.percent > config.MEMORY_WARNING_THRESHOLD:
            print(f"⚠️ 内存使用率过高: {memory.percent:.1f}%")
            
        # 如果内存使用过高，强制垃圾回收
        if memory.percent > config.MAX_MEMORY_USAGE:
            print(f"🚨 内存使用率危险: {memory.percent:.1f}%，执行垃圾回收...")
            gc.collect()  # 强制垃圾回收
            
        return memory_info
    except Exception as e:
        print(f"内存监控失败: {e}")
        return None

def safe_memory_check_decorator(func):
    """
    内存安全检查装饰器
    在执行内存密集型操作前检查内存使用情况
    """
    def wrapper(*args, **kwargs):
        memory_info = check_memory_usage()
        if memory_info and memory_info['percentage'] > config.MAX_MEMORY_USAGE:
            raise Exception(f"内存使用率过高 ({memory_info['percentage']:.1f}%)，停止处理以防止系统崩溃")
        return func(*args, **kwargs)
    return wrapper

def upload_to_imgbb(image_path, api_key="7c9e1b2a3f4d5e6f7a8b9c0d1e2f3a4b"):
    """
    上传图片到图床并返回在线URL
    
    Args:
        image_path (str): 本地图片文件路径
        api_key (str): 图床API密钥（可选）
    
    Returns:
        str: 上传后的图片在线URL
    """
    try:
        # 使用自己的图床服务
        upload_url = 'https://tuchuan.zeabur.app/api/upload'
        
        print(f"[INFO] 上传图片到图床: {image_path}")
        
        # 检查文件是否存在
        if not os.path.exists(image_path):
            raise Exception(f"图片文件不存在: {image_path}")
        
        # 上传文件
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(upload_url, files=files, timeout=3000)
        
        if response.status_code != 200:
            raise Exception(f"上传请求失败，状态码: {response.status_code}")
        
        result = response.json()
        if result.get('success'):
            image_url = result['url']
            print(f"[INFO] 图片上传成功: {image_url}")
            return image_url
        else:
            error_msg = result.get('error', '未知错误')
            raise Exception(f"上传失败: {error_msg}")
            
    except Exception as e:
        print(f"[ERROR] 图片上传失败: {str(e)}")
        raise e

def style_transform_image(image_path, style_prompt=None, image_size=None):
    """
    对图像进行风格化处理 - 严格按照test_style.py的成功示例
    
    Args:
        image_path (str): 本地图像文件路径
        style_prompt (str): 风格化提示词，如果为None则使用默认值
        image_size (str): 输出图像尺寸，如果为None则使用默认值
    
    Returns:
        dict: 包含处理结果的字典
    """
    try:
        # 使用配置文件中的默认值
        if style_prompt is None:
            style_prompt = config.DEFAULT_STYLE_PROMPT
        if image_size is None:
            image_size = config.DEFAULT_IMAGE_SIZE
        
        print(f"[INFO] 开始风格化处理: {image_path}")
        
        # 检查本地文件是否存在
        if not os.path.exists(image_path):
            return {
                'success': False,
                'error': f'本地图像文件不存在: {image_path}'
            }
        
        # 第一步：上传图片到图床获取在线URL
        try:
            print("Uploading image...")
            image_url = upload_to_imgbb(image_path)
            print(f"Image uploaded: {image_url}")
        except Exception as upload_error:
            print(f"[ERROR] 图片上传失败: {str(upload_error)}")
            # 上传失败直接返回错误，不使用降级
            return {
                'success': False,
                'error': f'图片上传失败: {str(upload_error)}'
            }
        
        # 第二步：严格按照test_style.py的格式调用API
        url = config.MODELSCOPE_API_URL
        
        # 使用与test_style.py完全相同的payload格式
        payload = {
            'model': config.MODELSCOPE_MODEL,
            'prompt': style_prompt,
            'image_url': image_url,
            'size': image_size
        }
        
        headers = {
            'Authorization': f'Bearer {config.MODELSCOPE_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        print(f"[INFO] 调用ModelScope API...")
        print(f"Response status: checking...")
        
        # 使用与test_style.py相同的请求方式
        response = requests.post(
            url, 
            data=json.dumps(payload, ensure_ascii=False).encode('utf-8'), 
            headers=headers,
            timeout=config.STYLE_PROCESSING_TIMEOUT
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error: {response.text}")
            return {
                'success': False,
                'error': f'API请求失败: 状态码 {response.status_code}, 响应: {response.text}'
            }
        
        # 解析响应
        response_data = response.json()
        print("API response received successfully")
        
        # 下载风格化后的图像 - 与test_style.py相同的方式
        styled_image_url = response_data['images'][0]['url']
        image_response = requests.get(styled_image_url)
        
        if image_response.status_code != 200:
            return {
                'success': False,
                'error': f'下载风格化图像失败: 状态码 {image_response.status_code}'
            }
        
        # 转换为PIL图像对象
        styled_image = Image.open(BytesIO(image_response.content))
        print(f"[INFO] 风格化图像处理成功，尺寸: {styled_image.size}")
        
        return {
            'success': True,
            'styled_image': styled_image,
            'styled_image_url': styled_image_url,
            'image_data': image_response.content,
            'original_path': image_path,
            'style_prompt': style_prompt,
            'uploaded_image_url': image_url
        }
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': f'风格化处理异常: {str(e)}'
        }

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

# 改进的异步事件循环管理
_async_loop = None
_loop_thread = None

def get_or_create_event_loop():
    """获取或创建事件循环"""
    global _async_loop, _loop_thread
    
    if _async_loop is None or _async_loop.is_closed():
        print("[INFO] 创建新的事件循环...")
        _async_loop = asyncio.new_event_loop()
        
        # 创建普通线程运行事件循环（非守护线程）
        def run_loop():
            try:
                asyncio.set_event_loop(_async_loop)
                _async_loop.run_forever()
            except Exception as e:
                print(f"[ERROR] 事件循环异常: {e}")
            finally:
                print("[INFO] 事件循环已停止")
        
        _loop_thread = threading.Thread(target=run_loop, daemon=False)
        _loop_thread.start()
        print("[INFO] 事件循环线程已启动")
    
    return _async_loop

def cleanup_event_loop():
    """清理事件循环资源"""
    global _async_loop, _loop_thread
    
    if _async_loop and not _async_loop.is_closed():
        print("[INFO] 正在清理事件循环...")
        # 停止事件循环
        _async_loop.call_soon_threadsafe(_async_loop.stop)
        
        # 等待线程结束（最多等待5秒）
        if _loop_thread and _loop_thread.is_alive():
            _loop_thread.join(timeout=5)
            if _loop_thread.is_alive():
                print("[WARNING] 事件循环线程未能在5秒内结束")
        
        # 关闭事件循环
        if not _async_loop.is_closed():
            _async_loop.close()
        
        _async_loop = None
        _loop_thread = None
        print("[INFO] 事件循环清理完成")

# 注册程序退出时的清理函数
atexit.register(cleanup_event_loop)

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
            'invalid_files': invalid_files if invalid_files else None,
            'video_path': saved_files[0]['filepath'] if saved_files else None,
            'files': saved_files
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
        max_concurrent = int(request.form.get('max_concurrent', config.MAX_CONCURRENT_REQUESTS))  # 使用配置文件中的默认值
        
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
        max_concurrent = int(request.form.get('max_concurrent', config.MAX_CONCURRENT_REQUESTS))  # 使用配置文件中的默认值
        
        # 更新任务状态
        task_status[task_id]['status'] = 'unified_processing'
        task_status[task_id]['message'] = '正在进行统一智能处理...'
        task_status[task_id]['progress'] = 0
        
        # 处理每个视频
        unified_results = []
        
        for i, video_file in enumerate(video_files):
            try:
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
                
                print(f"[INFO] 开始处理视频: {video_name}")
                
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
                
                print(f"[INFO] 视频处理完成: {video_name}, 成功: {result.get('success', False)}")
                
            except Exception as video_error:
                print(f"[ERROR] 处理视频 {video_name} 时出错: {str(video_error)}")
                result = {
                    'success': False,
                    'error': f'处理视频时出错: {str(video_error)}'
                }
            
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

# 9. 同步故事生成API
@app.route('/api/generate/story', methods=['POST'])
def generate_story():
    """同步三阶段故事生成API"""
    try:
        print("[INFO] 收到故事生成请求")
        
        # 获取JSON数据
        if not request.is_json:
            return jsonify({
                'success': False,
                'message': '请求必须是JSON格式'
            }), 400
        
        input_data = request.get_json()
        print(f"[INFO] 输入数据包含 {len(input_data.get('keyframes', []))} 个关键帧")
        
        # 验证输入数据格式
        if 'video_info' not in input_data or 'keyframes' not in input_data:
            return jsonify({
                'success': False,
                'message': '输入数据格式错误，需要包含video_info和keyframes字段'
            }), 400
        
                # 验证关键帧数据
        keyframes = input_data['keyframes']
        if not isinstance(keyframes, list) or len(keyframes) == 0:
            return jsonify({
                'success': False,
                'message': '关键帧数据不能为空'
            }), 400

        # 处理可选的文体风格参数
        style = input_data.get('style', None)
        if style and not isinstance(style, str):
            return jsonify({
                'success': False,
                'message': '文体风格参数必须是字符串类型'
            }), 400
        
        # 将风格参数添加到输入数据中
        if style:
            input_data['style'] = style.strip()
            print(f"[INFO] 使用文体风格: {style}")

        # 为输入数据添加task_id（如果没有的话）
        if 'task_id' not in input_data['video_info']:
            input_data['video_info']['task_id'] = str(uuid.uuid4())
        
        task_id = input_data['video_info']['task_id']
        print(f"[INFO] 开始同步故事生成任务: {task_id}")
        
        # 导入故事生成系统
        from story_generation_agents import StoryGenerationSystem
        
        # 创建故事生成系统实例，指定输出目录
        system = StoryGenerationSystem(output_dir=app.config['STORIES_FOLDER'])
        
        # 同步执行故事生成
        # 创建新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            print(f"[INFO] 开始执行故事生成")
            result = loop.run_until_complete(system.generate_story(input_data))
            print(f"[INFO] 故事生成完成，结果: {result.get('success', False)}")
            
        finally:
            loop.close()
        
        # 返回结果
        if result['success']:
            print(f"[INFO] 故事生成成功")
            return jsonify({
                'success': True,
                'message': '故事生成完成',
                'task_id': task_id,
                'story_result': result
            }), 200
        else:
            print(f"[INFO] 故事生成失败: {result.get('error', '未知错误')}")
            return jsonify({
                'success': False,
                'message': f'故事生成失败: {result.get("error", "未知错误")}',
                'task_id': task_id,
                'error': result.get("error", "未知错误")
            }), 500
            
    except Exception as e:
        print(f"[ERROR] 故事生成异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'故事生成请求失败: {str(e)}'
        }), 500

# 10. 获取可用文体风格列表API
@app.route('/api/story/styles', methods=['GET'])
def get_story_styles():
    """获取可用的文体风格列表"""
    try:
        from story_generation_agents import MasterEditorAgent, LLMClient
        
        # 创建一个临时的MasterEditorAgent实例来获取风格模板
        temp_llm_client = LLMClient()
        temp_agent = MasterEditorAgent(temp_llm_client)
        
        styles = []
        for style_name, style_data in temp_agent.style_templates.items():
            styles.append({
                'name': style_name,
                'description': style_data['description']
            })
        
        return jsonify({
            'success': True,
            'message': '获取文体风格列表成功',
            'styles': styles,
            'total_count': len(styles)
        }), 200
        
    except Exception as e:
        print(f"[ERROR] 获取文体风格列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取文体风格列表失败: {str(e)}'
        }), 500

# 11. 获取故事生成结果API（保留用于兼容性，但现在故事生成是同步的）
@app.route('/api/story/result/<task_id>', methods=['GET'])
def get_story_result(task_id):
    """获取故事生成结果（兼容性API）"""
    return jsonify({
        'success': False,
        'message': '故事生成现在是同步的，请直接调用 /api/generate/story 获取结果'
    }), 400

# 11. 获取故事文件API
@app.route('/api/stories/<path:filename>', methods=['GET'])
def get_story_file(filename):
    """获取故事文件"""
    try:
        # 检查文件是否存在
        file_path = os.path.join(app.config['STORIES_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_from_directory(app.config['STORIES_FOLDER'], filename)
        else:
            return jsonify({
                'success': False,
                'message': '找不到请求的故事文件'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取故事文件失败: {str(e)}'
        }), 500

# 12. 关键帧风格化处理API
@app.route('/api/process/style-transform', methods=['POST'])
def process_style_transform():
    """关键帧风格化处理API"""
    try:
        # 获取JSON数据
        if not request.is_json:
            return jsonify({
                'success': False,
                'message': '请求必须是JSON格式'
            }), 400
        
        input_data = request.get_json()
        
        # 验证必需参数
        task_id = input_data.get('task_id')
        if not task_id:
            return jsonify({
                'success': False,
                'message': '缺少任务ID'
            }), 400
        
        # 检查任务是否存在，如果不存在则创建新的任务状态（用于直接风格化处理）
        if task_id not in task_status:
            # 如果用户提供了图像URL，则允许直接处理
            if input_data.get('image_urls'):
                task_status[task_id] = {
                    'status': 'style_processing',
                    'progress': 0,
                    'message': '直接风格化处理中...',
                    'created_time': datetime.now().strftime('%Y%m%d_%H%M%S')
                }
                print(f"[INFO] 创建新任务进行直接风格化处理: {task_id}")
            else:
                return jsonify({
                    'success': False,
                    'message': '任务不存在且未提供图像URL'
                }), 404
        
        # 获取参数
        style_prompt = input_data.get('style_prompt')  # 可选，使用默认值
        image_size = input_data.get('image_size')  # 可选，使用默认值
        
        # 获取要处理的图像信息
        image_urls = input_data.get('image_urls', [])
        if not image_urls:
            # 如果没有指定图像URL，尝试从任务结果中获取关键帧
            unified_results = task_status[task_id].get('unified_results', [])
            key_frames_results = task_status[task_id].get('key_frames_results', [])
            
            if unified_results:
                # 从统一处理结果中获取关键帧
                for result in unified_results:
                    if isinstance(result, dict) and result.get('success', False):
                        key_frame_paths = result.get('key_frame_paths', [])
                        for path in key_frame_paths:
                            # 构建图像URL（假设可以通过API访问）
                            filename = os.path.basename(path)
                            image_url = f"http://localhost:5001/api/frames/{task_id}/{filename}"
                            image_urls.append({
                                'url': image_url,
                                'local_path': path,
                                'filename': filename
                            })
            elif key_frames_results:
                # 从关键帧结果中获取
                for result in key_frames_results:
                    key_frame_paths = result.get('key_frame_paths', [])
                    for path in key_frame_paths:
                        filename = os.path.basename(path)
                        image_url = f"http://localhost:5001/api/frames/{task_id}/{filename}"
                        image_urls.append({
                            'url': image_url,
                            'local_path': path,
                            'filename': filename
                        })
        
        if not image_urls:
            return jsonify({
                'success': False,
                'message': '没有找到可以处理的图像'
            }), 400
        
        # 更新任务状态
        task_status[task_id]['status'] = 'style_processing'
        task_status[task_id]['message'] = '正在进行风格化处理...'
        task_status[task_id]['progress'] = 0
        
        # 处理每个图像
        style_results = []
        total_images = len(image_urls)
        
        for i, image_info in enumerate(image_urls):
            try:
                # 更新进度
                progress = int((i / total_images) * 100)
                task_status[task_id]['progress'] = progress
                task_status[task_id]['message'] = f'正在处理第 {i+1}/{total_images} 张图像...'
                
                # 获取图像URL
                if isinstance(image_info, dict):
                    image_url = image_info['url']
                    filename = image_info.get('filename', f'image_{i}')
                    local_path = image_info.get('local_path', '')
                else:
                    image_url = image_info
                    filename = f'image_{i}'
                    local_path = ''
                
                # 进行风格化处理
                print(f"[INFO] 开始处理图像 {i+1}/{total_images}: {filename}")
                style_result = style_transform_image(
                    image_url=image_url,
                    style_prompt=style_prompt,
                    image_size=image_size
                )
                
                if style_result['success']:
                    # 保存风格化后的图像
                    styled_image = style_result['styled_image']
                    
                    # 生成保存路径
                    if local_path:
                        # 在原图像目录中保存
                        dir_path = os.path.dirname(local_path)
                        base_name = os.path.splitext(os.path.basename(local_path))[0]
                        styled_filename = f"{base_name}_styled.jpg"
                        styled_path = os.path.join(dir_path, styled_filename)
                    else:
                        # 在frames目录中保存
                        styled_filename = f"styled_{filename}"
                        styled_path = os.path.join(app.config['FRAMES_FOLDER'], styled_filename)
                    
                    # 保存图像
                    styled_image.save(styled_path, 'JPEG', quality=95)
                    
                    # 记录结果
                    style_results.append({
                        'success': True,
                        'original_url': image_url,
                        'original_filename': filename,
                        'styled_path': styled_path,
                        'styled_filename': os.path.basename(styled_path),
                        'styled_image_url': style_result['styled_image_url'],
                        'style_prompt': style_result['style_prompt']
                    })
                    
                    print(f"[INFO] 图像风格化完成: {styled_path}")
                
                else:
                    # 记录失败结果
                    style_results.append({
                        'success': False,
                        'original_url': image_url,
                        'original_filename': filename,
                        'error': style_result['error']
                    })
                    
                    print(f"[ERROR] 图像风格化失败: {style_result['error']}")
            
            except Exception as image_error:
                # 记录单个图像处理错误
                style_results.append({
                    'success': False,
                    'original_url': image_url if 'image_url' in locals() else 'unknown',
                    'original_filename': filename if 'filename' in locals() else 'unknown',
                    'error': f'处理图像时出错: {str(image_error)}'
                })
                print(f"[ERROR] 处理图像时出错: {str(image_error)}")
            
            # 更新进度
            task_status[task_id]['progress'] = int(((i + 1) / total_images) * 100)
        
        # 统计处理结果
        successful_count = sum(1 for result in style_results if result['success'])
        failed_count = total_images - successful_count
        
        # 更新任务状态
        task_status[task_id]['status'] = 'style_completed'
        task_status[task_id]['message'] = f'风格化处理完成，成功: {successful_count}，失败: {failed_count}'
        task_status[task_id]['progress'] = 100
        task_status[task_id]['style_results'] = style_results
        
        return jsonify({
            'success': True,
            'message': '风格化处理完成',
            'task_id': task_id,
            'processed_count': total_images,
            'successful_count': successful_count,
            'failed_count': failed_count,
            'style_results': style_results,
            'style_prompt': style_prompt or config.DEFAULT_STYLE_PROMPT
        }), 200
        
    except Exception as e:
        if 'task_id' in locals() and task_id in task_status:
            task_status[task_id]['status'] = 'error'
            task_status[task_id]['message'] = f'风格化处理失败: {str(e)}'
            task_status[task_id]['error'] = str(e)
            
        print(f"[ERROR] 风格化处理异常: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'风格化处理失败: {str(e)}'
        }), 500

# 13. 完整连环画生成API - 集成接口
@app.route('/api/process/complete-comic', methods=['POST'])
def process_complete_comic():
    """
    完整连环画生成API - 一键完成关键帧提取、故事生成、风格化处理
    
    前置条件：前端已完成视频上传API和基础帧提取API调用
    
    接受参数：
    - video_path: 视频文件路径（前端直接传入）
    - task_id: 任务ID（从前面的API调用中获得）
    - story_style: 故事风格关键词（前端指定）
    - 其他处理参数...
    
    这个接口将三个核心模块集成到一个流程中：
    1. 关键帧提取 - 从视频中智能提取关键帧
    2. 故事生成 - 为每个关键帧生成故事文本和互动提问
    3. 风格化处理 - 对关键帧进行艺术风格化处理
    
    返回完整的连环画数据，前端只需调用一次即可获得最终结果
    """
    try:
        print("[INFO] 收到完整连环画生成请求")
        
        # 获取必要参数
        video_path = request.form.get('video_path')
        task_id = request.form.get('task_id')
        story_style = request.form.get('story_style', '诗意散文')  # 故事风格关键词
        
        # 验证必要参数
        if not video_path:
            return jsonify({
                'success': False,
                'message': '缺少视频路径参数 video_path'
            }), 400
            
        if not task_id:
            return jsonify({
                'success': False,
                'message': '缺少任务ID参数 task_id'
            }), 400
        
        # 验证视频文件存在
        if not os.path.exists(video_path):
            return jsonify({
                'success': False,
                'message': f'视频文件不存在: {video_path}'
            }), 400
        
        # 验证任务ID存在（可选，根据实际需求）
        if task_id not in task_status:
            print(f"[WARNING] 任务ID {task_id} 不在状态管理中，创建新状态记录")
            # 为直接调用创建基础状态记录
            task_status[task_id] = {
                'status': 'ready_for_comic',
                'message': '准备生成连环画...',
                'progress': 0,
                'created_at': datetime.now().isoformat()
            }
        
        print(f"[INFO] 视频路径: {video_path}")
        print(f"[INFO] 任务ID: {task_id}")
        print(f"[INFO] 故事风格: {story_style}")
        
        # 获取处理参数
        params = {
            'target_frames': int(request.form.get('target_frames', 8)),
            'frame_interval': float(request.form.get('frame_interval', 1.0)),
            'significance_weight': float(request.form.get('significance_weight', 0.6)),
            'quality_weight': float(request.form.get('quality_weight', 0.4)),
            'style_prompt': request.form.get('style_prompt'),  # 可选
            'image_size': request.form.get('image_size'),      # 可选
            'story_style': story_style,                        # 故事风格关键词
            'max_concurrent': int(request.form.get('max_concurrent', config.MAX_CONCURRENT_REQUESTS))
        }
        
        print(f"[INFO] 处理参数: {params}")
        
        # 更新任务状态
        task_status[task_id]['status'] = 'complete_comic_processing'
        task_status[task_id]['message'] = '开始完整连环画生成...'
        task_status[task_id]['progress'] = 0
        task_status[task_id]['stage'] = 'initializing'
        
        # 创建视频文件信息（基于传入的路径）
        video_filename = os.path.basename(video_path)
        video_name = os.path.splitext(video_filename)[0]
        
        video_file_info = {
            'original_name': video_filename,
            'saved_name': video_filename,
            'filepath': video_path,
            'size': os.path.getsize(video_path)
        }
        
        print(f"[INFO] 开始处理视频: {video_name}")

        # 开始异步处理
        def async_complete_comic_processing():
            """异步执行完整连环画生成"""
            try:
                # 添加内存检查
                memory_info = check_memory_usage()
                if memory_info and memory_info['percentage'] > config.MAX_MEMORY_USAGE:
                    raise Exception(f"内存使用率过高 ({memory_info['percentage']:.1f}%)，停止处理")
                
                # 阶段1: 关键帧提取 (0-30%)
                task_status[task_id]['stage'] = 'extracting_keyframes'
                task_status[task_id]['message'] = '正在提取关键帧...'
                task_status[task_id]['progress'] = 10
                
                keyframes_result = extract_keyframes_for_comic(
                    video_path, task_id, video_name, params
                )
                
                if not keyframes_result['success']:
                    task_status[task_id]['status'] = 'complete_comic_failed'
                    task_status[task_id]['message'] = f'关键帧提取失败: {keyframes_result["error"]}'
                    task_status[task_id]['error'] = keyframes_result["error"]
                    return
                
                # 中途内存检查
                check_memory_usage()
                
                # 阶段2: 故事生成 (30-70%)
                task_status[task_id]['stage'] = 'generating_story'
                task_status[task_id]['message'] = '正在生成故事...'
                task_status[task_id]['progress'] = 40
                
                story_result = generate_story_for_comic(
                    keyframes_result, video_file_info, task_id, params
                )
                
                if not story_result['success']:
                    task_status[task_id]['status'] = 'complete_comic_failed'
                    task_status[task_id]['message'] = f'故事生成失败: {story_result["error"]}'
                    task_status[task_id]['error'] = story_result["error"]
                    return
                
                # 中途内存检查
                check_memory_usage()
                
                # 阶段3: 风格化处理 (70-100%)
                task_status[task_id]['stage'] = 'stylizing_frames'
                task_status[task_id]['message'] = '正在风格化处理...'
                task_status[task_id]['progress'] = 70
                
                stylized_result = stylize_frames_for_comic(
                    keyframes_result, story_result, task_id, params
                )
                
                if not stylized_result['success']:
                    task_status[task_id]['status'] = 'complete_comic_failed'
                    task_status[task_id]['message'] = f'风格化处理失败: {stylized_result["error"]}'
                    task_status[task_id]['error'] = stylized_result["error"]
                    return
                
                # 整合最终结果
                comic_result = integrate_comic_result(
                    keyframes_result, story_result, stylized_result, video_file_info
                )
                
                # 更新最终状态
                task_status[task_id]['status'] = 'complete_comic_completed'
                task_status[task_id]['progress'] = 100
                task_status[task_id]['message'] = '完整连环画生成完成'
                task_status[task_id]['stage'] = 'completed'
                task_status[task_id]['complete_comic_results'] = [comic_result]  # 单个视频结果
                task_status[task_id]['completed_time'] = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                print(f"[INFO] 任务 {task_id} 完整连环画生成完成")
                
                # 最后执行垃圾回收
                gc.collect()
                
            except MemoryError as e:
                print(f"[ERROR] 内存不足: {str(e)}")
                task_status[task_id]['status'] = 'complete_comic_failed'
                task_status[task_id]['message'] = f'内存不足，无法完成处理: {str(e)}'
                task_status[task_id]['error'] = f'MemoryError: {str(e)}'
                # 强制垃圾回收释放内存
                gc.collect()
                
            except ConnectionError as e:
                print(f"[ERROR] 网络连接错误: {str(e)}")
                task_status[task_id]['status'] = 'complete_comic_failed'
                task_status[task_id]['message'] = f'网络连接失败: {str(e)}'
                task_status[task_id]['error'] = f'ConnectionError: {str(e)}'
                
            except TimeoutError as e:
                print(f"[ERROR] 操作超时: {str(e)}")
                task_status[task_id]['status'] = 'complete_comic_failed'
                task_status[task_id]['message'] = f'操作超时: {str(e)}'
                task_status[task_id]['error'] = f'TimeoutError: {str(e)}'
                
            except Exception as e:
                print(f"[ERROR] 完整连环画生成异常: {str(e)}")
                import traceback
                traceback.print_exc()
                
                task_status[task_id]['status'] = 'complete_comic_failed'
                task_status[task_id]['message'] = f'完整连环画生成失败: {str(e)}'
                task_status[task_id]['error'] = str(e)
                task_status[task_id]['traceback'] = traceback.format_exc()
                
                # 异常时也执行垃圾回收
                gc.collect()
            
            finally:
                # 确保在任何情况下都记录完成时间
                if 'completed_time' not in task_status[task_id]:
                    task_status[task_id]['completed_time'] = datetime.now().strftime('%Y%m%d_%H%M%S')
                print(f"[INFO] 任务 {task_id} 处理结束，状态: {task_status[task_id].get('status', 'unknown')}")
        
        # 启动异步处理线程
        processing_thread = threading.Thread(target=async_complete_comic_processing)
        processing_thread.daemon = True
        processing_thread.start()
        
        # 返回任务启动成功响应
        return jsonify({
            'success': True,
            'message': '完整连环画生成已启动',
            'task_id': task_id,
            'status': 'complete_comic_processing',
            'progress': 0,
            'stage': 'initializing',
            'video_path': video_path,
            'story_style': story_style
        }), 200
        
    except Exception as e:
        print(f"[ERROR] 完整连环画生成请求异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'完整连环画生成请求失败: {str(e)}'
        }), 500

def extract_keyframes_for_comic(video_path, task_id, video_name, params):
    """为连环画提取关键帧"""
    try:
        # 🔧 解决OpenCV中文路径问题：使用安全的英文路径策略
        import re
        import hashlib
        
        # 策略1：使用任务ID + 时间戳作为目录名（纯英文数字）
        import time
        timestamp = int(time.time())
        safe_dir_name = f"{task_id}_{timestamp}"
        
        print(f"[INFO] 原始视频名称: {video_name}")
        print(f"[INFO] 安全目录名称: {safe_dir_name}")
        
        # 创建视频专属的输出目录（使用安全名称）
        output_dir = os.path.join(app.config['FRAMES_FOLDER'], safe_dir_name)
        
        # 确保路径正规化
        output_dir = os.path.normpath(output_dir)
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"[INFO] 输出目录: {output_dir}")
        
        # 验证目录创建成功且可写
        if not os.path.exists(output_dir):
            raise ValueError(f"无法创建输出目录: {output_dir}")
        
        if not os.access(output_dir, os.W_OK):
            raise ValueError(f"输出目录不可写: {output_dir}")
        
        print(f"[INFO] 目录验证成功，开始创建抽帧器")
        
        # 创建抽帧器
        extractor = DiversityFrameExtractor(output_dir=output_dir)
        
        print(f"[INFO] 抽帧器创建成功，开始关键帧提取")
        print(f"[INFO] 提取参数: target_frames={params['target_frames']}, interval={params['frame_interval']}")
        
        # 执行关键帧提取
        # 获取事件循环并运行异步任务
        loop = get_or_create_event_loop()
        future = asyncio.run_coroutine_threadsafe(
            extractor.unified_smart_extraction_async(
                video_path=video_path,
                target_key_frames=params['target_frames'],
                base_frame_interval=params['frame_interval'],
                significance_weight=params['significance_weight'],
                quality_weight=params['quality_weight'],
                max_concurrent=params['max_concurrent']
            ),
            loop
        )
        # 等待异步任务完成并获取结果
        result = future.result()
        
        print(f"[INFO] 关键帧提取完成，结果: success={result.get('success', False)}")
        
        if result['success']:
            print(f"[INFO] 关键帧提取成功: {len(result['selected_frames'])} 个关键帧")
            return {
                'success': True,
                'keyframes': result['selected_frames'],
                'key_frame_paths': result['key_frame_paths'],
                'json_file_path': result['json_file_path'],
                'output_dir': output_dir,
                'processing_stats': result['processing_stats'],
                'original_video_name': video_name,  # 保留原始名称用于显示
                'safe_dir_name': safe_dir_name      # 记录安全目录名
            }
        else:
            error_msg = result.get('error', '关键帧提取失败')
            print(f"[ERROR] 关键帧提取失败: {error_msg}")
            return {
                'success': False,
                'error': error_msg
            }
            
    except Exception as e:
        error_msg = f'关键帧提取异常: {str(e)}'
        print(f"[ERROR] {error_msg}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': error_msg
        }

def generate_story_for_comic(keyframes_result, video_file, task_id, params):
    """为连环画生成故事"""
    try:
        # 准备故事生成的输入数据
        input_data = {
            'video_info': {
                'task_id': task_id,
                'video_name': video_file['original_name'],  # 修正字段名
                'video_path': video_file['filepath']        # 修正字段名  
            },
            'keyframes': []
        }
        
        # 添加文体风格（如果指定）
        if params.get('story_style'):
            input_data['style'] = params['story_style']
        
        # 构建关键帧数据 - 直接使用关键帧提取的结果
        for keyframe in keyframes_result['keyframes']:
            keyframe_data = {
                'index': keyframe.get('index', 1),  # 使用原始索引
                'filename': keyframe.get('filename', ''),
                'photo_path': keyframe.get('photo_path', ''),
                'combined_score': keyframe.get('combined_score', 0.0),
                'significance_score': keyframe.get('significance_score', 0.0),
                'quality_score': keyframe.get('quality_score', 0.0),
                'description': keyframe.get('description', ''),
                'timestamp': keyframe.get('timestamp', 0.0),
                'frame_position': keyframe.get('frame_position', 0)
            }
            input_data['keyframes'].append(keyframe_data)
        
        # 如果关键帧数据中缺少描述，尝试从JSON文件中读取
        json_file_path = keyframes_result.get('json_file_path')
        if json_file_path and os.path.exists(json_file_path):
            try:
                with open(json_file_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                    json_keyframes = json_data.get('keyframes', [])
                    
                    # 更新描述信息
                    for i, keyframe_data in enumerate(input_data['keyframes']):
                        if i < len(json_keyframes) and json_keyframes[i].get('description'):
                            keyframe_data['description'] = json_keyframes[i]['description']
                            keyframe_data['photo_path'] = json_keyframes[i].get('photo_path', keyframe_data['photo_path'])
                            
                print(f"[INFO] 从JSON文件成功读取了关键帧描述信息")
            except Exception as e:
                print(f"[WARNING] 读取关键帧JSON文件失败: {e}")
        
        print(f"[INFO] 开始故事生成，输入数据包含 {len(input_data['keyframes'])} 个关键帧")
        
        # 导入故事生成系统
        from story_generation_agents import StoryGenerationSystem
        
        # 创建故事生成系统实例
        system = StoryGenerationSystem(output_dir=app.config['STORIES_FOLDER'])
        
        # 同步执行故事生成
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(system.generate_story(input_data))
        finally:
            loop.close()
        
        if result['success']:
            print(f"[INFO] 故事生成成功")
            return {
                'success': True,
                'story_data': result,  # 直接使用result，因为它已经包含了所有故事数据
                'story_file_path': result.get('json_file_path', '')
            }
        else:
            return {
                'success': False,
                'error': result.get('error', '故事生成失败')
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'故事生成异常: {str(e)}'
        }

def stylize_single_frame(frame_data, styled_dir, params):
    """
    处理单个关键帧的风格化
    这是从原始方法中提取出来的单帧处理逻辑，用于并发执行
    
    Args:
        frame_data: 包含帧索引和路径的字典 {'index': i, 'path': frame_path}
        styled_dir: 风格化图像保存目录
        params: 风格化参数
    
    Returns:
        dict: 风格化结果
    """
    i = frame_data['index']
    frame_path = frame_data['path']
    
    try:
        print(f"[INFO] 处理第 {i+1} 个关键帧: {frame_path}")
        filename = os.path.basename(frame_path)
        
        # 检查文件是否存在
        if not os.path.exists(frame_path):
            print(f"[WARNING] 关键帧文件不存在: {frame_path}")
            return {
                'original_path': frame_path,
                'styled_path': frame_path,
                'styled_filename': filename,
                'index': i,
                'style_failed': True,
                'error': '原始文件不存在'
            }
        
        # 执行风格化处理
        style_result = style_transform_image(
            image_path=frame_path,
            style_prompt=params.get('style_prompt'),
            image_size=params.get('image_size')
        )
        
        if style_result['success']:
            # 保存风格化后的图像
            styled_filename = f"styled_{filename}"
            styled_path = os.path.join(styled_dir, styled_filename)
            
            # 保存风格化图像数据
            with open(styled_path, 'wb') as f:
                f.write(style_result['image_data'])
            
            print(f"[INFO] 风格化图像已保存: {styled_path}")
            print(f"[INFO] 风格化成功: {filename}")
            
            return {
                'original_path': frame_path,
                'styled_path': styled_path,
                'styled_filename': styled_filename,
                'index': i,
                'style_failed': False,
                'styled_image_url': style_result['styled_image_url']
            }
        else:
            print(f"[ERROR] 风格化失败: {style_result['error']}")
            return {
                'original_path': frame_path,
                'styled_path': frame_path,
                'styled_filename': filename,
                'index': i,
                'style_failed': True,
                'error': style_result['error']
            }
            
    except Exception as frame_error:
        print(f"[ERROR] 处理帧 {i} 风格化时出错: {str(frame_error)}")
        return {
            'original_path': frame_path,
            'styled_path': frame_path,
            'styled_filename': os.path.basename(frame_path),
            'index': i,
            'style_failed': True,
            'error': str(frame_error)
        }

def stylize_frames_for_comic(keyframes_result, story_result, task_id, params):
    """为连环画风格化关键帧 - 顺序处理版本"""
    try:
        import time
        
        styled_frames = []
        
        # 从关键帧结果中获取路径信息
        key_frame_paths = keyframes_result.get('key_frame_paths', [])
        
        # 如果没有key_frame_paths，从keyframes数据中构建路径
        if not key_frame_paths:
            output_dir = keyframes_result.get('output_dir', '')
            keyframes = keyframes_result.get('keyframes', [])
            key_frame_paths = []
            
            for keyframe in keyframes:
                if 'photo_path' in keyframe:
                    # 使用绝对路径或相对于输出目录的路径
                    photo_path = keyframe['photo_path']
                    if not os.path.isabs(photo_path) and output_dir:
                        # 如果是相对路径，转换为绝对路径
                        photo_path = os.path.join(output_dir, os.path.basename(photo_path))
                    key_frame_paths.append(photo_path)
                elif 'filename' in keyframe:
                    # 根据文件名构建路径
                    filename = keyframe['filename']
                    if output_dir:
                        photo_path = os.path.join(output_dir, filename)
                        key_frame_paths.append(photo_path)
        
        print(f"[INFO] 风格化处理：找到 {len(key_frame_paths)} 个关键帧路径")
        print(f"[INFO] 使用顺序处理模式，逐个处理关键帧")
        
        # 创建风格化输出目录
        styled_dir = os.path.join(keyframes_result['output_dir'], 'styled')
        os.makedirs(styled_dir, exist_ok=True)
        
        # 记录开始时间
        start_time = time.time()
        
        # 顺序处理每个关键帧
        styled_frames = []
        successful_frames = 0
        
        for i, frame_path in enumerate(key_frame_paths):
            print(f"[INFO] 开始处理第 {i+1}/{len(key_frame_paths)} 个关键帧: {frame_path}")
            
            # 准备帧数据
            frame_data = {'index': i, 'path': frame_path}
            
            try:
                # 调用单帧处理方法
                result = stylize_single_frame(frame_data, styled_dir, params)
                styled_frames.append(result)
                
                # 统计成功数量
                if not result.get('style_failed', False):
                    successful_frames += 1
                    success_status = "成功"
                else:
                    success_status = "失败"
                
                # 显示进度
                print(f"[INFO] 进度: {i+1}/{len(key_frame_paths)} - 帧{i} {success_status}")
                
                # 计算预估剩余时间
                elapsed_time = time.time() - start_time
                if i > 0:  # 避免除以0
                    avg_time_per_frame = elapsed_time / (i + 1)
                    remaining_frames = len(key_frame_paths) - (i + 1)
                    estimated_remaining = avg_time_per_frame * remaining_frames
                    print(f"[INFO] 预计剩余时间: {estimated_remaining:.1f} 秒")
                
            except Exception as exc:
                print(f"[ERROR] 处理帧 {i} 时发生异常: {exc}")
                # 创建失败结果
                error_result = {
                    'original_path': frame_path,
                    'styled_path': frame_path,
                    'styled_filename': os.path.basename(frame_path),
                    'index': i,
                    'style_failed': True,
                    'error': str(exc)
                }
                styled_frames.append(error_result)
        
        # 统计处理结果
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"[INFO] 顺序风格化处理完成！")
        print(f"[INFO] 总处理时间: {processing_time:.2f} 秒")
        print(f"[INFO] 成功处理: {successful_frames}/{len(key_frame_paths)} 个关键帧")
        print(f"[INFO] 平均每帧处理时间: {processing_time/len(key_frame_paths):.2f} 秒")
        
        return {
            'success': True,
            'styled_frames': styled_frames,
            'styled_dir': styled_dir,
            'processing_stats': {
                'total_frames': len(key_frame_paths),
                'successful_frames': successful_frames,
                'failed_frames': len(key_frame_paths) - successful_frames,
                'processing_time': processing_time,
                'processing_mode': 'sequential'
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'风格化处理异常: {str(e)}'
        }

def integrate_comic_result(keyframes_result, story_result, stylized_result, video_file):
    """整合连环画最终结果"""
    try:
        story_data = story_result['story_data']
        styled_frames = stylized_result['styled_frames']
        
        # 构建完整的连环画数据
        comic_pages = []
        
        # 获取故事文本数据
        final_narrations = story_data.get('final_narrations', [])
        
        for i, narration in enumerate(final_narrations):
            # 查找对应的风格化帧
            styled_frame = next(
                (sf for sf in styled_frames if sf['index'] == i), 
                None
            )
            
            page = {
                'page_index': i,
                'story_text': narration.get('story_text', ''),
                'original_frame_path': narration.get('frame_path', ''),
                'styled_frame_path': styled_frame['styled_path'] if styled_frame else narration.get('frame_path', ''),
                'styled_filename': styled_frame['styled_filename'] if styled_frame else os.path.basename(narration.get('frame_path', '')),
                'frame_index': narration.get('frame_index', i),
                'style_applied': styled_frame and not styled_frame.get('style_failed', False) if styled_frame else False
            }
            comic_pages.append(page)
        
        # 构建最终结果
        final_result = {
            'video_name': video_file['original_name'],
            'success': True,
            'comic_data': {
                'story_info': {
                    'overall_theme': story_data.get('overall_theme', ''),
                    'title': story_data.get('overall_theme', ''),  # 使用主题作为标题
                    'summary': story_data.get('overall_theme', ''),  # 使用主题作为概要
                    'total_pages': len(comic_pages),
                    'video_name': video_file['original_name'],
                    'creation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                },
                'pages': comic_pages,
                'interactive_questions': story_data.get('interactive_questions', [])
            },
            'processing_info': {
                'keyframes_extracted': len(keyframes_result['keyframes']),
                'story_generated': len(final_narrations),
                'frames_stylized': len([sf for sf in styled_frames if not sf.get('style_failed', False)]),
                'keyframes_output_dir': keyframes_result['output_dir'],
                'story_file_path': story_result.get('story_file_path', ''),
                'styled_frames_dir': stylized_result['styled_dir']
            }
        }
        
        print(f"[INFO] 连环画结果整合完成: {len(comic_pages)} 页")
        return final_result
        
    except Exception as e:
        return {
            'video_name': video_file['original_name'],
            'success': False,
            'error': f'结果整合失败: {str(e)}'
        }

# 14. 获取完整连环画结果API
@app.route('/api/comic/result/<task_id>', methods=['GET'])
def get_complete_comic_result(task_id):
    """获取完整连环画生成结果"""
    try:
        if task_id not in task_status:
            return jsonify({
                'success': False,
                'message': '任务不存在'
            }), 404
        
        task_info = task_status[task_id]
        
        # 检查任务状态
        if task_info['status'] not in ['complete_comic_completed', 'complete_comic_failed']:
            return jsonify({
                'success': False,
                'message': '连环画生成尚未完成',
                'status': task_info['status'],
                'progress': task_info.get('progress', 0),
                'stage': task_info.get('stage', 'unknown'),
                'current_message': task_info.get('message', '')
            }), 202  # 202 表示正在处理中
        
        if task_info['status'] == 'complete_comic_failed':
            return jsonify({
                'success': False,
                'message': '连环画生成失败',
                'error': task_info.get('error', '未知错误')
            }), 500
        
        # 返回完整连环画结果
        complete_results = task_info.get('complete_comic_results', [])
        
        # 过滤成功的结果
        successful_results = [r for r in complete_results if r.get('success', False)]
        failed_results = [r for r in complete_results if not r.get('success', False)]
        
        return jsonify({
            'success': True,
            'message': '连环画生成完成',
            'task_id': task_id,
            'results': {
                'successful_comics': successful_results,
                'failed_comics': failed_results,
                'total_processed': len(complete_results),
                'success_count': len(successful_results),
                'failure_count': len(failed_results)
            },
            'task_info': {
                'status': task_info['status'],
                'completed_time': task_info.get('completed_time', ''),
                'total_processing_time': task_info.get('completed_time', '')
            }
        }), 200
        
    except Exception as e:
        print(f"[ERROR] 获取连环画结果异常: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取连环画结果失败: {str(e)}'
        }), 500

# 13. 文件过大错误处理
@app.errorhandler(413)
def too_large(e):
    """文件过大错误处理"""
    return jsonify({
        'success': False,
        'message': '文件过大，请选择小于1GB的视频文件'
    }), 413

# 添加直接访问frames目录的路由
@app.route('/frames/<path:subpath>')
def serve_frames(subpath):
    """
    直接服务frames目录下的静态文件
    这个路由允许通过 /frames/... 路径直接访问图片文件
    """
    try:
        # 构建完整的文件路径
        full_path = os.path.join(app.config['FRAMES_FOLDER'], subpath)
        
        # 检查文件是否存在
        if os.path.exists(full_path) and os.path.isfile(full_path):
            # 获取目录和文件名
            directory = os.path.dirname(full_path)
            filename = os.path.basename(full_path)
            return send_from_directory(directory, filename)
        else:
            return jsonify({
                'success': False,
                'message': '文件不存在'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'访问文件时发生错误: {str(e)}'
        }), 500

if __name__ == '__main__':
    import socket
    import sys
    
    # 检查端口是否可用的函数
    def is_port_available(port):
        """检查指定端口是否可用"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                return True
        except OSError:
            return False
    
    # 寻找可用端口
    port = 5001
    max_attempts = 10
    
    print(f"[INFO] 正在启动Flask应用...")
    
    for attempt in range(max_attempts):
        if is_port_available(port):
            print(f"[INFO] 找到可用端口: {port}")
            break
        else:
            print(f"[WARNING] 端口 {port} 被占用，尝试下一个端口...")
            port += 1
    else:
        print(f"[ERROR] 无法找到可用端口 (尝试了 {max_attempts} 个端口)")
        sys.exit(1)
    
    try:
        print(f"[INFO] 启动Flask服务器，访问地址: http://localhost:{port}")
        print(f"[INFO] 按 Ctrl+C 停止服务器")
        app.run(debug=True, host='0.0.0.0', port=port, threaded=True,use_reloader=False)
    except KeyboardInterrupt:
        print(f"\n[INFO] 服务器已停止")
    except Exception as e:
        print(f"[ERROR] 启动服务器时发生错误: {e}")
        sys.exit(1)