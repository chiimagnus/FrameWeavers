# iOS mockdata

现在你是否能够基于 @frontend_design.mdc ，做出最简单的demo，只验证流程能跑通即可。由于目前并没有拿到http链接来调用后端大模型，因此就先弄成mockdata。

## 连环画生成模块请求示例

Request URL：https://your-backend-api.com/v1/comics/create
Request Method：POST
key            value
Content-Type   multipart/form-data; boundary=...

参数名 (Parameter Name)   类型 (Type)  是否必须  说明
videoFile                 File         是       用户从相册中选择的视频文件本体。后端需要根据这个参数名来接收文件流。
deviceId                  String       是       客户端设备的唯一标识符。在iOS上，可以通过 UIDevice.current.identifierForVendor?.uuidString 来获取。这个ID可以帮助后端将处理任务和结果与特定的设备关联起来，即使用户不登录也能找回自己的任务。

## 连环画生成模块API响应示例

{
  // 请求的总体状态信息
  "status": {
    "code": 200, // HTTP状态码, 200表示成功
    "message": "连环画生成成功"
  },

  // 连环画的元数据
  "metadata": {
    "comicId": "c-1689642000-a8d4b3f2", // 唯一的连环画ID，可用于后续分享或查找
    "deviceId":"fdgartyjjhdgsfghujhg",//客户端设备的唯一标识符
    "originalVideoTitle": "2025年海边夏日之旅.mp4", // 用户上传的原始视频文件名（可选）
    "creationDate": "2025-07-18T01:00:00Z", // 生成时间 (ISO 8601格式)
    "panelCount": 8 // 总画格数量
  },

  // 连环画的核心内容，是一个包含所有画格的数组
  "panels": [
    {
      "panelNumber": 1, // 画格序号，从1开始
      "imageUrl": "https://storage.googleapis.com/frame-weavers/c-1689642000-a8d4b3f2/panel_01.jpg", // 该画格处理后的图片URL
      "narration": "故事，从一片宁静的沙滩开始。", 
    },
    {
      "panelNumber": 2,
      "imageUrl": "https://storage.googleapis.com/frame-weavers/c-1689642000-a8d4b3f2/panel_02.jpg",
      "narration": "突然，一个小小的身影闯入了画面。",
    },
    {
      "panelNumber": 3,
      "imageUrl": "https://storage.googleapis.com/frame-weavers/c-1689642000-a8d4b3f2/panel_03.jpg",
      "narration": null,
    },
    {
      "panelNumber": 4,
      "imageUrl": "https://storage.googleapis.com/frame-weavers/c-1689642000-a8d4b3f2/panel_04.jpg",
      "narration": "一家人的笑声，比阳光还要灿烂。",
    }
    // ... 此处省略其余画格 ...
  ],

  // AI互动提问模块所需的问题列表
  "finalQuestions": [
    "你还记得那天沙子的温度吗？",
    "视频里谁的笑声最大？",
    "如果用一个词来形容那天的天空，会是什么？",
    "这个小城堡最后怎么样了？",
    "下次去海边，你最想和谁一起？"
  ]
}
