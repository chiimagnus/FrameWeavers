import SwiftUI

/// 处理视图 - 遵循MVVM架构的主视图
struct ProcessingView: View {
    @Environment(\.dismiss) private var dismiss
    @ObservedObject var viewModel: VideoUploadViewModel
    @StateObject private var galleryViewModel = ProcessingGalleryViewModel()
    @StateObject private var baseFrameVM = BaseFrameExtractionViewModel()
    
    @State private var navigateToResults = false
    @State private var frames: [String: CGRect] = [:]
    @State private var currentStage: ProcessingStage = .upload
    @Namespace private var galleryNamespace
    
    // 定时器
    let scrollTimer = Timer.publish(every: 3, on: .main, in: .common).autoconnect()
    let jumpTimer = Timer.publish(every: 4, on: .main, in: .common).autoconnect()
    
    var body: some View {
        NavigationStack {
            ZStack {
                // 背景色
                Color(red: 0.91, green: 0.88, blue: 0.83).ignoresSafeArea()
                
                VStack(spacing: 20) {
                    // 处理阶段指示器
                    processingStageIndicator
                    
                    // 根据当前阶段显示不同内容
                    stageContentView
                }
                .padding(.vertical, 20)
                
                // 飞行图片覆盖层
                if let info = galleryViewModel.flyingImageInfo {
                    Image(info.id)
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                        .frame(width: info.sourceFrame.width, height: info.sourceFrame.height)
                        .clipShape(RoundedRectangle(cornerRadius: 8))
                        .matchedGeometryEffect(id: info.id, in: galleryNamespace)
                        .position(x: info.sourceFrame.midX, y: info.sourceFrame.midY)
                        .transition(.identity)
                }
            }
        }
        .onPreferenceChange(FramePreferenceKey.self) { value in
            self.frames.merge(value, uniquingKeysWith: { $1 })
        }
        .onReceive(scrollTimer) { _ in
            // 在所有等待状态下都播放滚动动画
            if viewModel.uploadStatus != .completed && viewModel.uploadStatus != .failed {
                galleryViewModel.currentScrollIndex += 1
            }
        }
        .onReceive(jumpTimer) { _ in
            // 在所有等待状态下都播放跳跃动画
            if viewModel.uploadStatus != .completed && viewModel.uploadStatus != .failed {
                withAnimation(.easeInOut(duration: 1.2)) {
                    galleryViewModel.triggerJumpAnimation(from: frames)
                }
            }
        }
        .onAppear {
            startProcessingFlow()
        }
        .onChange(of: viewModel.uploadStatus) { _, newStatus in
            handleUploadStatusChange(newStatus)
        }
        .onChange(of: baseFrameVM.status) { _, newStatus in
            handleBaseFrameStatusChange(newStatus)
        }
        .navigationDestination(isPresented: $navigateToResults) {
            if let result = viewModel.comicResult {
                OpenResultsView(comicResult: result)
            }
        }
        .navigationBarBackButtonHidden(true)
        .toolbar {
            ToolbarItem(placement: .navigationBarLeading) {
                Button(action: {
                    dismiss()
                }) {
                    Image(systemName: "chevron.left")
                        .foregroundColor(Color(hex: "#2F2617"))
                }
            }
        }
    }
}

// MARK: - 处理阶段相关视图
extension ProcessingView {
    /// 处理阶段指示器
    private var processingStageIndicator: some View {
        VStack(spacing: 8) {
            HStack(spacing: 20) {
                ForEach(ProcessingStage.allCases, id: \.self) { stage in
                    VStack(spacing: 4) {
                        Image(systemName: stage.iconName)
                            .font(.title2)
                            .foregroundColor(stage == currentStage ? .blue : .secondary)
                        
                        Text(stage.rawValue)
                            .font(.caption)
                            .foregroundColor(stage == currentStage ? .primary : .secondary)
                    }
                }
            }
            
            ProgressView(value: currentStage.progressValue)
                .progressViewStyle(LinearProgressViewStyle())
                .frame(maxWidth: 300)
                .padding(.horizontal)
        }
        .padding(.horizontal)
    }
    
    /// 根据当前阶段显示不同内容
    private var stageContentView: some View {
        Group {
            switch currentStage {
            case .upload:
                uploadContentView
            case .baseFrameExtraction:
                baseFrameExtractionContentView
            case .keyFrameExtraction, .storyGeneration, .styleProcessing, .comicGeneration:
                processingContentView
            case .completed:
                completedContentView
            }
        }
    }
    
