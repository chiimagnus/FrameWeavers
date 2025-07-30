"""
修复版本的app.py，添加了风格化处理的重试机制和改进的日志记录
"""

from flask import Flask, request, jsonify, send_from_directory, abort
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
import concurrent.futures
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

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
            logging.warning(f"内存使用率过高: {memory.percent:.1f}%")
            
        # 如果内存使用过高，强制垃圾回收
        if memory.percent > config.MAX_MEMORY_USAGE:
            logging.warning(f"内存使用率危险: {memory.percent:.1f}%，执行垃圾回收...")
            gc.collect()  # 强制垃圾回收
            
        return memory_info
    except Exception as e:
        logging.error(f"内存监控失败: {e}")
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
        with open(image_path, 'rb') as file:
            files = {'image': file}
            response = requests.post(
                config.IMGBB_UPLOAD_URL,
                files=files,
                timeout=config.CONNECTION_TIMEOUT
            )
        
        if response.status_code != 200:
            raise Exception(f"上传请求失败，状态码: {response.status_code}")
        
        result = response.json()
        if result.get('success'):
            image_url = result['url']
            logging.info(f"图片上传成功: {image_url}")
            return image_url
        else:
            error_msg = result.get('error', '未知错误')
            raise Exception(f"上传失败: {error_msg}")
            
    except Exception as e:
        logging.error(f"图片上传失败: {str(e)}")
        raise e

