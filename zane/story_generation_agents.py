"""
基于三阶段提示词的连环画故事生成系统
使用架构师、角色魂师、主编三个Agent来创作高质量的故事文本
"""

import json
import asyncio
import time
import re
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
from openai import OpenAI
from config import MOONSHOT_API_KEY, MOONSHOT_BASE_URL, MOONSHOT_MODEL, DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class KeyFrameData:
    """关键帧数据结构"""
    index: int
    filename: str
    photo_path: str
    combined_score: float
    significance_score: float
    quality_score: float
    description: str
    timestamp: float
    frame_position: int

@dataclass
class StoryResult:
    """故事生成结果数据结构"""
    task_id: str
    video_info: Dict[str, Any]
    overall_theme: str
    final_narrations: List[Dict[str, Any]]
    creation_time: str
    processing_stats: Dict[str, Any]

class LLMClient:
    """大语言模型客户端 - 使用Moonshot AI (Kimi)"""
    
    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        self.api_key = api_key or MOONSHOT_API_KEY
        self.base_url = base_url or MOONSHOT_BASE_URL
        self.model = model or MOONSHOT_MODEL
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    async def generate_text(self, prompt: str, max_tokens: int = None, temperature: float = None, system_prompt: str = None) -> str:
        """调用Moonshot AI生成文本"""
        try:
            max_tokens = max_tokens or DEFAULT_MAX_TOKENS
            temperature = temperature or DEFAULT_TEMPERATURE
            
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system", 
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            logger.info(f"正在调用Moonshot AI API，模型: {self.model}")
            
            # 异步调用API
            loop = asyncio.get_event_loop()
            completion = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            )
            
            response = completion.choices[0].message.content
            logger.info(f"Moonshot AI API调用成功，返回内容长度: {len(response)}")
            return response
            
        except Exception as e:
            logger.error(f"LLM API调用失败: {e}")
            raise e
    
    def extract_json_from_response(self, response: str) -> str:
        """从响应中提取JSON内容"""
        logger.debug(f"原始响应内容: {response[:200]}...")
        
        cleaned_response = response.strip()
        
        # 尝试找到JSON代码块
        json_match = re.search(r'```json\s*(.*?)\s*```', cleaned_response, re.DOTALL)
        if json_match:
            json_content = json_match.group(1).strip()
            logger.debug("找到JSON代码块")
            return json_content
        
        # 尝试直接解析整个响应
        try:
            json.loads(cleaned_response)
            logger.debug("整个响应就是有效的JSON")
            return cleaned_response
        except json.JSONDecodeError:
            pass
        
        # 尝试找到JSON对象
        obj_start = cleaned_response.find('{')
        if obj_start != -1:
            brace_count = 0
            for i, char in enumerate(cleaned_response[obj_start:], obj_start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        json_content = cleaned_response[obj_start:i+1]
                        try:
                            json.loads(json_content)
                            logger.debug("找到有效的JSON对象")
                            return json_content
                        except json.JSONDecodeError:
                            continue
        
        logger.warning("未能提取有效的JSON内容，返回原始响应")
        return cleaned_response

class ArchitectAgent:
    """架构师 (The Architect) - 分析关键帧并定义叙事功能"""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.name = "架构师"
    
    async def analyze_and_structure(self, keyframes: List[KeyFrameData]) -> Dict[str, Any]:
        """分析关键帧并输出故事蓝图"""
        logger.info(f"{self.name}: 开始分析关键帧并构建故事结构")
        
        # 构建关键帧描述
        frame_descriptions = []
        for frame in keyframes:
            frame_descriptions.append({
                "frame_index": frame.index - 1,  # 转换为0开始的索引
                "frame_path": frame.photo_path,
                "description": frame.description
            })
        
        system_prompt = """你是一位逻辑严谨的故事架构师。你的任务是分析一系列带有描述的关键帧，为每一个画面定义其在故事结构中的功能，并输出结构化的"故事蓝图"。"""
        
        prompt = f"""# 任务
1. **整体分析:** 通读所有帧的描述，提炼出故事的核心主题和情感基调。
2. **逐帧定义:** 为**每一个**输入的帧对象，撰写一句短语来定义其"叙事功能 (function)"，并将其作为该帧的`story_text`。
3. **保持结构:** 在输出中，必须完整保留每个对象的 `frame_index` 和 `frame_path`。

# 输入
keyframes_data: {json.dumps(frame_descriptions, ensure_ascii=False, indent=2)}

# 输出格式 (严格遵守此JSON结构)
{{
  "overall_theme": "一个关于在巨大压力下，亲情成为最后救赎的现代悲剧。",
  "architect_output": [
    {{
      "frame_index": 0,
      "frame_path": "/frames/video_abc/keyframe_01.jpg",
      "story_text": "引入危机：展现主角事业崩溃的瞬间。"
    }},
    {{
      "frame_index": 1,
      "frame_path": "/frames/video_abc/keyframe_02.jpg",
      "story_text": "情绪爆发：危机的直接后果，主角失控。"
    }}
  ]
}}"""
        
        response = await self.llm_client.generate_text(
            prompt, 
            max_tokens=2000, 
            temperature=0.7,
            system_prompt=system_prompt
        )
        
        try:
            json_content = self.llm_client.extract_json_from_response(response)
            result = json.loads(json_content)
            
            # 验证必要字段
            if "overall_theme" not in result:
                result["overall_theme"] = "一个关于生活中美好时刻的温馨故事"
            
            if "architect_output" not in result or not isinstance(result["architect_output"], list):
                result["architect_output"] = self._get_default_architect_output(keyframes)
            
            logger.info(f"{self.name}: 故事架构分析完成，主题：{result['overall_theme']}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"{self.name}: 解析架构结果失败 - {e}")
            return {
                "overall_theme": "一个关于生活中美好时刻的温馨故事",
                "architect_output": self._get_default_architect_output(keyframes)
            }
    
    def _get_default_architect_output(self, keyframes: List[KeyFrameData]) -> List[Dict[str, Any]]:
        """获取默认架构输出"""
        return [
            {
                "frame_index": frame.index - 1,
                "frame_path": frame.photo_path,
                "story_text": f"第{frame.index}个关键时刻：展现故事的重要节点。"
            }
            for frame in keyframes
        ]

class SoulWriterAgent:
    """角色魂师 (The Soul Writer) - 挖掘角色情感核心"""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.name = "角色魂师"
    
    async def analyze_emotions(self, keyframes: List[KeyFrameData], architect_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析角色情感并输出情感核心"""
        logger.info(f"{self.name}: 开始分析角色情感")
        
        # 构建初始关键帧数据
        initial_keyframes = []
        for frame in keyframes:
            initial_keyframes.append({
                "frame_index": frame.index - 1,
                "frame_path": frame.photo_path,
                "description": frame.description
            })
        
        system_prompt = """你是一位情感细腻的心理分析师和角色编剧。你专注于探索角色的内心世界。"""
        
        prompt = f"""# 任务
1. **综合理解:** 基于【原始画面描述】和【架构师的叙事功能】，深入理解每个画面的情境。
2. **挖掘情感:** 为**每一个**输入的帧，撰写一句深刻的"角色情感核心 (emotional core)"，并将其作为该帧的`story_text`。
3. **保持结构:** 在输出中，必须完整保留每个对象的 `frame_index` 和 `frame_path`。

# 输入
initial_keyframes: {json.dumps(initial_keyframes, ensure_ascii=False, indent=2)}

architect_data: {json.dumps(architect_data.get("architect_output", []), ensure_ascii=False, indent=2)}

# 指示
请将 `initial_keyframes` 和 `architect_data` 中 `frame_index` 相同的对象进行匹配分析，然后输出你的结果。

# 输出格式 (严格遵守此JSON结构)
{{
  "emotional_output": [
    {{
      "frame_index": 0,
      "frame_path": "/frames/video_abc/keyframe_01.jpg",
      "story_text": "压垮理智的最后一根稻草，世界在他眼前分崩离析。"
    }},
    {{
      "frame_index": 1,
      "frame_path": "/frames/video_abc/keyframe_02.jpg",
      "story_text": "无能为力的愤怒，将一切归咎于自己。"
    }}
  ]
}}"""
        
        response = await self.llm_client.generate_text(
            prompt, 
            max_tokens=2000, 
            temperature=0.8,
            system_prompt=system_prompt
        )
        
        try:
            json_content = self.llm_client.extract_json_from_response(response)
            result = json.loads(json_content)
            
            if "emotional_output" not in result or not isinstance(result["emotional_output"], list):
                result["emotional_output"] = self._get_default_emotional_output(keyframes)
            
            logger.info(f"{self.name}: 情感分析完成，共分析{len(result['emotional_output'])}个帧")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"{self.name}: 解析情感结果失败 - {e}")
            return {
                "emotional_output": self._get_default_emotional_output(keyframes)
            }
    
    def _get_default_emotional_output(self, keyframes: List[KeyFrameData]) -> List[Dict[str, Any]]:
        """获取默认情感输出"""
        return [
            {
                "frame_index": frame.index - 1,
                "frame_path": frame.photo_path,
                "story_text": f"第{frame.index}个情感时刻：内心深处的真实感受。"
            }
            for frame in keyframes
        ]

class MasterEditorAgent:
    """主编 (The Master Editor) - 创作最终旁白"""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.name = "主编"
    
    async def create_final_narrations(self, keyframes: List[KeyFrameData], architect_data: Dict[str, Any], emotional_data: Dict[str, Any]) -> Dict[str, Any]:
        """创作最终的故事旁白"""
        logger.info(f"{self.name}: 开始创作最终旁白")
        
        # 构建初始关键帧数据
        initial_keyframes = []
        for frame in keyframes:
            initial_keyframes.append({
                "frame_index": frame.index - 1,
                "frame_path": frame.photo_path,
                "description": frame.description
            })
        
        system_prompt = """你是一位荣获大奖的顶级剧本家和最终定稿人。你的任务是整合所有前期材料，创作出最终的、完美的旁白。"""
        
        prompt = f"""# 任务
1. **全面吸收:** 对每一个`frame_index`，综合分析其【原始描述】、【架构师的叙事功能】和【角色魂师的情感核心】。
2. **最终创作:** 基于以上所有信息，为**每一个**画面创作一句具有极高文学性和故事性的最终旁白，并将其作为该帧的`story_text`。
3. **保持结构:** 在输出中，必须完整保留每个对象的 `frame_index` 和 `frame_path`。

# 输入
initial_keyframes: {json.dumps(initial_keyframes, ensure_ascii=False, indent=2)}

architect_data: {json.dumps(architect_data.get("architect_output", []), ensure_ascii=False, indent=2)}

emotional_data: {json.dumps(emotional_data.get("emotional_output", []), ensure_ascii=False, indent=2)}

# 指示
请将三个输入数组中 `frame_index` 相同的对象进行匹配，作为创作每一帧旁白的完整上下文，然后输出最终定稿。

# 输出格式 (严格遵守此JSON结构，这将是模块的最终输出)
{{
  "final_narrations": [
    {{
      "frame_index": 0,
      "frame_path": "/frames/video_abc/keyframe_01.jpg",
      "story_text": "午夜十二点，数据是不会说谎的怪物。那条坠落的曲线，像一把尖刀，刺穿了他所有的幻想。"
    }},
    {{
      "frame_index": 1,
      "frame_path": "/frames/video_abc/keyframe_02.jpg",
      "story_text": "轰然起身的瞬间，失控的何止是那杯咖啡，更是他岌岌可危的人生。"
    }}
  ]
}}"""
        
        response = await self.llm_client.generate_text(
            prompt, 
            max_tokens=3000, 
            temperature=0.6,
            system_prompt=system_prompt
        )
        
        try:
            json_content = self.llm_client.extract_json_from_response(response)
            result = json.loads(json_content)
            
            if "final_narrations" not in result or not isinstance(result["final_narrations"], list):
                result["final_narrations"] = self._get_default_final_narrations(keyframes)
            
            logger.info(f"{self.name}: 最终旁白创作完成，共创作{len(result['final_narrations'])}个旁白")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"{self.name}: 解析最终结果失败 - {e}")
            return {
                "final_narrations": self._get_default_final_narrations(keyframes)
            }
    
    def _get_default_final_narrations(self, keyframes: List[KeyFrameData]) -> List[Dict[str, Any]]:
        """获取默认最终旁白"""
        return [
            {
                "frame_index": frame.index - 1,
                "frame_path": frame.photo_path,
                "story_text": f"这是第{frame.index}个美好的瞬间，时光在此刻定格，记录着生活中珍贵的回忆。"
            }
            for frame in keyframes
        ]

class StoryGenerationSystem:
    """三阶段故事生成系统"""
    
    def __init__(self, api_key: str = None, base_url: str = None, model: str = None, output_dir: str = "stories"):
        self.llm_client = LLMClient(api_key, base_url, model)
        self.architect_agent = ArchitectAgent(self.llm_client)
        self.soul_writer_agent = SoulWriterAgent(self.llm_client)
        self.master_editor_agent = MasterEditorAgent(self.llm_client)
        self.output_dir = output_dir
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def generate_story(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行完整的三阶段故事生成流程"""
        try:
            logger.info("开始三阶段故事生成流程")
            start_time = time.time()
            
            # 解析输入数据
            video_info = input_data["video_info"]
            keyframes_data = input_data["keyframes"]
            
            # 转换为KeyFrameData对象
            keyframes = [
                KeyFrameData(
                    index=kf["index"],
                    filename=kf["filename"],
                    photo_path=kf["photo_path"],
                    combined_score=kf["combined_score"],
                    significance_score=kf["significance_score"],
                    quality_score=kf["quality_score"],
                    description=kf["description"],
                    timestamp=kf["timestamp"],
                    frame_position=kf["frame_position"]
                )
                for kf in keyframes_data
            ]
            
            processing_stats = {
                "start_time": datetime.now().isoformat(),
                "architect_completed": False,
                "soul_writer_completed": False,
                "master_editor_completed": False,
                "errors": []
            }
            
            # 第一阶段：架构师分析
            logger.info("执行第一阶段：架构师分析")
            try:
                architect_result = await self.architect_agent.analyze_and_structure(keyframes)
                processing_stats["architect_completed"] = True
                processing_stats["architect_time"] = time.time() - start_time
            except Exception as e:
                error_msg = f"架构师分析失败: {e}"
                logger.error(error_msg)
                processing_stats["errors"].append(error_msg)
                architect_result = {
                    "overall_theme": "一个关于生活中美好时刻的温馨故事",
                    "architect_output": self.architect_agent._get_default_architect_output(keyframes)
                }
            
            # 第二阶段：角色魂师分析
            logger.info("执行第二阶段：角色魂师分析")
            try:
                emotional_result = await self.soul_writer_agent.analyze_emotions(keyframes, architect_result)
                processing_stats["soul_writer_completed"] = True
                processing_stats["soul_writer_time"] = time.time() - start_time
            except Exception as e:
                error_msg = f"角色魂师分析失败: {e}"
                logger.error(error_msg)
                processing_stats["errors"].append(error_msg)
                emotional_result = {
                    "emotional_output": self.soul_writer_agent._get_default_emotional_output(keyframes)
                }
            
            # 第三阶段：主编创作
            logger.info("执行第三阶段：主编创作")
            try:
                final_result = await self.master_editor_agent.create_final_narrations(keyframes, architect_result, emotional_result)
                processing_stats["master_editor_completed"] = True
                processing_stats["master_editor_time"] = time.time() - start_time
            except Exception as e:
                error_msg = f"主编创作失败: {e}"
                logger.error(error_msg)
                processing_stats["errors"].append(error_msg)
                final_result = {
                    "final_narrations": self.master_editor_agent._get_default_final_narrations(keyframes)
                }
            
            # 完成处理统计
            processing_stats["end_time"] = datetime.now().isoformat()
            processing_stats["total_time"] = time.time() - start_time
            processing_stats["success"] = len(processing_stats["errors"]) == 0
            
            # 构建最终结果
            story_result = StoryResult(
                task_id=video_info.get("task_id", str(int(time.time()))),
                video_info=video_info,
                overall_theme=architect_result.get("overall_theme", ""),
                final_narrations=final_result.get("final_narrations", []),
                creation_time=datetime.now().isoformat(),
                processing_stats=processing_stats
            )
            
            result = {
                "success": True,
                "task_id": story_result.task_id,
                "video_info": story_result.video_info,
                "overall_theme": story_result.overall_theme,
                "final_narrations": story_result.final_narrations,
                "creation_time": story_result.creation_time,
                "processing_stats": story_result.processing_stats,
                "intermediate_results": {
                    "architect_output": architect_result.get("architect_output", []),
                    "emotional_output": emotional_result.get("emotional_output", [])
                }
            }
            
            # 保存故事结果到文件
            json_file_path = self.save_story_to_json(result)
            result["json_file_path"] = json_file_path
            
            logger.info(f"三阶段故事生成完成，主题：{story_result.overall_theme}")
            return result
            
        except Exception as e:
            logger.error(f"故事生成流程失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "task_id": input_data.get("video_info", {}).get("task_id", "unknown")
            }
    
    def save_story_to_json(self, story_result: Dict[str, Any]) -> str:
        """
        保存故事生成结果到JSON文件
        
        Args:
            story_result: 故事生成结果字典
            
        Returns:
            str: 生成的JSON文件路径
        """
        try:
            # 生成JSON文件名（基于任务ID和视频名称）
            task_id = story_result.get("task_id", "unknown")
            video_info = story_result.get("video_info", {})
            video_name = video_info.get("video_name", "unknown_video")
            video_name_clean = os.path.splitext(video_name)[0]  # 去掉扩展名
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_filename = f"{video_name_clean}_story_{timestamp}.json"
            json_file_path = os.path.join(self.output_dir, json_filename)
            
            # 构建完整的JSON数据结构
            story_data = {
                "story_info": {
                    "task_id": task_id,
                    "video_name": video_name,
                    "video_path": video_info.get("video_path", ""),
                    "processing_time": story_result.get("creation_time", datetime.now().isoformat()),
                    "overall_theme": story_result.get("overall_theme", ""),
                    "total_narrations": len(story_result.get("final_narrations", []))
                },
                "final_narrations": story_result.get("final_narrations", []),
                "intermediate_results": story_result.get("intermediate_results", {}),
                "processing_stats": story_result.get("processing_stats", {}),
                "generation_metadata": {
                    "system_version": "1.0",
                    "agents_used": ["architect", "soul_writer", "master_editor"],
                    "export_time": datetime.now().isoformat()
                }
            }
            
            # 保存到JSON文件
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(story_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"故事结果已保存到：{json_file_path}")
            logger.info(f"包含旁白数量：{len(story_result.get('final_narrations', []))} 个")
            
            return json_file_path
            
        except Exception as e:
            logger.error(f"故事结果保存失败：{str(e)}")
            # 返回一个默认路径，避免程序崩溃
            return os.path.join(self.output_dir, "story_error.json")

# 便捷函数
async def generate_story_from_keyframes(input_data: Dict[str, Any], api_key: str = None, base_url: str = None, model: str = None, output_dir: str = "stories") -> Dict[str, Any]:
    """从关键帧数据生成故事的便捷函数"""
    system = StoryGenerationSystem(api_key, base_url, model, output_dir)
    return await system.generate_story(input_data)

if __name__ == "__main__":
    # 测试用例
    test_input = {
        "video_info": {
            "video_path": "测试视频3.mp4",
            "video_name": "测试视频3.mp4",
            "processing_time": "2025-07-25T23:00:47.899037",
            "total_keyframes": 2,
            "task_id": "test_task_001"
        },
        "keyframes": [
            {
                "index": 1,
                "filename": "base_frame_0001.jpg",
                "photo_path": "quick_start_frames\\base_frame_0001.jpg",
                "combined_score": 0.84,
                "significance_score": 0.8,
                "quality_score": 0.9,
                "description": "画面中，一名戴着黑框眼镜、穿着黑色皮夹克的女子正专注地看着手中的彩色卡片，似乎在思考下一步的动作。她的目光坚定，透露出一丝自信与专注。坐在她对面的是一位笑得合不拢嘴的年轻男子，他戴着白色耳机，穿着灰色连帽衫，显得非常开心和投入。他的双手自然地放在膝盖上，身体微微前倾，似乎正在享受这一刻的欢乐时光。两人身处一节现代化的高铁车厢内，背景中可以看到整齐排列的蓝色座椅和干净整洁的车厢环境。窗外的景色虽然模糊不清，但隐约能感受到列车行驶的速度与稳定。桌子上散落着更多的彩色卡片和其他物品，角落里还摆放着一些零食和药品包装盒。整个画面充满了温馨与愉悦的氛围，仿佛时间在此刻暂停，只为记录下这美好的一刻。",
                "timestamp": 0.0,
                "frame_position": 0
            },
            {
                "index": 2,
                "filename": "base_frame_0002.jpg",
                "photo_path": "quick_start_frames\\base_frame_0002.jpg",
                "combined_score": 0.84,
                "significance_score": 0.8,
                "quality_score": 0.9,
                "description": "在一辆现代高铁车厢内，一位年轻女子坐在蓝色座椅上，周围是舒适而整洁的环境。她穿着一件深色皮夹克，脸上带着浓重的笑意，甚至有些夸张的大笑使得她的眼睛几乎眯成了一条线，伴随着笑声，她用手轻拍着自己的脸颊，显得非常开心和放松。车厢内的光线柔和而均匀，投射在她的脸上形成柔和的高光，使得整个画面显得温馨和愉快。背景中还可以看到蓝白相间的座椅和广告海报，这些元素共同营造了一种轻松愉悦的旅途氛围。",
                "timestamp": 0.0,
                "frame_position": 0
            }
        ]
    }
    
    async def test():
        result = await generate_story_from_keyframes(test_input)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    #运行测试
    asyncio.run(test())