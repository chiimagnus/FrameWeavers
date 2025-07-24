import Foundation
import PhotosUI
import AVFoundation
import Combine

class VideoUploadViewModel: ObservableObject {
    @Published var selectedVideo: URL?
    @Published var uploadStatus: UploadStatus = .pending
    @Published var uploadProgress: Double = 0
    @Published var errorMessage: String?
    @Published var comicResult: ComicResult?
    @Published var isShowingPicker = false
    @Published var uploadMode: UploadMode = .mock

    private var cancellables = Set<AnyCancellable>()
    private var uploadTask: URLSessionUploadTask?
    
    func selectVideo(_ url: URL) {
        selectedVideo = url
        validateVideo(url)
    }
    
    private func validateVideo(_ url: URL) {
        let asset = AVAsset(url: url)
        let duration = asset.duration.seconds
        
        if duration > 300 { // 5分钟
            errorMessage = "视频时长超过5分钟"
            uploadStatus = .failed
        } else {
            errorMessage = nil
            uploadStatus = .pending
        }
    }
    
    func uploadVideo() {
        guard let videoURL = selectedVideo else { return }

        uploadStatus = .uploading
        uploadProgress = 0
        errorMessage = nil

        if uploadMode == .mock {
            uploadVideoMock(videoURL: videoURL)
        } else {
            uploadVideoReal(videoURL: videoURL)
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

    // MARK: - 真实HTTP上传
    private func uploadVideoReal(videoURL: URL) {
        guard let request = createUploadRequest(videoURL: videoURL) else {
            errorMessage = "创建上传请求失败"
            uploadStatus = .failed
            return
        }

        let session = URLSession.shared
        uploadTask = session.uploadTask(with: request, fromFile: videoURL) { [weak self] data, response, error in
            DispatchQueue.main.async {
                self?.handleUploadResponse(data: data, response: response, error: error)
            }
        }

        uploadTask?.resume()
    }

    private func createUploadRequest(videoURL: URL) -> URLRequest? {
        // 使用NetworkConfig统一管理网络配置
        let url = NetworkConfig.Endpoint.uploadVideo.url
        
        var request = URLRequest(url: url)
        request.httpMethod = NetworkConfig.HTTPMethod.POST.rawValue
        
        // 使用NetworkConfig的默认请求头
        let headers = NetworkConfig.defaultHeaders()
        for (key, value) in headers {
            request.setValue(value, forHTTPHeaderField: key)
        }
        
        return request
    }

    private func handleUploadResponse(data: Data?, response: URLResponse?, error: Error?) {
        if let error = error {
            errorMessage = "上传失败: \(error.localizedDescription)"
            uploadStatus = .failed
            return
        }

        guard let httpResponse = response as? HTTPURLResponse,
              200...299 ~= httpResponse.statusCode else {
            errorMessage = "服务器响应错误"
            uploadStatus = .failed
            return
        }

        // 上传成功，开始处理
        uploadStatus = .processing
        simulateProcessing()
    }
    
    private func simulateProcessing() {
        DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
            self.comicResult = self.createMockComicResult()
            self.uploadStatus = .completed
        }
    }
    
    private func createMockComicResult() -> ComicResult {
        return ComicResult(
            comicId: "mock-comic-123",
            deviceId: UIDevice.current.identifierForVendor?.uuidString ?? "mock-device",
            originalVideoTitle: selectedVideo?.lastPathComponent ?? "测试视频.mp4",
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
        selectedVideo = nil
        uploadStatus = .pending
        uploadProgress = 0
        errorMessage = nil
        comicResult = nil
        cancellables.removeAll()
        uploadTask?.cancel()
        uploadTask = nil
    }
}
