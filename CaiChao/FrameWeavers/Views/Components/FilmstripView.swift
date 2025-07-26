import SwiftUI

/// 简化版胶片条视图 - 只保留图片持续滚动功能
struct FilmstripView: View {
    @ObservedObject var galleryViewModel: ProcessingGalleryViewModel
    let namespace: Namespace.ID
    @State private var scrollOffset: CGFloat = 0
    @State private var isAnimating = false

    var body: some View {
        GeometryReader { geometry in
            let screenWidth = geometry.size.width
            let frameWidth: CGFloat = 130 // 120 + 10 spacing
            let imageCount = galleryViewModel.imageNames.count

            // 只保留滚动图片，删除所有装饰元素
            HStack(spacing: 10) {
                // 创建足够多的图片来实现无缝循环
                ForEach(0..<(imageCount * 4), id: \.self) { index in
                    let imageName = galleryViewModel.imageNames[index % imageCount]
                    let uniqueId = "\(imageName)_\(index)"

                    FilmstripFrameView(
                        imageName: imageName,
                        isHidden: galleryViewModel.hideSourceImageId == imageName,
                        namespace: namespace
                    )
                    .background(
                        GeometryReader { frameGeometry in
                            Color.clear
                                .preference(key: FramePreferenceKey.self, value: [
                                    uniqueId: frameGeometry.frame(in: .global)
                                ])
                                .onChange(of: frameGeometry.frame(in: .global)) {
                                    // 检查图片是否在屏幕中央
                                    checkCenterPosition(imageName: imageName, frame: frameGeometry.frame(in: .global), screenWidth: screenWidth)
                                }
                        }
                    )
                }
            }
            .padding(.horizontal, screenWidth / 2) // 减少padding，确保图片从可见区域开始
            .offset(x: scrollOffset)
            .onAppear {
                startContinuousScrolling(frameWidth: frameWidth, imageCount: imageCount)
            }
        }
        .frame(height: 100)
        .clipped()
    }

    /// 检查图片是否在屏幕中央
    private func checkCenterPosition(imageName: String, frame: CGRect, screenWidth: CGFloat) {
        let frameCenter = frame.midX
        let screenCenter = screenWidth / 2

        // 如果图片在屏幕中央附近且还没有被堆叠
        if abs(frameCenter - screenCenter) < 30 &&
           !galleryViewModel.stackedImages.contains(imageName) &&
           galleryViewModel.mainImageName != imageName {
            galleryViewModel.triggerJumpAnimation(imageName: imageName, sourceFrame: frame)
        }
    }

    /// 开始持续滚动动画
    private func startContinuousScrolling(frameWidth: CGFloat, imageCount: Int) {
        guard !isAnimating else { return }
        isAnimating = true

        // 计算一个完整循环的距离
        let cycleDistance = frameWidth * CGFloat(imageCount)
        
        // 计算初始偏移，让第一张图片从屏幕右侧开始可见
        let initialOffset = UIScreen.main.bounds.width

        // 设置初始位置，确保图片从屏幕内开始
        scrollOffset = initialOffset

        // 开始无限循环动画，添加延迟确保布局完成
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            withAnimation(.linear(duration: 10.0).repeatForever(autoreverses: false)) {
                scrollOffset = initialOffset - cycleDistance
            }
        }
    }
}

/// 胶片帧视图组件 - 保持不变
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