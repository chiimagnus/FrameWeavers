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

def style_transform_image(image_url, style_prompt=None, image_size=None):
    """
    对图像进行风格化处理
    
    Args:
        image_url (str): 图像的URL地址
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
        
        # 构建请求数据
        payload = {
            'model': config.MODELSCOPE_MODEL,
            'prompt': style_prompt,
            'image_url': image_url,
            'size': image_size
        }
        
        # 构建请求头
        headers = {
            'Authorization': f'Bearer {config.MODELSCOPE_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # 发送风格化请求
        print(f"[INFO] 开始风格化处理图像: {image_url}")
        response = requests.post(
            config.MODELSCOPE_API_URL, 
            data=json.dumps(payload, ensure_ascii=False).encode('utf-8'), 
            headers=headers,
            timeout=config.STYLE_PROCESSING_TIMEOUT
        )
        
        # 检查响应状态
        if response.status_code != 200:
            return {
                'success': False,
                'error': f'API请求失败，状态码: {response.status_code}, 响应: {response.text}'
            }
        
        # 解析响应数据
        response_data = response.json()
        
        # 检查响应数据格式
        if 'images' not in response_data or len(response_data['images']) == 0:
            return {
                'success': False,
                'error': f'API响应格式错误: {response_data}'
            }
        
        # 获取风格化后的图像URL
        styled_image_url = response_data['images'][0]['url']
        
        # 下载风格化后的图像
        print(f"[INFO] 下载风格化后的图像: {styled_image_url}")
        image_response = requests.get(styled_image_url, timeout=30)
        
        if image_response.status_code != 200:
            return {
                'success': False,
                'error': f'下载风格化图像失败，状态码: {image_response.status_code}'
            }
        
        # 转换为PIL图像对象
        styled_image = Image.open(BytesIO(image_response.content))
        
        return {
            'success': True,
            'styled_image': styled_image,
            'styled_image_url': styled_image_url,
            'original_url': image_url,
            'style_prompt': style_prompt
        }
        
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'error': '风格化处理超时，请稍后重试'
        }
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f'网络请求错误: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'风格化处理失败: {str(e)}'
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

# 创建异步事件循环
async_loop = asyncio.new_event_loop()

def run_async_task(coro):
    """在异步事件循环中运行协程"""
    import concurrent.futures
    
    def run_in_thread():
        # 在新线程中创建新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    
    # 使用线程池执行异步任务
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(run_in_thread)
        return future.result()

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

# 10. 获取故事生成结果API（保留用于兼容性，但现在故事生成是同步的）
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

# 13. 文件过大错误处理
@app.errorhandler(413)
def too_large(e):
    """文件过大错误处理"""
    return jsonify({
        'success': False,
        'message': '文件过大，请选择小于1GB的视频文件'
    }), 413

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)