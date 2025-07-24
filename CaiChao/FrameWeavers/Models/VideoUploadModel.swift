import Foundation
import UIKit

enum UploadStatus: String {
    case pending = "待上传"
    case uploading = "上传中"
    case processing = "处理中"
    case completed = "已完成"
    case failed = "失败"
}

// MARK: - 上传模式
enum UploadMode {
    case mock      // Mock模式，模拟上传
    case real      // 真实上传模式
}

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
    let task_id: String?
    let message: String?
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
