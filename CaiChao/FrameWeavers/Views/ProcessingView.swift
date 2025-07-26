import SwiftUI

/// 处理视图 - 遵循MVVM架构的主视图
struct ProcessingView: View {
    @Environment(\.dismiss) private var dismiss
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
                    // 始终显示胶片画廊视图
                    filmGalleryView
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

// MARK: - Subviews

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

            // 统一的进度条显示，在所有等待状态下都显示
            ProcessingLoadingView(progress: viewModel.uploadProgress, status: viewModel.uploadStatus)

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

// MARK: - Preview

struct ProcessingView_Previews: PreviewProvider {
    static var previews: some View {
        let viewModel = VideoUploadViewModel()
        viewModel.uploadStatus = .processing
        viewModel.uploadProgress = 0.5
        return ProcessingView(viewModel: viewModel)
    }
}
