import SwiftUI

struct ProcessingView: View {
    @ObservedObject var viewModel: VideoUploadViewModel
    @State private var navigateToResults = false
    
    var body: some View {
        NavigationStack {
            ZStack {
                // 背景渐变
                LinearGradient(
                    gradient: Gradient(colors: [
                        Color.black.opacity(0.9),
                        Color.gray.opacity(0.3)
                    ]),
                    startPoint: .top,
                    endPoint: .bottom
                )
                .ignoresSafeArea()
                
                VStack(spacing: 40) {
                    // 标题
                    VStack(spacing: 8) {
                        Text("正在处理您的视频")
                            .font(.title.bold())
                            .foregroundColor(.white)
                        
                        Text("AI正在将您的视频转换为漫画风格...")
                            .font(.body)
                            .foregroundColor(.white.opacity(0.7))
                    }
                    
                    // 胶片动画区域
                    ProcessingFilmStripView(
                        status: viewModel.uploadStatus,
                        progress: viewModel.uploadProgress
                    )
                    .frame(height: 200)
                    
                    // 状态信息
                    VStack(spacing: 20) {
                        statusIndicator
                        statusText
                        
                        if viewModel.uploadStatus == .uploading {
                            ProgressView(value: viewModel.uploadProgress)
                                .progressViewStyle(LinearProgressViewStyle())
                                .tint(.blue)
                                .scaleEffect(x: 1, y: 2, anchor: .center)
                                .padding(.horizontal, 40)
                        }
                    }
                    
                    Spacer()
                }
                .padding(.top, 60)
            }
        }
        .onAppear {
            if viewModel.uploadStatus == .pending {
                viewModel.uploadVideo()
            }
        }
        .onChange(of: viewModel.uploadStatus) { _, newStatus in
            if newStatus == .completed {
                DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
                    navigateToResults = true
                }
            }
        }
        .background(
            Group {
                if let result = viewModel.comicResult {
                    NavigationLink(
                        destination: OpenResultsView(comicResult: result),
                        isActive: $navigateToResults
                    ) {
                        EmptyView()
                    }
                }
            }
        )
    }
    
    // MARK: - 状态指示器
    private var statusIndicator: some View {
        ZStack {
            switch viewModel.uploadStatus {
            case .pending:
                Image(systemName: "clock")
                    .font(.system(size: 40))
                    .foregroundColor(.yellow)
                    .symbolEffect(.pulse)
                
            case .uploading:
                ZStack {
                    Circle()
                        .stroke(lineWidth: 4)
                        .opacity(0.3)
                        .foregroundColor(.blue)
                    
                    Circle()
                        .trim(from: 0.0, to: CGFloat(viewModel.uploadProgress))
                        .stroke(style: StrokeStyle(lineWidth: 4, lineCap: .round, lineJoin: .round))
                        .foregroundColor(.blue)
                        .rotationEffect(Angle(degrees: 270))
                        .animation(.linear(duration: 0.3), value: viewModel.uploadProgress)
                    
                    Text("\(Int(viewModel.uploadProgress * 100))%")
                        .font(.caption.bold())
                        .foregroundColor(.white)
                }
                .frame(width: 60, height: 60)
                
            case .processing:
                Image(systemName: "brain.head.profile")
                    .font(.system(size: 40))
                    .foregroundColor(.purple)
                    .symbolEffect(.variableColor)
                
            case .completed:
                Image(systemName: "checkmark.circle.fill")
                    .font(.system(size: 40))
                    .foregroundColor(.green)
                    .symbolEffect(.bounce)
                
            case .failed:
                Image(systemName: "xmark.circle.fill")
                    .font(.system(size: 40))
                    .foregroundColor(.red)
                    .symbolEffect(.bounce)
            }
        }
    }
    
    // MARK: - 状态文本
    private var statusText: some View {
        VStack(spacing: 8) {
            switch viewModel.uploadStatus {
            case .pending:
                Text("准备中...")
                    .font(.title3.bold())
                    .foregroundColor(.white)
                
            case .uploading:
                Text("正在上传视频")
                    .font(.title3.bold())
                    .foregroundColor(.white)
                
            case .processing:
                Text("AI正在处理")
                    .font(.title3.bold())
                    .foregroundColor(.white)
                
            case .completed:
                Text("处理完成！")
                    .font(.title3.bold())
                    .foregroundColor(.green)
                
            case .failed:
                Text("处理失败")
                    .font(.title3.bold())
                    .foregroundColor(.red)
            }
            
            // 子状态描述
            if viewModel.uploadStatus == .uploading {
                Text("正在上传... \(Int(viewModel.uploadProgress * 100))%")
                    .font(.body)
                    .foregroundColor(.white.opacity(0.7))
            } else if viewModel.uploadStatus == .processing {
                Text("这可能需要几分钟时间")
                    .font(.body)
                    .foregroundColor(.white.opacity(0.7))
            }
        }
    }
}

// MARK: - 处理过程中的胶片动画视图
struct ProcessingFilmStripView: View {
    let status: UploadStatus
    let progress: Double
    
    @State private var offset: CGFloat = 0
    @State private var isAnimating = false
    
    private let imageCount = 6
    private let imageSize: CGFloat = 60
    private let spacing: CGFloat = 15
    
