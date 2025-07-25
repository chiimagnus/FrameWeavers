import SwiftUI

// MARK: - Data Models and PreferenceKeys

// 用于在视图树中向上传递视图的Frame信息
struct FramePreferenceKey: PreferenceKey {
    static var defaultValue: [String: CGRect] = [:]
    static func reduce(value: inout [String : CGRect], nextValue: () -> [String : CGRect]) {
        value.merge(nextValue(), uniquingKeysWith: { $1 })
    }
}

// 飞行图片的信息
struct FlyingImageInfo: Identifiable {
    let id: String
    let sourceFrame: CGRect
}

// MARK: - Processing ViewModel Extension

extension VideoUploadViewModel {
    // 模拟图片数据，实际项目中可以从视频帧中提取
    var mockImageNames: [String] {
        return ["photo1", "photo2", "photo3", "photo4", "photo5", "photo6", "photo7", "photo8"]
    }

    // 为了无缝滚动，复制数组
    var loopedImageNames: [String] {
        let images = mockImageNames
        return images + images + images
    }
}

// MARK: - Processing Gallery ViewModel

class ProcessingGalleryViewModel: ObservableObject {
    @Published var mainImageName: String = "photo1"
    @Published var flyingImageInfo: FlyingImageInfo?
    @Published var hideSourceImageId: String?
    @Published var currentScrollIndex: Int = 0

    private let imageNames = ["photo1", "photo2", "photo3", "photo4", "photo5", "photo6", "photo7", "photo8"]

    var loopedImageNames: [String] {
        imageNames + imageNames + imageNames
    }

    init() {
        mainImageName = imageNames.first ?? ""
    }

    /// 触发一次图片跳跃动画
    func triggerJumpAnimation(from frames: [String: CGRect]) {
        guard let centerImageId = findCenterImageId(from: frames),
              let targetFrame = frames["photoStackTarget"] else { return }

        if centerImageId == mainImageName { return }

        guard let sourceFrame = frames[centerImageId] else { return }

        self.flyingImageInfo = FlyingImageInfo(id: centerImageId, sourceFrame: sourceFrame)
        self.hideSourceImageId = centerImageId

        DispatchQueue.main.asyncAfter(deadline: .now() + 1.2) {
            self.mainImageName = centerImageId
            self.flyingImageInfo = nil
            self.hideSourceImageId = nil
        }
    }

    /// 根据Frame信息计算当前在中心的图片ID
    private func findCenterImageId(from frames: [String: CGRect]) -> String? {
        let screenCenter = UIScreen.main.bounds.midX
        var closestImageId: String?
        var minDistance = CGFloat.infinity

        for (id, frame) in frames where imageNames.contains(id) {
            let distance = abs(frame.midX - screenCenter)
            if distance < minDistance {
                minDistance = distance
                closestImageId = id
            }
        }
        return closestImageId
    }
}

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

    // MARK: - 胶片画廊视图
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

    // MARK: - 传统进度视图
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

    // Helper to convert anchor to global frame
    private func frames(from anchor: Anchor<CGRect>) -> CGRect {
        return self.frames["scrollToIndex", default: .zero]
    }
}

// MARK: - Subviews

struct PhotoStackView: View {
    let mainImageName: String
    let namespace: Namespace.ID

    var body: some View {
        ZStack {
            // 背景卡片
            RoundedRectangle(cornerRadius: 12)
                .fill(Color.white.opacity(0.6))
                .frame(width: 310, height: 210)
                .rotationEffect(.degrees(5))

            RoundedRectangle(cornerRadius: 12)
                .fill(Color.white.opacity(0.8))
                .frame(width: 310, height: 210)
                .rotationEffect(.degrees(-4))

            // 主图卡片
            ZStack {
                if !mainImageName.isEmpty {
                    Image(mainImageName)
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                        .matchedGeometryEffect(id: mainImageName, in: namespace)
                }
            }
            .frame(width: 300, height: 200)
            .clipShape(RoundedRectangle(cornerRadius: 8))
            .background(
                RoundedRectangle(cornerRadius: 8).fill(.white)
            )
            .shadow(color: .black.opacity(0.2), radius: 10, y: 5)
            .rotationEffect(.degrees(1))

            // 胶带
            Rectangle()
                .fill(Color.white.opacity(0.4))
                .frame(width: 100, height: 25)
                .rotationEffect(.degrees(-4))
                .offset(y: -110)
        }
        .frame(height: 250)
    }
}

