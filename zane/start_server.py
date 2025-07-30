#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务器启动脚本
确保所有配置正确后启动Flask应用
"""

import os
import sys

def check_prerequisites():
    """检查启动前提条件"""
    print("🔍 检查启动前提条件...")
    
    # 检查.env文件
    if not os.path.exists('.env'):
        print("❌ .env文件不存在")
        print("💡 请运行: python setup_env.py 创建配置文件")
        return False
    
    print("✅ .env文件存在")
    
    # 检查配置
    try:
        from config import validate_config
        if not validate_config():
            print("⚠️ 配置验证失败，但服务器仍将启动")
        else:
            print("✅ 配置验证通过")
    except Exception as e:
        print(f"⚠️ 配置检查异常: {e}")
    
    # 检查必要目录
    directories = ['uploads', 'frames', 'stories']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"✅ 创建目录: {directory}")
        else:
            print(f"✅ 目录存在: {directory}")
    
    # 检查测试视频
    test_video = "测试视频3.mp4"
    if os.path.exists(test_video):
        print(f"✅ 测试视频存在: {test_video}")
    else:
        print(f"⚠️ 测试视频不存在: {test_video}")
        print("💡 请确保有测试视频文件用于测试")
    
    return True

def start_server():
    """启动服务器"""
    print("\n🚀 启动Flask服务器...")
    
    try:
        # 导入并启动应用
        from app import app
        
        # 获取配置
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
        
        print(f"📍 服务器地址: http://localhost:{port}")
        print(f"🔧 调试模式: {'开启' if debug else '关闭'}")
        print(f"📊 配置检查: http://localhost:{port}/api/config/status")
        print(f"🧪 API测试: python test_api_endpoints.py")
        print(f"🎨 连环画测试: python direct_comic_test.py")
        
        print("\n" + "="*50)
        print("🎉 服务器启动中...")
        print("按 Ctrl+C 停止服务器")
        print("="*50)
        
        app.run(host='0.0.0.0', port=port, debug=debug)
        
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    """主函数"""
    print("🔧 连环画剧本创作系统启动器")
    print("="*50)
    
    # 检查前提条件
    if not check_prerequisites():
        print("\n❌ 前提条件检查失败，无法启动服务器")
        sys.exit(1)
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main()