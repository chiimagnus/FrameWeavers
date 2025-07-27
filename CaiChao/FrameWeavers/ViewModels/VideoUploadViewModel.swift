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
    @Published var baseFrames: [BaseFrameData] = [] // 基础帧数据

    private var cancellables = Set<AnyCancellable>()
    private var uploadTask: URLSessionUploadTask?
    private var currentTaskId: String?  // 当前任务ID
    private var currentVideoPath: String?  // 当前视频路径
    private var progressTimer: Timer?   // 进度查询定时器
    private let baseFrameService = BaseFrameService() // 基础帧服务
    private let comicGenerationService = ComicGenerationService() // 连环画生成服务

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

        uploadVideosReal(videoURLs: selectedVideos)  // 仅使用真实上传模式
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

        // 添加必需的device_id参数
        let deviceId = DeviceIDGenerator.generateDeviceID()
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"device_id\"\r\n\r\n".data(using: .utf8)!)
        body.append("\(deviceId)\r\n".data(using: .utf8)!)

        // 添加视频文件
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

        // 添加调试信息
        print("HTTP状态码: \(httpResponse.statusCode)")
        if let responseString = String(data: data, encoding: .utf8) {
            print("服务器响应内容: \(responseString)")
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

                    // 保存视频路径
                    if let videoPath = response.video_path {
                        currentVideoPath = videoPath
                        print("📹 保存视频路径: \(videoPath)")
                    }

                    currentTaskId = taskId
                    uploadStatus = .processing
                    startProgressPolling(taskId: taskId)  // 开始轮询进度
                } else {
                    errorMessage = response.message
                    uploadStatus = .failed
                }
            } catch {
                print("JSON解析错误详情: \(error)")
                if let decodingError = error as? DecodingError {
                    print("解码错误详情: \(decodingError)")
                }
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

        // 打印响应内容以便调试
        if let responseString = String(data: data, encoding: .utf8) {
            print("任务状态响应: \(responseString)")
        }

        do {
            // 尝试解析为通用JSON对象
            if let jsonObject = try JSONSerialization.jsonObject(with: data) as? [String: Any] {
                // 提取关键字段
                let _ = jsonObject["success"] as? Bool ?? false
                let status = jsonObject["status"] as? String ?? ""
                let progress = jsonObject["progress"] as? Int ?? 0
                let message = jsonObject["message"] as? String ?? ""

                // 更新进度
                uploadProgress = Double(progress) / 100.0

                print("任务状态: \(status), 进度: \(progress)%")

                if status == "completed" {
                    uploadStatus = .processing // 先设置为处理中
                    progressTimer?.invalidate()
                    progressTimer = nil
                    // 开始提取基础帧
                    Task {
                        await extractBaseFrames()
                    }
                } else if status == "error" || status == "cancelled" {
                    uploadStatus = .failed
                    errorMessage = message
                    progressTimer?.invalidate()
                    progressTimer = nil
                } else {
                    // 处理中或上传完成等待处理
                    uploadStatus = .processing
                }
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

    // MARK: - 基础帧提取
    private func extractBaseFrames() async {
        guard let taskId = currentTaskId else {
            print("❌ 基础帧提取失败: 缺少任务ID")
            await MainActor.run {
                self.uploadStatus = .failed
                self.errorMessage = "缺少任务ID"
            }
            return
        }

        print("🎬 开始提取基础帧, taskId: \(taskId)")

        do {
            let response = try await baseFrameService.extractBaseFrames(taskId: taskId, interval: 1.0)
            print("✅ 基础帧提取API调用成功")
            print("📊 响应数据: success=\(response.success), message=\(response.message)")
            print("📁 结果数量: \(response.results.count)")

            // 转换响应数据为BaseFrameData
            let frames = response.results.flatMap { result in
                print("🎞️ 视频: \(result.videoName), 基础帧数量: \(result.baseFramesCount)")
                print("📸 基础帧路径: \(result.baseFramesPaths)")
                return result.baseFramesPaths.enumerated().map { index, path in
                    BaseFrameData(
                        framePath: path,
                        frameIndex: index,
                        timestamp: Double(index) * 1.0
                    )
                }
            }

            print("🖼️ 转换后的基础帧数量: \(frames.count)")

            await MainActor.run {
                self.baseFrames = frames
                print("✅ 基础帧数据已设置到ViewModel")
            }

            // 开始生成完整连环画
            await generateCompleteComic()

        } catch {
            print("❌ 基础帧提取失败: \(error)")
            await MainActor.run {
                self.uploadStatus = .failed
                self.errorMessage = "基础帧提取失败: \(error.localizedDescription)"
            }
        }
    }

    // MARK: - 生成完整连环画
    private func generateCompleteComic() async {
        guard let taskId = currentTaskId else {
            print("❌ 没有有效的任务ID")
            await MainActor.run {
                self.uploadStatus = .failed
                self.errorMessage = "没有有效的任务ID"
            }
            return
        }

        guard let videoPath = currentVideoPath else {
            print("❌ 没有有效的视频路径")
            await MainActor.run {
                self.uploadStatus = .failed
                self.errorMessage = "没有有效的视频路径"
            }
            return
        }

        print("🎬 开始生成完整连环画，任务ID: \(taskId)")
        print("📹 使用视频路径: \(videoPath)")

        do {
            // 创建请求参数，严格参考Python测试文件
            let request = CompleteComicRequest(
                taskId: taskId,
                videoPath: videoPath,  // 必须：使用后端返回的视频路径
                storyStyle: "温馨童话",  // 必须：故事风格关键词
                targetFrames: 5,  // 参考Python测试
                frameInterval: 2.0,  // 参考Python测试
                significanceWeight: 0.7,  // 参考Python测试
                qualityWeight: 0.3,  // 参考Python测试
                stylePrompt: "Convert to Ink and brushwork style, Chinese style, Yellowed and old, Low saturation, Low brightness",  // 参考Python测试
                imageSize: "1780x1024",  // 参考Python测试
                maxConcurrent: 50
            )

            // 启动连环画生成
            let response = try await comicGenerationService.startCompleteComicGeneration(request: request)
            print("✅ 连环画生成已启动: \(response.message)")

            await MainActor.run {
                self.uploadStatus = .processing
            }

            // 开始轮询任务状态，等待完成
            await pollComicGenerationStatus(taskId: taskId)

        } catch {
            print("❌ 连环画生成失败: \(error)")
            await MainActor.run {
                self.uploadStatus = .failed
                self.errorMessage = "连环画生成失败: \(error.localizedDescription)"
            }
        }
    }

    // MARK: - 轮询连环画生成状态
    private func pollComicGenerationStatus(taskId: String) async {
        let maxWaitTime: TimeInterval = 3000.0  // 最多等待3000秒（50分钟）
        let interval: TimeInterval = 2.0  // 每2秒查询一次，参考Python实现
        let startTime = Date()
        var lastProgress = -1
        var consecutiveErrors = 0  // 连续错误计数
        let maxConsecutiveErrors = 10  // 最多允许10次连续错误

        // 阶段描述映射，参考Python实现
        let stageDescriptions = [
            "initializing": "初始化中",
            "extracting_keyframes": "正在提取关键帧",
            "generating_story": "正在生成故事",
            "stylizing_frames": "正在风格化处理",
            "completed": "已完成"
        ]

        while Date().timeIntervalSince(startTime) < maxWaitTime {
            do {
                // 查询任务状态
                let statusUrl = NetworkConfig.Endpoint.taskStatus(taskId: taskId).url
                let (data, response) = try await URLSession.shared.data(from: statusUrl)

                guard let httpResponse = response as? HTTPURLResponse,
                      httpResponse.statusCode == 200 else {
                    let statusCode = (response as? HTTPURLResponse)?.statusCode ?? -1
                    consecutiveErrors += 1
                    print("❌ 状态查询失败，HTTP状态码: \(statusCode)，连续错误: \(consecutiveErrors)")

                    // 打印错误响应内容以便调试
                    if let errorString = String(data: data, encoding: .utf8) {
                        print("📄 错误响应内容: \(errorString)")
                    }

                    // 如果连续错误太多，或者是400错误且进度已经较高，尝试获取最终结果
                    if consecutiveErrors >= maxConsecutiveErrors ||
                       (statusCode == 400 && lastProgress >= 70) {
                        print("⚠️ 连续错误过多或高进度400错误，尝试获取最终结果")
                        await fetchComicResult(taskId: taskId)
                        return
                    }

                    do {
                        try await Task.sleep(nanoseconds: UInt64(interval * 1_000_000_000))
                    } catch {
                        print("⚠️ 等待间隔失败: \(error)")
                    }
                    continue
                }

                let statusResponse = try JSONDecoder().decode(TaskStatusResponse.self, from: data)

                // 成功获取状态，重置错误计数
                consecutiveErrors = 0

                // 只在进度变化时打印，参考Python实现
                if statusResponse.progress != lastProgress {
                    let stage = statusResponse.stage ?? "unknown"
                    let stageDesc = stageDescriptions[stage] ?? stage
                    print("📈 \(statusResponse.progress)% - \(stageDesc)")
                    lastProgress = statusResponse.progress

                    await MainActor.run {
                        self.uploadProgress = Double(statusResponse.progress) / 100.0
                    }
                }

                // 检查完成状态，参考Python实现
                if statusResponse.status == "complete_comic_completed" {
                    print("✅ 连环画生成完成！")
                    await fetchComicResult(taskId: taskId)
                    return
                } else if statusResponse.status == "complete_comic_failed" || statusResponse.status == "error" {
                    print("❌ 连环画生成失败: \(statusResponse.message)")
                    await MainActor.run {
                        self.uploadStatus = .failed
                        self.errorMessage = "连环画生成失败: \(statusResponse.message)"
                    }
                    return
                }

                // 等待下次查询
                do {
                    try await Task.sleep(nanoseconds: UInt64(interval * 1_000_000_000))
                } catch {
                    print("⚠️ 等待间隔失败: \(error)")
                    // 如果sleep失败，继续循环
                }

            } catch {
                print("⚠️ 查询状态异常: \(error)")
                // 继续尝试，参考Python实现
                do {
                    try await Task.sleep(nanoseconds: UInt64(interval * 1_000_000_000))
                } catch {
                    print("⚠️ 等待间隔失败: \(error)")
                    // 如果连sleep都失败了，直接跳出循环
                    break
                }
            }
        }

        // 超时处理
        print("⏰ 连环画生成监控超时（3000秒）")
        await MainActor.run {
            self.uploadStatus = .failed
            self.errorMessage = "连环画生成监控超时，请稍后重试"
        }
    }

    // MARK: - 获取连环画结果
    private func fetchComicResult(taskId: String) async {
        do {
            print("📖 获取连环画结果...")
            let resultResponse = try await comicGenerationService.getComicResult(taskId: taskId)

            if let comicResult = comicGenerationService.convertToComicResult(from: resultResponse, taskId: taskId) {
                print("✅ 连环画结果转换成功，共\(comicResult.panels.count)页")

                await MainActor.run {
                    self.comicResult = comicResult
                    self.uploadStatus = .completed
                    self.uploadProgress = 1.0
                }
            } else {
                print("❌ 连环画结果转换失败")
                await MainActor.run {
                    self.uploadStatus = .failed
                    self.errorMessage = "连环画结果转换失败"
                }
            }

        } catch {
            print("❌ 获取连环画结果失败: \(error)")
            await MainActor.run {
                self.uploadStatus = .failed
                self.errorMessage = "获取连环画结果失败: \(error.localizedDescription)"
            }
        }
    }

    private func createMockComicResult() -> ComicResult {
        let videoTitle = selectedVideos.isEmpty ? "测试视频.mp4" : selectedVideos.map { $0.lastPathComponent }.joined(separator: ", ")

        return ComicResult(
            comicId: "mock-comic-123",
            deviceId: UIDevice.current.identifierForVendor?.uuidString ?? "mock-device",
            title: "海滩上的温暖时光",  // 添加故事标题
            originalVideoTitle: videoTitle,
            creationDate: ISO8601DateFormatter().string(from: Date()),
            panelCount: 4,
            panels: [
                ComicPanel(panelNumber: 1, imageUrl: "Image1", narration: "故事从宁静的沙滩开始"),
                ComicPanel(panelNumber: 2, imageUrl: "Image2", narration: "一个小小身影闯入画面"),
                ComicPanel(panelNumber: 3, imageUrl: "Image3", narration: "阳光洒在海面上"),
                ComicPanel(panelNumber: 4, imageUrl: "Image4", narration: "一家人的笑声比阳光还灿烂")
            ],
            finalQuestions: [
                "你还记得那天沙子的温度吗？",
                "视频里谁的笑声最大？",
                "用一个词形容那天的天空？"
            ]
        )
    }
    
    // 上传模式切换方法已删除

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
        currentVideoPath = nil  // 清理视频路径
    }
}
