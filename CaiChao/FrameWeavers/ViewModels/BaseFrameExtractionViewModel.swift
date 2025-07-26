import Foundation
import Combine
import SwiftUI

// MARK: - 基础帧提取ViewModel
class BaseFrameExtractionViewModel: ObservableObject {
    @Published var status: BaseFrameExtractionStatus = .idle
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var progress: Double = 0.0
    
    private let baseFrameService: BaseFrameServiceProtocol
    private var cancellables = Set<AnyCancellable>()
    
    init(baseFrameService: BaseFrameServiceProtocol = BaseFrameService()) {
        self.baseFrameService = baseFrameService
    }
    
    // MARK: - 提取基础帧
    func extractBaseFrames(taskId: String, interval: Double = 1.0) async {
        guard !taskId.isEmpty else {
            await MainActor.run {
                self.status = .failed("任务ID不能为空")
                self.errorMessage = "任务ID不能为空"
            }
            return
        }
        
        await MainActor.run {
            self.isLoading = true
            self.status = .extracting
            self.progress = 0.0
            self.errorMessage = nil
        }
        
        do {
            let response = try await baseFrameService.extractBaseFrames(taskId: taskId, interval: interval)
            
            // 转换响应数据为BaseFrameData
            let baseFrames = response.results.flatMap { result in
                result.baseFramesPaths.enumerated().map { index, path in
                    BaseFrameData(
                        framePath: path,
                        frameIndex: index,
                        timestamp: Double(index) * interval
                    )
                }
            }
            
            await MainActor.run {
                self.status = .completed(baseFrames)
                self.progress = 1.0
                self.isLoading = false
            }
            
        } catch let error as BaseFrameError {
            await MainActor.run {
                self.status = .failed(error.localizedDescription)
                self.errorMessage = error.localizedDescription
                self.isLoading = false
                self.progress = 0.0
            }
        } catch {
            await MainActor.run {
                self.status = .failed("未知错误: \(error.localizedDescription)")
                self.errorMessage = "未知错误: \(error.localizedDescription)"
                self.isLoading = false
                self.progress = 0.0
            }
        }
    }
    
    // MARK: - 重置状态
    func reset() {
        status = .idle
        isLoading = false
        errorMessage = nil
        progress = 0.0
    }
    
    // MARK: - 获取当前基础帧
    var currentBaseFrames: [BaseFrameData] {
        switch status {
        case .completed(let frames):
            return frames
        default:
            return []
        }
    }
    
    // MARK: - 检查是否成功
    var isSuccessful: Bool {
        switch status {
        case .completed:
            return true
        default:
            return false
        }
    }
    
    // MARK: - 获取状态描述
    var statusDescription: String {
        switch status {
        case .idle:
            return "准备提取基础帧"
        case .extracting:
            return "正在提取基础帧..."
        case .completed(let frames):
            return "成功提取 \(frames.count) 个基础帧"
        case .failed(let error):
            return "提取失败: \(error)"
        }
    }
}

// MARK: - 基础帧预览ViewModel
class BaseFramePreviewViewModel: ObservableObject {
    @Published var selectedFrame: BaseFrameData?
    @Published var isZoomed = false
    
    func selectFrame(_ frame: BaseFrameData) {
        selectedFrame = frame
    }
    
    func toggleZoom() {
        isZoomed.toggle()
    }
    
    func clearSelection() {
        selectedFrame = nil
        isZoomed = false
    }
}