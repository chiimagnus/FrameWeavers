import requests
import base64
import json

def upload_to_github(image_path, github_token, repo_owner, repo_name, file_path):
    """上传图片到GitHub仓库并返回raw URL"""
    
    # 读取图片并转换为base64
    with open(image_path, "rb") as file:
        content = base64.b64encode(file.read()).decode()
    
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    
    data = {
        "message": f"Upload {file_path}",
        "content": content
    }
    
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.put(url, data=json.dumps(data), headers=headers)
    
    if response.status_code in [200, 201]:
        result = response.json()
        # 返回raw文件URL
        return f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/main/{file_path}"
    else:
        raise Exception(f"Upload failed: {response.text}")

# 使用示例（需要替换为你的GitHub信息）
# image_url = upload_to_github("unified_key_03.jpg", "your_token", "your_username", "your_repo", "images/unified_key_03.jpg")