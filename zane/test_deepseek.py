#!/usr/bin/env python3
"""
测试DeepSeek API集成
"""

import asyncio
import json
from story_generation_agents import LLMClient

async def test_deepseek_api():
    """测试DeepSeek API连接和响应"""
    print("开始测试DeepSeek API...")
    
    try:
        # 创建LLM客户端
        client = LLMClient()
        print(f"使用模型: {client.model}")
        print(f"API地址: {client.base_url}")
        
        # 测试简单的文本生成
        test_prompt = "请用一句话描述春天的美好。"
        
        print(f"发送测试提示: {test_prompt}")
        
        response = await client.generate_text(
            prompt=test_prompt,
            max_tokens=100,
            temperature=0.7
        )
        
        print(f"API响应成功!")
        print(f"响应内容: {response}")
        print(f"响应长度: {len(response)} 字符")
        
        return True
        
    except Exception as e:
        print(f"API测试失败: {e}")
        return False

async def test_story_generation():
    """测试故事生成功能"""
    print("\n开始测试故事生成功能...")
    
    # 简化的测试数据
    test_input = {
        "video_info": {
            "video_path": "test.mp4",
            "video_name": "test.mp4", 
            "task_id": "deepseek_test"
        },
        "keyframes": [
            {
                "index": 1,
                "filename": "test_frame_001.jpg",
                "photo_path": "test_frames/test_frame_001.jpg",
                "combined_score": 0.8,
                "significance_score": 0.8,
                "quality_score": 0.8,
                "description": "一个阳光明媚的午后，公园里有人在散步",
                "timestamp": 0.0,
                "frame_position": 0
            }
        ]
    }
    
    try:
        from story_generation_agents import generate_story_from_keyframes
        
        result = await generate_story_from_keyframes(test_input)
        
        if result.get("success"):
            print("故事生成测试成功!")
            print(f"故事标题: {result.get('story_title', 'N/A')}")
            print(f"故事主题: {result.get('overall_theme', 'N/A')}")
            print(f"生成旁白数量: {len(result.get('final_narrations', []))}")
            print(f"生成问题数量: {len(result.get('interactive_questions', []))}")
            
            # 显示第一个旁白示例
            narrations = result.get('final_narrations', [])
            if narrations:
                print(f"示例旁白: {narrations[0].get('story_text', 'N/A')}")
                
            return True
        else:
            print(f"故事生成失败: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"故事生成测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("=" * 50)
    print("DeepSeek API 集成测试")
    print("=" * 50)
    
    # 测试基础API连接
    api_test_result = await test_deepseek_api()
    
    if api_test_result:
        # 如果基础API测试通过，继续测试故事生成
        story_test_result = await test_story_generation()
        
        if story_test_result:
            print("\n✅ 所有测试通过! DeepSeek集成成功")
        else:
            print("\n❌ 故事生成测试失败")
    else:
        print("\n❌ API连接测试失败，请检查配置")

if __name__ == "__main__":
    asyncio.run(main())