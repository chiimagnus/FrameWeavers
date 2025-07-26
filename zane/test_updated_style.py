"""
测试更新后的连环画风格化关键帧方法
验证使用在线图片URL的方式是否正常工作
"""

import os
import sys
import json
from PIL import Image

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入更新后的风格化函数
from app import style_transform_image, upload_to_imgbb

def test_upload_function():
    """测试图片上传功能"""
    print("=== 测试图片上传功能 ===")
    
    # 测试图片路径
    test_image = "unified_key_03.jpg"
    
    if not os.path.exists(test_image):
        print(f"❌ 测试图片不存在: {test_image}")
        return False
    
    try:
        # 测试上传
        print(f"上传测试图片: {test_image}")
        image_url = upload_to_imgbb(test_image)
        print(f"✅ 上传成功！URL: {image_url}")
        return True
        
    except Exception as e:
        print(f"❌ 上传失败: {str(e)}")
        return False

def test_style_transform():
    """测试完整的风格化流程"""
    print("\n=== 测试完整风格化流程 ===")
    
    # 测试图片路径
    test_image = "unified_key_03.jpg"
    
    if not os.path.exists(test_image):
        print(f"❌ 测试图片不存在: {test_image}")
        return False
    
    try:
        # 执行风格化
        print(f"开始风格化处理: {test_image}")
        result = style_transform_image(
            image_path=test_image,
            style_prompt="Convert to Ink and brushwork style, Chinese style, Yellowed and old, Low saturation, Low brightness",
            image_size="1780x1024"
        )
        
        # 检查结果
        if result['success']:
            print("✅ 风格化处理成功！")
            
            # 检查是否使用了降级处理
            if result.get('fallback_used'):
                print("⚠️  注意：使用了降级处理（返回原图）")
                if 'upload_error' in result:
                    print(f"   上传错误: {result['upload_error']}")
                if 'api_error' in result:
                    print(f"   API错误: {result['api_error']}")
                if 'download_error' in result:
                    print(f"   下载错误: {result['download_error']}")
            else:
                print("🎉 风格化完全成功！")
                print(f"   风格化图片URL: {result.get('styled_image_url', '未知')}")
                print(f"   上传图片URL: {result.get('uploaded_image_url', '未知')}")
            
            # 保存结果图片
            if 'image_data' in result and result['image_data']:
                output_path = "test_updated_style_result.jpg"
                with open(output_path, 'wb') as f:
                    f.write(result['image_data'])
                print(f"✅ 结果图片已保存: {output_path}")
                
                # 检查图片信息
                try:
                    with Image.open(output_path) as img:
                        print(f"   图片尺寸: {img.size}")
                        print(f"   图片模式: {img.mode}")
                except Exception as img_error:
                    print(f"⚠️  无法读取保存的图片: {img_error}")
            
            return True
        else:
            print(f"❌ 风格化处理失败: {result.get('error', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始测试更新后的连环画风格化方法")
    print("=" * 50)
    
    # 检查测试图片
    test_images = ["unified_key_03.jpg", "styled_unified_key_02.jpg"]
    available_image = None
    
    for img in test_images:
        if os.path.exists(img):
            available_image = img
            break
    
    if not available_image:
        print("❌ 没有找到可用的测试图片")
        print("请确保以下文件之一存在:")
        for img in test_images:
            print(f"  - {img}")
        return
    
    print(f"使用测试图片: {available_image}")
    
    # 更新测试图片路径
    global test_image
    import sys
    if 'test_upload_function' in globals():
        test_upload_function.__globals__['test_image'] = available_image
    if 'test_style_transform' in globals():
        test_style_transform.__globals__['test_image'] = available_image
    
    # 执行测试
    upload_success = test_upload_function()
    style_success = test_style_transform()
    
    # 输出总结
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print(f"📤 图片上传测试: {'✅ 通过' if upload_success else '❌ 失败'}")
    print(f"🎨 风格化测试: {'✅ 通过' if style_success else '❌ 失败'}")
    
    if upload_success and style_success:
        print("\n🎉 所有测试通过！更新后的风格化方法工作正常。")
    else:
        print("\n⚠️  存在测试失败，请检查错误信息。")

if __name__ == "__main__":
    main() 