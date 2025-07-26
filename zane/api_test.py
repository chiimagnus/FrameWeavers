#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
帧织者API接口测试脚本
测试所有API接口的功能和响应
"""

import requests
import json
import time
import os
import uuid
from typing import Dict, Any, Optional

class FrameWeaverAPITester:
    """帧织者API测试类"""
    
    def __init__(self, base_url: str = "http://localhost:5001"):
        """
        初始化测试器
        
        Args:
            base_url: API服务器基础URL
        """
        self.base_url = base_url
        self.device_id = f"test_device_{uuid.uuid4().hex[:8]}"
        self.current_task_id = None
        
    def log(self, message: str, level: str = "INFO"):
        """打印日志"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def get_error_message(self, response: Dict[str, Any]) -> str:
        """从响应中提取错误消息"""
        if response.get('data'):
            if isinstance(response['data'], dict):
                return response['data'].get('message', 'Unknown error')
            else:
                return str(response['data'])
        elif response.get('error'):
            return response['error']
        else:
            return 'Unknown error'
        
    def make_request(self, method: str, endpoint: str, timeout: int = 600, **kwargs) -> Dict[str, Any]:
        """
        发送HTTP请求
        
        Args:
            method: HTTP方法
            endpoint: API端点
            timeout: 请求超时时间（秒）
            **kwargs: 请求参数
            
        Returns:
            响应数据
        """
        url = f"{self.base_url}{endpoint}"
        
        # 设置默认超时时间
        if 'timeout' not in kwargs:
            kwargs['timeout'] = timeout
        
        try:
            response = requests.request(method, url, **kwargs)
            
            # 记录请求信息
            self.log(f"{method} {endpoint} - Status: {response.status_code}")
            
            # 尝试解析JSON响应
            try:
                return {
                    "status_code": response.status_code,
                    "data": response.json(),
                    "success": True
                }
            except json.JSONDecodeError:
                return {
                    "status_code": response.status_code,
                    "data": response.text,
                    "success": False,
                    "error": "Invalid JSON response"
                }
                
        except requests.exceptions.RequestException as e:
            self.log(f"Request failed: {str(e)}", "ERROR")
            return {
                "status_code": 0,
                "data": None,
                "success": False,
                "error": str(e)
            }
    
    def test_video_upload(self, video_files: list = None) -> Optional[str]:
        """
        测试视频上传API
        
        Args:
            video_files: 视频文件路径列表
            
        Returns:
            任务ID（如果成功）
        """
        self.log("=== 测试视频上传API ===")
        
        # 如果没有提供视频文件，使用测试视频
        if not video_files:
            test_video = "测试视频3.mp4"
            if os.path.exists(test_video):
                video_files = [test_video]
            else:
                self.log("未找到测试视频文件，跳过上传测试", "WARNING")
                return None
        
        # 准备文件
        files = []
        for video_file in video_files:
            if os.path.exists(video_file):
                files.append(('videos', open(video_file, 'rb')))
            else:
                self.log(f"视频文件不存在: {video_file}", "WARNING")
        
        if not files:
            self.log("没有可用的视频文件", "ERROR")
            return None
        
        # 发送请求
        data = {'device_id': self.device_id}
        response = self.make_request('POST', '/api/upload/videos', data=data, files=files)
        
        # 关闭文件
        for _, file_obj in files:
            file_obj.close()
        
        # 检查响应
        if response['success'] and response['status_code'] == 200:
            task_id = response['data'].get('task_id')
            self.current_task_id = task_id
            self.log(f"视频上传成功，任务ID: {task_id}")
            return task_id
        else:
            self.log(f"视频上传失败: {self.get_error_message(response)}", "ERROR")
            return None
    
    def test_task_status(self, task_id: str = None) -> Dict[str, Any]:
        """
        测试任务状态查询API
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务状态信息
        """
        self.log("=== 测试任务状态查询API ===")
        
        if not task_id:
            task_id = self.current_task_id
            
        if not task_id:
            self.log("没有可用的任务ID", "ERROR")
            return {}
        
        response = self.make_request('GET', f'/api/task/status/{task_id}')
        
        if response['success'] and response['status_code'] == 200:
            status_info = response['data']
            self.log(f"任务状态: {status_info.get('status')} - {status_info.get('message')}")
            self.log(f"进度: {status_info.get('progress', 0)}%")
            return status_info
        else:
            self.log(f"获取任务状态失败: {self.get_error_message(response)}", "ERROR")
            return {}
    
    def test_cancel_task(self, task_id: str = None) -> bool:
        """
        测试取消任务API
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功
        """
        self.log("=== 测试取消任务API ===")
        
        if not task_id:
            task_id = self.current_task_id
            
        if not task_id:
            self.log("没有可用的任务ID", "ERROR")
            return False
        
        response = self.make_request('POST', f'/api/task/cancel/{task_id}')
        
        if response['success'] and response['status_code'] == 200:
            self.log("任务取消成功")
            return True
        else:
            self.log(f"取消任务失败: {self.get_error_message(response)}", "ERROR")
            return False
    
    def test_device_tasks(self, device_id: str = None) -> list:
        """
        测试设备任务历史API
        
        Args:
            device_id: 设备ID
            
        Returns:
            任务列表
        """
        self.log("=== 测试设备任务历史API ===")
        
        if not device_id:
            device_id = self.device_id
        
        response = self.make_request('GET', f'/api/device/{device_id}/tasks')
        
        if response['success'] and response['status_code'] == 200:
            tasks = response['data'].get('tasks', [])
            self.log(f"设备 {device_id} 共有 {len(tasks)} 个任务")
            for task in tasks[:3]:  # 只显示前3个任务
                self.log(f"  - {task['task_id']}: {task['status']} ({task['file_count']} 文件)")
            return tasks
        else:
            self.log(f"获取设备任务历史失败: {self.get_error_message(response)}", "ERROR")
            return []
    
    def test_extract_base_frames(self, task_id: str = None, interval: float = 1.0) -> bool:
        """
        测试基础帧提取API
        
        Args:
            task_id: 任务ID
            interval: 抽帧间隔
            
        Returns:
            是否成功
        """
        self.log("=== 测试基础帧提取API ===")
        
        if not task_id:
            task_id = self.current_task_id
            
        if not task_id:
            self.log("没有可用的任务ID", "ERROR")
            return False
        
        data = {
            'task_id': task_id,
            'interval': interval
        }
        
        response = self.make_request('POST', '/api/extract/base-frames', data=data)
        
        if response['success'] and response['status_code'] == 200:
            results = response['data'].get('results', [])
            self.log(f"基础帧提取成功，处理了 {len(results)} 个视频")
            for result in results:
                self.log(f"  - {result['video_name']}: {result['base_frames_count']} 帧")
            return True
        else:
            self.log(f"基础帧提取失败: {self.get_error_message(response)}", "ERROR")
            return False
    
    def test_extract_key_frames(self, task_id: str = None, target_frames: int = 8) -> bool:
        """
        测试关键帧提取API
        
        Args:
            task_id: 任务ID
            target_frames: 目标关键帧数量
            
        Returns:
            是否成功
        """
        self.log("=== 测试关键帧提取API ===")
        
        if not task_id:
            task_id = self.current_task_id
            
        if not task_id:
            self.log("没有可用的任务ID", "ERROR")
            return False
        
        data = {
            'task_id': task_id,
            'target_frames': target_frames,
            'significance_weight': 0.6,
            'quality_weight': 0.4,
            'max_concurrent': 10  # 降低并发数以避免测试时的性能问题
        }
        
        response = self.make_request('POST', '/api/extract/key-frames', data=data)
        
        if response['success'] and response['status_code'] == 200:
            results = response['data'].get('results', [])
            self.log(f"关键帧提取成功，处理了 {len(results)} 个视频")
            for result in results:
                self.log(f"  - {result['video_name']}: {result['key_frames_count']} 关键帧")
            return True
        else:
            self.log(f"关键帧提取失败: {self.get_error_message(response)}", "ERROR")
            return False
    
    def test_unified_process(self, task_id: str = None, target_frames: int = 8) -> bool:
        """
        测试统一智能处理API
        
        Args:
            task_id: 任务ID
            target_frames: 目标关键帧数量
            
        Returns:
            是否成功
        """
        self.log("=== 测试统一智能处理API ===")
        
        if not task_id:
            task_id = self.current_task_id
            
        if not task_id:
            self.log("没有可用的任务ID", "ERROR")
            return False
        
        data = {
            'task_id': task_id,
            'target_frames': target_frames,
            'interval': 1.0,
            'significance_weight': 0.6,
            'quality_weight': 0.4,
            'max_concurrent': 10
        }
        
        response = self.make_request('POST', '/api/process/unified', data=data)
        
        if response['success'] and response['status_code'] == 200:
            results = response['data'].get('results', [])
            self.log(f"统一智能处理成功，处理了 {len(results)} 个视频")
            for result in results:
                if result.get('success', True):
                    self.log(f"  - {result['video_name']}: {result['key_frames_count']} 关键帧")
                    if 'processing_stats' in result:
                        stats = result['processing_stats']
                        self.log(f"    处理时间: {stats.get('total_processing_time', 0):.1f}秒")
                else:
                    self.log(f"  - {result['video_name']}: 处理失败 - {result.get('error', 'Unknown error')}")
            return True
        else:
            self.log(f"统一智能处理失败: {self.get_error_message(response)}", "ERROR")
            return False
    
    def test_get_story_styles(self) -> list:
        """
        测试获取文体风格列表API
        
        Returns:
            风格列表
        """
        self.log("=== 测试获取文体风格列表API ===")
        
        response = self.make_request('GET', '/api/story/styles')
        
        if response['success'] and response['status_code'] == 200:
            data = response['data']
            if data.get('success'):
                styles = data.get('styles', [])
                total_count = data.get('total_count', 0)
                
                self.log(f"成功获取文体风格列表，共 {total_count} 种风格")
                
                # 显示所有可用风格
                for i, style in enumerate(styles):
                    name = style.get('name', 'N/A')
                    description = style.get('description', 'N/A')
                    self.log(f"  {i+1}. {name}: {description}")
                
                return styles
            else:
                self.log(f"获取文体风格列表失败: {data.get('message', '未知错误')}", "ERROR")
                return []
        else:
            self.log(f"获取文体风格列表API调用失败: {self.get_error_message(response)}", "ERROR")
            return []
    
    def test_generate_story_with_style(self, keyframes_data: Dict[str, Any] = None, style: str = None) -> bool:
        """
        测试带有文体风格的故事生成API
        
        Args:
            keyframes_data: 关键帧数据
            style: 文体风格
            
        Returns:
            是否成功
        """
        self.log(f"=== 测试故事生成API（风格: {style or '默认'}）===")
        
        # 如果没有提供关键帧数据，尝试从JSON文件加载
        if not keyframes_data:
            keyframes_data = self._load_keyframes_from_json()
        
        # 如果仍然没有数据，使用示例数据
        if not keyframes_data:
            keyframes_data = {
                "video_info": {
                    "task_id": self.current_task_id or str(uuid.uuid4()),
                    "video_name": "测试视频.mp4",
                    "duration": 120.5,
                    "fps": 30
                },
                "keyframes": [
                    {
                        "index": 1,
                        "filename": "test_frame_01.jpg",
                        "photo_path": "/path/to/test_frame_01.jpg",
                        "combined_score": 0.85,
                        "significance_score": 0.85,
                        "quality_score": 0.92,
                        "description": "一个阳光明媚的早晨，主人公走出家门",
                        "timestamp": 0.0,
                        "frame_position": 0
                    },
                    {
                        "index": 2,
                        "filename": "test_frame_02.jpg",
                        "photo_path": "/path/to/test_frame_02.jpg",
                        "combined_score": 0.78,
                        "significance_score": 0.78,
                        "quality_score": 0.88,
                        "description": "主人公在公园里遇到了朋友",
                        "timestamp": 15.0,
                        "frame_position": 450
                    }
                ]
            }
        
        # 添加文体风格参数（如果提供）
        if style:
            keyframes_data['style'] = style
            self.log(f"使用文体风格: {style}")
        
        # 设置较长的超时时间，因为故事生成可能需要较长时间
        response = self.make_request('POST', '/api/generate/story', 
                                   json=keyframes_data,
                                   headers={'Content-Type': 'application/json'},
                                   timeout=620)  # 2分钟超时
        
        if response['success'] and response['status_code'] == 200:
            story_result = response['data'].get('story_result', {})
            if story_result.get('success'):
                self.log("故事生成成功！")
                self.log(f"主题: {story_result.get('overall_theme', 'N/A')}")
                
                final_narrations = story_result.get('final_narrations', [])
                self.log(f"生成了 {len(final_narrations)} 个旁白")
                
                # 显示前3个旁白
                for i, narration in enumerate(final_narrations[:3]):
                    self.log(f"旁白 {i+1}: {narration.get('story_text', 'N/A')[:100]}...")
                
                # 显示处理统计
                stats = story_result.get('processing_stats', {})
                self.log(f"处理时间: {stats.get('total_time', 0):.1f}秒")
                
                # 如果使用了风格，显示风格信息
                if style:
                    self.log(f"风格效果: 生成的故事应该体现 '{style}' 风格的特点")
                
                return True
            else:
                self.log(f"故事生成失败: {story_result.get('error', '未知错误')}", "ERROR")
                return False
        else:
            self.log(f"故事生成API调用失败: {self.get_error_message(response)}", "ERROR")
            return False

    def test_generate_story(self, keyframes_data: Dict[str, Any] = None) -> bool:
        """
        测试同步故事生成API（保持原有接口不变）
        
        Args:
            keyframes_data: 关键帧数据
            
        Returns:
            是否成功
        """
        return self.test_generate_story_with_style(keyframes_data, None)
    
    def test_multiple_story_styles(self) -> bool:
        """
        测试多种文体风格的故事生成
        
        Returns:
            是否全部成功
        """
        self.log("=== 测试多种文体风格的故事生成 ===")
        
        # 首先获取可用的文体风格列表
        available_styles = self.test_get_story_styles()
        
        if not available_styles:
            self.log("无法获取文体风格列表，跳过多风格测试", "WARNING")
            return False
        
        # 选择几种代表性风格进行测试
        test_styles = []
        
        # 从可用风格中选择几种进行测试
        style_names = [style.get('name') for style in available_styles if style.get('name')]
        
        # 选择最多3种风格进行测试，避免测试时间过长
        test_style_names = style_names[:3] if len(style_names) >= 3 else style_names
        
        # 添加一个自定义风格进行测试
        test_style_names.append("科幻冒险")
        
        success_count = 0
        total_tests = len(test_style_names)
        
        for style_name in test_style_names:
            self.log(f"\n--- 测试风格: {style_name} ---")
            
            if self.test_generate_story_with_style(style=style_name):
                success_count += 1
                self.log(f"✓ 风格 '{style_name}' 测试成功")
            else:
                self.log(f"✗ 风格 '{style_name}' 测试失败", "ERROR")
            
            # 在每次测试之间稍作等待，避免API负载过重
            time.sleep(2)
        
        self.log(f"\n多风格测试完成: {success_count}/{total_tests} 成功")
        return success_count == total_tests
    
    def _load_keyframes_from_json(self) -> Optional[Dict[str, Any]]:
        """从JSON文件加载关键帧数据"""
        try:
            # 查找关键帧JSON文件
            json_files = [f for f in os.listdir('quick_start_frames') if f.endswith('.json')]
            
            if not json_files:
                self.log("未找到关键帧JSON文件", "WARNING")
                return None
            
            # 使用最新的JSON文件
            json_file = sorted(json_files)[-1]
            json_path = os.path.join('quick_start_frames', json_file)
            
            self.log(f"加载关键帧数据: {json_path}")
            
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 确保数据结构正确
            if 'video_info' in data and 'keyframes' in data:
                # 添加task_id如果不存在
                if 'task_id' not in data['video_info']:
                    data['video_info']['task_id'] = self.current_task_id or str(uuid.uuid4())
                
                self.log(f"成功加载 {len(data['keyframes'])} 个关键帧")
                return data
            else:
                self.log("JSON文件格式不正确", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"加载关键帧数据失败: {e}", "ERROR")
            return None
    
    def test_style_transform(self, task_id: str = None, style_prompt: str = None) -> bool:
        """
        测试风格化处理API
        
        Args:
            task_id: 任务ID，如果为None则使用当前任务ID
            style_prompt: 风格化提示词，如果为None则使用默认值
            
        Returns:
            是否成功
        """
        self.log("=== 测试风格化处理API ===")
        
        # 使用提供的task_id或当前任务ID
        target_task_id = task_id or self.current_task_id
        
        if not target_task_id:
            self.log("没有可用的任务ID，无法测试风格化处理", "WARNING")
            return False
        
        # 构建请求数据
        request_data = {
            "task_id": target_task_id
        }
        
        # 添加可选参数
        if style_prompt:
            request_data["style_prompt"] = style_prompt
            
        # 添加图像尺寸（可选）
        # request_data["image_size"] = "1920x1024"
        
        # 可以添加特定的图像URL列表（用于测试特定图像）
        # request_data["image_urls"] = [
        #     {"url": "http://localhost:5001/api/frames/task_id/image1.jpg", "filename": "image1.jpg"}
        # ]
        
        self.log(f"风格化处理任务ID: {target_task_id}")
        if style_prompt:
            self.log(f"使用自定义风格提示词: {style_prompt}")
        else:
            self.log("使用默认风格提示词")
        
        # 发送风格化处理请求
        response = self.make_request(
            "POST",
            "/api/process/style-transform",
            json=request_data,
            timeout=600  # 风格化处理可能需要较长时间
        )
        
        if response["success"] and response["status_code"] == 200:
            data = response["data"]
            if data.get("success"):
                self.log("风格化处理成功！")
                
                # 显示处理结果统计
                processed_count = data.get("processed_count", 0)
                successful_count = data.get("successful_count", 0)
                failed_count = data.get("failed_count", 0)
                
                self.log(f"处理图像总数: {processed_count}")
                self.log(f"成功处理: {successful_count}")
                self.log(f"处理失败: {failed_count}")
                self.log(f"使用的风格提示词: {data.get('style_prompt', 'N/A')}")
                
                # 显示风格化结果详情
                style_results = data.get("style_results", [])
                success_results = [r for r in style_results if r.get("success")]
                failed_results = [r for r in style_results if not r.get("success")]
                
                # 显示成功的结果（最多3个）
                for i, result in enumerate(success_results[:3]):
                    original_filename = result.get('original_filename', 'N/A')
                    styled_filename = result.get('styled_filename', 'N/A')
                    self.log(f"✓ 图像 {i+1}: {original_filename} -> {styled_filename}")
                
                if len(success_results) > 3:
                    self.log(f"... 还有 {len(success_results) - 3} 个成功结果")
                
                # 显示失败的结果（最多2个）
                for i, result in enumerate(failed_results[:2]):
                    original_filename = result.get('original_filename', 'N/A')
                    error = result.get('error', 'N/A')
                    self.log(f"✗ 图像失败: {original_filename} - {error}", "WARNING")
                
                if len(failed_results) > 2:
                    self.log(f"... 还有 {len(failed_results) - 2} 个失败结果", "WARNING")
                
                return True
            else:
                self.log(f"风格化处理失败: {data.get('message', 'Unknown error')}", "ERROR")
                return False
        else:
            error_message = self.get_error_message(response)
            self.log(f"风格化处理API请求失败: {error_message}", "ERROR")
            return False

    
    def wait_for_task_completion(self, task_id: str, max_wait_time: int = 300) -> bool:
        """
        等待任务完成
        
        Args:
            task_id: 任务ID
            max_wait_time: 最大等待时间（秒）
            
        Returns:
            是否成功完成
        """
        self.log(f"等待任务 {task_id} 完成...")
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            status_info = self.test_task_status(task_id)
            
            if not status_info:
                time.sleep(2)
                continue
                
            status = status_info.get('status')
            
            if status in ['completed', 'base_frames_extracted', 'key_frames_extracted']:
                self.log(f"任务完成，状态: {status}")
                return True
            elif status == 'error':
                self.log(f"任务失败: {status_info.get('message', 'Unknown error')}", "ERROR")
                return False
            elif status == 'cancelled':
                self.log("任务已取消", "WARNING")
                return False
            else:
                time.sleep(2)
        
        self.log("等待任务完成超时", "WARNING")
        return False
    
    def run_full_test(self, video_files: list = None):
        """
        运行完整的API测试
        
        Args:
            video_files: 视频文件路径列表
        """
        self.log("开始完整API测试")
        self.log(f"测试设备ID: {self.device_id}")
        
        # 1. 测试视频上传
        task_id = self.test_video_upload(video_files)
        if not task_id:
            self.log("视频上传失败，终止测试", "ERROR")
            return
        
        # 2. 等待上传完成
        if not self.wait_for_task_completion(task_id, 60):
            self.log("等待上传完成超时", "ERROR")
            return
        
        # 3. 测试设备任务历史
        self.test_device_tasks()
        
        # 4. 测试统一智能处理
        if self.test_unified_process(task_id):
            # 等待处理完成
            if self.wait_for_task_completion(task_id, 300):
                self.log("统一智能处理完成")
                
                # 5. 测试风格化处理
                if self.test_style_transform(task_id):
                    self.log("风格化处理测试完成")
                
                # 6. 测试获取文体风格列表
                styles = self.test_get_story_styles()
                
                # 7. 测试故事生成（现在是同步的）
                if self.test_generate_story():
                    self.log("故事生成测试完成")
                    
                    # 8. 测试带风格的故事生成（选择一种风格测试）
                    if styles:
                        test_style = styles[0].get('name')  # 选择第一种风格
                        if test_style:
                            self.log(f"测试文体风格: {test_style}")
                            if self.test_generate_story_with_style(style=test_style):
                                self.log("文体风格故事生成测试完成")
        
        self.log("完整API测试结束")
    
    def run_basic_test(self):
        """运行基础API测试（不需要视频文件）"""
        self.log("开始基础API测试")
        
        # 测试不存在的任务
        self.test_task_status("non_existent_task")
        
        # 测试设备任务历史
        self.test_device_tasks()
        
        # 测试获取文体风格列表
        self.test_get_story_styles()
        
        # 测试故事生成（使用示例数据）
        self.test_generate_story()
        
        self.log("基础API测试结束")
    
    def run_style_test(self):
        """运行专门的文体风格测试"""
        self.log("开始文体风格专项测试")
        
        # 1. 测试获取文体风格列表API
        styles = self.test_get_story_styles()
        
        if not styles:
            self.log("无法获取文体风格列表，终止风格测试", "ERROR")
            return
        
        # 2. 测试默认故事生成（无风格）
        self.log("\n--- 测试默认故事生成（无风格参数）---")
        self.test_generate_story()
        
        # 3. 测试预定义风格的故事生成
        self.log("\n--- 测试预定义风格故事生成 ---")
        for i, style in enumerate(styles[:2]):  # 只测试前2种风格，避免测试时间过长
            style_name = style.get('name')
            if style_name:
                self.log(f"\n测试风格 {i+1}: {style_name}")
                self.test_generate_story_with_style(style=style_name)
                time.sleep(1)  # 短暂等待
        
        # 4. 测试自定义风格
        custom_styles = ["科幻悬疑", "温暖回忆", "动作冒险"]
        self.log("\n--- 测试自定义风格故事生成 ---")
        for style in custom_styles:
            self.log(f"\n测试自定义风格: {style}")
            self.test_generate_story_with_style(style=style)
            time.sleep(1)  # 短暂等待
        
        # 5. 测试风格参数验证（错误情况）
        self.log("\n--- 测试风格参数验证 ---")
        self.test_style_parameter_validation()
        
        self.log("文体风格专项测试结束")
    
    def test_style_parameter_validation(self):
        """测试风格参数验证"""
        self.log("测试风格参数验证...")
        
        # 构建基础数据
        basic_data = {
            "video_info": {
                "task_id": str(uuid.uuid4()),
                "video_name": "测试视频.mp4",
                "duration": 60.0,
                "fps": 30
            },
            "keyframes": [
                {
                    "index": 1,
                    "filename": "test_frame_01.jpg",
                    "photo_path": "/path/to/test_frame_01.jpg",
                    "combined_score": 0.85,
                    "significance_score": 0.85,
                    "quality_score": 0.92,
                    "description": "测试场景",
                    "timestamp": 0.0,
                    "frame_position": 0
                }
            ]
        }
        
        # 测试1: 风格参数为非字符串类型
        test_data = basic_data.copy()
        test_data['style'] = 123  # 数字而不是字符串
        
        response = self.make_request('POST', '/api/generate/story', 
                                   json=test_data,
                                   headers={'Content-Type': 'application/json'})
        
        if response['status_code'] == 400:
            self.log("✓ 正确拒绝了非字符串类型的风格参数")
        else:
            self.log("✗ 未能正确验证风格参数类型", "WARNING")
        
        # 测试2: 空字符串风格参数
        test_data = basic_data.copy()
        test_data['style'] = ""
        
        response = self.make_request('POST', '/api/generate/story', 
                                   json=test_data,
                                   headers={'Content-Type': 'application/json'})
        
        if response['status_code'] == 200:
            self.log("✓ 正确处理了空字符串风格参数")
        else:
            self.log("✗ 空字符串风格参数处理失败", "WARNING")


