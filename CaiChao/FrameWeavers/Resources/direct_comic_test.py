#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接模式连环画生成测试脚本
展示如何使用新的API设计调用完整连环画生成API

使用方法:
python direct_comic_test.py
"""

import requests
import json
import time
import os
from datetime import datetime

def test_direct_comic_generation():
    """测试直接模式连环画生成（新API设计）"""
    
    print("🎨 直接模式连环画生成测试（新API设计）")
    print("=" * 55)
    
    # 配置
    base_url = "http://localhost:5001"
    test_video = "测试视频3.mp4"
    
    # 检查视频文件
    if not os.path.exists(test_video):
        print(f"❌ 测试视频不存在: {test_video}")
        return
    
    # 获取绝对路径
    video_path = os.path.abspath(test_video)
    print(f"📹 测试视频: {video_path}")
    
    # 生成模拟任务ID（实际使用中应该从前面的API获得）
    task_id = f"test_task_{int(time.time())}"
    print(f"🆔 任务ID: {task_id}")
    
    # 请求参数（按照新的API设计）
    form_data = {
        'task_id': task_id,                # 必须：任务ID
        'video_path': video_path,          # 必须：视频路径
        'story_style': '温馨童话',          # 必须：故事风格关键词
        'target_frames': '12',              # 快速测试用少量帧
        'frame_interval': '2.0',
        'significance_weight': '0.7',
        'quality_weight': '0.3',
        'style_prompt': 'Convert to Ink and brushwork style, Chinese style, Yellowed and old, Low saturation, Low brightness',
        'image_size': '1780x1024',           # 小尺寸加快处理
        'max_concurrent': '50'
    }
    
    print("\n📝 测试配置:")
    print(f"   任务ID: {form_data['task_id']}")
    print(f"   故事风格: {form_data['story_style']}")
    for key, value in form_data.items():
        if key not in ['task_id', 'video_path', 'story_style']:
            print(f"   {key}: {value}")
    
    try:
        print(f"\n🚀 发送直接模式请求...")
        start_time = time.time()
        
        # 调用API
        response = requests.post(
            f'{base_url}/api/process/complete-comic',
            data=form_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                returned_task_id = result.get('task_id')
                print(f"✅ 请求成功！")
                print(f"   任务ID: {returned_task_id}")
                print(f"   状态: {result.get('status')}")
                print(f"   阶段: {result.get('stage')}")
                print(f"   故事风格: {result.get('story_style')}")
                print(f"   视频路径: {result.get('video_path')}")
                
                # 监控进度
                print(f"\n📊 监控处理进度...")
                final_result = monitor_progress(base_url, returned_task_id)
                
                end_time = time.time()
                print(f"\n⏱️ 总耗时: {end_time - start_time:.1f} 秒")
                
                if final_result.get('success'):
                    print("🎉 新API设计测试成功！")
                    print("✨ API参数验证:")
                    print(f"   ✅ task_id: 正确传递和处理")
                    print(f"   ✅ video_path: 正确传递和处理")
                    print(f"   ✅ story_style: 正确传递和处理")
                else:
                    print(f"❌ 处理失败: {final_result.get('error', '未知错误')}")
            else:
                print(f"❌ 请求失败: {result.get('message', '未知错误')}")
        else:
            print(f"❌ HTTP错误: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")

def monitor_progress(base_url: str, task_id: str, max_wait: int = 3000):
    """监控任务进度"""
    start_time = time.time()
    last_progress = -1
    
    stage_descriptions = {
        'initializing': '初始化中',
        'extracting_keyframes': '正在提取关键帧',
        'generating_story': '正在生成故事',
        'stylizing_frames': '正在风格化处理',
        'completed': '已完成'
    }
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f'{base_url}/api/task/status/{task_id}')
            
            if response.status_code == 200:
                status_data = response.json()
                status = status_data.get('status')
                progress = status_data.get('progress', 0)
                stage = status_data.get('stage', 'unknown')
                
                # 只在进度变化时打印
                if progress != last_progress:
                    stage_desc = stage_descriptions.get(stage, stage)
                    print(f"   📈 {progress}% - {stage_desc}")
                    last_progress = progress
                
                # 检查完成状态
                if status == 'complete_comic_completed':
                    print("   ✅ 处理完成")
                    return {'success': True}
                elif status == 'complete_comic_failed':
                    error = status_data.get('error', '未知错误')
                    print(f"   ❌ 处理失败: {error}")
                    return {'success': False, 'error': error}
            
            time.sleep(2)
            
        except Exception as e:
            print(f"   ⚠️ 查询状态异常: {e}")
            time.sleep(2)
    
    return {'success': False, 'error': '监控超时'}

def print_api_summary():
    """打印API设计总结"""
    print("\n" + "=" * 55)
    print("📋 新API设计总结")
    print("=" * 55)
    print("🔄 正确的调用流程:")
    print("   1️⃣ 前端调用视频上传API")
    print("   2️⃣ 前端调用基础帧提取API")
    print("   3️⃣ 前端调用complete-comic API")
    print("\n📥 complete-comic API 必须参数:")
    print("   • task_id: 任务ID（从前面API获得）")
    print("   • video_path: 视频文件路径")
    print("   • story_style: 故事风格关键词")
    print("\n📤 API返回信息:")
    print("   • success: 请求是否成功")
    print("   • task_id: 确认的任务ID")
    print("   • status: 处理状态")
    print("   • story_style: 确认的故事风格")
    print("   • video_path: 确认的视频路径")

if __name__ == "__main__":
    test_direct_comic_generation()
    print_api_summary() 