import Foundation

enum UploadStatus: String {
    case pending = "待上传"
    case uploading = "上传中"
    case processing = "处理中"
    case completed = "已完成"
    case failed = "失败"
}

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
