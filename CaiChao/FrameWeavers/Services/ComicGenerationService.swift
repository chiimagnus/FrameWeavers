import Foundation

// MARK: - 完整连环画生成服务
class ComicGenerationService {
    private let baseURL: String
    
    init(baseURL: String = NetworkConfig.baseURL) {
        self.baseURL = baseURL
    }
    
    // MARK: - 启动完整连环画生成
    func startCompleteComicGeneration(request: CompleteComicRequest) async throws -> CompleteComicResponse {
        let endpoint = "/api/process/complete-comic"
        let urlString = baseURL + endpoint
        print("🌐 ComicGenerationService: 请求URL: \(urlString)")
        
        guard let url = URL(string: urlString) else {
            print("❌ ComicGenerationService: 无效的URL: \(urlString)")
            throw NSError(domain: "ComicGenerationService", code: -1, userInfo: [NSLocalizedDescriptionKey: "无效的URL"])
        }
        
        let parameters = [
            "task_id": request.taskId,
            "video_path": request.videoPath,  // 必须：视频路径参数
            "story_style": request.storyStyle,  // 必须：故事风格关键词
            "target_frames": String(request.targetFrames),
            "frame_interval": String(request.frameInterval),
            "significance_weight": String(request.significanceWeight),
            "quality_weight": String(request.qualityWeight),
            "style_prompt": request.stylePrompt,
            "image_size": request.imageSize,
            "max_concurrent": String(request.maxConcurrent)
        ]
        print("📝 ComicGenerationService: 请求参数: \(parameters)")
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")
        
        let bodyString = parameters.map { "\($0.key)=\($0.value)" }.joined(separator: "&")
        urlRequest.httpBody = bodyString.data(using: .utf8)
        print("📤 ComicGenerationService: 请求体: \(bodyString)")
        
        let (data, response) = try await URLSession.shared.data(for: urlRequest)
        print("📥 ComicGenerationService: 收到响应")
        
        guard let httpResponse = response as? HTTPURLResponse else {
            print("❌ ComicGenerationService: 无效的HTTP响应")
            throw NSError(domain: "ComicGenerationService", code: -2, userInfo: [NSLocalizedDescriptionKey: "无效的HTTP响应"])
        }
        
        print("📊 ComicGenerationService: HTTP状态码: \(httpResponse.statusCode)")
        
        if let responseString = String(data: data, encoding: .utf8) {
            print("📄 ComicGenerationService: 响应内容: \(responseString)")
        }
        
        guard httpResponse.statusCode == 200 else {
            let errorMessage = "HTTP错误: \(httpResponse.statusCode)"
            print("❌ ComicGenerationService: \(errorMessage)")
            throw NSError(domain: "ComicGenerationService", code: httpResponse.statusCode, userInfo: [NSLocalizedDescriptionKey: errorMessage])
        }
        
        do {
            let decoder = JSONDecoder()
            let response = try decoder.decode(CompleteComicResponse.self, from: data)
            print("✅ ComicGenerationService: 解析响应成功")
            return response
        } catch {
            print("❌ ComicGenerationService: 解析响应失败: \(error)")
            throw NSError(domain: "ComicGenerationService", code: -3, userInfo: [NSLocalizedDescriptionKey: "解析响应失败: \(error.localizedDescription)"])
        }
    }
    
    // MARK: - 获取连环画结果
    func getComicResult(taskId: String) async throws -> ComicResultResponse {
        let endpoint = "/api/comic/result/\(taskId)"
        let urlString = baseURL + endpoint
        print("🌐 ComicGenerationService: 获取结果URL: \(urlString)")
        
        guard let url = URL(string: urlString) else {
            print("❌ ComicGenerationService: 无效的URL: \(urlString)")
            throw NSError(domain: "ComicGenerationService", code: -1, userInfo: [NSLocalizedDescriptionKey: "无效的URL"])
        }
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "GET"
        
        let (data, response) = try await URLSession.shared.data(for: urlRequest)
        print("📥 ComicGenerationService: 收到结果响应")
        
        guard let httpResponse = response as? HTTPURLResponse else {
            print("❌ ComicGenerationService: 无效的HTTP响应")
            throw NSError(domain: "ComicGenerationService", code: -2, userInfo: [NSLocalizedDescriptionKey: "无效的HTTP响应"])
        }
        
        print("📊 ComicGenerationService: HTTP状态码: \(httpResponse.statusCode)")
        
        if let responseString = String(data: data, encoding: .utf8) {
            print("📄 ComicGenerationService: 结果响应内容: \(responseString)")
        }
        
        guard httpResponse.statusCode == 200 else {
            let errorMessage = "HTTP错误: \(httpResponse.statusCode)"
            print("❌ ComicGenerationService: \(errorMessage)")
            throw NSError(domain: "ComicGenerationService", code: httpResponse.statusCode, userInfo: [NSLocalizedDescriptionKey: errorMessage])
        }
        
        do {
            let decoder = JSONDecoder()
            let response = try decoder.decode(ComicResultResponse.self, from: data)
            print("✅ ComicGenerationService: 解析结果响应成功")
            return response
        } catch {
            print("❌ ComicGenerationService: 解析结果响应失败: \(error)")
            throw NSError(domain: "ComicGenerationService", code: -3, userInfo: [NSLocalizedDescriptionKey: "解析结果响应失败: \(error.localizedDescription)"])
        }
    }
    
    // MARK: - 将API响应转换为UI模型
    func convertToComicResult(from response: ComicResultResponse, taskId: String) -> ComicResult? {
        guard let firstComic = response.results.successfulComics.first else {
            print("❌ ComicGenerationService: 没有成功的连环画数据")
            return nil
        }
        
        let comicData = firstComic.comicData
        let storyInfo = comicData.storyInfo
        
        // 转换页面数据为ComicPanel
        let panels = comicData.pages.map { page in
            // 构建图片URL - 使用风格化后的图片
            let imageUrl = buildImageUrl(from: page.styledFramePath)
            
            return ComicPanel(
                panelNumber: page.pageIndex + 1,
                imageUrl: imageUrl,
                narration: page.storyText
            )
        }
        
        // 转换互动问题
        let questions = comicData.interactiveQuestions.map { $0.question }
        
        return ComicResult(
            comicId: taskId,
            deviceId: DeviceIDGenerator.generateDeviceID(),
            title: storyInfo.title,  // 使用故事标题
            originalVideoTitle: storyInfo.videoName,  // 保留原始视频文件名
            creationDate: storyInfo.creationTime,
            panelCount: panels.count,
            panels: panels,
            finalQuestions: questions
        )
    }
    
    // MARK: - 构建图片URL
    private func buildImageUrl(from path: String) -> String {
        if path.hasPrefix("http") {
            return path
        } else {
            // 如果是相对路径，需要拼接服务器地址
            let normalizedPath = path.replacingOccurrences(of: "\\", with: "/")
            return "\(baseURL)/\(normalizedPath)"
        }
    }
}