struct FilmstripView: View {
    @ObservedObject var galleryViewModel: ProcessingGalleryViewModel
    let namespace: Namespace.ID

    var body: some View {
        ScrollViewReader { proxy in
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 10) {
                    ForEach(galleryViewModel.loopedImageNames.indices, id: \.self) { index in
                        let imageName = galleryViewModel.loopedImageNames[index]
                        FilmstripFrameView(
                            imageName: imageName,
                            isHidden: galleryViewModel.hideSourceImageId == imageName,
                            namespace: namespace
                        )
                        .id(index)
                        .anchorPreference(key: FramePreferenceKey.self, value: .bounds) { anchor in
                            return [imageName: proxy[anchor]]
                        }
                    }
                }
                .padding(.horizontal)
            }
            .frame(height: 100)
            .background(Color.black.opacity(0.8))
            .overlay(sprocketHoles)
            .onChange(of: galleryViewModel.currentScrollIndex) { newIndex in
                withAnimation(.easeInOut(duration: 3.0)) {
                    proxy.scrollTo(newIndex, anchor: .center)
                }
                // 无限循环逻辑
                if newIndex >= galleryViewModel.loopedImageNames.count - 8 {
                    galleryViewModel.currentScrollIndex = 8
                    proxy.scrollTo(galleryViewModel.currentScrollIndex, anchor: .center)
                }
            }
        }
    }

    // 胶片齿孔
    var sprocketHoles: some View {
        VStack {
            HStack(spacing: 12) { ForEach(0..<20) { _ in Rectangle().frame(width: 4, height: 4) } }
            Spacer()
            HStack(spacing: 12) { ForEach(0..<20) { _ in Rectangle().frame(width: 4, height: 4) } }
        }
        .foregroundColor(.white.opacity(0.3))
        .padding(.vertical, 6)
    }
}

struct FilmstripFrameView: View {
    let imageName: String
    let isHidden: Bool
    let namespace: Namespace.ID

    var body: some View {
        ZStack {
            if !isHidden {
                Image(imageName)
                    .resizable()
                    .aspectRatio(contentMode: .fill)
                    .matchedGeometryEffect(id: imageName, in: namespace, isSource: true)
            } else {
                Rectangle().fill(.clear)
            }
        }
        .frame(width: 120, height: 80)
        .clipShape(RoundedRectangle(cornerRadius: 4))
        .opacity(isHidden ? 0 : 1)
    }
}

struct ProcessingLoadingView: View {
    let progress: Double
    let status: UploadStatus

    var body: some View {
        VStack(spacing: 15) {
            Text(statusText)
                .font(.system(size: 16))
                .foregroundColor(.gray)

            ZStack(alignment: .leading) {
                Capsule().fill(Color.black.opacity(0.1))
                Capsule()
                    .fill(Color.gray.opacity(0.8))
                    .frame(width: 200 * CGFloat(progress))
            }
            .frame(width: 200, height: 6)

            Text("\(Int(progress * 100))%")
                .font(.system(size: 14))
                .foregroundColor(.gray)
        }
    }

    private var statusText: String {
        switch status {
        case .pending: return "准备中..."
        case .uploading: return "上传中..."
        case .processing: return "正在生成你的回忆画册..."
        case .completed: return "处理完成！"
        case .failed: return "处理失败"
        }
    }
}

struct ProcessingView_Previews: PreviewProvider {
    static var previews: some View {
        let viewModel = VideoUploadViewModel()
        viewModel.uploadStatus = .processing
        viewModel.uploadProgress = 0.5
        return ProcessingView(viewModel: viewModel)
    }
}
