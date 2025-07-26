import Foundation

// MARK: - 网络配置
struct NetworkConfig {
    // 基础URL配置 - 根据运行环境自动选择
    static let baseURL: String = {
        #if targetEnvironment(simulator)
        return "https://e8065295b2fd.ngrok-free.app"
        #else
        return "https://e8065295b2fd.ngrok-free.app"
        #endif
    }()

    // API端点
    enum Endpoint {
        case uploadVideos           // 上传视频
        case taskStatus(taskId: String)  // 查询任务状态
        case taskCancel(taskId: String)  // 取消任务
        case completeComic          // 完整连环画生成
        case comicResult(taskId: String)  // 获取连环画结果

        var path: String {
            switch self {
            case .uploadVideos:
                return "/api/upload/videos"
            case .taskStatus(let taskId):
                return "/api/task/status/\(taskId)"
            case .taskCancel(let taskId):
                return "/api/task/cancel/\(taskId)"
            case .completeComic:
                return "/api/process/complete-comic"
            case .comicResult(let taskId):
                return "/api/comic/result/\(taskId)"
            }
        }

        var url: URL {
            guard let url = URL(string: NetworkConfig.baseURL + path) else {
                fatalError("无效的URL: \(NetworkConfig.baseURL + path)")
            }
            return url
        }
    }
    
    // HTTP方法
    enum HTTPMethod: String {
        case GET = "GET"
        case POST = "POST"
        case PUT = "PUT"
        case DELETE = "DELETE"
    }
    
    // 请求头
    static func defaultHeaders() -> [String: String] {
        return [
            "Content-Type": "multipart/form-data",
            "X-Device-ID": DeviceIDGenerator.generateDeviceID(),
            "User-Agent": "FrameWeavers/1.0.0 iOS"
        ]
    }
    
    // 超时配置
    static let timeoutInterval: TimeInterval = 60.0
    static let uploadTimeoutInterval: TimeInterval = 300.0  // 5分钟上传超时
}

// MARK: - 网络错误
enum NetworkError: Error, LocalizedError {
    case invalidURL
    case noData
    case decodingError(Error)
    case httpError(Int, String?)
    case uploadFailed(String)
    case timeout
    case noInternetConnection
    case unknown(Error)
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "无效的URL"
        case .noData:
            return "没有收到数据"
        case .decodingError(let error):
            return "数据解析失败: \(error.localizedDescription)"
        case .httpError(let code, let message):
            return "HTTP错误 \(code): \(message ?? "未知错误")"
        case .uploadFailed(let message):
            return "上传失败: \(message)"
        case .timeout:
            return "请求超时"
        case .noInternetConnection:
            return "网络连接不可用"
        case .unknown(let error):
            return "未知错误: \(error.localizedDescription)"
        }
    }
}
