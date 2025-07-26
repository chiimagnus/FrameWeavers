import SwiftUI

/// 胶片条视图组件
struct FilmstripView: View {
    @ObservedObject var galleryViewModel: ProcessingGalleryViewModel
    let namespace: Namespace.ID

    var body: some View {
        GeometryReader { geometry in
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
                }
                .frame(height: 100)
                .background(Color.black.opacity(0.8))
                .overlay(sprocketHoles)
                .onChange(of: galleryViewModel.currentScrollIndex) { newIndex in
                    // 更流畅的胶片运动动画
                    withAnimation(.linear(duration: 2.5)) {
                        proxy.scrollTo(newIndex, anchor: .center)
                    }
                    // 无限循环逻辑
                    if newIndex >= galleryViewModel.loopedImageNames.count - 8 {
                        DispatchQueue.main.asyncAfter(deadline: .now() + 2.5) {
                            galleryViewModel.currentScrollIndex = 8
                            proxy.scrollTo(galleryViewModel.currentScrollIndex, anchor: .center)
                        }
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