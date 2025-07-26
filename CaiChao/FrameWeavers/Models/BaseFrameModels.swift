import Foundation

// MARK: - 基础帧提取请求模型
struct BaseFrameExtractionRequest: Codable {
    let taskId: String
    let interval: Double
    
    enum CodingKeys: String, CodingKey {
        case taskId = "task_id"
        case interval = "interval"
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
        self.thumbnailURL = URL(string: framePath)
    }
}

// MARK: - 基础帧提取状态
enum BaseFrameExtractionStatus: Equatable {
    case idle
    case extracting
    case completed([BaseFrameData])
    case failed(String)
    
    static func == (lhs: BaseFrameExtractionStatus, rhs: BaseFrameExtractionStatus) -> Bool {
        switch (lhs, rhs) {
        case (.idle, .idle):
            return true
        case (.extracting, .extracting):
            return true
        case (.completed(let lhsFrames), .completed(let rhsFrames)):
            return lhsFrames == rhsFrames
        case (.failed(let lhsError), .failed(let rhsError)):
            return lhsError == rhsError
        default:
            return false
        }
    }
}

// MARK: - 处理阶段枚举
enum ProcessingStage: String, CaseIterable {
    case upload = "视频上传"
    case baseFrameExtraction = "基础帧提取"
    case keyFrameExtraction = "关键帧提取"
    case storyGeneration = "故事生成"
    case styleProcessing = "风格处理"
    case comicGeneration = "连环画生成"
    case completed = "处理完成"
    
    var iconName: String {
        switch self {
        case .upload: return "arrow.up.circle"
        case .baseFrameExtraction: return "photo.on.rectangle"
        case .keyFrameExtraction: return "key.viewfinder"
        case .storyGeneration: return "book.closed"
        case .styleProcessing: return "paintbrush"
        case .comicGeneration: return "rectangle.stack"
        case .completed: return "checkmark.circle"
        }
    }
    
    var progressValue: Double {
        switch self {
        case .upload: return 0.14
        case .baseFrameExtraction: return 0.28
        case .keyFrameExtraction: return 0.42
        case .storyGeneration: return 0.57
        case .styleProcessing: return 0.71
        case .comicGeneration: return 0.85
        case .completed: return 1.0
        }
    }
}