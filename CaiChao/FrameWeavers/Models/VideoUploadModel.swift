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
            // 修复Windows路径分隔符问题：将反斜杠替换为正斜杠
            let normalizedPath = framePath.replacingOccurrences(of: "\\", with: "/")
            let fullURL = "\(baseURL)/\(normalizedPath)"
            self.thumbnailURL = URL(string: fullURL)
            print("🔗 BaseFrameData: 原始路径: \(framePath)")
            print("🔗 BaseFrameData: 标准化路径: \(normalizedPath)")
            print("🔗 BaseFrameData: 完整URL: \(fullURL)")

            // 测试URL是否可访问
            if let url = self.thumbnailURL {
                Task {
                    do {
                        // 创建带有正确头部的请求
                        var request = URLRequest(url: url)
                        request.setValue("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1", forHTTPHeaderField: "User-Agent")
                        request.setValue("*/*", forHTTPHeaderField: "Accept")
                        request.setValue("gzip, deflate, br", forHTTPHeaderField: "Accept-Encoding")
                        request.setValue("keep-alive", forHTTPHeaderField: "Connection")

                        let (data, response) = try await URLSession.shared.data(for: request)
                        if let httpResponse = response as? HTTPURLResponse {
                            print("🌐 URL测试: \(fullURL) - 状态码: \(httpResponse.statusCode)")
                            print("📊 响应头: \(httpResponse.allHeaderFields)")
                            print("📦 数据大小: \(data.count) bytes")
                        }
                    } catch {
                        print("❌ URL测试失败: \(fullURL) - 错误: \(error.localizedDescription)")
                    }
                }
            }
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
        print("🌐 BaseFrameService: 请求URL: \(urlString)")

        guard let url = URL(string: urlString) else {
            print("❌ BaseFrameService: 无效的URL: \(urlString)")
            throw NSError(domain: "BaseFrameService", code: -1, userInfo: [NSLocalizedDescriptionKey: "无效的URL"])
        }

        let parameters = [
            "task_id": taskId,
            "interval": String(interval)
        ]
        print("📝 BaseFrameService: 请求参数: \(parameters)")

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")

        let bodyString = parameters.map { "\($0.key)=\($0.value)" }.joined(separator: "&")
        request.httpBody = bodyString.data(using: .utf8)
        print("📤 BaseFrameService: 请求体: \(bodyString)")

        let (data, response) = try await URLSession.shared.data(for: request)
        print("📥 BaseFrameService: 收到响应")

        guard let httpResponse = response as? HTTPURLResponse else {
            print("❌ BaseFrameService: 无效的HTTP响应")
            throw NSError(domain: "BaseFrameService", code: -2, userInfo: [NSLocalizedDescriptionKey: "无效的HTTP响应"])
        }

        print("📊 BaseFrameService: HTTP状态码: \(httpResponse.statusCode)")

        guard (200...299).contains(httpResponse.statusCode) else {
            print("❌ BaseFrameService: 服务器错误，状态码: \(httpResponse.statusCode)")
            if let responseString = String(data: data, encoding: .utf8) {
                print("📄 BaseFrameService: 错误响应内容: \(responseString)")
            }
            throw NSError(domain: "BaseFrameService", code: -2, userInfo: [NSLocalizedDescriptionKey: "服务器错误: \(httpResponse.statusCode)"])
        }

        if let responseString = String(data: data, encoding: .utf8) {
            print("📄 BaseFrameService: 响应内容: \(responseString)")
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
    let video_path: String?  // 新增：后端返回的视频路径
}

// MARK: - 任务状态查询响应
struct TaskStatusResponse: Codable {
    let success: Bool
    let task_id: String
    let status: String
    let message: String
    let progress: Int
    let stage: String?  // 添加stage字段
    let created_at: String

    // 移除files字段，因为可能导致解析错误
    enum CodingKeys: String, CodingKey {
        case success, task_id, status, message, progress, stage, created_at
    }
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

// MARK: - 完整连环画生成请求
struct CompleteComicRequest {
    let taskId: String
    let videoPath: String  // 必须：后端返回的视频路径
    let storyStyle: String  // 必须：故事风格关键词
    let targetFrames: Int
    let frameInterval: Double
    let significanceWeight: Double
    let qualityWeight: Double
    let stylePrompt: String
    let imageSize: String
    let maxConcurrent: Int

