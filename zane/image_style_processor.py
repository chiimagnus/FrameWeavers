"""
图像风格化处理模块

提供图像风格化处理的功能，支持单张图片处理和批量并发处理。
使用ModelScope API进行图像风格化，使用ImgBB作为图床。
"""

import os
import json
import time
import logging
import requests
import traceback
from PIL import Image
from io import BytesIO
import concurrent.futures
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Union, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('image_style_processor')

class ImageStyleProcessor:
    """图像风格化处理类"""
    
    def __init__(self, config=None):
        """
        初始化图像风格化处理器
        
        Args:
            config: 配置对象或字典，如果为None则使用默认配置
        """
        # 导入配置
        if config is None:
            from config import (
                IMGBB_API_KEY,
                IMGBB_UPLOAD_URL,
                MODELSCOPE_API_KEY,
                MODELSCOPE_API_URL,
                MODELSCOPE_MODEL,
                DEFAULT_STYLE_PROMPT,
                DEFAULT_IMAGE_SIZE,
                MAX_CONCURRENT_REQUESTS,
                CONNECTION_TIMEOUT,
                REQUEST_TIMEOUT
            )
            
            self.config = {
                'imgbb_api_key': IMGBB_API_KEY,
                'imgbb_upload_url': IMGBB_UPLOAD_URL,
                'modelscope_api_key': MODELSCOPE_API_KEY,
                'modelscope_api_url': MODELSCOPE_API_URL,
                'modelscope_model': MODELSCOPE_MODEL,
                'default_style_prompt': DEFAULT_STYLE_PROMPT,
                'default_image_size': DEFAULT_IMAGE_SIZE,
                'max_concurrent_requests': MAX_CONCURRENT_REQUESTS,
                'connection_timeout': CONNECTION_TIMEOUT,
                'request_timeout': REQUEST_TIMEOUT
            }
        else:
            self.config = config
        
        # 设置默认超时
        self.timeout = (
            self.config.get('connection_timeout', 30),
            self.config.get('request_timeout', 300)
        )
        
        logger.info("图像风格化处理器初始化完成")
    
    def upload_image(self, image_path: str) -> str:
        """
        上传图片到图床并返回URL
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            str: 上传后的图片URL
            
        Raises:
            FileNotFoundError: 文件不存在
            Exception: 上传失败
        """
        logger.info(f"开始上传图片: {image_path}")
        
        if not os.path.exists(image_path):
            logger.error(f"文件不存在: {image_path}")
            raise FileNotFoundError(f"文件不存在: {image_path}")
        
        try:
            # 使用固定的上传端点
            with open(image_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(
                    'https://tuchuan.zeabur.app/api/upload',
                    files=files,
                    timeout=self.timeout
                )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                image_url = result['url']
                logger.info(f"图片上传成功: {image_url}")
                return image_url
            else:
                error_msg = result.get('error', {}).get('message', '未知错误')
                logger.error(f"图片上传失败: {error_msg}")
                raise Exception(f"上传失败: {error_msg}")
                
        except requests.RequestException as e:
            logger.error(f"图片上传请求异常: {str(e)}")
            raise Exception(f"上传请求异常: {str(e)}")
    
    def apply_style(self, image_url: str, style_prompt: Optional[str] = None, size: Optional[str] = None) -> str:
        """
        对图片应用风格化处理
        
        Args:
            image_url: 图片URL
            style_prompt: 风格提示词，如果为None则使用默认值
            size: 输出图片尺寸，如果为None则使用默认值
            
        Returns:
            str: 处理后的图片URL
            
        Raises:
            Exception: 处理失败
        """
        logger.info(f"开始风格化处理图片: {image_url}")
        
        # 使用默认值或自定义值
        if style_prompt is None:
            style_prompt = self.config['default_style_prompt']
        if size is None:
            size = self.config['default_image_size']
        
        # 准备API调用
        url = self.config['modelscope_api_url']
        payload = {
            'model': self.config['modelscope_model'],
            'prompt': style_prompt,
            'image_url': image_url,
            'size': size
        }
        headers = {
            'Authorization': f'Bearer {self.config["modelscope_api_key"]}',
            'Content-Type': 'application/json'
        }
        
        try:
            # 发送API请求
            response = requests.post(
                url, 
                data=json.dumps(payload, ensure_ascii=False).encode('utf-8'), 
                headers=headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            response_data = response.json()
            
            if 'images' in response_data and len(response_data['images']) > 0:
                result_url = response_data['images'][0]['url']
                logger.info(f"风格化处理成功: {result_url}")
                return result_url
            else:
                logger.error(f"风格化处理失败，返回数据格式异常: {response_data}")
                raise Exception("风格化处理失败，返回数据格式异常")
                
        except requests.RequestException as e:
            logger.error(f"风格化处理请求异常: {str(e)}")
            raise Exception(f"风格化处理请求异常: {str(e)}")
    
    def download_image(self, image_url: str, output_path: str) -> str:
        """
        下载图片并保存到本地
        
        Args:
            image_url: 图片URL
            output_path: 输出文件路径
            
        Returns:
            str: 保存的文件路径
            
        Raises:
            Exception: 下载失败
        """
        logger.info(f"开始下载图片: {image_url}")
        
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            # 下载图片
            response = requests.get(image_url, timeout=self.timeout)
            response.raise_for_status()
            
            # 保存图片
            image = Image.open(BytesIO(response.content))
            image.save(output_path)
            logger.info(f"图片已保存: {output_path}")
            
            return output_path
            
        except requests.RequestException as e:
            logger.error(f"图片下载请求异常: {str(e)}")
            raise Exception(f"图片下载请求异常: {str(e)}")
        except Exception as e:
            logger.error(f"图片保存失败: {str(e)}")
            raise Exception(f"图片保存失败: {str(e)}")
    
    def process_image(self, 
                      image_path: str, 
                      output_path: Optional[str] = None, 
                      style_prompt: Optional[str] = None, 
                      size: Optional[str] = None) -> str:
        """
        处理单张图片的风格化转换
        
        Args:
            image_path: 图片文件路径
            output_path: 输出文件路径，如果为None则自动生成
            style_prompt: 风格提示词，如果为None则使用默认值
            size: 输出图片尺寸，如果为None则使用默认值
            
        Returns:
            str: 处理后的图片路径
            
        Raises:
            Exception: 处理失败
        """
        # 如果未指定输出路径，则自动生成
        if output_path is None:
            output_path = f"{Path(image_path).stem}_styled.jpg"
        
        try:
            # 上传图片
            image_url = self.upload_image(image_path)
            
            # 应用风格
            styled_url = self.apply_style(image_url, style_prompt, size)
            
            # 下载处理后的图片
            result_path = self.download_image(styled_url, output_path)
            
            return result_path
            
        except Exception as e:
            logger.error(f"处理图片 {image_path} 失败: {str(e)}")
            logger.debug(traceback.format_exc())
            raise
    
    def batch_process_images(self, 
                           image_paths: List[str], 
                           output_dir: Optional[str] = None, 
                           max_workers: Optional[int] = None, 
                           style_prompt: Optional[str] = None, 
                           size: Optional[str] = None) -> List[Tuple[str, Optional[str]]]:
        """
        批量并发处理多张图片
        
        Args:
            image_paths: 图片文件路径列表
            output_dir: 输出目录，如果为None则输出到原图片所在目录
            max_workers: 最大并发工作线程数，如果为None则使用配置值
            style_prompt: 风格提示词，如果为None则使用默认值
            size: 输出图片尺寸，如果为None则使用默认值
            
        Returns:
            List[Tuple[str, Optional[str]]]: 处理结果列表，每项为(原图路径, 处理后图片路径)，
                                           如果处理失败则第二项为None
        """
        logger.info(f"开始批量处理 {len(image_paths)} 张图片")
        
        # 如果未指定最大工作线程数，则使用配置中的值或CPU核心数的2倍（取较小值）
        if max_workers is None:
            import multiprocessing
            max_workers = min(
                self.config.get('max_concurrent_requests', 10), 
                multiprocessing.cpu_count() * 2
            )
        
        # 确保输出目录存在
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            # 提交所有任务
            for image_path in image_paths:
                if output_dir:
                    output_path = os.path.join(output_dir, f"{Path(image_path).stem}_styled.jpg")
                else:
                    output_path = f"{Path(image_path).stem}_styled.jpg"
                    
                future = executor.submit(
                    self.process_image, 
                    image_path, 
                    output_path, 
                    style_prompt, 
                    size
                )
                futures.append((future, image_path))
            
            # 收集结果
            for future, image_path in futures:
                try:
                    result = future.result()
                    results.append((image_path, result))
                    logger.info(f"完成处理: {image_path} -> {result}")
                except Exception as e:
                    logger.error(f"处理 {image_path} 失败: {str(e)}")
                    results.append((image_path, None))
        
        # 统计成功和失败的数量
        success_count = sum(1 for _, result in results if result is not None)
        fail_count = len(results) - success_count
        logger.info(f"批量处理完成: {success_count} 成功, {fail_count} 失败")
        
        return results


# 示例用法
if __name__ == "__main__":
    # 初始化处理器
    processor = ImageStyleProcessor()
    
    # 单张图片处理示例
    try:
        print("处理单张图片...")
        result = processor.process_image(
            "styled_unified_key_02.jpg",
            style_prompt="Convert to Ink and brushwork style, Chinese style, Yellowed and old, Low saturation, Low brightness"
        )
        print(f"处理结果: {result}")
    except Exception as e:
        print(f"单张处理失败: {e}")
    
    # 批量处理示例
    print("\n批量处理多张图片...")
    image_files = [
        "styled_unified_key_02.jpg",
        # 添加更多图片路径
    ]
    
    # 检查是否有足够的图片进行批量处理
    if len(image_files) <= 1:
        print("警告: 只有一张图片，批量处理示例将使用相同的图片多次")
        # 为了演示，使用相同的图片创建多个副本
        image_files = image_files * 3
    
    try:
        batch_results = processor.batch_process_images(
            image_files,
            output_dir="styled_output",
            style_prompt="Convert to Ink and brushwork style, Chinese style, Yellowed and old, Low saturation, Low brightness",
            size="1780x1024"
        )
        
        # 打印批量处理结果
        print("\n批量处理结果摘要:")
        for original, styled in batch_results:
            status = "成功" if styled else "失败"
            print(f"{original}: {status} -> {styled}")
    except Exception as e:
        print(f"批量处理失败: {e}")