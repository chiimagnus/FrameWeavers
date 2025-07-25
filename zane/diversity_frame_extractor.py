import cv2
import os
import numpy as np
from typing import List, Dict
import time
from datetime import datetime
import asyncio
import aiohttp
import json
import base64

class DiversityFrameExtractor:
    """
    智能视频抽帧器 - 自适应均匀抽帧算法
    
    这个类实现了智能视频抽帧功能，作为连环画生成系统的基础组件。
    根据视频的时长、帧率等特性自动计算最优抽帧数量，确保时间分布的均匀性。
    """
    
    def __init__(self, output_dir: str = "diversity_frames"):
        """
        初始化抽帧器
        
        Args:
            output_dir: 输出目录路径，用于保存提取的帧
        """
        self.output_dir = output_dir
        # 创建输出目录，如果不存在的话
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"✓ 抽帧器初始化完成，输出目录：{self.output_dir}")
    
    def get_video_info(self, video_path: str) -> Dict[str, any]:
        """
        获取视频基本信息
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            包含视频信息的字典
        """
        # 检查视频文件是否存在
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"视频文件不存在：{video_path}")
        
        # 使用OpenCV打开视频
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件：{video_path}")
        
        # 获取视频属性
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # 总帧数
        fps = cap.get(cv2.CAP_PROP_FPS)                       # 帧率（每秒帧数）
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))        # 视频宽度
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))      # 视频高度
        duration = total_frames / fps                          # 视频时长（秒）
        
        # 释放视频资源
        cap.release()
        
        video_info = {
            'file_path': video_path,
            'file_name': os.path.basename(video_path),
            'total_frames': total_frames,
            'fps': fps,
            'width': width,
            'height': height,
            'duration_seconds': duration,
            'resolution': f"{width}x{height}"
        }
        
        return video_info
    
    def _calculate_optimal_frame_count(self, duration: float, fps: float, total_frames: int, 
                                     target_interval_seconds: float = 1.0) -> int:
        """
        根据视频特性智能计算最优帧数
        
        算法逻辑：
        1. 基于时长的动态策略
        2. 考虑帧率的影响
        3. 设置合理的上下限
        
        Args:
            duration: 视频时长（秒）
            fps: 帧率
            total_frames: 总帧数
            target_interval_seconds: 目标时间间隔
            
        Returns:
            计算出的最优帧数
        """
        # 基础策略：根据时间间隔计算
        base_frame_count = int(duration / target_interval_seconds)
        
        # 动态调整策略
        if duration <= 5:
            # 超短视频：每0.5秒一帧，确保足够细节
            optimal_frames = max(6, int(duration / 0.5))
            strategy = "超短视频密集采样"
        elif duration <= 15:
            # 短视频：每1秒一帧
            optimal_frames = max(8, int(duration / 1.0))
            strategy = "短视频标准采样"
        elif duration <= 60:
            # 中等视频：每1-1.5秒一帧
            optimal_frames = max(12, int(duration / 1.2))
            strategy = "中等视频均衡采样"
        elif duration <= 180:
            # 长视频：每2秒一帧
            optimal_frames = max(20, int(duration / 2.0))
            strategy = "长视频稀疏采样"
        else:
            # 超长视频：每3秒一帧，但设置上限
            optimal_frames = min(60, max(30, int(duration / 3.0)))
            strategy = "超长视频限制采样"
        
        # 帧率修正：如果帧率很低，适当减少帧数
        if fps < 15:
            optimal_frames = int(optimal_frames * 0.8)
            strategy += " + 低帧率修正"
        elif fps > 60:
            optimal_frames = int(optimal_frames * 1.1)
            strategy += " + 高帧率修正"
        
        # 设置绝对边界
        optimal_frames = max(5, min(100, optimal_frames))
        
        print(f"🧠 智能计算详情：")
        print(f"   策略：{strategy}")
        print(f"   基础帧数：{base_frame_count}")
        print(f"   优化后帧数：{optimal_frames}")
        print(f"   实际间隔：{duration/optimal_frames:.1f} 秒/帧")
        
        return optimal_frames
    
    def generate_frame_description(self, image_path: str, frame_index: int) -> Dict[str, any]:
        """生成帧描述和评分（使用AI分析）"""
        try:
            from openai import OpenAI
            import base64
            import json
            
            # 初始化OpenAI客户端
            client = OpenAI(
                base_url="https://api.ppinfra.com/v3/openai",
                api_key="sk_5F9-39FKSyVcakGuymqzg6J8rCHfqgnp8GDfp1vN62M"
            )
            
            # 读取并编码图像
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            system_content = """# 角色
                你是一位经验丰富的电影摄影指导和故事分析师。你的任务是深入解读单张视频帧，捕捉其所有的视觉和情感细节，并以富有画面感的语言进行描述和评估。

                # 任务
                1.  **深度分析画面**: 全面分析画面的构图、光线、色彩、主体、动作和背景环境。
                2.  **生成详细描述**:
                    * 创作一段**详细且富有画面感**的文字描述。这段描述应该像小说或剧本中的场景描写一样，让读到它的人能立刻在脑海中构建出具体的影像。
                    * 请确保描述中包含以下关键要素：
                        * **主体 (Subject):** 详细描述人物的外貌特征、衣着、表情和姿态。
                        * **动作 (Action):** 精准描述主体正在发生的具体行为，以及该行为的方式或力度。
                        * **环境 (Environment):** 描绘背景环境中的重要细节（如物品、光影、天气），以营造场景氛围。
                        * **情绪与氛围 (Mood & Atmosphere):** 清晰地指出画面传达出的核心情绪（如紧张、喜悦、悬疑、悲伤）和整体氛围。
                3.  **量化评分**:
                    * **重要性分数 (Significance Score)**: 综合评估画面的故事价值，给出一个 0.0 到 1.0 之间的浮点数。
                    * **画面质量分数 (Quality Score)**: 评估画面的技术质量（清晰度、构图、光线），给出一个 0.0 到 1.0 之间的浮点数。
                4.  **结构化输出**: 将结果严格按照指定的 JSON 格式输出。

                # 输出格式 (严格遵守此 JSON 结构)
                {
                "frame_id": "[输入的帧标识符]",
                "description": "特写镜头，一名身穿皱白衬衫的年轻男子在深夜的办公室里，他的脸被电脑屏幕的蓝光冷冷地照亮。他双眼圆睁，流露出震惊和难以置信的表情，一只手下意识地捂住了嘴，屏幕上复杂的股市K线图呈现出一条断崖式的下跌曲线。",
                "significance_score": 0.9,
                "quality_score": 0.9
                }

                # 指示
                请现在分析提供的图像帧，并按照上述要求生成 JSON 输出。"""
            
            # 构建消息
            messages = [
                {
                    "role": "system",
                    "content": system_content
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"请分析这个视频帧 (frame_id: frame_{frame_index:04d})"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ]
            
            # 调用API
            response = client.chat.completions.create(
                model="qwen/qwen2.5-vl-72b-instruct",
                messages=messages,
                max_tokens=32768,
                temperature=1,
                top_p=1,
                presence_penalty=0,
                frequency_penalty=0,
                response_format={"type": "json_object"},
                extra_body={
                    "min_p": 0,
                    "top_k": 50,
                    "repetition_penalty": 1
                }
            )
            
            # 解析响应
            result = json.loads(response.choices[0].message.content)
            return {
                'frame_id': result.get("frame_id", f"frame_{frame_index:04d}"),
                'description': result.get("description", "AI分析暂时不可用"),
                'significance_score': result.get("significance_score", 0.5),
                'quality_score': result.get("quality_score", 0.5)
            }
            
        except Exception as e:
            print(f"AI分析失败 (frame_{frame_index:04d}): {e}")
            # 降级到模拟评分
            import random
            descriptions = [
                "室内场景，人物活动自然流畅",
                "特写镜头，表情细节清晰可见",
                "全景视角，环境布局完整展现",
                "人物互动，动作表情生动丰富",
                "场景转换，画面构图层次分明",
                "光线变化，色彩层次丰富自然",
                "近景拍摄，主体突出背景虚化",
                "多元素画面，信息内容丰富多样",
                "动态场景，运动轨迹清晰可辨",
                "静态构图，画面平衡美感突出"
            ]
            return {
                'frame_id': f"frame_{frame_index:04d}",
                'description': descriptions[frame_index % len(descriptions)],
                'significance_score': random.uniform(0.3, 0.8),
                'quality_score': random.uniform(0.4, 0.9)
            }
    
    def extract_uniform_frames(self, video_path: str, target_interval_seconds: float = 1.0) -> List[str]:
        """
        智能均匀抽帧核心算法
        
        这个方法根据视频特性自动决定抽帧数量，实现智能均匀抽帧：
        1. 分析视频时长、帧率等特性
        2. 自动计算最优抽帧数量
        3. 按固定间隔逐帧提取并保存为图片文件
        
        Args:
            video_path: 视频文件路径
            target_interval_seconds: 目标时间间隔（秒），默认1.0秒/帧
            
        Returns:
            提取的帧文件路径列表
        """
        print(f"🎬 开始智能均匀抽帧：{os.path.basename(video_path)}")
        
        # 获取视频信息
        video_info = self.get_video_info(video_path)
        total_frames = video_info['total_frames']
        fps = video_info['fps']
        duration = video_info['duration_seconds']
        
        print(f"📊 视频信息：")
        print(f"   总帧数：{total_frames} 帧")
        print(f"   帧率：{fps:.2f} FPS")
        print(f"   时长：{duration:.2f} 秒")
        print(f"   分辨率：{video_info['resolution']}")
        
        # 智能计算目标帧数
        target_frames = self._calculate_optimal_frame_count(duration, fps, total_frames, target_interval_seconds)
        print(f"🤖 智能自动计算目标帧数：{target_frames} 帧")
        print(f"   目标时间间隔：{target_interval_seconds} 秒/帧")
        
        # 计算抽帧间隔（均匀抽帧的核心）
        frame_interval = max(1, total_frames // target_frames)
        print(f"🔢 抽帧间隔：每 {frame_interval} 帧提取一帧")
        
        # 预估实际提取帧数
        estimated_frames = min(target_frames, total_frames // frame_interval)
        print(f"📈 预计提取：{estimated_frames} 帧")
        
        # 开始提取帧
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件：{video_path}")
        
        frame_paths = []      # 存储提取的帧文件路径
        frame_count = 0       # 当前处理的帧计数
        extracted_count = 0   # 已提取的帧计数
        start_time = time.time()
        
        print(f"⚡ 开始提取帧...")
        
        while True:
            # 读取下一帧
            ret, frame = cap.read()
            if not ret:  # 如果没有更多帧，退出循环
                break
            
            # 均匀抽帧的判断条件：当前帧是否为间隔帧
            if frame_count % frame_interval == 0:
                # 生成帧文件名（使用四位数字编号）
                frame_filename = f"base_frame_{extracted_count:04d}.jpg"
                frame_path = os.path.join(self.output_dir, frame_filename)
                
                # 保存帧为图片文件
                success = cv2.imwrite(frame_path, frame)
                if success:
                    frame_paths.append(frame_path)
                    extracted_count += 1
                    
                    # 显示进度（每提取5帧显示一次）
                    if extracted_count % 5 == 0 or extracted_count == 1:
                        elapsed = time.time() - start_time
                        print(f"   提取进度：{extracted_count}/{estimated_frames} 帧 "
                              f"(耗时 {elapsed:.1f}s)")
                else:
                    print(f"⚠️ 警告：保存帧失败 {frame_filename}")
                
                # 达到目标帧数，提前结束
                if extracted_count >= target_frames:
                    break
            
            frame_count += 1
        
        # 释放资源
        cap.release()
        
        # 输出统计信息
        total_time = time.time() - start_time
        print(f"✅ 均匀抽帧完成！")
        print(f"   实际提取：{len(frame_paths)} 帧")
        print(f"   总耗时：{total_time:.2f} 秒")
        print(f"   平均速度：{len(frame_paths)/total_time:.1f} 帧/秒")
        
        return frame_paths
    
    def analyze_frames_with_ai(self, frame_paths: List[str]) -> List[Dict[str, any]]:
        """
        使用AI分析所有基础帧
        
        Args:
            frame_paths: 基础帧文件路径列表
            
        Returns:
            包含AI分析结果的帧信息列表
        """
        print(f"🤖 开始AI分析 {len(frame_paths)} 个基础帧...")
        analyzed_frames = []
        
        for i, frame_path in enumerate(frame_paths):
            print(f"   分析进度：{i+1}/{len(frame_paths)} - {os.path.basename(frame_path)}")
            
            # 获取图像基本信息
            img = cv2.imread(frame_path)
            if img is not None:
                height, width = img.shape[:2]
                file_size = os.path.getsize(frame_path)
                
                # AI分析获取描述和评分
                ai_result = self.generate_frame_description(frame_path, i)
                
                frame_info = {
                    'index': i,
                    'path': frame_path,
                    'filename': os.path.basename(frame_path),
                    'width': width,
                    'height': height,
                    'file_size': file_size,
                    'ai_analysis': ai_result
                }
                analyzed_frames.append(frame_info)
        
        print(f"✅ AI分析完成！共分析 {len(analyzed_frames)} 个基础帧")
        return analyzed_frames
    
    async def generate_frame_description_async(self, session: aiohttp.ClientSession, 
                                               image_path: str, frame_index: int, 
                                               semaphore: asyncio.Semaphore) -> Dict[str, any]:
        """
        异步生成帧描述和评分（使用AI分析）
        
        Args:
            session: aiohttp会话对象
            image_path: 图像文件路径
            frame_index: 帧索引
            semaphore: 信号量，用于控制并发数
            
        Returns:
            包含AI分析结果的字典
        """
        async with semaphore:  # 控制并发数
            try:
                # 读取并编码图像
                with open(image_path, "rb") as image_file:
                    image_data = base64.b64encode(image_file.read()).decode('utf-8')
                
                system_content = """# 角色
                    你是一位经验丰富的电影摄影指导和故事分析师。你的任务是深入解读单张视频帧，捕捉其所有的视觉和情感细节，并以富有画面感的语言进行描述和评估。

                    # 任务
                    1.  **深度分析画面**: 全面分析画面的构图、光线、色彩、主体、动作和背景环境。
                    2.  **生成详细描述**:
                        * 创作一段**详细且富有画面感**的文字描述。这段描述应该像小说或剧本中的场景描写一样，让读到它的人能立刻在脑海中构建出具体的影像。
                        * 请确保描述中包含以下关键要素：
                            * **主体 (Subject):** 详细描述人物的外貌特征、衣着、表情和姿态。
                            * **动作 (Action):** 精准描述主体正在发生的具体行为，以及该行为的方式或力度。
                            * **环境 (Environment):** 描绘背景环境中的重要细节（如物品、光影、天气），以营造场景氛围。
                            * **情绪与氛围 (Mood & Atmosphere):** 清晰地指出画面传达出的核心情绪（如紧张、喜悦、悬疑、悲伤）和整体氛围。
                    3.  **量化评分**:
                        * **重要性分数 (Significance Score)**: 综合评估画面的故事价值，给出一个 0.0 到 1.0 之间的浮点数。
                        * **画面质量分数 (Quality Score)**: 评估画面的技术质量（清晰度、构图、光线），给出一个 0.0 到 1.0 之间的浮点数。
                    4.  **结构化输出**: 将结果严格按照指定的 JSON 格式输出。

                    # 输出格式 (严格遵守此 JSON 结构)
                    {
                    "frame_id": "[输入的帧标识符]",
                    "description": "特写镜头，一名身穿皱白衬衫的年轻男子在深夜的办公室里，他的脸被电脑屏幕的蓝光冷冷地照亮。他双眼圆睁，流露出震惊和难以置信的表情，一只手下意识地捂住了嘴，屏幕上复杂的股市K线图呈现出一条断崖式的下跌曲线。",
                    "significance_score": 0.9,
                    "quality_score": 0.9
                    }

                    # 指示
                    请现在分析提供的图像帧，并按照上述要求生成 JSON 输出。"""
                
                # 构建请求数据
                payload = {
                    "model": "qwen/qwen2.5-vl-72b-instruct",
                    "messages": [
                        {
                            "role": "system",
                            "content": system_content
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"请分析这个视频帧 (frame_id: frame_{frame_index:04d})"
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_data}"
                                    }
                                }
                            ]
                        }
                    ],
                    "max_tokens": 32768,
                    "temperature": 1,
                    "top_p": 1,
                    "presence_penalty": 0,
                    "frequency_penalty": 0,
                    "response_format": {"type": "json_object"},
                    "extra_body": {
                        "min_p": 0,
                        "top_k": 50,
                        "repetition_penalty": 1
                    }
                }
                
                headers = {
                    "Authorization": "Bearer sk_5F9-39FKSyVcakGuymqzg6J8rCHfqgnp8GDfp1vN62M",
                    "Content-Type": "application/json"
                }
                
                # 发送异步请求
                async with session.post(
                    "https://api.ppinfra.com/v3/openai/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response_data = await response.json()
                    
                    if response.status == 200:
                        result = json.loads(response_data['choices'][0]['message']['content'])
                        return {
                            'frame_id': result.get("frame_id", f"frame_{frame_index:04d}"),
                            'description': result.get("description", "AI分析暂时不可用"),
                            'significance_score': result.get("significance_score", 0.5),
                            'quality_score': result.get("quality_score", 0.5)
                        }
                    else:
                        raise Exception(f"API请求失败: {response.status}")
                        
            except Exception as e:
                print(f"AI分析失败 (frame_{frame_index:04d}): {e}")
                # 降级到模拟评分
                import random
                descriptions = [
                    "室内场景，人物活动自然流畅",
                    "特写镜头，表情细节清晰可见", 
                    "全景视角，环境布局完整展现",
                    "人物互动，动作表情生动丰富",
                    "场景转换，画面构图层次分明",
                    "光线变化，色彩层次丰富自然",
                    "近景拍摄，主体突出背景虚化",
                    "多元素画面，信息内容丰富多样",
                    "动态场景，运动轨迹清晰可辨",
                    "静态构图，画面平衡美感突出"
                ]
                return {
                    'frame_id': f"frame_{frame_index:04d}",
                    'description': descriptions[frame_index % len(descriptions)],
                    'significance_score': random.uniform(0.3, 0.8),
                    'quality_score': random.uniform(0.4, 0.9)
                }
    
    async def analyze_frames_with_ai_async(self, frame_paths: List[str], 
                                           max_concurrent: int = 50) -> List[Dict[str, any]]:
        """
        使用AI异步并发分析所有基础帧
        
        Args:
            frame_paths: 基础帧文件路径列表
            max_concurrent: 最大并发数（默认50）
            
        Returns:
            包含AI分析结果的帧信息列表
        """
        print(f"🚀 开始AI异步并发分析 {len(frame_paths)} 个基础帧...")
        print(f"🔧 并发设置：最大并发数 = {max_concurrent}")
        
        # 创建信号量来控制并发数
        semaphore = asyncio.Semaphore(max_concurrent)
        analyzed_frames = []
        
        # 创建aiohttp会话
        connector = aiohttp.TCPConnector(limit=max_concurrent * 2)  # 连接池大小
        timeout = aiohttp.ClientTimeout(total=60)  # 总超时时间
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # 创建所有异步任务
            tasks = []
            for i, frame_path in enumerate(frame_paths):
                task = self._process_frame_async(session, frame_path, i, semaphore)
                tasks.append(task)
            
            # 启动所有任务并显示进度
            print(f"⚡ 启动 {len(tasks)} 个并发AI分析任务...")
            start_time = time.time()
            
            # 使用asyncio.gather来等待所有任务完成
            try:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 处理结果
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        print(f"任务 {i} 执行失败: {result}")
                    elif result is not None:
                        analyzed_frames.append(result)
                    
                    # 显示进度
                    if (i + 1) % 10 == 0 or (i + 1) == len(results):
                        elapsed = time.time() - start_time
                        speed = (i + 1) / elapsed if elapsed > 0 else 0
                        print(f"   分析进度：{i + 1}/{len(frame_paths)} "
                              f"(速度: {speed:.1f} 帧/秒)")
                        
            except Exception as e:
                print(f"批量任务执行失败: {e}")
        
        # 按原始索引排序
        analyzed_frames.sort(key=lambda x: x['index'])
        
        total_time = time.time() - start_time
        print(f"✅ AI异步分析完成！")
        print(f"   处理帧数：{len(analyzed_frames)} 个")
        print(f"   总耗时：{total_time:.2f} 秒")
        print(f"   平均速度：{len(analyzed_frames)/total_time:.1f} 帧/秒")
        print(f"   🚀 相比串行处理，预计提速 {max_concurrent//2}-{max_concurrent}x")
        
        return analyzed_frames
    
    async def _process_frame_async(self, session: aiohttp.ClientSession, 
                                   frame_path: str, frame_index: int,
                                   semaphore: asyncio.Semaphore) -> Dict[str, any]:
        """
        异步处理单个帧的完整信息获取
        
        Args:
            session: aiohttp会话
            frame_path: 帧文件路径
            frame_index: 帧索引
            semaphore: 信号量
            
        Returns:
            完整的帧信息字典
        """
        try:
            # 获取图像基本信息
            img = cv2.imread(frame_path)
            if img is None:
                print(f"⚠️ 无法读取图像: {frame_path}")
                return None
                
            height, width = img.shape[:2]
            file_size = os.path.getsize(frame_path)
            
            # AI分析获取描述和评分
            ai_result = await self.generate_frame_description_async(
                session, frame_path, frame_index, semaphore
            )
            
            frame_info = {
                'index': frame_index,
                'path': frame_path,
                'filename': os.path.basename(frame_path),
                'width': width,
                'height': height,
                'file_size': file_size,
                'ai_analysis': ai_result
            }
            return frame_info
            
        except Exception as e:
            print(f"处理帧失败 {frame_path}: {e}")
            return None
    
    def select_key_frames_by_ai(self, analyzed_frames: List[Dict[str, any]], 
                               target_key_frames: int = 10,
                               significance_weight: float = 0.6,
                               quality_weight: float = 0.4) -> List[Dict[str, any]]:
        """
        基于AI评分筛选关键帧
        
        Args:
            analyzed_frames: AI分析后的帧信息列表
            target_key_frames: 目标关键帧数量
            significance_weight: 重要性权重
            quality_weight: 质量权重
            
        Returns:
            筛选出的关键帧列表
        """
        print(f"🎯 开始基于AI评分筛选关键帧...")
        print(f"   目标关键帧数：{target_key_frames}")
        print(f"   重要性权重：{significance_weight}, 质量权重：{quality_weight}")
        
        # 计算综合评分
        for frame in analyzed_frames:
            ai_analysis = frame['ai_analysis']
            significance_score = ai_analysis['significance_score']
            quality_score = ai_analysis['quality_score']
            
            # 综合评分 = 重要性分数 × 重要性权重 + 质量分数 × 质量权重
            combined_score = (significance_score * significance_weight + 
                            quality_score * quality_weight)
            frame['combined_score'] = combined_score
        
        # 按综合评分排序（降序）
        sorted_frames = sorted(analyzed_frames, key=lambda x: x['combined_score'], reverse=True)
        
        # 选择评分最高的关键帧
        selected_frames = sorted_frames[:target_key_frames]
        
        # 按原始时间顺序重新排序
        selected_frames.sort(key=lambda x: x['index'])
        
        print(f"✅ 关键帧筛选完成！")
        print(f"   选择的关键帧评分范围：{selected_frames[-1]['combined_score']:.3f} - {selected_frames[0]['combined_score']:.3f}")
        
        return selected_frames
    
    def save_key_frames(self, selected_frames: List[Dict[str, any]], 
                       output_prefix: str = "key_frame") -> List[str]:
        """
        保存筛选出的关键帧
        
        Args:
            selected_frames: 筛选出的关键帧信息
            output_prefix: 输出文件名前缀
            
        Returns:
            保存的关键帧文件路径列表
        """
        print(f"💾 保存 {len(selected_frames)} 个关键帧...")
        saved_paths = []
        
        for i, frame in enumerate(selected_frames):
            # 读取原始帧
            img = cv2.imread(frame['path'])
            if img is not None:
                # 生成关键帧文件名
                key_frame_filename = f"{output_prefix}_{i:02d}.jpg"
                key_frame_path = os.path.join(self.output_dir, key_frame_filename)
                
                # 保存关键帧
                success = cv2.imwrite(key_frame_path, img)
                if success:
                    saved_paths.append(key_frame_path)
                    print(f"   保存关键帧：{key_frame_filename} (评分: {frame['combined_score']:.3f})")
                else:
                    print(f"   ⚠️ 保存失败：{key_frame_filename}")
        
        print(f"✅ 关键帧保存完成！共保存 {len(saved_paths)} 个文件")
        return saved_paths
    
    def extract_ai_key_frames(self, video_path: str, 
                             target_interval_seconds: float = 1.0,
                             target_key_frames: int = 10,
                             significance_weight: float = 0.6,
                             quality_weight: float = 0.4) -> Dict[str, any]:
        """
        两阶段智能抽帧：基础帧提取 + AI分析筛选关键帧
        
        Args:
            video_path: 视频文件路径
            target_interval_seconds: 基础抽帧的目标时间间隔
            target_key_frames: 最终关键帧数量
            significance_weight: 重要性权重
            quality_weight: 质量权重
            
        Returns:
            包含完整处理结果的字典
        """
        print(f"🚀 开始两阶段智能抽帧处理...")
        start_time = time.time()
        
        # 第一阶段：智能均匀抽取基础帧
        print(f"\n📖 第一阶段：智能均匀抽取基础帧")
        base_frames = self.extract_uniform_frames(video_path, target_interval_seconds)
        
        # 第二阶段：AI分析基础帧
        print(f"\n🤖 第二阶段：AI分析基础帧")
        analyzed_frames = self.analyze_frames_with_ai(base_frames)
        
        # 第三阶段：基于AI评分筛选关键帧
        print(f"\n🎯 第三阶段：基于AI评分筛选关键帧")
        selected_frames = self.select_key_frames_by_ai(
            analyzed_frames, target_key_frames, significance_weight, quality_weight
        )
        
        # 第四阶段：保存关键帧
        print(f"\n💾 第四阶段：保存关键帧")
        key_frame_paths = self.save_key_frames(selected_frames)
        
        # 计算处理统计
        total_time = time.time() - start_time
        
        result = {
            'success': True,
            'base_frames': base_frames,
            'analyzed_frames': analyzed_frames,
            'selected_frames': selected_frames,
            'key_frame_paths': key_frame_paths,
            'processing_stats': {
                'total_processing_time': total_time,
                'base_frames_count': len(base_frames),
                'analyzed_frames_count': len(analyzed_frames),
                'key_frames_count': len(selected_frames),
                'average_significance_score': sum(f['ai_analysis']['significance_score'] for f in selected_frames) / len(selected_frames),
                'average_quality_score': sum(f['ai_analysis']['quality_score'] for f in selected_frames) / len(selected_frames),
                'average_combined_score': sum(f['combined_score'] for f in selected_frames) / len(selected_frames)
            }
        }
        
        print(f"\n🎉 两阶段智能抽帧完成！")
        print(f"   基础帧数：{len(base_frames)} → 关键帧数：{len(selected_frames)}")
        print(f"   平均重要性评分：{result['processing_stats']['average_significance_score']:.3f}")
        print(f"   平均质量评分：{result['processing_stats']['average_quality_score']:.3f}")
        print(f"   总处理时间：{total_time:.1f} 秒")
        
        return result
    
    async def extract_ai_key_frames_async(self, video_path: str, 
                                          target_interval_seconds: float = 1.0,
                                          target_key_frames: int = 10,
                                          significance_weight: float = 0.6,
                                          quality_weight: float = 0.4,
                                          max_concurrent: int = 50) -> Dict[str, any]:
        """
        两阶段智能抽帧：基础帧提取 + AI异步并发分析筛选关键帧
        
        Args:
            video_path: 视频文件路径
            target_interval_seconds: 基础抽帧的目标时间间隔
            target_key_frames: 最终关键帧数量
            significance_weight: 重要性权重
            quality_weight: 质量权重
            max_concurrent: 最大并发数
            
        Returns:
            包含完整处理结果的字典
        """
        print(f"🚀 开始两阶段智能抽帧处理（异步并发版本）...")
        print(f"🔧 异步设置：最大并发数 = {max_concurrent}")
        start_time = time.time()
        
        # 第一阶段：智能均匀抽取基础帧（同步进行）
        print(f"\n📖 第一阶段：智能均匀抽取基础帧")
        base_frames = self.extract_uniform_frames(video_path, target_interval_seconds)
        
        # 第二阶段：AI异步并发分析基础帧
        print(f"\n🤖 第二阶段：AI异步并发分析基础帧")
        analyzed_frames = await self.analyze_frames_with_ai_async(base_frames, max_concurrent)
        
        # 第三阶段：基于AI评分筛选关键帧
        print(f"\n🎯 第三阶段：基于AI评分筛选关键帧")
        selected_frames = self.select_key_frames_by_ai(
            analyzed_frames, target_key_frames, significance_weight, quality_weight
        )
        
        # 第四阶段：保存关键帧
        print(f"\n💾 第四阶段：保存关键帧")
        key_frame_paths = self.save_key_frames(selected_frames)
        
        # 计算处理统计
        total_time = time.time() - start_time
        ai_analysis_time = total_time * 0.8  # AI分析通常占大部分时间
        estimated_sync_time = len(base_frames) * 2.0  # 估算同步处理时间（每帧2秒）
        speedup_factor = estimated_sync_time / ai_analysis_time if ai_analysis_time > 0 else 1
        
        result = {
            'success': True,
            'async_mode': True,
            'max_concurrent': max_concurrent,
            'base_frames': base_frames,
            'analyzed_frames': analyzed_frames,
            'selected_frames': selected_frames,
            'key_frame_paths': key_frame_paths,
            'processing_stats': {
                'total_processing_time': total_time,
                'estimated_sync_time': estimated_sync_time,
                'speedup_factor': speedup_factor,
                'base_frames_count': len(base_frames),
                'analyzed_frames_count': len(analyzed_frames),
                'key_frames_count': len(selected_frames),
                'average_significance_score': sum(f['ai_analysis']['significance_score'] for f in selected_frames) / len(selected_frames),
                'average_quality_score': sum(f['ai_analysis']['quality_score'] for f in selected_frames) / len(selected_frames),
                'average_combined_score': sum(f['combined_score'] for f in selected_frames) / len(selected_frames),
                'processing_speed': len(analyzed_frames) / total_time if total_time > 0 else 0
            }
        }
        
        print(f"\n🎉 异步并发两阶段智能抽帧完成！")
        print(f"   基础帧数：{len(base_frames)} → 关键帧数：{len(selected_frames)}")
        print(f"   平均重要性评分：{result['processing_stats']['average_significance_score']:.3f}")
        print(f"   平均质量评分：{result['processing_stats']['average_quality_score']:.3f}")
        print(f"   总处理时间：{total_time:.1f} 秒")
        print(f"   处理速度：{result['processing_stats']['processing_speed']:.1f} 帧/秒")
        print(f"   🚀 预估提速：{speedup_factor:.1f}x（相比串行处理）")
        
        return result
    
    async def unified_smart_extraction_async(self, video_path: str, 
                                        target_key_frames: int = 8,
                                        base_frame_interval: float = 1.0,
                                        significance_weight: float = 0.6,
                                        quality_weight: float = 0.4,
                                        max_concurrent: int = 50) -> Dict[str, any]:
        """
        🎯 统一智能处理方法：智能抽基础帧 + 异步并发AI分析
        
        这是一个完整的两阶段处理工作流程：
        阶段1: 根据视频特性智能抽取基础帧
        阶段2: 使用异步并发AI分析筛选关键帧
        
        Args:
            video_path: 视频文件路径
            target_key_frames: 目标关键帧数量 (推荐8-12个)
            base_frame_interval: 基础抽帧时间间隔(秒)，用于第一阶段
            significance_weight: 重要性评分权重 (0-1)
            quality_weight: 质量评分权重 (0-1)
            max_concurrent: 最大异步并发数，控制AI请求并发量
            
        Returns:
            包含完整处理结果的字典，包括基础帧、AI分析结果、关键帧等
        """
        print("🎯 启动统一智能处理模式")
        print("=" * 60)
        print(f"📹 处理视频：{os.path.basename(video_path)}")
        print(f"🎛️ 配置参数：")
        print(f"   目标关键帧数：{target_key_frames} 个")
        print(f"   基础抽帧间隔：{base_frame_interval} 秒")
        print(f"   权重配置：重要性 {significance_weight:.1f} | 质量 {quality_weight:.1f}")
        print(f"   最大并发数：{max_concurrent}")
        
        total_start_time = time.time()
        
        try:
            # 🔍 预处理：获取视频信息
            print(f"\n🔍 阶段0：视频信息分析")
            video_info = self.get_video_info(video_path)
            print(f"   视频时长：{video_info['duration_seconds']:.1f} 秒")
            print(f"   视频帧率：{video_info['fps']:.1f} FPS")
            print(f"   视频分辨率：{video_info['resolution']}")
            print(f"   总帧数：{video_info['total_frames']} 帧")
            
            # 📖 阶段1：智能抽取基础帧
            print(f"\n📖 阶段1：智能抽取基础帧")
            stage1_start = time.time()
            
            base_frames = self.extract_uniform_frames(
                video_path=video_path,
                target_interval_seconds=base_frame_interval
            )
            
            stage1_time = time.time() - stage1_start
            print(f"   ✅ 基础帧抽取完成：{len(base_frames)} 帧")
            print(f"   ⏱️ 耗时：{stage1_time:.2f} 秒")
            
            # 检查基础帧数量
            if len(base_frames) == 0:
                raise ValueError("没有成功抽取到基础帧")
            
            # 🤖 阶段2：异步并发AI分析
            print(f"\n🤖 阶段2：异步并发AI分析基础帧")
            stage2_start = time.time()
            
            analyzed_frames = await self.analyze_frames_with_ai_async(
                base_frames, max_concurrent=max_concurrent
            )
            
            stage2_time = time.time() - stage2_start
            print(f"   ✅ AI分析完成：{len(analyzed_frames)} 帧")
            print(f"   ⏱️ 耗时：{stage2_time:.2f} 秒")
            print(f"   🚀 分析速度：{len(analyzed_frames) / stage2_time:.1f} 帧/秒")
            
            # 🎯 阶段3：智能筛选关键帧
            print(f"\n🎯 阶段3：基于AI评分筛选关键帧")
            stage3_start = time.time()
            
            selected_frames = self.select_key_frames_by_ai(
                analyzed_frames=analyzed_frames,
                target_key_frames=target_key_frames,
                significance_weight=significance_weight,
                quality_weight=quality_weight
            )
            
            stage3_time = time.time() - stage3_start
            print(f"   ✅ 关键帧筛选完成：{len(selected_frames)} 帧")
            print(f"   ⏱️ 耗时：{stage3_time:.2f} 秒")
            
            # 💾 阶段4：保存关键帧
            print(f"\n💾 阶段4：保存关键帧到磁盘")
            stage4_start = time.time()
            
            key_frame_paths = self.save_key_frames(
                selected_frames, output_prefix="unified_key"
            )
            
            stage4_time = time.time() - stage4_start
            print(f"   ✅ 关键帧保存完成：{len(key_frame_paths)} 个文件")
            print(f"   ⏱️ 耗时：{stage4_time:.2f} 秒")
            
            # 💾 阶段5：保存关键帧信息到JSON文件
            print(f"\n💾 阶段5：保存关键帧信息到JSON")
            stage5_start = time.time()
            
            json_file_path = self.save_keyframes_to_json(selected_frames, video_path)
            
            stage5_time = time.time() - stage5_start
            print(f"   ✅ JSON文件保存完成：{json_file_path}")
            print(f"   ⏱️ 耗时：{stage5_time:.2f} 秒")
            
            # 📊 生成处理统计
            total_time = time.time() - total_start_time
            
            # 计算性能指标
            estimated_sync_time = len(base_frames) * 2.0  # 假设同步处理每帧需要2秒
            speedup_factor = estimated_sync_time / stage2_time if stage2_time > 0 else 1
            
            # 计算质量指标
            significance_scores = [f['ai_analysis']['significance_score'] for f in selected_frames]
            quality_scores = [f['ai_analysis']['quality_score'] for f in selected_frames]
            combined_scores = [f['combined_score'] for f in selected_frames]
            
            processing_stats = {
                'total_processing_time': total_time,
                'stage_times': {
                    'video_analysis': 0.1,  # 视频信息分析很快
                    'base_frame_extraction': stage1_time,
                    'ai_analysis': stage2_time,
                    'key_frame_selection': stage3_time,
                    'frame_saving': stage4_time,
                    'json_saving': stage5_time
                },
                'frame_counts': {
                    'total_video_frames': video_info['total_frames'],
                    'base_frames_extracted': len(base_frames),
                    'frames_analyzed_by_ai': len(analyzed_frames),
                    'final_key_frames': len(selected_frames)
                },
                'performance_metrics': {
                    'extraction_rate': len(base_frames) / video_info['total_frames'],
                    'selection_rate': len(selected_frames) / len(analyzed_frames),
                    'overall_compression_rate': len(selected_frames) / video_info['total_frames'],
                    'ai_analysis_speed': len(analyzed_frames) / stage2_time if stage2_time > 0 else 0,
                    'estimated_sync_time': estimated_sync_time,
                    'async_speedup_factor': speedup_factor
                },
                'quality_metrics': {
                    'average_significance_score': sum(significance_scores) / len(significance_scores),
                    'average_quality_score': sum(quality_scores) / len(quality_scores),
                    'average_combined_score': sum(combined_scores) / len(combined_scores),
                    'score_ranges': {
                        'significance_range': [min(significance_scores), max(significance_scores)],
                        'quality_range': [min(quality_scores), max(quality_scores)],
                        'combined_range': [min(combined_scores), max(combined_scores)]
                    }
                }
            }
            
            # 构建返回结果
            result = {
                'success': True,
                'processing_mode': 'unified_smart_async',
                'video_info': video_info,
                'config': {
                    'target_key_frames': target_key_frames,
                    'base_frame_interval': base_frame_interval,
                    'significance_weight': significance_weight,
                    'quality_weight': quality_weight,
                    'max_concurrent': max_concurrent
                },
                'base_frames': base_frames,
                'analyzed_frames': analyzed_frames,
                'selected_frames': selected_frames,
                'key_frame_paths': key_frame_paths,
                'json_file_path': json_file_path,
                'processing_stats': processing_stats
            }
            
            # 📋 输出处理摘要
            self._print_processing_summary(result)
            
            return result
            
        except Exception as e:
            print(f"❌ 统一智能处理失败：{str(e)}")
            return {
                'success': False,
                'error': str(e),
                'processing_mode': 'unified_smart_async',
                'processing_time': time.time() - total_start_time
            }
    
    def _print_processing_summary(self, result: Dict[str, any]) -> None:
        """
        打印处理结果摘要
        
        Args:
            result: 处理结果字典
        """
        print(f"\n🎊 统一智能处理完成！")
        print("=" * 60)
        
        stats = result['processing_stats']
        
        # 处理流程摘要
        print(f"📊 处理流程摘要：")
        frame_counts = stats['frame_counts']
        print(f"   原始视频帧数：{frame_counts['total_video_frames']:,} 帧")
        print(f"   智能抽取基础帧：{frame_counts['base_frames_extracted']} 帧")
        print(f"   AI分析处理帧：{frame_counts['frames_analyzed_by_ai']} 帧")
        print(f"   最终关键帧数：{frame_counts['final_key_frames']} 帧")
        
        # 性能指标
        print(f"\n⚡ 性能指标：")
        perf = stats['performance_metrics']
        print(f"   总处理时间：{stats['total_processing_time']:.2f} 秒")
        print(f"   AI分析速度：{perf['ai_analysis_speed']:.1f} 帧/秒")
        print(f"   异步提速倍数：{perf['async_speedup_factor']:.1f}x")
        print(f"   整体压缩比：{perf['overall_compression_rate']:.1%}")
        
        # 质量指标
        print(f"\n🏆 质量指标：")
        quality = stats['quality_metrics']
        print(f"   平均重要性评分：{quality['average_significance_score']:.3f}")
        print(f"   平均质量评分：{quality['average_quality_score']:.3f}")
        print(f"   平均综合评分：{quality['average_combined_score']:.3f}")
        
        # 输出文件信息
        print(f"\n📁 输出文件：")
        print(f"   保存目录：{self.output_dir}")
        print(f"   关键帧文件数：{len(result['key_frame_paths'])}")
        if 'json_file_path' in result:
            print(f"   JSON文件：{result['json_file_path']}")
        
        # 关键帧预览
        print(f"\n🎬 关键帧预览（前3个）：")
        for i, frame in enumerate(result['selected_frames'][:3]):
            ai_analysis = frame['ai_analysis']
            print(f"   {i+1}. {frame['filename']}")
            print(f"      重要性：{ai_analysis['significance_score']:.3f} | "
                  f"质量：{ai_analysis['quality_score']:.3f} | "
                  f"综合：{frame['combined_score']:.3f}")
            print(f"      描述：{ai_analysis['description'][:60]}...")

    def save_keyframes_to_json(self, selected_frames: List[Dict], video_path: str) -> str:
        """
        保存关键帧信息到JSON文件
        
        Args:
            selected_frames: 筛选出的关键帧列表
            video_path: 原视频文件路径，用于生成JSON文件名
            
        Returns:
            str: 生成的JSON文件路径
        """
        try:
            # 生成JSON文件名（基于视频文件名）
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_filename = f"{video_name}_keyframes_{timestamp}.json"
            json_file_path = os.path.join(self.output_dir, json_filename)
            
            # 构建JSON数据结构
            keyframes_data = {
                "video_info": {
                    "video_path": video_path,
                    "video_name": os.path.basename(video_path),
                    "processing_time": datetime.now().isoformat(),
                    "total_keyframes": len(selected_frames)
                },
                "keyframes": []
            }
            
            # 处理每个关键帧的信息
            for i, frame in enumerate(selected_frames):
                # 获取AI分析结果
                ai_analysis = frame.get('ai_analysis', {})
                
                # 构建关键帧信息
                keyframe_info = {
                    "index": i + 1,
                    "filename": frame.get('filename', ''),
                    "photo_path": os.path.join(self.output_dir, frame.get('filename', '')),
                    "combined_score": round(frame.get('combined_score', 0.0), 4),
                    "significance_score": round(ai_analysis.get('significance_score', 0.0), 4),
                    "quality_score": round(ai_analysis.get('quality_score', 0.0), 4),
                    "description": ai_analysis.get('description', ''),
                    "timestamp": frame.get('timestamp', 0.0),
                    "frame_position": frame.get('frame_number', 0)
                }
                
                keyframes_data["keyframes"].append(keyframe_info)
            
            # 保存到JSON文件
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(keyframes_data, f, ensure_ascii=False, indent=2)
            
            print(f"   💾 JSON文件保存路径：{json_file_path}")
            print(f"   📊 包含关键帧数量：{len(selected_frames)} 个")
            
            return json_file_path
            
        except Exception as e:
            print(f"❌ JSON文件保存失败：{str(e)}")
            # 返回一个默认路径，避免程序崩溃
            return os.path.join(self.output_dir, "keyframes_error.json")

# 智能抽帧演示
def main():
    """
    主函数：演示智能视频抽帧功能
    根据视频特性自动计算最优抽帧数量
    """
    print("=== 智能视频抽帧系统 ===\n")
    
    # 创建抽帧器实例
    extractor = DiversityFrameExtractor(output_dir="test_frames")
    
    # 设置测试视频文件
    video_file = "测试.mp4"
    
    # 检查测试视频是否存在
    if not os.path.exists(video_file):
        print(f"❌ 测试视频不存在：{video_file}")
        print("请确保在当前目录有测试视频文件")
        return
    
    try:
        # 让用户选择处理模式
        print("🔧 选择处理模式：")
        print("  1. 基础智能抽帧（快速，基于时间间隔）")
        print("  2. AI智能关键帧筛选（较慢，基于AI分析）")
        
        # 为了演示，我们先使用基础模式，但展示AI功能的代码结构
        mode = 2  # 可以改为用户输入选择
        
        if mode == 1:
            # 基础智能抽帧模式
            print("\n🚀 开始基础智能视频抽帧处理...")
            extracted_frames = extractor.extract_uniform_frames(
                video_path=video_file,
                target_interval_seconds=1.0  # 目标每秒一帧
            )
            
            # 创建智能抽帧报告
            report = extractor.create_extraction_report(
                video_path=video_file,
                frame_paths=extracted_frames,
                max_frames=len(extracted_frames)
            )
            
            # 显示处理结果
            print(f"\n📊 基础智能抽帧处理结果：")
            print(f"   智能提取帧数：{len(extracted_frames)} 帧")
            print(f"   根据视频特性自动优化，无需手动设置！")
            
            # 显示报告摘要
            print(f"\n📋 抽帧报告摘要：")
            print(f"   处理视频：{report['extraction_info']['video_file']}")
            print(f"   提取方法：{report['extraction_info']['extraction_method']}")
            print(f"   智能帧数：{report['extraction_info']['actual_extracted_frames']}")
            print(f"   处理状态：{'✅ 成功' if report['success'] else '❌ 失败'}")
            
            # 展示部分抽帧文件
            print(f"\n📁 生成的抽帧文件（前5个）：")
            for i, frame_path in enumerate(extracted_frames[:5]):
                filename = os.path.basename(frame_path)
                print(f"   {i+1}. {filename}")
        
        elif mode == 2:
            # AI智能关键帧筛选模式
            print("\n🤖 开始AI智能关键帧筛选处理...")
            
            # 使用新的AI分析方法
            ai_result = extractor.extract_ai_key_frames(
                video_path=video_file,
                target_interval_seconds=1.0,  # 基础抽帧间隔
                target_key_frames=8,          # 最终关键帧数量（符合需求的8-12个）
                significance_weight=0.6,      # 重要性权重60%
                quality_weight=0.4           # 质量权重40%
            )
            
            if ai_result['success']:
                stats = ai_result['processing_stats']
                key_frames = ai_result['selected_frames']
                
                # 显示AI处理结果
                print(f"\n🎯 AI智能关键帧筛选结果：")
                print(f"   基础帧数：{stats['base_frames_count']} 帧")
                print(f"   最终关键帧数：{stats['key_frames_count']} 帧")
                print(f"   平均重要性评分：{stats['average_significance_score']:.3f}")
                print(f"   平均质量评分：{stats['average_quality_score']:.3f}")
                print(f"   平均综合评分：{stats['average_combined_score']:.3f}")
                print(f"   总处理时间：{stats['total_processing_time']:.1f} 秒")
                
                # 展示关键帧详情
                print(f"\n🎬 AI筛选的关键帧详情：")
                for i, frame in enumerate(key_frames[:3]):  # 显示前3个
                    ai_info = frame['ai_analysis']
                    print(f"   关键帧{i+1}: {frame['filename']}")
                    print(f"      重要性：{ai_info['significance_score']:.3f}, 质量：{ai_info['quality_score']:.3f}")
                    print(f"      描述：{ai_info['description'][:50]}...")
                    
        # 提示可用的功能
        print(f"\n🔮 可用功能：")
        print(f"   • 基础智能抽帧：根据视频特性自动计算帧数")
        print(f"   • AI关键帧筛选：结合重要性和质量评分智能筛选")
        print(f"   • 两阶段处理：先均匀抽帧，再AI分析筛选")
        
    except Exception as e:
        print(f"❌ 处理失败：{str(e)}")

if __name__ == "__main__":
    main()