    init(taskId: String,
         videoPath: String,
         storyStyle: String = "温馨童话",  // 参考Python测试的默认值
         targetFrames: Int = 12,  // 参考Python测试
         frameInterval: Double = 2.0,  // 参考Python测试
         significanceWeight: Double = 0.7,  // 参考Python测试
         qualityWeight: Double = 0.3,  // 参考Python测试
         stylePrompt: String = "Convert to Ink and brushwork style, Chinese style, Yellowed and old, Low saturation, Low brightness",  // 参考Python测试
         imageSize: String = "1780x1024",  // 参考Python测试
         maxConcurrent: Int = 50) {
        self.taskId = taskId
        self.videoPath = videoPath
        self.storyStyle = storyStyle
        self.targetFrames = targetFrames
        self.frameInterval = frameInterval
        self.significanceWeight = significanceWeight
        self.qualityWeight = qualityWeight
        self.stylePrompt = stylePrompt
        self.imageSize = imageSize
        self.maxConcurrent = maxConcurrent
    }
}

// MARK: - 完整连环画生成响应
struct CompleteComicResponse: Codable {
    let success: Bool
    let message: String
    let taskId: String
    let status: String
    let progress: Int
    let stage: String

    enum CodingKeys: String, CodingKey {
        case success = "success"
        case message = "message"
        case taskId = "task_id"
        case status = "status"
        case progress = "progress"
        case stage = "stage"
    }
}

// MARK: - 连环画结果响应
struct ComicResultResponse: Codable {
    let success: Bool
    let message: String
    let taskId: String
    let results: ComicResults

    enum CodingKeys: String, CodingKey {
        case success = "success"
        case message = "message"
        case taskId = "task_id"
        case results = "results"
    }
}

struct ComicResults: Codable {
    let successfulComics: [SuccessfulComic]
    let totalProcessed: Int
    let successCount: Int
    let failureCount: Int

    enum CodingKeys: String, CodingKey {
        case successfulComics = "successful_comics"
        case totalProcessed = "total_processed"
        case successCount = "success_count"
        case failureCount = "failure_count"
    }
}

struct SuccessfulComic: Codable {
    let videoName: String
    let success: Bool
    let comicData: ComicData

    enum CodingKeys: String, CodingKey {
        case videoName = "video_name"
        case success = "success"
        case comicData = "comic_data"
    }
}

struct ComicData: Codable {
    let storyInfo: StoryInfo
    let pages: [ComicPage]
    let interactiveQuestions: [InteractiveQuestion]

    enum CodingKeys: String, CodingKey {
        case storyInfo = "story_info"
        case pages = "pages"
        case interactiveQuestions = "interactive_questions"
    }
}

struct StoryInfo: Codable {
    let overallTheme: String
    let title: String
    let summary: String
    let totalPages: Int
    let videoName: String
    let creationTime: String

    enum CodingKeys: String, CodingKey {
        case overallTheme = "overall_theme"
        case title = "title"
        case summary = "summary"
        case totalPages = "total_pages"
        case videoName = "video_name"
        case creationTime = "creation_time"
    }
}

struct ComicPage: Codable {
    let pageIndex: Int
    let storyText: String
    let originalFramePath: String
    let styledFramePath: String
    let styledFilename: String
    let frameIndex: Int
    let styleApplied: Bool

    enum CodingKeys: String, CodingKey {
        case pageIndex = "page_index"
        case storyText = "story_text"
        case originalFramePath = "original_frame_path"
        case styledFramePath = "styled_frame_path"
        case styledFilename = "styled_filename"
        case frameIndex = "frame_index"
        case styleApplied = "style_applied"
    }
}

struct InteractiveQuestion: Codable {
    let questionId: Int
    let question: String
    let intent: String?  // 新增：问题意图
    let questionType: String

    // 可选字段，因为后端可能不返回
    let options: [String]?
    let sceneDescription: String?

    enum CodingKeys: String, CodingKey {
        case questionId = "id"  // 修正：后端返回的是 "id" 而不是 "question_id"
        case question = "question"
        case intent = "intent"  // 新增：对应后端的 intent 字段
        case questionType = "type"  // 修正：后端返回的是 "type" 而不是 "question_type"
        case options = "options"
        case sceneDescription = "scene_description"
    }
}

// MARK: - 连环画结果（用于UI显示）
struct ComicResult: Codable {
    let comicId: String
    let deviceId: String
    let title: String  // 故事标题
    let originalVideoTitle: String  // 原始视频文件名
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