    var body: some View {
        GeometryReader { geometry in
            VStack(spacing: 10) {
                // 胶片容器
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: spacing) {
                        ForEach(0..<imageCount * 3, id: \.self) { index in
                            let actualIndex = index % imageCount
                            filmItem(for: actualIndex, globalIndex: index)
                        }
                    }
                    .padding(.horizontal, spacing)
                    .offset(x: offset)
                }
                .disabled(true)
                
                // 进度指示器
                HStack(spacing: 8) {
                    ForEach(0..<imageCount, id: \.self) { index in
                        Circle()
                            .fill(getProgressColor(for: index))
                            .frame(width: 8, height: 8)
                    }
                }
            }
        }
        .onAppear {
            startAnimation()
        }
        .onChange(of: status) { _, newStatus in
            if newStatus == .completed {
                stopAnimation()
            }
        }
    }
    
    // MARK: - 胶片项
    private func filmItem(for index: Int, globalIndex: Int) -> some View {
        VStack(spacing: 4) {
            // 胶片齿孔
            HStack(spacing: 2) {
                ForEach(0..<2) { _ in
                    Circle()
                        .fill(Color.white.opacity(0.6))
                        .frame(width: 4, height: 4)
                }
            }
            
            // 图片
            ZStack {
                RoundedRectangle(cornerRadius: 6)
                    .fill(getBackgroundColor(for: index))
                    .frame(width: imageSize, height: imageSize)
                
                Image(systemName: getImageName(for: index))
                    .resizable()
                    .scaledToFit()
                    .foregroundColor(getImageColor(for: index))
                    .frame(width: imageSize * 0.6, height: imageSize * 0.6)
                
                // 处理状态覆盖层
                if status == .processing {
                    RoundedRectangle(cornerRadius: 6)
                        .fill(Color.black.opacity(0.3))
                        .frame(width: imageSize, height: imageSize)
                    
                    ProgressView()
                        .tint(.white)
                        .scaleEffect(0.8)
                }
            }
            
            // 胶片齿孔
            HStack(spacing: 2) {
                ForEach(0..<2) { _ in
                    Circle()
                        .fill(Color.white.opacity(0.6))
                        .frame(width: 4, height: 4)
                }
            }
        }
    }
    
    // MARK: - 动画控制
    private func startAnimation() {
        let totalWidth = CGFloat(imageCount) * (imageSize + spacing) + spacing
        
        withAnimation(
            .linear(duration: getAnimationDuration())
            .repeatForever(autoreverses: false)
        ) {
            offset = -totalWidth
            isAnimating = true
        }
    }
    
    private func stopAnimation() {
        isAnimating = false
    }
    
    private func getAnimationDuration() -> Double {
        switch status {
        case .uploading:
            return 15.0
        case .processing:
            return 25.0
        default:
            return 20.0
        }
    }
    
    // MARK: - 辅助方法
    private func getImageName(for index: Int) -> String {
        let symbols = ["photo", "photo.fill", "camera", "video", "film", "doc"]
        return symbols[index % symbols.count]
    }
    
    private func getImageColor(for index: Int) -> Color {
        let colors: [Color] = [.blue, .green, .orange, .pink, .purple, .yellow]
        return colors[index % colors.count]
    }
    
    private func getBackgroundColor(for index: Int) -> Color {
        let progress = CGFloat(index) / CGFloat(imageCount)
        let currentProgress = CGFloat(progress)
        
        if status == .uploading && currentProgress <= progress {
            return Color.blue.opacity(0.3)
        } else if status == .processing {
            return Color.purple.opacity(0.3)
        } else if status == .completed {
            return Color.green.opacity(0.3)
        }
        
        return Color.white.opacity(0.1)
    }
    
    private func getProgressColor(for index: Int) -> Color {
        let progress = CGFloat(index) / CGFloat(imageCount)
        let currentProgress = CGFloat(progress)
        
        switch status {
        case .uploading:
            return currentProgress <= progress ? .blue : .gray.opacity(0.3)
        case .processing:
            return currentProgress <= progress ? .purple : .gray.opacity(0.3)
        case .completed:
            return .green
        case .failed:
            return .red
        default:
            return .gray.opacity(0.3)
        }
    }
}

// MARK: - 预览
struct ProcessingView_Previews: PreviewProvider {
    static var previews: some View {
        Group {
            // 上传中状态
            ProcessingView(viewModel: {
                let vm = VideoUploadViewModel()
                vm.uploadStatus = .uploading
                vm.uploadProgress = 0.6
                return vm
            }())
            .previewDisplayName("上传中")
            
            // 处理中状态
            ProcessingView(viewModel: {
                let vm = VideoUploadViewModel()
                vm.uploadStatus = .processing
                return vm
            }())
            .previewDisplayName("处理中")
            
            // 完成状态
            ProcessingView(viewModel: {
                let vm = VideoUploadViewModel()
                vm.uploadStatus = .completed
                return vm
            }())
            .previewDisplayName("已完成")
            
            // 失败状态
            ProcessingView(viewModel: {
                let vm = VideoUploadViewModel()
                vm.uploadStatus = .failed
                return vm
            }())
            .previewDisplayName("失败")
        }
    }
}
