import SwiftUI
import PhotosUI

struct WelcomeView: View {
    @Binding var selectedItems: [PhotosPickerItem]
    
    var body: some View {
        VStack(spacing: 40) {
            Image("icon-home")
                .resizable()
                .frame(width: 100, height: 100)
                .shadow(radius: 10)

            TypewriterView(
                text: """
                有些记忆，
                沉在手机深处，
                无人翻阅，也无人倾听。
                我们捡起那些画面，
                像织布的人，
                一帧帧织成故事。
                不必剪辑，
                也无需文字，
                只要一段视频，
                我便替你开口。

                帧织者，
                让回忆再次发生。
                """,
                typeSpeed: 0.08
            )
            .font(.custom("Kaiti SC", size: 16))
            .fontWeight(.bold)
            .multilineTextAlignment(.center)
            .foregroundColor(Color(hex: "#2F2617"))
            .lineSpacing(15)

            PhotosPicker(
                selection: $selectedItems,
                maxSelectionCount: 5,  // 最多选择5个视频
                matching: .videos,
                photoLibrary: .shared()
            ) {
                ZStack {
                    Image("button-import")
                        .resizable()
                        .aspectRatio(contentMode: .fit)
                        .frame(width: 250, height: 44)
                    
                    Text("开启一段故事织造")
                        .font(.custom("Kaiti SC", size: 24))
                        .fontWeight(.bold)
                        .foregroundColor(Color(hex: "#855C23"))
                }
            }

            Text("""
            最多上传5段3分钟内的视频
            选择有故事的片段效果更佳
            """)
                .font(.custom("Kaiti SC", size: 12))
                .fontWeight(.bold)
                .multilineTextAlignment(.center)
                .foregroundColor(Color(hex: "#2F2617"))
                .tracking(1.2)
                .lineSpacing(10)
        }
        .padding()
    }
}

struct VideoUploadView: View {
    @StateObject private var viewModel = VideoUploadViewModel()
    @State private var selectedItems: [PhotosPickerItem] = []
    @State private var navigateToStyleSelection = false
    
    var body: some View {
        NavigationStack {
            ZStack {
                // 背景图片
                Image("背景")
                    .resizable()
                    .scaledToFill()
                    .ignoresSafeArea()
                
                VStack(spacing: 20) {
                    WelcomeView(selectedItems: $selectedItems)
                        .onChange(of: selectedItems) { _, newItems in
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
                                    // 选择视频后自动跳转到选择风格界面
                                    if !videoURLs.isEmpty {
                                        navigateToStyleSelection = true
                                    }
                                }
                            }
                        }
                    
                    // 导航到选择风格界面，传递视频URL
                    NavigationLink(
                        destination: SelectStyleView(selectedVideos: viewModel.selectedVideos),
                        isActive: $navigateToStyleSelection
                    ) {
                        EmptyView()
                    }
                }
                .padding()
            }
            .background(Color(red: 0.81, green: 0.74, blue: 0.66))
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
