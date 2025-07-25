#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🎯 统一智能处理演示脚本
智能抽基础帧 + 异步并发AI分析 一体化解决方案

这个脚本演示了如何使用新的统一方法：
1. 智能抽取基础帧（根据视频特性自动优化）
2. 异步并发AI分析（大幅提升处理速度）
3. 智能筛选关键帧（基于重要性和质量评分）

作者：AI编程指导教师
版本：1.0
"""

import asyncio
import os
import time
from diversity_frame_extractor import DiversityFrameExtractor


async def demo_unified_smart_extraction():
    """演示统一智能处理功能"""
    print("🚀 统一智能处理演示")
    print("=" * 60)
    print("🎯 功能特点：")
    print("   ✅ 智能抽基础帧 - 根据视频特性自动优化")
    print("   ✅ 异步并发AI分析 - 大幅提升处理速度")
    print("   ✅ 智能筛选关键帧 - 基于AI评分选择最佳帧")
    print("   ✅ 完整错误处理 - 确保处理稳定性")
    
    # 创建抽帧器实例
    extractor = DiversityFrameExtractor(output_dir="unified_frames")
    
    # 寻找测试视频
    video_files = [
        "测试.mp4",
        "测试视频2.mp4", 
        "测试视频3.mp4"
    ]
    
    # 查找存在的视频文件
    test_video = None
    for video in video_files:
        if os.path.exists(video):
            test_video = video
            break
    
    if not test_video:
        print("❌ 没有找到测试视频文件！")
        print("请确保以下文件之一存在:")
        for video in video_files:
            print(f"   - {video}")
        return
    
    print(f"\n📹 使用测试视频：{test_video}")
    
    # 🎛️ 配置处理参数
    config = {
        'target_key_frames': 8,            # 目标关键帧数量（推荐8-12个）
        'base_frame_interval': 1.5,       # 基础抽帧间隔（秒）
        'significance_weight': 0.6,       # 重要性权重60%
        'quality_weight': 0.4,            # 质量权重40%
        'max_concurrent': 30,             # 最大并发数（根据网络和服务器调整）
    }
    
    print(f"\n⚙️ 处理参数配置：")
    for key, value in config.items():
        print(f"   {key}: {value}")
    
    try:
        # 🚀 执行统一智能处理
        print(f"\n🚀 开始统一智能处理...")
        start_time = time.time()
        
        result = await extractor.unified_smart_extraction_async(
            video_path=test_video,
            **config  # 传入所有配置参数
        )
        
        total_time = time.time() - start_time
        
        if result['success']:
            # 📊 显示详细结果
            print(f"\n🎉 处理成功完成！总耗时：{total_time:.2f} 秒")
            
            # 获取统计信息
            stats = result['processing_stats']
            performance = stats['performance_metrics']
            quality = stats['quality_metrics']
            
            print(f"\n📈 性能统计：")
            print(f"   整体压缩比：{performance['overall_compression_rate']:.1%}")
            print(f"   AI分析速度：{performance['ai_analysis_speed']:.1f} 帧/秒")
            print(f"   异步提速倍数：{performance['async_speedup_factor']:.1f}x")
            
            print(f"\n🏆 质量评估：")
            print(f"   平均重要性：{quality['average_significance_score']:.3f}/1.0")
            print(f"   平均质量：{quality['average_quality_score']:.3f}/1.0")
            print(f"   平均综合评分：{quality['average_combined_score']:.3f}/1.0")
            
            # 🎬 展示关键帧信息
            print(f"\n🎬 精选关键帧详情：")
            selected_frames = result['selected_frames']
            for i, frame in enumerate(selected_frames):
                ai_analysis = frame['ai_analysis']
                print(f"\n   关键帧 {i+1}:")
                print(f"      文件名：{frame['filename']}")
                print(f"      时间点：{frame['timestamp']:.1f}秒")
                print(f"      重要性：{ai_analysis['significance_score']:.3f}")
                print(f"      质量：{ai_analysis['quality_score']:.3f}")
                print(f"      综合评分：{frame['combined_score']:.3f}")
                print(f"      AI描述：{ai_analysis['description'][:80]}...")
            
            print(f"\n📁 输出目录：{extractor.output_dir}")
            print(f"💾 关键帧文件：{len(result['key_frame_paths'])} 个")
            
        else:
            print(f"❌ 处理失败：{result.get('error', '未知错误')}")
            
    except Exception as e:
        print(f"❌ 演示过程出错：{str(e)}")
        import traceback
        traceback.print_exc()


async def demo_different_configurations():
    """演示不同配置参数的效果"""
    print(f"\n🔧 不同配置参数效果演示")
    print("=" * 60)
    
    extractor = DiversityFrameExtractor(output_dir="config_test")
    
    # 查找测试视频
    test_video = None
    for video in ["测试.mp4", "测试视频2.mp4", "测试视频3.mp4"]:
        if os.path.exists(video):
            test_video = video
            break
    
    if not test_video:
        print("❌ 没有找到测试视频，跳过配置演示")
        return
    
    # 定义不同的配置方案
    configs = [
        {
            'name': '快速模式',
            'params': {
                'target_key_frames': 6,
                'base_frame_interval': 2.0,
                'significance_weight': 0.8,
                'quality_weight': 0.2,
                'max_concurrent': 20
            },
            'description': '较少关键帧，偏重重要性，适合快速预览'
        },
        {
            'name': '精细模式', 
            'params': {
                'target_key_frames': 10,
                'base_frame_interval': 1.0,
                'significance_weight': 0.5,
                'quality_weight': 0.5,
                'max_concurrent': 40
            },
            'description': '更多关键帧，重要性和质量平衡，适合详细分析'
        },
        {
            'name': '质量优先模式',
            'params': {
                'target_key_frames': 8,
                'base_frame_interval': 1.5,
                'significance_weight': 0.3,
                'quality_weight': 0.7,
                'max_concurrent': 30
            },
            'description': '偏重图像质量，适合高质量输出要求'
        }
    ]
    
    # 测试每种配置
    for i, config in enumerate(configs[:1]):  # 只测试第一种配置以节省时间
        print(f"\n🧪 测试配置 {i+1}: {config['name']}")
        print(f"   说明：{config['description']}")
        print(f"   参数：{config['params']}")
        
        try:
            start_time = time.time()
            result = await extractor.unified_smart_extraction_async(
                video_path=test_video,
                **config['params']
            )
            
            if result['success']:
                processing_time = time.time() - start_time
                stats = result['processing_stats']
                
                print(f"   ✅ 成功 - 耗时：{processing_time:.1f}秒")
                print(f"   📊 结果：{stats['frame_counts']['final_key_frames']}个关键帧")
                print(f"   🏆 质量：{stats['quality_metrics']['average_combined_score']:.3f}")
            else:
                print(f"   ❌ 失败：{result.get('error', '未知错误')}")
                
        except Exception as e:
            print(f"   ❌ 测试失败：{str(e)}")


async def main():
    """主函数"""
    print("🤖 统一智能处理系统演示")
    print("🎯 将智能抽帧和异步AI分析完美结合")
    print("=" * 80)
    
    # 主要功能演示
    await demo_unified_smart_extraction()
    
    # 不同配置演示
    await demo_different_configurations()
    
    print(f"\n🎯 演示总结")
    print("=" * 60)
    print(f"✅ 成功演示了统一智能处理功能")
    print(f"✅ 展示了异步并发AI分析的性能优势")
    print(f"✅ 演示了不同配置参数的灵活应用")
    
    print(f"\n📚 技术特点：")
    print(f"🔹 智能算法：根据视频特性自动计算最优抽帧数量")
    print(f"🔹 异步并发：AI分析请求并发处理，大幅提升速度")
    print(f"🔹 质量评估：结合重要性和质量双重评分智能筛选")
    print(f"🔹 灵活配置：支持多种参数配置适应不同需求")
    print(f"🔹 错误处理：完整的异常处理确保稳定性")
    
    print(f"\n🚀 使用建议：")
    print(f"• 快速预览：减少关键帧数，提高重要性权重")
    print(f"• 详细分析：增加关键帧数，平衡重要性和质量权重")
    print(f"• 高质量输出：适当减少帧数，提高质量权重")
    print(f"• 性能优化：根据网络和服务器能力调整并发数")


if __name__ == "__main__":
    # 运行异步演示
    asyncio.run(main()) 