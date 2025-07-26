import SwiftUI

/// 飞跃图片动画组件
/// 用于显示从源位置飞跃到目标位置的图片动画
struct FlyingImageOverlay: View {
    let flyingImageInfo: FlyingImageInfo?
    let namespace: Namespace.ID
    
    var body: some View {
        if let info = flyingImageInfo {
            Image(info.id)
                .resizable()
                .aspectRatio(contentMode: .fill)
                .frame(width: info.sourceFrame.width, height: info.sourceFrame.height)
                .clipShape(RoundedRectangle(cornerRadius: 8))
                .matchedGeometryEffect(id: info.id, in: namespace)
                .position(x: info.sourceFrame.midX, y: info.sourceFrame.midY)
                .transition(.identity)
        }
    }
}
