import SwiftUI
import PhotosUI

struct VideoUploadView: View {
    @StateObject private var viewModel = VideoUploadViewModel()
    @State private var selectedItems: [PhotosPickerItem] = []
    
    var body: some View {
        NavigationStack {
            ZStack {
                // 背景图片
                Image("背景")
                    .resizable()
                    .scaledToFill()
                    .ignoresSafeArea()
                
                VStack(spacing: 20) {
                    // 简单的模式切换
                    HStack {
                        Text("模式:")
                            .font(.caption)

                        Picker("上传模式", selection: $viewModel.uploadMode) {
                            Text("Mock").tag(UploadMode.mock)
                            Text("真实").tag(UploadMode.real)
                        }
                        .pickerStyle(.segmented)

                        Spacer()
                    }
                    .padding(.horizontal)

                if viewModel.selectedVideos.isEmpty {
                    // 选择视频界面
                    PhotosPicker(
                        selection: $selectedItems,
                        maxSelectionCount: 5,  // 最多选择5个视频
                        matching: .videos,
                        photoLibrary: .shared()
                    ) {
                        VStack(spacing: 12) {
                            Image(systemName: "video.badge.plus")
                                .font(.system(size: 60))
                            Text("选择视频")
                                .font(.title2)
                            Text("最多选择5个视频，每个时长不超过5分钟")
                                .font(.caption)
                                .foregroundColor(.secondary)
                                .multilineTextAlignment(.center)
                        }
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                        .background(Color.gray.opacity(0.1))
                        .cornerRadius(12)
                    }
                    .onChange(of: selectedItems) { newItems in
                        Task {
                            var videoURLs: [URL] = []

                            for item in newItems {
                                if let data = try? await item.loadTransferable(type: Data.self),
                                   let url = saveVideoData(data) {
                                    videoURLs.append(url)
                                }
                            }

                            await MainActor.run {
                                viewModel.selectVideos(videoURLs)
                            }
                        }
                    }
                } else {
                    // 已选择视频界面
                    VStack(spacing: 20) {
                        // 显示选中的视频列表
                        VStack(spacing: 8) {
                            HStack {
                                Image(systemName: "video.fill")
                                    .font(.system(size: 20))
                                Text("已选择 \(viewModel.selectedVideos.count) 个视频")
                                    .font(.headline)
                                Spacer()
                            }

                            ForEach(Array(viewModel.selectedVideos.enumerated()), id: \.offset) { index, url in
                                HStack {
                                    Text("\(index + 1). \(url.lastPathComponent)")
                                        .font(.caption)
                                        .lineLimit(1)
                                    Spacer()
                                    Button("删除") {
                                        viewModel.removeVideo(at: index)
                                    }
                                    .font(.caption)
                                    .foregroundColor(.red)
                                }
                                .padding(.horizontal, 8)
                            }
                        }
                        .padding()
                        .background(Color.blue.opacity(0.1))
                        .cornerRadius(12)
                        
                        if let error = viewModel.errorMessage {
                            Text(error)
                                .foregroundColor(.red)
                                .font(.callout)
                        }
                        
                        if viewModel.uploadStatus == .pending {
                            Button("开始上传") {
                                viewModel.uploadVideo()
                            }
                            .buttonStyle(.borderedProminent)
                            .disabled(viewModel.errorMessage != nil)
                        }
                        
                        if viewModel.uploadStatus == .uploading {
                            VStack(spacing: 12) {
                                ProgressView(value: viewModel.uploadProgress)
                                Text("上传中... \(Int(viewModel.uploadProgress * 100))%")

                                Button("取消上传") {
                                    viewModel.cancelUpload()
                                }
                                .foregroundColor(.red)
                                .font(.caption)
                            }
                        }

                        if viewModel.uploadStatus == .processing {
                            VStack(spacing: 12) {
                                ProgressView(value: viewModel.uploadProgress)
                                Text("AI处理中... \(Int(viewModel.uploadProgress * 100))%")

                                Button("取消处理") {
                                    viewModel.cancelUpload()
                                }
                                .foregroundColor(.red)
                                .font(.caption)
                            }
                        }
                        
                        if viewModel.uploadStatus == .completed {
                            NavigationLink("查看结果") {
                                ComicResultView(comicResult: viewModel.comicResult!)
                            }
                            .buttonStyle(.borderedProminent)
                        }
                        
                        Button("重新选择") {
                            viewModel.reset()
                            selectedItems = []
                        }
                        .foregroundColor(.red)
                    }
                    .padding()
                }
            }
            .padding()
            .navigationTitle("视频转连环画")
            }
            .background(Color.clear) // 确保背景透明
        }
    }
    
    private func saveVideoData(_ data: Data) -> URL? {
        let tempDir = FileManager.default.temporaryDirectory
        let fileName = "temp_video_\(UUID().uuidString).mp4"
        let fileURL = tempDir.appendingPathComponent(fileName)
        
        do {
            try data.write(to: fileURL)
            return fileURL
        } catch {
            print("保存视频失败: \(error)")
            return nil
        }
    }
}

