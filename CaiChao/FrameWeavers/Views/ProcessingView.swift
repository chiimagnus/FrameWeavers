import SwiftUI

struct ProcessingView: View {
    @ObservedObject var viewModel: VideoUploadViewModel
    
    var body: some View {
        VStack {
            if viewModel.uploadStatus == .uploading {
                ProgressView(value: viewModel.uploadProgress)
                Text("上传中... \(Int(viewModel.uploadProgress * 100))%")
            } else if viewModel.uploadStatus == .processing {
                ProgressView()
                Text("AI处理中...")
            } else if viewModel.uploadStatus == .completed {
                Text("处理完成")
            }
        }
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
