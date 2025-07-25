import SwiftUI

/// 照片堆叠视图组件
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