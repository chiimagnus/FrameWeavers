#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能视频抽帧器 - 简单使用示例

这个示例展示了如何在实际项目中使用 DiversityFrameExtractor 进行智能抽帧
"""

from diversity_frame_extractor import DiversityFrameExtractor

def extract_video_frames(video_path: str, output_dir: str = "output_frames"):
    """
    从视频中智能提取帧的简单函数
    
    Args:
        video_path: 视频文件路径
        output_dir: 输出目录
        
    Returns:
        提取的帧文件路径列表
    """
    # 创建智能抽帧器
    extractor = DiversityFrameExtractor(output_dir=output_dir)
    
    try:
        # 智能抽帧（系统会自动根据视频特性决定帧数）
        frame_paths = extractor.extract_uniform_frames(
            video_path=video_path,
            target_interval_seconds=1.0  # 目标每秒一帧
        )
        
        print(f"✅ 成功提取 {len(frame_paths)} 帧")
        return frame_paths
        
    except Exception as e:
        print(f"❌ 抽帧失败：{e}")
        return []

def batch_process_videos(video_list: list):
    """
    批量处理多个视频
    
    Args:
        video_list: 视频文件路径列表
    """
    for i, video_path in enumerate(video_list):
        print(f"\n📹 处理视频 {i+1}/{len(video_list)}: {video_path}")
        
        # 为每个视频创建独立的输出目录
        output_dir = f"frames_video_{i+1}"
        
        # 提取帧
        frames = extract_video_frames(video_path, output_dir)
        
        if frames:
            print(f"   保存到：{output_dir}/")

# 使用示例
if __name__ == "__main__":
    print("=== 智能视频抽帧 - 使用示例 ===\n")
    
    # 示例1：处理单个视频
    print("📝 示例1：处理单个视频")
    frames = extract_video_frames("测试.mp4", "demo_frames")
    
    # 示例2：批量处理（如果有多个视频的话）
    # video_files = ["video1.mp4", "video2.mp4", "video3.mp4"]
    # batch_process_videos(video_files)
    
    print("\n🎯 提示：")
    print("- 系统会根据视频时长自动决定抽帧数量")
    print("- 短视频密集采样，长视频稀疏采样")
    print("- 无需手动设置帧数，智能优化处理") 