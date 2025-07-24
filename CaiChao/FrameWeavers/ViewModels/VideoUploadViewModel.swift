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
    private var currentTaskId: String?  // 当前任务ID
    private var progressTimer: Timer?   // 进度查询定时器

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

        // 根据API文档，只需要添加视频文件，不需要device_id
        for videoURL in videoURLs {
            body.append("--\(boundary)\r\n".data(using: .utf8)!)
            body.append("Content-Disposition: form-data; name=\"videos\"; filename=\"\(videoURL.lastPathComponent)\"\r\n".data(using: .utf8)!)

            // 根据文件扩展名设置正确的Content-Type
            let mimeType = getMimeType(for: videoURL)
            body.append("Content-Type: \(mimeType)\r\n\r\n".data(using: .utf8)!)

            let videoData = try Data(contentsOf: videoURL)
            body.append(videoData)
            body.append("\r\n".data(using: .utf8)!)
        }

        // 结束边界
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)

        return body
    }

    private func getMimeType(for url: URL) -> String {
        let fileExtension = url.pathExtension.lowercased()
        switch fileExtension {
        case "mp4":
            return "video/mp4"
        case "mov":
            return "video/quicktime"
        case "avi":
            return "video/x-msvideo"
        case "mkv":
            return "video/x-matroska"
        case "wmv":
            return "video/x-ms-wmv"
        case "flv":
            return "video/x-flv"
        case "3gp":
            return "video/3gpp"
        default:
            return "video/mp4"  // 默认
        }
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
                    print("上传文件数: \(response.uploaded_files ?? 0)")
                    if let invalidFiles = response.invalid_files, !invalidFiles.isEmpty {
                        print("无效文件: \(invalidFiles)")
                    }

                    currentTaskId = taskId
                    uploadStatus = .processing
                    startProgressPolling(taskId: taskId)  // 开始轮询进度
                } else {
                    errorMessage = response.message
                    uploadStatus = .failed
                }
            } catch {
                errorMessage = "解析响应失败: \(error.localizedDescription)"
                uploadStatus = .failed
            }
        } else {
            // 处理错误响应
            do {
                let errorResponse = try JSONDecoder().decode(RealUploadResponse.self, from: data)
                errorMessage = errorResponse.message
            } catch {
                errorMessage = "服务器错误 (\(httpResponse.statusCode))"
            }
            uploadStatus = .failed
        }
    }
    
    // MARK: - 进度轮询
    private func startProgressPolling(taskId: String) {
        progressTimer?.invalidate()

        progressTimer = Timer.scheduledTimer(withTimeInterval: 2.0, repeats: true) { [weak self] _ in
            self?.checkTaskStatus(taskId: taskId)
        }
    }

    private func checkTaskStatus(taskId: String) {
        let url = NetworkConfig.Endpoint.taskStatus(taskId: taskId).url

        URLSession.shared.dataTask(with: url) { [weak self] data, response, error in
            DispatchQueue.main.async {
                self?.handleTaskStatusResponse(data: data, response: response, error: error)
            }
        }.resume()
    }

    private func handleTaskStatusResponse(data: Data?, response: URLResponse?, error: Error?) {
        guard let data = data,
              let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            return
        }

        do {
            let statusResponse = try JSONDecoder().decode(TaskStatusResponse.self, from: data)

            // 更新进度
            uploadProgress = Double(statusResponse.progress) / 100.0

            switch statusResponse.status {
            case "uploaded":
                uploadStatus = .processing
            case "processing":
                uploadStatus = .processing
            case "completed":
                uploadStatus = .completed
                progressTimer?.invalidate()
                progressTimer = nil
                // 这里可以处理完成后的结果
                comicResult = createMockComicResult()  // 暂时用Mock结果
            case "error":
                uploadStatus = .failed
                errorMessage = statusResponse.message
                progressTimer?.invalidate()
                progressTimer = nil
            case "cancelled":
                uploadStatus = .failed
                errorMessage = "任务已取消"
                progressTimer?.invalidate()
                progressTimer = nil
            default:
                break
            }

        } catch {
            print("解析状态响应失败: \(error)")
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
        // 取消上传任务
        uploadTask?.cancel()
        uploadTask = nil

        // 停止进度轮询
        progressTimer?.invalidate()
        progressTimer = nil

        // 如果有任务ID，尝试取消后端任务
        if let taskId = currentTaskId {
            cancelBackendTask(taskId: taskId)
        }

        cancellables.removeAll()
        uploadStatus = .pending
        uploadProgress = 0
        errorMessage = nil
        currentTaskId = nil
    }

    private func cancelBackendTask(taskId: String) {
        let url = NetworkConfig.Endpoint.taskCancel(taskId: taskId).url
        var request = URLRequest(url: url)
        request.httpMethod = "POST"

        URLSession.shared.dataTask(with: request) { data, response, error in
            if let data = data,
               let httpResponse = response as? HTTPURLResponse,
               httpResponse.statusCode == 200 {
                do {
                    let cancelResponse = try JSONDecoder().decode(TaskCancelResponse.self, from: data)
                    print("任务取消结果: \(cancelResponse.message)")
                } catch {
                    print("解析取消响应失败: \(error)")
                }
            }
        }.resume()
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
        progressTimer?.invalidate()
        progressTimer = nil
        currentTaskId = nil
    }
}
