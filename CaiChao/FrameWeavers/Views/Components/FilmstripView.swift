import SwiftUI

/// 胶片条视图组件
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
                            return [imageName: CGRect.zero] // 简化处理，实际项目中可以计算真实frame
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