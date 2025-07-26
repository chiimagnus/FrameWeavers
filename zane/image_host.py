from flask import Flask, request, jsonify, send_from_directory, url_for
import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
import time

app = Flask(__name__)

# 配置
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(original_filename):
    """生成唯一的文件名"""
    ext = original_filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}_{int(time.time())}.{ext}"
    return unique_name

@app.route('/')
def index():
    """主页面，提供简单的上传界面"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>简易图床</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
            .upload-area { border: 2px dashed #ccc; padding: 40px; text-align: center; margin: 20px 0; }
            .upload-area:hover { border-color: #999; }
            input[type="file"] { margin: 10px 0; }
            button { background: #007cba; color: white; padding: 10px 20px; border: none; cursor: pointer; }
            button:hover { background: #005a87; }
            .result { margin: 20px 0; padding: 15px; background: #f0f0f0; border-radius: 5px; }
            .error { background: #ffe6e6; color: #d00; }
            .success { background: #e6ffe6; color: #060; }
        </style>
    </head>
    <body>
        <h1>简易图床工具</h1>
        <div class="upload-area">
            <form id="uploadForm" enctype="multipart/form-data">
                <p>选择图片文件上传</p>
                <input type="file" name="file" accept="image/*" required>
                <br>
                <button type="submit">上传图片</button>
            </form>
        </div>
        <div id="result"></div>
        
        <script>
            document.getElementById('uploadForm').onsubmit = function(e) {
                e.preventDefault();
                const formData = new FormData(this);
                const resultDiv = document.getElementById('result');
                
                resultDiv.innerHTML = '<p>上传中...</p>';
                
                fetch('/upload', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        resultDiv.innerHTML = `
                            <div class="result success">
                                <p><strong>上传成功！</strong></p>
                                <p>图片URL: <a href="${data.url}" target="_blank">${data.url}</a></p>
                                <p>文件名: ${data.filename}</p>
                                <img src="${data.url}" style="max-width: 300px; margin-top: 10px;">
                            </div>
                        `;
                    } else {
                        resultDiv.innerHTML = `<div class="result error"><p>上传失败: ${data.error}</p></div>`;
                    }
                })
                .catch(error => {
                    resultDiv.innerHTML = `<div class="result error"><p>上传失败: ${error}</p></div>`;
                });
            };
        </script>
    </body>
    </html>
    '''

@app.route('/upload', methods=['POST'])
def upload_file():
    """处理文件上传"""
    try:
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '没有选择文件'})
        
        file = request.files['file']
        
        # 检查文件名
        if file.filename == '':
            return jsonify({'success': False, 'error': '没有选择文件'})
        
        # 检查文件类型
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': '不支持的文件类型'})
        
        # 验证是否为有效图片
        try:
            img = Image.open(file.stream)
            img.verify()
            file.stream.seek(0)  # 重置文件指针
        except Exception:
            return jsonify({'success': False, 'error': '无效的图片文件'})
        
        # 生成唯一文件名
        filename = generate_unique_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # 保存文件
        file.save(filepath)
        
        # 生成访问URL
        file_url = url_for('uploaded_file', filename=filename, _external=True)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'url': file_url,
            'message': '上传成功'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """提供上传的文件访问"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/upload', methods=['POST'])
def api_upload():
    """API接口上传"""
    return upload_file()

@app.route('/health')
def health_check():
    """健康检查接口"""
    return jsonify({'status': 'ok', 'message': '图床服务运行正常'})

if __name__ == '__main__':
    print("简易图床服务启动中...")
    print("访问地址: http://localhost:5000")
    print("API接口: http://localhost:5000/api/upload")
    app.run(debug=True, host='0.0.0.0', port=5000)