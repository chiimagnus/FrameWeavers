import SwiftUI

struct ProcessingView: View {
    @ObservedObject var viewModel: VideoUploadViewModel
    @State private var navigateToResults = false
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 30) {
                if viewModel.uploadStatus == .pending {
                    ProgressView()
                    Text("准备中...")
                } else if viewModel.uploadStatus == .uploading {
                    ProgressView(value: viewModel.uploadProgress)
                    Text("上传中... \(Int(viewModel.uploadProgress * 100))%")
                } else if viewModel.uploadStatus == .processing {
                    ProgressView()
                    Text("AI处理中...")
                } else if viewModel.uploadStatus == .completed {
                    VStack {
                        Text("处理完成！")
                        if let result = viewModel.comicResult {
                            NavigationLink("查看结果", destination: OpenResultsView(comicResult: result))
                        }
                    }
                } else if viewModel.uploadStatus == .failed {
                    Text("处理失败，请重试")
                }
            }
            .font(.title2)
            .padding()
        }
        .onAppear {
            // 如果处于pending状态，自动开始上传
            if viewModel.uploadStatus == .pending {
                viewModel.uploadVideo()
            }
        }
        .onChange(of: viewModel.uploadStatus) { _, newStatus in
            if newStatus == .completed {
                // 延迟1秒后自动跳转
                DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
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
}

struct ProcessingView_Previews: PreviewProvider {
    static var previews: some View {
        let viewModel = VideoUploadViewModel()
        viewModel.uploadStatus = .uploading
        viewModel.uploadProgress = 0.5
        return ProcessingView(viewModel: viewModel)
    }
}
