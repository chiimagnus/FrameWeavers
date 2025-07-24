import Foundation
import PhotosUI
import AVFoundation
import Combine

class VideoUploadViewModel: ObservableObject {
    @Published var selectedVideos: [URL] = []  // 支持多视频
    @Published var uploadStatus: UploadStatus = .pending
    @Published var uploadProgress: Double = 0
    @Published var errorMessage: String?
    @Published var comicResult: ComicResult?
    @Published var isShowingPicker = false
    @Published var uploadMode: UploadMode = .mock

    private var cancellables = Set<AnyCancellable>()
    private var uploadTask: URLSessionUploadTask?

    // 兼容性属性，返回第一个选中的视频
    var selectedVideo: URL? {
        return selectedVideos.first
    }
    
    func selectVideo(_ url: URL) {
        selectedVideos = [url]  // 单视频选择
        validateVideos()
    }

    func selectVideos(_ urls: [URL]) {
        selectedVideos = urls  // 多视频选择
        validateVideos()
    }

    func addVideo(_ url: URL) {
        selectedVideos.append(url)
        validateVideos()
    }

    func removeVideo(at index: Int) {
        guard index < selectedVideos.count else { return }
        selectedVideos.remove(at: index)
        validateVideos()
    }

    private func validateVideos() {
        guard !selectedVideos.isEmpty else {
            errorMessage = nil
            uploadStatus = .pending
            return
        }

        // 验证每个视频
        for (index, url) in selectedVideos.enumerated() {
            let asset = AVAsset(url: url)
            let duration = asset.duration.seconds

            if duration > 300 { // 5分钟
                errorMessage = "视频\(index + 1)时长超过5分钟"
                uploadStatus = .failed
                return
            }
        }

        errorMessage = nil
        uploadStatus = .pending
    }
    
    func uploadVideo() {
        guard !selectedVideos.isEmpty else { return }

        uploadStatus = .uploading
        uploadProgress = 0
        errorMessage = nil

        if uploadMode == .mock {
            uploadVideoMock(videoURL: selectedVideos.first!)  // Mock模式只用第一个视频
        } else {
            uploadVideosReal(videoURLs: selectedVideos)  // 真实模式支持多视频
        }
    }

    // MARK: - Mock上传
    private func uploadVideoMock(videoURL: URL) {
        // 先清理之前的cancellables
        cancellables.removeAll()

        // 模拟上传过程
        Timer.publish(every: 0.1, on: .main, in: .common)
            .autoconnect()
            .sink { [weak self] _ in
                guard let self = self else { return }

                self.uploadProgress += 0.05

                if self.uploadProgress >= 1.0 {
                    // 立即取消Timer
                    self.cancellables.removeAll()
                    self.uploadStatus = .processing
                    self.simulateProcessing()
                }
            }
            .store(in: &cancellables)
    }

    // MARK: - 真实HTTP上传（支持多视频）
    private func uploadVideosReal(videoURLs: [URL]) {
        let url = NetworkConfig.Endpoint.uploadVideos.url

        // 创建multipart/form-data请求
        var request = URLRequest(url: url)
        request.httpMethod = "POST"

        let boundary = "Boundary-\(UUID().uuidString)"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")

        do {
            let httpBody = try createMultipartBody(videoURLs: videoURLs, boundary: boundary)

            let session = URLSession.shared
            uploadTask = session.uploadTask(with: request, from: httpBody) { [weak self] data, response, error in
                DispatchQueue.main.async {
                    self?.handleRealUploadResponse(data: data, response: response, error: error)
                }
            }

            uploadTask?.resume()

        } catch {
            errorMessage = "创建上传请求失败: \(error.localizedDescription)"
            uploadStatus = .failed
        }
    }

    private func createMultipartBody(videoURLs: [URL], boundary: String) throws -> Data {
        var body = Data()

        // 添加device_id字段
        let deviceId = DeviceIDGenerator.generateDeviceID()
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"device_id\"\r\n\r\n".data(using: .utf8)!)
        body.append("\(deviceId)\r\n".data(using: .utf8)!)