def main():
    """主函数"""
    print("帧织者API接口测试工具")
    print("=" * 50)
    
    # 创建测试器
    tester = FrameWeaverAPITester()
    
    # 检查是否有测试视频
    test_video = "测试视频3.mp4"
    
    if os.path.exists(test_video):
        print(f"找到测试视频: {test_video}")
        choice = input("选择测试模式:\n1. 完整测试（包含视频处理）\n2. 基础测试（仅API调用）\n3. 文体风格专项测试\n4. 多风格对比测试\n请输入选择 (1/2/3/4): ").strip()
        
        if choice == "1":
            tester.run_full_test([test_video])
        elif choice == "2":
            tester.run_basic_test()
        elif choice == "3":
            tester.run_style_test()
        elif choice == "4":
            tester.test_multiple_story_styles()
        else:
            print("无效选择，运行基础测试...")
            tester.run_basic_test()
    else:
        print(f"未找到测试视频文件: {test_video}")
        choice = input("选择测试模式:\n1. 基础测试（仅API调用）\n2. 文体风格专项测试\n3. 多风格对比测试\n请输入选择 (1/2/3): ").strip()
        
        if choice == "1":
            tester.run_basic_test()
        elif choice == "2":
            tester.run_style_test()
        elif choice == "3":
            tester.test_multiple_story_styles()
        else:
            print("无效选择，运行基础测试...")
            tester.run_basic_test()


