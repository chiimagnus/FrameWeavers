import Foundation

// MARK: - 网络配置
struct NetworkConfig {
    // 基础URL配置
    static let baseURL = "https://api.example.com"  // 替换为实际的API地址
    
    // API端点
    enum Endpoint {
        case uploadVideo
        case uploadProgress(mediaId: String)
        case validateVideo
        
        var path: String {
            switch self {
            case .uploadVideo:
                return "/api/v1/media/upload"
            case .uploadProgress(let mediaId):
                return "/api/v1/media/upload/\(mediaId)/progress"
            case .validateVideo:
                return "/api/v1/media/validate"
            }
        }
        
        var url: URL {
            return URL(string: NetworkConfig.baseURL + path)!
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
