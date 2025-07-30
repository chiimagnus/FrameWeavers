#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API端点测试脚本
验证所有API端点是否正常工作
"""

import requests
import json
import time

def test_health_check():
    """测试健康检查端点"""
    print("🔍 测试健康检查端点...")
    try:
        response = requests.get('http://localhost:5000/')
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 健康检查成功: {result.get('message')}")
            return True
        else:
            print(f"   ❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 健康检查异常: {e}")
        return False

def test_config_status():
    """测试配置状态端点"""
    print("🔍 测试配置状态端点...")
    try:
        response = requests.get('http://localhost:5000/api/config/status')
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 配置状态检查成功")
            print(f"   必需配置完整: {result.get('all_required_set', False)}")
            return True
        else:
            print(f"   ❌ 配置状态检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 配置状态检查异常: {e}")
        return False

def test_complete_comic_endpoint():
    """测试完整连环画生成端点"""
    print("🔍 测试完整连环画生成端点...")
    try:
        # 准备测试数据
        test_data = {
            'task_id': f'test_{int(time.time())}',
            'video_path': '测试视频3.mp4',  # 假设这个文件存在
            'story_style': '测试风格',
            'target_frames': '4',  # 少量帧用于快速测试
            'frame_interval': '2.0'
        }
        
        response = requests.post(
            'http://localhost:5000/api/process/complete-comic',
            data=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"   ✅ 端点响应成功")
                print(f"   任务ID: {result.get('task_id')}")
                print(f"   状态: {result.get('status')}")
                return True
            else:
                print(f"   ⚠️ 端点响应但处理失败: {result.get('message')}")
                return False
        else:
            print(f"   ❌ 端点请求失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ 端点测试异常: {e}")
        return False

def test_task_status_endpoint():
    """测试任务状态查询端点"""
    print("🔍 测试任务状态查询端点...")
    try:
        # 测试不存在的任务ID
        response = requests.get('http://localhost:5000/api/task/status/nonexistent')
        if response.status_code == 404:
            print(f"   ✅ 不存在任务的404响应正常")
            return True
        else:
            print(f"   ⚠️ 不存在任务的响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 任务状态查询异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 API端点测试开始...\n")
    
    tests = [
        ("健康检查", test_health_check),
        ("配置状态", test_config_status),
        ("完整连环画生成", test_complete_comic_endpoint),
        ("任务状态查询", test_task_status_endpoint)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        results[test_name] = test_func()
    
    # 总结结果
    print(f"\n{'='*50}")
    print("📊 测试结果总结：")
    print(f"{'='*50}")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name:<20}: {status}")
        if result:
            passed += 1
    
    print(f"\n📈 总体结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有API端点测试通过！")
        print("💡 现在可以运行: python direct_comic_test.py")
    else:
        print("⚠️ 部分API端点测试失败")
        print("💡 请检查Flask应用是否正常启动")
        print("💡 运行: python app.py 启动服务器")
    
    print(f"{'='*50}")

if __name__ == "__main__":
    main()