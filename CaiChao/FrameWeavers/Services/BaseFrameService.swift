import Foundation
import Combine

// MARK: - 基础帧提取服务协议
protocol BaseFrameServiceProtocol {
    func extractBaseFrames(taskId: String, interval: Double) async throws -> BaseFrameExtractionResponse
    func getBaseFrames(taskId: String) async throws -> [BaseFrameData]
}

// MARK: - 基础帧提取服务实现
class BaseFrameService: BaseFrameServiceProtocol {
    private let baseURL: String
    
    init(baseURL: String = NetworkConfig.baseURL) {
        self.baseURL = baseURL
    }
    
    // MARK: - 提取基础帧
    func extractBaseFrames(taskId: String, interval: Double = 1.0) async throws -> BaseFrameExtractionResponse {
        // 参数验证
        guard !taskId.isEmpty else {
            throw BaseFrameError.invalidTaskId
        }
        
        guard interval > 0 && interval <= 10.0 else {
            throw BaseFrameError.invalidInterval
        }
        
        let endpoint = "/api/extract/base-frames"
        let urlString = baseURL + endpoint
        
        guard let url = URL(string: urlString) else {
            throw BaseFrameError.invalidURL
        }
        
        // 构建请求参数
        let parameters = [
            "task_id": taskId,
            "interval": String(interval)
        ]
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")
        
        // 编码参数
        let bodyString = parameters.map { "\($0.key)=\($0.value)" }.joined(separator: "&")
        request.httpBody = bodyString.data(using: .utf8)
        
        do {
            let (data, response) = try await URLSession.shared.data(for: request)
            
            // 检查HTTP响应
            guard let httpResponse = response as? HTTPURLResponse else {
                throw BaseFrameError.networkError("无效的响应")
            }
            
            guard (200...299).contains(httpResponse.statusCode) else {
                let errorMessage = "服务器错误: \(httpResponse.statusCode)"
                throw BaseFrameError.serverError(errorMessage)
            }
            
            // 解码响应
            let decoder = JSONDecoder()
            let responseData = try decoder.decode(BaseFrameExtractionResponse.self, from: data)
            
            guard responseData.success else {
                throw BaseFrameError.apiError(responseData.message)
            }
            
            return responseData
            
        } catch let error as BaseFrameError {
            throw error
        } catch {
            throw BaseFrameError.networkError(error.localizedDescription)
        }
    }
    
    // MARK: - 获取基础帧数据
    func getBaseFrames(taskId: String) async throws -> [BaseFrameData] {
        // 这里可以扩展为从服务器获取已提取的基础帧
        // 目前返回空数组，后续根据实际需求实现
        return []
    }
}

// MARK: - 错误类型定义
enum BaseFrameError: LocalizedError {
    case invalidTaskId
    case invalidInterval
    case invalidURL
    case networkError(String)
    case serverError(String)
    case apiError(String)
    
    var errorDescription: String? {
        switch self {
        case .invalidTaskId:
            return "任务ID不能为空"
        case .invalidInterval:
            return "时间间隔必须在0.1-10.0秒之间"
        case .invalidURL:
            return "无效的URL"
        case .networkError(let message):
            return "网络错误: \(message)"
        case .serverError(let message):
            return "服务器错误: \(message)"
        case .apiError(let message):
            return "API错误: \(message)"
        }
    }
    
    var recoverySuggestion: String? {
        switch self {
        case .invalidTaskId:
            return "请检查任务ID是否正确"
        case .invalidInterval:
            return "请设置0.1-10.0秒之间的时间间隔"
        case .invalidURL:
            return "请检查服务器地址配置"
        case .networkError:
            return "请检查网络连接后重试"
        case .serverError:
            return "服务器暂时不可用，请稍后重试"
        case .apiError:
            return "请检查参数是否正确"
        }
    }
}