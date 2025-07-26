import requests
import os

def test_image_upload(image_path, server_url="http://localhost:5000"):
    """测试图片上传功能"""
    
    if not os.path.exists(image_path):
        print(f"错误: 图片文件 {image_path} 不存在")
        return None
    
    try:
        # 准备文件
        with open(image_path, 'rb') as f:
            files = {'file': f}
            
            # 发送上传请求
            response = requests.post(f"{server_url}/api/upload", files=files)
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    print("✅ 上传成功!")
                    print(f"文件名: {result['filename']}")
                    print(f"图片URL: {result['url']}")
                    return result['url']
                else:
                    print(f"❌ 上传失败: {result['error']}")
                    return None
            else:
                print(f"❌ 请求失败，状态码: {response.status_code}")
                return None
                
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败，请确保图床服务已启动")
        return None
    except Exception as e:
        print(f"❌ 上传出错: {str(e)}")
        return None

def test_health_check(server_url="http://localhost:5000"):
    """测试服务健康状态"""
    try:
        response = requests.get(f"{server_url}/health")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 服务状态: {result['message']}")
            return True
        else:
            print(f"❌ 服务异常，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== 图床服务测试 ===")
    
    # 健康检查
    print("\n1. 检查服务状态...")
    if not test_health_check():
        print("请先启动图床服务: python image_host.py")
        exit(1)
    
    # 测试上传
    print("\n2. 测试图片上传...")
    
    # 查找可用的测试图片
    test_images = [
        "result_image.jpg",
        "styled_unified_key_02.jpg", 
        "unified_key_03.jpg"
    ]
    
    uploaded_urls = []
    for img_path in test_images:
        if os.path.exists(img_path):
            print(f"\n测试上传: {img_path}")
            url = test_image_upload(img_path)
            if url:
                uploaded_urls.append(url)
            break
    else:
        print("没有找到测试图片文件")
        print("你可以手动指定图片路径进行测试:")
        print("python test_image_host.py")
    
    if uploaded_urls:
        print(f"\n✅ 测试完成，成功上传 {len(uploaded_urls)} 张图片")
        print("上传的图片URL:")
        for url in uploaded_urls:
            print(f"  - {url}")
    
    print("\n💡 使用说明:")
    print("1. 启动服务: python image_host.py")
    print("2. 浏览器访问: http://localhost:5000")
    print("3. API上传: POST http://localhost:5000/api/upload")