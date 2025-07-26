"""
测试更保守的风格化方法
使用更温和的提示词来保持更多原图特征
"""

import os
import sys
from PIL import Image

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入风格化函数
from app import style_transform_image

def test_conservative_styles():
    """测试不同强度的风格化效果"""
    
    test_image = "unified_key_03.jpg"
    
    if not os.path.exists(test_image):
        print(f"❌ 测试图片不存在: {test_image}")
        return
    
    # 不同强度的风格提示词
    style_tests = [
        {
            "name": "轻微水墨风格",
            "prompt": "Add subtle ink wash painting style, keep original composition and details",
            "output": "conservative_style_1.jpg"
        },
        {
            "name": "保持人物的水墨效果", 
            "prompt": "Transform to Chinese ink painting style while preserving character features and facial details",
            "output": "conservative_style_2.jpg"
        },
        {
            "name": "仅改变背景风格",
            "prompt": "Keep the main subject unchanged, only transform background to Chinese traditional painting style",
            "output": "conservative_style_3.jpg"
        },
        {
            "name": "温和的复古效果",
            "prompt": "Add gentle vintage effect with slightly lower saturation, keep all original details",
            "output": "conservative_style_4.jpg"
        }
    ]
    
    print("🎨 开始测试不同强度的风格化效果...")
    print("=" * 60)
    
    for i, test in enumerate(style_tests, 1):
        print(f"\n📝 测试 {i}: {test['name']}")
        print(f"   提示词: {test['prompt']}")
        
        try:
            result = style_transform_image(
                image_path=test_image,
                style_prompt=test['prompt'],
                image_size="1344x768"  # 使用测试成功的尺寸
            )
            
            if result['success']:
                if result.get('fallback_used'):
                    print(f"   ⚠️  使用了降级处理（返回原图）")
                else:
                    print(f"   ✅ 风格化成功")
                
                # 保存结果
                if 'image_data' in result and result['image_data']:
                    with open(test['output'], 'wb') as f:
                        f.write(result['image_data'])
                    print(f"   💾 结果已保存: {test['output']}")
                    
                    # 检查图片信息
                    with Image.open(test['output']) as img:
                        print(f"   📏 图片尺寸: {img.size}")
            else:
                print(f"   ❌ 风格化失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            print(f"   ❌ 测试异常: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎯 建议:")
    print("1. 使用更具体的指令，如'保持人物特征'、'仅改变背景'")
    print("2. 避免过强的风格词汇，如'Convert to'，改用'Add subtle'")
    print("3. 可以指定保持哪些元素不变")
    print("4. 尝试分步骤进行小幅度的风格调整")

if __name__ == "__main__":
    test_conservative_styles() 