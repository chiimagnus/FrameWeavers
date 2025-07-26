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
    
    def __init__(self, base_url: str = "http://localhost:5000"):
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
    
    def test_generate_story(self, keyframes_data: Dict[str, Any] = None) -> bool:
        """
        测试同步故事生成API
        
        Args:
            keyframes_data: 关键帧数据
            
        Returns:
            是否成功
        """
        self.log("=== 测试故事生成API ===")
        
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
                return True
            else:
                self.log(f"故事生成失败: {story_result.get('error', '未知错误')}", "ERROR")
                return False
        else:
            self.log(f"故事生成API调用失败: {self.get_error_message(response)}", "ERROR")
            return False
    
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
                
                # 5. 测试故事生成（现在是同步的）
                if self.test_generate_story():
                    self.log("故事生成测试完成")
        
        self.log("完整API测试结束")
    
    def run_basic_test(self):
        """运行基础API测试（不需要视频文件）"""
        self.log("开始基础API测试")
        
        # 测试不存在的任务
        self.test_task_status("non_existent_task")
        
        # 测试设备任务历史
        self.test_device_tasks()
        
        # 测试故事生成（使用示例数据）
        self.test_generate_story()
        
        self.log("基础API测试结束")


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
        choice = input("选择测试模式:\n1. 完整测试（包含视频处理）\n2. 基础测试（仅API调用）\n请输入选择 (1/2): ").strip()
        
        if choice == "1":
            tester.run_full_test([test_video])
        else:
            tester.run_basic_test()
    else:
        print(f"未找到测试视频文件: {test_video}")
        print("运行基础API测试...")
        tester.run_basic_test()


if __name__ == "__main__":
    main()