#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
关键帧风格化处理使用示例
演示如何使用新集成的风格化处理功能
"""

import requests
import json
import time


def style_transform_example():
    """风格化处理使用示例"""
    
    # API服务器地址
    base_url = "http://localhost:5000"
    
    # 示例：假设您已经有一个完成视频处理的任务ID
    # 在实际使用中，您需要先上传视频并完成关键帧提取
    task_id = "your_task_id_here"  # 替换为您的实际任务ID
    
    # 风格化处理的配置
    style_config = {
        "task_id": task_id,
        # 可选：自定义风格提示词
        "style_prompt": "Convert to Ink and brushwork style, Chinese style, Yellowed and old, Low saturation, Low brightness",
        # 可选：指定输出图像尺寸
        "image_size": "1920x1024",
        # 可选：指定特定的图像URL列表（如果不指定，会自动处理任务中的所有关键帧）
        # "image_urls": [
        #     {
        #         "url": "http://localhost:5000/api/frames/task_id/unified_key_00.jpg",
        #         "filename": "unified_key_00.jpg"
        #     }
        # ]
    }
    
    print("🎨 开始风格化处理...")
    print(f"任务ID: {task_id}")
    print(f"风格提示词: {style_config['style_prompt']}")
    
    try:
        # 发送风格化处理请求
        response = requests.post(
            f"{base_url}/api/process/style-transform",
            json=style_config,
            headers={'Content-Type': 'application/json'},
            timeout=600  # 10分钟超时
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success"):
                print("✅ 风格化处理成功完成！")
                
                # 显示处理结果统计
                print(f"📊 处理统计:")
                print(f"   总图像数: {result.get('processed_count', 0)}")
                print(f"   成功处理: {result.get('successful_count', 0)}")
                print(f"   处理失败: {result.get('failed_count', 0)}")
                
                # 显示处理结果详情
                style_results = result.get("style_results", [])
                print(f"\n🖼️ 处理结果详情:")
                
                for i, style_result in enumerate(style_results):
                    if style_result.get("success"):
                        print(f"   ✓ 图像 {i+1}: {style_result.get('original_filename')} -> {style_result.get('styled_filename')}")
                        print(f"     风格化图像保存路径: {style_result.get('styled_path')}")
                    else:
                        print(f"   ✗ 图像 {i+1} 处理失败: {style_result.get('error')}")
                
                print(f"\n🎯 使用的风格提示词: {result.get('style_prompt')}")
                
            else:
                print(f"❌ 风格化处理失败: {result.get('message', '未知错误')}")
                
        else:
            print(f"❌ API请求失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ 请求超时，风格化处理可能需要较长时间，请稍后重试")
    except requests.exceptions.RequestException as e:
        print(f"🔌 网络错误: {str(e)}")
    except Exception as e:
        print(f"💥 未知错误: {str(e)}")


def check_task_status(task_id):
    """检查任务状态"""
    base_url = "http://localhost:5000"
    
    try:
        response = requests.get(f"{base_url}/api/task/status/{task_id}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📋 任务状态: {result.get('status')}")
            print(f"📝 当前信息: {result.get('message')}")
            print(f"📈 进度: {result.get('progress', 0)}%")
            
            return result.get('status')
        else:
            print(f"❌ 获取任务状态失败: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"💥 检查任务状态时出错: {str(e)}")
        return None


def main():
    """主函数"""
    print("🌟 关键帧风格化处理示例")
    print("=" * 50)
    
    # 提示用户输入任务ID
    task_id = input("请输入您的任务ID (或按回车使用示例ID): ").strip()
    
    if not task_id:
        task_id = "your_task_id_here"
        print(f"使用示例任务ID: {task_id}")
        print("⚠️ 请确保将示例中的任务ID替换为您的实际任务ID")
        
    # 检查任务状态
    print(f"\n🔍 检查任务状态...")
    status = check_task_status(task_id)
    
    if status in ['completed', 'unified_processing', 'style_completed']:
        print("✅ 任务状态允许进行风格化处理")
        
        # 询问是否使用自定义风格
        use_custom_style = input("\n是否使用自定义风格提示词？(y/n): ").strip().lower()
        
        if use_custom_style == 'y':
            custom_prompt = input("请输入风格提示词: ").strip()
            if custom_prompt:
                # 这里可以修改style_transform_example函数来接收自定义提示词
                print(f"将使用自定义风格: {custom_prompt}")
        
        # 执行风格化处理
        style_transform_example()
        
    else:
        print("⚠️ 任务状态不允许进行风格化处理")
        print("💡 请确保任务已完成视频处理和关键帧提取")


if __name__ == "__main__":
    main() 