import SwiftUI

/// 照片堆叠视图组件
struct PhotoStackView: View {
    let mainImageName: String
    let stackedImages: [String]
    let namespace: Namespace.ID
    let galleryViewModel: ProcessingGalleryViewModel?

    init(mainImageName: String, stackedImages: [String], namespace: Namespace.ID, galleryViewModel: ProcessingGalleryViewModel? = nil) {
        self.mainImageName = mainImageName
        self.stackedImages = stackedImages
        self.namespace = namespace
        self.galleryViewModel = galleryViewModel
    }

    var body: some View {
        ZStack {
            // 堆叠的背景图片
            ForEach(stackedImages.indices, id: \.self) { index in
                let imageName = stackedImages[index]
                let offset = CGFloat(index) * 3
                let rotation = Double.random(in: -8...8)
                let baseFrame = galleryViewModel?.getBaseFrame(for: imageName)

                ZStack {
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
                    } else if baseFrame == nil {
                        // 只有在没有基础帧数据时才显示本地图片
                        Image(imageName)
                            .resizable()
                            .aspectRatio(contentMode: .fill)
                    } else {
                        // 有基础帧数据但URL无效时显示错误状态
                        Rectangle()
                            .fill(Color.orange.opacity(0.3))
                            .overlay(
                                Text("URL无效")
                                    .font(.caption)
                                    .foregroundColor(.white)
                            )
                    }
                }
                .frame(width: 300, height: 200)
                .clipShape(RoundedRectangle(cornerRadius: 8))
                .background(
                    RoundedRectangle(cornerRadius: 8).fill(.white)
                )
                .shadow(color: .black.opacity(0.1), radius: 5, y: 2)
                .rotationEffect(.degrees(rotation))
                .offset(x: offset, y: -offset)
                .zIndex(Double(index))
            }

            // 主图卡片
            ZStack {
                if !mainImageName.isEmpty {
                    let mainBaseFrame = galleryViewModel?.getBaseFrame(for: mainImageName)
                    if let baseFrame = mainBaseFrame, let url = baseFrame.thumbnailURL {
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
                        .matchedGeometryEffect(id: mainImageName, in: namespace)
                    } else if mainBaseFrame == nil {
                        // 只有在没有基础帧数据时才显示本地图片
                        Image(mainImageName)
                            .resizable()
                            .aspectRatio(contentMode: .fill)
                            .matchedGeometryEffect(id: mainImageName, in: namespace)
                    } else {
                        // 有基础帧数据但URL无效时显示错误状态
                        Rectangle()
                            .fill(Color.orange.opacity(0.3))
                            .overlay(
                                Text("URL无效")
                                    .font(.caption)
                                    .foregroundColor(.white)
                            )
                            .matchedGeometryEffect(id: mainImageName, in: namespace)
                    }
                }
            }
            .frame(width: 300, height: 200)
            .clipShape(RoundedRectangle(cornerRadius: 8))
            .background(
                RoundedRectangle(cornerRadius: 8).fill(.white)
            )
            .shadow(color: .black.opacity(0.2), radius: 10, y: 5)
            .rotationEffect(.degrees(1))
            .zIndex(Double(stackedImages.count + 1))

            // 胶带
            Rectangle()
                .fill(Color.white.opacity(0.4))
                .frame(width: 100, height: 25)
                .rotationEffect(.degrees(-4))
                .offset(y: -110)
                .zIndex(Double(stackedImages.count + 2))
        }
        .frame(height: 250)
    }
}