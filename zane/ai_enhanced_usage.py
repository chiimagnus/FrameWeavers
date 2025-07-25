#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI增强智能抽帧 - 完整使用示例

演示如何使用两阶段智能抽帧：
1. 第一阶段：基于视频特性的智能均匀抽帧
2. 第二阶段：基于AI分析的关键帧筛选
"""

from diversity_frame_extractor import DiversityFrameExtractor
import json
from datetime import datetime

def basic_intelligent_extraction(video_path: str):
    """基础智能抽帧示例"""
    print("🚀 基础智能抽帧模式")
    print("="*50)
    
    # 创建抽帧器
    extractor = DiversityFrameExtractor(output_dir="basic_frames")
    
    # 执行智能均匀抽帧
    frames = extractor.extract_uniform_frames(
        video_path=video_path,
        target_interval_seconds=1.0  # 每秒一帧
    )
    
    # 生成报告
    report = extractor.create_extraction_report(video_path, frames, len(frames))
    
    print(f"\n✅ 基础抽帧完成：")
    print(f"   提取帧数：{len(frames)}")
    print(f"   处理状态：{'成功' if report['success'] else '失败'}")
    
    return frames, report

def ai_enhanced_extraction(video_path: str, demo_mode: bool = True):
    """AI增强抽帧示例"""
    print("\n🤖 AI增强关键帧筛选模式")
    print("="*50)
    
    # 创建抽帧器
    extractor = DiversityFrameExtractor(output_dir="ai_enhanced_frames")
    
    if demo_mode:
        # 演示模式：处理较少帧数以节省时间
        print("📝 演示模式：处理前5个基础帧")
        
        # 第一步：提取基础帧
        base_frames = extractor.extract_uniform_frames(video_path, target_interval_seconds=2.0)
        demo_frames = base_frames[:5]  # 只取前5帧
        
        # 第二步：AI分析
        analyzed_frames = extractor.analyze_frames_with_ai(demo_frames)
        
        # 第三步：筛选关键帧
        key_frames = extractor.select_key_frames_by_ai(
            analyzed_frames, 
            target_key_frames=3,
            significance_weight=0.6,
            quality_weight=0.4
        )
        
        # 第四步：保存关键帧
        saved_paths = extractor.save_key_frames(key_frames, "ai_demo_key")
        
        return {
            'base_frames': demo_frames,
            'analyzed_frames': analyzed_frames,
            'key_frames': key_frames,
            'saved_paths': saved_paths
        }
    else:
        # 完整模式：使用完整的AI分析流程
        print("🔥 完整模式：使用完整AI分析流程")
        result = extractor.extract_ai_key_frames(
            video_path=video_path,
            target_interval_seconds=1.0,
            target_key_frames=8,  # 符合需求的8-12个关键帧
            significance_weight=0.6,
            quality_weight=0.4
        )
        return result

def create_comic_data_structure(key_frames_info: dict, video_path: str) -> dict:
    """
    创建符合连环画需求的数据结构
    
    Args:
        key_frames_info: AI分析的关键帧信息
        video_path: 视频路径
        
    Returns:
        符合需求文档的JSON数据结构
    """
    print("\n📋 生成连环画数据结构")
    print("="*50)
    
    # 获取关键帧信息
    if 'key_frames' in key_frames_info:
        # 演示模式数据结构
        selected_frames = key_frames_info['key_frames']
        key_frame_paths = key_frames_info['saved_paths']
    else:
        # 完整模式数据结构
        selected_frames = key_frames_info['selected_frames']
        key_frame_paths = key_frames_info['key_frame_paths']
    
    # 构建连环画数据结构（符合需求文档格式）
    comic_data = {
        "comic_id": f"comic_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "created_at": datetime.now().isoformat(),
        "source_video": video_path,
        "generation_method": "ai_enhanced_key_frame_selection",
        "frames": [],
        "interactive_questions": [],  # 待后续AI生成
        "metadata": {
            "total_key_frames": len(selected_frames),
            "processing_method": "two_stage_ai_analysis",
            "ai_analysis_enabled": True
        }
    }
    
    # 添加每个关键帧的信息
    for i, frame_info in enumerate(selected_frames):
        ai_analysis = frame_info['ai_analysis']
        
        frame_data = {
            "image_url": key_frame_paths[i] if i < len(key_frame_paths) else "",
            "narration": ai_analysis['description'],  # 使用AI生成的描述作为旁白
            "width": frame_info['width'],
            "height": frame_info['height'],
            "index": i,
            "ai_scores": {
                "significance_score": ai_analysis['significance_score'],
                "quality_score": ai_analysis['quality_score'],
                "combined_score": frame_info.get('combined_score', 0)
            }
        }
        comic_data["frames"].append(frame_data)
    
    print(f"✅ 连环画数据结构生成完成")
    print(f"   连环画ID：{comic_data['comic_id']}")
    print(f"   关键帧数量：{len(comic_data['frames'])}")
    print(f"   平均重要性评分：{sum(f['ai_scores']['significance_score'] for f in comic_data['frames']) / len(comic_data['frames']):.3f}")
    
    return comic_data

def save_results(comic_data: dict, filename: str = "ai_comic_output.json"):
    """保存结果到文件"""
    print(f"\n💾 保存结果到：{filename}")
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(comic_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 结果已保存")

def main():
    """主演示函数"""
    print("🎬 AI增强智能视频抽帧系统")
    print("="*60)
    
    video_path = "测试.mp4"
    
    # 检查视频文件
    import os
    if not os.path.exists(video_path):
        print(f"❌ 测试视频不存在：{video_path}")
        return
    
    # 选择处理模式
    print("\n请选择处理模式：")
    print("1. 基础智能抽帧（快速）")
    print("2. AI增强抽帧 - 演示模式（中等速度，处理5帧）")
    print("3. AI增强抽帧 - 完整模式（较慢，完整AI分析）")
    
    try:
        choice = input("\n请输入选择 (1/2/3): ").strip()
        
        if choice == "1":
            # 基础智能抽帧
            frames, report = basic_intelligent_extraction(video_path)
            print(f"\n🎯 基础模式完成，提取了 {len(frames)} 帧")
            
        elif choice == "2":
            # AI增强抽帧 - 演示模式
            result = ai_enhanced_extraction(video_path, demo_mode=True)
            
            # 创建连环画数据结构
            comic_data = create_comic_data_structure(result, video_path)
            
            # 保存结果
            save_results(comic_data, "ai_demo_comic.json")
            
            # 展示结果
            print(f"\n🎬 AI演示模式完成")
            print(f"   基础帧：{len(result['base_frames'])} → 关键帧：{len(result['key_frames'])}")
            
            # 展示关键帧详情
            print(f"\n📋 AI筛选的关键帧详情：")
            for i, frame in enumerate(result['key_frames']):
                ai_info = frame['ai_analysis']
                print(f"   关键帧{i+1}: {frame['filename']}")
                print(f"      重要性：{ai_info['significance_score']:.3f}, 质量：{ai_info['quality_score']:.3f}")
                print(f"      描述：{ai_info['description'][:60]}...")
            
        elif choice == "3":
            # AI增强抽帧 - 完整模式
            print("⚠️  完整模式需要较长时间进行AI分析，确认继续？")
            confirm = input("输入 'yes' 确认：").lower().strip()
            
            if confirm == 'yes':
                result = ai_enhanced_extraction(video_path, demo_mode=False)
                
                if result['success']:
                    # 创建连环画数据结构
                    comic_data = create_comic_data_structure(result, video_path)
                    
                    # 保存结果
                    save_results(comic_data, "ai_full_comic.json")
                    
                    # 展示统计信息
                    stats = result['processing_stats']
                    print(f"\n🎯 AI完整模式完成")
                    print(f"   基础帧：{stats['base_frames_count']} → 关键帧：{stats['key_frames_count']}")
                    print(f"   平均重要性：{stats['average_significance_score']:.3f}")
                    print(f"   平均质量：{stats['average_quality_score']:.3f}")
                    print(f"   总处理时间：{stats['total_processing_time']:.1f}秒")
                else:
                    print("❌ AI完整模式处理失败")
            else:
                print("已取消完整模式")
                
        else:
            print("❌ 无效选择")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断操作")
    except Exception as e:
        print(f"\n❌ 处理过程中出现错误：{e}")
    
    print(f"\n🎉 演示完成！")
    print(f"   • 基础模式：快速均匀抽帧，适合预览")
    print(f"   • AI演示模式：小规模AI分析，适合测试")
    print(f"   • AI完整模式：全面AI分析，适合生产环境")

if __name__ == "__main__":
    main() 