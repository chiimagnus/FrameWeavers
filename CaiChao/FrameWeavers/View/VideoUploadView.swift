import SwiftUI
import PhotosUI

struct VideoUploadView: View {
    @StateObject private var viewModel = VideoUploadViewModel()
    @State private var selectedItem: PhotosPickerItem?
    
    var body: some View {
        NavigationStack {
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

                if viewModel.selectedVideo == nil {
                    // 选择视频界面
                    PhotosPicker(
                        selection: $selectedItem,
                        matching: .videos,
                        photoLibrary: .shared()
                    ) {
                        VStack(spacing: 12) {
                            Image(systemName: "video.badge.plus")
                                .font(.system(size: 60))
                            Text("选择视频")
                                .font(.title2)
                            Text("时长需不超过5分钟")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                        .background(Color.gray.opacity(0.1))
                        .cornerRadius(12)
                    }
                    .onChange(of: selectedItem) { newItem in
                        Task {
                            if let data = try? await newItem?.loadTransferable(type: Data.self),
                               let url = saveVideoData(data) {
                                await MainActor.run {
                                    viewModel.selectVideo(url)
                                }
                            }
                        }
                    }
                } else {
                    // 已选择视频界面
                    VStack(spacing: 20) {
                        VStack(spacing: 12) {
                            Image(systemName: "video.fill")
                                .font(.system(size: 40))
                            Text(viewModel.selectedVideo?.lastPathComponent ?? "")
                                .font(.headline)
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
                                ProgressView()
                                Text("AI处理中，请稍候...")
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
                            selectedItem = nil
                        }
                        .foregroundColor(.red)
                    }
                    .padding()
                }
            }
            .padding()
            .navigationTitle("视频转连环画")
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

struct ComicResultView: View {
    let comicResult: ComicResult
    
    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                Text("连环画生成完成！")
                    .font(.title2.bold())
                
                ForEach(comicResult.panels) { panel in
                    VStack(alignment: .leading, spacing: 8) {
                        AsyncImage(url: URL(string: panel.imageUrl)) { image in
                            image
                                .resizable()
                                .aspectRatio(contentMode: .fit)
                        } placeholder: {
                            ProgressView()
                                .frame(height: 200)
                        }
                        .frame(maxWidth: .infinity)
                        .background(Color.gray.opacity(0.1))
                        .cornerRadius(8)
                        
                        if let narration = panel.narration {
                            Text(narration)
                                .font(.body)
                                .padding(.horizontal)
                        }
                    }
                }
                
                VStack(alignment: .leading, spacing: 12) {
                    Text("互动问题")
                        .font(.headline)
                    
                    ForEach(comicResult.finalQuestions, id: \.self) { question in
                        Text("• \(question)")
                            .font(.body)
                    }
                }
                .padding()
            }
            .padding()
        }
        .navigationTitle("连环画结果")
    }
}
