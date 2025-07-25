import SwiftUI

/// 处理视图 - 遵循MVVM架构的主视图
struct ProcessingView: View {
    @ObservedObject var viewModel: VideoUploadViewModel
    @State private var navigateToResults = false
    @StateObject private var galleryViewModel = ProcessingGalleryViewModel()
    @State private var frames: [String: CGRect] = [:]
    @Namespace private var galleryNamespace
    
    // 定时器
    let scrollTimer = Timer.publish(every: 3, on: .main, in: .common).autoconnect()
    let jumpTimer = Timer.publish(every: 4, on: .main, in: .common).autoconnect()
    
    var body: some View {
        NavigationStack {
            ZStack {
                // 背景色
                Color(red: 0.91, green: 0.88, blue: 0.83).ignoresSafeArea()
                
                VStack(spacing: 40) {
                    // 根据上传状态显示不同内容
                    if viewModel.uploadStatus == .processing {
                        // 显示胶片动画
                        filmGalleryView
                    } else {
                        // 显示传统进度界面
                        traditionalProgressView
                    }
                }
                .padding(.vertical, 50)
                
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
            if viewModel.uploadStatus == .processing {
                galleryViewModel.currentScrollIndex += 1
            }
        }
        .onReceive(jumpTimer) { _ in
            if viewModel.uploadStatus == .processing {
                withAnimation(.easeInOut(duration: 1.2)) {
                    galleryViewModel.triggerJumpAnimation(from: frames)
                }
            }
        }
        .onAppear {
            if viewModel.uploadStatus == .pending {
                viewModel.uploadVideo()
            }
        }
        .onChange(of: viewModel.uploadStatus) { _, newStatus in
            if newStatus == .completed {
                DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
                    navigateToResults = true
                }
            }
        }
        .navigationDestination(isPresented: $navigateToResults) {
            if let result = viewModel.comicResult {
                OpenResultsView(comicResult: result)
            }
        }
    }
}

// MARK: - Subviews

extension ProcessingView {
    /// 胶片画廊视图
    private var filmGalleryView: some View {
        VStack(spacing: 40) {
            PhotoStackView(mainImageName: galleryViewModel.mainImageName, namespace: galleryNamespace)
                .anchorPreference(key: FramePreferenceKey.self, value: .bounds) { anchor in
                    return ["photoStackTarget": self.frames(from: anchor)]
                }
            
            FilmstripView(galleryViewModel: galleryViewModel, namespace: galleryNamespace)
            
            ProcessingLoadingView(progress: viewModel.uploadProgress, status: viewModel.uploadStatus)
            
            Spacer()
        }
    }
    
    /// 传统进度视图
    private var traditionalProgressView: some View {
        VStack(spacing: 30) {
            if viewModel.uploadStatus == .pending {
                ProgressView()
                Text("准备中...")
            } else if viewModel.uploadStatus == .uploading {
                ProgressView(value: viewModel.uploadProgress)
                Text("上传中... \(Int(viewModel.uploadProgress * 100))%")
            } else if viewModel.uploadStatus == .completed {
                VStack {
                    Text("处理完成！")
                    Button("查看结果") {
                        navigateToResults = true
                    }
                }
            } else if viewModel.uploadStatus == .failed {
                Text("处理失败，请重试")
            }
        }
        .font(.title2)
        .padding()
    }
    
    /// Helper to convert anchor to global frame
    private func frames(from anchor: Anchor<CGRect>) -> CGRect {
        return CGRect.zero // 简化处理
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
