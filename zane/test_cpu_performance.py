#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CPU性能测试脚本
测试OpenCV在CPU环境下的性能表现
"""

import cv2
import os
import time
import psutil
import numpy as np
from diversity_frame_extractor import DiversityFrameExtractor

def test_cpu_performance():
    """测试CPU性能和资源使用情况"""
    print("=== OpenCV CPU性能测试 ===\n")
    
    # 显示系统信息
    print(f"🖥️  系统信息：")
    print(f"   CPU核心数：{os.cpu_count()}")
    print(f"   可用内存：{psutil.virtual_memory().available / (1024**3):.1f} GB")
    print(f"   OpenCV版本：{cv2.__version__}")
    print(f"   OpenCV优化状态：{'✅ 已启用' if cv2.useOptimized() else '❌ 未启用'}")
    print(f"   OpenCV线程数：{cv2.getNumThreads()}")
    
    # 测试视频文件
    test_video = "测试视频3.mp4"
    if not os.path.exists(test_video):
        print(f"\n❌ 测试视频不存在：{test_video}")
        print("请确保有测试视频文件")
        return
    
    print(f"\n🎬 测试视频：{test_video}")
    
    # 创建抽帧器
    extractor = DiversityFrameExtractor(output_dir="cpu_test_frames")
    
    # 监控资源使用
    process = psutil.Process()
    initial_memory = process.memory_info().rss / (1024**2)  # MB
    
    print(f"\n⚡ 开始性能测试...")
    print(f"   初始内存使用：{initial_memory:.1f} MB")
    
    start_time = time.time()
    
    try:
        # 测试基础抽帧性能
        print(f"\n📊 测试1：基础抽帧性能")
        frames = extractor.extract_uniform_frames(
            video_path=test_video,
            target_interval_seconds=2.0  # 每2秒一帧，减少处理量
        )
        
        basic_time = time.time() - start_time
        current_memory = process.memory_info().rss / (1024**2)
        memory_usage = current_memory - initial_memory
        
        print(f"   ✅ 基础抽帧完成")
        print(f"   处理时间：{basic_time:.2f} 秒")
        print(f"   提取帧数：{len(frames)} 帧")
        print(f"   处理速度：{len(frames)/basic_time:.1f} 帧/秒")
        print(f"   内存增长：{memory_usage:.1f} MB")
        print(f"   CPU使用率：{psutil.cpu_percent(interval=1):.1f}%")
        
        # 测试图像读写性能
        print(f"\n📊 测试2：图像读写性能")
        io_start = time.time()
        
        for i, frame_path in enumerate(frames[:5]):  # 测试前5帧
            img = cv2.imread(frame_path)
            if img is not None:
                # 模拟一些基本的图像处理
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                resized = cv2.resize(gray, (640, 480))
                
                # 保存处理后的图像
                test_output = f"cpu_test_frames/processed_{i:02d}.jpg"
                cv2.imwrite(test_output, resized)
                
                # 及时释放内存
                del img, gray, resized
        
        io_time = time.time() - io_start
        final_memory = process.memory_info().rss / (1024**2)
        
        print(f"   ✅ 图像处理完成")
        print(f"   处理时间：{io_time:.2f} 秒")
        print(f"   平均速度：{5/io_time:.1f} 帧/秒")
        print(f"   最终内存：{final_memory:.1f} MB")
        
        # 性能评估
        print(f"\n📈 性能评估：")
        if len(frames)/basic_time > 10:
            print(f"   抽帧性能：🟢 优秀 ({len(frames)/basic_time:.1f} 帧/秒)")
        elif len(frames)/basic_time > 5:
            print(f"   抽帧性能：🟡 良好 ({len(frames)/basic_time:.1f} 帧/秒)")
        else:
            print(f"   抽帧性能：🔴 需要优化 ({len(frames)/basic_time:.1f} 帧/秒)")
        
        if memory_usage < 100:
            print(f"   内存使用：🟢 优秀 ({memory_usage:.1f} MB)")
        elif memory_usage < 200:
            print(f"   内存使用：🟡 良好 ({memory_usage:.1f} MB)")
        else:
            print(f"   内存使用：🔴 需要优化 ({memory_usage:.1f} MB)")
        
        # 清理测试文件
        print(f"\n🧹 清理测试文件...")
        for frame_path in frames:
            if os.path.exists(frame_path):
                os.remove(frame_path)
        
        # 清理处理后的文件
        for i in range(5):
            test_output = f"cpu_test_frames/processed_{i:02d}.jpg"
            if os.path.exists(test_output):
                os.remove(test_output)
        
        print(f"   ✅ 清理完成")
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
    
    total_time = time.time() - start_time
    print(f"\n⏱️  总测试时间：{total_time:.2f} 秒")
    print(f"✅ CPU性能测试完成！")

def test_opencv_backends():
    """测试OpenCV可用的后端"""
    print("\n=== OpenCV后端信息 ===")
    
    # 检查可用的后端
    backends = []
    backend_names = {
        cv2.CAP_V4L2: "V4L2",
        cv2.CAP_FFMPEG: "FFmpeg", 
        cv2.CAP_GSTREAMER: "GStreamer",
        cv2.CAP_OPENCV_MJPEG: "OpenCV MJPEG"
    }
    
    for backend_id, name in backend_names.items():
        try:
            cap = cv2.VideoCapture()
            if cap.open("", backend_id):
                backends.append(name)
                cap.release()
        except:
            pass
    
    print(f"可用后端：{', '.join(backends) if backends else '默认后端'}")
    
    # 检查图像编解码器
    print(f"支持的图像格式：")
    formats = ['.jpg', '.png', '.bmp', '.tiff']
    for fmt in formats:
        try:
            # 创建测试图像
            test_img = np.zeros((100, 100, 3), dtype=np.uint8)
            test_path = f"test{fmt}"
            success = cv2.imwrite(test_path, test_img)
            if success and os.path.exists(test_path):
                print(f"   ✅ {fmt}")
                os.remove(test_path)
            else:
                print(f"   ❌ {fmt}")
        except:
            print(f"   ❌ {fmt}")

if __name__ == "__main__":
    test_cpu_performance()
    test_opencv_backends()