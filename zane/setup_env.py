#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境变量设置助手
帮助用户创建和配置.env文件
"""

import os
import shutil

def create_env_file():
    """创建.env文件"""
    print("=== 环境变量设置助手 ===\n")
    
    # 检查是否已存在.env文件
    if os.path.exists('.env'):
        print("⚠️ .env文件已存在")
        choice = input("是否要覆盖现有文件？(y/N): ").lower().strip()
        if choice != 'y':
            print("操作已取消")
            return
    
    # 复制.env.example到.env
    if os.path.exists('.env.example'):
        shutil.copy('.env.example', '.env')
        print("✅ 已创建.env文件（基于.env.example）")
    else:
        print("❌ .env.example文件不存在，无法创建.env文件")
        return
    
    print("\n📝 请编辑.env文件并填入你的实际API密钥：")
    print("   1. 打开.env文件")
    print("   2. 将示例密钥替换为你的真实密钥")
    print("   3. 保存文件")
    
    print("\n🔑 需要设置的主要密钥：")
    print("   • MOONSHOT_API_KEY - Moonshot AI API密钥")
    print("   • MODELSCOPE_API_KEY - ModelScope API密钥")
    print("   • OPENAI_API_KEY - OpenAI兼容API密钥")
    
    print("\n⚠️ 安全提醒：")
    print("   • 不要将.env文件提交到版本控制系统")
    print("   • 不要在公开场合分享你的API密钥")
    print("   • 定期更换API密钥以确保安全")

def validate_env():
    """验证环境变量设置"""
    print("\n=== 环境变量验证 ===\n")
    
    if not os.path.exists('.env'):
        print("❌ .env文件不存在，请先运行创建功能")
        return False
    
    # 加载.env文件
    from dotenv import load_dotenv
    load_dotenv()
    
    # 检查必需的环境变量
    required_vars = [
        "MOONSHOT_API_KEY",
        "MODELSCOPE_API_KEY", 
        "OPENAI_API_KEY"
    ]
    
    optional_vars = [
        "IMGBB_API_KEY",
        "GITHUB_TOKEN",
        "GITHUB_REPO_OWNER",
        "GITHUB_REPO_NAME"
    ]
    
    print("🔍 检查必需的环境变量：")
    all_required_set = True
    for var in required_vars:
        value = os.getenv(var)
        if value and not value.startswith('your-') and not value.startswith('sk-your-'):
            print(f"   ✅ {var}: 已设置")
        else:
            print(f"   ❌ {var}: 未设置或使用示例值")
            all_required_set = False
    
    print("\n🔍 检查可选的环境变量：")
    for var in optional_vars:
        value = os.getenv(var)
        if value and not value.startswith('your-'):
            print(f"   ✅ {var}: 已设置")
        else:
            print(f"   ⚪ {var}: 未设置（可选）")
    
    if all_required_set:
        print("\n✅ 所有必需的环境变量都已正确设置！")
        return True
    else:
        print("\n❌ 部分必需的环境变量未设置，请检查.env文件")
        return False

def test_config():
    """测试配置是否正常工作"""
    print("\n=== 配置测试 ===\n")
    
    try:
        # 尝试导入配置
        from config import validate_config
        
        print("🧪 测试配置导入...")
        success = validate_config()
        
        if success:
            print("✅ 配置测试通过！")
            
            # 显示配置摘要
            from config import (
                MOONSHOT_API_KEY, MODELSCOPE_API_KEY, OPENAI_API_KEY,
                DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS, MAX_CONCURRENT_REQUESTS
            )
            
            print("\n📊 配置摘要：")
            print(f"   Moonshot API: {'已配置' if MOONSHOT_API_KEY else '未配置'}")
            print(f"   ModelScope API: {'已配置' if MODELSCOPE_API_KEY else '未配置'}")
            print(f"   OpenAI API: {'已配置' if OPENAI_API_KEY else '未配置'}")
            print(f"   默认温度: {DEFAULT_TEMPERATURE}")
            print(f"   最大Token: {DEFAULT_MAX_TOKENS}")
            print(f"   最大并发: {MAX_CONCURRENT_REQUESTS}")
            
        else:
            print("❌ 配置测试失败，请检查.env文件")
            
    except Exception as e:
        print(f"❌ 配置测试出错: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("🔧 环境变量设置助手")
    print("请选择操作：")
    print("  1. 创建.env文件")
    print("  2. 验证环境变量")
    print("  3. 测试配置")
    print("  4. 全部执行")
    print("  0. 退出")
    
    while True:
        choice = input("\n请输入选项 (0-4): ").strip()
        
        if choice == '0':
            print("再见！")
            break
        elif choice == '1':
            create_env_file()
        elif choice == '2':
            validate_env()
        elif choice == '3':
            test_config()
        elif choice == '4':
            create_env_file()
            if validate_env():
                test_config()
        else:
            print("无效选项，请重新输入")

if __name__ == "__main__":
    main()