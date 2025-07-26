import requests
import json
from PIL import Image
from io import BytesIO

def upload_to_imgbb(image_path, api_key="7c9e1b2a3f4d5e6f7a8b9c0d1e2f3a4b"):
    """上传图片到imgbb并返回URL"""
    url = "https://api.imgbb.com/1/upload"
    
    with open(image_path, "rb") as file:
        files = {"image": file}
        data = {"key": api_key}
        response = requests.post(url, files=files, data=data)
        
    if response.status_code == 200:
        result = response.json()
        return result["data"]["url"]
    else:
        raise Exception(f"Upload failed: {response.text}")

# 上传本地图片获取URL
print("Uploading image...")
image_url = upload_to_imgbb("unified_key_03.jpg")
print(f"Image uploaded: {image_url}")

url = 'https://api-inference.modelscope.cn/v1/images/generations'

payload = {
    'model': 'black-forest-labs/FLUX.1-Kontext-dev',#ModelScope Model-Id,required
    'prompt': 'Convert to Ink and brushwork style, Chinese style, Yellowed and old, Low saturation, Low brightness',  # required
    'image_url': image_url,  # 使用上传后的图片URL
    'size': "1780x1024"
}
headers = {
    'Authorization': 'Bearer ms-a2eb2a0e-dded-42eb-b41c-835e3bd447b7',
    'Content-Type': 'application/json'
}

try:
    response = requests.post(url, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'), headers=headers)
    print(f"Response status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Error: {response.text}")
        exit(1)
    
    response_data = response.json()
    print("API response received successfully")
    
    image = Image.open(BytesIO(requests.get(response_data['images'][0]['url']).content))
    image.save('result_image.jpg')
    print("Image saved as result_image.jpg")
    
except FileNotFoundError:
    print("Error: unified_key_03.jpg file not found")
except Exception as e:
    print(f"Error: {e}")