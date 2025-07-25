#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
⚡ 快速开始：统一智能处理
一个简单的示例，演示如何用几行代码完成智能抽帧和AI分析

作者：AI编程指导教师
"""

import asyncio
from diversity_frame_extractor import DiversityFrameExtractor


async def quick_start():
    """快速开始示例"""
    print("⚡ 快速开始：统一智能处理")
    print("=" * 50)
    
    # 步骤1：创建抽帧器
    extractor = DiversityFrameExtractor(output_dir="quick_start_frames")
    
    # 步骤2：指定视频文件
    video_file = "测试视频3.mp4"  # 请确保这个文件存在
    
    # 步骤3：一行代码完成所有处理！
    print(f"🚀 开始处理视频：{video_file}")
    
    result = await extractor.unified_smart_extraction_async(
        video_path=video_file,
        target_key_frames=12,      # 想要的关键帧数量
        max_concurrent=50         # 并发数，可以调整
    )
    
    # 步骤4：查看结果
    if result['success']:
        print(f"✅ 处理成功！")
        print(f"🎯 提取了 {len(result['selected_frames'])} 个关键帧")
        print(f"📁 保存在目录：{extractor.output_dir}")
        print(f"📄 JSON文件：{result['json_file_path']}")
        
        # 显示关键帧信息
        for i, frame in enumerate(result['selected_frames'][:3]):
            print(f"   关键帧{i+1}: {frame['filename']} (评分: {frame['combined_score']:.3f})")
            print(f"   描述: {frame['ai_analysis']['description'][:60]}...")
    else:
        print(f"❌ 处理失败：{result.get('error')}")


# 运行示例
if __name__ == "__main__":
    asyncio.run(quick_start()) 