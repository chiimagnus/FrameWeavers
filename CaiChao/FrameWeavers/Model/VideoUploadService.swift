import Foundation
import UIKit

class VideoUploadService {
    static let shared = VideoUploadService()
    
    // 控制是否使用mock模式
    private let isMockMode: Bool = true
    
    private init() {}
    
    struct UploadResult {
        let success: Bool
        let url: String
        let key: String
        let etag: String?
        let size: Int64
        let isMock: Bool
        let error: String?
    }
    
    func uploadVideo(videoURL: URL, userId: String, progressHandler: @escaping (Double) -> Void, completion: @escaping (UploadResult) -> Void) {
        if isMockMode {
            uploadMockVideo(videoURL: videoURL, userId: userId, progressHandler: progressHandler, completion: completion)
        } else {
            uploadRealVideo(videoURL: videoURL, userId: userId, progressHandler: progressHandler, completion: completion)
        }
    }
    
    private func uploadMockVideo(videoURL: URL, userId: String, progressHandler: @escaping (Double) -> Void, completion: @escaping (UploadResult) -> Void) {
        // 模拟上传进度
        var progress: Double = 0
        let timer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { timer in
            progress += 0.05
            progressHandler(min(progress, 1.0))
            
            if progress >= 1.0 {
                timer.invalidate()
                
                // 生成mock数据
                let mockKey = "videos/\(DateFormatter().string(from: Date()))/mock_\(userId)_\(UUID().uuidString).mp4"
                let mockURL = "https://mock-cdn.example.com/\(mockKey)"
                let mockETag = UUID().uuidString
                
                let fileSize = getFileSize(url: videoURL)
                
                let result = UploadResult(
                    success: true,
                    url: mockURL,
                    key: mockKey,
                    etag: mockETag,
                    size: fileSize,
                    isMock: true,
                    error: nil
                )
                
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                    completion(result)
                }
            }
        }
        RunLoop.main.add(timer, forMode: .common)
    }
    
    private func uploadRealVideo(videoURL: URL, userId: String, progressHandler: @escaping (Double) -> Void, completion: @escaping (UploadResult) -> Void) {
        // 真实上传逻辑 - 这里需要替换为实际的上传API
        // 示例使用URLSession上传
        
        guard let uploadURL = URL(string: "https://your-api-endpoint.com/upload") else {
            let result = UploadResult(
                success: false,
                url: "",
                key: "",
                etag: nil,
                size: 0,
                isMock: false,
                error: "上传地址无效"
            )
            completion(result)
            return
        }
        
        var request = URLRequest(url: uploadURL)
        request.httpMethod = "POST"
        
        let boundary = UUID().uuidString
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        var body = Data()
        
        // 添加用户ID字段
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"user_id\"\r\n\r\n".data(using: .utf8)!)
        body.append("\(userId)\r\n".data(using: .utf8)!)
        
        // 添加视频文件
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"video\"; filename=\"\(videoURL.lastPathComponent)\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: video/mp4\r\n\r\n".data(using: .utf8)!)
        
        do {
            let videoData = try Data(contentsOf: videoURL)
            body.append(videoData)
            body.append("\r\n".data(using: .utf8)!)
            
            body.append("--\(boundary)--\r\n".data(using: .utf8)!)
            
            let session = URLSession(configuration: .default)
            let task = session.uploadTask(with: request, from: body) { data, response, error in
                DispatchQueue.main.async {
                    if let error = error {
                        let result = UploadResult(
                            success: false,
                            url: "",
                            key: "",
                            etag: nil,
                            size: 0,
                            isMock: false,
                            error: error.localizedDescription
                        )
                        completion(result)
                        return
                    }
                    
                    guard let httpResponse = response as? HTTPURLResponse,
                          httpResponse.statusCode == 200,
                          let data = data,
                          let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
                        let result = UploadResult(
                            success: false,
                            url: "",
                            key: "",
                            etag: nil,
                            size: 0,
                            isMock: false,
                            error: "上传失败"
                        )
                        completion(result)
                        return
                    }
                    
                    let result = UploadResult(
                        success: true,
                        url: json["url"] as? String ?? "",
                        key: json["key"] as? String ?? "",
                        etag: json["etag"] as? String,
                        size: json["size"] as? Int64 ?? 0,
                        isMock: false,
                        error: nil
                    )
                    completion(result)
                }
            }
            
            task.resume()
            
        } catch {
            let result = UploadResult(
                success: false,
                url: "",
                key: "",
                etag: nil,
                size: 0,
                isMock: false,
                error: error.localizedDescription
            )
            completion(result)
        }
    }
    
    private func getFileSize(url: URL) -> Int64 {
        do {
            let attributes = try FileManager.default.attributesOfItem(atPath: url.path)
            return attributes[.size] as? Int64 ?? 0
        } catch {
            return 0
        }
    }
} 