def style_transform_image(image_path, style_prompt=None, image_size=None, max_retries=3, retry_delay=5):
    """
    对图像进行风格化处理 - 严格按照test_style.py的成功示例
    
    Args:
        image_path (str): 本地图像文件路径
        style_prompt (str): 风格化提示词，如果为None则使用默认值
        image_size (str): 输出图像尺寸，如果为None则使用默认值
        max_retries (int): 最大重试次数
        retry_delay (int): 重试间隔时间(秒)
    
    Returns:
        dict: 包含处理结果的字典
    """
    try:
        # 使用配置文件中的默认值
        if style_prompt is None:
            style_prompt = config.DEFAULT_STYLE_PROMPT
        if image_size is None:
            image_size = config.DEFAULT_IMAGE_SIZE
        
        logging.info(f"开始风格化处理: {image_path}")
        
        # 检查本地文件是否存在
        if not os.path.exists(image_path):
            return {
                'success': False,
                'error': f'本地图像文件不存在: {image_path}'
            }
        
        # 第一步：上传图片到图床获取在线URL
        try:
            logging.info("正在上传图片...")
            image_url = upload_to_imgbb(image_path)
            logging.info(f"图片上传成功: {image_url}")
        except Exception as upload_error:
            logging.error(f"图片上传失败: {str(upload_error)}")
            # 上传失败直接返回错误，不使用降级
            return {
                'success': False,
                'error': f'图片上传失败: {str(upload_error)}'
            }
        
        # 第二步：严格按照test_style.py的格式调用API，添加重试机制
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
        
        # 添加重试机制
        retry_count = 0
        while retry_count < max_retries:
            try:
                logging.info(f"调用ModelScope API... (尝试 {retry_count + 1}/{max_retries})")
                
                # 使用与test_style.py相同的请求方式
                response = requests.post(
                    url, 
                    data=json.dumps(payload, ensure_ascii=False).encode('utf-8'), 
                    headers=headers,
                    timeout=config.STYLE_PROCESSING_TIMEOUT
                )
                
                logging.info(f"响应状态码: {response.status_code}")
                
                if response.status_code == 200:
                    # 解析响应
                    response_data = response.json()
                    logging.info("API响应成功接收")
                    
                    # 下载风格化后的图像 - 与test_style.py相同的方式
                    styled_image_url = response_data['images'][0]['url']
                    
                    # 下载图像数据
                    image_response = requests.get(styled_image_url, timeout=config.CONNECTION_TIMEOUT)
                    if image_response.status_code == 200:
                        image_data = image_response.content
                        
                        # 转换为PIL图像对象
                        styled_image = Image.open(BytesIO(image_data))
                        logging.info(f"风格化图像处理成功，尺寸: {styled_image.size}")
                        
                        # 返回成功结果
                        return {
                            'success': True,
                            'styled_image': styled_image,
                            'styled_image_url': styled_image_url,
                            'image_data': image_data,
                            'original_path': image_path
                        }
                    else:
                        error_msg = f"下载风格化图像失败: 状态码 {image_response.status_code}"
                        logging.error(error_msg)
                        # 尝试重试
                        retry_count += 1
                        if retry_count < max_retries:
                            logging.info(f"等待 {retry_delay} 秒后重试...")
                            time.sleep(retry_delay)
                            continue
                        return {
                            'success': False,
                            'error': error_msg
                        }
                elif response.status_code in [429, 503, 504]:
                    # 这些状态码表示服务器过载或超时，适合重试
                    error_msg = f"API请求失败: 状态码 {response.status_code}, 响应: {response.text}"
                    logging.warning(error_msg)
                    retry_count += 1
                    if retry_count < max_retries:
                        # 指数退避策略：每次重试增加等待时间
                        wait_time = retry_delay * (2 ** retry_count)
                        logging.info(f"等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return {
                            'success': False,
                            'error': f"多次尝试后API请求仍然失败: {error_msg}"
                        }
                else:
                    # 其他错误状态码，可能不适合重试
                    error_msg = f"API请求失败: 状态码 {response.status_code}, 响应: {response.text}"
                    logging.error(error_msg)
                    return {
                        'success': False,
                        'error': error_msg
                    }
                    
            except requests.exceptions.Timeout:
                logging.warning(f"API请求超时 (尝试 {retry_count + 1}/{max_retries})")
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = retry_delay * (2 ** retry_count)
                    logging.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    return {
                        'success': False,
                        'error': "API请求多次超时，无法完成风格化处理"
                    }
            except Exception as api_error:
                logging.error(f"API调用异常: {str(api_error)}")
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = retry_delay * (2 ** retry_count)
                    logging.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    return {
                        'success': False,
                        'error': f"API调用异常: {str(api_error)}"
                    }
        
        # 如果所有重试都失败
        return {
            'success': False,
            'error': "达到最大重试次数，风格化处理失败"
        }
        
    except Exception as e:
        logging.error(f"风格化处理异常: {str(e)}")
        logging.debug(traceback.format_exc())
        return {
            'success': False,
            'error': f"风格化处理异常: {str(e)}"
        }