def test_complete_comic_generation():
    """测试完整连环画生成接口"""
    print("\n" + "="*50)
    print("测试完整连环画生成接口")
    print("="*50)
    
    # 首先需要有一个已上传的任务
    print("1. 先上传一个测试视频...")
    
    # 使用现有的基础测试设置
    base_url = "http://localhost:5001"
    test_video_path = "测试视频3.mp4"
    
    if not os.path.exists(test_video_path):
        print("❌ 测试视频文件不存在，跳过连环画生成测试")
        return False
    
    # 上传视频
    try:
        with open(test_video_path, 'rb') as f:
            files = {'video': f}
            data = {'device_id': 'test_device'}
            response = requests.post(f'{base_url}/api/upload/videos', files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            task_id = result.get('task_id')
            print(f"✅ 获得任务ID: {task_id}")
        else:
            print("❌ 视频上传失败，跳过连环画生成测试")
            return False
    except Exception as e:
        print(f"❌ 上传视频时出错: {e}")
        return False
    
    # 等待上传完成
    print("2. 等待视频上传完成...")
    time.sleep(3)
    
    # 启动完整连环画生成
    print("3. 启动完整连环画生成...")
    comic_data = {
        'task_id': task_id,
        'target_frames': '6',  # 测试用较少帧数
        'frame_interval': '1.0',
        'significance_weight': '0.6',
        'quality_weight': '0.4',
        'style_prompt': '水彩画风格，温和色调',
        'story_style': '童话风格'
    }
    
    try:
        response = requests.post(f'{base_url}/api/process/complete-comic', data=comic_data)
        print(f"请求状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 连环画生成启动成功")
            print(f"   任务ID: {result.get('task_id')}")
            print(f"   状态: {result.get('status')}")
            print(f"   当前阶段: {result.get('stage')}")
            print(f"   进度: {result.get('progress')}%")
            
            # 简化的进度监控（避免长时间等待）
            print("\n4. 监控处理进度（简化版）...")
            
            # 等待一段时间后检查结果
            for i in range(5):  # 最多等待10秒
                time.sleep(2)
                status_response = requests.get(f'{base_url}/api/task/status/{task_id}')
                if status_response.status_code == 200:
                    status = status_response.json()
                    print(f"   进度: {status.get('progress', 0)}% - {status.get('stage', 'unknown')}")
                    
                    if status.get('status') == 'complete_comic_completed':
                        print("   ✅ 处理完成！")
                        break
                    elif status.get('status') == 'complete_comic_failed':
                        print(f"   ❌ 处理失败: {status.get('error', '未知错误')}")
                        return False
            
            print("✅ 连环画生成接口测试完成")
            return True
        else:
            print(f"❌ 启动失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_get_comic_result():
    """测试获取连环画结果接口"""
    print("\n" + "="*50)
    print("测试获取连环画结果接口")
    print("="*50)
    
    base_url = "http://localhost:5001"
    test_task_id = "test_task_id"
    
    try:
        response = requests.get(f'{base_url}/api/comic/result/{test_task_id}')
        print(f"请求状态码: {response.status_code}")
        
        if response.status_code == 404:
            print("✅ 正确返回404，任务不存在")
            return True
        elif response.status_code == 202:
            result = response.json()
            print("✅ 正确返回202，任务处理中")
            print(f"   状态: {result.get('status')}")
            print(f"   进度: {result.get('progress')}%")
            return True
        elif response.status_code == 200:
            result = response.json()
            print("✅ 成功获取连环画结果")
            return True
        else:
            print(f"⚠️ 意外的状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

if __name__ == "__main__":
    # 检查命令行参数
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "comic":
        # 仅测试连环画生成功能
        print("🎨 测试连环画生成功能")
        test_complete_comic_generation()
        test_get_comic_result()
    else:
        # 运行原有的主程序
        main()