import SwiftUI

/// 胶片条视图组件
struct FilmstripView: View {
    @ObservedObject var galleryViewModel: ProcessingGalleryViewModel
    @ObservedObject var uploadViewModel: VideoUploadViewModel
    let namespace: Namespace.ID
    
    // 用于持续滚动的偏移量
    @State private var scrollOffset: CGFloat = 0
    @State private var isScrolling = false
    
    // 滚动速度（每秒移动的像素）
    private let scrollSpeed: CGFloat = 50
    
    var body: some View {
        GeometryReader { geometry in
            let singleLoopWidth = CGFloat(galleryViewModel.imageNames.count) * 130.0
            
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 10) {
                    ForEach(galleryViewModel.loopedImageNames.indices, id: \.self) { index in
                        let imageName = galleryViewModel.loopedImageNames[index]
                        let baseFrame = galleryViewModel.getBaseFrame(for: imageName)
                        FilmstripFrameView(
                            imageName: imageName,
                            isHidden: galleryViewModel.hideSourceImageId == imageName,
                            namespace: namespace,
                            isSource: false, // 显式设置为 false
                            baseFrame: baseFrame
                        )
                        .id(index)
                        .background(
                            GeometryReader { frameGeometry in
                                Color.clear
                                    .preference(key: FramePreferenceKey.self, value: [
                                        imageName: frameGeometry.frame(in: .global)
                                    ])
                            }
                        )
                    }
                }
                .padding(.horizontal)
                .offset(x: -scrollOffset)
            }
            .frame(height: 100)
            .background(Color.black.opacity(0.8))
            .overlay(sprocketHoles)
            .onAppear {
                withAnimation(.linear(duration: 10).repeatForever(autoreverses: false)) {
                    scrollOffset = singleLoopWidth
                }
            }
            .onChange(of: uploadViewModel.uploadStatus) { _, newStatus in
                if newStatus == .completed || newStatus == .failed {
                    // 停止动画
                    withAnimation(.linear(duration: 0)) {
                        scrollOffset = scrollOffset
                    }
                }
            }
        }
        .frame(height: 100)
    }
    
    /// 胶片齿孔装饰
    var sprocketHoles: some View {
        VStack {
            HStack(spacing: 12) { 
                ForEach(0..<20) { _ in 
                    Rectangle().frame(width: 4, height: 4) 
                } 
            }
            Spacer()
            HStack(spacing: 12) { 
                ForEach(0..<20) { _ in 
                    Rectangle().frame(width: 4, height: 4) 
                } 
            }
        }
        .foregroundColor(.white.opacity(0.3))
        .padding(.vertical, 6)
    }
}

/// 胶片帧视图组件
struct FilmstripFrameView: View {
    let imageName: String
    let isHidden: Bool
    let namespace: Namespace.ID
    let isSource: Bool
    let baseFrame: BaseFrameData?

    init(imageName: String, isHidden: Bool, namespace: Namespace.ID, isSource: Bool, baseFrame: BaseFrameData? = nil) {
        self.imageName = imageName
        self.isHidden = isHidden
        self.namespace = namespace
        self.isSource = isSource
        self.baseFrame = baseFrame
    }

    var body: some View {
        ZStack {
            if !isHidden {
                if let baseFrame = baseFrame, let url = baseFrame.thumbnailURL {
                    AsyncImage(url: url) { image in
                        image
                            .resizable()
                            .aspectRatio(contentMode: .fill)
                    } placeholder: {
                        Rectangle()
                            .fill(Color.gray.opacity(0.3))
                            .overlay(
                                ProgressView()
                                    .scaleEffect(0.5)
                            )
                    }
                    .matchedGeometryEffect(id: imageName, in: namespace, isSource: isSource)
                } else if baseFrame == nil {
                    // 当没有基础帧数据时，显示空白而不是本地图片
                    Rectangle()
                        .fill(Color.clear)
                        .matchedGeometryEffect(id: imageName, in: namespace, isSource: isSource)
                } else {
                    // 有基础帧数据但URL无效时显示错误状态
                    Rectangle()
                        .fill(Color.red.opacity(0.3))
                        .overlay(
                            Text("文件不存在")
                                .font(.caption)
                                .foregroundColor(.white)
                        )
                        .matchedGeometryEffect(id: imageName, in: namespace, isSource: isSource)
                }
            } else {
                Rectangle().fill(.clear)
            }
        }
        .frame(width: 120, height: 80)
        .clipShape(RoundedRectangle(cornerRadius: 4))
        .opacity(isHidden ? 0 : 1)
    }
}