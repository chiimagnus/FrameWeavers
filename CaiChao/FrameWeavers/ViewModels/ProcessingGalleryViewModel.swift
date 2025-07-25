import SwiftUI
import Combine

/// 处理画廊的视图模型
class ProcessingGalleryViewModel: ObservableObject {
    @Published var mainImageName: String = "Image1"
    @Published var flyingImageInfo: FlyingImageInfo?
    @Published var hideSourceImageId: String?
    @Published var currentScrollIndex: Int = 0
    
    private let imageNames = ["Image1", "Image2", "Image3", "Image4", "Image1", "Image2", "Image3", "Image4"]
    
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

// MARK: - VideoUploadViewModel Extension

extension VideoUploadViewModel {
    /// 使用项目中现有的图片资源
    var mockImageNames: [String] {
        return ["Image1", "Image2", "Image3", "Image4", "Image1", "Image2", "Image3", "Image4"]
    }
    
    /// 为了无缝滚动，复制数组
    var loopedImageNames: [String] {
        let images = mockImageNames
        return images + images + images
    }
}