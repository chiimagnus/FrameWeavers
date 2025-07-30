#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境变量配置测试脚本
验证所有API密钥和配置是否正确设置
"""

import os
import sys

def test_env_loading():
    """测试环境变量加载"""
    print("=== 环境变量加载测试 ===\n")
    
    # 检查.env文件
    if os.path.exists('.env'):
        print("✅ .env文件存在")
        
        # 显示.env文件内容（隐藏敏感信息）
        print("\n📄 .env文件内容预览：")
        with open('.env', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i, line in enumerate(lines[:10], 1):  # 只显示前10行
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        # 隐藏敏感值
                        if any(sensitive in key.upper() for sensitive in ['KEY', 'TOKEN', 'SECRET']):
                            display_value = f"{value[:8]}..." if len(value) > 8 else "***"
                        else:
                            display_value = value
                        print(f"   {i:2d}. {key}={display_value}")
                    else:
                        print(f"   {i:2d}. {line}")
                elif line.startswith('#'):
                    print(f"   {i:2d}. {line}")
    else:
        print("❌ .env文件不存在")
        print("请运行: python setup_env.py 创建配置文件")
        return False
    
    return True

def test_config_import():
    """测试配置模块导入"""
    print("\n=== 配置模块导入测试 ===\n")
    
    try:
        print("🔄 导入配置模块...")
        import config
        print("✅ 配置模块导入成功")
        
        # 测试配置验证
        print("\n🔍 运行配置验证...")
        validation_result = config.validate_config()
        
        if validation_result:
            print("✅ 配置验证通过")
        else:
            print("⚠️ 配置验证失败，但模块加载正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置模块导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_keys():
    """测试API密钥配置"""
    print("\n=== API密钥配置测试 ===\n")
    
    try:
        from config import (
            MOONSHOT_API_KEY, MODELSCOPE_API_KEY, OPENAI_API_KEY,
            IMGBB_API_KEY, GITHUB_TOKEN
        )
        
        # 测试必需的API密钥
        required_keys = {
            'MOONSHOT_API_KEY': MOONSHOT_API_KEY,
            'MODELSCOPE_API_KEY': MODELSCOPE_API_KEY,
            'OPENAI_API_KEY': OPENAI_API_KEY
        }
        
        print("🔑 必需的API密钥：")
        all_required_set = True
        for key_name, key_value in required_keys.items():
            if key_value and not key_value.startswith('your-') and not key_value.startswith('sk-your-'):
                status = "✅ 已设置"
                preview = f"{key_value[:8]}...{key_value[-4:]}" if len(key_value) > 12 else "***"
            else:
                status = "❌ 未设置"
                preview = "未设置或使用示例值"
                all_required_set = False
            
            print(f"   {key_name}: {status} ({preview})")
        
        # 测试可选的API密钥
        optional_keys = {
            'IMGBB_API_KEY': IMGBB_API_KEY,
            'GITHUB_TOKEN': GITHUB_TOKEN
        }
        
        print("\n🔑 可选的API密钥：")
        for key_name, key_value in optional_keys.items():
            if key_value and not key_value.startswith('your-'):
                status = "✅ 已设置"
                preview = f"{key_value[:8]}...{key_value[-4:]}" if len(key_value) > 12 else "***"
            else:
                status = "⚪ 未设置"
                preview = "可选配置"
            
            print(f"   {key_name}: {status} ({preview})")
        
        return all_required_set
        
    except Exception as e:
        print(f"❌ API密钥测试失败: {e}")
        return False

def test_performance_config():
    """测试性能配置"""
    print("\n=== 性能配置测试 ===\n")
    
    try:
        from config import (
            MAX_CONCURRENT_REQUESTS, MEMORY_WARNING_THRESHOLD, MAX_MEMORY_USAGE,
            CONNECTION_TIMEOUT, REQUEST_TIMEOUT, DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS
        )
        
        performance_configs = {
            'MAX_CONCURRENT_REQUESTS': MAX_CONCURRENT_REQUESTS,
            'MEMORY_WARNING_THRESHOLD': MEMORY_WARNING_THRESHOLD,
            'MAX_MEMORY_USAGE': MAX_MEMORY_USAGE,
            'CONNECTION_TIMEOUT': CONNECTION_TIMEOUT,
            'REQUEST_TIMEOUT': REQUEST_TIMEOUT,
            'DEFAULT_TEMPERATURE': DEFAULT_TEMPERATURE,
            'DEFAULT_MAX_TOKENS': DEFAULT_MAX_TOKENS
        }
        
        print("⚙️ 性能配置：")
        for config_name, config_value in performance_configs.items():
            print(f"   {config_name}: {config_value}")
        
        # 验证配置合理性
        warnings = []
        if MAX_CONCURRENT_REQUESTS > 20:
            warnings.append(f"并发请求数过高 ({MAX_CONCURRENT_REQUESTS})，可能导致资源耗尽")
        if MEMORY_WARNING_THRESHOLD >= MAX_MEMORY_USAGE:
            warnings.append("内存警告阈值应小于最大内存使用限制")
        if CONNECTION_TIMEOUT > REQUEST_TIMEOUT:
            warnings.append("连接超时不应大于请求超时")
        
        if warnings:
            print("\n⚠️ 配置警告：")
            for warning in warnings:
                print(f"   • {warning}")
        else:
            print("\n✅ 性能配置合理")
        
        return True
        
    except Exception as e:
        print(f"❌ 性能配置测试失败: {e}")
        return False

def test_dependencies():
    """测试依赖库"""
    print("\n=== 依赖库测试 ===\n")
    
    dependencies = [
        ('python-dotenv', 'dotenv'),
        ('opencv-python-headless', 'cv2'),
        ('requests', 'requests'),
        ('flask', 'flask'),
        ('pillow', 'PIL'),
        ('numpy', 'numpy'),
        ('openai', 'openai'),
        ('aiohttp', 'aiohttp'),
        ('psutil', 'psutil')
    ]
    
    print("📦 依赖库检查：")
    all_deps_ok = True
    
    for package_name, import_name in dependencies:
        try:
            __import__(import_name)
            print(f"   ✅ {package_name}")
        except ImportError:
            print(f"   ❌ {package_name} - 未安装")
            all_deps_ok = False
        except Exception as e:
            print(f"   ⚠️ {package_name} - 导入异常: {e}")
            all_deps_ok = False
    
    return all_deps_ok

def test_flask_app():
    """测试Flask应用"""
    print("\n=== Flask应用测试 ===\n")
    
    try:
        print("🔄 导入Flask应用...")
        import app
        print("✅ Flask应用导入成功")
        
        # 测试应用配置
        print(f"   上传目录: {app.UPLOAD_FOLDER}")
        print(f"   帧目录: {app.FRAMES_FOLDER}")
        print(f"   故事目录: {app.STORIES_FOLDER}")
        
        # 检查目录是否存在
        directories = [app.UPLOAD_FOLDER, app.FRAMES_FOLDER, app.STORIES_FOLDER]
        for directory in directories:
            if os.path.exists(directory):
                print(f"   ✅ {directory} 目录存在")
            else:
                print(f"   ⚠️ {directory} 目录不存在，将自动创建")
        
        return True
        
    except Exception as e:
        print(f"❌ Flask应用测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🧪 环境变量配置测试开始...\n")
    
    # 运行所有测试
    tests = [
        ("环境变量加载", test_env_loading),
        ("配置模块导入", test_config_import),
        ("API密钥配置", test_api_keys),
        ("性能配置", test_performance_config),
        ("依赖库", test_dependencies),
        ("Flask应用", test_flask_app)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            results[test_name] = False
    
    # 总结结果
    print("\n" + "="*60)
    print("📊 测试结果总结：")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name:<20}: {status}")
        if result:
            passed += 1
    
    print(f"\n📈 总体结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！你的环境配置正确。")
        print("💡 现在可以运行: python app.py 启动服务器")
    else:
        print("⚠️ 部分测试失败，请检查配置。")
        print("💡 运行: python setup_env.py 获取配置帮助")
    
    print("="*60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)