# 图像风格化处理类 - 用于并发处理关键帧
class ImageStyleProcessor:
    """图像风格化处理类 - 简化版本，专用于连环画生成"""
    
    def __init__(self, max_workers=8):
        """
        初始化图像风格化处理器
        
        Args:
            max_workers: 最大并发工作线程数
        """
        self.max_workers = max_workers
        logging.info("图像风格化处理器初始化完成")
    
    def process_image(self, image_path, output_path=None, style_prompt=None, image_size=None):
        """
        处理单张图片的风格化转换
        
        Args:
            image_path: 图片文件路径
            output_path: 输出文件路径，如果为None则自动生成
            style_prompt: 风格提示词，如果为None则使用默认值
            image_size: 输出图片尺寸，如果为None则使用默认值
            
        Returns:
            dict: 处理结果
        """
        # 如果未指定输出路径，则自动生成
        if output_path is None:
            output_path = f"{Path(image_path).stem}_styled.jpg"
        
        try:
            # 调用app.py中已有的风格化处理函数，添加重试机制
            style_result = style_transform_image(
                image_path=image_path,
                style_prompt=style_prompt,
                image_size=image_size,
                max_retries=3,  # 添加重试次数
                retry_delay=5   # 添加重试延迟
            )
            
            if style_result['success']:
                # 保存风格化后的图像
                with open(output_path, 'wb') as f:
                    f.write(style_result['image_data'])
                
                return {
                    'original_path': image_path,
                    'styled_path': output_path,
                    'styled_filename': os.path.basename(output_path),
                    'style_failed': False,
                    'styled_image_url': style_result['styled_image_url']
                }
            else:
                logging.error(f"风格化处理失败: {style_result['error']}")
                return {
                    'original_path': image_path,
                    'styled_path': image_path,
                    'styled_filename': os.path.basename(image_path),
                    'style_failed': True,
                    'error': style_result['error']
                }
                
        except Exception as e:
            logging.error(f"处理图片 {image_path} 失败: {str(e)}")
            logging.debug(traceback.format_exc())
            return {
                'original_path': image_path,
                'styled_path': image_path,
                'styled_filename': os.path.basename(image_path),
                'style_failed': True,
                'error': str(e)
            }
    
    def batch_process_images(self, image_paths, output_dir=None, style_prompt=None, image_size=None):
        """
        批量处理图片的风格化转换
        
        Args:
            image_paths: 图片文件路径列表
            output_dir: 输出目录，如果为None则使用原始图片所在目录
            style_prompt: 风格提示词，如果为None则使用默认值
            image_size: 输出图片尺寸，如果为None则使用默认值
            
        Returns:
            List: 处理结果列表
        """
        logging.info(f"开始批量处理 {len(image_paths)} 张图片")
        
        # 确保输出目录存在
        if output_dir is not None:
            os.makedirs(output_dir, exist_ok=True)
        
        # 准备处理数据
        frame_data_list = []
        for i, path in enumerate(image_paths):
            # 生成输出路径
            if output_dir is not None:
                output_path = os.path.join(output_dir, f"{Path(path).stem}_styled.jpg")
            else:
                output_path = f"{Path(path).stem}_styled.jpg"
                
            frame_data_list.append({
                'path': path,
                'output_path': output_path,
                'index': i
            })
        
        results = []
        
        # 使用线程池并发处理
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_frame = {
                executor.submit(
                    self.process_image, 
                    frame_data['path'], 
                    frame_data['output_path'],
                    style_prompt,
                    image_size
                ): frame_data for frame_data in frame_data_list
            }
            
            # 获取结果
            for future in concurrent.futures.as_completed(future_to_frame):
                frame_data = future_to_frame[future]
                try:
                    result = future.result()
                    result['index'] = frame_data['index']  # 确保保留索引信息
                    results.append(result)
                    logging.info(f"完成处理: {frame_data['path']} -> {result['styled_path']}")
                except Exception as e:
                    logging.error(f"处理 {frame_data['path']} 失败: {str(e)}")
                    # 创建失败结果
                    error_result = {
                        'original_path': frame_data['path'],
                        'styled_path': frame_data['path'],  # 失败时使用原始路径
                        'styled_filename': os.path.basename(frame_data['path']),
                        'style_failed': True,
                        'error': str(e),
                        'index': frame_data['index']
                    }
                    results.append(error_result)
        
        # 按原始索引排序结果
        results.sort(key=lambda x: x['index'])
        
        # 统计成功和失败数量
        success_count = sum(1 for result in results if not result.get('style_failed', False))
        fail_count = len(results) - success_count
        logging.info(f"批量处理完成: {success_count} 成功, {fail_count} 失败")
        
        return results

if __name__ == "__main__":
    # 启动服务器
    print("[INFO] 正在启动Flask应用...")
    
    # 检查端口可用性并启动服务器
    port = 5001
    while port < 5010:
        if is_port_available(port):
            break
        else:
            print(f"[WARNING] 端口 {port} 被占用，尝试下一个端口...")
            port += 1
    
    print(f"[INFO] 找到可用端口: {port}")
    print(f"[INFO] 启动Flask服务器，访问地址: http://localhost:{port}")
    print(f"[INFO] 按 Ctrl+C 停止服务器")
    
    app.run(debug=True, host='0.0.0.0', port=port)