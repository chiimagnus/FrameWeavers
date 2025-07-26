import SwiftUI

/// 处理视图 - 遵循MVVM架构的主视图
struct ProcessingView: View {
    @Environment(\.dismiss) private var dismiss
    @ObservedObject var viewModel: VideoUploadViewModel
    @State private var navigateToResults = false
    @StateObject private var galleryViewModel = ProcessingGalleryViewModel()
    @State private var frames: [String: CGRect] = [:]
    @Namespace private var galleryNamespace
    @State private var showResultButton = false
    
    // 移除定时器，现在使用持续滚动动画
    
    var body: some View {
        NavigationStack {
            ZStack {
                // 背景色
                Color(red: 0.91, green: 0.88, blue: 0.83).ignoresSafeArea()
                
                VStack(spacing: 40) {
                    // 在所有状态下都显示胶片动画
                    if viewModel.uploadStatus != .failed {
                        // 显示胶片动画
                        filmGalleryView
                    } else {
                        // 只有失败状态显示错误信息
                        failedView
                    }
                }
                .padding(.vertical, 50)
                
                // 飞行图片覆盖层 - 使用独立的FlyingImageOverlay组件
                FlyingImageOverlay(
                    flyingImageInfo: galleryViewModel.flyingImageInfo,
                    namespace: galleryNamespace
                )
            }
        }
        .onPreferenceChange(FramePreferenceKey.self) { value in
            self.frames.merge(value, uniquingKeysWith: { $1 })
        }
        // 移除定时器监听，现在胶片自动持续滚动
        .onAppear {
            if viewModel.uploadStatus == .pending {
                viewModel.uploadVideo()
            }
        }
        .onChange(of: viewModel.uploadStatus) { _, newStatus in
            if newStatus == .completed {
                // 1秒后自动跳转到结果页面
                DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
                    navigateToResults = true
                }

                // 5秒后显示查看结果按钮（作为备用选项）
                DispatchQueue.main.asyncAfter(deadline: .now() + 5) {
                    withAnimation(.easeInOut(duration: 0.5)) {
                        showResultButton = true
                    }
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

            FilmstripView(galleryViewModel: galleryViewModel, namespace: galleryNamespace)

            // 统一的进度条显示，在所有等待状态下都显示
            ProcessingLoadingView(progress: viewModel.uploadProgress, status: viewModel.uploadStatus)

            // 在completed状态下5秒后显示查看结果按钮
            if viewModel.uploadStatus == .completed && showResultButton {
                Button(action: {
                    navigateToResults = true
                }) {
                    Text("查看结果")
                        .font(.title2)
                        .fontWeight(.medium)
                        .foregroundColor(.white)
                        .frame(width: 200, height: 50)
                        .background(Color(hex: "#2F2617"))
                        .cornerRadius(25)
                }
                .padding(.top, 20)
                .transition(.opacity.combined(with: .scale))
            }

            Spacer()
        }
    }
    
    /// 失败状态视图
    private var failedView: some View {
        VStack(spacing: 30) {
            Text("处理失败，请重试")
                .font(.title2)
                .foregroundColor(.red)

            Button(action: {
                dismiss()
            }) {
                Text("返回")
                    .font(.title2)
                    .fontWeight(.medium)
                    .foregroundColor(.white)
                    .frame(width: 200, height: 50)
                    .background(Color(hex: "#2F2617"))
                    .cornerRadius(25)
            }
        }
        .padding()
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
