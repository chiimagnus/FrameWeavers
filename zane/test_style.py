import requests
import json
import os
import time
from PIL import Image
from io import BytesIO
import concurrent.futures
from pathlib import Path

def upload_to_imgbb(image_path, api_key="7c9e1b2a3f4d5e6f7a8b9c0d1e2f3a4b"):
    """上传图片并返回URL"""
    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post('https://tuchuan.zeabur.app/api/upload', files=files)
    
    result = response.json()
    if result['success']:
        return result['url']
    else:
        raise Exception(f"上传失败: {result['error']}")

def process_image(image_path, output_path=None, style_prompt=None, size=None):
    """处理单张图片的风格化转换"""
    from config import (
        MODELSCOPE_API_KEY, 
        MODELSCOPE_API_URL, 
        MODELSCOPE_MODEL,
        DEFAULT_STYLE_PROMPT,
        DEFAULT_IMAGE_SIZE
    )
    
    # 使用默认值或自定义值
    if style_prompt is None:
        style_prompt = DEFAULT_STYLE_PROMPT
    if size is None:
        size = DEFAULT_IMAGE_SIZE
    if output_path is None:
        # 生成输出路径：原文件名_styled.jpg
        output_path = f"{Path(image_path).stem}_styled.jpg"
    
    try:
        # 上传图片
        print(f"上传图片: {image_path}")
        image_url = upload_to_imgbb(image_path)
        print(f"图片已上传: {image_url}")
        
        # 准备API调用
        url = MODELSCOPE_API_URL
        payload = {
            'model': MODELSCOPE_MODEL,
            'prompt': style_prompt,
            'image_url': image_url,
            'size': size
        }
        headers = {
            'Authorization': f'Bearer {MODELSCOPE_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # 发送API请求
        response = requests.post(
            url, 
            data=json.dumps(payload, ensure_ascii=False).encode('utf-8'), 
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"错误: {response.text}")
            return None
        
        # 处理响应
        response_data = response.json()
        print(f"图片 {image_path} 的API响应成功接收")
        
        # 下载并保存处理后的图像
        image = Image.open(BytesIO(requests.get(response_data['images'][0]['url']).content))
        image.save(output_path)
        print(f"图片已保存为 {output_path}")
        
        return output_path
    
    except FileNotFoundError:
        print(f"错误: 找不到文件 {image_path}")
        return None
    except Exception as e:
        print(f"处理 {image_path} 时出错: {e}")
        return None

def batch_process_images(image_paths, output_dir=None, max_workers=None, style_prompt=None, size=None):
    """批量并发处理多张图片"""
    from config import MAX_CONCURRENT_REQUESTS
    
    # 如果未指定最大工作线程数，则使用配置中的值或CPU核心数的2倍（取较小值）
    if max_workers is None:
        import multiprocessing
        max_workers = min(MAX_CONCURRENT_REQUESTS, multiprocessing.cpu_count() * 2)
    
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
                output_path = None
                
            future = executor.submit(
                process_image, 
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
                print(f"完成处理: {image_path} -> {result}")
            except Exception as e:
                print(f"处理 {image_path} 失败: {e}")
                results.append((image_path, None))
    
    return results

# 示例用法
if __name__ == "__main__":
    # 单张图片处理示例
    print("处理单张图片...")
    result = process_image("styled_unified_key_02.jpg")
    print(f"处理结果: {result}")
    
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
    
    batch_results = batch_process_images(
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