        // 添加多个视频文件
        for videoURL in videoURLs {
            body.append("--\(boundary)\r\n".data(using: .utf8)!)
            body.append("Content-Disposition: form-data; name=\"videos\"; filename=\"\(videoURL.lastPathComponent)\"\r\n".data(using: .utf8)!)
            body.append("Content-Type: video/mp4\r\n\r\n".data(using: .utf8)!)

            let videoData = try Data(contentsOf: videoURL)
            body.append(videoData)
            body.append("\r\n".data(using: .utf8)!)
        }

        // 结束边界
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)

        return body
    }

    private func handleRealUploadResponse(data: Data?, response: URLResponse?, error: Error?) {
        if let error = error {
            errorMessage = "上传失败: \(error.localizedDescription)"
            uploadStatus = .failed
            return
        }

        guard let httpResponse = response as? HTTPURLResponse else {
            errorMessage = "无效的服务器响应"
            uploadStatus = .failed
            return
        }

        guard let data = data else {
            errorMessage = "没有收到响应数据"
            uploadStatus = .failed
            return
        }

        if httpResponse.statusCode == 200 {
            do {
                let response = try JSONDecoder().decode(RealUploadResponse.self, from: data)
                if response.success, let taskId = response.task_id {
                    print("上传成功，任务ID: \(taskId)")
                    uploadStatus = .processing
                    simulateProcessing() // 暂时还是用模拟处理
                } else {
                    errorMessage = response.message ?? "上传失败"
                    uploadStatus = .failed
                }
            } catch {
                errorMessage = "解析响应失败: \(error.localizedDescription)"
                uploadStatus = .failed
            }
        } else {
            errorMessage = "服务器错误 (\(httpResponse.statusCode))"
            uploadStatus = .failed
        }
    }
    
    private func simulateProcessing() {
        DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
            self.comicResult = self.createMockComicResult()
            self.uploadStatus = .completed
        }
    }
    
    private func createMockComicResult() -> ComicResult {
        let videoTitle = selectedVideos.isEmpty ? "测试视频.mp4" : selectedVideos.map { $0.lastPathComponent }.joined(separator: ", ")

        return ComicResult(
            comicId: "mock-comic-123",
            deviceId: UIDevice.current.identifierForVendor?.uuidString ?? "mock-device",
            originalVideoTitle: videoTitle,
            creationDate: ISO8601DateFormatter().string(from: Date()),
            panelCount: 4,
            panels: [
                ComicPanel(panelNumber: 1, imageUrl: "https://picsum.photos/300/400?random=1", narration: "故事从宁静的沙滩开始"),
                ComicPanel(panelNumber: 2, imageUrl: "https://picsum.photos/300/400?random=2", narration: "一个小小身影闯入画面"),
                ComicPanel(panelNumber: 3, imageUrl: "https://picsum.photos/300/400?random=3", narration: "阳光洒在海面上"),
                ComicPanel(panelNumber: 4, imageUrl: "https://picsum.photos/300/400?random=4", narration: "一家人的笑声比阳光还灿烂")
            ],
            finalQuestions: [
                "你还记得那天沙子的温度吗？",
                "视频里谁的笑声最大？",
                "用一个词形容那天的天空？"
            ]
        )
    }
    
    // MARK: - 控制方法
    func toggleUploadMode() {
        uploadMode = uploadMode == .mock ? .real : .mock
    }

    func cancelUpload() {
        uploadTask?.cancel()
        uploadTask = nil
        cancellables.removeAll()
        uploadStatus = .pending
        uploadProgress = 0
        errorMessage = nil
    }

    func reset() {
        selectedVideos = []
        uploadStatus = .pending
        uploadProgress = 0
        errorMessage = nil
        comicResult = nil
        cancellables.removeAll()
        uploadTask?.cancel()
        uploadTask = nil
    }
}
