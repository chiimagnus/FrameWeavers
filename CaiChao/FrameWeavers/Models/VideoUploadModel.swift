import Foundation
import UIKit

// MARK: - 基础帧数据模型
struct BaseFrameData: Identifiable, Hashable {
    let id = UUID()
    let framePath: String
    let frameIndex: Int
    let timestamp: Double
    let thumbnailURL: URL?

    init(framePath: String, frameIndex: Int, timestamp: Double) {
        self.framePath = framePath
        self.frameIndex = frameIndex
        self.timestamp = timestamp
        // 构建完整的图片URL
        if framePath.hasPrefix("http") {
            self.thumbnailURL = URL(string: framePath)
        } else {
            // 如果是相对路径，需要拼接服务器地址
            let baseURL = NetworkConfig.baseURL
            self.thumbnailURL = URL(string: "\(baseURL)/\(framePath)")
        }
    }
}

// MARK: - 基础帧提取响应模型
struct BaseFrameExtractionResponse: Codable {
    let success: Bool
    let message: String
    let taskId: String
    let results: [BaseFrameResult]

    enum CodingKeys: String, CodingKey {
        case success = "success"
        case message = "message"
        case taskId = "task_id"
        case results = "results"
    }
}

// MARK: - 基础帧结果详情
struct BaseFrameResult: Codable, Identifiable {
    let id = UUID()
    let videoName: String
    let baseFramesCount: Int
    let baseFramesPaths: [String]
    let outputDir: String

    enum CodingKeys: String, CodingKey {
        case videoName = "video_name"
        case baseFramesCount = "base_frames_count"
        case baseFramesPaths = "base_frames_paths"
        case outputDir = "output_dir"
    }
}

// MARK: - 基础帧服务
class BaseFrameService {
    private let baseURL: String

    init(baseURL: String = NetworkConfig.baseURL) {
        self.baseURL = baseURL
    }

    func extractBaseFrames(taskId: String, interval: Double = 1.0) async throws -> BaseFrameExtractionResponse {
        let endpoint = "/api/extract/base-frames"
        let urlString = baseURL + endpoint

        guard let url = URL(string: urlString) else {
            throw NSError(domain: "BaseFrameService", code: -1, userInfo: [NSLocalizedDescriptionKey: "无效的URL"])
        }

        let parameters = [
            "task_id": taskId,
            "interval": String(interval)
        ]

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")

        let bodyString = parameters.map { "\($0.key)=\($0.value)" }.joined(separator: "&")
        request.httpBody = bodyString.data(using: .utf8)

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw NSError(domain: "BaseFrameService", code: -2, userInfo: [NSLocalizedDescriptionKey: "服务器错误"])
        }

        let decoder = JSONDecoder()
        return try decoder.decode(BaseFrameExtractionResponse.self, from: data)
    }
}

enum UploadStatus: String {
    case pending = "待上传"
    case uploading = "上传中"
    case processing = "处理中"
    case completed = "已完成"
    case failed = "失败"
}

// UploadMode 枚举已删除，仅保留真实上传模式

// MARK: - 设备信息
struct DeviceInfo: Codable {
    let model: String
    let osVersion: String
    let appVersion: String
}

// MARK: - 视频元数据
struct VideoMetadata: Codable {
    let originalFilename: String
    let fileSize: Int64
    let duration: Double
    let mimeType: String
    let mediaType: String
    let deviceId: String
    let deviceInfo: DeviceInfo
    let uploadedAt: String
}

// // MARK: - 上传请求
// struct VideoUploadRequest {
//     let videoURL: URL
//     let metadata: VideoMetadata
// }

// MARK: - 真实API响应模型
struct RealUploadResponse: Codable {
    let success: Bool
    let message: String
    let task_id: String?
    let uploaded_files: Int?
    let invalid_files: [String]?
}

// MARK: - 任务状态查询响应
struct TaskStatusResponse: Codable {
    let success: Bool
    let task_id: String
    let status: String
    let message: String
    let progress: Int
    let files: [String]?
    let created_at: String
}

// MARK: - 任务取消响应
struct TaskCancelResponse: Codable {
    let success: Bool
    let message: String
}

// MARK: - Mock API响应模型（保持兼容）
struct UploadResponse: Codable {
    let success: Bool
    let data: UploadData?
    let error: APIError?
    let message: String?
}

struct UploadData: Codable {
    let mediaId: String
    let mediaType: String
    let uploadStatus: String
    let processingEstimate: String?
    let fileInfo: FileInfo
    let deviceId: String
    let uploadedAt: String
}

struct FileInfo: Codable {
    let originalFilename: String
    let fileSize: Int64
    let duration: Double
    let format: String
}

// MARK: - 多视频上传请求
struct MultiVideoUploadRequest {
    let videoURLs: [URL]
    let deviceId: String
}

struct APIError: Codable {
    let code: String
    let message: String
    let details: [String: String]?  // 简化为 String 类型
}

// MARK: - 上传进度
struct UploadProgress {
    let percentage: Double
    let uploadedBytes: Int64
    let totalBytes: Int64
    let speed: String?
    let estimatedTimeRemaining: String?
}

// MARK: - 连环画结果
struct ComicResult: Codable {
    let comicId: String
    let deviceId: String
    let originalVideoTitle: String
    let creationDate: String
    let panelCount: Int
    let panels: [ComicPanel]
    let finalQuestions: [String]
}

struct ComicPanel: Codable, Identifiable {
    let id = UUID()
    let panelNumber: Int
    let imageUrl: String
    let narration: String?

    enum CodingKeys: String, CodingKey {
        case panelNumber, imageUrl, narration
    }
}

// MARK: - 设备ID生成器
class DeviceIDGenerator {
    static func generateDeviceID() -> String {
        let deviceModel = UIDevice.current.model.replacingOccurrences(of: " ", with: "_")
        let idfv = UIDevice.current.identifierForVendor?.uuidString.prefix(12) ?? "UNKNOWN"
        return "\(deviceModel)_\(idfv)"
    }

    static func getDeviceInfo() -> DeviceInfo {
        return DeviceInfo(
            model: UIDevice.current.model,
            osVersion: UIDevice.current.systemVersion,
            appVersion: Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "1.0.0"
        )
    }
}
