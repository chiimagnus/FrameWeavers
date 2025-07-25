import requests
import os

class VideoUploaderTest:
    def __init__(self):
        self.task_id = None

    def record_test_result(self, name, success, message, response=None):
        """一个简单的记录结果的方法，直接打印到控制台"""
        print(f"--- 测试名称: {name} ---")
        print(f"是否成功: {'是' if success else '否'}")
        print(f"信息: {message}")
        if response is not None:
            print(f"服务器响应状态码: {response.status_code}")
            try:
                print(f"服务器响应内容: {response.json()}")
            except ValueError:
                print(f"服务器响应内容: {response.text}")
        print("-" * 20)

    def test_upload_video(self, video_path):
        """测试上传视频"""
        # 引入必要的库
        import requests
        import os
        
        try:
            with open(video_path, 'rb') as video_file:
                # 注意这里的文件名应该是 video_file.name, 但为了简单我们直接用 basename
                files = {'videos': (os.path.basename(video_path), video_file, 'video/mp4')}
                data = {'device_id': "test_723788293"}
                
                response = requests.post(
                    "https://video-api.zeabur.app/api/upload/videos",
                    files=files,
                    data=data
                )
                
                if response.status_code == 200 and response.json().get('success'):
                    self.task_id = response.json().get('task_id')
                    self.record_test_result(
                        "上传视频",
                        True,
                        f"成功上传视频，获取任务ID: {self.task_id}",
                        response
                    )
                else:
                    self.record_test_result(
                        "上传视频",
                        False,
                        "上传视频失败",
                        response
                    )
        except Exception as e:
            self.record_test_result(
                "上传视频",
                False,
                f"发生异常: {str(e)}"
            )

if __name__ == "__main__":
    # 1. 创建一个测试类的实例
    tester = VideoUploaderTest()
    # 2. 通过这个实例来调用测试方法
    tester.test_upload_video(r"/Users/chii_magnus/Downloads/v0269cg10004d137hvvog65hjnl2qdng.MP4")