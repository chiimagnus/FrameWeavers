"""
测试图像风格化处理模块

演示如何使用图像风格化处理模块进行单张和批量并发处理。
"""

import os
import time
import glob
from pathlib import Path
from image_style_processor import ImageStyleProcessor

def test_single_image():
    """测试单张图片处理"""
    print("\n===== 测试单张图片处理 =====")
    
    # 初始化处理器
    processor = ImageStyleProcessor()
    
    # 定义测试图片路径
    test_image = "styled_unified_key_02.jpg"  # 替换为实际存在的图片路径
    
    # 确保测试图片存在
    if not os.path.exists(test_image):
        print(f"错误: 测试图片 {test_image} 不存在")
        return
    
    # 处理单张图片
    try:
        start_time = time.time()
        
        result = processor.process_image(
            test_image,
            output_path="single_test_result.jpg",
            style_prompt="Convert to Ink and brushwork style, Chinese style, Yellowed and old, Low saturation, Low brightness",
            size="1780x1024"
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"单张图片处理完成: {result}")
        print(f"处理时间: {processing_time:.2f} 秒")
    except Exception as e:
        print(f"单张图片处理失败: {e}")

def test_batch_processing():
    """测试批量并发处理"""
    print("\n===== 测试批量并发处理 =====")
    
    # 初始化处理器
    processor = ImageStyleProcessor()
    
    # 准备测试图片
    # 方法1: 使用指定的图片列表
    test_images = ["styled_unified_key_02.jpg"]  # 替换为实际存在的图片路径
    
    # 方法2: 使用目录中的所有图片
    # test_dir = "test_images"
    # if os.path.exists(test_dir):
    #     test_images = glob.glob(os.path.join(test_dir, "*.jpg"))
    
    # 确保有足够的测试图片
    if not test_images:
        print("错误: 没有找到测试图片")
        return
    
    # 为了测试并发，如果图片数量不足，复制现有图片
    if len(test_images) < 3:
        print(f"警告: 测试图片数量不足 ({len(test_images)}), 复制现有图片用于测试")
        test_images = test_images * 5  # 复制5份用于测试
    
    # 创建输出目录
    output_dir = "batch_test_results"
    os.makedirs(output_dir, exist_ok=True)
    
    # 批量处理图片
    try:
        print(f"开始批量处理 {len(test_images)} 张图片...")
        
        start_time = time.time()
        
        # 测试不同的并发数
        for max_workers in [2, 4, 8]:
            print(f"\n使用 {max_workers} 个工作线程:")
            
            batch_start_time = time.time()
            
            results = processor.batch_process_images(
                test_images[:10],  # 限制处理的图片数量
                output_dir=f"{output_dir}/workers_{max_workers}",
                max_workers=max_workers,
                style_prompt="Convert to Ink and brushwork style, Chinese style, Yellowed and old, Low saturation, Low brightness",
                size="1024x1024"  # 使用较小的尺寸加快测试
            )
            
            batch_end_time = time.time()
            batch_time = batch_end_time - batch_start_time
            
            # 统计结果
            success_count = sum(1 for _, result in results if result is not None)
            fail_count = len(results) - success_count
            
            print(f"批量处理完成: {success_count} 成功, {fail_count} 失败")
            print(f"处理时间: {batch_time:.2f} 秒")
            print(f"平均每张图片处理时间: {batch_time / len(test_images):.2f} 秒")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\n总测试时间: {total_time:.2f} 秒")
        
    except Exception as e:
        print(f"批量处理测试失败: {e}")

def test_error_handling():
    """测试错误处理"""
    print("\n===== 测试错误处理 =====")
    
    # 初始化处理器
    processor = ImageStyleProcessor()
    
    # 测试不存在的图片
    non_existent_image = "this_file_does_not_exist.jpg"
    
    try:
        print(f"测试处理不存在的图片: {non_existent_image}")
        result = processor.process_image(non_existent_image)
        print(f"结果: {result}")  # 这行代码不应该执行
    except Exception as e:
        print(f"预期的错误: {e}")
    
    # 测试批量处理中的错误处理
    print("\n测试批量处理中的错误处理")
    
    # 混合有效和无效的图片路径
    mixed_images = [
        "styled_unified_key_02.jpg",  # 有效图片
        "non_existent_1.jpg",         # 无效图片
        "non_existent_2.jpg"          # 无效图片
    ]
    
    try:
        results = processor.batch_process_images(
            mixed_images,
            output_dir="error_test_results"
        )
        
        print("\n批量处理结果:")
        for img_path, result_path in results:
            status = "成功" if result_path else "失败"
            print(f"{img_path}: {status}")
            
    except Exception as e:
        print(f"批量处理测试失败: {e}")

def main():
    """主测试函数"""
    print("===== 图像风格化处理模块测试 =====")
    
    # 测试单张图片处理
    test_single_image()
    
    # 测试批量并发处理
    test_batch_processing()
    
    # 测试错误处理
    test_error_handling()
    
    print("\n===== 测试完成 =====")

if __name__ == "__main__":
    main()