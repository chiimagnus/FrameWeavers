#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
问题诊断脚本
快速诊断和解决常见问题
"""

import os
import sys
import subprocess
import requests
import time

def check_python_version():
    """检查Python版本"""
    print("🐍 Python版本检查:")
    version = sys.version_info
    print(f"   版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("   ⚠️ 建议使用Python 3.8或更高版本")
        return False
    else:
        print("   ✅ Python版本符合要求")
        return True

def check_dependencies():
    """检查依赖包"""
    print("\n📦 依赖包检查:")
    
    required_packages = [
        'flask', 'requests', 'pillow', 'numpy', 
        'opencv-python-headless', 'openai', 'aiohttp', 
        'psutil', 'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'opencv-python-headless':
                import cv2
                print(f"   ✅ {package} (OpenCV {cv2.__version__})")
            elif package == 'pillow':
                import PIL
                print(f"   ✅ {package} (PIL {PIL.__version__})")
            elif package == 'python-dotenv':
                import dotenv
                print(f"   ✅ {package}")
            else:
                __import__(package.replace('-', '_'))
                print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n💡 安装缺失的包:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_config_files():
    """检查配置文件"""
    print("\n📄 配置文件检查:")
    
    # 检查.env文件
    if os.path.exists('.env'):
        print("   ✅ .env文件存在")
        
        # 检查关键配置
        with open('.env', 'r') as f:
            content = f.read()
            
        required_keys = ['MOONSHOT_API_KEY', 'MODELSCOPE_API_KEY', 'OPENAI_API_KEY']
        for key in required_keys:
            if key in content and not f'{key}=your-' in content:
                print(f"   ✅ {key} 已配置")
            else:
                print(f"   ❌ {key} 未配置或使用示例值")
    else:
        print("   ❌ .env文件不存在")
        print("   💡 运行: cp .env.example .env")
        return False
    
    # 检查其他重要文件
    important_files = ['app.py', 'config.py', 'diversity_frame_extractor.py']
    for file in important_files:
        if os.path.exists(file):
            print(f"   ✅ {file} 存在")
        else:
            print(f"   ❌ {file} 不存在")
            return False
    
    return True

def check_directories():
    """检查目录结构"""
    print("\n📁 目录结构检查:")
    
    required_dirs = ['uploads', 'frames', 'stories']
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"   ✅ {directory}/ 存在")
        else:
            print(f"   ⚠️ {directory}/ 不存在，将自动创建")
            os.makedirs(directory, exist_ok=True)
    
    return True

def check_test_files():
    """检查测试文件"""
    print("\n🎬 测试文件检查:")
    
    test_video = "测试视频3.mp4"
    if os.path.exists(test_video):
        size_mb = os.path.getsize(test_video) / (1024 * 1024)
        print(f"   ✅ {test_video} 存在 ({size_mb:.1f} MB)")
        return True
    else:
        print(f"   ⚠️ {test_video} 不存在")
        print("   💡 请准备一个测试视频文件用于测试")
        return False

def test_server_startup():
    """测试服务器启动"""
    print("\n🚀 服务器启动测试:")
    
    try:
        # 尝试导入主要模块
        print("   🔄 导入主要模块...")
        import app
        print("   ✅ 模块导入成功")
        
        # 检查Flask应用
        if hasattr(app, 'app'):
            print("   ✅ Flask应用对象存在")
            return True
        else:
            print("   ❌ Flask应用对象不存在")
            return False
            
    except Exception as e:
        print(f"   ❌ 模块导入失败: {e}")
        return False

def test_api_connectivity():
    """测试API连通性"""
    print("\n🌐 API连通性测试:")
    
    # 检查服务器是否运行
    try:
        response = requests.get('http://localhost:5000/', timeout=5)
        if response.status_code == 200:
            print("   ✅ 服务器正在运行")
            
            # 测试配置状态端点
            try:
                config_response = requests.get('http://localhost:5000/api/config/status', timeout=5)
                if config_response.status_code == 200:
                    print("   ✅ 配置状态端点正常")
                    return True
                else:
                    print(f"   ⚠️ 配置状态端点异常: {config_response.status_code}")
                    return False
            except Exception as e:
                print(f"   ⚠️ 配置状态端点测试失败: {e}")
                return False
                
        else:
            print(f"   ⚠️ 服务器响应异常: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ⚠️ 服务器未运行")
        print("   💡 请先运行: python app.py 或 python start_server.py")
        return False
    except Exception as e:
        print(f"   ❌ 连接测试失败: {e}")
        return False

def provide_solutions():
    """提供解决方案"""
    print("\n💡 常见问题解决方案:")
    print("="*50)
    
    print("1. 如果依赖包缺失:")
    print("   pip install -r requirements.txt")
    
    print("\n2. 如果.env文件不存在:")
    print("   cp .env.example .env")
    print("   然后编辑.env文件填入真实的API密钥")
    
    print("\n3. 如果服务器启动失败:")
    print("   python start_server.py")
    
    print("\n4. 如果API端点404错误:")
    print("   确保服务器正在运行")
    print("   检查请求的URL是否正确")
    
    print("\n5. 如果测试视频不存在:")
    print("   准备一个MP4格式的测试视频")
    print("   重命名为'测试视频3.mp4'")
    
    print("\n6. 完整测试流程:")
    print("   python diagnose.py          # 诊断问题")
    print("   python start_server.py      # 启动服务器")
    print("   python test_api_endpoints.py # 测试API")
    print("   python direct_comic_test.py  # 测试连环画生成")

def main():
    """主诊断函数"""
    print("🔍 连环画剧本创作系统诊断工具")
    print("="*50)
    
    checks = [
        ("Python版本", check_python_version),
        ("依赖包", check_dependencies),
        ("配置文件", check_config_files),
        ("目录结构", check_directories),
        ("测试文件", check_test_files),
        ("服务器启动", test_server_startup),
        ("API连通性", test_api_connectivity)
    ]
    
    results = {}
    for check_name, check_func in checks:
        results[check_name] = check_func()
    
    # 总结结果
    print("\n" + "="*50)
    print("📊 诊断结果总结:")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for check_name, result in results.items():
        status = "✅ 正常" if result else "❌ 异常"
        print(f"   {check_name:<15}: {status}")
        if result:
            passed += 1
    
    print(f"\n📈 总体状态: {passed}/{total} 项检查通过")
    
    if passed == total:
        print("🎉 系统状态良好！")
        print("💡 可以正常使用连环画生成功能")
    else:
        print("⚠️ 发现问题，请参考解决方案")
        provide_solutions()
    
    print("="*50)

if __name__ == "__main__":
    main()