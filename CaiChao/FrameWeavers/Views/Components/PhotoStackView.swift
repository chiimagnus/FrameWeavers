import SwiftUI

/// 照片堆叠视图组件
struct PhotoStackView: View {
    let mainImageName: String
    let stackedImages: [String]
    let namespace: Namespace.ID
    
    private let cardSize = CGSize(width: 300, height: 200)
    private let cornerRadius: CGFloat = 8
    
    var body: some View {
        ZStack {
            // 堆叠的背景图片
            ForEach(stackedImages.indices, id: \.self) { index in
                let offset = CGFloat(index) * 4
                let rotation = Double((index * 7) % 15 - 7)
                
                cardView(imageName: stackedImages[index])
                    .rotationEffect(.degrees(rotation))
                    .offset(x: offset, y: -offset * 0.8)
                    .zIndex(Double(index))
            }
            
            // 主图卡片
            if !mainImageName.isEmpty {
                cardView(imageName: mainImageName)
                    .matchedGeometryEffect(id: mainImageName, in: namespace)
                    .rotationEffect(.degrees(1))
                    .zIndex(Double(stackedImages.count + 1))
            }
        }
        .frame(height: 250)
    }
    
    @ViewBuilder
    private func cardView(imageName: String) -> some View {
        Image(imageName)
            .resizable()
            .aspectRatio(contentMode: .fill)
            .frame(width: cardSize.width, height: cardSize.height)
            .clipShape(RoundedRectangle(cornerRadius: cornerRadius))
            .background(
                RoundedRectangle(cornerRadius: cornerRadius)
                    .fill(.white)
            )
            .shadow(
                color: .black.opacity(imageName == mainImageName ? 0.2 : 0.15),
                radius: imageName == mainImageName ? 10 : 8,
                y: imageName == mainImageName ? 5 : 3
            )
    }
}