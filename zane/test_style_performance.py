"""
图像风格化处理性能对比测试

比较优化前后的图像风格化处理性能差异。
"""

import os
import time
import shutil
import tempfile
from pathlib import Path

# 导入优化后的处理器
from image_style_processor import ImageStyleProcessor

# 导入原始处理函数（需要先将原始代码封装为函数）
def original_process_image(image_path, output_path=None):
    """原始的图像处理函数"""
    import requests
    import json
    from PIL import Image
    from io import BytesIO
    from config import (
        MODELSCOPE_API_KEY, 
        MODELSCOPE_API_URL, 
        MODELSCOPE_MODEL
    )
    
    if output_path is None:
        output_path = f"{Path(image_path).stem}_original_result.jpg"
    
    # 上传本地图片获取URL
    print(f"上传图片: {image_path}")
    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post('https://tuchuan.zeabur.app/api/upload', files=files)
    
    result = response.json()
    if result['success']:
        image_url = result['url']
        print(f"图片已上传: {image_url}")
    else:
        raise Exception(f"上传失败: {result['error']}")
    
    # 准备API调用
    url = MODELSCOPE_API_URL
    payload = {
        'model': MODELSCOPE_MODEL,
        'prompt': 'Convert to Ink and brushwork style, Chinese style, Yellowed and old, Low saturation, Low brightness',
        'image_url': image_url,
        'size': "1780x1024"
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
    print("API响应成功接收")
    
    # 下载并保存处理后的图像
    image = Image.open(BytesIO(requests.get(response_data['images'][0]['url']).content))
    image.save(output_path)
    print(f"图片已保存为 {output_path}")
    
    return output_path

def prepare_test_images(count=5, source_image="styled_unified_key_02.jpg"):
    """准备测试图片"""
    if not os.path.exists(source_image):
        print(f"错误: 源图片 {source_image} 不存在")
        return []
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp(prefix="style_test_")
    
    # 复制源图片多次
    test_images = []
    for i in range(count):
        dest_path = os.path.join(temp_dir, f"test_image_{i+1}.jpg")
        shutil.copy(source_image, dest_path)
        test_images.append(dest_path)
    
    return test_images, temp_dir

def test_original_sequential(test_images):
    """测试原始顺序处理方法"""
    print("\n===== 测试原始顺序处理 =====")
    
    output_dir = "original_results"
    os.makedirs(output_dir, exist_ok=True)
    
    start_time = time.time()
    results = []
    
    for image_path in test_images:
        output_path = os.path.join(output_dir, f"{Path(image_path).name}_result.jpg")
        try:
            result = original_process_image(image_path, output_path)
            results.append((image_path, result))
            print(f"处理完成: {image_path} -> {result}")
        except Exception as e:
            print(f"处理失败: {image_path} - {e}")
            results.append((image_path, None))
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    # 统计结果
    success_count = sum(1 for _, result in results if result is not None)
    fail_count = len(results) - success_count
    
    print(f"顺序处理完成: {success_count} 成功, {fail_count} 失败")
    print(f"总处理时间: {processing_time:.2f} 秒")
    print(f"平均每张图片处理时间: {processing_time / len(test_images):.2f} 秒")
    
    return processing_time

def test_optimized_concurrent(test_images, max_workers=None):
    """测试优化后的并发处理方法"""
    print(f"\n===== 测试优化后的并发处理 (工作线程: {max_workers}) =====")
    
    output_dir = "optimized_results"
    if max_workers:
        output_dir = f"{output_dir}_{max_workers}"
    os.makedirs(output_dir, exist_ok=True)
    
    # 初始化处理器
    processor = ImageStyleProcessor()
    
    start_time = time.time()
    
    results = processor.batch_process_images(
        test_images,
        output_dir=output_dir,
        max_workers=max_workers,
        style_prompt="Convert to Ink and brushwork style, Chinese style, Yellowed and old, Low saturation, Low brightness",
        size="1780x1024"
    )
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    # 统计结果
    success_count = sum(1 for _, result in results if result is not None)
    fail_count = len(results) - success_count
    
    print(f"并发处理完成: {success_count} 成功, {fail_count} 失败")
    print(f"总处理时间: {processing_time:.2f} 秒")
    print(f"平均每张图片处理时间: {processing_time / len(test_images):.2f} 秒")
    
    return processing_time

def main():
    """主测试函数"""
    print("===== 图像风格化处理性能对比测试 =====")
    
    # 准备测试图片
    test_count = 5  # 测试图片数量
    test_images, temp_dir = prepare_test_images(test_count)
    
    if not test_images:
        print("错误: 无法准备测试图片")
        return
    
    print(f"已准备 {len(test_images)} 张测试图片")
    
    try:
        # 测试原始顺序处理
        original_time = test_original_sequential(test_images[:3])  # 使用较少的图片测试原始方法
        
        # 测试不同并发数的优化处理
        concurrent_times = {}
        for workers in [2, 4, 8]:
            concurrent_time = test_optimized_concurrent(test_images, workers)
            concurrent_times[workers] = concurrent_time
        
        # 输出性能比较结果
        print("\n===== 性能比较结果 =====")
        print(f"原始顺序处理时间: {original_time:.2f} 秒 (3张图片)")
        print(f"预估处理 {test_count} 张图片时间: {original_time/3*test_count:.2f} 秒")
        
        for workers, time_taken in concurrent_times.items():
            speedup = (original_time/3*test_count) / time_taken
            print(f"并发处理 ({workers} 工作线程) 时间: {time_taken:.2f} 秒, 加速比: {speedup:.2f}x")
        
    except Exception as e:
        print(f"测试过程中出错: {e}")
    finally:
        # 清理临时文件
        try:
            shutil.rmtree(temp_dir)
            print(f"已清理临时目录: {temp_dir}")
        except:
            print(f"无法清理临时目录: {temp_dir}")
    
    print("\n===== 测试完成 =====")

if __name__ == "__main__":
    main()