    /// 上传内容视图
    private var uploadContentView: some View {
        VStack(spacing: 40) {
            // 始终显示胶片画廊视图
            filmGalleryView
        }
    }
    
    /// 基础帧提取内容视图
    private var baseFrameExtractionContentView: some View {
        VStack(spacing: 20) {
            // 基础帧提取状态
            BaseFrameExtractionStatusView(viewModel: baseFrameVM)
            
            // 基础帧预览
            if !baseFrameVM.currentBaseFrames.isEmpty {
                BaseFramePreviewView(baseFrames: baseFrameVM.currentBaseFrames)
                    .padding(.horizontal)
            }
            
            Spacer()
        }
    }
    
    /// 处理中内容视图
    private var processingContentView: some View {
        VStack(spacing: 40) {
            filmGalleryView
        }
    }
    
    /// 完成内容视图
    private var completedContentView: some View {
        VStack(spacing: 40) {
            filmGalleryView
        }
    }
}

// MARK: - 子视图
extension ProcessingView {
    /// 胶片画廊视图
    private var filmGalleryView: some View {
        VStack(spacing: 40) {
            PhotoStackView(
                mainImageName: galleryViewModel.mainImageName,
                stackedImages: galleryViewModel.stackedImages,
                namespace: galleryNamespace
            )
                .anchorPreference(key: FramePreferenceKey.self, value: .bounds) { anchor in
                    return ["photoStackTarget": self.frames(from: anchor)]
                }

            FilmstripView(galleryViewModel: galleryViewModel, uploadViewModel: viewModel, namespace: galleryNamespace)

            // 统一的进度条显示
            ProcessingLoadingView(progress: getCurrentProgress(), status: getCurrentStatus())
            
            Spacer()
        }
    }
    
    /// Helper to convert anchor to global frame
    private func frames(from anchor: Anchor<CGRect>) -> CGRect {
        // 这里应该返回实际的全局frame，但由于我们在FilmstripView中已经处理了frame计算
        // 这个方法主要用于PhotoStackView的target frame
        return CGRect(x: UIScreen.main.bounds.midX - 150, y: 100, width: 300, height: 200)
    }
}

// MARK: - 处理流程控制
extension ProcessingView {
    /// 开始处理流程
    private func startProcessingFlow() {
        if viewModel.uploadStatus == .pending {
            viewModel.uploadVideo()
        }
    }
    
    /// 处理上传状态变化
    private func handleUploadStatusChange(_ newStatus: UploadStatus) {
        switch newStatus {
        case .completed:
            // 上传完成后开始基础帧提取
            if let taskId = viewModel.uploadedTaskId {
                currentStage = .baseFrameExtraction
                Task {
                    await baseFrameVM.extractBaseFrames(taskId: taskId)
                }
            }
        case .failed:
            // 处理失败情况
            break
        default:
            break
        }
    }
    
    /// 处理基础帧提取状态变化
    private func handleBaseFrameStatusChange(_ newStatus: BaseFrameExtractionStatus) {
        switch newStatus {
        case .completed:
            // 基础帧提取完成后进入下一阶段
            currentStage = .keyFrameExtraction
            // 这里可以触发关键帧提取
            DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                currentStage = .completed
                DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
                    navigateToResults = true
                }
            }
        case .failed(let error):
            // 处理错误
            print("基础帧提取失败: \(error)")
        default:
            break
        }
    }
    
    /// 获取当前进度
    private func getCurrentProgress() -> Double {
        switch currentStage {
        case .upload:
            return viewModel.uploadProgress
        case .baseFrameExtraction:
            return baseFrameVM.progress * 0.14 + 0.14 // 基础帧提取占14%
        case .keyFrameExtraction:
            return 0.42
        case .storyGeneration:
            return 0.57
        case .styleProcessing:
            return 0.71
        case .comicGeneration:
            return 0.85
        case .completed:
            return 1.0
        }
    }
    
    /// 获取当前状态
    private func getCurrentStatus() -> UploadStatus {
        switch currentStage {
        case .upload:
            return viewModel.uploadStatus
        case .baseFrameExtraction:
            return .processing
        case .keyFrameExtraction, .storyGeneration, .styleProcessing, .comicGeneration:
            return .processing
        case .completed:
            return .completed
        }
    }
}

// MARK: - Preview
struct ProcessingView_Previews: PreviewProvider {
    static var previews: some View {
        let viewModel = VideoUploadViewModel()
        viewModel.uploadStatus = .processing
        viewModel.uploadProgress = 0.5
        return ProcessingView(viewModel: viewModel)
    }
}
